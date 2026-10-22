"""D-13 / D-28 end to end: the FROZEN run_susie_rss.R, armed only by R4 flags, reads the declared EUR panel
allele-aware on a fixture region; a missing declared panel does not pass; the r4_run_finemap rule runs.

Every command is built by ta_r4.commands, the same functions the rule joins with shlex.join.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import REPO_ROOT, merged_config

from ta_r4 import paths
from ta_r4.arms import ARMS

pytestmark = pytest.mark.r4_heavy

RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
HTS_BIN = "/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin"
SMK = str(Path(sys.executable).parent / "snakemake")
FROZEN_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
BUILDER = REPO_ROOT / "tests/ta_r4/fixtures/build_fixture_region.R"
PAYLOAD = REPO_ROOT / "src/snakemake/scripts/ta_r4/make_matched_identity_payload.R"
TRAIT, ANC, REGION = "hypertension", "EUR", "FIX_1"
HDR = ["ancestry", "region_safe", "path", "md5", "sha256", "size_bytes", "n_var", "n_samples", "build",
       "source", "has_ref_alt"]


def _env():
    return dict(os.environ, PATH=f"{Path(RSCRIPT).parent}:{os.environ['PATH']}")


def _run(cmd, cwd):
    return subprocess.run([str(c) for c in cmd], cwd=cwd, env=_env(), capture_output=True, text=True)


def _ok(p):
    assert p.returncode == 0, f"rc={p.returncode}\nSTDOUT\n{p.stdout[-3000:]}\nSTDERR\n{p.stderr[-3000:]}"
    return p


def _write_manifest(root, arm, panel_rel, region_safe, anc=ANC):
    data = (root / panel_rel).read_bytes()
    mp = root / paths.panel_manifest_path(arm, anc)
    mp.parent.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(mp), delimiter="\t")) if mp.exists() else []
    rows.append(dict(ancestry=anc, region_safe=region_safe, path=panel_rel, md5=hashlib.md5(data).hexdigest(),
                     sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data), n_var=60, n_samples=400,
                     build="GRCh37", source="fixture", has_ref_alt="true"))
    with open(mp, "w", newline="") as fh:
        w = csv.DictWriter(fh, HDR, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


def build_fixture(root, arm="A3_1kg", region=REGION, chr_="1", start=1000, regions_rel=None):
    """Fixture inputs at their R4 repo-relative paths under `root`; the frozen script by symlink."""
    route = ARMS[arm]["route"]
    panel = paths.panel_path(arm, region, ANC)
    _ok(_run([RSCRIPT, BUILDER, "--panel", root / panel,
              "--sumstats", root / paths.sumstats_path(TRAIT, ANC, arm),
              "--catalog", root / paths.catalog_path(route, region),
              "--regions", root / (regions_rel or paths.regions_csv()),
              "--region-id", region, "--chr", chr_, "--start", start,
              "--bgzip", f"{HTS_BIN}/bgzip", "--tabix", f"{HTS_BIN}/tabix"], root))
    _write_manifest(root, arm, panel, region)
    for rel in (ARMS[arm]["policy"], "config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml",
                "config/ta_r4/overlay_A2_identity.yaml"):
        if not (root / rel).exists():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / rel, root / rel)
    for rel in (FROZEN_REL, "src/python"):
        link = root / rel
        if not link.exists():
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(REPO_ROOT / rel)
    return panel


def fit_arm(root, arm, trait=TRAIT, anc=ANC, region=REGION):
    from ta_r4 import commands
    cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml")
    rec = _run(commands.receipt_command(arm, trait, anc, region), root)
    fit = _run(commands.fit_command(arm, trait, anc, region, cfg, region_id=region), root)
    val = _run(commands.validate_command(arm, trait, anc, region), root)
    out = root / paths.fit_json(arm, trait, anc, region)
    return {"receipt": rec, "fit": fit, "validate": val,
            "json": json.loads(out.read_text()) if out.exists() else None,
            "receipt_json": json.loads((root / paths.ld_receipt_json(arm, trait, anc, region)).read_text())
            if (root / paths.ld_receipt_json(arm, trait, anc, region)).exists() else None}


def retained_ids(root, arm, trait=TRAIT, anc=ANC, region=REGION):
    """Variant ids the fit was computed on: names(fit$pip) of the .fit.rds (one per retained variant)."""
    rds = root / paths.fit_rds(arm, trait, anc, region)
    p = _ok(_run([RSCRIPT, "-e", f'f <- readRDS("{rds}"); stopifnot(!is.null(names(f$pip))); '
                                 f'cat(names(f$pip), sep = "\\n")'], root))
    return [ln for ln in p.stdout.splitlines() if ln]


@pytest.fixture(scope="session")
def r4_e2e(tmp_path_factory):
    root = tmp_path_factory.mktemp("r4_e2e")
    a3 = build_fixture(root)
    a2 = paths.panel_path("A2_identity", REGION, ANC)
    _ok(_run([RSCRIPT, PAYLOAD, "--in", root / a3, "--out", root / a2], root))
    _write_manifest(root, "A2_identity", a2, REGION)
    return {"root": root, "A3_1kg": fit_arm(root, "A3_1kg"), "A2_identity": fit_arm(root, "A2_identity")}


# ------------------------------------------------------------------------------------------------

def test_command_runs_the_frozen_script(r4_e2e):
    from ta_r4 import commands
    cfg = merged_config("config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_A3_1kg.yaml")
    cmd = commands.fit_command("A3_1kg", TRAIT, ANC, REGION, cfg, region_id=REGION)
    assert FROZEN_REL in cmd
    assert (r4_e2e["root"] / FROZEN_REL).resolve() == (REPO_ROOT / FROZEN_REL).resolve()
    assert subprocess.run(["git", "diff", "--quiet", "HEAD", "--", FROZEN_REL], cwd=REPO_ROOT).returncode == 0
    i = cmd.index
    assert cmd[i("--ld-authoritative") + 1] == "true" and cmd[i("--ld-allele-aware") + 1] == "true"
    assert cmd[i("--ld-file") + 1] == paths.panel_path("A3_1kg", REGION, ANC)
    assert cmd[i("--ld-dir") + 1] == paths.ld_dir_unused()
    assert not (r4_e2e["root"] / paths.ld_dir_unused()).exists()


def test_a3_reads_declared_panel_allele_aware(r4_e2e):
    from ta_r4.validate_r4_fits import validate_fit, manifest_row
    r = r4_e2e["A3_1kg"]
    _ok(r["receipt"]), _ok(r["fit"])
    d = r["json"]
    print("A3 fixture:", {k: d.get(k) for k in ("status", "ld_matrix", "ld_status", "ld_allele_flipped",
                                                  "ld_allele_dropped_palindromic", "ld_overlap")})
    assert d["status"] == "ok"
    assert d["ld_matrix"] == d["ld_file_declared"] == paths.panel_path("A3_1kg", REGION, ANC)
    assert d["ld_allele_flipped"] >= 1 and d["ld_allele_dropped_palindromic"] >= 1
    row = manifest_row(r4_e2e["root"] / paths.panel_manifest_path("A3_1kg", ANC), ANC, REGION)
    assert validate_fit(d, r["receipt_json"], row, "real_ld") == []
    assert _ok(r["validate"]).returncode == 0


def test_a2_identity_matched_passes(r4_e2e):
    from ta_r4.validate_r4_fits import validate_fit, manifest_row
    r = r4_e2e["A2_identity"]
    _ok(r["receipt"]), _ok(r["fit"])
    d = r["json"]
    print("A2 fixture:", {k: d.get(k) for k in ("status", "ld_matrix", "ld_status", "ld_overlap")})
    row = manifest_row(r4_e2e["root"] / paths.panel_manifest_path("A2_identity", ANC), ANC, REGION)
    assert validate_fit(d, r["receipt_json"], row, "identity_matched") == []
    assert _ok(r["validate"]).returncode == 0
    # The A2 fit really ran on R = I and A3 on the real panel: their PIPs differ.
    a3 = r4_e2e["A3_1kg"]["json"]
    assert d["pip"] != a3["pip"]


def test_missing_declared_panel_does_not_pass(r4_e2e, tmp_path):
    """Negative control: the same A3 call with the declared panel absent."""
    from ta_r4 import commands
    from ta_r4.validate_r4_fits import validate_fit
    root = tmp_path / "nc"
    shutil.copytree(r4_e2e["root"], root, symlinks=True)
    shutil.rmtree(root / "data/r4/results")
    _ok(_run(commands.receipt_command("A3_1kg", TRAIT, ANC, REGION), root))
    (root / paths.panel_path("A3_1kg", REGION, ANC)).unlink()
    cfg = merged_config("config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_A3_1kg.yaml")
    fit = _run(commands.fit_command("A3_1kg", TRAIT, ANC, REGION, cfg, region_id=REGION), root)
    out = root / paths.fit_json("A3_1kg", TRAIT, ANC, REGION)
    receipt = json.loads((root / paths.ld_receipt_json("A3_1kg", TRAIT, ANC, REGION)).read_text())
    if fit.returncode != 0:
        print("NC outcome: frozen script exited", fit.returncode)
        return
    d = json.loads(out.read_text())
    v = validate_fit(d, receipt, {"md5": receipt["md5"], "sha256": receipt["sha256"]}, "real_ld")
    print("NC outcome: rc 0;", {k: d.get(k) for k in ("ld_matrix", "ld_status", "ld_file_declared")},
          "violations:", v)
    assert v and {"LD_MATRIX_IDENTITY", "LD_DIR_MISSING"} <= set(v)
    val = _run(commands.validate_command("A3_1kg", TRAIT, ANC, REGION), root)
    assert val.returncode == 1 and "VIOLATION LD_MATRIX_IDENTITY" in val.stdout


def _receipt_line(smk):
    lines = [ln.strip() for ln in Path(smk).read_text().splitlines()
             if ln.strip().startswith('{PYTHON_BIN} -c "import json,sys; d=json.load(open(sys.argv[1]));')]
    assert len(lines) == 1, smk
    return lines[0]


def test_receipt_one_liner_matches_finemap_smk(r4_e2e, tmp_path):
    js = r4_e2e["root"] / paths.fit_json("A3_1kg", TRAIT, ANC, REGION)
    outs = []
    for i, smk in enumerate(("src/snakemake/rules/finemap.smk", "src/snakemake/rules/ta_r4_finemap.smk")):
        log = tmp_path / f"{i}.log"
        line = (_receipt_line(REPO_ROOT / smk).replace("{PYTHON_BIN}", sys.executable)
                .replace("{output.json}", str(js)).replace("{wildcards.region}", REGION)
                .replace("{wildcards.ancestry}", ANC).replace("{log.ld_z_consistency}", str(log)))
        subprocess.run(["bash", "-c", line], check=True)
        outs.append(log.read_text())
    assert outs[0] == outs[1]
    assert "ld_receipt_verdict ld_fields_present" in outs[0]


# --- the rule itself, in a fixture repo ---------------------------------------------------------

def _fixture_repo(tmp_path, arm, region):
    from .fixtures.make_fixture_repo import make_fixture_repo
    repo = make_fixture_repo(tmp_path)
    reg = next(r for r in csv.DictReader(open(repo / paths.regions_csv())) if r["region_id"] == region)
    build_fixture(repo, arm=arm, region=region, chr_=reg["chr"], start=int(float(reg["start"])),
                  regions_rel="data/r4/tmp/fixture_regions_unused.csv")
    return repo


def _smk(repo, arm, *args):
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml"]
    return _run([SMK, "-s", "Snakefile.ta_r4", "-d", ".", "--configfile", *cfg, "--cores", "1", *args], repo)


def test_rule_runs_on_fixture_repro_arm(tmp_path):
    from ta_r4 import commands
    arm, region = "repro_routeC", "FTO_16q12"
    repo = _fixture_repo(tmp_path, arm, region)
    target = paths.fit_json(arm, TRAIT, ANC, region)
    p = _ok(_smk(repo, arm, target, "-p"))
    cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml")
    out = p.stdout + p.stderr
    for cmd in (commands.fit_command(arm, TRAIT, ANC, region, cfg, region_id=region),
                commands.receipt_command(arm, TRAIT, ANC, region),
                commands.validate_command(arm, TRAIT, ANC, region)):
        assert shlex.join(cmd) in out
    rc = json.loads((repo / paths.ld_receipt_json(arm, TRAIT, ANC, region)).read_text())
    assert rc["present"] is True and rc["ld_source_class"] == "legacy_panel"
    d = json.loads((repo / target).read_text())
    assert d["ld_matrix"] == paths.panel_path(arm, region, ANC) and d["ld_authoritative"] is False
    logs = list((repo / "data/r4/logs").rglob("*.estimate_s.log"))
    assert len(logs) == 1 and "ld_receipt_verdict ld_fields_present" in logs[0].read_text()


def test_rule_fails_on_panel_swap(tmp_path):
    """Negative control (T-r4-W0c-02): manifest md5 != the panel on disk -> the job fails before R runs."""
    arm, region = "repro_routeC", "FTO_16q12"
    repo = _fixture_repo(tmp_path, arm, region)
    mp = repo / paths.panel_manifest_path(arm, ANC)
    rows = list(csv.DictReader(open(mp), delimiter="\t"))
    rows[0]["md5"] = "f" * 32
    with open(mp, "w", newline="") as fh:
        w = csv.DictWriter(fh, HDR, delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    p = _smk(repo, arm, paths.fit_json(arm, TRAIT, ANC, region))
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "LD_RECEIPT_REFUSED" in out and "!= manifest md5" in out
    assert "Overriding" not in out  # the frozen script never started
    assert not (repo / paths.fit_json(arm, TRAIT, ANC, region)).exists()


def test_rule_production_arm_refused_without_gate(tmp_path):
    arm, region = "A3_1kg", "FTO_16q12"
    repo = _fixture_repo(tmp_path, arm, region)
    p = _smk(repo, arm, paths.fit_json(arm, TRAIT, ANC, region), "-n")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "OsfGateError" in out and "sentinel absent" in out


def test_rule_listed_via_fire_script():
    p = subprocess.run(["bash", "bin/r4_fire.sh", "repro", "repro_routeC", "--list"], cwd=REPO_ROOT,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    assert re.search(r"^r4_run_finemap$", p.stdout, re.M)
