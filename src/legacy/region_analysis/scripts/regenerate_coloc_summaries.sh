#!/bin/bash
# Regenerate coloc summaries after AFR batch jobs complete

set -euo pipefail

PROJECT_DIR="${1:-/gpfs_common/share01/clintonlab/ckclinto/admix_map}"
cd "$PROJECT_DIR"

echo "==================================================="
echo "Regenerating Coloc Summaries"
echo "==================================================="

# Activate conda environment
export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"
source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true

# Check if we need conda activation
if ! command -v python &> /dev/null; then
  echo "Activating conda environment..."
  conda activate base
fi

echo ""
echo "Step 1: Count completed coloc results..."
total_coloc=$(ls -1 results/multitrait/coloc/*.json 2>/dev/null | wc -l)
afr_coloc=$(ls -1 results/multitrait/coloc/*AFR*.json 2>/dev/null | wc -l)
echo "  Total coloc results: $total_coloc"
echo "  AFR coloc results: $afr_coloc"

echo ""
echo "Step 2: Check for summarize script..."
if [[ ! -f "scripts/summarize_coloc_results.py" ]]; then
  echo "WARNING: scripts/summarize_coloc_results.py not found"
  echo "Looking for alternative summary scripts..."
  find scripts -name "*coloc*summary*" -o -name "*summary*coloc*" 2>/dev/null
  exit 1
fi

echo ""
echo "Step 3: Regenerate coloc summary..."
if python scripts/summarize_coloc_results.py \
  --input-dir results/multitrait/coloc \
  --output results/multitrait/coloc_summary.tsv 2>/dev/null; then
  echo "  ✓ Summary generated: results/multitrait/coloc_summary.tsv"
  wc -l results/multitrait/coloc_summary.tsv
else
  echo "  ⚠ summarize_coloc_results.py failed or doesn't exist"
  echo "  Checking for alternative approaches..."

  # Try alternative: use build_coloc_h4_reports.py
  if [[ -f "scripts/build_coloc_h4_reports.py" ]]; then
    echo "  Trying build_coloc_h4_reports.py..."
    python scripts/build_coloc_h4_reports.py
  fi
fi

echo ""
echo "Step 4: Check for augment script..."
if [[ -f "scripts/augment_coloc_summary.py" ]]; then
  echo "Regenerating augmented summary with QC flags..."
  python scripts/augment_coloc_summary.py \
    --input results/multitrait/coloc_summary.tsv \
    --output results/multitrait/coloc_summary_augmented.tsv 2>/dev/null || \
  python scripts/augment_coloc_summary.py \
    results/multitrait/coloc_summary.tsv \
    results/multitrait/coloc_summary_augmented.tsv
  echo "  ✓ Augmented summary: results/multitrait/coloc_summary_augmented.tsv"
fi

echo ""
echo "Step 5: Show new AFR coloc results (H4 > 0.5)..."
if [[ -f "results/multitrait/coloc_summary_augmented.tsv" ]]; then
  echo "=== NEW AFR COLOC RESULTS (H4 > 0.5) ==="
  awk -F'\t' 'NR==1 || ($3=="AFR" && $7 > 0.5)' results/multitrait/coloc_summary_augmented.tsv | column -t | head -20
elif [[ -f "results/multitrait/coloc_summary.tsv" ]]; then
  echo "=== NEW AFR COLOC RESULTS (H4 > 0.5) ==="
  awk -F'\t' 'NR==1 || ($7 > 0.5)' results/multitrait/coloc_summary.tsv | grep -E "(region|AFR)" | column -t | head -20
fi

echo ""
echo "==================================================="
echo "Summary Regeneration Complete"
echo "==================================================="
echo ""
echo "Output files:"
echo "  - results/multitrait/coloc_summary.tsv"
echo "  - results/multitrait/coloc_summary_augmented.tsv (if available)"
echo ""
echo "To view high-confidence AFR signals:"
echo "  awk -F'\\t' 'NR==1 || (\$3==\"AFR\" && \$7 > 0.8)' results/multitrait/coloc_summary_augmented.tsv | column -t"
