# A6 resolution: coloc.susie accepts susie_rss output after saveRDS/readRDS roundtrip?
suppressPackageStartupMessages({ library(testthat); library(susieR); library(coloc) })

synth_fit <- function(seed, signal_idx = 50) {
  set.seed(seed); n_var <- 100
  R <- cov2cor(crossprod(matrix(rnorm(n_var * 500), nrow = 500)))
  z <- rnorm(n_var); z[signal_idx] <- 5.5
  fit <- susie_rss(z = z, R = R, n = 20000, L = 5, max_iterations = 200)
  if (!inherits(fit, "susie")) class(fit) <- c("susie", class(fit))
  fit
}

test_that("A6 dispatch: raw susie_rss fits are rejected by coloc.susie (expected; drives fallback)", {
  # This test documents the A6 resolution branch: raw susie_rss fits lack the
  # annotated metadata (named pip, named sets, sld) that coloc.susie expects.
  # Run_susie_rss.R applies coloc:::annotate_susie() before saveRDS to fix this
  # (see positive test below). Keeping this as an explicit expect_error ensures
  # the dispatch decision is recorded in the test suite itself.
  fit_a <- synth_fit(1); fit_b <- synth_fit(2)
  expect_error(
    coloc::coloc.susie(fit_a, fit_b),
    regexp = "data\\.table|is\\.data\\.table"
  )
})

test_that("A6 fallback: annotate_susie-wrapped fits roundtrip and work with coloc.susie", {
  fit_a <- synth_fit(1); fit_b <- synth_fit(2)
  n_var <- length(fit_a$pip)
  snp_names <- sprintf("snp%03d", seq_len(n_var))
  set.seed(1); R_a <- cov2cor(crossprod(matrix(rnorm(n_var * 500), nrow = 500)))
  set.seed(2); R_b <- cov2cor(crossprod(matrix(rnorm(n_var * 500), nrow = 500)))

  fit_a_ann <- coloc:::annotate_susie(fit_a, snp_names, R_a)
  fit_b_ann <- coloc:::annotate_susie(fit_b, snp_names, R_b)

  tmp_a <- tempfile(fileext = ".fit.rds"); saveRDS(fit_a_ann, tmp_a)
  tmp_b <- tempfile(fileext = ".fit.rds"); saveRDS(fit_b_ann, tmp_b)
  fa <- readRDS(tmp_a); fb <- readRDS(tmp_b)
  expect_true(inherits(fa, "susie"))
  expect_false(is.null(fa$sld))
  expect_false(is.null(names(fa$pip)))

  res <- coloc::coloc.susie(fa, fb)
  expect_false(is.null(res$summary))
  expect_true("PP.H4.abf" %in% names(res$summary))
  unlink(c(tmp_a, tmp_b))
})
