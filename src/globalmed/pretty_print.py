"""
GlobalMed Result Pretty Printing and Analysis

Automatically discovers all models and languages in the results directory,
then prints a comparison table with models as rows and languages as columns.

Usage:
    python -m globalmed.pretty_print --subset "MedQA"
    python -m globalmed.pretty_print --subset "MedQA" --run_idx 0
    python -m globalmed.pretty_print --subset "MedQA" --prompt_style "da"
"""

import argparse
import json
import logging
import os
import string
from os.path import exists, isdir, join
from typing import Dict, List, Optional, Tuple

from prettytable import PrettyTable

from globalmed.config import RESULTS_DIR
from globalmed.data import DEFAULT_LANGUAGES

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Number of options per dataset
DATASET_NUM_OPTIONS = {
    "MedQA": 4,
    "HeadQA": 4,
    "MedExpQA": 5,
    "MMLU-Pro": 10,
    "BioNLI": 2,
}


def discover_models_and_results(
    subset: str,
    prompt_style: str = "shot"
) -> Dict[str, Dict[str, str]]:
    """
    Discover all models and their available result files for a given subset.

    Args:
        subset: Dataset subset name
        prompt_style: Prompt style

    Returns:
        Dict mapping model_id to {lang: json_path}
    """
    if not exists(RESULTS_DIR):
        return {}

    results = {}
    task_folder = f"{subset}_{prompt_style}"

    # Scan all model directories
    for model_dir in os.listdir(RESULTS_DIR):
        model_path = join(RESULTS_DIR, model_dir)
        if not isdir(model_path):
            continue

        task_path = join(model_path, task_folder)
        if not isdir(task_path):
            continue

        # Find all language JSON files
        lang_files = {}
        for filename in os.listdir(task_path):
            if filename.endswith(".json"):
                lang = filename.replace(".json", "")
                json_path = join(task_path, filename)
                lang_files[lang] = json_path

        if lang_files:
            results[model_dir] = lang_files

    return results


def load_results(result_path: str) -> Optional[List[Dict]]:
    """
    Load results from a JSON file, sorted and deduplicated by ID.

    Args:
        result_path: Path to JSON result file

    Returns:
        List of result dictionaries or None if file not found
    """
    if not exists(result_path):
        return None

    try:
        with open(result_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    # Sort by ID (extract numeric part for proper ordering)
    def sort_key(x):
        id_str = x.get("id", "")
        parts = id_str.split("_")
        try:
            return int(parts[-1])
        except (ValueError, IndexError):
            return 0

    data = sorted(data, key=sort_key)

    # Deduplicate by ID (keep last occurrence)
    data_dict = {doc["id"]: doc for doc in data}
    return list(data_dict.values())


def calculate_accuracy(
    results: List[Dict],
    num_options: int,
    run_idx: Optional[int] = None
) -> Tuple[float, int, int]:
    """
    Calculate accuracy for a specific run index or average across all runs.

    Args:
        results: List of result dictionaries
        num_options: Number of answer options
        run_idx: Specific run index (0-based), or None for average

    Returns:
        Tuple of (accuracy, total_samples, error_count)
    """
    predictions = []
    ground_truths = []
    error_count = 0

    for doc in results:
        gt = doc.get("ground_truth")
        answers = doc.get("answer", [])

        if gt is None:
            continue

        # Convert ground_truth to index
        if isinstance(gt, str) and gt.upper() in string.ascii_uppercase:
            gt_idx = string.ascii_uppercase.index(gt.upper())
        elif isinstance(gt, int):
            gt_idx = gt
        else:
            continue

        ground_truths.append(gt_idx)

        # Get prediction(s)
        if run_idx is not None:
            # Specific run index
            if answers is None or len(answers) <= run_idx:
                predictions.append(-1)
                error_count += 1
            elif answers[run_idx] is None:
                predictions.append(-1)
                error_count += 1
            else:
                pred = answers[run_idx]
                if isinstance(pred, str) and pred.upper() in string.ascii_uppercase:
                    pred_idx = string.ascii_uppercase.index(pred.upper())
                    if pred_idx < num_options:
                        predictions.append(pred_idx)
                    else:
                        predictions.append(-1)
                        error_count += 1
                else:
                    predictions.append(-1)
                    error_count += 1
        else:
            # Average across all valid answers
            if not answers:
                predictions.append(-1)
                error_count += 1
                continue

            correct = 0
            valid = 0
            for ans in answers:
                if ans is None:
                    continue
                valid += 1
                if isinstance(ans, str) and ans.upper() in string.ascii_uppercase:
                    pred_idx = string.ascii_uppercase.index(ans.upper())
                    if pred_idx == gt_idx:
                        correct += 1

            if valid > 0:
                # Use majority vote or average
                predictions.append(gt_idx if correct > valid / 2 else -1)
            else:
                predictions.append(-1)
                error_count += 1

    if not ground_truths:
        return 0.0, 0, 0

    # Calculate accuracy
    if run_idx is not None:
        correct = sum(1 for p, g in zip(predictions, ground_truths) if p == g)
        accuracy = correct / len(ground_truths) if ground_truths else 0.0
    else:
        # For average mode, calculate sample-wise accuracy
        # Error samples (all None answers) are included with score 0
        sample_scores = []
        for doc in results:
            gt = doc.get("ground_truth")
            answers = doc.get("answer", [])
            if gt is None:
                continue

            if isinstance(gt, str):
                gt_letter = gt.upper()
            elif isinstance(gt, int):
                gt_letter = string.ascii_uppercase[gt]
            else:
                continue

            # Handle missing/empty answers as error (score 0)
            if not answers:
                sample_scores.append(0.0)
                continue

            valid = 0
            correct = 0
            for ans in answers:
                if ans is None:
                    continue
                valid += 1
                if isinstance(ans, str) and ans.upper() == gt_letter:
                    correct += 1

            if valid > 0:
                sample_scores.append(correct / valid)
            else:
                # All answers are None - treat as error (score 0)
                sample_scores.append(0.0)

        accuracy = sum(sample_scores) / len(sample_scores) if sample_scores else 0.0

    return accuracy, len(ground_truths), error_count


def print_results_table(
    subset: str,
    prompt_style: str = "shot",
    run_idx: Optional[int] = 0,
    languages: Optional[List[str]] = None
) -> None:
    """
    Print a results table with models as rows and languages as columns.

    Args:
        subset: Dataset subset name
        prompt_style: Prompt style
        run_idx: Specific run index (0-based), or None for average
        languages: Languages to include (default: all)
    """
    # Discover all models and results
    model_results = discover_models_and_results(subset, prompt_style)

    if not model_results:
        print(f"No results found for {subset}_{prompt_style}")
        return

    # Sort models alphabetically
    model_ids = sorted(model_results.keys())
    lang_list = languages or DEFAULT_LANGUAGES
    num_options = DATASET_NUM_OPTIONS.get(subset, 4)

    # Build table
    table = PrettyTable()
    table.field_names = ["Model"] + lang_list

    for model_id in model_ids:
        row = [model_id]

        for lang in lang_list:
            if lang not in model_results[model_id]:
                row.append("-")
                continue

            json_path = model_results[model_id][lang]
            results = load_results(json_path)

            if results is None or len(results) == 0:
                row.append("-")
                continue

            accuracy, total, errors = calculate_accuracy(results, num_options, run_idx)

            if accuracy > 0:
                row.append(f"{accuracy*100:.2f}")
            else:
                row.append("-")

        table.add_row(row)

    # Print header info
    run_info = f"run_idx={run_idx}" if run_idx is not None else "average"
    print(f"\nDataset: {subset} ({prompt_style}) [{run_info}]")
    print(f"Models found: {len(model_ids)}")
    print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Pretty print GlobalMed evaluation results"
    )
    parser.add_argument("--subset", type=str, default="MedQA",
                        choices=["MedQA", "HeadQA", "MedExpQA", "MMLU-Pro", "BioNLI"],
                        help="Dataset subset")
    parser.add_argument("--prompt_style", type=str, default="shot", choices=["shot", "da"],
                        help="Prompt style")
    parser.add_argument("--run_idx", type=int, default=0,
                        help="Specific run index (0-based) for scoring.")
    parser.add_argument("--lang", type=str, nargs="+", default=None,
                        help="Languages to include (default: all 12)")
    args = parser.parse_args()

    # Print results table
    print_results_table(
        args.subset,
        args.prompt_style,
        run_idx=args.run_idx,
        languages=args.lang
    )


if __name__ == "__main__":
    main()
