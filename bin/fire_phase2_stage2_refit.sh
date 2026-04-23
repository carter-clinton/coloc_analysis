#!/bin/bash
# RECOVERY Stage 2 production re-fire — post-narrow-validation (2026-04-22).
#
# Fires the full Stage 2 cascade on the LSF cluster:
#   1. build_ld_rds_1kg_eur x8  — rebuild the 8 stale EUR autosomal LD RDS
#      (SH2B3_12q24 + FTO_16q12 already rebuilt during narrow validation;
#       HLA_6p21 + BMI_Xq24 + all AFR stay on identity fallback — out of scope
#       for this fire).
#   2. run_finemap x95 — re-fit ALL Phase 1 SuSiE fits. --rerun-triggers=mtime
#      picks them up because run_susie_rss.R mtime (Stage 1d + Stage 2 fixes)
#      is newer than the existing .fit.rds files.
#   3. Phase 1 aggregators (finemap_summary, filter_finemap_summary → tier3).
#   4. Trait-pair coloc.susie (multitrait/coloc_summary.tsv) — consumes the
#      refreshed tier3 table.
#   5. run_qtl_coloc x~1010 — GTEx eQTL + sQTL scope only (OneK1K sc-eQTL and
#      UKB-PPP pQTL raw data not staged; filtered via phase2_enabled_sources).
#      --rerun-triggers=mtime catches all of them because run_qtl_coloc.R was
#      edited (commit 069b34f, Apr 21 20:24) after the first-production JSONs
#      landed.
#   6. aggregate_qtl_coloc + assign_tiers + pph4_threshold_sweep.
#
# Expected deltas vs first-production (RECOVERY_PLAN Stage 2/4 exit criteria):
#   - finemap_summary.tsv credible_sets column: 12/96 -> >=40/96 non-empty
#   - tier_assignments.tsv: 0 Tier A -> >=1 Tier A (structurally unblocked)
#   - SH2B3_12q24 trait-pair coloc PP.H4=1.0 at rs3184504/rs10774625 preserved
#
# Scope caveats (document in CP#1-final framing):
#   - HLA_6p21 + BMI_Xq24 + all AFR regions still on identity-LD fallback.
#     AFR Tier A candidates are handicapped pending matched-ancestry LD panel.
#
# Preconditions verified at fire time:
#   - bjobs shows no active jobs (clean slate)
#   - git status clean (5 Stage 2 commits landed, STATE.md checkpoint committed)
#   - data/reference/ldsc/1000G_EUR_Phase3_plink/ present (503 EUR HM3 panel)
#
# Usage:
#   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
#   bash bin/fire_phase2_stage2_refit.sh
#
# Driver runs on login node; Snakemake dispatches 1000+ jobs to LSF via the
# config/cluster_lsf profile. Expect 2-4 hr total.

set -euo pipefail

export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
LOG="logs/phase2_stage2_refit_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

echo "[$(date +%H:%M:%S)] Stage 2 production re-fire starting. Log: $LOG"

# Multitrait coloc per-pair JSONs are not backward-chained by summarize_coloc_results
# (same intentional-unwiring pattern as all_qtl_coloc / aggregate_qtl_coloc). Enumerate
# existing per-pair JSON paths so --rerun-triggers=mtime re-fires them against the
# Stage-2-refreshed .fit.rds files. If the manifest grows during this fire, those new
# pair_ids will be picked up via build_coloc_manifest -> summarize_coloc_results dep,
# but only existing pair_ids get re-run here (58 from Stage 1d baseline).
MULTITRAIT_PAIR_JSONS=(results/multitrait/coloc_susie/*.json)
echo "[$(date +%H:%M:%S)] Multitrait per-pair JSONs enumerated: ${#MULTITRAIT_PAIR_JSONS[@]}"

"$SMK" \
  --profile config/cluster_lsf \
  --rerun-triggers=mtime \
  --config 'phase2_enabled_sources=["gtex_eqtl","gtex_sqtl"]' \
  --keep-going \
  all_qtl_coloc \
  results/multitrait/coloc_summary.tsv \
  results/qtl_coloc/tier_assignments.tsv \
  "${MULTITRAIT_PAIR_JSONS[@]}" \
  > "$LOG" 2>&1

echo "[$(date +%H:%M:%S)] Stage 2 production re-fire complete."
echo ""
echo "Primary outputs to inspect:"
echo "  results/fine_mapping/finemap_summary.tsv         (expect credible_sets >= 40/96)"
echo "  results/multitrait/coloc_summary.tsv             (expect SH2B3 PP.H4=1.0 preserved)"
echo "  results/qtl_coloc/tier_assignments.tsv           (expect >=1 Tier A)"
echo "  results/qtl_coloc/pph4_threshold_sweep.tsv"
echo "  results/qtl_coloc/gene_tissue_matrix.tsv"
