---
status: partial
phase: 09-replication-in-independent-cohorts
source: [09-VERIFICATION.md]
started: 2026-04-14T04:45:00Z
updated: 2026-04-14T04:45:00Z
---

## Current Test

[awaiting human testing — deferred to first real-data execution window, likely concurrent with Phase 9 smoke run alongside deferred Phase 5 smoke items DEF-RO7-01/02/03]

## Tests

### 1. Execute full Phase 9 Snakemake DAG end-to-end on real cohort sumstats
**expected:** Four D-07 artifacts (master_table.tsv, cross_ancestry_generalization_tier_ab.tsv, cojo_sensitivity.tsv, replication_holdout_supplementary.tsv) materialize with populated per-cohort replication columns. At least 2 cohort replications completed per SC#1. Replication-adjusted (FIQT + post-hoc-powered) effect sizes computed per SC#2. Hold-out table generated per SC#3.
**result:** [pending]

### 2. Scientific Layer 3: HLA negative control check
**expected:** ≥ 70% of HLA-region signals (chr6:28-33Mb) fail the joint criterion (`replicated_joint_0.8 == False`) in ≥ 3 of 4 cohort groups after real-data master_table.tsv is populated.
**result:** [pending]

### 3. COJO N=503 caveat narrative WARN emission
**expected:** Both `docs/methods/phase9_replication.md` narrative (verified present) and the `run_cojo.sh` stderr WARN (verified present via `4000` + `WARN` literals) surface the caveat when real 1000G EUR/AFR panels are used in live GCTA invocation.
**result:** [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

[none — pipeline infrastructure is complete and verified; outstanding items are execution-dependent, not code-dependent]
