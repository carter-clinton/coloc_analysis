#!/bin/bash
#BSUB -J trace_coloc_merge
#BSUB -o /share/clintonlab/ckclinto/admix_map/results/diagnostics/trace_coloc_%J.out
#BSUB -e /share/clintonlab/ckclinto/admix_map/results/diagnostics/trace_coloc_%J.err
#BSUB -n 1
#BSUB -R "rusage[mem=4GB]"
#BSUB -W 00:30
#BSUB -q short

# Add tabix to PATH
export PATH="/rs1/researchers/c/ckclinto/conda_envs/nyabg-tools/bin:$PATH"

# Load R environment (use the hyprcoloc conda environment)
source /rs1/researchers/c/ckclinto/miniconda3/bin/activate /gpfs_common/share01/clintonlab/ckclinto/admix_map/.conda/admix_map_r_hyprcoloc

# Run the diagnostic script
cd /share/clintonlab/ckclinto/admix_map
Rscript scripts/diagnostics/trace_coloc_merge.R /share/clintonlab/ckclinto/admix_map

echo ""
echo "Job completed at $(date)"
