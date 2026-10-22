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
  if (!is.null(file)) ggplot2::ggsave(file, p, width = width, height = height,
                                    device = grDevices::pdf, family = "Times", useDingbats = FALSE)
  p
}
