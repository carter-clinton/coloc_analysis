"""D-11 durable storage + REQ-PATH-PARAMETERIZATION + REQ-PUBLIC-DATA-ONLY enforcer."""
from __future__ import annotations

import csv
import os
import re
import subprocess
from pathlib import Path

import yaml

from .conftest import MAN_DIR, REPO_ROOT

BANNED_LITERALS = ("/rs1/researchers", "/share/clintonlab", "/gpfs_common")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def storage_violations(repo_root):
    """Reasons data/r4 under repo_root is not a symlink to a directory on /rs1."""
    link = Path(repo_root) / "data/r4"
    out = []
    if not os.path.islink(link):
        out.append(f"{link} is not a symlink")
    real = os.path.realpath(link)
    if not real.startswith("/rs1/"):
        out.append(f"realpath {real} is not under /rs1/")
    if not os.path.isdir(real):
        out.append(f"realpath {real} is not a directory")
    return out


def r4_scan_paths(repo_root):
    """Files covered by the literal scan; re-globbed at every run."""
    root = Path(repo_root)
    paths = []
    for d in ("config/ta_r4", "src/python/ta_r4", "src/snakemake/scripts/ta_r4"):
        paths += [p for p in (root / d).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    paths += sorted((root / "src/snakemake/rules").glob("ta_r4_*.smk"))
    if (root / "Snakefile.ta_r4").is_file():
        paths.append(root / "Snakefile.ta_r4")
    return paths


def literal_violations(paths):
    out = []
    for p in paths:
        text = Path(p).read_text(errors="replace")
        out += [f"{p}: {lit}" for lit in BANNED_LITERALS if lit in text]
    return out


def manifest_violations(tsv_path):
    """sha256 values must be 64-hex; the path column (first *path column, else col 0) unique."""
    with open(tsv_path, newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    if not rows or "sha256" not in rows[0]:
        return []
    cols = list(rows[0].keys())
    key = next((c for c in cols if c == "path" or c.endswith("_path")), cols[0])
    out = [f"{tsv_path}: bad sha256 {r['sha256']!r}" for r in rows if not HEX64.match(r["sha256"] or "")]
    seen = set()
    for r in rows:
        if r[key] in seen:
            out.append(f"{tsv_path}: duplicate {key} {r[key]!r}")
        seen.add(r[key])
    return out


def data_source_violations(doc):
    sources = (doc or {}).get("sources") or {}
    if not sources:
        return ["no sources"]
    return [
        f"{name}: needs non-empty license and public: true"
        for name, v in sources.items()
        if not (isinstance(v, dict) and v.get("license") and v.get("public") is True)
    ]


def test_data_r4_realpath_on_rs1():
    real = os.path.realpath(REPO_ROOT / "data/r4")
    assert real.startswith("/rs1/"), real
    assert os.path.isdir(real), real


def test_data_r4_is_a_symlink_not_a_dir():
    assert os.path.islink(REPO_ROOT / "data/r4")


def test_check_function_rejects_share_target(tmp_path):
    target = tmp_path / "elsewhere"
    target.mkdir()
    (tmp_path / "data").mkdir()
    os.symlink(target, tmp_path / "data/r4")
    assert not str(target.resolve()).startswith("/rs1/")
    assert storage_violations(tmp_path)
    # a real directory (not a link) is also rejected
    (tmp_path / "data/r4").unlink()
    (tmp_path / "data/r4").mkdir()
    assert any("not a symlink" in v for v in storage_violations(tmp_path))


def test_no_rs1_or_share_literals_in_r4_config_and_src(tmp_path):
    paths = r4_scan_paths(REPO_ROOT)
    assert paths, "scan covers no files"
    assert literal_violations(paths) == []
    bad = tmp_path / "bad.yaml"
    bad.write_text("x: /rs1/researchers/x\n")
    assert literal_violations([bad])


def test_manifests_parse(tmp_path):
    tsvs = sorted(MAN_DIR.glob("*.tsv"))
    with_sha = [p for p in tsvs if "sha256" in p.read_text().splitlines()[0].split("\t")]
    assert with_sha, f"no sha256 manifest under {MAN_DIR}"
    assert [v for p in with_sha for v in manifest_violations(p)] == []
    bad = tmp_path / "bad.tsv"
    bad.write_text("rel_path\tsha256\na\t" + "0" * 64 + "\na\tnothex\n")
    viol = manifest_violations(bad)
    assert any("bad sha256" in v for v in viol) and any("duplicate" in v for v in viol)


def test_data_sources_public():
    with open(REPO_ROOT / "config/ta_r4/data_sources.yaml") as fh:
        doc = yaml.safe_load(fh)
    assert data_source_violations(doc) == []
    assert data_source_violations({"sources": {"x": {"license": "CC0", "public": "yes"}}})
    assert data_source_violations({"sources": {"x": {"license": "", "public": True}}})


def test_data_r4_gitignored():
    def ignored(rel):
        return subprocess.run(["git", "-C", str(REPO_ROOT), "check-ignore", "-q", rel]).returncode

    assert ignored("data/r4") == 0
    assert ignored("data/r4_not_ignored_probe") == 1
