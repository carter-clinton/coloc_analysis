"""Overlay semantics for every R4 arm (D-01, D-14, D-15, B4)."""
from __future__ import annotations

import pytest
import yaml
from snakemake.utils import update_config

from ld_read_path import ld_allele_aware, ld_file_authoritative
from ta_r4 import arms as arms_mod
from ta_r4.arms import ARMS, arm_stage, production_arms
from ta_r4.paths import panel_manifest_path, result_dirs

from .conftest import MAN_DIR, REPO_ROOT, merged_config

BASE = "config/ta_r4/overlay_base.yaml"
EUR_PROD = ["A3_1kg", "A2_identity", "A3_ukb", "A3_ukb_isect", "A3_1kg_isect"]
AFR_PROD = ["AFR661_A3", "AFR661_A2", "AFR504_A3"]
REPRO = ["repro_routeC", "repro_routeL", "repro_k2d_routeC", "repro_k2d_routeL", "repro_sh2b3_r2"]


def _arm_cfg(arm):
    return merged_config(BASE, f"config/ta_r4/overlay_{arm}.yaml")


def test_arm_names():
    assert sorted(ARMS) == sorted(EUR_PROD + AFR_PROD + REPRO)
    assert sorted(production_arms()) == sorted(EUR_PROD + AFR_PROD)


@pytest.mark.parametrize("arm", EUR_PROD + AFR_PROD)
def test_production_overlay_arms_and_pins(arm):
    anc = ARMS[arm]["ancestry"]
    c = _arm_cfg(arm)
    assert ld_allele_aware(anc, c) == "true"
    assert ld_file_authoritative(anc, c) == "true"
    assert [e["source"] for e in c["ld_panel"][anc]] == [ARMS[arm]["panel_source"]]
    assert c["ld_panel"]["pin"][anc] == ARMS[arm]["panel_source"]
    dumped = yaml.safe_dump(c["ld_panel"][anc])
    assert "EUR_ukbb_pub" not in dumped
    assert f"data/r4/ld/{ARMS[arm]['panel_dir']}/" in dumped
    assert c["ta_r4"]["arm"] == arm


@pytest.mark.parametrize("arm", AFR_PROD)
def test_afr_overlay_drops_lockstep_and_aou(arm):
    c = _arm_cfg(arm)
    assert c["occlusion_lockstep"]["enabled"] is False
    assert "AFR_aou" not in yaml.safe_dump(c["ld_panel"]["AFR"])


@pytest.mark.parametrize("arm", REPRO)
def test_repro_overlay_is_legacy(arm):
    c = _arm_cfg(arm)
    assert ld_file_authoritative("EUR", c) == "false"
    assert ld_allele_aware("EUR", c) == "false"
    assert c["ld_read_path"]["ancestries"] == []
    for anc in ("EUR", "AFR"):
        assert [e["source"] for e in c["ld_panel"][anc]] == [ARMS[arm]["panel_source"]]
        assert f"data/r4/ld/{ARMS[arm]['panel_dir']}/" in yaml.safe_dump(c["ld_panel"][anc])


def test_base_config_untouched():
    c = merged_config()
    assert ld_allele_aware("EUR", c) == "false"
    assert c["ld_read_path"]["ancestries"] == ["AFR"]
    assert c["ld_panel"]["EUR"][0]["source"] == "EUR_ukbb_pub"


def test_identity_overlay_independent_of_real_panel():
    c = _arm_cfg("A2_identity")
    chain = c["ld_panel"]["EUR"]
    assert len(chain) == 1
    path = chain[0]["path"]
    assert "EUR_identity_r4" in path
    others = {r["panel_dir"] for a, r in ARMS.items() if a != "A2_identity"}
    assert not any(f"/{d}/" in path for d in others)


def test_stage_is_code_not_config():
    c = _arm_cfg("A3_1kg")
    update_config(c, {"ta_r4": {"stage": "repro"}})
    assert c["ta_r4"]["stage"] == "repro"
    assert arm_stage("A3_1kg") == "production"


def test_panel_manifest_path_per_ancestry():
    eur = panel_manifest_path("repro_routeC", "EUR")
    afr = panel_manifest_path("repro_routeC", "AFR")
    assert eur != afr
    assert REPO_ROOT / eur == MAN_DIR / "panels_legacy_repro.tsv"
    assert REPO_ROOT / afr == MAN_DIR / "panels_legacy_repro_AFR.tsv"
    assert panel_manifest_path("repro_k2d_routeC", "EUR") == panel_manifest_path("repro_k2d_routeL", "AFR")
    assert REPO_ROOT / panel_manifest_path("repro_k2d_routeC", "EUR") == MAN_DIR / "panels_k2d_identity.tsv"
    for arm in production_arms():
        p = panel_manifest_path(arm, ARMS[arm]["ancestry"])
        assert REPO_ROOT / p == MAN_DIR / f"panels_{ARMS[arm]['panel_dir']}.tsv"


def test_priors_single_source():
    d = yaml.safe_load((REPO_ROOT / "config/ta_r4/coloc_priors.yaml").read_text())
    assert d["p1"] == d["p2"] == 1e-4
    assert d["p12_primary"] == 5e-6
    assert d["p12_sensitivity"] == 1e-5
    assert d["locked"] is False


def test_repro_policy_differs_only_in_retry():
    base = yaml.safe_load((REPO_ROOT / "config/susie_policy.yaml").read_text())
    repro = yaml.safe_load((REPO_ROOT / "config/ta_r4/susie_policy_repro_iter100.yaml").read_text())
    assert repro["susie"]["max_iter_retry"] == 100
    base["susie"]["max_iter_retry"] = 100
    assert repro == base


def test_result_dirs_from_arms():
    prod = [a for a, r in ARMS.items() if r["stage"] == "production"]
    fits = result_dirs("fits")
    assert fits == sorted(f"data/r4/results/{a}/fine_mapping/susie" for a in prod)
    assert len(fits) == 8
    assert "data/r4/results/A3_1kg_isect/fine_mapping/susie" in fits
    coloc = result_dirs("coloc")
    assert coloc == sorted(f"data/r4/results/{a}/coloc" for a in prod) + [
        "data/r4/results/A1_EUR/coloc",
        "data/r4/results/A1_AFR/coloc",
    ]
    assert len(coloc) == 10
    for a in REPRO:
        assert not any(f"/{a}/" in d for d in fits + coloc)


def test_result_dirs_reads_arms_not_a_literal(monkeypatch):
    relabelled = {k: dict(v) for k, v in ARMS.items()}
    relabelled["repro_routeC"]["stage"] = "production"
    monkeypatch.setattr(arms_mod, "ARMS", relabelled)
    assert "data/r4/results/repro_routeC/fine_mapping/susie" in result_dirs("fits")
    assert "data/r4/results/repro_routeC/coloc" in result_dirs("coloc")
