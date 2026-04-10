#!/bin/bash
# Monitor hypertension t2d rerun job progress

JOB_ID="${1:-51786}"

echo "=== Monitoring Hypertension T2D Rerun Job: $JOB_ID ==="
echo ""

# Get job status summary
echo "Job Status Summary:"
bjobs -a $JOB_ID 2>/dev/null | tail -n +2 | awk '{print $3}' | sort | uniq -c | sort -rn

echo ""
echo "Total Jobs: 18"

# Count completed results
completed=$(ls -1 results/multitrait/coloc/*hypertension_vs_t2d*.json 2>/dev/null | wc -l)
echo "Completed Results: $completed / 18 expected from rerun"

# Show recent completions
echo ""
echo "Most Recent Completions (last 5):"
ls -lt results/multitrait/coloc/*hypertension_vs_t2d*.json 2>/dev/null | head -5 | awk '{print $9}' | xargs -I {} basename {}

# Check for failures
echo ""
echo "Recent Failures (if any):"
grep -l "FAILED" logs/htn_t2d_rerun_*.err 2>/dev/null | tail -5 | while read f; do
  job_num=$(echo "$f" | grep -oP 'htn_t2d_rerun_\K[0-9]+')
  pair=$(sed -n "${job_num}p" /tmp/hypertension_failed_dup.txt 2>/dev/null)
  echo "  Job $job_num: $pair"
done

echo ""
echo "To check detailed status:"
echo "  bjobs -w $JOB_ID"
