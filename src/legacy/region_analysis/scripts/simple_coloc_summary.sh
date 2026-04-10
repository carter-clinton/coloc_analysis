#!/bin/bash
# Simple script to summarize coloc results from JSON files

set -euo pipefail

PROJECT_DIR="${1:-/gpfs_common/share01/clintonlab/ckclinto/admix_map}"
COLOC_DIR="$PROJECT_DIR/results/multitrait/coloc"
OUTPUT="$PROJECT_DIR/results/multitrait/coloc_summary_new.tsv"

echo "Generating coloc summary from JSON files..."

# Header
echo -e "region\tancestry\ttrait_a\ttrait_b\tn_snps\tn_overlap\tPP.H0\tPP.H1\tPP.H2\tPP.H3\tPP.H4" > "$OUTPUT"

# Process each JSON file
for json in "$COLOC_DIR"/*.json; do
  if [[ ! -f "$json" ]]; then
    continue
  fi

  basename=$(basename "$json" .json)

  # Parse the pair_id format: region__ancestry__trait_a_vs_trait_b
  if [[ "$basename" =~ ^(.+)__([A-Z]+)__(.+)_vs_(.+)$ ]]; then
    region="${BASH_REMATCH[1]}"
    ancestry="${BASH_REMATCH[2]}"
    trait_a="${BASH_REMATCH[3]}"
    trait_b="${BASH_REMATCH[4]}"

    # Extract values from JSON using python
    python3 << PYEOF
import json
import sys

try:
    with open("$json") as f:
        data = json.load(f)

    # Get summary data
    summary = data.get("summary", {})
    n_snps = summary.get("nsnps", "NA")
    pp_h0 = summary.get("PP.H0.abf", "NA")
    pp_h1 = summary.get("PP.H1.abf", "NA")
    pp_h2 = summary.get("PP.H2.abf", "NA")
    pp_h3 = summary.get("PP.H3.abf", "NA")
    pp_h4 = summary.get("PP.H4.abf", "NA")

    # Get overlap count
    n_overlap = data.get("n_common_snps", n_snps)

    print(f"$region\t$ancestry\t$trait_a\t$trait_b\t{n_snps}\t{n_overlap}\t{pp_h0}\t{pp_h1}\t{pp_h2}\t{pp_h3}\t{pp_h4}")
except Exception as e:
    sys.stderr.write(f"Error processing $json: {e}\n")
PYEOF
  fi
done >> "$OUTPUT"

echo "Summary written to: $OUTPUT"
wc -l "$OUTPUT"

# Show top results by H4
echo ""
echo "=== Top 20 Results by PP.H4 ==="
sort -t$'\t' -k11 -rn "$OUTPUT" | head -21 | column -t

echo ""
echo "=== AFR Results with H4 > 0.5 ==="
awk -F'\t' 'NR==1 || ($2=="AFR" && $11 > 0.5)' "$OUTPUT" | sort -t$'\t' -k11 -rn | column -t
