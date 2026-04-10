---
phase: 00-data-access-infrastructure
plan: 04
subsystem: infra
tags: [snakemake, ci, smoke-test, testing, lsf, tabix, regression-testing]

# Dependency graph
requires:
  - "00-01: config/pipeline.yaml, config/datasets.yaml, envs/*.yml, schemas"
  - "00-03: Snakefile, src/snakemake/rules/*.smk, config/regions_curated.csv"
provides:
  - "tests/toy_3locus/Snakefile.test: smoke test Snakefile reusing production rules (D-15)"
  - "tests/toy_3locus/config_test.yaml: override config for toy data paths (D-15)"
  - "tests/toy_3locus/data/regions_toy.csv: 3 toy locus definitions (D-14)"
  - "tests/toy_3locus/expected/expected_results.yaml: expected PP.H4 values for regression (D-16)"
  - "scripts/subset_toy_loci.py: utility to create toy sumstats subsets from full data"
  - "scripts/run_ci_smoke.sh: LSF cron wrapper for scheduled CI (REQ-9)"
  - ".planning/ci_status.md: CI pass/fail status log (REQ-9)"
affects: [01-sumstats-harmonization, data-validation, regression-testing]

# Tech tracking
tech-stack:
  added: [tabix-subsetting, lsf-cron-ci]
  patterns: [smoke-test-reuses-production-rules, config-override-for-testing, dry-run-by-default]

key-files:
  created:
    - tests/toy_3locus/Snakefile.test
    - tests/toy_3locus/config_test.yaml
    - tests/toy_3locus/data/regions_toy.csv
    - tests/toy_3locus/expected/expected_results.yaml
    - scripts/subset_toy_loci.py
    - scripts/run_ci_smoke.sh
    - .planning/ci_status.md
  modified: []

key-decisions:
  - "Snakefile.test includes production rules via same include paths -- no rule duplication (D-04)"
  - "Smoke test defaults to dry-run mode; --full-run flag enables actual execution after data population"
  - "Expected PP.H4 values are approximate placeholders; will be updated after first run with real data (T-00-09)"

patterns-established:
  - "Pattern: Test Snakefiles use configfile override to redirect all paths to test directories"
  - "Pattern: CI smoke wrapper records structured pass/fail in .planning/ci_status.md"
  - "Pattern: Subsetting scripts use tabix for O(log n) region extraction from bgzipped sumstats"

requirements-completed: [REQ-9]

# Metrics
duration: 14min
completed: 2026-04-10
---

# Phase 0 Plan 4: CI Smoke Test Infrastructure Summary

**Toy 3-locus CI smoke test scaffolding with LSF cron wrapper, tabix-based subsetting script, and regression testing baselines for FTO/TCF7L2/SH2B3**

## Performance

- **Duration:** 14 min
- **Started:** 2026-04-10T19:39:46Z
- **Completed:** 2026-04-10T19:54:42Z
- **Tasks:** 3
- **Files created:** 7

## Accomplishments
- Created complete smoke test scaffolding in tests/toy_3locus/ with Snakefile.test that reuses all production rules via include directives (D-04, D-15)
- Defined 3 well-characterized toy loci (FTO chr16, TCF7L2 chr10, SH2B3 chr12) with expected PP.H4 regression baselines (D-14, D-16)
- Built tabix-based subsetting script to create toy data from full harmonized sumstats after download
- Created LSF cron wrapper with structured pass/fail logging to .planning/ci_status.md (REQ-9)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create smoke test scaffolding** - `0d4abb9` (feat)
2. **Task 2: Create toy locus subsetting script** - `2b7a5db` (feat)
3. **Task 3: Create CI smoke test LSF cron wrapper and status log** - `f41248f` (feat)

## Files Created/Modified
- `tests/toy_3locus/Snakefile.test` - Smoke test Snakefile importing production rules with test config override
- `tests/toy_3locus/config_test.yaml` - Test config redirecting all paths to tests/toy_3locus/ subdirectories
- `tests/toy_3locus/data/regions_toy.csv` - 3 toy locus definitions (FTO, TCF7L2, SH2B3) with +-500kb windows
- `tests/toy_3locus/expected/expected_results.yaml` - Expected PP.H4 values for regression testing (approximate placeholders)
- `scripts/subset_toy_loci.py` - Tabix-based subsetting utility for creating toy data from full sumstats
- `scripts/run_ci_smoke.sh` - LSF cron wrapper submitting smoke test via bsub -K and logging results
- `.planning/ci_status.md` - CI pass/fail status log with markdown table format

## Decisions Made
- **Production rule reuse (D-04):** Snakefile.test imports rules via the same `include:` paths as the production Snakefile rather than maintaining separate test-specific rules. This ensures the smoke test validates actual production logic.
- **Dry-run default:** The CI wrapper script defaults to Snakemake dry-run mode (`-n`) since toy data is not yet populated. The `--full-run` flag enables actual execution after data download.
- **Placeholder PP.H4 values (T-00-09):** Expected regression values are approximate (FTO: 0.95, TCF7L2: 0.92, SH2B3: 0.88) with +/-0.05 tolerance. These will be updated from actual coloc.abf output after the first successful run with real data.
- **Config schema compatibility:** config_test.yaml includes all schema-required fields (onekg, plink, resources, finemap, trait_ancestries) so the Snakemake schema validator passes without modification.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed hardcoded path from cron example comment**
- **Found during:** Task 3
- **Issue:** Crontab example comment contained a hardcoded absolute GPFS path which would fail acceptance criteria
- **Fix:** Replaced with generic `/path/to/coloc_analysis` placeholder
- **Files modified:** scripts/run_ci_smoke.sh
- **Verification:** grep for hardcoded paths returns 0 matches
- **Committed in:** f41248f (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix in comment)
**Impact on plan:** Minor comment fix. No functional scope change.

## Issues Encountered
None.

## Known Stubs
- `tests/toy_3locus/expected/expected_results.yaml` - PP.H4 values are approximate placeholders. After first real run with actual sumstats data, these must be updated from legacy coloc.abf output to establish the true regression baseline. This is intentional and documented in the file; Phase 1 data preparation will enable the first actual run.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Smoke test scaffolding is complete and ready for data population
- After data downloads (Phase 0 Track 0a / Phase 1), run `python scripts/subset_toy_loci.py` to populate toy data
- After toy data population, switch CI wrapper from dry-run to `--full-run` mode
- Expected PP.H4 values need updating after first successful run with real data
- Phase 0 infrastructure (Plans 01-04) is now complete: config layer, Snakemake skeleton, and CI smoke test are all in place

## Self-Check: PASSED

All 7 created files verified present on disk. All 3 task commits (0d4abb9, 2b7a5db, f41248f) verified in git log.

---
*Phase: 00-data-access-infrastructure*
*Completed: 2026-04-10*
