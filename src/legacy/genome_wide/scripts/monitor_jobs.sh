#!/bin/bash
# Monitor genome-wide colocalization jobs

GENOME_WIDE_DIR="/share/clintonlab/ckclinto/admixmap/genome_wide"
cd "$GENOME_WIDE_DIR"

echo "============================================================"
echo "GENOME-WIDE COLOC JOB MONITOR"
echo "============================================================"
echo "Time: $(date)"
echo ""

# Count completed
n_total=$(wc -l < config/coloc_pair_ids.txt)
n_complete=$(ls results/coloc/*.json 2>/dev/null | wc -l)
n_pending=$((n_total - n_complete))
pct_complete=$((n_complete * 100 / n_total))

echo "Progress: $n_complete / $n_total ($pct_complete%)"
echo "  Completed: $n_complete"
echo "  Pending: $n_pending"
echo ""

# Check job status
echo "Job status (bjobs):"
bjobs -w 2>/dev/null | grep -E "gw_coloc|JOBID" | head -20
echo ""

# Check for errors
n_errors=$(grep -l "Error\|error\|ERROR" logs/coloc_*.err 2>/dev/null | wc -l)
echo "Jobs with errors: $n_errors"

if [[ $n_errors -gt 0 ]]; then
  echo ""
  echo "Error files:"
  grep -l "Error\|error\|ERROR" logs/coloc_*.err 2>/dev/null | head -10
  echo ""
  echo "Sample error:"
  grep -l "Error\|error\|ERROR" logs/coloc_*.err 2>/dev/null | head -1 | xargs tail -20 2>/dev/null
fi

# Check for successful H4 signals
if [[ $n_complete -gt 0 ]]; then
  echo ""
  echo "Preliminary results:"
  n_h4_08=$(grep -l '"PP.H4.abf": 0\.[89]' results/coloc/*.json 2>/dev/null | wc -l)
  n_h4_05=$(grep -l '"PP.H4.abf": 0\.[5-9]' results/coloc/*.json 2>/dev/null | wc -l)
  echo "  Signals with H4 > 0.8: $n_h4_08"
  echo "  Signals with H4 > 0.5: $n_h4_05"
fi

echo ""
echo "============================================================"
