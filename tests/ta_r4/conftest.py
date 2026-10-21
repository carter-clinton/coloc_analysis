"""Shared fixtures and constants for tests/ta_r4 (ta-r4 head-to-head re-analysis)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

_SRC_PYTHON = REPO_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

PHASE_DIR = REPO_ROOT / ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission"
MAN_DIR = PHASE_DIR / "manifests"
R4_ROOT = "/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4"


def merged_config(*overlay_paths):
    """config/pipeline.yaml with each overlay applied in order (Snakemake semantics)."""
    from snakemake.utils import update_config

    with open(REPO_ROOT / "config/pipeline.yaml") as fh:
        cfg = yaml.safe_load(fh)
    for p in overlay_paths:
        with open(REPO_ROOT / p) as fh:
            update_config(cfg, yaml.safe_load(fh) or {})
    return cfg


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "r4_heavy: real-data live gates, Snakemake runs/dry-runs, frozen-script R "
        "end-to-end; run per wave via HEAVY, deselected by QUICK",
    )
