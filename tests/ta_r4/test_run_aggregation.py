"""run_aggregation.py: the single entry point for every R4 table, fixture-tested before the lock (W3d)."""
from __future__ import annotations

import ast
import builtins
import copy
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import doc, manifest, mrow

PY = "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11"
SRC = REPO_ROOT / "src/python/ta_r4/run_aggregation.py"
MAN_REL = ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests"
TABLES = ("branch_outcomes", "e1_paired_delta", "e2_agreement_sweep", "e3_reclassification", "e4_finemap_structure",
          "e4_no_cs_rate", "e4_cross_purity", "e5_diagnostics", "e6_panel_contrast", "e7_frozen_vs_fixed",
          "e8_simulation_rates", "afr_secondary", "negative_controls", "qtl_layer", "min_abs_corr_sweep",
          "hla_exploratory", "table1_data")
PAIRS = [("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d"), ("bmi", "stroke"), ("t2d", "stroke")]
P12 = ("p12_primary", "p12_sensitivity")


def _w(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj))


def _fit(n_cs):
    return {"status": "ok", "credible_sets": {f"CS{i + 1}": [{"CHR": "1", "POS": i}] for i in range(n_cs)},
            "d3b_ld_z_consistency_s": 0.2, "d3_ld_quality": {"n_outliers": 1, "max_logLR": 2.0},
            "ld_allele_exact": 90, "ld_allele_flipped": 10, "L_saturated": False,
            "min_abs_corr_sweep": [{"min_abs_corr": 0.5, "n_CS": n_cs, "cs_sizes": [1] * n_cs}]}


def build_tree(root, nc_bump=0.0):
    """3 curated EUR regions (5 pairs) + 1 NC region (3 pairs); every EUR production arm and A1 matched/allvars,
    both p12 keys: complete coloc coverage."""
    root = Path(root)
    rows = [mrow(f"CUR{i}", "EUR", p) for i in range(3) for p in PAIRS]
    rows += [mrow("NC_ABO", "EUR", p, row_class="negative_control", nc_set="blood_group") for p in PAIRS[:3]]
    m = manifest(rows)
    (root / "config/ta_r4").mkdir(parents=True, exist_ok=True)
    m.to_csv(root / "config/ta_r4/pair_manifest.tsv", sep="\t", index=False)
    for n in ("decision_rules", "coloc_priors", "simulation"):
        dst = root / f"config/ta_r4/{n}.yaml"
        if not dst.exists():
            shutil.copy2(REPO_ROOT / f"config/ta_r4/{n}.yaml", dst)
    res = root / "data/r4/results"
    for j, r in enumerate(rows):
        nc = r["row_class"] == "negative_control"
        for k in P12:
            base = 0.3 + 0.03 * j + (0.01 if k == "p12_sensitivity" else 0)
            vals = {"A3_1kg": base, "A2_identity": min(base + 0.1 + 0.005 * j, 0.99) + (nc_bump if nc else 0),
                    "A1_matched": min(base + 0.05, 0.99) + (nc_bump if nc else 0), "A1_allvars": 0.5,
                    "A3_ukb": 0.4, "A3_ukb_isect": 0.4, "A3_1kg_isect": 0.4}
            for lab, h4 in vals.items():
                d = doc(r["row_id"], lab, k, h4)
                if lab.startswith("A1_"):
                    p = res / f"A1_EUR/coloc/{r['row_id']}.{lab.split('_', 1)[1]}.{k}.json"
                else:
                    p = res / f"{lab}/coloc/{r['row_id']}.{k}.json"
                _w(p, d)
        for arm in ("A3_1kg", "A2_identity"):
            for t in (r["trait_a"], r["trait_b"]):
                _w(res / f"{arm}/fine_mapping/susie/{t}.EUR.{r['region_safe']}.json", _fit(2))
    _w(res / "A3_ukb/fine_mapping/susie/asthma.EUR.HLA_6p21.json", _fit(3))
    _w(res / f"repro_sh2b3_r2/coloc/{rows[0]['row_id']}.p12_primary.json",
       dict(doc(rows[0]["row_id"], "repro_sh2b3_r2", "p12_primary", 0.99), p12=1e-5))  # default priors
    _w(res / "sim/CUR0.H3_r2_0.6.gen_1kg.tsv",
       "# status=ok\n# reps_override=NA\nregion\tscenario\tgen_panel\trep\tseed\tarm\tmethod\tpp_h0\tpp_h1\tpp_h2"
       "\tpp_h3\tpp_h4\tpp_h4_max\tn_cs_a\tn_cs_b\tcausal_a\tcausal_b\tr2_causal\n"
       "CUR0\tH3_r2_0.6\tgen_1kg\t1\t1\tA2\tcoloc_susie\t0\t0\t0\t0.1\t0.9\t0.9\t1\t1\t1:1\t1:2\t0.6\n"
       "CUR0\tH3_r2_0.6\tgen_1kg\t1\t1\tA3\tcoloc_susie\t0\t0\t0\t0.9\t0.1\t0.1\t1\t1\t1:1\t1:2\t0.6\n")
    _w(res / "sim/CUR1.H3_r2_0.9.gen_1kg.tsv", "# status=no_qualifying_pair\nregion\tscenario\tgen_panel\trep\tseed"
       "\tarm\tmethod\tpp_h0\tpp_h1\tpp_h2\tpp_h3\tpp_h4\tpp_h4_max\tn_cs_a\tn_cs_b\tcausal_a\tcausal_b\tr2_causal\n")
    for f in ("known_answer_W3a.tsv", "known_answer_sh2b3.tsv"):
        dst = root / MAN_REL / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / MAN_REL / f, dst)
    return m


def _run(repo, out, **kw):
    from ta_r4.run_aggregation import run_aggregation

    return run_aggregation(repo, out, **kw)


def _read(out, name):
    return pd.read_csv(Path(out) / f"{name}.tsv", sep="\t", comment="#")


# ------------------------------------------------------------------ gate / labels

def test_unlocked_writes_nothing_and_exits_2(tmp_path):
    build_tree(tmp_path / "repo")
    out = tmp_path / "out"
    assert _run(tmp_path / "repo", out) == 2
    assert not out.exists() or not any(out.iterdir())


def test_cli_exit_2_without_draft(tmp_path):
    build_tree(tmp_path / "repo")
    p = subprocess.run([PY, "-B", "-m", "ta_r4.run_aggregation", "--repo", str(tmp_path / "repo"), "--out",
                        str(tmp_path / "out")], capture_output=True, text=True, cwd=REPO_ROOT / "src/python")
    assert p.returncode == 2, p.stderr
    assert not (tmp_path / "out").exists() or not any((tmp_path / "out").iterdir())


def test_draft_writes_exactly_17_draft_tables(tmp_path):
    from ta_r4.run_aggregation import TABLES as T

    build_tree(tmp_path / "repo")
    out = tmp_path / "out"
    assert _run(tmp_path / "repo", out, draft=True) == 0
    assert T == TABLES
    assert sorted(p.name for p in out.iterdir()) == sorted(f"{t}.tsv" for t in TABLES)
    for t in TABLES:
        assert (out / f"{t}.tsv").read_text().splitlines()[0] == "# status=DRAFT", t


def final_repo(tmp_path):
    """build_tree in a fixture lock repo with a matching W4a-T3 fixture sign-off: output_status FINAL."""
    import datetime as dt

    from ta_r4.r4_lock_gate import SIGNOFF_REL
    from ta_r4.signoff import canonical_sha256, record_signoff
    from .fixtures.make_fixture_repo import git, make_fixture_repo, write_fixture_lock

    repo = make_fixture_repo(tmp_path)
    build_tree(repo)
    git(repo, "add", "config/ta_r4/pair_manifest.tsv", f"{MAN_REL}/known_answer_W3a.tsv", f"{MAN_REL}/known_answer_sh2b3.tsv")
    git(repo, "commit", "-q", "-m", "fixture manifest")
    write_fixture_lock(repo)
    dr = yaml.safe_load((repo / "config/ta_r4/decision_rules.yaml").read_text())
    pri = yaml.safe_load((repo / "config/ta_r4/coloc_priors.yaml").read_text())
    raw = [f"carter-approved {dt.date.today().isoformat()}", f"p12_primary: {pri['p12_primary']}",
           f"kappa_cut: {dr['kappa_cut']}", f"n_both_min: {dr['n_both_min']}"]
    raw += [f"partial_rule.{k}: {v}" for k, v in dr["partial_rule"].items()]
    raw += [f"confirmatory_sha256: {canonical_sha256(dr['confirmatory'])}", "draft: approved"]
    record_signoff("W4a-T3", "\n".join(raw) + "\n", min_date="2026-10-01", signoff_dir=repo / SIGNOFF_REL)
    return repo


def test_final_label_with_fixture_lock_and_signoff(tmp_path):
    repo = final_repo(tmp_path)
    out = tmp_path / "out"
    assert _run(repo, out) == 0
    assert all((out / f"{t}.tsv").read_text().startswith("# status=FINAL\n") for t in TABLES)
    shutil.rmtree(out)
    assert _run(repo, out, draft=True) == 0
    assert all((out / f"{t}.tsv").read_text().startswith("# status=DRAFT\n") for t in TABLES)


# ------------------------------------------------------------------ content

@pytest.fixture(scope="module")
def drafted(tmp_path_factory):
    root = tmp_path_factory.mktemp("agg")
    m = build_tree(root / "repo")
    assert _run(root / "repo", root / "out", draft=True) == 0
    return m, root


def test_branch_outcomes_two_confirmatory_rows(drafted):
    from ta_r4.branch_classifier import classify
    from ta_r4.estimands import contrast_stats, load_rows, load_rules

    m, root = drafted
    b = _read(root / "out", "branch_outcomes")
    assert b.contrast.tolist() == ["A1_matched_vs_A3_1kg", "A2_identity_vs_A3_1kg"]
    assert set(b.p12_key) == {"p12_primary"}
    for col in ("n_rows", "n_both", "median_delta", "ci_lo", "ci_hi", "sign_p", "mcnemar_b", "mcnemar_c",
                "mcnemar_p", "kappa", "observed_agreement", "n_both_ok", "ci", "mcnemar", "kappa_ok", "branch", "via"):
        assert col in b.columns
    rules = load_rules(root / "repo")
    rows = load_rows(root / "repo")
    for r in b.itertuples():
        s = contrast_stats(rows, r.x, r.ref, rules, m)
        assert (r.branch, r.via) == classify(s, rules)
        assert r.n_rows == 15 and r.n_both == s["n_both"]
    for t in TABLES:
        if t != "branch_outcomes":
            assert "branch" not in _read(root / "out", t).columns, t


def test_row_counts_equal_fixture_admissible_rows(drafted):
    m, root = drafted
    conf = m[(m.row_class == "primary") & (m.admissible == "true")]
    e1 = _read(root / "out", "e1_paired_delta")
    rows = e1[e1.level == "row"]
    assert len(rows) == len(conf) * 2 * 2
    assert set(rows.row_id) == set(conf.row_id)
    s = e1[e1.level == "summary"]
    assert len(s) == 2 * 2 * 2 and set(s.subset) == {"both_have_cs", "all_rows"}
    nc = _read(root / "out", "negative_controls")
    assert set(nc.n_rows) == {3}
    sweep = _read(root / "out", "e2_agreement_sweep")
    assert sorted(set(sweep.threshold)) == [0.5, 0.7, 0.8, 0.9]
    for t in ("e1_paired_delta", "e2_agreement_sweep", "e3_reclassification", "e4_no_cs_rate", "e6_panel_contrast",
              "afr_secondary", "negative_controls", "branch_outcomes"):
        assert "p12_key" in _read(root / "out", t).columns, t
    e8 = _read(root / "out", "e8_simulation_rates")
    assert e8.set_index("arm").loc["A2", "k"] == 1
    nq = e8.set_index("scenario")
    assert nq.loc["H3_r2_0.9", "n_files_no_qualifying_pair"] == 1 and nq.loc["H3_r2_0.9", "n"] == 0
    assert set(e8.loc[e8.scenario == "H3_r2_0.6", "n_files_no_qualifying_pair"]) == {0}
    hla = _read(root / "out", "hla_exploratory")
    assert hla.n_cs.tolist() == [3]


def test_nc_perturbation_moves_nc_table_not_branch(tmp_path, drafted):
    _, root = drafted
    build_tree(tmp_path / "repo", nc_bump=-0.29)
    assert _run(tmp_path / "repo", tmp_path / "out", draft=True) == 0
    assert (tmp_path / "out/negative_controls.tsv").read_bytes() != (root / "out/negative_controls.tsv").read_bytes()
    assert (tmp_path / "out/branch_outcomes.tsv").read_bytes() == (root / "out/branch_outcomes.tsv").read_bytes()


def test_nc_rows_in_the_confirmatory_filter_change_branch_outcomes(tmp_path, drafted):
    _, root = drafted
    repo = tmp_path / "repo"
    (repo / "config/ta_r4").mkdir(parents=True)
    y = yaml.safe_load((REPO_ROOT / "config/ta_r4/decision_rules.yaml").read_text())
    y["confirmatory"]["rows"]["row_class"] = ["primary", "negative_control"]
    (repo / "config/ta_r4/decision_rules.yaml").write_text(yaml.safe_dump(y))
    build_tree(repo)
    assert _run(repo, tmp_path / "out", draft=True) == 0
    assert (tmp_path / "out/branch_outcomes.tsv").read_bytes() != (root / "out/branch_outcomes.tsv").read_bytes()


def test_repro_outputs_never_opened(tmp_path, monkeypatch):
    from ta_r4 import paths

    build_tree(tmp_path / "repo")
    opened = []
    real_open, real_read, real_popen = builtins.open, Path.read_text, Path.open

    def rec_open(f, *a, **k):
        opened.append(str(f))
        return real_open(f, *a, **k)

    def rec_read(self, *a, **k):
        opened.append(str(self))
        return real_read(self, *a, **k)

    def rec_popen(self, *a, **k):
        opened.append(str(self))
        return real_popen(self, *a, **k)

    monkeypatch.setattr(builtins, "open", rec_open)
    monkeypatch.setattr(Path, "read_text", rec_read)
    monkeypatch.setattr(Path, "open", rec_popen)
    assert _run(tmp_path / "repo", tmp_path / "out", draft=True) == 0
    monkeypatch.undo()
    assert opened
    root = str(tmp_path / "repo") + "/"
    rel = [p[len(root):] for p in opened if p.startswith(root)]
    assert any(p.startswith("data/r4/results/") for p in rel)
    assert not [p for p in rel if "repro_" in p]
    coloc = [p for p in opened if "/coloc/" in p]
    assert coloc
    dirs = tuple(str(tmp_path / "repo" / d) + "/" for d in paths.result_dirs("coloc"))
    assert all(p.startswith(dirs) for p in coloc)


def test_no_statistics_defined_in_run_aggregation():
    tree = ast.parse(SRC.read_text())
    banned_mods = {"math", "scipy", "random", "statistics", "numpy"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {a.name.split(".")[0] for a in node.names} & banned_mods
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in banned_mods
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"comb", "random", "default_rng", "binom", "percentile", "quantile"}, node.attr
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            name = getattr(node, "name", "").lower()
            assert not any(w in name for w in ("kappa", "mcnemar", "bootstrap", "wilson", "pvalue", "sign_test"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "estimands" in names and "branch_classifier" in names
