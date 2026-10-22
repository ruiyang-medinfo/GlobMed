# GlobMed BH FDR response materials

This package reproduces the run-level multiple-comparison analysis accompanying the response to Reviewer 2, comment 2. It contains the complete numerical results for 4,992 existing figure comparisons, not additional experiments. It does not change the manuscript, SI, or figure files.

## Run

Use Python 3.10 or later. No third-party packages, network access, manuscript file, or machine-specific paths are needed.

```sh
python3 reproduce_bh_fdr.py --data-dir data --output-dir results
```

Run this command from the extracted package folder. Alternatively, run the script by its absolute path without options; input and output paths default to folders beside the script. The script recomputes all results, including rounding bounds, and replaces files in the specified output folder. It may take several minutes.

## Input and provenance

`data/run_accuracy.csv` contains 23,040 printed run accuracies from 60 SI tables. Values are percentages reported to two decimal places, not unrounded predictions or individual ratings. Each row identifies the source SI table, model, dataset, language, and run. `data/comparisons.csv` defines every comparison and its figure/panel. `data/provenance.json` records the source file hash and extraction date.

Base-model run tables: Supplementary Tab.92–96 (BioNLI), 98–102 (MedNLI), 104–108 (HeadQA), 110–114 (MedExpQA), 116–120 (MedQA), and 122–126 (MMLU-Pro).

Fine-tuning run tables: Supplementary Tab.129–133, 135–139, 141–145, 147–151, 153–157, and 159–163, in the same dataset order. The corresponding `fine` rows include both each baseline and its GlobMed counterpart.

## Test and aggregation

The script reconstructs the original paired, two-sided t statistic from five run-index pairs (df = 4). A is the reference language/model and B is the target language/model; differences are B minus A, in percentage points. It does not verify that a shared run index represents a justified experimental pairing or an independent random seed.

- Supplementary Fig.2–57: one dataset and language pair per comparison; 56 models × 6 datasets × 11 target languages = 3,696 comparisons.
- Fig.4: first average datasets with the same original language within each run. English-original datasets are BioNLI, MedNLI, MedQA, and MMLU-Pro; Spanish-original datasets are HeadQA and MedExpQA. There are 56 × 2 × 11 = 1,232 comparisons. These reuse the SI inputs and are not independent replication evidence.
- Fig.5: 10 medical-model/base-model contrasts, averaging all six datasets and all 12 languages within each run.
- Fig.6: 6 reasoning-model/corresponding-model contrasts, using the same within-run averaging.
- Fig.7 and Supplementary Fig.58: 4 GlobMed/base pairs × 12 languages = 48 contrasts, averaging all six datasets within each run for the specified language.

The standard deviation is the sample SD across the five resulting aggregates, not the average of dataset SDs. The Student t tail uses a numerically stable analytic df = 4 expression with Decimal arithmetic.

## Multiplicity families

The question-based families were specified for this retrospective analysis before calculating the adjustments; they were not prospectively registered with the original experiments.

1. Language disparities: all 4,928 comparisons from Supplementary Fig.2–57 and Fig.4 jointly.
2. Medical fine-tuning: all 10 Fig.5 contrasts.
3. Reasoning: all 6 Fig.6 contrasts.
4. GlobMed fine-tuning: all 48 Fig.7 and Supplementary Fig.58 contrasts jointly.

For sorted p values, BH adjusted p at rank i is the minimum of m × p(j) / j over ranks j >= i, capped at 1. Strict thresholds match the existing figures: adjusted p < 0.05, 0.01, and 0.001, with an additional 0.0001 level in Fig.4. BH controls FDR under its independence/positive-dependence conditions; these conditions are not established by the available aggregate tables. Adjusting p values does not model item, generation-sample, or rater dependence and does not repair invalid underlying p values.

## Recommended interpretation and special cases

The response uses `p_BH_conservative`: assign adjustment-input p = 1 to all 15 zero-variance paired differences, keep them in their 4,928-comparison family, and make no ordinary t-test claim about those 15. Among the remaining 4,977 comparisons, 4,361 have raw p < 0.05 and 4,334 have conservative BH adjusted p < 0.05. The same 27 comparisons lose significance (22 SI and 5 Fig.4). All 64 comparisons in the other three families remain significant; all 48 GlobMed differences are positive.

The 15 zero-variance differences are all in Supplementary Fig.2 (Claude-3.5-Haiku). Thirteen have a nonzero constant difference; two have a zero constant difference. `t_statistic` and `p_raw` are missing for all 15. This can result from the limited printed precision and cannot be resolved by adding arbitrary numerical noise.

For traceability ONLY, separate `original_convention` columns reproduce a historical limiting convention: p = 0 for a nonzero constant difference and p = 1 for a zero difference. These reproduce the earlier 4,374 → 4,347 summary and 204 marker-level changes (130 SI; 74 Fig.4). A reported zero is not a validated exact p value. With the conservative treatment, 208 finite comparisons change marker level (133 SI; 75 Fig.4), including the same 27 losses; the other 181 remain significant. The 15 untestable contrasts require separate treatment, not ordinary significance stars.

Rounding analysis lets each printed accuracy vary within ±0.005 percentage points, hence each paired difference within ±0.01 points. It enumerates conservative bounds for the t-test p value, then uses BH monotonicity to propagate the bounds across the family. These are outer bounds, not confidence intervals, and ignore constraints shared by repeated input cells. Nine finite comparisons can cross 0.05 within the resulting bounds; two additional zero-difference/zero-variance comparisons have bounds that cross 0.05. `rounding_sensitive.csv` contains the nine finite cases. The five Fig.4 losses are stable under these bounds. The bounds allow the zero-variance contrasts to vary with rounding; they are not bounds around a permanently fixed p = 1 sensitivity scenario.

This analysis is conditional on the existing fixed benchmark items, the assumed run-index pairing, and the reported run aggregates. It cannot quantify sampling uncertainty over new items, verify run independence/normality with five replicates, or estimate individual-rater variance. Per-item predictions, run/seed metadata, and individual ratings would be needed to address those questions.

## Outputs

- `results/all_comparisons.csv`: all 4,992 rows, including the five A and B run aggregates, means, SDs, difference, t, raw p, both BH variants, family size, and diagnostic flags.
- `results/family_summary.csv`: family totals under both conventions.
- `results/lost_significance.csv`: the 27 lost-significance rows; their identities are the same under both BH treatments.
- `results/marker_level_changes_conservative.csv`: the 208 estimable contrasts whose significance level changes under conservative BH.
- `results/zero_variance.csv`: the 15 untestable cases.
- `results/rounding_sensitive.csv`: the nine finite comparisons sensitive to rounding at 0.05.
- `results/results.json`: the same detailed results in JSON, with missing values encoded as null.
- `DATA_DICTIONARY.md`: field definitions.
- `portable_verification.json`: comparison against the earlier independent audit implementation; all 4,992 rows reproduced with zero numerical discrepancy for the checked fields.

The response Word reports selected numerical tables for readability; the CSV is the complete record. No SI insertion or figure update has been performed by this package.
