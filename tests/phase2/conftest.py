"""Phase 2 pytest fixtures -- config loaders, fixture paths, region data."""
import csv
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
QTL_FIXTURES_DIR = PROJECT_ROOT / "tests" / "toy_3locus" / "data" / "qtl"


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def config_dir():
    return CONFIG_DIR


@pytest.fixture(scope="session")
def qtl_fixtures_dir():
    return QTL_FIXTURES_DIR


@pytest.fixture(scope="session")
def regions_grch38_path():
    return CONFIG_DIR / "regions_curated_grch38.csv"


@pytest.fixture(scope="session")
def regions_grch38(regions_grch38_path):
    """Load GRCh38 regions CSV as list of dicts."""
    with open(regions_grch38_path, newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="session")
def pph4_config():
    """Load pph4_thresholds.yaml."""
    path = CONFIG_DIR / "pph4_thresholds.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def neg_ctrl_config():
    """Load negative_controls.yaml."""
    path = CONFIG_DIR / "negative_controls.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def qtl_sources_config():
    """Load qtl_sources.yaml."""
    path = CONFIG_DIR / "qtl_sources.yaml"
    with open(path) as f:
        return yaml.safe_load(f)
