# tests/testthat-phase1/test_fit_roundtrip.R
# Validates G1 fit persistence: saveRDS/readRDS preserves SuSiE class + structure.
# Guards against Pitfall 1 (class stripping on roundtrip).
suppressPackageStartupMessages({ library(testthat); library(susieR) })

test_that("susie_rss fit roundtrips via saveRDS/readRDS preserving class", {
  set.seed(42)
  n_var <- 100
  R <- cov2cor(crossprod(matrix(rnorm(n_var * 200), nrow = 200)))
  z <- rnorm(n_var); z[50] <- 5.0
  fit <- susie_rss(z = z, R = R, n = 10000, L = 5, max_iterations = 100)
  expect_true(inherits(fit, "susie"))

  tmp <- tempfile(fileext = ".fit.rds")
  saveRDS(fit, tmp)
  fit2 <- readRDS(tmp)
  expect_true(inherits(fit2, "susie"))
  expect_false(is.null(fit2$sets))
  expect_true(is.numeric(fit2$pip))
  expect_equal(length(fit2$pip), n_var)
  unlink(tmp)
})
