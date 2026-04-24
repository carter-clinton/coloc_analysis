#!/bin/bash
# scripts/fire_identity_ld_rerun.sh -- Author: quick-260424-k2d
#
# Two-phase Snakemake fire for the Route A identity-LD re-run.
#
# Phase 1: finemap + manifest build (96 finemap + chain to coloc_manifest.tsv).
# Phase 2: coloc_susie pair JSONs (enumerated from the identity-LD coloc_manifest
#          built by Phase 1) + coloc_summary.tsv.
#
# Phases are sequential because run_coloc_susie's DAG needs coloc_manifest.tsv
# to resolve pair_id wildcards at plan time (coloc.smk:_coloc_manifest_row).
#
# Invocation (from repo root):
#   nohup bash scripts/fire_identity_ld_rerun.sh > /tmp/k2d_fire.log 2>&1 &
#
# Monitor: bjobs -u ckclinto; tail -f /tmp/k2d_fire.log

set -euo pipefail

cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
export PATH=/home/ckclinto/miniconda3/bin:$PATH

SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
CONFIGS=(--configfile config/pipeline.yaml --configfile config/pipeline_identity_overlay.yaml)
CLUSTER=(--cluster "config/bsub_wrapper.sh" --jobs 50 --keep-going --rerun-incomplete
         --use-conda --conda-prefix .snakemake/conda --latency-wait 120)

echo "=== Identity-LD re-run fire: $(date -Iseconds) ==="
echo "Phase 1: finemap + coloc_manifest.tsv"
$SMK "${CONFIGS[@]}" "${CLUSTER[@]}" \
  -s Snakefile \
  results_identity_ld/multitrait/coloc_manifest.tsv

echo ""
echo "=== Phase 1 complete: $(date -Iseconds) ==="
echo "Manifest pair count: $(tail -n +2 results_identity_ld/multitrait/coloc_manifest.tsv | wc -l)"

# Enumerate pair JSON targets from the freshly built identity-LD manifest
TARGETS=()
while IFS=$'\t' read -r _ _ _ _ _ _ _ _ _ pair_id; do
  TARGETS+=("results_identity_ld/multitrait/coloc_susie/${pair_id}.json")
done < <(tail -n +2 results_identity_ld/multitrait/coloc_manifest.tsv)

echo "Phase 2: ${#TARGETS[@]} coloc pair JSONs + coloc_summary.tsv"
$SMK "${CONFIGS[@]}" "${CLUSTER[@]}" \
  -s Snakefile \
  "${TARGETS[@]}" \
  results_identity_ld/multitrait/coloc_summary.tsv

echo ""
echo "=== Fire complete: $(date -Iseconds) ==="
echo "Summary: $(wc -l < results_identity_ld/multitrait/coloc_summary.tsv) lines in coloc_summary.tsv"
