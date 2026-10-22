#!/usr/bin/env python3
"""Recompute the paper's two-sided paired t tests from SI five-run tables."""
import argparse
import csv
import statistics
from decimal import Decimal, localcontext
from pathlib import Path


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def paired_test(a, b):
    with localcontext() as context:
        context.prec = 60
        differences = [y - x for x, y in zip(a, b)]
        mean = sum(differences) / 5
        sd = (sum((d - mean) ** 2 for d in differences) / 4).sqrt()
        if sd == 0:
            return float(mean), 0.0, None, None
        t = mean * Decimal(5).sqrt() / sd
        z = abs(t)
        h = (z * z + 4).sqrt()
        # Exact two-sided Student t tail for df = 4.
        p = (4 / (h * (h + z))) ** 2 * (1 + z / (2 * h))
        return float(mean), float(sd), float(t), float(p)


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--output", type=Path, default=root / "results/all_comparisons.csv")
    args = parser.parse_args()
    raw = read_csv(args.data_dir / "run_accuracy.csv")
    comparisons = read_csv(args.data_dir / "comparisons.csv")
    values = {(r["kind"], r["model"], r["dataset"], int(r["run"]), r["language"]):
              Decimal(r["accuracy_percent"]) for r in raw}
    languages = list(dict.fromkeys(r["language"] for r in raw))
    assert len(raw) == len(values) == 23040 and len(comparisons) == 4992

    def get_runs(kind, model, datasets, language):
        langs = languages if language == "Overall" else [language]
        return [sum(values[kind, model, d, run, lang] for d in datasets for lang in langs)
                / Decimal(len(datasets) * len(langs)) for run in range(1, 6)]

    results = []
    for c in comparisons:
        kind = "fine" if c["family"] == "globmed_finetuning" else "base"
        datasets = c["datasets"].split(";")
        reference = c["reference"] if c["family"] == "language_disparity" else c["language"]
        a = get_runs(kind, c["model1"], datasets, reference)
        b = get_runs(kind, c["model2"], datasets, c["language"])
        difference, sd, t, p = paired_test(a, b)
        row = dict(
            comparison_id=c["id"], group=c["group"], figure=int(c["figure"]), panel=c["panel"],
            model_A=c["model1"], model_B=c["model2"], reference_language=reference,
            target_language=c["language"], datasets=c["datasets"], n_runs=5, df=4,
            mean_A_percent=float(sum(a) / 5), mean_B_percent=float(sum(b) / 5),
            difference_B_minus_A_pp=difference,
            SD_A_pp=statistics.stdev(map(float, a)), SD_B_pp=statistics.stdev(map(float, b)),
            SD_difference_pp=sd, t_statistic=t, p_raw=p,
            zero_variance=(sd == 0),
        )
        for prefix, runs in [("A", a), ("B", b)]:
            for i, value in enumerate(runs, 1):
                row[f"{prefix}_run{i}"] = float(value)
        results.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {len(results)} comparisons to {args.output}")


if __name__ == "__main__":
    main()
