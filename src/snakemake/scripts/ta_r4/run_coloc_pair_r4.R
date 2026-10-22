#!/usr/bin/env Rscript
# R4 trait-pair colocalization for one pair_manifest row (D-01, D-02, D-21; Pitfalls 5 and 8).
#   --mode susie       coloc.susie on the arm's two fits; method coloc_susie, or fallback_abf (labelled,
#                      with fallback_reason) when either fit has 0 credible sets. The fallback IS the
#                      A1_matched computation, so its PPs equal A1_matched exactly.
#   --mode A1_matched  coloc.abf on the intersection of the two fits' retained variants (chr:pos keys).
#   --mode A1_allvars  coloc.abf on every region sumstats row matched between the traits on CHR:POS with
#                      unordered {REF,ALT} equality (CHR:POS only where a row has no alleles).
# Priors come only from --priors (p1, p2, the --p12-key value, overlap_min, trim_by_posterior) and are
# written into every output. Package defaults are never used.
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(jsonlite)
  library(coloc)
})

opt <- parse_args(OptionParser(option_list = list(
  make_option("--mode"), make_option("--fit-a"), make_option("--fit-b"),
  make_option("--sumstats-a"), make_option("--sumstats-b"), make_option("--trait-a"), make_option("--trait-b"),
  make_option("--ancestry"), make_option("--region-id"), make_option("--regions-csv"),
  make_option("--trait-manifest"), make_option("--priors"), make_option("--p12-key"),
  make_option("--row-id"), make_option("--arm"), make_option("--output")
)))
fail <- function(code, ...) stop(sprintf("%s: %s", code, sprintf(...)), call. = FALSE)

MODES <- c("A1_matched", "A1_allvars", "susie")
if (is.null(opt$mode) || !opt$mode %in% MODES) fail("MODE", "--mode must be one of %s", toString(MODES))
need <- c("sumstats-a", "sumstats-b", "trait-a", "trait-b", "ancestry", "region-id", "regions-csv",
          "trait-manifest", "priors", "p12-key", "row-id", "arm", "output")
if (opt$mode != "A1_allvars") need <- c("fit-a", "fit-b", need)
for (k in need) if (is.null(opt[[k]]) || !nzchar(opt[[k]])) fail("ARGS", "--%s is required for --mode %s", k, opt$mode)

# --- priors (single source) ------------------------------------------------------------------------------
pri <- yaml::read_yaml(opt$priors)
if (!opt$`p12-key` %in% c("p12_primary", "p12_sensitivity")) fail("P12_KEY", "unknown --p12-key %s", opt$`p12-key`)
for (k in c("p1", "p2", opt$`p12-key`, "overlap_min", "trim_by_posterior")) {
  if (is.null(pri[[k]])) fail("PRIORS", "%s missing from %s", k, opt$priors)
}
P1 <- as.numeric(pri$p1); P2 <- as.numeric(pri$p2); P12 <- as.numeric(pri[[opt$`p12-key`]])
OVERLAP_MIN <- as.numeric(pri$overlap_min); TRIM <- isTRUE(pri$trim_by_posterior)

# --- trait types / sdY (pre-registered; never estimated) ---------------------------------------------------
tm <- as.data.frame(fread(opt$`trait-manifest`, colClasses = "character", na.strings = NULL))
trait_info <- function(tr) {
  r <- tm[tm$trait == tr & tm$ancestry == opt$ancestry, , drop = FALSE]
  if (nrow(r) != 1) fail("TRAIT_MANIFEST", "%d rows for %s %s in %s", nrow(r), tr, opt$ancestry, opt$`trait-manifest`)
  if (!r$type %in% c("cc", "quant")) fail("TRAIT_TYPE", "%s type %s", tr, r$type)
  sdY <- suppressWarnings(as.numeric(r$sdY))
  if (r$type == "quant" && !(is.finite(sdY) && sdY > 0)) {
    fail("SDY_MISSING", "quant trait %s %s has no pre-registered sdY (%s); refusing to estimate it",
         tr, opt$ancestry, r$sdY)
  }
  list(type = r$type, sdY = if (r$type == "quant") sdY else NA_real_, N = suppressWarnings(as.numeric(r$N_median)))
}
ti_a <- trait_info(opt$`trait-a`); ti_b <- trait_info(opt$`trait-b`)

# --- region sumstats (the frozen run_susie_rss.R reader and bounds) -----------------------------------------
regions <- fread(opt$`regions-csv`)
reg <- regions[region_id == opt$`region-id`]
if (nrow(reg) != 1) fail("REGION", "%d rows for %s in %s", nrow(reg), opt$`region-id`, opt$`regions-csv`)
read_region <- function(path) {
  ss <- fread(cmd = sprintf("gunzip -c %s", shQuote(path)))
  if (!all(c("CHR", "POS", "BETA", "SE") %in% names(ss))) fail("SUMSTATS", "%s lacks CHR/POS/BETA/SE", path)
  ss[, CHR := as.character(CHR)]
  ss <- ss[CHR == as.character(reg$chr) & POS >= as.numeric(reg$start) & POS <= as.numeric(reg$end)]
  if (!"SNP_ID" %in% names(ss)) ss[, SNP_ID := NA_character_]
  ss[, SNP_ID := as.character(SNP_ID)]
  ss[SNP_ID == "" | SNP_ID == "NA", SNP_ID := NA_character_]
  for (a in c("REF", "ALT")) if (!a %in% names(ss)) ss[, (a) := NA_character_]
  ss[, cp := sprintf("%s:%s", CHR, format(as.integer(POS), scientific = FALSE, trim = TRUE))]
  # the frozen script's variant name: SNP_ID when present, else CHR:POS
  ss[, name := if (all(is.na(SNP_ID))) cp else ifelse(is.na(SNP_ID), cp, SNP_ID)]
  ss
}
ss_a <- read_region(opt$`sumstats-a`); ss_b <- read_region(opt$`sumstats-b`)

# --- fits and name alignment ---------------------------------------------------------------------------------
# Behaviour of run_coloc_susie.R:95-260 (fit names -> common chr:pos key via the source sumstats), except that a
# fit name with no sumstats row is an error here, not a silently dropped column.
align_names <- function(fit, ss, label) {
  nm <- colnames(fit$lbf_variable)
  if (is.null(nm)) fail("FIT_UNNAMED", "%s fit has no variant names", label)
  real <- nm[nm != "null"]
  dup <- ss$name[duplicated(ss$name)]
  if (any(real %in% dup)) fail("AMBIGUOUS_FIT_NAMES", "%s: %d fit names match >1 sumstats row", label, sum(real %in% dup))
  idx <- match(real, ss$name)
  if (anyNA(idx)) {
    fail("UNMAPPED_FIT_NAMES", paste0("%s: %d of %d fit variant names (e.g. %s) are neither a sumstats SNP_ID nor ",
                                      "CHR:POS in %s (LD-panel rsid override?); refusing to drop them"),
         label, sum(is.na(idx)), length(real), real[is.na(idx)][1], opt$`region-id`)
  }
  key <- ss$cp[idx]
  if (anyDuplicated(key)) fail("DUPLICATE_KEYS", "%s: two fit variants share a CHR:POS", label)
  map <- setNames(c(key, "null"), c(real, "null"))
  ren <- function(x) unname(map[x])
  for (s in c("alpha", "lbf_variable", "mu", "mu2")) if (!is.null(fit[[s]])) colnames(fit[[s]]) <- ren(colnames(fit[[s]]))
  if (!is.null(fit$pip)) names(fit$pip) <- ren(names(fit$pip))
  if (!is.null(fit$sets$cs)) for (i in seq_along(fit$sets$cs)) names(fit$sets$cs[[i]]) <- ren(names(fit$sets$cs[[i]]))
  list(fit = fit, keys = key, rows = ss[idx])
}
load_fit <- function(path, ss, label) {
  fit <- readRDS(path)
  if (is.null(fit$lbf_variable)) fail("FIT_EARLY_EXIT", "%s fit %s has no lbf_variable (status %s)", label, path,
                                      if (is.null(fit$status)) "NA" else fit$status)
  if (!inherits(fit, "susie")) class(fit) <- c("susie", class(fit))
  align_names(fit, ss, label)
}

# --- coloc.abf on explicit priors ------------------------------------------------------------------------------
dataset <- function(rows, keys, ti) {
  d <- list(beta = rows$BETA, varbeta = rows$SE^2, snp = keys, type = ti$type)
  if (is.finite(ti$N)) d$N <- ti$N
  if (ti$type == "quant") d$sdY <- ti$sdY
  d
}
run_abf <- function(ra, rb, keys) {
  if (!length(keys)) fail("NO_SHARED_VARIANTS", "no variants shared by %s and %s", opt$`trait-a`, opt$`trait-b`)
  res <- coloc.abf(dataset(ra, keys, ti_a), dataset(rb, keys, ti_b), p1 = P1, p2 = P2, p12 = P12)
  s <- as.list(res$summary)
  list(summary = list(s), pp = unname(unlist(s[sprintf("PP.H%d.abf", 0:4)])), n_snps = as.integer(s$nsnps), keys = keys)
}
a1_matched <- function(fa, fb) {
  keys <- sort(intersect(fa$keys, fb$keys), method = "radix")
  run_abf(fa$rows[match(keys, fa$keys)], fb$rows[match(keys, fb$keys)], keys)
}

missing_allele <- function(x) is.na(x) | toupper(trimws(x)) %in% c("", "N", ".", "NA")
a1_allvars <- function() {
  prep <- function(ss) {
    ok <- is.finite(ss$BETA) & is.finite(ss$SE) & ss$SE > 0
    x <- ss[ok]
    x[, miss := missing_allele(REF) | missing_allele(ALT)]
    x[, ak := ifelse(miss, NA_character_,
                     mapply(function(r, a) paste(sort(c(r, a), method = "radix"), collapse = "/"),
                            toupper(trimws(REF)), toupper(trimws(ALT))))]
    list(x = x, unusable = sum(!ok))
  }
  pa <- prep(ss_a); pb <- prep(ss_b)
  a <- pa$x; b <- pb$x
  n_allele <- 0L; n_pos <- 0L; n_mismatch <- 0L; n_dup <- 0L
  ra <- list(); rb <- list(); keys <- character(0)
  for (p in sort(intersect(a$cp, b$cp), method = "radix")) {
    xa <- a[cp == p]; xb <- b[cp == p]
    if (nrow(xa) == 1 && nrow(xb) == 1) {
      if (xa$miss || xb$miss) { n_pos <- n_pos + 1L }
      else if (xa$ak == xb$ak) { n_allele <- n_allele + 1L }
      else { n_mismatch <- n_mismatch + 1L; next }
      ra[[length(ra) + 1]] <- xa; rb[[length(rb) + 1]] <- xb; keys <- c(keys, p)
      next
    }
    # several rows at one position: allele-keyed pairs only, each allele set unique per trait
    if (any(xa$miss) || any(xb$miss) || anyDuplicated(xa$ak) || anyDuplicated(xb$ak)) {
      n_dup <- n_dup + max(nrow(xa), nrow(xb)); next
    }
    for (k in sort(intersect(xa$ak, xb$ak), method = "radix")) {
      n_allele <- n_allele + 1L
      ra[[length(ra) + 1]] <- xa[ak == k]; rb[[length(rb) + 1]] <- xb[ak == k]; keys <- c(keys, paste0(p, ":", k))
    }
  }
  if (!length(keys)) fail("NO_SHARED_VARIANTS", "no matched variants for %s / %s", opt$`trait-a`, opt$`trait-b`)
  res <- run_abf(rbindlist(ra), rbindlist(rb), keys)
  c(res, list(counts = list(n_matched_allele = n_allele, n_matched_pos_only = n_pos, n_allele_mismatch = n_mismatch,
                            n_dropped_duplicate = n_dup, n_dropped_unusable = pa$unusable + pb$unusable)))
}

# --- run ----------------------------------------------------------------------------------------------------
n_cs <- function(f) length(f$fit$sets$cs)
out <- list(n_cs_a = NA_integer_, n_cs_b = NA_integer_, fallback_reason = NA_character_,
            pp_h4_max = NA_real_, n_cs_pairs = NA_integer_, n_cs_pairs_h4_ge_0.8 = NA_integer_,
            n_matched_allele = NA_integer_, n_matched_pos_only = NA_integer_, n_allele_mismatch = NA_integer_,
            n_dropped_duplicate = NA_integer_, n_dropped_unusable = NA_integer_)
pp <- rep(NA_real_, 5)

if (opt$mode == "A1_allvars") {
  r <- a1_allvars()
  method <- "A1_abf_allvars"
  out[names(r$counts)] <- r$counts
} else {
  fa <- load_fit(opt$`fit-a`, ss_a, "fit_a"); fb <- load_fit(opt$`fit-b`, ss_b, "fit_b")
  out$n_cs_a <- n_cs(fa); out$n_cs_b <- n_cs(fb)
  zero <- c(if (out$n_cs_a == 0) "n_cs_a==0", if (out$n_cs_b == 0) "n_cs_b==0")
  if (opt$mode == "A1_matched" || length(zero)) {
    r <- a1_matched(fa, fb)
    method <- if (opt$mode == "A1_matched") "A1_abf_matched" else "fallback_abf"
    if (method == "fallback_abf") out$fallback_reason <- paste(zero, collapse = "&")
  } else {
    method <- "coloc_susie"
    keys <- sort(setdiff(intersect(colnames(fa$fit$lbf_variable), colnames(fb$fit$lbf_variable)), "null"),
                 method = "radix")
    res <- coloc.susie(fa$fit, fb$fit, p1 = P1, p2 = P2, p12 = P12, overlap.min = OVERLAP_MIN,
                       trim_by_posterior = TRIM)
    if (is.null(res$summary) || !"PP.H4.abf" %in% names(res$summary)) {
      fail("COLOC_SUSIE_EMPTY", "coloc.susie returned no summary (%d shared variants)", length(keys))
    }
    sm <- as.data.table(res$summary)
    h4 <- sm$PP.H4.abf
    out$n_cs_pairs <- nrow(sm)
    out$n_cs_pairs_h4_ge_0.8 <- sum(h4 >= 0.8, na.rm = TRUE)
    if (any(!is.na(h4))) {
      best <- which.max(h4)
      out$pp_h4_max <- h4[best]
      pp <- unname(unlist(sm[best, sprintf("PP.H%d.abf", 0:4), with = FALSE]))
    }
    r <- list(summary = lapply(seq_len(nrow(sm)), function(i) as.list(sm[i])), n_snps = length(keys), keys = keys)
  }
}
if (method != "coloc_susie") { pp <- r$pp; out$pp_h4_max <- pp[5] }

doc <- c(list(row_id = opt$`row-id`, arm = opt$arm, mode = opt$mode, method = method,
              trait_a = opt$`trait-a`, trait_b = opt$`trait-b`, ancestry = opt$ancestry, region_id = opt$`region-id`,
              type_a = ti_a$type, type_b = ti_b$type, sdY_a = ti_a$sdY, sdY_b = ti_b$sdY,
              p12_key = opt$`p12-key`, p1 = P1, p2 = P2, p12 = P12, overlap_min = OVERLAP_MIN, trim_by_posterior = TRIM,
              n_snps = r$n_snps,
              variant_set_sha256 = digest::digest(paste(sort(r$keys, method = "radix"), collapse = "\n"),
                                                  algo = "sha256", serialize = FALSE),
              pp_h0 = pp[1], pp_h1 = pp[2], pp_h2 = pp[3], pp_h3 = pp[4], pp_h4 = pp[5],
              summary = r$summary,
              coloc_version = as.character(packageVersion("coloc")),
              susieR_version = as.character(packageVersion("susieR")),
              R.version.string = R.version.string),
         out)
dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
tmp <- paste0(opt$output, ".tmp")
write_json(doc, tmp, auto_unbox = TRUE, digits = NA, na = "null", null = "null", pretty = TRUE)
invisible(file.rename(tmp, opt$output))
cat(sprintf("[run_coloc_pair_r4] %s %s %s method=%s n_snps=%d pp_h4_max=%s\n", opt$`row-id`, opt$arm,
            opt$`p12-key`, method, r$n_snps, format(out$pp_h4_max, digits = 6)))
