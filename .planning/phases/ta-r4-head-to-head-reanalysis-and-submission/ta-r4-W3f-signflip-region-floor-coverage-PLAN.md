---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.3
slug: W3f-signflip-region-floor-coverage
type: execute
wave: 15.3
depends_on: ["ta-r4-W3f-lock-paths-input-sha-in-job-gate"]
gap_closure: true
files_modified:
  - config/ta_r4/decision_rules.yaml
  - src/python/ta_r4/estimands.py
  - src/python/ta_r4/run_aggregation.py
  - src/python/ta_r4/extract_paste_block.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - tests/ta_r4/test_region_signflip.py
  - tests/ta_r4/test_confirmatory_completeness.py
  - tests/ta_r4/test_contrast_stats.py
  - tests/ta_r4/test_branch_classifier.py
  - tests/ta_r4/test_run_aggregation.py
  - tests/ta_r4/test_amendment_text.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "The confirmatory direction test is an exact region-level sign-flip test on d_r = b_r - c_r (both_have_cs subset, threshold_primary); the McNemar category is decided by its p and the sign of T; row-level exact McNemar b, c, p remain as descriptive columns only (Codex N7a, DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor)"
    - "n_both_ok requires n_both >= n_both_min AND n_regions >= n_regions_min (7); fewer contributing regions yields NON_INFORMATIVE (Codex N7b)"
    - "Codex's counterexample (10 rows from one region) no longer classifies as INFLATION_SUPPORTED: with the full 100-row manifest the estimator refuses (incomplete); with a 10-row manifest it is NON_INFORMATIVE"
    - "The confirmatory estimator compares observed outputs with the manifest's confirmatory rows and refuses on any missing row; run_aggregation runs coloc_coverage and refuses to write FINAL tables on any missing or extra output (Codex N6)"
    - "The 36-row truth table is unchanged: 18 NON_INFORMATIVE / 3 NO_SYSTEMATIC_DIFFERENCE / 3 HETEROGENEOUS / 2 INFLATION_SUPPORTED / 2 DEFLATION / 8 partial rule; HETEROGENEOUS total 11 under the proposed partial rules (T13)"
    - "The DRAFT carries render_confirmatory(rules) of the new confirmatory block verbatim, so test_amendment_text stays green"
  artifacts:
    - path: "src/python/ta_r4/estimands.py"
      provides: "region_signflip(); n_regions; ConfirmatoryIncomplete; contrast_stats(rows, X, ref, rules, manifest)"
    - path: "config/ta_r4/decision_rules.yaml"
      provides: "confirmatory.region_signflip, confirmatory.n_regions_min: 7, updated categories text"
    - path: "tests/ta_r4/test_region_signflip.py"
      provides: "hand-computed exact p values, Monte Carlo path, counterexample"
  key_links:
    - from: "src/python/ta_r4/estimands.py::categorize"
      to: "decision_rules.yaml confirmatory.n_regions_min / region_signflip.exact_max_k"
      via: "read at call time; a missing key raises (no defaults)"
      pattern: "n_regions_min"
    - from: "src/python/ta_r4/run_aggregation.py::run_aggregation"
      to: "src/python/ta_r4/coloc_coverage.py::expected_ids/check"
      via: "called for EUR and AFR before build_tables"
      pattern: "coloc_coverage"
---

<objective>
W3f fix-up, plan 3 of 6: the confirmatory statistics (review N7, both parts, as Carter decided) and the
completeness safeguard (N6).

Purpose: the McNemar test treated dependent trait-pair rows as independent and nothing required more than one
region; aggregation could classify an incomplete row set. Both could produce a confident branch from ten rows of
one region.
Output: exact region-level sign-flip test, region floor, estimator-level completeness check, coverage-gated FINAL
writes, the rendered confirmatory block in the DRAFT, tests with RED and negative controls.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3d-estimators-and-branch-classifier-SUMMARY.md

Standing rules: PLAN-INDEX §A/§B/§C. The committed decision_rules.yaml is never weakened to make a fixture pass:
fixture repos (tmp_path) may carry their own decision_rules.yaml (e.g. a lower n_regions_min) to reach branches
other than NON_INFORMATIVE, and each such override is named in the SUMMARY.

<interfaces>
src/python/ta_r4/estimands.py (current):
  select_manifest(manifest, spec); confirmatory_rows(manifest, rules)
  paired_frame(rows, X, ref, p12_key, both_rule, row_ids=None, a1_varset=None)  # inner join on row_id
  e1_paired_delta(...) -> {"both_have_cs": df, "all_rows": df}
  cluster_bootstrap_ci(values, clusters, B, seed, level, stat)
  _binom_two_sided(k, n); mcnemar_exact(b, c) -> (p, direction); cohen_kappa(table)
  _calls(p, thr) -> (a, b, c, d); agreement(p, thr) -> dict(threshold, n, a, b, c, d, kappa, observed_agreement, mcnemar_p, mcnemar_direction)
  describe_contrast(rows, X, ref, rules, row_ids, p12_key, both_rule, a1_varset=None, threshold=None) -> dict(..., n_both, ci_lo, ci_hi, sign_p, mcnemar_b, mcnemar_c, mcnemar_p, kappa, observed_agreement)
  categorize(stats, rules) -> {"n_both_ok", "ci", "mcnemar", "kappa_ok"}
  contrast_stats(rows, X, ref, rules) -> describe_contrast(...) + categories; ids are rebuilt from `rows` (the defect)
src/python/ta_r4/branch_classifier.py: classify(contrast_stats, rules); enumerate_truth_table(rules); category domains CI, MCNEMAR unchanged
src/python/ta_r4/coloc_coverage.py: expected_ids(manifest, ancestry, p12_keys, arms, a1_varsets) -> set[str]; check(expected, repo) -> (missing, extra)
src/python/ta_r4/run_aggregation.py: run_aggregation(repo, out_dir, *, draft=False, purity_runner) -> int (2 = DRAFT refused); build_tables(repo, rules, man, rows, fits, purity_runner)
src/python/ta_r4/extract_paste_block.py: render_confirmatory(rules) -> str (lines for contrasts, row set, clusters, both_have_cs, CI, McNemar/kappa, n_both, categories, precedence, exclusions)
src/python/ta_r4/signoff.py: canonical_sha256(obj) (the W4a-T3 confirmatory_sha256)
decision_rules.yaml confirmatory block (current): contrasts, reference_arm, rows, clusters, both_have_cs, ci, mcnemar_kappa {subset, call}, n_both {subset}, categories {n_both_ok, ci, mcnemar, kappa_ok}, excluded_from_classifier
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: N7 — exact region-level sign-flip test and the n_regions_min floor</name>
  <files>src/python/ta_r4/estimands.py, config/ta_r4/decision_rules.yaml, tests/ta_r4/test_region_signflip.py, tests/ta_r4/test_contrast_stats.py, tests/ta_r4/test_branch_classifier.py</files>
  <read_first>
    - src/python/ta_r4/estimands.py (whole), src/python/ta_r4/branch_classifier.py
    - config/ta_r4/decision_rules.yaml
    - tests/ta_r4/test_contrast_stats.py, tests/ta_r4/test_branch_classifier.py, tests/ta_r4/fixtures/estimand_fixtures.py
    - .planning/DECISIONS.md entry DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor (written in plan 15.1)
  </read_first>
  <behavior>
    - region_signflip(d_by_region, *, exact_max_k, B, seed) with d_by_region = {region: integer d_r}: k = #regions with d_r != 0; T = sum d_r; exact when k <= exact_max_k: p = #{s in {±1}^k : |sum s_r d_r| >= |T|} / 2^k (integer arithmetic); returns {"T", "k", "p", "method": "exact"|"monte_carlo", "direction": "X>A3"|"A3>X"|"none"}
    - exact p: d = 7 regions of +1 -> 0.015625; 6 regions of +1 -> 0.03125; [1,1,1] -> 0.25; [3,1,1] -> 0.25; [2,-1] -> 1.0; all d_r = 0 -> k 0, p 1.0, direction none
    - k > exact_max_k: seeded Monte Carlo, p = (1 + #{|T*| >= |T|}) / (B + 1), deterministic for a fixed seed; with exact_max_k forced to 5 on a k = 12 case, the MC p is within 4 binomial SE of the exact p
    - describe_contrast adds n_regions (distinct region_safe of the both_have_cs subset), signflip_T, signflip_k, signflip_p, signflip_method, signflip_direction; keeps mcnemar_b, mcnemar_c, mcnemar_p (descriptive)
    - categorize: n_both_ok = n_both >= n_both_min and n_regions >= confirmatory.n_regions_min; mcnemar = sig_X_gt_A3 if signflip_p < alpha and T > 0; sig_A3_gt_X if signflip_p < alpha and T < 0; else ns. Missing yaml keys (n_regions_min, region_signflip.exact_max_k) raise KeyError/ValueError
    - 7 contributing regions with d_r = [1,1,1,1,1,1,0] (one region has both_have_cs rows but no discordance): n_regions 7 so n_both_ok can be True, k = 6, p = 0.03125, category mcnemar = ns (the floor is necessary, not sufficient)
    - a case where row-level McNemar is significant but the region-level test is not (e.g. 10 discordant rows b=10, c=0 spread over 3 regions) categorizes mcnemar = ns and n_both_ok False if n_regions < 7
    - enumerate_truth_table counts unchanged: 18/3/3/2/2 + 8 partial_rule; HETEROGENEOUS = 11 with all partial_rule keys HETEROGENEOUS (T13)
  </behavior>
  <action>
    1. RED: write tests/ta_r4/test_region_signflip.py (unit cases above + categorize cases) and add the
       n_regions / signflip columns expectations to test_contrast_stats.py; add the T13 count assertion to
       test_branch_classifier.py if not already exact. Run; paste failures.
    2. decision_rules.yaml, inside `confirmatory:` (so `confirmatory_sha256` binds it):
       ```yaml
         region_signflip: {subset: both_have_cs, call: "region_stat >= threshold_primary", d_r: "b_r - c_r per region (b = X calls H4 and A3 does not; c = the reverse)", statistic: "T = sum of d_r over regions", p: "two-sided P(|T*| >= |T|) over all 2^k sign assignments of the k regions with d_r != 0", exact_max_k: 20, monte_carlo: "if k > exact_max_k: bootstrap_B draws with bootstrap_seed, p = (1 + #{|T*| >= |T|}) / (B + 1)"}
         n_regions_min: 7      # distinct regions with >= 1 both_have_cs row; necessary, not sufficient: min two-sided sign-flip p = 2/2^k, k = regions with non-zero d_r (k=6: 0.03125 > alpha; k=7: 0.015625)
         n_regions: {subset: both_have_cs}
       ```
       `mcnemar_kappa` keeps `{subset: both_have_cs, call: "region_stat >= threshold_primary"}` (kappa and descriptive
       row-level McNemar). categories: `n_both_ok: "n_both >= n_both_min and n_regions >= n_regions_min"`;
       `mcnemar: "sig_X_gt_A3 if signflip_p < alpha and T > 0; sig_A3_gt_X if signflip_p < alpha and T < 0; else ns (decided by region_signflip; row-level McNemar is descriptive)"`.
       `ci`, `kappa_ok`, alpha, n_both_min, kappa_cut, partial_rule, locked: false unchanged.
    3. estimands.py: implement region_signflip (exact via numpy over the 2^k sign matrix in chunks so k = 20 stays
       under ~200 MB; integer d_r), the describe_contrast columns (d_r from `_calls` per region on the both_have_cs
       subset), and categorize per the behaviour (read n_regions_min and exact_max_k from rules["confirmatory"]).
       mcnemar_exact stays and is reported, not used for categories.
    4. GREEN. Negative controls (paste): NC1 categorize from row-level mcnemar_p again → the "rows significant,
       regions not" case fails; NC2 drop the n_regions term from n_both_ok → the floor case fails; NC3 off-by-one
       (count |T*| > |T|) → the hand-computed p cases fail.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_region_signflip.py tests/ta_r4/test_contrast_stats.py tests/ta_r4/test_branch_classifier.py tests/ta_r4/test_estimands.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; the hand-computed p values are asserted exactly (0.015625, 0.03125, 0.25, 0.25, 1.0, 1.0), including the 7-regions-k-6 case (n_regions 7, k 6, p 0.03125, ns)
    - RED output and NC1–NC3 failures pasted in the SUMMARY
    - truth-table counts printed by the test equal 18/3/3/2/2/8 and HETEROGENEOUS total 11
  </acceptance_criteria>
  <done>The branch-driving direction test respects region clustering and cannot reach significance from fewer than seven regions.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: N6 — confirmatory completeness in the estimator and coverage-gated FINAL aggregation</name>
  <files>src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, tests/ta_r4/test_confirmatory_completeness.py, tests/ta_r4/test_run_aggregation.py, tests/ta_r4/test_contrast_stats.py</files>
  <read_first>
    - src/python/ta_r4/run_aggregation.py, src/python/ta_r4/coloc_coverage.py, tests/ta_r4/test_run_aggregation.py (fixture repo; FINAL fixture with write_fixture_lock), tests/ta_r4/test_coloc_coverage.py
    - the review's N6 counterexample text (10 rows from one region; INFLATION_SUPPORTED, n_both 10, CI [0.2, 0.2], McNemar p 0.001953125)
  </read_first>
  <behavior>
    - contrast_stats(rows, X, ref, rules, manifest) (manifest required, no default): expected ids = select_manifest(manifest, confirmatory rows spec without p12_key/a1_varset); each side (X, ref) must have exactly one output per expected id for the confirmatory p12_key (and a1_varset for A1); otherwise raise ConfirmatoryIncomplete naming the contrast and the counts missing per side (first 5 ids); outputs with method none count as present (they are rows, excluded later by both_have_cs)
    - counterexample A: manifest of 100 confirmatory rows over 10 regions, outputs for 10 rows of one region with the review's values -> ConfirmatoryIncomplete (not INFLATION_SUPPORTED)
    - counterexample B: the same 10 outputs with a manifest holding only those 10 rows -> branch NON_INFORMATIVE via rule1_n_both (n_regions 1 < 7)
    - run_aggregation FINAL (fixture lock): coloc_coverage.expected_ids + check for EUR and AFR before build_tables; any missing or extra -> exit 3, stderr lists counts and the first 20 paths, no table files written; complete coverage -> tables written with `# status=FINAL`
    - run_aggregation --draft: coverage computed and reported on stderr and as a second header line `# coverage=EUR missing=<n> extra=<n>; AFR missing=<n> extra=<n>` in every table; tables still DRAFT-labelled
  </behavior>
  <action>
    1. RED: tests/ta_r4/test_confirmatory_completeness.py (counterexamples A and B, the method-none-counts-as-present
       case, the FINAL exit-3 case, the DRAFT header case). Run; paste failures, including counterexample A
       returning INFLATION_SUPPORTED on the current code.
    2. Implement: ConfirmatoryIncomplete(ValueError) and the completeness check in contrast_stats (new `manifest`
       parameter); run_aggregation passes `man`; coverage in run_aggregation as specified (exit code 3 is new; 2 stays
       "DRAFT refused"). Update existing test_contrast_stats.py / test_run_aggregation.py call sites to pass the
       manifest, and give fixture repos a complete set of expected outputs or their own decision_rules.yaml where a
       non-NON_INFORMATIVE branch is asserted (name each override in the SUMMARY).
    3. GREEN. Negative controls (paste): NC1 rebuild ids from `rows` again (the old line) → counterexample A passes
       through and its test fails; NC2 skip the coverage call → the FINAL exit-3 test fails.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_confirmatory_completeness.py tests/ta_r4/test_run_aggregation.py tests/ta_r4/test_contrast_stats.py tests/ta_r4/test_coloc_coverage.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; counterexample A observed returning INFLATION_SUPPORTED before the fix and raising ConfirmatoryIncomplete after (both pasted); counterexample B returns ("NON_INFORMATIVE", "rule1_n_both")
    - the FINAL incomplete case exits 3 and the output directory contains no .tsv (asserted)
    - NC1/NC2 failures pasted
  </acceptance_criteria>
  <done>No branch can be produced from a row set that does not match the manifest.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: render the new confirmatory block into the DRAFT; record the interim sha; commit, push, LOG</name>
  <files>src/python/ta_r4/extract_paste_block.py, tests/ta_r4/test_amendment_text.py, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - src/python/ta_r4/extract_paste_block.py (render_confirmatory), tests/ta_r4/test_amendment_text.py (test_render_confirmatory_reads_the_yaml, test_confirmatory_check_fails_on_a_changed_cluster_rule, test_draft_extract_carries_the_rendered_confirmatory_block)
    - .planning/amendments/osf-amendment-r4-DRAFT.md paragraph (e) (the rendered block after "The confirmatory analysis is exactly:")
  </read_first>
  <behavior>
    - render_confirmatory(rules) renders a line for the region sign-flip test (subset, d_r, statistic, p, exact_max_k, Monte Carlo rule, B, seed) and a line for n_regions / n_regions_min; the McNemar/kappa line states that row-level McNemar is descriptive
    - a tmp yaml with n_regions_min 6 renders text the DRAFT extract does not contain -> the rendered-block test fails (negative control)
  </behavior>
  <action>
    1. RED: extend test_render_confirmatory_reads_the_yaml for the new lines; run; paste.
    2. Implement the render lines (wording taken from the yaml strings, no hand-typed numbers). Paste
       `render_confirmatory(yaml.safe_load(open("config/ta_r4/decision_rules.yaml")))` output into DRAFT (e) in place
       of the old rendered block, unchanged. Other DRAFT prose is plan 15.5.
    3. GREEN: test_amendment_text.py. Negative control: tmp yaml n_regions_min 6 → the rendered-block check fails (paste).
    4. Compute the interim sha:
       `cd src/python && $PY -c "import yaml; from ta_r4.signoff import canonical_sha256; print(canonical_sha256(yaml.safe_load(open('../../config/ta_r4/decision_rules.yaml'))['confirmatory']))"`
       Record old f6e6e90f83fd14975d3afa04789c3dcf1a9211b8e3ddd38bf23c72f8cbe0e9e3 → interim value in the LOG (final value is recomputed in plan 15.5).
    5. §C: $QUICK (wall time), the heavy aggregation tests, pins file. `git fsck`; explicit-path commit of all
       files_modified except the LOG (`feat(ta-r4-W3f): N7 region sign-flip test + n_regions_min 7; N6 completeness and coverage-gated FINAL`);
       `git fsck`; push. LOG entry (RED/GREEN/NC outputs, counterexample results, interim sha, QUICK time); refresh the W3f progress line in STATE.md (§C); commit LOG and STATE.md; push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py tests/ta_r4/test_region_signflip.py tests/ta_r4/test_confirmatory_completeness.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - test_amendment_text.py passes with the new rendered block; its NC observed failing
    - the LOG records old and interim confirmatory_sha256 and the command that produced the interim value
    - `git log origin/m3-W2-aou-deltas..HEAD` is empty after the push
  </acceptance_criteria>
  <done>The yaml, the estimator and the DRAFT's confirmatory sentences agree, and the change is pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| observed outputs → branch | the classifier must only ever see the pre-specified row set |
| yaml rule → category | the category must follow the locked rule, not a code default |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f3-01 | Tampering | incomplete outputs classified | mitigate | ConfirmatoryIncomplete in contrast_stats; coverage exit 3 before FINAL writes; NC1/NC2 |
| T-r4-W3f3-02 | Tampering | dependent rows treated as independent | mitigate | region-level sign-flip decides the category; n_regions_min 7 bound by confirmatory_sha256 |
| T-r4-W3f3-03 | Repudiation | DRAFT vs yaml drift | mitigate | rendered block pasted unchanged; text test with negative control |
</threat_model>

<verification>
Exact p values, floor, counterexamples, completeness and coverage gates pass with observed RED and negative
controls; the truth table is unchanged; the DRAFT carries the rendered block.
</verification>

<success_criteria>
The confirmatory branch is computed only from the complete pre-specified row set with a cluster-respecting test.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-signflip-region-floor-coverage-SUMMARY.md`
</output>
