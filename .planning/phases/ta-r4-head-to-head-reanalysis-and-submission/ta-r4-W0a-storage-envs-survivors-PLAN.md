---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 1
slug: W0a-storage-envs-survivors
type: execute
wave: 1
depends_on: []
files_modified:
  - bin/r4_link_storage.sh
  - config/ta_r4/data_sources.yaml
  - envs/qtl_processing.yml
  - tests/ta_r4/__init__.py
  - tests/ta_r4/conftest.py
  - tests/ta_r4/test_storage_on_rs1.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/survivors_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/tests_baseline_W0a.tsv
  - .planning/DECISIONS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PATH-PARAMETERIZATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "realpath(data/r4) starts with /rs1/ and bin/r4_link_storage.sh recreates the link idempotently (D-11)"
    - "Every untracked known-answer survivor (results_lsweep_*.bak.*, .planning/debug/stage2_narrow_validation/*, targeted_rerun_package_20260507_222752.zip) plus the tracked R2 JSONs is copied to data/r4/known_answer_survivors/ and listed with sha256 in a committed manifest whose row count equals the measured source file count"
    - "envs/qtl_processing.yml is byte-identical to `git show c2dfb08^:envs/qtl_processing.yml` (D-14)"
    - "A tests/m3 + tests/phase1 + tests/phase2 baseline (ids/passed/skipped/failed) measured at this wave's start is committed; later waves compare against it"
    - "DECISIONS.md carries new append-only entries: E-2 fix supersedes DEC-2026-08-07 option A for Track A (D-06); osf-correction-v2 retired unposted (D-19, supersedes the P-1 posting obligation of DEC-2026-08-12); SH2B3 known-answer premise correction (D-17)"
    - "tests/ta_r4/test_storage_on_rs1.py was observed RED before the symlink existed and is GREEN after"
    - "An annotated tag ta-r4-pre-baseline marks the pre-R4 HEAD and exists on origin (git ls-remote shows it); plain `git push` does not push tags, so it is pushed explicitly"
    - "tests/ta_r4/conftest.py registers the `r4_heavy` pytest marker; QUICK deselects it, HEAVY selects it (INDEX §A)"
  artifacts:
    - path: "bin/r4_link_storage.sh"
      provides: "idempotent creation of data/r4 -> /rs1 storage root with 2770 perms"
    - path: "tests/ta_r4/conftest.py"
      provides: "overlay-merge helper (snakemake.utils.update_config), REPO_ROOT, R4 constants, r4_heavy marker registration"
      contains: "update_config"
    - path: "tests/ta_r4/test_storage_on_rs1.py"
      provides: "D-11 + REQ-PATH-PARAMETERIZATION enforcer"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/survivors_sha256.tsv"
      provides: "sha256 of every rescued known-answer survivor"
    - path: "config/ta_r4/data_sources.yaml"
      provides: "R4 data sources with license + public: true (REQ-PUBLIC-DATA-ONLY)"
  key_links:
    - from: "data/r4"
      to: "/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4"
      via: "symlink created by bin/r4_link_storage.sh"
      pattern: "ln -sfn"
    - from: "tests/ta_r4/test_storage_on_rs1.py"
      to: "data/r4 realpath"
      via: "os.path.realpath assertion"
      pattern: "realpath"
---

<objective>
Wave 0a lays the durable-storage and environment foundation for the R4 head-to-head, and rescues
the purge-exposed known-answer survivors before the next `/share` purge. It also records the
three decisions that change the project record (E-2 fix, osf-correction-v2 retirement, SH2B3
premise correction) and measures the test baseline that every later wave compares against.

Purpose: D-10/D-11 (everything regenerated onto /rs1, with manifests), D-14 (restore
`qtl_processing.yml`), D-06/D-17/D-19 (DEC entries), §C baseline.
Output: the `data/r4` symlink and its link script; a survivors manifest; the restored env file; the
`tests/ta_r4` scaffold with the first RED-first enforcer; the DEC entries; the baseline TSV.
Nothing is fired. No Snakemake run.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-CONTEXT.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-INVENTORY-2026-10-21.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
@CLAUDE.md

<interfaces>
- Storage root: /rs1/researchers/c/ckclinto/coloc_analysis/ta_r4 (28 TB free; group clintonlab).
  Share only with `chmod 2770` (memory reference_clintonlab_group_membership_and_sharing).
- `data/` is gitignored; the `data/r4` symlink itself is NOT committed. The link script is.
- Survivor sources (measured 2026-10-21, all on purge-exposed /share):
  results_lsweep_L{15,20,30}.{preFix.bak.20260429_215312,preNiter500.bak.20260429_213644}/
  .planning/debug/stage2_narrow_validation/ (reald_fits/, identity_fits/, *_test.{bim,ld,log,nosex,rds,snplist})
  targeted_rerun_package_20260507_222752.zip
  results/multitrait/coloc_susie_R2/ and results/multitrait/coloc_susie_R2*/ (tracked; copied for co-location)
- Env restore source: `git show c2dfb08^:envs/qtl_processing.yml`. `src/snakemake/rules/envs` is a
  symlink to `../../../envs` (measured), so one file serves both paths.
- DECISIONS.md style: `## YYYY-MM-DD — DEC-YYYY-MM-DD-<slug>: <one-line>`, then body. Append-only;
  never edit an existing entry. DEC-2026-08-07-e2-orientation-disposition is at DECISIONS.md:1173.
- The tests/ta_r4 conftest must not shadow the root tests/conftest.py's R_SUBPROCESS_TIMEOUT_S
  (import it from `conftest` as tests/m3 does if needed).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED-first storage enforcer, then the data/r4 link, then rescue the survivors with a sha256 manifest</name>
  <files>tests/ta_r4/__init__.py, tests/ta_r4/conftest.py, tests/ta_r4/test_storage_on_rs1.py, bin/r4_link_storage.sh, config/ta_r4/data_sources.yaml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/survivors_sha256.tsv</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md (§A, §B)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 1" and §"Runtime State Inventory"
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-INVENTORY-2026-10-21.md §1
    - tests/conftest.py and tests/m3/conftest.py (import pattern, PROJECT_ROOT, sys.path for src/python)
    - .planning/REQUIREMENTS.md §REQ-PATH-PARAMETERIZATION and §REQ-PUBLIC-DATA-ONLY
  </read_first>
  <behavior>
    - test_data_r4_realpath_on_rs1: os.path.realpath(REPO/"data/r4") starts with "/rs1/" and is a directory
    - test_data_r4_is_a_symlink_not_a_dir: os.path.islink(REPO/"data/r4") is True (a real dir on /share would be purged)
    - test_check_function_rejects_share_target (negative control, always runs): the helper `storage_violations(repo_root)` returns a non-empty list for a tmp_path fixture whose data/r4 symlinks to a tmp dir outside /rs1
    - test_no_rs1_or_share_literals_in_r4_config_and_src: scanning every file under config/ta_r4/, src/python/ta_r4/, src/snakemake/scripts/ta_r4/, every src/snakemake/rules/ta_r4_*.smk and Snakefile.ta_r4 (whichever exist; the glob is re-evaluated at every run, so files added by later waves are scanned) finds no "/rs1/researchers", "/share/clintonlab" or "/gpfs_common" substring (REQ-PATH-PARAMETERIZATION; the property is the literal itself); negative control: the same scanner on a tmp file containing "/rs1/researchers/x" reports it
    - test_manifests_parse: every *.tsv under $MAN with a sha256 column has 64-hex values, and no duplicate path rows
    - test_data_sources_public: every entry in config/ta_r4/data_sources.yaml has non-empty `license` and `public: true`
  </behavior>
  <action>
    1. Create `tests/ta_r4/__init__.py` (empty) and `tests/ta_r4/conftest.py`. Define:
       `REPO_ROOT = Path(__file__).resolve().parents[2]`; insert `REPO_ROOT/"src/python"` on `sys.path`;
       `PHASE_DIR = REPO_ROOT/".planning/phases/ta-r4-head-to-head-reanalysis-and-submission"`;
       `MAN_DIR = PHASE_DIR/"manifests"`; `R4_ROOT = "/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4"`.
       Add the helper `merged_config(*overlay_paths)`, which loads `config/pipeline.yaml` with
       `yaml.safe_load` and applies `snakemake.utils.update_config` once per overlay in order. It is
       used from W0b1 on. Add a session fixture `repo_root`. Register the marker in
       `pytest_configure(config)`: `config.addinivalue_line("markers", "r4_heavy: real-data live gates, Snakemake runs/dry-runs, frozen-script R end-to-end; run per wave via HEAVY, deselected by QUICK")`.
       Rule for later waves: a test is marked `r4_heavy` if it runs `$SMK`, runs the frozen
       `run_susie_rss.R`, or reads `data/r4/results/`. Pure R/Python unit tests stay unmarked
       unless the measured QUICK run exceeds 120 s (§C measures it).
    2. Write `tests/ta_r4/test_storage_on_rs1.py` with the six behaviours above. Put the checking
       logic in pure functions inside the test module (`storage_violations(repo_root)`,
       `literal_violations(paths)`), so the negative controls exercise the same code.
       Run `$QUICK`. It MUST be RED on `test_data_r4_realpath_on_rs1` and
       `test_data_r4_is_a_symlink_not_a_dir`, because data/r4 does not exist yet. Paste that output
       into the SUMMARY.
    3. Write `bin/r4_link_storage.sh` (bash, `set -euo pipefail`). It does
       `mkdir -p /rs1/researchers/c/ckclinto/coloc_analysis/ta_r4/{downloads,ld,sumstats,results,logs/lsf,known_answer_survivors,tmp}`,
       then `chmod 2770` on the root and on each subdir. If `data/r4` exists and is NOT a symlink,
       it exits 2 with a message and never moves or deletes it. Otherwise it runs
       `ln -sfn /rs1/researchers/c/ckclinto/coloc_analysis/ta_r4 data/r4`, then prints
       `realpath data/r4`. The /rs1 literal belongs in `bin/`, which REQ-PATH-PARAMETERIZATION's scan
       (src/, config/) does not cover. Run it twice and confirm the second run is a no-op with the
       same realpath.
    4. Write `config/ta_r4/data_sources.yaml` with one top-level key `sources:` (a mapping name → entry). Each entry carries name, url, license, `public: true`,
       build and checksum (where published). Entries:
       - `ldsc_1000G_Phase3_plinkfiles`: Zenodo record 10515792, `1000G_Phase3_plinkfiles.tgz`, md5 a7773ab485827b533cb300c76356d76b, size 288277344, CC-BY-4.0, GRCh37.
       - `onekg_phase3_vcf`: the existing /rs1 VCF copy, referenced repo-relatively as `data/r4/inputs/1kg_vcf` (a W2b symlink), public, GRCh37.
       - `ukbb_ld_weissbrod_337k`: `s3://broad-alkesgroup-ukbb-ld/UKBB_LD/`, CC BY-4.0, hg19.
       - `pan_ukbb_ld`: documented alternate, not used.
       - `eqtl_catalogue_QTS000015`: GTEx v8 via the eQTL Catalogue, open licence, GRCh38.
       - the 8 harmonized sumstats: sha256 pinned by `.planning/amendments/sha256_manifest_harmonized_m1.tsv`.
       - `yengo2018_bmi_alleles`: `bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz`.
    5. Rescue the survivors. Build the source list with
       `find results_lsweep_L15.preFix.bak.20260429_215312 results_lsweep_L15.preNiter500.bak.20260429_213644 results_lsweep_L20.preFix.bak.20260429_215312 results_lsweep_L20.preNiter500.bak.20260429_213644 results_lsweep_L30.preFix.bak.20260429_215312 results_lsweep_L30.preNiter500.bak.20260429_213644 .planning/debug/stage2_narrow_validation results/multitrait/coloc_susie_R2* -type f` plus `targeted_rerun_package_20260507_222752.zip`.
       Record N_SRC = the line count. Copy with
       `rsync -a --relative <each source> data/r4/known_answer_survivors/` (sources are untouched).
       Write `$MAN/survivors_sha256.tsv` with header `rel_path\tsize_bytes\tsha256\tsource_abs`.
       Compute sha256 on the /rs1 copy, then verify it equals the sha256 of the /share source.
       Any mismatch: STOP and report.
    6. Re-run `$QUICK`. All of `test_storage_on_rs1.py` is GREEN. The two negative-control tests ran
       and passed, meaning each detected its injected violation.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_storage_on_rs1.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `readlink -f data/r4` prints `/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4`; `stat -c %a /rs1/researchers/c/ckclinto/coloc_analysis/ta_r4` prints `2770`
    - `bash bin/r4_link_storage.sh; echo $?` prints the same realpath and `0` on a second run
    - `pytest tests/ta_r4/test_storage_on_rs1.py -q` reports `6 passed`. The SUMMARY contains the earlier RED output, showing ≥ 2 failures on the realpath/symlink tests
    - `awk 'NR>1' $MAN/survivors_sha256.tsv | wc -l` equals N_SRC from step 5 (both numbers pasted in the SUMMARY), and `cut -f3 ... | grep -cvE '^[0-9a-f]{64}$'` prints 0
    - `$PY -c "import yaml;d=yaml.safe_load(open('config/ta_r4/data_sources.yaml'));assert all(v.get('public') is True and v.get('license') for v in d['sources'].values())"` exits 0
  </acceptance_criteria>
  <done>data/r4 is a symlink to /rs1 with 2770 perms; survivors copied and sha256-verified against their sources; the storage enforcer was observed RED and is now GREEN.</done>
</task>

<task type="auto">
  <name>Task 2: Tag the pre-R4 baseline, restore envs/qtl_processing.yml, isolate the R4 conda package cache, measure the test baseline</name>
  <files>envs/qtl_processing.yml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/tests_baseline_W0a.tsv</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 8" and §"Environment Availability"
    - memory note reference_snakemake_conda_clean_tarballs_shared_cache (Snakemake runs `conda clean --tarballs` on every writable pkgs_dir)
    - envs/README.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-VALIDATION.md (suite commands)
  </read_first>
  <action>
    0. Pre-R4 baseline tag (ROADMAP scope "freeze + tag the current Track A results/env"). Nothing
       has been committed by this phase's execution yet, so HEAD is the pre-R4 state.
       - `git fsck --connectivity-only 2>&1 | tail -3` must report no missing objects.
       - If `git rev-parse -q --verify refs/tags/ta-r4-pre-baseline` succeeds, STOP and report: never
         move or recreate an existing tag.
       - `git tag -a ta-r4-pre-baseline -m "ta-r4 pre-R4 baseline: Track A state before the R4 head-to-head (2026-10-21 plans)" HEAD`
       - `git push origin ta-r4-pre-baseline` (plain `git push` does not push tags; memory
         reference_ncsu_github_push_auth).
       - Record `git rev-parse ta-r4-pre-baseline^{commit}` and `git ls-remote --tags origin ta-r4-pre-baseline`
         in the SUMMARY; the two commit shas must be equal.
    1. Run `git show c2dfb08^:envs/qtl_processing.yml > envs/qtl_processing.yml`, then confirm
       `cmp <(git show c2dfb08^:envs/qtl_processing.yml) envs/qtl_processing.yml` exits 0 and
       `ls -la src/snakemake/rules/envs/qtl_processing.yml` resolves through the symlink. Edit nothing
       in the file. Its unpinned `>=` specs are frozen by a lockfile export after the first solve
       (W0b2 Task 3).
    2. Create `$R4_CONDA_PREFIX` and `$R4_CONDA_PREFIX/pkgs` (mkdir -p; chmod 2770). Write
       `$R4_CONDARC` containing exactly
       `pkgs_dirs:\n  - /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/pkgs\n` (YAML). This
       file lives on /rs1 and is not committed. Its path is passed by `bin/r4_fire.sh` (W0b2). Check
       with `CONDARC=$R4_CONDARC conda config --show pkgs_dirs` that only that directory is listed.
       The shared `/rs1/.../conda_pkgs` must NOT appear.
    3. Measure the baseline before any further code change:
       `$PY -m pytest tests/m3 tests/phase1 tests/phase2 -q -rA -p no:cacheprovider 2>&1 | tee data/r4/logs/tests_baseline_W0a.log`.
       Parse the `-rA` lines into `$MAN/tests_baseline_W0a.tsv` (columns `test_id\toutcome`). Also
       record the totals line. Reconcile: rows by outcome must sum to the reported totals. If any
       test FAILS at baseline, record it as a pre-existing failure in the LOG, by id. Do not fix it.
       Do not proceed silently: list it in the SUMMARY as a baseline fact.
  </action>
  <verify>
    <automated>cmp <(git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis show c2dfb08^:envs/qtl_processing.yml) /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/envs/qtl_processing.yml && echo IDENTICAL</automated>
  </verify>
  <acceptance_criteria>
    - the `cmp` above prints `IDENTICAL`
    - `CONDARC=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/condarc conda config --show pkgs_dirs` lists exactly one directory, `/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/pkgs`
    - `$MAN/tests_baseline_W0a.tsv` exists; the SUMMARY shows `awk -F'\t' 'NR>1{c[$2]++} END{for(k in c) print k,c[k]}'`, and its passed/skipped/failed values equal the pytest totals line
    - `git ls-remote --tags origin ta-r4-pre-baseline` prints one line, and `git cat-file -t ta-r4-pre-baseline` prints `tag` (annotated)
  </acceptance_criteria>
  <done>The env file is restored byte-identically, the R4 conda cache is isolated, and the baseline is committed and reconciled.</done>
</task>

<task type="auto">
  <name>Task 3: Append the three DEC entries, then run the wave-close protocol</name>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/DECISIONS.md lines 1173-1300 (DEC-2026-08-07-e2-orientation-disposition and its follow-ups) and the DEC-2026-08-12-* entries (grep -n "DEC-2026-08-12" .planning/DECISIONS.md)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-CONTEXT.md D-06, D-17, D-19
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md lines 40-160 (the L=15 swap)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    Append (do not edit existing text) three entries at the end of `.planning/DECISIONS.md`:
    1. `## 2026-10-21 — DEC-2026-10-21-ta-r4-e2-fix-supersedes-option-a: E-2 is FIXED for Track A (supersedes DEC-2026-08-07 option A for Track A only)`.
       Body:
       - Decider: Carter, 2026-10-21 (ta-r4 discuss-phase D-06).
       - Option A's premise ("Track A is in submission; fixing would move numbers in a manuscript under submission") is recorded as FALSE: the 2026-05-12 package was never submitted.
       - The fix has three TDD units: BMI allele restoration, panel REF/ALT emission with plink `--keep-allele-order`, and QTL-beta orientation behind `--qtl-orient`, default false.
       - All R4 arms run on fixed code. Frozen and fixed numbers are reported side by side.
       - Track B is unaffected: AFR-gated paths stay byte-identical with the flags at their defaults.
    2. `## 2026-10-21 — DEC-2026-10-21-osf-correction-v2-retired-unposted: osf-correction-v2 is retired UNPOSTED; the R4 pre-registration amendment carries the E-2 finding and fix`.
       Body: Carter D-19. This supersedes the P-1 posting obligation of DEC-2026-08-12 (cite its
       exact heading as found by grep). Its stated premise ("code is unchanged") is false under
       D-06. The Methods correction note is rewritten in W8a.
    3. `## 2026-10-21 — DEC-2026-10-21-sh2b3-known-answer-premise: the SH2B3 PP.H4 = 1.0 known answer is the EXACT R2 configuration (L=15 @ max_iter 500/1000 for BMI/HTN/stroke + Stage-2 L=10 for asthma/T2D), not max_iter 100`.
       Body: D-17 corrects D-12(b). Cite `ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md` with
       the line numbers you verify by reading it (expected near 153-156). The L=10 / iter-100 run is
       a separate measurement. The manuscript states the true provenance.
    Then run the §C wave-close protocol with label `W0a`. Stage exactly the files in this plan's
    `files_modified`. Never stage `data/r4` (a gitignored symlink created by `bin/r4_link_storage.sh`). The commit type is `chore`.
    Push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git log -1 --format=%s && git diff HEAD~1 --stat -- .planning/DECISIONS.md | tail -1 && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - `git diff HEAD~1 -- .planning/DECISIONS.md | grep -c '^-[^-]'` prints 0, so the change is append-only
    - `grep -c '^## 2026-10-21 — DEC-2026-10-21-' .planning/DECISIONS.md` prints 3
    - `$PY -m pytest tests/m3/test_source_freeze_pins.py -q` passes
    - the full-suite counts in the LOG equal the baseline plus the 6 new ta_r4 tests, with 0 removed ids and 0 outcome changes. Show the comparison as a `join` of `tests_baseline_W0a.tsv` against the new `-rA` output
    - `git status --porcelain -- envs/qtl_processing.yml config/ta_r4 tests/ta_r4 bin/r4_link_storage.sh` is empty after commit, and `git push` exited 0
  </acceptance_criteria>
  <done>The three DEC entries are appended; W0a is committed, fsck is clean and the commit is pushed; the LOG and STATE are updated.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| /share (purged) → /rs1 (durable) | known-answer survivors cross here; loss or corruption = an unrecoverable comparator |
| shared conda package cache | Snakemake's `conda clean --tarballs` can delete other projects' cached archives |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W0a-01 | Tampering | survivor copy | mitigate | sha256 of the /rs1 copy must equal the /share source's sha256 per file; manifest row count == measured source count |
| T-r4-W0a-02 | Denial of service | `/share` purge | mitigate | all R4 storage via the data/r4 symlink to /rs1; `test_storage_on_rs1` enforces the realpath |
| T-r4-W0a-03 | Information disclosure | /rs1 dirs | mitigate | `chmod 2770` (group-private), never world-readable |
| T-r4-W0a-04 | Denial of service | shared conda cache | mitigate | CONDARC pkgs_dirs isolated to `$R4_CONDA_PREFIX/pkgs` |
| T-r4-W0a-05 | Repudiation | DECISIONS.md | mitigate | append-only; acceptance requires 0 removed lines in the diff |
</threat_model>

<verification>
- `pytest tests/ta_r4 -q` green, with RED evidence in the SUMMARY.
- Survivors manifest reconciled: rows == source files, every sha256 verified against its source.
- The full suite shows no outcome change against the newly measured baseline.
</verification>

<success_criteria>
The purge can no longer destroy any R4 input or known-answer survivor. The test baseline is
measured and committed. Three DEC entries record the decisions that change the project record.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0a-storage-envs-survivors-SUMMARY.md`
</output>
