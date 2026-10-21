---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15
slug: W5a-eur-production-fits
type: execute
wave: 15
depends_on: ["W4"]
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_EUR_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_EUR_status.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "The OSF gate passes (exit 0) at the start of this plan; if it does not, the plan stops before any job is submitted (D-05, D-27)"
    - "EUR SuSiE-RSS fits exist for every (trait in 5) x (region in 10 admissible + 9 NC) under A3_1kg, A2_identity, A3_ukb, A3_ukb_isect, A3_1kg_isect (95 each), plus 5 HLA_6p21 exploratory A3_ukb fits labelled exploratory; total 480 fit JSONs, each with a receipt that validates in its arm's mode (D-01, D-03, D-07, D-13, D-24)"
    - "The live gates run (0 skips) and pass: test_no_silent_identity (every A3/A2 JSON), test_arm_variant_sets_identical (A2 vs A3_1kg, A3_ukb_isect vs A3_1kg_isect), test_priors_constant (no coloc yet → only fit-side checks)"
    - "Non-converged and early-exit fits are kept and counted (convergence is a covariate, not a filter); the status table reconciles to 480"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_EUR_status.tsv"
      provides: "arm x trait x region status / n_CS / ld_allele counters / estimate_s"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_EUR_sha256.tsv"
      provides: "sha256 of every production fit JSON, fit.rds and receipt"
  key_links:
    - from: "data/r4/results/<arm>/fine_mapping/susie/*.json"
      to: "tests/ta_r4/test_no_silent_identity.py live gate"
      via: "validate_fit in the arm's mode"
      pattern: "validate_fit"
---

<objective>
Wave 5a runs the pre-registered EUR production fine-mapping for every arm that has fits. It runs
only after the verified OSF posting, with every fit receipted and validated. Running the named live
gates on real outputs turns them from skipped placeholders into enforcers.

Purpose: D-01, D-03, D-07, D-10, D-13, D-24 (HLA exploratory).
Output: 480 production fits on /rs1 and committed status + sha256 manifests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/amendments/osf-amendment-r4-FINAL.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-osf-r4-amendment-and-gate-SUMMARY.md

<interfaces>
Fire: bash bin/r4_fire.sh production <ARM> <targets> --jobs 200   (targets from the R4 target functions in ta_r4_finemap.smk)
Arms: A3_1kg, A2_identity, A3_ukb, A3_ukb_isect, A3_1kg_isect (all EUR); HLA_6p21 is exploratory under A3_ukb only
Policy: config/susie_policy.yaml (production; max_iter 100/200, honoured since 02c4404, disclosed in the amendment)
Validators: python -m ta_r4.validate_r4_fits (runs inside every job); live gates in tests/ta_r4
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Gate check, code-state check, dry-run with expected counts</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - .planning/amendments/osf-amendment-r4-FINAL.md ("What is not changing": the locked commit and the analysis-code shas)
    - src/snakemake/rules/ta_r4_finemap.smk (target functions)
  </read_first>
  <action>
    1. `cd src/python && $PY -m ta_r4.r4_osf_gate --stage production`. Non-zero → STOP the plan
       and report.
    2. Code-state check: for each analysis-code and lock commit sha cited by the FINAL amendment,
       `git merge-base --is-ancestor <sha> HEAD`. Then run
       `git diff --stat <lock-commit-sha> HEAD -- src/snakemake/scripts/ta_r4 src/python/ta_r4 src/snakemake/rules/ta_r4_*.smk config/ta_r4 Snakefile.ta_r4 src/legacy/region_analysis/scripts/run_susie_rss.R src/snakemake/scripts/plink_ld_to_rds.R src/snakemake/scripts/run_qtl_coloc.R`.
       It must be empty. Any change to analysis code after the pre-registration is a STOP and a
       deviation to report to Carter.
    3. Dry-run each arm. Expected job counts: 95, 95, 100, 95, 95. Paste them.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_osf_gate --stage production && echo GATE_OPEN</automated>
  </verify>
  <acceptance_criteria>
    - `GATE_OPEN`; the `git diff --stat` output is empty (pasted); the dry-run counts are 95/95/100/95/95
  </acceptance_criteria>
  <done>Production is authorized, and the code is exactly what was pre-registered.</done>
</task>

<task type="auto">
  <name>Task 2: Fire the five EUR arms; monitor by output listing; manifest every artifact</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_EUR_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_EUR_status.tsv</files>
  <read_first>
    - memory feedback_lsf_queues, feedback_aou_fanout_gcs_listing_arbiter
    - config/ta_r4/cluster_lsf/config.yaml
  </read_first>
  <action>
    For each arm: `nohup bash bin/r4_fire.sh production <ARM> <targets> --jobs 200 > data/r4/logs/fire_<ARM>.log 2>&1 &`.
    Monitor by counting `data/r4/results/<ARM>/fine_mapping/susie/*.json`. When an arm ends,
    re-run its dry-run and confirm "Nothing to be done".
    - Any job that failed in the validator or the receipt md5 gate is a D-13 event. Record it by
      fit id with the violation names. Do NOT re-run it with weaker settings. A re-run is allowed
      only for infrastructure failures, and is recorded.
    - Write `fits_production_EUR_status.tsv`: arm, trait, region, status, n_CS, cs_sizes,
      convergence_status, ld_allele_exact, ld_allele_flipped, ld_allele_dropped_*,
      d3b_ld_z_consistency_s, exploratory flag.
    - Write `fits_production_EUR_sha256.tsv` covering every JSON, fit.rds and receipt.
    - Reconcile: status rows == 480; sha rows == 3 × the number of fits that produced all three
      files, plus early-exit JSON + receipt counts as defined by the early-exit contract. Show
      the arithmetic.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && for a in A3_1kg A2_identity A3_ukb A3_ukb_isect A3_1kg_isect; do echo $a $(ls data/r4/results/$a/fine_mapping/susie/*.json | wc -l); done</automated>
  </verify>
  <acceptance_criteria>
    - the counts print 95, 95, 100, 95, 95; `awk 'NR>1' fits_production_EUR_status.tsv | wc -l` prints 480
    - the per-arm status counts (ok / non_converged / too_many_variants / no_variants / other) are in the LOG and sum to the arm totals
  </acceptance_criteria>
  <done>All EUR production fits exist and are manifested.</done>
</task>

<task type="auto">
  <name>Task 3: Run the live gates on real outputs (no skips); wave-close (W5a)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - tests/ta_r4/test_no_silent_identity.py, tests/ta_r4/test_arm_variant_sets_identical.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    Run
    `$PY -m pytest tests/ta_r4/test_no_silent_identity.py tests/ta_r4/test_arm_variant_sets_identical.py -q -rs`.
    Both live gates must RUN and PASS. A skip now is a failure of this task. If the variant-set gate
    fails for any (trait, region), record the ids. That is a D-01 matched-design breach to report to
    Carter before W5b; do not proceed. Then run §C with label `W5a`, commit type `feat`, staging the
    two manifests.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_no_silent_identity.py tests/ta_r4/test_arm_variant_sets_identical.py -q -rs 2>&1 | tail -3</automated>
  </verify>
  <acceptance_criteria>
    - the output shows passed and `0 skipped` for the live gates
    - committed with explicit paths; pushed
  </acceptance_criteria>
  <done>The production fits are verified free of silent identity fallback, with matched variant sets.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| pre-registered code → executed code | any post-registration code change invalidates the pre-registration |
| frozen script exit 0 → valid fit | the script can exit 0 on identity fallback |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W5a-01 | Repudiation | post-registration code drift | mitigate | ancestry + empty `git diff --stat` vs the lock commit before firing |
| T-r4-W5a-02 | Tampering | silent identity fallback | mitigate | in-job validator + live gates with 0 skips |
| T-r4-W5a-03 | Tampering | selective re-runs | mitigate | re-runs only for infrastructure failures, recorded by id |
</threat_model>

<verification>
480 fits reconciled. Live gates passed with 0 skips. Code state equals the pre-registered state.
</verification>

<success_criteria>
The EUR fine-mapping substrate for the head-to-head exists exactly as pre-registered, with
machine-verified LD provenance.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5a-eur-production-fits-SUMMARY.md`
</output>
