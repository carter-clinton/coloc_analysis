#!/usr/bin/env python3
"""select_ld_regions_dev.py — M3 Wave 0 dev-subset selector.

Implements RESEARCH.md Q11 overlap design verbatim: 10-region dev subset =
3 EUR-Track-A overlap regions (FTO_16q12 / SH2B3_12q24 / APOE_19q13 — emit
BOTH AFR + EUR) + 5 AFR-known regions (FTO/SORT1/SH2B3/APOE/LDLR — AFR only,
where FTO/SH2B3/APOE overlap with the EUR slot makes the cross-ancestry
comparator extra-sharp) + 2 HLA-stress regions (chr6 HLA classical + chr8
8p23 inversion neighborhood — AFR only).

Total = 3 EUR + 5 AFR + 2 AFR-stress = **10 rows** (NOT 8 + 5 + 2; the 3 EUR
slots are the EUR halves of three of the five AFR-known slots — same regions,
emitted twice per D-M3-02 manifest semantics).

D-M3-04 anchor: spec default. RESEARCH Q11 picks specific m2_region_IDs.

The 10-row dev subset is consumed by:
* AoU dev-fire driver (Wave 2): drives the 4-check validation gate.
* Pytest harness: the test set runs the full Hail pipeline against the
  synthetic MT for these 10 rows.

This script is purely deterministic — no randomness, no external API calls.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# RESEARCH Q11 verbatim: 5 AFR-known regions
AFR_KNOWN_REGIONS = (
    "m2_region_00067",  # FTO 16q12 (BMI AFR PAGE 2019; spec §9.3 canonical Check 3 region)
    "m2_region_00006",  # SORT1 1p13 family (lipids AFR GLGC 2021)
    "m2_region_00040",  # SH2B3 12q24 (lipids AFR GLGC 2021)
    "m2_region_00083",  # APOE 19q13 (lipids AFR GLGC 2021)
    "m2_region_00027",  # LDLR 11p13 (lipids; classic)
)

# 3 EUR-Track-A overlap regions (Track A has EUR_1kg .rds for FTO_16q12,
# SH2B3_12q24, APOE_19q13 — see data/processed/ld_reference/EUR/*.rds)
EUR_OVERLAP_REGIONS = (
    "m2_region_00067",  # FTO_16q12 (Track A)
    "m2_region_00040",  # SH2B3_12q24 (Track A)
    "m2_region_00083",  # APOE_19q13 (Track A)
)

# 2 HLA-stress regions (RESEARCH Q11): chr6 HLA classical (28-34 Mb GRCh38
# overlap) + chr8 8p23 (7-13 Mb GRCh38 overlap). We pick by interval overlap
# rather than start-position equality because M2 union regions are wide.
HLA_STRESS_TARGETS = (
    {"chr": "6", "min_b38": 25_000_000, "max_b38": 40_000_000, "label": "HLA_6p21_classical"},
    {"chr": "8", "min_b38": 5_000_000, "max_b38": 15_000_000, "label": "8p23_inversion"},
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, type=Path,
                   help="322-row config/ld_regions.tsv from build_ld_region_manifest.py")
    p.add_argument("--out", required=True, type=Path,
                   help="Output 10-row TSV (config/ld_regions_dev.tsv)")
    return p.parse_args(argv)


def select_dev_rows(manifest_df: pd.DataFrame) -> pd.DataFrame:
    """Apply RESEARCH Q11 overlap design.

    Step 1: emit AFR-only rows for all 5 AFR-known regions.
    Step 2: emit EUR-only rows for the 3 overlap regions (FTO/SH2B3/APOE).
    Step 3: pick 1 HLA-stress region per target (chr6 HLA / chr8 8p23) and
            emit AFR-only rows. We deterministically pick the first manifest
            row whose interval overlaps the target window.
    """
    # Coerce chr to string for safe comparison (manifest emits int-like strings)
    manifest_df = manifest_df.copy()
    manifest_df["chr"] = manifest_df["chr"].astype(str)

    # Step 1: AFR-only rows for all 5 AFR-known
    afr_known = manifest_df[
        (manifest_df["region_id"].isin(AFR_KNOWN_REGIONS)) &
        (manifest_df["ancestry"] == "AFR")
    ].copy()

    # Step 2: EUR-only rows for the 3 overlap regions
    eur_overlap = manifest_df[
        (manifest_df["region_id"].isin(EUR_OVERLAP_REGIONS)) &
        (manifest_df["ancestry"] == "EUR")
    ].copy()

    # Step 3: HLA-stress rows
    stress_picks: list[pd.DataFrame] = []
    for target in HLA_STRESS_TARGETS:
        candidates = manifest_df[
            (manifest_df["chr"] == target["chr"]) &
            (manifest_df["ancestry"] == "AFR") &
            # Interval overlap: region.start <= target.max_b38 AND region.end >= target.min_b38
            (manifest_df["start_grch38"].astype(int) <= target["max_b38"]) &
            (manifest_df["end_grch38"].astype(int) >= target["min_b38"])
        ].copy()
        if candidates.empty:
            print(f"WARN: no manifest region overlaps stress target {target['label']}",
                  file=sys.stderr)
            continue
        # Deterministic: pick first row (sorted by region_id ascending)
        candidates = candidates.sort_values("region_id")
        first = candidates.head(1)
        stress_picks.append(first)

    parts = [afr_known, eur_overlap]
    if stress_picks:
        parts.extend(stress_picks)
    dev_df = pd.concat(parts, axis=0, ignore_index=True)

    # Drop dups (an AFR-known + HLA-stress could collide — unlikely here, but guard)
    dev_df = dev_df.drop_duplicates(subset=["region_id", "ancestry"], keep="first")

    # Sort: AFR rows first by region_id, then EUR rows
    dev_df["_sort_key"] = dev_df["ancestry"].map({"AFR": 0, "EUR": 1}).fillna(2)
    dev_df = dev_df.sort_values(["_sort_key", "region_id"]).drop(columns=["_sort_key"])
    dev_df = dev_df.reset_index(drop=True)
    return dev_df


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest_df = pd.read_csv(args.manifest, sep="\t")
    dev_df = select_dev_rows(manifest_df)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    dev_df.to_csv(args.out, sep="\t", index=False)
    print(f"OK: wrote {len(dev_df)} dev-subset rows -> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
