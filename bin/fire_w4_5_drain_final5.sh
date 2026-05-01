#!/bin/bash
# bin/fire_w4_5_drain_final5.sh — W4.5-A continuation: drain final missing run_qtl_coloc JSONs
# Phase: ta-sh2b3-canonical-and-cache-refresh
# Origin: quick task 260501-r1q (PLAN.md authored 2026-05-01)
#
# Differs from bin/fire_w4_5_qtl_coloc_only.sh in ONE way: NO --forcerun run_qtl_coloc.
# The 1270 already-fresh JSONs (mtimes 2026-04-30T16:53 to 18:04 EDT) stay put;
# only the missing targets dispatch via natural mtime cascade.
#
# Pre-flight (caller verifies; this script does NOT enforce):
#   - bjobs is empty (PID 2670648 confirmed dead)
#   - .snakemake/locks/0.{input,output}.lock surgically cleared (qtl_coloc/finemap entries dropped; identity_ld preserved)
#   - results/qtl_coloc/qtl_coloc_manifest.tsv exists with 1469 rows
#   - results/fine_mapping/susie/*.fit.rds count = 96 (V4 niter=1000)
#   - 3 anchor md5s pinned (bmi/htn/stk) and TRACK-A-FROZEN-NUMBERS.md md5 pinned
#
# Compute envelope: 4-5 jobs x 1-3 min each on serial queue + LSF queueing latency = ~10-30 min wall.
# If the queue is busy with PID 830751's identity_ld jobs, may stretch — that's expected; do not bkill.
set -euo pipefail
RS1_ROOT=/rs1/researchers/c/ckclinto/coloc_analysis
GPFS_ROOT=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
if [ -d "${RS1_ROOT}/.git" ]; then
  cd "${RS1_ROOT}"
else
  cd "${GPFS_ROOT}"
fi
export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"
export LSF_UNIT_FOR_LIMITS=GB
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
LOG="logs/wave4_5_drain_final5_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs
echo "[$(date +%H:%M:%S)] W4.5-A drain-final-5 starting. Log: $LOG" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Pre-drain JSON count: $(ls results/qtl_coloc/*.json 2>/dev/null | wc -l) (expected 1270)" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   SuSiE-RSS .fit.rds count: $(ls results/fine_mapping/susie/*.fit.rds 2>/dev/null | wc -l) (expected 96)" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] Snakemake all_qtl_coloc — NO --forcerun (mtime cascade dispatches missing only)" | tee -a "$LOG"
"$SMK" \
  --configfile config/pipeline.yaml \
  --profile config/cluster_lsf \
  --jobs 50 --keep-going --rerun-incomplete --use-conda \
  --conda-prefix .snakemake/conda --latency-wait 120 \
  -s Snakefile \
  all_qtl_coloc \
  2>&1 | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] W4.5-A drain-final-5 done" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Post-drain JSON count: $(ls results/qtl_coloc/*.json 2>/dev/null | wc -l) (expected 1274)" | tee -a "$LOG"
