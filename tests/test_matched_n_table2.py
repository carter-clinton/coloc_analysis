"""Integration test: Table 2 output structure (D-06a) + column order.

Table 2 must have one row per trait and the 10 required columns
specified in D-06a: trait, N_AFR_eff, N_EUR_eff, N_EUR_matched,
unmatched_concordance_pct, matched_concordance_pct, matched_ci95,
expected_concordance_hou_pct, rg_eur_afr_formatted, h7_verdict.

References:
    - D-06a: Table 2 row-per-trait structure with 10 required columns
    - D-06b: Secondary Table 2b with credible-set Jaccard per trait
"""
import os
import tempfile

import pandas as pd
import pytest
import yaml

from src.python.assemble_table2 import FINAL_COLS, assemble


# ---------------------------------------------------------------------------
# Synthetic fixture data (5 traits)
# ---------------------------------------------------------------------------
TRAITS = ["t2d", "stroke", "hypertension", "asthma", "bmi"]

SAMPLE_SIZES = {
    "t2d": {"AFR": 55525, "EUR": 228499},
    "stroke": {"AFR": 24000, "EUR": 446696},
    "hypertension": {"AFR": 28000, "EUR": 463010},
    "asthma": {"AFR": 15000, "EUR": 408354},
    "bmi": {"AFR": 55500, "EUR": 681275},
}


def _write_synthetic_inputs(tmpdir):
    """Create synthetic TSV inputs for assemble()."""
    # tier_a_retention.tsv
    tier = pd.DataFrame({
        "trait": TRAITS,
        "n_afr_tier_a": [10, 8, 12, 6, 9],
        "mean_retention": [0.72, 0.65, 0.80, 0.55, 0.70],
        "ci95_lo": [0.60, 0.50, 0.70, 0.40, 0.55],
        "ci95_hi": [0.84, 0.78, 0.90, 0.68, 0.82],
        "n_bootstraps": [100] * 5,
        "unmatched_concordance": [0.90, 0.88, 0.85, 0.80, 0.87],
    })
    tier_path = os.path.join(tmpdir, "tier_a_retention.tsv")
    tier.to_csv(tier_path, sep="\t", index=False)

    # jaccard.tsv
    jac = pd.DataFrame({
        "trait": TRAITS,
        "mean_jaccard": [0.45, 0.38, 0.52, 0.30, 0.42],
        "ci95_lo": [0.35, 0.28, 0.42, 0.20, 0.32],
        "ci95_hi": [0.55, 0.48, 0.62, 0.40, 0.52],
        "n_locus_pairs": [10, 8, 12, 6, 9],
    })
    jac_path = os.path.join(tmpdir, "jaccard.tsv")
    jac.to_csv(jac_path, sep="\t", index=False)

    # detection_probability.tsv
    det = pd.DataFrame({
        "trait": TRAITS,
        "expected_concordance_hou_null": [0.50, 0.42, 0.55, 0.35, 0.48],
    })
    det_path = os.path.join(tmpdir, "detection_probability.tsv")
    det.to_csv(det_path, sep="\t", index=False)

    # rg_matrix.tsv (D-04d) — only the 5 same-trait EUR-AFR benchmarks matter
    rg = pd.DataFrame({
        "trait1": TRAITS,
        "trait2": TRAITS,
        "rg": [0.85, 0.78, 0.92, 0.70, 0.88],
        "se": [0.05, 0.08, 0.04, 0.10, 0.06],
        "is_global_benchmark": [True] * 5,
        "ancestry_pair": ["EUR_AFR"] * 5,
    })
    rg_path = os.path.join(tmpdir, "rg_matrix.tsv")
    rg.to_csv(rg_path, sep="\t", index=False)

    # config/matched_n.yaml
    cfg = {"h7_reduction_threshold_pp": 20, "traits": TRAITS}
    cfg_path = os.path.join(tmpdir, "matched_n.yaml")
    with open(cfg_path, "w") as fh:
        yaml.dump(cfg, fh)

    # config/trait_sample_sizes.yaml
    ns_path = os.path.join(tmpdir, "trait_sample_sizes.yaml")
    with open(ns_path, "w") as fh:
        yaml.dump(SAMPLE_SIZES, fh)

    return {
        "tier": tier_path,
        "jaccard": jac_path,
        "detection": det_path,
        "rg": rg_path,
        "config": cfg_path,
        "sample_sizes": ns_path,
    }


@pytest.mark.phase4
class TestTable2Assembly:
    """D-06a Table 2 structure and content tests."""

    def test_table2_has_5_rows_10_cols(self, tmp_path):
        """Verify Table 2 has 5 rows (one per trait) and 10 columns per D-06a."""
        inputs = _write_synthetic_inputs(str(tmp_path))
        out_t2 = os.path.join(str(tmp_path), "table2.tsv")
        out_jac = os.path.join(str(tmp_path), "table2_jaccard.tsv")

        assemble(
            tier_a_tsv=inputs["tier"],
            jaccard_tsv=inputs["jaccard"],
            detection_tsv=inputs["detection"],
            rg_matrix_tsv=inputs["rg"],
            trait_sample_sizes_yaml=inputs["sample_sizes"],
            config_yaml=inputs["config"],
            out_table2=out_t2,
            out_table2_jaccard=out_jac,
        )

        df = pd.read_csv(out_t2, sep="\t")
        assert len(df) == 5, f"Expected 5 rows, got {len(df)}"
        assert len(df.columns) == 10, f"Expected 10 columns, got {len(df.columns)}"

    def test_table2_column_order(self, tmp_path):
        """Assert column order matches D-06a FINAL_COLS exactly."""
        inputs = _write_synthetic_inputs(str(tmp_path))
        out_t2 = os.path.join(str(tmp_path), "table2.tsv")
        out_jac = os.path.join(str(tmp_path), "table2_jaccard.tsv")

        assemble(
            tier_a_tsv=inputs["tier"],
            jaccard_tsv=inputs["jaccard"],
            detection_tsv=inputs["detection"],
            rg_matrix_tsv=inputs["rg"],
            trait_sample_sizes_yaml=inputs["sample_sizes"],
            config_yaml=inputs["config"],
            out_table2=out_t2,
            out_table2_jaccard=out_jac,
        )

        df = pd.read_csv(out_t2, sep="\t")
        assert list(df.columns) == FINAL_COLS

    def test_table2_n_eur_matched_equals_n_afr(self, tmp_path):
        """N_EUR_matched must equal N_AFR_eff (matched down to AFR power)."""
        inputs = _write_synthetic_inputs(str(tmp_path))
        out_t2 = os.path.join(str(tmp_path), "table2.tsv")
        out_jac = os.path.join(str(tmp_path), "table2_jaccard.tsv")

        assemble(
            tier_a_tsv=inputs["tier"],
            jaccard_tsv=inputs["jaccard"],
            detection_tsv=inputs["detection"],
            rg_matrix_tsv=inputs["rg"],
            trait_sample_sizes_yaml=inputs["sample_sizes"],
            config_yaml=inputs["config"],
            out_table2=out_t2,
            out_table2_jaccard=out_jac,
        )

        df = pd.read_csv(out_t2, sep="\t")
        assert (df["N_EUR_matched"] == df["N_AFR_eff"]).all()

    def test_table2_h7_verdicts_correct(self, tmp_path):
        """Verify H7 verdicts match expected from synthetic data.

        Synthetic: unmatched=90%,88%,85%,80%,87%  matched=72%,65%,80%,55%,70%
        Reductions: 18, 23, 5, 25, 17 pp
        Expected verdicts: holds, artifact, holds, artifact, holds
        """
        inputs = _write_synthetic_inputs(str(tmp_path))
        out_t2 = os.path.join(str(tmp_path), "table2.tsv")
        out_jac = os.path.join(str(tmp_path), "table2_jaccard.tsv")

        assemble(
            tier_a_tsv=inputs["tier"],
            jaccard_tsv=inputs["jaccard"],
            detection_tsv=inputs["detection"],
            rg_matrix_tsv=inputs["rg"],
            trait_sample_sizes_yaml=inputs["sample_sizes"],
            config_yaml=inputs["config"],
            out_table2=out_t2,
            out_table2_jaccard=out_jac,
        )

        df = pd.read_csv(out_t2, sep="\t")
        expected = [
            "concordance_holds",   # t2d:   90-72=18 < 20
            "power_artifact",      # stroke: 88-65=23 >= 20
            "concordance_holds",   # hyp:   85-80=5 < 20
            "power_artifact",      # asthma: 80-55=25 >= 20
            "concordance_holds",   # bmi:   87-70=17 < 20
        ]
        assert list(df["h7_verdict"]) == expected

    def test_table2_rg_formatted(self, tmp_path):
        """Verify r_g column is formatted as 'X.XXX +/- Y.YYY'."""
        inputs = _write_synthetic_inputs(str(tmp_path))
        out_t2 = os.path.join(str(tmp_path), "table2.tsv")
        out_jac = os.path.join(str(tmp_path), "table2_jaccard.tsv")

        assemble(
            tier_a_tsv=inputs["tier"],
            jaccard_tsv=inputs["jaccard"],
            detection_tsv=inputs["detection"],
            rg_matrix_tsv=inputs["rg"],
            trait_sample_sizes_yaml=inputs["sample_sizes"],
            config_yaml=inputs["config"],
            out_table2=out_t2,
            out_table2_jaccard=out_jac,
        )

        df = pd.read_csv(out_t2, sep="\t")
        for val in df["rg_eur_afr_formatted"]:
            assert "+/-" in val, f"Expected +/- format, got: {val}"

    def test_table2b_jaccard_output(self, tmp_path):
        """D-06b Table 2b must have jaccard columns."""
        inputs = _write_synthetic_inputs(str(tmp_path))
        out_t2 = os.path.join(str(tmp_path), "table2.tsv")
        out_jac = os.path.join(str(tmp_path), "table2_jaccard.tsv")

        assemble(
            tier_a_tsv=inputs["tier"],
            jaccard_tsv=inputs["jaccard"],
            detection_tsv=inputs["detection"],
            rg_matrix_tsv=inputs["rg"],
            trait_sample_sizes_yaml=inputs["sample_sizes"],
            config_yaml=inputs["config"],
            out_table2=out_t2,
            out_table2_jaccard=out_jac,
        )

        jdf = pd.read_csv(out_jac, sep="\t")
        assert len(jdf) == 5
        assert "mean_jaccard" in jdf.columns
        assert "trait" in jdf.columns
