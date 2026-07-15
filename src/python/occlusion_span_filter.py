"""Overlapping-deletion REFERENCE-OCCLUSION span filter (m3-07b, T1).

THE PROBLEM THIS SOLVES
-----------------------
When an indel-aware caller emits a deletion as a left-anchored VCF record
(``REF = <anchor><deleted bases…>``, ``ALT = <anchor>``), the deletion's
REFERENCE FOOTPRINT spans ``[POS, POS + len(REF) − 1]`` — several reference
bases. Any OTHER variant record whose position falls strictly inside that
footprint is *occluded*: on a haplotype carrying the deletion, the occluded
site's alleles are not observable, so the pairwise genotype table between the
two records is degenerate and plink ``--r`` emits ``0/0 -> NaN`` LD (whole
row/col NaN with the diagonal still 1.0 — the m3-02e-T4 fire-#3 fingerprint).

The mechanism is SETTLED and byte-verified (``m3_region1_nan_geometry_verdict.md``,
body anchor ``4543dcf4…``). The POLICY is pre-registered on OSF (osf.io/az52u,
POSTED 2026-07-10T13:32:22Z, recorded ``ac4c990``): such a variant is EXCLUDED
from the LD panel — in lockstep with the harmonized sumstats, with per-variant
provenance — and is NEVER zeroed. ``NaN -> 0`` is DEAD.

THE DETERMINISTIC OCCLUSION RULE (conservative; RESEARCH §2/§7)
---------------------------------------------------------------
    V is OCCLUDED iff ∃ another window variant D with ``len(REF_D) > 1`` and

        POS_D < POS_V <= POS_D + len(REF_D) − 1

    computed over the ORIGINAL window (all in-window variants).

Three properties of that rule are load-bearing and each is pinned by a test in
``tests/m3/test_occlusion_span_filter.py``:

* **Footprint is ``len(REF)`` ONLY.** An SNV (``len(REF) == 1``) never occludes.
  An INSERTION (``len(ALT) > len(REF)``, ``REF`` = a single anchor base) has a
  single-base footprint and never occludes a downstream base — the inserted
  sequence is not reference span (RESEARCH §7 decision 2).
* **The left bound is STRICT** (``POS_D < POS_V``). A DISTINCT variant sharing a
  deletion's POS is a co-located representation (Hail ``split_multi`` emits these
  genome-wide; handled upstream by ``bcftools norm -m``), NOT an occlusion drop.
  Using ``<=`` would over-drop the multiallelic partner of every deletion.
* **Computed over the ORIGINAL window, not iteratively.** In a chain
  ``D1 ⊃ D2 ⊃ V3``, BOTH ``D2`` and ``V3`` drop — ``V3`` is NOT rescued by ``D2``
  having been dropped (RESEARCH §7 decision 1). This over-excludes deliberately;
  every drop is audited variant-by-variant in the provenance manifest
  (``occlusion_manifest.py``).

Only the DOWNSTREAM occluded variant ``V`` is excluded; the occluding deletion
``D`` is KEPT. Because an occluder always has the strictly smaller position,
excluding every occluded ``V`` removes every occlusion edge in one pass.

WHAT THIS MODULE CANNOT SEE
---------------------------
This detector is COORDINATE-ONLY: it reads ``.bim`` geometry and nothing else.
The region-1 pair-4 tangle (``DEL 5922716`` / ``SNP 5922718`` / ``DEL 5922724``)
is instructive. The verdict records TWO NaN edges there, but only ONE is a
reference-span overlap: ``DEL 5922716 -> SNP 5922718`` (5922716's 7 bp footprint
ends at 5922722, covering 5922718). The ``5922718 <-> 5922724`` NaN pair is
DISJOINT in reference coordinates (del4 starts strictly downstream of the SNP) —
it is a GENOTYPE-layer consequence, invisible here, and this module MUST NOT
synthesize an edge for it. Dropping 5922718 via its one direct upstream edge
collapses the whole 3-record tangle anyway ("one drop, two edges" — RESEARCH §7),
so no extra edge is needed and none is emitted.

``.bim`` ALLELE CONVENTION (``plink_ld_to_npz.load_bim``, FROZEN)
-----------------------------------------------------------------
Columns are ``[chr, snp_id, cm, bp, A1, A2]`` with **A1 = ALT** (col 5) and
**A2 = REF** (col 6) under ``hl.export_plink``; the canonical variant id is
``{chr}:{bp}:{A2}:{A1}`` = ``chr:pos:REF:ALT``. A deletion therefore carries a
MULTI-CHAR A2/REF whose length IS its reference footprint.

Pure: stdlib only, no I/O in the rule itself, no plink, no Hail — CI-runnable.
"""
from __future__ import annotations

from pathlib import Path
from typing import NamedTuple, Sequence

__all__ = [
    "OcclusionEdge",
    "detect_occluded_variants",
    "load_bim_rows",
    "parse_bim_row",
]

#: ``.bim`` column indices (see the module docstring's allele-convention note).
_COL_CHR = 0
_COL_ID = 1
_COL_BP = 3
_COL_ALT = 4  # A1
_COL_REF = 5  # A2 — its LENGTH is the reference footprint


class OcclusionEdge(NamedTuple):
    """A single ``(occluder_id, occluded_id)`` reference-span-overlap edge.

    A 2-field ``NamedTuple`` is deliberate: it is HASHABLE and compares EQUAL to
    the plain 2-tuple the test-suite contract pins (``set(edges)`` and
    ``for (o, v) in edge_set``), while still giving call sites readable
    ``.occluder_id`` / ``.occluded_id`` access. Do NOT grow a third field — that
    would break tuple equality against the pinned contract. There is deliberately
    no ``geometry`` field: every edge this coordinate-only detector emits is a
    ``ref_span_overlap`` by construction, so the label would carry no information.
    """

    occluder_id: str
    occluded_id: str


class _Variant(NamedTuple):
    """A parsed ``.bim`` row (internal)."""

    index: int
    vid: str
    pos: int
    ref_len: int

    @property
    def span_end(self) -> int:
        """Last reference base covered: ``POS + len(REF) − 1``."""
        return self.pos + self.ref_len - 1

    @property
    def is_deletion(self) -> bool:
        """``len(REF) > 1`` — the ONLY thing that can occlude."""
        return self.ref_len > 1


def parse_bim_row(row: Sequence, *, index: int = 0) -> _Variant:
    """Validate + parse ONE ``.bim`` row into a ``_Variant``.

    RAISES ``ValueError`` on a malformed row (< 6 fields, or a non-integer bp)
    rather than silently skipping it (T-m3-07b-04, ASVS V5): a silently-dropped
    row would under-exclude and let an occluded NaN reach the frozen reader.
    Mirrors the loud-failure discipline of ``_retained_window_bim``.
    """
    if isinstance(row, (str, bytes)):
        raise ValueError(
            f"malformed .bim row at index {index}: expected a sequence of >=6 "
            f"fields, got a bare {type(row).__name__}"
        )
    try:
        n_fields = len(row)
    except TypeError as exc:  # not a sized sequence at all
        raise ValueError(
            f"malformed .bim row at index {index}: not a sized sequence ({exc})"
        ) from exc
    if n_fields < 6:
        raise ValueError(
            f"malformed .bim row at index {index}: expected >=6 fields "
            f"(chr, snp_id, cm, bp, A1, A2), got {n_fields}: {row!r}"
        )
    try:
        pos = int(str(row[_COL_BP]).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"malformed .bim row at index {index}: bp field "
            f"{row[_COL_BP]!r} is not an integer"
        ) from exc
    ref = str(row[_COL_REF]).strip()
    if not ref:
        raise ValueError(
            f"malformed .bim row at index {index}: empty REF (A2) field"
        )
    return _Variant(index=index, vid=str(row[_COL_ID]), pos=pos, ref_len=len(ref))


def load_bim_rows(bim_path: "str | Path") -> list[list[str]]:
    """Read a ``.bim`` into ``[chr, snp_id, cm, bp, A1, A2]`` string rows.

    Convenience for running the detector against a real ``.bim`` (the GATED
    region-1 known-answer check). Mirrors ``plink_ld_to_npz._read_bim_rows``'s
    ``parts[:6]`` contract WITHOUT importing it, so this module stays pure-stdlib
    and importable in any CI env (``plink_ld_to_npz`` pulls numpy). Blank lines
    are skipped; a short non-blank row RAISES via ``parse_bim_row`` downstream.
    """
    rows: list[list[str]] = []
    for line in Path(bim_path).read_text().splitlines():
        if not line.strip():
            continue
        rows.append(line.split()[:6])
    return rows


def _attribute_occluder(occluders: list[_Variant]) -> _Variant:
    """Pick the SINGLE occluding deletion a variant is attributed to.

    A variant covered by ONE deletion (the region-1 case, and the overwhelming
    majority genome-wide) has no choice to make. NESTED deletions (``D1 ⊃ D2 ⊃ V``)
    do: the manifest records exactly ONE ``occluding_deletion_id`` per drop, so the
    tie-break must be DETERMINISTIC and reproducible across runs and machines
    (``test_doubly_occluded_variant_appears_exactly_once``).

    Rule: the NEAREST upstream covering deletion (greatest ``POS_D``) — the most
    proximal, most specific reference-span explanation for the drop. Ties are
    broken by the LONGEST footprint, then lexicographically by variant id, so the
    choice never depends on input row order or dict iteration order.
    """
    return max(occluders, key=lambda d: (d.pos, d.ref_len, d.vid))


def detect_occluded_variants(
    rows: Sequence[Sequence],
) -> tuple[list[str], list[OcclusionEdge]]:
    """Return ``(occluded_ids, edges)`` for one window's ``.bim`` rows.

    Parameters
    ----------
    rows
        The window's ``.bim`` rows as 6-field sequences
        ``[chr, snp_id, cm, bp, A1=ALT, A2=REF]`` (tuples from a fixture, or
        ``list[str]`` from :func:`load_bim_rows` / ``_read_bim_rows``). The rule
        is evaluated over the ORIGINAL window exactly as given.

    Returns
    -------
    occluded_ids
        SORTED, UNIQUE col-2 ids of every occluded variant — the exact set to
        write to ``{out_prefix}.occluded.excludelist`` and hand to plink
        ``--exclude`` BEFORE ``--r``. A doubly-occluded variant appears EXACTLY
        ONCE (a duplicate would double-count the genome-wide catalog and could
        double-drop in lockstep).
    edges
        One :class:`OcclusionEdge` ``(occluder_id, occluded_id)`` per occluded
        variant — its deterministic single attribution to a REAL covering
        deletion (see :func:`_attribute_occluder`). Every drop is explained by
        exactly one edge, which is what the manifest's ``ref_span_*`` /
        ``occluding_deletion_*`` columns are derived from. Hashable 2-tuples:
        ``set(edges)`` and ``for (o, v) in edges`` both work.

    Raises
    ------
    ValueError
        On a malformed row (< 6 fields or a non-integer bp) — loud, never silent.
    """
    variants = [parse_bim_row(row, index=i) for i, row in enumerate(rows)]
    deletions = [v for v in variants if v.is_deletion]

    # Fast path: no deletion in the window -> nothing can occlude anything.
    if not deletions:
        return [], []

    occluded_ids: list[str] = []
    edges: list[OcclusionEdge] = []
    for v in variants:
        # THE RULE: strict on the left (a co-located distinct variant is NOT
        # occluded), inclusive on the right (the last covered base IS occluded).
        # `d.index != v.index` guards self-comparison explicitly; the strict left
        # bound already makes self-occlusion impossible, but relying on that
        # implicitly would make the guard invisible to a future edit.
        covering = [
            d for d in deletions
            if d.index != v.index and d.pos < v.pos <= d.span_end
        ]
        if not covering:
            continue
        occluded_ids.append(v.vid)  # once per VARIANT, never once per edge
        edges.append(
            OcclusionEdge(occluder_id=_attribute_occluder(covering).vid,
                          occluded_id=v.vid)
        )

    # Sort for a stable, diff-able excludelist. `set()` then `sorted()` collapses
    # the (pathological) case of two window rows sharing a col-2 id; the driver's
    # `_retained_window_bim` raises loudly on that separately.
    return sorted(set(occluded_ids)), edges
