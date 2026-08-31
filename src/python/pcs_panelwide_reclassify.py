"""POST-HOC panel-wide ``--exclude`` reclassification of an emitted pcs_pairs.tsv.

(1) WHY IT EXISTS — ``already_occluded`` IS ANCHOR-RELATIVE
-----------------------------------------------------------
``pairwise_completeness_scan``'s ``already_occluded`` is computed at
``pairwise_completeness_scan.py:616`` as::

    already_occluded = bool(deletion.pos < partner.pos <= deletion.span_end)

— against THE ANCHOR DELETION ONLY. The PRODUCTION excludelist is a DIFFERENT
quantity: ``occlusion_span_filter.detect_occluded_variants`` evaluated over
EVERY deletion in the window (``run_native_ld_panel.py:878``, on the row set
built at ``:851-872``).

Therefore ``already_occluded == False`` means "not inside THIS anchor's span".
It does NOT mean "survives ``--exclude``", and ``n_undefined_not_already_occluded``
does NOT count pairs that survive filtering. This module computes the panel-wide
quantity that the scanner never asked for, from the scanner's OWN output.

(2) WHY VID-KEYED — BECAUSE PRODUCTION IS
------------------------------------------
``detect_occluded_variants`` returns col-2 IDS because that is exactly what
plink ``--exclude`` consumes (``aou_ld_panel.py:2910-2913``), and ``--exclude``
on a DUPLICATED id drops EVERY row carrying it. A vid key therefore MATCHES
PRODUCTION SEMANTICS, and any id ambiguity is PRODUCTION'S ambiguity: it is
counted in ``n_pairs_with_ambiguous_member_id`` and NAMED in
``ambiguous_member_ids``, never "fixed" by switching to row indices.

⚠ Do NOT conflate this with ``_pair_key`` (``pairwise_completeness_scan.py:446``),
which is deliberately INDEX-keyed for the OPPOSITE reason: two rows sharing a
``.`` id are DISTINCT pairs and a vid key would UNDERCOUNT them. Both
conventions are correct; they answer different questions. Pair-level rollups
here use ``pair_key``; occlusion verdicts use the vid.

(3) MONOTONICITY AND SCOPE
---------------------------
Occlusion is MONOTONE in the row set: for a variant present in both, ``R`` a
subset of ``R'`` implies ``occluded(v, R)`` implies ``occluded(v, R')``, because
adding rows can only ADD covering deletions and the self-guard is index-based
and recomputed per call. CONSEQUENCE: an OCCLUDED verdict computed on a SUBSET
is SOUND, while a NOT-OCCLUDED verdict on a SUBSET is NOT. Every not-occluded
verdict emitted here is therefore RELATIVE TO the row set named in
``provenance`` — which records the bim path, its sha256, its line count, the
region ids NAMED, the per-region in-window row counts, and a literal
``verdict_scope`` sentence saying exactly this.
``tests/m3/test_pcs_panelwide_reclassify.py::test_occlusion_is_monotone_in_the_row_set``
proves the property the soundness argument rests on rather than assuming it.

(4) POST-HOC ONLY — IT CANNOT REQUIRE A RE-RUN
-----------------------------------------------
This tool reads an ALREADY-EMITTED ``pcs_pairs.tsv``, the cohort ``.bim`` and
the region manifest, AND NOTHING ELSE. It opens no ``.bed``, decodes no
genotype, and therefore CANNOT require the ~4h20m sweep to be re-run: the
sweep's OUTPUT is this tool's INPUT.

That property is MACHINE-CHECKED, not narrated. An AST gate (in this module's
verify block and in
``test_the_tool_never_opens_a_bed_or_decodes_a_genotype``) fails on any
``BedReader``/``Genotypes``/``MISSING_DOSAGE`` import, any ``BedReader``
reference, any ``read_variant`` call, or any ``.bed`` string literal OUTSIDE a
docstring. The gate is AST-based rather than ``grep``-based precisely so that
this paragraph — which MENTIONS ``.bed`` — cannot false-fire it.

(5) WHAT IT DOES NOT ESTABLISH
-------------------------------
No prevalence. No boundary width. No policy, criterion or threshold moves. The
pre-registered ``n_undefined_rows`` 15 / ``n_undefined_distinct_pairs`` 13 /
``already_occluded`` 10 / ``not_already_occluded`` 3 and the offset histogram
are UNCHANGED and are not revised by anything here; this module ADDS a DERIVED
quantity BESIDE them.

Pure stdlib. No numpy, no Hail, no plink, no network.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from occlusion_span_filter import detect_occluded_variants

# PRIVATE BY NAME, SHARED BY DESIGN: a local copy would diverge from the
# scanner's own window selection the day either moves. The identity of all
# three imports is asserted by
# test_the_frozen_detector_is_called_not_reimplemented.
from pairwise_completeness_scan import (  # noqa: F401
    DEFAULT_ANCESTRY,
    TSV_COLUMNS,
    _read_regions_tsv,
    iter_bim_windows,
)

__all__ = [
    "OUT_COLUMNS",
    "PER_REGION_KEYS",
    "POOLED_KEYS",
    "PROVENANCE_KEYS",
    "VERDICT_SCOPE",
    "main",
    "reclassify",
]

#: The emitted per-row TSV columns, in order.
OUT_COLUMNS: tuple = (
    "region_id",
    "del_index",
    "del_vid",
    "del_pos",
    "partner_index",
    "partner_vid",
    "partner_pos",
    "offset",
    "side",
    "already_occluded",
    "pair_key",
    "del_occluded_panelwide",
    "partner_occluded_panelwide",
    "del_occluding_deletion_id",
    "partner_occluding_deletion_id",
    "occluding_deletion_id",
    "pair_reaches_matrix",
    "del_globally_invariant",
    "partner_globally_invariant",
    "member_id_ambiguous",
)

PROVENANCE_KEYS: tuple = (
    "pairs_tsv_path",
    "pairs_tsv_sha256",
    "pairs_tsv_n_lines",
    "bim_path",
    "bim_sha256",
    "bim_n_lines",
    "regions_tsv_path",
    "regions_tsv_sha256",
    "ancestry",
    "region_ids",
    "region_ids_selected",
    "region_ids_out_of_scope",
    "n_rows_in_window_per_region",
    "verdict_scope",
)

POOLED_KEYS: tuple = (
    "n_rows_in_tsv",
    "n_defined_rows_in",
    "n_undefined_rows_in",
    "n_undefined_distinct_pairs_in",
    "n_undefined_rows_out_of_scope",
    "n_rows_member_occluded_panelwide",
    "n_rows_neither_member_occluded_panelwide",
    "n_pairs_member_occluded_panelwide",
    "n_pairs_neither_member_occluded_panelwide",
    "n_pairs_neither_occluded_and_no_globally_invariant_member",
    "n_pairs_with_ambiguous_member_id",
    "ambiguous_member_ids",
    "occluded_member_vids",
)

PER_REGION_KEYS: tuple = (
    "region_id",
    "chrom",
    "start_bp",
    "end_bp",
    "n_rows_in_window",
    "n_occluded_ids_in_window",
    "n_undefined_rows_in",
    "n_undefined_distinct_pairs_in",
    "n_rows_member_occluded_panelwide",
    "n_rows_neither_member_occluded_panelwide",
    "n_pairs_member_occluded_panelwide",
    "n_pairs_neither_member_occluded_panelwide",
    "n_pairs_neither_occluded_and_no_globally_invariant_member",
    "n_pairs_with_ambiguous_member_id",
    "ambiguous_member_ids",
)

#: The literal scope sentence written into every summary. Occlusion is MONOTONE
#: in the row set, so the two verdict directions do NOT carry the same warrant.
VERDICT_SCOPE: str = (
    "Occlusion is MONOTONE in the row set: for a variant present in both, "
    "R subset-of R' implies occluded(v, R) implies occluded(v, R'). An OCCLUDED "
    "verdict computed on a SUBSET of the region window is therefore SOUND, while "
    "a NOT-OCCLUDED verdict on a SUBSET is NOT — it can flip once the missing "
    "rows are supplied. Every not-occluded verdict in this summary is RELATIVE "
    "TO the row set named by bim_path / bim_sha256 / bim_n_lines and the "
    "per-region n_rows_in_window counts recorded beside it."
)

#: ``.bim`` column indices (mirrored from occlusion_span_filter's convention:
#: A1 = ALT is column 5, A2 = REF is column 6, and len(REF) IS the footprint).
_BIM_COL_ID = 1


# =========================================================================== #
# Small, separately testable helpers                                          #
# =========================================================================== #

def _sha256(path: "str | Path") -> str:
    """Streamed sha256 of a file.

    A full pass over a ~20.7M-line cohort manifest takes seconds-to-minutes.
    That is PROVENANCE, not overhead: a verdict that cannot name the bytes it
    was computed against is not reproducible.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _count_lines(path: "str | Path") -> int:
    """Non-blank line count, streamed."""
    total = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                total += 1
    return total


def _parse_bool(value: str) -> bool:
    """Parse the scanner's rendered boolean, LOUDLY.

    ``_render_field`` writes exactly ``True`` / ``False``; anything else means
    the artifact was not produced by that writer and a truthiness coercion
    (``bool("False") is True``) would invert the verdict silently.
    """
    text = str(value).strip()
    if text == "True":
        return True
    if text == "False":
        return False
    raise ValueError(
        f"unparseable boolean field {value!r}: the scanner renders exactly "
        f"'True' or 'False'; anything else means this TSV was not written by "
        f"pairwise_completeness_scan.write_tsv"
    )


def _count_distinct_pairs(rows) -> int:
    """DISTINCT ``(region_id, pair_key)`` count over ``rows``.

    A MODULE-GLOBAL function, not an inline expression, so the reconciliation
    below has something a test can monkeypatch into disagreement — a
    self-check that has never been observed failing is not a check
    (``feedback_green_assertion_needs_a_negative_control``).
    """
    return len({(r["region_id"], r["pair_key"]) for r in rows})


def _reconcile_or_raise(scope: str, unit: str, member: int, neither: int,
                        total: int) -> None:
    """The two populations are EXHAUSTIVE over ``total`` or the tool STOPS.

    A count is a claim: it reconciles arithmetically or nothing is written.
    """
    if member + neither != total:
        raise ValueError(
            f"{scope}: the two panel-wide populations do not reconcile at the "
            f"{unit} level — member_occluded {member} + neither {neither} = "
            f"{member + neither}, but the input carries {total} {unit}(s). "
            f"These MUST be exhaustive and disjoint; a difference means the "
            f"classification lost or double-counted a {unit}."
        )


def _render(value) -> str:
    """Render one scalar for the TSV, deterministically."""
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


# =========================================================================== #
# The reclassification                                                        #
# =========================================================================== #

def _read_pairs_tsv(pairs_tsv: Path) -> list:
    """Parse the pairs TSV BY HEADER, never positionally.

    RAISES if the header is not EXACTLY ``TSV_COLUMNS``: a drifted header means
    the artifact was not produced by this scanner and its pair semantics are
    unverified.
    """
    with open(pairs_tsv, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        observed = tuple(reader.fieldnames or ())
        if observed != tuple(TSV_COLUMNS):
            missing = [c for c in TSV_COLUMNS if c not in observed]
            unexpected = [c for c in observed if c not in TSV_COLUMNS]
            raise ValueError(
                f"pairs TSV header does not equal pairwise_completeness_scan."
                f"TSV_COLUMNS for {pairs_tsv}: missing {missing}, unexpected "
                f"{unexpected}, observed {len(observed)} columns vs expected "
                f"{len(TSV_COLUMNS)}. A drifted header means this artifact was "
                f"not written by this scanner, so its pair semantics are "
                f"unverified and no verdict is computed."
            )
        return [dict(row) for row in reader]


def _classify_region(region_id: str, chrom: str, start_bp: int, end_bp: int,
                     indexed_rows, undefined_rows: list) -> tuple:
    """Reclassify ONE region's undefined rows against its FULL window row set."""
    window_rows = [row for _index, row in indexed_rows]
    occluded_ids, edges = detect_occluded_variants(window_rows)
    occluded = set(occluded_ids)
    attributed = {edge.occluded_id: edge.occluder_id for edge in edges}
    id_counts = Counter(str(row[_BIM_COL_ID]) for row in window_rows)

    out_rows = []
    ambiguous_vids: set = set()
    for row in undefined_rows:
        del_vid = row["del_vid"]
        partner_vid = row["partner_vid"]
        for vid, role in ((del_vid, "del_vid"), (partner_vid, "partner_vid")):
            if vid not in id_counts:
                raise ValueError(
                    f"region {region_id}: {role} {vid!r} from the pairs TSV does "
                    f"not appear in that region's window row set "
                    f"[{chrom}:{start_bp}-{end_bp}] ({len(window_rows)} rows). "
                    f"The .bim you supplied is not the .bim these pairs came "
                    f"from; a not-occluded verdict here would be a silent "
                    f"fabrication, so nothing is classified."
                )
        del_occ = del_vid in occluded
        partner_occ = partner_vid in occluded
        del_occluder = attributed.get(del_vid, "") if del_occ else ""
        partner_occluder = attributed.get(partner_vid, "") if partner_occ else ""
        out_rows.append({
            "region_id": region_id,
            "del_index": row["del_index"],
            "del_vid": del_vid,
            "del_pos": row["del_pos"],
            "partner_index": row["partner_index"],
            "partner_vid": partner_vid,
            "partner_pos": row["partner_pos"],
            "offset": row["offset"],
            "side": row["side"],
            "already_occluded": _parse_bool(row["already_occluded"]),
            "pair_key": row["pair_key"],
            "del_occluded_panelwide": del_occ,
            "partner_occluded_panelwide": partner_occ,
            "del_occluding_deletion_id": del_occluder,
            "partner_occluding_deletion_id": partner_occluder,
            # PRECEDENCE, stated: the deletion member's attribution when it is
            # occluded, otherwise the partner's. The two per-member columns
            # above stay authoritative when BOTH members are occluded.
            "occluding_deletion_id": del_occluder or partner_occluder,
            "pair_reaches_matrix": not (del_occ or partner_occ),
            "del_globally_invariant": _parse_bool(row["del_globally_invariant"]),
            "partner_globally_invariant": _parse_bool(
                row["partner_globally_invariant"]
            ),
            "member_id_ambiguous": bool(
                id_counts[del_vid] > 1 or id_counts[partner_vid] > 1
            ),
        })
        # NAME the ids that are ACTUALLY duplicated. Collecting both members of
        # a flagged ROW would name the innocent partner too, turning a precise
        # production-semantics warning into a list a reader cannot act on.
        for vid in (del_vid, partner_vid):
            if id_counts[vid] > 1:
                ambiguous_vids.add(vid)
    return out_rows, sorted(occluded), len(window_rows), sorted(ambiguous_vids)


def _roll_up(scope: str, out_rows: list, ambiguous_vids) -> dict:
    """Row-level AND pair-level counts for one scope, RECONCILED before return."""
    n_rows_member = sum(
        1 for r in out_rows
        if r["del_occluded_panelwide"] or r["partner_occluded_panelwide"]
    )
    n_rows_neither = len(out_rows) - n_rows_member
    _reconcile_or_raise(scope, "row", n_rows_member, n_rows_neither, len(out_rows))

    pair_member: dict = {}
    pair_gi: dict = {}
    for r in out_rows:
        key = (r["region_id"], r["pair_key"])
        occluded = r["del_occluded_panelwide"] or r["partner_occluded_panelwide"]
        pair_member[key] = pair_member.get(key, False) or occluded
        gi = r["del_globally_invariant"] or r["partner_globally_invariant"]
        pair_gi[key] = pair_gi.get(key, False) or gi

    n_pairs_member = sum(1 for v in pair_member.values() if v)
    n_pairs_neither = sum(1 for v in pair_member.values() if not v)
    n_distinct = _count_distinct_pairs(out_rows)
    _reconcile_or_raise(scope, "pair", n_pairs_member, n_pairs_neither, n_distinct)

    third_tier = sum(
        1 for key, occluded in pair_member.items()
        if not occluded and not pair_gi[key]
    )
    ambiguous_ids = sorted(set(ambiguous_vids))
    n_pairs_ambiguous = len({
        (r["region_id"], r["pair_key"]) for r in out_rows if r["member_id_ambiguous"]
    })
    occluded_member_vids = sorted({
        vid
        for r in out_rows
        for vid, flag in (
            (r["del_vid"], r["del_occluded_panelwide"]),
            (r["partner_vid"], r["partner_occluded_panelwide"]),
        )
        if flag
    })
    return {
        "n_undefined_rows_in": len(out_rows),
        "n_undefined_distinct_pairs_in": n_distinct,
        "n_rows_member_occluded_panelwide": n_rows_member,
        "n_rows_neither_member_occluded_panelwide": n_rows_neither,
        "n_pairs_member_occluded_panelwide": n_pairs_member,
        "n_pairs_neither_member_occluded_panelwide": n_pairs_neither,
        "n_pairs_neither_occluded_and_no_globally_invariant_member": third_tier,
        "n_pairs_with_ambiguous_member_id": n_pairs_ambiguous,
        "ambiguous_member_ids": ambiguous_ids,
        "occluded_member_vids": occluded_member_vids,
    }


def reclassify(pairs_tsv: "str | Path", bim_path: "str | Path",
               regions_tsv: "str | Path", *, ancestry: str = DEFAULT_ANCESTRY,
               region_ids: "list[str] | None" = None) -> tuple:
    """Return ``(out_rows, summary)`` for one emitted ``pcs_pairs.tsv``.

    Reads the pairs TSV, the region manifest and the cohort ``.bim``. Nothing
    else is opened; no genotype is decoded; the sweep is never re-run.
    """
    pairs_tsv = Path(pairs_tsv)
    bim_path = Path(bim_path)
    regions_tsv = Path(regions_tsv)
    for path in (pairs_tsv, regions_tsv):
        if not path.exists():
            raise FileNotFoundError(f"missing input: {path}")
    if not bim_path.exists():
        raise FileNotFoundError(
            f"missing cohort .bim: {bim_path}. This tool reads the prefix's own "
            f".bim and nothing else."
        )

    rows = _read_pairs_tsv(pairs_tsv)
    undefined_rows = [r for r in rows if _parse_bool(r["undefined"])]

    windows_selected = _read_regions_tsv(regions_tsv, region_ids, ancestry=ancestry)
    selected_ids = [w[0] for w in windows_selected]
    selected_set = set(selected_ids)

    tsv_region_ids = sorted({r["region_id"] for r in undefined_rows})
    unknown = [rid for rid in tsv_region_ids if rid not in selected_set]
    if unknown and region_ids is None:
        raise ValueError(
            f"pairs TSV carries undefined rows for region id(s) {unknown} that "
            f"{regions_tsv} does not contain for ancestry {ancestry!r}. That is "
            f"a manifest/ancestry mismatch, not a residual: refusing to drop "
            f"them silently."
        )
    in_scope = [r for r in undefined_rows if r["region_id"] in selected_set]
    out_of_scope_ids = unknown

    scan_ids = {r["region_id"] for r in in_scope}
    windows = [w for w in windows_selected if w[0] in scan_ids]
    indexed = iter_bim_windows(
        # pad_bp=0 is LOAD-BEARING. Production builds its excludelist row set
        # from EXACTLY the in-window rows for [from_bp, to_bp] on chrom, with NO
        # padding (run_native_ld_panel.py:851-878). A padded row set is a
        # DIFFERENT population and would answer a different question.
        bim_path, windows, pad_bp=0,
    )

    all_out: list = []
    per_region: dict = {}
    rows_in_window: dict = {}
    pooled_ambiguous: set = set()
    for region_id, chrom, start_bp, end_bp in windows:
        region_rows = [r for r in in_scope if r["region_id"] == region_id]
        out_rows, occluded_ids, n_window_rows, region_ambiguous = _classify_region(
            region_id, chrom, start_bp, end_bp, indexed[region_id], region_rows
        )
        pooled_ambiguous.update(region_ambiguous)
        rollup = _roll_up(f"region {region_id}", out_rows, region_ambiguous)
        rollup.pop("occluded_member_vids")
        per_region[region_id] = {
            "region_id": region_id,
            "chrom": chrom,
            "start_bp": int(start_bp),
            "end_bp": int(end_bp),
            "n_rows_in_window": n_window_rows,
            "n_occluded_ids_in_window": len(occluded_ids),
            **rollup,
        }
        rows_in_window[region_id] = n_window_rows
        all_out.extend(out_rows)

    pooled = _roll_up("pooled", all_out, pooled_ambiguous)
    pooled.update({
        "n_rows_in_tsv": len(rows),
        "n_defined_rows_in": len(rows) - len(undefined_rows),
        "n_undefined_rows_out_of_scope": len(undefined_rows) - len(in_scope),
    })

    summary = {
        "provenance": {
            "pairs_tsv_path": str(pairs_tsv),
            "pairs_tsv_sha256": _sha256(pairs_tsv),
            "pairs_tsv_n_lines": _count_lines(pairs_tsv),
            "bim_path": str(bim_path),
            "bim_sha256": _sha256(bim_path),
            "bim_n_lines": _count_lines(bim_path),
            "regions_tsv_path": str(regions_tsv),
            "regions_tsv_sha256": _sha256(regions_tsv),
            "ancestry": ancestry,
            "region_ids": sorted(scan_ids),
            "region_ids_selected": sorted(selected_set),
            "region_ids_out_of_scope": sorted(out_of_scope_ids),
            "n_rows_in_window_per_region": rows_in_window,
            "verdict_scope": VERDICT_SCOPE,
        },
        "pooled": {key: pooled[key] for key in POOLED_KEYS},
        "per_region": {
            rid: {key: block[key] for key in PER_REGION_KEYS}
            for rid, block in per_region.items()
        },
    }
    return all_out, summary


def write_out_tsv(out_rows, path: "str | Path") -> None:
    """Write the per-row verdict TSV. Header EQUALS :data:`OUT_COLUMNS`."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\t".join(OUT_COLUMNS) + "\n")
        for row in out_rows:
            fh.write("\t".join(_render(row[col]) for col in OUT_COLUMNS) + "\n")


# =========================================================================== #
# CLI                                                                         #
# =========================================================================== #

def _build_parser() -> argparse.ArgumentParser:
    """The argv contract, mirroring ``pairwise_completeness_scan.py:1343``.

    ⚠ THE NAME IS A DECLARED CROSS-TASK CONTRACT: the staged-invocation gate in
    ``.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md``
    feeds its STAGED argv to this exact function, so a staged typo fails at
    verify time on this node instead of inside the perimeter.
    """
    parser = argparse.ArgumentParser(
        prog="pcs_panelwide_reclassify",
        description=(
            "POST-HOC: for each UNDEFINED pair in an already-emitted "
            "pcs_pairs.tsv, does either member land on the PRODUCTION "
            "excludelist that detect_occluded_variants builds over EVERY "
            "deletion in the region window? Reads the pairs TSV, the region "
            "manifest and the cohort .bim ONLY. Decodes no genotype, computes "
            "no LD, changes no criterion, and cannot require the sweep to be "
            "re-run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pairs-tsv", dest="pairs_tsv", type=Path, required=True,
        help=(
            "an emitted pcs_pairs.tsv. Its header must EQUAL "
            "pairwise_completeness_scan.TSV_COLUMNS or the run stops."
        ),
    )
    parser.add_argument(
        "--bfile-prefix", dest="bfile_prefix", type=Path, required=True,
        help=(
            "plink1 bfile prefix. ONLY the prefix's own .bim is opened — this "
            "tool is coordinate-only and reads no genotypes at all."
        ),
    )
    parser.add_argument(
        "--regions-tsv", dest="regions_tsv", type=Path, required=True,
        help=(
            "a config/ld_regions.tsv-shaped manifest (1-based cols 1 region_id, "
            "2 chr, 7 ancestry, 15 window_start, 16 window_end). Keyed on "
            "(region_id x ancestry), so --ancestry selects as well as --region-ids."
        ),
    )
    parser.add_argument(
        "--ancestry", dest="ancestry", default=DEFAULT_ANCESTRY,
        help=(
            "which ancestry's windows to read (1-based column 7). Reading the "
            f"manifest BLIND returns every window twice. Default {DEFAULT_ANCESTRY}."
        ),
    )
    parser.add_argument(
        "--region-ids", dest="region_ids",
        help=(
            "comma-separated subset of --regions-tsv region ids. OMIT the flag "
            "to use every region; a value that names no id after stripping "
            "(e.g. ' , ') is an ERROR and exits 2, NOT a silent all-region run."
        ),
    )
    parser.add_argument(
        "--out", dest="out", type=Path, required=True,
        help="per-undefined-row verdict TSV output path",
    )
    parser.add_argument(
        "--summary", dest="summary", type=Path, required=True,
        help="summary JSON output path (provenance / pooled / per_region)",
    )
    return parser


def main(argv: "list[str] | None" = None) -> int:
    """Run the reclassification. 0 on success, 2 on a bad or missing input.

    Every input is validated BEFORE either output file is opened, so a failure
    never leaves a partial artifact behind.
    """
    args = _build_parser().parse_args(argv)

    if args.region_ids is None:
        region_ids = None
    else:
        region_ids = [r.strip() for r in args.region_ids.split(",") if r.strip()]
        if not region_ids:
            print(
                f"ERROR: --region-ids was given but names no region id after "
                f"stripping: {args.region_ids!r}. OMIT the flag entirely to use "
                f"every region in --regions-tsv; an empty value is not the same "
                f"request.",
                file=sys.stderr,
            )
            return 2

    bim_path = Path(args.bfile_prefix).with_suffix(".bim")
    try:
        out_rows, summary = reclassify(
            args.pairs_tsv, bim_path, args.regions_tsv,
            ancestry=args.ancestry, region_ids=region_ids,
        )
    except (ValueError, FileNotFoundError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    write_out_tsv(out_rows, args.out)
    Path(args.summary).write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    pooled = summary["pooled"]
    print("=== PANEL-WIDE RECLASSIFICATION (POST-HOC; nothing was re-run) ===")
    for key in POOLED_KEYS:
        print(f"{key}\t{pooled[key]}")
    print()
    print("VERDICT SCOPE: " + summary["provenance"]["verdict_scope"])
    print(
        "NOTE: these are COUNTS over the scanned regions. They are NOT a "
        "prevalence, and they REVISE no pre-registered number."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
