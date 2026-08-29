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


# =========================================================================== #
# T3 — egress-clean TSV / summary rollup, the CLI, and the PENDING PASTE       #
# =========================================================================== #

#: Tokens that must never appear in an emitted column or key name. The AoU
#: egress boundary is aggregate counts, fractions and variant coordinates ONLY.
_FORBIDDEN_EGRESS_TOKENS = ("sample", "iid", "fid", "id_list", "dosage")

#: The maximum rendered length of any single emitted field. A per-sample vector
#: cannot fit in 64 chars, so this is a shape check on the egress surface.
_MAX_FIELD_CHARS = 64


#: The most entries an emitted aggregate distribution may hold. An offset
#: histogram over a +/-25 bp window has at most 2*25 + 1 == 51 distinct offsets
#: and the lost-frac bins have 6, so this is generous — while a per-sample map
#: over 73,122 samples could never satisfy it.
_MAX_DISTRIBUTION_ENTRIES = 512


def _assert_egress_clean(column_names, row_mapping):
    """The SHARED egress assertion — used by the green test AND its negative control.

    Two emitted summary fields are aggregate DISTRIBUTIONS (the undefined-set
    offset histogram and the defined-row lost-frac bins), so the rule is applied
    RECURSIVELY rather than flatly: every key and every value inside a
    distribution must itself be a short scalar, and the distribution's cardinality
    is bounded by something that is NOT n_samples. That is strictly stronger than
    a flat width check on the rendered dict — a per-sample map cannot hide inside.
    """
    for name in list(column_names) + list(row_mapping):
        low = str(name).lower()
        for token in _FORBIDDEN_EGRESS_TOKENS:
            assert token not in low, (
                f"emitted name {name!r} contains forbidden egress token {token!r}"
            )

    def _check_scalar(label, value):
        rendered = str(value)
        assert len(rendered) <= _MAX_FIELD_CHARS, (
            f"field {label!r} renders to {len(rendered)} chars (> {_MAX_FIELD_CHARS}); "
            "per-sample data must never cross the perimeter"
        )

    for name, value in row_mapping.items():
        if isinstance(value, dict):
            assert len(value) <= _MAX_DISTRIBUTION_ENTRIES, (
                f"distribution {name!r} holds {len(value)} entries "
                f"(> {_MAX_DISTRIBUTION_ENTRIES}); that is per-sample scale"
            )
            for k, v in value.items():
                _check_scalar(f"{name}[{k!r}] key", k)
                _check_scalar(f"{name}[{k!r}]", v)
        else:
            _check_scalar(name, value)


_MIRROR_00057_CELLS = {
    ("0", "0"): 7024,
    ("0", "NA"): 57,
    ("0", "1"): 82,
    ("1", "NA"): 87,
    ("NA", "NA"): 60,
    ("NA", "1"): 1,
    ("NA", "0"): 2,
}


def test_tsv_columns_exact_tuple_equality():
    """``TSV_COLUMNS`` is pinned by EXACT tuple equality — a must-be-identity check.

    Adding, removing or reordering a column breaks this deliberately.
    """
    import pairwise_completeness_scan as pcs

    assert pcs.TSV_COLUMNS == (
        "region_id",
        "del_index",
        "del_vid",
        "del_chr",
        "del_pos",
        "del_ref_len",
        "del_span_end",
        "partner_index",
        "partner_vid",
        "partner_pos",
        "offset",
        "side",
        "already_occluded",
        "pair_key",
        "n_called_del",
        "n_called_partner",
        "n_both_called",
        "del_invariant",
        "del_globally_invariant",
        "partner_invariant",
        "partner_globally_invariant",
        "undefined",
        "invariant_member",
        "del_carriers_marginal",
        "del_carriers_retained",
        "del_carriers_lost",
        "del_carriers_lost_frac",
        "del_maf_marginal",
        "del_minor_allele_tie",
        "partner_carriers_marginal",
        "partner_carriers_retained",
        "partner_carriers_lost",
        "partner_carriers_lost_frac",
        "partner_maf_marginal",
        "partner_minor_allele_tie",
        "confounding_pattern",
    )


def test_pair_result_fields_are_the_tsv_columns():
    """A must-be-identity link: the record's fields ARE the emitted columns."""
    import pairwise_completeness_scan as pcs

    assert pcs.PairResult._fields == pcs.TSV_COLUMNS


def test_summary_keys_exact_equality():
    """``SUMMARY_KEYS`` is pinned by exact equality, and a real summary matches it."""
    import pairwise_completeness_scan as pcs

    assert pcs.SUMMARY_KEYS == (
        "region_id",
        "window_bp",
        "n_deletions",
        "n_candidate_rows",
        "n_distinct_pairs",
        "n_undefined_rows",
        "n_undefined_distinct_pairs",
        "n_undefined_already_occluded",
        "n_undefined_not_already_occluded",
        "undefined_offset_histogram",
        "defined_carriers_lost_frac_bins",
        "max_carriers_lost_frac_defined",
        "n_defined_lost_frac_ge_0p9",
        "n_candidates_edge_clipped",
        "n_globally_invariant_variants",
        "n_undefined_rows_with_globally_invariant_member",
    )
    # F7: the denominators are EXPLICIT — an empty region with no deletions.
    assert set(
        pcs.summarize(
            "R", [], n_deletions=0, n_candidates_edge_clipped=0
        ).keys()
    ) == set(pcs.SUMMARY_KEYS)


def test_egress_emitted_names_and_field_widths_are_clean(tmp_path):
    """No emitted name names a person; no emitted field is per-sample sized."""
    import pairwise_completeness_scan as pcs

    pr = _single_pair_result(pcs, tmp_path, _MIRROR_00057_CELLS, prefix="egress")
    _assert_egress_clean(pcs.TSV_COLUMNS, pr._asdict())
    _assert_egress_clean(
        pcs.SUMMARY_KEYS,
        pcs.summarize("R", [pr], n_deletions=1, n_candidates_edge_clipped=0),
    )


def test_egress_assertion_catches_a_per_sample_field(tmp_path):
    """NEGATIVE CONTROL — the SAME helper must FAIL on a polluted row.

    A green assertion is evidence only if it has been seen to fail
    (``feedback_green_assertion_needs_a_negative_control``).
    """
    import pairwise_completeness_scan as pcs

    pr = _single_pair_result(pcs, tmp_path, _MIRROR_00057_CELLS, prefix="egressnc")
    polluted = dict(pr._asdict())
    polluted["sample_ids"] = ",".join(f"I{i}" for i in range(7313))

    with pytest.raises(AssertionError) as exc:
        _assert_egress_clean(pcs.TSV_COLUMNS, polluted)
    assert "sample" in str(exc.value)

    # ... and a long value under an innocuous NAME is caught by the width rule.
    polluted2 = dict(pr._asdict())
    polluted2["extra"] = "x" * 65
    with pytest.raises(AssertionError) as exc2:
        _assert_egress_clean(pcs.TSV_COLUMNS, polluted2)
    assert "65 chars" in str(exc2.value)

    # ... and a per-sample MAP hidden inside an aggregate-looking distribution
    # is caught by the cardinality bound, not merely by the rendered width.
    polluted3 = dict(
        pcs.summarize("R", [pr], n_deletions=1, n_candidates_edge_clipped=0)
    )
    polluted3["undefined_offset_histogram"] = {str(i): 1 for i in range(7313)}
    with pytest.raises(AssertionError) as exc3:
        _assert_egress_clean(pcs.SUMMARY_KEYS, polluted3)
    assert "per-sample scale" in str(exc3.value)


def test_no_summary_key_names_a_rate_or_prevalence():
    """The summary reports COUNTS and FRACTIONS only — never an inferred rate.

    The prevalence, the boundary width and the tail are OPEN questions. A key
    called ``*_rate`` or ``*_prevalence`` would invite quoting one region as an
    answer to them.
    """
    import pairwise_completeness_scan as pcs

    for key in pcs.SUMMARY_KEYS:
        low = key.lower()
        for banned in ("rate", "prevalence", "estimate", "ceiling"):
            assert banned not in low, f"summary key {key!r} contains {banned!r}"


def test_write_tsv_header_equals_tsv_columns(tmp_path):
    """The header written to disk EQUALS ``TSV_COLUMNS``, in order."""
    import pairwise_completeness_scan as pcs

    pr = _single_pair_result(pcs, tmp_path, _MIRROR_00057_CELLS, prefix="tsvhdr")
    out = tmp_path / "pairs.tsv"
    pcs.write_tsv([pr], out)

    lines = out.read_text().splitlines()
    assert tuple(lines[0].split("\t")) == pcs.TSV_COLUMNS
    assert len(lines) == 2
    values = lines[1].split("\t")
    assert len(values) == len(pcs.TSV_COLUMNS)
    row = dict(zip(pcs.TSV_COLUMNS, values))
    assert row["del_vid"] == _DEL_VID_00057
    assert row["undefined"] == "True"
    assert row["offset"] == "1"
    assert row["n_both_called"] == "7106"
    assert row["del_carriers_lost"] == "87"


def _fake_result(pcs, **overrides):
    """A hand-built :class:`PairResult` for summary arithmetic (no genotypes)."""
    base = dict(
        region_id="R", del_index=0, del_vid="d0", del_chr="chr1", del_pos=1000,
        del_ref_len=3, del_span_end=1002, partner_index=1, partner_vid="p1",
        partner_pos=1003, offset=1, side="downstream", already_occluded=False,
        pair_key="d0|p1", n_called_del=100, n_called_partner=100,
        n_both_called=90, del_invariant=False, del_globally_invariant=False,
        partner_invariant=False, partner_globally_invariant=False,
        undefined=False, invariant_member="none", del_carriers_marginal=10,
        del_carriers_retained=10, del_carriers_lost=0,
        del_carriers_lost_frac=0.0, del_maf_marginal=0.05,
        del_minor_allele_tie=False,
        partner_carriers_marginal=8, partner_carriers_retained=8,
        partner_carriers_lost=0, partner_carriers_lost_frac=0.0,
        partner_maf_marginal=0.04, partner_minor_allele_tie=False,
        confounding_pattern="none",
    )
    base.update(overrides)
    return pcs.PairResult(**base)


def test_summarize_counts_every_number():
    """Every summary number asserted on a hand-built result list."""
    import pairwise_completeness_scan as pcs

    results = [
        # 1. a NEWLY DISCOVERED undefined pair at offset +1
        _fake_result(pcs, pair_key="a|b", offset=1, already_occluded=False,
                     undefined=True, del_invariant=True, invariant_member="deletion",
                     del_carriers_lost=10, del_carriers_lost_frac=1.0,
                     confounding_pattern="perfect_deletion_confounding"),
        # 2. an ALREADY-OCCLUDED undefined pair, interior (offset 0)
        _fake_result(pcs, pair_key="c|d", offset=0, side="interior",
                     already_occluded=True, undefined=True, del_invariant=True,
                     invariant_member="deletion", del_carriers_lost=10,
                     del_carriers_lost_frac=1.0,
                     confounding_pattern="perfect_deletion_confounding"),
        # 3. a DEFINED pair deep in the partial-confounding tail
        _fake_result(pcs, pair_key="e|f", offset=2, del_carriers_retained=5,
                     del_carriers_lost=82, del_carriers_marginal=87,
                     del_carriers_lost_frac=82 / 87, confounding_pattern="partial"),
        # 4. a healthy DEFINED pair
        _fake_result(pcs, pair_key="g|h", offset=-3, side="upstream"),
        # 5. the OTHER ordered row of pair 1 (same pair_key, own offset)
        _fake_result(pcs, pair_key="a|b", offset=-4, side="upstream",
                     del_index=1, partner_index=0, already_occluded=False,
                     undefined=True, del_invariant=True, invariant_member="deletion",
                     del_carriers_lost=10, del_carriers_lost_frac=1.0,
                     confounding_pattern="perfect_deletion_confounding"),
    ]
    s = pcs.summarize(
        "m2_region_00057", results, window_bp=25,
        n_deletions=3, n_candidates_edge_clipped=0,
    )

    assert set(s) == set(pcs.SUMMARY_KEYS)
    assert s["region_id"] == "m2_region_00057"
    assert s["window_bp"] == 25
    assert s["n_deletions"] == 3
    assert s["n_candidate_rows"] == 5
    assert s["n_distinct_pairs"] == 4          # a|b counted ONCE
    assert s["n_undefined_rows"] == 3          # rows 1, 2, 5
    assert s["n_undefined_distinct_pairs"] == 2  # a|b and c|d
    # Rows and pairs are DIFFERENT counts and neither may be quoted as the other.
    assert s["n_undefined_rows"] != s["n_undefined_distinct_pairs"]


def test_summarize_separates_already_occluded_from_newly_discovered():
    """'Already covered by the posted rule' is separated from 'newly discovered'."""
    import pairwise_completeness_scan as pcs

    results = [
        _fake_result(pcs, pair_key="a|b", offset=1, already_occluded=False,
                     undefined=True, del_invariant=True, invariant_member="deletion"),
        _fake_result(pcs, pair_key="c|d", offset=0, side="interior",
                     already_occluded=True, undefined=True, del_invariant=True,
                     invariant_member="deletion"),
        _fake_result(pcs, pair_key="e|f", offset=4),  # defined
    ]
    # F7: one deletion anchors all three rows (every _fake_result del_index is 0).
    s = pcs.summarize("R", results, n_deletions=1, n_candidates_edge_clipped=0)

    assert s["n_undefined_distinct_pairs"] == 2
    assert s["n_undefined_already_occluded"] == 1
    assert s["n_undefined_not_already_occluded"] == 1
    # The split must be EXHAUSTIVE — no undefined pair may fall between them.
    assert (
        s["n_undefined_already_occluded"] + s["n_undefined_not_already_occluded"]
        == s["n_undefined_distinct_pairs"]
    )


def test_summarize_offset_histogram_over_undefined_rows_only():
    """The offset histogram is what supplies the EMPIRICAL boundary width.

    It is taken over the UNDEFINED set only, per ROW (each row carries one
    anchor-relative offset), so it sums to ``n_undefined_rows``. It is a
    DISTRIBUTION, not a width: this task states no width.
    """
    import pairwise_completeness_scan as pcs

    results = [
        _fake_result(pcs, pair_key="a|b", offset=1, undefined=True,
                     del_invariant=True, invariant_member="deletion"),
        _fake_result(pcs, pair_key="c|d", offset=1, undefined=True,
                     del_invariant=True, invariant_member="deletion"),
        _fake_result(pcs, pair_key="e|f", offset=-2, undefined=True,
                     side="upstream", partner_invariant=True,
                     invariant_member="partner"),
        _fake_result(pcs, pair_key="g|h", offset=7),   # DEFINED -> not counted
    ]
    s = pcs.summarize("R", results, n_deletions=1, n_candidates_edge_clipped=0)

    assert s["undefined_offset_histogram"] == {"-2": 1, "1": 2}
    assert sum(s["undefined_offset_histogram"].values()) == s["n_undefined_rows"] == 3
    assert list(s["undefined_offset_histogram"]) == ["-2", "1"]  # numeric order
    assert "7" not in s["undefined_offset_histogram"]
    # JSON-safe: keys are strings.
    assert all(isinstance(k, str) for k in s["undefined_offset_histogram"])


def test_summarize_defined_lost_frac_bins_and_tail():
    """The DEFINED-row lost-frac distribution — the only view of a partial tail.

    A DEFINED row can never carry ``lost_frac == 1.0`` (lost_frac 1.0 implies the
    member is invariant, which implies undefined), which is why the top bin is
    open at 1.
    """
    import pairwise_completeness_scan as pcs

    results = [
        _fake_result(pcs, pair_key="a|b", del_carriers_lost_frac=0.0),
        _fake_result(pcs, pair_key="c|d", del_carriers_lost_frac=0.2),
        _fake_result(pcs, pair_key="e|f", del_carriers_lost_frac=0.4),
        _fake_result(pcs, pair_key="g|h", del_carriers_lost_frac=0.75),
        _fake_result(pcs, pair_key="i|j", del_carriers_lost_frac=82 / 87),  # 0.9425
        _fake_result(pcs, pair_key="k|l", del_carriers_lost_frac=0.995),
        # an UNDEFINED row must NOT enter the defined-only bins
        _fake_result(pcs, pair_key="m|n", undefined=True, del_invariant=True,
                     invariant_member="deletion", del_carriers_lost_frac=1.0),
        # the partner's gradient counts too: the bin uses max(del, partner)
        _fake_result(pcs, pair_key="o|p", del_carriers_lost_frac=0.0,
                     partner_carriers_lost_frac=0.93),
    ]
    s = pcs.summarize("R", results, n_deletions=1, n_candidates_edge_clipped=0)

    assert s["defined_carriers_lost_frac_bins"] == {
        "0": 1,
        "(0,0.25]": 1,
        "(0.25,0.5]": 1,
        "(0.5,0.9]": 1,
        "(0.9,0.99]": 2,     # 0.9425 and 0.93 (the latter via the PARTNER's gradient)
        "(0.99,1)": 1,
    }
    # Component-exact: the bins must sum to the DEFINED row count, never to the
    # row count (feedback_aggregate_agreement_hides_component_errors).
    assert sum(s["defined_carriers_lost_frac_bins"].values()) == 7  # 8 rows - 1 undefined
    assert len(results) - 1 == 7
    assert s["n_defined_lost_frac_ge_0p9"] == 3    # 0.9425, 0.995, 0.93
    assert round(s["max_carriers_lost_frac_defined"], 6) == 0.995


def test_pending_paste_exists_and_carries_the_harness_crosscheck():
    """The in-perimeter block exists, is marker-delimited, and cross-checks 00057."""
    paste = PROJECT_ROOT / ".planning" / "debug" / (
        "260825-PENDING-PASTE-pairwise-completeness-sweep.md"
    )
    assert paste.exists(), f"missing PENDING PASTE: {paste}"
    text = paste.read_text()
    for needle in (
        "--- PASTE FROM HERE ---",
        "--- PASTE ENDS HERE ---",
        "71048",
        "871",
        "20394741",
        "20394743",
        "occ_measure_sample.tsv",
        "m2_region_00057",
        "DISCARD ALL",
    ):
        assert needle in text, f"PENDING PASTE is missing {needle!r}"


# --------------------------------------------------------------------------- #
# The CLI — exercised END-TO-END in tmp_path. No perimeter, no network.        #
# --------------------------------------------------------------------------- #

def test_cli_single_region_reproduces_the_00057_oracles(tmp_path):
    """One region, end to end, reproducing the T2 oracles through the CLI."""
    import csv
    import json

    import pairwise_completeness_scan as pcs

    base = _joint_table_bfile(tmp_path, _MIRROR_00057_CELLS, prefix="cli1")
    out = tmp_path / "pairs.tsv"
    summ = tmp_path / "summary.json"
    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--region-id", "m2_region_00057",
        "--chr", "15",
        "--from-bp", "20394700",
        "--to-bp", "20394800",
        "--window-bp", "5",
        "--out", str(out),
        "--summary", str(summ),
    ])
    assert rc == 0
    assert out.exists() and summ.exists()

    rows = list(csv.DictReader(out.open(), delimiter="\t"))
    assert len(rows) == 1
    row = rows[0]
    assert row["region_id"] == "m2_region_00057"
    assert row["del_vid"] == _DEL_VID_00057
    assert row["partner_vid"] == _PARTNER_VID_00057
    assert row["offset"] == "1"
    assert row["undefined"] == "True"
    assert row["already_occluded"] == "False"
    assert int(row["n_both_called"]) == 7106
    assert int(row["del_carriers_lost"]) == 87
    assert row["confounding_pattern"] == "perfect_deletion_confounding"

    payload = json.loads(summ.read_text())
    assert set(payload) == {"m2_region_00057"}
    s = payload["m2_region_00057"]
    assert set(s) == set(pcs.SUMMARY_KEYS)
    assert s["n_candidate_rows"] == 1
    assert s["n_undefined_distinct_pairs"] == 1
    assert s["n_undefined_not_already_occluded"] == 1
    assert s["n_undefined_already_occluded"] == 0
    assert s["undefined_offset_histogram"] == {"1": 1}
    assert s["window_bp"] == 5
    assert s["n_deletions"] == 1


def _multi_region_bfile(tmp_path: Path, prefix: str = "cli2") -> Path:
    """Two single-chromosome windows, each with one deletion + one partner."""
    n = 16
    return _write_bfile(
        tmp_path,
        codes_per_variant=[
            [_CODE_HOM_A2] * 12 + [_CODE_HET] * 2 + [_CODE_MISSING] * 2,  # del r1
            [_CODE_HOM_A2] * 10 + [_CODE_HET] * 6,                        # snp r1
            [_CODE_HOM_A2] * 14 + [_CODE_HET] * 2,                        # del r2
            [_CODE_HOM_A2] * 9 + [_CODE_HET] * 7,                         # snp r2
        ],
        n_samples=n,
        prefix=prefix,
        bim_rows=[
            _bim_row("chr1", 1000, "ATG", "A"),   # span_end 1002
            _bim_row("chr1", 1004, "T", "C"),     # offset +2
            _bim_row("chr1", 5000, "AT", "A"),    # span_end 5001
            _bim_row("chr1", 5002, "G", "A"),     # offset +1
        ],
    )


def _regions_tsv(
    tmp_path: Path, name: str = "ld_regions.tsv", ancestry: str = "AFR"
) -> Path:
    """A config/ld_regions.tsv-shaped file: 1-based cols 1/2/7/15/16.

    Column 7 (0-based 6) is ``ancestry``. The real manifest is keyed on
    ``(region_id x ancestry)`` — 276 ids x {AFR, EUR} — and the scanner reads it
    on that key (quick-260826-qq9), so a fixture that left column 7 as ``"."``
    would match no ancestry and select nothing.
    """
    path = tmp_path / name
    header = ["c%d" % i for i in range(1, 17)]
    header[0], header[1], header[6] = "region_id", "chr", "ancestry"
    header[14], header[15] = "window_start_grch38", "window_end_grch38"
    rows = [header]
    for rid, chrom, start, end in [("r1", "1", 990, 1010), ("r2", "chr1", 4990, 5010)]:
        row = ["."] * 16
        row[0], row[1], row[6] = rid, chrom, ancestry
        row[14], row[15] = str(start), str(end)
        rows.append(row)
    path.write_text("".join("\t".join(r) + "\n" for r in rows))
    return path


def test_cli_multi_region_one_bim_pass(tmp_path, monkeypatch):
    """N regions cost the SAME number of ``.bim`` opens as one — one streaming pass."""
    import builtins
    import csv
    import json

    import pairwise_completeness_scan as pcs

    base = _multi_region_bfile(tmp_path)
    regions = _regions_tsv(tmp_path)
    bim = base.with_suffix(".bim")

    real_open = builtins.open
    counts = {"n": 0}

    def counting_open(file, *args, **kwargs):
        try:
            if Path(file) == bim:
                counts["n"] += 1
        except TypeError:
            pass
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", counting_open)

    def run(region_ids, tag):
        counts["n"] = 0
        out = tmp_path / f"pairs_{tag}.tsv"
        summ = tmp_path / f"summary_{tag}.json"
        rc = pcs.main([
            "--bfile-prefix", str(base),
            "--regions-tsv", str(regions),
            "--region-ids", region_ids,
            "--window-bp", "10",
            "--out", str(out),
            "--summary", str(summ),
        ])
        assert rc == 0
        return counts["n"], out, summ

    opens_one, _out1, _s1 = run("r1", "one")
    opens_two, out2, summ2 = run("r1,r2", "two")

    assert opens_two == opens_one, (
        f".bim opens grew with region count ({opens_one} -> {opens_two}); "
        "the .bim must be streamed ONCE for all windows"
    )

    rows = list(csv.DictReader(out2.open(), delimiter="\t"))
    assert len(rows) == 2
    assert {r["region_id"] for r in rows} == {"r1", "r2"}
    assert {r["offset"] for r in rows} == {"2", "1"}

    payload = json.loads(summ2.read_text())
    assert set(payload) == {"r1", "r2"}
    for s in payload.values():
        assert set(s) == set(pcs.SUMMARY_KEYS)
        assert s["n_candidate_rows"] == 1


def test_cli_cache_variants_one_is_byte_identical(tmp_path):
    """A MEMORY knob must not be a CORRECTNESS knob."""
    import filecmp

    import pairwise_completeness_scan as pcs

    base = _multi_region_bfile(tmp_path, prefix="cli3")
    regions = _regions_tsv(tmp_path, name="regions3.tsv")

    outs = []
    for tag, cache in (("dflt", None), ("one", "1")):
        out = tmp_path / f"pairs_{tag}.tsv"
        argv = [
            "--bfile-prefix", str(base),
            "--regions-tsv", str(regions),
            "--region-ids", "r1,r2",
            "--window-bp", "10",
            "--out", str(out),
        ]
        if cache is not None:
            argv += ["--cache-variants", cache]
        assert pcs.main(argv) == 0
        outs.append(out)

    assert filecmp.cmp(outs[0], outs[1], shallow=False)
    assert outs[0].read_text() == outs[1].read_text()


def test_cli_missing_bfile_exits_nonzero_and_writes_no_partial_tsv(tmp_path, capsys):
    """A missing component exits NON-ZERO, names the path, and writes NOTHING."""
    import pairwise_completeness_scan as pcs

    base = _joint_table_bfile(tmp_path, _MIRROR_00057_CELLS, prefix="cli4")
    base.with_suffix(".bed").unlink()
    out = tmp_path / "should_not_exist.tsv"

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--region-id", "R", "--chr", "15",
        "--from-bp", "20394700", "--to-bp", "20394800",
        "--out", str(out),
    ])
    assert rc != 0
    assert not out.exists(), "a partial TSV was written despite a missing input"
    captured = capsys.readouterr()
    assert ".bed" in (captured.err + captured.out)
    assert str(base.with_suffix(".bed")) in (captured.err + captured.out)


def test_cli_help_mentions_measurement_window(capsys):
    """``--help`` exits 0 and says ``--window-bp`` is a MEASUREMENT window."""
    import pairwise_completeness_scan as pcs

    with pytest.raises(SystemExit) as exc:
        pcs.main(["--help"])
    assert exc.value.code == 0
    text = capsys.readouterr().out
    assert "MEASUREMENT window" in text
    assert "not a threshold" in text


# =========================================================================== #
# quick-260825-qpf — REMEDIATION of the Codex adversarial review              #
#                                                                             #
# T1: F6 the normalised seek index · F4 the index-based pair key ·            #
#     F5 the exact af_a1 == 0.5 minor-allele tie                              #
# Every assertion below was SEEN RED against the shipped module first.        #
# =========================================================================== #

#: The module's own source file, read TEXTUALLY by the named enforcers. A SYMBOL
#: pin, never a fixed-SHA whole-file pin
#: (``feedback_fixed_sha_whole_file_pin_is_a_timebomb``).
_PCS_SOURCE = _SRC_PYTHON / "pairwise_completeness_scan.py"


def _codes(dosage_strings) -> list[int]:
    """``--recode A`` dosage strings -> .bed 2-bit codes, in sample order."""
    return [_DOSAGE_STR_TO_CODE[s] for s in dosage_strings]


# --------------------------------------------------------------------------- #
# F6 — the seek offset must use the BOUNDS-CHECKED index, not the raw argument #
# --------------------------------------------------------------------------- #

def test_read_variant_accepts_a_coercible_index(tmp_path):
    """``"1"`` and ``1.0`` must read the SAME block as ``1``.

    RED against the shipped module: bounds were checked on ``idx = int(index)``
    but the seek was computed from the RAW ``index``, so ``3 + "1" * bpv`` is a
    ``str`` (``int + str`` -> ``TypeError``) and ``3 + 1.0 * bpv`` is a ``float``
    (``seek(float)`` -> ``TypeError``).

    Each coercion is read on its OWN reader. Sharing one reader would let the
    LRU decode cache (keyed on the NORMALISED index) serve the answer without
    ever computing an offset, which would mask the defect entirely.
    """
    import pairwise_completeness_scan as pcs

    n_samples = 8
    base = _write_bfile(
        tmp_path,
        codes_per_variant=[_distinguishable_codes(i, n_samples) for i in range(3)],
        n_samples=n_samples,
        prefix="coercible",
    )

    with pcs.BedReader(base) as reader_int:
        expected = np.array(reader_int.read_variant(1).dosage)
        other = np.array(reader_int.read_variant(0).dosage)
    # the fixture must actually be able to tell the blocks apart
    assert not np.array_equal(expected, other)

    with pcs.BedReader(base) as reader_str:
        got_str = np.array(reader_str.read_variant("1").dosage)
    with pcs.BedReader(base) as reader_float:
        got_float = np.array(reader_float.read_variant(1.0).dosage)

    assert np.array_equal(got_str, expected)
    assert np.array_equal(got_float, expected)


def test_read_variant_rejects_a_non_integral_index(tmp_path):
    """A NON-INTEGRAL index must RAISE ``ValueError`` naming it — never truncate.

    This is the one that matters. Once F6 is fixed, a bare ``int(1.5) == 1``
    would seek to variant 1 and return a perfectly well-formed dosage array for
    the WRONG VARIANT, with no error anywhere — exactly the failure class the
    module's GLOBAL-INDEX rule exists to prevent
    (cf. ``test_window_relative_index_reads_the_wrong_block``).

    RED against the shipped module for the RIGHT reason: it raises a ``TypeError``
    from deep inside ``file.seek()`` as an ACCIDENT of the very defect F6 fixes,
    not as a deliberate, named rejection. Pinning the TYPE and the MESSAGE is what
    makes the rejection survive the fix.
    """
    import pairwise_completeness_scan as pcs

    base = _write_bfile(
        tmp_path,
        codes_per_variant=[_distinguishable_codes(i, 8) for i in range(3)],
        n_samples=8,
        prefix="nonintegral",
    )
    with pcs.BedReader(base) as reader:
        with pytest.raises(ValueError, match="non-integral"):
            reader.read_variant(1.5)


def test_seek_offset_uses_the_normalised_index():
    """NAMED TEXTUAL ENFORCER: the bounds-checked quantity IS the addressed one.

    ``feedback_a_claimed_invariant_needs_a_named_enforcer`` — an invariant with
    no enforcer is a belief. Comment-insensitive on the SYMBOL.
    """
    src = _PCS_SOURCE.read_text()
    assert src.count("3 + idx * self.bytes_per_variant") == 1, (
        "the .bed seek offset must be computed from the NORMALISED index `idx`"
    )
    assert "3 + index * self.bytes_per_variant" not in src, (
        "the raw `index` argument must never reach the seek arithmetic"
    )


# --------------------------------------------------------------------------- #
# F4 — the pair key must be the GLOBALLY-UNIQUE .bim row indices               #
# --------------------------------------------------------------------------- #

def _duplicate_id_bfile(tmp_path: Path, prefix: str = "dupid") -> Path:
    """One deletion + TWO distinct partner rows that BOTH carry the id ``.``.

    A bare ``.`` in the id column is a real, common ``.bim`` occurrence. The two
    partners sit at DIFFERENT positions, and exactly one of the two pairs is
    UNDEFINED, so a key that collapses them is visible in the counts.

      idx 0  1:1000 REF ``AT`` ALT ``A``  -> a 1 bp deletion, span_end 1001
      idx 1  1:1003 id ``.``              -> no-called at BOTH deletion carriers
                                             => the deletion is invariant in the
                                             intersection => UNDEFINED
      idx 2  1:1005 id ``.``              -> fully called, both members variable
                                             => DEFINED
    """
    deletion = ["0", "0", "0", "0", "1", "1", "0", "0"]
    partner_a = ["0", "1", "0", "1", "NA", "NA", "0", "1"]
    partner_b = ["0", "1", "0", "1", "1", "0", "1", "0"]
    return _write_bfile(
        tmp_path,
        codes_per_variant=[_codes(deletion), _codes(partner_a), _codes(partner_b)],
        n_samples=8,
        prefix=prefix,
        bim_rows=[
            ["1", "1:1000:AT:A", "0", "1000", "A", "AT"],
            ["1", ".", "0", "1003", "C", "T"],
            ["1", ".", "0", "1005", "G", "A"],
        ],
    )


def _scan_duplicate_id_fixture(pcs, tmp_path: Path, prefix: str = "dupid"):
    base = _duplicate_id_bfile(tmp_path, prefix=prefix)
    rows = pcs.load_bim_rows(base.with_suffix(".bim"))
    reader = pcs.BedReader(base)
    try:
        return pcs.scan_region(reader, "R", list(enumerate(rows)), window_bp=5)
    finally:
        reader.close()


def test_duplicate_variant_ids_do_not_collapse_distinct_pairs(tmp_path):
    """TWO partner rows sharing the id ``.`` are TWO pairs, not one.

    RED against the shipped vid-keyed implementation, which reported
    ``n_distinct_pairs == 1`` — an UNDERCOUNT, which is the dangerous direction:
    it makes the instrument report FEWER distinct pairs than exist and would
    deflate any denominator derived from it.
    """
    import pairwise_completeness_scan as pcs

    results = _scan_duplicate_id_fixture(pcs, tmp_path)
    assert len(results) == 2
    assert sum(1 for r in results if r.undefined) == 1

    summary = pcs.summarize("R", results, n_deletions=1, n_candidates_edge_clipped=0)
    assert summary["n_candidate_rows"] == 2
    assert summary["n_distinct_pairs"] == 2
    assert summary["n_undefined_distinct_pairs"] == 1
    assert summary["n_undefined_not_already_occluded"] == 1


def test_pair_key_names_the_rows_it_keys(tmp_path):
    """MUST-BE-IDENTITY: the key IS the two row indices it is derived from.

    Not a "looks right" check — the key is decomposed and compared to the row's
    own ``del_index``/``partner_index``.
    """
    import pairwise_completeness_scan as pcs

    results = _scan_duplicate_id_fixture(pcs, tmp_path, prefix="dupidkey")
    assert results, "fixture emitted no rows"
    for r in results:
        assert sorted(int(x) for x in r.pair_key.split("|")) == sorted(
            [r.del_index, r.partner_index]
        )


# --------------------------------------------------------------------------- #
# F5 — the EXACT af_a1 == 0.5 tie must report the LARGER carrier loss          #
# --------------------------------------------------------------------------- #

#: THE TAIL-HIDING FIXTURE. 8 samples; the deletion's A1 dosages are
#: ``[2, 2, 2, 2, 0, 0, 0, 0]`` so ``af_a1 = 8 / (2 * 8) = 0.5`` EXACTLY — 0.5 is
#: exactly representable in binary floating point, so this is an equality, not a
#: near-miss. The partner is no-called at 3 of the 4 A2-carriers and called at all
#: four A1-carriers, and stays VARIABLE inside the intersection so the pair is
#: DEFINED (there is no NaN here for anything downstream to catch).
#:
#:   A1-carriers (dosage >= 1) = samples 0-3, lost 0  -> lost_frac 0.00  (OLD)
#:   A2-carriers (dosage <= 1) = samples 4-7, lost 3  -> lost_frac 0.75  (NEW)
_EXACT_TIE_CELLS = {
    ("2", "0"): 2,
    ("2", "1"): 2,
    ("0", "NA"): 3,
    ("0", "0"): 1,
}


def test_exact_allele_frequency_tie_reports_the_larger_carrier_loss(tmp_path):
    """At ``af_a1 == 0.5`` the gradient must track the DEPLETED allele.

    RED against the shipped ``if af_a1 <= 0.5`` rule, which picked A1 by fiat and
    reported ``del_carriers_lost_frac == 0.0`` — a REASSURING number for a member
    whose other allele lost 3 of its 4 carriers to the partner's missingness.
    That is precisely the partial-confounding tail this instrument exists to find,
    and the shipped rule binned it as ``"0"``.
    """
    import pairwise_completeness_scan as pcs

    pr = _single_pair_result(pcs, tmp_path, _EXACT_TIE_CELLS, prefix="exacttie")

    # the fixture really is at the exact tie
    assert pr.del_maf_marginal == 0.5
    assert pr.n_called_del == 8
    assert pr.n_both_called == 5

    assert pr.undefined is False, "the pair must stay DEFINED — this is the tail"
    assert pr.del_carriers_marginal == 4
    assert pr.del_carriers_retained == 1
    assert pr.del_carriers_lost == 3
    assert pr.del_carriers_lost_frac == 0.75
    assert pr.del_minor_allele_tie is True
    assert pr.partner_minor_allele_tie is False

    summary = pcs.summarize("R", [pr], n_deletions=1, n_candidates_edge_clipped=0)
    assert summary["defined_carriers_lost_frac_bins"]["(0.5,0.9]"] == 1
    assert summary["defined_carriers_lost_frac_bins"]["0"] == 0
    assert summary["max_carriers_lost_frac_defined"] == 0.75


def test_no_tie_flag_when_the_minor_allele_is_unambiguous(tmp_path):
    """An ordinary pair reports both tie flags FALSE.

    Without this, ``minor_allele_tie is True`` could be a constant and the tie
    column would carry no information.
    """
    import pairwise_completeness_scan as pcs

    pr = _single_pair_result(pcs, tmp_path, _MIRROR_00057_CELLS, prefix="notie")
    assert pr.del_maf_marginal != 0.5
    assert pr.partner_maf_marginal != 0.5
    assert pr.del_minor_allele_tie is False
    assert pr.partner_minor_allele_tie is False


# =========================================================================== #
# quick-260825-qpf — T2: make the two SILENT COUPLINGS visible                 #
#                                                                             #
# F2 region-edge clipping (REPORTED, not changed) · the --mac 1 retained-set   #
# parity class · F1 the --nonfounders coupling (PINNED, not changed) ·         #
# F7 explicit-or-raise summary denominators.                                   #
# Nothing here changes what the scanner DECIDES. It changes what it REPORTS.   #
# =========================================================================== #

def _region_tsv(
    tmp_path: Path, specs, name: str = "regions_qpf.tsv", ancestry: str = "AFR"
) -> Path:
    """A ``config/ld_regions.tsv``-shaped file from ``[(id, chr, start, end)]``.

    Column 7 (0-based 6) carries ``ancestry`` — the real manifest's second key
    (quick-260826-qq9); see :func:`_regions_tsv`.
    """
    path = tmp_path / name
    header = ["c%d" % i for i in range(1, 17)]
    header[0], header[1], header[6] = "region_id", "chr", "ancestry"
    header[14], header[15] = "window_start_grch38", "window_end_grch38"
    rows = [header]
    for rid, chrom, start, end in specs:
        row = ["."] * 16
        row[0], row[1], row[6] = rid, chrom, ancestry
        row[14], row[15] = str(start), str(end)
        rows.append(row)
    path.write_text("".join("\t".join(r) + "\n" for r in rows))
    return path


#: The region under test in the edge-clip fixtures, INCLUSIVE on both bounds.
_EDGE_REGION = (1000, 1010)


def _edge_clip_bfile(tmp_path: Path, *, third_bp: int, prefix: str) -> Path:
    """A deletion at the region's LEFT edge, an in-region partner, and a third row.

      idx 0  chr1:1000 REF ``AT`` ALT ``A``  -> a 1 bp deletion, span_end 1001,
                                                INSIDE ``_EDGE_REGION``
      idx 1  chr1:1005 SNP                   -> INSIDE the region
      idx 2  chr1:``third_bp`` SNP           -> OUTSIDE the region. At 1011 it is
                                                one bp past ``to_bp`` and INSIDE
                                                the deletion's +/-25 bp reach, so
                                                the region boundary suppresses it.
    """
    n = 16
    return _write_bfile(
        tmp_path,
        codes_per_variant=[
            [_CODE_HOM_A2] * 12 + [_CODE_HET] * 2 + [_CODE_MISSING] * 2,
            [_CODE_HOM_A2] * 10 + [_CODE_HET] * 6,
            [_CODE_HOM_A2] * 9 + [_CODE_HET] * 7,
        ],
        n_samples=n,
        prefix=prefix,
        bim_rows=[
            _bim_row("chr1", 1000, "AT", "A"),
            _bim_row("chr1", 1005, "T", "C"),
            _bim_row("chr1", third_bp, "G", "A"),
        ],
    )


def _run_edge_cli(pcs, tmp_path: Path, *, third_bp: int, tag: str, window_bp: int = 25):
    """Run the CLI over ``_EDGE_REGION`` and return ``(rows, summary)``."""
    import csv
    import json

    base = _edge_clip_bfile(tmp_path, third_bp=third_bp, prefix=f"edge{tag}")
    regions = _region_tsv(
        tmp_path, [("edge", "1", _EDGE_REGION[0], _EDGE_REGION[1])], name=f"reg_{tag}.tsv"
    )
    out = tmp_path / f"pairs_{tag}.tsv"
    summ = tmp_path / f"summary_{tag}.json"
    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "edge",
        "--window-bp", str(window_bp),
        "--out", str(out),
        "--summary", str(summ),
    ])
    assert rc == 0
    rows = list(csv.DictReader(out.open(), delimiter="\t"))
    return rows, json.loads(summ.read_text())["edge"]


# --------------------------------------------------------------------------- #
# F2 — the BEHAVIOUR-PRESERVATION guard comes FIRST, then the counter          #
# --------------------------------------------------------------------------- #

def test_no_emitted_row_references_a_variant_outside_the_region(tmp_path):
    """The region's universe is EXACTLY the region's own matrix, still.

    The edge-clip counter is fed by a PADDED ``.bim`` read. This is the assertion
    that proves the padding is only ever COUNTED and never LEAKS an out-of-region
    pair into the output — a variant outside ``[from_bp, to_bp]`` is not a row of
    that region's LD matrix and cannot produce a NaN there.

    Seen red against a scratch copy that emitted the padded partners.
    """
    import pairwise_completeness_scan as pcs

    rows, _summary = _run_edge_cli(pcs, tmp_path, third_bp=1011, tag="bounds")
    assert rows, "fixture emitted no rows"
    lo, hi = _EDGE_REGION
    for r in rows:
        assert lo <= int(r["del_pos"]) <= hi, r
        assert lo <= int(r["partner_pos"]) <= hi, r


def test_edge_clipped_candidates_are_counted_not_silently_absent(tmp_path):
    """A partner ONE BP past ``to_bp`` is suppressed — and now COUNTED.

    RED: ``n_candidates_edge_clipped`` did not exist, so the suppression was
    invisible and a region-edge deletion looked like a deletion with fewer
    neighbours. The review filed this as a HIGH; it is re-dispositioned to
    REPORTED-not-CHANGED because the clipping itself is CORRECT (see the guard
    above), and the defect was the SILENCE.
    """
    import pairwise_completeness_scan as pcs

    rows, summary = _run_edge_cli(pcs, tmp_path, third_bp=1011, tag="clip")

    assert summary["n_candidates_edge_clipped"] == 1
    assert summary["n_candidate_rows"] == 1          # hand-counted: del 1000 x snp 1005
    assert summary["n_deletions"] == 1
    assert all(r["partner_pos"] != "1011" for r in rows)
    assert all("1011" != r["del_pos"] for r in rows)


def test_no_edge_clipping_reports_zero(tmp_path):
    """An interior-only fixture reports 0 — the counter is not a constant."""
    import pairwise_completeness_scan as pcs

    # 2000 is outside the region AND outside the deletion's +/-25 bp reach.
    _rows, summary = _run_edge_cli(pcs, tmp_path, third_bp=2000, tag="noclip")
    assert summary["n_candidates_edge_clipped"] == 0
    assert summary["n_candidate_rows"] == 1


# --------------------------------------------------------------------------- #
# The `--mac 1` / RETAINED-SET PARITY class, counted so it is SUBTRACTABLE     #
# --------------------------------------------------------------------------- #

#: A partner that is ALL HOM-REF across its entire called set: invariant within
#: its OWN called set, independent of any partner. The deletion is variable.
_GLOBALLY_INVARIANT_CELLS = {
    ("0", "0"): 5,
    ("1", "0"): 3,
}


def test_globally_invariant_variant_is_reported_separately(tmp_path):
    """A member invariant in its OWN called set is FLAGGED and COUNTED.

    RED: neither the columns nor the two summary keys existed. The production
    matrix is built on the RETAINED set (post ``--exclude``, post ``--mac 1``)
    while this scanner enumerates the full window ``.bim``, so such a variant makes
    every pair containing it read as undefined — an OVER-report. Counting the class
    is what makes it SUBTRACTABLE instead of a finding.
    """
    import pairwise_completeness_scan as pcs

    pr = _single_pair_result(pcs, tmp_path, _GLOBALLY_INVARIANT_CELLS, prefix="globinv")
    assert pr.partner_globally_invariant is True
    assert pr.del_globally_invariant is False
    assert pr.undefined is True
    assert pr.invariant_member == "partner"

    summary = pcs.summarize("R", [pr], n_deletions=1, n_candidates_edge_clipped=0)
    assert summary["n_globally_invariant_variants"] == 1
    assert summary["n_undefined_rows_with_globally_invariant_member"] == 1


def test_ordinary_variants_are_not_globally_invariant(tmp_path):
    """The MEASURED 00057 mirror is UNDEFINED with NO globally invariant member.

    This is the separation that matters: the 00057 pair is undefined because the
    deletion is constant WITHIN THE INTERSECTION, while both members are perfectly
    variable within their own called sets. A counter that just re-counted
    ``undefined`` would report 1 here.
    """
    import pairwise_completeness_scan as pcs

    pr = _single_pair_result(pcs, tmp_path, _MIRROR_00057_CELLS, prefix="notglobinv")
    assert pr.undefined is True
    assert pr.del_globally_invariant is False
    assert pr.partner_globally_invariant is False

    summary = pcs.summarize("R", [pr], n_deletions=1, n_candidates_edge_clipped=0)
    assert summary["n_undefined_rows"] == 1
    assert summary["n_globally_invariant_variants"] == 0
    assert summary["n_undefined_rows_with_globally_invariant_member"] == 0


# --------------------------------------------------------------------------- #
# F1 — the --nonfounders COUPLING, with a named CROSS-MODULE enforcer          #
# --------------------------------------------------------------------------- #

def test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag():
    """READ-ONLY cross-module SYMBOL pin on ``build_plink_ld_command``'s square branch.

    plink1.9 LD considers FOUNDERS ONLY by default. This scanner counts ALL
    ``.fam`` rows, which is the MATCHING policy only because the production square
    command passes ``--nonfounders``. If that flag is ever dropped, the scanner's
    verdicts stop being comparable to the matrix they are about — so the coupling
    gets an enforcer instead of a sentence.

    The pin is on the ARGV the function BUILDS, parsed with ``ast``, not on the
    file's text: the in-code comment beside that line also contains the string
    ``--nonfounders``, so a textual grep would stay green with the flag deleted
    from the command. It is a SYMBOL pin, never a fixed-SHA whole-file pin
    (``feedback_fixed_sha_whole_file_pin_is_a_timebomb``).

    ``src/python/aou_ld_panel.py`` is READ here and is NEVER written by this plan.
    """
    import ast

    import pairwise_completeness_scan as pcs

    panel = _SRC_PYTHON / "aou_ld_panel.py"
    assert panel.exists(), panel
    tree = ast.parse(panel.read_text())
    fns = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "build_plink_ld_command"
    ]
    assert len(fns) == 1, f"expected exactly one build_plink_ld_command, got {len(fns)}"

    square_branches = [
        n for n in ast.walk(fns[0])
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Compare)
        and len(n.test.ops) == 1
        and isinstance(n.test.ops[0], ast.Eq)
        and isinstance(n.test.comparators[0], ast.Constant)
        and n.test.comparators[0].value == "square"
    ]
    assert len(square_branches) == 1, (
        f"expected exactly one `mode == \"square\"` branch, got {len(square_branches)}"
    )
    emitted = {
        c.value
        for stmt in square_branches[0].body
        for c in ast.walk(stmt)
        if isinstance(c, ast.Constant) and isinstance(c.value, str)
    }
    assert "--r" in emitted and "square" in emitted, emitted
    assert "--nonfounders" in emitted, (
        "the production square LD command no longer passes --nonfounders; plink1.9 "
        "LD is FOUNDERS-ONLY by default, so this scanner's all-samples policy is no "
        "longer the matching one and its verdicts are not comparable. Switch the "
        "scanner to founders-only or restore the flag."
    )

    doc = pcs.__doc__ or ""
    assert "--nonfounders" in doc
    assert "founders" in doc.lower()
    assert "test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag" in doc


# --------------------------------------------------------------------------- #
# F7 — EXPLICIT-OR-RAISE denominators                                          #
# --------------------------------------------------------------------------- #

def test_summarize_requires_its_denominators():
    """``summarize`` must RAISE rather than invent a denominator from the rows.

    RED: it defaulted ``n_deletions`` to the number of DISTINCT ``del_index``
    values in ``results``, so a region holding an isolated deletion with no
    candidate partner (``results == []``) was summarised as ``n_deletions == 0``.
    That is not a missing number, it is a WRONG one, and it is the denominator any
    later per-deletion arithmetic would divide by.
    """
    import pairwise_completeness_scan as pcs

    with pytest.raises(TypeError, match="n_deletions"):
        pcs.summarize("R", [])
    with pytest.raises(TypeError, match="n_candidates_edge_clipped"):
        pcs.summarize("R", [], n_deletions=1)

    # ... and the explicit form reports what it was TOLD, not what it inferred.
    s = pcs.summarize("R", [], n_deletions=1, n_candidates_edge_clipped=0)
    assert s["n_deletions"] == 1
    assert s["n_candidate_rows"] == 0


# =========================================================================== #
# quick-260825-qpf — T3: the plink PAIRWISE-COMPLETE FALSIFIER in the runbook, #
# and the R6 governance amendment                                             #
# =========================================================================== #

_PENDING_PASTE = PROJECT_ROOT / ".planning" / "debug" / (
    "260825-PENDING-PASTE-pairwise-completeness-sweep.md"
)

#: The three step headings whose ORDER is the load-bearing property: the
#: instrument's premise must be tested BEFORE the harness cross-check and BEFORE
#: any number is generated.
_STEP_FALSIFIER = "=== STEP 1 — THE plink PAIRWISE-COMPLETE FALSIFIER"
_STEP_CROSSCHECK = "=== STEP 2 — THE 00057 HARNESS CROSS-CHECK"
_STEP_SWEEP = "=== STEP 3 — THE SWEEP"

#: The three runbooks that cite "R6's occ_measure/ allowance". Two of the three
#: WRAP the citation across a newline, so a one-line grep finds only ONE of them
#: (MEASURED). Every check below is newline-tolerant.
_R6_CITING_RUNBOOKS = (
    ".planning/debug/260819-PENDING-PASTE-2-samepos-and-chain.md",
    ".planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md",
    ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md",
)

_OX1_AGENT_PROMPT = PROJECT_ROOT / ".planning" / "quick" / (
    "260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r"
) / "260812-ox1-AGENT-PROMPT.md"


def test_pending_paste_carries_the_falsifier_tokens():
    """The falsifier's load-bearing tokens are all present in the runbook.

    RED: the paste had no falsifier at all. These are the tokens that make the
    experiment reproducible from the paste alone — the three competing hypotheses,
    the production LD modifiers, and the PINNED plink build the VM must be running.
    """
    text = _PENDING_PASTE.read_text()
    for needle in (
        "pairwise-complete",
        "mean-imputation",
        "listwise",
        "--write-snplist",
        "--mac 1",
        "--nonfounders",
        "--keep-allele-order",
        "--extract",
        "plink1.9 --version",
        "v1.90b7.2",
        "DISCARD THE SWEEP",
        "founder",
        ".snplist",
        "retention",
    ):
        assert needle in text, f"PENDING PASTE is missing the falsifier token {needle!r}"


def test_pending_paste_runs_the_falsifier_before_the_crosscheck_and_the_sweep():
    """ORDER IS THE POINT: falsify the premise BEFORE producing any number.

    A falsifier placed after the sweep would be a post-hoc rationalisation. RED:
    STEP 1 was the 00057 cross-check and no falsifier existed.

    Every pre-existing needle must survive the rewrite — the cross-check and the
    sweep are MOVED and RENUMBERED, never dropped.
    """
    text = _PENDING_PASTE.read_text()
    for heading in (_STEP_FALSIFIER, _STEP_CROSSCHECK, _STEP_SWEEP):
        assert heading in text, f"missing step heading {heading!r}"
    assert (
        text.index(_STEP_FALSIFIER)
        < text.index(_STEP_CROSSCHECK)
        < text.index(_STEP_SWEEP)
    ), "the falsifier must come BEFORE the cross-check, which comes BEFORE the sweep"

    for needle in (
        "--- PASTE FROM HERE ---",
        "--- PASTE ENDS HERE ---",
        "71048",
        "871",
        "20394741",
        "20394743",
        "occ_measure_sample.tsv",
        "m2_region_00057",
        "DISCARD ALL",
    ):
        assert needle in text, f"PENDING PASTE lost the pre-existing needle {needle!r}"

    # No orphaned pointer at the OLD step numbering: the STEP 1 consequence must
    # forbid BOTH later steps by name. NEWLINE-TOLERANT — the sentence wraps in
    # the rendered runbook, and pinning the line break would be pinning a proxy
    # (``feedback_scope_a_guard_to_the_property_not_a_proxy``).
    import re

    assert "Do not skip STEP 1." in text
    assert re.search(r"Do NOT run STEP 2\.\s+Do\s+NOT run STEP 3\.", text), (
        "STEP 1's discard consequence must name BOTH STEP 2 and STEP 3"
    )


def test_pending_paste_no_longer_claims_it_calls_no_plink():
    """NEGATIVE NEEDLE — a retracted claim must be GONE, not merely contradicted.

    RED: ``"This sweep calls no plink at all"`` appeared TWICE (MEASURED) — once in
    the header prose and once in the PATH bullet, where it demoted the per-shell
    ``export PATH="$HOME/bin:$PATH"`` off the critical path. STEP 1 calls plink1.9
    three times, so both occurrences are false and the PATH export is REQUIRED.
    """
    text = _PENDING_PASTE.read_text()
    assert "calls no plink at all" not in text
    assert 'export PATH="$HOME/bin:$PATH"' in text
    assert "REQUIRED FIRST ACTION" in text


def test_r6_records_the_occ_measure_allowance_and_all_three_runbooks_cite_it():
    """The rule and its citations must AGREE — a cited rule that does not exist
    is an unenforceable permission, and agents act on the citation.

    RED: ``grep -c occ_measure`` on ``260812-ox1-AGENT-PROMPT.md`` was 0 (MEASURED)
    while THREE runbooks cited "R6's occ_measure/ allowance".

    The assertion is scoped to the ``^R6.`` ... ``^R7.`` BLOCK, not the whole file
    (``feedback_scope_a_guard_to_the_property_not_a_proxy``): the property is that
    R6 ITSELF names the directory, and a mention anywhere else in the file would
    satisfy a whole-file grep without satisfying the property.
    """
    import re

    text = _OX1_AGENT_PROMPT.read_text()
    match = re.search(r"^R6\.(.*?)^R7\.", text, re.S | re.M)
    assert match, "could not locate the R6 block in the ox1 AGENT-PROMPT"
    block = match.group(1)
    assert "occ_measure" in block, (
        "R6 still does not name /home/jupyter/occ_measure/, yet three runbooks "
        "cite 'R6's occ_measure/ allowance'"
    )
    assert "2026-08-25" in block and "quick-260825-qpf" in block, (
        "the R6 addition must carry its dated provenance"
    )

    for rel in _R6_CITING_RUNBOOKS:
        runbook = (PROJECT_ROOT / rel).read_text()
        # NEWLINE-TOLERANT: two of the three wrap the citation across a line break,
        # so a naive one-line grep finds only ONE of them (MEASURED).
        assert re.search(r"R6's\s+occ_measure/", runbook), (
            f"{rel} no longer cites R6's occ_measure/ allowance"
        )


# =========================================================================== #
# quick-260826-qq9 — T1: THE MANIFEST IS KEYED ON (region_id x ancestry)      #
#                                                                             #
# ``config/ld_regions.tsv`` is 553 lines = 1 header + 276 region_ids x         #
# {AFR, EUR}. The shipped ``_read_regions_tsv`` read 0-based columns 0/1/14/15 #
# ONLY, so it returned EVERY window TWICE. That doubled the ``.bim`` rows,     #
# quadrupled the candidate pairs, and — with the driver's last-wins            #
# ``summaries`` dict against an accumulating ``all_results`` — inflated the    #
# 21-region STEP 3 sweep's row-basis counts by 8x.                             #
#                                                                             #
# Provenance: .planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-      #
# duplication-and-the-prereg-prediction.md                                     #
# =========================================================================== #

#: The REAL manifest. These tests pin the instrument against the file it will
#: actually be run on, not only against synthetic fixtures — the defect was
#: invisible to every synthetic fixture in this file because none of them
#: carried the ancestry column at all.
_REAL_REGIONS_TSV = PROJECT_ROOT / "config" / "ld_regions.tsv"

#: READ-ONLY. Parsed with ``ast`` by the cross-module contract enforcer below;
#: never imported, never written.
_RUN_NATIVE_LD_PANEL = PROJECT_ROOT / "src" / "python" / "run_native_ld_panel.py"


def _ancestry_regions_tsv(tmp_path: Path, specs, name: str = "regions_anc.tsv") -> Path:
    """A ``config/ld_regions.tsv``-shaped file that CARRIES the ancestry column.

    ``specs`` is ``[(region_id, chrom, start, end, ancestry)]``. ``ancestry`` is
    written at 0-based index 6 (1-based column 7), which is where the real
    manifest carries it.
    """
    path = tmp_path / name
    header = ["c%d" % i for i in range(1, 17)]
    header[0], header[1], header[6] = "region_id", "chr", "ancestry"
    header[14], header[15] = "window_start_grch38", "window_end_grch38"
    rows = [header]
    for rid, chrom, start, end, ancestry in specs:
        row = ["."] * 16
        row[0], row[1], row[6] = rid, chrom, ancestry
        row[14], row[15] = str(start), str(end)
        rows.append(row)
    path.write_text("".join("\t".join(r) + "\n" for r in rows))
    return path


def test_read_regions_tsv_reads_the_real_manifest_on_region_id_x_ancestry():
    """THE DIRECT PIN OF THE DEFECT, against the REAL file.

    553 lines = 1 header + 276 x 2. An ancestry-keyed read returns 276 windows
    per ancestry with 276 DISTINCT ids. The shipped code returned 552 for both,
    every id twice.
    """
    import pairwise_completeness_scan as pcs

    lines = _REAL_REGIONS_TSV.read_text().splitlines()
    assert len(lines) == 553, (
        f"config/ld_regions.tsv is {len(lines)} lines, expected 1 header + 276 x 2"
    )

    afr = pcs._read_regions_tsv(_REAL_REGIONS_TSV, None)
    eur = pcs._read_regions_tsv(_REAL_REGIONS_TSV, None, ancestry="EUR")

    assert len(afr) == 276, f"AFR read returned {len(afr)} windows, not 276"
    assert len(eur) == 276, f"EUR read returned {len(eur)} windows, not 276"
    assert len({w[0] for w in afr}) == 276, "AFR windows carry a repeated region_id"
    assert len({w[0] for w in eur}) == 276, "EUR windows carry a repeated region_id"
    assert {w[0] for w in afr} == {w[0] for w in eur}


def test_read_regions_tsv_real_manifest_subset_is_n_windows_not_2n():
    """A ``--region-ids`` subset of N ids yields EXACTLY N windows, never 2N."""
    import pairwise_completeness_scan as pcs

    ids = ["m2_region_00001", "m2_region_00120__sub03", "m2_region_00149"]
    got = pcs._read_regions_tsv(_REAL_REGIONS_TSV, ids)

    assert len(got) == 3, f"3 requested ids returned {len(got)} windows"
    assert {w[0] for w in got} == set(ids)
    assert len({w[0] for w in got}) == 3


def test_read_regions_tsv_returns_the_requested_ancestrys_real_bounds():
    """A COUNT alone cannot prove the RIGHT row was kept — pin the BOUNDS.

    ``m2_region_00120__sub03`` is one of the 123 ids whose AFR window is STRICTLY
    INSIDE its EUR window (EUR pads +/-2 Mb). Because the file order is
    AFR-then-EUR per region, an ancestry-blind read that de-duplicated by
    last-wins would have kept the EUR bounds for BOTH — so this assertion
    separates "the right number of rows" from "the right rows".
    """
    import pairwise_completeness_scan as pcs

    afr = {w[0]: (w[2], w[3]) for w in pcs._read_regions_tsv(_REAL_REGIONS_TSV, None)}
    eur = {
        w[0]: (w[2], w[3])
        for w in pcs._read_regions_tsv(_REAL_REGIONS_TSV, None, ancestry="EUR")
    }

    assert afr["m2_region_00120__sub03"] == (72941765, 83784838)
    assert eur["m2_region_00120__sub03"] == (70941765, 85784838)
    # AFR strictly inside EUR — the reason the 8x duplication was NON-UNIFORM.
    assert eur["m2_region_00120__sub03"][0] < afr["m2_region_00120__sub03"][0]
    assert afr["m2_region_00120__sub03"][1] < eur["m2_region_00120__sub03"][1]
    # ...and one of the 153 ids whose bounds are IDENTICAL in both ancestries.
    assert afr["m2_region_00001"] == eur["m2_region_00001"] == (10000, 13506933)


def test_read_regions_tsv_selects_the_ancestrys_bounds_on_a_synthetic_manifest(tmp_path):
    """Same property, hermetically: the default selects AFR, ``--ancestry EUR``
    selects the wider EUR row, and NEITHER returns both."""
    import pairwise_completeness_scan as pcs

    regions = _ancestry_regions_tsv(
        tmp_path,
        [
            ("r1", "1", 1000, 2000, "AFR"),
            ("r1", "1", 500, 2500, "EUR"),
            ("r2", "chr1", 5000, 6000, "AFR"),
            ("r2", "chr1", 4500, 6500, "EUR"),
        ],
    )

    afr = pcs._read_regions_tsv(regions, None)
    eur = pcs._read_regions_tsv(regions, None, ancestry="EUR")

    assert afr == [("r1", "1", 1000, 2000), ("r2", "chr1", 5000, 6000)]
    assert eur == [("r1", "1", 500, 2500), ("r2", "chr1", 4500, 6500)]
    # lowercase is accepted, exactly as production's uppercase match accepts it
    assert pcs._read_regions_tsv(regions, None, ancestry="afr") == afr


def test_default_ancestry_is_afr_in_the_module_and_in_the_parser():
    """The default is LOAD-BEARING: it is what makes the already-written,
    UNMODIFIED STEP 3 sweep command correct (see the companion test below)."""
    import pairwise_completeness_scan as pcs

    assert pcs.DEFAULT_ANCESTRY == "AFR"
    actions = [a for a in pcs._build_parser()._actions if a.dest == "ancestry"]
    assert len(actions) == 1, "--ancestry is missing from the parser"
    assert actions[0].default == "AFR"


def test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing():
    """THE PASTE IS NOT EDITED — the DEFAULT is what makes it correct.

    ``.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`` STEP 3
    invokes the scanner with ``--regions-tsv config/ld_regions.tsv`` and NO
    ``--ancestry`` token. That command is correct UNMODIFIED if and only if the
    default is ``AFR`` — the AFR cohort is what ``/home/jupyter/afr_cohort``
    holds. Both halves are asserted here, because either alone is satisfiable by
    the wrong code: the token count is green against the shipped (defective)
    scanner, and the default alone says nothing about the paste.
    """
    import pairwise_completeness_scan as pcs

    text = _PENDING_PASTE.read_text()
    assert "=== STEP 3" in text, "the STEP 3 block is gone from the PENDING PASTE"
    assert '"--regions-tsv", "config/ld_regions.tsv"' in text
    assert text.count("--ancestry") == 0, (
        "the PENDING PASTE now names --ancestry; it is a received/pending runbook "
        "and this plan does not edit it"
    )
    assert pcs.DEFAULT_ANCESTRY == "AFR", (
        "the unmodified STEP 3 command passes no --ancestry, so the default IS "
        "the ancestry the sweep measures"
    )


def test_ancestry_predicate_agrees_with_the_production_filter_contract():
    """The ancestry predicate is MIRRORED from production, never invented.

    ``run_native_ld_panel._filter_ancestry`` is the contract every AoU LD-panel
    run already uses to split ``config/ld_regions.tsv`` into its AFR and EUR
    halves. The scanner MUST agree with it exactly, or the instrument measures a
    different row set than the panel it is measuring.

    The contract is read AT CALL TIME: parse ``run_native_ld_panel.py`` with
    ``ast``, take ONLY the ``_filter_ancestry`` FunctionDef via
    ``ast.get_source_segment``, and ``exec`` it in an EMPTY namespace. The module
    is never imported — importing would pull a heavy dependency set AND could be
    served from a stale ``.pyc``
    (``feedback_negative_control_defeated_by_bytecode_cache``). This is a SYMBOL
    pin, not a fixed-SHA whole-file pin
    (``feedback_fixed_sha_whole_file_pin_is_a_timebomb``): it survives every edit
    to that file except one that changes THIS predicate.

    NOTE ON WHITESPACE — the property is scoped deliberately. Production does NOT
    strip: ``"  AFR  ".upper() != "AFR"``, so a whitespace-padded manifest cell is
    DROPPED. ``_matches_ancestry`` mirrors that exactly. Whitespace tolerance in
    the scanner lives one layer UP, in ``_tsv_field``, which strips the cell
    before the predicate ever sees it — so the composite parse is tolerant while
    the predicate stays a byte-faithful mirror. Putting the ``.strip()`` in the
    predicate instead would make this enforcer FAIL on exactly one of the 16
    cases below (MEASURED).
    """
    import ast

    import pairwise_completeness_scan as pcs

    source = _RUN_NATIVE_LD_PANEL.read_text()
    tree = ast.parse(source)
    fn = next(
        (
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "_filter_ancestry"
        ),
        None,
    )
    assert fn is not None, (
        "run_native_ld_panel._filter_ancestry is GONE — the scanner's ancestry "
        "predicate no longer has a production contract to mirror"
    )
    segment = ast.get_source_segment(source, fn)
    assert segment is not None and segment.lstrip().startswith("def _filter_ancestry")
    namespace: dict = {}
    exec(compile(segment, "<_filter_ancestry contract>", "exec"), namespace)
    production = namespace["_filter_ancestry"]

    row_values = ["AFR", "afr", "  AFR  ", "EUR", "eur", "", ".", "nan"]
    disagreements = []
    for row_value in row_values:
        for ancestry in ("AFR", "EUR"):
            expected = len(production([{"ancestry": row_value}], ancestry)) == 1
            actual = pcs._matches_ancestry(row_value, ancestry)
            if actual is not expected:
                disagreements.append((row_value, ancestry, expected, actual))
    assert not disagreements, (
        "_matches_ancestry diverges from run_native_ld_panel._filter_ancestry on "
        f"(row_value, ancestry, production, scanner): {disagreements}"
    )

    # the predicate must be a BOOL, not a truthy list, so the comparison above is
    # an identity comparison and not an accidental pass on `[] == False`
    assert pcs._matches_ancestry("AFR", "AFR") is True
    assert pcs._matches_ancestry("EUR", "AFR") is False

    # the FAIL-SAFE shape: a MISSING ancestry yields "" and is DROPPED, never raised
    assert production([{}], "AFR") == []
    assert pcs._matches_ancestry("", "AFR") is False

    # non-str row values go through str() on BOTH sides, never raise
    for odd in (None, float("nan"), 0):
        assert pcs._matches_ancestry(odd, "AFR") is (
            len(production([{"ancestry": odd}], "AFR")) == 1
        )


def test_region_only_in_the_unrequested_ancestry_raises_naming_the_id(tmp_path):
    """A LOUD ERROR, never a silent drop — AND THE ASSERTION NOW MEANS IT.

    ``seen`` accumulates ONLY rows that pass the ancestry filter, so asking for a
    region that exists only as EUR while reading AFR hits the pre-existing
    ``region ids not found in`` error instead of quietly returning an empty
    window list.

    THIS TEST WAS A FALSE INVARIANT UNTIL quick-260828-uej. Its fixture was
    ``name="eur_only.tsv"`` and it asserted ``"eur_only" in str(excinfo.value)``
    — but the error interpolates ``{path}``, so THE FIXTURE'S OWN FILENAME
    satisfied the assertion. MEASURED, both directions:

      * deleting ``: {missing}`` from the f-string in ``_read_regions_tsv`` left
        the OLD test GREEN (the id came from the path);
      * the same deletion makes THIS repaired test RED.

    Two changes close it. The fixture is ``anc_split.tsv``, so the filename can no
    longer carry the id; and the message is SPLIT ONCE on the interpolated path,
    with the assertion scoped to the TAIL — the only route left to it is the
    ``{missing}`` list itself.

    Its CLI sibling ``test_cli_region_only_in_the_unrequested_ancestry_exits_2_and_
    writes_no_tsv`` (fixture ``ancerr.tsv``) already covered the property BY
    ACCIDENT — its fixture name happens not to contain the id. Accident is not
    coverage; this test is the one that states the property.
    """
    import pairwise_completeness_scan as pcs

    regions = _ancestry_regions_tsv(
        tmp_path,
        [("r1", "1", 1000, 2000, "AFR"), ("eur_only", "1", 3000, 4000, "EUR")],
        name="anc_split.tsv",
    )
    assert "eur_only" not in str(regions), (
        "the fixture filename must not be able to satisfy the assertion below"
    )

    with pytest.raises(ValueError) as excinfo:
        pcs._read_regions_tsv(regions, ["r1", "eur_only"])
    message = str(excinfo.value)
    assert str(regions) in message, (
        f"the message no longer interpolates the path, so the split below is "
        f"not the scoping it claims to be: {message!r}"
    )
    tail = message.split(str(regions), 1)[1]
    assert "eur_only" in tail, (
        f"the missing id is not named AFTER the interpolated path — only the "
        f"path itself carried it: {message!r}"
    )

    # ...and it IS reachable with --ancestry EUR, so the raise is about the
    # ancestry key and not about the id being absent from the file entirely.
    got = pcs._read_regions_tsv(regions, ["eur_only"], ancestry="EUR")
    assert got == [("eur_only", "1", 3000, 4000)]


def test_composite_whitespace_ancestry_parse_selects_where_production_drops(
    tmp_path,
):
    """THE COMPOSITE PARSE, PINNED AT THE SELECTION LAYER — not at the predicate.

    ``test_ancestry_predicate_agrees_with_the_production_filter_contract`` pins
    ``_matches_ancestry`` against production and is GREEN — but the scanner's real
    path is ``_tsv_field(...)`` (which STRIPS) and THEN ``_matches_ancestry``. The
    predicate test therefore says nothing about a whitespace-padded manifest cell.
    That gap is exactly the reviewer's MEDIUM finding.

    This test drives ``"  AFR  "`` through ``_read_regions_tsv`` and pins TODAY'S
    ACTUAL BEHAVIOUR: the scanner SELECTS the row. It then MEASURES the production
    divergence instead of asserting it in prose — ``_filter_ancestry`` is
    ast-extracted from ``run_native_ld_panel.py`` AT CALL TIME and ``exec``'d in an
    empty namespace (never imported, so a stale ``.pyc`` cannot make this green —
    ``feedback_negative_control_defeated_by_bytecode_cache``), and production DROPS
    the same row.

    THIS IS A DIVERGENCE. It is LATENT, not live: the checked-in
    ``config/ld_regions.tsv`` carries ZERO padded-or-quoted ancestry cells, which
    is what ``test_real_manifest_carries_no_padded_or_quoted_ancestry_cells``
    below MONITORS. That monitor is what keeps this latent; the day it goes RED,
    this divergence becomes live and must be closed rather than recorded.

    RED mechanism, OBSERVED (quick-260828-uej): removing ``.strip()`` from
    ``_tsv_field`` drops the padded row, ``_read_regions_tsv`` returns ``[]`` and
    this test fails.
    """
    import ast

    import pairwise_completeness_scan as pcs

    regions = _ancestry_regions_tsv(
        tmp_path,
        [("padded", "1", 1000, 2000, "  AFR  ")],
        name="padded_anc.tsv",
    )

    # THE SCANNER SELECTS IT — through the real composite path, not the predicate.
    got = pcs._read_regions_tsv(regions, None)
    assert got == [("padded", "1", 1000, 2000)], (
        f"the scanner no longer selects a whitespace-padded ancestry cell: {got}"
    )

    # PRODUCTION, READ AT CALL TIME, DROPS IT.
    source = _RUN_NATIVE_LD_PANEL.read_text()
    tree = ast.parse(source)
    fn = next(
        (
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "_filter_ancestry"
        ),
        None,
    )
    assert fn is not None, (
        "run_native_ld_panel._filter_ancestry is GONE — there is no production "
        "contract left to measure the divergence against"
    )
    segment = ast.get_source_segment(source, fn)
    assert segment is not None and segment.lstrip().startswith("def _filter_ancestry")
    namespace: dict = {}
    exec(compile(segment, "<_filter_ancestry contract>", "exec"), namespace)
    production = namespace["_filter_ancestry"]

    assert production([{"ancestry": "  AFR  "}], "AFR") == [], (
        "production now ACCEPTS a padded ancestry cell — the divergence this test "
        "measures has changed shape and the record must be rewritten"
    )
    # ...and it is the PADDING, not the value: unpadded, production takes it.
    assert len(production([{"ancestry": "AFR"}], "AFR")) == 1


def test_real_manifest_carries_no_padded_or_quoted_ancestry_cells():
    """THE MONITOR THAT KEEPS THE DIVERGENCE LATENT.

    The scanner strips the ancestry cell and production does not. That only
    MATTERS if a row with a padded or quoted ancestry cell actually exists.
    MEASURED at quick-260828-uej: 0 of 552 data rows in the real
    ``config/ld_regions.tsv``. This test re-measures it AT CALL TIME and goes RED
    the day such a row appears — which is the only condition under which the
    divergence pinned above becomes live.
    """
    import pairwise_completeness_scan as pcs

    manifest = PROJECT_ROOT / "config" / "ld_regions.tsv"
    assert manifest.exists(), f"the real manifest is gone: {manifest}"

    offenders = []
    data_rows = 0
    for lineno, line in enumerate(manifest.read_text().splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) <= pcs._REGIONS_TSV_END_COL:
            continue
        try:
            int(parts[pcs._REGIONS_TSV_START_COL])
            int(parts[pcs._REGIONS_TSV_END_COL])
        except ValueError:
            continue  # the header row
        data_rows += 1
        cell = parts[pcs._REGIONS_TSV_ANCESTRY_COL]
        if cell != cell.strip() or '"' in cell:
            offenders.append((lineno, cell))

    assert data_rows == 552, (
        f"the manifest's shape changed: {data_rows} data rows, expected 552 "
        f"(276 region ids x {{AFR, EUR}})"
    )
    assert not offenders, (
        "the real manifest now carries padded-or-quoted ancestry cells, so the "
        "scanner-vs-production whitespace divergence pinned by "
        "test_composite_whitespace_ancestry_parse_selects_where_production_drops "
        f"is LIVE and must be closed, not recorded: {offenders}"
    )


def test_cli_region_only_in_the_unrequested_ancestry_exits_2_and_writes_no_tsv(
    tmp_path, capsys
):
    """Through ``main()`` that becomes ``ERROR: ...`` on stderr + return code 2,
    BEFORE any output file is opened."""
    import pairwise_completeness_scan as pcs

    base = _multi_region_bfile(tmp_path, prefix="ancerr")
    regions = _ancestry_regions_tsv(
        tmp_path,
        [("r1", "1", 990, 1010, "AFR"), ("r2", "chr1", 4990, 5010, "EUR")],
        name="ancerr.tsv",
    )
    out = tmp_path / "should_not_exist.tsv"

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
    ])

    assert rc == 2
    captured = capsys.readouterr()
    assert "ERROR:" in captured.err
    assert "r2" in captured.err
    assert not out.exists(), "a partial TSV was written before the input was validated"


def test_tsv_field_is_bounds_tolerant_standalone():
    """``_tsv_field`` is unit-tested DIRECTLY against raw lists.

    It is NOT routed through ``_read_regions_tsv`` — see the companion test
    below for why that would be a FALSE INVARIANT. A naive ``parts[index].strip()``
    raises ``IndexError`` on the first case.
    """
    import pairwise_completeness_scan as pcs

    assert pcs._tsv_field(["a", "b"], 6) == ""
    assert pcs._tsv_field(["a", "b", "c", "d", "e", "f", "  AFR "], 6) == "AFR"
    assert pcs._tsv_field([], 0) == ""
    assert pcs._tsv_field(["  x  "], 0) == "x"


def test_read_regions_tsv_length_guard_masks_the_accessor_so_tsv_field_is_tested_alone(
    tmp_path,
):
    """DOCUMENTS THE LAYERING — and why the test above is not routed through the parser.

    ``_REGIONS_TSV_ANCESTRY_COL`` (6) is LESS than ``_REGIONS_TSV_END_COL`` (15),
    so the pre-existing ``if len(parts) <= _REGIONS_TSV_END_COL: continue`` guard
    already drops every short row BEFORE column 6 is touched. A bounds-tolerance
    assertion routed through ``_read_regions_tsv`` therefore passes whether or not
    ``_tsv_field`` exists at all — a false invariant of exactly the class this
    project has been bitten by before (a grep pin green on broken code).

    The guard is the FIRST line of defense; ``_tsv_field`` is the SECOND, and it
    is what keeps the parse correct if the column order ever changes so that
    ancestry sits PAST ``_REGIONS_TSV_END_COL``.

    What THIS test pins: the ordering fact itself, and that a truncated row does
    not raise out of the parse while the well-formed rows around it are returned.
    """
    import pairwise_completeness_scan as pcs

    assert pcs._REGIONS_TSV_ANCESTRY_COL < pcs._REGIONS_TSV_END_COL, (
        "ancestry now sits past the length guard — the guard no longer masks "
        "_tsv_field, and this test's premise must be re-derived"
    )

    regions = _ancestry_regions_tsv(
        tmp_path, [("r1", "1", 1000, 2000, "AFR")], name="ragged.tsv"
    )
    with regions.open("a") as fh:
        fh.write("truncated\t1\n")            # 2 fields — dropped by the guard
        fh.write("\t".join(["short"] * 7) + "\n")  # 7 fields — still short

    windows = pcs._read_regions_tsv(regions, None)
    assert windows == [("r1", "1", 1000, 2000)]


# =========================================================================== #
# quick-260826-qq9 — T2: DEFENSE IN DEPTH against SILENT MULTIPLICATION        #
#                                                                             #
# T1 fixes the CAUSE (an ancestry-blind manifest read). These tests pin the    #
# MECHANISM that turned that read into an 8x inflation, so the same class of   #
# silent multiplication cannot recur from a different cause:                   #
#                                                                             #
#   iter_bim_windows builds ``specs`` as a LIST and ``out`` as a DICT keyed on #
#   region_id, so a repeated id appends each matching .bim row ONCE PER        #
#   MATCHING SPEC -> rows 2x -> deletion x partner pairs 4x; the driver's      #
#   ``summaries`` dict then LAST-WINS while ``all_results`` ACCUMULATES -> two #
#   driver passes -> 8x in the emitted TSV; and the stdout table iterates the  #
#   LIST while looking up the DICT, so every region printed twice.             #
#                                                                             #
# Lifted from the local reproduction (6 rows, chr15, bp 1000..1005):           #
#   CONTROL ("R","15",1000,1005)                    -> 6 rows [0,1,2,3,4,5]    #
#   CASE A  the same id twice, IDENTICAL bounds     -> was 12 rows             #
#                                                     [0,0,1,1,2,2,3,3,4,4,5,5]#
#   CASE B  the same id twice, DIFFERING bounds     -> was 8 rows              #
#                                                     [0,1,1,2,2,3,4,5]        #
# Both shapes are REAL: of the 21 swept regions, 12 have IDENTICAL AFR/EUR     #
# bounds and 9 (``__subNN``) have the AFR window strictly INSIDE the EUR one.  #
# =========================================================================== #

def _six_row_bim(tmp_path: Path, name: str = "dup.bim") -> Path:
    """The reproduction's ``.bim``: 6 rows on chr15 at bp 1000..1005."""
    path = tmp_path / name
    path.write_text("".join(f"15\tv{i}\t0\t{1000 + i}\tA\tG\n" for i in range(6)))
    return path


def test_iter_bim_windows_single_region_id_control_still_returns_six_rows(tmp_path):
    """THE NEGATIVE CONTROL FOR THE DUPLICATE GUARD, KEPT GREEN.

    A guard that raised on EVERYTHING would be worthless
    (``feedback_green_assertion_needs_a_negative_control``). The single-id case
    must be BYTE-FOR-BYTE what it always was: 6 rows, global indices [0..5].
    This test is green before AND after the guard lands — deliberately.
    """
    import pairwise_completeness_scan as pcs

    out = pcs.iter_bim_windows(_six_row_bim(tmp_path), [("R", "15", 1000, 1005)])

    assert list(out) == ["R"]
    assert len(out["R"]) == 6
    assert [i for i, _row in out["R"]] == [0, 1, 2, 3, 4, 5]


def test_iter_bim_windows_duplicate_region_id_identical_bounds_raises(tmp_path):
    """CASE A — the same id twice with IDENTICAL bounds.

    Shipped behaviour: 12 rows with indices [0,0,1,1,2,2,3,3,4,4,5,5] — every
    ``.bim`` row appended once per matching spec. That is the EXACT 2x that the
    153 identical-bounds region_ids in ``config/ld_regions.tsv`` produced.
    """
    import pairwise_completeness_scan as pcs

    with pytest.raises(ValueError) as excinfo:
        pcs.iter_bim_windows(
            _six_row_bim(tmp_path, "a.bim"),
            [("R", "15", 1000, 1005), ("R", "15", 1000, 1005)],
        )
    message = str(excinfo.value)
    assert "R" in message, message
    assert "duplicate region_id" in message, message


def test_iter_bim_windows_duplicate_region_id_differing_bounds_raises(tmp_path):
    """CASE B — the same id twice with DIFFERENT, OVERLAPPING bounds.

    Shipped behaviour: 8 rows with indices [0,1,1,2,2,3,4,5] — a NON-UNIFORM
    multiplication, which is why the contaminated sweep's 2,865,513 / 1,453,157
    ratio is 1.972 and not 2.000. This is the shape the 123 ``__subNN``-style
    ids produce, where the AFR window sits strictly inside the EUR window.
    """
    import pairwise_completeness_scan as pcs

    with pytest.raises(ValueError) as excinfo:
        pcs.iter_bim_windows(
            _six_row_bim(tmp_path, "b.bim"),
            [("R", "15", 1000, 1002), ("R", "15", 1001, 1005)],
        )
    assert "R" in str(excinfo.value)


def test_assert_unique_region_ids_names_the_offending_ids_and_their_counts():
    """The shared helper is a NAMED ENFORCER, not an anonymous inline check
    (``feedback_a_claimed_invariant_needs_a_named_enforcer``)."""
    import pairwise_completeness_scan as pcs

    # the CONTROL shape returns None and does not raise
    assert (
        pcs._assert_unique_region_ids(
            [("R", "15", 1000, 1005), ("S", "15", 1000, 1005)]
        )
        is None
    )

    with pytest.raises(ValueError) as excinfo:
        pcs._assert_unique_region_ids(
            [
                ("R", "15", 1000, 1005),
                ("R", "15", 1000, 1005),
                ("S", "15", 1, 2),
                ("S", "15", 1, 2),
                ("S", "15", 1, 2),
                ("T", "15", 1, 2),
            ]
        )
    message = str(excinfo.value)
    assert "R" in message and "S" in message
    assert "2" in message and "3" in message, (
        f"the repeat COUNTS must be named, not just the ids: {message}"
    )
    assert "'T'" not in message, f"the non-duplicated id must not be blamed: {message}"


def test_cli_duplicate_region_id_manifest_exits_2_and_writes_no_tsv(tmp_path, capsys):
    """A duplicated region_id is a CLEAN exit 2, never a traceback and never
    last-wins.

    ⚠ HONEST LABELLING OF WHAT THIS TEST DEMONSTRATES: it passes via ``main()``'s
    PRE-LOOP ``_assert_unique_region_ids(windows)`` call. It does NOT exercise the
    driver loop's ``if region_id in summaries: raise`` line, which is UNREACHABLE
    in the shipped configuration — ``iter_bim_windows`` is called before the loop
    and carries the same guard internally. So THIS test must not be read as
    evidence for that third layer; it would be green for the wrong reason.

    That third layer IS separately covered, by
    ``test_driver_summaries_guard_independently_refuses_last_wins_with_both_upstream_layers_disabled``,
    which monkeypatches the shared module-global enforcer to neutralize layers 1
    and 2 and then attributes the raise by the traceback's final frame. (An earlier
    revision of this docstring claimed no committed test could reach layer 3. That
    was true of the naive front-door test and false in general — quick-260826-qq9 T4.)

    Note that an ancestry filter CANNOT save this manifest: both rows are AFR.
    """
    import pairwise_completeness_scan as pcs

    base = _multi_region_bfile(tmp_path, prefix="dupcli")
    regions = _ancestry_regions_tsv(
        tmp_path,
        [("r1", "1", 990, 1010, "AFR"), ("r1", "1", 990, 1010, "AFR")],
        name="dup_afr.tsv",
    )
    out = tmp_path / "should_not_exist.tsv"

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1",
        "--window-bp", "10",
        "--out", str(out),
    ])

    assert rc == 2
    err = capsys.readouterr().err
    assert "ERROR:" in err and "r1" in err
    assert not out.exists(), "a partial TSV survived a duplicated region_id"


def test_cli_stdout_table_prints_exactly_one_line_per_region_id(tmp_path, capsys):
    """The per-region table iterates ``windows`` and looks up ``summaries``.

    With ``_assert_unique_region_ids`` upstream, ``windows`` carries unique ids by
    construction, so no region can print twice. Previously a 2-ancestry manifest
    made EVERY region print twice with identical values — a defect the receiving
    agent flagged from the sweep's own stdout.
    """
    import pairwise_completeness_scan as pcs

    base = _multi_region_bfile(tmp_path, prefix="tbl")
    regions = _ancestry_regions_tsv(
        tmp_path,
        [
            ("r1", "1", 990, 1010, "AFR"),
            ("r1", "1", 890, 1110, "EUR"),
            ("r2", "chr1", 4990, 5010, "AFR"),
            ("r2", "chr1", 4890, 5110, "EUR"),
        ],
        name="tbl.tsv",
    )
    assert pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(tmp_path / "pairs.tsv"),
    ]) == 0

    stdout = capsys.readouterr().out.splitlines()
    header_at = next(i for i, ln in enumerate(stdout) if ln.split("\t")[0] == "region_id")
    data = []
    for line in stdout[header_at + 1:]:
        if not line.strip():
            break
        data.append(line.split("\t")[0])

    assert len(data) == 2, f"the table printed {len(data)} lines for 2 regions: {data}"
    assert len(set(data)) == len(data), f"a region_id printed twice: {data}"
    assert set(data) == {"r1", "r2"}


def test_pooled_candidate_rows_is_the_summaries_basis_and_names_it(tmp_path, capsys):
    """THE TWO 'POOLED' DENOMINATORS ARE ONE BASIS, AND EACH LINE SAYS SO.

    Previously ``POOLED candidate rows`` printed ``len(all_results)`` (the
    DUPLICATED basis) three lines below a histogram and bins computed from
    ``summaries`` (the DEDUPED basis) — different denominators under one heading.
    In the contaminated sweep that read 2,865,513 against a summaries basis of
    1,453,157.
    """
    import csv

    import pairwise_completeness_scan as pcs

    base = _multi_region_bfile(tmp_path, prefix="pooled")
    regions = _ancestry_regions_tsv(
        tmp_path,
        [("r1", "1", 990, 1010, "AFR"), ("r2", "chr1", 4990, 5010, "AFR")],
        name="pooled.tsv",
    )
    out = tmp_path / "pairs.tsv"
    summ = tmp_path / "summary.json"
    assert pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
        "--summary", str(summ),
    ]) == 0

    stdout = capsys.readouterr().out
    pooled_lines = [ln for ln in stdout.splitlines() if ln.startswith("POOLED")]
    assert len(pooled_lines) == 3, pooled_lines
    for line in pooled_lines:
        assert "basis: per-region summaries" in line, (
            f"a POOLED line does not state its basis: {line!r}"
        )

    import json

    summaries = json.loads(summ.read_text())
    expected = sum(s["n_candidate_rows"] for s in summaries.values())
    emitted = len(list(csv.DictReader(out.open(), delimiter="\t")))
    assert expected == emitted == 2

    rows_line = next(ln for ln in pooled_lines if "candidate rows" in ln)
    assert rows_line.rsplit(": ", 1)[1] == str(expected)
    assert "reconciled against the emitted TSV rows" in rows_line


def _bump_one_region_summary(monkeypatch, pcs):
    """Monkeypatch ``summarize`` so ONE region reports ``n_candidate_rows`` + 1.

    The perturbation is applied to the FIRST region only, so the pooled
    per-region basis exceeds the emitted-TSV basis by exactly 1 and the
    must-be-identity reconciliation in ``main()`` must fire. Extracted so every
    quarantine test drives the SAME disagreement rather than re-deriving it.
    """
    real_summarize = pcs.summarize
    state = {"bumped": False}

    def off_by_one(*args, **kwargs):
        summary = real_summarize(*args, **kwargs)
        if not state["bumped"]:
            state["bumped"] = True
            summary = dict(summary)
            summary["n_candidate_rows"] = summary["n_candidate_rows"] + 1
        return summary

    monkeypatch.setattr(pcs, "summarize", off_by_one)


def _two_region_disagreement_fixture(tmp_path, prefix="recon", name="recon.tsv"):
    """The two-region bfile + AFR manifest every quarantine test scans."""
    base = _multi_region_bfile(tmp_path, prefix=prefix)
    regions = _ancestry_regions_tsv(
        tmp_path,
        [("r1", "1", 990, 1010, "AFR"), ("r2", "chr1", 4990, 5010, "AFR")],
        name=name,
    )
    return base, regions


#: What a contaminated artifact looks like in the stale-file tests. Deliberately
#: NOT a substring of any real TSV field, so `in` here cannot false-pass.
_JUNK_MARKER = "JUNK-STALE-CONTAMINATED-ROW"


def test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2(
    tmp_path, monkeypatch, capsys
):
    """A MUST-BE-IDENTITY TRANSFORM — and a disagreement costs a RENAME, not a RUN.

    ``feedback_aggregate_agreement_hides_component_errors``: agreement by eye is
    what let two denominators print three lines apart for a whole sweep. Here the
    per-region ``n_candidate_rows`` is perturbed by +1 for ONE region and the run
    must report BOTH numbers.

    RENAMED AND INVERTED by ``quick-260828-uej``. It previously asserted
    ``pytest.raises(ValueError)`` — and its NAME said ``_raises_``, which is now
    false. ``main()`` writes the TSV FIRST (so no stale artifact can survive at
    the read path), then reconciles, and on disagreement QUARANTINES the output
    to ``<out>.SUSPECT`` and returns 2 like every other failure path. Three
    properties at once: nothing plausible survives at ``--out`` (an operator's
    ``wc -l`` fails loudly instead of returning a stale 2,865,514); the compute is
    salvaged in the ``.SUSPECT`` sibling; and the reconciliation ARITHMETIC is
    byte-unchanged. The ``not out.exists()`` half SURVIVES the inversion and is
    still meaningful — the file is renamed AWAY, never left behind.
    """
    import json
    import re

    import pairwise_completeness_scan as pcs

    base, regions = _two_region_disagreement_fixture(tmp_path)
    out = tmp_path / "pcs_pairs.tsv"
    summ = tmp_path / "pcs_summary.json"

    _bump_one_region_summary(monkeypatch, pcs)

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
        "--summary", str(summ),
    ])
    assert rc == 2, "a POOLED disagreement must RETURN 2, not raise a traceback"

    err = capsys.readouterr().err
    assert err.count("ERROR:") == 1, (
        f"exactly ONE ERROR line belongs on stderr, got: {err!r}"
    )
    # BOTH numbers, each anchored by the surrounding message text rather than by a
    # bare `in` — a bare "3" is satisfiable by any digit anywhere, including in
    # tmp_path (the standing rule of quick-260828-uej).
    assert re.search(r"n_candidate_rows = 3(?!\d)", err), (
        f"the per-region basis (3) is not named: {err!r}"
    )
    assert re.search(r"carries 2(?!\d) candidate rows", err), (
        f"the emitted-TSV basis (2) is not named: {err!r}"
    )
    assert "n_candidate_rows" in err

    suspect = Path(str(out) + ".SUSPECT")
    assert str(suspect) in err, (
        f"the ERROR line must name the quarantine path: {err!r}"
    )

    assert not out.exists(), (
        "a TSV survived at --out even though the two POOLED bases disagreed"
    )
    assert suspect.exists(), "the ~4h18m of compute was discarded, not quarantined"
    rows = suspect.read_text().splitlines()
    assert rows[0] == "\t".join(pcs.TSV_COLUMNS)
    assert len(rows) - 1 == 2, (
        f"the quarantined TSV must hold the emitted rows, got {len(rows) - 1}"
    )

    summary_suspect = Path(str(summ) + ".SUSPECT")
    assert not summ.exists(), "the summary JSON survived at --summary"
    assert summary_suspect.exists(), "the summary JSON was not quarantined alongside"
    assert set(json.loads(summary_suspect.read_text())) == {"r1", "r2"}


def test_a_stale_artifact_at_out_does_not_survive_a_successful_run(tmp_path):
    """BLOCKER-2's read path, SUCCESS half: writing TRUNCATES.

    The contaminated ``/home/jupyter/occ_measure/pcs_pairs.tsv`` (871,038,152 B,
    2,865,514 lines) sits at exactly the path the runbook ``wc -l``s. A successful
    run must leave ONLY fresh bytes there — zero pre-existing lines survive.

    NEGATIVE CONTROL, OBSERVED (quick-260828-uej): flipping ``write_tsv``'s
    ``open(out_path, "w")`` to ``"a"`` leaves the junk lines in place and this
    test goes RED. ``__pycache__`` is cleared around that mutation because ``"w"``
    and ``"a"`` are the SAME byte length
    (``feedback_negative_control_defeated_by_bytecode_cache``).
    """
    import pairwise_completeness_scan as pcs

    base, regions = _two_region_disagreement_fixture(
        tmp_path, prefix="stale_ok", name="stale_ok.tsv"
    )
    out = tmp_path / "pcs_pairs.tsv"
    out.write_text("".join(f"{_JUNK_MARKER}-{i}\n" for i in range(5)))
    assert len(out.read_text().splitlines()) == 5

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
    ])
    assert rc == 0

    text = out.read_text()
    assert _JUNK_MARKER not in text, (
        "a contaminated line survived a SUCCESSFUL run at the read path"
    )
    lines = text.splitlines()
    assert lines[0] == "\t".join(pcs.TSV_COLUMNS)
    assert len(lines) - 1 == 2


def test_a_stale_artifact_at_out_does_not_survive_a_quarantined_run(
    tmp_path, monkeypatch, capsys
):
    """BLOCKER-2's read path, FAILURE half: nothing plausible survives at ``--out``.

    This is the half the old ordering got WRONG. Reconciling BEFORE the write left
    the 871 MB contaminated file untouched at the exact path the operator then
    ``wc -l``s — 2,865,514 would have come back and read as a result. Now the
    write truncates it and the rename carries it away, so the ``wc -l`` FAILS
    LOUDLY, and the ``.SUSPECT`` sibling holds the FRESH rows, never the junk.

    RED mechanism: revert the write/reconcile order and the junk is still at
    ``out`` when the run exits.
    """
    import pairwise_completeness_scan as pcs

    base, regions = _two_region_disagreement_fixture(
        tmp_path, prefix="stale_bad", name="stale_bad.tsv"
    )
    out = tmp_path / "pcs_pairs.tsv"
    out.write_text("".join(f"{_JUNK_MARKER}-{i}\n" for i in range(5)))

    _bump_one_region_summary(monkeypatch, pcs)

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
    ])
    capsys.readouterr()
    assert rc == 2
    assert not out.exists(), (
        "the contaminated artifact survived at the read path — an operator's "
        "`wc -l` would return a stale number instead of failing"
    )

    suspect = Path(str(out) + ".SUSPECT")
    assert suspect.exists()
    quarantined = suspect.read_text()
    assert _JUNK_MARKER not in quarantined, (
        "the quarantined file carries the OLD junk, not the fresh rows"
    )
    assert quarantined.splitlines()[0] == "\t".join(pcs.TSV_COLUMNS)
    assert len(quarantined.splitlines()) - 1 == 2


def test_a_preexisting_suspect_is_rotated_not_clobbered(
    tmp_path, monkeypatch, capsys
):
    """ROTATE, never delete — the project ruling applies to the quarantine too.

    ``.planning/debug/260824-STAGE-A-env-stop-plink1.9-and-stale-scratch-TSV.md``:
    a prior artifact is EVIDENCE. A second disagreement must not destroy the first
    one's bytes.

    RED mechanism: a bare ``Path(out).replace(suspect)`` onto an existing
    ``.SUSPECT`` overwrites it and the marker line is gone.
    """
    import re

    import pairwise_completeness_scan as pcs

    base, regions = _two_region_disagreement_fixture(
        tmp_path, prefix="rot", name="rot.tsv"
    )
    out = tmp_path / "pcs_pairs.tsv"
    suspect = Path(str(out) + ".SUSPECT")
    marker = "EARLIER-SUSPECT-BYTES-THAT-MUST-SURVIVE"
    suspect.write_text(marker + "\n")

    _bump_one_region_summary(monkeypatch, pcs)

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
    ])
    capsys.readouterr()
    assert rc == 2

    rotated = sorted(tmp_path.glob(out.name + ".SUSPECT.*"))
    assert len(rotated) == 1, (
        f"expected exactly one rotated sibling, got {[p.name for p in rotated]}"
    )
    assert marker in rotated[0].read_text(), (
        "the earlier .SUSPECT bytes were CLOBBERED, not rotated"
    )
    stamp = rotated[0].name.split(".SUSPECT.", 1)[1]
    assert re.fullmatch(r"\d{8}T\d{6}Z", stamp), (
        f"the rotation stamp is not a UTC stamp: {stamp!r}"
    )

    assert suspect.exists()
    fresh = suspect.read_text()
    assert marker not in fresh
    assert fresh.splitlines()[0] == "\t".join(pcs.TSV_COLUMNS)


def test_the_quarantine_name_is_built_by_string_concatenation_not_with_suffix(
    tmp_path, monkeypatch, capsys
):
    """``Path.with_suffix`` would turn ``pcs_pairs.tsv`` into ``pcs_pairs.SUSPECT``.

    That silently DESTROYS the extension the operator greps for and, worse, would
    collide with the summary's quarantine name (``pcs_summary.SUSPECT``). The
    quarantined name must END WITH the original name plus ``.SUSPECT``, so a
    future ``with_suffix`` refactor goes RED here.
    """
    import pairwise_completeness_scan as pcs

    base, regions = _two_region_disagreement_fixture(
        tmp_path, prefix="cat", name="cat.tsv"
    )
    out = tmp_path / "pcs_pairs.tsv"
    summ = tmp_path / "pcs_summary.json"

    _bump_one_region_summary(monkeypatch, pcs)

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
        "--summary", str(summ),
    ])
    capsys.readouterr()
    assert rc == 2

    assert (tmp_path / "pcs_pairs.tsv.SUSPECT").exists()
    assert (tmp_path / "pcs_summary.json.SUSPECT").exists()
    # the `with_suffix` products must NOT exist
    assert not (tmp_path / "pcs_pairs.SUSPECT").exists(), (
        "the quarantine used Path.with_suffix — the .tsv extension was destroyed"
    )
    assert not (tmp_path / "pcs_summary.SUSPECT").exists()

    for original in (out, summ):
        quarantined = Path(str(original) + ".SUSPECT")
        assert quarantined.name.endswith(original.name + ".SUSPECT")


def test_an_empty_after_strip_region_ids_is_an_error_while_the_absent_flag_still_means_all_regions(
    tmp_path, monkeypatch, capsys
):
    """``--region-ids ' , '`` was a SILENT ~13x cost blow-up.

    ``[r.strip() for r in v.split(",") if r.strip()]`` yielded ``[]`` -> falsy ->
    ``wanted = None`` -> NO filter -> every region in the manifest. On the real
    276-region manifest that turns a 21-region sweep into a 276-region one and
    fails loudly NOWHERE. It is now a ``ValueError`` inside the EXISTING ``try:``,
    so it lands on the existing ``ERROR:`` + ``return 2`` path with no traceback,
    BEFORE any scan and BEFORE any file is written.

    The flag ABSENT still means "all regions" — that path is UNCHANGED and is the
    NEGATIVE CONTROL kept green in the second half.
    """
    import pairwise_completeness_scan as pcs

    base, regions = _two_region_disagreement_fixture(
        tmp_path, prefix="rid", name="rid.tsv"
    )
    out = tmp_path / "empty_region_ids.tsv"

    def _never(*args, **kwargs):  # pragma: no cover - must not be reached
        raise AssertionError("the scan STARTED on an empty --region-ids")

    monkeypatch.setattr(pcs, "iter_bim_windows", _never)

    rc = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", " , ",
        "--window-bp", "10",
        "--out", str(out),
    ])
    err = capsys.readouterr().err
    assert rc == 2
    assert "--region-ids" in err, f"the flag is not named: {err!r}"
    assert repr(" , ") in err, f"the offending value is not shown: {err!r}"
    assert not out.exists(), "an output file was created on an empty --region-ids"

    # --- NEGATIVE CONTROL: the flag ABSENT is UNCHANGED and still scans all ---
    monkeypatch.undo()
    out_all = tmp_path / "all_regions.tsv"
    rc_all = pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--window-bp", "10",
        "--out", str(out_all),
    ])
    capsys.readouterr()
    assert rc_all == 0, "omitting --region-ids must still scan every region"
    assert len(out_all.read_text().splitlines()) - 1 == 2


def test_two_ancestry_manifest_emits_no_inflated_counts_end_to_end(tmp_path, capsys):
    """THE REGRESSION THAT WOULD HAVE CAUGHT THE 8x.

    An AFR row AND an EUR row for each of two regions, over the existing
    ``_multi_region_bfile`` fixture. Shipped code emitted 4 TSV rows (2x), printed
    4 table lines, and reported ``n_candidate_rows == 2`` per region. The repaired
    scanner emits EXACTLY 2 — one per region — and pools to 2.
    """
    import csv
    import json

    import pairwise_completeness_scan as pcs

    base = _multi_region_bfile(tmp_path, prefix="e2e")
    regions = _ancestry_regions_tsv(
        tmp_path,
        [
            ("r1", "1", 990, 1010, "AFR"),
            ("r1", "1", 890, 1110, "EUR"),
            ("r2", "chr1", 4990, 5010, "AFR"),
            ("r2", "chr1", 4890, 5110, "EUR"),
        ],
        name="e2e.tsv",
    )
    out = tmp_path / "pairs.tsv"
    summ = tmp_path / "summary.json"
    assert pcs.main([
        "--bfile-prefix", str(base),
        "--regions-tsv", str(regions),
        "--region-ids", "r1,r2",
        "--window-bp", "10",
        "--out", str(out),
        "--summary", str(summ),
    ]) == 0

    rows = list(csv.DictReader(out.open(), delimiter="\t"))
    assert len(rows) == 2, f"a 2-ancestry manifest emitted {len(rows)} rows, not 2"
    assert {r["region_id"] for r in rows} == {"r1", "r2"}

    summaries = json.loads(summ.read_text())
    assert set(summaries) == {"r1", "r2"}
    for region_id, summary in summaries.items():
        assert summary["n_candidate_rows"] == 1, (region_id, summary["n_candidate_rows"])

    stdout = capsys.readouterr().out
    header_at = next(
        i for i, ln in enumerate(stdout.splitlines()) if ln.split("\t")[0] == "region_id"
    )
    table = []
    for line in stdout.splitlines()[header_at + 1:]:
        if not line.strip():
            break
        table.append(line)
    assert len(table) == 2, f"the table printed {len(table)} lines, not 2"

    pooled = next(
        ln for ln in stdout.splitlines()
        if ln.startswith("POOLED") and "candidate rows" in ln
    )
    assert pooled.rsplit(": ", 1)[1] == "2", pooled


def test_driver_summaries_guard_independently_refuses_last_wins_with_both_upstream_layers_disabled(
    tmp_path, monkeypatch
):
    """LAYER 3 -- the driver's ``if region_id in summaries: raise`` -- IS testable.

    ⚠ SUPERSEDES an earlier claim in this file and in the module that "NO committed
    test can exercise it". That claim was right about the NAIVE test (feed a
    duplicated manifest through the front door and it passes via layer 1 or 2, a
    FALSE INVARIANT) and wrong to conclude no committed test is possible.

    Testing the INNERMOST layer of a defense-in-depth stack REQUIRES disabling the
    outer ones -- the same way a DB unique constraint is tested by bypassing
    app-level validation, or a fallback by disabling the primary. That is not a
    contrived setup; it is the only setup under which the property "if upstream
    validation is ever bypassed or removed, the innermost write still refuses to
    last-win" can be observed at all.

    Layers 1 (``iter_bim_windows``, :739) and 2 (``main()``, :1435) both call the
    MODULE-GLOBAL ``_assert_unique_region_ids``, so a single monkeypatch neutralizes
    both. What remains active is exactly layer 3.

    ATTRIBUTION, NOT MERELY A RAISE: this asserts the traceback's FINAL frame is the
    driver line. Without that, a green here would only prove "something stopped it"
    -- the very error this test exists to avoid repeating.

    NEGATIVE CONTROL (must be re-observed if this test is ever edited): deleting the
    ``if region_id in summaries: raise`` branch makes this test FAIL -- the run
    completes and ``summaries`` silently last-wins. Recorded in the quick's SUMMARY.
    """
    import traceback
    import pairwise_completeness_scan as pcs

    monkeypatch.setattr(pcs, "_assert_unique_region_ids", lambda windows: None)

    base = _multi_region_bfile(tmp_path, prefix="layer3")
    regions = _ancestry_regions_tsv(
        tmp_path,
        [("r1", "1", 990, 1010, "AFR"), ("r1", "1", 990, 1010, "AFR")],
        name="layer3_dup.tsv",
    )
    out = tmp_path / "should_not_exist.tsv"

    with pytest.raises(ValueError) as excinfo:
        pcs.main([
            "--bfile-prefix", str(base),
            "--regions-tsv", str(regions),
            "--region-ids", "r1",
            "--window-bp", "10",
            "--out", str(out),
        ])

    assert "evaluated twice" in str(excinfo.value)
    assert "r1" in str(excinfo.value)

    # ATTRIBUTION: the raise must originate at the DRIVER line, not upstream.
    frames = traceback.extract_tb(excinfo.tb)
    last = frames[-1]
    assert last.name == "main", f"raised from {last.name!r}, expected the driver in main()"
    assert "raise ValueError" in (last.line or "") or "evaluated twice" in (last.line or ""), last.line
    src_line = last.lineno
    driver_guard_lineno = next(
        i for i, ln in enumerate(
            Path(pcs.__file__).read_text().splitlines(), start=1
        ) if "if region_id in summaries:" in ln
    )
    assert 0 <= src_line - driver_guard_lineno <= 6, (
        f"raise at line {src_line} is not inside the driver guard at "
        f"{driver_guard_lineno} -- attribution failed, a DIFFERENT layer fired"
    )

    assert not out.exists(), "a partial TSV survived the driver-layer refusal"
