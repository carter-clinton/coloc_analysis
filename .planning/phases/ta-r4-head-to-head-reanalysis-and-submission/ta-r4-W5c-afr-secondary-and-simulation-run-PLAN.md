---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 20
slug: W5c-afr-secondary-and-simulation-run
type: execute
wave: 20
depends_on: ["ta-r4-W5b-eur-production-coloc"]
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_AFR_status.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_AFR_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_AFR_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sim_outputs_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SUSIE-RSS-POLICY

must_haves:
  truths:
    - "AFR secondary fits exist for asthma, stroke, t2d x the 10 AFR-admissible regions under AFR661_A3, AFR661_A2 (primary substrate, D-20) and AFR504_A3 (sensitivity): 90 fit JSONs, all validated (D-07, D-13, D-20)"
    - "AFR coloc covers the 30 admissible AFR rows x {AFR661_A3, AFR661_A2, AFR504_A3} x 2 p12 keys (180) plus A1_AFR matched/allvars x 2 p12 keys (120) = 300 outputs, coverage exact, live gates 0 skips"
    - "The E8 simulation ran all 100 pre-registered jobs (10 regions x 5 scenarios x 2 generation panels) at the locked simulation.yaml with reps = 200 (no override); every TSV row count == 200 x 3 arms, or the job recorded no_qualifying_pair with zero rows (D-23)"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sim_outputs_sha256.tsv"
      provides: "sha256 + row counts of all 100 simulation TSVs"
  key_links:
    - from: "config/ta_r4/simulation.yaml (locked)"
      to: "data/r4/results/sim/*.tsv"
      via: "r4_sim rule (gated)"
      pattern: "locked: true"
---

<objective>
Wave 5c runs the two pre-registered secondary analyses: the AFR arm on 1000G AFR (661 primary,
504 sensitivity) and the E8 known-truth simulation. Both are gated, coverage-checked and manifested.

Purpose: D-07, D-20, D-23, D-13.
Output: AFR fits and coloc outputs, the simulation TSVs, and manifests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5b-eur-production-coloc-SUMMARY.md

<interfaces>
Arms: AFR661_A3, AFR661_A2, AFR504_A3 (bin/r4_fire.sh production <ARM> ...); A1_AFR runs within the AFR661_A3 invocation
Sim: rule r4_sim, targets R4_SIM_TARGETS (active under ARM A3_1kg), outputs data/r4/results/sim/{region}.{scenario}.{gen}.tsv
Coverage: python -m ta_r4.coloc_coverage --ancestry AFR ...
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Gate + code-state re-check; AFR fits for three arms; live gates</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_AFR_status.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_production_AFR_sha256.tsv</files>
  <read_first>
    - the W5a PLAN Task 1 (the gate + code-state check commands to repeat)
    - data/r4/findings/afr_panel_size.tsv (regions expected to report too_many_variants)
  </read_first>
  <action>
    Repeat the lock gate check and the code-state diff against lock commit A
    (W5a Task 1 steps 1-2); STOP on failure. Do not commit while a fire is in flight (§B.14). Dry-run: 30 jobs per arm. Fire the
    three arms and monitor by listing. Write the status TSV (90 rows) and the sha256 manifest.
    Fits whose panel exceeded the variant cap are reported with their status, not dropped. Run
    `test_no_silent_identity.py` and `test_arm_variant_sets_identical.py` (the AFR661_A2 vs
    AFR661_A3 pair). Both must run with 0 skips and pass.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && for a in AFR661_A3 AFR661_A2 AFR504_A3; do echo $a $(ls data/r4/results/$a/fine_mapping/susie/*.json | wc -l); done</automated>
  </verify>
  <acceptance_criteria>
    - the counts print 30, 30, 30; the status TSV has 90 rows; the live gates show 0 skipped
  </acceptance_criteria>
  <done>AFR fits complete and validated.</done>
</task>

<task type="auto">
  <name>Task 2: AFR coloc (all arms, both p12 keys, A1 both variant sets) with exact coverage</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_AFR_sha256.tsv</files>
  <read_first>
    - src/snakemake/rules/ta_r4_coloc.smk; src/python/ta_r4/coloc_coverage.py
  </read_first>
  <action>
    Dry-run: 60 per susie arm; 120 for A1_AFR. Fire. Run the coverage check, which must report
    0 missing and 0 extra over 300. Run the fallback and priors live gates (0 skips). Write the
    sha256 manifest (300 rows) and log the method counts only (no PP.H4 summaries before W7).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.coloc_coverage --ancestry AFR --repo ../..</automated>
  </verify>
  <acceptance_criteria>
    - coverage prints `missing=0 extra=0 expected=300`; the live gates show 0 skipped; the manifest has 300 rows
  </acceptance_criteria>
  <done>AFR coloc complete with exact coverage.</done>
</task>

<task type="auto">
  <name>Task 3: Run the E8 simulation (100 gated jobs at the locked config); verify row counts</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sim_outputs_sha256.tsv</files>
  <read_first>
    - config/ta_r4/simulation.yaml (must show locked: true)
    - src/snakemake/rules/ta_r4_sim.smk
  </read_first>
  <action>
    Assert `simulation.yaml` has `locked: true` and no reps override anywhere in the rule's shell
    (`bash bin/r4_fire.sh production A3_1kg -n -p <one sim target>` printout shows no
    `--reps-override`). Fire `R4_SIM_TARGETS` (100 jobs, serial queue). Monitor by listing. Per
    TSV, count data rows. Each must be 600 (200 reps × 3 arms), or 0 with a `no_qualifying_pair`
    header note. Write `sim_outputs_sha256.tsv` (`file, rows, sha256, note`). Reconcile:
    sum of rows == 600 × (100 − n_no_qualifying). Log the n_no_qualifying list.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ls data/r4/results/sim/*.tsv | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - 100 TSVs; the per-file row counts satisfy the rule above (awk summary pasted); the reconciliation arithmetic is in the LOG
  </acceptance_criteria>
  <done>The known-truth calibration data exist exactly as pre-registered.</done>
</task>

<task type="auto">
  <name>Task 4: Wave-close (W5c)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W5c`, commit type `feat`, staging the four manifests.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git fsck --connectivity-only 2>&1 | tail -2 && git status --porcelain -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests</automated>
  </verify>
  <acceptance_criteria>
    - fsck clean; the manifests are committed (empty porcelain); pushed
  </acceptance_criteria>
  <done>W5c committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| locked config → simulation run | a smoke override leaking into production would change E8 |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W5c-01 | Tampering | reps override in production | mitigate | assert locked: true and the absence of `--reps-override` in the printed shell; row-count rule per file |
| T-r4-W5c-02 | Tampering | AFR silent identity | mitigate | in-job validator + live gates with 0 skips |
| T-r4-W5c-03 | Repudiation | interim peeking | mitigate | counts only; no PP.H4 summaries before W7 |
</threat_model>

<verification>
90 AFR fits, 300 AFR coloc outputs, 100 sim TSVs, all reconciled and gated.
</verification>

<success_criteria>
Both pre-registered secondary analyses are complete and verified.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5c-afr-secondary-and-simulation-run-SUMMARY.md`
</output>
