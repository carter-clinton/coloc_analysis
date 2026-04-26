#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# fig_h3_ld_overlap_dose_response.R --
#   Track A audit High-Quality #3 LD-reference-quality dose-response figure
# ---------------------------------------------------------------------------
#
# Purpose: AUDIT-REVIEW-2026-04-25.md High-Quality #3 identified an
# under-explored disk-truth question -- how does the inferred coloc signal
# depend on the LD-reference overlap of the SuSiE-RSS fit that feeds it?
# This script extends the per-row Tier-C-table disclosure published in the
# manuscript prose by quick-260425-kki to a dose-response visualization
# across all admissible Track A fits, answering the audit's verbatim ask:
# "plot PP.H4 vs ld_overlap_fraction to show the dose-response of
# LD-reference quality on the inferred coloc signal."
#
# Output: a 2-panel composite.
#   Panel A -- SuSiE-RSS credible-set yield x ld_overlap_fraction across the
#     60 EUR (region, trait) fits. The 36 AFR fits are excluded because no
#     AFR LD panel is loaded (TRACK-A-FROZEN-NUMBERS.md scope caveat). Point
#     color encodes SuSiE status. Vertical reference at ld_overlap_fraction
#     = 0.5 (Benner et al. 2017 AJHG calibration threshold).
#   Panel B -- QTL-coloc PP.H4 x GWAS-side MIN ld_overlap_fraction across
#     the 32 successful (region, gene, tissue, qtl_source) attempts (all
#     EUR). MIN-aggregation across the 5 GWAS-side trait fits is a
#     conservative worst-case bound -- the qtl_coloc per-attempt JSON does
#     not record which trait was the GWAS-side input. Reference vertical at
#     the Benner threshold; horizontal references at PP.H4 = 0.5 (Tier B)
#     and 0.8 (Tier A). Headline FTO_16q12 EUR IRX3 / Pancreas Tier-C
#     signal (PP.H4 = 0.3099, min_ld_of = 0) annotated as the structural
#     inflation flag the audit surfaced.
#
# Provenance:
#   AUDIT-REVIEW-2026-04-25.md High-Quality #3 (.planning/amendments/)
#   results/fine_mapping/finemap_summary.tsv (Stage 2 fire 2026-04-22)
#   results/fine_mapping/susie/*.json (96 per-fit JSONs)
#   results/qtl_coloc/*.json (1,274 per-attempt JSONs; 32 status=success)
#   .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (locked-scalar ledger)
#   Benner et al. 2017, AJHG 101:539-551 (calibration threshold).
#
# Outputs:
#   docs/manuscript/figures/fig_h3_ld_overlap_dose_response.pdf (cairo_pdf, 170 x 200 mm)
#   docs/manuscript/figures/fig_h3_ld_overlap_dose_response.png (600 dpi, 170 x 200 mm)
#
# Render env: /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
# Invocation (from project root): Rscript src/R/figures/fig_h3_ld_overlap_dose_response.R
#
# The "h3" stem is the audit's neutral High-Quality #3 tag. Manuscript slot
# assignment (Fig 4 reclaim vs new Fig 6 vs supplementary) is deferred to a
# follow-on /gsd-quick after Carter reviews the rendered composite.
#
# Author: Carter K. Clinton -- 2026-04-25 (quick-260425-wa2)
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(jsonlite); library(readr); library(dplyr); library(tidyr)
  library(ggplot2); library(patchwork); library(scales)
})
has_ggrepel <- requireNamespace("ggrepel", quietly = TRUE)
`%||%` <- function(a, b) if (!is.null(a)) a else b

# --- Locked scalars (cross-checked at runtime; hard-fail on drift) ---------
# Authoritative ledger: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
N_REAL_LD_FITS_TOTAL <- 96L
N_REAL_LD_NONEMPTY   <- 51L
N_QTL_SUCCESS        <- 32L
N_EUR_FITS_EXPECTED  <- 60L
N_AFR_FITS_EXPECTED  <- 36L
BENNER_THRESHOLD     <- 0.5
TIER_B_THRESHOLD     <- 0.5
TIER_A_THRESHOLD     <- 0.8
FTO_HEADLINE_PPH4    <- 0.3099
SH2B3_ASTHMA_LDOF    <- 0.0385

# --- Path constants --------------------------------------------------------
REAL_TSV  <- "results/fine_mapping/finemap_summary.tsv"
SUSIE_DIR <- "results/fine_mapping/susie"
QTL_DIR   <- "results/qtl_coloc"
OUT_DIR   <- "docs/manuscript/figures"
OUT_PDF   <- file.path(OUT_DIR, "fig_h3_ld_overlap_dose_response.pdf")
OUT_PNG   <- file.path(OUT_DIR, "fig_h3_ld_overlap_dose_response.png")

# --- Palette (reuses fig2 / fig3 / fig5 hues) ------------------------------
COL_OK <- "#3B6AA0"; COL_TOO_MANY <- "#E08A3C"; COL_NON_CONV <- "#C0392B"
COL_NO_VARIANTS <- "#8A8A8A"; COL_BENNER <- "#4A4A4A"
COL_TIER_B <- "#D95F02"; COL_TIER_A <- "#7570B3"
COL_EQTL <- "#3B6AA0"; COL_SQTL <- "#6FAE9D"
STATUS_LEVELS <- c("ok", "too_many_variants", "non_converged", "no_variants")
STATUS_PALETTE <- setNames(c(COL_OK, COL_TOO_MANY, COL_NON_CONV, COL_NO_VARIANTS), STATUS_LEVELS)

# --- Helper: extract per-fit overlap record from a SuSiE JSON --------------
load_susie_overlap_record <- function(json_path) {
  d <- tryCatch(fromJSON(json_path, simplifyVector = FALSE), error = function(e) NULL)
  if (is.null(d)) return(NULL)
  cs <- d$credible_sets
  n_cs <- if (is.null(cs)) 0L else length(cs)
  lof <- d$ld_overlap_fraction
  tibble::tibble(
    trait = d$trait %||% NA_character_,
    ancestry = d$ancestry %||% NA_character_,
    region_id = d$region_id %||% NA_character_,
    status = d$status %||% NA_character_,
    ld_status = d$ld_status %||% NA_character_,
    ld_overlap_fraction = if (is.null(lof)) NA_real_ else as.numeric(lof),
    credible_sets = as.integer(n_cs)
  )
}

# --- Helper: extract successful qtl_coloc record from a per-attempt JSON ---
load_qtl_success_record <- function(json_path) {
  d <- tryCatch(fromJSON(json_path, simplifyVector = FALSE), error = function(e) NULL)
  if (is.null(d) || !identical(d$status, "success")) return(NULL)
  pph4 <- d$summary$PP.H4.abf
  if (is.null(pph4)) return(NULL)
  tibble::tibble(
    region = d$region %||% NA_character_,
    ancestry = d$ancestry %||% NA_character_,
    gene_id = d$gene_id %||% NA_character_,
    tissue = d$tissue %||% NA_character_,
    qtl_source = d$qtl_source %||% NA_character_,
    n_snps_overlap = if (is.null(d$n_snps_overlap)) NA_integer_ else as.integer(d$n_snps_overlap),
    pph4 = as.numeric(pph4)
  )
}

# --- Read finemap_summary.tsv + cross-check denominator --------------------
if (!file.exists(REAL_TSV)) stop(sprintf("fig_h3: finemap summary TSV missing at '%s'.", REAL_TSV))
real_summary <- read_tsv(REAL_TSV, show_col_types = FALSE)
stopifnot(
  "TRACK-A-FROZEN-NUMBERS.md: finemap_summary.tsv row count drifted from 96" = nrow(real_summary) == N_REAL_LD_FITS_TOTAL,
  "TRACK-A-FROZEN-NUMBERS.md: non-empty credible-set count drifted from 51" = sum(real_summary$credible_sets > 0, na.rm = TRUE) == N_REAL_LD_NONEMPTY
)

# --- Walk per-fit SuSiE JSONs (96 files) -----------------------------------
susie_files <- list.files(SUSIE_DIR, pattern = "\\.json$", full.names = TRUE)
stopifnot("Per-fit SuSiE JSON count drifted from 96" = length(susie_files) == N_REAL_LD_FITS_TOTAL)
susie_disclosure <- bind_rows(lapply(susie_files, load_susie_overlap_record))
stopifnot("Per-fit SuSiE JSON parse drift" = nrow(susie_disclosure) == N_REAL_LD_FITS_TOTAL)
n_eur_total <- sum(susie_disclosure$ancestry == "EUR")
n_afr_total <- sum(susie_disclosure$ancestry == "AFR")
stopifnot(
  "Ancestry split drift: EUR != 60" = n_eur_total == N_EUR_FITS_EXPECTED,
  "Ancestry split drift: AFR != 36" = n_afr_total == N_AFR_FITS_EXPECTED
)

# Cross-check: status distribution + SH2B3 EUR asthma ld_overlap_fraction
status_counts <- susie_disclosure |> count(status) |> arrange(desc(n))
sh2b3_asthma <- susie_disclosure |>
  filter(region_id == "SH2B3_12q24", ancestry == "EUR", trait == "asthma")
stopifnot(
  "SH2B3 EUR asthma not found" = nrow(sh2b3_asthma) == 1,
  "SH2B3 EUR asthma ld_overlap_fraction drifted from 0.0385" =
    !is.na(sh2b3_asthma$ld_overlap_fraction) &&
    abs(sh2b3_asthma$ld_overlap_fraction - SH2B3_ASTHMA_LDOF) < 1e-4
)

# --- Walk per-attempt qtl_coloc JSONs (1,274 files) ------------------------
qtl_files <- list.files(QTL_DIR, pattern = "\\.json$", full.names = TRUE)
qtl_success <- bind_rows(lapply(qtl_files, load_qtl_success_record))
stopifnot(
  "TRACK-A-FROZEN-NUMBERS.md: qtl_coloc success count drifted from 32" = nrow(qtl_success) == N_QTL_SUCCESS,
  "qtl_coloc successes include non-EUR rows" = all(qtl_success$ancestry == "EUR")
)

# Cross-check: FTO_16q12 EUR IRX3 / Pancreas / gtex_eqtl PP.H4 = 0.3099
fto_irx3_pancreas <- qtl_success |>
  filter(region == "FTO_16q12", ancestry == "EUR",
         gene_id == "ENSG00000177508", tissue == "Pancreas",
         qtl_source == "gtex_eqtl")
stopifnot(
  "FTO_16q12 EUR IRX3 / Pancreas / gtex_eqtl row not found" = nrow(fto_irx3_pancreas) == 1,
  "FTO_16q12 EUR IRX3 / Pancreas PP.H4 drifted from 0.3099" =
    abs(fto_irx3_pancreas$pph4 - FTO_HEADLINE_PPH4) < 1e-4
)

# --- Compute per-(region, ancestry) min ld_overlap_fraction ---------------
# Worst-case-bound aggregation: NA values (ld not measured for that fit)
# treated as 0 -- matches the conservative reading of the audit's caveat.
min_overlap_by_cell <- susie_disclosure |>
  mutate(ldof_for_min = ifelse(is.na(ld_overlap_fraction), 0, ld_overlap_fraction)) |>
  group_by(region_id, ancestry) |>
  summarise(min_ld_overlap_fraction = min(ldof_for_min), .groups = "drop")

qtl_with_overlap <- qtl_success |>
  left_join(min_overlap_by_cell,
            by = c("region" = "region_id", "ancestry" = "ancestry"))
stopifnot(
  "qtl_with_overlap join missing rows" = nrow(qtl_with_overlap) == N_QTL_SUCCESS,
  "FTO_16q12 EUR min_ld_overlap_fraction drifted from 0" = {
    v <- qtl_with_overlap |> filter(region == "FTO_16q12", ancestry == "EUR") |>
      pull(min_ld_overlap_fraction)
    length(v) > 0 && all(abs(v - 0) < 1e-6)
  }
)

# Panel A data: 60 EUR fits. Coerce NA ld_overlap_fraction to 0 (the 19 EUR
# fits with NA never had LD measured -- conceptually = "no LD overlap" for
# the dose-response question; documented in the in-figure caption).
panel_a_data <- susie_disclosure |>
  filter(ancestry == "EUR") |>
  mutate(plot_ldof = ifelse(is.na(ld_overlap_fraction), 0, ld_overlap_fraction),
         status = factor(status, levels = STATUS_LEVELS),
         n_cs_capped = pmin(credible_sets, 10L))
stopifnot("Panel A data drift: not 60 EUR fits" = nrow(panel_a_data) == N_EUR_FITS_EXPECTED)

ann_a_sh2b3 <- panel_a_data |> filter(region_id == "SH2B3_12q24", trait == "asthma")
ann_a_fto   <- panel_a_data |> filter(region_id == "FTO_16q12") |>
  arrange(desc(n_cs_capped)) |> slice(1)

# Diagnostic scalars surfaced for orchestrator follow-on:
n_eur_below_benner       <- sum(panel_a_data$plot_ldof < BENNER_THRESHOLD)
n_eur_at_or_above_benner <- sum(panel_a_data$plot_ldof >= BENNER_THRESHOLD)
n_qtl_suspect <- qtl_with_overlap |>
  filter(pph4 >= TIER_B_THRESHOLD, min_ld_overlap_fraction < BENNER_THRESHOLD) |>
  nrow()

# --- Panel A: SuSiE-RSS CS yield x ld_overlap_fraction ---------------------
panel_a <- ggplot(panel_a_data, aes(x = plot_ldof, y = n_cs_capped, color = status)) +
  geom_vline(xintercept = BENNER_THRESHOLD, linetype = "dashed",
             color = COL_BENNER, linewidth = 0.4) +
  geom_point(size = 2.0, alpha = 0.85,
             position = position_jitter(width = 0.005, height = 0.18, seed = 42L)) +
  annotate("text", x = BENNER_THRESHOLD + 0.01, y = 9.7,
           label = "Benner 2017 threshold (0.5)",
           hjust = 0, size = 2.4, color = COL_BENNER, fontface = "italic") +
  scale_color_manual(values = STATUS_PALETTE, name = "SuSiE status",
                     drop = FALSE, breaks = STATUS_LEVELS) +
  scale_x_continuous(limits = c(-0.02, 1.02), breaks = seq(0, 1, 0.1),
                     labels = scales::number_format(accuracy = 0.1)) +
  scale_y_continuous(limits = c(-0.5, 10.5), breaks = seq(0, 10, 2), expand = c(0, 0)) +
  labs(
    title = "A -- SuSiE-RSS credible-set yield as a function of LD-reference overlap",
    subtitle = paste0("All 60 EUR real-LD region x trait fits with ld_overlap_fraction; ",
                      "reference at Benner 2017 0.5 calibration threshold"),
    x = "ld_overlap_fraction (fraction of fit variants matched to 1000G EUR LD panel)",
    y = "Credible sets (count, capped at L = 10)"
  ) +
  theme_classic(base_size = 9) +
  theme(plot.title = element_text(face = "bold", size = 10),
        plot.subtitle = element_text(size = 8, color = "grey25"),
        legend.position = "bottom", legend.title = element_text(size = 8),
        legend.text = element_text(size = 7.5),
        legend.key.size = unit(0.4, "cm"),
        axis.title = element_text(size = 8.5), axis.text = element_text(size = 7.5),
        plot.margin = margin(5, 8, 5, 5))

if (has_ggrepel) {
  panel_a <- panel_a +
    ggrepel::geom_text_repel(
      data = ann_a_sh2b3,
      aes(x = plot_ldof, y = n_cs_capped,
          label = "SH2B3 EUR asthma\n(ld_of = 0.0385, ok)"),
      inherit.aes = FALSE, size = 2.3, fontface = "italic", color = "grey20",
      nudge_x = 0.18, nudge_y = 1.4,
      segment.color = "grey50", segment.size = 0.3,
      box.padding = 0.4, point.padding = 0.3, min.segment.length = 0
    ) +
    ggrepel::geom_text_repel(
      data = ann_a_fto,
      aes(x = plot_ldof, y = n_cs_capped,
          label = "FTO_16q12 EUR\n(ld_of = 0; Tier-C headline locus)"),
      inherit.aes = FALSE, size = 2.3, fontface = "italic", color = "grey20",
      nudge_x = 0.20, nudge_y = -1.0,
      segment.color = "grey50", segment.size = 0.3,
      box.padding = 0.4, point.padding = 0.3, min.segment.length = 0
    )
} else {
  panel_a <- panel_a +
    geom_text(data = ann_a_sh2b3, aes(x = plot_ldof, y = n_cs_capped),
              label = "SH2B3 EUR asthma (ld_of = 0.0385)", inherit.aes = FALSE,
              size = 2.3, fontface = "italic", color = "grey20",
              hjust = 0, vjust = -1.4, nudge_x = 0.04) +
    geom_text(data = ann_a_fto, aes(x = plot_ldof, y = n_cs_capped),
              label = "FTO_16q12 EUR (ld_of = 0)", inherit.aes = FALSE,
              size = 2.3, fontface = "italic", color = "grey20",
              hjust = 0, vjust = 1.6, nudge_x = 0.04)
}

# --- Panel B: QTL-coloc PP.H4 x GWAS-side min ld_overlap_fraction ----------
panel_b_data <- qtl_with_overlap |>
  mutate(qtl_source = factor(qtl_source, levels = c("gtex_eqtl", "gtex_sqtl")))
ann_b_fto <- panel_b_data |>
  filter(region == "FTO_16q12", gene_id == "ENSG00000177508",
         tissue == "Pancreas", qtl_source == "gtex_eqtl")

panel_b <- ggplot(panel_b_data,
                  aes(x = min_ld_overlap_fraction, y = pph4, color = qtl_source)) +
  geom_vline(xintercept = BENNER_THRESHOLD, linetype = "dashed",
             color = COL_BENNER, linewidth = 0.4) +
  geom_hline(yintercept = TIER_B_THRESHOLD, linetype = "dashed",
             color = COL_TIER_B, linewidth = 0.4) +
  geom_hline(yintercept = TIER_A_THRESHOLD, linetype = "dashed",
             color = COL_TIER_A, linewidth = 0.4) +
  geom_point(size = 2.2, alpha = 0.85,
             position = position_jitter(width = 0.005, height = 0.005, seed = 17L)) +
  annotate("text", x = BENNER_THRESHOLD + 0.01, y = 0.96,
           label = "Benner 2017 threshold (0.5)",
           hjust = 0, size = 2.3, color = COL_BENNER, fontface = "italic") +
  annotate("text", x = 0.98, y = TIER_B_THRESHOLD + 0.02, label = "Tier B (0.5)",
           hjust = 1, size = 2.3, color = COL_TIER_B, fontface = "italic") +
  annotate("text", x = 0.98, y = TIER_A_THRESHOLD + 0.02, label = "Tier A (0.8)",
           hjust = 1, size = 2.3, color = COL_TIER_A, fontface = "italic") +
  scale_color_manual(values = c("gtex_eqtl" = COL_EQTL, "gtex_sqtl" = COL_SQTL),
                     name = "QTL source", drop = FALSE) +
  scale_x_continuous(limits = c(-0.02, 1.02), breaks = seq(0, 1, 0.1),
                     labels = scales::number_format(accuracy = 0.1)) +
  scale_y_continuous(limits = c(-0.02, 1.02), breaks = seq(0, 1, 0.2), expand = c(0, 0)) +
  labs(
    title = "B -- QTL-coloc PP.H4 as a function of GWAS-side LD-reference overlap",
    subtitle = paste0("32 successful QTL-coloc attempts (status = success); ",
                      "x = MIN ld_overlap_fraction across 5 trait fits at the same region x ancestry cell"),
    x = "min ld_overlap_fraction across GWAS-side trait fits (worst-case bound)",
    y = "QTL-coloc PP.H4"
  ) +
  theme_classic(base_size = 9) +
  theme(plot.title = element_text(face = "bold", size = 10),
        plot.subtitle = element_text(size = 8, color = "grey25"),
        legend.position = "bottom", legend.title = element_text(size = 8),
        legend.text = element_text(size = 7.5),
        legend.key.size = unit(0.4, "cm"),
        axis.title = element_text(size = 8.5), axis.text = element_text(size = 7.5),
        plot.margin = margin(5, 8, 5, 5))

if (has_ggrepel && nrow(ann_b_fto) >= 1) {
  panel_b <- panel_b + ggrepel::geom_text_repel(
    data = ann_b_fto,
    aes(x = min_ld_overlap_fraction, y = pph4,
        label = "FTO_16q12 EUR IRX3 / Pancreas\nPP.H4 = 0.3099  (ld_of = 0)"),
    inherit.aes = FALSE, size = 2.4, fontface = "italic", color = "grey15",
    nudge_x = 0.22, nudge_y = 0.20,
    segment.color = "grey50", segment.size = 0.3,
    box.padding = 0.5, point.padding = 0.3, min.segment.length = 0
  )
} else if (nrow(ann_b_fto) >= 1) {
  panel_b <- panel_b + geom_text(
    data = ann_b_fto, aes(x = min_ld_overlap_fraction, y = pph4),
    label = "FTO_16q12 EUR IRX3 / Pancreas (PP.H4=0.3099, ld_of=0)",
    inherit.aes = FALSE, size = 2.3, fontface = "italic", color = "grey15",
    hjust = 0, vjust = -1.3, nudge_x = 0.04
  )
}

# --- Composite assembly + caption ------------------------------------------
caption_text <- paste0(
  "Figure H3. LD-reference-quality dose-response on coloc inference at admissible Track A loci.\n",
  "Panel A -- SuSiE-RSS credible-set yield x ld_overlap_fraction. Each point = one EUR (region, trait) ",
  "SuSiE-RSS fit (n = 60). The 36 AFR fits are excluded because no AFR LD panel is loaded ",
  "(TRACK-A-FROZEN-NUMBERS.md scope caveat). Color = SuSiE status. Vertical reference at ",
  "ld_overlap_fraction = 0.5 (Benner et al. 2017 AJHG calibration threshold). Annotated points: ",
  "SH2B3_12q24 EUR asthma (ld_of = 0.0385, the lone 'ok' SH2B3 EUR fit) and FTO_16q12 EUR ",
  "(ld_of = 0, the headline-Tier-C locus).\n",
  "Panel B -- QTL-coloc PP.H4 x GWAS-side ld_overlap_fraction. Each point = one successful ",
  "(region, gene, tissue, qtl_source) QTL-coloc attempt (n = 32, all EUR per disk). The x-axis ",
  "uses MIN ld_overlap_fraction across the 5 GWAS-side trait fits at the same (region, ancestry) ",
  "cell -- a conservative worst-case bound, because the qtl_coloc per-attempt JSON does not ",
  "record which trait's GWAS-side SuSiE fit was the input. The headline FTO_16q12 EUR IRX3 / ",
  "Pancreas Tier-C signal (PP.H4 = 0.3099, summary block hit2 = rs11075995) sits at min ",
  "ld_of = 0 -- the structural inflation flag the audit surfaced.\n",
  "Sources: results/fine_mapping/finemap_summary.tsv + results/fine_mapping/susie/*.json ",
  "(Stage 2 production fire 2026-04-22); results/qtl_coloc/*.json (per-attempt 2026-04-22 fire); ",
  "reference threshold from Benner et al. 2017 AJHG 101:539-551; tier thresholds from ",
  ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md."
)

composite <- panel_a / panel_b +
  plot_layout(heights = c(1, 1)) +
  plot_annotation(
    caption = caption_text,
    theme = theme(plot.caption = element_text(size = 6.5, color = "grey30",
                                              hjust = 0, lineheight = 1.15,
                                              margin = margin(t = 6)))
  )

# --- Render -----------------------------------------------------------------
dir.create(OUT_DIR, recursive = TRUE, showWarnings = FALSE)
if (!isTRUE(capabilities("cairo")))
  stop("fig_h3_ld_overlap_dose_response.R: R build lacks cairo capability.")
ggsave(OUT_PDF, composite, width = 170, height = 200, units = "mm", device = cairo_pdf)
ggsave(OUT_PNG, composite, width = 170, height = 200, units = "mm", dpi = 600)

# --- Diagnostic stdout -----------------------------------------------------
fto_min_ldof <- qtl_with_overlap |>
  filter(region == "FTO_16q12", ancestry == "EUR", gene_id == "ENSG00000177508",
         tissue == "Pancreas", qtl_source == "gtex_eqtl") |>
  pull(min_ld_overlap_fraction)

message("=== fig_h3_ld_overlap_dose_response.R diagnostic ===")
message(sprintf("Total real-LD fits parsed: %d (expected %d)",
                nrow(susie_disclosure), N_REAL_LD_FITS_TOTAL))
message(sprintf("EUR fits with measured ld_overlap_fraction: %d", n_eur_total))
message(sprintf("AFR fits (no measured ld_overlap_fraction): %d", n_afr_total))
message("Status distribution:")
for (i in seq_len(nrow(status_counts)))
  message(sprintf("  %-22s %d", status_counts$status[i], status_counts$n[i]))
message(sprintf("EUR fits below Benner threshold (ld_overlap_fraction < %.1f): %d",
                BENNER_THRESHOLD, n_eur_below_benner))
message(sprintf("EUR fits at or above Benner threshold (>= %.1f): %d",
                BENNER_THRESHOLD, n_eur_at_or_above_benner))
message(sprintf("Total qtl_coloc successes parsed: %d (expected %d; all EUR)",
                nrow(qtl_success), N_QTL_SUCCESS))
message(sprintf("FTO_16q12 EUR IRX3/Pancreas: PP.H4=%.4f min_ld_overlap_fraction=%g",
                fto_irx3_pancreas$pph4, fto_min_ldof))
message(sprintf("SH2B3_12q24 EUR asthma: ld_overlap_fraction=%.4f",
                sh2b3_asthma$ld_overlap_fraction))
message(sprintf("Suspect-quadrant points (PP.H4 >= %.1f AND min_ld_of < %.1f): %d",
                TIER_B_THRESHOLD, BENNER_THRESHOLD, n_qtl_suspect))
message("---")
message(sprintf("wrote %s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))
message(sprintf("wrote %s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))
message("Figure H3 render complete.")
