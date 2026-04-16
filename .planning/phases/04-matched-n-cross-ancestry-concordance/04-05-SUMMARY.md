---
phase: 04-matched-n-cross-ancestry-concordance
plan: 05
subsystem: analysis
tags: [matched-n, bootstrap, concordance, table2, violin, h7-verdict, snakemake, ggplot2]

# Dependency graph
requires:
  - phase: 04-03
    provides: compute_tier_a_retention.R + jaccard.R rules
  - phase: 04-04
    provides: LDSC r_g matrix + detection probability rules
provides:
  - D-06a Table 2 assembly (10-col, 1 row/trait) with H7 verdict
  - D-06b Jaccard Table 2b assembly
  - D-06c Supplementary violin figure with unmatched + Hou null overlays
  - Per-bootstrap retention output for violin input
  - Negative-control integration test for HLA/pigmentation tier flip detection
  - Populated VALIDATION.md with 17 verification entries (nyquist-compliant)
affects: [phase-11-manuscript, phase-04-production-launch]

# Tech tracking
tech-stack:
  added: [assemble_table2.py, plot_violin.R]
  patterns: [H7 verdict from config threshold, per-bootstrap retention TSV for violin, negative-control skip-if-absent pattern]

key-files:
  created:
    - src/python/assemble_table2.py
    - src/snakemake/scripts/plot_violin.R
  modified:
    - src/snakemake/rules/matched_n.smk
    - src/snakemake/scripts/compute_tier_a_retention.R
    - tests/test_matched_n_table2.py
    - tests/test_matched_n_h7.py
    - tests/test_matched_n_negcontrol.py
    - .planning/phases/04-matched-n-cross-ancestry-concordance/04-VALIDATION.md

key-decisions:
  - "H7 verdict uses >= semantics at 20pp boundary (boundary = power_artifact)"
  - "Per-bootstrap retention emitted as additional output from existing retention rule (not a separate rule)"
  - "Negative-control test skips cleanly when is_negative_control column absent from tier_assignments.tsv"

patterns-established:
  - "assemble_table2.py CLI pattern: merge upstream TSVs via pd.merge on trait column"
  - "Per-bootstrap retention TSV (trait, bootstrap_idx, retention) as violin input contract"
  - "Negative-control test uses skip-if-absent pattern for graceful pre-production testing"

requirements-completed: [Table-2-replacement, H7-pre-registration]

# Metrics
duration: 7min
completed: 2026-04-16
---

# Phase 4 Plan 05: Smoke-pilot gate + Table 2 assembly + violin figure + supplementary outputs Summary

**D-06a 10-column Table 2 with H7 verdict per trait, D-06b Jaccard table, D-06c violin figure with unmatched/Hou overlays, negative-control integration test, and fully populated VALIDATION.md**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-16T03:19:22Z
- **Completed:** 2026-04-16T03:26:31Z
- **Tasks:** 4
- **Files modified:** 9

## Accomplishments
- D-06a Table 2 assembles from 4 upstream TSVs with exactly 10 columns per trait, H7 verdict computed from config threshold (20pp)
- D-06c violin figure wired with per-bootstrap retention distribution, unmatched concordance dashed overlay, and Hou expected null dotted overlay
- 13 unit/integration tests pass (H7 boundary semantics, table structure, column order, N_EUR_matched = N_AFR_eff, r_g formatting, Jaccard output)
- Negative-control integration test skips cleanly when pre-production data absent, fails explicitly on HLA/pigmentation tier flips post-production
- VALIDATION.md populated with 17 concrete verification entries covering all plans 04-01 through 04-05

## Task Commits

Each task was committed atomically:

1. **Task 1: Smoke pilot (A-1 calibration gate)** - `f39002c` (feat) -- prior session
2. **Task 2: assemble_table2.py (D-06a + D-06b + D-02d H7)** - `b7e1f41` (feat)
3. **Task 3: plot_violin.R (D-06c) + per_bootstrap_retention** - `76c9a89` (feat)
4. **Task 4: Negative-control test + VALIDATION.md** - `827ed0d` (feat)

## Files Created/Modified
- `src/python/assemble_table2.py` - D-06a Table 2 assembly with H7 verdict, D-06b Jaccard table
- `src/snakemake/scripts/plot_violin.R` - D-06c violin figure with facet_wrap per trait
- `src/snakemake/rules/matched_n.smk` - Added assemble_table2 + plot_violin rules; updated compute_tier_a_retention output block with per_boot
- `src/snakemake/scripts/compute_tier_a_retention.R` - Added --out-per-boot CLI arg + per-bootstrap row collection for D-06c violin input
- `tests/test_matched_n_table2.py` - 6 integration tests: 5-row/10-col structure, column order, N_EUR_matched, H7 verdicts, r_g format, Jaccard
- `tests/test_matched_n_h7.py` - 7 unit tests: power_artifact, concordance_holds, exact boundary, no/negative reduction, zero, custom threshold
- `tests/test_matched_n_negcontrol.py` - 2 integration tests: HLA/pigmentation tier flip check, manifest existence check
- `.planning/phases/04-matched-n-cross-ancestry-concordance/04-VALIDATION.md` - 17 verification entries, nyquist_compliant: true

## Decisions Made
- H7 verdict >= semantics at boundary: 20pp exactly = "power_artifact" (frozen in test_h7_exact_boundary)
- Per-bootstrap retention added as additional output to existing compute_tier_a_retention rule rather than creating a separate rule (avoids re-computing retention)
- Negative-control test uses pytest.skip when tier_assignments.tsv absent or lacks is_negative_control column (graceful pre-production testing)
- Violin plot uses facet_wrap with free_x scales, one panel per trait, Phase 5 dashboard color palette

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
- Snakemake dry-run for `all_matched_n` shows MissingInputException for `results/phase2/tier_assignments.tsv` -- this is expected behavior (upstream Phase 2 output not yet present on disk). The DAG topology is valid and all rules resolve correctly.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All Phase 4 Snakemake rules are wired: manifest -> bootstrap -> coloc -> retention/jaccard/sign -> detection_probability -> rg_matrix -> table2 -> violin
- Full production launch command: `snakemake --profile config/cluster_lsf --use-conda all_matched_n`
- Production gated on: (1) Phase 2 tier_assignments.tsv existing, (2) Carter's pilot approval (received)
- Post-production: negative-control test will activate automatically when bootstrap coloc outputs land

---
*Phase: 04-matched-n-cross-ancestry-concordance*
*Completed: 2026-04-16*
