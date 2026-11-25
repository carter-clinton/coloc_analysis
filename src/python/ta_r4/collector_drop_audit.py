"""r4 collector drop audit (W3f 15.8a, review R2): every input row collect_region_variants.py does not keep, classified.

replay() re-implements collect_variants (src/legacy/region_analysis/scripts/collect_region_variants.py, not edited)
step for step and tags each in-window input row with the step that removes it. audit_region() runs the replay and the
unmodified collector on the same inputs and refuses (ReplayMismatch) unless the replay's kept rows equal the collector's
and its TSV is byte-equal to the on-disk raw catalog.

Classes (a dropped row gets exactly one):
  keying, named row (`SNP::<rsid>`, :104-123), against the record holding the rsid when the row is read:
    exact_duplicate               same CHR/POS/REF/ALT values as that record
    allele_less                   the row has no real alleles (REF or ALT in "", N, nan)
    rsid_same_key_other_bytes     same normalized allele key, other bytes
    rsid_other_allele_key         another allele key
    rsid_replaced_allele_less     the stored allele-less record, replaced by this rsid's row with real alleles
  keying, unnamed row (:106-109):
    unnamed_duplicate             repeat of an unnamed CHR/POS/ref/alt (alleles lower-cased)
  post-steps:
    unnamed_at_named_position     :143-150, unnamed row at a CHR:POS that carries a named row (allele_less if no alleles)
    unnamed_same_position_other_alleles  :151-155, second unnamed row at a CHR:POS (allele_less if no alleles)
    other                         anything else (the :142 drop_duplicates, or a named row removed at :151-155): STOP
Allele key = catalog_unique_key.py's (_norm_chr(CHR), int(POS), REF.strip().upper(), ALT.strip().upper()); swapped =
(chr, pos, ALT, REF).

  python -m ta_r4.collector_drop_audit region --region R [--json-dir D]
  python -m ta_r4.collector_drop_audit manifest --out TSV [--json-dir D]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path

import pandas as pd

from ta_r4 import paths
from ta_r4.catalog_unique_key import _norm_chr

COLLECTOR = "src/legacy/region_analysis/scripts/collect_region_variants.py"
AUDIT_DIR = f"{paths.R4}/ld/variants_r4_collector_dropped"
JSON_DIR = f"{paths.R4}/tmp/w3f/q158/drops"
CLASSES = ("exact_duplicate", "rsid_same_key_other_bytes", "rsid_other_allele_key", "rsid_replaced_allele_less",
           "unnamed_duplicate", "unnamed_at_named_position", "unnamed_same_position_other_alleles", "allele_less")
AUDIT_COLUMNS = ("CHR", "POS", "REF", "ALT", "SNP_ID", "source_file", "source_row", "class", "kept_SNP_ID",
                 "kept_REF", "kept_ALT", "real_alleles", "key_in_final_catalog", "swapped_key_in_final_catalog")
_NO_ALLELE = {"", "n", "nan"}


class ReplayMismatch(RuntimeError):
    pass


def load_collector(repo="."):
    """The unmodified legacy collector, imported by file path."""
    spec = importlib.util.spec_from_file_location("collect_region_variants", Path(repo) / COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm_key(chrom, pos, ref, alt):
    return (_norm_chr(str(chrom)), int(pos), str(ref).strip().upper(), str(alt).strip().upper())


def catalog_keys_from_lines(lines):
    """Normalized allele keys of a catalog given as lines (header first)."""
    rd = csv.reader([ln.rstrip("\r\n") for ln in lines], delimiter="\t", quoting=csv.QUOTE_NONE)
    header = next(rd)
    c = {k: header.index(k) for k in ("CHR", "POS", "REF", "ALT")}
    return {norm_key(f[c["CHR"]], f[c["POS"]].strip(), f[c["REF"]], f[c["ALT"]]) for f in rd}


def catalog_keys(path):
    with open(path, newline="") as fh:
        return catalog_keys_from_lines(fh.readlines())


def _real(ref, alt):
    return str(ref).lower() not in _NO_ALLELE and str(alt).lower() not in _NO_ALLELE


def replay(harmonized_paths, chrom, start, end):
    """(kept_df, dropped): kept_df as collect_variants returns it; dropped = one dict per in-window row not kept."""
    chrom_clean = str(chrom)
    records = OrderedDict()
    tags = []  # per in-window row: dict(CHR raw, POS, REF, ALT, SNP_ID, source_file, source_row)
    dropped = []

    def drop(i, cls, by):
        dropped.append({"i": i, "class": cls, "by": by})

    for path in harmonized_paths:
        path_obj = Path(path)
        if not path_obj.exists():
            continue
        header = pd.read_csv(path_obj, sep="\t", nrows=0, compression="gzip")
        available = header.columns.tolist()
        usecols = ["CHR", "POS"]
        ref_missing = "REF" not in available
        alt_missing = "ALT" not in available
        snp_missing = "SNP_ID" not in available
        if not ref_missing:
            usecols.append("REF")
        if not alt_missing:
            usecols.append("ALT")
        if not snp_missing:
            usecols.append("SNP_ID")
        chunks = pd.read_csv(path_obj, sep="\t", usecols=usecols, compression="gzip", chunksize=500_000)
        for chunk in chunks:
            if chunk.empty:
                continue
            chr_input = chunk["CHR"].astype(str)
            chunk["CHR"] = (
                chunk["CHR"].astype(str).str.replace("^chr", "", regex=True).str.replace("^CHR", "", regex=True)
            )
            chunk["POS"] = pd.to_numeric(chunk["POS"], errors="coerce")
            mask = (chunk["CHR"] == chrom_clean) & ((chunk["POS"] >= start) & (chunk["POS"] <= end))
            if not mask.any():
                continue
            subset_cols = ["CHR", "POS"]
            if not ref_missing:
                subset_cols.append("REF")
            if not alt_missing:
                subset_cols.append("ALT")
            if not snp_missing:
                subset_cols.append("SNP_ID")
            subset = chunk.loc[mask, subset_cols].dropna(subset=["POS"])
            if int(mask.sum()) != len(subset):
                raise ReplayMismatch(f"{path}: {int(mask.sum()) - len(subset)} in-window rows with NaN POS")
            if subset.empty:
                continue
            subset["POS"] = subset["POS"].astype(int)
            if ref_missing:
                subset["REF"] = "N"
            if alt_missing:
                subset["ALT"] = "N"
            if "SNP_ID" not in subset.columns:
                subset["SNP_ID"] = pd.NA
            src_rows = subset.index.tolist()
            src_chr = chr_input.loc[subset.index].tolist()
            for row, src_row, chr_raw in zip(subset.itertuples(index=False), src_rows, src_chr):
                snp_id = getattr(row, "SNP_ID", None)
                snp_id_clean = None
                if snp_id is not None and pd.notna(snp_id):
                    snp_id_str = str(snp_id).strip()
                    if snp_id_str and snp_id_str.lower() != "na":
                        snp_id_clean = snp_id_str
                ref_val = getattr(row, "REF", "N")
                alt_val = getattr(row, "ALT", "N")
                ref_clean = str(ref_val).lower()
                alt_clean = str(alt_val).lower()
                has_real_alleles = ref_clean not in {"", "n", "nan"} and alt_clean not in {"", "n", "nan"}
                i = len(tags)
                tags.append({"CHR": chr_raw, "POS": int(row.POS), "REF": str(ref_val), "ALT": str(alt_val),
                             "SNP_ID": snp_id_clean or "", "source_file": str(path), "source_row": int(src_row)})

                if snp_id_clean:
                    key = f"SNP::{snp_id_clean}"
                else:
                    key = f"POS::{row.CHR}::{row.POS}::{ref_clean}::{alt_clean}"
                    if key in records:
                        drop(i, "unnamed_duplicate", records[key]["_src"])
                        continue

                existing = records.get(key)
                if existing is None or (
                    snp_id_clean
                    and (existing["REF"].lower() in {"", "n"} or existing["ALT"].lower() in {"", "n"})
                    and has_real_alleles
                ):
                    if existing is not None:
                        drop(existing["_src"], "rsid_replaced_allele_less", i)
                    records[key] = {"CHR": row.CHR, "POS": row.POS, "REF": ref_val, "ALT": alt_val,
                                    "SNP_ID": snp_id_clean, "_src": i}
                else:
                    e = tags[existing["_src"]]
                    t = tags[i]
                    if [t[c] for c in ("CHR", "POS", "REF", "ALT")] == [e[c] for c in ("CHR", "POS", "REF", "ALT")]:
                        cls = "exact_duplicate"
                    elif not has_real_alleles:
                        cls = "allele_less"
                    elif norm_key(t["CHR"], t["POS"], t["REF"], t["ALT"]) == norm_key(e["CHR"], e["POS"], e["REF"],
                                                                                       e["ALT"]):
                        cls = "rsid_same_key_other_bytes"
                    else:
                        cls = "rsid_other_allele_key"
                    drop(i, cls, existing["_src"])
    cols = ["CHR", "POS", "REF", "ALT", "SNP_ID"]
    if not records:
        return pd.DataFrame(columns=cols), _finish(dropped, tags)
    df = pd.DataFrame(list(records.values()), columns=cols + ["_src"])
    if df.empty:
        return df.drop(columns=["_src"]), _finish(dropped, tags)

    df["SNP_ID"] = df["SNP_ID"].fillna("").astype(str)
    df["REF"] = df["REF"].fillna("").astype(str)
    df["ALT"] = df["ALT"].fillna("").astype(str)
    ref_missing = df["REF"].str.lower().isin({"", "n", "nan"})
    alt_missing = df["ALT"].str.lower().isin({"", "n", "nan"})
    df["has_real_alleles"] = ~(ref_missing | alt_missing)
    df["has_snp"] = df["SNP_ID"].str.len() > 0
    df = df.sort_values(by=["has_snp", "has_real_alleles"], ascending=[False, False], kind="mergesort")
    before = set(df["_src"])
    df = df.drop_duplicates(subset=["CHR", "POS", "REF", "ALT", "SNP_ID"], keep="first")
    for i in sorted(before - set(df["_src"])):
        drop(i, "other", None)
    df["pos_key"] = df["CHR"].astype(str) + ":" + df["POS"].astype(str)
    pos_with_ids = set(df.loc[df["SNP_ID"] != "", "pos_key"])
    if pos_with_ids:
        keep_mask = ~((df["SNP_ID"] == "") & df["pos_key"].isin(pos_with_ids))
        first_named = {}
        for pk, s in zip(df.loc[df["SNP_ID"] != "", "pos_key"], df.loc[df["SNP_ID"] != "", "_src"]):
            first_named.setdefault(pk, s)
        for pk, s, real in zip(df.loc[~keep_mask, "pos_key"], df.loc[~keep_mask, "_src"],
                               df.loc[~keep_mask, "has_real_alleles"]):
            drop(s, "unnamed_at_named_position" if real else "allele_less", first_named[pk])
        df = df.loc[keep_mask].copy()
    df["primary_key"] = df.apply(lambda row: row["SNP_ID"] if row["SNP_ID"] else row["pos_key"], axis=1)
    dup = df.duplicated(subset=["primary_key"], keep="first")
    if dup.any():
        first = {}
        for pk, s in zip(df.loc[~dup, "primary_key"], df.loc[~dup, "_src"]):
            first[pk] = s
        for pk, s, snp, real in zip(df.loc[dup, "primary_key"], df.loc[dup, "_src"], df.loc[dup, "SNP_ID"],
                                    df.loc[dup, "has_real_alleles"]):
            if snp:
                cls = "other"
            else:
                cls = "unnamed_same_position_other_alleles" if real else "allele_less"
            drop(s, cls, first[pk])
    df = df.drop_duplicates(subset=["primary_key"], keep="first")
    df = df.drop(columns=["has_real_alleles", "has_snp", "primary_key", "pos_key"])
    df = df.sort_values(["CHR", "POS"]).reset_index(drop=True)
    kept_src = set(df["_src"])
    df = df.drop(columns=["_src"])
    out = _finish(dropped, tags)
    seen = [d["i"] for d in dropped]
    if len(seen) != len(set(seen)) or set(seen) & kept_src or len(seen) + len(kept_src) != len(tags):
        raise ReplayMismatch(f"row accounting: {len(tags)} input, {len(kept_src)} kept, {len(seen)} dropped "
                             f"({len(seen) - len(set(seen))} twice, {len(set(seen) & kept_src)} also kept)")
    return df, out


def _finish(dropped, tags):
    out = []
    for d in dropped:
        t = dict(tags[d["i"]])
        b = tags[d["by"]] if d["by"] is not None else {"SNP_ID": "", "REF": "", "ALT": ""}
        t.update({"class": d["class"], "kept_SNP_ID": b["SNP_ID"], "kept_REF": b["REF"], "kept_ALT": b["ALT"],
                  "real_alleles": _real(t["REF"], t["ALT"])})
        out.append(t)
    return out


def flag_dropped(dropped, final_keys):
    """Add key_in_final_catalog / swapped_key_in_final_catalog (normalized allele key) to each dropped row."""
    out = []
    for d in dropped:
        k = norm_key(d["CHR"], d["POS"], d["REF"], d["ALT"])
        d = dict(d)
        d["key_in_final_catalog"] = k in final_keys
        d["swapped_key_in_final_catalog"] = (k[0], k[1], k[3], k[2]) in final_keys
        out.append(d)
    return out


def audit_bytes(flagged):
    rows = sorted(flagged, key=lambda d: (d["CHR"], d["POS"], d["source_file"], d["source_row"]))
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    w.writerow(AUDIT_COLUMNS)
    for d in rows:
        w.writerow([d[c] for c in AUDIT_COLUMNS])
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        gz.write(buf.getvalue().encode("utf-8"))
    return raw.getvalue()


def r4_regions(repo="."):
    with open(Path(repo) / paths.MAN / "catalogs_sha256.tsv", newline="") as fh:
        return sorted(r["region_safe"] for r in csv.DictReader(fh, delimiter="\t") if r["route"] == "r4")


def r4_sumstats(repo="."):
    """The 8 r4 catalog inputs in CATALOG_SUMSTATS["r4"] order (ta_r4_panels.smk:14-17)."""
    import yaml

    with open(Path(repo) / "config/pipeline.yaml") as fh:
        cfg = yaml.safe_load(fh)
    out = [paths.sumstats_path(t, a, "A3_1kg") for t in cfg["traits"] for a in cfg["trait_ancestries"].get(t, [])]
    if len(out) != 8:
        raise ValueError(f"expected the 8 Track A sumstats, got {out}")
    return out


def region_window(region_safe, repo="."):
    """(region_id, chr, start, end) by the Snakefile.ta_r4 safe-id rule and the collector's load_regions."""
    col = load_collector(repo)
    regions = col.load_regions(Path(repo) / paths.regions_csv())
    safe_to_id = {}
    for orig in regions:
        safe = orig.replace(".", "_").replace("/", "_")
        suffix = 1
        while safe in safe_to_id:
            suffix += 1
            safe = f"{safe}_{suffix}"
        safe_to_id[safe] = orig
    rid = safe_to_id[region_safe]
    r = regions[rid]
    return rid, r["chr"], r["start"], r["end"]


def audit_region(region_safe, repo=".", write=True, json_dir=JSON_DIR):
    """Replay + identity checks + flags for one r4 region; returns (summary, audit gzip bytes)."""
    repo = Path(repo)
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        inputs = r4_sumstats(".")
        missing = [p for p in inputs if not Path(p).exists()]
        if missing:
            raise ReplayMismatch(f"{region_safe}: missing inputs {missing}")
        rid, chrom, start, end = region_window(region_safe, ".")
        kept, dropped = replay(inputs, chrom, start, end)
        collector = load_collector(".").collect_variants(inputs, chrom, start, end)
        if not kept.equals(collector):
            raise ReplayMismatch(f"{region_safe}: replay kept rows != collect_variants output")
        on_disk = open(paths.catalog_raw_path(region_safe), "rb").read()
        if kept.to_csv(sep="\t", index=False).encode("utf-8") != on_disk:
            raise ReplayMismatch(f"{region_safe}: replay TSV != on-disk {paths.catalog_raw_path(region_safe)}")
        flagged = flag_dropped(dropped, catalog_keys(paths.catalog_path("r4", region_safe)))
        body = audit_bytes(flagged)
        audit_path = f"{AUDIT_DIR}/{region_safe}.tsv.gz"
        lost = [d for d in flagged if d["real_alleles"] and not d["key_in_final_catalog"]]
        summary = {
            "region_safe": region_safe, "region_id": rid, "chr": chrom, "start": start, "end": end,
            "n_input_rows": len(kept) + len(flagged), "n_kept": len(kept), "n_dropped": len(flagged),
            **{f"n_dropped_{c}": sum(d["class"] == c for d in flagged) for c in CLASSES + ("other",)},
            "n_lost_keys": len(lost),
            "n_lost_keys_swapped_present": sum(d["swapped_key_in_final_catalog"] for d in lost),
            "audit_path": audit_path, "audit_rows": len(flagged),
            "audit_sha256": hashlib.sha256(body).hexdigest(),
            "lost_keys": sorted({norm_key(d["CHR"], d["POS"], d["REF"], d["ALT"]) for d in lost}),
        }
        if write:
            Path(audit_path).parent.mkdir(parents=True, exist_ok=True)
            part = Path(audit_path + ".part")
            part.write_bytes(body)
            os.replace(part, audit_path)
            Path(json_dir).mkdir(parents=True, exist_ok=True)
            with open(Path(json_dir) / f"{region_safe}.json", "w") as fh:
                json.dump(summary, fh, indent=1)
        return summary, body
    finally:
        os.chdir(cwd)


MANIFEST_COLUMNS = (["region_safe", "n_input_rows", "n_kept", "n_dropped"]
                    + [f"n_dropped_{c}" for c in CLASSES + ("other",)]
                    + ["n_lost_keys", "n_lost_keys_swapped_present", "audit_path", "audit_rows", "audit_sha256"])


def write_manifest(out, json_dir=JSON_DIR, repo="."):
    regions = r4_regions(repo)
    rows = []
    for r in regions:
        with open(Path(json_dir) / f"{r}.json") as fh:
            rows.append(json.load(fh))
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(MANIFEST_COLUMNS)
        for s in rows:
            w.writerow([s[c] for c in MANIFEST_COLUMNS])
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m ta_r4.collector_drop_audit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("region")
    a1.add_argument("--region", required=True)
    a1.add_argument("--json-dir", default=JSON_DIR)
    a2 = sub.add_parser("manifest")
    a2.add_argument("--out", required=True)
    a2.add_argument("--json-dir", default=JSON_DIR)
    a = ap.parse_args(argv)
    if a.cmd == "region":
        s, _ = audit_region(a.region, ".", write=True, json_dir=a.json_dir)
        bad = s["n_dropped_other"] or s["n_input_rows"] != s["n_kept"] + s["n_dropped"]
        print(json.dumps({k: v for k, v in s.items() if k != "lost_keys"}))
        return 3 if bad else 0
    rows = write_manifest(a.out, a.json_dir, ".")
    print(f"manifest {a.out}: {len(rows)} regions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
