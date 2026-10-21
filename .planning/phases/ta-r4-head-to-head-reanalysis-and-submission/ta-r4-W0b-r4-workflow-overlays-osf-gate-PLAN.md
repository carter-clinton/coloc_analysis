---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 2
slug: W0b-r4-workflow-overlays-osf-gate
type: execute
wave: 2
depends_on: ["W0a"]
files_modified:
  - Snakefile.ta_r4
  - bin/r4_fire.sh
  - config/ta_r4/cluster_lsf/config.yaml
  - config/ta_r4/cluster_lsf/cluster_config.yaml
  - config/ta_r4/overlay_base.yaml
  - config/ta_r4/overlay_A3_1kg.yaml
  - config/ta_r4/overlay_A2_identity.yaml
  - config/ta_r4/overlay_A3_ukb.yaml
  - config/ta_r4/overlay_A3_ukb_isect.yaml
  - config/ta_r4/overlay_A3_1kg_isect.yaml
  - config/ta_r4/overlay_AFR661_A3.yaml
  - config/ta_r4/overlay_AFR661_A2.yaml
  - config/ta_r4/overlay_AFR504_A3.yaml
  - config/ta_r4/overlay_repro_routeC.yaml
  - config/ta_r4/overlay_repro_routeL.yaml
  - config/ta_r4/overlay_repro_k2d_routeC.yaml
  - config/ta_r4/overlay_repro_k2d_routeL.yaml
  - config/ta_r4/overlay_repro_sh2b3_r2.yaml
  - config/ta_r4/susie_policy_repro_iter100.yaml
  - config/ta_r4/coloc_priors.yaml
  - config/ta_r4/regions_r4.csv
  - config/ta_r4/pair_manifest.tsv
  - src/python/ta_r4/__init__.py
  - src/python/ta_r4/arms.py
  - src/python/ta_r4/paths.py
  - src/python/ta_r4/build_pair_manifest.py
  - src/python/ta_r4/r4_osf_gate.py
  - src/snakemake/rules/ta_r4_env.smk
  - tests/ta_r4/test_overlay_semantics.py
  - tests/ta_r4/test_pair_manifest.py
  - tests/ta_r4/test_osf_gate.py
  - tests/ta_r4/test_track_b_isolation.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_plink.yml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_qtl_processing.yml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_python_stats.yml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_named.yml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION
  - REQ-SUSIE-RSS-POLICY
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "The main Snakefile, config/pipeline.yaml and every pre-existing src/snakemake/rules/*.smk are unchanged by this plan; R4 runs from a standalone Snakefile.ta_r4 (D-15)"
    - "Each arm's stage (repro | production) comes from a hard-coded table in src/python/ta_r4/arms.py, not from config, so `--config` cannot relabel a production arm as repro"
    - "Merging overlay_base + overlay_<arm> onto config/pipeline.yaml makes ld_allele_aware(anc) == 'true' and ld_file_authoritative(anc) == 'true' for A2/A3/A3-UKB/AFR arms, replaces the ld_panel chain wholesale with exactly one R4 entry, and pins it; base config alone still gives EUR 'false' (D-14, D-15)"
    - "For every arm x manifest row, every path from ta_r4.paths lies under data/r4/ (except the read-only sumstats symlink) and contains none of EUR_ukbb_pub, EUR_ukbb_ld, EUR_aou, AFR_aou, data/processed/ld_reference/, sumstats_harmonized_occl (D-04, D-15)"
    - "config/ta_r4/pair_manifest.tsv has 246 rows = 12 x 10 EUR + 12 x 3 AFR + 9 x 10 EUR negative-control; 220 admissible; HLA_6p21 and BMI_Xq24 rows carry admissible=false with a reason (D-07, D-24)"
    - "Without a git-tracked, committed sentinel whose amendment sha256 matches the OSF API record, `snakemake -n` on any production target exits non-zero with OsfGateError; repro targets are not gated (D-05, D-27)"
    - "Snakemake job envs (plink, qtl_processing, python_stats) are solved into /rs1/.../smk_job_envs/ta_r4 with CONDARC-isolated pkgs and their lockfiles are committed (REQ-SNAKEMAKE-CI)"
  artifacts:
    - path: "Snakefile.ta_r4"
      provides: "standalone R4 workflow entry; requires ta_r4.arm; includes ta_r4*.smk"
    - path: "src/python/ta_r4/arms.py"
      provides: "ARMS table: arm -> {stage, ancestry, panel_source, panel_template, policy, validator_mode, route}"
      exports: ["ARMS", "arm_stage"]
    - path: "src/python/ta_r4/paths.py"
      provides: "single source for every R4 input/output path"
    - path: "src/python/ta_r4/r4_osf_gate.py"
      provides: "check_osf_gate(repo_root, stage, fetch=..., now=...) raising OsfGateError"
      exports: ["check_osf_gate", "OsfGateError", "SENTINEL_REL"]
    - path: "config/ta_r4/pair_manifest.tsv"
      provides: "pre-registered static all-pairs manifest (no tier gate)"
      contains: "admissible"
    - path: "bin/r4_fire.sh"
      provides: "the only supported way to run Snakefile.ta_r4"
  key_links:
    - from: "Snakefile.ta_r4 production rules"
      to: "src/python/ta_r4/r4_osf_gate.py::check_osf_gate"
      via: "input function evaluated at DAG time"
      pattern: "check_osf_gate"
    - from: "bin/r4_fire.sh"
      to: "config/ta_r4/overlay_<arm>.yaml"
      via: "--configfile config/pipeline.yaml config/ta_r4/overlay_base.yaml config/ta_r4/overlay_$ARM.yaml"
      pattern: "overlay_base.yaml"
---

<objective>
Wave 0b builds the R4 workflow skeleton and puts every arm's configuration and every
path in one place. It pre-registers the static all-pairs manifest and implements the OSF sentinel
gate in code. All of it ships behind RED-first tests, including the dry-run Track B isolation and
gate negative controls.

Purpose: D-01/D-07/D-24 (arms + manifest), D-14 (overlays; the identity overlay does not depend on
the real panel), D-04/D-15 (isolation), D-05/D-27 (gate), REQ-SNAKEMAKE-CI (pinned envs).
Output: `Snakefile.ta_r4`, `bin/r4_fire.sh`, overlays, policies, priors, regions, manifest, the
`src/python/ta_r4` package, four test modules and the env lockfiles. No fits.

Design choice (Claude's discretion, D-14 "overlay design"): a **standalone** `Snakefile.ta_r4`
instead of an `include:` inside the main `Snakefile`. The base DAG then cannot change by
construction, and no R4 output pattern can collide with `finemap.smk::run_finemap`'s
`finemap_output()` pattern (an AmbiguousRuleException risk). The overlays still go through
`snakemake.utils.update_config` on top of `config/pipeline.yaml`, exactly as the research's
Pattern 2 verified, so the shipped `ld_read_path` / `ld_panel` helper semantics are what arm the
frozen script.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-CONTEXT.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0a-storage-envs-survivors-SUMMARY.md

<interfaces>
From src/python/ld_read_path.py (shipped; do not edit):
  ld_read_path_applies(ancestry, config) -> bool
  ld_matrix_region_id(region, ancestry, config, curated_to_m2, region_safe_to_id) -> str   # applies CURATED_TO_M2 crosswalk on the allow-list
  ld_file_authoritative(ancestry, config) -> "true" | "false"
  ld_allele_aware(ancestry, config) -> "true" | "false"
  ld_coloc_applies(ancestry, config) -> bool
From src/python/ld_panel.py (shipped; do not edit):
  resolve_ld_path(region_id, ancestry, config, region_safe) -> Path
    pin > strict_aou_only > walk; ValueError if pin not in chain; FileNotFoundError if pinned file missing (DAG time)
config/pipeline.yaml (do not edit): ld_panel.EUR chain head EUR_ukbb_pub; ld_read_path {ancestries: [AFR], allele_aware: true};
  occlusion_lockstep {ancestries: [AFR]}; finemap.ld_reference_dir data/processed/ld_reference; paths.results_root results
snakemake.utils.update_config (7.32.4): dicts merge recursively, LISTS REPLACE WHOLESALE (verified in research).
The frozen fit invocation to mirror (finemap.smk:441-455):
  Rscript src/legacy/region_analysis/scripts/run_susie_rss.R --sumstats S --trait T --ancestry A --method susie
    --region REGION_ID --regions-csv CSV --ld-dir DIR --ld-file DECLARED --ld-authoritative true|false
    --ld-allele-aware true|false --variant-list CATALOG --credible-set 0.95 --policy POLICY --output JSON
  with `export SUSIE_MAX_VARIANTS=16000`.
Legacy script (3dd76df) options: --sumstats --trait --ancestry --method --region --regions-csv --ld-dir
  --variant-list --credible-set --policy --output   (NO --ld-file / --ld-authoritative / --ld-allele-aware)
regions_curated.csv schema: region_id,ancestry,chr,start,end,lead_snp,gene,trait_list,source,canonical_pairs (12 rows)
config/negative_controls.yaml: cosmetic (OCA2/HERC2 15:28000000-28500000, SLC24A5 15:48000000-48500000,
  MC1R 16:89900000-90100000, TYR 11:88500000-89000000, IRF4 6:396000-500000) and blood_group
  (ABO 9:136125000-136155000, RH 1:25580000-25750000, FUT1/FUT2 19:49200000-49260000, KEL 7:142630000-142720000), GRCh37
OSF public API: GET https://api.osf.io/v2/files/<guid>/ -> data.attributes.extra.hashes.{sha256,md5},
  data.attributes.date_created; the containing node is in data.relationships.target (check the live schema on file k8w7n, az52u)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Arms table, path module, overlays and policies — RED-first overlay semantics tests</name>
  <files>src/python/ta_r4/__init__.py, src/python/ta_r4/arms.py, src/python/ta_r4/paths.py, config/ta_r4/overlay_base.yaml, config/ta_r4/overlay_A3_1kg.yaml, config/ta_r4/overlay_A2_identity.yaml, config/ta_r4/overlay_A3_ukb.yaml, config/ta_r4/overlay_A3_ukb_isect.yaml, config/ta_r4/overlay_A3_1kg_isect.yaml, config/ta_r4/overlay_AFR661_A3.yaml, config/ta_r4/overlay_AFR661_A2.yaml, config/ta_r4/overlay_AFR504_A3.yaml, config/ta_r4/overlay_repro_routeC.yaml, config/ta_r4/overlay_repro_routeL.yaml, config/ta_r4/overlay_repro_k2d_routeC.yaml, config/ta_r4/overlay_repro_k2d_routeL.yaml, config/ta_r4/overlay_repro_sh2b3_r2.yaml, config/ta_r4/susie_policy_repro_iter100.yaml, config/ta_r4/coloc_priors.yaml, tests/ta_r4/test_overlay_semantics.py</files>
  <read_first>
    - src/python/ld_read_path.py (whole file) and src/python/ld_panel.py lines 53-130
    - config/pipeline.yaml lines 180-400 (finemap, ld_panel, occlusion_lockstep, ld_read_path blocks)
    - config/pipeline_identity_overlay.yaml (the k2d overlay being superseded for A2)
    - config/susie_policy.yaml and config/susie_policy_L15.yaml (record their max_iter values in the SUMMARY)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 2", §"Pattern 3", §"Pattern 4", §"Code Examples"
  </read_first>
  <behavior>
    - For arm in {A3_1kg, A2_identity, A3_ukb, A3_ukb_isect, A3_1kg_isect}: merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml") gives ld_allele_aware("EUR",c)=="true", ld_file_authoritative("EUR",c)=="true", [e["source"] for e in c["ld_panel"]["EUR"]] == [ARMS[arm]["panel_source"]], c["ld_panel"]["pin"]["EUR"] == ARMS[arm]["panel_source"], and "EUR_ukbb_pub" not in yaml.safe_dump(c["ld_panel"]["EUR"])
    - For arm in {AFR661_A3, AFR661_A2, AFR504_A3}: the same with "AFR", plus c["occlusion_lockstep"]["enabled"] is False, so no AFR_aou entry remains in c["ld_panel"]["AFR"]
    - For the repro arms: ld_file_authoritative("EUR",c)=="false", ld_allele_aware("EUR",c)=="false" and ld_read_path ancestries == []
    - test_base_config_untouched (negative control): merged_config() with no overlays gives ld_allele_aware("EUR")=="false" and ld_read_path ancestries == ["AFR"], and the EUR chain head is "EUR_ukbb_pub"
    - test_identity_overlay_independent_of_real_panel: the A2_identity chain has one entry, whose path template contains "EUR_identity_r4" and no other panel dir
    - test_r4_paths_independent_of_crosswalk: for every region in config/ta_r4/regions_r4.csv (curated + NC), resolve_ld_path(region_id=region_safe, ancestry, merged config, region_safe=region_safe) on a tmp tree containing the expected file returns data/r4/ld/<panel_dir>/<region_safe>.rds. The R4 rules never call ld_matrix_region_id; NC ids are absent from the curated→M2 crosswalk
    - test_stage_is_code_not_config: arm_stage("A3_1kg") == "production" even after update_config(c, {"ta_r4": {"stage": "repro"}})
    - test_priors_single_source: coloc_priors.yaml has p1 == p2 == 1e-4, p12_primary == 5e-6, p12_sensitivity == 1e-5, and locked: false (W4 flips it)
  </behavior>
  <action>
    1. `src/python/ta_r4/arms.py` defines the `ARMS: dict[str, dict]` literal. Keys per arm: `stage`,
       `ancestry`, `panel_source`, `panel_dir` (under `data/r4/ld/`), `route` (`r4` | `legacy`),
       `policy` (repo-relative), `validator_mode` (`real_ld` | `identity_matched` | `legacy_any`)
       and `variant_catalog`. Rows:
       - A3_1kg: production, EUR, EUR_1kg_r4, EUR_1kg_r4, r4, config/susie_policy.yaml, real_ld.
       - A2_identity: production, EUR, EUR_identity_r4, EUR_identity_r4, r4, config/susie_policy.yaml, identity_matched.
       - A3_ukb: production, EUR, EUR_ukb337k_r4, EUR_ukb337k_r4, r4, config/susie_policy.yaml, real_ld.
       - A3_ukb_isect: production, EUR, EUR_ukb337k_isect_r4, EUR_ukb337k_isect_r4, r4, config/susie_policy.yaml, real_ld.
       - A3_1kg_isect: production, EUR, EUR_1kg_isect_r4, EUR_1kg_isect_r4, r4, config/susie_policy.yaml, real_ld. (E6 intersection-matched pair with A3_ukb_isect: both panels are restricted to the variants present in both.)
       - AFR661_A3: production, AFR, AFR661_1kg_r4, AFR661_1kg_r4, r4, config/susie_policy.yaml, real_ld.
       - AFR661_A2: production, AFR, AFR661_identity_r4, AFR661_identity_r4, r4, config/susie_policy.yaml, identity_matched.
       - AFR504_A3: production, AFR, AFR504_1kg_r4, AFR504_1kg_r4, r4, config/susie_policy.yaml, real_ld.
       - repro_routeC: repro, EUR+AFR, legacy, legacy_repro, legacy semantics on current code, config/ta_r4/susie_policy_repro_iter100.yaml, legacy_any.
       - repro_routeL: repro, legacy_repro, route legacy (script `data/r4/legacy_code/run_susie_rss_3dd76df.R`), config/susie_policy.yaml (the legacy code's max_iterations bug reproduces the effective 100), legacy_any.
       - repro_k2d_routeC / repro_k2d_routeL: repro, k2d_identity panel dir, the same policies as their real-LD twins, legacy_any.
       - repro_sh2b3_r2: repro, legacy_repro panel, policy config/susie_policy_L15.yaml for bmi/hypertension/stroke. asthma/t2d reuse the routeC L10 fits (wired in W3b), legacy_any.
       Export `arm_stage(arm) -> str`, which reads `ARMS` only.
       `src/python/ta_r4/paths.py` holds the pure functions every path comes from:
       - `panel_path(arm, region_safe)`
       - `fit_json(arm, trait, anc, region_safe)` = `data/r4/results/{arm}/fine_mapping/susie/{trait}.{anc}.{region_safe}.json`, plus `.fit.rds` and `.ld_receipt.json` siblings
       - `sumstats_path(trait, anc, arm)`: bmi.EUR on an r4 route → `data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz` (D-18); everything else → `data/processed/sumstats_harmonized/{trait}.{anc}.tsv.bgz`
       - `catalog_path(route, region_safe)`
       - `coloc_json(arm_or_A1, row_id)`, `ld_dir_unused()` = `data/r4/ld_dir_unused` (MUST NOT exist)
       - `regions_csv()` = `config/ta_r4/regions_r4.csv`
    2. Overlays.
       - `overlay_base.yaml`: `ta_r4: {enabled: true}`, `enable_ld_pipeline: false`,
         `occlusion_lockstep: {enabled: false}`,
         `ld_read_path: {enabled: true, ancestries: [EUR, AFR], allele_aware: true, coloc: true}`.
       - Each production arm overlay: `ta_r4: {arm: <ARM>}`, `ld_panel: {<ANC>: [{source: <panel_source>, path: "data/r4/ld/<panel_dir>/{region_safe}.rds"}], pin: {<ANC>: <panel_source>}}`.
       - Repro overlays: `ld_read_path: {ancestries: []}` plus a chain for the legacy panel dir.
       Every overlay has a 3-line header comment naming its arm and how to run it via `bin/r4_fire.sh`.
    3. `susie_policy_repro_iter100.yaml` is a copy of `config/susie_policy.yaml` with only
       `max_iter_retry: 100` changed. Assert this in the SUMMARY with
       `diff config/susie_policy.yaml config/ta_r4/susie_policy_repro_iter100.yaml` showing exactly
       that one line.
       `coloc_priors.yaml`: `p1: 1.0e-4`, `p2: 1.0e-4`, `p12_primary: 5.0e-6`,
       `p12_sensitivity: 1.0e-5`, `overlap_min: 0.5`, `trim_by_posterior: true`,
       `locked: false`, `citation_check: "verify Wallace 2020 p12 recommendation before W4"`.
    4. Write `tests/ta_r4/test_overlay_semantics.py` with the behaviours above. Run it RED: modules
       and overlays are absent, so imports fail. Paste the output. Implement until GREEN. For the
       negative control: temporarily delete `pin:` from `overlay_A3_1kg.yaml`, observe the
       pin-assertion test go RED, restore it, and record both outputs.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_overlay_semantics.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/ta_r4/test_overlay_semantics.py -q` passes. The SUMMARY shows the initial RED (ImportError or collection error) and the pin-removal RED
    - `$PY -c "import sys;sys.path.insert(0,'src/python');from ta_r4.arms import ARMS;print(sorted(ARMS))"` prints the 13 arm names (8 production + 5 repro)
    - `git diff --quiet HEAD -- config/pipeline.yaml Snakefile src/snakemake/rules/finemap.smk src/legacy/region_analysis/scripts/run_susie_rss.R; echo $?` prints 0
  </acceptance_criteria>
  <done>Arm semantics are pinned by tests; stage is code-owned; the base config is unchanged.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Regions file and the pre-registered all-pairs manifest</name>
  <files>config/ta_r4/regions_r4.csv, src/python/ta_r4/build_pair_manifest.py, config/ta_r4/pair_manifest.tsv, tests/ta_r4/test_pair_manifest.py</files>
  <read_first>
    - config/regions_curated.csv (12 rows; note `BMI_5q13.3` → safe id `BMI_5q13_3` per Snakefile:51 `replace(".", "_").replace("/", "_")`)
    - config/negative_controls.yaml
    - src/python/create_coloc_manifest.py and the filter at src/python/filter_finemap_summary.py:374 (the tier gate R4 must NOT use)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 5", §"Pitfall 15"
  </read_first>
  <behavior>
    - The manifest has exactly 246 data rows; by row_class: primary EUR 120, primary AFR 36, negative_control 90
    - admissible == "true" for exactly 220 rows; every admissible == "false" row has region_id in {HLA_6p21, BMI_Xq24} and a non-empty inadmissible_reason
    - Every unordered EUR trait pair appears exactly once per EUR region (10 per region); trait_a < trait_b lexicographically
    - The AFR rows use only {asthma, stroke, t2d}
    - row_id is unique and equals f"{region_safe}__{ancestry}__{trait_a}_vs_{trait_b}"
    - No column depends on any fit outcome (no status/tier column). Negative control: a manifest containing a "status" column fails the schema test
    - The builder is deterministic: running it twice gives byte-identical output (sha256 equal)
    - ABO rows carry nc_caveat == "reported_stroke_association_verify" (research A5) and do not use the stroke pairs as negative-control evidence by default
  </behavior>
  <action>
    1. `config/ta_r4/regions_r4.csv`: the same columns as `config/regions_curated.csv`. The 12
       curated rows are copied verbatim, then 9 negative-control rows are added with `ancestry=EUR`,
       GRCh37 coordinates from `config/negative_controls.yaml`, `source=negative_control`, an empty
       `canonical_pairs`, and region_ids `NC_OCA2_HERC2, NC_SLC24A5, NC_MC1R, NC_TYR, NC_IRF4,
       NC_ABO, NC_RH, NC_FUT1_FUT2, NC_KEL`. The frozen `run_susie_rss.R` takes its region
       coordinates from `--regions-csv`. Read how it looks a region up (by region_id only, or by
       region_id + ancestry) and record the answer in the SUMMARY. If it filters on ancestry, add
       AFR duplicates of the 12 curated rows.
    2. `src/python/ta_r4/build_pair_manifest.py` (argparse: `--regions`, `--out`). It writes the TSV
       with columns `row_id, ancestry, region_id, region_safe, trait_a, trait_b, row_class,
       admissible, inadmissible_reason, canonical_pair, nc_set, nc_caveat`. Rules:
       - EUR primary: the 12 curated regions × C(5,2) = 10 pairs.
       - AFR primary: the 12 curated regions × C(3,2) = 3 pairs.
       - Negative control: the 9 NC regions × 10 EUR pairs; `nc_set` is `cosmetic` or `blood_group`.
       - `admissible = false` for HLA_6p21 (`reason: "D-24: no admissible panel (69k HM3 variants > 16000 cap); UKB exploratory row only"`) and BMI_Xq24 (`reason: "D-24: chrX absent from LDSC 1000G and UKB LD"`).
       - `canonical_pair` is true when `f"{trait_a}_vs_{trait_b}"` is in the region's `canonical_pairs`.
       - Sort by `(row_class, ancestry, region_safe, trait_a, trait_b)` and write with `\n` line endings.
    3. Write `tests/ta_r4/test_pair_manifest.py` (the behaviours above), RED first. Then generate
       `config/ta_r4/pair_manifest.tsv` with
       `$PY src/python/ta_r4/build_pair_manifest.py --regions config/ta_r4/regions_r4.csv --out config/ta_r4/pair_manifest.tsv`.
       The test regenerates into `tmp_path` and asserts sha256 equality with the committed file, so
       the committed manifest is exactly the builder's output.
    4. The arithmetic goes in the SUMMARY: 120 + 36 + 90 = 246; inadmissible 2×10 + 2×3 = 26;
       246 − 26 = 220.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_pair_manifest.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `awk 'NR>1' config/ta_r4/pair_manifest.tsv | wc -l` prints 246, and `awk -F'\t' 'NR>1 && $8=="true"' config/ta_r4/pair_manifest.tsv | wc -l` prints 220 (column index confirmed against the header in the SUMMARY)
    - the pytest file passes; the SUMMARY shows its RED run and the "status column" negative control failing the schema check
  </acceptance_criteria>
  <done>A static, deterministic, outcome-independent manifest is committed and pinned by its builder.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: OSF sentinel gate, Snakefile.ta_r4 skeleton, fire script, LSF profile, env solves — RED-first gate and isolation tests</name>
  <files>src/python/ta_r4/r4_osf_gate.py, Snakefile.ta_r4, src/snakemake/rules/ta_r4_env.smk, bin/r4_fire.sh, config/ta_r4/cluster_lsf/config.yaml, config/ta_r4/cluster_lsf/cluster_config.yaml, tests/ta_r4/test_osf_gate.py, tests/ta_r4/test_track_b_isolation.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_plink.yml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_qtl_processing.yml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_python_stats.yml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_named.yml</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 7", §"Pitfall 11", §"Pitfall 14"
    - memory feedback_gsd_automode_bypasses_blocking_fire_gates (why the gate is code)
    - config/cluster_lsf/config.yaml, config/cluster_lsf/cluster_config.yaml, config/bsub_wrapper.sh
    - Snakefile lines 1-63 (region parsing to mirror for regions_r4.csv)
    - envs/plink.yml, envs/python_stats.yml, envs/r_coloc.yml
  </read_first>
  <behavior>
    - check_osf_gate(repo, "repro") returns None, even with no sentinel
    - check_osf_gate(repo, "production") raises OsfGateError naming the specific reason for each of these cases:
      (a) sentinel absent;
      (b) sentinel present but untracked (git ls-files --error-unmatch fails);
      (c) sentinel tracked but has uncommitted changes;
      (d) missing key among {osf_url, osf_file_guid, posted_utc, amendment_path, amendment_sha256, head_sha};
      (e) amendment_path untracked or its sha256 != amendment_sha256;
      (f) posted_utc in the future or unparseable;
      (g) head_sha not an ancestor of HEAD;
      (h) fetch(guid) returns sha256 != amendment_sha256;
      (i) fetch raises (network down): fail closed;
      (j) the API's target node id != "az52u"
    - Positive control: a tmp git repo with a committed amendment + sentinel and a fake fetch returning the matching sha256 and node az52u → returns None
    - There is NO env var, config key or CLI flag that bypasses the production check. test_no_bypass scans r4_osf_gate's AST for os.environ / os.getenv reads and asserts none
    - Dry-run: `$SMK -s Snakefile.ta_r4 -n --configfile config/pipeline.yaml config/ta_r4/overlay_base.yaml config/ta_r4/overlay_A3_1kg.yaml r4_gate_probe` exits non-zero, and stderr contains "OsfGateError" (the real repo has no sentinel). The same with overlay_repro_routeC and target r4_gate_probe_repro exits 0
    - Isolation: for every arm in ARMS and every manifest row, every path returned by ta_r4.paths lies under data/r4/ or data/processed/sumstats_harmonized/ and contains none of the forbidden substrings. Negative control: a monkeypatched panel_path returning "data/processed/ld_reference/EUR_ukbb_pub/x.rds" is reported
    - Isolation: `$SMK -s Snakefile.ta_r4 -n` for repro_routeC on target r4_env_probe_all lists no forbidden substring in `--printshellcmds` output
  </behavior>
  <action>
    1. `src/python/ta_r4/r4_osf_gate.py`:
       - `SENTINEL_REL = ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json"`
       - `class OsfGateError(RuntimeError)`
       - `def check_osf_gate(repo_root: Path, stage: str, *, fetch=fetch_osf_file, now=None) -> None`, implementing the 10 checks in the order listed. git calls go through `subprocess.run([...], cwd=repo_root, capture_output=True)`, never `shell=True`.
       - `fetch_osf_file(guid)`: `urllib.request` GET of `https://api.osf.io/v2/files/{guid}/` with a 30 s timeout. It returns `{"sha256", "md5", "date_created", "target_node"}`. Confirm the JSON path to the target node against the live record for GUID `k8w7n` (M1 amendment file on az52u) and paste the parsed dict in the SUMMARY. That is the live known answer for the parser.
       - `main()` with `--stage` exits 1 and prints the reason on OsfGateError.
       It reads NO environment variables.
    2. `Snakefile.ta_r4`:
       - `configfile: "config/pipeline.yaml"`. Require `config["ta_r4"]["enabled"] is True` and `config["ta_r4"]["arm"] in ARMS`, else raise `WorkflowError("run via bin/r4_fire.sh")`.
       - `sys.path.insert(0, "src/python")`.
       - Import `ta_r4.arms` and `ta_r4.paths`. Parse `config/ta_r4/regions_r4.csv` into REGION_INFOS / REGION_SAFE_TO_ID / REGION_METADATA with the Snakefile:51-61 rule.
       - Load `config/ta_r4/pair_manifest.tsv`.
       - Define `def gate_input(wildcards): check_osf_gate(Path(workflow.basedir), arm_stage(ARM)); return SENTINEL_OR_EMPTY`. For production it returns the sentinel path, so the sentinel is a declared input. For repro it returns `[]`.
       - Rules `r4_gate_probe` (production gate exercise, touches `data/r4/tmp/gate_probe_{ARM}.ok`; input `gate_input`) and `r4_gate_probe_repro`.
       - Include every `src/snakemake/rules/ta_r4_*.smk` in sorted filename order (`for _smk in sorted(glob.glob("src/snakemake/rules/ta_r4_*.smk")): include: _smk`). Later plans then only add files (`ta_r4_panels.smk`, `ta_r4_panels_afr_ukb.smk`, `ta_r4_finemap.smk`, `ta_r4_coloc.smk`, `ta_r4_qtl.smk`, `ta_r4_sim.smk`, `ta_r4_repro.smk`) and never edit `Snakefile.ta_r4`. This plan ships `ta_r4_env.smk` only. Rule names must be unique across these files.
       - `ta_r4_env.smk` defines `r4_env_probe_{plink,qtl_processing,python_stats}`. Each uses `conda: str(Path(workflow.basedir)/"envs"/"<name>.yml")` and writes the tool version (`plink --version`, `python -c "import pandas,pysam;print(...)"`, etc.) to `data/r4/logs/env_probe/<name>.txt`. A rule `r4_env_probe_all` collects them.
    3. `bin/r4_fire.sh STAGE ARM [snakemake args...]`, with `set -euo pipefail`:
       - Refuse unless `ARMS[ARM].stage == STAGE`, checked via `$PY -c`.
       - `export CONDARC=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/condarc`.
       - Run `bash bin/r4_link_storage.sh`.
       - `exec $SMK -s Snakefile.ta_r4 --configfile config/pipeline.yaml config/ta_r4/overlay_base.yaml config/ta_r4/overlay_${ARM}.yaml --use-conda --conda-prefix /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4 --profile config/ta_r4/cluster_lsf "$@"`.
       The /rs1 literals live in `bin/`, which is outside the REQ-PATH scan.
    4. `config/ta_r4/cluster_lsf/config.yaml` is a copy of `config/cluster_lsf/config.yaml` with logs
       at `-o data/r4/logs/lsf/%J.{rule}.out -e data/r4/logs/lsf/%J.{rule}.err` and `jobs: 200`.
       `cluster_config.yaml` sets `__default__: {queue: serial, mem_mb: 8000, threads: 1}`.
       Panel/fit rules with mem ≥ 16000 stay on serial (1 slot); never `standard` with < 8 threads.
    5. Tests: write `test_osf_gate.py` and `test_track_b_isolation.py` RED first. The dry-run tests
       call `$SMK` through subprocess with `cwd=REPO_ROOT` and the repo's real config. Implement
       until GREEN.
    6. Solve the envs: `bash bin/r4_fire.sh repro repro_routeC r4_env_probe_all --conda-create-envs-only --cores 1`,
       then `bash bin/r4_fire.sh repro repro_routeC r4_env_probe_all --cores 1 --profile ''`. The
       second command runs locally; if `--profile ''` is rejected, pass `--cluster ''` per the
       Snakemake 7 CLI and record what worked.
       For each env dir listed by `$SMK -s Snakefile.ta_r4 ... --list-conda-envs`, run
       `conda env export --no-builds -p <dir> > $MAN/env_lock_<name>.yml`. Also export the named env:
       `conda env export --no-builds -p /rs1/researchers/c/ckclinto/conda_envs/r_coloc > $MAN/env_lock_r_coloc_named.yml`.
       Confirm `ls /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/pkgs | wc -l` > 0. Also
       confirm the shared cache's archive count is unchanged: count before and after with
       `ls /rs1/researchers/c/ckclinto/conda_pkgs/*.tar.bz2 /rs1/researchers/c/ckclinto/conda_pkgs/*.conda 2>/dev/null | wc -l`.
       Record the PLINK binary path from the plink env as `R4_PLINK=<env>/bin/plink` in the SUMMARY.
       W1 tests use it.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_osf_gate.py tests/ta_r4/test_track_b_isolation.py -q</automated>
  </verify>
  <acceptance_criteria>
    - both test files pass. The SUMMARY shows each one's RED run, and the dry-run production refusal output contains `OsfGateError` and `sentinel absent` (or the implemented reason string)
    - `bash bin/r4_fire.sh production repro_routeC -n r4_gate_probe_repro; echo $?` prints a refusal and a non-zero exit (stage mismatch)
    - `$MAN/env_lock_{plink,qtl_processing,python_stats,r_coloc_named}.yml` exist and each contains a `dependencies:` key
    - the shared `/rs1/researchers/c/ckclinto/conda_pkgs` archive count is equal before and after the solve (both numbers in the SUMMARY)
    - `$PY -c "import ast,sys;t=ast.parse(open('src/python/ta_r4/r4_osf_gate.py').read());print(sum(1 for n in ast.walk(t) if isinstance(n,ast.Attribute) and n.attr in ('environ','getenv')))"` prints 0
  </acceptance_criteria>
  <done>Production is unreachable without a real, committed and OSF-verified posting. The R4 workflow dry-runs. Envs are pinned with lockfiles.</done>
</task>

<task type="auto">
  <name>Task 4: Wave-close (W0b)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    If the implemented arm list differs from INDEX §A (13 arms), correct §A to match `ARMS` and
    record why in the LOG. Then run §C with label `W0b`, commit type `feat`. Stage exactly this
    plan's `files_modified`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/ta_r4 -q` passes; `tests/m3` outcomes equal the W0a baseline (0 removed ids, 0 outcome changes, shown as a join)
    - `git log -1 --name-only` lists only paths from this plan's files_modified; `git push` exited 0
  </acceptance_criteria>
  <done>W0b committed and pushed; LOG and STATE updated.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GSD auto-mode → production compute | an auto-selected checkpoint must not be able to start the pre-registered comparison |
| R4 config → Track B config | overlays must not leak into the base pipeline or build EUR chain members |
| OSF public API → gate | the network response decides whether the gate opens |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W0b-01 | Elevation of privilege | r4_osf_gate | mitigate | the gate requires a git-tracked committed sentinel, the amendment sha256 matching both the committed file and the OSF API record, and node az52u; no env/config bypass (AST test); stage comes from code |
| T-r4-W0b-02 | Spoofing | sentinel fabricated by an agent | mitigate | an agent cannot make the OSF API return a matching sha256 for an unposted file; §B.12 forbids creating it |
| T-r4-W0b-03 | Tampering | silent panel substitution via the EUR chain | mitigate | chain replaced wholesale + pin; forbidden-substring isolation test over every arm × row |
| T-r4-W0b-04 | Denial of service | OSF API outage | accept | fail closed; production waits; no data at risk |
| T-r4-W0b-05 | Tampering | arm-dependent pair attrition | mitigate | static manifest, deterministic builder, sha256-pinned by test |
</threat_model>

<verification>
- `pytest tests/ta_r4 -q` green, with RED evidence for each new module.
- A dry-run production refusal is observed against the real repo.
- The main Snakefile, pipeline.yaml and the frozen script are unchanged (`git diff --quiet`).
</verification>

<success_criteria>
Every arm is defined once, in code. Every path comes from one module. The manifest is fixed
before data exists. Production cannot run without a verified OSF posting.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0b-r4-workflow-overlays-osf-gate-SUMMARY.md`
</output>
