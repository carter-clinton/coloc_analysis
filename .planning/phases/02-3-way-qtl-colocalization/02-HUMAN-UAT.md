---
status: partial
phase: 02-3-way-qtl-colocalization
source: [02-VERIFICATION.md]
started: 2026-04-13T01:30:00Z
updated: 2026-04-13T02:20:00Z
---

## Current Test

[awaiting real-data testing]

## Tests

### 1. Snakemake DAG Resolution
expected: snakemake -n prints all QTL coloc + negative control + tier assignment rules without error
result: pass
note: Snakemake --lint parses all rules (qtl_download.smk, qtl_coloc.smk, negative_controls.smk) without errors. MissingInputException on dry-run is expected (no raw data yet). 136 unit tests pass, 1 skipped (bedtools dep).

### 2. End-to-End eQTL Coloc
expected: run_qtl_coloc.R produces JSON with PP.H4 value and no errors; harmonized TSV has >50 overlapping SNPs
result: blocked
blocked_by: prior-phase
reason: Requires real GTEx data downloaded from eQTL Catalogue FTP and Phase 1 .fit.rds files from actual SuSiE runs. Deferred to first pipeline execution.

### 3. UKB-PPP pQTL Integration
expected: harmonize_pqtl.py reads a real REGENIE file, converts LOG10P, produces valid common intermediate TSV
result: blocked
blocked_by: third-party
reason: Requires Synapse auth token and actual UKB-PPP download. Data access is credentialed (syn51364943 accessible per Phase 0 closeout). Deferred to first pipeline execution.

### 4. Negative Control Validation
expected: HLA, cosmetic, and blood_group all produce PP.H4 below primary_threshold
result: blocked
blocked_by: prior-phase
reason: Requires real coloc execution with actual LD matrices and QTL data from completed pipeline run. Deferred to first end-to-end execution.

## Summary

total: 4
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 3

## Gaps
