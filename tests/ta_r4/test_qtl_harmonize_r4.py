"""W3e Task 1: ta_r4.harmonize_qtl_r4 runs the shipped harmonizers once per manifest feature (molecular_trait_id).

eQTL: output equals the shipped harmonize_eqtl.py CLI for the same gene. sQTL: the shipped CLI filters on gene_id,
so a gene with two junctions comes out as both junctions' rows mixed (duplicate variant_ids); per junction the
wrapper's files partition exactly those rows.
"""
from __future__ import annotations

import csv
import gzip
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from .conftest import REPO_ROOT

from ta_r4 import harmonize_qtl_r4 as H

HDR = ["molecular_trait_id", "chromosome", "position", "ref", "alt", "variant", "ma_samples", "maf", "pvalue",
       "beta", "se", "type", "ac", "an", "r2", "molecular_trait_object_id", "gene_id", "median_tpm", "rsid"]
MCOLS = ["qtl_row_id", "region_safe", "ancestry", "trait", "source", "tissue", "qtd", "gene_id",
         "molecular_trait_id", "chr38", "start38", "end38", "n_qtl_variants_in_window"]
WIN = (9, 1000, 2000)
GENE_A, GENE_B = "ENSG00000000001", "ENSG00000000002"
J1, J2 = "9:1100:1900:clu_1_+", "9:1200:1800:clu_2_+"


def _rows(feature, gene, n, seed):
    out = []
    for i in range(n):
        pos = 900 + 50 * i  # 900, 950 outside the window; the rest inside up to 2000
        maf = 0.002 if i == 5 else 0.1 + 0.01 * (i % 7)  # one MAF drop
        out.append([feature, "9", pos, "A", "G", f"chr9_{pos}_A_G", 10, maf, 0.5, 0.01 * (i + seed), 0.05, "SNP",
                    20, 1000, "NA", feature, gene, 3.0, f"rs{1000 + i}"])
    return out


def _write_input(path, rows):
    with gzip.open(path, "wt") as fh:
        fh.write("\t".join(HDR) + "\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")


def _write_manifest(path, source, qtd, feats):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(MCOLS)
        for trait in ("asthma", "bmi"):
            for f, g in feats:
                w.writerow([f"FIX__EUR__{trait}__{source}__Whole_Blood__{f}", "FIX_1", "EUR", trait, source,
                            "Whole_Blood", qtd, g, f, *WIN, 5])


def _read(path):
    with gzip.open(path, "rt") as fh:
        return fh.read().splitlines()


def _shipped(tmp, script, inp, gene, out):
    cmd = [sys.executable, str(REPO_ROOT / "src/python" / script), "--input", str(inp), "--region-chr", "9",
           "--region-start", str(WIN[1]), "--region-end", str(WIN[2]), "--gene-id", gene, "--tissue-name",
           "Whole_Blood", "--tissue-n", "670", "--qtl-source-config", str(REPO_ROOT / H.QTL_SOURCES),
           "--output", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp,
                       env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src/python")})
    assert r.returncode == 0, r.stderr
    return _read(out)


@pytest.fixture()
def eqtl(tmp_path):
    inp = tmp_path / "QTDE.all.tsv.gz"
    _write_input(inp, _rows(GENE_A, GENE_A, 30, 0) + _rows(GENE_B, GENE_B, 25, 3))
    man = tmp_path / "m.tsv"
    _write_manifest(man, "eqtl", "QTDE", [(GENE_A, GENE_A), (GENE_B, GENE_B)])
    return tmp_path, inp, man


@pytest.fixture()
def sqtl(tmp_path):
    inp = tmp_path / "QTDS.cc.tsv.gz"
    _write_input(inp, _rows(J1, GENE_A, 30, 0) + _rows(J2, GENE_A, 30, 7))
    man = tmp_path / "m.tsv"
    _write_manifest(man, "sqtl", "QTDS", [(J1, GENE_A), (J2, GENE_A)])
    return tmp_path, inp, man


def test_group_features_distinct_and_sorted(eqtl):
    _, _, man = eqtl
    feats, win = H.group_features(H.manifest_rows(man), "eqtl", "QTDE", "FIX_1")
    assert feats == [(GENE_A, GENE_A), (GENE_B, GENE_B)]
    assert win == {"tissue": "Whole_Blood", "chr": "9", "start": 1000, "end": 2000}


def test_eqtl_equals_shipped_cli(eqtl):
    tmp, inp, man = eqtl
    recs = H.harmonize_group("eqtl", "QTDE", "FIX_1", manifest=man, input_path=str(inp), out_root=str(tmp / "h"))
    assert [r["molecular_trait_id"] for r in recs] == [GENE_A, GENE_B]
    for r, gene in zip(recs, (GENE_A, GENE_B)):
        assert r["rel_path"] == str(tmp / "h/eqtl/QTDE" / gene / "FIX_1.harmonized.tsv.gz")
        assert _read(r["rel_path"]) == _shipped(tmp, "harmonize_eqtl.py", inp, gene, tmp / f"{gene}.ship.tsv.gz")
        assert r["n_rows"] == len(_read(r["rel_path"])) - 1 > 0
        assert r["sha256"] == H.sha256(r["rel_path"])


def test_sqtl_partitions_the_shipped_gene_level_rows(sqtl):
    tmp, inp, man = sqtl
    recs = H.harmonize_group("sqtl", "QTDS", "FIX_1", manifest=man, input_path=str(inp), out_root=str(tmp / "h"))
    assert [r["molecular_trait_id"] for r in recs] == [J1, J2]
    per = [_read(r["rel_path"]) for r in recs]
    ship = _shipped(tmp, "harmonize_sqtl.py", inp, GENE_A, tmp / "gene.ship.tsv.gz")
    assert per[0][0] == per[1][0] == ship[0]
    assert Counter(per[0][1:] + per[1][1:]) == Counter(ship[1:])
    vid = [ln.split("\t")[0] for ln in ship[1:]]
    assert max(Counter(vid).values()) == 2  # the shipped gene-level file mixes the two junctions
    for p in per:
        v = [ln.split("\t")[0] for ln in p[1:]]
        assert len(v) == len(set(v)) > 0
    assert per[0] != per[1]


def test_empty_feature_is_written_and_reported(eqtl):
    tmp, inp, man = eqtl
    _write_manifest(man, "eqtl", "QTDE", [(GENE_A, GENE_A), ("ENSG00000009999", "ENSG00000009999")])
    recs = H.harmonize_group("eqtl", "QTDE", "FIX_1", manifest=man, input_path=str(inp), out_root=str(tmp / "h"))
    empty = [r for r in recs if r["n_rows"] == 0]
    assert [r["molecular_trait_id"] for r in empty] == ["ENSG00000009999"]
    assert empty[0]["message"].startswith("No variants after harmonization")
    assert len(_read(empty[0]["rel_path"])) == 1  # header only


def test_reader_restored_after_each_feature(eqtl):
    tmp, inp, man = eqtl
    import harmonize_eqtl
    orig = harmonize_eqtl._read_eqtl_file
    H.harmonize_group("eqtl", "QTDE", "FIX_1", manifest=man, input_path=str(inp), out_root=str(tmp / "h"))
    assert harmonize_eqtl._read_eqtl_file is orig


def test_done_file_columns(eqtl, tmp_path):
    tmp, inp, man = eqtl
    recs = H.harmonize_group("eqtl", "QTDE", "FIX_1", manifest=man, input_path=str(inp), out_root=str(tmp / "h"))
    H.write_done(recs, tmp_path / "g.done")
    with open(tmp_path / "g.done", newline="") as fh:
        got = list(csv.DictReader(fh, delimiter="\t"))
    assert list(got[0]) == H.DONE_COLUMNS and len(got) == 2


def test_real_groups_and_download_paths():
    rows = H.manifest_rows(REPO_ROOT / H.MANIFEST)
    gs = H.groups(rows)
    idx = H.group_index(rows)
    assert sorted(idx) == gs and sum(map(len, idx.values())) == len(rows)
    n_feat = sum(len(H.group_features(idx[g], *g)[0]) for g in gs)
    assert n_feat == len({(r["source"], r["qtd"], r["molecular_trait_id"], r["region_safe"]) for r in rows})
    for qtd in sorted({g[1] for g in gs}):
        p = H.download_path(qtd, dl_manifest=REPO_ROOT / H.DL_MANIFEST)
        assert p.startswith("data/r4/downloads/eqtl_catalogue/") and p.endswith((".all.tsv.gz", ".cc.tsv.gz"))
