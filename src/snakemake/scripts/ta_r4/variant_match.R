# Shared variant matching for ta_r4 R scripts (W3f N2, 15.7c F10): allele normalisation, the position + allele
# classification map_fit_names uses (run_coloc_pair_r4.R), and resolve_fit_names, which recovers the allele key of
# each fit variable name the way run_susie_rss.R built it (sumstats SNP_ID, panel-rsid override, blank -> CHR:POS,
# make.unique). Sourced by run_coloc_pair_r4.R and cs_cross_purity.R; defines functions only.

norm_allele <- function(x) toupper(trimws(as.character(x)))
missing_allele <- function(x) is.na(x) | norm_allele(x) %in% c("", "N", ".", "NA")
complement <- function(x) chartr("ACGT", "TGCA", x)
norm_chr <- function(x) sub("^CHR", "", norm_allele(x))

# Each candidate (sr[j], sa[j]) against reference alleles (r0, a0): exact, swapped (exact when basis is not REF/ALT),
# strand (complement of exact or swapped, non-palindromic SNVs only), mismatch, or no_alleles (s_miss[j]).
classify_alleles <- function(r0, a0, sr, sa, s_miss, basis) {
  snv <- nchar(r0) == 1 && nchar(a0) == 1
  pal <- snv && complement(r0) == a0
  vapply(seq_along(sr), function(j) {
    if (s_miss[j]) return("no_alleles")
    if (sr[j] == r0 && sa[j] == a0) return("exact")
    if (sr[j] == a0 && sa[j] == r0) return(if (basis == "REF/ALT") "swapped" else "exact")
    if (snv && !pal && nchar(sr[j]) == 1 && nchar(sa[j]) == 1 &&
        ((sr[j] == complement(r0) && sa[j] == complement(a0)) ||
         (sr[j] == complement(a0) && sa[j] == complement(r0)))) return("strand")
    "mismatch"
  }, character(1))
}

# One reference variant against the candidate rows at its position: status matched (j = the one compatible
# candidate, kind = its class), ambiguous (> 1 compatible, or 1 beside a candidate without alleles), no_alleles,
# or allele_mismatch.
match_at_position <- function(r0, a0, sr, sa, s_miss, basis) {
  cls <- classify_alleles(r0, a0, sr, sa, s_miss, basis)
  good <- cls %in% c("exact", "swapped", "strand")
  if (sum(good) == 1 && !any(cls == "no_alleles")) return(list(status = "matched", j = which(good), kind = cls[good]))
  if (sum(good) >= 1) return(list(status = "ambiguous", j = NA_integer_, kind = NA_character_))
  if (any(cls == "no_alleles")) return(list(status = "no_alleles", j = NA_integer_, kind = NA_character_))
  list(status = "allele_mismatch", j = NA_integer_, kind = NA_character_)
}

# A panel's variants as (chr, pos, ref, alt, basis): REF/ALT, else A2/A1 as an unordered pair.
panel_alleles <- function(pv) {
  has_ra <- all(c("REF", "ALT") %in% names(pv))
  has_a12 <- all(c("A1", "A2") %in% names(pv))
  basis <- if (has_ra) "REF/ALT" else if (has_a12) "A1/A2_unordered" else "none"
  n <- nrow(pv)
  list(id = as.character(pv$SNP_ID), chr = norm_chr(pv$CHR), pos = suppressWarnings(as.integer(pv$POS)),
       ref = if (has_ra) norm_allele(pv$REF) else if (has_a12) norm_allele(pv$A2) else rep(NA_character_, n),
       alt = if (has_ra) norm_allele(pv$ALT) else if (has_a12) norm_allele(pv$A1) else rep(NA_character_, n),
       basis = basis)
}

# Rows of `ss` (CHR, POS, REF, ALT) that run_susie_rss.R's allele-aware panel match keeps against panel `p`
# (panel_alleles): exact or swapped on a panel key that is not duplicated, usable alleles, no palindromic SNV.
panel_keeps <- function(ss, p) {
  ok_p <- !missing_allele(p$ref) & !missing_allele(p$alt) & !is.na(p$pos)
  k4 <- paste(p$chr, p$pos, p$ref, p$alt, sep = ":")
  k4[!ok_p] <- NA_character_
  dup <- duplicated(k4) | duplicated(k4, fromLast = TRUE)
  k4 <- k4[!dup & !is.na(k4)]
  sr <- norm_allele(ss$REF); sa <- norm_allele(ss$ALT)
  ok_s <- !missing_allele(sr) & !missing_allele(sa)
  pos <- paste(norm_chr(ss$CHR), suppressWarnings(as.integer(ss$POS)), sep = ":")
  pal <- nchar(sr) == 1L & nchar(sa) == 1L & paste0(sr, sa) %in% c("AT", "TA", "CG", "GC")
  ok_s & !pal & (paste(pos, sr, sa, sep = ":") %in% k4 | paste(pos, sa, sr, sep = ":") %in% k4)
}

# Allele key of each fit variable name. base = name without a trailing ".N". Routes, first with a candidate wins:
#   sumstats: window rows with SNP_ID == base whose key is in the catalog (exact, as run_susie_rss.R's join) and
#             kept by the fit panel (panel_keeps);
#   panel:    fit-panel rows with SNP_ID == base (the rsid override);
#   chrpos:   base as CHR:POS with exactly one fit-panel row.
# Keys are ordered by catalog order. ".N" rule: one key and a suffix = duplicate_row (resolved only under
# allow_duplicate_rows); k > 1 keys = refused_multi_key, or under allow_duplicate_rows the (N+1)-th key
# (bad_occurrence when N >= k). No candidate = unresolved.
# Returns a data.frame: name, base, route, status (ok / duplicate_row / refused_multi_key / bad_occurrence /
# unresolved), n_keys, chr, pos, ref, alt.
resolve_fit_names <- function(names, sumstats_window, catalog_order, fit_panel, allow_duplicate_rows = FALSE) {
  ss <- sumstats_window
  sid <- as.character(ss$SNP_ID)
  s_chr <- norm_chr(ss$CHR); s_pos <- suppressWarnings(as.integer(ss$POS))
  s_ref <- norm_allele(ss$REF); s_alt <- norm_allele(ss$ALT)
  ck <- paste(norm_chr(catalog_order$CHR), suppressWarnings(as.integer(catalog_order$POS)),
              norm_allele(catalog_order$REF), norm_allele(catalog_order$ALT), sep = ":")
  s_k <- paste(s_chr, s_pos, s_ref, s_alt, sep = ":")
  s_ord <- match(s_k, ck)
  p <- panel_alleles(fit_panel)
  s_in <- !is.na(sid) & !is.na(s_ord) & panel_keeps(ss, p)
  p_cp <- paste(p$chr, p$pos, sep = ":")
  cat_rank <- function(chr, pos, ref, alt) {
    o <- match(paste(chr, pos, ref, alt, sep = ":"), ck)
    o2 <- match(paste(chr, pos, alt, ref, sep = ":"), ck)
    ifelse(is.na(o), o2, o)
  }
  one <- function(nm) {
    suf <- grepl("\\.[0-9]+$", nm)
    base <- sub("\\.[0-9]+$", "", nm)
    occ <- if (suf) as.integer(sub("^.*\\.", "", nm)) else 0L
    keys <- NULL; route <- NA_character_
    h <- which(s_in & sid == base)
    if (length(h)) {
      keys <- data.frame(chr = s_chr[h], pos = s_pos[h], ref = s_ref[h], alt = s_alt[h], rank = s_ord[h])
      route <- "sumstats"
    } else {
      h <- which(p$id == base)
      if (!length(h)) {
        h <- which(p_cp == sub("^chr", "", base, ignore.case = TRUE))
        if (length(h) == 1) route <- "chrpos" else h <- integer(0)
      } else route <- "panel"
      if (length(h)) keys <- data.frame(chr = p$chr[h], pos = p$pos[h], ref = p$ref[h], alt = p$alt[h],
                                        rank = cat_rank(p$chr[h], p$pos[h], p$ref[h], p$alt[h]))
    }
    row <- function(status, k = NULL) data.frame(
      name = nm, base = base, route = route, status = status, n_keys = if (is.null(keys)) 0L else nrow(keys),
      chr = if (is.null(k)) NA_character_ else k$chr, pos = if (is.null(k)) NA_integer_ else k$pos,
      ref = if (is.null(k)) NA_character_ else k$ref, alt = if (is.null(k)) NA_character_ else k$alt,
      stringsAsFactors = FALSE)
    if (is.null(keys)) return(row("unresolved"))
    keys <- keys[order(is.na(keys$rank), keys$rank, seq_len(nrow(keys))), , drop = FALSE]
    keys <- keys[!duplicated(paste(keys$chr, keys$pos, keys$ref, keys$alt)), , drop = FALSE]
    k <- nrow(keys)
    if (k == 1) {
      if (suf && !isTRUE(allow_duplicate_rows)) return(row("duplicate_row", keys[1, ]))
      return(row("ok", keys[1, ]))
    }
    if (!isTRUE(allow_duplicate_rows)) return(row("refused_multi_key"))
    if (occ >= k) return(row("bad_occurrence"))
    row("ok", keys[occ + 1L, ])
  }
  if (!length(names)) return(data.frame(name = character(), base = character(), route = character(),
                                         status = character(), n_keys = integer(), chr = character(),
                                         pos = integer(), ref = character(), alt = character()))
  do.call(rbind, lapply(names, one))
}
