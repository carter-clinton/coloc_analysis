"""Every Track A sumstats file's build, measured by anchor positions, equals its declared build."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ta_r4 import sumstats_build as B

from .conftest import REPO_ROOT

SOURCES = yaml.safe_load((REPO_ROOT / "config/ta_r4/data_sources.yaml").read_text())["sources"]
SUMSTATS = sorted(k for k in SOURCES if k.startswith("sumstats_"))
PINNED_ASTHMA_EUR = REPO_ROOT / "data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz"
TABIX = "/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin/tabix"


def _measure(path):
    if not Path(path).exists():
        pytest.skip(f"{path} not present")
    if not Path(f"{path}.tbi").exists():
        pytest.skip(f"{path} has no tabix index")
    return B.infer_build(B.build_hits(path, TABIX))


def test_eight_track_a_sumstats_entries():
    assert len(SUMSTATS) == 8


def test_infer_build_rule():
    assert B.infer_build({"GRCh37": 657, "GRCh38": 0}) == "GRCh37"
    assert B.infer_build({"GRCh37": 1, "GRCh38": 657}) == "GRCh38"
    assert B.infer_build({"GRCh37": 300, "GRCh38": 300}) == "indeterminate"
    assert B.infer_build({"GRCh37": 10, "GRCh38": 0}) == "indeterminate"


PROVENANCE = [(k, f) for k in SUMSTATS for f in ("lifted_from", "legacy_route_input") if f in SOURCES[k]]


@pytest.mark.r4_heavy
@pytest.mark.parametrize("key", SUMSTATS)
def test_measured_build_equals_declared(key):
    src = SOURCES[key]
    assert _measure(REPO_ROOT / src["url"]) == src["build"]


@pytest.mark.r4_heavy
@pytest.mark.parametrize("key,field", PROVENANCE)
def test_provenance_inputs_measured_build_equals_declared(key, field):
    src = SOURCES[key][field]
    assert _measure(REPO_ROOT / src["path"]) == src["build"]


def test_asthma_provenance_recorded():
    assert {k for k, _ in PROVENANCE} == {"sumstats_asthma_EUR", "sumstats_asthma_AFR"}


@pytest.mark.r4_heavy
def test_negative_control_pinned_asthma_eur_measures_grch38():
    assert _measure(PINNED_ASTHMA_EUR) == "GRCh38"
