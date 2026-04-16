#!/bin/bash
# bsub wrapper for Snakemake on NCSU HPC.
# - Converts mem_mb to GB (LSF_UNIT_FOR_LIMITS=GB on this cluster)
# - Sets wall time to queue maximum (serial=5760 min, long=14400 min)
#   since all queues default to 30 min RUNLIMIT
# - Snakemake passes the jobscript as the last positional argument

ARGS=()
JOBSCRIPT=""
MEM_GB=4
QUEUE="serial"

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
    -q)
      QUEUE="$2"
      ARGS+=("-q" "$2")
      shift 2
      ;;
    -W)
      # Skip any incoming -W; we set wall time based on queue below
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

# Set wall time to queue maximum to override 30-min default RUNLIMIT.
# serial max=5760 min (4 days), long max=14400 min (10 days),
# standard max=2880 min (2 days).
case "$QUEUE" in
  long)     ARGS+=("-W" "14400") ;;
  standard) ARGS+=("-W" "2880")  ;;
  *)        ARGS+=("-W" "5760")  ;;
esac

mkdir -p logs/lsf 2>/dev/null

if [ -n "$JOBSCRIPT" ]; then
  bsub "${ARGS[@]}" < "$JOBSCRIPT"
else
  bsub "${ARGS[@]}"
fi
