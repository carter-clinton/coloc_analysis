# fig2_cs_yield.R — Track A Figure 2 (identity-LD vs real-LD credible-set yield)
#
# Purpose: Build the headline-yield figure for the Track A pivot manuscript —
#   a two-bar comparison of non-empty SuSiE-RSS credible-set counts under
#   identity-LD fallback (48 / 95) vs real 1000G Phase 3 EUR LD (51 / 96).
#   Under the matched-coverage comparator the contrast is ~1.06x fold
#   increase under matched-coverage comparator. This figure must make
#   that delta legible at a single-column width.
#
# Comparator-tightening note (2026-04-25, propagated by quick-260425-kki):
#   We tightened the comparator from a partial-coverage Stage 1d narrow-
#   validation baseline (12/96, 2 of 10 admissible regions had identity-LD
#   fits) to the matched-coverage k2d full-coverage 2026-04-25 re-fire
#   (48/95 vs 51/96 = 1.06x yield); the inflation magnitude shifted from
#   4.25x to ~1.06x. The 12/96 baseline is preserved verbatim under a
#   SUPERSEDED 2026-04-25 per quick-260425-kki markup in TRACK-A-FROZEN-
#   NUMBERS.md for audit traceability.
#
# Data sources (loaded at runtime; cross-checked vs disk-truth):
#   results/fine_mapping/finemap_summary.tsv
#     (Stage 2 production fire, 2026-04-22 — 97 lines = 1 header + 96 admissible fits.)
#   .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv
#     (k2d full-coverage identity-LD re-fire, 2026-04-25 — 96 lines = 1 header + 95 fits.)
#   The 51 non-empty real-LD count and 48 non-empty identity-LD count are
#   each derived at runtime from disk and cross-checked against the
#   expected scalars to catch any silent drift.
#
# Authoritative ledger: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   (canonical source of the 48 / 95 / 51 / 96 / 1.06x matched-coverage
#    contrast; if Stage 2 or k2d numbers ever shift, update that file
#    FIRST then propagate here in the same commit.)
#
# Upstream plans:
#   .planning/amendments/ID-VS-REF-LD-STRATEGY.md §5 (figure spec)
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
# Author: Carter K. Clinton -- 2026-04-24 (built quick-260424-lpy; aligned quick-260424-mqo;
#         comparator-tightened quick-260425-kki 2026-04-25)
#
# Figure-number provenance (R2 alignment pass, quick-260424-mqo, 2026-04-24):
#   Filename stem is now 'fig2_cs_yield' to align with the canonical 5-figure
#   manuscript scheme. Authoritative slot owners:
#     - docs/manuscript/id-vs-ref-LD.md L289-L297 (live manuscript captions)
#     - .planning/amendments/ID-VS-REF-LD-STRATEGY.md §5 (canonical id-vs-ref-LD strategy figure spec)
#   Both place this credible-set-yield artifact at the Figure 2 slot. The earlier
#   workspace-plan sketch (snappy-humming-pine.md §2.3) labelled this as "Fig 1"
#   in a 3-figure scheme; that integer numbering is an early sketch and is
#   reconciled to the manuscript-canonical scheme by quick-260424-mqo (see the
#   §2.3 R2-reconciliation annotation in snappy-humming-pine.md). The matched-
#   coverage scalars (48 / 95 / 51 / 96 / 1.06x) are anchored at
#   TRACK-A-FROZEN-NUMBERS.md.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(scales)
})

# --- Disk-truth scalars (matched-coverage k2d re-fire 2026-04-25) -------------
# These are expected values derived from disk; the fits TSVs are read at runtime
# below and the assertions hard-fail if any value drifts. If k2d or Stage 2 are
# re-fired, update .planning/amendments/TRACK-A-FROZEN-NUMBERS.md FIRST, then
# update these scalars in the same commit.

# k2d identity-LD full-coverage re-fire (2026-04-25); disk-truth source.
IDENTITY_LD_TSV          <- ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"
N_IDENTITY_LD_TOTAL_EXPECTED <- 95L     # k2d enumerated 95 of 96 fits
N_IDENTITY_LD_NONEMPTY_EXPECTED <- 48L  # disk-derived assertion
N_TOTAL_FITS             <- 96L         # Stage 2 real-LD admissible-fit denominator
N_REAL_LD_NONEMPTY       <- 51L         # Stage 2 real-LD; cross-checked against disk

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

# Disk-backed derivation for identity-LD baseline (matched-coverage k2d, 2026-04-25)
if (!file.exists(IDENTITY_LD_TSV)) {
  stop(sprintf(
    "fig2_cs_yield.R: identity-LD source TSV not found at '%s'. Run from project root.",
    IDENTITY_LD_TSV
  ))
}
df_id <- read_tsv(IDENTITY_LD_TSV, show_col_types = FALSE,
                  col_types = cols(.default = col_character()))
df_id$n_CS <- suppressWarnings(as.integer(df_id$n_CS))
stopifnot(nrow(df_id) == N_IDENTITY_LD_TOTAL_EXPECTED)
n_id_nonempty <- sum(df_id$n_CS > 0, na.rm = TRUE)
if (n_id_nonempty != N_IDENTITY_LD_NONEMPTY_EXPECTED) {
  stop(sprintf(
    paste0(
      "fig2_cs_yield.R: disk-derived identity-LD non-empty CS count (%d) does not match ",
      "expected k2d full-coverage value %d from IDENTITY-LD-K2D-FIT-SUMMARY.tsv. ",
      "If k2d has been re-fired, update the expected scalar here and TRACK-A-FROZEN-NUMBERS.md ",
      "in the same commit."
    ),
    n_id_nonempty, N_IDENTITY_LD_NONEMPTY_EXPECTED
  ))
}
N_IDENTITY_LD_TOTAL <- nrow(df_id)

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
message(sprintf("Total real-LD fits parsed: %d (expected %d)", nrow(df), N_TOTAL_FITS))
message(sprintf("Total identity-LD fits parsed: %d (expected %d)", nrow(df_id), N_IDENTITY_LD_TOTAL_EXPECTED))
message(sprintf("Identity-LD non-empty fits (k2d full-coverage 2026-04-25): %d / %d",
                n_id_nonempty, N_IDENTITY_LD_TOTAL))
message(sprintf("Real-LD non-empty fits (Stage 2 2026-04-22): %d / %d",
                n_real_nonempty, N_TOTAL_FITS))
message(sprintf("Empty real-LD fits: %d (expected %d)", n_real_empty, N_TOTAL_FITS - N_REAL_LD_NONEMPTY))
message(sprintf("Identity-LD baseline (disk-derived from IDENTITY-LD-K2D-FIT-SUMMARY.tsv, k2d full-coverage 2026-04-25): %d", n_id_nonempty))
message(sprintf("Fold change (matched-coverage): %.3fx (%d / %d)",
                n_real_nonempty / n_id_nonempty, n_real_nonempty, n_id_nonempty))
message("=== per-ancestry x per-trait CS-yield split (Stage 2 real-LD) ===")
print(as.data.frame(diag))

# --- Plot data ---------------------------------------------------------------
lvl_id   <- "Identity-LD fallback\n(k2d 2026-04-25)"
lvl_real <- "Real 1000G Phase 3 EUR LD\n(Stage 2 2026-04-22)"

plot_df <- tibble::tibble(
  condition = factor(
    c(lvl_id, lvl_real),
    levels = c(lvl_id, lvl_real)
  ),
  n_nonempty = c(n_id_nonempty, n_real_nonempty),
  label = c(
    sprintf("%d / %d  (%.1f%%)",
            n_id_nonempty, N_IDENTITY_LD_TOTAL,
            100 * n_id_nonempty / N_IDENTITY_LD_TOTAL),
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
    "text",
    x = 1.5, y = 65,
    label = sprintf("%.2fx yield\n(matched-coverage)",
                    n_real_nonempty / n_id_nonempty),
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
    title    = "SuSiE-RSS credible-set yield under matched-coverage comparator",
    subtitle = "Real 1000G Phase 3 EUR LD vs identity-LD fallback (k2d full-coverage 2026-04-25) -- ~1.06x fold increase under matched-coverage comparator",
    x        = "LD reference panel",
    y        = "Non-empty credible sets (count)",
    caption  = paste0(
      "Sources: results/fine_mapping/finemap_summary.tsv (Stage 2 real-LD, 2026-04-22) +\n",
      ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (k2d full-coverage identity-LD, 2026-04-25).\n",
      "Matched-coverage comparator: 48 of 95 identity-LD fits vs 51 of 96 real-LD fits = ~1.06x yield.\n",
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
message(sprintf("fold-change: %.3fx (%d real-LD / %d identity-LD k2d)",
                n_real_nonempty / n_id_nonempty, n_real_nonempty, n_id_nonempty))
message(sprintf("counts: identity-LD=%d/%d, real-LD=%d/%d",
                n_id_nonempty, N_IDENTITY_LD_TOTAL, n_real_nonempty, N_TOTAL_FITS))
message(sprintf("wrote %s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))
message(sprintf("wrote %s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))
