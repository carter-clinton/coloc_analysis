"""Tests for src/python/build_replication_manifest.py (Plan 09-03 Task 1).

TDD RED -> GREEN:
  - test_tier_c_excluded       : D-02b (Tier C signals must NOT appear in manifest)
  - test_bbj_only_for_tier_ab  : D-05c (BBJ never for credible_set_SNP rows)
  - test_afr_never_finngen     : D-05 panel asymmetry (AFR dispatch must not hit FinnGen)
  - test_eur_never_mvp_afr     : D-05 panel asymmetry (EUR dispatch must not hit MVP-AFR)
  - test_missing_file_marked   : Missing replication sumstats file -> keep row with flag

These use the session-scoped `replication_cohorts_config` fixture from conftest.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PY = PROJECT_ROOT / "src" / "python"
if str(SRC_PY) not in sys.path:
    sys.path.insert(0, str(SRC_PY))

from build_replication_manifest import build_manifest  # noqa: E402


def _write_config(tmp_path: Path, cfg: dict) -> Path:
    p = tmp_path / "cfg.yaml"
    with open(p, "w") as f:
        yaml.safe_dump(cfg, f)
    return p


def test_tier_c_excluded(tmp_path: Path, replication_cohorts_config):
    """D-02b: Tier C signals MUST NOT appear in manifest."""
    tiers = pd.DataFrame(
        [
            {
                "signal_id": "t2d_EUR_chr10_r1",
                "gwas_trait": "t2d",
                "gwas_ancestry": "EUR",
                "region": "chr10:100-200",
                "gene_id": "TCF7L2",
                "tissue": "Islet",
                "qtl_source": "gtex",
                "gwas_pph4": 0.95,
                "qtl_pph4": 0.9,
                "tier": "Tier A",
            },
            {
                "signal_id": "t2d_EUR_chr10_r2",
                "gwas_trait": "t2d",
                "gwas_ancestry": "EUR",
                "region": "chr10:300-400",
                "gene_id": "FAKE",
                "tissue": "Liver",
                "qtl_source": "gtex",
                "gwas_pph4": 0.6,
                "qtl_pph4": 0.3,
                "tier": "Tier C",
            },
        ]
    )
    credset = pd.DataFrame()
    (tmp_path / "tiers.tsv").write_text(tiers.to_csv(sep="\t", index=False))
    (tmp_path / "credset.tsv").write_text(credset.to_csv(sep="\t", index=False))
    cfg_path = _write_config(tmp_path, replication_cohorts_config)
    df = build_manifest(
        tmp_path / "credset.tsv",
        tmp_path / "tiers.tsv",
        cfg_path,
        tmp_path / "out.tsv",
    )
    # Only Tier A row should map to manifest rows; Tier C region 300-400 must be absent
    assert not df.empty, "Tier A triple must produce at least one row"
    assert not df["region"].str.contains("300-400").any(), "Tier C region must be excluded"


def test_bbj_only_for_tier_ab(tmp_path: Path, replication_cohorts_config):
    """D-05c: BBJ must never appear for credible_set_SNP rows (tier_ab_only scope)."""
    credset = pd.DataFrame(
        [
            {
                "trait": "t2d",
                "ancestry": "EUR",
                "region": "chr10:100-200",
                "lead_snp": "rs123",
            }
        ]
    )
    tiers = pd.DataFrame()
    (tmp_path / "tiers.tsv").write_text(tiers.to_csv(sep="\t", index=False))
    (tmp_path / "credset.tsv").write_text(credset.to_csv(sep="\t", index=False))
    cfg_path = _write_config(tmp_path, replication_cohorts_config)
    df = build_manifest(
        tmp_path / "credset.tsv",
        tmp_path / "tiers.tsv",
        cfg_path,
        tmp_path / "out.tsv",
    )
    assert not df.empty
    bbj_credset = df[(df["signal_class"] == "credible_set_SNP") & (df["cohort"] == "bbj")]
    assert len(bbj_credset) == 0, "BBJ must never appear for credible_set_SNP rows"


def test_tier_ab_triple_dispatches_to_bbj(tmp_path: Path, replication_cohorts_config):
    """D-05c: Tier A+B EUR triples SHOULD dispatch to BBJ (generalization layer)."""
    tiers = pd.DataFrame(
        [
            {
                "signal_id": "t2d_EUR_chr10_r1",
                "gwas_trait": "t2d",
                "gwas_ancestry": "EUR",
                "region": "chr10:100-200",
                "gene_id": "TCF7L2",
                "tissue": "Islet",
                "qtl_source": "gtex",
                "gwas_pph4": 0.95,
                "qtl_pph4": 0.9,
                "tier": "Tier A",
            }
        ]
    )
    credset = pd.DataFrame()
    (tmp_path / "tiers.tsv").write_text(tiers.to_csv(sep="\t", index=False))
    (tmp_path / "credset.tsv").write_text(credset.to_csv(sep="\t", index=False))
    cfg_path = _write_config(tmp_path, replication_cohorts_config)
    df = build_manifest(
        tmp_path / "credset.tsv",
        tmp_path / "tiers.tsv",
        cfg_path,
        tmp_path / "out.tsv",
    )
    bbj_rows = df[df["cohort"] == "bbj"]
    assert len(bbj_rows) == 1, "Tier A EUR triple must produce exactly 1 BBJ row"
    assert bbj_rows.iloc[0]["is_generalization"] is True or bbj_rows.iloc[0]["is_generalization"] == True  # noqa: E712
    assert bbj_rows.iloc[0]["cohort_ancestry"] == "EAS"


def test_afr_never_finngen(tmp_path: Path, replication_cohorts_config):
    """D-05: AFR discovery must NEVER dispatch to FinnGen (EUR-only cohort)."""
    credset = pd.DataFrame(
        [{"trait": "t2d", "ancestry": "AFR", "region": "chr10:1-2", "lead_snp": "rs1"}]
    )
    tiers = pd.DataFrame()
    (tmp_path / "tiers.tsv").write_text(tiers.to_csv(sep="\t", index=False))
    (tmp_path / "credset.tsv").write_text(credset.to_csv(sep="\t", index=False))
    cfg_path = _write_config(tmp_path, replication_cohorts_config)
    df = build_manifest(
        tmp_path / "credset.tsv",
        tmp_path / "tiers.tsv",
        cfg_path,
        tmp_path / "out.tsv",
    )
    assert not (df["cohort"] == "finngen_r12").any(), "AFR must never route to FinnGen"


def test_eur_never_mvp_afr(tmp_path: Path, replication_cohorts_config):
    """D-05: EUR discovery must NEVER dispatch to MVP-AFR."""
    credset = pd.DataFrame(
        [{"trait": "t2d", "ancestry": "EUR", "region": "chr10:1-2", "lead_snp": "rs1"}]
    )
    tiers = pd.DataFrame()
    (tmp_path / "tiers.tsv").write_text(tiers.to_csv(sep="\t", index=False))
    (tmp_path / "credset.tsv").write_text(credset.to_csv(sep="\t", index=False))
    cfg_path = _write_config(tmp_path, replication_cohorts_config)
    df = build_manifest(
        tmp_path / "credset.tsv",
        tmp_path / "tiers.tsv",
        cfg_path,
        tmp_path / "out.tsv",
    )
    assert not (df["cohort"] == "mvp_afr").any(), "EUR must never route to MVP-AFR"


def test_ld_panel_routed(tmp_path: Path, replication_cohorts_config):
    """D-08: LD panel routed per cohort ancestry."""
    credset = pd.DataFrame(
        [
            {"trait": "t2d", "ancestry": "EUR", "region": "chr10:1-2", "lead_snp": "rs1"},
            {"trait": "t2d", "ancestry": "AFR", "region": "chr10:3-4", "lead_snp": "rs2"},
        ]
    )
    tiers = pd.DataFrame()
    (tmp_path / "tiers.tsv").write_text(tiers.to_csv(sep="\t", index=False))
    (tmp_path / "credset.tsv").write_text(credset.to_csv(sep="\t", index=False))
    cfg_path = _write_config(tmp_path, replication_cohorts_config)
    df = build_manifest(
        tmp_path / "credset.tsv",
        tmp_path / "tiers.tsv",
        cfg_path,
        tmp_path / "out.tsv",
    )
    # EUR -> ukbb_ld; AFR -> hgdp_1kg_afr; BBJ would be EAS -> thousand_g_eas
    assert (df[df["cohort"] == "finngen_r12"]["ld_panel"] == "ukbb_ld").all()
    mvp_afr = df[df["cohort"] == "mvp_afr"]
    assert (mvp_afr["ld_panel"] == "hgdp_1kg_afr").all()


def test_empty_inputs_return_empty(tmp_path: Path, replication_cohorts_config):
    """Both inputs empty -> empty manifest (not a crash)."""
    (tmp_path / "tiers.tsv").write_text(pd.DataFrame().to_csv(sep="\t", index=False))
    (tmp_path / "credset.tsv").write_text(pd.DataFrame().to_csv(sep="\t", index=False))
    cfg_path = _write_config(tmp_path, replication_cohorts_config)
    df = build_manifest(
        tmp_path / "credset.tsv",
        tmp_path / "tiers.tsv",
        cfg_path,
        tmp_path / "out.tsv",
    )
    assert df.empty or len(df) == 0
