---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 3
slug: W0b2-pair-manifest-osf-gate-workflow
type: execute
wave: 3
depends_on: ["ta-r4-W0b1-arms-paths-overlays-signoff"]
files_modified:
  - config/ta_r4/regions_r4.csv
  - config/ta_r4/pair_manifest.tsv
  - src/python/ta_r4/select_null_windows.py
  - src/python/ta_r4/build_pair_manifest.py
  - src/python/ta_r4/r4_osf_gate.py
  - Snakefile.ta_r4
  - src/snakemake/rules/ta_r4_env.smk
  - bin/r4_fire.sh
  - config/ta_r4/cluster_lsf/config.yaml
  - config/ta_r4/cluster_lsf/cluster_config.yaml
  - tests/ta_r4/fixtures/make_fixture_repo.py
  - tests/ta_r4/test_null_windows.py
  - tests/ta_r4/test_pair_manifest.py
  - tests/ta_r4/test_osf_gate.py
  - tests/ta_r4/test_track_b_isolation.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/null_windows_selection.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/compute_node_network_probe.tsv
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
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "config/ta_r4/regions_r4.csv has 31 rows: 12 curated + 9 negative-control loci (cosmetic 5, blood_group 4) + 10 GWAS-null windows NC_NULL_01..NC_NULL_10 chosen by a deterministic, seeded, outcome-independent rule; this is the third admissible negative-control set (REQ-NEGATIVE-CONTROLS; HLA, the config's third set, is inadmissible under D-24)"
    - "config/ta_r4/pair_manifest.tsv has 346 rows = 12 x 10 EUR + 12 x 3 AFR + 19 x 10 EUR negative-control; 320 admissible; HLA_6p21 and BMI_Xq24 rows carry admissible=false with a reason (D-07, D-24)"
    - "The OSF API is called ONCE per production fire, on the submit host, by `r4_osf_gate verify-online` inside bin/r4_fire.sh; it writes a host receipt {sentinel_sha256, amendment_sha256, osf_reported_sha256, osf_target_node, head_sha, checked_utc, host, api_response_sha256} (B5)"
    - "Inside Snakemake (DAG evaluation and every LSF job) the gate is OFFLINE and memoized per process: sentinel git-tracked and committed, sha256 matches, receipt present for the current HEAD and consistent with the sentinel; no network call (B5)"
    - "Without a valid sentinel + receipt, `snakemake -n` on a production target exits non-zero with OsfGateError; repro targets are not gated. The refusal is tested on a fixture repo without a sentinel, so the test stays meaningful after Carter commits the real sentinel (B3, D-05, D-27)"
    - "No env var, config key or CLI flag bypasses the production check (AST scan + env-var monkeypatch + signature check)"
    - "Compute-node reachability of api.osf.io is measured by an LSF job and recorded (informational; the design does not depend on it)"
    - "Snakemake job envs are solved into /rs1/.../smk_job_envs/ta_r4 with CONDARC-isolated pkgs and their lockfiles are committed (REQ-SNAKEMAKE-CI)"
  artifacts:
    - path: "src/python/ta_r4/r4_osf_gate.py"
      provides: "verify_online(repo, *, fetch, now) -> receipt; check_osf_gate(repo, stage) offline + memoized; OsfGateError; SENTINEL_REL; CLI verify-online / check"
      exports: ["check_osf_gate", "verify_online", "OsfGateError", "SENTINEL_REL", "RECEIPT_DIR_REL"]
    - path: "src/python/ta_r4/select_null_windows.py"
      provides: "deterministic GWAS-null window selection (third negative-control set)"
    - path: "config/ta_r4/pair_manifest.tsv"
      provides: "pre-registered static all-pairs manifest (no tier gate)"
      contains: "admissible"
    - path: "Snakefile.ta_r4"
      provides: "standalone R4 workflow entry; requires ta_r4.arm; includes ta_r4_*.smk in sorted order"
    - path: "bin/r4_fire.sh"
      provides: "the only supported way to run Snakefile.ta_r4; runs verify-online before any production fire"
    - path: "tests/ta_r4/fixtures/make_fixture_repo.py"
      provides: "minimal git repo copied from the working tree, sentinel excluded, for gate dry-run tests"
  key_links:
    - from: "Snakefile.ta_r4 production rules"
      to: "src/python/ta_r4/r4_osf_gate.py::check_osf_gate"
      via: "input function evaluated at DAG time (offline, memoized)"
      pattern: "check_osf_gate"
    - from: "bin/r4_fire.sh"
      to: "src/python/ta_r4/r4_osf_gate.py verify-online"
      via: "one OSF API call per production fire on the submit host"
      pattern: "verify-online"
    - from: "bin/r4_fire.sh"
      to: "config/ta_r4/overlay_<arm>.yaml"
      via: "--configfile config/pipeline.yaml config/ta_r4/overlay_base.yaml config/ta_r4/overlay_$ARM.yaml"
      pattern: "overlay_base.yaml"
---

<objective>
Wave 0b2 pre-registers the static all-pairs manifest (including a third, GWAS-null negative-control
set), implements the OSF gate as a one-call-per-fire online verification on the submit host plus an
offline in-job check, and builds the standalone R4 workflow skeleton with pinned job environments.
All of it ships behind RED-first tests.

Purpose: D-07/D-24 (manifest), D-05/D-27 (gate), D-04/D-15 (isolation), REQ-NEGATIVE-CONTROLS
(third set), REQ-SNAKEMAKE-CI (pinned envs). Checker items B3, B5, B6, W10.
Output: regions file, null-window selector, manifest + builder, gate module, `Snakefile.ta_r4`,
`bin/r4_fire.sh`, LSF profile, fixture-repo helper, five test modules, env lockfiles, network probe
record. No fits.

Design choice (Claude's discretion, D-14 "overlay design"): a **standalone** `Snakefile.ta_r4`
instead of an `include:` inside the main `Snakefile`. The base DAG then cannot change by
construction, and no R4 output pattern can collide with `finemap.smk::run_finemap`'s
`finemap_output()` pattern. `include:` inside a `for` loop over sorted `ta_r4_*.smk` files was
verified on Snakemake 7.32.4 (planner scratch test, 2026-10-21; `workflow.include(path)` also works).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0b1-arms-paths-overlays-signoff-SUMMARY.md

<interfaces>
From W0b1: ta_r4.arms.{ARMS, arm_stage, production_arms}; ta_r4.paths.{panel_path, fit_json, sumstats_path, catalog_path, coloc_json, ld_dir_unused, regions_csv, result_dirs}
From W0a: tests/ta_r4/conftest.py merged_config, REPO_ROOT, PHASE_DIR, MAN_DIR; marker r4_heavy
Legacy script (3dd76df) options: --sumstats --trait --ancestry --method --region --regions-csv --ld-dir
  --variant-list --credible-set --policy --output   (NO --ld-file / --ld-authoritative / --ld-allele-aware)
regions_curated.csv schema: region_id,ancestry,chr,start,end,lead_snp,gene,trait_list,source,canonical_pairs (12 rows)
config/negative_controls.yaml: cosmetic (OCA2/HERC2 15:28000000-28500000, SLC24A5 15:48000000-48500000,
  MC1R 16:89900000-90100000, TYR 11:88500000-89000000, IRF4 6:396000-500000) and blood_group
  (ABO 9:136125000-136155000, RH 1:25580000-25750000, FUT1/FUT2 19:49200000-49260000, KEL 7:142630000-142720000), GRCh37;
  hla_immune chr6:25-35 Mb (inadmissible, D-24)
Track A sumstats (8, sha256-pinned by .planning/amendments/sha256_manifest_harmonized_m1.tsv):
  data/processed/sumstats_harmonized/{asthma,bmi,hypertension,stroke,t2d}.EUR.tsv.bgz, {asthma,stroke,t2d}.AFR.tsv.bgz
OSF public API: GET https://api.osf.io/v2/files/<guid>/ -> data.attributes.extra.hashes.{sha256,md5},
  data.attributes.date_created; the containing node is in data.relationships.target (check the live schema on file k8w7n, az52u)
Snakemake 7.32.4: `for _smk in sorted(glob.glob(...)): include: _smk` works (verified)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Regions file with the third negative-control set (GWAS-null windows) and the pre-registered all-pairs manifest</name>
  <files>config/ta_r4/regions_r4.csv, src/python/ta_r4/select_null_windows.py, src/python/ta_r4/build_pair_manifest.py, config/ta_r4/pair_manifest.tsv, tests/ta_r4/test_null_windows.py, tests/ta_r4/test_pair_manifest.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/null_windows_selection.tsv</files>
  <read_first>
    - config/regions_curated.csv (12 rows; note `BMI_5q13.3` → safe id `BMI_5q13_3` per Snakefile:51 `replace(".", "_").replace("/", "_")`)
    - config/negative_controls.yaml (incl. `matched_null_spec`, whose intent the null windows implement on GRCh37)
    - src/python/create_coloc_manifest.py and the filter at src/python/filter_finemap_summary.py:374 (the tier gate R4 must NOT use)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 5", §"Pitfall 15"
    - .planning/REQUIREMENTS.md §REQ-NEGATIVE-CONTROLS (≥ 3 sets)
  </read_first>
  <behavior>
    Null windows (test_null_windows.py, fixture sumstats in tmp_path):
    - Candidates are 250,000-bp tiles `[k*250000+1, (k+1)*250000]` on chr1–22
    - A tile is excluded if it overlaps any curated region (any ancestry) ±1 Mb, any cosmetic/blood_group NC region ±1 Mb, or chr6:25,000,000–35,000,000; or if any of the 8 Track A files has a variant with P < 1e-5 inside it; or if any of the 5 EUR files has < 200 variants inside it
    - Selection: candidates sorted by (chr, start); `numpy.random.default_rng(20261021).choice(n, 10, replace=False)`; selected tiles re-sorted genomically and named NC_NULL_01..NC_NULL_10
    - Deterministic: two runs give the same sha256 for both outputs
    - Negative controls: a fixture tile holding one variant with P = 1e-6 is excluded; a tile 900 kb from a curated region is excluded; a tile with 199 EUR variants is excluded
    Pair manifest (test_pair_manifest.py):
    - Exactly 346 data rows; by row_class: primary EUR 120, primary AFR 36, negative_control 190
    - admissible == "true" for exactly 320 rows; every admissible == "false" row has region_id in {HLA_6p21, BMI_Xq24} and a non-empty inadmissible_reason
    - Every unordered EUR trait pair appears exactly once per EUR region (10 per region); trait_a < trait_b lexicographically
    - AFR rows use only {asthma, stroke, t2d}
    - row_id is unique and equals f"{region_safe}__{ancestry}__{trait_a}_vs_{trait_b}"
    - nc_set ∈ {cosmetic, blood_group, gwas_null} for negative_control rows; 50 + 40 + 100 = 190
    - No column depends on any fit outcome (no status/tier column). Negative control: a manifest containing a "status" column fails the schema test
    - The builder is deterministic: running it twice gives byte-identical output (sha256 equal)
    - ABO rows carry nc_caveat == "reported_stroke_association_verify" (research A5) and do not use the stroke pairs as negative-control evidence by default
  </behavior>
  <action>
    1. `src/python/ta_r4/select_null_windows.py` (argparse: `--sumstats` (8 paths), `--sha256-manifest .planning/amendments/sha256_manifest_harmonized_m1.tsv`,
       `--regions-curated`, `--negative-controls`, `--window 250000`, `--pmax 1e-5`, `--min-variants 200`,
       `--n-select 10`, `--seed 20261021`, `--candidates-out`, `--selected-out`).
       - Verify each input's sha256 against the m1 manifest before reading (exit 2 on mismatch).
       - Stream each file once (gzip + csv), accumulating per-tile min P and per-tile EUR variant counts.
       - Write all eligible candidates to `data/r4/findings/null_window_candidates.tsv`
         (chr, start, end, n_var per EUR trait, min_p over the 8 files).
       - Write `$MAN/null_windows_selection.tsv`: one row per selected window (region_id, chr, start,
         end, n_var per EUR trait, min_p), followed by `#` comment lines giving n_candidates, the
         candidates file sha256 and each input file sha256.
       This rule conditions on GWAS P-values only (it defines a null), never on any arm outcome. W4a
       discloses it in the amendment.
    2. `config/ta_r4/regions_r4.csv`: the same columns as `config/regions_curated.csv`. The 12
       curated rows are copied verbatim. Then the 9 cosmetic/blood_group rows are added with
       `ancestry=EUR`, GRCh37 coordinates from `config/negative_controls.yaml`,
       `source=negative_control`, an empty `canonical_pairs`, and region_ids `NC_OCA2_HERC2, NC_SLC24A5, NC_MC1R, NC_TYR, NC_IRF4,
       NC_ABO, NC_RH, NC_FUT1_FUT2, NC_KEL`. Then the 10 `NC_NULL_*` rows from the selection, with
       `source=negative_control_gwas_null`. The frozen `run_susie_rss.R` takes region coordinates
       from `--regions-csv`. Read how it looks a region up (by region_id only, or by region_id +
       ancestry) and record the answer in the SUMMARY. If it filters on ancestry, add AFR
       duplicates of the 12 curated rows.
    3. `src/python/ta_r4/build_pair_manifest.py` (argparse: `--regions`, `--out`). It writes the TSV
       with columns `row_id, ancestry, region_id, region_safe, trait_a, trait_b, row_class,
       admissible, inadmissible_reason, canonical_pair, nc_set, nc_caveat`. Rules:
       - EUR primary: the 12 curated regions × C(5,2) = 10 pairs.
       - AFR primary: the 12 curated regions × C(3,2) = 3 pairs.
       - Negative control: the 19 NC regions × 10 EUR pairs; `nc_set` is `cosmetic`, `blood_group` or `gwas_null`.
       - `admissible = false` for HLA_6p21 (`reason: "D-24: no admissible panel (69k HM3 variants > 16000 cap); UKB exploratory fits only, no coloc row"`) and BMI_Xq24 (`reason: "D-24: chrX absent from LDSC 1000G and UKB LD"`).
       - `canonical_pair` is true when `f"{trait_a}_vs_{trait_b}"` is in the region's `canonical_pairs`.
       - Sort by `(row_class, ancestry, region_safe, trait_a, trait_b)` and write with `\n` line endings.
    4. Write both test modules RED first. Then run the selector and the builder:
       `$PY src/python/ta_r4/build_pair_manifest.py --regions config/ta_r4/regions_r4.csv --out config/ta_r4/pair_manifest.tsv`.
       The manifest test regenerates into `tmp_path` and asserts sha256 equality with the committed
       file, so the committed manifest is exactly the builder's output.
    5. The arithmetic goes in the SUMMARY: 120 + 36 + 190 = 346; inadmissible 2×10 + 2×3 = 26;
       346 − 26 = 320; NC 5×10 + 4×10 + 10×10 = 190. Also paste n_candidates and the 10 selected windows.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_null_windows.py tests/ta_r4/test_pair_manifest.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `awk 'NR>1' config/ta_r4/pair_manifest.tsv | wc -l` prints 346, and the admissible count (column index confirmed against the header in the SUMMARY) prints 320
    - `awk -F, 'NR>1' config/ta_r4/regions_r4.csv | wc -l` prints 31
    - both pytest files pass; the SUMMARY shows their RED runs, the "status column" negative control and the three null-window exclusion negative controls
  </acceptance_criteria>
  <done>A static, deterministic, outcome-independent manifest with three admissible negative-control sets is committed and pinned by its builders.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: OSF gate — one online verification per fire on the submit host, offline memoized in-job check (B5)</name>
  <files>src/python/ta_r4/r4_osf_gate.py, tests/ta_r4/test_osf_gate.py</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 7", §"Pitfall 11", §"Pitfall 14"
    - memory feedback_gsd_automode_bypasses_blocking_fire_gates (why the gate is code)
    - memory feedback_failsafe_default_is_caller_relative (fail closed)
  </read_first>
  <behavior>
    Unit tests (fast, unmarked; tmp git repos built in-test):
    - check_osf_gate(repo, "repro") returns None, even with no sentinel; any stage other than "repro"/"production" raises ValueError
    - Offline check_osf_gate(repo, "production") raises OsfGateError naming the reason for each case:
      (a) sentinel absent; (b) sentinel untracked (`git ls-files --error-unmatch` fails); (c) sentinel tracked with uncommitted changes;
      (d) a missing key among {osf_url, osf_file_guid, posted_utc, amendment_path, amendment_sha256, head_sha};
      (e) amendment_path untracked or its sha256 != amendment_sha256; (f) posted_utc in the future or unparseable;
      (g) sentinel head_sha not an ancestor of HEAD;
      (k) no receipt for the current HEAD under data/r4/gate/; (l) receipt sentinel_sha256 != sha256(sentinel);
      (m) receipt amendment_sha256 or osf_reported_sha256 != sentinel amendment_sha256; (n) receipt osf_target_node != "az52u";
      (o) receipt head_sha != HEAD
    - verify_online(repo, fetch=fake) runs (a)–(g), then fetch once, then raises for (h) API sha256 != amendment_sha256, (i) fetch raises (network down: fail closed), (j) API target node != "az52u"; on success it writes data/r4/gate/osf_receipt_<HEAD>.json and osf_api_response_<HEAD>.json and returns the receipt
    - Positive control: tmp repo with committed amendment + sentinel; verify_online with a fake fetch returning the matching sha256 and node az52u writes a receipt; check_osf_gate(repo, "production") then returns None
    - Memoization: after one passing offline check, a second call in the same process makes 0 further subprocess calls (monkeypatched counter)
    - Offline path makes no network call: with `urllib.request.urlopen` monkeypatched to raise, the offline positive control still passes
    - No bypass: an AST scan finds no os.environ / os.getenv in r4_osf_gate.py; setting env vars R4_GATE_BYPASS=1, R4_STAGE=repro, OSF_GATE_SKIP=1 does not change any outcome; `inspect.signature(check_osf_gate)` has exactly (repo_root, stage) plus keyword-only `now`
  </behavior>
  <action>
    1. Write `tests/ta_r4/test_osf_gate.py` unit section RED; paste.
    2. `src/python/ta_r4/r4_osf_gate.py`:
       - `SENTINEL_REL = ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json"`, `RECEIPT_DIR_REL = "data/r4/gate"`
       - `class OsfGateError(RuntimeError)`
       - `_local_checks(repo, now)` implements (a)–(g); `fetch_osf_file(guid)` does a `urllib.request` GET of `https://api.osf.io/v2/files/{guid}/` with a 30 s timeout and returns `{"sha256", "md5", "date_created", "target_node", "raw"}`
       - `verify_online(repo_root, *, fetch=fetch_osf_file, now=None) -> dict` (submit host only; writes the receipt and the raw response, receipt carries `api_response_sha256`)
       - `check_osf_gate(repo_root, stage, *, now=None) -> None` (offline). It memoizes with `functools.lru_cache` keyed on (realpath, HEAD); HEAD is read once per process per repo
       - git calls via `subprocess.run([...], cwd=repo_root, capture_output=True)`, never `shell=True`
       - CLI: `python -m ta_r4.r4_osf_gate verify-online --stage production` and `python -m ta_r4.r4_osf_gate check --stage production`; each exits 1 and prints the reason on OsfGateError
       - It reads NO environment variables.
       Confirm the JSON path of the target node against the live record for GUID `k8w7n` (M1
       amendment file on az52u) and paste the parsed dict in the SUMMARY. That is the live known
       answer for the parser. This one-off is the only network call this plan makes to OSF.
    3. GREEN. Negative control: temporarily skip check (o) and observe the head-mismatch test RED; restore; paste both.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_osf_gate.py -q -m "not r4_heavy"</automated>
  </verify>
  <acceptance_criteria>
    - the unit tests pass; the SUMMARY shows the RED run, the (o)-skip negative control, and the parsed k8w7n dict
    - `$PY -c "import ast;t=ast.parse(open('src/python/ta_r4/r4_osf_gate.py').read());print(sum(1 for n in ast.walk(t) if isinstance(n,ast.Attribute) and n.attr in ('environ','getenv')))"` prints 0
  </acceptance_criteria>
  <done>The gate costs one OSF API call per fire, runs offline in every job, and fails closed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Snakefile.ta_r4, fire script, LSF profile, fixture-repo gate dry-runs, isolation tests, compute-node network probe, env solves</name>
  <files>Snakefile.ta_r4, src/snakemake/rules/ta_r4_env.smk, bin/r4_fire.sh, config/ta_r4/cluster_lsf/config.yaml, config/ta_r4/cluster_lsf/cluster_config.yaml, tests/ta_r4/fixtures/make_fixture_repo.py, tests/ta_r4/test_osf_gate.py, tests/ta_r4/test_track_b_isolation.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/compute_node_network_probe.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_plink.yml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_qtl_processing.yml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_python_stats.yml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_named.yml</files>
  <read_first>
    - config/cluster_lsf/config.yaml, config/cluster_lsf/cluster_config.yaml, config/bsub_wrapper.sh
    - Snakefile lines 1-63 (region parsing to mirror for regions_r4.csv)
    - envs/plink.yml, envs/python_stats.yml, envs/r_coloc.yml
    - src/python/ld_panel.py (resolve_ld_path) and src/python/ld_read_path.py
  </read_first>
  <behavior>
    Heavy (marked r4_heavy) gate dry-runs on a fixture repo (B3):
    - `make_fixture_repo(tmp_path)` copies from the WORKING TREE exactly: Snakefile.ta_r4, config/pipeline.yaml, config/ta_r4/, src/python/, src/snakemake/rules/ta_r4_*.smk, envs/; it never copies the sentinel or data/; it runs `git init`, sets a fixed author, commits, and returns the path
    - Fixture repo without a sentinel: `$SMK -s Snakefile.ta_r4 -d <fixture> -n --configfile ...overlay_base.yaml ...overlay_A3_1kg.yaml r4_gate_probe` exits non-zero and stderr contains "OsfGateError"; the same with overlay_repro_routeC and target r4_gate_probe_repro exits 0
    - Fixture repo positive control: a committed fixture sentinel + amendment and a receipt written by verify_online with a fake fetch (in-process) → the production dry-run exits 0. Fixture sentinels exist only under tmp_path (§B.12 applies to the real repo)
    - Real-repo state test (conditional, never permanently RED): if the real sentinel is NOT tracked, `check --stage production` exits 1 with "sentinel absent"; if it IS tracked, the local checks (a)–(g) pass. A receipt is not required here because receipts are per-HEAD and per-fire
    Isolation (test_track_b_isolation.py):
    - For every arm in ARMS and every manifest row, every path from ta_r4.paths lies under data/r4/ or data/processed/sumstats_harmonized/ and contains none of EUR_ukbb_pub, EUR_ukbb_ld, EUR_aou, AFR_aou, data/processed/ld_reference/, sumstats_harmonized_occl. Negative control: a monkeypatched panel_path returning "data/processed/ld_reference/EUR_ukbb_pub/x.rds" is reported
    - test_r4_paths_independent_of_crosswalk: for every region in regions_r4.csv (curated + all NC), resolve_ld_path(region_id=region_safe, ancestry, merged config, region_safe=region_safe) on a tmp tree containing the expected file returns data/r4/ld/<panel_dir>/<region_safe>.rds. R4 rules never call ld_matrix_region_id; NC ids are absent from the curated→M2 crosswalk
    - (heavy) `$SMK -s Snakefile.ta_r4 -n --printshellcmds` for repro_routeC on target r4_env_probe_all lists no forbidden substring
  </behavior>
  <action>
    1. `Snakefile.ta_r4`:
       - `configfile: "config/pipeline.yaml"`. Require `config["ta_r4"]["enabled"] is True` and `config["ta_r4"]["arm"] in ARMS`, else raise `WorkflowError("run via bin/r4_fire.sh")`.
       - `sys.path.insert(0, str(Path(workflow.basedir)/"src/python"))`; import `ta_r4.arms`, `ta_r4.paths`, `ta_r4.r4_osf_gate`.
       - Parse `config/ta_r4/regions_r4.csv` into REGION_INFOS / REGION_SAFE_TO_ID / REGION_METADATA with the Snakefile:51-61 rule. Load `config/ta_r4/pair_manifest.tsv`.
       - `def gate_input(wildcards): check_osf_gate(Path(workflow.basedir), arm_stage(ARM)); return [SENTINEL_REL] if arm_stage(ARM) == "production" else []`. The check is offline and memoized (Task 2), so per-job cost is one cached git read.
       - Rules `r4_gate_probe` (touches `data/r4/tmp/gate_probe_{ARM}.ok`; input `gate_input`) and `r4_gate_probe_repro`.
       - `for _smk in sorted(glob.glob(str(Path(workflow.basedir)/"src/snakemake/rules/ta_r4_*.smk"))): include: _smk`. Later plans only add files (`ta_r4_panels.smk`, `ta_r4_panels_afr_ukb.smk`, `ta_r4_finemap.smk`, `ta_r4_coloc.smk`, `ta_r4_qtl.smk`, `ta_r4_sim.smk`, `ta_r4_repro.smk`) and never edit `Snakefile.ta_r4`. Rule names must be unique across these files.
       - `ta_r4_env.smk` defines `r4_env_probe_{plink,qtl_processing,python_stats}`. Each uses `conda: str(Path(workflow.basedir)/"envs"/"<name>.yml")` and writes the tool version to `data/r4/logs/env_probe/<name>.txt`. A rule `r4_env_probe_all` collects them.
    2. `bin/r4_fire.sh STAGE ARM [snakemake args...]`, with `set -euo pipefail`:
       - Refuse unless `ARMS[ARM].stage == STAGE` (checked via `$PY -c`).
       - `export CONDARC=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/condarc`; run `bash bin/r4_link_storage.sh`.
       - If STAGE is production: refuse if `git status --porcelain -- Snakefile.ta_r4 src/python/ta_r4 src/snakemake config/ta_r4 src/legacy` is non-empty (the receipt binds HEAD); then run `(cd src/python && $PY -m ta_r4.r4_osf_gate verify-online --stage production)` and abort on non-zero. Print: "Do not commit until this fire ends: in-job gate checks require HEAD == receipt head_sha."
       - `exec $SMK -s Snakefile.ta_r4 --configfile config/pipeline.yaml config/ta_r4/overlay_base.yaml config/ta_r4/overlay_${ARM}.yaml --use-conda --conda-prefix /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4 --profile config/ta_r4/cluster_lsf "$@"`.
       The /rs1 literals live in `bin/`, which is outside the REQ-PATH scan (src/, config/).
    3. `config/ta_r4/cluster_lsf/config.yaml`: a copy of `config/cluster_lsf/config.yaml` with logs at
       `-o data/r4/logs/lsf/%J.{rule}.out -e data/r4/logs/lsf/%J.{rule}.err` and `jobs: 200`.
       `cluster_config.yaml` sets `__default__: {queue: serial, mem_mb: 8000, threads: 1}`.
       Panel/fit rules with mem ≥ 16000 stay on serial (1 slot); never `standard` with < 8 threads.
    4. `tests/ta_r4/fixtures/make_fixture_repo.py` and the heavy tests above; `test_track_b_isolation.py`.
       Write them RED first, then GREEN.
    5. Compute-node network probe (B5; informational): submit
       `bsub -q serial -n 1 -W 10 -o data/r4/logs/net_probe.%J.out -e data/r4/logs/net_probe.%J.err "curl -sS -o /dev/null -w '%{http_code}' --max-time 20 https://api.osf.io/v2/; echo \" curl_exit=\$?\""`,
       and run the same `curl` on the submit host. Write `$MAN/compute_node_network_probe.tsv`
       (`host, exec_host, utc, http_code, curl_exit`) with both rows; `exec_host` from the LSF output
       header. Whatever the result, the gate design does not depend on it; record it in the LOG.
    6. Solve the envs: `bash bin/r4_fire.sh repro repro_routeC r4_env_probe_all --conda-create-envs-only --cores 1`,
       then `bash bin/r4_fire.sh repro repro_routeC r4_env_probe_all --cores 1 --profile ''`. If
       `--profile ''` is rejected, pass `--cluster ''` per the Snakemake 7 CLI and record what worked.
       For each env dir listed by `--list-conda-envs`, run
       `conda env export --no-builds -p <dir> > $MAN/env_lock_<name>.yml`; also
       `conda env export --no-builds -p /rs1/researchers/c/ckclinto/conda_envs/r_coloc > $MAN/env_lock_r_coloc_named.yml`.
       Confirm `ls /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/pkgs | wc -l` > 0 and
       that the shared cache's archive count is unchanged (count
       `ls /rs1/researchers/c/ckclinto/conda_pkgs/*.tar.bz2 /rs1/researchers/c/ckclinto/conda_pkgs/*.conda 2>/dev/null | wc -l`
       before and after). Record the PLINK binary path as `R4_PLINK=<env>/bin/plink` in the SUMMARY; W1 tests use it.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_osf_gate.py tests/ta_r4/test_track_b_isolation.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - both files pass with the heavy tests RUN (`-rs` shows no skip of a heavy test). The SUMMARY shows each RED run and the fixture production-refusal stderr containing `OsfGateError` and `sentinel absent`
    - `bash bin/r4_fire.sh production repro_routeC -n r4_gate_probe_repro; echo $?` prints a refusal and a non-zero exit (stage mismatch)
    - `$MAN/env_lock_{plink,qtl_processing,python_stats,r_coloc_named}.yml` exist and each contains a `dependencies:` key
    - the shared `/rs1/researchers/c/ckclinto/conda_pkgs` archive count is equal before and after the solve (both numbers in the SUMMARY)
    - `$MAN/compute_node_network_probe.tsv` has 2 data rows (submit host + LSF exec host)
  </acceptance_criteria>
  <done>The R4 workflow dry-runs; production refusal is proven on a sentinel-free fixture; envs are pinned with lockfiles; compute-node network reachability is recorded.</done>
</task>

<task type="auto">
  <name>Task 4: Wave-close (W0b2)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §A, §C
  </read_first>
  <action>
    If the implemented arm list differs from INDEX §A (13 arms), or the selected NC_NULL windows
    need recording there, correct §A to match `ARMS` and `regions_r4.csv` and record why in the LOG.
    Then run §C with label `W0b2`, commit type `feat`. Stage exactly this plan's `files_modified`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - QUICK and HEAVY green; `tests/m3` outcomes equal the W0a baseline (0 removed ids, 0 outcome changes, shown as a join)
    - `git log -1 --name-only` lists only paths from this plan's files_modified; `git push` exited 0
  </acceptance_criteria>
  <done>W0b2 committed and pushed; LOG and STATE updated.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GSD auto-mode → production compute | an auto-selected checkpoint must not be able to start the pre-registered comparison |
| OSF public API → submit host | the network response decides whether a fire may start |
| host receipt → LSF jobs | jobs trust a file written on the submit host |
| R4 config → Track B config | overlays must not leak into the base pipeline or build EUR chain members |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W0b2-01 | Elevation of privilege | r4_osf_gate | mitigate | git-tracked committed sentinel; amendment sha256 == sentinel == OSF API (online, per fire) == receipt (offline, per job); node az52u; no env/config bypass (AST + monkeypatch + signature tests); stage from code |
| T-r4-W0b2-02 | Spoofing | sentinel or receipt fabricated by an agent | mitigate | §B.12 forbids writing either in the real repo; the receipt is rewritten by verify-online at every fire and carries the raw API response sha256; the posting checkpoint is human-action |
| T-r4-W0b2-03 | Denial of service | OSF API rate limits / compute-node network | mitigate | one API call per fire on the submit host; jobs offline and memoized; network probe recorded |
| T-r4-W0b2-04 | Tampering | HEAD moves during a fire | mitigate | receipt binds HEAD; fire script refuses a dirty analysis tree and warns not to commit mid-fire; a mismatch fails closed |
| T-r4-W0b2-05 | Tampering | arm-dependent pair attrition | mitigate | static manifest, deterministic builders, sha256-pinned by test |
| T-r4-W0b2-06 | Tampering | silent panel substitution via the EUR chain | mitigate | chain replaced wholesale + pin; forbidden-substring isolation test over every arm × row |
</threat_model>

<verification>
- `pytest tests/ta_r4 -q` green, with RED evidence for each new module.
- A production refusal is observed on a sentinel-free fixture repo; the real-repo state test is conditional.
- The main Snakefile, pipeline.yaml and the frozen script are unchanged (`git diff --quiet`).
</verification>

<success_criteria>
The manifest (with three admissible negative-control sets) is fixed before data exists. Production
cannot run without a verified OSF posting, at a cost of one API call per fire.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0b2-pair-manifest-osf-gate-workflow-SUMMARY.md`
</output>
