"""run_cpassoc.py integration tests — per-stratum CPASSOC orchestrator.

D-M2-04 — Python reimplementation with LDSC intercept matrix as R.
D-M2-Q6 — _MIN_PER_STRATUM=3 floor enforcement.
Q7 — PSD-preserving principal-submatrix slice with eigvalsh probe.

Plan reference: m2-03-cpassoc-3-strata-PLAN.md Task 1.

Synthetic 5-trait fixture: hand-built R + munged.gz files; assert SHom/SHet
chi-square p-values land in [0, 1]; p-values reduce to chi-square survival
function on the synthetic z-matrix; output schema matches the per-stratum
TSV contract (chr, pos, rsid, A1, A2, n_traits, SHom_stat, SHom_p,
SHet_stat, SHet_p, contributing_traits).
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

try:
    from run_cpassoc import (
        run_cpassoc,
        _slice_R_for_trait_order,
        _intersect_and_align,
        _load_munged,
    )
    _RUN_CPASSOC_AVAILABLE = True
except ImportError:
    _RUN_CPASSOC_AVAILABLE = False
    run_cpassoc = None  # type: ignore[assignment]
    _slice_R_for_trait_order = None  # type: ignore[assignment]
    _intersect_and_align = None  # type: ignore[assignment]
    _load_munged = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _RUN_CPASSOC_AVAILABLE,
    reason="src/python/run_cpassoc.py not yet landed (Wave 3 Task 1)",
)


# ---------------------------------------------------------------------------
# Helpers — build a synthetic multi-trait test environment.
# ---------------------------------------------------------------------------

def _write_munged(path: Path, snps: list[tuple[str, str, str, float, float]]) -> None:
    """Write LDSC-munged HM3 .sumstats.gz with [SNP, A1, A2, Z, N] columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        f.write("SNP\tA1\tA2\tZ\tN\n")
        for snp, a1, a2, z, n in snps:
            f.write(f"{snp}\t{a1}\t{a2}\t{z}\t{n}\n")


def _build_synthetic_env(tmp_path: Path, K: int = 5, n_snps: int = 50) -> tuple[Path, Path, Path, list[str]]:
    """Build a synthetic K-trait CPASSOC test environment.

    Returns
    -------
    (matrix_path, sidecar_path, munged_dir, trait_order)
    """
    rng = np.random.default_rng(42)
    trait_order = [f"trait_{i:02d}" for i in range(K)]

    # PSD R matrix with off-diagonal structure
    A = rng.uniform(0.0, 0.3, size=(K, K))
    R = (A + A.T) / 2.0
    np.fill_diagonal(R, 1.0)

    # Wide-TSV matrix with index col
    M = pd.DataFrame(R, index=trait_order, columns=trait_order)
    matrix_path = tmp_path / "matrix.tsv"
    M.to_csv(matrix_path, sep="\t")

    # Sidecar mimicking the Wave 2 residcov.trait_order.json
    sidecar_path = tmp_path / "residcov.trait_order.json"
    sidecar_path.write_text(json.dumps({"trait_order": trait_order, "K": K}, indent=2))

    # Per-trait munged .sumstats.gz files
    munged_dir = tmp_path / "munged"
    snp_ids = [f"rs{1000 + i}" for i in range(n_snps)]
    a1_vec = ["A"] * n_snps
    a2_vec = ["G"] * n_snps

    for trait in trait_order:
        z_vec = rng.standard_normal(n_snps)
        n_vec = rng.uniform(50000, 500000, size=n_snps)
        rows = list(zip(snp_ids, a1_vec, a2_vec, z_vec, n_vec))
        _write_munged(munged_dir / f"{trait}.sumstats.gz", rows)

    return matrix_path, sidecar_path, munged_dir, trait_order


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------

def test_load_munged_schema(tmp_path):
    """_load_munged returns DataFrame with [SNP, A1, A2, Z, N] columns."""
    f = tmp_path / "x.sumstats.gz"
    _write_munged(f, [("rs1", "A", "G", 1.5, 1000.0), ("rs2", "T", "C", -0.3, 1500.0)])
    df = _load_munged(f)
    assert set(df.columns) == {"SNP", "A1", "A2", "Z", "N"}
    assert len(df) == 2
    assert list(df["SNP"]) == ["rs1", "rs2"]


def test_slice_R_PSD_probe(tmp_path):
    """_slice_R_for_trait_order asserts PSD via eigvalsh."""
    K = 4
    trait_order = [f"t{i}" for i in range(K)]
    R = np.eye(K) + 0.1 * np.ones((K, K))  # PSD
    M = pd.DataFrame(R, index=trait_order, columns=trait_order)
    matrix_path = tmp_path / "M.tsv"
    M.to_csv(matrix_path, sep="\t")

    R_sliced = _slice_R_for_trait_order(matrix_path, trait_order)
    assert R_sliced.shape == (K, K)
    assert np.allclose(R_sliced, R_sliced.T)  # symmetric
    eigvals = np.linalg.eigvalsh(R_sliced)
    assert eigvals.min() > -1e-10  # PSD


def test_slice_R_partial_subset(tmp_path):
    """_slice_R_for_trait_order produces principal submatrix when subset requested."""
    full_keys = ["a", "b", "c", "d"]
    R = np.array(
        [
            [1.0, 0.1, 0.2, 0.3],
            [0.1, 1.0, 0.1, 0.2],
            [0.2, 0.1, 1.0, 0.1],
            [0.3, 0.2, 0.1, 1.0],
        ]
    )
    M = pd.DataFrame(R, index=full_keys, columns=full_keys)
    matrix_path = tmp_path / "M.tsv"
    M.to_csv(matrix_path, sep="\t")

    subset = ["b", "d"]
    R_sub = _slice_R_for_trait_order(matrix_path, subset)
    assert R_sub.shape == (2, 2)
    assert R_sub[0, 0] == 1.0
    assert R_sub[1, 1] == 1.0
    assert R_sub[0, 1] == pytest.approx(0.2)


def test_intersect_and_align_basic(tmp_path):
    """_intersect_and_align inner-joins on SNP and aligns alleles."""
    df_a = pd.DataFrame(
        {
            "SNP": ["rs1", "rs2", "rs3"],
            "A1": ["A", "T", "G"],
            "A2": ["G", "C", "A"],
            "Z": [1.0, 2.0, 3.0],
            "N": [1000, 2000, 3000],
        }
    )
    df_b = pd.DataFrame(
        {
            "SNP": ["rs1", "rs2", "rs4"],
            "A1": ["A", "C", "T"],   # rs2 alleles swapped
            "A2": ["G", "T", "G"],
            "Z": [0.5, 0.7, 1.1],
            "N": [1100, 2100, 4000],
        }
    )
    merged = _intersect_and_align({"a": df_a, "b": df_b})
    # Intersection: rs1 (same alleles), rs2 (swapped — sign-flipped Z_b)
    assert set(merged.index) == {"rs1", "rs2"}
    assert merged.loc["rs1", "Z_b"] == pytest.approx(0.5)  # same alleles
    assert merged.loc["rs2", "Z_b"] == pytest.approx(-0.7)  # swap → flip


def test_run_cpassoc_synthetic_5_trait(tmp_path):
    """End-to-end: synthetic 5-trait fixture produces valid output schema."""
    matrix_path, sidecar_path, munged_dir, trait_order = _build_synthetic_env(
        tmp_path, K=5, n_snps=50
    )
    out_path = tmp_path / "cpassoc_results.tsv"

    n = run_cpassoc(
        stratum="EUR",
        matrix_path=matrix_path,
        mtag_sidecar_path=sidecar_path,
        munged_dir=munged_dir,
        out_path=out_path,
    )

    assert n == 50
    assert out_path.exists()
    df = pd.read_csv(out_path, sep="\t")
    required = {
        "chr", "pos", "rsid", "A1", "A2", "n_traits",
        "SHom_stat", "SHom_p", "SHet_stat", "SHet_p", "contributing_traits",
    }
    assert required.issubset(df.columns)
    assert len(df) == 50
    # Schema invariants
    assert (df["n_traits"] == 5).all()
    assert (df["SHom_stat"] >= 0).all()
    assert (df["SHet_stat"] >= 0).all()
    assert df["SHom_p"].between(0, 1).all()
    assert df["SHet_p"].between(0, 1).all()
    # contributing_traits is the trait_order joined by ;
    assert (df["contributing_traits"] == ";".join(trait_order)).all()


def test_run_cpassoc_below_floor_raises(tmp_path):
    """K < _MIN_PER_STRATUM=3 raises ValueError per D-M2-Q6."""
    K = 2
    trait_order = [f"trait_{i}" for i in range(K)]
    R = np.eye(K)
    M = pd.DataFrame(R, index=trait_order, columns=trait_order)
    matrix_path = tmp_path / "M.tsv"
    M.to_csv(matrix_path, sep="\t")

    sidecar_path = tmp_path / "sidecar.json"
    sidecar_path.write_text(json.dumps({"trait_order": trait_order, "K": K}))

    munged_dir = tmp_path / "m"
    munged_dir.mkdir()
    for t in trait_order:
        _write_munged(munged_dir / f"{t}.sumstats.gz", [("rs1", "A", "G", 1.0, 1000.0)])

    with pytest.raises(ValueError, match="_MIN_PER_STRATUM"):
        run_cpassoc(
            stratum="AFR",
            matrix_path=matrix_path,
            mtag_sidecar_path=sidecar_path,
            munged_dir=munged_dir,
            out_path=tmp_path / "out.tsv",
        )


def test_run_cpassoc_pvalue_uses_chi2_sf(tmp_path):
    """p-values agree with scipy.stats.chi2.sf at the right df."""
    from scipy.stats import chi2

    matrix_path, sidecar_path, munged_dir, trait_order = _build_synthetic_env(
        tmp_path, K=4, n_snps=20
    )
    out_path = tmp_path / "out.tsv"
    K = len(trait_order)
    run_cpassoc(
        stratum="EUR",
        matrix_path=matrix_path,
        mtag_sidecar_path=sidecar_path,
        munged_dir=munged_dir,
        out_path=out_path,
    )
    df = pd.read_csv(out_path, sep="\t")
    # SHom_p == chi2.sf(SHom_stat, df=K)
    np.testing.assert_allclose(
        df["SHom_p"].values, chi2.sf(df["SHom_stat"].values, df=K), atol=1e-12
    )
    # SHet_p == chi2.sf(SHet_stat, df=K-1)
    np.testing.assert_allclose(
        df["SHet_p"].values, chi2.sf(df["SHet_stat"].values, df=K - 1), atol=1e-12
    )
