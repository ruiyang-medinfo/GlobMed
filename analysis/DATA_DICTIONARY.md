# Data dictionary

All CSVs use UTF-8 with a byte-order mark. Decimal points are periods. Blank numerical cells indicate an unestimable ordinary t test, not a zero value. Boolean fields use True/False.

## Inputs

`run_accuracy.csv`: `kind` separates base-model evaluation (`base`) from fine-tuning evaluation (`fine`); `model`, `dataset`, `run`, and `language` identify a score; `SI_table` is its SI table number; `accuracy_percent` is the printed accuracy in percent. The table's exact header is authoritative.

`comparisons.csv`: `id` is the stable comparison identifier; `family`, `group`, `figure`, and `panel` locate the comparison; `model1` and `model2` are A and B; `reference` and `language` identify the reference and target languages; `datasets` is a semicolon-delimited list. `Overall` requests equal averaging over the 12 languages, within a run.

## Results

| Field | Meaning |
| --- | --- |
| comparison_id | Stable T0001–T4992 identifier linking inputs and outputs |
| family | One of language_disparity, medical_finetuning, reasoning, globmed_finetuning |
| group / figure / panel | Original plotted location; SI panel 1–6 means BioNLI, MedNLI, HeadQA, MedExpQA, MedQA, MMLU-Pro |
| model_A / model_B | Reference and target models; identical for a language comparison |
| reference_language / target_language | A and B language; Overall denotes the within-run average over 12 languages |
| datasets | Datasets equally averaged within each run |
| n_runs / df | Five paired run aggregates and four t degrees of freedom |
| mean_A_percent / mean_B_percent | Mean accuracy across the five A or B aggregates, in percent |
| difference_B_minus_A_pp | Mean paired difference in percentage points; positive means B is higher |
| SD_A_pp / SD_B_pp | Sample SD of the five A or B aggregates, in percentage points |
| SD_difference_pp | Sample SD of the five B minus A differences |
| A_run1–A_run5 / B_run1–B_run5 | Five within-run aggregates used by the test |
| t_statistic | Signed mean difference divided by its estimated standard error; blank/null for zero variance |
| p_raw | Two-sided unadjusted t-test p; blank/null for zero variance |
| zero_variance | True when all five printed paired differences are identical |
| p_original_convention | Same as p_raw for finite tests; historical convention 0 for nonzero constant differences, 1 for zero constant differences; NOT a validated p for zero variance |
| family_size | Full number of comparisons in the adjustment family, including untestable rows |
| p_BH_conservative | Family BH after assigning adjustment-input p = 1 to the 15 zero-variance cases; response's reported BH values |
| p_BH_original_convention | Family BH of p_original_convention, retained for reconciliation only |
| BH_level_conservative | Level 0–3, or 0–4 for Fig.4, from conservative BH; blank/null for zero-variance contrasts |
| lost_significance_conservative | Finite raw p < 0.05 and conservative BH p >= 0.05 |
| raw_level_original / BH_level_original | Historical significance levels 0–3, or 0–4 for Fig.4; based on the original-convention columns, not on conservative BH |
| lost_significance_original | Historical raw p < 0.05 and original-convention BH p >= 0.05; the same 27 identities are lost in the conservative analysis |
| rounding_p_lower / rounding_p_upper | Conservative p bounds for ±0.01 pp error in each paired difference; NOT confidence intervals |
| rounding_BH_lower / rounding_BH_upper | BH propagation of the lower and upper p bounds across the whole family, allowing all scores to vary within rounding bounds |
| rounding_sensitive_at_005 | The propagated interval straddles the strict 0.05 decision threshold |
| inferential_status | Finite test, rounding-sensitive finite test, or zero variance/unestimable ordinary t test |

The original figure stars cannot be inferred from `p_BH_conservative` by reading `BH_level_original`; use `BH_level_conservative` if using the conservative scenario. No figure has yet been edited to implement either scenario.
