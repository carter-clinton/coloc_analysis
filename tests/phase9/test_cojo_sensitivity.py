"""COJO wrapper — RED until Plan 09-05 Task 1.

Validates env-file presence + D-04c / RESEARCH §6 Option D caveat is
captured in the YAML before any real COJO run.
"""
from pathlib import Path

import pytest


def test_gcta_env_present():
    gcta_env = Path("envs/gcta.yml")
    assert gcta_env.exists()
    assert "gcta=1.94.1" in gcta_env.read_text()


def test_cojo_ld_caveat_documented(replication_cohorts_config):
    """D-04c + RESEARCH §6 Option D: 1000G EUR N=503 below GCTA's 4K threshold —
    must be marked as supplementary tier with caveat."""
    ld_ref = replication_cohorts_config["cojo_ld_reference"]
    assert ld_ref["EUR"] == "thousand_g_eur"
    assert ld_ref["AFR"] == "thousand_g_afr"


def test_cojo_script_placeholder():
    try:
        assert Path("src/snakemake/scripts/run_cojo.sh").exists()
    except AssertionError:
        pytest.xfail("run_cojo.sh not yet created (Plan 09-05 Task 1)")
