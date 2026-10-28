---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 19
slug: W5b-eur-production-coloc
type: execute
wave: 19
depends_on: ["ta-r4-W5a-eur-production-fits"]
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_EUR_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-NEGATIVE-CONTROLS
  - REQ-PP.H4-THRESHOLD-SWEEP

must_haves:
  truths:
    - "Every admissible EUR manifest row (100 primary + 190 negative-control = 290) has, for each p12 key {p12_primary, p12_sensitivity}: one output per susie arm (A3_1kg, A2_identity, A3_ukb, A3_ukb_isect, A3_1kg_isect) and one A1_matched and one A1_allvars output; total 290 x 2 x 7 = 4060 JSONs (D-01, D-07, D-21)"
    - "Rows with 0 CS on either side carry method fallback_abf; no coloc_susie row has n_cs 0; priors in every JSON equal the locked yaml (live gates run with 0 skips) (D-02)"
    - "The pre-lock coverage tool (W3d, unchanged since the lock) proves output ids == the expected (row x arm x p12) set exactly; the code-state diff against lock commit A is empty before the fire (B2)"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_EUR_sha256.tsv"
      provides: "sha256 of all 4060 EUR coloc outputs"
  key_links:
    - from: "config/ta_r4/pair_manifest.tsv"
      to: "data/r4/results/*/coloc/"
      via: "coloc_coverage.py expected set (W3d)"
      pattern: "coloc_coverage"
---

<objective>
Wave 5b runs the pre-registered EUR trait-pair colocalization for every arm and both prior
settings. Coverage is proven exactly with the pre-lock coverage tool, and the fallback and priors
live gates run on real outputs.

Purpose: D-01, D-02, D-07, D-21; REQ-NEGATIVE-CONTROLS (all three NC sets present); REQ-PP.H4-THRESHOLD-SWEEP inputs.
Output: 4,060 coloc JSONs on /rs1 and the sha256 manifest. No new code (B2).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5a-eur-production-fits-SUMMARY.md

<interfaces>
Rules (W0d): r4_coloc_pair -> data/r4/results/{ARM}/coloc/{row_id}.{p12key}.json;
  r4_coloc_A1 (ARM A3_1kg) -> data/r4/results/A1_EUR/coloc/{row_id}.{matched|allvars}.{p12key}.json
Fire: bash bin/r4_fire.sh production <ARM> <R4_COLOC_TARGETS(arm)>
Coverage (W3d): cd src/python && $PY -m ta_r4.coloc_coverage --ancestry EUR --repo ../..   (expected 4060)
Gate + code-state checks: W5a Task 1 steps 1-2 (lock commit A)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Gate + code-state re-check; fire EUR coloc for all arms and both p12 keys; prove coverage</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - the W5a PLAN Task 1 (gate + code-state check commands to repeat)
    - src/snakemake/rules/ta_r4_coloc.smk; src/python/ta_r4/coloc_coverage.py
  </read_first>
  <action>
    1. Re-run the lock gate check and the code-state `git diff --stat` against
       lock commit A from W5a Task 1. STOP on either failure.
    2. Dry-run each arm. The expected counts are 290 × 2 = 580 per susie arm, and 1,160 for A1
       (matched + allvars, in the A3_1kg invocation). Fire, then monitor by listing. Do not commit
       while a fire is in flight (§B.14).
    3. `cd src/python && $PY -m ta_r4.coloc_coverage --ancestry EUR --repo ../..` must report
       `missing=0 extra=0 expected=4060`. Arithmetic: 5 × 580 + 1,160 = 4,060.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.coloc_coverage --ancestry EUR --repo ../..</automated>
  </verify>
  <acceptance_criteria>
    - coverage prints `missing=0 extra=0 expected=4060` (output pasted); the dry-run counts are pasted
  </acceptance_criteria>
  <done>The full EUR comparison set exists with exact coverage.</done>
</task>

<task type="auto">
  <name>Task 2: Live gates on real outputs; sha256 manifest; method counts only; wave-close (W5b)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_EUR_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - tests/ta_r4/test_fallback_labelled.py, tests/ta_r4/test_priors_constant.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    1. Run `$PY -m pytest tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q -rs`.
       The live gates glob only `paths.result_dirs("coloc")` and must run (0 skips) and pass.
    2. Write the sha256 manifest (4,060 rows). Record per-arm counts of method values
       (coloc_susie / fallback_abf / A1_*) in the LOG, reconciled to the totals. These are counts
       only. No PP.H4 summaries are computed or logged before W7, to avoid informal peeking at
       estimands.
    3. Run §C with label `W5b`, commit type `feat`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q -rs 2>&1 | tail -3 && awk 'NR>1' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_EUR_sha256.tsv | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - the live gates show 0 skipped and pass
    - the manifest row count prints 4060; committed with explicit paths; pushed
  </acceptance_criteria>
  <done>EUR trait-pair colocalization is complete and verified for every arm and both prior settings.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| results on disk → estimands | an incomplete or mixed result set silently changes estimates |
| executor → results | informal peeking at PP.H4 before the pre-registered aggregation |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W5b-01 | Tampering | missing or extra outputs | mitigate | exact coverage check over manifest × arm × p12 with the pre-lock tool |
| T-r4-W5b-02 | Tampering | pooled fallback / default priors | mitigate | live gates with 0 skips over ARMS-derived dirs only |
| T-r4-W5b-03 | Repudiation | interim peeking | mitigate | only method counts are logged before W7; no PP.H4 summaries |
| T-r4-W5b-04 | Repudiation | post-lock code | mitigate | code-state diff against lock commit A is empty; no new code in this plan |
</threat_model>

<verification>
4,060 outputs with exact coverage. The fallback and priors gates passed on real data. The gate and code-state checks were re-run.
</verification>

<success_criteria>
The complete pre-registered EUR comparison set exists, verified, ready for the pre-registered aggregation.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5b-eur-production-coloc-SUMMARY.md`
</output>
