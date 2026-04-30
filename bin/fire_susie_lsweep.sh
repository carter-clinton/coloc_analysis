#!/bin/bash
# bin/fire_susie_lsweep.sh — Wave 1 driver (D-TA-02)
# Phase: ta-sh2b3-canonical-and-cache-refresh
#
# Fires SuSiE-RSS at L ∈ {15, 20, 30} for SH2B3 EUR BMI + hypertension + stroke
# (3 traits × 3 L values = 9 fits) under per-L policy YAML overlays scaffolded
# by Wave 0 Task 3 + the Pitfall 2 mitigation patch in Wave 0 Task 4
# (finemap.smk:62 now reads policy from config).
#
# Compute envelope: ~2-4 hr per fit on serial queue with la_multitrait_r env
# (per AUDIT-RESPONSE 2026-04-26 line 260). 9 fits dispatched in parallel
# across LSF slots → expect ~4-8 hr aggregate wall.
#
# Convergence verification (per-fit JSON):
#   - n_CS << L (Zou 2022 §Discussion criterion)
#   - convergence_status == "converged_*"
#   - L_saturated == false
#
# D-TA-Wave1-headline decision (51/96 numerator update vs disclosure column)
# is recorded post-fire from the per-trait outcomes.
#
# Pre-fire requirements:
#   - Wave 0 Task 7 (D-TA-OSF-COVERAGE) cleared (HARD GATE on this Wave 1 fire)
#   - D-TA-01 path resolved (see CONTEXT.md D-TA-Wave-0-foundations addendum;
#     /rs1/.../coloc_analysis was found NOT to be a git repo on Wave 0 fire
#     date — Carter MUST resolve the namespace collision before this driver
#     fires, OR redirect cwd to GPFS path)
#
# Usage:
#   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
#   bash bin/fire_susie_lsweep.sh
#
# Driver runs on login node; Snakemake dispatches 9 jobs to LSF via the
# config/cluster_lsf profile.

set -euo pipefail

# D-TA-01 canonical source path. If the path is not a git repo, fall back to
# GPFS interactive mount (same physical filesystem per D-TA-01 §"Why" L121).
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
LOG="logs/wave1_susie_lsweep_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

L_VALUES=(15 20 30)
TRAITS=(bmi hypertension stroke)
REGION=SH2B3_12q24
POP=EUR

echo "[$(date +%H:%M:%S)] Wave 1 SuSiE-RSS L-sweep fire starting. Log: $LOG" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Region: $REGION ($POP)" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Traits: ${TRAITS[*]}" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   L values: ${L_VALUES[*]}" | tee -a "$LOG"

for L in "${L_VALUES[@]}"; do
  echo "[$(date +%H:%M:%S)] L=${L} fire starting" | tee -a "$LOG"
  TARGETS=()
  for T in "${TRAITS[@]}"; do
    TARGETS+=("results_lsweep_L${L}/fine_mapping/susie/${T}.${POP}.${REGION}.json")
  done
  "$SMK" \
    --configfile config/pipeline.yaml \
    --configfile "config/pipeline_lsweep_L${L}_overlay.yaml" \
    --profile config/cluster_lsf \
    --jobs 50 --keep-going --rerun-incomplete --use-conda \
    --conda-prefix .snakemake/conda --latency-wait 120 \
    -s Snakefile \
    "${TARGETS[@]}" \
    2>&1 | tee -a "$LOG"
  echo "[$(date +%H:%M:%S)] L=${L} fire done" | tee -a "$LOG"
done

echo "[$(date +%H:%M:%S)] All L-sweep fires complete. Run convergence verification next:" | tee -a "$LOG"
echo "  bin/verify_ta_sh2b3_phase.sh --wave 1" | tee -a "$LOG"
