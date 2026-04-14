library(testthat)

# Wave-4 tests for Plan 09-04 Task 1 — run_replication_coloc_susie.R wrapper.
#
# testthat::test_file() changes cwd into the test file's directory, so relative
# paths to project-root artifacts must walk up. `.locate()` mirrors the
# Wave-3 pattern documented in test_fiqt.R (candidate-list resolver).

.locate <- function(relpath) {
  for (prefix in c("", "../", "../../", "../../../")) {
    candidate <- file.path(prefix, relpath)
    if (file.exists(candidate)) return(normalizePath(candidate))
  }
  NA_character_
}

test_that("run_replication_coloc emits PP.H4 sweep booleans on mock paired fits", {
  skip_if_not_installed("coloc")
  skip_if_not_installed("jsonlite")

  script <- .locate("src/snakemake/scripts/run_replication_coloc_susie.R")
  skip_if_not(!is.na(script), "run_replication_coloc_susie.R not found — Plan 09-04 Task 1 not yet implemented")

  disc <- .locate("tests/phase9/fixtures/mock_disc.fit.rds")
  rep  <- .locate("tests/phase9/fixtures/mock_rep.fit.rds")
  skip_if_not(!is.na(disc) && !is.na(rep),
              "fixtures missing — run Rscript tests/phase9/r/gen_coloc_fixtures.R first")

  source(script, local = TRUE)

  tmp <- tempfile(fileext = ".json")
  res_invis <- run_replication_coloc(
    disc_fit_path = disc,
    rep_fit_path  = rep,
    signal_id = "mock_sig",
    cohort = "mock_cohort",
    pph4_thresholds = c(0.5, 0.7, 0.8, 0.9),
    output_json = tmp
  )

  expect_true(file.exists(tmp))
  res <- jsonlite::fromJSON(tmp)

  # Schema: all 4 sweep columns present
  expect_true("replicated_pph4_0.5" %in% names(res))
  expect_true("replicated_pph4_0.7" %in% names(res))
  expect_true("replicated_pph4_0.8" %in% names(res))
  expect_true("replicated_pph4_0.9" %in% names(res))

  # Success flag present
  expect_true("coloc_succeeded" %in% names(res))
  expect_true(res$coloc_succeeded)

  # pph4_best in [0, 1]
  expect_true("pph4_best" %in% names(res))
  expect_gte(res$pph4_best, 0)
  expect_lte(res$pph4_best, 1)

  # Sweep booleans consistent with pph4_best
  expect_identical(res$replicated_pph4_0.5, res$pph4_best >= 0.5)
  expect_identical(res$replicated_pph4_0.9, res$pph4_best >= 0.9)
})

test_that("run_replication_coloc emits coloc_succeeded=FALSE on readRDS failure", {
  skip_if_not_installed("jsonlite")

  script <- .locate("src/snakemake/scripts/run_replication_coloc_susie.R")
  skip_if_not(!is.na(script), "run_replication_coloc_susie.R not found")
  source(script, local = TRUE)

  tmp <- tempfile(fileext = ".json")
  # Non-existent files — coloc.susie will never be called, readRDS will error.
  res <- run_replication_coloc(
    disc_fit_path = "/nonexistent/a.fit.rds",
    rep_fit_path  = "/nonexistent/b.fit.rds",
    signal_id = "sig_fail",
    cohort = "coh",
    pph4_thresholds = c(0.5, 0.7, 0.8, 0.9),
    output_json = tmp
  )
  expect_true(file.exists(tmp))
  parsed <- jsonlite::fromJSON(tmp)
  expect_false(parsed$coloc_succeeded)
})

# Preserve the original RED marker test (TCF7L2 smoke) under its pre-execution
# skip — it will unlock when Phase-1 discovery and Wave-3 replication fits
# materialize on disk for the real TCF7L2 region.
test_that("coloc.susie on TCF7L2/T2D discovery+replication pair returns PP.H4 > 0.8", {
  skip_if_not_installed("coloc")
  skip_if_not_installed("susieR")
  disc_path <- .locate("results/fine_mapping/t2d_EUR_chr10_tcf7l2.fit.rds")
  skip_if_not(!is.na(disc_path),
              "Phase 1 discovery fit not present (pre-execution)")
  rep_path <- .locate("results/replication/fits/t2d_EUR_chr10_tcf7l2_finngen_r12.fit.rds")
  skip_if_not(!is.na(rep_path),
              "replication fit not yet generated (Plan 09-03)")
  disc_fit <- readRDS(disc_path)
  rep_fit <- readRDS(rep_path)
  res <- coloc::coloc.susie(disc_fit, rep_fit)
  expect_gt(max(res$summary$PP.H4.abf), 0.8)
})
