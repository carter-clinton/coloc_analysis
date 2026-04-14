#!/usr/bin/env Rscript
# Fit SuSiE-RSS on the replication cohort sumstats for a single region.
#
# Reuses config/susie_policy.yaml from Phase 1 (D-08 reuse, not fork). The
# replication fit is consumed by Plan 09-04's coloc.susie re-estimation rule,
# which pairs it against the Phase-1 discovery fit (results/fine_mapping/*.fit.rds).
#
# Invocation pattern mirrors `run_susie_rss.R` but uses `coloc::runsusie` with
# `suffix = 2` so the output fit is immediately consumable by
# `coloc.susie(discovery_fit, replication_fit)` in Wave 4.
#
# Usage (CLI, from Snakemake rule fit_replication_susie):
#   Rscript run_replication_susie.R \
#     sumstats=<path.tsv[.gz]> \
#     ld_panel=<ukbb_ld|hgdp_1kg_afr|thousand_g_eas> \
#     region=<chr:start-end> \
#     policy=config/susie_policy.yaml \
#     out=<fit.rds> \
#     [type=cc|quant] [case_n=N] [ctrl_n=N] [n=N]

suppressPackageStartupMessages({
  library(susieR)
  library(coloc)
  library(data.table)
  library(yaml)
})

# Null-coalesce operator. Defined near the top so the CLI block below can
# use it safely. (M-2 revision from Plan 09-03 checker iteration 2: declare
# BEFORE first use — not at the bottom as the plan draft did.)
# For scalar inputs: treat NULL / length-0 / NA / "" as "missing" and return b.
# For vector / list inputs: treat only NULL / length-0 as missing (return b),
# leave the actual value intact otherwise (NA/"" checks don't apply element-wise
# and would break scalar semantics if vectorized).
`%||%` <- function(a, b) {
  if (is.null(a) || length(a) == 0L) return(b)
  if (length(a) == 1L && !is.list(a)) {
    if (is.na(a) || identical(a, "")) return(b)
  }
  a
}


#' Load the Phase-1 SuSiE policy YAML.
#'
#' The file schema matches config/susie_policy.yaml:
#'   susie:
#'     L: int
#'     coverage: float
#'     max_iter_primary: int
#'     max_iter_retry: int
#'     ld_regularization_eps: float
#'     min_abs_corr_default: float
#'
#' @param path character path to policy YAML
#' @return list with keys L, coverage, max_iter_primary, max_iter_retry,
#'         ld_regularization_eps, min_abs_corr
load_policy <- function(path) {
  raw <- yaml::read_yaml(path)
  susie_cfg <- raw$susie %||% list()
  list(
    L = susie_cfg$L %||% 10L,
    coverage = susie_cfg$coverage %||% 0.95,
    max_iter_primary = susie_cfg$max_iter_primary %||% 100L,
    max_iter_retry = susie_cfg$max_iter_retry %||% 200L,
    ld_regularization_eps = susie_cfg$ld_regularization_eps %||% 1e-4,
    min_abs_corr = susie_cfg$min_abs_corr_default %||% 0.5
  )
}


#' Resolve an LD panel key to an on-disk RDS path.
#'
#' Keys come from config/replication_cohorts.yaml::ld_panels:
#'   ukbb_ld         -> Phase-1 Plan 01-02 output
#'   hgdp_1kg_afr    -> Phase-1 Plan 01-03 output
#'   thousand_g_eas  -> NEW Phase-9 1000G EAS panel (deferred; placeholder path)
#'
#' Resolution honors the same `{region}.rds` convention as Phase 1.
#'
#' @param ld_panel character key
#' @param region character "chr:start-end" string
ld_panel_path <- function(ld_panel, region) {
  # Region-safe ID: replace ':' and '-' with '_'
  safe_region <- gsub("[^A-Za-z0-9_]", "_", region)
  base <- switch(
    ld_panel,
    ukbb_ld = "data/processed/ld_reference/ukbb_ld",
    hgdp_1kg_afr = "data/processed/ld_reference/hgdp_1kg_afr",
    thousand_g_eas = "data/processed/ld_reference/thousand_g_eas",
    stop(sprintf("unknown ld_panel: %s", ld_panel))
  )
  file.path(base, sprintf("%s.rds", safe_region))
}


#' Parse a "chr:start-end" region string into an integer chrom and bounds.
parse_region <- function(region) {
  # Accept either "10:100-200", "chr10:100-200", or "10:100:200"
  r <- gsub("^chr", "", region)
  parts <- strsplit(r, "[:\\-]")[[1]]
  if (length(parts) < 3L) {
    stop(sprintf("region '%s' not in chr:start-end format", region))
  }
  list(
    chrom = as.integer(parts[1]),
    start = as.integer(parts[2]),
    end = as.integer(parts[3])
  )
}


#' Fit SuSiE-RSS on a replication-cohort sumstats region.
#'
#' Reuses the Phase-1 runsusie invocation pattern (suffix=2 so the fit
#' object is coloc.susie-ready). Wrapped in a two-stage retry ladder:
#' primary call with policy defaults; on error, retry with lowered
#' `min_abs_corr = 0.1`.
#'
#' @param sumstats_tsv path to canonical harmonized sumstats (gz ok)
#' @param region       character "chr:start-end" (GRCh37)
#' @param ld_rds       path to per-region LD matrix RDS
#' @param output_rds   path to write the fit object
#' @param trait_type   "cc" or "quant"
#' @param case_n,ctrl_n,total_n scalar numerics
#' @param policy_path  path to config/susie_policy.yaml
fit_replication_susie <- function(
  sumstats_tsv,
  region,
  ld_rds,
  output_rds,
  trait_type = c("cc", "quant"),
  case_n = NULL,
  ctrl_n = NULL,
  total_n = NULL,
  policy_path = "config/susie_policy.yaml"
) {
  trait_type <- match.arg(trait_type)
  policy <- load_policy(policy_path)

  reg <- parse_region(region)
  sumstats <- data.table::fread(sumstats_tsv)
  # Normalize column case — canonical harmonized schema uses upper-case.
  data.table::setnames(sumstats, toupper(names(sumstats)))

  # Range-filter to the region
  sumstats <- sumstats[
    CHR == reg$chrom & BP >= reg$start & BP <= reg$end
  ]
  if (nrow(sumstats) < 50L) {
    stop(sprintf(
      "region %s has only %d SNPs after filter (need >= 50)",
      region,
      nrow(sumstats)
    ))
  }

  # Load per-region LD and align by SNP
  ld <- readRDS(ld_rds)
  ld_snps <- rownames(ld)
  if (is.null(ld_snps)) {
    stop(sprintf("LD RDS at %s has no rownames (SNP IDs)", ld_rds))
  }
  common <- intersect(sumstats$SNP, ld_snps)
  if (length(common) < 50L) {
    stop(sprintf(
      "only %d SNPs intersect sumstats and LD panel (need >= 50)",
      length(common)
    ))
  }
  sumstats <- sumstats[SNP %in% common]
  # Re-order sumstats to match ld alignment
  sumstats <- sumstats[match(common, sumstats$SNP)]
  ld_sub <- ld[common, common]

  # Effective sample size
  n_eff <- total_n %||% as.integer(stats::median(sumstats$N, na.rm = TRUE))

  D <- list(
    beta = sumstats$BETA,
    varbeta = sumstats$SE^2,
    snp = sumstats$SNP,
    position = sumstats$BP,
    type = if (trait_type == "cc") "cc" else "quant",
    LD = ld_sub,
    N = n_eff,
    MAF = pmin(sumstats$EAF, 1 - sumstats$EAF)
  )
  if (trait_type == "cc") {
    if (is.null(case_n) || is.null(ctrl_n) || case_n == 0 || ctrl_n == 0) {
      stop("trait_type='cc' requires positive case_n and ctrl_n")
    }
    D$s <- case_n / (case_n + ctrl_n)
  }

  # Retry ladder: primary runsusie; on error, retry with min_abs_corr=0.1
  fit <- tryCatch(
    coloc::runsusie(
      D,
      suffix = 2L,
      L = policy$L,
      coverage = policy$coverage,
      min_abs_corr = policy$min_abs_corr
    ),
    error = function(e) {
      message(sprintf(
        "primary runsusie failed (%s) — retrying with min_abs_corr=0.1",
        conditionMessage(e)
      ))
      coloc::runsusie(
        D,
        suffix = 2L,
        L = policy$L,
        coverage = policy$coverage,
        min_abs_corr = 0.1
      )
    }
  )
  dir.create(dirname(output_rds), recursive = TRUE, showWarnings = FALSE)
  saveRDS(fit, output_rds)
  invisible(fit)
}


# ---- CLI entrypoint -----------------------------------------------------
if (!interactive() && sys.nframe() == 0L) {
  raw_args <- commandArgs(trailingOnly = TRUE)
  # key=value parsing
  split_kv <- strsplit(raw_args, "=", fixed = TRUE)
  nm <- setNames(
    vapply(split_kv, function(x) paste(x[-1], collapse = "="), character(1)),
    vapply(split_kv, `[`, character(1), 1)
  )

  required <- c("sumstats", "region", "out", "policy", "ld_panel")
  missing_args <- setdiff(required, names(nm))
  if (length(missing_args) > 0) {
    stop(sprintf(
      "missing required CLI args: %s",
      paste(missing_args, collapse = ", ")
    ))
  }

  ld_rds <- ld_panel_path(nm[["ld_panel"]], nm[["region"]])

  fit_replication_susie(
    sumstats_tsv = nm[["sumstats"]],
    region       = nm[["region"]],
    ld_rds       = ld_rds,
    output_rds   = nm[["out"]],
    trait_type   = nm[["type"]] %||% "cc",
    case_n       = suppressWarnings(as.integer(nm[["case_n"]] %||% NA)),
    ctrl_n       = suppressWarnings(as.integer(nm[["ctrl_n"]] %||% NA)),
    total_n      = suppressWarnings(as.integer(nm[["n"]] %||% NA)),
    policy_path  = nm[["policy"]]
  )
}
