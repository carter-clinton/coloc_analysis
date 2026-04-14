library(testthat)

# RED until Plan 09-03 Task 2 + Plan 09-04 Task 1 populate replication
# fits and coloc results for TCF7L2/T2D.

test_that("coloc.susie on TCF7L2/T2D discovery+replication pair returns PP.H4 > 0.8", {
  skip_if_not_installed("coloc")
  skip_if_not_installed("susieR")
  disc_path <- "results/fine_mapping/t2d_EUR_chr10_tcf7l2.fit.rds"
  skip_if_not(
    file.exists(disc_path),
    "Phase 1 discovery fit not present (pre-execution)"
  )
  rep_path <- "results/replication/fits/t2d_EUR_chr10_tcf7l2_finngen_r12.fit.rds"
  skip_if_not(
    file.exists(rep_path),
    "replication fit not yet generated (Plan 09-03)"
  )
  disc_fit <- readRDS(disc_path)
  rep_fit <- readRDS(rep_path)
  res <- coloc::coloc.susie(disc_fit, rep_fit)
  expect_gt(max(res$summary$PP.H4.abf), 0.8)
})
