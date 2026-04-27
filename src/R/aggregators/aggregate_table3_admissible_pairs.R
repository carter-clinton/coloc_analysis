# aggregate_table3_admissible_pairs.R -- Track A pre-bioRxiv placeholder-fill
# aggregator for placeholders PH-02, PH-03, PH-04, PH-10b (and used as the
# shared aggregator for the W1 + W5b yield/admissible-pairs scalars in
# quick-260427-e8n).
#
# Purpose: Single-source aggregation over results/multitrait/coloc_summary.tsv
#   (28 attempted Stage 2 trait-pair coloc.susie rows; all PP.H4/PP.H4.abf
#   columns empty per audit-v2 Eval 3.3 IN-PROGRESS) producing the
#   disclosure-honest yield-redistribution table, the admissible-pairs Table 3
#   body, and the per-pair PP.H4 summary scalars used to fill manuscript
#   placeholders L136 (PH-02), L151-154 (PH-03), L156 (PH-04), and L287
#   (PH-10b, Table 3 EUR body).
#
# The identity-LD trait-pair coloc.susie comparator was NOT produced under the
# matched-coverage k2d 2026-04-25 re-fire (k2d covered fine-mapping only, not
# trait-pair coloc.susie -- per audit-v2 Eval 3.3 IN-PROGRESS); the yield
# redistribution table is therefore disclosure-honest "all real-LD empty +
# identity-LD trait-pair comparator absent = both-null = 28 of 28".
#
# Closes Decision-pending item 4 of docs/manuscript/track_a_pivot.md L362
# (pre-bioRxiv blocker; deferred-items #5 of quick-260427-azv SUMMARY).
#
# Authoritative ledger: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   (quick-260427-e8n appends a "Pre-bioRxiv placeholder-fill (2026-04-27) -- LIVE"
#    block carrying the locked scalars emitted by this script to stdout.)
#
# Outputs (relative to PROJECT_ROOT):
#   results/track_a_aggregations/yield_redistribution.tsv         (4 rows; W1 PH-03)
#   results/track_a_aggregations/pair_pp_h4_summary.tsv           (1 row;  W1 PH-02/PH-04)
#   results/track_a_aggregations/table3_admissible_pairs.tsv      (~16 EUR rows; W5b PH-10b)
#
# Stdout (captured by the orchestrator for the FROZEN-NUMBERS LIVE block):
#   FROZEN_BEGIN ... FROZEN_END markers with locked scalars.
#
# Render env: /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
#   (R 4.4.2; base R only -- no extra packages required for this script).
#
# Invocation (from project root):
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     src/R/aggregators/aggregate_table3_admissible_pairs.R
#
# Disk-truth assertions (hard-fail to catch silent drift):
#   - coloc_summary.tsv has 28 data rows + 15-column header.
#   - 0 of 28 PP.H4 / PP.H4.abf cells are non-empty.
#   - EUR slice = 16 rows; AFR slice = 12 rows.
#
# Author: Carter K. Clinton -- 2026-04-27 (built quick-260427-e8n; pre-bioRxiv
#         placeholder-fill; closes Decision-pending item 4).

suppressPackageStartupMessages({
  invisible(NULL)  # base R only
})

# --- Paths --------------------------------------------------------------------

PROJECT_ROOT <- normalizePath(getwd(), mustWork = TRUE)
if (!dir.exists(file.path(PROJECT_ROOT, "results", "multitrait"))) {
  stop(sprintf("[agg-table3] expected to be run from project root; cwd=%s missing results/multitrait",
               PROJECT_ROOT))
}

COLOC_SUMMARY_PATH <- file.path(PROJECT_ROOT, "results", "multitrait", "coloc_summary.tsv")
OUT_DIR            <- file.path(PROJECT_ROOT, "results", "track_a_aggregations")
OUT_YIELD          <- file.path(OUT_DIR, "yield_redistribution.tsv")
OUT_SUMMARY        <- file.path(OUT_DIR, "pair_pp_h4_summary.tsv")
OUT_TABLE3         <- file.path(OUT_DIR, "table3_admissible_pairs.tsv")

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

stopifnot(file.exists(COLOC_SUMMARY_PATH))

# --- Load + disk-truth assertions ---------------------------------------------

# Read as character to preserve "" empty-cell semantics (PP.H4 columns are all empty
# strings; reading as numeric would coerce to NA and lose the disclosure framing).
coloc_summary <- read.table(
  COLOC_SUMMARY_PATH,
  sep = "\t",
  header = TRUE,
  stringsAsFactors = FALSE,
  na.strings = character(0),  # do NOT treat "" as NA -- preserve empty-cell semantics
  colClasses = "character",
  comment.char = ""
)

stopifnot(nrow(coloc_summary) == 28)
stopifnot(ncol(coloc_summary) == 15)

# Disk-truth: every PP.H4 / PP.H4.abf cell is empty.
n_pph4_nonempty     <- sum(nchar(coloc_summary$PP.H4)     > 0)
n_pph4_abf_nonempty <- sum(nchar(coloc_summary$PP.H4.abf) > 0)
stopifnot(n_pph4_nonempty     == 0)
stopifnot(n_pph4_abf_nonempty == 0)

# Disk-truth: 16 EUR + 12 AFR.
n_eur <- sum(coloc_summary$ancestry == "EUR")
n_afr <- sum(coloc_summary$ancestry == "AFR")
stopifnot(n_eur == 16)
stopifnot(n_afr == 12)

# --- (a) Yield redistribution -------------------------------------------------
# Disclosure-honest framing: real-LD all-empty PP.H4 + identity-LD trait-pair
# coloc.susie comparator absent => Survived=0 / Lost=0 / Rescued=0 / Both-null=28.

framing_msg <- paste0(
  "real-LD all-empty (28/28 PP.H4 columns empty); identity-LD trait-pair ",
  "coloc.susie comparator absent (k2d 2026-04-25 re-fire was fine-mapping-only, ",
  "not trait-pair coloc.susie); see audit-v2 Eval 3.3 IN-PROGRESS"
)

yield_df <- data.frame(
  category  = c("Survived", "Lost", "Rescued", "Both-null"),
  count     = c(0, 0, 0, 28),
  threshold = c("identity >= 0.8 AND real >= 0.8",
                "identity >= 0.8 AND real < 0.8",
                "identity < 0.8 AND real >= 0.8",
                "identity < 0.8 OR both empty"),
  framing   = rep(framing_msg, 4),
  stringsAsFactors = FALSE
)

write.table(
  yield_df,
  file = OUT_YIELD,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE,
  fileEncoding = "UTF-8"
)
message(sprintf("[agg-table3] wrote %s (4 rows)", OUT_YIELD))

# --- (b) Pair PP.H4 summary ---------------------------------------------------

summary_df <- data.frame(
  n_total_pairs            = 28L,
  n_pairs_with_pp_h4       = 0L,
  n_admissible_eur_pairs   = n_eur,
  n_admissible_afr_pairs   = n_afr,
  mean_delta_pp_h4         = "non-computable: 0 real-LD PP.H4 values",
  median_delta_pp_h4       = "non-computable",
  range_delta_pp_h4        = "non-computable",
  framing                  = framing_msg,
  stringsAsFactors = FALSE
)

write.table(
  summary_df,
  file = OUT_SUMMARY,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE,
  fileEncoding = "UTF-8"
)
message(sprintf("[agg-table3] wrote %s (1 row)", OUT_SUMMARY))

# --- (c) Table 3 admissible pairs (EUR slice) ---------------------------------
# One row per EUR admissible region x trait-pair (16 rows total per disk).
# Two SH2B3 EUR canonical pairs (BMI-HTN, HTN-stroke) are NOT in coloc_summary
# (per audit-v2 Eval 3.4); those rows are produced by the manuscript prose
# (Table 3 L284-285) verbatim and are NOT emitted by this aggregator (which
# operates strictly on coloc_summary.tsv). The manuscript prose-fill task
# (W5-T3) appends the aggregator-emitted rows BELOW the existing L284-285
# rows.

eur_slice <- coloc_summary[coloc_summary$ancestry == "EUR", , drop = FALSE]
stopifnot(nrow(eur_slice) == 16)

# Region -> human-readable gene mapping (per manuscript and frozen-numbers L121-125).
region_to_gene <- c(
  APOL1_22q12       = "APOL1",
  CXADR_F2RL1_6p21  = "CXADR/F2RL1",
  FTO_16q12         = "FTO",
  MC4R_18q21        = "MC4R",
  SH2B3_12q24       = "SH2B3"
)

trait_pair_str <- function(a, b) sprintf("%s–%s", a, b)

table3_df <- data.frame(
  Region                   = eur_slice$base_region,
  Gene                     = ifelse(eur_slice$base_region %in% names(region_to_gene),
                                    region_to_gene[eur_slice$base_region],
                                    eur_slice$base_region),
  `Trait Pair`             = mapply(trait_pair_str, eur_slice$trait_a, eur_slice$trait_b),
  `PP.H4 (identity)`       = "_empty_ (Stage 2)",
  `PP.H4 (real)`           = "_empty_ (Stage 2)",
  `Delta`                  = "—",
  `n_cs_a (ident)`         = "n/a",
  `n_cs_a (real)`          = "n/a",
  Outcome                  = paste0("both-null (real-LD PP.H4 empty; ",
                                    "identity-LD trait-pair coloc.susie comparator absent)"),
  stringsAsFactors = FALSE,
  check.names = FALSE
)

write.table(
  table3_df,
  file = OUT_TABLE3,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE,
  fileEncoding = "UTF-8"
)
message(sprintf("[agg-table3] wrote %s (%d EUR rows)", OUT_TABLE3, nrow(table3_df)))

# --- Locked scalars (emit to stdout for FROZEN-NUMBERS) -----------------------

cat("FROZEN_BEGIN\n")
cat(sprintf("n_total_pairs\t%d\n",            28L))
cat(sprintf("n_pairs_with_pp_h4\t%d\n",       0L))
cat(sprintf("n_admissible_eur_pairs\t%d\n",   n_eur))
cat(sprintf("n_admissible_afr_pairs\t%d\n",   n_afr))
cat(sprintf("survived_count\t%d\n",           0L))
cat(sprintf("lost_count\t%d\n",               0L))
cat(sprintf("rescued_count\t%d\n",            0L))
cat(sprintf("both_null_count\t%d\n",          28L))
cat(sprintf("mean_delta_pp_h4\t%s\n",         "non-computable"))
cat(sprintf("median_delta_pp_h4\t%s\n",       "non-computable"))
cat(sprintf("range_delta_pp_h4\t%s\n",        "non-computable"))
cat(sprintf("table3_eur_rows_emitted\t%d\n",  nrow(table3_df)))
cat("FROZEN_END\n")

message("[agg-table3] done.")
