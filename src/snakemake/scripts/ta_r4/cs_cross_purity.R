#!/usr/bin/env Rscript
# Cross-evaluated credible-set purity (Pitfall 9): for each CS of a SuSiE fit, the minimum |r| among its members
# under the LD matrix of --panel (e.g. A2 identity-LD sets scored against EUR_1kg_r4). A fit variant name maps
# to the panel row whose SNP_ID equals it, else to the unique row with that CHR:POS. Ambiguous members are errors.
# Unmatched members are errors unless --allow-absent (panels with different variant sets); then they are counted
# (n_present < n_cs_variants, note partial_present) and a CS with fewer than min(2, size) members present has NA
# purity (note fewer_than_2_present).
# Output TSV: cs, size, n_cs_variants, n_present, min_abs_corr, mean_abs_corr, purity_fit, note.
suppressPackageStartupMessages(library(optparse))

fail <- function(code, ...) stop(sprintf("%s: %s", code, sprintf(...)), call. = FALSE)

opt <- parse_args(OptionParser(option_list = list(
  make_option("--fit"), make_option("--panel"), make_option("--output"),
  make_option("--allow-absent", action = "store_true", default = FALSE))))
for (k in c("fit", "panel", "output")) if (is.null(opt[[k]])) fail("ARGS", "--%s is required", k)

fit <- readRDS(opt$fit)
panel <- readRDS(opt$panel)
R <- panel$R
v <- panel$variants
if (is.null(R) || is.null(v) || nrow(R) != nrow(v)) fail("PANEL", "%s lacks R/variants of equal size", opt$panel)
nm <- colnames(fit$lbf_variable)
if (is.null(nm)) fail("FIT_UNNAMED", "%s has no variant names", opt$fit)
cp <- paste0(sub("^chr", "", as.character(v$CHR)), ":", as.integer(v$POS))

panel_index <- function(name) {
  i <- which(as.character(v$SNP_ID) == name)
  if (length(i) == 1) return(i)
  if (length(i) > 1) fail("AMBIGUOUS", "%s matches %d panel SNP_IDs", name, length(i))
  i <- which(cp == sub("^chr", "", name))
  if (length(i) == 1) return(i)
  if (length(i) > 1) fail("AMBIGUOUS", "%s matches %d panel rows by CHR:POS", name, length(i))
  if (isTRUE(opt$`allow-absent`)) return(NA_integer_)
  fail("UNMATCHED", "fit variant %s is not in panel %s", name, opt$panel)
}

cs <- fit$sets$cs
pur <- fit$sets$purity
rows <- lapply(seq_along(cs), function(k) {
  all_idx <- vapply(nm[cs[[k]]], panel_index, integer(1))
  idx <- all_idx[!is.na(all_idx)]
  size <- length(all_idx)
  few <- length(idx) < min(2L, size)
  a <- abs(R[idx, idx, drop = FALSE])
  off <- a[upper.tri(a)]
  note <- if (few) "fewer_than_2_present" else if (length(idx) < size) "partial_present" else ""
  data.frame(cs = if (is.null(names(cs))) paste0("L", k) else names(cs)[k], size = size, n_cs_variants = size,
             n_present = length(idx),
             min_abs_corr = if (few) NA_real_ else if (length(off)) min(off) else 1,
             mean_abs_corr = if (few) NA_real_ else if (length(off)) mean(off) else 1,
             purity_fit = if (!is.null(pur$min.abs.corr)) pur$min.abs.corr[k] else NA_real_, note = note)
})
out <- if (length(rows)) do.call(rbind, rows) else
  data.frame(cs = character(), size = integer(), n_cs_variants = integer(), n_present = integer(),
             min_abs_corr = numeric(), mean_abs_corr = numeric(), purity_fit = numeric(), note = character())
tmp <- paste0(opt$output, ".tmp")
write.table(out, tmp, sep = "\t", quote = FALSE, row.names = FALSE, na = "NA")
file.rename(tmp, opt$output)
