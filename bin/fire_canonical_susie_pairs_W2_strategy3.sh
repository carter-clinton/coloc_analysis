#!/bin/bash
# Wave 2 per-pair direct dispatch (Strategy 3 — bypass Snakemake)
# Anticipated by config/pipeline_canonical_r2_overlay.yaml NOTE block (option a).
# Pitfall 3 mitigation: writes to results/multitrait/coloc_susie_R2/ only;
# does NOT trigger summarize_coloc_results aggregator.
set -euo pipefail
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"
export LSF_UNIT_FOR_LIMITS=GB

RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
LOGDIR=logs/lsf
OUTDIR=results/multitrait/coloc_susie_R2
mkdir -p "$LOGDIR" "$OUTDIR"

DISPATCH_TS=$(date +%Y%m%d_%H%M%S)
PAIRS=(
  asthma_vs_bmi
  asthma_vs_hypertension
  asthma_vs_stroke
  bmi_vs_hypertension
  bmi_vs_stroke
  bmi_vs_t2d
  hypertension_vs_stroke
  hypertension_vs_t2d
  stroke_vs_t2d
)

# manifest path (R2)
MANIFEST_R2=results/multitrait/coloc_manifest_R2.tsv
POLICY=config/susie_policy.yaml

# Validate prerequisites
[ -f "$MANIFEST_R2" ] || { echo "ABORT: $MANIFEST_R2 missing"; exit 1; }
[ -f "$POLICY" ] || { echo "ABORT: $POLICY missing"; exit 1; }
[ -x "$RSCRIPT" ] || { echo "ABORT: $RSCRIPT not executable"; exit 1; }
for T in asthma bmi hypertension stroke t2d; do
  F="results/fine_mapping/susie/${T}.EUR.SH2B3_12q24.fit.rds"
  [ -f "$F" ] || { echo "ABORT: $F missing"; exit 1; }
done

JOB_IDS_FILE="logs/wave2_canonical_susie_${DISPATCH_TS}.jobids.txt"
> "$JOB_IDS_FILE"

for PAIR in "${PAIRS[@]}"; do
  PAIR_ID="SH2B3_12q24__EUR__${PAIR}"
  TRAIT_A="${PAIR%%_vs_*}"
  TRAIT_B="${PAIR##*_vs_}"
  FIT_A="results/fine_mapping/susie/${TRAIT_A}.EUR.SH2B3_12q24.fit.rds"
  FIT_B="results/fine_mapping/susie/${TRAIT_B}.EUR.SH2B3_12q24.fit.rds"
  OUT="$OUTDIR/${PAIR_ID}.json"
  ERR="$LOGDIR/wave2_${PAIR_ID}_${DISPATCH_TS}.err"
  OUTLOG="$LOGDIR/wave2_${PAIR_ID}_${DISPATCH_TS}.out"

  if [ -f "$OUT" ]; then
    echo "[skip] $OUT already exists (pre-existing)"
    continue
  fi

  CMD="\
$RSCRIPT src/snakemake/scripts/run_coloc_susie.R \
  --fit-a $FIT_A \
  --fit-b $FIT_B \
  --policy $POLICY \
  --pair-id $PAIR_ID \
  --manifest $MANIFEST_R2 \
  --output $OUT"

  BSUB_OUT=$(bsub -q serial -W 5760 -n 1 -R "rusage[mem=8]" \
    -e "$ERR" -o "$OUTLOG" \
    -J "w2_${PAIR}" \
    "$CMD" 2>&1)
  echo "[$PAIR] $BSUB_OUT"
  JID=$(echo "$BSUB_OUT" | grep -oE 'Job <[0-9]+>' | grep -oE '[0-9]+')
  if [ -n "$JID" ]; then
    echo "$JID $PAIR_ID" >> "$JOB_IDS_FILE"
  fi
done

echo "[$(date +%H:%M:%S)] Dispatch complete. Job IDs written to $JOB_IDS_FILE"
echo "DISPATCH_TS=$DISPATCH_TS"
