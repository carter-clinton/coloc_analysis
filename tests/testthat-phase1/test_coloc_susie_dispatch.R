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

test_that("coloc.susie dispatches on susie_rss output without warning or silent refit", {
  fit_a <- synth_fit(1); fit_b <- synth_fit(2)
  tmp_a <- tempfile(fileext = ".fit.rds"); saveRDS(fit_a, tmp_a)
  tmp_b <- tempfile(fileext = ".fit.rds"); saveRDS(fit_b, tmp_b)
  fa <- readRDS(tmp_a); fb <- readRDS(tmp_b)
  expect_true(inherits(fa, "susie")); expect_true(inherits(fb, "susie"))

  old_warn <- options(warn = 2); on.exit(options(old_warn))
  res <- tryCatch(
    coloc::coloc.susie(fa, fb),
    error = function(e) {
      stop(paste0("A6 FALLBACK REQUIRED: coloc.susie rejected susie_rss roundtrip. ",
                  "Switch run_susie_rss.R to call coloc::runsusie() instead. ",
                  "Original error: ", conditionMessage(e)))
    }
  )
  expect_false(is.null(res$summary))
  expect_true("PP.H4.abf" %in% names(res$summary))
  unlink(c(tmp_a, tmp_b))
})
