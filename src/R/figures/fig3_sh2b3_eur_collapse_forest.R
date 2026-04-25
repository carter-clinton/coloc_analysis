#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# Figure 3 — SH2B3 12q24 EUR identity-LD-vs-real-LD structural-collapse forest
#
# Purpose
# -------
# Two-panel composite (forest + side-annotation table) that surfaces the
# structural credible-set-yield collapse at SH2B3 12q24 EUR under real 1000G
# Phase 3 EUR LD relative to identity-LD fallback. Five EUR traits (asthma,
# bmi, hypertension, stroke, t2d) x two LD conditions = 10 disk-verified data
# points. Companion canonical-pair narrative PP.H4 = 1.0 numbers (BMI x
# hypertension, hypertension x stroke) are surfaced as side annotations only.
#
# Honest framing lock (echoed in the in-figure caption)
# ------------------------------------------------------
# This figure is NOT a literal "PP.H4 with 95% CI" forest. PP.H4 is a posterior
# probability and the production manifest does not store posterior intervals;
# inventing CIs would be methodologically dishonest. The figure's argument is
# structural credible-set-yield collapse + non-convergence under real-LD, with
# locked PP.H4 narrative numbers shown as side annotations only.
#
# Panels
# ------
#   Left  — Per-trait CS-yield mirror bars: identity-LD count (gray) extends
#           leftward from x=0; real-LD count (blue) extends rightward. Bars
#           labelled with n_cs values; non_converged real-LD traits flagged
#           with bold red asterisk + "non_converged" annotation.
#   Right — Locked PP.H4 narrative table (TRACK-A-FROZEN-NUMBERS.md L51 + L79):
#             BMI x hypertension     id-LD PP.H4=1.00  -> real-LD untestable
#             hypertension x stroke  id-LD PP.H4=1.00  -> real-LD untestable
#             asthma x t2d           real-LD coloc.susie status=no_signal; n_cs_a=0
#             ATXN2 / Adrenal_Gland  real-LD QTL coloc PP.H4=0.0517 (below Tier C 0.5)
#
# Caveats
# -------
#   * No 95% CI on PP.H4. Reason stated in caption.
#   * Reference lines at PP.H4 = 0.5 / 0.8 are deliberately omitted because the
#     left panel's X axis is credible-set count, not PP.H4; placing those
#     thresholds on a CS-count axis would mislead.
#   * Real-LD coloc.susie at SH2B3 EUR ran only the asthma_vs_t2d pair on disk
#     (status = no_signal; n_cs_a = 0); the other canonical SH2B3 EUR pairs are
#     absent from the manifest, consistent with credible-set collapse. This is
#     surfaced in the side-annotation panel and the caption.
#
# Data sources (loaded at runtime; cross-checked vs locked scalars)
# -----------------------------------------------------------------
#   results/fine_mapping/finemap_summary.tsv         (Stage 2 real-LD)
#   results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json
#                                                     (identity-LD; 2026-04-25 k2d re-fire)
#
# Locked scalars: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   (canonical source for PP.H4 narrative + per-trait disk-derived CS counts.
#    If Stage 2 is ever re-fired, update that file FIRST then propagate here in
#    the same commit; the cross-checks below will hard-fail otherwise.)
#
# Outputs
# -------
#   docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf  (cairo_pdf, 170 x 110 mm)
#   docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png  (600 dpi, same dims)
#
# Render env
# ----------
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#   R 4.4.2 + ggplot2 4.0.1 + patchwork 1.3.x + scales + jsonlite + readr + dplyr
#
# Invocation
# ----------
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     src/R/figures/fig3_sh2b3_eur_collapse_forest.R
#
# Figure-number provenance: Track A canonical 5-figure roster per
# .planning/amendments/TRACK-A-PIVOT.md §5; manuscript caption block at
# docs/manuscript/track_a_pivot.md L289-L297. Figure 3 = the "survival forest"
# slot per L289-L297. This build resolves §6 item 2 "Decision pending"
# (identity-LD comparison branch existence) using the 2026-04-25 k2d re-fire
# JSONs at results_identity_ld/fine_mapping/susie/.
#
# Author: Carter K. Clinton | Quick task: 260425-1vy
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(jsonlite)
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(patchwork)
  library(scales)
})

# --- Locked scalars from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md ------
# Stage 2 production fire reference: 2026-04-22.
# k2d identity-LD re-fire reference: 2026-04-25.
REGION_ID            <- "SH2B3_12q24"
ANCESTRY             <- "EUR"
TRAITS_EXPECTED      <- c("asthma", "bmi", "hypertension", "stroke", "t2d")
N_TRAITS             <- 5L

# Locked PP.H4 narrative numbers (TRACK-A-FROZEN-NUMBERS.md L51 + L79):
PP_H4_BMI_HTN_LIT    <- 1.0       # narrative; identity-LD coloc.abf at canonical leads
PP_H4_HTN_STROKE_LIT <- 1.0       # narrative; identity-LD coloc.abf at canonical leads
PP_H4_ATXN2_REAL     <- 0.0517    # real-LD QTL coloc.abf; sole quantitative real-LD number
TIER_B_THRESHOLD     <- 0.5       # reference threshold (NOT plotted on left panel)
TIER_A_THRESHOLD     <- 0.8       # reference threshold (NOT plotted on left panel)

# Disk-derived expectations (cross-checked at read time; hard-fail on drift):
EXPECTED_REAL_CS    <- list(asthma = 1L, bmi = 8L, hypertension = 4L,
                            stroke = 2L, t2d = 9L)
EXPECTED_ID_CS      <- list(asthma = 0L, bmi = 3L, hypertension = 10L,
                            stroke = 10L, t2d = 2L)
EXPECTED_REAL_STATUS <- list(asthma = "ok", bmi = "non_converged",
                             hypertension = "non_converged",
                             stroke = "non_converged", t2d = "ok")

# --- Palette (matches fig2 / fig5 / fig1a for visual coherence) -------------
COL_IDENT  <- "#8A8A8A"   # identity-LD bars
COL_REAL   <- "#3B6AA0"   # real-LD bars
COL_FLAG   <- "#C0392B"   # non_converged flag asterisk
COL_TEXT   <- "#4A4A4A"   # body annotations
COL_HEADER <- "#2D2D2D"   # table header

# --- Paths -------------------------------------------------------------------
REAL_TSV   <- "results/fine_mapping/finemap_summary.tsv"
ID_DIR     <- "results_identity_ld/fine_mapping/susie"
OUT_DIR    <- "docs/manuscript/figures"
OUT_PDF    <- file.path(OUT_DIR, "fig3_sh2b3_eur_collapse_forest.pdf")
OUT_PNG    <- file.path(OUT_DIR, "fig3_sh2b3_eur_collapse_forest.png")

# --- Hard-fail propagation message helper -----------------------------------
prop_fail <- function(label, expected, observed) {
  stop(sprintf(
    paste0(
      "fig3_sh2b3_eur_collapse_forest.R: disk-derived %s does not match locked ",
      "scalar from TRACK-A-FROZEN-NUMBERS.md. Expected: %s. Observed: %s. ",
      "If Stage 2 or k2d identity-LD has been re-fired, update ",
      "TRACK-A-FROZEN-NUMBERS.md and this script in the same commit."
    ),
    label, paste(expected, collapse = ","), paste(observed, collapse = ",")
  ))
}

# --- Load real-LD finemap summary -------------------------------------------
if (!file.exists(REAL_TSV)) {
  stop(sprintf("fig3: real-LD TSV missing at '%s'.", REAL_TSV))
}

real_raw <- read_tsv(REAL_TSV, show_col_types = FALSE) |>
  filter(region_id == REGION_ID, ancestry == ANCESTRY) |>
  arrange(trait)

# Cross-check: 5 EUR traits at SH2B3
if (nrow(real_raw) != N_TRAITS) {
  prop_fail(sprintf("real-LD row count at %s/%s", REGION_ID, ANCESTRY),
            N_TRAITS, nrow(real_raw))
}
if (!setequal(real_raw$trait, TRAITS_EXPECTED)) {
  prop_fail("real-LD trait set", TRAITS_EXPECTED, sort(real_raw$trait))
}

# Cross-check: per-trait CS counts + status
for (trt in TRAITS_EXPECTED) {
  obs_cs  <- real_raw$credible_sets[real_raw$trait == trt]
  exp_cs  <- EXPECTED_REAL_CS[[trt]]
  if (!identical(as.integer(obs_cs), as.integer(exp_cs))) {
    prop_fail(sprintf("real-LD credible_sets for %s", trt), exp_cs, obs_cs)
  }
  obs_st  <- real_raw$status[real_raw$trait == trt]
  exp_st  <- EXPECTED_REAL_STATUS[[trt]]
  if (!identical(obs_st, exp_st)) {
    prop_fail(sprintf("real-LD status for %s", trt), exp_st, obs_st)
  }
}

message(sprintf("[load] real-LD: %d rows at %s/%s", nrow(real_raw),
                REGION_ID, ANCESTRY))

# --- Load identity-LD JSONs -------------------------------------------------
load_id_cs <- function(trait) {
  p <- file.path(ID_DIR, sprintf("%s.%s.%s.json", trait, ANCESTRY, REGION_ID))
  if (!file.exists(p)) {
    stop(sprintf("fig3: identity-LD JSON missing for trait '%s' at '%s'.",
                 trait, p))
  }
  j <- fromJSON(p, simplifyVector = FALSE)
  cs <- j$credible_sets
  list(n_cs = if (is.null(cs)) 0L else length(cs),
       status = j$status %||% NA_character_,
       path = p)
}

`%||%` <- function(a, b) if (!is.null(a)) a else b

id_records <- lapply(TRAITS_EXPECTED, load_id_cs)
names(id_records) <- TRAITS_EXPECTED

for (trt in TRAITS_EXPECTED) {
  obs <- id_records[[trt]]$n_cs
  exp <- EXPECTED_ID_CS[[trt]]
  if (!identical(as.integer(obs), as.integer(exp))) {
    prop_fail(sprintf("identity-LD credible_sets for %s", trt), exp, obs)
  }
}

message(sprintf("[load] identity-LD: %d JSONs sourced from %s",
                length(id_records), ID_DIR))
message("Sourced 5 JSONs (identity-LD)")
for (trt in TRAITS_EXPECTED) {
  message(sprintf("  Identity-LD CS yield: trait=%s n_CS=%d", trt,
                  id_records[[trt]]$n_cs))
}

# --- Assemble tidy forest_df ------------------------------------------------
forest_df <- tibble(
  trait        = factor(TRAITS_EXPECTED, levels = rev(TRAITS_EXPECTED)),
  n_cs_id      = vapply(TRAITS_EXPECTED, function(t) id_records[[t]]$n_cs, integer(1)),
  n_cs_real    = vapply(TRAITS_EXPECTED,
                        function(t) as.integer(real_raw$credible_sets[real_raw$trait == t]),
                        integer(1)),
  status_real  = vapply(TRAITS_EXPECTED,
                        function(t) real_raw$status[real_raw$trait == t],
                        character(1)),
  converged_real = vapply(TRAITS_EXPECTED,
                          function(t) real_raw$status[real_raw$trait == t] == "ok",
                          logical(1))
)

message("=== fig3_sh2b3_eur_collapse_forest.R per-trait CS table ===")
print(as.data.frame(forest_df))

# --- Build forest panel (left) ----------------------------------------------
# Mirror geometry: identity-LD bar extends LEFT (negative x); real-LD bar
# extends RIGHT (positive x). Numeric labels placed at the bar's *outer* end
# (away from x=0) so single- and double-digit values align consistently.
x_max <- max(c(forest_df$n_cs_id, forest_df$n_cs_real))

# Asymmetric x-axis: extra width on the right for non_converged flags
x_lo  <- -x_max - 2.0
x_hi  <-  x_max + 9.5

forest_panel <- ggplot(forest_df) +
  # identity-LD (leftward)
  geom_col(aes(x = -n_cs_id, y = trait), fill = COL_IDENT,
           width = 0.6, alpha = 0.92) +
  geom_text(aes(x = -n_cs_id - 0.3, y = trait,
                label = as.character(n_cs_id)),
            hjust = 1, size = 2.4, colour = COL_TEXT,
            fontface = "bold") +
  # real-LD (rightward)
  geom_col(aes(x = n_cs_real, y = trait), fill = COL_REAL,
           width = 0.6, alpha = 0.92) +
  geom_text(aes(x = n_cs_real + 0.3, y = trait,
                label = as.character(n_cs_real)),
            hjust = 0, size = 2.4, colour = COL_TEXT,
            fontface = "bold") +
  # non_converged flag (placed safely past the longest bar; uses its own
  # right-side gutter inside the same scale)
  geom_text(data = filter(forest_df, !converged_real),
            aes(x = x_max + 1.4, y = trait),
            label = "* non_converged",
            size = 2.05, fontface = "italic", colour = COL_FLAG,
            hjust = 0) +
  # central axis line at 0
  geom_vline(xintercept = 0, colour = COL_HEADER, linewidth = 0.5) +
  # subtle dashed grid at integer ticks
  geom_vline(xintercept = c(-10, -5, 5, 10),
             colour = "grey88", linewidth = 0.25, linetype = "dashed") +
  scale_x_continuous(
    limits = c(x_lo, x_hi),
    breaks = c(-10, -5, 0, 5, 10),
    labels = c("10", "5", "0", "5", "10"),
    expand = c(0, 0)
  ) +
  labs(
    title    = "SH2B3 12q24 EUR CS yield",
    subtitle = paste0("gray = identity-LD;  blue = real 1000G Phase 3 EUR LD\n",
                      "* = real-LD status non_converged"),
    x = "n credible sets (identity-LD)  <-  0  ->  n credible sets (real-LD)",
    y = NULL
  ) +
  theme_classic(base_size = 9) +
  theme(
    plot.title    = element_text(size = 9.5, face = "bold"),
    plot.subtitle = element_text(size = 7.0, colour = "grey25",
                                 lineheight = 1.10),
    axis.title.x  = element_text(size = 6.8),
    axis.text.x   = element_text(size = 7),
    axis.text.y   = element_text(face = "italic", size = 8.5),
    axis.line.y   = element_blank(),
    axis.ticks.y  = element_blank(),
    plot.margin   = margin(t = 4, r = 4, b = 4, l = 4)
  )

# --- Build side-annotation panel (right) ------------------------------------
# Locked PP.H4 narrative table; values hard-coded from locked-scalar block.
# Two-line-per-row layout (claim line above, outcome line below) so that
# nothing has to truncate at narrow side-panel widths.
narrative_rows <- tibble(
  ord     = c(4L, 3L, 2L, 1L),
  claim   = c(
    "BMI x hypertension",
    "hypertension x stroke",
    "asthma x t2d  (sole pair on disk)",
    "ATXN2 / Adrenal_Gland"
  ),
  outcome = c(
    sprintf("id-LD PP.H4 = %.2f  ->  real-LD untestable", PP_H4_BMI_HTN_LIT),
    sprintf("id-LD PP.H4 = %.2f  ->  real-LD untestable", PP_H4_HTN_STROKE_LIT),
    "real-LD coloc.susie status = no_signal; n_cs_a = 0",
    sprintf("real-LD QTL coloc PP.H4 = %.4f  (< 0.5)", PP_H4_ATXN2_REAL)
  )
)

annotation_panel <- ggplot(narrative_rows) +
  # Header bar
  annotate("rect", xmin = 0, xmax = 10, ymin = 4.65, ymax = 5.20,
           fill = COL_HEADER, colour = NA) +
  annotate("text", x = 0.2, y = 4.93,
           label = "Identity-LD claim  ->  Real-LD outcome",
           hjust = 0, vjust = 0.5, size = 2.5, colour = "white",
           fontface = "bold") +
  # Row backgrounds (alternating subtle stripes)
  geom_rect(aes(xmin = 0, xmax = 10, ymin = ord - 0.42, ymax = ord + 0.42),
           fill = rep(c("white", "grey95"), length.out = nrow(narrative_rows)),
           colour = NA) +
  # Claim line (bold)
  geom_text(aes(x = 0.2, y = ord + 0.16, label = claim),
            hjust = 0, vjust = 0.5, size = 2.1, colour = COL_HEADER,
            fontface = "bold") +
  # Outcome line
  geom_text(aes(x = 0.2, y = ord - 0.18, label = outcome),
            hjust = 0, vjust = 0.5, size = 1.95, colour = COL_TEXT) +
  scale_x_continuous(limits = c(0, 10), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0.4, 5.5), expand = c(0, 0)) +
  labs(
    title = "Locked PP.H4 narrative",
    subtitle = "TRACK-A-FROZEN-NUMBERS.md  (no posterior CIs plotted)"
  ) +
  theme_void(base_size = 8) +
  theme(
    plot.title    = element_text(size = 8.5, face = "bold",
                                 colour = COL_HEADER, hjust = 0,
                                 margin = margin(b = 1)),
    plot.subtitle = element_text(size = 6.8, colour = "grey30", hjust = 0,
                                 margin = margin(b = 4)),
    plot.margin   = margin(t = 4, r = 4, b = 4, l = 4)
  )

# --- Composite assembly -----------------------------------------------------
composite <- forest_panel + annotation_panel +
  plot_layout(widths = c(1.55, 1.45)) +
  plot_annotation(
    caption = paste0(
      "Figure 3. Structural collapse of identity-LD signal at SH2B3 12q24 EUR under real-LD re-analysis.\n",
      "Left panel: per-trait SuSiE-RSS credible-set yield at SH2B3_12q24 EUR under identity-LD fallback ",
      "(gray, leftward) vs real 1000G Phase 3 EUR LD (blue, rightward). Asterisks mark traits with ",
      "status=non_converged under real-LD (4 of 5 EUR traits).\n",
      "Right panel: locked PP.H4 narrative numbers from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md ",
      "(Stage 2 production fire 2026-04-22). PP.H4 95% confidence intervals are not shown - PP.H4 is a ",
      "posterior probability and the production manifest does not store posterior intervals; inventing ",
      "them would be methodologically dishonest. The figure's argument is structural credible-set-yield ",
      "collapse plus non-convergence under real-LD, with PP.H4 endpoints as locked side annotations.\n",
      "Sources: results/fine_mapping/finemap_summary.tsv (real-LD); ",
      "results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json (identity-LD; 2026-04-25 k2d re-fire); ",
      "results/qtl_coloc/tier_assignments.tsv (PP.H4=0.0517 ATXN2 / Adrenal_Gland)."
    ),
    theme = theme(plot.caption = element_text(size = 6.5, colour = "grey30",
                                              hjust = 0, lineheight = 1.15,
                                              margin = margin(t = 5)))
  )

# --- Render -----------------------------------------------------------------
dir.create(OUT_DIR, recursive = TRUE, showWarnings = FALSE)

if (!isTRUE(capabilities("cairo"))) {
  stop("fig3_sh2b3_eur_collapse_forest.R: R build lacks cairo capability.")
}

ggsave(OUT_PDF, composite, width = 180, height = 110, units = "mm",
       device = cairo_pdf)
ggsave(OUT_PNG, composite, width = 180, height = 110, units = "mm",
       dpi = 600)

# --- Diagnostic stdout (verified by Task 2 verify block) --------------------
message("=== fig3_sh2b3_eur_collapse_forest.R diagnostic ===")
message(sprintf("Region: %s   Ancestry: %s   Traits: %d", REGION_ID, ANCESTRY, N_TRAITS))
message("Per-trait CS yield (identity-LD -> real-LD):")
for (i in seq_len(nrow(forest_df))) {
  trt <- as.character(forest_df$trait[i])
  message(sprintf("  %-13s id_cs=%2d  ->  real_cs=%2d  status=%s",
                  trt, forest_df$n_cs_id[i], forest_df$n_cs_real[i],
                  forest_df$status_real[i]))
}
message(sprintf("Locked narrative PP.H4 (TRACK-A-FROZEN-NUMBERS.md L51 + L79):"))
message(sprintf("  BMI x hypertension      id-LD = %.2f", PP_H4_BMI_HTN_LIT))
message(sprintf("  hypertension x stroke   id-LD = %.2f", PP_H4_HTN_STROKE_LIT))
message(sprintf("  ATXN2 / Adrenal_Gland   real-LD = %.4f", PP_H4_ATXN2_REAL))
message(sprintf("Render OUT_PDF=%s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))
message(sprintf("Render OUT_PNG=%s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))
message("Figure 3 render complete.")
