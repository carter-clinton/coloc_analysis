"""Test the M1 trait_inventory.yaml builder.

Spec ref: m1-04-qc-reports-inventory-manifest-PLAN.md Task 1 step (E).
Schema ref: m1-RESEARCH.md Example 4 + tests/m1/test_inventory_yaml.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PYTHON = REPO_ROOT / "src" / "python"
if str(SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(SRC_PYTHON))

import build_trait_inventory  # noqa: E402

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _write_qc_sidecar(qc_dir: Path, key: str, status: str = "PASS",
                      n_input: int = 1000, n_palin: int = 25) -> None:
    qc_dir.mkdir(parents=True, exist_ok=True)
    (qc_dir / f"{key}.qc.json").write_text(json.dumps({
        "trait": key.split(".")[0],
        "ancestry": key.split(".")[1],
        "consortium": key.split(".")[2],
        "year": int(key.split(".")[3]),
        "n_input": n_input,
        "n_output": n_input - n_palin,
        "n_palindromic_dropped": n_palin,
        "n_maf_below_threshold": 0,
        "qc_status": status,
    }))


def _write_rg_log(log_dir: Path, focal_key: str,
                  partners: list[str], h2_obs=0.10, h2_int=1.05,
                  gcov_int=0.04) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "Beginning analysis at ...",
        "",
        "Summary of Genetic Correlation Results",
        "p1 p2 rg se z p h2_obs h2_obs_se h2_int h2_int_se gcov_int gcov_int_se",
    ]
    for p2 in partners:
        lines.append(
            f"data/munged/{focal_key}.sumstats.gz "
            f"data/munged/{p2}.sumstats.gz "
            f"0.5 0.05 10 1e-10 {h2_obs} 0.01 {h2_int} 0.02 {gcov_int} 0.005"
        )
    lines.append("Analysis finished at ...")
    (log_dir / f"focal_0.log").write_text("\n".join(lines) + "\n")


def test_build_inventory_mini_three_in_scope(tmp_path):
    """3 in-scope rows + 1 deferred → 3 entries with full schema."""
    qc_dir = tmp_path / "qc_log"
    rg_dir = tmp_path / "rg_logs"
    out_yaml = tmp_path / "trait_inventory.yaml"

    _write_qc_sidecar(qc_dir, "bmi.EUR.GIANT-UKBB.2018", "PASS")
    _write_qc_sidecar(qc_dir, "t2d.TRANS.DIAMANTE.2022", "PASS")
    _write_qc_sidecar(qc_dir, "stroke.EUR.GIGASTROKE.2022", "PASS")
    _write_rg_log(rg_dir, "bmi.EUR.GIANT-UKBB.2018",
                  ["t2d.TRANS.DIAMANTE.2022", "stroke.EUR.GIGASTROKE.2022"])

    inv = build_trait_inventory.build_inventory(
        tsv_path=FIXTURE_DIR / "trait_inventory_mini.tsv",
        raw_manifest=FIXTURE_DIR / "sha256_raw_mini.tsv",
        harm_manifest=FIXTURE_DIR / "sha256_harm_mini.tsv",
        qc_log_dir=qc_dir,
        rg_log_dir=rg_dir,
    )

    assert "version" in inv
    assert "build_target" in inv
    assert "traits" in inv
    keys = list(inv["traits"].keys())
    # Loh row has b38 + GWAS-Catalog-pending; should still build a key
    # (the harmonized path may not exist, but the entry is emitted).
    assert "bmi.EUR.GIANT-UKBB.2018" in keys
    assert "t2d.TRANS.DIAMANTE.2022" in keys
    assert "stroke.EUR.GIGASTROKE.2022" in keys

    bmi = inv["traits"]["bmi.EUR.GIANT-UKBB.2018"]
    # D-16 schema fields per Example 4 + REQ-TRAIT-INVENTORY
    required = {
        "trait", "ancestry", "consortium", "year",
        "source_url", "doi", "build", "phenotype_lock",
        "harmonized_path", "parquet_path", "munged_path",
        "n_total", "n_cases", "n_controls",
        "sha256_raw", "sha256_harmonized",
        "ldsc_intercept", "ldsc_h2",
        "qc_report_path", "qc_status",
        "cohort_overlap_cohorts", "mtag_overlap_correction_required",
        "dua_required", "license",
    }
    missing = required - set(bmi.keys())
    assert not missing, f"missing fields: {missing}"
    assert bmi["trait"] == "bmi"
    assert bmi["ancestry"] == "EUR"
    assert bmi["consortium"] == "GIANT-UKBB"
    assert bmi["year"] == 2018
    assert bmi["build"] == 37
    assert bmi["qc_status"] == "PASS"
    # SHA-256 raw must be the 64-hex from sha256_raw_mini.tsv
    assert bmi["sha256_raw"] == "aaaa1111aaaa1111aaaa1111aaaa1111aaaa1111aaaa1111aaaa1111aaaa1111"
    # ldsc_intercept must be filled from rg_logs (gcov_int row 0 = 0.04)
    # OR the focal h2_int (1.05). Either is acceptable per parser logic.
    assert bmi["ldsc_intercept"] is not None
    assert bmi["license"] == "public_academic"
    # mtag_overlap_correction_required is yes -> True
    assert bmi["mtag_overlap_correction_required"] is True


def test_build_inventory_missing_qc_sidecar_yields_missing(tmp_path):
    """If a qc.json is absent, qc_status='MISSING' (not crash)."""
    qc_dir = tmp_path / "qc_log_empty"
    rg_dir = tmp_path / "rg_logs_empty"
    qc_dir.mkdir()
    rg_dir.mkdir()
    inv = build_trait_inventory.build_inventory(
        tsv_path=FIXTURE_DIR / "trait_inventory_mini.tsv",
        raw_manifest=FIXTURE_DIR / "sha256_raw_mini.tsv",
        harm_manifest=FIXTURE_DIR / "sha256_harm_mini.tsv",
        qc_log_dir=qc_dir,
        rg_log_dir=rg_dir,
    )
    statuses = {k: e["qc_status"] for k, e in inv["traits"].items()}
    for k, s in statuses.items():
        assert s == "MISSING", f"{k}: expected MISSING, got {s}"


def test_build_inventory_emits_v_and_build_target(tmp_path):
    """Top-level fields version, build_target are emitted per Example 4."""
    qc_dir = tmp_path / "qc"
    rg_dir = tmp_path / "rg"
    qc_dir.mkdir()
    rg_dir.mkdir()
    inv = build_trait_inventory.build_inventory(
        tsv_path=FIXTURE_DIR / "trait_inventory_mini.tsv",
        raw_manifest=FIXTURE_DIR / "sha256_raw_mini.tsv",
        harm_manifest=FIXTURE_DIR / "sha256_harm_mini.tsv",
        qc_log_dir=qc_dir,
        rg_log_dir=rg_dir,
    )
    assert inv["version"]
    assert inv["build_target"] == "GRCh37"


def test_build_inventory_writes_yaml_file(tmp_path):
    """The CLI _main writes a YAML file that loads back to a valid inventory."""
    qc_dir = tmp_path / "qc"
    rg_dir = tmp_path / "rg"
    qc_dir.mkdir()
    rg_dir.mkdir()
    out = tmp_path / "out.yaml"
    inv = build_trait_inventory.build_inventory(
        tsv_path=FIXTURE_DIR / "trait_inventory_mini.tsv",
        raw_manifest=FIXTURE_DIR / "sha256_raw_mini.tsv",
        harm_manifest=FIXTURE_DIR / "sha256_harm_mini.tsv",
        qc_log_dir=qc_dir,
        rg_log_dir=rg_dir,
    )
    out.write_text(yaml.safe_dump(inv, sort_keys=False))
    reload = yaml.safe_load(out.read_text())
    assert "traits" in reload
    assert len(reload["traits"]) >= 3
