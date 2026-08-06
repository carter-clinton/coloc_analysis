"""build_curated_m2_crosswalk.py — the curated Track-A <-> M2 region crosswalk (m3-04c).

``config/regions_curated.csv`` names 12 Track-A loci by SLUG (``FTO_16q12``,
``SH2B3_12q24``, ...). ``config/ld_regions.tsv`` names the 276 AoU LD windows by
SEQUENTIAL M2 ID (``m2_region_00067``, ``m2_region_00040__sub14``, ...). The
``AFR_aou`` chain head in ``config/pipeline.yaml`` templates on ``{region_id}``,
i.e. the M2 id — but ``Snakefile:45-62`` builds ``REGION_SAFE_TO_ID`` ONLY from
``config/regions_curated.csv``, where the ``region_id`` column IS the slug. That
map is therefore essentially the identity for curated slugs and can never yield
``m2_region_00067``: without this crosswalk ``resolve_ld_path`` asks for
``AFR_aou/FTO_16q12.rds``, a filename the producer never writes.

This module builds the missing translation and emits it as a reproducible config
artifact (``config/curated_to_m2_region_map.tsv``), the same convention as
``config/region_id_mapping.tsv``.

---------------------------------------------------------------------------
⚠ DO NOT SELECT ON ``start_grch37`` / ``end_grch37``
---------------------------------------------------------------------------
For a SPLIT parent those columns hold the PARENT's bounding box copied verbatim
into every subregion row (``build_ld_region_manifest.py:585-587,650-653``). All
18 subregions of ``m2_region_00040`` carry an identical ~89 Mb
``37,729,542-126,774,248`` span; only the ``*_grch38`` columns vary. A
"smallest containing span" rule over those columns is a perfect 18-WAY TIE whose
lexicographic tie-break returns ``m2_region_00040__sub00`` — whose REAL GRCh37
window is ``37,857,542-45,792,298``: ZERO bp of overlap with SH2B3
(``chr12:111,400,000-112,000,000``), ~66 Mb away. That specification would have
pointed the Track A ANCHOR locus at an unrelated window's LD panel, and a "12/12
independent reproduction" did not catch it because the reproduction
re-implemented the same comparison.

Selection therefore happens in ONE coordinate build: each candidate's GRCh38
WINDOW and CORE are lifted back to GRCh37 (the project's canonical analytic
plane, D-01, ``genome_build: GRCh37``) and compared physically against the
curated GRCh37 interval.

---------------------------------------------------------------------------
The selection rule
---------------------------------------------------------------------------
1. CONTAINED = candidates whose lifted window fully contains the curated
   interval. Rank them by, in order:
     (a) CORE overlap with the curated interval, DESC
     (b) window span, ASC
     (c) min distance from the curated interval to either window edge, DESC
     (d) ``region_id`` lexicographic, ASC
   -> ``status="contained"``.
2. else PARTIAL: the candidate with the largest lifted-window intersection,
   recording ``window_overlap_bp`` / ``overlap_frac``. A partial match is NEVER
   promoted to a containment.
3. else ``m2_region_id=""``, ``status="unmapped"``.

HONEST NOTE — on today's data only key (a) is ever load-bearing, and only for
``SH2B3_12q24``. Every other curated region has EXACTLY ONE containing
candidate, so (b)/(c)/(d) are determinism backstops, not active discriminators.
Stated plainly here rather than implying the ladder does more work than it does.

---------------------------------------------------------------------------
The ``__sub14`` vs ``__sub15`` decision — a SCIENTIFIC choice, surfaced
---------------------------------------------------------------------------
Both windows FULLY contain SH2B3, so containment cannot decide. Core overlap can::

    __sub14  core GRCh37 106,944,368-111,923,169  ->  523,169 bp of 600,000 (87.2%)
    __sub15  core GRCh37 111,923,169-116,857,945  ->   76,831 bp of 600,000 (12.8%)

They partition the locus EXACTLY at the shared core boundary GRCh37 111,923,169
(GRCh38 111,485,365); SH2B3 STRADDLES it. RULE: maximize CORE overlap ->
``__sub14``. Why core overlap is the right primary key:

1. It matches the manifest's OWN semantics. ``core_*`` / ``subregion_index``
   define which subregion OWNS which variants, and ``stitch_subregions_to_rds.R``
   de-dups on core ownership. Picking the subregion whose core owns most of the
   locus picks the panel the pipeline itself treats as authoritative for those
   variants.
2. The independent secondary criterion AGREES (corroboration, not coincidence):
   min distance from the locus to a window edge is 2,923,170 bp for ``__sub14``
   vs 2,520,858 bp for ``__sub15``, so ``__sub14`` also truncates LD less.
3. Window span cannot decide: 10,978,802 vs 10,978,803 bp.

⚠ DISCLOSED LIMITATION — NEITHER core fully contains SH2B3. 12.8% of the locus
lives in ``__sub15``'s core, so ``__sub14``'s panel covers those variants only
through its BUFFER, where a stitched parent's core-ownership de-dup would have
assigned them elsewhere. This is a real property of using a subregion panel for
a locus that straddles a core boundary, and it is why the region-1 gate must
check the REALIZED variant overlap/coverage (``run_susie_rss.R:184``) rather
than assume the bp arithmetic carries over.

---------------------------------------------------------------------------
RUNTIME DEPENDENCY — ``pyliftover``
---------------------------------------------------------------------------
The lift needs ``pyliftover`` and ``data/external/liftover/hg38ToHg19.over.chain.gz``
— the ONLY chain the repo ships. There is NO hg19->hg38 chain; do not assume one.

``pyliftover`` is DECLARED in ``envs/m3-r-ld.yml`` (the tracked NCSU-side M3 env,
which now names this module as a consumer) and in ``envs/m3-aou-dev.yml``. It is
also importable from the untracked local ``smoke_dev`` interpreter that runs the
test suite; that interpreter has NO env yml, so a rebuild of it would otherwise
break this builder with no documented cause. Two mitigations: the declaration
above, and a LAZY import that raises a named, actionable ``ImportError``.

The import is lazy for a second reason: ``src/snakemake/rules/finemap.smk``
imports :func:`load_curated_to_m2` at module scope, and that path must never
require ``pyliftover`` — otherwise ``snakemake --list`` would fail in any env
lacking it.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

__all__ = [
    "CROSSWALK_COLUMNS",
    "build_curated_m2_crosswalk",
    "load_curated_to_m2",
    "overlap_bp",
    "select_m2_candidate",
]

CROSSWALK_COLUMNS = [
    "region_safe",
    "curated_region_id",
    "chr",
    "curated_start_grch37",
    "curated_end_grch37",
    "m2_region_id",
    "m2_window_start_grch37",
    "m2_window_end_grch37",
    "m2_core_start_grch37",
    "m2_core_end_grch37",
    "window_overlap_bp",
    "core_overlap_bp",
    "overlap_frac",
    "n_containing_candidates",
    "status",
]

DEFAULT_REGIONS_CURATED = "config/regions_curated.csv"
DEFAULT_LD_REGIONS = "config/ld_regions.tsv"
DEFAULT_CHAIN = "data/external/liftover/hg38ToHg19.over.chain.gz"
DEFAULT_OUT_TSV = "config/curated_to_m2_region_map.tsv"

#: Only AFR rows are read: all 276 unique region ids appear under AFR, and the
#: EUR half of the manifest describes the retired AoU-EUR panel.
MANIFEST_ANCESTRY = "AFR"


# ---------------------------------------------------------------------------
# small pure helpers
# ---------------------------------------------------------------------------
def _chrom_match_key(value: str) -> str:
    """Normalize a contig for comparison.

    Strips a ``chr`` prefix on BOTH sides of every comparison. ``run_native_ld_panel.py``
    grew the same helper because a literal ``==`` against a ``chr``-prefixed contig
    silently matched zero rows for 17 hours and banked 0/276 regions.
    """
    return str(value).strip().replace("chr", "").replace("CHR", "")


def overlap_bp(a_start: int, a_end: int, b_start: int, b_end: int) -> int:
    """Half-open intersection length in bp (0 when disjoint)."""
    return max(0, min(a_end, b_end) - max(a_start, b_start))


def _safe_slug(region_id: str) -> str:
    """Mirror ``Snakefile:49``'s filesystem-safe slug construction."""
    return region_id.replace(".", "_").replace("/", "_")


# ---------------------------------------------------------------------------
# the selection rule -- pure, and tested SYNTHETICALLY (T1.2/T1.3/T1.4)
# ---------------------------------------------------------------------------
def select_m2_candidate(curated_start, curated_end, candidates) -> dict:
    """Pick the M2 candidate for one curated interval.

    Args:
        curated_start / curated_end: the curated interval, GRCh37.
        candidates: iterable of dicts with ``region_id``, ``window_start``,
            ``window_end``, ``core_start``, ``core_end`` — all ALREADY LIFTED to
            GRCh37 and already restricted to the curated interval's chromosome.

    Returns:
        dict carrying the ``m2_*`` / overlap / ``status`` fields of one crosswalk
        row (the caller supplies the curated-side fields).

    Separated from the I/O so the RANKING can be exercised on synthetic
    geometry: the defect this module exists to prevent was a ranking defect, and
    a ranking that can only be tested through the production manifest is a
    ranking nobody can probe.
    """
    curated_start = int(curated_start)
    curated_end = int(curated_end)
    curated_span = curated_end - curated_start

    cands = list(candidates)
    contained = [
        c
        for c in cands
        if int(c["window_start"]) <= curated_start and int(c["window_end"]) >= curated_end
    ]

    def _row(cand, status, n_containing):
        w0, w1 = int(cand["window_start"]), int(cand["window_end"])
        c0, c1 = int(cand["core_start"]), int(cand["core_end"])
        win_ov = overlap_bp(w0, w1, curated_start, curated_end)
        return {
            "m2_region_id": cand["region_id"],
            "m2_window_start_grch37": w0,
            "m2_window_end_grch37": w1,
            "m2_core_start_grch37": c0,
            "m2_core_end_grch37": c1,
            "window_overlap_bp": win_ov,
            "core_overlap_bp": overlap_bp(c0, c1, curated_start, curated_end),
            "overlap_frac": (win_ov / curated_span) if curated_span else 0.0,
            "n_containing_candidates": n_containing,
            "status": status,
        }

    if contained:
        def _rank(cand):
            w0, w1 = int(cand["window_start"]), int(cand["window_end"])
            core_ov = overlap_bp(
                int(cand["core_start"]), int(cand["core_end"]), curated_start, curated_end
            )
            edge_dist = min(curated_start - w0, w1 - curated_end)
            return (
                -core_ov,          # (a) CORE overlap, DESC -- the PRIMARY key
                w1 - w0,           # (b) window span, ASC
                -edge_dist,        # (c) distance to the nearest window edge, DESC
                str(cand["region_id"]),  # (d) determinism backstop
            )

        return _row(min(contained, key=_rank), "contained", len(contained))

    overlapping = [
        c
        for c in cands
        if overlap_bp(
            int(c["window_start"]), int(c["window_end"]), curated_start, curated_end
        )
        > 0
    ]
    if overlapping:
        def _rank_partial(cand):
            return (
                -overlap_bp(
                    int(cand["window_start"]),
                    int(cand["window_end"]),
                    curated_start,
                    curated_end,
                ),
                int(cand["window_end"]) - int(cand["window_start"]),
                str(cand["region_id"]),
            )

        return _row(min(overlapping, key=_rank_partial), "partial", 0)

    return {
        "m2_region_id": "",
        "m2_window_start_grch37": "",
        "m2_window_end_grch37": "",
        "m2_core_start_grch37": "",
        "m2_core_end_grch37": "",
        "window_overlap_bp": 0,
        "core_overlap_bp": 0,
        "overlap_frac": 0.0,
        "n_containing_candidates": 0,
        "status": "unmapped",
    }


# ---------------------------------------------------------------------------
# liftover
# ---------------------------------------------------------------------------
def _open_lifter(chain_path):
    """LAZY ``pyliftover`` import with a named, actionable failure."""
    try:
        from pyliftover import LiftOver
    except ImportError as exc:  # pragma: no cover - env-shape guard
        raise ImportError(
            "build_curated_m2_crosswalk needs `pyliftover` to lift the M2 GRCh38 "
            "windows back to the project's canonical GRCh37 plane. It is DECLARED in "
            "envs/m3-r-ld.yml (pip:) and envs/m3-aou-dev.yml; install with "
            "`pip install pyliftover`. This import is deliberately lazy so that "
            "finemap.smk's module-scope load_curated_to_m2() import -- and therefore "
            "`snakemake --list` -- never depends on it."
        ) from exc

    chain_path = Path(chain_path)
    if not chain_path.exists():
        raise FileNotFoundError(
            f"liftover chain not found at {chain_path}. The repo ships EXACTLY ONE "
            "chain (hg38ToHg19.over.chain.gz); there is no hg19->hg38 chain."
        )
    return LiftOver(str(chain_path))


def _lift_point(lifter, chrom: str, pos: int):
    """Return the first ``(chrom, pos, strand, score)`` hit, or ``None``."""
    hits = lifter.convert_coordinate(f"chr{_chrom_match_key(chrom)}", int(pos))
    if not hits:
        return None
    return hits[0]


def _lift_interval(lifter, chrom, start, end, stats, kind):
    """Lift a GRCh38 interval to GRCh37, normalizing with ``min``/``max``.

    Counts, rather than silently absorbs, the three degenerate outcomes. All
    three are DEAD on today's data for the WINDOW lift, which is exactly why they
    must be counted: a future manifest regeneration would otherwise get no signal.
    """
    a = _lift_point(lifter, chrom, start)
    b = _lift_point(lifter, chrom, end)
    if a is None or b is None:
        return None
    if a[2] != b[2]:
        stats[f"n_strand_inconsistent_{kind}"] += 1
    p, q = int(a[1]), int(b[1])
    if p > q:
        stats[f"n_inverted_{kind}"] += 1
    return (min(p, q), max(p, q))


# ---------------------------------------------------------------------------
# the builder
# ---------------------------------------------------------------------------
def build_curated_m2_crosswalk(
    regions_curated_csv=DEFAULT_REGIONS_CURATED,
    ld_regions_tsv=DEFAULT_LD_REGIONS,
    chain_path=DEFAULT_CHAIN,
    out_tsv=DEFAULT_OUT_TSV,
) -> dict:
    """Build the crosswalk TSV. Returns a stats dict (also echoed to stderr)."""
    regions_curated_csv = Path(regions_curated_csv)
    ld_regions_tsv = Path(ld_regions_tsv)
    out_tsv = Path(out_tsv)

    stats = {
        "n_curated": 0,
        "n_afr_manifest_rows": 0,
        "n_contained": 0,
        "n_partial": 0,
        "n_unmapped": 0,
        # (a) WINDOW lift failures -- excluded from candidacy, never silently dropped
        "n_window_lift_failures": 0,
        # (a') CORE lift failures where the WINDOW lifted fine. core_overlap_bp is the
        # PRIMARY sort key, so a silent window-substitution would distort the ranking
        # that picks __sub14. Fall back to the window bounds, but RECORD it.
        "n_core_lift_failures_window_ok": 0,
        # (b) intervals returned INVERTED before min/max normalization
        "n_inverted_window": 0,
        "n_inverted_core": 0,
        # (c) STRAND-INCONSISTENT lifts (start and end land on opposite strands)
        "n_strand_inconsistent_window": 0,
        "n_strand_inconsistent_core": 0,
    }

    lifter = _open_lifter(chain_path)

    # --- candidates: the AFR half of the M2 manifest, lifted to GRCh37 --------
    candidates_by_chrom: dict[str, list[dict]] = {}
    with ld_regions_tsv.open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["ancestry"] != MANIFEST_ANCESTRY:
                continue
            stats["n_afr_manifest_rows"] += 1
            chrom = _chrom_match_key(row["chr"])
            window = _lift_interval(
                lifter,
                chrom,
                row["window_start_grch38"],
                row["window_end_grch38"],
                stats,
                "window",
            )
            if window is None:
                stats["n_window_lift_failures"] += 1
                print(
                    f"[build_curated_m2_crosswalk] WARN window liftover FAILED, "
                    f"candidate excluded: {row['region_id']}",
                    file=sys.stderr,
                )
                continue
            core = _lift_interval(
                lifter,
                chrom,
                row["core_start_grch38"],
                row["core_end_grch38"],
                stats,
                "core",
            )
            if core is None:
                stats["n_core_lift_failures_window_ok"] += 1
                print(
                    f"[build_curated_m2_crosswalk] WARN core liftover FAILED "
                    f"(window OK), falling back to window bounds for the PRIMARY "
                    f"sort key: {row['region_id']}",
                    file=sys.stderr,
                )
                core = window
            candidates_by_chrom.setdefault(chrom, []).append(
                {
                    "region_id": row["region_id"],
                    "window_start": window[0],
                    "window_end": window[1],
                    "core_start": core[0],
                    "core_end": core[1],
                }
            )

    # --- one row per curated region ------------------------------------------
    out_rows = []
    with regions_curated_csv.open(newline="") as fh:
        for row in csv.DictReader(fh):
            stats["n_curated"] += 1
            curated_id = row["region_id"]
            chrom = _chrom_match_key(row["chr"])
            start = int(float(row["start"]))
            end = int(float(row["end"]))

            picked = select_m2_candidate(
                start, end, candidates_by_chrom.get(chrom, [])
            )
            stats[f"n_{picked['status']}"] += 1

            out_rows.append(
                {
                    "region_safe": _safe_slug(curated_id),
                    "curated_region_id": curated_id,
                    "chr": chrom,
                    "curated_start_grch37": start,
                    "curated_end_grch37": end,
                    "m2_region_id": picked["m2_region_id"],
                    "m2_window_start_grch37": picked["m2_window_start_grch37"],
                    "m2_window_end_grch37": picked["m2_window_end_grch37"],
                    "m2_core_start_grch37": picked["m2_core_start_grch37"],
                    "m2_core_end_grch37": picked["m2_core_end_grch37"],
                    "window_overlap_bp": picked["window_overlap_bp"],
                    "core_overlap_bp": picked["core_overlap_bp"],
                    # fixed precision -> byte-identical rebuilds (T1.9)
                    "overlap_frac": f"{picked['overlap_frac']:.6f}",
                    "n_containing_candidates": picked["n_containing_candidates"],
                    "status": picked["status"],
                }
            )

    out_rows.sort(key=lambda r: r["region_safe"])

    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with out_tsv.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=CROSSWALK_COLUMNS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(out_rows)

    for key, value in stats.items():
        print(f"[build_curated_m2_crosswalk] {key}={value}", file=sys.stderr)
    print(f"[build_curated_m2_crosswalk] wrote {out_tsv}", file=sys.stderr)
    return stats


# ---------------------------------------------------------------------------
# the consumer-side loader (imported at module scope by finemap.smk)
# ---------------------------------------------------------------------------
#: The ONLY statuses ``load_curated_to_m2`` will hand to ``resolve_ld_path``.
#:
#: An ALLOW-LIST, not a deny-list (m3-04c blast radius, FINDING M). Before
#: quick-260806-b77 this was ``if status == "unmapped": continue`` -- a deny-list
#: of ONE -- so a ``partial`` row (a candidate whose lifted window merely
#: INTERSECTS the curated interval, ``overlap_frac`` possibly 0.30) would be
#: handed over exactly like a ``contained`` one, contradicting this module's own
#: promise: "A partial match is NEVER promoted to a containment" (see the
#: selection rule in the module docstring, and ``select_m2_candidate``, where
#: ``"partial"`` is a really-emitted status).
_LOADABLE_STATUSES = ("contained",)


def load_curated_to_m2(path=DEFAULT_OUT_TSV) -> dict:
    """Load ``region_safe -> m2_region_id`` for the CONTAINED curated regions only.

    ONLY rows whose ``status`` is in :data:`_LOADABLE_STATUSES` (``contained``)
    are returned. Rows whose ``status`` is ``unmapped`` — or whose
    ``m2_region_id`` is empty — are SKIPPED SILENTLY (today's behaviour, and the
    byte-identity ``260805-23d`` relies on). **Any OTHER status is refused and
    named on stderr**, because a silent refusal is how finding M would have come
    back.

    ⚠ A ``partial`` ROW IS NOT PROMOTED. ``select_m2_candidate`` emits
    ``status="partial"`` when no candidate CONTAINS the curated interval and it
    falls back to the largest intersection, recording ``window_overlap_bp`` /
    ``overlap_frac``. Handing such a row to ``resolve_ld_path`` would fine-map a
    locus on a panel that covers only PART of it, silently — the builder's own
    promise ("A partial match is NEVER promoted to a containment") enforced at
    the point of consumption rather than only at the point of construction.

    A refused row falls through to ``REGION_SAFE_TO_ID`` at the call site
    exactly as an ``unmapped`` one does — ``dict.get(region,
    REGION_SAFE_TO_ID[region])`` — which is **the fail-safe direction for this
    caller**: the DAG keeps today's legacy 1kG path instead of silently
    fine-mapping on a panel that covers only part of the locus.
    (``[[feedback_failsafe_default_is_caller_relative]]``.)

    A MISSING file returns ``{}`` (not an error): the DAG must still build on a
    fresh clone before the crosswalk has been generated. No ``pyliftover`` is
    needed on this path.
    """
    path = Path(path)
    if not path.exists():
        return {}
    mapping = {}
    refused = []
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            status = row.get("status")
            if status in _LOADABLE_STATUSES:
                m2_id = (row.get("m2_region_id") or "").strip()
                if not m2_id:
                    continue
                mapping[row["region_safe"]] = m2_id
                continue
            if status == "unmapped":
                # a DECISION was recorded: no candidate overlapped at all.
                continue
            refused.append((row.get("region_safe", ""), status))
    if refused:
        detail = "; ".join(f"{rs} (status={st!r})" for rs, st in sorted(refused))
        print(
            f"[build_curated_m2_crosswalk] WARN load_curated_to_m2 REFUSED "
            f"{len(refused)} crosswalk row(s) whose status is not "
            f"{list(_LOADABLE_STATUSES)}: {detail}. A partial match is NEVER "
            f"promoted to a containment, so these regions fall through to the "
            f"legacy region-safe id and keep today's LD panel.",
            file=sys.stderr,
        )
    return mapping


# ---------------------------------------------------------------------------
# the DRIFT / COVERAGE readers (m3-04c blast radius, FINDING L)
# ---------------------------------------------------------------------------
def crosswalk_covered_region_safes(path=DEFAULT_OUT_TSV) -> set:
    """Every ``region_safe`` the crosswalk has a ROW for, mapped or not.

    Distinct from :func:`load_curated_to_m2`, which returns only the USABLE
    rows. An ``unmapped`` row is COVERAGE — a decision was recorded for that
    region. An ABSENT row is DRIFT: the artifact predates the region.

    FINDING L: ``finemap.smk``'s WARN fired only on a FULLY EMPTY dict, so a
    13th curated region added without rebuilding the crosswalk was silently
    legacy-routed — the AoU AFR panel simply stayed unreachable for it, with no
    message anywhere. Returns ``set()`` when the artifact is absent so a fresh
    clone still builds a DAG.
    """
    path = Path(path)
    if not path.exists():
        return set()
    with path.open(newline="") as fh:
        return {
            row["region_safe"]
            for row in csv.DictReader(fh, delimiter="\t")
            if row.get("region_safe")
        }


def crosswalk_missing_region_safes(
    regions_curated_csv=DEFAULT_REGIONS_CURATED, path=DEFAULT_OUT_TSV
) -> list:
    """Curated slugs with NO crosswalk row at all, sorted. Empty == in sync.

    Reuses the same ``region_id`` column and the same :func:`_safe_slug` the
    builder itself writes into the ``region_safe`` column, so the comparison
    cannot drift from the artifact's own key space.

    When the CROSSWALK is absent every curated slug is returned (it is entirely
    uncovered). When the CURATED CSV is absent ``[]`` is returned: the caller is
    ``finemap.smk`` at DAG-parse time and the fail-safe direction there is not
    to manufacture a warning out of a missing input it does not own.
    """
    curated_path = Path(regions_curated_csv)
    if not curated_path.exists():
        return []
    covered = crosswalk_covered_region_safes(path)
    with curated_path.open(newline="") as fh:
        curated = {_safe_slug(row["region_id"]) for row in csv.DictReader(fh)}
    return sorted(curated - covered)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the curated Track-A <-> M2 region crosswalk by PHYSICAL overlap "
            "in GRCh37 (M2 GRCh38 windows lifted back via hg38ToHg19)."
        )
    )
    parser.add_argument("--regions-curated", default=DEFAULT_REGIONS_CURATED)
    parser.add_argument("--ld-regions", default=DEFAULT_LD_REGIONS)
    parser.add_argument("--chain", default=DEFAULT_CHAIN)
    parser.add_argument("--out", default=DEFAULT_OUT_TSV)
    args = parser.parse_args(argv)

    build_curated_m2_crosswalk(
        regions_curated_csv=args.regions_curated,
        ld_regions_tsv=args.ld_regions,
        chain_path=args.chain,
        out_tsv=args.out,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
