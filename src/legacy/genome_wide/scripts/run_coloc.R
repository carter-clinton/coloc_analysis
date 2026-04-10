#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(optparse)
  library(data.table)
  library(jsonlite)
  library(coloc)
})

option_list <- list(
  make_option("--manifest", type = "character", help = "Coloc manifest TSV"),
  make_option("--pair-id", dest = "pair_id", type = "character", help = "Pair identifier to run"),
  make_option("--output", type = "character", help = "Output JSON path"),
  make_option("--ref-fasta", dest = "ref_fasta", type = "character", default = "",
              help = "Optional GRCh37/hg19 reference FASTA for bcftools norm")
)
opt <- parse_args(OptionParser(option_list = option_list))
if (is.null(opt$manifest) || is.null(opt$pair_id) || is.null(opt$output)) {
  stop("--manifest, --pair-id, and --output are required", call. = FALSE)
}

read_manifest <- function(path) {
  df <- fread(path, sep = "\t", data.table = FALSE)
  if (!"pair_id" %in% names(df)) stop("Manifest missing 'pair_id' column")
  df
}

read_sumstats <- function(path) {
  if (grepl("\\.(bgz|gz)$", path, ignore.case = TRUE)) {
    fread(cmd = sprintf("gunzip -c %s", shQuote(path)), sep = "\t")
  } else {
    fread(path, sep = "\t")
  }
}

read_region_tabix <- function(path, chr, start, end) {
  tabix_bin <- Sys.which("tabix")
  if (tabix_bin == "") {
    return(data.table())
  }
  region <- sprintf("%s:%d-%d", chr, start, end)
  cmd <- sprintf("%s -h %s %s", shQuote(tabix_bin), shQuote(path), region)
  dt <- tryCatch(
    fread(cmd = cmd, sep = "\t"),
    error = function(e) data.table()
  )
  dt
}

find_effect_columns <- function(cols) {
  effect_candidates <- c("EA","EFFECT_ALLELE","A1","ALLELE1","EFF_ALLELE","EFFECT","ALT","ALT_ALLELE")
  other_candidates <- c("OA","OTHER_ALLELE","A2","ALLELE2","OTHER","REF","REF_ALLELE")
  effect <- effect_candidates[effect_candidates %in% cols]
  other <- other_candidates[other_candidates %in% cols]
  list(
    ea = if (length(effect) > 0) effect[1] else NA_character_,
    oa = if (length(other) > 0) other[1] else NA_character_
  )
}

add_effect_alleles <- function(dt) {
  cols <- names(dt)
  found <- find_effect_columns(cols)
  if (!is.na(found$ea)) {
    dt[, EA := get(found$ea)]
  } else if ("ALT" %in% cols) {
    dt[, EA := ALT]
  } else {
    dt[, EA := NA_character_]
  }
  if (!is.na(found$oa)) {
    dt[, OA := get(found$oa)]
  } else if ("REF" %in% cols) {
    dt[, OA := REF]
  } else {
    dt[, OA := NA_character_]
  }
  dt
}

normalize_sumstats <- function(path, chr, start, end, ref_fasta = "") {
  dt <- read_region_tabix(path, chr, start, end)
  if (nrow(dt) == 0 || !"CHR" %in% names(dt) || !"POS" %in% names(dt)) {
    # fallback to full read if tabix unavailable or returned malformed output
    dt <- read_sumstats(path)
  }
  # Ensure CHR/POS exist for windowing and overlap.
  if (!"CHR" %in% names(dt) || !"POS" %in% names(dt)) {
    stop(sprintf("Sumstats %s missing CHR/POS columns", path))
  }
  dt[, CHR := gsub("^chr", "", CHR, ignore.case = TRUE)]
  dt[, CHR := as.character(CHR)]
  dt[, POS := as.numeric(POS)]
  dt <- dt[CHR == chr & POS >= start & POS <= end]
  if (nrow(dt) == 0) {
    return(dt)
  }
  if (!"SNP_ID" %in% names(dt)) {
    candidate_cols <- c("snp_id", "SNP", "snp", "RSID", "rsid", "MarkerName", "markername", "ID", "id")
    found <- candidate_cols[candidate_cols %in% names(dt)]
    if (length(found) > 0) {
      dt[, SNP_ID := get(found[1])]
    } else {
      dt[, SNP_ID := paste0(CHR, ":", POS)]
    }
  }
  dt <- add_effect_alleles(dt)
  if (!"REF" %in% names(dt)) dt[, REF := NA_character_]
  if (!"ALT" %in% names(dt)) dt[, ALT := NA_character_]
  dt
}

build_dataset <- function(df, prefix) {
  beta_col <- paste0("BETA_", prefix)
  se_col <- paste0("SE_", prefix)
  n_col <- paste0("N_", prefix)
  maf_col <- paste0("EAF_", prefix)

  beta <- suppressWarnings(as.numeric(df[[beta_col]]))
  se <- suppressWarnings(as.numeric(df[[se_col]]))
  varbeta <- se^2

  snp <- df$SNP_ID
  if (is.null(snp) || all(is.na(snp))) {
    if (prefix == "A" && all(c("CHR_A", "POS_A") %in% names(df))) {
      snp <- paste0(df$CHR_A, ":", df$POS_A)
    } else if (prefix == "B" && all(c("CHR_B", "POS_B") %in% names(df))) {
      snp <- paste0(df$CHR_B, ":", df$POS_B)
    } else {
      snp <- paste0(seq_len(nrow(df)))
    }
  }

  dataset <- list(
    beta = beta,
    varbeta = varbeta,
    snp = snp,
    type = "quant",
    sdY = 1
  )

  if (n_col %in% names(df)) {
    nvec <- suppressWarnings(as.numeric(df[[n_col]]))
    if (length(nvec) == length(beta) && all(!is.na(nvec))) {
      dataset$N <- nvec
    } else if (length(nvec) > 1) {
      dataset$N <- median(nvec, na.rm = TRUE)
    }
  }

  if (maf_col %in% names(df)) {
    maf_vec <- suppressWarnings(as.numeric(df[[maf_col]]))
    if (length(maf_vec) == length(beta) &&
        all(!is.na(maf_vec)) &&
        all(maf_vec > 0 & maf_vec < 1)) {
      dataset$MAF <- maf_vec
    }
  }
  dataset
}

manifest <- read_manifest(opt$manifest)
row <- manifest[manifest$pair_id == opt$pair_id, , drop = FALSE]
if (nrow(row) != 1) {
  stop(sprintf("pair_id %s not found in manifest", opt$pair_id))
}
chr <- gsub("^chr", "", as.character(row$chr[1]), ignore.case = TRUE)
region_start <- as.numeric(row$start[1])
region_end <- as.numeric(row$end[1])

ss_a <- normalize_sumstats(row$path_a[1], chr, region_start, region_end, opt$ref_fasta)
ss_b <- normalize_sumstats(row$path_b[1], chr, region_start, region_end, opt$ref_fasta)
if (nrow(ss_a) == 0 || nrow(ss_b) == 0) {
  stop("No variants found inside region window for one of the traits")
}
keep_cols <- c("SNP_ID", "CHR", "POS", "REF", "ALT", "EA", "OA", "BETA", "SE", "N", "EAF")
allele_cols <- c("SNP_ID", "CHR", "REF", "ALT", "EA", "OA")
for (col in keep_cols) {
  if (!col %in% names(ss_a)) {
    ss_a[[col]] <- if (col %in% allele_cols) NA_character_ else NA_real_
  }
  if (!col %in% names(ss_b)) {
    ss_b[[col]] <- if (col %in% allele_cols) NA_character_ else NA_real_
  }
}
setnames(ss_a, keep_cols[-1], paste0(keep_cols[-1], "_A"))
setnames(ss_b, keep_cols[-1], paste0(keep_cols[-1], "_B"))

ss_a[, CHR_A := as.character(CHR_A)]
ss_b[, CHR_B := as.character(CHR_B)]
ss_a[, POS_A := as.numeric(POS_A)]
ss_b[, POS_B := as.numeric(POS_B)]
ss_a[, CHRPOS_A := ifelse(!is.na(CHR_A) & !is.na(POS_A),
                          paste0(CHR_A, ":", round(POS_A)),
                          NA_character_)]
ss_b[, CHRPOS_B := ifelse(!is.na(CHR_B) & !is.na(POS_B),
                          paste0(CHR_B, ":", round(POS_B)),
                          NA_character_)]

cols_a <- c("SNP_ID", "CHR_A", "POS_A", paste0(keep_cols[-1], "_A"))
cols_b <- c("SNP_ID", "CHR_B", "POS_B", paste0(keep_cols[-1], "_B"))
cols_a <- unique(cols_a[cols_a %in% names(ss_a)])
cols_b <- unique(cols_b[cols_b %in% names(ss_b)])

merged <- merge(
  ss_a[, ..cols_a],
  ss_b[, ..cols_b],
  by.x = c("CHR_A", "POS_A"),
  by.y = c("CHR_B", "POS_B")
)
merged <- merged[complete.cases(merged[, .(BETA_A, SE_A, BETA_B, SE_B)])]
n_merge_chrpos <- nrow(merged)

comp_base <- function(x) chartr("ACGT", "TGCA", x)

reconcile_effect_alleles <- function(dt) {
  dt <- as.data.table(dt)
  counts <- list(
    n_match = 0L,
    n_swap = 0L,
    n_strand_match = 0L,
    n_strand_swap = 0L,
    n_ambiguous_rescued = 0L,
    n_other_dropped = 0L
  )
  if (nrow(dt) == 0) {
    return(list(dt = dt, counts = counts))
  }
  # Normalize allele columns (effect alleles preferred).
  for (col in c("EA_A","OA_A","EA_B","OA_B","REF_A","ALT_A","REF_B","ALT_B")) {
    if (col %in% names(dt)) {
      dt[, (col) := toupper(as.character(get(col)))]
    }
  }

  ea_a <- dt$EA_A; oa_a <- dt$OA_A; ea_b <- dt$EA_B; oa_b <- dt$OA_B
  is_snp <- nchar(ea_a)==1 & nchar(oa_a)==1 & nchar(ea_b)==1 & nchar(oa_b)==1
  match <- ea_a == ea_b & oa_a == oa_b
  swap <- ea_a == oa_b & oa_a == ea_b
  strand_match <- is_snp & comp_base(ea_b) == ea_a & comp_base(oa_b) == oa_a
  strand_swap <- is_snp & comp_base(ea_b) == oa_a & comp_base(oa_b) == ea_a

  # Strand-ambiguous SNPs: A/T or C/G
  ambig <- is_snp & ((ea_a %in% c("A","T") & oa_a %in% c("A","T")) |
                     (ea_a %in% c("C","G") & oa_a %in% c("C","G")))

  rescue_match <- rep(FALSE, nrow(dt))
  rescue_swap <- rep(FALSE, nrow(dt))
  if ("EAF_A" %in% names(dt) && "EAF_B" %in% names(dt)) {
    eaf_a <- dt$EAF_A
    eaf_b <- dt$EAF_B
    ok <- ambig & !is.na(eaf_a) & !is.na(eaf_b)
    rescue_match[ok] <- abs(eaf_a[ok] - eaf_b[ok]) < 0.1
    rescue_swap[ok] <- abs(eaf_a[ok] - (1 - eaf_b[ok])) < 0.1
  }

  # For ambiguous SNPs, override strand classifications with rescue decisions.
  ambig_override <- ambig & (strand_match | strand_swap)
  strand_match[ambig_override] <- FALSE
  strand_swap[ambig_override] <- FALSE

  keep <- match | swap | strand_match | strand_swap | rescue_match | rescue_swap
  counts$n_match <- sum(match, na.rm = TRUE)
  counts$n_swap <- sum(swap, na.rm = TRUE)
  counts$n_strand_match <- sum(strand_match, na.rm = TRUE)
  counts$n_strand_swap <- sum(strand_swap, na.rm = TRUE)
  counts$n_ambiguous_rescued <- sum(rescue_match | rescue_swap, na.rm = TRUE)
  counts$n_other_dropped <- sum(!keep, na.rm = TRUE)

  dt_keep <- dt[keep]
  flip_mask <- swap | strand_swap | rescue_swap
  if (any(flip_mask)) {
    dt_keep[flip_mask[keep], BETA_B := -1 * BETA_B]
    if ("EAF_B" %in% names(dt_keep)) {
      dt_keep[flip_mask[keep], EAF_B := ifelse(!is.na(EAF_B), 1 - EAF_B, EAF_B)]
    }
  }

  list(dt = dt_keep, counts = counts)
}

dedup_by_chrpos <- function(dt) {
  dt <- as.data.table(dt)
  if (nrow(dt) == 0 || !"CHR_A" %in% names(dt) || !"POS_A" %in% names(dt)) {
    return(dt)
  }
  key <- paste0(dt$CHR_A, ":", dt$POS_A)
  if (!any(duplicated(key))) {
    return(dt)
  }
  p_from_beta <- function(beta, se) {
    z <- beta / se
    2 * pnorm(-abs(z))
  }
  dt[, P_A := p_from_beta(BETA_A, SE_A)]
  dt[, P_B := p_from_beta(BETA_B, SE_B)]
  setorder(dt, P_A, P_B)
  dt <- dt[!duplicated(key)]
  dt[, c("P_A", "P_B") := NULL]
  dt
}

recon <- reconcile_effect_alleles(merged)
merged <- recon$dt
counts <- recon$counts
merged <- dedup_by_chrpos(merged)

# Ensure numeric columns and drop any rows with missing beta/se after coercion.
for (col in c("BETA_A","SE_A","BETA_B","SE_B","EAF_A","EAF_B","N_A","N_B")) {
  if (col %in% names(merged)) {
    merged[, (col) := suppressWarnings(as.numeric(get(col)))]
  }
}
merged <- merged[complete.cases(merged[, .(BETA_A, SE_A, BETA_B, SE_B)])]

# Enforce a stable SNP key for downstream coloc.
if (all(c("CHR_A","POS_A") %in% names(merged))) {
  merged[, SNP_ID := paste0(CHR_A, ":", POS_A)]
}

if (nrow(merged) < 5) {
  warning(sprintf("Insufficient overlapping SNPs (%d) for %s", nrow(merged), opt$pair_id))
}

if (n_merge_chrpos == 0) {
  placeholder <- list(
    base_region = row$base_region[1],
    ancestry = row$ancestry[1],
    trait_a = row$trait_a[1],
    trait_b = row$trait_b[1],
    chr = chr,
    start = region_start,
    end = region_end,
    n_common_snps = 0,
    n_merge_chrpos = 0,
    summary = list(error = "no_overlap_chrpos"),
    diagnostics = list(
      path_a = row$path_a[1],
      path_b = row$path_b[1],
      issue = "no_overlap_chrpos",
      n_a_region = nrow(ss_a),
      n_b_region = nrow(ss_b),
      n_merge_chrpos = n_merge_chrpos,
      n_match = counts$n_match,
      n_swap = counts$n_swap,
      n_strand_match = counts$n_strand_match,
      n_strand_swap = counts$n_strand_swap,
      n_ambiguous_rescued = counts$n_ambiguous_rescued,
      n_other_dropped = counts$n_other_dropped,
      n_final = nrow(merged)
    ),
    top_snps = data.frame()
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(placeholder, opt$output, auto_unbox = TRUE, pretty = TRUE)
  quit(save = "no", status = 0)
}

# If CHR:POS overlap exists but nothing survives allele reconciliation, emit mismatch report.
if (n_merge_chrpos > 0 && nrow(merged) == 0) {
  mismatch_dir <- "results/multitrait/coloc_mismatch"
  dir.create(mismatch_dir, recursive = TRUE, showWarnings = FALSE)
  mismatch_path <- file.path(mismatch_dir, paste0(opt$pair_id, ".tsv"))
  # Reconstruct diagnostics table from original merge for debugging.
  diag_dt <- as.data.table(merged)
  # If merged is empty, fall back to raw merged before reconciliation.
  diag_dt <- as.data.table(merge(
    ss_a[, ..cols_a],
    ss_b[, ..cols_b],
    by.x = c("CHR_A", "POS_A"),
    by.y = c("CHR_B", "POS_B")
  ))
  if (nrow(diag_dt) > 0) {
    diag_dt[, EA_A := toupper(as.character(EA_A))]
    diag_dt[, OA_A := toupper(as.character(OA_A))]
    diag_dt[, EA_B := toupper(as.character(EA_B))]
    diag_dt[, OA_B := toupper(as.character(OA_B))]
    diag_dt[, REF_A := toupper(as.character(REF_A))]
    diag_dt[, ALT_A := toupper(as.character(ALT_A))]
    diag_dt[, REF_B := toupper(as.character(REF_B))]
    diag_dt[, ALT_B := toupper(as.character(ALT_B))]
    diag_dt <- diag_dt[1:min(200, nrow(diag_dt))]
    fwrite(diag_dt, mismatch_path, sep = "\t")
  }
  placeholder <- list(
    base_region = row$base_region[1],
    ancestry = row$ancestry[1],
    trait_a = row$trait_a[1],
    trait_b = row$trait_b[1],
    chr = chr,
    start = region_start,
    end = region_end,
    n_common_snps = 0,
    n_merge_chrpos = n_merge_chrpos,
    summary = list(error = "allele_mismatch_after_norm"),
    diagnostics = list(
      path_a = row$path_a[1],
      path_b = row$path_b[1],
      issue = "allele_mismatch_after_norm",
      n_a_region = nrow(ss_a),
      n_b_region = nrow(ss_b),
      n_merge_chrpos = n_merge_chrpos,
      n_match = counts$n_match,
      n_swap = counts$n_swap,
      n_strand_match = counts$n_strand_match,
      n_strand_swap = counts$n_strand_swap,
      n_ambiguous_rescued = counts$n_ambiguous_rescued,
      n_other_dropped = counts$n_other_dropped,
      n_final = nrow(merged)
    ),
    top_snps = data.frame(),
    mismatch_report = mismatch_path
  )
  dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
  write_json(placeholder, opt$output, auto_unbox = TRUE, pretty = TRUE)
  quit(save = "no", status = 0)
}

dataset1 <- build_dataset(merged, "A")
dataset2 <- build_dataset(merged, "B")
res <- coloc.abf(dataset1 = dataset1, dataset2 = dataset2)
summary_list <- as.list(res$summary)

best_snps <- data.frame()
if (!is.null(res$results)) {
  ord <- order(-res$results$SNP.PP.H4, na.last = TRUE)
  best_snps <- res$results[ord, ]
  if (nrow(best_snps) > 20) {
    best_snps <- best_snps[1:20, ]
  }
}
output <- list(
  base_region = row$base_region[1],
  ancestry = row$ancestry[1],
  trait_a = row$trait_a[1],
  trait_b = row$trait_b[1],
  chr = chr,
  start = region_start,
  end = region_end,
  n_common_snps = nrow(merged),
  n_merge_chrpos = n_merge_chrpos,
  summary = summary_list,
  diagnostics = list(
    path_a = row$path_a[1],
    path_b = row$path_b[1],
    n_a_region = nrow(ss_a),
    n_b_region = nrow(ss_b),
    n_merge_chrpos = n_merge_chrpos,
    n_match = counts$n_match,
    n_swap = counts$n_swap,
    n_strand_match = counts$n_strand_match,
    n_strand_swap = counts$n_strand_swap,
    n_ambiguous_rescued = counts$n_ambiguous_rescued,
    n_other_dropped = counts$n_other_dropped,
    n_final = nrow(merged)
  ),
  top_snps = best_snps
)
dir.create(dirname(opt$output), recursive = TRUE, showWarnings = FALSE)
write_json(output, opt$output, auto_unbox = TRUE, pretty = TRUE)
