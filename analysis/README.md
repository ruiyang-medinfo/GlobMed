# Statistical analysis

Recompute the paper's 4,992 two-sided paired t tests from the five printed SI
run values (df = 4). Python 3.10+; no additional packages required.

```sh
python3 analysis/paired_t_tests.py
```

Inputs are `data/run_accuracy.csv` and `data/comparisons.csv`; source tables
are recorded in `data/provenance.json`. Output is `results/all_comparisons.csv`.

| Figure | Comparisons | Within-run aggregation |
|---|---:|---|
| Supplementary Fig.2–57 | 3,696 | Individual dataset and language pair |
| Fig.4 | 1,232 | Datasets grouped by original language |
| Fig.5 | 10 | All six datasets and 12 languages |
| Fig.6 | 6 | All six datasets and 12 languages |
| Fig.7 / Supplementary Fig.58 | 48 | Six datasets for each language |

Rows include the five A/B values, means, sample SDs, B−A difference, t statistic
and unadjusted `p_raw`. Accuracy is in percent; differences and SDs are in
percentage points. Tests pair the printed run indices. Blank t/p values mark
zero-variance differences; printed values do not recover unrounded predictions
or item/rater-level uncertainty.
