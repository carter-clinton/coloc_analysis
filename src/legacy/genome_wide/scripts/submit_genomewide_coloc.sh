#!/bin/bash
#BSUB -J gw_coloc[1-7150]
#BSUB -o logs/coloc_%I.out
#BSUB -e logs/coloc_%I.err
#BSUB -n 1
#BSUB -R "rusage[mem=4GB]"
#BSUB -W 0:30
#BSUB -q short

# Change to project directory
cd /share/clintonlab/ckclinto/admixmap/genome_wide

# Activate conda environment
source ~/.bashrc
conda activate /gpfs_common/share01/clintonlab/ckclinto/admix_map/.conda/admix_map_r_hyprcoloc 2>/dev/null || conda activate la_multitrait_r 2>/dev/null || true

# Get pair ID for this job
PAIR_ID=$(sed -n "${LSB_JOBINDEX}p" config/coloc_pair_ids.txt)

if [[ -z "$PAIR_ID" ]]; then
  echo "No pair ID for index $LSB_JOBINDEX"
  exit 0
fi

# Check if output already exists
OUTPUT_FILE="results/coloc/${PAIR_ID}.json"
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "Output exists, skipping: $OUTPUT_FILE"
  exit 0
fi

echo "Processing: $PAIR_ID"
echo "Job index: $LSB_JOBINDEX"
echo "Start time: $(date)"

# Run colocalization
Rscript scripts/run_coloc_genomewide.R \
  --manifest config/genomewide_coloc_manifest.tsv \
  --pair-id "$PAIR_ID" \
  --output "$OUTPUT_FILE"

echo "End time: $(date)"
