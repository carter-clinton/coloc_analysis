---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7d
slug: W3f-a1-allvars-secondary
type: execute
wave: 15.7d
depends_on: ["ta-r4-W3f-cross-purity-variant-resolution"]
gap_closure: true
files_modified:
  - src/python/ta_r4/run_aggregation.py
  - tests/ta_r4/test_a1_allvars_secondary.py
  - tests/ta_r4/test_run_aggregation.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-a1-allvars-secondary-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "run_aggregation writes a 20th table `a1_allvars_secondary`, placed after `afr_secondary`: A1_allvars vs A3_1kg on the primary curated EUR row ids and A1_allvars vs AFR661_A3 on the AFR ids, per p12 key, built by estimands.e6_panel_contrast (E1 with n_snps medians, E2 over the sweep, E3, drops) with an ancestry column"
    - "row_drops gains family `a1_allvars` for the same two contrasts"
    - "Each E1 value in the table equals a direct estimands.e1_paired_delta(rows, 'A1_allvars', ref, k, rule, ids) + e1_summary computation (identity)"
    - "branch_outcomes, e1_paired_delta, e2_agreement_sweep and e3_reclassification are byte-identical to the start commit on the fixture (the confirmatory analysis does not move)"
    - "test_draft_writes_exactly_19_draft_tables is renamed test_draft_writes_exactly_20_draft_tables (declared rename; the TABLES tuple in tests/ta_r4/test_run_aggregation.py gains the table); one declared spec update: tests.ta_r4.test_run_aggregation::test_row_drops_and_long_e6_tables, whose `set(rd.family) == {confirmatory, e6, afr_secondary}` assertion gains `a1_allvars` (id kept, passed); every other pre-existing id keeps its outcome"
    - "FULL vs full_15_7c.xml: removed == exactly the one renamed id; added == the 6 <new_tests> + its successor; 0 outcome changes; 2,642 = 2,589 P / 53 S / 0 F"
  artifacts:
    - path: "src/python/ta_r4/run_aggregation.py"
      provides: "A1_ALLVARS contrasts, table a1_allvars_secondary, row_drops family a1_allvars"
    - path: "tests/ta_r4/test_a1_allvars_secondary.py"
      provides: "the 6 tests in <new_tests>"
  key_links:
    - from: "run_aggregation.build_tables"
      to: "estimands.e6_panel_contrast"
      via: "A1_ALLVARS_EUR / A1_ALLVARS_AFR contrast tuples"
      pattern: "A1_ALLVARS"
---

<objective>
Close F12 (CONFIRMED): `coloc_coverage.py:16` requires the A1 `allvars` outputs and D-21 / DRAFT (d) call them a
secondary row, but `run_aggregation.py:207-219` builds E1–E3 only for the confirmatory `a1_varset` (matched), and no
other family reports allvars; it appears only inside the pooled negative-control rates. Adding the report changes no
confirmatory number.

Output: one descriptive table built from the existing e6_panel_contrast estimator (the reusable path the AFR A1
contrast already uses), a drop-table family, 6 tests and one declared test rename. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/python/ta_r4/run_aggregation.py
@src/python/ta_r4/estimands.py

**Standing rules:** PLAN-INDEX §A, §B and the 15.7 shared protocol.

**Forbidden:** changing the confirmatory contrasts, `decision_rules.yaml`, the existing 19 tables' content.

**Measured at planning:**
- `run_aggregation.AFR` already holds `("A1_matched", "AFR661_A3", "matched", "AFR661_A3 method coloc_susie")`;
  `e6_panel_contrast` handles an X without fits.
- `estimands.build_rows`: A1 outputs have label `A1_matched` / `A1_allvars`, so the label selects the variant set.
- `tests/ta_r4/test_run_aggregation.py:22` TABLES tuple and `:134` `test_draft_writes_exactly_19_draft_tables`;
  `tests/ta_r4/test_confirmatory_completeness.py:12` imports that TABLES tuple (outcome must stay passed).
- Prior precedent for the rename: 17 → 18 (ade4e9c5), 18 → 19 (bed315d4).
</context>

<new_tests>
tests/ta_r4/test_a1_allvars_secondary.py; N_new = 6, plus one rename.
1. `test_allvars_table_has_both_ancestries_and_both_p12_keys`
2. `test_allvars_rows_are_the_primary_curated_and_afr_ids`
3. `test_allvars_e1_equals_a_direct_paired_computation` (identity)
4. `test_allvars_table_tracks_allvars_not_matched` (fixture where allvars and matched PP.H4 differ: the table follows
   allvars; RED if the code read matched)
5. `test_row_drops_has_the_a1_allvars_family`
6. `test_confirmatory_tables_unchanged` (the four confirmatory tables byte-equal to those written by run_aggregation.py
   at the literal commit `PRE_157D_REF`, the HEAD at 15.7d start written into the test as a constant, loaded with
   `git show PRE_157D_REF:src/python/ta_r4/run_aggregation.py` into tmp_path; no `$Q` file is read)
Rename: `tests.ta_r4.test_run_aggregation::test_draft_writes_exactly_19_draft_tables` →
`…::test_draft_writes_exactly_20_draft_tables`.
Declared spec update (id kept, passed): `tests.ta_r4.test_run_aggregation::test_row_drops_and_long_e6_tables`: the
expected family set becomes `{confirmatory, e6, afr_secondary, a1_allvars}`; nothing else in it changes.

Expected FULL: base full_15_7c.xml (2,636) − 1 + 7 = 2,642 = 2,589 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: a1_allvars_secondary table and drop family (RED first)</name>
  <files>src/python/ta_r4/run_aggregation.py, tests/ta_r4/test_a1_allvars_secondary.py, tests/ta_r4/test_run_aggregation.py, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - run_aggregation.py :27-56, :191-265; estimands.py :161-210, :551-597
    - tests/ta_r4/test_run_aggregation.py :1-145 (build_tree, TABLES, _run)
  </read_first>
  <behavior>See <new_tests>.</behavior>
  <action>
    0. `git rev-parse HEAD > $Q/start_15_7d.txt`; write that sha into the test as the literal `PRE_157D_REF`.
    1. RED: tests 1-6 (1-5 RED; 6 green; record).
    2. GREEN: `A1_ALLVARS_EUR = (("A1_allvars", "A3_1kg", "allvars", "A3_1kg method coloc_susie"),)`,
       `A1_ALLVARS_AFR = (("A1_allvars", "AFR661_A3", "allvars", "AFR661_A3 method coloc_susie"),)`;
       `t["a1_allvars_secondary"]` = concat of e6_panel_contrast over `ids` (EUR) and `afr_ids` (AFR), each with
       `ancestry`; TABLES gains it after `afr_secondary`; row_drops gains family `a1_allvars` (EUR and AFR). Rename
       the one test and extend its TABLES tuple; extend the family set in test_row_drops_and_long_e6_tables; change
       nothing else in either test.
    3. DRAFT (e): after the AFR sentence ("… are reported the same way."), add "A1 on all variants (`allvars`) is
       reported the same way against `A3_1kg` (EUR) and `AFR661_A3` (AFR), as a secondary descriptive comparison."
       Old string asserted unique; test_amendment_text.py green.
    4. Module and test_run_aggregation.py, test_confirmatory_completeness.py, test_reporting_widened.py green.
       Commit 1 (`feat(ta-r4-W3f): A1 allvars secondary table and drop family (15.7d, F12)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_a1_allvars_secondary.py tests/ta_r4/test_run_aggregation.py tests/ta_r4/test_confirmatory_completeness.py tests/ta_r4/test_reporting_widened.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider</automated>
  </verify>
  <done>Table and drop family present; confirmatory tables unchanged; one declared rename.</done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm, per-id reconciliation vs full_15_7c.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-a1-allvars-secondary-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7d: `$Q/check_15_7d.py` asserts removed == {the _19_ id}, its successor present
    and passed, added == the 6 + successor, 0 outcome changes (the declared id stays passed), 2,642 = 2,589 / 53 / 0. Records (LOG, STATE NEXT =
    15.7e, NOT PUSHED; PLAN-INDEX COMPLETE; SUMMARY with the rename and a `## Declared spec updates` section naming test_row_drops_and_long_e6_tables). fsck; commit 2, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7d.py && test -z "$(git status --porcelain -- src tests)"</automated>
  </verify>
  <done>FULL reconciled; records committed; no push.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| code → registered report list | a computed secondary outcome that is never reported |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157d-01 | Repudiation | allvars outcome unreported | mitigate | dedicated table + drop family (1, 2, 5) |
| T-r4-157d-02 | Tampering | confirmatory tables moving | mitigate | byte identity vs the start commit (6) |
</threat_model>

<verification>
- 6 new tests and the rename successor pass; check_15_7d.py passes.
</verification>

<success_criteria>
- The A1 all-variants comparison D-21 commits to is reported as its own secondary table.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-a1-allvars-secondary-SUMMARY.md`
</output>
