"""THE ONE canonical ``(CHR, POS)`` key contract for the occlusion lockstep.

Three modules previously duplicated this rule VERBATIM —
``occlusion_present_rate_scan._canonical_key``,
``drop_occluded_from_sumstats._canonical_key`` and
``occlusion_manifest._present_rate_key`` — and every copy ended in a bare
``int(pos)``. They now all delegate here, so the panel<->sumstats join is computed
in exactly one place and cannot drift between the producer, the scan and the drop.

D-04b-01 — THE DEFECT THIS MODULE CLOSES
----------------------------------------
``int('5982778.0')`` raises ``ValueError``, and BOTH consumers swallowed that raise
FAIL-OPEN (keep the row / score the file absent). A full streaming pass over all ten
``*.AFR*.tsv.bgz`` (``m3-04b-BLAST-RADIUS.md``, D-04b-01) measured the exposure:

    bmi.AFR.PAGE.2019.GRCh37   POS is 100% FLOAT ('56019.0')
                               17,195,956 body rows, 17,195,956 failing int(pos)

    every other AFR file       integer POS, 0 failing

So the defect is ONE file, TOTALLY — not a scattering. Today it costs the published
present-rate ``k/n`` (6 of 9 rather than the correct 7 of 9 for rs182965575). It
becomes a live SILENT UNDER-DROP on a real ``run_finemap`` input the moment BMI-AFR
is re-harmonized to the canonical ``bmi.AFR.tsv.bgz`` name ``Snakefile:68-71``
already requests.

INTEGRAL FLOATS ARE ACCEPTED. NON-INTEGRAL ONES RAISE. NOTHING IS EVER TRUNCATED.
--------------------------------------------------------------------------------
``'5982778.0'`` is the integer 5,982,778 written badly, and reading it as such loses
nothing. ``'5982778.5'`` is not a genomic coordinate at all, and silently truncating
it to 5,982,778 would fabricate a plausible-but-WRONG position. The join is
(CHR,POS)-only and DROP-ONLY (``snp_id_bridge.R:107-121``), so a fabricated position
deletes the WRONG variant's row from real scientific data — strictly worse than
failing. Every raise QUOTES the offending value so the caller's unparseable counter
can print a self-explanatory exemplar line.

The string form is matched with an explicit ``re.fullmatch``, NOT ``int()`` /
``float()`` behind a ``try``. That is deliberate: ``int('1_000')`` returns 1000 and
``int('５９８２７７８')`` accepts full-width digits — two latent quirks the blast
radius flagged (no live exposure today). Scientific notation occurs ZERO times in the
whole AFR corpus, so accepting ``'1e6'`` would be a silent WIDENING; rejecting it
makes such a file BLARE through the unparseable counter instead of scoring
silently absent.

DELIBERATELY DEPENDENCY-FREE
----------------------------
STDLIB ONLY — no pandas, no numpy, no pyliftover. ``occlusion_present_rate_scan``
guarantees it stays importable without the span filter or pyliftover ("stdlib only —
streamed line-wise"), and this module is on its import path. numpy scalars are
supported by DUCK TYPING, never by importing numpy.

Runs in smoke_dev py3.11. No Hail, no perimeter, $0.
"""
from __future__ import annotations

import re

__all__ = ["canonical_coord_key", "coerce_integral_position"]

#: A plain integer position. ``[0-9]`` (not ``\d``) is deliberate: ``\d`` matches
#: full-width and other Unicode decimal digits, which ``int()`` also accepts — one of
#: the two latent quirks this module closes.
_INT_RE = re.compile(r"[+-]?[0-9]+")

#: An INTEGRAL float position: digits, a dot, then zero or more digits that must ALL
#: be ``0``. ``'5982778.'`` and ``'5982778.00'`` qualify; ``'5982778.5'`` does not.
_INTEGRAL_FLOAT_RE = re.compile(r"([+-]?[0-9]+)\.([0-9]*)")

#: Appended to every raise so the message says what IS accepted, not just what failed.
_ACCEPTED = (
    "accepted: an integer ('5982778'), an INTEGRAL float ('5982778.0', '5982778.', "
    "'5982778.00') or an integral numeric value. REJECTED (never truncated, never "
    "guessed): a non-integral position ('5982778.5'), scientific notation ('1e6'), "
    "digit separators ('1_000'), non-ASCII digits, '', 'NA', '.', None"
)


def _reject(value, why: str) -> "ValueError":
    """Build the one raise shape: QUOTE the value, say why, say what is accepted."""
    return ValueError(
        f"cannot read {value!r} (type {type(value).__name__}) as a genomic position: "
        f"{why}. {_ACCEPTED}."
    )


def _coerce_str(text: str) -> int:
    """Coerce a STRING position via explicit full-match patterns (never ``int()``)."""
    stripped = text.strip()
    if _INT_RE.fullmatch(stripped):
        return int(stripped)
    match = _INTEGRAL_FLOAT_RE.fullmatch(stripped)
    if match:
        fraction = match.group(2)
        if set(fraction) <= {"0"}:
            return int(match.group(1))
        raise _reject(
            text,
            "it is a NON-INTEGRAL float and truncating it would fabricate a "
            "plausible-but-wrong coordinate that deletes the WRONG sumstats row",
        )
    raise _reject(text, "it does not full-match an integer or an integral float")


def coerce_integral_position(value) -> int:
    """Read ``value`` as an integral genomic position, or raise ``ValueError``.

    * ``int`` (and any integral duck type, e.g. ``numpy.int64``, where
      ``int(value) == value``): returned as a plain ``int``.
    * ``float`` (and ``numpy.float64``): accepted ONLY when integral
      (``float(value).is_integer()``); otherwise raises. **NEVER truncated.**
    * ``str``: ``.strip()``, then an explicit ``re.fullmatch`` — see the module
      docstring for why this is not ``int()``/``float()`` behind a ``try``.
    * anything else (``None``, ``''``, ``'NA'``, ``'.'``, bytes, a bool): raises.

    Every raise quotes the offending value AND names what is accepted.
    """
    if isinstance(value, str):
        return _coerce_str(value)
    if value is None:
        raise _reject(value, "it is None (an absent position, not a coordinate)")
    if isinstance(value, bool):
        # bool subclasses int; a flag is not a coordinate and must not become 0/1.
        raise _reject(value, "a bool is not a genomic position")

    # Integral duck types (int, numpy.int64, ...) — recognized WITHOUT importing
    # numpy: an integral value round-trips through int() unchanged and is not a
    # float instance. Checked before the float path so a large int64 can never
    # lose precision through a float round-trip.
    if not isinstance(value, float):
        try:
            as_int = int(value)
        except (TypeError, ValueError):
            as_int = None
        if as_int is not None:
            try:
                if as_int == value:
                    return as_int
            except (TypeError, ValueError):  # pragma: no cover - exotic comparands
                pass

    # Float-like: accepted only when integral.
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        raise _reject(value, "it is not a numeric value at all") from None
    if as_float != as_float:  # NaN, without importing math
        raise _reject(value, "it is NaN (an absent position, not a coordinate)")
    if not as_float.is_integer():
        raise _reject(
            value,
            "it is NON-INTEGRAL and truncating it would fabricate a "
            "plausible-but-wrong coordinate that deletes the WRONG sumstats row",
        )
    return int(as_float)


def canonical_coord_key(chrom, pos) -> tuple:
    """The canonical GRCh37 join key: ``(contig, position)``.

    Contig normalization is BYTE-IDENTICAL to the three implementations this module
    replaced: ``str(chrom).strip()``, strip a case-insensitive leading ``chr``, and
    a purely-``.isdigit()`` contig becomes an ``int``. That is what makes the
    manifest producer's string ``'1'`` and the scan's int ``1`` the SAME variant
    rather than two silent near-misses.

    ``.isdigit()`` is deliberately NOT tightened. It accepts non-ASCII decimal digits
    the way it always has; tightening it here would MOVE the manifest-side key and
    break the join, which reads downstream exactly like "nothing was occluded".

    LOW-5 IS EXPLICITLY OUT OF SCOPE. ``asthma.AFR`` encodes chrX as ``'X'`` while
    ``bmi.AFR.PAGE`` encodes it as ``'23'``, so ``('X', p)`` and ``(23, p)`` can never
    compare equal — a latent silent no-match. It is inert today (all 276 AFR regions
    are chr1-22) and closing it would move the key for every consumer at once. Do NOT
    "fix" LOW-5 here by accident; it needs its own plan and its own regression.
    """
    contig = str(chrom).strip()
    if contig.lower().startswith("chr"):
        contig = contig[3:]
    if contig.isdigit():
        contig = int(contig)
    return (contig, coerce_integral_position(pos))
