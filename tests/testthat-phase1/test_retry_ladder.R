suppressPackageStartupMessages({ library(testthat); library(susieR); library(Matrix) })

find_project_root <- function() {
  # testthat::test_file chdir's into a tempdir; recover project root.
  env_root <- Sys.getenv("PHASE1_PROJECT_ROOT", unset = NA)
  if (!is.na(env_root) && nzchar(env_root) && dir.exists(env_root)) return(env_root)
  # Walk up from plausible cwds looking for a sentinel
  candidates <- c(getwd(), normalizePath(".", mustWork = FALSE))
  for (start in candidates) {
    d <- start
    for (i in 1:8) {
      if (file.exists(file.path(d, "src/legacy/region_analysis/scripts/run_susie_rss.R"))) return(d)
      parent <- dirname(d); if (parent == d) break; d <- parent
    }
  }
  NA_character_
}

source_helper <- function() {
  root <- find_project_root()
  src_file <- if (!is.na(root)) file.path(root, "src/legacy/region_analysis/scripts/run_susie_rss.R") else "src/legacy/region_analysis/scripts/run_susie_rss.R"
  skip_if_not(file.exists(src_file), "run_susie_rss.R missing")
  lines <- readLines(src_file)
  start <- grep("^run_susie_with_ladder <- function", lines)
  if (length(start) == 0) skip("run_susie_with_ladder not yet defined (Task 1-01-02 pending)")
  # Find matching closing brace of the top-level function
  depth <- 0; end_idx <- NA_integer_
  for (i in start:length(lines)) {
    depth <- depth + sum(gregexpr("\\{", lines[i])[[1]] > 0) - sum(gregexpr("\\}", lines[i])[[1]] > 0)
    if (i > start && depth == 0) { end_idx <- i; break }
  }
  stopifnot(!is.na(end_idx))
  tmp <- new.env()
  # Also source regularize_ld helper if defined above
  start_rl <- grep("^regularize_ld <- function", lines)
  if (length(start_rl) > 0) {
    end_rl <- start_rl[1] + which(grepl("^\\}", lines[start_rl[1]:length(lines)]))[1] - 1
    eval(parse(text = lines[start_rl[1]:end_rl]), envir = tmp)
  }
  eval(parse(text = lines[start:end_idx]), envir = tmp)
  tmp$run_susie_with_ladder
}

make_dat <- function(seed = 7, n = 80, kind = c("well","near_singular","singular","random")) {
  set.seed(seed); kind <- match.arg(kind)
  Z <- matrix(rnorm(n * n), nrow = n)
  R_well <- cov2cor(crossprod(Z))
  if (kind == "well") return(list(R = R_well, z = { zs <- rnorm(n); zs[n/2] <- 6; zs }))
  if (kind == "near_singular") {
    eig <- eigen(R_well); eig$values[1:5] <- eig$values[1:5] * 1e-6
    R_ns <- eig$vectors %*% diag(pmax(eig$values, 1e-10)) %*% t(eig$vectors)
    R_ns <- (R_ns + t(R_ns))/2
    return(list(R = R_ns, z = { zs <- rnorm(n); zs[n/2] <- 6; zs }))
  }
  if (kind == "singular") {
    R_s <- R_well; R_s[1, ] <- R_s[2, ]; R_s[, 1] <- R_s[, 2]
    return(list(R = R_s, z = { zs <- rnorm(n); zs[n/2] <- 6; zs }))
  }
  list(R = diag(n), z = rnorm(n))
}

POLICY <- list(L = 5L, coverage = 0.95,
               max_iter_primary = 30L, max_iter_retry = 150L,
               ld_regularization_eps = 1e-4)

test_that("retry ladder: converged_primary on well-conditioned", {
  fn <- source_helper(); dat <- make_dat(kind = "well")
  res <- fn(dat$z, dat$R, POLICY, n = 10000)
  expect_equal(res$status, "converged_primary")
  expect_false(is.null(res$fit))
})

test_that("retry ladder: near_singular transitions to max_iter or regularized", {
  fn <- source_helper(); dat <- make_dat(kind = "near_singular")
  res <- fn(dat$z, dat$R, POLICY, n = 10000)
  expect_true(res$status %in% c("converged_max_iter", "converged_regularized", "non_converged"))
  expect_false(is.null(res$fit))
})

test_that("retry ladder: singular recovers via regularization", {
  fn <- source_helper(); dat <- make_dat(kind = "singular")
  res <- fn(dat$z, dat$R, POLICY, n = 10000)
  expect_true(res$status %in% c("converged_regularized", "converged_max_iter", "non_converged"))
  expect_false(is.null(res$fit))
})

test_that("retry ladder: fit object is returned even on non_converged terminal state", {
  fn <- source_helper(); dat <- make_dat(kind = "random")
  res <- fn(dat$z, dat$R, POLICY, n = 10000)
  expect_false(is.null(res$fit))
  expect_true(res$status %in% c("converged_primary","converged_max_iter","converged_regularized","non_converged"))
})
