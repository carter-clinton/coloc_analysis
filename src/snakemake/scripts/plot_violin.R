#!/usr/bin/env Rscript
# =============================================================================
# D-06c: Supplementary Figure — Bootstrap concordance violin per trait
#
# One violin panel per trait (facet_wrap), showing the per-bootstrap
# retention distribution. Overlaid:
#   - Dashed horizontal line: unmatched concordance % (Phase 2, full EUR N)
#   - Dotted horizontal line: expected concordance % under Hou null (D-05b)
#
# Inputs:
#   --per-boot: per_bootstrap_retention.tsv (trait, bootstrap_idx, retention)
#   --table2:   table2.tsv (D-06a, for overlay values)
#   --out:      output PDF path (8.5 x 11 inches)
#
# References:
#   - D-06c: Supplementary violin figure per CONTEXT.md
#   - D-02a: Primary metric (Tier A retention)
#   - D-05b: Hou null expected concordance
#   - Phase 5 dashboard palette (reuse color conventions)
# =============================================================================

suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(ggplot2)
})

option_list <- list(
  make_option("--per-boot", dest = "per_boot", type = "character",
              help = "Path to per_bootstrap_retention.tsv"),
  make_option("--table2", dest = "table2", type = "character",
              help = "Path to table2.tsv (D-06a)"),
  make_option("--out", dest = "out", type = "character",
              help = "Output PDF path")
)

opt <- parse_args(OptionParser(option_list = option_list))

stopifnot(!is.null(opt$per_boot), !is.null(opt$table2), !is.null(opt$out))

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
per_boot <- fread(opt$per_boot)
table2 <- fread(opt$table2)

# Convert retention to percentage for consistency with table2
per_boot[, retention_pct := retention * 100]

# Extract overlay values from table2
overlays <- table2[, .(trait,
                       unmatched = unmatched_concordance_pct,
                       hou_null  = expected_concordance_hou_pct)]

# ---------------------------------------------------------------------------
# 2. Build violin plot
# ---------------------------------------------------------------------------
# Phase 5 dashboard palette (muted, accessible)
fill_color <- "#4A90D9"
unmatched_color <- "#D94A4A"     # red dashed: unmatched
hou_null_color  <- "#8B8B8B"     # grey dotted: Hou null

p <- ggplot(per_boot, aes(x = trait, y = retention_pct)) +
  geom_violin(fill = fill_color, alpha = 0.6, color = NA) +
  geom_boxplot(width = 0.1, outlier.size = 0.5, fill = "white", alpha = 0.8) +

  # Overlay: unmatched concordance (dashed red)
  geom_hline(
    data = overlays,
    aes(yintercept = unmatched),
    linetype = "dashed", color = unmatched_color, linewidth = 0.7
  ) +

  # Overlay: Hou expected null (dotted grey)
  geom_hline(
    data = overlays,
    aes(yintercept = hou_null),
    linetype = "dotted", color = hou_null_color, linewidth = 0.7
  ) +

  facet_wrap(~trait, scales = "free_x", nrow = 1) +

  labs(
    title = "Matched-N Bootstrap Concordance by Trait (D-06c)",
    subtitle = paste0(
      "Dashed red = unmatched concordance (full EUR N); ",
      "Dotted grey = Hou expected null"
    ),
    x = NULL,
    y = "Tier A retention (%)"
  ) +

  theme_minimal(base_size = 11) +
  theme(
    strip.text = element_text(face = "bold"),
    axis.text.x = element_blank(),
    axis.ticks.x = element_blank(),
    panel.grid.major.x = element_blank(),
    plot.title = element_text(size = 13, face = "bold"),
    plot.subtitle = element_text(size = 9, color = "grey40")
  )

# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------
dir.create(dirname(opt$out), recursive = TRUE, showWarnings = FALSE)
ggsave(opt$out, plot = p, width = 8.5, height = 11, units = "in")
cat("[plot_violin] Saved to", opt$out, "\n")
