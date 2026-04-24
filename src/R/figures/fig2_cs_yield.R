# fig2_cs_yield.R — Track A Figure 2 (identity-LD vs real-LD credible-set yield)
#
# Purpose: Build the headline-yield figure for the Track A pivot manuscript —
#   a two-bar comparison of non-empty SuSiE-RSS credible-set counts under
#   identity-LD fallback (12 / 96) vs real 1000G Phase 3 EUR LD (51 / 96).
#   The 4.25x fold increase is the single most load-bearing methodological
#   claim of the Track A "identity-LD inflation" audit. This figure must make
#   that delta unmissable at a single-column width.
#
# Data source: results/fine_mapping/finemap_summary.tsv
#   (Stage 2 production fire, 2026-04-22 — 97 lines = 1 header + 96 admissible fits).
#   The 51 non-empty credible-set count is derived at runtime from disk and
#   cross-checked against the locked scalar to catch any silent drift.
#
# Locked scalars: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   (canonical source of the 12 identity-LD baseline and 51 real-LD / 96 total /
#    4.25x fold-change; if Stage 2 numbers ever shift, update that file FIRST
#    then propagate here in the same commit.)
#
# Upstream plans:
#   .planning/amendments/TRACK-A-PIVOT.md §5 (figure spec)
#   /home/ckclinto/.claude/plans/snappy-humming-pine.md §2.3 ("Fig 1 = CS yield")
#
# Outputs:
#   docs/manuscript/figures/fig2_cs_yield.pdf  (cairo_pdf, 85 mm x 70 mm)
#   docs/manuscript/figures/fig2_cs_yield.png  (600 dpi, 85 mm x 70 mm)
#
# Render env: /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#   (R 4.4.2, ggplot2 4.0.1, tidyverse 2.0.0, scales 1.4.0; cairo capability verified.)
#
# Invocation (from project root):
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig2_cs_yield.R
#
# Author: Carter K. Clinton -- 2026-04-24 (built quick-260424-lpy; aligned quick-260424-mqo)
#
# Figure-number provenance (R2 alignment pass, quick-260424-mqo, 2026-04-24):
#   Filename stem is now 'fig2_cs_yield' to align with the canonical 5-figure
#   manuscript scheme. Authoritative slot owners:
#     - docs/manuscript/track_a_pivot.md L289-L297 (live manuscript captions)
#     - .planning/amendments/TRACK-A-PIVOT.md §5 (canonical pivot-plan figure spec)
#   Both place this credible-set-yield artifact at the Figure 2 slot. The earlier
#   workspace-plan sketch (snappy-humming-pine.md §2.3) labelled this as "Fig 1"
#   in a 3-figure scheme; that integer numbering is an early sketch and is
#   reconciled to the manuscript-canonical scheme by quick-260424-mqo (see the
#   §2.3 R2-reconciliation annotation in snappy-humming-pine.md). Locked scalars
#   (12 / 96 / 51 / 4.25x) remain authoritative at TRACK-A-FROZEN-NUMBERS.md.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(scales)
})

# --- Locked scalars from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md --------
# If any of these change, update TRACK-A-FROZEN-NUMBERS.md FIRST, then this file
# in the same commit. The cross-check below will hard-fail otherwise.
N_TOTAL_FITS           <- 96L    # Stage 2 admissible-fit denominator
N_IDENTITY_LD_NONEMPTY <- 12L    # pre-Stage-2 identity-LD fallback baseline
N_REAL_LD_NONEMPTY     <- 51L    # Stage 2 expected; cross-checked against disk below
FOLD_CHANGE_EXPECTED   <- 4.25   # 51 / 12 = 4.25

INPUT_TSV <- "results/fine_mapping/finemap_summary.tsv"
OUT_DIR   <- "docs/manuscript/figures"
OUT_PDF   <- file.path(OUT_DIR, "fig2_cs_yield.pdf")
OUT_PNG   <- file.path(OUT_DIR, "fig2_cs_yield.png")

# --- Input validation + disk-backed derivation -------------------------------
if (!file.exists(INPUT_TSV)) {
  stop(sprintf(
    "fig2_cs_yield.R: input TSV not found at '%s'. Run from project root (/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis).",
    INPUT_TSV
  ))
}

df <- read_tsv(INPUT_TSV, show_col_types = FALSE)

stopifnot(nrow(df) == N_TOTAL_FITS)  # frozen denominator; TRACK-A-FROZEN-NUMBERS.md

n_real_nonempty <- sum(df$credible_sets > 0, na.rm = TRUE)
n_real_empty    <- N_TOTAL_FITS - n_real_nonempty

if (n_real_nonempty != N_REAL_LD_NONEMPTY) {
  stop(sprintf(
    paste0(
      "fig2_cs_yield.R: disk-derived non-empty CS count (%d) does not match locked ",
      "scalar N_REAL_LD_NONEMPTY = %d from TRACK-A-FROZEN-NUMBERS.md. ",
      "If Stage 2 has been re-fired, update TRACK-A-FROZEN-NUMBERS.md and this script ",
      "in the same commit."
    ),
    n_real_nonempty, N_REAL_LD_NONEMPTY
  ))
}

# --- Diagnostic: per-ancestry x per-trait CS-yield split ---------------------
diag <- df |>
  mutate(has_cs = credible_sets > 0) |>
  count(ancestry, trait, has_cs) |>
  tidyr::pivot_wider(
    names_from  = has_cs,
    values_from = n,
    values_fill = 0L,
    names_prefix = "cs_"
  )

message("=== fig2_cs_yield.R diagnostic ===")
message(sprintf("Total fits parsed: %d (expected %d)", nrow(df), N_TOTAL_FITS))
message(sprintf("Non-empty real-LD fits: %d (expected %d)", n_real_nonempty, N_REAL_LD_NONEMPTY))
message(sprintf("Empty real-LD fits: %d (expected %d)", n_real_empty, N_TOTAL_FITS - N_REAL_LD_NONEMPTY))
message(sprintf("Identity-LD fallback baseline: %d (locked from TRACK-A-FROZEN-NUMBERS.md)", N_IDENTITY_LD_NONEMPTY))
message(sprintf("Fold change: %.2fx", n_real_nonempty / N_IDENTITY_LD_NONEMPTY))
message("=== per-ancestry x per-trait CS-yield split (Stage 2 real-LD) ===")
print(as.data.frame(diag))

# --- Plot data ---------------------------------------------------------------
lvl_id   <- "Identity-LD fallback\n(pre-Stage-2)"
lvl_real <- "Real 1000G Phase 3 EUR LD\n(Stage 2)"

plot_df <- tibble::tibble(
  condition = factor(
    c(lvl_id, lvl_real),
    levels = c(lvl_id, lvl_real)
  ),
  n_nonempty = c(N_IDENTITY_LD_NONEMPTY, n_real_nonempty),
  label = c(
    sprintf("%d / %d  (%.1f%%)",
            N_IDENTITY_LD_NONEMPTY, N_TOTAL_FITS,
            100 * N_IDENTITY_LD_NONEMPTY / N_TOTAL_FITS),
    sprintf("%d / %d  (%.1f%%)",
            n_real_nonempty, N_TOTAL_FITS,
            100 * n_real_nonempty / N_TOTAL_FITS)
  )
)

# --- ggplot build ------------------------------------------------------------
plot <- ggplot(plot_df, aes(x = condition, y = n_nonempty, fill = condition)) +
  geom_col(width = 0.6, show.legend = FALSE) +
  geom_text(aes(label = label), vjust = -0.6, size = 2.8) +
  geom_hline(
    yintercept = N_TOTAL_FITS,
    linetype   = "dashed",
    colour     = "grey50",
    linewidth  = 0.3
  ) +
  annotate(
    "text",
    x = 2.45, y = N_TOTAL_FITS,
    label = "96 admissible fits",
    hjust = 1, vjust = -0.5,
    size = 2.6, colour = "grey30"
  ) +
  annotate(
    "segment",
    x = 1.1, xend = 1.9, y = 15, yend = 55,
    arrow = arrow(length = unit(2, "mm")),
    colour = "grey40", linewidth = 0.3
  ) +
  annotate(
    "text",
    x = 1.5, y = 82,
    label = sprintf("%.2fx yield\nunder real-LD",
                    n_real_nonempty / N_IDENTITY_LD_NONEMPTY),
    size = 3, fontface = "bold", lineheight = 0.95
  ) +
  scale_y_continuous(
    limits = c(0, 105),
    breaks = c(0, 25, 50, 75, 96),
    expand = expansion(mult = c(0, 0.02))
  ) +
  scale_fill_manual(
    values = setNames(
      c("#8A8A8A", "#3B6AA0"),
      c(lvl_id, lvl_real)
    )
  ) +
  coord_cartesian(clip = "off") +
  labs(
    title    = "SuSiE-RSS credible-set yield across 96 admissible fits",
    subtitle = "Real 1000G Phase 3 EUR LD vs identity-LD fallback -- 4.25x fold increase",
    x        = "LD reference panel",
    y        = "Non-empty credible sets (count)",
    caption  = paste0(
      "Source: results/fine_mapping/finemap_summary.tsv (Stage 2, 2026-04-22 production fire).\n",
      "Identity-LD scalar baseline from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (canonical).\n",
      "EUR + AFR admissible fits pooled for credible-set-yield count."
    )
  ) +
  theme_classic(base_size = 9) +
  theme(
    plot.title    = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 8.5, colour = "grey25"),
    plot.caption  = element_text(size = 6.5, colour = "grey30", hjust = 0, lineheight = 1.0),
    axis.text.x   = element_text(size = 8, lineheight = 0.9),
    plot.margin   = margin(t = 5, r = 8, b = 5, l = 5)
  )

# --- Save --------------------------------------------------------------------
dir.create(OUT_DIR, recursive = TRUE, showWarnings = FALSE)

if (!isTRUE(capabilities("cairo"))) {
  stop("fig2_cs_yield.R: R build lacks cairo capability; cairo_pdf unavailable. Aborting rather than falling back to pdf() (font handling differs).")
}

message("=== writing outputs ===")
message(sprintf("  %s", OUT_PDF))
message(sprintf("  %s", OUT_PNG))

ggsave(OUT_PDF, plot, width = 85, height = 70, units = "mm", device = cairo_pdf)
ggsave(OUT_PNG, plot, width = 85, height = 70, units = "mm", dpi = 600)

# --- Post-save verification stdout (asserted by Task 2 verify block) ---------
message(sprintf("fold-change: %.2fx (51/12 baseline)", n_real_nonempty / N_IDENTITY_LD_NONEMPTY))
message(sprintf("counts: identity-LD=12, real-LD=%d, empty=%d, total=%d",
                n_real_nonempty, n_real_empty, N_TOTAL_FITS))
message(sprintf("wrote %s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))
message(sprintf("wrote %s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))
