#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# src/scripts/ld_npz_to_rds.R -- M3 Wave 3 (.npz -> .rds) LD converter.
#
# Source: AOU-LD-PIPELINE.md §8.2 (verbatim recipe) PLUS three M3-specific
# augmentations:
#   (a) chr-prefix normalisation. Some AoU exports emit variant_ids as
#       "chr16:53809247:T:A"; some emit "16:53809247:T:A". This script
#       strips a leading "chr" from every non-rsid variant ID before the
#       liftover step so downstream R/Python consumers see one canonical
#       shape (DEC-2026-04-24-01 canonical analytic plane = GRCh37).
#   (b) GRCh38 -> GRCh37 variant-coordinate liftover via pyliftover
#       (UCSC chain at data/external/liftover/hg38ToHg19.over.chain.gz;
#       SHA-256 captured in the provenance JSON for reproducibility).
#       Per DEC-2026-04-24-01: AoU emits GRCh38; project canonical
#       analytic plane is GRCh37; the conversion step is the canonical
#       liftover boundary (no liftover at fine-mapping consumer side).
#   (c) Provenance manifest stored inside the .rds list (npz_path,
#       chain_path, chain_sha256, datetime, n_var_input, n_var_output,
#       n_var_dropped_liftover, genome_build) so every .rds can be
#       audited against the AoU export bundle that produced it.
#
# Usage:
#   Rscript src/scripts/ld_npz_to_rds.R <npz_path> <rds_path> <chain_path>
#
# .rds payload schema:
#   list(
#     ld         = <numeric matrix (n x n, symmetric, dimnames = b37 IDs)>,
#     snp_ids    = <character vector length n; b37 IDs>,
#     provenance = <named list, see header (c)>
#   )
#
# Wired into Snakemake at src/snakemake/rules/m3_convert_npz_rds.smk via
# `Rscript src/scripts/ld_npz_to_rds.R {input.npz} {output.rds} {input.chain}`.
# Conda env: envs/m3-r-ld.yml (r-base 4.4 + reticulate + Matrix + jsonlite +
# digest + numpy + pyliftover via pip).
#
# T-M3-S2-W3 mitigation: every .rds carries the chain SHA-256 + npz path so
# the manuscript supplementary materials can audit any region's LD provenance.
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(reticulate)
  library(Matrix)
  library(jsonlite)
  library(digest)
})

# ---------------------------------------------------------------------------
# m3-02b (HIGH#3) payload reconciliation:
#   The REAL downstream loader (src/legacy/region_analysis/scripts/run_susie_rss.R
#   ::load_ld_matrix) reads obj$R + obj$variants and does as.matrix(R). The old
#   list(ld, snp_ids, provenance) payload has obj$R == NULL and is REJECTED. We
#   now emit list(R=<Matrix>, variants=<data.frame CHR,POS,REF,ALT,SNP_ID,AF>,
#   snp_ids=<kept for back-compat>, provenance=...). Helper below parses a b37
#   SNP_ID (chr:pos:ref:alt OR rsid) into the variants data.frame columns.
# ---------------------------------------------------------------------------
parse_variants_frame <- function(snp_ids_b37, af = NULL) {
  n <- length(snp_ids_b37)
  chr <- rep(NA_character_, n); pos <- rep(NA_integer_, n)
  ref <- rep(NA_character_, n); alt <- rep(NA_character_, n)
  for (i in seq_len(n)) {
    sid <- snp_ids_b37[[i]]
    if (is.na(sid) || !nzchar(sid)) next
    if (grepl("^rs[0-9]+$", sid)) next  # rsid: CHR/POS stay NA (loader falls back to SNP_ID)
    parts <- strsplit(sid, ":", fixed = TRUE)[[1]]
    if (length(parts) >= 4L) {
      chr[[i]] <- parts[[1]]
      pos[[i]] <- suppressWarnings(as.integer(parts[[2]]))
      ref[[i]] <- parts[[3]]
      alt[[i]] <- parts[[4]]
    }
  }
  if (is.null(af)) af <- rep(NA_real_, n)
  data.frame(
    SNP_ID = as.character(snp_ids_b37),
    CHR = chr, POS = pos, REF = ref, ALT = alt, AF = as.numeric(af),
    stringsAsFactors = FALSE
  )
}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3L) {
  stop("usage: Rscript ld_npz_to_rds.R <npz_path> <rds_path> <chain_path>")
}
npz_path   <- args[[1]]
rds_path   <- args[[2]]
chain_path <- args[[3]]

if (!file.exists(npz_path)) stop("npz not found: ", npz_path)
if (!file.exists(chain_path)) stop("chain not found: ", chain_path)

chain_sha256 <- digest(file = chain_path, algo = "sha256")

# ---------------------------------------------------------------------------
# 1. Load .npz via numpy/reticulate (matches AOU-LD-PIPELINE.md §8.2)
# ---------------------------------------------------------------------------
np <- reticulate::import("numpy", convert = TRUE)
z  <- np$load(npz_path, allow_pickle = TRUE)
tri <- z$f[["ld"]]
if (!is.matrix(tri)) stop("unexpected ld shape in ", npz_path)

# ---------------------------------------------------------------------------
# 2. Symmetry recovery (lower-triangular -> full symmetric)
#
# WR-003 fix (2026-05-01): the AoU side casts to float32 in _save_npz +
# bm_to_npz, and `tri + t(tri) - diag(diag(tri))` over float32 introduces
# ~1e-6 ulp drift on the off-diagonal that depends on float ordering. This
# can leave isSymmetric(tri) FALSE for huge regions (HLA, 8p23) even after
# the recovery step. Force exact symmetry via the (M + t(M))/2 idempotent
# projection so the downstream Cholesky path in coloc/SuSiE never trips
# on near-symmetric numerical noise.
# ---------------------------------------------------------------------------
if (!isSymmetric(tri)) tri <- tri + t(tri) - diag(diag(tri))
tri <- (tri + t(tri)) / 2

# ---------------------------------------------------------------------------
# 3. Recover SNP IDs: prefer rsid; fall back to chr:pos:ref:alt synthetic IDs
# ---------------------------------------------------------------------------
rsids <- as.character(z$f[["rsids"]])
vids  <- as.character(z$f[["variant_ids"]])
snp_ids_grch38 <- ifelse(nzchar(rsids), rsids, vids)
n_input <- length(snp_ids_grch38)

# m3-02b: AF metadata (phase deliverable = LD + AF). Read the allele_freq array
# if present (row-aligned to variant_ids); else NA. Carried into obj$variants$AF.
allele_freq_in <- tryCatch(as.numeric(z$f[["allele_freq"]]), error = function(e) NULL)
if (is.null(allele_freq_in) || length(allele_freq_in) != n_input) {
  allele_freq_in <- rep(NA_real_, n_input)
}

# ---------------------------------------------------------------------------
# 4. Strip "chr" prefix on non-rsid synthetic IDs.  rsids never have a
#    "chr" prefix, so the regex anchored at start matches "chrN:..." only.
# ---------------------------------------------------------------------------
snp_ids_grch38 <- sub("^chr", "", snp_ids_grch38)

# ---------------------------------------------------------------------------
# 5. GRCh38 -> GRCh37 liftover via pyliftover (DEC-2026-04-24-01).
#    rsids are genome-build-agnostic; pass through untouched.
#    chr:pos:ref:alt synthetic IDs: parse, liftover pos, reform with b37 pos.
#    Failed liftovers are recorded as NA and dropped from the matrix below.
# ---------------------------------------------------------------------------
pyliftover <- reticulate::import("pyliftover", convert = TRUE)
lo <- pyliftover$LiftOver(chain_path)

liftover_one <- function(vid) {
  if (is.na(vid) || !nzchar(vid)) return(NA_character_)
  if (grepl("^rs[0-9]+$", vid)) return(vid)
  parts <- strsplit(vid, ":", fixed = TRUE)[[1]]
  if (length(parts) < 4L) return(NA_character_)
  chr <- parts[[1]]; pos38 <- suppressWarnings(as.integer(parts[[2]]))
  ref <- parts[[3]]; alt <- parts[[4]]
  if (is.na(pos38)) return(NA_character_)
  # pyliftover is 0-based; .convert_coordinate expects "chr<n>" plus 0-based pos.
  result <- lo$convert_coordinate(paste0("chr", chr), pos38 - 1L)
  if (is.null(result) || length(result) == 0L) return(NA_character_)
  pos37 <- as.integer(result[[1]][[2]]) + 1L
  paste(chr, pos37, ref, alt, sep = ":")
}
snp_ids_grch37 <- vapply(snp_ids_grch38, liftover_one, character(1L), USE.NAMES = FALSE)

drop_idx  <- is.na(snp_ids_grch37)
n_dropped <- sum(drop_idx)
if (n_dropped > 0L) {
  message(sprintf(
    "LIFTOVER_DROP %d / %d variants in %s",
    n_dropped, n_input, npz_path
  ))
  keep <- !drop_idx
  tri <- tri[keep, keep, drop = FALSE]
  snp_ids_grch37 <- snp_ids_grch37[keep]
  allele_freq_in <- allele_freq_in[keep]  # m3-02b: align AF to kept rows
}
n_output <- length(snp_ids_grch37)

# ---------------------------------------------------------------------------
# 6. Set dimnames (b37 IDs)
# ---------------------------------------------------------------------------
dimnames(tri) <- list(snp_ids_grch37, snp_ids_grch37)

# ---------------------------------------------------------------------------
# 7. Provenance manifest (T-M3-S2-W3 mitigation)
# ---------------------------------------------------------------------------
provenance <- list(
  npz_path               = npz_path,
  chain_path             = chain_path,
  chain_sha256           = chain_sha256,
  datetime               = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
  n_var_input            = n_input,
  n_var_output           = n_output,
  n_var_dropped_liftover = n_dropped,
  genome_build           = "GRCh37",
  source_genome_build    = "GRCh38",
  converter_script       = "src/scripts/ld_npz_to_rds.R",
  converter_version      = "m3-W3-T1"
)

# ---------------------------------------------------------------------------
# 8. Save  (m3-02b HIGH#3: reconcile payload to the REAL loader contract)
#
# run_susie_rss.R::load_ld_matrix() reads obj$R + obj$variants and does
# as.matrix(R). We emit:
#   R        = the symmetric LD as a sparse Matrix (dgCMatrix), dimnames = b37 IDs
#   variants = data.frame(SNP_ID, CHR, POS, REF, ALT, AF) in row order
#   snp_ids  = kept for back-compat (legacy consumers that read obj$snp_ids)
#   ld       = kept for back-compat (legacy consumers that read obj$ld)
# ---------------------------------------------------------------------------
R <- methods::as(tri, "CsparseMatrix")  # sparse dgCMatrix; loader densifies lazily
dimnames(R) <- list(snp_ids_grch37, snp_ids_grch37)
variants <- parse_variants_frame(snp_ids_grch37, af = allele_freq_in)

saveRDS(
  list(
    R          = R,
    variants   = variants,
    snp_ids    = snp_ids_grch37,  # back-compat
    ld         = tri,             # back-compat (legacy dense consumers)
    provenance = provenance
  ),
  rds_path,
  compress = "xz"
)
message(sprintf("WROTE %s (%d x %d; dropped %d of %d; R+variants payload)",
                rds_path, n_output, n_output, n_dropped, n_input))
