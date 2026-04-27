# aggregate_per_trait_pair_and_hubs.R -- Track A pre-bioRxiv placeholder-fill
# aggregator for placeholders PH-05 (per-trait-pair distribution) and PH-07
# (8-hub fates) of quick-260427-e8n.
#
# Purpose: Two aggregations over results/multitrait/coloc_summary.tsv (28 rows)
#   and results/fine_mapping/finemap_summary.tsv (96 rows):
#   1. Per (trait_a, trait_b) attempted-count + PP.H4 distribution (W2 PH-05).
#   2. 8-hub manifest-presence + Stage 2 trait-pair fate table (W2 PH-07).
#
# The 8 hubs (per manuscript L172) are the original identity-LD eight-locus
# pleiotropy claim:
#   KCNJ11/ABCC8 11p15, NEGR1 1p31.1, APOE 19q13, FTO 16q12, MC4R 18q21,
#   SH2B3 12q24, PPARG 3p25, SEC16B 1q25.2.
# Per W0 inventory: only FTO, MC4R, SH2B3 are in the Stage 2 trait-pair
# coloc.susie manifest at all (all PP.H4 empty); APOE is in finemap_summary
# but NOT in trait-pair coloc.susie manifest; KCNJ11/ABCC8, NEGR1, PPARG,
# SEC16B are absent from both.
#
# Authoritative ledger: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   §Pre-bioRxiv placeholder-fill (2026-04-27) -- LIVE (extended in W2 with
#   PH-05/07 scalars).
#
# Outputs (relative to PROJECT_ROOT):
#   results/track_a_aggregations/per_trait_pair_distribution.tsv  (W2 PH-05)
#   results/track_a_aggregations/eight_hub_fates.tsv              (W2 PH-07)
#
# Stdout: FROZEN_BEGIN ... FROZEN_END markers with locked scalars.
#
# Render env: /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#
# Invocation (from project root):
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     src/R/aggregators/aggregate_per_trait_pair_and_hubs.R
#
# Disk-truth assertions (hard-fail to catch silent drift):
#   - coloc_summary.tsv 28 rows / 0 non-empty PP.H4.
#   - finemap_summary.tsv 96 rows.
#   - eight_hub_fates exactly 8 rows; n_with_valid_pp_h4 = 0 sum across all 8.
#
# Author: Carter K. Clinton -- 2026-04-27 (built quick-260427-e8n W2; closes
#         PH-05 + PH-07 of Decision-pending item 4).

suppressPackageStartupMessages({
  invisible(NULL)
})

# --- Paths --------------------------------------------------------------------

PROJECT_ROOT <- normalizePath(getwd(), mustWork = TRUE)
if (!dir.exists(file.path(PROJECT_ROOT, "results", "multitrait"))) {
  stop(sprintf("[agg-tpd-hubs] expected to be run from project root; cwd=%s",
               PROJECT_ROOT))
}

COLOC_SUMMARY_PATH  <- file.path(PROJECT_ROOT, "results", "multitrait",   "coloc_summary.tsv")
FINEMAP_SUMMARY_PATH <- file.path(PROJECT_ROOT, "results", "fine_mapping", "finemap_summary.tsv")
OUT_DIR             <- file.path(PROJECT_ROOT, "results", "track_a_aggregations")
OUT_TPD             <- file.path(OUT_DIR, "per_trait_pair_distribution.tsv")
OUT_HUBS            <- file.path(OUT_DIR, "eight_hub_fates.tsv")

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

stopifnot(file.exists(COLOC_SUMMARY_PATH))
stopifnot(file.exists(FINEMAP_SUMMARY_PATH))

# --- Load -----------------------------------------------------------------

coloc_summary <- read.table(
  COLOC_SUMMARY_PATH,
  sep = "\t", header = TRUE,
  stringsAsFactors = FALSE,
  na.strings = character(0),
  colClasses = "character",
  comment.char = ""
)
finemap_summary <- read.table(
  FINEMAP_SUMMARY_PATH,
  sep = "\t", header = TRUE,
  stringsAsFactors = FALSE,
  na.strings = character(0),
  colClasses = "character",
  comment.char = ""
)

stopifnot(nrow(coloc_summary) == 28)
stopifnot(sum(nchar(coloc_summary$PP.H4) > 0) == 0)
stopifnot(nrow(finemap_summary) == 96)

# --- (a) Per-trait-pair distribution -----------------------------------------

trait_pair_keys <- unique(paste(coloc_summary$trait_a, coloc_summary$trait_b, sep = "|"))

per_pair_rows <- lapply(trait_pair_keys, function(k) {
  parts <- strsplit(k, "\\|", fixed = FALSE)[[1]]
  ta <- parts[[1]]; tb <- parts[[2]]
  rows <- coloc_summary[coloc_summary$trait_a == ta & coloc_summary$trait_b == tb, , drop = FALSE]
  data.frame(
    trait_a               = ta,
    trait_b               = tb,
    n_attempted           = nrow(rows),
    n_with_valid_pp_h4    = sum(nchar(rows$PP.H4) > 0),
    pp_h4_ge_0_5_count    = 0L,  # disk-truth: all PP.H4 empty
    pp_h4_ge_0_8_count    = 0L,  # disk-truth: all PP.H4 empty
    regions_attempted     = paste(unique(rows$base_region), collapse = ";"),
    survive_count         = 0L,
    collapse_count        = nrow(rows),
    stringsAsFactors = FALSE
  )
})
tpd_df <- do.call(rbind, per_pair_rows)
tpd_df <- tpd_df[order(tpd_df$trait_a, tpd_df$trait_b), , drop = FALSE]

write.table(
  tpd_df,
  file = OUT_TPD,
  sep = "\t", quote = FALSE, row.names = FALSE,
  fileEncoding = "UTF-8"
)
message(sprintf("[agg-tpd-hubs] wrote %s (%d unique trait-pairs)", OUT_TPD, nrow(tpd_df)))

# --- (b) 8-hub fates ----------------------------------------------------------

# Hub spec from manuscript L172.
hubs <- list(
  list(name = "KCNJ11/ABCC8", region_pattern = "KCNJ11|ABCC8|11p15"),
  list(name = "NEGR1",        region_pattern = "NEGR1|1p31"),
  list(name = "APOE",         region_pattern = "APOE|19q13"),
  list(name = "FTO",          region_pattern = "FTO_16q12"),
  list(name = "MC4R",         region_pattern = "MC4R_18q21"),
  list(name = "SH2B3",        region_pattern = "SH2B3_12q24"),
  list(name = "PPARG",        region_pattern = "PPARG|3p25"),
  list(name = "SEC16B",       region_pattern = "SEC16B|1q25")
)

# finemap_summary region_id column (per W0 inventory) carries the trait.ANCESTRY.region_id stem.
# We check both base_region (coloc_summary) and region_id (finemap_summary) for hub presence.

is_hub_in_coloc_summary <- function(pat) {
  any(grepl(pat, coloc_summary$base_region))
}
is_hub_in_finemap_summary <- function(pat) {
  any(grepl(pat, finemap_summary$region_id))
}
n_trait_pair_attempts <- function(pat) {
  sum(grepl(pat, coloc_summary$base_region))
}
n_trait_pair_with_valid <- function(pat) {
  sub <- coloc_summary[grepl(pat, coloc_summary$base_region), , drop = FALSE]
  sum(nchar(sub$PP.H4) > 0)
}

hub_rows <- lapply(hubs, function(h) {
  pat <- h$region_pattern
  in_coloc <- is_hub_in_coloc_summary(pat)
  in_fm    <- is_hub_in_finemap_summary(pat)
  n_att    <- n_trait_pair_attempts(pat)
  n_val    <- n_trait_pair_with_valid(pat)
  fate <- if (n_val > 0) {
    "survives"
  } else if (in_coloc) {
    "trait_pair_attempted_all_empty_pp"
  } else if (in_fm) {
    "fine_mapping_only_no_trait_pair"
  } else {
    "absent_from_stage2_manifest"
  }
  region_id <- if (in_coloc) {
    paste(unique(coloc_summary$base_region[grepl(pat, coloc_summary$base_region)]), collapse = ";")
  } else if (in_fm) {
    # extract the {region_id} portion of finemap_summary$region_id (often `bmi.EUR.APOE_19q13`)
    matches <- finemap_summary$region_id[grepl(pat, finemap_summary$region_id)]
    paste(unique(matches), collapse = ";")
  } else {
    NA_character_
  }
  data.frame(
    hub_name                       = h$name,
    region_id                      = region_id %||% NA_character_,
    manifest_present               = in_coloc,
    fine_mapping_present           = in_fm,
    n_trait_pair_rows_attempted    = n_att,
    n_trait_pair_rows_with_valid_pp_h4 = n_val,
    fate                           = fate,
    stringsAsFactors = FALSE
  )
})

`%||%` <- function(a, b) if (is.null(a)) b else a

hubs_df <- do.call(rbind, hub_rows)
stopifnot(nrow(hubs_df) == 8)
stopifnot(sum(hubs_df$n_trait_pair_rows_with_valid_pp_h4) == 0)

write.table(
  hubs_df,
  file = OUT_HUBS,
  sep = "\t", quote = FALSE, row.names = FALSE,
  fileEncoding = "UTF-8"
)
message(sprintf("[agg-tpd-hubs] wrote %s (%d hubs)", OUT_HUBS, nrow(hubs_df)))

# --- Locked scalars (emit to stdout for FROZEN-NUMBERS) -----------------------

n_unique_trait_pairs <- nrow(tpd_df)
hubs_in_manifest_count <- sum(hubs_df$manifest_present)
hubs_finemap_only_count <- sum(!hubs_df$manifest_present & hubs_df$fine_mapping_present)
hubs_absent_count <- sum(!hubs_df$manifest_present & !hubs_df$fine_mapping_present)
hubs_survive_count <- sum(hubs_df$fate == "survives")

cat("FROZEN_BEGIN\n")
cat(sprintf("n_unique_trait_pairs\t%d\n",     n_unique_trait_pairs))
cat(sprintf("hubs_in_manifest_count\t%d\n",   hubs_in_manifest_count))
cat(sprintf("hubs_finemap_only_count\t%d\n",  hubs_finemap_only_count))
cat(sprintf("hubs_absent_count\t%d\n",        hubs_absent_count))
cat(sprintf("hubs_survive_count\t%d\n",       hubs_survive_count))
cat("FROZEN_END\n")

# Print the hub table for visual verification.
message("[agg-tpd-hubs] hub table:")
print(hubs_df)

message("[agg-tpd-hubs] done.")
