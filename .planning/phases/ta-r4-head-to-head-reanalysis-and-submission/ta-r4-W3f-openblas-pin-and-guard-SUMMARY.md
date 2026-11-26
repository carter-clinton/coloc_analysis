---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8b
subsystem: ta_r4 job guard / conda job env
tags: [openblas, conda, job-guard, snakemake, reproducibility, R6]
requires: [ta-r4-W3f-sumstats-orientation-eligibility-and-draft]
provides: [libopenblas pin in envs/r_coloc.yml, r_coloc exact pin file, job env lock manifest, guard --blas-pinned, rule_gate]
affects: [15.8c, Track B / m3 r_coloc env rebuild]
tech-stack:
  added: []
  patterns: ["gate flag derived from Snakemake's own record of each rule's conda directive", "env identity proven before guard code"]
key-files:
  created:
    - envs/r_coloc.linux-64.pin.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/env_lock_r_coloc_job.tsv
    - src/python/ta_r4/conda_job_env.py
    - tests/ta_r4/test_job_guard_blas.py
    - tests/ta_r4/fixtures/rule_conda_envs.py
    - tests/ta_r4/fixtures/conda_prefix.py
  modified:
    - envs/r_coloc.yml
    - src/python/ta_r4/job_guard.py
    - src/python/ta_r4/commands.py
    - src/snakemake/rules/ta_r4_finemap.smk
    - src/snakemake/rules/ta_r4_coloc.smk
    - src/snakemake/rules/ta_r4_sim.smk
    - src/snakemake/rules/ta_r4_qtl.smk
    - tests/ta_r4/test_job_guard.py
    - tests/ta_r4/test_in_job_gate.py
    - tests/ta_r4/fixtures/qtl_group_fixture.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/DECISIONS.md
decisions:
  - "DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only (Q-158R6G A, 4e47c20d, not edited)"
  - "DEC-2026-11-26-ta-r4-draft-k-blas-wording (Q-158KW, cd96833e)"
metrics:
  completed: 2026-11-26
  tasks: 5
---

# Phase ta-r4 Plan 15.8b: OpenBLAS pin and BLAS guard Summary

envs/r_coloc.yml now pins libopenblas=0.3.34 and has an exact pin file. The job env was rebuilt and shown identical
to the measured env (env D, 516ec209…_, 222/222 URL#md5, libopenblas .so sha256 f1424288…572b, R library 144/144)
before any guard code changed. In every gated job of the five r_coloc rules the guard (`--blas-pinned`) now refuses
another BLAS. The flag comes from each rule's own conda directive, never from a list. The aggregate and tiers jobs
record `blas: not_checked`. DRAFT (k) has Carter's Q-158KW wording. No fit was run.

## Commits

| Task | Commit | What |
|------|--------|------|
| 1 | e47b6a83 | conda_job_env.job_env_dir locator (== Snakemake Env.address) |
| 2 step 0 | cd96833e | Q-158KW gated, DEC-2026-11-26-ta-r4-draft-k-blas-wording, plan as executed |
| 2 | b113fcba | libopenblas=0.3.34 pin + r_coloc.linux-64.pin.txt; env D built (Slurm 2104927) and proven identical; env_lock_r_coloc_job.tsv |
| 3 | e852040a | job_guard `--blas-pinned` (refuses another BLAS), not_checked record otherwise |
| 4 | 99949f41 | commands.is_r_coloc_env + rule_gate; 5 call sites; tests 14-16; rule_conda_envs.py |
| 5 step 1 | c54f6412 | DRAFT (k) as approved (Q-158KW) |
| 5 fix | 3e37c63a | job_env_dir(yml, prefix) with prefix required; no path literal in src; tests read the prefix from bin/r4_fire.sh (deviation 6) |
| 5 step 2 | (records commit) | LOG, PLAN-INDEX, STATE, this SUMMARY |

Earlier: 4e47c20d (Q-158R6G gated + DEC, by the executor of the earlier plan version); caa5e6e3 (that executor's
out-of-order pin + guard commit) was reverted in 5ee7efe0, and its evidence is archived in `$Q8/b/prior_caa5e6e3/`
(MANIFEST.txt). That evidence is not used for this run.

## Slurm jobs (all `--constraint=cascadelake`)

2101499 (Task 1 BLAS measure), 2103983 / 2104242 / 2104347 / 2104437 / 2104491 / 2104600 (Task 2-3 scratch jobs,
`$Q8/b/*.slurm`; 2104600 disproved the dry-run `conda-env:` truth source, stop_15_8b_t3.txt), 2104875 (RED + NC 0),
2104927 (env build + identity + identity NCs), 2105245 (Task 2 green, 103 passed), 2105573 (Task 3 heavy RED), 2105815
(Task 3 green 45 passed + NC 11), 2106577 (Task 4 step 1: 5/2 split on both repos, SPLIT_5_2_OK), 2106800 (Task 4 RED:
12 failed / 40 passed), 2106819 (Task 4 green 52 passed + NCs 12-17), 2106909 (FULL, 1 F), 2107067 (QUICK diagnosis of that F), 2108827 (fix: NCs, QUICK, guard + locator
tests), 2108889 (FULL after the fix). 2106900 was a FULL submission
cancelled while pending (resubmitted at 48G, as 15.8a4).

## Per-rule flag (measured; test 15 is the enforcer)

| Rule | Snakemake conda_env (rule_conda_envs.py) | `--blas-pinned` | Guard record |
|------|------------------------------------------|-----------------|--------------|
| r4_run_finemap | <basedir>/envs/r_coloc.yml | yes | blas.status pinned |
| r4_coloc_pair | <basedir>/envs/r_coloc.yml | yes | blas.status pinned |
| r4_coloc_A1 | <basedir>/envs/r_coloc.yml | yes | blas.status pinned |
| r4_sim | <basedir>/envs/r_coloc.yml | yes | blas.status pinned |
| r4_qtl_group | <basedir>/envs/r_coloc.yml | yes | blas.status pinned |
| r4_qtl_aggregate | None | no | checked.blas_pinned "not_checked", blas.reason = BLAS_NOT_CHECKED_REASON |
| r4_qtl_tiers | None | no | checked.blas_pinned "not_checked", blas.reason = BLAS_NOT_CHECKED_REASON |

The same 5/2 split was measured on the real repo and on the test gate repo, with `git status --porcelain` equal before
and after (rule_envs_{real,gate}_15_8b.json, Slurm 2106577). Call sites after the change: 0 `gate_command(` lines and
5 `rule_gate(workflow` lines (finemap:55, coloc:68, coloc:99, sim:64, qtl:67; gate_sites_after_15_8b.txt).

## Q-158R6G

Carter chose A: run the BLAS check only for the gated rules that use the r_coloc env. These are r4_run_finemap,
r4_coloc_pair, r4_coloc_A1, r4_sim and r4_qtl_group, whose gates carry `--blas-pinned`. r4_qtl_aggregate and
r4_qtl_tiers run no R (smoke_dev python, pip numpy/scipy). They keep today's guard, and their job records say
`checked.blas_pinned: "not_checked"` with `blas: {status: not_checked, reason: BLAS_NOT_CHECKED_REASON}`. This holds
in tests 12 and 16, end to end. The DEC is DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only (4e47c20d, unedited).

## Track B / m3

- 23 rules outside ta_r4 use envs/r_coloc.yml (r_coloc_users_15_8b.txt).
- `.snakemake/conda` holds 0 staged yamls, and 0 env dirs are built from the current r_coloc.yml.
- bin/setup-envs.sh's phase-2 fallback walks only staged `*.yaml` files. On that path Track B solves the yaml, not the
  pin file: the libopenblas version is held by the pin line, the build strings are not.
- Track B and m3 rebuild their r_coloc env on their next Snakemake run, from the same pin file, at libopenblas 0.3.34.

## Env and cache

- Env D = `/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/516ec2091adc39b232503aaa1cee4352_` was created
  from the pin file ("Using pinnings from", no "Failed to install"). It has a `.pin.txt` sibling cmp-equal to the repo
  pin file and no `.yaml` sibling. The identity script printed IDENTITY_OK, and its 4 NCs each printed IDENTITY_DIFF
  with the named check among the FAILs.
- Old env 0f343627…_ is kept. The pinned yaml no longer locates it.
- Shared cache /rs1/researchers/c/ckclinto/conda_pkgs: entries=2188, sorted-ls sha256 38c1cf64…f0d1, the same before
  and after the build (CACHE_UNCHANGED).

## Negative controls (all seen failing; `$Q8/nc_15_8b.txt`, md5-restored)

- NC 0: the locator hash with realpath(prefix) left out makes test 8 fail.
- Identity NCs (i)-(iv) each print IDENTITY_DIFF on their own check. Task 2 step 5 NCs: locator, manifest and pin.
- t3-1 … t3-11 (16 NCs: 1, 2a-c, 3a-b, 4, 5, 6a-b, 7, 8, 9, 10a-b, 11; one per guard check / record / CLI / default probe): each FAILED-AS-REQUIRED.
- t4-12 is_r_coloc_env always False → tests 14 and 15 fail. t4-13 flag appended for False → test 14 fails. t4-14 r4_sim
  loses its flag → test 15 fails on r4_sim. t4-15 aggregate gains the flag → test 15 fails (iff against rule_envs).
  t4-16 tiers gains `conda: r_coloc.yml` → test 15 fails on the partition. t4-17 finemap renders False → tests 15 and
  16 fail (the named 0.3.32 env is not refused).

## FULL

FULL Slurm 2108889 (c022n03 Cascade Lake, HEAD 3e37c63a, 2h28m; QUICK 897 P / 2 S, HEAVY 346 P / 5 S, PINS 39 P):
2,744 = 2,691 P / 53 S / 0 F (data/r4/tmp/w3f/q158/full_15_8b.xml, sha256 ac60ea0d…402d0b). check_15_8b.py vs
full_15_8a4.xml (2,728 = 2,675 P / 53 S, read from the file): 0 removed; +16, all passed; 0 outcome changes on
pre-existing ids; the 11 declared spec updates passed -> passed; totals 2,744 / 2,691 / 53 / 0; CHECK PASS
(check_15_8b.txt). Per id: every one of the 16 new ids below passed, and every one of the 11 declared ids passed.

The first FULL (Slurm 2106909, HEAD c54f6412) gave 2,744 = 2,690 P / 53 S / 1 F with CHECK FAIL on one outcome
change: test_storage_on_rs1::test_no_rs1_or_share_literals_in_r4_config_and_src passed -> failed (deviation 6). It is
kept as full_15_8b_2106909_1F.xml + check_15_8b_2106909_1F.txt and is superseded.

Expected chain: full_15_8b.xml 2,744 (the plan's PLAN-INDEX said 2,739, for 11 new tests). Downstream: 15.8c 2,752,
15.8c2 2,758, 15.8d 2,764, 15.8e 2,766, 15.8f 2,768.

## New test ids

tests.ta_r4.test_job_guard_blas::test_pin_is_read_from_r_coloc_yml
tests.ta_r4.test_job_guard_blas::test_guard_refuses_a_libopenblas_version_other_than_the_pin
tests.ta_r4.test_job_guard_blas::test_guard_refuses_blas_symlinks_not_to_the_pinned_openblas
tests.ta_r4.test_job_guard_blas::test_guard_refuses_without_conda_prefix
tests.ta_r4.test_job_guard_blas::test_guard_refuses_a_runtime_config_of_another_version
tests.ta_r4.test_job_guard_blas::test_guard_refuses_a_missing_or_other_r_blas
tests.ta_r4.test_job_guard_blas::test_guard_record_has_the_blas_block
tests.ta_r4.test_job_guard_blas::test_job_env_locator_equals_snakemake_env_address
tests.ta_r4.test_job_guard_blas::test_real_job_env_passes_and_named_env_is_refused
tests.ta_r4.test_job_guard_blas::test_pin_file_equals_the_job_env_explicit_list
tests.ta_r4.test_job_guard_blas::test_env_lock_manifest_matches_the_job_env
tests.ta_r4.test_job_guard_blas::test_unflagged_guard_records_not_checked_and_reads_no_blas
tests.ta_r4.test_job_guard_blas::test_cli_blas_pinned_flag_reaches_check
tests.ta_r4.test_job_guard_blas::test_gate_command_flags_only_the_r_coloc_env
tests.ta_r4.test_in_job_gate::test_gate_blas_flag_follows_each_rules_conda_directive
tests.ta_r4.test_in_job_gate::test_flagged_gate_refuses_another_blas_and_unflagged_gate_records_not_checked

## Declared spec updates

tests.ta_r4.test_job_guard::test_guard_writes_the_record (checked gains "blas_pinned": True; Task 3)
tests.ta_r4.test_job_guard::test_gate_command_production_is_the_guard (call gains blas_pinned=False; argv unchanged)
tests.ta_r4.test_in_job_gate::test_gate_command_stages (blas_pinned=False; the 3 ValueError cases match "needs arm, config and label")
tests.ta_r4.test_in_job_gate::test_gate_in_a_job_fails_after_locked_path_drift (CONDA_PREFIX = env D, job_env_dir(envs/r_coloc.yml))
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_run_finemap]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_coloc_pair]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_coloc_A1]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_sim]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_qtl_group]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_qtl_aggregate]
tests.ta_r4.test_in_job_gate::test_production_shell_begins_with_the_gate[r4_qtl_tiers]
(the 7 parametrized ids: `want` takes blas_pinned from the rule_envs record of the job's rule, by realpath)

Fixture-builder edits (ids unchanged): `_check` (test_job_guard.py), `_job_env` (qtl_group_fixture.py, uses the
locator), the `rule_envs` module fixture, and tests/ta_r4/fixtures/rule_conda_envs.py.

## Deviations from Plan

1. **[Plan text] "grep's file order" is alphabetical.** gate_sites_15_8b.txt lists coloc, finemap, qtl, sim, while
   <context> lists sim, qtl, finemap, coloc. The 9 lines are the same (files, line numbers, roles), so this is a
   plan-text deviation only.
2. **RED observation (no code change).** test_gate_in_a_job_fails_after_locked_path_drift passed at RED too. Before the
   wiring the finemap gate carries no `--blas-pinned`, so CONDA_PREFIX is not read. It is a declared spec update, not
   a new test. Its CONDA_PREFIX = D matters after the wiring, and it passed in the green run.
3. **DRAFT (k) got its own commit (c54f6412), before FULL.** That way FULL ran on a clean HEAD containing the DRAFT
   change. The plan bundled it into the Task 5 records commit. The content is unchanged.
4. **test 16 does not assert `"--blas-pinned" in fit`** (the parked draft did). That assertion would make NC 17 fail
   on a text check. Without it, test 16 fails on behaviour: the named env is accepted (rc 0), as NC 17 shows at :188.
5. **The plan's expected chain says full_15_8b.xml 2,739** (PLAN-INDEX amendment, written for 11 new tests). The
   revised plan has 16 new tests, so the expected total is 2,744. Downstream plans read their base totals from the
   file.

6. **[Rule 1 - Bug; orchestrator decision] D-11 banned literal in src (Task 1).** e47b6a83 added
   `R4_CONDA_PREFIX = "/rs1/researchers/…/smk_job_envs/ta_r4"` to src/python/ta_r4/conda_job_env.py:10 as the default
   of `job_env_dir`. test_storage_on_rs1::test_no_rs1_or_share_literals_in_r4_config_and_src failed in FULL 2106909
   (passed -> failed, the only outcome change) and in QUICK 2107067 (quick_diag_15_8b_2107067.out, 1 failed /
   793 passed, -x). Fix (3e37c63a): the constant is removed and `prefix` is a required argument,
   `job_env_dir(yml, prefix)`. src has no caller of job_env_dir, so no src caller changed. bin/r4_fire.sh:13 stays
   the single source of truth. New tests/ta_r4/fixtures/conda_prefix.py `r4_conda_prefix()` reads it by exact match
   `^R4_CONDA_PREFIX=(\S+)$` and raises unless there is exactly one match. Callers updated: qtl_group_fixture
   (`R4_CONDA_PREFIX = r4_conda_prefix()`, used by `_job_env`), test_job_guard_blas (module `R4_CONDA_PREFIX =
   r4_conda_prefix()`, used by the skip marker and tests 8-11), and test_in_job_gate's drift test (passes
   `r4_conda_prefix()` explicitly). Not changed: tests/ta_r4/fixtures/build_toy_workflow.py:218 still has its own
   `R4_CONDA_PREFIX` literal (added in c536547c, before this plan; not a job_env_dir caller, not in the D-11 scan); the other pre-existing copies
   of the prefix in tests are the env-dir literals HTS_BIN / TABIX / R4_PLINK (55c377a7…_) in 6 files. Out of scope. NCs (Slurm 2108827, fix_15_8b_2108827.out): the pre-fix file fails the
   storage test (2107067, 2106909); the helper raises on tmp copies of the fire script with 2 and with 0 assignment
   lines, and returns the prefix on the 1-line copy; locator NC 0 (realpath(prefix) dropped) makes test 8 fail
   against the new signature (rc 1), and it passes again after the md5-checked restore. QUICK 897 P / 2 S; guard and
   locator tests (test_job_guard_blas, test_job_guard, test_storage_on_rs1, the drift test) 54 passed. The FULL that
   failed is kept as full_15_8b_2106909_1F.xml (sha256 99ee5541…cfec9cc9) with
   check_15_8b_2106909_1F.txt.

## Known Stubs

None.

## Self-Check: PASSED

- Files found: envs/r_coloc.linux-64.pin.txt, manifests/env_lock_r_coloc_job.tsv, src/python/ta_r4/conda_job_env.py
  (0 D-11 literals), tests/ta_r4/test_job_guard_blas.py, tests/ta_r4/fixtures/rule_conda_envs.py,
  tests/ta_r4/fixtures/conda_prefix.py, data/r4/tmp/w3f/q158/full_15_8b.xml, check_15_8b.txt.
- Commits found: e47b6a83, cd96833e, b113fcba, e852040a, 99949f41, c54f6412, 3e37c63a.
- check_15_8b.py rc 0 (CHECK PASS); both DRAFT (k) strings are present (the Task 5 <verify> greps).
- decision_rules.yaml locked: false, n_regions_min 7. No fit, no OSF, no lock, no push.
