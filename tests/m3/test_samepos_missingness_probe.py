"""RED-first tests for src/python/samepos_missingness_probe.py (quick-260831-kw8).

WHAT THE MODULE UNDER TEST MEASURES
------------------------------------
At a SAME-POSITION ``.bim`` site (two or more rows sharing ``(chrom, pos)``),
are the sibling rows CO-CALLED — the site is called implies BOTH rows are
called — or COMPLEMENTARY — a row's ALT carriers are MISSING at its sibling?

WHY IT MATTERS, AND WHY IT IS A MEASUREMENT AND NOT AN INFERENCE
-----------------------------------------------------------------
The posted occlusion predicate's left bound is STRICT (``d.pos < v.pos``), so
``v.pos == d.pos`` rows are invisible to it BY CONSTRUCTION. Same-position rows
are ~7-11% of rows in every region sampled. Whether that blind spot is REAL
depends on which way the sibling rows are called, and the only honest way to
settle it is to look at the bytes.

⚠ THE COMPETING INFERENCE IS NOT TESTABLE HERE. ``hl.split_multi_hts`` is
DOCUMENTED to downcode other-ALT carriers to REFERENCE (which would make the
class EMPTY) rather than to MISSING (which would make it REAL) — but Hail is
NOT INSTALLED on this node, so that cannot be verified here. These tests pin
the INSTRUMENT on synthetic ``.bed`` bytes with KNOWN answers; they establish
nothing about the cohort.

WHAT THIS FILE DOES NOT ESTABLISH
----------------------------------
No prevalence. No claim about the real panel. The probe is NOT run against any
real ``.bed`` by this file, and both labels are demonstrated ALONGSIDE the
``mixed`` negative control so neither can be returned unconditionally.

RED-for-the-right-reason: the module under test is imported INSIDE each test
body, never at module top, so pytest COLLECTS this file cleanly and a missing
module fails as a test failure rather than a collection error. This mirrors
``tests/m3/test_pairwise_completeness_scan.py``.

Runs in smoke_dev py3.11 (stdlib + numpy). No Hail, no plink, no network.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level import of the module under test -- see the docstring.

# plink1 .bed 2-bit codes (the byte contract under test)
# 00 = hom-A1 (dosage 2) | 01 = MISSING | 10 = het (dosage 1) | 11 = hom-A2 (0)
_HOM_A1 = 0b00
_MISSING = 0b01
_HET = 0b10
_HOM_A2 = 0b11


def _pack_variant(codes, n_samples: int) -> bytes:
    """Pack ``n_samples`` 2-bit codes into a variant block, LOW-to-HIGH."""
    out = bytearray((n_samples + 3) // 4)
    for byte_i in range(len(out)):
        packed = 0
        for slot in range(4):
            s = byte_i * 4 + slot
            packed |= ((codes[s] if s < n_samples else 0b00) & 0b11) << (2 * slot)
        out[byte_i] = packed
    return bytes(out)


def _write_bfile(tmp_path: Path, *, codes_per_variant, bim_rows, prefix="probe") -> Path:
    """Write a synthetic plink1 .bed/.bim/.fam trio; return the prefix path."""
    base = tmp_path / prefix
    n_samples = len(codes_per_variant[0])
    blob = bytearray(b"\x6c\x1b\x01")
    for codes in codes_per_variant:
        assert len(codes) == n_samples
        blob.extend(_pack_variant(codes, n_samples))
    base.with_suffix(".bed").write_bytes(bytes(blob))
    base.with_suffix(".bim").write_text(
        "".join("\t".join(str(f) for f in r) + "\n" for r in bim_rows)
    )
    base.with_suffix(".fam").write_text(
        "".join(f"F{i}\tI{i}\t0\t0\t0\t-9\n" for i in range(n_samples))
    )
    return base


def _row(pos: int, alt: str, ref: str = "T", chrom="1") -> list:
    """A .bim row: [chr, vid, cm, bp, A1=ALT, A2=REF]."""
    return [str(chrom), f"{chrom}:{pos}:{ref}:{alt}", "0", str(pos), alt, ref]


def _regions_tsv(tmp_path: Path, specs, name="regions.tsv") -> Path:
    """A config/ld_regions.tsv-shaped manifest carrying the ancestry column."""
    path = tmp_path / name
    header = ["c%d" % i for i in range(1, 17)]
    header[0], header[1], header[6] = "region_id", "chr", "ancestry"
    header[14], header[15] = "window_start_grch38", "window_end_grch38"
    rows = [header]
    for rid, chrom, start, end, anc in specs:
        r = ["."] * 16
        r[0], r[1], r[6] = rid, chrom, anc
        r[14], r[15] = str(start), str(end)
        rows.append(r)
    path.write_text("".join("\t".join(x) + "\n" for x in rows))
    return path


def _run(tmp_path, codes_per_variant, bim_rows, *, prefix="probe", extra=None,
         start=900, end=1100):
    """Build a trio + manifest, run main(), return (records, summary)."""
    import samepos_missingness_probe as S

    base = _write_bfile(tmp_path, codes_per_variant=codes_per_variant,
                        bim_rows=bim_rows, prefix=prefix)
    regions = _regions_tsv(tmp_path, [("r1", "1", start, end, "AFR")],
                           name=f"{prefix}_regions.tsv")
    out = tmp_path / f"{prefix}_pairs.tsv"
    summary = tmp_path / f"{prefix}_summary.json"
    argv = ["--bfile-prefix", str(base), "--regions-tsv", str(regions),
            "--out", str(out), "--summary", str(summary)]
    argv += list(extra or [])
    rc = S.main(argv)
    assert rc == 0, f"main() returned {rc}"
    return out.read_text(), json.loads(summary.read_text())


def _records(out_text):
    lines = [ln for ln in out_text.splitlines() if ln.strip()]
    header = lines[0].split("\t")
    return [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]


# --------------------------------------------------------------------------- #
# THE TWO KNOWN ANSWERS, AND THE NEGATIVE CONTROL THAT SEPARATES THEM          #
# --------------------------------------------------------------------------- #

def test_co_called_signature_when_both_rows_are_called_in_every_sample(tmp_path):
    """Site called => BOTH rows called. Nothing is stripped by intersecting."""
    n = 8
    a = [_HOM_A1, _HET] + [_HOM_A2] * 6          # carriers at samples 0,1
    b = [_HOM_A2, _HOM_A2, _HOM_A1, _HET] + [_HOM_A2] * 4   # ALL called
    out, summary = _run(tmp_path, [a, b], [_row(1000, "C"), _row(1000, "G")])

    recs = _records(out)
    assert len(recs) == 2, "one record per ORDERED within-group pair"
    fwd = next(r for r in recs if r["a_vid"].endswith(":C"))
    assert float(fwd["frac_carriers_a_missing_at_b"]) == 0.0
    assert int(fwd["n_both"]) == int(fwd["n_called_a"]) == int(fwd["n_called_b"]) == n
    assert fwd["label"] == "co_called"
    assert summary["pooled"]["label_counts"]["co_called"] == 2


def test_complementary_signature_when_each_rows_alt_carriers_are_missing_at_the_sibling(tmp_path):
    """A row's ALT carriers are MISSING at its sibling -> the class is REAL."""
    a = [_HOM_A1, _HET] + [_HOM_A2] * 6           # carriers at 0,1
    b = [_MISSING, _MISSING, _HOM_A1, _HET] + [_HOM_A2] * 4   # missing exactly there
    out, summary = _run(tmp_path, [a, b], [_row(1000, "C"), _row(1000, "G")])

    recs = _records(out)
    fwd = next(r for r in recs if r["a_vid"].endswith(":C"))
    assert float(fwd["frac_carriers_a_missing_at_b"]) == 1.0
    assert int(fwd["n_both"]) < int(fwd["n_called_a"])
    assert fwd["label"] == "complementary"
    # on the both-called subset a is HOM_A2 everywhere -> invariant -> UNDEFINED
    assert fwd["a_invariant_on_both"] == "True"
    assert fwd["undefined"] == "True"
    assert summary["pooled"]["n_undefined_pairs"] >= 1
    assert any("1:1000:T:C" in v for v in summary["pooled"]["undefined_pair_vids"])


def test_the_mixed_case_is_labelled_mixed_and_not_forced_into_either_bucket(tmp_path):
    """NEGATIVE CONTROL: an intermediate fraction gets NEITHER label.

    Without this, the two greens above are consistent with a function that
    returns a constant (`feedback_green_assertion_needs_a_negative_control`).
    """
    a = [_HOM_A1, _HET, _HET, _HET] + [_HOM_A2] * 4        # 4 carriers
    b = [_MISSING, _MISSING, _HOM_A1, _HET] + [_HOM_A2] * 4  # 2 of 4 missing
    out, _summary = _run(tmp_path, [a, b], [_row(1000, "C"), _row(1000, "G")])

    fwd = next(r for r in _records(out) if r["a_vid"].endswith(":C"))
    assert float(fwd["frac_carriers_a_missing_at_b"]) == 0.5
    assert fwd["label"] == "mixed"


def test_labels_describe_the_measurement_not_the_mechanism():
    """The vocabulary is EXACTLY three neutral words. No label names a cause."""
    import samepos_missingness_probe as S

    assert set(S.LABELS) == {"co_called", "complementary", "mixed"}
    joined = " ".join(S.LABELS).lower()
    for banned in ("split", "hail", "downcode", "reference", "multi",
                   "empty", "real", "blind"):
        assert banned not in joined, f"a LABEL names a mechanism/conclusion: {banned}"
    # the thresholds are NAMED CONSTANTS documented as reporting bins
    assert 0.0 <= S.CO_CALLED_MAX_FRAC < S.COMPLEMENTARY_MIN_FRAC <= 1.0


def test_single_row_sites_are_not_measured_and_are_not_counted_as_same_position(tmp_path):
    """Multiplicity 1 contributes NOTHING -- no record, no site, no label."""
    a = [_HOM_A1, _HET] + [_HOM_A2] * 6
    b = [_HOM_A2] * 4 + [_HET] * 4
    out, summary = _run(tmp_path, [a, b], [_row(1000, "C"), _row(1020, "G")])

    assert _records(out) == []
    assert summary["pooled"]["n_sites_total"] == 0
    assert summary["pooled"]["n_sites_measured"] == 0
    assert summary["pooled"]["n_pairs"] == 0


def test_the_sample_is_deterministic_and_the_census_is_reported_beside_it(tmp_path):
    """Two runs byte-identical; a CAPPED run reports what it did NOT look at.

    A sample must never be readable as a census
    (`feedback_skip_guard_masks_not_fixes`): the skip counters are EMITTED, not
    silent.
    """
    # two same-position sites (1000 x2, 1050 x2) + one 3-row site at 1080
    codes = [
        [_HOM_A1, _HET] + [_HOM_A2] * 6,
        [_HOM_A2] * 8,
        [_HOM_A1, _HET] + [_HOM_A2] * 6,
        [_HOM_A2] * 8,
        [_HOM_A1] + [_HOM_A2] * 7,
        [_HET] + [_HOM_A2] * 7,
        [_HOM_A2] * 8,
    ]
    rows = [_row(1000, "C"), _row(1000, "G"), _row(1050, "C"), _row(1050, "G"),
            _row(1080, "C"), _row(1080, "G"), _row(1080, "A")]

    out1, s1 = _run(tmp_path, codes, rows, prefix="d1",
                    extra=["--max-sites-per-region", "1", "--max-multiplicity", "2"])
    out2, s2 = _run(tmp_path, codes, rows, prefix="d2",
                    extra=["--max-sites-per-region", "1", "--max-multiplicity", "2"])
    assert out1 == out2, "the per-pair TSV is not deterministic"
    assert json.dumps(s1["pooled"], sort_keys=True) == json.dumps(s2["pooled"], sort_keys=True)

    pooled = s1["pooled"]
    assert pooled["n_sites_total"] == 2, "the 3-row site is over the cap, not a site"
    assert pooled["n_sites_measured"] == 1
    assert pooled["n_sites_total"] != pooled["n_sites_measured"]
    assert pooled["n_groups_skipped_over_max_multiplicity"] == 1
    assert pooled["n_sites_skipped_over_max_sites_per_region"] == 1


def test_the_summary_carries_no_per_sample_data(tmp_path):
    """EGRESS: aggregate counts, fractions, bins and variant ids ONLY."""
    n_samples = 8
    a = [_HOM_A1, _HET] + [_HOM_A2] * 6
    b = [_MISSING, _MISSING, _HOM_A1, _HET] + [_HOM_A2] * 4
    _out, summary = _run(tmp_path, [a, b], [_row(1000, "C"), _row(1000, "G")])

    def walk(node, path="summary"):
        if isinstance(node, dict):
            for k, v in node.items():
                assert isinstance(k, str), f"{path}: non-str key"
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            assert len(node) < n_samples, f"{path}: list of length {len(node)} >= n_samples"
            for i, v in enumerate(node):
                assert isinstance(v, str), f"{path}[{i}]: a list leaf must be a str id"
        else:
            assert isinstance(node, (int, float, str, bool)) or node is None, (
                f"{path}: leaf of type {type(node).__name__}"
            )

    walk(summary)
    flat = json.dumps(summary)
    for banned in ("dosage", "sample_id", "IID", "FID"):
        assert banned not in flat, f"per-sample surface in the summary: {banned}"


def test_the_bed_reader_is_the_scanners_own():
    """ONE .bed byte contract, ONE implementation -- function/class IDENTITY."""
    import samepos_missingness_probe as S
    import pairwise_completeness_scan as P

    assert S.BedReader is P.BedReader, "a SECOND .bed reader was written"
    assert S.iter_bim_windows is P.iter_bim_windows
    assert S._read_regions_tsv is P._read_regions_tsv


def test_the_parser_is_the_declared_cross_task_contract():
    """``_build_parser`` is DECLARED, not incidental: the staged doc is fed to it."""
    import argparse
    import samepos_missingness_probe as S

    parser = S._build_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    ns = parser.parse_args(["--bfile-prefix", "/x/y", "--regions-tsv", "/x/r.tsv",
                            "--out", "/x/o.tsv", "--summary", "/x/s.json"])
    assert ns.ancestry == "AFR", "DEFAULT_ANCESTRY must be the scanner's default"
    assert ns.max_multiplicity == S.DEFAULT_MAX_MULTIPLICITY
    assert ns.max_sites_per_region == S.DEFAULT_MAX_SITES_PER_REGION
    with pytest.raises(SystemExit):
        parser.parse_args(["--bfile-prefix"])


def test_an_empty_region_ids_value_is_an_error_not_a_full_scan(tmp_path):
    """Matching the scanner's ruling: an empty --region-ids must never widen."""
    import samepos_missingness_probe as S

    a = [_HOM_A1, _HET] + [_HOM_A2] * 6
    base = _write_bfile(tmp_path, codes_per_variant=[a, [_HOM_A2] * 8],
                        bim_rows=[_row(1000, "C"), _row(1000, "G")], prefix="e1")
    regions = _regions_tsv(tmp_path, [("r1", "1", 900, 1100, "AFR")])
    with pytest.raises(ValueError) as exc:
        S.main(["--bfile-prefix", str(base), "--regions-tsv", str(regions),
                "--region-ids", "  ", "--out", str(tmp_path / "o.tsv"),
                "--summary", str(tmp_path / "s.json")])
    assert "region-ids" in str(exc.value)


def test_the_probe_docstring_labels_the_hail_claim_an_unverified_inference():
    """The inference sits BESIDE the measurement and is never mistaken for it."""
    import ast

    p = PROJECT_ROOT / "src" / "python" / "samepos_missingness_probe.py"
    doc = ast.get_docstring(ast.parse(p.read_text(encoding="utf-8"))) or ""
    flat = " ".join(doc.split())   # NORMALISE: a ~79-char wrap would false-negative
    for needle in ("INFERENCE", "not installed", "split_multi_hts",
                   "never a number to adjust", "co_called", "complementary"):
        assert needle in flat, f"MISSING FROM THE DOCSTRING: {needle}"
    # the DECISION RULE must be stated BEFORE any run
    assert "EMPTY" in flat and "REAL" in flat
