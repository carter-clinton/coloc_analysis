#!/usr/bin/env python3
import argparse
import csv
import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

DEFAULT_TABIX = "/rs1/researchers/c/ckclinto/conda_envs/snakemake/bin/tabix"


def resolve_tabix() -> str:
    tabix_bin = os.environ.get("TABIX_BIN")
    if tabix_bin:
        return tabix_bin
    found = shutil.which("tabix")
    if found:
        return found
    if os.path.exists(DEFAULT_TABIX):
        return DEFAULT_TABIX
    return "tabix"


TABIX_BIN = resolve_tabix()


def parse_args():
    parser = argparse.ArgumentParser(description="Create HyPrColoc manifest.")
    parser.add_argument("--harmonized", nargs="+", required=True)
    parser.add_argument("--regions", required=True)
    parser.add_argument("--tier3", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-shared", type=int, default=200)
    parser.add_argument("--min-shared-secondary", type=int, default=50)
    parser.add_argument(
        "--include-traits",
        default="",
        help="Comma-separated traits to consider (others are dropped).",
    )
    parser.add_argument(
        "--require-traits",
        default="",
        help="Comma-separated traits that must be present to form a group.",
    )
    parser.add_argument(
        "--secondary-loci",
        default="RAD50_IL13_5q31.1,HHEX_10q23",
        help="Comma-separated base regions eligible for secondary overlap threshold.",
    )
    parser.add_argument(
        "--secondary-ancestries",
        default="AFR",
        help="Comma-separated ancestries eligible for secondary overlap threshold.",
    )
    return parser.parse_args()


def load_region_metadata(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "parent_region" not in df.columns:
        df["parent_region"] = df["region_id"].str.split("__").str[0]
    df["parent_region"] = df["parent_region"].fillna(df["region_id"])
    df["chr"] = (
        df["chr"]
        .astype(str)
        .str.replace("^chr", "", regex=True)
        .str.replace("^CHR", "", regex=True)
    )
    df["start"] = pd.to_numeric(df["start"], errors="coerce")
    df["end"] = pd.to_numeric(df["end"], errors="coerce")
    return (
        df.groupby("parent_region")
        .agg({"chr": "first", "start": "min", "end": "max"})
        .rename_axis("base_region")
        .reset_index()
    )


def parse_trait_ancestry(path: str) -> Tuple[str, str]:
    name = Path(path).name
    tokens = name.split(".")
    if len(tokens) < 2:
        return "", ""
    return tokens[0], tokens[1]


def harmonized_index(paths: List[str]) -> Dict[Tuple[str, str], str]:
    idx = {}
    for path in paths:
        trait, ancestry = parse_trait_ancestry(path)
        if trait and ancestry:
            idx[(trait, ancestry)] = path
    return idx


def read_header(path: str) -> Optional[List[str]]:
    cmd = f"zcat -f {shlex.quote(path)} | head -n 1"
    try:
        output = subprocess.check_output(["bash", "-c", cmd], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not output:
        return None
    return output.split("\t")


def header_indices(header: Optional[List[str]]) -> Dict[str, int]:
    if not header:
        return {}
    return {col.upper(): idx for idx, col in enumerate(header)}


def variant_set(path: str, chrom: str, start: int, end: int, header_idx: Dict[str, int]) -> Set[str]:
    cmd = [TABIX_BIN, path, f"{chrom}:{start}-{end}"]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("tabix not found; set TABIX_BIN or install tabix.") from exc
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"tabix failed for {path}: {err}")
    output = proc.stdout
    if not output.strip():
        return set()

    chr_idx = header_idx["CHR"] if "CHR" in header_idx else header_idx.get("CHROM")
    pos_idx = header_idx["POS"] if "POS" in header_idx else header_idx.get("BP")
    snp_idx = None
    for name in ("SNP_ID", "SNPID", "RSID", "MARKERNAME", "ID"):
        if name in header_idx:
            snp_idx = header_idx[name]
            break

    ids = set()
    for row in csv.reader(output.splitlines(), delimiter="\t"):
        if not row:
            continue
        if row[0].startswith("#"):
            continue
        if chr_idx is not None and pos_idx is not None:
            if chr_idx < len(row) and pos_idx < len(row):
                chrom_val = row[chr_idx]
                if chrom_val.lower().startswith("chr"):
                    chrom_val = chrom_val[3:]
                ids.add(f"{chrom_val}:{row[pos_idx]}")
                continue
        if snp_idx is not None and snp_idx < len(row):
            snp = row[snp_idx]
            if snp:
                ids.add(snp)
    return ids


def main():
    args = parse_args()
    tier3 = pd.read_csv(args.tier3, sep="\t")
    if tier3.empty:
        pd.DataFrame().to_csv(args.output, sep="\t", index=False)
        return

    tier3["base_region"] = tier3["region_id"].astype(str).str.split("__").str[0]

    coords = load_region_metadata(Path(args.regions))
    coords_map = coords.set_index("base_region").to_dict("index")
    index = harmonized_index(args.harmonized)
    header_map = {path: header_indices(read_header(path)) for path in index.values()}
    secondary_loci = {item.strip() for item in args.secondary_loci.split(",") if item.strip()}
    secondary_ancestries = {item.strip() for item in args.secondary_ancestries.split(",") if item.strip()}
    include_traits = {item.strip() for item in args.include_traits.split(",") if item.strip()}
    require_traits = {item.strip() for item in args.require_traits.split(",") if item.strip()}

    rows = []
    for (base_region, ancestry), group in tier3.groupby(["base_region", "ancestry"]):
        traits = sorted(group["trait"].unique())
        if include_traits:
            traits = [t for t in traits if t in include_traits]
        if require_traits and not require_traits.issubset(set(traits)):
            continue
        if len(traits) < 3:
            continue
        coord = coords_map.get(base_region)
        if coord is None:
            continue
        chrom = str(coord["chr"])
        start = int(coord["start"])
        end = int(coord["end"])
        trait_paths = []
        snp_sets = []
        snps_by_trait = []
        for trait in traits:
            path = index.get((trait, ancestry))
            if not path:
                continue
            header_idx = header_map.get(path, {})
            snps = variant_set(path, chrom, start, end, header_idx)
            if not snps:
                continue
            trait_paths.append((trait, path))
            snp_sets.append(snps)
            snps_by_trait.append((trait, len(snps)))

        if len(trait_paths) < 3:
            continue

        shared = snp_sets[0].copy()
        for snps in snp_sets[1:]:
            shared &= snps
        n_shared = len(shared)

        if n_shared >= args.min_shared:
            status = "ready"
            overlap_mode = "primary"
        elif (
            ancestry in secondary_ancestries
            and base_region in secondary_loci
            and n_shared >= args.min_shared_secondary
        ):
            status = "ready_secondary"
            overlap_mode = "secondary"
        else:
            status = "low_overlap"
            overlap_mode = "low"
        rows.append(
            {
                "group_id": f"{base_region}__{ancestry}",
                "base_region": base_region,
                "ancestry": ancestry,
                "chr": chrom,
                "start": start,
                "end": end,
                "traits_included": ",".join([t for t, _ in trait_paths]),
                "n_traits": len(trait_paths),
                "n_shared_snps": n_shared,
                "status": status,
                "overlap_mode": overlap_mode,
                "paths": ";".join([f"{t}={p}" for t, p in trait_paths]),
                "nsnps_by_trait": ";".join([f"{t}={n}" for t, n in snps_by_trait]),
            }
        )

    manifest = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
