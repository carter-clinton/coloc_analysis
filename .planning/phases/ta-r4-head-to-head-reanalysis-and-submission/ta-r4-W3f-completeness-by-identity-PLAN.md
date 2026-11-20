---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7b
slug: W3f-completeness-by-identity
type: execute
wave: 15.7b
depends_on: ["ta-r4-W3f-runtime-config-guard"]
gap_closure: true
files_modified:
  - src/python/ta_r4/id_reconcile.py
  - src/python/ta_r4/run_aggregation.py
  - src/python/ta_r4/run_qtl_group_r4.py
  - src/snakemake/rules/ta_r4_qtl.smk
  - tests/ta_r4/test_id_reconcile.py
  - tests/ta_r4/test_sim_completeness_identity.py
  - tests/ta_r4/test_qtl_coverage_at_aggregation.py
  - tests/ta_r4/test_qtl_empty_summary_is_none.py
  - tests/ta_r4/test_run_aggregation.py
  - tests/ta_r4/test_sim_by_method_and_cells.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-completeness-by-identity-SUMMARY.md
autonomous: true
requirements:
  - REQ-SNAKEMAKE-CI
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "A simulation cell file with status ok passes run_aggregation._sim only if, for each arm A1/A2/A3, its rep values are exactly 1..reps once each; every row's region, scenario and gen_panel equal the file's cell; every seed equals seed_base + stable_index(cell, rep); and its `config_sha256` header equals the sha256 of the repo's config/ta_r4/simulation.yaml. Codex's probe (200 copies of replicate 1 with wrong labels) is refused"
    - "ta_r4.id_reconcile.stable_index equals the R harness's stable_index for every (region, scenario, gen_panel, rep) of the committed simulation.yaml (20,000 values), compared as a full table; the same comparison with two dimensions swapped in the Python order fails (negative control)"
    - "Every `# ` header line is parsed as space-separated k=v tokens (the R lines are `# simulate_coloc_r4 region=%s scenario=%s gen_panel=%s`, `# reps_override=%s`, `# status=%s`, `# window_variants=%d reps=%d config_sha256=%s`); the header's region / scenario / gen_panel must equal the file's cell"
    - "Reps rule: in both FINAL and DRAFT each arm must carry replicate ids exactly 1..cfg reps (simulation.yaml `reps`) and the header `reps` must equal that count; FINAL additionally requires `reps_override=none`; DRAFT accepts an override whose run produced the configured count (today's DRAFT behaviour, test_sim_by_method_and_cells.py:163-176, unchanged)"
    - "In FINAL, run_aggregation refuses (exit 3, nothing written) unless, for each QTL arm, the qtl_coloc_summary.tsv ids equal config/ta_r4/qtl_manifest.tsv's 116,550 qtl_row_ids exactly once each with a non-empty method, and the QTL_A3 JSON docs E7 reads reconcile to the same ids; DRAFT prints the problems"
    - "The r4_qtl_aggregate job fails, and Snakemake removes its outputs, when the summary does not reconcile with the manifest: the tierable step reconciles before writing. It reconciles only when `--manifest` is passed explicitly; without it the step behaves as today, so tests/ta_r4/test_qtl_fallback_export.py::test_tierable_summary_keeps_only_coloc_susie and ::test_tiers_from_tierable_equal_tiers_from_full keep their outcomes"
    - "A QTL row whose run_qtl_coloc.R status is success but whose summary is empty or has no finite PP.H4.abf is written with method none and none reason coloc_susie_empty / coloc_susie_no_finite_h4 (the GWAS pair reasons), is not tierable, and its reason reaches the aggregate's none_status"
    - "aggregate_qtl_coloc.py, run_qtl_coloc.R and every Track B file are unchanged"
    - "The 31 ids in <new_tests> pass; FULL vs full_15_7a.xml: 0 removed, added == <new_tests>, 0 outcome changes; 2,618 = 2,565 P / 53 S / 0 F"
  artifacts:
    - path: "src/python/ta_r4/id_reconcile.py"
      provides: "Reconciliation(missing, extra, duplicated, ok), reconcile(expected, observed), stable_index(cfg, region, scenario, gen, rep)"
    - path: "src/python/ta_r4/run_aggregation.py"
      provides: "_sim with identity checks; _qtl_coverage replacing _qtl_missing"
    - path: "src/python/ta_r4/run_qtl_group_r4.py"
      provides: "run_row none mapping for empty / non-finite success; tierable_summary(src, out, manifest) reconciles first"
  key_links:
    - from: "run_aggregation._sim"
      to: "id_reconcile.reconcile / stable_index"
      via: "per arm replicate ids and per row seeds"
      pattern: "reconcile\\("
    - from: "run_aggregation.run_aggregation"
      to: "_qtl_coverage"
      via: "FINAL refusal exit 3"
      pattern: "_qtl_coverage\\("
    - from: "ta_r4_qtl.smk r4_qtl_aggregate"
      to: "run_qtl_group_r4 --tierable-summary --manifest"
      via: "shell"
      pattern: "--tierable-summary"
---

<objective>
Close F4, F6 and F7. One bug class: completeness checked by count or existence, not by identity.

- **F4 (CONFIRMED, `run_aggregation.py:106-128`).** `_sim` checks file names, the header status / reps_override and
  `df.arm.value_counts() == {arm: reps}` only. Replicate ids, row labels, seeds and the `config_sha256` header that
  `simulate_coloc_r4.R` writes are never read. It changes no number under a correct producer; it is the gate that
  would catch a wrong one.
- **F6 (PARTLY).** Per-group coverage is enforced: `run_qtl_group_r4.main` writes `.done` only when its group
  reconciles, and `r4_qtl_aggregate` requires every group's `.done`. What is missing is end-to-end reconciliation:
  `aggregate_qtl_coloc.py:177-209` writes the summary from a glob and only warns about missing ids, never extras;
  `run_aggregation._qtl_missing` (:181-183) checks that the files exist. A stale or extra JSON outside any group key, or
  a file changed after its `.done`, reaches the tables.
- **F7 (CONFIRMED, `run_qtl_coloc.R:754-762`, `run_qtl_group_r4.py:160-163`).** A `coloc.susie` call that returns no
  summary still has status success; the runner labels it `coloc_susie` and the tier filter admits it. It mislabels
  method counts in `qtl_rows`; tiers are unaffected because assign_tiers ignores NaN rows.

Fixes stay in ta_r4 files: no edit to aggregate_qtl_coloc.py or run_qtl_coloc.R (shared with Track B).
Output: `ta_r4/id_reconcile.py` (reused by both completeness checks), the three fixes, 31 tests, records. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/python/ta_r4/run_aggregation.py
@src/python/ta_r4/run_qtl_group_r4.py
@src/snakemake/scripts/ta_r4/simulate_coloc_r4.R
@config/ta_r4/simulation.yaml

**Standing rules:** PLAN-INDEX §A, §B and the 15.7 shared protocol.

**Forbidden:** edits to `src/python/aggregate_qtl_coloc.py`, `src/snakemake/scripts/run_qtl_coloc.R`,
`simulate_coloc_r4.R`, `config/**`, Track B files; weakening any existing assertion.

**Measured at planning (re-measure in Task 1 step 1):**
- `simulate_coloc_r4.R:91-97` `stable_index`: dims sorted with `method = "radix"`; index =
  ((i_region−1)·n_sc·n_gen + (i_sc−1)·n_gen + (i_gen−1))·reps + rep; `:159-160` seed = seed_base + index,
  `set.seed(seed)` per replicate. Header line `# window_variants=%d reps=%d config_sha256=%s` (digest of the
  `--config` file). Columns include region, scenario, gen_panel, rep, seed, arm.
- Committed simulation.yaml: 10 regions × 5 scenarios × 2 gen_panels = 100 cells, reps 200, seed_base 20261021.
- Existing fixtures that write sim files with seed = rep (or 1) and no config_sha256 header:
  `tests/ta_r4/test_run_aggregation.py:80-90` and `tests/ta_r4/test_sim_by_method_and_cells.py:104-130` (`_cell`,
  `sim_repo`). These builders are updated (fixture-only; PLAN-INDEX 15.7 rule) to write correct seeds and the header.
- `config/ta_r4/qtl_manifest.tsv`: 116,551 lines (116,550 rows), id column `qtl_row_id`; summary id column
  `qtl_coloc_id` = JSON stem (`aggregate_qtl_coloc.py:84`).
- `run_qtl_coloc.R` writes `summary = best_row` where an empty summary is `list()` → JSON `[]`; `best_row` comes from
  `which.max(PP.H4.abf)` and can carry NA → JSON null.
</context>

<new_tests>
N_new = 31.
tests/ta_r4/test_id_reconcile.py
1. `test_reconcile_exact_set_ok`
2. `test_reconcile_reports_missing`
3. `test_reconcile_reports_extra`
4. `test_reconcile_reports_duplicates`
tests/ta_r4/test_sim_completeness_identity.py
5. `test_sim_accepts_a_correct_cell`
6. `test_sim_rejects[copies_of_rep1]` (Codex's probe: reps rows per arm, all rep 1)
7. `test_sim_rejects[rep_out_of_range]`
8. `test_sim_rejects[wrong_region_label]`
9. `test_sim_rejects[wrong_scenario_label]`
10. `test_sim_rejects[wrong_gen_panel_label]`
11. `test_sim_rejects[wrong_seed]`
12. `test_sim_rejects[config_sha256_mismatch]`
13. `test_sim_rejects[missing_config_sha256]`
14. `test_stable_index_matches_the_r_harness` (r4_heavy; Rscript `sys.source`s the harness's `stable_index` and
    prints all 20,000 values for the committed yaml; equal as a full table)
14a. `test_stable_index_with_swapped_dimensions_differs_from_the_r_harness` (r4_heavy; negative control: a Python
    order with scenario and gen_panel swapped must differ from the R table in at least one value)
14b. `test_sim_header_parsed_from_the_r_format` (header lines built with the R sprintf formats above, values with
    spaces excluded; every k=v recovered, including config_sha256 on the window_variants line)
tests/ta_r4/test_qtl_coverage_at_aggregation.py
15. `test_qtl_summary_matching_manifest_passes`
16. `test_qtl_coverage_flags[missing_row]`
17. `test_qtl_coverage_flags[extra_row]`
18. `test_qtl_coverage_flags[duplicate_row]`
19. `test_qtl_coverage_flags[empty_method]`
20. `test_final_refuses_on_a_qtl_coverage_gap` (exit 3, out dir empty; mirror the existing FINAL-refusal pattern in
    test_run_aggregation.py)
21. `test_tierable_step_refuses_an_incomplete_summary` (main --tierable-summary --manifest → rc 1, --out absent)
22. `test_a3_json_docs_reconciled`
tests/ta_r4/test_qtl_empty_summary_is_none.py
23. `test_success_with_empty_summary_is_method_none[empty_list]`
24. `test_success_with_empty_summary_is_method_none[empty_dict]`
25. `test_success_with_empty_summary_is_method_none[null_h4]`
26. `test_success_with_empty_summary_is_method_none[nan_h4]`
27. `test_success_with_finite_summary_stays_coloc_susie`
28. `test_none_row_is_not_tierable`
29. `test_aggregate_exports_the_none_reason` (aggregate_qtl_coloc.py --with-method-columns on the written doc:
    none_status == reason; reads the shared script, does not change it)

Expected FULL: base full_15_7a.xml (2,587) + 31 = 2,618 = 2,565 P / 53 S / 0 F. Ids 14a/14b are listed by their names.
</new_tests>

<interfaces>
run_aggregation (existing): expected_sim_cells(repo) -> ({file: (region, scenario, gen)}, reps); _sim(repo, *, final);
  _qtl(repo) -> (layer, docs, tiers_legacy, tiers_a3); _qtl_missing(repo) -> list[str]  (replaced);
  estimands.SimulationIncomplete; QTL_ARMS = ("QTL_A3", "QTL_A2", "QTL_legacy"); QTL_SUMMARY, QTL_TIERS, QTL_JSON_DIR.
run_qtl_group_r4 (existing): run_row(...) -> method; tierable_summary(src, out) -> (kept, total); NO_CS; main().
estimands.NONE_REASONS = ("coloc_susie_empty", "coloc_susie_no_finite_h4", "fit_early_exit").
New (exact names):
  id_reconcile.Reconciliation  (dataclass: missing: list, extra: list, duplicated: list; ok property; summary(n=10) -> str)
  id_reconcile.reconcile(expected: Iterable, observed: Sequence) -> Reconciliation
  id_reconcile.stable_index(cfg: dict, region, scenario, gen, rep) -> int     # mirrors simulate_coloc_r4.R:91-97
  run_aggregation._qtl_coverage(repo) -> list[str]   # problems; [] = complete
  run_qtl_group_r4.tierable_summary(src, out, manifest=None)   # manifest given → reconcile first, ValueError on a gap
</interfaces>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: id_reconcile utility; F4 simulation identity; F6 QTL reconciliation (RED first)</name>
  <files>src/python/ta_r4/id_reconcile.py, src/python/ta_r4/run_aggregation.py, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_qtl.smk, tests/ta_r4/test_id_reconcile.py, tests/ta_r4/test_sim_completeness_identity.py, tests/ta_r4/test_qtl_coverage_at_aggregation.py, tests/ta_r4/test_run_aggregation.py, tests/ta_r4/test_sim_by_method_and_cells.py</files>
  <read_first>
    - run_aggregation.py :99-139 (_sim), :157-183 (_qtl, _qtl_rows, _qtl_missing), :274-312 (run_aggregation)
    - simulate_coloc_r4.R :85-100, :150-240 (columns, header)
    - tests/ta_r4/test_run_aggregation.py :1-140 and tests/ta_r4/test_sim_by_method_and_cells.py :95-140 (fixtures)
    - ta_r4_qtl.smk :124-146 (r4_qtl_aggregate shell)
  </read_first>
  <behavior>See <new_tests> 1-22.</behavior>
  <action>
    0. `git rev-parse HEAD > $Q/start_15_7b.txt`. Confirm 15.7a's commits are in the log.
    1. Re-measure the <context> facts (print the R `stable_index` source lines; count the manifest; list every
       existing test that writes sim files or calls `_qtl_missing` / `tierable_summary`). A difference → STOP.
    2. RED. Write tests 1-22 and the id_reconcile stubs (`reconcile` returns ok; `stable_index` returns 0). Keep
       `_sim` and `_qtl_missing` as they are. Expected RED: 2-4, 6-14, 14b, 16-22. Expected green: 1, 5, 15 and 14a (a constant stub also differs from R; 14a means something only beside 14 green, which proves the swapped order is the only difference). Record all.
    3. GREEN.
       - `id_reconcile` per <interfaces>; `stable_index` sorts with plain `sorted()` (codepoint order equals R's radix
         order for these ASCII ids; test 14 is the enforcer).
       - `_sim`, status ok: per arm `reconcile(range(1, reps+1), df.rep[df.arm == a])`; every row's
         region/scenario/gen_panel equal the cell; every seed equals `seed_base + stable_index(...)`; header
         `config_sha256` equals the sha256 of `Path(repo)/SIM_CFG` bytes (checked for every status, including
         no_qualifying_pair); header `reps` equals reps; the header's
         region / scenario / gen_panel equal the cell. Parse every `# ` line as space-separated k=v tokens (the current
         parser at :117-118 drops everything after the first `=` on the window_variants line). Reps rule as in
         must_haves. Each failure is
         one `bad` entry naming the file. The no_qualifying_pair branch is unchanged.
       - `_qtl_coverage(repo)`: for each QTL arm, summary and tier table exist; summary `qtl_coloc_id` reconciles
         with the manifest's `qtl_row_id`; no empty `method`; QTL_A3 JSON doc ids (the `_qtl` rglob ids) reconcile
         too. `run_aggregation` uses it where `_qtl_missing` was (same FINAL exit 3 / DRAFT print). Delete
         `_qtl_missing` only if no other caller exists.
       - `tierable_summary(src, out, manifest=None)`: reconcile only when `manifest` is given; main passes it only when
         the `--manifest` flag is given explicitly (no default for this subcommand). The rule shell appends
         `--manifest {input.manifest}` after `--out {output.tierable}`, so the rendered-jobs regex in
         test_in_job_gate.py still matches; run test_qtl_fallback_export.py and test_in_job_gate.py after the edit.
       - Fixture builders in test_run_aggregation.py and test_sim_by_method_and_cells.py write `seed_base +
         stable_index` seeds and the `config_sha256` header of the yaml they wrote; the fixture QTL manifest for
         any FINAL-path test lists exactly the fixture's summary ids. Do not change any assertion line: an AST
         comparison against the commit in `$Q/start_15_7b.txt` (a scratch record read by the executor's script, never
         by a test) must show only fixture helpers changed (record in
         `$Q/noweaken_15_7b.txt`).
       - Tests 1-22 green; every pre-existing test in the two edited modules passes.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && set -o pipefail && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_id_reconcile.py tests/ta_r4/test_sim_completeness_identity.py tests/ta_r4/test_qtl_coverage_at_aggregation.py tests/ta_r4/test_run_aggregation.py tests/ta_r4/test_sim_by_method_and_cells.py tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_qtl_fallback_export.py -q -p no:cacheprovider && git diff --quiet HEAD -- src/python/aggregate_qtl_coloc.py src/snakemake/scripts/run_qtl_coloc.R src/snakemake/scripts/ta_r4/simulate_coloc_r4.R config/</automated>
  </verify>
  <done>RED observed as listed; tests 1-22, 14a, 14b and the existing modules green; shared scripts untouched; fixture-only edits proven by AST.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: F7 empty / non-finite QTL coloc.susie → method none; DRAFT; FULL; records (no push)</name>
  <files>src/python/ta_r4/run_qtl_group_r4.py, tests/ta_r4/test_qtl_empty_summary_is_none.py, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-completeness-by-identity-SUMMARY.md</files>
  <read_first>
    - run_qtl_group_r4.py :133-187 (run_row, _best_pp); tests/ta_r4/test_qtl_group_runner.py :20-60, :170-190 (fake run pattern)
    - run_coloc_pair_r4.R, the GWAS none reasons (`coloc_susie_empty`, `coloc_susie_no_finite_h4`)
  </read_first>
  <behavior>See <new_tests> 23-29.</behavior>
  <action>
    1. RED: tests 23-29 against the current run_row (23-26, 28-29 RED; 27 green). Record.
    2. GREEN: in run_row, status success → if the summary is not a dict with a finite float `PP.H4.abf`: method
       `none`, `doc["status"] = reason` (`coloc_susie_empty` when the summary is empty or absent, else
       `coloc_susie_no_finite_h4`), `doc["qtl_r_status"] = "success"`, `fallback_reason` None. Finite → unchanged.
       Do not change the n_cs > 0 ValueError.
    3. DRAFT (l): after "Rows below the 50-variant bridge floor are kept with method `none`." add " So are rows for
       which `coloc.susie` returns no summary or no finite PP.H4." (old string asserted unique). In (g), check that
       the "200 replicates per arm" wording now matches the check; change nothing if it does.
       test_amendment_text.py green.
    4. Commit 1 (`fix(ta-r4-W3f): completeness by identity (simulation replicates, QTL rows vs manifest); empty QTL
       coloc.susie is method none (15.7b, F4 F6 F7)`), explicit paths.
    5. Close per the 15.7 protocol: `$Q/close.sh 15_7b` (sbatch as 15.7a), `junit_cmp.py $Q/full_15_7a.xml
       $Q/full_15_7b.xml`, `$Q/check_15_7b.py` (removed 0; added == the 31; 0 outcome changes; 2,618 = 2,565 / 53 /
       0). Records: LOG (RED/GREEN, each NC, the AST no-weaken result, FULL arithmetic), STATE block (NEXT = 15.7c,
       NOT PUSHED), PLAN-INDEX row COMPLETE, SUMMARY. `git fsck` before/after. Commit 2 (docs), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_empty_summary_is_none.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7b.py && test -z "$(git status --porcelain -- src tests)"</automated>
  </verify>
  <done>F7 mapped to none with a reason; DRAFT sentence matches the code; FULL reconciled; records committed; no push.</done>
</task>

</tasks>

<enforcers>
| must_have | enforcer | negative control |
|---|---|---|
| replicate ids distinct 1..reps | test 6, 7 | stub reconcile returns ok (RED) |
| row labels = cell | tests 8-10 | current _sim (RED) |
| seed rule | test 11 + test 14 (full-table identity with R) + 14a (swapped order must differ) | stub stable_index = 0 (14 RED) |
| header parsing | 14b | current parser (RED) |
| config hash | tests 12-13 | current _sim (RED) |
| QTL rows = manifest | tests 16-20, 22 | current _qtl_missing (RED) |
| aggregation job fails on a gap | test 21 | current tierable_summary (RED) |
| empty / non-finite → none | tests 23-26, 28-29 | current run_row (RED) |
| no assertion weakened | AST compare of the two fixture modules | — (identity) |
</enforcers>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| result files on /rs1 → aggregation | stale, duplicated or mislabelled outputs can enter FINAL tables |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157b-01 | Tampering | sim cell files | mitigate | replicate, label, seed and config-hash checks (tests 6-14) |
| T-r4-157b-02 | Tampering | QTL summary / JSON dir | mitigate | id reconciliation at aggregation and in the aggregate job (16-22) |
| T-r4-157b-03 | Repudiation | QTL method counts | mitigate | none + reason for empty / non-finite posteriors (23-29) |
| T-r4-157b-04 | Tampering | fixture edits hiding a weakened test | mitigate | AST no-weaken check, recorded |
</threat_model>

<verification>
- The 31 tests pass; check_15_7b.py passes; shared Track B scripts and config unchanged.
- `git diff $(cat data/r4/tmp/w3f/q157/start_15_7b.txt)..HEAD --name-only` ⊆ files_modified.
</verification>

<success_criteria>
- FINAL cannot be written from a simulation or QTL result set that does not match its design by identity.
- QTL rows without a usable posterior are labelled `none` with a reason, like the GWAS pairs.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-completeness-by-identity-SUMMARY.md`
</output>
