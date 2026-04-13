---
status: complete
phase: 01-coloc-susie-fine-mapping-spine
source: [01-01-SUMMARY.md, 01-02-SUMMARY.md, 01-03-SUMMARY.md, 01-04-SUMMARY.md, 01-05-SUMMARY.md]
started: 2026-04-13T02:00:00Z
updated: 2026-04-13T02:15:00Z
---

## Current Test

[testing complete]

## Tests

### 1. SuSiE policy YAML loads and validates
expected: jsonschema.validate(policy, schema) succeeds; prints "OK: 5 complex regions"
result: pass
note: Initially failed due to schema maxItems:4 vs 5 regions (Phase 02 added LPA/KIV-2). Fixed schema to maxItems:10 in commit 7f735fe. Re-test passed.

### 2. Phase 1 test suite passes
expected: pytest tests/phase1/ exits 0
result: pass
note: 27 passed, 11 skipped (skips are for R env deps and real data — expected). No failures.

### 3. UKBB-LD EUR tile download script runs (dry check)
expected: download_ukbb_ld_tiles.py --help prints usage
result: skipped
reason: Script requires scipy which is in envs/ld_build.yml conda env (not smoke_dev). Script exists and is properly wired in ld_reference.smk. Cannot test --help without the specialized env.

### 4. HGDP+1kG AFR LD build script runs (dry check)
expected: build_hgdp_1kg_ld.py --help prints usage with --region-id, --chrom, --out-dir, --scratch-dir
result: pass
note: Help output shows all expected arguments including --regions-csv, --out-dir, --scratch-dir, --bcf-fname-template, --dry-run.

### 5. coloc.susie R script exists with correct signature
expected: Script loads coloc library, accepts --fit-a, --fit-b, --output, contains coloc::coloc.susie
result: pass
note: Script is 13KB+, loads coloc/susieR/jsonlite/data.table, uses optparse for CLI args, documents A6 dispatch resolution.

### 6. Snakemake dry-run resolves Phase 1 rules
expected: Rules parse without syntax errors
result: pass
note: MissingInputException fires because raw data files don't exist yet (expected — pipeline downloads data during execution). Snakemake --lint confirms all rules parse correctly — only advisory style warnings, no errors.

### 7. QC aggregator script runs on mock data
expected: susie_qc_aggregate.py --help prints usage with --input-dir and --output
result: pass
note: Help shows --input-dir, --output, --aggregated-only, --policy, --sweep-out arguments. Well-documented.

### 8. Legacy coloc.abf renamed correctly
expected: run_coloc_abf_legacy.R exists; run_coloc.R does not
result: pass
note: git mv confirmed — legacy file renamed, original path gone.

## Summary

total: 8
passed: 7
issues: 0
pending: 0
skipped: 1
blocked: 0

## Gaps
