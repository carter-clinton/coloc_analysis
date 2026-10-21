"""Pre-registered static all-pairs manifest (D-07, D-24); no tier gate, no outcome column."""
from __future__ import annotations

import csv
import hashlib
import itertools
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from .conftest import REPO_ROOT

from ta_r4 import build_pair_manifest as bpm

SCRIPT = REPO_ROOT / "src/python/ta_r4/build_pair_manifest.py"
MANIFEST = REPO_ROOT / "config/ta_r4/pair_manifest.tsv"
REGIONS = REPO_ROOT / "config/ta_r4/regions_r4.csv"
EUR = ("asthma", "bmi", "hypertension", "stroke", "t2d")
AFR = ("asthma", "stroke", "t2d")
INADMISSIBLE = {"HLA_6p21", "BMI_Xq24"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _rows(p=MANIFEST):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _build(out):
    return subprocess.run([sys.executable, str(SCRIPT), "--regions", str(REGIONS), "--out", str(out)],
                          capture_output=True, text=True)


def test_counts_by_class():
    rows = _rows()
    assert len(rows) == 346
    c = Counter((r["row_class"], r["ancestry"]) for r in rows)
    assert c == {("primary", "EUR"): 120, ("primary", "AFR"): 36, ("negative_control", "EUR"): 190}


def test_admissible():
    rows = _rows()
    assert sum(r["admissible"] == "true" for r in rows) == 320
    assert {r["admissible"] for r in rows} == {"true", "false"}
    bad = [r for r in rows if r["admissible"] == "false"]
    assert len(bad) == 26
    assert {r["region_id"] for r in bad} == INADMISSIBLE
    assert all(r["inadmissible_reason"].startswith("D-24:") for r in bad)
    assert all(r["inadmissible_reason"] == "" for r in rows if r["admissible"] == "true")


def test_eur_pairs_complete_per_region():
    rows = [r for r in _rows() if r["ancestry"] == "EUR"]
    by = {}
    for r in rows:
        assert r["trait_a"] < r["trait_b"]
        by.setdefault(r["region_safe"], []).append((r["trait_a"], r["trait_b"]))
    assert len(by) == 31
    for reg, pairs in by.items():
        assert sorted(pairs) == list(itertools.combinations(EUR, 2)), reg


def test_afr_traits_only():
    rows = [r for r in _rows() if r["ancestry"] == "AFR"]
    assert {r["trait_a"] for r in rows} | {r["trait_b"] for r in rows} == set(AFR)
    assert len({r["region_safe"] for r in rows}) == 12


def test_row_id():
    rows = _rows()
    ids = [r["row_id"] for r in rows]
    assert len(set(ids)) == len(ids)
    for r in rows:
        assert r["row_id"] == f"{r['region_safe']}__{r['ancestry']}__{r['trait_a']}_vs_{r['trait_b']}"
    assert "BMI_5q13_3__EUR__asthma_vs_bmi" in ids


def test_nc_sets():
    nc = [r for r in _rows() if r["row_class"] == "negative_control"]
    assert Counter(r["nc_set"] for r in nc) == {"cosmetic": 50, "blood_group": 40, "gwas_null": 100}
    assert all(r["nc_set"] == "" for r in _rows() if r["row_class"] == "primary")
    assert all(r["admissible"] == "true" for r in nc)


def test_abo_caveat():
    rows = _rows()
    abo = [r for r in rows if r["region_id"] == "NC_ABO"]
    assert len(abo) == 10
    assert all(r["nc_caveat"] == "reported_stroke_association_verify" for r in abo)
    assert all(r["nc_caveat"] == "" for r in rows if r["region_id"] != "NC_ABO")


def test_canonical_pair():
    rows = {r["row_id"]: r for r in _rows()}
    assert rows["FTO_16q12__EUR__bmi_vs_t2d"]["canonical_pair"] == "true"
    assert rows["FTO_16q12__EUR__asthma_vs_bmi"]["canonical_pair"] == "false"
    assert rows["SH2B3_12q24__AFR__stroke_vs_t2d"]["canonical_pair"] == "true"
    assert sum(r["canonical_pair"] == "true" for r in rows.values()) == 15 + 2
    # 15 EUR canonical pairs in regions_curated.csv (FTO 3, MC4R 1, SH2B3 9, APOL1 1, CXADR 1); AFR: SH2B3 asthma_vs_stroke + stroke_vs_t2d


def test_schema_ok():
    assert bpm.schema_violations(MANIFEST) == []


def test_schema_rejects_outcome_column(tmp_path):
    bad = tmp_path / "m.tsv"
    lines = MANIFEST.read_text().splitlines()
    bad.write_text("\n".join([lines[0] + "\tstatus"] + [l + "\tok" for l in lines[1:]]) + "\n")
    v = bpm.schema_violations(bad)
    assert v and any("status" in x for x in v)


def test_committed_manifest_is_builder_output(tmp_path):
    r = _build(tmp_path / "a.tsv")
    assert r.returncode == 0, r.stderr
    assert sha(tmp_path / "a.tsv") == sha(MANIFEST)


def test_builder_deterministic(tmp_path):
    assert _build(tmp_path / "a.tsv").returncode == 0
    assert _build(tmp_path / "b.tsv").returncode == 0
    assert sha(tmp_path / "a.tsv") == sha(tmp_path / "b.tsv")
    assert b"\r" not in (tmp_path / "a.tsv").read_bytes()


def test_sorted():
    rows = _rows()
    key = [(r["row_class"], r["ancestry"], r["region_safe"], r["trait_a"], r["trait_b"]) for r in rows]
    assert key == sorted(key)
