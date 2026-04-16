#!/usr/bin/env Rscript
# =============================================================================
# D-02b SECONDARY METRIC: Credible-set Jaccard similarity at PP.H4 >= 0.5
# D-02c TERTIARY SANITY CHECK: lead-variant direction-of-effect sign agreement
#
# D-02e EXPLICITLY NOT REUSED: Phase 9 joint PP.H4 + effect-size criterion
# (reason: conflates coloc stability with effect-size stability, would
# double-count power loss and inflate observed concordance reduction).
#
# For each trait x bootstrap:
#   1. Load coloc.rds under results/matched_n/coloc/{trait}/*/bootstrap_{b}/
#   2. At loci with BOTH AFR and EUR-matched achieving PP.H4 >= 0.5 (relaxed
#      gate per D-02b), compute Jaccard = |CS_AFR intersect CS_EUR_b| /
#      |CS_AFR union CS_EUR_b|
#   3. Aggregate: mean_jaccard, 95% CI from bootstrap quantiles
#   4. Also emit sign_agreement.tsv per D-02c from coloc_summary.tsv
#
# Output:
#   --out-jaccard: jaccard.tsv
#     (trait, mean_jaccard, ci95_lo, ci95_hi, n_locus_pairs)
#   --out-sign: sign_agreement.tsv
#     (trait, n_loci_checked, n_sign_agree, frac_sign_agree)
#
# CLI:
#   Rscript compute_jaccard.R \
#     --tier-assignments <tier_assignments.tsv> \
#     --coloc-dir <results/matched_n/coloc/> \
#     --out-jaccard <jaccard.tsv> \
#     --out-sign <sign_agreement.tsv> \
#     --relaxed-threshold 0.5 \
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
              help = "Root of bootstrap coloc results"),
  make_option("--out-jaccard", dest = "out_jaccard", type = "character",
              help = "Output path for jaccard.tsv"),
  make_option("--out-sign", dest = "out_sign", type = "character",
              help = "Output path for sign_agreement.tsv"),
  make_option("--relaxed-threshold", dest = "relaxed_threshold",
              type = "double", default = 0.5,
              help = "PP.H4 >= 0.5 relaxed threshold for Jaccard gate (D-02b)"),
  make_option("--n-bootstraps", dest = "n_bootstraps", type = "integer",
              default = 100L, help = "Number of bootstrap resamples")
)

opt <- parse_args(OptionParser(option_list = option_list))

stopifnot(!is.null(opt$tier_assignments), !is.null(opt$coloc_dir),
          !is.null(opt$out_jaccard))

relaxed_threshold <- opt$relaxed_threshold
n_boot <- opt$n_bootstraps

# ---------------------------------------------------------------------------
# 1. Load tier assignments, filter to AFR Tier A
# ---------------------------------------------------------------------------
tiers <- fread(opt$tier_assignments)
setnames(tiers, tolower(names(tiers)))
afr_tier_a <- tiers[tolower(ancestry) == "afr" & toupper(tier) == "A"]

if (nrow(afr_tier_a) == 0) {
  stop("No AFR Tier A loci found in tier_assignments.tsv", call. = FALSE)
}

traits_with_loci <- split(afr_tier_a$region_id, afr_tier_a$trait)

cat("[compute_jaccard] Found", length(traits_with_loci), "traits\n")

# ---------------------------------------------------------------------------
# Helper: extract credible set variants from a coloc.rds object
# Returns list of CS variant name vectors (one per signal)
# ---------------------------------------------------------------------------
extract_cs_variants <- function(fit) {
  if (is.null(fit) || is.null(fit$sets) || is.null(fit$sets$cs)) {
    return(list())
  }
  cs_list <- fit$sets$cs
  # Each CS is a vector of indices; convert to variant names if available
  var_names <- names(fit$pip)
  lapply(cs_list, function(idx) {
    if (!is.null(var_names)) var_names[idx] else as.character(idx)
  })
}

# ---------------------------------------------------------------------------
# Helper: compute Jaccard between two sets of variants
# ---------------------------------------------------------------------------
jaccard <- function(set_a, set_b) {
  if (length(set_a) == 0 && length(set_b) == 0) return(NA_real_)
  intersection_size <- length(intersect(set_a, set_b))
  union_size <- length(union(set_a, set_b))
  if (union_size == 0) return(NA_real_)
  intersection_size / union_size
}

# ---------------------------------------------------------------------------
# Helper: check if a locus passes the relaxed PP.H4 gate
# ---------------------------------------------------------------------------
passes_relaxed_gate <- function(coloc_tsv_path, threshold) {
  if (!file.exists(coloc_tsv_path)) return(FALSE)
  dt <- tryCatch(fread(coloc_tsv_path), error = function(e) NULL)
  if (is.null(dt) || nrow(dt) == 0) return(FALSE)
  # PP.H4 >= 0.5 relaxed gate: at least one signal row above threshold
  any(dt$pph4 >= threshold, na.rm = TRUE)
}

# ---------------------------------------------------------------------------
# 2-3. Per-trait Jaccard computation across bootstraps
# ---------------------------------------------------------------------------
jaccard_results <- list()
sign_results <- list()

for (trait in names(traits_with_loci)) {
  loci <- traits_with_loci[[trait]]
  cat("[compute_jaccard] Trait:", trait, " | Loci:", length(loci), "\n")

  # Collect per-bootstrap Jaccard values
  jaccard_per_boot <- numeric(n_boot)
  n_locus_pairs_per_boot <- integer(n_boot)
  all_sign_agrees <- integer(0)

  for (b in seq_len(n_boot)) {
    locus_jaccards <- numeric(0)

    for (locus in loci) {
      coloc_tsv_path <- file.path(
        opt$coloc_dir, trait, locus,
        paste0("bootstrap_", b), "coloc_summary.tsv"
      )

      # D-02b: both AFR and EUR-matched must achieve PP.H4 >= 0.5
      if (!passes_relaxed_gate(coloc_tsv_path, relaxed_threshold)) next

      # Load coloc.rds for credible set extraction
      coloc_rds_path <- file.path(
        opt$coloc_dir, trait, locus,
        paste0("bootstrap_", b), "coloc.rds"
      )

      if (file.exists(coloc_rds_path)) {
        coloc_obj <- tryCatch(readRDS(coloc_rds_path), error = function(e) NULL)
        if (!is.null(coloc_obj) && !is.null(coloc_obj$coloc_result)) {
          # Extract CS from coloc result's underlying fits
          res <- coloc_obj$coloc_result

          # coloc.susie stores dataset-level CS info
          # CS variants are in the original fit objects
          # For Jaccard, use the union of all CS variants per dataset
          cs_afr_all <- character(0)
          cs_eur_all <- character(0)

          # Access via the stored fit references if available
          if (!is.null(res$dataset1) && !is.null(res$dataset1$sets)) {
            for (cs in res$dataset1$sets$cs) {
              nm <- names(res$dataset1$pip)
              if (!is.null(nm)) cs_afr_all <- union(cs_afr_all, nm[cs])
            }
          }
          if (!is.null(res$dataset2) && !is.null(res$dataset2$sets)) {
            for (cs in res$dataset2$sets$cs) {
              nm <- names(res$dataset2$pip)
              if (!is.null(nm)) cs_eur_all <- union(cs_eur_all, nm[cs])
            }
          }

          if (length(cs_afr_all) > 0 || length(cs_eur_all) > 0) {
            j <- jaccard(cs_afr_all, cs_eur_all)
            if (!is.na(j)) locus_jaccards <- c(locus_jaccards, j)
          }
        }
      }

      # Collect sign agreement from TSV
      if (file.exists(coloc_tsv_path)) {
        dt <- tryCatch(fread(coloc_tsv_path), error = function(e) NULL)
        if (!is.null(dt) && "lead_sign_agree" %in% names(dt)) {
          all_sign_agrees <- c(all_sign_agrees, dt$lead_sign_agree)
        }
      }
    }

    jaccard_per_boot[b] <- if (length(locus_jaccards) > 0) {
      mean(locus_jaccards)
    } else NA_real_

    n_locus_pairs_per_boot[b] <- length(locus_jaccards)
  }

  # Aggregate across bootstraps (excluding NAs from bootstraps with no qualifying loci)
  valid_jaccards <- jaccard_per_boot[!is.na(jaccard_per_boot)]
  if (length(valid_jaccards) > 0) {
    mean_j <- mean(valid_jaccards)
    ci <- quantile(valid_jaccards, probs = c(0.025, 0.975))
    n_pairs <- round(mean(n_locus_pairs_per_boot[!is.na(jaccard_per_boot)]))
  } else {
    mean_j <- NA_real_
    ci <- c(NA_real_, NA_real_)
    n_pairs <- 0L
  }

  jaccard_results[[trait]] <- data.table(
    trait = trait,
    mean_jaccard = round(mean_j, 6),
    ci95_lo = round(ci[[1]], 6),
    ci95_hi = round(ci[[2]], 6),
    n_locus_pairs = n_pairs
  )

  # D-02c sign agreement
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
out_jaccard <- rbindlist(jaccard_results)
dir.create(dirname(opt$out_jaccard), recursive = TRUE, showWarnings = FALSE)
fwrite(out_jaccard, opt$out_jaccard, sep = "\t")
cat("[compute_jaccard] wrote", nrow(out_jaccard), "traits to", opt$out_jaccard, "\n")

if (!is.null(opt$out_sign)) {
  out_sign <- rbindlist(sign_results)
  dir.create(dirname(opt$out_sign), recursive = TRUE, showWarnings = FALSE)
  fwrite(out_sign, opt$out_sign, sep = "\t")
  cat("[compute_jaccard] wrote", nrow(out_sign), "traits to", opt$out_sign, "\n")
}

cat("[compute_jaccard] done.\n")
