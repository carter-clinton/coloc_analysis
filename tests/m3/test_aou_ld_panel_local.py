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


# ----- Checkpoint-URI tests (m3-W1-checkpoint-suffix regression guards) -----

def test_qc_checkpoint_uri_primary_afr():
    """sensitivity=False AFR -> mt_afr_qc.mt (current behavior preserved)."""
    from aou_ld_panel import _qc_checkpoint_uri
    assert _qc_checkpoint_uri("test-bucket", "afr", False) == \
        "gs://test-bucket/ld/mt_afr_qc.mt"


def test_qc_checkpoint_uri_sensitivity_afr():
    """sensitivity=True AFR -> mt_afr_pca_selfid_qc.mt (D-M3-07 distinct path).

    Three downstream notebooks (AOU-1 cohort_summary table at Cell 7,
    AOU-2_per_region_ld.ipynb, AOU-4_validation.ipynb) already consume
    this exact path; the producer load_qc_cohort was the drift point
    surfaced 2026-05-12.
    """
    from aou_ld_panel import _qc_checkpoint_uri
    assert _qc_checkpoint_uri("test-bucket", "afr", True) == \
        "gs://test-bucket/ld/mt_afr_pca_selfid_qc.mt"


def test_qc_checkpoint_uri_eur_primary():
    """EUR is always sensitivity=False -> mt_eur_qc.mt (D-M3-01 parity)."""
    from aou_ld_panel import _qc_checkpoint_uri
    assert _qc_checkpoint_uri("test-bucket", "eur", False) == \
        "gs://test-bucket/ld/mt_eur_qc.mt"


def test_qc_checkpoint_uri_distinct_paths_regression():
    """REGRESSION GUARD (m3-W1-checkpoint-suffix, 2026-05-12): AFR primary
    and sensitivity cohorts MUST write to distinct checkpoint URIs.
    Prevents the silent overwrite where Cell 4 (sensitivity=True) would
    trash Cell 3's (sensitivity=False) checkpoint at the shared mt_afr_qc.mt
    path. Three downstream notebooks consume both paths independently."""
    from aou_ld_panel import _qc_checkpoint_uri
    primary = _qc_checkpoint_uri("test-bucket", "afr", False)
    sensitivity = _qc_checkpoint_uri("test-bucket", "afr", True)
    assert primary != sensitivity, (
        f"AFR primary and sensitivity cohorts must write to distinct "
        f"checkpoints; both got {primary}"
    )


# ----- _normalize_bucket + prefixed-bucket contract tests
# ----- (m3-W1-bucket-prefix-defensive, 2026-05-14 regression guards) -----


def test_normalize_bucket_strips_prefix():
    """Bare requirement: _normalize_bucket strips the gs:// protocol prefix."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("gs://fc-secure-XXX") == "fc-secure-XXX"


def test_normalize_bucket_keeps_bare():
    """Back-compat: bare bucket names pass through unchanged."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("fc-secure-XXX") == "fc-secure-XXX"


def test_normalize_bucket_strips_trailing_slash():
    """Defensive: trailing slash on bucket path normalized away (otherwise
    f-string construction yields "gs://bucket//ld/..." double-slash)."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("fc-secure-XXX/") == "fc-secure-XXX"
    assert _normalize_bucket("gs://fc-secure-XXX/") == "fc-secure-XXX"


def test_normalize_bucket_idempotent():
    """Property: applying _normalize_bucket twice yields same as once.
    Guards against accidental future regressions where re-normalization could
    over-strip (e.g. removing characters from a bare name that happens to
    start with 'gs:')."""
    from aou_ld_panel import _normalize_bucket
    for raw in [
        "fc-secure-XXX",
        "gs://fc-secure-XXX",
        "gs://fc-secure-XXX/",
        "test-bucket",
    ]:
        once = _normalize_bucket(raw)
        twice = _normalize_bucket(once)
        assert once == twice, f"non-idempotent: f({raw!r})={once!r}, f(f({raw!r}))={twice!r}"


def test_normalize_bucket_handles_malformed_extra_slash():
    """Defensive: malformed gs:///bucket (3 slashes) still normalizes cleanly.
    Belt-and-suspenders against AoU env-var edge cases."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("gs:///fc-secure-XXX") == "fc-secure-XXX"


def test_qc_checkpoint_uri_accepts_prefixed_bucket():
    """REGRESSION GUARD (m3-W1-bucket-prefix-defensive, 2026-05-14):
    _qc_checkpoint_uri must accept both bare ('fc-secure-XXX') and
    already-prefixed ('gs://fc-secure-XXX') bucket inputs and produce the
    SAME canonical single-gs:// URI either way.

    Bug surfaced 2026-05-14 during AOU-1 Wave 1 fire on AoU Workbench: the
    notebook caller passed os.environ['WORKSPACE_BUCKET'] (which AoU ships as
    'gs://fc-secure-...') into the prior bare-only contract, yielding
    'gs://gs://fc-secure-.../ld/mt_afr_qc.mt' -- a malformed double-protocol
    URI that would have failed at GCS-write boundary during Cell 3's
    load_qc_cohort. Defensive normalization in the helper closes the
    integration gap between the helper's bare-only test contract and the
    notebook's prefixed env-var convention.
    """
    from aou_ld_panel import _qc_checkpoint_uri
    bare = _qc_checkpoint_uri("test-bucket", "afr", False)
    prefixed = _qc_checkpoint_uri("gs://test-bucket", "afr", False)
    assert bare == prefixed == "gs://test-bucket/ld/mt_afr_qc.mt", (
        f"bare vs prefixed inputs must produce identical canonical URI; "
        f"got bare={bare!r}, prefixed={prefixed!r}"
    )


def test_intermediate_checkpoint_uri_post_split_afr_primary():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split.mt"


def test_intermediate_checkpoint_uri_post_sample_qc_afr_sensitivity():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_sample_qc", True)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_pca_selfid_post_sample_qc.mt"


def test_intermediate_checkpoint_uri_eur_no_sensitivity():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "eur", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_eur_post_split.mt"


def test_intermediate_checkpoint_uri_with_interval_filter_chr22():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_split", False, "chr22")
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split_chr22.mt"


def test_intermediate_checkpoint_uri_accepts_prefixed_bucket():
    """Defensive: bucket may arrive as 'gs://...' (per _normalize_bucket contract)."""
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("gs://fc-secure-XXX", "afr", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split.mt"


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
