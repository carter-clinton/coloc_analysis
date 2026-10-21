#!/usr/bin/env bash
# Create (idempotently) the ta-r4 durable storage root on /rs1 and the repo symlink data/r4 -> it.
set -euo pipefail

R4ROOT=/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINK="$REPO/data/r4"

mkdir -p "$R4ROOT"/{downloads,ld,sumstats,results,logs/lsf,known_answer_survivors,tmp}
chmod 2770 "$R4ROOT" "$R4ROOT"/{downloads,ld,sumstats,results,logs,logs/lsf,known_answer_survivors,tmp}

if [ -e "$LINK" ] && [ ! -L "$LINK" ]; then
    echo "ERROR: $LINK exists and is not a symlink; refusing to touch it" >&2
    exit 2
fi
ln -sfn "$R4ROOT" "$LINK"
realpath "$LINK"
