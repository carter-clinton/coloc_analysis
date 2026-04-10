#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(optparse)
})

option_list <- list(
  make_option("--rds", type = "character", help = "LD RDS file"),
  make_option("--snp-a", type = "character", help = "SNP ID A (rsID or chr:pos)"),
  make_option("--snp-b", type = "character", help = "SNP ID B (rsID or chr:pos)")
)
opt <- parse_args(OptionParser(option_list = option_list))
if (is.null(opt$rds) || is.null(opt$snp_a) || is.null(opt$snp_b)) {
  stop("--rds, --snp-a, --snp-b are required", call. = FALSE)
}

ld <- readRDS(opt$rds)
vars <- ld$variants
if (is.null(vars)) {
  cat("NA")
  quit(save = "no", status = 0)
}

find_idx <- function(snp) {
  if (is.null(snp) || snp == "") return(NA_integer_)
  idx <- which(vars$SNP_ID == snp)
  if (length(idx) > 0) return(idx[1])
  if (grepl(":", snp)) {
    parts <- strsplit(snp, ":")[[1]]
    if (length(parts) >= 2) {
      chr <- gsub("^chr", "", parts[1], ignore.case = TRUE)
      pos <- suppressWarnings(as.integer(parts[2]))
      if (!is.na(pos)) {
        idx <- which(vars$CHR == as.integer(chr) & vars$POS == pos)
        if (length(idx) > 0) return(idx[1])
      }
    }
  }
  NA_integer_
}

idx_a <- find_idx(opt$snp_a)
idx_b <- find_idx(opt$snp_b)
if (is.na(idx_a) || is.na(idx_b)) {
  cat("NA")
  quit(save = "no", status = 0)
}

r_val <- ld$R[idx_a, idx_b]
if (is.na(r_val)) {
  cat("NA")
  quit(save = "no", status = 0)
}
cat(sprintf("%.6f", r_val^2))
