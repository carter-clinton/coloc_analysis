#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize HyPrColoc outputs.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_json(path: Path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None


def main():
    args = parse_args()
    manifest = pd.read_csv(args.manifest, sep="\t")
    rows = []
    for _, row in manifest.iterrows():
        group_id = row["group_id"]
        out_path = Path(args.out_dir) / f"{group_id}.json"
        data = load_json(out_path)
        if not data:
            rows.append(
                {
                    "group_id": group_id,
                    "base_region": row["base_region"],
                    "ancestry": row["ancestry"],
                    "traits": row.get("traits_included", ""),
                    "status": "missing",
                    "n_shared_snps": row.get("n_shared_snps", 0),
                }
            )
            continue
        status = data.get("status", "ok")
        result = data.get("result", {})
        summary = data.get("summary", {})
        candidate = ""
        posterior = ""
        traits_used = ""
        regional_prob = ""
        dropped_trait = ""
        if isinstance(summary, dict):
            candidate = summary.get("candidate", candidate)
            posterior = summary.get("posterior", posterior)
            traits_used = summary.get("traits_used", traits_used)
        if isinstance(result, dict):
            candidate = candidate or result.get("candidate", "")
            posterior = posterior or result.get("posterior", "")
            traits_used = traits_used or result.get("traits", "")
            results = result.get("results")
            if isinstance(results, list) and results:
                top = results[0]
                regional_prob = top.get("regional_prob", regional_prob)
                dropped_trait = top.get("dropped_trait", dropped_trait)
        rows.append(
            {
                "group_id": group_id,
                "base_region": data.get("base_region", row["base_region"]),
                "ancestry": data.get("ancestry", row["ancestry"]),
                "traits": ",".join(data.get("traits", [])) if isinstance(data.get("traits"), list) else data.get("traits", ""),
                "status": status,
                "n_shared_snps": data.get("n_shared_snps", row.get("n_shared_snps", 0)),
                "candidate": candidate,
                "posterior": posterior,
                "traits_used": traits_used,
                "regional_prob": regional_prob,
                "dropped_trait": dropped_trait,
            }
        )
    out = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
