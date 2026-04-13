---
phase: 05-pathway-partitioned-heritability
plan: 02
subsystem: pathway
tags: [magma, gprofiler, enrichment, fdr, background, snakemake, subprocess]

# Dependency graph
requires:
  - phase: 05-pathway-partitioned-heritability
    plan: 01
    provides: "Conda envs, GMT pathway gene sets, utility scripts, pathway.smk skeleton, sumstats_utils.py"
  - phase: 02-qtl-colocalization
    provides: "Tier assignments, harmonized sumstats, assign_tiers.py"
provides:
  - "MAGMA 3-step wrapper (annotate/gene/geneset) with binary trait effective-N"
  - "g:Profiler enrichment wrapper with REST API + R fallback + IEA exclusion"
  - "5-trait union background gene list builder (500kb window, D-03a/Reimand 2019)"
  - "MAGMA Snakemake rules: annotate, build_set_file, gene_analysis, geneset_analysis, fdr"
  - "g:Profiler Snakemake rules: build_background, extract_tier_ab_genes, enrichment, negative_controls"
  - "53 passing Phase 5 tests (18 new: 7 MAGMA + 11 g:Profiler)"
affects: [05-05-aggregation-permutation]

# Tech tracking
tech-stack:
  added: [requests-http, statsmodels-multipletests]
  patterns: [subprocess-list-args, exponential-backoff-retry, temp-file-cleanup, effective-N-binary-traits]

key-files:
  created:
    - src/python/run_magma.py
    - src/python/build_gprofiler_bg.py
    - src/python/run_gprofiler.py
  modified:
    - src/snakemake/rules/pathway.smk
    - tests/phase5/test_magma_geneset.py
    - tests/phase5/test_gprofiler.py

key-decisions:
  - "requests imported at module level with try/except fallback for test mockability"
  - "MAGMA annotate runs once per genome build (not per trait) for efficiency"
  - "MAGMA FDR correction via statsmodels multipletests BH method (joint across all gene sets per trait)"
  - "g:Profiler REST API as default with R fallback; no_iea=True for electronic annotation exclusion"

patterns-established:
  - "Subprocess list args pattern: all MAGMA calls use list arguments, never shell=True (T-05-05)"
  - "Temp file pattern: pval file created, used, cleaned up in finally block (T-05-11)"
  - "API retry pattern: 3 attempts with exponential backoff [2s, 4s, 8s] and response validation (T-05-12)"
  - "Background construction: 5-trait union with interval merge + gene intersection (D-03a)"

requirements-completed: [REQ-7]

# Metrics
duration: 11min
completed: 2026-04-13
---

# Phase 5 Plan 2: MAGMA + g:Profiler Analysis Summary

**MAGMA 3-step enrichment pipeline with binary trait effective-N and g:Profiler functional enrichment with 500kb discoverability-matched background, IEA exclusion, and API retry logic**

## Performance

- **Duration:** 11 min
- **Started:** 2026-04-13T20:34:35Z
- **Completed:** 2026-04-13T20:45:35Z
- **Tasks:** 2/2
- **Files modified:** 6

## Accomplishments
- Created run_magma.py: MAGMA 3-step wrapper (annotate/gene/geneset) with subprocess list args (T-05-05), binary trait effective-N computation (Pitfall 4), temp pval file cleanup (T-05-11)
- Created build_gprofiler_bg.py: 5-trait union background gene list builder with 500kb window extension, interval merging, gene intersection (D-03a/Reimand 2019)
- Created run_gprofiler.py: REST API mode with HTTPS enforcement (T-05-08), IEA exclusion (D-03b), 3x retry with exponential backoff (T-05-12), response schema validation; R fallback mode via gprofiler2
- Replaced 4 placeholder Snakemake rules with 9 working rules: 5 MAGMA rules (annotate, build_set_file, gene_analysis, geneset_analysis, fdr) + 4 g:Profiler rules (build_background, extract_tier_ab_genes, enrichment, negative_controls)
- 53 Phase 5 tests passing (18 new tests validating command construction, effective-N, pval format, background windows, IEA exclusion, retry logic, response validation, interval merging)

## Task Commits

Each task was committed atomically:

1. **Task 1: MAGMA 3-step wrapper + Snakemake rules** - `641f1b6` (feat)
2. **Task 2: g:Profiler background builder + enrichment wrapper + Snakemake rules** - `7e8bc5b` (feat)

## Files Created/Modified
- `src/python/run_magma.py` - MAGMA 3-step wrapper: annotate, gene analysis (with effective-N), gene-set analysis
- `src/python/build_gprofiler_bg.py` - 5-trait union background gene list builder (500kb window, P<5e-8)
- `src/python/run_gprofiler.py` - g:Profiler enrichment wrapper (REST API + R fallback, IEA exclusion, retry)
- `src/snakemake/rules/pathway.smk` - 9 working MAGMA + g:Profiler rules replacing 4 placeholders
- `tests/phase5/test_magma_geneset.py` - 7 new tests: annotate cmd, effective-N, pval format
- `tests/phase5/test_gprofiler.py` - 11 new tests: background, IEA flag, retry, validation, interval merge

## Decisions Made
- Module-level `requests` import with try/except fallback for test mockability (avoids import-time failure when requests not installed)
- MAGMA annotate runs once per genome build (shared across traits) rather than per trait x ancestry
- FDR correction uses statsmodels `multipletests` with BH method for joint correction across all gene sets per trait (D-01a/D-01b)
- g:Profiler REST API as default mode with R gprofiler2 as fallback; electronic annotation exclusion enabled by default per D-03b

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] requests module import not mockable at function level**
- **Found during:** Task 2 test execution
- **Issue:** `requests` was imported inside `run_enrichment_api()` function, making `patch("run_gprofiler.requests")` fail with `AttributeError`
- **Fix:** Moved `import requests` to module level with `try/except ImportError` fallback; runtime check inside function
- **Files modified:** src/python/run_gprofiler.py
- **Verification:** All 16 g:Profiler tests pass including mock-based API tests
- **Committed in:** 7e8bc5b (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking issue)
**Impact on plan:** Auto-fix necessary for test mockability. No scope creep.

## Known Stubs

| Stub | File | Reason |
|------|------|--------|
| 6 placeholder `pass` rules | src/snakemake/rules/pathway.smk | Intentional: LDSC, HESS, permutation rules for Plans 05-03 through 05-05 |

These stubs are intentional infrastructure for future plans and do not block Plan 02's goal.

## Issues Encountered
None beyond the auto-fixed blocking issue documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- MAGMA and g:Profiler analysis pipelines fully implemented
- 6 remaining placeholder rules (LDSC munge, partitioned h2, LDSC-SEG, HESS, permutation, aggregation) ready for Plans 05-03 through 05-05
- Plan 05-03 (LDSC partitioned heritability) can proceed immediately
- All 53 Phase 5 tests provide regression safety

## Self-Check: PASSED

- 3/3 created files found (run_magma.py, build_gprofiler_bg.py, run_gprofiler.py)
- 3/3 modified files verified (pathway.smk, test_magma_geneset.py, test_gprofiler.py)
- 2/2 task commits found (641f1b6, 7e8bc5b)
- 53/53 tests passing

---
*Phase: 05-pathway-partitioned-heritability*
*Completed: 2026-04-13*
