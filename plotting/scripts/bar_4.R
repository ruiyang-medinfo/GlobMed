.script_file <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value=TRUE)[1])
.script_file <- gsub("~+~", " ", .script_file, fixed=TRUE)
source(file.path(dirname(normalizePath(.script_file)), "..", "paper_data.R"))
library(ggplot2)

llama <- paper_runs("LLaMA-3.1-8B")
biomedical <- paper_runs("Bio-Medical-LLaMA-3-8B")
medreason <- paper_runs("MedReason-8B")
huatuo <- paper_runs("HuatuoGPT-o1-8B")
openbio <- paper_runs("OpenBioLLM-8B")

bar_width <- 0.6

data <- data.frame(
  Position  = c(rep(1, 5), rep(1 + bar_width, 5),
                rep(2.5, 5), rep(2.5 + bar_width, 5),
                rep(4, 5), rep(4 + bar_width, 5),
                rep(5.5, 5), rep(5.5 + bar_width, 5)),
  GroupName = rep(c("LLaMA-3.1-8B", "Bio-Medical-LLaMA-3-8B",
                    "LLaMA-3.1-8B", "MedReason-8B",
                    "LLaMA-3.1-8B", "HuatuoGPT-o1-8B",
                    "LLaMA-3.1-8B", "OpenBioLLM-8B"), each = 5),
  Value     = c(llama, biomedical,
                llama, medreason,
                llama, huatuo,
                llama, openbio)
)

summary_data <- data.frame(
  Position  = c(1, 1 + bar_width, 2.5, 2.5 + bar_width,
                4, 4 + bar_width, 5.5, 5.5 + bar_width),
  GroupName = c("LLaMA-3.1-8B", "Bio-Medical-LLaMA-3-8B",
                "LLaMA-3.1-8B", "MedReason-8B",
                "LLaMA-3.1-8B", "HuatuoGPT-o1-8B",
                "LLaMA-3.1-8B", "OpenBioLLM-8B"),
  Mean      = c(mean(llama), mean(biomedical),
                mean(llama), mean(medreason),
                mean(llama), mean(huatuo),
                mean(llama), mean(openbio)),
  SD        = c(sd(llama), sd(biomedical),
                sd(llama), sd(medreason),
                sd(llama), sd(huatuo),
                sd(llama), sd(openbio))
)

top_y <- max(summary_data$Mean + summary_data$SD)
bar_height <- top_y + 1.5
text_height <- bar_height + 0.8

p <- ggplot(summary_data, aes(x = Position, y = Mean, fill = GroupName)) +
  geom_bar(stat = "identity", width = bar_width, color = "white", linewidth = 0.5) +
  geom_errorbar(aes(ymin = Mean - SD, ymax = Mean + SD),
                width = 0.12, linewidth = 0.6) +

  annotate("segment", x = 1, xend = 1, y = bar_height - 1, yend = bar_height, linewidth = 0.6) +
  annotate("segment", x = 1.45, xend = 1.45, y = bar_height - 1, yend = bar_height, linewidth = 0.6) +
  annotate("segment", x = 1, xend = 1.45, y = bar_height, yend = bar_height, linewidth = 0.6) +
  annotate("text", x = 1.225, y = text_height, label = paper_star("LLaMA-3.1-8B", "Bio-Medical-LLaMA-3-8B", "Fig5"), size = 5) +

  annotate("segment", x = 2.5, xend = 2.5, y = bar_height - 0.5, yend = bar_height + 0.5, linewidth = 0.6) +
  annotate("segment", x = 2.95, xend = 2.95, y = bar_height - 0.5, yend = bar_height + 0.5, linewidth = 0.6) +
  annotate("segment", x = 2.5, xend = 2.95, y = bar_height + 0.5, yend = bar_height + 0.5, linewidth = 0.6) +
  annotate("text", x = 2.725, y = text_height + 0.5, label = paper_star("LLaMA-3.1-8B", "MedReason-8B", "Fig5"), size = 5) +

  annotate("segment", x = 4, xend = 4, y = bar_height, yend = bar_height + 1, linewidth = 0.6) +
  annotate("segment", x = 4.45, xend = 4.45, y = bar_height, yend = bar_height + 1, linewidth = 0.6) +
  annotate("segment", x = 4, xend = 4.45, y = bar_height + 1, yend = bar_height + 1, linewidth = 0.6) +
  annotate("text", x = 4.225, y = text_height + 1, label = paper_star("LLaMA-3.1-8B", "HuatuoGPT-o1-8B", "Fig5"), size = 5) +

  annotate("segment", x = 5.5, xend = 5.5, y = bar_height - 1, yend = bar_height, linewidth = 0.6) +
  annotate("segment", x = 5.95, xend = 5.95, y = bar_height - 1, yend = bar_height, linewidth = 0.6) +
  annotate("segment", x = 5.5, xend = 5.95, y = bar_height, yend = bar_height, linewidth = 0.6) +
  annotate("text", x = 5.725, y = text_height, label = paper_star("LLaMA-3.1-8B", "OpenBioLLM-8B", "Fig5"), size = 5) +

  scale_fill_manual(
    values = c("LLaMA-3.1-8B" = "#c7cde6",
               "Bio-Medical-LLaMA-3-8B" = "#b6d8ca",
               "MedReason-8B" = "#a8d8ea",
               "HuatuoGPT-o1-8B" = "#d4a5d4",
               "OpenBioLLM-8B" = "#f4c2a8"),
    breaks = c("LLaMA-3.1-8B", "Bio-Medical-LLaMA-3-8B",
               "MedReason-8B", "HuatuoGPT-o1-8B", "OpenBioLLM-8B"),
    name = NULL
  ) +
  scale_x_continuous(expand = c(0.1, 0)) +
  coord_cartesian(ylim = c(15, 45)) +
  theme_classic() +
  theme(
    legend.position = "top",
    legend.direction = "horizontal",
    legend.background = element_blank(),
    legend.text = element_text(size = 8, color = "black"),
    legend.key.size = unit(0.6, "cm"),
    legend.margin = margin(5, 5, 5, 5),

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


ggsave(file.path(out_dir, "bar_4.pdf"), p, width = 8, height = 4)
