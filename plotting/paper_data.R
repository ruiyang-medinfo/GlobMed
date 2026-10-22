# Numerical inputs: SI printed five-run tables, bundled in analysis/data.
# Source this file from the supplied entry scripts; no model/API calls.
plot_root <- normalizePath(file.path(dirname(.script_file), ".."))
out_dir <- file.path(plot_root, "output")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
runs <- read.csv(file.path(plot_root, "../analysis/data/run_accuracy.csv"),
                 fileEncoding = "UTF-8-BOM", check.names = FALSE)
tests <- read.csv(file.path(plot_root, "../analysis/results/all_comparisons.csv"),
                  fileEncoding = "UTF-8-BOM", check.names = FALSE)

paper_runs <- function(model, language = NULL, kind = "base") {
  x <- runs[runs$model == model & runs$kind == kind, ]
  if (!is.null(language)) x <- x[x$language == language, ]
  stopifnot(nrow(x) == if (is.null(language)) 360 else 30)
  vapply(1:5, function(i) mean(x$accuracy_percent[x$run == i]), numeric(1))
}

paper_radar <- function(models, axes) {
  result <- data.frame(group = models, check.names = FALSE)
  for (axis in axes) {
    result[[axis]] <- vapply(models, function(model) {
      x <- runs[runs$kind == "base" & runs$model == model &
                  (runs$dataset == axis | runs$language == axis), ]
      stopifnot(nrow(x) == if (axis %in% runs$dataset) 60 else 30)
      mean(x$accuracy_percent)
    }, numeric(1))
  }
  result
}

paper_star <- function(model_a, model_b, group, language = NULL) {
  x <- tests[tests$model_A == model_a & tests$model_B == model_b & tests$group == group, ]
  if (!is.null(language)) x <- x[x$target_language == language, ]
  stopifnot(nrow(x) == 1)
  p <- x$p_raw
  if (is.na(p)) return("not estimable")
  if (p < .001) "***" else if (p < .01) "**" else if (p < .05) "*" else "ns"
}
