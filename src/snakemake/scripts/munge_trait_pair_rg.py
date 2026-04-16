#!/usr/bin/env python3
"""Parse LDSC r_g .log files into a single TSV for downstream FDR correction.

D-04a: 10 cross-trait pairs x 3 ancestry-pair strata = 30 tests
D-04b: 5 same-trait EUR-AFR benchmarks (is_global_benchmark=TRUE)
Total: 35 tests; all fed into BH-FDR q<0.05 per D-04c.

Output columns:
    trait1, trait2, ancestry1, ancestry2, is_global_benchmark,
    rg, se, z, p, h2_obs_t1, h2_obs_t2

LDSC .log format parsed:
    - 'Genetic Correlation' section contains: rg, se, z, p
    - 'Heritability of phenotype 1/2' sections contain h2 observed
"""
import argparse
import re
import sys
from pathlib import Path


def parse_ldsc_rg_log(log_path):
    """Parse an LDSC r_g .log file and extract genetic correlation stats.

    Returns a dict with keys: rg, se, z, p, h2_obs_t1, h2_obs_t2.
    Returns None values if the log indicates LDSC could not compute r_g.
    """
    text = Path(log_path).read_text()

    result = {
        "rg": None, "se": None, "z": None, "p": None,
        "h2_obs_t1": None, "h2_obs_t2": None,
    }

    # Parse genetic correlation block
    # LDSC outputs lines like:
    # Genetic Correlation
    # -------------------
    # Genetic Correlation: 0.1234 (0.0567)
    # Z-score: 2.18
    # P: 0.0294
    rg_match = re.search(
        r"Genetic Correlation:\s*([-\d.eE+naNA]+)\s*\(([-\d.eE+naNA]+)\)",
        text,
    )
    if rg_match:
        try:
            result["rg"] = float(rg_match.group(1))
            result["se"] = float(rg_match.group(2))
        except ValueError:
            pass

    z_match = re.search(r"Z-score:\s*([-\d.eE+naNA]+)", text)
    if z_match:
        try:
            result["z"] = float(z_match.group(1))
        except ValueError:
            pass

    p_match = re.search(r"P:\s*([-\d.eE+naNA]+)", text)
    if p_match:
        try:
            result["p"] = float(p_match.group(1))
        except ValueError:
            pass

    # Parse h2 observed for phenotype 1 and 2
    # LDSC outputs: "Total Observed scale h2: 0.1234 (0.0123)"
    h2_matches = re.findall(
        r"Total Observed scale h2:\s*([-\d.eE+naNA]+)", text
    )
    if len(h2_matches) >= 1:
        try:
            result["h2_obs_t1"] = float(h2_matches[0])
        except ValueError:
            pass
    if len(h2_matches) >= 2:
        try:
            result["h2_obs_t2"] = float(h2_matches[1])
        except ValueError:
            pass

    return result


def parse_filename(log_path):
    """Extract trait1, trait2, ancestry1, ancestry2 from log filename.

    Expected format: {trait1}_{trait2}_{ancestry1}_{ancestry2}.log
    """
    stem = Path(log_path).stem  # e.g., "t2d_stroke_EUR_AFR"
    parts = stem.rsplit("_", 2)  # Split from right: ancestry2, ancestry1, rest
    if len(parts) < 3:
        raise ValueError(f"Cannot parse filename: {log_path}")

    ancestry2 = parts[-1]
    ancestry1 = parts[-2]
    trait_part = parts[-3]

    # trait_part may contain underscore if traits have underscores;
    # but our 5 T1 traits (t2d, stroke, hypertension, asthma, bmi) are all
    # single-word, so we can split on the last underscore within trait_part
    # for same-trait cases (e.g., "t2d_t2d")
    trait_split = trait_part.rsplit("_", 1)
    if len(trait_split) == 2:
        trait1, trait2 = trait_split
    else:
        # Single trait name — same-trait test
        trait1 = trait2 = trait_split[0]

    return trait1, trait2, ancestry1, ancestry2


def main():
    parser = argparse.ArgumentParser(
        description="Parse LDSC r_g .log files into TSV for FDR correction."
    )
    parser.add_argument("--log-dir", required=True, help="Directory containing .log files")
    parser.add_argument("--out", required=True, help="Output TSV path")
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    log_files = sorted(log_dir.glob("*.log"))

    if not log_files:
        print(f"WARNING: No .log files found in {log_dir}", file=sys.stderr)

    rows = []
    for lf in log_files:
        trait1, trait2, ancestry1, ancestry2 = parse_filename(lf)
        stats = parse_ldsc_rg_log(lf)

        # D-04b: same-trait cross-ancestry r_g is the global benchmark
        is_global_benchmark = (trait1 == trait2) and (
            {ancestry1, ancestry2} == {"EUR", "AFR"}
        )

        rows.append({
            "trait1": trait1,
            "trait2": trait2,
            "ancestry1": ancestry1,
            "ancestry2": ancestry2,
            "is_global_benchmark": is_global_benchmark,
            "rg": stats["rg"],
            "se": stats["se"],
            "z": stats["z"],
            "p": stats["p"],
            "h2_obs_t1": stats["h2_obs_t1"],
            "h2_obs_t2": stats["h2_obs_t2"],
        })

    # Write output TSV
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "trait1", "trait2", "ancestry1", "ancestry2", "is_global_benchmark",
        "rg", "se", "z", "p", "h2_obs_t1", "h2_obs_t2",
    ]
    with open(out_path, "w") as f:
        f.write("\t".join(columns) + "\n")
        for row in rows:
            vals = []
            for col in columns:
                v = row[col]
                if v is None:
                    vals.append("NA")
                elif isinstance(v, bool):
                    vals.append(str(v).upper())
                else:
                    vals.append(str(v))
            f.write("\t".join(vals) + "\n")

    print(f"Wrote {len(rows)} r_g test results to {out_path}")


if __name__ == "__main__":
    main()
