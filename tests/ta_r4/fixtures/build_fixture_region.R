#!/usr/bin/env Rscript
# Fixture region for the frozen-script e2e tests (W0c). Generated at test time; nothing binary is committed.
# 400 genotypes x 60 SNPs in 3 LD blocks, 2 causal SNPs, 1 transposed-allele SNP, 1 palindromic SNP.
# Writes: panel .rds (plink_ld_to_rds.R shape + REF/ALT, REF := A2, ALT := A1), bgzipped + tabix-indexed
# sumstats (hypertension.EUR.tsv.bgz columns), variant catalog TSV, regions CSV.
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
})

opt <- parse_args(OptionParser(option_list = list(
  make_option("--panel"), make_option("--sumstats"), make_option("--catalog"), make_option("--regions"),
  make_option("--region-id", default = "FIX_1"), make_option("--chr", default = "1"),
  make_option("--start", type = "integer", default = 1000L),
  make_option("--bgzip"), make_option("--tabix")
)))

set.seed(20261021)
n <- 400L; m <- 60L; block <- rep(1:3, each = 20L)
CAUSAL <- c(5L, 45L); TRANSPOSED <- 8L; PALINDROMIC <- 30L

hap <- function() {
  u <- matrix(rnorm(n * 3L), n, 3L)
  q <- qnorm(1 - seq(0.15, 0.45, length.out = m))
  sapply(seq_len(m), function(j) as.integer(0.85 * u[, block[j]] + sqrt(1 - 0.85^2) * rnorm(n) > q[j]))
}
G <- hap() + hap()                       # ALT dosage
X <- scale(G)
y <- 0.5 * X[, CAUSAL[1]] + 0.4 * X[, CAUSAL[2]] + rnorm(n)
fits <- t(sapply(seq_len(m), function(j) summary(lm(y ~ G[, j]))$coefficients[2, c(1, 2, 4)]))

pairs <- list(c("A", "C"), c("A", "G"), c("C", "T"), c("G", "T"), c("C", "A"), c("G", "A"))
ref <- character(m); alt <- character(m)
for (j in seq_len(m)) { p <- pairs[[(j - 1L) %% length(pairs) + 1L]]; ref[j] <- p[1]; alt[j] <- p[2] }
ref[PALINDROMIC] <- "A"; alt[PALINDROMIC] <- "T"
ref[TRANSPOSED] <- "A"; alt[TRANSPOSED] <- "G"

pos <- opt$start + 1000L * (seq_len(m) - 1L)
chr <- as.character(opt$chr)
R <- cor(G); dimnames(R) <- NULL
variants <- data.frame(SNP_ID = sprintf("rs%d", 9000000L + seq_len(m)), CHR = chr, POS = pos,
                       A1 = alt, A2 = ref, REF = ref, ALT = alt, stringsAsFactors = FALSE)
dir.create(dirname(opt$panel), recursive = TRUE, showWarnings = FALSE)
saveRDS(list(R = R, variants = variants, ld_source = "fixture_r4", region_id = opt$`region-id`,
             ancestry = "EUR"), opt$panel)

eaf <- colMeans(G) / 2
ss <- data.table(CHR = chr, POS = pos, REF = ref, ALT = alt, BETA = fits[, 1], SE = fits[, 2], P = fits[, 3],
                 EAF = eaf, N = n, SNP_ID = sprintf("%s:%d", chr, pos), TRAIT = "hypertension",
                 ANCESTRY = "EUR", BUILD = "GRCh37")
# Transposed in the sumstats: alleles swapped, effect and frequency re-signed to the other allele.
ss[TRANSPOSED, `:=`(REF = alt[TRANSPOSED], ALT = ref[TRANSPOSED], BETA = -BETA, EAF = 1 - EAF)]

dir.create(dirname(opt$sumstats), recursive = TRUE, showWarnings = FALSE)
plain <- sub("\\.bgz$", "", opt$sumstats)
fwrite(ss, plain, sep = "\t")
stopifnot(system2(opt$bgzip, c("-f", "-c", plain), stdout = opt$sumstats) == 0)
unlink(plain)
stopifnot(system2(opt$tabix, c("-f", "-s", "1", "-b", "2", "-e", "2", "-S", "1", opt$sumstats)) == 0)

dir.create(dirname(opt$catalog), recursive = TRUE, showWarnings = FALSE)
fwrite(ss[, .(CHR, POS, REF, ALT, SNP_ID)], opt$catalog, sep = "\t")

dir.create(dirname(opt$regions), recursive = TRUE, showWarnings = FALSE)
fwrite(data.table(region_id = opt$`region-id`, ancestry = "EUR", chr = chr, start = opt$start,
                  end = opt$start + 60000L, lead_snp = variants$SNP_ID[CAUSAL[1]], gene = "FIX",
                  trait_list = "hypertension", source = "fixture", canonical_pairs = ""),
       opt$regions)
cat(sprintf("fixture %s: %d variants, causal %s, transposed %d, palindromic %d\n",
            opt$`region-id`, m, paste(CAUSAL, collapse = ","), TRANSPOSED, PALINDROMIC))
