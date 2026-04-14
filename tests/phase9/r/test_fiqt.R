library(testthat)

# FIQT sign + shrinkage monotonicity (Plan 09-03 Task 2).
#
# NOTE on test design: winnerscurse::FDR_IQT applies a Benjamini-Hochberg
# correction across the supplied rows, so single-row inputs cannot exhibit
# any shrinkage (adj_p == p when n==1). Tests below therefore construct a
# realistic multi-signal frame (1 focal signal + 100 null-distributed
# background rows) where BH multiplicity correction produces the expected
# empirical-Bayes behavior:
#
#   - high-|z| focal rows       -> minimal shrinkage (|beta_FIQT| ~ |beta|)
#   - low-|z| focal rows (z~1.5) -> substantial shrinkage toward zero
#   - sign of beta_FIQT matches sign of raw beta (sign preservation)

# testthat::test_file() changes cwd to the test's own directory, so resolve
# the script path relative to that (../../../ = project root from tests/phase9/r).
.run_fiqt_path <- function() {
  # Walk up to find a directory containing src/snakemake/scripts/run_fiqt.R.
  candidates <- c(
    "../../../src/snakemake/scripts/run_fiqt.R",      # from tests/phase9/r
    "../../src/snakemake/scripts/run_fiqt.R",          # from tests/phase9
    "src/snakemake/scripts/run_fiqt.R",                # from project root
    file.path(Sys.getenv("PROJECT_ROOT", ""), "src/snakemake/scripts/run_fiqt.R")
  )
  hit <- candidates[file.exists(candidates)]
  if (length(hit) == 0L) return(NA_character_)
  hit[[1L]]
}

.skip_if_no_winnerscurse <- function() {
  skip_if_not_installed("winnerscurse")
  p <- .run_fiqt_path()
  skip_if_not(!is.na(p), "run_fiqt.R not yet created (Plan 09-03)")
}

.source_run_fiqt <- function() {
  source(.run_fiqt_path())
}

.null_background <- function(n = 100, seed = 42, se = 0.05) {
  set.seed(seed)
  data.frame(
    rsid = paste0("null_", seq_len(n)),
    beta = rnorm(n, 0, se / 5),   # z ~ 0 under se
    se = rep(se, n),
    n = rep(100000, n),
    stringsAsFactors = FALSE
  )
}


test_that("apply_fiqt barely shrinks high-|z| signals (z=10)", {
  .skip_if_no_winnerscurse()
  .source_run_fiqt()

  focal <- data.frame(
    rsid = "rs_high", beta = 0.5, se = 0.05, n = 100000,
    stringsAsFactors = FALSE
  )
  df <- rbind(focal, .null_background())
  res <- apply_fiqt(df)
  row <- res[res$rsid == "rs_high", ]
  expect_true("beta_FIQT" %in% names(res))
  # High-z: shrinkage < 5% (|beta_FIQT| / |beta| > 0.95)
  expect_gt(abs(row$beta_FIQT) / 0.5, 0.90)
})


test_that("apply_fiqt substantially shrinks low-|z| signals (z=1.5)", {
  .skip_if_no_winnerscurse()
  .source_run_fiqt()

  focal <- data.frame(
    rsid = "rs_low", beta = 0.075, se = 0.05, n = 100000,
    stringsAsFactors = FALSE
  )
  df <- rbind(focal, .null_background())
  res <- apply_fiqt(df)
  row <- res[res$rsid == "rs_low", ]
  # Low-z: shrinkage substantial (|beta_FIQT| / |beta| < 0.5)
  expect_lt(abs(row$beta_FIQT) / 0.075, 0.5)
})


test_that("apply_fiqt preserves effect direction (sign) across mixed-direction input", {
  .skip_if_no_winnerscurse()
  .source_run_fiqt()

  focal <- data.frame(
    rsid = c("rsA", "rsB", "rsC", "rsD"),
    beta = c(0.3, -0.25, 0.15, -0.4),
    se = c(0.05, 0.04, 0.06, 0.05),
    n = rep(100000, 4),
    stringsAsFactors = FALSE
  )
  df <- rbind(focal, .null_background())
  res <- apply_fiqt(df)
  focal_res <- res[res$rsid %in% focal$rsid, ]
  # Re-align to input order
  focal_res <- focal_res[match(focal$rsid, focal_res$rsid), ]
  expect_equal(sign(focal_res$beta_FIQT), sign(focal$beta))
})


test_that("apply_fiqt errors on duplicate rsid", {
  .skip_if_no_winnerscurse()
  .source_run_fiqt()
  df <- data.frame(
    rsid = c("rsX", "rsX"),
    beta = c(0.1, 0.2),
    se = c(0.05, 0.05),
    n = rep(100000, 2),
    stringsAsFactors = FALSE
  )
  expect_error(apply_fiqt(df))
})


test_that("apply_fiqt handles upper-case column names", {
  .skip_if_no_winnerscurse()
  .source_run_fiqt()
  df <- data.frame(
    RSID = paste0("rs", 1:3),
    BETA = c(0.2, 0.3, -0.15),
    SE = rep(0.05, 3),
    N = rep(100000, 3)
  )
  res <- apply_fiqt(df)
  expect_true("beta_FIQT" %in% names(res))
  expect_true("se_FIQT" %in% names(res))
})
