---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8b
slug: W3f-openblas-pin-and-guard
type: execute
wave: 15.8b
depends_on: ["ta-r4-W3f-sumstats-orientation-eligibility-and-draft"]
gap_closure: true
files_modified:
  - envs/r_coloc.yml
  - envs/r_coloc.linux-64.pin.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_job.tsv
  - src/python/ta_r4/conda_job_env.py          # the one job-env locator (Task 1, the fixture, tests 8-11)
  - src/python/ta_r4/job_guard.py
  - tests/ta_r4/test_job_guard_blas.py
  - tests/ta_r4/test_job_guard.py              # `_check` helper (fixture builder) + test_guard_writes_the_record (declared)
  - tests/ta_r4/fixtures/qtl_group_fixture.py  # `_job_env` uses the locator (fixture-builder edit)
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates Q-157J and Q-158R6S (`Proceed, pin r_coloc only (Recommended)`, sha256 7b3d1045…5b2d) pass (15.8 protocol); otherwise nothing is edited"
    - "Only envs/r_coloc.yml (shared with Track B and m3) gains a pin and a pin file; python_stats, plink and qtl_processing are not pinned (Carter Q-158R6S); the guard fails closed if any gated r4 job env drifts from the pin; the SUMMARY and LOG record the measured number of r_coloc rules outside ta_r4 (plan-checker: 23), that Track B and m3 rebuild their r_coloc env on their next Snakemake run from the same pin file at the same libopenblas version, and that bin/setup-envs.sh's phase-2 fallback walks only staged *.yaml files, so on that path Track B solves the yaml, not the pin file (libopenblas version held by the pin line; build strings not held)"
    - "One locator, `conda_job_env.job_env_dir(yml, prefix)` = `<prefix>/<md5(realpath(prefix) + yaml bytes)>_`, equal to Snakemake 7.32.4's own Env(...).address for the same yaml and conda prefix (test 8); it raises if `envs/r_coloc.post-deploy.sh` exists (a post-deploy script enters Snakemake's hash); it is used by Task 1, the qtl_group_fixture and tests 8-11; before the edit it returns 0f3436279d4146c376747a0ea5bfd4bf_ (the env the jobs and the 17 kernel-experiment runs used)"
    - "Measured before any edit, in a Cascade Lake Slurm job, in that env activated with `source /rs1/researchers/c/ckclinto/miniconda3/bin/activate <env>` (as Snakemake's shellcmd does): conda-meta libopenblas version and build; realpaths of lib/libblas.so.3, liblapack.so.3, libcblas.so.3; R's extSoftVersion()['BLAS'] and La_library() realpaths; openblas_get_config() and openblas_get_corename(); the OPENBLAS_VERBOSE=2 'Core:' line; sha256 of lib/libopenblasp-r<ver>.so; and the conda-meta libopenblas of every env of a gated production rule"
    - "One conda binary, /rs1/researchers/c/ckclinto/miniconda3/condabin/conda, makes the pin file and every explicit list in Task 3 and test 10. envs/r_coloc.yml pins `libopenblas=<the measured version>`; envs/r_coloc.linux-64.pin.txt is `conda list --explicit --md5 -p <0f343627 env>`; manifests/env_lock_r_coloc_job.tsv lists every conda-meta package (name, version, build string, channel, md5) of that env, the libopenblas .so sha256 and the measured corename"
    - "Env identity, with no fit run, checked by `$Q8/env_identity_15_8b.py <env dir>` (exit 0 = identical): for D = job_env_dir(envs/r_coloc.yml) after the build, `str(D) + \".pin.txt\"` is cmp-equal (byte-exact) to envs/r_coloc.linux-64.pin.txt; `str(D) + \".yaml\"` is absent; the build log has 'Using pinnings from' and not 'Failed to install'; the `@EXPLICIT` URL#md5 lines of `conda list --explicit --md5 -p D` equal those of the repo pin file (the `# created-by` header is not compared); D's libopenblasp-r<ver>.so sha256 equals the measured env's; `ls D/lib/R/library` equals the measured env's. Its negative control: the same script on the old env 0f343627 (which has `_.yaml` and no `_.pin.txt`) exits non-zero. Any difference on D is a STOP for Carter (Q-158R6)"
    - "job_guard.check(…, blas_probe=None, r_blas_probe=None) refuses a production job when: CONDA_PREFIX is unset; conda-meta has no or several libopenblas records or a version other than the pin; libblas.so.3 / liblapack.so.3 do not resolve to that env's libopenblasp-r<pin>.so; the runtime config's version token is not exactly the pin (`config.split()[1] == pin`, not a prefix match); `$CONDA_PREFIX/bin/Rscript` is missing (a violation, not a skip); or the BLAS R itself reports (`Rscript -e 'cat(extSoftVersion()[[\"BLAS\"]])'`, R loads it in its own process; the guard never dlopens it) resolves to another file. Both probes are injectable. The pin is read from envs/r_coloc.yml; the record gains a `blas` block and checked.blas_pinned = true"
    - "DRAFT (k) says production jobs refuse an OpenBLAS library other than the pinned version; old string asserted unique"
    - "The shared cache /rs1/researchers/c/ckclinto/conda_pkgs is unchanged by the build: its entry count and the sha256 of its sorted `ls` are equal before and after"
  artifacts:
    - path: "envs/r_coloc.linux-64.pin.txt"
      provides: "exact package set of the r4 R job env"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_job.tsv"
      provides: "the job env's own lock and its measured OpenBLAS corename (env_lock_r_coloc_named.yml describes the named env, not the job env)"
    - path: "src/python/ta_r4/conda_job_env.py"
      provides: "the Snakemake job-env locator"
  key_links:
    - from: "job_guard.check"
      to: "envs/r_coloc.yml libopenblas pin"
      via: "pin parsed at check time; CONDA_PREFIX conda-meta + realpath + subprocess probe + Rscript BLAS"
      pattern: "libopenblas"
---

<objective>
Close review R6 as Carter chose (Q-157J "R6: pin libopenblas"; Q-158R6S). The job guard checks the CPU but not the BLAS
library, and the committed env lock describes the named r_coloc env (OpenBLAS 0.3.32), while jobs run in the
Snakemake-built env (0.3.34). This plan measures what the jobs load, pins it in envs/r_coloc.yml with an exact pin file,
records the job env's lock, and makes the guard refuse any other BLAS. The rebuilt env is proven identical to the
measured one by its package list and library hash, with no fit run (a new pre-lock fit would fall outside the approved
F15 paragraph's "17 runs"); any difference stops for Carter.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: as in ta-r4-W3f-collector-drop-audit-PLAN.md <question> (sha256 805afcd8…503e; free text "… R6: pin  libopenblas …").
Q-158R6S (answered 2026-11-25): file `W3f-carter-15-8-Q-158R6S-reply-2026-11-25.txt`, sha256
`7b3d1045f770bdea49123a85d58866501a46dbe62b0d9ddf5f9ac6bf36875b2d`, label `Proceed, pin r_coloc only (Recommended)`;
question text in 15.8a's <question> table.
Task 3 question (only on a STOP), QID Q-158R6, file `W3f-carter-15-8-Q-158R6-reply-<date>.txt`: "The env Snakemake built
for the libopenblas pin differs from the env the jobs and the 17 kernel-experiment runs used (diff of package URLs and
md5s, or the OpenBLAS library hash). How should 15.8b proceed?" Labels: `A: Do not pin yet; find why the pin file did
not reproduce the env (new plan)` / `B: Accept the rebuilt env and record the change (re-measure the kernel experiment
in a new plan, disclosed as pilot runs)` / `C: Other (free text)`. No label is marked Recommended until the diff is
known; the executor states which it recommends and why.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md
@src/python/ta_r4/job_guard.py
@src/python/ta_r4/commands.py
@envs/r_coloc.yml
@bin/r4_fire.sh
@bin/setup-envs.sh
@config/ta_r4/cluster_slurm/jobscript.sh
@tests/ta_r4/fixtures/build_toy_workflow.py
@tests/ta_r4/fixtures/qtl_group_fixture.py
@tests/ta_r4/test_job_guard.py

**Standing rules:** the 15.8 shared protocol (15.8a <protocol>); memory rules
reference_snakemake_conda_clean_tarballs_shared_cache (isolate pkgs_dirs), feedback_verify_assumption_before_shipping,
feedback_a_claimed_invariant_needs_a_named_enforcer, feedback_green_assertion_needs_a_negative_control. **No fit is run
in this plan.** `CONDA=/rs1/researchers/c/ckclinto/miniconda3/condabin/conda` everywhere a conda command is named.

**Measured at planning (re-measure in Task 1):**
- `R4_CONDA_PREFIX=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4` (bin/r4_fire.sh:13). md5(realpath(prefix)
  + envs/r_coloc.yml bytes) = `0f3436279d4146c376747a0ea5bfd4bf`, the existing env dir; its `0f343627…_.yaml` is
  cmp-equal to envs/r_coloc.yml. conda-meta `libopenblas-0.3.34-pthreads_hf13c14d_2`,
  `libblas-3.11.0-11_h4a7cf45_openblas`, `r-base-4.4.2-hc737e89_2`; `lib/libblas.so.3 -> libopenblasp-r0.3.34.so`,
  `liblapack.so.3` likewise; `lib/R/lib/libR.so` links `lib/R/lib/../../libblas.so.3`. The plink, python_stats and
  qtl_processing envs in the prefix also have libopenblas 0.3.34. The named env `/rs1/researchers/c/ckclinto/conda_envs/r_coloc`
  has 0.3.32 (manifests/env_lock_r_coloc_named.yml:60); close.sh's RSCRIPT is that named env, so the tests' R is not the
  job env.
- Snakemake 7.32.4 (`snakemake/deployment/conda.py`): env hash = md5(realpath(env dir) + yaml content [+ post-deploy
  script]); **the pin file is not in the hash**. With `<stem>.linux-64.pin.txt` next to the yaml, creation uses it and
  the env dir gets a sibling `str(D) + ".pin.txt"` (not `str(D) + ".yaml"`); **if creation from the pin file fails,
  Snakemake logs "Failed to install conda environment from pin file … Trying regular environment definition file" and
  solves the yaml** (:555-575). `conda clean` runs only when `--conda-cleanup-pkgs` is given (:542-552); we never pass
  it, and still isolate CONDA_PKGS_DIRS / CONDARC / HOME as r4_fire.sh does. Editing the yaml creates a new env dir; the
  old one stays.
- bin/setup-envs.sh phase 2 walks staged `.snakemake/conda/*.yaml` and creates missing prefixes from them directly, so
  on that path the pin file is not used (record for Track B; r4 builds go through Snakemake, not setup-envs.sh).
- tests/ta_r4/fixtures/qtl_group_fixture.py:18-26 `_job_env` asserts exactly one `$R4_CONDA_PREFIX/*_.yaml` byte-equal
  to envs/r_coloc.yml and runs at import (`RSCRIPT = str(_job_env() / "bin/Rscript")`). The pin-file build writes no
  `.yaml` sibling, so after the edit 0 match → `_job_env` uses the locator (fixture-builder edit, ids unchanged). Its 5
  importers are test_qtl_group_runner, test_coloc_pair_r4, test_verify_inputs, test_fit_name_alignment and
  test_purity_determinism. (15.8a3 already edited this fixture: after the R builder it copies each toy
  `data/processed/sumstats_harmonized/<tr>.EUR.tsv.bgz` to `paths.sumstats_path(tr, "EUR", "A3_1kg")`, the r4-route
  oriented path; the `_job_env` edit here is separate and must keep that copy block unchanged.) **Between the Task 2 commit (yaml edited) and the Task 3 build they are expected to fail
  collection** (the located env does not exist yet). That is not to be "fixed"; the Task 3 step 2 re-run of those
  modules is the proof that they work afterwards.
- tests/ta_r4/test_job_guard.py: `_check` helper :89-91 calls `job_guard.check(REPO_ROOT, ARM, digest, environ=…,
  cpuinfo=…, record_dir=…, label=…)`; test_guard_writes_the_record :107-121 asserts
  `rec["checked"] == {"lock_gate": True, "config_digest": True, "cpu_cascadelake": True, "kernel_env": True}` →
  declared spec update (the dict gains `"blas_pinned": True`). `_check` builds a valid fake prefix and merges its
  `CONDA_PREFIX` into whatever `environ` the caller passes (or CLEAN_ENV), unless the caller sets `CONDA_PREFIX`
  itself, and passes stub `blas_probe` / `r_blas_probe` returning the pinned values (fixture builder).
- The gate command (commands.gate_command :107-117) runs `sys.executable -m ta_r4.job_guard` in the job shell where
  Snakemake activated the rule's env, so `CONDA_PREFIX` is the job env. The default `blas_probe` runs the ctypes calls in
  a fresh `sys.executable -I -c` subprocess with the absolute library path (the guard process never loads that
  OpenBLAS); the default `r_blas_probe` runs `$CONDA_PREFIX/bin/Rscript`.

**Valid fake prefix (unit tests 2-7):** conda-meta with one `libopenblas-<pin>-…json`; `lib/libopenblasp-r<pin>.so` (a
dummy file); `lib/libblas.so.3`, `lib/liblapack.so.3` → that file; `bin/Rscript` present; `blas_probe` stub returning
`OpenBLAS <pin> DYNAMIC_ARCH …` and a corename; `r_blas_probe` stub returning the dummy file's path. Each of tests 2-6
changes exactly one of these and asserts `pytest.raises(JobGuardError, match=<that violation's message>)`, so a removed
check cannot be hidden by another violation.
</context>

<new_tests>
tests/ta_r4/test_job_guard_blas.py; N_new = 11 (one junit id each, no parametrize).
1. `test_pin_is_read_from_r_coloc_yml` (`libopenblas_pin(<tmp repo whose envs/r_coloc.yml has libopenblas=9.9.9>) ==
   "9.9.9"`; none or two such lines → JobGuardError)
2. `test_guard_refuses_a_libopenblas_version_other_than_the_pin` (valid prefix, conda-meta record 0.3.32; match= the
   conda-meta version message)
3. `test_guard_refuses_blas_symlinks_not_to_the_pinned_openblas` (valid prefix, libblas.so.3 → another file; match=)
4. `test_guard_refuses_without_conda_prefix` (match=)
5. `test_guard_refuses_a_runtime_config_of_another_version` (valid prefix, probe stub `OpenBLAS 0.3.340 DYNAMIC_ARCH …`,
   which a prefix comparison would accept; match= the runtime-version message)
6. `test_guard_refuses_a_missing_or_other_r_blas` (two cases, each on a fresh valid prefix with one change: `bin/Rscript`
   removed → match= the missing-Rscript message; `r_blas_probe` returning another file → match= the R-BLAS message)
7. `test_guard_record_has_the_blas_block` (valid prefix; check() passes; record has blas.version/library/config/
   corename/r_blas and checked.blas_pinned)
8. `test_job_env_locator_equals_snakemake_env_address` (r4_heavy; `job_env_dir(envs/r_coloc.yml, R4_CONDA_PREFIX)` ==
   the address of `snakemake.deployment.conda.Env` built for the same yaml with a stub workflow whose conda prefix is
   R4_CONDA_PREFIX; the dir exists and holds `bin/Rscript`; with a tmp `envs/r_coloc.post-deploy.sh`, job_env_dir
   raises)
9. `test_real_job_env_passes_and_named_env_is_refused` (r4_heavy; calls blas_facts/blas_violations directly, not
   check(): the located job env gives [] and its corename equals the corename row of env_lock_r_coloc_job.tsv; the named
   env /rs1/researchers/c/ckclinto/conda_envs/r_coloc (0.3.32) gives a non-empty list containing the version violation)
10. `test_pin_file_equals_the_job_env_explicit_list` (r4_heavy; `str(D) + ".pin.txt"` cmp-equal to the repo pin file;
    the @EXPLICIT URL#md5 lines of `$CONDA list --explicit --md5 -p D` equal those of the repo pin file)
11. `test_env_lock_manifest_matches_the_job_env` (r4_heavy; conda-meta records, the libopenblas .so sha256, corename row)
Expected FULL: base full_15_8a4.xml (expected 2,728; 15.8a 2,700 + 15.8a2 14 + 15.8a3 8 + 15.8a4 6) + 11 = 2,739. Declared spec updates:
tests.ta_r4.test_job_guard::test_guard_writes_the_record (assertion edit, above); `_check` and `_job_env` are
fixture-builder edits (every test using them keeps its id and passes).
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: Gates; locator; measure the BLAS the jobs load (Cascade Lake, read-only)</name>
  <files>src/python/ta_r4/conda_job_env.py (scratch measurements: $Q8/blas_measure_15_8b.txt, $Q8/blas_probe_15_8b.sh)</files>
  <read_first>
    - job_guard.py (all); commands.py :1-30, :100-130; bin/r4_fire.sh :1-30, :95-115; bin/setup-envs.sh (all);
      build_toy_workflow.py :210-270
    - qtl_group_fixture.py :1-40; test_job_guard.py :1-125
    - snakemake/deployment/conda.py :95-200, :360-400, :520-580 (smoke_dev); every `conda:` directive in src/snakemake
  </read_first>
  <action>
    0. `git rev-parse HEAD > $Q8/start_15_8b.txt`; `bash $Q8/gate_157j.sh`; `bash $Q8/gate_158.sh Q-158R6S`.
    1. `conda_job_env.py`: `job_env_dir(yml, prefix=R4_CONDA_PREFIX)` per must_haves (reads the yaml bytes; no glob;
       raises if the yaml's `.post-deploy.sh` sibling exists). Check it returns `…/0f3436279d4146c376747a0ea5bfd4bf_`
       for the current yaml, that it equals Snakemake's Env address for the same yaml and prefix, and that
       `str(dir) + ".yaml"` is cmp-equal to envs/r_coloc.yml; else STOP (the hash rule is not what the plan assumes).
    2. `$Q8/blas_probe_15_8b.sh` via `sbatch -p compute -A clintonlab_cpu -q normal -t 00:20:00 --mem=4G
       --constraint=cascadelake`: `source /rs1/researchers/c/ckclinto/miniconda3/bin/activate <env dir>`, then print the
       must_haves facts (`Rscript -e 'cat(extSoftVersion()[["BLAS"]], La_library(), La_version(), sep="\n")'` with
       OPENBLAS_VERBOSE=2; the ctypes probe in a `-I` subprocess; `sha256sum lib/libopenblasp-r*.so`;
       `$CONDA list --explicit --md5 -p <env>`). Repeat the conda-meta part for every env of a gated production rule.
       Save to `$Q8/blas_measure_15_8b.txt` (`libopenblas_version=`, `corename=`, `libopenblas_sha256=` lines; the
       corename is copied into the committed manifest in Task 3). No fit is run.
    3. STOP if: R's BLAS realpath is not the conda-meta libopenblas file; the runtime version differs from conda-meta;
       a gated production rule has no conda env; a gated rule's env has another libopenblas version (that env is not
       pinned, per Q-158R6S; the guard would refuse it — Carter's call).
    4. Count every rule outside ta_r4 whose `conda:` is envs/r_coloc.yml (measured; the plan-checker counts 23), and any
       env dir built from it under `.snakemake/conda` with its libopenblas version → `$Q8/r_coloc_users_15_8b.txt`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158R6S && grep -q "^libopenblas_version=" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^corename=" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^libopenblas_sha256=" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt</automated>
  </verify>
  <done>The locator equals Snakemake's env address; BLAS library, version, kernel and file hash measured in the activated job env on Cascade Lake.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Pin + pin file + guard BLAS check + fixture locator (RED first)</name>
  <files>envs/r_coloc.yml, envs/r_coloc.linux-64.pin.txt, src/python/ta_r4/job_guard.py, tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/test_job_guard.py, tests/ta_r4/fixtures/qtl_group_fixture.py</files>
  <behavior>
    - Tests 1-7 on tmp_path valid fake prefixes with exactly one change each (<context>); tests 8-11 against the real
      envs (skip only when /rs1 is absent, as the other r4_heavy tests)
  </behavior>
  <action>
    1. RED: tests 1-11 (`$Q8/red_15_8b.txt`; test 8 fails on the missing locator).
    2. `qtl_group_fixture._job_env` → `conda_job_env.job_env_dir(REPO_ROOT / yml)` plus an existence assert (fixture
       builder). Before step 3, check the 5 importers collect (the locator still returns 0f343627).
    3. envs/r_coloc.yml: one line `  - libopenblas=<measured version>` after `r-base`. Pin file: `$CONDA list --explicit
       --md5 -p <0f343627 env>` → envs/r_coloc.linux-64.pin.txt (starts with the header lines, then `@EXPLICIT`). From
       here until the Task 3 build, the 5 importers are expected to fail collection (<context>); do not change them.
    4. job_guard.py: `libopenblas_pin(repo)`; `blas_facts(prefix, probe, r_probe)`; `blas_violations(facts, pin)`
       (runtime version token compared exactly: `config.split()[1] == pin`; a missing bin/Rscript is a violation);
       `check(…, blas_probe=None, r_blas_probe=None)` (None → the default probes) calls them after
       kernel_env_violations with `environ.get("CONDA_PREFIX")`, raises JobGuardError listing every violation (one
       message per check, each distinct), adds `rec["blas"]` and `checked["blas_pinned"] = True`. Nothing else changes.
       test_job_guard.py: `_check` per <context>; the declared edit of test_guard_writes_the_record adds
       `"blas_pinned": True`.
    5. Tests 1-7 and test_job_guard.py green. NCs (`$Q8/nc_15_8b.txt`), md5-restore each: (1) `libopenblas_pin` returns a
       hard-coded "0.3.34" → test 1 fails (the tmp repo says 9.9.9); (2) conda-meta version comparison removed → test 2
       fails; (3) symlink check removed → test 3 fails; (4) missing CONDA_PREFIX treated as pass → test 4 fails;
       (5) runtime version compared as a prefix (`startswith`) → test 5 fails; (6a) missing Rscript treated as a skip →
       test 6 fails; (6b) R-BLAS comparison removed → test 6 fails.
    6. Commit (`feat(ta-r4-W3f): pin libopenblas in r_coloc.yml + exact pin file; job guard refuses another BLAS (15.8b)`),
       explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_job_guard_blas.py tests/ta_r4/test_job_guard.py -q -p no:cacheprovider -m "not r4_heavy"</automated>
  </verify>
  <done>Pin and pin file committed; each unit test isolates one violation and fails under its own mutation; the fixture locates the env by hash.</done>
</task>

<task type="auto">
  <name>Task 3: Build the env (isolated) + identity proof (no fit); manifest; DRAFT (k); FULL; records (STOP for Carter on any difference)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_job.tsv, tests/ta_r4/test_job_guard_blas.py, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-SUMMARY.md</files>
  <action>
    1. Shared cache before: entry count and sha256 of the sorted `ls` of /rs1/researchers/c/ckclinto/conda_pkgs →
       `$Q8/conda_pkgs_before_15_8b.txt`. Build: with the exports of bin/r4_fire.sh:13-21, run the toy workflow's
       snakemake invocation (build_toy_workflow.py:256-266) with `--conda-create-envs-only` (no
       `--conda-cleanup-pkgs`); log to `$Q8/env_build_15_8b.log`. Shared cache after → `$Q8/conda_pkgs_after_15_8b.txt`;
       cmp with before (equal, else STOP).
    2. Identity: write `$Q8/env_identity_15_8b.py <env dir>` (must_haves; exit 0 only if every check holds) and run it
       on D = job_env_dir(envs/r_coloc.yml). **Negative control** (`$Q8/nc_15_8b.txt`): run it on the old env 0f343627
       (has `.yaml`, no `.pin.txt`): it must exit non-zero. Write env_lock_r_coloc_job.tsv from D's conda-meta plus the
       .so sha256 and the Task 1 corename. Run tests 8-11 on Cascade Lake (sbatch), plus test_job_guard.py and the 5
       qtl_group_fixture importers (they now collect and pass). NCs (md5-restore each): one yaml byte changed in a tmp
       copy, and another prefix → job_env_dir gives a different dir that does not exist (test 8's identity would fail);
       one manifest row perturbed in a tmp copy → test 11 fails; one URL#md5 line changed in a tmp pin copy → test 10
       fails.
    3. **STOP** (checkpoint:human-action semantics, stops even under --auto) on any difference in 1-2: print the diff,
       present Q-158R6, write nothing more, wait for Carter's reply file. Do not re-pin; delete neither env; run no fit.
    4. DRAFT (k): `with `OPENBLAS_CORETYPE` set, or under a run configuration` (assert unique) → `with
       `OPENBLAS_CORETYPE` set, with an OpenBLAS library other than version <pin> (pinned in the environment, with its
       exact package list), or under a run configuration`. test_amendment_text.py, test_prelock_pilot_fits.py green.
    5. `$Q8/close.sh 15_8b` under sbatch; `$Q8/check_15_8b.py` (base full_15_8a4.xml; NEW = the 11 ids; declared =
       test_guard_writes_the_record). Records: LOG (measurement, identity and its NC, r_coloc users count, the
       setup-envs.sh note, conda_pkgs before/after, NCs, check); PLAN-INDEX 15.8b row; STATE (NEXT = 15.8c; NOT PUSHED);
       SUMMARY with both sections (junit-form ids) and the Track B / m3 notes of must_haves. fsck; commit explicit
       paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8b.py && grep -q "libopenblas=" envs/r_coloc.yml && test -s envs/r_coloc.linux-64.pin.txt && grep -q "Using pinnings from" data/r4/tmp/w3f/q158/env_build_15_8b.log && ! grep -q "Failed to install" data/r4/tmp/w3f/q158/env_build_15_8b.log && cmp data/r4/tmp/w3f/q158/conda_pkgs_before_15_8b.txt data/r4/tmp/w3f/q158/conda_pkgs_after_15_8b.txt</automated>
  </verify>
  <done>The r4 R job env is pinned to the BLAS it loads and rebuilt with an identical package list and library file, the identity check is shown to fail on the old env, and the guard enforces the pin; or Carter has the diff.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| env recipe → numerical results | a rebuilt env may load another BLAS kernel and move non-converged fits |
| job env → shared conda cache | conda clean on a shared pkgs dir |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158b-01 | Tampering | silent yaml-solve fallback from the pin file | mitigate | `.pin.txt` sibling byte-equal, `.yaml` sibling absent, log scan, URL#md5 identity; identity script seen to fail on the old env; STOP on difference |
| T-r4-158b-02 | Tampering | numeric drift after rebuild | mitigate | identical URL#md5 package list and identical libopenblas .so sha256 to the env of the 17 kernel runs; no new fit |
| T-r4-158b-03 | Denial of service | shared conda pkgs cache wiped | mitigate | no --conda-cleanup-pkgs; CONDA_PKGS_DIRS/CONDARC isolated; /rs1/researchers/c/ckclinto/conda_pkgs entry count + sorted-ls sha256 before == after |
| T-r4-158b-04 | Elevation | job runs with an unpinned BLAS | mitigate | guard refuses on version, symlink, exact runtime version token, missing Rscript or R-reported BLAS mismatch; each check isolated by its own test and NC |
</threat_model>

<verification>
- check_15_8b.py passes; identity recorded with its negative control; the shared conda cache unchanged; no fit run.
</verification>

<success_criteria>
- A production job can only run against the pinned OpenBLAS in the recorded job env.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-SUMMARY.md`
</output>
