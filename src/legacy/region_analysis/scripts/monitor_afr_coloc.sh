#!/bin/bash
# Monitor AFR coloc job array progress

JOB_ID="${1:-49394}"

echo "=== Monitoring AFR Coloc Job Array: $JOB_ID ==="
echo ""

# Get job status summary
echo "Job Status Summary:"
bjobs -a $JOB_ID 2>/dev/null | tail -n +2 | awk '{print $3}' | sort | uniq -c | sort -rn

echo ""
echo "Total Jobs: 150"

# Count completed results
completed=$(ls -1 results/multitrait/coloc/*AFR*asthma*.json 2>/dev/null | wc -l)
echo "Completed Results: $completed / 99 (asthma pairs)"

# Show recent completions
echo ""
echo "Most Recent Completions (last 5):"
ls -lt results/multitrait/coloc/*AFR*.json 2>/dev/null | head -5 | awk '{print $9}' | xargs -I {} basename {}

# Check for failures
echo ""
echo "Recent Failures (if any):"
grep -l "FAILED" logs/afr_coloc_*.err 2>/dev/null | tail -5 | while read f; do
  job_num=$(echo "$f" | grep -oP 'afr_coloc_\K[0-9]+')
  pair=$(sed -n "${job_num}p" results/multitrait/afr_pairs.txt 2>/dev/null)
  echo "  Job $job_num: $pair"
done

echo ""
echo "To check detailed status:"
echo "  bjobs -w $JOB_ID"
echo ""
echo "To check a specific job log:"
echo "  tail logs/afr_coloc_<N>.out"
echo "  tail logs/afr_coloc_<N>.err"
