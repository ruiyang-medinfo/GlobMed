# Long data: model, run, accuracy (0–100). Supply the two-sided p value separately.
# Use overall accuracy per run; set ylim to the paper panel's limits.
plot_bars_overall <- function(data, p_value, ylim, file = NULL,
                      width = 3.5, height = 4) {
  stopifnot(all(c("model", "run", "accuracy") %in% names(data)),
            length(p_value) == 1, is.finite(p_value), p_value >= 0, p_value <= 1,
            length(ylim) == 2, ylim[1] < ylim[2])
  models <- unique(as.character(data$model))
  stopifnot(length(models) == 2, !anyDuplicated(data[c("model", "run")]))
  values <- lapply(models, function(m) data$accuracy[data$model == m])
  stopifnot(all(lengths(values) >= 2), all(is.finite(data$accuracy)))
  summary <- data.frame(model = factor(models, levels = models), x = c(1, 1.6),
                        mean = vapply(values, mean, numeric(1)), sd = vapply(values, sd, numeric(1)))
  level <- sum(p_value < c(.05, .01, .001))
  label <- if (level) paste(rep("*", level), collapse = "") else "ns"
  bracket <- max(summary$mean + summary$sd) + 2
  p <- ggplot2::ggplot(summary, ggplot2::aes(x, mean, fill = model)) +
    ggplot2::geom_col(width = .6, colour = "white", linewidth = .2) +
    ggplot2::geom_errorbar(ggplot2::aes(ymin = mean-sd, ymax = mean+sd), width = .15, linewidth = .6) +
    ggplot2::annotate("segment", x = c(1,1,1.6), xend = c(1,1.6,1.6),
                      y = c(bracket-1,bracket,bracket), yend = c(bracket,bracket,bracket-1), linewidth = .6) +
    ggplot2::annotate("text", x = 1.3, y = bracket+1, label = label, family = "serif", size = 5) +
    ggplot2::scale_fill_manual(values = c("#C7CDE6", "#B6D8CA"), name = NULL) +
    ggplot2::scale_x_continuous(breaks = 1.3,
                               labels = "",
                               expand = c(.3, 0)) +
    ggplot2::coord_cartesian(ylim = ylim) +
    ggplot2::labs(x = NULL, y = "Accuracy") +
    ggplot2::theme_classic(base_family = "serif", base_size = 12) +
    ggplot2::theme(legend.position = "top",
                   legend.direction = "vertical", legend.justification = "left",
                   legend.text = ggplot2::element_text(size = 9),
                   axis.text = ggplot2::element_text(colour = "black"),
                   axis.ticks.x = ggplot2::element_blank(),
                   axis.line = ggplot2::element_line(linewidth = .6),
                   axis.ticks.y = ggplot2::element_line(linewidth = .6))
  if (!is.null(file)) ggplot2::ggsave(file, p, width = width, height = height,
                                    device = grDevices::pdf, family = "Times", useDingbats = FALSE)
  p
}
