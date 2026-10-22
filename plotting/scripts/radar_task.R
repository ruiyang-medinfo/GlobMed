.script_file <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value=TRUE)[1])
.script_file <- gsub("~+~", " ", .script_file, fixed=TRUE)
source(file.path(dirname(normalizePath(.script_file)), "..", "paper_data.R"))
library(dplyr)
library(scales)
library(ggplot2)
library(ggradar)

radar_data <- paper_radar(c("Gemma-3-4B", "MedGemma-4B"), c("BioNLI", "MedNLI", "HeadQA", "MedExpQA", "MedQA", "MMLU-Pro"))

radar_data_scaled <- radar_data %>%
  mutate(across(-group, ~ rescale(.x, to = c(0, 1), from = c(0, 100))))

radar_data_scaled$group <- factor(radar_data_scaled$group,
                                  levels = c("Gemma-3-4B", "MedGemma-4B"))

p <- ggradar(
  radar_data_scaled,
  grid.min = 0,
  grid.max = 1,
  grid.mid = 0.5,
  values.radar = c("0", "50", "100"),
  group.colours = c("#707ba6", "#1f8a5f"),
  group.point.size = 3,
  group.line.width = 1,
  background.circle.colour = "white",
  gridline.mid.colour = "grey",
  legend.position = "bottom",
  legend.text.size = 14,
  axis.label.size = 4.5
) +
  theme(legend.box.margin = margin(t = -20))


ggsave(file.path(out_dir, "gemma3_4b_task.pdf"), p, width = 5, height = 5)

objects <- intersect(c("radar_data", "radar_data_scaled", "summary_data"), ls())
jsonlite::write_json(mget(objects), file.path(out_dir, "radar_task_values.json"), dataframe="rows", auto_unbox=TRUE, pretty=TRUE, digits=15, na="null")
