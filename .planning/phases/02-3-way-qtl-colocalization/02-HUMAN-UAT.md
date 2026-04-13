---
status: partial
phase: 02-3-way-qtl-colocalization
source: [02-VERIFICATION.md]
started: 2026-04-13T01:30:00Z
updated: 2026-04-13T01:30:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Snakemake DAG Resolution
expected: snakemake -n prints all QTL coloc + negative control + tier assignment rules without error
result: [pending]

### 2. End-to-End eQTL Coloc
expected: run_qtl_coloc.R produces JSON with PP.H4 value and no errors; harmonized TSV has >50 overlapping SNPs
result: [pending]

### 3. UKB-PPP pQTL Integration
expected: harmonize_pqtl.py reads a real REGENIE file, converts LOG10P, produces valid common intermediate TSV
result: [pending]

### 4. Negative Control Validation
expected: HLA, cosmetic, and blood_group all produce PP.H4 below primary_threshold
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
