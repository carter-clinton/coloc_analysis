#!/usr/bin/env Rscript
#==============================================================================
# Genome-Wide Colocalization Analysis
# Runs coloc for a single pair from the manifest
#==============================================================================

suppressPackageStartupMessages({
  library(data.table)
  library(coloc)
  library(optparse)
  library(jsonlite)
})

# Parse arguments
option_list <- list(
  make_option("--manifest", type="character", help="Path to manifest file"),
  make_option("--pair-id", type="character", help="Pair ID to process"),
  make_option("--output", type="character", help="Output JSON file path"),
  make_option("--min-snps", type="integer", default=50, help="Minimum overlapping SNPs")
)

opt <- parse_args(OptionParser(option_list=option_list))

# Load manifest
manifest <- fread(opt$manifest)
pair_info <- manifest[pair_id == opt$`pair-id`]

if (nrow(pair_info) == 0) {
  stop(paste("Pair not found:", opt$`pair-id`))
}

# Extract info
region <- paste0(pair_info$chr, ":", pair_info$start, "-", pair_info$end)
trait_a <- pair_info$trait_a
trait_b <- pair_info$trait_b
path_a <- pair_info$path_a
path_b <- pair_info$path_b
ancestry <- pair_info$ancestry

cat("============================================================\n")
cat("COLOCALIZATION ANALYSIS\n")
cat("============================================================\n")
cat("Pair ID:", opt$`pair-id`, "\n")
cat("Region:", region, "\n")
cat("Trait A:", trait_a, "\n")
cat("Trait B:", trait_b, "\n")
cat("Ancestry:", ancestry, "\n")
cat("\n")

# Function to load regional data via tabix
load_regional_data <- function(filepath, chr, start, end) {
  region_str <- paste0(chr, ":", start, "-", end)
  
  # Get header
  header_cmd <- paste("zcat", filepath, "| head -1")
  header <- strsplit(system(header_cmd, intern=TRUE), "\t")[[1]]
  
  # Tabix query
  tabix_cmd <- paste("tabix", filepath, region_str)
  lines <- tryCatch(
    system(tabix_cmd, intern=TRUE),
    error = function(e) character(0)
  )
  
  if (length(lines) == 0) {
    return(NULL)
  }
  
  df <- fread(text=paste(lines, collapse="\n"), header=FALSE)
  setnames(df, header)
  
  return(df)
}

# Load data
cat("Loading data...\n")
df_a <- load_regional_data(path_a, pair_info$chr, pair_info$start, pair_info$end)
df_b <- load_regional_data(path_b, pair_info$chr, pair_info$start, pair_info$end)

if (is.null(df_a) || is.null(df_b)) {
  result <- list(
    pair_id = opt$`pair-id`,
    region = region,
    trait_a = trait_a,
    trait_b = trait_b,
    ancestry = ancestry,
    status = "NO_DATA",
    n_snps = 0,
    PP.H0.abf = NA,
    PP.H1.abf = NA,
    PP.H2.abf = NA,
    PP.H3.abf = NA,
    PP.H4.abf = NA
  )
  
  jsonlite::write_json(result, opt$output, auto_unbox=TRUE, pretty=TRUE)
  cat("No data in region - saved empty result\n")
  quit(status=0)
}

cat("  Trait A:", nrow(df_a), "variants\n")
cat("  Trait B:", nrow(df_b), "variants\n")

# Create CHRPOS key for merging
df_a[, CHRPOS := paste(CHR, POS, sep=":")]
df_b[, CHRPOS := paste(CHR, POS, sep=":")]

# Merge on position
merged <- merge(df_a, df_b, by="CHRPOS", suffixes=c("_A", "_B"))
cat("  Overlapping:", nrow(merged), "variants\n")

if (nrow(merged) < opt$`min-snps`) {
  result <- list(
    pair_id = opt$`pair-id`,
    region = region,
    trait_a = trait_a,
    trait_b = trait_b,
    ancestry = ancestry,
    status = "LOW_OVERLAP",
    n_snps = nrow(merged),
    PP.H0.abf = NA,
    PP.H1.abf = NA,
    PP.H2.abf = NA,
    PP.H3.abf = NA,
    PP.H4.abf = NA
  )
  
  jsonlite::write_json(result, opt$output, auto_unbox=TRUE, pretty=TRUE)
  cat("Insufficient overlap - saved empty result\n")
  quit(status=0)
}

# Prepare coloc datasets
# For quantitative traits, we need either sdY or MAF+N to estimate it
# If no EAF available, estimate sdY from beta/SE assuming standardized phenotype

dataset_a <- list(
  beta = merged$BETA_A,
  varbeta = merged$SE_A^2,
  snp = merged$CHRPOS,
  position = merged$POS_A,
  type = "quant",
  N = median(merged$N_A, na.rm=TRUE)
)

dataset_b <- list(
  beta = merged$BETA_B,
  varbeta = merged$SE_B^2,
  snp = merged$CHRPOS,
  position = merged$POS_B,
  type = "quant",
  N = median(merged$N_B, na.rm=TRUE)
)

# Handle case/control traits first
if (trait_a %in% c("t2d", "stroke", "asthma", "hypertension")) {
  dataset_a$type <- "cc"
  if ("N_CASE_A" %in% names(merged)) {
    s <- median(merged$N_CASE_A, na.rm=TRUE) /
         (median(merged$N_CASE_A, na.rm=TRUE) + median(merged$N_CTRL_A, na.rm=TRUE))
    dataset_a$s <- s
  } else {
    dataset_a$s <- 0.5  # Assume balanced if not available
  }
} else {
  # Quantitative trait - need MAF or sdY
  if ("EAF_A" %in% names(merged)) {
    dataset_a$MAF <- pmin(merged$EAF_A, 1 - merged$EAF_A)
  } else {
    # No MAF available, estimate sdY=1 (assuming standardized phenotype)
    dataset_a$sdY <- 1
  }
}

if (trait_b %in% c("t2d", "stroke", "asthma", "hypertension")) {
  dataset_b$type <- "cc"
  if ("N_CASE_B" %in% names(merged)) {
    s <- median(merged$N_CASE_B, na.rm=TRUE) /
         (median(merged$N_CASE_B, na.rm=TRUE) + median(merged$N_CTRL_B, na.rm=TRUE))
    dataset_b$s <- s
  } else {
    dataset_b$s <- 0.5
  }
} else {
  # Quantitative trait - need MAF or sdY
  if ("EAF_B" %in% names(merged)) {
    dataset_b$MAF <- pmin(merged$EAF_B, 1 - merged$EAF_B)
  } else {
    # No MAF available, estimate sdY=1 (assuming standardized phenotype)
    dataset_b$sdY <- 1
  }
}

# Run coloc
cat("\nRunning colocalization...\n")
coloc_result <- tryCatch({
  coloc.abf(dataset_a, dataset_b)
}, error = function(e) {
  cat("Coloc error:", e$message, "\n")
  return(NULL)
})

if (is.null(coloc_result)) {
  result <- list(
    pair_id = opt$`pair-id`,
    region = region,
    trait_a = trait_a,
    trait_b = trait_b,
    ancestry = ancestry,
    status = "COLOC_ERROR",
    n_snps = nrow(merged),
    PP.H0.abf = NA,
    PP.H1.abf = NA,
    PP.H2.abf = NA,
    PP.H3.abf = NA,
    PP.H4.abf = NA
  )
  
  jsonlite::write_json(result, opt$output, auto_unbox=TRUE, pretty=TRUE)
  quit(status=0)
}

# Extract results
pp <- coloc_result$summary

# Find lead SNP (highest H4 contribution)
if (!is.null(coloc_result$results)) {
  lead_idx <- which.max(coloc_result$results$SNP.PP.H4)
  lead_snp <- coloc_result$results$snp[lead_idx]
  lead_pp_h4 <- coloc_result$results$SNP.PP.H4[lead_idx]
} else {
  lead_snp <- NA
  lead_pp_h4 <- NA
}

result <- list(
  pair_id = opt$`pair-id`,
  region = region,
  trait_a = trait_a,
  trait_b = trait_b,
  ancestry = ancestry,
  status = "SUCCESS",
  n_snps = pp["nsnps"],
  PP.H0.abf = pp["PP.H0.abf"],
  PP.H1.abf = pp["PP.H1.abf"],
  PP.H2.abf = pp["PP.H2.abf"],
  PP.H3.abf = pp["PP.H3.abf"],
  PP.H4.abf = pp["PP.H4.abf"],
  lead_snp = lead_snp,
  lead_snp_pp_h4 = lead_pp_h4
)

# Save result
jsonlite::write_json(result, opt$output, auto_unbox=TRUE, pretty=TRUE)

cat("\n============================================================\n")
cat("RESULTS\n")
cat("============================================================\n")
cat("PP.H0 (neither):", round(pp["PP.H0.abf"], 4), "\n")
cat("PP.H1 (trait A only):", round(pp["PP.H1.abf"], 4), "\n")
cat("PP.H2 (trait B only):", round(pp["PP.H2.abf"], 4), "\n")
cat("PP.H3 (both, different):", round(pp["PP.H3.abf"], 4), "\n")
cat("PP.H4 (both, shared):", round(pp["PP.H4.abf"], 4), "\n")
cat("\nSaved to:", opt$output, "\n")
