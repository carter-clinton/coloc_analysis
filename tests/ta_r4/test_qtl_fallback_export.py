"""W3f 15.4 Task 2 (N12): QTL fallback_abf rows keep their method and posteriors in the aggregate table, tiers read
an explicit method == coloc_susie filter, and the Track B default aggregate output is byte-identical (D-15)."""
from __future__ import annotations

import csv
import json
import subprocess

import pytest

from .conftest import REPO_ROOT
from .test_in_job_gate import rendered  # noqa: F401  (module-scoped dry-run fixture)

PY = "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11"
AGG = REPO_ROOT / "src/python/aggregate_qtl_coloc.py"
TIERS = REPO_ROOT / "src/python/assign_tiers.py"
PRE_CHANGE = "319ae8f1"  # last commit of aggregate_qtl_coloc.py before the --with-method-columns flag
META = {"qtl_n": 500, "qtl_sdy": 1, "ancestry": "EUR"}


def _pp(h):
    return {f"PP.H{i}.abf": v for i, v in enumerate(h)}


def docs():
    """run_qtl_group_r4 doc shape (doc.update(run_qtl_coloc.R JSON) + method / fallback / top-level pp_h*)."""
    susie = {**META, "qtl_row_id": "R1__x__eqtl__QTD1__G1", "qtl_source": "gtex_eqtl", "tissue": "Lung",
             "gene_id": "G1", "region": "R1", "n_snps_overlap": 300, "n_cs_gwas": 1, "n_cs_qtl": 2,
             "status": "success", "summary": {**_pp([0.0, 0.01, 0.04, 0.05, 0.9]), "hit1": "1:10", "hit2": "1:11"},
             "method": "coloc_susie", "fallback_reason": None, **{f"pp_h{i}": v for i, v in
                                                                  enumerate([0.0, 0.01, 0.04, 0.05, 0.9])}}
    low = {**susie, "qtl_row_id": "R1__x__eqtl__QTD2__G2", "gene_id": "G2", "tissue": "Liver",
           "summary": {**_pp([0.1, 0.1, 0.1, 0.1, 0.6]), "hit1": "1:12", "hit2": "1:13"},
           **{f"pp_h{i}": v for i, v in enumerate([0.1, 0.1, 0.1, 0.1, 0.6])}}
    fb = {"pp_h0": 0.01, "pp_h1": 0.01, "pp_h2": 0.01, "pp_h3": 0.02, "pp_h4": 0.95, "n_snps": 280}
    fallback = {**META, "qtl_row_id": "R1__x__sqtl__QTD3__J1", "qtl_source": "gtex_sqtl", "tissue": "Lung",
                "gene_id": "G3", "region": "R1", "n_snps_overlap": 280, "n_cs_gwas": 1, "n_cs_qtl": 0,
                "status": "no_qtl_cs", "summary": [], "method": "fallback_abf", "fallback_reason": "qtl_n_cs==0",
                "fallback": fb, **{f"pp_h{i}": fb[f"pp_h{i}"] for i in range(5)}}
    only_fb = {**fallback, "qtl_row_id": "R2__x__eqtl__QTD1__G4", "region": "R2", "gene_id": "G4",
               "qtl_source": "gtex_eqtl"}
    none = {**META, "qtl_row_id": "R2__x__eqtl__QTD1__G5", "qtl_source": "gtex_eqtl", "tissue": "Lung",
            "gene_id": "G5", "region": "R2", "status": "ld_join_fatal:panel_bridge_below_threshold",
            "summary": [], "method": "none", "fallback_reason": None,
            **{f"pp_h{i}": None for i in range(5)}}
    return {d["qtl_row_id"]: d for d in (susie, low, fallback, only_fb, none)}


@pytest.fixture
def jdir(tmp_path):
    d = tmp_path / "qtl"
    d.mkdir()
    for rid, doc in docs().items():
        (d / f"{rid}.json").write_text(json.dumps(doc))
    (tmp_path / "manifest.tsv").write_text("qtl_row_id\n" + "".join(f"{r}\n" for r in docs()))
    return d


def _agg(script, jdir, out, *extra):
    p = subprocess.run([PY, "-B", str(script), "--json-dir", str(jdir), "--manifest", str(jdir.parent / "manifest.tsv"),
                        "--output", str(out), *extra], capture_output=True, text=True)
    return p


def _rows(p):
    with open(p) as fh:
        return {r["qtl_coloc_id"]: r for r in csv.DictReader(fh, delimiter="\t")}


def test_default_output_byte_identical_to_pre_change(jdir, tmp_path):
    old = tmp_path / "aggregate_qtl_coloc_pre.py"
    old.write_text(subprocess.run(["git", "show", f"{PRE_CHANGE}:src/python/aggregate_qtl_coloc.py"], cwd=REPO_ROOT,
                                  check=True, capture_output=True, text=True).stdout)
    a, b = _agg(old, jdir, tmp_path / "old.tsv"), _agg(AGG, jdir, tmp_path / "new.tsv")
    assert a.returncode == 0 and b.returncode == 0, (a.stderr, b.stderr)
    assert (tmp_path / "new.tsv").read_bytes() == (tmp_path / "old.tsv").read_bytes()
    assert len(_rows(tmp_path / "new.tsv")) == 5


def test_method_columns_keep_fallback_label_and_posteriors(jdir, tmp_path):
    p = _agg(AGG, jdir, tmp_path / "m.tsv", "--with-method-columns")
    assert p.returncode == 0, p.stderr
    t = _rows(tmp_path / "m.tsv")
    for c in ("method", "fallback_reason", "none_status", "pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4"):
        assert c in next(iter(t.values())), c
    fb = t["R1__x__sqtl__QTD3__J1"]
    assert fb["method"] == "fallback_abf" and fb["fallback_reason"] == "qtl_n_cs==0"
    assert float(fb["pp_h4"]) == docs()["R1__x__sqtl__QTD3__J1"]["fallback"]["pp_h4"] == 0.95
    assert fb["PP.H4.abf"] == ""  # summary semantics: blank for fallback
    s = t["R1__x__eqtl__QTD1__G1"]
    assert s["method"] == "coloc_susie" and float(s["pp_h4"]) == float(s["PP.H4.abf"]) == 0.9
    n = t["R2__x__eqtl__QTD1__G5"]
    assert n["method"] == "none" and n["none_status"] == "ld_join_fatal:panel_bridge_below_threshold"
    assert n["pp_h4"] == "" and s["none_status"] == "" and fb["none_status"] == ""


def test_method_columns_refuse_a_doc_without_method(jdir, tmp_path):
    d = docs()["R1__x__eqtl__QTD1__G1"]
    del d["method"]
    (jdir / "R1__x__eqtl__QTD1__G1.json").write_text(json.dumps(d))
    p = _agg(AGG, jdir, tmp_path / "m.tsv", "--with-method-columns")
    assert p.returncode != 0 and "R1__x__eqtl__QTD1__G1" in p.stderr and "no method" in p.stderr
    assert not (tmp_path / "m.tsv").exists()
    assert _agg(AGG, jdir, tmp_path / "d.tsv").returncode == 0  # default path unchanged


def _tierable(src, out):
    return subprocess.run([PY, "-B", "-m", "ta_r4.run_qtl_group_r4", "--qtl-arm", "QTL_A3", "--tierable-summary",
                           str(src), "--out", str(out)], capture_output=True, text=True, cwd=REPO_ROOT / "src/python")


def test_tierable_summary_keeps_only_coloc_susie(jdir, tmp_path):
    assert _agg(AGG, jdir, tmp_path / "m.tsv", "--with-method-columns").returncode == 0
    p = _tierable(tmp_path / "m.tsv", tmp_path / "tierable.tsv")
    assert p.returncode == 0, p.stderr
    t = _rows(tmp_path / "tierable.tsv")
    assert sorted(t) == ["R1__x__eqtl__QTD1__G1", "R1__x__eqtl__QTD2__G2"]
    assert {r["method"] for r in t.values()} == {"coloc_susie"}
    full = (tmp_path / "m.tsv").read_text().splitlines()
    assert (tmp_path / "tierable.tsv").read_text().splitlines()[0] == full[0]


def test_tierable_summary_refuses_an_empty_method(jdir, tmp_path):
    assert _agg(AGG, jdir, tmp_path / "m.tsv", "--with-method-columns").returncode == 0
    lines = (tmp_path / "m.tsv").read_text().splitlines()
    i = lines[0].split("\t").index("method")
    f = lines[1].split("\t")
    f[i] = ""
    lines[1] = "\t".join(f)
    (tmp_path / "m.tsv").write_text("\n".join(lines) + "\n")
    p = _tierable(tmp_path / "m.tsv", tmp_path / "tierable.tsv")
    assert p.returncode != 0 and "method" in p.stderr
    assert not (tmp_path / "tierable.tsv").exists()


def _tiers(summary, gwas, out):
    p = subprocess.run([PY, "-B", str(TIERS), "--input", str(summary), "--gwas-coloc", str(gwas), "--pph4-config",
                        str(REPO_ROOT / "config/pph4_thresholds.yaml"), "--output", str(out), "--sweep",
                        "--sweep-output", str(out) + ".sweep"], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    with open(out) as fh:
        return {(r["region"], r["ancestry"]): r for r in csv.DictReader(fh, delimiter="\t")}


def test_tiers_from_tierable_equal_tiers_from_full(jdir, tmp_path):
    """The old exclusion of fallback rows was implicit (blank PP.H4.abf); the explicit filter changes no tier.
    Measured side effects: all_supporting_sources narrows to sources with coloc_susie rows, and the sweep no longer
    counts a region without any coloc_susie row as Tier C."""
    assert _agg(AGG, jdir, tmp_path / "m.tsv", "--with-method-columns").returncode == 0
    assert _tierable(tmp_path / "m.tsv", tmp_path / "tierable.tsv").returncode == 0
    gwas = tmp_path / "gwas.tsv"
    gwas.write_text("row_id\tregion\tancestry\tmethod\tPP.H4.abf\nr1\tR1\tEUR\tcoloc_susie\t0.92\n"
                    "r2\tR2\tEUR\tcoloc_susie\t0.85\n")
    full = _tiers(tmp_path / "m.tsv", gwas, tmp_path / "t_full.tsv")
    tier = _tiers(tmp_path / "tierable.tsv", gwas, tmp_path / "t_tierable.tsv")
    assert set(full) == set(tier) == {("R1", "EUR"), ("R2", "EUR")}
    for k in full:
        for c in ("tier", "best_gwas_pph4", "best_qtl_pph4", "resolving_gene", "resolving_tissue",
                  "resolving_qtl_source"):
            assert full[k][c] == tier[k][c], (k, c)
    assert full[("R1", "EUR")]["tier"] == "Tier A" and full[("R2", "EUR")]["tier"] != "Tier A"
    assert full[("R1", "EUR")]["all_supporting_sources"] == "gtex_eqtl;gtex_sqtl"
    assert tier[("R1", "EUR")]["all_supporting_sources"] == "gtex_eqtl"
    assert full[("R2", "EUR")]["all_supporting_sources"] == "gtex_eqtl"
    assert tier[("R2", "EUR")]["all_supporting_sources"] == ""
    # Sweep mode: on the full summary R2 (no coloc_susie row, best PP.H4.abf NaN) counts as Tier C because NaN fails
    # every comparison in assign_tier; on the tierable summary it has no row and is not counted.
    sweep = {}
    for k in ("full", "tierable"):
        with open(tmp_path / f"t_{k}.tsv.sweep") as fh:
            sweep[k] = {r["threshold"]: r for r in csv.DictReader(fh, delimiter="\t")}
    assert set(sweep["full"]) == set(sweep["tierable"]) == {"0.5", "0.7", "0.8", "0.9"}
    for thr, f in sweep["full"].items():
        t = sweep["tierable"][thr]
        assert (f["n_tier_a"], f["n_tier_b"]) == (t["n_tier_a"], t["n_tier_b"]) == ("1", "0"), thr
        assert (f["n_tier_c"], t["n_tier_c"]) == ("1", "0"), thr


@pytest.mark.r4_heavy
def test_rendered_jobs_aggregate_with_method_columns_and_tier_the_tierable_file(rendered):
    """From the `$SMK -n -p` listing of a fixture lock repo (test_in_job_gate.rendered)."""
    import re

    _, _, js = rendered
    agg = [c for r, _, cs in js if r == "r4_qtl_aggregate" for c in cs]
    tiers = [c for r, _, cs in js if r == "r4_qtl_tiers" for c in cs]
    a = [c for c in agg if "aggregate_qtl_coloc.py" in c]
    assert len(a) == 1 and "--with-method-columns" in a[0]
    assert "--output data/r4/results/QTL_A3/qtl_coloc_summary.tsv" in a[0]
    t = [c for c in agg if "--tierable-summary" in c]
    assert len(t) == 1
    assert re.search(r"--tierable-summary data/r4/results/QTL_A3/qtl_coloc_summary.tsv "
                     r"--out data/r4/results/QTL_A3/qtl_coloc_summary_tierable.tsv", t[0])
    inp = [m.group(1) for c in tiers for m in [re.search(r"assign_tiers\.py --input (\S+)", c)] if m]
    assert inp == ["data/r4/results/QTL_A3/qtl_coloc_summary_tierable.tsv"]
