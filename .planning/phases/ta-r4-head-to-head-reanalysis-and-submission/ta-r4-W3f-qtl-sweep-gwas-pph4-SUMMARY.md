---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7g
subsystem: ta-r4 QTL tiering (W3f review F3), shared with Track B
tags: [assign-tiers, pph4-sweep, nan-rule, q-f3, q-f3b, track-b-shared]
requires: [ta-r4-W3f-purity-determinism]
provides: [assign_tiers GWAS-table sweep, assign_tiers --nan-gwas-below-threshold, assign_tiers.best_gwas, run_qtl_group_r4.tiers_argv, W6 NaN-GWAS tripwire]
affects: [ta-r4-W3f-null-window-reselection, Track B qtl_coloc.smk assign_tiers sweep output, W6 / E7 QTL_legacy comparator, DRAFT (l)]
tech-stack:
  added: []
  patterns: [must-be-identity test (sweep == full mode at every threshold), PRE-ref literal loaded with git show for byte identity]
key-files:
  created:
    - tests/ta_r4/test_qtl_sweep_gwas_pph4.py
  modified:
    - src/python/assign_tiers.py
    - src/python/ta_r4/run_qtl_group_r4.py
    - src/snakemake/rules/ta_r4_qtl.smk
    - tests/ta_r4/test_qtl_fallback_export.py
    - .planning/DECISIONS.md
    - .planning/HANDOFF.json
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/deferred-items.md
decisions:
  - "DEC-2026-11-20-ta-r4-qtl-sweep-gwas-pph4: Carter Q-F3 = B: Fix the sweep for Track B too; Q-F3B = A: Keep it as today, logged as the legacy rule (Recommended). Track B assign_tiers sweep output changes by Carter's choice"
  - "The NaN rule is opt-in (--nan-gwas-below-threshold), passed only by r4_qtl_tiers through tiers_argv; Track B full mode is unchanged"
  - "GWAS-table sweep rows: one per (threshold, ancestry) over the GWAS ancestries, then any QTL-only ancestry with zero counts (full mode has no row for it)"
commits: [90cf52d7, 7405ba4a]  # + the 15.7g records commit
completed: 2026-11-21
---

# Phase ta-r4 Plan 15.7g: W3f QTL sweep uses the GWAS PP.H4 Summary

The PP.H4 threshold sweep now applies the tier definitions to the GWAS PP.H4 whenever a GWAS table is given, for Track
B and r4. Before, `assign_tiers.py:96` passed the best QTL PP.H4 as the GWAS value, so Codex's example (GWAS 0.1,
QTL 0.9) counted as Tier A at 0.8. Now it is below threshold. The sweep equals full-mode tiering at every sweep value;
a must-be-identity test checks this on 25 randomized frames, with and without the NaN rule. A sweep with no GWAS table
keeps the legacy rule unchanged and logs it (Carter Q-F3B A). Under the r4-only flag, a NaN best GWAS PP.H4 is below
threshold.

## Gates

- `gate_reply.py Q-F3 --question <plan text> --sha256 f8694860…664703 "B: Fix the sweep for Track B too"`: printed the
  label and sha256, rc 0.
- `gate_reply.py Q-F3B --question <plan text> --sha256 b744a828…1cc1b "A: Keep it as today, logged as the legacy rule
  (Recommended)"`: printed the label and sha256, rc 0.
- Both ran before any edit (`$Q/gate_15_7g.txt`). Start sha 62353dbe (`$Q/start_15_7g.txt`), used in the test as the
  literal `PRE_157G_REF`. assign_tiers.py there is as last changed in 8fcade77.
- 90cf52d7: DEC-2026-11-20-ta-r4-qtl-sweep-gwas-pph4. It quotes both replies and states that Track B output changes
  by Carter's choice.

## Track B impact (step 1)

- No Track B tier artifact is on disk, so the number of Track B rows that change cannot be measured. **Not measurable:
  no artifact.**
- Read-only search by md5 for `17ff46dbbfe78dd537d6b9bff7f3ae67`, the only surviving record of
  results/qtl_coloc/tier_assignments.tsv. `$Q/trackb_md5_search_15_7g.sh`, Slurm 2016136, ran over results/,
  /share/clintonlab/ckclinto and /rs1/researchers/c/ckclinto (depth 6, symlinks followed, files named `*tier*`).
  **60 candidates, 0 hits** (`$Q/trackb_md5_search_15_7g.txt`). No copy exists, so there are no inputs to recompute
  from.
- Track B callers: rule `assign_tiers` (qtl_coloc.smk, `--gwas-coloc`) now gets the fixed sweep. Rule
  `pph4_threshold_sweep` (negative_controls.smk, no GWAS table) keeps the legacy sweep and logs a warning; this is
  logged in deferred-items.md. Neither rule file, `config/` nor tests/phase2 changed (`git diff 62353dbe HEAD`).

## RED → GREEN

- RED (`$Q/red_15_7g.txt`, `$Q/red_15_7g.xml`, Slurm 2016160, cascadelake c020n01): 10 failed / 1 passed, as planned.
  - Tests 1-8, 10 and 11 failed on the defect. They failed on the missing `best_gwas`, `nan_below` and `tiers_argv`
    (AttributeError / TypeError), on test 7's sweep counts (the CLI sweep tiered R1 by its QTL value), and on test
    8's missing legacy warning.
  - Test 9 (full mode without the flag is byte-identical to PRE_157G_REF) passed, as planned.
- GREEN, 7405ba4a:
  - `assign_tiers.py`:
    - `assign_tier(..., nan_below=False)`.
    - `best_gwas()`, the full-mode GWAS best-table block moved out unchanged.
    - `log_nan_gwas()` logs `NaN-GWAS groups: N (region, ancestry) with a NaN best GWAS PP.H4 [full|sweep]`.
    - `sweep_tiers(..., tier_b_min=0.5, gwas_best=None, nan_below=False)`. With `gwas_best`, each threshold applies
      assign_tier to (best GWAS, best QTL) over the GWAS (region, ancestry) groups, as full mode does. Without it,
      the warning is logged and `_legacy_sweep_tiers` (the pre-15.7g body, unchanged) runs, never given nan_below.
    - `assign_tiers_full(..., nan_below=False)`.
    - `main`: `--nan-gwas-below-threshold`. The sweep gets the GWAS best table and the config's
      `tier_definitions.tier_b.min_pph4_qtl` when the `--gwas-coloc` table is loaded and non-empty; otherwise it takes
      the legacy path.
  - `run_qtl_group_r4.tiers_argv(summary, gwas, pph4, tiers, sweep, py)` builds
    `[py, src/python/assign_tiers.py, --input, …, --gwas-coloc, …, --pph4-config, …, --output, …, --sweep,
    --sweep-output, …, --nan-gwas-below-threshold]`. Rule `r4_qtl_tiers` renders it as `params.tiers` (shlex.join).
    The `assign_tiers.py --input <summary>` order is kept, so test_rendered_jobs_aggregate_with_method_columns_and_tier_the_tierable_file
    still matches.
  - Task 1 verify set (Slurm 2016337, then 2016424 after the DRAFT edit): 108 passed / 2 skipped / 0 failed.
    Track B rule files and config/ are unchanged. test_amendment_text: 21 passed / 2 skipped.

## Negative controls

Mutation NCs on the GREEN source (`$Q/mutation_nc_15_7g.py`, Slurm 2016362, cascadelake c020n01). Each mutation ran
the 11 new tests, the declared id and both phase2 files (40 tests). Each failed exactly its predicted set, which was
written before the run. All three source files were md5-restored, and `md5sum -c $Q/pre_mut_15_7g.md5` was OK. No
phase2 test failed under any mutation.

| Mutation | Failed (exactly) |
|---|---|
| M1 main never passes the GWAS table to the sweep | 7, declared id |
| M2 GWAS sweep uses the QTL value as the GWAS value | 1, 2, 3, 6, 7 |
| M3 assign_tier ignores nan_below | 5, 6 |
| M4 legacy sweep applies the NaN rule | 8 |
| M5 legacy warning removed | 8 |
| M6 full-mode default applies the NaN rule | 5, 9 |
| M7 GWAS sweep ignores the config tier_b_min | 7 |
| M8 tiers_argv drops the flag | 11 |
| M9 rule bypasses tiers_argv (old inline shell) | 11 |
| M10 NaN-GWAS count not logged in full mode | 10 |
| M11 GWAS sweep skips regions without a QTL row | 2, 3, 4, declared id |
| M12 empty GWAS table sent down the GWAS path | 8 |
| M13 GWAS sweep ignores nan_below | 2, 3, 6 |

## QTL_legacy (E7's frozen comparator)

- qtl_tiers.tsv is full-mode output, so the sweep fix cannot move it. The sweep fix changes only qtl_tiers_sweep.tsv.
- Measured (`$Q/qtl_legacy_tiers_15_7g.py`, Slurm 2016384). On 200 randomized frames with method-`none` GWAS rows,
  the r4 call shape (`tiers_argv`, flag on) was compared with PRE_157G_REF's CLI, with 0 violations:
  - Every qtl_tiers.tsv row that moved had a NaN best GWAS PP.H4 (194 rows in the 126 frames that had a NaN-GWAS group).
  - Every frame without a NaN-GWAS group was byte-identical.
  - Without the flag, all 200 frames were byte-identical.
  - Nothing measured shows QTL_legacy moving through the sweep fix, so there was no STOP.
- Not measurable on real data: QTL_legacy has no outputs, and `coloc_inputs` finds 0 of 100 repro_routeL pair JSONs
  on disk (the same holds for QTL_A3 and QTL_A2; `$Q/nan_rule_real_inputs_15_7g.txt`).
- Planning bound re-measured from the repro_routeL fit JSONs (`$Q/qtl_legacy_bound_15_7g.txt`), the same as at
  planning:
  - In all 10 QTL regions, at least 3 of 5 EUR fits completed.
  - APOL1_22q12 (stroke, t2d), BMI_5q13_3 (stroke) and MC4R_18q21 (stroke) each have a completed 0-set fit, so a
    finite fallback pair exists there.
- HANDOFF `do_not` gained one string (13 → 14; every existing string kept). It is the W6 tripwire: if any
  `NaN-GWAS groups: N` line in data/r4/logs/QTL_legacy/qtl_tiers.log has N > 0, STOP for Carter before E7.

## NaN rule: affected-group count

- The count is logged in every mode: full and sweep, with and without the flag, and on the legacy no-table run, where
  full mode logs 0. Test 10 checks this, and M10 shows it can fail.
- Real r4 inputs: **not measurable.** 0 of 100 trait-pair coloc JSONs exist for each QTL arm, so no real group count
  exists before W5a/W6. The W6 tripwire reads the logged count.
- Fixtures: `_nan_frames` gives 2 NaN-GWAS groups (logged 2 in full and in the sweep). In the QTL_legacy measurement,
  126 of 200 frames had at least one NaN-GWAS group, and 194 rows moved, all of them NaN-GWAS rows.

## DRAFT (l)

`$Q/draft_15_7g.py` (old string asserted unique, 1 occurrence). "and in the PP.H4 threshold sweep a region with no
`coloc_susie` row is not counted in any tier" became the plan's sentence: "the PP.H4 threshold sweep applies the tier
definitions at each threshold to the region's best trait-pair PP.H4 and best `coloc_susie` QTL PP.H4, as the primary
tiering does, and a region whose trait-pair rows have no PP.H4 (all method `none`) is below threshold". This sentence
is the DRAFT clause for the NaN rule. test_amendment_text: 21 passed / 2 skipped.

## Task 2: FULL

Slurm 2016509 (cascadelake c020n01, HEAD 7405ba4a, `sbatch --wait`; `$Q/close_15_7g_2016509.out`): QUICK 849 P / 2 S;
HEAVY 328 P / 5 S; PINS 39 P; FULL **2,678 = 2,625 P / 53 S / 0 F** (`$Q/full_15_7g.xml`).

Against full_15_7f.xml (`$Q/check_15_7g.txt`, `$Q/cmp_15_7g.txt`):
- 0 ids removed.
- 11 ids added, all passed: exactly the 11 new tests (`$Q/new_tests_15_7g.txt`).
- 0 outcome changes, including 0 in tests/m3 and 0 in tests/phase2 (ids and outcomes identical; the 6 phase2 sweep
  ids passed in both).
- The declared spec update went passed → passed.

check_15_7g.py: PASS, rc 0. Its 3 NCs each FAIL with rc 1 (`$Q/check_15_7g_nc.txt`): base as new; a synthetic failure
on the declared id; a synthetic failure on a phase2 sweep id. src/ and tests/ are clean.

No push, no production fit, decision_rules.yaml `locked: false`, no OSF posting, n_regions_min 7.

## Declared spec updates

tests.ta_r4.test_qtl_fallback_export::test_tiers_from_tierable_equal_tiers_from_full

What changed: the sweep assertions only, plus the docstring sentence that described the old sweep. The tier-table
assertions are unchanged, the id is kept, and it went passed → passed. Values were derived by hand from the fixture
and recorded before the edit (`$Q/spec_update_15_7g.txt`):
- GWAS table: R1 0.92, R2 0.85. Best QTL PP.H4: R1 0.9 on both summaries; R2 has none on either (blank on the full
  summary, no row on the tierable one). tier_b_min 0.5.
- R1 is Tier A at 0.5, 0.7, 0.8 and 0.9. R2 is Tier C at 0.5-0.8 and below threshold at 0.9.
- (n_tier_a, n_tier_b, n_tier_c): 0.5 (1,0,1), 0.7 (1,0,1), 0.8 (1,0,1), 0.9 (1,0,0), the same on both summaries.
- The old assertion was full (1,0,1) and tierable (1,0,0) at every threshold.
- In this fixture the full summary's sweep does not differ from the tierable one. The plan allowed a difference
  through R2's fallback row, but that row's PP.H4.abf is blank in the summary.
The measured GREEN values equal the hand derivation.

## New tests (11)

tests/ta_r4/test_qtl_sweep_gwas_pph4.py:
1. test_codex_example_is_below_threshold
2. test_sweep_at_primary_equals_full_mode_counts (identity; 25 frames x flag on/off)
3. test_sweep_equals_full_mode_at_every_threshold
4. test_region_with_gwas_but_no_qtl_row_is_tier_c
5. test_nan_gwas_is_below_threshold_in_full_mode_under_the_flag
6. test_nan_gwas_is_below_threshold_in_the_sweep_under_the_flag
7. test_cli_with_gwas_table_uses_it_in_the_sweep (also checks the config's tier_b_min is used)
8. test_gwas_less_sweep_unchanged_and_warns (PRE_157G_REF sweep_tiers and CLI, 25 frames with all-NaN groups, with
   and without the flag)
9. test_full_mode_without_the_flag_is_byte_identical (PRE_157G_REF; function and CLI)
10. test_nan_gwas_group_count_is_logged
11. test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order (r4_heavy: reads the rendered r4_qtl_tiers job)

The 6 phase2 sweep ids are not edited and stay passed.

## Deviations from Plan

1. **Test 11 is r4_heavy.** It checks the rendered `r4_qtl_tiers` command from the module-scoped Snakemake dry-run
   (test_in_job_gate's `rendered` fixture), not the rule's source text. The id and count are unchanged.
2. **`sweep_tiers` has a `nan_below` keyword** in addition to the plan's signature. The plan's NaN rule in the
   GWAS-table sweep needs it. The legacy path ignores it, which test 8 and M4 check.
3. **Sweep ancestry rows.** With a GWAS table, rows cover the GWAS ancestries and then any QTL-only ancestry, with
   zero counts. This keeps today's per-QTL-ancestry rows and still equals full mode, which has no rows for such an
   ancestry.
4. **Declared spec update docstring.** The docstring sentence that described the old sweep was also updated, so the
   test no longer states false behaviour. No assertion other than the sweep block changed.
5. **Extra evidence beyond the plan:** 13 mutation NCs, the QTL_legacy synthetic measurement, the planning-bound
   re-measurement and check_15_7g NCs. A second read-only md5 search with progressive logging (Slurm 2016510) was
   submitted in case the first hit its 1 h limit; it was cancelled as redundant once the first finished. By then it had searched only results/:
   4 candidates, 0 hits (`$Q/trackb_md5_search2_15_7g_2016510.out`).
6. **Task 1 verify was re-run** after the DRAFT edit. The first GREEN run came before it.

## Known Stubs

None.

## Self-Check: PASSED

All created and modified files and the scratch evidence files exist; commits 90cf52d7 and 7405ba4a exist; HANDOFF do_not has 14 strings; decision_rules.yaml is `locked: false`.
