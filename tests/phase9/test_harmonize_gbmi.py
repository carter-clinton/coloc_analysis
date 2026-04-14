"""Unit tests for harmonize_gbmi.py (Plan 09-02 Task 3, B-2 guard)."""
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from harmonize_gbmi import (  # noqa: E402
    ANCESTRY_PREFIX_MAP,
    harmonize_gbmi_sumstats,
)


def test_gbmi_canonical_output_eur(mock_gbmi_sumstats, tmp_path, canonical_schema):
    prefix = tmp_path / "gbmi_t2d"
    qc = harmonize_gbmi_sumstats(
        mock_gbmi_sumstats, prefix, trait="t2d", ancestry="eur"
    )
    df = pd.read_csv(qc["output"], sep="\t", compression="gzip")
    for col in canonical_schema:
        assert col in df.columns, f"missing {col}"
    assert qc["ancestry"] == "eur"
    assert qc["cohort"] == "gbmi_eur"
    # mock fixture has all_meta_beta = 0.09
    assert (df["BETA"] == 0.09).all()


def test_gbmi_missing_afr_columns_raises_clear_error(mock_gbmi_sumstats, tmp_path):
    """B-2 guard: an EUR-only file must FAIL LOUDLY when asked for AFR stratum.

    The mock fixture only has `all_meta_*` columns; requesting ancestry=afr
    must raise ValueError that names afr_meta and lists the actual columns.
    """
    prefix = tmp_path / "gbmi_t2d"
    with pytest.raises(ValueError, match="afr_meta"):
        harmonize_gbmi_sumstats(
            mock_gbmi_sumstats, prefix, trait="t2d", ancestry="afr"
        )


def test_gbmi_invalid_ancestry_raises():
    with pytest.raises(ValueError, match="not in"):
        harmonize_gbmi_sumstats(
            Path("/dev/null"), Path("/tmp/x"), trait="t2d", ancestry="xxx"
        )


def test_gbmi_ancestry_prefix_map_has_all_five():
    """AR/AMR/EAS/EUR/SAS strata supported per config."""
    assert set(ANCESTRY_PREFIX_MAP) == {"eur", "afr", "eas", "amr", "sas"}
    assert ANCESTRY_PREFIX_MAP["eur"] == "all_meta"
    assert ANCESTRY_PREFIX_MAP["afr"] == "afr_meta"
