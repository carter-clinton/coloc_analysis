#!/usr/bin/env Rscript
# FIQT empirical-Bayes winner's-curse correction wrapper (D-04a).
#
# Consumes : TSV with canonical discovery-signal columns
#              rsid, beta, se, n  (case-insensitive)
# Produces : TSV with the same columns plus
#              beta_FIQT  — FDR-inverse-quantile-transformed beta
#              se_FIQT    — passthrough SE (winnerscurse::FDR_IQT does not
#                           return a shrunken SE; retained verbatim so downstream
#                           consumers have a predictable column name).
#
# References:
#   - Bigdeli TB et al. 2016 Bioinformatics 32:2598-2603 (FIQT definition)
#   - amandaforde/winnerscurse GitHub package (`FDR_IQT` implementation)
#
# Usage (CLI, used by Snakemake rule run_fiqt_on_discovery):
#   Rscript src/snakemake/scripts/run_fiqt.R <input.tsv> <output.tsv>
#
# Usage (library):
#   source("src/snakemake/scripts/run_fiqt.R")
#   df <- data.frame(rsid=..., beta=..., se=..., n=...)
#   df_adj <- apply_fiqt(df)

suppressPackageStartupMessages({
  # Lazy install: winnerscurse is GitHub-only (no CRAN / Bioconductor).
  # envs/r_coloc.yml already ships r-remotes so this one-time install works.
  if (!requireNamespace("winnerscurse", quietly = TRUE)) {
    if (!requireNamespace("remotes", quietly = TRUE)) {
      install.packages("remotes", repos = "https://cloud.r-project.org")
    }
    remotes::install_github(
      "amandaforde/winnerscurse",
      upgrade = "never",
      quiet = TRUE
    )
  }
  library(winnerscurse)
  library(data.table)
})


#' Apply FIQT winner's-curse correction to a data frame of discovery signals.
#'
#' Normalizes column case, validates required columns, calls
#' `winnerscurse::FDR_IQT`, and returns a data frame with `beta_FIQT` and
#' `se_FIQT` appended.
#'
#' NOTE on row order: `winnerscurse::FDR_IQT` internally `dplyr::arrange()`s
#' rows by descending |z|. This function preserves that behavior so callers
#' can rely on the winnerscurse contract; join back by `rsid` if original
#' order matters.
#'
#' @param df data.frame or data.table with columns rsid, beta, se, n
#' @return data.frame with beta_FIQT + se_FIQT columns appended
apply_fiqt <- function(df) {
  df <- as.data.frame(df)
  # Normalize column case (winnerscurse requires lowercase: rsid, beta, se)
  names(df) <- tolower(names(df))
  required <- c("rsid", "beta", "se")
  missing_cols <- setdiff(required, names(df))
  if (length(missing_cols) > 0) {
    stop(sprintf(
      "apply_fiqt: missing required columns: %s (have: %s)",
      paste(missing_cols, collapse = ", "),
      paste(names(df), collapse = ", ")
    ))
  }
  if (!is.numeric(df$beta) || !is.numeric(df$se)) {
    stop("apply_fiqt: beta and se must be numeric")
  }
  # winnerscurse::FDR_IQT requires rsid uniqueness
  if (any(duplicated(df$rsid))) {
    stop("apply_fiqt: rsid column must be unique")
  }

  res <- winnerscurse::FDR_IQT(summary_data = df, min_pval = 1e-300)

  if (!("beta_FIQT" %in% names(res))) {
    stop(sprintf(
      "apply_fiqt: winnerscurse::FDR_IQT did not return beta_FIQT (got: %s)",
      paste(names(res), collapse = ", ")
    ))
  }

  # Passthrough SE: winnerscurse does not emit se_FIQT. Phase 9 downstream
  # consumers expect a se_FIQT column to exist; set it equal to raw SE so
  # the schema is stable.
  res$se_FIQT <- res$se

  res
}


# ---- CLI entrypoint -----------------------------------------------------
# Invoked directly via Rscript; sourced invocations skip this block
# (source() sets sys.nframe() > 0L).
if (!interactive() && sys.nframe() == 0L) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 2) {
    stop("usage: Rscript run_fiqt.R <input.tsv> <output.tsv>")
  }
  input_path <- args[[1]]
  output_path <- args[[2]]

  df_in <- data.table::fread(input_path)
  data.table::setnames(df_in, tolower(names(df_in)))
  df_out <- apply_fiqt(df_in)
  data.table::fwrite(df_out, output_path, sep = "\t")
  message(sprintf(
    "FIQT applied to %d signals; output: %s",
    nrow(df_out),
    output_path
  ))
}
