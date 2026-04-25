#!/usr/bin/env bash
# bin/fire_m1_03_complete.sh — END-TO-END m1-03 driver:
#   1. Refire empty harmonized files (calls bin/refire_empty_harmonized.sh)
#   2. Stage 1: Munge all populated harmonized files
#   3. Stage 2: Build trait_keys.txt from disk
#   4. Stage 3: LDSC --rg star fire
#   5. Stage 4: Reduce -> NxN matrix + long-form TSV + validation JSON
#
# Single-instance lock to prevent multiple concurrent runs corrupting outputs.
set -uo pipefail

LOCKFILE=logs/m1_03_complete.lock
if [ -f "$LOCKFILE" ]; then
    PID=$(cat "$LOCKFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "ERROR: another m1-03 run alive (PID $PID). Refusing to start."
        exit 1
    fi
    echo "Stale lockfile (PID $PID dead); removing."
    rm -f "$LOCKFILE"
fi
mkdir -p logs
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

echo "===== m1-03 master driver starting at $(date) ====="

# Stage 0: Refire empty harmonized.
echo "===== Stage 0: refire empty harmonized files ====="
bash bin/refire_empty_harmonized.sh 2>&1
echo "===== Stage 0 complete at $(date) ====="

# Stages 1-4 from existing driver.
echo "===== Stages 1-4: munge + trait_keys + rg-stars + reduce ====="
bash bin/fire_m1_03_munge_and_rg.sh all 2>&1
echo "===== m1-03 master driver complete at $(date) ====="
