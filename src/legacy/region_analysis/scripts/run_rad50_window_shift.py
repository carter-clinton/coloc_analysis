#!/usr/bin/env python3
"""
Run RAD50_IL13 window-shift coloc checks for AFR stroke vs T2D.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regions",
        default="config/regions_tiled.csv",
        help="Regions tiled CSV.",
    )
    parser.add_argument(
        "--output",
        default="results/analysis/rad50_window_shift.tsv",
        help="Output TSV.",
    )
    parser.add_argument(
        "--shift",
        type=int,
        default=250000,
        help="Shift size in bp.",
    )
    parser.add_argument(
        "--rscript",
        default=None,
        help="Rscript path with coloc installed.",
    )
    return parser.parse_args()


def load_config_rscript() -> str:
    cfg = yaml.safe_load(Path("config/config.yaml").read_text())
    return cfg.get("finemap", {}).get("rscript_bin", "Rscript")


def write_manifest(path: Path, row: dict) -> None:
    df = pd.DataFrame([row])
    df.to_csv(path, sep="\t", index=False)


def run_coloc(rscript: str, manifest: Path, pair_id: str, out_json: Path) -> None:
    cmd = [
        rscript,
        "scripts/run_coloc.R",
        "--manifest",
        str(manifest),
        "--pair-id",
        pair_id,
        "--output",
        str(out_json),
    ]
    subprocess.check_call(cmd)


def main() -> None:
    args = parse_args()
    rscript = args.rscript or load_config_rscript()

    regions = pd.read_csv(args.regions)
    sub = regions[regions["parent_region"] == "RAD50_IL13_5q31.1"]
    if sub.empty:
        raise SystemExit("Missing RAD50_IL13_5q31.1 in regions.")

    chrom = str(sub["chr"].iloc[0])
    start = int(sub["start"].min())
    end = int(sub["end"].max())

    shifts = {
        "baseline": (start, end),
        "shift_minus": (max(1, start - args.shift), max(1, end - args.shift)),
        "shift_plus": (start + args.shift, end + args.shift),
    }

    out_rows = []
    out_dir = Path("results/analysis/rad50_window_shift")
    out_dir.mkdir(parents=True, exist_ok=True)

    for label, (s, e) in shifts.items():
        pair_id = f"RAD50_IL13_5q31.1__AFR__stroke_vs_t2d__{label}"
        manifest_row = {
            "pair_id": pair_id,
            "base_region": "RAD50_IL13_5q31.1",
            "ancestry": "AFR",
            "trait_a": "stroke",
            "trait_b": "t2d",
            "chr": chrom,
            "start": s,
            "end": e,
            "path_a": "data_processed/sumstats_harmonized_fixed/stroke.AFR.tsv.bgz",
            "path_b": "data_processed/sumstats_harmonized_fixed/t2d.AFR.tsv.bgz",
        }
        manifest_path = out_dir / f"{pair_id}.manifest.tsv"
        out_json = out_dir / f"{pair_id}.json"
        write_manifest(manifest_path, manifest_row)
        run_coloc(rscript, manifest_path, pair_id, out_json)

        data = json.loads(out_json.read_text())
        summary = data.get("summary", {})
        pp_h3 = summary.get("PP.H3")
        pp_h4 = summary.get("PP.H4")
        if pp_h3 is None:
            pp_h3 = summary.get("PP.H3.abf")
        if pp_h4 is None:
            pp_h4 = summary.get("PP.H4.abf")
        out_rows.append(
            {
                "shift": label,
                "chr": chrom,
                "start": s,
                "end": e,
                "n_common_snps": data.get("n_common_snps"),
                "PP.H3": pp_h3,
                "PP.H4": pp_h4,
                "ld_source": "1KGP_AFR",
            }
        )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(out_rows).to_csv(out_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
