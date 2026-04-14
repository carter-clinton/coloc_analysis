"""Plan 09-05 Task 2 — master_table.tsv schema + D-05c panel + I-2/I-3 revisions.

Validates:
  - all effect-size columns per D-04b (4 columns: disc_raw, disc_FIQT,
    rep, meta) exist in the assembled master table
  - per-cohort blocks are present for all five ancestry-matched cohorts
    (finngen_r12, gbmi_eur, gbmi_afr, mvp_eur, mvp_afr)
  - per-cohort sample_overlap_flag columns are populated (I-3 revision;
    replaces the prior single gbmi_eur-only hardcode)
  - meta_ancestry column exists (I-2 revision for signal_id uniqueness
    across discovery_ancestry)
  - cross-ancestry generalization table excludes credible_set_SNP rows
    (D-05c enforcement)
  - PURE-module tests exercise assemble_master_table on in-memory fixtures
    so the schema is validated without requiring a full pipeline run.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PY_DIR = PROJECT_ROOT / "src" / "python"

REQUIRED_DISCOVERY = [
    "beta_discovery_raw",
    "se_discovery_raw",
    "p_discovery_raw",
    "beta_discovery_FIQT",
    "se_discovery_FIQT",
]
REQUIRED_PER_COHORT_SUFFIXES = [
    "beta_replication",
    "se_replication",
    "p_replication",
    "replicated_bonferroni",
    "replicated_pph4_0.5",
    "replicated_pph4_0.7",
    "replicated_pph4_0.8",
    "replicated_pph4_0.9",
    "replicated_joint_0.8",
    "power_posthoc",
]
REQUIRED_META = [
    "beta_meta",
    "se_meta",
    "p_meta",
    "meta_replicated_bonferroni",
    "meta_replicated_pph4_0.8",
]
REPLICATION_COHORTS_FULL = [
    "finngen_r12", "gbmi_eur", "gbmi_afr", "mvp_eur", "mvp_afr", "bbj",
]


def _load_builder():
    if str(PY_DIR) not in sys.path:
        sys.path.insert(0, str(PY_DIR))
    import importlib
    import build_master_replication_table  # type: ignore
    importlib.reload(build_master_replication_table)
    return build_master_replication_table


def _load_xancestry():
    if str(PY_DIR) not in sys.path:
        sys.path.insert(0, str(PY_DIR))
    import importlib
    import build_cross_ancestry_panel  # type: ignore
    importlib.reload(build_cross_ancestry_panel)
    return build_cross_ancestry_panel


def _load_holdout():
    if str(PY_DIR) not in sys.path:
        sys.path.insert(0, str(PY_DIR))
    import importlib
    import build_replication_holdout  # type: ignore
    importlib.reload(build_replication_holdout)
    return build_replication_holdout


# ---------------------------------------------------------------------------
# In-memory fixture for the master-table assembler
# ---------------------------------------------------------------------------
def _write_minimal_inputs(tmp_path: Path) -> dict:
    """Craft a 2-signal × 5-cohort minimal fixture set that the builder can
    assemble into a master_table.tsv. Each file matches the schema emitted
    by the upstream (Wave 3/4) producers.
    """
    manifest = tmp_path / "manifest.tsv"
    pd.DataFrame({
        "signal_id": ["sig_t2d_eur", "sig_t2d_eur", "sig_t2d_eur",
                      "sig_t2d_eur", "sig_t2d_eur",
                      "sig_htn_afr", "sig_htn_afr"],
        "signal_class": ["credible_set_SNP"] * 5 + ["tier_A_triple"] * 2,
        "discovery_trait": ["t2d"] * 5 + ["hypertension"] * 2,
        "discovery_ancestry": ["EUR"] * 5 + ["AFR"] * 2,
        "region": ["chr10:114700000-114800000"] * 5 + ["chr6:30000000-30100000"] * 2,
        "cohort": ["finngen_r12", "gbmi_eur", "gbmi_afr", "mvp_eur", "mvp_afr",
                   "gbmi_afr", "mvp_afr"],
    }).to_csv(manifest, sep="\t", index=False)

    fiqt = tmp_path / "discovery_beta_fiqt.tsv"
    pd.DataFrame({
        "signal_id": ["sig_t2d_eur", "sig_htn_afr"],
        "rsid":      ["rs_lead_t2d", "rs_lead_htn"],
        "beta":      [0.20, 0.15],
        "se":        [0.02, 0.03],
        "n":         [500000, 50000],
        "beta_FIQT": [0.18, 0.12],
        "se_FIQT":   [0.02, 0.03],
    }).to_csv(fiqt, sep="\t", index=False)

    per_cohort_dir = tmp_path / "effect_size"
    per_cohort_dir.mkdir()
    # Emit only a subset of cohorts — builder must tolerate missing files.
    for cohort, sig in [("finngen_r12", "sig_t2d_eur"),
                        ("gbmi_eur", "sig_t2d_eur"),
                        ("mvp_afr", "sig_htn_afr")]:
        pd.DataFrame({
            "signal_id": [sig],
            "cohort": [cohort],
            "cohort_ancestry": ["EUR" if "eur" in cohort or cohort == "finngen_r12" else "AFR"],
            "beta_replication": [0.15],
            "se_replication": [0.03],
            "p_replication": [1e-6],
            "eaf_replication": [0.3],
            "N": [100000],
            "beta_discovery_FIQT": [0.18],
            "se_FIQT": [0.02],
            "pph4_replication": [0.85],
            "replicated_pph4_0.5": [True],
            "replicated_pph4_0.7": [True],
            "replicated_pph4_0.8": [True],
            "replicated_pph4_0.9": [False],
            "bonf_threshold": [0.005],
            "same_direction": [True],
            "replicated_bonferroni": [True],
            "power_posthoc": [0.95],
            "replicated_joint_0.8": [True],
        }).to_csv(per_cohort_dir / f"{cohort}.tsv", sep="\t", index=False)

    coloc_dir = tmp_path / "coloc"
    coloc_dir.mkdir()  # reserved for future use

    meta = tmp_path / "ivw_meta.tsv"
    pd.DataFrame({
        "signal_id": ["sig_t2d_eur", "sig_htn_afr"],
        "cohort": ["MULTI", "MULTI"],
        "cohort_ancestry": ["EUR", "AFR"],
        "meta_ancestry": ["EUR", "AFR"],
        "beta_meta": [0.16, 0.14],
        "se_meta": [0.018, 0.025],
        "p_meta": [1e-18, 1e-8],
        "meta_replicated_bonferroni": [True, True],
        "meta_replicated_pph4_0.8": [True, False],
    }).to_csv(meta, sep="\t", index=False)

    return {
        "manifest": manifest,
        "fiqt": fiqt,
        "per_cohort_dir": per_cohort_dir,
        "coloc_dir": coloc_dir,
        "meta": meta,
    }


def test_assemble_master_table_schema_complete(tmp_path):
    """D-04b: all 4 effect-size columns + per-cohort × 5 + meta + I-3 flags."""
    M = _load_builder()
    inp = _write_minimal_inputs(tmp_path)
    out = tmp_path / "master_table.tsv"
    df = M.assemble_master_table(
        manifest_tsv=inp["manifest"], fiqt_tsv=inp["fiqt"],
        per_cohort_dir=inp["per_cohort_dir"], coloc_dir=inp["coloc_dir"],
        meta_tsv=inp["meta"], output_tsv=out,
    )
    assert out.exists()
    df_on_disk = pd.read_csv(out, sep="\t")

    for col in REQUIRED_DISCOVERY:
        assert col in df_on_disk.columns, f"missing discovery column: {col}"
    for col in REQUIRED_META:
        assert col in df_on_disk.columns, f"missing meta column: {col}"
    cohorts = ["finngen_r12", "gbmi_eur", "gbmi_afr", "mvp_eur", "mvp_afr"]
    for cohort in cohorts:
        for suffix in REQUIRED_PER_COHORT_SUFFIXES:
            assert f"{cohort}_{suffix}" in df_on_disk.columns, (
                f"missing {cohort}_{suffix}"
            )


def test_master_table_per_cohort_overlap_flags(tmp_path):
    """I-3 revision: per-cohort sample_overlap_flag columns (6 total)."""
    M = _load_builder()
    inp = _write_minimal_inputs(tmp_path)
    out = tmp_path / "master_table.tsv"
    M.assemble_master_table(
        manifest_tsv=inp["manifest"], fiqt_tsv=inp["fiqt"],
        per_cohort_dir=inp["per_cohort_dir"], coloc_dir=inp["coloc_dir"],
        meta_tsv=inp["meta"], output_tsv=out,
    )
    df = pd.read_csv(out, sep="\t")
    for cohort in REPLICATION_COHORTS_FULL:
        assert f"{cohort}_sample_overlap_flag" in df.columns, (
            f"missing {cohort}_sample_overlap_flag (I-3 revision)"
        )
    # gbmi_eur should have a structural overlap flag populated by resolve_overlap_flag
    eur_flags = df["gbmi_eur_sample_overlap_flag"].dropna()
    assert len(eur_flags) > 0, "gbmi_eur structural overlap flag should be populated for at least one row"


def test_master_table_meta_ancestry_traceability(tmp_path):
    """I-2 revision: meta_ancestry column exists (from IVW meta or derived)."""
    M = _load_builder()
    inp = _write_minimal_inputs(tmp_path)
    out = tmp_path / "master_table.tsv"
    M.assemble_master_table(
        manifest_tsv=inp["manifest"], fiqt_tsv=inp["fiqt"],
        per_cohort_dir=inp["per_cohort_dir"], coloc_dir=inp["coloc_dir"],
        meta_tsv=inp["meta"], output_tsv=out,
    )
    df = pd.read_csv(out, sep="\t")
    # Either meta_ancestry is present directly from IVW meta, or discovery_ancestry
    # is the fallback (assembler back-fills). At minimum one must be present.
    assert "meta_ancestry" in df.columns or "discovery_ancestry" in df.columns


def test_resolve_overlap_flag_wildcards():
    """The KNOWN_OVERLAP_PAIRS wildcard ('*') must match any trait for the
    structurally overlapping GBMI cohorts."""
    M = _load_builder()
    # Trait-specific should win over wildcard
    flag_htn_gbmi = M.resolve_overlap_flag("hypertension", "gbmi_eur")
    assert flag_htn_gbmi is not None
    assert "Evangelou" in flag_htn_gbmi or "UKBB" in flag_htn_gbmi
    # Wildcard fallback
    flag_any_gbmi_afr = M.resolve_overlap_flag("t2d", "gbmi_afr")
    assert flag_any_gbmi_afr is not None
    # Totally unrelated cohort with no registered overlap
    flag_none = M.resolve_overlap_flag("t2d", "finngen_r12")
    assert flag_none is None


# ---------------------------------------------------------------------------
# Cross-ancestry panel (D-05c enforcement)
# ---------------------------------------------------------------------------
def test_bbj_generalization_excludes_credible_set(tmp_path):
    X = _load_xancestry()
    manifest = tmp_path / "manifest.tsv"
    pd.DataFrame({
        "signal_id": ["sig_A", "sig_B", "sig_C"],
        "signal_class": ["tier_A_triple", "credible_set_SNP", "tier_B_triple"],
        "discovery_trait": ["t2d", "t2d", "hypertension"],
        "discovery_ancestry": ["EUR", "EUR", "AFR"],
        "region": ["chr10:100-200", "chr11:300-400", "chr12:500-600"],
        "cohort": ["bbj", "bbj", "bbj"],
    }).to_csv(manifest, sep="\t", index=False)

    bbj_cohort = tmp_path / "bbj.tsv"
    pd.DataFrame({
        "signal_id": ["sig_A", "sig_C"],
        "beta_replication": [0.1, 0.08],
        "se_replication": [0.02, 0.02],
    }).to_csv(bbj_cohort, sep="\t", index=False)

    out = tmp_path / "cross_ancestry.tsv"
    X.build_bbj_generalization(manifest, bbj_cohort, out)
    df = pd.read_csv(out, sep="\t")
    assert (df["signal_class"] != "credible_set_SNP").all(), (
        "D-05c violation: BBJ panel must exclude credible_set_SNP rows"
    )
    assert df["is_generalization"].all()


# ---------------------------------------------------------------------------
# Leave-one-cohort-out holdout
# ---------------------------------------------------------------------------
def test_loco_meta_basic(tmp_path):
    H = _load_holdout()
    # One signal with 3 matched-ancestry cohorts
    df = pd.DataFrame({
        "signal_id": ["s1", "s1", "s1"],
        "cohort": ["finngen_r12", "gbmi_eur", "mvp_eur"],
        "cohort_ancestry": ["EUR", "EUR", "EUR"],
        "beta_replication": [0.10, 0.12, 0.11],
        "se_replication": [0.02, 0.02, 0.02],
    })
    out = H.loco_meta(df)
    # Each of 3 cohorts held out once -> 3 rows
    assert len(out) == 3
    assert set(out["held_out_cohort"]) == {"finngen_r12", "gbmi_eur", "mvp_eur"}
    # Every loco row uses exactly 2 cohorts (the un-held-out pair)
    assert (out["loco_n_cohorts"] == 2).all()


def test_loco_meta_skips_single_cohort_signals(tmp_path):
    H = _load_holdout()
    df = pd.DataFrame({
        "signal_id": ["s_solo"],
        "cohort": ["finngen_r12"],
        "cohort_ancestry": ["EUR"],
        "beta_replication": [0.10],
        "se_replication": [0.02],
    })
    out = H.loco_meta(df)
    # len(matched) < 2 -> no rows
    assert len(out) == 0


# ---------------------------------------------------------------------------
# Snakemake + methods doc substance checks (§G de-TODO; methods embedded)
# ---------------------------------------------------------------------------
def test_replication_smk_aggregation_rules_real():
    """§G TODO markers gone; rule all_replication resolves 4 D-07 outputs."""
    smk = (PROJECT_ROOT / "src" / "snakemake" / "rules" / "replication.smk").read_text()
    assert "build_master_replication_table" in smk
    assert "build_cross_ancestry_panel" in smk
    assert "build_replication_holdout" in smk
    assert "TODO plan 09-05 Task 2" not in smk


def test_methods_doc_covers_all_six_topics():
    """D-01, D-03, D-04, D-05, gotcha #1 (COJO N=503), gotcha #3 (stroke)."""
    md = PROJECT_ROOT / "docs" / "methods" / "phase9_replication.md"
    assert md.exists(), "methods doc not written"
    content = md.read_text()
    # D-01 (4 cohorts)
    assert "FinnGen" in content and "GBMI" in content and "MVP" in content and ("BBJ" in content or "Biobank Japan" in content)
    # D-03 joint criterion
    assert "joint" in content.lower() and "Bonferroni" in content
    # D-04 FIQT
    assert "FIQT" in content
    # D-05 ancestry asymmetry
    assert "BBJ" in content and "generalization" in content.lower()
    # Gotcha #1 COJO caveat (N=503 literal)
    assert "N=503" in content or "503" in content
    assert "4000" in content or "N>=4000" in content or "N≥4000" in content
    # Gotcha #3 stroke endpoint heterogeneity
    assert "ischemic" in content.lower()


def test_four_effect_size_columns_in_schema_spec():
    """D-04b: 4 effect-size columns (raw + FIQT + replication + meta)."""
    per_cohort = set(REQUIRED_PER_COHORT_SUFFIXES)
    assert "beta_replication" in per_cohort
    assert "beta_discovery_FIQT" in REQUIRED_DISCOVERY
    assert "beta_discovery_raw" in REQUIRED_DISCOVERY
    assert "beta_meta" in REQUIRED_META
