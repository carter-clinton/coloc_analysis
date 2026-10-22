---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W0b2-pair-manifest-osf-gate-workflow
subsystem: pair manifest / negative controls / OSF gate / standalone R4 workflow / job envs
tags: [ta-r4, negative-controls, gwas-null, pair-manifest, osf-gate, snakemake, lsf, conda-isolation, lockfiles]
requires: [ta-r4-W0b1-arms-paths-overlays-signoff]
provides:
  - config/ta_r4/regions_r4.csv (31 rows = 12 curated + 9 cosmetic/blood_group + 10 GWAS-null)
  - config/ta_r4/pair_manifest.tsv (346 rows, 320 admissible; static, deterministic, no tier gate)
  - src/python/ta_r4/select_null_windows.py, build_pair_manifest.py
  - src/python/ta_r4/r4_osf_gate.py (verify_online once per fire on the submit host; check_osf_gate offline + memoized)
  - Snakefile.ta_r4 (standalone; includes src/snakemake/rules/ta_r4_*.smk in sorted order)
  - bin/r4_fire.sh (the only supported entry; conda-isolated; production -> verify-online first)
  - config/ta_r4/cluster_lsf profile (logs under data/r4/logs/lsf, jobs 200, conda-frontend conda)
  - tests/ta_r4/fixtures/make_fixture_repo.py (sentinel-free fixture repo from the working tree)
  - env lockfiles for plink / qtl_processing / python_stats / r_coloc (named)
  - R4_PLINK=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin/plink
affects: [W0c, W0d, W1 (R4_PLINK), W2a-W2d (panel rules add ta_r4_*.smk), W4a (discloses the null-window rule), W4b (posting gate: OSF anonymous-read finding), every production fire]
tech-stack:
  added: []
  patterns: [standalone Snakefile with sorted include of ta_r4_*.smk, DAG-time input-function gate, per-HEAD host receipt, fixture-repo dry-run tests, CONDA_PKGS_DIRS+HOME+CONDARC isolation]
key-files:
  created:
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
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_{plink,qtl_processing,python_stats,r_coloc_named}.yml
  modified:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "R4 condarc uses channel_priority flexible: envs/plink.yml (bioconda listed first) is UNSATISFIABLE under strict with today's repodata (measured twice: the stopped executor's log and a scratch dry-run); flexible solves. Lockfiles pin the result."
  - "R4 profile pins conda-frontend conda: Snakemake 7.32.4 defaults to mamba (found in miniconda3/condabin, which r4_fire.sh prepends); the pkgs_dirs isolation was measured for conda only."
  - "bin/r4_fire.sh creates data/r4/logs/lsf: config/bsub_wrapper.sh only creates logs/lsf, and the R4 profile writes LSF logs under data/r4."
  - "run_susie_rss.R (current and 3dd76df) looks a region up by region_id ONLY (`regions[region_id == opt$region][1]`), so no AFR duplicate rows were added to regions_r4.csv."
  - "OSF anonymous-read finding (not fixed; hand-off): api.osf.io returns 401 for node az52u and file k8w7n without credentials, while registration pvb5j is public (200). verify_online is anonymous by design (reads no env vars), so it fails closed (i) for any file on a non-public node."
metrics:
  duration: "resume session ~50 min (2026-10-22T14:58Z-15:50Z); T1-T2 were committed 2026-10-21"
  completed: 2026-10-22
  tasks: 4
  files: 21 code/config/test/manifest + PLAN-INDEX/LOG/STATE/ROADMAP/SUMMARY
---

# Phase ta-r4 Plan W0b2: Pair manifest, OSF gate, R4 workflow Summary

The pre-registered all-pairs manifest is fixed before any data exist. It has 346 rows, 320 of them
admissible, and three admissible negative-control sets: cosmetic, blood_group, and 10 seeded
GWAS-null windows. The OSF gate costs one API call per production fire, made on the submit host.
Every DAG evaluation and every LSF job then re-checks offline against a per-HEAD receipt, and the
check fails closed. Production refusal is proven on a fixture repo that has no sentinel.
`Snakefile.ta_r4` and `bin/r4_fire.sh` run the R4 workflow separately from Track B. The three job
envs were solved from scratch into the R4 prefix with the shared conda cache untouched, and their
lockfiles are committed.

## Commits

| Task | Commit | Content |
|---|---|---|
| 1 | `9bb65c01` | regions_r4, select_null_windows, build_pair_manifest, pair_manifest, null_windows_selection, 2 test modules (committed 2026-10-21 by the stopped executor) |
| 2 | `ab77e97c` | r4_osf_gate + unit tests (committed 2026-10-21 by the stopped executor) |
| 3 | `2d4da61e` | Snakefile.ta_r4, ta_r4_env.smk, r4_fire.sh, LSF profile, fixture repo, gate dry-run + isolation tests, probe TSV, 4 env lockfiles |
| 4 | wave-close commits | PLAN-INDEX §A, LOG, STATE (feat); SUMMARY + ROADMAP (docs) |

## Resume handling

Tasks 1–2 were already committed. Their tests were re-run first: T1 `28 passed` (197 s are the
r4_heavy real-data rerun), and T2 is covered by the Task 3 run below. The Task 3 WIP was read line by line
against the spec. It conformed (Snakefile guard, imports, safe-id rule, `gate_input`, the two probe
rules, sorted include, env probes, fire-script stage check / dirty-tree refusal / verify-online /
exec line, profile copy, fixture copy set, all listed behaviours), with three gaps fixed (see
Deviations 1–3). The stopped executor's evidence for T1 and T2 was never written down. The parts
that can be reproduced were re-derived here (RED runs, the (o)-skip control, the arithmetic, the
run_susie_rss lookup). The part that cannot be reproduced is the k8w7n dict (see Deviation 5).

## Acceptance evidence (commands run, output as observed)

### Task 1 (re-verified)
- `awk 'NR>1' config/ta_r4/pair_manifest.tsv | wc -l` → 346. The header has `admissible` at column 8,
  and `$8=="true"` gives **320**. `awk -F, 'NR>1' config/ta_r4/regions_r4.csv | wc -l` → **31**.
- Arithmetic. Rows by class: primary EUR 120 (12 × 10) + primary AFR 36 (12 × 3) + negative_control
  190 = **346**. Inadmissible: HLA_6p21 EUR 10 + AFR 3, BMI_Xq24 EUR 10 + AFR 3 = 2×10 + 2×3 = **26**,
  and 346 − 26 = **320**. NC by set: cosmetic 50 + blood_group 40 + gwas_null 100 = 5×10 + 4×10 + 10×10 = **190**.
  ABO: 10 rows with `nc_caveat=reported_stroke_association_verify`. `canonical_pair=true`: 17 rows.
- n_candidates = **2865**. candidates sha256 = `352c77ec…dcce9`. Rule: `window=250000 pmax=1e-05 min_variants=200 n_select=10 seed=20261021`.
  The 10 selected windows (GRCh37, start–end):
  NC_NULL_01 1:99500001-99750000, NC_NULL_02 1:218750001-219000000, NC_NULL_03 2:190000001-190250000,
  NC_NULL_04 3:30750001-31000000, NC_NULL_05 3:178250001-178500000, NC_NULL_06 6:81500001-81750000,
  NC_NULL_07 11:21500001-21750000, NC_NULL_08 13:38500001-38750000, NC_NULL_09 13:71000001-71250000,
  NC_NULL_10 14:49000001-49250000.
- **run_susie_rss region lookup.** It is by `region_id` only, in both the current frozen script
  (`reg <- regions[region_id == opt$region][1]`, line 762) and `3dd76df` (line 266). There is no
  ancestry filter, so no AFR duplicates are needed.
- **RED (re-derived).** `select_null_windows.py` and `build_pair_manifest.py` were moved aside and the
  tests run: `E ImportError: cannot import name 'select_null_windows' from 'ta_r4'` and `... 'build_pair_manifest' ...`,
  i.e. collection errors. The files were restored and `sha256sum -c` gave OK.
- `pytest tests/ta_r4/test_null_windows.py tests/ta_r4/test_pair_manifest.py -q` → `28 passed`.
  The slowest test is `test_real_selection_reproduces_committed` (197 s, already `r4_heavy`).

### Task 2 (re-verified)
- **RED (re-derived).** `r4_osf_gate.py` was moved aside: `E ImportError: cannot import name 'r4_osf_gate' from 'ta_r4'`, a collection error. Restored, and `sha256sum -c` gave OK.
- **(o)-skip negative control.** `if rc.get("head_sha") != head:` was changed to `if False and ...`. Result:
  `FAILED test_o_receipt_head_sha - Failed: DID NOT RAISE` and `FAILED test_env_vars_do_not_change_pass`,
  `2 failed, 46 passed, 4 deselected`. Restored (`cmp` identical) → `48 passed, 4 deselected`.
- AST check `sum(... n.attr in ('environ','getenv'))` → **0**.
- **k8w7n parsed dict: NOT obtainable** (see Deviation 5). `fetch_osf_file('k8w7n')` raises
  `HTTPError 401: Unauthorized`. `curl` returns `{"errors":[{"detail":"Authentication credentials were not provided."}]}`
  for `/v2/files/k8w7n/`, for `/v2/nodes/az52u/`, and for the file id `69ed77efdd1c6c083fda8961` that `/v2/guids/k8w7n/` redirects to.
  `/v2/registrations/pvb5j/` → 200, `public: True`. The parser is therefore pinned only by the synthetic
  `test_parse_osf_file_response`, which reads `relationships.target.data.id` with an href fallback.

### Task 3
- **RED.** `Snakefile.ta_r4`, `bin/r4_fire.sh`, `ta_r4_env.smk` and `config/ta_r4/cluster_lsf/` were moved to scratch:
  `9 failed, 55 passed, 3 errors`. Failed: the sentinel+receipt fixture dry-run, `test_r4_rules_never_call_ld_matrix_region_id`,
  `test_dry_run_shell_commands_isolated`, `test_fire_conda_pkgs_dirs_is_exactly_the_r4_cache`, and all 5 `test_fire_refusals`.
  Errors: the 3 module-fixture dry-run tests (FileNotFoundError). Restored, and `sha256sum -c` gave OK for all 5 files.
- **GREEN on the unmodified WIP:** `67 passed in 18.94s`.
- **Negative controls for every assertion that passed without the implementation, plus the gate call itself** (each restored, `cmp` identical):
  - NC1: `check_osf_gate(...)` removed from `gate_input` → `test_fixture_production_dry_run_refuses` RED
    (the dry-run fails only with `MissingInputException ... Missing input files for rule r4_gate_probe`, with no OsfGateError).
  - NC2: CLI `check` returns 0 on OsfGateError → `test_real_repo_state` RED (`assert 0 == 1`).
  - NC3 (in-process): resolve with the base config (no overlay) → `test_r4_paths_independent_of_crosswalk` RED
    (`FileNotFoundError: No LD panel found for FTO_16q12 EUR`).
  - NC4 (in-process): `NC_NULL_01` injected into the crosswalk → `test_nc_ids_absent_from_crosswalk` RED.
  - NC5: `ls data/processed/ld_reference/` injected into the plink probe shell → `test_dry_run_shell_commands_isolated` RED
    (`['data/processed/ld_reference/'] == []`).
  - NC6: an `ld_matrix_region_id` name in `ta_r4_env.smk` → `test_r4_rules_never_call_ld_matrix_region_id` RED.
  - The isolation test's own in-test control (`test_isolation_check_reports_a_track_b_panel`) passes.
- **Fixture production refusal** (fixture repo `78182c9 fixture from working tree`, no sentinel):
  `$SMK r4_gate_probe -s Snakefile.ta_r4 -d . -n --configfile ...overlay_A3_1kg.yaml` → rc=1, output:
  ```
  InputFunctionException in rule r4_gate_probe in file .../fixture_repo/Snakefile.ta_r4, line 66:
  Error:
    OsfGateError: (a) sentinel absent: .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json
  ```
  The traceback runs through the fixture's own `src/python/ta_r4`. The repro arm with target `r4_gate_probe_repro` → rc=0.
- `bash bin/r4_fire.sh production repro_routeC -n r4_gate_probe_repro; echo $?` →
  `REFUSED: arm repro_routeC is stage 'repro', not 'production'`, then `2`.
- **Env solve from scratch.** First the prefix was confirmed to be `/rs1/.../smk_job_envs/ta_r4`. Then the stale `55c377a7…_.yaml`, `pkgs/`, `home/` and `condarc` were removed (0 entries left; no env dir had been created).
  `bash bin/r4_fire.sh repro repro_routeC r4_env_probe_all --conda-create-envs-only --cores 1` → rc=0 in 10m08s,
  which created qtl_processing `dc880444…_`, plink `55c377a7…_` and python_stats `8f7292f9…_`.
  `bash bin/r4_fire.sh repro repro_routeC r4_env_probe_all --cores 1 --profile ''` → **`--profile ''` accepted**
  (the jobs ran as `localrule`), `4 of 4 steps (100%) done`, rc=0, 24.8 s. Probe outputs:
  - plink: `<R4>/55c377a7…_/bin/plink`; `PLINK v1.90b6.21 64-bit (19 Oct 2020)`; `PLINK v2.00a5.12LM`; `bcftools 1.21`
  - qtl_processing: python 3.11.17, pysam 0.24.1, pandas 3.0.6; `tabix (htslib) 1.24`
  - python_stats: python 3.11.17, numpy 1.26.4, pandas 2.2.3, scipy 1.14.1; snakemake 7.32.4
  - **R4_PLINK=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin/plink**
- Lockfiles (`conda env export --no-builds -p <dir>`, run under the same isolation): env_lock_plink.yml 110 lines,
  qtl_processing 186, python_stats 252, r_coloc_named 224. Each has exactly 1 `dependencies:` key.
  Key pins: plink=1.90b6.21, plink2=2.00a5.12, bcftools=1.21 / htslib=1.24 (plink env), r-base=4.4.3;
  r_coloc: r-base=4.4.2, r-susier=0.14.2, r-coloc=5.2.3.
- **Shared cache** (`/rs1/researchers/c/ckclinto/conda_pkgs`). Archive count (`*.tar.bz2 *.conda`) **before 0, after 0**.
  Because 0 = 0 is a weak test, two stronger measures were also taken: entries before 2188 / after 2188, with an identical
  listing sha256 (`f094b37d…9085`); du 23348M / 23348M; no entry newer than the session start.
  The R4 cache `smk_job_envs/ta_r4/pkgs` holds 809 entries (403 archives), i.e. > 0.
  `bash bin/r4_fire.sh --show-conda-pkgs-dirs` lists exactly the R4 pkgs dir.
- **Network probe.** `compute_node_network_probe.tsv` has 2 data rows. The LSF row was verified against
  `data/r4/logs/net_probe.404985.{out,err}`: job 404985, exec host c017n03, serial queue, output `000 curl_exit=28`,
  stderr `curl: (28) Connection timed out after 20004 milliseconds`, started 18:28:45 EDT = 22:28:45Z, matching the row.
  The submit-host row (login01, 200) has no log, so it was re-measured on today's submit host:
  `login03.hpc.ncsu.edu 2026-10-22T15:12:55Z 200 curl_exit=0`. The TSV is unchanged. The design does not depend on either row.
- Verify command `pytest tests/ta_r4/test_osf_gate.py tests/ta_r4/test_track_b_isolation.py -q -rs` → **67 passed**,
  with no skips and all 5 heavy tests run (`-m r4_heavy` → `5 passed, 62 deselected`).

### Task 4 (wave close, §C)
- QUICK `time $PY -m pytest tests/ta_r4 -x -q -m 'not r4_heavy'` → `180 passed, 6 deselected`, real **24.9 s**
  (measured while FULL was running). HEAVY → `6 passed, 180 deselected` (204 s). `test_source_freeze_pins.py` → `39 passed`.
- FULL (`tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q -rA --junitxml`) → `1614 passed, 46 skipped, 4 warnings in 1149.45s`, rc 0.
  Join by id (from the junit XML) vs `manifests/tests_baseline_W0a.tsv`: collected **1660**, baseline 1474, common 1474,
  **removed 0, added 186, outcome changes 0**. Added by file: osf_gate 52, signoff 35, overlay_semantics 25,
  signoffs 22, null_windows 15, track_b_isolation 15, pair_manifest 13, storage_on_rs1 7, import_isolation 2. All 186 passed.
  1474 + 186 = 1660, and 1428 + 186 = 1614. tests/m3: 1299 baseline ids, 0 missing, 0 changed.
  `tests/m3/sparse_parent_benchmark.tsv` was restored after the run.
- `git diff --quiet HEAD -- Snakefile config/pipeline.yaml src/legacy/region_analysis/scripts/run_susie_rss.R src/snakemake/rules/finemap.smk` → 0.
- No real sentinel, no `data/r4/gate/`, and no `carter-approved` text were written.

## Deviations from Plan

1. **[Rule 3 — blocking] `channel_priority: flexible` in the R4 condarc (the orchestrator decision said strict).**
   Under strict, `envs/plink.yml` (bioconda listed first) is unsatisfiable today. This is what stopped the
   previous executor's solve: `LibMambaUnsatisfiableError ... bcftools-1.21 requires htslib >=1.21,<1.25 ...
   r-base 4.4.3 requires libdeflate >=1.25` (c-ares/libnghttp2 chain). Reproduced in a scratch prefix (strict rc=1),
   and flexible rc=0 (c-ares/libdeflate from conda-forge, htslib 1.24 from bioconda). `~/.condarc` would hit the same failure;
   W0a had already noted that this choice was open. PLAN-INDEX §A records it. The lockfiles pin what was solved.
   Snakemake prints its "not configured to use strict channel priorities" warning; that is expected.
2. **[Rule 2 — isolation] `conda-frontend: conda` in the R4 profile.** Snakemake 7.32.4 defaults to mamba, which
   it finds in `miniconda3/condabin`, and the stopped executor's first attempt did run `mamba env create`. The pkgs_dirs
   isolation was measured for conda only.
3. **[Rule 2] `mkdir -p data/r4/logs/lsf` in `bin/r4_fire.sh`.** `config/bsub_wrapper.sh` creates only `logs/lsf`, while the
   R4 profile writes `-o/-e` under `data/r4/logs/lsf`.
4. **[Measured] Snakemake 7.32.4 prints the DAG-time `OsfGateError` on stdout, and stderr is empty** (0 lines). The plan says
   "stderr contains OsfGateError". The tests therefore assert on stdout + stderr. Both `OsfGateError` and
   `sentinel absent` are asserted.
5. **[Unverifiable; hand-off] The k8w7n known-answer dict could not be obtained.** OSF's API refuses anonymous reads of node
   az52u and its file k8w7n (401), while registration pvb5j is public. Consequences:
   (a) the target-node JSON path is pinned only by a synthetic response;
   (b) `verify_online` makes an anonymous GET by design (no env vars, no token), so a production fire will fail closed at (i)
   unless the R4 amendment is on a node the API serves anonymously.
   (c) This also bears on how public the existing az52u amendments really are. That is Carter's call, and nothing was changed.
   **W4b (posting gate) must confirm an anonymous `curl https://api.osf.io/v2/files/<guid>/` returns 200 before Carter
   writes the sentinel.** If the posting must stay non-public, authenticated reads would be a design change (Rule 4) and
   must not be added silently.
6. **[Evidence gap, partly closed] The stopped executor's T1/T2 RED runs were not recorded.** They were re-derived after the
   fact (modules moved aside), together with the (o)-skip control. These re-derivations show that the tests discriminate. They do
   not show that the tests were written first.
7. **[Detail] The probe TSV has an extra `note` column, and `host` holds a label (`submit_host`, `lsf_serial_job_404985`)**, with the
   hostname in `exec_host`. Kept as is.
8. **[Detail] `test_track_b_isolation.py` also covers `bin/r4_fire.sh`** (refusals, `--show-conda-pkgs-dirs`), and the fire script
   refuses `--conda-cleanup-pkgs`. `r4_gate_probe_repro` raises WorkflowError for a production arm.

## Hand-offs

- **W1:** `R4_PLINK` (above).
- **Later rule plans:** add `src/snakemake/rules/ta_r4_*.smk` only; rule names must be unique. Jobs inherit
  `HOME=$R4_CONDA_PREFIX/home` from `bin/r4_fire.sh`, so `~/.Rprofile` and user R libraries are NOT visible in R4 jobs. Use conda envs.
- **W4b:** see Deviation 5 (anonymous API readability of the posted file and node).
- **Requirements:** REQ-OSF-PREREG / REQ-SNAKEMAKE-CI / REQ-PATH-PARAMETERIZATION / REQ-NEGATIVE-CONTROLS are
  cross-track ([AB]) and span milestones. This plan contributes to them; none is marked complete.

## Known Stubs

None. `r4_env_probe_*` are probes by design.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: network | src/python/ta_r4/r4_osf_gate.py | outbound anonymous GET to api.osf.io from the submit host (in the threat model, T-r4-W0b2-03); currently returns 401 for node az52u (Deviation 5) |
| threat_flag: env-override | bin/r4_fire.sh | exports HOME/CONDA_PKGS_DIRS/CONDARC for the Snakemake process and all LSF jobs (isolation; changes the home that jobs see) |

## Self-Check: PASSED

The files listed above exist and are tracked at `2d4da61e`. Commits `9bb65c01`, `ab77e97c` and `2d4da61e` exist.
The QUICK, HEAVY, FULL and freeze-pin numbers are the ones observed above.
