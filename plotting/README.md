# Paper plotting functions

Five independent scripts, one per plotting purpose. Supply your own data;
sourcing a script loads no data and creates no files.

```r
install.packages(c("ggplot2", "remotes"))
remotes::install_github("ricardo-bion/ggradar@f99517ae4df2903d3dbd4116af91b24009a5ac93")

source("plotting/radar_tasks.R")
plot_radar_tasks(task_data, file = "radar_tasks.pdf")
source("plotting/radar_languages.R")
plot_radar_languages(language_data, file = "radar_languages.pdf")
source("plotting/bars_overall.R")
plot_bars_overall(overall_runs, p_value = p, ylim = axis_limits, file = "bars_overall.pdf")
source("plotting/bars_language.R")
plot_bars_language(language_runs, p_value = p, ylim = axis_limits, language = "English", file = "bars_language.pdf")
source("plotting/heatmap.R")
plot_heatmap(p_values, file = "heatmap.pdf")
```

- Radars: two rows (models); first column is the model name, other columns are dataset or language accuracies in percent. Column order sets axis order.
- Bars: columns `model`, `run`, `accuracy` (percent), using overall or single-language accuracy per run. Mean and sample SD are calculated. Supply the two-sided p value and panel axis limits.
- Heatmap: columns `model`, `language`, `p_value`; optional model/language orders and title.

Radar and bar functions cover the component types in Figs.5–7 and Supplementary Fig.58; the heatmap function follows Fig.4. Model pairs, axis order and limits are supplied by the caller. Final manual composition is separate. These functions consolidate the supplied scripts and add the heatmap; input data and generated figures are not bundled.
