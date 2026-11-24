"""15.7i (F15): every pre-lock pilot fit on disk is listed, with sha256, in manifests/prelock_pilot_fits.tsv."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

from .conftest import MAN_DIR, REPO_ROOT

MANIFEST = MAN_DIR / "prelock_pilot_fits.tsv"
#: The two pilot-fit trees (data/r4 is a symlink into /rs1; rglob below follows the directories explicitly).
PILOT_TREES = ("data/r4/measure_asthma_fix/fits", "data/r4/measure_asthma_fix/bmi_determinism/fits")
COLUMNS = ("path", "kind", "sha256", "set", "trait", "ancestry", "region", "status", "convergence_status",
           "n_cs_purity_filtered", "cs_sizes", "used_for")


def _disk_files():
    out = set()
    for t in PILOT_TREES:
        root = REPO_ROOT / t
        assert root.is_dir(), f"pilot tree missing: {t}"
        for p in root.rglob("*"):
            if p.is_file() and p.name.endswith((".json", ".rds")):
                out.add(str(p.relative_to(REPO_ROOT)))
    return out


def _rows():
    assert MANIFEST.is_file(), f"missing {MANIFEST.relative_to(REPO_ROOT)}"
    with open(MANIFEST, newline="") as fh:
        rd = csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t")
        assert tuple(rd.fieldnames) == COLUMNS
        return list(rd)


@pytest.mark.r4_heavy
def test_manifest_lists_every_pilot_fit_on_disk():
    rows = _rows()
    listed = [r["path"] for r in rows]
    assert len(listed) == len(set(listed)), "duplicate manifest rows"
    disk = _disk_files()
    unlisted = sorted(disk - set(listed))
    missing = sorted(set(listed) - disk)
    assert not unlisted, f"pilot fits on disk but not in the manifest: {unlisted[:5]} ({len(unlisted)})"
    assert not missing, f"manifest rows with no file on disk: {missing[:5]} ({len(missing)})"


@pytest.mark.r4_heavy
def test_manifest_sha256_match():
    bad = []
    for r in _rows():
        h = hashlib.sha256(Path(REPO_ROOT / r["path"]).read_bytes()).hexdigest()
        if h != r["sha256"]:
            bad.append(r["path"])
    assert not bad, f"sha256 mismatch: {bad[:5]} ({len(bad)})"
