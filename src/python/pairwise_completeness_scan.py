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


# =========================================================================== #
# Candidate enumeration — BOTH SIDES, under ONE signed convention             #
# =========================================================================== #

class CandidatePair(NamedTuple):
    """One ORDERED (anchor deletion, partner) candidate row.

    A deletion-deletion neighbour therefore yields TWO rows — one per anchor,
    each carrying its OWN anchor-relative offset — but ONE distinct
    :attr:`pair_key`. The region summary reports ``n_candidate_rows`` AND
    ``n_distinct_pairs`` so neither can be quoted as the other.
    """

    region_id: str
    del_index: int
    del_vid: str
    del_chr: str
    del_pos: int
    del_ref_len: int
    del_span_end: int
    partner_index: int
    partner_vid: str
    partner_pos: int
    offset: int
    side: str
    already_occluded: bool
    pair_key: str


def span_offset(deletion, variant) -> int:
    """SIGNED DISTANCE from ``deletion``'s REF interval ``[pos, span_end]``.

    ``variant.pos <  deletion.pos``        -> ``variant.pos - deletion.pos``
                                             (NEGATIVE, upstream)
    ``deletion.pos <= variant.pos <= span_end`` -> ``0`` (interior; BOTH ends
                                             inclusive, so a CO-LOCATED variant
                                             is offset 0)
    ``variant.pos >  deletion.span_end``   -> ``variant.pos - deletion.span_end``
                                             (POSITIVE, downstream)

    The offset is ANCHOR-relative and is therefore NOT symmetric for a
    deletion-deletion pair; that is the convention, not a defect.

    ⚠ ``offset == 0`` is NOT the same predicate as ``already_occluded``. The
    POSTED occlusion rule's left bound is STRICT
    (``d.pos < v.pos <= d.span_end``), so a co-located variant has offset 0 and
    ``already_occluded is False``. Conflating them would silently reclassify
    "newly discovered" as "already covered".

    The MEASURED ``m2_region_00057`` partner sits at offset ``+1``.
    """
    if variant.pos < deletion.pos:
        return variant.pos - deletion.pos
    if variant.pos > deletion.span_end:
        return variant.pos - deletion.span_end
    return 0


def side_for_offset(offset: int) -> str:
    """``"upstream"`` | ``"interior"`` | ``"downstream"`` for a signed offset."""
    if offset < 0:
        return "upstream"
    if offset > 0:
        return "downstream"
    return "interior"


def _norm_chrom(value) -> str:
    """Normalise a ``.bim`` chromosome field: ``chr15`` and ``15`` are the same."""
    text = str(value).strip().lower()
    return text[3:] if text.startswith("chr") else text


def enumerate_candidates(
    region_id: str,
    indexed_rows: Sequence,
    *,
    window_bp: int = DEFAULT_WINDOW_BP,
) -> list[CandidatePair]:
    """Enumerate every (deletion, partner) candidate within ``+/- window_bp``.

    ``indexed_rows`` is a sequence of ``(GLOBAL 0-based .bim index, 6-field row)``
    pairs, SORTED by position ascending (:func:`iter_bim_windows` produces exactly
    that). Unsorted input RAISES — the windowing is a binary search and would
    silently under-enumerate otherwise. Mixed chromosomes RAISE: a window is
    single-chromosome by contract.

    ``window_bp`` is a MEASUREMENT parameter swept on BOTH sides. The posted
    occlusion rule is one-sided, but alignment ambiguity at an indel is not
    directional, so an upstream partner is enumerated with a NEGATIVE offset.
    Nothing is excluded or decided on the basis of this window.
    """
    if window_bp < 0:
        raise ValueError(f"window_bp must be >= 0, got {window_bp}")

    variants: list[tuple] = []
    chroms: set[str] = set()
    raw_chroms: list[str] = []
    prev_pos: "int | None" = None
    for global_index, row in indexed_rows:
        variant = parse_bim_row(row, index=int(global_index))
        if prev_pos is not None and variant.pos < prev_pos:
            raise ValueError(
                f"region {region_id}: .bim rows must be sorted by position "
                f"ascending (binary-search windowing depends on the order); "
                f"saw {variant.pos} after {prev_pos}"
            )
        prev_pos = variant.pos
        chrom = str(row[_COL_CHR])
        chroms.add(_norm_chrom(chrom))
        raw_chroms.append(chrom)
        variants.append(variant)

    if len(chroms) > 1:
        raise ValueError(
            f"region {region_id}: a window is single-chromosome by contract, "
            f"got chromosomes {sorted(chroms)}"
        )

    positions = [v.pos for v in variants]
    pairs: list[CandidatePair] = []
    for anchor_i, deletion in enumerate(variants):
        if not deletion.is_deletion:
            continue  # footprint is len(REF) ONLY: an SNV/insertion anchors nothing
        lo_bp = deletion.pos - window_bp
        hi_bp = deletion.span_end + window_bp
        lo = bisect_left(positions, lo_bp)
        hi = bisect_right(positions, hi_bp)   # INCLUSIVE at exactly +window_bp
        for j in range(lo, hi):
            partner = variants[j]
            if partner.index == deletion.index:
                continue  # never a self-pair
            offset = span_offset(deletion, partner)
            pairs.append(
                CandidatePair(
                    region_id=region_id,
                    del_index=deletion.index,
                    del_vid=deletion.vid,
                    del_chr=raw_chroms[anchor_i],
                    del_pos=deletion.pos,
                    del_ref_len=deletion.ref_len,
                    del_span_end=deletion.span_end,
                    partner_index=partner.index,
                    partner_vid=partner.vid,
                    partner_pos=partner.pos,
                    offset=offset,
                    side=side_for_offset(offset),
                    # THE POSTED RULE, computed separately and never conflated
                    # with `offset == 0`. Strict left bound.
                    already_occluded=bool(
                        deletion.pos < partner.pos <= deletion.span_end
                    ),
                    pair_key="|".join(sorted((deletion.vid, partner.vid))),
                )
            )
    return pairs


def iter_bim_windows(bim_path: "str | Path", windows: Iterable) -> dict:
    """ONE streaming pass over the FULL ``.bim``; GLOBAL 0-based indices out.

    ``windows`` is an iterable of ``(region_id, chrom, start_bp, end_bp)``
    (both bounds inclusive). Returns ``{region_id: [(global_index, row), ...]}``
    with rows in file order, which is position order within a chromosome.

    The GLOBAL index is what :meth:`BedReader.read_variant` requires. This
    function exists precisely so no caller is ever tempted to hand it a
    window-relative index off a pre-extracted window ``.bim``; see the module
    docstring and ``test_window_relative_index_reads_the_wrong_block``.
    """
    specs = [
        (str(region_id), _norm_chrom(chrom), int(start_bp), int(end_bp))
        for region_id, chrom, start_bp, end_bp in windows
    ]
    out: dict = {region_id: [] for region_id, _c, _s, _e in specs}

    with open(bim_path, "r", encoding="utf-8") as fh:
        index = -1
        for line in fh:
            if not line.strip():
                continue
            index += 1
            row = line.split()[:6]
            if len(row) < 6:
                raise ValueError(
                    f"malformed .bim row at index {index} of {bim_path}: "
                    f"expected >=6 fields, got {len(row)}: {row!r}"
                )
            row_chrom = _norm_chrom(row[_COL_CHR])
            try:
                pos = int(row[_COL_BP])
            except ValueError as exc:
                raise ValueError(
                    f"malformed .bim row at index {index} of {bim_path}: bp "
                    f"field {row[_COL_BP]!r} is not an integer"
                ) from exc
            for region_id, chrom, start_bp, end_bp in specs:
                if row_chrom == chrom and start_bp <= pos <= end_bp:
                    out[region_id].append((index, row))
    return out


# =========================================================================== #
# THE PAIRWISE TEST (the property, directly) and the CARRIERS-LOST GRADIENT   #
# =========================================================================== #

class PairResult(NamedTuple):
    """One evaluated candidate row: the :class:`CandidatePair` fields plus the
    pairwise verdict and the gradient. Field order IS :data:`TSV_COLUMNS`."""

    region_id: str
    del_index: int
    del_vid: str
    del_chr: str
    del_pos: int
    del_ref_len: int
    del_span_end: int
    partner_index: int
    partner_vid: str
    partner_pos: int
    offset: int
    side: str
    already_occluded: bool
    pair_key: str
    n_called_del: int
    n_called_partner: int
    n_both_called: int
    del_invariant: bool
    partner_invariant: bool
    undefined: bool
    invariant_member: str
    del_carriers_marginal: int
    del_carriers_retained: int
    del_carriers_lost: int
    del_carriers_lost_frac: float
    del_maf_marginal: float
    partner_carriers_marginal: int
    partner_carriers_retained: int
    partner_carriers_lost: int
    partner_carriers_lost_frac: float
    partner_maf_marginal: float
    confounding_pattern: str


def _minor_allele_carriers(dosage: np.ndarray, called: np.ndarray):
    """``(carrier_mask, maf_marginal)`` with the minor allele chosen EMPIRICALLY.

    The minor allele is decided over the member's OWN called set: A1 when
    ``sum(dosage) / 2 / n_called <= 0.5``, else A2. A carrier holds >= 1 copy of
    it. No frequency threshold and no reference panel is consulted.
    """
    n_called = int(called.sum())
    if n_called == 0:
        return np.zeros(dosage.shape, dtype=bool), 0.0
    af_a1 = float(dosage[called].sum()) / (2.0 * n_called)
    if af_a1 <= 0.5:
        mask = dosage >= 1                      # >= 1 copy of A1
    else:
        mask = (dosage >= 0) & (dosage <= 1)    # >= 1 copy of A2
    return mask & called, min(af_a1, 1.0 - af_a1)


def _gradient(carrier_mask: np.ndarray, both: np.ndarray):
    """``(marginal, retained, lost, lost_frac)`` carriers for one member.

    ``lost_frac`` is 0.0 when the member has no carriers at all, so it is never
    a divide-by-zero and never a NaN in the emitted TSV.
    """
    marginal = int(carrier_mask.sum())
    retained = int((carrier_mask & both).sum())
    lost = marginal - retained
    lost_frac = (lost / marginal) if marginal > 0 else 0.0
    return marginal, retained, lost, lost_frac


def _confounding_pattern(
    n_both_called: int,
    del_invariant: bool,
    partner_invariant: bool,
    del_carriers_marginal: int,
    del_carriers_lost_frac: float,
    partner_carriers_marginal: int,
    partner_carriers_lost_frac: float,
) -> str:
    """A DERIVED LABEL ONLY — never the test. See the module docstring.

    ``carriers(X) ⊆ missing(Y)`` shows up HERE and nowhere else: it is what
    distinguishes ``perfect_*_confounding`` from ``partial``, after
    :func:`evaluate_pair` has already decided ``undefined`` from the property.
    """
    if n_both_called == 0:
        return "empty_intersection"
    if del_invariant and del_carriers_marginal > 0 and del_carriers_lost_frac == 1.0:
        return "perfect_deletion_confounding"
    if (
        partner_invariant
        and partner_carriers_marginal > 0
        and partner_carriers_lost_frac == 1.0
    ):
        return "perfect_partner_confounding"
    if max(del_carriers_lost_frac, partner_carriers_lost_frac) > 0.0:
        return "partial"
    return "none"


def evaluate_pair(reader: BedReader, pair: CandidatePair) -> PairResult:
    """Decide UNDEFINED for one candidate pair and record the gradient.

    THE PROPERTY, stated directly: within ``called(X) ∩ called(Y)``, is X
    constant, or is Y constant? An empty intersection is the degenerate TRUE
    case. BOTH members are tested — the deletion is not assumed to be the
    collapsing one. There is NO set-containment test on this path.
    """
    geno_del = reader.read_variant(pair.del_index)
    geno_partner = reader.read_variant(pair.partner_index)
    dosage_del = geno_del.dosage
    dosage_partner = geno_partner.dosage
    called_del = geno_del.called
    called_partner = geno_partner.called
    both = called_del & called_partner
    n_both_called = int(both.sum())

    if n_both_called == 0:
        # DEGENERATE TRUE CASE — no pairwise-complete sample exists at all.
        del_invariant = True
        partner_invariant = True
    else:
        del_invariant = bool(np.unique(dosage_del[both]).size == 1)
        partner_invariant = bool(np.unique(dosage_partner[both]).size == 1)

    # THE PRIMARY TEST. Never a containment shortcut — see
    # test_undefined_without_carriers_subset_of_missing.
    undefined = bool(del_invariant or partner_invariant)

    if del_invariant and partner_invariant:
        invariant_member = "both"
    elif del_invariant:
        invariant_member = "deletion"
    elif partner_invariant:
        invariant_member = "partner"
    else:
        invariant_member = "none"

    del_carrier_mask, del_maf = _minor_allele_carriers(dosage_del, called_del)
    partner_carrier_mask, partner_maf = _minor_allele_carriers(
        dosage_partner, called_partner
    )
    del_marginal, del_retained, del_lost, del_lost_frac = _gradient(
        del_carrier_mask, both
    )
    p_marginal, p_retained, p_lost, p_lost_frac = _gradient(
        partner_carrier_mask, both
    )

    return PairResult(
        *pair,
        n_called_del=int(called_del.sum()),
        n_called_partner=int(called_partner.sum()),
        n_both_called=n_both_called,
        del_invariant=del_invariant,
        partner_invariant=partner_invariant,
        undefined=undefined,
        invariant_member=invariant_member,
        del_carriers_marginal=del_marginal,
        del_carriers_retained=del_retained,
        del_carriers_lost=del_lost,
        del_carriers_lost_frac=del_lost_frac,
        del_maf_marginal=del_maf,
        partner_carriers_marginal=p_marginal,
        partner_carriers_retained=p_retained,
        partner_carriers_lost=p_lost,
        partner_carriers_lost_frac=p_lost_frac,
        partner_maf_marginal=partner_maf,
        confounding_pattern=_confounding_pattern(
            n_both_called,
            del_invariant,
            partner_invariant,
            del_marginal,
            del_lost_frac,
            p_marginal,
            p_lost_frac,
        ),
    )


def scan_region(
    reader: BedReader,
    region_id: str,
    indexed_rows: Sequence,
    *,
    window_bp: int = DEFAULT_WINDOW_BP,
) -> list[PairResult]:
    """Enumerate then evaluate every candidate row for ONE region.

    Every genotype read goes through :meth:`BedReader.read_variant`, so the
    ``.bed`` is opened once and only candidate blocks are ever touched.
    """
    pairs = enumerate_candidates(region_id, indexed_rows, window_bp=window_bp)
    return [evaluate_pair(reader, pair) for pair in pairs]


def main(argv: "list[str] | None" = None) -> int:  # pragma: no cover - T3 builds this
    """CLI entry point. Implemented in T3."""
    raise NotImplementedError("the CLI lands in T3")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
