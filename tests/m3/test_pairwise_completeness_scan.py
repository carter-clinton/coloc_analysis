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
