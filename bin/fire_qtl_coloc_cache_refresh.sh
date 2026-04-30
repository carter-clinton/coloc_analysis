#!/bin/bash
# bin/fire_qtl_coloc_cache_refresh.sh — Wave 4 driver (D-TA-04)
# Phase: ta-sh2b3-canonical-and-cache-refresh
#
# Cache invalidation + Snakemake re-fire post commits 069b34f
# (run_qtl_coloc.R chr:pos tolerance) + 7d54183 (run_susie_rss.R LD-rsid
# override). Both fixes are HEAD ancestors per Wave 0 Task 1.
#
# Cache scope per D-TA-04-DIAGNOSTIC (Wave 0 Task 2 outcome RSID):
#   - Default SUSIE_LAYER_SCOPE=no  → QTL_COLOC_ONLY (~10 hr at 50 cores)
#   - SUSIE_LAYER_SCOPE=yes        → BOTH_LAYERS    (~15 hr; +5 hr SuSiE)
#
# Compute envelope: ~10 hr at 50 LSF cores for ~1,274 QTL-coloc attempts.
# Wave 4.5 fallback: if Wave 4 PASS criterion (`too_few_snps ≤ 200`) fails,
# the diagnostic conclusion is revised and SuSiE-RSS layer also refired.
#
# Cache backup convention (Pitfall 5: idempotent backup-name uniqueness):
#   results/qtl_coloc                  → results/qtl_coloc.preFix.bak.${TS}
#   results/fine_mapping/susie         → results/fine_mapping/susie.preFix.bak.${TS}
#                                        (only when SUSIE_LAYER_SCOPE=yes)
#
# Usage:
#   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
#   bash bin/fire_qtl_coloc_cache_refresh.sh                 # default QTL-only
#   SUSIE_LAYER_SCOPE=yes bash bin/fire_qtl_coloc_cache_refresh.sh   # both layers

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
LOG="logs/wave4_qtl_coloc_refresh_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

# Backup with timestamp (Pitfall 5: idempotent backup-name uniqueness)
TS=$(date +%Y%m%d_%H%M%S)
BACKUP_QTL="results/qtl_coloc.preFix.bak.${TS}"
BACKUP_SUSIE="results/fine_mapping/susie.preFix.bak.${TS}"

if [ ! -d "results/qtl_coloc" ]; then
  echo "ERROR: results/qtl_coloc does not exist. Wave 4 has nothing to invalidate." | tee -a "$LOG"
  exit 1
fi
echo "[$(date +%H:%M:%S)] Wave 4 QTL-coloc cache refresh starting. Log: $LOG" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   SUSIE_LAYER_SCOPE=${SUSIE_LAYER_SCOPE:-no}" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] Backing up results/qtl_coloc → ${BACKUP_QTL}" | tee -a "$LOG"
mv results/qtl_coloc "${BACKUP_QTL}"

if [ "${SUSIE_LAYER_SCOPE:-no}" = "yes" ]; then
  if [ -d "results/fine_mapping/susie" ]; then
    echo "[$(date +%H:%M:%S)] Backing up results/fine_mapping/susie → ${BACKUP_SUSIE}" | tee -a "$LOG"
    mv results/fine_mapping/susie "${BACKUP_SUSIE}"
  fi
fi

# Snakemake re-fire — target 'all_qtl_coloc' rule (verified in Wave 0 Task 1
# Snakefile rule-name surface enumeration; Snakefile L209).
echo "[$(date +%H:%M:%S)] Snakemake all_qtl_coloc re-fire starting" | tee -a "$LOG"
"$SMK" \
  --configfile config/pipeline.yaml \
  --profile config/cluster_lsf \
  --jobs 50 --keep-going --rerun-incomplete --use-conda \
  --conda-prefix .snakemake/conda --latency-wait 120 \
  -s Snakefile \
  all_qtl_coloc \
  2>&1 | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] Wave 4 re-fire done" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "PASS criterion: too_few_snps count drops from 1,005 baseline to ≤ 200" | tee -a "$LOG"
echo "Verification: bin/verify_ta_sh2b3_phase.sh --wave 4" | tee -a "$LOG"
