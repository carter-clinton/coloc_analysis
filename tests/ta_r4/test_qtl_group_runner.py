"""W3e Task 2: ta_r4.run_qtl_group_r4 (D-02 on the QTL layer, D-06, D-22) and the ta_r4_qtl.smk group gate.

Fixture group (fixtures/qtl_group_fixture.py): traits tA (signal) / tB (null) x eQTL features f1 (signal) / f2 (null).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures import qtl_group_fixture as F

from ta_r4 import paths
from ta_r4 import run_qtl_group_r4 as G
from ta_r4.harmonize_qtl_r4 import harmonized_path, manifest_rows

SMK = "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake"
F1, F2 = F.FEATURES
ID = {(t, f): f"{F.REGION}__EUR__{t}__eqtl__{F.TISSUE}__{f}" for t in F.TRAITS for f in F.FEATURES}
EXPECT = {("tA", F1): ("coloc_susie", None), ("tA", F2): ("fallback_abf", "qtl_n_cs==0"),
          ("tB", F1): ("fallback_abf", "gwas_n_cs==0"), ("tB", F2): ("fallback_abf", "gwas_n_cs==0&qtl_n_cs==0")}


def _row(trait="tA", feature=F1, region=F.REGION):
    return {"qtl_row_id": ID[(trait, feature)], "region_safe": region, "trait": trait, "source": "eqtl",
            "tissue": F.TISSUE, "qtd": F.QTD, "gene_id": feature, "molecular_trait_id": feature}


# ---- quick: argv, priors, reasons, coverage ------------------------------------------------------------------------
def test_qtl_arm_mapping():
    assert {q: G.fit_arm(q) for q in G.QTL_ARMS} == {"QTL_A3": "A3_1kg", "QTL_A2": "A2_identity",
                                                     "QTL_legacy": "repro_routeL"}
    assert {a: G.qtl_arm_for(a) for a in ("A3_1kg", "A2_identity", "repro_routeL", "A3_ukb", "repro_routeC")} == \
        {"A3_1kg": "QTL_A3", "A2_identity": "QTL_A2", "repro_routeL": "QTL_legacy", "A3_ukb": None,
         "repro_routeC": None}


def test_legacy_argv_is_the_exact_pre_fix_argv():
    r = _row()
    got = G.qtl_command("QTL_legacy", r, "OUT", 1.0)
    want = ["Rscript", "src/snakemake/scripts/run_qtl_coloc.R",
            "--gwas-fit", "data/r4/results/repro_routeL/fine_mapping/susie/tA.EUR.FIX_1.fit.rds",
            "--qtl-sumstats", f"data/r4/qtl/harmonized/eqtl/{F.QTD}/{F1}/FIX_1.harmonized.tsv.gz",
            "--ld-matrix", "data/r4/ld/legacy_repro/EUR/FIX_1.rds", "--qtl-source", "gtex_eqtl",
            "--tissue", F.TISSUE, "--gene-id", F1, "--region", "FIX_1", "--ancestry", "EUR", "--sdy", "1.0",
            "--sample-size", "670", "--policy", "config/susie_policy.yaml", "--ld-allele-join", "false",
            "--output", "OUT"]
    assert got == want


@pytest.mark.parametrize("qtl_arm, panel", [("QTL_A3", "data/r4/ld/EUR_1kg_r4/FIX_1.rds"),
                                            ("QTL_A2", "data/r4/ld/EUR_identity_r4/FIX_1.rds")])
def test_fixed_arms_argv(qtl_arm, panel):
    got = G.qtl_command(qtl_arm, _row(), "OUT", 1.0)
    fa = G.fit_arm(qtl_arm)
    assert got[got.index("--gwas-fit") + 1] == f"data/r4/results/{fa}/fine_mapping/susie/tA.EUR.FIX_1.fit.rds"
    assert got[got.index("--ld-matrix") + 1] == panel
    assert got[got.index("--ld-allele-join") + 1] == "true"
    assert got[got.index("--variant-list") + 1] == "data/r4/ld/variants_r4/FIX_1.tsv"
    assert got[got.index("--qtl-orient") + 1] == "true"
    assert got[-2:] == ["--output", "OUT"]


def test_fallback_argv_uses_the_arm_flags():
    leg = G.abf_command("QTL_legacy", _row(), "FIX_1", "OUT", 1.0, "qtl_n_cs==0")
    a3 = G.abf_command("QTL_A3", _row(), "FIX_1", "OUT", 1.0, "qtl_n_cs==0")
    assert leg[leg.index("--ld-allele-join") + 1] == "false" and leg[leg.index("--qtl-orient") + 1] == "false"
    assert "--variant-list" not in leg
    assert a3[a3.index("--ld-allele-join") + 1] == "true" and a3[a3.index("--qtl-orient") + 1] == "true"
    assert a3[a3.index("--variant-list") + 1] == "data/r4/ld/variants_r4/FIX_1.tsv"
    for c in (leg, a3):
        assert c[c.index("--mode") + 1] == "qtl_abf" and c[c.index("--p12-key") + 1] == "p12_primary"
        assert c[c.index("--priors") + 1] == "config/ta_r4/coloc_priors.yaml"


def test_priors_equal_yaml_and_refuse_a_change(tmp_path):
    y = yaml.safe_load(open(REPO_ROOT / "config/ta_r4/coloc_priors.yaml"))
    assert G.priors(REPO_ROOT / "config/ta_r4/coloc_priors.yaml") == {
        "p1": y["p1"], "p2": y["p2"], "p12": y["p12_primary"], "overlap_min": y["overlap_min"],
        "trim_by_posterior": y["trim_by_posterior"], "p12_key": "p12_primary"}
    bad = tmp_path / "pri.yaml"
    bad.write_text(yaml.safe_dump({**y, "p12_primary": 1e-5}))
    with pytest.raises(ValueError, match="coloc.susie defaults"):
        G.priors(bad)


@pytest.mark.parametrize("d, want", [({"n_cs_gwas": 0, "n_cs_qtl": 2}, "gwas_n_cs==0"),
                                     ({"n_cs_gwas": 3, "n_cs_qtl": 0}, "qtl_n_cs==0"),
                                     ({"n_cs_gwas": 0, "n_cs_qtl": 0}, "gwas_n_cs==0&qtl_n_cs==0")])
def test_fallback_reason(d, want):
    assert G.fallback_reason(d) == want


def test_fallback_reason_refuses_nonzero():
    with pytest.raises(ValueError):
        G.fallback_reason({"status": "no_qtl_cs", "n_cs_gwas": 1, "n_cs_qtl": 1})


def test_coverage_negative_control(tmp_path):
    ids = list(ID.values())
    for i in ids:
        (tmp_path / f"{i}.json").write_text("{}")
    (tmp_path / f"{F.REGION}__EUR__tA__sqtl__{F.TISSUE}__x.json").write_text("{}")  # other group: ignored
    assert G.coverage(tmp_path, ids) == ([], [])
    (tmp_path / f"{ID[('tB', F2)]}.json").unlink()
    assert G.coverage(tmp_path, ids) == ([ID[("tB", F2)]], [])
    extra = f"{F.REGION}__EUR__tC__eqtl__{F.TISSUE}__{F1}"
    (tmp_path / f"{extra}.json").write_text("{}")
    assert G.coverage(tmp_path, ids) == ([ID[("tB", F2)]], [extra])


def test_real_manifest_ids_have_six_fields():
    rows = manifest_rows(REPO_ROOT / "config/ta_r4/qtl_manifest.tsv")
    bad = [r["qtl_row_id"] for r in rows
           if r["qtl_row_id"].split("__") != [r["region_safe"], r["ancestry"], r["trait"], r["source"], r["tissue"],
                                               r["molecular_trait_id"]]]
    assert bad == []


def test_region_ids_cover_the_qtl_regions():
    ids = G.region_ids(REPO_ROOT / "config/ta_r4/regions_r4.csv")
    rows = manifest_rows(REPO_ROOT / "config/ta_r4/qtl_manifest.tsv")
    assert {r["region_safe"] for r in rows} <= set(ids)
    assert ids["BMI_5q13_3"] == "BMI_5q13.3"


def test_gwas_coloc_table(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pm = tmp_path / "pm.tsv"
    pm.write_text("row_id\tancestry\tregion_safe\tadmissible\n"
                  "R1__EUR__a_vs_b\tEUR\tR1\ttrue\nR1__AFR__a_vs_b\tAFR\tR1\ttrue\n"
                  "R2__EUR__a_vs_b\tEUR\tR2\ttrue\nR1__EUR__c_vs_d\tEUR\tR1\tfalse\n")
    qm = tmp_path / "qm.tsv"
    qm.write_text("region_safe\nR1\n")
    p = Path(paths.coloc_json("A3_1kg", "R1__EUR__a_vs_b", "p12_primary"))
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"method": "fallback_abf", "pp_h4": 0.25}))
    assert G.coloc_inputs("QTL_A3", pair_manifest=pm, manifest=qm) == [str(p)]
    n = G.gwas_coloc_table("QTL_A3", "t.tsv", pair_manifest=pm, manifest=qm)
    assert n == 1
    assert Path("t.tsv").read_text() == ("row_id\tregion\tancestry\tmethod\tPP.H4.abf\n"
                                         "R1__EUR__a_vs_b\tR1\tEUR\tfallback_abf\t0.25\n")


# ---- heavy: the group run on the fixture --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    root = F.build(tmp_path_factory.mktemp("qtl_group") / "root")
    old, env = os.getcwd(), os.environ.get("PATH")
    os.environ["PATH"] = F.r_env()["PATH"]
    os.chdir(root)
    try:
        out = {a: G.run_group(a, F.REGION, "eqtl", F.QTD, manifest="config/ta_r4/qtl_manifest.tsv")
               for a in ("QTL_A3", "QTL_legacy")}
    finally:
        os.chdir(old)
        os.environ["PATH"] = env
    return root, out


def _docs(root, qtl_arm):
    return {k: json.loads((root / G.out_dir(qtl_arm) / f"{i}.json").read_text()) for k, i in ID.items()}


@pytest.mark.r4_heavy
@pytest.mark.parametrize("qtl_arm", ["QTL_A3", "QTL_legacy"])
def test_group_methods_reasons_and_coverage(runs, qtl_arm):
    root, out = runs
    counts, missing, extra = out[qtl_arm]
    assert (counts, missing, extra) == ({"coloc_susie": 1, "fallback_abf": 3}, [], [])
    docs = _docs(root, qtl_arm)
    for k, (method, reason) in EXPECT.items():
        d = docs[k]
        assert (d["method"], d["fallback_reason"], d["qtl_arm"]) == (method, reason, qtl_arm), k
        if method == "coloc_susie":
            assert d["status"] == "success" and d["n_cs_gwas"] > 0 and d["n_cs_qtl"] > 0
            assert d["pp_h4"] == d["summary"]["PP.H4.abf"] and "fallback" not in d
        else:
            fb = d["fallback"]
            assert d["status"] in ("no_qtl_cs", "no_gwas_cs") and d["summary"] == []
            assert (fb["method"], fb["mode"], fb["fallback_reason"]) == ("fallback_abf", "qtl_abf", reason)
            assert fb["n_snps"] == d["n_snps_overlap"] and d["pp_h4"] == fb["pp_h4"]
            assert fb["p12"] == d["priors"]["p12"] == 5e-6
    assert all(set(d["argv"][:2]) == {"Rscript", G.QTL_SCRIPT} for d in docs.values())


@pytest.mark.r4_heavy
def test_legacy_rows_record_the_pre_fix_argv(runs):
    root, _ = runs
    for k, d in _docs(root, "QTL_legacy").items():
        a = d["argv"]
        assert a[a.index("--ld-allele-join") + 1] == "false"
        assert "--qtl-orient" not in a and "--variant-list" not in a
        assert not any(x.startswith("qtl_orient") for x in d)
        assert a == G.qtl_command("QTL_legacy", _row(*k), a[-1], 1.0)


@pytest.mark.r4_heavy
def test_fixed_rows_carry_orientation_counters(runs):
    root, _ = runs
    for d in _docs(root, "QTL_A3").values():
        a = d["argv"]
        assert a[a.index("--qtl-orient") + 1] == "true"
        c = [d[f"qtl_orient_{k}"] for k in ("exact", "flipped", "dropped_palindromic", "dropped_mismatch",
                                            "dropped_unparseable")]
        assert sum(c) == d["ld_panel_overlap"] and c[0] + c[1] == d["n_snps_overlap"]
        assert c[1] == len(F.SWAP) and c[2] == len(F.PAL)


@pytest.mark.r4_heavy
def test_deleted_output_fails_coverage(runs):
    root, _ = runs
    odir = root / G.out_dir("QTL_A3")
    victim = odir / f"{ID[('tA', F2)]}.json"
    keep = victim.read_bytes()
    victim.unlink()
    try:
        assert G.coverage(odir, list(ID.values())) == ([ID[("tA", F2)]], [])
    finally:
        victim.write_bytes(keep)
    assert G.coverage(odir, list(ID.values())) == ([], [])


def _group_cli(root, odir, done, env):
    return subprocess.run([sys.executable, "-m", "ta_r4.run_qtl_group_r4",
                           "--qtl-arm", "QTL_A3", "--region", F.REGION, "--source", "eqtl", "--qtd", F.QTD,
                           "--manifest", "config/ta_r4/qtl_manifest.tsv", "--out-dir", str(odir), "--done", str(done)],
                          cwd=root, capture_output=True, text=True, env={**env, "PYTHONPATH": str(REPO_ROOT / "src/python")})


@pytest.mark.r4_heavy
def test_cli_exit_1_names_the_missing_row(runs, tmp_path):
    """A group whose run_qtl_coloc.R call fails for one feature: that row fails, coverage exits 1 naming it.
    (Since W3f 15.2 an absent harmonized file fails input verification first: test_cli_absent_harmonized_file_...)"""
    root, _ = runs
    wrap = tmp_path / "bin"
    wrap.mkdir()
    (wrap / "Rscript").write_text(f'#!/bin/bash\nfor a in "$@"; do [ "$a" = {F2} ] && exit 3; done\n'
                                  f'exec {F.RSCRIPT} "$@"\n')
    (wrap / "Rscript").chmod(0o755)
    env = F.r_env()
    p = _group_cli(root, tmp_path / "out", tmp_path / "g.done", {**env, "PATH": f"{wrap}:{env['PATH']}"})
    assert p.returncode == 1, p.stderr[-2000:]
    assert "COVERAGE FAILED missing=2 extra=0" in p.stderr
    for t in F.TRAITS:
        assert f"missing {ID[(t, F2)]}" in p.stderr
    assert not (tmp_path / "g.done").exists()


@pytest.mark.r4_heavy
def test_cli_absent_harmonized_file_fails_input_verification(runs, tmp_path):
    root, _ = runs
    rel = harmonized_path("eqtl", F.QTD, F2, F.REGION)
    keep = (root / rel).read_bytes()
    (root / rel).unlink()
    try:
        p = _group_cli(root, tmp_path / "out", tmp_path / "g.done", F.r_env())
    finally:
        (root / rel).write_bytes(keep)
    assert p.returncode == 1 and "InputIntegrityError" in p.stderr and rel in p.stderr, p.stderr[-2000:]
    assert not (tmp_path / "g.done").exists() and not (tmp_path / "out").exists()


@pytest.mark.r4_heavy
def test_coloc_susie_defaults_match_the_yaml_guard():
    """run_qtl_coloc.R calls coloc.susie() without priors: the package defaults must be the values the runner records."""
    code = ('f <- formals(coloc::coloc.bf_bf); cat(f$p1, f$p2, f$p12, f$overlap.min, f$trim_by_posterior)')
    p = subprocess.run([F.RSCRIPT, "-e", code], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    p1, p2, p12, om, trim = p.stdout.split()
    assert {"p1": float(p1), "p2": float(p2), "p12": float(p12), "overlap_min": float(om),
            "trim_by_posterior": trim == "TRUE"} == G.COLOC_SUSIE_DEFAULTS


# ---- heavy: Snakemake gate ------------------------------------------------------------------------------------------
@pytest.mark.r4_heavy
def test_qtl_A3_group_refused_without_lock(tmp_path):
    from .fixtures.make_fixture_repo import make_fixture_repo
    repo = make_fixture_repo(tmp_path)
    target = G.done_path("QTL_A3", "SH2B3_12q24", "eqtl", "QTD000116")
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_A3_1kg.yaml"]
    p = subprocess.run([SMK, target, "-s", "Snakefile.ta_r4", "-d", ".", "-n", "--configfile", *cfg], cwd=repo,
                       capture_output=True, text=True)
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "LockGateError" in out and "lock record absent" in out, out[-2000:]
    assert "r4_qtl_group" in out


@pytest.mark.r4_heavy
def test_qtl_rules_exist_only_in_their_fit_arm_invocation():
    def rules(stage, arm):
        p = subprocess.run(["bash", "bin/r4_fire.sh", stage, arm, "--list"], cwd=REPO_ROOT, capture_output=True,
                           text=True)
        assert p.returncode == 0, p.stderr[-2000:]
        return set(p.stdout.split())
    qtl = {"r4_qtl_group", "r4_qtl_aggregate", "r4_qtl_tiers", "r4_qtl_all"}
    assert qtl <= rules("repro", "repro_routeL") and "r4_qtl_harmonize" in rules("repro", "repro_routeL")
    other = rules("repro", "repro_routeC")
    assert not qtl & other and "r4_qtl_harmonize" in other
