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
  - src/python/ta_r4/conda_job_env.py          # DONE in Task 1 (e47b6a83); used by the fixture and tests 8-11, 15, 16
  - src/python/ta_r4/job_guard.py              # Task 3
  - src/python/ta_r4/commands.py               # gate_command(blas_pinned=) + is_r_coloc_env + rule_gate (Task 4)
  - src/snakemake/rules/ta_r4_finemap.smk      # gate param -> r4cmd.rule_gate (Task 4)
  - src/snakemake/rules/ta_r4_coloc.smk        # r4_coloc_pair, r4_coloc_A1 gate params -> r4cmd.rule_gate (Task 4)
  - src/snakemake/rules/ta_r4_sim.smk          # r4_sim gate param -> r4cmd.rule_gate (Task 4)
  - src/snakemake/rules/ta_r4_qtl.smk          # _r4_qtl_gate_cmd -> r4cmd.rule_gate (Task 4)
  - tests/ta_r4/test_job_guard_blas.py         # tests 8, 10, 11 (Task 2); 1-7, 9, 12, 13 (Task 3); 14 (Task 4)
  - tests/ta_r4/test_job_guard.py              # `_check` helper (fixture builder) + 2 declared spec updates
  - tests/ta_r4/test_in_job_gate.py            # tests 15-16 + `rule_envs` fixture + 3 declared spec updates (9 ids)
  - tests/ta_r4/fixtures/rule_conda_envs.py    # Snakemake's own parsed conda directive per rule (test 15's truth source)
  - tests/ta_r4/fixtures/qtl_group_fixture.py  # `_job_env` uses the locator (fixture-builder edit)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt  # the only new reply file (Q-158R6G files committed in 4e47c20d)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-PLAN.md  # committed at Task 2 step 0 (HEAD records the plan executed)
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
    - "Gates Q-157J, Q-158R6S (`Proceed, pin r_coloc only (Recommended)`, sha256 7b3d1045…5b2d), Q-158R6G (`A: BLAS check only for r_coloc rules (Recommended)`, sha256 e766bbbd…8a24) and Q-158KW (`Approve as written (Recommended)`, sha256 1f641dcc…b99a) pass (15.8 protocol); otherwise nothing is edited. The Q-158R6G DEC (DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only) is in 4e47c20d and is not edited; Q-158KW is recorded in a follow-on entry, DEC-2026-11-26-ta-r4-draft-k-blas-wording, whose quote is cmp-equal to its reply file"
    - "Only envs/r_coloc.yml (shared with Track B and m3) gains a pin and a pin file; python_stats, plink and qtl_processing are not pinned (Carter Q-158R6S). The BLAS check runs only in gated jobs of rules whose conda directive is envs/r_coloc.yml (Carter Q-158R6G A); there it fails closed if the job env drifts from the pin. The SUMMARY and LOG record (measured in Task 1, data/r4/tmp/w3f/q158/r_coloc_users_15_8b.txt): 23 rules outside ta_r4 use envs/r_coloc.yml; .snakemake/conda holds 0 staged yamls (0 env dirs built from the current r_coloc.yml); bin/setup-envs.sh's phase-2 fallback walks only staged *.yaml files, so on that path Track B solves the yaml, not the pin file (libopenblas version held by the pin line; build strings not held); Track B and m3 rebuild their r_coloc env on their next Snakemake run from the same pin file at the same libopenblas version"
    - "One locator, `conda_job_env.job_env_dir(yml, prefix)` = `<prefix>/<md5(realpath(prefix) + yaml bytes)>_` (committed e47b6a83), equal to Snakemake 7.32.4's Env(...).address for the same yaml and conda prefix (measured, locator_15_8b.txt LOCATOR_OK; test 8, whose first assertion is that equality, seen failing under a hash mutation while the yaml is unedited); it raises if `envs/r_coloc.post-deploy.sh` exists; it is used by the qtl_group_fixture and tests 8-11, 15, 16; before the yaml edit it returns 0f3436279d4146c376747a0ea5bfd4bf_"
    - "Measured in Task 1 (Slurm 2101499, c020n02, Xeon Gold 6226R Cascade Lake; blas_measure_15_8b.txt, blas_probe_15_8b_2101499.out), env 0f343627 activated with miniconda3/bin/activate: conda-meta libopenblas-0.3.34-pthreads_hf13c14d_2; lib/libblas.so.3, liblapack.so.3, libcblas.so.3, R's extSoftVersion()['BLAS'] and La_library() all realpath to lib/libopenblasp-r0.3.34.so (sha256 f1424288…572b); openblas_get_config `OpenBLAS 0.3.34 DYNAMIC_ARCH NO_AFFINITY SkylakeX MAX_THREADS=128`; corename and the OPENBLAS_VERBOSE=2 Core line SkylakeX; 222 @EXPLICIT lines. The env has no bin/python3, so the ctypes probe ran under smoke_dev python3.11 -I"
    - "One conda binary, /rs1/researchers/c/ckclinto/miniconda3/condabin/conda, makes the pin file and every explicit list in Task 2 and test 10. envs/r_coloc.yml pins `libopenblas=0.3.34`; envs/r_coloc.linux-64.pin.txt is `conda list --explicit --md5 -p <0f343627 env>`; manifests/env_lock_r_coloc_job.tsv lists every conda-meta package (name, version, build string, channel, md5) of that env, the libopenblas .so sha256 and the measured corename"
    - "The env is built and proven identical in Task 2, before any guard or gate code is edited and before the pin is committed. Env identity, with no fit run, checked by `$Q8/env_identity_15_8b.py <env dir>` (exit 0 = identical): for D = job_env_dir(envs/r_coloc.yml) after the build, `str(D) + \".pin.txt\"` is cmp-equal (byte-exact) to envs/r_coloc.linux-64.pin.txt; `str(D) + \".yaml\"` is absent; the build log has 'Using pinnings from' and not 'Failed to install'; the `@EXPLICIT` URL#md5 lines of `conda list --explicit --md5 -p D` equal those of the repo pin file (the `# created-by` header is not compared); D's libopenblasp-r<ver>.so sha256 equals the measured env's; D/lib/R/library equals the measured env's (sorted package directory names plus each DESCRIPTION Version). The script prints one PASS/FAIL line per check; its negative controls make each check fail on its own: the old env 0f343627 (sibling checks), a reference pin with one md5 changed (explicit list), the named 0.3.32 env (libopenblas sha256, R library) or a reference tree with one DESCRIPTION Version changed (R library); the named check must be among the FAILs. Any difference on D is a STOP for Carter (Q-158R6) with HEAD at the docs commit of Task 2 step 0 and the shared yaml restored to HEAD"
    - "job_guard.check(…, blas_pinned, blas_probe=None, r_blas_probe=None); CLI flag `--blas-pinned` → blas_pinned=True, absent → False. With blas_pinned=True it refuses a production job when: CONDA_PREFIX is unset; conda-meta has zero libopenblas records, several, or one of a version other than the pin; libblas.so.3 or liblapack.so.3 does not resolve to that env's libopenblasp-r<pin>.so; the runtime config's version token is not exactly the pin (`config.split()[1] == pin`, not a prefix match); `$CONDA_PREFIX/bin/Rscript` is missing (a violation, not a skip); or the BLAS R itself reports (`Rscript -e 'cat(extSoftVersion()[[\"BLAS\"]])'`, R loads it in its own process; the guard never dlopens it) resolves to another file. Each of these has its own message, its own isolating test case and its own NC. The record gains a `blas` block (status pinned, version, library, config, corename, r_blas) and checked.blas_pinned = true. With blas_pinned=False it calls no BLAS function (no pin read, no conda-meta read, no probe) and the record has checked.blas_pinned = \"not_checked\" and blas = {status: not_checked, reason: BLAS_NOT_CHECKED_REASON}, never an absent field. Both probes are injectable; the default blas_probe runs the ctypes calls in `sys.executable -I -c` (the guard's own interpreter, smoke_dev 3.11), never `$CONDA_PREFIX/bin/python3` (absent in the r_coloc env). The pin is read from envs/r_coloc.yml"
    - "gate_command(…, blas_pinned=) appends `--blas-pinned` iff blas_pinned is True and raises ValueError (message naming blas_pinned) for a production call whose blas_pinned is not exactly True or False. Every gated rule renders its gate through `commands.rule_gate(workflow, rule, stage, arm, config, wildcards)`, which derives blas_pinned from that rule's conda directive (`workflow.get_rule(rule).conda_env`) via `is_r_coloc_env(conda_env, workflow.basedir)` (realpath equal to <basedir>/envs/r_coloc.yml; None → False; relative, callable or other types → ValueError). No hand-kept rule list decides the flag. Test 15 checks the rendered flag of every gated job against Snakemake's own parsed directive of its rule (tests/ta_r4/fixtures/rule_conda_envs.py: an in-process Snakemake 7.32.4 Workflow + include, no DAG, no rule_gate call), comparing realpaths itself; and it pins the measured partition of Q-158R6G: flagged == {r4_run_finemap, r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group} (non-empty, so the iff cannot pass vacuously), unflagged == {r4_qtl_aggregate, r4_qtl_tiers}. Test 15 fails when a gated r_coloc rule loses the flag and when aggregate or tiers gains it, each seen failing"
    - "DRAFT (k) carries exactly the wording Carter approved in Q-158KW: `with `OPENBLAS_CORETYPE` set, with an OpenBLAS library other than version 0.3.34 in a job that runs in the R environment (the version is pinned there, with its exact package list), or under a run configuration` followed by the sentence `The QTL aggregation and tier jobs run no R; their job records state that the OpenBLAS library was not checked.`; old string asserted unique; any other wording is a STOP for Carter"
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
    - path: "tests/ta_r4/fixtures/rule_conda_envs.py"
      provides: "{rule: conda_env} from Snakemake's own parse of Snakefile.ta_r4 (test 15's truth source)"
    - path: ".planning/DECISIONS.md"
      provides: "the DEC entry with the byte-exact Q-158R6G and Q-158KW quotes"
      contains: "Q-158KW"
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
    - from: "tests/ta_r4/test_in_job_gate.py::test_gate_blas_flag_follows_each_rules_conda_directive"
      to: "tests/ta_r4/fixtures/rule_conda_envs.py"
      via: "subprocess under smoke_dev python3.11; JSON {rule: conda_env}"
      pattern: "rule_conda_envs"
---

<objective>
Close review R6 as Carter chose (Q-157J "R6: pin libopenblas"; Q-158R6S; Q-158R6G A; Q-158KW). The job guard checks
the CPU but not the BLAS library, and the committed env lock describes the named r_coloc env (OpenBLAS 0.3.32), while
jobs run in the Snakemake-built env (0.3.34). This plan measured what the jobs load (Task 1, done), pins it in
envs/r_coloc.yml with an exact pin file, rebuilds the env and proves it identical to the measured one by its package
list and library hash before any guard code changes, records the job env's lock, and then makes the guard refuse any
other BLAS in every gated job whose rule runs in the r_coloc env. The two gated QTL rules without a conda env
(r4_qtl_aggregate, r4_qtl_tiers) keep today's guard and their job record says the BLAS was not checked (Q-158R6G A).
No fit is run (a new pre-lock fit would fall outside the approved F15 paragraph's "17 runs"); any env difference
stops for Carter.
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
`W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt`, sha256
`e766bbbd642280d55e7e176b5887be2b033b9ac65d219a66e102b86a995d8a24`, label `A: BLAS check only for r_coloc rules (Recommended)`.
**Already gated and recorded in 4e47c20d** (by an executor of the earlier plan version): both Q-158R6G reply files
(2026-11-26, and the earlier wording 2026-11-25, sha256 1cdfc554…55fa, label `A: check only r_coloc rules
(Recommended)`) are committed; `gate_158.sh` has the `F[Q-158R6G]` entry; DECISIONS.md:3832 holds
`DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only` with both quotes cmp-checked and a "How the flag is set" bullet.
This plan re-runs the Q-158R6G gate and never edits or re-quotes that entry. (caa5e6e3, the same executor's pin +
guard commit made out of order, was reverted in 5ee7efe0; envs/, src/ and tests/ equal e47b6a83 and no pinned env
dir exists.)
The option as shown to Carter: "Run the BLAS check only for the gated rules that use the r_coloc env (r4_run_finemap,
r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group). Aggregate and tiers keep today's guard, and their job record says
the BLAS was not checked. The plan's must_haves and tests get revised, then 15.8b resumes at Task 2."
Q-158KW (answered 2026-11-26, the DRAFT (k) wording): file `W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt` (untracked
until Task 2 step 0), sha256 `1f641dccebaae2f6539a9e563330546e2f6867767093011e12f574e2f378b99a`, label
`Approve as written (Recommended)`; question text = line 1 after `Question Q-158KW (2026-11-26): `. It approves exactly
the Task 5 step 1 replacement and new sentence; any change to that wording is a STOP for Carter.
Task 2 question (only on a STOP), QID Q-158R6, file `W3f-carter-15-8-Q-158R6-reply-<date>.txt`: "The env Snakemake built
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
@Snakefile.ta_r4
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
no re-pin to make a check pass; no `git add .` / `-A`, explicit paths only; no `git reset`). Scope stays Q-158R6S:
only envs/r_coloc.yml is pinned. Every heavy run (pytest r4_heavy, BLAS probes, dry-runs and Snakemake parses used as
evidence, the env build, FULL) goes through `sbatch -p compute -A clintonlab_cpu -q normal -t <limit>
--constraint=cascadelake`. Memory rules reference_snakemake_conda_clean_tarballs_shared_cache (isolate pkgs_dirs),
feedback_verify_assumption_before_shipping, feedback_a_claimed_invariant_needs_a_named_enforcer,
feedback_green_assertion_needs_a_negative_control, feedback_negative_control_defeated_by_bytecode_cache (run every NC
with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`). **No fit is run in this plan.**
`CONDA=/rs1/researchers/c/ckclinto/miniconda3/condabin/conda` everywhere a conda command is named.

**Task 1 measurements (DONE; files in `$Q8` = data/r4/tmp/w3f/q158):** start_15_8b.txt (HEAD 82339a6d before Task 1);
gate_15_8b.txt (Q-157J and Q-158R6S gates rc 0); locator_15_8b.py/.txt (job_env_dir == Snakemake Env.address ==
…/0f3436279d4146c376747a0ea5bfd4bf_, sibling `_.yaml` cmp-equal, LOCATOR_OK); blas_probe_15_8b.sh,
blas_probe_15_8b_2101499.out and blas_measure_15_8b.txt (must_haves truth 4; `libopenblas_version=0.3.34`,
`corename=SkylakeX`, `libopenblas_sha256=f1424288e9ac125331102c0150b66fbd244560987779552e0e97d5cfd9de572b`;
`$CONDA_PREFIX/bin/python3: No such file or directory`, so the ctypes probe fell back to smoke_dev python3.11 -I);
r_coloc_users_15_8b.py/.txt (23 rules outside ta_r4; `snakemake_conda_dir_exists=True n_yaml=0`;
`env_dirs_built_from_current_r_coloc_yml=0`). The other envs in the prefix (plink 55c377a7, python_stats 8f7292f9,
qtl_processing dc880444) are not used by any gated rule and also carry libopenblas-0.3.34-pthreads_hf13c14d_2.

**Gated rules (verified by the planner from the .smk files; Task 4 step 1 re-verifies).**
`grep -n "gate_command(\|_r4_qtl_gate_cmd(" src/snakemake/rules/ta_r4_*.smk` prints exactly these 9 lines (file:line,
in grep's file order):
`ta_r4_sim.smk:64` (r4_sim gate, `gate_command(`), `ta_r4_qtl.smk:63` (`def _r4_qtl_gate_cmd(rule):`),
`ta_r4_qtl.smk:67` (the helper's `gate_command(`), `ta_r4_qtl.smk:122` (`_r4_qtl_gate_cmd("r4_qtl_group")`),
`ta_r4_qtl.smk:143` (`_r4_qtl_gate_cmd("r4_qtl_aggregate")`), `ta_r4_qtl.smk:167` (`_r4_qtl_gate_cmd("r4_qtl_tiers")`),
`ta_r4_finemap.smk:55` (r4_run_finemap), `ta_r4_coloc.smk:68` (r4_coloc_pair), `ta_r4_coloc.smk:99` (r4_coloc_A1)
— 5 `gate_command(` lines, 1 def, 3 helper uses. The 7 gated rules: r4_run_finemap (`conda:` envs/r_coloc.yml,
finemap.smk:49-50), r4_coloc_pair and r4_coloc_A1 (`conda: _R4_COLOC_ENV` = envs/r_coloc.yml, coloc.smk:14, :62, :93),
r4_sim (sim.smk:58-59), r4_qtl_group (qtl.smk:116-117), and r4_qtl_aggregate, r4_qtl_tiers (no `conda:` directive;
`py=sys.executable`: smoke_dev 3.11, pip numpy/scipy with their own scipy_openblas, no R). This equals
test_in_job_gate.PRODUCTION_RULES. Snakemake 7.32.4 stores the directive as given (workflow.py:1688-1705: a Path
becomes str; `rule.conda_env = ruleinfo.conda_env`), so for these rules `workflow.get_rule(name).conda_env` is the
absolute string `<basedir>/envs/r_coloc.yml` or None. `workflow.get_rule` raises on an unknown name, so a rule name
typed into rule_gate that is not a rule fails at render time.
**Truth source for test 15 (replaces the dry-run `conda-env:` line, which Snakemake 7.32.4 prints only in
`job_error()`, logging.py:523-537, never in `job_info()`, :428-462).** `tests/ta_r4/fixtures/rule_conda_envs.py <repo>
<arm>`, run as a subprocess under `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11` with cwd = repo:
`wf = snakemake.workflow.Workflow(snakefile=<repo>/Snakefile.ta_r4, overwrite_configfiles=[abs paths of
job_guard.CONFIG_FILES(arm)], overwrite_config=job_guard.merged_config_from_files(repo, arm), config_args=None)`;
`wf.include(<repo>/Snakefile.ta_r4, overwrite_default_target=True)`; print JSON `{rule.name: rule.conda_env if
isinstance(rule.conda_env, str) or rule.conda_env is None else "<non-str:" + type name + ">"}` for every rule in
`wf.rules`. This is Snakemake's own parse of each `conda:` directive. It builds no DAG, evaluates no params lambda and
never calls rule_gate or commands.is_r_coloc_env; Snakefile.ta_r4's top level only reads files (regions csv, pair
manifest) and checks the configfile list (:31-36), and the lock gate runs only in input functions. The test decides
"r_coloc" itself: `os.path.realpath(env) == os.path.realpath(<repo>/envs/r_coloc.yml)`.

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
  oriented path; the `_job_env` edit here is separate and must keep that copy block unchanged.) **Because Task 2 builds
  the located env before its commit, the 5 importers collect and pass at every commit of this plan**; there is no
  window in which HEAD has them failing.
- tests/ta_r4/test_job_guard.py: `_check` helper :89-91 calls `job_guard.check(REPO_ROOT, ARM, digest, environ=…,
  cpuinfo=…, record_dir=…, label=…)`; test_guard_writes_the_record :107-121 asserts
  `rec["checked"] == {"lock_gate": True, "config_digest": True, "cpu_cascadelake": True, "kernel_env": True}` →
  declared spec update in Task 3 (the dict gains `"blas_pinned": True`). `_check` gains `blas_pinned=True` (default),
  builds a valid fake prefix and merges its `CONDA_PREFIX` into whatever `environ` the caller passes (or CLEAN_ENV),
  unless the caller sets `CONDA_PREFIX` itself, and passes stub `blas_probe` / `r_blas_probe` returning the pinned
  values (fixture builder). test_gate_command_production_is_the_guard :138-142 → declared spec update in Task 4 (the
  call gains `blas_pinned=False`; the expected argv is unchanged).
- tests/ta_r4/test_in_job_gate.py (module pytestmark r4_heavy), all declared spec updates in Task 4:
  test_gate_command_stages :177-189 (every production call gains `blas_pinned=False`; each of the three
  `pytest.raises(ValueError)` cases gains `blas_pinned=False` and `match="needs arm, config and label"`, the existing
  message at commands.py:115, so no case can pass on the new blas_pinned ValueError, whose message names
  `blas_pinned`; expected argv unchanged); test_production_shell_begins_with_the_gate[<7 rules>] :126-139 (`want` gains
  `blas_pinned=` from the `rule_envs` record of the job's rule, decided by realpath in the test, not from a list);
  test_gate_in_a_job_fails_after_locked_path_drift :158-174 (both gate subprocesses get `env={**os.environ,
  "CONDA_PREFIX": str(job_env_dir(REPO_ROOT / "envs/r_coloc.yml"))}`, the env Task 2 built; **never the old env
  0f343627**, which the pinned yaml no longer locates; the assertions are unchanged). make_fixture_repo copies
  src/python, envs and every ta_r4_*.smk from the working tree, so a working-tree mutation is seen by a fresh module
  run.
- The gate command runs `sys.executable -m ta_r4.job_guard` (commands._PY) in the job shell. For an r_coloc rule
  Snakemake activated the env, so `CONDA_PREFIX` is the job env; for aggregate/tiers no env is activated and
  CONDA_PREFIX is whatever the launching shell had, which the unflagged guard never reads. The default `blas_probe`
  runs the ctypes calls in a fresh `sys.executable -I -c` subprocess with the absolute library path (the guard process
  never loads that OpenBLAS; sys.executable is smoke_dev 3.11 because the r_coloc env has no python3, Task 1); the
  default `r_blas_probe` runs `$CONDA_PREFIX/bin/Rscript`.
- `$Q8/gate_158.sh` (as extended in 4e47c20d) resolves the reply file as `${F[$QID]:-W3f-carter-15-8-$QID-reply-2026-11-25.txt}`
  and stages it under the same name with `15-8` → `15-7`; gate_reply.py requires the staging name's date to equal line
  1's date (gate_reply.py:38-64), so a 2026-11-26 reply needs an `F[...]` entry. The Q-158R6G entry (`F[Q-158R6G]` =
  the 2026-11-26 file, with `GATE_NC_QUESTION` / `GATE_NC_LABEL` / `GATE_NC_SHA` overrides) is committed; Task 2 step 0
  adds Q-158KW the same way.

**Valid fake prefix (unit tests 2-7):** conda-meta with one `libopenblas-<pin>-…json`; `lib/libopenblasp-r<pin>.so` (a
dummy file); `lib/libblas.so.3`, `lib/liblapack.so.3` → that file; `bin/Rscript` present; `blas_probe` stub returning
`OpenBLAS <pin> DYNAMIC_ARCH …` and a corename; `r_blas_probe` stub returning the dummy file's path. Tests 2-7 call
check with `blas_pinned=True`. Each case of tests 2-6 starts from a fresh valid prefix, changes exactly one of these
and asserts `pytest.raises(JobGuardError, match=<that violation's message>)`, so a removed check cannot be hidden by
another violation.
</context>

<new_tests>
N_new = 16 (one junit id each, no parametrize; multi-case tests loop over fresh tmp prefixes inside one id).
tests/ta_r4/test_job_guard_blas.py:
1. `test_pin_is_read_from_r_coloc_yml` (`libopenblas_pin(<tmp repo whose envs/r_coloc.yml has libopenblas=9.9.9>) ==
   "9.9.9"`; none or two such lines → JobGuardError)
2. `test_guard_refuses_a_libopenblas_version_other_than_the_pin` (blas_pinned=True; three cases, each on a fresh valid
   prefix with one change, each with its own match=: (a) the one conda-meta record is 0.3.32 → the version message;
   (b) no libopenblas conda-meta record → the no-record message; (c) a second libopenblas record (0.3.34 and 0.3.32)
   → the several-records message) — the "flagged rule with the wrong libopenblas refuses" unit case
3. `test_guard_refuses_blas_symlinks_not_to_the_pinned_openblas` (blas_pinned=True; two cases, each on a fresh valid
   prefix: (a) libblas.so.3 → another file → match= the libblas message; (b) liblapack.so.3 → another file, libblas.so.3
   intact → match= the liblapack message)
4. `test_guard_refuses_without_conda_prefix` (blas_pinned=True; match=)
5. `test_guard_refuses_a_runtime_config_of_another_version` (blas_pinned=True; valid prefix, probe stub
   `OpenBLAS 0.3.340 DYNAMIC_ARCH …`, which a prefix comparison would accept; match= the runtime-version message)
6. `test_guard_refuses_a_missing_or_other_r_blas` (blas_pinned=True; two cases, each on a fresh valid prefix with one
   change: `bin/Rscript` removed → match= the missing-Rscript message; `r_blas_probe` returning another file → match=
   the R-BLAS message)
7. `test_guard_record_has_the_blas_block` (blas_pinned=True; valid prefix; check() passes; record has blas.status
   "pinned", blas.version/library/config/corename/r_blas and checked.blas_pinned is True)
8. `test_job_env_locator_equals_snakemake_env_address` (r4_heavy; **first assertion**: `str(job_env_dir(envs/r_coloc.yml,
   R4_CONDA_PREFIX)) == Env(...).address` of `snakemake.deployment.conda.Env` built for the same yaml with a stub
   workflow whose conda prefix is R4_CONDA_PREFIX (as $Q8/locator_15_8b.py); then the dir exists and holds
   `bin/Rscript`; with a tmp `envs/r_coloc.post-deploy.sh`, job_env_dir raises)
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
    `pytest.raises(ValueError, match="blas_pinned")`; `gate_command("repro")` == ["true"])
tests/ta_r4/test_in_job_gate.py (module r4_heavy; uses `rendered` and a new module fixture `rule_envs` = the JSON of
`fixtures/rule_conda_envs.py <gate repo> A3_1kg`, <context>):
15. `test_gate_blas_flag_follows_each_rules_conda_directive` (gated jobs = every job of `rendered` whose first command's
    argv contains `ta_r4.job_guard`; their rule set == PRODUCTION_RULES; every gated rule is a key of `rule_envs` with
    a str or None value; for each gated job, `"--blas-pinned" in argv` iff `rule_envs[rule]` is a str and
    `os.path.realpath(rule_envs[rule]) == os.path.realpath(<gate repo>/envs/r_coloc.yml)`; then the measured
    partition of Q-158R6G: the set of flagged rules is non-empty and == {r4_run_finemap, r4_coloc_pair, r4_coloc_A1,
    r4_sim, r4_qtl_group}, the unflagged set == {r4_qtl_aggregate, r4_qtl_tiers}, and each of the 7 rules has at least
    one rendered gated job)
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
`_job_env`, `rule_envs` and fixtures/rule_conda_envs.py are fixture-builder edits (every test using them keeps its id
and passes).
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
    every gated rule with an env uses 0f343627 at 0.3.34). **Resolved by Carter Q-158R6G A** (BLAS check only for
    r_coloc rules). Step 4: 23 r_coloc rules outside ta_r4; .snakemake/conda has 0 staged yamls. Measurement note for
    Task 3: the r_coloc env has no bin/python3, so the ctypes probe ran under smoke_dev python3.11 with -I.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git cat-file -e e47b6a83 && grep -q "^libopenblas_version=0.3.34$" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^corename=SkylakeX$" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^libopenblas_sha256=f1424288e9ac125331102c0150b66fbd244560987779552e0e97d5cfd9de572b$" data/r4/tmp/w3f/q158/blas_measure_15_8b.txt && grep -q "^LOCATOR_OK$" data/r4/tmp/w3f/q158/locator_15_8b.txt && grep -q "^r_coloc_rule_count_outside_ta_r4=23$" data/r4/tmp/w3f/q158/r_coloc_users_15_8b.txt</automated>
  </verify>
  <done>The locator equals Snakemake's env address; BLAS library, version, kernel and file hash measured in the activated job env on Cascade Lake; the step-3 STOP is answered by Q-158R6G A.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Q-158R6G + Q-158KW record; test-8 NC on the unedited yaml; pin + pin file; isolated build + identity proof; manifest; fixture locator (STOP for Carter on any difference, before any guard code)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-PLAN.md, .planning/DECISIONS.md, envs/r_coloc.yml, envs/r_coloc.linux-64.pin.txt, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_job.tsv, tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/fixtures/qtl_group_fixture.py</files>
  <behavior>
    - Tests 8, 10, 11 (r4_heavy) against the real envs; test 8's address-equality assertion seen failing under a hash
      mutation while the yaml is still unedited
    - The rebuilt env is identical to 0f343627 by pin-file bytes, URL#md5 list, .so sha256 and R library listing
  </behavior>
  <action>
    0. **(a) Archive the prior run first**, before any other step: `mkdir -p $Q8/b/prior_caa5e6e3` and move there
       red_15_8b.txt, nc_15_8b.txt, gate_nc_15_8b.txt, gate_15_8b_r6g.txt and env_build_15_8b.py from `$Q8`; copy (not
       move) dec_quote_15_8b.txt there and keep it at its path (the Task 2 verify cmp's it against the committed 2026-11-26
       Q-158R6G reply); write `$Q8/b/prior_caa5e6e3/MANIFEST.txt` (sha256 of each file, and that they came from the
       executor of the earlier plan version, commits 4e47c20d / caa5e6e3, the latter reverted in 5ee7efe0). Record the
       archive in the Task 5 LOG entry. None of it is evidence for this run.
       **(b) Q-158R6G (already recorded):** `bash $Q8/gate_157j.sh` and the existing Q-158R6G gate are re-run below; the
       committed DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only (DECISIONS.md:3832) is not edited or re-quoted.
       **(c) Q-158KW.** `sha256sum $P/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt` = 1f641dcc…b99a, else STOP. Add to
       `$Q8/gate_158.sh`, in the existing `F[]` style after the Q-158R6G block: `Q[Q-158KW]="$(sed -n '1s/^Question
       Q-158KW (2026-11-26): //p' "$P/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt")"`,
       `S[Q-158KW]=1f641dccebaae2f6539a9e563330546e2f6867767093011e12f574e2f378b99a`,
       `L[Q-158KW]="Approve as written (Recommended)"`, `F[Q-158KW]=W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt`, and
       the three override lines `Q[Q-158KW]=${GATE_NC_QUESTION:-${Q[Q-158KW]}}`, `L[Q-158KW]=${GATE_NC_LABEL:-…}`,
       `S[Q-158KW]=${GATE_NC_SHA:-…}` (no date map). Run `bash $Q8/gate_158.sh Q-158R6S Q-158R6G Q-158KW` →
       `$Q8/gate_15_8b_kw.txt` (rc 0). NCs for Q-158KW alone (`bash $Q8/gate_158.sh Q-158KW` with one override each;
       `$Q8/gate_nc_15_8b.txt`): GATE_NC_MUTATE=1 (one byte of the copy), GATE_NC_LABEL="Other (free text)",
       GATE_NC_SHA with one character changed, GATE_NC_QUESTION = the question with its leading `Q-158KW` → each exit 2
       with the matching GATE FAIL line; then the real three-QID gate rc 0 again.
       **(d) Follow-on DEC.** Append a new entry at the end of DECISIONS.md, as the Q-158* entries are written:
       `## 2026-11-26 — DEC-2026-11-26-ta-r4-draft-k-blas-wording: DRAFT (k) states the OpenBLAS pin for jobs in the R
       environment and the not_checked record of the QTL aggregation and tier jobs, in the wording Carter approved
       (Carter, Q-158KW)`; bullets: Decider (Carter 2026-11-26; gated via gate_158.sh, NCs gate_nc_15_8b.txt); follows
       DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only (Q-158R6G A); the Q-158KW path and sha256; the approved
       replacement and new sentence go into DRAFT (k) exactly as Task 5 step 1 (any change is a new question to Carter);
       Not authorized (no production fit, no OSF posting, no W4a-T3 lock; decision_rules.yaml stays locked: false;
       n_regions_min stays 7; no re-pin to make a check pass; lifts nothing under D-28). The quote, Q-158KW only, is
       written by `{ printf '\n```text\n'; cat "$P/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt"; printf '```\n'; } >>
       .planning/DECISIONS.md` (never retyped); extract the lines between its fences into `$Q8/dec_quote_15_8b_kw.txt`
       and `cmp` it with the reply file (equal, else STOP). `git diff` of DECISIONS.md shows additions only, after
       line 3832's entry.
       **(e) Commit**, explicit paths: the Q-158KW reply, .planning/DECISIONS.md and this PLAN
       (`docs(ta-r4-W3f): Q-158KW gated and recorded as DEC-2026-11-26-ta-r4-draft-k-blas-wording; 15.8b plan as
       executed (15.8b)`). HEAD after this commit records the plan being executed and is the STOP baseline of step 4.
    1. RED (yaml unedited): write tests 8, 10, 11 into tests/ta_r4/test_job_guard_blas.py; run them (sbatch
       cascadelake) → `$Q8/red_15_8b.txt`: 10 fails (no pin file), 11 fails (no manifest); test 8 passes (locator
       committed in Task 1).
    2. **NC 0 for test 8, re-run here before the yaml edit** (the prior run's NC0 is archived, not reused;
       `$Q8/nc_15_8b.txt`; sbatch cascadelake; md5-restore): job_env_dir with
       `realpath(prefix)` left out of the hash → test 8 fails, and the recorded failure is its first assertion, the
       `job_env_dir(...) == Env(...).address` comparison (the pytest assertion text shows both addresses); a failure
       anywhere else does not count as the NC. Restore; test 8 green again.
    3. envs/r_coloc.yml: one line `  - libopenblas=0.3.34` after `r-base`. Pin file: `$CONDA list --explicit --md5 -p
       /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/0f3436279d4146c376747a0ea5bfd4bf_` →
       envs/r_coloc.linux-64.pin.txt (starts with the header lines, then `@EXPLICIT`; 222 URL#md5 lines as measured,
       else STOP). Nothing is committed yet.
    4. Build + identity (sbatch cascadelake). Shared cache before: entry count and sha256 of the sorted `ls` of
       /rs1/researchers/c/ckclinto/conda_pkgs → `$Q8/conda_pkgs_before_15_8b.txt`. **Build** (`$Q8/env_build_15_8b.py`,
       a fresh script; the archived prior copy is reference only): repo = a `build_toy_workflow(<fresh tmp dir>)` copy
       (make_fixture_repo copies the working tree's envs/, so the copy holds the edited yaml and the pin file; the script
       asserts both are cmp-equal to the working-tree files and that job_env_dir(<copy>/envs/r_coloc.yml) ==
       job_env_dir(envs/r_coloc.yml), the realpath(prefix) + yaml-bytes hash being repo-independent); targets =
       `toy_targets("A3_1kg")` (r4_run_finemap fits and r4_coloc_pair / r4_coloc_A1 outputs, all r_coloc rules, so the
       DAG needs the r_coloc env); `run_toy(repo, "A3_1kg", targets, "--conda-create-envs-only", smk=SMK)` with
       smk_env() (CONDA_PKGS_DIRS / HOME / CONDARC isolated as bin/r4_fire.sh:13-21; no `--conda-cleanup-pkgs`); log to
       `$Q8/env_build_15_8b.log`; afterwards D = job_env_dir(envs/r_coloc.yml) exists with `str(D) + ".pin.txt"`, else
       STOP. Shared cache after → `$Q8/conda_pkgs_after_15_8b.txt`; cmp with before (equal, else STOP).
       **Identity:** write `$Q8/env_identity_15_8b.py <env dir> [--ref-pin FILE] [--ref-env DIR]` (defaults: the repo
       pin file and the measured env 0f343627). It runs every check and prints one line per check, `CHECK <name>
       PASS|FAIL <detail>`, then exits 0 only if all pass. Checks: `pin_sibling` (`str(D) + ".pin.txt"` cmp-equal to the
       ref pin), `no_yaml_sibling` (`str(D) + ".yaml"` absent), `build_log` ('Using pinnings from' present, 'Failed to
       install' absent), `explicit_list` (the `@EXPLICIT` URL#md5 lines of `$CONDA list --explicit --md5 -p D` equal
       those of the ref pin; the `# created-by` header not compared), `libopenblas_sha256` (sha256 of
       D/lib/libopenblasp-r0.3.34.so equals the ref env's, f1424288…572b), `r_library` (the sorted package directory
       names of D/lib/R/library and each package's DESCRIPTION `Version:` field equal the ref env's). Run it on D (all
       PASS). **Negative controls** (`$Q8/nc_15_8b.txt`; each must exit non-zero and print FAIL on the named check):
       (i) on the old env 0f343627 → `pin_sibling` and `no_yaml_sibling` FAIL; (ii) `--ref-pin` = a tmp copy of the pin
       file with one md5 changed → `explicit_list` FAIL (pin_sibling also FAILs; explicit_list must be among the
       FAILs); (iii) on the named env /rs1/researchers/c/ckclinto/conda_envs/r_coloc (0.3.32) with `--ref-env` D →
       `libopenblas_sha256` FAIL (the script reports the missing r0.3.34 .so as FAIL, not a crash) and `r_library` FAIL
       (that env's R library differs; if it does not, use (iv)); (iv) `--ref-env` = a tmp tree whose lib/R/library is a
       copy of D's DESCRIPTION files with one Version edited → `r_library` FAIL, every other check PASS. A NC whose
       named check PASSes does not count.
       **STOP** (checkpoint:human-action semantics, stops even under --auto) on any difference in this step: save
       `git diff -- envs/r_coloc.yml` and copies of the pin file and tests/ta_r4/test_job_guard_blas.py into
       `$Q8/stop_15_8b/`, restore the shared yaml with `git checkout -- envs/r_coloc.yml`, move the untracked pin file
       and test file into `$Q8/stop_15_8b/` (so neither Track B nor r4 sees an uncommitted pin), print the diff,
       present Q-158R6, and wait for Carter's reply file. HEAD is then the step-0 commit (KW reply, DECISIONS.md, this
       PLAN), with no guard, gate, fixture or env edit committed and every existing test as at e47b6a83; no revert is
       needed. Do not re-pin; delete neither env; run no fit; never `git reset`.
    5. Manifest: write manifests/env_lock_r_coloc_job.tsv from D's conda-meta plus the .so sha256 and the Task 1
       corename (SkylakeX). `qtl_group_fixture._job_env` → `conda_job_env.job_env_dir(REPO_ROOT / "envs/r_coloc.yml")`
       plus an existence assert (fixture builder; the 15.8a3 copy block unchanged). Green (sbatch cascadelake, `-v`):
       tests 8, 10, 11 and the 5 qtl_group_fixture importers (they collect and pass against D). NCs (md5-restore
       each): one yaml byte changed in a tmp copy, and another prefix → job_env_dir gives a different dir that does not
       exist; one manifest row perturbed in a tmp copy → test 11 fails; one URL#md5 line changed in a tmp pin copy →
       test 10 fails.
    6. Commit (`feat(ta-r4-W3f): pin libopenblas=0.3.34 in r_coloc.yml + exact pin file; rebuilt job env proven
       identical; job env lock manifest (15.8b)`): envs/r_coloc.yml, envs/r_coloc.linux-64.pin.txt, the manifest,
       tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/fixtures/qtl_group_fixture.py, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158R6S Q-158R6G Q-158KW && git ls-files --error-unmatch .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt && cmp data/r4/tmp/w3f/q158/dec_quote_15_8b.txt .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt && cmp data/r4/tmp/w3f/q158/dec_quote_15_8b_kw.txt .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt && test -d data/r4/tmp/w3f/q158/b/prior_caa5e6e3 && grep -q "libopenblas=0.3.34" envs/r_coloc.yml && test -s envs/r_coloc.linux-64.pin.txt && grep -q "Using pinnings from" data/r4/tmp/w3f/q158/env_build_15_8b.log && ! grep -q "Failed to install" data/r4/tmp/w3f/q158/env_build_15_8b.log && cmp data/r4/tmp/w3f/q158/conda_pkgs_before_15_8b.txt data/r4/tmp/w3f/q158/conda_pkgs_after_15_8b.txt && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/env_identity_15_8b.py "$(PYTHONPATH=src/python /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c 'from ta_r4.conda_job_env import job_env_dir; print(job_env_dir("envs/r_coloc.yml"))')"</automated>
  </verify>
  <done>Prior-run evidence archived; Q-158KW gated and committed with this plan in a follow-on DEC whose quote is cmp-equal (the Q-158R6G entry untouched); test 8 seen failing on its address assertion before the yaml edit; the pinned env rebuilt in isolation, identical to the measured env and the shared cache unchanged; pin, pin file, manifest and fixture committed with the 5 importers passing; or Carter has the diff with HEAD at the docs commit and the shared yaml restored.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: opt-in guard BLAS check (RED first)</name>
  <files>src/python/ta_r4/job_guard.py, tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/test_job_guard.py</files>
  <behavior>
    - Tests 1-7, 12, 13 on tmp_path fake prefixes with exactly one change per case (<context>); test 9 on the real
      envs with the default probes
    - blas_pinned=True keeps every refusal of tests 2-6; blas_pinned=False reads no BLAS and records not_checked
  </behavior>
  <action>
    1. RED: tests 1-7, 9, 12, 13 and the declared edit of test_guard_writes_the_record (`"blas_pinned": True`) →
       `$Q8/red_15_8b_t3.txt` (each fails or errors: no libopenblas_pin / blas_facts / blas_pinned parameter /
       `--blas-pinned`). `_check` per <context> (fixture builder).
    2. job_guard.py: `libopenblas_pin(repo)`; `blas_facts(prefix, probe, r_probe)` (None → default probes: blas_probe
       = `[sys.executable, "-I", "-c", <ctypes openblas_get_config/openblas_get_corename on argv[1]>, <absolute
       realpath of libblas.so.3>]`, never `$CONDA_PREFIX/bin/python3`; r_blas_probe = `$CONDA_PREFIX/bin/Rscript -e
       'cat(extSoftVersion()[["BLAS"]])'`); `blas_violations(facts, pin)` with one distinct message per check: no
       CONDA_PREFIX; zero libopenblas conda-meta records; several records; a record of another version; libblas.so.3
       not resolving to `lib/libopenblasp-r<pin>.so`; liblapack.so.3 likewise (its own message); runtime version token
       not exactly the pin (`config.split()[1] == pin`); missing bin/Rscript (a violation); R-reported BLAS another
       file. `BLAS_NOT_CHECKED_REASON = "no --blas-pinned: the rule's conda env is not envs/r_coloc.yml, so the job
       runs no R and its BLAS is not pinned (Q-158R6G A)"`. `check(…, blas_pinned, blas_probe=None,
       r_blas_probe=None)`: blas_pinned keyword-only and required, `is True` or `is False` (else JobGuardError). After
       kernel_env_violations: if True, read the pin and `environ.get("CONDA_PREFIX")`, call blas_facts/blas_violations,
       raise JobGuardError listing every violation, set `rec["blas"] = {"status": "pinned", …facts}` and
       `checked["blas_pinned"] = True`; if False, call none of libopenblas_pin / blas_facts / blas_violations / a
       probe, set `rec["blas"] = {"status": "not_checked", "reason": BLAS_NOT_CHECKED_REASON}` and
       `checked["blas_pinned"] = "not_checked"`. main(): `c.add_argument("--blas-pinned", action="store_true")` →
       `check(…, blas_pinned=args.blas_pinned)`; the OK line adds `blas pinned` or `blas not_checked`. Update the module
       docstring's usage line. Nothing else changes.
    3. Green: tests 1-7, 12, 13 and test_job_guard.py (non-heavy, login node); test 9 (sbatch cascadelake, against D
       built in Task 2) → `$Q8/t3_15_8b.txt`. NCs (`$Q8/nc_15_8b.txt`, appended), md5-restore each, each failing its
       named test case: (1) `libopenblas_pin` returns a hard-coded "0.3.34" → test 1; (2a) version comparison removed
       → test 2 case a; (2b) zero records treated as pass → test 2 case b; (2c) several records → the first one taken
       → test 2 case c; (3a) libblas check removed → test 3 case a; (3b) liblapack check removed → test 3 case b; (4)
       missing CONDA_PREFIX treated as pass → test 4; (5) runtime version compared as a prefix (`startswith`) → test 5;
       (6a) missing Rscript treated as a skip → test 6; (6b) R-BLAS comparison removed → test 6; (7) the flagged
       branch skipped (`if blas_pinned:` → `if False:`) → tests 2-7; (8) the unflagged branch calls blas_facts → test
       12; (9) the unflagged branch writes no `blas` / `checked.blas_pinned` field → test 12; (10) `--blas-pinned`
       ignored (always False) → test 13, and default True → test 13; (11) the default blas_probe uses
       `$CONDA_PREFIX/bin/python3` → test 9 (FileNotFoundError, sbatch).
    4. Commit (`feat(ta-r4-W3f): job guard refuses another BLAS when --blas-pinned, records not_checked otherwise
       (15.8b, Q-158R6G A)`), explicit paths. No gate command passes the flag yet, so every production gate at this
       commit records not_checked; Task 4 wires the flag.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_job_guard_blas.py tests/ta_r4/test_job_guard.py -q -p no:cacheprovider -m "not r4_heavy" && grep -q "test_real_job_env_passes_and_named_env_is_refused PASSED" data/r4/tmp/w3f/q158/t3_15_8b.txt</automated>
  </verify>
  <done>With --blas-pinned each unit case isolates one violation (including zero/several conda-meta records and liblapack) and fails under its own mutation; without it the guard reads no BLAS and records not_checked with a reason; the default probe runs under the guard's interpreter against the real env.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: gate_command --blas-pinned derived from each rule's conda directive; call sites; derivation tests (RED first)</name>
  <files>src/python/ta_r4/commands.py, src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk, src/snakemake/rules/ta_r4_sim.smk, src/snakemake/rules/ta_r4_qtl.smk, tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/test_job_guard.py, tests/ta_r4/test_in_job_gate.py, tests/ta_r4/fixtures/rule_conda_envs.py</files>
  <behavior>
    - Test 14 (unit): is_r_coloc_env / gate_command flag and ValueErrors
    - Tests 15-16 (r4_heavy, sbatch cascadelake): the rendered flag follows Snakemake's own parse of each rule's conda
      directive and the measured 5/2 partition; a flagged gate refuses another BLAS end to end; an unflagged gate
      passes and records not_checked
  </behavior>
  <action>
    1. Re-verify and measure first. `grep -n "gate_command(\|_r4_qtl_gate_cmd(" src/snakemake/rules/ta_r4_*.smk` →
       `$Q8/gate_sites_15_8b.txt` must be exactly the 9 lines of <context> (same files, line numbers and roles), else
       STOP. Write tests/ta_r4/fixtures/rule_conda_envs.py (<context>) and run it (sbatch) on the **real repo** with arm
       A3_1kg → `$Q8/rule_envs_real_15_8b.json`, with `git status --porcelain` before and after equal (else STOP: the
       parse has side effects). Restricted to the 7 gated rules it must give exactly: the five r_coloc rules → a str
       whose realpath is the repo's envs/r_coloc.yml, r4_qtl_aggregate and r4_qtl_tiers → None. If the in-process load
       fails in Snakemake 7.32.4, or the split is not 5/2, STOP (no fallback to source-text grep: a grep matches text,
       not meaning). Repeat on the test_in_job_gate gate repo (same result).
    2. RED: tests 14-16 and the declared edits of test_gate_command_production_is_the_guard, test_gate_command_stages,
       test_production_shell_begins_with_the_gate and test_gate_in_a_job_fails_after_locked_path_drift (<context>); add
       the `rule_envs` module fixture → `$Q8/red_15_8b_t4.txt` (14 fails on the missing is_r_coloc_env / blas_pinned; 15
       fails because no gate has `--blas-pinned` while the flagged set must equal the five rules; 16 fails because the
       finemap gate passes no `--blas-pinned` and the named env is accepted). **Parked drafts** from the reverted run
       (`$Q8/b/t3_prepared/`, archived evidence only, not trusted as tested): reuse commands.py and the four .smk
       call-site drafts after diffing each against steps 3-4 below (the plan text wins on any difference); rewrite the
       test_in_job_gate.py draft on `rule_envs` and delete its `rendered_conda` fixture and every `conda-env:` parse
       (that source was disproven: Slurm 2104600, `$Q8/stop_15_8b_t3.txt`); take test 14 from
       test_job_guard_blas.with_test14.py only after adding `match="blas_pinned"` to its bare `pytest.raises(ValueError)`
       calls. The existing `rendered` fixture keeps its 3-tuple `(repo, row, js)` unchanged, because
       test_qtl_fallback_export.py:183 and test_qtl_sweep_gwas_pph4.py:270 unpack it; `rule_envs` is a separate
       module fixture that builds or reuses the gate repo (its own `tmp_path_factory` dir is fine) and returns the
       JSON dict.
    3. commands.py: `R_COLOC_YML = "envs/r_coloc.yml"`; `is_r_coloc_env(conda_env, basedir)` (None → False; a str or
       os.PathLike that is absolute → `os.path.realpath(conda_env) == os.path.realpath(Path(basedir) / R_COLOC_YML)`;
       relative, callable or any other type → ValueError naming the value); `gate_command(stage, arm=None, config=None,
       label=None, *, blas_pinned=None)`: repro → ["true"] (blas_pinned ignored); production keeps the existing
       "needs arm, config and label" ValueError, then raises `ValueError(f"a production gate_command needs blas_pinned True or False, not {blas_pinned!r}")` (the one blas_pinned message, as in the parked draft) unless `blas_pinned is True or blas_pinned is False`, and appends `"--blas-pinned"` after
       `--label LABEL` iff True; docstring states the Q-158R6G rule. `rule_gate(workflow, rule, stage, arm, config,
       wildcards)` = `shlex.join(gate_command(stage, arm, config, label=job_label(rule, wildcards),
       blas_pinned=is_r_coloc_env(workflow.get_rule(rule).conda_env, workflow.basedir)))` for production,
       `shlex.join(["true"])` for repro (no conda lookup). No rule list in commands.py.
    4. Call sites (each rule name typed once, as today's label): ta_r4_finemap.smk:55 `gate=lambda w:
       r4cmd.rule_gate(workflow, "r4_run_finemap", STAGE, ARM, config, w)`; ta_r4_coloc.smk:68 and :99 likewise
       ("r4_coloc_pair", "r4_coloc_A1"); ta_r4_sim.smk:64 ("r4_sim"); ta_r4_qtl.smk:67 inside `_r4_qtl_gate_cmd(rule)` →
       `return r4cmd.rule_gate(workflow, rule, arm_stage(fa), fa, config, w)`; the def at :63 and the three uses at
       :122, :143, :167 unchanged. No `conda:` directive, shell line or other param changes; aggregate and tiers stay
       without a conda env. Afterwards `grep -n "gate_command(" src/snakemake/rules/ta_r4_*.smk` prints nothing and
       `grep -n "rule_gate(workflow" src/snakemake/rules/ta_r4_*.smk` prints exactly 5 lines (finemap:55, coloc:68,
       coloc:99, sim:64, qtl:67) → `$Q8/gate_sites_after_15_8b.txt` (counts recorded; test 15 is the enforcer).
    5. Green (sbatch cascadelake, `-t 01:00:00 --mem=16G`, `-v -p no:cacheprovider`): test 14, test_job_guard.py,
       the whole test_in_job_gate.py (the drift test passes: its CONDA_PREFIX is D, built in Task 2) →
       `$Q8/t4_15_8b.txt`. NCs (`$Q8/nc_15_8b.txt`, appended; md5-restore each; heavy ones under sbatch with a fresh
       module run, so the gate repo copies the mutated tree): (12) is_r_coloc_env always False → test 14 and test 15
       fail (the flagged set is empty, not the five); (13) gate_command appends the flag for blas_pinned=False too →
       test 14 fails; (14) **a gated r_coloc rule loses its flag**: ta_r4_sim.smk:64 changed to `lambda w:
       shlex.join(r4cmd.gate_command(STAGE, ARM, config, label=r4cmd.job_label("r4_sim", w), blas_pinned=False))` →
       test 15 fails on r4_sim (the iff against rule_envs); (15) **the flag added to aggregate**: `_r4_qtl_gate_cmd`
       passes `blas_pinned=True` for rule == "r4_qtl_aggregate" (bypassing rule_gate's derivation) → test 15 fails
       (the iff: rule_envs says None); (16) **tiers gains the r_coloc env**: `conda: str(Path(workflow.basedir) /
       "envs" / "r_coloc.yml")` added to r4_qtl_tiers → the derivation and rule_envs agree, and test 15 fails on the
       measured partition; (17) the finemap call site renders `blas_pinned=False` → test 16 fails (the named env is not
       refused) and test 15 fails.
    6. Commit (`feat(ta-r4-W3f): gate_command --blas-pinned derived from each rule's conda directive; aggregate/tiers
       record BLAS not_checked (15.8b, Q-158R6G A)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ! grep -q "gate_command(" src/snakemake/rules/ta_r4_finemap.smk src/snakemake/rules/ta_r4_coloc.smk src/snakemake/rules/ta_r4_sim.smk src/snakemake/rules/ta_r4_qtl.smk && test "$(grep -c "rule_gate(workflow" src/snakemake/rules/ta_r4_finemap.smk src/snakemake/rules/ta_r4_coloc.smk src/snakemake/rules/ta_r4_sim.smk src/snakemake/rules/ta_r4_qtl.smk | awk -F: '{s+=$2} END {print s}')" = 5 && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_job_guard_blas.py tests/ta_r4/test_job_guard.py -q -p no:cacheprovider -m "not r4_heavy" && grep -q "test_in_job_gate.py::test_gate_blas_flag_follows_each_rules_conda_directive PASSED" data/r4/tmp/w3f/q158/t4_15_8b.txt && grep -q "test_in_job_gate.py::test_flagged_gate_refuses_another_blas_and_unflagged_gate_records_not_checked PASSED" data/r4/tmp/w3f/q158/t4_15_8b.txt && grep -q "test_in_job_gate.py::test_gate_in_a_job_fails_after_locked_path_drift PASSED" data/r4/tmp/w3f/q158/t4_15_8b.txt</automated>
  </verify>
  <done>Snakemake's own parse of the real Snakefile gives the 5/2 split (measured first); every gated rule renders its gate through rule_gate; `--blas-pinned` appears exactly for the five r_coloc rules, as that parse says, with the flagged set non-empty; losing the flag on an r_coloc rule, or adding it to aggregate or tiers, each fails test 15 (seen); a flagged gate refuses the 0.3.32 env and an unflagged gate records not_checked, end to end.</done>
</task>

<task type="auto">
  <name>Task 5: DRAFT (k) as approved (Q-158KW); FULL; records</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-SUMMARY.md</files>
  <action>
    1. DRAFT (k), exactly the wording Carter approved in Q-158KW (one script, `$Q8/draft_k_15_8b.py`; it inserts
       strings it extracts from the reply file, never retyped copies). From line 1 of `$P/W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt`:
       NEW_CLAUSE = the substring between `Proposed: "…` and ` that differs…"` (i.e. `with `OPENBLAS_CORETYPE` set,
       with an OpenBLAS library other than version 0.3.34 in a job that runs in the R environment (the version is
       pinned there, with its exact package list), or under a run configuration`); NEW_SENTENCE = the substring between
       `followed by a new sentence: "` and `" Approve` (i.e. `The QTL aggregation and tier jobs run no R; their job
       records state that the OpenBLAS library was not checked.`). Each delimiter must occur exactly once in line 1,
       else STOP. In .planning/amendments/osf-amendment-r4-DRAFT.md (paragraph (k), ~line 135): OLD = `with
       `OPENBLAS_CORETYPE` set, or under a run configuration` occurs exactly once → replaced by NEW_CLAUSE; ANCHOR =
       `reproduced bitwise under this kernel.` occurs exactly once → NEW_SENTENCE inserted after it, separated by one
       space. The script asserts both counts, then that NEW_CLAUSE and NEW_SENTENCE each occur exactly once afterwards.
       test_amendment_text.py and test_prelock_pilot_fits.py green. (The Q-158KW question says "for Task 4"; that step
       is now Task 5 step 1 after the reorder, a cosmetic difference; the approved text is unchanged.) **Any change to
       this wording** (a framing or length failure, a wish to reword, a delimiter or anchor count other than 1) **is a
       STOP for Carter**: write nothing more and present the problem; the text is never reworded to pass.
    2. `$Q8/close.sh 15_8b` under sbatch; `$Q8/check_15_8b.py` (base full_15_8a4.xml, its actual totals; NEW = the 16
       ids of <new_tests>; declared = the 11 ids of <new_tests>). Records: LOG (the $Q8/b/prior_caa5e6e3/ archive and why, Task 1 measurement with Slurm 2101499,
       Q-158R6G, Q-158KW and their DEC, the build-before-wiring order, identity and its NC, the flag derivation, its
       truth source and the measured partition, the r_coloc users count, the setup-envs.sh note, conda_pkgs
       before/after, NCs, check); PLAN-INDEX 15.8b row; STATE (NEXT = 15.8c; NOT PUSHED); SUMMARY with `## Declared spec
       updates` and `## New test ids` (junit-form ids, one per line), a `## Track B / m3` section recording: 23 Track B
       rules use envs/r_coloc.yml; .snakemake/conda has 0 staged yamls; bin/setup-envs.sh's phase-2 fallback solves
       staged yamls, not the pin file; Track B and m3 rebuild this env on their next run (from the pin file at
       libopenblas 0.3.34 via Snakemake); and a `## Q-158R6G` section: which rules are BLAS-checked and that
       aggregate/tiers records say not_checked. fsck; commit explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8b.py && grep -qF "with an OpenBLAS library other than version 0.3.34 in a job that runs in the R environment (the version is pinned there, with its exact package list), or under a run configuration" .planning/amendments/osf-amendment-r4-DRAFT.md && grep -qF "The QTL aggregation and tier jobs run no R; their job records state that the OpenBLAS library was not checked." .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <done>DRAFT (k) carries exactly the Q-158KW-approved wording; FULL reconciles to base + 16 with the 11 declared spec updates; LOG, PLAN-INDEX, STATE and SUMMARY record the plan; nothing pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| env recipe → numerical results | a rebuilt env may load another BLAS kernel and move non-converged fits |
| job env → shared conda cache | conda clean on a shared pkgs dir |
| rule definition → gate flag | a rule's conda directive decides whether its job is BLAS-checked |
| plan text → public amendment | DRAFT (k) wording reaches OSF |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158b-01 | Tampering | silent yaml-solve fallback from the pin file | mitigate | `.pin.txt` sibling byte-equal, `.yaml` sibling absent, log scan, URL#md5 identity; identity script seen to fail on the old env; STOP on difference before any guard code, with the shared yaml restored to HEAD |
| T-r4-158b-02 | Tampering | numeric drift after rebuild | mitigate | identical URL#md5 package list and identical libopenblas .so sha256 to the env of the 17 kernel runs; no new fit |
| T-r4-158b-03 | Denial of service | shared conda pkgs cache wiped | mitigate | no --conda-cleanup-pkgs; CONDA_PKGS_DIRS/CONDARC isolated; /rs1/researchers/c/ckclinto/conda_pkgs entry count + sorted-ls sha256 before == after |
| T-r4-158b-04 | Elevation | an r_coloc job runs with an unpinned BLAS | mitigate | with --blas-pinned the guard refuses on zero/several/other-version conda-meta records, libblas or liblapack symlink, exact runtime version token, missing Rscript or R-reported BLAS mismatch; each check isolated by its own test case and NC; test 16 end to end |
| T-r4-158b-05 | Elevation | a gated r_coloc rule renders its gate without --blas-pinned | mitigate | the flag is derived in rule_gate from workflow.get_rule(rule).conda_env; test 15 compares each rendered flag with Snakemake's own parse (rule_conda_envs.py, no rule_gate call) and the non-empty measured 5/2 partition; NCs 12, 14-17 seen failing |
| T-r4-158b-06 | Repudiation | an unchecked BLAS looks checked or leaves no trace | mitigate | unflagged records carry checked.blas_pinned "not_checked" and blas.reason (test 12, test 16); DRAFT (k) states it |
| T-r4-158b-07 | Tampering | public wording drifts from what Carter approved | mitigate | DRAFT strings taken from the Q-158KW reply file and compared byte-for-byte; any change is a STOP |
</threat_model>

<verification>
- check_15_8b.py passes; Q-158R6G and Q-158KW gated and their DEC quotes cmp-equal; identity recorded with its
  negative control before any guard code; the shared conda cache unchanged; the flag derivation, its truth source,
  the 5/2 partition and its NCs recorded; DRAFT (k) byte-equal to the approved wording; no fit run.
</verification>

<success_criteria>
- A production job of an r_coloc rule can only run against the pinned OpenBLAS in the recorded job env; a gated job
  without that env says in its record that its BLAS was not checked.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-SUMMARY.md`
</output>
