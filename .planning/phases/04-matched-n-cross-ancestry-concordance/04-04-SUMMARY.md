---
phase: 04-matched-n-cross-ancestry-concordance
plan: 04
subsystem: ldsc-rg-matrix-detection-probability
tags: [ldsc-rg, fdr, detection-probability, ncp, d-04, d-05, matched-n, original-research]

requires:
  - phase: 04-01
    provides: config/matched_n.yaml, matched_n.smk skeleton
  - phase: 05-pathway-partitioned-heritability
    provides: LDSC infrastructure (munged sumstats + LD scores + ldsc_py3 env)
provides:
  - LDSC r_g rules (ldsc_rg, collect_rg_logs, apply_rg_fdr) in matched_n.smk
  - munge_trait_pair_rg.py (LDSC .log parser)
  - apply_fdr.py (BH-FDR q<0.05 + SE>0.3 flag)
  - compute_detection_probability.py (NCP from empirical beta/SE)
  - compute_detection_probability rule in matched_n.smk
  - results/matched_n/rg_matrix.tsv (D-06d supplementary table)
  - results/matched_n/detection_probability.tsv (D-05b trait-level expected concordance)
affects: [04-05, phase-11-manuscript]

tech-stack:
  added: [statsmodels.stats.multitest (BH-FDR), scipy.stats.ncx2 (noncentral chi-squared)]
  patterns: [BH-FDR across all tests jointly, NCP-based detection probability, original-research construction framing]

key-files:
  created:
    - src/snakemake/scripts/munge_trait_pair_rg.py
    - src/python/apply_fdr.py
    - src/python/compute_detection_probability.py
    - .planning/osf_deviations.md
  modified:
    - src/snakemake/rules/matched_n.smk
    - tests/test_matched_n_fdr.py
    - tests/test_matched_n_detection.py

key-decisions:
  - "BH-FDR applied across all 35 tests jointly (30 cross-trait + 5 same-trait benchmarks) per D-04c"
  - "SE>0.3 flagged as unreliable_se column (not excluded) per research A-2 minimum-deviation"
  - "D-05 NCP framework is original-research construction (not Hou 2023 radmix) per B-2 resolution"
  - "EUR ldscores used for both ref-ld-chr and w-ld-chr in cross-ancestry r_g (LDSC convention)"
  - "T3 schema-freeze test merged into T2 commit (no separate commit needed)"

patterns-established:
  - "Pattern: osf_deviations.md for tracking pre-registration clarifications vs amendments"
  - "Pattern: regression test guarding against broken citation reintroduction"

requirements-completed: []

duration: 14min
completed: 2026-04-16
---

# Phase 4 Plan 04: LDSC 35-test r_g matrix (D-04) + empirical NCP detection probability (D-05) Summary

**35-test LDSC r_g matrix (30 cross-trait + 5 same-trait EUR-AFR benchmarks) with BH-FDR q<0.05 + SE>0.3 flag, plus per-locus NCP detection probability from empirical beta/SE as original-research construction (not Hou 2023)**

## Performance

- **Duration:** 14 min
- **Started:** 2026-04-16T02:42:41Z
- **Completed:** 2026-04-16T02:57:34Z
- **Tasks:** 4 (3 committed, T3 merged into T2)
- **Files modified:** 7

## Accomplishments

- 35-test LDSC r_g matrix wired in Snakemake: 30 cross-trait (C(5,2) x 3 ancestry strata) + 5 same-trait EUR-AFR benchmarks (D-04a/b)
- BH-FDR q<0.05 applied across all 35 tests jointly (D-04c), matching Phase 5 FDR convention
- SE>0.3 flagged as `unreliable_se` column without row exclusion (research A-2 minimum-deviation)
- Per-locus detection probability: NCP = (beta_hat/SE)^2, P(chi^2_1(NCP) >= T) via scipy.stats.ncx2 (D-05a)
- Trait-level expected concordance via arithmetic mean aggregation (D-05b/d)
- D-05 explicitly framed as ORIGINAL-RESEARCH CONSTRUCTION with regression tests (B-2 resolution)
- D-05c parametric prior exclusion documented and tested
- B-2-resolution entry added to .planning/osf_deviations.md
- 13 tests passing (6 FDR + 7 detection probability)

## Task Commits

1. **Task 1: ldsc_rg + collect_rg_logs rules + munge_trait_pair_rg.py** - `28e305c` (feat)
2. **Task 2+3: apply_fdr.py + tests + apply_rg_fdr rule + schema freeze** - `0fed4aa` (feat)
3. **Task 4: compute_detection_probability.py + tests + rule + osf_deviations.md** - `7af8d3d` (feat)

## Files Created/Modified

- `src/snakemake/rules/matched_n.smk` - Added ldsc_rg, collect_rg_logs, apply_rg_fdr, compute_detection_probability rules + RG_COMBOS combo expansion
- `src/snakemake/scripts/munge_trait_pair_rg.py` - LDSC .log parser for r_g matrix assembly
- `src/python/apply_fdr.py` - BH-FDR q<0.05 + SE>0.3 unreliable_se flag (D-04c, A-2)
- `src/python/compute_detection_probability.py` - NCP-based detection probability, original-research construction (D-05)
- `tests/test_matched_n_fdr.py` - 6 tests: BH verification, NA preservation, SE flag, schema freeze (replaced xfail stub)
- `tests/test_matched_n_detection.py` - 7 tests: NCP math, aggregation, empty-trait, header regression, schema (replaced xfail stub)
- `.planning/osf_deviations.md` - B-2-resolution clarification entry

## Decisions Made

- BH-FDR applied across all 35 tests jointly (30 cross-trait + 5 same-trait EUR-AFR benchmarks), not per-ancestry-pair or per-trait-pair-stratified (D-04c)
- SE>0.3 flagged as `unreliable_se` column without row removal per research A-2 minimum-deviation option (a)
- D-05 detection-probability framework documented as original-research construction (B-2 resolution); Hou 2023 PMC10403901 is the radmix paper, not NCP framework
- EUR ldscores used for both --ref-ld-chr and --w-ld-chr in EUR-AFR cross-ancestry r_g tests per LDSC convention (noted as limitation in rule comments)
- T3 (schema freeze test) content was fully delivered in T2 commit; no separate commit needed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's NCP=36 detection probability ~0.78 was inaccurate**
- **Found during:** Task 4 test execution
- **Issue:** Plan stated beta=0.3, SE=0.05 -> NCP=36 -> detection prob ~0.78, but actual scipy.stats.ncx2.sf(29.72, df=1, nc=36) = ~0.708
- **Fix:** Corrected test tolerance to assert ~0.708 instead of ~0.78
- **Files modified:** tests/test_matched_n_detection.py
- **Committed in:** 7af8d3d

**2. [Rule 1 - Bug] Floating-point precision in NCP assertion**
- **Found during:** Task 4 test execution
- **Issue:** (0.3/0.05)^2 = 35.99999999999999, not exactly 36.0
- **Fix:** Changed exact equality to abs tolerance < 1e-10
- **Files modified:** tests/test_matched_n_detection.py
- **Committed in:** 7af8d3d

### Task Merging

**T3 merged into T2:** The test_rg_matrix_schema test and apply_rg_fdr rule were naturally implemented as part of T2, since T3 only added a schema freeze test to the same file T2 was rewriting. No separate commit was warranted.

## Issues Encountered

None beyond the auto-fixed items above.

## User Setup Required

None.

## Next Phase Readiness

- LDSC r_g matrix fully wired: 35 tests resolve via Snakemake rules
- BH-FDR + SE-flag pipeline complete: rg_raw.tsv -> rg_matrix.tsv
- Detection probability pipeline complete: tier_assignments.tsv -> detection_probability.tsv
- Plan 04-05 can now wire Table 2 assembly consuming rg_matrix.tsv + detection_probability.tsv
- .planning/osf_deviations.md established for tracking pre-registration clarifications

## Self-Check: PASSED

All 7 created/modified files verified present on disk. All 3 task commits (28e305c, 0fed4aa, 7af8d3d) verified in git log.
