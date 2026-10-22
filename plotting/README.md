# Quantitative figure components

These ten scripts are cleaned versions of the supplied R plotting scripts.
They generate selected panels, not complete publication layouts. Schematics
(including Fig.1) were manually composed in Adobe Illustrator, maps in ArcGIS,
and supplementary plots in Origin. Those editable project files are not in
the supplied R folder. The `.ai` Illustrator format does not imply generative AI.

## Run

Dependencies used for validation: R 4.4.0, ggplot2 3.5.1, dplyr 1.1.4, scales
1.3.0, jsonlite 2.0.0 and ggradar 0.2 at commit
`f99517ae4df2903d3dbd4116af91b24009a5ac93` of `ricardo-bion/ggradar`.

```r
install.packages(c("ggplot2", "dplyr", "scales", "jsonlite", "remotes"))
remotes::install_github("ricardo-bion/ggradar@f99517ae4df2903d3dbd4116af91b24009a5ac93")
```

From the repository root:

```sh
Rscript --vanilla plotting/scripts/radar_task.R
Rscript --vanilla plotting/scripts/bar_4.R
```

Run the other scripts the same way. Outputs are vector PDFs and numerical
JSON sidecars in `plotting/output/`; override with `GLOBMED_PLOT_DIR`.
The scripts read the bundled SI run tables and statistical outputs under
`analysis/`, so no private filesystem paths or model access are needed.
Regenerate statistical outputs with `python analysis/reproduce_bh_fdr.py`
if changing inputs. By default bar annotations use the conservative BH adjusted
p values; set `GLOBMED_P_MODE=raw` for the original unadjusted convention.
The corresponding Fig.5/6/7 comparisons retain their levels after BH.

## Mapping

| Script | Corresponding component | Coverage |
|---|---|---|
| `radar_task.R` | Fig.5a task radar | Gemma-3-4B / MedGemma-4B |
| `radar_task_5.R` | Fig.5e task radars | Five 8B models combined |
| `radar_lang_5.R` | Fig.5e language radars | Five 8B models combined |
| `radar_language.R` | Fig.5e language radar | LLaMA-3.1-8B / HuatuoGPT-o1-8B |
| `radar_3_task.R` | Fig.5f task radars | Three 70B models combined |
| `radar_language_3.R` | Fig.5f language radars | Three 70B models combined |
| `bar_4.R` | Fig.5e bars | Four medical/base comparisons combined |
| `bar_2.R` | Fig.5f bars | Two medical/base comparisons combined |
| `bar_2_label.R` | Fig.6a bars | DeepSeek-V3 / DeepSeek-R1 |
| `bar.R` | Fig.7c English bars | MedGemma-4B / GlobMed-MedGemma-4B |

Combined panels in these scripts use several series/colors together; the final
paper separates some into two-model panels and applies manual layout. These
scripts do not cover every panel of Figs.1-7 or the Origin supplementary plots.
No pixel-identical or complete figure recreation is claimed.

## Corrections from the supplied scripts

- Replace private absolute export paths with a portable output directory.
- Read all numerical values from the bundled SI input tables; aggregate within
  each run before calculating mean/sample SD. The original six radar scripts'
  180 values agreed within 0.005 percentage points; the four real bar scripts'
  80 run values agreed within their printed precision.
- Fix inconsistent `Llama`/`LLaMA` factor levels that prevented the five-model
  task radar from rendering. Normalize model-name hyphens/capitalization.
- Put the Gemma task radar axes in the same dataset order as final Fig.5a.
- Correct `bar.R` from Zulu to **English**. Its inputs were the English values,
  approximately 58.976% and 66.907%, not Zulu values.
- Align bracket endpoints with actual bar centers and update deprecated line
  size arguments without changing their requested widths.
- Replace hard-coded asterisks with calculated annotations. The original
  HuatuoGPT-o1-8B bar script used one star; its two-sided p = 0.0048921454
  corresponds to two stars, as in the final Fig.5e. Use the figures' three-star
  ceiling for p < 0.001 rather than arbitrary four-star labels.
- Exclude the supplied `bar_plot.R`: it generated `rnorm()` demonstration
  samples, so it is not empirical figure-generation code. It was not used as
  an input to the statistical analysis.

All ten cleaned scripts executed and their PDFs were visually inspected.
This release does not modify the manuscript's existing PDF or SI artwork.
