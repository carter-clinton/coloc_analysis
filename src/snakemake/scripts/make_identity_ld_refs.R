#!/usr/bin/env Rscript
# make_identity_ld_refs.R -- Author: quick-260424-k2d (Route A identity-LD re-fire)
#
# Produces identity-LD payloads compatible with src/legacy/region_analysis/scripts/run_susie_rss.R
# load_ld_matrix() (lines 132-147), which detects list(use_identity=TRUE) and triggers
# the diag() fallback at lines 465-468 to construct R <- diag(nrow(subset)) at runtime.
#
# Payload schema (must match existing data/processed/ld_reference/EUR/_identity_backup/*.rds.ident):
#   list(
#     R            = NULL,                    # NULL triggers the identity-matrix fallback branch
#     variants     = <data.frame 5 cols>,     # CHR, POS, REF, ALT, SNP_ID for variant matching
#     use_identity = TRUE,                    # isTRUE(obj$use_identity) is the gating condition
#     status       = "identity"               # surfaces as ld_status in the output finemap JSON
#   )
#
# Usage (no CLI args; hard-coded 12-region loop for transparency):
#   /rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript \
#     src/snakemake/scripts/make_identity_ld_refs.R

suppressPackageStartupMessages({
  library(data.table)
})

VARIANTS_DIR <- "data/processed/ld_reference/variants"
OUTPUT_ROOT  <- "data/processed/ld_reference_identity"
ANCESTRIES   <- c("EUR", "AFR")

REGIONS <- c(
  "FTO_16q12",
  "MC4R_18q21",
  "SH2B3_12q24",
  "APOL1_22q12",
  "PYHIN1_1q23",
  "CXADR_F2RL1_6p21",
  "BMI_5q13_3",
  "9p21_CDKN2A",
  "APOE_19q13",
  "SLC2A9_urate",
  "BMI_Xq24",
  "HLA_6p21"
)

# Identity-LD is matrix-structure-free: the same payload works for both
# ancestries. Variant lists (data/processed/ld_reference/variants/*.tsv) are
# region-level and not population-partitioned, so we write the identical
# payload to EUR/ and AFR/ for each region. This keeps the Snakemake
# run_finemap rule happy for the full 96-fit DAG (finemap_manifest.tsv
# includes both EUR and AFR rows).

for (ancestry in ANCESTRIES) {
  out_dir <- file.path(OUTPUT_ROOT, ancestry)
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  cat(sprintf("=== %s (out: %s) ===\n", ancestry, out_dir))
  for (region_safe in REGIONS) {
    variants_path <- file.path(VARIANTS_DIR, paste0(region_safe, ".tsv"))
    if (!file.exists(variants_path)) {
      cat(sprintf("  SKIP %-22s -- variants file missing: %s\n", region_safe, variants_path))
      next
    }
    variants_df <- as.data.frame(fread(variants_path, sep = "\t", header = TRUE))
    payload <- list(
      R = NULL,
      variants = variants_df,
      use_identity = TRUE,
      status = "identity"
    )
    out_path <- file.path(out_dir, paste0(region_safe, ".rds"))
    saveRDS(payload, out_path)
    cat(sprintf("  WROTE %-22s (%6d variants) -> %s\n",
                region_safe, nrow(variants_df), out_path))
  }
}

for (ancestry in ANCESTRIES) {
  out_dir <- file.path(OUTPUT_ROOT, ancestry)
  cat(sprintf("Done %s: %d identity-LD payloads in %s\n",
              ancestry,
              length(list.files(out_dir, pattern = "\\.rds$")),
              out_dir))
}
