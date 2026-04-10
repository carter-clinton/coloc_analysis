#!/usr/bin/env Rscript
# Trace exactly what run_coloc.R sees for one AFR NO_OVERLAP pair

suppressPackageStartupMessages(library(data.table))

args <- commandArgs(trailingOnly = TRUE)
project_dir <- if (length(args) > 0) args[1] else "/share/clintonlab/ckclinto/admix_map"

# Pick a test pair: APOE_19q13__AFR__asthma_vs_stroke
region <- "APOE_19q13"
ancestry <- "AFR"
trait_a <- "asthma"
trait_b <- "stroke"
pair_id <- paste(region, ancestry, paste(trait_a, "vs", trait_b, sep="_"), sep="__")

cat("=============================================================\n")
cat("TRACING COLOC MERGE FOR:", pair_id, "\n")
cat("=============================================================\n\n")

# Get region coordinates from regions_tiled.csv
regions <- fread(file.path(project_dir, "config/regions_tiled.csv"))
cat("Regions file columns:", paste(names(regions), collapse=", "), "\n\n")

# Find matching region
region_match <- regions[grepl(region, region_id, ignore.case=TRUE)]
cat("Matching regions for '", region, "':\n", sep="")
print(region_match[, .(region_id, chr, start, end)])

if (nrow(region_match) == 0) {
  stop("No matching region found!")
}

# Use first match
r <- region_match[1]
chrom <- r$chr
start_pos <- r$start
end_pos <- r$end
cat("\nUsing: chr", chrom, ":", start_pos, "-", end_pos, "\n\n")

# Load sumstats files
file_a <- file.path(project_dir, "data_processed/sumstats_harmonized_fixed", paste0(trait_a, ".", ancestry, ".tsv.bgz"))
file_b <- file.path(project_dir, "data_processed/sumstats_harmonized_fixed", paste0(trait_b, ".", ancestry, ".tsv.bgz"))

cat("File A:", file_a, "\n")
cat("File B:", file_b, "\n\n")

# Method 1: Tabix query (what run_coloc.R likely does)
cat("=== METHOD 1: TABIX QUERY ===\n")
region_str <- sprintf("%s:%d-%d", chrom, start_pos, end_pos)
cat("Query string:", region_str, "\n")

tabix_cmd_a <- sprintf("tabix %s %s", file_a, region_str)
tabix_cmd_b <- sprintf("tabix %s %s", file_b, region_str)

cat("Command A:", tabix_cmd_a, "\n")
cat("Command B:", tabix_cmd_b, "\n\n")

# Get headers
header_a <- fread(cmd = sprintf("zcat %s | head -1", file_a), header = FALSE)
header_b <- fread(cmd = sprintf("zcat %s | head -1", file_b), header = FALSE)
cols_a <- as.character(header_a[1,])
cols_b <- as.character(header_b[1,])

cat("Columns in file A:", paste(cols_a, collapse=", "), "\n")
cat("Columns in file B:", paste(cols_b, collapse=", "), "\n\n")

# Load via tabix
df_a <- tryCatch({
  fread(cmd = tabix_cmd_a, header = FALSE, col.names = cols_a)
}, error = function(e) {
  cat("ERROR loading A:", e$message, "\n")
  data.table()
})

df_b <- tryCatch({
  fread(cmd = tabix_cmd_b, header = FALSE, col.names = cols_b)
}, error = function(e) {
  cat("ERROR loading B:", e$message, "\n")
  data.table()
})

cat("Rows loaded via tabix:\n")
cat("  File A:", nrow(df_a), "\n")
cat("  File B:", nrow(df_b), "\n\n")

if (nrow(df_a) == 0 || nrow(df_b) == 0) {
  cat("WARNING: Tabix returned 0 rows for one or both files!\n")
  cat("Trying with 'chr' prefix...\n")

  region_str_chr <- sprintf("chr%s:%d-%d", chrom, start_pos, end_pos)
  tabix_cmd_a_chr <- sprintf("tabix %s %s", file_a, region_str_chr)
  tabix_cmd_b_chr <- sprintf("tabix %s %s", file_b, region_str_chr)

  df_a_chr <- tryCatch(fread(cmd = tabix_cmd_a_chr, header = FALSE, col.names = cols_a), error = function(e) data.table())
  df_b_chr <- tryCatch(fread(cmd = tabix_cmd_b_chr, header = FALSE, col.names = cols_b), error = function(e) data.table())

  cat("With 'chr' prefix: A=", nrow(df_a_chr), ", B=", nrow(df_b_chr), "\n\n")

  if (nrow(df_a_chr) > nrow(df_a)) df_a <- df_a_chr
  if (nrow(df_b_chr) > nrow(df_b)) df_b <- df_b_chr
}

# Check data types
cat("=== DATA TYPE CHECK ===\n")
if (nrow(df_a) > 0) {
  cat("File A - CHR type:", class(df_a$CHR), ", sample:", head(df_a$CHR, 3), "\n")
  cat("File A - POS type:", class(df_a$POS), ", sample:", head(df_a$POS, 3), "\n")
}
if (nrow(df_b) > 0) {
  cat("File B - CHR type:", class(df_b$CHR), ", sample:", head(df_b$CHR, 3), "\n")
  cat("File B - POS type:", class(df_b$POS), ", sample:", head(df_b$POS, 3), "\n")
}
cat("\n")

# Build CHRPOS key (what run_coloc.R should do)
cat("=== MERGE KEY CONSTRUCTION ===\n")
if (nrow(df_a) > 0 && nrow(df_b) > 0) {
  # Normalize CHR (remove 'chr' prefix if present)
  df_a[, CHR_clean := gsub("^chr", "", as.character(CHR))]
  df_b[, CHR_clean := gsub("^chr", "", as.character(CHR))]

  # Build CHRPOS key
  df_a[, CHRPOS := paste(CHR_clean, POS, sep = ":")]
  df_b[, CHRPOS := paste(CHR_clean, POS, sep = ":")]

  cat("Sample CHRPOS keys from A:", head(df_a$CHRPOS, 5), "\n")
  cat("Sample CHRPOS keys from B:", head(df_b$CHRPOS, 5), "\n\n")

  # Check overlap
  chrpos_a <- unique(df_a$CHRPOS)
  chrpos_b <- unique(df_b$CHRPOS)
  overlap <- intersect(chrpos_a, chrpos_b)

  cat("Unique CHRPOS in A:", length(chrpos_a), "\n")
  cat("Unique CHRPOS in B:", length(chrpos_b), "\n")
  cat("CHRPOS overlap:", length(overlap), "\n\n")

  # Test merge
  cat("=== MERGE TEST ===\n")
  merged <- merge(df_a, df_b, by = "CHRPOS", suffixes = c("_A", "_B"))
  cat("Merged rows:", nrow(merged), "\n")

  if (nrow(merged) > 0) {
    cat("\nFirst 5 merged rows:\n")
    print(head(merged[, .(CHRPOS, CHR_A, POS_A, BETA_A = get("BETA_A"), BETA_B = get("BETA_B"))], 5))
  }

  # Check for SNP_ID column and test that merge
  if ("SNP_ID" %in% cols_a && "SNP_ID" %in% cols_b) {
    cat("\n=== SNP_ID MERGE TEST ===\n")
    snp_a <- unique(df_a$SNP_ID)
    snp_b <- unique(df_b$SNP_ID)
    snp_overlap <- intersect(snp_a, snp_b)
    cat("SNP_ID overlap:", length(snp_overlap), "\n")
    cat("Sample SNP_IDs A:", head(snp_a, 3), "\n")
    cat("Sample SNP_IDs B:", head(snp_b, 3), "\n")
  }
} else {
  cat("Cannot test merge - one or both dataframes empty\n")
}

cat("\n=============================================================\n")
cat("SUMMARY\n")
cat("=============================================================\n")
cat("If tabix returned data but merge shows 0 overlap, check:\n")
cat("  1. CHR column format mismatch\n")
cat("  2. POS column type mismatch (character vs integer)\n")
cat("  3. Different position encoding (0-based vs 1-based)\n")
cat("If tabix returned 0 rows, check:\n")
cat("  1. Region coordinates passed to run_coloc.R\n")
cat("  2. Chromosome naming in tabix query\n")
