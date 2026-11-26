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
  - src/python/ta_r4/conda_job_env.py          # DONE in Task 1 (e47b6a83); used by the fixture and tests 8-11, 15
  - src/python/ta_r4/job_guard.py
  - src/python/ta_r4/commands.py               # gate_command(blas_pinned=) + is_r_coloc_env + rule_gate (Task 3)
  - src/snakemake/rules/ta_r4_finemap.smk      # gate param -> r4cmd.rule_gate (Task 3)
  - src/snakemake/rules/ta_r4_coloc.smk        # r4_coloc_pair, r4_coloc_A1 gate params -> r4cmd.rule_gate (Task 3)
  - src/snakemake/rules/ta_r4_sim.smk          # r4_sim gate param -> r4cmd.rule_gate (Task 3)
  - src/snakemake/rules/ta_r4_qtl.smk          # _r4_qtl_gate_cmd -> r4cmd.rule_gate (Task 3)
  - tests/ta_r4/test_job_guard_blas.py
  - tests/ta_r4/test_job_guard.py              # `_check` helper (fixture builder) + 2 declared spec updates
  - tests/ta_r4/test_in_job_gate.py            # tests 15-16 + `rendered_conda` fixture + 3 declared spec updates (9 ids)
  - tests/ta_r4/fixtures/qtl_group_fixture.py  # `_job_env` uses the locator (fixture-builder edit)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt
  - .planning/DECISIONS.md
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
    - "Gates Q-157J, Q-158R6S (`Proceed, pin r_coloc only (Recommended)`, sha256 7b3d1045…5b2d) and Q-158R6G (`A: BLAS check only for r_coloc rules (Recommended)`, sha256 e766bbbd…8a24) pass (15.8 protocol); otherwise nothing is edited. Q-158R6G is committed with a DEC entry whose quote is cmp-equal to the reply file"
    - "Only envs/r_coloc.yml (shared with Track B and m3) gains a pin and a pin file; python_stats, plink and qtl_processing are not pinned (Carter Q-158R6S). The BLAS check runs only in gated jobs of rules whose conda directive is envs/r_coloc.yml (Carter Q-158R6G A); there it fails closed if the job env drifts from the pin. The SUMMARY and LOG record (measured in Task 1, data/r4/tmp/w3f/q158/r_coloc_users_15_8b.txt): 23 rules outside ta_r4 use envs/r_coloc.yml; .snakemake/conda holds 0 staged yamls (0 env dirs built from the current r_coloc.yml); bin/setup-envs.sh's phase-2 fallback walks only staged *.yaml files, so on that path Track B solves the yaml, not the pin file (libopenblas version held by the pin line; build strings not held); Track B and m3 rebuild their r_coloc env on their next Snakemake run from the same pin file at the same libopenblas version"
    - "One locator, `conda_job_env.job_env_dir(yml, prefix)` = `<prefix>/<md5(realpath(prefix) + yaml bytes)>_` (committed e47b6a83), equal to Snakemake 7.32.4's Env(...).address for the same yaml and conda prefix (measured, locator_15_8b.txt LOCATOR_OK; test 8); it raises if `envs/r_coloc.post-deploy.sh` exists; it is used by the qtl_group_fixture and tests 8-11, 15; before the yaml edit it returns 0f3436279d4146c376747a0ea5bfd4bf_"
    - "Measured in Task 1 (Slurm 2101499, c020n02, Xeon Gold 6226R Cascade Lake; blas_measure_15_8b.txt, blas_probe_15_8b_2101499.out), env 0f343627 activated with miniconda3/bin/activate: conda-meta libopenblas-0.3.34-pthreads_hf13c14d_2; lib/libblas.so.3, liblapack.so.3, libcblas.so.3, R's extSoftVersion()['BLAS'] and La_library() all realpath to lib/libopenblasp-r0.3.34.so (sha256 f1424288…572b); openblas_get_config `OpenBLAS 0.3.34 DYNAMIC_ARCH NO_AFFINITY SkylakeX MAX_THREADS=128`; corename and the OPENBLAS_VERBOSE=2 Core line SkylakeX; 222 @EXPLICIT lines. The env has no bin/python3, so the ctypes probe ran under smoke_dev python3.11 -I"
    - "One conda binary, /rs1/researchers/c/ckclinto/miniconda3/condabin/conda, makes the pin file and every explicit list in Task 4 and test 10. envs/r_coloc.yml pins `libopenblas=0.3.34`; envs/r_coloc.linux-64.pin.txt is `conda list --explicit --md5 -p <0f343627 env>`; manifests/env_lock_r_coloc_job.tsv lists every conda-meta package (name, version, build string, channel, md5) of that env, the libopenblas .so sha256 and the measured corename"
    - "Env identity, with no fit run, checked by `$Q8/env_identity_15_8b.py <env dir>` (exit 0 = identical): for D = job_env_dir(envs/r_coloc.yml) after the build, `str(D) + \".pin.txt\"` is cmp-equal (byte-exact) to envs/r_coloc.linux-64.pin.txt; `str(D) + \".yaml\"` is absent; the build log has 'Using pinnings from' and not 'Failed to install'; the `@EXPLICIT` URL#md5 lines of `conda list --explicit --md5 -p D` equal those of the repo pin file (the `# created-by` header is not compared); D's libopenblasp-r<ver>.so sha256 equals the measured env's; `ls D/lib/R/library` equals the measured env's. Its negative control: the same script on the old env 0f343627 (which has `_.yaml` and no `_.pin.txt`) exits non-zero. Any difference on D is a STOP for Carter (Q-158R6)"
    - "job_guard.check(…, blas_pinned, blas_probe=None, r_blas_probe=None); CLI flag `--blas-pinned` → blas_pinned=True, absent → False. With blas_pinned=True it refuses a production job when: CONDA_PREFIX is unset; conda-meta has no or several libopenblas records or a version other than the pin; libblas.so.3 / liblapack.so.3 do not resolve to that env's libopenblasp-r<pin>.so; the runtime config's version token is not exactly the pin (`config.split()[1] == pin`, not a prefix match); `$CONDA_PREFIX/bin/Rscript` is missing (a violation, not a skip); or the BLAS R itself reports (`Rscript -e 'cat(extSoftVersion()[[\"BLAS\"]])'`, R loads it in its own process; the guard never dlopens it) resolves to another file; the record gains a `blas` block (status pinned, version, library, config, corename, r_blas) and checked.blas_pinned = true. With blas_pinned=False it calls no BLAS function (no pin read, no conda-meta read, no probe) and the record has checked.blas_pinned = \"not_checked\" and blas = {status: not_checked, reason: BLAS_NOT_CHECKED_REASON}, never an absent field. Both probes are injectable; the default blas_probe runs the ctypes calls in `sys.executable -I -c` (the guard's own interpreter, smoke_dev 3.11), never `$CONDA_PREFIX/bin/python3` (absent in the r_coloc env). The pin is read from envs/r_coloc.yml"
    - "gate_command(…, blas_pinned=) appends `--blas-pinned` iff blas_pinned is True and raises ValueError for a production call whose blas_pinned is not exactly True or False. Every gated rule renders its gate through `commands.rule_gate(workflow, rule, stage, arm, config, wildcards)`, which derives blas_pinned from Snakemake's own record of that rule's conda directive (`workflow.get_rule(rule).conda_env`) via `is_r_coloc_env(conda_env, workflow.basedir)` (realpath equal to <basedir>/envs/r_coloc.yml; None → False; relative, callable or other types → ValueError). No hand-kept rule list decides the flag. Measured partition, pinned by test 15: flagged = r4_run_finemap, r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group; unflagged = r4_qtl_aggregate, r4_qtl_tiers. Test 15 fails when a gated r_coloc rule loses the flag and when aggregate or tiers gains it, each seen failing"
    - "DRAFT (k) says production jobs that run in the R environment refuse an OpenBLAS library other than the pinned version, and that the QTL aggregation and tier jobs (which run no R) record that their BLAS was not checked; old string asserted unique"
    - "The shared cache /rs1/researchers/c/ckclinto/conda_pkgs is unchanged by the build: its entry count and the sha256 of its sorted `ls` are equal before and after"
  artifacts:
    - path: "envs/r_coloc.linux-64.pin.txt"
      provides: "exact package set of the r4 R job env"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_job.tsv"
      provides: "the job env's own lock and its measured OpenBLAS corename (env_lock_r_coloc_named.yml describes the named env, not the job env)"
    - path: "src/python/ta_r4/conda_job_env.py"
      provides: "the Snakemake job-env locator (committed e47b6a83)"
    - path: "src/python/ta_r4/commands.py"
      provides: "rule_gate / is_r_coloc_env: the --blas-pinned flag derived from each rule's conda directive"
      contains: "def rule_gate"
    - path: ".planning/DECISIONS.md"
      provides: "the Q-158R6G DEC entry with the byte-exact reply quote"
      contains: "Q-158R6G"
  key_links:
    - from: "job_guard.check"
      to: "envs/r_coloc.yml libopenblas pin"
      via: "blas_pinned=True: pin parsed at check time; CONDA_PREFIX conda-meta + realpath + subprocess probe + Rscript BLAS"
      pattern: "libopenblas"
    - from: "src/snakemake/rules/ta_r4_*.smk gate params"
      to: "commands.rule_gate"
      via: "workflow.get_rule(rule).conda_env → is_r_coloc_env → gate_command(blas_pinned=) → `--blas-pinned`"
      pattern: "rule_gate\\(workflow"
    - from: "job_guard.main"
      to: "job_guard.check(blas_pinned=)"
      via: "argparse store_true `--blas-pinned`"
      pattern: "--blas-pinned"
---

<objective>
Close review R6 as Carter chose (Q-157J "R6: pin libopenblas"; Q-158R6S; Q-158R6G A). The job guard checks the CPU
but not the BLAS library, and the committed env lock describes the named r_coloc env (OpenBLAS 0.3.32), while jobs run
in the Snakemake-built env (0.3.34). This plan measures what the jobs load (done, Task 1), pins it in envs/r_coloc.yml
with an exact pin file, records the job env's lock, and makes the guard refuse any other BLAS in every gated job whose
rule runs in the r_coloc env. The two gated QTL rules without a conda env (r4_qtl_aggregate, r4_qtl_tiers) keep
today's guard and their job record says the BLAS was not checked (Q-158R6G A). The rebuilt env is proven identical to
the measured one by its package list and library hash, with no fit run (a new pre-lock fit would fall outside the
approved F15 paragraph's "17 runs"); any difference stops for Carter.
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
Q-158R6G (answered 2026-11-26, the Task 1 step 3 STOP "a gated production rule has no conda env"): file
`W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt` (untracked until Task 2 step 0), sha256
`e766bbbd642280d55e7e176b5887be2b033b9ac65d219a66e102b86a995d8a24`, label `A: BLAS check only for r_coloc rules (Recommended)`.
The question text is line 1 of the file after the prefix `Question Q-158R6G (2026-11-26): ` (the gate proves it).
**A second, earlier file exists for the same QID:** `W3f-carter-15-8-Q-158R6G-reply-2026-11-25.txt` (untracked, sha256
1cdfc554…55fa, an earlier wording of the same question, label `A: check only r_coloc rules (Recommended)`). The
coordinator names the 2026-11-26 file as Carter's answer; only it is gated and committed. The 2026-11-25 file is left
untouched and untracked (not deleted, not committed), and the DEC entry names it with its sha256 as an earlier
presentation of the same question, not the decision record. The staging copy holds only the 2026-11-26 file, so the
tool's exactly-one-file rule is met.
The option as shown to Carter: "Run the BLAS check only for the gated rules that use the r_coloc env (r4_run_finemap,
r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group). Aggregate and tiers keep today's guard, and their job record says
the BLAS was not checked. The plan's must_haves and tests get revised, then 15.8b resumes at Task 2."
Task 4 question (only on a STOP), QID Q-158R6, file `W3f-carter-15-8-Q-158R6-reply-<date>.txt`: "The env Snakemake built
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
@src/python/ta_r4/conda_job_env.py
@src/snakemake/rules/ta_r4_qtl.smk
@envs/r_coloc.yml
@bin/r4_fire.sh
@bin/setup-envs.sh
@config/ta_r4/cluster_slurm/jobscript.sh
@tests/ta_r4/fixtures/build_toy_workflow.py
@tests/ta_r4/fixtures/qtl_group_fixture.py
@tests/ta_r4/test_job_guard.py
@tests/ta_r4/test_in_job_gate.py

**Standing rules:** the 15.8 shared protocol (15.8a <protocol>), including its **Never** list (no `git push`; no
production fit; no OSF posting; no W4a-T3 lock; decision_rules.yaml `locked` stays false and `n_regions_min` stays 7;
no re-pin to make a check pass; no `git add .` / `-A`, explicit paths only). Scope stays Q-158R6S: only
envs/r_coloc.yml is pinned. Every heavy run (pytest r4_heavy, BLAS probes, dry-runs used as evidence, the env build,
FULL) goes through `sbatch -p compute -A clintonlab_cpu -q normal -t <limit> --constraint=cascadelake`. Memory rules
reference_snakemake_conda_clean_tarballs_shared_cache (isolate pkgs_dirs), feedback_verify_assumption_before_shipping,
feedback_a_claimed_invariant_needs_a_named_enforcer, feedback_green_assertion_needs_a_negative_control,
feedback_negative_control_defeated_by_bytecode_cache (run every NC with `PYTHONDONTWRITEBYTECODE=1` and
`-p no:cacheprovider`). **No fit is run in this plan.** `CONDA=/rs1/researchers/c/ckclinto/miniconda3/condabin/conda`
everywhere a conda command is named.

**Task 1 measurements (DONE; files in `$Q8` = data/r4/tmp/w3f/q158):** start_15_8b.txt (HEAD 82339a6d before Task 1);
gate_15_8b.txt (Q-157J and Q-158R6S gates rc 0); locator_15_8b.py/.txt (job_env_dir == Snakemake Env.address ==
…/0f3436279d4146c376747a0ea5bfd4bf_, sibling `_.yaml` cmp-equal, LOCATOR_OK); blas_probe_15_8b.sh,
blas_probe_15_8b_2101499.out and blas_measure_15_8b.txt (must_haves truth 4; `libopenblas_version=0.3.34`,
`corename=SkylakeX`, `libopenblas_sha256=f1424288e9ac125331102c0150b66fbd244560987779552e0e97d5cfd9de572b`;
`$CONDA_PREFIX/bin/python3: No such file or directory`, so the ctypes probe fell back to smoke_dev python3.11 -I);
r_coloc_users_15_8b.py/.txt (23 rules outside ta_r4; `snakemake_conda_dir_exists=True n_yaml=0`;
`env_dirs_built_from_current_r_coloc_yml=0`). The other envs in the prefix (plink 55c377a7, python_stats 8f7292f9,
qtl_processing dc880444) are not used by any gated rule and also carry libopenblas-0.3.34-pthreads_hf13c14d_2.

**Gated rules (verified by the planner from the .smk files, re-verify in Task 3 step 1):** the 7 call sites of
`r4cmd.gate_command` in src/snakemake/rules are r4_run_finemap (ta_r4_finemap.smk:55, `conda:` envs/r_coloc.yml :49),
r4_coloc_pair (ta_r4_coloc.smk:68, `conda: _R4_COLOC_ENV` = envs/r_coloc.yml), r4_coloc_A1 (ta_r4_coloc.smk:99, same),
r4_sim (ta_r4_sim.smk:64, `conda:` envs/r_coloc.yml :58), and via `_r4_qtl_gate_cmd` (ta_r4_qtl.smk:63-68)
r4_qtl_group (:122, `conda:` envs/r_coloc.yml :116), r4_qtl_aggregate (:143) and r4_qtl_tiers (:167), the last two
with no `conda:` directive, running `py=sys.executable` (smoke_dev 3.11, pip numpy/scipy with their own
scipy_openblas, no R). This equals test_in_job_gate.PRODUCTION_RULES. Snakemake 7.32.4 stores the directive as given
(workflow.py:1688-1705: a Path becomes str; `rule.conda_env = ruleinfo.conda_env`), so for these rules
`workflow.get_rule(name).conda_env` is the absolute string `<basedir>/envs/r_coloc.yml` or None. `workflow.get_rule`
raises on an unknown name, so a rule name typed into rule_gate that is not the rule fails at render time. In a
`-n -p --use-conda` dry run Snakemake prints `conda-env: <Env.address>` for each job that has a conda env
(logging.py:536-537; jobs.py:1112); test 15 uses that as the independent record of each rule's directive.

**Measured at planning (unchanged by Task 1):**
- `R4_CONDA_PREFIX=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4` (bin/r4_fire.sh:13). The named env
  `/rs1/researchers/c/ckclinto/conda_envs/r_coloc` has 0.3.32 (manifests/env_lock_r_coloc_named.yml:60); close.sh's
  RSCRIPT is that named env, so the tests' R is not the job env.
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
  oriented path; the `_job_env` edit here is separate and must keep that copy block unchanged.) **Between the Task 2
  commit (yaml edited) and the Task 4 build they are expected to fail collection** (the located env does not exist
  yet), and so is test_in_job_gate::test_gate_in_a_job_fails_after_locked_path_drift after Task 3 (its flagged
  r4_run_finemap gate now needs the located job env as CONDA_PREFIX). That is not to be "fixed"; the Task 4 step 2
  re-run of those modules is the proof that they work afterwards.
- tests/ta_r4/test_job_guard.py: `_check` helper :89-91 calls `job_guard.check(REPO_ROOT, ARM, digest, environ=…,
  cpuinfo=…, record_dir=…, label=…)`; test_guard_writes_the_record :107-121 asserts
  `rec["checked"] == {"lock_gate": True, "config_digest": True, "cpu_cascadelake": True, "kernel_env": True}` →
  declared spec update (the dict gains `"blas_pinned": True`). `_check` gains `blas_pinned=True` (default), builds a
  valid fake prefix and merges its `CONDA_PREFIX` into whatever `environ` the caller passes (or CLEAN_ENV), unless the
  caller sets `CONDA_PREFIX` itself, and passes stub `blas_probe` / `r_blas_probe` returning the pinned values (fixture
  builder). test_gate_command_production_is_the_guard :138-142 → declared spec update (the call gains
  `blas_pinned=False`; the expected argv is unchanged).
- tests/ta_r4/test_in_job_gate.py (module pytestmark r4_heavy): test_gate_command_stages :177-189 → declared spec
  update (every production call and each of the three ValueError cases gains `blas_pinned=False`, so each case still
  raises for its own missing field; expected argv unchanged); test_production_shell_begins_with_the_gate[<7 rules>]
  :126-139 → declared spec update (`want` gains `blas_pinned=` from the `rendered_conda` record of the job's rule, not
  from a list); test_gate_in_a_job_fails_after_locked_path_drift :158-174 → declared spec update (both gate
  subprocesses get `env={**os.environ, "CONDA_PREFIX": str(job_env_dir(REPO_ROOT / "envs/r_coloc.yml"))}`; the
  assertions are unchanged). make_fixture_repo copies src/python, envs and every ta_r4_*.smk from the working tree, so
  a working-tree mutation is seen by a fresh module run.
- The gate command runs `sys.executable -m ta_r4.job_guard` (commands._PY) in the job shell. For an r_coloc rule
  Snakemake activated the env, so `CONDA_PREFIX` is the job env; for aggregate/tiers no env is activated and
  CONDA_PREFIX is whatever the launching shell had, which the unflagged guard never reads. The default `blas_probe`
  runs the ctypes calls in a fresh `sys.executable -I -c` subprocess with the absolute library path (the guard process
  never loads that OpenBLAS; sys.executable is smoke_dev 3.11 because the r_coloc env has no python3, Task 1); the
  default `r_blas_probe` runs `$CONDA_PREFIX/bin/Rscript`.

**Valid fake prefix (unit tests 2-7):** conda-meta with one `libopenblas-<pin>-…json`; `lib/libopenblasp-r<pin>.so` (a
dummy file); `lib/libblas.so.3`, `lib/liblapack.so.3` → that file; `bin/Rscript` present; `blas_probe` stub returning
`OpenBLAS <pin> DYNAMIC_ARCH …` and a corename; `r_blas_probe` stub returning the dummy file's path. Tests 2-7 call
check with `blas_pinned=True`. Each of tests 2-6 changes exactly one of these and asserts
`pytest.raises(JobGuardError, match=<that violation's message>)`, so a removed check cannot be hidden by another
violation.
</context>

<new_tests>
N_new = 16 (one junit id each, no parametrize).
tests/ta_r4/test_job_guard_blas.py:
1. `test_pin_is_read_from_r_coloc_yml` (`libopenblas_pin(<tmp repo whose envs/r_coloc.yml has libopenblas=9.9.9>) ==
   "9.9.9"`; none or two such lines → JobGuardError)
2. `test_guard_refuses_a_libopenblas_version_other_than_the_pin` (blas_pinned=True; valid prefix, conda-meta record
   0.3.32; match= the conda-meta version message) — the "flagged rule with the wrong libopenblas refuses" unit case
3. `test_guard_refuses_blas_symlinks_not_to_the_pinned_openblas` (blas_pinned=True; valid prefix, libblas.so.3 →
   another file; match=)
4. `test_guard_refuses_without_conda_prefix` (blas_pinned=True; match=)
5. `test_guard_refuses_a_runtime_config_of_another_version` (blas_pinned=True; valid prefix, probe stub
   `OpenBLAS 0.3.340 DYNAMIC_ARCH …`, which a prefix comparison would accept; match= the runtime-version message)
6. `test_guard_refuses_a_missing_or_other_r_blas` (blas_pinned=True; two cases, each on a fresh valid prefix with one
   change: `bin/Rscript` removed → match= the missing-Rscript message; `r_blas_probe` returning another file → match=
   the R-BLAS message)
7. `test_guard_record_has_the_blas_block` (blas_pinned=True; valid prefix; check() passes; record has blas.status
   "pinned", blas.version/library/config/corename/r_blas and checked.blas_pinned is True)
8. `test_job_env_locator_equals_snakemake_env_address` (r4_heavy; `job_env_dir(envs/r_coloc.yml, R4_CONDA_PREFIX)` ==
   the address of `snakemake.deployment.conda.Env` built for the same yaml with a stub workflow whose conda prefix is
   R4_CONDA_PREFIX (as $Q8/locator_15_8b.py); the dir exists and holds `bin/Rscript`; with a tmp
   `envs/r_coloc.post-deploy.sh`, job_env_dir raises)
9. `test_real_job_env_passes_and_named_env_is_refused` (r4_heavy; calls blas_facts/blas_violations directly with the
   **default** probes (None), not check(): the located job env gives [] and its corename equals the corename row of
   env_lock_r_coloc_job.tsv; the named env /rs1/researchers/c/ckclinto/conda_envs/r_coloc (0.3.32) gives a non-empty
   list containing the version violation; a default probe that used `$CONDA_PREFIX/bin/python3` fails here)
10. `test_pin_file_equals_the_job_env_explicit_list` (r4_heavy; `str(D) + ".pin.txt"` cmp-equal to the repo pin file;
    the @EXPLICIT URL#md5 lines of `$CONDA list --explicit --md5 -p D` equal those of the repo pin file)
11. `test_env_lock_manifest_matches_the_job_env` (r4_heavy; conda-meta records, the libopenblas .so sha256, corename row)
12. `test_unflagged_guard_records_not_checked_and_reads_no_blas` (blas_pinned=False; environ has CONDA_PREFIX → a fake
    prefix where every BLAS check would fail (conda-meta 0.3.32, no bin/Rscript, libblas.so.3 → another file);
    blas_probe / r_blas_probe stubs that raise AssertionError, and monkeypatched job_guard.blas_facts,
    blas_violations and libopenblas_pin that raise AssertionError; check() passes; record checked.blas_pinned ==
    "not_checked", blas == {"status": "not_checked", "reason": job_guard.BLAS_NOT_CHECKED_REASON}, the reason
    non-empty and naming Q-158R6G)
13. `test_cli_blas_pinned_flag_reaches_check` (monkeypatch job_guard.check to capture kwargs; `main([...,
    "--blas-pinned"])` → blas_pinned is True; the same argv without it → blas_pinned is False)
14. `test_gate_command_flags_only_the_r_coloc_env` (unit: `is_r_coloc_env(str(REPO_ROOT/"envs/r_coloc.yml"),
    REPO_ROOT)` is True, also through a tmp symlink to that file; None → False; envs/python_stats.yml → False;
    relative "envs/r_coloc.yml", a callable and an int → ValueError; `gate_command("production", ARM, cfg, label=L,
    blas_pinned=True)` == the blas_pinned=False argv + ["--blas-pinned"]; blas_pinned None / missing / 1 →
    ValueError; `gate_command("repro")` == ["true"])
tests/ta_r4/test_in_job_gate.py (module r4_heavy; uses `rendered` and a new module fixture `rendered_conda` = the same
gate repo dry-run with `--use-conda --conda-frontend conda --conda-prefix <tmp_path_factory dir>` and
`/rs1/researchers/c/ckclinto/miniconda3/condabin` first on PATH; nothing is created in a dry run):
15. `test_gate_blas_flag_follows_each_rules_conda_directive` (gated jobs = every job of `rendered_conda` whose first
    command's argv contains `ta_r4.job_guard`; their rule set == PRODUCTION_RULES; each job's gate equals the
    `rendered` gate of the same rule and wildcards; for each, `"--blas-pinned" in argv` iff the job has a
    `conda-env:` line equal to `str(job_env_dir(<gate repo>/envs/r_coloc.yml, <tmp conda prefix>))`; a job with no
    `conda-env:` line is unflagged; and the measured partition of Q-158R6G: flagged rules == {r4_run_finemap,
    r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group}, unflagged == {r4_qtl_aggregate, r4_qtl_tiers})
16. `test_flagged_gate_refuses_another_blas_and_unflagged_gate_records_not_checked` (in the gate repo: the rendered
    r4_run_finemap gate with CONDA_PREFIX = the named env /rs1/researchers/c/ckclinto/conda_envs/r_coloc → rc 1 and
    stderr has the libopenblas version message; the rendered r4_qtl_aggregate gate with CONDA_PREFIX removed from env
    → rc 0, and its record `<gate repo>/data/r4/logs/job_guard/*.<label>.json` has checked.blas_pinned ==
    "not_checked" and blas.reason == job_guard.BLAS_NOT_CHECKED_REASON)
Expected FULL: base full_15_8a4.xml (expected 2,728; 15.8a 2,700 + 15.8a2 14 + 15.8a3 8 + 15.8a4 6; use its actual
totals) + 16 = 2,744. Declared spec updates (11 ids):
tests.ta_r4.test_job_guard::test_guard_writes_the_record,
tests.ta_r4.test_job_guard::test_gate_command_production_is_the_guard,
tests.ta_r4.test_in_job_gate::test_gate_command_stages,
tests.ta_r4.test_in_job_gate::test_gate_in_a_job_fails_after_locked_path_drift,
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_run_finemap] and the same id for
r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group, r4_qtl_aggregate, r4_qtl_tiers (reasons in <context>). `_check`,
`_job_env` and `rendered_conda` are fixture-builder edits (every test using them keeps its id and passes).
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1 (DONE): Gates; locator; measure the BLAS the jobs load (Cascade Lake, read-only)</name>
  <files>src/python/ta_r4/conda_job_env.py (committed e47b6a83; scratch measurements in $Q8, listed in <context>)</files>
  <action>
    DONE 2026-11-25. Do not re-run. Evidence: commit e47b6a83 (`feat(ta-r4-W3f): Snakemake job-env locator
    conda_job_env.job_env_dir (15.8b Task 1 step 1)`); $Q8/start_15_8b.txt, gate_15_8b.txt, locator_15_8b.py/.txt
    (LOCATOR_OK), blas_probe_15_8b.sh, Slurm 2101499 output blas_probe_15_8b_2101499.out (c020n02, Cascade Lake,
    exit 0:0, no fit), blas_measure_15_8b.txt, r_coloc_users_15_8b.py/.txt.
    Step 3 STOP fired on "a gated production rule has no conda env" (r4_qtl_aggregate, r4_qtl_tiers); the other three
    STOP conditions did not fire (R's BLAS realpath = the conda-meta libopenblas file; runtime 0.3.34 = conda-meta;
    every gated rule with an env uses 0f343627 at 0.3.34). **Resolved by Carter Q-158R6G A** (check only r_coloc
    rules). Step 4: 23 r_coloc rules outside ta_r4; .snakemake/conda has 0 staged yamls. Measurement note for Task 2:
    the r_coloc env has no bin/python3, so the ctypes probe ran under smoke_dev python3.11 with -I.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git cat-file -e e47b6a83 && grep -q "^libopenblas_version=0.3.34$" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^corename=SkylakeX$" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^libopenblas_sha256=f1424288e9ac125331102c0150b66fbd244560987779552e0e97d5cfd9de572b$" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^LOCATOR_OK$" data/r4/tmp/w3f/q158/locator_15_8b.txt && grep -q "^r_coloc_rule_count_outside_ta_r4=23$" data/r4/tmp/w3f/q158/r_coloc_users_15_8b.txt</automated>
  </verify>
  <done>The locator equals Snakemake's env address; BLAS library, version, kernel and file hash measured in the activated job env on Cascade Lake; the step-3 STOP is answered by Q-158R6G A.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Q-158R6G record; pin + pin file; opt-in guard BLAS check; fixture locator (RED first)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt, .planning/DECISIONS.md, envs/r_coloc.yml, envs/r_coloc.linux-64.pin.txt, src/python/ta_r4/job_guard.py, tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/test_job_guard.py, tests/ta_r4/fixtures/qtl_group_fixture.py</files>
  <behavior>
    - Tests 1-7, 12, 13 on tmp_path fake prefixes with exactly one change each (<context>); tests 8-11 against the real
      envs (skip only when /rs1 is absent, as the other r4_heavy tests)
    - blas_pinned=True keeps every refusal of tests 2-6; blas_pinned=False reads no BLAS and records not_checked
  </behavior>
  <action>
    0. Record Q-158R6G (before any code edit). `sha256sum` the 2026-11-26 reply = e766bbbd…8a24, else STOP. The gate
       stages that file by its full name (not a `Q-158R6G-reply-*` glob, which would also match the 2026-11-25 file);
       if gate_158.sh stages by glob, the Q-158R6G entry names the file explicitly. Extend
       `$Q8/gate_158.sh` with `Q[Q-158R6G]` = line 1 of the file after `Question Q-158R6G (2026-11-26): ` (copied with
       `sed -n '1s/^Question Q-158R6G (2026-11-26): //p'`, not retyped), `S[Q-158R6G]=e766bbbd642280d55e7e176b5887be2b033b9ac65d219a66e102b86a995d8a24`,
       `L[Q-158R6G]="A: BLAS check only for r_coloc rules (Recommended)"`. Run `bash $Q8/gate_157j.sh` and
       `bash $Q8/gate_158.sh Q-158R6S Q-158R6G` → `$Q8/gate_15_8b_r6g.txt` (rc 0). NCs as 15.8a4 did
       (`$Q8/gate_nc_15_8b.txt`): one byte changed in the copy (GATE_NC_MUTATE=1), another label, one sha256
       character changed, the question typed with its leading QID → each exit 2; then the real gate rc 0.
       DECISIONS.md: append a new entry at the end, as the Q-158* entries are written (grep Q-158R6S, Q-158EL):
       `## 2026-11-26 — DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only: the job guard checks the libopenblas pin
       only in gated jobs of rules whose conda env is envs/r_coloc.yml; r4_qtl_aggregate and r4_qtl_tiers record that
       the BLAS was not checked (Carter, Q-158R6G A)`; bullets: Decider (Carter 2026-11-26, answering the 15.8b Task 1
       step 3 STOP; gated via gate_158.sh, NCs gate_nc_15_8b.txt); the reply path and sha256 with its mapping (R6 →
       15.8b, scope of DEC-2026-11-24-ta-r4-w3f-15-8-open-items narrowed for the guard only; the pin stays r_coloc
       only per Q-158R6S); the flag is derived from each rule's conda directive (rule_gate), the measured partition;
       Not authorized (as the 15.8 entries: no production fit, no OSF posting, no W4a-T3 lock; decision_rules.yaml
       stays locked: false; n_regions_min stays 7; no re-pin to make a check pass; lifts nothing under D-28). The quote
       is written by `{ printf '\n```text\n'; cat "$P/W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt"; printf '```\n'; } >> .planning/DECISIONS.md`
       (never retyped); then extract the lines between that block's fences into `$Q8/dec_quote_15_8b.txt` and
       `cmp` it with the reply file (equal, else STOP). Commit the reply file and DECISIONS.md, explicit paths:
       `docs(ta-r4-W3f): Q-158R6G gated (A) and recorded as DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only (15.8b)`.
    1. RED: tests 1-7, 9-13 (`$Q8/red_15_8b.txt`; each fails or errors on import: no libopenblas_pin / blas_facts /
       blas_pinned parameter / `--blas-pinned` / pin file / manifest). Test 8 passes at RED because the locator was
       committed in Task 1; its evidence is a negative control instead (step 5 NC 0).
    2. `qtl_group_fixture._job_env` → `conda_job_env.job_env_dir(REPO_ROOT / "envs/r_coloc.yml")` plus an existence
       assert (fixture builder). Before step 3, check the 5 importers collect (the locator still returns 0f343627).
    3. envs/r_coloc.yml: one line `  - libopenblas=0.3.34` after `r-base`. Pin file: `$CONDA list --explicit --md5 -p
       /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/0f3436279d4146c376747a0ea5bfd4bf_` →
       envs/r_coloc.linux-64.pin.txt (starts with the header lines, then `@EXPLICIT`; 222 URL#md5 lines as measured,
       else STOP). From here until the Task 4 build, the 5 importers are expected to fail collection (<context>); do
       not change them.
    4. job_guard.py: `libopenblas_pin(repo)`; `blas_facts(prefix, probe, r_probe)` (None → default probes: blas_probe
       = `[sys.executable, "-I", "-c", <ctypes openblas_get_config/openblas_get_corename on argv[1]>, <absolute
       realpath of libblas.so.3>]`, never `$CONDA_PREFIX/bin/python3`; r_blas_probe = `$CONDA_PREFIX/bin/Rscript -e
       'cat(extSoftVersion()[["BLAS"]])'`); `blas_violations(facts, pin)` (runtime version token compared exactly:
       `config.split()[1] == pin`; a missing bin/Rscript is a violation); `BLAS_NOT_CHECKED_REASON = "no
       --blas-pinned: the rule's conda env is not envs/r_coloc.yml, so the job runs no R and its BLAS is not pinned
       (Q-158R6G A)"`. `check(…, blas_pinned, blas_probe=None, r_blas_probe=None)`: blas_pinned is keyword-only and
       required, `is True` or `is False` (else JobGuardError). After kernel_env_violations: if True, read the pin and
       `environ.get("CONDA_PREFIX")`, call blas_facts/blas_violations, raise JobGuardError listing every violation (one
       message per check, each distinct), set `rec["blas"] = {"status": "pinned", …facts}` and
       `checked["blas_pinned"] = True`; if False, call none of libopenblas_pin / blas_facts / blas_violations / a
       probe, set `rec["blas"] = {"status": "not_checked", "reason": BLAS_NOT_CHECKED_REASON}` and
       `checked["blas_pinned"] = "not_checked"`. main(): `c.add_argument("--blas-pinned", action="store_true")` →
       `check(…, blas_pinned=args.blas_pinned)`; the OK line adds `blas pinned` or `blas not_checked`. Update the module
       docstring's usage line. Nothing else changes. test_job_guard.py: `_check` per <context> (default
       blas_pinned=True); the declared edits of test_guard_writes_the_record (`"blas_pinned": True`) and
       test_gate_command_production_is_the_guard (call gains `blas_pinned=False`, which gate_command accepts only after
       Task 3, so this one id is RED until Task 3 step 2; record that in red_15_8b.txt).
    5. Default probe on the existing env (scratch, sbatch cascadelake, `$Q8/default_probe_15_8b.txt`):
       `blas_violations(blas_facts(<0f343627 env>, None, None), "0.3.34") == []` and the facts' corename is SkylakeX.
       Tests 1-7, 12, 13 and test_job_guard.py (except the id named in step 4) green. NCs (`$Q8/nc_15_8b.txt`),
       md5-restore each: (0) job_env_dir without `realpath(prefix)` in the hash → test 8 fails (sbatch); (1)
       `libopenblas_pin` returns a hard-coded "0.3.34" → test 1 fails; (2) conda-meta version comparison removed →
       test 2 fails; (3) symlink check removed → test 3 fails; (4) missing CONDA_PREFIX treated as pass → test 4
       fails; (5) runtime version compared as a prefix (`startswith`) → test 5 fails; (6a) missing Rscript treated as a
       skip → test 6 fails; (6b) R-BLAS comparison removed → test 6 fails; (7) the flagged branch skipped (`if
       blas_pinned:` → `if False:`) → tests 2-7 fail; (8) the unflagged branch calls blas_facts → test 12 fails; (9) the
       unflagged branch writes no `blas` / `checked.blas_pinned` field → test 12 fails; (10) `--blas-pinned` ignored
       (always False) → test 13 fails, and default True → test 13 fails; (11) the default blas_probe uses
       `$CONDA_PREFIX/bin/python3` → the default-probe check above fails (FileNotFoundError; recorded).
    6. Commit (`feat(ta-r4-W3f): pin libopenblas in r_coloc.yml + exact pin file; job guard refuses another BLAS when
       --blas-pinned, records not_checked otherwise (15.8b)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158R6S Q-158R6G && git ls-files --error-unmatch .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt && cmp data/r4/tmp/w3f/q158/dec_quote_15_8b.txt .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_job_guard_blas.py tests/ta_r4/test_job_guard.py -q -p no:cacheprovider -m "not r4_heavy" --deselect tests/ta_r4/test_job_guard.py::test_gate_command_production_is_the_guard</automated>
  </verify>
  <done>Q-158R6G committed with a cmp-equal DEC quote; pin and pin file committed; with --blas-pinned each unit test isolates one violation and fails under its own mutation; without it the guard reads no BLAS and records not_checked with a reason; the default probe runs under the guard's interpreter; the fixture locates the env by hash.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: gate_command --blas-pinned derived from each rule's conda directive; call sites; derivation tests (RED first)</name>
  <files>src/python/ta_r4/commands.py, src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk, src/snakemake/rules/ta_r4_sim.smk, src/snakemake/rules/ta_r4_qtl.smk, tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/test_in_job_gate.py</files>
  <behavior>
    - Test 14 (unit): is_r_coloc_env / gate_command flag and ValueErrors
    - Tests 15-16 (r4_heavy, sbatch cascadelake): the flag follows Snakemake's record of each rule's conda directive;
      a flagged gate refuses another BLAS end to end; an unflagged gate passes and records not_checked
  </behavior>
  <action>
    1. Re-verify the gated rules: `grep -n "gate_command\|_r4_qtl_gate_cmd(\|conda:" src/snakemake/rules/ta_r4_*.smk`
       equals <context> (7 call sites; 5 r_coloc; aggregate/tiers without `conda:`), else STOP. Measure the truth
       source (sbatch): build the test_in_job_gate gate repo, dry-run it with `--use-conda --conda-frontend conda
       --conda-prefix <tmp>` (condabin first on PATH) → `$Q8/dryrun_conda_15_8b.txt`; every r_coloc job block has
       `    conda-env: <tmp>/<hash>_` equal to job_env_dir(<gate repo>/envs/r_coloc.yml, <tmp>), aggregate/tiers
       blocks have none, and `<tmp>` is still empty afterwards. If not, STOP (test 15's truth source is not what the
       plan assumes).
    2. RED: tests 14-16 and the declared edits of test_gate_command_stages, test_production_shell_begins_with_the_gate
       and test_gate_in_a_job_fails_after_locked_path_drift (<context>) → `$Q8/red_15_8b_t3.txt` (14 fails on the
       missing is_r_coloc_env / blas_pinned; 15 fails because no gate has `--blas-pinned`; 16 fails because the
       finemap gate passes no `--blas-pinned`). Add the `rendered_conda` module fixture (fixture builder).
    3. commands.py: `R_COLOC_YML = "envs/r_coloc.yml"`; `is_r_coloc_env(conda_env, basedir)` (None → False; a str or
       os.PathLike that is absolute → `os.path.realpath(conda_env) == os.path.realpath(Path(basedir) / R_COLOC_YML)`;
       relative, callable or any other type → ValueError naming the value; Snakemake 7.32.4 stores our directives as
       absolute str, <context>); `gate_command(stage, arm=None, config=None, label=None, *, blas_pinned=None)`:
       repro → ["true"] (blas_pinned ignored); production additionally raises ValueError unless `blas_pinned is True or
       blas_pinned is False`, and appends `"--blas-pinned"` after `--label LABEL` iff True; docstring states the
       Q-158R6G rule. `rule_gate(workflow, rule, stage, arm, config, wildcards)` = `shlex.join(gate_command(stage, arm,
       config, label=job_label(rule, wildcards), blas_pinned=is_r_coloc_env(workflow.get_rule(rule).conda_env,
       workflow.basedir)))` for production, `shlex.join(["true"])` for repro (no conda lookup needed). No rule list
       in commands.py.
    4. Call sites (each rule name typed once, as today's label): ta_r4_finemap.smk:55 `gate=lambda w:
       r4cmd.rule_gate(workflow, "r4_run_finemap", STAGE, ARM, config, w)`; ta_r4_coloc.smk:68 and :99 likewise
       ("r4_coloc_pair", "r4_coloc_A1"); ta_r4_sim.smk:64 ("r4_sim"); ta_r4_qtl.smk `_r4_qtl_gate_cmd(rule)` →
       `r4cmd.rule_gate(workflow, rule, arm_stage(fa), fa, config, w)`. No `conda:` directive, shell line or other
       param changes; aggregate and tiers stay without a conda env. After this step no `.smk` calls gate_command
       directly (`grep -c "gate_command" src/snakemake/rules/ta_r4_*.smk` all 0; recorded as a count, test 15 is the
       enforcer).
    5. Green (sbatch cascadelake, `-t 01:00:00 --mem=16G`): test 14, test_job_guard.py (incl.
       test_gate_command_production_is_the_guard), and test_in_job_gate.py except
       test_gate_in_a_job_fails_after_locked_path_drift, which is expected to fail until the Task 4 build (its flagged
       gate's CONDA_PREFIX is the located env; <context>), run with `-v -p no:cacheprovider` → `$Q8/t3_15_8b.txt`. NCs (`$Q8/nc_15_8b.txt`, appended;
       md5-restore each; heavy ones under sbatch with a fresh module run):
       (12) is_r_coloc_env always False → test 14 and test 15 fail; (13) gate_command appends the flag for
       blas_pinned=False too → test 14 fails; (14) **a gated r_coloc rule loses its flag**: ta_r4_sim.smk:64 changed to
       `lambda w: shlex.join(r4cmd.gate_command(STAGE, ARM, config, label=r4cmd.job_label("r4_sim", w),
       blas_pinned=False))` → test 15 fails on r4_sim; (15) **the flag added to aggregate**: `_r4_qtl_gate_cmd` passes
       `blas_pinned=True` for rule == "r4_qtl_aggregate" (bypassing rule_gate's derivation) → test 15 fails (the iff);
       (16) **tiers gains the r_coloc env**: `conda: str(Path(workflow.basedir) / "envs" / "r_coloc.yml")` added to
       r4_qtl_tiers → test 15 fails (the measured partition) and the derivation flags it; (17) the finemap call site
       renders `blas_pinned=False` → test 16 fails (the named env is not refused).
    6. Commit (`feat(ta-r4-W3f): gate_command --blas-pinned derived from each rule's conda directive; aggregate/tiers
       record BLAS not_checked (15.8b, Q-158R6G A)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ! grep -q "gate_command" src/snakemake/rules/ta_r4_finemap.smk src/snakemake/rules/ta_r4_coloc.smk src/snakemake/rules/ta_r4_sim.smk src/snakemake/rules/ta_r4_qtl.smk && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_job_guard_blas.py tests/ta_r4/test_job_guard.py -q -p no:cacheprovider -m "not r4_heavy" && grep -q "test_in_job_gate.py::test_gate_blas_flag_follows_each_rules_conda_directive PASSED" data/r4/tmp/w3f/q158/t3_15_8b.txt && grep -q "test_in_job_gate.py::test_flagged_gate_refuses_another_blas_and_unflagged_gate_records_not_checked PASSED" data/r4/tmp/w3f/q158/t3_15_8b.txt</automated>
  </verify>
  <done>Every gated rule renders its gate through rule_gate; `--blas-pinned` appears exactly for the five r_coloc rules, as Snakemake's own conda-env record says; losing the flag on an r_coloc rule, or adding it to aggregate or tiers, each fails test 15 (seen); a flagged gate refuses the 0.3.32 env and an unflagged gate records not_checked, end to end.</done>
</task>

<task type="auto">
  <name>Task 4: Build the env (isolated) + identity proof (no fit); manifest; DRAFT (k); FULL; records (STOP for Carter on any difference)</name>
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
       .so sha256 and the Task 1 corename (SkylakeX). Run tests 8-11 and 15-16 on Cascade Lake (sbatch), plus
       test_job_guard.py, the whole test_in_job_gate.py (test_gate_in_a_job_fails_after_locked_path_drift now passes)
       and the 5 qtl_group_fixture importers (they now collect and pass). NCs (md5-restore each): one yaml byte
       changed in a tmp copy, and another prefix → job_env_dir gives a different dir that does not exist (test 8's
       identity would fail); one manifest row perturbed in a tmp copy → test 11 fails; one URL#md5 line changed in a
       tmp pin copy → test 10 fails.
    3. **STOP** (checkpoint:human-action semantics, stops even under --auto) on any difference in 1-2: print the diff,
       present Q-158R6, write nothing more, wait for Carter's reply file. Do not re-pin; delete neither env; run no fit.
    4. DRAFT (k): `with `OPENBLAS_CORETYPE` set, or under a run configuration` (assert unique) → `with
       `OPENBLAS_CORETYPE` set, with an OpenBLAS library other than version 0.3.34 in a job that runs in the R
       environment (the version is pinned there, with its exact package list), or under a run configuration`, plus,
       after that sentence, `The jobs that run in the R environment, and so are checked against the pinned OpenBLAS,
       are fine-mapping, trait-pair colocalization (SuSiE and A1), simulation and QTL colocalization; the QTL
       aggregation and tier jobs run no R, and their job records state that the OpenBLAS library was not checked.` (one script; the old string asserted unique). test_amendment_text.py,
       test_prelock_pilot_fits.py green; a framing or length failure is STOP (not reworded to pass).
    5. `$Q8/close.sh 15_8b` under sbatch; `$Q8/check_15_8b.py` (base full_15_8a4.xml, its actual totals; NEW = the 16
       ids of <new_tests>; declared = the 11 ids of <new_tests>). Records: LOG (Task 1 measurement with Slurm 2101499,
       Q-158R6G and its DEC, the flag derivation and measured partition, identity and its NC, the r_coloc users count,
       the setup-envs.sh note, conda_pkgs before/after, NCs, check); PLAN-INDEX 15.8b row; STATE (NEXT = 15.8c; NOT
       PUSHED); SUMMARY with `## Declared spec updates` and `## New test ids` (junit-form ids, one per line), and a
       `## Track B / m3` section recording: 23 Track B rules use envs/r_coloc.yml; .snakemake/conda has 0 staged
       yamls; bin/setup-envs.sh's phase-2 fallback solves staged yamls, not the pin file; Track B and m3 rebuild this
       env on their next run (from the pin file at libopenblas 0.3.34 via Snakemake). Also a `## Q-158R6G` section:
       which rules are BLAS-checked and that aggregate/tiers records say not_checked. fsck; commit explicit paths.
       No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8b.py && grep -q "libopenblas=0.3.34" envs/r_coloc.yml && test -s envs/r_coloc.linux-64.pin.txt && grep -q "Using pinnings from" data/r4/tmp/w3f/q158/env_build_15_8b.log && ! grep -q "Failed to install" data/r4/tmp/w3f/q158/env_build_15_8b.log && cmp data/r4/tmp/w3f/q158/conda_pkgs_before_15_8b.txt data/r4/tmp/w3f/q158/conda_pkgs_after_15_8b.txt</automated>
  </verify>
  <done>The r4 R job env is pinned to the BLAS it loads and rebuilt with an identical package list and library file, the identity check is shown to fail on the old env, and the guard enforces the pin in every r_coloc gated job while aggregate/tiers records say not_checked; or Carter has the diff.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| env recipe → numerical results | a rebuilt env may load another BLAS kernel and move non-converged fits |
| job env → shared conda cache | conda clean on a shared pkgs dir |
| rule definition → gate flag | a rule's conda directive decides whether its job is BLAS-checked |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158b-01 | Tampering | silent yaml-solve fallback from the pin file | mitigate | `.pin.txt` sibling byte-equal, `.yaml` sibling absent, log scan, URL#md5 identity; identity script seen to fail on the old env; STOP on difference |
| T-r4-158b-02 | Tampering | numeric drift after rebuild | mitigate | identical URL#md5 package list and identical libopenblas .so sha256 to the env of the 17 kernel runs; no new fit |
| T-r4-158b-03 | Denial of service | shared conda pkgs cache wiped | mitigate | no --conda-cleanup-pkgs; CONDA_PKGS_DIRS/CONDARC isolated; /rs1/researchers/c/ckclinto/conda_pkgs entry count + sorted-ls sha256 before == after |
| T-r4-158b-04 | Elevation | an r_coloc job runs with an unpinned BLAS | mitigate | with --blas-pinned the guard refuses on version, symlink, exact runtime version token, missing Rscript or R-reported BLAS mismatch; each check isolated by its own test and NC; test 16 end to end |
| T-r4-158b-05 | Elevation | a gated r_coloc rule renders its gate without --blas-pinned | mitigate | the flag is derived in rule_gate from workflow.get_rule(rule).conda_env; test 15 compares it with Snakemake's own conda-env record and the measured partition; NCs 14-16 seen failing |
| T-r4-158b-06 | Repudiation | an unchecked BLAS looks checked or leaves no trace | mitigate | unflagged records carry checked.blas_pinned "not_checked" and blas.reason (test 12, test 16); DRAFT (k) states it |
</threat_model>

<verification>
- check_15_8b.py passes; Q-158R6G gated and its DEC quote cmp-equal; identity recorded with its negative control; the
  shared conda cache unchanged; the flag derivation and its NCs recorded; no fit run.
</verification>

<success_criteria>
- A production job of an r_coloc rule can only run against the pinned OpenBLAS in the recorded job env; a gated job
  without that env says in its record that its BLAS was not checked.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-SUMMARY.md`
</output>
