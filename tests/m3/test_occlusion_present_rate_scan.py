"""RED-first tests for src/python/occlusion_present_rate_scan.py (m3-07a Wave 0, T3).

The present-rate scan QUANTIFIES THE SCIENTIFIC COST of the pre-registered
exclusion policy: for each occluded variant, in how many of the n AFR harmonized
sumstats does a row actually exist? That k/n is (a) the Angle-1/3 catalog seed and
(b) the concrete evidence that retired NaN->0 as directionally wrong — the harm was
made concrete by rs182965575, present in 7 of 9 AFR sumstats, which NaN->0 would
have silently conditioned to "no LD" instead of honestly excluding.

Harmonized AFR sumstats header (public GRCh37):
    CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD
CHR/POS are located BY NAME (auto-detected), not by column position.

RED-for-the-right-reason: ``occlusion_present_rate_scan`` does not exist yet (07c
builds it). It is imported INSIDE each test body so pytest COLLECTS cleanly and
each test fails as a test/assert failure, NOT a collection error.

The real 9-file genome-wide scan is an integration/validation step, not a unit
test — these run on tiny synthetic TSV fixtures.

Runs in smoke_dev py3.11 (pandas). No Hail.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import occlusion_present_rate_scan`` — see the docstring.

_HARMONIZED_HEADER = [
    "CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N",
    "SNP_ID", "TRAIT", "ANCESTRY", "BUILD",
]


def _row(chrom: int, pos: int, trait: str) -> dict:
    """One harmonized-sumstats row with plausible values."""
    return {
        "CHR": chrom, "POS": pos, "REF": "A", "ALT": "G",
        "BETA": 0.012, "SE": 0.004, "P": 3.1e-3, "EAF": 0.21, "N": 15000,
        "SNP_ID": f"{chrom}:{pos}:A:G", "TRAIT": trait,
        "ANCESTRY": "AFR", "BUILD": "GRCh37",
    }


def _write_sumstats(path: Path, rows: list[dict], columns: list[str] | None = None) -> Path:
    """Write a tiny harmonized AFR sumstats TSV."""
    import pandas as pd

    cols = columns or _HARMONIZED_HEADER
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=cols).to_csv(path, sep="\t", index=False)
    return path


# --------------------------------------------------------------------------- #
# 1. present rate = k / n                                                      #
# --------------------------------------------------------------------------- #

def test_variant_present_in_k_of_n_files_gives_rate_k_over_n(tmp_path):
    """A variant present in 2 of 3 sumstats -> present_rate == 2/3, with the
    numerator/denominator both recorded (n_traits_present / n_traits_scanned)."""
    import occlusion_present_rate_scan as prs

    target = (1, 5_982_778)   # snpC on GRCh37 (the pair-4 occluded variant)
    other = (1, 7_000_000)

    f1 = _write_sumstats(tmp_path / "bmi.AFR.tsv", [_row(*target, "bmi"), _row(*other, "bmi")])
    f2 = _write_sumstats(tmp_path / "ldl.AFR.tsv", [_row(*target, "ldl")])
    f3 = _write_sumstats(tmp_path / "sbp.AFR.tsv", [_row(*other, "sbp")])  # target ABSENT

    res = prs.scan_present_rate([target], [f1, f2, f3])

    rec = res[target]
    assert rec["n_traits_present"] == 2
    assert rec["n_traits_scanned"] == 3
    assert rec["present_rate"] == pytest.approx(2 / 3)


def test_absent_variant_gives_zero(tmp_path):
    """A variant in NONE of the scanned files -> present_rate 0.0 (0 of n), NOT a
    missing key and NOT a division error."""
    import occlusion_present_rate_scan as prs

    absent = (1, 5_982_778)
    f1 = _write_sumstats(tmp_path / "bmi.AFR.tsv", [_row(1, 7_000_000, "bmi")])
    f2 = _write_sumstats(tmp_path / "ldl.AFR.tsv", [_row(1, 8_000_000, "ldl")])

    res = prs.scan_present_rate([absent], [f1, f2])

    rec = res[absent]
    assert rec["n_traits_present"] == 0
    assert rec["n_traits_scanned"] == 2
    assert rec["present_rate"] == 0.0


def test_variant_present_in_every_file_gives_rate_one(tmp_path):
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    f1 = _write_sumstats(tmp_path / "bmi.AFR.tsv", [_row(*v, "bmi")])
    f2 = _write_sumstats(tmp_path / "ldl.AFR.tsv", [_row(*v, "ldl")])

    res = prs.scan_present_rate([v], [f1, f2])
    assert res[v]["present_rate"] == 1.0
    assert res[v]["n_traits_present"] == 2


# --------------------------------------------------------------------------- #
# 2. traits_present enrichment (feeds the manifest column)                     #
# --------------------------------------------------------------------------- #

def test_traits_present_names_the_traits_where_the_variant_exists(tmp_path):
    """The scan reports WHICH traits carry the variant — that list is the
    manifest's traits_present column and the Angle-1/3 catalog payload."""
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    f1 = _write_sumstats(tmp_path / "bmi.AFR.tsv", [_row(*v, "bmi")])
    f2 = _write_sumstats(tmp_path / "ldl.AFR.tsv", [_row(1, 9_000_000, "ldl")])
    f3 = _write_sumstats(tmp_path / "sbp.AFR.tsv", [_row(*v, "sbp")])

    res = prs.scan_present_rate([v], [f1, f2, f3])

    assert sorted(res[v]["traits_present"]) == ["bmi", "sbp"]


# --------------------------------------------------------------------------- #
# 3. CHR/POS auto-detection (by NAME, not position)                            #
# --------------------------------------------------------------------------- #

def test_chr_pos_columns_auto_detected_regardless_of_order(tmp_path):
    """CHR/POS are located BY HEADER NAME. A file whose columns are REORDERED
    (same header set, different order) must yield the identical present-rate — a
    positional read would silently score the wrong column."""
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    reordered = ["SNP_ID", "TRAIT", "POS", "BETA", "CHR", "SE", "P",
                 "REF", "ALT", "EAF", "N", "ANCESTRY", "BUILD"]

    f_std = _write_sumstats(tmp_path / "std.AFR.tsv", [_row(*v, "bmi")])
    f_reo = _write_sumstats(tmp_path / "reo.AFR.tsv", [_row(*v, "ldl")], columns=reordered)

    # sanity: the fixture really is reordered on disk
    assert f_reo.read_text().splitlines()[0].split("\t")[:2] == ["SNP_ID", "TRAIT"]

    res = prs.scan_present_rate([v], [f_std, f_reo])
    assert res[v]["n_traits_present"] == 2
    assert res[v]["present_rate"] == 1.0


def test_scan_multiple_variants_independently(tmp_path):
    """Several occluded variants scanned in one pass keep independent k/n."""
    import occlusion_present_rate_scan as prs

    a, b = (1, 5_982_776), (1, 5_982_778)
    f1 = _write_sumstats(tmp_path / "bmi.AFR.tsv", [_row(*a, "bmi"), _row(*b, "bmi")])
    f2 = _write_sumstats(tmp_path / "ldl.AFR.tsv", [_row(*a, "ldl")])

    res = prs.scan_present_rate([a, b], [f1, f2])

    assert res[a]["n_traits_present"] == 2
    assert res[b]["n_traits_present"] == 1
    assert res[b]["present_rate"] == pytest.approx(0.5)
