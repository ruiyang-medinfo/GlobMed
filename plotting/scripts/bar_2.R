.script_file <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value=TRUE)[1])
.script_file <- gsub("~+~", " ", .script_file, fixed=TRUE)
source(file.path(dirname(normalizePath(.script_file)), "..", "paper_data.R"))
library(ggplot2)

llama <- paper_runs("LLaMA-3.1-70B")
huatuo <- paper_runs("HuatuoGPT-o1-70B")
openbio <- paper_runs("OpenBioLLM-70B")

bar_width <- 0.6
gap <- 0.4

data <- data.frame(
  Position  = c(rep(1, 5), rep(1 + bar_width, 5),
                rep(2.5, 5), rep(2.5 + bar_width, 5)),
  GroupName = rep(c("LLaMA-3.1-70B", "HuatuoGPT-o1-70B",
                    "LLaMA-3.1-70B", "OpenBioLLM-70B"), each = 5),
  Value     = c(llama, huatuo, llama, openbio)
)


summary_data <- data.frame(
  Position  = c(1, 1 + bar_width, 2.5, 2.5 + bar_width),
  GroupName = c("LLaMA-3.1-70B", "HuatuoGPT-o1-70B",
                "LLaMA-3.1-70B", "OpenBioLLM-70B"),
  Mean      = c(mean(llama), mean(huatuo),
                mean(llama), mean(openbio)),
  SD        = c(sd(llama), sd(huatuo),
                sd(llama), sd(openbio))
)

top_y <- max(summary_data$Mean + summary_data$SD)
bar_height <- top_y + 2
text_height <- bar_height + 1

p <- ggplot(summary_data, aes(x = Position, y = Mean, fill = GroupName)) +
  geom_bar(stat = "identity", width = bar_width, color = "white", linewidth = 0.5) +
  geom_errorbar(aes(ymin = Mean - SD, ymax = Mean + SD),
                width = 0.15, linewidth = 0.7) +

  annotate("segment", x = 1, xend = 1, y = bar_height - 1, yend = bar_height, linewidth = 0.7) +
  annotate("segment", x = 1.6, xend = 1.6, y = bar_height - 1, yend = bar_height, linewidth = 0.7) +
  annotate("segment", x = 1, xend = 1.6, y = bar_height, yend = bar_height, linewidth = 0.7) +
  annotate("text", x = 1.3, y = text_height, label = paper_star("LLaMA-3.1-70B", "HuatuoGPT-o1-70B", "Fig5"), size = 6) +

  annotate("segment", x = 2.5, xend = 2.5, y = bar_height - 1.5, yend = bar_height - 0.5, linewidth = 0.7) +
  annotate("segment", x = 3.1, xend = 3.1, y = bar_height - 1.5, yend = bar_height - 0.5, linewidth = 0.7) +
  annotate("segment", x = 2.5, xend = 3.1, y = bar_height - 0.5, yend = bar_height - 0.5, linewidth = 0.7) +
  annotate("text", x = 2.8, y = bar_height + 0.5, label = paper_star("LLaMA-3.1-70B", "OpenBioLLM-70B", "Fig5"), size = 6) +

  scale_fill_manual(
    values = c("LLaMA-3.1-70B" = "#c7cde6",
               "HuatuoGPT-o1-70B" = "#b6d8ca",
               "OpenBioLLM-70B" = "#a8d8ea"),
    breaks = c("LLaMA-3.1-70B", "HuatuoGPT-o1-70B", "OpenBioLLM-70B"),
    name = NULL
  ) +
  scale_x_continuous(expand = c(0.3, 0)) +
  coord_cartesian(ylim = c(30, 65)) +
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


ggsave(file.path(out_dir, "bar_2.pdf"), p, width = 6, height = 4)
