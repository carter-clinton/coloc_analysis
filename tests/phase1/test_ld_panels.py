"""Wave 2 LD panel validation -- UKBB-LD (01-02) and HGDP+1kG (01-03).

RED-until-GREEN scaffold (Plan 01-02 Task 1-02-03): tests skip cleanly
until the corresponding downloader rules produce real outputs. Once
Task 1-02-02 (UKBB-LD) and Task 1-03-02 (HGDP+1kG) run, the `.rds` files
appear under LD_REF_DIR and these tests assert real structure.

Plan 01-03 Task 1-03-03 adds test_hgdp_afr_sample_count, which validates
the AFR sample count recorded in the sidecar .meta.json. Bounds are
950-1010 based on wave2b_preflight.log step 8 (1003 samples in
metadata, 986 reconciled against chr22 BCF header) -- the plan pre-spec's
~730 was an older 1kG-only figure.

Environment variables:
    LD_REF_DIR  -- root of the LD reference cache (default: data/ld_reference)

Sub-directories expected:
    {LD_REF_DIR}/EUR_ukbb_ld/   -- Plan 01-02 outputs
    {LD_REF_DIR}/AFR_hgdp_1kg/  -- Plan 01-03 outputs
"""
import json
import os
from pathlib import Path

import pytest

try:
    import pyreadr  # noqa: F401
    HAVE_PYREADR = True
except ImportError:
    HAVE_PYREADR = False

LD_REF_DIR = Path(os.environ.get("LD_REF_DIR", "data/processed/ld_reference"))
EUR_DIR = LD_REF_DIR / "EUR_ukbb_ld"
AFR_DIR = LD_REF_DIR / "AFR_hgdp_1kg"

pytestmark = pytest.mark.skipif(
    not HAVE_PYREADR,
    reason="pyreadr not installed (only materialized in ld_build env)",
)


def _load_rds(path: Path):
    """Load a .rds produced by pyreadr.write_rds. Returns the first value."""
    result = pyreadr.read_r(str(path))
    if None in result:
        return result[None]
    return next(iter(result.values()))


def _load_meta(rds_path: Path) -> dict:
    """Load the sidecar .meta.json written alongside the .rds."""
    meta_path = rds_path.with_suffix(".meta.json")
    if not meta_path.exists():
        pytest.skip(f"sidecar {meta_path} not yet produced")
    return json.loads(meta_path.read_text())


def test_ukbb_ld_output():
    """At least one non-HLA UKBB-LD region .rds exists and is well-formed."""
    if not EUR_DIR.exists():
        pytest.skip(f"{EUR_DIR} not yet populated (run Task 1-02-02)")
    rds_files = list(EUR_DIR.glob("*.rds"))
    if not rds_files:
        pytest.skip(f"No .rds files in {EUR_DIR} yet")
    # Prefer a non-HLA region to test the single-tile path
    candidate = next((f for f in rds_files if "HLA" not in f.name), rds_files[0])
    obj = _load_rds(candidate)
    assert obj is not None, f"{candidate} loaded to None"

    meta = _load_meta(candidate)
    assert "ld_source" in meta, f"meta missing ld_source: {meta}"
    assert meta["ld_source"].startswith("ukbb_ld_tiled"), (
        f"unexpected ld_source: {meta['ld_source']}"
    )
    assert meta.get("n_variants", 0) >= 50, (
        f"expected >=50 variants in non-HLA region, got {meta.get('n_variants')}"
    )


def test_hgdp_afr_output():
    """At least one AFR HGDP+1kG region .rds exists (Plan 01-03 sibling)."""
    if not AFR_DIR.exists():
        pytest.skip(f"{AFR_DIR} not yet populated (run Task 1-03-02)")
    rds_files = list(AFR_DIR.glob("*.rds"))
    assert len(rds_files) >= 1, f"No .rds files in {AFR_DIR}"


def test_hgdp_afr_sample_count():
    """AFR sample count recorded in sidecar .meta.json is in the expected range.

    Plan 01-03 Task 1-03-03. Bounds are 950-1010 based on
    wave2b_preflight.log step 8 (1003 in metadata, 986 reconciled
    against chr22 BCF header). Anything outside this range indicates
    either an upstream metadata re-release or a sample-id prefix
    reconciliation regression (Pitfall 3).
    """
    if not AFR_DIR.exists():
        pytest.skip(f"{AFR_DIR} not yet populated (run Task 1-03-02)")
    meta_files = list(AFR_DIR.glob("*.meta.json"))
    if not meta_files:
        pytest.skip(
            "AFR meta.json files not yet produced "
            "(Task 1-03-02 rule plumbing-only until DEF-01-04 liftover resolves)"
        )
    for mf in meta_files:
        m = json.loads(mf.read_text())
        n = m.get("n_samples_afr")
        assert n is not None, f"{mf} missing n_samples_afr"
        assert 950 <= n <= 1010, (
            f"AFR sample count {n} in {mf.name} outside expected 950-1010 range "
            f"(preflight: 1003 metadata / 986 BCF-reconciled); "
            f"either upstream panel re-released or Pitfall 3 prefix regression"
        )
        # Also check the ld_source flag survives (T-1-04 mitigation)
        assert m.get("ld_source") == "hgdp_1kg_v3_1_2", (
            f"{mf.name} missing or wrong ld_source: {m.get('ld_source')}"
        )
