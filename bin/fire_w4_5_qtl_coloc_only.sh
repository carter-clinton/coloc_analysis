#!/bin/bash
# bin/fire_w4_5_qtl_coloc_only.sh — Wave 4.5 launcher (D-TA-WAVE4-5-A-OUTCOME)
# Phase: ta-sh2b3-canonical-and-cache-refresh
#
# 2nd-pass qtl_coloc layer rebuild after V4 dispatch (commit c8ee71a tracker_v5)
# completed SuSiE-RSS layer rebuild but planned 0 run_qtl_coloc instances. Per
# qtl_coloc.smk lines 56-60 docstring, the smk module is an explicit 2-pass
# system: pass 1 (V4) built the manifest; pass 2 (this script) reads it at
# parse time via _qtl_coloc_per_id_jsons() and expands per-id targets.
#
# This script BYPASSES bin/fire_qtl_coloc_cache_refresh.sh because that
# driver mv's results/qtl_coloc/ -> backup unconditionally, which would mv
# the V4-built manifest -> backup and defeat pass 2 (manifest must be at
# results/qtl_coloc/qtl_coloc_manifest.tsv at parse time for the
# QTL_COLOC_PER_ID_JSONS expansion to find 1469 rows).
#
# Pre-flight (caller verifies; this script does NOT enforce):
#   - results/qtl_coloc/qtl_coloc_manifest.tsv exists with 1469 rows
#   - results/fine_mapping/susie/ has 96 .fit.rds files at niter=1000 (V4)
#   - run_susie_rss.R mtime is OLDER than oldest .fit.rds (else SuSiE cascade
#     re-triggers and the V4 rebuild gets clobbered)
#   - All 4 invariant md5s unchanged: TRACK-A 9d0405a4..., coloc_summary
#     5fa3c4..., IDENTITY-LD-K2D 8ef28cf..., W2_R2 b74e36e2...
#
# Snakemake invocation: --forcerun run_qtl_coloc (NOT --forcerun run_finemap)
# preserves the V4-rebuilt SuSiE layer; downstream aggregator chain
# (aggregate_qtl_coloc, summarize_coloc_results, assign_tiers,
# build_gene_tissue_matrix) re-runs naturally via mtime cascade once
# run_qtl_coloc finishes.
#
# Compute envelope: ~1-3 hr at 50 LSF cores for ~1469 fast run_qtl_coloc
# instances on serial queue (no time cap).
#
# Usage:
#   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
#   bash bin/fire_w4_5_qtl_coloc_only.sh

set -euo pipefail

RS1_ROOT=/rs1/researchers/c/ckclinto/coloc_analysis
GPFS_ROOT=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
if [ -d "${RS1_ROOT}/.git" ]; then
  cd "${RS1_ROOT}"
else
  echo "[WARN] ${RS1_ROOT} is not a git repo — falling back to GPFS path (D-TA-Wave-0-foundations finding)"
  cd "${GPFS_ROOT}"
fi

export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
LOG="logs/wave4_5_qtl_coloc_only_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

# Sanity check: manifest must exist for pass-2 expansion to find rows
MANIFEST="results/qtl_coloc/qtl_coloc_manifest.tsv"
if [ ! -f "$MANIFEST" ]; then
  echo "ERROR: $MANIFEST does not exist. Pass 1 (V4 dispatch) must complete before W4.5-a." | tee -a "$LOG"
  exit 1
fi
N_ROWS=$(($(wc -l < "$MANIFEST") - 1))
echo "[$(date +%H:%M:%S)] Wave 4.5-a qtl_coloc-only refire starting. Log: $LOG" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Manifest: $MANIFEST ($N_ROWS rows)" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   SuSiE-RSS .fit.rds count: $(ls results/fine_mapping/susie/*.fit.rds 2>/dev/null | wc -l)" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] No mv steps (driver bypass — preserve manifest + V4 SuSiE layer)" | tee -a "$LOG"

# Snakemake re-fire — target 'all_qtl_coloc' with --forcerun run_qtl_coloc only.
# Aggregator chain rebuilds via natural mtime cascade once per-id JSONs land.
echo "[$(date +%H:%M:%S)] Snakemake all_qtl_coloc re-fire starting (--forcerun run_qtl_coloc)" | tee -a "$LOG"
"$SMK" \
  --configfile config/pipeline.yaml \
  --profile config/cluster_lsf \
  --jobs 50 --keep-going --rerun-incomplete --use-conda \
  --conda-prefix .snakemake/conda --latency-wait 120 \
  --forcerun run_qtl_coloc \
  -s Snakefile \
  all_qtl_coloc \
  2>&1 | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] Wave 4.5-a re-fire done" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "PASS criterion (W4.5-a-specific): results/qtl_coloc/*.json count >= 1000 AND too_few_snps count <= 200" | tee -a "$LOG"
echo "Verification: bin/verify_ta_sh2b3_phase.sh --wave 4 (note: C9 has integer-comparison bug; manual gate computation needed)" | tee -a "$LOG"
