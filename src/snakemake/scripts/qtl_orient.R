# qtl_orient.R -- D-06 unit 3 (ta-r4). Sourced by run_qtl_coloc.R only under --qtl-orient true.
#
# qtl_orient_vector(variant_id, panel_ref, panel_alt)
#   QTL betas are signed on the ALT of their own variant_id (chr{c}_{pos}_{ref}_{alt}). Compared against the
#   bound panel row's REF/ALT: exact -> +1, transposed -> -1; palindromic (A/T, C/G), mismatched and
#   unparseable variant_ids -> NA (the caller drops them). Returns list(orient, counts).

qtl_orient_vector <- function(variant_id, panel_ref, panel_alt) {
  up <- function(x) toupper(trimws(as.character(x)))
  vid <- up(variant_id)
  m <- regmatches(vid, regexec("^CHR[0-9XY]+_[0-9]+_([ACGT]+)_([ACGT]+)$", vid))
  q_ref <- vapply(m, function(x) if (length(x) == 3L) x[2] else NA_character_, character(1))
  q_alt <- vapply(m, function(x) if (length(x) == 3L) x[3] else NA_character_, character(1))
  p_ref <- up(panel_ref)
  p_alt <- up(panel_alt)

  unparseable <- is.na(q_ref)
  pal <- !unparseable & nchar(q_ref) == 1L & nchar(q_alt) == 1L &
    paste0(q_ref, q_alt) %in% c("AT", "TA", "CG", "GC")
  ok <- !unparseable & !pal
  exact <- ok & !is.na(p_ref) & !is.na(p_alt) & q_ref == p_ref & q_alt == p_alt
  flipped <- ok & !is.na(p_ref) & !is.na(p_alt) & q_ref == p_alt & q_alt == p_ref
  exact[is.na(exact)] <- FALSE
  flipped[is.na(flipped)] <- FALSE
  orient <- ifelse(exact, 1, ifelse(flipped, -1, NA_real_))

  list(orient = orient,
       counts = list(exact = sum(exact), flipped = sum(flipped),
                     dropped_palindromic = sum(pal),
                     dropped_mismatch = sum(ok & !exact & !flipped),
                     dropped_unparseable = sum(unparseable)))
}
