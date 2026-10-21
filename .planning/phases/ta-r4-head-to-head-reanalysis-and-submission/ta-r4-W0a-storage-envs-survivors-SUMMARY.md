---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W0a-storage-envs-survivors
subsystem: storage / environment / test scaffold / decision record
tags: [ta-r4, durable-storage, rs1, survivors, sha256, conda, baseline, decisions]
requires: []
provides:
  - data/r4 symlink to /rs1 durable storage (bin/r4_link_storage.sh)
  - tests/ta_r4 scaffold (conftest with merged_config, r4_heavy marker) and storage enforcer
  - survivors_sha256.tsv (92 rescued known-answer files)
  - tests_baseline_W0a.tsv (1474 ids)
  - restored envs/qtl_processing.yml
  - DEC-2026-10-21 entries (E-2 fix, osf-correction-v2 retired, SH2B3 premise)
  - annotated tag ta-r4-pre-baseline on origin
affects: [W0b1, W0b2, every later ta-r4 wave (baseline comparison)]
tech-stack:
  added: []
  patterns: [repo-relative data/r4 symlink to /rs1, sha256 manifest per artifact class, RED-first enforcer with in-test negative controls]
key-files:
  created:
    - bin/r4_link_storage.sh
    - config/ta_r4/data_sources.yaml
    - tests/ta_r4/__init__.py
    - tests/ta_r4/conftest.py
    - tests/ta_r4/test_storage_on_rs1.py
    - envs/qtl_processing.yml
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/survivors_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/tests_baseline_W0a.tsv
  modified:
    - .gitignore
    - .planning/DECISIONS.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "Tag ta-r4-pre-baseline created before the first W0a commit (plan placed it in Task 2), so it marks the true pre-R4 HEAD 3a2c1add"
  - "CONDARC alone does not isolate pkgs_dirs; measured working recipe handed to W0b2; ~/.condarc not edited"
  - "Kept tests/ta_r4/__init__.py as planned; the measured ta_r4 package-name clash is handed to W0b1"
metrics:
  duration: "~65 min (2026-10-21T20:53Z start)"
  completed: 2026-10-21
  tasks: 3
  files: 13
---

# Phase ta-r4 Plan W0a: Storage, envs, survivors Summary

`data/r4` now points at /rs1 (2770). The 92 known-answer survivors that were exposed to the
`/share` purge are copied there and sha256-verified against their sources. `qtl_processing.yml`
is restored byte-identically, the test baseline (1474 ids, 0 failed) is committed, three DEC
entries are appended, and the annotated tag `ta-r4-pre-baseline` is on origin.

## Commits

| Task | Commit | Content |
|---|---|---|
| (T2 step 0, run first) | tag `ta-r4-pre-baseline` (object `09e7795f`) → `3a2c1add` | pre-R4 HEAD, pushed explicitly |
| 1 | `c8130c5a` | link script, .gitignore, tests/ta_r4 scaffold + enforcer, data_sources.yaml, survivors manifest |
| 2 | `c26d77ad` | envs/qtl_processing.yml, tests_baseline_W0a.tsv |
| 3 | `6f968b1b` | three DEC entries (append-only) |
| docs | (this commit) | LOG, STATE, ROADMAP, SUMMARY |

## Acceptance evidence (commands run, output as observed)

### Task 1
- `readlink -f data/r4` → `/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4`; `stat -c %a` on the root → `2770` (all 8 subdirs 2770 too; group `oit-rs-researcher-ckclinto`, inherited from the /rs1 parent dir, not `clintonlab`).
- `bash bin/r4_link_storage.sh; echo $?`, run twice: both print the same realpath and `0`. On a scratch fake repo with a real `data/r4` dir: `ERROR: ... exists and is not a symlink; refusing to touch it`, `refusal rc=2`, dir and its sentinel file untouched.
- `git check-ignore -q data/r4 && echo IGNORED` → `IGNORED`; `git diff HEAD -- .gitignore` → `+/data/r4` only (1 added, 0 removed); `git status --porcelain -- data/r4` → empty.
- **RED (before link, config and manifest existed)**, `$QUICK`:
  ```
  FAILED tests/ta_r4/test_storage_on_rs1.py::test_data_r4_realpath_on_rs1 - Ass...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed in 0.05s
  ```
  The same file without `-x`, `-rA`:
  ```
  E       AssertionError: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/data/r4
  E        +  where False = <function islink ...>((PosixPath('/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis') / 'data/r4'))
  E       AssertionError: scan covers no files
  E       AssertionError: no sha256 manifest under .../manifests
  E       FileNotFoundError: [Errno 2] No such file or directory: '.../config/ta_r4/data_sources.yaml'
  E       AssertionError: assert 1 == 0   (git check-ignore data/r4)
  PASSED tests/ta_r4/test_storage_on_rs1.py::test_check_function_rejects_share_target
  FAILED tests/ta_r4/test_storage_on_rs1.py::test_data_r4_realpath_on_rs1
  FAILED tests/ta_r4/test_storage_on_rs1.py::test_data_r4_is_a_symlink_not_a_dir
  FAILED tests/ta_r4/test_storage_on_rs1.py::test_no_rs1_or_share_literals_in_r4_config_and_src
  FAILED tests/ta_r4/test_storage_on_rs1.py::test_manifests_parse
  FAILED tests/ta_r4/test_storage_on_rs1.py::test_data_sources_public
  FAILED tests/ta_r4/test_storage_on_rs1.py::test_data_r4_gitignored
  6 failed, 1 passed in 0.15s
  ```
- **GREEN:** `pytest tests/ta_r4/test_storage_on_rs1.py -q` → `7 passed in 0.16s`.
- **Negative controls seen biting.** Each checker was replaced by a blind stub in-process and its test run: storage blind → RED; literal blind → RED; manifest blind → RED; data-source blind → RED; `BANNED_LITERALS=()` → RED. A real `config/ta_r4/zz_nc_probe.yaml` containing `/share/clintonlab/x` → `1 failed` (`... zz_nc_probe.yaml: /share/clintonlab`); after removal → `1 passed`.
- N_SRC = `92` (find over the 6 lsweep backups + stage2_narrow_validation + `coloc_susie_R2*` `-type f`, plus the zip; 0 symlinks among the sources). `awk 'NR>1' survivors_sha256.tsv | wc -l` → `92`; `grep -cvE '^[0-9a-f]{64}$'` on column 3 → `0`. By source: 24 lsweep (6×4) + 46 stage2_narrow_validation + 21 coloc_susie_R2* + 1 zip = 92. The destination file list equals the source list (`diff` empty). `diff` of the source and copy sha256 lists → empty (`ALL_SHA_MATCH`), and every size is equal. Total 123,987,565 bytes; 19 `.rds` (10 real + 7 identity fits + 2 `*_test.rds`).
- data_sources check (`$PY -c "import yaml;...assert all(...)"`) → `14 sources OK`, exit 0.

### Task 2
- `cmp <(git show c2dfb08^:envs/qtl_processing.yml) envs/qtl_processing.yml && echo IDENTICAL` → `IDENTICAL`. `src/snakemake/rules/envs` → `../../../envs` (symlink), so the file resolves through it.
- Tag: `git rev-parse ta-r4-pre-baseline^{commit}` → `3a2c1add3540e8a30e7a7bb48615a1e1f17e4be3`; `git ls-remote origin 'refs/tags/ta-r4-pre-baseline*'` → `09e7795f… refs/tags/ta-r4-pre-baseline` and `3a2c1add… refs/tags/ta-r4-pre-baseline^{}` (the shas are equal); `git cat-file -t ta-r4-pre-baseline` → `tag`. `fsck --connectivity-only` before the tag: 0 missing/broken (dangling blobs only).
- **Conda isolation: acceptance criterion NOT met as written** (see Deviations): `CONDARC=…/ta_r4/condarc conda config --show pkgs_dirs` →
  ```
  - /rs1/researchers/c/ckclinto/conda_pkgs
  - /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/pkgs
  - /rs1/researchers/c/ckclinto/miniconda3/pkgs
  ```
  `CONDA_PKGS_DIRS=…/ta_r4/pkgs HOME=…/ta_r4/home CONDARC=…/ta_r4/condarc conda config --show pkgs_dirs` → exactly `- /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/pkgs`.
- Baseline: `awk -F'\t' 'NR>1{c[$2]++} END{for(k in c) print k,c[k]}' tests_baseline_W0a.tsv` → `skipped 46`, `passed 1428`. Totals line: `1428 passed, 46 skipped, 4 warnings in 967.31s (0:16:07)`. Collected 1474 = 1428 + 46. tests/m3 subtotal is 1299 / 1265 / 34, equal to the 2026-09-19 record. No failures at baseline.
  - Method: `-rA` lists skips grouped by location (`SKIPPED [N] file:line`), not by id. Skipped ids are therefore the collected ids minus the PASSED ids. Per-file skip counts equal the `SKIPPED [N]` sums for all 11 files. The 7 `ERROR …` lines in the log are captured log output from passing tests, not outcomes.

### Task 3
- `git diff HEAD~1 -- .planning/DECISIONS.md | grep -c '^-[^-]'` → `0`; `grep -c '^## 2026-10-21 — DEC-2026-10-21-' .planning/DECISIONS.md` → `3`.
- The D-19 entry cites the exact heading `DEC-2026-08-12-e2-p1-closing-sentence` (DECISIONS.md:1862). The D-17 entry cites `ta-sh2b3-W2-…-SUMMARY.md:155` (the L=15 swap; 3+2 split) and `:102` (BMI fit L=15/niter=1000), both checked by reading.
- `test_source_freeze_pins.py` → `39 passed`.
- QUICK → `7 passed` (32 s wall on the first cold run, 0.36 s warm; under 120 s). HEAVY → `7 deselected`, exit 5 (no r4_heavy tests exist yet). `--markers` lists `@pytest.mark.r4_heavy`.
- FULL → `1435 passed, 46 skipped, 4 warnings in 889.35s`. Join vs `tests_baseline_W0a.tsv`: common 1474, **removed 0, added 7 (all tests/ta_r4/test_storage_on_rs1.py, passed), outcome changes 0**.
- fsck before and after the T3 commit: 0 missing/broken. `git push origin m3-W2-aou-deltas` → `3a2c1add..6f968b1b`, exit 0. `git status --porcelain -- envs/qtl_processing.yml config/ta_r4 tests/ta_r4 bin/r4_link_storage.sh` → empty.

## Deviations from Plan

1. **[Ordering] Tag before Task 1.** The plan puts the tag in Task 2 step 0 and assumes "nothing has been committed by this phase's execution yet". With per-task commits that would have tagged the Task 1 commit. The tag was created first, on `3a2c1add`, which is the pre-R4 HEAD the plan intends.
2. **[Plan premise false — measured, not fixed] CONDARC alone does not isolate `pkgs_dirs`.** Conda always reads `~/.condarc` (its `pkgs_dirs` lists the shared cache), and `~/.bashrc` exports `CONDA_PKGS_DIRS=/rs1/.../conda_pkgs`. Sequence parameters merge across sources, and `#!final` can only block higher-precedence files, never lower ones. Verified in the conda 26.1.1 source. The condarc was written exactly as specified. The measured working recipe is `CONDA_PKGS_DIRS=$R4_CONDA_PREFIX/pkgs HOME=$R4_CONDA_PREFIX/home CONDARC=$R4_CONDARC` (`$R4_CONDA_PREFIX/home` created, empty). It drops `~/.condarc`'s `channel_priority: strict` and `solver: libmamba`, so W0b2 must restore those in the R4 condarc or accept the solve change. Mitigating fact, also measured: Snakemake 7.32.4's `--conda-cleanup-pkgs` defaults to None (it runs `conda clean --tarballs` only when the flag is passed); the 2026-10-11 incident was Snakemake 9.x. `~/.condarc` was not edited (user config).
3. **[Hand-off, not fixed] `ta_r4` package-name clash.** `tests/` has no `__init__.py`, so `tests/ta_r4/__init__.py` makes pytest import the test dir as the top-level package `ta_r4`. W0b1 creates `src/python/ta_r4/`. Measured on a scratch mock (pytest 9.0.3): `from ta_r4.paths import X` → `ModuleNotFoundError: No module named 'ta_r4.paths'`, in either run order. Dropping the `__init__.py` instead makes `tests/ta_r4/conftest.py` the bare `conftest` module. That breaks the tests/m3 `from conftest import R_SUBPROCESS_TIMEOUT_S` imports (`ImportError: cannot import name ...`), also measured. Kept as planned, because W0a's tests do not import `ta_r4`. W0b1 must choose a resolution (for example a different src package name, or a `pkgutil.extend_path` in `tests/ta_r4/__init__.py`) before its first `from ta_r4...` test.
4. **[Detail] Baseline log split.** stdout went to `data/r4/logs/tests_baseline_W0a.log`, and `/usr/bin/time -v` stderr to `tests_baseline_W0a.time` (16:09.93 wall, 4.17 GB max RSS), instead of `2>&1 | tee`.
5. **[Rule 2] Survivor permissions.** `chmod -R g+rwX,o-rwx` on `data/r4/known_answer_survivors/` (T-r4-W0a-03); 0 world-readable files afterwards.

## Known Stubs

`config/ta_r4/data_sources.yaml`: `onekg_phase3_vcf.url` = `data/r4/inputs/1kg_vcf`, which is a W2b symlink and does not exist yet (intentional per plan). `checksum: null` where no checksum is published.

## Threat Flags

None. No new network endpoints or auth paths. /rs1 dirs are 2770.

## Self-Check: PASSED
