"""RED-first tests for src/python/pairwise_completeness_scan.py (quick-260825-ngh).

WHAT THE MODULE UNDER TEST MEASURES
-----------------------------------
For a pair ``(X, Y)``, plink's ``r`` is UNDEFINED iff, within
``called(X) ∩ called(Y)``, ``X`` is constant or ``Y`` is constant (the empty
intersection included as the degenerate true case). ``carriers(X) ⊆ missing(Y)``
is ONE SUFFICIENT SPECIAL CASE of that condition and is NEVER the test — it
appears only as the derived ``confounding_pattern`` label. Tests in this file
pin that distinction directly
(:func:`test_undefined_without_carriers_subset_of_missing`).

WHY IT EXISTS
-------------
``.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md``
§MECHANISM CONFIRMED. That record is the PROVENANCE for the numbers this file
mirrors; nothing here re-derives them.

WHAT THIS FILE DOES NOT ESTABLISH
---------------------------------
No prevalence, no boundary width, no partial-confounding tail size. Those are
OPEN and are settled ONLY by running the instrument in-perimeter over the
pre-committed sample. n=1 supplies none of them.

RED-for-the-right-reason: ``pairwise_completeness_scan`` is imported INSIDE each
test body, NOT at module top, so pytest COLLECTS this file cleanly and every test
fails as a test/assert failure (``ModuleNotFoundError`` raised at call time)
rather than as a collection error. This mirrors
``tests/m3/test_occlusion_span_filter.py``.

Runs in smoke_dev py3.11 (stdlib + numpy). No Hail, no plink, no perimeter.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import pairwise_completeness_scan`` — see the docstring.


# --------------------------------------------------------------------------- #
# plink1 .bed 2-bit codes (the byte contract under test)                       #
# --------------------------------------------------------------------------- #
# 00 = hom-A1 (dosage 2) · 01 = MISSING · 10 = het (dosage 1) · 11 = hom-A2 (0)
_CODE_HOM_A1 = 0b00
_CODE_MISSING = 0b01
_CODE_HET = 0b10
_CODE_HOM_A2 = 0b11

#: ``--recode A`` dosage string -> the .bed 2-bit code that encodes it.
#: A1 == ALT, so an ALT-dosage of 0 is hom-REF == hom-A2 == 0b11.
_DOSAGE_STR_TO_CODE = {
    "0": _CODE_HOM_A2,
    "1": _CODE_HET,
    "2": _CODE_HOM_A1,
    "NA": _CODE_MISSING,
}


# --------------------------------------------------------------------------- #
# .bim row helpers (shape mirrored from tests/m3/test_occlusion_span_filter.py) #
# --------------------------------------------------------------------------- #

def _ref_seq(n: int, anchor: str = "G") -> str:
    """A deterministic n-char REF string, left-anchored on ``anchor``."""
    filler = "ACGT" * ((n // 4) + 1)
    return (anchor + filler)[:n]


def _del_row(bp: int, ref_len: int, chrom: str | int = 1) -> list[str]:
    """A DELETION .bim row whose REF (A2) spans exactly ``ref_len`` bases."""
    assert ref_len > 1, "a deletion must have len(REF) > 1"
    ref = _ref_seq(ref_len)
    alt = ref[0]  # left-anchored: ALT is the single anchor base
    return [str(chrom), f"{chrom}:{bp}:{ref}:{alt}", "0", str(bp), alt, ref]


def _snp_row(bp: int, ref: str = "T", alt: str = "C", chrom: str | int = 1) -> list[str]:
    """A ``len(REF) == 1`` .bim row (never an occluder, never an anchor)."""
    return [str(chrom), f"{chrom}:{bp}:{ref}:{alt}", "0", str(bp), alt, ref]


def _ins_row(bp: int, ins_len: int, chrom: str | int = 1) -> list[str]:
    """An INSERTION row: len(ALT) > len(REF), REF = a single anchor base."""
    ref = "G"
    alt = _ref_seq(ins_len + 1, anchor="G")
    return [str(chrom), f"{chrom}:{bp}:{ref}:{alt}", "0", str(bp), alt, ref]


# --------------------------------------------------------------------------- #
# The bfile fixture builder — everything downstream stands on this            #
# --------------------------------------------------------------------------- #

def _pack_variant(codes, n_samples: int, pad_bits: int = 0b00) -> bytes:
    """Pack ``n_samples`` 2-bit codes into a variant block, LOW-to-HIGH.

    The sample with the LOWEST index occupies bits 0-1 of the first byte. Unused
    trailing bit-pairs of the last byte are filled with ``pad_bits`` — the knob
    that lets a test prove padding cannot manufacture a phantom sample.
    """
    bytes_per_variant = (n_samples + 3) // 4
    out = bytearray(bytes_per_variant)
    for byte_i in range(bytes_per_variant):
        packed = 0
        for slot in range(4):
            s = byte_i * 4 + slot
            code = codes[s] if s < n_samples else pad_bits
            packed |= (code & 0b11) << (2 * slot)
        out[byte_i] = packed
    return bytes(out)


def _write_bfile(
    tmp_path: Path,
    *,
    codes_per_variant,
    n_samples: int,
    mode: int = 0x01,
    magic: bytes = b"\x6c\x1b",
    pad_bits: int = 0b00,
    bim_rows=None,
    truncate_bytes: int = 0,
    extra_bytes: int = 0,
    prefix: str = "fixture",
    n_fam_lines: int | None = None,
) -> Path:
    """Write a synthetic plink1 ``.bed``/``.bim``/``.fam`` trio; return the prefix.

    Every structural knob a fail-closed reader must reject is exposed:
    ``magic``, ``mode``, ``truncate_bytes``, ``extra_bytes``, a ``bim_rows`` list
    whose length may disagree with ``codes_per_variant``, and ``n_fam_lines``.
    """
    base = tmp_path / prefix
    n_variants = len(codes_per_variant)

    blob = bytearray(magic)
    blob.append(mode & 0xFF)
    for codes in codes_per_variant:
        assert len(codes) == n_samples, "each variant needs one code per sample"
        blob.extend(_pack_variant(codes, n_samples, pad_bits=pad_bits))
    if truncate_bytes:
        del blob[len(blob) - truncate_bytes:]
    if extra_bytes:
        blob.extend(b"\x00" * extra_bytes)
    base.with_suffix(".bed").write_bytes(bytes(blob))

    if bim_rows is None:
        bim_rows = [_snp_row(1000 + 10 * i) for i in range(n_variants)]
    base.with_suffix(".bim").write_text(
        "".join("\t".join(str(f) for f in row) + "\n" for row in bim_rows)
    )

    fam_n = n_samples if n_fam_lines is None else n_fam_lines
    base.with_suffix(".fam").write_text(
        "".join(f"F{i}\tI{i}\t0\t0\t0\t-9\n" for i in range(fam_n))
    )
    return base


def _distinguishable_codes(i: int, n_samples: int) -> list[int]:
    """Codes for variant ``i`` that differ from every other variant's (i < 64)."""
    codes = [_CODE_HOM_A1] * n_samples
    codes[0] = i % 4
    if n_samples > 1:
        codes[1] = (i // 4) % 4
    if n_samples > 2:
        codes[2] = (i // 16) % 4
    return codes


# --------------------------------------------------------------------------- #
# The frozen import surface — the constants are NEVER re-declared here         #
# --------------------------------------------------------------------------- #

def test_frozen_bim_symbols_are_imported_not_forked():
    """``parse_bim_row`` / ``load_bim_rows`` must be the SAME objects, not copies.

    Object identity on FUNCTIONS is a DISCRIMINATING check: functions are never
    interned across modules, so a forked copy genuinely fails this.

    ⚠ Do NOT "strengthen" this with ``pcs._COL_REF is osf._COL_REF``. CPython
    interns small ints (-5..256), so two INDEPENDENTLY declared ``_COL_REF = 5``
    also satisfy ``is`` — a FALSE INVARIANT that passes on a fork (verified
    empirically 2026-08-25). The authoritative enforcer for the CONSTANTS is the
    textual guard in :func:`test_module_declares_no_bim_column_indices_of_its_own`.
    """
    import occlusion_span_filter as osf
    import pairwise_completeness_scan as pcs

    assert pcs.parse_bim_row is osf.parse_bim_row
    assert pcs.load_bim_rows is osf.load_bim_rows
    # The constants must at least carry the frozen VALUES.
    assert (pcs._COL_CHR, pcs._COL_ID, pcs._COL_BP, pcs._COL_ALT, pcs._COL_REF) == (
        osf._COL_CHR, osf._COL_ID, osf._COL_BP, osf._COL_ALT, osf._COL_REF,
    )


def test_module_declares_no_bim_column_indices_of_its_own():
    """The TEXTUAL guard: zero ``_COL_* =`` assignments in the scanner's source.

    This is the named enforcer for "the constants are imported, never forked"
    (``feedback_a_claimed_invariant_needs_a_named_enforcer``). It reads the source
    at call time rather than trusting an import-time object graph.
    """
    import re

    src = (_SRC_PYTHON / "pairwise_completeness_scan.py").read_text()
    assignments = re.findall(
        r"^\s*(_COL_CHR|_COL_ID|_COL_BP|_COL_ALT|_COL_REF)\s*=", src, flags=re.M
    )
    assert assignments == [], f"forked .bim column index declarations: {assignments}"
    assert "occlusion_span_filter" in src


# --------------------------------------------------------------------------- #
# The .bed decoder                                                             #
# --------------------------------------------------------------------------- #

def test_all_four_two_bit_codes_decode_to_expected_dosages(tmp_path):
    """00 -> 2, 01 -> MISSING, 10 -> 1, 11 -> 0; ``called`` False only at 01."""
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path,
        codes_per_variant=[[_CODE_HOM_A1, _CODE_MISSING, _CODE_HET, _CODE_HOM_A2]],
        n_samples=4,
    )
    reader = pcs.BedReader(base)
    try:
        geno = reader.read_variant(0)
        assert geno.dosage.tolist() == [2, pcs.MISSING_DOSAGE, 1, 0]
        assert geno.dosage.dtype == np.int8
        assert geno.called.tolist() == [True, False, True, True]
    finally:
        reader.close()


def test_packing_is_low_to_high_within_a_byte(tmp_path):
    """A byte whose bit-pairs are 00,01,10,11 LOW-to-HIGH -> [2, MISSING, 1, 0].

    Seen RED against a high-to-low implementation (perturbation P1), which
    returns the reversed order [0, 1, MISSING, 2].
    """
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path,
        codes_per_variant=[[_CODE_HOM_A1, _CODE_MISSING, _CODE_HET, _CODE_HOM_A2]],
        n_samples=4,
    )
    raw = base.with_suffix(".bed").read_bytes()
    # 11 10 01 00 read high-to-low == 0b11100100 == 0xE4
    assert raw[3] == 0b11100100, "the fixture itself must pack low-to-high"

    reader = pcs.BedReader(base)
    try:
        assert reader.read_variant(0).dosage.tolist() == [2, pcs.MISSING_DOSAGE, 1, 0]
    finally:
        reader.close()


def test_n_samples_multiple_of_four_decodes_exact_length(tmp_path):
    """``n_samples % 4 == 0``: exactly ``n_samples`` values, no truncation surprise."""
    import pairwise_completeness_scan as pcs

    codes = [_CODE_HOM_A1, _CODE_MISSING, _CODE_HET, _CODE_HOM_A2] * 2
    base = _write_bfile(tmp_path, codes_per_variant=[codes], n_samples=8)
    reader = pcs.BedReader(base)
    try:
        assert reader.bytes_per_variant == 2
        assert reader.n_samples == 8
        geno = reader.read_variant(0)
        assert len(geno.dosage) == 8
        assert geno.dosage.tolist() == [2, pcs.MISSING_DOSAGE, 1, 0] * 2
    finally:
        reader.close()


@pytest.mark.parametrize("n_samples", [5, 7])
def test_padding_bits_cannot_manufacture_a_phantom_sample(tmp_path, n_samples):
    """Two fixtures differing ONLY in trailing padding bits decode BYTE-IDENTICALLY.

    A must-be-identity comparison (``np.array_equal``), not a tolerance. A
    reshape-without-truncate implementation (perturbation P3) lengthens the array
    and decodes ``pad_bits=0b11`` as a phantom dosage-0 sample — exactly the red
    this test exists to observe.
    """
    import pairwise_completeness_scan as pcs

    codes = [(_CODE_HOM_A1, _CODE_HET, _CODE_HOM_A2, _CODE_MISSING)[i % 4]
             for i in range(n_samples)]
    base0 = _write_bfile(
        tmp_path, codes_per_variant=[codes], n_samples=n_samples,
        pad_bits=0b00, prefix=f"pad00_{n_samples}",
    )
    base3 = _write_bfile(
        tmp_path, codes_per_variant=[codes], n_samples=n_samples,
        pad_bits=0b11, prefix=f"pad11_{n_samples}",
    )
    # The two .bed files really do differ in their padding bits.
    assert base0.with_suffix(".bed").read_bytes() != base3.with_suffix(".bed").read_bytes()

    r0 = pcs.BedReader(base0)
    r3 = pcs.BedReader(base3)
    try:
        a = r0.read_variant(0).dosage
        b = r3.read_variant(0).dosage
        assert len(a) == n_samples
        assert len(b) == n_samples
        assert np.array_equal(a, b)
    finally:
        r0.close()
        r3.close()


def test_seek_by_index_returns_the_right_block(tmp_path):
    """variant 0 all hom-A1, 1 all het, 2 all hom-A2 -> all-2 / all-1 / all-0.

    Seen RED against a perturbed offset ``3 + i*(bpv+1)`` (P2) and against a
    reader hardcoded to always seek block 0 (P4).
    """
    import pairwise_completeness_scan as pcs

    n = 6
    base = _write_bfile(
        tmp_path,
        codes_per_variant=[
            [_CODE_HOM_A1] * n,
            [_CODE_HET] * n,
            [_CODE_HOM_A2] * n,
        ],
        n_samples=n,
    )
    reader = pcs.BedReader(base)
    try:
        assert reader.n_variants == 3
        assert reader.read_variant(0).dosage.tolist() == [2] * n
        assert reader.read_variant(1).dosage.tolist() == [1] * n
        assert reader.read_variant(2).dosage.tolist() == [0] * n
    finally:
        reader.close()


def test_bad_magic_raises(tmp_path):
    """RAISE 1 — bad magic bytes; the message names the observed bytes."""
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4], n_samples=4,
        magic=b"\x00\x00",
    )
    with pytest.raises(ValueError) as exc:
        pcs.BedReader(base)
    msg = str(exc.value)
    assert "magic" in msg.lower()
    assert "00" in msg  # the observed bytes are quoted back


def test_individual_major_mode_raises(tmp_path):
    """RAISE 2 — individual-major mode byte 0x00 must RAISE, never be decoded.

    A silent mode mistake transposes the whole matrix and corrupts every
    downstream number, so this may not be a warning.
    """
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4], n_samples=4, mode=0x00,
    )
    with pytest.raises(ValueError) as exc:
        pcs.BedReader(base)
    msg = str(exc.value)
    assert "mode" in msg.lower()
    assert "individual" in msg.lower()


def test_truncated_bed_raises(tmp_path):
    """RAISE 3a — a file one byte short of ``3 + n_variants*bpv`` RAISES."""
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4] * 3, n_samples=4,
        truncate_bytes=1,
    )
    with pytest.raises(ValueError) as exc:
        pcs.BedReader(base)
    msg = str(exc.value)
    assert "size" in msg.lower()
    assert "6" in msg and "5" in msg  # expected 3 + 3*1 = 6, actual 5


def test_over_long_bed_raises(tmp_path):
    """RAISE 3b — an OVER-LONG file RAISES too. The size check is ``==``, not ``>=``."""
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4] * 3, n_samples=4,
        extra_bytes=1,
    )
    with pytest.raises(ValueError) as exc:
        pcs.BedReader(base)
    assert "size" in str(exc.value).lower()


def test_bim_line_count_mismatch_raises(tmp_path):
    """RAISE 4 — a ``.bim`` carrying one extra row makes the bfile LOUD.

    The ``.bim`` line count is what defines ``n_variants``; if it disagrees with
    the ``.bed`` size, seek-by-index would silently address the wrong blocks past
    some point. Fail closed.
    """
    import pairwise_completeness_scan as pcs

    rows = [_snp_row(1000 + 10 * i) for i in range(4)]  # 4 rows for 3 blocks
    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4] * 3, n_samples=4,
        bim_rows=rows,
    )
    with pytest.raises(ValueError) as exc:
        pcs.BedReader(base)
    msg = str(exc.value)
    assert "size" in msg.lower()
    assert ".bim" in msg


def test_fam_line_count_mismatch_raises(tmp_path):
    """A ``.fam`` disagreeing with the ``.bed`` size RAISES (bytes_per_variant moves)."""
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4] * 3, n_samples=4,
        n_fam_lines=9,  # bpv would become 3, not 1
    )
    with pytest.raises(ValueError) as exc:
        pcs.BedReader(base)
    assert "size" in str(exc.value).lower()


@pytest.mark.parametrize("bad_index", [-1, 3, 99])
def test_out_of_range_index_raises(tmp_path, bad_index):
    """An out-of-range variant index RAISES — never a silent read of other bytes."""
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4] * 3, n_samples=4,
    )
    reader = pcs.BedReader(base)
    try:
        with pytest.raises((IndexError, ValueError)):
            reader.read_variant(bad_index)
    finally:
        reader.close()


@pytest.mark.parametrize("missing_suffix", [".bed", ".bim", ".fam"])
def test_missing_bfile_component_raises(tmp_path, missing_suffix):
    """A missing ``.bed``/``.bim``/``.fam`` RAISES and names the missing path."""
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path, codes_per_variant=[[_CODE_HOM_A1] * 4], n_samples=4,
    )
    base.with_suffix(missing_suffix).unlink()
    with pytest.raises(FileNotFoundError) as exc:
        pcs.BedReader(base)
    assert missing_suffix in str(exc.value)


def test_window_relative_index_reads_the_wrong_block(tmp_path):
    """DOCUMENTATION TEST — why the scanner refuses a loose window ``.bim``.

    A pre-extracted window ``.bim`` carries WINDOW-RELATIVE row indices. Handing
    one of those to a GLOBAL reader silently returns a DIFFERENT variant's
    genotypes, with no error anywhere. This test demonstrates that exact
    corruption so the module's global-index rule has a named reason.
    """
    import pairwise_completeness_scan as pcs

    n = 8
    base = _write_bfile(
        tmp_path,
        codes_per_variant=[_distinguishable_codes(i, n) for i in range(6)],
        n_samples=n,
    )
    reader = pcs.BedReader(base)
    try:
        # The window's row 0 is the bfile's GLOBAL row 5.
        as_window_relative = reader.read_variant(0)
        as_global = reader.read_variant(5)
        assert not np.array_equal(as_window_relative.dosage, as_global.dosage), (
            "fixture must make the two blocks distinguishable"
        )
        # Every one of the six blocks is mutually distinguishable, so ANY index
        # confusion is a wrong-genotype read, not a benign no-op.
        seen = {tuple(reader.read_variant(i).dosage.tolist()) for i in range(6)}
        assert len(seen) == 6
    finally:
        reader.close()


def test_reader_does_not_slurp_the_bed(tmp_path):
    """Structural bound: no attribute holds the whole file or the whole matrix.

    The production ``.bed`` is ~354 GB. ``feedback_dense_matrix_verify_memory_bounded``:
    never let a verify materialize unboundedly.
    """
    import pairwise_completeness_scan as pcs

    n_samples, n_variants = 1000, 50
    base = _write_bfile(
        tmp_path,
        codes_per_variant=[[_CODE_HET] * n_samples for _ in range(n_variants)],
        n_samples=n_samples,
    )
    bed_size = base.with_suffix(".bed").stat().st_size
    assert bed_size == 3 + n_variants * ((n_samples + 3) // 4)

    reader = pcs.BedReader(base)
    try:
        reader.read_variant(0)
        reader.read_variant(7)

        def _sized_values(obj):
            for value in vars(obj).values():
                yield value
                if isinstance(value, dict):
                    yield from value.values()

        for value in _sized_values(reader):
            if isinstance(value, np.ndarray):
                assert value.size < n_variants * n_samples, (
                    f"reader materialized a {value.size}-element array"
                )
            elif isinstance(value, (bytes, bytearray, memoryview)):
                assert len(value) < bed_size, "reader slurped the whole .bed"
    finally:
        reader.close()


def test_decode_cache_is_bounded_and_evicts(tmp_path):
    """The LRU decode cache never grows past ``cache_variants`` entries.

    The memory bound is ``cache_variants * n_samples`` bytes (int8 dosage only;
    ``called`` is derived on access) — ~150 MB at the production default.
    """
    import pairwise_completeness_scan as pcs

    n = 8
    base = _write_bfile(
        tmp_path,
        codes_per_variant=[_distinguishable_codes(i, n) for i in range(6)],
        n_samples=n,
    )
    reader = pcs.BedReader(base, cache_variants=2)
    try:
        for i in range(6):
            reader.read_variant(i)
            assert len(reader._cache) <= 2
        assert len(reader._cache) == 2
        assert list(reader._cache.keys()) == [4, 5]  # LRU kept the two most recent
    finally:
        reader.close()


def test_cache_variants_one_is_still_correct(tmp_path):
    """A memory knob must not be a correctness knob, even at ``cache_variants=1``."""
    import pairwise_completeness_scan as pcs

    n = 8
    base = _write_bfile(
        tmp_path,
        codes_per_variant=[_distinguishable_codes(i, n) for i in range(6)],
        n_samples=n,
    )
    big = pcs.BedReader(base, cache_variants=64)
    small = pcs.BedReader(base, cache_variants=1)
    try:
        for i in [0, 1, 0, 1, 2, 0, 5, 4, 5]:
            assert np.array_equal(
                small.read_variant(i).dosage, big.read_variant(i).dosage
            )
    finally:
        big.close()
        small.close()


def test_missing_dosage_sentinel_and_called_property(tmp_path):
    """``MISSING_DOSAGE`` is negative and ``called`` is exactly ``dosage >= 0``."""
    import pairwise_completeness_scan as pcs

    assert pcs.MISSING_DOSAGE < 0
    assert pcs.BED_MAGIC == b"\x6c\x1b"
    assert pcs.BED_MODE_SNP_MAJOR == 0x01
    assert pcs.BED_MODE_INDIVIDUAL_MAJOR == 0x00

    base = _write_bfile(
        tmp_path,
        codes_per_variant=[[_CODE_MISSING, _CODE_HET, _CODE_MISSING, _CODE_HOM_A2]],
        n_samples=4,
    )
    reader = pcs.BedReader(base)
    try:
        geno = reader.read_variant(0)
        assert np.array_equal(geno.called, geno.dosage >= 0)
        assert geno.called.tolist() == [False, True, False, True]
    finally:
        reader.close()


# =========================================================================== #
# T2 — candidate enumeration (both sides), the DIRECT pairwise test, gradient  #
# =========================================================================== #

def _bim_row(chrom: str, bp: int, ref: str, alt: str) -> list[str]:
    """An explicit .bim row: [chr, chr:bp:REF:ALT, cm, bp, A1=ALT, A2=REF]."""
    return [chrom, f"{chrom}:{bp}:{ref}:{alt}", "0", str(bp), alt, ref]


#: The MEASURED m2_region_00057 pair geometry (halt record §MECHANISM CONFIRMED).
_DEL_VID_00057 = "chr15:20394741:AT:A"
_PARTNER_VID_00057 = "chr15:20394743:T:C"


def _joint_table_bfile(
    tmp_path: Path,
    cells,
    *,
    prefix: str,
    del_pos: int = 20394741,
    del_ref: str = "AT",
    del_alt: str = "A",
    partner_pos: int = 20394743,
    partner_ref: str = "T",
    partner_alt: str = "C",
    chrom: str = "chr15",
) -> Path:
    """Turn a joint ``(deletion, partner)`` dosage/NA table into a 2-variant bfile.

    ``cells`` maps ``(del_dosage_str, partner_dosage_str)`` -> sample count, using
    the ``plink --recode A`` string vocabulary ``{"0", "1", "2", "NA"}`` exactly as
    the halt record's dump prints it. The fixture geometry MATCHES the measured
    pair: the deletion's REF spans ``[20394741, 20394742]`` and the partner sits at
    ``20394743``, i.e. offset ``+1`` past ``span_end``.
    """
    del_codes: list[int] = []
    partner_codes: list[int] = []
    for (a, b), count in cells.items():
        del_codes.extend([_DOSAGE_STR_TO_CODE[a]] * count)
        partner_codes.extend([_DOSAGE_STR_TO_CODE[b]] * count)
    n_samples = len(del_codes)
    return _write_bfile(
        tmp_path,
        codes_per_variant=[del_codes, partner_codes],
        n_samples=n_samples,
        prefix=prefix,
        bim_rows=[
            _bim_row(chrom, del_pos, del_ref, del_alt),
            _bim_row(chrom, partner_pos, partner_ref, partner_alt),
        ],
    )


def _single_pair_result(pcs, tmp_path: Path, cells, prefix: str, window_bp: int = 5):
    """Build a 2-variant joint-table bfile and evaluate its ONE candidate pair."""
    base = _joint_table_bfile(tmp_path, cells, prefix=prefix)
    rows = pcs.load_bim_rows(base.with_suffix(".bim"))
    indexed = list(enumerate(rows))
    pairs = pcs.enumerate_candidates("R", indexed, window_bp=window_bp)
    assert len(pairs) == 1, f"expected exactly one candidate row, got {len(pairs)}"
    reader = pcs.BedReader(base)
    try:
        return pcs.evaluate_pair(reader, pairs[0])
    finally:
        reader.close()


# --------------------------------------------------------------------------- #
# The SIGNED OFFSET convention                                                 #
# --------------------------------------------------------------------------- #

def test_span_offset_signed_convention_table():
    """ONE stated convention: signed distance from the REF interval [pos, span_end].

    ``V.pos < D.pos``            -> ``V.pos - D.pos``      (NEGATIVE, upstream)
    ``D.pos <= V.pos <= span_end`` -> ``0``                (interior, BOTH ends inclusive)
    ``V.pos > span_end``         -> ``V.pos - span_end``   (POSITIVE, downstream)
    """
    import pairwise_completeness_scan as pcs

    # A 3 bp deletion at 1000: REF interval is [1000, 1002].
    deletion = pcs.parse_bim_row(_del_row(1000, 3), index=0)
    assert deletion.span_end == 1002

    table = [
        (990, -10, "upstream"),
        (999, -1, "upstream"),
        (1000, 0, "interior"),   # CO-LOCATED: inside the interval, left end inclusive
        (1001, 0, "interior"),
        (1002, 0, "interior"),   # right end inclusive
        (1003, 1, "downstream"),  # <- the MEASURED 00057 partner's offset
        (1027, 25, "downstream"),
    ]
    for bp, expected_offset, expected_side in table:
        variant = pcs.parse_bim_row(_snp_row(bp), index=1)
        assert pcs.span_offset(deletion, variant) == expected_offset, (
            f"offset at bp={bp}: expected {expected_offset}"
        )
        assert pcs.side_for_offset(expected_offset) == expected_side


def test_offset_zero_and_already_occluded_are_not_the_same_predicate():
    """A CO-LOCATED partner has ``offset == 0`` but ``already_occluded == False``.

    The POSTED occlusion rule's left bound is STRICT (``d.pos < v.pos <= span_end``),
    so "interior" and "already covered by the posted criterion" are DIFFERENT
    predicates and must never be silently conflated.
    """
    import pairwise_completeness_scan as pcs

    rows = [
        (0, _del_row(1000, 3)),
        (1, _snp_row(1000)),   # co-located with the deletion's POS
        (2, _snp_row(1001)),   # strictly inside -> occluded under the posted rule
    ]
    pairs = pcs.enumerate_candidates("R", rows, window_bp=5)
    by_pos = {p.partner_pos: p for p in pairs}

    assert by_pos[1000].offset == 0
    assert by_pos[1000].side == "interior"
    assert by_pos[1000].already_occluded is False   # STRICT left bound

    assert by_pos[1001].offset == 0
    assert by_pos[1001].side == "interior"
    assert by_pos[1001].already_occluded is True

    # The two predicates disagree on at least one emitted row -> not the same test.
    assert {p.offset == 0 for p in pairs} != {p.already_occluded for p in pairs} or (
        any(p.offset == 0 and not p.already_occluded for p in pairs)
    )


def test_default_window_bp_is_25_and_is_a_measurement_window():
    """``DEFAULT_WINDOW_BP`` is 25 and the docstring calls it a MEASUREMENT window."""
    import pairwise_completeness_scan as pcs

    assert pcs.DEFAULT_WINDOW_BP == 25
    doc = pcs.__doc__ or ""
    assert "MEASUREMENT window" in doc or "MEASUREMENT window" in (
        (_SRC_PYTHON / "pairwise_completeness_scan.py").read_text()
    )


# --------------------------------------------------------------------------- #
# Candidate enumeration                                                        #
# --------------------------------------------------------------------------- #

def test_enumerate_emits_both_sides_with_signed_offsets():
    """The posted rule is one-sided; alignment ambiguity at an indel is NOT.

    An UPSTREAM partner must be enumerated with a NEGATIVE offset. Seen RED
    against a one-sided window (perturbation P6).
    """
    import pairwise_completeness_scan as pcs

    rows = [
        (0, _snp_row(997)),        # upstream, offset -3
        (1, _del_row(1000, 3)),    # anchor: REF interval [1000, 1002]
        (2, _snp_row(1005)),       # downstream, offset +3
    ]
    pairs = pcs.enumerate_candidates("R", rows, window_bp=10)
    by_pos = {p.partner_pos: p for p in pairs}
    assert set(by_pos) == {997, 1005}

    assert by_pos[997].offset == -3
    assert by_pos[997].side == "upstream"
    assert by_pos[997].already_occluded is False

    assert by_pos[1005].offset == 3
    assert by_pos[1005].side == "downstream"
    assert by_pos[1005].already_occluded is False

    for p in pairs:
        assert p.region_id == "R"
        assert p.del_index == 1
        assert p.del_pos == 1000
        assert p.del_span_end == 1002
        assert p.del_ref_len == 3


def test_window_boundary_is_inclusive_at_exactly_plus_and_minus_K():
    """Exactly ``+K`` and exactly ``-K`` are IN; ``+(K+1)`` and ``-(K+1)`` are OUT.

    Seen RED against a ``<`` boundary (perturbation P7), which drops the ``+K`` row.
    """
    import pairwise_completeness_scan as pcs

    K = 5
    rows = [
        (0, _snp_row(1000 - K - 1)),   # 994  -> EXCLUDED
        (1, _snp_row(1000 - K)),       # 995  -> INCLUDED, offset -5
        (2, _del_row(1000, 3)),        # span_end 1002
        (3, _snp_row(1002 + K)),       # 1007 -> INCLUDED, offset +5
        (4, _snp_row(1002 + K + 1)),   # 1008 -> EXCLUDED
    ]
    pairs = pcs.enumerate_candidates("R", rows, window_bp=K)
    offsets = sorted(p.offset for p in pairs)
    assert offsets == [-K, K]
    assert sorted(p.partner_pos for p in pairs) == [995, 1007]


def test_only_deletions_anchor_candidates():
    """An SNV and an INSERTION have a single-base footprint and anchor NOTHING."""
    import pairwise_completeness_scan as pcs

    rows = [
        (0, _snp_row(1000)),
        (1, _ins_row(1002, 6)),   # len(ALT) > len(REF); REF is one anchor base
        (2, _snp_row(1004)),
    ]
    assert pcs.enumerate_candidates("R", rows, window_bp=25) == []

    # Adding ONE real deletion turns the same neighbourhood into candidates.
    rows_with_del = rows + [(3, _del_row(1006, 4))]
    rows_with_del.sort(key=lambda t: int(t[1][_BP_COL]))
    pairs = pcs.enumerate_candidates("R", rows_with_del, window_bp=25)
    assert {p.del_index for p in pairs} == {3}


_BP_COL = 3  # .bim bp column, for sorting FIXTURE rows only (never a module constant)


def test_self_pairs_are_never_emitted():
    """A deletion never pairs with itself, even though it lies in its own window."""
    import pairwise_completeness_scan as pcs

    rows = [(0, _del_row(1000, 3))]
    assert pcs.enumerate_candidates("R", rows, window_bp=25) == []

    rows2 = [(0, _del_row(1000, 3)), (1, _snp_row(1004))]
    pairs = pcs.enumerate_candidates("R", rows2, window_bp=25)
    assert all(p.del_index != p.partner_index for p in pairs)
    assert len(pairs) == 1


def test_deletion_deletion_neighbour_emits_two_rows_one_pair_key():
    """Two neighbouring deletions give TWO ordered rows but ONE distinct pair.

    The summary counts ``n_candidate_rows`` AND ``n_distinct_pairs`` so neither can
    be quoted as the other.
    """
    import pairwise_completeness_scan as pcs

    rows = [(0, _del_row(1000, 3)), (1, _del_row(1010, 2))]
    pairs = pcs.enumerate_candidates("R", rows, window_bp=25)
    assert len(pairs) == 2
    assert len({p.pair_key for p in pairs}) == 1
    # The two anchors carry their OWN offsets, and they are NOT mirror images:
    # offset is measured from the ANCHOR's REF interval, so anchoring on the
    # 3 bp deletion at 1000 puts its partner 1010 - 1002 = +8 past span_end,
    # while anchoring on the 2 bp deletion at 1010 puts its partner
    # 1000 - 1010 = -10 before pos. That asymmetry is the convention working.
    assert sorted(p.offset for p in pairs) == [-10, 8]
    assert {(p.del_index, p.partner_index) for p in pairs} == {(0, 1), (1, 0)}


def test_unsorted_input_raises():
    """Binary-search windowing depends on position order — fail CLOSED, not silent."""
    import pairwise_completeness_scan as pcs

    rows = [(0, _del_row(1000, 3)), (1, _snp_row(990))]
    with pytest.raises(ValueError) as exc:
        pcs.enumerate_candidates("R", rows, window_bp=25)
    assert "sorted" in str(exc.value).lower() or "order" in str(exc.value).lower()


def test_mixed_chromosome_input_raises():
    """A window is single-chromosome by contract."""
    import pairwise_completeness_scan as pcs

    rows = [(0, _del_row(1000, 3, chrom=1)), (1, _snp_row(1004, chrom=2))]
    with pytest.raises(ValueError) as exc:
        pcs.enumerate_candidates("R", rows, window_bp=25)
    assert "chrom" in str(exc.value).lower()


def test_interior_partner_is_flagged_already_occluded():
    """A partner strictly inside the REF span is 'already covered' by the posted rule."""
    import pairwise_completeness_scan as pcs

    rows = [(0, _del_row(1000, 5)), (1, _snp_row(1003)), (2, _snp_row(1009))]
    pairs = {p.partner_pos: p for p in pcs.enumerate_candidates("R", rows, window_bp=25)}
    assert pairs[1003].already_occluded is True   # 1000 < 1003 <= 1004
    assert pairs[1003].offset == 0
    assert pairs[1009].already_occluded is False
    assert pairs[1009].offset == 5


def test_iter_bim_windows_one_pass_global_indices(tmp_path, monkeypatch):
    """ONE streaming pass over the FULL .bim; values carry GLOBAL 0-based indices."""
    import builtins

    import pairwise_completeness_scan as pcs

    bim = tmp_path / "cohort.bim"
    bim.write_text(
        "".join(
            "\t".join(_snp_row(1000 + 10 * i, chrom=1)) + "\n" for i in range(20)
        )
    )

    real_open = builtins.open
    opens = {"n": 0}

    def counting_open(file, *args, **kwargs):
        try:
            if Path(file) == bim:
                opens["n"] += 1
        except TypeError:
            pass
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", counting_open)

    windows = [
        ("r1", "1", 1000, 1030),      # rows 0..3
        ("r2", "chr1", 1100, 1120),   # rows 10..12  (chr-prefix normalised)
        ("r3", "1", 1195, 1300),      # empty
    ]
    got = pcs.iter_bim_windows(bim, windows)

    assert opens["n"] == 1, f".bim opened {opens['n']} times, expected exactly 1"
    assert [i for i, _row in got["r1"]] == [0, 1, 2, 3]
    assert [i for i, _row in got["r2"]] == [10, 11, 12]
    assert got["r3"] == []
    assert [row[_BP_COL] for _i, row in got["r2"]] == ["1100", "1110", "1120"]


# --------------------------------------------------------------------------- #
# THE PAIRWISE TEST — the property, directly — and the GRADIENT                #
# --------------------------------------------------------------------------- #

def test_mirrors_a_measured_case_00057_perfect_confounding_MIRRORS_A_MEASURED_CASE(tmp_path):
    """MIRRORS_A_MEASURED_CASE — a 1/10-scale mirror of the m2_region_00057 pair.

    PROVENANCE (cited, never re-derived):
    ``.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md``
    §MECHANISM CONFIRMED. The measured joint table totals 73,122 (the full cohort
    .fam), 0 of 871 deletion carriers are called at the partner, the intersection
    is 71,048, and the deletion's marginal AF is 0.601%.

    This fixture MIRRORS that measurement at 1/10 scale. It DERIVES nothing and
    establishes NO prevalence: one pair cannot supply a rate, a boundary width, or
    a tail. Every oracle below is HAND-COMPUTED in this test body.

    ``n_samples = 7313`` is deliberately ``% 4 == 1``, so this realistic fixture
    ALSO exercises the padding-truncation path.
    """
    import pairwise_completeness_scan as pcs

    cells = {
        ("0", "0"): 7024,
        ("0", "NA"): 57,
        ("0", "1"): 82,
        ("1", "NA"): 87,
        ("NA", "NA"): 60,
        ("NA", "1"): 1,
        ("NA", "0"): 2,
    }
    assert sum(cells.values()) == 7313
    assert 7313 % 4 == 1  # exercises padding

    pr = _single_pair_result(pcs, tmp_path, cells, prefix="m00057")

    # -- geometry: the partner sits ONE BASE past the deletion's REF span end --
    assert pr.del_vid == _DEL_VID_00057
    assert pr.partner_vid == _PARTNER_VID_00057
    assert pr.del_ref_len == 2
    assert pr.del_span_end == 20394742
    assert pr.offset == 1
    assert pr.side == "downstream"
    assert pr.already_occluded is False   # the posted rule correctly declined

    # -- the intersection: 7024 + 82 = 7106 --
    assert pr.n_both_called == 7024 + 82 == 7106

    # -- the property: A collapses inside the intersection, B does not --
    assert pr.del_invariant is True
    assert pr.partner_invariant is False
    assert pr.undefined is True
    assert pr.invariant_member == "deletion"

    # -- deletion gradient: 7024+57+82+87 = 7250 called; 87 carriers, 0 retained --
    assert pr.n_called_del == 7024 + 57 + 82 + 87 == 7250
    assert pr.del_carriers_marginal == 87
    assert pr.del_carriers_retained == 0
    assert pr.del_carriers_lost == 87
    assert pr.del_carriers_lost_frac == 1.0
    # 87 / (2 * 7250) = 0.006
    assert round(pr.del_maf_marginal, 4) == 0.0060
    # The MEASURED marginal was 0.601%. The mirror lands within 0.01 pp — that
    # agreement is a FIXTURE PROPERTY (the mirror was built at 1/10 scale from the
    # measured cells), NOT an independent rederivation of the measurement.
    assert abs(pr.del_maf_marginal * 100.0 - 0.601) <= 0.01

    # -- partner gradient: 7024+82+1+2 = 7109 called; 83 carriers, 82 retained --
    assert pr.n_called_partner == 7024 + 82 + 1 + 2 == 7109
    assert pr.partner_carriers_marginal == 83
    assert pr.partner_carriers_retained == 82
    assert pr.partner_carriers_lost == 1
    assert round(pr.partner_carriers_lost_frac, 8) == round(1 / 83, 8)

    # -- the DERIVED label (never the test) --
    assert pr.confounding_pattern == "perfect_deletion_confounding"


def test_partial_confounding_is_DEFINED_and_the_gradient_sees_it(tmp_path):
    """THIS IS THE BLIND SPOT.

    The identical fixture with 5 of the 87 ``('1','NA')`` samples moved to
    ``('1','0')``. plink returns a FINITE ``r`` — **no NaN check anywhere in the
    pipeline fires on this row** — yet that ``r`` was computed on a biased
    subsample that has lost 82 of the deletion's 87 carriers. The carriers-lost
    GRADIENT is the only instrument in the project that can see it.

    Whether such a tail EXISTS in the panel is OPEN. This test proves only that
    the instrument reports it when it is present.
    """
    import pairwise_completeness_scan as pcs

    cells = {
        ("0", "0"): 7024,
        ("0", "NA"): 57,
        ("0", "1"): 82,
        ("1", "NA"): 82,   # 87 - 5
        ("1", "0"): 5,     # the 5 carriers that ARE called at the partner
        ("NA", "NA"): 60,
        ("NA", "1"): 1,
        ("NA", "0"): 2,
    }
    assert sum(cells.values()) == 7313

    pr = _single_pair_result(pcs, tmp_path, cells, prefix="m00057partial")

    assert pr.undefined is False          # <- plink would return a finite r
    assert pr.del_invariant is False
    assert pr.partner_invariant is False
    assert pr.invariant_member == "none"

    assert pr.n_both_called == 7024 + 82 + 5 == 7111
    assert pr.del_carriers_marginal == 87
    assert pr.del_carriers_retained == 5
    assert pr.del_carriers_lost == 82
    assert round(pr.del_carriers_lost_frac, 4) == 0.9425   # 82 / 87
    assert pr.confounding_pattern == "partial"


def test_partner_is_the_invariant_member(tmp_path):
    """BOTH members are tested. Do not assume the deletion is the collapsing one."""
    import pairwise_completeness_scan as pcs

    cells = {                    # the 00057 table with the roles mirrored
        ("0", "0"): 7024,
        ("NA", "0"): 57,
        ("1", "0"): 82,
        ("NA", "1"): 87,
        ("NA", "NA"): 60,
        ("1", "NA"): 1,
        ("0", "NA"): 2,
    }
    pr = _single_pair_result(pcs, tmp_path, cells, prefix="mirrorrole")

    assert pr.n_both_called == 7024 + 82 == 7106
    assert pr.del_invariant is False
    assert pr.partner_invariant is True
    assert pr.undefined is True
    assert pr.invariant_member == "partner"
    assert pr.partner_carriers_marginal == 87
    assert pr.partner_carriers_retained == 0
    assert pr.partner_carriers_lost_frac == 1.0
    assert pr.confounding_pattern == "perfect_partner_confounding"


def test_undefined_without_carriers_subset_of_missing(tmp_path):
    """The primary path is THE PROPERTY, not the ``carriers ⊆ missing`` shortcut.

    Here ``carriers(deletion) ⊆ missing(partner)`` is DEMONSTRABLY FALSE — 20 of
    the deletion's 30 carriers ARE called at the partner — and the pair is STILL
    undefined, because the PARTNER collapses inside the intersection.

    Seen RED against an implementation whose primary test is the one-directional
    deletion-side containment shortcut (perturbation P5-T2/a).
    """
    import pairwise_completeness_scan as pcs

    cells = {
        ("1", "0"): 20,    # deletion carriers CALLED at the partner
        ("1", "NA"): 10,   # deletion carriers missing at the partner
        ("0", "0"): 400,
        ("NA", "1"): 15,   # every partner carrier is no-called at the deletion
        ("0", "NA"): 5,
    }
    assert sum(cells.values()) == 450

    # The shortcut predicate, computed HERE so the test states what it refutes:
    del_carriers = cells[("1", "0")] + cells[("1", "NA")]              # 30
    del_carriers_in_missing_partner = cells[("1", "NA")]               # 10
    assert del_carriers_in_missing_partner < del_carriers, (
        "carriers(deletion) is NOT a subset of missing(partner) in this fixture"
    )

    pr = _single_pair_result(pcs, tmp_path, cells, prefix="notsubset")

    assert pr.n_both_called == 420
    assert pr.del_invariant is False        # the deletion IS variable here
    assert pr.partner_invariant is True     # the partner is the one that collapses
    assert pr.undefined is True
    assert pr.invariant_member == "partner"
    assert pr.del_carriers_marginal == 30
    assert pr.del_carriers_retained == 20
    assert round(pr.del_carriers_lost_frac, 6) == round(10 / 30, 6)


def test_empty_intersection_is_undefined(tmp_path):
    """Disjoint call sets: the degenerate TRUE case, reported explicitly."""
    import pairwise_completeness_scan as pcs

    cells = {
        ("0", "NA"): 200,
        ("1", "NA"): 30,
        ("NA", "0"): 180,
        ("NA", "1"): 40,
    }
    pr = _single_pair_result(pcs, tmp_path, cells, prefix="disjoint")

    assert pr.n_both_called == 0
    assert pr.undefined is True
    assert pr.del_invariant is True
    assert pr.partner_invariant is True
    assert pr.invariant_member == "both"
    assert pr.confounding_pattern == "empty_intersection"


def test_fully_defined_pair_has_zero_gradient(tmp_path):
    """A healthy pair: defined, and BOTH gradients are exactly zero."""
    import pairwise_completeness_scan as pcs

    cells = {
        ("0", "0"): 800,
        ("1", "0"): 60,
        ("0", "1"): 55,
        ("1", "1"): 25,
    }
    pr = _single_pair_result(pcs, tmp_path, cells, prefix="healthy")

    assert pr.undefined is False
    assert pr.del_invariant is False
    assert pr.partner_invariant is False
    assert pr.invariant_member == "none"
    assert pr.del_carriers_lost == 0
    assert pr.partner_carriers_lost == 0
    assert pr.del_carriers_lost_frac == 0.0
    assert pr.partner_carriers_lost_frac == 0.0
    assert pr.confounding_pattern == "none"


def test_lost_frac_one_implies_undefined(tmp_path):
    """PROPERTY: ``carriers_lost_frac == 1.0`` for a member IMPLIES it is invariant.

    Guards against a gradient that disagrees with the primary test. Asserted over
    every constructed case at once, so a future case cannot quietly violate it.
    """
    import pairwise_completeness_scan as pcs

    cases = {
        "perfect_del": {
            ("0", "0"): 7024, ("0", "NA"): 57, ("0", "1"): 82, ("1", "NA"): 87,
            ("NA", "NA"): 60, ("NA", "1"): 1, ("NA", "0"): 2,
        },
        "partial": {
            ("0", "0"): 7024, ("0", "NA"): 57, ("0", "1"): 82, ("1", "NA"): 82,
            ("1", "0"): 5, ("NA", "NA"): 60, ("NA", "1"): 1, ("NA", "0"): 2,
        },
        "partner_collapses": {
            ("1", "0"): 20, ("1", "NA"): 10, ("0", "0"): 400,
            ("NA", "1"): 15, ("0", "NA"): 5,
        },
        "healthy": {
            ("0", "0"): 800, ("1", "0"): 60, ("0", "1"): 55, ("1", "1"): 25,
        },
    }
    seen_a_one = False
    for name, cells in cases.items():
        pr = _single_pair_result(pcs, tmp_path, cells, prefix=f"impl_{name}")
        if pr.del_carriers_lost_frac == 1.0 and pr.del_carriers_marginal > 0:
            seen_a_one = True
            assert pr.del_invariant is True, f"{name}: del lost_frac 1.0 but not invariant"
            assert pr.undefined is True
        if pr.partner_carriers_lost_frac == 1.0 and pr.partner_carriers_marginal > 0:
            seen_a_one = True
            assert pr.partner_invariant is True, f"{name}: partner lost_frac 1.0 but not invariant"
            assert pr.undefined is True
    assert seen_a_one, "the property was never exercised — the test proves nothing"


def test_scan_region_evaluates_every_candidate_row(tmp_path):
    """``scan_region`` returns one :class:`PairResult` per enumerated candidate row."""
    import pairwise_completeness_scan as pcs

    n = 12
    base = _write_bfile(
        tmp_path,
        codes_per_variant=[
            [_CODE_HOM_A2] * 10 + [_CODE_HET, _CODE_MISSING],   # deletion
            [_CODE_HOM_A2] * 8 + [_CODE_HET] * 4,               # partner A
            [_CODE_HOM_A2] * 6 + [_CODE_HET] * 6,               # partner B
        ],
        n_samples=n,
        bim_rows=[
            _bim_row("chr1", 1000, "ATG", "A"),   # span_end 1002
            _bim_row("chr1", 1004, "T", "C"),     # offset +2
            _bim_row("chr1", 1009, "G", "A"),     # offset +7
        ],
    )
    rows = pcs.load_bim_rows(base.with_suffix(".bim"))
    indexed = list(enumerate(rows))
    reader = pcs.BedReader(base)
    try:
        results = pcs.scan_region(reader, "R7", indexed, window_bp=10)
    finally:
        reader.close()

    assert len(results) == 2
    assert {r.offset for r in results} == {2, 7}
    assert all(r.region_id == "R7" for r in results)
    assert all(r.del_index == 0 for r in results)
    assert {r.partner_index for r in results} == {1, 2}
    assert all(r.n_both_called > 0 for r in results)
