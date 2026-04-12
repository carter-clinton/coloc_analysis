#!/usr/bin/env Rscript
# plink_ld_to_rds.R -- convert plink2 LD text output to the .rds shape
# consumed by run_susie_rss.R::load_ld_matrix.
#
# Plan 01-03 Task 1-03-02 helper. Called by build_hgdp_1kg_ld.py after
# plink2 --r-phased / --r2-phased / --r2 produces a square-matrix LD
# file. plink2 CLI varies by version; the caller passes the concrete
# paths via --ld and --variants so this script does not have to guess.
#
# Output shape (matches run_susie_rss.R load_ld_matrix expectation):
#   list(
#     R         = <numeric symmetric matrix>,
#     variants  = data.frame(SNP_ID, CHR, POS, A1, A2),
#     ld_source = "hgdp_1kg_v3_1_2",
#     region_id = <string>,
#     ancestry  = "AFR"
#   )
#
# T-1-02b mitigation: strict numeric typing via data.table::fread; NA
# rows rejected before writing. No shell interpolation of plink-produced
# strings -- all values are read as structured columns.

suppressPackageStartupMessages({
  if (!requireNamespace("optparse", quietly = TRUE)) {
    # Minimal fallback if optparse isn't in the conda env.
    parse_cli <- function(argv) {
      out <- list()
      i <- 1
      while (i <= length(argv)) {
        key <- sub("^--", "", argv[[i]])
        key <- gsub("-", "_", key)
        out[[key]] <- argv[[i + 1]]
        i <- i + 2
      }
      out
    }
  } else {
    library(optparse)
    parse_cli <- function(argv) {
      opts <- list(
        make_option("--ld", type = "character"),
        make_option("--variants", type = "character"),
        make_option("--region-id", dest = "region_id", type = "character"),
        make_option("--ancestry", type = "character", default = "AFR"),
        make_option("--ld-source", dest = "ld_source", type = "character",
                    default = "hgdp_1kg_v3_1_2"),
        make_option("--output", type = "character")
      )
      parse_args(OptionParser(option_list = opts), args = argv)
    }
  }
  library(data.table)
})

args <- commandArgs(trailingOnly = TRUE)
opt <- parse_cli(args)

stopifnot(
  !is.null(opt$ld), !is.null(opt$variants),
  !is.null(opt$region_id), !is.null(opt$output)
)

# --- Load the square LD matrix --------------------------------------------
# plink2 writes the matrix as tab-separated floats, one variant per row.
# Some builds prepend a header with variant ids; data.table::fread
# autodetects. Force colClasses=numeric to catch non-numeric contamination.
ld_dt <- tryCatch(
  fread(opt$ld, header = FALSE, sep = "\t", data.table = FALSE),
  error = function(e) stop("Failed to parse plink LD file ", opt$ld, ": ", conditionMessage(e))
)
# Coerce to numeric matrix and reject any NA cells that survive parsing.
R <- as.matrix(ld_dt)
suppressWarnings(storage.mode(R) <- "numeric")
if (anyNA(R)) {
  n_na <- sum(is.na(R))
  stop(sprintf("plink LD file %s contains %d NA cells after numeric coercion", opt$ld, n_na))
}

# plink2 square mode writes the full matrix, but be defensive and enforce
# symmetry in case a --r-phased build writes upper-triangle only.
if (!isSymmetric(R, tol = 1e-6)) {
  R <- R + t(R) - diag(diag(R))
}

# --- Load variant metadata ------------------------------------------------
# plink2 emits .pvar (header comment lines starting with '##' then a
# '#CHROM ID POS REF ALT' header) or .bim for legacy plink1 format.
ext <- tolower(tools::file_ext(opt$variants))
if (ext %in% c("pvar", "vcor")) {
  pv <- fread(opt$variants, skip = "#CHROM", header = TRUE, sep = "\t", data.table = FALSE)
  names(pv) <- sub("^#", "", names(pv))
  variants <- data.frame(
    SNP_ID = pv$ID,
    CHR = as.character(pv$CHROM),
    POS = as.integer(pv$POS),
    A1 = as.character(pv$REF),
    A2 = as.character(pv$ALT),
    stringsAsFactors = FALSE
  )
} else if (ext == "bim") {
  bim <- fread(opt$variants, header = FALSE, sep = "\t", data.table = FALSE)
  # plink1 .bim: CHR, SNP_ID, cM, POS, A1, A2
  variants <- data.frame(
    SNP_ID = bim[[2]],
    CHR = as.character(bim[[1]]),
    POS = as.integer(bim[[4]]),
    A1 = as.character(bim[[5]]),
    A2 = as.character(bim[[6]]),
    stringsAsFactors = FALSE
  )
} else {
  stop(sprintf("Unrecognized variant file extension '%s' for %s", ext, opt$variants))
}

if (nrow(R) != nrow(variants)) {
  stop(sprintf(
    "plink LD matrix has %d rows but variant file has %d rows -- size mismatch",
    nrow(R), nrow(variants)
  ))
}

# --- Assemble + write -----------------------------------------------------
ld_obj <- list(
  R = R,
  variants = variants,
  ld_source = if (is.null(opt$ld_source)) "hgdp_1kg_v3_1_2" else opt$ld_source,
  region_id = opt$region_id,
  ancestry = if (is.null(opt$ancestry)) "AFR" else opt$ancestry
)

dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
saveRDS(ld_obj, opt$output)
cat(sprintf(
  "[plink_ld_to_rds] wrote %s with %d variants (ld_source=%s)\n",
  opt$output, nrow(R), ld_obj$ld_source
))
