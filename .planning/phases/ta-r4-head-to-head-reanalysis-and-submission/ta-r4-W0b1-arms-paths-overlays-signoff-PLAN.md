---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 2
slug: W0b1-arms-paths-overlays-signoff
type: execute
wave: 2
depends_on: ["ta-r4-W0a-storage-envs-survivors"]
files_modified:
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
  - src/python/ta_r4/__init__.py
  - src/python/ta_r4/arms.py
  - src/python/ta_r4/paths.py
  - src/python/ta_r4/signoff.py
  - tests/ta_r4/test_overlay_semantics.py
  - tests/ta_r4/test_signoff.py
  - tests/ta_r4/test_signoffs.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PATH-PARAMETERIZATION
  - REQ-SUSIE-RSS-POLICY
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "Each arm's stage (repro | production) comes from a hard-coded table in src/python/ta_r4/arms.py, not from config, so `--config` cannot relabel a production arm as repro"
    - "Merging overlay_base + overlay_<arm> onto config/pipeline.yaml makes ld_allele_aware(anc) == 'true' and ld_file_authoritative(anc) == 'true' for A2/A3/A3-UKB/AFR arms, replaces the ld_panel chain wholesale with exactly one R4 entry, and pins it; base config alone still gives EUR 'false' (D-14, D-15)"
    - "paths.result_dirs(kind) derives every live-gate and aggregation glob from ARMS (stage == production) plus A1_EUR / A1_AFR for coloc, so repro outputs (default priors, different schema) are never globbed and new production arms (e.g. A3_1kg_isect) are never missed (B4, W1)"
    - "signoff.parse_signoff accepts only a reply whose first line is exactly `carter-approved YYYY-MM-DD` followed by every required `key: value` for that checkpoint id; a bare `approved` (the auto-mode response) raises SignoffError, so the executor re-presents the checkpoint and records nothing (B1)"
    - "tests/ta_r4/test_signoffs.py enforces the code-level sentinels: locked configs require a valid W4a-T3 sign-off whose values equal the configs; review_decisions.yaml requires W2c-T4; a tracked OSF sentinel requires W4b-T3; a venue overlay requires W9-T1; a checked W9 ROADMAP line requires W9-T4"
    - "config/pipeline.yaml, Snakefile and every pre-existing src/snakemake/rules/*.smk are unchanged (D-15)"
  artifacts:
    - path: "src/python/ta_r4/arms.py"
      provides: "ARMS table: arm -> {stage, ancestry, panel_source, panel_dir, route, policy, validator_mode, variant_catalog}"
      exports: ["ARMS", "arm_stage", "production_arms"]
    - path: "src/python/ta_r4/paths.py"
      provides: "single source for every R4 input/output path, incl. result_dirs(kind)"
      exports: ["panel_path", "panel_manifest_path", "fit_json", "sumstats_path", "catalog_path", "coloc_json", "ld_dir_unused", "regions_csv", "result_dirs"]
    - path: "src/python/ta_r4/signoff.py"
      provides: "Carter sign-off parser/recorder/verifier (SCHEMAS per checkpoint id)"
      exports: ["SCHEMAS", "SignoffError", "parse_signoff", "record_signoff", "verify_signoff"]
    - path: "tests/ta_r4/test_signoffs.py"
      provides: "conditional code-level sentinels over every Carter sign-off"
  key_links:
    - from: "tests/ta_r4/test_signoffs.py"
      to: "config/ta_r4/{coloc_priors,decision_rules,simulation}.yaml locked flag"
      via: "locked: true requires signoffs/W4a-T3.yaml with equal values"
      pattern: "W4a-T3"
    - from: "src/python/ta_r4/paths.py::result_dirs"
      to: "src/python/ta_r4/arms.py::ARMS"
      via: "stage == production filter"
      pattern: "production"
---

<objective>
Wave 0b1 defines every arm, every path and every overlay in one place, behind RED-first overlay
semantics tests. It also builds the Carter sign-off helper that every human-action checkpoint in
this phase uses, together with the conditional code-level sentinels that tie configuration state
to a recorded, valid sign-off.

Purpose: D-01/D-14/D-15 (arms, overlays, isolation of the base config), B1 (auto-mode cannot
produce Carter's sign-off), B4 (globs from ARMS). Split from the original W0b (checker B6); the
pair manifest, OSF gate and workflow skeleton follow in W0b2.
Output: `src/python/ta_r4/{arms,paths,signoff}.py`, 13 overlays, the reproduction policy, the
priors file, three test modules. No Snakemake run.
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
From W0a: tests/ta_r4/conftest.py merged_config(*overlay_paths), REPO_ROOT, PHASE_DIR, MAN_DIR; marker r4_heavy.
Sign-off directory: .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/<checkpoint_id>.yaml
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Arms table, path module, overlays, policies and priors — RED-first overlay semantics tests</name>
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
    - test_stage_is_code_not_config: arm_stage("A3_1kg") == "production" even after update_config(c, {"ta_r4": {"stage": "repro"}})
    - test_panel_manifest_path_per_ancestry: repro_routeC with EUR and AFR returns two different files; every production arm returns `panels_<panel_dir>.tsv`
    - test_priors_single_source: coloc_priors.yaml has p1 == p2 == 1e-4, p12_primary == 5e-6, p12_sensitivity == 1e-5, and locked: false (W4b flips it)
    - test_result_dirs_from_arms: result_dirs("fits") == sorted fit dirs of exactly the arms with stage == "production" (8 dirs, includes A3_1kg_isect); result_dirs("coloc") == those arms' coloc dirs + data/r4/results/A1_EUR/coloc + data/r4/results/A1_AFR/coloc (10 dirs); no repro arm appears. Negative control: with a monkeypatched ARMS that relabels repro_routeC as production, its dir appears (the function reads ARMS, not a literal list)
  </behavior>
  <action>
    1. `src/python/ta_r4/arms.py` defines the `ARMS: dict[str, dict]` literal. Keys per arm: `stage`,
       `ancestry`, `panel_source`, `panel_dir` (under `data/r4/ld/`), `route` (`r4` | `legacy`),
       `policy` (repo-relative), `validator_mode` (`real_ld` | `identity_matched` | `legacy_any`)
       and `variant_catalog`. Rows:
       - A3_1kg: production, EUR, EUR_1kg_r4, EUR_1kg_r4, r4, config/susie_policy.yaml, real_ld.
       - A2_identity: production, EUR, EUR_identity_r4, EUR_identity_r4, r4, config/susie_policy.yaml, identity_matched.
       - A3_ukb: production, EUR, EUR_ukb337k_r4, EUR_ukb337k_r4, r4, config/susie_policy.yaml, real_ld. (W2d may switch panel_source/panel_dir to EUR_ukb337k_hm3_r4 if Carter chooses the HM3 restriction at W2c; that edit is pre-lock.)
       - A3_ukb_isect: production, EUR, EUR_ukb337k_isect_r4, EUR_ukb337k_isect_r4, r4, config/susie_policy.yaml, real_ld.
       - A3_1kg_isect: production, EUR, EUR_1kg_isect_r4, EUR_1kg_isect_r4, r4, config/susie_policy.yaml, real_ld. (E6 intersection-matched pair with A3_ukb_isect.)
       - AFR661_A3: production, AFR, AFR661_1kg_r4, AFR661_1kg_r4, r4, config/susie_policy.yaml, real_ld.
       - AFR661_A2: production, AFR, AFR661_identity_r4, AFR661_identity_r4, r4, config/susie_policy.yaml, identity_matched.
       - AFR504_A3: production, AFR, AFR504_1kg_r4, AFR504_1kg_r4, r4, config/susie_policy.yaml, real_ld.
       - repro_routeC: repro, EUR+AFR, legacy, legacy_repro, legacy semantics on current code, config/ta_r4/susie_policy_repro_iter100.yaml, legacy_any.
       - repro_routeL: repro, legacy_repro, route legacy (script `data/r4/legacy_code/run_susie_rss_3dd76df.R`), config/susie_policy.yaml (the legacy code's max_iterations bug reproduces the effective 100), legacy_any.
       - repro_k2d_routeC / repro_k2d_routeL: repro, k2d_identity panel dir, the same policies as their real-LD twins, legacy_any.
       - repro_sh2b3_r2: repro, legacy_repro panel, policy config/susie_policy_L15.yaml for bmi/hypertension/stroke. asthma/t2d reuse the Route L L10 fits (wired in W3b), legacy_any.
       Export `arm_stage(arm) -> str` and `production_arms(ancestry=None) -> list[str]`, both reading `ARMS` only.
       `src/python/ta_r4/paths.py` holds the pure functions every path comes from:
       - `panel_path(arm, region_safe)`
       - `fit_json(arm, trait, anc, region_safe)` = `data/r4/results/{arm}/fine_mapping/susie/{trait}.{anc}.{region_safe}.json`, plus `.fit.rds` and `.ld_receipt.json` siblings
       - `sumstats_path(trait, anc, arm)`: bmi.EUR on an r4 route → `data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz` (D-18); everything else → `data/processed/sumstats_harmonized/{trait}.{anc}.tsv.bgz`
       - `catalog_path(route, region_safe)`
       - `coloc_json(arm_or_A1, row_id, p12_key, varset=None)`, `ld_dir_unused()` = `data/r4/ld_dir_unused` (MUST NOT exist)
       - `regions_csv()` = `config/ta_r4/regions_r4.csv` (created in W0b2)
       - `panel_manifest_path(arm, ancestry)`: `$MAN/panels_<panel_dir>.tsv` for single-ancestry panel dirs; for the multi-ancestry legacy dir, `panels_legacy_repro.tsv` (EUR) and `panels_legacy_repro_AFR.tsv` (AFR); `panels_k2d_identity.tsv` for k2d (both ancestries in one file). Every panel manifest carries an `ancestry` column and is keyed by (ancestry, region_safe) (checker W-3)
       - `result_dirs(kind)` with kind ∈ {"fits", "coloc"}: built from `production_arms()`; for "coloc" it appends `data/r4/results/A1_EUR/coloc` and `data/r4/results/A1_AFR/coloc`. Every live gate and the W7 aggregation glob through this function only (B4).
    2. Overlays.
       - `overlay_base.yaml`: `ta_r4: {enabled: true}`, `enable_ld_pipeline: false`,
         `occlusion_lockstep: {enabled: false}`,
         `ld_read_path: {enabled: true, ancestries: [EUR, AFR], allele_aware: true, coloc: true}`.
       - Each production arm overlay: `ta_r4: {arm: <ARM>}`, `ld_panel: {<ANC>: [{source: <panel_source>, path: "data/r4/ld/<panel_dir>/{region_safe}.rds"}], pin: {<ANC>: <panel_source>}}`.
       - Repro overlays: `ld_read_path: {ancestries: []}` plus a chain for the legacy panel dir.
       Every overlay has a 3-line header comment naming its arm and how to run it via `bin/r4_fire.sh`.
    3. `susie_policy_repro_iter100.yaml` is a copy of `config/susie_policy.yaml` with only
       `max_iter_retry: 100` changed. Show this in the SUMMARY with
       `diff config/susie_policy.yaml config/ta_r4/susie_policy_repro_iter100.yaml` (exactly one line).
       `coloc_priors.yaml`: `p1: 1.0e-4`, `p2: 1.0e-4`, `p12_primary: 5.0e-6`,
       `p12_sensitivity: 1.0e-5`, `overlap_min: 0.5`, `trim_by_posterior: true`,
       `locked: false`, `citation_check: "verify Wallace 2020 p12 recommendation before W4a"`.
    4. Write `tests/ta_r4/test_overlay_semantics.py` with the behaviours above. Run it RED: modules
       and overlays are absent, so imports fail. Paste the output. Implement until GREEN. Negative
       control: temporarily delete `pin:` from `overlay_A3_1kg.yaml`, observe the pin-assertion test
       go RED, restore it, and record both outputs.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_overlay_semantics.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/ta_r4/test_overlay_semantics.py -q` passes. The SUMMARY shows the initial RED (ImportError or collection error), the pin-removal RED and the result_dirs relabel negative control
    - `$PY -c "import sys;sys.path.insert(0,'src/python');from ta_r4.arms import ARMS;print(sorted(ARMS))"` prints the 13 arm names (8 production + 5 repro)
    - `git diff --quiet HEAD -- config/pipeline.yaml Snakefile src/snakemake/rules/finemap.smk src/legacy/region_analysis/scripts/run_susie_rss.R; echo $?` prints 0
  </acceptance_criteria>
  <done>Arm semantics are pinned by tests; stage is code-owned; every result glob derives from ARMS; the base config is unchanged.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Carter sign-off helper and the conditional code-level sentinels (B1)</name>
  <files>src/python/ta_r4/signoff.py, tests/ta_r4/test_signoff.py, tests/ta_r4/test_signoffs.py</files>
  <read_first>
    - ~/.claude/get-shit-done/workflows/execute-phase.md lines 625-645 (auto mode: human-verify auto-approved with "approved", decision auto-selects option 1, ONLY human-action stops)
    - memory feedback_gsd_automode_bypasses_blocking_fire_gates
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §D
  </read_first>
  <behavior>
    signoff.py (unit, tests/ta_r4/test_signoff.py):
    - SCHEMAS maps checkpoint id → required keys and enums:
      W2c-T4: ukb_native ∈ {native, hm3}; qtl_scope ∈ {full, tissues_frozen, eqtl_only, tissues_frozen+eqtl_only}; plus the dynamic keys passed by the caller (one `trait.<trait>.<ancestry>.<field>` per UNRESOLVED trait-manifest cell)
      W3b-T3: instructions
      W4a-T3: p12_primary, kappa_cut, n_both_min, partial_rule.ci_pos_mcnemar_ns, partial_rule.ci_pos_mcnemar_opposite, partial_rule.ci_neg_mcnemar_ns, partial_rule.ci_neg_mcnemar_opposite (each ∈ the five branch names), confirmatory_sha256 = 64 lowercase hex chars; test_signoffs asserts it equals the sha256 of the canonical-serialized `confirmatory:` block of the LOCKED `config/ta_r4/decision_rules.yaml` (negative control: one edited value in the block → RED), draft ∈ {approved}. No ukb_native: it is decided once, at W2c-T4
      W4b-T3: posted ∈ {yes}
      W7-T3: instructions
      W8b-T3: instructions
      W9-T1: venue
      W9-T4: journal, submitted_date, manuscript_id, osf_url
    - parse_signoff(raw, checkpoint_id, *, min_date, today, extra_required=()) returns {date, fields}. The first non-empty line must match `^carter-approved (\d{4}-\d{2}-\d{2})$` exactly; every following non-empty line is `key: value`
    - Rejections (each raises SignoffError whose message starts "WAIT:"): `approved`; `Approved.`; `carter-approved` without a date; `carter-approved 2026-13-01`; a date after today + 1 day; a date before min_date; a missing required key; an empty value; an enum violation; an unknown key (typo guard); a duplicate key
    - record_signoff(checkpoint_id, raw, *, min_date, signoff_dir) writes `<checkpoint_id>.yaml` with `raw` (verbatim, YAML block scalar), `raw_sha256`, `token_date`, `fields`, `recorded_utc`; it refuses to overwrite an existing file
    - verify_signoff(checkpoint_id, *, signoff_dir) re-parses `raw`, checks `raw_sha256`, and returns fields; editing one character of `raw` in the file makes it raise
    - CLI: `python -m ta_r4.signoff record <ID> --raw-file F --min-date YYYY-MM-DD [--extra-required k ...]` and `python -m ta_r4.signoff verify <ID>`; both exit 1 with the SignoffError message on failure
    Conditional sentinels (tests/ta_r4/test_signoffs.py; each is a function taking a repo root so fixtures can exercise it, then one test applies it to the real repo):
    - every file in signoffs/ verifies
    - if config/ta_r4/review_decisions.yaml exists → W2c-T4 verifies and its ukb_native / qtl_scope / trait fields equal the file's values; and every config/ta_r4/trait_manifest.tsv cell whose source is `Carter <date>` equals the W2c-T4 field `trait.<trait>.<ancestry>.<field>` (and every such field has a matching cell)
    - if any of config/ta_r4/{coloc_priors,decision_rules,simulation}.yaml has locked: true → W4a-T3 verifies and p12_primary, kappa_cut, n_both_min and the four partial_rule entries equal the config values
    - if the OSF sentinel is git-tracked → W4b-T3 verifies
    - if docs/manuscript/r4/submission/venue_overlay.yaml exists → W9-T1 verifies
    - if the ROADMAP line for ta-r4-W9-submission-prep-PLAN.md is checked (`- [x]`) → W9-T4 verifies
    - Negative controls (tmp_path fixtures): a locked decision_rules.yaml with no sign-off fails; a sign-off whose kappa_cut differs from the config fails; a checked W9 ROADMAP line with no W9-T4 fails; a trait-manifest cell edited after the sign-off fails
  </behavior>
  <action>
    1. Write both test modules RED and paste the failures.
    2. Implement `signoff.py` (stdlib + PyYAML; `SIGNOFF_DIR = PHASE_DIR/"signoffs"`). It reads no
       environment variables and has no override flag.
    3. GREEN. Then the negative-control proof: temporarily relax the first-line regex to
       `^(carter-)?approved`, observe the bare-`approved` test go RED, restore, and paste both.
    4. In the real repo none of the conditions hold yet, so `test_signoffs.py` passes vacuously
       except for the fixture negative controls. That is expected: the sentinels become live as the
       phase creates the guarded files.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_signoff.py tests/ta_r4/test_signoffs.py -q</automated>
  </verify>
  <acceptance_criteria>
    - both files pass; the SUMMARY shows the initial RED, the relaxed-regex RED, and the three fixture negative controls failing as designed
    - a CLI test in test_signoff.py runs `python -m ta_r4.signoff record W3b-T3` on a raw file containing only `approved`, with a tmp_path signoff dir, and asserts exit code 1, a `WAIT:` message and no file written
  </acceptance_criteria>
  <done>An auto-generated "approved" cannot be recorded as Carter's sign-off, and configuration states that require a sign-off are enforced in code.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W0b1)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W0b1`, commit type `feat`. Stage exactly this plan's `files_modified`.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - QUICK and HEAVY green; `tests/m3` outcomes equal the W0a baseline (0 removed ids, 0 outcome changes, shown as a join)
    - `git log -1 --name-only` lists only paths from this plan's files_modified; `git push` exited 0
  </acceptance_criteria>
  <done>W0b1 committed and pushed; LOG and STATE updated.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GSD auto-mode → Carter's judgement | auto-mode answers human-verify with "approved" and decisions with option 1 |
| R4 config → Track B config | overlays must not leak into the base pipeline |
| result globs → live gates / aggregation | a hand-written glob can include repro outputs or miss a production arm |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W0b1-01 | Spoofing | Carter sign-off | mitigate | `carter-approved YYYY-MM-DD` + required keys; bare "approved" raises; sign-off file sha256-checked on verify; every Carter checkpoint is `checkpoint:human-action` |
| T-r4-W0b1-02 | Elevation of privilege | config relabels stage | mitigate | stage read from the ARMS literal; test_stage_is_code_not_config |
| T-r4-W0b1-03 | Tampering | silent panel substitution via the EUR chain | mitigate | chain replaced wholesale + pin; overlay semantics tests with a pin-removal negative control |
| T-r4-W0b1-04 | Repudiation | locks applied without Carter | mitigate | test_signoffs: locked: true requires a valid W4a-T3 sign-off with equal values |
| T-r4-W0b1-05 | Tampering | wrong result set globbed | mitigate | result_dirs derived from ARMS; relabel negative control |
</threat_model>

<verification>
- `pytest tests/ta_r4 -q` green, with RED evidence for each new module.
- The main Snakefile, pipeline.yaml and the frozen script are unchanged (`git diff --quiet`).
</verification>

<success_criteria>
Every arm and path is defined once, in code. Carter's sign-off cannot be produced by auto-mode, and
the configuration states that depend on it are enforced by tests.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0b1-arms-paths-overlays-signoff-SUMMARY.md`
</output>
