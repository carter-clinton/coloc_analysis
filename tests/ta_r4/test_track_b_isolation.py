"""Track B isolation (D-04, D-15): no R4 path reaches a Track B panel or sumstats tree."""
from __future__ import annotations

import csv
import io
import subprocess
import sys
import tokenize
from pathlib import Path

import pytest

from .conftest import REPO_ROOT, merged_config

from ta_r4 import paths as r4paths
from ta_r4.arms import ARMS, arm_ancestries

sys.path.insert(0, str(REPO_ROOT / "src/python"))
from ld_panel import resolve_ld_path  # noqa: E402
from build_curated_m2_crosswalk import load_curated_to_m2  # noqa: E402

FORBIDDEN = ("EUR_ukbb_pub", "EUR_ukbb_ld", "EUR_aou", "AFR_aou", "data/processed/ld_reference/",
             "sumstats_harmonized_occl")
ALLOWED_PREFIXES = ("data/r4/", "data/processed/sumstats_harmonized/")
MANIFEST = REPO_ROOT / "config/ta_r4/pair_manifest.tsv"
REGIONS = REPO_ROOT / "config/ta_r4/regions_r4.csv"
SMK = str(Path(sys.executable).parent / "snakemake")


def _rows(p, delim):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh, delimiter=delim))


def _safe(region_id):
    return region_id.replace(".", "_").replace("/", "_")


def arm_row_paths(paths_mod=r4paths):
    """Every path ta_r4.paths gives for every arm x manifest row it applies to."""
    out = []
    for arm, spec in ARMS.items():
        for row in _rows(MANIFEST, "\t"):
            anc, safe = row["ancestry"], row["region_safe"]
            if anc not in arm_ancestries(arm):
                continue
            out.append(paths_mod.panel_path(arm, safe, anc))
            for t in (row["trait_a"], row["trait_b"]):
                out += [paths_mod.fit_json(arm, t, anc, safe), paths_mod.fit_rds(arm, t, anc, safe),
                        paths_mod.ld_receipt_json(arm, t, anc, safe), paths_mod.sumstats_path(t, anc, arm)]
            out.append(paths_mod.catalog_path(spec["route"], safe))
            out.append(paths_mod.coloc_json(arm, row["row_id"], "p12_primary"))
    for a1 in ("A1_EUR", "A1_AFR"):
        out.append(paths_mod.coloc_json(a1, "x__EUR__a_vs_b", "p12_primary", varset="matched"))
    out += paths_mod.result_dirs("fits") + paths_mod.result_dirs("coloc")
    out += [paths_mod.ld_dir_unused(), paths_mod.regions_csv()]
    return out


def isolation_violations(paths):
    bad = []
    for p in paths:
        if p == r4paths.regions_csv():
            continue
        if not p.startswith(ALLOWED_PREFIXES) or any(f in p for f in FORBIDDEN):
            bad.append(p)
    return bad


def test_every_arm_row_path_is_isolated():
    paths = arm_row_paths()
    assert len(paths) > 10_000
    assert isolation_violations(paths) == []


def test_isolation_check_reports_a_track_b_panel(monkeypatch):
    monkeypatch.setattr(r4paths, "panel_path",
                        lambda arm, safe, anc=None: "data/processed/ld_reference/EUR_ukbb_pub/x.rds")
    bad = isolation_violations(arm_row_paths(r4paths))
    assert bad and set(bad) == {"data/processed/ld_reference/EUR_ukbb_pub/x.rds"}


@pytest.mark.parametrize("p", ["data/processed/sumstats_harmonized_occl/bmi.EUR.tsv.bgz",
                               "data/processed/ld_reference/EUR/FTO_16q12.rds", "data/r4/ld/EUR_aou/x.rds"])
def test_isolation_check_reports_forbidden(p):
    assert isolation_violations([p]) == [p]


def test_r4_paths_independent_of_crosswalk(tmp_path, monkeypatch):
    regions = _rows(REGIONS, ",")
    assert len(regions) == 31
    monkeypatch.chdir(tmp_path)
    n = 0
    for arm in ARMS:
        cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml")
        for anc in arm_ancestries(arm):
            for r in regions:
                safe = _safe(r["region_id"])
                want = r4paths.panel_path(arm, safe, anc)
                Path(want).parent.mkdir(parents=True, exist_ok=True)
                Path(want).touch()
                got = resolve_ld_path(region_id=safe, ancestry=anc, config=cfg, region_safe=safe)
                assert str(got) == want, (arm, anc, safe)
                n += 1
    assert n == 31 * sum(len(arm_ancestries(a)) for a in ARMS)


def test_nc_ids_absent_from_crosswalk():
    xwalk = load_curated_to_m2(REPO_ROOT / "config/curated_to_m2_region_map.tsv")
    assert xwalk, "crosswalk did not load"
    nc = {_safe(r["region_id"]) for r in _rows(REGIONS, ",") if r["source"].startswith("negative_control")}
    assert len(nc) == 19
    assert not nc & set(xwalk)


def _name_tokens(path):
    toks = tokenize.generate_tokens(io.StringIO(Path(path).read_text()).readline)
    return {t.string for t in toks if t.type == tokenize.NAME}


def test_r4_rules_never_call_ld_matrix_region_id():
    files = [REPO_ROOT / "Snakefile.ta_r4", *sorted((REPO_ROOT / "src/snakemake/rules").glob("ta_r4_*.smk"))]
    assert len(files) >= 2
    hits = [f.name for f in files if {"ld_matrix_region_id", "CURATED_TO_M2", "load_curated_to_m2"} & _name_tokens(f)]
    assert hits == []


@pytest.mark.r4_heavy
def test_dry_run_shell_commands_isolated():
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_repro_routeC.yaml"]
    r = subprocess.run([SMK, "r4_env_probe_all", "-s", "Snakefile.ta_r4", "-n", "-F", "--printshellcmds",
                        "--configfile", *cfg], cwd=REPO_ROOT, capture_output=True, text=True)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-2000:]
    assert "plink --version" in out and "r4_env_probe_python_stats" in out
    assert [f for f in FORBIDDEN if f in out] == []


# --- bin/r4_fire.sh ------------------------------------------------------------------------------

FIRE = REPO_ROOT / "bin/r4_fire.sh"


def _fire(*args):
    return subprocess.run(["bash", str(FIRE), *args], cwd=REPO_ROOT, capture_output=True, text=True)


def test_fire_conda_pkgs_dirs_is_exactly_the_r4_cache():
    r = _fire("--show-conda-pkgs-dirs")
    assert r.returncode == 0, r.stderr
    dirs = [l.strip()[2:] for l in r.stdout.splitlines() if l.strip().startswith("- ")]
    assert len(dirs) == 1, dirs
    assert dirs[0].endswith("/conda_envs/smk_job_envs/ta_r4/pkgs")


@pytest.mark.parametrize("args,needle", [
    (("production", "repro_routeC", "-n", "r4_gate_probe_repro"), "is stage 'repro', not 'production'"),
    (("repro", "A3_1kg", "-n", "r4_gate_probe"), "is stage 'production', not 'repro'"),
    (("repro", "no_such_arm", "-n"), "unknown arm"),
    (("repro", "repro_routeC", "--conda-cleanup-pkgs", "tarballs"), "--conda-cleanup-pkgs"),
    (("production",), "usage"),
])
def test_fire_refusals(args, needle):
    r = _fire(*args)
    assert r.returncode == 2
    assert needle in r.stderr, r.stderr
