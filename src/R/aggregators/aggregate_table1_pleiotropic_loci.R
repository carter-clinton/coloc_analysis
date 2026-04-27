# aggregate_table1_pleiotropic_loci.R -- Track A pre-bioRxiv placeholder-fill
# aggregator for placeholder PH-06 (Table 1 surviving rows) of quick-260427-e8n.
#
# Purpose: Filter results/multitrait/coloc_summary.tsv to rows where the
#   real-LD PP.H4 column is non-empty AND PP.H4 >= 0.5, the manuscript's
#   pre-registered Tier B threshold. Per disclosure_decisions PH-06 chosen=a
#   (locked at plan-write time per execution_protocol §7), the expected
#   output is 0 rows (since all 28 PP.H4 columns are empty under real-LD).
#
# This is the disclosure-honest 0-row outcome that backs Table 1 ("no
# real-LD-surviving signal at PP.H4 >= 0.5"). Threshold-lowering to 0.3
# (which would surface the FTO_16q12 EUR Tier-C 0.3099 signal) is
# explicitly OUT of scope -- would reframe the threshold without OSF
# amendment; manuscript already locked to "Tier B threshold = 0.5"
# throughout.
#
# A hard-fail assertion guards against silent positive-result drift: if a
# future re-fit produces non-zero PP.H4 >= 0.5 rows, this assert will fail
# and the manuscript narrative will require updating (positive-result
# safety net).
#
# Authoritative ledger: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   §Pre-bioRxiv placeholder-fill (2026-04-27) -- LIVE (extended in W3 with
#   PH-06 scalar table1_surviving_n=0).
#
# Outputs (relative to PROJECT_ROOT):
#   results/track_a_aggregations/table1_surviving_rows.tsv  (header + 0 data
#                                                            rows + a leading
#                                                            disclosure comment)
#
# Stdout: FROZEN_BEGIN ... FROZEN_END markers.
#
# Render env: /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#
# Invocation (from project root):
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     src/R/aggregators/aggregate_table1_pleiotropic_loci.R
#
# Disk-truth assertions:
#   - coloc_summary.tsv 28 rows; 0 non-empty PP.H4.
#   - n_surviving_rows == 0 (positive-result safety net).
#
# Author: Carter K. Clinton -- 2026-04-27 (built quick-260427-e8n W3; closes
#         PH-06 of Decision-pending item 4).

suppressPackageStartupMessages({
  invisible(NULL)
})

# --- Paths --------------------------------------------------------------------

PROJECT_ROOT <- normalizePath(getwd(), mustWork = TRUE)
if (!dir.exists(file.path(PROJECT_ROOT, "results", "multitrait"))) {
  stop(sprintf("[agg-table1] expected to be run from project root; cwd=%s",
               PROJECT_ROOT))
}

COLOC_SUMMARY_PATH <- file.path(PROJECT_ROOT, "results", "multitrait", "coloc_summary.tsv")
OUT_DIR            <- file.path(PROJECT_ROOT, "results", "track_a_aggregations")
OUT_TABLE1         <- file.path(OUT_DIR, "table1_surviving_rows.tsv")

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)
stopifnot(file.exists(COLOC_SUMMARY_PATH))

PP_H4_THRESHOLD <- 0.5  # manuscript Tier B threshold; locked.
COLOC_MD5       <- "5fa3c4004970c5da711d05947cb1f7d2"

# --- Load + filter ------------------------------------------------------------

coloc_summary <- read.table(
  COLOC_SUMMARY_PATH,
  sep = "\t", header = TRUE,
  stringsAsFactors = FALSE,
  na.strings = character(0),
  colClasses = "character",
  comment.char = ""
)

stopifnot(nrow(coloc_summary) == 28)
stopifnot(sum(nchar(coloc_summary$PP.H4) > 0) == 0)

# Filter: rows with non-empty AND numeric AND >= 0.5 PP.H4.
non_empty_idx <- nchar(coloc_summary$PP.H4) > 0
if (any(non_empty_idx)) {
  pp_numeric <- suppressWarnings(as.numeric(coloc_summary$PP.H4[non_empty_idx]))
  surviving_idx <- which(non_empty_idx)[!is.na(pp_numeric) & pp_numeric >= PP_H4_THRESHOLD]
} else {
  surviving_idx <- integer(0)
}
n_surviving_rows <- length(surviving_idx)

# Hard-fail (positive-result safety net): if this trips, manuscript narrative
# must be updated.
stopifnot(n_surviving_rows == 0)

# --- Build output: header preserved per manuscript Table 1 schema -------------

table1_columns <- c(
  "Rank",
  "Locus",
  "Trait Pair",
  "PP.H4 (real-LD)",
  "PP.H4 (identity-LD)",
  "Delta PP.H4",
  "CS size (real-LD)",
  "Lead variant (PIP)",
  "Gene",
  "Pathway"
)

# Write header + zero data rows + leading disclosure comment line.
header_comment <- paste0(
  "# Disclosure-honest 0-row outcome -- 0 of 28 attempted Stage 2 trait-pair ",
  "coloc.susie rows survive at PP.H4 >= ", PP_H4_THRESHOLD,
  " (all 28 PP.H4 columns are empty under real-LD; per AUDIT-REVIEW-V2-2026-04-26.md ",
  "Eval 3.3 IN-PROGRESS). Source: results/multitrait/coloc_summary.tsv md5 ",
  COLOC_MD5,
  ". Threshold-lowering to 0.3 (which would surface the FTO_16q12 EUR Tier-C ",
  "0.3099 signal) is OUT of scope per disclosure_decisions PH-06 chosen=a ",
  "(would reframe the threshold without OSF amendment)."
)

con <- file(OUT_TABLE1, open = "w", encoding = "UTF-8")
writeLines(header_comment, con)
writeLines(paste(table1_columns, collapse = "\t"), con)
# 0 data rows.
close(con)

message(sprintf("[agg-table1] wrote %s (header + %d data rows; threshold=%s)",
                OUT_TABLE1, n_surviving_rows, PP_H4_THRESHOLD))

# --- Locked scalars (emit to stdout for FROZEN-NUMBERS) -----------------------

cat("FROZEN_BEGIN\n")
cat(sprintf("table1_surviving_n\t%d\n",        n_surviving_rows))
cat(sprintf("table1_threshold\t%s\n",          PP_H4_THRESHOLD))
cat(sprintf("table1_total_attempted\t%d\n",    nrow(coloc_summary)))
cat(sprintf("table1_total_with_pp_h4\t%d\n",   sum(non_empty_idx)))
cat("FROZEN_END\n")

message("[agg-table1] done.")
