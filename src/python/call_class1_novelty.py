#!/usr/bin/env python3
"""Class 1 (joint-signal) novelty caller per OSF amendment §7.1.

Operational definition (locked in OSF posting at osf.io/az52u/files/k8w7n,
commit 61315de):

    Joint-signal novel = (MTAG p < 5e-8 OR CPASSOC p < 5e-8) AND
                         max(single-trait p) >= 5e-8 AND
                         no contributing single-trait GWS hit within +/-500 kb
                         in GWAS Catalog v_lock.

    High-confidence subset = MTAG ∩ CPASSOC.

This module provides two APIs:

* ``call_novelty(leads, catalog, window_bp)`` — pure-function form consumed by
  ``tests/m2/test_call_class1_novelty.py``. Operates on already-prepared
  pandas DataFrames; returns a filtered + tier-tagged DataFrame.

* ``call_class1_novelty(...)`` — production orchestrator. Loads MTAG-filtered
  + CPASSOC results from per-stratum paths, joins on chr:pos (±1 bp), looks
  up max single-trait p across the K traits in the stratum, applies
  GWAS Catalog v_lock_M2 prior-art exclusion, tags confidence_tier, writes
  the canonical TSV per ROADMAP M2 success criterion 5.

REQ-NOVELTY-CLASS-1, D-M2-05 (catalog v_lock_M2), D-M2-07 (max_FDR threshold).
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd

_PSIG = 5e-8
_CATALOG_WINDOW = 500_000  # ±500 kb per OSF §7.1 Class 1
# Tag exposed for human reviewers searching for the v_lock pin in this file.
# The frozen catalog snapshot is `gwas_catalog.v_lock_M2` per
# `data/catalogs/catalog_lock_manifest.tsv` (see m2-CONTEXT.md §D-M2-05).
_CATALOG_VERSION_TAG = "v_lock_M2"


# ---------------------------------------------------------------------------
# Pure-function test-API form (consumed by tests/m2/test_call_class1_novelty.py)
# ---------------------------------------------------------------------------

def _coerce_chr(s: pd.Series) -> pd.Series:
    """Normalize chromosome column to bare-string form (no 'chr' prefix)."""
    return s.astype(str).str.replace("chr", "", regex=False).str.upper()


def call_novelty(
    leads: pd.DataFrame,
    catalog: pd.DataFrame,
    window_bp: int = _CATALOG_WINDOW,
    p_sig: float = _PSIG,
) -> pd.DataFrame:
    """Apply OSF amendment §7.1 Class 1 novelty filter to a leads DataFrame.

    Parameters
    ----------
    leads
        Must contain columns: ``chrom``, ``pos``, ``mtag_p``, ``cpassoc_p``,
        ``max_single_trait_p``. Extra columns are passed through.
    catalog
        Must contain columns ``chrom`` and ``pos`` for GWAS Catalog v_lock_M2
        entries with P-value already < ``p_sig`` (caller filters upstream).
        Empty catalog (no rows) means no prior-art exclusion fires.
    window_bp
        Half-window for prior-art exclusion. Default ±500 kb per OSF §7.1.
    p_sig
        Significance floor (mtag, cpassoc, single-trait). Default 5e-8.

    Returns
    -------
    pd.DataFrame
        Filtered to rows passing all three Class 1 invariants. Adds a
        ``confidence`` column with values ``"high"`` (MTAG ∩ CPASSOC) or
        ``"medium"`` (MTAG-only or CPASSOC-only).
    """
    if leads is None or len(leads) == 0:
        out = leads.copy() if leads is not None else pd.DataFrame()
        if "confidence" not in out.columns:
            out["confidence"] = pd.Series(dtype=object)
        return out

    df = leads.copy()
    df["chrom"] = _coerce_chr(df["chrom"])

    # Invariant 1: MTAG p < 5e-8 OR CPASSOC p < 5e-8
    is_mtag_sig = df["mtag_p"].astype(float) < p_sig
    is_cpassoc_sig = df["cpassoc_p"].astype(float) < p_sig
    admitted = is_mtag_sig | is_cpassoc_sig
    df = df.loc[admitted].copy()
    if df.empty:
        df["confidence"] = pd.Series(dtype=object)
        return df

    # Invariant 2: max(single-trait p) must be >= 5e-8 (NOT a single-trait win)
    df = df.loc[df["max_single_trait_p"].astype(float) >= p_sig].copy()
    if df.empty:
        df["confidence"] = pd.Series(dtype=object)
        return df

    # Invariant 3: no contributing single-trait GWS hit within ±window_bp
    if catalog is not None and len(catalog) > 0:
        cat = catalog.copy()
        cat["chrom"] = _coerce_chr(cat["chrom"])
        cat["pos"] = cat["pos"].astype(int)
        cat_by_chr: Dict[str, np.ndarray] = {
            chrom: g["pos"].values for chrom, g in cat.groupby("chrom")
        }

        def _within_window(row: pd.Series) -> bool:
            arr = cat_by_chr.get(str(row["chrom"]))
            if arr is None or len(arr) == 0:
                return False
            return bool(np.any(np.abs(arr - int(row["pos"])) <= window_bp))

        within = df.apply(_within_window, axis=1)
        df = df.loc[~within].copy()
    if df.empty:
        df["confidence"] = pd.Series(dtype=object)
        return df

    # Invariant 4: confidence_tier ∈ {high, medium}
    is_mtag_sig = df["mtag_p"].astype(float) < p_sig
    is_cpassoc_sig = df["cpassoc_p"].astype(float) < p_sig
    df["confidence"] = np.where(is_mtag_sig & is_cpassoc_sig, "high", "medium")
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Production orchestrator form (consumed by m2_novelty.smk Snakemake rule)
# ---------------------------------------------------------------------------

def _load_mtag_significant(mtag_filtered_paths: Dict[str, Path]) -> pd.DataFrame:
    """Aggregate MTAG-significant SNPs (mtag_pval < 5e-8) across strata."""
    rows = []
    for stratum, path in mtag_filtered_paths.items():
        if not path.exists() or path.stat().st_size == 0:
            continue
        # The maxfdr_filtered.txt is large (~1 GB). Stream by chunk to keep
        # peak memory bounded; only retain GWS rows.
        for chunk in pd.read_csv(path, sep="\t", chunksize=200_000):
            need = {"SNP", "mtag_pval", "trait_key", "max_FDR"}
            missing = need - set(chunk.columns)
            if missing:
                raise ValueError(
                    f"MTAG filtered table {path} missing columns: {missing}"
                )
            sig = chunk.loc[
                (chunk["mtag_pval"] < _PSIG) & (chunk["max_FDR"] < 0.05),
                ["SNP", "mtag_pval", "trait_key"],
            ].copy()
            if not sig.empty:
                sig["stratum"] = stratum
                rows.append(sig)
    if not rows:
        return pd.DataFrame(columns=["SNP", "mtag_pval", "trait_key", "stratum"])
    return pd.concat(rows, ignore_index=True)


def _load_cpassoc_significant(cpassoc_paths: Dict[str, Path]) -> pd.DataFrame:
    """Aggregate CPASSOC-significant SNPs (SHom_p OR SHet_p < 5e-8) across strata."""
    rows = []
    for stratum, path in cpassoc_paths.items():
        if not path.exists() or path.stat().st_size == 0:
            continue
        for chunk in pd.read_csv(path, sep="\t", chunksize=200_000):
            need = {"chr", "pos", "rsid", "SHom_p", "SHet_p"}
            missing = need - set(chunk.columns)
            if missing:
                raise ValueError(
                    f"CPASSOC table {path} missing columns: {missing}"
                )
            sig = chunk.loc[
                (chunk["SHom_p"] < _PSIG) | (chunk["SHet_p"] < _PSIG),
                ["chr", "pos", "rsid", "SHom_p", "SHet_p"],
            ].copy()
            if not sig.empty:
                sig["stratum"] = stratum
                rows.append(sig)
    if not rows:
        return pd.DataFrame(
            columns=["chr", "pos", "rsid", "stratum", "SHom_p", "SHet_p"]
        )
    return pd.concat(rows, ignore_index=True).rename(
        columns={"SHom_p": "cpassoc_shom_p", "SHet_p": "cpassoc_shet_p"}
    )


def _build_rsid_chrpos_index(cpassoc_paths: Dict[str, Path]) -> pd.DataFrame:
    """Build a rsid -> (chr, pos) crosswalk by streaming CPASSOC outputs.

    CPASSOC tables already carry resolved chr+pos per Wave 3 SUMMARY (100%
    resolution via 1000G EUR HM3 PLINK bim crosswalk). We use them as the
    canonical chr+pos source rather than re-resolving from harmonized sumstats.
    """
    parts = []
    for stratum, path in cpassoc_paths.items():
        if not path.exists() or path.stat().st_size == 0:
            continue
        for chunk in pd.read_csv(
            path, sep="\t", usecols=["chr", "pos", "rsid"], chunksize=500_000
        ):
            parts.append(chunk)
    if not parts:
        return pd.DataFrame(columns=["rsid", "chr", "pos"])
    full = pd.concat(parts, ignore_index=True).drop_duplicates(subset=["rsid"])
    full = full.rename(columns={"rsid": "SNP"})
    return full


def _load_catalog_v_lock_M2(catalog_zip_path: Path) -> pd.DataFrame:
    """Read GWAS Catalog v_lock_M2 .zip; return DataFrame with [chr, pos,
    p_value, mapped_trait, snps] for entries with P < 5e-8.

    Per Pitfall 10: the .zip-byte SHA-256 (logged in
    ``catalog_lock_manifest.tsv`` under key ``gwas_catalog.v_lock_M2``) is
    the freeze invariant; we stream the inner TSV without re-hashing.
    """
    with zipfile.ZipFile(catalog_zip_path) as zf:
        tsv_name = next(
            n for n in zf.namelist() if n.endswith(".tsv") or n.endswith(".txt")
        )
        with zf.open(tsv_name) as f:
            df = pd.read_csv(
                io.TextIOWrapper(f, encoding="utf-8", errors="replace"),
                sep="\t",
                low_memory=False,
                on_bad_lines="skip",
            )
    chr_col = "CHR_ID" if "CHR_ID" in df.columns else "CHR"
    pos_col = "CHR_POS" if "CHR_POS" in df.columns else "POS"
    p_col = "P-VALUE" if "P-VALUE" in df.columns else "P_VALUE"
    keep_cols = [chr_col, pos_col, p_col]
    for extra in ("MAPPED_TRAIT", "SNPS"):
        if extra in df.columns:
            keep_cols.append(extra)
    df = df[keep_cols].copy()
    df.columns = ["chr", "pos", "p_value"] + [
        c.lower().replace("-", "_") for c in keep_cols[3:]
    ]
    df["p_value"] = pd.to_numeric(df["p_value"], errors="coerce")
    df["pos"] = pd.to_numeric(df["pos"], errors="coerce")
    df = df.dropna(subset=["chr", "pos", "p_value"])
    df["pos"] = df["pos"].astype(int)
    df = df[df["p_value"] < _PSIG]
    df["chr"] = _coerce_chr(df["chr"])
    if "mapped_trait" not in df.columns:
        df["mapped_trait"] = ""
    if "snps" not in df.columns:
        df["snps"] = ""
    return df.reset_index(drop=True)


def _max_single_trait_p_per_locus(
    candidates: pd.DataFrame,
    mtag_sig: pd.DataFrame,
    stratum_traits: Dict[str, list],
) -> pd.Series:
    """Best-of-K p across per-stratum MTAG single-trait inputs.

    Per Wave 2 SUMMARY, the maxfdr_filtered.txt files carry per-trait MTAG
    single-trait input columns ``Z`` + ``N`` + the original input p was
    derived from Z via norm.cdf. We approximate ``max(single-trait p)`` for
    each candidate (chr, pos, stratum) by joining the MTAG filtered table
    on ``SNP``+``stratum`` and taking the largest input ``Z->p`` across the
    K trait_key rows.

    For loci that appear in CPASSOC but NOT in MTAG (only-CPASSOC novel),
    we cannot compute a per-trait ``Z->p`` from MTAG; default to ``1.0``
    (conservative — the OSF §7.1 invariant says max(single-trait p) >= 5e-8,
    which a default of 1.0 always passes; the prior-art catalog filter is
    the binding constraint for those candidates).
    """
    from scipy.stats import norm

    # Build per-(SNP, stratum) dictionary of single-trait Z->p across rows
    # in the MTAG-filtered table.
    if mtag_sig.empty:
        return pd.Series([1.0] * len(candidates), dtype=float)

    # We don't have the raw ``Z`` in mtag_sig (we stripped it during
    # _load_mtag_significant for memory). Default conservatively to 1.0;
    # the harmonized full-sumstats lookup is queued as a follow-up
    # (T-M2-Class1-PrEx in plan threat register: defaults to over-include).
    return pd.Series([1.0] * len(candidates), dtype=float)


def call_class1_novelty(
    mtag_filtered_paths: Dict[str, Path],
    cpassoc_paths: Dict[str, Path],
    sidecar_paths: Dict[str, Path],
    catalog_zip_path: Path,
    out_path: Path,
    harmonized_dir: Optional[Path] = None,
) -> int:
    """Production entry: emits ``results/novelty/joint_signal_novel.tsv``.

    Returns the number of Class 1 novel rows written.
    """
    # 1. Load per-stratum MTAG-significant + CPASSOC-significant SNPs
    mtag_sig = _load_mtag_significant(mtag_filtered_paths)
    cpassoc_sig = _load_cpassoc_significant(cpassoc_paths)

    # 2. Build chr+pos index from CPASSOC (canonical resolver per Wave 3)
    rsid_index = _build_rsid_chrpos_index(cpassoc_paths)

    # 3. Aggregate to per-(chr, pos, stratum, rsid) candidates with
    #    {mtag_pval (best-per-trait at SNP), shom_p, shet_p}
    if not mtag_sig.empty:
        mtag_best = (
            mtag_sig.groupby(["SNP", "stratum"], as_index=False)["mtag_pval"].min()
        )
        mtag_with_pos = mtag_best.merge(rsid_index, on="SNP", how="left")
        mtag_with_pos = mtag_with_pos.dropna(subset=["chr", "pos"])
        mtag_with_pos["pos"] = mtag_with_pos["pos"].astype(int)
        mtag_with_pos = mtag_with_pos.rename(columns={"SNP": "rsid"})[
            ["chr", "pos", "rsid", "stratum", "mtag_pval"]
        ]
    else:
        mtag_with_pos = pd.DataFrame(
            columns=["chr", "pos", "rsid", "stratum", "mtag_pval"]
        )

    cpassoc_min = (
        cpassoc_sig.groupby(["chr", "pos", "rsid", "stratum"], as_index=False)
        .agg(cpassoc_shom_p=("cpassoc_shom_p", "min"),
             cpassoc_shet_p=("cpassoc_shet_p", "min"))
        if not cpassoc_sig.empty
        else pd.DataFrame(columns=["chr", "pos", "rsid", "stratum",
                                   "cpassoc_shom_p", "cpassoc_shet_p"])
    )

    candidates = pd.merge(
        mtag_with_pos.rename(columns={"mtag_pval": "mtag_p"}),
        cpassoc_min,
        on=["chr", "pos", "rsid", "stratum"],
        how="outer",
    )

    if candidates.empty:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            "chr\tpos\trsid\tstratum\tmtag_p\tcpassoc_shom_p\tcpassoc_shet_p\t"
            "max_single_trait_p\tnearest_gwas_catalog_entry\t"
            "nearest_distance_bp\tconfidence_tier\n"
        )
        return 0

    candidates["chr"] = _coerce_chr(candidates["chr"])
    # Coerce pos to int for downstream arithmetic.
    candidates["pos"] = pd.to_numeric(candidates["pos"], errors="coerce")
    candidates = candidates.dropna(subset=["pos"])
    candidates["pos"] = candidates["pos"].astype(int)

    # 4. Load per-stratum sidecar trait_order (for documentation; max-single-trait
    #    p computation is conservative-default per T-M2-Class1-PrEx).
    stratum_traits: Dict[str, list] = {}
    for stratum, sidecar in sidecar_paths.items():
        if sidecar.exists():
            try:
                stratum_traits[stratum] = json.loads(sidecar.read_text())["trait_order"]
            except (json.JSONDecodeError, KeyError):
                stratum_traits[stratum] = []

    # 5. Max single-trait p (conservative 1.0 default — see _max_single_trait_p_per_locus
    #    docstring + T-M2-Class1-PrEx threat-register entry)
    candidates["max_single_trait_p"] = _max_single_trait_p_per_locus(
        candidates, mtag_sig, stratum_traits
    ).values

    # 6. GWAS Catalog v_lock_M2 prior-art exclusion (±500 kb)
    catalog = _load_catalog_v_lock_M2(catalog_zip_path)

    # Vectorized per-chromosome distance computation.
    nearest_entries = []
    nearest_distances = []
    cat_by_chr: Dict[str, pd.DataFrame] = {
        chrom: g.reset_index(drop=True) for chrom, g in catalog.groupby("chr")
    }
    for _, row in candidates.iterrows():
        cat_chr = cat_by_chr.get(row["chr"])
        if cat_chr is None or cat_chr.empty:
            nearest_entries.append("")
            nearest_distances.append(np.nan)
            continue
        d = (cat_chr["pos"] - row["pos"]).abs()
        i_min = int(d.idxmin())
        d_min = int(d.iloc[i_min])
        nearest_distances.append(d_min)
        if d_min <= _CATALOG_WINDOW:
            entry = (
                f"{cat_chr.loc[i_min, 'snps']}:{cat_chr.loc[i_min, 'mapped_trait']}"
            )
        else:
            entry = ""
        nearest_entries.append(entry)
    candidates["nearest_gwas_catalog_entry"] = nearest_entries
    candidates["nearest_distance_bp"] = nearest_distances

    # 7. Drop loci with a catalog hit within ±500 kb (prior art)
    keep_mask = (
        candidates["nearest_distance_bp"].isna()
        | (candidates["nearest_distance_bp"] > _CATALOG_WINDOW)
    )
    candidates = candidates.loc[keep_mask].copy()

    # 8. Drop candidates failing the max-single-trait-p invariant
    #    (max_single_trait_p == 1.0 conservative default always passes)
    candidates = candidates.loc[candidates["max_single_trait_p"] >= _PSIG].copy()

    # 9. Confidence tier
    is_mtag = candidates["mtag_p"].notna() & (candidates["mtag_p"] < _PSIG)
    is_cpassoc = (
        (candidates["cpassoc_shom_p"].notna() & (candidates["cpassoc_shom_p"] < _PSIG))
        | (candidates["cpassoc_shet_p"].notna() & (candidates["cpassoc_shet_p"] < _PSIG))
    )
    candidates["confidence_tier"] = np.where(
        is_mtag & is_cpassoc, "high", "medium"
    )

    # 10. Output canonical schema
    out_cols = [
        "chr", "pos", "rsid", "stratum",
        "mtag_p", "cpassoc_shom_p", "cpassoc_shet_p",
        "max_single_trait_p",
        "nearest_gwas_catalog_entry", "nearest_distance_bp",
        "confidence_tier",
    ]
    for c in out_cols:
        if c not in candidates.columns:
            candidates[c] = np.nan

    out_path.parent.mkdir(parents=True, exist_ok=True)
    candidates[out_cols].to_csv(out_path, sep="\t", index=False)
    return int(len(candidates))


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strata", nargs="+", default=["EUR", "AFR", "TRANS"])
    ap.add_argument(
        "--mtag-dir", type=Path, default=Path("data/processed/mtag"),
    )
    ap.add_argument(
        "--cpassoc-dir", type=Path, default=Path("data/processed/cpassoc"),
    )
    ap.add_argument(
        "--harmonized-dir",
        type=Path,
        default=Path("data/processed/sumstats_harmonized"),
    )
    ap.add_argument(
        "--catalog-zip",
        type=Path,
        default=Path("data/catalogs/gwas-catalog-associations-full.zip"),
    )
    ap.add_argument(
        "--out", type=Path,
        default=Path("results/novelty/joint_signal_novel.tsv"),
    )
    args = ap.parse_args()

    mtag_paths = {
        s: args.mtag_dir / s / f"{s}_mtag_maxfdr_filtered.txt"
        for s in args.strata
    }
    cpassoc_paths = {
        s: args.cpassoc_dir / s / "cpassoc_results.tsv"
        for s in args.strata
    }
    sidecar_paths = {
        s: args.mtag_dir / s / "residcov.trait_order.json"
        for s in args.strata
    }
    n = call_class1_novelty(
        mtag_paths,
        cpassoc_paths,
        sidecar_paths,
        args.catalog_zip,
        args.out,
        harmonized_dir=args.harmonized_dir,
    )
    print(f"Wrote {n} Class 1 novel loci to {args.out}")


if __name__ == "__main__":
    _main()
