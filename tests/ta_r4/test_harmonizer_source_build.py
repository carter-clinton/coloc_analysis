"""The legacy harmonizer refuses to stamp BUILD with a build its source is not in (asthma.EUR GRCh38 mislabel)."""
from __future__ import annotations

import subprocess
import sys

import yaml

from .conftest import REPO_ROOT

SCRIPT = REPO_ROOT / "src/legacy/region_analysis/scripts/harmonize_sumstats.py"
sys.path.insert(0, str(REPO_ROOT / "src/legacy/region_analysis"))
from scripts.dataset_config import dataset_descriptor  # noqa: E402


def _run(tmp_path, source_build):
    cfg = {"datasets": {"toy": {"defaults": {"sep": "\t"}, "traits": {"tt": {"ancestries": {"EUR": {"path": "x"}}}}}}}
    if source_build:
        cfg["datasets"]["toy"]["source_build"] = source_build
    (tmp_path / "datasets.yaml").write_text(yaml.safe_dump(cfg))
    (tmp_path / "in.tsv").write_text("CHR\tPOS\tREF\tALT\tBETA\tSE\tP\tSNP\n1\t100\tA\tG\t0.1\t0.05\t0.04\trs1\n")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(tmp_path / "in.tsv"), "--output", str(tmp_path / "out.tsv"),
         "--trait", "tt", "--ancestry", "EUR", "--build", "GRCh37", "--dataset-name", "toy",
         "--datasets-config", str(tmp_path / "datasets.yaml")],
        capture_output=True, text=True,
    )


def test_gbmi_asthma_declares_grch38():
    for anc in ("EUR", "AFR"):
        d = dataset_descriptor(trait="asthma", ancestry=anc, config_path=str(REPO_ROOT / "config/datasets.yaml"),
                               dataset_name="gbmi_asthma")
        assert d["source_build"] == "GRCh38"


def test_refuses_to_stamp_grch37_on_grch38_source(tmp_path):
    p = _run(tmp_path, "GRCh38")
    assert p.returncode != 0 and "does not lift over" in p.stderr
    assert not (tmp_path / "out.tsv").exists()


def test_matching_or_undeclared_source_build_harmonizes(tmp_path):
    for sb in ("GRCh37", None):
        p = _run(tmp_path, sb)
        assert p.returncode == 0, p.stderr
        assert (tmp_path / "out.tsv").read_text().splitlines()[1].endswith("\tGRCh37")
