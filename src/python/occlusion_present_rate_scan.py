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
out of the manifest (where the producer emits the STRING ``'1'``) still joins. That
rule is now IMPORTED from ``occlusion_coord_key`` — the ONE place the (CHR,POS) key
is computed — rather than mirrored here. It used to be mirrored, and the three
verbatim copies is how D-04b-01 (a bare ``int(pos)`` that raises on the
float-formatted POS carried by 100% of ``bmi.AFR.PAGE.2019.GRCh37``) survived in
triplicate. ``occlusion_coord_key`` is deliberately STDLIB-ONLY, so this scanner
still needs neither the span filter nor pyliftover and stays importable without them.

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
import sys
from pathlib import Path
from typing import Iterable, Sequence

from occlusion_coord_key import canonical_coord_key

__all__ = ["scan_present_rate"]

#: Fallback column indices, mirroring the hinge-check awk prototype's
#: ``cc=(h["CHR"]?h["CHR"]:1); pc=(h["POS"]?h["POS"]:(h["BP"]?h["BP"]:2))``.
_FALLBACK_CHR_IDX = 0
_FALLBACK_POS_IDX = 1

#: Accepted position-column names, in precedence order (POS wins over BP).
_POS_NAMES = ("POS", "BP")


def _canonical_key(chrom, pos) -> tuple:
    """Canonical GRCh37 scan/join key — see ``occlusion_coord_key``.

    A ONE-LINE DELEGATION, kept under its private name so every existing reference
    (and every test that pins the three implementations byte-compatible) still
    resolves. The rule itself lives in exactly one module now; it used to be
    duplicated verbatim here, in ``drop_occluded_from_sumstats`` and in
    ``occlusion_manifest``, which is how D-04b-01 survived in triplicate.
    """
    return canonical_coord_key(chrom, pos)


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


def _raise_nothing_parsed(path: Path, what: str, first_bad) -> None:
    """The HIGH-0 guard: the file has content but yielded NO usable coordinate.

    A file with rows and no readable coordinates is BROKEN, not empty — and the two
    are indistinguishable in the k/n this scan publishes, which is a PRE-REGISTERED
    number (osf.io/az52u). The only honest answer is to refuse.
    """
    raise ValueError(
        f"REFUSING to score {path} as 'nothing present': {what} "
        f"(first offending line/value: {first_bad!r}). A file that carries content "
        "but no readable (CHR,POS) coordinate is BROKEN, not empty, and scoring it "
        "silently under-counts k — and, for a blank-first-line file, n as well — in "
        "the PRE-REGISTERED present-rate (osf.io/az52u). Fix the POS column, the "
        "header, or the column detection; do not silence this."
    )


def scan_present_rate(variants_grch37: Iterable[Sequence],
                      sumstats_paths: Iterable["str | Path"],
                      *, stats: "dict | None" = None) -> dict:
    """PRESENT-vs-ABSENT rate of each occluded variant across the scanned sumstats.

    ``variants_grch37``: the occluded variants as GRCh37 ``(chr, pos)`` pairs (i.e.
    the manifest's ``(chr, pos_grch37)`` AFTER Stage-B liftover).
    ``sumstats_paths``: the harmonized sumstats to scan — the 9 public AFR files in
    production, tiny synthetic TSVs under unit test. One file = one trait.
    ``stats``: OPTIONAL kwarg-only out-param. When a dict is supplied it is populated
    IN PLACE with the scan's parse health (see below). Omitting it changes nothing.

    Returns ``{(chr, pos): {"n_traits_present": int, "n_traits_scanned": int,
    "present_rate": float, "traits_present": list[str]}}``. Those four names are
    ``occlusion_manifest.STAGE_B_TRAIT_COLUMNS`` + the rate, so the return feeds
    ``enrich_occlusion_manifest(present_rate=...)`` directly (see module docstring).
    **The per-variant record carries EXACTLY those four keys — a fifth would break
    that no-adapter contract**, which is why the health numbers ride out through
    ``stats`` instead.

    ``stats`` receives ``n_files_scanned``, ``n_distinct_traits_scanned``,
    ``duplicate_traits``, ``n_rows_seen``, ``n_rows_parsed``, ``n_unparseable``,
    ``n_truncated``, ``n_files_empty`` and ``per_file`` (one record per file, with its
    resolved trait label). All of it is accumulated inside the EXISTING single pass —
    these are genome-wide files and a second pass is not affordable.

    A variant absent from EVERY file returns a RECORD with ``n_traits_present == 0``
    and ``present_rate == 0.0`` — never a missing key, never a ZeroDivisionError.
    "Scanned and found nowhere" is a real, reportable scientific result (it is the
    cheap end of the exclusion cost); silently omitting it would be indistinguishable
    from "not scanned".

    A variant occurring MORE THAN ONCE in one file (a multi-allelic collision) counts
    ONCE toward k — matching the (CHR,POS)-only, first-record-wins join semantics of
    ``snp_id_bridge.R:107-121``. Counting hits instead of files would let
    ``present_rate`` exceed 1.0.

    RAISES ``ValueError`` (HIGH-0) when a file carries body rows but yields ZERO
    coercible coordinates — including the case where its FIRST line is blank and real
    content follows, which previously scored the WHOLE file "nothing present" and
    mis-counted BOTH k and n. A header-only or 0-byte file does NOT raise: it has
    ``n_rows_seen == 0``, is counted in ``n_files_empty``, and a legitimately empty
    scan stays legal.
    """
    keys = list(dict.fromkeys(_canonical_key(*v) for v in variants_grch37))
    paths = [Path(p) for p in sumstats_paths]

    traits_present: dict[tuple, list[str]] = {k: [] for k in keys}
    targets = set(keys)

    per_file: list[dict] = []
    tot_rows_seen = tot_rows_parsed = tot_unparseable = tot_truncated = 0
    n_files_empty = 0

    for path in paths:
        # Every file gets a label up front (the filename fallback) so an EMPTY file
        # still reports which trait it was meant to be; the first body row refines it
        # from the authoritative TRAIT column exactly as before.
        label = _trait_label(path, [], None)
        rows_seen = rows_parsed = n_unparseable = n_truncated = 0
        first_bad = None

        with _open_text(path) as fh:
            header_line = fh.readline()
            if not header_line.strip():
                # A blank/absent first line is EITHER a legitimately empty file OR a
                # file whose header is blank and whose content sits below it. The
                # second case used to be `continue`d silently, scoring the whole file
                # "nothing present" and mis-counting k AND n. Probe for content
                # STREAMING (stop at the first non-blank line) so a genome-wide file
                # is never materialized.
                stray = next((ln for ln in fh if ln.strip()), None)
                if stray is not None:
                    _raise_nothing_parsed(
                        path,
                        "its FIRST line is blank but non-blank content follows, so "
                        "no header could be located and every row below it was "
                        "previously discarded unread",
                        stray.rstrip("\r\n"),
                    )
                n_files_empty += 1
                per_file.append({
                    "path": str(path), "trait": label, "n_rows_seen": 0,
                    "n_rows_parsed": 0, "n_unparseable": 0, "n_truncated": 0,
                    "n_hits": 0,
                })
                continue
            chr_idx, pos_idx, trait_idx = _locate_columns(
                header_line.rstrip("\r\n").split("\t")
            )

            labelled = False
            hits: set = set()
            for line in fh:
                if not line.strip():
                    continue
                rows_seen += 1
                fields = line.rstrip("\r\n").split("\t")
                if not labelled:
                    label = _trait_label(path, fields, trait_idx)
                    labelled = True
                if max(chr_idx, pos_idx) >= len(fields):
                    n_truncated += 1          # truncated row: carries no coordinate
                    if first_bad is None:
                        first_bad = line.rstrip("\r\n")
                    continue
                try:
                    key = _canonical_key(fields[chr_idx], fields[pos_idx])
                except (TypeError, ValueError):
                    n_unparseable += 1        # unparseable coordinate cannot match
                    if first_bad is None:
                        first_bad = fields[pos_idx]
                    continue
                rows_parsed += 1
                if key in targets:
                    hits.add(key)

            for key in hits:
                traits_present[key].append(label)

        if rows_seen == 0:
            n_files_empty += 1
        elif rows_parsed == 0:
            _raise_nothing_parsed(
                path,
                f"it carries {rows_seen} body row(s) and NOT ONE yielded a coercible "
                f"coordinate ({n_unparseable} unparseable, {n_truncated} truncated)",
                first_bad,
            )

        tot_rows_seen += rows_seen
        tot_rows_parsed += rows_parsed
        tot_unparseable += n_unparseable
        tot_truncated += n_truncated
        per_file.append({
            "path": str(path), "trait": label, "n_rows_seen": rows_seen,
            "n_rows_parsed": rows_parsed, "n_unparseable": n_unparseable,
            "n_truncated": n_truncated, "n_hits": len(hits),
        })

    n_scanned = len(paths)

    labels = [rec["trait"] for rec in per_file]
    duplicate_traits = sorted({t for t in labels if labels.count(t) > 1})
    if duplicate_traits:
        # LOW-1, VISIBILITY ONLY. The production glob resolves 9 FILES but only 8
        # DISTINCT TRAITS (stroke.AFR and stroke.AFR.GIGASTROKE.2022.GRCh37 both
        # report `stroke`). The denominator is DELIBERATELY NOT changed: the project
        # record and the pre-registration publish "present in k of 9 AFR SUMSTATS" —
        # a FILE rate. Redefining it to distinct traits would MOVE a pre-registered
        # number, which is not an executor's call. Reported here so a reader can see
        # the double-count instead of inheriting it silently.
        print(
            f"[occlusion_present_rate_scan] NOTE: scanned {n_scanned} file(s) but "
            f"only {len(set(labels))} DISTINCT trait(s) — duplicated: "
            f"{', '.join(duplicate_traits)}. `n_traits_scanned` is therefore a FILE "
            "rate, NOT a trait rate. That is the published denominator "
            "(osf.io/az52u) and is left UNCHANGED here; the double-count is reported, "
            "never silently folded in.",
            file=sys.stderr,
        )

    if stats is not None:
        stats.update({
            "n_files_scanned": n_scanned,
            "n_distinct_traits_scanned": len(set(labels)),
            "duplicate_traits": duplicate_traits,
            "n_rows_seen": tot_rows_seen,
            "n_rows_parsed": tot_rows_parsed,
            "n_unparseable": tot_unparseable,
            "n_truncated": tot_truncated,
            "n_files_empty": n_files_empty,
            "per_file": per_file,
        })

    return {
        key: {
            "n_traits_present": len(traits),
            "n_traits_scanned": n_scanned,
            "present_rate": (len(traits) / n_scanned) if n_scanned else 0.0,
            "traits_present": traits,
        }
        for key, traits in traits_present.items()
    }
