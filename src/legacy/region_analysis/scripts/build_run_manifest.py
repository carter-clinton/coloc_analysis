#!/usr/bin/env python3
"""
Build a run manifest with key inputs and version metadata.
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="results/analysis/run_manifest.tsv",
        help="Output TSV path.",
    )
    return parser.parse_args()


def main():
    items = []
    now = datetime.now(timezone.utc).isoformat()
    items.append({"item": "run_timestamp_utc", "path": "", "value": now})

    git_commit = run_cmd(["git", "rev-parse", "HEAD"])
    if git_commit:
        items.append({"item": "git_commit", "path": "", "value": git_commit})
        git_status = run_cmd(["git", "status", "--porcelain"])
        items.append({"item": "git_dirty", "path": "", "value": str(bool(git_status))})

    python_ver = run_cmd(["python3", "--version"])
    items.append({"item": "python_version", "path": "", "value": python_ver})

    r_ver = run_cmd(["Rscript", "--version"])
    items.append({"item": "r_version", "path": "", "value": r_ver})

    for rel in [
        "config/config.yaml",
        "config/datasets.yaml",
        "config/regions_tiled.csv",
        "results/fine_mapping/finemap_summary_augmented.tsv",
        "results/multitrait/coloc_summary_augmented.tsv",
        "results/multitrait/hyprcoloc_summary.tsv",
    ]:
        path = Path(rel)
        if not path.exists():
            continue
        items.append(
            {
                "item": "input_file",
                "path": str(path),
                "value": str(path.stat().st_mtime),
            }
        )

    output_path = Path(parse_args().output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["item", "path", "value"], delimiter="\t")
        writer.writeheader()
        writer.writerows(items)


if __name__ == "__main__":
    main()
