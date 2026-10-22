"""
OpenAI/Azure OpenAI API Inference Script

Supports:
- OpenAI official API
- Azure OpenAI API (via --use_azure flag)
- OpenRouter (third-party models)
- Local vLLM/SGLang serve (OpenAI-compatible endpoints)

Usage:
    # Using OpenAI
    export OPENAI_BASE="https://api.openai.com/v1"
    export OPENAI_KEY="your-key"
    python -m globalmed.run_openai --model_id "gpt-4o" --subset "MedQA"

    # Using Azure OpenAI
    export AZURE_OPENAI_BASE="https://your-resource.openai.azure.com/"
    export AZURE_OPENAI_KEY="your-key"
    export AZURE_OPENAI_API_VERSION="2024-12-01-preview"
    python -m globalmed.run_openai --model_id "gpt-4o" --subset "MedQA" --use_azure

    # Using local model
    export OPENAI_BASE="http://localhost:8000/v1"
    export OPENAI_KEY="EMPTY"
    python -m globalmed.run_openai --model_id "Qwen/Qwen3-8B" --subset "MedQA"
"""

import argparse
import asyncio
import json
import logging
import os
import random
from os.path import dirname, exists, join
from typing import Any, Dict, List, Optional, Set

from openai import AsyncOpenAI, AsyncAzureOpenAI
from tqdm.asyncio import tqdm_asyncio

from globalmed.config import (
    RESULTS_DIR,
    load_env,
    uses_max_completion_tokens,
)
from globalmed.data import read_data, DEFAULT_LANGUAGES, get_num_options
from globalmed.sampling import (add_sampling_arguments, validate_arguments,
                                optional_generation_args, load_finished_ids)
from globalmed.prompt import get_message_from_doc
from string import ascii_uppercase
from globalmed.judge import extract_answer

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def run_model_by_message(
    client: AsyncOpenAI,
    messages: List[Dict],
    data_id: str,
    model: str,
    gen_args: Dict[str, Any],
    timeout: int = 300
) -> Optional[Any]:
    """
    Call model with retry logic.

    Args:
        client: OpenAI async client
        messages: Message list
        data_id: Data item ID (for logging)
        model: Model identifier
        gen_args: Generation arguments
        timeout: Timeout in seconds

    Returns:
        API response or None
    """
    retry_num = 0
    max_retries = 10
    response = None

    while retry_num <= max_retries:
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **gen_args
                ),
                timeout=timeout
            )
            return response

        except asyncio.TimeoutError:
            logger.error(f"Timeout for {data_id}")

        except Exception as e:
            error_str = str(e).lower()
            if any(x in error_str for x in ["rate limit", "too many requests", "429"]):
                logger.warning(f"Rate limit for {data_id}: {e}")
            elif any(x in error_str for x in ["server error", "500", "502", "503"]):
                logger.warning(f"Server error for {data_id}: {e}")
            else:
                logger.error(f"Error for {data_id}: {e}")
                return None  # Non-retryable error

        retry_num += 1
        if retry_num <= max_retries:
            wait_time = min(2 ** retry_num + random.uniform(0, 1), 60)
            logger.info(f"Retry {retry_num}/{max_retries} for {data_id} after {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

    logger.error(f"Max retries reached for {data_id}")
    return None


def build_generation_args(args):
    if uses_max_completion_tokens(args.model_id):
        gen_args = {"max_completion_tokens": args.max_tokens}
    else:
        gen_args = {"max_tokens": args.max_tokens}

    gen_args["n"] = args.n_sampling
    gen_args.update(optional_generation_args(args))

    # Add reasoning effort for o-series models
    if args.reasoning_effort:
        gen_args["reasoning_effort"] = args.reasoning_effort

    # Add thinking mode for compatible models (e.g., Qwen3 via vLLM)
    if args.think_mode == "think":
        gen_args["extra_body"] = {"chat_template_kwargs": {"enable_thinking": True}}
    elif args.think_mode == "nothink":
        gen_args["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}

    return gen_args


async def process_item(
    client: AsyncOpenAI,
    doc: Dict,
    args: argparse.Namespace,
    lang: str
) -> Dict:
    """
    Process a single data item.

    Args:
        client: OpenAI async client
        doc: Data document
        args: Command line arguments
        lang: Language code

    Returns:
        Result dictionary
    """
    messages = get_message_from_doc(doc, args.subset, lang, args.prompt_style)

    gen_args = build_generation_args(args)

    response = await run_model_by_message(
        client, messages, doc["id"], args.model_id, gen_args
    )

    return {
        "id": doc["id"],
        "metadata": doc,
        "request": messages,
        "response": response
    }


async def process_with_semaphore(
    client: AsyncOpenAI,
    doc: Dict,
    args: argparse.Namespace,
    lang: str,
    semaphore: asyncio.Semaphore
) -> Dict:
    """
    Process item with concurrency control.

    Args:
        client: OpenAI async client
        doc: Data document
        args: Command line arguments
        lang: Language code
        semaphore: Asyncio semaphore

    Returns:
        Result dictionary
    """
    async with semaphore:
        # Small random delay to avoid burst requests
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return await process_item(client, doc, args, lang)


def generate_final_json(
    jsonl_path: str,
    lang: str,
    expected_ids: Optional[Set[str]] = None
) -> None:
    """
    Generate final JSON result file from JSONL.

    Args:
        jsonl_path: Path to JSONL file
        lang: Language code
        expected_ids: Set of expected item IDs (for completeness check)
    """
    if not exists(jsonl_path):
        logger.warning(f"JSONL file not found: {jsonl_path}")
        return

    # Use dict to deduplicate by id (later entries override earlier ones)
    final_data_dict: Dict[str, Dict] = {}

    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line.strip())
                doc_id = doc["id"]

                # Get ground truth from metadata
                answer_index = doc["metadata"].get("answer_index", 0)
                ground_truth = ascii_uppercase[answer_index]

                # Handle missing or empty responses
                if not doc.get("responses"):
                    final_data_dict[doc_id] = {
                        "id": doc_id,
                        "answer": [None],
                        "ground_truth": ground_truth,
                    }
                    continue

                # Get answers directly from JSONL (already extracted during inference)
                answers = [r.get("answer") for r in doc["responses"]]

                # Later entries override earlier ones (keep newest)
                final_data_dict[doc_id] = {
                    "id": doc_id,
                    "answer": answers,
                    "ground_truth": ground_truth,
                }
            except (json.JSONDecodeError, KeyError):
                continue

    if not final_data_dict:
        logger.warning("No valid items found in JSONL, skipping JSON export")
        return

    # Check completeness if expected_ids provided
    if expected_ids:
        exported_ids = set(final_data_dict.keys())
        missing_ids = expected_ids - exported_ids
        if missing_ids:
            logger.warning(f"{len(missing_ids)} items missing from JSON export")
            logger.warning(f"Missing IDs (first 5): {sorted(missing_ids)[:5]}")

    # Convert to sorted list
    final_data = list(final_data_dict.values())
    final_data.sort(key=lambda x: x["id"])

    json_path = jsonl_path.replace(".jsonl", ".json")
    with open(json_path, "w") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    logger.info(f"Exported {len(final_data)} items to {json_path}")


async def main():
    parser = argparse.ArgumentParser(
        description="OpenAI/Azure OpenAI inference for GlobalMed"
    )
    parser.add_argument("--model_id", type=str, required=True,
                        help="Model identifier")
    parser.add_argument("--subset", type=str, default="MedQA",
                        choices=["MedQA", "HeadQA", "MedExpQA", "MMLU-Pro", "BioNLI", "MedNLI"],
                        help="Dataset subset")
    parser.add_argument("--prompt_style", type=str, default="shot",
                        choices=["shot", "da"],
                        help="Prompt style: shot (CoT) or da (direct answer)")
    parser.add_argument("--lang", type=str, default=None,
                        help="Single language to process (default: all)")
    parser.add_argument("--n_sampling", type=int, default=1,
                        help="Number of samples per question")
    parser.add_argument("--max_tokens", type=int, default=16384,
                        help="Maximum tokens for generation")
    parser.add_argument("--reasoning_effort", type=str, default=None,
                        choices=["low", "minimal", "medium", "high"],
                        help="Reasoning effort for o-series models")
    parser.add_argument("--think_mode", type=str, default="none",
                        choices=["none", "think", "nothink"],
                        help="Thinking mode for compatible models")
    parser.add_argument("--n_thread", type=int, default=32,
                        help="Number of concurrent requests")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of samples to process (for testing)")
    parser.add_argument("--use_azure", action="store_true",
                        help="Use Azure OpenAI instead of OpenAI")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing results")
    add_sampling_arguments(parser)
    args = parser.parse_args()
    validate_arguments(args)

    # Load environment variables
    load_env()

    # Format model ID for filesystem
    reformat_model_id = args.model_id.replace("/", "--")
    if args.reasoning_effort:
        reformat_model_id += f"-{args.reasoning_effort}"
    if args.think_mode != "none":
        reformat_model_id += f"-{args.think_mode}"

    # Initialize client
    if args.use_azure:
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_BASE"),
            azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", args.model_id),
            api_key=os.environ.get("AZURE_OPENAI_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        )
        logger.info(f"Using Azure OpenAI: {os.environ.get('AZURE_OPENAI_BASE')}")
    else:
        client = AsyncOpenAI(
            base_url=os.environ.get("OPENAI_BASE", "https://api.openai.com/v1"),
            api_key=os.environ.get("OPENAI_KEY"),
        )
        logger.info(f"Using OpenAI: {os.environ.get('OPENAI_BASE', 'https://api.openai.com/v1')}")

    generation = {"backend": "openai", "model": args.model_id, "parameters": build_generation_args(args)}

    # Language list
    lang_list = [args.lang] if args.lang else DEFAULT_LANGUAGES

    for lang in lang_list:
        result_save_path = join(
            RESULTS_DIR, reformat_model_id,
            f"{args.subset}_{args.prompt_style}", f"{lang}.jsonl"
        )
        os.makedirs(dirname(result_save_path), exist_ok=True)

        # Load finished IDs
        finished_ids = []
        if not args.overwrite:
            finished_ids = load_finished_ids(result_save_path, args.n_sampling, generation)

        # Load data
        try:
            ds = read_data(args.subset, lang, local_mednli=args.local_mednli)
            if args.limit is not None:
                ds = ds[:args.limit]
        except Exception as e:
            logger.error(f"[{lang}] Failed to load data: {e}")
            continue

        # Track all expected IDs for completeness check
        all_expected_ids = {d["id"] for d in ds}

        # Filter out finished samples
        ds = [d for d in ds if d["id"] not in finished_ids]

        if not ds:
            logger.info(f"[{lang}] All samples completed, skipping")
            generate_final_json(result_save_path, lang, expected_ids=all_expected_ids)
            continue

        logger.info(f"[{lang}] Processing {len(ds)} samples")

        try:
            # Create tasks with semaphore
            semaphore = asyncio.Semaphore(args.n_thread)
            tasks = [
                process_with_semaphore(client, doc, args, lang, semaphore)
                for doc in ds
            ]

            # Process with progress bar
            with open(result_save_path, "w" if args.overwrite else "a") as f:
                for coro in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
                    ret = await coro

                    dump_dict = {
                        "id": ret["id"],
                        "request": json.dumps(ret["request"], ensure_ascii=False),
                        "responses": [],
                        "metadata": ret["metadata"],
                        "generation": generation,
                    }

                    if ret["response"] and hasattr(ret["response"], "choices"):
                        # Get num_choices from metadata options
                        num_choices = get_num_options(args.subset)

                        for choice in sorted(ret["response"].choices, key=lambda choice: choice.index):
                            content = getattr(choice.message, "content", None)
                            reasoning = getattr(choice.message, "reasoning_content", None)
                            answer = extract_answer(
                                content, lang=lang, num_choices=num_choices
                            ) if content else None

                            dump_dict["responses"].append({
                                "run_idx": choice.index,
                                "content": content,
                                "reasoning": reasoning,
                                "answer": answer,
                            })
                    else:
                        # Failed response - fill with None
                        dump_dict["responses"] = [
                            {"content": None, "answer": None}
                            for _ in range(args.n_sampling)
                        ]

                    f.write(json.dumps(dump_dict, ensure_ascii=False) + "\n")
                    f.flush()

        except Exception as e:
            logger.error(f"[{lang}] Error during processing: {e}")
            raise

        # Generate final JSON
        generate_final_json(result_save_path, lang, expected_ids=all_expected_ids)

    # Close client after all languages are processed
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
