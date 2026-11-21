---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7d
subsystem: ta-r4 aggregation (W3f review F12)
tags: [a1-allvars, secondary-table, row-drops, descriptive, e6-panel-contrast]
requires: [ta-r4-W3f-cross-purity-variant-resolution]
provides: [run_aggregation table a1_allvars_secondary, row_drops family a1_allvars, A1_ALLVARS_EUR / A1_ALLVARS_AFR contrasts]
affects: [ta-r4-W3f-none-rows-denominators, W7 aggregation]
tech-stack:
  added: []
  patterns: [byte-identity of untouched tables against the module loaded from a literal start-commit ref]
key-files:
  created:
    - tests/ta_r4/test_a1_allvars_secondary.py
  modified:
    - src/python/ta_r4/run_aggregation.py
    - tests/ta_r4/test_run_aggregation.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
decisions:
  - "a1_allvars_secondary has an ancestry column first, then the e6_panel_contrast columns; EUR uses the confirmatory row ids (_ids), AFR the AFR ids, as afr_secondary does"
  - "row_drops family a1_allvars is built with row_drop_table on the same two contrasts, without a1_varset (the label A1_allvars already selects the variant set)"
commits: [1cf179d1]  # + the 15.7d records commit
completed: 2026-11-20
---

# Phase ta-r4 Plan 15.7d: W3f A1 allvars secondary table Summary

D-21 and DRAFT (d) call A1 on all variants a secondary row, and that row is now reported. run_aggregation writes a 20th table, `a1_allvars_secondary`, with A1_allvars vs A3_1kg (EUR, confirmatory ids) and A1_allvars vs AFR661_A3 (AFR ids). Each p12 key gets E1 with n_snps medians, E2 over the sweep, E3, E4/E5 per side and drops. The table comes from the existing `estimands.e6_panel_contrast`, and `row_drops` gains family `a1_allvars`. No confirmatory number moves.

## Task 1 RED → GREEN (1cf179d1)

- Start sha 7b1e0fd2 (`$Q/start_15_7d.txt`), in the test as the literal `PRE_157D_REF`.
- RED (`$Q/red_15_7d.txt`, `$Q/red_15_7d.xml`): tests 1-5 FAILED (1-4 on the missing table file, 5 on the missing family), and test 6 PASSED, as the plan said.
- GREEN: Task 1 verify (5 files) gave 59 P / 2 S (`$Q/green_15_7d.xml`). Per id against full_15_7c.xml: +6 new, the _20_ successor, no outcome changes, and the 2 skips are pre-existing.
- Mutation NCs (`$Q/mutation_nc_15_7d.txt`) ran 6 mutations of the GREEN source. Each failed exactly its predicted tests, and the source was md5-restored after each one:
  - M1: table reads A1_matched. Fails tests 1, 3, 4, 5.
  - M2: EUR table on every EUR row, NC included. Fails 2, 3, 4.
  - M3: drop family mislabelled. Fails 5 and test_row_drops_and_long_e6_tables.
  - M4: branch_outcomes `via` moves. Fails 6 and test_branch_outcomes_two_confirmatory_rows.
  - M5: AFR side dropped. Fails 1, 2, 3, 4.
  - M6: table removed from TABLES. The _20_ successor fails.
  - Run 1 (`$Q/mutation_nc_15_7d_run1_mispredicted.txt`) got two predictions wrong, both by missing an extra failure. M4 also fails test_branch_outcomes_two_confirmatory_rows, which compares `via`. M5 also fails test 2, which asserts the AFR n. I corrected the predictions; no code or test changed.
- No-weaken AST check (`$Q/noweaken_15_7d.py`): PASS. It allows only three changes to test_run_aggregation.py relative to the start sha: the TABLES insertion, the rename with an AST-identical body, and the one family-set assert. Its 5 NCs all FAIL (`$Q/noweaken_15_7d_nc.txt`): a weakened assert, a removed `T == TABLES` assert, a wrong family set, a renamed other test and a changed PAIRS.
- DRAFT (e): I inserted one sentence after the unique "each against `AFR661_A3`) are reported the same way." (`$Q/draft_15_7d.py`). test_amendment_text is green.

## Task 2: FULL

Slurm 2011462 (`sbatch --wait`, cascadelake c020n03, HEAD 1cf179d1): QUICK 826 P / 2 S; HEAVY 315 P / 5 S; PINS 39 P; FULL **2,642 = 2,589 P / 53 S / 0 F**.

Against full_15_7c.xml (`$Q/check_15_7d.txt`, `$Q/cmp_15_7d.txt`):
- 1 id removed: the declared rename `test_draft_writes_exactly_19_draft_tables`.
- 7 ids added, all passed: the 6 new tests and `test_draft_writes_exactly_20_draft_tables`.
- 0 outcome changes, including 0 in tests/m3.
- The declared spec update went passed → passed.

check_15_7d.py: PASS. Its NCs FAIL as they should (base as new; a synthetic failure on the declared id) (`$Q/check_15_7d_nc.txt`).

## Declared spec updates

tests.ta_r4.test_run_aggregation::test_row_drops_and_long_e6_tables

What changed: `set(rd.family) == {"confirmatory", "e6", "afr_secondary"}` gains `"a1_allvars"`. Nothing else in the test changed (no-weaken AST PASS).

Declared rename (removed id, successor passed):
tests.ta_r4.test_run_aggregation::test_draft_writes_exactly_19_draft_tables → tests.ta_r4.test_run_aggregation::test_draft_writes_exactly_20_draft_tables (the body is AST-identical; the module TABLES tuple gains `a1_allvars_secondary` after `afr_secondary`).

## New tests (6)

tests/ta_r4/test_a1_allvars_secondary.py:
1. test_allvars_table_has_both_ancestries_and_both_p12_keys
2. test_allvars_rows_are_the_primary_curated_and_afr_ids
3. test_allvars_e1_equals_a_direct_paired_computation
4. test_allvars_table_tracks_allvars_not_matched
5. test_row_drops_has_the_a1_allvars_family
6. test_confirmatory_tables_unchanged

## Deviations from Plan

1. **The fixture extends build_tree inside the new test file.** It adds 5 AFR primary rows with every AFR arm and A1 matched/allvars. It also overwrites the EUR A1 allvars docs with values that vary by row, because build_tree's constant 0.5 would make E1 degenerate. build_tree itself is unchanged.
2. **The no-weaken AST check was added** (not required by the plan, following the 15.7c precedent), with its own NCs.
3. **Mutation-NC run 1 got two predictions wrong.** This is recorded above. Every intended test failed in run 1 too; the misses were extra failures in tests I had not predicted.

## Known Stubs

None.

## Self-Check: PASSED
