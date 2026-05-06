# src/R/regularization/snp_id_bridge.R
# ta-r3 W1 — chr:pos <-> rsid bridge for variant-ID convention drift
# between harmonized sumstats and per-region LD reference panels.
#
# Background
# ----------
# The harmonized-sumstats SNP_ID column at
# data/processed/sumstats_harmonized/{trait}.{ANC}.tsv.bgz is rsid for some
# upstream sources (e.g. asthma, bmi → "rs7957299") and chr:pos for others
# (e.g. hypertension, stroke, t2d → "12:111000057"). The per-region 1KG-EUR
# LD reference at data/processed/ld_reference/{ANC}/{REGION}.rds carries a
# $variants data.frame in which $SNP_ID is exclusively rsid (verified
# 2026-05-06 against SH2B3_12q24.rds: 895 / 895 rsids).
#
# Naive intersect(ld$variants$SNP_ID, sumstats$SNP_ID) returns 0 for the
# chr:pos sumstats and hard-fails any downstream fine-mapping that needs a
# common variant key (e.g. susieR::susie_rss subsetting via R[overlap,
# overlap]).
#
# This is the same class of bug previously fixed in commits 069b34f
# (run_qtl_coloc.R: tries {rsid, chrpos, variant_id} keys, picks max overlap)
# and 7d54183 (run_susie_rss.R: overrides chr:pos sumstats SNP_IDs with
# LD-side rsids). Neither fix exposed a reusable utility, so the new
# PSD-regularized fitter scaffolded in bccd0d6
# (src/R/regularization/refit_sh2b3_psd_regularized.R) re-introduced the
# defect. This file extracts the bridge so the same logic can be reused by
# any future R analysis that joins sumstats to a 1KG-EUR LD panel.
#
# API
# ---
#   bridge_snp_id_to_ld_ref(sumstats, ld_variants,
#                            chr_col      = "CHR",
#                            pos_col      = "POS",
#                            snp_id_col   = "SNP_ID",
#                            ld_chr_col   = "CHR",
#                            ld_pos_col   = "POS",
#                            ld_snp_id_col = "SNP_ID",
#                            verbose      = TRUE)
#
#     Returns a copy of `sumstats` with column `snp_id_col` overwritten to
#     match the LD-side convention WHERE a (CHR, POS) match exists in
#     `ld_variants`. Rows that fail to bridge keep their original SNP_ID
#     (downstream intersect() will simply drop them, same as before).
#
#     `sumstats`     : data.table or coercible to one; must contain
#                      chr_col, pos_col, snp_id_col.
#     `ld_variants`  : data.frame or data.table; must contain ld_chr_col,
#                      ld_pos_col, ld_snp_id_col.
#
# Behavior contract
# -----------------
#   1. NEVER regress overlap: if sumstats$SNP_ID already matched a row of
#      ld_variants$SNP_ID, that row's SNP_ID is preserved.
#   2. Bridge ONLY when the sumstats SNP_ID is non-rsid (chr:pos or NA/blank)
#      AND the LD-ref has a clean rsid for that (CHR, POS) tuple. This
#      mirrors the conservative override in commit 7d54183.
#   3. Idempotent: calling twice yields the same result as calling once.
#   4. No side effects on the caller's sumstats data.table (returns a copy).

suppressPackageStartupMessages({
  library(data.table)
})

# --- helpers ---------------------------------------------------------------

# Match the rsid pattern used in commit 7d54183.
.is_rsid <- function(x) grepl("^rs[0-9]+$", x)
# Match chr:pos on autosomes 1-22 + X/Y; integer pos.
.is_chrpos <- function(x) grepl("^[0-9XY]+:[0-9]+$", x)

# --- main ------------------------------------------------------------------

bridge_snp_id_to_ld_ref <- function(sumstats,
                                    ld_variants,
                                    chr_col       = "CHR",
                                    pos_col       = "POS",
                                    snp_id_col    = "SNP_ID",
                                    ld_chr_col    = "CHR",
                                    ld_pos_col    = "POS",
                                    ld_snp_id_col = "SNP_ID",
                                    verbose       = TRUE) {
  stopifnot(is.data.frame(sumstats), is.data.frame(ld_variants))
  ss <- as.data.table(sumstats)  # copy; never mutate caller
  ld <- as.data.table(ld_variants)

  for (col in c(chr_col, pos_col, snp_id_col)) {
    if (!col %in% names(ss)) {
      stop(sprintf("bridge_snp_id_to_ld_ref: sumstats missing column '%s'", col))
    }
  }
  for (col in c(ld_chr_col, ld_pos_col, ld_snp_id_col)) {
    if (!col %in% names(ld)) {
      stop(sprintf("bridge_snp_id_to_ld_ref: ld_variants missing column '%s'", col))
    }
  }

  # Normalize CHR + POS types for the join key (silent coercion mirrors
  # run_susie_rss.R load_ld_matrix). data.table's join is type-strict, so
  # both sides must agree on character vs integer.
  ss[, (chr_col)    := as.character(get(chr_col))]
  ss[, (pos_col)    := as.integer(get(pos_col))]
  ss[, (snp_id_col) := as.character(get(snp_id_col))]
  ld[, (ld_chr_col)    := as.character(get(ld_chr_col))]
  ld[, (ld_pos_col)    := as.integer(get(ld_pos_col))]
  ld[, (ld_snp_id_col) := as.character(get(ld_snp_id_col))]

  # Build a (CHR, POS) -> ld_rsid lookup. If duplicate (CHR, POS) tuples
  # exist in the LD ref (multi-allelic), we keep the FIRST rsid — same
  # collision policy as positional row-index alignment in load_ld_matrix.
  ld_lookup <- ld[, .SD[1L], by = c(ld_chr_col, ld_pos_col)][
    , .(chr_key = get(ld_chr_col),
        pos_key = get(ld_pos_col),
        ld_rsid = get(ld_snp_id_col))
  ]
  setkey(ld_lookup, chr_key, pos_key)

  # Join sumstats -> ld_lookup on (CHR, POS).
  ss[, .row_idx := .I]
  ss[, .chr_key := get(chr_col)]
  ss[, .pos_key := get(pos_col)]
  joined <- ld_lookup[ss, on = .(chr_key = .chr_key, pos_key = .pos_key)]
  setorder(joined, .row_idx)

  current  <- joined[[snp_id_col]]
  proposed <- joined$ld_rsid

  is_rsid_ld     <- !is.na(proposed) & .is_rsid(proposed)
  is_chrpos_ss   <- !is.na(current) & .is_chrpos(current)
  is_blank_ss    <- is.na(current) | current == "" | current == "NA"
  is_already_rs  <- !is.na(current) & .is_rsid(current)

  # Conservative override: replace ONLY when the LD has a clean rsid AND
  # the sumstats id is chr:pos or blank. Already-rsid ids are preserved.
  replace_mask <- is_rsid_ld & (is_chrpos_ss | is_blank_ss) & !is_already_rs

  if (verbose) {
    n_total      <- length(current)
    n_already_rs <- sum(is_already_rs)
    n_replaced   <- sum(replace_mask)
    n_chrpos_unmatched <- sum(is_chrpos_ss & !is_rsid_ld)
    message(sprintf(
      "[snp_id_bridge] n=%d already_rsid=%d bridged=%d chrpos_unbridgeable=%d",
      n_total, n_already_rs, n_replaced, n_chrpos_unmatched
    ))
  }

  # Apply the override and clean up scratch columns. data.table's [<-
  # semantics requires character to match column type.
  ss[replace_mask, (snp_id_col) := proposed[replace_mask]]
  ss[, c(".row_idx", ".chr_key", ".pos_key") := NULL]

  ss
}
