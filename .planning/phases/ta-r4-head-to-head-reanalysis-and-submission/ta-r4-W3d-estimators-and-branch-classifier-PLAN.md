---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 12
slug: W3d-estimators-and-branch-classifier
type: tdd
wave: 12
depends_on: ["W3c"]
files_modified:
  - config/ta_r4/decision_rules.yaml
  - src/python/ta_r4/estimands.py
  - src/python/ta_r4/branch_classifier.py
  - src/snakemake/scripts/ta_r4/cs_cross_purity.R
  - tests/ta_r4/test_estimands.py
  - tests/ta_r4/test_branch_classifier.py
  - tests/ta_r4/test_cs_cross_purity.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-OSF-PREREG
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "E1-E8 are implemented as pure, tested functions before any production data exists, and the code commit sha is cited by the W4 amendment (rigor upgrade 1; D-26)"
    - "The region-level PP.H4 statistic is fixed: coloc_susie → pp_h4_max over CS pairs; A1 and fallback_abf → PP.H4; fallback rows are flagged and every estimand is reported on (i) the both-have-CS subset and (ii) all rows with fallback labelled (Pitfall 8, D-02)"
    - "E1 uses a region-cluster bootstrap (B = 10000, seed 20261021, percentile 95% CI, clusters = admissible regions) and a paired sign test; E2 uses 2x2 tables, Cohen's kappa and an exact McNemar at {0.5, 0.7, 0.8, 0.9}; the confirmatory contrasts A1 vs A3 and A2 vs A3 each use alpha 0.025"
    - "The branch classifier maps EVERY combination of (n_both >= n_both_min, McNemar significant + direction, bootstrap CI sign, kappa >= kappa_cut) to exactly one of INFLATION_SUPPORTED, NO_SYSTEMATIC_DIFFERENCE, DEFLATION, HETEROGENEOUS, NON_INFORMATIVE; the mapping for combinations the research table leaves uncovered is an explicit `partial_rule` in decision_rules.yaml, flagged for Carter to lock in W4"
    - "Estimand outputs are labelled DRAFT unless decision_rules.yaml, coloc_priors.yaml and simulation.yaml all carry locked: true AND the OSF gate passes for stage production"
    - "Cross-evaluated purity scores A2 credible sets against the real 1000G R (Pitfall 9)"
  artifacts:
    - path: "src/python/ta_r4/estimands.py"
      provides: "load_rows, region_stat, e1_paired_delta, cluster_bootstrap_ci, sign_test, e2_agreement, mcnemar_exact, cohen_kappa, e3_reclassification, e4_finemap_structure, e5_diagnostics, e6_panel_contrast, e7_frozen_vs_fixed, e8_simulation_rates, wilson_ci"
    - path: "src/python/ta_r4/branch_classifier.py"
      provides: "classify(contrast_stats, rules) -> branch; enumerate_truth_table(rules)"
    - path: "config/ta_r4/decision_rules.yaml"
      provides: "alpha, kappa_cut, n_both_min, thresholds, bootstrap B/seed, partial_rule, locked: false"
  key_links:
    - from: "src/python/ta_r4/estimands.py"
      to: "config/ta_r4/decision_rules.yaml"
      via: "read at call time; DRAFT label unless locked"
      pattern: "locked"
---

<objective>
Wave 3d writes and tests every estimator (E1–E8) and the outcome-branch classifier before the OSF
post. The pre-registration can then cite frozen analysis code, and the decision rule is total: no
result can fall between branches.

Purpose: D-26, D-02 (dual reporting), D-23 (E8 rates), Pitfalls 8 and 9; REQ-PP.H4-THRESHOLD-SWEEP.
Output: estimator and classifier modules, the cross-purity R helper, decision rules (draft), tests.
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
Fit JSON keys: status, n_CS / cs fields, d3b_ld_z_consistency_s (estimate_s_rss λ̂), kriging fields (read run_susie_rss.R for exact names),
  ld_allele_exact, ld_allele_flipped
QTL JSON counters (W1): qtl_orient_exact, qtl_orient_flipped, qtl_orient_dropped_*
Sim TSV (W3c): region, scenario, gen_panel, rep, seed, arm, method, pp_h0..pp_h4, pp_h4_max, n_cs_a, n_cs_b, causal_a, causal_b, r2_causal
Branch table (RESEARCH §Estimands, draft per D-26):
  INFLATION_SUPPORTED: McNemar X>A3 at alpha AND bootstrap CI of median ΔPP.H4 excludes 0 (positive)
  NO_SYSTEMATIC_DIFFERENCE: CI includes 0 AND kappa >= 0.6
  DEFLATION: mirror of INFLATION
  HETEROGENEOUS: CI includes 0 AND kappa < 0.6
  NON_INFORMATIVE: n_both < 10
smoke_dev Python 3.11: check numpy/pandas availability; implement exact binomial with math.comb (no scipy dependency)
</interfaces>
</context>

<feature>
  <name>R4 estimators and the total outcome-branch classifier</name>
  <files>config/ta_r4/decision_rules.yaml, src/python/ta_r4/estimands.py, src/python/ta_r4/branch_classifier.py, src/snakemake/scripts/ta_r4/cs_cross_purity.R, tests/ta_r4/test_estimands.py, tests/ta_r4/test_branch_classifier.py, tests/ta_r4/test_cs_cross_purity.py</files>
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
    - Labelling: with any of the three configs unlocked → every output carries `status: DRAFT`. With all locked plus a passing gate (injected fake fetch) → `status: FINAL`
    Classifier:
    - enumerate_truth_table yields all 2 (n_both ok) × 3 (McNemar: sig X>A3 / sig A3>X / ns) × 3 (CI: >0 / <0 / includes 0) × 2 (kappa ok) = 36 combos. Each maps to exactly one branch; the test asserts total coverage and uniqueness
    - The five research rows map as specified. The uncovered combos, e.g. McNemar significant but CI includes 0, or CI > 0 but McNemar ns, map by `partial_rule` (draft: HETEROGENEOUS) and are listed in the output with `via: partial_rule`
    - Negative control: deleting the partial_rule key makes the coverage test fail
    Cross purity (R):
    - cs_cross_purity.R --fit A2.fit.rds --panel EUR_1kg_r4.rds → for each CS, the minimum |r| among CS members under the given panel. On a fixture where an identity-LD CS contains two variants with real |r| = 0.1, it returns 0.1 (while the purity under R = I is 1)
  </behavior>
  <implementation>
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
      partial_rule: HETEROGENEOUS
      locked: false
      notes: "kappa_cut, n_both_min and partial_rule are Carter's to lock in W4 (D-26)"
      ```
    REFACTOR only if needed. Never call any estimator on real production data in this plan; none exists yet.
  </implementation>
</feature>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED → GREEN for estimators, classifier and cross purity</name>
  <files>config/ta_r4/decision_rules.yaml, src/python/ta_r4/estimands.py, src/python/ta_r4/branch_classifier.py, src/snakemake/scripts/ta_r4/cs_cross_purity.R, tests/ta_r4/test_estimands.py, tests/ta_r4/test_branch_classifier.py, tests/ta_r4/test_cs_cross_purity.py</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Estimands and decision rules", §"Pitfall 8", §"Pitfall 9"
    - src/python/ta_r4/r4_osf_gate.py (for the FINAL-label gate check)
    - config/pph4_thresholds.yaml (REQ sweep values)
    - src/legacy/region_analysis/scripts/run_susie_rss.R (grep the JSON key names for estimate_s / kriging; read only)
  </read_first>
  <behavior>See the feature block.</behavior>
  <action>Implement per the feature block. Negative controls, each observed RED and then restored: delete `partial_rule` (coverage test RED); make the bootstrap resample rows instead of clusters (cluster-width test RED).</action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_estimands.py tests/ta_r4/test_branch_classifier.py tests/ta_r4/test_cs_cross_purity.py -q</automated>
  </verify>
  <acceptance_criteria>
    - all pass; the SUMMARY shows the RED run and both negative-control REDs
    - the SUMMARY pastes the 36-row truth table with branch and `via` columns, and lists the combos resolved by `partial_rule`. This list goes into the W4 amendment as an explicit decision for Carter
  </acceptance_criteria>
  <done>The analysis is fully specified in tested code before the data exist.</done>
</task>

<task type="auto">
  <name>Task 2: Wave-close (W3d)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W3d`, commit type `feat`. The LOG records the commit sha (cited by the W4 amendment as the frozen analysis-code commit together with W0d/W3c/W3e).</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - tests/ta_r4 green; tests/m3 unchanged against the baseline; committed; pushed; sha in the LOG
  </acceptance_criteria>
  <done>W3d committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| results → decision rule | a rule written after seeing results is not a pre-registration |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3d-01 | Repudiation | post-hoc branch choice | mitigate | the classifier is total over 36 combos (tested); config locked in W4; code sha cited in the amendment |
| T-r4-W3d-02 | Tampering | DRAFT numbers presented as final | mitigate | the FINAL label requires all three configs locked and the OSF gate passing |
| T-r4-W3d-03 | Tampering | pseudo-replication in CIs | mitigate | the cluster bootstrap over regions; a test proves cluster-not-row resampling |
</threat_model>

<verification>
The arithmetic of every estimator is checked against hand-computed values. The classifier is total
and unique. Both negative controls were observed.
</verification>

<success_criteria>
No production number can be interpreted by a rule that was not fixed, tested and cited before the
data existed.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3d-estimators-and-branch-classifier-SUMMARY.md`
</output>
