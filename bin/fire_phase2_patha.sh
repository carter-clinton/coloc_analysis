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

# Fire all_qtl_coloc (scope-filtered) + matched-null-loci supplementary.
# Per REQ-7 scope reconciliation (commit 2026-04-20):
#   - HLA-immune neg-ctrl: covered within all_qtl_coloc via 113 HLA_6p21/asthma
#     rows from the curated regions manifest
#   - cosmetic + blood_group: delivered via Phase 5 (MAGMA+LDSC-SEG+HESS+g:Profiler,
#     all three curated_sets covered in Launch 15 outputs)
#   - matched-null-loci: 500 bedtools-shuffle regions produce the empirical
#     null distribution; target requested explicitly here as a supplement
#   - run_curated_negative_controls: wired-but-partial (manifest lacks
#     gwas_fit paths for cosmetic + blood_group regions outside the curated 12);
#     made an optional input of assign_tiers so the primary QTL coloc can
#     complete without it. The rule still exists and can be fired manually
#     once Phase 1 is extended in T2.
# Recovery Plan Stage 1 (2026-04-21): explicitly include the trait-pair
# multitrait coloc summary as a target. Without it, the DAG does not
# materialize results/multitrait/coloc_summary.tsv, causing assign_tiers
# to emit "GWAS coloc file is empty" and collapse all tiers to zero.
# See .planning/debug/multitrait_coloc_empty.md.
"$SMK" \
  --profile config/cluster_lsf \
  --config 'phase2_enabled_sources=["gtex_eqtl","gtex_sqtl"]' \
  --keep-going \
  all_qtl_coloc \
  results/multitrait/coloc_summary.tsv \
  results/negative_controls/null_loci_summary.tsv \
  > "$LOG" 2>&1

echo "Phase 2 first-production complete. Log: $LOG"
echo "Primary outputs:"
echo "  results/qtl_coloc/tier_assignments.tsv"
echo "  results/qtl_coloc/pph4_threshold_sweep.tsv"
echo "  results/qtl_coloc/gene_tissue_matrix.tsv"
echo "  results/qtl_coloc/gene_tissue_long.tsv"
echo "  results/negative_controls/null_loci_summary.tsv"
