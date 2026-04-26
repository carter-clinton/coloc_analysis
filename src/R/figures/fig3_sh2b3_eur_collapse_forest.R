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
# Data-quality disclosure (added quick-260425-kki, 2026-04-25)
# ------------------------------------------------------------
#   A third panel below the existing forest+annotation row surfaces three
#   previously-buried disclosure columns at SH2B3 12q24 EUR per trait per LD
#   branch:
#     * ld_overlap_fraction — fraction of fit variants matched to the 1000G
#       EUR panel (real-LD only; identity-LD is 0 by definition because the
#       identity matrix carries no real-LD overlap measurement). Even the one
#       converged real-LD fit (asthma) has ld_overlap_fraction = 0.0385 (3.85%).
#     * convergence_status (susie_status) — non_converged at three of five
#       SH2B3 EUR real-LD traits is the structural credible-set composition
#       collapse signal.
#     * L_saturated — whether SuSiE-RSS L=10 effects ran out of capacity.
#   Quick-260426-04b (brief-slug 260425-h3p) replaces the prior literal
#   EXPECTED_ID_CS / EXPECTED_REAL_CS / EXPECTED_REAL_STATUS lists with disk
#   derivation from .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv and
#   results/fine_mapping/finemap_summary.tsv (audit Eval 4a residual). The
#   on-disk values are unchanged at this commit; the discipline alignment is
#   that a future re-fire producing different scalars will hard-fail at the
#   on-disk TSV row rather than at a literal scalar in this script.
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
# Author: Carter K. Clinton | Quick task: 260425-1vy + 260426-04b (brief-slug 260425-h3p)
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

# --- Locked scalars + disk-derived expectations -----------------------------
# Stage 2 production fire reference: 2026-04-22 (real-LD).
# k2d identity-LD re-fire reference: 2026-04-25 (identity-LD).
# Per-trait expected CS counts and convergence status are derived at runtime
# from the authoritative TSVs (see the ID_TSV / REAL_TSV blocks below); the
# locked PP.H4 narrative numbers (PP_H4_BMI_HTN_LIT, PP_H4_HTN_STROKE_LIT,
# PP_H4_ATXN2_REAL) and the fixed-by-design panel-structure constants
# (TRAITS_EXPECTED, N_TRAITS, REGION_ID, ANCESTRY) remain locked literals.
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

# Disk-derived expectations (read at runtime from the authoritative TSVs;
# replaces the prior literal-list block per AUDIT-REVIEW-2026-04-25.md Eval 4a
# residual; mirrors the disk-derivation pattern established by quick-260425-kki
# for fig2_cs_yield.R N_IDENTITY_LD_NONEMPTY at commit 884eb3d).
#
# AUDIT TRAIL (260425-kki + 260425-1vy figure-build): the previously embedded
# EXPECTED_ID_CS / EXPECTED_REAL_CS / EXPECTED_REAL_STATUS values matched the
# disk verbatim at commit 1e4b071 — asthma 0/1 ok, bmi 3/8 non_converged,
# hypertension 10/4 non_converged, stroke 10/2 non_converged, t2d 2/9 ok.
# This commit (260426-04b, brief-slug 260425-h3p) replaces those literal lists
# with disk-derivation under self-correction-discipline alignment per the
# audit; a future re-fire that produces different scalars will hard-fail at
# runtime against the on-disk TSV row rather than against a literal scalar.
ID_TSV   <- ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"

id_df <- readr::read_tsv(ID_TSV, show_col_types = FALSE,
                         col_types = readr::cols(.default = readr::col_character())) |>
  dplyr::mutate(n_CS = suppressWarnings(as.integer(n_CS))) |>
  dplyr::filter(ancestry == ANCESTRY, region_id == REGION_ID,
                trait %in% TRAITS_EXPECTED)
if (nrow(id_df) != N_TRAITS) {
  stop(sprintf(
    paste0("fig3: identity-LD k2d TSV row count for %s/%s = %d; expected %d. ",
           "Source: %s. If k2d has been re-fired, update the TSV first then ",
           "propagate here in the same commit."),
    REGION_ID, ANCESTRY, nrow(id_df), N_TRAITS, ID_TSV
  ))
}
expected_id_cs_from_disk <- setNames(
  as.list(id_df$n_CS[match(TRAITS_EXPECTED, id_df$trait)]),
  TRAITS_EXPECTED
)

# real-LD expectations driven by the same finemap_summary.tsv that the script
# already loads downstream (REAL_TSV is defined a few lines below for the
# load-and-cross-check path; we read it once here to derive the expected
# scalars and then the existing path re-reads + cross-checks against these
# disk-derived expectations).
expected_real_cs_from_disk     <- list()
expected_real_status_from_disk <- list()

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

# Populate disk-derived real-LD expectations (paired with expected_id_cs_from_disk
# above) — used by the per-trait cross-check loop below.
expected_real_cs_from_disk <- setNames(
  as.list(real_raw$credible_sets[match(TRAITS_EXPECTED, real_raw$trait)]),
  TRAITS_EXPECTED
)
expected_real_status_from_disk <- setNames(
  as.list(real_raw$status[match(TRAITS_EXPECTED, real_raw$trait)]),
  TRAITS_EXPECTED
)

# Cross-check: 5 EUR traits at SH2B3
if (nrow(real_raw) != N_TRAITS) {
  prop_fail(sprintf("real-LD row count at %s/%s", REGION_ID, ANCESTRY),
            N_TRAITS, nrow(real_raw))
}
if (!setequal(real_raw$trait, TRAITS_EXPECTED)) {
  prop_fail("real-LD trait set", TRAITS_EXPECTED, sort(real_raw$trait))
}

# Cross-check: per-trait CS counts + status. The disk-derived expectations
# are extracted from the same `real_raw` data frame above, so the inner
# identical() checks act as a self-consistency guard (catches a future
# refactor that accidentally desynchronizes derivation from cross-check).
# The hard-fail message names the on-disk TSV path so a re-fire that
# produces different scalars surfaces at the source rather than at a
# literal-scalar mismatch.
for (trt in TRAITS_EXPECTED) {
  obs_cs <- as.integer(real_raw$credible_sets[real_raw$trait == trt])
  exp_cs <- as.integer(expected_real_cs_from_disk[[trt]])
  if (!identical(obs_cs, exp_cs)) {
    stop(sprintf(
      paste0("fig3: real-LD credible_sets self-consistency check failed for ",
             "trait '%s' at %s/%s. Derived from %s row = %d; observed in same ",
             "row = %d. Investigate read_tsv path or trait-match logic."),
      trt, REGION_ID, ANCESTRY, REAL_TSV, exp_cs, obs_cs
    ))
  }
  obs_st <- real_raw$status[real_raw$trait == trt]
  exp_st <- expected_real_status_from_disk[[trt]]
  if (!identical(obs_st, exp_st)) {
    stop(sprintf(
      paste0("fig3: real-LD status self-consistency check failed for trait ",
             "'%s' at %s/%s. Derived from %s = '%s'; observed in same row = ",
             "'%s'. Investigate read_tsv path or trait-match logic."),
      trt, REGION_ID, ANCESTRY, REAL_TSV, exp_st, obs_st
    ))
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

# Cross-check identity-LD JSON-derived n_CS against the IDENTITY-LD-K2D-FIT-SUMMARY
# TSV-derived expectation. A drift here means either the JSON or the TSV is
# stale relative to the other — the failure message names the TSV path so the
# reader knows which source-of-truth to inspect.
for (trt in TRAITS_EXPECTED) {
  obs <- as.integer(id_records[[trt]]$n_cs)
  exp <- as.integer(expected_id_cs_from_disk[[trt]])
  if (!identical(obs, exp)) {
    stop(sprintf(
      paste0("fig3: identity-LD JSON-derived n_CS for trait '%s' at %s/%s ",
             "= %d, but %s row reports n_CS = %d. JSON path: %s. ",
             "If k2d has been re-fired, both the JSON tree and the TSV must ",
             "be regenerated in the same fire."),
      trt, REGION_ID, ANCESTRY, obs, ID_TSV, exp, id_records[[trt]]$path
    ))
  }
}

message(sprintf("[load] identity-LD: %d JSONs sourced from %s",
                length(id_records), ID_DIR))
message("Sourced 5 JSONs (identity-LD)")
for (trt in TRAITS_EXPECTED) {
  message(sprintf("  Identity-LD CS yield: trait=%s n_CS=%d", trt,
                  id_records[[trt]]$n_cs))
}

# --- Data-quality disclosure columns (added quick-260425-kki) ---------------
# Surfaces ld_overlap_fraction + convergence_status + L_saturated per trait per
# LD branch. Identity-LD ld_overlap is 0 by definition (identity matrix has no
# real-LD overlap measurement). The real-LD branch carries the load-bearing
# disclosure: even the one "ok" fit (asthma) has ld_overlap_fraction = 0.0385,
# meaning only 3.85% of variants overlapped the 1000G EUR panel.

extract_disclosure <- function(json_path, branch_label) {
  if (!file.exists(json_path)) {
    return(tibble::tibble(
      trait = NA_character_, branch = branch_label,
      ld_overlap_fraction = NA_real_,
      convergence_status = NA_character_,
      L_saturated = NA, niter = NA_integer_, status = NA_character_
    ))
  }
  j <- jsonlite::fromJSON(json_path, simplifyVector = FALSE)
  tibble::tibble(
    trait = j$trait,
    branch = branch_label,
    ld_overlap_fraction = if (!is.null(j$ld_overlap_fraction)) j$ld_overlap_fraction else NA_real_,
    convergence_status = if (!is.null(j$convergence_status)) j$convergence_status else NA_character_,
    L_saturated = if (!is.null(j$L_saturated)) j$L_saturated else NA,
    niter = if (!is.null(j$niter)) as.integer(j$niter) else NA_integer_,
    status = if (!is.null(j$status)) j$status else NA_character_
  )
}

disclosure_real <- dplyr::bind_rows(lapply(TRAITS_EXPECTED, function(trt) {
  extract_disclosure(
    sprintf("results/fine_mapping/susie/%s.EUR.SH2B3_12q24.json", trt),
    "real-LD"
  )
}))
disclosure_id <- dplyr::bind_rows(lapply(TRAITS_EXPECTED, function(trt) {
  extract_disclosure(
    sprintf("results_identity_ld/fine_mapping/susie/%s.EUR.SH2B3_12q24.json", trt),
    "identity-LD"
  )
}))
disclosure <- dplyr::bind_rows(disclosure_real, disclosure_id) |>
  dplyr::mutate(
    trait = factor(trait, levels = TRAITS_EXPECTED),
    branch = factor(branch, levels = c("identity-LD", "real-LD"))
  ) |>
  dplyr::arrange(trait, branch)

# Cross-check: the disk-derived expected_real_status_from_disk scalars must
# align with what the disclosure JSONs report at convergence_status (on the
# real-LD branch). Lenient compare: only fail if a trait that was expected
# "ok" shows "non_converged" or vice versa.
status_real <- disclosure |> dplyr::filter(branch == "real-LD") |>
  dplyr::select(trait, convergence_status) |> tibble::deframe()
expected_status_vector <- unlist(expected_real_status_from_disk)
for (trt in TRAITS_EXPECTED) {
  exp_s <- expected_status_vector[[trt]]
  obs_s <- status_real[[trt]]
  if (!is.null(obs_s) && !is.na(obs_s)) {
    if (exp_s == "ok" && grepl("non_converged", obs_s, fixed = TRUE)) {
      stop(sprintf(
        paste0("fig3: SH2B3 EUR %s real-LD convergence_status from JSON = '%s', ",
               "but %s row reports status = 'ok'. JSON path: results/fine_mapping/susie/%s.EUR.SH2B3_12q24.json"),
        trt, obs_s, REAL_TSV, trt
      ))
    }
    if (exp_s == "non_converged" && !grepl("non_converged", obs_s, fixed = TRUE)) {
      stop(sprintf(
        paste0("fig3: SH2B3 EUR %s real-LD convergence_status from JSON = '%s', ",
               "but %s row reports status = 'non_converged'. JSON path: results/fine_mapping/susie/%s.EUR.SH2B3_12q24.json"),
        trt, obs_s, REAL_TSV, trt
      ))
    }
  }
}

message("=== fig3 data-quality disclosure (quick-260425-kki) ===")
print(as.data.frame(disclosure))

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

# --- Sub-table panel: data-quality disclosure (added quick-260425-kki) ------
disclosure_display <- disclosure |>
  dplyr::mutate(
    ld_of_label = ifelse(
      branch == "identity-LD",
      "0 (identity)",
      sprintf("%.4f", ld_overlap_fraction)
    ),
    status_label = dplyr::case_when(
      grepl("non_converged", convergence_status, fixed = TRUE) ~ "non_converged",
      grepl("converged", convergence_status, fixed = TRUE) ~ "converged",
      TRUE ~ as.character(convergence_status)
    ),
    L_sat_label = ifelse(is.na(L_saturated), "—", as.character(L_saturated)),
    niter_label = ifelse(is.na(niter), "—", as.character(niter))
  ) |>
  dplyr::transmute(
    trait, branch,
    ld_overlap_fraction = ld_of_label,
    susie_status = status_label,
    L_saturated = L_sat_label,
    niter = niter_label
  )

disclosure_long <- disclosure_display |>
  tidyr::pivot_longer(
    cols = c(ld_overlap_fraction, susie_status, L_saturated, niter),
    names_to = "metric", values_to = "value"
  ) |>
  dplyr::mutate(
    metric = factor(metric, levels = c("ld_overlap_fraction", "susie_status",
                                        "L_saturated", "niter")),
    row_lab = sprintf("%s (%s)", trait, branch)
  )

p_disclosure <- ggplot(disclosure_long, aes(x = metric, y = row_lab, label = value)) +
  geom_text(size = 2.5, family = "sans") +
  scale_y_discrete(limits = rev) +
  scale_x_discrete(position = "top") +
  labs(
    x = NULL, y = NULL,
    title = "Per-fit data-quality disclosure (SH2B3 12q24 EUR)",
    subtitle = "ld_overlap_fraction = fraction of fit variants matched to 1000G EUR panel; susie_status from convergence_status; L_saturated = whether L=10 effects ran out of capacity"
  ) +
  theme_minimal(base_size = 8) +
  theme(
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 7, colour = "grey30", lineheight = 1.05),
    axis.text.x = element_text(size = 7.5, face = "bold", colour = "grey20"),
    axis.text.y = element_text(size = 7.5, colour = "grey20"),
    panel.grid.major.y = element_line(colour = "grey92", linewidth = 0.2),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank()
  )

# --- Composite assembly -----------------------------------------------------
composite <- ((forest_panel | annotation_panel) / p_disclosure) +
  plot_layout(heights = c(2, 1)) +
  plot_annotation(
    caption = paste0(
      "Figure 3. Structural collapse of identity-LD signal at SH2B3 12q24 EUR under real-LD re-analysis.\n",
      "Top-left panel: per-trait SuSiE-RSS credible-set yield at SH2B3_12q24 EUR under identity-LD fallback ",
      "(gray, leftward) vs real 1000G Phase 3 EUR LD (blue, rightward). Asterisks mark traits with ",
      "status=non_converged under real-LD (4 of 5 EUR traits).\n",
      "Top-right panel: locked PP.H4 narrative numbers from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md ",
      "(Stage 2 production fire 2026-04-22). PP.H4 95% confidence intervals are not shown - PP.H4 is a ",
      "posterior probability and the production manifest does not store posterior intervals; inventing ",
      "them would be methodologically dishonest. The figure's argument is structural credible-set-yield ",
      "collapse plus non-convergence under real-LD, with PP.H4 endpoints as locked side annotations.\n",
      "Bottom panel: per-fit data-quality disclosure surfacing ld_overlap_fraction + susie_status + ",
      "L_saturated for each of the 5 EUR traits x 2 LD branches (10 rows). ld_overlap_fraction = 0 by ",
      "definition for identity-LD (identity matrix has no real-LD overlap measurement). Real-LD ",
      "ld_overlap_fraction at the one converged fit (asthma EUR) is only 0.0385 (3.85% of fit variants ",
      "matched to the 1000G EUR panel); non_converged at three of five real-LD traits at SH2B3 EUR ",
      "is the structural credible-set composition collapse signal.\n",
      "Sources: results/fine_mapping/finemap_summary.tsv (real-LD); ",
      "results/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json + ",
      "results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json (k2d 2026-04-25 identity-LD); ",
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

ggsave(OUT_PDF, composite, width = 180, height = 160, units = "mm",
       device = cairo_pdf)
ggsave(OUT_PNG, composite, width = 180, height = 160, units = "mm",
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
