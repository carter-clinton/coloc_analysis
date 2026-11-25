---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8d
slug: W3f-e7-filtered-cs-counts
type: execute
wave: 15.8d
depends_on: ["ta-r4-W3f-qtl-legacy-rule-and-e7-rounding"]
gap_closure: true
files_modified:
  - src/python/ta_r4/estimands.py
  - src/python/ta_r4/run_aggregation.py
  - src/python/ta_r4/r4_lock_gate.py
  - tests/ta_r4/test_e7_filtered_counts.py
  - tests/ta_r4/test_estimands.py            # test_e7_frozen_vs_fixed_and_flipped_shares (declared)
  - tests/ta_r4/test_run_aggregation.py      # fixture builder only (the manifest in the fixture repo), if needed
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fit_cs_repro_routeL_exact_purity.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-e7-filtered-cs-counts-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "Gate Q-157J passes (15.8 protocol); otherwise nothing is edited"
    - "E7 fit_yield frozen_value = `<status_L>;n_cs=<n_cs_rds_sets>` from manifests/fit_cs_json_vs_rds.tsv (the earlier route's purity-filtered sets, length(fit$sets$cs) of the repro_routeL fits; NA for early exits), and a new column frozen_value_json_unfiltered = the old `<status_L>;n_cs=<n_cs_L>` (fit_yield rows only; empty elsewhere); `changed` = frozen_value != fixed_value, so it compares purity-filtered with purity-filtered"
    - "A real_ld W3a row with no row in fit_cs_json_vs_rds.tsv, or a key mismatch (trait, ancestry, region_safe, status), raises; no silent fallback to the JSON count"
    - "Measured: the earlier route's stored filtered counts equal exact-purity counts for all 96 repro_routeL fits (no candidate set above 100 members is subsampled, or the exact recompute on the scored matrix gives the same count); any fit where they differ is a STOP for Carter (which earlier-side definition E7 uses)"
    - "fit_cs_json_vs_rds.tsv joins known_answer_W3a.tsv in r4_lock_gate.LOCKED_PATHS and is named in DRAFT (m); DRAFT (e) E7 says the earlier side counts purity-filtered sets (with the unfiltered JSON count also reported)"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fit_cs_repro_routeL_exact_purity.tsv"
      provides: "stored vs exact-purity set counts of the 96 earlier-route fits"
  key_links:
    - from: "run_aggregation (E7)"
      to: "manifests/fit_cs_json_vs_rds.tsv"
      via: "estimands.e7_frozen_vs_fixed(..., fit_cs_filtered=...)"
      pattern: "fit_cs_json_vs_rds"
---

<objective>
Close review R3 as Carter chose ("R3: yes it should be counted"). E7's fit yield compares the earlier fits' JSON set
count, which includes impure sets, with R4's purity-filtered count, so `changed` mixes a change of definition with a
change of yield (estimands.py:452-456; known_answer_compare.py:122-123). This plan puts the earlier fits'
purity-filtered counts on the frozen side, keeps the JSON count as a labelled column, and first measures that the
earlier filtered counts equal exact-purity counts, since R4 uses exact purity (15.7f).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: as in ta-r4-W3f-collector-drop-audit-PLAN.md <question>.
Task 1 STOP question (only if a fit's stored and exact counts differ), QID Q-158R3, file
`W3f-carter-15-8-Q-158R3-reply-<date>.txt`: "For N of the 96 earlier-route fits the stored purity-filtered set count
(susieR's 100-member subsample) differs from the exact-purity count R4 uses (table). Which count should E7's earlier
side use?" Labels: `A: Exact-purity count (same definition as R4) (Recommended)` / `B: Stored count (the earlier
pipeline's own definition), with the exact count as a further column` / `C: Other (free text)`.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md
@src/python/ta_r4/estimands.py
@src/python/ta_r4/run_aggregation.py
@src/python/ta_r4/sh2b3_known_answer.py
@src/python/ta_r4/measure_fit_eligibility.py

**Verified at planning (99ab219d).**
- estimands.py:438-458 `e7_frozen_vs_fixed`: fit_yield frozen = `f"{r.status_L};n_cs={r.n_cs_L}"` from
  known_answer_W3a (`pair == "real_ld"`); fixed = the A3 fit's `n_cs` (fit_frame :104-124, `len(credible_sets)` of the
  R4 JSON, purity-filtered, exact purity since 15.7f); `changed` = frozen != fixed (:448).
- known_answer_compare.py:120-123: `n_cs` = number of JSON `credible_sets` (earlier JSON includes impure sets; (h)).
- manifests/fit_cs_json_vs_rds.tsv (W3b, 57ed36a8; 96 rows: trait, ancestry, region_safe, status, n_cs_json,
  n_cs_rds_sets, eq) = W3a `n_cs_L` vs `length(fit$sets$cs)` of the repro_routeL `.fit.rds`
  (sh2b3_known_answer.py:136-155, :195); re-derived from disk by
  test_sh2b3_known_answer.py::test_live_r1_and_fit_cs_tables. Example row 3: asthma AFR APOE_19q13 7 JSON / 0 sets.
  data/r4/results/repro_routeL/fine_mapping/susie has the 96 `.fit.rds`.
- run_aggregation.py:389-393 builds E7 from KNOWN_W3A (:35) and KNOWN_SH2B3; r4_lock_gate.py LOCKED_PATHS :25-55 lists
  known_answer_W3a.tsv and known_answer_sh2b3.tsv but not fit_cs_json_vs_rds.tsv.
- susieR 0.14.2 susie_get_cs subsamples purity only for sets with more than n_purity = 100 members, so a stored count
  can differ from the exact one only through such a set.
- Pre-existing test asserting the old frozen value: tests.ta_r4.test_estimands::test_e7_frozen_vs_fixed_and_flipped_shares
  (`frozen_value == "ok;n_cs=2"` from `n_cs_L`) → declared spec update: the fixture gains the filtered table and the
  assertion checks the filtered frozen value and the unfiltered column.
</context>

<new_tests>
tests/ta_r4/test_e7_filtered_counts.py; N_new = 6.
1. `test_frozen_value_is_the_purity_filtered_count`
2. `test_unfiltered_json_count_is_kept_in_its_labelled_column`
3. `test_changed_compares_filtered_with_filtered` (JSON 7 / filtered 0 vs fixed 0 → changed False)
4. `test_missing_or_mismatched_filtered_row_raises`
5. `test_filtered_manifest_is_a_locked_path`
6. `test_exact_purity_manifest_matches_the_stored_counts` (r4_heavy; reads the committed exact-purity manifest and
   re-derives the stored counts from the 96 RDS)
Expected FULL: base full_15_8c2.xml (expected 2,726) + 6 = 2,732. Declared: test_e7_frozen_vs_fixed_and_flipped_shares, plus any
test_run_aggregation / test_lock_gate / test_amendment_text id whose fixture builder or LOCKED_PATHS listing gains the
manifest (named in the SUMMARY).
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: Gate; measure stored vs exact-purity counts on the 96 earlier-route fits (STOP on any difference)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fit_cs_repro_routeL_exact_purity.tsv</files>
  <read_first>
    - measure_fit_eligibility.py :418-720 (15.7h2 exact purity on the scored matrix; PurityIdentityError)
    - sh2b3_known_answer.py :130-160; data/r4/measure_asthma_fix/bmi_determinism/base_cmd.txt (route L argv form)
  </read_first>
  <action>
    0. `git rev-parse HEAD > $Q8/start_15_8d.txt`; `bash $Q8/gate_157j.sh`.
    1. For each repro_routeL fit with a fit object: the candidate components susie_get_cs evaluates (coverage 0.95)
       and their sizes. Components with > 100 members → recompute exact purity on the matrix the fit was scored on
       with the 15.7h2 routine (scored-matrix candidates must reproduce the stored sets first, else
       PurityIdentityError → STOP: the scored matrix is unknown). Run under Slurm (`-t 01:00:00 --mem=32G`).
    2. Write fit_cs_repro_routeL_exact_purity.tsv: trait, ancestry, region_safe, status, n_cs_rds_sets (stored),
       n_components_over_100, n_cs_exact, eq. eq false anywhere → STOP: present Q-158R3 (checkpoint:human-action
       semantics, stops even under --auto), write nothing else until Carter's reply file exists and its sha256 is
       pinned here.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && test "$(tail -n +2 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fit_cs_repro_routeL_exact_purity.tsv | wc -l)" = 96</automated>
  </verify>
  <done>The earlier side's filtered count is shown to be the same definition as R4's (or Carter has chosen).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: E7 filtered frozen side + labelled unfiltered column + lock path (RED first)</name>
  <files>src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, src/python/ta_r4/r4_lock_gate.py, tests/ta_r4/test_e7_filtered_counts.py, tests/ta_r4/test_estimands.py, tests/ta_r4/test_run_aggregation.py</files>
  <behavior>
    - Tests 1-6 per <new_tests>
  </behavior>
  <action>
    1. RED: tests 1-6 (`$Q8/red_15_8d.txt`).
    2. estimands.e7_frozen_vs_fixed gains a required keyword `fit_cs_filtered` (the fit_cs_json_vs_rds frame); fit_yield
       rows take frozen from `n_cs_rds_sets` (Carter B: from it, plus an `n_cs_exact` column) and put the old string in
       `frozen_value_json_unfiltered`; every other section leaves that column empty; output columns are the old ones
       plus 15.8c2's two columns, then the new column at the end. run_aggregation reads `f"{paths.MAN}/fit_cs_json_vs_rds.tsv"` (constant
       `FIT_CS_FILTERED`) and passes it. r4_lock_gate.LOCKED_PATHS adds it next to known_answer_W3a.tsv.
    3. Declared edit of test_e7_frozen_vs_fixed_and_flipped_shares (fixture + the frozen assertion, reason: it asserts
       the definition mismatch R3 fixes); fixture-builder edits in test_run_aggregation if its fixture repo needs the
       manifest. Green: tests 1-6, test_estimands.py, test_run_aggregation.py, test_lock_gate.py,
       test_sh2b3_known_answer.py.
    4. NCs (`$Q8/nc_15_8d.txt`): frozen back to n_cs_L → tests 1, 3 fail; silent fallback on a missing row → test 4
       fails; manifest dropped from LOCKED_PATHS → test 5 fails; one row of a tmp copy of
       fit_cs_repro_routeL_exact_purity.tsv perturbed (n_cs_exact + 1), test 6 pointed at the copy → test 6 fails.
       md5-restore each. Commit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_e7_filtered_counts.py tests/ta_r4/test_estimands.py tests/ta_r4/test_run_aggregation.py tests/ta_r4/test_lock_gate.py tests/ta_r4/test_sh2b3_known_answer.py -q -p no:cacheprovider</automated>
  </verify>
  <done>E7 `changed` compares filtered with filtered; the unfiltered count is kept and labelled; the input is locked.</done>
</task>

<task type="auto">
  <name>Task 3: DRAFT (e) E7 + (m); FULL vs full_15_8c2.xml; records (no push)</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-e7-filtered-cs-counts-SUMMARY.md</files>
  <action>
    1. DRAFT script: (e) E7 `(the earlier side counts the credible sets of the earlier fit JSON, which include impure
       sets (h); the R4 side counts purity-filtered sets)` (assert unique; use 15.7j's exact text if it changed, quoted
       in the LOG) → `(both sides count purity-filtered credible sets; the earlier fit JSON's count, which includes
       impure sets (h), is reported alongside)`. (m): add `manifests/fit_cs_json_vs_rds.tsv` where known_answer_W3a.tsv
       is listed (test_draft_extract_names_every_frozen_path green). Pre-Paste: `LOCKED_PATHS` (29 entries; re-checked
       W3f 15.5)` → `LOCKED_PATHS` (30 entries; re-checked W3f 15.8d)` (old string asserted unique; the count is
       `len(r4_lock_gate.LOCKED_PATHS)` measured after the edit, not typed). test_amendment_text.py,
       test_prelock_pilot_fits.py green.
    2. `$Q8/close.sh 15_8d`; `$Q8/check_15_8d.py` (base full_15_8c2.xml; NEW = 6; declared per <new_tests>). Records:
       LOG, PLAN-INDEX 15.8d row, STATE (NEXT = 15.8e; NOT PUSHED), SUMMARY with both sections. The LOG and SUMMARY
       record that the 30 early-exit fits (24 too_many_variants, 6 no_variants in fit_cs_json_vs_rds.tsv) move from
       `n_cs=0` to `n_cs=NA` on the frozen side, so `changed` shifts for those rows (it now matches a fixed-side NA).
       fsck; commit. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8d.py && grep -q "fit_cs_json_vs_rds" src/python/ta_r4/r4_lock_gate.py</automated>
  </verify>
  <done>R3 closed in code and text; FULL reconciled; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| earlier record → E7 claim of a changed yield | the two sides must use one credible-set definition |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158d-01 | Tampering | definition change reported as yield change | mitigate | filtered vs filtered; exact-purity identity measured on all 96 fits; STOP on difference |
| T-r4-158d-02 | Tampering | E7 input edited after the lock | mitigate | manifest added to LOCKED_PATHS |
</threat_model>

<verification>
- check_15_8d.py passes; exact-purity manifest 96 rows, all eq (or Carter's reply pinned).
</verification>

<success_criteria>
- E7 `changed` means a change in fit yield under one definition.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-e7-filtered-cs-counts-SUMMARY.md`
</output>
