---
phase: 04-matched-n-cross-ancestry-concordance
plan: 01
subsystem: matched-n-bootstrap
tags: [snakemake, yaml-schema, pytest, matched-n, cross-ancestry, bootstrap, ldsc-rg]

requires:
  - phase: 01-coloc-susie-fine-mapping-spine
    provides: .fit.rds SuSiE objects + susie_policy.yaml
  - phase: 02-3-way-qtl-colocalization
    provides: tier_assignments.tsv (Tier A locus list)
  - phase: 05-pathway-partitioned-heritability
    provides: LDSC infrastructure (munged sumstats + LD scores for r_g)
provides:
  - config/matched_n.yaml with all pre-registered parameters locked
  - schemas/matched_n.schema.yaml for config validation
  - src/snakemake/rules/matched_n.smk skeleton with manifest generation
  - 7 Wave 0 pytest xfail stubs covering D-01/D-02/D-04/D-05 units
  - bmi.AFR tiered fallback documentation (MVP > AoU > Pan-UKBB)
  - RESEARCH Q1 (SE-inflation ref) and Q4 (LSF quota) resolutions
affects: [04-02, 04-03, 04-04, 04-05, phase-11-manuscript]

tech-stack:
  added: [jsonschema (validation)]
  patterns: [configfile string literal per Phase 9 learning, additiveConfig, xfail-stub-per-D-ID]

key-files:
  created:
    - config/matched_n.yaml
    - schemas/matched_n.schema.yaml
    - src/snakemake/rules/matched_n.smk
    - tests/test_matched_n_se_inflation.py
    - tests/test_matched_n_tier_a.py
    - tests/test_matched_n_h7.py
    - tests/test_matched_n_detection.py
    - tests/test_matched_n_fdr.py
    - tests/test_matched_n_negcontrol.py
    - tests/test_matched_n_table2.py
    - tests/fixtures/matched_n/README.md
    - tests/conftest.py
  modified:
    - Snakefile
    - .planning/data_access.md

key-decisions:
  - "bootstrap_fits_root on /rs1 allocation to avoid GPFS quota pressure"
  - "Root tests/conftest.py created with phase4/phase5/phase9 markers"
  - "NCSU LSF standard queue: 1024 concurrent slots per user (resolves A-1 compute concern)"

patterns-established:
  - "Pattern: xfail test stub per D-ID for traceability"
  - "Pattern: config + schema pair in config/ + schemas/ per Phase 0 D-06"
  - "Pattern: tiered data-access fallback (Tier 1/2/3) in data_access.md"

requirements-completed: []

duration: 8min
completed: 2026-04-16
---

# Phase 4 Plan 01: Scaffold, Config, Wave 0 Test Stubs Summary

**Pre-registered matched-N config (100 bootstraps, 20pp H7 threshold, seed formula, FDR q<0.05) + Snakemake skeleton with manifest rule + 7 xfail test stubs + bmi.AFR tiered data-access fallback (MVP N=55k primary)**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-16T02:16:42Z
- **Completed:** 2026-04-16T02:24:39Z
- **Tasks:** 4
- **Files modified:** 14

## Accomplishments
- Configuration contract locked: all D-01/D-02/D-03/D-04/D-05 parameters validated by JSON schema
- Snakemake skeleton loads (snakemake --list shows all_matched_n + build_matched_n_manifest)
- 7 pytest xfail stubs collected (0.09s), each referencing its D-ID for full traceability
- bmi.AFR data gap resolved: MVP phs002453 (N=55.5k, SE-inflation 3.55x) supersedes Pan-UKBB (N=6k, SE-inflation 10.8x)
- NCSU LSF quota documented: 1024 concurrent slots on standard queue — sufficient for 300k fits

## Task Commits

Each task was committed atomically:

1. **Task 1: config/matched_n.yaml + schema** - `4d5c80d` (feat)
2. **Task 2: matched_n.smk skeleton + manifest rule + bmi.AFR** - `2d7103c` (feat)
3. **Task 3: Wave 0 test stubs (7 xfail)** - `a39532a` (test)
4. **Task 4: RESEARCH Q1/Q4 resolution** - `e8f10cc` (docs)

## Files Created/Modified
- `config/matched_n.yaml` - Pre-registered parameters for matched-N analysis
- `schemas/matched_n.schema.yaml` - JSON schema validating all config keys
- `src/snakemake/rules/matched_n.smk` - Snakemake skeleton with manifest generation rule
- `Snakefile` - Added include directive for matched_n.smk
- `tests/test_matched_n_se_inflation.py` - D-01a SE-inflation formula xfail stub
- `tests/test_matched_n_tier_a.py` - D-02a Tier A retention xfail stub
- `tests/test_matched_n_h7.py` - D-02d 20pp verdict xfail stub
- `tests/test_matched_n_detection.py` - D-05a NCP detection probability xfail stub
- `tests/test_matched_n_fdr.py` - D-04c BH-FDR xfail stub
- `tests/test_matched_n_negcontrol.py` - CP#1(c) negative control xfail stub
- `tests/test_matched_n_table2.py` - D-06a Table 2 structure xfail stub
- `tests/fixtures/matched_n/README.md` - Synthetic fixture plan
- `tests/conftest.py` - Root conftest with phase4/5/9 markers
- `.planning/data_access.md` - bmi.AFR tiered fallback + Q1/Q4 resolutions

## Decisions Made
- bootstrap_fits_root placed on /rs1 allocation (/rs1/researchers/c/ckclinto/matched_n_fits) to avoid GPFS quota pressure from 100 .fit.rds per (trait, region)
- Created root tests/conftest.py with phase4, phase5, phase9 marker registration (no root conftest existed previously)
- LSF standard queue has 1024 JL/U (concurrent slots per user) — resolves RESEARCH A-1 concern about compute envelope

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created root tests/conftest.py**
- **Found during:** Task 3 (Wave 0 test stubs)
- **Issue:** No root tests/conftest.py existed; phase4 marker would trigger PytestUnknownMarkWarning
- **Fix:** Created tests/conftest.py with pytest_configure registering phase4, phase5, phase9 markers
- **Files modified:** tests/conftest.py
- **Verification:** pytest collects all 7 stubs without warnings
- **Committed in:** a39532a (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential for pytest marker registration. No scope creep.

## Issues Encountered
- Snakemake dry-run of all_matched_n shows MissingInputException for table2/rg_matrix/violin — expected, as production rules are skeleton-only (Plans 04-02 through 04-05 will add them)

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Config contract locked: Plans 04-02 through 04-05 can implement against config/matched_n.yaml
- Manifest rule ready: build_matched_n_manifest generates bootstrap manifest from Phase 2 tier_assignments
- Test stubs ready: Each plan will convert xfail stubs to passing tests as implementation lands
- bmi.AFR data access: Next action is to verify MVP phs002453 BMI AFR downloadability (before Plan 04-02)
- LSF pilot: Plan 04-05 T1 should run 100-fit pilot on short queue to calibrate wall-clock

## Self-Check: PASSED

All 12 created files verified present on disk. All 4 task commits (4d5c80d, 2d7103c, a39532a, e8f10cc) verified in git log.

---
*Phase: 04-matched-n-cross-ancestry-concordance*
*Completed: 2026-04-16*
