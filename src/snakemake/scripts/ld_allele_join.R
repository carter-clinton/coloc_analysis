#!/usr/bin/env Rscript
# ==========================================================================
# ld_allele_join.R -- the SHARED allele-aware 4-key join.
#
# 260805-w7u, m3-04c blast-radius FINDING E (gate row
# `m3-04c-BLAST-RADIUS.md:141`, "Any GWAS x QTL colocalization"), together with
# the coloc-side KEY defect that closing E alone would have activated.
#
# `source()`-able, side-effect free, no top-level execution. Exports:
#
#     ld_allele_join_indices(subset_dt, variants_dt)
#         -> list(keep = <integer subset row indices>,
#                 ld   = <integer variants row indices, parallel to keep>,
#                 orient = <numeric +1 / -1, parallel to keep>,
#                 counts = list(exact, flipped, dropped_ambiguous,
#                               dropped_palindromic, dropped_mismatch,
#                               dropped_unusable, reject))
#
# Both frames need CHR / POS / REF / ALT.
#
# --------------------------------------------------------------------------
# (a) THIS IS A DELIBERATE SECOND IMPLEMENTATION. SAY SO OUT LOUD.
# --------------------------------------------------------------------------
# The identical join already exists, inside
# `src/legacy/region_analysis/scripts/run_susie_rss.R` -- the nested closure
# `match_indices_allele_aware` at :220-323, landed by 260805-o7o to close
# blast-radius finding H. A second independent allele-key implementation is
# EXACTLY how finding H came to exist in two places to begin with, so this file
# needs a justification, not a shrug.
#
# (b) THE FROZEN-FILE REASON IT IS NOT AN EXTRACTION.
# --------------------------------------------------------------------------
# `run_susie_rss.R` is RE-FROZEN at `bf04199` (re-pinned 2026-08-06 by
# `quick-260806-pd3` for blast-radius finding K-1; `AUTH-K1-UNFREEZE` is SPENT,
# as is the unfreeze granted 2026-08-05). A pure-move extraction is still a
# frozen-file edit, and would need its own
# `identical()`-on-the-whole-`load_ld_matrix`-result proof at `allele_aware`
# TRUE **and** FALSE. That is a reviewed task of its own, not a rider on this
# one -- and see (d): it was EVALUATED against an OPEN window and still
# DEFERRED.
#
# (c) AGREEMENT IS MACHINE-CHECKED, NOT PROMISED.
# --------------------------------------------------------------------------
# `tests/m3/test_qtl_coloc_allele_join.py` drives the SHIPPED matcher -- obtained
# from the real frozen source by a body-walk extraction of the assignment
# expression, never hand-copied -- and this implementation, on the SAME
# fixtures, and asserts identical `keep`, `ld`, `orient` and all six counters on
# every disposition class. Two negative controls back it: perturbing THIS file
# turns the agreement test RED, and pointing the extractor at a deliberately
# ALTERED copy of `run_susie_rss.R` also turns it RED (proving the "shipped"
# side really tracks the shipped source and is not a stand-in). Drift is
# therefore a test failure on every suite run rather than a discipline anyone
# has to maintain.
#
# (d) THE NAMED FOLLOW-UP -- EVALUATED 2026-08-06 AND **DEFERRED**.
# --------------------------------------------------------------------------
#     The proposal: replace `run_susie_rss.R:220-323` with
#     `source("src/snakemake/scripts/ld_allele_join.R")`.
#
#     `quick-260806-pd3` opened a freeze window on `run_susie_rss.R` for an
#     INDEPENDENT reason (blast-radius finding K-1) and deliberately did NOT
#     take this rider, so the "next time the freeze is opened" trigger has now
#     fired once and been declined on the merits. Four findings, all measured:
#
#     1. DECISIVE. `run_susie_rss.R` contains **ZERO `source()` calls today**
#        (`grep -c "source(" -> 0`). The extraction would introduce a
#        FIRST-OF-ITS-KIND runtime file dependency on the exact code path the
#        ~11-day / $385-1,084 AoU fire exercises. A failed `source()` at fire
#        time is a catastrophic, expensive failure mode THAT DOES NOT EXIST
#        TODAY.
#     2. The duplication is ALREADY drift-guarded on EVERY suite run by
#        `tests/m3/test_qtl_coloc_allele_join.py`'s differential agreement test
#        plus NC-2f / NC-2g, which body-walk the SHIPPED closure out of the real
#        source. The benefit is STYLE, not SAFETY.
#     3. THE PATH MECHANISM IS WIDER THAN ASSUMED. `run_qtl_coloc.R` does NOT
#        resolve this file via a CLI argument: `--ld-allele-join`
#        (`run_qtl_coloc.R:62`) is a BOOLEAN flag, and the PATH is resolved
#        SCRIPT-RELATIVELY at `run_qtl_coloc.R:153`
#        (`file.path(.script_dir(), "ld_allele_join.R")`). `run_susie_rss.R`
#        lives in `src/legacy/region_analysis/scripts/`, so `.script_dir()`
#        would NOT find this file -- a genuinely NEW path mechanism (a new CLI
#        argument threaded from `finemap.smk`, or a repo-root walk) would be
#        required.
#     4. Technically feasible: `.up`, `.usable`, `.allele_counts0`
#        (`run_susie_rss.R:210-218`) are referenced ONLY at `:223` and
#        `:237-249`, all inside the closure's own body, whose sole call site is
#        `:332`. Nothing else in `load_ld_matrix` uses them. This removes an
#        objection but supplies no justification.
#
#     **FREEZE ECONOMY IS NOT SUFFICIENT JUSTIFICATION TO ACCEPT FIRE-PATH
#     RISK.** Points 1 and 3 stand regardless of how cheap the window is.
#
#     ANY FUTURE ATTEMPT MUST SATISFY ALL THREE:
#       (i)   a FAIL-CLOSED-AND-LOUD design -- a missing or unsourceable shared
#             file must STOP with a named error and must NEVER degrade to a
#             position-only match. That degradation **IS finding H**.
#       (ii)  an `identical()`-on-the-whole-`load_ld_matrix`-result proof at
#             `allele_aware` TRUE **and** FALSE against the then-current pin
#             (`bf04199` as of 2026-08-06).
#       (iii) a RE-FREEZE re-pin at the new SHA, after which
#             `git diff --exit-code <new-sha> -- run_susie_rss.R` becomes the
#             forward gate.
#
#     This file stays deliberately shaped as a drop-in `source()` target so the
#     change remains a delete-and-source, not a rewrite, if it is ever taken.
#
# --------------------------------------------------------------------------
# THE ORIENTATION CONTRACT (carried over verbatim in substance from the shipped
# implementation, because it is what makes the dispositions correct):
#   * PANEL. src/python/plink_ld_to_npz.py:29-35 -- under plink
#     --keep-allele-order the .bim A1 == ALT == alleles[1] and A2 == REF, and the
#     canonical vid is {chr}:{bp}:{REF}:{ALT}. plink --r signs the correlation on
#     A1 dosage, i.e. on ALT.
#   * The variant catalog ({ld_reference}/variants/{region}.tsv) carries
#     CHR/POS/REF/ALT/SNP_ID sourced from the harmonized sumstats, where ALT is
#     the EFFECT allele.
#   => Both sides code on ALT; a TRANSPOSED pair is a bookkeeping difference,
#      recorded in `orient`, not bad data.
#
# ⚠ THIS FILE RESOLVES ROW BINDING. IT DOES NOT APPLY `orient` TO ANYTHING.
#   Callers decide. `run_susie_rss.R` negates z. `run_qtl_coloc.R` deliberately
#   does NOT (see E-2 in `.planning/phases/m3-aou-afr-ld-panel-build/
#   deferred-items.md`): the QTL-beta <-> panel-ALT orientation is pre-existing
#   on the legacy 1kG/EUR path and correcting it would move Track-A numbers that
#   are in submission. What this join buys the coloc path today is the
#   ROW-BINDING half -- a multiallelic site binding to an arbitrary ALT's LD ROW
#   is a wrong-row error independent of sign -- plus the counters that make E-2's
#   magnitude MEASURABLE instead of invisible.
#
# DISPOSITIONS (all counted; a write-only counter is not observability, so every
# one of these reaches the per-pair JSON and the per-pair log receipt):
#   chr:pos hit + (REF,ALT) exact       -> KEEP, orient +1   `exact`
#   chr:pos hit + (REF,ALT) transposed  -> KEEP, orient -1   `flipped`
#   palindromic (A/T, T/A, C/G, G/C)    -> DROP              `dropped_palindromic`
#   position present, no compatible pair-> DROP              `dropped_mismatch`
#   >1 panel row shares the 4-key       -> DROP              `dropped_ambiguous`
#   REF/ALT missing / "" / "N" / NA     -> DROP              `dropped_unusable`
#   position absent from the panel      -> ordinary non-overlap, NOT counted
#
# WHY PALINDROMES ARE DROPPED, specific to THIS panel rather than boilerplate:
# src/scripts/ld_npz_to_rds.R:348-361 (liftover_one) lifts GRCh38->GRCh37 and
# re-forms the vid carrying `ref` and `alt` through VERBATIM -- it does not
# complement them. A strand-inverted chain block therefore yields a panel
# REF/ALT reverse-complemented relative to GRCh37. For a NON-palindromic variant
# that surfaces as an allele MISMATCH: detectable, countable, droppable. For a
# PALINDROMIC one it surfaces as an EXACT MATCH that is silently sign-wrong --
# the ONE class whose error is invisible from the allele codes alone. Dropping
# them removes the sole undetectable failure mode. Deliberately NOT configurable:
# a knob here is just another silent lever.
#
# Two match() calls on 4-keys, no loop: multiallelics are disambiguated BY
# CONSTRUCTION rather than by a tie-break someone has to trust.
# ==========================================================================

.up <- function(x) toupper(trimws(as.character(x)))

.usable <- function(x) {
  x <- .up(x)
  !is.na(x) & nzchar(x) & x != "N"
}

.allele_counts0 <- function(reject = NULL) {
  list(exact = 0L, flipped = 0L, dropped_ambiguous = 0L,
       dropped_palindromic = 0L, dropped_mismatch = 0L,
       dropped_unusable = 0L, reject = reject)
}

ld_allele_join_indices <- function(subset_dt, variants_dt) {
  empty <- function(reject = NULL) list(
    keep = integer(0), ld = integer(0), orient = numeric(0),
    counts = .allele_counts0(reject))

  need <- c("CHR", "POS", "REF", "ALT")
  # THE TWO VERIFICATION-IMPOSSIBLE CASES. These are STRUCTURED REJECTIONS,
  # never a fallback: silently degrading to a position-only match in either is
  # PRECISELY the defect this join exists to close. The caller must treat a
  # non-NULL `reject` as fatal under the gate -- returning zero rows quietly is
  # how "no colocalization found" comes to read as a scientific result.
  if (is.null(variants_dt) || !all(need %in% names(variants_dt))) {
    return(empty("alleles_unavailable_panel"))
  }
  if (is.null(subset_dt) || !all(need %in% names(subset_dt))) {
    return(empty("alleles_unavailable_sumstats"))
  }
  pan_ref <- .up(variants_dt$REF)
  pan_alt <- .up(variants_dt$ALT)
  pan_ok <- .usable(pan_ref) & .usable(pan_alt)
  if (!any(pan_ok)) return(empty("alleles_unavailable_panel"))
  sub_ref <- .up(subset_dt$REF)
  sub_alt <- .up(subset_dt$ALT)
  sub_ok <- .usable(sub_ref) & .usable(sub_alt)
  if (!any(sub_ok)) return(empty("alleles_unavailable_sumstats"))

  pan_pos <- suppressWarnings(as.integer(variants_dt$POS))
  sub_pos <- suppressWarnings(as.integer(subset_dt$POS))
  pan_chr <- .up(variants_dt$CHR)
  sub_chr <- .up(subset_dt$CHR)
  pos_key_pan <- paste(pan_chr, pan_pos, sep = ":")
  pos_key_sub <- paste(sub_chr, sub_pos, sep = ":")
  # paste() renders NA as the literal "NA", so an unparseable coordinate would
  # otherwise become a REAL key that can collide. Null them explicitly.
  pos_key_pan[is.na(pan_chr) | is.na(pan_pos)] <- NA_character_
  pos_key_sub[is.na(sub_chr) | is.na(sub_pos)] <- NA_character_

  k4_pan <- paste(pos_key_pan, pan_ref, pan_alt, sep = ":")
  k4_pan[!pan_ok | is.na(pos_key_pan)] <- NA_character_
  # AMBIGUITY GUARD. A 4-key that appears twice in the panel cannot be bound to
  # a single LD row, so it is removed from the match TABLE entirely -- the
  # 260805-23d "a fallback that is never constructed cannot be silently taken"
  # discipline.
  dup4 <- duplicated(k4_pan) | duplicated(k4_pan, fromLast = TRUE)
  dup_pos <- unique(pos_key_pan[dup4 & !is.na(k4_pan)])
  k4_pan[dup4] <- NA_character_
  # match(NA, table) HITS an NA in the table, so every nulled panel key gets a
  # unique unmatchable sentinel instead of staying NA.
  na_pan <- which(is.na(k4_pan))
  if (length(na_pan) > 0) {
    k4_pan[na_pan] <- paste0("NO_PANEL_KEY", na_pan)
  }

  k4_exact <- paste(pos_key_sub, sub_ref, sub_alt, sep = ":")
  k4_swap <- paste(pos_key_sub, sub_alt, sub_ref, sep = ":")
  bad_sub <- !sub_ok | is.na(pos_key_sub)
  k4_exact[bad_sub] <- NA_character_
  k4_swap[bad_sub] <- NA_character_

  m_exact <- match(k4_exact, k4_pan)
  m_swap <- match(k4_swap, k4_pan)
  m_exact[is.na(k4_exact)] <- NA_integer_
  m_swap[is.na(k4_swap)] <- NA_integer_

  pal <- nchar(sub_ref) == 1L & nchar(sub_alt) == 1L &
    paste0(sub_ref, sub_alt) %in% c("AT", "TA", "CG", "GC")
  pal[is.na(pal)] <- FALSE
  unus <- bad_sub
  posin <- !is.na(pos_key_sub) & (pos_key_sub %in% pos_key_pan[!is.na(pos_key_pan)])
  amb <- posin & is.na(m_exact) & is.na(m_swap) & (pos_key_sub %in% dup_pos)

  keep_mask <- !unus & !pal & (!is.na(m_exact) | !is.na(m_swap))
  m_use <- ifelse(!is.na(m_exact), m_exact, m_swap)
  orient_all <- ifelse(!is.na(m_exact), 1, -1)

  keep_idx <- which(keep_mask)
  ld_idx <- as.integer(m_use[keep_mask])
  orient <- as.numeric(orient_all[keep_mask])
  # THE order(keep_idx) LOCKSTEP -- applied to keep_idx, ld_idx AND orient
  # TOGETHER. Letting `orient` fall out of step with `keep_idx` is the one way
  # this join could itself produce a sign error, and 260805-o7o caught exactly
  # that defect on the fine-map side by breaking this line as a control.
  if (length(keep_idx) > 0) {
    ord <- order(keep_idx)
    keep_idx <- keep_idx[ord]
    ld_idx <- ld_idx[ord]
    orient <- orient[ord]
  }

  counts <- list(
    exact = as.integer(sum(keep_mask & !is.na(m_exact))),
    flipped = as.integer(sum(keep_mask & is.na(m_exact))),
    dropped_ambiguous = as.integer(sum(amb)),
    dropped_palindromic = as.integer(sum(!unus & pal & posin)),
    dropped_mismatch = as.integer(sum(!unus & !pal & posin &
                                        is.na(m_exact) & is.na(m_swap) & !amb)),
    # NOTE: `dropped_unusable` is the SUBSET-side allele-less class. A row whose
    # PANEL counterpart has the unusable alleles cannot bind either and is
    # counted under `dropped_mismatch` -- still dropped, still counted, only the
    # label differs. Carried over deliberately so the two implementations agree
    # on the labelling as well as on the arithmetic.
    dropped_unusable = as.integer(sum(unus & posin)),
    reject = NULL
  )
  list(keep = keep_idx, ld = ld_idx, orient = orient, counts = counts)
}
