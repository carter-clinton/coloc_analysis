#!/usr/bin/env Rscript
# A6 RESOLUTION (01-01-07 result 2026-04-12): coloc.susie requires annotate_susie-style
# field additions (named pip, named sets, sld). Rather than switching to coloc::runsusie
# (which takes a coloc dataset list, not raw z/R/n -- plan pre-spec was factually incorrect),
# we call coloc:::annotate_susie(fit, snp_names, R) on each fit before saveRDS. This
# produces a .fit.rds that coloc.susie can consume directly in Wave 3. Task 1-01-02 notes.
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(susieR)
  library(jsonlite)
  library(Matrix)
  library(yaml)
  library(digest)
  library(coloc)
})

`%||%` <- function(x, y) {
  if (!is.null(x)) x else y
}

# Helpers: regularize LD + structured retry ladder (REQ-2 convergence policy).
# MIN_LD_* constants are now loaded from YAML policy at runtime (see below).

regularize_ld <- function(R, eps = 1e-4) {
  R_reg <- R + diag(eps, nrow(R))
  (R_reg + t(R_reg)) / 2
}

run_susie_with_ladder <- function(z, R, policy, n) {
  L_ <- policy$L
  cov_ <- policy$coverage
  max1 <- policy$max_iter_primary
  max2 <- policy$max_iter_retry
  eps  <- policy$ld_regularization_eps

  susie_call <- function(R_use, max_it) {
    # NOTE 2026-04-29: susieR::susie_rss has no `max_iterations` formal — it forwards
    # `...` to susie_suff_stat (sufficient-statistics path) whose iteration cap is
    # `max_iter` (default 100). The previous `max_iterations = max_it` argument name
    # was silently swallowed and ignored, causing every fit to run with the default
    # max_iter=100 regardless of policy. Use `max_iter = max_it` so it propagates.
    # Bug surfaced 2026-04-29 during niter=500 re-fire (W1 Carter option-a) when the
    # patched policy YAMLs failed to lift the cap; verified against susieR 0.14.2.
    args <- list(z = z, R = R_use, L = L_, coverage = cov_, max_iter = max_it)
    if (!is.null(n) && !is.na(n) && is.finite(n)) args$n <- n
    do.call(susieR::susie_rss, args)
  }

  fit1 <- tryCatch(susie_call(R, max1), error = function(e) NULL)
  if (!is.null(fit1) && isTRUE(fit1$converged))
    return(list(fit = fit1, status = "converged_primary"))

  fit2 <- tryCatch(susie_call(R, max2), error = function(e) NULL)
  if (!is.null(fit2) && isTRUE(fit2$converged))
    return(list(fit = fit2, status = "converged_max_iter"))

  R_reg <- regularize_ld(R, eps)
  fit3 <- tryCatch(susie_call(R_reg, max2), error = function(e) NULL)
  if (!is.null(fit3) && isTRUE(fit3$converged))
    return(list(fit = fit3, status = "converged_regularized"))

  fit_keep <- fit3 %||% fit2 %||% fit1
  if (!is.null(fit_keep) && !inherits(fit_keep, "susie"))
    class(fit_keep) <- c("susie", class(fit_keep))
  list(fit = fit_keep, status = "non_converged")
}

safe_region_id <- function(region_id) {
  gsub("[^A-Za-z0-9_]", "_", region_id)
}

# m3-04c Task 1b (DEC-2026-08-05-m3-ld-read-path): `ld_file` is the LD .rds that
# Snakemake DECLARED as run_finemap's `input.ld_matrix`, i.e. whatever
# src/python/ld_panel.py::resolve_ld_path selected. It is AUTHORITATIVE when
# readable; the `ld_dir` reconstruction below survives strictly as the
# back-compat fallback for callers that pass no --ld-file.
#
# WHY: before this, the declared input was never passed to this script, so a
# declared `input:` absent from the rule's `shell:` was a DAG DECLARATION ONLY
# (BLOCKER-1). This function rebuilt its own path as
# file.path(ld_dir, ancestry, region_id + ".rds") -- where `ancestry` is "AFR"
# and never "AFR_aou" -- so the AoU panel was UNREACHABLE and every AFR fit fell
# silently through to the identity matrix below. `ld_file` is placed FIRST in
# the candidate list so resolve_ld_path is the single source of truth.
#
# `ld_file` is the LAST formal and defaults to NULL, so every existing
# positional caller is unaffected.
load_ld_matrix <- function(ld_dir, ancestry, region_id, subset, ld_file = NULL) {
  # THE TRAP (m3-04c Task 1b): the pre-change guard tested ld_dir ALONE, so a
  # naive --ld-file addition would still bail here whenever ld_dir was absent --
  # i.e. it would do nothing in exactly the case it exists for. Bail only when
  # NEITHER source is usable. The status string stays byte-identical for the
  # both-absent case so nothing downstream moves.
  have_ld_file <- !is.null(ld_file) && nzchar(ld_file) && file.exists(ld_file)
  have_ld_dir  <- !is.null(ld_dir) && ld_dir != "" && file.exists(ld_dir)
  if (!have_ld_file && !have_ld_dir) {
    return(list(R = NULL, source = NULL, status = "ld_dir_missing"))
  }

  match_indices <- function(subset_dt, variants_dt) {
    keep_idx <- integer(0)
    ld_idx <- integer(0)

    if (!is.null(variants_dt) &&
        "SNP_ID" %in% names(variants_dt) &&
        "SNP_ID" %in% names(subset_dt)) {
      subset_ids <- subset_dt$SNP_ID
      variant_ids <- variants_dt$SNP_ID
      valid_subset <- which(!is.na(subset_ids) & subset_ids != "")
      if (length(valid_subset) > 0) {
        valid_variants <- which(!is.na(variant_ids) & variant_ids != "")
        if (length(valid_variants) > 0) {
          matches <- match(subset_ids[valid_subset], variant_ids[valid_variants])
          matched <- !is.na(matches)
          if (any(matched)) {
            keep_idx <- c(keep_idx, valid_subset[matched])
            ld_idx <- c(ld_idx, valid_variants[matches[matched]])
          }
        }
      }
    }

    remaining <- setdiff(seq_len(nrow(subset_dt)), keep_idx)
    if (!is.null(variants_dt) &&
        all(c("CHR", "POS") %in% names(variants_dt)) &&
        length(remaining) > 0) {
      key_subset <- paste(subset_dt$CHR[remaining], subset_dt$POS[remaining], sep = ":")
      key_ld <- paste(variants_dt$CHR, variants_dt$POS, sep = ":")
      matches <- match(key_subset, key_ld)
      matched <- !is.na(matches)
      if (any(matched)) {
        keep_idx <- c(keep_idx, remaining[matched])
        ld_idx <- c(ld_idx, matches[matched])
      }
    }

    if (length(keep_idx) > 0) {
      ord <- order(keep_idx)
      keep_idx <- keep_idx[ord]
      ld_idx <- ld_idx[ord]
    }
    list(keep = keep_idx, ld = ld_idx)
  }

  safe_id <- safe_region_id(region_id)
  # Build the ld_dir reconstruction ONLY when ld_dir is usable: R's
  # file.path(NULL, "AFR", "x.rds") returns character(0) and
  # file.path("", "AFR", "x.rds") returns an absolute "/AFR/x.rds" -- both wrong.
  dir_candidates <- if (have_ld_dir) unique(c(
    file.path(ld_dir, ancestry, paste0(region_id, ".rds")),
    file.path(ld_dir, ancestry, paste0(safe_id, ".rds"))
  )) else character(0)
  # The DECLARED file goes FIRST: that is what makes resolve_ld_path the single
  # source of truth for which LD matrix a fit reads (m3-04c Task 1b).
  candidates <- unique(c(
    if (have_ld_file) ld_file else character(0),
    dir_candidates
  ))

  n_subset <- nrow(subset)
  best_partial <- NULL
  seen_candidate <- FALSE
  best_overlap <- 0

  for (candidate in candidates) {
    if (!file.exists(candidate)) {
      next
    }
    seen_candidate <- TRUE
    obj <- tryCatch(readRDS(candidate), error = function(e) NULL)
    if (is.null(obj)) {
      next
    }
    overlap <- 0
    coverage <- 0
    if (is.list(obj)) {
      use_identity <- isTRUE(obj$use_identity)
      status_label <- obj$status %||% "ld_loaded"
      R <- obj$R
      variants <- obj$variants
      if (use_identity && is.null(R)) {
        return(list(R = NULL, source = candidate, status = status_label, variants = variants))
      }
      if (is.null(R)) {
        next
      }
      if (is.null(variants) && !is.null(obj$variants)) {
        variants <- obj$variants
      }
    } else if (is.matrix(obj) || inherits(obj, "Matrix")) {
      R <- obj
      variants <- NULL
    } else {
      next
    }

    match_info <- match_indices(subset, variants)
    keep_idx <- match_info$keep
    ld_idx <- match_info$ld
    overlap <- length(keep_idx)
    coverage <- if (n_subset > 0) overlap / n_subset else 0
    best_overlap <- max(best_overlap, overlap)

    if (!is.null(variants) && length(keep_idx) > 0 && !is.null(ld_idx)) {
      variants <- variants[ld_idx, , drop = FALSE]
      if (!is.null(R)) {
        R <- R[ld_idx, ld_idx, drop = FALSE]
      }
    } else if (nrow(R) != length(keep_idx)) {
      if (overlap < MIN_LD_MIN_USE) {
        next
      }
    }

    if (overlap >= MIN_LD_OVERLAP && coverage >= MIN_LD_COVERAGE) {
      status_final <- status_label
      if (grepl("^ld_loaded", status_label)) {
        status_final <- sprintf("ld_loaded;overlap_ok;%d;%.3f", overlap, coverage)
      }
      return(list(
        R = as.matrix(R),
        source = candidate,
        status = status_final,
        variants = variants,
        subset_idx = keep_idx,
        overlap = overlap,
        coverage = coverage
      ))
    }

    if (overlap >= MIN_LD_MIN_USE) {
      status_partial <- status_label
      if (grepl("^ld_loaded", status_label)) {
        status_partial <- sprintf("ld_loaded;partial_overlap;%d;%.3f", overlap, coverage)
      }
      best_partial <- list(
        R = as.matrix(R),
        source = candidate,
        status = status_partial,
        variants = variants,
        subset_idx = keep_idx,
        overlap = overlap,
        coverage = coverage
      )
    }
  }

  if (!is.null(best_partial)) {
    return(best_partial)
  }

  if (seen_candidate && best_overlap > 0) {
    return(list(
      R = NULL,
      source = NULL,
      status = "ld_overlap_insufficient",
      overlap = best_overlap,
      coverage = if (n_subset > 0) best_overlap / n_subset else 0
    ))
  }

  list(R = NULL, source = NULL, status = "ld_missing", overlap = 0, coverage = 0)
}

option_list <- list(
  make_option("--sumstats", type = "character", help = "Path to harmonized sumstats (.tsv.bgz)"),
  make_option("--trait", type = "character", help = "Trait name"),
  make_option("--ancestry", type = "character", help = "Ancestry label"),
  make_option("--method", type = "character", help = "Fine-mapping method"),
  make_option("--region", type = "character", help = "Region ID"),
  make_option("--regions-csv", type = "character", help = "CSV defining regions"),
  make_option("--ld-dir", type = "character", help = "Directory containing ancestry-specific LD (optional)"),
  # m3-04c Task 1b (DEC-2026-08-05-m3-ld-read-path): the resolved LD .rds that
  # Snakemake declared as run_finemap's input.ld_matrix (i.e. resolve_ld_path's
  # answer). AUTHORITATIVE when readable -- it is tried FIRST -- and the
  # --ld-dir reconstruction is the back-compat fallback for callers that omit
  # it. Without this the declared input was a DAG declaration only and the
  # AFR_aou panel was unreachable (BLOCKER-1).
  make_option("--ld-file", type = "character", default = NULL,
              help = paste("Resolved LD .rds declared by Snakemake as input.ld_matrix.",
                           "Authoritative when readable; --ld-dir is the fallback.")),
  make_option("--variant-list", type = "character", help = "Optional TSV restricting variants (CHR,POS,REF,ALT)"),
  make_option("--credible-set", type = "double", default = 0.95, help = "Credible set probability"),
  make_option("--policy", type = "character", default = "config/susie_policy.yaml",
              help = "Path to SuSiE policy YAML"),
  make_option("--output", type = "character", help = "Output JSON path")
)

opt <- parse_args(OptionParser(option_list = option_list))
SUSIE_MAX_VARIANTS <- as.integer(Sys.getenv("SUSIE_MAX_VARIANTS", "6000"))

# Load policy from YAML (REQ-2 #2). Replaces former env-var lookups (MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE).
# Defaults preserve backward compatibility if policy is missing fields.
policy <- yaml::read_yaml(opt$policy)
MIN_LD_OVERLAP       <- policy$susie$min_ld_overlap       %||% 50L
MIN_LD_COVERAGE      <- policy$susie$min_ld_coverage      %||% 0.5
MIN_LD_MIN_USE       <- policy$susie$min_ld_min_use       %||% 10L
L_DEFAULT            <- policy$susie$L                    %||% 10L
COVERAGE             <- policy$susie$coverage             %||% 0.95
MAX_ITER_PRIMARY     <- policy$susie$max_iter_primary     %||% 100L
MAX_ITER_RETRY       <- policy$susie$max_iter_retry       %||% 200L
LD_REG_EPS           <- policy$susie$ld_regularization_eps %||% 1e-4
MIN_ABS_CORR_DEFAULT <- policy$susie$min_abs_corr_default %||% 0.5
MIN_ABS_CORR_SWEEP   <- policy$susie$min_abs_corr_sweep   %||% c(0.1, 0.5, 0.9)

regions <- fread(opt$`regions-csv`)
if (!"region_id" %in% names(regions)) {
  stop("regions CSV must include column 'region_id'")
}
if (!(opt$region %in% regions$region_id)) {
  stop(sprintf("Region %s not found in %s", opt$region, opt$`regions-csv`))
}
reg <- regions[region_id == opt$region][1]

read_cmd <- sprintf("gunzip -c %s", shQuote(opt$sumstats))
sumstats <- fread(cmd = read_cmd)
if (!all(c("CHR", "POS", "BETA", "SE") %in% names(sumstats))) {
  stop("Sumstats must include CHR, POS, BETA, SE columns")
}

if (!"SNP_ID" %in% names(sumstats)) {
  sumstats[, SNP_ID := NA_character_]
} else {
  sumstats[, SNP_ID := as.character(SNP_ID)]
  sumstats[SNP_ID == "" | SNP_ID == "NA", SNP_ID := NA_character_]
}

sumstats[, CHR := as.character(CHR)]
subset <- sumstats[
  CHR == as.character(reg$chr) &
    POS >= as.numeric(reg$start) &
    POS <= as.numeric(reg$end)
]
subset_base <- copy(subset)
ancestry_upper <- toupper(opt$ancestry)
used_variant_catalog <- FALSE
variant_catalog_attempted <- FALSE
variant_catalog_fallback <- FALSE
ld_overlap_zero_fallback <- FALSE  # m3-04c HIGH-2: set only by the Path-2 (ld_overlap==0) revert

if (!is.null(opt$`variant-list`) && opt$`variant-list` != "" && file.exists(opt$`variant-list`)) {
  variant_dt <- tryCatch(fread(opt$`variant-list`), error = function(e) NULL)
  if (!is.null(variant_dt) && nrow(variant_dt) > 0) {
    variant_catalog_attempted <- TRUE
    use_snp_id <- ("SNP_ID" %in% names(variant_dt) && "SNP_ID" %in% names(subset))
    if (use_snp_id) {
      variant_dt[, SNP_ID := as.character(SNP_ID)]
      subset[, SNP_ID := as.character(SNP_ID)]
      variant_nonmissing <- sum(!is.na(variant_dt$SNP_ID) & variant_dt$SNP_ID != "")
      subset_nonmissing <- sum(!is.na(subset$SNP_ID) & subset$SNP_ID != "")
      if (variant_nonmissing < 10 || subset_nonmissing < 10) {
        message("SNP_ID mostly missing; falling back to CHR/POS join.")
        use_snp_id <- FALSE
      }
    }

    if (use_snp_id) {
      variant_dt[, idx := .I]
      subset <- subset[variant_dt, on = "SNP_ID", nomatch = 0][order(idx)]
      subset[, idx := NULL]
      used_variant_catalog <- nrow(subset) > 0
      if ("i.CHR" %in% names(subset)) {
        subset[!is.na(`i.CHR`), CHR := as.character(`i.CHR`)]
        subset[, `i.CHR` := NULL]
      }
      if ("i.POS" %in% names(subset)) {
        subset[!is.na(`i.POS`), POS := as.integer(`i.POS`)]
        subset[, `i.POS` := NULL]
      }
    } else if (all(c("CHR", "POS") %in% names(variant_dt))) {
      variant_dt[, CHR := as.character(CHR)]
      variant_dt[, POS := as.integer(POS)]
      variant_dt[, idx := .I]
      setkey(variant_dt, CHR, POS)
      setkey(subset, CHR, POS)
      subset <- subset[variant_dt, nomatch = 0][order(idx)]
      subset[, idx := NULL]
      used_variant_catalog <- nrow(subset) > 0
    }
  }
}

if (
  nrow(subset) == 0 &&
  variant_catalog_attempted &&
  ancestry_upper == "AFR" &&
  nrow(subset_base) > 0
) {
  message(sprintf(
    "Variant catalog removed all SNPs for AFR region %s; using unfiltered region SNPs.",
    opt$region
  ))
  subset <- copy(subset_base)
  used_variant_catalog <- FALSE
  variant_catalog_fallback <- TRUE
}

if (nrow(subset) == 0) {
  warning(sprintf("No variants found for region %s", opt$region))
  result <- list(
    trait = opt$trait,
    ancestry = opt$ancestry,
    method = opt$method,
    region_id = opt$region,
    chrom = reg$chr,
    start = reg$start,
    end = reg$end,
    sumstats = opt$sumstats,
    ld_dir = opt$`ld-dir`,
    status = "no_variants",
    notes = "No variants within region bounds",
    variant_catalog_path = opt$`variant-list`,
    variant_catalog_attempted = variant_catalog_attempted,
    variant_catalog_used = used_variant_catalog,
    variant_catalog_fallback = variant_catalog_fallback
  )
  write(toJSON(result, auto_unbox = TRUE, pretty = TRUE), file = opt$output)
  # Write placeholder .fit.rds so Snakemake's dual-output rule doesn't raise
  # MissingOutputException for regions with no variants.
  fit_rds_path <- sub("\\.json$", ".fit.rds", opt$output)
  saveRDS(list(status = "no_variants", region = opt$region), file = fit_rds_path)
  quit(status = 0)
}

if (nrow(subset) > SUSIE_MAX_VARIANTS) {
  warning(sprintf(
    "Region %s contains %d variants (limit %d). Skipping fine-mapping.",
    opt$region,
    nrow(subset),
    SUSIE_MAX_VARIANTS
  ))
  result <- list(
    trait = opt$trait,
    ancestry = opt$ancestry,
    method = opt$method,
    region_id = opt$region,
    chrom = reg$chr,
    start = reg$start,
    end = reg$end,
    sumstats = opt$sumstats,
    ld_dir = opt$`ld-dir`,
    status = "too_many_variants",
    notes = sprintf("n_variants=%d exceeds SUSIE_MAX_VARIANTS=%d", nrow(subset), SUSIE_MAX_VARIANTS),
    variant_catalog_path = opt$`variant-list`,
    variant_catalog_attempted = variant_catalog_attempted,
    variant_catalog_used = used_variant_catalog,
    variant_catalog_fallback = variant_catalog_fallback
  )
  write(toJSON(result, auto_unbox = TRUE, pretty = TRUE), file = opt$output)
  # Write placeholder .fit.rds so Snakemake's dual-output rule doesn't raise
  # MissingOutputException for skipped dense regions (PYHIN1, HLA, etc.)
  fit_rds_path <- sub("\\.json$", ".fit.rds", opt$output)
  saveRDS(list(status = "too_many_variants",
               region = opt$region,
               n_variants = nrow(subset),
               limit = SUSIE_MAX_VARIANTS), file = fit_rds_path)
  quit(status = 0)
}

attempt <- 1
repeat {
  # m3-04c Task 1b: --ld-file (the artifact Snakemake DECLARED, via
  # resolve_ld_path) is threaded through and wins over the --ld-dir
  # reconstruction. opt$`ld-dir` at :368/:400/the result list stays as-is: it is
  # provenance, not the read path.
  ld_result <- load_ld_matrix(opt$`ld-dir`, opt$ancestry, opt$region, subset, ld_file = opt$`ld-file`)
  ld_overlap <- ld_result$overlap %||% 0
  if (ld_overlap == 0 && used_variant_catalog && attempt == 1) {
    message("No LD overlap after applying variant catalog filter; retrying without catalog restriction.")
    subset <- copy(subset_base)
    used_variant_catalog <- FALSE
    # m3-04c Task 1b / HIGH-2: this revert used to leave NO distinguishing
    # signal -- used_variant_catalog went FALSE exactly as it does on the Path-1
    # (AFR empty-filtered-subset) revert, and variant_catalog_fallback was never
    # set. Both flags are now recorded and both are read by the per-region
    # estimate_s log. Science behaviour is UNCHANGED: still one retry against
    # subset_base. Only observability changes.
    variant_catalog_fallback <- TRUE
    ld_overlap_zero_fallback <- TRUE
    attempt <- attempt + 1
    next
  }
  break
}

if (!is.null(ld_result$subset_idx)) {
  subset <- subset[ld_result$subset_idx]
}

# susie_credible_set_yield (2026-04-21): prefer the LD-side variant identifier
# as the canonical SNP name when the LD panel has authoritative rsids
# (e.g., 1000G EUR Phase 3 plink via build_ld_rds_1kg_eur), but only when
# the sumstats-side SNP_ID is a non-rsid (e.g., "12:111400006" from the
# Evangelou 2018 BP sumstats). This ensures annotate_susie names the fit
# with rsids — the build-invariant cross-source key that run_qtl_coloc.R
# uses for GWAS↔QTL variant matching. Without this, QTL coloc reports
# too_few_snps across all SH2B3/APOE/9p21/etc. rows because chr:pos-style
# SNP_IDs cannot be matched against GRCh38 QTL positions.
if (!is.null(ld_result$variants) &&
    "SNP_ID" %in% names(ld_result$variants) &&
    nrow(ld_result$variants) == nrow(subset)) {
  ld_ids <- as.character(ld_result$variants$SNP_ID)
  current_ids <- as.character(subset$SNP_ID)
  is_rsid_ld      <- grepl("^rs[0-9]+$", ld_ids)
  is_chrpos_sumst <- grepl("^[0-9XY]+:[0-9]+$", current_ids)
  # Override only where LD has a clean rsid and sumstats has a chr:pos or blank
  replace_mask <- is_rsid_ld & (is_chrpos_sumst | is.na(current_ids) | current_ids == "")
  if (any(replace_mask)) {
    message(sprintf(
      "Overriding %d sumstats SNP_IDs with LD-panel rsids (%d already rsid, %d unmatched).",
      sum(replace_mask),
      sum(grepl("^rs[0-9]+$", current_ids)),
      sum(!replace_mask & !grepl("^rs[0-9]+$", current_ids))
    ))
    subset[replace_mask, SNP_ID := ld_ids[replace_mask]]
  }
}

subset[, z := BETA / SE]
mean_n <- suppressWarnings(mean(as.numeric(subset$N), na.rm = TRUE))
if (is.nan(mean_n) || is.infinite(mean_n)) {
  mean_n <- NA
}
ld_overlap_fraction <- ld_result$coverage %||% 0
if (is.null(ld_result$R)) {
  message(sprintf("No LD matrix found for %s (%s). Falling back to identity.", opt$region, opt$ancestry))
  R <- diag(nrow(subset))
  ld_source <- ld_result$source %||% "identity"
  ld_status <- ld_result$status
} else {
  R <- ld_result$R
  R <- (R + t(R)) / 2
  diag(R) <- 1
  ld_source <- ld_result$source
  ld_status <- ld_result$status
}

# REQ-2: structured retry ladder driven by YAML policy (Task 1-01-02).
# Replaces former 2-step tryCatch (max_iter bump + local regularize_ld with eps=1e-6).
ladder_policy <- list(
  L = min(L_DEFAULT, nrow(subset)),
  coverage = opt$`credible-set` %||% COVERAGE,
  max_iter_primary = MAX_ITER_PRIMARY,
  max_iter_retry = MAX_ITER_RETRY,
  ld_regularization_eps = LD_REG_EPS
)
ladder_out <- run_susie_with_ladder(
  z = subset$z,
  R = R,
  policy = ladder_policy,
  n = mean_n
)
fit <- ladder_out$fit
convergence_status <- ladder_out$status
if (is.null(fit)) {
  # Final identity fallback (preserves prior behavior of always returning a fit object)
  message(sprintf(
    "Retry ladder exhausted for %s (%s); falling back to identity LD.",
    opt$region, opt$ancestry
  ))
  ld_status <- paste(ld_status, "fallback_identity", sep = ";")
  ld_source <- "identity_fallback"
  ladder_out <- run_susie_with_ladder(
    z = subset$z, R = diag(nrow(subset)),
    policy = ladder_policy, n = mean_n
  )
  fit <- ladder_out$fit
  convergence_status <- paste(ladder_out$status, "identity_fallback", sep = ";")
}
cs <- susie_get_cs(fit)

credible_sets <- list()
if (!is.null(cs$cs)) {
  for (i in seq_along(cs$cs)) {
    set_indices <- cs$cs[[i]]
    variants <- subset[set_indices, list(CHR, POS, BETA, SE, pip = fit$pip[set_indices])]
    credible_sets[[paste0("CS", i)]] <- variants
  }
}

result <- list(
  trait = opt$trait,
  ancestry = opt$ancestry,
  method = opt$method,
  region_id = opt$region,
  chrom = reg$chr,
  start = reg$start,
  end = reg$end,
    sumstats = opt$sumstats,
    ld_dir = opt$`ld-dir`,
    ld_matrix = ld_source,
    # m3-04c Task 1b: DECLARED beside OPENED. ld_matrix is the path this script
    # actually opened; ld_file_declared is the path Snakemake resolved and
    # passed. Their equality is the per-region receipt for
    # `resolved == what-the-script-opens` AFTER the fire (plan verification 11).
    # Additive JSON keys are safe: summarize_finemap_results.py reads with
    # .get() against a fixed FIELDNAMES list.
    ld_file_declared = opt$`ld-file`,
    ld_status = ld_status,
    ld_overlap = ld_overlap,
    ld_overlap_fraction = ld_overlap_fraction,
    status = "success",
    variant_catalog_path = opt$`variant-list`,
    variant_catalog_attempted = variant_catalog_attempted,
    variant_catalog_used = used_variant_catalog,
    variant_catalog_fallback = variant_catalog_fallback,
    ld_overlap_zero_fallback = ld_overlap_zero_fallback,
    credible_sets = credible_sets,
    pip = fit$pip[fit$pip > 0]
)

# ============================================================
# Task 1-01-02: Fit persistence + D1/D2/D3 diagnostics + post-hoc sweep.
# ============================================================

# A6 fallback: annotate fit with coloc-compatible metadata (named pip, named sets, sld).
# Must come BEFORE saveRDS so Wave 3 coloc.susie can consume the .fit.rds directly.
if (!is.null(fit)) {
  if (!inherits(fit, "susie")) class(fit) <- c("susie", class(fit))
  snp_names <- if ("SNP_ID" %in% names(subset) && !all(is.na(subset$SNP_ID))) {
    ifelse(is.na(subset$SNP_ID) | subset$SNP_ID == "",
           sprintf("%s:%s", subset$CHR, subset$POS),
           as.character(subset$SNP_ID))
  } else {
    sprintf("%s:%s", subset$CHR, subset$POS)
  }
  snp_names <- make.unique(snp_names)
  # t1_phase2_first_production bugfix (qtl_coloc_snp_name_mismatch, 2026-04-20):
  # coloc:::annotate_susie calls .susie_setld(res$sets$cs, LD) which indexes
  # LD by credible-set variant NAMES. When LD is an identity fallback built
  # via diag(nrow(subset)), it has no dimnames and the name-based indexing
  # errors with "no 'dimnames' attribute for array", causing annotate_susie
  # to fail silently (tryCatch returns the un-annotated fit). This then
  # blocks Phase 2 coloc (run_qtl_coloc.R cannot extract SNP names).
  # Fix: attach snp_names as dimnames to R BEFORE annotate_susie so identity
  # LD and real LD take the same code path. No behavioral change for
  # already-named LD (dimnames overwrite is a no-op when length(snp_names)
  # matches nrow(R)).
  if (is.null(dimnames(R)) && nrow(R) == length(snp_names)) {
    dimnames(R) <- list(snp_names, snp_names)
  }
  fit <- tryCatch(
    coloc:::annotate_susie(fit, snp_names, R),
    error = function(e) {
      message(sprintf("annotate_susie failed (%s); saving un-annotated fit.", conditionMessage(e)))
      fit
    }
  )
  fit_rds_path <- sub("\\.json$", ".fit.rds", opt$output)
  dir.create(dirname(fit_rds_path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(fit, file = fit_rds_path)
}

# D1 -- z-score sanity
z_ks <- tryCatch(ks.test(subset$z, "pnorm")$p.value, error = function(e) NA_real_)
d1 <- list(
  ks_pvalue = z_ks,
  max_abs_z = suppressWarnings(max(abs(subset$z), na.rm = TRUE)),
  lambda_gc = median(subset$z^2, na.rm = TRUE) / qchisq(0.5, df = 1)
)

# D2 -- convergence
d2 <- list(
  converged = isTRUE(fit$converged),
  niter = fit$niter %||% NA_integer_,
  elbo_final = if (!is.null(fit$elbo)) tail(fit$elbo, 1) else NA_real_,
  convergence_status = convergence_status
)

# D3 -- LD quality via kriging_rss (never serialize ggplot -- Pitfall 8)
krig <- tryCatch(
  susieR::kriging_rss(z = subset$z, R = R, n = mean_n),
  error = function(e) NULL
)
d3 <- if (!is.null(krig)) {
  # susieR::kriging_rss returns $conditional_dist (not $conc) in susieR >= 0.12
  conc <- krig$conditional_dist %||% krig$conc
  if (!is.null(conc) && !is.null(conc$logLR) && is.numeric(conc$z)) {
    list(
      n_outliers = sum(conc$logLR > 2 & abs(conc$z) > 2, na.rm = TRUE),
      max_logLR  = suppressWarnings(max(conc$logLR, na.rm = TRUE)),
      lambda     = krig$lambda %||% NA_real_
    )
  } else {
    list(n_outliers = NA_integer_, max_logLR = NA_real_, lambda = NA_real_)
  }
} else list(n_outliers = NA_integer_, max_logLR = NA_real_, lambda = NA_real_)

# D3b -- m3-02e Move 3 (Zou 2022): SuSiE-RSS estimate_s z-vs-LD consistency guard.
# estimate_s_rss returns a scalar s in [0,1] measuring agreement between the GWAS
# z-scores and the LD matrix. A high s indicates a z-vs-LD mismatch -- exactly the
# allele-flip / encoding failure that the native-plink AFR LD (--keep-allele-order)
# and the public-EUR hg19->hg38 liftover are most exposed to. Serialized per region
# (ld_z_consistency_s) so the finemap rule can flag an LD-source mismatch before it
# silently corrupts fine-mapping. tryCatch -> NA on any susieR-version/shape error
# (additive field; backward compatible with summarize_finemap_results.py).
s_estimate <- tryCatch(
  susieR::estimate_s_rss(z = subset$z, R = R, n = mean_n),
  error = function(e) NA_real_
)
result$d3b_ld_z_consistency_s   <- s_estimate
result$ld_source_mismatch_flag  <- isTRUE(is.numeric(s_estimate) && s_estimate > 0.5)

# Post-hoc min_abs_corr sweep (FREE -- no refit, Pattern 4)
sweep_rows <- lapply(MIN_ABS_CORR_SWEEP, function(macor) {
  cs_m <- tryCatch(
    susieR::susie_get_cs(fit, Xcorr = R, coverage = COVERAGE, min_abs_corr = macor),
    error = function(e) list(cs = list())
  )
  n_cs <- length(cs_m$cs %||% list())
  list(
    min_abs_corr = macor,
    n_CS = n_cs,
    cs_sizes = if (n_cs > 0) as.integer(sapply(cs_m$cs, length)) else integer(0),
    cs_pip_sum = if (n_cs > 0) as.numeric(sapply(cs_m$cs, function(idx) sum(fit$pip[idx]))) else numeric(0)
  )
})

# L saturation flag at default macor
n_cs_default <- tryCatch(
  length((susieR::susie_get_cs(fit, Xcorr = R, coverage = COVERAGE,
                               min_abs_corr = MIN_ABS_CORR_DEFAULT)$cs) %||% list()),
  error = function(e) NA_integer_
)
l_saturated <- isTRUE(n_cs_default >= L_DEFAULT)

# Augment result list (backward compatible with summarize_finemap_results.py)
result$min_abs_corr_sweep <- sweep_rows
result$L_used              <- L_DEFAULT
result$L_saturated         <- l_saturated
result$converged           <- d2$converged
result$niter               <- d2$niter
result$elbo_final          <- d2$elbo_final
result$convergence_status  <- convergence_status
result$status              <- if (grepl("non_converged", convergence_status)) "non_converged" else "ok"
result$d1_zscore_sanity    <- d1
result$d2_convergence      <- d2
result$d3_ld_quality       <- d3
result$policy_hash         <- digest::digest(policy, algo = "sha1")

dir.create(dirname(opt$output), showWarnings = FALSE, recursive = TRUE)
write(toJSON(result, auto_unbox = TRUE, pretty = TRUE, na = "null"), file = opt$output)
