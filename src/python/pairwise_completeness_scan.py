"""Pairwise-completeness scanner — a genotype-only detector of UNDEFINED LD.

WHAT PROPERTY THIS DETECTS
--------------------------
For a pair ``(X, Y)``, plink's ``r`` is undefined iff, within
``called(X) ∩ called(Y)``, X is constant or Y is constant (the empty
intersection included).

``carriers(X) ⊆ missing(Y)`` is ONE SUFFICIENT SPECIAL CASE of that condition
and is NEVER the test — it appears only as the derived ``confounding_pattern``
label. The primary path tests INVARIANCE WITHIN THE INTERSECTION, on BOTH
members, and nothing else. The test that pins this is
``tests/m3/test_pairwise_completeness_scan.py::test_undefined_without_carriers_subset_of_missing``:
it constructs a pair that IS undefined while ``carriers(deletion) ⊆ missing(partner)``
is demonstrably FALSE, and the detector must still report ``undefined=True``.

WHY IT EXISTS
-------------
``.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md``
§MECHANISM CONFIRMED. In ``m2_region_00057`` the 1 bp deletion
``chr15:20394741:AT:A`` (``ref_len 2`` -> ``span_end 20394742``) and the SNP
``chr15:20394743:T:C`` — ONE BASE past the deletion's REF span — are perfectly
confounded: **0 of 871** deletion carriers are called at the partner. Within the
**71,048** samples called at both, the deletion is constant, plink writes
``0/0 -> NaN``, and the deletion's MARGINAL allele frequency is a healthy
**0.601%**. The pre-registered occlusion criterion tests REF-span OVERLAP and
correctly declined to exclude the pair.

SECOND-ORDER CONSEQUENCE, in one sentence: partial confounding yields a FINITE
``r`` computed on a carrier-depleted, non-random subsample, and NO NaN check
anywhere in the pipeline catches it — which is why this module records a
carriers-lost GRADIENT and not merely a binary.

WHAT THIS IS NOT
----------------
This module changes NO criterion, NO threshold, NO span rule and NO NaN policy.
It is not on the fire path and is imported by nothing that is. It states NO
prevalence.

**Three things are OPEN and are NOT answered here:** (a) the prevalence of
undefined pairs across the panel, (b) the true boundary width and whether it is
one-sided, (c) whether a partial-confounding tail exists and how large. They are
settled ONLY by running this instrument in-perimeter over the pre-committed
21-region sample. **n = 1 supplies none of them** — inferring a constant from a
single region is exactly the error that produced the withdrawn ``0.0005`` bound.

THE plink1 ``.bed`` BYTE CONTRACT
---------------------------------
* bytes 0-1 magic ``0x6c 0x1b``; byte 2 mode: ``0x01`` = SNP-major
  (variant-major), ``0x00`` = individual-major.
* ``bytes_per_variant = (n_samples + 3) // 4``; variant ``i``'s block starts at
  ``3 + i * bytes_per_variant``.
* Within a byte: FOUR samples, the sample with the LOWEST index in the LOW-order
  2 bits (bits 0-1).
* 2-bit codes: ``00`` = hom-A1 · ``01`` = MISSING · ``10`` = het · ``11`` = hom-A2.
* Dosage of A1: ``00 -> 2``, ``10 -> 1``, ``11 -> 0``, ``01 -> missing``.
* Trailing bit-pairs of the last byte of each block are PADDING when
  ``n_samples % 4 != 0``.
* Expected file size is exactly ``3 + n_variants * bytes_per_variant``.

**A byte-order or mode mistake here silently corrupts every downstream number,
so every structural check RAISES** — bad magic, individual-major mode, a size
mismatch in EITHER direction, and a ``.bim``/``.fam`` line count that disagrees
with the ``.bed`` size. None of them is a warning.

THE GLOBAL-INDEX RULE
---------------------
The scanner takes a ``--bfile-prefix`` and streams THAT PREFIX'S OWN ``.bim``
(:func:`iter_bim_windows`) to derive GLOBAL 0-based variant indices. It never
accepts a pre-extracted window ``.bim``, because such a file carries
WINDOW-RELATIVE indices that would silently address the WRONG ``.bed`` blocks —
a wrong-genotype read with no error anywhere. The negative control that pins this
is ``test_window_relative_index_reads_the_wrong_block``.

MEMORY
------
Only the candidate variants' blocks are ever read; the ~354 GB production
``.bed`` is never materialized. The decode cache holds int8 dosage ONLY
(``called`` is derived on access), so the bound is
``cache_variants * n_samples`` bytes — about 150 MB at the 2048 default and
73,122 samples.

Pure stdlib + numpy. No plink, no Hail, no network, no perimeter contact.
"""
from __future__ import annotations

import argparse
import json
import sys
from bisect import bisect_left, bisect_right
from collections import OrderedDict
from pathlib import Path
from typing import Iterable, NamedTuple, Sequence

import numpy as np

# The FROZEN .bim semantics — imported, never forked. This module declares NO
# .bim column index of its own (never a 2nd copy); the textual enforcer is
# tests/m3/test_pairwise_completeness_scan.py::test_module_declares_no_bim_column_indices_of_its_own.
from occlusion_span_filter import (  # noqa: F401  (_COL_ALT/_COL_ID used by callers + tests)
    _COL_ALT,
    _COL_BP,
    _COL_CHR,
    _COL_ID,
    _COL_REF,
    load_bim_rows,
    parse_bim_row,
)

__all__ = [
    "BED_MAGIC",
    "BED_MODE_INDIVIDUAL_MAJOR",
    "BED_MODE_SNP_MAJOR",
    "BedReader",
    "DEFAULT_WINDOW_BP",
    "Genotypes",
    "MISSING_DOSAGE",
    "main",
]

#: Sentinel dosage for a no-called genotype. Negative so ``dosage >= 0`` is
#: exactly the called mask.
MISSING_DOSAGE: int = -1

BED_MAGIC: bytes = b"\x6c\x1b"
BED_MODE_SNP_MAJOR: int = 0x01
BED_MODE_INDIVIDUAL_MAJOR: int = 0x00

#: MEASUREMENT window (bp) swept on BOTH sides of a deletion's REF span.
#: This is a measurement parameter, NEVER a threshold: nothing is excluded,
#: flagged or decided on the basis of it. Widening it costs reads, not validity.
DEFAULT_WINDOW_BP: int = 25

#: 2-bit code -> dosage of A1. Index is the code; see the byte contract above.
_CODE_TO_DOSAGE = np.array([2, MISSING_DOSAGE, 1, 0], dtype=np.int8)

#: The four LOW-to-HIGH bit-pair shifts within one packed byte.
_BIT_SHIFTS = np.array([0, 2, 4, 6], dtype=np.uint8)


class Genotypes(NamedTuple):
    """One variant's decoded dosages.

    ``dosage`` is int8 of length ``n_samples`` with :data:`MISSING_DOSAGE` where
    the sample is no-called. ``called`` is DERIVED on access rather than stored,
    which is what keeps the decode cache's bound at ``cache_variants * n_samples``
    bytes instead of twice that.
    """

    dosage: np.ndarray

    @property
    def called(self) -> np.ndarray:
        """Boolean mask of non-missing genotypes."""
        return self.dosage >= 0


def _count_lines(path: Path) -> int:
    """Count non-blank lines in a text file without holding it all at once."""
    n = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


class BedReader:
    """Seek-by-index plink1 ``.bed`` reader. Reads ONLY the blocks asked for.

    Every structural property of the trio is validated at construction, in this
    order, each with its own message: magic -> mode -> file size (which is also
    what makes a ``.bim``/``.fam`` line-count disagreement loud). Index bounds are
    validated per read. All of them RAISE; see the module docstring for why none
    may be a warning.
    """

    def __init__(self, bfile_prefix: "str | Path", *, cache_variants: int = 2048) -> None:
        if cache_variants < 1:
            raise ValueError(f"cache_variants must be >= 1, got {cache_variants}")
        prefix = Path(bfile_prefix)
        self.prefix = prefix
        self.bed_path = prefix.with_suffix(".bed")
        self.bim_path = prefix.with_suffix(".bim")
        self.fam_path = prefix.with_suffix(".fam")
        for path in (self.bed_path, self.bim_path, self.fam_path):
            if not path.exists():
                raise FileNotFoundError(
                    f"missing bfile component for prefix {prefix}: {path}"
                )

        self.n_samples: int = _count_lines(self.fam_path)
        self.n_variants: int = _count_lines(self.bim_path)
        if self.n_samples < 1:
            raise ValueError(f"empty .fam (0 samples): {self.fam_path}")
        if self.n_variants < 1:
            raise ValueError(f"empty .bim (0 variants): {self.bim_path}")
        self.bytes_per_variant: int = (self.n_samples + 3) // 4

        self.cache_variants = int(cache_variants)
        self._cache: "OrderedDict[int, np.ndarray]" = OrderedDict()

        self._fh = open(self.bed_path, "rb")
        try:
            header = self._fh.read(3)
            if len(header) < 3:
                raise ValueError(
                    f"truncated .bed header for {self.bed_path}: expected 3 bytes, "
                    f"got {len(header)}"
                )
            if bytes(header[:2]) != BED_MAGIC:
                raise ValueError(
                    f"bad .bed magic bytes in {self.bed_path}: expected "
                    f"{BED_MAGIC.hex()}, observed {bytes(header[:2]).hex()}"
                )
            mode = header[2]
            if mode == BED_MODE_INDIVIDUAL_MAJOR:
                raise ValueError(
                    f"unsupported .bed mode byte 0x{mode:02x} in {self.bed_path}: "
                    "this is INDIVIDUAL-major layout; this reader decodes only "
                    f"SNP-major (0x{BED_MODE_SNP_MAJOR:02x}). Decoding it as "
                    "SNP-major would transpose the matrix silently."
                )
            if mode != BED_MODE_SNP_MAJOR:
                raise ValueError(
                    f"unknown .bed mode byte 0x{mode:02x} in {self.bed_path}: "
                    f"expected SNP-major 0x{BED_MODE_SNP_MAJOR:02x} or "
                    f"individual-major 0x{BED_MODE_INDIVIDUAL_MAJOR:02x}"
                )

            expected = 3 + self.n_variants * self.bytes_per_variant
            actual = self.bed_path.stat().st_size
            if actual != expected:
                raise ValueError(
                    f".bed file size mismatch for {self.bed_path}: expected "
                    f"{expected} bytes, actual {actual} bytes. Expected size is "
                    f"3 + n_variants * bytes_per_variant with n_variants="
                    f"{self.n_variants} (from {self.bim_path.name}, a .bim line "
                    f"count) and n_samples={self.n_samples} (from "
                    f"{self.fam_path.name}) -> bytes_per_variant="
                    f"{self.bytes_per_variant}. A disagreement means the trio is "
                    "mismatched; seek-by-index would address the wrong blocks."
                )
        except BaseException:
            self._fh.close()
            raise

    # -- context manager sugar ------------------------------------------- #
    def __enter__(self) -> "BedReader":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying ``.bed`` handle (idempotent)."""
        fh = getattr(self, "_fh", None)
        if fh is not None and not fh.closed:
            fh.close()

    # -- the read path ---------------------------------------------------- #
    def _decode_block(self, raw: bytes) -> np.ndarray:
        """Decode one packed variant block into an int8 dosage array.

        Vectorised shift-and-mask, then TRUNCATE to ``n_samples`` — the
        truncation IS the padding fix (a reshape without it manufactures up to
        three phantom samples per variant).
        """
        block = np.frombuffer(raw, dtype=np.uint8)
        codes = (block[:, None] >> _BIT_SHIFTS) & 3
        flat = codes.ravel()[: self.n_samples]
        return _CODE_TO_DOSAGE[flat]

    def read_variant(self, index: int) -> Genotypes:
        """Return :class:`Genotypes` for the GLOBAL 0-based ``.bim`` row ``index``.

        ``index`` is GLOBAL — a row number in the prefix's own ``.bim``. Passing a
        window-relative index reads a different variant with no error; see the
        module docstring's global-index rule.
        """
        idx = int(index)
        if idx < 0 or idx >= self.n_variants:
            raise IndexError(
                f"variant index {idx} out of range for {self.bed_path}: "
                f"n_variants={self.n_variants} (valid 0..{self.n_variants - 1})"
            )
        cached = self._cache.get(idx)
        if cached is not None:
            self._cache.move_to_end(idx)
            return Genotypes(cached)

        offset = 3 + index * self.bytes_per_variant
        self._fh.seek(offset)
        raw = self._fh.read(self.bytes_per_variant)
        if len(raw) != self.bytes_per_variant:
            raise ValueError(
                f"short read at variant {idx} of {self.bed_path}: expected "
                f"{self.bytes_per_variant} bytes at offset {offset}, got {len(raw)}"
            )
        dosage = self._decode_block(raw)
        self._cache[idx] = dosage
        while len(self._cache) > self.cache_variants:
            self._cache.popitem(last=False)
        return Genotypes(dosage)


def main(argv: "list[str] | None" = None) -> int:  # pragma: no cover - T3 builds this
    """CLI entry point. Implemented in T3."""
    raise NotImplementedError("the CLI lands in T3")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
