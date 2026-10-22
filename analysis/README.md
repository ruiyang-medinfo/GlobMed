# Statistical analysis

Recompute the paper's 4,992 two-sided paired t tests from the five printed SI
run values (df = 4). Python 3.10+; no additional packages required.

```sh
python3 analysis/paired_t_tests.py
```

Supply local `analysis/data/run_accuracy.csv` and `analysis/data/comparisons.csv`.
Input data and generated results are not included in the repository.
Output: `analysis/results/all_comparisons.csv`.

Required CSV columns:
- `run_accuracy.csv`: `kind` (`base` or `fine`), `model`, `dataset`, `run` (1–5), `language`, `accuracy_percent`.
- `comparisons.csv`: `id`, `family`, `group`, `figure`, `panel`, `model1`, `model2`, `reference`, `language`, `datasets`.

`datasets` is semicolon-separated; `Overall` averages all languages.
`family` is `language_disparity`, `medical_finetuning`, `reasoning`, or
`globmed_finetuning`; use the last value for fine-tuning run tables.

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
