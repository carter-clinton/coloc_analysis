#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 4 ]]; then
  echo "Usage: $0 <1kg_vcf.gz> <sample_list> <out_prefix> <maf> [geno]" >&2
  exit 1
fi

VCF="$1"
SAMPLES="$2"
OUT="$3"
MAF="$4"
GENO="${5:-0.01}"

plink \
  --vcf "${VCF}" \
  --keep "${SAMPLES}" \
  --maf "${MAF}" \
  --geno "${GENO}" \
  --make-bed \
  --out "${OUT}"
