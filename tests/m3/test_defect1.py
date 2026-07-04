"""Defect 1 (quick 260703-vk9) — snplist-read race guard + skip-when-no-drop.

Root cause (Seth, offline-verified): the live region-1 failure
(``.ld.bin implies 102421 but the window .bim has 0 rows``) was a RACE, not a
logic bug. ``_retained_window_bim`` read ``{out_prefix}.snplist`` with a bare
``read_text()`` and NO retry-on-zero guard (unlike the sibling raw-window .bim
read), racing plink's flush -> an empty snplist -> 0 retained ids -> a false
n_var mismatch. Fix = (A) a pure decision helper ``_needs_retained_subset`` so the
square path SKIPS the intersection when --mac dropped nothing (bin == raw, the
observed AFR regime — the race cannot occur there), and (B) an ``expect_nonzero``
bounded retry on the snplist read for the real-drop path, mirroring
``_window_bim_n_var_retry_on_zero``. A persistently-empty snplist still returns 0
so the caller's byte-identical n_var mismatch still fires (no semantics loosened).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC_PYTHON = Path(__file__).resolve().parents[2] / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import run_native_ld_panel as drv  # noqa: E402


# --------------------------------------------------------------------------- #
# Change A — the pure decision helper                                         #
# --------------------------------------------------------------------------- #

def test_needs_retained_subset_decision():
    """Intersection is needed ONLY when --mac actually dropped variants
    (bin_n_var != raw_window_n_var). Equal counts (observed AFR regime) -> skip."""
    # No drop -> no intersection (skip the snplist read / the race).
    assert drv._needs_retained_subset(102421, 102421) is False
    # A real MAC=0 drop -> must intersect to align n_var to the retained set.
    assert drv._needs_retained_subset(102410, 102421) is True
    # A degenerate mismatch (e.g. transient 0) is still "not equal" -> intersect,
    # and the caller's downstream n_var check still fires.
    assert drv._needs_retained_subset(0, 102421) is True


# --------------------------------------------------------------------------- #
# Change B — the snplist read is race-guarded when a drop is expected         #
# --------------------------------------------------------------------------- #

def _write_raw_window_bim(path: Path, ids: list[str]) -> None:
    path.write_text(
        "\n".join(f"1\t{v}\t0\t{100 + i}\tA\tG" for i, v in enumerate(ids)) + "\n"
    )


def test_snplist_empty_recovers_on_retry(tmp_path, monkeypatch):
    """A transient EMPTY snplist read self-heals in-run when expect_nonzero=True:
    the bounded retry re-reads the (now-flushed) snplist and returns the real count."""
    ids = ["v1", "v2", "v3"]
    raw_bim = tmp_path / "region.window.bim"
    _write_raw_window_bim(raw_bim, ids)
    snplist = tmp_path / "region.snplist"
    snplist.write_text("\n".join(ids) + "\n")  # real content on disk

    real_read_text = Path.read_text
    state = {"snplist_reads": 0}

    def flaky_read_text(self, *args, **kwargs):
        # Only the snplist's FIRST read returns the un-flushed empty string;
        # every other read (incl. the raw window .bim) passes through.
        if self.name == snplist.name:
            state["snplist_reads"] += 1
            if state["snplist_reads"] == 1:
                return ""
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", flaky_read_text)
    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)  # no real wait

    n_var, retained_bim = drv._retained_window_bim(
        raw_bim, snplist, region_id="test_region", expect_nonzero=True
    )

    assert n_var == 3                       # recovered the real retained count
    assert state["snplist_reads"] >= 2      # it actually retried
    assert Path(retained_bim).exists()


def test_snplist_persistently_empty_returns_zero(tmp_path, monkeypatch):
    """A GENUINELY empty snplist still returns 0 after the bounded retries, so the
    caller's byte-identical n_var mismatch ValueError still fires (no loosening)."""
    raw_bim = tmp_path / "region.window.bim"
    _write_raw_window_bim(raw_bim, ["v1", "v2", "v3"])
    snplist = tmp_path / "region.snplist"
    snplist.write_text("")  # persistently empty

    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)  # skip the waits

    n_var, retained_bim = drv._retained_window_bim(
        raw_bim, snplist, region_id="test_region", expect_nonzero=True
    )

    assert n_var == 0
