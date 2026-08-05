#!/usr/bin/env python3
"""MEASURE the pre-registered present-rate k/n for rs182965575 over the REAL AFR corpus.

WHY THIS SCRIPT EXISTS
----------------------
``present in 7 of 9 AFR sumstats`` is a PRE-REGISTERED number (osf.io/az52u,
amendment-update POSTED 2026-07-10T13:32:22Z, recorded ``ac4c990``). It is quoted in
four module docstrings and in ``m3_occlusion_lockstep.smk``. Before D-04b-01 was
fixed the code could only produce **6 of 9**, because ``bmi.AFR.PAGE.2019.GRCh37``
writes POS as a float string (``'5982778.0'``) in 100% of its 17,195,956 rows and
``int(pos)`` raised on every one of them — swallowed fail-open, scoring the whole
trait ABSENT (m3-04b-BLAST-RADIUS.md, D-04b-01 / HIGH-0).

A published number must be MEASURED, not asserted from memory. This script produces
the auditable artifact: ``measure_present_rate_kn.json`` beside it, recording k, n,
which traits carry the variant, and the full parse-health of the scan that produced
them.

SCOPE — THE 9 FILES, NOT 10
---------------------------
``data/processed/sumstats_harmonized/*.AFR*.tsv.bgz`` EXCLUDING
``asthma.AFR.grch38_backup.tsv.bgz``. That backup is build 38; scanning it would put
GRCh38 coordinates into a GRCh37 k/n. This is exactly the scope
``m3_occlusion_lockstep.smk:156-159`` defines for the production scan, restated here
so the measured number and the pipeline's number come from the same file set.

COST / PERIMETER
----------------
``$0``. NC State only. ALREADY-PUBLIC GRCh37 summary statistics, READ-ONLY, streamed
line-wise (no file is ever materialized). No AoU resource, no ``gs://`` object, no
perimeter contact, no spend.

RUNTIME: 9 files, ~130M rows, gzip-decompressed in Python -> expect 1-4 HOURS. Run it
detached with a generous cap and poll the log; do not kill it.

    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python \\
        .planning/quick/260804-rtc-.../measure_present_rate_kn.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from occlusion_present_rate_scan import scan_present_rate  # noqa: E402

#: rs182965575 — the settled hinge anchor. GRCh38 5,922,718 -> GRCh37 5,982,778.
VARIANT_RSID = "rs182965575"
VARIANT_CHR = 1
VARIANT_POS_GRCH37 = 5_982_778

HARMONIZED_DIR = PROJECT_ROOT / "data" / "processed" / "sumstats_harmonized"

#: The build-38 backup is NOT an analytic input — see the module docstring.
EXCLUDED_SUFFIX = ".grch38_backup.tsv.bgz"

OUT_JSON = Path(__file__).with_name("measure_present_rate_kn.json")


def scan_scope() -> list[Path]:
    """The 9 real public AFR GRCh37 harmonized sumstats, sorted and de-duplicated."""
    return sorted(
        p for p in HARMONIZED_DIR.glob("*.AFR*.tsv.bgz")
        if not p.name.endswith(EXCLUDED_SUFFIX)
    )


def main() -> int:
    paths = scan_scope()
    print(f"[measure] scan scope: {len(paths)} file(s)", flush=True)
    for p in paths:
        print(f"[measure]   {p.name}  ({p.stat().st_size / 1e6:.1f} MB)", flush=True)
    if len(paths) != 9:
        print(
            f"[measure] WARNING: expected the 9-file GRCh37 AFR scope, found "
            f"{len(paths)}. The published denominator is a FILE rate over exactly "
            "these 9; do not publish a k/n measured over a different scope.",
            file=sys.stderr, flush=True,
        )

    target = (VARIANT_CHR, VARIANT_POS_GRCH37)
    stats: dict = {}
    t0 = time.time()
    result = scan_present_rate([target], paths, stats=stats)
    elapsed = time.time() - t0

    rec = result[target]
    payload = {
        "variant": VARIANT_RSID,
        "chr": VARIANT_CHR,
        "pos_grch37": VARIANT_POS_GRCH37,
        "n_traits_present": rec["n_traits_present"],
        "n_traits_scanned": rec["n_traits_scanned"],
        "present_rate": rec["present_rate"],
        "traits_present": sorted(rec["traits_present"]),
        "stats": stats,
        "files": [str(p.relative_to(PROJECT_ROOT)) for p in paths],
        "elapsed_seconds": round(elapsed, 1),
        "note": (
            "n_traits_scanned is a FILE rate over the 9 GRCh37 AFR harmonized "
            "sumstats — the denominator the pre-registration (osf.io/az52u) "
            "publishes. It is NOT a distinct-trait rate: the scope resolves 9 files "
            "but only 8 distinct traits (stroke.AFR and "
            "stroke.AFR.GIGASTROKE.2022.GRCh37 both report 'stroke'). See LOW-1 — "
            "the double-count is REPORTED in stats.duplicate_traits, never silently "
            "folded into the denominator."
        ),
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"[measure] {VARIANT_RSID} present in {rec['n_traits_present']} of "
        f"{rec['n_traits_scanned']} AFR sumstats "
        f"({elapsed / 60:.1f} min) -> {OUT_JSON}",
        flush=True,
    )
    print(f"[measure] traits_present = {sorted(rec['traits_present'])}", flush=True)
    print(f"[measure] parse health   = {json.dumps({k: v for k, v in stats.items() if k != 'per_file'})}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
