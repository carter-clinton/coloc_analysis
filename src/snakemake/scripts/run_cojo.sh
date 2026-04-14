#!/usr/bin/env bash
# Plan 09-05 Task 1 — GCTA --cojo-slct wrapper (D-04c + RESEARCH §6 Option D).
#
# Runs stepwise conditional + joint analysis at a single locus × cohort using
# GCTA 1.94.1 and an external 1000G Phase 3 LD reference (503 EUR / 661 AFR).
# Both LD panels are below GCTA's recommended N >= 4000 threshold; output is
# scoped as TIER-2 SUPPLEMENTARY (not primary replication) and a WARN is
# emitted to stderr when the reference is under-sized (gotcha #1 layer-1
# enforcement; T-09-22 mitigation).
#
# Usage:
#   run_cojo.sh <ma_file> <plink_prefix> <locus_snp_list> <out_prefix>
#
# Arguments:
#   ma_file         - GCTA 8-column .ma file (from prepare_cojo_ma.py)
#   plink_prefix    - 1000G PLINK prefix, e.g.
#                     data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.EUR.QC.10
#   locus_snp_list  - file with one SNP rsid per line (--extract target)
#   out_prefix      - output prefix; GCTA will emit <out_prefix>.jma.cojo etc.
#
# T-09-07 mitigation: set -euo pipefail + positional args are the ONLY
# user-controlled inputs and are always double-quoted below.

set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "usage: run_cojo.sh <ma_file> <plink_prefix> <locus_snp_list> <out_prefix>" >&2
  exit 2
fi

MA="$1"
PLINK_PREFIX="$2"
LOCUS_SNPS="$3"
OUT_PREFIX="$4"

# ---------------------------------------------------------------------------
# Gotcha #1 layer-1: WARN stderr if LD reference under-sized
# ---------------------------------------------------------------------------
FAM_FILE="${PLINK_PREFIX}.fam"
if [ ! -f "${FAM_FILE}" ]; then
  echo "ERROR: LD reference fam file not found: ${FAM_FILE}" >&2
  exit 3
fi

N_SAMPLES=$(wc -l < "${FAM_FILE}")
if [ "${N_SAMPLES}" -lt 4000 ]; then
  echo "WARN: LD reference ${PLINK_PREFIX} has N=${N_SAMPLES} (< 4000 GCTA threshold). COJO results are TIER-2 SENSITIVITY per RESEARCH §6 Option D / gotcha #1." >&2
fi

# ---------------------------------------------------------------------------
# GCTA invocation — all args are positional + literal; no shell expansion
# of user input beyond the double-quoted variables.
# ---------------------------------------------------------------------------
mkdir -p "$(dirname "${OUT_PREFIX}")"

gcta \
  --bfile "${PLINK_PREFIX}" \
  --cojo-file "${MA}" \
  --cojo-slct \
  --cojo-p 5e-8 \
  --cojo-wind 10000 \
  --extract "${LOCUS_SNPS}" \
  --out "${OUT_PREFIX}"
