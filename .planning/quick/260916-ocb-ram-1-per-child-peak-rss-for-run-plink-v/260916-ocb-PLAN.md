---
phase: quick-260916-ocb
plan: 01
type: execute               # TDD inside the tasks: observed-RED commit first, then GREEN
wave: 1
depends_on: []
mode: quick-full
branch: m3-W2-aou-deltas
basis: 11f61e8              # HEAD at planning time; tracked tree clean
worktree: none              # GPFS: worktrees disabled project-wide
autonomous: true
push: false                 # commit only; the orchestrator commits PLAN/SUMMARY/STATE afterwards
revision: 1                 # plan-checker round 1 adopted in full (1 blocker, 5 warnings, 7 info) — see <revision_log>
decision: "Carter, 2026-09-16: \"Small launcher process (Recommended)\""
requirements: ["QUICK-260916-ocb", "RAM-1"]   # STATE.md RESUME item 2; defect record .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md:112-125

files_modified:
  - tests/m3/test_run_plink_peak_rss.py        # CREATED (Task 1, RED commit)
  - src/python/run_native_ld_panel.py          # MODIFIED (Task 2): ONLY lines 183-202 at basis — banner comment, one new private constant _PLINK_PEAK_RSS_LAUNCHER, _run_plink body + docstring
  - .planning/quick/260916-ocb-ram-1-per-child-peak-rss-for-run-plink-v/260916-ocb-SUMMARY.md   # CREATED (Task 3) — NOT committed by the executor

files_frozen:
  - src/python/fire_verifier.py
  - src/python/plink_ld_to_npz.py
  - src/python/condition_ld_matrix.py
  - src/python/occlusion_*.py
  - src/python/aou_ld_panel.py
  - tests/m3/test_run_native_ld_panel.py       # the large existing file is NOT churned
  - .planning/amendments/**
  - .planning/osf_deviations.md
  - .planning/HANDOFF.json
  - .planning/STATE.md                         # the ORCHESTRATOR updates STATE.md — never a task
  - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md
  - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/**
  - .planning/quick/260812-ox1-*/**            # the fire command's SIGHUP exposure is RECORDED, not fixed (Task 3 §5 (l))
  - every historical panel TSV / posted or record file

must_haves:
  truths:
    - "In ONE process, after _run_plink ran a child that touched 300 MiB (reported >= 250 MiB), _run_plink on `python -c pass` reports < 64 MiB; `_run_plink([true])` reports < 24 MiB (the launcher's bias). No inheritance across calls; the promised bias bound is pinned."
    - "A calling process that touched and FREED 256 MiB (VmHWM >= 250 MiB, VmRSS < 200 MiB), and a calling process HOLDING 256 MiB resident, both get < 64 MiB for `python -c pass`. The driver's own high-water and resident memory are not charged to plink."
    - "A 300 MiB grandchild the child waited for counts (>= 250 MiB). A 300 MiB grandchild the child did NOT wait for does not count (< 64 MiB)."
    - "A non-zero exit raises CalledProcessError with the child's returncode and .cmd == the ORIGINAL cmd. A SIGTERM-killed child gives returncode -15. Failure to exec plink raises an exception identical to subprocess.run(cmd, check=True)'s in type, args, errno, strerror, filename and str."
    - "Relative to subprocess.run, plink's inherited fd set and ignored-signal mask (with SIGINT and SIGHUP ignored in the driver) are IDENTICAL. stdout/stderr pass through uncaptured and in order. A stdlib-shadowing json.py/signal.py/subprocess.py in the cwd does not break the call. No fd, zombie or ResourceWarning leaks."
    - "SIGTERM parity is no worse than subprocess.run, measured both ways:
      - GNU `timeout` without --foreground sends SIGTERM to its whole process group, so plink is KILLED at expiry, as today.
      - SIGTERM delivered to the driver ALONE (`kill <pid>`, `timeout --foreground`) kills the driver (-15) while plink runs on until it finishes, as today. The launcher then exits without a traceback and nothing hangs.
      - SIGINT to the driver kills plink and KeyboardInterrupt propagates."
    - "A launcher that exits without a valid report (no report / garbage / valid report then non-zero exit) raises exactly subprocess.SubprocessError and never returns numbers. An interpreter lacking os.waitstatus_to_exitcode fails BEFORE plink is spawned."
    - "The recorded fix (Popen(cmd) + os.wait4 directly from the calling process) was OBSERVED RED on exactly its declared set (NC01). All 12 negative controls reproduce their declared failure sets EXACTLY, whole file, with everything else passing. A standing premise test proves that a direct wait4 reading charges the parent's resident memory to the child."
    - "Full tests/m3 and tests/phase2 reconcile BY NODE ID to their pre-edit baselines plus exactly the new file's 25 items (all passed). test_source_freeze_pins.py is GREEN before and after. 260916-kht-verify.py default mode is RESULT GREEN. Its --live RED rows (if any) all resolve to src/python/run_native_ld_panel.py citations whose start line is >= 184, the first edited line (planner check: all 24 such citations start at 723-1325). Every old-side diff hunk lies within basis lines 183-202."
  artifacts:
    - path: "tests/m3/test_run_plink_peak_rss.py"
      provides: "RED-first per-child peak-RSS tests + _run_plink contract/parity pins against the REAL function (21 functions, 25 items)"
      contains: "drv._run_plink("
      min_lines: 350
    - path: "src/python/run_native_ld_panel.py"
      provides: "_run_plink measuring plink's own peak RSS through an isolated launcher + os.wait4"
      contains: "_PLINK_PEAK_RSS_LAUNCHER"
  key_links:
    - from: "src/python/run_native_ld_panel.py:process_region"
      to: "_run_plink"
      via: "unchanged call site (was :1017 at basis)"
      pattern: "wall_min, peak_ram_gib = _run_plink\\(cmd\\)"
    - from: "_run_plink"
      to: "_PLINK_PEAK_RSS_LAUNCHER"
      via: "subprocess.Popen of an isolated interpreter with the report pipe passed by fd"
      pattern: "sys\\.executable, \"-I\", \"-S\", \"-c\", _PLINK_PEAK_RSS_LAUNCHER"
    - from: "_PLINK_PEAK_RSS_LAUNCHER"
      to: "plink's own rusage"
      via: "os.wait4 on the plink pid; exit-code helper bound before the spawn; returncode set (no double wait)"
      pattern: "os\\.wait4\\(child\\.pid, 0\\)"
    - from: "tests/m3/test_run_plink_peak_rss.py"
      to: "the REAL _run_plink (never the monkeypatched seam)"
      via: "direct calls + harness subprocesses importing run_native_ld_panel"
      pattern: "drv\\._run_plink\\("
    - from: "src/python/fire_verifier.py:check_peak_ram"
      to: "panel column peak_ram_gib"
      via: "UNCHANGED consumer; now receives per-plink values"
      pattern: "def check_peak_ram"
---

<objective>
Fix RAM-1: `run_native_ld_panel._run_plink` must report the peak resident memory of THE plink process it just ran. It must not report a high-water mark inherited from earlier children or from the driver process itself. This lands before Stage C and is OFF the LD path (measurement wrapper only).

Purpose: over a 276-region serial Stage C, the panel's `peak_ram_gib` column currently flat-lines at a running maximum. For example, m2_region_00057 inherited sub14's 26.5745 GiB. `fire_verifier stage-b`'s `check_peak_ram` evaluates that contaminated series.

Output:
- a RED-first test file (one RED commit);
- a launcher-based `_run_plink` (one fix commit);
- 12 bytecode-safe negative controls with declared, measured failure sets;
- Python 3.9 smoke;
- name-level suite reconciliation;
- a SUMMARY.

<decision_record>
**DECISION (Carter, 2026-09-16): "Small launcher process (Recommended)".** The option text promised:
- bias ≤ ~11 MiB (3.11) / ~4 MiB (3.9), regardless of driver memory;
- error parity with `subprocess.run`;
- one added process on the fire path;
- "plan must also prove SIGTERM/timeout behaviour is no worse than today's subprocess.run".

This plan delivers each promise and pins each one with a named enforcer:
- **bias:** A6 `test_launcher_bias_is_bounded` (< 24 MiB), the 3.9 smoke, and NC10;
- **error parity:** B3, B4 and B5, plus B12/B13 (fd and signal-disposition parity);
- **SIGTERM/timeout:** B10, B11 and B7, plus NC07, NC08 and NC04.

The SUMMARY MUST cite this decision verbatim (Task 3 §5 (a0)).
</decision_record>

WHY NOT THE RECORDED FIX (measured, NCSU login03, 2026-09-16). The defect record (`260824-STAGE-B-HALT…md:124`) says the clean fix is "`subprocess.Popen` + `os.wait4(pid, 0)`, whose `rusage` is that child's own". **That is false in this environment.** At exec, Linux folds the SPAWNING process's memory into the child's `ru_maxrss`:
- **CPython 3.11** (`subprocess._USE_VFORK=True`) and `os.posix_spawn`: the floor is the parent's lifetime high-water. The parent touched and freed 500 MiB (VmHWM 523060 KiB, VmRSS 11400 KiB). A child that was `/usr/bin/true` or `python -c pass` then read **523060 KiB**.
- **CPython 3.9** (fork): the floor is the parent's current resident size. With the parent holding 400 MiB, `/usr/bin/true` read **413992 KiB**. So on 3.9 the recorded fix fails "held" (A3) but not "freed" (A2). The smoke measured freed 9.6 MiB vs held 265.6 MiB.
- **Unmodified `_run_plink`**, imported in a fresh 3.11 process:
  - The FIRST tiny child read **106.8 MiB**, the importer's own numpy/pandas footprint (VmHWM 109504 KiB).
  - A 300 MiB child read 308.0, then a tiny child read **308.0** again.
  - In a fresh process that touched and freed 256 MiB, a tiny child read **362.8 MiB**.
- **Production shape.** Right before every spawn the driver runs `_window_bim_n_var`. That does `read_text().splitlines()` over the whole cohort `.bim` (20,767,864 lines). A 2M-line probe raised VmHWM by about 277 MiB while VmRSS fell back to 27 MiB. The driver also converts `.ld.bin` in-process after plink. So the recorded fix would report the DRIVER's high-water, and the column would flat-line again.
- **Rejected alternative:** a `/proc/self/clear_refs` "5" reset. Its floor is the parent's current RSS, and it adds a host `/proc` capability dependency with no safe failure mode.

The launcher's floor is 11264 KiB (3.11) / 4352 KiB (3.9), measured with the parent holding 400 MiB. NC01 re-observes the recorded fix going RED.

**Planner prototype (measured reference, NOT authoritative).** A full prototype lives OUTSIDE the repo at `/gpfs_common/share01/clintonlab/ckclinto/tmp/260916-ocb-planner-prototype/`. Its MD5SUMS lists: `test_run_plink_peak_rss.py` `ed568d7c…`, `seam_new.txt` `7d74a8f4…`, `make_mutants.py` `b9d3acc2…`, `smoke39.py` `fadf3197…` and `junit_reasons.py` `11b2881c…`. `runs/` holds the logs behind every predicted set below.
- The prototype test file imports the driver from `$OCB_DRV_DIR`. The real file must use the repo bootstrap in Task 1 Step 3.
- You MAY start from these files, but the `<behavior>`/`<action>` text below is the spec.
- Every planner observation must be RE-OBSERVED by you in the repo; none substitutes for yours.
- Measured runtimes: whole new file ~6 s; NC01 ~66 s; NC04 ~67 s; NC08 ~97 s.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md
@.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md  (lines 110-125 only: the RAM-1 record)
@src/python/run_native_ld_panel.py  (lines 74-104 imports, 183-202 the seam, 225-232 `_run_gsutil`, 1013-1020 the caller)
@src/python/fire_verifier.py  (lines 733-754 `check_peak_ram` — READ ONLY, do not edit)

<environment>
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python        # 3.11.15, pytest 9.0.3 — the ONLY test interpreter
PY39=/usr/bin/python3                                                  # 3.9.25, stdlib only (no numpy/pytest) — compile + launcher smoke only
SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/260916-ocb        # mkdir -p; ALL run logs, junit XML, mutants, copies live here (never /tmp, never the repo)
PROTO=/gpfs_common/share01/clintonlab/ckclinto/tmp/260916-ocb-planner-prototype   # read-only reference
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
Node login03 reports nproc=1; run suites SEQUENTIALLY. Full tests/m3 takes ~14 min > the 10-min foreground Bash cap:
run it with run_in_background and wait for the junit XML + the final summary line in the log.
Pytest invocation shape (always): cd $REPO && $PY -m pytest -p no:cacheprovider <targets> -q -rfE --junitxml=$SCRATCH/<name>.xml > $SCRATCH/<name>.log 2>&1
Tools the new tests require at NCSU (measured present): /usr/bin/timeout (GNU coreutils 8.32), true, sh, grep.
</environment>

<interfaces>
Current seam (basis 11f61e8, run_native_ld_panel.py:183-202) — the thing being replaced:
```python
# --------------------------------------------------------------------------- #
# SOLE subprocess seam (tests monkeypatch exactly this one function)          #
# --------------------------------------------------------------------------- #

def _run_plink(cmd: list[str]) -> tuple[float, float]:
    """Run the plink argv via subprocess; return (wall_min, peak_ram_gib).
    ...RUSAGE_CHILDREN.ru_maxrss DELTA ... This is the ONLY subprocess call site ..."""
    rss_before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    t0 = time.time()
    subprocess.run(cmd, check=True)
    wall_min = (time.time() - t0) / 60.0
    rss_after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    peak_kib = max(rss_after - rss_before, rss_after)
    peak_ram_gib = peak_kib / 1024.0 / 1024.0
    return (wall_min, peak_ram_gib)
```
Measured fact: the docstring's "ONLY subprocess call site" is ALREADY false. `_run_gsutil` (:225-232) calls `subprocess.run(["gsutil", ...])`. The corrected wording is "the only place plink is spawned".

Module imports at module scope (DO NOT EDIT the import block; `json`, `os`, `subprocess`, `sys`, `time` are all already imported; `resource` will become unused — leave it, record it in the SUMMARY; `signal` is NOT imported — the parent uses `Popen.terminate()` so it does not need it).

Sole caller (:1017-1019, unchanged):
```python
wall_min, peak_ram_gib = _run_plink(cmd)
result["wall_min"] = round(wall_min, 4)
result["peak_ram_gib"] = round(peak_ram_gib, 4)
```
`cmd` comes from `aou_ld_panel.build_plink_ld_command`: a `list[str]` whose element 0 is the literal `"plink1.9"`.

Consumer (READ ONLY): `fire_verifier.check_peak_ram(peak_gib, vm_gib=120.0, headroom_frac=0.15)` — FAIL CLOSED on None; FAIL if `peak_gib > vm_gib*(1-headroom)`. Note NaN would compare False and PASS (fail-open), which is why `_run_plink` must RAISE rather than return NaN when it cannot measure.

Source-text enforcers that read run_native_ld_panel.py (must stay GREEN; new code and docstrings must NOT contain these substrings anywhere in the file):
- tests/m3/test_run_native_ld_panel.py: `compute_region_ld`, `_write_a3_banded_correlation_bm`, `row_correlation`, `ld_matrix`, `condition_ld_matrix`, `write_conditioned_ld_npz`, `nan_to_num`, `/share/clintonlab`, `/rs1/researchers`, `/gpfs_common`; `--keep-allele-order` in any non-docstring string constant; no module-scope `import hail`.
- tests/m3/test_occlusion_gate_constants.py (comment-stripped source): `0.0005`, `0.005056`, `0.5056`, `3.42`.
- tests/m3/test_fire_verifier.py status-vocabulary AST extractor: every `x["status"] = …` assignment and every `{"status": …}` dict literal. Add NO such key in parent code. (Names inside the launcher STRING are not parsed.)
- tests/m3/test_pairwise_completeness_scan.py ast-extracts `_filter_ancestry` (untouched).
The planner's prototype seam (`$PROTO/seam_new.txt`) was checked free of every substring above.

Measured interpreter fact that shapes A7: `import subprocess` itself reads `os.waitstatus_to_exitcode` (3.11.15 `subprocess.py:107`; 3.9.25 `subprocess.py:1842` in the `Popen` class body). So a launcher prelude of `import os\ndel os.waitstatus_to_exitcode\n` dies at `import subprocess` in EVERY launcher version and cannot discriminate. The planner measured it GREEN on both the before-spawn and after-spawn binding. The discriminating prelude imports subprocess FIRST: `import os, subprocess\ndel os.waitstatus_to_exitcode\n`. That is also the faithful simulation of an interpreter whose subprocess works but whose `os` lacks the helper.
</interfaces>

<measured_baseline>
Planner measurements, NCSU login03, 2026-09-16 (the executor RE-MEASURES the starred rows in Task 1 and records both):
| quantity | value |
|---|---|
| ★ bare `python -c pass` own maxrss (GNU `/usr/bin/time -f %M`, forks from a tiny C parent) | 8192 KiB |
| ★ 300 MiB touched child own maxrss (GNU time) | 315480 KiB (308.1 MiB) |
| ★ smoke_dev python after `import run_native_ld_panel` (VmHWM) | 109504–111424 KiB |
| launcher prototype floor (`-I -S`, imports json/os/signal/subprocess/sys), 3.11 / 3.9 | 11264 / 4352 KiB |
| launcher `_run_plink([true])` bias, 3.11 (prototype A6) / 3.9 (smoke) | ≤ 11.25 / 4.18 MiB |
| ★ direct `Popen`+`wait4` of `python -c pass` while parent HOLDS 400 MiB, 3.11 | 420776 KiB |
| unmodified `_run_plink`: first tiny / 300 MiB / tiny after / tiny after parent alloc+free 256 MiB | 106.8 / 308.0 / 308.0 / 362.8 MiB |
| prototype on unmodified code, RED readings (junit) | A1 307.88, A2 362.98, A3 364.95, A4 364.95, A6 364.95 MiB |
Threshold rationale (constants in the test file, justified in its docstring):
- **`_CEIL_MIB = 64`.** It is 5.8x the launcher floor (11.0 MiB). It is 1.67x below the smallest contaminated reading ever measured (106.8 MiB, which is the importer's footprint alone) and 4.8x below the 300 MiB child.
- **`_BIAS_CEIL_MIB = 24`.** It is 2.1x the worst measured launcher bias on 3.11 (11.25 MiB) and 4.5x below the importer footprint (106.8 MiB). A 32 MiB launcher pad pushes the bias to ~43 MiB, which crosses 24 but stays under 64 (NC10: A6 RED, A1 GREEN).
- **`_BIG_FLOOR_MIB = 250`.** It is 58 MiB below the measured 308 MiB and 3.9x above the ceiling, so the "report ~0 for everything" failure is pinned too.
- **`_HOLD_MIB = 256`.** It gives a harness peak of about 107 + 256 = 363 MiB and a child peak of at most 308 MiB, sequential, so every process stays under 400 MiB.
None of these thresholds is a timing threshold.
</measured_baseline>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Baselines, premise re-measurement, and the RED test file (9 RED / 16 GREEN on unmodified code, reason-checked, RED commit)</name>
  <files>tests/m3/test_run_plink_peak_rss.py</files>
  <behavior>
    Message conventions (W2; Step 4 parses them):
    - every precondition assert message starts with `PRECONDITION:`;
    - every RSS-reading assert message has the form `READING <value:.2f> MiB >= <ceil> MiB (<label>)` or `READING <value:.2f> MiB < <floor> MiB (<label>)`, produced by two helpers `_reading_lt(value_mib, ceil, label)` / `_reading_ge(value_mib, floor, label)`.
    All pidfiles/donefiles written by children are ATOMIC (write `<path>.tmp`, then `os.rename`), and the poller requires non-empty content (I3).

    RED on UNMODIFIED code (9 items):
    - A1 test_second_child_does_not_inherit_first_childs_peak: in-process, the real drv._run_plink. Child A = [sys.executable, "-c", _BIG_SRC]: `_reading_ge(..., 250, "300 MiB child")` asserted FIRST. Then child B = _TINY: `_reading_lt(..., 64, "tiny child after a 300 MiB child")`. Unmodified: B ≈ 308 MiB.
    - A2 test_child_peak_excludes_driver_high_water_after_free: harness imports the driver, touches and frees 256 MiB (then gc.collect()), records /proc/self/status, calls _run_plink(TINY). Preconditions: VmHWM >= 250*1024 KiB AND VmRSS < 200*1024 KiB. READING < 64. Unmodified ≈ 363 MiB.
    - A3 test_child_peak_excludes_driver_resident_memory_while_held: same, but the harness HOLDS the 256 MiB during the call. Precondition: VmRSS >= 250*1024 KiB. READING < 64.
    - A4 test_unwaited_grandchild_is_not_charged_to_child:
      - The child Popen's a grandchild and exits WITHOUT waiting. The grandchild atomically writes its pid, touches 300 MiB, and atomically writes a donefile.
      - PRECONDITION: the donefile appears within 60 s. Then READING < 64.
      - finally: wait up to 60 s for the grandchild to be gone-or-zombie; SIGKILL it if not.
    - A5 test_launcher_without_valid_report_fails_closed[garbage_report|no_report|report_then_nonzero_exit]:
      - `monkeypatch.setattr(drv, "_PLINK_PEAK_RSS_LAUNCHER", src)`, with src ∈ {`"raise SystemExit(7)\n"`; `"import os, sys\nos.write(int(sys.argv[1]), b'not json\\n')\n"`; `"import os, sys\nos.write(int(sys.argv[1]), b'[\"R\", 0, 1024]\\n')\nraise SystemExit(5)\n"`}.
      - `pytest.raises(subprocess.SubprocessError)` around `drv._run_plink(TINY)`, then `type(ei.value) is subprocess.SubprocessError`.
      - Unmodified: AttributeError from monkeypatch.setattr (`<module 'run_native_ld_panel' from '…'> has no attribute '_PLINK_PEAK_RSS_LAUNCHER'`).
    - A6 test_launcher_bias_is_bounded (W3): `true_bin = shutil.which("true")` (None → `pytest.fail("PRECONDITION: …")`); `_reading_lt(mib(_run_plink([true_bin])[1]), 24, "bare `true` = the launcher's own bias")`. Unmodified ≈ 365 MiB.
    - A7 test_launcher_fails_before_spawn_without_waitstatus_to_exitcode (W5):
      - `src = "import os, subprocess\ndel os.waitstatus_to_exitcode\n" + drv._PLINK_PEAK_RSS_LAUNCHER` (subprocess MUST be imported first; see `<interfaces>`); monkeypatch it in.
      - `pytest.raises(subprocess.SubprocessError)` around `_run_plink([sys.executable, "-c", <atomic pid writer>, str(pidfile)])`, then `type(...) is SubprocessError`.
      - Then `assert not pidfile.exists()`: plink must never start.
      - Unmodified: AttributeError reading the missing constant (`module 'run_native_ld_panel' has no attribute '_PLINK_PEAK_RSS_LAUNCHER'`).
    GREEN on UNMODIFIED code (16 items; these pin the contract that must be PRESERVED):
    - B1 test_returns_two_finite_nonnegative_floats: result is a tuple of len 2; each `type(v) is float`, math.isfinite, >= 0.
    - B2 test_waited_grandchild_is_charged_to_child: the child runs `subprocess.run([sys.executable, "-c", _BIG_SRC], check=True)`. READING >= 250.
    - B3 test_nonzero_exit_raises_calledprocesserror_with_original_cmd: cmd = [sys.executable, "-c", "raise SystemExit(3)"]. Assert type is CalledProcessError, returncode == 3, exc.cmd == cmd, exc.output is None, exc.stderr is None.
    - B4 test_signal_killed_child_raises_negative_returncode: cmd = [sys.executable, "-c", "import os, signal; os.kill(os.getpid(), signal.SIGTERM)"]. Assert returncode == -signal.SIGTERM.
    - B5 test_exec_failure_matches_subprocess_run_exactly[missing_abs_path|missing_on_path|not_executable]:
      - cmds: ["plink1.9-ocb-missing-" + uuid4().hex, "--version"]; [str(tmp_path / "nope" / "plink1.9")]; [str(f)] where f is a tmp_path file written with "#!/bin/sh\n" and chmod 0o644.
      - Capture ref = the exception from subprocess.run(cmd, check=True) and got = the exception from drv._run_plink(cmd).
      - Assert type(got) is type(ref), and equal args, errno, strerror, filename, filename2 and str.
    - B6 test_stdout_and_stderr_pass_through_uncaptured_in_order: harness with stdout/stderr redirected to two tmp files. Body: print("H-BEFORE", flush=True); drv._run_plink([sys.executable, "-c", "import sys; print('CHILD-OUT', flush=True); print('CHILD-ERR', file=sys.stderr, flush=True)"]); print("H-AFTER", flush=True). Assert:
      - stdout lines == ["H-BEFORE", "CHILD-OUT", "H-AFTER"] exactly;
      - "CHILD-ERR" is a stderr line;
      - "Traceback" is not in the stderr text;
      - harness rc == 0.
    - B7 test_interrupt_kills_child_and_propagates:
      - Harness body: `try: drv._run_plink([sys.executable, "-c", <atomic pid writer + time.sleep(120)>, pidfile])`, then print a JSON line {"outcome": "returned"}; `except KeyboardInterrupt:` print {"outcome": "KeyboardInterrupt"}.
      - The test polls the pidfile (60 s; fail with the harness stderr if the harness exits first), then `os.kill(harness.pid, SIGINT)` and communicate(timeout=60).
      - Assert outcome == "KeyboardInterrupt", harness rc == 0, and the child pid VANISHED from /proc within 30 s (a 'Z' state is NOT gone here).
      - finally: SIGKILL the child if alive; kill the harness if still running.
    - B8 test_no_fd_zombie_or_resourcewarning_leak: harness body:
      - n0 = len(os.listdir("/proc/self/fd"));
      - with warnings.catch_warnings(record=True) as w: warnings.simplefilter("always"); drv._run_plink(TINY); gc.collect();
      - n1 = the same count;
      - zombie check: os.waitpid(-1, os.WNOHANG) raising ChildProcessError → no_children=True.
      - Print JSON with n0, n1, no_children and the list of ResourceWarning messages.
      - Assert n0 == n1, no_children is True, and the list is empty.
      - This pins the DRIVER's fds only; B12 pins the child's.
    - B9 test_launcher_ignores_cwd_module_shadowing: monkeypatch.chdir(tmp_path); write json.py, signal.py and subprocess.py there, each containing "raise SystemExit(99)\n"; call drv._run_plink(TINY). Assert only that it returns a 2-tuple of floats. Do NOT assert a peak bound here: unmodified code would be RED for the wrong reason.
    - B10 test_driver_sigterm_leaves_plink_to_finish_and_nothing_hangs (BLOCKER):
      - Launch: harness Popen with `start_new_session=True`, stdout DEVNULL, stderr to a tmp file. Body: `drv._run_plink([sys.executable, "-c", child_src, pidfile, releasefile])`. `child_src` atomically writes its pid, then polls up to 120 s for the release file.
      - Before SIGTERM: poll the pidfile; read the child's ppid from `/proc/<c>/stat` (field after the last ')'); watch = [child] + [ppid if ppid != harness.pid] (the launcher).
      - SIGTERM and assert: `os.kill(harness.pid, SIGTERM)`; assert `harness.wait(timeout=30) == -signal.SIGTERM`; create the release file; assert every watched pid is gone-or-zombie within 30 s; assert "Traceback" not in the stderr file.
      - finally: create the release file; SIGKILL any watched pid still running; kill the harness if running.
    - B11 test_timeout_group_sigterm_kills_plink (BLOCKER):
      - Launch: `timeout_bin = shutil.which("timeout")`; None → `pytest.fail("PRECONDITION: …never skip")`. Run `[timeout_bin, "600", sys.executable, "-c", <harness>, …]` with `start_new_session=True`, stderr to a tmp file, and the same body/child as B10.
      - Before SIGTERM: poll the pidfile; watch = [child, ppid] (the launcher, or the harness on unmodified code).
      - SIGTERM and assert: `os.kill(proc.pid, SIGTERM)`; `proc.wait(timeout=30)` (value not asserted); assert every watched pid is gone-or-zombie within 30 s WITHOUT creating the release file first; assert no "Traceback" in stderr.
      - finally: create the release file; SIGKILL survivors; kill proc.
    - B12 test_child_fds_match_subprocess_run (W4): one harness runs child `import os, sys; fds = sorted(os.listdir('/proc/self/fd'), key=int); open(sys.argv[1], 'w').write(' '.join(fds))` through BOTH `subprocess.run(..., check=True)` and `drv._run_plink(...)`, then returns both listings. Assert equal (measured `'0 1 2 3'` both).
    - B13 test_child_signal_dispositions_match_subprocess_run (planner addition, the enforcer for I2):
      - Harness sets SIGINT and SIGHUP to SIG_IGN. Then it runs `[sh, "-c", 'exec grep "^SigIgn" /proc/self/status > "$1"', "sh", outfile]` through BOTH subprocess.run and drv._run_plink, where `sh = shutil.which("sh")` is passed as argv.
      - PRECONDITION: the subprocess.run mask has the SIGINT and SIGHUP bits set.
      - Assert the two SigIgn lines are equal.
      - This pins restore_signals parity and the SIG_IGN-inherited-SIGINT case.
    - C1 test_premise_direct_wait4_charges_parent_resident_memory_to_child: harness WITHOUT the driver import. It HOLDS 256 MiB touched, then p = subprocess.Popen([sys.executable, "-c", "pass"]); _, st, ru = os.wait4(p.pid, 0); p.returncode = os.waitstatus_to_exitcode(st); prints ru.ru_maxrss. Assert >= 250*1024 KiB. It does NOT call _run_plink. Its docstring says it is the PREMISE MONITOR for the launcher: if it goes RED, the kernel/CPython stopped charging parent memory at exec, and `_run_plink`'s rationale must be re-evaluated.
  </behavior>
  <action>
**Step 0 — guards.**
- Run `git -C $REPO log --oneline -3` and `git -C $REPO status --porcelain --untracked-files=no`. Expect HEAD 11f61e8 and an EMPTY tracked status. Anything you did not make → STOP and report.
- Run `mkdir -p $SCRATCH`. Never stage the pre-existing untracked files (`targeted_rerun_*`, `results_lsweep_*`, …).

**Step 1 — baselines BEFORE any edit, in this order, sequential.** Save every log/XML under $SCRATCH.
- (a) Full `tests/m3` → `m3-before.{xml,log}` (background; wait for completion).
- (b) `tests/phase2` → `p2-before.{xml,log}`.
- (c) `tests/m3/test_source_freeze_pins.py` → `pins-before.log`.
- (d) `TMPDIR=$SCRATCH/khttmp /usr/bin/python3 .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py > $SCRATCH/kht-default-before.txt` and the same with `--live` → `kht-live-before.txt`. `mkdir -p $SCRATCH/khttmp` first. The planner observed `--live` at 11f61e8: `RESULT GREEN checks=318 parsed=88 table=88 verified=88`, exit 0.
- Record the exact final summary line of each run.
- STOP conditions:
  - Either kht run is not `RESULT GREEN` (pre-existing drift would confound the post-change attribution).
  - A baseline failed/error item lies in a file that reads the edited module: test_run_native_ld_panel.py, test_fire_verifier.py, test_occlusion_gate_constants.py, test_pairwise_completeness_scan.py or test_source_freeze_pins.py.
- Any other baseline failed/error item: record its node id verbatim and continue. The Task 3 reconciliation then requires its outcome to be UNCHANGED.
- Last recorded values were 1187/33/0 and 136/1/0; re-measured values are authoritative.
- Write `$SCRATCH/junit_outcomes.py`: `python junit_outcomes.py X.xml` prints one line per testcase, `<classname>::<name>\t<outcome>`, sorted. Outcome is:
  - `failed` if a `<failure>` child exists;
  - `error` if `<error>`;
  - `xfailed` if `<skipped type="pytest.xfail">`;
  - `skipped` if another `<skipped>`;
  - else `passed`.
  It also prints to stderr the counts per outcome and the total. Run it on both baseline XMLs → `m3-before.tsv`, `p2-before.tsv`. Reconcile its counts against pytest's own summary line; a mismatch → fix the parser before going on.

**Step 2 — re-measure the premises** (record numbers in the SUMMARY next to the planner's table):
- `/usr/bin/time -f %M $PY -c pass`.
- `/usr/bin/time -f %M $PY -c "<_BIG_SRC>"`.
- The driver import VmHWM: `$PY -c "import sys; sys.path.insert(0,'src/python'); import run_native_ld_panel; print(open('/proc/self/status').read())"` and grep VmHWM.
- A direct Popen+wait4 of `python -c pass` from a python that holds 256 MiB touched.

If the direct reading is < 250*1024 KiB, the launcher's premise does not reproduce → STOP and report. Do not implement.

**Step 3 — write `tests/m3/test_run_plink_peak_rss.py`** with exactly the 21 test functions / 25 collected items in `<behavior>`, using those names. `$PROTO/test_run_plink_peak_rss.py` implements all of them and may be used as a starting point.

Module docstring must contain:
- the RAM-1 defect in 3 sentences;
- the decision record line;
- the measured premise table (planner values + your Step 2 values);
- the threshold rationale from `<measured_baseline>`;
- a table of each test with its expected unmodified-code outcome (RED/GREEN) and why.

Bootstrap (REPLACES the prototype's `$OCB_DRV_DIR` block): `PROJECT_ROOT = Path(__file__).resolve().parents[2]`; `_SRC_PYTHON = PROJECT_ROOT / "src" / "python"`; insert it on sys.path; then `import run_native_ld_panel as drv`. This mirrors test_run_native_ld_panel.py:27-32. The harness path argument is `str(_SRC_PYTHON)`.

Constants: `_CEIL_MIB = 64.0`, `_BIAS_CEIL_MIB = 24.0`, `_BIG_FLOOR_MIB = 250.0`, `_HOLD_MIB = 256`, `_BIG_SRC = "b = bytearray(300 * 2**20)\nfor i in range(0, len(b), 4096):\n    b[i] = 1\n"`, and `_TINY = [sys.executable, "-c", "pass"]`. Convert GiB→MiB by multiplying by 1024.

Harness helpers:
- `_harness_argv(body, *extra, import_driver=True)`: preamble `import gc, json, os, signal, subprocess, sys, time, warnings`; put `sys.argv[1]` on sys.path; when import_driver, `import run_native_ld_panel as drv`; a `_status_kib()` that parses VmHWM/VmRSS from /proc/self/status; then the dedented body.
- `_run_harness_json(tmp_path, body, *extra, import_driver=True, timeout=180)`: runs that argv with `cwd=tmp_path`, `env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}`, capture_output. It asserts rc == 0 with a `PRECONDITION:` message that includes stderr, and returns `json.loads` of the LAST non-empty stdout line.
- Process helpers:
  - `_poll_pidfile(path, proc=None, timeout=60)`: requires non-empty content; fails with `PRECONDITION:` if `proc` exits first.
  - `_stat_fields(pid)`: splits after the last ')' of /proc/<pid>/stat.
  - `_gone(pid, timeout, zombie_counts)`.
  - `_sigkill_quietly(pid)`.

Pass paths into harnesses as argv, never as literals, and put no absolute-path literals in the test file. No timing assertions on RSS. The only time bounds are liveness polls (60/30 s).

**Step 4 — observe RED against the UNMODIFIED code, and check the REASONS (W2).** Run `$PY -m pytest -p no:cacheprovider tests/m3/test_run_plink_peak_rss.py -v -rfE --junitxml=$SCRATCH/red.xml > $SCRATCH/red.log 2>&1`.
- REQUIRED sets: collected == 25; FAILED == exactly {A1, A2, A3, A4, A5[garbage_report], A5[no_report], A5[report_then_nonzero_exit], A6, A7} (9); PASSED == exactly the 16 B/C items. The planner's prototype measured exactly this: `9 failed, 16 passed`.
- REQUIRED reasons: write `$SCRATCH/red_reasons.py` (`$PROTO/junit_reasons.py` is a starting point) to parse each failure's message+text from `red.xml`. STOP unless:
  - A1, A2, A3 and A4 each fail on a `READING <v> MiB >= 64.0 MiB (…)` line with v >= 64, and A1's label is the tiny-after-big one;
  - A6 fails on `READING <v> MiB >= 24.0 MiB (…)` with v >= 24;
  - each A5 case fails with `AttributeError` naming `_PLINK_PEAK_RSS_LAUNCHER`, raised from `monkeypatch.setattr`;
  - A7 fails with `AttributeError: module 'run_native_ld_panel' has no attribute '_PLINK_PEAK_RSS_LAUNCHER'`;
  - NO failure message starts with `PRECONDITION:`.

  Planner-measured readings: A1 307.88, A2 362.98, A3 364.95, A4 364.95, A6 364.95 MiB.
- If a B/C item is RED on unmodified code, the TEST is wrong: it failed to pin the existing contract. Fix the test (never the source), re-run, and record what changed and why.
- If an A item is GREEN, or fails for any other reason → STOP and report (its premise or its design is broken).
- Paste the `-rfE` short summary and the reason table (item | kind | value | label) into the SUMMARY verbatim.

**Step 5 — RED commit.**
- Pre-commit guard (`git log --oneline -3` and the tracked status; only your file may appear).
- `git add tests/m3/test_run_plink_peak_rss.py`.
- Commit message: `test(quick-260916-ocb): RED — per-child peak RSS + _run_plink contract/parity pins (9 RED on unmodified code: inheritance across calls, driver high-water, driver resident memory, unwaited grandchild, launcher fail-closed x3, launcher bias, fail-before-spawn; 16 GREEN pins incl. exec-error identity, fd + signal-disposition parity with subprocess.run, SIGINT kill-through, driver-SIGTERM and timeout-group-SIGTERM parity)`, ending with the line `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- GPFS "invalid object / Error building trees" → STOP and report.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest -p no:cacheprovider tests/m3/test_run_plink_peak_rss.py -q -rfE 2>&1 | tail -14   # EXPECT at this commit: 9 failed, 16 passed; FAILED ids == A1,A2,A3,A4,A5[garbage_report|no_report|report_then_nonzero_exit],A6,A7</automated>
  </verify>
  <done>
    - Baseline logs, XMLs and TSVs exist in $SCRATCH with recorded summary lines; both kht modes were GREEN before the edit.
    - Premises re-measured and recorded.
    - The test file is committed alone.
    - Its observed outcome on unmodified code is exactly 9 RED / 16 GREEN, and every RED fails for its declared reason (READING values / AttributeError), with no PRECONDITION failure. RED output and the reason table are captured verbatim.
    - `git status --porcelain --untracked-files=no` is empty after the commit.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: GREEN — launcher-based _run_plink + docstring, 12 whole-file negative controls with declared failure sets, Python 3.9 smoke, fix commit</name>
  <files>src/python/run_native_ld_panel.py</files>
  <behavior>
    - All 25 items in tests/m3/test_run_plink_peak_rss.py PASS. The test file is byte-identical to the RED commit: `git diff HEAD -- tests/` is empty. If any test seems to need an edit → STOP and report; never weaken a committed RED.
    - These stay GREEN: tests/m3/test_run_native_ld_panel.py, tests/m3/test_fire_verifier.py, tests/m3/test_occlusion_gate_constants.py, tests/m3/test_pairwise_completeness_scan.py, tests/m3/test_source_freeze_pins.py.
    - Each negative control NC01-NC12, run over the WHOLE new file, yields a FAILED set EXACTLY equal to its declared set, with every other item PASSED. Then the file is restored byte-identical (cmp) and all 25 are observed GREEN again.
  </behavior>
  <action>
**Step 1 — implement (per `<decision_record>`).** Edit ONLY basis lines 183-202 of `src/python/run_native_ld_panel.py`. Do not touch lines 1-182 (the import block and constants stay line-stable) or anything after `_run_plink`. `$PROTO/seam_new.txt` is the planner's measured version of exactly this block (it replaces basis lines 183-202 verbatim; +117 lines).

(a) Banner lines 183-185: change the middle line to `# SOLE plink subprocess seam (tests monkeypatch exactly this one function)    #`, with FOUR spaces before the closing `#`. Verify `len(line) == 79` with python (planner measured 79). The old "SOLE subprocess seam" was already false (`_run_gsutil` at :225-232).

(b) Directly below the banner, add a `#:` comment (2-4 lines) plus the module-private constant `_PLINK_PEAK_RSS_LAUNCHER = r'''…'''`, whose content is exactly this program (Python 3.9-compatible; stdlib only):
```python
import json, os, signal, subprocess, sys

exitcode_of = os.waitstatus_to_exitcode  # bound BEFORE the spawn: fail before plink runs
report_fd = int(sys.argv[1])
argv = sys.argv[2:]
child = None
kill_requested = False


def _report(record):
    try:
        os.write(report_fd, (json.dumps(record) + "\n").encode("ascii"))
    except OSError:
        pass  # the driver is gone (EPIPE): nobody is left to read the report


def _kill_child(signum, frame):
    global kill_requested
    kill_requested = True
    if child is not None and child.returncode is None:
        try:
            os.kill(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


signal.signal(signal.SIGTERM, _kill_child)
if signal.getsignal(signal.SIGINT) is not signal.SIG_IGN:
    signal.signal(signal.SIGINT, _kill_child)
try:
    child = subprocess.Popen(argv)
except OSError as exc:
    _report(["E", exc.errno, exc.strerror, exc.filename])
    raise SystemExit(0)
if kill_requested:
    _kill_child(None, None)
_, wait_status, usage = os.wait4(child.pid, 0)
child.returncode = exitcode_of(wait_status)
_report(["R", child.returncode, usage.ru_maxrss])
```
Why each piece exists (put the short form in the `#:` comment or the `_run_plink` docstring, not both):
- `subprocess.Popen` inside the launcher reproduces the parent's old exec semantics exactly: PATH lookup, `restore_signals`, `close_fds` (so plink never inherits the report fd; B12), and the exec-error exception. `close_fds=False` would also switch 3.11 to its posix_spawn path and change plink's ignored-signal mask (NC09 measured SigIgn `0x180000003` vs `0x3`).
- `exitcode_of` is bound before the spawn, so an interpreter without `os.waitstatus_to_exitcode` fails before plink runs instead of after hours of compute (A7).
- The SIGTERM handler is installed BEFORE the spawn and the `kill_requested` re-check comes AFTER it, so an early SIGTERM cannot orphan plink.
- Handlers, not SIG_IGN: handled signals reset to default across exec, while ignored ones would be inherited by plink (NC08 turns B4/B7/B11/B13 RED).
- The SIGINT handler is installed ONLY if SIGINT was not already ignored. A driver started with SIGINT ignored (e.g. a background job of a non-interactive shell) must hand plink an ignored SIGINT, exactly as `subprocess.run` did (B13; NC12).
- `_report` swallows `OSError`: if the driver died (e.g. `kill <pid>`), the launcher exits silently after plink finishes (B10; NC07).
- `child.returncode` is set right after `os.wait4`, so Popen never waits on a reaped pid (no double wait, no ResourceWarning).
- The pid-reuse window between reap and assignment is the same one `Popen.kill` already has. It is not made stricter.

(c) Replace `_run_plink`'s body (signature unchanged: `def _run_plink(cmd: list[str]) -> tuple[float, float]:`):
```python
    read_fd, write_fd = os.pipe()
    chunks: list[bytes] = []
    t0 = time.time()
    try:
        with subprocess.Popen(
            [sys.executable, "-I", "-S", "-c", _PLINK_PEAK_RSS_LAUNCHER, str(write_fd), *cmd],
            pass_fds=(write_fd,),
        ) as launcher:
            os.close(write_fd)
            write_fd = -1
            try:
                while True:
                    chunk = os.read(read_fd, 4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                launcher.wait()
            except BaseException:
                launcher.terminate()  # launcher SIGKILLs plink, reports, exits
                launcher.wait()
                raise
    finally:
        os.close(read_fd)
        if write_fd != -1:
            os.close(write_fd)
    wall_min = (time.time() - t0) / 60.0
    try:
        record = json.loads(b"".join(chunks).decode("ascii"))
    except ValueError:  # JSONDecodeError and UnicodeDecodeError are both ValueError
        record = None
    ran = (isinstance(record, list) and len(record) == 3 and record[0] == "R"
           and all(type(v) is int for v in record[1:]))
    exec_failed = (isinstance(record, list) and len(record) == 4 and record[0] == "E"
                   and type(record[1]) is int and isinstance(record[2], str)
                   and (record[3] is None or isinstance(record[3], str)))
    if launcher.returncode != 0 or not (ran or exec_failed):
        raise subprocess.SubprocessError(
            f"plink peak-RSS launcher exited {launcher.returncode} without a valid "
            f"report; refusing to fabricate wall_min/peak_ram_gib for {cmd!r}")
    if exec_failed:
        # OSError(errno, strerror, filename) constructs the errno's subclass, e.g.
        # FileNotFoundError — identical to what subprocess.run(cmd) raised here.
        raise OSError(record[1], record[2], record[3])
    if record[1] != 0:
        raise subprocess.CalledProcessError(record[1], cmd)
    return (wall_min, record[2] / 1024.0 / 1024.0)
```
Local variable names are free, but there must be NO `["status"]` subscript assignment and NO `"status":` dict key (the status-vocabulary AST enforcer). No banned substring (see `<interfaces>`).

(d) Rewrite `_run_plink`'s docstring to state the TRUE semantics. Everything stated must be measured or pinned:
- First line: `Run the plink argv; return (wall_min, peak_ram_gib) for THIS plink process.`
- `peak_ram_gib` = plink's OWN peak RSS from `os.wait4`'s rusage for the plink pid. This includes descendants plink itself waited for, and not descendants it did not wait for. Enforcers: test_waited_grandchild_is_charged_to_child and test_unwaited_grandchild_is_not_charged_to_child.
- It also includes a constant floor of a few MiB, the launcher interpreter's own resident size. Enforcer: test_launcher_bias_is_bounded (< 24 MiB).
- It is never inherited from earlier calls or from the driver's memory.
- Linux `ru_maxrss` is KiB (→ /1024/1024 GiB). macOS reports bytes. This module targets Linux (the AoU analysis VM, NCSU) and does no platform branching.
- WHY a launcher. At exec, the child's `ru_maxrss` absorbs the SPAWNING process's memory. Measured 2026-09-16: CPython 3.11 subprocess (vfork) charges the parent's lifetime high-water; CPython 3.9 (fork) charges the parent's current resident size. This driver reads the whole cohort `.bim` just before each spawn and loads `.ld.bin` matrices in-process after, so a direct `Popen(cmd)` + `os.wait4` would report the driver's memory. The pre-260916 `RUSAGE_CHILDREN` reading additionally never decreased across children, which is how `m2_region_00057` inherited `sub14`'s 26.5745 GiB. Premise monitor: test_premise_direct_wait4_charges_parent_resident_memory_to_child.
- Contract (pinned by tests/m3/test_run_plink_peak_rss.py):
  - stdout/stderr, fds and signal dispositions are inherited as `subprocess.run(cmd, check=True)` left them.
  - A non-zero exit raises `subprocess.CalledProcessError(returncode, cmd)`; a negative returncode means killed by that signal.
  - Failure to execute plink raises the same `OSError` subclass and args (e.g. `FileNotFoundError: [Errno 2] No such file or directory: 'plink1.9'`).
  - A launcher without a valid report raises `subprocess.SubprocessError`, never numbers (NaN would pass `fire_verifier.check_peak_ram` open).
  - An exception while waiting (e.g. KeyboardInterrupt) terminates the launcher, which SIGKILLs plink, then re-raises. `subprocess.run` also killed the child; its 0.25 s SIGINT grace is not reproduced.
  - SIGTERM to the driver alone leaves plink running to completion (as before). SIGTERM to the process group (GNU `timeout` expiry) kills plink (as before).
  - No EINTR loop is needed: `os.read`/`waitpid`/`wait4` retry automatically since PEP 475.
  - `wall_min` includes launcher start-up (tens of ms).
- Keep: headless-safe on a Spot VM (no /usr/bin/time dependency).
- Keep, corrected: `This is the ONLY place plink is spawned (gsutil has its own seam, _run_gsutil), so tests monkeypatch a single seam.`

**Step 2 — GREEN.**
- Delete `src/python/__pycache__/run_native_ld_panel.*.pyc`.
- `$PY -m pytest -p no:cacheprovider tests/m3/test_run_plink_peak_rss.py -v -rfE > $SCRATCH/green.log 2>&1` → 25 passed.
- Then run the five enforcer/neighbour files from `<behavior>` → all GREEN.
- `git diff HEAD --stat` shows ONLY `src/python/run_native_ld_panel.py`.
- `cp src/python/run_native_ld_panel.py $SCRATCH/rnlp.GREEN.py`; `md5sum` it.

**Step 3 — negative controls (W1).** Each runs the WHOLE file. The observed FAILED set must EQUAL the declared set below, with ALL other items PASSED. A mutation that does not apply is a failed control, not a pass. Protocol for each NCnn:
1. Build the mutant with a python script (`$PROTO/make_mutants.py` does all 12) that reads `$SCRATCH/rnlp.GREEN.py`, asserts each anchor occurs EXACTLY once (for NC01, locate `_run_plink` via `ast` FunctionDef lineno..end_lineno), writes the mutant over `src/python/run_native_ld_panel.py`, and prints the md5 (must differ from GREEN). The `"-I", "-S", "-c"` argv text ALSO appears in the `#:` comment, so NC03's anchor must be the code-specific `"-I", "-S", "-c", _PLINK_PEAK_RSS_LAUNCHER, str(write_fd)`. The planner's exactly-once guard caught the ambiguous form.
2. `rm -f src/python/__pycache__/run_native_ld_panel.*.pyc`.
3. `PYTHONDONTWRITEBYTECODE=1 $PY -B -m pytest -p no:cacheprovider tests/m3/test_run_plink_peak_rss.py -q -rfE --junitxml=$SCRATCH/NCnn.xml > $SCRATCH/NCnn.log 2>&1`.
4. Compute FAILED/PASSED sets from the XML. REQUIRED: FAILED == declared; PASSED == the other items; collected == 25. Any difference → STOP and report both sets (do not "adjust" the declaration).
5. `cp $SCRATCH/rnlp.GREEN.py src/python/run_native_ld_panel.py && cmp $SCRATCH/rnlp.GREEN.py src/python/run_native_ld_panel.py`, then rm the pyc.

Declared sets. Every set was MEASURED on 3.11.15 with the planner prototype; logs are in `$PROTO/runs/NC*.log`. Ids: A5×3 = the three A5 params, B5×3 = the three B5 params.
| NC | mutation (anchor → replacement) | declared FAILED set | planner measured |
|---|---|---|---|
| NC01 | recorded fix: `_run_plink` body → `proc = subprocess.Popen(cmd)`; `_, st, ru = os.wait4(proc.pid, 0)`; `proc.returncode = os.waitstatus_to_exitcode(st)`; `CalledProcessError(proc.returncode, cmd)` if non-zero; return `(wall, ru.ru_maxrss/1024/1024)` | A1, A2, A3, A4, A5×3, A6, A7, B7 | 10 failed / 15 passed, 66 s |
| NC02 | `CalledProcessError(record[1], cmd)` → `(record[1], launcher.args)` | B3 | 1 / 24 |
| NC03 | drop `"-I", ` (code-specific anchor above) | B9 | 1 / 24 |
| NC04 | launcher `_kill_child` body → `pass` | B7 | 1 / 24, 67 s |
| NC05 | delete `os.close(read_fd)` from the parent's `finally` | B8 | 1 / 24 |
| NC06 | `OSError(record[1], record[2], record[3])` → `OSError(record[1], record[2])` | B5×3 | 3 / 22 |
| NC07 | `_report` without its try/except (bare `os.write`) | B10 | 1 / 24 |
| NC08 | `signal.signal(signal.SIGTERM, _kill_child)` → `signal.signal(signal.SIGTERM, signal.SIG_IGN)` | B4, B7, B11, B13 | 4 / 21, 97 s |
| NC09 | `subprocess.Popen(argv)` → `subprocess.Popen(argv, close_fds=False)` | B12, B13 | 2 / 23 |
| NC10 | insert a 32 MiB touched pad (`_pad = bytearray(32 * 2**20)` + touch loop) before `try:\n    child = subprocess.Popen(argv)` | A6 (A1 must stay GREEN) | 1 / 24 |
| NC11 | delete the `exitcode_of = …` line; `exitcode_of(wait_status)` → `os.waitstatus_to_exitcode(wait_status)` | A7 | 1 / 24 |
| NC12 | the SIGINT `if …: signal.signal(…)` → unconditional `signal.signal(signal.SIGINT, _kill_child)` | B13 | 1 / 24 |
Notes on the sets:
- **NC01.** The recorded fix passes B10/B11/B12/B13/C1 (it spawns plink directly). It fails B7 because nothing kills the child on KeyboardInterrupt.
- **Recorded fix on 3.9 (fork).** It would fail A3 (held) but NOT A2 (freed); see the Step 4 smoke. The declared sets are 3.11 sets, the only test interpreter.
- **NC08 collateral** is legitimate. plink inherits an ignored SIGTERM, so it survives its own SIGTERM (B4 "DID NOT RAISE"). The group SIGTERM (B11) and the terminate path (B7) also fail, and SigIgn differs (B13).
- **NC09's extra B13 failure** is the posix_spawn path noted in Step 1(b). B12 measured `'0 1 2 3 4'` vs `'0 1 2 3'`.

After all twelve: run the full new file → 25 passed; `md5sum src/python/run_native_ld_panel.py` == the GREEN md5; `git diff HEAD --stat` unchanged from Step 2. Record a table NCnn | mutation | declared set | observed FAILED set | equal? | key observed value (NC01's A2/A3 MiB, NC10's A6 MiB) | restore cmp OK.

**Step 4 — Python 3.9 compatibility (scratch-only, nothing committed).**
- (a) `$PY39 -c "import sys; p=sys.argv[1]; compile(open(p).read(), p, 'exec'); print('compile OK', sys.version.split()[0])" src/python/run_native_ld_panel.py`. `compile()` writes no pyc.
- (b) `$SCRATCH/smoke39.py` (`$PROTO/smoke39.py` is the measured prototype). It `ast.parse`s the module and takes `ast.get_source_segment` for the `_PLINK_PEAK_RSS_LAUNCHER` Assign and the `_run_plink` FunctionDef. It `exec`s both, prefixed with `from __future__ import annotations`, into a namespace pre-loaded with `json, os, subprocess, sys, time`. Checks, each printed PASS/FAIL (planner-measured values in brackets):
  - interpreter is 3.9 [3.9.25];
  - 300 MiB child >= 250 [306.79];
  - tiny after big < 64 [7.00];
  - `run([shutil.which("true")])` bias < 24 [4.18] (W3);
  - I5, fork case: parent HOLDS 256 MiB touched → launcher reading of `python -c pass` < 24 [7.00];
  - I5, fork case: the same parent's direct Popen+wait4 >= 250 MiB [265.6] (premise);
  - I5, fork case: after `del` of the 256 MiB, direct wait4 < 64 [9.6] (why the recorded fix passes A2 on 3.9);
  - returncode 3 → CalledProcessError with the original cmd;
  - SIGTERM → -15;
  - ENOENT exception identical to `subprocess.run`'s (type/args/filename/str).
  Run `$PY39 $SCRATCH/smoke39.py src/python/run_native_ld_panel.py`. All PASS (planner: `SMOKE39 PASS 10/10`), else STOP and report. The planner also ran it on the NC01 mutant, which went `FAIL 9/10` on exactly the held-parent launcher check. Re-observe that on NC01 once and record it.

**Step 5 — fix commit.**
- Pre-commit guard (`git log --oneline -3` shows the Task 1 RED commit on top; the tracked status shows only `src/python/run_native_ld_panel.py`).
- `git add src/python/run_native_ld_panel.py`.
- Commit message: `fix(quick-260916-ocb): _run_plink reports plink's OWN peak RSS via a small isolated launcher + os.wait4 (RAM-1; Carter 2026-09-16 "Small launcher process (Recommended)"; the recorded direct Popen+wait4 fix measured RED — at exec the child absorbs the driver's memory); subprocess.run(check=True) contract, fd/signal-disposition parity and SIGTERM/timeout behaviour preserved and pinned; 12 negative controls reproduced their declared failure sets`, ending with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- GPFS object-store error → STOP and report.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && rm -f src/python/__pycache__/run_native_ld_panel.*.pyc && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest -p no:cacheprovider tests/m3/test_run_plink_peak_rss.py tests/m3/test_run_native_ld_panel.py tests/m3/test_fire_verifier.py tests/m3/test_occlusion_gate_constants.py tests/m3/test_source_freeze_pins.py -q 2>&1 | tail -3 && git diff HEAD~1 --stat   # EXPECT 0 failed; the fix commit touches only src/python/run_native_ld_panel.py</automated>
  </verify>
  <done>
    - 25/25 new tests GREEN at the fix commit, and the test file is unchanged since the RED commit.
    - The enforcer/neighbour files are GREEN.
    - NC01-NC12 each reproduced its declared FAILED set EXACTLY (whole file, all others passed), with the file restored byte-identical (cmp) and GREEN re-observed.
    - Python 3.9 compile + 10-check smoke PASS, and the NC01 smoke re-observed failing only the held-parent check.
    - Fix commit contains only run_native_ld_panel.py.
  </done>
</task>

<task type="auto">
  <name>Task 3: Full-suite reconciliation by node id, freeze pins, kht verifier drift record, symbol- and hunk-level scope proof, SUMMARY</name>
  <files>.planning/quick/260916-ocb-ram-1-per-child-peak-rss-for-run-plink-v/260916-ocb-SUMMARY.md</files>
  <action>
No source or test edits in this task. Any RED below → STOP and report; do not "fix" forward.

**1. Final suites** (same interpreter, sequential): full `tests/m3` → `m3-after.{xml,log}` (background, wait); `tests/phase2` → `p2-after.{xml,log}`; `test_source_freeze_pins.py` → `pins-after.log`. Run `junit_outcomes.py` → `m3-after.tsv`, `p2-after.tsv`.

**2. Name-level reconciliation** (a scratch python script, output saved to `$SCRATCH/reconcile.txt`). For each suite compute:
- added = after_ids − before_ids;
- removed = before_ids − after_ids;
- changed = the ids in both whose outcome differs.

REQUIRED:
- `tests/m3`: added == exactly the 25 ids of `tests/m3/test_run_plink_peak_rss.py` (cross-check against `$PY -m pytest -p no:cacheprovider --collect-only -q tests/m3/test_run_plink_peak_rss.py`), all `passed`; removed == ∅; changed == ∅.
- `tests/phase2`: added == removed == changed == ∅.
- Arithmetic: after totals per outcome == before totals + {passed: +25}.

Anything else → STOP and report the exact ids.

**3. kht verifier.**
- Run `TMPDIR=$SCRATCH/khttmp /usr/bin/python3 .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py > $SCRATCH/kht-default-after.txt`. REQUIRED: last line `RESULT GREEN …`. Its default mode reads cited files at basis c93e97b, so a RED here means something other than line drift → STOP.
- Run the same with `--live` → `kht-live-after.txt`; exit code is expected non-zero if line numbers moved. Extract every line starting `RED ` and the cNN citation id in it.
- For each RED cNN, find that id's `c-res:cNN` line in the same output. REQUIRED: it resolves to `src/python/run_native_ld_panel.py` and the cited start line is >= 184 (the first edited line). Any RED on a different file, or at a line < 184 → STOP.
- Record the exact RED id list and the RESULT line: this is the EXPECTED, DOCUMENTED drift. Do NOT edit the banked draft or its verifier.

**4. Scope proof** (`$SCRATCH/scope_proof.py`, output saved).
- **Symbol level.** For `src/python/run_native_ld_panel.py` at `11f61e8` (`git show`) vs HEAD, `ast.parse` both. For every top-level node EXCEPT the `_run_plink` FunctionDef and the new `_PLINK_PEAK_RSS_LAUNCHER` Assign, compare `ast.get_source_segment` text pairwise in order, plus the module docstring. REQUIRED: all identical, and HEAD has exactly one additional top-level Assign (the constant). This covers the import block.
- **Hunk level (I4; the AST proof cannot see comments).** Parse every `@@ -a[,b] +c[,d] @@` header of `git diff -U0 11f61e8..HEAD -- src/python/run_native_ld_panel.py`. REQUIRED for each old-side range:
  - if b > 0 (or b omitted, meaning 1): `183 <= a` and `a + b - 1 <= 202`;
  - if b == 0 (pure insertion after line a): `182 <= a <= 202`.
  The planner's prototype diff measured old-side hunks `-184`, `-186,0`, `-188`, `-190,4`, `-195`, `-197`, `-199,4`, all inside. If the real diff shows a hunk outside only because git aligned blank lines differently, re-run with `--diff-algorithm=patience` and record both outputs. A hunk outside under both → STOP.
- `git diff --name-only 11f61e8..HEAD` == {`src/python/run_native_ld_panel.py`, `tests/m3/test_run_plink_peak_rss.py`}.
- Frozen paths: the two-file `--name-only` equality plus an empty `git status --porcelain --untracked-files=no` proves no frozen path changed. No per-glob pathspec loop is needed.

**5. Write the SUMMARY** (`260916-ocb-SUMMARY.md`, summary template; the executor does NOT commit it). It MUST contain:
- (a0) **DECISION**: quote verbatim `Carter, 2026-09-16: "Small launcher process (Recommended)"`, its four promises, and, per promise, the enforcing tests/controls and their observed outcomes (the `<decision_record>` mapping).
- (a) the planner's measured deviation from the recorded fix, plus your Step-2 re-measurements side by side;
- (b) the Task-1 RED output verbatim (9 RED / 16 GREEN) with the reason table, and any B/C test fixed before the RED commit, with the reason;
- (c) the GREEN output;
- (d) the NC01-NC12 table (declared vs observed sets), with NC01's A2/A3 MiB readings called out as "the recorded fix, observed RED";
- (e) the Python 3.9 compile + smoke output (including the I5 fork cases and the NC01 smoke re-observation);
- (f) baseline and final exact summary lines for `tests/m3`, `tests/phase2` and freeze pins, plus the name-level reconciliation result (the 25 added ids listed, removed ∅, changed ∅);
- (g) kht default RESULT line before/after, the `--live` RESULT line before/after, and the exact RED id list, marked EXPECTED DRIFT (lines after basis :202 moved by +N; state N as the measured line delta; the planner's prototype measured +117);
- (h) symbol-level and hunk-level scope proof outputs;
- (i) CONTRACT DELTAS AND FIRE-PATH BEHAVIOUR. Each item is marked as measured by a named test, or as not tested:
  - launcher failure → `SubprocessError` (new, fail-closed; A5/A7);
  - no 0.25 s SIGINT grace before the kill (B7);
  - `wall_min` includes launcher start-up;
  - a `PathLike` `cmd[0]`'s exec-error filename becomes `str` (signature is `list[str]`; `build_plink_ld_command` returns `str`);
  - an empty `cmd` raises `SubprocessError` rather than `IndexError` (out of contract);
  - **SIGTERM.** SIGTERM is catchable; Python's default action simply terminates the driver without running `finally` blocks.
    - **(1) SIGTERM to the process group.** GNU `timeout` without `--foreground` sends SIGTERM to its whole process group at expiry (measured with coreutils 8.32 at NCSU). plink is KILLED, TODAY and with the launcher (B11); the launcher also SIGKILLs it.
    - **(2) SIGTERM to the driver ALONE** (`kill <driver pid>`, `timeout --foreground`). The driver exits -15 and plink keeps running to completion, TODAY and with the launcher. The launcher then finds no reader, swallows EPIPE and exits without a traceback (B10).
    - **(3) SIGKILL to the driver.** Same as (2): plink runs on. Not tested separately.
  - **SIGINT parity (I2).** The launcher installs its SIGINT handler only when SIGINT was not inherited as ignored, so a SIGINT-ignoring driver (e.g. a background job of a non-interactive shell) still hands plink an ignored SIGINT (B13, NC12). A Ctrl-C to the foreground group reaches plink directly, as before.
  - **(I6) Launcher killed alone** (the OOM killer choosing the ~11 MiB launcher is very unlikely, or `kill -9 <launcher>`). plink keeps running. The driver sees the pipe close with no report, raises `SubprocessError` for that region, and the loop starts the NEXT region, so TWO plinks can run concurrently until the orphan finishes. Not tested; accepted as unlikely.
  - **(I7) Process matching.**
    - plink's parent process is now the launcher.
    - `pgrep -f plink1.9` / `pkill -f plink1.9` now ALSO match the launcher, because its argv contains the full plink argv.
    - `pkill -f plink1.9` therefore SIGTERMs the launcher too. It SIGKILLs plink, so the region's returncode is -9, not -15.
    - `pgrep plink1.9` without `-f` is unaffected.
    - The Stage C runbook has no ancestry-based liveness check (planner grep of `260812-ox1-*` found none).
  - **One added process per plink call** (Carter's accepted cost), ~11 MiB (3.11) / ~4 MiB (3.9).
- (j) HISTORICAL DATA — NOT retro-edited:
  - Already-banked Stage A/B panel rows carry the OLD semantics. Under the old code, EVERY reading = max(driver high-water at spawn, plink's own, every earlier child's reading).
  - `m2_region_00057`'s 26.5745 is inherited (it equals `sub14`'s).
  - Region 1's 30.6591 came from its own Stage-A process, so there is no earlier-child inheritance. It is still max(that driver's pre-spawn high-water, which includes the cohort `.bim` scan, plink's own), so attribution to plink alone is not proven by the TSV.
  - Region 17's 2.9689, recorded as "real, first child", is likewise NOT attributable to plink alone: the first tiny child under the unmodified code read the importer's footprint (106.8 MiB), not its own ~8 MiB.
  - Do not quote any old `peak_ram_gib` as a plink measurement.
- (k) FOLLOW-UPS, not done:
  - `import resource` is now unused and was left to keep lines 1-182 stable;
  - `tests/m3/test_run_native_ld_panel.py:14` still says "SOLE subprocess seam" (frozen here);
  - COST-1's Stage-B→C RAM extrapolation must use only post-fix readings;
  - `HANDOFF.json`/STATE RAM-1 wording ("Popen + os.wait4") should be refreshed by the orchestrator to "small isolated launcher + os.wait4 (direct wait4 measured contaminated; Carter 2026-09-16)";
  - **PRE-FIRE ITEM (W5):** record `python3 -V` (and `python -V` if that is the fire interpreter) on the AoU VM before Stage C. `os.waitstatus_to_exitcode` needs ≥ 3.9. A7 guarantees an older interpreter fails at region 1 before any plink compute, but it would still fail.
- (l) **Observations not acted on (for Carter; out of scope for this task, nothing edited).**
  - **The problem.** The committed fire command `nohup timeout 312h python3 …` (`260812-ox1-AGENT-PROMPT.md:398`, `BROWSER-PASTE.md:532`) does not shield the driver from SIGHUP. GNU timeout 8.32 installs its own SIGHUP handler over nohup's SIG_IGN and forwards SIGHUP to the group.
  - **Plan-checker measurements.** SIGHUP kills a driver stand-in under `nohup timeout 600 python`, but it survives under `nohup python` or `timeout 600 nohup python`.
  - **Unmeasured.** The VM's coreutils version, and whether closing a Jupyter terminal sends SIGHUP.
  - **Relation to this change.** The launcher is neutral to this exposure: it neither adds nor removes it.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && tail -1 /gpfs_common/share01/clintonlab/ckclinto/tmp/260916-ocb/kht-default-after.txt && cat /gpfs_common/share01/clintonlab/ckclinto/tmp/260916-ocb/reconcile.txt && git diff --name-only 11f61e8..HEAD && git diff -U0 11f61e8..HEAD -- src/python/run_native_ld_panel.py | grep '^@@' && git status --porcelain --untracked-files=no   # EXPECT: RESULT GREEN; m3 added=25 removed=0 changed=0; phase2 all 0; exactly the 2 files; every old-side hunk within 183-202; tracked status empty</automated>
  </verify>
  <done>
    - `tests/m3` and `tests/phase2` reconcile by node id to baseline plus exactly the 25 new passed items.
    - Freeze pins GREEN before and after.
    - kht default GREEN after the commits; kht `--live` RED ids (if any) are all run_native_ld_panel.py citations at line >= 184 and are listed as expected drift.
    - Symbol-level and hunk-level scope proofs pass.
    - The SUMMARY exists with sections (a0)-(l), citing the decision verbatim.
    - Nothing else is modified or staged.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| driver → launcher interpreter | `sys.executable` runs a module-constant program; argv comes from `build_plink_ld_command` (list[str], no shell) |
| launcher → driver report pipe | a single JSON record the driver parses and must not over-trust |
| working directory → launcher imports | a cwd `json.py`/`subprocess.py` could hijack a non-isolated `-c` interpreter |
| signals → driver / launcher / plink | SIGINT, SIGTERM (driver-only or group) and SIGKILL must leave plink in the same state as under `subprocess.run` |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-ocb-01 | Tampering | launcher imports | mitigate | launcher runs `-I -S` (no cwd/env on sys.path, no site); pinned by B9, and NC03 (drop `-I`) observed RED |
| T-ocb-02 | Repudiation | fabricated RAM numbers | mitigate | strict record validation (types, arity, tag) + launcher rc == 0, else `SubprocessError`; never NaN (NaN passes `check_peak_ram` open); pinned by A5×3; an interpreter without `os.waitstatus_to_exitcode` fails before the spawn (A7, NC11) |
| T-ocb-03 | Denial of service | plink left running or killed differently than today | mitigate | **(a) SIGINT/KeyboardInterrupt in the driver.** Parent `terminate()` → launcher SIGKILLs plink (handler installed before the spawn, `kill_requested` re-check after). Pinned by B7; NC04 observed RED. **(b) Group SIGTERM** (GNU `timeout` expiry without `--foreground`). plink is killed as today; pinned by B11; NC08 observed RED. **(c) SIGTERM to the driver alone.** plink runs to completion as today; the launcher exits without a traceback and nothing hangs. Pinned by B10; NC07 observed RED. **(d) Launcher SIGKILLed alone.** plink runs on while the next region starts. Accepted, not tested; listed in SUMMARY (i). |
| T-ocb-04 | Denial of service / information leak | fd / zombie leak over 276 serial regions; report fd leaking into plink | mitigate | **Driver side:** pipe fds closed in `finally`, returncode set after `wait4`; pinned by B8; NC05 observed RED. **Child side:** the launcher's `subprocess.Popen` keeps `close_fds=True`, so plink's fd set equals `subprocess.run`'s; pinned by B12; NC09 observed RED (extra fd 4). B8 does NOT pin child fds. |
| T-ocb-05 | Elevation of privilege | launcher execution | accept | same uid, same interpreter the driver already runs, argv list with no shell and no string interpolation |
| T-ocb-06 | Information disclosure | stdio capture | accept | nothing captured; stdout/stderr inherited exactly as before (B6) |
| T-ocb-07 | Tampering | signal dispositions handed to plink | mitigate | launcher installs handlers (reset to default at exec) and leaves an inherited-ignored SIGINT ignored; plink's SigIgn mask equals `subprocess.run`'s with SIGINT and SIGHUP ignored in the driver; pinned by B13; NC08, NC09 and NC12 observed RED |
</threat_model>

<verification>
- New file: 9 RED on unmodified code (committed as RED, each failing for its declared reason), then 25/25 GREEN at the fix commit, with the test file unchanged in between.
- NC01 (the recorded direct Popen+wait4 fix) reproduced its declared set {A1, A2, A3, A4, A5×3, A6, A7, B7}, with MiB readings recorded. NC02-NC12 each reproduced their declared sets over the whole file; restores cmp-identical.
- Python 3.9 compile + 10-check smoke PASS (bias < 24, fork held/freed cases).
- `tests/m3` + `tests/phase2` reconciled by node id: +25 passed, 0 removed, 0 changed.
- `test_source_freeze_pins.py` GREEN before/after; kht default `RESULT GREEN` after; `--live` drift confined to run_native_ld_panel.py citations at line >= 184.
- `git diff --name-only 11f61e8..HEAD` == the two planned files; every frozen path zero-diff; AST proof shows only `_run_plink` and the new constant changed; every old-side hunk lies within basis lines 183-202.
- The SUMMARY cites Carter's decision verbatim and maps each promise to its enforcers.
</verification>

<success_criteria>
- `peak_ram_gib` from `_run_plink` is plink's own peak plus the launcher's bounded bias (< 24 MiB pinned; ~11 MiB on 3.11 / ~4 MiB on 3.9 measured). It is independent of earlier calls and of the driver's memory history or resident size. This is proven by tests observed RED on the old code and on the recorded fix.
- The `_run_plink` contract with its caller is preserved and pinned:
  - signature and return types;
  - CalledProcessError with the original cmd, and negative signal codes;
  - exec-error identity with `subprocess.run`;
  - inherited stdio, fds and signal dispositions;
  - SIGINT kill-through;
  - SIGTERM parity, both driver-only and group/timeout.
  Deltas are confined to failure paths and listed in the SUMMARY.
- There is zero change outside basis lines 183-202 and zero change to frozen files or historical records.
- Two commits: `test(quick-260916-ocb): …` (RED) then `fix(quick-260916-ocb): …` (GREEN), both explicit-path, both ending with the Co-Authored-By line, no push.
</success_criteria>

<revision_log>
Revision 1 (2026-09-16). Carter's decision recorded; plan-checker round 1 adopted in full. Every changed number below was re-measured by the planner with a full prototype (`$PROTO`, md5s in the objective).
- **DECISION.** `<decision_record>` added, plus frontmatter `decision:`. The SUMMARY must cite it: new §5 (a0).
- **BLOCKER (SIGTERM/timeout).**
  - B10 (driver-only SIGTERM) and B11 (`timeout` group SIGTERM) added, each with its negative control (NC07, NC08).
  - "Uncatchable" wording removed.
  - The must_haves truth, SUMMARY (i) and T-ocb-03 were rewritten to the measured semantics.
  - Both tests are GREEN on unmodified code.
- **W1.** Negative controls run the WHOLE file against a declared, planner-MEASURED failure set. All others must pass.
  - NC01's set is {A1, A2, A3, A4, A5×3, A6, A7, B7}. A6/A7 are new since the checker's list.
  - The 3.9 note is recorded: the recorded fix fails A3 but not A2 there.
- **W2.** `PRECONDITION:` / `READING <x> MiB` message conventions added. Task 1 Step 4 parses junit reasons and STOPs on any other failure reason. The planner measured every RED failing for its declared reason.
- **W3.** A6 (`_BIAS_CEIL_MIB = 24` on `true`), the 3.9 smoke bias check, and NC10 (32 MiB pad: A6 RED, A1 GREEN, measured).
- **W4.** B12 (child fd parity) + NC09. T-ocb-04 corrected: B8 pins driver fds only.
- **W5.** `exitcode_of` bound before the spawn; A7 + NC11; SUMMARY pre-fire item `python3 -V`.
  - **CORRECTION to the checker's literal A7 prelude.** `import os\ndel os.waitstatus_to_exitcode\n` makes `import subprocess` itself raise (3.11 subprocess.py:107; 3.9 subprocess.py:1842). The launcher then dies before the spawn under BOTH bindings, so the planner measured it GREEN on both and it cannot discriminate.
  - A7 therefore uses `import os, subprocess\ndel os.waitstatus_to_exitcode\n`. Measured: GREEN on the before-spawn binding, RED (child started) on the after-spawn binding.
- **I1.** Banner line has 4 spaces before `#`; measured length 79.
- **I2.** SIGINT handler conditional on a non-ignored inherited disposition.
  - **PLANNER ADDITION:** B13 (plink SigIgn mask equals `subprocess.run`'s with SIGINT+SIGHUP ignored) + NC12, so the I2 claim has a named enforcer.
  - Measured side finding: `close_fds=False` also changes the mask (posix_spawn path), so NC09 fails B12 AND B13.
- **I3.** All child pid/done files atomic (tmp + rename); pollers require non-empty content.
- **I4.** Hunk-range proof added (old-side hunks ⊆ basis 183-202); prototype hunks listed.
- **I5.** 3.9 smoke fork cases (held → launcher 7.00 MiB, direct 265.6 MiB; freed → direct 9.6 MiB).
- **I6, I7.** SUMMARY (i) items added (launcher-only kill → concurrent plinks; `pgrep -f`/`pkill -f` match the launcher, `pkill -f` → -9).
- **Out of scope.** The SIGHUP exposure of `nohup timeout 312h python3 …` is RECORDED in SUMMARY (l); `260812-ox1-*` added to files_frozen.
- **Counts.** 15→21 functions, 19→25 items, 7/12→9/16, reconciliation +19→+25, NC 6→12, commit messages updated.
- **Anchor hygiene.** NC03's anchor must be code-specific: the `"-I", "-S", "-c"` text also appears in the `#:` comment. The planner's exactly-once guard caught it.
</revision_log>

<output>
After completion, create `.planning/quick/260916-ocb-ram-1-per-child-peak-rss-for-run-plink-v/260916-ocb-SUMMARY.md` (Task 3 §5; do NOT commit it — the orchestrator commits PLAN/SUMMARY/STATE).
</output>

<orchestrator_addendum date="2026-09-16" source="plan-checker iteration 2 (VERIFICATION PASSED, 0 blockers / 0 warnings / 3 info) — all three info items ADOPTED under Carter's --auto --chain">
These are BINDING and take precedence over any conflicting text above. Record each in the SUMMARY with before/after.

A-1 (checker I-a — B7 robustness): the FIRST statement of B7's harness body must be
`signal.signal(signal.SIGINT, signal.default_int_handler)` (import signal as needed). Reason (measured by the checker):
`nohup pytest … &` launched from a non-interactive bash starts pytest with SIGINT IGNORED, and B7 then fails on CORRECT code
(1 failed, 61.29 s); with this line it passes (1 passed, 1.21 s). This line only restores the SIGINT disposition the declared
negative-control sets were measured under. Because it changes B7, RE-OBSERVE NC01, NC04 and NC08 with the line in place and
confirm their observed failure sets still EQUAL the declared sets ({A1,A2,A3,A4,A5×3,A6,A7,B7}; {B7}; {B4,B7,B11,B13}). If any
set changes, STOP and report — do not edit the declared set to match.

A-2 (checker I-b): citation START lines in the banked Stage C draft are 723–1325 (1328 is an end line). Every "723-1328"
above has been replaced with "723-1325" by the orchestrator (sed, all occurrences).

A-3 (checker I-c — A7 reason-check): A7's GREEN must also check WHY the launcher failed: capture fd-level stderr (pytest `capfd`)
and assert `"waitstatus_to_exitcode" in capfd.readouterr().err`, in addition to SubprocessError + no child pidfile. Observe it
GREEN on the fixed code and confirm NC11 is still RED for its declared reason.

Test counts are unchanged by A-1..A-3 (21 functions / 25 items; unmodified 9 failed / 16 passed; reconciliation +25).
</orchestrator_addendum>
