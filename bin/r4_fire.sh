#!/usr/bin/env bash
# The only supported way to run Snakefile.ta_r4.
#   bash bin/r4_fire.sh <stage> <arm> [snakemake args / targets...]
#   bash bin/r4_fire.sh --show-conda-pkgs-dirs     (prints the isolated conda pkgs_dirs and exits)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
CONDA_BIN=/rs1/researchers/c/ckclinto/miniconda3/condabin
R4_CONDA_PREFIX=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4
R4_CONDARC=$R4_CONDA_PREFIX/condarc

# Conda isolation (W0a measured: CONDARC alone still lists the shared cache via ~/.condarc and
# ~/.bashrc's CONDA_PKGS_DIRS). ~/.condarc and ~/.bashrc are not edited.
# channel_priority flexible: envs/plink.yml (bioconda first) is unsatisfiable under strict (W0b2).
mkdir -p "$R4_CONDA_PREFIX/pkgs" "$R4_CONDA_PREFIX/home"
printf 'pkgs_dirs:\n  - %s\nchannel_priority: flexible\nsolver: libmamba\n' "$R4_CONDA_PREFIX/pkgs" > "$R4_CONDARC"
export CONDA_PKGS_DIRS="$R4_CONDA_PREFIX/pkgs" HOME="$R4_CONDA_PREFIX/home" CONDARC="$R4_CONDARC"
export PATH="$CONDA_BIN:$PATH"

if [ "${1:-}" = "--show-conda-pkgs-dirs" ]; then
    exec conda config --show pkgs_dirs
fi

if [ $# -lt 2 ]; then
    echo "usage: bash bin/r4_fire.sh <repro|production> <arm> [snakemake args...]" >&2
    exit 2
fi
STAGE=$1
ARM=$2
shift 2

for a in "$@"; do
    case "$a" in
        --conda-cleanup-pkgs*) echo "REFUSED: --conda-cleanup-pkgs is never passed (shared-cache incident 2026-10-11)" >&2; exit 2 ;;
    esac
done

if ! "$PY" - "$ARM" "$STAGE" <<'PYEOF'
import sys
sys.path.insert(0, "src/python")
from ta_r4.arms import ARMS
arm, stage = sys.argv[1], sys.argv[2]
if arm not in ARMS:
    sys.exit(f"REFUSED: unknown arm {arm!r}; known: {sorted(ARMS)}")
if ARMS[arm]["stage"] != stage:
    sys.exit(f"REFUSED: arm {arm} is stage {ARMS[arm]['stage']!r}, not {stage!r}")
PYEOF
then
    exit 2
fi

bash bin/r4_link_storage.sh >/dev/null
mkdir -p data/r4/logs/lsf

if [ "$STAGE" = production ]; then
    DIRTY=$(git status --porcelain -- Snakefile.ta_r4 src/python/ta_r4 src/snakemake config/ta_r4 src/legacy)
    if [ -n "$DIRTY" ]; then
        echo "REFUSED: uncommitted changes in the analysis tree (the receipt binds HEAD):" >&2
        echo "$DIRTY" >&2
        exit 2
    fi
    (cd src/python && "$PY" -m ta_r4.r4_osf_gate verify-online --stage production)
    echo "Do not commit until this fire ends: in-job gate checks require HEAD == receipt head_sha."
fi

exec "$SMK" -s Snakefile.ta_r4 \
    --configfile config/pipeline.yaml config/ta_r4/overlay_base.yaml "config/ta_r4/overlay_${ARM}.yaml" \
    --use-conda --conda-prefix "$R4_CONDA_PREFIX" \
    --profile config/ta_r4/cluster_lsf "$@"
