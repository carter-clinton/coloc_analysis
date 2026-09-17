---
phase: quick-260916-ocb
plan: 01
subsystem: m3 native-plink LD panel driver (measurement wrapper, OFF the LD path)
tags: [ram-1, peak-rss, wait4, rusage, subprocess, launcher, tdd, negative-controls, signals, python39]
requires:
  - "basis 11f61e8 (tracked tree clean)"
  - "Carter, 2026-09-16: \"Small launcher process (Recommended)\""
provides:
  - "tests/m3/test_run_plink_peak_rss.py: 21 functions / 25 items. A1-A7 pin the per-child peak-RSS property, B1-B13 pin the _run_plink contract and parity, C1 is the premise monitor"
  - "src/python/run_native_ld_panel.py: _run_plink measures plink's OWN peak RSS through the module-private launcher _PLINK_PEAK_RSS_LAUNCHER + os.wait4"
affects:
  - "fire_verifier check_peak_ram (UNCHANGED consumer; now receives per-plink values)"
  - "COST-1 Stage-B->C RAM extrapolation (must use post-fix readings only)"
  - "STATE.md / HANDOFF.json RAM-1 wording (orchestrator)"
tech-stack:
  added: []
  patterns:
    - "read a child's rusage in a small isolated -I -S launcher, never in the memory-heavy spawner (exec folds the spawner's memory into the child's ru_maxrss)"
    - "fail closed with SubprocessError rather than return NaN (NaN would pass check_peak_ram)"
    - "whole-file negative controls against declared failure sets, restored cmp-identical"
key-files:
  created:
    - tests/m3/test_run_plink_peak_rss.py
  modified:
    - src/python/run_native_ld_panel.py
key-decisions:
  - "Implemented Carter's 2026-09-16 decision \"Small launcher process (Recommended)\". The recorded direct Popen+os.wait4 fix exists only as negative control NC01, which was observed RED"
  - "import resource left in place (now unused) so lines 1-182 stay line-stable"
requirements-completed: [QUICK-260916-ocb, RAM-1]
metrics:
  duration: "43 min (2026-09-16T22:50:05Z -> 23:33Z; ~29 min of it the two full tests/m3 runs)"
  completed: "2026-09-16"
  tasks: 3
  files: 2
---

# Phase quick-260916-ocb Plan 01: RAM-1 per-child peak RSS for `_run_plink` Summary

**`_run_plink` now reports the peak RSS of the plink process it just ran.** A small `-I -S` launcher starts plink with `subprocess.Popen`, reaps it with `os.wait4`, and sends plink's own `ru_maxrss` back over a pipe. Measured on the fixed code:
- a 300 MiB child followed by a tiny child reads 307.96 then 11.00 MiB (the old code read 308 then 308);
- a tiny child launched while the driver holds 256 MiB reads 11.25 MiB (the old code read about 363).

The recorded direct `Popen`+`wait4` fix was observed RED as NC01 (A2 362.59 / A3 362.92 MiB). All 12 planned negative controls reproduced their declared failure sets exactly. `tests/m3` reconciles by node id to the baseline plus 25 new passing tests; `tests/phase2` is unchanged.

**Status for the orchestrator:**
- Two commits (`f8ff9cd` RED, `9a3eb97` fix), not pushed.
- PLAN, this SUMMARY and STATE.md are NOT committed.
- No cloud, no fire, and nothing outside the two planned files.
- Two findings need a look:
  - kht `--live` went RED on 7 rows beyond the 24 citations the plan predicted (§g). All 7 are about the edited file and are pure line shift or git-freeze facts.
  - `git fsck` shows old missing objects on GPFS (§ Observations). HEAD and both new commits are intact.

## Performance

- **Started:** 2026-09-16T22:50:05Z. **RED commit** `f8ff9cd` 23:09:14Z. **Fix commit** `9a3eb97` 23:17:15Z. **Completed:** ~23:33Z.
- **Duration:** 43 min. The two full `tests/m3` runs took 15:23 and 13:19 of that.
- **Tasks:** 3/3. **Files in commits:** 2 (1 created, 1 modified).

## Task Commits

1. **Task 1, RED test file:** `f8ff9cd`, `test(quick-260916-ocb): RED — per-child peak RSS + _run_plink contract/parity pins (…)`. Only `tests/m3/test_run_plink_peak_rss.py` (+674 lines).
2. **Task 2, launcher fix:** `9a3eb97`, `fix(quick-260916-ocb): _run_plink reports plink's OWN peak RSS via a small isolated launcher + os.wait4 (…)`. Only `src/python/run_native_ld_panel.py` (+156/−13; 1344 → 1487 lines, **+143**).
3. **Task 3, verification:** no commit.

Both commit messages end with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`. Files were staged by explicit path, with the pre-commit guard run before each commit (`git log --oneline -3` + tracked status). Neither commit hit a GPFS object error.

---

## (a0) DECISION — Carter, 2026-09-16: "Small launcher process (Recommended)"

| # | Promise | Enforcer(s) | Observed |
|---|---|---|---|
| 1 | bias ≤ ~11 MiB (3.11) / ~4 MiB (3.9), regardless of driver memory | A6 `test_launcher_bias_is_bounded` (< 24 MiB); 3.9 smoke; NC10 | A6 GREEN. 3.11 probe: `true` 11.00 MiB, and 11.25 MiB with the driver holding 256 MiB. 3.9 smoke: bias 4.19 MiB; launcher reading 7.00 MiB with the parent holding 256 MiB. NC10 (32 MiB pad): A6 RED at 43.20 MiB, A1 stays GREEN. |
| 2 | error parity with `subprocess.run` | B3, B4, B5×3, plus B12/B13 (fd and signal-disposition parity) | All GREEN. RED under NC02 (B3), NC06 (B5×3), NC08 (B4, B13), NC09 (B12, B13), NC12 (B13). |
| 3 | one added process on the fire path | By construction: one launcher per call, which spawns plink | Not a test. B10/B11 read plink's ppid and find the launcher, not the driver. |
| 4 | "plan must also prove SIGTERM/timeout behaviour is no worse than today's subprocess.run" | B10 (SIGTERM to the driver alone), B11 (GNU `timeout` SIGTERM to the process group), B7 (SIGINT); NC07, NC08, NC04 | B10/B11/B7 GREEN on the unmodified code AND on the fix. NC07: B10 RED (BrokenPipeError traceback). NC08: B11 RED ("pid … survived timeout's group SIGTERM"). NC04: B7 RED (child never killed; harness `communicate` TimeoutExpired). |

## (a) Why not the recorded fix: planner's measurements vs mine

The recorded fix (`Popen(cmd)` + `os.wait4` from the driver) is contaminated because exec folds the SPAWNING process's memory into the child's `ru_maxrss`. I re-measured the premises in Task 1 Step 2 (NCSU login03, smoke_dev 3.11.15, KiB, 3 runs each):

| quantity | planner | executor |
|---|---|---|
| bare `python -c pass`, own maxrss (GNU time `%M`) | 8192 | 8192, 8192, 8192 |
| 300 MiB touched child, own maxrss (GNU time `%M`) | 315480 | 315352, 315480, 315396 |
| smoke_dev python after `import run_native_ld_panel` (VmHWM) | 109504–111424 | 111592, 109564, 109624 |
| direct `Popen`+`wait4` of `python -c pass`, parent HOLDS memory | 420776 (400 MiB held) | **273084, 273336, 273332** (256 MiB held; parent VmRSS 273112–273224) |

The premise reproduces: the direct reading is ≥ 250×1024 KiB, the level that would have stopped the task. It tracks the parent's resident size, not the child's ~8 MiB.

Related readings from this session, all in MiB:
- **Unmodified code (RED run, 3.11):** A1 308.09, A2 362.82, A3 363.65, A4 363.65, A6 363.65. The planner measured 307.88 / 362.98 / 364.95 / 364.95 / 364.95.
- **Recorded fix (NC01, 3.11):** A1 117.95 (the pytest process's high-water), **A2 362.59, A3 362.92**, A4 119.95, A6 119.95.
- **Fixed code (`green_readings_probe.py`, 3.11; importer VmHWM 109776 KiB):**
  - `true` 11.00; first tiny child 11.25; 300 MiB child 307.96; tiny after big 11.00.
  - With the driver holding 256 MiB (VmRSS 371948 KiB): tiny 11.25, `true` 11.25. A direct `wait4` from the same process read **362.90**.
  - After the driver freed it (VmRSS 109800 KiB): tiny 11.00.
- **3.9 (fork) smoke cases:**
  - parent holding 256 MiB: direct `wait4` 266.0, launcher 7.00;
  - parent after freeing it: direct `wait4` 10.0.
  - The planner measured 265.6 / 7.00 / 9.6.

## (b) Task 1 — RED on unmodified code: 9 RED / 16 GREEN, reasons checked

Verbatim `-rfE` short summary:

```
=========================== short test summary info ============================
FAILED tests/m3/test_run_plink_peak_rss.py::test_second_child_does_not_inherit_first_childs_peak
FAILED tests/m3/test_run_plink_peak_rss.py::test_child_peak_excludes_driver_high_water_after_free
FAILED tests/m3/test_run_plink_peak_rss.py::test_child_peak_excludes_driver_resident_memory_while_held
FAILED tests/m3/test_run_plink_peak_rss.py::test_unwaited_grandchild_is_not_charged_to_child
FAILED tests/m3/test_run_plink_peak_rss.py::test_launcher_without_valid_report_fails_closed[garbage_report]
FAILED tests/m3/test_run_plink_peak_rss.py::test_launcher_without_valid_report_fails_closed[no_report]
FAILED tests/m3/test_run_plink_peak_rss.py::test_launcher_without_valid_report_fails_closed[report_then_nonzero_exit]
FAILED tests/m3/test_run_plink_peak_rss.py::test_launcher_bias_is_bounded - A...
FAILED tests/m3/test_run_plink_peak_rss.py::test_launcher_fails_before_spawn_without_waitstatus_to_exitcode
========================= 9 failed, 16 passed in 5.79s =========================
```

The set check (`nc_check.py red.xml "A1,A2,A3,A4,A5x3,A6,A7"`) gave `collected=25 failed=9 passed=16` → **EQUAL**. All 16 B/C items passed.

Reason table: `red_reasons.py red.xml --check-red` → `RED-REASONS OK`, exit 0, no `PRECONDITION:` failure. Absolute module path shortened to `…`:

```
item | kind | value | label
test_second_child_does_not_inherit_first_childs_peak | READING | 308.09 MiB >= 64.0 MiB | tiny child after a 300 MiB child
test_child_peak_excludes_driver_high_water_after_free | READING | 362.82 MiB >= 64.0 MiB | tiny child after the driver freed 256 MiB
test_child_peak_excludes_driver_resident_memory_while_held | READING | 363.65 MiB >= 64.0 MiB | tiny child while the driver holds 256 MiB
test_unwaited_grandchild_is_not_charged_to_child | READING | 363.65 MiB >= 64.0 MiB | child whose 300 MiB grandchild was not waited
test_launcher_without_valid_report_fails_closed[garbage_report] | AttributeError |  | AttributeError: <module 'run_native_ld_panel' from '…'> has no attribute '_PLINK_PEAK_RSS_LAUNCHER'
test_launcher_without_valid_report_fails_closed[no_report] | AttributeError |  | AttributeError: <module 'run_native_ld_panel' from '…'> has no attribute '_PLINK_PEAK_RSS_LAUNCHER'
test_launcher_without_valid_report_fails_closed[report_then_nonzero_exit] | AttributeError |  | AttributeError: <module 'run_native_ld_panel' from '…'> has no attribute '_PLINK_PEAK_RSS_LAUNCHER'
test_launcher_bias_is_bounded | READING | 363.65 MiB >= 24.0 MiB | bare `true` = the launcher's own bias
test_launcher_fails_before_spawn_without_waitstatus_to_exitcode | AttributeError |  | AttributeError: module 'run_native_ld_panel' has no attribute '_PLINK_PEAK_RSS_LAUNCHER'
```

- **No B/C test was fixed before the RED commit.** All 16 passed on the first run.
- **One fix in the reason checker (a scratch parser, not a test).**
  - `red_reasons.py` v1 also required `_pytest/monkeypatch.py` to appear in the traceback. pytest prunes its own frames, so v1 flagged all three A5 rows.
  - v2 accepts an A5 row only if three things hold:
    - the failing `>` statement is the `monkeypatch.setattr(drv, "_PLINK_PEAK_RSS_LAUNCHER", …)` call;
    - the `E` line directly under it is the AttributeError;
    - that message uses MonkeyPatch's own `<module … from …>` form (plain attribute access says `module 'x'`).
  - I checked v2 against 4 corrupted copies of `red.xml`. Each went RED (exit 1):
    - A1 label → `300 MiB child`;
    - A5 message → plain `module '…'` form;
    - `PRECONDITION:` injected into A2;
    - A6 ceiling 24.0 → 64.0.

## (c) GREEN

- **New file:** `25 passed in 6.53s` after removing the pyc.
- **Enforcer/neighbour files** (`test_run_native_ld_panel.py`, `test_fire_verifier.py`, `test_occlusion_gate_constants.py`, `test_pairwise_completeness_scan.py`, `test_source_freeze_pins.py`): `330 passed, 1 skipped in 15.36s`. The skip (`test_fire_verifier::test_coverage_disclosure_live_gate_against_the_repo_file`) is also skipped in the baseline.
- **Task 2 `<verify>` at the fix commit:** `240 passed, 1 skipped in 14.08s`. `git diff HEAD~1 --stat` shows only `src/python/run_native_ld_panel.py | 169`.
- **Test file untouched between RED and fix:** `git diff HEAD -- tests/` was 0 bytes before the fix commit, and the fix commit touches only the source file.
- **After all negative controls:** `25 passed in 5.89s`. `md5sum src/python/run_native_ld_panel.py` = `de5352822a6a092d80b0a26b19bb4eae`, the same as `rnlp.GREEN.py`.

## (d) Negative controls: declared vs observed, whole file

How each control ran:
1. Built the mutant from `rnlp.GREEN.py`, checking that each anchor occurs exactly once.
2. Removed the pyc.
3. Ran `PYTHONDONTWRITEBYTECODE=1 $PY -B -m pytest … --junitxml=NCnn.xml`.
4. Compared sets with `nc_check.py`: collected == 25, FAILED == declared, PASSED == all the rest.
5. Restored with `cp` + `cmp` and removed the pyc.

Runner log: `ncs-run1.log`. **All 12 EQUAL; all 12 restores `cmp` OK.**

| NC | mutation | declared FAILED | observed FAILED | equal? | key observed value | restore | runtime |
|---|---|---|---|---|---|---|---|
| **NC01** | **the recorded fix**: `_run_plink` → `Popen(cmd)` + `os.wait4` | A1, A2, A3, A4, A5×3, A6, A7, B7 | same (10 failed / 15 passed) | **EQUAL** | **Recorded fix, observed RED: A2 362.59 MiB, A3 362.92 MiB.** Also A1 117.95, A4 119.95, A6 119.95; A5×3/A7 `DID NOT RAISE SubprocessError`; B7 harness `TimeoutExpired` (child not killed) | cmp OK | 66.47 s |
| NC02 | `CalledProcessError(record[1], launcher.args)` | B3 | B3 | EQUAL | `At index 1 diff: '-I' != '-c'` | cmp OK | 6.27 s |
| NC03 | drop `"-I", ` (code-specific anchor) | B9 | B9 | EQUAL | `launcher exited 99 without a valid report` | cmp OK | 6.12 s |
| NC04 | launcher `_kill_child` body → `pass` | B7 | B7 | EQUAL | harness `communicate` `TimeoutExpired` (plink kept the pipes open) | cmp OK | 66.61 s |
| NC05 | delete `os.close(read_fd)` | B8 | B8 | EQUAL | `{'n0': 4, 'n1': 5, 'no_children': True, 'rw': []}` | cmp OK | 6.22 s |
| NC06 | `OSError(record[1], record[2])` | B5×3 | B5×3 | EQUAL | `assert None == '<filename>'` ×3 | cmp OK | 6.24 s |
| NC07 | `_report` without its try/except | B10 | B10 | EQUAL | stderr `BrokenPipeError: [Errno 32] Broken pipe` traceback | cmp OK | 6.00 s |
| NC08 | `signal.signal(signal.SIGTERM, signal.SIG_IGN)` | B4, B7, B11, B13 | B4, B7, B11, B13 | EQUAL | B4 `DID NOT RAISE CalledProcessError`; B11 `pid 2123377 survived timeout's group SIGTERM`; B13 plink SigIgn `0x4003` vs run `0x3` | cmp OK | 96.91 s |
| NC09 | `Popen(argv, close_fds=False)` | B12, B13 | B12, B13 | EQUAL | `{'plink': '0 1 2 3 4', 'run': '0 1 2 3'}`; SigIgn `0x180000003` vs `0x3` | cmp OK | 6.16 s |
| NC10 | 32 MiB touched pad before the spawn | A6 (A1 must stay GREEN) | A6 | EQUAL | **A6 43.20 MiB**; A1 PASSED | cmp OK | 6.33 s |
| NC11 | `exitcode_of` deleted; `os.waitstatus_to_exitcode` called after the spawn | A7 | A7 | EQUAL | `CHILD-STARTED: plink ran before the missing os.waitstatus_to_exitcode was detected` | cmp OK | 6.30 s |
| NC12 | SIGINT handler installed unconditionally | B13 | B13 | EQUAL | plink SigIgn `0x1` vs run `0x3` | cmp OK | 6.27 s |
| NC13-A3 *(supplementary, not in plan)* | `exitcode_of = getattr(os, 'waitstatus_to_exitcode', None) or sys.exit(4)`: launcher exits SILENTLY before the spawn | A7 (written to `NC13A3.declared` BEFORE the run) | A7 | EQUAL | `LAUNCHER-REASON: the launcher failed for another reason` (only the A-3 check can catch this) | cmp OK | 6.50 s |

**Addendum A-1.** B7's harness body starts with `signal.signal(signal.SIGINT, signal.default_int_handler)`. NC01, NC04 and NC08 all ran with that line in place, and their observed sets equal the declared {A1,A2,A3,A4,A5×3,A6,A7,B7}, {B7} and {B4,B7,B11,B13}. For reference, the executor shell's `SigIgn` was `0000000000001000` (only SIGPIPE ignored).

**Addendum A-2.** Confirmed: the 24 run_native_ld_panel.py citations in the kht draft start at lines 723–1325.

**Addendum A-3.** A7 now also asserts `"waitstatus_to_exitcode" in capfd.readouterr().err`, after the SubprocessError and no-pidfile checks. It is GREEN on the fix. NC11 is still RED for its declared reason (CHILD-STARTED). NC13-A3 shows the new assert can fail on its own.

## (e) Python 3.9 compatibility (scratch only)

```
$ /usr/bin/python3 -c "…compile(open(p, encoding='utf-8').read(), p, 'exec')…" src/python/run_native_ld_panel.py
compile OK 3.9.25                  (no cpython-39 pyc written)

$ /usr/bin/python3 smoke39.py src/python/run_native_ld_panel.py
PASS python :: 3.9.25
PASS 300 MiB child >= 250 :: 307.02 MiB
PASS tiny after big < 64 :: 7.00 MiB
PASS launcher bias (true) < 24 :: 4.19 MiB
PASS fork: parent HOLDS 256 MiB -> launcher reading < 24 :: 7.00 MiB
PASS fork: parent HOLDS 256 MiB -> direct wait4 >= 250 (premise) :: 266.0 MiB
PASS fork: parent FREED 256 MiB -> direct wait4 < 64 (recorded fix passes A2 on 3.9) :: 10.0 MiB
PASS rc 3 -> CalledProcessError(original cmd) :: (3, True)
PASS SIGTERM -> -15 :: -15
PASS ENOENT identical to subprocess.run :: [Errno 2] No such file or directory: 'plink1.9-ocb-missing-smoke39'
SMOKE39 PASS 10/10

$ /usr/bin/python3 smoke39.py mut_NC01.py     # NC01 mutant built in SCRATCH (md5 06921cf3…); repo file untouched
PASS python :: 3.9.25
PASS 300 MiB child >= 250 :: 306.78 MiB
PASS tiny after big < 64 :: 9.79 MiB
PASS launcher bias (true) < 24 :: 9.79 MiB
FAIL fork: parent HOLDS 256 MiB -> launcher reading < 24 :: 265.79 MiB
PASS fork: parent HOLDS 256 MiB -> direct wait4 >= 250 (premise) :: 265.8 MiB
PASS fork: parent FREED 256 MiB -> direct wait4 < 64 (recorded fix passes A2 on 3.9) :: 9.8 MiB
PASS rc 3 -> CalledProcessError(original cmd) :: (3, True)
PASS SIGTERM -> -15 :: -15
PASS ENOENT identical to subprocess.run :: [Errno 2] No such file or directory: 'plink1.9-ocb-missing-smoke39'
SMOKE39 FAIL 9/10
```

NC01 failed only the held-parent check, as the planner saw. `smoke39.py` is the prototype with one change: `open(path, encoding="utf-8")`, because the module contains non-ASCII text.

## (f) Suites before/after, reconciled by node id

| suite | baseline (HEAD 11f61e8, before any edit) | final (HEAD 9a3eb97) |
|---|---|---|
| `tests/m3` | `1187 passed, 33 skipped, 4 warnings in 923.52s (0:15:23)` | `1212 passed, 33 skipped, 4 warnings in 799.95s (0:13:19)` |
| `tests/phase2` | `136 passed, 1 skipped in 1.83s` | `136 passed, 1 skipped in 1.72s` |
| `tests/m3/test_source_freeze_pins.py` | `39 passed in 1.26s` | `39 passed in 1.19s` |

`junit_outcomes.py` agrees with pytest's own counts:

| run | junit counts |
|---|---|
| m3 before | `passed=1187 skipped=33 total=1220` |
| m3 after | `passed=1212 skipped=33 total=1245` |
| phase2 before | `passed=136 skipped=1 total=137` |
| phase2 after | `passed=136 skipped=1 total=137` |

Reconciliation (`reconcile.txt`):
- **`tests/m3`: added=25, removed=0, changed=0.** The arithmetic holds: `after == before + {passed: +25}`, and `RECONCILE OK`.
  - The 25 added ids equal `--collect-only` of the new file, and every one is `passed`.
  - Ids (class `tests.m3.test_run_plink_peak_rss`):
    - `test_second_child_does_not_inherit_first_childs_peak`
    - `test_child_peak_excludes_driver_high_water_after_free`
    - `test_child_peak_excludes_driver_resident_memory_while_held`
    - `test_unwaited_grandchild_is_not_charged_to_child`
    - `test_launcher_without_valid_report_fails_closed[garbage_report]`, `[no_report]`, `[report_then_nonzero_exit]`
    - `test_launcher_bias_is_bounded`
    - `test_launcher_fails_before_spawn_without_waitstatus_to_exitcode`
    - `test_returns_two_finite_nonnegative_floats`
    - `test_waited_grandchild_is_charged_to_child`
    - `test_nonzero_exit_raises_calledprocesserror_with_original_cmd`
    - `test_signal_killed_child_raises_negative_returncode`
    - `test_exec_failure_matches_subprocess_run_exactly[missing_abs_path]`, `[missing_on_path]`, `[not_executable]`
    - `test_stdout_and_stderr_pass_through_uncaptured_in_order`
    - `test_interrupt_kills_child_and_propagates`
    - `test_no_fd_zombie_or_resourcewarning_leak`
    - `test_launcher_ignores_cwd_module_shadowing`
    - `test_driver_sigterm_leaves_plink_to_finish_and_nothing_hangs`
    - `test_timeout_group_sigterm_kills_plink`
    - `test_child_fds_match_subprocess_run`
    - `test_child_signal_dispositions_match_subprocess_run`
    - `test_premise_direct_wait4_charges_parent_resident_memory_to_child`
- **`tests/phase2`: added=0, removed=0, changed=0.** `RECONCILE OK`.
- **Negative controls on the reconciler** (`reconcile_negative_controls.txt`, each exit 1 `RECONCILE FAILED`):
  - no expected ids → `ARITHMETIC MISMATCH`;
  - one outcome flipped → `changed=1`;
  - one phase2 id dropped → `removed=1`.

## (g) kht verifier: before/after, and the drift record

| mode | before (HEAD 11f61e8) | after (HEAD 9a3eb97) |
|---|---|---|
| default (reads cited files at c93e97b) | `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, exit 0 | `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, exit 0. Output identical to before once the ref token is normalised. |
| `--live` (working tree) | `RESULT GREEN checks=318 parsed=88 table=88 verified=88`, exit 0 | `RESULT RED 31/318 parsed=88 table=88 verified=64`, exit 1 |

**EXPECTED DRIFT: lines after basis :202 moved by +143 (measured; the planner's prototype measured +117).** `kht_drift.py` → `KHT-DRIFT NO-STOP`. The 31 RED rows fall into three classes:

1. **24 citation rows, exactly as the plan predicted.** Ids: `c05 c07 c08 c09 c10 c11 c20 c21 c23 c47 c48 c49 c50 c51 c52 c53 c54 c55 c56 c59 c66 c67 n01 n07`.
   - Every one has a `c-res` row resolving to `src/python/run_native_ld_panel.py`, with start lines 723–1325 (all ≥ 184).
   - These are exactly the 24 citations of that file in the draft.
2. **FINDING, not predicted by the plan: 5 AST-anchor rows on the same file.** `c-ast:S3` (RN:967), `S4` (962-965), `S5` (1106), `S6` (1136-1139) and `S9` (806/866/923/925). All are at lines ≥ 799.
   - S9's own message shows the shift: `gate_sidecar = ... at 1066 (want 923)`, and 1066 = 923 + 143.
3. **FINDING, not predicted by the plan: 2 git freeze-fact rows.**
   - `RED e:log … HEAD -- RN FV PL: rc=0 count=1`. The single commit counted is `9a3eb97` (this fix).
   - `RED e:diff git diff --quiet c93e97b -- RN FV PL rc=1 (want 0)`. `git diff --name-only c93e97b -- RN FV PL` lists only `src/python/run_native_ld_panel.py`.
   - The planner's prototype never committed, so it could not have seen these rows.

The verifier's own docstring says a `--live` RED after a later edit to a cited file "is the CORRECT outcome". None of the plan's STOP conditions fired: no RED row names another file, and none sits at a line < 184.

**Proof that this is pure line shift** (`kht-shift-proof.txt`):
- `c93e97b` file == `11f61e8` file: True.
- Basis lines 203..1344 == HEAD lines 346..1487: True.
- For all 24 RED citations and the 4 line-anchored c-ast rows, the cited text at basis L..M is identical to HEAD L+143..M+143.
- Verdict: `SHIFT-PROOF PASS`.

The banked draft and its verifier were NOT edited.

## (h) Scope proof (`scope_proof.py 11f61e8` → `scope_proof.txt`, exit 0)

```
SYMBOL: basis top-level nodes=59 HEAD top-level nodes=60
SYMBOL: basis seam nodes=['FunctionDef _run_plink'] HEAD seam nodes=['Assign _PLINK_PEAK_RSS_LAUNCHER', 'FunctionDef _run_plink']
SYMBOL: top-level Assign count basis=10 HEAD=11 (delta 1)
SYMBOL: compared 58 non-seam top-level nodes + module docstring; differences=0
SYMBOL-LEVEL PASS
HUNK[default]: @@ -184 +184 @@ old=(184,1) inside 183-202
HUNK[default]: @@ -186,0 +187,47 @@ old=(186,0) inside 183-202
HUNK[default]: @@ -188 +235,60 @@ old=(188,1) inside 183-202
HUNK[default]: @@ -190,4 +296,3 @@ old=(190,4) inside 183-202
HUNK[default]: @@ -195 +300,2 @@ old=(195,1) inside 183-202
HUNK[default]: @@ -197 +303,22 @@ old=(197,1) inside 183-202
HUNK[default]: @@ -199,4 +326,20 @@ old=(199,4) inside 183-202
HUNK[default]: 7 hunks, ALL INSIDE
HUNK-LEVEL PASS
NAME-ONLY: ['src/python/run_native_ld_panel.py', 'tests/m3/test_run_plink_peak_rss.py']
NAME-ONLY PASS
TRACKED-STATUS: ''
TRACKED-STATUS PASS (empty)
SCOPE-PROOF PASS
```

- **Hunks match the planner's.** The old-side hunks are exactly the prototype's list: `-184`, `-186,0`, `-188`, `-190,4`, `-195`, `-197`, `-199,4`. Patience diff was not needed.
- **The scope proof can fail.** Run against basis `4fa2778` (parent of `e5e7ac7`), it reported:
  - `SYMBOL-LEVEL FAIL`, with 35 differences;
  - `HUNK[default]: 13 hunks, SOME OUTSIDE` and `HUNK[patience]: 14 hunks, SOME OUTSIDE`;
  - `NAME-ONLY FAIL` and `SCOPE-PROOF FAIL`, exit 1.
- **No frozen path changed.** The two-file `--name-only` list plus an empty tracked status prove it.

## (i) Contract deltas and fire-path behaviour

- **Launcher failure → `subprocess.SubprocessError` (new, fail-closed).** Tested by A5×3 and A7; NC11 and NC13-A3 observed RED. The seam never returns NaN.
- **No 0.25 s SIGINT grace before the kill.** On KeyboardInterrupt the parent terminates the launcher, which SIGKILLs plink at once. B7 tests the kill and the re-raise, not the missing grace period.
- **`wall_min` now includes launcher start-up** (tens of ms). Not tested.
- **A `PathLike` `cmd[0]`'s exec-error `filename` becomes `str`** (it crosses the JSON report). The signature is `list[str]` and `build_plink_ld_command` returns `str`. Not tested.
- **An empty `cmd` raises `SubprocessError` instead of `IndexError`.** Out of contract; not tested.
- **SIGTERM.** SIGTERM is catchable, but Python's default action simply terminates the driver without running `finally` blocks.
  - **(1) To the process group.** GNU `timeout` without `--foreground` (coreutils 8.32 at NCSU) sends SIGTERM to its whole group at expiry. plink is KILLED today and with the launcher; the launcher also SIGKILLs it. Tested by B11 (GREEN before and after; NC08 RED).
  - **(2) To the driver ALONE** (`kill <driver pid>`, `timeout --foreground`). The driver exits −15 and plink runs to completion, today and with the launcher. The launcher then finds no reader, swallows EPIPE and exits without a traceback; nothing hangs. Tested by B10 (GREEN before and after; NC07 RED).
  - **(3) SIGKILL to the driver.** Same as (2): plink keeps running. Not tested separately.
- **SIGINT parity (I2).** The launcher installs its SIGINT handler only if SIGINT was not inherited as ignored. A driver that ignores SIGINT (e.g. a background job of a non-interactive shell) therefore still hands plink an ignored SIGINT. Tested by B13 (NC12 RED: `0x1` vs `0x3`). A Ctrl-C to the foreground group reaches plink directly, as before.
- **(I6) Launcher killed alone** (OOM killer or `kill -9 <launcher>`). plink keeps running. The driver sees the pipe close with no report, raises `SubprocessError` for that region, and the loop starts the NEXT region, so TWO plinks can run at once until the orphan finishes. Not tested; accepted as unlikely.
- **(I7) Process matching.**
  - plink's parent is now the launcher (seen in B10/B11).
  - `pgrep -f plink1.9` and `pkill -f plink1.9` now ALSO match the launcher, because its argv contains the full plink argv.
  - So `pkill -f plink1.9` also SIGTERMs the launcher, which SIGKILLs plink; the region's returncode is −9, not −15.
  - `pgrep plink1.9` without `-f` is unaffected.
  - The Stage C runbook has no ancestry-based liveness check (planner grep). Not tested.
- **One added process per plink call** (Carter's accepted cost): ~11 MiB on 3.11 (probe 11.00–11.25), ~4 MiB on 3.9 (smoke 4.19).

## (j) Historical data — NOT retro-edited

- **Old semantics.** Already-banked Stage A/B panel rows used the old code, where EVERY reading = max(driver high-water at spawn, plink's own peak, every earlier child's reading).
- **`m2_region_00057`.** Its 26.5745 GiB is inherited; it equals `sub14`'s.
- **Region 1.** Its 30.6591 GiB came from its own Stage-A process, so nothing was inherited from an earlier child. It is still max(that driver's pre-spawn high-water, which includes the cohort `.bim` scan; plink's own peak), so the TSV does not prove the number is plink's alone.
- **Region 17.** Its 2.9689 GiB, recorded as "real, first child", cannot be attributed to plink alone either. Under the old code, the first tiny child read the importer's footprint: the planner measured 106.8 MiB, and the importer VmHWM re-measured here is 109564–111592 KiB. It did not read its own ~8 MiB.
- **Do not quote any old `peak_ram_gib` as a plink measurement.**

## (k) Follow-ups (not done)

- `import resource` is now unused. It was left in place so lines 1–182 stay line-stable.
- `tests/m3/test_run_native_ld_panel.py:14` still says "SOLE subprocess seam" (frozen here).
- COST-1's Stage-B→C RAM extrapolation must use only post-fix readings.
- The orchestrator should refresh the RAM-1 wording in `HANDOFF.json` and STATE ("Fix with `Popen` + `os.wait4`") to: "small isolated launcher + os.wait4 (direct wait4 measured contaminated; Carter 2026-09-16)".
- **PRE-FIRE ITEM (W5):** before Stage C, record `python3 -V` on the AoU VM (and `python -V` if that is the fire interpreter). `os.waitstatus_to_exitcode` needs Python ≥ 3.9. A7 guarantees an older interpreter fails at region 1 before any plink compute, but it would still fail.
- **kht draft citations.** If the draft is ever re-verified in `--live` mode, its 24 citations of `run_native_ld_panel.py` (and the S3–S6/S9 anchors) are now +143 lines. The draft is frozen here; this is a note, not an action.

## (l) Observations not acted on (for Carter; out of scope, nothing edited)

- **SIGHUP exposure of the fire command.** The committed command `nohup timeout 312h python3 …` (`260812-ox1-AGENT-PROMPT.md:398`, `BROWSER-PASTE.md:532`) does not shield the driver from SIGHUP. GNU timeout 8.32 installs its own SIGHUP handler over nohup's SIG_IGN and forwards SIGHUP to the group.
  - **Plan-checker measurements:** SIGHUP kills a driver stand-in under `nohup timeout 600 python`, but not under `nohup python` or `timeout 600 nohup python`.
  - **Unmeasured:** the VM's coreutils version, and whether closing a Jupyter terminal sends SIGHUP.
  - **The launcher is neutral:** it neither adds nor removes this exposure.
- **GPFS git object store (pre-existing, reported, not touched).** A read-only `git fsck --connectivity-only` (`fsck.txt`, 585 lines) reports 194 broken links from 162 trees, plus missing blobs/trees. This matches the known GPFS loose-object loss.
  - None of it touches this work. For HEAD `9a3eb97`, `f8ff9cd` and basis `11f61e8`, every object in the full tree resolves (2086 / 2086 / 2085, **0 missing**), and none of the 162 broken trees is in HEAD's tree.
  - Both commits succeeded with no "invalid object / Error building trees" error. Nothing was repaired.

---

## Deviations from Plan

### Auto-fixed issues

**1. [Rule 3 - Blocking] Plan-mandated `tests/m3` runs dirty a TRACKED file**
- **Found during:** Task 1 Step 1, after the m3 baseline; it happened again after the Task 3 m3 run.
- **Issue:** `test_sparse_parent_benchmark_records_metrics` rewrites `tests/m3/sparse_parent_benchmark.tsv` with fresh timings, so `git status` showed ` M tests/m3/sparse_parent_benchmark.tsv`.
  - Baseline run: `read_s` 1.133→0.973, `densify_window_s` 0.236→0.154. The file's mtime (23:03:32Z) falls inside my m3-before run (22:50:12–23:05:38Z).
  - After run: `read_s` 1.133→0.996, `densify_window_s` 0.236→0.154.
- **Fix:** each time, saved the generated file and its diff to scratch (`sparse_parent_benchmark.{tsv.m3-before-sideeffect,m3-before.diff,tsv.m3-after-sideeffect,m3-after.diff}`), then ran `git checkout -- tests/m3/sparse_parent_benchmark.tsv`. The tracked status was empty before the RED commit, before the fix commit, and at the end.
- **Files modified:** none committed.

**2. [Rule 1 - Bug, scratch tool] Over-strict RED reason parser**
- See §(b). The parser was fixed, not a test, and the fix was checked against 4 corrupted inputs.

### Recorded differences (within the spec)

- **Test file vs the planner prototype.** The prototype's MD5SUMS were verified OK before use. Differences:
  - repo bootstrap (`PROJECT_ROOT`/`_SRC_PYTHON`) instead of `$OCB_DRV_DIR`;
  - the A-1 line in B7 and the A-3 `capfd` check in A7;
  - `_poll_pidfile` includes the harness stderr if the harness exits first;
  - the A4 donefile poll requires non-empty content;
  - a missing `sh` in B13 is a `pytest.fail("PRECONDITION: …")`;
  - docstrings throughout, including the required module docstring. Its premise table has both the planner's and my Step-2 values.
  - Counts are unchanged: 21 functions / 25 items; 9 RED / 16 GREEN on unmodified code.
- **Seam is +143 lines vs the prototype's +117.** The `_PLINK_PEAK_RSS_LAUNCHER` program and the `_run_plink` body match the plan's §(b)/(c) verbatim. The docstring is longer because it carries:
  - the "why each piece exists" short forms (§(b) allows the comment or the docstring; I chose the docstring);
  - the §(d) fds and SIGTERM bullets, which the prototype lacked.
- **Supplementary NC13-A3.** Added so A-3's new assert has its own negative control. Its expected set was declared before the run.
- **kht `--live`:** 7 extra RED rows beyond the 24 predicted citations. See §(g): a FINDING, with no STOP condition met.
- **Tooling.** Write/Edit hooks did not time out. One Write of a scratch body-draft `.md` was refused by a hook (subagent report-file rule). This SUMMARY at its planned `.planning` path was written normally, and the content is also in the handback.

## Known Stubs

None.

## Threat Flags

None. No new network endpoint, auth path, or trust-boundary schema. Every boundary the launcher touches (driver→launcher argv, report pipe, cwd imports, signals, fds) is in the plan's `<threat_model>` T-ocb-01…07. Each `mitigate` row has its named test and an observed-RED control:

| control | covers |
|---|---|
| B9 / NC03 | cwd module shadowing |
| A5 / A7 / NC11 | fail-closed launcher, fail before spawn |
| B7 / NC04 | SIGINT kill-through |
| B11 / NC08 | group SIGTERM |
| B10 / NC07 | driver-only SIGTERM |
| B8 / NC05 | driver fd/zombie/ResourceWarning leaks |
| B12 / NC09 | child fd parity |
| B13 / NC08, NC09, NC12 | signal-disposition parity |

## Process hygiene

- **No probe processes left.** `ps` at the end showed no python/timeout/pytest processes from this task. The only match was a `sleep 180` whose parent shell `sh` pid 1953078 has been up ~3 h; it is not mine and was left alone.
- **NC08 survivor gone.** The plink stand-in `pid 2123377` that survived NC08's group SIGTERM is gone.
- **`__pycache__`** is git-ignored (`.gitignore:24`).

## Scratch artefacts (not in the repo)

All under `/gpfs_common/share01/clintonlab/ckclinto/tmp/260916-ocb/`:
- **Baselines and finals:** `m3-{before,after}.{xml,log,tsv}`, `p2-{before,after}.*`, `pins-{before,after}.log`, `kht-{default,live}-{before,after}.txt`.
- **RED and GREEN runs:** `red.{xml,log}`, `red_reasons.txt`, `reasons_nc/`, `green*.{xml,log}`, `neighbours-green.*`, `task2-verify.txt`.
- **Negative controls:** `NC01..NC12.{xml,log,reasons.txt}`, `NC13A3.*`, `ncs-run1.log`.
- **Measurements:** `premises-step2.txt`, `green-readings.txt`, `py39-compile.txt`, `smoke39-{green,NC01}.txt`.
- **Reconciliation, scope and kht:** `reconcile.txt`, `reconcile_negative_controls.txt`, `scope_proof.txt`, `scope_proof_negative_control_full.txt`, `kht-drift.txt`, `kht-shift-proof.txt`, `fsck.txt`.
- **Scripts:** `junit_outcomes.py`, `red_reasons.py` (+ `red_reasons.v1.py`), `nc_check.py`, `make_mutant.py`, `run_ncs.sh`, `smoke39.py`, `reconcile.py`, `scope_proof.py`, `kht_drift.py`, `green_readings_probe.py`.
- **Snapshots:** `rnlp.BASIS.py`, `rnlp.GREEN.py` (md5 `de535282…`), `new_ids.txt`.

## Self-Check: PASSED

- `tests/m3/test_run_plink_peak_rss.py`: FOUND (674 lines; 21 `def test_`; contains `drv._run_plink(`).
- `src/python/run_native_ld_panel.py`: FOUND; contains `_PLINK_PEAK_RSS_LAUNCHER`, `sys.executable, "-I", "-S", "-c", _PLINK_PEAK_RSS_LAUNCHER`, `os.wait4(child.pid, 0)`; the caller `wall_min, peak_ram_gib = _run_plink(cmd)` is unchanged.
- Commits `f8ff9cd` and `9a3eb97`: FOUND in `git log` on `m3-W2-aou-deltas`, with every tree object present.

---

## ⚠ AS-OF CORRECTION 2026-09-16 (appended by quick-260916-vqp; nothing above is edited)

Appended by `quick-260916-vqp` after the 2026-09-16 blast-radius review (finding B10). Nothing
above this heading is edited, softened or removed; these are as-of corrections only.

**1. `:47`-`:48` are now FALSE — the work is committed AND pushed.** `:47` reads "Two commits
(`f8ff9cd` RED, `9a3eb97` fix), not pushed." and `:48` reads "PLAN, this SUMMARY and STATE.md are
NOT committed." Both were true when written. Since then the close-out landed at `0231cbf`
("docs(quick-260916-ocb): close out RAM-1 — PLAN + SUMMARY + VERIFICATION (passed 9/9) +
STATE.md") and the branch was pushed: re-measured 2026-09-16,
`git rev-parse HEAD origin/m3-W2-aou-deltas` prints
`621701c8c28168b13f188467670d1ab90502ea06` twice, i.e. `origin/m3-W2-aou-deltas == HEAD == 621701c`.

**2. `:392` names the WRONG benchmark writer.** It attributes the rewrite of
`tests/m3/sparse_parent_benchmark.tsv` to `test_sparse_parent_benchmark_records_metrics`. Measured
2026-09-16 with `grep -n 'def test_\|BENCHMARK_TSV' tests/m3/test_sparse_parent_benchmark.py`: the
unconditional writer is **`test_no_whole_parent_dense_materialization`**
(`tests/m3/test_sparse_parent_benchmark.py:54`-`:138`), which calls
`BENCHMARK_TSV.write_text(header + line)` at `:138`. `test_sparse_parent_benchmark_records_metrics`
begins at `:141` and only READS the file (`:145`-`:148`). The recorded remedy —
`git checkout -- tests/m3/sparse_parent_benchmark.tsv` after a full run — is UNCHANGED and still
correct; only the attribution was wrong.
