.script_file <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value=TRUE)[1])
.script_file <- gsub("~+~", " ", .script_file, fixed=TRUE)
source(file.path(dirname(normalizePath(.script_file)), "..", "paper_data.R"))
library(ggplot2)

group1 <- paper_runs("DeepSeek-V3")
group2 <- paper_runs("DeepSeek-R1")

bar_width <- 0.6

data <- data.frame(
  Position  = rep(c(1, 1 + bar_width), each = 5),
  GroupName = rep(c("DeepSeek-V3", "DeepSeek-R1"), each = 5),
  Value     = c(group1, group2)
)

summary_data <- data.frame(
  Position  = c(1, 1 + bar_width),
  GroupName = c("DeepSeek-V3", "DeepSeek-R1"),
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
  annotate("text", x = 1.3, y = text_height, label = paper_star("DeepSeek-V3", "DeepSeek-R1", "Fig6"), size = 6) +

  scale_fill_manual(values = c("DeepSeek-V3" = "#c7cde6", "DeepSeek-R1" = "#b6d8ca"),
                    breaks = c("DeepSeek-V3", "DeepSeek-R1"),
                    name = NULL) +
  scale_x_continuous(expand = c(0.3, 0)) +
  coord_cartesian(ylim = c(65, 80)) +
  theme_classic() +
  theme(
    legend.position = "top",
    legend.direction = "horizontal",
    legend.background = element_blank(),
    legend.text = element_text(size = 9, color = "black"),
    legend.key.size = unit(0.7, "cm"),
    legend.margin = margin(10, 10, 10, 10),

    axis.title.x = element_blank(),
    axis.text.x  = element_blank(),
    axis.ticks.x = element_blank(),
    axis.title.y = element_text(size = 12, color = "black"),
    axis.text.y  = element_text(size = 10, color = "black"),
    axis.line.x  = element_line(linewidth = 0.7),
    axis.line.y  = element_line(linewidth = 0.7),
    axis.ticks.y = element_line(linewidth = 0.7)
  ) +
  labs(y = "Accuracy (%)")



ggsave(file.path(out_dir, "deepseek.pdf"), p, width = 3.5, height = 4)
