# AFR Coloc Rerun Summary

## Overview
After fixing the genome build mismatch (asthma.AFR: GRCh38 → GRCh37), all 150 AFR coloc pairs have been resubmitted for analysis.

## Job Information
- **Job ID**: 49445
- **Total Jobs**: 150 AFR pairs
- **Job Type**: LSF array job
- **Memory**: 8GB per job
- **Time Limit**: 1 hour per job
- **Status**: Running (started Jan 27, 2026 13:23)

## Files and Scripts

### Input Files
- **Pair List**: `results/multitrait/afr_pairs.txt` (150 pairs)
- **Manifest**: `results/multitrait/coloc_manifest.tsv`
- **Fixed Sumstats**:
  - `data_processed/sumstats_harmonized_fixed/asthma.AFR.tsv.bgz` (GRCh37)
  - `data_processed/sumstats_harmonized_fixed/stroke.AFR.tsv.bgz` (GRCh37)
  - `data_processed/sumstats_harmonized_fixed/t2d.AFR.tsv.bgz` (GRCh37)

### Scripts
- **Batch Submission**: `scripts/run_afr_coloc_batch.sh`
- **Monitor Progress**: `scripts/monitor_afr_coloc.sh`
- **Regenerate Summaries**: `scripts/regenerate_coloc_summaries.sh`
- **Liftover Script**: `scripts/liftover_asthma_afr.sh`
- **Position Diagnostic**: `scripts/diagnostics/check_position_alignment.sh`

### Output Files
- **Coloc Results**: `results/multitrait/coloc/*AFR*.json`
- **Logs**: `logs/afr_coloc_*.{out,err}`

## Monitoring Progress

### Quick Status Check
```bash
bash scripts/monitor_afr_coloc.sh 49445
```

### Detailed Job Status
```bash
bjobs -w 49445
```

### Check Specific Job
```bash
# View output
tail logs/afr_coloc_<N>.out

# View errors/warnings
tail logs/afr_coloc_<N>.err
```

### Count Completed Results
```bash
ls -1 results/multitrait/coloc/*AFR*asthma*.json 2>/dev/null | wc -l
```

## After Jobs Complete

### 1. Regenerate Summaries
```bash
bash scripts/regenerate_coloc_summaries.sh
```

This will:
- Count completed coloc results
- Generate `results/multitrait/coloc_summary.tsv`
- Generate `results/multitrait/coloc_summary_augmented.tsv` (with QC flags)
- Display high-confidence AFR signals (H4 > 0.5)

### 2. View High-Confidence Results
```bash
# H4 > 0.5
awk -F'\t' 'NR==1 || ($3=="AFR" && $7 > 0.5)' \
  results/multitrait/coloc_summary_augmented.tsv | column -t

# H4 > 0.8 (very high confidence)
awk -F'\t' 'NR==1 || ($3=="AFR" && $7 > 0.8)' \
  results/multitrait/coloc_summary_augmented.tsv | column -t
```

### 3. Check Specific Region
```bash
# Example: APOE region
grep "APOE_19q13__AFR" results/multitrait/coloc_summary_augmented.tsv
```

## Expected Improvements

### Before Liftover (Genome Build Mismatch)
- **asthma ∩ stroke**: 17 variants (0.5%)
- **asthma ∩ t2d**: 87 variants (0.8%)
- **stroke ∩ t2d**: 2,960 variants (91.9%)

### After Liftover (All GRCh37)
- **asthma ∩ stroke**: 3,111 variants (96.6%) ⬆️
- **asthma ∩ t2d**: 8,736 variants (82.1%) ⬆️
- **stroke ∩ t2d**: 2,960 variants (91.9%) ✓

With 96%+ overlap, we now expect:
- Meaningful H4 posterior probabilities for true colocalization
- Reduced false negatives from sparse overlap
- More reliable multi-trait colocalization signals

## Genome Build Verification

All three traits are now confirmed to be on **GRCh37** (hg19):

```bash
# Verify alignment (should show all on GRCh37)
bash scripts/diagnostics/check_position_alignment.sh
```

Expected output:
```
=== GENOME BUILD CHECK ===
  asthma.AFR: Found at POS=45411941 (GRCh37)
  stroke.AFR: Found at POS=45411941 (GRCh37)
  t2d.AFR:    Found at POS=45411941 (GRCh37)
```

## Backup Files

Original GRCh38 version of asthma.AFR preserved:
- `data_processed/sumstats_harmonized_fixed/asthma.AFR.grch38_backup.tsv.bgz`

## Troubleshooting

### Jobs Failing
Check error logs:
```bash
grep -l "Error\|FAILED" logs/afr_coloc_*.err | head -10
```

### Missing Results
If some pairs didn't complete, identify and rerun:
```bash
# Find missing pairs
comm -13 \
  <(ls results/multitrait/coloc/*AFR*asthma*.json | xargs -n1 basename | sed 's/.json//' | sort) \
  <(grep "AFR.*asthma" results/multitrait/coloc_manifest.tsv | cut -f10 | sort) \
  > missing_pairs.txt

# Rerun specific pair
PAIR_ID="<pair_id_from_missing_pairs.txt>"
conda activate la_multitrait_r
Rscript scripts/run_coloc.R \
  --manifest results/multitrait/coloc_manifest.tsv \
  --pair-id "$PAIR_ID" \
  --output "results/multitrait/coloc/${PAIR_ID}.json"
```

## Next Steps

1. **Monitor** job completion (1-2 hours for 150 jobs)
2. **Regenerate** summaries when all jobs complete
3. **Analyze** high-confidence colocalization signals
4. **Compare** results to previous run (should see more signals)
5. **Validate** top hits with biological knowledge

## Contact
For questions about this rerun, refer to:
- Liftover details: `scripts/liftover_asthma_afr.sh`
- Position alignment diagnostic: `scripts/diagnostics/check_position_alignment.sh`
