#!/usr/bin/env Rscript
# Two-trait fixture region for the R4 coloc tests (W0d). Generated at test time; nothing binary is committed.
# Same genotype shape as build_fixture_region.R (400 x 60 SNPs, 3 LD blocks, transposed SNP 8, palindromic SNP 30).
# Trait A: causal SNPs 5 and 45 (two credible sets). Trait B: causal SNP 5 (one CS), or none with --b-null.
# Trait B also carries SNP 12 with alleles transposed against the catalog and SNP 20 with missing alleles,
# so the frozen script's allele-keyed catalog join drops both from B's fit (A1 all-variants keeps them).
# Writes: panel .rds (REF/ALT, SNP_ID style --panel-snpid), PLAIN TSV sumstats for A and B (the caller
# concatenates regions and bgzips), the variant catalog TSV.
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
})

opt <- parse_args(OptionParser(option_list = list(
  make_option("--panel"), make_option("--sumstats-a"), make_option("--sumstats-b"), make_option("--catalog"),
  make_option("--region-id"), make_option("--chr", default = "1"),
  make_option("--start", type = "integer", default = 1000L),
  make_option("--seed", type = "integer", default = 20261021L),
  make_option("--a-snpid", default = "rsid"), make_option("--b-snpid", default = "chrpos"),
  make_option("--panel-snpid", default = "chrpos"),
  make_option("--b-null", action = "store_true", default = FALSE),
  make_option("--trait-a", default = "asthma"), make_option("--trait-b", default = "bmi")
)))

set.seed(opt$seed)
n <- 400L; m <- 60L; block <- rep(1:3, each = 20L)
TRANSPOSED <- 8L; PALINDROMIC <- 30L; B_TRANSPOSED <- 12L; B_NO_ALLELES <- 20L

hap <- function() {
  u <- matrix(rnorm(n * 3L), n, 3L)
  q <- qnorm(1 - seq(0.15, 0.45, length.out = m))
  sapply(seq_len(m), function(j) as.integer(0.85 * u[, block[j]] + sqrt(1 - 0.85^2) * rnorm(n) > q[j]))
}
G <- hap() + hap()
X <- scale(G)
y_a <- 0.5 * X[, 5] + 0.4 * X[, 45] + rnorm(n)
y_b <- if (opt$`b-null`) rnorm(n) else 0.5 * X[, 5] + rnorm(n)
gwas <- function(y) t(sapply(seq_len(m), function(j) summary(lm(y ~ G[, j]))$coefficients[2, c(1, 2, 4)]))

pairs <- list(c("A", "C"), c("A", "G"), c("C", "T"), c("G", "T"), c("C", "A"), c("G", "A"))
ref <- character(m); alt <- character(m)
for (j in seq_len(m)) { p <- pairs[[(j - 1L) %% length(pairs) + 1L]]; ref[j] <- p[1]; alt[j] <- p[2] }
ref[PALINDROMIC] <- "A"; alt[PALINDROMIC] <- "T"
ref[TRANSPOSED] <- "A"; alt[TRANSPOSED] <- "G"

pos <- opt$start + 1000L * (seq_len(m) - 1L)
chr <- as.character(opt$chr)
cp <- sprintf("%s:%d", chr, pos)
rsid <- sprintf("rs%d", 9000000L + (opt$seed %% 1000L) * 100L + seq_len(m))
ids <- function(style) switch(style, rsid = rsid, chrpos = cp, stop("snpid style must be rsid|chrpos"))

R <- cor(G); dimnames(R) <- NULL
variants <- data.frame(SNP_ID = ids(opt$`panel-snpid`), CHR = chr, POS = pos,
                       A1 = alt, A2 = ref, REF = ref, ALT = alt, stringsAsFactors = FALSE)
dir.create(dirname(opt$panel), recursive = TRUE, showWarnings = FALSE)
saveRDS(list(R = R, variants = variants, ld_source = "fixture_r4", region_id = opt$`region-id`,
             ancestry = "EUR"), opt$panel)

eaf <- colMeans(G) / 2
sumstats <- function(y, trait, style) {
  f <- gwas(y)
  ss <- data.table(CHR = chr, POS = pos, REF = ref, ALT = alt, BETA = f[, 1], SE = f[, 2], P = f[, 3],
                   EAF = eaf, N = n, SNP_ID = ids(style), TRAIT = trait, ANCESTRY = "EUR", BUILD = "GRCh37")
  ss[TRANSPOSED, `:=`(REF = alt[TRANSPOSED], ALT = ref[TRANSPOSED], BETA = -BETA, EAF = 1 - EAF)]
  ss
}
ss_a <- sumstats(y_a, opt$`trait-a`, opt$`a-snpid`)
ss_b <- sumstats(y_b, opt$`trait-b`, opt$`b-snpid`)
ss_b[B_TRANSPOSED, `:=`(REF = ALT, ALT = REF, BETA = -BETA, EAF = 1 - EAF)]
ss_b[B_NO_ALLELES, `:=`(REF = NA_character_, ALT = NA_character_)]

for (x in list(list(ss_a, opt$`sumstats-a`), list(ss_b, opt$`sumstats-b`))) {
  dir.create(dirname(x[[2]]), recursive = TRUE, showWarnings = FALSE)
  fwrite(x[[1]], x[[2]], sep = "\t", na = "")
}
dir.create(dirname(opt$catalog), recursive = TRUE, showWarnings = FALSE)
fwrite(ss_a[, .(CHR, POS, REF, ALT, SNP_ID)], opt$catalog, sep = "\t")
cat(sprintf("fixture pair %s chr%s seed %d: A=%s(%s) B=%s(%s%s) panel ids %s\n", opt$`region-id`, chr, opt$seed,
            opt$`trait-a`, opt$`a-snpid`, opt$`trait-b`, opt$`b-snpid`, if (opt$`b-null`) ", null" else "",
            opt$`panel-snpid`))
