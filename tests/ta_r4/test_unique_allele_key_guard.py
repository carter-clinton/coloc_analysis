"""W3f 15.5a (DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze): under --require-unique-allele-key true
the frozen run_susie_rss.R stops with DUPLICATE_ALLELE_KEYS when a normalized CHR:POS:REF:ALT repeats in the fit
subset (after the panel restriction, before the post-restriction cap); default false is unchanged.

Fixture: test_cap_after_panel's (40-variant catalog, 25-variant panel) plus byte-exact rs twins of panel variants
2, 3, 4, a lowercase twin of panel variant 6 and a second ALT at variant 10's position (absent from the panel).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys

import pytest

from .conftest import REPO_ROOT, merged_config
from .test_frozen_script_armed_e2e import (ANC, FROZEN_REL, HTS_BIN, REGION, RSCRIPT, TRAIT, _ok, _run,
                                           _write_manifest, build_fixture)

from ta_r4 import commands, paths
from ta_r4.arms import ARMS, CURRENT_SCRIPT

ARM = "A3_1kg"
FLAG = "--require-unique-allele-key"
CAP_FLAG = "--cap-after-ld-restriction"
#: The pre-guard code pin (DEC-2026-11-04 N1 wrap). Differential substrate: never re-pin.
PRE_GUARD_REF = "1f77128"
CATALOG_IDX = [i for i in range(1, 42) if i != 30]
PANEL_IDX = CATALOG_IDX[:25]
EXACT_TWINS = (2, 3, 4)
LOWER_TWIN = 6
MULTI = 10
DUP_KEYS = ("1:2000:A:G", "1:3000:C:T", "1:4000:G:T", "1:6000:G:A")


def _argv(cap, flag=None):
    cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{ARM}.yaml")
    cmd = commands.fit_command(ARM, TRAIT, ANC, REGION, cfg, region_id=REGION)
    assert cmd[1].startswith("SUSIE_MAX_VARIANTS=")
    cmd[1] = f"SUSIE_MAX_VARIANTS={cap}"
    for f in (FLAG, "--exact-purity"):  # 15.7f: the pre-guard substrate (1f77128) predates --exact-purity
        while f in cmd:
            i = cmd.index(f)
            del cmd[i:i + 2]
    if flag is not None:
        cmd += [FLAG, flag]
    return cmd


def _twin_lines(lines):
    out = []
    for j in EXACT_TWINS:
        f = lines[j].split("\t")
        out.append("\t".join(f[:4] + [f"rs{9000000 + j}"]))
    f = lines[LOWER_TWIN].split("\t")
    out.append("\t".join([f[0], f[1], f[2].lower(), f[3].lower(), f"rs{9000000 + LOWER_TWIN}"]))
    f = lines[MULTI].split("\t")
    other = next(a for a in "ACGT" if a not in (f[2], f[3]))
    out.append("\t".join([f[0], f[1], f[2], other, "rs9100010"]))
    return out


@pytest.fixture(scope="module")
def base(tmp_path_factory):
    root = tmp_path_factory.mktemp("unique_key_guard")
    panel = build_fixture(root)
    cat = root / paths.catalog_path(ARMS[ARM]["route"], REGION)
    lines = cat.read_text().splitlines()
    body = [lines[i] for i in CATALOG_IDX] + _twin_lines(lines)
    body.sort(key=lambda ln: int(ln.split("\t")[1]))
    cat.write_text("\n".join([lines[0]] + body) + "\n")
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


def _dedup_catalog(root):
    cat = root / paths.catalog_path(ARMS[ARM]["route"], REGION)
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src/python"))
    p = subprocess.run([sys.executable, "-m", "ta_r4.catalog_unique_key", "--in", str(cat), "--out", str(cat),
                        "--dropped", str(root / "dropped.tsv")], capture_output=True, text=True, env=env)
    _ok(p)
    s = json.loads(p.stdout.strip().splitlines()[-1])
    assert (s["n_dropped_exact"], s["n_dropped_case_ws"], s["n_chrpos_extra_kept"]) == (3, 1, 1)


def _fit(root, cap, flag=None, argv=None):
    p = _run(argv or _argv(cap, flag), root)
    out = root / paths.fit_json(ARM, TRAIT, ANC, REGION)
    return p, (json.loads(out.read_text()) if out.exists() else None)


def _rds(root):
    rds = root / paths.fit_rds(ARM, TRAIT, ANC, REGION)
    if not rds.exists():
        return None
    p = _ok(_run([RSCRIPT, "-e", f'f <- readRDS("{rds}"); '
                                 'cat(jsonlite::toJSON(list(status = f$status, '
                                 'lbf_cols = if (is.null(f$lbf_variable)) NULL else colnames(f$lbf_variable), '
                                 'lbf_ncol = if (is.null(f$lbf_variable)) NULL else ncol(f$lbf_variable)), '
                                 'auto_unbox = TRUE, null = "null"))'], root))
    return json.loads(p.stdout.strip().splitlines()[-1])


def _no_lbf_rds(root):
    r = _rds(root)
    assert r is None or r["lbf_ncol"] is None, r


@pytest.mark.r4_heavy
def test_dup_catalog_stops(root):
    p, _ = _fit(root, 16000, "true")
    assert p.returncode != 0
    assert "DUPLICATE_ALLELE_KEYS:" in p.stderr, p.stderr[-2000:]
    assert "n_dup_rows=4 " in p.stderr, p.stderr[-2000:]
    for k in DUP_KEYS:
        assert k in p.stderr, (k, p.stderr[-2000:])
    _no_lbf_rds(root)


@pytest.mark.r4_heavy
def test_deduplicated_catalog_fits(root):
    _dedup_catalog(root)
    p, d = _fit(root, 16000, "true")
    _ok(p)
    assert d["status"] != "too_many_variants", d.get("notes")
    r = _rds(root)
    assert r["lbf_ncol"] is not None
    cols = [c for c in r["lbf_cols"] if c != "null"]
    assert len(cols) == len(set(cols)) == len(PANEL_IDX)
    for j in (MULTI, LOWER_TWIN) + EXACT_TWINS:
        assert any(c.endswith(f"{9000000 + j}") or c == f"1:{1000 * j}" for c in cols), (j, cols)


@pytest.mark.r4_heavy
def test_guard_runs_before_cap(root):
    p, d = _fit(root, 0, "true")
    assert p.returncode != 0
    assert "DUPLICATE_ALLELE_KEYS:" in p.stderr, p.stderr[-2000:]
    assert d is None or d.get("status") != "too_many_variants"


@pytest.mark.r4_heavy
def test_sumstats_duplicate_stops_on_clean_catalog(root):
    _dedup_catalog(root)
    ss = root / paths.sumstats_path(TRAIT, ANC, ARM)
    with gzip.open(ss, "rt") as fh:
        lines = fh.read().splitlines()
    lines.insert(4, lines[3])  # a byte-exact copy of sumstats row 3 (variant 3)
    plain = ss.with_suffix("")
    plain.write_text("\n".join(lines) + "\n")
    with open(ss, "wb") as out:
        _ok(subprocess.run([f"{HTS_BIN}/bgzip", "-f", "-c", str(plain)], stdout=out, stderr=subprocess.PIPE))
    plain.unlink()
    _ok(_run([f"{HTS_BIN}/tabix", "-f", "-s", "1", "-b", "2", "-e", "2", "-S", "1", ss], root))
    p, _ = _fit(root, 16000, "true")
    assert p.returncode != 0
    assert "DUPLICATE_ALLELE_KEYS:" in p.stderr, p.stderr[-2000:]
    assert "n_dup_rows=1 " in p.stderr and "1:3000:C:T" in p.stderr, p.stderr[-2000:]
    _no_lbf_rds(root)


def _outputs(root):
    j = root / paths.fit_json(ARM, TRAIT, ANC, REGION)
    rds = root / paths.fit_rds(ARM, TRAIT, ANC, REGION)
    return (json.loads(j.read_text()) if j.exists() else None,
            hashlib.md5(rds.read_bytes()).hexdigest() if rds.exists() else None)


#: JSON/RDS fields dropped before the differential: none (the script writes no timing field and every path
#: argument is repo-relative, so two roots give equal values).
VOLATILE = ()


@pytest.mark.r4_heavy
@pytest.mark.parametrize("flag", [None, "false"])
def test_default_is_pre_guard_behaviour(root, tmp_path, flag):
    p_new, _ = _fit(root, 16000, flag)
    new = _outputs(root)
    old_root = tmp_path / "old"
    shutil.copytree(root, old_root, symlinks=True)
    for f in (paths.fit_json(ARM, TRAIT, ANC, REGION), paths.fit_rds(ARM, TRAIT, ANC, REGION)):
        (old_root / f).unlink(missing_ok=True)
    pre = subprocess.run(["git", "show", f"{PRE_GUARD_REF}:{FROZEN_REL}"], cwd=REPO_ROOT, capture_output=True,
                         text=True, check=True).stdout
    link = old_root / FROZEN_REL
    link.unlink()
    link.write_text(pre)
    p_old, _ = _fit(old_root, 16000, None, argv=_argv(16000, None))
    assert p_new.returncode == p_old.returncode, (p_new.stderr[-2000:], p_old.stderr[-2000:])
    old = _outputs(old_root)
    assert new[0] is not None and old[0] is not None
    assert {k: v for k, v in new[0].items() if k not in VOLATILE} == \
        {k: v for k, v in old[0].items() if k not in VOLATILE}
    assert new[1] == old[1]


@pytest.mark.r4_heavy
def test_flag_value_is_strict(root):
    p, _ = _fit(root, 16000, "maybe")
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
            assert cmd.index(FLAG) == cmd.index(CAP_FLAG) + 2, arm
        else:
            assert FLAG not in cmd, arm
