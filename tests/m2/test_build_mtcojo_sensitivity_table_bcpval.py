"""mtCOJO sensitivity-aggregator GCTA v1.94.1 schema-alignment tests
(quick task 260429-tq9, obligation M2-POST-M3-08).

Pin the column-lookup contract for build_mtcojo_sensitivity_table.build_sensitivity_table()
to GCTA v1.94.1 actual `.cojo` output schema:

    SNP A1 A2 freq b se p N bC bC_se bC_pval

The conditional p-value column is `bC_pval`. The pre-260429-tq9 aggregator
looked up `c.get("p_cojo", c.get("pC", None))`, which silently classifies
every row as FAIL because neither column is present in v1.94.1 output.

These three tests pin (1) the new bC_pval lookup, (2) back-compat for the
legacy p_cojo column, (3) the FAIL fall-through when neither column exists.

conftest.py inserts src/python on sys.path; module is imported by basename.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import build_mtcojo_sensitivity_table as bmst


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_eligible(path: Path, target: str, max_overlap: float = 0.15) -> None:
    """Write a one-row mtcojo_eligible_targets.tsv fixture."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        {
            "target_trait": [target],
            "max_overlapping_intercept": [max_overlap],
            "max_with_trait": ["dummy_covariate"],
            "n_mtag_novel_loci": [3],
        }
    )
    df.to_csv(path, sep="\t", index=False)


def _write_mtag_filtered(path: Path, target: str, snp_pvals: dict[str, float]) -> None:
    """Write a minimal MTAG-filtered fixture mirroring the production schema:

        SNP A1 A2 Z N FRQ mtag_beta mtag_se mtag_z mtag_pval max_FDR trait_key
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for snp, pval in snp_pvals.items():
        rows.append(
            {
                "SNP": snp,
                "A1": "A",
                "A2": "G",
                "Z": 5.5,
                "N": 100000.0,
                "FRQ": 0.3,
                "mtag_beta": 0.05,
                "mtag_se": 0.009,
                "mtag_z": 5.5,
                "mtag_pval": pval,
                "max_FDR": 0.0,
                "trait_key": target,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(path, sep="\t", index=False)


def _write_cojo_v1_94_1(path: Path, snp_bcpvals: dict[str, float]) -> None:
    """Write a GCTA v1.94.1 schema cojo file: SNP A1 A2 freq b se p N bC bC_se bC_pval."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for snp, bcp in snp_bcpvals.items():
        rows.append(
            {
                "SNP": snp,
                "A1": "A",
                "A2": "G",
                "freq": 0.3,
                "b": 0.01,
                "se": 0.005,
                "p": 1e-3,
                "N": 100000,
                "bC": 0.012,
                "bC_se": 0.005,
                "bC_pval": bcp,
            }
        )
    df = pd.DataFrame(rows)
    # Whitespace-delimited (production aggregator reads with sep=r"\s+")
    df.to_csv(path, sep="\t", index=False)


def _write_cojo_legacy_p_cojo(path: Path, snp_pcojos: dict[str, float]) -> None:
    """Write a legacy schema cojo file: SNP A1 A2 freq b se p N b_cojo se_cojo p_cojo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for snp, pc in snp_pcojos.items():
        rows.append(
            {
                "SNP": snp,
                "A1": "A",
                "A2": "G",
                "freq": 0.3,
                "b": 0.01,
                "se": 0.005,
                "p": 1e-3,
                "N": 100000,
                "b_cojo": 0.012,
                "se_cojo": 0.005,
                "p_cojo": pc,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(path, sep="\t", index=False)


def _write_cojo_neither_column(path: Path, snps: list[str]) -> None:
    """Write a malformed cojo file with neither bC_pval nor p_cojo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for snp in snps:
        rows.append(
            {
                "SNP": snp,
                "A1": "A",
                "A2": "G",
                "b": 0.01,
                "se": 0.005,
                "p": 1e-3,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(path, sep="\t", index=False)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_classifies_on_bcpval_when_present(tmp_path: Path):
    """Test 1 (RED) — GCTA v1.94.1 schema with bC_pval column.

    3 SNPs with bC_pval = {1e-10 (PASS), 1e-6 (WARN), 0.5 (FAIL)} must
    yield 3 sensitivity rows with the matching flags and mtcojo_p
    populated from bC_pval.
    """
    target = "fixture_target_trait"
    snp_pvals = {"rs10001": 1e-10, "rs10002": 1e-6, "rs10003": 0.5}

    eligible = tmp_path / "mtcojo_eligible_targets.tsv"
    _write_eligible(eligible, target)

    mtcojo_dir = tmp_path / "mtcojo"
    cojo_path = mtcojo_dir / f"{target}.mtcojo.cojo"
    _write_cojo_v1_94_1(cojo_path, snp_pvals)

    # MTAG-novel: every SNP under 5e-8 (so all 3 intersect cojo)
    mtag_filtered = tmp_path / "mtag_filtered.txt"
    _write_mtag_filtered(
        mtag_filtered,
        target,
        {snp: 1e-9 for snp in snp_pvals},
    )

    df = bmst.build_sensitivity_table(
        eligible_path=eligible,
        mtcojo_dir=mtcojo_dir,
        mtag_filtered_path=mtag_filtered,
        stratum="EUR",
    )

    assert len(df) == 3, f"expected 3 rows, got {len(df)}: {df}"
    flags_by_snp = dict(zip(df["locus_id"], df["sensitivity_flag"]))
    assert flags_by_snp["rs10001"] == "PASS", f"rs10001 (bC_pval=1e-10) must be PASS, got {flags_by_snp['rs10001']}"
    assert flags_by_snp["rs10002"] == "WARN", f"rs10002 (bC_pval=1e-6) must be WARN, got {flags_by_snp['rs10002']}"
    assert flags_by_snp["rs10003"] == "FAIL", f"rs10003 (bC_pval=0.5) must be FAIL, got {flags_by_snp['rs10003']}"

    p_by_snp = dict(zip(df["locus_id"], df["mtcojo_p"]))
    assert p_by_snp["rs10001"] == pytest.approx(1e-10), "mtcojo_p must populate from bC_pval for rs10001"
    assert p_by_snp["rs10002"] == pytest.approx(1e-6), "mtcojo_p must populate from bC_pval for rs10002"
    assert p_by_snp["rs10003"] == pytest.approx(0.5), "mtcojo_p must populate from bC_pval for rs10003"


def test_legacy_p_cojo_column_back_compat(tmp_path: Path):
    """Test 2 — legacy schema (p_cojo column) must still classify correctly.

    The schema-aligned aggregator falls back to p_cojo when bC_pval is absent
    (back-compat for any hypothetical re-test against an older GCTA build).
    """
    target = "fixture_legacy_target"
    eligible = tmp_path / "mtcojo_eligible_targets.tsv"
    _write_eligible(eligible, target)

    mtcojo_dir = tmp_path / "mtcojo"
    cojo_path = mtcojo_dir / f"{target}.mtcojo.cojo"
    _write_cojo_legacy_p_cojo(cojo_path, {"rs20001": 1e-10})

    mtag_filtered = tmp_path / "mtag_filtered.txt"
    _write_mtag_filtered(mtag_filtered, target, {"rs20001": 1e-9})

    df = bmst.build_sensitivity_table(
        eligible_path=eligible,
        mtcojo_dir=mtcojo_dir,
        mtag_filtered_path=mtag_filtered,
        stratum="EUR",
    )

    assert len(df) == 1, f"expected 1 row, got {len(df)}: {df}"
    assert df.iloc[0]["sensitivity_flag"] == "PASS", (
        f"legacy p_cojo=1e-10 must classify as PASS, got {df.iloc[0]['sensitivity_flag']}"
    )
    assert df.iloc[0]["mtcojo_p"] == pytest.approx(1e-10), (
        "mtcojo_p must populate from legacy p_cojo when bC_pval absent"
    )


def test_neither_column_returns_fail(tmp_path: Path):
    """Test 3 — malformed cojo (neither bC_pval nor p_cojo) returns FAIL,
    not KeyError. Verifies the _classify() None-branch is reached cleanly.
    """
    target = "fixture_malformed_target"
    eligible = tmp_path / "mtcojo_eligible_targets.tsv"
    _write_eligible(eligible, target)

    mtcojo_dir = tmp_path / "mtcojo"
    cojo_path = mtcojo_dir / f"{target}.mtcojo.cojo"
    _write_cojo_neither_column(cojo_path, ["rs30001"])

    mtag_filtered = tmp_path / "mtag_filtered.txt"
    _write_mtag_filtered(mtag_filtered, target, {"rs30001": 1e-9})

    df = bmst.build_sensitivity_table(
        eligible_path=eligible,
        mtcojo_dir=mtcojo_dir,
        mtag_filtered_path=mtag_filtered,
        stratum="EUR",
    )

    assert len(df) == 1, f"expected 1 row even for malformed cojo, got {len(df)}: {df}"
    assert df.iloc[0]["sensitivity_flag"] == "FAIL", (
        f"malformed cojo (no p column) must classify as FAIL, got {df.iloc[0]['sensitivity_flag']}"
    )
    assert df.iloc[0]["mtcojo_p"] is None or pd.isna(df.iloc[0]["mtcojo_p"]), (
        "mtcojo_p must be None/NaN when neither bC_pval nor p_cojo present"
    )
