"""Genome-wide reference-occlusion CATALOG assembler (m3-04b, Task 1).

THE PRODUCTION CALLER the m3-07b/07c functions never had. Four functions shipped
with ZERO callers — ``occlusion_manifest.aggregate_manifests`` (alias
``build_occlusion_catalog``), ``occlusion_manifest.add_grch37_positions``,
``occlusion_manifest.enrich_occlusion_manifest`` and
``occlusion_present_rate_scan.scan_present_rate``. This module calls all four, in
order, and writes ONE genome-wide enriched catalog that is simultaneously

  * the **Angle-1/3 catalog seed** — the auditable census of every variant the LD
    panel excluded for reference occlusion across all 276 regions, with the
    per-variant scientific cost (``traits_present`` / k of n) attached; and
  * the **drop key** the lockstep sumstats filter reads
    (``drop_occluded_from_sumstats``, 07c) — the same manifest, the same
    ``(chr, pos_grch37)`` key the panel exclusion was derived from, so the panel and
    the sumstats can never disagree about which variants exist (osf.io/az52u,
    file ``trsx5``, POSTED 2026-07-10T13:32:22Z).

THE EMPTY CATALOG IS SCHEMA-COMPLETE, AND THAT IS THE WHOLE POINT
-----------------------------------------------------------------
``enrich_occlusion_manifest`` SHORT-CIRCUITS on empty input
(``occlusion_manifest.py:361-363``): it writes the input's columns and returns,
so the output carries NO ``pos_grch37``. Delegating naively would therefore make
``drop_occluded_from_sumstats._load_manifest_keys`` fail CLOSED — correctly, by its
own deliberate design — on the *legitimate* no-op that is today's tree, where the
AoU fire has banked ZERO per-region manifests. The consume seam would be unrunnable
until the fire lands, which is the wire-it-later-and-forget failure mode this phase
has already paid for twice.

So after enrichment this module RE-ASSERTS the full schema
(:data:`CATALOG_COLUMNS`), adding any missing column as ``pd.NA``. An empty catalog
is then a header-only file that still declares ``chr`` and ``pos_grch37``, the drop
is an audited, honest ``n_dropped == 0``, and the seam goes live the moment real
manifests arrive with zero further wiring.

DEGRADED RECONSTRUCTION — OPT-IN, NEVER SILENT
----------------------------------------------
Today only the ``{region_id}.occluded.excludelist`` objects are uploaded out of the
perimeter (``run_native_ld_panel.py:937``); the Stage-A manifest is written to local
scratch and never sent (the producer-side fix is m3-04c's PRE-FIRE item). A catalog
CAN be rebuilt from those excludelists — the variant ids are ``chr:pos:ref:alt`` on
GRCh38 — but the ref-span and occluding-deletion attribution is UNRECOVERABLE from
them. Degraded rows therefore carry those columns as explicit NA and are stamped
``provenance_source="excludelist_degraded"``, and the assembler REFUSES to emit a
degraded catalog unless ``allow_degraded`` is passed explicitly. The loss is visible
IN the artifact rather than inferred from its absence.

A line that does not parse as ``chr:pos:ref:alt`` is skipped with a loud STDERR
warning and counted — never guessed at. A fabricated coordinate would drop the WRONG
sumstats row, the exact harm the lockstep exists to prevent.

EGRESS (REQ-AOU-LD-EGRESS): every emitted column is coordinate/ID/aggregate-rate
only. Nothing per-person, per-sample or per-genotype is derived here, and
``tests/m3/test_occlusion_catalog_assembly.py`` re-runs the Stage-A token scan over
this catalog's own header so a column cannot ride out through the rollup.

Runs in smoke_dev py3.11 (pandas + pyliftover). No Hail, no perimeter, $0.
m3-06 stays HELD: this module imports NOTHING from the LD-conditioning path, and
the NaN-to-zero fill it once proposed is DEAD — occluded variants are EXCLUDED with
provenance, never zeroed.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

import occlusion_manifest as om
from occlusion_present_rate_scan import scan_present_rate

__all__ = [
    "CATALOG_COLUMNS",
    "PROVENANCE_EXCLUDELIST_DEGRADED",
    "PROVENANCE_STAGE_A_MANIFEST",
    "assemble_occlusion_catalog",
    "load_expected_region_ids",
    "main",
]

#: Provenance stamps. The catalog says how it was built, on every row, because
#: "built from the real Stage-A manifests" and "reconstructed from the ids that
#: happened to be uploaded" are different scientific claims.
PROVENANCE_STAGE_A_MANIFEST = "stage_a_manifest"
PROVENANCE_EXCLUDELIST_DEGRADED = "excludelist_degraded"

#: The columns an assembled catalog ALWAYS carries, in this order — including when
#: it is EMPTY. ``chr`` + ``pos_grch37`` are the load-bearing pair: they are the
#: drop key ``drop_occluded_from_sumstats._load_manifest_keys`` fails closed on.
CATALOG_COLUMNS: list[str] = [
    *om.STAGE_A_COLUMNS,
    "provenance_source",
    "pos_grch37",
    "chain_sha256",
    *om.STAGE_B_TRAIT_COLUMNS,
    "present_rate",
]

#: Columns an excludelist can never carry — the occluding deletion's identity and
#: REF-span footprint live in the .bim geometry the manifest was derived from.
_DEGRADED_UNRECOVERABLE = [
    "ref_span_start_grch38",
    "ref_span_end_grch38",
    "occluding_deletion_id",
    "occluding_deletion_ref_len",
]

#: The driver writes ``{region_id}.occluded.excludelist``
#: (``run_native_ld_panel.py:806``), uploaded under the same name (``:937``).
_EXCLUDELIST_SUFFIX = ".occluded"


def load_expected_region_ids(regions_tsv: "str | Path",
                             ancestry: str = "AFR") -> "set[str]":
    """The expected ``region_id`` set for ``ancestry``, from the M2 region manifest.

    ⚠ **THE 276/552 TRAP.** ``config/ld_regions.tsv`` is header + **552 DATA ROWS** =
    **276 unique ``region_id`` x 2 ancestries (AFR, EUR)**. The authoritative count is
    ``nunique(region_id)`` FILTERED TO ``ancestry`` — **NEVER** ``len(df)`` or
    ``wc -l``, which give 552/553 and would make any coverage assertion built on them
    fail 100% of the time. Verified directly:

        awk -F'\\t' 'NR>1{print $1}' config/ld_regions.tsv | sort -u | wc -l  -> 276
        ... $7=="AFR" ...                                                     -> 276
        ... $7=="EUR" ...                                                     -> 276

    Both ancestries carry the SAME 276 ids; only the ROWS double. Returns ``str`` ids
    so the comparison never depends on a pandas dtype inference.
    """
    df = pd.read_csv(regions_tsv, sep="\t", dtype={"region_id": str})
    for col in ("region_id", "ancestry"):
        if col not in df.columns:
            raise ValueError(
                f"{regions_tsv} is missing the {col!r} column; the expected-region "
                "set is derived from nunique(region_id) filtered to ancestry."
            )
    return set(df.loc[df["ancestry"] == ancestry, "region_id"].astype(str))


def _region_id_from_excludelist(path: Path) -> str:
    """``m2_region_00001.occluded.excludelist`` -> ``m2_region_00001``."""
    stem = path.name
    for suffix in (".excludelist", ".txt"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    if stem.endswith(_EXCLUDELIST_SUFFIX):
        stem = stem[: -len(_EXCLUDELIST_SUFFIX)]
    return stem


def _parse_excludelist_variant(vid: str) -> "dict | None":
    """Parse a ``chr:pos:ref:alt`` GRCh38 variant id, or return None.

    The production ids come from ``hl.export_plink`` (``run_native_ld_panel.py:391-400``)
    and are 4-field colon-delimited. Anything else — an rsID, a truncated line, a
    non-numeric position — is NOT coerced: a plausible-but-wrong coordinate would
    join and drop the WRONG sumstats row.
    """
    parts = vid.split(":")
    if len(parts) != 4:
        return None
    chrom, pos, ref, alt = (p.strip() for p in parts)
    contig = chrom[3:] if chrom.lower().startswith("chr") else chrom
    if not contig or not ref or not alt:
        return None
    try:
        pos_i = int(pos)
    except (TypeError, ValueError):
        return None
    if pos_i <= 0:
        return None
    return {"chr": contig, "pos_grch38": pos_i, "ref": ref, "alt": alt}


def _degraded_records(excludelist_paths: Sequence[Path]) -> "tuple[list[dict], int]":
    """Reconstruct Stage-A-shaped records from the uploaded excludelists.

    Returns ``(records, n_unparseable)``. The unrecoverable attribution columns are
    explicit ``pd.NA``; ``occlusion_order`` is ``"direct"`` because every
    coordinate-derived occlusion a Stage A can see is a direct REF-span overlap
    (``occlusion_manifest`` module docstring, "ON occlusion_order").
    """
    records: list[dict] = []
    n_unparseable = 0
    for path in excludelist_paths:
        region_id = _region_id_from_excludelist(path)
        for raw in path.read_text().splitlines():
            vid = raw.strip()
            if not vid:
                continue
            parsed = _parse_excludelist_variant(vid)
            if parsed is None:
                n_unparseable += 1
                print(
                    f"[assemble_occlusion_catalog] WARNING: {path.name}: line "
                    f"{vid!r} is not a chr:pos:ref:alt GRCh38 variant id — SKIPPED "
                    "and counted, never guessed at (a fabricated coordinate would "
                    "drop the WRONG sumstats row).",
                    file=sys.stderr,
                )
                continue
            rec = {
                "region_id": region_id,
                "chr": parsed["chr"],
                "variant_id": vid,
                "pos_grch38": parsed["pos_grch38"],
                "ref": parsed["ref"],
                "alt": parsed["alt"],
                "reason": om.REASON_REFERENCE_OCCLUSION,
                "occlusion_order": "direct",
            }
            for col in _DEGRADED_UNRECOVERABLE:
                rec[col] = pd.NA
            records.append(rec)
    return records, n_unparseable


def _write_stage_a(records: Sequence[dict], path: Path, provenance: str) -> None:
    """Write a Stage-A-shaped frame (plus ``provenance_source``) to ``path``."""
    columns = [*om.STAGE_A_COLUMNS, "provenance_source"]
    df = pd.DataFrame(list(records))
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    df["provenance_source"] = provenance
    extras = [c for c in df.columns if c not in columns]
    df = df[[*columns, *extras]]
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def _derive_present_rate(df: pd.DataFrame) -> list:
    """``n_traits_present / n_traits_scanned``, NA-guarded at n == 0.

    Closes the first pre-existing ``63bdb59`` consumer note: the rate was derivable
    in principle and never PERSISTED, so every reader had to re-derive it (and could
    re-derive it differently). ``n == 0`` is ``pd.NA``, never 0.0 — "nothing was
    scanned" and "scanned, found nowhere" are different results.
    """
    rates: list = []
    for k, n in zip(df["n_traits_present"], df["n_traits_scanned"]):
        try:
            kf, nf = float(k), float(n)
        except (TypeError, ValueError):
            rates.append(pd.NA)
            continue
        if pd.isna(kf) or pd.isna(nf) or nf <= 0:
            rates.append(pd.NA)
        else:
            rates.append(kf / nf)
    return rates


def _complete_schema(out_path: Path) -> pd.DataFrame:
    """Re-assert :data:`CATALOG_COLUMNS` on the enriched catalog and rewrite it.

    THE step that makes an EMPTY catalog usable. See the module docstring.
    """
    df = pd.read_csv(out_path, sep="\t",
                     dtype={"region_id": str, "variant_id": str})
    for col in CATALOG_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    df["present_rate"] = _derive_present_rate(df)
    extras = [c for c in df.columns if c not in CATALOG_COLUMNS]
    df = df[[*CATALOG_COLUMNS, *extras]]
    df.to_csv(out_path, sep="\t", index=False)
    return df


_README_TEMPLATE = """# Occlusion catalog — reader notes

Artifact: `{name}`
Produced by: `src/python/assemble_occlusion_catalog.py`
(m3-04b Task 1; pre-registration osf.io/az52u, file `trsx5`, POSTED 2026-07-10T13:32:22Z)

## What this is

The genome-wide census of every variant the AFR LD panel excluded because an
overlapping deletion's REF span makes its LD structurally undefined
(`occlusion_span_filter.py`, m3-07b). It is BOTH the Angle-1/3 catalog seed and the
drop key `src/python/drop_occluded_from_sumstats.py` reads — the same manifest the
panel exclusion is keyed on, so the panel and the sumstats cannot disagree about
which variants exist.

## Two reader gotchas (pre-existing `63bdb59` consumer notes)

1. **`traits_present` is a STRINGIFIED LIST, not a list.** `enrich_occlusion_manifest`
   serialises the scan's `list[str]` through `DataFrame.to_csv`, so a reader gets the
   *string* `"['bmi', 'ldl']"`, not `['bmi', 'ldl']`. Parse it explicitly:

   ```python
   import ast
   traits = ast.literal_eval(row["traits_present"]) if pd.notna(row["traits_present"]) else []
   ```

   `ast.literal_eval` (never `eval`) is the recommended parse. The serialisation is
   NOT changed here: it is shipped and pinned by
   `tests/m3/test_occlusion_manifest.py`, and changing it would move a contract this
   plan is required to leave at a 0-line diff.

2. **`present_rate` is persisted here, as `n_traits_present / n_traits_scanned`**, and
   is `NA` (not `0.0`) when `n_traits_scanned == 0` — "nothing was scanned" and
   "scanned, found nowhere" are different scientific results.

## Provenance

`provenance_source` is one of:

* `{stage_a}` — built from the real per-region Stage-A manifests. Full
  ref-span / occluding-deletion attribution present.
* `{degraded}` — reconstructed from the uploaded
  `{{region_id}}.occluded.excludelist` objects because the Stage-A manifests did not
  cross the perimeter. Variant identity is intact; `ref_span_start_grch38`,
  `ref_span_end_grch38`, `occluding_deletion_id` and `occluding_deletion_ref_len`
  are **NA and unrecoverable**. Requires an explicit `--allow-degraded`.

`chain_sha256` records the identity of the hg38ToHg19 chain used for `pos_grch37`,
so the build-37 coordinates are reproducible rather than taken on faith. A variant
that did not lift carries `pos_grch37 = NA` — never a guessed coordinate.

## Empty is a valid state

Before the AoU fire banks per-region manifests this catalog is HEADER-ONLY. It still
declares `chr` and `pos_grch37` on purpose, so the lockstep drop runs as an audited
`n_dropped == 0` no-op instead of tripping the (correct) fail-closed Stage-A guard in
`drop_occluded_from_sumstats._load_manifest_keys`.
"""


def assemble_occlusion_catalog(
    manifest_paths: Iterable["str | Path"],
    chain_path: "str | Path",
    sumstats_paths: Iterable["str | Path"],
    out_path: "str | Path",
    *,
    excludelist_paths: "Iterable[str | Path] | None" = None,
    allow_degraded: bool = False,
    expected_region_ids: "Iterable[str] | None" = None,
    allow_partial_manifest: bool = False,
) -> dict:
    """Assemble the genome-wide enriched occlusion catalog.

    ``manifest_paths``  : per-region Stage-A ``occlusion_manifest.tsv`` files (may be
                          empty / absent — that is the state of the tree today).
    ``chain_path``      : ``data/external/liftover/hg38ToHg19.over.chain.gz``.
    ``sumstats_paths``  : harmonized GRCh37 sumstats to scan for the present-rate
                          (the 9 public AFR files in production).
    ``out_path``        : the catalog TSV. ``{out_path}.README.md`` is written beside it.
    ``excludelist_paths``: optional ``{region_id}.occluded.excludelist`` objects, used
                          ONLY when the Stage-A rollup is empty.
    ``allow_degraded``  : must be True to emit a degraded (excludelist-derived) catalog.
    ``expected_region_ids``: optional expected ``region_id`` set (see
                          :func:`load_expected_region_ids` and THE 276/552 TRAP). An
                          OBSERVED id outside it RAISES; a strict SUBSET is REPORTED.
    ``allow_partial_manifest``: must be True to accept a Stage-A rollup that does NOT
                          cover every region carrying an excludelist (BLOCKER-4).

    Returns ``{"n_regions", "n_variants", "n_lifted", "n_unlifted", "n_unparseable",
    "source", "n_regions_excludelist_only", "regions_excludelist_only",
    "n_regions_expected", "n_regions_missing", "n_files_scanned",
    "n_distinct_traits_scanned", "n_scan_rows_seen", "n_scan_rows_parsed",
    "n_scan_unparseable"}``. The ``n_scan_*`` prefix is
    load-bearing: ``n_unparseable`` already means "excludelist LINES that did not
    parse" and must not be conflated with "sumstats COORDINATES that did not parse".

    Raises ``ValueError`` when a degraded reconstruction is possible but not
    authorised. Nothing is written to ``out_path`` in that case. Also propagates the
    present-rate scan's own refusal when a scanned file carries body rows but yields
    no coercible coordinate at all (HIGH-0).
    """
    out_path = Path(out_path)
    chain_path = Path(chain_path)
    manifest_paths = [Path(p) for p in manifest_paths]
    sumstats_paths = [Path(p) for p in sumstats_paths]
    excludelist_paths = [Path(p) for p in (excludelist_paths or [])]

    n_unparseable = 0
    orphaned: list[str] = []
    expected: "set[str] | None" = (
        {str(r) for r in expected_region_ids}
        if expected_region_ids is not None else None
    )

    with tempfile.TemporaryDirectory(prefix="occlusion_catalog_") as tmpdir:
        stage_a = Path(tmpdir) / "occlusion_catalog.stage_a.tsv"

        # (a) the shipped rollup — dedup on (region_id, variant_id), absent/empty
        #     per-region manifests skipped (a region with zero occlusion writes none).
        om.aggregate_manifests(manifest_paths, stage_a)
        rollup = pd.read_csv(stage_a, sep="\t",
                             dtype={"region_id": str, "variant_id": str})

        # (b) degraded reconstruction, opt-in only
        if not rollup.empty:
            source = PROVENANCE_STAGE_A_MANIFEST
            # BLOCKER-4. The override below fires when the rollup is merely NON-EMPTY.
            # The shipped note claimed "the manifests carry strictly more provenance",
            # which is TRUE PER REGION and FALSE AS A SET CLAIM the moment the
            # manifest set is a SUBSET of the regions that have excludelists. Those
            # regions' occluded variants would then never be dropped from the
            # sumstats: ORPHANED VARIANTS, wearing a `stage_a_manifest` stamp saying
            # everything is fine. The triggering state is already coded — the
            # per-region Stage-A append at run_native_ld_panel.py:821-831 is
            # best-effort and continues on any exception WHILE STILL WRITING the
            # excludelist.
            manifest_regions = set(rollup["region_id"].astype(str))
            excl_regions = {_region_id_from_excludelist(p) for p in excludelist_paths}
            orphaned = sorted(excl_regions - manifest_regions)
            if orphaned and not allow_partial_manifest:
                raise ValueError(
                    "REFUSING to stamp provenance_source='stage_a_manifest' on a "
                    f"PARTIAL Stage-A rollup. {len(orphaned)} region(s) carry an "
                    "excludelist but have NO Stage-A manifest in this rollup: "
                    f"{', '.join(orphaned)}. Ignoring the excludelists here is only "
                    "justified when every excludelist region is ALSO covered by a "
                    "manifest — 'the manifests carry strictly more provenance' is "
                    "true PER REGION and FALSE AS A SET CLAIM when the manifest set "
                    "is a SUBSET of the regions with excludelists. Proceeding would "
                    "silently omit those regions from the catalog, so their occluded "
                    "variants are NEVER DROPPED from the sumstats — ORPHANED "
                    "VARIANTS, the exact failure the pre-registered lockstep exists "
                    "to forbid (osf.io/az52u), under a provenance stamp that says "
                    "everything is fine. REMEDIES: (1) supply the missing Stage-A "
                    "manifests for those regions, or (2) pass "
                    "--allow-partial-manifest / allow_partial_manifest=True to "
                    "accept a knowingly-incomplete catalog EXPLICITLY (the gap is "
                    "then reported as n_regions_excludelist_only)."
                )
            # NOT A UNION, DELIBERATELY. Merging manifest rows with excludelist rows
            # would produce a MIXED provenance_source — a property §1 of the blast
            # radius verified as currently invariant (assemble_occlusion_catalog.py:202
            # assigns it as a scalar over the whole frame) — and would let DEGRADED
            # rows, which permanently lack the ref-span / occluding-deletion
            # attribution, ride out WITHOUT the allow_degraded gate the
            # pre-registration depends on. Refusing (or an explicit opt-in) keeps both
            # properties intact.
            if excludelist_paths:
                print(
                    "[assemble_occlusion_catalog] NOTE: every region carrying an "
                    "excludelist is already covered by a Stage-A manifest"
                    + (f" EXCEPT {', '.join(orphaned)} (accepted explicitly via "
                       "--allow-partial-manifest)" if orphaned else "")
                    + f", so the {len(excludelist_paths)} excludelist(s) are IGNORED "
                    "(for a covered region the manifest carries strictly more "
                    "provenance).",
                    file=sys.stderr,
                )
            _write_stage_a(rollup.to_dict("records"), stage_a, source)
        elif excludelist_paths:
            source = PROVENANCE_EXCLUDELIST_DEGRADED
            degraded_regions = sorted(
                {_region_id_from_excludelist(p) for p in excludelist_paths}
            )
            if not allow_degraded:
                missing = ", ".join(str(p) for p in manifest_paths) or "(none supplied)"
                raise ValueError(
                    "REFUSING to assemble a DEGRADED occlusion catalog. The Stage-A "
                    f"per-region manifests are absent or empty [{missing}], so the "
                    "only reconstruction available is from the "
                    f"{len(excludelist_paths)} uploaded excludelist(s) for region(s): "
                    f"{', '.join(degraded_regions)}. That reconstruction PERMANENTLY "
                    "loses the ref-span and occluding-deletion attribution "
                    f"({', '.join(_DEGRADED_UNRECOVERABLE)}), which the "
                    "pre-registration (osf.io/az52u) commits to publishing. Pass "
                    "--allow-degraded / allow_degraded=True to accept that loss "
                    "explicitly; it must never happen silently."
                )
            records, n_unparseable = _degraded_records(excludelist_paths)
            _write_stage_a(records, stage_a, source)
        else:
            source = "empty"
            _write_stage_a([], stage_a, source)

        # (c) Stage-B lift, used ONLY to build the present-rate scan keys. enrich()
        #     re-lifts internally from the file; the shipped API takes present_rate as
        #     an INPUT, so the keys must exist before it is called. Two lifts of a few
        #     thousand rows is the honest cost of not editing a frozen module.
        stage_a_df = pd.read_csv(stage_a, sep="\t",
                                 dtype={"region_id": str, "variant_id": str})

        # (b2) region-coverage reporting, computed BEFORE out_path is touched so a
        #      refusal never leaves a partial catalog behind.
        observed_regions = (
            {str(r) for r in stage_a_df["region_id"].dropna()}
            if "region_id" in stage_a_df.columns and not stage_a_df.empty else set()
        )
        n_regions_expected = n_regions_missing = None
        if expected is not None:
            unknown = sorted(observed_regions - expected)
            if unknown:
                raise ValueError(
                    f"REFUSING to write a catalog with {len(unknown)} region id(s) "
                    f"that are NOT in the expected set: {', '.join(unknown)}. That is "
                    "region-naming drift or a crosswalk bug, and a catalog keyed on "
                    "ids nothing downstream recognises drops NOTHING while looking "
                    f"complete. The expected set holds {len(expected)} id(s) (from "
                    "the M2 region manifest, nunique(region_id) filtered to the "
                    "ancestry). Fix the ids or the manifest; do not silence this."
                )
            n_regions_expected = len(expected)
            # REPORTED, NEVER ASSERTED. A region with ZERO occluded variants writes no
            # manifest at all (aggregate_manifests skips absent/empty ones), so
            # n_regions == len(expected) is NOT a valid invariant — asserting it would
            # fail on every honest run. What IS actionable is the number itself, next
            # to the catalog, so a reader can judge coverage rather than assume it.
            n_regions_missing = len(expected - observed_regions)

        present_rate = None
        #: The scan's PARSE HEALTH (HIGH-4/HIGH-0). Filled in place by
        #: scan_present_rate and threaded into enrich, whose key-membership guard
        #: cannot see a scan that read nothing (every requested key comes back).
        scan_stats: dict = {}
        if not stage_a_df.empty:
            lifted = om.add_grch37_positions(
                stage_a_df.to_dict("records"), chain_path=chain_path
            )
            keys = [
                (rec["chr"], rec["pos_grch37"])
                for rec in lifted
                if rec.get("pos_grch37") is not None
            ]
            # (d) the present-rate scan. Pass None (NOT {}) when there is nothing
            #     liftable: enrich's documented raise boundary treats a non-empty
            #     present_rate that matches no liftable row as a key-contract
            #     regression, and an empty dict is falsy anyway — being explicit here
            #     keeps the intent readable rather than accidental.
            if keys:
                present_rate = scan_present_rate(
                    keys, sumstats_paths, stats=scan_stats
                )

        # (e) the shipped enrichment: pos_grch37 + chain_sha256 + the Stage-B seam.
        out_path.parent.mkdir(parents=True, exist_ok=True)
        om.enrich_occlusion_manifest(
            stage_a, chain_path, out_path=out_path, present_rate=present_rate,
            scan_stats=scan_stats or None,
        )

    # THE schema completion (see module docstring). Without this an EMPTY catalog
    # carries no pos_grch37 and the whole consume seam is unrunnable today.
    df = _complete_schema(out_path)

    lifted_mask = df["pos_grch37"].notna() if len(df) else df.index
    n_lifted = int(lifted_mask.sum()) if len(df) else 0
    n_regions = int(df["region_id"].nunique()) if len(df) else 0

    Path(f"{out_path}.README.md").write_text(
        _README_TEMPLATE.format(
            name=out_path.name,
            stage_a=PROVENANCE_STAGE_A_MANIFEST,
            degraded=PROVENANCE_EXCLUDELIST_DEGRADED,
        )
    )

    return {
        "n_regions": n_regions,
        "n_variants": int(len(df)),
        "n_lifted": n_lifted,
        "n_unlifted": int(len(df)) - n_lifted,
        "n_unparseable": n_unparseable,
        "source": source,
        # BLOCKER-4 coverage. `n_regions_excludelist_only` puts the incompleteness IN
        # the artifact's provenance, so it can never be inferred from an absence.
        "n_regions_excludelist_only": len(orphaned),
        "regions_excludelist_only": orphaned,
        "n_regions_expected": n_regions_expected,
        "n_regions_missing": n_regions_missing,
        # The present-rate scan's PARSE HEALTH (HIGH-4). Deliberately prefixed
        # `n_scan_*`: `n_unparseable` above is ALREADY TAKEN by the degraded
        # excludelist path and counts unparseable excludelist LINES, which is a
        # different thing from an unparseable sumstats COORDINATE. Colliding them
        # would make the catalog's own audit numbers ambiguous — the exact class of
        # failure this plan exists to close.
        "n_files_scanned": int(scan_stats.get("n_files_scanned", 0)),
        "n_distinct_traits_scanned": int(
            scan_stats.get("n_distinct_traits_scanned", 0)
        ),
        "n_scan_rows_seen": int(scan_stats.get("n_rows_seen", 0)),
        "n_scan_rows_parsed": int(scan_stats.get("n_rows_parsed", 0)),
        "n_scan_unparseable": int(scan_stats.get("n_unparseable", 0)),
    }


def main(argv: "Sequence[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="assemble_occlusion_catalog",
        description=(
            "Assemble the genome-wide reference-occlusion catalog from the per-region "
            "Stage-A manifests (or, with --allow-degraded, from the uploaded "
            "excludelists), lift to GRCh37, and join the present-rate scan."
        ),
    )
    parser.add_argument("--manifest", nargs="*", default=[],
                        help="per-region Stage-A occlusion_manifest.tsv paths")
    parser.add_argument("--excludelist", nargs="*", default=[],
                        help="{region_id}.occluded.excludelist paths (degraded fallback)")
    parser.add_argument("--chain", required=True,
                        help="hg38ToHg19 liftover chain (.over.chain.gz)")
    parser.add_argument("--sumstats", nargs="*", default=[],
                        help="harmonized GRCh37 sumstats to scan for the present-rate")
    parser.add_argument("--out", required=True, help="catalog TSV to write")
    parser.add_argument("--allow-degraded", action="store_true",
                        help="authorise an excludelist-derived (degraded) catalog")
    parser.add_argument("--regions-tsv", default=None,
                        help=("M2 region manifest (config/ld_regions.tsv). When given, "
                              "the expected region_id set is derived from it — "
                              "nunique(region_id) filtered to --regions-ancestry, "
                              "NEVER len(df): the file is 552 data rows = 276 ids x 2 "
                              "ancestries"))
    parser.add_argument("--regions-ancestry", default="AFR",
                        help="ancestry to filter --regions-tsv on (default: AFR)")
    parser.add_argument("--allow-partial-manifest", action="store_true",
                        help=("accept a Stage-A rollup that does NOT cover every "
                              "region carrying an excludelist (the gap is then "
                              "reported as n_regions_excludelist_only)"))
    args = parser.parse_args(argv)

    expected_region_ids = None
    if args.regions_tsv:
        expected_region_ids = load_expected_region_ids(
            args.regions_tsv, ancestry=args.regions_ancestry
        )

    result = assemble_occlusion_catalog(
        args.manifest, args.chain, args.sumstats, args.out,
        excludelist_paths=args.excludelist, allow_degraded=args.allow_degraded,
        expected_region_ids=expected_region_ids,
        allow_partial_manifest=args.allow_partial_manifest,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
