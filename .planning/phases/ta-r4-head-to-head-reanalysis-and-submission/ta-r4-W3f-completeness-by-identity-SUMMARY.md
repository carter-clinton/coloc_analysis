---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7b
subsystem: ta-r4 aggregation completeness / QTL runner (W3f review F4, F6, F7)
tags: [completeness-by-identity, simulation-seeds, config-sha256, qtl-manifest, coloc-susie-none, id-reconcile]
requires: [ta-r4-W3f-runtime-config-guard]
provides: [ta_r4.id_reconcile, run_aggregation._sim identity checks, run_aggregation._qtl_coverage, tierable_summary manifest reconcile, QTL empty-summary none mapping]
affects: [ta-r4-W3f-cross-purity-variant-resolution, W7 aggregation, W6 QTL layer]
tech-stack:
  added: []
  patterns: [reconcile observed ids against the design set (missing / extra / duplicated), Python mirror of an R index checked as a full table against R]
key-files:
  created:
    - src/python/ta_r4/id_reconcile.py
    - tests/ta_r4/test_id_reconcile.py
    - tests/ta_r4/test_sim_completeness_identity.py
    - tests/ta_r4/test_qtl_coverage_at_aggregation.py
    - tests/ta_r4/test_qtl_empty_summary_is_none.py
  modified:
    - src/python/ta_r4/run_aggregation.py
    - src/python/ta_r4/run_qtl_group_r4.py
    - src/snakemake/rules/ta_r4_qtl.smk
    - tests/ta_r4/test_run_aggregation.py
    - tests/ta_r4/test_sim_by_method_and_cells.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
decisions:
  - "_sim checks identity only after the per-arm row count matches (count mismatch keeps its existing message); seed checks skip rows whose rep is not a valid 1..reps integer, which the rep-id check already reports"
  - "--manifest of run_qtl_group_r4 has no default any more; the group and gwas-coloc-table subcommands fall back to harmonize_qtl_r4.MANIFEST, --tierable-summary reconciles only when the flag is given"
commits: [5fce26a8]  # + the 15.7b records commit
completed: 2026-11-20
---

# Phase ta-r4 Plan 15.7b: W3f completeness by identity Summary

FINAL now needs the simulation and QTL result sets to match their design by identity, not by count. `ta_r4.id_reconcile` reconciles observed ids against the expected set (missing, extra, duplicated). It also has `stable_index`, the Python copy of the harness's replicate index, which test 14 checks against R over the full 20,000-value table.

- **F4.** `run_aggregation._sim` now checks every status-ok cell. Each arm must have replicate ids exactly 1..reps once each. Every row's region, scenario and gen_panel must equal the cell. Every seed must equal seed_base + stable_index. Every header line is parsed as space-separated k=v tokens (`sim_header`). The header must give the cell's region, scenario and gen_panel, `reps` equal to the configured count, and `config_sha256` equal to the sha256 of the repo's simulation.yaml (checked for every status). Codex's probe (copies of replicate 1) is refused.
- **F6.** `_qtl_coverage` replaces `_qtl_missing`. For each QTL arm it checks that the summary and tier table exist, that the summary ids reconcile with qtl_manifest.tsv, and that no method is empty. It also reconciles the QTL_A3 JSON doc ids. FINAL refuses with exit 3; DRAFT prints. `r4_qtl_aggregate` passes `--manifest {input.manifest}` to `--tierable-summary`, which reconciles before it writes anything.
- **F7.** In `run_row`, a success whose summary is empty or absent is now method `none` with status `coloc_susie_empty`. A success whose summary has no finite PP.H4.abf is `none` with `coloc_susie_no_finite_h4`. Both keep `qtl_r_status: success`. These rows are not tierable, and the aggregate exports the reason as none_status.

aggregate_qtl_coloc.py, run_qtl_coloc.R, simulate_coloc_r4.R, config/ and the Track B files are unchanged.

## Task 1 (5fce26a8)

- Re-measured as planned (`data/r4/tmp/w3f/q157/measure_15_7b.txt`).
- RED: 20 F / 4 P, exactly the planned split (green 1, 5, 14a, 15). 14b failed on ImportError. Its NC ran the 14b assertion against the start parser and FAILs (region / scenario / gen_panel / reps / config_sha256 lost).
- GREEN: Task 1 verify 82 P. test_in_job_gate, test_confirmatory_completeness and test_job_guard: 60 P, 0 changes.
- AST no-weaken PASS (only build_tree, final_repo, _cell, sim_repo changed; new helpers only). Its NC (one weakened assertion) FAILs.

## Task 2 (5fce26a8 + records)

- RED: 6 F / 1 P as planned (27 green). GREEN: 7 P.
- 10 mutation NCs, each failing its named enforcers; source md5-restored after each.
- DRAFT (l): one sentence. (g) unchanged; it already matches the check. test_amendment_text 21 P / 2 S.
- FULL (Slurm 2008417, sbatch --wait, cascadelake c020n03, HEAD 5fce26a8):
  - QUICK 804 P / 2 S; HEAVY 313 P / 5 S; PINS 39 P.
  - FULL **2,618 = 2,565 P / 53 S / 0 F**.
  - vs full_15_7a.xml: removed 0, added 31 (all passed), outcome changes 0, tests/m3 0.
  - check_15_7b.py PASS; its NCs (base as new; synthetic failed pre-existing id) FAIL.

## New tests (31)

- `tests.ta_r4.test_id_reconcile::test_reconcile_exact_set_ok`
- `tests.ta_r4.test_id_reconcile::test_reconcile_reports_missing`
- `tests.ta_r4.test_id_reconcile::test_reconcile_reports_extra`
- `tests.ta_r4.test_id_reconcile::test_reconcile_reports_duplicates`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_accepts_a_correct_cell`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[copies_of_rep1]`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[rep_out_of_range]`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[wrong_region_label]`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[wrong_scenario_label]`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[wrong_gen_panel_label]`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[wrong_seed]`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[config_sha256_mismatch]`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_rejects[missing_config_sha256]`
- `tests.ta_r4.test_sim_completeness_identity::test_stable_index_matches_the_r_harness`
- `tests.ta_r4.test_sim_completeness_identity::test_stable_index_with_swapped_dimensions_differs_from_the_r_harness`
- `tests.ta_r4.test_sim_completeness_identity::test_sim_header_parsed_from_the_r_format`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_qtl_summary_matching_manifest_passes`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_qtl_coverage_flags[missing_row]`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_qtl_coverage_flags[extra_row]`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_qtl_coverage_flags[duplicate_row]`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_qtl_coverage_flags[empty_method]`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_final_refuses_on_a_qtl_coverage_gap`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_tierable_step_refuses_an_incomplete_summary`
- `tests.ta_r4.test_qtl_coverage_at_aggregation::test_a3_json_docs_reconciled`
- `tests.ta_r4.test_qtl_empty_summary_is_none::test_success_with_empty_summary_is_method_none[empty_list]`
- `tests.ta_r4.test_qtl_empty_summary_is_none::test_success_with_empty_summary_is_method_none[empty_dict]`
- `tests.ta_r4.test_qtl_empty_summary_is_none::test_success_with_empty_summary_is_method_none[null_h4]`
- `tests.ta_r4.test_qtl_empty_summary_is_none::test_success_with_empty_summary_is_method_none[nan_h4]`
- `tests.ta_r4.test_qtl_empty_summary_is_none::test_success_with_finite_summary_stays_coloc_susie`
- `tests.ta_r4.test_qtl_empty_summary_is_none::test_none_row_is_not_tierable`
- `tests.ta_r4.test_qtl_empty_summary_is_none::test_aggregate_exports_the_none_reason`

## Declared spec updates

none

## Deviations from Plan

1. **[Rule 3] `sbatch --wait` instead of srun.** As in 15.7a, FULL ran with the same partition, account, QOS, `--constraint=cascadelake` and wall time.
2. **[Rule 2] Helpers not in <interfaces>:** `run_aggregation.sim_header` (the k=v header parser; test 14b calls it), `_sim_identity`, `_qtl_doc_ids`, `QTL_MANIFEST`, and `run_qtl_group_r4._empty_reason`.
3. **Fixture detail:** `final_repo` calls `_write_sim` again after `write_fixture_lock`. The lock commit rewrites simulation.yaml (`locked: true`), which changes its sha256. It also commits the fixture qtl_manifest.tsv. build_tree writes 2 QTL_A3 JSON docs so the A3 doc reconciliation has its design set.
4. **_sim order of checks:** identity checks run only after the existing per-arm row-count check passes. A count mismatch keeps its existing single message, and that check is not weakened.
5. **NC bookkeeping:** two predictions in mutation run 1 were wrong (M1, M4). These were not code defects. M4 was split into M4a / M4b; both runs are kept. The first synthetic-XML NC was malformed (ParseError); it was rebuilt with ElementTree.

## Known Stubs

None.

## Threat Flags

None. The checks narrow the existing aggregation surface.

## Self-Check: PASSED

Files and commit 5fce26a8 present; 31 new ids listed; decision_rules.yaml locked: false; config/ and the shared scripts unchanged.
