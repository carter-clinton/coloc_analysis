---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7a
slug: W3f-runtime-config-guard
type: execute
wave: 15.7a
depends_on: ["ta-r4-W3f-review-suite-and-close"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-6-push-and-15-7-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F2-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F2Q-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F3-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-DEN-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F9-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15-wording-as-approved-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15-wording-as-approved-v2-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F3B-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15W-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-PROXY-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-NREG-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-PROXYA-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-PROXYB-reply-2026-11-20.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-runtime-config-guard-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-completeness-by-identity-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-cross-purity-variant-resolution-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-a1-allvars-secondary-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-none-rows-denominators-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-purity-determinism-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-sweep-gwas-pph4-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-null-window-reselection-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-proxy-asthma-refit-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-pilot-fit-disclosure-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-review-suite-and-close-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/DECISIONS.md
  - src/python/ta_r4/job_guard.py
  - src/python/ta_r4/commands.py
  - src/snakemake/rules/ta_r4_finemap.smk
  - src/snakemake/rules/ta_r4_coloc.smk
  - src/snakemake/rules/ta_r4_qtl.smk
  - src/snakemake/rules/ta_r4_sim.smk
  - Snakefile.ta_r4
  - bin/r4_fire.sh
  - tests/ta_r4/test_job_guard.py
  - tests/ta_r4/test_in_job_gate.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-runtime-config-guard-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI
  - REQ-SUSIE-RSS-POLICY

must_haves:
  truths:
    - "bin/r4_fire.sh production refuses, before storage linking, the lock gate or Snakemake, every Snakemake argument outside a fixed allowlist (targets; -n/--dry-run; -p/--printshellcmds; -r/--reason; -j/--jobs N; -k/--keep-going; --rerun-incomplete; --quiet; --list; --unlock) and refuses R4_FIRE_PY / R4_FIRE_SMK when set; repro stage behaviour is unchanged"
    - "Snakefile.ta_r4 refuses at parse time (module level after ARM, :24), for a production arm and before gate_input's check_lock_gate (:55) runs at DAG build, a non-empty workflow.config_args (any --config) or an ordered command-line configfile list (workflow.overwrite_configfiles as absolute paths, repeats removed keeping the first occurrence, the `configfile:` directive's own entry excluded) that differs from the ordered absolute CONFIG_FILES(arm): Snakemake merges configfiles in order, so a reordered list is refused too"
    - "A clean, fixture-locked production dry run (the test_in_job_gate fixture) still passes construction: the positive control that the refusals are run against"
    - "Every production job's first command is `python -m ta_r4.job_guard check`: it runs the existing r4_lock_gate check, recomputes the merged config from the three committed files with snakemake.utils.update_config, fails unless its sha256 equals the digest the job was built with, fails unless /proc/cpuinfo is Cascade Lake (family 6, model 85, avx512_vnni present, avx512_bf16 absent) and no OPENBLAS_* variable other than OPENBLAS_VERBOSE and OPENBLAS_NUM_THREADS is set, and writes a JSON record (host, CPU model, checked flags, OpenBLAS env, digest, credible_set, ld flags) named `<SLURM_JOB_ID or local>.<label>.json`, where label = `<rule>.<sorted wildcards k=v joined by _>`, so no two jobs share a record"
    - "On a lock-gate failure `job_guard check` prints `LockGateError: <message>` to stderr and exits 1, exactly as r4_lock_gate.main (:172-176) does, resolving the repo the same way (the module path's parents[3]); other guard failures print `JobGuardError: <message>` and exit 1. So tests.ta_r4.test_in_job_gate::test_gate_in_a_job_fails_after_locked_path_drift (rc 1 and \"(g) locked paths drifted\" in stderr) holds unchanged"
    - "commands.fit_command with credible_set 0.5 still renders --credible-set 0.5, and the guard of that job fails on the digest: the reviewer's probe is reproduced and caught"
    - "The repro gate stays [\"true\"]; repro jobs, test_slurm_profile.py (repro fire with R4_FIRE_SMK) and test_qtl_group_runner.py (lock-refusal dry run, repro --list) keep their outcomes"
    - "The 12 declared test_in_job_gate.py spec updates keep their ids and pass; the fire fixture no longer uses R4_FIRE_PY / R4_FIRE_SMK"
    - "The 32 ids in <new_tests> pass; FULL vs full_W3f.xml: 0 removed, added == <new_tests>, 0 outcome changes, 2,587 = 2,534 P / 53 S / 0 F"
    - "Commit 1 holds the 15.6 reply, the fourteen 15.7 reply/wording files (12 replies, wording v1 and v2), the DEC, all eleven 15.7 PLAN files and PLAN-INDEX; gate_reply.py passes its 14 recorded negative controls"
  artifacts:
    - path: "src/python/ta_r4/job_guard.py"
      provides: "JobGuardError, CONFIG_FILES, merged_config_from_files, config_digest, cpu_is_cascadelake, kernel_env_violations, check, main"
    - path: "tests/ta_r4/test_job_guard.py"
      provides: "the 32 tests in <new_tests>"
    - path: ".planning/DECISIONS.md"
      provides: "DEC-2026-11-20-ta-r4-w3f-15-7-code-fixup quoting all fifteen decision files byte-for-byte"
    - path: "data/r4/tmp/w3f/q157/gate_reply.py"
      provides: "the 15.7 reply gate (scratch tool, not committed; never read by a test)"
  key_links:
    - from: "src/snakemake/rules/ta_r4_*.smk production rules"
      to: "ta_r4.job_guard check"
      via: "commands.gate_command(stage, arm, config, label) → argv with --arm, --config-sha256 and --label"
      pattern: "gate_command\\("
    - from: "ta_r4.job_guard.check"
      to: "ta_r4.r4_lock_gate"
      via: "the lock gate's existing check function, called first, unchanged"
      pattern: "r4_lock_gate"
    - from: "Snakefile.ta_r4"
      to: "workflow.config_args / workflow.overwrite_configfiles"
      via: "construction-time refusal before check_lock_gate"
      pattern: "config_args"
---

<objective>
Close review finding F1 (CONFIRMED at planning): the lock freezes files but not the effective run configuration.
`bin/r4_fire.sh:73-76` forwards `"$@"` to Snakemake; `commands.py:50` renders `--credible-set` from the merged
config, and `run_susie_rss.R:1198-1200` uses it as the ladder's coverage, so `--config finemap={credible_set:0.5}`
changes every production credible set while every frozen file is unchanged. The cascadelake constraint lives in an
overridable profile (`config/ta_r4/cluster_slurm/config.yaml:6`) and `jobscript.sh:4-5` only logs.

This plan also opens 15.7: it commits the 15.6/15.7 reply, Carter's twelve 2026-11-20 answers and both F15 wording
files (v2 supersedes v1), the umbrella DEC, the eleven 15.7 PLAN files and PLAN-INDEX, and builds the reply gate and close script.
Output: `ta_r4/job_guard.py`, the fire allowlist, the construction refusal, 32 tests, 12 declared spec updates. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@bin/r4_fire.sh
@Snakefile.ta_r4
@src/python/ta_r4/commands.py
@src/python/ta_r4/r4_lock_gate.py
@tests/ta_r4/test_in_job_gate.py

**Standing rules:** PLAN-INDEX §A, §B and the 15.7 shared protocol. Task verify commands run on a Cascade Lake node
(`srun -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 00:45:00 …`), since the guard reads the real
CPU in its CLI paths. Explicit-path staging only; never stage
`.planning/config.json` or the two `data/processed/...` deletions. RED first with negative controls observed failing.
No push.

**Forbidden:** edits to `config/pipeline.yaml`, `config/ta_r4/**`, `src/legacy/**`, `r4_lock_gate.py`, tests/m3;
changing repro-stage behaviour; a production fire.

**Decision files (record; quote via `cat`, never retype).** `W3f-carter-15-6-push-and-15-7-reply-2026-11-20.txt`
(Q2 → "Plan 15.7 code fix-up (Recommended)"), and the 2026-11-20 files for Q-F2, Q-F2Q, Q-F3, Q-F3B, Q-DEN, Q-F9,
Q-F15, Q-F15W, Q-PROXY, Q-PROXYA, Q-PROXYB, Q-NREG plus the F15 wording v1 and v2. sha256 at planning: Q-DEN 0775b935…b832c,
Q-F2 57886063…2e5a, Q-F2Q 63a54f5f…790e, Q-F3 f8694860…4703, Q-F3B b744a828…cc1b, Q-F9 c2cc9915…c089,
Q-F15 aaff9960…5877, Q-F15W 5bd31c68…ef05, Q-PROXY f07eece8…bcdf, Q-PROXYA 6597d02e…08c5, Q-PROXYB 651c901c…6f80, Q-NREG 2ca9b987…ce18 (free-text reply line
`Carter reply (verbatim): yes, A and add D to 15.7j and keep 7`), wording v1 c60e4346…439a, wording v2
65c3851d…243b (full values in each gated plan's `<question>` block).

**Measured at planning (re-measure in Task 1 step 2; do not copy):**
- HEAD fcfd7ca8 at the end of planning (553c8fc8 plus a HANDOFF/STATE session-close commit); origin..HEAD = 1.
- `Snakefile.ta_r4:14` `configfile: "config/pipeline.yaml"`; `:24` `ARM = _R4["arm"]`; `:55` construction-time
  `check_lock_gate(...)`. Snakemake 7.32.4 `Workflow` has `config_args` (the `--config` items),
  `overwrite_configfiles` (command-line `--configfile` list) and `configfiles` (which also holds the directive's
  entry). On a normal fire `overwrite_configfiles` and `configfiles` are non-empty, so the refusal keys on
  `config_args` and on the set comparison in must_haves. Print all three on the rendered fixture before coding.
- Production rules calling `r4cmd.gate_command(STAGE)`: ta_r4_finemap.smk:55, ta_r4_coloc.smk:68 and :99,
  ta_r4_sim.smk:64 (sim runs under ARM A3_1kg); ta_r4_qtl.smk:64 (`_r4_qtl_gate_cmd`, used at :118, :139, :163).
- tests/ta_r4/test_in_job_gate.py: `_fire` sets `R4_FIRE_PY`/`R4_FIRE_SMK` to stubs (:206-212); `test_gate_command_stages`
  (:169) and `test_production_shell_begins_with_the_gate` (:126, compares the first command to
  `shlex.join(commands.gate_command("production"))`).
- Other tests touching the fire or gate: tests/ta_r4/test_slurm_profile.py:160-170 (repro + R4_FIRE_SMK; unaffected
  because the env refusal is production-only); tests/ta_r4/test_qtl_group_runner.py:283-308 (lock-refusal dry run with
  no overrides, and `bin/r4_fire.sh repro … --list`; both must keep their outcomes).
- Baseline FULL node c025n04: `intel,cascadelake,gold6226,avx512`.

**Declared spec updates (ids kept, still passing; 12 ids).** The coordinator's count of 11 omits one: the dirty-path
test has 3 parametrizations.
- `tests.ta_r4.test_in_job_gate::test_gate_command_stages`: production argv is now the guard
  (`gate_command("production", arm, cfg, label=…)`); it also asserts ValueError when arm, config or label is None;
  repro still returns `["true"]`.
- `…::test_production_shell_begins_with_the_gate[<rule>]` for the 7 PRODUCTION_RULES: the single constant at
  test_in_job_gate.py:131 becomes a per-job list. For each rendered job of the rule, the expected first command is
  `shlex.join(commands.gate_command("production", arm, cfg, label=f"{rule}." + "_".join(f"{k}={v}" for k, v in
  sorted(wildcards.items()))))`, with `wildcards` parsed from that job's `attrs["wildcards"]`, arm "A3_1kg" (QTL
  rules: `r4qtl.fit_arm(qtl_arm)`, also A3_1kg in the fixture) and `cfg = job_guard.merged_config_from_files(repo,
  "A3_1kg")`.
- `…::test_fire_clean_tree_reaches_snakemake` and `…::test_fire_refuses_a_dirty_locked_path[susie_policy]`,
  `[glob_new_and_modified]`, `[glob_deleted]`: fixture route only. `_fire_repo` rewrites the `PY=` and `SMK=` default
  lines in its own copy of `bin/r4_fire.sh` to the stub paths (each pattern asserted to occur exactly once) and
  `_fire` no longer sets the env vars. Assertions unchanged.
`test_fire_stub_paths_prints_the_real_locked_paths` uses the same fixture builder; its assertion is unchanged.
</context>

<new_tests>
tests/ta_r4/test_job_guard.py; N_new = 32.
1. `test_cpu_cascadelake_accepted`
2. `test_cpu_rejected[skylake_sp]`  3. `[cooper_lake]`  4. `[broadwell]`  5. `[haswell]`
6. `test_openblas_coretype_rejected`
7. `test_openblas_verbose_and_num_threads_allowed`
8. `test_merged_config_matches_snakemake_update_config`
9. `test_credible_set_override_changes_the_digest` (0.95 → 0.5)
10. `test_guard_refuses_a_digest_mismatch`
11. `test_guard_writes_the_record`
12. `test_guard_runs_the_lock_gate_first`
13. `test_gate_command_production_is_the_guard`
14. `test_gate_command_repro_unchanged`
15. `test_fire_refuses_production_flag[--config]`  16. `[-C]`  17. `[--configfile]`  18. `[--profile]`
19. `[--cluster]`  20. `[--jobscript]`
21. `test_fire_refuses_env_override[R4_FIRE_PY]`  22. `[R4_FIRE_SMK]`
23. `test_fire_allows_production_flag[-n]`  24. `[-p]`  25. `[--list]`  26. `[--unlock]`  27. `[-j_4]` (each reaches
    the stub snakemake with the flag forwarded; same rewritten-defaults fixture route as the spec updates)
28. `test_clean_locked_production_dry_run_passes_construction` (r4_heavy; the test_in_job_gate fixture repo; the
    positive control)
29. `test_construction_refuses[config_arg]` (r4_heavy; 28's repo + `--config x=1`)
30. `test_construction_refuses[extra_configfile]` (r4_heavy; + a fourth `--configfile`)
31. `test_construction_refuses[overlay_at_another_path]` (r4_heavy; a byte-identical copy of the arm overlay passed from
    another path: the absolute-path set differs. An omitted overlay cannot be tested here, because Snakefile.ta_r4:22-23
    raises before ARM exists; that existing message is accepted as the refusal for that case)
32. `test_construction_refuses[reordered_configfiles]` (r4_heavy; the three files passed as arm overlay before
    overlay_base)
Each of 29-32 asserts the refusal message appears and no lock-gate message precedes it.

Expected FULL: 2,555 + 32 = 2,587 = 2,534 P / 53 S / 0 F. If a test must be split or merged, STOP: the list is the contract.
</new_tests>

<interfaces>
src/python/ta_r4/r4_lock_gate.py (read-only): `_check(repo)` raises LockGateError.
src/python/ta_r4/commands.py: `gate_command(stage)`; `_PY = ["env", "PYTHONPATH=src/python", sys.executable, "-m"]`.
New (exact names):
  job_guard.ALLOWED_OPENBLAS_ENV = ("OPENBLAS_VERBOSE", "OPENBLAS_NUM_THREADS")
  job_guard.CONFIG_FILES(arm) -> ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml"]
  job_guard.merged_config_from_files(repo, arm) -> dict
  job_guard.config_digest(cfg) -> str     # sha256 of json.dumps(cfg, sort_keys=True, separators=(",", ":"), default=str)
  job_guard.cpu_is_cascadelake(cpuinfo: str) -> bool
  job_guard.kernel_env_violations(environ) -> list[str]
  job_guard.check(repo, arm, digest, *, environ, cpuinfo, record_dir, label) -> dict   # raises JobGuardError; writes <job>.<label>.json
  CLI: python -m ta_r4.job_guard check --stage production --arm ARM --config-sha256 HEX --record-dir data/r4/logs/job_guard --label LABEL
  commands.gate_command(stage, arm=None, config=None, label=None)   # repro → ["true"]; production requires arm, config and label (ValueError if any is None)
Scratch (not committed): $Q/gate_reply.py, $Q/gate_nc/, $Q/close.sh, $Q/check_tmpl.py, $Q/check_15_7a.py
</interfaces>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Planning commit + DEC; reply gate with negative controls; job guard, fire allowlist, construction refusal (RED first)</name>
  <files>the fifteen decision files, the eleven 15.7 PLAN files, ta-r4-PLAN-INDEX.md, .planning/DECISIONS.md, src/python/ta_r4/job_guard.py, src/python/ta_r4/commands.py, src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk, src/snakemake/rules/ta_r4_qtl.smk, src/snakemake/rules/ta_r4_sim.smk, Snakefile.ta_r4, bin/r4_fire.sh, tests/ta_r4/test_job_guard.py, tests/ta_r4/test_in_job_gate.py</files>
  <read_first>
    - bin/r4_fire.sh, Snakefile.ta_r4 :1-80, commands.py :98-104 and every gate_command call site
    - tests/ta_r4/test_in_job_gate.py (whole), tests/ta_r4/test_slurm_profile.py :155-175, tests/ta_r4/test_qtl_group_runner.py :280-310
    - DECISIONS.md entry DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation (format)
  </read_first>
  <behavior>See <new_tests>.</behavior>
  <action>
    0. **Planning commit.** `mkdir -p data/r4/tmp/w3f/q157` (= $Q). `git rev-parse HEAD > $Q/start_15_7a.txt`. The 15.6
       reply must contain exactly one line `Carter reply (verbatim, selected option): Plan 15.7 code fix-up
       (Recommended)`. `sha256sum` all fifteen decision files into `$Q/replies.sha256`. DEC
       `DEC-2026-11-20-ta-r4-w3f-15-7-code-fixup`: decider; each of the fifteen files quoted with `cat` in its own
       ```text fence (extract and `cmp` each); scope = the 15.7 plan list with each answer mapped to its plan; it
       states that n_regions_min stays 7 (Q-NREG), that the proxy work and its 20 asthma pilot fits are in 15.7h2
       (Q-PROXYA; Q-PROXYB: run as planned despite the expected early exits), and that wording v2 supersedes v1 (Q-F15W) subject to 15.7i's recount. Commit 1
       (`docs(ta-r4-W3f): 15.7 plan set + Carter 15.7 replies + DEC-2026-11-20-ta-r4-w3f-15-7-code-fixup (15.7a)`):
       the fifteen files, the eleven PLAN files, PLAN-INDEX, DECISIONS.md, by explicit path.
    1. **Reply gate.** Write `$Q/gate_reply.py <QID> --question TEXT --sha256 HEX [--dir D] LABEL…` per the PLAN-INDEX
       15.7 protocol. Negative controls on synthetic files in `$Q/gate_nc/` (passed with `--dir`), rcs in
       `$Q/gate_nc.txt`: (a) no file → 2; (b) two files for one QID → 2; (c) label with a trailing space → 2; (d) two
       reply lines → 2; (e) malformed Question line (no `(date):`) → 2; (f) QID in line 1 ≠ file name → 2; (g) date in
       line 1 ≠ file name → 2; (h) CRLF endings → 2; (i) `--question` text differs by one character → 2; (j) sha256
       differs → 2; (k) a Q-F2Q file present and Q-F2 asked → Q-F2 matched by exact file name only (rc per the Q-F2
       file; with only the Q-F2Q file present, Q-F2 → 2); (l) a third `Carter note (verbatim): …` line → 0; (m) a free-text reply line with `--free-text` equal → 0; (n)
       `--free-text` differing by one character → 2. Then run it on the twelve real reply files with the labels / free
       text and question texts in the gated plans; each → 0. Write `$Q/close.sh <tag>` (copy
       of close_W3f.sh; only the junit path and header differ) and `$Q/check_tmpl.py`.
    2. **Re-measure** the <context> facts; print `workflow.config_args`, `overwrite_configfiles` and `configfiles` from a
       dry run of the test_in_job_gate fixture into `$Q/smk_attrs.txt`. A difference → STOP.
    3. **RED.** Write the 32 tests and the 12 spec updates against stubs: `cpu_is_cascadelake` → True,
       `kernel_env_violations` → [], `merged_config_from_files` → {}, `config_digest` → "0"*64, `check` returns {} and
       writes no file and does not call the lock gate; `gate_command`, r4_fire.sh and Snakefile.ta_r4 unchanged except
       that the fixtures use the rewritten-defaults route. Expected RED: 2-6, 8-13, 15-22, 29-32, and the 8 gate-shell
       spec updates (they expect the guard). Expected green: 1, 7, 14, 23-28 and the 4 fire spec updates. Record in
       `$Q/red_15_7a.txt`.
    4. **GREEN.** `job_guard.py` per <interfaces>; `gate_command(stage, arm=None, config=None, label=None)` (repro unchanged;
       production requires arm, config and label, else ValueError); the five call sites pass `ARM` (the Snakefile's arm; for the QTL rules
       `r4qtl.fit_arm(w.qtl_arm)`, which is ARM in that invocation), `config`, and `label` from a `lambda w:` param
       built from the rule name and its sorted wildcards. `_r4_qtl_gate_cmd(w)` (ta_r4_qtl.smk:64) is shared by the
       three QTL rules (:118, :139, :163), so it gains a rule-name parameter (`_r4_qtl_gate_cmd(rule)` returning a
       `lambda w:`), and each of the three rules passes its own name, giving a distinct label per rule. The
       Snakefile.ta_r4 refusal per must_haves sits at module level, right after `ARM = _R4["arm"]` (:24), so it runs
       when the Snakefile is parsed and before `gate_input`'s `check_lock_gate` (:55), which runs at DAG build;
       r4_fire.sh: the R4_FIRE_PY / R4_FIRE_SMK refusal for production sits right after `shift 2` (line 34), before $PY
       is first used (line 42); the argument allowlist (`-j`/`--jobs` consume one numeric value; a non-dash token is a
       target) sits after the arm check and before `r4_link_storage.sh`. All 32 green; the 12 spec updates green;
       test_slurm_profile.py and test_qtl_group_runner.py outcomes equal full_W3f.xml (script compare).
    5. **Non-weakening.** `git diff --quiet HEAD -- config/ src/legacy/ tests/m3/ src/python/ta_r4/r4_lock_gate.py`. AST
       compare of test_in_job_gate.py against `$Q/start_15_7a.txt`: only `_fire_repo`, `_fire` and the two named test
       functions differ (`$Q/noweaken_15_7a.txt`).
    6. **DRAFT** (k): after "Every production job runs on one CPU type (…)", add "; each production job refuses to run
       on another CPU type, with `OPENBLAS_CORETYPE` set, or under a run configuration that differs from the committed
       configuration files, and records what it checked". Old string asserted unique; test_amendment_text.py green.
    7. Commit 2 (`feat(ta-r4-W3f): production jobs check resolved config digest, CPU type and OpenBLAS env; fire and
       Snakefile refuse overrides (15.7a, F1)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && set -o pipefail && srun -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 00:45:00 --mem=16G /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_job_guard.py tests/ta_r4/test_in_job_gate.py tests/ta_r4/test_snakemake_toy_e2e.py tests/ta_r4/test_frozen_script_armed_e2e.py tests/ta_r4/test_lock_gate.py tests/ta_r4/test_track_b_isolation.py tests/ta_r4/test_slurm_profile.py tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider && test "$(/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_job_guard.py --collect-only -q -p no:cacheprovider | grep -c '::')" = 32 && git diff --quiet HEAD -- config/ src/legacy/ tests/m3/ && sha256sum -c data/r4/tmp/w3f/q157/replies.sha256 && test "$(grep -c ' rc=' data/r4/tmp/w3f/q157/gate_nc.txt)" = 14</automated>
  </verify>
  <done>Commit 1 holds the decision files, DEC, eleven plans and PLAN-INDEX; the gate's 14 NCs recorded; RED observed as listed; 32/32 and the 12 spec updates green; repro behaviour unchanged.</done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm, per-id reconciliation vs full_W3f.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-runtime-config-guard-SUMMARY.md</files>
  <action>
    1. `git status --porcelain -- tests src` empty; sbatch `$Q/close.sh 15_7a` per the protocol. Restore
       `tests/m3/sparse_parent_benchmark.tsv`.
    2. `junit_cmp.py data/r4/tmp/w3f/full_W3f.xml $Q/full_15_7a.xml > $Q/cmp_15_7a.txt`; `$Q/check_15_7a.py`: removed 0;
       added == the 32 (`tests.ta_r4.test_job_guard::` prefix), all passed; 0 outcome changes, the 12 declared ids
       included (passed → passed); 2,587 = 2,534 / 53 / 0. The SUMMARY lists the 32 ids, and its `## Declared spec
       updates` section the 12 ids.
    3. Records: LOG, STATE block (NEXT = 15.7b; NOT PUSHED), PLAN-INDEX row COMPLETE, SUMMARY. fsck before/after.
       Commit 3, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7a.py && test -z "$(git status --porcelain -- src tests bin Snakefile.ta_r4 .planning/DECISIONS.md)"</automated>
  </verify>
  <done>FULL reconciled per id; records committed; nothing pushed.</done>
</task>

</tasks>

<enforcers>
| must_have | enforcer | negative control |
|---|---|---|
| fire allowlist | 15-22 | unchanged r4_fire.sh (RED) |
| allowlist not over-broad | 23-27 | — (flags reach snakemake) |
| construction refusal keyed correctly (order included) | 29-32 against the positive control 28 | unchanged Snakefile (RED); 28 green proves a normal fire still passes |
| in-job digest | 9, 10 | stub digest (RED) |
| CPU / kernel env | 2-6 | stub (RED) |
| record written | 11 | stub writes nothing (RED) |
| lock gate first | 12 | stub skips it (RED) |
| reply gate | $Q/gate_nc.txt (a)-(n) | — (14 recorded rcs) |
| lock gate still enforced inside a job, through the guard | existing `tests.ta_r4.test_in_job_gate::test_gate_in_a_job_fails_after_locked_path_drift` (assertions unchanged; it now runs the guard, so it must run on a Cascade Lake node) | its own drift step |
| production jobs still run end to end with the guard in place | existing tests/ta_r4/test_snakemake_toy_e2e.py (A3_1kg and A2_identity toy fires; Cascade Lake node) | — |
| FULL | check_15_7a.py | — (per-id identity) |
</enforcers>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| operator CLI → production fire | flags, profile and env can change science without touching a frozen file |
| Slurm node → numerical kernel | CPU type selects the OpenBLAS kernel |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157a-01 | Tampering | `--config` / extra configfile | mitigate | allowlist + construction refusal + in-job digest (9, 10, 15-17, 29-32) |
| T-r4-157a-02 | Tampering | profile / cluster / jobscript override | mitigate | allowlist (18-20) + in-job CPU check (2-5) |
| T-r4-157a-03 | Tampering | inherited OPENBLAS_CORETYPE | mitigate | kernel_env_violations (6) |
| T-r4-157a-04 | Repudiation | which config/CPU a result came from | mitigate | per-job JSON record (11) |
| T-r4-157a-05 | Denial of service | refusal blocks every legitimate fire | mitigate | positive control 28; allowed flags 23-27 |
| T-r4-157a-06 | Repudiation | Carter's answers | mitigate | fifteen files committed, sha256-checked, quoted and cmp-checked in the DEC |
</threat_model>

<verification>
- 32 new tests and 12 spec updates pass; check_15_7a.py passes; no diff under config/, src/legacy/, tests/m3/.
- `git diff $(cat data/r4/tmp/w3f/q157/start_15_7a.txt)..HEAD --name-only` ⊆ files_modified.
</verification>

<success_criteria>
- A production fire cannot run under an overridden config, profile or kernel env; each job records what it checked; a normal fire still constructs.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-runtime-config-guard-SUMMARY.md`
</output>
