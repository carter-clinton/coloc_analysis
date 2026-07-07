# src/R/regularization/psd_utils.R
# Canonical positive-semi-definite (PSD) regularization utilities.
#
# These are the r3 PSD methods pre-registered for the EUR panel under
# osf-amendment-r3-2026-05-04.md:
#   - psd_regularize_ridge   : Wen et al. 2017 ridge (R_reg = R + lambda*I, then
#                              row-and-column normalize so diag = 1).
#   - psd_regularize_eigclip : Hutchinson 2020 eigenvalue-clip (clip eigenvalues to
#                              lambda_floor = 1e-6, reconstruct, row-col normalize).
#
# Extracted VERBATIM (identical bodies) from
# src/R/regularization/refit_sh2b3_psd_regularized.R lines 71-87 so this file is the
# SINGLE canonical definition consumed by BOTH the EUR r3 SuSiE-RSS refit AND the
# AFR native-plink LD panel conditioning pre-registered under
# osf-amendment-afr-native-ld-nan-psd-2026-07-03.md (which extends the r3 PSD scope
# to AFR and does NOT alter these numerics).
#
# Track-A sensitivity: the r3 / EUR numerics MUST NOT change. Byte-identity of the
# extraction is gated by tests/testthat-phase1/test_psd_utils_byte_identical.R
# (identical() vs a frozen golden captured from the pre-refactor inline source, plus
# a verbatim in-test cross-check). Do NOT add a third PSD implementation or alter the
# function bodies, lambda semantics, or row/col normalization.

# -------------------------------------------------------------------------
# PSD regularization functions
# Wen 2017 ridge: R_reg = R + lambda * I; then row-and-column normalize so diag(R_reg) = 1
psd_regularize_ridge <- function(R, lambda) {
  R_reg <- R + lambda * diag(nrow(R))
  d <- sqrt(diag(R_reg))
  R_reg <- sweep(sweep(R_reg, 1, d, "/"), 2, d, "/")
  R_reg
}

# Hutchinson 2020 eigenvalue-clip: clip negative eigenvalues to lambda_floor (default 1e-6),
# reconstruct R_clip = V * diag(max(d, lambda_floor)) * V^T, then row-col normalize.
psd_regularize_eigclip <- function(R, lambda_floor = 1e-6) {
  e <- eigen(R, symmetric = TRUE)
  d_clip <- pmax(e$values, lambda_floor)
  R_clip <- e$vectors %*% diag(d_clip) %*% t(e$vectors)
  d <- sqrt(diag(R_clip))
  R_clip <- sweep(sweep(R_clip, 1, d, "/"), 2, d, "/")
  R_clip
}
