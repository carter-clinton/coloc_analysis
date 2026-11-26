---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8c2
subsystem: ta-r4 W3f (Q-F3NL QTL_legacy NaN rule; Q-158E7R E7 matched rounding)
tags: [qtl, tiers, nan-gwas, jsonlite, e7, comparator]
requires: [ta-r4-W3f-qtl-json-full-precision]
provides: [tiers_argv per arm, estimands.round_like_jsonlite_default, run_aggregation._qtl_tiers_qtl4dp, E7 fixed_value_qtl_4dp / changed_qtl_4dp]
affects: [15.8d (appends its E7 column after these), 15.8f, W6 tripwire]
tech-stack:
  added: []
  patterns: ["per-arm key in QTL_ARMS drives the argv; the rule passes the wildcard arm", "re-derive through the production script as a subprocess on a temp copy, never a re-implementation"]
key-files:
  created:
    - tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py
  modified:
    - src/python/ta_r4/run_qtl_group_r4.py
    - src/snakemake/rules/ta_r4_qtl.smk
    - src/python/ta_r4/estimands.py
    - src/python/ta_r4/run_aggregation.py
    - tests/ta_r4/test_qtl_sweep_gwas_pph4.py
    - .planning/DECISIONS.md
    - .planning/HANDOFF.json
    - .planning/amendments/osf-amendment-r4-DRAFT.md
decisions:
  - "DEC-2026-11-25-ta-r4-qtl-legacy-nan-rule-and-e7-matched-rounding: --nan-gwas-below-threshold for QTL_A3/QTL_A2 only (QTL_legacy keeps the earlier rule, Q-F3NL); E7 qtl_tier gains fixed_value_qtl_4dp / changed_qtl_4dp (Q-158E7R)"
metrics:
  completed: 2026-11-26
  duration: "11:28-15:09 EST (FULL 2h51m)"
---

# Phase ta-r4 Plan 15.8c2: QTL_legacy NaN rule and E7 matched rounding Summary

QTL_legacy, E7's earlier-pipeline comparator, now keeps the earlier NaN-GWAS rule. `--nan-gwas-below-threshold` is
passed for QTL_A3 and QTL_A2 only, driven by a per-arm `QTL_ARMS` key; the r4_qtl_tiers rule passes `w.qtl_arm`.
E7 qtl_tier rows also carry the QTL_A3 tier re-derived by assign_tiers.py (QTL_A3's own argv) from QTL_A3 posteriors
rounded exactly as jsonlite's default writes them, so `changed` can be read with and without the rounding difference.

## Commits

| Task | Commit | What |
|------|--------|------|
| 1 | 258102ee | DEC (both replies quoted from the files, cmp'd); QTL_ARMS `nan_gwas_below_threshold`; `tiers_argv(qtl_arm, …)`; rule passes `w.qtl_arm`; 6 new tests; 1 declared edit |
| 2 | 97ae2574 | `round_like_jsonlite_default`; `_qtl_tiers_qtl4dp`; E7 `fixed_value_qtl_4dp` / `changed_qtl_4dp` |
| 3 | 35cb04f7 | DRAFT (l), (e) E7, Pre-Paste; HANDOFF do_not 14 → 15 |
| 3 | (records) | LOG, PLAN-INDEX, STATE, this SUMMARY |

## Gates

gate_157j.sh rc 0 (805afcd8…0503e); gate_158.sh Q-F3NL Q-158E7R rc 0 (9b4c0bb0…62b6a1,
`Keep legacy rule for QTL_legacy (Recommended)`; 43a4d899…76bd09, `Add a matched-rounding column (Recommended)`);
sha256sum of each original matches. Record: data/r4/tmp/w3f/q158/gate_15_8c2.txt.

## What changed

- `run_qtl_group_r4.QTL_ARMS`: `"nan_gwas_below_threshold": True` (QTL_A3, QTL_A2), `False` (QTL_legacy).
  `tiers_argv(qtl_arm, summary, gwas, pph4, tiers, sweep, py=…)` appends the flag only when True; the order is
  otherwise unchanged; an unknown arm raises KeyError. assign_tiers.py untouched.
- ta_r4_qtl.smk r4_qtl_tiers: `tiers_argv(w.qtl_arm, …)`. Rendered (`snakemake -n -p`): QTL_A3 (A3_1kg invocation)
  has the flag; QTL_legacy (repro_routeL invocation, only r4_qtl_tiers scheduled) does not.
- `estimands.round_like_jsonlite_default(x)`: jsonlite 2.0.0 num_to_char at digits = 4: for 1e-5 < |x| < 2^31 - 1,
  modp_dtoa2 (scaled fraction truncated; up when the remainder > 0.5, or == 0.5 with an odd last digit); otherwise
  `%.*g` with ceil(min(15, max(1, log10|x|) + 4)) digits. Checked against R's default `toJSON` in the r_coloc job env
  (516ec209…_) on 230,010 values: 10^5 uniform, 10^5 log-uniform 1e-300..1, 10^4 in 1e-5..1e-4, 10^4 decimal ties
  x.xxxx5 and 10 named values; 0 mismatches (e.g. 0.00015 → 0.0001, 0.00005 → 0, 3.2e-5 → 0, 1.234567e-7 →
  1.2346e-07, 0.79996 → 0.8).
- `run_aggregation._qtl_tiers_qtl4dp(repo)`: None when QTL_A3's qtl_coloc_summary_tierable.tsv is absent
  (FileNotFoundError if the summary exists but QTL_A3's gwas_coloc_for_tiers.tsv does not). Otherwise a temp copy with
  PP.H0.abf … PP.H4.abf rounded (other columns byte-for-byte), then assign_tiers.py via
  `tiers_argv("QTL_A3", copy, QTL_A3 GWAS table, config/pph4_thresholds.yaml, tmp outputs)`; returns the tier table.
- `e7_frozen_vs_fixed(…, qtl_tiers_fixed_4dp=None)`: `fixed_value_qtl_4dp`, `changed_qtl_4dp` appended last;
  filled on qtl_tier rows only; `changed` unchanged. The aggregator passes `_qtl_tiers_qtl4dp(repo)`.
- DRAFT: (l) the NaN rule is for the A3 and A2 QTL arms, the earlier-pipeline comparator keeps the earlier rule;
  (e) E7 QTL tiers also reported with A3 posteriors rounded to 4 decimals; the Pre-Paste Reference row
  `passed by r4_qtl_tiers only` (1 occurrence) → `passed by r4_qtl_tiers for the A3 and A2 QTL arms only`. Old strings
  asserted unique (draft_15_8c2.py); test_amendment_text + test_prelock_pilot_fits 24 P / 2 S.
- HANDOFF do_not: the 15.7g W6 string kept; the `SUPERSEDES the 15.7g W6 tripwire (15.8c2, Carter Q-F3NL):` string
  appended; 14 → 15; every pre-existing string present, other keys unchanged (handoff_15_8c2.py).

## Deviations from Plan

1. **[Rule 1 - test harness] Rendered-command token.** In my new test 2, the QTL_A3 flag check split the rendered
   command after `rstrip(")")`, but the command continues `) > log 2>&1`, so the last token was
   `--nan-gwas-below-threshold)`. It now splits the text before the first `)`. Found at the first Task 1 green
   (green_t1_15_8c2.txt, Slurm 2112827); re-run passed (green_t1b_15_8c2.txt, Slurm 2112920). The `startswith(want + ")")` pin was unchanged.
2. RED: all 6 tests failed for the missing code (red_15_8c2.txt, Slurm 2112770): KeyError on the new key, TypeError
   on the new tiers_argv signature, AttributeError on the two new functions.
3. The plan's file list allowed edits of test_estimands.py / test_run_aggregation.py; neither needed one (the
   aggregation fixtures have no QTL_A3 tierable summary, so the new columns stay empty there). No 15.7g test asserts
   the flag on QTL_legacy (grep), so no further declared id.

## Negative controls (data/r4/tmp/w3f/q158/nc_15_8c2.txt; all 6 tests per NC; md5-restored)

- t1 (Slurm 2112990): flag for every arm again → test 1 fails; the rule passes a literal `"QTL_A3"` instead of
  `w.qtl_arm` → test 2 fails (QTL_legacy rendered with the flag; test 1 passes).
- t2 (Slurm 2113144): Python `round(x, 4)` instead of the jsonlite rule → test 3 fails; exact (unrounded) copy used →
  test 5 fails; the two columns not written → test 4 fails (5 also); matched run writing into
  data/r4/results/QTL_A3 instead of tmp → test 6 fails.

Result: ALL NCs FAILED AS REQUIRED AND RESTORED (both sets).

## FULL

- FULL (Slurm 2113242, c022n02 Cascade Lake, HEAD 35cb04f7, 2h51m): QUICK 903 P / 2 S, HEAVY 354 P / 5 S, PINS 39 P; FULL 2,758 = 2,705 P / 53 S / 0 F (full_15_8c2.xml, sha256 e69a6fa2…2a8d45); check_15_8c2.py vs full_15_8c.xml (2,752 read from the file): 0 removed, +6 all passed, 0 outcome changes, 1 declared passed -> passed, CHECK PASS (check_15_8c2.txt).
- Base for 15.8d = data/r4/tmp/w3f/q158/full_15_8c2.xml. sparse_parent_benchmark.tsv restored by close.sh.

## New test ids

tests.ta_r4.test_qtl_legacy_rule_and_e7_rounding::test_tiers_argv_passes_the_nan_flag_for_a3_and_a2_only
tests.ta_r4.test_qtl_legacy_rule_and_e7_rounding::test_rendered_r4_qtl_tiers_command_per_arm
tests.ta_r4.test_qtl_legacy_rule_and_e7_rounding::test_round_like_jsonlite_default_matches_jsonlite
tests.ta_r4.test_qtl_legacy_rule_and_e7_rounding::test_e7_qtl_tier_has_the_matched_rounding_columns
tests.ta_r4.test_qtl_legacy_rule_and_e7_rounding::test_matched_rounding_isolates_a_boundary_flip
tests.ta_r4.test_qtl_legacy_rule_and_e7_rounding::test_matched_rounding_changes_nothing_frozen

## Declared spec updates

tests.ta_r4.test_qtl_sweep_gwas_pph4::test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order

## Known Stubs

None.

## Not done (by rule)

No production fit, no OSF, no lock, no push; decision_rules.yaml locked: false, n_regions_min 7; no re-pin.
NEXT = 15.8d.

## Self-Check: PASSED

Commits 258102ee, 97ae2574, 35cb04f7 exist; the test file, full_15_8c2.xml, red/nc/check records exist; check_15_8c2.py CHECK PASS; HANDOFF carries the SUPERSEDES string; decision_rules.yaml locked: false.
