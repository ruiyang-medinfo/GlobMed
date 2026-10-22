"""Validate and summarize a final result JSON, one accuracy per sample slot."""
import argparse
import json
import statistics
from pathlib import Path


def summarize(rows, n_runs=5):
    if n_runs < 1 or not rows:
        raise ValueError("Require a positive run count and nonempty results")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate result IDs")
    if any(len(row.get("answer", [])) != n_runs for row in rows):
        raise ValueError(f"Every item must have exactly {n_runs} answer slots")
    accuracy = [100 * sum(row["answer"][i] == row["ground_truth"] for row in rows)
                / len(rows) for i in range(n_runs)]
    return {"items": len(rows), "n_runs": n_runs,
            "missing_answers": sum(a is None for row in rows for a in row["answer"]),
            "run_accuracy_percent": accuracy,
            "mean_accuracy_percent": statistics.mean(accuracy),
            "sample_SD_pp": statistics.stdev(accuracy) if n_runs > 1 else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_file", type=Path)
    parser.add_argument("--n_runs", type=int, default=5)
    args = parser.parse_args()
    result = summarize(json.loads(args.result_file.read_text()), args.n_runs)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
