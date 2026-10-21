---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 4
slug: W0c-receipts-validators-enforcers
type: execute
wave: 4
depends_on: ["ta-r4-W0b2-pair-manifest-osf-gate-workflow"]
files_modified:
  - src/python/ta_r4/validate_r4_fits.py
  - src/python/ta_r4/write_ld_receipt.py
  - src/python/ta_r4/commands.py
  - src/snakemake/scripts/ta_r4/make_matched_identity_payload.R
  - src/snakemake/rules/ta_r4_finemap.smk
  - tests/ta_r4/fixtures/build_fixture_region.R
  - tests/ta_r4/test_no_silent_identity.py
  - tests/ta_r4/test_frozen_script_armed_e2e.py
  - tests/ta_r4/test_arm_variant_sets_identical.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "validate_r4_fits.py rejects every silent-identity shape: the NULL-R branch (run_susie_rss.R:1114), ladder-exhaustion identity_fallback (:1144), LD_DECLARED_ABSENT / ld_dir_missing degradation (:157-165), ld_matrix != ld_file_declared, ld_authoritative false, ld_allele_aware false, and receipt md5 != panel-manifest md5 (D-13)"
    - "Every R4 fit writes a sibling .ld_receipt.json {declared, md5, sha256, size, arm, stage, overlay_sha256, git_sha, policy_sha256, panel_manifest_md5}; the rule exits non-zero if the declared panel md5 differs from the committed panel manifest or the validator fails"
    - "Running the FROZEN run_susie_rss.R (unedited) on a fixture region with REF/ALT under A3 flags yields a JSON that passes validate_r4_fits in real_ld mode; the same run against a missing declared panel does NOT pass (D-13, D-28)"
    - "The A2 identity payload derived from the A3 panel carries an explicit R = I and the identical variants frame, so A2 and A3 fits on the fixture have identical retained-variant sets (D-01, Pattern 3)"
    - "run_susie_rss.R is byte-unchanged; test_source_freeze_pins stays green (D-28)"
  artifacts:
    - path: "src/python/ta_r4/validate_r4_fits.py"
      provides: "D-13 enforcer; CLI exit 1 on any violation; modes real_ld | identity_matched | legacy_any"
      exports: ["validate_fit", "main"]
    - path: "src/snakemake/rules/ta_r4_finemap.smk"
      provides: "rule r4_run_finemap (receipt + md5 gate + frozen script + validator)"
      contains: "r4_run_finemap"
    - path: "src/snakemake/scripts/ta_r4/make_matched_identity_payload.R"
      provides: "A2 payload = A3 panel variants + explicit identity R"
    - path: "tests/ta_r4/test_no_silent_identity.py"
      provides: "named D-13 enforcer (unit + live gate)"
  key_links:
    - from: "src/snakemake/rules/ta_r4_finemap.smk::r4_run_finemap"
      to: "src/legacy/region_analysis/scripts/run_susie_rss.R"
      via: "Rscript call mirroring finemap.smk:441-455 with --ld-authoritative/--ld-allele-aware from ld_read_path helpers"
      pattern: "run_susie_rss.R"
    - from: "src/snakemake/rules/ta_r4_finemap.smk::r4_run_finemap"
      to: "src/python/ta_r4/validate_r4_fits.py"
      via: "post-fit validator call; non-zero exit fails the job"
      pattern: "validate_r4_fits"
---

<objective>
Wave 0c builds the D-13 machinery that makes a silent identity fallback impossible to miss:
per-fit LD receipts, a validator that fails a job on any identity shape, and the R4 fit rule that
wraps the code-frozen `run_susie_rss.R` without editing it. It also proves end to end, on a
fixture region, that the frozen script armed by R4 flags does the authoritative, allele-aware
EUR read the research predicts, and that A2/A3 variant sets are identical by construction.

Purpose: D-13, D-28, D-01 (matched variant sets).
Output: validator + receipt writer + identity-payload builder + fit rule + three tests. No real fits.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0b1-arms-paths-overlays-signoff-SUMMARY.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0b2-pair-manifest-osf-gate-workflow-SUMMARY.md

<interfaces>
Frozen script hot spots (read; never edit), per RESEARCH:
  run_susie_rss.R:142 load_ld_matrix(ld_dir, ancestry, region_id, subset, ...)
  :149-166 --ld-dir back-compat fallback; :157-165 LD_DECLARED_ABSENT degradation (status ld_dir_missing)
  :220-323 match_indices_allele_aware (4-key join, palindrome drop, z negation) -> JSON ld_allele_* counters
  :426-439 declared mode rejects use_identity=TRUE payloads (loud)
  :642-657 assert_declared_ld_authoritative -> stop() on unreadable / use_identity / no matrix / < MIN_LD_MIN_USE
  :1080-1092 allele-aware wiring; :1112-1117 NULL-R branch (k2d semantics); :1114 diag(n) fallback exits 0; :1144 ladder exhaustion identity_fallback
JSON keys already emitted (finemap.smk:561 receipt one-liner reads them): status, ld_matrix, ld_file_declared,
  ld_authoritative, ld_status, convergence_status, ld_allele_aware, ld_allele_exact, ld_allele_flipped,
  ld_allele_dropped_{palindromic,mismatch,ambiguous,unusable}, ld_allele_catalog_join, variant_catalog_fallback,
  ld_overlap_zero_fallback, d3b_ld_z_consistency_s, ld_overlap, ld_overlap_fraction, n_CS / cs fields
Early exits (no LD keys): status in {no_variants, too_many_variants} -> validator records "early_exit" (not a violation, but counted)
From W0b1: ta_r4.arms.ARMS[arm]["validator_mode"], ta_r4.arms.production_arms(), ta_r4.paths.{panel_path, fit_json, sumstats_path, catalog_path, ld_dir_unused, regions_csv, result_dirs}
From W0b2: Snakefile.ta_r4 gate_input (offline, memoized check_osf_gate); tests/ta_r4/fixtures/make_fixture_repo.py
Panel manifest (written by W2a/W2b): $MAN/panels_<panel_dir>.tsv columns region_safe, path, md5, sha256, size_bytes, n_var, n_samples, build, source, has_ref_alt
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: D-13 validator and receipt writer — RED-first unit enforcer with injected silent shapes</name>
  <files>src/python/ta_r4/validate_r4_fits.py, src/python/ta_r4/write_ld_receipt.py, tests/ta_r4/test_no_silent_identity.py</files>
  <read_first>
    - src/legacy/region_analysis/scripts/run_susie_rss.R lines 140-170, 420-440, 640-660, 1075-1150 (read only)
    - src/snakemake/rules/finemap.smk lines 456-562 (the existing receipt one-liner and the early-exit semantics)
    - tests/m3/test_finemap_receipt_early_exit.py (existing early-exit contract)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 6"
  </read_first>
  <behavior>
    - real_ld mode passes a JSON with ld_matrix == ld_file_declared == receipt.declared, ld_authoritative true, ld_status matching ^ld_loaded;(overlap_ok|partial_overlap);, ld_allele_aware true, no "identity" substring in ld_matrix/ld_status/convergence_status, and receipt md5 == manifest md5
    - real_ld mode FAILS, with the violation name, for each injected shape:
      ld_matrix "identity"/NULL;
      convergence_status containing "identity_fallback";
      status "ld_dir_missing" or an ld_status starting "LD_DECLARED_ABSENT";
      ld_matrix != ld_file_declared;
      ld_authoritative false;
      ld_allele_aware false;
      receipt md5 != manifest md5;
      a JSON missing the ld_matrix key with status "ok" (ALARM_LD_FIELDS_MISSING)
    - identity_matched mode passes only when ld_matrix == the declared identity payload path and the payload sha256 matches the manifest. It fails when ld_matrix points at a real panel
    - legacy_any mode never fails on LD source, but records ld_source_class in {real, identity_null_R, identity_payload, missing}
    - Early exits (no_variants, too_many_variants) are classified "early_exit" in all modes, exit 0, and are counted in the summary line
    - CLI: `python -m ta_r4.validate_r4_fits --mode real_ld --fit X.json --receipt X.ld_receipt.json --panel-manifest M.tsv` exits 1 on any violation and prints one line per violation
  </behavior>
  <action>
    1. Write `tests/ta_r4/test_no_silent_identity.py`. Build fixture JSON dicts in-test: one valid
       per mode plus one per injected shape (≥ 9 negative cases). Parametrize over them. Also add a
       **live gate** `test_live_r4_fits_have_no_identity` (marked `r4_heavy`). It globs
       `*.json` under every dir in `ta_r4.paths.result_dirs("fits")`, i.e. every production arm in
       ARMS including A3_1kg_isect (checker W1/B4; no hand-written arm list), and validates each
       JSON with its receipt in its arm's `validator_mode`. Repro dirs are never globbed. A unit test
       asserts the gate's dir list equals `result_dirs("fits")` and contains `A3_1kg_isect`. While **no** production results
       directory exists it skips with reason `"no production fits yet (W5a enables)"`. Once any such
       directory exists, it must find ≥ 1 JSON per existing arm dir or fail. A zero-file glob over an
       existing dir is a FAIL, not a pass (memory feedback_skip_guard_masks_not_fixes).
       Run RED (module absent) and paste the output.
    2. Implement `validate_r4_fits.py` with
       `validate_fit(fit: dict, receipt: dict, manifest_row: dict | None, mode: str) -> list[str]`
       (violation names) and `main()`.
       `write_ld_receipt.py` (CLI) takes `--declared --arm --stage --overlay-files ... --policy --panel-manifest --region-safe --out`
       and writes `{declared, md5, sha256, size_bytes, arm, stage, overlay_sha256, git_sha, policy_sha256, panel_manifest_md5}`.
       `overlay_sha256` is the sha256 of the concatenated bytes of the overlay files in order.
       `git_sha` comes from `git rev-parse HEAD`. It exits 3 if `declared` md5 != the manifest row md5,
       or if there is no manifest row.
    3. GREEN. Then the negative-control proof: temporarily make `validate_fit` ignore
       `convergence_status`, observe the identity_fallback case go RED, restore, and paste both.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_no_silent_identity.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the pytest run reports ≥ 13 passed and exactly 1 skipped, the live gate, with the skip reason text shown via `-rs`
    - the SUMMARY shows the initial RED, plus the sabotage RED on the identity_fallback case
    - `$PY -m ta_r4.validate_r4_fits --mode real_ld --fit <identity-fixture.json> ...; echo $?` (run from src/python) prints `1`
  </acceptance_criteria>
  <done>The D-13 enforcer exists, is shown able to fail on every silent shape, and has a live gate ready for W5a.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Identity payload builder, r4_run_finemap rule, and the end-to-end frozen-script fixture test</name>
  <files>src/snakemake/scripts/ta_r4/make_matched_identity_payload.R, src/python/ta_r4/commands.py, src/snakemake/rules/ta_r4_finemap.smk, tests/ta_r4/fixtures/build_fixture_region.R, tests/ta_r4/test_frozen_script_armed_e2e.py, tests/ta_r4/test_arm_variant_sets_identical.py</files>
  <read_first>
    - src/snakemake/rules/finemap.smk lines 274-562 (the rule being mirrored, incl. SUSIE_MAX_VARIANTS export and params)
    - src/snakemake/scripts/make_identity_ld_refs.R (the k2d R=NULL payload — NOT to be reused for A2)
    - src/snakemake/scripts/plink_ld_to_rds.R lines 60-140 (the .rds shape: list(R=..., variants=data.frame(SNP_ID,CHR,POS,A1,A2[,REF,ALT]), ld_source=...))
    - src/legacy/region_analysis/scripts/run_susie_rss.R lines 200-330 (what panel columns the allele-aware join needs; how sumstats are read — tabix vs fread)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 3", §"Pattern 6", §"Pitfall 7"
  </read_first>
  <behavior>
    - make_matched_identity_payload.R --in A3.rds --out A2.rds writes list(R = diag(n) as a base matrix, variants = identical(in$variants), ld_source = "identity_matched_r4"). identical(out$variants, in$variants) is TRUE, and all(out$R == diag(n)) is TRUE
    - e2e A3: the frozen script with the r4_run_finemap shell (authoritative true, allele-aware true, --ld-file fixture A3 .rds, --ld-dir data/r4/ld_dir_unused, absent) on a 60-variant fixture region (2 causal signals, 1 transposed-allele SNP, 1 palindromic SNP) produces status ok. ld_allele_flipped >= 1, ld_allele_dropped_palindromic >= 1, and validate_fit(mode=real_ld) returns []
    - e2e A2: the same with the matched identity payload produces validate_fit(mode=identity_matched) == []. The set of retained variant ids in the A2 fit equals the set in the A3 fit
    - e2e negative control: the same A3 call with --ld-file pointing to a non-existent path. Either the script exits non-zero, or the JSON fails validate_fit(real_ld) with a named violation. The test asserts one of the two and records which happened
    - test_arm_variant_sets_identical (live gate, marked r4_heavy): for each (trait, ancestry, region) present in both arms of each matched pair — (A2_identity, A3_1kg), (AFR661_A2, AFR661_A3), (A3_ukb_isect, A3_1kg_isect) — the retained-variant id sets are equal. It skips only while neither arm dir exists; with one present and the other absent, it fails
  </behavior>
  <action>
    1. `tests/ta_r4/fixtures/build_fixture_region.R` (run with `$RSCRIPT`, seed 20261021). It
       simulates 400 genotypes × 60 SNPs with block LD and writes:
       - a panel .rds in the `plink_ld_to_rds.R` shape, including `REF`/`ALT` (`REF := A2, ALT := A1`)
       - a bgzipped + tabix-indexed sumstats file with the columns of `hypertension.EUR.tsv.bgz`
         (`CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD`). One SNP has REF/ALT swapped
         with BETA negated; one SNP is palindromic (A/T).
       - a variant catalog TSV
       - a `regions.csv` row `FIX_1,EUR,1,1000,61000,...`
       bgzip/tabix come from the R4 plink env (path recorded in the W0b2 SUMMARY). Fixtures are
       generated into `tmp_path` at test time; no binary fixtures are committed.
    2. `make_matched_identity_payload.R` (optparse `--in --out`). It stops if `in$R` is NULL or
       `in$variants` lacks REF/ALT. Use `diag(nrow(in$R))`, a base dense matrix, to match what the
       loader accepts. Check `run_susie_rss.R` for whether `Matrix::Diagonal` is accepted, and
       record which one.
    3. `src/snakemake/rules/ta_r4_finemap.smk`: rule `r4_run_finemap` with
       - output `ta_r4.paths.fit_json(ARM, "{trait}", "{ancestry}", "{region}")` and its `.fit.rds` and `.ld_receipt.json`
       - input: sumstats from `paths.sumstats_path`, variants from `paths.catalog_path`
       - input `ld_matrix=lambda w: str(resolve_ld_path(region_id=w.region, ancestry=w.ancestry, config=config, region_safe=w.region))`. The R4 chain templates use `{region_safe}` only, so the curated→M2 crosswalk (`ld_matrix_region_id`) is deliberately NOT called. The negative-control regions are absent from the crosswalk, and calling it could raise or move a path
         (for repro arms, the legacy-dir path built from `paths.panel_path`)
       - input `policy=ARMS[ARM]["policy"]`, `gate=gate_input`, `panel_manifest=$MAN/panels_<panel_dir>.tsv`
       - params `ld_authoritative=ld_file_authoritative(w.ancestry, config)`, `ld_allele_aware=ld_allele_aware(w.ancestry, config)`
       - `conda: "envs/r_coloc.yml"` (pinned)
       The shell, in order (`set -euo pipefail`):
       (i) `test -s {input.ld_matrix}`;
       (ii) `python -m ta_r4.write_ld_receipt ...`, which exits 3 on md5 mismatch;
       (iii) `export SUSIE_MAX_VARIANTS=16000`, then the exact `Rscript src/legacy/region_analysis/scripts/run_susie_rss.R` argument list from finemap.smk:441-455, with `--ld-dir data/r4/ld_dir_unused` and `--regions-csv config/ta_r4/regions_r4.csv`.
         For route `legacy` arms, call `data/r4/legacy_code/run_susie_rss_3dd76df.R` with only the 3dd76df options;
       (iv) `python -m ta_r4.validate_r4_fits --mode {params.mode} ...` (non-zero fails the job);
       (v) the existing receipt one-liner from finemap.smk:561, copied verbatim, writing `{log.ld_z_consistency}` under `data/r4/logs/`.
    4. Tests: `test_frozen_script_armed_e2e.py` invokes the exact shell command strings that the
       rule's shell would produce, through subprocess with `$RSCRIPT`'s env on PATH, so the e2e
       test exercises the frozen script, not a copy. Put the command assembly in the new module
       `src/python/ta_r4/commands.py` as `fit_command(arm, trait, ancestry, region_safe, config) -> list[str]`
       and use it from both the rule (joined with `shlex.join`) and the test. Mark the e2e tests
       `r4_heavy` (they run the frozen R script).
       `test_arm_variant_sets_identical.py` holds the live gate plus a fixture-level version using
       the e2e outputs. Write RED first, then make it GREEN.
    5. Confirm D-28: `git diff --quiet HEAD -- src/legacy/region_analysis/scripts/run_susie_rss.R`
       and `$PY -m pytest tests/m3/test_source_freeze_pins.py -q` passes.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_frozen_script_armed_e2e.py tests/ta_r4/test_arm_variant_sets_identical.py tests/m3/test_source_freeze_pins.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the e2e tests pass, and the SUMMARY pastes the fixture A3 JSON's `ld_matrix`, `ld_status`, `ld_allele_flipped`, `ld_allele_dropped_palindromic` values plus the retained-variant counts for A2 and A3 (equal)
    - the missing-panel negative control's observed outcome (non-zero exit vs named violation) is recorded verbatim
    - `git diff --quiet HEAD -- src/legacy/region_analysis/scripts/run_susie_rss.R; echo $?` prints 0 and `test_source_freeze_pins.py` passes
    - `$SMK -s Snakefile.ta_r4 --configfile config/pipeline.yaml config/ta_r4/overlay_base.yaml config/ta_r4/overlay_repro_routeC.yaml --list` (via bin/r4_fire.sh) lists `r4_run_finemap`
  </acceptance_criteria>
  <done>The frozen script, armed only by flags, is proven on a fixture to read the declared EUR panel with allele-aware orientation. A2/A3 variant sets are identical by construction. Silent fallback is caught.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W0c)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W0c`, commit type `feat`. Stage exactly this plan's files_modified.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - tests/ta_r4 green; tests/m3 outcomes unchanged against the W0a baseline (join shown); pushed
  </acceptance_criteria>
  <done>W0c committed, pushed, logged.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| frozen R script → R4 rule | the script exits 0 on silent identity fallbacks; the rule must not trust its exit code alone |
| panel file on disk → fit | a swapped or partially written panel would silently change numbers |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W0c-01 | Repudiation | silent diag(n) fallback (:1114/:1144/:157) | mitigate | validate_r4_fits in the rule shell; any identity shape → non-zero exit; live gate re-validates all JSONs |
| T-r4-W0c-02 | Tampering | panel swap between manifest and fit | mitigate | receipt md5 vs the committed panel manifest; exit 3 on mismatch |
| T-r4-W0c-03 | Tampering | edit to the frozen script | mitigate | source_freeze pins in every wave; the e2e test calls the frozen path |
| T-r4-W0c-04 | Tampering | A2/A3 variant-set drift | mitigate | the payload copies the A3 variants frame; the named live gate compares the retained sets |
</threat_model>

<verification>
- D-13 unit enforcer: ≥ 9 injected shapes rejected; the sabotage RED was observed.
- The e2e test proves the frozen-script authoritative + allele-aware read on EUR with A2 ≡ A3 variant sets.
</verification>

<success_criteria>
No R4 fit can exit 0 having read anything but its declared, manifest-matched panel, and this is
shown on a fixture before any real data exists.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0c-receipts-validators-enforcers-SUMMARY.md`
</output>
