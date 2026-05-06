#!/usr/bin/env Rscript
# src/R/aggregators/merge_r2_into_summary.R
#
# ta-r3 W3: merge R2 canonical-pair parity rows into coloc_summary.tsv
#
# Reads:
#   results/multitrait/coloc_susie/*.json                (R1 cache; preserved as-is)
#   results/multitrait/coloc_susie_R2/*.json             (canonical R2; 9 SH2B3 + 6 W3)
#   results/multitrait/coloc_susie_R2_FTO/*.json         (W3 FTO_16q12 EUR)
#   results/multitrait/coloc_susie_R2_MC4R/*.json        (W3 MC4R_18q21 EUR)
#   results/multitrait/coloc_susie_R2_APOL1/*.json       (W3 APOL1_22q12 EUR)
#   results/multitrait/coloc_susie_R2_CXADR/*.json       (W3 CXADR_F2RL1_6p21 EUR)
#   results/multitrait/coloc_summary.tsv                 (input — post-W2 baseline)
#
# Writes:
#   results/multitrait/coloc_summary.tsv                 (merged; W3 rows appended/upserted)
#
# Mirrors SH2B3 R2 merge pattern from /gsd-quick 260501-wdn (W5 closeout).
#
# Phase: ta-r3-audit-v2-driven-psd-and-r1-refire (Wave 3 audit-driven re-analysis)
# Honors plan-of-plans risk register row 4: SH2B3 R2 rows + R1 W2-rerun rows
# preserved (NEVER overwrite — APPEND or UPSERT only).

suppressPackageStartupMessages({
  library(jsonlite)
  library(data.table)
})

SUMMARY_PATH <- "results/multitrait/coloc_summary.tsv"

# All R2 directories (canonical SH2B3 + 4 W3 per-region) — every directory is
# read; the canonical coloc_susie_R2/ also contains W3 copies, but UPSERT-by-
# pair_id makes that idempotent.
R2_DIRS <- c(
  "results/multitrait/coloc_susie_R2",       # 9 SH2B3 + 6 W3 (canonical)
  "results/multitrait/coloc_susie_R2_FTO",   # 3 W3 FTO_16q12 EUR
  "results/multitrait/coloc_susie_R2_MC4R",  # 1 W3 MC4R_18q21 EUR
  "results/multitrait/coloc_susie_R2_APOL1", # 1 W3 APOL1_22q12 EUR
  "results/multitrait/coloc_susie_R2_CXADR"  # 1 W3 CXADR_F2RL1_6p21 EUR
)

parse_json_to_row <- function(jpath) {
  j <- tryCatch(jsonlite::fromJSON(jpath), error = function(e) NULL)
  pair_id <- sub("\\.json$", "", basename(jpath))
  if (is.null(j)) {
    return(list(pair_id = pair_id, PP.H0.abf = NA_real_, PP.H1.abf = NA_real_,
                PP.H2.abf = NA_real_, PP.H3.abf = NA_real_, PP.H4.abf = NA_real_))
  }
  s <- j$summary
  if (is.null(s) || (is.list(s) && length(s) == 0)) {
    return(list(pair_id = pair_id, PP.H0.abf = NA_real_, PP.H1.abf = NA_real_,
                PP.H2.abf = NA_real_, PP.H3.abf = NA_real_, PP.H4.abf = NA_real_))
  }
  # summary is a single-row dict (per run_coloc_susie.R legacy-compat schema:
  # max-PP.H4-across-CS-pairs row promoted to top-level summary)
  if (is.data.frame(s) && nrow(s) > 0) {
    idx <- which.max(s[["PP.H4.abf"]])
    if (length(idx) == 0) idx <- 1
    list(pair_id = pair_id,
         PP.H0.abf = as.numeric(s[["PP.H0.abf"]][idx] %||% NA),
         PP.H1.abf = as.numeric(s[["PP.H1.abf"]][idx] %||% NA),
         PP.H2.abf = as.numeric(s[["PP.H2.abf"]][idx] %||% NA),
         PP.H3.abf = as.numeric(s[["PP.H3.abf"]][idx] %||% NA),
         PP.H4.abf = as.numeric(s[["PP.H4.abf"]][idx] %||% NA))
  } else if (is.list(s)) {
    list(pair_id = pair_id,
         PP.H0.abf = as.numeric(s[["PP.H0.abf"]] %||% NA),
         PP.H1.abf = as.numeric(s[["PP.H1.abf"]] %||% NA),
         PP.H2.abf = as.numeric(s[["PP.H2.abf"]] %||% NA),
         PP.H3.abf = as.numeric(s[["PP.H3.abf"]] %||% NA),
         PP.H4.abf = as.numeric(s[["PP.H4.abf"]] %||% NA))
  } else {
    list(pair_id = pair_id, PP.H0.abf = NA_real_, PP.H1.abf = NA_real_,
         PP.H2.abf = NA_real_, PP.H3.abf = NA_real_, PP.H4.abf = NA_real_)
  }
}

`%||%` <- function(x, y) if (!is.null(x) && length(x) > 0) x else y

# Collect R2 rows (UPSERT semantics: same pair_id from canonical wins over per-region)
r2_seen <- list()
for (d in R2_DIRS) {
  if (!dir.exists(d)) next
  for (f in list.files(d, pattern = "\\.json$", full.names = TRUE)) {
    row <- parse_json_to_row(f)
    pid <- row$pair_id
    # Canonical R2 dir takes precedence (already present from W2 + W3 copies)
    if (is.null(r2_seen[[pid]])) {
      r2_seen[[pid]] <- row
    }
  }
}
r2_dt <- rbindlist(r2_seen, fill = TRUE)
cat(sprintf("Collected %d unique R2 pair_id rows from %d directories\n",
             nrow(r2_dt), length(R2_DIRS)))

# Read existing coloc_summary.tsv (post-W2 baseline = 37 rows)
existing <- fread(SUMMARY_PATH)
cat(sprintf("Existing coloc_summary.tsv: %d rows + header\n", nrow(existing)))

# UPSERT merge: replace rows in existing where pair_id matches an R2 row;
# append new R2 pair_ids that don't already exist
existing_pair_ids <- existing$pair_id
new_pair_ids <- r2_dt$pair_id
keep_mask <- !(existing$pair_id %in% new_pair_ids)
n_replaced <- sum(!keep_mask)
n_new <- sum(!(new_pair_ids %in% existing_pair_ids))
n_kept <- sum(keep_mask)

merged <- rbind(existing[keep_mask], r2_dt, fill = TRUE)
cat(sprintf("Merge: kept %d existing + replaced %d + appended %d new = %d total rows\n",
             n_kept, n_replaced, n_new, nrow(merged)))

# Sort by pair_id for deterministic byte-level output
merged <- merged[order(pair_id)]
fwrite(merged, SUMMARY_PATH, sep = "\t", na = "")
cat(sprintf("WROTE %s\n", SUMMARY_PATH))
