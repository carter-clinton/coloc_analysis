"""Harmonize one (source, qtd, region) group of config/ta_r4/qtl_manifest.tsv with the shipped harmonizers (W3e, D-05).

The manifest feature is the molecular_trait_id (for eqtl it equals gene_id; for sqtl it is a splice junction). The
shipped harmonize_eqtl()/harmonize_sqtl() filter on gene_id only, which would mix every junction of a gene in one
file. So the window is read once with the shipped reader, cut to one molecular_trait_id, and handed to the shipped
harmonize function in place of its reader; every other step (region, gene, MAF, N, columns) is the shipped code.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import os
import sys
from pathlib import Path

import yaml

import harmonize_eqtl
import harmonize_sqtl
from build_tissue_n_lookup import GTEX_V8_TISSUE_N_FALLBACK

from ta_r4 import paths

MANIFEST = "config/ta_r4/qtl_manifest.tsv"
DL_MANIFEST = f"{paths.MAN}/qtl_downloads_sha256.tsv"
DL_ROOT = f"{paths.R4}/downloads/eqtl_catalogue"
QTL_SOURCES = "config/qtl_sources.yaml"
HARMONIZED = f"{paths.R4}/qtl/harmonized"
SOURCES = {"eqtl": (harmonize_eqtl, "harmonize_eqtl", "gtex_eqtl"),
           "sqtl": (harmonize_sqtl, "harmonize_sqtl", "gtex_sqtl")}
DONE_COLUMNS = ["rel_path", "sha256", "n_rows", "source", "qtd", "molecular_trait_id", "gene_id", "region_safe",
                "message"]


def manifest_rows(manifest=MANIFEST):
    with open(manifest, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def group_features(rows, source, qtd, region):
    """Sorted distinct (molecular_trait_id, gene_id) of one group, plus the group's tissue and GRCh38 window."""
    g = [r for r in rows if (r["source"], r["qtd"], r["region_safe"]) == (source, qtd, region)]
    if not g:
        raise ValueError(f"no manifest rows for {source} {qtd} {region}")
    meta = {(r["tissue"], r["chr38"], r["start38"], r["end38"]) for r in g}
    if len(meta) != 1:
        raise ValueError(f"{source} {qtd} {region}: tissue/window not unique {sorted(meta)}")
    tissue, chrom, start, end = meta.pop()
    feats = sorted({(r["molecular_trait_id"], r["gene_id"]) for r in g})
    if len({f for f, _ in feats}) != len(feats):
        raise ValueError(f"{source} {qtd} {region}: a molecular_trait_id maps to two gene_ids")
    return feats, {"tissue": tissue, "chr": chrom, "start": int(start), "end": int(end)}


def groups(rows):
    return sorted({(r["source"], r["qtd"], r["region_safe"]) for r in rows})


def group_index(rows):
    """{(source, qtd, region_safe): manifest rows} in one pass."""
    idx = {}
    for r in rows:
        idx.setdefault((r["source"], r["qtd"], r["region_safe"]), []).append(r)
    return idx


def harmonized_path(source, qtd, feature, region):
    return f"{HARMONIZED}/{source}/{qtd}/{feature}/{region}.harmonized.tsv.gz"


def done_path(source, qtd, region):
    return f"{HARMONIZED}/{source}/{qtd}/{region}.done"


def download_path(qtd, dl_manifest=DL_MANIFEST, root=DL_ROOT):
    with open(dl_manifest, newline="") as fh:
        hit = [r for r in csv.DictReader(fh, delimiter="\t") if r["qtd"] == qtd]
    if len(hit) != 1:
        raise ValueError(f"{len(hit)} download rows for {qtd} in {dl_manifest}")
    return f"{root}/{qtd}/{os.path.basename(hit[0]['url'])}"


def tissue_n(tissue):
    return GTEX_V8_TISSUE_N_FALLBACK[tissue]


@contextlib.contextmanager
def _reader(module, frame):
    """The shipped harmonize function reads `frame` (one molecular_trait_id) instead of the file."""
    orig = module._read_eqtl_file
    module._read_eqtl_file = lambda _path, _region: frame.copy()
    try:
        yield
    finally:
        module._read_eqtl_file = orig


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def harmonize_group(source, qtd, region, *, manifest=MANIFEST, input_path=None, qtl_sources=QTL_SOURCES,
                    out_root=HARMONIZED):
    module, fn_name, _ = SOURCES[source]
    feats, win = group_features(manifest_rows(manifest), source, qtd, region)
    input_path = input_path or download_path(qtd)
    with open(qtl_sources) as fh:
        cfg = yaml.safe_load(fh)
    region_d = {"chr": win["chr"], "start": win["start"], "end": win["end"]}
    window = harmonize_eqtl._read_eqtl_file(input_path, region_d)  # the shipped reader, once per group
    if "molecular_trait_id" not in window.columns and len(window):
        raise ValueError(f"{input_path}: no molecular_trait_id column")
    out = []
    for feature, gene in feats:
        frame = window[window["molecular_trait_id"] == feature] if len(window) else window
        with _reader(module, frame):
            df = getattr(module, fn_name)(input_path=input_path, region=region_d, gene_id=gene,
                                          tissue_name=win["tissue"], tissue_n=tissue_n(win["tissue"]), config=cfg)
        p = f"{out_root}/{source}/{qtd}/{feature}/{region}.harmonized.tsv.gz"
        harmonize_eqtl.write_harmonized(df, p)
        msg = "" if len(df) else f"No variants after harmonization for {gene} / {win['tissue']}"
        out.append({"rel_path": p, "sha256": sha256(p), "n_rows": len(df), "source": source, "qtd": qtd,
                    "molecular_trait_id": feature, "gene_id": gene, "region_safe": region, "message": msg})
    return out


def write_done(records, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", newline="") as fh:
        w = csv.DictWriter(fh, DONE_COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(records)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, choices=sorted(SOURCES))
    ap.add_argument("--qtd", required=True)
    ap.add_argument("--region", required=True)
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--done", required=True)
    a = ap.parse_args(argv)
    recs = harmonize_group(a.source, a.qtd, a.region, manifest=a.manifest)
    write_done(recs, a.done)
    print(f"[harmonize_qtl_r4] {a.source} {a.qtd} {a.region}: {len(recs)} features, "
          f"{sum(r['n_rows'] == 0 for r in recs)} empty")
    return 0


if __name__ == "__main__":
    sys.exit(main())
