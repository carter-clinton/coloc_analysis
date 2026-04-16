#!/bin/bash
# bsub wrapper for Snakemake on NCSU HPC.
# - Converts mem_mb to GB (LSF_UNIT_FOR_LIMITS=GB on this cluster)
# - Does NOT pass -W (wall time) — let jobs run to completion
# - Snakemake passes the jobscript as the last positional argument

ARGS=()
JOBSCRIPT=""
MEM_GB=4

while [[ $# -gt 0 ]]; do
  case "$1" in
    -R)
      # Extract mem_mb and convert to GB (ceiling, minimum 1)
      MEM_NUM=$(echo "$2" | grep -oP 'mem=\K[0-9.]+')
      if [ -n "$MEM_NUM" ]; then
        MEM_GB=$(python3 -c "import math; print(max(1, math.ceil(float('$MEM_NUM')/1000)))")
      fi
      ARGS+=("-R" "rusage[mem=${MEM_GB}]")
      shift 2
      ;;
    -W)
      # Skip wall time — do not cap, let jobs run to completion
      shift 2
      ;;
    *)
      # Last arg is the jobscript path
      if [[ -f "$1" ]]; then
        JOBSCRIPT="$1"
        shift
      else
        ARGS+=("$1")
        shift
      fi
      ;;
  esac
done

mkdir -p logs/lsf 2>/dev/null

if [ -n "$JOBSCRIPT" ]; then
  bsub "${ARGS[@]}" < "$JOBSCRIPT"
else
  bsub "${ARGS[@]}"
fi
