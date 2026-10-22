# Reusable plotting functions in the paper's style. No data are bundled or loaded.
# source("plotting/plot_figures.R"), then call a function with your own data.

.save_plot <- function(plot, file, width, height) {
  if (!is.null(file)) ggplot2::ggsave(file, plot, width = width, height = height,
                                    device = grDevices::pdf, family = "Times", useDingbats = FALSE)
  plot
}

# Wide data: first column = model; remaining columns = axis accuracies (0–100).
# Column order determines the clockwise axis order; row order determines colours.
plot_radar <- function(data, file = NULL, width = 5, height = 5) {
  stopifnot(nrow(data) == 2, ncol(data) >= 4,
            all(vapply(data[-1], is.numeric, logical(1))),
            all(as.matrix(data[-1]) >= 0 & as.matrix(data[-1]) <= 100))
  names(data)[1] <- "group"
  data$group <- factor(data$group, levels = data$group)
  data[-1] <- data[-1] / 100
  p <- ggradar::ggradar(
    data, font.radar = "serif", grid.min = 0, grid.mid = .5, grid.max = 1,
    values.radar = c("0", "50", "100"), group.colours = c("#707BA6", "#1F8A5F"),
    group.point.size = 3, group.line.width = 1, background.circle.colour = "white",
    gridline.mid.colour = "grey", legend.position = "bottom", legend.text.size = 14,
    axis.label.size = 4.5, grid.label.size = 4.5
  ) + ggplot2::guides(colour = ggplot2::guide_legend(ncol = 1)) +
    ggplot2::theme(legend.box.margin = ggplot2::margin(t = -20))
  .save_plot(p, file, width, height)
}

# Long data: model, run, accuracy (0–100). Supply the two-sided p value separately.
# Set ylim to the paper panel's limits; x_label adds a language label and hides the legend.
plot_bars <- function(data, p_value, ylim, file = NULL, x_label = NULL,
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
                               labels = if (is.null(x_label)) "" else x_label,
                               expand = c(if (is.null(x_label)) .3 else .5, 0)) +
    ggplot2::coord_cartesian(ylim = ylim) +
    ggplot2::labs(x = NULL, y = "Accuracy") +
    ggplot2::theme_classic(base_family = "serif", base_size = 12) +
    ggplot2::theme(legend.position = if (is.null(x_label)) "top" else "none",
                   legend.direction = "vertical", legend.justification = "left",
                   legend.text = ggplot2::element_text(size = 9),
                   axis.text = ggplot2::element_text(colour = "black"),
                   axis.ticks.x = ggplot2::element_blank(),
                   axis.line = ggplot2::element_line(linewidth = .6),
                   axis.ticks.y = ggplot2::element_line(linewidth = .6))
  .save_plot(p, file, width, height)
}

# Long data: model, language, p_value. One row per cell; thresholds match Figure 4.
plot_heatmap <- function(data, file = NULL, model_order = unique(data$model),
                         language_order = unique(data$language), title = NULL,
                         width = 14, height = 6) {
  stopifnot(all(c("model", "language", "p_value") %in% names(data)),
            !anyDuplicated(data[c("model", "language")]),
            all(is.finite(data$p_value) & data$p_value >= 0 & data$p_value <= 1))
  labels <- c("ns", "*", "**", "***", "****")
  levels <- vapply(data$p_value, function(p) sum(p < c(.05,.01,.001,.0001)), integer(1))
  data$significance <- factor(labels[levels+1], levels = labels)
  data$model <- factor(data$model, levels = model_order)
  data$language <- factor(data$language, levels = rev(language_order))
  rounded <- ggplot2::ggproto("PaperRoundedTile", ggplot2::Geom,
    required_aes = c("x", "y"),
    default_aes = ggplot2::aes(fill = "grey", alpha = NA),
    draw_key = ggplot2::draw_key_rect,
    draw_panel = function(data, panel_params, coord) {
      corners <- data
      corners$x <- corners$x + .92
      corners$y <- corners$y + .82
      a <- coord$transform(data, panel_params)
      b <- coord$transform(corners, panel_params)
      cells <- lapply(seq_len(nrow(a)), function(i)
        grid::roundrectGrob(a$x[i], a$y[i], width = abs(b$x[i]-a$x[i]),
                            height = abs(b$y[i]-a$y[i]), r = grid::unit(.035, "inches"),
                            default.units = "npc", gp = grid::gpar(fill = a$fill[i], col = NA)))
      grid::gTree(children = do.call(grid::gList, cells))
    }
  )
  p <- ggplot2::ggplot(data, ggplot2::aes(model, language, fill = significance)) +
    ggplot2::layer(geom = rounded, stat = "identity", position = "identity", params = list()) +
    ggplot2::scale_fill_manual(values = c("#C7CDE6", "#DDE3EC", "#E8EBE8", "#D0E3D7", "#B6D8CA"),
                               drop = FALSE, name = "Significance") +
    ggplot2::labs(x = NULL, y = NULL, title = title) +
    ggplot2::guides(fill = ggplot2::guide_legend(title.position = "top", label.position = "bottom", nrow = 1)) +
    ggplot2::theme_minimal(base_family = "serif", base_size = 12) +
    ggplot2::theme(panel.grid = ggplot2::element_blank(),
                   axis.text = ggplot2::element_text(colour = "black", face = "bold"),
                   axis.text.x = ggplot2::element_text(angle = 90, hjust = 1, vjust = .5),
                   legend.position = "top", legend.justification = "left",
                   legend.title = ggplot2::element_text(face = "bold"),
                   legend.text = ggplot2::element_text(face = "bold"),
                   plot.title = ggplot2::element_text(face = "bold"))
  .save_plot(p, file, width, height)
}
