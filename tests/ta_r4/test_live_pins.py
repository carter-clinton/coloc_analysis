"""Live: every catalog and every catalog-derived production panel on disk hashes to its committed manifest row."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from ta_r4 import paths
from ta_r4 import verify_inputs as V

REPO = Path(__file__).resolve().parents[2]
#: panels whose rules read variants_r4 (ta_r4_panels_afr_ukb.smk: --extract range / native catalog positions)
CATALOG_DERIVED = ("AFR661_1kg_r4", "AFR504_1kg_r4", "AFR661_identity_r4", "EUR_ukb337k_r4")

pytestmark = [pytest.mark.r4_heavy,
              pytest.mark.skipif(not (REPO / "data/r4/ld/variants_r4").is_dir(), reason="data/r4 not built")]


def _paths(manifest, col):
    with open(REPO / manifest, newline="") as fh:
        return [r[col] for r in csv.DictReader(fh, delimiter="\t")]


def test_catalogs_match_manifest():
    files = _paths(V.CATALOGS, "rel_path")
    assert len(files) == 43
    V.verify(files, [V.CATALOGS], REPO)


@pytest.mark.parametrize("panel", CATALOG_DERIVED)
def test_catalog_derived_panels_match_manifest(panel):
    m = f"{paths.MAN}/panels_{panel}.tsv"
    files = _paths(m, "path")
    on_disk = sorted(str(p.relative_to(REPO)) for p in (REPO / f"data/r4/ld/{panel}").glob("*.rds"))
    assert sorted(files) == on_disk
    V.verify(files, [m], REPO)


#: DEC-2026-11-17-ta-r4-catalog-unique-allele-key: the r4 catalog, its raw builder output and the dropped audit rows.
KEPT_DIR, RAW_DIR, DROPPED_DIR = "data/r4/ld/variants_r4", "data/r4/ld/variants_r4_raw", "data/r4/ld/variants_r4_dropped"
UNIQUE_KEY_MANIFEST = f"{paths.MAN}/catalogs_r4_unique_key.tsv"


def _r4_regions():
    with open(REPO / V.CATALOGS, newline="") as fh:
        return [r["region_safe"] for r in csv.DictReader(fh, delimiter="\t") if r["route"] == "r4"]


def _norm_key(line):
    c, p, r, a = line.rstrip("\n").split("\t")[:4]
    c = c.strip()
    for pre in ("chr", "CHR"):
        if c.startswith(pre):
            c = c[len(pre):]
            break
    return (c, int(p.strip()), r.strip().upper(), a.strip().upper())


def _body(rel):
    return (REPO / rel).read_text().splitlines(keepends=True)[1:]


@pytest.mark.parametrize("region", _r4_regions())
def test_r4_catalog_one_row_per_allele_key(region):
    keys = [_norm_key(x) for x in _body(f"{KEPT_DIR}/{region}.tsv")]
    assert len(keys) == len(set(keys)), "normalized duplicate keys in the kept catalog"


@pytest.mark.parametrize("region", _r4_regions())
def test_r4_catalog_kept_plus_dropped_is_raw(region):
    dropped = ["\t".join(x.rstrip("\n").split("\t")[:5]) + "\n" for x in _body(f"{DROPPED_DIR}/{region}.tsv")]
    assert sorted(_body(f"{KEPT_DIR}/{region}.tsv") + dropped) == sorted(_body(f"{RAW_DIR}/{region}.tsv"))


@pytest.mark.parametrize("region", _r4_regions())
def test_r4_catalog_key_set_is_raw_key_set(region):
    kept = {_norm_key(x) for x in _body(f"{KEPT_DIR}/{region}.tsv")}
    assert kept == {_norm_key(x) for x in _body(f"{RAW_DIR}/{region}.tsv")}


def test_raw_and_dropped_match_unique_key_manifest():
    import hashlib

    with open(REPO / UNIQUE_KEY_MANIFEST, newline="") as fh:
        rows = {r["region_safe"]: r for r in csv.DictReader(fh, delimiter="\t")}
    assert sorted(rows) == sorted(_r4_regions())
    for region, r in rows.items():
        for d, col in ((RAW_DIR, "raw_sha256"), (DROPPED_DIR, "dropped_sha256")):
            assert hashlib.sha256((REPO / f"{d}/{region}.tsv").read_bytes()).hexdigest() == r[col], (region, col)
