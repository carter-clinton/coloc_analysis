#!/usr/bin/env Rscript
# A2 identity payload from the A3 panel (D-01, Pattern 3): the same variants frame and an explicit R = I.
# Not the k2d R = NULL payload: the declared-mode loader rejects use_identity, and an R = NULL fit is
# not panel-restricted (Pitfall 7). No `status` field, so the loader labels it ld_loaded like A3.
suppressPackageStartupMessages(library(optparse))

opt <- parse_args(OptionParser(option_list = list(make_option("--in"), make_option("--out"))))
src <- readRDS(opt$`in`)
if (is.null(src$R)) stop("A3 panel has no R matrix: ", opt$`in`)
if (!all(c("REF", "ALT") %in% names(src$variants))) stop("A3 panel variants lack REF/ALT: ", opt$`in`)
n <- nrow(src$R)
if (nrow(src$variants) != n) stop(sprintf("A3 panel R is %d x %d but variants has %d rows", n, n, nrow(src$variants)))

payload <- list(R = diag(n), variants = src$variants, ld_source = "identity_matched_r4")
dir.create(dirname(opt$out), recursive = TRUE, showWarnings = FALSE)
saveRDS(payload, opt$out)
cat(sprintf("identity payload %s: n=%d from %s\n", opt$out, n, opt$`in`))
