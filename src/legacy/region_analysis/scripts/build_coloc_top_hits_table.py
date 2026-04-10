#!/usr/bin/env python3
"""
Build a EUR vs AFR side-by-side H4 top-hits table with QC annotations.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate",
        default="results/analysis/coloc_candidate_h4.tsv",
        help="Candidate H4 table.",
    )
    parser.add_argument(
        "--clean",
        default="results/analysis/coloc_main_h4.tsv",
        help="Strict clean H4 table.",
    )
    parser.add_argument(
        "--effect-scale",
        default="results/qc/effect_scale_report_fixed.tsv",
        help="Effect-scale QC report (fixed sumstats).",
    )
    parser.add_argument(
        "--output",
        default="results/analysis/coloc_top_hits_table.tsv",
        help="Output TSV path.",
    )
    return parser.parse_args()


def rename_cols(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    keep = {
        "PP.H3": f"{prefix}PP.H3",
        "PP.H4": f"{prefix}PP.H4",
        "n_common_snps": f"{prefix}n_common_snps",
        "overlap_tier": f"{prefix}overlap_tier",
        "overlap_frac_min": f"{prefix}overlap_frac_min",
        "ld_overlap_min": f"{prefix}ld_overlap_min",
        "qc_flag": f"{prefix}qc_flag",
    }
    cols = [c for c in keep if c in df.columns]
    out = df[["base_region", "trait_a", "trait_b"] + cols].copy()
    out = out.rename(columns=keep)
    return out


def pp_class(h3: float, h4: float) -> str:
    if np.isnan(h4) and np.isnan(h3):
        return ""
    if h4 >= 0.8:
        return "H4_shared"
    if h3 >= 0.8 and (np.isnan(h4) or h4 < 0.5):
        return "H3_distinct"
    return "ambiguous"


def qc_class(row_key: Tuple[str, str], clean_set: set, cand_set: set) -> str:
    if row_key in clean_set:
        return "clean"
    if row_key in cand_set:
        return "candidate"
    return "flagged"


def build_effect_scale_map(report_path: Path) -> Dict[Tuple[str, str], Dict[str, float]]:
    if not report_path.exists():
        return {}
    df = pd.read_csv(report_path, sep="\t")
    df["trait"] = df["trait"].astype(str)
    df["ancestry"] = df["ancestry"].astype(str)
    df["p_score_raw"] = pd.to_numeric(df.get("p_score_raw"), errors="coerce")
    df["P_mismatch_raw_pct"] = pd.to_numeric(df.get("P_mismatch_raw_pct"), errors="coerce")
    out: Dict[Tuple[str, str], Dict[str, float]] = {}
    for _, row in df.iterrows():
        key = (row["trait"], row["ancestry"])
        out[key] = {
            "p_score_raw": row.get("p_score_raw"),
            "p_mismatch_raw_pct": row.get("P_mismatch_raw_pct"),
        }
    return out


def add_notes(row: pd.Series) -> str:
    notes = []
    for anc_prefix in ("eur_", "afr_"):
        qc_flag = str(row.get(f"{anc_prefix}qc_flag", "") or "")
        n_common = row.get(f"{anc_prefix}n_common_snps")
        if "LOW_OVERLAP" in qc_flag:
            if pd.notna(n_common):
                notes.append(f"{anc_prefix.upper()}LOW_OVERLAP (n={int(n_common)})")
            else:
                notes.append(f"{anc_prefix.upper()}LOW_OVERLAP")
        if "LOW_LD" in qc_flag:
            notes.append(f"{anc_prefix.upper()}LOW_LD")
        if "LOW_N" in qc_flag:
            notes.append(f"{anc_prefix.upper()}LOW_N")
        if "UNSTABLE_EFFECT_SCALE" in qc_flag:
            notes.append(f"{anc_prefix.upper()}EFFECT_SCALE_MISMATCH")
    if row.get("base_region") == "APOE_19q13":
        notes.append("APOE candidate; LD-heavy locus")
    return "; ".join(dict.fromkeys(notes))


def trait_pair_parts(tp: str) -> Tuple[str, str]:
    parts = tp.split("__")
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", ""


def main() -> None:
    args = parse_args()
    cand_path = Path(args.candidate)
    clean_path = Path(args.clean)
    if not cand_path.exists():
        raise SystemExit(f"Missing candidate H4 table: {cand_path}")
    if not clean_path.exists():
        raise SystemExit(f"Missing clean H4 table: {clean_path}")

    cand = pd.read_csv(cand_path, sep="\t")
    clean = pd.read_csv(clean_path, sep="\t")

    cand["PP.H4"] = pd.to_numeric(cand.get("PP.H4"), errors="coerce")
    cand["PP.H3"] = pd.to_numeric(cand.get("PP.H3"), errors="coerce")
    cand["trait_pair"] = cand["trait_a"].astype(str) + "__" + cand["trait_b"].astype(str)
    clean["trait_pair"] = clean["trait_a"].astype(str) + "__" + clean["trait_b"].astype(str)

    eur = cand[cand["ancestry"] == "EUR"].copy()
    afr = cand[cand["ancestry"] == "AFR"].copy()

    eur = rename_cols(eur, "eur_")
    eur["trait_pair"] = eur["trait_a"].astype(str) + "__" + eur["trait_b"].astype(str)
    eur = eur.drop(columns=["trait_a", "trait_b"])

    afr = rename_cols(afr, "afr_")
    afr["trait_pair"] = afr["trait_a"].astype(str) + "__" + afr["trait_b"].astype(str)
    afr = afr.drop(columns=["trait_a", "trait_b"])

    merged = pd.merge(
        eur,
        afr,
        on=["base_region", "trait_pair"],
        how="outer",
    )

    clean_keys = set(
        zip(clean["base_region"], clean["trait_pair"], clean["ancestry"])
    )
    cand_keys = set(
        zip(cand["base_region"], cand["trait_pair"], cand["ancestry"])
    )

    merged["eur_pair_qc_class"] = merged.apply(
        lambda r: qc_class(
            (r["base_region"], r["trait_pair"], "EUR"), clean_keys, cand_keys
        ),
        axis=1,
    )
    merged["afr_pair_qc_class"] = merged.apply(
        lambda r: qc_class(
            (r["base_region"], r["trait_pair"], "AFR"), clean_keys, cand_keys
        ),
        axis=1,
    )

    merged["eur_pp_class"] = merged.apply(
        lambda r: pp_class(
            pd.to_numeric(r.get("eur_PP.H3"), errors="coerce"),
            pd.to_numeric(r.get("eur_PP.H4"), errors="coerce"),
        ),
        axis=1,
    )
    merged["afr_pp_class"] = merged.apply(
        lambda r: pp_class(
            pd.to_numeric(r.get("afr_PP.H3"), errors="coerce"),
            pd.to_numeric(r.get("afr_PP.H4"), errors="coerce"),
        ),
        axis=1,
    )

    effect_map = build_effect_scale_map(Path(args.effect_scale))

    eur_median_a = []
    eur_median_b = []
    eur_tail_a = []
    eur_tail_b = []
    afr_median_a = []
    afr_median_b = []
    afr_tail_a = []
    afr_tail_b = []

    for _, row in merged.iterrows():
        trait_a, trait_b = trait_pair_parts(row["trait_pair"])
        eur_a = effect_map.get((trait_a, "EUR"), {})
        eur_b = effect_map.get((trait_b, "EUR"), {})
        afr_a = effect_map.get((trait_a, "AFR"), {})
        afr_b = effect_map.get((trait_b, "AFR"), {})
        eur_median_a.append(eur_a.get("p_score_raw"))
        eur_median_b.append(eur_b.get("p_score_raw"))
        eur_tail_a.append(eur_a.get("p_mismatch_raw_pct"))
        eur_tail_b.append(eur_b.get("p_mismatch_raw_pct"))
        afr_median_a.append(afr_a.get("p_score_raw"))
        afr_median_b.append(afr_b.get("p_score_raw"))
        afr_tail_a.append(afr_a.get("p_mismatch_raw_pct"))
        afr_tail_b.append(afr_b.get("p_mismatch_raw_pct"))

    merged["eur_p_median_mismatch_traitA"] = eur_median_a
    merged["eur_p_median_mismatch_traitB"] = eur_median_b
    merged["eur_p_tail_mismatch_traitA"] = eur_tail_a
    merged["eur_p_tail_mismatch_traitB"] = eur_tail_b
    merged["afr_p_median_mismatch_traitA"] = afr_median_a
    merged["afr_p_median_mismatch_traitB"] = afr_median_b
    merged["afr_p_tail_mismatch_traitA"] = afr_tail_a
    merged["afr_p_tail_mismatch_traitB"] = afr_tail_b

    merged["notes"] = merged.apply(add_notes, axis=1)

    merged["max_pp_h4"] = merged[["eur_PP.H4", "afr_PP.H4"]].max(axis=1, skipna=True)
    merged["ancestries_present"] = merged.apply(
        lambda r: ";".join(
            [label for label, val in (("EUR", r.get("eur_PP.H4")), ("AFR", r.get("afr_PP.H4"))) if pd.notna(val)]
        ),
        axis=1,
    )
    merged = merged.sort_values("max_pp_h4", ascending=False)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
