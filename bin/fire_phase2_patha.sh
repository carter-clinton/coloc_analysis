#!/bin/bash
# T1 Phase 2 first-production (Path A scope: gtex_eqtl + gtex_sqtl + negative controls).
#
# Preconditions:
#   - All 49 eQTL + 49 sQTL tissue .all.tsv.gz / .cc.tsv.gz files staged under
#     data/raw/gtex_v8/ and data/raw/gtex_v8_sqtl/ (verify via scripts/verify_phase2_data_staged.sh)
#   - Phase 1 fits present under results/fine_mapping/susie/ with named variants
#     (Option 1 fix, commit 6a4fdd8)
#   - config/qtl_sources.yaml + config/eqtl_catalogue_qtd_map.yaml committed
#     (commit 3879a77 + 2bde4c6)
#
# Launch via LSF:
set -euo pipefail
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
LOG="logs/phase2_firstprod_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

# Fire all_qtl_coloc + negative controls + pph4 threshold sweep
"$SMK" \
  --profile config/cluster_lsf \
  --config 'phase2_enabled_sources=["gtex_eqtl","gtex_sqtl"]' \
  --keep-going \
  all_qtl_coloc \
  results/negative_controls/curated_neg_ctrl_results.tsv \
  results/negative_controls/null_loci_summary.tsv \
  results/qtl_coloc/pph4_threshold_sweep.tsv \
  > "$LOG" 2>&1

echo "Phase 2 first-production complete. Log: $LOG"
echo "Results: results/qtl_coloc/tier_assignments.tsv"
