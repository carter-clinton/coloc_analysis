#!/usr/bin/env Rscript
# =============================================================================
# Phase 1 Wave 4 -- coloc.susie replacement for the legacy run_coloc.R
# (which used coloc::coloc.abf). Loads two .fit.rds files produced by
# run_susie_rss.R (Wave 1) and calls coloc::coloc.susie(fit_a, fit_b).
#
# Emits a JSON compatible with legacy downstream consumers:
#   augment_coloc_summary.py, build_coloc_h4_reports.py,
#   build_coloc_top_hits_table.py.
#
# REQ-2 success criterion #4: coloc.susie replaces coloc.abf.
# A6 dispatch resolution (see 01-01-SUMMARY.md): fits persisted by
# run_susie_rss.R are already wrapped via coloc:::annotate_susie, so
# coloc::coloc.susie can consume them directly via S3 dispatch on
# class("susie"). We do NOT call runsusie() again here.
# =============================================================================

suppressPackageStartupMessages({
  library(optparse)
  library(coloc)
  library(susieR)
  library(jsonlite)
  library(data.table)
})

`%||%` <- function(x, y) if (!is.null(x)) x else y

option_list <- list(
  make_option("--fit-a",    dest = "fit_a",    type = "character",
              help = "Path to trait A .fit.rds from run_susie_rss.R"),
  make_option("--fit-b",    dest = "fit_b",    type = "character",
              help = "Path to trait B .fit.rds from run_susie_rss.R"),
  make_option("--policy",   type = "character", default = "config/susie_policy.yaml",
              help = "SuSiE policy YAML (parsed for provenance only)"),
  make_option("--pair-id",  dest = "pair_id",  type = "character",
              help = "Pair identifier from coloc_manifest.tsv"),
  make_option("--manifest", type = "character", default = NA_character_,
              help = "Path to coloc_manifest.tsv (optional; used to recover trait/ancestry/region)"),
  make_option("--trait-a",  dest = "trait_a",  type = "character", default = NA_character_),
  make_option("--trait-b",  dest = "trait_b",  type = "character", default = NA_character_),
  make_option("--ancestry", type = "character", default = NA_character_),
  make_option("--region",   type = "character", default = NA_character_),
  make_option("--output",   type = "character", help = "Output JSON path")
)
opt <- parse_args(OptionParser(option_list = option_list))

if (is.null(opt$fit_a) || is.null(opt$fit_b) || is.null(opt$output) || is.null(opt$pair_id)) {
  stop("--fit-a, --fit-b, --pair-id, and --output are required", call. = FALSE)
}
stopifnot(file.exists(opt$fit_a), file.exists(opt$fit_b))

fit_a <- readRDS(opt$fit_a)
fit_b <- readRDS(opt$fit_b)

# A6 safety: ensure coloc.susie S3 dispatch finds class("susie").
# run_susie_rss.R already annotates via coloc:::annotate_susie, but
# belt-and-suspenders in case of schema drift.
if (!inherits(fit_a, "susie")) class(fit_a) <- c("susie", class(fit_a))
if (!inherits(fit_b, "susie")) class(fit_b) <- c("susie", class(fit_b))

# Recover trait/ancestry/region from manifest if not provided on CLI
if (!is.na(opt$manifest) && !is.null(opt$manifest) && file.exists(opt$manifest)) {
  mf <- fread(opt$manifest)
  if ("pair_id" %in% names(mf)) {
    row <- mf[pair_id == opt$pair_id]
    if (nrow(row) == 1) {
      if (is.na(opt$trait_a)  && "trait_a"  %in% names(row)) opt$trait_a  <- as.character(row$trait_a)
      if (is.na(opt$trait_b)  && "trait_b"  %in% names(row)) opt$trait_b  <- as.character(row$trait_b)
      if (is.na(opt$ancestry) && "ancestry" %in% names(row)) opt$ancestry <- as.character(row$ancestry)
      if (is.na(opt$region)   && "region"   %in% names(row)) opt$region   <- as.character(row$region)
    }
  }
}

# -----------------------------------------------------------------------------
# Empty credible-set guard (Pitfall 6 from 01-RESEARCH.md)
# If either fit has zero credible sets, coloc.susie errors. Emit a no-signal
# JSON compatible with the legacy schema and exit cleanly.
# -----------------------------------------------------------------------------
cs_a <- fit_a$sets$cs %||% list()
cs_b <- fit_b$sets$cs %||% list()
n_cs_a <- length(cs_a)
n_cs_b <- length(cs_b)

if (n_cs_a == 0 || n_cs_b == 0) {
  empty_summary <- list(
    nsnps     = NA_integer_,
    PP.H0.abf = NA_real_,
    PP.H1.abf = NA_real_,
    PP.H2.abf = NA_real_,
    PP.H3.abf = NA_real_,
    PP.H4.abf = NA_real_
  )
  empty <- list(
    pair_id       = opt$pair_id,
    status        = "no_signal",
    trait_a       = opt$trait_a,
    trait_b       = opt$trait_b,
    ancestry      = opt$ancestry,
    region        = opt$region,
    base_region   = opt$region,
    n_cs_a        = n_cs_a,
    n_cs_b        = n_cs_b,
    summary       = empty_summary,
    susie_pairs   = list(),
    n_pairs_total = 0
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(empty, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
  cat("[run_coloc_susie] no signal for", opt$pair_id,
      "(n_cs_a=", n_cs_a, "n_cs_b=", n_cs_b, ") -- wrote empty JSON\n")
  quit(status = 0)
}

# -----------------------------------------------------------------------------
# Main coloc.susie call
# res$summary is a data.frame with one row per pairwise CS comparison:
#   nsnps, hit1, hit2, PP.H0.abf..PP.H4.abf, idx1, idx2
# -----------------------------------------------------------------------------
res <- coloc::coloc.susie(fit_a, fit_b)
summary_dt <- as.data.table(res$summary)

# -----------------------------------------------------------------------------
# Property check: PP.H0..H4 should sum to approximately 1.0 per row
# (Pattern 6 / test_coloc_susie_posterior_sum.py)
# -----------------------------------------------------------------------------
pp_cols <- c("PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf")
if (all(pp_cols %in% names(summary_dt)) && nrow(summary_dt) > 0) {
  row_sums <- rowSums(summary_dt[, ..pp_cols])
  max_dev <- max(abs(row_sums - 1.0), na.rm = TRUE)
  if (is.finite(max_dev) && max_dev > 1e-4) {
    warning(sprintf(
      "[run_coloc_susie] posterior sum deviation %.2e > 1e-4 detected in %d rows",
      max_dev, sum(abs(row_sums - 1.0) > 1e-4, na.rm = TRUE)))
  }
}

# -----------------------------------------------------------------------------
# Legacy compat layer (Pattern 6 Option A):
#   summary     = best-pairwise row (max PP.H4.abf) -- matches legacy consumer
#   susie_pairs = full list of all pairwise rows    -- new field for Phase 1
# -----------------------------------------------------------------------------
if (nrow(summary_dt) > 0 && "PP.H4.abf" %in% names(summary_dt)) {
  best_idx <- which.max(summary_dt$PP.H4.abf)
  best_row <- if (length(best_idx) == 1) as.list(summary_dt[best_idx]) else list()
} else {
  best_idx <- integer(0)
  best_row <- list()
}

output <- list(
  pair_id       = opt$pair_id,
  status        = "success",
  trait_a       = opt$trait_a,
  trait_b       = opt$trait_b,
  ancestry      = opt$ancestry,
  region        = opt$region,
  base_region   = opt$region,
  summary       = best_row,                                        # legacy-compat
  susie_pairs   = lapply(seq_len(nrow(summary_dt)),                # new field
                         function(i) as.list(summary_dt[i])),
  n_pairs_total = nrow(summary_dt),
  n_cs_a        = n_cs_a,
  n_cs_b        = n_cs_b
)

dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
write_json(output, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
cat("[run_coloc_susie] wrote", opt$output,
    "with", nrow(summary_dt), "pairwise rows",
    "(n_cs_a=", n_cs_a, "n_cs_b=", n_cs_b, ")\n")
