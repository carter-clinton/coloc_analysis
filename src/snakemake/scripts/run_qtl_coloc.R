#!/usr/bin/env Rscript
# ==========================================================================
# Phase 2 -- unified GWAS-vs-QTL coloc.susie runner.
#
# Accepts a pre-fitted GWAS .fit.rds (from Phase 1 run_susie_rss.R) on the
# GWAS side, and a harmonized QTL sumstats TSV on the QTL side. Fits
# SuSiE-RSS on the QTL data and calls coloc.susie(gwas_fit, qtl_fit).
#
# All QTL sources (eQTL, sQTL, pQTL, sc-eQTL) produce the same harmonized
# TSV intermediate format, so this script is source-agnostic.
#
# T-02-07 mitigation: check_dataset() validates QTL data before SuSiE;
#   skip if n_snps_overlap < 50.
# ==========================================================================

suppressPackageStartupMessages({
  library(optparse)
  library(coloc)
  library(susieR)
  library(jsonlite)
  library(data.table)
})

`%||%` <- function(x, y) if (!is.null(x)) x else y

# -------------------------------------------------------------------------
# CLI argument parsing
# -------------------------------------------------------------------------
option_list <- list(
  make_option("--gwas-fit",      dest = "gwas_fit",      type = "character",
              help = "Path to Phase 1 .fit.rds (SuSiE object with class 'susie')"),
  make_option("--qtl-sumstats",  dest = "qtl_sumstats",  type = "character",
              help = "Path to harmonized QTL TSV (output of harmonize_*.py)"),
  make_option("--ld-matrix",     dest = "ld_matrix",     type = "character",
              help = "Path to LD .rds matrix (from Phase 1 ld_reference pipeline)"),
  make_option("--qtl-source",    dest = "qtl_source",    type = "character",
              help = "Source identifier: gtex_eqtl, gtex_sqtl, ukbppp_pqtl, onek1k_sceqtl"),
  make_option("--tissue",        type = "character",
              help = "Tissue or cell type name"),
  make_option("--gene-id",       dest = "gene_id",       type = "character",
              help = "Ensembl gene ID"),
  make_option("--region",        type = "character",
              help = "Region ID from regions_curated"),
  make_option("--ancestry",      type = "character",
              help = "Ancestry code (EUR, AFR, etc.)"),
  make_option("--sdy",           type = "double",   default = 1.0,
              help = "Numeric sdY value for QTL data (1.0 for GTEx/OneK1K; estimated for pQTL)"),
  make_option("--sample-size",   dest = "sample_size",   type = "integer",
              help = "Integer N for QTL dataset"),
  make_option("--policy",        type = "character", default = "config/susie_policy.yaml",
              help = "Path to config/susie_policy.yaml"),
  # ------------------------------------------------------------------
  # 260805-w7u -- m3-04c blast-radius FINDING E, gate row
  # "Any GWAS x QTL colocalization". BOTH default to the LEGACY behaviour so
  # that a caller which never passes them is INERT. That is not hypothetical:
  # src/python/sample_null_loci.py:369-384 is a SECOND caller of this script and
  # will never pass either flag (its rows are ancestry="EUR" with
  # ld_matrix_path: ""). It is the live proof that the default direction is the
  # right one, and tests/m3/test_qtl_coloc_allele_join.py asserts it against
  # that exact argv.
  # ------------------------------------------------------------------
  make_option("--ld-allele-join", dest = "ld_allele_join", type = "character",
              default = "false",
              help = paste("'true' or 'false'. When true, bridge the LD panel to",
                           "the GWAS fit through the region variant catalog with",
                           "the allele-aware 4-key join, and FAIL NON-ZERO when",
                           "that bridge cannot be built. Any other value is a",
                           "hard error -- never a silent default.")),
  make_option("--variant-list",  dest = "variant_list",   type = "character",
              default = NULL,
              help = paste("Region variant catalog TSV (CHR/POS/REF/ALT/SNP_ID),",
                           "i.e. {ld_reference}/variants/{region}.tsv -- the same",
                           "artifact run_finemap.input.variants consumes. Required",
                           "when --ld-allele-join is true.")),
  make_option("--output",        type = "character",
              help = "Output JSON path")
)
opt <- parse_args(OptionParser(option_list = option_list))

# Validate required arguments
required_args <- c("gwas_fit", "qtl_sumstats", "ld_matrix", "output")
for (arg_name in required_args) {
  if (is.null(opt[[arg_name]])) {
    stop(paste0("--", gsub("_", "-", arg_name), " is required"), call. = FALSE)
  }
}

# Validate file existence
stopifnot(file.exists(opt$gwas_fit))
stopifnot(file.exists(opt$qtl_sumstats))
stopifnot(file.exists(opt$ld_matrix))

# =========================================================================
# 260805-w7u -- FINDING E. THE GATE, THE SHARED JOIN, AND THE LOUD FAILURE.
# =========================================================================
# ⚠ WHY THIS EXISTS AT ALL, stated once, plainly.
#
# At 7b1025d qtl_coloc.smk built the legacy {ld_reference}/{ancestry}/{region}.rds
# and handed THAT to coloc::runsusie while the GWAS fit it colocalizes had been
# produced on the AoU panel -- two different LD panels inside one coloc.susie
# posterior. Task 1 of 260805-w7u routes the PATH through resolve_ld_path.
# Fixing only the path substitutes a DIFFERENT silent failure, because the AoU
# panel's key space is not the fit's:
#
#   * ld_npz_to_rds.R:440 writes R as a dsCMatrix WITH dimnames = the GRCh37
#     chr:pos:ref:alt ids. `ld_snp_names <- rownames(ld_full) %||% ...` (below)
#     short-circuits on the FIRST non-NULL, so those panel-space ids ARE
#     ld_snp_names and build_ld_rownames() never runs. (The legacy 1kG .rds is
#     the opposite shape -- plink_ld_to_rds.R:88 sets dimnames(R) <- NULL and its
#     R is a base matrix from as.matrix(ld_dt) -- which is exactly why EUR coloc
#     works today, and why nothing below may touch the ungated path.)
#   * GWAS fit names are SUMSTATS-space: either an rsid or "chr:pos". Neither can
#     ever equal "chr:pos:ref:alt", so the LD intersection would be EMPTY.
#   * An empty intersection at 7b1025d wrote too_few_snps and EXITED 0. So did a
#     sparse dsCMatrix rejected by runsusie inside a tryCatch, and so did an
#     un-intersected use_identity fit on diag(n). In bulk, "no colocalization
#     found" at rc 0 reads as a scientific result.
#
# THE BRIDGE. {ld_reference}/variants/{region}.tsv -- CHR/POS/REF/ALT/SNP_ID,
# GRCh37, already run_finemap.input.variants. Panel = ld_obj$variants,
# catalog = subset_dt: the shared matcher's contract IS satisfiable here.
#
# EVERYTHING BELOW IS BEHIND ONE FLAG. With --ld-allele-join false (the default,
# and what every ancestry off the allow-list renders) this file behaves exactly
# as it did at 7b1025d, byte for byte, for every input.
# =========================================================================
LD_ALLELE_JOIN_FLAG <- opt$ld_allele_join %||% "false"
if (!identical(LD_ALLELE_JOIN_FLAG, "true") &&
    !identical(LD_ALLELE_JOIN_FLAG, "false")) {
  # Never silently default: this flag decides which LD ROW a variant binds to.
  stop(sprintf("--ld-allele-join must be exactly 'true' or 'false', got '%s'",
               LD_ALLELE_JOIN_FLAG), call. = FALSE)
}
LD_ALLELE_JOIN <- identical(LD_ALLELE_JOIN_FLAG, "true")

# The realized-overlap floor. Deliberately the SAME literal 50 the two
# pre-existing gates use (:183 and the post-LD-intersection gate below), so this
# change invents no new fatal threshold -- it only changes whether falling below
# the existing one is LOUD. config/susie_policy.yaml `susie.min_ld_overlap` is 50
# and tests/m3/test_qtl_coloc_allele_join.py reads the policy and pins that the
# two agree, so a policy edit that diverges from this constant is a test failure
# rather than a silent drift.
MIN_COLOC_LD_OVERLAP <- 50L

.script_dir <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f) > 0) return(dirname(normalizePath(f[1], mustWork = FALSE)))
  of <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  if (!is.null(of)) return(dirname(normalizePath(of, mustWork = FALSE)))
  "src/snakemake/scripts"
}
LD_ALLELE_JOIN_R <- file.path(.script_dir(), "ld_allele_join.R")
if (LD_ALLELE_JOIN) {
  # Sourced ONLY under the gate: a missing file must not be able to change the
  # return code of the ungated path, which is what keeps EUR byte-identical even
  # in a partial checkout.
  if (!file.exists(LD_ALLELE_JOIN_R)) {
    stop(sprintf(paste("[run_qtl_coloc] LD_JOIN_FATAL reason=join_source_missing",
                       "region=%s ancestry=%s expected=%s"),
                 opt$region %||% "?", opt$ancestry %||% "?", LD_ALLELE_JOIN_R),
         call. = FALSE)
  }
  source(LD_ALLELE_JOIN_R)
}

# ---- provenance, filled in as it is MEASURED; NULL means "not measured" ----
# NULL (not 0, not "") is the discipline inherited from 260805-o7o: a counter
# that is 0 says "measured and clean", a counter that is absent says "never ran".
# Conflating them is how a disarmed gate comes to look like a clean result.
LD_KEY_SPACE <- NULL
LD_PANEL_OVERLAP <- NULL
LD_CANDIDATE_OVERLAPS <- NULL
LD_JOIN_COUNTS <- NULL

ld_provenance <- function() {
  # ⚠ RETURNS AN EMPTY LIST OFF THE GATE, AND THAT IS LOAD-BEARING. In R
  # `list(k = NULL)` CREATES a named NULL element (unlike `x$k <- NULL`, which
  # deletes), so building this unconditionally would make the ungated result
  # STRUCTURALLY different from 7b1025d's and break the byte-identical EUR
  # proof. This exact trap cost 260805-o7o a rewrite; NC-2e re-observes it.
  if (!LD_ALLELE_JOIN) return(list())
  cnt <- LD_JOIN_COUNTS
  g <- function(nm) if (is.null(cnt)) NA_integer_ else as.integer(cnt[[nm]])
  list(
    ld_matrix                     = opt$ld_matrix %||% NA_character_,
    ld_allele_join                = LD_ALLELE_JOIN_FLAG,
    ld_key_space                  = LD_KEY_SPACE %||% NA_character_,
    ld_panel_overlap              = if (is.null(LD_PANEL_OVERLAP)) NA_integer_
                                    else as.integer(LD_PANEL_OVERLAP),
    ld_allele_exact               = g("exact"),
    ld_allele_flipped             = g("flipped"),
    ld_allele_dropped_palindromic = g("dropped_palindromic"),
    ld_allele_dropped_mismatch    = g("dropped_mismatch"),
    ld_allele_dropped_ambiguous   = g("dropped_ambiguous"),
    ld_allele_dropped_unusable    = g("dropped_unusable")
  )
}

attach_ld_provenance <- function(result) {
  extra <- ld_provenance()
  for (nm in names(extra)) result[[nm]] <- extra[[nm]]
  result
}

ld_join_stop <- function(reason, detail = "") {
  # ONE structured, non-zero exit. Names the reason, the region, the ancestry,
  # the realized overlap, the threshold, and EVERY measured candidate key-space
  # overlap -- because "0 overlap" without knowing which key spaces were tried is
  # the same non-diagnosis the four exit-0 layers already produce.
  cand <- if (is.null(LD_CANDIDATE_OVERLAPS)) "not measured" else
    paste(sprintf("%s=%d", names(LD_CANDIDATE_OVERLAPS),
                  as.integer(LD_CANDIDATE_OVERLAPS)), collapse = ", ")
  stop(sprintf(paste0(
    "[run_qtl_coloc] LD_JOIN_FATAL reason=%s region=%s ancestry=%s ",
    "ld_matrix=%s realized_overlap=%s threshold=%d candidate_overlaps=[%s] %s"),
    reason, opt$region %||% "?", opt$ancestry %||% "?",
    opt$ld_matrix %||% "?",
    if (is.null(LD_PANEL_OVERLAP)) "NA" else as.character(LD_PANEL_OVERLAP),
    MIN_COLOC_LD_OVERLAP, cand, detail), call. = FALSE)
}

# -------------------------------------------------------------------------
# Helper: write status JSON and exit cleanly
# -------------------------------------------------------------------------
write_status_json <- function(status_code, message = NULL) {
  result <- list(
    status        = status_code,
    message       = message %||% status_code,
    qtl_source    = opt$qtl_source %||% NA_character_,
    tissue        = opt$tissue %||% NA_character_,
    gene_id       = opt$gene_id %||% NA_character_,
    region        = opt$region %||% NA_character_,
    ancestry      = opt$ancestry %||% NA_character_,
    n_snps_overlap = 0L,
    qtl_n         = opt$sample_size %||% NA_integer_,
    qtl_sdy       = opt$sdy %||% NA_real_,
    summary       = list(),
    all_pairs     = list(),
    n_cs_gwas     = NA_integer_,
    n_cs_qtl      = NA_integer_
  )
  result <- attach_ld_provenance(result)
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(result, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
  cat(sprintf("[run_qtl_coloc] %s for %s/%s/%s -- wrote %s\n",
              status_code, opt$gene_id %||% "?", opt$tissue %||% "?",
              opt$region %||% "?", opt$output))
}

# -------------------------------------------------------------------------
# 1. Load GWAS fit
# -------------------------------------------------------------------------
gwas_fit <- readRDS(opt$gwas_fit)
if (!inherits(gwas_fit, "susie")) {
  class(gwas_fit) <- c("susie", class(gwas_fit))
}

# -------------------------------------------------------------------------
# 2. Read QTL sumstats
# -------------------------------------------------------------------------
qtl_df <- fread(opt$qtl_sumstats)
if (nrow(qtl_df) == 0) {
  write_status_json("too_few_snps", "QTL sumstats file is empty")
  quit(status = 0)
}

# Ensure numeric types
qtl_df[, beta := as.numeric(beta)]
qtl_df[, se   := as.numeric(se)]
qtl_df[, maf  := as.numeric(maf)]
qtl_df[, position := as.integer(position)]

# -------------------------------------------------------------------------
# 3. Match SNPs between GWAS fit and QTL data
# -------------------------------------------------------------------------
# qtl_coloc_snp_name_mismatch bugfix (2026-04-20):
# GWAS SuSiE fits from run_susie_rss.R carry rsid names (sourced from
# sumstats SNP_ID column) on $alpha colnames and $pip names, because Phase 1
# sumstats are GRCh37 but harmonized QTL TSVs are GRCh38. Direct coord
# matching would fail across builds. The harmonized TSV carries a parallel
# `rsid` column populated for >99% of variants, so rsid is the build-
# invariant common key between Phase 1 fit and Phase 2 QTL data.
gwas_snps <- NULL
if (!is.null(gwas_fit$alpha) && !is.null(colnames(gwas_fit$alpha))) {
  gwas_snps <- colnames(gwas_fit$alpha)
} else if (!is.null(names(gwas_fit$pip))) {
  gwas_snps <- names(gwas_fit$pip)
}

if (is.null(gwas_snps)) {
  write_status_json("too_few_snps", "Cannot extract SNP names from GWAS fit")
  quit(status = 0)
}

# Drop the sentinel "null" column (coloc::annotate_susie appends one when the
# fit has fewer credible sets than L; it is not a real variant).
gwas_snps <- gwas_snps[gwas_snps != "null"]

# Match by best-overlap key across rsid / chr:pos / variant_id. Phase 1
# SuSiE fits can carry either rsids (bmi.*, asthma.* sumstats) or chr:pos
# strings (hypertension.*, stroke.*, t2d.* sumstats) on colnames(fit$alpha),
# depending on the SNP_ID convention of each harmonized sumstats file. The
# QTL harmonized TSV carries `rsid` and `variant_id` (chr_pos_ref_alt).
# Derive chr:pos from variant_id so we can match chr:pos-formatted fits that
# would otherwise silently 0-overlap against rsid-only QTL keys (root cause
# of the all-zero-overlap SH2B3_12q24 QTL coloc runs surfaced 2026-04-21
# during Stage 3 Option C; same class as the trait-pair bug fixed in 335f514).
# variant_id format: "chr12_110962202_G_A" -> chrpos "12:110962202"
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
cat(sprintf("[run_qtl_coloc] candidate overlaps: %s\n",
            paste(sprintf("%s=%d", names(overlaps), overlaps), collapse = ", ")))
match_key      <- names(which.max(overlaps))
qtl_snps       <- candidates[[match_key]]
overlap_snps   <- intersect(gwas_snps, qtl_snps)
n_snps_overlap <- length(overlap_snps)

cat(sprintf("[run_qtl_coloc] match_key=%s, GWAS snps: %d, QTL snps: %d, overlap: %d\n",
            match_key, length(gwas_snps), length(qtl_snps), n_snps_overlap))

# T-02-07: skip if too few overlapping SNPs
if (n_snps_overlap < 50) {
  write_status_json("too_few_snps",
                    sprintf("Only %d overlapping SNPs (need >= 50)", n_snps_overlap))
  quit(status = 0)
}

# -------------------------------------------------------------------------
# 4. Load LD matrix and subset to matching SNPs
# -------------------------------------------------------------------------
# qtl_coloc_snp_name_mismatch bugfix (2026-04-20):
# The LD .rds produced by the Phase 1 ld_reference pipeline is a LIST with
# components {R, variants, use_identity, status}. When the region's variant
# count exceeds LD_MAX_VARIANTS (default 6000), R is NULL and use_identity
# is TRUE. Previously this code assumed a bare matrix and would fail at
# rownames(ld_full) == NULL. Handle all three forms:
#   (a) list with R matrix and variants -> use obj$R with rsid rownames
#       (sourced from obj$variants$SNP_ID when available).
#   (b) list with use_identity=TRUE or R=NULL -> construct named identity
#       matrix over overlap_snps; coloc::runsusie will still run (LD is
#       the identity so SuSiE treats variants as independent).
#   (c) bare matrix (legacy / future) -> use directly, require dimnames.
ld_obj <- readRDS(opt$ld_matrix)

build_ld_rownames <- function(obj) {
  # Derive rsid-keyed names from the variants dataframe when available.
  if (!is.list(obj) || is.null(obj$variants) || !is.data.frame(obj$variants)) {
    return(NULL)
  }
  v <- obj$variants
  if ("SNP_ID" %in% names(v) && any(!is.na(v$SNP_ID) & v$SNP_ID != "" & v$SNP_ID != "NA")) {
    return(as.character(v$SNP_ID))
  }
  if (all(c("CHR", "POS") %in% names(v))) {
    return(sprintf("%s:%s", v$CHR, v$POS))
  }
  NULL
}

if (is.list(ld_obj) && !is.matrix(ld_obj)) {
  use_identity <- isTRUE(ld_obj$use_identity) || is.null(ld_obj$R)
  if (use_identity && LD_ALLELE_JOIN) {
    # THE use_identity BYPASS (m3-04c-BLAST-RADIUS:38). At 7b1025d this branch
    # built diag(n) over the FIT keys, never intersected the panel at all, and
    # ran coloc.susie on it with only a cat() -- the emitted JSON recorded
    # NOTHING about which LD was used. Under an armed gate that is not a
    # fallback, it is a silent substitution of "no LD" for "the LD we routed
    # this job through the resolver to obtain". Non-zero, named.
    ld_join_stop("use_identity_under_gate",
                 sprintf("panel status=%s; the .rds carries no usable R",
                         ld_obj$status %||% "unknown"))
  }
  if (use_identity) {
    # Identity fallback: build a named identity over overlap_snps.
    ld_matrix_subset <- diag(length(overlap_snps))
    dimnames(ld_matrix_subset) <- list(overlap_snps, overlap_snps)
    ld_snp_names <- overlap_snps  # trivially matches overlap
    cat(sprintf("[run_qtl_coloc] LD .rds has use_identity=TRUE (status=%s); using identity matrix\n",
                ld_obj$status %||% "unknown"))
  } else {
    ld_full <- ld_obj$R
    ld_snp_names <- rownames(ld_full) %||% colnames(ld_full) %||% build_ld_rownames(ld_obj)
    if (is.null(ld_snp_names)) {
      write_status_json("too_few_snps", "LD matrix has no row/col names and no variants metadata")
      quit(status = 0)
    }
    if (is.null(rownames(ld_full)) || is.null(colnames(ld_full))) {
      # Attach rsid dimnames from obj$variants (parallel-ordered).
      if (length(ld_snp_names) != nrow(ld_full)) {
        write_status_json("too_few_snps",
                          sprintf("LD rownames length %d != nrow %d",
                                  length(ld_snp_names), nrow(ld_full)))
        quit(status = 0)
      }
      dimnames(ld_full) <- list(ld_snp_names, ld_snp_names)
    }
  }
} else if (is.matrix(ld_obj) || inherits(ld_obj, "Matrix")) {
  # T-w7u-04. Under the gate the coercion is DEFERRED to the SUBSET: as.matrix()
  # on a full n_var x n_var panel is the BLOCKER-D dense-materialisation hazard
  # (n_var 75,497 at SH2B3 __sub14 -> ~45 GB;
  # [[feedback_dense_matrix_verify_memory_bounded]]). Off the gate the legacy
  # eager coercion is retained character-for-character.
  ld_full <- if (LD_ALLELE_JOIN) ld_obj else as.matrix(ld_obj)
  ld_snp_names <- rownames(ld_full) %||% colnames(ld_full)
  if (is.null(ld_snp_names)) {
    write_status_json("too_few_snps", "LD matrix has no row/col names")
    quit(status = 0)
  }
} else {
  write_status_json("too_few_snps",
                    sprintf("LD .rds has unexpected class: %s",
                            paste(class(ld_obj), collapse = "/")))
  quit(status = 0)
}

# -------------------------------------------------------------------------
# 4b. 260805-w7u -- THE PANEL <-> CATALOG <-> FIT BRIDGE (gated)
# -------------------------------------------------------------------------
# ld_row_index maps a FIT-SPACE name to an INTEGER panel row, so the subset can
# be taken by index on the sparse matrix and coerced afterwards.
ld_row_index <- NULL
if (LD_ALLELE_JOIN && (!exists("use_identity") || !isTRUE(use_identity))) {

  # ---- the catalog: the ONLY artifact that speaks both key spaces ----
  if (is.null(opt$variant_list) || !nzchar(opt$variant_list)) {
    ld_join_stop("variant_catalog_absent",
                 "no --variant-list supplied; the panel<->fit bridge cannot be built")
  }
  if (!file.exists(opt$variant_list)) {
    ld_join_stop("variant_catalog_missing",
                 sprintf("--variant-list %s does not exist", opt$variant_list))
  }
  catalog <- tryCatch(as.data.frame(fread(opt$variant_list)),
                      error = function(e) NULL)
  if (is.null(catalog) || nrow(catalog) == 0) {
    ld_join_stop("variant_catalog_unreadable",
                 sprintf("--variant-list %s is unreadable or empty", opt$variant_list))
  }

  # ---- the panel side ----
  panel_variants <- if (is.list(ld_obj) && !is.matrix(ld_obj)) ld_obj$variants else NULL
  if (is.null(panel_variants) || !is.data.frame(panel_variants)) {
    ld_join_stop("panel_variants_absent",
                 "the LD .rds carries no `variants` frame, so its rows cannot be allele-keyed")
  }
  if (nrow(panel_variants) != nrow(ld_full)) {
    # A variants frame out of step with R would silently bind every z to the
    # wrong row -- the exact error class this join exists to remove.
    ld_join_stop("panel_variants_out_of_step",
                 sprintf("variants rows=%d but R rows=%d",
                         nrow(panel_variants), nrow(ld_full)))
  }

  # ---- the shared allele-aware 4-key join ----
  join <- ld_allele_join_indices(catalog, panel_variants)
  LD_JOIN_COUNTS <- join$counts
  if (!is.null(join$counts$reject)) {
    ld_join_stop(join$counts$reject,
                 "verification is impossible: one side carries no usable REF/ALT")
  }

  # ⚠ `join$orient` IS MEASURED AND REPORTED, AND DELIBERATELY NOT APPLIED.
  # This closes the ROW-BINDING half only. Signing the QTL beta against the
  # panel's ALT (E-2) is pre-existing on the legacy 1kG/EUR path, is not named by
  # finding E, and correcting it would move Track-A EUR numbers that are in
  # submission. What the counters buy is that E-2's magnitude becomes MEASURABLE
  # (ld_allele_flipped) instead of invisible. See
  # .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md.

  # ---- MEASURE the candidate key spaces; do not assume one ----
  # The same best-overlap discipline this script already uses on the QTL side.
  bound_cat <- join$keep
  bound_pan <- join$ld
  cat_snp_id <- if ("SNP_ID" %in% names(catalog))
    as.character(catalog$SNP_ID)[bound_cat] else rep(NA_character_, length(bound_cat))
  cat_chrpos <- paste(toupper(trimws(as.character(catalog$CHR)))[bound_cat],
                      suppressWarnings(as.integer(catalog$POS))[bound_cat], sep = ":")
  pan_chrpos <- paste(toupper(trimws(as.character(panel_variants$CHR))),
                      suppressWarnings(as.integer(panel_variants$POS)), sep = ":")
  pan_k4 <- paste(pan_chrpos,
                  toupper(trimws(as.character(panel_variants$REF))),
                  toupper(trimws(as.character(panel_variants$ALT))), sep = ":")

  diagnostic_spaces <- list(
    panel_rownames = rownames(ld_full) %||% character(0),
    panel_chrpos = pan_chrpos,
    panel_chrpos_ref_alt = pan_k4
  )
  bridged_spaces <- list(
    catalog_snp_id = cat_snp_id,
    catalog_chrpos = cat_chrpos
  )
  all_spaces <- c(diagnostic_spaces, bridged_spaces)
  LD_CANDIDATE_OVERLAPS <- vapply(
    all_spaces, function(v) length(intersect(overlap_snps, v[!is.na(v)])), integer(1))
  cat(sprintf("[run_qtl_coloc] LD candidate key-space overlaps: %s\n",
              paste(sprintf("%s=%d", names(LD_CANDIDATE_OVERLAPS),
                            LD_CANDIDATE_OVERLAPS), collapse = ", ")))

  bridged_overlaps <- LD_CANDIDATE_OVERLAPS[names(bridged_spaces)]
  LD_KEY_SPACE <- names(which.max(bridged_overlaps))
  chosen <- bridged_spaces[[LD_KEY_SPACE]]

  # A bridged name that appears twice cannot bind to ONE panel row, so it is
  # removed from the lookup ENTIRELY rather than resolved by first-hit -- the
  # 260805-23d "a fallback that is never constructed cannot be silently taken"
  # discipline, applied to the bridge as well as to the 4-key.
  usable <- !is.na(chosen) & nzchar(chosen)
  dup <- duplicated(chosen) | duplicated(chosen, fromLast = TRUE)
  keep_bridge <- usable & !dup
  ld_row_index <- bound_pan[keep_bridge]
  names(ld_row_index) <- chosen[keep_bridge]
  ld_snp_names <- names(ld_row_index)
  LD_PANEL_OVERLAP <- length(intersect(overlap_snps, ld_snp_names))
}

# Final overlap must include the LD matrix's named variants (unless identity
# fallback, in which case we already built LD over overlap_snps).
if (!exists("use_identity") || !isTRUE(use_identity)) {
  overlap_snps <- intersect(overlap_snps, ld_snp_names)
  n_snps_overlap <- length(overlap_snps)
  if (LD_ALLELE_JOIN) {
    LD_PANEL_OVERLAP <- n_snps_overlap
    if (n_snps_overlap < MIN_COLOC_LD_OVERLAP) {
      # F3: at 7b1025d this wrote too_few_snps and EXITED 0, which in bulk is
      # indistinguishable from biology. Under the gate it is a DAG failure.
      ld_join_stop("panel_bridge_below_threshold",
                   sprintf("key_space=%s; the bridged panel<->fit overlap is below the floor",
                           LD_KEY_SPACE %||% "none"))
    }
    # BOUNDED COERCION. Subset the SPARSE matrix by INTEGER panel row indices
    # FIRST, coerce the SUBSET, then attach FIT-SPACE dimnames. Never
    # as.matrix(ld_full): T-w7u-04.
    idx <- as.integer(ld_row_index[overlap_snps])
    ld_matrix_subset <- as.matrix(ld_full[idx, idx, drop = FALSE])
    dimnames(ld_matrix_subset) <- list(overlap_snps, overlap_snps)
    storage.mode(ld_matrix_subset) <- "double"
  } else {
    if (n_snps_overlap < 50) {
      write_status_json("too_few_snps",
                        sprintf("Only %d SNPs after LD intersection (need >= 50)", n_snps_overlap))
      quit(status = 0)
    }
    ld_matrix_subset <- ld_full[overlap_snps, overlap_snps, drop = FALSE]
  }
}

# Subset QTL data to overlap SNPs (in same order as LD matrix rows).
qtl_df <- qtl_df[match(overlap_snps, qtl_df[[match_key]]), ]

# -------------------------------------------------------------------------
# 5. Build QTL dataset list for coloc
# -------------------------------------------------------------------------
qtl_data <- list(
  beta     = qtl_df$beta,
  varbeta  = qtl_df$se^2,
  snp      = overlap_snps,
  position = qtl_df$position,
  type     = "quant",
  N        = as.integer(opt$sample_size),
  sdY      = as.numeric(opt$sdy),
  MAF      = qtl_df$maf,
  LD       = ld_matrix_subset
)

# -------------------------------------------------------------------------
# 6. Validate QTL dataset (T-02-07 mitigation)
# -------------------------------------------------------------------------
tryCatch({
  coloc::check_dataset(qtl_data, req = "LD")
}, error = function(e) {
  write_status_json("qtl_dataset_invalid", conditionMessage(e))
  quit(status = 0)
})

# -------------------------------------------------------------------------
# 7. Fit SuSiE on QTL side
# -------------------------------------------------------------------------
qtl_fit <- tryCatch({
  coloc::runsusie(qtl_data, suffix = 2)
}, error = function(e) {
  cat(sprintf("[run_qtl_coloc] runsusie failed: %s, retrying with max_iter=200\n",
              conditionMessage(e)))
  tryCatch({
    coloc::runsusie(qtl_data, suffix = 2, maxit = 200)
  }, error = function(e2) {
    NULL
  })
})

if (is.null(qtl_fit)) {
  write_status_json("qtl_susie_failed", "runsusie() failed after retry with max_iter=200")
  quit(status = 0)
}

# -------------------------------------------------------------------------
# 8. Check for credible sets on QTL side
# -------------------------------------------------------------------------
cs_qtl <- qtl_fit$sets$cs %||% list()
n_cs_qtl <- length(cs_qtl)
cs_gwas <- gwas_fit$sets$cs %||% list()
n_cs_gwas <- length(cs_gwas)

if (n_cs_qtl == 0) {
  result <- list(
    status        = "no_qtl_cs",
    message       = "No credible sets on QTL side",
    qtl_source    = opt$qtl_source %||% NA_character_,
    tissue        = opt$tissue %||% NA_character_,
    gene_id       = opt$gene_id %||% NA_character_,
    region        = opt$region %||% NA_character_,
    ancestry      = opt$ancestry %||% NA_character_,
    n_snps_overlap = n_snps_overlap,
    qtl_n         = opt$sample_size %||% NA_integer_,
    qtl_sdy       = opt$sdy %||% NA_real_,
    summary       = list(),
    all_pairs     = list(),
    n_cs_gwas     = n_cs_gwas,
    n_cs_qtl      = 0L
  )
  result <- attach_ld_provenance(result)
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(result, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
  cat(sprintf("[run_qtl_coloc] no_qtl_cs for %s/%s -- wrote %s\n",
              opt$gene_id %||% "?", opt$tissue %||% "?", opt$output))
  quit(status = 0)
}

if (n_cs_gwas == 0) {
  result <- list(
    status        = "no_gwas_cs",
    message       = "No credible sets on GWAS side",
    qtl_source    = opt$qtl_source %||% NA_character_,
    tissue        = opt$tissue %||% NA_character_,
    gene_id       = opt$gene_id %||% NA_character_,
    region        = opt$region %||% NA_character_,
    ancestry      = opt$ancestry %||% NA_character_,
    n_snps_overlap = n_snps_overlap,
    qtl_n         = opt$sample_size %||% NA_integer_,
    qtl_sdy       = opt$sdy %||% NA_real_,
    summary       = list(),
    all_pairs     = list(),
    n_cs_gwas     = 0L,
    n_cs_qtl      = n_cs_qtl
  )
  result <- attach_ld_provenance(result)
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(result, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
  cat(sprintf("[run_qtl_coloc] no_gwas_cs for %s/%s -- wrote %s\n",
              opt$gene_id %||% "?", opt$tissue %||% "?", opt$output))
  quit(status = 0)
}

# -------------------------------------------------------------------------
# 9. Run coloc.susie
# -------------------------------------------------------------------------
res <- coloc::coloc.susie(gwas_fit, qtl_fit)
summary_dt <- as.data.table(res$summary)

# -------------------------------------------------------------------------
# Posterior sum sanity check (same pattern as Phase 1 run_coloc_susie.R)
# -------------------------------------------------------------------------
pp_cols <- c("PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf")
if (all(pp_cols %in% names(summary_dt)) && nrow(summary_dt) > 0) {
  row_sums <- rowSums(summary_dt[, ..pp_cols])
  max_dev <- max(abs(row_sums - 1.0), na.rm = TRUE)
  if (is.finite(max_dev) && max_dev > 1e-4) {
    warning(sprintf(
      "[run_qtl_coloc] posterior sum deviation %.2e > 1e-4 in %d rows",
      max_dev, sum(abs(row_sums - 1.0) > 1e-4, na.rm = TRUE)))
  }
}

# -------------------------------------------------------------------------
# 10. Build output: best pairwise row + all pairs
# -------------------------------------------------------------------------
if (nrow(summary_dt) > 0 && "PP.H4.abf" %in% names(summary_dt)) {
  best_idx <- which.max(summary_dt$PP.H4.abf)
  best_row <- if (length(best_idx) == 1) as.list(summary_dt[best_idx]) else list()
} else {
  best_row <- list()
}

output <- list(
  status         = "success",
  qtl_source     = opt$qtl_source %||% NA_character_,
  tissue         = opt$tissue %||% NA_character_,
  gene_id        = opt$gene_id %||% NA_character_,
  region         = opt$region %||% NA_character_,
  ancestry       = opt$ancestry %||% NA_character_,
  n_snps_overlap = n_snps_overlap,
  qtl_n          = opt$sample_size %||% NA_integer_,
  qtl_sdy        = opt$sdy %||% NA_real_,
  summary        = best_row,
  all_pairs      = lapply(seq_len(nrow(summary_dt)),
                          function(i) as.list(summary_dt[i])),
  n_cs_gwas      = n_cs_gwas,
  n_cs_qtl       = n_cs_qtl
)
output <- attach_ld_provenance(output)

# -------------------------------------------------------------------------
# 11. Write output JSON
# -------------------------------------------------------------------------
dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
write_json(output, opt$output, auto_unbox = TRUE, pretty = TRUE, na = "null")
cat(sprintf("[run_qtl_coloc] wrote %s with %d pairwise rows (n_cs_gwas=%d, n_cs_qtl=%d)\n",
            opt$output, nrow(summary_dt), n_cs_gwas, n_cs_qtl))
