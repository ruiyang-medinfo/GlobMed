# Language-level radar (Figs.5-7 and Supplementary Fig.58).
# Wide data: first column = model; remaining columns = language accuracies (0–100).
# Column order determines the clockwise axis order; row order determines colours.
plot_radar_languages <- function(data, file = NULL, width = 5, height = 5) {
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
  if (!is.null(file)) ggplot2::ggsave(file, p, width = width, height = height,
                                    device = grDevices::pdf, family = "Times", useDingbats = FALSE)
  p
}
