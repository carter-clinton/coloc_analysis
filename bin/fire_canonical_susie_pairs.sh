#!/bin/bash
# bin/fire_canonical_susie_pairs.sh — R2 canonical-pair coloc.susie driver
#
# Phase: ta-r3-audit-v2-driven-psd-and-r1-refire (Wave 3 audit-driven re-analysis)
# Predecessor: ta-sh2b3-canonical-and-cache-refresh (Wave 2 SH2B3 R2 fire)
#
# Fires coloc.susie on canonical trait-pairs for a given region/ancestry against
# pre-fitted Wave-1 SuSiE-RSS objects. Outputs land in a parallel namespace
# `results/multitrait/coloc_susie_R2/{pair_id}.json` to preserve the Stage 2
# `coloc_summary.tsv` md5 invariant (Pitfall 3 — Wave 5 explicitly re-renders).
#
# W3 audit-driven re-analysis adds parameterization for `--region` + `--ancestry`
# (default `SH2B3_12q24` / `EUR` — backwards-compatible per ta-r3 W3 plan-of-plans
# risk register row 3). When called with NO args, the driver reproduces the
# pre-W3 SH2B3 EUR behavior bit-for-bit.
#
# Usage (backwards-compatible — NO args):
#   PRIMARY_L=20 bash bin/fire_canonical_susie_pairs.sh
#
# Usage (W3 parameterized):
#   bash bin/fire_canonical_susie_pairs.sh --region FTO_16q12 --ancestry EUR
#   bash bin/fire_canonical_susie_pairs.sh --region MC4R_18q21 --ancestry EUR
#   bash bin/fire_canonical_susie_pairs.sh --region APOL1_22q12 --ancestry EUR
#   bash bin/fire_canonical_susie_pairs.sh --region CXADR_F2RL1_6p21 --ancestry EUR
#
# Pitfall 3 mitigation: per-pair JSONs land under
#   results/multitrait/coloc_susie_R2/{REGION}__{ANCESTRY}__{trait_a}_vs_{trait_b}.json
# (parallel to the existing results/multitrait/coloc_susie/ namespace) so the
# Stage 2 coloc_summary.tsv md5 invariant remains byte-identical until Wave 5.
#
# Compute envelope: ~10-30 min per pair on serial queue with la_multitrait_r env.
# 6 W3 pairs across 4 regions (FTO=3, MC4R=1, APOL1=1, CXADR=1) plus the 9 existing
# SH2B3 EUR pairs — well under serial 96-hr cap.

set -euo pipefail

# -----------------------------------------------------------------------------
# Argument parsing (backwards-compatible: NO args → SH2B3_12q24 EUR defaults)
# -----------------------------------------------------------------------------
REGION="SH2B3_12q24"
ANCESTRY="EUR"

usage() {
  cat <<USAGE
Usage: fire_canonical_susie_pairs.sh [--region <REGION>] [--ancestry <ANCESTRY>] [--help]

Options:
  --region    Region ID (default: SH2B3_12q24)
              Supported: SH2B3_12q24, FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21
  --ancestry  Ancestry (default: EUR)
              Supported: EUR (AFR/HIS deferred to Track B per OSF amendment §3 M3)
  --help      Show this help

When called with NO args, reproduces the pre-W3 SH2B3 EUR behavior bit-for-bit
(plan-of-plans risk register row 3 backwards-compat invariant).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region)
      REGION="$2"
      shift 2
      ;;
    --ancestry)
      ANCESTRY="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

# -----------------------------------------------------------------------------
# Working directory selection (D-TA-01 canonical)
# -----------------------------------------------------------------------------
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
LOG="logs/wave2_canonical_susie_${REGION}_${ANCESTRY}_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

PRIMARY_L="${PRIMARY_L:-20}"

# -----------------------------------------------------------------------------
# Per-region canonical-pair enumeration
# -----------------------------------------------------------------------------
# SH2B3_12q24 EUR (predecessor — 9 pairs, full lattice over {asthma, bmi,
# hypertension, stroke, t2d} minus already-on-disk asthma_vs_t2d):
#
# Other regions: canonical-pair enumeration per regions_curated.csv trait_list
# mapped to our 5-trait sumstats inventory {asthma, bmi, hypertension, stroke,
# t2d}. Pair names are alphabetically sorted (trait_a < trait_b lexically) per
# the pre-W2 manifest convention.
case "${REGION}" in
  SH2B3_12q24)
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
    ;;
  FTO_16q12)
    # trait_list bmi;t2d;htn → bmi, hypertension, t2d → 3 canonical pairs
    PAIRS=(
      bmi_vs_hypertension
      bmi_vs_t2d
      hypertension_vs_t2d
    )
    ;;
  MC4R_18q21)
    # trait_list bmi;t2d → 1 canonical pair
    PAIRS=(
      bmi_vs_t2d
    )
    ;;
  APOL1_22q12)
    # trait_list htn;ckd;stroke? — ckd not in trait inventory; question-marked
    # stroke retained as informative under audit-driven re-analysis → 1 canonical pair
    PAIRS=(
      hypertension_vs_stroke
    )
    ;;
  CXADR_F2RL1_6p21)
    # trait_list htn;obesity → bmi (proxy for obesity), hypertension → 1 canonical pair
    PAIRS=(
      bmi_vs_hypertension
    )
    ;;
  *)
    echo "[ERROR] Unsupported region: ${REGION}" >&2
    echo "        Supported: SH2B3_12q24, FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21" >&2
    exit 1
    ;;
esac

# Build full pair_ids and Snakemake targets
PAIR_IDS=()
TARGETS=()
for p in "${PAIRS[@]}"; do
  pid="${REGION}__${ANCESTRY}__${p}"
  PAIR_IDS+=("${pid}")
  TARGETS+=("results/multitrait/coloc_susie_R2/${pid}.json")
done

echo "[$(date +%H:%M:%S)] R2 canonical-pair coloc.susie fire starting." | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Region:   ${REGION}" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Ancestry: ${ANCESTRY}" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   PRIMARY_L=${PRIMARY_L}" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Pairs: ${#PAIRS[@]} (${PAIRS[*]})" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Output namespace: results/multitrait/coloc_susie_R2/" | tee -a "$LOG"
echo "[$(date +%H:%M:%S)]   Log: $LOG" | tee -a "$LOG"

# -----------------------------------------------------------------------------
# Build the R2 manifest (covers all currently-fired regions; backwards-compatible)
# -----------------------------------------------------------------------------
echo "[$(date +%H:%M:%S)] Building R2 manifest" | tee -a "$LOG"
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 \
  src/python/build_coloc_manifest_r2.py 2>&1 | tee -a "$LOG"

# -----------------------------------------------------------------------------
# Fire coloc.susie via Snakemake under the R2 overlay
# -----------------------------------------------------------------------------
"$SMK" \
  --configfile config/pipeline.yaml \
  --configfile config/pipeline_canonical_r2_overlay.yaml \
  --profile config/cluster_lsf \
  --jobs 50 --keep-going --rerun-incomplete --use-conda \
  --conda-prefix .snakemake/conda --latency-wait 120 \
  -s Snakefile \
  "${TARGETS[@]}" \
  2>&1 | tee -a "$LOG"

echo "[$(date +%H:%M:%S)] R2 fire done for ${REGION} ${ANCESTRY}" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Verification:" | tee -a "$LOG"
echo "  for t in ${TARGETS[*]}; do [ -f \"\$t\" ] && echo OK \"\$t\" || echo MISSING \"\$t\"; done" | tee -a "$LOG"
