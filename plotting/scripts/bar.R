.script_file <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value=TRUE)[1])
.script_file <- gsub("~+~", " ", .script_file, fixed=TRUE)
source(file.path(dirname(normalizePath(.script_file)), "..", "paper_data.R"))
library(ggplot2)

group1 <- paper_runs("MedGemma-4B", language = "English", kind = "fine")
group2 <- paper_runs("GlobMed-MedGemma-4B", language = "English", kind = "fine")

bar_width <- 0.6

data <- data.frame(
  Position  = rep(c(1, 1 + bar_width), each = 5),
  GroupName = rep(c("MedGemma-4B", "GlobMed-MedGemma-4B"), each = 5),
  Value     = c(group1, group2)
)

summary_data <- data.frame(
  Position  = c(1, 1 + bar_width),
  GroupName = c("MedGemma-4B", "GlobMed-MedGemma-4B"),
  Mean      = c(mean(group1), mean(group2)),
  SD        = c(sd(group1), sd(group2))
)

top_y <- max(summary_data$Mean + summary_data$SD)
bar_height <- top_y + 2
text_height <- bar_height + 1

p <- ggplot(summary_data, aes(x = Position, y = Mean, fill = GroupName)) +
  geom_bar(stat = "identity", width = bar_width, color = "white", linewidth = 0.5) +
  geom_errorbar(aes(ymin = Mean - SD, ymax = Mean + SD),
                width = 0.15, linewidth = 0.7) +

  annotate("segment", x = 1,   xend = 1,   y = bar_height - 1, yend = bar_height, linewidth = 0.7) +
  annotate("segment", x = 1.6, xend = 1.6, y = bar_height - 1, yend = bar_height, linewidth = 0.7) +
  annotate("segment", x = 1,   xend = 1.6, y = bar_height,     yend = bar_height, linewidth = 0.7) +
  annotate("text", x = 1.3, y = text_height, label = paper_star("MedGemma-4B", "GlobMed-MedGemma-4B", "Fig7", "English"), size = 6) +

  scale_fill_manual(values = c("MedGemma-4B" = "#c7cde6", "GlobMed-MedGemma-4B" = "#b6d8ca")) +
  scale_x_continuous(breaks = c(1.3), labels = c("English"), expand = c(0.5, 0)) +
  coord_cartesian(ylim = c(55, 70)) +

  theme_classic() +
  theme(
    legend.position = "none",
    axis.title.x = element_blank(),
    axis.text = element_text(size = 12, color = "black"),
    axis.title.y = element_text(size = 12, color = "black"),
    axis.line = element_line(linewidth = 0.7),
    axis.ticks.y = element_line(linewidth = 0.7),
    axis.ticks.x = element_blank()
  ) +
  labs(y = "Accuracy (%)")


ggsave(file.path(out_dir, "bar.pdf"), p, width = 3, height = 3.5)

objects <- intersect(c("radar_data", "radar_data_scaled", "summary_data"), ls())
jsonlite::write_json(mget(objects), file.path(out_dir, "bar_values.json"), dataframe="rows", auto_unbox=TRUE, pretty=TRUE, digits=15, na="null")
