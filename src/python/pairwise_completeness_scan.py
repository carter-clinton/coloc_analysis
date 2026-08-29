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

SAMPLE POLICY — A COUPLING, NOT AN ASSUMPTION
---------------------------------------------
This scanner counts EVERY ``.fam`` row and evaluates EVERY sample; it applies no
founder filter. plink1.9's LD calculations consider FOUNDERS ONLY by default.
The production square command
(``aou_ld_panel.build_plink_ld_command``) passes ``--nonfounders``, so
all-samples is the MATCHING policy and the two are comparable.

**If ``--nonfounders`` is ever dropped from that command, this scanner must
switch to founders-only or its verdicts become non-comparable** — it would call a
pair defined on the strength of samples plink never looked at. That is a COUPLING
between two modules, so it has a named enforcer rather than a sentence:
``tests/m3/test_pairwise_completeness_scan.py::test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag``
parses ``build_plink_ld_command`` and fails if the flag leaves its square branch.
The scanner is NOT changed here: the review filed the founders question as a
defect, and it is re-dispositioned to a DOCUMENTED-AND-ENFORCED coupling because
production already passes the flag.

REGION EDGES — CLIPPED BY DESIGN, COUNTED SO IT IS NEVER SILENT
---------------------------------------------------------------
A region's universe is EXACTLY that region's own LD matrix — the variants plink
retained inside ``--from-bp``/``--to-bp``. A variant OUTSIDE those bounds is not a
row of that matrix and therefore cannot produce a NaN in it, so declining to emit
a pair that reaches past the boundary is CORRECT. The defect was that the
suppression was SILENT: a deletion at a region edge simply looked like a deletion
with fewer neighbours.

:func:`iter_bim_windows` therefore accepts ``pad_bp`` and, in the SAME single
streaming pass, also returns the ``[start - pad, end + pad]`` flanks;
:func:`enumerate_candidates` takes ``region_bounds`` and emits ONLY in-bounds
anchors with in-bounds partners (so the emitted set is IDENTICAL to an unpadded
run — pinned by
``test_no_emitted_row_references_a_variant_outside_the_region``); and
:func:`count_edge_clipped_candidates` reports how many ordered rows the boundary
suppressed, as ``n_candidates_edge_clipped``.

ANCHOR-side clipping (a deletion OUTSIDE the region whose span reaches in) is out
of scope for the same reason: such a deletion is not a row of that region's
matrix either, so no pair containing it exists there at all.

RETAINED-SET PARITY (``--exclude`` / ``--mac 1``)
--------------------------------------------------
The production matrix is built on the RETAINED set — post ``--exclude`` (the
occlusion manifest) and post ``--mac 1`` (MAC-0 variants dropped). This scanner
enumerates the FULL window ``.bim``. The two sides of that gap are made visible
rather than assumed away:

* the ``--exclude`` side is already visible as ``already_occluded``;
* the ``--mac 1`` side is the new ``del_globally_invariant`` /
  ``partner_globally_invariant`` columns and the ``n_globally_invariant_variants``
  / ``n_undefined_rows_with_globally_invariant_member`` counters. A member is
  "globally invariant" when it is constant within its OWN called set.

The set relation, in the correct direction: ``{MAC 0} ⊆ {invariant within its own
called set}``. A MAC-0 variant is necessarily invariant among its called samples;
the CONVERSE IS FALSE — an all-heterozygous variant is invariant here yet has
``MAC == n_called``. A globally invariant variant makes EVERY pair containing it
read as undefined, which would be an OVER-report relative to a matrix that never
contained it. Both observed regions reported ``n_dropped_monomorphic = 0``, but
that is a measurement of two regions and not a guarantee, so the class is COUNTED
and SUBTRACTABLE instead of folded into the undefined total.

THE MINOR-ALLELE TIE RULE
-------------------------
The carriers-lost gradient is computed over the member's MINOR allele, decided
EMPIRICALLY over that member's own called set. When ``af_a1`` is EXACTLY 0.5
there is no minor allele: the two are equally frequent, and picking one by fiat
(the shipped rule picked A1) can report a member whose OTHER allele lost most of
its carriers to the partner's missingness as entirely unaffected — precisely the
partial-confounding tail this instrument exists to find, binned as reassuring.
At the exact tie the gradient is therefore computed for BOTH alleles and the
LARGER ``lost_frac`` is reported (ties broken by the larger ``lost`` count, then
by A1), and the emitted ``del_minor_allele_tie`` / ``partner_minor_allele_tie``
columns make the tie visible so the choice is never invisible in the output. For
every ``af_a1 != 0.5`` the numbers are IDENTICAL to the shipped behaviour.

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
from collections import Counter, OrderedDict
from datetime import datetime, timezone
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


def _as_variant_index(value) -> int:
    """Normalise a variant index to an ``int``, or RAISE. Never truncate.

    Accepts ``int`` / ``np.integer`` / a digit ``str`` / an INTEGRAL ``float``.

    RAISES ``ValueError`` on a NON-INTEGRAL float. ``int(1.5) == 1`` would seek to
    variant 1 and return a perfectly well-formed dosage array for the WRONG
    VARIANT with no error anywhere — the same wrong-genotype-read failure class
    the module's GLOBAL-INDEX rule exists to prevent. Anything ``int()`` itself
    rejects also raises, as a ``ValueError`` naming the offending value.

    The value this returns is BOTH the bounds-checked quantity AND the addressed
    quantity in :meth:`BedReader.read_variant` — see
    ``test_seek_offset_uses_the_normalised_index``.
    """
    if isinstance(value, (float, np.floating)):
        if not float(value).is_integer():
            raise ValueError(
                f"non-integral variant index {value!r}: a variant index must be a "
                "whole number. Truncating it would seek a DIFFERENT .bed block and "
                "return a well-formed dosage array for the wrong variant, with no "
                "error anywhere."
            )
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"invalid variant index {value!r} ({type(value).__name__}): {exc}"
        ) from exc


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
        idx = _as_variant_index(index)
        if idx < 0 or idx >= self.n_variants:
            raise IndexError(
                f"variant index {idx} out of range for {self.bed_path}: "
                f"n_variants={self.n_variants} (valid 0..{self.n_variants - 1})"
            )
        cached = self._cache.get(idx)
        if cached is not None:
            self._cache.move_to_end(idx)
            return Genotypes(cached)

        # The BOUNDS-CHECKED quantity IS the ADDRESSED quantity. Never `index`.
        offset = 3 + idx * self.bytes_per_variant
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


def _pair_key(index_a: int, index_b: int) -> str:
    """Order-normalised key over the two GLOBALLY-UNIQUE ``.bim`` ROW INDICES.

    NEVER the variant ids. Two rows can share an id — a bare ``.`` and a
    duplicated rsID are both ordinary ``.bim`` occurrences — and an id-keyed pair
    key COLLAPSES two DISTINCT pairs into one. That is an UNDERCOUNT, which is the
    dangerous direction: every denominator derived from ``n_distinct_pairs`` would
    be too small and the undefined already-occluded/newly-discovered split would be
    computed over the wrong set. The vids stay on the row, for display only.

    A deletion-deletion neighbour still yields TWO ordered rows and ONE key: the
    sorted index pair is identical from either anchor.
    """
    lo, hi = sorted((int(index_a), int(index_b)))
    return f"{lo}|{hi}"


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


def _prepare_variants(region_id: str, indexed_rows: Sequence):
    """``(variants, raw_chroms)`` from ``(global_index, row)`` pairs, VALIDATED.

    Unsorted input RAISES — the windowing is a binary search and would silently
    under-enumerate otherwise. Mixed chromosomes RAISE: a window is
    single-chromosome by contract. Shared by :func:`enumerate_candidates` and
    :func:`count_edge_clipped_candidates` so the two can never disagree about
    which rows exist.
    """
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
    return variants, raw_chroms


def _in_bounds(pos: int, region_bounds) -> bool:
    """``region_bounds is None`` -> everything is in bounds (today's behaviour)."""
    if region_bounds is None:
        return True
    return int(region_bounds[0]) <= pos <= int(region_bounds[1])


def enumerate_candidates(
    region_id: str,
    indexed_rows: Sequence,
    *,
    window_bp: int = DEFAULT_WINDOW_BP,
    region_bounds: "tuple[int, int] | None" = None,
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

    ``region_bounds=None`` is TODAY'S BEHAVIOUR EXACTLY. When given as
    ``(start_bp, end_bp)`` (both inclusive), a deletion ANCHORS only if it is in
    bounds and a partner is EMITTED only if it is in bounds, so the emitted set is
    IDENTICAL to an unpadded run even when ``indexed_rows`` carries padded flanks.
    See the module docstring's REGION EDGES section.
    """
    if window_bp < 0:
        raise ValueError(f"window_bp must be >= 0, got {window_bp}")

    variants, raw_chroms = _prepare_variants(region_id, indexed_rows)

    positions = [v.pos for v in variants]
    pairs: list[CandidatePair] = []
    for anchor_i, deletion in enumerate(variants):
        if not deletion.is_deletion:
            continue  # footprint is len(REF) ONLY: an SNV/insertion anchors nothing
        if not _in_bounds(deletion.pos, region_bounds):
            continue  # not a row of this region's matrix; it anchors nothing HERE
        lo_bp = deletion.pos - window_bp
        hi_bp = deletion.span_end + window_bp
        lo = bisect_left(positions, lo_bp)
        hi = bisect_right(positions, hi_bp)   # INCLUSIVE at exactly +window_bp
        for j in range(lo, hi):
            partner = variants[j]
            if partner.index == deletion.index:
                continue  # never a self-pair
            if not _in_bounds(partner.pos, region_bounds):
                # CLIPPED BY DESIGN — counted by count_edge_clipped_candidates,
                # never emitted: it is not a row of this region's LD matrix.
                continue
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
                    # INDEX-keyed, never vid-keyed: two rows sharing a `.` id are
                    # DISTINCT pairs and a vid key UNDERCOUNTS them. See _pair_key.
                    pair_key=_pair_key(deletion.index, partner.index),
                )
            )
    return pairs


def count_edge_clipped_candidates(
    region_id: str,
    indexed_rows: Sequence,
    *,
    window_bp: int = DEFAULT_WINDOW_BP,
    region_bounds: "tuple[int, int]",
) -> int:
    """ORDERED candidate ROWS the region boundary suppressed. Counted, not emitted.

    An IN-BOUNDS deletion's ``+/- window_bp`` reach may cover a partner OUTSIDE
    ``region_bounds``. That pair cannot exist in this region's LD matrix, so
    :func:`enumerate_candidates` correctly declines to emit it — this function is
    what stops that decision from being SILENT.

    ANCHOR-side clipping is deliberately NOT counted: a deletion outside the
    region is not a row of that region's matrix, so no pair containing it exists
    there at all. ``indexed_rows`` must therefore carry the padded flanks
    (:func:`iter_bim_windows` with ``pad_bp >= window_bp``) or this returns 0 by
    construction.
    """
    if window_bp < 0:
        raise ValueError(f"window_bp must be >= 0, got {window_bp}")
    start_bp, end_bp = int(region_bounds[0]), int(region_bounds[1])

    variants, _raw_chroms = _prepare_variants(region_id, indexed_rows)
    positions = [v.pos for v in variants]

    clipped = 0
    for deletion in variants:
        if not deletion.is_deletion:
            continue
        if not (start_bp <= deletion.pos <= end_bp):
            continue  # anchor-side clipping is out of scope — see the docstring
        lo = bisect_left(positions, deletion.pos - window_bp)
        hi = bisect_right(positions, deletion.span_end + window_bp)
        for j in range(lo, hi):
            partner = variants[j]
            if partner.index == deletion.index:
                continue
            if start_bp <= partner.pos <= end_bp:
                continue
            clipped += 1
    return clipped


def _assert_unique_region_ids(windows) -> None:
    """Raise ``ValueError`` if any ``region_id`` appears more than once.

    WHY THIS IS A HARD ERROR AND NOT A SILENT DEDUPE — the mechanism that turned
    an ancestry-blind manifest read into an 8x inflation of a whole sweep:

    * :func:`iter_bim_windows` builds ``specs`` as a **LIST** and ``out`` as a
      **DICT** keyed on ``region_id``, so a repeated id appends each matching
      ``.bim`` row ONCE PER MATCHING SPEC -> rows 2x -> ``deletion x partner``
      candidate pairs 4x.
    * :func:`main`'s driver then writes ``summaries[region_id] = ...``
      (**LAST-WINS**) while ``all_results.extend(...)`` **ACCUMULATES**, so the
      region is evaluated twice: 8x in the emitted TSV, and two mutually
      inconsistent denominators in the same stdout block.
    * the per-region stdout table iterates the **LIST** while looking up the
      **DICT**, so every region prints twice with identical values.

    A dedupe would hide all of that. The raise makes it loud, at the earliest
    layer that can see it. Enforcers:
    ``test_iter_bim_windows_duplicate_region_id_identical_bounds_raises`` (CASE A,
    identical bounds), ``..._differing_bounds_raises`` (CASE B, the non-uniform
    shape), and the CONTROL
    ``test_iter_bim_windows_single_region_id_control_still_returns_six_rows``,
    which must stay GREEN — a guard that raised on everything would be worthless.
    """
    counts = Counter(str(window[0]) for window in windows)
    duplicates = {rid: n for rid, n in counts.items() if n > 1}
    if duplicates:
        raise ValueError(
            f"duplicate region_id(s) in windows: {duplicates} — a region_id must "
            f"appear at most ONCE; the manifest is keyed on "
            f"(region_id x ancestry), so an unfiltered read yields each region twice"
        )


def iter_bim_windows(
    bim_path: "str | Path",
    windows: Iterable,
    *,
    pad_bp: int = 0,
) -> dict:
    """ONE streaming pass over the FULL ``.bim``; GLOBAL 0-based indices out.

    ``windows`` is an iterable of ``(region_id, chrom, start_bp, end_bp)``
    (both bounds inclusive). Returns ``{region_id: [(global_index, row), ...]}``
    with rows in file order, which is position order within a chromosome.

    ``pad_bp=0`` is TODAY'S BEHAVIOUR EXACTLY. With ``pad_bp > 0`` the returned
    rows ALSO include the ``[start - pad, end + pad]`` flanks — in the SAME single
    pass, so N regions still cost ONE ``.bim`` open — which is what lets
    :func:`count_edge_clipped_candidates` see the partners the region boundary
    suppresses. The ``(global_index, row)`` tuple shape is UNCHANGED, and the
    padded rows never reach the output: :func:`enumerate_candidates` filters them
    out via ``region_bounds``.

    The GLOBAL index is what :meth:`BedReader.read_variant` requires. This
    function exists precisely so no caller is ever tempted to hand it a
    window-relative index off a pre-extracted window ``.bim``; see the module
    docstring and ``test_window_relative_index_reads_the_wrong_block``.
    """
    if pad_bp < 0:
        raise ValueError(f"pad_bp must be >= 0, got {pad_bp}")
    pad = int(pad_bp)
    # Materialize BEFORE the guard so an iterator argument is not consumed by it,
    # and guard BEFORE `specs` is built: a repeated region_id would otherwise
    # append every matching .bim row once per matching spec. The pad_bp check
    # stays FIRST so its error ordering is unchanged.
    windows = list(windows)
    _assert_unique_region_ids(windows)
    specs = [
        (str(region_id), _norm_chrom(chrom), int(start_bp) - pad, int(end_bp) + pad)
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
    del_globally_invariant: bool
    partner_invariant: bool
    partner_globally_invariant: bool
    undefined: bool
    invariant_member: str
    del_carriers_marginal: int
    del_carriers_retained: int
    del_carriers_lost: int
    del_carriers_lost_frac: float
    del_maf_marginal: float
    del_minor_allele_tie: bool
    partner_carriers_marginal: int
    partner_carriers_retained: int
    partner_carriers_lost: int
    partner_carriers_lost_frac: float
    partner_maf_marginal: float
    partner_minor_allele_tie: bool
    confounding_pattern: str


def _mask_gradient(carrier_mask: np.ndarray, both: np.ndarray):
    """``(marginal, retained, lost, lost_frac)`` carriers for one carrier mask.

    ``lost_frac`` is 0.0 when the mask holds no carriers at all, so it is never
    a divide-by-zero and never a NaN in the emitted TSV.
    """
    marginal = int(carrier_mask.sum())
    retained = int((carrier_mask & both).sum())
    lost = marginal - retained
    lost_frac = (lost / marginal) if marginal > 0 else 0.0
    return marginal, retained, lost, lost_frac


def _carrier_gradient(dosage: np.ndarray, called: np.ndarray, both: np.ndarray):
    """``(marginal, retained, lost, lost_frac, maf, minor_allele_tie, globally_invariant)``.

    The minor allele is decided EMPIRICALLY over the member's OWN called set —
    no frequency threshold and no reference panel is consulted:

    * ``af_a1 = dosage[called].sum() / (2 * n_called)``
    * ``af_a1 < 0.5`` -> the A1 carriers (``dosage >= 1``), ``tie`` False
    * ``af_a1 > 0.5`` -> the A2 carriers (``0 <= dosage <= 1``), ``tie`` False
    * ``af_a1 == 0.5`` -> **THE EXACT TIE.** There is no minor allele. The
      gradient is computed for BOTH masks and the one with the LARGER
      ``lost_frac`` is returned; ties are broken by the larger ``lost`` COUNT,
      and a full tie by A1. ``tie`` is True so the choice is visible in the
      emitted TSV. See the module docstring's THE MINOR-ALLELE TIE RULE for WHY
      a fiat choice at the tie can read a depleted member as reassuring.
    * ``n_called == 0`` -> an all-zero gradient, ``maf`` 0.0, ``tie`` False and
      ``globally_invariant`` True (the empty called set is invariant).

    ``globally_invariant`` is ``np.unique(dosage[called]).size <= 1``: the member
    is constant within its OWN called set, independent of any partner. It is
    RETAINED-SET PARITY bookkeeping, not a verdict — see the module docstring.

    Behaviour for every ``af_a1 != 0.5`` is IDENTICAL to the pre-remediation
    ``_minor_allele_carriers`` + ``_gradient`` pair this function replaces.
    """
    n_called = int(called.sum())
    if n_called == 0:
        return 0, 0, 0, 0.0, 0.0, False, True

    af_a1 = float(dosage[called].sum()) / (2.0 * n_called)
    maf = min(af_a1, 1.0 - af_a1)
    globally_invariant = bool(np.unique(dosage[called]).size <= 1)

    a1_mask = (dosage >= 1) & called                     # >= 1 copy of A1
    a2_mask = (dosage >= 0) & (dosage <= 1) & called     # >= 1 copy of A2

    if af_a1 < 0.5:
        return (*_mask_gradient(a1_mask, both), maf, False, globally_invariant)
    if af_a1 > 0.5:
        return (*_mask_gradient(a2_mask, both), maf, False, globally_invariant)

    # EXACT TIE: report the allele that LOST MORE, never A1 by fiat.
    g_a1 = _mask_gradient(a1_mask, both)
    g_a2 = _mask_gradient(a2_mask, both)
    chosen = g_a1 if (g_a1[3], g_a1[2]) >= (g_a2[3], g_a2[2]) else g_a2
    return (*chosen, maf, True, globally_invariant)


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

    (
        del_marginal,
        del_retained,
        del_lost,
        del_lost_frac,
        del_maf,
        del_tie,
        del_globally_invariant,
    ) = _carrier_gradient(dosage_del, called_del, both)
    (
        p_marginal,
        p_retained,
        p_lost,
        p_lost_frac,
        partner_maf,
        partner_tie,
        partner_globally_invariant,
    ) = _carrier_gradient(dosage_partner, called_partner, both)

    return PairResult(
        *pair,
        n_called_del=int(called_del.sum()),
        n_called_partner=int(called_partner.sum()),
        n_both_called=n_both_called,
        del_invariant=del_invariant,
        del_globally_invariant=del_globally_invariant,
        partner_invariant=partner_invariant,
        partner_globally_invariant=partner_globally_invariant,
        undefined=undefined,
        invariant_member=invariant_member,
        del_carriers_marginal=del_marginal,
        del_carriers_retained=del_retained,
        del_carriers_lost=del_lost,
        del_carriers_lost_frac=del_lost_frac,
        del_maf_marginal=del_maf,
        del_minor_allele_tie=del_tie,
        partner_carriers_marginal=p_marginal,
        partner_carriers_retained=p_retained,
        partner_carriers_lost=p_lost,
        partner_carriers_lost_frac=p_lost_frac,
        partner_maf_marginal=partner_maf,
        partner_minor_allele_tie=partner_tie,
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
    region_bounds: "tuple[int, int] | None" = None,
) -> list[PairResult]:
    """Enumerate then evaluate every candidate row for ONE region.

    Every genotype read goes through :meth:`BedReader.read_variant`, so the
    ``.bed`` is opened once and only candidate blocks are ever touched.

    ``region_bounds`` is a pass-through to :func:`enumerate_candidates`; ``None``
    is today's behaviour.
    """
    pairs = enumerate_candidates(
        region_id, indexed_rows, window_bp=window_bp, region_bounds=region_bounds
    )
    return [evaluate_pair(reader, pair) for pair in pairs]


# =========================================================================== #
# EGRESS-CLEAN emission — aggregate counts, fractions and COORDINATES only    #
# =========================================================================== #

#: The emitted TSV columns, in order. Pinned by EXACT tuple equality in the test
#: suite and identical to ``PairResult._fields`` (a must-be-identity link, so a
#: new field cannot silently escape the egress review).
TSV_COLUMNS: tuple = PairResult._fields

#: The per-region summary's key set, pinned by exact equality in the test suite.
#: COUNTS and FRACTIONS only: no key may name a rate, prevalence, estimate or
#: ceiling, because the prevalence, the boundary width and the partial-confounding
#: tail are OPEN questions that one region cannot answer.
SUMMARY_KEYS: tuple = (
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
    # --- REPORTING the two silent couplings (quick-260825-qpf) ------------- #
    "n_candidates_edge_clipped",
    "n_globally_invariant_variants",
    "n_undefined_rows_with_globally_invariant_member",
)

#: Bins for the DEFINED-row carriers-lost distribution. The top bin is OPEN at 1
#: on purpose: ``lost_frac == 1.0`` implies the member is invariant, which implies
#: the pair is UNDEFINED, so a defined row can never reach 1.0.
LOST_FRAC_BIN_LABELS: tuple = (
    "0",
    "(0,0.25]",
    "(0.25,0.5]",
    "(0.5,0.9]",
    "(0.9,0.99]",
    "(0.99,1)",
)


def _lost_frac_bin(value: float) -> str:
    """Bin one DEFINED row's ``max(del, partner)`` carriers-lost fraction."""
    if value <= 0.0:
        return "0"
    if value <= 0.25:
        return "(0,0.25]"
    if value <= 0.5:
        return "(0.25,0.5]"
    if value <= 0.9:
        return "(0.5,0.9]"
    if value <= 0.99:
        return "(0.9,0.99]"
    return "(0.99,1)"


def _render_field(value) -> str:
    """Render one scalar for the TSV, deterministically.

    Floats use ``repr`` (shortest round-trip) so the output is byte-stable across
    runs and independent of any memory knob.
    """
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        return repr(value)
    return str(value)


def write_tsv(results: Iterable[PairResult], path: "str | Path") -> None:
    """Write the per-pair TSV. Header EQUALS :data:`TSV_COLUMNS`, in order.

    EGRESS: every emitted field is a scalar — a count, a fraction, a variant
    coordinate or id, or a label. No per-sample vector, no sample identifier, no
    dosage ever reaches this file. In-perimeter the full TSV STAYS in-perimeter;
    only the aggregate summary is intended to cross.
    """
    out_path = Path(path)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\t".join(TSV_COLUMNS) + "\n")
        for result in results:
            fh.write(
                "\t".join(_render_field(getattr(result, col)) for col in TSV_COLUMNS)
                + "\n"
            )


def _quarantine_output(path: "str | Path", stamp: str) -> Path:
    """Move ``path`` aside to ``<path>.SUSPECT`` and return the new location.

    THE NAME IS BUILT BY STRING CONCATENATION, never by ``Path.with_suffix``.
    ``Path("pcs_pairs.tsv").with_suffix(".SUSPECT")`` is ``pcs_pairs.SUSPECT``:
    it DESTROYS the extension an operator greps for and collides with the
    summary's quarantine name (``pcs_summary.SUSPECT``). Pinned by
    ``test_the_quarantine_name_is_built_by_string_concatenation_not_with_suffix``.

    ROTATE, NEVER DELETE. If a ``.SUSPECT`` from an earlier disagreement is
    already there, it is first moved to ``<path>.SUSPECT.<stamp>`` so its bytes
    survive — the same project ruling that governs the in-perimeter artifacts
    (``.planning/debug/260824-STAGE-A-env-stop-plink1.9-and-stale-scratch-TSV.md``).
    """
    suspect = Path(str(path) + ".SUSPECT")
    if suspect.exists():
        suspect.replace(Path(str(suspect) + "." + stamp))
    Path(path).replace(suspect)
    return suspect


def summarize(
    region_id: str,
    results: Iterable[PairResult],
    *,
    window_bp: int = DEFAULT_WINDOW_BP,
    n_deletions: int,
    n_candidates_edge_clipped: int,
) -> dict:
    """Roll one region's results up into the aggregate that may cross the perimeter.

    The three quantities this exists to expose:

    * ``n_undefined_already_occluded`` vs ``n_undefined_not_already_occluded`` —
      separates pairs the POSTED criterion already covers from the NEWLY
      DISCOVERED class. The split is exhaustive over undefined DISTINCT pairs.
    * ``undefined_offset_histogram`` — ``{offset: count}`` over the UNDEFINED set,
      per ROW (each row carries one anchor-relative offset), so it sums to
      ``n_undefined_rows``. This DISTRIBUTION is what supplies an empirical
      boundary width instead of a guess. It is not itself a width.
    * ``defined_carriers_lost_frac_bins`` / ``n_defined_lost_frac_ge_0p9`` — the
      DEFINED-row tail, i.e. finite-``r`` pairs computed on carrier-depleted
      subsamples that no NaN check anywhere in the pipeline can see.

    Counts and fractions ONLY. Nothing here is a rate, and no single region's
    numbers may be read as a prevalence.
    """
    rows = list(results)
    undefined_rows = [r for r in rows if r.undefined]
    defined_rows = [r for r in rows if not r.undefined]

    undefined_keys = {r.pair_key for r in undefined_rows}
    # A DISTINCT pair counts as already-occluded if ANY of its ordered rows is.
    occluded_keys = {r.pair_key for r in undefined_rows if r.already_occluded}

    histogram: dict = {}
    for r in undefined_rows:
        key = str(r.offset)
        histogram[key] = histogram.get(key, 0) + 1
    histogram = {k: histogram[k] for k in sorted(histogram, key=int)}

    bins = {label: 0 for label in LOST_FRAC_BIN_LABELS}
    max_frac = 0.0
    n_tail = 0
    for r in defined_rows:
        frac = max(r.del_carriers_lost_frac, r.partner_carriers_lost_frac)
        bins[_lost_frac_bin(frac)] += 1
        if frac > max_frac:
            max_frac = frac
        if frac >= 0.9:
            n_tail += 1

    globally_invariant_indices: set = set()
    for r in rows:
        if r.del_globally_invariant:
            globally_invariant_indices.add(r.del_index)
        if r.partner_globally_invariant:
            globally_invariant_indices.add(r.partner_index)
    n_undefined_with_gi = sum(
        1
        for r in undefined_rows
        if r.del_globally_invariant or r.partner_globally_invariant
    )

    return {
        "region_id": region_id,
        "window_bp": int(window_bp),
        "n_deletions": int(n_deletions),
        "n_candidate_rows": len(rows),
        "n_distinct_pairs": len({r.pair_key for r in rows}),
        "n_undefined_rows": len(undefined_rows),
        "n_undefined_distinct_pairs": len(undefined_keys),
        "n_undefined_already_occluded": len(occluded_keys),
        "n_undefined_not_already_occluded": len(undefined_keys - occluded_keys),
        "undefined_offset_histogram": histogram,
        "defined_carriers_lost_frac_bins": bins,
        "max_carriers_lost_frac_defined": max_frac,
        "n_defined_lost_frac_ge_0p9": n_tail,
        "n_candidates_edge_clipped": int(n_candidates_edge_clipped),
        "n_globally_invariant_variants": len(globally_invariant_indices),
        "n_undefined_rows_with_globally_invariant_member": n_undefined_with_gi,
    }


# =========================================================================== #
# CLI                                                                         #
# =========================================================================== #

#: 0-based column indices in ``config/ld_regions.tsv``
#: (1-based 1 / 2 / 7 / 15 / 16).
#:
#: ⚠ THE MANIFEST IS KEYED ON ``(region_id x ancestry)``, NOT on ``region_id``
#: alone: 553 lines = 1 header + 276 region_ids x {AFR, EUR} = 552 data rows.
#: Reading it ancestry-BLIND returns EVERY window TWICE, which doubles the
#: ``.bim`` rows, quadruples the candidate pairs and — with the driver's
#: last-wins ``summaries`` dict against an accumulating ``all_results`` —
#: inflates the emitted row count by 8x. That is exactly what happened to the
#: 21-region STEP 3 sweep of 2026-08-26; see
#: ``.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md``.
_REGIONS_TSV_ID_COL = 0
_REGIONS_TSV_CHR_COL = 1
_REGIONS_TSV_ANCESTRY_COL = 6
_REGIONS_TSV_START_COL = 14
_REGIONS_TSV_END_COL = 15

#: The ancestry the scanner reads when none is named. LOAD-BEARING: the
#: already-written STEP 3 sweep command in
#: ``.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`` passes
#: NO ``--ancestry`` token, and the cohort it scans is ``afr_cohort``. Pinned by
#: ``test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing``.
DEFAULT_ANCESTRY = "AFR"


def _tsv_field(parts: "list[str]", index: int) -> str:
    """Return ``parts[index]`` stripped, or ``""`` if the row is too short.

    A NAMED, MODULE-LEVEL function rather than an inline expression so it can be
    unit-tested APART from :func:`_read_regions_tsv`'s row-length guard, which
    masks it: ``_REGIONS_TSV_ANCESTRY_COL`` (6) is less than
    ``_REGIONS_TSV_END_COL`` (15), so today every short row is already dropped
    before column 6 is touched. An inline expression would be
    untestable-by-construction and any test routed through the parser would be a
    FALSE INVARIANT — green whether or not the bounds tolerance exists. See
    ``test_tsv_field_is_bounds_tolerant_standalone`` and its companion
    ``test_read_regions_tsv_length_guard_masks_the_accessor_so_tsv_field_is_tested_alone``.
    """
    return parts[index].strip() if index < len(parts) else ""


def _matches_ancestry(row_value, ancestry) -> bool:
    """The manifest ancestry predicate, MIRRORED from production.

    The contract is ``run_native_ld_panel._filter_ancestry``
    (``src/python/run_native_ld_panel.py``), which every AoU LD-panel run already
    uses to split this same manifest into its AFR and EUR halves::

        [r for r in regions
         if str(r.get("ancestry", "")).upper() == ancestry.upper()]

    Two properties of that contract are reproduced deliberately:

    * ``str(...)`` on the row value, so a missing/None/NaN cell yields a string
      that matches no non-empty ancestry and the row is DROPPED — it never
      raises (the fail-safe shape).
    * NO ``.strip()``. Production does not strip, so ``"  AFR  "`` does NOT match
      ``"AFR"`` there. Whitespace tolerance in this module lives one layer UP, in
      :func:`_tsv_field`, which strips the cell before this predicate sees it —
      the composite parse is tolerant while the predicate stays a byte-faithful
      mirror. Putting the ``.strip()`` here instead would break the mirror on
      exactly one of the enforcer's 16 cases (MEASURED, quick-260826-qq9).

    Enforcer: ``test_ancestry_predicate_agrees_with_the_production_filter_contract``
    ast-extracts ``_filter_ancestry``'s SOURCE at call time and compares the two
    over a case table. It is a SYMBOL pin, not a whole-file SHA pin.
    """
    return str(row_value).upper() == str(ancestry).upper()


def _read_regions_tsv(
    path: "str | Path",
    region_ids: "list[str] | None",
    *,
    ancestry: str = DEFAULT_ANCESTRY,
):
    """Parse a ``config/ld_regions.tsv``-shaped manifest into window specs.

    The manifest is keyed on ``(region_id x ancestry)``, so ONLY rows matching
    ``ancestry`` (1-based column 7) are returned — see
    :data:`_REGIONS_TSV_ANCESTRY_COL`. Rows whose start/end columns are not
    integers (e.g. a header) are skipped.

    ``seen`` accumulates ONLY rows that pass the ancestry filter, so a
    ``region_ids`` entry that exists only in the OTHER ancestry raises the
    ``region ids not found in`` error rather than being silently dropped.
    """
    wanted = set(region_ids) if region_ids else None
    windows = []
    seen = set()
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) <= _REGIONS_TSV_END_COL:
            continue
        region_id = parts[_REGIONS_TSV_ID_COL].strip()
        try:
            start_bp = int(parts[_REGIONS_TSV_START_COL])
            end_bp = int(parts[_REGIONS_TSV_END_COL])
        except ValueError:
            continue  # header or a non-window row
        if not _matches_ancestry(_tsv_field(parts, _REGIONS_TSV_ANCESTRY_COL), ancestry):
            continue
        if wanted is not None and region_id not in wanted:
            continue
        windows.append((region_id, parts[_REGIONS_TSV_CHR_COL].strip(), start_bp, end_bp))
        seen.add(region_id)
    if wanted is not None:
        missing = sorted(wanted - seen)
        if missing:
            # The ancestry is named because the id may well BE in the file, in
            # the OTHER ancestry — without it the message would be misleading.
            raise ValueError(
                f"region ids not found in {path} for ancestry {ancestry!r}: {missing}"
            )
    return windows


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pairwise_completeness_scan",
        description=(
            "Measure PAIRWISE-COMPLETENESS around deletion REF spans: for each "
            "candidate (deletion, partner) pair, is one member constant within "
            "called(X) & called(Y) (so plink's r is UNDEFINED), and what fraction "
            "of each member's carriers is lost to the other's missingness? "
            "Reads ONLY the candidate variants' .bed blocks. Computes no LD. "
            "Changes no criterion, no threshold and no policy: it MEASURES."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--bfile-prefix", dest="bfile_prefix", type=Path, required=True,
        help=(
            "plink1 bfile prefix (.bed/.bim/.fam). The prefix's OWN .bim is "
            "streamed to derive GLOBAL 0-based variant indices; a pre-extracted "
            "window .bim would carry window-relative indices and silently read "
            "the WRONG .bed blocks."
        ),
    )
    parser.add_argument("--region-id", dest="region_id", help="single-region mode: region id")
    parser.add_argument("--chr", dest="chrom", help="single-region mode: chromosome ('15' or 'chr15')")
    parser.add_argument("--from-bp", dest="from_bp", type=int, help="single-region mode: window start (inclusive)")
    parser.add_argument("--to-bp", dest="to_bp", type=int, help="single-region mode: window end (inclusive)")
    parser.add_argument(
        "--regions-tsv", dest="regions_tsv", type=Path,
        help=(
            "multi-region mode: a config/ld_regions.tsv-shaped manifest "
            "(1-based cols 1 region_id, 2 chr, 7 ancestry, 15 window_start, "
            "16 window_end). The manifest is keyed on (region_id x ancestry) — "
            "276 ids x {AFR, EUR} = 552 data rows — so rows are selected by "
            "--ancestry as well as by id. ALL windows are served from ONE "
            "streaming .bim pass."
        ),
    )
    parser.add_argument(
        "--region-ids", dest="region_ids",
        help=(
            "comma-separated subset of --regions-tsv region ids. OMIT the flag "
            "to scan every region; a value that names no id after stripping "
            "(e.g. ' , ') is an ERROR and exits 2, NOT a silent all-region scan."
        ),
    )
    parser.add_argument(
        "--ancestry", dest="ancestry", default=DEFAULT_ANCESTRY,
        help=(
            "which ancestry's windows to read from --regions-tsv (1-based "
            "column 7; matched case-insensitively, exactly as "
            "run_native_ld_panel._filter_ancestry does). The manifest is keyed "
            "on (region_id x ancestry), so reading it BLIND returns every window "
            f"TWICE and silently doubles every row-basis count. Default {DEFAULT_ANCESTRY}."
        ),
    )
    parser.add_argument(
        "--window-bp", dest="window_bp", type=int, default=DEFAULT_WINDOW_BP,
        help=(
            "MEASUREMENT window (bp) on BOTH sides of the deletion REF span — "
            "not a threshold. Nothing is excluded, flagged or decided on the "
            f"basis of it; widening it costs reads, not validity. Default {DEFAULT_WINDOW_BP}."
        ),
    )
    parser.add_argument("--out", dest="out", type=Path, required=True, help="per-pair TSV output path")
    parser.add_argument("--summary", dest="summary", type=Path, help="per-region summary JSON output path")
    parser.add_argument(
        "--cache-variants", dest="cache_variants", type=int, default=2048,
        help=(
            "LRU decode-cache size in variants. A MEMORY knob, not a correctness "
            "knob: --cache-variants 1 yields a byte-identical TSV. Bound is "
            "cache_variants * n_samples bytes."
        ),
    )
    return parser


def main(argv: "list[str] | None" = None) -> int:
    """Run the scan. Returns 0 on success, non-zero on a bad or missing input.

    Every input is validated BEFORE the output file is opened, so a failure never
    leaves a partial TSV behind.
    """
    args = _build_parser().parse_args(argv)

    prefix = Path(args.bfile_prefix)
    for suffix in (".bed", ".bim", ".fam"):
        component = prefix.with_suffix(suffix)
        if not component.exists():
            print(
                f"ERROR: missing bfile component {component} for prefix {prefix}",
                file=sys.stderr,
            )
            return 2

    try:
        if args.regions_tsv is not None:
            if not Path(args.regions_tsv).exists():
                print(f"ERROR: missing --regions-tsv {args.regions_tsv}", file=sys.stderr)
                return 2
            # AN EMPTY-AFTER-STRIP VALUE IS AN ERROR, NOT "ALL REGIONS".
            # The old conditional expression let `--region-ids " , "` produce
            # `[]`, which is FALSY, which fell through to `region_ids = None`,
            # which means NO FILTER — a silent scan of every region in the
            # manifest (21 -> 276, a ~13x cost blow-up) that failed loudly
            # nowhere. Raising here lands on the existing `except ValueError`
            # below, so it exits 2 with an `ERROR:` line and no traceback, BEFORE
            # any scan and BEFORE any file is written. The flag ABSENT still
            # means "all regions" — that path is UNCHANGED.
            if args.region_ids is None:
                region_ids = None
            else:
                region_ids = [r.strip() for r in args.region_ids.split(",") if r.strip()]
                if not region_ids:
                    raise ValueError(
                        f"--region-ids was given but names no region id after "
                        f"stripping: {args.region_ids!r}. OMIT the flag entirely "
                        f"to scan every region in --regions-tsv; an empty value "
                        f"is not the same request."
                    )
            windows = _read_regions_tsv(
                args.regions_tsv, region_ids, ancestry=args.ancestry
            )
        elif all(v is not None for v in (args.region_id, args.chrom, args.from_bp, args.to_bp)):
            windows = [(args.region_id, args.chrom, args.from_bp, args.to_bp)]
        else:
            print(
                "ERROR: specify either --regions-tsv (+ optional --region-ids) or "
                "all of --region-id/--chr/--from-bp/--to-bp",
                file=sys.stderr,
            )
            return 2
        # LAYER 2 of the duplicate-region_id defense, inside the existing
        # try/except so a duplicate exits 2 with a message rather than a
        # traceback. (Layer 1 is iter_bim_windows'; layer 3 is the driver loop's
        # refuse-to-overwrite, which is INTENTIONAL UNREACHABLE REDUNDANCY —
        # see there.)
        _assert_unique_region_ids(windows)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not windows:
        print("ERROR: no windows selected", file=sys.stderr)
        return 2
    if args.window_bp < 0:
        print(f"ERROR: --window-bp must be >= 0, got {args.window_bp}", file=sys.stderr)
        return 2

    # ONE streaming pass over the FULL .bim for every window. The pad is what
    # makes the region-edge clipping COUNTABLE; the padded rows are filtered out
    # of the OUTPUT by region_bounds, so the emitted set is unchanged.
    indexed = iter_bim_windows(
        prefix.with_suffix(".bim"), windows, pad_bp=args.window_bp
    )

    all_results: list[PairResult] = []
    summaries: dict = {}
    reader = BedReader(prefix, cache_variants=args.cache_variants)
    try:
        for region_id, _chrom, start_bp, end_bp in windows:
            rows = indexed[region_id]
            region_bounds = (int(start_bp), int(end_bp))
            # n_deletions is a DENOMINATOR: count IN-BOUNDS deletions only, or the
            # pad would silently inflate it.
            n_deletions = sum(
                1
                for i, row in rows
                if _in_bounds(parse_bim_row(row, index=i).pos, region_bounds)
                and parse_bim_row(row, index=i).is_deletion
            )
            results = scan_region(
                reader,
                region_id,
                rows,
                window_bp=args.window_bp,
                region_bounds=region_bounds,
            )
            n_clipped = count_edge_clipped_candidates(
                region_id,
                rows,
                window_bp=args.window_bp,
                region_bounds=region_bounds,
            )
            all_results.extend(results)
            # LAYER 3 — UNREACHABLE IN THE SHIPPED CONFIGURATION, BUT TESTED.
            # `windows` is already guaranteed unique by `_assert_unique_region_ids`
            # above (and by `iter_bim_windows`, called before this loop), so this
            # branch cannot fire as shipped. A NAIVE committed test — feeding a
            # duplicated manifest through the front door — would pass via one of
            # those earlier layers and be a FALSE INVARIANT.
            #
            # It does NOT follow that no committed test can reach it. Testing the
            # innermost layer of a defense-in-depth stack REQUIRES disabling the
            # outer ones; layers 1 and 2 both call the MODULE-GLOBAL
            # `_assert_unique_region_ids`, so one monkeypatch neutralizes both and
            # leaves exactly this branch active. That test is committed —
            # `test_driver_summaries_guard_independently_refuses_last_wins_with_
            # both_upstream_layers_disabled` — and it attributes the raise by the
            # traceback's FINAL FRAME rather than merely asserting something rose.
            # Negative control observed: deleting this branch makes that test go
            # RED (quick-260826-qq9 T4). Note what caught it instead — the POOLED
            # denominator identity below, reporting 4 summary rows against 8
            # emitted rows: the same 2x inflation that corrupted the 2026-08-26
            # sweep, in miniature. This layer is not the last line; it is the
            # EARLIEST, and the only one that names the offending region_id.
            # It exists because `summaries[region_id] = ...` is a LAST-WINS write
            # against an ACCUMULATING `all_results`: that asymmetry is what
            # doubled the driver passes on top of the already-doubled rows.
            if region_id in summaries:
                raise ValueError(
                    f"region_id {region_id!r} evaluated twice — summaries would "
                    f"silently last-win"
                )
            summaries[region_id] = summarize(
                region_id,
                results,
                window_bp=args.window_bp,
                n_deletions=n_deletions,
                n_candidates_edge_clipped=n_clipped,
            )
    finally:
        reader.close()

    # WRITE FIRST, THEN RECONCILE, THEN QUARANTINE. The order is deliberate and
    # it INVERTS what shipped before (quick-260828-uej). Three reasons, in the
    # order they were argued:
    #
    #   (a) WRITING TRUNCATES ANY STALE ARTIFACT AT THE READ PATH. The runbook
    #       has the operator `wc -l /home/jupyter/occ_measure/pcs_pairs.tsv`
    #       immediately after the sweep. The CONTAMINATED 2026-08-26 artifact —
    #       871,038,152 B, 2,865,514 lines — sits at exactly that path. Under the
    #       old order a failure exited BEFORE any write, that file survived
    #       untouched, and the `wc -l` returned 2865514: a stale number that reads
    #       like a fresh result.
    #   (b) THE RENAME LEAVES NOTHING AT `--out`. After a disagreement the output
    #       is MOVED to `<out>.SUSPECT`, so the operator's `wc -l` FAILS LOUDLY
    #       instead of returning any number at all.
    #   (c) THE COMPUTE IS SALVAGED. The 21-region sweep costs ~4h18m. A
    #       traceback discarded all of it; a rename preserves every emitted row
    #       in `<out>.SUSPECT` for forensics.
    #
    # THE ARITHMETIC BELOW IS UNCHANGED. Only POSITION and FAILURE HANDLING moved.
    # THE TWO 'POOLED' DENOMINATORS ARE ONE BASIS, BY IDENTITY — NOT BY EYE.
    # `POOLED candidate rows` used to print len(all_results) (the emitted-TSV
    # basis) three lines below a histogram and bins computed from `summaries`
    # (the per-region basis). When a region was evaluated twice those two bases
    # DISAGREED, and the disagreement printed under a single POOLED heading with
    # nothing to flag it: the 2026-08-26 sweep reported 2,865,513 against a
    # summaries basis of 1,453,157. Prefer a must-be-identity transform over a
    # must-match count (`feedback_aggregate_agreement_hides_component_errors`).
    #
    # RESIDUAL — STATED, NOT CLOSED HERE. The EARLY-exit paths (a missing bfile
    # component, `no windows selected`, a duplicate region_id, an empty
    # `--region-ids`) still return 2 BEFORE anything is written, so a stale
    # artifact at the output path SURVIVES those. That hole is closed by the
    # runbook — STEP 2b ROTATE plus STEP 3's pre-flight existence guard in
    # `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` — and
    # NOT by this code. Do not read the write-first ordering as covering them.
    write_tsv(all_results, args.out)
    if args.summary is not None:
        Path(args.summary).write_text(json.dumps(summaries, indent=2, sort_keys=True))

    pooled_candidate_rows = sum(s["n_candidate_rows"] for s in summaries.values())
    if pooled_candidate_rows != len(all_results):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        quarantined = _quarantine_output(args.out, stamp)
        if args.summary is not None:
            _quarantine_output(args.summary, stamp)
        print(
            f"ERROR: POOLED denominator disagreement: sum of per-region "
            f"n_candidate_rows = {pooled_candidate_rows} but the emitted TSV "
            f"carries {len(all_results)} candidate rows. These MUST be the same "
            f"basis; a difference means at least one region was evaluated more "
            f"than once (or a summary was built from a different row set). The "
            f"output is QUARANTINED at {quarantined} — nothing survives at "
            f"{args.out}, so a `wc -l` there fails loudly rather than returning a "
            f"stale number.",
            file=sys.stderr,
        )
        return 2

    # --- stdout: AGGREGATE ONLY. Safe to paste back across the perimeter. ---
    scalar_keys = [k for k in SUMMARY_KEYS if not k.endswith(("histogram", "bins"))]
    print("\t".join(scalar_keys))
    for region_id, _c, _s, _e in windows:
        summary = summaries[region_id]
        print("\t".join(_render_field(summary[k]) for k in scalar_keys))

    pooled_hist: dict = {}
    pooled_bins = {label: 0 for label in LOST_FRAC_BIN_LABELS}
    for summary in summaries.values():
        for offset, count in summary["undefined_offset_histogram"].items():
            pooled_hist[offset] = pooled_hist.get(offset, 0) + count
        for label, count in summary["defined_carriers_lost_frac_bins"].items():
            pooled_bins[label] += count
    pooled_hist = {k: pooled_hist[k] for k in sorted(pooled_hist, key=int)}

    print()
    print(
        "POOLED undefined-set offset histogram (basis: per-region summaries): "
        f"{pooled_hist}"
    )
    print(
        "POOLED defined-row carriers_lost_frac bins (basis: per-region "
        f"summaries): {pooled_bins}"
    )
    print(
        "POOLED candidate rows (basis: per-region summaries, reconciled against "
        f"the emitted TSV rows): {pooled_candidate_rows}"
    )
    print(
        "NOTE: these are COUNTS over the scanned regions. They are NOT a "
        "prevalence, NOT a boundary width, and NOT a tail size for the panel."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
