#!/usr/bin/env Rscript
# =============================================================================
# D-02a PRIMARY METRIC: Tier A retention fraction per trait
# D-02e EXPLICITLY NOT REUSED: Phase 9 joint PP.H4 + effect-size criterion
# (reason: conflates coloc stability with effect-size stability, would
# double-count power loss and inflate observed concordance reduction).
#
# D-02c SANITY CHECK: lead-variant direction-of-effect sign agreement
# (computed alongside retention; should be ~100%).
#
# D-02d UNMATCHED BASELINE: one pass over Phase 2 coloc_summary at full
# EUR N (not bootstrapped) to produce the unmatched concordance comparison
# for the pre-registered H7 verdict.
#
# For each trait:
#   1. Load Phase 2 tier_assignments.tsv; filter ancestry=='AFR' AND tier=='A'
#   2. For each bootstrap b in 1..B: load coloc_summary.tsv, check
#      is_tier_a_b = (max pph4 >= 0.8) AND (at_least_one_qtl_coloc >= 0.8)
#   3. retention_b = n_retained / n_afr_tier_a per bootstrap
#   4. Aggregate: mean, 95% CI from quantiles
#   5. Compute unmatched concordance (full EUR N, same criterion)
#   6. Emit sign agreement stats from lead_sign_agree column
#
# Output:
#   --out: tier_a_retention.tsv
#         (trait, n_afr_tier_a, mean_retention, ci95_lo, ci95_hi,
#          n_bootstraps, unmatched_concordance)
#   --out-sign: sign_agreement.tsv
#         (trait, n_loci_checked, n_sign_agree, frac_sign_agree)
#
# CLI:
#   Rscript compute_tier_a_retention.R \
#     --tier-assignments <tier_assignments.tsv> \
#     --coloc-dir <results/matched_n/coloc/> \
#     --unmatched-coloc-dir <results/phase2/coloc/> \
#     --out <tier_a_retention.tsv> \
#     --out-sign <sign_agreement.tsv> \
#     --concordance-threshold 0.8 \
#     --n-bootstraps 100
# =============================================================================

suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
})

option_list <- list(
  make_option("--tier-assignments", dest = "tier_assignments", type = "character",
              help = "Path to Phase 2 tier_assignments.tsv"),
  make_option("--coloc-dir", dest = "coloc_dir", type = "character",
              help = "Root of bootstrap coloc results (results/matched_n/coloc/)"),
  make_option("--unmatched-coloc-dir", dest = "unmatched_coloc_dir", type = "character",
              help = "Root of Phase 2 unmatched coloc results (full EUR N)"),
  make_option("--out", dest = "out", type = "character",
              help = "Output path for tier_a_retention.tsv"),
  make_option("--out-sign", dest = "out_sign", type = "character",
              help = "Output path for sign_agreement.tsv"),
  make_option("--out-per-boot", dest = "out_per_boot", type = "character",
              default = NULL,
              help = "Output path for per_bootstrap_retention.tsv (D-06c violin input)"),
  make_option("--concordance-threshold", dest = "concordance_threshold",
              type = "double", default = 0.8,
              help = "PP.H4 threshold for Tier A (default 0.8, D-02a)"),
  make_option("--n-bootstraps", dest = "n_bootstraps", type = "integer",
              default = 100L, help = "Number of bootstrap resamples (default 100)")
)

opt <- parse_args(OptionParser(option_list = option_list))

stopifnot(!is.null(opt$tier_assignments), !is.null(opt$coloc_dir),
          !is.null(opt$out))

threshold <- opt$concordance_threshold
n_boot <- opt$n_bootstraps

# ---------------------------------------------------------------------------
# 1. Load tier assignments, filter to AFR Tier A
# ---------------------------------------------------------------------------
tiers <- fread(opt$tier_assignments)

# Normalize column names for robustness
setnames(tiers, tolower(names(tiers)))

afr_tier_a <- tiers[tolower(ancestry) == "afr" & toupper(tier) == "A"]

if (nrow(afr_tier_a) == 0) {
  stop("No AFR Tier A loci found in tier_assignments.tsv", call. = FALSE)
}

# Get unique traits and their Tier A loci
traits_with_loci <- split(afr_tier_a$region_id, afr_tier_a$trait)

cat("[compute_tier_a_retention] Found", length(traits_with_loci), "traits with AFR Tier A loci\n")

# ---------------------------------------------------------------------------
# Helper: check if a locus achieves Tier A in a given coloc_summary.tsv
# ---------------------------------------------------------------------------
check_tier_a <- function(coloc_tsv_path, threshold) {
  if (!file.exists(coloc_tsv_path)) {
    return(list(is_tier_a = FALSE, sign_agrees = integer(0)))
  }

  dt <- tryCatch(fread(coloc_tsv_path), error = function(e) NULL)
  if (is.null(dt) || nrow(dt) == 0) {
    return(list(is_tier_a = FALSE, sign_agrees = integer(0)))
  }

  # Tier A criterion: max pph4 >= threshold AND at least one signal with
  # pph4 >= threshold (treating each signal row as a potential QTL coloc)
  max_pph4 <- max(dt$pph4, na.rm = TRUE)

  # "at least one QTL coloc >= threshold" means at least one signal row
  # with pph4 >= threshold. In the matched-N context, each signal row
  # from coloc.susie represents a CS pair; any row achieving threshold
  # counts as QTL-level evidence.
  any_qtl_above <- any(dt$pph4 >= threshold, na.rm = TRUE)

  is_tier_a <- (max_pph4 >= threshold) && any_qtl_above

  # Collect sign agreement values
  sign_col <- if ("lead_sign_agree" %in% names(dt)) dt$lead_sign_agree else integer(0)

  list(is_tier_a = is_tier_a, sign_agrees = sign_col)
}

# ---------------------------------------------------------------------------
# 2-4. Per-trait x per-bootstrap retention computation
# ---------------------------------------------------------------------------
retention_results <- list()
sign_results <- list()
per_boot_rows <- list()  # for D-06c violin: trait x bootstrap_idx x retention

for (trait in names(traits_with_loci)) {
  loci <- traits_with_loci[[trait]]
  n_tier_a <- length(loci)

  cat("[compute_tier_a_retention] Trait:", trait, " | AFR Tier A loci:", n_tier_a, "\n")

  # Per-bootstrap retention
  retention_per_boot <- numeric(n_boot)
  all_sign_agrees <- integer(0)

  for (b in seq_len(n_boot)) {
    n_retained <- 0L

    for (locus in loci) {
      coloc_path <- file.path(
        opt$coloc_dir, trait, locus,
        paste0("bootstrap_", b), "coloc_summary.tsv"
      )
      result <- check_tier_a(coloc_path, threshold)

      if (result$is_tier_a) n_retained <- n_retained + 1L
      all_sign_agrees <- c(all_sign_agrees, result$sign_agrees)
    }

    retention_per_boot[b] <- n_retained / n_tier_a
  }

  # Collect per-bootstrap rows for D-06c violin input
  for (b in seq_len(n_boot)) {
    per_boot_rows[[length(per_boot_rows) + 1L]] <- data.table(
      trait = trait,
      bootstrap_idx = b,
      retention = retention_per_boot[b]
    )
  }

  mean_ret <- mean(retention_per_boot)
  ci <- quantile(retention_per_boot, probs = c(0.025, 0.975))

  # ---------------------------------------------------------------------------
  # 5. Unmatched concordance (D-02d): full EUR N, same Tier A criterion
  # ---------------------------------------------------------------------------
  unmatched_concordance <- NA_real_
  if (!is.null(opt$unmatched_coloc_dir) && dir.exists(opt$unmatched_coloc_dir)) {
    n_unmatched_retained <- 0L
    for (locus in loci) {
      unmatched_path <- file.path(
        opt$unmatched_coloc_dir, trait, locus, "coloc_summary.tsv"
      )
      unmatched_result <- check_tier_a(unmatched_path, threshold)
      if (unmatched_result$is_tier_a) n_unmatched_retained <- n_unmatched_retained + 1L
    }
    unmatched_concordance <- n_unmatched_retained / n_tier_a
  }

  retention_results[[trait]] <- data.table(
    trait = trait,
    n_afr_tier_a = n_tier_a,
    mean_retention = round(mean_ret, 6),
    ci95_lo = round(ci[[1]], 6),
    ci95_hi = round(ci[[2]], 6),
    n_bootstraps = n_boot,
    unmatched_concordance = round(unmatched_concordance, 6)
  )

  # ---------------------------------------------------------------------------
  # 6. Sign agreement (D-02c)
  # ---------------------------------------------------------------------------
  valid_signs <- all_sign_agrees[!is.na(all_sign_agrees)]
  n_checked <- length(valid_signs)
  n_agree <- sum(valid_signs == 1L)
  frac_agree <- if (n_checked > 0) n_agree / n_checked else NA_real_

  sign_results[[trait]] <- data.table(
    trait = trait,
    n_loci_checked = n_checked,
    n_sign_agree = n_agree,
    frac_sign_agree = round(frac_agree, 6)
  )

  # D-02c: WARN if sign agreement < 98%
  if (!is.na(frac_agree) && frac_agree < 0.98) {
    message(sprintf(
      "WARN: [D-02c] Trait %s sign agreement = %.1f%% (< 98%%) — potential pipeline bug",
      trait, frac_agree * 100
    ))
  }
}

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
out_retention <- rbindlist(retention_results)
dir.create(dirname(opt$out), recursive = TRUE, showWarnings = FALSE)
fwrite(out_retention, opt$out, sep = "\t")
cat("[compute_tier_a_retention] wrote", nrow(out_retention), "traits to", opt$out, "\n")

if (!is.null(opt$out_sign)) {
  out_sign <- rbindlist(sign_results)
  dir.create(dirname(opt$out_sign), recursive = TRUE, showWarnings = FALSE)
  fwrite(out_sign, opt$out_sign, sep = "\t")
  cat("[compute_tier_a_retention] wrote", nrow(out_sign), "traits to", opt$out_sign, "\n")
}

# ---------------------------------------------------------------------------
# Write per-bootstrap retention (D-06c violin input)
# ---------------------------------------------------------------------------
if (!is.null(opt$out_per_boot)) {
  out_per_boot <- rbindlist(per_boot_rows)
  dir.create(dirname(opt$out_per_boot), recursive = TRUE, showWarnings = FALSE)
  fwrite(out_per_boot, opt$out_per_boot, sep = "\t")
  cat("[compute_tier_a_retention] wrote", nrow(out_per_boot), "per-bootstrap rows to", opt$out_per_boot, "\n")
}

cat("[compute_tier_a_retention] done.\n")
