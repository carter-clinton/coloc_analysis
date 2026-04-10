#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(susieR)
  library(jsonlite)
  library(Matrix)
})

`%||%` <- function(x, y) {
  if (!is.null(x)) x else y
}

MIN_LD_OVERLAP <- as.integer(Sys.getenv("SUSIE_MIN_LD_OVERLAP", "50"))
MIN_LD_COVERAGE <- as.numeric(Sys.getenv("SUSIE_MIN_LD_COVERAGE", "0.5"))
MIN_LD_MIN_USE <- as.integer(Sys.getenv("SUSIE_MIN_LD_MIN_USE", "10"))

safe_region_id <- function(region_id) {
  gsub("[^A-Za-z0-9_]", "_", region_id)
}

load_ld_matrix <- function(ld_dir, ancestry, region_id, subset) {
  if (is.null(ld_dir) || ld_dir == "" || !file.exists(ld_dir)) {
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
  candidates <- unique(c(
    file.path(ld_dir, ancestry, paste0(region_id, ".rds")),
    file.path(ld_dir, ancestry, paste0(safe_id, ".rds"))
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
  make_option("--variant-list", type = "character", help = "Optional TSV restricting variants (CHR,POS,REF,ALT)"),
  make_option("--credible-set", type = "double", default = 0.95, help = "Credible set probability"),
  make_option("--output", type = "character", help = "Output JSON path")
)

opt <- parse_args(OptionParser(option_list = option_list))
SUSIE_MAX_VARIANTS <- as.integer(Sys.getenv("SUSIE_MAX_VARIANTS", "6000"))

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
  quit(status = 0)
}

attempt <- 1
repeat {
  ld_result <- load_ld_matrix(opt$`ld-dir`, opt$ancestry, opt$region, subset)
  ld_overlap <- ld_result$overlap %||% 0
  if (ld_overlap == 0 && used_variant_catalog && attempt == 1) {
    message("No LD overlap after applying variant catalog filter; retrying without catalog restriction.")
    subset <- copy(subset_base)
    used_variant_catalog <- FALSE
    attempt <- attempt + 1
    next
  }
  break
}

if (!is.null(ld_result$subset_idx)) {
  subset <- subset[ld_result$subset_idx]
}
subset[, z := BETA / SE]
mean_n <- suppressWarnings(mean(as.numeric(subset$N), na.rm = TRUE))
if (is.nan(mean_n) || is.infinite(mean_n)) {
  mean_n <- NA
}
run_susie <- function(R_mat) {
  if (is.na(mean_n)) {
    susie_rss(z = subset$z, R = R_mat, L = min(10, nrow(subset)), coverage = opt$`credible-set`)
  } else {
    susie_rss(z = subset$z, R = R_mat, L = min(10, nrow(subset)), coverage = opt$`credible-set`, n = mean_n)
  }
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
regularize_ld <- function(R_mat, eps = 1e-6) {
  diag(R_mat) <- diag(R_mat) + eps
  (R_mat + t(R_mat)) / 2
}

fit <- tryCatch(
  run_susie(R),
  error = function(err) {
    message(sprintf(
      "susie_rss failed for %s (%s): %s. Trying regularized LD.",
      opt$region, opt$ancestry, err$message
    ))
    R_reg <- regularize_ld(R, eps = 1e-4)
    tryCatch(
      run_susie(R_reg),
      error = function(err2) {
        message(sprintf(
          "Regularized LD also failed for %s (%s): %s. Falling back to identity.",
          opt$region, opt$ancestry, err2$message
        ))
        ld_status <<- paste(ld_status, "fallback_identity", sep = ";")
        ld_source <<- "identity_fallback"
        run_susie(diag(nrow(subset)))
      }
    )
  }
)
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
    ld_status = ld_status,
    ld_overlap = ld_overlap,
    ld_overlap_fraction = ld_overlap_fraction,
    status = "success",
    variant_catalog_path = opt$`variant-list`,
    variant_catalog_attempted = variant_catalog_attempted,
    variant_catalog_used = used_variant_catalog,
    variant_catalog_fallback = variant_catalog_fallback,
    credible_sets = credible_sets,
    pip = fit$pip[fit$pip > 0]
)

dir.create(dirname(opt$output), showWarnings = FALSE, recursive = TRUE)
write(toJSON(result, auto_unbox = TRUE, pretty = TRUE), file = opt$output)
