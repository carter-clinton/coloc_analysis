#!/usr/bin/env Rscript
# src/R/regularization/refit_sh2b3_psd_regularized.R
# ta-r3 W1: PSD-regularized SuSiE-RSS re-fit per OSF amendment osf-amendment-r3-2026-05-04.md
# Implements: Wen 2017 ridge (R_reg = R + lambda*I + row-col normalize) AND
#             Hutchinson 2020 eigenvalue-clip alternative (clip negatives to lambda_floor=1e-6).
# Reused from src/legacy/region_analysis/scripts/run_susie_rss.R: z = BETA / SE inline derivation pattern.
# SuSiE-RSS call: susieR::susie_rss(z, R_reg, n, L=10, coverage=0.95, max_iter=1000,
#                                    estimate_residual_variance=FALSE, check_R=FALSE).
#
# CLI:
#   Rscript refit_sh2b3_psd_regularized.R \
#     --trait <asthma|bmi|hypertension|stroke|t2d> \
#     --lambda <numeric>                                # ridge lambda or eigclip floor
#     --method <ridge|eigclip>                          # default ridge (Wen 2017)
#     [--region <SH2B3_12q24>]                          # default SH2B3_12q24
#     [--ancestry <EUR>]                                # default EUR
#     [--ld_path <data/processed/ld_reference/EUR/SH2B3_12q24.rds>]
#     [--sumstats_dir <data/processed/sumstats_harmonized>]
#     --out <results/fine_mapping_psd_regularized/<trait>.<ancestry>.<region>.lambda<lambda>.fit.rds>
#
# Output RDS is a list with fields: trait, region, ancestry, lambda, lambda_method,
# L_used, niter, n_CS, converged, n, n_snps, dropped_snps_count, residual_variance,
# wall_sec, susie_fit (full susie object).

suppressPackageStartupMessages({
  library(optparse)
  library(susieR)
  library(data.table)
})

# -------------------------------------------------------------------------
# null-coalesce helper (avoid rlang dependency; %||% not in base R)
`%||%` <- function(a, b) if (is.null(a) || length(a) == 0L) b else a

# -------------------------------------------------------------------------
# chr:pos <-> rsid bridge for variant-ID convention drift between harmonized
# sumstats and per-region 1KG-EUR LD reference panels (introduced by
# ta-r3 W1 2026-05-06; same class of bug previously fixed in commits
# 069b34f + 7d54183 for the run_qtl_coloc.R / run_susie_rss.R paths).
# Locates the utility relative to this script so the fitter is invocable from
# any cwd (LSF jobs run with cwd=project root, but unit tests source from a
# different cwd).
.bridge_path <- file.path(dirname(sub("^--file=", "",
  grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)[1])),
  "snp_id_bridge.R")
if (!file.exists(.bridge_path)) {
  # Fallback to project-relative path when sourced via R -e.
  .bridge_path <- "src/R/regularization/snp_id_bridge.R"
}
stopifnot(file.exists(.bridge_path))
source(.bridge_path)
stopifnot(exists("bridge_snp_id_to_ld_ref", mode = "function"))

opt <- OptionParser(option_list = list(
  make_option("--trait", type = "character", help = "asthma|bmi|hypertension|stroke|t2d"),
  make_option("--lambda", type = "numeric", help = "ridge lambda or eigclip floor"),
  make_option("--method", type = "character", default = "ridge",
              help = "ridge (Wen 2017) or eigclip (Hutchinson 2020) [default ridge]"),
  make_option("--region", type = "character", default = "SH2B3_12q24"),
  make_option("--ancestry", type = "character", default = "EUR"),
  make_option("--ld_path", type = "character",
              default = "data/processed/ld_reference/EUR/SH2B3_12q24.rds"),
  make_option("--sumstats_dir", type = "character",
              default = "data/processed/sumstats_harmonized"),
  make_option("--out", type = "character", help = "output .fit.rds path")
)) |> parse_args()

# -------------------------------------------------------------------------
# PSD regularization functions
# Wen 2017 ridge: R_reg = R + lambda * I; then row-and-column normalize so diag(R_reg) = 1
psd_regularize_ridge <- function(R, lambda) {
  R_reg <- R + lambda * diag(nrow(R))
  d <- sqrt(diag(R_reg))
  R_reg <- sweep(sweep(R_reg, 1, d, "/"), 2, d, "/")
  R_reg
}

# Hutchinson 2020 eigenvalue-clip: clip negative eigenvalues to lambda_floor (default 1e-6),
# reconstruct R_clip = V * diag(max(d, lambda_floor)) * V^T, then row-col normalize.
psd_regularize_eigclip <- function(R, lambda_floor = 1e-6) {
  e <- eigen(R, symmetric = TRUE)
  d_clip <- pmax(e$values, lambda_floor)
  R_clip <- e$vectors %*% diag(d_clip) %*% t(e$vectors)
  d <- sqrt(diag(R_clip))
  R_clip <- sweep(sweep(R_clip, 1, d, "/"), 2, d, "/")
  R_clip
}

# -------------------------------------------------------------------------
# Load LD
# Project schema (verified 2026-05-05 against data/processed/ld_reference/EUR/SH2B3_12q24.rds):
# Top-level object is a list with fields:
#   - R         : numeric matrix (n_variants x n_variants); LD R^2-style PSD-imperfect matrix
#   - variants  : data.frame with columns SNP_ID, CHR, POS, A1, A2 (positional row-index aligns with R)
#   - ld_source : char e.g. "onekg_phase3_eur_hm3"
#   - region_id : char e.g. "SH2B3_12q24"
#   - ancestry  : char e.g. "EUR"
# The matrix has NO row/column names; SNP-id alignment is positional via variants$SNP_ID.
ld <- readRDS(opt$ld_path)
stopifnot(is.list(ld), !is.null(ld$R), !is.null(ld$variants))
R <- ld$R
ld_variants <- ld$variants
stopifnot(is.matrix(R), isSymmetric(R, tol = 1e-6),
          nrow(R) == nrow(ld_variants), "SNP_ID" %in% names(ld_variants))
# Attach rownames/colnames from variants$SNP_ID for downstream subsetting.
rownames(R) <- ld_variants$SNP_ID
colnames(R) <- ld_variants$SNP_ID

# -------------------------------------------------------------------------
# Load harmonized sumstats; subset to LD overlap.
# Project schema (verified 2026-05-05 against data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz):
# Columns: CHR, POS, BETA, SE, P, N, SNP_ID, TRAIT, ANCESTRY, BUILD
sumstats_path <- file.path(opt$sumstats_dir,
                           sprintf("%s.%s.tsv.bgz", opt$trait, opt$ancestry))
stopifnot(file.exists(sumstats_path))
ss <- fread(cmd = sprintf("zcat %s", sumstats_path))

# SH2B3 12q24 region anchor: chr12 cytoband 12q24.12 (~111-113 Mb GRCh37 boundary).
chr_anchor <- 12L
pos_lo <- 111e6L; pos_hi <- 113e6L
chrcol <- intersect(c("CHR", "chr", "Chr", "chromosome"), names(ss))[1]
poscol <- intersect(c("POS", "pos", "Pos", "BP", "position"), names(ss))[1]
betacol <- intersect(c("BETA", "beta", "Effect"), names(ss))[1]
secol  <- intersect(c("SE", "se", "StdErr"), names(ss))[1]
ncol_  <- intersect(c("N", "n_total", "Nsamples"), names(ss))[1]

if (is.null(ncol_) || is.na(ncol_)) {
  # Per harmonized-sumstats convention; if absent, infer from neff or set fallback per trait.
  n_eff <- 350000L
} else {
  n_eff <- as.integer(median(ss[[ncol_]], na.rm = TRUE))
}

sub <- ss[get(chrcol) == chr_anchor & get(poscol) >= pos_lo & get(poscol) <= pos_hi]
sub[, z := get(betacol) / get(secol)]   # mirror src/legacy/region_analysis/scripts/run_susie_rss.R:466

# Match LD SNP_IDs -> sumstats SNP_ID. The harmonized sumstats schema uses SNP_ID;
# the LD variants$SNP_ID is the canonical join key.
snpcol <- intersect(c("SNP_ID", "SNP", "MarkerName", "rsid", "ID"), names(sub))[1]
stopifnot(!is.na(snpcol))

# Bridge chr:pos<->rsid convention drift: harmonized sumstats use rsid for
# asthma/bmi but chr:pos for hypertension/stroke/t2d, while ld$variants$SNP_ID
# is 100% rsid. Without this bridge, intersect() returns 0 for chr:pos sumstats
# and stopifnot below fires. See .planning/debug/ta_r3_w1_snp_id_overlap_zero.md
# and tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R.
sub <- bridge_snp_id_to_ld_ref(
  sumstats      = sub,
  ld_variants   = ld_variants,
  chr_col       = chrcol,
  pos_col       = poscol,
  snp_id_col    = snpcol,
  ld_chr_col    = "CHR",
  ld_pos_col    = "POS",
  ld_snp_id_col = "SNP_ID"
)

overlap <- intersect(rownames(R), sub[[snpcol]])
stopifnot(length(overlap) > 0)
n_dropped <- nrow(sub) - length(overlap)
sub <- sub[get(snpcol) %in% overlap]
setkeyv(sub, snpcol)
sub <- sub[overlap]   # reorder to match R rownames
R_sub <- R[overlap, overlap]
z <- sub$z

# -------------------------------------------------------------------------
# Regularize
R_reg <- if (opt$method == "ridge") {
  psd_regularize_ridge(R_sub, opt$lambda)
} else if (opt$method == "eigclip") {
  psd_regularize_eigclip(R_sub, opt$lambda)
} else {
  stop(sprintf("Unknown method: %s", opt$method))
}

# -------------------------------------------------------------------------
# Fit susie_rss
t0 <- Sys.time()
fit <- susieR::susie_rss(
  z = z, R = R_reg, n = n_eff,
  L = 10, coverage = 0.95, max_iter = 1000,
  estimate_residual_variance = FALSE, check_R = FALSE
)
wall_sec <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

converged <- isTRUE(fit$converged)
n_CS <- if (!is.null(fit$sets$cs)) length(fit$sets$cs) else 0L

out_list <- list(
  trait = opt$trait, region = opt$region, ancestry = opt$ancestry,
  lambda = opt$lambda, lambda_method = opt$method,
  L_used = 10L, niter = fit$niter %||% NA_integer_,
  n_CS = n_CS, converged = converged,
  n = n_eff, n_snps = length(z), dropped_snps_count = n_dropped,
  residual_variance = fit$sigma2 %||% NA_real_,
  wall_sec = wall_sec, susie_fit = fit
)
dir.create(dirname(opt$out), recursive = TRUE, showWarnings = FALSE)
saveRDS(out_list, opt$out)
cat(sprintf("WROTE %s; converged=%s; n_CS=%d; niter=%s; lambda=%s; method=%s; wall=%.1fs\n",
            opt$out, converged, n_CS,
            as.character(out_list$niter), opt$lambda, opt$method, wall_sec))
