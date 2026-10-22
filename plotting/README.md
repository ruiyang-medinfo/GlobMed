# Paper plotting functions

`plot_figures.R` contains three reusable functions. It loads no data and creates
no files when sourced. Install `ggplot2` and `ggradar` before use.

```r
install.packages(c("ggplot2", "remotes"))
remotes::install_github("ricardo-bion/ggradar@f99517ae4df2903d3dbd4116af91b24009a5ac93")

source("plotting/plot_figures.R")
plot_radar(radar_data, file = "radar.pdf")
plot_bars(run_data, p_value = p, ylim = axis_limits, file = "bars.pdf")
plot_heatmap(p_values, file = "heatmap.pdf")
```

- Radar: two rows (models); first column is the model name, other columns are axis accuracies in percent. Column order sets axis order.
- Bars: columns `model`, `run`, `accuracy`; mean and sample SD are calculated. Supply the two-sided p value and panel axis limits. Optional `x_label` adds a language label.
- Heatmap: columns `model`, `language`, `p_value`; optional model/language orders and title.

Radar and bar functions cover the component types in Figs.5–7 and Supplementary Fig.58; the heatmap function follows Fig.4. Model pairs, axis order and limits are supplied by the caller. Final manual composition is separate. These functions consolidate the supplied scripts and add the heatmap; input data and generated figures are not bundled.
