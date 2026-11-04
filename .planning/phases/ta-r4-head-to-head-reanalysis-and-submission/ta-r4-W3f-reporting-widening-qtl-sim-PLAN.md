---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.4
slug: W3f-reporting-widening-qtl-sim
type: execute
wave: 15.4
depends_on: ["ta-r4-W3f-signflip-region-floor-coverage"]
gap_closure: true
files_modified:
  - src/python/ta_r4/estimands.py
  - src/python/ta_r4/run_aggregation.py
  - src/snakemake/scripts/ta_r4/cs_cross_purity.R
  - src/python/aggregate_qtl_coloc.py
  - src/python/ta_r4/run_qtl_group_r4.py
  - src/snakemake/rules/ta_r4_qtl.smk
  - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R
  - tests/ta_r4/test_reporting_widened.py
  - tests/ta_r4/test_qtl_fallback_export.py
  - tests/ta_r4/test_sim_by_method_and_cells.py
  - tests/ta_r4/test_run_aggregation.py
  - tests/ta_r4/test_cs_cross_purity.py
  - tests/ta_r4/test_estimands.py
  - tests/ta_r4/test_simulation_harness.py
  - tests/ta_r4/test_qtl_group_runner.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-NEGATIVE-CONTROLS
  - REQ-SUSIE-RSS-POLICY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "A row_drops table reports, per contrast x p12 key x side, expected rows, outputs, method none rows by none_reason, fallback rows, both_have_cs rows and rows dropped from both_have_cs (Codex N8 reporting)"
    - "E4 cross-purity is computed for every fit whose RDS has credible sets, whatever its status, for the native UKB/1000G pair in both directions, the intersection pair, A2 vs A3 and the AFR analogues; the no-CS rate is reported per pair row, per region and per fit with the denominator named (Codex N9, code widened)"
    - "E6 recomputes E1-E5 on the sensitivity contrasts with drop counts (all-row and both-CS subsets, agreement sweep, reclassification, no-CS rates, diagnostics, variant-count differences), not a both-CS summary only (Codex N10, code widened)"
    - "QTL fallback_abf rows keep their method label and posteriors in the aggregate table; tiering explicitly filters method == coloc_susie; run_aggregation exports every QTL row (Codex N12)"
    - "The simulation never refits with R = I; it reports rates by method without pooling coloc_susie with fallback_abf; aggregation fails unless all 100 cells (10 regions x 5 scenarios x 2 generation panels) are present with the configured replicate count (Codex N14)"
    - "Without --with-method-columns aggregate_qtl_coloc.py output is byte-identical to its pre-change output (Track B unchanged, D-15)"
  artifacts:
    - path: "src/python/ta_r4/estimands.py"
      provides: "row_drop_table(), widened e4_no_cs_rate(), e6_panel_contrast() long-format E1-E5 + drops, e8 rates by method"
    - path: "src/python/aggregate_qtl_coloc.py"
      provides: "--with-method-columns: method, fallback_reason, none_status, pp_h0..pp_h4"
    - path: "src/snakemake/scripts/ta_r4/simulate_coloc_r4.R"
      provides: "no identity refit; fit_status_a/b and none_reason columns"
  key_links:
    - from: "src/snakemake/rules/ta_r4_qtl.smk r4_qtl_tiers"
      to: "qtl_coloc_summary_tierable.tsv"
      via: "run_qtl_group_r4 --tierable-summary filters method == coloc_susie before assign_tiers"
      pattern: "tierable"
    - from: "src/python/ta_r4/run_aggregation.py::_e8"
      to: "config/ta_r4/simulation.yaml regions x scenarios x gen_panels"
      via: "expected cell set; missing -> SimulationIncomplete"
      pattern: "SimulationIncomplete"
---

<objective>
W3f fix-up, plan 4 of 6: reporting commitments that the code did not meet (review N8 drop reporting, N9, N10,
N12, N14). Per Carter's rule, where the review offered "narrow the text or widen the code", the code is widened.

Purpose: E4, E6, QTL fallbacks and the simulation must report what the amendment promises, so W7 has no
undisclosed analytical choice left to make.
Output: widened estimators and tables, QTL method-labelled export with explicit tier filter, simulation without
identity refit and with by-method rates and a complete-cell requirement, tests with RED and negative controls.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md

Standing rules: PLAN-INDEX §A/§B/§C; §B.7 (Track B isolation: aggregate_qtl_coloc.py is shared, so its default
output must not change). The TABLES tuple in run_aggregation grows; update test_draft_writes_exactly_17_draft_tables
to the new count and name the added tables in the SUMMARY (a spec change, not a weakened test).

<interfaces>
src/python/ta_r4/run_aggregation.py:
  TABLES (17 names); CROSS_PURITY = (("A2_identity","A3_1kg"), ("A3_ukb_isect","A3_1kg_isect"), ("A3_1kg_isect","A3_ukb_isect"))
  _cross_purity(repo, fits, runner): iterates fits[(arm == fit_arm) & (status == "ok")]  # the N9 defect
  E6 = (("A3_ukb","A3_1kg","native","both methods coloc_susie"), ("A3_ukb_isect","A3_1kg_isect","isect","both methods coloc_susie"))
  AFR = (("AFR661_A2","AFR661_A3",...), ("A1_matched","AFR661_A3",...), ("AFR504_A3","AFR661_A3",...)) -> afr_secondary via e6_panel_contrast
  _sim(repo) reads whichever data/r4/results/sim/*.tsv exist (# status= header); _e8(repo, rules)
  _qtl(repo): reads data/r4/results/{QTL_A3,QTL_A2,QTL_legacy}/qtl_tiers.tsv and QTL_A3/qtl/*.json
src/python/ta_r4/estimands.py:
  e4_no_cs_rate(rows) (pair-row level only), e4_finemap_structure(fits), e5_diagnostics(fits)
  e6_panel_contrast(rows, rules, row_ids, contrasts, p12_keys): describe_contrast + median n_snps only  # the N10 defect
  e8_simulation_rates(sim, threshold, level): groups by (arm, scenario, gen_panel), pooling methods  # the N14 defect
src/snakemake/scripts/ta_r4/cs_cross_purity.R --fit --panel --output (min/mean abs corr of each CS under another panel)
src/python/aggregate_qtl_coloc.py: parse_coloc_json reads METADATA_COLS + data["summary"] PP.H*.abf only  # the N12 defect
src/python/ta_r4/run_qtl_group_r4.py: per-row doc has method in {coloc_susie, fallback_abf, none}, fallback_reason, top-level pp_h0..pp_h4
src/snakemake/rules/ta_r4_qtl.smk: r4_qtl_aggregate -> qtl_coloc_summary.tsv; r4_qtl_tiers -> assign_tiers.py --input {summary}
src/snakemake/scripts/ta_r4/simulate_coloc_r4.R: fit_frozen() refits with diag(m) when the ladder returns NULL (the N14 defect); COLUMNS; run_rep(); main() writes "# status=ok|no_qualifying_pair" and "# reps_override=none|<n>"
config/ta_r4/simulation.yaml: regions (10), scenarios (5), gen_panels (2), reps 200
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: N8 row_drops table; N9 widened cross-purity and no-CS rates; N10 E6 = E1–E5 with drops</name>
  <files>src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, src/snakemake/scripts/ta_r4/cs_cross_purity.R, tests/ta_r4/test_reporting_widened.py, tests/ta_r4/test_run_aggregation.py, tests/ta_r4/test_cs_cross_purity.py, tests/ta_r4/test_estimands.py</files>
  <read_first>
    - src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, src/snakemake/scripts/ta_r4/cs_cross_purity.R
    - tests/ta_r4/test_run_aggregation.py, tests/ta_r4/test_cs_cross_purity.py, tests/ta_r4/test_estimands.py, tests/ta_r4/fixtures/estimand_fixtures.py
    - DRAFT paragraph (e) E4 and E6 (the promised wording the code must now meet)
  </read_first>
  <behavior>
    - row_drop_table(rows, manifest, contrasts, p12_keys): one row per (contrast, p12_key, side in {x, ref}) with n_expected (manifest), n_output, n_method_none, n_none_<reason> for each none_reason, n_fallback, n_paired, n_both_have_cs, n_dropped_not_both_have_cs; counts reconcile: n_output = n_method_none + n_fallback + n_coloc_susie (+ A1 rows) and n_paired <= min(n_output_x, n_output_ref) (asserted in the function; raise on violation)
    - cross-purity: fits with status non_converged (or any status) whose RDS has non-empty sets$cs are scored; fits without a CS or early exits get a row with note no_cs / early_exit; pairs scored = (A2_identity→A3_1kg), (A3_ukb→A3_1kg), (A3_1kg→A3_ukb), (A3_ukb_isect→A3_1kg_isect), (A3_1kg_isect→A3_ukb_isect), (AFR661_A2→AFR661_A3), (AFR504_A3→AFR661_A3), (AFR661_A3→AFR504_A3); a CS with < 2 of its variants present in the panel arm gets NA purity and note fewer_than_2_present, with n_cs_variants and n_present columns
    - e4_no_cs_rate has a `level` column in {pair_row, region, fit} and a `denominator` column naming it ("pair rows of the arm", "pair rows of the arm in the region", "fits of the arm")
    - e6_panel_contrast returns a long table (variant_set, contrast, p12_key, estimand in {E1,E2,E3,E4,E5,drops}, subset in {both_have_cs, all_rows, -}, metric, value) computed for each sensitivity contrast; the same function produces afr_secondary
    - TABLES gains row_drops; the DRAFT-table count test is updated to the new count
  </behavior>
  <action>
    1. RED: tests/ta_r4/test_reporting_widened.py (fixture rows with a non-converged fit that has sets, an
       early-exit, a method-none coloc row, a fallback row; native panels with partially absent CS variants; expected
       counts hand-computed in the test). Run; paste failures.
    2. Implement row_drop_table, the widened e4_no_cs_rate, e6_panel_contrast long format (reusing e1_summary,
       e2_agreement, e3_reclassification, e4_*, e5_diagnostics on the subset — no new statistics), the CROSS_PURITY
       tuple and the status-agnostic `_cross_purity`. cs_cross_purity.R: report n_cs_variants / n_present and NA
       purity below 2 present (only if it does not already; read first). Add `row_drops` to TABLES and build_tables.
    3. GREEN. Negative controls (paste): NC1 restore `status == "ok"` → the non-converged purity case fails;
       NC2 make e6 return the old summary → the E2/E3 rows case fails; NC3 break the reconciliation (count fallback
       rows as none) → row_drop_table raises in its test.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_reporting_widened.py tests/ta_r4/test_run_aggregation.py tests/ta_r4/test_cs_cross_purity.py tests/ta_r4/test_estimands.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; RED and NC1–NC3 outputs pasted
    - the fixture row_drops counts equal the hand-computed values in the test (asserted per cell)
  </acceptance_criteria>
  <done>E4, E6 and the outcome-state drops are reported as the amendment promises.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: N12 — QTL fallback rows exported with method and PPs; explicit tier filter; qtl_rows table</name>
  <files>src/python/aggregate_qtl_coloc.py, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_qtl.smk, src/python/ta_r4/run_aggregation.py, tests/ta_r4/test_qtl_fallback_export.py, tests/ta_r4/test_qtl_group_runner.py</files>
  <read_first>
    - src/python/aggregate_qtl_coloc.py (whole), src/python/assign_tiers.py (which columns it reads)
    - src/python/ta_r4/run_qtl_group_r4.py (doc construction ~:140-175, CLI), src/snakemake/rules/ta_r4_qtl.smk (r4_qtl_aggregate, r4_qtl_tiers)
    - tests for aggregate_qtl_coloc under tests/ (grep -rl aggregate_qtl_coloc tests) and tests/ta_r4/test_track_b_isolation.py
  </read_first>
  <behavior>
    - aggregate_qtl_coloc.py without the flag: output byte-identical to the pre-change script on a fixture JSON dir containing coloc_susie, fallback_abf and none docs (differential test: run `git show <pre-change sha>:src/python/aggregate_qtl_coloc.py` from a tmp copy)
    - with `--with-method-columns`: extra columns method, fallback_reason, none_status, pp_h0..pp_h4; a fallback_abf doc has method fallback_abf and pp_h4 equal to doc["fallback"]["pp_h4"]; PP.H*.abf columns keep the summary semantics (blank for fallback); a doc without a method key is an error under the flag
    - run_qtl_group_r4 `--tierable-summary IN --out OUT` writes only rows with method == coloc_susie; a row with an empty method is an error
    - tiers from the tierable summary equal tiers from the full summary on the fixture (the old exclusion was implicit; this proves the explicit filter changes no tier)
    - run_aggregation writes a qtl_rows table (every row of each QTL arm's qtl_coloc_summary.tsv, with qtl_arm); in FINAL a missing QTL arm summary or tier table exits 3; DRAFT tolerates absence
  </behavior>
  <action>
    1. RED: tests/ta_r4/test_qtl_fallback_export.py with the behaviours (fixture JSONs in the run_qtl_group_r4 doc
       shape). Run; paste failures (fallback label and PP missing, as Codex reproduced in memory).
    2. Implement the flag in aggregate_qtl_coloc.py (default path untouched), the `--tierable-summary` CLI in
       run_qtl_group_r4.py, and in ta_r4_qtl.smk: r4_qtl_aggregate passes `--with-method-columns` and also writes
       `data/r4/results/{qtl_arm}/qtl_coloc_summary_tierable.tsv`; r4_qtl_tiers reads the tierable file. Add
       `qtl_rows` to TABLES / build_tables.
    3. GREEN; run Track B tests that touch aggregate_qtl_coloc / assign_tiers and test_track_b_isolation.py: outcomes
       unchanged (paste counts). Negative controls (paste): NC1 read `summary` only under the flag → the fallback PP
       case fails; NC2 let the tierable filter pass fallback_abf → the filter case fails.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_fallback_export.py tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_track_b_isolation.py tests/ta_r4/test_run_aggregation.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; the byte-identical default-output test is green and was seen RED when a column was added unconditionally (NC0, pasted)
    - NC1/NC2 failures pasted; Track B test counts unchanged
  </acceptance_criteria>
  <done>QTL fallback evidence is reported with its label and posterior, and excluded from tiers by an explicit rule.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: N14 — simulation without identity refit, rates by method, all cells required; commit, push, LOG</name>
  <files>src/snakemake/scripts/ta_r4/simulate_coloc_r4.R, src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, tests/ta_r4/test_sim_by_method_and_cells.py, tests/ta_r4/test_simulation_harness.py, tests/ta_r4/test_run_aggregation.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R (whole), config/ta_r4/simulation.yaml, src/snakemake/rules/ta_r4_sim.smk
    - tests/ta_r4/test_simulation_harness.py (fixture roots, test_susie_identity_vs_frozen_script, test_output_columns_and_rows)
    - src/python/ta_r4/validate_r4_fits.py:80 (production rejects identity substitution)
  </read_first>
  <behavior>
    - fit_frozen never calls the ladder with diag(m) after a NULL fit under the fit panel; it returns fit NULL and the ladder status
    - run_rep: an arm with a NULL fit on either trait writes its row with method "none", none_reason "fit_failed:<status_a>|<status_b>", NA PPs; output columns add fit_status_a, fit_status_b, none_reason
    - e8_simulation_rates groups by (arm, method, scenario, gen_panel); coloc_susie and fallback_abf never share a row; method none rows are counted (n) with rate NA
    - run_aggregation _e8: expected cells = regions x scenarios x gen_panels from the repo's config/ta_r4/simulation.yaml (100 for the committed yaml); any missing cell file -> SimulationIncomplete (exit 3, nothing written) in FINAL and DRAFT; an ok cell must have reps x 3 rows (reps from the yaml) and, in FINAL, `# reps_override=none`; no_qualifying_pair cells have 0 rows and are counted
  </behavior>
  <action>
    1. RED: tests/ta_r4/test_sim_by_method_and_cells.py (R unit case with a fit panel whose ladder returns NULL via a
       stubbed run_susie_with_ladder in the sourced env; Python cases for e8 grouping and the cell requirement with a
       tmp simulation.yaml listing 2 regions). Run; paste failures.
    2. Implement in simulate_coloc_r4.R (remove the identity refit block; add the columns) and in estimands /
       run_aggregation. Update test_simulation_harness.py and test_run_aggregation.py fixtures (fixture repo carries its
       own simulation.yaml with exactly its cells) — list each update in the SUMMARY.
    3. GREEN. Negative controls (paste): NC1 restore the identity refit → the no-refit case fails; NC2 pool methods in
       e8 → the by-method case fails; NC3 delete one fixture cell file → aggregation exits 3 (test asserts).
    4. §C: $QUICK (wall time), $HEAVY for this plan's files, pins file. `git fsck`; explicit-path commit of all
       files_modified except the LOG (`feat(ta-r4-W3f): N8 row_drops, N9/N10 widened E4/E6, N12 QTL fallback export, N14 simulation`);
       `git fsck`; push. LOG entry (RED/GREEN/NC outputs, table count before/after, Track B counts, QTL tier equality,
       QUICK time); refresh the W3f progress line in STATE.md (§C); commit LOG and STATE.md; push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sim_by_method_and_cells.py tests/ta_r4/test_simulation_harness.py tests/ta_r4/test_run_aggregation.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; RED and NC1–NC3 outputs pasted
    - with the committed simulation.yaml, the expected-cell function returns 100 cells (asserted)
    - `git log origin/m3-W2-aou-deltas..HEAD` is empty after the push
  </acceptance_criteria>
  <done>The calibration arm uses the production failure policy and reports per method over a complete design.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| per-row outputs → reported tables | a reporting gap hides a state the amendment promises to report |
| shared aggregator → Track B | a change to aggregate_qtl_coloc.py could alter Track B outputs |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f4-01 | Repudiation | drops / fallbacks not reported | mitigate | row_drops with internal reconciliation; qtl_rows export; NCs |
| T-r4-W3f4-02 | Tampering | Track B aggregate output | mitigate | flag-gated columns; byte-identical differential test vs the pre-change script |
| T-r4-W3f4-03 | Tampering | partial simulation read as complete | mitigate | expected 100-cell set from the yaml; SimulationIncomplete; replicate count check |
</threat_model>

<verification>
Widened E4/E6, row_drops, QTL export and simulation behaviours pass with observed RED and negative controls;
Track B outputs unchanged.
</verification>

<success_criteria>
Every reporting commitment the review found unmet is implemented in code, not narrowed in text.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-reporting-widening-qtl-sim-SUMMARY.md`
</output>
