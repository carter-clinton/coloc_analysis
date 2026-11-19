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


#: DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1: at most one variant per CHR:POS in every UKB native panel.
UKB_NATIVE_DIR = "data/r4/ld/EUR_ukb337k_r4"
UKB_NATIVE_MANIFEST = f"{paths.MAN}/panels_EUR_ukb337k_r4.tsv"
UKB_RESOLVED_MANIFEST = f"{paths.MAN}/ukb_native_multiallelic_resolved.tsv"
_K4 = ["CHR", "POS", "REF", "ALT"]


def _ukb_regions():
    with open(REPO / UKB_NATIVE_MANIFEST, newline="") as fh:
        return [r["region_safe"] for r in csv.DictReader(fh, delimiter="\t")]


_UKB_VARIANTS = {}


def _ukb_variants(region):
    """The variants frame of {UKB_NATIVE_DIR}/{region}.rds (cached per directory; R is discarded)."""
    import os

    from ta_r4 import ukb337k_tiles

    key = (UKB_NATIVE_DIR, region)
    if key not in _UKB_VARIANTS:
        rs = os.environ.get("RSCRIPT", "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript")
        _, v = ukb337k_tiles.read_rds(REPO / UKB_NATIVE_DIR / f"{region}.rds", rscript=rs, tmpdir=REPO / "data/r4/tmp")
        _UKB_VARIANTS[key] = v
    return _UKB_VARIANTS[key]


def _ukb_audit():
    import pandas as pd

    a = pd.read_csv(REPO / UKB_RESOLVED_MANIFEST, sep="\t", dtype=str, keep_default_na=False)
    a["POS"] = a["POS"].astype(int)
    return a


@pytest.mark.parametrize("region", _ukb_regions())
def test_ukb_native_one_variant_per_chrpos(region):
    v = _ukb_variants(region)
    dup = v[v.duplicated(["CHR", "POS"], keep=False)]
    assert dup.empty, f"{region}: duplicated CHR:POS {sorted(set(zip(dup['CHR'], dup['POS'])))[:5]}"


@pytest.mark.parametrize("region", _ukb_regions())
def test_ukb_native_resolution_audit_reconciles(region):
    from ta_r4.ukb_native_multiallelic import is_snv

    with open(REPO / UKB_NATIVE_MANIFEST, newline="") as fh:
        m = {r["region_safe"]: r for r in csv.DictReader(fh, delimiter="\t")}[region]
    a = _ukb_audit()
    a = a[a["region_safe"] == region]
    v = _ukb_variants(region)
    kept, dropped = a[a["action"] == "kept_snv"], a[a["action"] == "dropped"]
    assert int(m["n_var"]) == len(v)
    assert int(m["n_var"]) + int(m["n_var_dropped_multiallelic"]) == len(v) + len(dropped)
    assert len(dropped) == int(m["n_var_dropped_multiallelic"])
    assert len(kept) == int(m["n_sites_kept_snv"])
    pos = a.groupby("POS")["action"].apply(set)
    assert len(pos) == int(m["n_sites_multiallelic"])
    assert sum(1 for s in pos if "kept_snv" not in s) == int(m["n_sites_dropped_all"])
    panel = set(zip(v["SNP_ID"], *(v[c].astype(str) for c in _K4)))
    for _, r in kept.iterrows():
        assert is_snv(r["REF"], r["ALT"]) and (r["SNP_ID"], r["CHR"], str(r["POS"]), r["REF"], r["ALT"]) in panel, r
    panel4 = {k[1:] for k in panel}
    for _, r in dropped.iterrows():
        assert (r["CHR"], str(r["POS"]), r["REF"], r["ALT"]) not in panel4, r


def test_ukb_native_pyhin1_160680184_keeps_rs184461353():
    v = _ukb_variants("PYHIN1_1q23")
    at = v[(v["CHR"] == "1") & (v["POS"] == 160680184)]
    assert list(at["SNP_ID"]) == ["rs184461353"]
    assert {at["REF"].iloc[0], at["ALT"].iloc[0]} == {"A", "G"}
