---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7e
subsystem: ta-r4 coloc pair docs + estimands (W3f review F8, F11)
tags: [no-cs-rate, known-states, negative-controls, by-method, early-exit, q-den]
requires: [ta-r4-W3f-a1-allvars-secondary]
provides: [early-exit pair docs keep the completed side's n_cs + early_exit_a/b, e4_no_cs_rate n_unknown + no_cs_rate_known, negative_control_rates long by method + with_posterior]
affects: [ta-r4-W3f-purity-determinism, W7 aggregation, DRAFT (e) (l)]
tech-stack:
  added: []
  patterns: [byte-identity of confirmatory tables against modules loaded from a literal start-commit ref (git show)]
key-files:
  created:
    - tests/ta_r4/test_none_rows_denominators.py
  modified:
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
    - src/python/ta_r4/estimands.py
    - tests/ta_r4/test_run_aggregation.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/DECISIONS.md
decisions:
  - "DEC-2026-11-20-ta-r4-none-rows-denominators: Carter Q-DEN = A: Known states only (Recommended)"
  - "early_exit_a / early_exit_b are written only on early-exit pair docs; fitted docs keep their exact key set (test_coloc_pair_r4::test_output_keys_exact unchanged)"
  - "negative_controls always has a with_posterior row per (nc_set, label, p12_key), with n_rows 0 and share_h4 NaN when every row is none; n_fallback_abf is a column on every row"
  - "e4_no_cs_rate: no_cs_rate_known is NaN when a group has no row of known state; n_unknown / no_cs_rate_known are NaN on fit-level rows"
commits: [699fdb23, 8d272492]  # + the 15.7e records commit
completed: 2026-11-20
---

# Phase ta-r4 Plan 15.7e: W3f none rows and denominators Summary

Carter's Q-DEN answer A ("Known states only") is now the rule for two rates. F11: when one fit of a pair exits early, the pair doc keeps the completed side's n_cs and records which side exited (`early_exit_a` / `early_exit_b`), so a completed side with 0 sets is a known no-CS. The pair no-CS rate reports `n_unknown` and `no_cs_rate_known` next to the unchanged all-rows rate. F8: negative-control rates are split by method, with a `with_posterior` row that labels fallback, and `none` rows are counted but are in no share denominator. No confirmatory number moves.

## Gate

`gate_reply.py Q-DEN --question <plan text> --sha256 0775b935…b832c "A: Known states only (Recommended)"` printed the label and sha256, rc 0 (`$Q/gate_15_7e.txt`). Run before any edit.

## Task 1 RED → GREEN

- Start sha f20b667b (`$Q/start_15_7e.txt`), in the test as the literal `PRE_157E_REF`.
- Commit 699fdb23: DEC-2026-11-20-ta-r4-none-rows-denominators. Its quoted block is `cmp`-identical to the reply file.
- RED (`$Q/red_15_7e.txt`; `$Q/red_15_7e_light.xml`, `$Q/red_15_7e_heavy.xml`), current code with the new tests and the declared assert applied:
  - Tests 3-5 failed (no `n_unknown`), 7-11 failed (no `method` column), and the declared spec update failed (no `method` column). Tests 6 and 12 passed, as planned.
  - Tests 1-2 (heavy, Slurm 2012560) failed on the defect itself. The completed side's n_cs was null where the full run gives 2 (SAME) and 0 (NULL), and `early_exit_a` was missing. In this run tests 1-2 were parametrized (4 ids). I then folded each into one id with a loop over the same cases, so the file has exactly the plan's 12 ids. Heavy mutations H1/H2 below show that the final form fails on the defect.
  - test_estimands::test_e4_no_cs_rate and test_reporting_widened::test_e4_no_cs_rate_levels_and_denominators passed in RED and GREEN with their asserted values unchanged, as measured at planning.
- GREEN (8d272492): Task 1 verify plus test_coloc_pair_r4.py (R touched), Slurm 2012646 = 103 P / 2 S (`$Q/green_15_7e.xml`). The 2 skips are the pre-existing test_amendment_text skips.
- Mutation NCs on the GREEN source. Each failed exactly its predicted tests, and the source was md5-restored (`$Q/pre_mut_15_7e.md5`).
  - Light (`$Q/mutation_nc_15_7e_light.txt`):
    - M1: unknown never counted → 4, 5.
    - M2: known rate over all rows → 5.
    - M3: none rows enter with_posterior → 8, 9, 11.
    - M4: none row gets a share → 8.
    - M5: fallback not labelled → 9.
    - M6: A1 methods merged → 10, 11.
    - M7: pooled table → 7-11.
    - M8: E3 output order moves → 12.
    - M9: fit level drops early exits → 6 and two test_reporting_widened tests.
    - M10: known zero needs a known partner → 3, 5.
  - Heavy, Slurm 2012849 (`$Q/mut_heavy_15_7e_2012849.out`):
    - H1: completed-side n_cs dropped → 1, 2.
    - H2: exit sides not recorded → 2.
    - Run 1 (Slurm 2012775, `$Q/mutation_nc_15_7e_heavy_run1_mispredicted.txt`) mispredicted H1. Test 2 also asserts that the completed side's n_cs is an int. I corrected the prediction; no code or test changed.
- No-weaken AST check (`$Q/noweaken_15_7e.py`): PASS. Relative to the start sha, test_run_aggregation.py differs only in the one NC assert. Its 4 NCs FAIL (`$Q/noweaken_15_7e_nc.txt`): a weakened `>=`, the wrong method excluded, another assert dropped and another test renamed.
- DRAFT (`$Q/draft_15_7e.py`): rewrote (e) E4 pair level and (l) NC share; old strings asserted unique. test_amendment_text is green.

## Task 2: FULL

Slurm 2012884 (`sbatch --wait`, cascadelake c023n03, HEAD 8d272492; `$Q/close_15_7e_2012884.out`): QUICK 836 P / 2 S; HEAVY 317 P / 5 S; PINS 39 P; FULL **2,654 = 2,601 P / 53 S / 0 F** (`$Q/full_15_7e.xml`).

Against full_15_7d.xml (`$Q/check_15_7e.txt`, `$Q/cmp_15_7e.txt`):
- 0 ids removed.
- 12 ids added, all passed: exactly the 12 new tests (`$Q/new_tests_15_7e.txt`).
- 0 outcome changes, including 0 in tests/m3.
- The declared spec update went passed → passed.

check_15_7e.py: PASS. Its NCs FAIL as they should (base as new; a synthetic failure on the declared id) (`$Q/check_15_7e_nc.txt`).

## Declared spec updates

tests.ta_r4.test_run_aggregation::test_row_counts_equal_fixture_admissible_rows

What changed: `assert set(nc.n_rows) == {3}` (pooled table) became `assert set(nc[nc.method != "with_posterior"].groupby(["nc_set", "label", "p12_key"]).n_rows.sum()) == {3}`, the same check on the per-group totals of the long table. Nothing else in the file changed (no-weaken AST PASS). The id was kept and went passed → passed.

## New tests (12)

tests/ta_r4/test_none_rows_denominators.py:
1. test_early_exit_pair_keeps_the_completed_sides_n_cs (r4_heavy)
2. test_early_exit_pair_records_which_side_exited (r4_heavy)
3. test_known_zero_beside_an_early_exit_is_no_cs
4. test_unknown_without_a_known_zero_is_counted_as_unknown
5. test_no_cs_rate_known_excludes_unknown_rows
6. test_fit_level_rule_unchanged
7. test_nc_rates_split_by_method
8. test_nc_none_rows_are_counted_not_in_a_share_denominator
9. test_nc_with_posterior_row_labels_fallback
10. test_nc_a1_methods_are_their_own_rows
11. test_nc_group_totals_reconcile
12. test_confirmatory_outputs_unchanged

## Deviations from Plan

1. **`early_exit_a` / `early_exit_b` are written only on early-exit docs.** The plan asks for these keys on the early-exit pair doc. Writing them on every doc would have broken test_coloc_pair_r4::test_output_keys_exact (an exact key set), which is not a declared spec update. They are therefore added in the early-exit branch only. Test 2 asserts that a fitted doc does not carry them.
2. **Test 6 compares against the start-commit module.** It checks the fit-level rows column by column against `estimands.py` loaded from `PRE_157E_REF` via `git show`, not only against hand counts.
3. **Test 12 runs the old modules in a subprocess.** It copies `src/python/ta_r4`, replaces estimands.py and run_aggregation.py with their `PRE_157E_REF` versions, and runs run_aggregation in a subprocess. It then byte-compares branch_outcomes and E1-E3 against the current run on build_tree.
4. **Heavy tests 1-2 were folded from parametrized to single ids after RED** (see Task 1), to match N_new = 12.
5. **No-weaken AST check and mutation NCs added**, following the 15.7c/15.7d precedent. Heavy run 1 mispredicted H1 (recorded above).

## Known Stubs

None.

## Self-Check: PASSED
