---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7e
slug: W3f-none-rows-denominators
type: execute
wave: 15.7e
depends_on: ["ta-r4-W3f-a1-allvars-secondary"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md
  - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
  - src/python/ta_r4/estimands.py
  - tests/ta_r4/test_none_rows_denominators.py
  - tests/ta_r4/test_run_aggregation.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-none-rows-denominators-SUMMARY.md
autonomous: true
requirements:
  - REQ-NEGATIVE-CONTROLS
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "Gate: gate_reply.py Q-DEN with the <question> text and sha256 prints \"A: Known states only (Recommended)\"; any other result → nothing is edited"
    - "A pair JSON whose one fit exited early keeps the completed side's n_cs (length of its purity-filtered sets) and records early_exit_a / early_exit_b; the early-exit side stays NA"
    - "e4_no_cs_rate (pair_row and region levels) counts a row as no-CS when either side has a known 0; a row with no known 0 and an unknown side is counted in n_unknown; no_cs_rate stays over all pair rows of the arm (the stated denominator) and no_cs_rate_known = n_no_cs / (n_rows − n_unknown) is added; the fit level is unchanged"
    - "negative_controls is long by method per (nc_set, label, p12_key): one row each for coloc_susie, fallback_abf, A1_abf_matched, A1_abf_allvars and none that occur, plus with_posterior (every method except none, fallback labelled by n_fallback_abf); each row has n_rows, n_h4, share_h4; `none` rows are counted but are in no share denominator (share_h4 NaN on the none row)"
    - "Measured at planning by reading the fixtures: tests/ta_r4/test_estimands.py::test_e4_no_cs_rate and tests/ta_r4/test_reporting_widened.py::test_e4_no_cs_rate_levels_and_denominators (:120) keep their asserted values (no fixture row has a known 0 beside an unknown side; the r3 none row moves to n_unknown, n_no_cs stays 1, rate 0.25); tests/ta_r4/test_coloc_none_states.py asserts no n_cs and is unaffected; one declared spec update: tests/ta_r4/test_run_aggregation.py::test_row_counts_equal_fixture_admissible_rows"
    - "branch_outcomes and E1–E3 are byte-identical to the literal commit PRE_157E_REF on the fixture"
    - "The 12 ids in <new_tests> pass; FULL vs full_15_7d.xml: 0 removed, added == <new_tests>, 0 outcome changes (the declared id stays passed); 2,654 = 2,601 P / 53 S / 0 F"
  artifacts:
    - path: "src/python/ta_r4/estimands.py"
      provides: "_no_cs, _unknown_cs, e4_no_cs_rate (n_unknown, no_cs_rate_known), negative_control_rates (long by method)"
    - path: "src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R"
      provides: "early-exit pair docs keep the completed side's n_cs; early_exit_a / early_exit_b"
  key_links:
    - from: "run_coloc_pair_r4.R early-exit branch"
      to: "estimands._no_cs / _unknown_cs"
      via: "pair JSON n_cs_a / n_cs_b"
      pattern: "early_exit_a"
---

<objective>
Close F8 and F11 with Carter's Q-DEN answer A, "Known states only".

- **F8 (CONFIRMED, `estimands.py:599-607`).** Negative-control rates pool coloc_susie and fallback_abf, and `none` rows
  count as non-calls in the denominator; DRAFT (d) commits every estimand to the coloc.susie subset and to all rows
  with fallback labelled.
- **F11 (CONFIRMED, `run_coloc_pair_r4.R:503-519`, `estimands.py:317-319`).** An early exit on either side sets both
  pair n_cs to NA, so a completed side with 0 sets is lost. Exposure (DRAFT (k)): A3_ukb 14 of 100 primary rows, each AFR
  arm 4 of 30; the 1000G, identity and intersection arms 0.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
File: `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-DEN-reply-2026-11-20.txt`,
sha256 `0775b93555759dcea462f83a9cfe11b7364672021934a9daa8aac4766d5b832c`.
Question text (line 1 after `Question Q-DEN (2026-11-20): `):
How should rows with no posterior or no credible-set count enter rates? Today an early exit on either side sets both n_cs to NA, which drops the pair from the no-CS rate; this affects 14/100 A3_ukb primary rows and 4/30 per AFR arm. Negative-control rates aren't split by method, and 'none' rows count as non-calls.
Required label: `A: Known states only (Recommended)`
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/python/ta_r4/estimands.py
@src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
@tests/ta_r4/test_run_aggregation.py

**Gate.** `$PY $Q/gate_reply.py Q-DEN --question "<the question text above>" --sha256 0775b935…b832c (full value above)
"A: Known states only (Recommended)"`. Non-zero → STOP, edit nothing.

**Forbidden:** changing region_stat, the confirmatory subset rules, the fit-level no-CS rule, `decision_rules.yaml`.

**Measured at planning:**
- `run_coloc_pair_r4.R:449-458` read_fit returns `list(early_exit = st)` for an early-exit fit, else the fit; the
  completed side's sets are `raw$fit$sets$cs`.
- `tests/ta_r4/test_run_aggregation.py:220-221` asserts `set(nc.n_rows) == {3}` on the pooled table. Under the long
  table that holds per method, so it is the declared spec update: the assertion becomes the same check on the per-group
  totals, `set(nc[nc.method != "with_posterior"].groupby(["nc_set", "label", "p12_key"]).n_rows.sum()) == {3}`.
- test_estimands.py:193-208 (docs with explicit n_cs only) and test_reporting_widened.py:110-125 (r3 is a `none` doc
  with both n_cs NA) keep their values; the executor confirms both in the RED run.
</context>

<new_tests>
tests/ta_r4/test_none_rows_denominators.py; N_new = 12.
1. `test_early_exit_pair_keeps_the_completed_sides_n_cs` (r4_heavy; Rscript on the test_coloc_none_states fixture)
2. `test_early_exit_pair_records_which_side_exited` (r4_heavy)
3. `test_known_zero_beside_an_early_exit_is_no_cs`
4. `test_unknown_without_a_known_zero_is_counted_as_unknown`
5. `test_no_cs_rate_known_excludes_unknown_rows`
6. `test_fit_level_rule_unchanged`
7. `test_nc_rates_split_by_method`
8. `test_nc_none_rows_are_counted_not_in_a_share_denominator`
9. `test_nc_with_posterior_row_labels_fallback`
10. `test_nc_a1_methods_are_their_own_rows`
11. `test_nc_group_totals_reconcile` (per-method n_rows sum == the group's rows)
12. `test_confirmatory_outputs_unchanged` (PRE_157E_REF literal; `git show` of estimands.py / run_aggregation.py)
Declared spec update: `tests.ta_r4.test_run_aggregation::test_row_counts_equal_fixture_admissible_rows` (one assertion,
as in <context>; id kept, passed).
Expected FULL: base full_15_7d.xml (2,642) + 12 = 2,654 = 2,601 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gate, DEC, known-state counts and per-method NC rates (RED first), DRAFT</name>
  <files>.planning/DECISIONS.md, src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R, src/python/ta_r4/estimands.py, tests/ta_r4/test_none_rows_denominators.py, tests/ta_r4/test_run_aggregation.py, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - estimands.py :28-60, :317-350, :599-607; run_coloc_pair_r4.R :449-530
    - tests/ta_r4/test_reporting_widened.py :20-60, :100-125; tests/ta_r4/test_coloc_none_states.py; tests/ta_r4/test_run_aggregation.py :205-226
  </read_first>
  <action>
    0. Gate. `git rev-parse HEAD > $Q/start_15_7e.txt`; write it into the test as the literal `PRE_157E_REF`. DEC
       `DEC-2026-11-20-ta-r4-none-rows-denominators` quoting the reply file (`cat` + `cmp`); the file itself was
       committed in 15.7a. Commit 1 (`docs(ta-r4-W3f): DEC Q-DEN = A known states only (15.7e)`), DECISIONS.md only.
    1. RED: tests 1-12 and the declared spec update against the current code (all RED except 6 and 12); confirm
       test_e4_no_cs_rate and test_e4_no_cs_rate_levels_and_denominators still pass with the new tests' stubs. Record.
    2. GREEN per must_haves. R: in the early-exit branch, for a side whose `early_exit` is NA set
       `n_cs_<side> <- length(raw$fit$sets$cs %||% list())`; add `early_exit_a`, `early_exit_b`. Python: `_unknown_cs`,
       `e4_no_cs_rate` columns, `negative_control_rates` long by method. Apply the one declared assertion change.
    3. DRAFT: (e) E4 pair level becomes "per pair row (either trait with zero sets; a trait whose fit exited early has
       no count, and a row with no known zero and such a side is counted as unknown; rates over the arm's pair rows and
       over its rows of known state)"; (l) "share of rows with S ≥ 0.8 per set and arm" becomes "share of rows with S ≥
       0.8 per set, arm and method (`coloc_susie`, `fallback_abf`, A1, and all rows with a posterior, fallback
       labelled); rows with method `none` are counted and are in no denominator". Old strings asserted unique;
       test_amendment_text.py green.
    4. Commit 2 (`fix(ta-r4-W3f): pair no-CS keeps the completed side; NC rates by method (15.7e, F8 F11, Q-DEN A)`).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_none_rows_denominators.py tests/ta_r4/test_run_aggregation.py tests/ta_r4/test_reporting_widened.py tests/ta_r4/test_coloc_none_states.py tests/ta_r4/test_estimands.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider && grep -q "DEC-2026-11-20-ta-r4-none-rows-denominators" .planning/DECISIONS.md</automated>
  </verify>
  <done>Gate passed; DEC quotes the reply byte-for-byte; RED observed; 12 new tests and the one spec update green.</done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm, per-id reconciliation vs full_15_7d.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-none-rows-denominators-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7e: `$Q/check_15_7e.py` (removed 0; added == the 12; 0 outcome changes; the
    declared id passed; 2,654 = 2,601 / 53 / 0). Records (STATE NEXT = 15.7f; NOT PUSHED; SUMMARY lists the 12 ids and
    the spec-update id). fsck; commit 3, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7e.py && test -z "$(git status --porcelain -- src tests)"</automated>
  </verify>
  <done>FULL reconciled; records committed; no push.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| rate definitions → public text | a denominator chosen after outcomes exist is a forking path |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157e-01 | Repudiation | denominator choice | mitigate | gate on the verbatim reply (text + sha256); DEC quotes it; no production outputs exist |
| T-r4-157e-02 | Tampering | confirmatory analysis | mitigate | test 12 byte identity vs PRE_157E_REF |
</threat_model>

<verification>
- Gate output in the LOG; check_15_7e.py passes.
</verification>

<success_criteria>
- Pair no-CS and negative-control rates follow Carter's known-states definition, and the DRAFT states it.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-none-rows-denominators-SUMMARY.md`
</output>
