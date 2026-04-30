#!/usr/bin/env Rscript
# =============================================================================
# Phase 1 Wave 4 -- multi-signal SuSiE colocalization replacement for the
# legacy single-variant ABF backend (kept under src/legacy/ for reference
# only, not wired into any active rule). Loads two .fit.rds files produced
# by run_susie_rss.R (Wave 1) and calls coloc::coloc.susie(fit_a, fit_b).
#
# Emits a JSON compatible with legacy downstream consumers:
#   augment_coloc_summary.py, build_coloc_h4_reports.py,
#   build_coloc_top_hits_table.py.
#
# REQ-2 success criterion #4 (multi-signal coloc backend replaces the
# legacy single-variant backend).
# A6 dispatch resolution (see 01-01-SUMMARY.md): fits persisted by
# run_susie_rss.R are already wrapped via coloc:::annotate_susie, so
# coloc::coloc.susie can consume them directly via S3 dispatch on
# class("susie"). We do NOT call runsusie() again here.
#
# trait_pair_coloc_hard_failures bugfix (Stage 1d, 2026-04-21):
# run_susie_rss.R:522-529 picks SNP names per-fit: rsid when sumstats SNP_ID
# column is populated, otherwise chr:pos. The harmonized sumstats catalog is
# heterogeneous — bmi.EUR and asthma.EUR carry real rsids in SNP_ID while
# hypertension/stroke/t2d.EUR carry chr:pos strings. This causes any
# bmi × {hypertension,stroke,t2d} pair to have zero-overlap colnames
# between the two fits; coloc::coloc.bf_bf returns a stub with NULL
# $summary, and `coloc.susie` errors on `ret$summary[, :=(...)]` against
# NULL. Analogous to commit 931a9c8 (QTL coloc rsid mismatch). Fix:
# rewrite each fit's variant names to a common chr:pos key derived from
# CHR and POS columns of the source sumstats files (which every harmonized
# sumstats carries, regardless of SNP_ID content), BEFORE calling
# coloc.susie. No Phase 1 re-fit required.
# =============================================================================

suppressPackageStartupMessages({
  library(optparse)
  library(coloc)
  library(susieR)
  library(jsonlite)
  library(data.table)
  # R.utils is declared in envs/r_coloc.yml but unused in this script body.
  # Make optional so direct invocation under la_multitrait_r (Wave 2 W2 R2 fire,
  # bypassing Snakemake --use-conda per pipeline_canonical_r2_overlay.yaml NOTE
  # option a) does not fail when R.utils is absent. Rule 1 auto-fix
  # (ta-sh2b3 W2 dispatch); revert by reinstating `library(R.utils)` if a
  # downstream code path adds genuine R.utils calls.
  if (requireNamespace("R.utils", quietly = TRUE)) {
    library(R.utils)
  }
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
# trait_pair_coloc_hard_failures (Stage 1d, 2026-04-21):
# Align variant naming between fit_a and fit_b to a common chr:pos key,
# derived from CHR/POS/SNP_ID columns of the source sumstats. Without this,
# cross-trait pairs where one trait's sumstats carry rsids and the other
# carries chr:pos strings produce zero-overlap colnames and crash coloc.susie.
#
# Source resolution: each .fit.rds has a companion .json (same basename)
# written by run_susie_rss.R that carries `sumstats`, `chrom`, `start`, `end`.
# Read the region window from the json, load CHR/POS/SNP_ID from the
# sumstats, build SNP_ID -> chr:pos map, rewrite the fit's colnames.
# -----------------------------------------------------------------------------

load_fit_sidecar <- function(fit_path) {
  json_path <- sub("\\.fit\\.rds$", ".json", fit_path)
  if (!file.exists(json_path)) return(NULL)
  tryCatch(jsonlite::fromJSON(json_path), error = function(e) NULL)
}

load_region_sumstats <- function(sumstats_path, chrom, start, end) {
  if (is.null(sumstats_path) || !file.exists(sumstats_path)) return(NULL)
  df <- tryCatch(data.table::fread(sumstats_path),
                 error = function(e) { message("fread failed: ", conditionMessage(e)); NULL })
  if (is.null(df) || nrow(df) == 0) return(NULL)
  req_cols <- c("CHR", "POS", "SNP_ID")
  if (!all(req_cols %in% names(df))) return(NULL)
  # CHR may be numeric in file but character in json (or vice versa); coerce.
  df <- df[as.character(CHR) == as.character(chrom) &
           POS >= as.integer(start) & POS <= as.integer(end)]
  if (nrow(df) == 0) return(NULL)
  df[, cp := sprintf("%s:%s", CHR, POS)]
  df
}

#' Rewrite a SuSiE fit's variant-level names to chr:pos keys.
#'
#' Drops colnames that don't map to a known SNP_ID (keeps the "null" sentinel
#' column untouched, matching coloc::coloc.bf_bf's expectation). Rewrites
#' alpha, lbf_variable, mu, mu2 (all L x n_snps matrices), pip (named vector),
#' and the per-CS names attribute on fit$sets$cs[[i]]. Credible-set integer
#' indices still point at the ORIGINAL column positions, so we only prune
#' columns that have no sumstats map AND are not referenced by any CS.
rewrite_fit_to_chrpos <- function(fit, ss_df, label = "") {
  if (is.null(ss_df) || nrow(ss_df) == 0) {
    message(sprintf("[rewrite_fit:%s] no sumstats mapping available; leaving fit unchanged", label))
    return(list(fit = fit, n_mapped = NA_integer_, n_total = NA_integer_))
  }
  rsid_map <- setNames(as.character(ss_df$cp), as.character(ss_df$SNP_ID))

  rewrite_names <- function(nms) {
    out <- ifelse(nms == "null", "null", unname(rsid_map[nms]))
    out
  }

  # Identify columns referenced by any CS (to preserve index validity).
  cs_ref_idx <- integer(0)
  if (!is.null(fit$sets) && !is.null(fit$sets$cs)) {
    for (cs in fit$sets$cs) cs_ref_idx <- union(cs_ref_idx, as.integer(cs))
  }

  rewrite_matrix <- function(x) {
    if (is.null(x) || is.null(colnames(x))) return(list(x = x, keep = NULL))
    cn <- colnames(x)
    new_cn <- rewrite_names(cn)
    # Keep a column if (a) it rewrote successfully, (b) it is "null" sentinel,
    # or (c) it is referenced by a CS (even if unmapped — we refuse to break
    # the CS index → variant-name pointer).
    keep <- !is.na(new_cn) | cn == "null" | seq_along(cn) %in% cs_ref_idx
    # For CS-referenced-but-unmapped columns, fall back to the original name
    # so the CS attr-name stays valid. This is conservative: such variants
    # simply won't participate in the coloc intersect.
    new_cn[is.na(new_cn) & keep] <- cn[is.na(new_cn) & keep]
    list(x = x[, keep, drop = FALSE], keep = keep, new_cn = new_cn[keep])
  }

  # Rewrite alpha first — we use its keep mask to align other L x n_snps slots.
  a_res <- rewrite_matrix(fit$alpha)
  if (!is.null(a_res$keep)) {
    fit$alpha <- a_res$x
    colnames(fit$alpha) <- a_res$new_cn

    align <- function(mat) {
      if (is.null(mat) || is.null(colnames(mat)) || ncol(mat) != length(a_res$keep)) return(mat)
      mat <- mat[, a_res$keep, drop = FALSE]
      colnames(mat) <- a_res$new_cn
      mat
    }
    fit$lbf_variable <- align(fit$lbf_variable)
    fit$mu           <- align(fit$mu)
    fit$mu2          <- align(fit$mu2)

    # Rebuild CS index: old column indices → new column indices under keep.
    if (!is.null(fit$sets) && !is.null(fit$sets$cs)) {
      old_to_new <- cumsum(a_res$keep)
      for (i in seq_along(fit$sets$cs)) {
        old_idx <- as.integer(fit$sets$cs[[i]])
        old_names <- names(fit$sets$cs[[i]])
        new_idx <- old_to_new[old_idx]
        # Filter out any CS indices that somehow got dropped (shouldn't happen
        # given keep logic above, but defensive).
        valid <- old_idx <= length(a_res$keep) & a_res$keep[old_idx]
        new_idx <- new_idx[valid]
        if (!is.null(old_names)) {
          new_names <- rewrite_names(old_names[valid])
          # Fall back to old name if unmapped.
          new_names[is.na(new_names)] <- old_names[valid][is.na(new_names)]
          names(new_idx) <- new_names
        }
        fit$sets$cs[[i]] <- new_idx
      }
    }
  }

  # Rewrite pip (named vector over all variants).
  if (!is.null(fit$pip) && !is.null(names(fit$pip))) {
    nm <- names(fit$pip)
    new_nm <- rewrite_names(nm)
    keep_pip <- !is.na(new_nm) | nm == "null"
    fit$pip <- fit$pip[keep_pip]
    names(fit$pip) <- new_nm[keep_pip]
  }

  total <- if (!is.null(a_res$keep)) length(a_res$keep) else NA_integer_
  mapped <- if (!is.null(a_res$keep)) sum(a_res$keep) else NA_integer_
  list(fit = fit, n_mapped = mapped, n_total = total)
}

sc_a <- load_fit_sidecar(opt$fit_a)
sc_b <- load_fit_sidecar(opt$fit_b)
ss_a <- if (!is.null(sc_a)) load_region_sumstats(sc_a$sumstats, sc_a$chrom, sc_a$start, sc_a$end) else NULL
ss_b <- if (!is.null(sc_b)) load_region_sumstats(sc_b$sumstats, sc_b$chrom, sc_b$start, sc_b$end) else NULL

# Only rewrite if both sides can be mapped. If either is missing, leave the
# fits unchanged and let coloc.susie attempt naive alignment (falls through
# to the error-JSON path below when it fails).
if (!is.null(ss_a) && !is.null(ss_b)) {
  res_a <- rewrite_fit_to_chrpos(fit_a, ss_a, label = "fit_a")
  res_b <- rewrite_fit_to_chrpos(fit_b, ss_b, label = "fit_b")
  fit_a <- res_a$fit
  fit_b <- res_b$fit
  cat(sprintf("[run_coloc_susie] %s: chr:pos rewrite fit_a=%d/%d fit_b=%d/%d (intersect=%d)\n",
              opt$pair_id,
              res_a$n_mapped, res_a$n_total,
              res_b$n_mapped, res_b$n_total,
              length(intersect(colnames(fit_a$alpha), colnames(fit_b$alpha)))))
} else {
  cat(sprintf("[run_coloc_susie] %s: skipping chr:pos rewrite (sc_a=%s, sc_b=%s, ss_a=%s, ss_b=%s)\n",
              opt$pair_id,
              !is.null(sc_a), !is.null(sc_b),
              !is.null(ss_a), !is.null(ss_b)))
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

write_status_json <- function(status, extra = list()) {
  empty_summary <- list(
    nsnps     = NA_integer_,
    PP.H0.abf = NA_real_,
    PP.H1.abf = NA_real_,
    PP.H2.abf = NA_real_,
    PP.H3.abf = NA_real_,
    PP.H4.abf = NA_real_
  )
  base <- list(
    pair_id       = opt$pair_id,
    status        = status,
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
  out <- modifyList(base, extra)
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(out, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
}

if (n_cs_a == 0 || n_cs_b == 0) {
  write_status_json("no_signal")
  cat("[run_coloc_susie] no signal for", opt$pair_id,
      "(n_cs_a=", n_cs_a, "n_cs_b=", n_cs_b, ") -- wrote empty JSON\n")
  quit(status = 0)
}

# -----------------------------------------------------------------------------
# Main coloc.susie call
# res$summary is a data.frame with one row per pairwise CS comparison:
#   nsnps, hit1, hit2, PP.H0.abf..PP.H4.abf, idx1, idx2
# -----------------------------------------------------------------------------
res <- tryCatch(
  coloc::coloc.susie(fit_a, fit_b),
  error = function(e) {
    cat("[run_coloc_susie] coloc.susie errored:", conditionMessage(e), "\n")
    NULL
  }
)

if (is.null(res) || is.null(res$summary)) {
  # Defensive: even after rewrite, if coloc.susie still errors or returns a
  # stub (e.g. a fresh "no intersect" case), emit a structured error JSON
  # rather than exiting with a non-zero status and no output.
  write_status_json("error", list(error_msg = "coloc.susie returned NULL or NULL-summary"))
  cat("[run_coloc_susie] wrote error JSON for", opt$pair_id, "\n")
  quit(status = 0)
}

summary_dt <- as.data.table(res$summary)

# -----------------------------------------------------------------------------
# Property check: PP.H0..H4 should sum to approximately 1.0 per row
# (Pattern 6 / test_coloc_susie_posterior_sum.py)
# -----------------------------------------------------------------------------
pp_cols <- c("PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf")
if (all(pp_cols %in% names(summary_dt)) && nrow(summary_dt) > 0) {
  # Only check rows where PPs are actually populated (coloc.bf_bf can return
  # NA PPs when posterior overlap is too small — see overlap.min warning).
  pp_mat <- as.matrix(summary_dt[, ..pp_cols])
  row_sums <- rowSums(pp_mat)
  complete <- !is.na(row_sums)
  if (any(complete)) {
    max_dev <- max(abs(row_sums[complete] - 1.0), na.rm = TRUE)
    if (is.finite(max_dev) && max_dev > 1e-4) {
      warning(sprintf(
        "[run_coloc_susie] posterior sum deviation %.2e > 1e-4 detected in %d rows",
        max_dev, sum(abs(row_sums[complete] - 1.0) > 1e-4, na.rm = TRUE)))
    }
  }
}

# -----------------------------------------------------------------------------
# Legacy compat layer (Pattern 6 Option A):
#   summary     = best-pairwise row (max PP.H4.abf) -- matches legacy consumer
#   susie_pairs = full list of all pairwise rows    -- new field for Phase 1
# When all PP.H4.abf values are NA (low posterior overlap per overlap.min),
# coloc.bf_bf returns rows with valid nsnps/hit1/hit2 but NA PPs. In that
# case fall back to the first row so downstream consumers still get a
# numeric nsnps and hit names for provenance.
# -----------------------------------------------------------------------------
if (nrow(summary_dt) > 0 && "PP.H4.abf" %in% names(summary_dt)) {
  pph4 <- summary_dt$PP.H4.abf
  if (all(is.na(pph4))) {
    best_idx <- 1L
    result_status <- "no_posterior"  # rows exist but PPs are NA (overlap too small)
  } else {
    best_idx <- which.max(pph4)
    result_status <- "success"
  }
  best_row <- as.list(summary_dt[best_idx])
} else {
  best_idx <- integer(0)
  best_row <- list()
  result_status <- "no_signal"
}

output <- list(
  pair_id       = opt$pair_id,
  status        = result_status,
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
    "(n_cs_a=", n_cs_a, "n_cs_b=", n_cs_b, ") status=", result_status, "\n")
