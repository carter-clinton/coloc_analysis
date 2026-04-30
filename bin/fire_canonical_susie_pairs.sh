#!/bin/bash
# bin/fire_canonical_susie_pairs.sh — Wave 2 driver (D-TA-03)
# Phase: ta-sh2b3-canonical-and-cache-refresh
#
# Fires coloc.susie on 9 new SH2B3 EUR canonical trait-pairs (full lattice
# minus already-on-disk asthma_vs_t2d) against Wave-1 converged fits at the
# primary-result-L (set via PRIMARY_L env var; default 20 per D-TA-02).
#
# 9 pairs:
#   asthma_vs_bmi, asthma_vs_hypertension, asthma_vs_stroke,
#   bmi_vs_hypertension (canonical literature claim),
#   bmi_vs_stroke, bmi_vs_t2d,
#   hypertension_vs_stroke (canonical literature claim),
#   hypertension_vs_t2d, stroke_vs_t2d
#
# Pitfall 3 mitigation: per-pair JSONs land under
#   results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__{pair}.json
# (parallel to the existing results/multitrait/coloc_susie/ namespace) so
# the Stage 2 coloc_summary.tsv md5 invariant
# (5fa3c4004970c5da711d05947cb1f7d2) remains byte-identical until the
# Wave 5 explicit re-render documents the relaxation.
#
# Compute envelope: ~2 hr per pair on serial queue with la_multitrait_r env
# (per CONTEXT.md L176). 9 pairs in parallel → expect ~2-4 hr aggregate wall.
#
# Pre-fire requirements:
#   - Wave 1 complete with primary-result-L identified (default L=20)
#   - results_lsweep_L${PRIMARY_L}/fine_mapping/susie/*.fit.rds exist for all 5
#     SH2B3 EUR per-trait fits (asthma + bmi + hypertension + stroke + t2d)
#
# Usage:
#   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
#   PRIMARY_L=20 bash bin/fire_canonical_susie_pairs.sh

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
LOG="logs/wave2_canonical_susie_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

PRIMARY_L="${PRIMARY_L:-20}"
PAIRS=(
  SH2B3_12q24__EUR__asthma_vs_bmi
  SH2B3_12q24__EUR__asthma_vs_hypertension
  SH2B3_12q24__EUR__asthma_vs_stroke
  SH2B3_12q24__EUR__bmi_vs_hypertension
  SH2B3_12q24__EUR__bmi_vs_stroke
  SH2B3_12q24__EUR__bmi_vs_t2d
  SH2B3_12q24__EUR__hypertension_vs_stroke
  SH2B3_12q24__EUR__hypertension_vs_t2d
  SH2B3_12q24__EUR__stroke_vs_t2d
)
TARGETS=()
for p in "${PAIRS[@]}"; do
  TARGETS+=("results/multitrait/coloc_susie_R2/${p}.json")
done

echo "[$(date +%H:%M:%S)] Wave 2 canonical-pair coloc.susie fire starting. Log: $LOG" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   PRIMARY_L=${PRIMARY_L}" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Pairs: ${#PAIRS[@]}" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Output namespace: results/multitrait/coloc_susie_R2/" | tee -a "$LOG"

# Build the R2 manifest first (Wave 0 Task 5 builder)
echo "[$(date +%H:%M:%S)] Building R2 manifest" | tee -a "$LOG"
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 \
  src/python/build_coloc_manifest_r2.py 2>&1 | tee -a "$LOG"

# Fire coloc.susie via Snakemake under the R2 overlay
"$SMK" \
  --configfile config/pipeline.yaml \
  --configfile config/pipeline_canonical_r2_overlay.yaml \
  --profile config/cluster_lsf \
  --jobs 50 --keep-going --rerun-incomplete --use-conda \
  --conda-prefix .snakemake/conda --latency-wait 120 \
  -s Snakefile \
  "${TARGETS[@]}" \
  2>&1 | tee -a "$LOG"
echo "[$(date +%H:%M:%S)] Wave 2 fire done" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Verification: bin/verify_ta_sh2b3_phase.sh --wave 2" | tee -a "$LOG"
