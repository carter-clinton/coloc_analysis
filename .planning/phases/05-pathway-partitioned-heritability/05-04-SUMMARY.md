---
phase: 05-pathway-partitioned-heritability
plan: 04
subsystem: pathway
tags: [hess, rho-hess, local-genetic-covariance, python27, subprocess, snakemake]

# Dependency graph
requires:
  - phase: 05-pathway-partitioned-heritability
    plan: 02
    provides: "MAGMA wrapper, g:Profiler wrapper, 9 working Snakemake rules"
  - phase: 05-pathway-partitioned-heritability
    plan: 03
    provides: "LDSC partitioned h2 wrapper, LDSC-SEG wrapper, 9 Snakemake rules, sumstats_utils.py"
provides:
  - "HESS/rho-HESS wrapper (local-rhog/combine/compare steps) with Python 2.7 subprocess invocation"
  - "Harmonized-to-HESS format conversion with Z=BETA/SE and effective N"
  - "Pleiotropic vs background z-score comparison (D-02c)"
  - "GRCh37 genome build validation for HESS LD panel (T-05-17)"
  - "7 new Snakemake rules replacing 1 HESS placeholder (validate_panel, format_sumstats, local_rhog, combine, compare_pleio, negative_controls, aggregate)"
  - "TRAIT_PAIRS generation with shared ancestry filtering (10 pairs from 5 traits)"
  - "81 passing Phase 5 tests (9 new HESS tests)"
affects: [05-05-aggregation-permutation]

# Tech tracking
tech-stack:
  added: [hess-rho-hess, python27-subprocess-invocation]
  patterns: [subprocess-list-args, z-score-enrichment-test, trait-pair-generation, shared-ancestry-filtering, grch37-build-validation]

key-files:
  created:
    - src/python/run_hess.py
    - tests/phase5/test_hess.py
  modified:
    - src/snakemake/rules/pathway.smk

key-decisions:
  - "Python 2.7 HESS invoked via subprocess with list args only (T-05-18 / no shell=True)"
  - "Z = BETA/SE with NaN rejection and positive-N validation (T-05-19)"
  - "GRCh37 build validation via hardcoded reference SNP positions (T-05-17)"
  - "Pleiotropic vs background z-score = (mean_pleio - mean_bg) / pooled_SE (D-02c)"
  - "TRAIT_PAIRS computed at Snakemake load time from config trait_ancestries intersection"
  - "hess_py27 conda env for HESS rules; magma env for Python 3 format/compare steps"

patterns-established:
  - "HESS subprocess pattern: Python 3 wrapper invokes Python 2.7 via explicit path"
  - "Enrichment comparison pattern: partition overlap -> classify -> z-score test"
  - "Trait pair pattern: C(5,2) = 10 pairs, filtered by shared ancestry availability"

requirements-completed: [REQ-7]

# Metrics
duration: 6min
completed: 2026-04-13
---

# Phase 5 Plan 4: HESS/rho-HESS Local Genetic Covariance Summary

**HESS/rho-HESS local genetic covariance wrapper with Python 2.7 subprocess invocation, Z=BETA/SE format conversion, pleiotropic vs background z-score enrichment test (D-02c), and GRCh37 build validation**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-13T21:00:07Z
- **Completed:** 2026-04-13T21:06:38Z
- **Tasks:** 2/2
- **Files modified:** 3

## Accomplishments

- Created run_hess.py: 3-step CLI wrapper (local-rhog, combine, compare) with Python 2.7 subprocess invocation via explicit python27 path, harmonized_to_hess() format conversion computing Z=BETA/SE with NaN rejection, compare_pleiotropic_vs_background() z-score enrichment test partitioning HESS output by overlap with regions_curated.csv, validate_hess_panel_build() GRCh37 position checks
- Replaced 1 HESS placeholder Snakemake rule with 7 working rules: hess_validate_panel (one-time build check), hess_format_sumstats (per trait x ancestry), hess_local_rhog (per pair x ancestry x chromosome with hess_py27 conda env), hess_combine (per pair x ancestry), hess_compare_pleio (per pair x ancestry), hess_negative_controls (REQ-7), hess_aggregate (summary table)
- Added TRAIT_PAIRS generation to pathway.smk: computes 10 unique pairs from 5 traits, filters by shared ancestry (intersection of trait_ancestries), generates wildcard lists for expand()
- 81 Phase 5 tests passing (9 new: format columns, Z-score computation, effective N, pleio vs bg comparison, trait pair generation, shared ancestry filtering, build validation correct, build validation wrong, no shell=True AST check)

## Task Commits

Each task was committed atomically:

1. **Task 1: HESS/rho-HESS wrapper script** - `7d83d3a` (feat)
2. **Task 2: HESS Snakemake rules + 9 unit tests** - `df07a69` (feat)

## Files Created/Modified

- `src/python/run_hess.py` - HESS 3-step wrapper: local-rhog, combine, compare with Py2.7 subprocess, format conversion, enrichment z-score
- `src/snakemake/rules/pathway.smk` - 7 new HESS rules replacing 1 placeholder + TRAIT_PAIRS generation block
- `tests/phase5/test_hess.py` - 9 tests: format, Z-score, effective N, pleio vs bg, pair generation, ancestry filtering, build validation, shell=True check

## Decisions Made

- Python 2.7 HESS invoked via subprocess.run([python27_path, hess_script, ...]) with list args only -- no shell=True anywhere in run_hess.py (T-05-18 mitigation, verified by AST-based test)
- Z-score computed as BETA/SE with explicit NaN/Inf rejection; N validated as positive integer (T-05-19)
- GRCh37 validation checks 5 hardcoded reference SNP positions (rs1, rs12, rs334, rs7412, rs429358) against known GRCh37 coordinates (T-05-17)
- Pleiotropic vs background comparison: partition overlap detection -> split -> mean covariance per group -> z = (mean_pleio - mean_bg) / sqrt(se_pleio^2 + se_bg^2) -> two-sided p-value
- TRAIT_PAIRS computed at Snakemake module load time using intersection of trait_ancestries; underscore-prefixed loop vars avoid namespace pollution
- hess_py27 conda env for rules that invoke HESS (local_rhog, combine); magma env (Python 3) for format conversion and comparison steps

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing] Added hess_negative_controls rule**
- **Found during:** Task 2
- **Issue:** Plan specified `rule hess_negative_controls` in must_haves truths but did not include it in the task action
- **Fix:** Added rule that compares local covariance at negative control loci (REQ-7 / D-06b compliance)
- **Files modified:** src/snakemake/rules/pathway.smk
- **Commit:** df07a69

## Known Stubs

| Stub | File | Reason |
|------|------|--------|
| 2 placeholder `pass` rules | src/snakemake/rules/pathway.smk | Intentional: permutation_null and aggregate_pathway_results for Plan 05-05 |

These stubs are intentional infrastructure for Plan 05-05 and do not block Plan 04's goal.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HESS/rho-HESS pipeline fully implemented (format, local-rhog, combine, compare, aggregate)
- 1 remaining placeholder set (permutation + aggregation) ready for Plan 05-05
- Plan 05-05 (aggregation + permutation null) can proceed immediately
- All 81 Phase 5 tests provide regression safety

## Self-Check: PASSED

- 2/2 created files found (run_hess.py, test_hess.py)
- 1/1 modified files verified (pathway.smk)
- 2/2 task commits found (7d83d3a, df07a69)
- 81/81 tests passing

---
*Phase: 05-pathway-partitioned-heritability*
*Completed: 2026-04-13*
