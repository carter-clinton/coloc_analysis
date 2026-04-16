# Phase 4 Smoke Pilot (A-1 Calibration Gate)

**Status:** Wired -- awaiting LSF execution
**Date wired:** 2026-04-16
**Pilot scope:** t2d x TCF7L2_10q25_2 x 5 bootstraps

## Purpose

Gate the full ~100k-fit production launch on empirical timing data from a
single trait x region x 5 bootstraps. Validates the complete pipeline:

    bootstrap_driver.py -> run_susie_rss.R (SuSiE refit) -> run_matched_coloc.R (coloc.susie)

## Execution Command

```bash
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
    --profile config/cluster_lsf \
    --use-conda \
    -s Snakefile \
    results/matched_n/SMOKE_PILOT_REPORT.md
```

This triggers:
- 5x `run_matched_bootstrap` (SE-inflation + SuSiE refit per D-01b)
- 5x `run_matched_coloc` (coloc.susie with fixed AFR .fit.rds per D-01c)
- 1x `smoke_pilot_bootstrap` (aggregates timing + convergence into report)

## GO/NO-GO Criteria

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| SuSiE convergence | 5/5 fits converge | Any non-convergence -> investigate LD or sumstats |
| Wall-clock per bootstrap | < 5 min | If > 5 min, check LD matrix size + SuSiE L parameter |
| PP.H4 stability | Range < 0.3 across 5 bootstraps | Wild variance -> bootstrap noise dominates signal |
| Extrapolated total | < 14 days at 1024 concurrent LSF slots | If > 14 days, reduce scope (NOT bootstrap_n, OSF-locked at 100) |

## Extrapolation Formula

```
total_wall_clock = wall_clock_per_bootstrap * total_fits / lsf_concurrent_slots
total_fits = bootstrap_n (100) * n_traits (5) * n_regions (~200) = ~100,000
lsf_concurrent_slots = 1024 (NCSU LSF standard queue)
```

## Possible Outcomes

1. **GO**: All criteria met -> proceed to full `snakemake all_matched_n` launch
2. **GO with topology adjustment**: convergence OK but wall-clock > 5 min -> adjust LSF mem/time per rule
3. **NO-GO: convergence failure**: SuSiE does not converge -> investigate LD matrix conditioning / increase max_iter
4. **NO-GO: wall-clock > 14 days**: Reduce region count (not bootstrap_n per OSF pre-reg). Consider: (a) restrict to Tier A loci only (not A+B), (b) restrict to top 100 regions by Phase 2 PP.H4

## Notes

- `bootstrap_n` is OSF-pinned at 100 per pre-registration. Do NOT reduce below 100.
- Pilot region TCF7L2_10q25_2 is the strongest T2D positive control (PP.H4 ~ 1.0 across ancestries per Phase 9 smoke).
- AFR .fit.rds for t2d at this region must exist from Phase 1 first-production before the pilot can run.
