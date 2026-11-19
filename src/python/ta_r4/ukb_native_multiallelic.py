"""UKB 337k native panels with at most one variant per CHR:POS (DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1).

Applied to build_native's output (after the catalog allele filter). At a CHR:POS with 2+ variants, the single SNV
(one-base ACGT REF and ALT) is kept and the others dropped; with zero or 2+ SNVs every variant there is dropped.
Single-variant positions are untouched, indels included (no --snps-only).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ta_r4 import ukb337k_tiles

ACGT = frozenset("ACGT")
AUDIT_COLS = ["SNP_ID", "CHR", "POS", "REF", "ALT", "n_at_pos", "n_snv", "class", "action"]
STAT_KEYS = ("n_sites_multiallelic", "n_sites_kept_snv", "n_sites_dropped_all", "n_var_dropped_multiallelic")


def is_snv(ref, alt):
    return len(ref) == 1 and len(alt) == 1 and ref in ACGT and alt in ACGT


def resolve_multiallelic_positions(R, v):
    """(R_kept = R[keep][:, keep], v_kept, audit, stats); v_kept keeps the input order with a fresh index."""
    v = v.reset_index(drop=True)
    key = list(zip(v["CHR"].astype(str), v["POS"].astype(np.int64)))
    groups = {}
    for i, k in enumerate(key):
        groups.setdefault(k, []).append(i)
    keep = np.ones(len(v), dtype=bool)
    audit, st = [], dict.fromkeys(STAT_KEYS, 0)
    for rows in groups.values():
        if len(rows) < 2:
            continue
        snv = [i for i in rows if is_snv(v.at[i, "REF"], v.at[i, "ALT"])]
        cls = "one_snv" if len(snv) == 1 else ("no_snv" if not snv else "multi_snv")
        st["n_sites_multiallelic"] += 1
        st["n_sites_kept_snv" if cls == "one_snv" else "n_sites_dropped_all"] += 1
        for i in rows:
            kept = cls == "one_snv" and i == snv[0]
            keep[i] = kept
            audit.append({**{c: v.at[i, c] for c in ("SNP_ID", "CHR", "POS", "REF", "ALT")}, "n_at_pos": len(rows),
                          "n_snv": len(snv), "class": cls, "action": "kept_snv" if kept else "dropped"})
    st["n_var_dropped_multiallelic"] = int((~keep).sum())
    ix = np.flatnonzero(keep)
    R_kept = R if keep.all() else R[np.ix_(ix, ix)]
    return R_kept, v.iloc[ix].reset_index(drop=True), pd.DataFrame(audit, columns=AUDIT_COLS), st


def _zero_filled_pairs(tile_list, chrom, start, end, v):
    """Pairs i < j of v sharing no tile (assemble_region's zero-filled pairs, from each tile's in-window 4-keys)."""
    keys = list(zip(v["CHR"].astype(str), v["POS"].astype(np.int64), v["REF"], v["ALT"]))
    member = np.zeros((len(v), len(tile_list)), dtype=bool)
    for t, (_, gz) in enumerate(tile_list):
        tv = ukb337k_tiles.read_tile_variants(gz)
        m = (tv["CHR"] == str(chrom)) & (tv["POS"] >= start) & (tv["POS"] <= end)
        tk = set(zip(tv.loc[m, "CHR"], tv.loc[m, "POS"].astype(np.int64), tv.loc[m, "REF"], tv.loc[m, "ALT"]))
        member[:, t] = [k in tk for k in keys]
    # rows with the same tile set share every tile; count pairs over tile-set classes
    pat, cnt = np.unique(member, axis=0, return_counts=True)
    n = len(v)
    filled = sum(int(cnt[a]) * int(cnt[b]) for a in range(len(pat)) for b in range(len(pat))
                 if (pat[a] & pat[b]).any())
    return (n * n - filled) // 2


def build_native_multiallelic(tile_list, chrom, start, end, catalog_tsv):
    """ukb337k_tiles.build_native, then resolve_multiallelic_positions. Stats: build_native's, with n_var and
    n_pairs_zero_filled for the final panel, plus the four resolution counts."""
    R, v, st = ukb337k_tiles.build_native(tile_list, chrom, start, end, catalog_tsv)
    R, v, audit, rst = resolve_multiallelic_positions(R, v)
    st = dict(st)
    if rst["n_var_dropped_multiallelic"]:
        st["n_pairs_zero_filled"] = _zero_filled_pairs(tile_list, chrom, start, end, v)
    st["n_var"] = len(v)
    st.update(rst)
    return R, v, st, audit


def audit_path(stats_path):
    p = Path(stats_path)
    if not p.name.endswith(".stats.tsv"):
        raise ValueError(f"stats path must end in .stats.tsv: {p}")
    return p.with_name(p.name[: -len(".stats.tsv")] + ".multiallelic_resolved.tsv")


def write_native_multiallelic_panel(tile_list, chrom, start, end, catalog_tsv, out, stats_path, region_id="",
                                    rscript=None):
    R, v, st, audit = build_native_multiallelic(tile_list, chrom, start, end, catalog_tsv)
    ukb337k_tiles.write_rds(R, v, out, "ukb337k_native", region_id, "EUR", "ukb_allele2_allele1", rscript)
    ap = audit_path(stats_path)
    ap.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(ap, sep="\t", index=False, lineterminator="\n")
    return st


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build-native")
    for k in ("--region-id", "--region-safe", "--chr", "--start", "--end", "--stats", "--catalog", "--out"):
        b.add_argument(k, required=True)
    a = ap.parse_args(argv)
    start, end = int(a.start), int(a.end)
    tiles = ukb337k_tiles.region_tiles(a.chr, start, end)
    if not tiles:
        raise SystemExit(f"no fetched tile covers {a.chr}:{start}-{end}")
    st = write_native_multiallelic_panel(tiles, a.chr, start, end, a.catalog, a.out, a.stats, a.region_id)
    ukb337k_tiles._write_stats(a.stats, a.region_safe, tiles, st)
    print(a.region_safe, st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
