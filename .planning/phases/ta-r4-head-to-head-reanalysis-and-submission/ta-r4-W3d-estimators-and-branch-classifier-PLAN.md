---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 14
slug: W3d-estimators-and-branch-classifier
type: execute
wave: 14
depends_on: ["ta-r4-W3c-simulation-harness"]
files_modified:
  - config/ta_r4/decision_rules.yaml
  - src/python/ta_r4/estimands.py
  - src/python/ta_r4/branch_classifier.py
  - src/python/ta_r4/coloc_coverage.py
  - src/snakemake/scripts/ta_r4/cs_cross_purity.R
  - tests/ta_r4/test_estimands.py
  - tests/ta_r4/test_branch_classifier.py
  - tests/ta_r4/test_cs_cross_purity.py
  - tests/ta_r4/test_coloc_coverage.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-OSF-PREREG
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "E1-E8 are implemented as pure, tested functions before any production data exists, and the code commit sha is cited by the W4a amendment (rigor upgrade 1; D-26)"
    - "The region-level PP.H4 statistic is fixed: coloc_susie → pp_h4_max over CS pairs; A1 and fallback_abf → PP.H4; fallback rows are flagged and every estimand is reported on (i) the both-have-CS subset and (ii) all rows with fallback labelled (Pitfall 8, D-02)"
    - "E1 uses a region-cluster bootstrap (B = 10000, seed 20261021, percentile 95% CI, clusters = admissible regions) and a paired sign test; E2 uses 2x2 tables, Cohen's kappa and an exact McNemar at {0.5, 0.7, 0.8, 0.9}; the confirmatory contrasts A1 vs A3 and A2 vs A3 each use alpha 0.025"
    - "The branch classifier applies a fixed precedence (n_both first; then CI includes 0 → kappa; then CI and McNemar agree → INFLATION/DEFLATION; else partial_rule) and maps all 36 combinations to exactly one branch: 18 NON_INFORMATIVE, 3 NO_SYSTEMATIC_DIFFERENCE, 3 HETEROGENEOUS, 2 INFLATION_SUPPORTED, 2 DEFLATION, and 8 via partial_rule (checker W5)"
    - "The 8 uncovered combinations are exactly: CI > 0 with McNemar non-significant or significant A3>X, and CI < 0 with McNemar non-significant or significant X>A3 (each × kappa ok/not ok); decision_rules.yaml carries one partial_rule key per (CI sign, McNemar state) pair (4 keys), each a draft for Carter to lock in W4a (D-26)"
    - "Estimand outputs are labelled DRAFT unless decision_rules.yaml, coloc_priors.yaml and simulation.yaml all carry locked: true, signoffs/W4a-T3.yaml verifies, AND the offline OSF gate passes for stage production"
    - "Cross-evaluated purity scores A2 credible sets against the real 1000G R (Pitfall 9)"
    - "coloc_coverage.py proves output ids == the expected (admissible row × production arm of the ancestry + A1_<ANC> matched/allvars × p12 key) set exactly; it is analysis code, so it exists before the lock and the amendment cites it (B2)"
  artifacts:
    - path: "src/python/ta_r4/estimands.py"
      provides: "load_rows, region_stat, e1_paired_delta, cluster_bootstrap_ci, sign_test, e2_agreement, mcnemar_exact, cohen_kappa, e3_reclassification, e4_finemap_structure, e5_diagnostics, e6_panel_contrast, e7_frozen_vs_fixed, e8_simulation_rates, wilson_ci"
    - path: "src/python/ta_r4/branch_classifier.py"
      provides: "classify(contrast_stats, rules) -> (branch, via); enumerate_truth_table(rules)"
    - path: "src/python/ta_r4/coloc_coverage.py"
      provides: "expected-vs-observed coverage over manifest × arm × p12 (CLI exits 1 on any missing/extra)"
    - path: "config/ta_r4/decision_rules.yaml"
      provides: "alpha, kappa_cut, n_both_min, thresholds, bootstrap B/seed, partial_rule (4 keys), locked: false"
  key_links:
    - from: "src/python/ta_r4/estimands.py"
      to: "config/ta_r4/decision_rules.yaml"
      via: "read at call time; DRAFT label unless locked + signed off + gate"
      pattern: "locked"
    - from: "src/python/ta_r4/coloc_coverage.py"
      to: "src/python/ta_r4/arms.py::production_arms"
      via: "expected arms per ancestry"
      pattern: "production_arms"
---

<objective>
Wave 3d writes and tests every estimator (E1–E8), the outcome-branch classifier and the coloc
coverage tool before the OSF post. The pre-registration can then cite frozen analysis code, the
decision rule is total with a stated precedence, and no production completeness check is written
after the lock.

Purpose: D-26, D-02 (dual reporting), D-23 (E8 rates), Pitfalls 8 and 9; REQ-PP.H4-THRESHOLD-SWEEP;
checker B2 (coverage tool pre-lock) and W5 (precedence + enumerated uncovered combinations).
Output: estimator, classifier and coverage modules, the cross-purity R helper, decision rules (draft), tests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3c-simulation-harness-SUMMARY.md

<interfaces>
Coloc JSON keys (W0d): row_id, arm, mode, method, p12_key, pp_h0..pp_h4 (abf/fallback), pp_h4_max, n_cs_pairs, n_cs_pairs_h4_ge_0.8,
  n_cs_a, n_cs_b, fallback_reason, priors, variant_set_sha256, n_snps
Coloc output paths (W0d): data/r4/results/{ARM}/coloc/{row_id}.{p12key}.json; data/r4/results/A1_{ANC}/coloc/{row_id}.{matched|allvars}.{p12key}.json
Fit JSON keys: status, n_CS / cs fields, d3b_ld_z_consistency_s (estimate_s_rss λ̂), kriging fields (read run_susie_rss.R for exact names),
  ld_allele_exact, ld_allele_flipped
QTL JSON counters (W1): qtl_orient_exact, qtl_orient_flipped, qtl_orient_dropped_*
Sim TSV (W3c): region, scenario, gen_panel, rep, seed, arm, method, pp_h0..pp_h4, pp_h4_max, n_cs_a, n_cs_b, causal_a, causal_b, r2_causal
From W0b1/W0b2: ta_r4.arms.production_arms(ancestry), ta_r4.paths.result_dirs, ta_r4.signoff.verify_signoff, ta_r4.r4_osf_gate.{check_osf_gate, verify_online}
Branch table (RESEARCH §Estimands, draft per D-26):
  INFLATION_SUPPORTED: McNemar X>A3 at alpha AND bootstrap CI of median ΔPP.H4 excludes 0 (positive)
  NO_SYSTEMATIC_DIFFERENCE: CI includes 0 AND kappa >= 0.6
  DEFLATION: mirror of INFLATION
  HETEROGENEOUS: CI includes 0 AND kappa < 0.6
  NON_INFORMATIVE: n_both < 10
smoke_dev Python 3.11: check numpy/pandas availability; implement exact binomial with math.comb (no scipy dependency)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED → GREEN for estimators, the total classifier with explicit precedence, and cross purity</name>
  <files>config/ta_r4/decision_rules.yaml, src/python/ta_r4/estimands.py, src/python/ta_r4/branch_classifier.py, src/snakemake/scripts/ta_r4/cs_cross_purity.R, tests/ta_r4/test_estimands.py, tests/ta_r4/test_branch_classifier.py, tests/ta_r4/test_cs_cross_purity.py</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Estimands and decision rules", §"Pitfall 8", §"Pitfall 9"
    - src/python/ta_r4/r4_osf_gate.py and src/python/ta_r4/signoff.py (for the FINAL-label check)
    - config/pph4_thresholds.yaml (REQ sweep values)
    - src/legacy/region_analysis/scripts/run_susie_rss.R (grep the JSON key names for estimate_s / kriging; read only)
  </read_first>
  <behavior>
    Estimators (synthetic inputs with hand-computed answers):
    - region_stat: coloc_susie row → pp_h4_max; fallback → PP.H4 with is_fallback True; A1 → PP.H4
    - e1_paired_delta: rows joined on (row_id, p12_key). Deltas for X in {A1_matched, A2}. The both_have_cs subset (A2 vs A3: both coloc_susie; A1 vs A3: A3 coloc_susie) and the all_rows set are both returned
    - cluster_bootstrap_ci: B = 10000 and the same seed give an identical CI. If all deltas = 0.1, the CI is [0.1, 0.1]. Resampling is over clusters, not rows: a test with 1 cluster holding all the variance gives a CI wider than a row bootstrap would
    - sign_test: 8 positive / 0 negative / 2 ties → exact two-sided p = 2 × 0.5^8 = 0.0078125; ties are excluded
    - mcnemar_exact: b=10, c=0 → p = 2 × 0.5^10 = 0.001953125, direction "X>A3"; b=c → p = 1.0
    - cohen_kappa: [[20,5],[10,15]] → kappa = (0.7 − 0.5)/(1 − 0.5) = 0.4 exactly (expected agreement 0.5 by construction of the margins: (25×30 + 25×20)/50² = 0.5)
    - e2 at all four thresholds; e3 argmax table; e4 no-CS rate per arm = rows with n_cs == 0 on either side / rows
    - e8: false-H4 = share of H3 reps with region PP.H4 >= 0.8, per (arm, r² bin, gen_panel), with a Wilson 95% CI; 0 of 200 → CI upper ≈ 0.0188 (Wilson, z = 1.96)
    - e7 joins known_answer_W3a / known_answer_sh2b3 (frozen side) with R4-A3 rows (fixed side) on fit or pair ids and reports flipped share = flipped / (exact + flipped) per region (fine-map) and per QTL row
    - Labelling: with any of the three configs unlocked → every output carries `status: DRAFT`. All three locked but no valid W4a-T3 sign-off → DRAFT. All locked + a valid fixture sign-off + a passing offline gate (fixture repo with fixture sentinel and a receipt written by verify_online with a fake fetch) → `status: FINAL`
    Classifier (inputs: n_both_ok ∈ {T, F}; mcnemar ∈ {sig_X_gt_A3, sig_A3_gt_X, ns}; ci ∈ {pos, neg, incl0}; kappa_ok ∈ {T, F}; 2 × 3 × 3 × 2 = 36 combinations):
    - Precedence, applied in order, first match wins:
      1. n_both_ok == F → NON_INFORMATIVE (18 combos; via "rule1_n_both")
      2. ci == incl0 → NO_SYSTEMATIC_DIFFERENCE if kappa_ok else HETEROGENEOUS, whatever McNemar says (6 combos: 3 + 3; via "rule2_ci_includes_0")
      3. ci == pos and mcnemar == sig_X_gt_A3 → INFLATION_SUPPORTED (2 combos; via "rule3_agree")
      4. ci == neg and mcnemar == sig_A3_gt_X → DEFLATION (2 combos; via "rule3_agree")
      5. otherwise → rules["partial_rule"][key] with key ∈ {ci_pos_mcnemar_ns, ci_pos_mcnemar_opposite, ci_neg_mcnemar_ns, ci_neg_mcnemar_opposite} (8 combos: 4 keys × kappa ok/not; via "partial_rule:<key>")
    - enumerate_truth_table returns 36 rows; the test asserts uniqueness and total coverage, and the per-branch counts 18 / 3 / 3 / 2 / 2 / 8 (sum 36)
    - The test asserts the 8 partial_rule rows are exactly the (ci, mcnemar) pairs {(pos, ns), (pos, sig_A3_gt_X), (neg, ns), (neg, sig_X_gt_A3)} × kappa_ok {T, F}
    - Negative controls: deleting any one partial_rule key makes the coverage test fail; swapping steps 1 and 2 reclassifies the (n_both_ok F, ci incl0) combos away from NON_INFORMATIVE, so the per-branch count test goes RED
    Cross purity (R):
    - cs_cross_purity.R --fit A2.fit.rds --panel EUR_1kg_r4.rds → for each CS, the minimum |r| among CS members under the given panel. On a fixture where an identity-LD CS contains two variants with real |r| = 0.1, it returns 0.1 (while the purity under R = I is 1)
  </behavior>
  <action>
    RED: write all three test modules and run them; paste the failures.
    GREEN:
    - `estimands.py` and `branch_classifier.py` (numpy + pandas from smoke_dev; record versions).
    - `cs_cross_purity.R` (r_coloc env).
    - `decision_rules.yaml`:
      ```
      alpha: 0.025
      kappa_cut: 0.6
      n_both_min: 10
      threshold_primary: 0.8
      threshold_secondary: 0.5
      sweep: [0.5, 0.7, 0.8, 0.9]
      bootstrap_B: 10000
      bootstrap_seed: 20261021
      ci_level: 0.95
      region_stat_coloc_susie: pp_h4_max
      precedence: [n_both, ci_includes_0, ci_mcnemar_agree, partial_rule]
      partial_rule:
        ci_pos_mcnemar_ns: HETEROGENEOUS
        ci_pos_mcnemar_opposite: HETEROGENEOUS
        ci_neg_mcnemar_ns: HETEROGENEOUS
        ci_neg_mcnemar_opposite: HETEROGENEOUS
      locked: false
      notes: "kappa_cut, n_both_min and the four partial_rule entries are Carter's to lock in W4a (D-26)"
      ```
    Negative controls, each observed RED and then restored: delete one partial_rule key (coverage
    test RED); swap precedence steps 1 and 2 (precedence test RED); make the bootstrap resample rows
    instead of clusters (cluster-width test RED). Never call any estimator on real production data
    in this plan; none exists yet.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_estimands.py tests/ta_r4/test_branch_classifier.py tests/ta_r4/test_cs_cross_purity.py -q</automated>
  </verify>
  <acceptance_criteria>
    - all pass; the SUMMARY shows the RED run and the three negative-control REDs
    - the SUMMARY pastes the 36-row truth table with branch and `via` columns and the per-branch counts 18/3/3/2/2/8. The 8 partial_rule rows go into the W4a amendment as an explicit decision for Carter
  </acceptance_criteria>
  <done>The analysis is fully specified in tested code before the data exist, with a total, ordered decision rule.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Coloc coverage tool (TDD), moved pre-lock (B2)</name>
  <files>src/python/ta_r4/coloc_coverage.py, tests/ta_r4/test_coloc_coverage.py</files>
  <read_first>
    - config/ta_r4/pair_manifest.tsv; src/python/ta_r4/paths.py; src/python/ta_r4/arms.py
    - src/snakemake/rules/ta_r4_coloc.smk (output path patterns)
  </read_first>
  <behavior>
    - expected_ids(manifest, ancestry, p12_keys=("p12_primary","p12_sensitivity")) returns the set of output paths for admissible rows of that ancestry: one per (row, production arm of that ancestry from `production_arms(ancestry)`, p12 key), plus A1_<ANC> matched and allvars per (row, p12 key)
    - check(expected, repo) globs only the dirs those paths live in (the ancestry's arms from `result_dirs("coloc")`) and returns (missing, extra)
    - CLI `python -m ta_r4.coloc_coverage --ancestry {EUR,AFR} --repo PATH` prints `missing=<n> extra=<n> expected=<n>` and exits 1 if missing or extra is non-zero
    - On the real manifest (no outputs yet) `expected` is 290 × 2 × 7 = 4060 for EUR (5 production EUR arms + 2 A1 varsets) and 30 × 2 × 5 = 300 for AFR (3 production AFR arms + 2 A1 varsets); a test asserts both numbers from the committed manifest and ARMS
    - Fixture: 3 rows × 2 arms × 2 keys → 12 expected; deleting one file gives missing == {that path}; a stray file is reported as extra; a repro-arm file is never counted
  </behavior>
  <action>Tests RED (paste), implement, GREEN. Negative control: run the CLI against a fixture dir with one file removed and observe exit 1. Record the two expected totals in the SUMMARY.</action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_coloc_coverage.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the test passes; the SUMMARY shows RED, the negative control, and expected totals 4060 (EUR) and 300 (AFR)
  </acceptance_criteria>
  <done>Coverage can be proven exactly, with code frozen before the lock.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W3d)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W3d`, commit type `feat`. The LOG records the commit sha (cited by the W4a amendment as an analysis-code commit together with W0d/W3c/W3e).</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - QUICK and HEAVY green; tests/m3 unchanged against the baseline; committed; pushed; sha in the LOG
  </acceptance_criteria>
  <done>W3d committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| results → decision rule | a rule written after seeing results is not a pre-registration |
| results on disk → completeness claim | a coverage check written after the data exist can be shaped to them |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3d-01 | Repudiation | post-hoc branch choice | mitigate | total classifier with explicit precedence (tested counts 18/3/3/2/2/8); partial_rule keys locked by Carter in W4a; code sha cited in the amendment |
| T-r4-W3d-02 | Tampering | DRAFT numbers presented as final | mitigate | FINAL requires all three configs locked, a valid W4a-T3 sign-off and the offline gate passing |
| T-r4-W3d-03 | Tampering | pseudo-replication in CIs | mitigate | cluster bootstrap over regions; a test proves cluster-not-row resampling |
| T-r4-W3d-04 | Tampering | incomplete result set | mitigate | coverage tool frozen pre-lock; expected totals asserted from the committed manifest and ARMS |
</threat_model>

<verification>
The arithmetic of every estimator is checked against hand-computed values. The classifier is total,
unique and ordered. The coverage tool exists before the lock. All negative controls were observed.
</verification>

<success_criteria>
No production number can be interpreted, or declared complete, by code that was not fixed, tested
and cited before the data existed.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3d-estimators-and-branch-classifier-SUMMARY.md`
</output>
