#!/usr/bin/env bash
# scripts/run_ci_smoke.sh
# LSF cron wrapper for CI smoke test (REQ-9)
#
# Usage:
#   bash scripts/run_ci_smoke.sh              # dry-run (default until data populated)
#   bash scripts/run_ci_smoke.sh --full-run   # full execution (after data populated)
#
# Cron setup: Add to crontab or bsub scheduler for nightly runs.
# Example crontab entry (substitute your project root):
#   0 2 * * * cd /path/to/coloc_analysis && bash scripts/run_ci_smoke.sh
#
# Records pass/fail with timestamp in .planning/ci_status.md
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CI_STATUS="$PROJECT_ROOT/.planning/ci_status.md"
LOG_DIR="$PROJECT_ROOT/logs/ci"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_TAG="$(date '+%Y%m%d_%H%M%S')"

mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/smoke_${DATE_TAG}.log"

# Parse arguments
MODE="dry-run"
SNAKEMAKE_FLAGS="-n"  # dry-run by default
if [[ "${1:-}" == "--full-run" ]]; then
    MODE="full"
    SNAKEMAKE_FLAGS=""
fi

echo "[$TIMESTAMP] Starting CI smoke test (mode: $MODE)..." | tee "$LOG_FILE"

# Change to project root for correct relative path resolution
cd "$PROJECT_ROOT"

# Submit smoke test as LSF job and wait for completion
# bsub -K: synchronous submission (blocks until job completes)
# -q short: use short queue
# -n 2: 2 cores
# -M 8000: 8 GB memory limit
bsub -K -q short -n 2 -M 8000 \
    -o "$LOG_FILE" -e "$LOG_FILE" \
    -J "ci_smoke_${DATE_TAG}" \
    "snakemake $SNAKEMAKE_FLAGS \
        --snakefile tests/toy_3locus/Snakefile.test \
        --cores 2 \
        --use-conda" \
    2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

# Record result in ci_status.md
if [ "$EXIT_CODE" -eq 0 ]; then
    STATUS="PASS"
else
    STATUS="FAIL"
fi

# Initialize ci_status.md if it does not have the table header yet
if ! grep -q "Timestamp" "$CI_STATUS" 2>/dev/null; then
    cat > "$CI_STATUS" <<'HEADER'
# CI Smoke Test Status Log

Records pass/fail for the toy 3-locus CI smoke test (REQ-9).

| Timestamp | Status | Log File | Mode |
|-----------|--------|----------|------|
HEADER
fi

echo "| ${TIMESTAMP} | ${STATUS} | ${LOG_FILE} | ${MODE} |" >> "$CI_STATUS"

echo "[$TIMESTAMP] CI smoke test: $STATUS (exit code: $EXIT_CODE, mode: $MODE)"
