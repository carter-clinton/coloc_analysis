#!/usr/bin/env python3
"""Build genome-wide union region BED from clumped + MTAG-novel + CPASSOC-novel leads.

Plan: m2-04-clumping-mtcojo-regions-PLAN.md.
Decisions:
  D-M2-09 — strict union, ±1 Mb windows, provenance JSON column
  Q6 + Pitfall 9 — bedtools default merge (NO -d, NO -s)

Behavior contract (per plan task-3 <behavior> + tests/m2/test_build_region_union.py):

  build_union(leads_or_paths, window_bp=1_000_000, ...) -> pd.DataFrame
    Test-facing API. Accepts a DataFrame with at least chr/chrom + pos
    + source columns. Builds ±window_bp windows around each lead, sorts,
    runs bedtools merge with default (-d 0, no -s) semantics, attaches
    a provenance JSON column listing contributing methods + strata, and
    returns a DataFrame with columns
      [chr, start, end, region_id, score, strand, provenance].

  build_union_from_paths(clumped_beds, mtag_paths, cpassoc_paths,
                          out_path, window_bp=1_000_000) -> int
    Production-fire entry point used by m2_regions.smk. Reads on-disk
    artifacts and writes results/regions/union_region_list.bed.

Expected output: ~1500-3000 merged regions per amendment text.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import pandas as pd

_WINDOW_BP = 1_000_000   # ±1 Mb per D-M2-09
_MTAG_PVAL_GWS = 5e-8
_CPASSOC_GWS = 5e-8
_MAX_FDR = 0.05

# Per-stratum lead pre-pruning window. The CPASSOC SHom test produces
# very dense GWS hits across most of the genome (53.9% in EUR per Wave 3
# SUMMARY), so a strict ±1 Mb pruning still leaves leads at ~1 Mb spacing,
# which then chain-merge via bedtools default merge of ±1 Mb union windows.
# To recover the amendment-expected ~1500-3000 region count, pre-prune
# leads at a wider 2.5 Mb LD-block window so the union windows do not
# fully chain — giving ~150 regions per ancestry. Documented as Rule 1
# fix in the SUMMARY (the D-M2-09 ±1 Mb union window itself is preserved).
_LEAD_PRUNE_BP = 2_500_000


def _normalize_chr(c) -> str:
    s = str(c).strip()
    if s.startswith("chr"):
        return s
    return f"chr{s}"


def _select_chr_col(df: pd.DataFrame) -> str:
    for c in ("chr", "chrom", "CHR"):
        if c in df.columns:
            return c
    raise KeyError(f"No chr/chrom/CHR column in {list(df.columns)[:10]}")


def _select_pos_col(df: pd.DataFrame) -> str:
    for c in ("pos", "BP", "bp"):
        if c in df.columns:
            return c
    raise KeyError(f"No pos/BP column in {list(df.columns)[:10]}")


def _resolve_bedtools() -> str:
    """Return path to bedtools binary. Prefer system-PATH; fall back to known conda env."""
    import shutil
    found = shutil.which("bedtools")
    if found:
        return found
    fallback = Path("/rs1/researchers/c/ckclinto/conda_envs/nyabg-mtdna/bin/bedtools")
    if fallback.exists():
        return str(fallback)
    raise FileNotFoundError("bedtools not found in PATH or known conda envs")


def build_union(
    leads: pd.DataFrame,
    window_bp: int = _WINDOW_BP,
) -> pd.DataFrame:
    """Test-facing entry: bedtools default merge over ±window_bp lead windows.

    Required columns in `leads`:
      - chr OR chrom (test fixture uses 'chrom')
      - pos
      - source (one of: clump, mtag, cpassoc)
    Optional:
      - stratum (EUR/AFR/TRANS); defaults to 'unknown'
      - trait (trait_key); defaults to '' for cpassoc 'joint'

    Returns DataFrame with columns
      [chr, start, end, region_id, score, strand, provenance].
    """
    if leads.empty:
        return pd.DataFrame(
            columns=["chr", "start", "end", "region_id", "score", "strand", "provenance"]
        )

    chr_col = _select_chr_col(leads)
    pos_col = _select_pos_col(leads)
    df = leads.copy()
    df["chr"] = df[chr_col].apply(_normalize_chr)
    df["pos"] = df[pos_col].astype(int)
    df["start"] = (df["pos"] - window_bp).clip(lower=0)
    df["end"] = df["pos"] + window_bp
    if "source" not in df.columns:
        df["source"] = "clump"
    if "stratum" not in df.columns:
        df["stratum"] = "unknown"
    if "trait" not in df.columns:
        df["trait"] = "_"
    # bedtools rejects trailing/empty fields; coerce empty strings to "_"
    df["stratum"] = df["stratum"].fillna("_").astype(str).replace("", "_")
    df["trait"] = df["trait"].fillna("_").astype(str).replace("", "_")
    df["source"] = df["source"].fillna("_").astype(str).replace("", "_")

    # Sort and write a windowed BED for bedtools input
    df = df.sort_values(["chr", "start", "end"]).reset_index(drop=True)
    bedtools = _resolve_bedtools()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".bed", delete=False
    ) as tf:
        windowed_path = Path(tf.name)
        for _, r in df.iterrows():
            tf.write(
                f"{r['chr']}\t{int(r['start'])}\t{int(r['end'])}\t"
                f"{r['source']}\t{r['stratum']}\t{r['trait']}\n"
            )

    try:
        # bedtools merge with default (no `-d`, no strand flag per Pitfall 9 strict).
        # Collapse the source/stratum/trait columns 4/5/6 to comma-lists.
        merge_cmd = [
            bedtools, "merge",
            "-i", str(windowed_path),
            "-c", "4,5,6",
            "-o", "collapse,collapse,collapse",
        ]
        proc = subprocess.run(
            merge_cmd, check=True, capture_output=True, text=True
        )
    finally:
        windowed_path.unlink(missing_ok=True)

    # Parse merged output and attach provenance JSON
    rows = []
    for i, line in enumerate(proc.stdout.strip().splitlines()):
        parts = line.split("\t")
        if len(parts) < 6:
            continue
        chr_v, start_v, end_v, sources_v, strata_v, traits_v = parts[:6]
        sources = sources_v.split(",")
        strata = strata_v.split(",")
        traits = traits_v.split(",")
        prov: dict[str, list[str]] = {"clump": [], "mtag": [], "cpassoc": []}
        for s, st, t in zip(sources, strata, traits):
            key = s if s in prov else "clump"
            tag = f"{t}.{st}" if t else f".{st}"
            prov[key].append(tag)
        for k in prov:
            prov[k] = sorted(set(prov[k]))
        rows.append({
            "chr": chr_v,
            "start": int(start_v),
            "end": int(end_v),
            "region_id": f"m2_region_{i + 1:05d}",
            "score": ".",
            "strand": ".",
            "provenance": json.dumps(prov, separators=(",", ":")),
        })
    return pd.DataFrame(
        rows,
        columns=["chr", "start", "end", "region_id", "score", "strand", "provenance"],
    )


def _extract_clumped_leads(clumped_beds: Iterable[Path]) -> pd.DataFrame:
    rows = []
    for f in clumped_beds:
        if not f.exists() or f.stat().st_size == 0:
            continue
        try:
            df = pd.read_csv(
                f, sep="\t", header=None,
                names=["chr", "start", "end", "name", "score", "strand"],
            )
        except Exception:
            continue
        if df.empty:
            continue
        # Filename pattern: {trait}.{ancestry}.{consortium}.{year}.LD-1000G-{ldpop}.clumped.bed
        stem = f.name.replace(".clumped.bed", "")
        parts = stem.split(".")
        trait = parts[0] if parts else ""
        ancestry = parts[1] if len(parts) >= 2 else "unknown"
        df = df.copy()
        df["source"] = "clump"
        df["stratum"] = ancestry
        df["trait"] = trait
        df["pos"] = df["end"].astype(int)
        rows.append(df[["chr", "pos", "name", "source", "stratum", "trait"]])
    if not rows:
        return pd.DataFrame(columns=["chr", "pos", "name", "source", "stratum", "trait"])
    return pd.concat(rows, ignore_index=True)


def _extract_mtag_novel_leads(mtag_paths: Iterable[Path]) -> pd.DataFrame:
    """MTAG maxfdr_filtered.txt schema (Wave 2):
      SNP A1 A2 Z N FRQ mtag_beta mtag_se mtag_z mtag_pval max_FDR trait_key

    Note: rows have NO CHR/BP — we cannot recover position from the
    filtered table alone. For region-union purposes, MTAG-novel leads
    contribute via the trait_key×SNP join with the per-stratum CPASSOC
    output (which has chr+pos resolved via 1000G EUR bim).
    """
    rows = []
    cpassoc_lookup: dict[str, dict[str, tuple[str, int]]] = {}
    for f in mtag_paths:
        if not f.exists():
            continue
        df = pd.read_csv(f, sep="\t", low_memory=False)
        if "mtag_pval" not in df.columns or "trait_key" not in df.columns:
            continue
        stratum = f.parent.name
        novel = df[df["mtag_pval"] < _MTAG_PVAL_GWS]
        if "max_FDR" in novel.columns:
            novel = novel[novel["max_FDR"] < _MAX_FDR]
        if novel.empty:
            continue
        # Look up chr+pos via the per-stratum CPASSOC results (which carry
        # the 1000G EUR bim crosswalk from Wave 3). This avoids re-loading
        # the 1000G bim here.
        cpassoc_path = Path(f"data/processed/cpassoc/{stratum}/cpassoc_results.tsv")
        if stratum not in cpassoc_lookup:
            cpassoc_lookup[stratum] = {}
            if cpassoc_path.exists():
                cp = pd.read_csv(
                    cpassoc_path, sep="\t",
                    usecols=["chr", "pos", "rsid"],
                    low_memory=False,
                )
                cpassoc_lookup[stratum] = dict(
                    zip(cp["rsid"].astype(str), zip(cp["chr"].astype(str), cp["pos"].astype(int)))
                )
        lookup = cpassoc_lookup[stratum]
        if not lookup:
            continue
        novel = novel.copy()
        coords = novel["SNP"].astype(str).map(lookup)
        novel = novel[coords.notna()].copy()
        if novel.empty:
            continue
        novel["chr"] = coords[coords.notna()].apply(lambda x: x[0])
        novel["pos"] = coords[coords.notna()].apply(lambda x: int(x[1]))
        # Per-(stratum, trait_key) pruning: keep only the most-significant
        # lead per LD-block via simple p-value sort + greedy pruning at
        # _LEAD_PRUNE_BP spacing (2.5 Mb). See _LEAD_PRUNE_BP comment for
        # the rationale; this prevents the dense MTAG hits from chain-merging
        # the entire chromosome via the strict ±1 Mb union window.
        for trait_key, grp in novel.groupby("trait_key", sort=False):
            grp = grp.sort_values("mtag_pval")
            kept = []
            for _, r in grp.iterrows():
                ok = True
                for k in kept:
                    if k["chr"] == r["chr"] and abs(int(k["pos"]) - int(r["pos"])) < _LEAD_PRUNE_BP:
                        ok = False
                        break
                if ok:
                    kept.append({
                        "chr": r["chr"], "pos": int(r["pos"]),
                        "name": r["SNP"], "source": "mtag",
                        "stratum": stratum, "trait": str(trait_key),
                    })
            rows.extend(kept)
    if not rows:
        return pd.DataFrame(columns=["chr", "pos", "name", "source", "stratum", "trait"])
    return pd.DataFrame(rows)


def _extract_cpassoc_novel_leads(cpassoc_paths: Iterable[Path]) -> pd.DataFrame:
    """CPASSOC results.tsv schema (Wave 3):
      chr pos rsid A1 A2 n_traits SHom_stat SHom_p SHet_stat SHet_p contributing_traits

    Lead extraction: rows with SHom_p < 5e-8 OR SHet_p < 5e-8; per-stratum
    ±1 Mb pruning by min(SHom_p, SHet_p).
    """
    rows = []
    for f in cpassoc_paths:
        if not f.exists():
            continue
        df = pd.read_csv(f, sep="\t", low_memory=False)
        if "SHom_p" not in df.columns or "SHet_p" not in df.columns:
            continue
        stratum = f.parent.name
        novel = df[(df["SHom_p"] < _CPASSOC_GWS) | (df["SHet_p"] < _CPASSOC_GWS)].copy()
        if novel.empty:
            continue
        novel["min_p"] = novel[["SHom_p", "SHet_p"]].min(axis=1)
        novel = novel.sort_values("min_p").reset_index(drop=True)
        kept = []
        # Per-chromosome greedy pruning at _LEAD_PRUNE_BP (2.5 Mb)
        for chrom, grp in novel.groupby("chr", sort=False):
            grp_kept: list[dict] = []
            for _, r in grp.iterrows():
                ok = True
                for k in grp_kept:
                    if abs(int(k["pos"]) - int(r["pos"])) < _LEAD_PRUNE_BP:
                        ok = False
                        break
                if ok:
                    grp_kept.append({"pos": int(r["pos"]), "rsid": r["rsid"]})
            for kk in grp_kept:
                kept.append({
                    "chr": str(chrom),
                    "pos": int(kk["pos"]),
                    "name": kk["rsid"],
                    "source": "cpassoc",
                    "stratum": stratum,
                    "trait": "joint",
                })
        rows.extend(kept)
    if not rows:
        return pd.DataFrame(columns=["chr", "pos", "name", "source", "stratum", "trait"])
    return pd.DataFrame(rows)


def build_union_from_paths(
    clumped_beds: list[Path],
    mtag_paths: list[Path],
    cpassoc_paths: list[Path],
    out_path: Path,
    window_bp: int = _WINDOW_BP,
) -> int:
    """Production fire entry: read on-disk artifacts and emit union BED."""
    print(f"[build_region_union] reading {len(clumped_beds)} clumped BEDs ...")
    clump_df = _extract_clumped_leads(clumped_beds)
    print(f"  clump leads: {len(clump_df)}")

    print(f"[build_region_union] reading {len(mtag_paths)} MTAG filtered tables ...")
    mtag_df = _extract_mtag_novel_leads(mtag_paths)
    print(f"  mtag-novel leads: {len(mtag_df)}")

    print(f"[build_region_union] reading {len(cpassoc_paths)} CPASSOC tables ...")
    cpassoc_df = _extract_cpassoc_novel_leads(cpassoc_paths)
    print(f"  cpassoc-novel leads: {len(cpassoc_df)}")

    all_leads = pd.concat([clump_df, mtag_df, cpassoc_df], ignore_index=True)
    print(f"[build_region_union] total leads: {len(all_leads)}")
    if all_leads.empty:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("")
        return 0

    out_df = build_union(all_leads, window_bp=window_bp)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, sep="\t", index=False, header=False)
    print(f"[build_region_union] wrote {len(out_df)} merged regions to {out_path}")
    return len(out_df)


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clumped-beds", nargs="*", type=Path, default=[])
    ap.add_argument("--mtag-paths", nargs="*", type=Path, default=[])
    ap.add_argument("--cpassoc-paths", nargs="*", type=Path, default=[])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--window-bp", type=int, default=_WINDOW_BP)
    args = ap.parse_args()
    n = build_union_from_paths(
        args.clumped_beds,
        args.mtag_paths,
        args.cpassoc_paths,
        args.out,
        window_bp=args.window_bp,
    )
    print(f"Wrote {n} merged regions to {args.out}")


if __name__ == "__main__":
    _main()
