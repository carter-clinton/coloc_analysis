"""N1 (W3f, DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze): under --cap-after-ld-restriction true the
frozen run_susie_rss.R applies SUSIE_MAX_VARIANTS to the panel-restricted subset; default false is unchanged.

Fixture: the W0c region with its catalog cut to 40 variants (palindromic SNP excluded) and its panel to 25 of them.
The fixture policy lowers min_ld_overlap to 20 so a 25-variant overlap is accepted (production policy: 50).
"""
from __future__ import annotations

import json
import shutil

import pytest

from .conftest import merged_config
from .test_frozen_script_armed_e2e import (ANC, REGION, RSCRIPT, TRAIT, _ok, _run, _write_manifest,
                                           build_fixture)

from ta_r4 import commands, paths
from ta_r4.arms import ARMS, CURRENT_SCRIPT

ARM = "A3_1kg"
FLAG = "--cap-after-ld-restriction"
CATALOG_IDX = [i for i in range(1, 42) if i != 30]   # 40 rows, 1-based, palindromic SNP 30 excluded
PANEL_IDX = CATALOG_IDX[:25]


def _argv(cap, flag=None):
    cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{ARM}.yaml")
    cmd = commands.fit_command(ARM, TRAIT, ANC, REGION, cfg, region_id=REGION)
    assert cmd[1].startswith("SUSIE_MAX_VARIANTS=")
    cmd[1] = f"SUSIE_MAX_VARIANTS={cap}"
    if FLAG in cmd:
        i = cmd.index(FLAG)
        del cmd[i:i + 2]
    if flag is not None:
        cmd += [FLAG, flag]
    return cmd


@pytest.fixture(scope="module")
def base(tmp_path_factory):
    root = tmp_path_factory.mktemp("cap_after_panel")
    panel = build_fixture(root)
    cat = root / paths.catalog_path(ARMS[ARM]["route"], REGION)
    lines = cat.read_text().splitlines()
    cat.write_text("\n".join([lines[0]] + [lines[i] for i in CATALOG_IDX]) + "\n")
    keep = ",".join(str(i) for i in PANEL_IDX)
    _ok(_run([RSCRIPT, "-e", f'p <- readRDS("{root / panel}"); k <- c({keep}); p$R <- p$R[k, k, drop = FALSE]; '
                             f'p$variants <- p$variants[k, , drop = FALSE]; saveRDS(p, "{root / panel}")'], root))
    (root / paths.panel_manifest_path(ARM, ANC)).unlink()
    _write_manifest(root, ARM, panel, REGION)
    pol = root / ARMS[ARM]["policy"]
    txt = pol.read_text()
    assert "min_ld_overlap: 50" in txt
    pol.write_text(txt.replace("min_ld_overlap: 50", "min_ld_overlap: 20"))
    _ok(_run(commands.receipt_command(ARM, TRAIT, ANC, REGION), root))
    return root


@pytest.fixture
def root(base, tmp_path):
    r = tmp_path / "r"
    shutil.copytree(base, r, symlinks=True)
    return r


def _fit(root, cap, flag=None):
    p = _run(_argv(cap, flag), root)
    out = root / paths.fit_json(ARM, TRAIT, ANC, REGION)
    return p, (json.loads(out.read_text()) if out.exists() else None)


def _rds(root):
    rds = root / paths.fit_rds(ARM, TRAIT, ANC, REGION)
    p = _ok(_run([RSCRIPT, "-e", f'f <- readRDS("{rds}"); '
                                 'cat(jsonlite::toJSON(list(status = f$status, n_variants = f$n_variants, '
                                 'n_variants_pre_ld = f$n_variants_pre_ld, cap_stage = f$cap_stage, '
                                 'lbf_cols = if (is.null(f$lbf_variable)) NULL else colnames(f$lbf_variable), '
                                 'lbf_ncol = if (is.null(f$lbf_variable)) NULL else ncol(f$lbf_variable)), '
                                 'auto_unbox = TRUE, null = "null"))'], root))
    return json.loads(p.stdout.strip().splitlines()[-1])


@pytest.mark.r4_heavy
@pytest.mark.parametrize("flag", [None, "false"])
def test_default_caps_before_panel(root, flag):
    p, d = _fit(root, 30, flag)
    _ok(p)
    assert d["status"] == "too_many_variants"
    r = _rds(root)
    assert (r["status"], r["n_variants"]) == ("too_many_variants", 40)
    assert "n_variants_pre_ld" not in d and "cap_stage" not in d


@pytest.mark.r4_heavy
def test_flag_true_fits_panel_restricted_subset(root):
    p, d = _fit(root, 30, "true")
    _ok(p)
    assert d["status"] != "too_many_variants", d.get("notes")
    r = _rds(root)
    assert r["lbf_ncol"] is not None
    assert r["lbf_ncol"] - ("null" in (r["lbf_cols"] or [])) == 25


@pytest.mark.r4_heavy
def test_flag_true_caps_after_panel(root):
    p, d = _fit(root, 20, "true")
    _ok(p)
    assert (d["status"], d["n_variants"], d["n_variants_pre_ld"], d["cap_stage"]) == \
        ("too_many_variants", 25, 40, "after_ld_restriction")
    r = _rds(root)
    assert (r["status"], r["n_variants"], r["n_variants_pre_ld"], r["cap_stage"]) == \
        ("too_many_variants", 25, 40, "after_ld_restriction")
    v = _run(commands.validate_command(ARM, TRAIT, ANC, REGION), root)
    assert v.returncode == 0, v.stdout + v.stderr
    assert "early_exit=1" in v.stdout


@pytest.mark.r4_heavy
def test_flag_value_is_strict(root):
    p, _ = _fit(root, 30, "maybe")
    assert p.returncode != 0
    assert FLAG in p.stderr


def test_fit_command_flag_per_arm():
    for arm, row in ARMS.items():
        cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml")
        anc = row["ancestry"] if isinstance(row["ancestry"], str) else row["ancestry"][0]
        cmd = commands.fit_command(arm, TRAIT, anc, REGION, cfg, region_id=REGION)
        if row["script"] == CURRENT_SCRIPT and row["validator_mode"] != "legacy_any":
            assert cmd.count(FLAG) == 1, arm
            assert cmd[cmd.index(FLAG) + 1] == "true", arm
        else:
            assert FLAG not in cmd, arm
