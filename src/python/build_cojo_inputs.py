#!/usr/bin/env python3
"""Build per-stratum COJO-format sumstats + mtcojo input list.

For a given (stratum, target_trait), reads the residcov.trait_order.json
sidecar to find all K stratum traits, materializes one COJO file per
trait at `<out_dir>/{trait_key}.cojo`, and emits the 2-column mtcojo
input list at `<out_dir>/{target}.mtcojo.list` with the target trait FIRST
followed by all covariate traits.

COJO format (whitespace-delimited): SNP A1 A2 freq b se p N

Source schema (M1 harmonized .tsv.bgz):
  CHR BP SNP EA OA BETA SE P EAF N

Plan: m2-04-clumping-mtcojo-regions-PLAN.md (D-M2-08, D-M2-Q5).
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import pandas as pd


def _harmonized_path(harmonized_dir: Path, trait_key: str) -> Path:
    """Locate the harmonized .tsv.bgz for a trait_key (`bmi.EUR.GIANT-UKBB.2018`)."""
    candidate = harmonized_dir / f"{trait_key}.GRCh37.tsv.bgz"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"harmonized sumstats not found for {trait_key} at {candidate}"
    )


def materialize_cojo(harmonized_path: Path, out_path: Path) -> int:
    """Read harmonized .tsv.bgz, emit COJO-format file (SNP A1 A2 freq b se p N).

    EA → A1, OA → A2, EAF → freq, BETA → b, SE → se, P → p, N → N.
    Returns row count.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(harmonized_path, sep="\t", compression="gzip")
    rename = {}
    # Tolerate column-name variants (sbp.EUR uses REF/ALT/SNP_ID instead of OA/EA/SNP)
    if "EA" in df.columns and "OA" in df.columns:
        rename.update({"EA": "A1", "OA": "A2"})
    elif "ALT" in df.columns and "REF" in df.columns:
        rename.update({"ALT": "A1", "REF": "A2"})
    if "EAF" in df.columns:
        rename["EAF"] = "freq"
    if "BETA" in df.columns:
        rename["BETA"] = "b"
    if "SE" in df.columns:
        rename["SE"] = "se"
    if "P" in df.columns:
        rename["P"] = "p"
    if "SNP" not in df.columns and "SNP_ID" in df.columns:
        rename["SNP_ID"] = "SNP"
    df = df.rename(columns=rename)
    needed = ["SNP", "A1", "A2", "freq", "b", "se", "p", "N"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(
            f"build_cojo_inputs: harmonized {harmonized_path} missing columns {missing}; "
            f"have {list(df.columns)[:20]}"
        )
    df = df[needed].dropna(subset=["SNP", "A1", "A2", "p"])
    # GCTA mtCOJO requires sumstats with no NaN in essential cols
    df = df.dropna(subset=["b", "se", "freq", "N"])
    # GCTA mtCOJO REJECTS duplicate SNP IDs — keep first occurrence per SNP
    df = df.drop_duplicates(subset=["SNP"], keep="first")
    df.to_csv(out_path, sep="\t", index=False)
    return len(df)


def build_inputs(
    target: str,
    stratum: str,
    sidecar: Path,
    harmonized_dir: Path,
    out_dir: Path,
) -> Path:
    """Materialize per-trait COJO files + mtcojo input list.

    Returns path to the mtcojo input list file (target_trait first).
    """
    side = json.loads(sidecar.read_text())
    trait_order = side["trait_order"]
    if target not in trait_order:
        raise ValueError(f"target {target} not in stratum {stratum} trait_order {trait_order}")

    out_dir.mkdir(parents=True, exist_ok=True)
    list_path = out_dir / f"{target}.mtcojo.list"

    # Materialize each trait's COJO file (cached: skip if already present + non-empty)
    cojo_paths: dict[str, Path] = {}
    for trait in trait_order:
        cojo_path = out_dir / f"{trait}.cojo"
        if not cojo_path.exists() or cojo_path.stat().st_size == 0:
            harm = _harmonized_path(harmonized_dir, trait)
            n = materialize_cojo(harm, cojo_path)
            print(f"  cojo: {trait} → {n} SNPs")
        cojo_paths[trait] = cojo_path

    # Write mtcojo list: target FIRST, then covariates in trait_order
    others = [t for t in trait_order if t != target]
    with open(list_path, "w") as f:
        f.write(f"{target}\t{cojo_paths[target].resolve()}\n")
        for t in others:
            f.write(f"{t}\t{cojo_paths[t].resolve()}\n")
    return list_path


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, help="trait_key of the focal target trait")
    ap.add_argument("--stratum", required=True, choices=("EUR", "AFR", "TRANS"))
    ap.add_argument("--sidecar", type=Path, required=True)
    ap.add_argument("--harmonized-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    list_path = build_inputs(
        args.target,
        args.stratum,
        args.sidecar,
        args.harmonized_dir,
        args.out_dir,
    )
    print(f"Wrote mtcojo list at {list_path}")


if __name__ == "__main__":
    _main()
