---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7a
subsystem: ta-r4 production fire / in-job guard (W3f review F1)
tags: [job-guard, config-digest, cascadelake, openblas, snakemake, fire-allowlist, reply-gate]
requires: [ta-r4-W3f-review-suite-and-close]
provides: [ta_r4.job_guard, production fire allowlist, Snakefile construction refusal, 15.7 reply gate + close script, DEC-2026-11-20-ta-r4-w3f-15-7-code-fixup]
affects: [ta-r4-W3f-completeness-by-identity, all later 15.7 plans, W5 production fires]
tech-stack:
  added: []
  patterns: [in-job config digest recomputed from committed files, parse-time Workflow.config_args / overwrite_configfiles refusal]
key-files:
  created:
    - src/python/ta_r4/job_guard.py
    - tests/ta_r4/test_job_guard.py
  modified:
    - src/python/ta_r4/commands.py
    - src/snakemake/rules/ta_r4_finemap.smk
    - src/snakemake/rules/ta_r4_coloc.smk
    - src/snakemake/rules/ta_r4_qtl.smk
    - src/snakemake/rules/ta_r4_sim.smk
    - Snakefile.ta_r4
    - bin/r4_fire.sh
    - tests/ta_r4/test_in_job_gate.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/DECISIONS.md
decisions:
  - "The job digest is computed from the live Snakemake config at DAG time and recomputed in-job from the three committed files with snakemake.io.load_configfile + update_config (Snakemake's own loader), so any --config / --configfile / profile-injected override fails the job"
  - "The construction refusal keys on workflow.config_args and the ordered, de-duplicated absolute workflow.overwrite_configfiles (measured: configfiles also carries the directive's relative entry)"
commits: [c015a4e4, 420aa998]
completed: 2026-11-20
---

# Phase ta-r4 Plan 15.7a: W3f runtime config guard Summary

Every production job now starts with `python -m ta_r4.job_guard check`. It runs the lock gate first, then refuses unless all of these hold: the job's config sha256 equals the digest of the committed pipeline/overlay files; the CPU is Cascade Lake (family 6, model 85, avx512_vnni, no avx512_bf16); and no OPENBLAS_* variable is set other than VERBOSE / NUM_THREADS. It then writes a per-job JSON record. `bin/r4_fire.sh` production refuses R4_FIRE_PY / R4_FIRE_SMK and any flag outside the allowlist. `Snakefile.ta_r4` refuses a production `--config`, or a configfile list that differs from CONFIG_FILES(arm), at parse time.

## Task 1 (c015a4e4, 420aa998)

- Commit 1 holds the 15 decision files, the 11 PLAN files, PLAN-INDEX and the DEC. Each file is quoted via cat and byte-compared after extraction (15/15). replies.sha256 is quoted in the DEC.
- Reply gate: 14 NCs (a)-(n) at the expected rcs, each failing for its own named reason. All 12 real replies → 0.
- Measured attrs as planned (`data/r4/tmp/w3f/q157/smk_attrs.txt`).
- RED: 31 F / 18 P, exactly the planned split. GREEN: Task 1 verify 197 P / 2 S; 32 collected.
- Mutation NCs (6) each fail exactly their enforcing tests. Non-weakening AST PASS (its NC FAILs). test_amendment_text 21 P / 2 S.

## Task 2: FULL (Slurm 2007035, c020n03, HEAD 420aa998)

- QUICK 775 P / 2 S; HEAVY 311 P / 5 S; PINS 39 P; FULL **2,587 = 2,534 P / 53 S / 0 F**.
- vs full_W3f.xml: removed 0, added 32 (all passed), outcome changes 0, tests/m3 changes 0; check_15_7a.py PASS (NCs FAIL).

## New tests (32)

- `tests.ta_r4.test_job_guard::test_cpu_cascadelake_accepted`
- `tests.ta_r4.test_job_guard::test_cpu_rejected[skylake_sp]`
- `tests.ta_r4.test_job_guard::test_cpu_rejected[cooper_lake]`
- `tests.ta_r4.test_job_guard::test_cpu_rejected[broadwell]`
- `tests.ta_r4.test_job_guard::test_cpu_rejected[haswell]`
- `tests.ta_r4.test_job_guard::test_openblas_coretype_rejected`
- `tests.ta_r4.test_job_guard::test_openblas_verbose_and_num_threads_allowed`
- `tests.ta_r4.test_job_guard::test_merged_config_matches_snakemake_update_config`
- `tests.ta_r4.test_job_guard::test_credible_set_override_changes_the_digest`
- `tests.ta_r4.test_job_guard::test_guard_refuses_a_digest_mismatch`
- `tests.ta_r4.test_job_guard::test_guard_writes_the_record`
- `tests.ta_r4.test_job_guard::test_guard_runs_the_lock_gate_first`
- `tests.ta_r4.test_job_guard::test_gate_command_production_is_the_guard`
- `tests.ta_r4.test_job_guard::test_gate_command_repro_unchanged`
- `tests.ta_r4.test_job_guard::test_fire_refuses_production_flag[--config]`
- `tests.ta_r4.test_job_guard::test_fire_refuses_production_flag[-C]`
- `tests.ta_r4.test_job_guard::test_fire_refuses_production_flag[--configfile]`
- `tests.ta_r4.test_job_guard::test_fire_refuses_production_flag[--profile]`
- `tests.ta_r4.test_job_guard::test_fire_refuses_production_flag[--cluster]`
- `tests.ta_r4.test_job_guard::test_fire_refuses_production_flag[--jobscript]`
- `tests.ta_r4.test_job_guard::test_fire_refuses_env_override[R4_FIRE_PY]`
- `tests.ta_r4.test_job_guard::test_fire_refuses_env_override[R4_FIRE_SMK]`
- `tests.ta_r4.test_job_guard::test_fire_allows_production_flag[-n]`
- `tests.ta_r4.test_job_guard::test_fire_allows_production_flag[-p]`
- `tests.ta_r4.test_job_guard::test_fire_allows_production_flag[--list]`
- `tests.ta_r4.test_job_guard::test_fire_allows_production_flag[--unlock]`
- `tests.ta_r4.test_job_guard::test_fire_allows_production_flag[-j_4]`
- `tests.ta_r4.test_job_guard::test_clean_locked_production_dry_run_passes_construction`
- `tests.ta_r4.test_job_guard::test_construction_refuses[config_arg]`
- `tests.ta_r4.test_job_guard::test_construction_refuses[extra_configfile]`
- `tests.ta_r4.test_job_guard::test_construction_refuses[overlay_at_another_path]`
- `tests.ta_r4.test_job_guard::test_construction_refuses[reordered_configfiles]`

## Declared spec updates

tests.ta_r4.test_in_job_gate::test_gate_command_stages
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_run_finemap]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_coloc_pair]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_coloc_A1]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_sim]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_qtl_group]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_qtl_aggregate]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_qtl_tiers]
tests.ta_r4.test_in_job_gate::test_fire_clean_tree_reaches_snakemake
tests.ta_r4.test_in_job_gate::test_fire_refuses_a_dirty_locked_path[susie_policy]
tests.ta_r4.test_in_job_gate::test_fire_refuses_a_dirty_locked_path[glob_new_and_modified]
tests.ta_r4.test_in_job_gate::test_fire_refuses_a_dirty_locked_path[glob_deleted]

## Deviations from Plan

1. **[Rule 3 - Blocking] srun → sbatch --wait.** Interactive `srun -q normal` is refused here ("QOS 'normal' is batch-only"). Every Cascade Lake verify ran as `sbatch --wait` with the same partition, account, QOS, `--constraint=cascadelake` and wall time.
2. **[Rule 2] `commands.job_label(rule, wildcards)` and `commands.GUARD_RECORD_DIR`** were added (not in <interfaces>). They give the five call sites one label builder. The spec test still computes the label independently, inline.
3. **replies.sha256 sits under the data/r4 symlink to /rs1, so git can't commit it there.** Its exact bytes are quoted in the DEC (a cmp-checked block), so commit 1 carries it.
4. **The Snakefile refusal sits after `STAGE = arm_stage(ARM)` (one line below :24).** It needs STAGE. It is still module level and parse time, before gate_input's check_lock_gate.
5. **Extra negative controls:** 6 post-GREEN mutations, plus NCs for the DEC cmp, the AST check and check_15_7a.py.
6. **A docs commit I did not make landed during FULL:** 61994a1b (HANDOFF.json, .continue-here.md). It touches no src/tests file. FULL ran at 420aa998.

## Known Stubs

None.

## Threat Flags

None: the guard narrows the existing surface. New writes go to `data/r4/logs/job_guard/` (repo-relative, gitignored data).

## Self-Check: PASSED

Files and commits c015a4e4, 420aa998 present; 12 declared ids listed; decision_rules.yaml locked: false; config/ unchanged.
