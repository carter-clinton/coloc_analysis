#!/usr/bin/env Rscript
# R4 trait-pair colocalization for one pair_manifest row (D-01, D-02, D-21; Pitfalls 5 and 8).
#   --mode susie       coloc.susie on the arm's two fits; method coloc_susie, or fallback_abf (labelled,
#                      with fallback_reason) when either fit has 0 credible sets. The fallback IS the
#                      A1_matched computation, so its PPs equal A1_matched exactly.
#   --mode A1_matched  coloc.abf on the intersection of the two fits' retained variants (chr:pos keys).
#   --mode A1_allvars  coloc.abf on every region sumstats row matched between the traits on CHR:POS with
#                      unordered {REF,ALT} equality (CHR:POS only where a row has no alleles).
#   --mode qtl_abf     GWAS x QTL fallback_abf (D-02 on the QTL layer, W3e): coloc.abf on the variant set
#                      run_qtl_coloc.R bridges (qtl_bridge(), its steps 3-4c replicated), GWAS beta/se from the
#                      region sumstats rows of the fit's names, QTL quant with --sdy.
# Fit names map to sumstats rows through the fit's LD panel (map_fit_names, W3f N2); any unmapped name is an error.
# Early-exit fits and empty / no-finite-H4 coloc.susie summaries are written as method "none" with none_reason (N8).
# Priors come only from --priors (p1, p2, the --p12-key value, overlap_min, trim_by_posterior) and are
# written into every output. Package defaults are never used.
# coloc_pair_core() is shared with simulate_coloc_r4.R (W3c), which source()s this file; main() runs only as a script.
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(jsonlite)
  library(coloc)
})

fail <- function(code, ...) stop(sprintf("%s: %s", code, sprintf(...)), call. = FALSE)
`%||%` <- function(x, y) if (!is.null(x)) x else y
MODES <- c("A1_matched", "A1_allvars", "susie", "qtl_abf")

# --- coloc.abf on explicit priors (pri: p1, p2, p12, overlap_min, trim) -----------------------------------------
dataset <- function(rows, keys, ti) {
  d <- list(beta = rows$BETA, varbeta = rows$SE^2, snp = keys, type = ti$type)
  if (is.finite(ti$N)) d$N <- ti$N
  if (ti$type == "quant") d$sdY <- ti$sdY
  d
}
run_abf <- function(ra, rb, keys, ti_a, ti_b, pri, labels) {
  if (!length(keys)) fail("NO_SHARED_VARIANTS", "no variants shared by %s and %s", labels[1], labels[2])
  res <- coloc.abf(dataset(ra, keys, ti_a), dataset(rb, keys, ti_b), p1 = pri$p1, p2 = pri$p2, p12 = pri$p12)
  s <- as.list(res$summary)
  list(summary = list(s), pp = unname(unlist(s[sprintf("PP.H%d.abf", 0:4)])), n_snps = as.integer(s$nsnps), keys = keys)
}
a1_matched <- function(fa, fb, ti_a, ti_b, pri, labels) {
  keys <- sort(intersect(fa$keys, fb$keys), method = "radix")
  run_abf(fa$rows[match(keys, fa$keys)], fb$rows[match(keys, fb$keys)], keys, ti_a, ti_b, pri, labels)
}

# fa / fb: list(fit, keys, rows) with fit columns named by keys; fit = NULL is allowed for A1_matched (n_cs NA).
coloc_pair_core <- function(fa, fb, ti_a, ti_b, pri, mode, labels = c("trait_a", "trait_b")) {
  if (!mode %in% c("A1_matched", "susie")) fail("MODE", "coloc_pair_core runs A1_matched or susie, not %s", mode)
  n_cs <- function(f) if (is.null(f$fit)) NA_integer_ else length(f$fit$sets$cs)
  out <- list(n_cs_a = n_cs(fa), n_cs_b = n_cs(fb), fallback_reason = NA_character_, pp_h4_max = NA_real_,
              n_cs_pairs = NA_integer_, n_cs_pairs_h4_ge_0.8 = NA_integer_, none_reason = NA_character_)
  pp <- rep(NA_real_, 5)
  zero <- if (mode == "susie") c(if (out$n_cs_a == 0) "n_cs_a==0", if (out$n_cs_b == 0) "n_cs_b==0")
  if (mode == "A1_matched" || length(zero)) {
    r <- a1_matched(fa, fb, ti_a, ti_b, pri, labels)
    method <- if (mode == "A1_matched") "A1_abf_matched" else "fallback_abf"
    if (method == "fallback_abf") out$fallback_reason <- paste(zero, collapse = "&")
  } else {
    method <- "coloc_susie"
    keys <- sort(setdiff(intersect(colnames(fa$fit$lbf_variable), colnames(fb$fit$lbf_variable)), "null"),
                 method = "radix")
    res <- coloc.susie(fa$fit, fb$fit, p1 = pri$p1, p2 = pri$p2, p12 = pri$p12, overlap.min = pri$overlap_min,
                       trim_by_posterior = pri$trim)
    if (is.null(res$summary) || !"PP.H4.abf" %in% names(res$summary) || !nrow(res$summary)) {
      method <- "none"
      out$none_reason <- "coloc_susie_empty"
      r <- list(summary = list(), n_snps = length(keys), keys = keys)
    } else {
      sm <- as.data.table(res$summary)
      h4 <- sm$PP.H4.abf
      out$n_cs_pairs <- nrow(sm)
      out$n_cs_pairs_h4_ge_0.8 <- sum(h4 >= 0.8, na.rm = TRUE)
      if (any(is.finite(h4))) {
        best <- which.max(h4)
        out$pp_h4_max <- h4[best]
        pp <- unname(unlist(sm[best, sprintf("PP.H%d.abf", 0:4), with = FALSE]))
      } else {
        method <- "none"
        out$none_reason <- "coloc_susie_no_finite_h4"
      }
      r <- list(summary = lapply(seq_len(nrow(sm)), function(i) as.list(sm[i])), n_snps = length(keys), keys = keys)
    }
  }
  if (method %in% c("A1_abf_matched", "fallback_abf")) { pp <- r$pp; out$pp_h4_max <- pp[5] }
  list(method = method, pp = pp, r = r, out = out)
}

# --- shared by main() and qtl_abf_main() ------------------------------------------------------------------------
load_priors <- function(path, p12_key) {
  pri <- yaml::read_yaml(path)
  if (!p12_key %in% c("p12_primary", "p12_sensitivity")) fail("P12_KEY", "unknown --p12-key %s", p12_key)
  for (k in c("p1", "p2", p12_key, "overlap_min", "trim_by_posterior")) {
    if (is.null(pri[[k]])) fail("PRIORS", "%s missing from %s", k, path)
  }
  list(p1 = as.numeric(pri$p1), p2 = as.numeric(pri$p2), p12 = as.numeric(pri[[p12_key]]),
       overlap_min = as.numeric(pri$overlap_min), trim = isTRUE(pri$trim_by_posterior))
}

# trait types / sdY (pre-registered; never estimated)
trait_info <- function(tm, tr, ancestry, tm_path) {
  r <- tm[tm$trait == tr & tm$ancestry == ancestry, , drop = FALSE]
  if (nrow(r) != 1) fail("TRAIT_MANIFEST", "%d rows for %s %s in %s", nrow(r), tr, ancestry, tm_path)
  if (!r$type %in% c("cc", "quant")) fail("TRAIT_TYPE", "%s type %s", tr, r$type)
  sdY <- suppressWarnings(as.numeric(r$sdY))
  if (r$type == "quant" && !(is.finite(sdY) && sdY > 0)) {
    fail("SDY_MISSING", "quant trait %s %s has no pre-registered sdY (%s); refusing to estimate it",
         tr, ancestry, r$sdY)
  }
  list(type = r$type, sdY = if (r$type == "quant") sdY else NA_real_, N = suppressWarnings(as.numeric(r$N_median)))
}

# region sumstats (the frozen run_susie_rss.R reader and bounds)
read_region <- function(path, reg) {
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

# --- fit names -> region sumstats rows, through the LD panel the fit was built against (W3f N2) -------------------
norm_allele <- function(x) toupper(trimws(as.character(x)))
missing_allele <- function(x) is.na(x) | norm_allele(x) %in% c("", "N", ".", "NA")
complement <- function(x) chartr("ACGT", "TGCA", x)

# names: fit variant names; ss: read_region() rows; panel: the panel's variants data.frame (SNP_ID, CHR, POS and
# REF/ALT, else A1/A2 as an unordered set). Returns list(idx = ss row per name, counts); any unmapped name fails.
map_fit_names <- function(names, ss, panel, label) {
  n <- length(names)
  idx <- rep(NA_integer_, n)
  kind <- rep(NA_character_, n)
  why <- rep(NA_character_, n)
  ss_dup <- ss$name[duplicated(ss$name)]
  direct <- match(names, ss$name)
  ok_direct <- !is.na(direct) & !names %in% ss_dup
  idx[ok_direct] <- direct[ok_direct]
  kind[ok_direct] <- "direct"
  basis <- NA_character_
  if (any(!ok_direct)) {
    pv <- if (is.data.frame(panel)) panel else NULL
    has_ra <- !is.null(pv) && all(c("REF", "ALT") %in% names(pv))
    has_a12 <- !is.null(pv) && all(c("A1", "A2") %in% names(pv))
    basis <- if (has_ra) "REF/ALT" else if (has_a12) "A1/A2_unordered" else "none"
    pid <- if (is.null(pv)) character(0) else as.character(pv$SNP_ID)
    pcp <- if (is.null(pv)) character(0) else
      sprintf("%s:%s", sub("^chr", "", as.character(pv$CHR)), format(as.integer(pv$POS), scientific = FALSE, trim = TRUE))
    pr <- if (has_ra) norm_allele(pv$REF) else if (has_a12) norm_allele(pv$A2) else rep(NA_character_, length(pid))
    pa <- if (has_ra) norm_allele(pv$ALT) else if (has_a12) norm_allele(pv$A1) else rep(NA_character_, length(pid))
    sr <- norm_allele(ss$REF); sa <- norm_allele(ss$ALT)
    s_miss <- missing_allele(ss$REF) | missing_allele(ss$ALT)
    for (i in which(!ok_direct)) {
      hit <- which(pid == names[i])
      if (!length(hit)) { why[i] <- "absent"; next }
      if (length(hit) > 1) { why[i] <- "panel_duplicate"; next }
      rows <- which(ss$cp == pcp[hit])
      if (!length(rows)) { why[i] <- "no_position"; next }
      r0 <- pr[hit]; a0 <- pa[hit]
      if (missing_allele(r0) || missing_allele(a0)) { why[i] <- "panel_no_alleles"; next }
      snv <- nchar(r0) == 1 && nchar(a0) == 1
      pal <- snv && complement(r0) == a0
      cls <- vapply(rows, function(j) {
        if (s_miss[j]) return("no_alleles")
        if (sr[j] == r0 && sa[j] == a0) return("exact")
        if (sr[j] == a0 && sa[j] == r0) return(if (basis == "REF/ALT") "swapped" else "exact")
        if (snv && !pal && nchar(sr[j]) == 1 && nchar(sa[j]) == 1 &&
            ((sr[j] == complement(r0) && sa[j] == complement(a0)) ||
             (sr[j] == complement(a0) && sa[j] == complement(r0)))) return("strand")
        "mismatch"
      }, character(1))
      good <- cls %in% c("exact", "swapped", "strand")
      if (sum(good) == 1 && !any(cls == "no_alleles")) {
        idx[i] <- rows[good]; kind[i] <- cls[good]
      } else if (sum(good) >= 1) {
        why[i] <- "ambiguous"
      } else if (any(cls == "no_alleles")) {
        why[i] <- "no_alleles"
      } else {
        why[i] <- "allele_mismatch"
      }
    }
  }
  bad <- is.na(idx)
  if (any(bad)) {
    tab <- table(factor(why[bad], levels = unique(why[bad])))
    fail("UNMAPPED_FIT_NAMES", "%s: %d of %d fit variant names unmapped (%s); first: %s", label, sum(bad), n,
         paste(sprintf("%s=%d", names(tab), as.integer(tab)), collapse = ", "), paste(head(names[bad], 5), collapse = ", "))
  }
  list(idx = idx, counts = list(n_names = n, n_direct = sum(kind == "direct"), n_panel_exact = sum(kind == "exact"),
                                n_panel_swapped = sum(kind == "swapped"), n_panel_strand = sum(kind == "strand"),
                                allele_basis = basis))
}

# The panel passed on the command line must be the panel the fit read (its JSON: ld_file_declared, else ld_matrix).
check_fit_panel <- function(fit_path, panel_path, label) {
  js <- sub("\\.fit\\.rds$", ".json", fit_path)
  if (!file.exists(js)) fail("FIT_PANEL_MISMATCH", "%s: no fit JSON %s", label, js)
  d <- jsonlite::fromJSON(js, simplifyVector = TRUE)
  rec <- d$ld_file_declared %||% d$ld_matrix
  if (is.null(rec) || is.na(rec) || !nzchar(rec) || !file.exists(rec) || !file.exists(panel_path) ||
      normalizePath(rec) != normalizePath(panel_path)) {
    fail("FIT_PANEL_MISMATCH", "%s: --ld-panel %s is not the panel the fit recorded (%s)", label, panel_path,
         if (is.null(rec)) "none" else rec)
  }
  invisible(TRUE)
}

region_row <- function(regions_csv, rid) {
  regions <- fread(regions_csv)
  reg <- regions[region_id == rid]
  if (nrow(reg) != 1) fail("REGION", "%d rows for %s in %s", nrow(reg), rid, regions_csv)
  reg
}

# --- the run_qtl_coloc.R GWAS<->QTL<->LD bridge (its steps 3, 4, 4b, final overlap, 4c) ---------------------------
# Returns list(status = "ok" | a run_qtl_coloc.R status | "ld_join_fatal", reason, snps (fit-space names, in that
# script's order), qtl (rows aligned to snps, beta oriented under qtl_orient), match_key, ld_key_space, counts).
qtl_bridge <- function(gwas_snps, qtl_df, ld_obj, catalog, ld_allele_join, qtl_orient) {
  stopped <- function(status, reason) list(status = status, reason = reason)
  qtl_df <- as.data.table(qtl_df)
  gwas_snps <- gwas_snps[gwas_snps != "null"]
  qtl_df[, beta := as.numeric(beta)]
  qtl_df[, se   := as.numeric(se)]
  qtl_df[, maf  := as.numeric(maf)]
  qtl_df[, position := as.integer(position)]
  qtl_df$chrpos <- local({
    parts <- strsplit(as.character(qtl_df$variant_id), "_", fixed = TRUE)
    chrom <- sub("^chr", "", sapply(parts, `[`, 1))
    pos   <- sapply(parts, `[`, 2)
    paste0(chrom, ":", pos)
  })
  candidates <- list()
  if ("rsid" %in% names(qtl_df) &&
      any(!is.na(qtl_df$rsid) & qtl_df$rsid != "" & qtl_df$rsid != "NA")) {
    candidates[["rsid"]] <- qtl_df$rsid
  }
  candidates[["chrpos"]]     <- qtl_df$chrpos
  candidates[["variant_id"]] <- qtl_df$variant_id
  overlaps <- sapply(candidates, function(v) length(intersect(gwas_snps, v)))
  match_key <- names(which.max(overlaps))
  overlap_snps <- intersect(gwas_snps, candidates[[match_key]])
  if (length(overlap_snps) < 50) return(stopped("too_few_snps", "fit_qtl_overlap"))

  use_identity <- FALSE
  if (is.list(ld_obj) && !is.matrix(ld_obj)) {
    use_identity <- isTRUE(ld_obj$use_identity) || is.null(ld_obj$R)
    if (use_identity && ld_allele_join) return(stopped("ld_join_fatal", "use_identity_under_gate"))
    if (!use_identity) {
      ld_full <- ld_obj$R
      ld_snp_names <- rownames(ld_full) %||% colnames(ld_full)
      if (is.null(ld_snp_names) && is.data.frame(ld_obj$variants)) {
        v <- ld_obj$variants
        if ("SNP_ID" %in% names(v) && any(!is.na(v$SNP_ID) & v$SNP_ID != "" & v$SNP_ID != "NA")) {
          ld_snp_names <- as.character(v$SNP_ID)
        } else if (all(c("CHR", "POS") %in% names(v))) {
          ld_snp_names <- sprintf("%s:%s", v$CHR, v$POS)
        }
      }
      if (is.null(ld_snp_names)) return(stopped("too_few_snps", "ld_unnamed"))
      if ((is.null(rownames(ld_full)) || is.null(colnames(ld_full))) && length(ld_snp_names) != nrow(ld_full)) {
        return(stopped("too_few_snps", "ld_rownames_length"))
      }
    }
  } else if (is.matrix(ld_obj) || inherits(ld_obj, "Matrix")) {
    ld_full <- ld_obj
    ld_snp_names <- rownames(ld_full) %||% colnames(ld_full)
    if (is.null(ld_snp_names)) return(stopped("too_few_snps", "ld_unnamed"))
  } else {
    return(stopped("too_few_snps", "ld_class"))
  }

  ld_key_space <- NA_character_
  ld_row_index <- NULL
  counts <- list()
  if (ld_allele_join && !use_identity) {
    if (is.null(catalog) || nrow(catalog) == 0) return(stopped("ld_join_fatal", "variant_catalog_absent"))
    panel_variants <- ld_obj$variants
    if (is.null(panel_variants) || !is.data.frame(panel_variants)) return(stopped("ld_join_fatal", "panel_variants_absent"))
    if (nrow(panel_variants) != nrow(ld_full)) return(stopped("ld_join_fatal", "panel_variants_out_of_step"))
    if (qtl_orient && !all(c("REF", "ALT") %in% names(panel_variants))) return(stopped("ld_join_fatal", "panel_ref_alt"))
    join <- ld_allele_join_indices(catalog, panel_variants)
    if (!is.null(join$counts$reject)) return(stopped("ld_join_fatal", join$counts$reject))
    bound_cat <- join$keep
    bound_pan <- join$ld
    cat_snp_id <- if ("SNP_ID" %in% names(catalog))
      as.character(catalog$SNP_ID)[bound_cat] else rep(NA_character_, length(bound_cat))
    cat_chrpos <- paste(toupper(trimws(as.character(catalog$CHR)))[bound_cat],
                        suppressWarnings(as.integer(catalog$POS))[bound_cat], sep = ":")
    bridged_spaces <- list(catalog_snp_id = cat_snp_id, catalog_chrpos = cat_chrpos)
    bridged_overlaps <- vapply(bridged_spaces, function(v) length(intersect(overlap_snps, v[!is.na(v)])), integer(1))
    ld_key_space <- names(which.max(bridged_overlaps))
    chosen <- bridged_spaces[[ld_key_space]]
    usable <- !is.na(chosen) & nzchar(chosen)
    dup <- duplicated(chosen) | duplicated(chosen, fromLast = TRUE)
    keep_bridge <- usable & !dup
    ld_row_index <- bound_pan[keep_bridge]
    names(ld_row_index) <- chosen[keep_bridge]
    ld_snp_names <- names(ld_row_index)
  }
  if (!use_identity) {
    overlap_snps <- intersect(overlap_snps, ld_snp_names)
    if (length(overlap_snps) < 50) {
      return(if (ld_allele_join) stopped("ld_join_fatal", "panel_bridge_below_threshold")
             else stopped("too_few_snps", "ld_overlap"))
    }
  }
  qtl_df <- qtl_df[match(overlap_snps, qtl_df[[match_key]]), ]
  if (qtl_orient) {
    pidx <- as.integer(ld_row_index[overlap_snps])
    qo <- qtl_orient_vector(qtl_df$variant_id, ld_obj$variants$REF[pidx], ld_obj$variants$ALT[pidx])
    counts <- qo$counts
    keep_q <- !is.na(qo$orient)
    orient_keep <- qo$orient[keep_q]
    qtl_df <- qtl_df[keep_q, ]
    qtl_df[, beta := beta * orient_keep]
    overlap_snps <- overlap_snps[keep_q]
    if (length(overlap_snps) < 50) return(stopped("ld_join_fatal", "qtl_orient_below_threshold"))
  }
  list(status = "ok", reason = NA_character_, snps = overlap_snps, qtl = qtl_df, match_key = match_key,
       ld_key_space = ld_key_space, counts = counts)
}

script_dir <- function() {
  f <- sub("^--file=", "", grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE))
  if (length(f)) dirname(normalizePath(f[1])) else "src/snakemake/scripts/ta_r4"
}

qtl_abf_main <- function(opt) {
  need <- c("gwas-fit", "sumstats-a", "trait-a", "ancestry", "region-id", "regions-csv", "trait-manifest", "priors",
            "p12-key", "qtl-sumstats", "ld-matrix", "ld-allele-join", "qtl-orient", "sdy", "sample-size",
            "fallback-reason", "row-id", "arm", "output")
  for (k in need) if (is.null(opt[[k]]) || !nzchar(opt[[k]])) fail("ARGS", "--%s is required for --mode qtl_abf", k)
  for (k in c("ld-allele-join", "qtl-orient")) {
    if (!opt[[k]] %in% c("true", "false")) fail("ARGS", "--%s must be exactly 'true' or 'false', got '%s'", k, opt[[k]])
  }
  join <- opt$`ld-allele-join` == "true"; orient <- opt$`qtl-orient` == "true"
  if (orient && !join) fail("ARGS", "--qtl-orient true requires --ld-allele-join true")
  scripts <- dirname(script_dir())
  if (join) source(file.path(scripts, "ld_allele_join.R"))
  if (orient) source(file.path(scripts, "qtl_orient.R"))
  catalog <- NULL
  if (join) {
    if (is.null(opt$`variant-list`) || !file.exists(opt$`variant-list`)) fail("ARGS", "--variant-list is required under --ld-allele-join true")
    catalog <- as.data.frame(fread(opt$`variant-list`))
  }
  P <- load_priors(opt$priors, opt$`p12-key`)
  tm <- as.data.frame(fread(opt$`trait-manifest`, colClasses = "character", na.strings = NULL))
  ti_g <- trait_info(tm, opt$`trait-a`, opt$ancestry, opt$`trait-manifest`)
  sdy <- as.numeric(opt$sdy); nq <- as.numeric(opt$`sample-size`)
  if (!(is.finite(sdy) && sdy > 0) || !(is.finite(nq) && nq > 0)) fail("ARGS", "--sdy and --sample-size must be > 0")
  ti_q <- list(type = "quant", sdY = sdy, N = nq)

  fit <- readRDS(opt$`gwas-fit`)
  gwas_snps <- if (!is.null(fit$alpha) && !is.null(colnames(fit$alpha))) colnames(fit$alpha) else names(fit$pip)
  if (is.null(gwas_snps)) fail("FIT_UNNAMED", "GWAS fit %s has no variant names", opt$`gwas-fit`)
  b <- qtl_bridge(gwas_snps, fread(opt$`qtl-sumstats`), readRDS(opt$`ld-matrix`), catalog, join, orient)
  if (b$status != "ok") fail("BRIDGE", "%s (%s): no bridged variant set for the fallback", b$status, b$reason)

  ss <- read_region(opt$`sumstats-a`, region_row(opt$`regions-csv`, opt$`region-id`))
  ld_obj <- readRDS(opt$`ld-matrix`)
  nm <- map_fit_names(b$snps, ss, if (is.list(ld_obj)) ld_obj$variants else NULL, "gwas_fit")
  idx <- nm$idx
  r <- run_abf(ss[idx], data.table(BETA = b$qtl$beta, SE = b$qtl$se), b$snps, ti_g, ti_q, P,
               c(opt$`trait-a`, "qtl"))
  pp <- r$pp
  doc <- c(list(row_id = opt$`row-id`, arm = opt$arm, mode = "qtl_abf", method = "fallback_abf",
                fallback_reason = opt$`fallback-reason`, trait = opt$`trait-a`, ancestry = opt$ancestry,
                region_id = opt$`region-id`, type_gwas = ti_g$type, sdY_gwas = ti_g$sdY, N_gwas = ti_g$N,
                qtl_sdy = sdy, qtl_n = nq, ld_allele_join = opt$`ld-allele-join`, qtl_orient = opt$`qtl-orient`,
                match_key = b$match_key, ld_key_space = b$ld_key_space, name_map = nm$counts,
                p12_key = opt$`p12-key`, p1 = P$p1, p2 = P$p2, p12 = P$p12, n_snps = r$n_snps,
                variant_set_sha256 = digest::digest(paste(sort(b$snps, method = "radix"), collapse = "\n"),
                                                    algo = "sha256", serialize = FALSE),
                pp_h0 = pp[1], pp_h1 = pp[2], pp_h2 = pp[3], pp_h3 = pp[4], pp_h4 = pp[5],
                summary = r$summary,
                coloc_version = as.character(packageVersion("coloc")), R.version.string = R.version.string),
           if (length(b$counts)) setNames(b$counts, paste0("qtl_orient_", names(b$counts))) else list())
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  tmp <- paste0(opt$output, ".tmp")
  write_json(doc, tmp, auto_unbox = TRUE, digits = NA, na = "null", null = "null", pretty = TRUE)
  invisible(file.rename(tmp, opt$output))
  cat(sprintf("[run_coloc_pair_r4] %s %s qtl_abf method=fallback_abf n_snps=%d pp_h4=%s\n", opt$`row-id`, opt$arm,
              r$n_snps, format(pp[5], digits = 6)))
}

main <- function() {
  opt <- parse_args(OptionParser(option_list = list(
    make_option("--mode"), make_option("--fit-a"), make_option("--fit-b"),
    make_option("--sumstats-a"), make_option("--sumstats-b"), make_option("--trait-a"), make_option("--trait-b"),
    make_option("--ancestry"), make_option("--region-id"), make_option("--regions-csv"),
    make_option("--trait-manifest"), make_option("--priors"), make_option("--p12-key"),
    make_option("--row-id"), make_option("--arm"), make_option("--output"),
    make_option("--gwas-fit"), make_option("--qtl-sumstats"), make_option("--ld-matrix"), make_option("--variant-list"),
    make_option("--ld-allele-join"), make_option("--qtl-orient"), make_option("--sdy"), make_option("--sample-size"),
    make_option("--fallback-reason"), make_option("--ld-panel")
  )))
  if (is.null(opt$mode) || !opt$mode %in% MODES) fail("MODE", "--mode must be one of %s", toString(MODES))
  if (opt$mode == "qtl_abf") return(invisible(qtl_abf_main(opt)))
  need <- c("sumstats-a", "sumstats-b", "trait-a", "trait-b", "ancestry", "region-id", "regions-csv",
            "trait-manifest", "priors", "p12-key", "row-id", "arm", "output")
  if (opt$mode != "A1_allvars") need <- c("fit-a", "fit-b", "ld-panel", need)
  for (k in need) if (is.null(opt[[k]]) || !nzchar(opt[[k]])) fail("ARGS", "--%s is required for --mode %s", k, opt$mode)
  labels <- c(opt$`trait-a`, opt$`trait-b`)

  # --- priors (single source) ----------------------------------------------------------------------------------
  P <- load_priors(opt$priors, opt$`p12-key`)

  tm <- as.data.frame(fread(opt$`trait-manifest`, colClasses = "character", na.strings = NULL))
  ti_a <- trait_info(tm, opt$`trait-a`, opt$ancestry, opt$`trait-manifest`)
  ti_b <- trait_info(tm, opt$`trait-b`, opt$ancestry, opt$`trait-manifest`)

  # --- region sumstats (the frozen run_susie_rss.R reader and bounds) ---------------------------------------------
  reg <- region_row(opt$`regions-csv`, opt$`region-id`)
  ss_a <- read_region(opt$`sumstats-a`, reg); ss_b <- read_region(opt$`sumstats-b`, reg)

  # --- fits and name alignment -----------------------------------------------------------------------------------
  # Behaviour of run_coloc_susie.R:95-260 (fit names -> common chr:pos key via the source sumstats), except that a
  # fit name with no sumstats row is an error here, not a silently dropped column.
  panel_cache <- NULL
  panel_variants <- function() {
    if (is.null(panel_cache)) {
      pnl <- readRDS(opt$`ld-panel`)
      panel_cache <<- list(v = if (is.list(pnl)) pnl$variants else NULL)
    }
    panel_cache$v
  }
  align_names <- function(fit, ss, label) {
    nm <- colnames(fit$lbf_variable)
    if (is.null(nm)) fail("FIT_UNNAMED", "%s fit has no variant names", label)
    real <- nm[nm != "null"]
    m <- map_fit_names(real, ss, panel_variants(), label)
    idx <- m$idx
    key <- ss$cp[idx]
    if (anyDuplicated(key)) fail("DUPLICATE_KEYS", "%s: two fit variants share a CHR:POS", label)
    map <- setNames(c(key, "null"), c(real, "null"))
    ren <- function(x) unname(map[x])
    for (s in c("alpha", "lbf_variable", "mu", "mu2")) if (!is.null(fit[[s]])) colnames(fit[[s]]) <- ren(colnames(fit[[s]]))
    if (!is.null(fit$pip)) names(fit$pip) <- ren(names(fit$pip))
    if (!is.null(fit$sets$cs)) for (i in seq_along(fit$sets$cs)) names(fit$sets$cs[[i]]) <- ren(names(fit$sets$cs[[i]]))
    list(fit = fit, keys = key, rows = ss[idx], name_map = m$counts)
  }
  EARLY_EXIT <- c("no_variants", "too_many_variants")
  read_fit <- function(path, label) {
    fit <- readRDS(path)
    if (is.null(fit$lbf_variable)) {
      st <- if (is.null(fit$status)) NA_character_ else as.character(fit$status)
      if (!isTRUE(st %in% EARLY_EXIT)) fail("FIT_EARLY_EXIT", "%s fit %s has no lbf_variable (status %s)", label, path, st)
      return(list(early_exit = st))
    }
    if (!inherits(fit, "susie")) class(fit) <- c("susie", class(fit))
    list(early_exit = NA_character_, fit = fit)
  }
  load_fit <- function(raw, path, ss, label) {
    check_fit_panel(path, opt$`ld-panel`, label)
    align_names(raw$fit, ss, label)
  }

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
    res <- run_abf(rbindlist(ra), rbindlist(rb), keys, ti_a, ti_b, P, labels)
    c(res, list(counts = list(n_matched_allele = n_allele, n_matched_pos_only = n_pos, n_allele_mismatch = n_mismatch,
                              n_dropped_duplicate = n_dup, n_dropped_unusable = pa$unusable + pb$unusable)))
  }

  # --- run ----------------------------------------------------------------------------------------------------------
  out <- list(n_cs_a = NA_integer_, n_cs_b = NA_integer_, fallback_reason = NA_character_,
              pp_h4_max = NA_real_, n_cs_pairs = NA_integer_, n_cs_pairs_h4_ge_0.8 = NA_integer_,
              n_matched_allele = NA_integer_, n_matched_pos_only = NA_integer_, n_allele_mismatch = NA_integer_,
              n_dropped_duplicate = NA_integer_, n_dropped_unusable = NA_integer_, none_reason = NA_character_,
              name_map_a = NULL, name_map_b = NULL)

  if (opt$mode == "A1_allvars") {
    r <- a1_allvars()
    method <- "A1_abf_allvars"
    out[names(r$counts)] <- r$counts
    pp <- r$pp; out$pp_h4_max <- pp[5]
  } else {
    raw_a <- read_fit(opt$`fit-a`, "fit_a"); raw_b <- read_fit(opt$`fit-b`, "fit_b")
    if (!is.na(raw_a$early_exit) || !is.na(raw_b$early_exit)) {
      method <- "none"
      out$none_reason <- sprintf("fit_early_exit:%s|%s", raw_a$early_exit, raw_b$early_exit)
      r <- list(summary = list(), n_snps = NA_integer_, keys = NULL)
      pp <- rep(NA_real_, 5)
    } else {
      fa <- load_fit(raw_a, opt$`fit-a`, ss_a, "fit_a"); fb <- load_fit(raw_b, opt$`fit-b`, ss_b, "fit_b")
      res <- coloc_pair_core(fa, fb, ti_a, ti_b, P, opt$mode, labels)
      method <- res$method; r <- res$r; pp <- res$pp
      out[names(res$out)] <- res$out
      out$name_map_a <- fa$name_map; out$name_map_b <- fb$name_map
    }
  }

  doc <- c(list(row_id = opt$`row-id`, arm = opt$arm, mode = opt$mode, method = method,
                trait_a = opt$`trait-a`, trait_b = opt$`trait-b`, ancestry = opt$ancestry, region_id = opt$`region-id`,
                type_a = ti_a$type, type_b = ti_b$type, sdY_a = ti_a$sdY, sdY_b = ti_b$sdY,
                p12_key = opt$`p12-key`, p1 = P$p1, p2 = P$p2, p12 = P$p12, overlap_min = P$overlap_min,
                trim_by_posterior = P$trim,
                n_snps = r$n_snps,
                variant_set_sha256 = if (is.null(r$keys)) NA_character_ else
                  digest::digest(paste(sort(r$keys, method = "radix"), collapse = "\n"), algo = "sha256", serialize = FALSE),
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
  cat(sprintf("[run_coloc_pair_r4] %s %s %s method=%s n_snps=%s pp_h4_max=%s none_reason=%s\n", opt$`row-id`,
              opt$arm, opt$`p12-key`, method, r$n_snps, format(out$pp_h4_max, digits = 6), out$none_reason))
}

if (sys.nframe() == 0L) main()
