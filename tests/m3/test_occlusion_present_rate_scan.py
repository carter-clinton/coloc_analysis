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


def test_float_formatted_pos_counts_toward_k(tmp_path):
    """THE k/n UNDERCOUNT (D-04b-01). A float-formatted POS must count toward k.

    Two files carrying the SAME variant: one writes POS as ``5982778`` and the other
    as ``5982778.0`` — the exact shape 100% of ``bmi.AFR.PAGE.2019.GRCh37``'s
    17,195,956 rows carry (m3-04b-BLAST-RADIUS.md, D-04b-01). Today
    ``int('5982778.0')`` raises, ``occlusion_present_rate_scan.py:176-177`` swallows
    it, and the file scores ABSENT -> k=1 of 2 instead of 2 of 2.

    On the real corpus this is exactly why rs182965575 publishes 6 of 9 today when
    the project record — and the pre-registration (osf.io/az52u) — is 7 of 9.
    """
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    f_int = _write_sumstats(tmp_path / "asthma.AFR.tsv", [_row(*v, "asthma")])

    # POS written VERBATIM as a float string — str(int) can never produce this shape
    f_float = tmp_path / "bmi.AFR.PAGE.2019.GRCh37.tsv"
    f_float.write_text(
        "\t".join(_HARMONIZED_HEADER) + "\n"
        + "\t".join(str(x) for x in [
            1, "5982778.0", "A", "G", 0.012, 0.004, 3.1e-3, 0.21, 15000,
            "1:5982778:A:G", "bmi", "AFR", "GRCh37",
        ]) + "\n"
    )

    res = prs.scan_present_rate([v], [f_int, f_float])

    rec = res[v]
    assert rec["n_traits_present"] == 2, (
        "the float-POS file scores ABSENT today, undercounting k"
    )
    assert rec["n_traits_scanned"] == 2
    assert rec["present_rate"] == 1.0
    assert sorted(rec["traits_present"]) == ["asthma", "bmi"]


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


# --------------------------------------------------------------------------- #
# 4. HIGH-4 — a PARSE-HEALTH out-param, without touching the per-variant shape #
# --------------------------------------------------------------------------- #

def _write_raw(path: Path, header: list[str], body_lines: list[str]) -> Path:
    """Write a sumstats file with body lines VERBATIM (so a row can be malformed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\t".join(header) + "\n" + "".join(f"{ln}\n" for ln in body_lines))
    return path


def _raw_row(chrom, pos, trait="bmi") -> str:
    return "\t".join(str(x) for x in [
        chrom, pos, "A", "G", 0.012, 0.004, 3.1e-3, 0.21, 15000,
        f"{chrom}:{pos}:A:G", trait, "AFR", "GRCh37",
    ])


def test_stats_out_param_reports_parse_health(tmp_path):
    """``stats=`` is populated with the scan's PARSE HEALTH, and the per-variant
    return is left BYTE-IDENTICAL (still exactly the four contract keys).

    The four per-variant names are ``occlusion_manifest.STAGE_B_TRAIT_COLUMNS`` plus
    the rate and are fed to ``enrich_occlusion_manifest(present_rate=...)`` with NO
    adapter. Adding a fifth key there would break that contract, so the health
    numbers ride out through a separate out-param instead.
    """
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    good = _write_raw(tmp_path / "bmi.AFR.tsv", _HARMONIZED_HEADER,
                      [_raw_row(1, 5_982_778), _raw_row(1, 7_000_000)])
    messy = _write_raw(tmp_path / "ldl.AFR.tsv", _HARMONIZED_HEADER,
                       [_raw_row(1, 5_982_778, "ldl"),
                        _raw_row(1, "NA", "ldl"),          # unparseable coordinate
                        "1"])                              # truncated row
    stats: dict = {}

    res = prs.scan_present_rate([v], [good, messy], stats=stats)

    assert set(res[v]) == {"n_traits_present", "n_traits_scanned",
                           "present_rate", "traits_present"}, (
        "the per-variant record is a NO-ADAPTER contract — do not add a fifth key"
    )
    assert res[v]["n_traits_present"] == 2

    assert stats["n_files_scanned"] == 2
    assert stats["n_rows_seen"] == 5
    assert stats["n_rows_parsed"] == 3
    assert stats["n_unparseable"] == 1
    assert stats["n_truncated"] == 1
    assert stats["n_files_empty"] == 0
    assert stats["n_distinct_traits_scanned"] == 2
    assert stats["duplicate_traits"] == []
    assert len(stats["per_file"]) == 2
    assert {rec["trait"] for rec in stats["per_file"]} == {"bmi", "ldl"}


def test_scan_still_works_without_the_stats_kwarg(tmp_path):
    """``stats`` is kwarg-only and defaults to None — the shipped call signature is
    unchanged, so every existing caller keeps working untouched."""
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    f1 = _write_sumstats(tmp_path / "bmi.AFR.tsv", [_row(*v, "bmi")])

    res = prs.scan_present_rate([v], [f1])
    assert res[v]["n_traits_present"] == 1


# --------------------------------------------------------------------------- #
# 5. HIGH-0 — a guard that can ACTUALLY FIRE on a total parse failure          #
# --------------------------------------------------------------------------- #

def test_body_rows_but_nothing_parsed_RAISES(tmp_path):
    """A file with body rows and NOT ONE coercible coordinate is BROKEN, not empty.

    That is the unambiguous predicate the whole HIGH-0 finding turns on: ``n_rows_seen
    > 0 and n_rows_parsed == 0``. Today ``occlusion_present_rate_scan.py:176-177``
    swallows every failure and the file scores "nothing present", which is
    indistinguishable from a real, honest absence and silently mis-counts k.
    """
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    broken = _write_raw(tmp_path / "broken.AFR.tsv", _HARMONIZED_HEADER,
                        [_raw_row(1, "1e6"), _raw_row(1, "NA")])

    with pytest.raises(ValueError) as exc:
        prs.scan_present_rate([v], [broken])

    msg = str(exc.value)
    assert "broken.AFR.tsv" in msg      # names the file
    assert "1e6" in msg                 # names the first offending value


def test_header_only_and_zero_byte_files_do_not_raise(tmp_path):
    """A legitimately EMPTY scan stays legal. ``n_rows_seen == 0`` is not a failure —
    it is a file with nothing in it, and it increments ``n_files_empty``."""
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    header_only = _write_raw(tmp_path / "hdr.AFR.tsv", _HARMONIZED_HEADER, [])
    zero_byte = tmp_path / "zero.AFR.tsv"
    zero_byte.write_text("")
    stats: dict = {}

    res = prs.scan_present_rate([v], [header_only, zero_byte], stats=stats)

    assert res[v]["n_traits_present"] == 0
    assert res[v]["n_traits_scanned"] == 2
    assert stats["n_files_empty"] == 2
    assert stats["n_rows_seen"] == 0


def test_duplicate_trait_labels_are_REPORTED_without_moving_the_denominator(
        tmp_path, capsys):
    """LOW-1 — the ``stroke`` double-count is made VISIBLE, and NOTHING is redefined.

    The production glob resolves 9 FILES but only 8 DISTINCT TRAITS: both
    ``stroke.AFR`` and ``stroke.AFR.GIGASTROKE.2022.GRCh37`` report ``stroke``.

    The published denominator STAYS A FILE RATE. The project record and the
    pre-registration (osf.io/az52u) say "present in 7 of 9 AFR **sumstats**".
    Redefining it to distinct traits would MOVE a pre-registered number, which is
    Carter's call and not an executor's — so this is reported loudly and deferred, not
    silently corrected.
    """
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    f1 = _write_sumstats(tmp_path / "stroke.AFR.tsv", [_row(*v, "stroke")])
    f2 = _write_sumstats(tmp_path / "stroke.AFR.GIGASTROKE.2022.GRCh37.tsv",
                         [_row(*v, "stroke")])
    stats: dict = {}

    res = prs.scan_present_rate([v], [f1, f2], stats=stats)
    err = capsys.readouterr().err

    assert stats["n_files_scanned"] == 2
    assert stats["n_distinct_traits_scanned"] == 1
    assert stats["duplicate_traits"] == ["stroke"]
    assert "stroke" in err and "distinct" in err.lower(), (
        "the double-count must fire a LOUD note, not just sit in a dict"
    )

    # THE DENOMINATOR IS UNTOUCHED — it is a FILE rate, deliberately.
    assert res[v]["n_traits_scanned"] == 2
    assert res[v]["n_traits_present"] == 2
    assert res[v]["present_rate"] == 1.0


def test_blank_first_line_with_content_below_RAISES(tmp_path):
    """A file whose FIRST line is blank but which carries content below RAISES.

    Today ``occlusion_present_rate_scan.py:159`` ``continue``s on a blank header and
    scores the WHOLE file "nothing present" — mis-counting BOTH k (the variant is
    there and is missed) AND n (the file counts toward the denominator while
    contributing nothing). That is the worst of the swallow sites because it corrupts
    the published denominator, not just the numerator.
    """
    import occlusion_present_rate_scan as prs

    v = (1, 5_982_778)
    path = tmp_path / "leadingblank.AFR.tsv"
    path.write_text(
        "\n" + "\t".join(_HARMONIZED_HEADER) + "\n" + _raw_row(1, 5_982_778) + "\n"
    )

    with pytest.raises(ValueError) as exc:
        prs.scan_present_rate([v], [path])

    assert "leadingblank.AFR.tsv" in str(exc.value)
