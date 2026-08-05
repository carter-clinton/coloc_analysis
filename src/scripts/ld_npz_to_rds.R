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
#   Rscript src/scripts/ld_npz_to_rds.R <npz_path> <rds_path> <chain_path> \
#           [max_n_var]
#
# .rds payload schema:
#   list(
#     R          = <symmetric sparse Matrix (dsCMatrix), dimnames = b37 IDs>,
#     variants   = <data.frame SNP_ID, CHR, POS, REF, ALT, AF; row order>,
#     snp_ids    = <character vector length n; b37 IDs>  (back-compat),
#     provenance = <named list, see header (c)>
#   )
#
# Wired into Snakemake at src/snakemake/rules/m3_convert_npz_rds.smk via
# `Rscript src/scripts/ld_npz_to_rds.R {input.npz} {output.rds} {input.chain}
#  {params.max_n_var}`.
# Conda env: envs/m3-r-ld.yml (r-base 4.4 + reticulate + Matrix + jsonlite +
# digest + numpy + pyliftover via pip).
#
# T-M3-S2-W3 mitigation: every .rds carries the chain SHA-256 + npz path so
# the manuscript supplementary materials can audit any region's LD provenance.
#
# ---------------------------------------------------------------------------
# 260805-23d Task 5 -- m3-04c blast radius, BLOCKER-D (Carter's decision,
# 2026-08-05). This file is one of the three FROZEN CONTRACTS; the decision
# unfreezes it FOR THIS TASK ONLY. src/python/plink_ld_to_npz.py and the m3-06
# LD-conditioning module stay FROZEN, and m3-06 stays HELD (this script neither
# imports it nor revives any NaN-to-zero mapping).
#
# WHAT WAS WRONG. The reader pulled the whole LD array across the reticulate
# boundary with convert = TRUE, i.e. an R n**2 DOUBLE, then built three more
# whole-matrix temporaries for the symmetry recovery, then PERSISTED the dense
# matrix into the artifact as a back-compat field -- all under a declared
# mem_mb of 8000. For the SMALLEST crosswalk target (SH2B3
# m2_region_00040__sub14, n_var 75,497) the R double alone is 45.6 GB.
#
# WHAT CHANGED.
#   1. The dense back-compat field is GONE from the payload. VERIFIED NO
#      PRODUCTION CONSUMER: run_susie_rss.R::load_ld_matrix reads obj$R,
#      obj$variants, obj$status, obj$use_identity; run_qtl_coloc.R:222 reads
#      ld_obj$R / ld_obj$use_identity. The only readers of the dense field
#      repo-wide were the two .rds reader helpers in
#      tests/m3/test_ld_npz_to_rds.py, rewritten in the same change to read
#      obj$R and to ASSERT the field is absent, so the removal is PINNED
#      rather than merely untested. (plink_ld_to_rds.R's opt$ld is an
#      unrelated CLI argument.)
#   2. The read is BLOCK-BOUNDED. The LD array stays a NumPy handle on the
#      Python side and is consumed as fixed square tiles, reusing the loop
#      shape of the frozen producer's _is_symmetric_blocked /
#      _strict_upper_is_zero_blocked (src/python/plink_ld_to_npz.py). Peak R
#      memory is O(nnz) + O(block**2), never O(n**2).
#   3. A FAIL-FAST n_var ceiling (argv[4], default 120000) aborts in seconds
#      instead of OOM-killing after hours.
#
# DISCLOSED RESIDUAL -- BLOCKER-D IS NOT FULLY CLOSED. The .npz's own `ld` key
# is a DENSE float32 array written by the FROZEN producer, so even a perfectly
# bounded reader must hold ONE dense float32 copy: 22.8 GB at n_var 75,497
# (SH2B3 __sub14), 67.3 GB at MC4R, ~553 GB at the FTO/HLA ~372k targets --
# just to READ. This work makes SH2B3's subregion feasible on a big-memory node
# and makes the large targets fail fast at the stated ceiling. It does NOT make
# them convertible; that needs a genuinely sparse .npz, which is a PRODUCER-side
# change on a frozen file and is out of scope here.
#
# BIT-EXACTNESS. The tiled arithmetic reproduces the old whole-matrix result
# exactly, not approximately: floating-point addition is commutative, x - 0 == x,
# (x + x) - x == x and (x + x) / 2 == x for every finite x, so the old
# "mirror then symmetrize" and "symmetrize only" paths collapse to the per-tile
# expressions below. Pinned by identical() -- not all.equal() -- on the whole
# payload in tests/m3/test_ld_npz_to_rds_bounded.py.
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
#
# argv[4] (optional) is the n_var ceiling. Snakemake supplies it from config
# `m3_convert_max_n_var`; an ad-hoc 3-argument invocation keeps the default so
# every pre-existing caller and test still works unchanged.
# ---------------------------------------------------------------------------
DEFAULT_MAX_N_VAR <- 120000L

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3L) {
  stop("usage: Rscript ld_npz_to_rds.R <npz_path> <rds_path> <chain_path> [max_n_var]")
}
npz_path   <- args[[1]]
rds_path   <- args[[2]]
chain_path <- args[[3]]

max_n_var <- DEFAULT_MAX_N_VAR
if (length(args) >= 4L && nzchar(args[[4]])) {
  parsed_max <- suppressWarnings(as.integer(args[[4]]))
  if (is.na(parsed_max) || parsed_max < 1L) {
    stop(sprintf("max_n_var must be a positive integer, got %s", args[[4]]))
  }
  max_n_var <- parsed_max
}

if (!file.exists(npz_path)) stop("npz not found: ", npz_path)
if (!file.exists(chain_path)) stop("chain not found: ", chain_path)

chain_sha256 <- digest(file = chain_path, algo = "sha256")

# Tile edge. 1024 matches the frozen producer's block-loop default. The env
# override exists so the multi-tile path can be exercised on a small fixture;
# production never sets it.
BLOCK <- suppressWarnings(as.integer(Sys.getenv("M3_LD_CONVERT_BLOCK", "1024")))
if (is.na(BLOCK) || BLOCK < 1L) BLOCK <- 1024L

# ---------------------------------------------------------------------------
# 1. Python-side .npz accessors.
#
# Everything that touches the LD array lives here so the array is never
# converted to an R n**2 double. The R side only ever sees tiles.
# ---------------------------------------------------------------------------
NPZ_ACCESSORS <- r"---(
import numpy as np

_M3_NPZ = {}


def m3_npz_open(path):
    """Open the .npz ONCE and report its keys.

    NpzFile.__getitem__ DECOMPRESSES on every access, so each key is fetched at
    most once and the LD array is cached (m3_npz_bind_ld) rather than re-read
    per tile.
    """
    _M3_NPZ.clear()
    _M3_NPZ["z"] = np.load(path, allow_pickle=True)
    return sorted(str(k) for k in _M3_NPZ["z"].files)


def m3_npz_small(key):
    """A SMALL 1-D key (rsids / variant_ids / allele_freq / lower_triangular),
    or None when absent. Never call this for the LD array."""
    z = _M3_NPZ["z"]
    if key not in z.files:
        return None
    return z[key]


def m3_npz_bind_ld(key="ld"):
    """Materialise the dense LD array in PYTHON and keep the handle there.

    DISCLOSED RESIDUAL: the key is a DENSE float32 written by the FROZEN
    producer (src/python/plink_ld_to_npz.py), so exactly one dense float32 copy
    is unavoidable on the read side. What is removed is every DERIVED
    whole-matrix copy.
    """
    arr = _M3_NPZ["z"][key]
    _M3_NPZ["ld"] = arr
    return [int(v) for v in arr.shape]


def m3_npz_tile(i0, i1, j0, j1):
    """(ld[i0:i1, j0:j1], ld[j0:j1, i0:i1]) as float64, or None when BOTH tiles
    are entirely zero and can therefore contribute nothing.

    Block-loop shape borrowed from the frozen producer's _is_symmetric_blocked /
    _strict_upper_is_zero_blocked: a fixed square tile, so the transient is
    bounded by block**2 and never by n_var**2. NaN is NEVER treated as zero
    (`nan != 0` is True), so a tile carrying NaN is always returned -- m3-06
    stays HELD and no NaN is silently mapped to 0.
    """
    arr = _M3_NPZ["ld"]
    a = arr[i0:i1, j0:j1]
    b = arr[j0:j1, i0:i1]
    if not bool((a != 0).any()) and not bool((b != 0).any()):
        return None
    return (np.array(a, dtype=np.float64), np.array(b, dtype=np.float64))
)---"

reticulate::py_run_string(NPZ_ACCESSORS)
npz_py <- reticulate::py

npz_keys <- as.character(npz_py$m3_npz_open(npz_path))
for (required in c("ld", "variant_ids", "rsids")) {
  if (!(required %in% npz_keys)) {
    stop(sprintf("npz %s has no '%s' key (keys: %s)",
                 npz_path, required, paste(npz_keys, collapse = ",")))
  }
}

# ---------------------------------------------------------------------------
# 2. Recover SNP IDs: prefer rsid; fall back to chr:pos:ref:alt synthetic IDs.
#    Read BEFORE the LD array so the n_var ceiling below can abort at ~zero cost.
# ---------------------------------------------------------------------------
rsids <- as.character(npz_py$m3_npz_small("rsids"))
vids  <- as.character(npz_py$m3_npz_small("variant_ids"))
snp_ids_grch38 <- ifelse(nzchar(rsids), rsids, vids)
n_input <- length(snp_ids_grch38)

# m3-02b: AF metadata (phase deliverable = LD + AF). Read the allele_freq array
# if present (row-aligned to variant_ids); else NA. Carried into obj$variants$AF.
allele_freq_in <- tryCatch(as.numeric(npz_py$m3_npz_small("allele_freq")),
                           error = function(e) NULL)
if (is.null(allele_freq_in) || length(allele_freq_in) != n_input) {
  allele_freq_in <- rep(NA_real_, n_input)
}

# ---------------------------------------------------------------------------
# 3. FAIL-FAST n_var ceiling (blast-radius BLOCKER-D).
#
#    The producer writes a DENSE n_var**2 float32, so the READ alone costs
#    4 * n_var**2 bytes before any conversion work happens. Refusing at a stated
#    ceiling costs seconds; discovering the same limit by OOM-kill costs hours of
#    a node and leaves a half-written artifact. Raise config m3_convert_max_n_var
#    and m3_convert_mem_mb TOGETHER, on a node that actually has the memory.
# ---------------------------------------------------------------------------
region_label <- sub("\\.npz$", "", basename(npz_path))
if (n_input > max_n_var) {
  stop(sprintf(paste0(
    "LD_CONVERT_N_VAR_CEILING: region=%s npz=%s n_var=%d exceeds max_n_var=%d. ",
    "The .npz 'ld' key is a DENSE float32 array written by the FROZEN producer ",
    "src/python/plink_ld_to_npz.py, so simply READING it costs %.1f GB (a dense ",
    "float64 would be %.1f GB) before any conversion work. This reader is ",
    "block-bounded and holds no derived whole-matrix copy, but it cannot make ",
    "that producer-side copy go away. Remedy: raise config m3_convert_max_n_var ",
    "AND m3_convert_mem_mb together on a big-memory node, or emit a sparse .npz ",
    "producer-side (OUT OF SCOPE here: plink_ld_to_npz.py is a frozen contract)."),
    region_label, npz_path, n_input, max_n_var,
    (as.numeric(n_input)^2 * 4) / 1e9, (as.numeric(n_input)^2 * 8) / 1e9),
    call. = FALSE)
}

# ---------------------------------------------------------------------------
# 4. Bind the LD array on the Python side and validate its shape.
# ---------------------------------------------------------------------------
ld_shape <- as.integer(unlist(npz_py$m3_npz_bind_ld("ld")))
if (length(ld_shape) != 2L || ld_shape[[1]] != ld_shape[[2]]) {
  stop("unexpected ld shape in ", npz_path)
}
n_var <- ld_shape[[1]]
if (n_var != n_input) {
  stop(sprintf("ld is %d x %d but %s carries %d variant ids",
               n_var, n_var, npz_path, n_input))
}

# ---------------------------------------------------------------------------
# 5. Symmetry recovery -- HONOR the lower_triangular flag the .npz carries.
#
# CR-01 fix (2026-06-19): the one-sided recovery (mirror the populated triangle)
# is ONLY valid when the stored array is one-sided -- the Path A.2 case
# (_save_npz lower_triangular=True). For a FULL (Path A.1) matrix it DOUBLES
# every off-diagonal (r -> 2r), and the subsequent averaging does NOT undo it.
# The OLD gate `if (!isSymmetric(...))` was the trap: a full float32 LD matrix
# carries ~1e-7 triangle asymmetry from Hail block-sum order -- ~7 orders of
# magnitude above isSymmetric's ~2.2e-14 tol -- so the gate fired and silently
# doubled the off-diagonals (corrupting the LD panel fed to SuSiE-RSS).
#
# WR-003 (float32) rationale, corrected: the float32 drift is real for both
# paths. The .npz already records which triangle convention it used in the
# `lower_triangular` flag (aou_ld_panel.py _save_npz). We read it and, per tile:
#   * lower_triangular == TRUE  -> one-sided input. value(i,j) = A(i,j) + A(j,i),
#     minus the diagonal term on i == j. Mirroring the populated triangle and
#     then averaging is exactly this: the mirrored matrix is bit-symmetric, and
#     (x + x) / 2 == x for every finite x.
#   * lower_triangular == FALSE / absent -> FULL input, already two-sided, so
#     ONLY project out float asymmetry: value(i,j) = (A(i,j) + A(j,i)) / 2
#     (avg(r,r) = r, never doubles). This is also a no-op for the already-
#     mirrored lower-tri case.
# The idempotent averaging projection is ALWAYS applied so the downstream
# Cholesky path in coloc/SuSiE never trips on near-symmetric numerical noise.
# ---------------------------------------------------------------------------
lower_only <- tryCatch(as.logical(npz_py$m3_npz_small("lower_triangular"))[1],
                       error = function(e) FALSE)
if (length(lower_only) != 1L || is.na(lower_only)) lower_only <- FALSE

# ---------------------------------------------------------------------------
# 6. Strip "chr" prefix on non-rsid synthetic IDs.  rsids never have a
#    "chr" prefix, so the regex anchored at start matches "chrN:..." only.
# ---------------------------------------------------------------------------
snp_ids_grch38 <- sub("^chr", "", snp_ids_grch38)

# ---------------------------------------------------------------------------
# 7. GRCh38 -> GRCh37 liftover via pyliftover (DEC-2026-04-24-01).
#    rsids are genome-build-agnostic; pass through untouched.
#    chr:pos:ref:alt synthetic IDs: parse, liftover pos, reform with b37 pos.
#    Failed liftovers are recorded as NA and dropped from the matrix below.
#
#    Runs BEFORE the tile loop so a dropped variant's entries are never
#    accumulated at all, rather than accumulated and then subset away.
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
  snp_ids_grch37 <- snp_ids_grch37[!drop_idx]
  allele_freq_in <- allele_freq_in[!drop_idx]  # m3-02b: align AF to kept rows
}
n_output <- length(snp_ids_grch37)

# ---------------------------------------------------------------------------
# 8. Block-bounded assembly of the symmetric sparse LD matrix.
#
# Iterate the UPPER block triangle (bj >= bi) and emit only entries with global
# row <= global column: as(<dense symmetric>, "CsparseMatrix") yields a dsCMatrix
# with uplo "U", which stores exactly that triangle, so emitting it directly is
# both the memory-lean choice AND the one that reproduces the old object
# bit-for-bit. Dropped (unliftable) variants are filtered per tile and the
# surviving indices remapped on the fly, so no dense subset is ever formed.
#
# Peak R memory: O(nnz stored) + O(BLOCK**2), never O(n_var**2).
# ---------------------------------------------------------------------------
kept_index <- cumsum(!drop_idx)   # position of each variant in the kept space
keep_mask  <- !drop_idx

acc_i <- list(); acc_j <- list(); acc_x <- list(); n_acc <- 0L
starts <- if (n_var > 0L) seq.int(1L, n_var, by = BLOCK) else integer(0)

for (bi in seq_along(starts)) {
  i0 <- starts[[bi]]; i1 <- min(i0 + BLOCK - 1L, n_var)
  rows_keep <- keep_mask[i0:i1]
  if (!any(rows_keep)) next
  for (bj in seq.int(bi, length(starts))) {
    j0 <- starts[[bj]]; j1 <- min(j0 + BLOCK - 1L, n_var)
    cols_keep <- keep_mask[j0:j1]
    if (!any(cols_keep)) next

    tiles <- npz_py$m3_npz_tile(i0 - 1L, i1, j0 - 1L, j1)
    if (is.null(tiles)) next          # both tiles all-zero: contributes nothing

    v <- tiles[[1]] + t(tiles[[2]])
    if (bi == bj && isTRUE(lower_only)) {
      # The global diagonal lies inside this block; a(i,i) + a(i,i) - a(i,i).
      d <- seq_len(nrow(v))
      v[cbind(d, d)] <- v[cbind(d, d)] - diag(tiles[[1]])
    }
    if (!isTRUE(lower_only)) v <- v / 2

    sel <- (is.na(v) | v != 0) & outer(rows_keep, cols_keep, "&")
    if (bi == bj) sel <- sel & upper.tri(v, diag = TRUE)
    nz <- which(sel)
    if (!length(nz)) next

    nr <- nrow(v)
    rr <- ((nz - 1L) %% nr) + 1L
    cc <- ((nz - 1L) %/% nr) + 1L
    n_acc <- n_acc + 1L
    acc_i[[n_acc]] <- kept_index[i0 + rr - 1L]
    acc_j[[n_acc]] <- kept_index[j0 + cc - 1L]
    acc_x[[n_acc]] <- v[nz]
  }
}

# Unlist one accumulator at a time and release each immediately: the transient
# doubling then applies to ONE vector rather than all three at once.
i_all <- unlist(acc_i, use.names = FALSE); acc_i <- NULL; invisible(gc(FALSE))
j_all <- unlist(acc_j, use.names = FALSE); acc_j <- NULL; invisible(gc(FALSE))
x_all <- unlist(acc_x, use.names = FALSE); acc_x <- NULL; invisible(gc(FALSE))
if (is.null(i_all)) { i_all <- integer(0); j_all <- integer(0); x_all <- numeric(0) }
nnz_stored <- length(x_all)

R <- Matrix::sparseMatrix(
  i = i_all, j = j_all, x = x_all,
  dims = c(n_output, n_output),
  dimnames = list(snp_ids_grch37, snp_ids_grch37),
  symmetric = TRUE
)
# sparseMatrix() infers uplo from the supplied triangle; with NO stored entries
# (an all-zero panel, or zero surviving variants) it cannot, and defaults to "L"
# where the dense coercion yields "U". Pin it so the degenerate case is identical
# too. Unconditionally safe: the triplets above are ALWAYS the upper triangle.
R@uplo <- "U"
rm(i_all, j_all, x_all); invisible(gc(FALSE))

variants <- parse_variants_frame(snp_ids_grch37, af = allele_freq_in)

# ---------------------------------------------------------------------------
# 9. Provenance manifest (T-M3-S2-W3 mitigation)
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
# 10. Save  (m3-02b HIGH#3: reconcile payload to the REAL loader contract)
#
# run_susie_rss.R::load_ld_matrix() reads obj$R + obj$variants and does
# as.matrix(R). We emit:
#   R        = the symmetric LD as a sparse Matrix (dsCMatrix), dimnames = b37 IDs
#   variants = data.frame(SNP_ID, CHR, POS, REF, ALT, AF) in row order
#   snp_ids  = kept for back-compat (legacy consumers that read obj$snp_ids)
#
# The dense back-compat field is deliberately absent -- see the BLOCKER-D block
# in the header. It had no production consumer and it was the reason block-wise
# processing alone could never have bounded this script.
# ---------------------------------------------------------------------------
saveRDS(
  list(
    R          = R,
    variants   = variants,
    snp_ids    = snp_ids_grch37,  # back-compat
    provenance = provenance
  ),
  rds_path,
  compress = "xz"
)

gc_tab <- gc(verbose = FALSE)
r_peak_mb <- suppressWarnings(sum(as.numeric(gc_tab[, ncol(gc_tab)])))
message(sprintf("WROTE %s (%d x %d; dropped %d of %d; R+variants payload)",
                rds_path, n_output, n_output, n_dropped, n_input))
message(sprintf(
  "R_HEAP_PEAK_MB %.1f (block=%d n_var=%d n_kept=%d nnz_stored=%d lower_triangular=%s)",
  r_peak_mb, BLOCK, n_var, n_output, nnz_stored, isTRUE(lower_only)))
