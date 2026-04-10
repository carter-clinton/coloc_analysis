# AFR Coloc Results Analysis - Post Genome Build Fix

**Date**: January 27, 2026
**Job ID**: 49445
**Status**: Complete

## Executive Summary

After fixing the critical genome build mismatch (asthma.AFR GRCh38 → GRCh37), we reran colocalization analysis for 150 AFR ancestry pairs across three traits (asthma, stroke, t2d). While variant overlap improved dramatically (0.5% → 96.6%), **colocalization signals remain weak**, with only **1 signal achieving H4 > 0.10**.

## Key Findings

### 1. Job Completion
- **Total Submitted**: 150 AFR pairs
- **Successfully Completed**: 139 (92.7%)
- **Failed**: 6 (4.0%) - duplicated SNPs in asthma dataset
- **Missing**: 5 (3.3%)

### 2. Genome Build Fix Impact

**Variant Overlap (APOE region chr19:45000000-46500000)**

| Trait Pair | Before Fix | After Fix | Improvement |
|------------|-----------|----------|-------------|
| asthma ∩ stroke | 17 (0.5%) | 3,111 (96.6%) | **184x** |
| asthma ∩ t2d | 87 (0.8%) | 8,736 (82.1%) | **103x** |
| stroke ∩ t2d | 2,960 (91.9%) | 2,960 (91.9%) | ✓ (already aligned) |

**Build Status (Confirmed GRCh37)**
- ✓ asthma.AFR: APOE rs429358 at position 45411941 (GRCh37)
- ✓ stroke.AFR: APOE rs429358 at position 45411941 (GRCh37)
- ✓ t2d.AFR: APOE rs429358 at position 45411941 (GRCh37)

### 3. Colocalization Results

**H4 Posterior Probability Distribution (144 AFR pairs)**

| H4 Threshold | Count | Percentage |
|-------------|-------|------------|
| H4 > 0.5 (strong) | 0 | 0.0% |
| H4 > 0.2 (moderate) | 0 | 0.0% |
| H4 > 0.1 (suggestive) | 1 | 0.7% |
| H4 > 0.05 (weak) | 2 | 1.4% |
| H4 ≤ 0.05 (minimal) | 141 | 97.9% |

**Top 10 AFR Signals (Ranked by H4)**

| Rank | Region | Traits | H4 | H3 | n_SNPs |
|------|--------|--------|----|----|--------|
| 1 | TCF7L2_10q25 | stroke vs t2d | 0.1523 | 0.0790 | 1,215 |
| 2 | HNF1A_12q24.31 | stroke vs t2d | 0.0546 | 0.0396 | 516 |
| 3 | PPARG_3p25 | stroke vs t2d | 0.0530 | 0.1230 | 1,437 |
| 4 | SLC30A8_8q24.11 | stroke vs t2d | 0.0489 | 0.0936 | 1,193 |
| 5 | ORMDL3_GSDMB_17q12q21 | stroke vs t2d | 0.0489 | 0.1636 | 2,399 |
| 6 | ATP2B1_12q21.33 | stroke vs t2d | 0.0479 | 0.0500 | 764 |
| 7 | ORMDL3_GSDMB_17q12q21 | asthma vs t2d | 0.0469 | 0.4256 | 8,330 |
| 8 | SLC30A8_8q24.11 | asthma vs t2d | 0.0460 | 0.2084 | 3,594 |
| 9 | BMI_5q13.3 | asthma vs t2d | 0.0459 | 0.1701 | 23,521 |
| 10 | IRS1_2q36 | stroke vs t2d | 0.0457 | 0.0782 | 1,077 |

**Notable Finding**: The only suggestive signal (H4 > 0.10) is **TCF7L2** for stroke vs t2d, a known type 2 diabetes gene.

### 4. Breakdown by Trait Pair

| Trait Pair | Total Pairs | H4 > 0.05 | Strongest Signal |
|------------|-------------|-----------|-----------------|
| AFR asthma vs stroke | 45 | 0 | TMEM18_2p25 (H4=0.0396) |
| AFR asthma vs t2d | 49 | 0 | ORMDL3_GSDMB (H4=0.0469) |
| AFR stroke vs t2d | 50 | 3 | TCF7L2 (H4=0.1523) |

**Key Observation**: Stroke vs t2d shows the strongest signals, while asthma-related pairs show minimal colocalization despite improved overlap.

## Failed Jobs

Six jobs failed due to **duplicated SNPs in asthma dataset**:

1. BMI_5q13.3__AFR__asthma_vs_stroke
2. FADS1_11q12__AFR__asthma_vs_stroke
3. GPRC5B_16p12.3__AFR__asthma_vs_stroke
4. GPRC5B_16p12.3__AFR__asthma_vs_t2d
5. PCSK9_1p32__AFR__asthma_vs_stroke
6. SLC4A7_3p24__AFR__asthma_vs_stroke

**Action Needed**: The asthma.AFR dataset requires deduplication before these regions can be analyzed.

## Interpretation & Discussion

### Why Are AFR Signals Weak Despite Fixed Overlap?

The genome build fix successfully aligned positions across traits, increasing variant overlap from <1% to >80-95%. However, colocalization signals remain weak. Possible explanations:

1. **True Biological Differences**
   - Different genetic architectures between AFR and EUR populations
   - Population-specific causal variants not shared across traits
   - Different LD structures affecting signal detection

2. **Statistical Power**
   - AFR GWAS typically have smaller sample sizes than EUR GWAS
   - Reduced power to detect shared signals
   - Winner's curse affecting replication

3. **Trait-Specific Patterns**
   - Stroke vs t2d shows strongest signals (metabolic overlap)
   - Asthma shows minimal colocalization with other traits
   - May reflect limited genetic overlap between respiratory and metabolic traits in AFR

4. **Data Quality Issues**
   - Duplicated SNPs in asthma dataset (6 regions failed)
   - May indicate broader QC issues affecting power

### Comparison to EUR Results

While we haven't done a formal comparison, the EUR results show much stronger colocalization signals (multiple H4 > 0.9), suggesting:
- Better powered EUR GWAS enable stronger signal detection
- More shared genetic architecture in EUR populations
- Or methodological differences in GWAS quality between ancestries

## Files Generated

### Summary Files
- [results/multitrait/coloc_summary_new.tsv](results/multitrait/coloc_summary_new.tsv) - Complete summary (439 pairs)
- [results/multitrait/afr_pairs.txt](results/multitrait/afr_pairs.txt) - List of 150 AFR pairs

### Scripts
- [scripts/run_afr_coloc_batch.sh](scripts/run_afr_coloc_batch.sh) - Batch submission script
- [scripts/monitor_afr_coloc.sh](scripts/monitor_afr_coloc.sh) - Progress monitoring
- [scripts/simple_coloc_summary.sh](scripts/simple_coloc_summary.sh) - Summary generator
- [scripts/liftover_asthma_afr.sh](scripts/liftover_asthma_afr.sh) - Genome build liftover
- [scripts/diagnostics/check_position_alignment.sh](scripts/diagnostics/check_position_alignment.sh) - Position diagnostics

### Result Files
- 144 JSON files in [results/multitrait/coloc/](results/multitrait/coloc/)
- 150 log files in [logs/](logs/)

## Recommendations

### Immediate Actions
1. **Deduplicate asthma.AFR dataset** to enable analysis of 6 failed regions
2. **Investigate TCF7L2** signal (H4=0.15) - highest AFR signal
3. **Compare to old results** (pre-fix) to quantify impact of genome build correction

### Future Analyses
1. **Conditional analysis** - Use H3 signals to identify independent associations
2. **Fine-mapping** - Focus on top regions (TCF7L2, HNF1A, PPARG)
3. **Cross-ancestry comparison** - Formally compare AFR vs EUR colocalization
4. **Sample size analysis** - Quantify power differences between ancestries
5. **Functional follow-up** - Investigate biological mechanisms for top hits

### Quality Control
1. **SNP deduplication** - Implement systematic deduplication for all traits
2. **Genome build verification** - Add automated checks to workflow
3. **Position validation** - Regular monitoring of alignment across traits

## Conclusions

The genome build fix was **critical and successful** - it corrected a fundamental data alignment issue that would have produced completely unreliable results. The 100x+ improvement in variant overlap validates the fix.

However, the **weak colocalization signals** in AFR ancestry suggest:
- Either limited shared genetic architecture for these trait combinations in AFR populations
- Or statistical power limitations due to smaller AFR GWAS sample sizes

The strongest signal (**TCF7L2** for stroke vs t2d, H4=0.15) is biologically plausible given TCF7L2's established role in diabetes, but falls short of conventional thresholds for strong colocalization (H4 > 0.5).

**Bottom Line**: The genome build issue is resolved, data quality is improved, but biological signals remain weak. Consider expanding to larger AFR GWAS or focusing on EUR analyses where power is greater.

---

For questions or additional analyses, see:
- [AFR_COLOC_RERUN_SUMMARY.md](AFR_COLOC_RERUN_SUMMARY.md) - Workflow documentation
- Job logs in `logs/afr_coloc_*.{out,err}`
