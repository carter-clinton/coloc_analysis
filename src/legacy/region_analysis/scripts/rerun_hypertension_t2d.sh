#!/bin/bash
#BSUB -J htn_t2d_rerun[1-18]
#BSUB -o logs/htn_t2d_rerun_%I.out
#BSUB -e logs/htn_t2d_rerun_%I.err
#BSUB -n 1
#BSUB -R "rusage[mem=8GB]"
#BSUB -W 1:00

cd /gpfs_common/share01/clintonlab/ckclinto/admix_map

# Load conda
export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"
source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true

# Activate environment
conda activate la_multitrait_r

# Get pair ID for this job
PAIR_ID=$(sed -n "${LSB_JOBINDEX}p" results/multitrait/hypertension_rerun_pairs.txt)

echo "=================================================="
echo "Job ${LSB_JOBINDEX}: Rerunning coloc for ${PAIR_ID}"
echo "=================================================="

# Run coloc
Rscript scripts/run_coloc.R \
  --manifest results/multitrait/coloc_manifest.tsv \
  --pair-id "$PAIR_ID" \
  --output "results/multitrait/coloc/${PAIR_ID}.json"

exit_code=$?
if [[ $exit_code -eq 0 ]]; then
  echo "SUCCESS: Coloc completed for ${PAIR_ID}"
else
  echo "FAILED: Coloc failed for ${PAIR_ID} with exit code $exit_code"
fi

exit $exit_code
