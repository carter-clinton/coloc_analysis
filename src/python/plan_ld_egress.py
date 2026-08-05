#!/usr/bin/env python3
"""plan_ld_egress.py — m3-04c Task 2: the AFR LD egress REQUEST plan.

A THIN CLI over the SHIPPED bundler ``ld_egress_bundle.plan_egress_bundles``
(``ade6066``, m3-02d). It contains no grouping or bin-packing logic of its own,
and ``src/python/validate_bundle_sizes.py`` — which the stale m3-04 plan asked
for — is deliberately NOT written: its function already exists here.

WHAT A "BUNDLE" IS (m3-04c egress-unit redefinition; see
``.planning/amendments/m3-egress-and-validation-protocol-addendum.md``).
The producer ``src/python/run_native_ld_panel.py`` uploads per-region ``.npz``
DIRECTLY to ``gs://<bucket>/ld/AFR_aou/{region_id}.npz`` (``:922-938``). No
stage exists at which a "chr1 AFR bundle" OBJECT exists, so nothing can be
sized or split on the bucket side. A bundle here is a REQUEST-LEVEL GROUPING
OF OBJECT URIs: at most 22 AFR chromosome groups, plus within-chromosome size
splits, each transferred with one ``gsutil -m cp``. AFR only — EUR is the
public UKBB 337k panel (``EUR_ukbb_pub``), built on NC State for ``$0``.

THE CAP IS NOT A HARD LIMIT. ``ld_egress_bundle.EGRESS_CAP_GB = 50`` is a
CONSERVATIVE PROJECT WORKING CEILING, NOT a documented hard AoU API limit
(``ld_egress_bundle.py:9-15``). AoU's real mechanism is an alert threshold plus
manual relaxation at egress-request time; the real number is confirmed on the
first export. ``--cap-gb`` exists so that confirmation can be applied without a
code change.

INPUT. ``--sizes-tsv`` with columns ``region_id``, ``chr``, ``bytes``. Building
that capture is a Task 3 (in-perimeter) step, not this module's job. The
recipe, for the record — a `gsutil ls -l` listing carries a size and a URI but
NO chromosome, so it is joined against the region manifest::

    gsutil ls -l "gs://<bucket>/ld/AFR_aou/*.npz" > /tmp/afr_npz_ls.txt
    awk 'NF>=3 && $3 ~ /\\.npz$/ {n=split($3,p,"/"); id=p[n]; sub(/\\.npz$/,"",id);
         print id"\\t"$1}' /tmp/afr_npz_ls.txt | sort > /tmp/afr_sizes_raw.tsv
    awk -F'\\t' 'NR>1 && $7=="AFR" {print $1"\\t"$2}' config/ld_regions.tsv \\
        | sort -u > /tmp/afr_region_chr.tsv
    { printf 'region_id\\tchr\\tbytes\\n';
      join -t $'\\t' /tmp/afr_sizes_raw.tsv /tmp/afr_region_chr.tsv \\
        | awk -F'\\t' '{print $1"\\t"$3"\\t"$2}'; } > config/afr_npz_sizes.tsv

OUTPUT. One row per bundle (``bundle_id, chr, n_cells, total_bytes, total_gb,
region_ids``) plus a trailing ``#``-prefixed summary carrying
``n_bundles_over_cap`` and ``chromosomes_split``, so a reviewer sees a split or
an un-splittable oversize cell without re-deriving it.

REQ-AOU-LD-EGRESS: only summary variant×variant LD + allele frequency cross the
egress boundary; this planner only ever reads a size table.
REQ-PATH-PARAMETERIZATION: no hardcoded absolute HPC paths.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

# Reuse the SHIPPED helper — do NOT re-implement grouping or splitting.
import ld_egress_bundle  # noqa: E402
from ld_egress_bundle import (  # noqa: E402
    EGRESS_CAP_GB,
    chromosomes_split,
    n_bundles_over_cap,
    plan_egress_bundles,
)

_GB = 1_000_000_000

DEFAULT_OUT = Path(".planning/amendments/m3_egress_plan_AFR.tsv")

REQUIRED_COLUMNS = ("region_id", "chr", "bytes")
PLAN_COLUMNS = (
    "bundle_id",
    "chr",
    "n_cells",
    "total_bytes",
    "total_gb",
    "region_ids",
)


def read_sizes_tsv(path: Path) -> list[dict]:
    """Read the per-region size table into ``plan_egress_bundles`` cell dicts."""
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                f"{path}: missing required column(s) {missing}; expected "
                f"{list(REQUIRED_COLUMNS)}. A `gsutil ls -l` capture carries a "
                f"size and a URI but NO chromosome — join it against "
                f"config/ld_regions.tsv (ancestry == 'AFR') to add `chr`; the "
                f"recipe is in this module's docstring."
            )
        cells = []
        for row in reader:
            region_id = (row.get("region_id") or "").strip()
            if not region_id:
                continue
            cells.append({
                "region_id": region_id,
                "chr": (row.get("chr") or "").strip(),
                "bytes": int(float(row["bytes"])),
            })
    if not cells:
        raise ValueError(f"{path}: no data rows")
    return cells


def write_plan_tsv(bundles: list[dict], out_path: Path, cap_bytes: int) -> Path:
    """Emit the request plan plus its trailing ``#``-prefixed summary."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    over_cap = n_bundles_over_cap(bundles, cap_bytes=cap_bytes)
    split_chroms = sorted(chromosomes_split(bundles))
    total_bytes = sum(b["total_bytes"] for b in bundles)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(PLAN_COLUMNS)
        for b in bundles:
            writer.writerow([
                b["bundle_id"],
                b["chr"],
                b["n_cells"],
                b["total_bytes"],
                f"{ld_egress_bundle.bundle_gib(b):.3f}",
                ",".join(b["region_ids"]),
            ])
        fh.write(
            f"# AFR-only egress REQUEST plan (m3-04c Task 2). A bundle is a\n"
            f"# REQUEST-LEVEL grouping of per-region .npz object URIs, not an\n"
            f"# object: the producer writes .npz DIRECTLY to\n"
            f"# gs://<bucket>/ld/AFR_aou/{{region_id}}.npz.\n"
            f"# n_bundles={len(bundles)}\n"
            f"# n_cells={sum(b['n_cells'] for b in bundles)}\n"
            f"# total_gb={total_bytes / _GB:.3f}\n"
            f"# cap_gb={cap_bytes / _GB:g} "
            f"(CONSERVATIVE PROJECT WORKING CEILING, not a hard AoU API limit)\n"
            f"# n_bundles_over_cap={over_cap}\n"
            f"# chromosomes_split={','.join(split_chroms) if split_chroms else 'none'}\n"
        )
    return out_path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Plan the AFR LD egress REQUESTS from a per-region .npz size table, "
            "using the shipped ld_egress_bundle.plan_egress_bundles helper."
        )
    )
    p.add_argument("--sizes-tsv", required=True,
                   help="TSV with columns region_id, chr, bytes")
    p.add_argument("--cap-gb", type=float, default=float(EGRESS_CAP_GB),
                   help=(f"per-request working ceiling in decimal GB "
                         f"(default {EGRESS_CAP_GB}; a project working ceiling, "
                         f"NOT a hard AoU API limit)"))
    p.add_argument("--out", default=str(DEFAULT_OUT),
                   help=f"output plan TSV (default {DEFAULT_OUT})")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cap_bytes = int(round(args.cap_gb * _GB))
    cells = read_sizes_tsv(Path(args.sizes_tsv))
    bundles = plan_egress_bundles(cells, cap_bytes=cap_bytes)
    out_path = write_plan_tsv(bundles, Path(args.out), cap_bytes)
    split_chroms = sorted(chromosomes_split(bundles))
    print(
        f"[plan_ld_egress] {len(cells)} regions -> {len(bundles)} egress "
        f"request(s) at cap {args.cap_gb:g} GB; "
        f"over_cap={n_bundles_over_cap(bundles, cap_bytes=cap_bytes)}; "
        f"split={','.join(split_chroms) if split_chroms else 'none'}; "
        f"wrote {out_path}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
