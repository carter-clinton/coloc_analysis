"""Wave 1 test: URL format validation + MVP sub-accession presence.

Validates config/replication_cohorts.yaml structure independent of
downstream production code. RED-free in Wave 1.
"""
import pytest


def test_finngen_url_format(replication_cohorts_config):
    cfg = replication_cohorts_config["cohorts"]["finngen_r12"]
    assert cfg["http_mirror"].startswith(
        "https://storage.googleapis.com/finngen-public-data-r12"
    )
    assert cfg["file_pattern"] == "finngen_R12_{endpoint}.gz"
    assert cfg["traits"]["t2d"]["endpoint"] == "T2D"
    assert cfg["traits"]["stroke"]["endpoint"] == "I9_STR_EXH"
    assert cfg["traits"]["hypertension"]["endpoint"] == "I9_HYPTENSESS"


def test_mvp_phs_enumeration(replication_cohorts_config):
    """T2D sub-accessions must be present (DIAMANTE 2022 verified);
    non-T2D traits must have EXPLICIT status (pha ID or NOT_RELEASED).
    """
    cfg = replication_cohorts_config["cohorts"]["mvp_phs001672"]
    t2d = cfg["traits"]["t2d"]
    assert t2d["eur"]["pha"] == "pha004945.1"
    assert t2d["afr"]["pha"] == "pha004943.1"
    for trait in ["hypertension", "stroke", "asthma", "bmi"]:
        entry = cfg["traits"].get(trait)
        assert entry is not None, (
            f"MVP trait {trait} missing — must have explicit entry or "
            f"NOT_RELEASED marker"
        )


def test_bbj_file_pattern(replication_cohorts_config):
    cfg = replication_cohorts_config["cohorts"]["bbj_hum0197_v3"]
    assert cfg["file_pattern"] == "hum0197.v3.BBJ.{trait_code}.v1.zip"
    assert cfg["traits"]["stroke"]["trait_code"] == "IS"
    assert "ischemic-only" in cfg["traits"]["stroke"]["note"].lower()
    assert cfg["traits"]["hypertension"]["trait_code"] == "SBP"
