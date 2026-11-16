#!/usr/bin/env bash
# Snakemake --cluster-status for Slurm: prints running | success | failed for the id sbatch --parsable printed.
jid=${1%%;*}
st=$(sacct -j "$jid" -X -n -P -o State 2>/dev/null | head -n 1 | awk '{print $1}')
[ -n "$st" ] || st=$(squeue -h -j "$jid" -o %T 2>/dev/null | head -n 1)
case "$st" in
    COMPLETED) echo success ;;
    ""|PENDING|CONFIGURING|RUNNING|COMPLETING|REQUEUED|REQUEUE_HOLD|REQUEUE_FED|RESIZING|SUSPENDED|STAGE_OUT|SIGNALING) echo running ;;
    *) echo failed ;;
esac
