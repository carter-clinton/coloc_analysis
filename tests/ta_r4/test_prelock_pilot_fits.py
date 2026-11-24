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


#: Approved F15 wording (Carter, Q-F15V3); v1 and v2 are superseded and must not appear in the DRAFT.
APPROVED = "W3f-carter-15-7-Q-F15-wording-as-approved-v3-2026-11-24.txt"
SUPERSEDED = ("W3f-carter-15-7-Q-F15-wording-as-approved-2026-11-20.txt",
              "W3f-carter-15-7-Q-F15-wording-as-approved-v2-2026-11-20.txt")
DRAFT = REPO_ROOT / ".planning/amendments/osf-amendment-r4-DRAFT.md"


def _unwrap(name):
    return (MAN_DIR.parent / name).read_text().rstrip("\n").replace("\n", " ")


def test_draft_paragraph_equals_the_approved_file_unwrapped():
    text = DRAFT.read_text()
    para = _unwrap(APPROVED)
    h = [ln for ln in text.split("\n") if ln.startswith("(h) **Known-answer results (before the lock).**")]
    assert len(h) == 1 and h[0].endswith(" " + para)
    assert text.count("**Pre-lock pilot fits.**") == 1
    for old in SUPERSEDED:
        assert _unwrap(old) not in text, f"superseded wording present: {old}"
    assert "before any production-arm fit exists" in text and "before any production fit exists" not in text
