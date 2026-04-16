#!/usr/bin/env bash
# bin/bootstrap-conda-envs.sh -- Create all conda envs needed for a snakemake target.
# Handles the libmamba 2.5 "Non-conda folder exists at prefix" bug by
# iteratively discovering needed envs via snakemake and creating them
# with direct mamba calls.
#
# Usage: bin/bootstrap-conda-envs.sh [target]   # default: all_pathway

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

SNAKEMAKE="/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake"
MAMBA="/rs1/researchers/c/ckclinto/miniconda3/bin/mamba"
CONDA_DIR=".snakemake/conda"
TARGET="${1:-all_pathway}"
MAX_ITERATIONS=20

echo "[bootstrap] target: $TARGET"
echo "[bootstrap] snakemake: $SNAKEMAKE"
echo "[bootstrap] mamba: $MAMBA"

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "[bootstrap] iteration $i: running snakemake --conda-create-envs-only"
  if "$SNAKEMAKE" --use-conda --conda-create-envs-only --cores 1 "$TARGET" 2>&1; then
    echo "[bootstrap] ALL ENVS READY"
    exit 0
  fi

  echo "[bootstrap] snakemake failed — creating missing envs via direct mamba"
  created=0
  for yaml in "$CONDA_DIR"/*.yaml; do
    [ -e "$yaml" ] || continue
    hash=$(basename "$yaml" .yaml)
    prefix="$CONDA_DIR/$hash"
    # Skip if env is already valid
    [ -d "$prefix/conda-meta" ] && continue
    # Remove empty stub dir left by snakemake
    if [ -d "$prefix" ]; then
      rmdir "$prefix" 2>/dev/null || { echo "[bootstrap] WARN: $prefix non-empty, skipping"; continue; }
    fi
    echo "[bootstrap] creating: $hash"
    if "$MAMBA" env create --quiet --yes --file "$yaml" --prefix "$prefix"; then
      created=$((created + 1))
    else
      echo "[bootstrap] FAILED: $hash"
    fi
  done

  if [ "$created" -eq 0 ]; then
    echo "[bootstrap] ERROR: no new envs created but snakemake still failing"
    exit 1
  fi
  echo "[bootstrap] created $created env(s), retrying snakemake..."
done

echo "[bootstrap] ERROR: max iterations ($MAX_ITERATIONS) reached"
exit 1
