"""ta-r4 W2c: static, outcome-independent QTL-coloc manifest (build_qtl_manifest)."""
from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

import pytest
import yaml

from .conftest import MAN_DIR, REPO_ROOT

HTS_BIN = "/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin"
TABIX = f"{HTS_BIN}/tabix"
COMMITTED = REPO_ROOT / "config/ta_r4/qtl_manifest.tsv"
DL_MAN = MAN_DIR / "qtl_downloads_sha256.tsv"

HEADER = ["molecular_trait_id", "chromosome", "position", "ref", "alt", "variant", "ma_samples", "maf", "pvalue",
          "beta", "se", "type", "ac", "an", "r2", "molecular_trait_object_id", "gene_id", "median_tpm", "rsid"]

# region R1 = chr1:1000-2000, R2 = chr2:5000-6000 (inclusive)
REGIONS = [{"region_safe": "R1", "chr38": "1", "start38": 1000, "end38": 2000},
           {"region_safe": "R2", "chr38": "2", "start38": 5000, "end38": 6000}]
TRAITS = ["t_a", "t_b", "t_c"]


def _rec(mtid, chrom, pos, gene=None):
    gene = gene or mtid
    return [mtid, chrom, str(pos), "A", "G", f"chr{chrom}_{pos}_A_G", "5", "0.1", "0.5", "0.1", "0.2", "SNP",
            "5", "100", "NA", mtid, gene, "1.0", f"rs{pos}"]


def _write_bgz(path, recs):
    import ta_r4.build_qtl_manifest  # noqa: F401  (RED before the module exists)
    recs = sorted(recs, key=lambda r: (int(r[1]), int(r[2])))
    plain = path.with_suffix("")
    plain.write_text("\t".join(HEADER) + "\n" + "".join("\t".join(r) + "\n" for r in recs))
    subprocess.run([f"{HTS_BIN}/bgzip", "-f", str(plain)], check=True)
    subprocess.run([TABIX, "-f", "-s", "2", "-b", "3", "-e", "3", "-S", "1", str(path)], check=True)


# file key: (source, tissue) -> records
FIXTURE = {
    ("eqtl", "T1"): [_rec("G1", "1", 1000), _rec("G1", "1", 1500), _rec("G2", "1", 2000), _rec("G3", "1", 999),
                     _rec("G3", "1", 2001), _rec("G4", "2", 5500)],
    ("eqtl", "T2"): [_rec("G1", "1", 1200), _rec("G9", "2", 6000)],
    ("sqtl", "T1"): [_rec("1:1:2:clu_1_+", "1", 1100, "G1"), _rec("1:1:2:clu_1_+", "1", 1101, "G1"),
                     _rec("2:5:6:clu_2_-", "2", 4999, "G4")],
    ("sqtl", "T2"): [_rec("2:5:6:clu_3_-", "2", 5000, "G9")],
}
# expected (region, source, tissue, molecular_trait_id) -> n distinct variants in window
EXPECTED = {
    ("R1", "eqtl", "T1", "G1"): 2, ("R1", "eqtl", "T1", "G2"): 1, ("R2", "eqtl", "T1", "G4"): 1,
    ("R1", "eqtl", "T2", "G1"): 1, ("R2", "eqtl", "T2", "G9"): 1,
    ("R1", "sqtl", "T1", "1:1:2:clu_1_+"): 2,
    ("R2", "sqtl", "T2", "2:5:6:clu_3_-"): 1,
}


@pytest.fixture
def files(tmp_path):
    out = []
    for i, ((src, tissue), recs) in enumerate(sorted(FIXTURE.items())):
        p = tmp_path / f"QTD{i:06d}.tsv.gz"
        _write_bgz(p, recs)
        out.append({"qtd": f"QTD{i:06d}", "source": src, "tissue": tissue, "path": str(p)})
    return out


def _build(files, scope="full", frozen=frozenset({"T1"})):
    from ta_r4 import build_qtl_manifest as b
    return b.build_rows(b.scope_filter(files, scope, frozen), REGIONS, TRAITS, TABIX, jobs=2)


def _key(r):
    return (r["region_safe"], r["source"], r["tissue"], r["molecular_trait_id"])


def test_rows_are_window_features_times_traits(files):
    rows = _build(files)
    got = {}
    for r in rows:
        got.setdefault(_key(r), set()).add(r["trait"])
        assert int(r["n_qtl_variants_in_window"]) == EXPECTED[_key(r)]
    assert set(got) == set(EXPECTED)
    assert all(v == set(TRAITS) for v in got.values())
    assert len(rows) == len(EXPECTED) * len(TRAITS)
    assert len({r["qtl_row_id"] for r in rows}) == len(rows)


def test_sqtl_keeps_gene_id_and_junction_id(files):
    rows = [r for r in _build(files) if r["source"] == "sqtl" and r["region_safe"] == "R1"]
    assert {(r["molecular_trait_id"], r["gene_id"]) for r in rows} == {("1:1:2:clu_1_+", "G1")}


@pytest.mark.parametrize("scope,expected_pairs", [
    ("full", {("eqtl", "T1"), ("eqtl", "T2"), ("sqtl", "T1"), ("sqtl", "T2")}),
    ("tissues_frozen", {("eqtl", "T1"), ("sqtl", "T1")}),
    ("eqtl_only", {("eqtl", "T1"), ("eqtl", "T2")}),
    ("tissues_frozen+eqtl_only", {("eqtl", "T1")}),
])
def test_scope_is_a_pure_subset_filter(files, scope, expected_pairs):
    full = {tuple(sorted(r.items())) for r in _build(files)}
    sub = _build(files, scope)
    assert {tuple(sorted(r.items())) for r in sub} <= full
    assert {(r["source"], r["tissue"]) for r in sub} == expected_pairs
    exp_full = [r for r in _build(files) if (r["source"], r["tissue"]) in expected_pairs]
    assert len(sub) == len(exp_full)


def test_unknown_scope_refused(files):
    from ta_r4 import build_qtl_manifest as b
    with pytest.raises(ValueError):
        b.scope_filter(files, "tier_a_only", frozenset())


def test_schema_rejects_status_or_tier_column():
    from ta_r4 import build_qtl_manifest as b
    b.check_schema(b.COLUMNS)
    for bad in ("status", "tier", "qtl_tier", "fit_status"):
        with pytest.raises(ValueError):
            b.check_schema(b.COLUMNS + [bad])


def test_written_manifest_deterministic(files, tmp_path):
    from ta_r4 import build_qtl_manifest as b
    a, c = tmp_path / "a.tsv", tmp_path / "c.tsv"
    b.write_manifest(_build(files), a)
    b.write_manifest(list(reversed(_build(files))), c)
    assert a.read_bytes() == c.read_bytes()
    assert a.read_text().splitlines()[0].split("\t") == b.COLUMNS


def test_frozen_tissues_are_the_legacy_lookup():
    from ta_r4 import build_qtl_manifest as b
    tissues, src = b.frozen_tissues()
    with open(REPO_ROOT / "config/eqtl_catalogue_qtd_map.yaml") as fh:
        qmap = set(yaml.safe_load(fh)["tissues"])
    assert len(tissues) == 49 and set(tissues) == qmap
    assert "GTEX_V8_TISSUE_N_FALLBACK" in src


def test_default_scope(tmp_path):
    from ta_r4 import build_qtl_manifest as b
    assert b.default_scope(tmp_path / "absent.yaml") == "full"
    p = tmp_path / "rd.yaml"
    p.write_text("qtl_scope: eqtl_only\n")
    assert b.default_scope(p) == "eqtl_only"
    p.write_text("qtl_scope: everything\n")
    with pytest.raises(ValueError):
        b.default_scope(p)


def test_admissible_regions_and_traits():
    from ta_r4 import build_qtl_manifest as b
    regions = b.admissible_regions()
    assert [r["region_safe"] for r in regions] == sorted([
        "FTO_16q12", "MC4R_18q21", "SH2B3_12q24", "APOL1_22q12", "PYHIN1_1q23", "CXADR_F2RL1_6p21",
        "BMI_5q13_3", "9p21_CDKN2A", "APOE_19q13", "SLC2A9_urate"])
    bmi = next(r for r in regions if r["region_safe"] == "BMI_5q13_3")
    assert (bmi["chr38"], bmi["start38"], bmi["end38"]) == ("5", 72704173, 76704175)
    assert b.eur_traits() == ["asthma", "bmi", "hypertension", "stroke", "t2d"]


def _read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_committed_manifest_schema_and_reconciliation():
    from ta_r4 import build_qtl_manifest as b
    rows = _read(COMMITTED)
    assert list(rows[0].keys()) == b.COLUMNS
    b.check_schema(list(rows[0].keys()))
    feats = {(r["region_safe"], r["source"], r["tissue"], r["molecular_trait_id"]) for r in rows}
    assert len(rows) == len(feats) * len(b.eur_traits())
    assert {r["region_safe"] for r in rows} <= {x["region_safe"] for x in b.admissible_regions()}
    assert len({r["qtl_row_id"] for r in rows}) == len(rows)


@pytest.mark.r4_heavy
def test_committed_manifest_regenerates_identically(tmp_path):
    from ta_r4 import build_qtl_manifest as b
    out1, out2 = tmp_path / "m1.tsv", tmp_path / "m2.tsv"
    for out in (out1, out2):
        rc = b.main(["--downloads-manifest", str(DL_MAN), "--tabix", TABIX, "--out", str(out), "--jobs", "8"])
        assert rc == 0
    sha = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (out1, out2, COMMITTED)]
    assert sha[0] == sha[1] == sha[2]
