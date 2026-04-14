library(testthat)

# FIQT sign + shrinkage monotonicity — RED until Plan 09-03 Task 1 creates
# src/snakemake/scripts/run_fiqt.R.

test_that("FIQT shrinks to zero at z=0 and approaches beta_raw at z->inf", {
  skip_if_not_installed("winnerscurse")
  skip_if_not(
    file.exists("src/snakemake/scripts/run_fiqt.R"),
    "run_fiqt.R not yet created (Plan 09-03)"
  )
  source("src/snakemake/scripts/run_fiqt.R")

  # High z (z=10): shrinkage should be < 5%
  df_high <- data.frame(rsid = "rs1", beta = 0.5, se = 0.05, n = 100000)
  res_high <- apply_fiqt(df_high)
  expect_gt(abs(res_high$beta_FIQT) / abs(df_high$beta), 0.95)

  # Low z (z=1.5): shrinkage should be substantial
  df_low <- data.frame(rsid = "rs2", beta = 0.075, se = 0.05, n = 100000)
  res_low <- apply_fiqt(df_low)
  expect_lt(abs(res_low$beta_FIQT) / abs(df_low$beta), 0.8)
})

test_that("FIQT preserves effect direction (sign)", {
  skip_if_not(
    file.exists("src/snakemake/scripts/run_fiqt.R"),
    "run_fiqt.R not yet created (Plan 09-03)"
  )
  source("src/snakemake/scripts/run_fiqt.R")
  df <- data.frame(
    rsid = c("rs1", "rs2", "rs3"),
    beta = c(0.3, -0.2, 0.15),
    se = c(0.05, 0.05, 0.08),
    n = c(100000, 100000, 100000)
  )
  res <- apply_fiqt(df)
  expect_equal(sign(res$beta_FIQT), sign(df$beta))
})
