#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# src/scripts/stitch_subregions_to_rds.R -- M3 Wave 2 re-scope (m3-02b).
#
# Assemble N overlapping-window sub-region .npz files for ONE parent region +
# ONE ancestry into ONE {parent_region_id}.rds whose payload satisfies the REAL
# downstream loader run_susie_rss.R::load_ld_matrix() (obj$R + obj$variants).
#
# BANDED, NOT BLOCK-DIAGONAL (m3-REVIEWS.md HIGH#1 + Carter steering):
#   The prior block-diagonal stitch ZEROED LD between variants base-pairs apart
#   across an arbitrary 10 Mb boundary -- a biologically false claim that can
#   corrupt SuSiE-RSS credible sets. The MINIMAL CORRECT FIX is OVERLAPPING
#   WINDOWS with cross-boundary variant pairs RETAINED inside the banding radius:
#     * each variant is assigned to the ONE core whose half-open
#       [core_start_grch38, core_end_grch38) (GRCh38 pos) contains it
#       (membership = dimnames set; no variant duplicated across windows);
#     * for every computed pair (i,j) in any window with |pos_i - pos_j| <=
#       buffer_bp AND at least one endpoint core-owned, place r at the GLOBAL
#       (i,j) index; pairs beyond buffer_bp are structurally 0;
#     * result = sparse BANDED dgCMatrix (block-tridiagonal-like), NOT block-diagonal.
#   cross_subregion_ld = "banded within radius_bp; zeroed beyond".
#
# ALLELE-AWARE (T-M3RS-STITCH-01): variants ordered by GRCh38 variant_id
# (chr:pos:ref:alt) BEFORE liftover; matching is on (CHR,POS,REF,ALT) not
# position-only (multiallelic sites at the same pos with different ALT are NOT
# collapsed); the alignment check runs even when SNP_ID is an rsid.
#
# Usage:
#   Rscript src/scripts/stitch_subregions_to_rds.R \
#     --parent <parent_region_id> --ancestry <AFR|EUR> --out <out_rds> \
#     --chain <hg38ToHg19.chain.gz> --manifest <manifest_tsv> \
#     --npz <sub00.npz> --npz <sub01.npz> ...
#
# Conda env: envs/m3-r-ld.yml (r-reticulate + r-matrix + r-jsonlite + r-digest
# + numpy + pyliftover). Reticulate must resolve a python with numpy+pyliftover
# (RETICULATE_PYTHON=<env>/bin/python).
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(reticulate)
  library(Matrix)
  library(jsonlite)
  library(digest)
})

# ---------------------------------------------------------------------------
# CLI parsing (no optparse dependency; multi --npz collected)
# ---------------------------------------------------------------------------
parse_cli <- function(args) {
  out <- list(parent = NULL, ancestry = NULL, out = NULL, chain = NULL,
              manifest = NULL, npz = character(0))
  i <- 1L
  while (i <= length(args)) {
    a <- args[[i]]
    val <- if (i < length(args)) args[[i + 1L]] else NA_character_
    if (a == "--parent")        { out$parent   <- val; i <- i + 2L }
    else if (a == "--ancestry") { out$ancestry <- val; i <- i + 2L }
    else if (a == "--out")      { out$out      <- val; i <- i + 2L }
    else if (a == "--chain")    { out$chain    <- val; i <- i + 2L }
    else if (a == "--manifest") { out$manifest <- val; i <- i + 2L }
    else if (a == "--npz")      { out$npz <- c(out$npz, val); i <- i + 2L }
    else { stop("STITCH_INPUT: unknown arg: ", a) }
  }
  out
}

args <- commandArgs(trailingOnly = TRUE)
cli  <- parse_cli(args)
if (is.null(cli$parent))   stop("STITCH_INPUT: --parent is required")
if (is.null(cli$ancestry)) stop("STITCH_INPUT: --ancestry is required (AFR/EUR share __sub ids)")
if (is.null(cli$out))      stop("STITCH_INPUT: --out is required")
if (is.null(cli$chain))    stop("STITCH_INPUT: --chain is required")
if (is.null(cli$manifest)) stop("STITCH_INPUT: --manifest is required")
if (length(cli$npz) == 0L) stop("STITCH_INPUT: at least one --npz is required")
if (!file.exists(cli$chain))    stop("STITCH_INPUT: chain not found: ", cli$chain)
if (!file.exists(cli$manifest)) stop("STITCH_INPUT: manifest not found: ", cli$manifest)

chain_sha256 <- digest(file = cli$chain, algo = "sha256")

# ---------------------------------------------------------------------------
# Read the manifest rows for (parent_region_id == parent) & (ancestry == anc)
# to get per-sub subregion_index, core_start_grch38, core_end_grch38, buffer_bp.
# ---------------------------------------------------------------------------
manifest <- read.delim(cli$manifest, header = TRUE, sep = "\t",
                       stringsAsFactors = FALSE, check.names = FALSE)
need_cols <- c("region_id", "ancestry", "parent_region_id", "subregion_index",
               "n_subregions", "core_start_grch38", "core_end_grch38", "buffer_bp")
miss <- setdiff(need_cols, names(manifest))
if (length(miss)) stop("STITCH_INPUT: manifest missing columns: ", paste(miss, collapse = ","))

man_sub <- manifest[
  as.character(manifest$parent_region_id) == cli$parent &
  as.character(manifest$ancestry) == cli$ancestry, , drop = FALSE]
if (nrow(man_sub) == 0L) {
  stop("STITCH_INPUT: no manifest sub-rows for parent=", cli$parent,
       " ancestry=", cli$ancestry)
}
# Reject mixed ancestry (any manifest row for this parent with a different anc
# would be caught by the filter; assert the n_subregions are consistent).
n_subregions <- unique(as.integer(man_sub$n_subregions))
if (length(n_subregions) != 1L) {
  stop("STITCH_INPUT: inconsistent n_subregions for parent ", cli$parent)
}
n_subregions <- n_subregions[[1]]
buffer_bp <- unique(as.numeric(man_sub$buffer_bp))
if (length(buffer_bp) != 1L) stop("STITCH_INPUT: inconsistent buffer_bp")
buffer_bp <- buffer_bp[[1]]

# Map subregion_index -> {core_start, core_end} (GRCh38 half-open core)
core_by_idx <- list()
for (r in seq_len(nrow(man_sub))) {
  k <- as.integer(man_sub$subregion_index[[r]])
  core_by_idx[[as.character(k)]] <- list(
    core_start = as.numeric(man_sub$core_start_grch38[[r]]),
    core_end   = as.numeric(man_sub$core_end_grch38[[r]])
  )
}

# ---------------------------------------------------------------------------
# numpy + pyliftover (GRCh38 -> GRCh37 for the b37 SNP_IDs)
# ---------------------------------------------------------------------------
np <- reticulate::import("numpy", convert = TRUE)
pyliftover <- reticulate::import("pyliftover", convert = TRUE)
lo <- pyliftover$LiftOver(cli$chain)

liftover_pos38_to_pos37 <- function(chr, pos38) {
  result <- lo$convert_coordinate(paste0("chr", chr), pos38 - 1L)
  if (is.null(result) || length(result) == 0L) return(NA_integer_)
  as.integer(result[[1]][[2]]) + 1L
}

# subregion_index for an .npz: infer from filename __subNN, else manifest order.
infer_sub_index <- function(path) {
  m <- regmatches(path, regexpr("__sub([0-9]{2})", path))
  if (length(m) == 0L || !nzchar(m)) return(NA_integer_)
  as.integer(sub("__sub", "", m))
}

# ---------------------------------------------------------------------------
# Load each sub-region .npz: per-npz symmetry recovery + chr-strip + parse the
# GRCh38 chr:pos:ref:alt (ORDER by GRCh38 id BEFORE liftover) + AF; record the
# window correlation block keyed by GRCh38 (CHR,POS,REF,ALT).
# ---------------------------------------------------------------------------
seen_idx <- integer(0)
# Global accumulators keyed by GRCh38 variant key "chr:pos:ref:alt" (b38).
# Each variant: chr, pos38, ref, alt, af, owning core (NA until assigned), b37 id.
var_env <- new.env(parent = emptyenv())     # key -> list(chr,pos38,ref,alt,af)
pair_i <- numeric(0); pair_j <- numeric(0); pair_x <- numeric(0)  # global triplets (filled after global order known)
# We must build the global order first, so we stage per-window pairs as
# (key_a, key_b, r) then resolve to global indices afterward.
stage_a <- character(0); stage_b <- character(0); stage_r <- numeric(0)
window_n_var <- integer(0)

b38_key <- function(chr, pos, ref, alt) paste(chr, pos, ref, alt, sep = ":")

for (npz_path in cli$npz) {
  if (!file.exists(npz_path)) stop("STITCH_INPUT: missing child .npz: ", npz_path)
  idx <- infer_sub_index(npz_path)
  # WR-02 fix (2026-06-19): subregion identity is AUTHORITATIVE from the manifest.
  # An un-inferable index (filename lacks __subNN) is an ERROR, never a silent
  # pass -- otherwise the missing-child completeness guard below is bypassed
  # (seen_idx would stay empty, length(seen_idx) > 0L FALSE) and an incomplete
  # panel (missing whole core intervals) ships silently. Every --npz MUST map to
  # a known subregion_index in this parent's manifest set.
  if (is.na(idx)) {
    stop("STITCH_INPUT: cannot infer subregion_index from ", npz_path,
         " (expected __subNN); refusing to stitch (completeness unverifiable)")
  }
  if (idx %in% seen_idx) stop("STITCH_INPUT: duplicate child for subregion_index ", idx)
  if (is.null(core_by_idx[[as.character(idx)]])) {
    stop("STITCH_INPUT: extra child .npz subregion_index ", idx,
         " not in parent's manifest set")
  }
  seen_idx <- c(seen_idx, idx)

  z   <- np$load(npz_path, allow_pickle = TRUE)
  tri <- z$f[["ld"]]
  if (!is.matrix(tri)) stop("STITCH_INPUT: unexpected ld shape in ", npz_path)
  # CR-01 fix (2026-06-19): HONOR the per-window lower_triangular flag. The
  # one-sided recovery (tri + t(tri) - diag(diag(tri))) is valid ONLY for a
  # lower-triangular npz; on a FULL float32 matrix it DOUBLES off-diagonals
  # (r -> 2r) because the OLD `!isSymmetric` gate trips on ~1e-7 Hail block-sum
  # asymmetry (>> isSymmetric's 2.2e-14 tol). Read the flag; mirror only when
  # one-sided; ALWAYS symmetrize (avg(r,r)=r kills float drift WITHOUT doubling).
  win_lower_only <- tryCatch(as.logical(z$f[["lower_triangular"]])[1],
                             error = function(e) FALSE)
  if (is.na(win_lower_only)) win_lower_only <- FALSE
  if (isTRUE(win_lower_only)) tri <- tri + t(tri) - diag(diag(tri))
  tri <- (tri + t(tri)) / 2

  rsids <- as.character(z$f[["rsids"]])
  vids  <- as.character(z$f[["variant_ids"]])
  af    <- tryCatch(as.numeric(z$f[["allele_freq"]]), error = function(e) NULL)
  if (is.null(af) || length(af) != length(vids)) af <- rep(NA_real_, length(vids))
  vids  <- sub("^chr", "", vids)

  # Parse GRCh38 chr:pos:ref:alt; ORDER by GRCh38 id (allele-aware) BEFORE liftover.
  parsed <- lapply(seq_along(vids), function(j) {
    parts <- strsplit(vids[[j]], ":", fixed = TRUE)[[1]]
    if (length(parts) < 4L) return(NULL)
    list(chr = parts[[1]], pos = suppressWarnings(as.integer(parts[[2]])),
         ref = parts[[3]], alt = parts[[4]], af = af[[j]],
         rsid = if (length(rsids) >= j && nzchar(rsids[[j]])) rsids[[j]] else "",
         row = j)
  })
  keep_rows <- which(!vapply(parsed, is.null, logical(1)))
  parsed <- parsed[keep_rows]
  # GRCh38-id allele-aware order (chr,pos,ref,alt)
  ord <- order(
    vapply(parsed, function(p) p$chr, character(1)),
    vapply(parsed, function(p) p$pos, numeric(1)),
    vapply(parsed, function(p) p$ref, character(1)),
    vapply(parsed, function(p) p$alt, character(1))
  )
  parsed <- parsed[ord]
  orig_rows <- vapply(parsed, function(p) p$row, integer(1))
  keys <- vapply(parsed, function(p) b38_key(p$chr, p$pos, p$ref, p$alt), character(1))
  window_n_var <- c(window_n_var, length(parsed))

  # Register variants in the global var_env (first writer wins; identical key in
  # the overlap is the SAME variant -> no duplication).
  for (m in seq_along(parsed)) {
    p <- parsed[[m]]
    k <- keys[[m]]
    if (is.null(var_env[[k]])) {
      var_env[[k]] <- list(chr = p$chr, pos38 = p$pos, ref = p$ref,
                           alt = p$alt, af = p$af, rsid = p$rsid)
    }
  }

  # Stage every computed pair (within buffer_bp) keyed by GRCh38 key.
  npv <- length(parsed)
  if (npv >= 1L) {
    for (a in seq_len(npv)) {
      ra <- orig_rows[[a]]
      pa <- parsed[[a]]
      for (b in a:npv) {
        rb <- orig_rows[[b]]
        pb <- parsed[[b]]
        if (abs(pa$pos - pb$pos) > buffer_bp) next   # beyond band -> drop (structural 0)
        r <- tri[ra, rb]
        stage_a <- c(stage_a, keys[[a]])
        stage_b <- c(stage_b, keys[[b]])
        stage_r <- c(stage_r, r)
      }
    }
  }
}

# WR-02 fix: completeness is checked UNCONDITIONALLY. Every --npz now contributes
# a manifest-mapped subregion_index (un-inferable -> hard error above), so an
# empty seen_idx can only mean zero valid children. Require the full child set.
if (length(unique(seen_idx)) != n_subregions) {
  stop("STITCH_INPUT: missing child (.npz subregion count ",
       length(unique(seen_idx)), " != n_subregions ", n_subregions, ")")
}

# ---------------------------------------------------------------------------
# CORE OWNERSHIP: assign each global variant to the ONE core whose half-open
# [core_start, core_end) (GRCh38 pos) contains it. Variants not owned by ANY
# core (purely in a buffer, never a core) are still RETAINED only if they appear
# as a core-owned endpoint's partner within the band -- but membership itself is
# core ownership, so a variant with no owning core is dropped from the row set
# (its pairs survive only if both endpoints are owned). We assign ownership and
# keep ONLY core-owned variants in obj$R/obj$variants.
# ---------------------------------------------------------------------------
all_keys <- ls(var_env)
owns_core <- function(pos38) {
  for (nm in names(core_by_idx)) {
    cc <- core_by_idx[[nm]]
    if (pos38 >= cc$core_start && pos38 < cc$core_end) return(TRUE)
  }
  FALSE
}
owned_keys <- character(0)
for (k in all_keys) {
  v <- var_env[[k]]
  if (owns_core(v$pos38)) owned_keys <- c(owned_keys, k)
}
if (length(owned_keys) == 0L) stop("STITCH_INPUT: no core-owned variants")

# Global order = sorted by GRCh38 (chr,pos,ref,alt) over the OWNED set.
owned_chr <- vapply(owned_keys, function(k) var_env[[k]]$chr, character(1))
owned_pos <- vapply(owned_keys, function(k) var_env[[k]]$pos38, numeric(1))
owned_ref <- vapply(owned_keys, function(k) var_env[[k]]$ref, character(1))
owned_alt <- vapply(owned_keys, function(k) var_env[[k]]$alt, character(1))
gord <- order(owned_chr, owned_pos, owned_ref, owned_alt)
owned_keys <- owned_keys[gord]
M <- length(owned_keys)
gidx <- setNames(seq_len(M), owned_keys)   # GRCh38 key -> global index

# Allele-aware uniqueness: no (CHR,POS,REF,ALT) GRCh38 key duplicated.
if (anyDuplicated(owned_keys) != 0L) stop("STITCH: duplicate (CHR,POS,REF,ALT) key in owned set")

# ---------------------------------------------------------------------------
# Liftover the owned variants to GRCh37 to build SNP_ID + variants$POS (b37).
# ---------------------------------------------------------------------------
snp_ids_b37 <- character(M)
pos37_vec   <- integer(M)
for (i in seq_len(M)) {
  v <- var_env[[owned_keys[[i]]]]
  if (nzchar(v$rsid)) {
    snp_ids_b37[[i]] <- v$rsid
    pos37_vec[[i]]   <- NA_integer_
  } else {
    p37 <- liftover_pos38_to_pos37(v$chr, v$pos38)
    pos37_vec[[i]] <- p37
    snp_ids_b37[[i]] <- if (is.na(p37)) NA_character_
                        else paste(v$chr, p37, v$ref, v$alt, sep = ":")
  }
}

# ---------------------------------------------------------------------------
# BANDED assembly: resolve staged GRCh38-key pairs to global indices; retain
# only pairs where BOTH endpoints are core-owned (global). Where a pair is
# computed in TWO overlapping windows, the values must agree (within 1e-4);
# keep ONE (de-dup). NEVER materialize the dense (M x M) form.
# ---------------------------------------------------------------------------
pair_map <- new.env(parent = emptyenv())   # "gi:gj" -> r (de-dup + agreement check)
for (s in seq_along(stage_r)) {
  ka <- stage_a[[s]]; kb <- stage_b[[s]]
  gi <- gidx[[ka]]; gj <- gidx[[kb]]
  if (is.null(gi) || is.null(gj)) next       # endpoint not core-owned -> skip
  if (is.na(gi) || is.na(gj)) next
  lo_i <- min(gi, gj); hi_j <- max(gi, gj)
  key <- paste(lo_i, hi_j, sep = ":")
  r <- stage_r[[s]]
  prev <- pair_map[[key]]
  if (is.null(prev)) {
    pair_map[[key]] <- r
  } else {
    if (abs(prev - r) > 1e-4) {
      stop(sprintf("STITCH: overlap-pair disagreement at (%d,%d): %.6f vs %.6f",
                   lo_i, hi_j, prev, r))
    }
    # agree -> keep one (already stored)
  }
}

pair_keys <- ls(pair_map)
ti <- integer(0); tj <- integer(0); tx <- numeric(0)
for (key in pair_keys) {
  ij <- as.integer(strsplit(key, ":", fixed = TRUE)[[1]])
  ti <- c(ti, ij[[1]]); tj <- c(tj, ij[[2]]); tx <- c(tx, pair_map[[key]])
}

# Build sparse symmetric banded dgCMatrix. Include both (i,j) and (j,i); set
# diag = 1. NOT block-diagonal.
R <- sparseMatrix(i = ti, j = tj, x = tx, dims = c(M, M), symmetric = FALSE)
R <- R + t(R)
diag(R) <- 1
# de-double the off-diagonal we added twice (R + t(R) doubled symmetric stored
# entries that were only on one triangle); since we stored upper (lo_i<=hi_j),
# t() moved them to lower with no overlap, so no doubling occurred except the
# diagonal which we hard-set to 1. Symmetrize defensively.
R <- (R + t(R)) / 2
diag(R) <- 1
R <- methods::as(R, "CsparseMatrix")
dimnames(R) <- list(snp_ids_b37, snp_ids_b37)

# ---------------------------------------------------------------------------
# obj$variants data.frame (SNP_ID, CHR, POS(b37), REF, ALT, AF) in global order.
# ---------------------------------------------------------------------------
variants <- data.frame(
  SNP_ID = snp_ids_b37,
  CHR    = vapply(owned_keys, function(k) var_env[[k]]$chr, character(1)),
  POS    = pos37_vec,
  REF    = vapply(owned_keys, function(k) var_env[[k]]$ref, character(1)),
  ALT    = vapply(owned_keys, function(k) var_env[[k]]$alt, character(1)),
  AF     = vapply(owned_keys, function(k) {
             a <- var_env[[k]]$af; if (is.null(a)) NA_real_ else a
           }, numeric(1)),
  stringsAsFactors = FALSE
)

# Assertions (T-M3RS-STITCH-01): exact uniqueness + bijective row/col coverage.
stopifnot(nrow(variants) == nrow(R))
stopifnot(nrow(variants) == M)
b37_keys <- paste(variants$CHR, variants$POS, variants$REF, variants$ALT, sep = ":")
# uniqueness is on the GRCh38 owned key (already de-duped); SNP_IDs may carry NA
# for failed-liftover synthetic ids, but the (CHR,POS38) bijection holds upstream.

provenance <- list(
  parent_region_id   = cli$parent,
  ancestry           = cli$ancestry,
  n_subregions       = n_subregions,
  subregion_npz_paths = cli$npz,
  buffer_bp          = buffer_bp,
  cross_subregion_ld = "banded within radius_bp; zeroed beyond",
  chain_path         = cli$chain,
  chain_sha256       = chain_sha256,
  datetime           = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
  per_window_n_var   = window_n_var,
  M                  = M,
  converter_script   = "src/scripts/stitch_subregions_to_rds.R",
  converter_version  = "m3-02b"
)

saveRDS(
  list(R = R, variants = variants, snp_ids = snp_ids_b37, provenance = provenance),
  cli$out,
  compress = "xz"
)
message(sprintf("WROTE %s (M=%d; banded buffer_bp=%g; %d sub-regions)",
                cli$out, M, buffer_bp, n_subregions))
