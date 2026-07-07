# tests/testthat-phase1/test_psd_utils_byte_identical.R
# m3-06-W6-T1 (ROADMAP 999.1 §2) — byte-identity regression gate for the
# Track-A-sensitive PSD refactor.
#
# Background (2026-07-07):
# refit_sh2b3_psd_regularized.R is EUR r3 code tied to an in-flight Track-A
# submission + the r3 OSF amendment (osf-amendment-r3-2026-05-04.md). W6 factors
# its two PSD functions (psd_regularize_ridge — Wen 2017; psd_regularize_eigclip
# — Hutchinson 2020, lambda_floor=1e-6) into a shared, path-robust
# src/R/regularization/psd_utils.R so the AFR native-panel conditioning
# (osf-amendment-afr-native-ld-nan-psd-2026-07-03.md) can reuse the SAME
# pre-registered numerics. The refactor MUST NOT change r3 numerics.
#
# This test gates the extraction on TWO independent anchors:
#   (1) a frozen golden captured from the PRE-refactor inline source
#       (tests/testthat-phase1/fixtures/psd_golden_r3.rds), and
#   (2) a VERBATIM in-test copy of the original functions (ref_ridge/ref_eigclip)
#       — anchoring byte-identity to the literal source text as well as the golden.
# Every battery entry is checked with identical() (bit-for-bit, full double
# precision).
#
# Follows the base-R stopifnot()/quit(status=) style of
# tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R (no testthat).
#
# Invocation:
#   /rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript \
#     tests/testthat-phase1/test_psd_utils_byte_identical.R
#
# Behavior:
#   - PRE-fix (psd_utils.R absent): FAIL with non-zero exit (failing-test-first).
#   - POST-fix: every battery entry identical() to the golden AND to the
#     verbatim in-test reference; exit 0.

# ---------------------------------------------------------------------------
# Locate project root regardless of current working directory.
script_path <- tryCatch({
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) sub("^--file=", "", file_arg[1]) else NULL
}, error = function(e) NULL)
if (is.null(script_path) || !nzchar(script_path)) {
  script_path <- "tests/testthat-phase1/test_psd_utils_byte_identical.R"
}
project_root <- normalizePath(file.path(dirname(script_path), "..", ".."),
                              mustWork = FALSE)
if (dir.exists(project_root)) setwd(project_root)

# ---------------------------------------------------------------------------
# VERBATIM in-test reference copy of the ORIGINAL inline functions
# (refit_sh2b3_psd_regularized.R lines 71-87). Secondary byte-identity anchor.
ref_ridge <- function(R, lambda) {
  R_reg <- R + lambda * diag(nrow(R))
  d <- sqrt(diag(R_reg))
  R_reg <- sweep(sweep(R_reg, 1, d, "/"), 2, d, "/")
  R_reg
}
ref_eigclip <- function(R, lambda_floor = 1e-6) {
  e <- eigen(R, symmetric = TRUE)
  d_clip <- pmax(e$values, lambda_floor)
  R_clip <- e$vectors %*% diag(d_clip) %*% t(e$vectors)
  d <- sqrt(diag(R_clip))
  R_clip <- sweep(sweep(R_clip, 1, d, "/"), 2, d, "/")
  R_clip
}

# ---------------------------------------------------------------------------
# Load the frozen golden fixture.
GOLDEN_PATH <- "tests/testthat-phase1/fixtures/psd_golden_r3.rds"
if (!file.exists(GOLDEN_PATH)) {
  cat(sprintf("[test] FAIL: golden fixture missing at %s\n", GOLDEN_PATH))
  quit(status = 1)
}
golden <- readRDS(GOLDEN_PATH)
stopifnot(is.list(golden), !is.null(golden$inputs), !is.null(golden$ridge),
          !is.null(golden$eigclip))
Rwell  <- golden$inputs$Rwell
Rindef <- golden$inputs$Rindef
LAMBDAS      <- golden$meta$lambdas
LAMBDA_FLOOR <- golden$meta$lambda_floor
cat(sprintf("[test] golden loaded: lambdas={%s} lambda_floor=%g min_eig_indef=%.6g\n",
            paste(LAMBDAS, collapse = ","), LAMBDA_FLOOR, golden$meta$min_eig_indef))
# Confirm the golden's indefinite matrix genuinely exercises the eigclip floor.
stopifnot(golden$meta$min_eig_indef < LAMBDA_FLOOR)

# ---------------------------------------------------------------------------
# Source the canonical util under test (will be created by the fix). The test
# FAILS hard if it is missing — the desired failure mode pre-fix (RED).
UTIL_PATH <- "src/R/regularization/psd_utils.R"
cat(sprintf("[test] canonical util expected at: %s\n", UTIL_PATH))
if (!file.exists(UTIL_PATH)) {
  cat("[test] FAIL: src/R/regularization/psd_utils.R does not yet exist (pre-fix state).\n")
  cat("[test] This is the FAILING-TEST-FIRST condition.\n")
  quit(status = 1)
}
source(UTIL_PATH)
stopifnot(exists("psd_regularize_ridge", mode = "function"),
          exists("psd_regularize_eigclip", mode = "function"))

# ---------------------------------------------------------------------------
# Assertions.
cat("\n[test] === assertions ===\n")
fail <- FALSE
check <- function(label, a, b) {
  ok <- identical(a, b)
  cat(sprintf("[test] %-46s identical=%s\n", label, ok))
  if (!ok) fail <<- TRUE
  ok
}

# 1) ridge at every pre-registered lambda, on the well-conditioned matrix.
for (lam in LAMBDAS) {
  key <- sprintf("Rwell_%s", format(lam, scientific = FALSE))
  out <- psd_regularize_ridge(Rwell, lam)
  check(sprintf("ridge Rwell lambda=%s vs golden", lam), out, golden$ridge[[key]])
  check(sprintf("ridge Rwell lambda=%s vs verbatim", lam), out, ref_ridge(Rwell, lam))
}
# 1b) ridge at every lambda, on the indefinite matrix (robustness coverage).
for (lam in LAMBDAS) {
  key <- sprintf("Rindef_%s", format(lam, scientific = FALSE))
  out <- psd_regularize_ridge(Rindef, lam)
  check(sprintf("ridge Rindef lambda=%s vs golden", lam), out, golden$ridge[[key]])
  check(sprintf("ridge Rindef lambda=%s vs verbatim", lam), out, ref_ridge(Rindef, lam))
}

# 2) eigclip on the well-conditioned matrix (clip is a no-op — min eig > floor).
out_ew <- psd_regularize_eigclip(Rwell, LAMBDA_FLOOR)
check("eigclip Rwell vs golden", out_ew, golden$eigclip$Rwell)
check("eigclip Rwell vs verbatim", out_ew, ref_eigclip(Rwell, LAMBDA_FLOOR))

# 3) eigclip on the NEGATIVE-eigenvalue matrix (clip branch genuinely fires).
out_ei <- psd_regularize_eigclip(Rindef, LAMBDA_FLOOR)
check("eigclip Rindef (neg-eig) vs golden", out_ei, golden$eigclip$Rindef)
check("eigclip Rindef (neg-eig) vs verbatim", out_ei, ref_eigclip(Rindef, LAMBDA_FLOOR))

# ---------------------------------------------------------------------------
if (fail) {
  cat("\n[test] FAIL: at least one battery entry is NOT identical() (numeric drift).\n")
  quit(status = 1)
}
cat("\n[test] PASS: psd_utils.R ridge/eigclip identical() to the frozen golden AND\n")
cat("[test] PASS: identical() to the verbatim in-test reference — r3 numerics unchanged.\n")
quit(status = 0)
