---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 5
slug: W0d-pair-coloc-r4-script
type: tdd
wave: 5
depends_on: ["ta-r4-W0c-receipts-validators-enforcers"]
files_modified:
  - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
  - src/snakemake/rules/ta_r4_coloc.smk
  - tests/ta_r4/fixtures/build_fixture_pair.R
  - tests/ta_r4/test_coloc_pair_r4.py
  - tests/ta_r4/test_fallback_labelled.py
  - tests/ta_r4/test_priors_constant.py
  - tests/ta_r4/fixtures/build_toy_workflow.py
  - tests/ta_r4/test_snakemake_toy_e2e.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "One R4 script produces every trait-pair outcome: A1_abf_matched (primary, D-21), A1_abf_allvars (secondary, D-21), coloc_susie, fallback_abf (D-02); method labels are mutually exclusive and never pooled"
    - "Whenever n_cs_a == 0 or n_cs_b == 0 the method is fallback_abf with fallback_reason, and its PP.H0..H4 equal A1_abf_matched exactly (identity check, Pitfall 8)"
    - "p1, p2, p12 come only from config/ta_r4/coloc_priors.yaml and are written into every output; coloc.abf and coloc.susie never run on their package defaults (Pitfall 5)"
    - "coloc_susie outputs equal a direct coloc::coloc.susie(fit_a, fit_b, p1, p2, p12) call on the same fixture fits, so the wrapper adds no numerics"
    - "Every output records variant_set_sha256 (sorted ids used), n_snps, overlap_min, trim_by_posterior, coloc and susieR versions"
    - "The fallback and priors live gates glob only paths.result_dirs('coloc') (production arms from ARMS + A1_EUR/A1_AFR), so W3b reproduction outputs (default priors, R2-era schema) are never read (B4)"
    - "A toy end-to-end run of `Snakefile.ta_r4 --use-conda` on 3 fixture regions (fits under A3_1kg and A2_identity, coloc_susie, A1 matched/allvars) completes with every validator passing (REQ-SNAKEMAKE-CI)"
  artifacts:
    - path: "src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R"
      provides: "A1 / coloc_susie / fallback_abf for one manifest row"
      min_lines: 120
    - path: "src/snakemake/rules/ta_r4_coloc.smk"
      provides: "rules r4_coloc_pair (susie arms) and r4_coloc_A1 (within the A3 invocations), gated"
    - path: "tests/ta_r4/test_fallback_labelled.py"
      provides: "named D-02 enforcer (unit + live gate)"
    - path: "tests/ta_r4/test_priors_constant.py"
      provides: "named priors enforcer (unit + live gate)"
    - path: "tests/ta_r4/test_snakemake_toy_e2e.py"
      provides: "REQ-SNAKEMAKE-CI toy 3-locus end-to-end run (r4_heavy)"
  key_links:
    - from: "run_coloc_pair_r4.R"
      to: "config/ta_r4/coloc_priors.yaml"
      via: "yaml::read_yaml; p12 key chosen by --p12-key"
      pattern: "coloc_priors.yaml"
    - from: "src/snakemake/rules/ta_r4_coloc.smk"
      to: "config/ta_r4/pair_manifest.tsv"
      via: "row_id wildcard over admissible rows"
      pattern: "pair_manifest.tsv"
---

<objective>
Wave 0d builds, test-first, the single colocalization script that every arm uses. This makes D-01's
"identical priors", D-02's labelled fallback and D-21's two A1 variant sets properties of one tested
code path, not conventions. Analysis code is frozen before the OSF post.

Purpose: D-01, D-02, D-21, Pitfalls 5 and 8.
Output: `run_coloc_pair_r4.R`, `ta_r4_coloc.smk`, three test modules. No real data.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0c-receipts-validators-enforcers-SUMMARY.md

<interfaces>
coloc 5.2.3 (verified in research): coloc.abf(dataset1, dataset2, MAF=NULL, p1=1e-4, p2=1e-4, p12=1e-5);
  coloc.susie(dataset1, dataset2, back_calculate_lbf=FALSE, susie.args=list(), ...) -> passes ... to coloc.bf_bf(bf1, bf2, p1=1e-4, p2=1e-4, p12=5e-6, overlap.min=0.5, trim_by_posterior=TRUE)
  coloc.abf dataset with beta/varbeta: list(beta, varbeta, snp, type="cc"|"quant", N, sdY (quant))
Existing name-alignment logic to replicate behaviourally (not source()): src/snakemake/scripts/run_coloc_susie.R lines 95-260
  (chr:pos rewrite when fits carry chr:pos vs rsid; no-signal emission when n_cs == 0)
Fit objects: <fit>.fit.rds written by run_susie_rss.R, already annotated (coloc:::annotate_susie applied before saveRDS)
From W0b1: config/ta_r4/coloc_priors.yaml {p1, p2, p12_primary, p12_sensitivity, overlap_min, trim_by_posterior, locked}
Trait manifest (W2a writes the real one): config/ta_r4/trait_manifest.tsv columns trait, ancestry, type (cc|quant), sdY (NA for cc), sdY_source, N_median
</interfaces>
</context>

<feature>
  <name>R4 trait-pair colocalization (A1 matched, A1 all-variants, coloc.susie, fallback_abf)</name>
  <files>src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R, tests/ta_r4/fixtures/build_fixture_pair.R, tests/ta_r4/test_coloc_pair_r4.py, tests/ta_r4/test_fallback_labelled.py, tests/ta_r4/test_priors_constant.py</files>
  <behavior>
    Cases (fixture: 2 traits on the W0c fixture region; trait A has 2 CS; trait B variants have 1 CS, or 0 CS for the "null" variant):
    - --mode susie, both traits have CS → method "coloc_susie"; summary rows equal direct coloc::coloc.susie(fa, fb, p1, p2, p12) to 1e-12; region stats: pp_h4_max, n_cs_pairs, n_cs_pairs_h4_ge_0.8, pp_h0..h4 of the max-PP.H4 row
    - --mode susie, trait B has 0 CS → method "fallback_abf", fallback_reason "n_cs_b==0"; PP.H0..H4 identical (==) to the --mode A1_matched output on the same row
    - --mode A1_matched → variant set = intersection of the two fits' retained variant ids; method "A1_abf_matched"
    - --mode A1_allvars → variant set = all region sumstats rows matched between the two traits on CHR:POS with an unordered {REF,ALT} equality (rows with missing alleles: CHR:POS only, counted as n_matched_pos_only); method "A1_abf_allvars"; n_snps >= the A1_matched n_snps
    - Priors: every output's priors == yaml values for the selected --p12-key. Negative control: coloc.abf with package defaults gives a different PP.H4 on the fixture (asserted !=), proving the explicit prior is load-bearing
    - quant trait with sdY from the trait manifest → dataset carries sdY; missing sdY for a quant trait → stop() (no silent estimation)
    - Live gates (marked r4_heavy; glob ONLY `*.json` under each dir of `ta_r4.paths.result_dirs("coloc")`; skip only while none of those dirs exists; then ≥1 file per existing dir required): no JSON has method coloc_susie with n_cs_a==0 or n_cs_b==0; every JSON's priors equal the yaml; per row_id, all arms' p12 values for a given p12_key are equal. A unit test asserts the gates' dir list equals `result_dirs("coloc")` and excludes every repro arm (B4). Negative control: a tmp results tree with a repro_sh2b3_r2 coloc JSON carrying default priors is NOT read by the gate
  </behavior>
  <implementation>
    `run_coloc_pair_r4.R` (optparse):
    `--mode {A1_matched,A1_allvars,susie}`, `--fit-a`, `--fit-b` (rds; required except A1_allvars),
    `--sumstats-a`, `--sumstats-b`, `--trait-a`, `--trait-b`, `--ancestry`, `--region-id`,
    `--regions-csv`, `--trait-manifest`, `--priors`, `--p12-key {p12_primary,p12_sensitivity}`,
    `--row-id`, `--arm`, `--output`.
    - Read the region bounds from `--regions-csv`. Read sumstats rows inside the bounds with the same reader the frozen script uses for bgzipped TSVs; check this and record it in the SUMMARY.
    - Name alignment: replicate run_coloc_susie.R:95-260 semantics as a local function `align_names()`. Add a differential test that, on fixtures carrying rsid names and chr:pos names, `align_names()` yields the same key sets as running `run_coloc_susie.R` itself on the same fits. No runtime `source()` of another script (memory feedback_freeze_economy_is_not_a_reason_to_take_risk).
    - The output JSON keys are exactly those in the must_haves, plus row_id, arm, mode, method, n_cs_a, n_cs_b, fallback_reason (null unless fallback) and an `R.version.string`.
    - `jsonlite::write_json(auto_unbox=TRUE, digits=NA)`.
    `ta_r4_coloc.smk`:
    - Rule `r4_coloc_pair`, for arms with fits. Output `data/r4/results/{ARM}/coloc/{row_id}.{p12key}.json`; inputs are the two fit `.rds` from `ta_r4.paths.fit_json`, the gate input, the priors and the trait manifest; mode `susie`.
    - Rule `r4_coloc_A1`, active only when ARM in {A3_1kg, AFR661_A3}. Output `data/r4/results/A1_{ANC}/coloc/{row_id}.{varset}.{p12key}.json`, with varset ∈ {matched, allvars}.
    - Admissible rows only, from `config/ta_r4/pair_manifest.tsv`, filtered by the arm's ancestry.
    - Target functions `R4_COLOC_TARGETS(arm)` are defined here for later waves.
    - Conda `envs/r_coloc.yml`.
    RED: write the three test modules first, run, paste the failures. GREEN: implement. REFACTOR only if needed.
  </implementation>
</feature>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED tests, then the coloc script (A1 matched / A1 allvars / susie / fallback) to GREEN</name>
  <files>tests/ta_r4/fixtures/build_fixture_pair.R, tests/ta_r4/test_coloc_pair_r4.py, tests/ta_r4/test_fallback_labelled.py, tests/ta_r4/test_priors_constant.py, src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R</files>
  <read_first>
    - src/snakemake/scripts/run_coloc_susie.R (whole file; esp. 95-260 and the no-signal branch at ~254)
    - tests/ta_r4/fixtures/build_fixture_region.R and tests/ta_r4/test_frozen_script_armed_e2e.py (W0c fixture + frozen-script fit helper to reuse)
    - config/ta_r4/coloc_priors.yaml
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pitfall 5", §"Pitfall 8", §"Code Examples"
  </read_first>
  <behavior>See the feature block above; every listed case is a test.</behavior>
  <action>
    Build the fixture fits by running the frozen `run_susie_rss.R`, through the W0c
    `commands.fit_command` helper, on two fixture traits. Tests that need these fixture fits are
    marked `r4_heavy` (they run the frozen script). That way the fits have the real annotated
    shape. Write the fixture trait manifest into `tmp_path`: trait A cc; trait B quant with
    sdY 1.0. Write all tests and run them RED (script absent); paste. Implement
    `run_coloc_pair_r4.R` per the feature block until GREEN. Then run the negative controls and
    paste each:
    - temporarily hard-code `p12 = 1e-5` in the script; observe `test_priors_constant` go RED; restore.
    - temporarily label fallbacks "coloc_susie"; observe `test_fallback_labelled` go RED; restore.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_coloc_pair_r4.py tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - all unit tests pass; exactly the live-gate tests skip, with reason text shown
    - the SUMMARY shows the initial RED and both sabotage REDs
    - the SUMMARY pastes the fixture's fallback PP.H4 and A1_matched PP.H4 (equal to all digits) and coloc_susie pp_h4_max vs the direct call (|diff| ≤ 1e-12)
  </acceptance_criteria>
  <done>One tested script yields every pair outcome with explicit priors and labelled fallbacks.</done>
</task>

<task type="auto">
  <name>Task 2: Snakemake coloc rules (gated), production dry-run refusal, and the toy end-to-end `--use-conda` run (REQ-SNAKEMAKE-CI)</name>
  <files>src/snakemake/rules/ta_r4_coloc.smk, tests/ta_r4/fixtures/build_toy_workflow.py, tests/ta_r4/test_snakemake_toy_e2e.py</files>
  <read_first>
    - Snakefile.ta_r4 and src/snakemake/rules/ta_r4_finemap.smk (W0b2/W0c)
    - src/python/ta_r4/paths.py, src/python/ta_r4/arms.py
    - tests/ta_r4/fixtures/make_fixture_repo.py, tests/ta_r4/fixtures/build_fixture_region.R (W0b2/W0c)
    - .planning/REQUIREMENTS.md §REQ-SNAKEMAKE-CI (toy 3-locus end-to-end)
  </read_first>
  <action>
    1. Write `src/snakemake/rules/ta_r4_coloc.smk` per the feature block. Both rules take
       `gate=gate_input`, so production arms refuse without the sentinel.
    2. Dry-run evidence:
       `bash bin/r4_fire.sh production A3_1kg -n data/r4/results/A3_1kg/coloc/SH2B3_12q24__EUR__bmi_vs_hypertension.p12_primary.json`
       must exit non-zero with `OsfGateError` (no sentinel). Panels and fits do not exist yet either.
       Record which error fires first. The gate is evaluated in the input function; if the panel
       resolver raises first, record it. The gate refusal is proven separately by
       `r4_gate_probe` (W0b2). Note that `bin/r4_fire.sh` runs `verify-online` first for production,
       so this refusal comes from the fire script's gate step; record its message.
    3. Toy end-to-end (REQ-SNAKEMAKE-CI; `tests/ta_r4/test_snakemake_toy_e2e.py`, marked `r4_heavy`):
       - `tests/ta_r4/fixtures/build_toy_workflow.py` takes a `make_fixture_repo(tmp_path)` repo and
         writes into it: 3 fixture regions FIX_1..FIX_3 (`build_fixture_region.R`, seeds
         20261021+k) as `config/ta_r4/regions_r4.csv`; a 3-row `pair_manifest.tsv` (one trait pair per
         region, ancestry EUR); a 2-row `trait_manifest.tsv`; fixture sumstats at the paths
         `ta_r4.paths.sumstats_path` returns; A3 panels at `data/r4/ld/EUR_1kg_r4/FIX_k.rds` and A2
         payloads via `make_matched_identity_payload.R`; panel manifests under the fixture's
         `$MAN`; catalogs; and a fixture amendment + sentinel committed in the fixture repo plus a
         receipt written in-process by `verify_online` with a fake fetch. These fixture gate files
         exist only under tmp_path (§B.12 applies to the real repo).
       - It runs `$SMK -s <fx>/Snakefile.ta_r4 -d <fx> --configfile <fx>/config/pipeline.yaml <fx>/config/ta_r4/overlay_base.yaml <fx>/config/ta_r4/overlay_A3_1kg.yaml --use-conda --conda-prefix /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4 --cores 2 <targets>`
         with `CONDARC` set as in `bin/r4_fire.sh`, then the same for `overlay_A2_identity.yaml`.
         Targets: 2 traits × 3 regions fits per arm; the 3 rows × {p12_primary, p12_sensitivity}
         coloc outputs per arm; and A1 matched + allvars in the A3_1kg invocation.
       - Asserts: exit 0; every target exists; every fit has a receipt and passed the in-job
         validator; coloc JSON methods are within {coloc_susie, fallback_abf, A1_abf_matched,
         A1_abf_allvars}; priors equal the fixture yaml. Negative control: deleting the A3 panel
         manifest row for FIX_2 makes the run fail at the receipt md5 gate (exit non-zero, named rule).
       Record the wall time in the SUMMARY.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_snakemake_toy_e2e.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - `bash bin/r4_fire.sh repro repro_routeC --list` lists `r4_coloc_pair`; the production dry-run above exits non-zero (stderr excerpt in the SUMMARY)
    - the toy e2e test RAN (no skip) and passed; its negative control failed as designed; wall time recorded
  </acceptance_criteria>
  <done>The coloc rules are wired behind the gate, and the full R4 workflow runs end to end with `--use-conda` on fixture data.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W0d)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W0d`, commit type `feat`. Stage exactly this plan's files_modified.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - QUICK and HEAVY green; tests/m3 unchanged against the baseline (join shown); pushed
  </acceptance_criteria>
  <done>W0d committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| package defaults → estimates | coloc.abf and coloc.susie defaults differ (p12 1e-5 vs 5e-6) |
| fallback rows → estimands | fallback values are LD-free and identical across arms by construction |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W0d-01 | Tampering | silent default priors | mitigate | priors only from yaml; recorded per output; live gate; sabotage RED observed |
| T-r4-W0d-02 | Repudiation | pooled fallback | mitigate | mutually exclusive method labels; live gate forbids coloc_susie with n_cs 0 |
| T-r4-W0d-03 | Tampering | silent sdY estimation | mitigate | stop() when a quant trait lacks a pre-registered sdY |
</threat_model>

<verification>
Unit tests and both sabotage REDs observed. The fallback ≡ A1_matched identity holds exactly.
The wrapper reproduces a direct coloc.susie call.
</verification>

<success_criteria>
Every trait-pair number in R4 comes from one tested script with explicit, recorded priors and
unpoolable method labels.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0d-pair-coloc-r4-script-SUMMARY.md`
</output>
