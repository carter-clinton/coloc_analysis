"""Shared pytest fixtures for tests/m3 (Wave 0 + later wave reuse).

Fixtures:
    union_bed_fixture       — 5-row mini union BED (EUR + TRANS + AFR provenance)
    chain_fixture           — abs path to GRCh37 -> GRCh38 chain
    mock_aou_env            — monkeypatched WORKSPACE_BUCKET/GOOGLE_PROJECT/WGS_*
    synthetic_mt_path       — lazy-built synthetic_aou.mt path (Hail Balding-Nichols)

Per RESEARCH Q6: synthetic MT exercises every Hail call path
(read_matrix_table -> filter_cols -> anti_join_cols -> split_multi_hts ->
sample_qc -> variant_qc -> filter_intervals -> ld_matrix).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Project root (tests/m3/conftest.py -> tests/m3 -> tests -> ROOT)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Make src/python importable for `from ld_panel import ...` and friends
# (matches existing tests/m1/conftest.py pattern).
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# The shared contention-safe R-subprocess timeout constant
# (R_SUBPROCESS_TIMEOUT_S) lives in the ROOT tests/conftest.py — that is the
# module pytest imports as the bare ``conftest`` (this m3 conftest is shadowed by
# it under the default prepend import mode), so the m3 R-execution modules import
# it via ``from conftest import R_SUBPROCESS_TIMEOUT_S``.


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def chain_fixture() -> Path:
    """Absolute path to UCSC GRCh37 -> GRCh38 chain (data/external/liftover/...)."""
    p = PROJECT_ROOT / "data" / "external" / "liftover" / "hg19ToHg38.over.chain.gz"
    if not p.exists():
        pytest.skip(f"chain file not present: {p}")
    return p


@pytest.fixture()
def union_bed_fixture(tmp_path: Path) -> Path:
    """Mini 5-row union BED for testing the reformatter without the full 161-row M2 input.

    Mix of single-trait EUR (clump only), AFR (mtag), and TRANS provenance to
    exercise per-ancestry source_trait derivation. Coordinates chosen so all
    five regions liftover cleanly (avoid pericentromeric / ALT regions).

    Provenance JSON quoting matches the M2 BED convention (literal embedded
    quotes are doubled) so the parser exercise mirrors production input.
    """
    # The M2 BED double-quotes embedded quotes. We construct identical strings.
    rows = [
        # FTO 16q12 — narrow region (~2 Mb). MTAG includes BMI AFR PAGE 2019.
        ("chr16", 53500000, 55500000, "test_region_001",
         '{"clump":["bmi.EUR"],"mtag":["bmi.AFR.PAGE.2019.AFR","bmi.EUR.GIANT-UKBB.2018.EUR"],"cpassoc":["joint.AFR"]}'),
        # SORT1 1p13 — narrow region (~2 Mb). EUR + AFR lipids.
        ("chr1", 109000000, 111000000, "test_region_002",
         '{"clump":["ldl.EUR","ldl.TRANS"],"mtag":["ldl.AFR.GLGC.2021.AFR","ldl.EUR.GLGC.2021.EUR"],"cpassoc":["joint.TRANS"]}'),
        # APOL1 22q12 — narrow (~1.5 Mb).
        ("chr22", 36000000, 37500000, "test_region_003",
         '{"clump":["egfr.AFR"],"mtag":["egfr.AFR.CKDGen.2019.AFR"],"cpassoc":["joint.AFR"]}'),
        # SH2B3 12q24 — narrow (~1 Mb). EUR-primary; no AFR mtag.
        ("chr12", 111000000, 112000000, "test_region_004",
         '{"clump":["bmi.EUR"],"mtag":["bmi.EUR.GIANT-UKBB.2018.EUR"],"cpassoc":["joint.EUR"]}'),
        # Wide chr6 region (~10 Mb) -> tests medium region_class
        ("chr6", 30000000, 40000000, "test_region_005",
         '{"clump":["sbp.EUR"],"mtag":["sbp.EUR.Evangelou-ICBP-UKBB.2018.EUR"],"cpassoc":["joint.AFR"]}'),
    ]
    # Match the M2 BED's quoting convention (column 7 is wrapped in literal
    # double quotes, with embedded quotes doubled).
    bed_path = tmp_path / "mini_union.bed"
    with bed_path.open("w") as fh:
        for chrom, start, end, region_id, prov_json in rows:
            quoted_prov = '"' + prov_json.replace('"', '""') + '"'
            fh.write(f"{chrom}\t{start}\t{end}\t{region_id}\t.\t.\t{quoted_prov}\n")
    return bed_path


@pytest.fixture()
def mock_aou_env(monkeypatch, tmp_path: Path) -> dict:
    """Monkeypatch AoU env vars to safe local-only values.

    Production access is impossible from a local pytest run (T-M3-EGR-W0
    threat mitigation): WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH is set to a local
    path under tmp_path that only the synthetic MT fixture should populate.
    """
    bucket = "fc-secure-pytest-stub"
    monkeypatch.setenv("WORKSPACE_BUCKET", bucket)
    monkeypatch.setenv("GOOGLE_PROJECT", "test-proj-pytest")
    stub_mt = tmp_path / "synthetic_aou.mt"
    monkeypatch.setenv("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH", str(stub_mt))
    return {
        "WORKSPACE_BUCKET": bucket,
        "GOOGLE_PROJECT": "test-proj-pytest",
        "WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH": str(stub_mt),
    }


@pytest.fixture(scope="session")
def synthetic_mt_path(tmp_path_factory) -> Path:
    """Lazy-build the synthetic AoU MT via tests/m3/fixtures/build_synthetic_mt.py.

    If hail is not installed, pytest.skip() — driver tests will be skipped at
    the test layer too via pytest.importorskip("hail").
    """
    hail = pytest.importorskip("hail")  # noqa: F841 - surface skip reason cleanly
    fixtures_dir = PROJECT_ROOT / "tests" / "m3" / "fixtures"
    target = fixtures_dir / "synthetic_mt" / "synthetic_aou.mt"
    if target.exists():
        return target
    builder = fixtures_dir / "build_synthetic_mt.py"
    if not builder.exists():
        pytest.skip(f"synthetic MT builder not present: {builder}")
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(builder), "--out", str(target)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        pytest.skip(f"synthetic MT build failed (code {res.returncode}): {res.stderr[-2000:]}")
    return target


@pytest.fixture(scope="session")
def synthetic_mt_path_missing(tmp_path_factory) -> Path:
    """Synthetic AoU MT WITH per-genotype missingness injected (call_rate<1.0).

    The default ``synthetic_mt_path`` fixture is built from Balding-Nichols
    fully-called genotypes (call_rate==1.0), which makes the >=0.98 call_rate
    sample filter a guaranteed no-op — the coverage gap that let the Gate B
    nano sample-axis collapse through
    (.planning/debug/m3-gateb-nano-sample-axis-collapse.md).

    This fixture injects ~5% per-genotype missingness so per-sample call_rate
    on a small (below-floor) window falls below 0.98. Pre-fix that would drop
    every sample (118903x0 collapse); post-fix the nano-degeneracy guard skips
    the filter and retains samples. Built into a session-scoped tmp dir so it
    never collides with the committed default fixture.
    """
    hail = pytest.importorskip("hail")  # noqa: F841 - surface skip reason cleanly
    fixtures_dir = PROJECT_ROOT / "tests" / "m3" / "fixtures"
    builder = fixtures_dir / "build_synthetic_mt.py"
    if not builder.exists():
        pytest.skip(f"synthetic MT builder not present: {builder}")
    target = tmp_path_factory.mktemp("synthetic_mt_missing") / "synthetic_aou_missing.mt"
    cmd = [sys.executable, str(builder), "--out", str(target),
           "--missingness", "0.05", "--force"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        pytest.skip(f"synthetic missing-MT build failed (code {res.returncode}): {res.stderr[-2000:]}")
    return target
