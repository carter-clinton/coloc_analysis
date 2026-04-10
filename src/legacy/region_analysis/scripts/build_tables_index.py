#!/usr/bin/env python3
"""
Build an index of TSV outputs with basic metadata.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


DESCRIPTIONS = {
    "finemap_summary.tsv": "SuSiE fine-mapping summary (per region × trait × ancestry)",
    "finemap_summary_augmented.tsv": "Fine-mapping summary with LD/QC annotations",
    "finemap_tier1_high_conf.tsv": "Tier1 fine-mapping high-confidence subset",
    "finemap_tier2_relaxed.tsv": "Tier2 fine-mapping relaxed subset",
    "finemap_tier3_coloc.tsv": "Tier3 coloc-eligible subset",
    "coloc_summary.tsv": "Pairwise coloc summary (PP.H3/PP.H4)",
    "coloc_summary_augmented.tsv": "Coloc summary with QC metrics",
    "coloc_main_hits.tsv": "Main coloc results table for manuscript",
    "coloc_manifest.tsv": "Pairwise coloc manifest",
    "hyprcoloc_manifest.tsv": "HyPrColoc group manifest",
    "hyprcoloc_summary.tsv": "HyPrColoc summary",
    "region_trait_qc.tsv": "Region × trait QC metrics",
    "effect_scale_report.tsv": "Effect-scale QC report",
    "effect_scale_actions.tsv": "Effect-scale recommended actions",
    "figures_index.tsv": "Index of figure files",
    "cross_ancestry_finemap_compare.tsv": "Cross-ancestry finemap comparison",
    "cross_ancestry_coloc_compare.tsv": "Cross-ancestry coloc comparison",
    "replication_finemap_compare.tsv": "Replication finemap comparison",
    "replication_coloc_compare.tsv": "Replication coloc comparison",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default="results",
        help="Root directory to scan for TSV files.",
    )
    parser.add_argument(
        "--output",
        default="results/analysis/tables_index.tsv",
        help="Output TSV path.",
    )
    return parser.parse_args()


def count_lines(path: Path) -> int:
    with path.open("r") as handle:
        return sum(1 for _ in handle)


def main():
    args = parse_args()
    root = Path(args.root)
    rows = []
    for path in sorted(root.rglob("*.tsv")):
        try:
            with path.open("r") as handle:
                header = handle.readline().strip()
        except OSError:
            continue
        n_rows = max(count_lines(path) - 1, 0)
        n_cols = len(header.split("\t")) if header else 0
        desc = DESCRIPTIONS.get(path.name, "TSV output")
        rows.append(
            {
                "path": str(path),
                "rows": n_rows,
                "cols": n_cols,
                "description": desc,
                "modified": path.stat().st_mtime,
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "rows", "cols", "description", "modified"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
