#!/bin/bash
#==============================================================================
# Rerun failed colocalization jobs
# Run this after the initial batch completes
#==============================================================================

GENOME_WIDE_DIR="/share/clintonlab/ckclinto/admixmap/genome_wide"
cd "$GENOME_WIDE_DIR"

echo "============================================================"
echo "RERUN FAILED JOBS"
echo "============================================================"
echo "Time: $(date)"
echo ""

# Count current status
n_total=$(wc -l < config/coloc_pair_ids.txt)
n_complete=$(ls results/coloc/*.json 2>/dev/null | wc -l)
n_success=$(grep -l '"status": "SUCCESS"' results/coloc/*.json 2>/dev/null | wc -l)
n_failed=$((n_complete - n_success))
n_missing=$((n_total - n_complete))

echo "Total pairs: $n_total"
echo "Completed: $n_complete"
echo "  - Successful: $n_success"
echo "  - Failed: $n_failed"
echo "Missing: $n_missing"
echo ""

# Find failed jobs (COLOC_ERROR or LOW_OVERLAP)
echo "Finding failed results..."
grep -l '"status": "COLOC_ERROR"\|"status": "NO_DATA"' results/coloc/*.json 2>/dev/null | \
  xargs -I{} basename {} .json > tmp/failed_pairs.txt

# Find missing pairs (no result file)
comm -23 <(sort config/coloc_pair_ids.txt) \
         <(ls results/coloc/*.json 2>/dev/null | xargs -n1 basename | sed 's/.json//' | sort) \
         > tmp/missing_pairs.txt

# Combine failed and missing
cat tmp/failed_pairs.txt tmp/missing_pairs.txt | sort | uniq > tmp/rerun_pairs.txt
n_rerun=$(wc -l < tmp/rerun_pairs.txt)

echo "Pairs to rerun: $n_rerun"
echo ""

if [[ $n_rerun -eq 0 ]]; then
  echo "No jobs need rerunning!"
  exit 0
fi

# Remove failed result files so they can be regenerated
echo "Removing failed result files..."
while read pair_id; do
  rm -f "results/coloc/${pair_id}.json" 2>/dev/null
done < tmp/failed_pairs.txt

# Create rerun submission script
echo "Creating rerun submission script..."

n_lines=$(wc -l < tmp/rerun_pairs.txt)

cat > scripts/submit_rerun.sh << EOF
#!/bin/bash
#BSUB -J gw_coloc_rerun[1-${n_lines}]
#BSUB -o logs/rerun_%I.out
#BSUB -e logs/rerun_%I.err
#BSUB -n 1
#BSUB -R "rusage[mem=4GB]"
#BSUB -W 0:30
#BSUB -q short

cd $GENOME_WIDE_DIR
source ~/.bashrc
export PATH="/share/clintonlab/ckclinto/admixmap/genome_wide/bin/bin:\$PATH"
conda activate /gpfs_common/share01/clintonlab/ckclinto/admix_map/.conda/admix_map_r_hyprcoloc 2>/dev/null || true

PAIR_ID=\$(sed -n "\${LSB_JOBINDEX}p" tmp/rerun_pairs.txt)
if [[ -z "\$PAIR_ID" ]]; then
  exit 0
fi

OUTPUT_FILE="results/coloc/\${PAIR_ID}.json"
if [[ -f "\$OUTPUT_FILE" ]]; then
  exit 0
fi

echo "Rerunning: \$PAIR_ID"
Rscript scripts/run_coloc_genomewide.R \
  --manifest config/genomewide_coloc_manifest.tsv \
  --pair-id "\$PAIR_ID" \
  --output "\$OUTPUT_FILE"
EOF

echo ""
echo "To submit rerun jobs:"
echo "  bsub < scripts/submit_rerun.sh"
echo ""

# Optionally submit automatically
if [[ "$1" == "--submit" ]]; then
  echo "Submitting rerun jobs..."
  bsub < scripts/submit_rerun.sh
fi

echo "============================================================"
