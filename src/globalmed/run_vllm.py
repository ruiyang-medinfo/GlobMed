"""
vLLM Local Model Inference Script

For running local models with vLLM offline batch inference.

Requirements:
    pip install 'globalmed[vllm]'

Usage:
    python -m globalmed.run_vllm --model_id "meta-llama/Llama-3.3-70B-Instruct" --subset "MedQA"
"""

import argparse
import json
import logging
import os
from os.path import dirname, exists, join
from typing import Dict, List, Optional, Set

from tqdm import tqdm

from globalmed.config import RESULTS_DIR, load_env
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


def setup_tokenizer(model_id: str):
    """
    Setup tokenizer for the model.

    Args:
        model_id: Model identifier

    Returns:
        Configured tokenizer
    """
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

    # Ensure pad token is set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return tokenizer


def prepare_prompts(
    ds: List[Dict],
    tokenizer,
    args: argparse.Namespace,
    lang: str
) -> List[str]:
    """
    Prepare prompts using chat template.

    Args:
        ds: Data documents
        tokenizer: Tokenizer
        args: Arguments
        lang: Language code

    Returns:
        List of formatted prompts
    """
    prompts = []

    for doc in ds:
        messages = get_message_from_doc(doc, args.subset, lang, args.prompt_style)

        # Apply chat template
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            **({"enable_thinking": args.think_mode == "think"}
               if args.think_mode != "none" else {}),
        )
        prompts.append(prompt)

    return prompts


def generate_final_json(
    jsonl_path: str,
    lang: str,
    expected_ids: Optional[Set[str]] = None
) -> None:
    """
    Generate final JSON result file.

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


def main():
    parser = argparse.ArgumentParser(
        description="vLLM local inference for GlobalMed"
    )
    parser.add_argument("--model_id", type=str, required=True,
                        help="Model identifier (HuggingFace model ID)")
    parser.add_argument("--subset", type=str, default="MedQA",
                        choices=["MedQA", "HeadQA", "MedExpQA", "MMLU-Pro", "BioNLI", "MedNLI"],
                        help="Dataset subset")
    parser.add_argument("--prompt_style", type=str, default="shot",
                        choices=["shot", "da"],
                        help="Prompt style")
    parser.add_argument("--lang", type=str, default=None,
                        help="Single language to process")
    parser.add_argument("--n_sampling", type=int, default=1,
                        help="Number of samples per question")
    parser.add_argument("--max_tokens", type=int, default=16384,
                        help="Maximum tokens for generation")
    parser.add_argument("--batch_size", type=int, default=128,
                        help="Batch size for vLLM")
    parser.add_argument("--tensor_parallel_size", type=int, default=None,
                        help="Tensor parallel size (default: auto)")
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.9,
                        help="GPU memory utilization")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of samples to process (for testing)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing results")
    parser.add_argument("--think_mode", choices=["none", "think", "nothink"],
                        default="none", help="Explicit thinking mode for compatible chat templates")
    add_sampling_arguments(parser)
    args = parser.parse_args()
    validate_arguments(args)

    load_env()

    # Import vLLM (optional dependency)
    try:
        import torch
        from vllm import LLM, SamplingParams
    except ImportError:
        raise ImportError(
            "vLLM is required for this script. "
            "Install it with: pip install 'globalmed[vllm]'"
        )

    # Format model ID for filesystem
    reformat_model_id = args.model_id.replace("/", "--")

    # Auto-detect tensor parallel size
    tensor_parallel_size = args.tensor_parallel_size
    if tensor_parallel_size is None:
        tensor_parallel_size = torch.cuda.device_count() or 1
        logger.info(f"Auto-detected {tensor_parallel_size} GPU(s)")

    # Initialize vLLM
    logger.info(f"Loading model: {args.model_id}")
    llm = LLM(
        model=args.model_id,
        tensor_parallel_size=tensor_parallel_size,
        gpu_memory_utilization=args.gpu_memory_utilization,
        trust_remote_code=True,
    )

    # Setup tokenizer
    tokenizer = setup_tokenizer(args.model_id)

    # Sampling parameters
    sampling_params = SamplingParams(
        n=args.n_sampling,
        max_tokens=args.max_tokens,
        **optional_generation_args(args),
    )

    generation = {"backend": "vllm", "model": args.model_id, "think_mode": args.think_mode,
                  "parameters": {"n": args.n_sampling, "max_tokens": args.max_tokens,
                                 **optional_generation_args(args)}}

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

        # Prepare prompts
        prompts = prepare_prompts(ds, tokenizer, args, lang)

        # Process in batches with real-time JSONL writing
        with open(result_save_path, "w" if args.overwrite else "a") as f:
            for batch_start in tqdm(range(0, len(prompts), args.batch_size), desc=f"[{lang}]"):
                batch_end = min(batch_start + args.batch_size, len(prompts))
                batch_prompts = prompts[batch_start:batch_end]
                batch_docs = ds[batch_start:batch_end]

                # Generate
                outputs = llm.generate(batch_prompts, sampling_params)

                # Process outputs and write immediately
                for idx, (doc, output) in enumerate(zip(batch_docs, outputs)):
                    # Get num_choices from metadata options
                    num_choices = get_num_options(args.subset)

                    result = {
                        "id": doc["id"],
                        "request": batch_prompts[idx],
                        "responses": [],
                        "metadata": doc,
                        "generation": generation,
                    }

                    for completion in sorted(output.outputs, key=lambda completion: completion.index):
                        text = completion.text
                        answer = extract_answer(
                            text, lang=lang, num_choices=num_choices
                        ) if text else None
                        result["responses"].append({
                            "run_idx": completion.index,
                            "content": text,
                            "answer": answer,
                        })

                    # Write immediately after each sample
                    f.write(json.dumps(result, ensure_ascii=False) + "\n")
                    f.flush()

        # Generate final JSON
        generate_final_json(result_save_path, lang, expected_ids=all_expected_ids)

    logger.info("Inference completed!")


if __name__ == "__main__":
    main()
