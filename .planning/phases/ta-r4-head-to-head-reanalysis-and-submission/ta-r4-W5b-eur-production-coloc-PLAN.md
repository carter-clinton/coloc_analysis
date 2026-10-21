---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 16
slug: W5b-eur-production-coloc
type: execute
wave: 16
depends_on: ["W5a"]
files_modified:
  - src/python/ta_r4/coloc_coverage.py
  - tests/ta_r4/test_coloc_coverage.py
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
    - "Every admissible EUR manifest row (100 primary + 90 negative-control = 190) has, for each p12 key {p12_primary, p12_sensitivity}: one output per susie arm (A3_1kg, A2_identity, A3_ukb, A3_ukb_isect, A3_1kg_isect) and one A1_matched and one A1_allvars output; total 190 x 2 x 7 = 2660 JSONs (D-01, D-07, D-21)"
    - "Rows with 0 CS on either side carry method fallback_abf; no coloc_susie row has n_cs 0; priors in every JSON equal the locked yaml (live gates run with 0 skips) (D-02)"
    - "A coverage tool proves output ids == the expected (row x arm x p12) set exactly; any missing or extra id fails"
  artifacts:
    - path: "src/python/ta_r4/coloc_coverage.py"
      provides: "expected-vs-observed coverage over manifest x arm x p12"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_EUR_sha256.tsv"
      provides: "sha256 of all 2660 EUR coloc outputs"
  key_links:
    - from: "config/ta_r4/pair_manifest.tsv"
      to: "data/r4/results/*/coloc*/"
      via: "coloc_coverage.py expected set"
      pattern: "pair_manifest"
---

<objective>
Wave 5b runs the pre-registered EUR trait-pair colocalization for every arm and both prior
settings. Coverage is proven exactly, and the fallback and priors live gates run on real outputs.

Purpose: D-01, D-02, D-07, D-21; REQ-NEGATIVE-CONTROLS (NC rows present); REQ-PP.H4-THRESHOLD-SWEEP inputs.
Output: 2,660 coloc JSONs on /rs1, a coverage tool + test, and the sha256 manifest.
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
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Coverage tool (TDD)</name>
  <files>src/python/ta_r4/coloc_coverage.py, tests/ta_r4/test_coloc_coverage.py</files>
  <read_first>
    - config/ta_r4/pair_manifest.tsv; src/python/ta_r4/paths.py
  </read_first>
  <behavior>
    - expected_ids(manifest, ancestry="EUR", arms, p12_keys, a1_varsets) returns the set of output paths for admissible rows
    - check(expected, observed_dir_glob) returns (missing, extra). The CLI `python -m ta_r4.coloc_coverage --ancestry {EUR,AFR} --repo PATH` prints `missing=<n> extra=<n> expected=<n>` and exits 1 if missing or extra is non-zero. Arms come from ARMS filtered by ancestry plus A1_<ANC> (matched, allvars); p12 keys {p12_primary, p12_sensitivity}
    - Fixture: 3 rows × 2 arms × 2 keys → 12 expected; deleting one file gives missing == {that path}; an extra stray file is reported as extra
  </behavior>
  <action>Tests RED (paste), implement, GREEN. Negative control: run the check against a fixture dir with one file removed and observe exit 1.</action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_coloc_coverage.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the test passes; the SUMMARY shows RED and the negative control
  </acceptance_criteria>
  <done>Coverage can be proven exactly.</done>
</task>

<task type="auto">
  <name>Task 2: Gate re-check, fire EUR coloc for all arms and both p12 keys, prove coverage, run live gates; wave-close (W5b)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/coloc_production_EUR_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - src/snakemake/rules/ta_r4_coloc.smk
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    1. Re-run the gate check and the code-state `git diff --stat` check from W5a Task 1. STOP on
       either failure.
    2. Dry-run each arm. The expected counts are 190 × 2 = 380 per susie arm, and 760 for A1 (in
       the A3_1kg invocation). Fire, then monitor by listing.
    3. `$PY -m ta_r4.coloc_coverage --ancestry EUR ...` must report 0 missing and 0 extra over 2,660.
    4. Run `$PY -m pytest tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q -rs`.
       The live gates must run (0 skips) and pass.
    5. Write the sha256 manifest (2,660 rows). Record per-arm counts of method values
       (coloc_susie / fallback_abf / A1_*) in the LOG, reconciled to the totals. Note: these are
       counts only. No PP.H4 summaries are computed or logged before W7, to avoid informal peeking
       at estimands.
    6. Run §C with label `W5b`, commit type `feat`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q -rs 2>&1 | tail -3</automated>
  </verify>
  <acceptance_criteria>
    - coverage reports `missing=0 extra=0 expected=2660` (output pasted)
    - the live gates show 0 skipped and pass
    - `awk 'NR>1' coloc_production_EUR_sha256.tsv | wc -l` prints 2660; committed with explicit paths; pushed
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
| T-r4-W5b-01 | Tampering | missing or extra outputs | mitigate | exact coverage check over manifest × arm × p12 |
| T-r4-W5b-02 | Tampering | pooled fallback / default priors | mitigate | live gates with 0 skips |
| T-r4-W5b-03 | Repudiation | interim peeking | mitigate | only method counts are logged before W7; no PP.H4 summaries |
</threat_model>

<verification>
2,660 outputs with exact coverage. The fallback and priors gates passed on real data. The gate and code-state checks were re-run.
</verification>

<success_criteria>
The complete pre-registered EUR comparison set exists, verified, ready for the pre-registered aggregation.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5b-eur-production-coloc-SUMMARY.md`
</output>
