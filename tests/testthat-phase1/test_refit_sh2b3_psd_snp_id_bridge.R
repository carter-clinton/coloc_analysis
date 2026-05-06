# tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R
# ta-r3 W1 regression — variant-ID bridge in src/R/regularization/refit_sh2b3_psd_regularized.R
#
# Background (2026-05-06 / debug session ta_r3_w1_snp_id_overlap_zero):
# The harmonized-sumstats SNP_ID convention drifts across the 5 EUR traits at
# data/processed/sumstats_harmonized/{trait}.EUR.tsv.bgz:
#   asthma, bmi              -> rsid    (e.g. "rs7957299")
#   hypertension, stroke, t2d -> chr:pos (e.g. "12:111000057")
# The LD reference at data/processed/ld_reference/EUR/SH2B3_12q24.rds carries
# variants$SNP_ID as 895/895 rsids. The original fitter in commit bccd0d6
# does a naive intersect(rownames(R), sub$SNP_ID) which yields 0 overlap for
# chr:pos sumstats and hard-fails at stopifnot(length(overlap) > 0).
#
# This is the same class of bug fixed previously in commits 069b34f
# (run_qtl_coloc.R) + 7d54183 (run_susie_rss.R), now recurring in the new
# PSD-regularized fitter scaffolded in bccd0d6.
#
# This regression test does NOT use testthat (none of la_multitrait_r,
# r_coloc, or rstats-nyabg ships testthat alongside susieR+data.table). It
# uses base-R stopifnot() and matches the minimal-assertion style of
# tests/testthat-phase1/test_fit_roundtrip.R.
#
# Invocation:
#   /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
#     tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R
#
# Behavior:
#   - On a BROKEN fitter (no chr:pos<->rsid bridge): test fails with
#     non-zero exit AND a banner reporting which traits had 0 overlap.
#   - On a FIXED fitter: all 5 traits pass; exit 0.

suppressPackageStartupMessages({
  library(data.table)
})

# ---------------------------------------------------------------------------
# Locate project root regardless of current working directory.
script_path <- tryCatch({
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) sub("^--file=", "", file_arg[1]) else NULL
}, error = function(e) NULL)
if (is.null(script_path) || !nzchar(script_path)) {
  script_path <- "tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R"
}
project_root <- normalizePath(file.path(dirname(script_path), "..", ".."),
                              mustWork = FALSE)
if (dir.exists(project_root)) setwd(project_root)

# ---------------------------------------------------------------------------
# Test inputs.
LD_PATH      <- "data/processed/ld_reference/EUR/SH2B3_12q24.rds"
SUMSTATS_DIR <- "data/processed/sumstats_harmonized"
TRAITS       <- c("asthma", "bmi", "hypertension", "stroke", "t2d")
CHR_ANCHOR   <- 12L
POS_LO       <- 111e6L
POS_HI       <- 113e6L

stopifnot(file.exists(LD_PATH))
ld <- readRDS(LD_PATH)
stopifnot(is.list(ld), !is.null(ld$R), !is.null(ld$variants))
ld_variants <- as.data.table(ld$variants)
stopifnot(all(c("SNP_ID", "CHR", "POS") %in% names(ld_variants)))

# Source the bridge utility (will be created by the fix). The test FAILS hard
# if the utility is missing — which is exactly the desired failure mode pre-fix.
BRIDGE_PATH <- "src/R/regularization/snp_id_bridge.R"
cat(sprintf("[test] bridge utility expected at: %s\n", BRIDGE_PATH))
if (!file.exists(BRIDGE_PATH)) {
  cat("[test] FAIL: bridge utility does not yet exist (pre-fix state).\n")
  cat("[test] This is the FAILING-TEST-FIRST condition.\n")
  quit(status = 1)
}
source(BRIDGE_PATH)
stopifnot(exists("bridge_snp_id_to_ld_ref", mode = "function"))

# ---------------------------------------------------------------------------
# Per-trait check: build the bridged subset and confirm overlap > 0.
results <- list()
for (trait in TRAITS) {
  ss_path <- file.path(SUMSTATS_DIR, sprintf("%s.EUR.tsv.bgz", trait))
  stopifnot(file.exists(ss_path))
  ss <- fread(cmd = sprintf("zcat %s", ss_path))
  stopifnot(all(c("CHR", "POS", "SNP_ID") %in% names(ss)))

  sub <- ss[as.integer(CHR) == CHR_ANCHOR &
              as.integer(POS) >= POS_LO &
              as.integer(POS) <= POS_HI]

  # Pre-bridge: how many overlap with LD rsids on the raw SNP_ID?
  raw_overlap <- length(intersect(ld_variants$SNP_ID, sub$SNP_ID))

  # Bridged
  sub_bridged <- bridge_snp_id_to_ld_ref(sub, ld_variants)
  bridged_overlap <- length(intersect(ld_variants$SNP_ID, sub_bridged$SNP_ID))

  results[[trait]] <- list(
    trait = trait,
    n_region_rows = nrow(sub),
    raw_overlap = raw_overlap,
    bridged_overlap = bridged_overlap,
    snp_id_sample = head(sub$SNP_ID, 1)
  )

  cat(sprintf("[test] trait=%s n_region=%d raw_overlap=%d bridged_overlap=%d sample=%s\n",
              trait, nrow(sub), raw_overlap, bridged_overlap,
              head(sub$SNP_ID, 1)))
}

# ---------------------------------------------------------------------------
# Assertions.
cat("\n[test] === assertions ===\n")

# 1) Every trait must have non-zero bridged overlap.
fail_traits <- vapply(results,
                      function(r) r$bridged_overlap == 0L,
                      logical(1))
if (any(fail_traits)) {
  cat("[test] FAIL: zero bridged overlap for traits: ",
      paste(names(results)[fail_traits], collapse = ", "), "\n", sep = "")
  quit(status = 1)
}

# 2) Bridged overlap must be >= raw overlap (bridge is monotone non-decreasing).
mono <- vapply(results,
               function(r) r$bridged_overlap >= r$raw_overlap,
               logical(1))
if (!all(mono)) {
  cat("[test] FAIL: bridged_overlap < raw_overlap for: ",
      paste(names(results)[!mono], collapse = ", "), "\n", sep = "")
  quit(status = 1)
}

# 3) Bridge must produce real lift on chr:pos traits (ht/stroke/t2d should go
#    from raw_overlap=0 to bridged_overlap >= 100).
chrpos_traits <- c("hypertension", "stroke", "t2d")
for (t in chrpos_traits) {
  r <- results[[t]]
  if (r$raw_overlap != 0L) {
    cat(sprintf("[test] WARN: %s raw_overlap=%d (expected 0 for chr:pos sumstats)\n",
                t, r$raw_overlap))
  }
  if (r$bridged_overlap < 100L) {
    cat(sprintf("[test] FAIL: %s bridged_overlap=%d (expected >= 100)\n",
                t, r$bridged_overlap))
    quit(status = 1)
  }
}

# 4) Already-rsid traits (asthma, bmi) must have raw_overlap > 0 already; the
#    bridge must NOT regress them.
for (t in c("asthma", "bmi")) {
  r <- results[[t]]
  if (r$raw_overlap == 0L) {
    cat(sprintf("[test] FAIL: %s raw_overlap=0 (expected >0 for rsid sumstats)\n", t))
    quit(status = 1)
  }
  if (r$bridged_overlap < r$raw_overlap) {
    cat(sprintf("[test] FAIL: %s bridge regressed: raw=%d bridged=%d\n",
                t, r$raw_overlap, r$bridged_overlap))
    quit(status = 1)
  }
}

cat("\n[test] PASS: all 5 traits have bridged_overlap > 0\n")
cat("[test] PASS: chr:pos traits successfully bridged via (CHR, POS)\n")
cat("[test] PASS: rsid traits unchanged by bridge\n")
quit(status = 0)
