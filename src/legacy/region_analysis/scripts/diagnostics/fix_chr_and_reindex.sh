#!/bin/bash
set -euo pipefail

# Add tabix and bgzip to PATH from conda environment
export PATH="/rs1/researchers/c/ckclinto/conda_envs/nyabg-tools/bin:$PATH"

PROJECT_DIR="${1:-/share/clintonlab/ckclinto/admix_map}"
HARMONIZED_DIR="$PROJECT_DIR/data_processed/sumstats_harmonized_fixed"
BACKUP_DIR="$PROJECT_DIR/data_processed/sumstats_harmonized_fixed_backup_$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

for file in "$HARMONIZED_DIR"/*.AFR.tsv.bgz; do
  [[ -f "$file" ]] || continue
  echo "Processing: $(basename "$file")"

  has_chr=$(zcat "$file" | head -1000 | awk -F'\t' 'NR==1{for(i=1;i<=NF;i++) if($i=="CHR") c=i} NR>1{print $c}' | grep -c "^chr" || true)

  if [[ "$has_chr" -gt 0 ]]; then
    echo "  Normalizing chr prefix..."
    cp "$file" "$BACKUP_DIR/"
    [[ -f "$file.tbi" ]] && cp "$file.tbi" "$BACKUP_DIR/"

    chr_col=$(zcat "$file" | head -1 | tr '\t' '\n' | nl | grep -w "CHR" | awk '{print $1}')
    zcat "$file" | awk -F'\t' -v OFS='\t' -v col="$chr_col" 'NR==1{print;next}{gsub(/^chr/,"",$col);print}' | bgzip -c > "${file}.tmp"
    mv "${file}.tmp" "$file"
  fi

  echo "  Reindexing..."
  tabix -f -s1 -b2 -e2 -S1 "$file"
done
echo "Done. Backups in: $BACKUP_DIR"
