#!/usr/bin/env bash
set -euo pipefail

cd /share/clintonlab/ckclinto/admix_map

export PATH="/rs1/researchers/c/ckclinto/conda_envs/snakemake/bin:${PATH}"
export TABIX_BIN="${TABIX_BIN:-/rs1/researchers/c/ckclinto/conda_envs/snakemake/bin/tabix}"

if [ "$#" -gt 0 ]; then
  SNAKE_ARGS="$*"
else
  SNAKE_ARGS="--cores 4"
fi

env HOME=/share/clintonlab/ckclinto/admix_map \
    TMPDIR=/share/clintonlab/ckclinto/admix_map/tmp \
    SNAKEMAKE_TMPDIR=/share/clintonlab/ckclinto/admix_map/tmp \
    PYTHONPATH=/share/clintonlab/ckclinto/admix_map \
    /rs1/researchers/c/ckclinto/conda_envs/snakemake/bin/snakemake ${SNAKE_ARGS}
