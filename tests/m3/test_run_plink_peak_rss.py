"""RAM-1 (quick-260916-ocb): ``run_native_ld_panel._run_plink`` must report the peak
resident memory of THE plink process it just ran — per child, not inherited.

THE DEFECT (3 sentences). ``_run_plink`` reported ``peak_ram_gib`` from
``resource.getrusage(RUSAGE_CHILDREN).ru_maxrss``, a high-water mark over every child
the driver ever waited for, so across a serial panel the column flat-lines at the
largest plink so far (``m2_region_00057`` inherited ``sub14``'s 26.5745 GiB). The
recorded clean fix — ``subprocess.Popen(cmd)`` + ``os.wait4`` straight from the
driver — is ALSO contaminated here, because at exec the child's ``ru_maxrss`` absorbs
the SPAWNING process's memory (CPython 3.11 vfork: the parent's lifetime high-water;
CPython 3.9 fork: the parent's current resident size). ``fire_verifier stage-b``'s
``check_peak_ram`` evaluates whatever series this seam produces, so the driver's own
``.bim`` scan / ``.ld.bin`` load / numpy+pandas footprint must never be charged to plink.

DECISION (Carter, 2026-09-16): "Small launcher process (Recommended)" — plink is spawned
by a small isolated interpreter (``-I -S``) that reaps it with ``os.wait4`` and reports
plink's own rusage over a pipe. Promises and their enforcers here: bias <= ~11 MiB
(3.11) / ~4 MiB (3.9) -> ``test_launcher_bias_is_bounded`` (< 24 MiB); error parity
with ``subprocess.run`` -> B3/B4/B5 + B12/B13; one added process per plink call;
SIGTERM/timeout no worse than today -> B10/B11/B7.

MEASURED PREMISES (NCSU login03, 2026-09-16; KiB unless stated)
| quantity                                                            | planner      | executor (Task 1 Step 2) |
|---------------------------------------------------------------------|--------------|--------------------------|
| bare ``python -c pass`` own maxrss (GNU time %M)                    | 8192         | 8192 (x3)                |
| 300 MiB touched child own maxrss (GNU time %M)                      | 315480       | 315352-315480 (x3)       |
| smoke_dev python after ``import run_native_ld_panel`` (VmHWM)       | 109504-111424| 109564-111592 (x3)       |
| direct ``Popen``+``wait4`` of ``python -c pass``, parent HOLDS mem  | 420776 (400 MiB held) | 273084-273336 (256 MiB held, parent VmRSS 273112-273224; x3) |
| launcher floor (``-I -S``), 3.11 / 3.9, parent holding 400 MiB      | 11264 / 4352 | (not re-measured here)   |
| unmodified ``_run_plink``: first tiny / 300 MiB / tiny after / tiny after parent alloc+free 256 MiB | 106.8 / 308.0 / 308.0 / 362.8 MiB | see Task 1 Step 4 RED readings |

THRESHOLDS (none is a timing threshold)
- ``_CEIL_MIB = 64``: 5.8x the launcher floor (11.0 MiB); 1.67x below the smallest
  contaminated reading ever measured (106.8 MiB = the importer's footprint alone);
  4.8x below the 300 MiB child.
- ``_BIAS_CEIL_MIB = 24``: 2.1x the worst measured 3.11 launcher bias (11.25 MiB) and
  4.5x below the importer footprint (106.8 MiB). A 32 MiB launcher pad (~43 MiB) crosses
  24 but stays under 64 (negative control NC10: A6 RED, A1 GREEN).
- ``_BIG_FLOOR_MIB = 250``: 58 MiB below the measured 308 MiB and 3.9x above the
  ceiling, so a "report ~0 for everything" failure is pinned too.
- ``_HOLD_MIB = 256``: harness peak ~107 + 256 = 363 MiB, child peak <= ~308 MiB,
  sequential — every process stays under 400 MiB.

TESTS and their expected outcome on the UNMODIFIED (pre-260916-ocb) ``_run_plink``
| id  | test                                                                   | unmodified | why |
|-----|------------------------------------------------------------------------|------------|-----|
| A1  | test_second_child_does_not_inherit_first_childs_peak                   | RED   | RUSAGE_CHILDREN high-water: tiny child after a 300 MiB child reads ~308 MiB |
| A2  | test_child_peak_excludes_driver_high_water_after_free                  | RED   | vfork folds the driver's lifetime high-water into the child (~363 MiB) |
| A3  | test_child_peak_excludes_driver_resident_memory_while_held             | RED   | the held 256 MiB is charged to the child (~365 MiB) |
| A4  | test_unwaited_grandchild_is_not_charged_to_child                       | RED   | the importer's high-water is charged (~365 MiB) |
| A5  | test_launcher_without_valid_report_fails_closed[x3]                    | RED   | AttributeError: no ``_PLINK_PEAK_RSS_LAUNCHER`` to monkeypatch |
| A6  | test_launcher_bias_is_bounded                                          | RED   | bare ``true`` reads the importer's high-water (~365 MiB) |
| A7  | test_launcher_fails_before_spawn_without_waitstatus_to_exitcode        | RED   | AttributeError: no ``_PLINK_PEAK_RSS_LAUNCHER`` |
| B1  | test_returns_two_finite_nonnegative_floats                             | GREEN | return-type contract preserved |
| B2  | test_waited_grandchild_is_charged_to_child                             | GREEN | a waited 300 MiB descendant counts under both designs |
| B3  | test_nonzero_exit_raises_calledprocesserror_with_original_cmd          | GREEN | ``check=True`` contract |
| B4  | test_signal_killed_child_raises_negative_returncode                    | GREEN | negative returncode contract |
| B5  | test_exec_failure_matches_subprocess_run_exactly[x3]                   | GREEN | today IS ``subprocess.run`` |
| B6  | test_stdout_and_stderr_pass_through_uncaptured_in_order                | GREEN | stdio inherited, nothing captured |
| B7  | test_interrupt_kills_child_and_propagates                              | GREEN | ``subprocess.run`` kills the child on KeyboardInterrupt |
| B8  | test_no_fd_zombie_or_resourcewarning_leak                              | GREEN | ``subprocess.run`` leaks nothing |
| B9  | test_launcher_ignores_cwd_module_shadowing                             | GREEN | nothing imports from the cwd today |
| B10 | test_driver_sigterm_leaves_plink_to_finish_and_nothing_hangs           | GREEN | driver-only SIGTERM leaves plink running today |
| B11 | test_timeout_group_sigterm_kills_plink                                 | GREEN | GNU timeout's group SIGTERM kills plink today |
| B12 | test_child_fds_match_subprocess_run                                    | GREEN | today IS ``subprocess.run`` (identity) |
| B13 | test_child_signal_dispositions_match_subprocess_run                    | GREEN | today IS ``subprocess.run`` (identity) |
| C1  | test_premise_direct_wait4_charges_parent_resident_memory_to_child      | GREEN | PREMISE MONITOR, does not call ``_run_plink`` |

Message conventions: every precondition assert message starts with ``PRECONDITION:``;
every RSS-reading assert message is ``READING <v> MiB >= <ceil> MiB (<label>)`` or
``READING <v> MiB < <floor> MiB (<label>)``. Child pid/done files are written
atomically (tmp + rename) and polled for non-empty content.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import signal
import subprocess
import sys
import textwrap
import time
import uuid
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import run_native_ld_panel as drv  # noqa: E402

_CEIL_MIB = 64.0
_BIAS_CEIL_MIB = 24.0
_BIG_FLOOR_MIB = 250.0
_HOLD_MIB = 256
_BIG_SRC = "b = bytearray(300 * 2**20)\nfor i in range(0, len(b), 4096):\n    b[i] = 1\n"
_TINY = [sys.executable, "-c", "pass"]
_ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

# Child snippet: write its own pid ATOMICALLY (tmp + rename) to sys.argv[1].
_CHILD_WRITE_PID = (
    "import os, sys\n"
    "_t = sys.argv[1] + '.tmp'\n"
    "with open(_t, 'w') as _f:\n"
    "    _f.write(str(os.getpid()))\n"
    "os.rename(_t, sys.argv[1])\n"
)
# ... then poll up to 120 s for the release file sys.argv[2] and exit 0.
_CHILD_WAIT_RELEASE = _CHILD_WRITE_PID + (
    "import time\n"
    "_deadline = time.monotonic() + 120\n"
    "while time.monotonic() < _deadline and not os.path.exists(sys.argv[2]):\n"
    "    time.sleep(0.05)\n"
)


def _mib(gib: float) -> float:
    """GiB (the seam's unit) -> MiB."""
    return gib * 1024.0


def _reading_lt(value_mib: float, ceil: float, label: str) -> None:
    assert value_mib < ceil, f"READING {value_mib:.2f} MiB >= {ceil} MiB ({label})"


def _reading_ge(value_mib: float, floor: float, label: str) -> None:
    assert value_mib >= floor, f"READING {value_mib:.2f} MiB < {floor} MiB ({label})"


# --------------------------------------------------------------------------- #
# Harness helpers: a fresh interpreter whose memory history the test controls  #
# --------------------------------------------------------------------------- #

_PREAMBLE = (
    "import gc, json, os, signal, subprocess, sys, time, warnings\n"
    "sys.path.insert(0, sys.argv[1])\n"
)
_STATUS_FN = (
    "def _status_kib():\n"
    "    out = {}\n"
    "    with open('/proc/self/status') as fh:\n"
    "        for line in fh:\n"
    "            key = line.split(':')[0]\n"
    "            if key in ('VmHWM', 'VmRSS'):\n"
    "                out[key] = int(line.split()[1])\n"
    "    return out\n"
)


def _harness_argv(body: str, *extra, import_driver: bool = True) -> list[str]:
    """argv for ``python -c <preamble + body> <src/python> *extra``."""
    src = _PREAMBLE
    if import_driver:
        src += "import run_native_ld_panel as drv\n"
    src += _STATUS_FN + textwrap.dedent(body)
    return [sys.executable, "-c", src, str(_SRC_PYTHON), *[str(e) for e in extra]]


def _run_harness_json(tmp_path: Path, body: str, *extra, import_driver: bool = True,
                      timeout: int = 180) -> dict:
    """Run a harness to completion; return json.loads of its LAST non-empty stdout line."""
    proc = subprocess.run(_harness_argv(body, *extra, import_driver=import_driver),
                          cwd=tmp_path, env=_ENV, capture_output=True, text=True,
                          timeout=timeout)
    assert proc.returncode == 0, (
        f"PRECONDITION: harness rc={proc.returncode}\nstderr:\n{proc.stderr}")
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert lines, f"PRECONDITION: harness printed nothing\nstderr:\n{proc.stderr}"
    return json.loads(lines[-1])


def _poll_pidfile(path: Path, proc=None, timeout: float = 60.0,
                  errpath: Path | None = None) -> int:
    """Wait for a NON-EMPTY pidfile; fail (PRECONDITION) if ``proc`` exits first."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            text = path.read_text().strip()
            if text:
                return int(text)
        if proc is not None and proc.poll() is not None:
            detail = ""
            if proc.stderr is not None:
                try:
                    detail = proc.communicate(timeout=10)[1]
                except subprocess.TimeoutExpired:
                    detail = "<stderr pipe still held open by a descendant>"
            elif errpath is not None and errpath.exists():
                detail = errpath.read_text()
            pytest.fail(f"PRECONDITION: process exited rc={proc.returncode} before the "
                        f"child wrote {path.name}\nstderr:\n{detail}")
        time.sleep(0.05)
    pytest.fail(f"PRECONDITION: {path.name} never appeared within {timeout} s")


def _stat_fields(pid: int) -> list[str] | None:
    """/proc/<pid>/stat fields AFTER the last ')' -> [state, ppid, ...]; None if gone."""
    try:
        with open(f"/proc/{pid}/stat") as fh:
            data = fh.read()
    except (FileNotFoundError, ProcessLookupError):
        return None
    return data.rsplit(")", 1)[1].split()


def _gone(pid: int, timeout: float, zombie_counts: bool) -> bool:
    """True once ``pid`` has vanished (or, if ``zombie_counts``, is a zombie)."""
    deadline = time.monotonic() + timeout
    while True:
        f = _stat_fields(pid)
        if f is None or (zombie_counts and f[0] in ("Z", "X")):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def _sigkill_quietly(pid: int) -> None:
    """SIGKILL ``pid`` if it is still a running (non-zombie) process."""
    f = _stat_fields(pid)
    if f is not None and f[0] not in ("Z", "X"):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


# =========================================================================== #
# A — RED on the unmodified code: the per-child peak-RSS property              #
# =========================================================================== #

def test_second_child_does_not_inherit_first_childs_peak():
    """A1: in ONE process, a tiny child after a 300 MiB child reads < 64 MiB."""
    _, big = drv._run_plink([sys.executable, "-c", _BIG_SRC])
    _reading_ge(_mib(big), _BIG_FLOOR_MIB, "300 MiB child")
    _, tiny = drv._run_plink(_TINY)
    _reading_lt(_mib(tiny), _CEIL_MIB, "tiny child after a 300 MiB child")


def test_child_peak_excludes_driver_high_water_after_free(tmp_path):
    """A2: a driver that touched and FREED 256 MiB is not charged to plink."""
    body = """
    hold = int(sys.argv[2])
    x = bytearray(hold * 2**20)
    for i in range(0, len(x), 4096):
        x[i] = 1
    del x
    gc.collect()
    pre = _status_kib()
    _, peak = drv._run_plink([sys.executable, "-c", "pass"])
    print(json.dumps({"pre": pre, "peak_mib": peak * 1024.0}))
    """
    out = _run_harness_json(tmp_path, body, _HOLD_MIB)
    assert out["pre"]["VmHWM"] >= 250 * 1024, f"PRECONDITION: VmHWM too low {out['pre']}"
    assert out["pre"]["VmRSS"] < 200 * 1024, f"PRECONDITION: VmRSS not freed {out['pre']}"
    _reading_lt(out["peak_mib"], _CEIL_MIB, "tiny child after the driver freed 256 MiB")


def test_child_peak_excludes_driver_resident_memory_while_held(tmp_path):
    """A3: a driver HOLDING 256 MiB resident is not charged to plink."""
    body = """
    hold = int(sys.argv[2])
    x = bytearray(hold * 2**20)
    for i in range(0, len(x), 4096):
        x[i] = 1
    pre = _status_kib()
    _, peak = drv._run_plink([sys.executable, "-c", "pass"])
    del x
    print(json.dumps({"pre": pre, "peak_mib": peak * 1024.0}))
    """
    out = _run_harness_json(tmp_path, body, _HOLD_MIB)
    assert out["pre"]["VmRSS"] >= 250 * 1024, f"PRECONDITION: VmRSS not held {out['pre']}"
    _reading_lt(out["peak_mib"], _CEIL_MIB, "tiny child while the driver holds 256 MiB")


def test_unwaited_grandchild_is_not_charged_to_child(tmp_path):
    """A4: a 300 MiB grandchild the child did NOT wait for is not plink's memory."""
    pidfile = tmp_path / "grand.pid"
    donefile = tmp_path / "grand.done"
    grand_src = _CHILD_WRITE_PID + _BIG_SRC + (
        "_t = sys.argv[2] + '.tmp'\n"
        "with open(_t, 'w') as _f:\n"
        "    _f.write('done')\n"
        "os.rename(_t, sys.argv[2])\n"
    )
    child_src = ("import subprocess, sys\n"
                 "subprocess.Popen([sys.executable, '-c', sys.argv[1], sys.argv[2], "
                 "sys.argv[3]])\n")
    _, peak = drv._run_plink([sys.executable, "-c", child_src, grand_src,
                              str(pidfile), str(donefile)])
    gpid = None
    try:
        gpid = _poll_pidfile(pidfile)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if donefile.exists() and donefile.read_text().strip():
                break
            time.sleep(0.05)
        assert donefile.exists() and donefile.read_text().strip(), (
            "PRECONDITION: the 300 MiB grandchild did not finish within 60 s")
        _reading_lt(_mib(peak), _CEIL_MIB, "child whose 300 MiB grandchild was not waited")
    finally:
        if gpid is not None and not _gone(gpid, 60, zombie_counts=True):
            _sigkill_quietly(gpid)


_BAD_LAUNCHERS = {
    "no_report": "raise SystemExit(7)\n",
    "garbage_report": "import os, sys\nos.write(int(sys.argv[1]), b'not json\\n')\n",
    "report_then_nonzero_exit": (
        "import os, sys\nos.write(int(sys.argv[1]), b'[\"R\", 0, 1024]\\n')\n"
        "raise SystemExit(5)\n"),
}


@pytest.mark.parametrize("case", sorted(_BAD_LAUNCHERS))
def test_launcher_without_valid_report_fails_closed(case, monkeypatch):
    """A5: no numbers without a valid report — exactly subprocess.SubprocessError.

    A NaN would PASS ``fire_verifier.check_peak_ram`` open, so the seam must raise.
    """
    monkeypatch.setattr(drv, "_PLINK_PEAK_RSS_LAUNCHER", _BAD_LAUNCHERS[case])
    with pytest.raises(subprocess.SubprocessError) as ei:
        drv._run_plink(_TINY)
    assert type(ei.value) is subprocess.SubprocessError, repr(ei.value)


def test_launcher_bias_is_bounded():
    """A6: bare ``true`` reads < 24 MiB — the launcher's own bias is pinned."""
    true_bin = shutil.which("true")
    if true_bin is None:
        pytest.fail("PRECONDITION: no `true` on PATH (this test must never skip)")
    _, peak = drv._run_plink([true_bin])
    _reading_lt(_mib(peak), _BIAS_CEIL_MIB, "bare `true` = the launcher's own bias")


def test_launcher_fails_before_spawn_without_waitstatus_to_exitcode(tmp_path, monkeypatch,
                                                                     capfd):
    """A7: an interpreter lacking os.waitstatus_to_exitcode fails BEFORE plink starts.

    ``subprocess`` is imported FIRST: ``import subprocess`` itself reads the helper, so
    deleting it before that import would kill every launcher version and discriminate
    nothing. The launcher's stderr must name the missing helper (the WHY).
    """
    pidfile = tmp_path / "a7.pid"
    src = ("import os, subprocess\ndel os.waitstatus_to_exitcode\n"
           + drv._PLINK_PEAK_RSS_LAUNCHER)
    monkeypatch.setattr(drv, "_PLINK_PEAK_RSS_LAUNCHER", src)
    with pytest.raises(subprocess.SubprocessError) as ei:
        drv._run_plink([sys.executable, "-c", _CHILD_WRITE_PID, str(pidfile)])
    assert type(ei.value) is subprocess.SubprocessError, repr(ei.value)
    assert not pidfile.exists(), (
        "CHILD-STARTED: plink ran before the missing os.waitstatus_to_exitcode "
        "was detected")
    err = capfd.readouterr().err
    assert "waitstatus_to_exitcode" in err, (
        f"LAUNCHER-REASON: the launcher failed for another reason\nstderr:\n{err}")


# =========================================================================== #
# B — GREEN on the unmodified code: the contract that must be PRESERVED        #
# =========================================================================== #

def test_returns_two_finite_nonnegative_floats():
    """B1: (wall_min, peak_ram_gib), both finite non-negative floats."""
    out = drv._run_plink(_TINY)
    assert type(out) is tuple and len(out) == 2, repr(out)
    for v in out:
        assert type(v) is float and math.isfinite(v) and v >= 0.0, repr(out)


def test_waited_grandchild_is_charged_to_child():
    """B2: a 300 MiB grandchild the child WAITED for counts as the child's peak."""
    child_src = ("import subprocess, sys\n"
                 "subprocess.run([sys.executable, '-c', sys.argv[1]], check=True)\n")
    _, peak = drv._run_plink([sys.executable, "-c", child_src, _BIG_SRC])
    _reading_ge(_mib(peak), _BIG_FLOOR_MIB, "child that waited for a 300 MiB grandchild")


def test_nonzero_exit_raises_calledprocesserror_with_original_cmd():
    """B3: CalledProcessError(returncode, ORIGINAL cmd), nothing captured."""
    cmd = [sys.executable, "-c", "raise SystemExit(3)"]
    with pytest.raises(subprocess.CalledProcessError) as ei:
        drv._run_plink(cmd)
    e = ei.value
    assert type(e) is subprocess.CalledProcessError
    assert e.returncode == 3
    assert e.cmd == cmd
    assert e.output is None and e.stderr is None


def test_signal_killed_child_raises_negative_returncode():
    """B4: a SIGTERM-killed child -> returncode -15."""
    cmd = [sys.executable, "-c", "import os, signal; os.kill(os.getpid(), signal.SIGTERM)"]
    with pytest.raises(subprocess.CalledProcessError) as ei:
        drv._run_plink(cmd)
    assert ei.value.returncode == -signal.SIGTERM


def _exec_fail_cmd(case: str, tmp_path: Path) -> list[str]:
    if case == "missing_on_path":
        return ["plink1.9-ocb-missing-" + uuid.uuid4().hex, "--version"]
    if case == "missing_abs_path":
        return [str(tmp_path / "nope" / "plink1.9")]
    f = tmp_path / "not_executable"
    f.write_text("#!/bin/sh\n")
    f.chmod(0o644)
    return [str(f)]


@pytest.mark.parametrize("case", ["missing_abs_path", "missing_on_path", "not_executable"])
def test_exec_failure_matches_subprocess_run_exactly(case, tmp_path):
    """B5: failure to exec plink raises what subprocess.run(cmd, check=True) raised."""
    cmd = _exec_fail_cmd(case, tmp_path)
    with pytest.raises(OSError) as ref_i:
        subprocess.run(cmd, check=True)
    with pytest.raises(OSError) as got_i:
        drv._run_plink(cmd)
    ref, got = ref_i.value, got_i.value
    assert type(got) is type(ref)
    assert got.args == ref.args
    assert got.errno == ref.errno
    assert got.strerror == ref.strerror
    assert got.filename == ref.filename
    assert got.filename2 == ref.filename2
    assert str(got) == str(ref)


def test_stdout_and_stderr_pass_through_uncaptured_in_order(tmp_path):
    """B6: plink's stdout/stderr are inherited, uncaptured, and interleave in order."""
    body = """
    print("H-BEFORE", flush=True)
    drv._run_plink([sys.executable, "-c",
                    "import sys; print('CHILD-OUT', flush=True); "
                    "print('CHILD-ERR', file=sys.stderr, flush=True)"])
    print("H-AFTER", flush=True)
    """
    out_p, err_p = tmp_path / "h.out", tmp_path / "h.err"
    with open(out_p, "wb") as o, open(err_p, "wb") as e:
        rc = subprocess.run(_harness_argv(body), cwd=tmp_path, env=_ENV, stdout=o,
                            stderr=e, timeout=180).returncode
    err = err_p.read_text()
    assert rc == 0, err
    assert out_p.read_text().splitlines() == ["H-BEFORE", "CHILD-OUT", "H-AFTER"]
    assert "CHILD-ERR" in err.splitlines()
    assert "Traceback" not in err


def test_interrupt_kills_child_and_propagates(tmp_path):
    """B7: SIGINT to the driver kills plink and KeyboardInterrupt propagates.

    The harness body FIRST restores Python's SIGINT handler: a pytest started from a
    non-interactive shell's background job inherits SIGINT ignored, which would make
    this test fail on CORRECT code (orchestrator addendum A-1, measured by the checker).
    """
    pidfile = tmp_path / "b7.pid"
    child_src = _CHILD_WRITE_PID + "import time\ntime.sleep(120)\n"
    body = """
    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        drv._run_plink([sys.executable, "-c", sys.argv[2], sys.argv[3]])
        print(json.dumps({"outcome": "returned"}), flush=True)
    except KeyboardInterrupt:
        print(json.dumps({"outcome": "KeyboardInterrupt"}), flush=True)
    """
    harness = subprocess.Popen(_harness_argv(body, child_src, pidfile), cwd=tmp_path,
                               env=_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
    cpid = None
    try:
        cpid = _poll_pidfile(pidfile, harness)
        os.kill(harness.pid, signal.SIGINT)
        out, err = harness.communicate(timeout=60)
        assert harness.returncode == 0, err
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert lines and json.loads(lines[-1])["outcome"] == "KeyboardInterrupt", (out, err)
        assert _gone(cpid, 30, zombie_counts=False), (
            f"child {cpid} still present (or an unreaped zombie) 30 s after SIGINT")
    finally:
        if cpid is not None:
            _sigkill_quietly(cpid)
        if harness.poll() is None:
            harness.kill()
        harness.communicate()


def test_no_fd_zombie_or_resourcewarning_leak(tmp_path):
    """B8: the DRIVER leaks no fd, no zombie, no ResourceWarning (B12 pins the child)."""
    body = """
    n0 = len(os.listdir("/proc/self/fd"))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        drv._run_plink([sys.executable, "-c", "pass"])
        gc.collect()
    n1 = len(os.listdir("/proc/self/fd"))
    try:
        os.waitpid(-1, os.WNOHANG)
        no_children = False
    except ChildProcessError:
        no_children = True
    rw = [str(x.message) for x in w if issubclass(x.category, ResourceWarning)]
    print(json.dumps({"n0": n0, "n1": n1, "no_children": no_children, "rw": rw}))
    """
    out = _run_harness_json(tmp_path, body)
    assert out["n0"] == out["n1"], out
    assert out["no_children"] is True, out
    assert out["rw"] == [], out


def test_launcher_ignores_cwd_module_shadowing(tmp_path, monkeypatch):
    """B9: stdlib-shadowing json.py/signal.py/subprocess.py in the cwd break nothing.

    No peak bound here on purpose: the unmodified code would be RED for the wrong reason.
    """
    for name in ("json", "signal", "subprocess"):
        (tmp_path / f"{name}.py").write_text("raise SystemExit(99)\n")
    monkeypatch.chdir(tmp_path)
    out = drv._run_plink(_TINY)
    assert type(out) is tuple and len(out) == 2, repr(out)
    assert all(type(v) is float for v in out), repr(out)


def test_driver_sigterm_leaves_plink_to_finish_and_nothing_hangs(tmp_path):
    """B10: SIGTERM to the driver ALONE (``kill <pid>``, ``timeout --foreground``).

    Today the driver dies -15 while plink runs on to completion. With the launcher the
    same holds, and the launcher then exits without a traceback; nothing hangs.
    """
    pidfile, release = tmp_path / "b10.pid", tmp_path / "b10.release"
    errp = tmp_path / "b10.err"
    body = """
    drv._run_plink([sys.executable, "-c", sys.argv[2], sys.argv[3], sys.argv[4]])
    print("RETURNED", flush=True)
    """
    with open(errp, "wb") as e:
        harness = subprocess.Popen(
            _harness_argv(body, _CHILD_WAIT_RELEASE, pidfile, release), cwd=tmp_path,
            env=_ENV, stdout=subprocess.DEVNULL, stderr=e, start_new_session=True)
    watch: list[int] = []
    try:
        cpid = _poll_pidfile(pidfile, harness, errpath=errp)
        watch.append(cpid)
        f = _stat_fields(cpid)
        assert f is not None, "PRECONDITION: child vanished before SIGTERM"
        ppid = int(f[1])
        if ppid != harness.pid:
            watch.append(ppid)  # the launcher
        os.kill(harness.pid, signal.SIGTERM)
        assert harness.wait(timeout=30) == -signal.SIGTERM
        release.write_text("go")
        for pid in watch:
            assert _gone(pid, 30, zombie_counts=True), (
                f"pid {pid} still running 30 s after the release file")
        err = errp.read_text()
        assert "Traceback" not in err, err
    finally:
        release.write_text("go")
        for pid in watch:
            _sigkill_quietly(pid)
        if harness.poll() is None:
            harness.kill()
            harness.wait()


def test_timeout_group_sigterm_kills_plink(tmp_path):
    """B11: GNU ``timeout`` (no --foreground) SIGTERMs its whole group: plink is KILLED."""
    timeout_bin = shutil.which("timeout")
    if timeout_bin is None:
        pytest.fail("PRECONDITION: GNU timeout not on PATH (this test must never skip)")
    pidfile, release = tmp_path / "b11.pid", tmp_path / "b11.release"
    errp = tmp_path / "b11.err"
    body = """
    drv._run_plink([sys.executable, "-c", sys.argv[2], sys.argv[3], sys.argv[4]])
    print("RETURNED", flush=True)
    """
    argv = [timeout_bin, "600",
            *_harness_argv(body, _CHILD_WAIT_RELEASE, pidfile, release)]
    with open(errp, "wb") as e:
        proc = subprocess.Popen(argv, cwd=tmp_path, env=_ENV, stdout=subprocess.DEVNULL,
                                stderr=e, start_new_session=True)
    watch: list[int] = []
    try:
        cpid = _poll_pidfile(pidfile, proc, errpath=errp)
        watch.append(cpid)
        f = _stat_fields(cpid)
        assert f is not None, "PRECONDITION: child vanished before SIGTERM"
        watch.append(int(f[1]))  # the launcher (or the harness on the unmodified code)
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait(timeout=30)
        for pid in watch:
            assert _gone(pid, 30, zombie_counts=True), (
                f"pid {pid} survived timeout's group SIGTERM")
        err = errp.read_text()
        assert "Traceback" not in err, err
    finally:
        release.write_text("go")
        for pid in watch:
            _sigkill_quietly(pid)
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def test_child_fds_match_subprocess_run(tmp_path):
    """B12: plink's inherited fd set equals subprocess.run's (no report-fd leak)."""
    body = """
    child = ("import os, sys\\n"
             "fds = sorted(os.listdir('/proc/self/fd'), key=int)\\n"
             "open(sys.argv[1], 'w').write(' '.join(fds))\\n")
    subprocess.run([sys.executable, "-c", child, sys.argv[2]], check=True)
    drv._run_plink([sys.executable, "-c", child, sys.argv[3]])
    print(json.dumps({"run": open(sys.argv[2]).read(), "plink": open(sys.argv[3]).read()}))
    """
    out = _run_harness_json(tmp_path, body, tmp_path / "run.fds", tmp_path / "plink.fds")
    assert out["plink"] == out["run"], out


def test_child_signal_dispositions_match_subprocess_run(tmp_path):
    """B13: plink's ignored-signal mask equals subprocess.run's, SIGINT+SIGHUP ignored.

    Pins restore_signals parity and the SIG_IGN-inherited-SIGINT case (a driver started
    as a background job of a non-interactive shell must hand plink an ignored SIGINT).
    """
    sh = shutil.which("sh")
    if sh is None:
        pytest.fail("PRECONDITION: no sh on PATH (this test must never skip)")
    body = """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    sh = sys.argv[2]
    probe = 'exec grep "^SigIgn" /proc/self/status > "$1"'
    subprocess.run([sh, "-c", probe, "sh", sys.argv[3]], check=True)
    drv._run_plink([sh, "-c", probe, "sh", sys.argv[4]])
    print(json.dumps({"run": open(sys.argv[3]).read(), "plink": open(sys.argv[4]).read()}))
    """
    out = _run_harness_json(tmp_path, body, sh, tmp_path / "run.sig", tmp_path / "plink.sig")
    mask = int(out["run"].split()[1], 16)
    assert mask & (1 << (signal.SIGINT - 1)), f"PRECONDITION: SIGINT not ignored in ref {out}"
    assert mask & (1 << (signal.SIGHUP - 1)), f"PRECONDITION: SIGHUP not ignored in ref {out}"
    assert out["plink"] == out["run"], out


# =========================================================================== #
# C — PREMISE MONITOR                                                          #
# =========================================================================== #

def test_premise_direct_wait4_charges_parent_resident_memory_to_child(tmp_path):
    """C1: PREMISE MONITOR for the launcher design. Does NOT call ``_run_plink``.

    A parent HOLDING 256 MiB spawns ``python -c pass`` with a direct Popen + os.wait4;
    the child's ru_maxrss must absorb the parent's memory (>= 250 MiB). If this goes RED,
    the kernel/CPython stopped charging the spawner's memory at exec, and the rationale
    for ``_run_plink``'s launcher must be re-evaluated.
    """
    body = """
    hold = int(sys.argv[2])
    x = bytearray(hold * 2**20)
    for i in range(0, len(x), 4096):
        x[i] = 1
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    _, st, ru = os.wait4(p.pid, 0)
    p.returncode = os.waitstatus_to_exitcode(st)
    del x
    print(json.dumps({"direct_kib": ru.ru_maxrss}))
    """
    out = _run_harness_json(tmp_path, body, _HOLD_MIB, import_driver=False)
    assert out["direct_kib"] >= 250 * 1024, (
        f"READING {out['direct_kib'] / 1024.0:.2f} MiB < 250 MiB (PREMISE GONE: a direct "
        f"wait4 no longer charges the parent's memory -- re-evaluate the launcher)")
