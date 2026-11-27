---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8d
subsystem: ta-r4 W3f (Q-157J R3: E7 fit-yield count definition)
tags: [e7, credible-sets, purity, susieR, lock-gate]
requires: [ta-r4-W3f-qtl-legacy-rule-and-e7-rounding]
provides: [E7 fit_yield frozen = purity-filtered count, frozen_value_json_unfiltered, run_aggregation.FIT_CS_FILTERED, manifests/fit_cs_repro_routeL_exact_purity.tsv]
affects: [15.8e, 15.8f]
tech-stack:
  added: []
  patterns: ["exact purity <= subsampled purity: only a KEPT set over n_purity members can change a count"]
key-files:
  created:
    - tests/ta_r4/test_e7_filtered_counts.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fit_cs_repro_routeL_exact_purity.tsv
  modified:
    - src/python/ta_r4/estimands.py
    - src/python/ta_r4/run_aggregation.py
    - src/python/ta_r4/r4_lock_gate.py
    - tests/ta_r4/test_estimands.py
    - tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py
    - tests/ta_r4/test_run_aggregation.py
    - tests/ta_r4/test_a1_allvars_secondary.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
decisions:
  - "Q-157J R3 (Carter: yes it should be counted): E7 fit_yield compares purity-filtered with purity-filtered; JSON count kept as a labelled column"
  - "Q-158DFX (Carter: Fix the test (Recommended)): the pre-157d differential passes fit_cs_filtered to E7; production keeps it required"
metrics:
  completed: 2026-11-26
  duration: "15:12-21:10 EST (two FULLs, 2h33m + 2h36m)"
---

# Phase ta-r4 Plan 15.8d: E7 filtered credible-set counts Summary

E7's fit-yield frozen side is now the earlier route-L fit's purity-filtered set count (`length(fit$sets$cs)`,
manifests/fit_cs_json_vs_rds.tsv `n_cs_rds_sets`; NA for an early exit), so `changed` compares one definition with
itself. The earlier JSON count, which includes impure sets, is kept as `frozen_value_json_unfiltered`. The manifest is
now a locked path. Stored and exact-purity counts were shown equal on all 96 earlier fits.

## Commits

| Task | Commit | What |
|------|--------|------|
| 1 | ca776492 | fit_cs_repro_routeL_exact_purity.tsv (96 rows; 66 eq true, 30 NA) |
| 2 | f9afd684 | E7 `fit_cs_filtered`, `frozen_value_json_unfiltered`; FIT_CS_FILTERED; LOCKED_PATHS 29 -> 30; 6 new tests |
| 3 | cf02643d | DRAFT (e) E7, (m), Pre-Paste LOCKED_PATHS 30 |
| 3 | b1b5aa00 | test_confirmatory_tables_unchanged fixture (Carter Q-158DFX) + reply file |
| 3 | (records) | LOG, PLAN-INDEX, STATE, this SUMMARY |

## Gates

gate_157j.sh rc 0 (805afcd8…0503e, original sha256sum matches). Q-158DFX reply
W3f-carter-15-8-Q-158DFX-reply-2026-11-26.txt, sha256 dbe60868e73171d992d6bb204070cc372608a9cb7489b35c865168bbcbac154d,
`Fix the test (Recommended)`.

## 96-fit check (Task 1)

- 66 fitted fits: n_cs_exact = n_cs_rds_sets, eq true for all. 30 early exits (24 too_many_variants, 6 no_variants): NA.
- 25 fits have a candidate component over 100 members (up to 15,846); 0 stored (kept) sets have over 100 members;
  every stored set is the same-member candidate of its component (Slurm 2115132, 2115173, 2115237; susieR 0.14.2).
- Argument: susieR 0.14.2 `get_purity` subsamples only a set over n_purity = 100 members
  (`if (length(pos) > n) pos = sample(pos, n)`) and returns the minimum |r| over the sampled pairs, which is >= the
  all-pairs minimum. So exact purity <= stored purity: a component dropped at fit time stays dropped, and only a kept
  set over 100 members could change a count. None exists. No Q-158R3 STOP.

## What changed

- `estimands.e7_frozen_vs_fixed(…, fit_cs_filtered)` (required keyword): fit_yield frozen =
  `<status_L>;n_cs=<n_cs_rds_sets>`; `frozen_value_json_unfiltered` (last column, after 15.8c2's
  `fixed_value_qtl_4dp`, `changed_qtl_4dp`) = the old `<status_L>;n_cs=<n_cs_L>`, fit_yield rows only (empty
  elsewhere); `changed` = frozen != fixed. A missing row, a duplicate row, or a status / n_cs_json mismatch with
  known_answer_W3a raises. No fallback.
- `run_aggregation.FIT_CS_FILTERED = f"{paths.MAN}/fit_cs_json_vs_rds.tsv"`, passed to E7.
- `r4_lock_gate.LOCKED_PATHS`: `manifests/fit_cs_json_vs_rds.tsv` after known_answer_W3a.tsv (30 entries).
- **Early exits:** the 30 early-exit fits move from `n_cs=0` to `n_cs=NA` on the frozen side, so `changed` shifts for
  those rows (it now matches a fixed-side NA).
- DRAFT (draft_15_8d.py, old strings unique): (e) E7 `(both sides count purity-filtered credible sets; the earlier fit
  JSON's count, which includes impure sets (h), is reported alongside)`; (m) names
  `manifests/fit_cs_json_vs_rds.tsv`; Pre-Paste `LOCKED_PATHS` (30 entries; re-checked W3f 15.8d), 30 = len() measured.
  test_amendment_text + test_prelock_pilot_fits 24 P / 2 S.

## Deviations from Plan

1. **[Rule 3 - method] Exact-purity identity without the 15.7h2 routine.** The routine reads `ld_file_declared`, which
   0 of the 96 route-L JSONs have. I used the subsample bound above instead. It decides every fit without the scored
   matrix, and the outcome would be identical under the routine. Test 6 re-derives the stored counts and both
   over-100 counts from the 96 RDS.
2. **[Rule 1 - my harness] Membership check.** Slurm 2115173 reported 25 fits "not candidates". The cause was that
   `susie_get_cs` without Xcorr returns no `cs_index`. I fixed the check to match by component name and reran
   (2115237).
3. **[Rule 4 -> Carter Q-158DFX] FULL run 1 failed 1 id.** Run 1 was Slurm 2115350 at HEAD cf02643d.
   test_a1_allvars_secondary::test_confirmatory_tables_unchanged runs the PRE_157D_REF run_aggregation against today's
   estimands. That run_aggregation does not pass the new required argument, so it raised a TypeError before writing
   any table. check_15_8d.py CHECK FAIL (check_15_8d_run1.txt; junit kept as full_15_8d_run1_2115350.xml). Carter
   chose to fix the test. b1b5aa00 gives the pre-157d module an estimands proxy whose `e7_frozen_vs_fixed` passes the
   committed manifest. The four confirmatory tables are still compared byte for byte, and
   `git diff --quiet cf02643d -- src` is rc 0. NCs (Slurm 2117242): wrapper removed -> TypeError; e1_paired_delta
   reversed in the current aggregation -> byte diff; md5-restored.
4. A second planned-file-list deviation: test_qtl_legacy_rule_and_e7_rounding.py was edited. Its `_e7` helper is a
   fixture builder, and the column-order test is declared, because the plan puts the new E7 column last.
5. FULL run 2 used `--mem=64G`, the orchestrator's resource change after run 1's seff peak of 48/48 GB. Run 2's seff
   peak was 64.00/64 GB. It also completed with exit 0, but memory sits at the limit, so the sampled figure may
   include page cache. Flag for 15.8e sizing.

## Negative controls (all md5-restored)

- nc_15_8d.txt (Slurm 2115317): frozen back to n_cs_L -> tests 1, 3 fail; silent fallback on a missing row -> test 4;
  manifest dropped from LOCKED_PATHS -> test 5; tmp copy with asthma.AFR.9p21_CDKN2A n_cs_exact 0 -> 1, test 6 pointed
  at it -> test 6. ALL NCs FAILED AS REQUIRED AND RESTORED.
- nc_15_8d_dfx.txt (Slurm 2117242): the two Q-158DFX NCs above.
- check_15_8d.py: run 1's CHECK FAIL on a real failure is its negative control.

## FULL

- RED red_15_8d.txt: 6/6 failed. Green Slurm 2115273: 141 P.
- FULL run 2 (Slurm 2117279, c026n02 Cascade Lake, HEAD b1b5aa00, 2h36m, 64G): QUICK 908 P / 2 S, HEAVY 355 P / 5 S,
  PINS 39 P; FULL 2,764 = 2,711 P / 53 S / 0 F (full_15_8d.xml, sha256 849b31a2…9761e4); check_15_8d.py vs
  full_15_8c2.xml (2,758 read from the file): 0 removed, +6 all passed, 0 outcome changes, 3 declared passed ->
  passed, CHECK PASS (check_15_8d.txt). sparse_parent_benchmark.tsv restored.
- Base for 15.8e = data/r4/tmp/w3f/q158/full_15_8d.xml.

## New test ids

tests.ta_r4.test_e7_filtered_counts::test_frozen_value_is_the_purity_filtered_count
tests.ta_r4.test_e7_filtered_counts::test_unfiltered_json_count_is_kept_in_its_labelled_column
tests.ta_r4.test_e7_filtered_counts::test_changed_compares_filtered_with_filtered
tests.ta_r4.test_e7_filtered_counts::test_missing_or_mismatched_filtered_row_raises
tests.ta_r4.test_e7_filtered_counts::test_filtered_manifest_is_a_locked_path
tests.ta_r4.test_e7_filtered_counts::test_exact_purity_manifest_matches_the_stored_counts

## Declared spec updates

tests.ta_r4.test_estimands::test_e7_frozen_vs_fixed_and_flipped_shares
tests.ta_r4.test_qtl_legacy_rule_and_e7_rounding::test_e7_qtl_tier_has_the_matched_rounding_columns
tests.ta_r4.test_a1_allvars_secondary::test_confirmatory_tables_unchanged

(The first: the fixture gains the filtered table, and the assertion checks the filtered frozen value and the unfiltered
column. The second: E7 gains a last column, so the slices become [-3:-1] / [:-3]. The third: Carter Q-158DFX,
W3f-carter-15-8-Q-158DFX-reply-2026-11-26.txt, sha256
dbe60868e73171d992d6bb204070cc372608a9cb7489b35c865168bbcbac154d.)

## Known Stubs

None.

## Not done (by rule)

No production fit, no OSF, no lock, no push; decision_rules.yaml locked: false, n_regions_min 7; no re-pin.
NEXT = 15.8e.

## Self-Check: PASSED

Commits ca776492, f9afd684, cf02643d, b1b5aa00 exist; the test file, both manifests, full_15_8d.xml, red/nc/check
records exist; check_15_8d.py CHECK PASS; `git diff --quiet cf02643d -- src` rc 0; decision_rules.yaml locked: false.
