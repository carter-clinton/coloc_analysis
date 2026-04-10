#!/bin/bash
set -euo pipefail

# Add tabix to PATH from conda environment
export PATH="/rs1/researchers/c/ckclinto/conda_envs/nyabg-tools/bin:$PATH"

PROJECT_DIR="${1:-/share/clintonlab/ckclinto/admix_map}"
HARMONIZED_DIR="$PROJECT_DIR/data_processed/sumstats_harmonized_fixed"
OUTPUT_DIR="$PROJECT_DIR/results/diagnostics/afr_no_overlap_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "=== 1. CHROMOSOME NAMING ===" | tee "$OUTPUT_DIR/01_chr_naming.txt"
for trait in asthma stroke t2d; do
  file="$HARMONIZED_DIR/${trait}.AFR.tsv.bgz"
  [[ -f "$file" ]] && echo "--- ${trait}.AFR ---" && zcat "$file" | awk -F'\t' 'NR==1{for(i=1;i<=NF;i++) if($i=="CHR") c=i} NR>1 && NR<=101{print $c}' | sort -u | head -5
done | tee -a "$OUTPUT_DIR/01_chr_naming.txt"

echo -e "\n=== 2. TABIX INDEX STATUS ===" | tee "$OUTPUT_DIR/02_tabix.txt"
for trait in asthma stroke t2d; do
  file="$HARMONIZED_DIR/${trait}.AFR.tsv.bgz"
  [[ -f "$file" ]] && echo "--- ${trait}.AFR ---" && ls -l "$file" "$file.tbi" 2>/dev/null && tabix -l "$file" 2>/dev/null | head -5
done | tee -a "$OUTPUT_DIR/02_tabix.txt"

echo -e "\n=== 3. TABIX vs AWK TEST (APOE_19q13) ===" | tee "$OUTPUT_DIR/03_comparison.txt"
for trait in asthma stroke t2d; do
  file="$HARMONIZED_DIR/${trait}.AFR.tsv.bgz"
  [[ -f "$file" ]] || continue
  tabix_num=$(tabix "$file" "19:45000000-46500000" 2>/dev/null | wc -l)
  tabix_chr=$(tabix "$file" "chr19:45000000-46500000" 2>/dev/null | wc -l)
  awk_count=$(zcat "$file" | awk -F'\t' 'NR==1{for(i=1;i<=NF;i++){if($i=="CHR")c=i;if($i=="POS")p=i}next}{gsub(/^chr/,"",$c);if($c==19 && $p>=45000000 && $p<=46500000)n++}END{print n+0}')
  echo "${trait}.AFR: tabix(19:...)=$tabix_num tabix(chr19:...)=$tabix_chr awk=$awk_count"
done | tee -a "$OUTPUT_DIR/03_comparison.txt"

echo -e "\nOutput: $OUTPUT_DIR"
