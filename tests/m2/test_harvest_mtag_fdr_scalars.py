"""Pin parse + join contracts for src/python/harvest_mtag_fdr_scalars.py.

Production-fire closure of Wave 2-D6 hand-off
(m2-02-task4-mtag-production-fire.md §6).

Two test cases pin the harvest-script behavior BEFORE implementation
(RED-then-GREEN TDD per quick-260429-w2a Task 4 contract):

1. parse_fdr_log — regex extraction of '^FDR of Trait N: <float>'
   from MTAG --fdr run log; fixture embeds the 6 AFR smoke witness
   scalars from quick-260429-utt SMOKE-AFR-FDR.log L46–L51 verbatim
   (mix of fixed-decimal AND scientific notation), asserts exact
   float-precision match for all 6 scalars.

2. rewrite_maxfdr_column — col 11 join on col 12 (trait_key) preserves
   row count + all other cols byte-for-byte; KeyError on unmapped
   trait_key; audit TSV lists per-trait n_rows correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src/python to import path (harvest module lives there)
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

# Module imports MUST happen after path injection (and will fail in RED phase)
import harvest_mtag_fdr_scalars as harvest  # noqa: E402


# ---------------------------------------------------------------------------
# Test 1: parse_fdr_log — regex contract
# ---------------------------------------------------------------------------

# AFR smoke witness from quick-260429-utt SMOKE-AFR-FDR.log L46-L51
# (verbatim; mix of fixed-decimal AND scientific notation).
AFR_SMOKE_LOG_FIXTURE = """
Beginning maxFDR calculations. Depending on the number of grid points specified, this might take some time...
T=6
Optimization terminated successfully.
         Current function value: -4792360.092238
         Iterations: 104
Completed estimation of spike-slab parameters resulting in the following causal probabilities
Trait 0: \t 0.361
Trait 1: \t 0.058
2 probabilities remain after restricting to the grid points with causal probabilities less than one unit (i.e. 1/intervals) from the Spike-Slab fitted causal probabilities.
Number of gridpoints to search: 2
Performing grid search using 4 cores.
Grid search: 100.0 percent finished for . Time: 0.029 min
<><><<>><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
grid point indices for max FDR for each trait: [0 0 0 1 0 0]
FDR with the Spike-Slab parameters
FDR of Trait 1: 0.00970590589390107 at probs = [0.  0.  0.  0.  0.5 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.5]
FDR of Trait 2: 0.003316170693667885 at probs = [0.  0.  0.  0.  0.5 0.  0.  0.5]
FDR of Trait 3: 4.08283132227812e-06 at probs = [0.  0.  0.  0.  0.5 0.5]
FDR of Trait 4: 0.11541401327515466 at probs = [0.5 0.5]
FDR of Trait 5: 8.642644223250632e-09 at probs = [0.  0.  0.  0.  0.5 0.5]
FDR of Trait 6: 0.0017651764636435043 at probs = [0.  0.  0.  0.  0.5 0.5]
<><><<>><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
Completed FDR calculations.
""".lstrip("\n")

# Expected scalars (1-indexed), exact-float-match contract.
AFR_EXPECTED_SCALARS = {
    1: 0.00970590589390107,
    2: 0.003316170693667885,
    3: 4.08283132227812e-06,
    4: 0.11541401327515466,
    5: 8.642644223250632e-09,
    6: 0.0017651764636435043,
}


def test_parse_fdr_log_smoke_witness_exact_float_match(tmp_path: Path) -> None:
    """parse_fdr_log returns the exact 6-scalar AFR smoke witness dict."""
    log = tmp_path / "AFR_mtag_fdr_run.log"
    log.write_text(AFR_SMOKE_LOG_FIXTURE)

    parsed = harvest.parse_fdr_log(log)

    assert parsed == AFR_EXPECTED_SCALARS, (
        f"Expected exact match to AFR smoke witness 6 scalars; got {parsed!r}"
    )


def test_parse_fdr_log_no_fdr_lines_raises(tmp_path: Path) -> None:
    """parse_fdr_log raises ValueError on a log with no 'FDR of Trait' lines."""
    log = tmp_path / "empty_fdr_run.log"
    log.write_text(
        "Beginning maxFDR calculations.\n"
        "T=6\n"
        "Some other content but no FDR of Trait lines.\n"
    )
    with pytest.raises(ValueError, match="No 'FDR of Trait"):
        harvest.parse_fdr_log(log)


def test_parse_fdr_log_handles_scientific_notation(tmp_path: Path) -> None:
    """parse_fdr_log correctly parses scientific notation (e.g., 8.64e-09)."""
    log = tmp_path / "scinot_fdr_run.log"
    log.write_text(
        "FDR of Trait 1: 8.642644223250632e-09 at probs = [...]\n"
        "FDR of Trait 2: 4.08283132227812e-06 at probs = [...]\n"
    )
    parsed = harvest.parse_fdr_log(log)
    assert parsed == {1: 8.642644223250632e-09, 2: 4.08283132227812e-06}


# ---------------------------------------------------------------------------
# Test 2: rewrite_maxfdr_column — column-join contract
# ---------------------------------------------------------------------------

def _make_test_filtered(tmp_path: Path) -> Path:
    """Build a 4-row tab-separated fixture with col 11=0.0 placeholder
    and col 12 alternating between trait_a / trait_b (2 each).

    Schema mirrors the production _mtag_maxfdr_filtered.txt:
      col 1..10:  arbitrary preserved cols
      col 11:     max_FDR = "0.0" (placeholder)
      col 12:     trait_key
    """
    p = tmp_path / "stratum_mtag_maxfdr_filtered.txt"
    header = "\t".join(
        ["SNP", "A1", "A2", "Z", "N", "FRQ", "mtag_beta", "mtag_se",
         "mtag_z", "mtag_pval", "max_FDR", "trait_key"]
    ) + "\n"
    rows = [
        "rs1\tA\tG\t1.0\t100\t0.5\t0.1\t0.01\t10.0\t1e-23\t0.0\ttrait_a\n",
        "rs2\tC\tT\t2.0\t200\t0.3\t0.2\t0.02\t10.0\t1e-23\t0.0\ttrait_b\n",
        "rs3\tA\tG\t3.0\t150\t0.4\t0.15\t0.015\t10.0\t1e-23\t0.0\ttrait_a\n",
        "rs4\tC\tT\t4.0\t250\t0.6\t0.25\t0.025\t10.0\t1e-23\t0.0\ttrait_b\n",
    ]
    p.write_text(header + "".join(rows))
    return p


def test_rewrite_maxfdr_column_join_contract(tmp_path: Path) -> None:
    """rewrite_maxfdr_column rewrites col 11 from 0.0 placeholder to mapped
    scalars by joining on col 12; preserves row count + all other cols."""
    filtered = _make_test_filtered(tmp_path)
    audit = tmp_path / "stratum_mtag_fdr_audit.tsv"
    mapping = {"trait_a": 0.5, "trait_b": 0.01}

    pre_lines = filtered.read_text().splitlines()
    pre_header = pre_lines[0]

    harvest.rewrite_maxfdr_column(filtered, mapping, audit)

    post_lines = filtered.read_text().splitlines()
    post_header = post_lines[0]
    post_data = post_lines[1:]

    # (a) Header bytes preserved
    assert post_header == pre_header

    # (b) Row count preserved (header + 4 data rows)
    assert len(post_data) == 4

    # (c) Col 11 distinct values become exactly the K=2 mapped scalars
    col11 = sorted({line.split("\t")[10] for line in post_data})
    expected = sorted({repr(0.5), repr(0.01)})
    assert col11 == expected, f"col 11 distinct mismatch: {col11!r} vs {expected!r}"

    # (d) Col 12 unchanged byte-for-byte (per-row check)
    for pre, post in zip(pre_lines[1:], post_data):
        assert pre.split("\t")[11] == post.split("\t")[11]

    # (e) All other cols (1-10) unchanged byte-for-byte (per-row check)
    for pre, post in zip(pre_lines[1:], post_data):
        pre_cols = pre.split("\t")
        post_cols = post.split("\t")
        for i in list(range(0, 10)):  # 0-indexed: cols 1-10
            assert pre_cols[i] == post_cols[i], f"col {i+1} mutated at row"

    # Audit TSV: 2 rows with correct n_rows counts
    audit_lines = audit.read_text().splitlines()
    assert audit_lines[0] == "trait_key\tmax_FDR\tn_rows"
    audit_data = {
        line.split("\t")[0]: int(line.split("\t")[2])
        for line in audit_lines[1:]
    }
    assert audit_data == {"trait_a": 2, "trait_b": 2}


def test_rewrite_maxfdr_column_unmapped_trait_key_raises(tmp_path: Path) -> None:
    """rewrite_maxfdr_column raises KeyError if a row's trait_key is not in
    the mapping; offending key appears in the message."""
    filtered = _make_test_filtered(tmp_path)
    audit = tmp_path / "stratum_mtag_fdr_audit.tsv"
    mapping = {"trait_a": 0.5}  # trait_b deliberately missing

    with pytest.raises(KeyError, match="trait_b"):
        harvest.rewrite_maxfdr_column(filtered, mapping, audit)
