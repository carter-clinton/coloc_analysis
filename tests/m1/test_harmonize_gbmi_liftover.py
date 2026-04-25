"""TDD RED — failing tests for harmonize_gbmi.py --liftover-chain extension.

Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md Task 2.

Test cases:
- Case 1: harmonize WITH --liftover-chain pointing at staged hg38ToHg19 chain.
  Output exists; QC sidecar reports liftover drop count.
- Case 2: harmonize WITHOUT --liftover-chain (Phase 09 behavior, no
  liftover) — output schema unchanged.
- Case 3: --liftover-chain pointing to a path with "hg19ToHg38" in the
  basename — must raise ValueError (Pitfall #7 silent wrong-direction).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))


@pytest.fixture
def gbmi_b38_fixture(fixtures_dir: Path) -> Path:
    """Gzipped GBMI b38 fixture (matches production file extension)."""
    return fixtures_dir / "gbmi_b38_head.tsv.gz"


@pytest.fixture
def chain_path(project_root: Path) -> Path:
    return project_root / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"


def test_gbmi_no_liftover_phase09_regression(
    tmp_path: Path, gbmi_b38_fixture: Path
) -> None:
    """Without --liftover-chain, behavior matches Phase 09 (no liftover)."""
    import harmonize_gbmi as hg

    out_prefix = tmp_path / "asthma"
    qc = hg.harmonize_gbmi_sumstats(
        input_gz=gbmi_b38_fixture,
        output_prefix=out_prefix,
        trait="asthma",
        ancestry="eur",
    )
    assert "n_rows" in qc
    expected_out = tmp_path / "asthma_eur.tsv.gz"
    assert expected_out.exists()
    df = pd.read_csv(expected_out, sep="\t", compression="gzip")
    expected_cols = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
    assert list(df.columns)[:10] == expected_cols


def test_gbmi_with_liftover_chain_argparse_present() -> None:
    """The CLI argparse must accept --liftover-chain."""
    import harmonize_gbmi as hg

    # Build the parser the same way _main does.
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output-prefix", required=True)
    ap.add_argument("--trait", required=True)
    ap.add_argument("--ancestry", required=True, choices=sorted(hg.ANCESTRY_PREFIX_MAP))
    # The new argument:
    src = (PROJECT_ROOT / "src" / "python" / "harmonize_gbmi.py").read_text()
    assert "--liftover-chain" in src
    assert "hg38ToHg19" in src


def test_gbmi_liftover_chain_wrong_direction_raises(
    tmp_path: Path, gbmi_b38_fixture: Path
) -> None:
    """--liftover-chain pointing to a hg19ToHg38 path must raise ValueError."""
    import harmonize_gbmi as hg

    bad_chain = tmp_path / "hg19ToHg38.over.chain.gz"
    bad_chain.write_bytes(b"")  # contents irrelevant — guard fires on basename.

    with pytest.raises(ValueError, match="hg38ToHg19"):
        hg.harmonize_gbmi_sumstats(
            input_gz=gbmi_b38_fixture,
            output_prefix=tmp_path / "asthma",
            trait="asthma",
            ancestry="eur",
            liftover_chain=bad_chain,
        )


def test_gbmi_liftover_chain_correct_direction_smoke(
    tmp_path: Path, gbmi_b38_fixture: Path, chain_path: Path
) -> None:
    """If the staged hg38ToHg19 chain is present, liftover is invoked
    (verified by checking qc dict has liftover_drop_rate key)."""
    if not chain_path.exists():
        pytest.skip(f"hg38ToHg19 chain missing at {chain_path}")
    import harmonize_gbmi as hg

    qc = hg.harmonize_gbmi_sumstats(
        input_gz=gbmi_b38_fixture,
        output_prefix=tmp_path / "asthma",
        trait="asthma",
        ancestry="eur",
        liftover_chain=chain_path,
    )
    # The harmonizer prints liftover qc to stderr; the returned dict
    # gains a `liftover_drop_rate` key (or `n_liftover_input` etc.).
    assert any(
        k in qc for k in ("liftover_drop_rate", "n_liftover_input", "n_liftover_lifted")
    ), f"qc dict missing liftover keys: {qc.keys()}"
