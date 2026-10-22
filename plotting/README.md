# Figure scripts

These R scripts generate the quantitative components listed below, using the
bundled SI values and unadjusted p values in `analysis/`.

```r
install.packages(c("ggplot2", "dplyr", "scales", "remotes"))
remotes::install_github("ricardo-bion/ggradar@f99517ae4df2903d3dbd4116af91b24009a5ac93")
```

Run from the repository root; PDFs are saved in `plotting/output/`:

```sh
Rscript --vanilla plotting/scripts/radar_task.R
Rscript --vanilla plotting/scripts/bar_4.R
```

| Script | Figure component |
|---|---|
| `radar_task.R` | Fig.5a: Gemma-3-4B / MedGemma-4B |
| `radar_task_5.R`, `radar_lang_5.R` | Fig.5e: five 8B models |
| `radar_language.R` | Fig.5e: LLaMA-3.1-8B / HuatuoGPT-o1-8B |
| `radar_3_task.R`, `radar_language_3.R` | Fig.5f: three 70B models |
| `bar_4.R`, `bar_2.R` | Fig.5e / Fig.5f: medical-model comparisons |
| `bar_2_label.R` | Fig.6a: DeepSeek-V3 / DeepSeek-R1 |
| `bar.R` | Fig.7c: English MedGemma / GlobMed comparison |

Final figures include manual layout. Schematics such as Fig.1 were composed
in Adobe Illustrator, maps in ArcGIS, and supplementary plots in Origin;
these scripts do not recreate their complete layouts.
