"""GWAS-null windows drawn from the pool the production inputs define (W3f 15.7h, review F9; DEC-2026-11-20-ta-r4-null-window-reselection)."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import MAN_DIR, REPO_ROOT

from ta_r4 import ukb337k_tiles as ukb

SCRIPT = REPO_ROOT / "src/python/ta_r4/select_null_windows.py"
SELECTION = MAN_DIR / "null_windows_selection.tsv"
SUPERSEDED = MAN_DIR / "null_windows_selection.superseded-2026-10-21.tsv"
SUMSTATS_MANIFEST = MAN_DIR / "sumstats_r4_sha256.tsv"
H = "data/processed/sumstats_harmonized"
SUPERSEDED_INPUTS = [f"{H}/{t}.EUR.tsv.bgz" for t in ("asthma", "bmi", "hypertension", "stroke", "t2d")] + [
    f"{H}/{t}.AFR.tsv.bgz" for t in ("asthma", "stroke", "t2d")]
PRODUCTION_INPUTS = [
    "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz", "data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz",
    f"{H}/hypertension.EUR.tsv.bgz", f"{H}/stroke.EUR.tsv.bgz", f"{H}/t2d.EUR.tsv.bgz",
    "data/r4/sumstats/asthma.AFR.grch37_lifted_strand.tsv.bgz", f"{H}/stroke.AFR.tsv.bgz", f"{H}/t2d.AFR.tsv.bgz"]
SUPERSEDED_SHA256 = "f0df241aaae8054f08da583d7b538ab0f3a5a92d2e62eec4f89ed622d4dd6227"
SUPERSEDED_CANDIDATES_SHA256 = "352c77ecca5061f0e86d5c8ea48f9c388818a8a0b5a335d06cbfab16d12dcce9"
SUPERSEDED_WINDOWS = [(1, 99500001), (1, 218750001), (2, 190000001), (3, 30750001), (3, 178250001),
                      (6, 81500001), (11, 21500001), (13, 38500001), (13, 71000001), (14, 49000001)]
PRODUCTION_WINDOWS = [(1, 99750001), (1, 232000001), (2, 202500001), (3, 34000001), (3, 191500001),
                      (6, 82750001), (11, 21500001), (13, 42000001), (13, 71000001), (14, 49250001)]


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _rows(p):
    with open(p) as fh:
        return list(csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t"))


def _windows(p):
    return [(int(r["chr"]), int(r["start"])) for r in _rows(p)]


def _comment(p, key):
    return [l.split("\t", 1)[1] for l in Path(p).read_text().splitlines() if l.startswith(f"# {key}\t")]


def _select(inputs, tmp_path):
    cand, sel = tmp_path / "cand.tsv", tmp_path / "sel.tsv"
    r = subprocess.run([sys.executable, str(SCRIPT), "--sumstats", *(str(REPO_ROOT / p) for p in inputs),
                        "--sha256-manifest", str(SUMSTATS_MANIFEST),
                        "--regions-curated", str(REPO_ROOT / "config/regions_curated.csv"),
                        "--negative-controls", str(REPO_ROOT / "config/negative_controls.yaml"),
                        "--candidates-out", str(cand), "--selected-out", str(sel)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return cand, sel


@pytest.mark.r4_heavy
def test_driver_reproduces_the_superseded_selection(tmp_path):
    """The driver, on the superseded inputs checked by `path`, writes the superseded selection byte for byte."""
    cand, sel = _select(SUPERSEDED_INPUTS, tmp_path)
    assert _sha(cand) == SUPERSEDED_CANDIDATES_SHA256
    assert sel.read_bytes() == SUPERSEDED.read_bytes()


@pytest.mark.r4_heavy
def test_selection_reproduces_from_the_production_inputs(tmp_path):
    cand, sel = _select(PRODUCTION_INPUTS, tmp_path)
    assert sel.read_bytes() == SELECTION.read_bytes()
    assert _comment(SELECTION, "candidates_sha256") == [_sha(cand)]
    assert _comment(SELECTION, "n_candidates") == ["2886"]
    assert _windows(SELECTION) == PRODUCTION_WINDOWS
    with open(SUMSTATS_MANIFEST, newline="") as fh:
        pinned = {Path(r["path"]).name: r["sha256"] for r in csv.DictReader(fh, delimiter="\t")
                  if r["path"] in PRODUCTION_INPUTS}
    assert len(pinned) == 8
    assert sorted(_comment(SELECTION, "input_sha256")) == sorted(f"{n}\t{s}" for n, s in pinned.items())


def test_superseded_selection_is_kept():
    assert _sha(SUPERSEDED) == SUPERSEDED_SHA256
    assert _comment(SUPERSEDED, "n_candidates") == ["2865"]
    assert _comment(SUPERSEDED, "candidates_sha256") == [SUPERSEDED_CANDIDATES_SHA256]
    assert _windows(SUPERSEDED) == SUPERSEDED_WINDOWS
    assert _comment(SUPERSEDED, "rule") == _comment(SELECTION, "rule")
    assert SELECTION.read_bytes() != SUPERSEDED.read_bytes()


def test_new_window_tiles_do_not_depend_on_what_is_on_disk():
    """For every NC_NULL window, the builder's manifest-filtered tile choice equals the unfiltered covering set."""
    man, root = REPO_ROOT / ukb.TILE_MANIFEST, REPO_ROOT / ukb.DOWNLOAD_DIR
    rows = _rows(SELECTION)
    assert [r["region_id"] for r in rows] == [f"NC_NULL_{i:02d}" for i in range(1, 11)]
    for r in rows:
        c, s, e = r["chr"], int(r["start"]), int(r["end"])
        want = [ukb.tile_paths(n, root) for n in ukb.covering_tiles(c, s, e)]
        assert want, r["region_id"]
        assert ukb.region_tiles(c, s, e, manifest=man, root=root) == want, r["region_id"]
