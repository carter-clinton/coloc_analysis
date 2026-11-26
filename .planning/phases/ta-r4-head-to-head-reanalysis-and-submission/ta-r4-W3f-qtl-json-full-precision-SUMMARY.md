---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8c
subsystem: ta-r4 W3f (R4: serialization precision before thresholds)
tags: [jsonlite, precision, qtl, coloc, simulation, track-b-isolation]
requires: [ta-r4-W3f-openblas-pin-and-guard]
provides: [run_qtl_coloc.R --json-full-precision, exact r4 pair JSON, exact simulation posteriors]
affects: [15.8c2 (E7 matched rounding), 15.8f]
tech-stack:
  added: []
  patterns: ["opt-in flag on a Track-B-shared script, default path byte-identical (15.7f pattern)"]
key-files:
  created:
    - tests/ta_r4/test_qtl_json_precision.py
  modified:
    - src/snakemake/scripts/run_qtl_coloc.R
    - src/python/ta_r4/run_qtl_group_r4.py
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
    - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R
    - tests/ta_r4/test_purity_determinism.py
    - tests/ta_r4/test_coloc_pair_r4.py
    - .planning/DECISIONS.md
    - .planning/amendments/osf-amendment-r4-DRAFT.md
decisions:
  - "DEC-2026-11-24-ta-r4-qtl-json-full-precision-flag: I(17) behind --json-full-precision (QTL_A3/QTL_A2 only), I(17) in run_coloc_pair_r4.R, %.17g simulation posteriors (Q-158DIG A)"
metrics:
  completed: 2026-11-26
  duration: "07:44-11:30 EST (FULL 2h49m)"
---

# Phase ta-r4 Plan 15.8c: QTL JSON full precision Summary

The r4 QTL arms (QTL_A3/QTL_A2), the r4 trait-pair and qtl_abf JSON, and the simulation posterior columns now write
17-significant-digit values. Every double round-trips exactly before any threshold. QTL_legacy and Track B keep
jsonlite's 4-decimal default, and their output is byte-identical to the pre-15.8c script.

## Commits

| Task | Commit | What |
|------|--------|------|
| 1 | dc4d8156 | DEC-2026-11-24-ta-r4-qtl-json-full-precision-flag (both replies quoted from the files, cmp'd); writer inventory |
| 2 | eca81966 | `--json-full-precision` + `write_result` helper; arms; pair I(17); simulation %.17g; 8 new tests; 2 declared edits |
| 3 | 635ffc1c | DRAFT (l) sentence |
| 3 | (records) | LOG, PLAN-INDEX, STATE, this SUMMARY |

## Gates

gate_157j.sh rc 0 (805afcd8…0503e); gate_158.sh Q-158DIG rc 0 (ea8fe4cd…ceb4,
`A: Exact round-trip everywhere r4 thresholds (Recommended)`). Record: data/r4/tmp/w3f/q158/gate_15_8c.txt.

## Writer inventory (data/r4/tmp/w3f/q158/writers_15_8c.tsv)

Measured in the r_coloc job env (516ec209…_; jsonlite 2.0.0, data.table 1.16.4). The written text was parsed in
Python against R's `%a` values, using 10^5 uniform doubles plus 0.8 − 2⁻⁵³:
- 0% round-trip for jsonlite's default.
- 8.07% for `digits = NA`, fwrite and write.table.
- 100% for `I(17)` and `sprintf("%.17g")`.
- 0.8 − 2⁻⁵³ survives only `I(17)` and `%.17g`.

The thresholded writers are exactly the plan's <context> list. Two other things checked:
- jsonlite's `I(17)` token is identical to C's `%.17g` (measured).
- R's own `as.numeric` parse of 15-digit text differs from the correctly rounded Python parse on a few values. R's
  `jsonlite::fromJSON` agrees with Python.

## Deviations from Plan

1. **[Rule 1 - test harness] Trace target.** In my new test, `trace(..., where = asNamespace("jsonlite"))` did not
   intercept calls to the attached `write_json`. It now traces the attached function, and the test asserts that the
   dump exists. This was found at RED, in test 7.
2. **Declared pre-existing edit (allowed by Task 2 step 6).** The test is
   tests.ta_r4.test_coloc_pair_r4::test_qtl_abf_pp_equal_direct_coloc_abf, line 323.
   - What failed: the test compares the qtl_abf JSON (`d[k] for k in PP`) with exact `==` against a direct
     `coloc.abf` oracle printed with `toJSON(..., digits = NA)`, which is 15 digits. After the change the writer emits
     17 digits (6.676449210020358e-05 vs 6.67644921002036e-05).
   - The edit: only the oracle's `digits = NA` became `digits = I(17)`. The comparison stays exact, so the test is
     stricter, not looser.
   - It passed after the edit (green2_15_8c.txt). No tolerance-based test was edited.
3. **RED note.** Tests 2 (default byte identity) and 6 (QTL_legacy 4 decimals) passed at RED. They pin behaviour the
   plan must not change, so they cannot fail before the code exists. They were seen failing under NC 2 (helper always
   full → test 2) and NC 3 (QTL_legacy given the flag → test 6).
4. Placement: the plan text says `--json-full-precision` goes "after `--exact-purity`" in the option list; it does.
   In argv it goes immediately before `--qtl-orient`, after `--variant-list`, as specified.

## Negative controls (data/r4/tmp/w3f/q158/nc_15_8c.txt, Slurm 2110820)

All 8 tests were run for each NC, and each NC was md5-restored:
- Helper ignores the flag: tests 3 and 4 fail.
- Helper always uses full precision: test 2 fails (3 and 4 also fail).
- QTL_legacy given the flag: tests 5 and 6 fail.
- Pair writer back to `digits = NA`: test 7 fails (8 also fails).
- Simulation format removed: test 7 fails.
- Flag validation removed: test 1 fails.
- Scratch file with an unclassified `write_json` in ta_r4: test 8 fails (the file was then removed).

Result: ALL NCs FAILED AS REQUIRED AND RESTORED.

## FULL (Slurm 2110960, c020n03 Cascade Lake, HEAD 635ffc1c)

- QUICK: 899 P / 2 S. HEAVY: 352 P / 5 S. PINS: 39 P.
- FULL: 2,752 = 2,699 P / 53 S / 0 F (data/r4/tmp/w3f/q158/full_15_8c.xml, sha256 ac058269…39d245).
- check_15_8c.py vs full_15_8b.xml (2,744): 0 removed, +8 all passed, 0 outcome changes on pre-existing ids, both
  declared ids passed → passed. Totals 2,752 / 2,699 / 53 / 0. CHECK PASS (check_15_8c.txt).

## New test ids

tests.ta_r4.test_qtl_json_precision::test_flag_rejects_values_other_than_true_false
tests.ta_r4.test_qtl_json_precision::test_default_output_is_byte_identical_to_the_pre_15_8c_script
tests.ta_r4.test_qtl_json_precision::test_full_precision_round_trips_and_rounds_to_the_default
tests.ta_r4.test_qtl_json_precision::test_boundary_posteriors_are_not_rounded_onto_the_threshold
tests.ta_r4.test_qtl_json_precision::test_qtl_command_passes_full_precision_except_legacy
tests.ta_r4.test_qtl_json_precision::test_qtl_legacy_tiers_input_keeps_4_decimal_posteriors
tests.ta_r4.test_qtl_json_precision::test_r4_pair_and_simulation_writers_round_trip
tests.ta_r4.test_qtl_json_precision::test_every_r4_writer_is_classified

## Declared spec updates

tests.ta_r4.test_purity_determinism::test_qtl_default_path_unchanged_without_the_flag
tests.ta_r4.test_coloc_pair_r4::test_qtl_abf_pp_equal_direct_coloc_abf

## Known Stubs

None.

## Not done (by rule)

No production fit, no OSF, no lock, no push; decision_rules.yaml locked: false, n_regions_min 7; no re-pin.
NEXT = 15.8c2.

## Self-Check: PASSED

Commits dc4d8156, eca81966, 635ffc1c exist; the test file, full_15_8c.xml, nc/red/writers records exist; check_15_8c.py CHECK PASS.
