"""Every production job re-runs the lock gate first and checks its inputs (W3f 15.2, review N4/N5); bin/r4_fire.sh refuses
a dirty locked path using the gate's own list.

The rendered shells come from `$SMK -n -p` on a fixture repo with a fixture lock (tmp_path only, §B.12)."""
from __future__ import annotations

import csv
import os
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path

import pytest
import yaml

from ta_r4 import commands, paths
from ta_r4 import harmonize_qtl_r4 as H
from ta_r4 import run_qtl_group_r4 as Q
from ta_r4.r4_lock_gate import LOCKED_PATHS

from .conftest import REPO_ROOT
from .fixtures.make_fixture_repo import git, make_fixture_repo, write_fixture_lock
from .test_lock_gate import SMK

pytestmark = pytest.mark.r4_heavy
REG = "SH2B3_12q24"
PRODUCTION_RULES = ("r4_run_finemap", "r4_coloc_pair", "r4_coloc_A1", "r4_sim", "r4_qtl_group", "r4_qtl_aggregate",
                    "r4_qtl_tiers")
REPO_COPIES = ("config/susie_policy.yaml", "config/qtl_sources.yaml", "config/pph4_thresholds.yaml",
               "src/legacy/region_analysis/scripts/run_susie_rss.R", "src/snakemake/scripts",
               paths.panel_manifest_path("A3_1kg", "EUR"), H.DL_MANIFEST)


def _write(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, header, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def build_gate_repo(tmp_path):
    """Fixture repo, one QTL group and one admissible EUR pair row in SH2B3_12q24, locked; data leaves touched."""
    repo = make_fixture_repo(tmp_path)
    for rel in REPO_COPIES:
        src, dst = REPO_ROOT / rel, repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, dst)
    rows = H.manifest_rows(str(REPO_ROOT / H.MANIFEST))
    grp = sorted(g for g in H.groups(rows) if g[2] == REG)[0]
    with open(REPO_ROOT / H.MANIFEST) as fh:
        _write(repo / H.MANIFEST, fh.readline().rstrip("\n").split("\t"),
               [r for r in rows if (r["source"], r["qtd"], r["region_safe"]) == grp])
    with open(REPO_ROOT / "config/ta_r4/pair_manifest.tsv", newline="") as fh:
        prs = list(csv.DictReader(fh, delimiter="\t"))
    row = next(r for r in prs if r["admissible"] == "true" and r["ancestry"] == "EUR" and r["region_safe"] == REG)
    _write(repo / "config/ta_r4/pair_manifest.tsv", list(prs[0]), [row])
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "gate fixture inputs")
    write_fixture_lock(repo)
    traits = sorted({r["trait"] for r in rows if (r["source"], r["qtd"], r["region_safe"]) == grp}
                    | {row["trait_a"], row["trait_b"]})
    sim = yaml.safe_load((repo / "config/ta_r4/simulation.yaml").read_text())
    leaves = [paths.sumstats_path(t, "EUR", "A3_1kg") for t in traits] + [
        paths.catalog_path("r4", REG), paths.panel_path("A3_1kg", REG, "EUR"), H.download_path(grp[1]),
        H.download_path(grp[1]) + ".tbi"] + [f"data/r4/ld/{p}/{REG}.rds" for p in {sim["fit_panel"], *sim["gen_panels"].values()}]
    old = time.time() - 3600
    for f in leaves + [H.done_path(*grp)]:
        (repo / f).parent.mkdir(parents=True, exist_ok=True)
        (repo / f).write_text("fixture\n")
        os.utime(repo / f, (old, old))
    os.utime(repo / H.done_path(*grp), None)
    scen = sorted(sim["scenarios"])[0]
    targets = [paths.fit_json("A3_1kg", traits[0], "EUR", REG), commands.coloc_output("A3_1kg", row, "p12_primary", "susie"),
               commands.coloc_output("A3_1kg", row, "p12_primary", "A1_allvars"),
               f"data/r4/results/sim/{REG}.{scen}.gen_1kg.tsv", Q.done_path("QTL_A3", REG, grp[0], grp[1]),
               "data/r4/results/QTL_A3/qtl_coloc_summary.tsv", "data/r4/results/QTL_A3/qtl_tiers.tsv"]
    return repo, row, targets


def dry_run(repo, targets):
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_A3_1kg.yaml"]
    p = subprocess.run([SMK, *targets, "-s", "Snakefile.ta_r4", "-d", ".", "-n", "-p", "--configfile", *cfg], cwd=repo,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def jobs(out):
    """[(rule, {attr: value}, [commands])] from the `-n -p` listing; commands split on newlines and `&&`."""
    body = out.split("\nJob stats:", 2)
    text = body[1] if len(body) > 2 else out
    res = []
    for blk in re.split(r"(?m)^\[[^\]\n]+\]$", text)[1:]:
        lines = blk.strip("\n").splitlines()
        m = re.fullmatch(r"(?:local)?rule (\w+):", lines[0])
        if not m:
            continue
        attrs, i = {}, 1
        while i < len(lines) and re.match(r"^    \w+: ", lines[i]):
            k, v = lines[i].strip().split(": ", 1)
            attrs[k] = v
            i += 1
        shell = "\n".join(lines[i:]).split("\nJob stats:")[0]
        cmds = [c.strip() for ln in shell.splitlines() for c in ln.split("&&")]
        res.append((m.group(1), attrs, [c for c in cmds if c and c != "set -euo pipefail"]))
    return res


def _strip_redirect(cmd):
    a = shlex.split(cmd)
    while a and (a[-1] == "2>&1" or (len(a) >= 2 and a[-2] in (">", ">>"))):
        a = a[:-1] if a[-1] == "2>&1" else a[:-2]
    return a


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    repo, row, targets = build_gate_repo(tmp_path_factory.mktemp("gate"))
    rc, out = dry_run(repo, targets)
    assert rc == 0, out[-3000:]
    return repo, row, jobs(out)


@pytest.mark.parametrize("rule", PRODUCTION_RULES)
def test_production_shell_begins_with_the_gate(rendered, rule):
    _, _, js = rendered
    mine = [j for j in js if j[0] == rule]
    assert mine, f"{rule} not in the dry-run"
    assert [c[0] if c else None for _, _, c in mine] == [shlex.join(commands.gate_command("production"))] * len(mine)


def test_fit_shell_verifies_its_inputs_after_the_gate(rendered):
    _, _, js = rendered
    fits = [j for j in js if j[0] == "r4_run_finemap"]
    assert len(fits) == 5
    for _, attrs, cmds in fits:
        w = dict(kv.split("=", 1) for kv in attrs["wildcards"].split(", "))
        assert shlex.split(cmds[1]) == commands.verify_command("A3_1kg", w["trait"], w["ancestry"], w["region"])


@pytest.mark.parametrize("rule,mode", [("r4_coloc_pair", "susie"), ("r4_coloc_A1", "A1_allvars")])
def test_coloc_shell_verifies_both_sumstats_after_the_gate(rendered, rule, mode):
    _, row, js = rendered
    (_, _, cmds), = [j for j in js if j[0] == rule]
    assert _strip_redirect(cmds[1]) == commands.coloc_verify_command("A3_1kg", row, mode)


def test_gate_in_a_job_fails_after_locked_path_drift(rendered):
    repo, _, js = rendered
    gate = shlex.split([c for r, _, c in js if r == "r4_run_finemap"][0][0])
    before = subprocess.run(gate, cwd=repo, capture_output=True, text=True)
    print("gate rc before drift", before.returncode)
    assert before.returncode == 0, before.stderr
    pol = repo / "config/susie_policy.yaml"
    keep = pol.read_text()
    pol.write_text(keep + "# drift\n")
    git(repo, "commit", "-qam", "drift after lock")
    try:
        after = subprocess.run(gate, cwd=repo, capture_output=True, text=True)
    finally:
        pol.write_text(keep)
        git(repo, "commit", "-qam", "restore")
    print("gate rc after drift", after.returncode)
    assert after.returncode == 1 and "(g) locked paths drifted" in after.stderr and "config/susie_policy.yaml" in after.stderr


def test_gate_command_stages():
    assert commands.gate_command("production") == commands._PY + ["ta_r4.r4_lock_gate", "check", "--stage", "production"]
    assert commands.gate_command("repro") == ["true"]
    with pytest.raises(ValueError):
        commands.gate_command("prod")


# ---- bin/r4_fire.sh DIRTY check uses the gate's list ----------------------------------------------------------------

REAL_PY = shutil.which("python3.11", path=str(Path(SMK).parent)) or str(Path(SMK).parent / "python3.11")


def _fire_repo(tmp_path):
    repo = tmp_path / "fire"
    for rel in ("bin/r4_fire.sh", "src/python/ta_r4", "config/susie_policy.yaml"):
        src, dst = REPO_ROOT / rel, repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__")) if src.is_dir() else shutil.copy2(src, dst))
    (repo / "bin/r4_link_storage.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    for n in ("ta_r4_a.smk", "ta_r4_b.smk"):
        (repo / "src/snakemake/rules").mkdir(parents=True, exist_ok=True)
        (repo / "src/snakemake/rules" / n).write_text("# rules\n")
    (repo / ".gitignore").write_text("/data/\n__pycache__/\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fire fixture")
    stub = tmp_path / "stub"
    stub.mkdir()
    (stub / "py").write_text("#!/usr/bin/env bash\n"
                             'if [ "$1 $2 $3" = "-m ta_r4.r4_lock_gate check" ]; then echo stub gate OK; exit 0; fi\n'
                             f'exec {REAL_PY} "$@"\n')
    (stub / "smk").write_text(f'#!/usr/bin/env bash\necho "$@" > {stub}/smk_called\nexit 0\n')
    for f in ("py", "smk"):
        (stub / f).chmod(0o755)
    return repo, stub


def _fire(repo, stub):
    (stub / "smk_called").unlink(missing_ok=True)
    env = dict(os.environ, R4_FIRE_PY=str(stub / "py"), R4_FIRE_SMK=str(stub / "smk"))
    p = subprocess.run(["bash", "bin/r4_fire.sh", "production", "A3_1kg", "-n"], cwd=repo, capture_output=True,
                       text=True, env=env)
    return p, (stub / "smk_called").exists()


def test_fire_stub_paths_prints_the_real_locked_paths(tmp_path):
    repo, stub = _fire_repo(tmp_path)
    p = subprocess.run([str(stub / "py"), "-m", "ta_r4.r4_lock_gate", "paths"], cwd=repo / "src/python",
                       capture_output=True, text=True)
    assert p.returncode == 0 and tuple(p.stdout.splitlines()) == LOCKED_PATHS


def test_fire_clean_tree_reaches_snakemake(tmp_path):
    repo, stub = _fire_repo(tmp_path)
    p, called = _fire(repo, stub)
    assert p.returncode == 0 and called, p.stderr
    assert "every production job re-runs the lock gate" in p.stdout


def _dirty(repo, case):
    rules = repo / "src/snakemake/rules"
    if case == "susie_policy":
        with open(repo / "config/susie_policy.yaml", "a") as fh:
            fh.write("# drift\n")
        return ["config/susie_policy.yaml"]
    if case == "glob_new_and_modified":
        (rules / "ta_r4_new.smk").write_text("# new\n")
        (rules / "ta_r4_a.smk").write_text("# edited\n")
        return ["src/snakemake/rules/ta_r4_new.smk", "src/snakemake/rules/ta_r4_a.smk"]
    if case == "glob_deleted":
        (rules / "ta_r4_b.smk").unlink()
        return ["src/snakemake/rules/ta_r4_b.smk"]
    raise ValueError(case)


@pytest.mark.parametrize("case", ["susie_policy", "glob_new_and_modified", "glob_deleted"])
def test_fire_refuses_a_dirty_locked_path(tmp_path, case):
    repo, stub = _fire_repo(tmp_path)
    names = _dirty(repo, case)
    p, called = _fire(repo, stub)
    assert p.returncode == 2 and "REFUSED" in p.stderr and not called, (p.returncode, p.stderr[-2000:])
    assert all(n in p.stderr for n in names), p.stderr
