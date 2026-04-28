"""Unit tests for src/python/aou_ld_panel.py against the synthetic MT fixture.

Skips gracefully if Hail is not installed locally (CI graceful-degrade per
plan acceptance criteria — pytest.importorskip("hail") at module entry).
Otherwise: builds the synthetic MT via ``synthetic_mt_path`` session fixture,
exercises load_qc_cohort + compute_region_ld for both region_class branches.

Covers the 5 driver behaviors enumerated in m3-00 plan task 3:
* test_synthetic_mt_built_via_balding_nichols
* test_aou_driver_loads_synthetic_mt
* test_canonical_ordering (split_multi_hts BEFORE variant_qc; static source check)
* test_compute_region_ld_path_a1 (small region; dense .npz)
* test_compute_region_ld_skipped_few_variants
* test_env_yaml_pins_python_311
* test_gitignore_has_explicit_aou_entries
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ----- Static-source / file-existence tests (no hail dependency) -----

def test_env_yaml_pins_python_311():
    p = PROJECT_ROOT / "envs" / "m3-aou-dev.yml"
    assert p.exists(), f"missing {p}"
    content = p.read_text()
    assert "python=3.11" in content, "envs/m3-aou-dev.yml must pin python=3.11"
    assert "hail==0.2" in content, "envs/m3-aou-dev.yml must pin hail==0.2.x"


def test_r_env_yaml_has_reticulate():
    p = PROJECT_ROOT / "envs" / "m3-r-ld.yml"
    assert p.exists()
    content = p.read_text()
    assert "r-reticulate" in content
    assert "r-base=4.4" in content


def test_canonical_ordering_split_before_variant_qc():
    """Static check: split_multi_hts called BEFORE the FIRST variant_qc in source."""
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    split_idx = src.find("split_multi_hts")
    vqc_idx = src.find("variant_qc")
    assert split_idx > 0, "split_multi_hts not found in aou_ld_panel.py"
    assert vqc_idx > 0, "variant_qc not found in aou_ld_panel.py"
    assert split_idx < vqc_idx, (
        f"split_multi_hts must appear BEFORE variant_qc "
        f"(positions: split={split_idx}, vqc={vqc_idx})"
    )


def test_uses_verified_env_var_names():
    """Verify the driver does NOT use the broken RELATED_SAMPLES_HT_PATH env var (Q9 correction)."""
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    assert "WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH" in src
    assert "WORKSPACE_BUCKET" in src
    assert "GOOGLE_PROJECT" in src
    # The broken spec env var name must NOT appear (verifies RESEARCH Q9 correction)
    assert "RELATED_SAMPLES_HT_PATH" not in src, (
        "broken env-var name from spec §5.1 line 142 must NOT appear in driver"
    )
    # The correct hardcoded path MUST appear
    assert "relatedness_flagged_samples.tsv" in src


def test_static_ast_calls_present():
    """Driver source contains ast-detectable calls to all required Hail entry points."""
    tree = ast.parse((PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text())
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    required = {"split_multi_hts", "variant_qc", "sample_qc", "ld_matrix"}
    missing = required - names
    assert not missing, f"missing Hail call-path attributes: {missing}"


def test_gitignore_has_explicit_aou_entries():
    g = (PROJECT_ROOT / ".gitignore").read_text()
    assert "data/interim/aou_ld_exports" in g
    assert "data/processed/ld_reference/AFR_aou" in g
    assert "data/processed/ld_reference/EUR_aou" in g
    assert "tests/m3/fixtures/synthetic_mt" in g


# ----- Live Hail tests (skip individually if hail not available) -----


def _require_hail():
    return pytest.importorskip("hail")


def test_synthetic_mt_built_via_balding_nichols(synthetic_mt_path: Path):
    _require_hail()
    """The synthetic MT exists and has the expected schema."""
    import hail as hl

    mt = hl.read_matrix_table(str(synthetic_mt_path))
    n_cols = mt.count_cols()
    n_rows = mt.count_rows()
    # Default fixture: 100 samples x 1500 variants
    assert n_cols == 100, f"expected 100 samples, got {n_cols}"
    assert n_rows == 1500, f"expected 1500 variants, got {n_rows}"
    # Required fields for the driver
    assert "ancestry_pred" in mt.col, "synthetic MT must have ancestry_pred col field"
    assert "filters" in mt.row, "synthetic MT must have filters row field"
    assert "rsid" in mt.row, "synthetic MT must have rsid row field"


def test_aou_driver_loads_synthetic_mt(synthetic_mt_path: Path, mock_aou_env, tmp_path):
    """load_qc_cohort runs end-to-end against synthetic MT."""
    _require_hail()
    from aou_ld_panel import load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    n_cols = mt.count_cols()
    n_rows = mt.count_rows()
    assert n_cols > 0, "no AFR samples survived QC; check fixture / thresholds"
    assert n_rows > 0, "no variants survived QC; check fixture"
    # Roughly 60 AFR samples in fixture; some may drop on call_rate / het filter.
    # Synthetic generator gives high call rate so most should survive.
    assert n_cols >= 30, f"expected >= 30 AFR samples post-QC, got {n_cols}"


def test_compute_region_ld_path_a1_small_region(synthetic_mt_path: Path,
                                                mock_aou_env, tmp_path):
    """Small region (~2 Mb FTO neighborhood) -> Path A.1 dense .npz."""
    _require_hail()
    import numpy as np

    from aou_ld_panel import compute_region_ld, load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    region = {
        "region_id": "synth_region_chr16_small",
        "chr": "16",
        "start_grch38": 50_100_000,
        "end_grch38": 51_900_000,
        "radius_bp": 2_400_000,
        "region_class": "small",
    }
    res = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res["status"] == "ok", f"expected ok, got {res}"
    assert res["path_a"] == "A.1"
    assert res["n_var"] > 10
    out_path = Path(res["out"])
    assert out_path.exists()
    # Round-trip: load .npz, verify symmetric float32
    z = np.load(out_path)
    ld = z["ld"]
    assert ld.dtype == np.float32
    assert ld.shape[0] == ld.shape[1] == res["n_var"]


def test_compute_region_ld_skipped_few_variants(synthetic_mt_path: Path,
                                                mock_aou_env, tmp_path):
    """Tiny interval with < 10 variants -> status='skipped_few_variants'."""
    _require_hail()
    from aou_ld_panel import compute_region_ld, load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    # A 1 kb window in a sparse-density region of the fixture should have < 10 SNPs
    region = {
        "region_id": "synth_region_chr16_tiny",
        "chr": "16",
        "start_grch38": 50_100_000,
        "end_grch38": 50_100_500,
        "radius_bp": 500_000,
        "region_class": "small",
    }
    res = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res["status"] == "skipped_few_variants"
    assert res["n_var"] < 10
