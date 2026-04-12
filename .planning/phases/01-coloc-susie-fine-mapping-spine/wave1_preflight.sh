#!/usr/bin/env bash
# Wave 1 preflight -- remove stale {FINEMAP_DIR}/susie cache. Idempotent.
# T-1-05 mitigation: ensures fit-persistence switchover is not bypassed by
# Phase 0 dry-run residue. Safe to run multiple times.
set -euo pipefail
FINEMAP_DIR="${FINEMAP_DIR:-results/finemap}"
find "${FINEMAP_DIR}/susie" -type f 2>/dev/null | xargs -r rm -v || true
echo "[wave1_preflight] Cache clear complete. Files remaining: $(find "${FINEMAP_DIR}/susie" -type f 2>/dev/null | wc -l)"
