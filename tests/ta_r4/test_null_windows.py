"""GWAS-null window selection: the third admissible negative-control set (REQ-NEGATIVE-CONTROLS)."""
from __future__ import annotations

import csv
import gzip
import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

from .conftest import MAN_DIR, REPO_ROOT

from ta_r4 import select_null_windows as snw

SCRIPT = REPO_ROOT / "src/python/ta_r4/select_null_windows.py"
SELECTION = MAN_DIR / "null_windows_selection.tsv"
W = 250_000
EUR = ("asthma", "bmi", "hypertension", "stroke", "t2d")
AFR = ("asthma", "stroke", "t2d")

# Fixture genome: chr1 tiles k=0..39 and chr2 tiles k=60..99, 200 variants each in every file.
CHR1_TILES = range(0, 40)
CHR2_TILES = range(60, 100)
CURATED = (2, 20_000_001, 20_600_000)  # excludes chr2 tiles whose start <= 21_600_000
TILE_STRONG = (1, 3)       # one variant P = 1e-6 in t2d.AFR
TILE_WEAK = (1, 4)         # one variant P = 2e-5 (boundary: kept)
TILE_199 = (1, 5)          # 199 variants in hypertension.EUR
TILE_900KB = (2, 86)       # start 21_500_001: 900_001 bp after the curated end
TILE_1150KB = (2, 87)      # start 21_750_001: kept


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _write_sumstats(path, trait, anc):
    rows = ["CHR\tPOS\tBETA\tSE\tP\tSNP_ID"]
    for chrom, tiles in ((1, CHR1_TILES), (2, CHR2_TILES)):
        for k in tiles:
            n = 199 if (chrom, k) == TILE_199 and (trait, anc) == ("hypertension", "EUR") else 200
            for i in range(n):
                pos = k * W + 1 + i * 1000
                p = 0.5
                if i == 7 and (chrom, k) == TILE_STRONG and (trait, anc) == ("t2d", "AFR"):
                    p = 1e-6
                if i == 9 and (chrom, k) == TILE_WEAK and (trait, anc) == ("asthma", "EUR"):
                    p = 2e-5
                rows.append(f"{chrom}\t{pos}\t0.01\t0.01\t{p}\trs{chrom}_{pos}")
    rows.append("X\t1000\t0.01\t0.01\t1e-30\trsX")  # non-autosomal: ignored
    with gzip.open(path, "wt") as fh:
        fh.write("\n".join(rows) + "\n")


@pytest.fixture(scope="module")
def fixture_inputs(tmp_path_factory):
    d = tmp_path_factory.mktemp("nullwin")
    paths = []
    for t in EUR:
        paths.append(d / f"{t}.EUR.tsv.bgz")
        _write_sumstats(paths[-1], t, "EUR")
    for t in AFR:
        paths.append(d / f"{t}.AFR.tsv.bgz")
        _write_sumstats(paths[-1], t, "AFR")
    man = d / "sha.tsv"
    man.write_text("relative_path\tsha256\tbytes\n" + "".join(
        f"{p.name}\t{sha(p)}\t{p.stat().st_size}\n" for p in paths))
    cur = d / "regions_curated.csv"
    cur.write_text(
        "region_id,ancestry,chr,start,end,lead_snp,gene,trait_list,source,canonical_pairs\n"
        f"CUR_A,EUR,{CURATED[0]},{CURATED[1]},{CURATED[2]},NA,NA,bmi,x,\"\"\n"
        "CUR_X,EUR,X,1,1000,NA,NA,bmi,x,\"\"\n")
    nc = d / "negative_controls.yaml"
    nc.write_text(yaml.safe_dump({"curated_sets": {
        "cosmetic": {"regions_grch37": [{"chr": 1, "start": 7_000_001, "end": 7_100_000, "gene": "G1"}]},
        "blood_group": {"regions_grch37": [{"chr": 9, "start": 1, "end": 2, "gene": "G2"}]},
        "hla_immune": {"region_grch37": {"chr": 6, "start": 25_000_000, "end": 35_000_000}},
    }}))
    return {"dir": d, "sumstats": paths, "manifest": man, "curated": cur, "nc": nc}


def _run(fx, out_dir, sumstats=None, manifest=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    cand, sel = out_dir / "cand.tsv", out_dir / "sel.tsv"
    cmd = [sys.executable, str(SCRIPT), "--sumstats", *map(str, sumstats or fx["sumstats"]),
           "--sha256-manifest", str(manifest or fx["manifest"]),
           "--regions-curated", str(fx["curated"]), "--negative-controls", str(fx["nc"]),
           "--candidates-out", str(cand), "--selected-out", str(sel)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r, cand, sel


def _tsv(p):
    with open(p) as fh:
        return list(csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t"))


def _tiles(rows):
    return {(int(r["chr"]), (int(r["start"]) - 1) // W) for r in rows}


@pytest.fixture(scope="module")
def run_once(fixture_inputs, tmp_path_factory):
    r, cand, sel = _run(fixture_inputs, tmp_path_factory.mktemp("run1"))
    assert r.returncode == 0, r.stderr
    return cand, sel


def test_tile_geometry():
    assert snw.tile_bounds(snw.tile_index(1, W), W) == (1, 250_000)
    assert snw.tile_bounds(snw.tile_index(250_000, W), W) == (1, 250_000)
    assert snw.tile_bounds(snw.tile_index(250_001, W), W) == (250_001, 500_000)


def test_strong_p_tile_excluded(run_once):
    tiles = _tiles(_tsv(run_once[0]))
    assert TILE_STRONG not in tiles
    assert TILE_WEAK in tiles


def test_tile_900kb_from_curated_excluded(run_once):
    tiles = _tiles(_tsv(run_once[0]))
    assert TILE_900KB not in tiles
    assert TILE_1150KB in tiles


def test_tile_with_199_eur_variants_excluded(run_once):
    tiles = _tiles(_tsv(run_once[0]))
    assert TILE_199 not in tiles
    assert (1, 6) in tiles


def test_nc_region_pm_1mb_excluded(run_once):
    tiles = _tiles(_tsv(run_once[0]))
    # cosmetic fixture 7_000_001-7_100_000 +/- 1 Mb -> chr1 tiles k=24..32 are out
    assert not tiles & {(1, k) for k in range(24, 33)}
    assert (1, 23) in tiles and (1, 33) in tiles


def test_candidate_set_exact(run_once):
    expect = ({(1, k) for k in CHR1_TILES} - {TILE_STRONG, TILE_199} - {(1, k) for k in range(24, 33)}
              | {(2, k) for k in CHR2_TILES if k * W + 1 > CURATED[2] + 1_000_000
                 or (k + 1) * W < CURATED[1] - 1_000_000})
    assert _tiles(_tsv(run_once[0])) == expect


def test_selection_rule_is_seeded_rng_over_sorted_candidates(run_once):
    cand = sorted(_tiles(_tsv(run_once[0])))
    idx = np.random.default_rng(20261021).choice(len(cand), 10, replace=False)
    expect = sorted(cand[i] for i in idx)
    rows = _tsv(run_once[1])
    assert [(int(r["chr"]), (int(r["start"]) - 1) // W) for r in rows] == expect
    assert [r["region_id"] for r in rows] == [f"NC_NULL_{i:02d}" for i in range(1, 11)]


def test_selected_comment_block(run_once, fixture_inputs):
    lines = [l for l in Path(run_once[1]).read_text().splitlines() if l.startswith("#")]
    text = "\n".join(lines)
    assert f"n_candidates\t{len(_tsv(run_once[0]))}" in text
    assert f"candidates_sha256\t{sha(run_once[0])}" in text
    for p in fixture_inputs["sumstats"]:
        assert f"{p.name}\t{sha(p)}" in text


def test_deterministic(fixture_inputs, run_once, tmp_path):
    r, cand, sel = _run(fixture_inputs, tmp_path / "run2")
    assert r.returncode == 0, r.stderr
    assert sha(cand) == sha(run_once[0]) and sha(sel) == sha(run_once[1])


def test_sha_mismatch_exits_2(fixture_inputs, tmp_path):
    bad = tmp_path / "bad.tsv"
    bad.write_text(fixture_inputs["manifest"].read_text().replace(
        sha(fixture_inputs["sumstats"][0]), "0" * 64))
    r, cand, _ = _run(fixture_inputs, tmp_path / "o", manifest=bad)
    assert r.returncode == 2
    assert not cand.exists()


# --- committed real-data selection and regions_r4.csv ----------------------------------------

def test_committed_selection_shape():
    rows = _tsv(SELECTION)
    assert [r["region_id"] for r in rows] == [f"NC_NULL_{i:02d}" for i in range(1, 11)]
    keys = [(int(r["chr"]), int(r["start"])) for r in rows]
    assert keys == sorted(keys)
    for r in rows:
        assert 1 <= int(r["chr"]) <= 22
        assert (int(r["start"]) - 1) % W == 0 and int(r["end"]) - int(r["start"]) + 1 == W
        assert float(r["min_p"]) >= 1e-5
        assert all(int(r[f"n_var_{t}"]) >= 200 for t in EUR)


def test_regions_r4_is_rebuilt_from_sources():
    text = snw.regions_r4_text(REPO_ROOT / "config/regions_curated.csv",
                               REPO_ROOT / "config/negative_controls.yaml", SELECTION)
    assert (REPO_ROOT / "config/ta_r4/regions_r4.csv").read_text() == text


def test_regions_r4_rows():
    path = REPO_ROOT / "config/ta_r4/regions_r4.csv"
    lines = path.read_text().splitlines()
    cur = (REPO_ROOT / "config/regions_curated.csv").read_text().splitlines()
    assert lines[: len(cur)] == cur  # header + 12 curated rows verbatim
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 31
    nc = [r["region_id"] for r in rows if r["source"] == "negative_control"]
    assert nc == ["NC_OCA2_HERC2", "NC_SLC24A5", "NC_MC1R", "NC_TYR", "NC_IRF4",
                  "NC_ABO", "NC_RH", "NC_FUT1_FUT2", "NC_KEL"]
    null = [r["region_id"] for r in rows if r["source"] == "negative_control_gwas_null"]
    assert null == [f"NC_NULL_{i:02d}" for i in range(1, 11)]
    assert all(r["ancestry"] == "EUR" and r["canonical_pairs"] == "" for r in rows[12:])


def test_null_windows_respect_exclusions():
    with open(REPO_ROOT / "config/negative_controls.yaml") as fh:
        ncy = yaml.safe_load(fh)
    zones = snw.exclusion_zones(REPO_ROOT / "config/regions_curated.csv", ncy)
    for r in _tsv(SELECTION):
        c, s, e = int(r["chr"]), int(r["start"]), int(r["end"])
        assert not any(zc == c and s <= zb and e >= za for zc, za, zb in zones), r["region_id"]


@pytest.mark.r4_heavy
def test_real_selection_reproduces_committed(tmp_path):
    """Re-run the selector on the 8 sha256-pinned Track A files (~3.5 min)."""
    s = REPO_ROOT / "data/processed/sumstats_harmonized"
    files = [s / f"{t}.EUR.tsv.bgz" for t in EUR] + [s / f"{t}.AFR.tsv.bgz" for t in AFR]
    cand, sel = tmp_path / "cand.tsv", tmp_path / "sel.tsv"
    r = subprocess.run([sys.executable, str(SCRIPT), "--sumstats", *map(str, files),
                        "--sha256-manifest", str(REPO_ROOT / ".planning/amendments/sha256_manifest_harmonized_m1.tsv"),
                        "--regions-curated", str(REPO_ROOT / "config/regions_curated.csv"),
                        "--negative-controls", str(REPO_ROOT / "config/negative_controls.yaml"),
                        "--candidates-out", str(cand), "--selected-out", str(sel)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert sha(sel) == sha(SELECTION)
    assert f"candidates_sha256\t{sha(cand)}" in SELECTION.read_text()
