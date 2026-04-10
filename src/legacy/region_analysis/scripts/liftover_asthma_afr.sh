#!/bin/bash
#=============================================================================
# Liftover asthma.AFR from GRCh38 to GRCh37
#=============================================================================
set -euo pipefail

PROJECT_DIR="${1:-/gpfs_common/share01/clintonlab/ckclinto/admix_map}"
HARMONIZED_DIR="$PROJECT_DIR/data_processed/sumstats_harmonized_fixed"
INPUT_FILE="$HARMONIZED_DIR/asthma.AFR.tsv.bgz"
OUTPUT_FILE="$HARMONIZED_DIR/asthma.AFR.grch37.tsv.bgz"
BACKUP_FILE="$HARMONIZED_DIR/asthma.AFR.grch38_backup.tsv.bgz"
CHAIN_DIR="$PROJECT_DIR/data_raw/liftover"
CHAIN_FILE="$CHAIN_DIR/hg38ToHg19.over.chain.gz"
TMP_DIR="$PROJECT_DIR/tmp/liftover_$$"

mkdir -p "$CHAIN_DIR" "$TMP_DIR"

echo "============================================================="
echo "LIFTOVER: asthma.AFR GRCh38 → GRCh37"
echo "============================================================="

# Step 1: Download chain file if needed
if [[ ! -f "$CHAIN_FILE" ]]; then
  echo "Downloading chain file..."
  wget -q -O "$CHAIN_FILE" \
    "https://hgdownload.cse.ucsc.edu/goldenpath/hg38/liftOver/hg38ToHg19.over.chain.gz"
  echo "  Downloaded: $CHAIN_FILE"
else
  echo "Chain file exists: $CHAIN_FILE"
fi

# Step 2: Check for liftOver tool
if ! command -v liftOver &> /dev/null; then
  echo "Installing liftOver..."
  conda install -y -c bioconda ucsc-liftover || {
    echo "Downloading liftOver binary..."
    mkdir -p "$PROJECT_DIR/bin"
    wget -q -O "$PROJECT_DIR/bin/liftOver" \
      "http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/liftOver"
    chmod +x "$PROJECT_DIR/bin/liftOver"
    export PATH="$PROJECT_DIR/bin:$PATH"
  }
fi

echo ""
echo "Step 1: Converting to BED format..."
# Create BED file (chr, start, end, id)
# BED is 0-based, so start = pos - 1
zcat "$INPUT_FILE" | awk -F'\t' '
  NR==1 {
    for(i=1;i<=NF;i++) {
      if($i=="CHR") chr_col=i
      if($i=="POS") pos_col=i
    }
    next
  }
  {
    chr = $chr_col
    pos = $pos_col
    # Add chr prefix if missing (liftOver requires it)
    if (chr !~ /^chr/) chr = "chr" chr
    # BED is 0-based half-open, so for a SNP at position P: start=P-1, end=P
    print chr "\t" (pos-1) "\t" pos "\t" NR
  }
' > "$TMP_DIR/input.bed"

input_count=$(wc -l < "$TMP_DIR/input.bed")
echo "  Input variants: $input_count"

echo ""
echo "Step 2: Running liftOver..."
liftOver \
  "$TMP_DIR/input.bed" \
  "$CHAIN_FILE" \
  "$TMP_DIR/lifted.bed" \
  "$TMP_DIR/unmapped.bed"

lifted_count=$(wc -l < "$TMP_DIR/lifted.bed")
unmapped_count=$(wc -l < "$TMP_DIR/unmapped.bed" || echo 0)
echo "  Lifted: $lifted_count"
echo "  Unmapped: $unmapped_count"

echo ""
echo "Step 3: Creating position mapping..."
# Create mapping: original_line_number -> new_position
awk -F'\t' '{
  # Convert back to 1-based position
  new_pos = $3
  line_num = $4
  # Remove chr prefix for consistency with other files
  chr = $1
  gsub(/^chr/, "", chr)
  print line_num "\t" chr "\t" new_pos
}' "$TMP_DIR/lifted.bed" | sort -k1,1n > "$TMP_DIR/position_map.tsv"

echo ""
echo "Step 4: Applying liftover to sumstats..."
# Backup original
cp "$INPUT_FILE" "$BACKUP_FILE"
echo "  Backup saved: $BACKUP_FILE"

# Create lifted file with Python for reliability
export TMP_DIR INPUT_FILE
python3 << PYEOF
import gzip
import sys
import os

tmp_dir = os.environ.get('TMP_DIR')
input_file = os.environ.get('INPUT_FILE')

# Read position map
pos_map = {}
with open(f"{tmp_dir}/position_map.tsv") as f:
    for line in f:
        parts = line.strip().split("\t")
        line_num = int(parts[0])
        new_chr = parts[1]
        new_pos = int(parts[2])
        pos_map[line_num] = (new_chr, new_pos)

print(f"  Position map loaded: {len(pos_map)} entries")

# Process sumstats
with gzip.open(input_file, "rt") as fin, gzip.open(f"{tmp_dir}/lifted.tsv.gz", "wt") as fout:
    header = fin.readline().strip().split("\t")
    fout.write("\t".join(header) + "\n")

    # Find CHR and POS columns
    chr_col = header.index("CHR")
    pos_col = header.index("POS")

    kept = 0
    dropped = 0
    line_num = 2  # 1-indexed, header is line 1

    for line in fin:
        if line_num in pos_map:
            fields = line.strip().split("\t")
            new_chr, new_pos = pos_map[line_num]
            fields[chr_col] = str(new_chr)
            fields[pos_col] = str(new_pos)
            fout.write("\t".join(fields) + "\n")
            kept += 1
        else:
            dropped += 1
        line_num += 1

    print(f"  Kept: {kept}, Dropped: {dropped}")
PYEOF

echo ""
echo "Step 5: Sorting and indexing..."
# Export conda environment PATH for bgzip and tabix
export PATH="/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin:$PATH"

# Sort by CHR and POS
zcat "$TMP_DIR/lifted.tsv.gz" | \
  awk -F'\t' 'NR==1{print; next} {print | "sort -k1,1V -k2,2n"}' | \
  bgzip -c > "$OUTPUT_FILE"

# Index with tabix
tabix -f -s1 -b2 -e2 -S1 "$OUTPUT_FILE"

echo ""
echo "Step 6: Validation..."
# Check a known SNP
echo "Checking APOE rs429358 position..."
new_pos=$(zcat "$OUTPUT_FILE" | awk -F'\t' 'NR==1{for(i=1;i<=NF;i++) if($i=="POS") p=i} $p==45411941{found=1; exit} END{print found+0}')
if [[ "$new_pos" == "1" ]]; then
  echo "  ✓ Found rs429358 at GRCh37 position 45411941"
else
  echo "  ⚠ rs429358 not found at expected position - check liftover"
fi

# Compare overlap with stroke
echo ""
echo "Checking overlap with stroke.AFR (both should be GRCh37 now)..."
tabix "$OUTPUT_FILE" 19:45000000-46500000 2>/dev/null | cut -f2 | sort -n > "$TMP_DIR/asthma_pos.txt"
tabix "$HARMONIZED_DIR/stroke.AFR.tsv.bgz" 19:45000000-46500000 2>/dev/null | cut -f2 | sort -n > "$TMP_DIR/stroke_pos.txt"

asthma_count=$(wc -l < "$TMP_DIR/asthma_pos.txt")
stroke_count=$(wc -l < "$TMP_DIR/stroke_pos.txt")
overlap=$(comm -12 "$TMP_DIR/asthma_pos.txt" "$TMP_DIR/stroke_pos.txt" | wc -l)

echo "  asthma.AFR (lifted): $asthma_count variants in APOE region"
echo "  stroke.AFR: $stroke_count variants in APOE region"
echo "  Overlap: $overlap variants"

if [[ "$overlap" -gt 500 ]]; then
  echo "  ✓ Good overlap - liftover successful!"
else
  echo "  ⚠ Low overlap - investigate further"
fi

echo ""
echo "Step 7: Replace original file..."
mv "$OUTPUT_FILE" "$INPUT_FILE"
mv "${OUTPUT_FILE}.tbi" "${INPUT_FILE}.tbi"
echo "  Replaced: $INPUT_FILE"

# Cleanup
rm -rf "$TMP_DIR"

echo ""
echo "============================================================="
echo "LIFTOVER COMPLETE"
echo "============================================================="
echo "Original (GRCh38): $BACKUP_FILE"
echo "Lifted (GRCh37): $INPUT_FILE"
echo ""
echo "Next steps:"
echo "  1. Verify: bash scripts/diagnostics/check_position_alignment.sh"
echo "  2. Rerun coloc: snakemake -j 20 results/multitrait/coloc_summary.tsv --forcerun"
