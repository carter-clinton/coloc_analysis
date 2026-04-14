#!/usr/bin/env Rscript
# Plan 09-04 Task 2 — IVW fixed-effect meta-analysis across ancestry-matched
# replication cohorts per signal (D-06b).
#
# Uses metafor::rma.uni(method = "FE") — NOT a hand-rolled IVW — so the
# output standard error correctly accounts for heterogeneity-conditional
# variance shrinkage and downstream consumers get the metafor diagnostics
# for free (QE, pval, I², CI) if they later inspect the fit object.
#
# T-09-17 mitigation: groups by cohort_ancestry before meta so EUR and AFR
# replication cohorts NEVER enter the same meta row for a signal. BBJ
# (EAS, is_generalization=TRUE) is excluded upstream — it's reported as
# generalization, not primary replication (D-05c).
#
# CLI:
#   Rscript aggregate_replication_meta.R <per_cohort.tsv> <output.tsv>
#
# Expected input columns:
#   signal_id, cohort, cohort_ancestry, beta_replication, se_replication,
#   is_generalization (optional; rows with TRUE are excluded from meta)

suppressPackageStartupMessages({
  library(metafor)
  library(data.table)
})


#' IVW fixed-effect meta for a single (signal_id × cohort_ancestry) group.
#'
#' Input data.table must have columns beta_replication, se_replication,
#' cohort_ancestry, cohort. Returns a one-row data.table or NULL if fewer
#' than `min_cohorts` contributing cohorts after NA filter.
#'
#' @param sub data.table with per-cohort rows for ONE signal_id
#' @param min_cohorts minimum cohorts required for a meta row (default 2)
ivw_meta_per_signal <- function(sub, min_cohorts = 2L) {
  valid <- sub[
    !is.na(beta_replication) &
    !is.na(se_replication) &
    se_replication > 0
  ]
  if (nrow(valid) < min_cohorts) return(NULL)

  fit <- tryCatch(
    metafor::rma.uni(
      yi  = valid$beta_replication,
      sei = valid$se_replication,
      method = "FE"
    ),
    error = function(e) NULL
  )
  if (is.null(fit)) return(NULL)

  # WR-08 fix: do NOT emit signal_id here — data.table's by-group return
  # already carries the grouping columns (signal_id + cohort_ancestry).
  # Emitting signal_id as a column of the returned data.table causes
  # either "duplicated column signal_id" (newer data.table) or silent
  # column drop (older data.table) depending on version. Let the grouping
  # machinery attach grouping cols to avoid version-dependent behavior.
  data.table(
    meta_ancestry = valid$cohort_ancestry[1],
    beta_meta = as.numeric(fit$beta),
    se_meta = as.numeric(fit$se),
    p_meta = as.numeric(fit$pval),
    meta_n_cohorts_contributing = nrow(valid),
    meta_cohorts = paste(valid$cohort, collapse = ",")
  )
}


#' Aggregate a combined per-cohort TSV into per-(signal × ancestry) meta rows.
#'
#' D-05c: is_generalization=TRUE rows (BBJ) excluded from meta.
#' D-06b: group by signal_id AND cohort_ancestry to enforce ancestry-matched
#' meta (T-09-17 mitigation).
#'
#' @param per_cohort_tsv path to combined per-cohort effect-size TSV
#' @param output_tsv path to write meta TSV
aggregate_ivw <- function(per_cohort_tsv, output_tsv) {
  df <- fread(per_cohort_tsv)

  # Ancestry-match gate (T-09-17)
  if (!"cohort_ancestry" %in% names(df)) {
    stop("per-cohort TSV missing cohort_ancestry column — cannot enforce D-06b ancestry-matched meta")
  }

  # Exclude generalization rows (BBJ) per D-05c if the flag is present.
  # WR-06 fix: coerce safely from any of (logical, "True"/"TRUE"/"true"
  # with optional whitespace, 0/1, "0"/"1"). NA is treated as FALSE
  # (i.e., kept in meta) only when the row is already ancestry-matched
  # upstream; the NA->FALSE coercion here preserves the prior behavior
  # for NA rows but adds defensive handling for pandas 0/1 booleans and
  # whitespace-padded strings.
  if ("is_generalization" %in% names(df)) {
    is_gen_raw <- df$is_generalization
    is_gen_norm <- trimws(tolower(as.character(is_gen_raw)))
    is_gen_bool <- ifelse(
      is.na(is_gen_raw) | is_gen_norm %in% c("", "na"),
      FALSE,
      is_gen_norm %in% c("true", "t", "1")
    )
    df[, is_generalization := is_gen_bool]
    df <- df[is_generalization == FALSE]
  }

  # Group by (signal_id, cohort_ancestry); meta per group.
  results <- df[
    ,
    ivw_meta_per_signal(.SD),
    by = .(signal_id, cohort_ancestry),
    .SDcols = c(
      "signal_id", "cohort", "cohort_ancestry",
      "beta_replication", "se_replication"
    )
  ]

  if (nrow(results) == 0L) {
    # Empty result — still write a header so Snakemake sees the target.
    empty <- data.table(
      signal_id = character(0),
      cohort_ancestry = character(0),
      meta_ancestry = character(0),
      beta_meta = numeric(0),
      se_meta = numeric(0),
      p_meta = numeric(0),
      meta_n_cohorts_contributing = integer(0),
      meta_cohorts = character(0),
      meta_replicated_bonferroni = logical(0)
    )
    fwrite(empty, output_tsv, sep = "\t")
    invisible(empty)
    return(invisible(empty))
  }

  # Bonferroni at meta level — denominator = number of distinct signals
  # that got a meta row (same per-test-family convention as per-cohort).
  n_sig <- uniqueN(results$signal_id)
  alpha_meta <- 0.05 / max(1L, n_sig)
  results[, meta_replicated_bonferroni := p_meta < alpha_meta]

  fwrite(results, output_tsv, sep = "\t")
  invisible(results)
}


# ---- CLI entrypoint -----------------------------------------------------
if (!interactive() && sys.nframe() == 0L) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 2L) {
    stop("usage: Rscript aggregate_replication_meta.R <per_cohort.tsv> <output.tsv>")
  }
  aggregate_ivw(args[1], args[2])
}
