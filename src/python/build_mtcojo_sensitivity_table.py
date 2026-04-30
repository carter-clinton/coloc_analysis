#!/usr/bin/env python3
"""Aggregate per-target mtCOJO outputs into a per-stratum sensitivity table.

For each eligible (stratum, target_trait), reads the mtcojo .cojo output
and joins MTAG-novel hit p-values to compute a per-locus sensitivity
flag (PASS / WARN / FAIL).

Output schema (Q8 + D-M2-Q3):
  locus_id, trait, mtag_p_original, mtcojo_p, max_overlapping_intercept,
  sensitivity_flag, [trans_ld_panel_concordance for TRANS]

trans_ld_panel_concordance is reserved for the D-M2-Q3 sensitivity column;
the first-pass production fire writes a placeholder string ("primary_only")
in the TRANS rows and the column is omitted for EUR/AFR.

Plan: m2-04-clumping-mtcojo-regions-PLAN.md (D-M2-08, D-M2-Q3, D-M2-Q5).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


_GWS = 5e-8
_NOMINAL = 1e-5


def _classify(p_cojo: float | None) -> str:
    if p_cojo is None or pd.isna(p_cojo):
        return "FAIL"
    if p_cojo < _GWS:
        return "PASS"
    if p_cojo < _NOMINAL:
        return "WARN"
    return "FAIL"


def build_sensitivity_table(
    eligible_path: Path,
    mtcojo_dir: Path,
    mtag_filtered_path: Path,
    stratum: str,
) -> pd.DataFrame:
    elig = pd.read_csv(eligible_path, sep="\t")
    if elig.empty:
        cols = ["locus_id", "trait", "mtag_p_original", "mtcojo_p",
                "max_overlapping_intercept", "sensitivity_flag"]
        if stratum == "TRANS":
            cols.append("trans_ld_panel_concordance")
        return pd.DataFrame(columns=cols)

    # Pre-load MTAG filtered hits — one MTAG hit per (SNP × trait_key)
    mtag = pd.read_csv(mtag_filtered_path, sep="\t")
    mtag_by_target: dict[str, pd.DataFrame] = {}
    for trait, sub in mtag.groupby("trait_key"):
        mtag_by_target[trait] = sub[["SNP", "mtag_pval"]].rename(
            columns={"mtag_pval": "mtag_p_original"}
        )

    rows = []
    for _, r in elig.iterrows():
        target = r["target_trait"]
        cojo_path = mtcojo_dir / f"{target}.mtcojo.cojo"
        if not cojo_path.exists():
            # mtCOJO failed for this target — emit one FAIL row for the (target) bucket
            rows.append({
                "locus_id": "",
                "trait": target,
                "mtag_p_original": None,
                "mtcojo_p": None,
                "max_overlapping_intercept": r["max_overlapping_intercept"],
                "sensitivity_flag": "FAIL",
                **({"trans_ld_panel_concordance": "primary_only"} if stratum == "TRANS" else {}),
            })
            continue

        # mtCOJO output is whitespace-delimited; columns include
        # SNP A1 A2 freq b se p N b_cojo se_cojo p_cojo (Q8 schema)
        try:
            cojo = pd.read_csv(cojo_path, sep=r"\s+", engine="python")
        except Exception:
            continue
        if cojo.empty:
            continue
        # Filter to MTAG-novel SNPs only (intersect SNP between cojo + mtag)
        mt = mtag_by_target.get(target, pd.DataFrame(columns=["SNP", "mtag_p_original"]))
        if mt.empty:
            continue
        mt_novel = mt[mt["mtag_p_original"] < _GWS]
        merged = cojo.merge(mt_novel, on="SNP", how="inner")
        if merged.empty:
            continue
        for _, c in merged.iterrows():
            p_cojo = c.get("bC_pval", c.get("p_cojo", c.get("pC", None)))
            row = {
                "locus_id": c.get("SNP", ""),
                "trait": target,
                "mtag_p_original": float(c.get("mtag_p_original", float("nan"))),
                "mtcojo_p": float(p_cojo) if p_cojo is not None and not pd.isna(p_cojo) else None,
                "max_overlapping_intercept": float(r["max_overlapping_intercept"]),
                "sensitivity_flag": _classify(p_cojo),
            }
            if stratum == "TRANS":
                # D-M2-Q3 — TRANS sensitivity column. First-pass fire uses
                # primary 1000G EUR LD; AFR sensitivity re-fire is queued
                # as a follow-up task.
                row["trans_ld_panel_concordance"] = "primary_only"
            rows.append(row)
    return pd.DataFrame(rows)


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stratum", required=True)
    ap.add_argument("--eligible", type=Path, required=True)
    ap.add_argument("--mtcojo-dir", type=Path, required=True)
    ap.add_argument("--mtag-filtered", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    df = build_sensitivity_table(
        args.eligible,
        args.mtcojo_dir,
        args.mtag_filtered,
        args.stratum,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, sep="\t", index=False)
    n_pass = (df["sensitivity_flag"] == "PASS").sum() if not df.empty else 0
    n_warn = (df["sensitivity_flag"] == "WARN").sum() if not df.empty else 0
    n_fail = (df["sensitivity_flag"] == "FAIL").sum() if not df.empty else 0
    print(f"{args.stratum}: {len(df)} loci → PASS={n_pass} WARN={n_warn} FAIL={n_fail}")


if __name__ == "__main__":
    _main()
