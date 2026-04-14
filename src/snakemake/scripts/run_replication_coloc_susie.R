#!/usr/bin/env Rscript
# Plan 09-04 Task 1 — coloc.susie re-estimation wrapper.
#
# Runs coloc::coloc.susie(discovery_fit, replication_fit) for a single
# (signal_id × cohort) pair and emits a PP.H4 sweep JSON per D-03b:
#   replicated_pph4_0.5 / 0.7 / 0.8 / 0.9  (boolean per threshold)
# plus the best-pair coloc summary (Pattern 6 Option A from Phase 1 01-04).
#
# Output schema intentionally mirrors Phase 1 run_coloc_susie.R so downstream
# augment / aggregation consumers (Plan 09-05 §G) can reuse existing code:
#   signal_id, cohort, coloc_succeeded, pph4_best,
#   best_hit1, best_hit2, nsnps, susie_pairs (full pairwise),
#   replicated_pph4_{0.5,0.7,0.8,0.9}
#
# Failure mode: tryCatch wraps coloc.susie AND readRDS — any error produces
# coloc_succeeded=FALSE with the error message preserved; the JSON still
# carries the sweep columns (set to NA) so Plan 09-05 can join uniformly.
#
# CLI:
#   Rscript run_replication_coloc_susie.R \
#     disc=<discovery .fit.rds> rep=<replication .fit.rds> \
#     signal_id=<id> cohort=<cohort_key> \
#     thresholds=<0.5,0.7,0.8,0.9> out=<output.json>

suppressPackageStartupMessages({
  library(coloc)
  library(jsonlite)
})

# %||% operator — defined BEFORE the CLI block that uses it (Wave-3 M-2
# revision convention). Vector/list-safe.
`%||%` <- function(a, b) {
  if (is.null(a) || length(a) == 0L) return(b)
  if (length(a) == 1L && !is.list(a)) {
    if (is.na(a) || identical(a, "")) return(b)
  }
  a
}


#' Run coloc.susie on a discovery/replication SuSiE pair and emit the
#' Plan 09-04 JSON schema.
#'
#' @param disc_fit_path path to Phase-1 discovery .fit.rds
#' @param rep_fit_path  path to Wave-3 replication .fit.rds
#' @param signal_id character signal ID (manifest row's signal_id)
#' @param cohort character cohort key (manifest row's cohort)
#' @param pph4_thresholds numeric vector of sweep thresholds
#' @param output_json path to write JSON
#' @return invisible list (also written to JSON)
run_replication_coloc <- function(
  disc_fit_path,
  rep_fit_path,
  signal_id,
  cohort,
  pph4_thresholds = c(0.5, 0.7, 0.8, 0.9),
  output_json
) {
  # Wrap BOTH readRDS + coloc.susie in the same tryCatch so either failure
  # mode yields coloc_succeeded=FALSE (T-09-16 mitigation).
  res <- tryCatch({
    disc_fit <- readRDS(disc_fit_path)
    rep_fit  <- readRDS(rep_fit_path)

    # A6 safety (inherited from Phase 1 run_coloc_susie.R): ensure S3
    # dispatch finds class("susie"). Wave-3 runsusie already annotates,
    # but belt-and-suspenders against schema drift.
    if (!inherits(disc_fit, "susie")) class(disc_fit) <- c("susie", class(disc_fit))
    if (!inherits(rep_fit,  "susie")) class(rep_fit)  <- c("susie", class(rep_fit))

    s <- coloc::coloc.susie(disc_fit, rep_fit)
    list(summary = s$summary, error = NULL)
  }, error = function(e) {
    list(summary = NULL, error = conditionMessage(e))
  })

  # Construct sweep column names up front so both success/failure paths
  # emit the same keys — simplifies Plan 09-05 join.
  sweep_names <- sprintf("replicated_pph4_%s", format(pph4_thresholds, trim = TRUE))

  if (is.null(res$summary) || !is.data.frame(res$summary) || nrow(res$summary) == 0L) {
    # Failure / no-signal path
    sweep <- setNames(as.list(rep(NA, length(pph4_thresholds))), sweep_names)
    out <- c(
      list(
        signal_id = signal_id,
        cohort = cohort,
        coloc_succeeded = FALSE,
        error = res$error %||% "coloc.susie returned empty summary",
        pph4_best = NA_real_,
        best_hit1 = NA_character_,
        best_hit2 = NA_character_,
        nsnps = NA_integer_,
        susie_pairs = list()
      ),
      sweep
    )
  } else {
    summ <- res$summary
    best_idx <- which.max(summ$PP.H4.abf)
    pph4_best <- as.numeric(summ$PP.H4.abf[best_idx])
    sweep_vals <- pph4_best >= pph4_thresholds
    sweep <- setNames(as.list(sweep_vals), sweep_names)

    # Convert summary to a list-of-rows (jsonlite friendly); preserves
    # the full pairwise table for downstream audits.
    susie_pairs <- lapply(seq_len(nrow(summ)), function(i) as.list(summ[i, , drop = FALSE]))

    out <- c(
      list(
        signal_id = signal_id,
        cohort = cohort,
        coloc_succeeded = TRUE,
        error = NULL,
        pph4_best = pph4_best,
        best_hit1 = as.character(summ$hit1[best_idx]),
        best_hit2 = as.character(summ$hit2[best_idx]),
        nsnps = as.integer(summ$nsnps[best_idx]),
        susie_pairs = susie_pairs
      ),
      sweep
    )
  }

  dir.create(dirname(output_json), recursive = TRUE, showWarnings = FALSE)
  jsonlite::write_json(out, output_json, auto_unbox = TRUE, pretty = TRUE, na = "null")
  invisible(out)
}


# ---- CLI entrypoint -----------------------------------------------------
if (!interactive() && sys.nframe() == 0L) {
  raw_args <- commandArgs(trailingOnly = TRUE)
  split_kv <- strsplit(raw_args, "=", fixed = TRUE)
  nm <- setNames(
    vapply(split_kv, function(x) paste(x[-1], collapse = "="), character(1)),
    vapply(split_kv, `[`, character(1), 1)
  )

  required <- c("disc", "rep", "signal_id", "cohort", "out")
  missing_args <- setdiff(required, names(nm))
  if (length(missing_args) > 0) {
    stop(sprintf("missing required CLI args: %s", paste(missing_args, collapse = ", ")))
  }

  thresholds <- as.numeric(strsplit(nm[["thresholds"]] %||% "0.5,0.7,0.8,0.9", ",")[[1]])

  run_replication_coloc(
    disc_fit_path   = nm[["disc"]],
    rep_fit_path    = nm[["rep"]],
    signal_id       = nm[["signal_id"]],
    cohort          = nm[["cohort"]],
    pph4_thresholds = thresholds,
    output_json     = nm[["out"]]
  )
}
