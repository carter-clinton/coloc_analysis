"""Reference-occlusion PROVENANCE MANIFEST (m3-07b, T2).

This module is the other half of the pre-registered policy. Excluding a variant
whose LD is structurally undefined (``occlusion_span_filter.py``) is only half of
what the OSF amendment-update commits to (osf.io/az52u, POSTED
2026-07-10T13:32:22Z, recorded ``ac4c990``): the variant is dropped in LOCKSTEP
from the LD panel AND the harmonized sumstats, and **every drop is auditable**.
A missing or incorrect manifest column is a PRE-REGISTRATION FAILURE, not a
logging nit — this is load-bearing scientific provenance, and it is the seed of
the genome-wide Angle-1/3 occlusion catalog.

TWO STAGES, SPLIT ON THE EGRESS BOUNDARY
----------------------------------------
**Stage A — in-perimeter, egress-clean.** :func:`build_region_records` /
:func:`append_region_manifest` emit pure COORDINATE GEOMETRY: variant ids,
positions, alleles, the occluding deletion's reference span. NO genotypes, NO
per-person or per-sample counts (REQ-AOU-LD-EGRESS). Everything here is derivable
from a ``.bim`` alone — it is variant *annotation*, not individual-level data, so
it may cross the AoU perimeter with the aggregate LD matrix. The test suite
enforces this with a substring/token scan over every emitted key, so an
``n_samples``/``genotype_ac``-style column cannot quietly ride out.

**Stage B — NC-State enrichment.** :func:`add_grch37_positions` adds
``pos_grch37`` (+ the chain SHA-256 for provenance) once the manifest is outside
the perimeter. The panel<->sumstats join is (CHR,POS)-only on GRCh37
(``snp_id_bridge.R:107-121``, drop-only, no re-key), so a wrong ``pos_grch37``
would silently drop the WRONG sumstats row and break the lockstep. The liftover
therefore reuses the EXACT ``ld_npz_to_rds.R:167-183`` recipe (pyliftover,
``convert_coordinate("chr"+chr, pos-1)`` 0-based in, ``+1`` out) rather than
re-deriving a convention, and records a failed lift as an explicit NA — never a
guessed or passed-through coordinate.

``traits_present`` / ``n_traits_present`` / ``n_traits_scanned`` are a DOCUMENTED
SEAM: the columns are declared here (:data:`STAGE_B_TRAIT_COLUMNS`) and populated
by the 07c present-rate scan. They are deliberately absent from Stage A.

ON ``occlusion_order``
----------------------
Emitted as ``"direct"`` for EVERY record, and that is not a placeholder. A
coordinate-only Stage A sees exactly one thing: a variant sitting inside an
occluding deletion's REF span — a DIRECT ``ref_span_overlap``. That includes
region-1's snpC (5922718), whose occluder is the UPSTREAM ``DEL 5922716``
(``m3_region1_nan_geometry_verdict.md:19`` records that pair as
``ref_span_overlap``). The "second-order" label in the verdict attaches to the
*disjoint* pair-4 EDGE (``5922718 <-> DEL 5922724``), which occludes nothing and
is a GENOTYPE-layer consequence this stage cannot observe. Emitting
``second_order`` here would require hardcoding position 5922718 — publishing a
false provenance label across all 276 regions. If a later genotype-aware stage
annotates that tangle, it does so in its OWN field rather than mislabelling this
variant's coordinate-derived occlusion.

Runs in smoke_dev py3.11 (pandas; pyliftover imported LAZILY so the in-perimeter
Stage-A path needs neither the chain file nor the package). No Hail.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

from occlusion_span_filter import detect_occluded_variants, parse_bim_row

__all__ = [
    "REASON_REFERENCE_OCCLUSION",
    "STAGE_A_COLUMNS",
    "STAGE_B_TRAIT_COLUMNS",
    "add_grch37_positions",
    "aggregate_manifests",
    "append_occlusion_rows",
    "append_region_manifest",
    "build_occlusion_catalog",
    "build_region_records",
    "chain_sha256",
    "enrich_occlusion_manifest",
]

#: The single reason constant every reference-occlusion drop carries. Exported so
#: call sites and tests reference THE constant rather than re-typing the string
#: (the source doc-set renders the arrow with and without surrounding spaces).
REASON_REFERENCE_OCCLUSION = "reference-occlusion → undefined-LD"

#: Stage-A schema, in emission order. COORDINATE/ID-ONLY — see the module
#: docstring's egress note before adding anything here.
STAGE_A_COLUMNS = [
    "region_id",
    "chr",
    "variant_id",
    "pos_grch38",
    "ref",
    "alt",
    "ref_span_start_grch38",
    "ref_span_end_grch38",
    "occluding_deletion_id",
    "occluding_deletion_ref_len",
    "reason",
    "occlusion_order",
]

#: Stage-B trait columns — the DOCUMENTED 07c seam (populated by the present-rate
#: scan, not by this module).
STAGE_B_TRAIT_COLUMNS = ["traits_present", "n_traits_present", "n_traits_scanned"]

#: Every edge a coordinate-only Stage A can derive is a direct REF-span overlap.
_OCCLUSION_ORDER_DIRECT = "direct"

_DEDUP_KEY = ["region_id", "variant_id"]


def build_region_records(region_id: str, rows: Sequence[Sequence]) -> list[dict]:
    """Build the Stage-A records for ONE region's window ``.bim`` rows.

    Runs the span filter over ``rows`` and emits one coordinate-only record per
    OCCLUDED variant. ``ref_span_start/end_grch38`` and the ``occluding_deletion_*``
    columns are derived from the OCCLUDING deletion the detector attributed the
    drop to (region-1's snpC -> the UPSTREAM ``DEL 5922716``, never the downstream
    ``DEL 5922724``) — getting that backwards would publish a wrong provenance
    record for a real variant.

    Records are emitted in ``occluded_ids`` order (sorted, unique), so the manifest
    is deterministic and diff-able across re-runs.
    """
    parsed = [parse_bim_row(r, index=i) for i, r in enumerate(rows)]
    by_id = {v.vid: v for v in parsed}
    # The raw row carries the alleles; the parsed variant carries the geometry.
    raw_by_id = {str(r[1]): r for r in rows}

    occluded_ids, edges = detect_occluded_variants(rows)
    occluder_of = {occluded: occluder for occluder, occluded in edges}

    records: list[dict] = []
    for vid in occluded_ids:
        v = by_id[vid]
        raw = raw_by_id[vid]
        d = by_id[occluder_of[vid]]
        records.append({
            "region_id": str(region_id),
            "chr": str(raw[0]),
            "variant_id": vid,
            "pos_grch38": v.pos,
            "ref": str(raw[5]),          # A2 = REF
            "alt": str(raw[4]),          # A1 = ALT
            "ref_span_start_grch38": d.pos,
            "ref_span_end_grch38": d.span_end,   # POS_D + len(REF_D) − 1
            "occluding_deletion_id": d.vid,
            "occluding_deletion_ref_len": d.ref_len,
            "reason": REASON_REFERENCE_OCCLUSION,
            "occlusion_order": _OCCLUSION_ORDER_DIRECT,
        })
    return records


def append_region_manifest(manifest_path: "str | Path",
                           records: Iterable[dict]) -> Path:
    """Append Stage-A ``records`` to ``manifest_path``, RESUME-SAFE.

    Dedup is keyed on ``(region_id, variant_id)`` — mirroring
    ``run_native_ld_panel._append_panel_row_local``'s dedup-by-region_id pattern,
    widened because a manifest holds MANY rows per region. Re-appending the same
    region (a Spot-VM preemption re-run, or a resumed loop re-touching a banked
    region) is a NO-OP; the SAME variant id under a DIFFERENT region is a distinct
    record and is kept. The header is written exactly once.

    Returns the manifest path.
    """
    manifest_path = Path(manifest_path)
    records = [dict(r) for r in records]
    if not records:
        return manifest_path

    new = pd.DataFrame(records)
    # Preserve the declared column order; tolerate extra columns a caller added.
    ordered = [c for c in STAGE_A_COLUMNS if c in new.columns]
    ordered += [c for c in new.columns if c not in ordered]
    new = new[ordered]

    if not manifest_path.exists():
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        new.to_csv(manifest_path, sep="\t", index=False)
        return manifest_path

    existing = pd.read_csv(manifest_path, sep="\t",
                           dtype={"region_id": str, "variant_id": str})
    banked = set(
        zip(existing["region_id"].astype(str), existing["variant_id"].astype(str))
    )
    fresh = new[[
        (str(r), str(v)) not in banked
        for r, v in zip(new["region_id"], new["variant_id"])
    ]]
    if fresh.empty:
        return manifest_path  # already banked -> no duplicate rows
    with manifest_path.open("a") as fh:
        fresh.to_csv(fh, sep="\t", index=False, header=False)
    return manifest_path


def append_occlusion_rows(out_dir: "str | Path", region_id: str,
                          rows: Sequence[Sequence], *,
                          edges=None,
                          manifest_name: str = "occlusion_manifest.tsv") -> Path:
    """Driver-facing Stage-A hook: build + append this region's records.

    The one call ``run_native_ld_panel.process_region`` makes, right where the
    span filter's occluded ids/edges are known. Writes
    ``{out_dir}/occlusion_manifest.tsv`` (resume-safe). ``edges`` is accepted for
    call-site symmetry with the detector's return value but is not required —
    :func:`build_region_records` re-derives the attribution from ``rows`` so the
    manifest can never disagree with the filter about WHO occluded WHOM.
    """
    records = build_region_records(region_id, rows)
    return append_region_manifest(Path(out_dir) / manifest_name, records)


def aggregate_manifests(manifest_paths: Iterable["str | Path"],
                        out_path: "str | Path") -> Path:
    """Concatenate per-region manifests into the genome-wide occlusion catalog.

    This rollup IS the Angle-1/3 catalog seed: the full, auditable census of every
    variant the panel excluded for reference occlusion across all 276 regions.
    Absent/empty manifests are skipped (a region with zero occlusion writes no
    manifest); dedup on ``(region_id, variant_id)`` is re-applied so re-running the
    rollup is idempotent.
    """
    out_path = Path(out_path)
    frames = []
    for p in manifest_paths:
        p = Path(p)
        if not p.exists() or p.stat().st_size == 0:
            continue
        df = pd.read_csv(p, sep="\t", dtype={"region_id": str, "variant_id": str})
        if not df.empty:
            frames.append(df)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not frames:
        pd.DataFrame(columns=STAGE_A_COLUMNS).to_csv(out_path, sep="\t", index=False)
        return out_path

    catalog = pd.concat(frames, ignore_index=True)
    catalog = catalog.drop_duplicates(subset=_DEDUP_KEY, keep="first")
    catalog.to_csv(out_path, sep="\t", index=False)
    return out_path


def chain_sha256(chain_path: "str | Path") -> str:
    """SHA-256 of the liftover chain — provenance for the GRCh37 coordinates.

    Mirrors ``ld_npz_to_rds.R:96`` (``digest(file=chain_path, algo="sha256")``) so
    the manifest records the SAME chain identity the RDS export does. Chunked, so
    it never materializes the file in memory.
    """
    h = hashlib.sha256()
    with Path(chain_path).open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def add_grch37_positions(records: Iterable[dict],
                         *, chain_path: "str | Path") -> list[dict]:
    """Stage B: add ``pos_grch37`` to each record via the hg38->hg19 chain.

    Reuses the EXACT ``ld_npz_to_rds.R:167-183`` convention — pyliftover is 0-based,
    so ``convert_coordinate("chr"+chr, pos38 - 1)`` goes in and the result's
    coordinate ``+ 1`` comes out. Verified against the settled hinge-check anchors
    (5922716/5922718/5922724 -> 5982776/5982778/5982784).

    A variant that does NOT lift records ``pos_grch37 = None`` — an EXPLICIT
    missing value. It is never given the GRCh38 position as a fallback and never a
    nearest-neighbour guess: the panel<->sumstats join is (CHR,POS)-only on GRCh37,
    so a plausible-but-wrong coordinate would silently join the WRONG sumstats row.
    ``ld_npz_to_rds.R:184-190`` records failed liftovers as NA and drops them; this
    is the same discipline.

    Returns NEW dicts (the inputs are not mutated). pyliftover is imported here,
    not at module scope, so the in-perimeter Stage-A path never needs it.
    """
    from pyliftover import LiftOver  # lazy: Stage A must not require the chain

    lo = LiftOver(str(chain_path))
    out: list[dict] = []
    for rec in records:
        rec = dict(rec)
        pos38 = int(rec["pos_grch38"])
        contig = str(rec["chr"])
        if not contig.lower().startswith("chr"):
            contig = f"chr{contig}"
        hits = lo.convert_coordinate(contig, pos38 - 1)  # 0-based in
        rec["pos_grch37"] = (int(hits[0][1]) + 1) if hits else None  # +1 out
        out.append(rec)
    return out


def enrich_occlusion_manifest(manifest_path: "str | Path",
                              chain_path: "str | Path",
                              *, out_path: "str | Path | None" = None,
                              present_rate: dict | None = None) -> Path:
    """Stage B on a whole manifest file: add ``pos_grch37`` + ``chain_sha256``.

    Reads the Stage-A manifest, lifts every record to GRCh37, stamps the chain's
    SHA-256 on every row (so the build-37 coordinates are reproducible from the
    recorded chain identity), and declares the ``traits_present`` seam columns.

    ``present_rate`` is the 07c hand-off: ``{variant_id: {...}}`` supplying the
    trait-scan columns. When None, the seam columns are declared and left EMPTY —
    07c populates them. They are declared even when empty so the schema is stable
    and a downstream consumer can tell "not yet scanned" from "scanned, absent".

    Writes to ``out_path`` (default: in place) and returns that path.
    """
    manifest_path = Path(manifest_path)
    out_path = Path(out_path) if out_path is not None else manifest_path

    df = pd.read_csv(manifest_path, sep="\t", dtype={"region_id": str, "variant_id": str})
    if df.empty:
        df.to_csv(out_path, sep="\t", index=False)
        return out_path

    lifted = add_grch37_positions(df.to_dict("records"), chain_path=chain_path)
    out = pd.DataFrame(lifted)
    out["chain_sha256"] = chain_sha256(chain_path)

    for col in STAGE_B_TRAIT_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA
    if present_rate:
        for col in STAGE_B_TRAIT_COLUMNS:
            out[col] = [
                present_rate.get(vid, {}).get(col, pd.NA) for vid in out["variant_id"]
            ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, sep="\t", index=False)
    return out_path


#: Alias matching the plan's declared export name for the rollup.
build_occlusion_catalog = aggregate_manifests
