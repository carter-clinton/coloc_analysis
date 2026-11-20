---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7g
slug: W3f-qtl-sweep-gwas-pph4
type: execute
wave: 15.7g
depends_on: ["ta-r4-W3f-purity-determinism"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md
  - src/python/assign_tiers.py
  - src/python/ta_r4/run_qtl_group_r4.py
  - src/snakemake/rules/ta_r4_qtl.smk
  - tests/ta_r4/test_qtl_sweep_gwas_pph4.py
  - tests/ta_r4/test_qtl_fallback_export.py      # declared spec update
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/deferred-items.md
  - .planning/HANDOFF.json
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-sweep-gwas-pph4-SUMMARY.md
autonomous: true
requirements:
  - REQ-PP.H4-THRESHOLD-SWEEP

must_haves:
  truths:
    - "Gates: Q-F3 prints \"B: Fix the sweep for Track B too\" with the <question> text and sha256; Q-F3B prints \"A: Keep it as today, logged as the legacy rule (Recommended)\", each with its <question> text and sha256; otherwise nothing is edited"
    - "assign_tiers.py, for every caller that supplies a GWAS table (Track B rule assign_tiers and r4 rule r4_qtl_tiers both pass --gwas-coloc): the sweep at each threshold t applies the full-mode tier definitions to (best GWAS PP.H4 per (region, ancestry), best QTL PP.H4), iterating over GWAS regions as full mode does, with tier_b_min from the config; Codex's example (GWAS 0.1, QTL 0.9) is below_threshold at 0.8"
    - "At t = primary_threshold the sweep counts equal the full-mode tier table's counts (must-be-identity), and at every sweep value when full mode is run at that threshold"
    - "NaN rule, r4 only, behind an opt-in flag: with `--nan-gwas-below-threshold` (passed only by the r4 rule through tiers_argv), a NaN or missing best GWAS PP.H4 is below_threshold in full mode and in the GWAS-table sweep (measured at planning: assign_tier(nan, 0.9, 0.8) returns 'Tier A'). Without the flag, full mode is byte-identical to PRE_157G_REF on any input, NaN groups included, so Track B output changes only through the sweep fix. assign_tiers logs the number of (region, ancestry) groups with a NaN best GWAS PP.H4 in every mode"
    - "The no-table legacy sweep path bypasses the NaN rule even under the flag: it is PRE_157G_REF's code path unchanged"
    - "Per Q-F3B A: a sweep without a GWAS table (Track B rule pph4_threshold_sweep, negative_controls.smk:111-132; the 6 phase2 sweep tests) returns exactly what PRE_157G_REF returns (on frames that include all-NaN groups too) and logs a warning naming the legacy QTL-as-GWAS rule; 0 phase2 ids change; the defect is logged in deferred-items.md"
    - "Track B impact is recorded: no Track B tier artifact is on disk (planning searched results/, /share/clintonlab/ckclinto and /rs1 to depth 6; only the md5 record 17ff46dbbfe78dd537d6b9bff7f3ae67 of results/qtl_coloc/tier_assignments.tsv survives), so the number of Track B rows that change cannot be measured; the executor repeats the search by md5 and, if a copy and its inputs exist, recomputes the count"
    - "QTL_legacy (E7's frozen comparator): its qtl_tiers.tsv is full mode, so the sweep fix does not touch it; the NaN rule moves it only if every GWAS pair in a QTL region is method none. Not measurable before W6 (no repro_routeL pair outputs exist). Bound at planning: in all 10 QTL regions ≥ 3 of 5 repro_routeL EUR fits completed, and in APOL1_22q12, BMI_5q13_3 and MC4R_18q21 a completed fit has 0 sets, so a finite fallback pair exists there. A HANDOFF W6 tripwire is added: if QTL_legacy's tiers log a NaN-GWAS group, STOP for Carter before E7"
    - "One declared spec update: tests.ta_r4.test_qtl_fallback_export::test_tiers_from_tierable_equal_tiers_from_full asserts the old sweep (R2, which has no coloc_susie QTL row, counted as Tier C on the full summary through NaN comparisons). After the fix R2 is tiered from the GWAS table (GWAS PP.H4 0.85): Tier C at 0.5-0.8 on the tierable summary and below threshold at 0.9, and the full summary's sweep can differ from the tierable one through R2's fallback row. Its sweep assertions are rewritten to the values full-mode tiering gives at each threshold on each summary (derived by hand from the fixture and recorded in the SUMMARY before the edit); its tier-table assertions are unchanged; id kept, passed"
    - "run_qtl_group_r4.tiers_argv keeps the rule's argument order (`assign_tiers.py --input <summary> --gwas-coloc … --pph4-config … --output … --sweep --sweep-output …`), so test_in_job_gate's rendered-jobs check still matches"
    - "The 11 ids in <new_tests> pass; FULL vs full_15_7f.xml: 0 removed, added == <new_tests>, outcome changes 0 except the declared id (still passed; tests/phase2 unchanged); 2,678 = 2,625 P / 53 S / 0 F"
  artifacts:
    - path: "tests/ta_r4/test_qtl_sweep_gwas_pph4.py"
      provides: "the tests in <new_tests>"
  key_links:
    - from: "ta_r4_qtl.smk r4_qtl_tiers"
      to: "assign_tiers.py --gwas-coloc --sweep"
      via: "run_qtl_group_r4.tiers_argv(...)"
      pattern: "tiers_argv"
---

<objective>
Close F3 (CONFIRMED; Codex's example reproduced) with Carter's Q-F3 answer B, "Fix the sweep for Track B too":
`assign_tiers.py:96` calls `assign_tier(best_pph4, best_pph4, …)` in `sweep_tiers`, so the sweep treats the QTL PP.H4
as the GWAS value. Fix it in the shared file, for every caller with a GWAS table, together with the adjacent NaN defect
(`assign_tier(nan, 0.9, 0.8)` is "Tier A"). The fix changes Track B's `assign_tiers` sweep output; Carter chose that.

A sweep without any GWAS table (Track B's `pph4_threshold_sweep` rule and 6 phase2 tests) cannot apply the
definitions; per Carter's Q-F3B A it keeps today's behaviour, logged as the legacy rule.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-F3: file `W3f-carter-15-7-Q-F3-reply-2026-11-20.txt`, sha256 `f869486010dd063adadc2190d08574e793f5e372700560ec6093d71058664703`.
Question text: The QTL PP.H4 threshold sweep calls assign_tier(best_pph4, best_pph4, ...) at assign_tiers.py:96, using the QTL value as the GWAS value. assign_tiers.py is shared with Track B. All three options replace the DRAFT (l) sentence that describes the faulty sweep. Which fix?
Required label: `B: Fix the sweep for Track B too`

Q-F3B: file `W3f-carter-15-7-Q-F3B-reply-2026-11-20.txt`, sha256 `b744a8288ae8aff40ab4128a3eb3dbbd59c3b986deb3b4d3758b07b654b1cc1b`.
Question text: Under your Q-F3 B, the QTL sweep uses the GWAS table wherever one is given. Track B's pph4_threshold_sweep rule (negative_controls.smk) and 6 tests in tests/phase2 call the sweep with no GWAS table, where the tier definitions can't be applied. What should that no-table call do?
Required label: `A: Keep it as today, logged as the legacy rule (Recommended)`
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/python/assign_tiers.py
@src/snakemake/rules/ta_r4_qtl.smk

**Gates.** `$PY $Q/gate_reply.py Q-F3 --question … --sha256 … "B: Fix the sweep for Track B too"` and
`$PY $Q/gate_reply.py Q-F3B --question … --sha256 … "A: Keep it as today, logged as the legacy rule
(Recommended)"`. Either non-zero → STOP.

**Forbidden:** Track B rule files (`qtl_coloc.smk`, `negative_controls.smk`), `config/pph4_thresholds.yaml`,
`decision_rules.yaml`.

**Measured at planning:**
- Track B callers: qtl_coloc.smk rule `assign_tiers` (`--gwas-coloc`, so its sweep changes); negative_controls.smk rule
  `pph4_threshold_sweep` (no GWAS table). `results/multitrait/coloc_summary.tsv` (40 rows, 5 with PP.H4) has no
  `region`/`ancestry` columns, so Track B's rule cannot run on it as it stands; no Track B tier output is on disk.
- phase2 sweep tests, all without a GWAS table: `tests/phase2/test_pph4_sweep.py::TestSweepLogic::{test_tier_count_monotonicity,
  test_sweep_output_has_ancestry_column, test_sweep_produces_all_tiers, test_sweep_produces_4_thresholds}` and
  `tests/phase2/test_tier_assignment.py::TestSweepProducesThresholds::{test_sweep_produces_4_thresholds,
  test_sweep_monotonic_tier_a}`. phase2 full-mode fixtures have no NaN PP.H4, so `TestAssignTiersFull` and
  `TestAssignTierFunction` are unaffected.
- `config/pph4_thresholds.yaml` tier_b min_pph4_qtl 0.5 (= the sweep default).
</context>

<new_tests>
tests/ta_r4/test_qtl_sweep_gwas_pph4.py; N_new = 11.
1. `test_codex_example_is_below_threshold`
2. `test_sweep_at_primary_equals_full_mode_counts` (identity)
3. `test_sweep_equals_full_mode_at_every_threshold`
4. `test_region_with_gwas_but_no_qtl_row_is_tier_c`
5. `test_nan_gwas_is_below_threshold_in_full_mode_under_the_flag`
6. `test_nan_gwas_is_below_threshold_in_the_sweep_under_the_flag`
7. `test_cli_with_gwas_table_uses_it_in_the_sweep` (main with --gwas-coloc --sweep, the Track B and r4 call shape)
8. `test_gwas_less_sweep_unchanged_and_warns` (equal to PRE_157G_REF's sweep_tiers on randomized frames that include
   all-NaN groups, with and without the flag)
9. `test_full_mode_without_the_flag_is_byte_identical` (PRE_157G_REF literal; randomized frames including NaN groups)
10. `test_nan_gwas_group_count_is_logged`
11. `test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order`
The 6 phase2 sweep ids in <context> are not edited and keep their outcomes.
Declared spec update: `tests.ta_r4.test_qtl_fallback_export::test_tiers_from_tierable_equal_tiers_from_full` (sweep
assertions only, per must_haves).
Expected FULL: base full_15_7f.xml (2,667) + 11 = 2,678 = 2,625 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gates, DEC, shared sweep fix and NaN rule (RED first), records of Track B and QTL_legacy impact, DRAFT</name>
  <files>.planning/DECISIONS.md, src/python/assign_tiers.py, tests/ta_r4/test_qtl_fallback_export.py, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_qtl.smk, tests/ta_r4/test_qtl_sweep_gwas_pph4.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/deferred-items.md, .planning/HANDOFF.json, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - assign_tiers.py (whole); tests/phase2/test_pph4_sweep.py; tests/phase2/test_tier_assignment.py; ta_r4_qtl.smk :147-171
  </read_first>
  <action>
    0. Gates. `git rev-parse HEAD > $Q/start_15_7g.txt`; literal `PRE_157G_REF` in the test. DEC
       `DEC-2026-11-20-ta-r4-qtl-sweep-gwas-pph4` quoting both replies (committed in 15.7a); it states that Track B
       output changes by Carter's choice. Commit 1 (DECISIONS.md).
    1. Track B count: search again for a file with md5 17ff46dbbfe78dd537d6b9bff7f3ae67 (read-only, sbatch); if found
       with its inputs, compute old vs new tier rows and sweep rows and record; else record "not measurable: no
       artifact".
    2. RED: tests 1-11 (RED: 1-8, 10, 11; green: 9). Record.
    3. GREEN: `sweep_tiers(results_df, sweep_values, gwas_pph4_col="PP.H4.abf", tier_b_min=0.5, gwas_best=None)`;
       `main` passes the GWAS best table when `--gwas-coloc` is loaded and non-empty, and the config's tier_b_min; the
       NaN rule only under `--nan-gwas-below-threshold` (an `assign_tier(..., nan_below=False)` keyword the flag sets; the
       default path is PRE_157G_REF's); the NaN-group count logged in every mode; the GWAS-less path unchanged with the
       warning and never given nan_below. `run_qtl_group_r4.tiers_argv(...)` builds the r4 rule's command; the rule uses it.
    4. deferred-items.md: "Track B pph4_threshold_sweep (no GWAS table) keeps the legacy QTL-as-GWAS sweep (review
       F3; Q-F3B A); it is logged as legacy at run time". HANDOFF: add the W6 tripwire from
       must_haves under `do_not` / W6 notes (one key, every existing string kept).
    5. DRAFT (l): replace "and in the PP.H4 threshold sweep a region with no `coloc_susie` row is not counted in any
       tier" with "the PP.H4 threshold sweep applies the tier definitions at each threshold to the region's best
       trait-pair PP.H4 and best `coloc_susie` QTL PP.H4, as the primary tiering does, and a region whose trait-pair
       rows have no PP.H4 (all method `none`) is below threshold". test_amendment_text.py green. Commit 2.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_sweep_gwas_pph4.py tests/ta_r4/test_qtl_fallback_export.py tests/ta_r4/test_in_job_gate.py tests/phase2/test_pph4_sweep.py tests/phase2/test_tier_assignment.py tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider && git diff --quiet HEAD -- src/snakemake/rules/qtl_coloc.smk src/snakemake/rules/negative_controls.smk config/</automated>
  </verify>
  <done>Gates passed; sweep equals full mode at every threshold; NaN rule; Track B and QTL_legacy impact recorded; W6 tripwire; DRAFT matches.</done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm, per-id reconciliation vs full_15_7f.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-sweep-gwas-pph4-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7g: `$Q/check_15_7g.py` (removed 0; added == the 11; 0 outcome changes except the declared
    test_qtl_fallback_export id, still passed; tests/phase2 unchanged; 2,678 = 2,625 / 53 / 0). Records (STATE NEXT = 15.7h; NOT PUSHED;
    SUMMARY with ids and the Track B count result). fsck; commit 3.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7g.py && test -z "$(git status --porcelain -- src tests)"</automated>
  </verify>
  <done>FULL reconciled; records committed; no push.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| shared tiering script → Track B and the E7 comparator | the fix moves Track B output and could move frozen-comparator tiers |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157g-01 | Tampering | Track B outputs | accept | Carter chose B; DEC records it; count recorded when measurable |
| T-r4-157g-02 | Tampering | E7 comparator tiers | mitigate | sweep fix leaves full mode; NaN rule tripwire STOPs W6 for Carter |
| T-r4-157g-03 | Tampering | sweep semantics | mitigate | identity with full mode at every threshold (2, 3); flag-off byte identity (9) |
| T-r4-157g-04 | Tampering | Track B full-mode tiers | mitigate | NaN rule behind an r4-only flag; test 9 |
</threat_model>

<verification>
- check_15_7g.py passes; Track B rule files and config unchanged.
</verification>

<success_criteria>
- Every sweep with a GWAS table reproduces the tier definitions at each threshold, for Track B and r4.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-sweep-gwas-pph4-SUMMARY.md`
</output>
