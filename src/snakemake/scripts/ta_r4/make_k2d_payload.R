#!/usr/bin/env Rscript
# One k2d identity payload (the make_identity_ld_refs.R payload, per region): R = NULL, use_identity = TRUE.
# Reproduction only (repro_k2d_* arms); production A2 uses make_matched_identity_payload.R.
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
})

opt <- parse_args(OptionParser(option_list = list(make_option("--variants"), make_option("--out"))))
variants_df <- as.data.frame(fread(opt$variants, sep = "\t", header = TRUE))
payload <- list(R = NULL, variants = variants_df, use_identity = TRUE, status = "identity")
dir.create(dirname(opt$out), recursive = TRUE, showWarnings = FALSE)
saveRDS(payload, opt$out)
cat(sprintf("k2d payload %s (%d variants) from %s\n", opt$out, nrow(variants_df), opt$variants))
