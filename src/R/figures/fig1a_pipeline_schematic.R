#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# Figure 1A — Track A real-LD audit pipeline schematic (methods overview)
#
# Purpose
# -------
# Single-page 5-panel logical-flow schematic for the Track A pipeline. This is
# a methods-overview figure rendered entirely from ggplot geometric primitives
# (geom_rect / geom_segment / geom_text / geom_label) plus a patchwork
# composite. NO data files are read; all numeric labels are hard-coded scalars
# sourced from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (Stage 2
# production fire, 2026-04-22). Companion to Figure 1B (regional CS-membership
# panels).
#
# Panels
# ------
#   1. Input universe — 50 candidate loci × 5 traits (BMI, T2D, hypertension,
#      stroke, asthma) × 2 ancestries (EUR, AFR). Stacked label tiers.
#   2. Methodological fork — identity-LD branch (gray) vs real 1000G Phase 3
#      EUR LD branch (blue) diverge from a common stem.
#   3. Admissibility filter — 10 EUR autosomal curated regions admitted to
#      real-LD; HLA_6p21 + BMI_Xq24 + all AFR remain on identity-LD fallback
#      (caveat box).
#   4. Two coloc engines — coloc.susie (28 trait-pair attempts) and
#      coloc.abf via run_qtl_coloc.R (1,274 QTL attempts).
#   5. Tier + negative-control endpoint — 0 Tier A, 0 Tier B, 9 Tier C,
#      224 negative-control rows.
#
# Caveats
# -------
#   * Geometric primitives only. No data joins, no readr / jsonlite imports.
#     Counts are hard-coded scalars from TRACK-A-FROZEN-NUMBERS.md.
#   * Identity-LD vs real-LD branches are quantitatively analyzed in
#     Figures 1B, 2, 3, 5; this Figure 1A summarises the methodological flow.
#   * Counts must be propagated through TRACK-A-FROZEN-NUMBERS.md FIRST if
#     Stage 2 is ever re-fired; this file then propagates in the same commit.
#
# Data sources
# ------------
#   None at runtime (geometric-primitive figure).
#   Citations: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (frozen scalars).
#
# Outputs
# -------
#   docs/manuscript/figures/fig1a_pipeline_schematic.pdf  (cairo_pdf, 170 x 100 mm)
#   docs/manuscript/figures/fig1a_pipeline_schematic.png  (600 dpi, same dims)
#
# Render env
# ----------
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#   R 4.4.2 + ggplot2 4.0.1 + patchwork 1.3.x + grid (base)
#
# Invocation
# ----------
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     src/R/figures/fig1a_pipeline_schematic.R
#
# Figure-number provenance: Track A canonical 5-figure roster per
# .planning/amendments/ID-VS-REF-LD-STRATEGY.md §5; manuscript caption block at
# docs/manuscript/id-vs-ref-LD.md L289-L297. Figure 1 Panel A is the
# methods-overview companion to Figure 1B (regional anchor-locus composite).
#
# Author: Carter K. Clinton | Quick task: 260425-1vy
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(grid)
})

# --- Locked scalars from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md ------
# If any of these change, update TRACK-A-FROZEN-NUMBERS.md FIRST, then this
# file in the same commit. Stage 2 production fire reference: 2026-04-22.
N_LOCI                <- 50L     # candidate-locus panel size
N_TRAITS              <- 5L      # BMI, T2D, hypertension, stroke, asthma
N_ANCESTRIES          <- 2L      # EUR, AFR
N_ADMISSIBLE_REAL_LD  <- 10L     # EUR autosomal curated regions admitted
N_PAIRWISE_ATTEMPTS   <- 28L     # trait-pair coloc.susie attempts
N_QTL_ATTEMPTS        <- 1274L   # QTL coloc.abf attempts (run_qtl_coloc.R)
N_TIER_A              <- 0L      # locked
N_TIER_B              <- 0L      # locked
N_TIER_C              <- 9L      # 4 AFR + 5 EUR
N_NEG_CTRL            <- 224L    # cosmetic + blood_group + hla_immune

# --- Palette (matches fig2_cs_yield.R for visual coherence) ------------------
COL_IDENT  <- "#8A8A8A"   # identity-LD branch / non-admitted regions
COL_REAL   <- "#3B6AA0"   # real-LD branch / admitted regions / Tier C
COL_NEG    <- "#F2A65A"   # negative-control accent
COL_TEXT   <- "#4A4A4A"   # body annotations
COL_PANEL  <- "#FFFFFF"   # panel background
COL_BORDER <- "#2D2D2D"   # panel borders

OUT_DIR    <- "docs/manuscript/figures"
OUT_PDF    <- file.path(OUT_DIR, "fig1a_pipeline_schematic.pdf")
OUT_PNG    <- file.path(OUT_DIR, "fig1a_pipeline_schematic.png")

# --- Empty-canvas theme (no axes, no grid) -----------------------------------
empty_theme <- theme_void(base_size = 8) +
  theme(
    plot.title = element_text(size = 8.5, face = "bold", hjust = 0.5,
                              colour = COL_BORDER, margin = margin(b = 2)),
    plot.margin = margin(t = 4, r = 4, b = 4, l = 4)
  )

# --- Panel 1: Input universe -------------------------------------------------
# Three stacked tiers of locked counts.
panel_1_data <- data.frame(
  y     = c(3.0, 2.0, 1.0),
  label = c(sprintf("%d candidate loci", N_LOCI),
            sprintf("%d traits", N_TRAITS),
            sprintf("%d ancestries", N_ANCESTRIES)),
  sub   = c("",
            "BMI, T2D, hypertension, stroke, asthma",
            "EUR, AFR"),
  stringsAsFactors = FALSE
)

panel_1 <- ggplot(panel_1_data) +
  geom_rect(aes(xmin = 0.05, xmax = 1.95, ymin = y - 0.42, ymax = y + 0.42),
            fill = "white", colour = COL_BORDER, linewidth = 0.35) +
  geom_text(aes(x = 1.0, y = y + 0.12, label = label),
            size = 2.7, colour = COL_TEXT, fontface = "bold") +
  geom_text(aes(x = 1.0, y = y - 0.18, label = sub),
            size = 1.95, colour = COL_TEXT, fontface = "italic") +
  annotate("segment", x = 1.0, xend = 1.0, y = 2.55, yend = 2.43,
           arrow = arrow(length = unit(1.4, "mm"), type = "closed"),
           colour = COL_TEXT, linewidth = 0.3) +
  annotate("segment", x = 1.0, xend = 1.0, y = 1.55, yend = 1.43,
           arrow = arrow(length = unit(1.4, "mm"), type = "closed"),
           colour = COL_TEXT, linewidth = 0.3) +
  scale_x_continuous(limits = c(0, 2), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0.4, 3.6), expand = c(0, 0)) +
  labs(title = "1. Input universe") +
  empty_theme

# --- Panel 2: Methodological fork -------------------------------------------
# Common stem -> two divergent arrows (identity-LD gray, real-LD blue).
panel_2 <- ggplot() +
  annotate("label", x = 1.0, y = 3.45, label = "harmonized sumstats",
           size = 2.4, colour = COL_TEXT, fontface = "bold",
           fill = "white") +
  annotate("segment", x = 1.0, xend = 1.0, y = 3.15, yend = 2.7,
           colour = COL_TEXT, linewidth = 0.45) +
  annotate("segment", x = 1.0, xend = 0.35, y = 2.65, yend = 1.75,
           arrow = arrow(length = unit(1.6, "mm"), type = "closed"),
           colour = COL_IDENT, linewidth = 0.55) +
  annotate("segment", x = 1.0, xend = 1.65, y = 2.65, yend = 1.75,
           arrow = arrow(length = unit(1.6, "mm"), type = "closed"),
           colour = COL_REAL,  linewidth = 0.55) +
  annotate("label", x = 0.35, y = 1.4, label = "identity-LD\nfallback",
           size = 2.3, colour = "white", fontface = "bold",
           fill = COL_IDENT, lineheight = 0.95) +
  annotate("label", x = 1.65, y = 1.4, label = "real 1000G\nPhase 3 LD",
           size = 2.3, colour = "white", fontface = "bold",
           fill = COL_REAL, lineheight = 0.95) +
  scale_x_continuous(limits = c(-0.05, 2.05), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0.6, 3.85), expand = c(0, 0)) +
  labs(title = "2. Methodological fork") +
  empty_theme

# --- Panel 3: Admissibility filter ------------------------------------------
# Funnel-style cascade: full universe -> 10 EUR autosomal admitted.
panel_3 <- ggplot() +
  # Top tier: full universe
  annotate("rect", xmin = 0.1, xmax = 1.9, ymin = 3.05, ymax = 3.55,
           fill = "white", colour = COL_BORDER, linewidth = 0.3) +
  annotate("text", x = 1.0, y = 3.30,
           label = sprintf("%d loci x %d ancestries", N_LOCI, N_ANCESTRIES),
           size = 2.4, colour = COL_TEXT, fontface = "bold") +
  # Funnel polygon
  annotate("polygon",
           x = c(0.1, 1.9, 1.55, 0.45),
           y = c(3.05, 3.05, 2.55, 2.55),
           fill = COL_REAL, alpha = 0.20, colour = NA) +
  annotate("segment", x = 1.0, xend = 1.0, y = 2.50, yend = 2.20,
           arrow = arrow(length = unit(1.4, "mm"), type = "closed"),
           colour = COL_TEXT, linewidth = 0.3) +
  # Admitted tier (real-LD)
  annotate("rect", xmin = 0.45, xmax = 1.55, ymin = 1.62, ymax = 2.18,
           fill = COL_REAL, colour = COL_BORDER, linewidth = 0.3) +
  annotate("text", x = 1.0, y = 1.90,
           label = sprintf("%d EUR autosomal\nregions admitted",
                           N_ADMISSIBLE_REAL_LD),
           size = 2.2, colour = "white", fontface = "bold",
           lineheight = 0.95) +
  # Caveat box (identity-LD fallback)
  annotate("rect", xmin = 0.10, xmax = 1.90, ymin = 0.65, ymax = 1.35,
           fill = COL_IDENT, alpha = 0.18, colour = COL_IDENT,
           linewidth = 0.3, linetype = "dashed") +
  annotate("text", x = 1.0, y = 1.00,
           label = "fallback: HLA_6p21,\nBMI_Xq24, all AFR",
           size = 2.1, colour = COL_TEXT, fontface = "italic",
           lineheight = 0.95) +
  scale_x_continuous(limits = c(0, 2), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0.4, 3.7), expand = c(0, 0)) +
  labs(title = "3. Admissibility filter") +
  empty_theme

# --- Panel 4: Two coloc engines ---------------------------------------------
panel_4 <- ggplot() +
  # coloc.susie box
  annotate("rect", xmin = 0.05, xmax = 0.95, ymin = 1.7, ymax = 2.85,
           fill = "white", colour = COL_REAL, linewidth = 0.5) +
  annotate("text", x = 0.5, y = 2.62, label = "coloc.susie",
           size = 2.6, colour = COL_REAL, fontface = "bold") +
  annotate("text", x = 0.5, y = 2.32, label = "(trait-pair)",
           size = 2.0, colour = COL_TEXT, fontface = "italic") +
  annotate("text", x = 0.5, y = 1.95,
           label = sprintf("%d attempts", N_PAIRWISE_ATTEMPTS),
           size = 2.5, colour = COL_TEXT, fontface = "bold") +
  # coloc.abf box
  annotate("rect", xmin = 1.05, xmax = 1.95, ymin = 1.7, ymax = 2.85,
           fill = "white", colour = COL_REAL, linewidth = 0.5) +
  annotate("text", x = 1.5, y = 2.62, label = "coloc.abf",
           size = 2.6, colour = COL_REAL, fontface = "bold") +
  annotate("text", x = 1.5, y = 2.32, label = "(QTL)",
           size = 2.0, colour = COL_TEXT, fontface = "italic") +
  annotate("text", x = 1.5, y = 1.95,
           label = sprintf("%s attempts", format(N_QTL_ATTEMPTS, big.mark = ",")),
           size = 2.5, colour = COL_TEXT, fontface = "bold") +
  annotate("segment", x = 1.0, xend = 1.0, y = 1.65, yend = 1.20,
           arrow = arrow(length = unit(1.6, "mm"), type = "closed"),
           colour = COL_TEXT, linewidth = 0.3) +
  annotate("text", x = 1.0, y = 0.95, label = "tier assignment",
           size = 2.25, colour = COL_TEXT, fontface = "italic") +
  scale_x_continuous(limits = c(0, 2), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0.6, 3.5), expand = c(0, 0)) +
  labs(title = "4. Coloc engines") +
  empty_theme

# --- Panel 5: Tier + negative-control endpoint ------------------------------
panel_5_data <- data.frame(
  x_lo  = c(0.10, 0.55, 1.00, 1.45),
  x_hi  = c(0.50, 0.95, 1.40, 1.95),
  label = c(sprintf("Tier A\n%d", N_TIER_A),
            sprintf("Tier B\n%d", N_TIER_B),
            sprintf("Tier C\n%d", N_TIER_C),
            sprintf("Neg-ctrl\n%d", N_NEG_CTRL)),
  fill  = c(COL_IDENT, COL_IDENT, COL_REAL, COL_NEG),
  text_col = c(COL_TEXT, COL_TEXT, "white", "white"),
  stringsAsFactors = FALSE
)

panel_5 <- ggplot(panel_5_data) +
  geom_rect(aes(xmin = x_lo, xmax = x_hi, ymin = 1.05, ymax = 2.45, fill = fill),
            colour = COL_BORDER, linewidth = 0.3) +
  geom_text(aes(x = (x_lo + x_hi) / 2, y = 1.75, label = label,
                colour = text_col),
            size = 2.4, fontface = "bold", lineheight = 0.95) +
  scale_fill_identity() +
  scale_colour_identity() +
  scale_x_continuous(limits = c(0, 2.05), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0.4, 3.1), expand = c(0, 0)) +
  labs(title = "5. Tier + neg-ctrl") +
  empty_theme

# --- Composite assembly ------------------------------------------------------
# 2-row layout (top: panels 1-2-3; bottom: panels 4-5 + spacer) gives each
# panel ~57 mm width instead of 34 mm at single-column 170 mm. Bottom row
# spacer (plot_spacer()) keeps panels 4 and 5 at the same width as the top
# row.
composite <- wrap_plots(
  panel_1, panel_2, panel_3,
  panel_4, panel_5, plot_spacer(),
  ncol = 3
) +
  plot_annotation(
    caption = paste0(
      "Figure 1A. Track A real-LD audit pipeline schematic. Counts are locked from ",
      ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md (Stage 2 production fire 2026-04-22).\n",
      "Panels render geometric primitives; no data joins. Identity-LD vs real-LD branches are ",
      "quantitatively analyzed in Figures 1B, 2, 3, 5; this panel A summarises the methodological flow."
    ),
    theme = theme(plot.caption = element_text(size = 6.5, colour = "grey30",
                                              hjust = 0, lineheight = 1.15,
                                              margin = margin(t = 5)))
  )

# --- Render ------------------------------------------------------------------
dir.create(OUT_DIR, recursive = TRUE, showWarnings = FALSE)

if (!isTRUE(capabilities("cairo"))) {
  stop("fig1a_pipeline_schematic.R: R build lacks cairo capability; cairo_pdf unavailable.")
}

ggsave(OUT_PDF, composite, width = 170, height = 130, units = "mm",
       device = cairo_pdf)
ggsave(OUT_PNG, composite, width = 170, height = 130, units = "mm",
       dpi = 600)

# --- Diagnostic stdout (verified by Task 1 verify block) --------------------
message("=== fig1a_pipeline_schematic.R diagnostic ===")
message(sprintf("Panels: 5  (Input universe -> Fork -> Filter -> Engines -> Tier+NegCtrl)"))
message(sprintf("Locked scalars used (TRACK-A-FROZEN-NUMBERS.md):"))
message(sprintf("  N_LOCI                = %d", N_LOCI))
message(sprintf("  N_TRAITS              = %d", N_TRAITS))
message(sprintf("  N_ANCESTRIES          = %d", N_ANCESTRIES))
message(sprintf("  N_ADMISSIBLE_REAL_LD  = %d", N_ADMISSIBLE_REAL_LD))
message(sprintf("  N_PAIRWISE_ATTEMPTS   = %d", N_PAIRWISE_ATTEMPTS))
message(sprintf("  N_QTL_ATTEMPTS        = %d", N_QTL_ATTEMPTS))
message(sprintf("  N_TIER_A / B / C      = %d / %d / %d", N_TIER_A, N_TIER_B, N_TIER_C))
message(sprintf("  N_NEG_CTRL            = %d", N_NEG_CTRL))
message(sprintf("Render OUT_PDF=%s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))
message(sprintf("Render OUT_PNG=%s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))
message("Figure 1A render complete.")
