#!/usr/bin/env python3
"""Aggregate per-pair QTL coloc JSON outputs into a summary TSV.

Reads all JSON files in the QTL coloc directory, extracts the summary row
(best PP.H4.abf pairwise comparison) from each, and writes a flat TSV for
downstream filtering and tiering.

Usage:
    python aggregate_qtl_coloc.py \
        --json-dir results/qtl_coloc \
        --manifest results/qtl_coloc/qtl_coloc_manifest.tsv \
        --output results/qtl_coloc/qtl_coloc_summary.tsv
"""
import argparse
import json
import logging
import os
import sys
from glob import glob
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Columns to extract from each JSON summary object
SUMMARY_PP_COLS = [
    "PP.H0.abf",
    "PP.H1.abf",
    "PP.H2.abf",
    "PP.H3.abf",
    "PP.H4.abf",
]

METADATA_COLS = [
    "qtl_source",
    "tissue",
    "gene_id",
    "region",
    "ancestry",
    "n_snps_overlap",
    "qtl_n",
    "qtl_sdy",
    "n_cs_gwas",
    "n_cs_qtl",
    "status",
]


def parse_coloc_json(json_path: str) -> dict:
    """Parse a single QTL coloc JSON file and extract the summary row.

    Parameters
    ----------
    json_path : str
        Path to a {qtl_coloc_id}.json file produced by run_qtl_coloc.R.

    Returns
    -------
    dict
        Flat dictionary with metadata + PP columns, or None if parsing fails.
    """
    try:
        with open(json_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Skipping malformed JSON %s: %s", json_path, e)
        return None

    qtl_coloc_id = Path(json_path).stem
    row = {"qtl_coloc_id": qtl_coloc_id}

    # Extract metadata fields
    for col in METADATA_COLS:
        row[col] = data.get(col, "")

    # Extract best PP.H4 summary row
    summary = data.get("summary", {})
    if isinstance(summary, dict):
        for col in SUMMARY_PP_COLS:
            row[col] = summary.get(col, "")
        # Also extract hit1/hit2 if present (credible set indices)
        row["hit1"] = summary.get("hit1", "")
        row["hit2"] = summary.get("hit2", "")
    else:
        # Empty summary (e.g., no credible sets found)
        for col in SUMMARY_PP_COLS:
            row[col] = ""
        row["hit1"] = ""
        row["hit2"] = ""

    return row


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate QTL coloc JSON results into summary TSV"
    )
    parser.add_argument(
        "--json-dir",
        required=True,
        help="Directory containing per-pair *.json coloc results",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="QTL coloc manifest TSV (used to verify completeness)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output summary TSV path",
    )
    args = parser.parse_args()

    # Find all JSON files
    json_files = sorted(glob(os.path.join(args.json_dir, "*.json")))
    logger.info("Found %d JSON files in %s", len(json_files), args.json_dir)

    if len(json_files) == 0:
        logger.warning(
            "No JSON coloc results found in %s. "
            "Writing empty summary with header only.",
            args.json_dir,
        )

    # Parse all JSON files
    rows = []
    n_skipped = 0
    for jf in json_files:
        row = parse_coloc_json(jf)
        if row is not None:
            rows.append(row)
        else:
            n_skipped += 1

    if n_skipped > 0:
        logger.warning("Skipped %d malformed JSON files", n_skipped)

    # Define output column order
    out_cols = (
        ["qtl_coloc_id"]
        + METADATA_COLS
        + SUMMARY_PP_COLS
        + ["hit1", "hit2"]
    )

    # Write output TSV
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        f.write("\t".join(out_cols) + "\n")
        for row in rows:
            f.write("\t".join(str(row.get(c, "")) for c in out_cols) + "\n")

    logger.info(
        "Wrote %d rows to %s (%d skipped)",
        len(rows),
        args.output,
        n_skipped,
    )

    # Cross-check with manifest
    if os.path.exists(args.manifest):
        with open(args.manifest) as f:
            # Skip header
            manifest_ids = set()
            header = f.readline()
            for line in f:
                fields = line.strip().split("\t")
                if fields:
                    manifest_ids.add(fields[0])
        result_ids = {r["qtl_coloc_id"] for r in rows}
        missing = manifest_ids - result_ids
        if missing:
            logger.warning(
                "%d manifest entries have no JSON output (may still be running): %s",
                len(missing),
                ", ".join(sorted(list(missing)[:5]))
                + ("..." if len(missing) > 5 else ""),
            )


if __name__ == "__main__":
    main()
