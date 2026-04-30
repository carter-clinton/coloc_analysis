#!/usr/bin/env python3
"""src/python/build_coloc_manifest_r2.py — Wave 2 manifest builder (D-TA-03).

Phase: ta-sh2b3-canonical-and-cache-refresh

Filters the existing results/multitrait/coloc_manifest.tsv to the 9 SH2B3 EUR
canonical trait-pairs (lattice minus already-on-disk asthma_vs_t2d) and writes
a parallel manifest at results/multitrait/coloc_manifest_R2.tsv.

When some R2 pair_ids are not present in the source manifest, the builder
synthesizes rows by cloning the schema from an existing SH2B3 EUR row and
substituting trait1/trait2 columns from the pair_id parse.

Pitfall 3 mitigation: the parallel manifest decouples Wave 2 outputs from
the canonical Stage 2 coloc_manifest.tsv (and downstream coloc_summary.tsv
md5 invariant 5fa3c4004970c5da711d05947cb1f7d2) until the Wave 5 explicit
re-render relaxation.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# D-TA-01 canonical path (with GPFS fallback per W0 Task 1 finding).
RS1_ROOT = Path("/rs1/researchers/c/ckclinto/coloc_analysis")
GPFS_ROOT = Path("/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis")
REPO_ROOT = RS1_ROOT if (RS1_ROOT / ".git").is_dir() else GPFS_ROOT

SOURCE_MANIFEST = REPO_ROOT / "results/multitrait/coloc_manifest.tsv"
R2_MANIFEST = REPO_ROOT / "results/multitrait/coloc_manifest_R2.tsv"

R2_PAIRS = (
    "SH2B3_12q24__EUR__asthma_vs_bmi",
    "SH2B3_12q24__EUR__asthma_vs_hypertension",
    "SH2B3_12q24__EUR__asthma_vs_stroke",
    "SH2B3_12q24__EUR__bmi_vs_hypertension",
    "SH2B3_12q24__EUR__bmi_vs_stroke",
    "SH2B3_12q24__EUR__bmi_vs_t2d",
    "SH2B3_12q24__EUR__hypertension_vs_stroke",
    "SH2B3_12q24__EUR__hypertension_vs_t2d",
    "SH2B3_12q24__EUR__stroke_vs_t2d",
)


def main() -> None:
    if not SOURCE_MANIFEST.exists():
        raise FileNotFoundError(
            f"{SOURCE_MANIFEST} not present; cannot build R2 manifest"
        )
    src = pd.read_csv(SOURCE_MANIFEST, sep="\t")
    if "pair_id" not in src.columns:
        raise KeyError(
            f"Source manifest missing 'pair_id' column. Columns: {list(src.columns)}"
        )

    # Filter to the 9 R2 pair IDs already present
    existing = src[src["pair_id"].isin(R2_PAIRS)]
    missing = set(R2_PAIRS) - set(existing["pair_id"].tolist())

    if missing:
        # Synthesize rows by cloning an existing SH2B3 EUR template
        template_rows = src[src["pair_id"].str.startswith("SH2B3_12q24__EUR__")]
        if template_rows.empty:
            raise RuntimeError(
                f"Cannot synthesize missing R2 pairs {missing}: "
                "no SH2B3 EUR template row in source manifest"
            )
        template = template_rows.iloc[0]
        synth_rows = []
        for pid in sorted(missing):
            row = template.copy()
            row["pair_id"] = pid
            # Update trait_a/trait_b (or trait1/trait2) columns from the pair_id
            parts = pid.split("__")[2].split("_vs_")
            if "trait_a" in src.columns and "trait_b" in src.columns:
                row["trait_a"] = parts[0]
                row["trait_b"] = parts[1]
                if "path_a" in src.columns:
                    ancestry = pid.split("__")[1]
                    row["path_a"] = (
                        f"data/processed/sumstats_harmonized/{parts[0]}.{ancestry}.tsv.bgz"
                    )
                    row["path_b"] = (
                        f"data/processed/sumstats_harmonized/{parts[1]}.{ancestry}.tsv.bgz"
                    )
            elif "trait1" in src.columns and "trait2" in src.columns:
                row["trait1"] = parts[0]
                row["trait2"] = parts[1]
            synth_rows.append(row)
        existing = pd.concat([existing, pd.DataFrame(synth_rows)], ignore_index=True)

    existing = existing.sort_values("pair_id").reset_index(drop=True)
    R2_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    existing.to_csv(R2_MANIFEST, sep="\t", index=False)
    print(f"Wrote {len(existing)} rows to {R2_MANIFEST}")


if __name__ == "__main__":
    main()
