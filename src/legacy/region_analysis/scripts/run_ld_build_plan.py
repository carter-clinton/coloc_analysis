#!/usr/bin/env python3
"""
Execute build_ld_rds.py for each entry in the LD build plan.
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
from pathlib import Path
from typing import Dict

import yaml


def load_config(path: Path) -> Dict:
    with path.open() as handle:
        return yaml.safe_load(handle)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--plan",
        default="results/fine_mapping/ld_build_plan.tsv",
        help="Path to ld_build_plan.tsv generated earlier.",
    )
    p.add_argument(
        "--config",
        default="config/config.yaml",
        help="Global config file (for ld root + Rscript path).",
    )
    p.add_argument(
        "--max-variants",
        type=int,
        default=6000,
        help="Max variants per region (passed via LD_MAX_VARIANTS).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Rebuild even if output exists.",
    )
    p.add_argument(
        "--ancestry",
        action="append",
        help="Only build for specific ancestry (can be repeated).",
    )
    p.add_argument(
        "--region",
        action="append",
        help="Only build for specific region_id (can be repeated).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    plan_path = Path(args.plan)
    if not plan_path.exists():
        raise SystemExit(f"Plan file not found: {plan_path}")

    cfg = load_config(Path(args.config))
    ld_root = Path(cfg["paths"]["ld_1kg_root"])
    variant_dir = Path(cfg["paths"]["ld_reference"]) / "variants"
    rscript = cfg["finemap"]["rscript_bin"]

    def to_safe(name: str) -> str:
        safe = name.replace("/", "_").replace(".", "_")
        return safe

    with plan_path.open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        tasks = list(reader)

    if not tasks:
        print("No LD build tasks found.")
        return

    env = os.environ.copy()
    env["LD_MAX_VARIANTS"] = str(args.max_variants)

    ancestries_filter = set(args.ancestry) if args.ancestry else None
    regions_filter = set(args.region) if args.region else None

    for row in tasks:
        region = row["region_id"]
        ancestry = row["ancestry"]
        if ancestries_filter and ancestry not in ancestries_filter:
            continue
        if regions_filter and region not in regions_filter:
            continue
        chrom = row["chr"]
        start = row.get("start")
        end = row.get("end")
        output = Path(row.get("ld_rds_expected", ""))
        region_safe = to_safe(region)
        variant_path = variant_dir / f"{region_safe}.tsv"
        samples_path = Path(row.get("samples_file", ""))
        if not output:
            print(f"[ld-build-plan] Skipping {region} ({ancestry}): missing output path")
            continue
        if output.exists() and not args.force:
            print(f"[ld-build-plan] Skipping existing {output}")
            continue
        vcf = ld_root / "vcf" / f"chr{chrom}.vcf.gz"
        if not vcf.exists():
            print(f"[ld-build-plan] Missing VCF for chr{chrom}: {vcf}")
            continue
        if not samples_path.exists():
            print(f"[ld-build-plan] Missing samples file: {samples_path}")
            continue
        if not variant_path.exists():
            print(f"[ld-build-plan] Missing variant list: {variant_path}")
            continue
        if not start or not end:
            print(f"[ld-build-plan] Missing coordinates for {region}")
            continue
        cmd = [
            "python3",
            "scripts/build_ld_rds.py",
            "--vcf",
            str(vcf),
            "--samples",
            str(samples_path),
            "--chrom",
            str(chrom),
            "--start",
            str(start),
            "--end",
            str(end),
            "--region-id",
            region,
            "--ancestry",
            ancestry,
            "--output",
            str(output),
            "--rscript",
            rscript,
            "--variant-list",
            str(variant_path),
        ]
        print(f"[ld-build-plan] Building {output} ...")
        subprocess.run(cmd, check=True, env=env)


if __name__ == "__main__":
    main()
