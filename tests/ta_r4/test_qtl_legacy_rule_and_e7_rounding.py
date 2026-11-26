"""W3f 15.8c2 (DEC-2026-11-25-ta-r4-qtl-legacy-nan-rule-and-e7-matched-rounding; Carter Q-F3NL, Q-158E7R).

QTL_legacy, E7's earlier-pipeline comparator, keeps the earlier NaN-GWAS rule: tiers_argv passes
--nan-gwas-below-threshold for QTL_A3 and QTL_A2 only. QTL_legacy posteriors are written by jsonlite's default
(4 decimals) while QTL_A3's are exact (15.8c), so E7 also reports the QTL_A3 tier re-derived from QTL_A3 posteriors
rounded as jsonlite's default writes them (fixed_value_qtl_4dp, changed_qtl_4dp).
"""
from __future__ import annotations

import hashlib
import math
import os
import random
import re
import shlex
import subprocess
import time

import pandas as pd
import pytest

from ta_r4 import estimands, run_aggregation
from ta_r4 import run_qtl_group_r4 as Q

from .conftest import REPO_ROOT
from .fixtures.qtl_group_fixture import RSCRIPT
from .test_in_job_gate import build_gate_repo, jobs, rendered  # noqa: F401  (rendered is a fixture)
from .test_lock_gate import SMK

FLAG = "--nan-gwas-below-threshold"
PP = ("PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf")
TIER_HEAD = "region\tancestry\ttier\tbest_gwas_pph4\tbest_qtl_pph4\tresolving_gene\tresolving_tissue" \
            "\tresolving_qtl_source\tall_supporting_sources\tneg_ctrl_set\n"


def _argv(qtl_arm):
    return Q.tiers_argv(qtl_arm, "S", "G", "P", "T", "W", py="PY")


def test_tiers_argv_passes_the_nan_flag_for_a3_and_a2_only():
    base = ["PY", "src/python/assign_tiers.py", "--input", "S", "--gwas-coloc", "G", "--pph4-config", "P",
            "--output", "T", "--sweep", "--sweep-output", "W"]
    assert set(Q.QTL_ARMS) == {"QTL_A3", "QTL_A2", "QTL_legacy"}
    for qtl_arm in ("QTL_A3", "QTL_A2"):
        assert Q.QTL_ARMS[qtl_arm]["nan_gwas_below_threshold"] is True
        assert _argv(qtl_arm) == base + [FLAG], qtl_arm
    assert Q.QTL_ARMS["QTL_legacy"]["nan_gwas_below_threshold"] is False
    assert _argv("QTL_legacy") == base
    with pytest.raises(KeyError):
        _argv("QTL_nope")


def _tiers_cmds(js):
    return [(a, c) for r, a, cs in js if r == "r4_qtl_tiers" for c in cs if "assign_tiers.py" in c]


def _want(qtl_arm, py):
    d = f"data/r4/results/{qtl_arm}"
    return shlex.join(Q.tiers_argv(qtl_arm, f"{d}/qtl_coloc_summary_tierable.tsv", f"{d}/gwas_coloc_for_tiers.tsv",
                                   "config/pph4_thresholds.yaml", f"{d}/qtl_tiers.tsv", f"{d}/qtl_tiers_sweep.tsv",
                                   py=py))


@pytest.mark.r4_heavy
def test_rendered_r4_qtl_tiers_command_per_arm(rendered, tmp_path):  # noqa: F811
    # QTL_A3 in the A3_1kg invocation (the module dry-run)
    a3 = _tiers_cmds(rendered[2])
    assert len(a3) == 1
    py = re.search(r"(\S+) src/python/assign_tiers\.py", a3[0][1]).group(1)
    assert a3[0][1].startswith(_want("QTL_A3", py) + ")") and FLAG in shlex.split(a3[0][1].partition(")")[0]), a3
    # QTL_legacy in the repro_routeL invocation: the rule's inputs exist, only r4_qtl_tiers is scheduled
    repo, _, _ = build_gate_repo(tmp_path)
    d = "data/r4/results/QTL_legacy"
    old = time.time() - 3600
    ins = [f"{d}/qtl_coloc_summary_tierable.tsv"] + Q.coloc_inputs(
        "QTL_legacy", pair_manifest=str(repo / "config/ta_r4/pair_manifest.tsv"), manifest=str(repo / Q.MANIFEST))
    assert len(ins) > 1
    for f in ins:
        (repo / f).parent.mkdir(parents=True, exist_ok=True)
        (repo / f).write_text("fixture\n")
        os.utime(repo / f, (old, old))
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_repro_routeL.yaml"]
    p = subprocess.run([SMK, f"{d}/qtl_tiers.tsv", "-s", "Snakefile.ta_r4", "-d", ".", "-n",
                        "-p", "--configfile", *cfg], cwd=repo, capture_output=True, text=True)
    out = p.stdout + p.stderr
    assert p.returncode == 0, out[-3000:]
    js = jobs(out)
    assert [r for r, _, _ in js] == ["r4_qtl_tiers"], [r for r, _, _ in js]
    leg = _tiers_cmds(js)
    assert len(leg) == 1 and "qtl_arm=QTL_legacy" in leg[0][0]["wildcards"], leg
    py = re.search(r"(\S+) src/python/assign_tiers\.py", leg[0][1]).group(1)
    assert FLAG not in leg[0][1], leg[0][1]
    assert leg[0][1].startswith(_want("QTL_legacy", py) + ")"), leg[0][1]


@pytest.mark.r4_heavy
def test_round_like_jsonlite_default_matches_jsonlite(tmp_path):
    rng = random.Random(20261126)
    x = [rng.random() for _ in range(10 ** 5)]
    x += [10 ** rng.uniform(-300, 0) for _ in range(10 ** 5)]
    x += [rng.uniform(1e-5, 1e-4) for _ in range(10 ** 4)]
    x += [(k + 0.5) / 1e4 for k in range(10 ** 4)]  # decimal ties x.xxxx5
    x += [0.0, 1.0, 1e-5, 0.00005, 0.00015, 3.2e-5, 1.234567e-7, 0.79996, 0.99995, 1.00005]
    (tmp_path / "x.hex").write_text("".join(v.hex() + "\n" for v in x))
    r = ('suppressWarnings(library(jsonlite)); a <- commandArgs(TRUE); x <- as.numeric(readLines(a[1])); '
         'stopifnot(!anyNA(x)); writeLines(toJSON(x), a[2])')
    p = subprocess.run([RSCRIPT, "-e", r, str(tmp_path / "x.hex"), str(tmp_path / "x.json")], capture_output=True,
                       text=True)
    assert p.returncode == 0, p.stderr
    toks = (tmp_path / "x.json").read_text().strip()[1:-1].split(",")
    assert len(toks) == len(x)
    bad = [(v, t, estimands.round_like_jsonlite_default(v)) for v, t in zip(x, toks)
           if estimands.round_like_jsonlite_default(v) != float(t)]
    assert not bad, (len(bad), bad[:10])
    assert {0.00015: 0.0001, 3.2e-5: 0.0, 1.234567e-7: 1.2346e-07, 0.79996: 0.8} == {
        v: float(toks[x.index(v)]) for v in (0.00015, 3.2e-5, 1.234567e-7, 0.79996)}
    assert math.isnan(estimands.round_like_jsonlite_default(float("nan")))


def _qrepo(root, a3_pph4, legacy_tier, with_summary=True):
    """Fixture repo: QTL_A3 tierable summary (exact posteriors), its GWAS table and tiers, QTL_legacy tiers, config."""
    res = root / "data/r4/results"
    (root / "config").mkdir(parents=True)
    (root / "config/pph4_thresholds.yaml").write_bytes((REPO_ROOT / "config/pph4_thresholds.yaml").read_bytes())
    (res / "QTL_A3").mkdir(parents=True)
    (res / "QTL_legacy").mkdir(parents=True)
    rest = (1 - a3_pph4) / 4
    if with_summary:
        (res / "QTL_A3/qtl_coloc_summary_tierable.tsv").write_text(
            "qtl_coloc_id\tqtl_source\ttissue\tgene_id\tregion\tancestry\tmethod\t" + "\t".join(PP) + "\n"
            + f"q1\tgtex_eqtl\tWhole_Blood\tENSG1\tR1\tEUR\tcoloc_susie\t{rest!r}\t{rest!r}\t{rest!r}\t{rest!r}"
              f"\t{a3_pph4!r}\n"
            + "q2\tgtex_eqtl\tWhole_Blood\tENSG2\tR2\tEUR\tcoloc_susie\t0.1\t0.1\t0.1\t0.1\t0.6\n")
    (res / "QTL_A3/gwas_coloc_for_tiers.tsv").write_text(
        "region\tancestry\ttrait_a\ttrait_b\tPP.H4.abf\nR1\tEUR\ttA\ttB\t0.95\nR2\tEUR\ttA\ttB\t0.95\n")
    exact = "Tier A" if a3_pph4 >= 0.8 else "Tier B"
    (res / "QTL_A3/qtl_tiers.tsv").write_text(TIER_HEAD + f"R1\tEUR\t{exact}\t0.95\t{a3_pph4!r}\t\t\t\t\t\n"
                                              + "R2\tEUR\tTier B\t0.95\t0.6\t\t\t\t\t\n")
    (res / "QTL_legacy/qtl_tiers.tsv").write_text(TIER_HEAD + f"R1\tEUR\t{legacy_tier}\t0.95\t0.8\t\t\t\t\t\n"
                                                  + "R2\tEUR\tTier B\t0.95\t0.6\t\t\t\t\t\n")
    return root


def _e7(repo, t4):
    _, _, frozen, fixed = run_aggregation._qtl(repo)
    e = pd.DataFrame(columns=["pair", "trait", "ancestry", "region_safe", "status_L", "n_cs_L"])
    s = pd.DataFrame(columns=["config_label", "pair_id", "status", "pp_h4_reproduced"])
    fits = pd.DataFrame(columns=["arm", "trait", "ancestry", "region_safe", "status", "n_cs", "ld_allele_exact",
                                 "ld_allele_flipped"])
    rows = pd.DataFrame(columns=["row_id", "label", "p12_key", "region_stat"])
    return estimands.e7_frozen_vs_fixed(e, s, fits, rows, [], a3_arm={"EUR": "A3_1kg"}, p12_key="p12_primary",
                                        qtl_tiers_frozen=frozen, qtl_tiers_fixed=fixed, qtl_tiers_fixed_4dp=t4)


def test_e7_qtl_tier_has_the_matched_rounding_columns(tmp_path):
    repo = _qrepo(tmp_path / "r", 0.6, "Tier B")
    t4 = run_aggregation._qtl_tiers_qtl4dp(repo)
    assert t4 is not None
    t = _e7(repo, t4)
    assert list(t.columns)[-2:] == ["fixed_value_qtl_4dp", "changed_qtl_4dp"]
    assert list(t.columns)[:-2] == ["section", "id", "region_safe", "ancestry", "frozen_value", "fixed_value",
                                    "changed", "n_exact", "n_flipped", "flipped_share"]
    q = t[t.section == "qtl_tier"].set_index("id")
    assert q.loc["R2.EUR", "fixed_value_qtl_4dp"] == "Tier B" and q.loc["R2.EUR", "changed_qtl_4dp"] == False  # noqa
    # without a 4-decimal table (QTL_A3's summary absent) the two columns are empty
    bare = _qrepo(tmp_path / "b", 0.6, "Tier B", with_summary=False)
    assert run_aggregation._qtl_tiers_qtl4dp(bare) is None
    t0 = _e7(bare, None)
    q0 = t0[t0.section == "qtl_tier"]
    assert len(q0) == 2 and (q0.fixed_value_qtl_4dp == "").all() and q0.changed_qtl_4dp.isna().all()


def test_matched_rounding_isolates_a_boundary_flip(tmp_path):
    repo = _qrepo(tmp_path / "r", 0.79996, "Tier A")
    t4 = run_aggregation._qtl_tiers_qtl4dp(repo)
    assert t4.set_index("region").loc["R1", "tier"] == "Tier A"
    assert float(t4.set_index("region").loc["R1", "best_qtl_pph4"]) == 0.8
    q = _e7(repo, t4).set_index("id")
    r1 = q.loc["R1.EUR"]
    assert (r1.frozen_value, r1.fixed_value, r1.fixed_value_qtl_4dp) == ("Tier A", "Tier B", "Tier A")
    assert r1.changed == True and r1.changed_qtl_4dp == False  # noqa: E712  (the change is the rounding only)


def _tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def test_matched_rounding_changes_nothing_frozen(tmp_path):
    repo = _qrepo(tmp_path / "r", 0.79996, "Tier A")
    frozen = [REPO_ROOT / run_aggregation.KNOWN_W3A, REPO_ROOT / run_aggregation.KNOWN_SH2B3]
    before, fb = _tree(repo), [hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen]
    t4 = run_aggregation._qtl_tiers_qtl4dp(repo)
    assert t4 is not None and len(t4) == 2
    assert _tree(repo) == before  # inputs, QTL tables and config byte-equal; nothing written under the repo
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen] == fb
    assert Q.tiers_argv("QTL_legacy", "S", "G", "P", "T", "W", py="PY")[-1] == "W"  # QTL_legacy's argv unchanged
