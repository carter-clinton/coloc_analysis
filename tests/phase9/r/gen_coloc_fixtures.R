#!/usr/bin/env Rscript
# One-shot fixture generator for Plan 09-04 Task 1 coloc replication tests.
#
# Creates tests/phase9/fixtures/mock_disc.fit.rds + mock_rep.fit.rds using
# coloc::runsusie(suffix=<n>) on synthetic z-scores + identity LD for 20 SNPs,
# L=3, shared causal variant at index 10. runsusie() ensures the saved fits
# carry the coloc:::annotate_susie attributes needed for downstream
# coloc::coloc.susie S3 dispatch (mirrors the Phase-1 .fit.rds convention used
# by run_susie_rss.R).
#
# Idempotent: running twice overwrites the two .rds files with byte-identical
# payloads (set.seed(42) + deterministic LD).

suppressPackageStartupMessages({
  library(coloc)
  library(susieR)
})

set.seed(42)
p <- 20L
L <- 3L
LD <- diag(p)
rownames(LD) <- colnames(LD) <- paste0("snp", seq_len(p))

# Discovery: causal at SNP 10, strong z ~ 6
z_disc <- rnorm(p, mean = 0, sd = 1)
z_disc[10] <- 6.0
names(z_disc) <- rownames(LD)

# Replication: same causal at SNP 10, attenuated z ~ 4
z_rep <- rnorm(p, mean = 0, sd = 1)
z_rep[10] <- 4.0
names(z_rep) <- rownames(LD)

# Build coloc-format dataset and fit via runsusie so the returned object
# carries the coloc:::annotate_susie attributes needed by coloc.susie.
# We synthesize beta/varbeta from z: beta=z*se, se=1/sqrt(N) standard form,
# then pass to runsusie. The suffix argument distinguishes the two fits so
# coloc.susie(disc, rep) can pair them unambiguously.
n_disc <- 50000L
n_rep  <- 50000L
se_common <- 1 / sqrt(n_disc)

build_D <- function(z, snps, n) {
  list(
    beta = z * se_common,
    varbeta = rep(se_common^2, length(z)),
    snp = snps,
    position = seq_along(z),
    type = "quant",
    LD = LD,
    N = n,
    sdY = 1
  )
}

D_disc <- build_D(z_disc, rownames(LD), n_disc)
D_rep  <- build_D(z_rep,  rownames(LD), n_rep)

fit_disc <- coloc::runsusie(D_disc, suffix = 1L, L = L, coverage = 0.95)
fit_rep  <- coloc::runsusie(D_rep,  suffix = 2L, L = L, coverage = 0.95)

out_dir <- "tests/phase9/fixtures"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
saveRDS(fit_disc, file.path(out_dir, "mock_disc.fit.rds"))
saveRDS(fit_rep,  file.path(out_dir, "mock_rep.fit.rds"))
cat(sprintf("Fixtures written to %s/ (mock_disc.fit.rds, mock_rep.fit.rds)\n", out_dir))
