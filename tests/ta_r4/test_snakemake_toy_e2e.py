"""REQ-SNAKEMAKE-CI: Snakefile.ta_r4 --use-conda end to end on 3 fixture regions, under A3_1kg and A2_identity.

Fits (receipt -> frozen script -> validator), coloc_susie / fallback_abf, and A1 matched + allvars in the A3
invocation. The gate passes on a fixture sentinel + verify_online receipt that exist only under tmp_path.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import pytest
import yaml

from .fixtures.build_toy_workflow import (ANC, TOY_ARMS, TOY_REGIONS, TRAIT_A, TRAIT_B, build_toy_workflow, pair_row,
                                          run_toy, toy_targets)
from .test_fallback_labelled import METHODS, coloc_result_docs, fallback_violations
from .test_priors_constant import cross_arm_p12_violations, prior_violations

from ta_r4 import commands, paths
from ta_r4.arms import ARMS

pytestmark = pytest.mark.r4_heavy
SMK = str(Path(sys.executable).parent / "snakemake")
PP = ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4")


@pytest.fixture(scope="module")
def toy(tmp_path_factory):
    repo = build_toy_workflow(tmp_path_factory.mktemp("toy"))
    runs = {}
    for arm in TOY_ARMS:
        t0 = time.time()
        p = run_toy(repo, arm, toy_targets(arm), smk=SMK)
        runs[arm] = (p, time.time() - t0)
        print(f"toy {arm}: rc {p.returncode}, {len(toy_targets(arm))} targets, wall {time.time() - t0:.1f} s")
    return repo, runs


def test_toy_runs_end_to_end(toy):
    repo, runs = toy
    for arm, (p, _) in runs.items():
        assert p.returncode == 0, f"{arm}\nSTDOUT\n{p.stdout[-4000:]}\nSTDERR\n{p.stderr[-4000:]}"
        missing = [t for t in toy_targets(arm) if not (repo / t).is_file()]
        assert missing == [], missing
        assert len(toy_targets(arm)) == (6 + 6 + (12 if arm == "A3_1kg" else 0))


def test_every_fit_has_receipt_and_passes_validator(toy):
    from ta_r4.validate_r4_fits import manifest_row, validate_fit
    repo, _ = toy
    n = 0
    for arm in TOY_ARMS:
        for r in TOY_REGIONS:
            for t in (TRAIT_A, TRAIT_B):
                d = json.loads((repo / paths.fit_json(arm, t, ANC, r.region_id)).read_text())
                rc = json.loads((repo / paths.ld_receipt_json(arm, t, ANC, r.region_id)).read_text())
                row = manifest_row(repo / paths.panel_manifest_path(arm, ANC), ANC, r.region_id)
                assert validate_fit(d, rc, row, ARMS[arm]["validator_mode"]) == [], (arm, t, r.region_id)
                assert d["ld_matrix"] == paths.panel_path(arm, r.region_id, ANC)
                n += 1
    assert n == 12


def test_coloc_outputs_methods_priors_and_gates(toy):
    repo, _ = toy
    pri = yaml.safe_load(open(repo / commands.COLOC_PRIORS))
    docs, problems = coloc_result_docs(repo)  # the live gates, run on the fixture tree
    assert problems == [] and len(docs) == 6 + 6 + 12
    assert {f.parent.parent.name for f, _ in docs} == {"A3_1kg", "A2_identity", "A1_EUR"}
    assert {d["method"] for _, d in docs} <= METHODS
    assert fallback_violations(docs) == [] and prior_violations(docs, pri) == [] and cross_arm_p12_violations(docs) == []
    by = {(d["arm"], d["row_id"], d["mode"], d["p12_key"]): d for _, d in docs}
    for k in commands.P12_KEYS:
        for r in TOY_REGIONS:
            rid = pair_row(r.region_id)["row_id"]
            want = "fallback_abf" if r.b_null else "coloc_susie"
            assert by[("A3_1kg", rid, "susie", k)]["method"] == by[("A2_identity", rid, "susie", k)]["method"] == want
        # Pitfall 8: the fallback is LD-free, so A3, A2 and A1 matched agree exactly at FIX_3.
        rid = pair_row("FIX_3")["row_id"]
        trio = [by[("A3_1kg", rid, "susie", k)], by[("A2_identity", rid, "susie", k)], by[("A1_EUR", rid, "A1_matched", k)]]
        assert len({tuple(d[p] for p in PP) for d in trio}) == 1
        assert len({d["variant_set_sha256"] for d in trio}) == 1


def test_negative_control_missing_manifest_row_fails_at_receipt(toy):
    """Delete the A3 panel manifest row for FIX_2: the forced FIX_2 fit fails in r4_run_finemap at the receipt."""
    repo, _ = toy
    mp = repo / paths.panel_manifest_path("A3_1kg", ANC)
    rows = list(csv.DictReader(open(mp), delimiter="\t"))
    keep = [r for r in rows if r["region_safe"] != "FIX_2"]
    assert len(keep) == len(rows) - 1
    with open(mp, "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(keep)
    target = paths.fit_json("A3_1kg", TRAIT_A, ANC, "FIX_2")
    p = run_toy(repo, "A3_1kg", [target], "--forcerun", "r4_run_finemap", smk=SMK)
    out = p.stdout + p.stderr
    print("NC rc", p.returncode, [ln for ln in out.splitlines() if "LD_RECEIPT_REFUSED" in ln or "Error in rule" in ln])
    assert p.returncode != 0 and "Error in rule r4_run_finemap" in out
    assert "LD_RECEIPT_REFUSED: no manifest row (EUR, FIX_2)" in out


def test_coloc_rule_listed_via_fire_script():
    from .conftest import REPO_ROOT
    import re
    import subprocess
    p = subprocess.run(["bash", "bin/r4_fire.sh", "repro", "repro_routeC", "--list"], cwd=REPO_ROOT,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    assert re.search(r"^r4_coloc_pair$", p.stdout, re.M)


def test_coloc_rule_refused_without_gate(tmp_path):
    """No sentinel: the A1 all-variants target (no fit dependency) refuses at the coloc rule's own gate call."""
    import subprocess
    from .fixtures.make_fixture_repo import make_fixture_repo
    repo = make_fixture_repo(tmp_path)
    target = paths.coloc_json("A1_EUR", "SH2B3_12q24__EUR__bmi_vs_hypertension", "p12_primary", "allvars")
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_A3_1kg.yaml"]
    p = subprocess.run([SMK, target, "-s", "Snakefile.ta_r4", "-d", ".", "-n", "--configfile", *cfg], cwd=repo,
                       capture_output=True, text=True)
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "OsfGateError" in out and "sentinel absent" in out, out[-2000:]
    assert "rule r4_coloc_A1" in out
