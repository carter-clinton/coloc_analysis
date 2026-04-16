#!/usr/bin/env bash
# bin/setup-envs.sh -- Pre-create all project conda envs in .snakemake/conda/
#
# Why this exists
#   Snakemake's own --use-conda --conda-create-envs-only path hits a
#   reproducible interop bug with mamba 2.5:
#
#     error libmamba Non-conda folder exists at prefix - aborting
#
#   even when the target prefix does not exist. This is documented as scout
#   issue #4 at .planning/quick/260414-bmi-magma-scout/SCOUT-FINDINGS.md.
#
#   The same `mamba env create --file X.yaml --prefix Y` command works fine
#   when invoked directly, which is what this script does as a fallback.
#
# What it does
#   1. Uses the pinned smoke_dev snakemake (Python 3.11 + snakemake 7.32.4)
#      to ask snakemake to stage hashed env yamls into .snakemake/conda/*.yaml.
#   2. For each staged yaml without a matching prefix directory, invokes
#      `mamba env create` directly. The directly-invoked command is not
#      subject to the libmamba 2.5 interop bug.
#   3. Skips prefixes that already exist (idempotent).
#
# Usage
#   bin/setup-envs.sh [target]     # default target: all_pathway
#   bin/setup-envs.sh pathway_aggregate
#
# Prereqs
#   - /rs1/researchers/c/ckclinto/conda_envs/smoke_dev exists
#     (Python 3.11 + snakemake 7.32.4 + pulp<2.8)
#   - /rs1/researchers/c/ckclinto/miniconda3/bin/mamba exists
#
# Notes on hess_py27
#   hess_py27.yml still lists `defaults`. First-time creation will hit the
#   Anaconda ToS interactive prompt (scout issue #5). Answer `Y` once; the
#   env is then cached and subsequent invocations skip it. Python 2.7 is
#   EOL-only on `defaults`, so this is unavoidable.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

SMOKE_DEV="/rs1/researchers/c/ckclinto/conda_envs/smoke_dev"
SNAKEMAKE="$SMOKE_DEV/bin/snakemake"
MAMBA="/rs1/researchers/c/ckclinto/miniconda3/bin/mamba"
CONDA_DIR=".snakemake/conda"
TARGET="${1:-all_pathway}"

# Preflight
for path in "$SNAKEMAKE" "$MAMBA"; do
  if [[ ! -x "$path" ]]; then
    echo "[setup-envs] ERROR: required executable missing: $path" >&2
    exit 1
  fi
done

mkdir -p "$CONDA_DIR"

echo "[setup-envs] project: $PROJECT_ROOT"
echo "[setup-envs] target:  $TARGET"
echo "[setup-envs] snakemake: $SNAKEMAKE"
echo "[setup-envs] mamba:     $MAMBA"

# Step 1: Let snakemake stage the hashed yamls + attempt its own create path.
# If the wrapper succeeds, great. If it hits the libmamba 2.5 bug, it will
# leave the staged yamls in place for us to handle directly.
echo "[setup-envs] phase 1: snakemake --conda-create-envs-only (best effort)"
"$SNAKEMAKE" \
  --use-conda \
  --conda-frontend mamba \
  --conda-create-envs-only \
  --cores 1 \
  "$TARGET" \
  || echo "[setup-envs] snakemake wrapper path returned non-zero (likely scout issue #4) — falling through to direct-mamba fallback"

# Step 2: Walk staged yamls and create any missing prefixes directly.
echo "[setup-envs] phase 2: direct-mamba fallback for any missing prefixes"
created=0
skipped=0
failed=0
for yaml in "$CONDA_DIR"/*.yaml; do
  [[ -e "$yaml" ]] || continue
  # Snakemake convention: yaml is HASH_.yaml, env dir is HASH_/
  # Strip .yaml suffix to get the prefix (which already ends in _).
  prefix="${yaml%.yaml}"
  if [[ -d "$prefix/conda-meta" ]]; then
    skipped=$((skipped + 1))
    continue
  fi
  if [[ -d "$prefix" && ! -d "$prefix/conda-meta" ]]; then
    # Empty stub dir that snakemake created before bailing — remove so
    # mamba doesn't refuse with "Non-conda folder exists at prefix".
    rmdir "$prefix" 2>/dev/null || { echo "[setup-envs] WARN: $prefix exists and is non-empty non-env; skipping"; failed=$((failed + 1)); continue; }
  fi
  echo "[setup-envs] creating: $(basename "$prefix")  <-  $(basename "$yaml")"
  if "$MAMBA" env create --quiet --yes --file "$yaml" --prefix "$prefix"; then
    created=$((created + 1))
  else
    echo "[setup-envs] FAILED: $yaml"
    failed=$((failed + 1))
  fi
done

echo "[setup-envs] summary: created=$created skipped=$skipped failed=$failed"
if [[ "$failed" -gt 0 ]]; then
  exit 2
fi
echo "[setup-envs] done"
