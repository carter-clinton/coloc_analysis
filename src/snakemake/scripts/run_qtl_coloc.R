#!/usr/bin/env Rscript
# ==========================================================================
# Phase 2 -- unified GWAS-vs-QTL coloc.susie runner.
#
# Accepts a pre-fitted GWAS .fit.rds (from Phase 1 run_susie_rss.R) on the
# GWAS side, and a harmonized QTL sumstats TSV on the QTL side. Fits
# SuSiE-RSS on the QTL data and calls coloc.susie(gwas_fit, qtl_fit).
#
# All QTL sources (eQTL, sQTL, pQTL, sc-eQTL) produce the same harmonized
# TSV intermediate format, so this script is source-agnostic.
#
# T-02-07 mitigation: check_dataset() validates QTL data before SuSiE;
#   skip if n_snps_overlap < 50.
# ==========================================================================

suppressPackageStartupMessages({
  library(optparse)
  library(coloc)
  library(susieR)
  library(jsonlite)
  library(data.table)
})

`%||%` <- function(x, y) if (!is.null(x)) x else y

# -------------------------------------------------------------------------
# CLI argument parsing
# -------------------------------------------------------------------------
option_list <- list(
  make_option("--gwas-fit",      dest = "gwas_fit",      type = "character",
              help = "Path to Phase 1 .fit.rds (SuSiE object with class 'susie')"),
  make_option("--qtl-sumstats",  dest = "qtl_sumstats",  type = "character",
              help = "Path to harmonized QTL TSV (output of harmonize_*.py)"),
  make_option("--ld-matrix",     dest = "ld_matrix",     type = "character",
              help = "Path to LD .rds matrix (from Phase 1 ld_reference pipeline)"),
  make_option("--qtl-source",    dest = "qtl_source",    type = "character",
              help = "Source identifier: gtex_eqtl, gtex_sqtl, ukbppp_pqtl, onek1k_sceqtl"),
  make_option("--tissue",        type = "character",
              help = "Tissue or cell type name"),
  make_option("--gene-id",       dest = "gene_id",       type = "character",
              help = "Ensembl gene ID"),
  make_option("--region",        type = "character",
              help = "Region ID from regions_curated"),
  make_option("--ancestry",      type = "character",
              help = "Ancestry code (EUR, AFR, etc.)"),
  make_option("--sdy",           type = "double",   default = 1.0,
              help = "Numeric sdY value for QTL data (1.0 for GTEx/OneK1K; estimated for pQTL)"),
  make_option("--sample-size",   dest = "sample_size",   type = "integer",
              help = "Integer N for QTL dataset"),
  make_option("--policy",        type = "character", default = "config/susie_policy.yaml",
              help = "Path to config/susie_policy.yaml"),
  make_option("--output",        type = "character",
              help = "Output JSON path")
)
opt <- parse_args(OptionParser(option_list = option_list))

# Validate required arguments
required_args <- c("gwas_fit", "qtl_sumstats", "ld_matrix", "output")
for (arg_name in required_args) {
  if (is.null(opt[[arg_name]])) {
    stop(paste0("--", gsub("_", "-", arg_name), " is required"), call. = FALSE)
  }
}

# Validate file existence
stopifnot(file.exists(opt$gwas_fit))
stopifnot(file.exists(opt$qtl_sumstats))
stopifnot(file.exists(opt$ld_matrix))

# -------------------------------------------------------------------------
# Helper: write status JSON and exit cleanly
# -------------------------------------------------------------------------
write_status_json <- function(status_code, message = NULL) {
  result <- list(
    status        = status_code,
    message       = message %||% status_code,
    qtl_source    = opt$qtl_source %||% NA_character_,
    tissue        = opt$tissue %||% NA_character_,
    gene_id       = opt$gene_id %||% NA_character_,
    region        = opt$region %||% NA_character_,
    ancestry      = opt$ancestry %||% NA_character_,
    n_snps_overlap = 0L,
    qtl_n         = opt$sample_size %||% NA_integer_,
    qtl_sdy       = opt$sdy %||% NA_real_,
    summary       = list(),
    all_pairs     = list(),
    n_cs_gwas     = NA_integer_,
    n_cs_qtl      = NA_integer_
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(result, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
  cat(sprintf("[run_qtl_coloc] %s for %s/%s/%s -- wrote %s\n",
              status_code, opt$gene_id %||% "?", opt$tissue %||% "?",
              opt$region %||% "?", opt$output))
}

# -------------------------------------------------------------------------
# 1. Load GWAS fit
# -------------------------------------------------------------------------
gwas_fit <- readRDS(opt$gwas_fit)
if (!inherits(gwas_fit, "susie")) {
  class(gwas_fit) <- c("susie", class(gwas_fit))
}

# -------------------------------------------------------------------------
# 2. Read QTL sumstats
# -------------------------------------------------------------------------
qtl_df <- fread(opt$qtl_sumstats)
if (nrow(qtl_df) == 0) {
  write_status_json("too_few_snps", "QTL sumstats file is empty")
  quit(status = 0)
}

# Ensure numeric types
qtl_df[, beta := as.numeric(beta)]
qtl_df[, se   := as.numeric(se)]
qtl_df[, maf  := as.numeric(maf)]
qtl_df[, position := as.integer(position)]

# -------------------------------------------------------------------------
# 3. Match SNPs between GWAS fit and QTL data
# -------------------------------------------------------------------------
# qtl_coloc_snp_name_mismatch bugfix (2026-04-20):
# GWAS SuSiE fits from run_susie_rss.R carry rsid names (sourced from
# sumstats SNP_ID column) on $alpha colnames and $pip names, because Phase 1
# sumstats are GRCh37 but harmonized QTL TSVs are GRCh38. Direct coord
# matching would fail across builds. The harmonized TSV carries a parallel
# `rsid` column populated for >99% of variants, so rsid is the build-
# invariant common key between Phase 1 fit and Phase 2 QTL data.
gwas_snps <- NULL
if (!is.null(gwas_fit$alpha) && !is.null(colnames(gwas_fit$alpha))) {
  gwas_snps <- colnames(gwas_fit$alpha)
} else if (!is.null(names(gwas_fit$pip))) {
  gwas_snps <- names(gwas_fit$pip)
}

if (is.null(gwas_snps)) {
  write_status_json("too_few_snps", "Cannot extract SNP names from GWAS fit")
  quit(status = 0)
}

# Drop the sentinel "null" column (coloc::annotate_susie appends one when the
# fit has fewer credible sets than L; it is not a real variant).
gwas_snps <- gwas_snps[gwas_snps != "null"]

# Match by best-overlap key across rsid / chr:pos / variant_id. Phase 1
# SuSiE fits can carry either rsids (bmi.*, asthma.* sumstats) or chr:pos
# strings (hypertension.*, stroke.*, t2d.* sumstats) on colnames(fit$alpha),
# depending on the SNP_ID convention of each harmonized sumstats file. The
# QTL harmonized TSV carries `rsid` and `variant_id` (chr_pos_ref_alt).
# Derive chr:pos from variant_id so we can match chr:pos-formatted fits that
# would otherwise silently 0-overlap against rsid-only QTL keys (root cause
# of the all-zero-overlap SH2B3_12q24 QTL coloc runs surfaced 2026-04-21
# during Stage 3 Option C; same class as the trait-pair bug fixed in 335f514).
# variant_id format: "chr12_110962202_G_A" -> chrpos "12:110962202"
qtl_df$chrpos <- local({
  parts <- strsplit(as.character(qtl_df$variant_id), "_", fixed = TRUE)
  chrom <- sub("^chr", "", sapply(parts, `[`, 1))
  pos   <- sapply(parts, `[`, 2)
  paste0(chrom, ":", pos)
})

candidates <- list()
if ("rsid" %in% names(qtl_df) &&
    any(!is.na(qtl_df$rsid) & qtl_df$rsid != "" & qtl_df$rsid != "NA")) {
  candidates[["rsid"]] <- qtl_df$rsid
}
candidates[["chrpos"]]     <- qtl_df$chrpos
candidates[["variant_id"]] <- qtl_df$variant_id

overlaps <- sapply(candidates, function(v) length(intersect(gwas_snps, v)))
cat(sprintf("[run_qtl_coloc] candidate overlaps: %s\n",
            paste(sprintf("%s=%d", names(overlaps), overlaps), collapse = ", ")))
match_key      <- names(which.max(overlaps))
qtl_snps       <- candidates[[match_key]]
overlap_snps   <- intersect(gwas_snps, qtl_snps)
n_snps_overlap <- length(overlap_snps)

cat(sprintf("[run_qtl_coloc] match_key=%s, GWAS snps: %d, QTL snps: %d, overlap: %d\n",
            match_key, length(gwas_snps), length(qtl_snps), n_snps_overlap))

# T-02-07: skip if too few overlapping SNPs
if (n_snps_overlap < 50) {
  write_status_json("too_few_snps",
                    sprintf("Only %d overlapping SNPs (need >= 50)", n_snps_overlap))
  quit(status = 0)
}

# -------------------------------------------------------------------------
# 4. Load LD matrix and subset to matching SNPs
# -------------------------------------------------------------------------
# qtl_coloc_snp_name_mismatch bugfix (2026-04-20):
# The LD .rds produced by the Phase 1 ld_reference pipeline is a LIST with
# components {R, variants, use_identity, status}. When the region's variant
# count exceeds LD_MAX_VARIANTS (default 6000), R is NULL and use_identity
# is TRUE. Previously this code assumed a bare matrix and would fail at
# rownames(ld_full) == NULL. Handle all three forms:
#   (a) list with R matrix and variants -> use obj$R with rsid rownames
#       (sourced from obj$variants$SNP_ID when available).
#   (b) list with use_identity=TRUE or R=NULL -> construct named identity
#       matrix over overlap_snps; coloc::runsusie will still run (LD is
#       the identity so SuSiE treats variants as independent).
#   (c) bare matrix (legacy / future) -> use directly, require dimnames.
ld_obj <- readRDS(opt$ld_matrix)

build_ld_rownames <- function(obj) {
  # Derive rsid-keyed names from the variants dataframe when available.
  if (!is.list(obj) || is.null(obj$variants) || !is.data.frame(obj$variants)) {
    return(NULL)
  }
  v <- obj$variants
  if ("SNP_ID" %in% names(v) && any(!is.na(v$SNP_ID) & v$SNP_ID != "" & v$SNP_ID != "NA")) {
    return(as.character(v$SNP_ID))
  }
  if (all(c("CHR", "POS") %in% names(v))) {
    return(sprintf("%s:%s", v$CHR, v$POS))
  }
  NULL
}

if (is.list(ld_obj) && !is.matrix(ld_obj)) {
  use_identity <- isTRUE(ld_obj$use_identity) || is.null(ld_obj$R)
  if (use_identity) {
    # Identity fallback: build a named identity over overlap_snps.
    ld_matrix_subset <- diag(length(overlap_snps))
    dimnames(ld_matrix_subset) <- list(overlap_snps, overlap_snps)
    ld_snp_names <- overlap_snps  # trivially matches overlap
    cat(sprintf("[run_qtl_coloc] LD .rds has use_identity=TRUE (status=%s); using identity matrix\n",
                ld_obj$status %||% "unknown"))
  } else {
    ld_full <- ld_obj$R
    ld_snp_names <- rownames(ld_full) %||% colnames(ld_full) %||% build_ld_rownames(ld_obj)
    if (is.null(ld_snp_names)) {
      write_status_json("too_few_snps", "LD matrix has no row/col names and no variants metadata")
      quit(status = 0)
    }
    if (is.null(rownames(ld_full)) || is.null(colnames(ld_full))) {
      # Attach rsid dimnames from obj$variants (parallel-ordered).
      if (length(ld_snp_names) != nrow(ld_full)) {
        write_status_json("too_few_snps",
                          sprintf("LD rownames length %d != nrow %d",
                                  length(ld_snp_names), nrow(ld_full)))
        quit(status = 0)
      }
      dimnames(ld_full) <- list(ld_snp_names, ld_snp_names)
    }
  }
} else if (is.matrix(ld_obj) || inherits(ld_obj, "Matrix")) {
  ld_full <- as.matrix(ld_obj)
  ld_snp_names <- rownames(ld_full) %||% colnames(ld_full)
  if (is.null(ld_snp_names)) {
    write_status_json("too_few_snps", "LD matrix has no row/col names")
    quit(status = 0)
  }
} else {
  write_status_json("too_few_snps",
                    sprintf("LD .rds has unexpected class: %s",
                            paste(class(ld_obj), collapse = "/")))
  quit(status = 0)
}

# Final overlap must include the LD matrix's named variants (unless identity
# fallback, in which case we already built LD over overlap_snps).
if (!exists("use_identity") || !isTRUE(use_identity)) {
  overlap_snps <- intersect(overlap_snps, ld_snp_names)
  n_snps_overlap <- length(overlap_snps)
  if (n_snps_overlap < 50) {
    write_status_json("too_few_snps",
                      sprintf("Only %d SNPs after LD intersection (need >= 50)", n_snps_overlap))
    quit(status = 0)
  }
  ld_matrix_subset <- ld_full[overlap_snps, overlap_snps, drop = FALSE]
}

# Subset QTL data to overlap SNPs (in same order as LD matrix rows).
qtl_df <- qtl_df[match(overlap_snps, qtl_df[[match_key]]), ]

# -------------------------------------------------------------------------
# 5. Build QTL dataset list for coloc
# -------------------------------------------------------------------------
qtl_data <- list(
  beta     = qtl_df$beta,
  varbeta  = qtl_df$se^2,
  snp      = overlap_snps,
  position = qtl_df$position,
  type     = "quant",
  N        = as.integer(opt$sample_size),
  sdY      = as.numeric(opt$sdy),
  MAF      = qtl_df$maf,
  LD       = ld_matrix_subset
)

# -------------------------------------------------------------------------
# 6. Validate QTL dataset (T-02-07 mitigation)
# -------------------------------------------------------------------------
tryCatch({
  coloc::check_dataset(qtl_data, req = "LD")
}, error = function(e) {
  write_status_json("qtl_dataset_invalid", conditionMessage(e))
  quit(status = 0)
})

# -------------------------------------------------------------------------
# 7. Fit SuSiE on QTL side
# -------------------------------------------------------------------------
qtl_fit <- tryCatch({
  coloc::runsusie(qtl_data, suffix = 2)
}, error = function(e) {
  cat(sprintf("[run_qtl_coloc] runsusie failed: %s, retrying with max_iter=200\n",
              conditionMessage(e)))
  tryCatch({
    coloc::runsusie(qtl_data, suffix = 2, maxit = 200)
  }, error = function(e2) {
    NULL
  })
})

if (is.null(qtl_fit)) {
  write_status_json("qtl_susie_failed", "runsusie() failed after retry with max_iter=200")
  quit(status = 0)
}

# -------------------------------------------------------------------------
# 8. Check for credible sets on QTL side
# -------------------------------------------------------------------------
cs_qtl <- qtl_fit$sets$cs %||% list()
n_cs_qtl <- length(cs_qtl)
cs_gwas <- gwas_fit$sets$cs %||% list()
n_cs_gwas <- length(cs_gwas)

if (n_cs_qtl == 0) {
  result <- list(
    status        = "no_qtl_cs",
    message       = "No credible sets on QTL side",
    qtl_source    = opt$qtl_source %||% NA_character_,
    tissue        = opt$tissue %||% NA_character_,
    gene_id       = opt$gene_id %||% NA_character_,
    region        = opt$region %||% NA_character_,
    ancestry      = opt$ancestry %||% NA_character_,
    n_snps_overlap = n_snps_overlap,
    qtl_n         = opt$sample_size %||% NA_integer_,
    qtl_sdy       = opt$sdy %||% NA_real_,
    summary       = list(),
    all_pairs     = list(),
    n_cs_gwas     = n_cs_gwas,
    n_cs_qtl      = 0L
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(result, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
  cat(sprintf("[run_qtl_coloc] no_qtl_cs for %s/%s -- wrote %s\n",
              opt$gene_id %||% "?", opt$tissue %||% "?", opt$output))
  quit(status = 0)
}

if (n_cs_gwas == 0) {
  result <- list(
    status        = "no_gwas_cs",
    message       = "No credible sets on GWAS side",
    qtl_source    = opt$qtl_source %||% NA_character_,
    tissue        = opt$tissue %||% NA_character_,
    gene_id       = opt$gene_id %||% NA_character_,
    region        = opt$region %||% NA_character_,
    ancestry      = opt$ancestry %||% NA_character_,
    n_snps_overlap = n_snps_overlap,
    qtl_n         = opt$sample_size %||% NA_integer_,
    qtl_sdy       = opt$sdy %||% NA_real_,
    summary       = list(),
    all_pairs     = list(),
    n_cs_gwas     = 0L,
    n_cs_qtl      = n_cs_qtl
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(result, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
  cat(sprintf("[run_qtl_coloc] no_gwas_cs for %s/%s -- wrote %s\n",
              opt$gene_id %||% "?", opt$tissue %||% "?", opt$output))
  quit(status = 0)
}

# -------------------------------------------------------------------------
# 9. Run coloc.susie
# -------------------------------------------------------------------------
res <- coloc::coloc.susie(gwas_fit, qtl_fit)
summary_dt <- as.data.table(res$summary)

# -------------------------------------------------------------------------
# Posterior sum sanity check (same pattern as Phase 1 run_coloc_susie.R)
# -------------------------------------------------------------------------
pp_cols <- c("PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf")
if (all(pp_cols %in% names(summary_dt)) && nrow(summary_dt) > 0) {
  row_sums <- rowSums(summary_dt[, ..pp_cols])
  max_dev <- max(abs(row_sums - 1.0), na.rm = TRUE)
  if (is.finite(max_dev) && max_dev > 1e-4) {
    warning(sprintf(
      "[run_qtl_coloc] posterior sum deviation %.2e > 1e-4 in %d rows",
      max_dev, sum(abs(row_sums - 1.0) > 1e-4, na.rm = TRUE)))
  }
}

# -------------------------------------------------------------------------
# 10. Build output: best pairwise row + all pairs
# -------------------------------------------------------------------------
if (nrow(summary_dt) > 0 && "PP.H4.abf" %in% names(summary_dt)) {
  best_idx <- which.max(summary_dt$PP.H4.abf)
  best_row <- if (length(best_idx) == 1) as.list(summary_dt[best_idx]) else list()
} else {
  best_row <- list()
}

output <- list(
  status         = "success",
  qtl_source     = opt$qtl_source %||% NA_character_,
  tissue         = opt$tissue %||% NA_character_,
  gene_id        = opt$gene_id %||% NA_character_,
  region         = opt$region %||% NA_character_,
  ancestry       = opt$ancestry %||% NA_character_,
  n_snps_overlap = n_snps_overlap,
  qtl_n          = opt$sample_size %||% NA_integer_,
  qtl_sdy        = opt$sdy %||% NA_real_,
  summary        = best_row,
  all_pairs      = lapply(seq_len(nrow(summary_dt)),
                          function(i) as.list(summary_dt[i])),
  n_cs_gwas      = n_cs_gwas,
  n_cs_qtl       = n_cs_qtl
)

# -------------------------------------------------------------------------
# 11. Write output JSON
# -------------------------------------------------------------------------
dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
write_json(output, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
cat(sprintf("[run_qtl_coloc] wrote %s with %d pairwise rows (n_cs_gwas=%d, n_cs_qtl=%d)\n",
            opt$output, nrow(summary_dt), n_cs_gwas, n_cs_qtl))
