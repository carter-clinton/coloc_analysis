#!/bin/bash
# RECOVERY Stage 2 follow-up — force-rebuild aggregators after fire_phase2_stage2_refit.sh.
#
# Reason: the per-id qtl_coloc JSONs are not declared as inputs to
# aggregate_qtl_coloc (intentional — see qtl_coloc.smk:336-347), so refreshing
# 22 qtl_coloc JSONs does NOT trigger aggregate_qtl_coloc -> assign_tiers ->
# pph4_threshold_sweep re-derivation. Same gap exists for Phase-1 and
# multitrait aggregators (filter_finemap_summary, summarize_coloc_results).
#
# This script:
#   1. Waits for the primary fire driver PID to exit (argv[1] or auto-detect).
#   2. Verifies the driver exit was clean (log lacks LockException / Error).
#   3. Fires snakemake with --forcerun on each aggregator whose output is
#      now stale-by-design relative to the refreshed per-id artifacts.
#
# Usage:
#   bash bin/followup_phase2_stage2_aggregators.sh <primary_driver_pid>
#
# Outputs: logs/phase2_stage2_followup_<ts>.log

set -euo pipefail

PRIMARY_PID="${1:?primary driver PID required}"
export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
FOLLOWUP_LOG="logs/phase2_stage2_followup_$(date +%Y%m%d_%H%M%S).log"

echo "[$(date +%H:%M:%S)] Waiting for primary driver PID $PRIMARY_PID to exit..." \
  | tee -a "$FOLLOWUP_LOG"

# Poll until PID is gone. Driver is disown'd so `wait` won't work.
while kill -0 "$PRIMARY_PID" 2>/dev/null; do
  sleep 30
done

echo "[$(date +%H:%M:%S)] Primary driver PID $PRIMARY_PID exited." \
  | tee -a "$FOLLOWUP_LOG"

# Locate the primary log (most recent phase2_stage2_refit log).
PRIMARY_LOG=$(ls -t logs/phase2_stage2_refit_*.log 2>/dev/null | head -1)
echo "[$(date +%H:%M:%S)] Primary log: $PRIMARY_LOG" | tee -a "$FOLLOWUP_LOG"

if grep -qE "LockException|WorkflowError|exited with non-zero|Complete log.*Killed" "$PRIMARY_LOG" 2>/dev/null; then
  echo "[$(date +%H:%M:%S)] Primary log contains errors — ABORTING follow-up." \
    | tee -a "$FOLLOWUP_LOG"
  grep -E "LockException|WorkflowError|exited with non-zero|Error" "$PRIMARY_LOG" | head -20 \
    | tee -a "$FOLLOWUP_LOG"
  exit 1
fi

# Summary of primary run.
echo "[$(date +%H:%M:%S)] Primary run tail:" | tee -a "$FOLLOWUP_LOG"
tail -5 "$PRIMARY_LOG" | tee -a "$FOLLOWUP_LOG"

echo "[$(date +%H:%M:%S)] Firing aggregator --forcerun..." | tee -a "$FOLLOWUP_LOG"

# Note: pph4_threshold_sweep.tsv is output of BOTH assign_tiers (qtl_coloc.smk)
# and a separate pph4_threshold_sweep rule (negative_controls.smk) — the latter
# reads a non-existent qtl_coloc_aggregated.tsv. We force assign_tiers only,
# which produces both tier_assignments.tsv and pph4_threshold_sweep.tsv. Do not
# list pph4_threshold_sweep.tsv as a target — snakemake picks the broken rule.
"$SMK" \
  --profile config/cluster_lsf \
  --rerun-triggers mtime \
  --config 'phase2_enabled_sources=["gtex_eqtl","gtex_sqtl"]' \
  --forcerun aggregate_qtl_coloc assign_tiers filter_finemap_summary summarize_coloc_results \
  --keep-going \
  results/qtl_coloc/tier_assignments.tsv \
  results/fine_mapping/finemap_tier3_coloc.tsv \
  results/multitrait/coloc_summary.tsv \
  >> "$FOLLOWUP_LOG" 2>&1

echo "[$(date +%H:%M:%S)] Follow-up complete. Log: $FOLLOWUP_LOG"
echo ""
echo "Primary outputs to inspect:"
echo "  results/qtl_coloc/tier_assignments.tsv                  (expect >=1 Tier A vs 0 baseline)"
echo "  results/qtl_coloc/pph4_threshold_sweep.tsv              (side-output of assign_tiers)"
echo "  results/fine_mapping/finemap_tier3_coloc.tsv            (coloc-promoted loci)"
echo "  results/fine_mapping/finemap_tier1_high_conf.tsv"
echo "  results/fine_mapping/finemap_tier2_relaxed.tsv"
echo "  results/fine_mapping/finemap_summary_augmented.tsv"
echo "  results/multitrait/coloc_summary.tsv                    (expect SH2B3 PP.H4=1.0)"
