"""W3f 15.7g (review F3; Carter Q-F3 B, Q-F3B A): the PP.H4 threshold sweep applies the tier definitions to the
GWAS PP.H4 wherever a GWAS table is given; the no-table sweep is the logged legacy rule; NaN GWAS PP.H4 is
below_threshold under the r4-only flag."""
from __future__ import annotations

import copy
import csv
import importlib.util
import logging
import re
import shlex
import subprocess

import numpy as np
import pandas as pd
import pytest
import yaml

import assign_tiers as T
from ta_r4 import run_qtl_group_r4 as Q

from .conftest import REPO_ROOT
from .test_in_job_gate import rendered  # noqa: F401  (module-scoped dry-run fixture)

PY = "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11"
SCRIPT = REPO_ROOT / "src/python/assign_tiers.py"
PRE_157G_REF = "62353dbe"  # HEAD at the start of 15.7g; assign_tiers.py as last changed in 8fcade77
TIERS = ("Tier A", "Tier B", "Tier C")
NAN_LOG = re.compile(r"NaN-GWAS groups: (\d+) ")


@pytest.fixture(scope="module")
def cfg():
    with open(REPO_ROOT / "config/pph4_thresholds.yaml") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def old(tmp_path_factory):
    src = subprocess.run(["git", "show", f"{PRE_157G_REF}:src/python/assign_tiers.py"], cwd=REPO_ROOT, check=True,
                         capture_output=True, text=True).stdout
    p = tmp_path_factory.mktemp("pre157g") / "assign_tiers_pre157g.py"
    p.write_text(src)
    spec = importlib.util.spec_from_file_location("assign_tiers_pre157g", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, p


def _val(rng, p_nan):
    if rng.random() < p_nan:
        return np.nan
    if rng.random() < 0.2:
        return float(rng.choice([0.5, 0.7, 0.8, 0.9]))
    return float(rng.uniform(0, 1))


def frames(seed):
    """(qtl, gwas) with all-NaN groups on both sides, regions on one side only, two ancestries."""
    rng = np.random.default_rng(seed)
    q, g = [], []
    for r in range(12):
        for anc in ("EUR", "AFR"):
            if rng.random() < 0.8:
                all_nan = rng.random() < 0.15
                for k in range(int(rng.integers(1, 5))):
                    q.append({"region": f"R{r}", "ancestry": anc, "qtl_source": str(rng.choice(["gtex_eqtl", "gtex_sqtl"])),
                              "tissue": f"t{k}", "gene_id": f"G{r}_{k}",
                              "PP.H4.abf": np.nan if all_nan else _val(rng, 0.2)})
            if rng.random() < 0.8:
                all_nan = rng.random() < 0.2
                for k in range(int(rng.integers(1, 4))):
                    g.append({"row_id": f"p{r}_{anc}_{k}", "region": f"R{r}", "ancestry": anc, "method": "coloc_susie",
                              "PP.H4.abf": np.nan if all_nan else _val(rng, 0.15)})
    g.append({"row_id": "pnan", "region": "RNAN", "ancestry": "EUR", "method": "none", "PP.H4.abf": np.nan})
    q.append({"region": "RNAN", "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "t", "gene_id": "G",
              "PP.H4.abf": 0.95})
    return pd.DataFrame(q), pd.DataFrame(g)


def _full_counts(tier_df, ancestries):
    return {a: tuple(int(((tier_df["ancestry"] == a) & (tier_df["tier"] == t)).sum()) if len(tier_df) else 0
                     for t in TIERS) for a in ancestries}


def _sweep_counts(sw, t):
    s = sw[sw["threshold"] == t]
    return {r["ancestry"]: (int(r["n_tier_a"]), int(r["n_tier_b"]), int(r["n_tier_c"])) for _, r in s.iterrows()}


def _sweep(q, g, cfg, nan_below=False):
    return T.sweep_tiers(q, cfg["sweep_values"], tier_b_min=cfg["tier_definitions"]["tier_b"]["min_pph4_qtl"],
                         gwas_best=T.best_gwas(g), nan_below=nan_below)


def _write(df, p):
    df.to_csv(p, sep="\t", index=False)
    return p


def _cli(script, *args):
    return subprocess.run([PY, "-B", str(script), *map(str, args)], capture_output=True, text=True)


def test_codex_example_is_below_threshold(cfg):
    q = pd.DataFrame([{"region": "R1", "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "Lung",
                       "gene_id": "G1", "PP.H4.abf": 0.9}])
    g = pd.DataFrame([{"region": "R1", "ancestry": "EUR", "PP.H4.abf": 0.1}])
    sw = _sweep(q, g, cfg)
    for t in cfg["sweep_values"]:
        assert _sweep_counts(sw, t) == {"EUR": (0, 0, 0)}, t
    assert T.assign_tiers_full(q, g, cfg)["tier"].tolist() == ["below_threshold"]


def test_sweep_at_primary_equals_full_mode_counts(cfg):
    for seed in range(25):
        q, g = frames(seed)
        for nb in (False, True):
            full = T.assign_tiers_full(q, g, cfg, nan_below=nb)
            sw = _sweep(q, g, cfg, nan_below=nb)
            anc = set(sw["ancestry"])
            assert set(full["ancestry"]) <= anc
            assert _sweep_counts(sw, cfg["primary_threshold"]) == _full_counts(full, anc), (seed, nb)


def test_sweep_equals_full_mode_at_every_threshold(cfg):
    for seed in range(25):
        q, g = frames(seed)
        for nb in (False, True):
            sw = _sweep(q, g, cfg, nan_below=nb)
            anc = set(sw["ancestry"])
            for t in cfg["sweep_values"]:
                c = copy.deepcopy(cfg)
                c["primary_threshold"] = t
                assert _sweep_counts(sw, t) == _full_counts(T.assign_tiers_full(q, g, c, nan_below=nb), anc), \
                    (seed, nb, t)


def test_region_with_gwas_but_no_qtl_row_is_tier_c(cfg):
    q = pd.DataFrame([{"region": "R1", "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "Lung",
                       "gene_id": "G1", "PP.H4.abf": 0.9}])
    g = pd.DataFrame([{"region": "R1", "ancestry": "EUR", "PP.H4.abf": 0.92},
                      {"region": "R2", "ancestry": "EUR", "PP.H4.abf": 0.85}])
    sw = _sweep(q, g, cfg)
    want = {0.5: (1, 0, 1), 0.7: (1, 0, 1), 0.8: (1, 0, 1), 0.9: (1, 0, 0)}
    assert {t: _sweep_counts(sw, t)["EUR"] for t in cfg["sweep_values"]} == want


def _nan_frames():
    q = pd.DataFrame([{"region": r, "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "Lung", "gene_id": "G",
                       "PP.H4.abf": 0.9} for r in ("R1", "R2", "R3")])
    g = pd.DataFrame([{"region": "R1", "ancestry": "EUR", "PP.H4.abf": 0.95},
                      {"region": "R2", "ancestry": "EUR", "PP.H4.abf": np.nan},
                      {"region": "R3", "ancestry": "EUR", "PP.H4.abf": np.nan},
                      {"region": "R3", "ancestry": "EUR", "PP.H4.abf": np.nan}])
    return q, g


def test_nan_gwas_is_below_threshold_in_full_mode_under_the_flag(cfg):
    q, g = _nan_frames()
    off = dict(zip(T.assign_tiers_full(q, g, cfg)["region"], T.assign_tiers_full(q, g, cfg)["tier"]))
    on = T.assign_tiers_full(q, g, cfg, nan_below=True)
    assert off == {"R1": "Tier A", "R2": "Tier A", "R3": "Tier A"}  # the defect, kept without the flag
    assert dict(zip(on["region"], on["tier"])) == {"R1": "Tier A", "R2": "below_threshold", "R3": "below_threshold"}
    assert T.assign_tier(np.nan, 0.9, 0.8) == "Tier A"
    assert T.assign_tier(np.nan, 0.9, 0.8, nan_below=True) == "below_threshold"
    assert T.assign_tier(None, 0.9, 0.8, nan_below=True) == "below_threshold"
    assert T.assign_tier(0.95, 0.9, 0.8, nan_below=True) == "Tier A"


def test_nan_gwas_is_below_threshold_in_the_sweep_under_the_flag(cfg):
    q, g = _nan_frames()
    on, off = _sweep(q, g, cfg, nan_below=True), _sweep(q, g, cfg)
    for t in cfg["sweep_values"]:
        assert _sweep_counts(on, t) == {"EUR": (1, 0, 0)}, t
        assert _sweep_counts(off, t) == {"EUR": (3, 0, 0)}, t


def test_cli_with_gwas_table_uses_it_in_the_sweep(cfg, tmp_path):
    """Track B / r4 call shape: --gwas-coloc --sweep; tier_b_min is read from the config."""
    q = _write(pd.DataFrame([{"region": "R1", "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "Lung",
                              "gene_id": "G1", "PP.H4.abf": 0.9},
                             {"region": "R2", "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "Lung",
                              "gene_id": "G2", "PP.H4.abf": 0.55}]), tmp_path / "q.tsv")
    g = _write(pd.DataFrame([{"region": "R1", "ancestry": "EUR", "PP.H4.abf": 0.1},
                             {"region": "R2", "ancestry": "EUR", "PP.H4.abf": 0.95}]), tmp_path / "g.tsv")
    c = copy.deepcopy(cfg)
    c["tier_definitions"]["tier_b"]["min_pph4_qtl"] = 0.6
    (tmp_path / "c.yaml").write_text(yaml.safe_dump(c))
    for conf, r2 in ((REPO_ROOT / "config/pph4_thresholds.yaml", (0, 1, 0)), (tmp_path / "c.yaml", (0, 0, 1))):
        p = _cli(SCRIPT, "--input", q, "--gwas-coloc", g, "--pph4-config", conf, "--output", tmp_path / "t.tsv",
                 "--sweep", "--sweep-output", tmp_path / "s.tsv")
        assert p.returncode == 0, p.stderr
        sw = pd.read_csv(tmp_path / "s.tsv", sep="\t")
        assert _sweep_counts(sw, 0.8) == {"EUR": r2}, conf  # R1 (GWAS 0.1, QTL 0.9) is below threshold
        assert "legacy" not in p.stderr


def test_gwas_less_sweep_unchanged_and_warns(cfg, old, tmp_path, caplog):
    mod, oldp = old
    for seed in range(25):
        q, _ = frames(seed)
        want = mod.sweep_tiers(q, cfg["sweep_values"])
        for kw in ({}, {"nan_below": True}):
            caplog.clear()
            with caplog.at_level(logging.WARNING, logger="assign_tiers"):
                got = T.sweep_tiers(q, cfg["sweep_values"], **kw)
            assert got.to_csv(sep="\t", index=False) == want.to_csv(sep="\t", index=False), (seed, kw)
            assert any("legacy" in r.getMessage() and "QTL PP.H4 as the GWAS PP.H4" in r.getMessage()
                       for r in caplog.records if r.levelno == logging.WARNING), (seed, kw)
    q = _write(frames(3)[0], tmp_path / "q.tsv")
    conf = REPO_ROOT / "config/pph4_thresholds.yaml"
    a = _cli(oldp, "--input", q, "--pph4-config", conf, "--output", tmp_path / "o.tsv", "--sweep",
             "--sweep-output", tmp_path / "o_s.tsv")
    assert a.returncode == 0, a.stderr
    for extra in ((), ("--nan-gwas-below-threshold",)):
        b = _cli(SCRIPT, "--input", q, "--pph4-config", conf, "--output", tmp_path / "n.tsv", "--sweep",
                 "--sweep-output", tmp_path / "n_s.tsv", *extra)
        assert b.returncode == 0, b.stderr
        assert (tmp_path / "n_s.tsv").read_bytes() == (tmp_path / "o_s.tsv").read_bytes(), extra
        assert "legacy" in b.stderr


def test_full_mode_without_the_flag_is_byte_identical(cfg, old, tmp_path):
    mod, oldp = old
    for seed in range(25):
        q, g = frames(seed)
        neg = None if seed % 2 else pd.DataFrame([{"region": "N1", "ancestry": "EUR", "PP.H4.abf": 0.3,
                                                   "gene_id": "GN", "qtl_source": "gtex_eqtl", "neg_ctrl_set": "s"}])
        for gg in (g, g.iloc[0:0]):
            a = mod.assign_tiers_full(q, gg, cfg, neg).to_csv(sep="\t", index=False)
            b = T.assign_tiers_full(q, gg, cfg, neg).to_csv(sep="\t", index=False)
            assert a == b, seed
    q, g = frames(7)
    _write(q, tmp_path / "q.tsv")
    _write(g, tmp_path / "g.tsv")
    for s, o in ((oldp, "o.tsv"), (SCRIPT, "n.tsv")):
        p = _cli(s, "--input", tmp_path / "q.tsv", "--gwas-coloc", tmp_path / "g.tsv", "--pph4-config",
                 REPO_ROOT / "config/pph4_thresholds.yaml", "--output", tmp_path / o, "--sweep")
        assert p.returncode == 0, p.stderr
    assert (tmp_path / "n.tsv").read_bytes() == (tmp_path / "o.tsv").read_bytes()


def test_nan_gwas_group_count_is_logged(cfg, tmp_path, caplog):
    q, g = _nan_frames()
    for nb in (False, True):
        caplog.clear()
        with caplog.at_level(logging.INFO, logger="assign_tiers"):
            T.assign_tiers_full(q, g, cfg, nan_below=nb)
            _sweep(q, g, cfg, nan_below=nb)
        n = [int(m.group(1)) for r in caplog.records for m in [NAN_LOG.search(r.getMessage())] if m]
        assert n == [2, 2], (nb, n)
    _write(q, tmp_path / "q.tsv")
    _write(g, tmp_path / "g.tsv")
    conf = REPO_ROOT / "config/pph4_thresholds.yaml"
    for extra, want in (((), "2"), (("--nan-gwas-below-threshold",), "2"), (("--no-gwas",), "0")):
        gw = [] if extra == ("--no-gwas",) else ["--gwas-coloc", tmp_path / "g.tsv"]
        fl = [] if extra == ("--no-gwas",) else list(extra)
        p = _cli(SCRIPT, "--input", tmp_path / "q.tsv", *gw, "--pph4-config", conf, "--output", tmp_path / "t.tsv",
                 "--sweep", "--sweep-output", tmp_path / "s.tsv", *fl)
        assert p.returncode == 0, p.stderr
        assert NAN_LOG.findall(p.stderr) and set(NAN_LOG.findall(p.stderr)) == {want}, (extra, p.stderr)


@pytest.mark.r4_heavy
def test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order(rendered):  # noqa: F811
    assert Q.tiers_argv("S", "G", "P", "T", "W", py="PY") == [
        "PY", "src/python/assign_tiers.py", "--input", "S", "--gwas-coloc", "G", "--pph4-config", "P", "--output", "T",
        "--sweep", "--sweep-output", "W", "--nan-gwas-below-threshold"]
    _, _, js = rendered
    cmds = [c for r, _, cs in js if r == "r4_qtl_tiers" for c in cs if "assign_tiers.py" in c]
    assert len(cmds) == 1
    py = re.search(r"(\S+) src/python/assign_tiers\.py", cmds[0]).group(1)
    d = "data/r4/results/QTL_A3"
    want = shlex.join(Q.tiers_argv(f"{d}/qtl_coloc_summary_tierable.tsv", f"{d}/gwas_coloc_for_tiers.tsv",
                                   "config/pph4_thresholds.yaml", f"{d}/qtl_tiers.tsv", f"{d}/qtl_tiers_sweep.tsv",
                                   py=py))
    assert cmds[0].startswith(want + ")"), cmds[0]
