#!/usr/bin/env Rscript
# Cross-evaluated credible-set purity (Pitfall 9): for each CS of a SuSiE fit, the minimum |r| among its members
# under the LD matrix of --panel (e.g. A2 identity-LD sets scored against EUR_1kg_r4).
# Each member is resolved to its allele key through what the fit was built from (variant_match.R
# resolve_fit_names: --fit-sumstats rows in the --region-id window that are in --fit-catalog and kept by
# --fit-panel, else the --fit-panel rsid, else a unique CHR:POS in --fit-panel; a `.N` duplicate row is
# DUPLICATE_ROW unless --allow-duplicate-rows, which is for measuring pre-15.5a fits only; a base with several keys
# is an error (REFUSED_MULTI_KEY) unless --allow-duplicate-rows, which takes the (N+1)-th key in catalog order).
# No route is UNRESOLVED. The key is located in --panel by position + alleles (exact,
# swapped, or the strand complement of a non-palindromic SNV): one match is present, several are AMBIGUOUS, none is
# absent. Absent members are errors (UNMATCHED) unless --allow-absent; then they are counted (n_present <
# n_cs_variants, note partial_present) and a CS with fewer than min(2, size) members present has NA purity (note
# fewer_than_2_present). DUPLICATE_ROW, BAD_OCCURRENCE, UNRESOLVED and AMBIGUOUS are errors even under --allow-absent.
# Output TSV: cs, size, n_cs_variants, n_present, min_abs_corr, mean_abs_corr, purity_fit, note, n_route_sumstats,
# n_route_panel, n_route_chrpos, n_match_exact, n_match_swapped, n_match_strand, n_refused_multi_key.
suppressPackageStartupMessages({ library(optparse); library(data.table) })

fail <- function(code, ...) stop(sprintf("%s: %s", code, sprintf(...)), call. = FALSE)
own <- sub("^--file=", "", grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE))
source(file.path(if (length(own)) dirname(normalizePath(own[1])) else "src/snakemake/scripts/ta_r4", "variant_match.R"))

opt <- parse_args(OptionParser(option_list = list(
  make_option("--fit"), make_option("--panel"), make_option("--output"),
  make_option("--allow-absent", action = "store_true", default = FALSE),
  make_option("--fit-sumstats"), make_option("--fit-catalog"), make_option("--region-id"), make_option("--regions-csv"),
  make_option("--fit-panel"), make_option("--allow-duplicate-rows", action = "store_true", default = FALSE))))
for (k in c("fit", "panel", "output", "fit-sumstats", "fit-catalog", "region-id", "regions-csv", "fit-panel")) {
  if (is.null(opt[[k]]) || !nzchar(opt[[k]])) fail("ARGS", "--%s is required", k)
}

fit <- readRDS(opt$fit)
panel <- readRDS(opt$panel)
R <- panel$R
v <- panel$variants
if (is.null(R) || is.null(v) || nrow(R) != nrow(v)) fail("PANEL", "%s lacks R/variants of equal size", opt$panel)
nm <- colnames(fit$lbf_variable)
if (is.null(nm)) fail("FIT_UNNAMED", "%s has no variant names", opt$fit)
fpv <- readRDS(opt$`fit-panel`)$variants
if (is.null(fpv)) fail("FIT_PANEL", "%s has no variants", opt$`fit-panel`)

# the fit's region sumstats: run_susie_rss.R's reader and window (run_coloc_pair_r4.R read_region)
regions <- fread(opt$`regions-csv`, colClasses = "character")
reg <- regions[region_id == opt$`region-id`]
if (nrow(reg) != 1) fail("REGION", "%d rows for %s in %s", nrow(reg), opt$`region-id`, opt$`regions-csv`)
ss <- fread(cmd = sprintf("gunzip -c %s", shQuote(opt$`fit-sumstats`)), colClasses = "character")
if (!all(c("CHR", "POS", "REF", "ALT") %in% names(ss))) fail("SUMSTATS", "%s lacks CHR/POS/REF/ALT", opt$`fit-sumstats`)
ss[, POS := as.numeric(POS)]
ss <- ss[CHR == as.character(reg$chr) & POS >= as.numeric(reg$start) & POS <= as.numeric(reg$end)]
if (!"SNP_ID" %in% names(ss)) ss[, SNP_ID := NA_character_]
ss[SNP_ID == "" | SNP_ID == "NA", SNP_ID := NA_character_]
catalog <- fread(opt$`fit-catalog`, colClasses = "character")
if (!all(c("CHR", "POS", "REF", "ALT") %in% names(catalog))) fail("CATALOG", "%s lacks CHR/POS/REF/ALT", opt$`fit-catalog`)

cs <- fit$sets$cs
pur <- fit$sets$purity
members <- unique(nm[unlist(cs)])
res <- resolve_fit_names(members, ss, catalog, fpv, isTRUE(opt$`allow-duplicate-rows`))
for (code in c("duplicate_row", "refused_multi_key", "bad_occurrence", "unresolved")) {
  b <- res$name[res$status == code]
  if (length(b)) fail(toupper(code), "%d of %d credible-set members of %s (first: %s)", length(b), length(members),
                      opt$fit, paste(head(b, 5), collapse = ", "))
}
res <- res[match(nm, res$name), , drop = FALSE]  # by fit column; NA rows for non-members

# locate each resolved key in --panel by position + alleles
op <- panel_alleles(v)
o_cp <- paste(op$chr, op$pos, sep = ":")
o_miss <- missing_allele(op$ref) | missing_allele(op$alt)
fp_basis <- panel_alleles(fpv)$basis
locate <- function(j) {
  r <- res[j, ]
  rows <- which(o_cp == paste(r$chr, r$pos, sep = ":"))
  if (!length(rows)) return(list(i = NA_integer_, kind = "absent"))
  if (missing_allele(r$ref) || missing_allele(r$alt)) fail("UNRESOLVED", "%s resolves to %s:%s without alleles",
                                                           r$name, r$chr, r$pos)
  key_basis <- if (r$route == "sumstats") "REF/ALT" else fp_basis
  basis <- if (op$basis == "REF/ALT" && key_basis == "REF/ALT") "REF/ALT" else "A1/A2_unordered"
  m <- match_at_position(r$ref, r$alt, op$ref[rows], op$alt[rows], o_miss[rows], basis)
  if (m$status == "ambiguous") fail("AMBIGUOUS", "%s (%s:%s %s/%s) matches %d rows of panel %s", r$name, r$chr, r$pos,
                                    r$ref, r$alt, length(rows), opt$panel)
  if (m$status != "matched") return(list(i = NA_integer_, kind = "absent"))
  list(i = rows[m$j], kind = m$kind)
}

rows <- lapply(seq_along(cs), function(k) {
  mem <- cs[[k]]
  refused <- res$status[mem] == "refused_multi_key"
  loc <- lapply(mem[!refused], function(j) {
    l <- locate(j)
    if (is.na(l$i) && !isTRUE(opt$`allow-absent`)) fail("UNMATCHED", "fit variant %s is not in panel %s", nm[j], opt$panel)
    l
  })
  all_idx <- vapply(loc, function(l) l$i, integer(1))
  kinds <- vapply(loc, function(l) l$kind, character(1))
  idx <- all_idx[!is.na(all_idx)]
  size <- length(mem)
  few <- length(idx) < min(2L, size)
  a <- abs(R[idx, idx, drop = FALSE])
  off <- a[upper.tri(a)]
  note <- if (few) "fewer_than_2_present" else if (length(idx) < size) "partial_present" else ""
  if (any(refused)) note <- paste(c(if (nzchar(note)) note, "refused_multi_key"), collapse = ";")
  route <- res$route[mem][!refused]
  data.frame(cs = if (is.null(names(cs))) paste0("L", k) else names(cs)[k], size = size, n_cs_variants = size,
             n_present = length(idx),
             min_abs_corr = if (few) NA_real_ else if (length(off)) min(off) else 1,
             mean_abs_corr = if (few) NA_real_ else if (length(off)) mean(off) else 1,
             purity_fit = if (!is.null(pur$min.abs.corr)) pur$min.abs.corr[k] else NA_real_, note = note,
             n_route_sumstats = sum(route == "sumstats"), n_route_panel = sum(route == "panel"),
             n_route_chrpos = sum(route == "chrpos"), n_match_exact = sum(kinds == "exact"),
             n_match_swapped = sum(kinds == "swapped"), n_match_strand = sum(kinds == "strand"),
             n_refused_multi_key = sum(refused))
})
out <- if (length(rows)) do.call(rbind, rows) else
  data.frame(cs = character(), size = integer(), n_cs_variants = integer(), n_present = integer(),
             min_abs_corr = numeric(), mean_abs_corr = numeric(), purity_fit = numeric(), note = character(),
             n_route_sumstats = integer(), n_route_panel = integer(), n_route_chrpos = integer(),
             n_match_exact = integer(), n_match_swapped = integer(), n_match_strand = integer(),
             n_refused_multi_key = integer())
tmp <- paste0(opt$output, ".tmp")
write.table(out, tmp, sep = "\t", quote = FALSE, row.names = FALSE, na = "NA")
file.rename(tmp, opt$output)
