"""Present-rate-per-ancestry scan over the public GRCh37 AFR sumstats (m3-07c, T3).

This module QUANTIFIES THE SCIENTIFIC COST of the pre-registered exclusion policy
(osf.io/az52u, amendment-update POSTED 2026-07-10T13:32:22Z, recorded ``ac4c990``).
Excluding a variant whose LD is structurally undefined is defensible only if we can
say, honestly and per-variant, WHAT WAS LOST: in how many of the n harmonized AFR
sumstats does a row for that variant actually exist? That k/n is

  * the concrete evidence that retired ``NaN->0`` as directionally wrong — the harm
    is not hypothetical: rs182965575 (GRCh37 chr1:5982778) is PRESENT in 7 of 9 AFR
    sumstats, and ``NaN->0`` would have silently conditioned it to "no LD" rather
    than honestly excluding it; and
  * the Angle-1/3 occlusion-catalog payload — ``traits_present`` NAMES the traits
    that carry the variant, so a reader can audit the loss trait by trait instead of
    taking a bare count on faith.

THE KEY IS THE ``(chr, pos_grch37)`` TUPLE — AND THAT IS A CONTRACT, NOT A CHOICE
--------------------------------------------------------------------------------
:func:`scan_present_rate` returns ``{(chr, pos): {...}}`` keyed on GRCh37, and its
four value keys are exactly ``occlusion_manifest.STAGE_B_TRAIT_COLUMNS`` plus the
rate. That is deliberate: the return is fed DIRECTLY to

    occlusion_manifest.enrich_occlusion_manifest(..., present_rate=<this return>)

with NO adapter. That consumer joins on ``(chr, pos_grch37)`` POST-liftover — never
on ``variant_id``, because this scan reads GRCh37 sumstats by (CHR,POS) and can
never compute a GRCh38 ``variant_id``. It also RAISES ``ValueError`` if liftable
manifest rows exist and not one key matches, so a key-shape drift here surfaces as
a hard failure rather than a manifest silently filled with NA.

Keys are canonicalized ("chr1"/"1" -> 1) by the same rule as
``occlusion_manifest._present_rate_key``, so a caller that reads ``chr`` straight
out of the manifest (where the producer emits the STRING ``'1'``) still joins. The
rule is mirrored rather than imported: this scanner needs neither the span filter
nor pyliftover, and must stay importable without them.

CHR/POS ARE LOCATED BY NAME
---------------------------
Harmonized AFR sumstats header (public GRCh37):
    CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD
Columns are located BY HEADER NAME, reusing the hinge-check scan prototype
(``m3_region1_occlusion_hinge_check.md:124-141``): CHR by name else column 1, POS
by name else BP by name else column 2. A positional read would silently score the
wrong column against a file whose columns are ordered differently and report a
confident, wrong rate.

REQ-PUBLIC-DATA-ONLY: this reads ALREADY-PUBLIC GRCh37 summary statistics,
read-only, at NC State. No perimeter, no genotypes, no individual-level data, no
spend. The real 9-file genome-wide scan is a GATED integration/validation step; the
function is unit-covered on tiny synthetic fixtures.

Runs in smoke_dev py3.11 (stdlib only — streamed line-wise so a genome-wide
sumstats is never materialized in memory). No Hail.
"""
from __future__ import annotations

import gzip
from pathlib import Path
from typing import Iterable, Sequence

__all__ = ["scan_present_rate"]

#: Fallback column indices, mirroring the hinge-check awk prototype's
#: ``cc=(h["CHR"]?h["CHR"]:1); pc=(h["POS"]?h["POS"]:(h["BP"]?h["BP"]:2))``.
_FALLBACK_CHR_IDX = 0
_FALLBACK_POS_IDX = 1

#: Accepted position-column names, in precedence order (POS wins over BP).
_POS_NAMES = ("POS", "BP")


def _canonical_key(chrom, pos) -> tuple:
    """Canonical GRCh37 scan/join key: ``(chr, pos)`` with a normalized contig.

    Mirrors ``occlusion_manifest._present_rate_key`` EXACTLY (strip a ``chr``
    prefix; a purely numeric contig becomes an ``int``) so this scan's return joins
    the manifest without an adapter. The manifest producer emits ``chr`` as the
    string ``'1'`` while the RED keys on the int ``1`` — normalizing both to ``1``
    is what makes those two the same variant instead of two silent near-misses.
    """
    contig = str(chrom).strip()
    if contig.lower().startswith("chr"):
        contig = contig[3:]
    if contig.isdigit():
        contig = int(contig)
    return (contig, int(pos))


def _open_text(path: Path):
    """Open a sumstats file, transparently handling bgzip/gzip.

    BGZF (``.bgz``) is gzip-compatible, so the stdlib reader handles the real
    ``*.AFR*.tsv.bgz`` files and the plain ``.tsv`` unit fixtures identically.
    """
    if path.suffix.lower() in {".gz", ".bgz"}:
        return gzip.open(path, "rt")
    return path.open("rt")


def _locate_columns(header: Sequence[str]) -> tuple:
    """Locate (chr_idx, pos_idx, trait_idx) BY NAME. Returns trait_idx=None if absent."""
    idx = {name.strip().upper(): i for i, name in enumerate(header)}
    chr_idx = idx.get("CHR", _FALLBACK_CHR_IDX)
    pos_idx = next((idx[n] for n in _POS_NAMES if n in idx), _FALLBACK_POS_IDX)
    return chr_idx, pos_idx, idx.get("TRAIT")


def _trait_label(path: Path, first_fields: Sequence[str], trait_idx) -> str:
    """The trait this file reports on.

    Prefers the harmonized ``TRAIT`` column (authoritative — it survives a renamed
    file); falls back to the filename's leading dot-part (``bmi.AFR.tsv.bgz`` ->
    ``bmi``) when the column is absent or blank. ONE label per file: the
    denominator ``n_traits_scanned`` counts FILES, so a file must contribute at most
    one trait name or the k/n would not be a rate.
    """
    if trait_idx is not None and trait_idx < len(first_fields):
        value = first_fields[trait_idx].strip()
        if value:
            return value
    return path.name.split(".")[0]


def scan_present_rate(variants_grch37: Iterable[Sequence],
                      sumstats_paths: Iterable["str | Path"]) -> dict:
    """PRESENT-vs-ABSENT rate of each occluded variant across the scanned sumstats.

    ``variants_grch37``: the occluded variants as GRCh37 ``(chr, pos)`` pairs (i.e.
    the manifest's ``(chr, pos_grch37)`` AFTER Stage-B liftover).
    ``sumstats_paths``: the harmonized sumstats to scan — the 9 public AFR files in
    production, tiny synthetic TSVs under unit test. One file = one trait.

    Returns ``{(chr, pos): {"n_traits_present": int, "n_traits_scanned": int,
    "present_rate": float, "traits_present": list[str]}}``. Those four names are
    ``occlusion_manifest.STAGE_B_TRAIT_COLUMNS`` + the rate, so the return feeds
    ``enrich_occlusion_manifest(present_rate=...)`` directly (see module docstring).

    A variant absent from EVERY file returns a RECORD with ``n_traits_present == 0``
    and ``present_rate == 0.0`` — never a missing key, never a ZeroDivisionError.
    "Scanned and found nowhere" is a real, reportable scientific result (it is the
    cheap end of the exclusion cost); silently omitting it would be indistinguishable
    from "not scanned".

    A variant occurring MORE THAN ONCE in one file (a multi-allelic collision) counts
    ONCE toward k — matching the (CHR,POS)-only, first-record-wins join semantics of
    ``snp_id_bridge.R:107-121``. Counting hits instead of files would let
    ``present_rate`` exceed 1.0.
    """
    keys = list(dict.fromkeys(_canonical_key(*v) for v in variants_grch37))
    paths = [Path(p) for p in sumstats_paths]

    traits_present: dict[tuple, list[str]] = {k: [] for k in keys}
    targets = set(keys)

    for path in paths:
        with _open_text(path) as fh:
            header_line = fh.readline()
            if not header_line.strip():
                continue                      # empty file -> scanned, nothing present
            chr_idx, pos_idx, trait_idx = _locate_columns(
                header_line.rstrip("\r\n").split("\t")
            )

            label = None
            hits: set = set()
            for line in fh:
                if not line.strip():
                    continue
                fields = line.rstrip("\r\n").split("\t")
                if label is None:
                    label = _trait_label(path, fields, trait_idx)
                if max(chr_idx, pos_idx) >= len(fields):
                    continue                  # truncated row: carries no coordinate
                try:
                    key = _canonical_key(fields[chr_idx], fields[pos_idx])
                except (TypeError, ValueError):
                    continue                  # unparseable coordinate cannot match
                if key in targets:
                    hits.add(key)

            for key in hits:
                traits_present[key].append(label)

    n_scanned = len(paths)
    return {
        key: {
            "n_traits_present": len(traits),
            "n_traits_scanned": n_scanned,
            "present_rate": (len(traits) / n_scanned) if n_scanned else 0.0,
            "traits_present": traits,
        }
        for key, traits in traits_present.items()
    }
