"""Static, outcome-independent QTL-coloc manifest (ta-r4 W2c).

One row per (admissible EUR region, EUR trait, source, tissue, molecular_trait_id) where the downloaded
eQTL Catalogue file has >= 1 row inside the region's GRCh38 window (tabix slice). No GWAS-fit status or tier.
--scope is a pure (source, tissue) filter applied before slicing.
"""
from __future__ import annotations

import argparse
import ast
import concurrent.futures as cf
import csv
import gzip
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
PAIR_MANIFEST = REPO / "config/ta_r4/pair_manifest.tsv"
REGIONS_CSV = REPO / "config/regions_curated_grch38.csv"
REVIEW_DECISIONS = REPO / "config/ta_r4/review_decisions.yaml"
FROZEN_LOOKUP = REPO / "src/python/build_tissue_n_lookup.py"
DL_MANIFEST = REPO / ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_downloads_sha256.tsv"
DL_ROOT = REPO / "data/r4/downloads/eqtl_catalogue"

SCOPES = ("full", "tissues_frozen", "eqtl_only", "tissues_frozen+eqtl_only")
SOURCE_LABEL = {"gtex_eqtl": "eqtl", "gtex_sqtl": "sqtl"}
COLUMNS = ["qtl_row_id", "region_safe", "ancestry", "trait", "source", "tissue", "qtd", "gene_id",
           "molecular_trait_id", "chr38", "start38", "end38", "n_qtl_variants_in_window"]
FORBIDDEN = ("status", "tier")


def check_schema(columns):
    bad = [c for c in columns if any(f in c.lower() for f in FORBIDDEN)]
    if bad:
        raise ValueError(f"outcome-dependent column(s) not allowed: {bad}")


def frozen_tissues(path=FROZEN_LOOKUP):
    """Tissue set of the frozen Track A QTL layer: the keys of the lookup the legacy manifest iterated."""
    tree = ast.parse(Path(path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "GTEX_V8_TISSUE_N_FALLBACK"
                                                for t in node.targets):
            tissues = frozenset(ast.literal_eval(node.value))
            return tissues, f"{Path(path).relative_to(REPO)}:{node.lineno} GTEX_V8_TISSUE_N_FALLBACK"
    raise ValueError(f"GTEX_V8_TISSUE_N_FALLBACK not found in {path}")


def default_scope(path=REVIEW_DECISIONS):
    p = Path(path)
    if not p.is_file():
        return "full"
    scope = (yaml.safe_load(p.read_text()) or {}).get("qtl_scope", "full")
    if scope not in SCOPES:
        raise ValueError(f"qtl_scope {scope!r} not in {SCOPES}")
    return scope


def scope_filter(files, scope, frozen):
    if scope not in SCOPES:
        raise ValueError(f"scope {scope!r} not in {SCOPES}")
    out = list(files)
    if "tissues_frozen" in scope:
        out = [f for f in out if f["tissue"] in frozen]
    if "eqtl_only" in scope:
        out = [f for f in out if f["source"] == "eqtl"]
    return out


def _pair_rows(path=PAIR_MANIFEST):
    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t")
                if r["ancestry"] == "EUR" and r["admissible"] == "true" and r["row_class"] == "primary"]


def admissible_regions(pair_manifest=PAIR_MANIFEST, regions_csv=REGIONS_CSV):
    ids = {r["region_id"]: r["region_safe"] for r in _pair_rows(pair_manifest)}
    with open(regions_csv, newline="") as fh:
        coords = {r["region_id"]: r for r in csv.DictReader(fh)}
    out = []
    for rid, safe in ids.items():
        c = coords[rid]
        out.append({"region_safe": safe, "chr38": c["chr"], "start38": int(c["start_grch38"]),
                    "end38": int(c["end_grch38"])})
    return sorted(out, key=lambda r: r["region_safe"])


def eur_traits(pair_manifest=PAIR_MANIFEST):
    rows = _pair_rows(pair_manifest)
    return sorted({r["trait_a"] for r in rows} | {r["trait_b"] for r in rows})


def slice_features(path, chrom, start, end, tabix):
    """{molecular_trait_id: (gene_id, n distinct variants)} for rows with start <= position <= end."""
    with gzip.open(path, "rt") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
    p = subprocess.run([tabix, path, f"{chrom}:{start}-{end}"], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"tabix failed on {path}: {p.stderr.strip()}")
    i_m, i_g, i_v, i_p = (hdr.index(c) for c in ("molecular_trait_id", "gene_id", "variant", "position"))
    feats = {}
    for ln in p.stdout.splitlines():
        f = ln.split("\t")
        pos = int(f[i_p])
        if pos < start or pos > end:
            continue
        gene, variants = feats.setdefault(f[i_m], (f[i_g], set()))
        if gene != f[i_g]:
            raise RuntimeError(f"{path}: {f[i_m]} maps to two gene_ids {gene}, {f[i_g]}")
        variants.add(f[i_v])
    return {k: (g, len(v)) for k, (g, v) in feats.items()}


def build_rows(files, regions, traits, tabix, jobs=4):
    tasks = [(f, r) for f in files for r in regions]
    with cf.ThreadPoolExecutor(jobs) as ex:
        results = ex.map(lambda t: slice_features(t[0]["path"], t[1]["chr38"], t[1]["start38"], t[1]["end38"],
                                                  tabix), tasks)
        rows = []
        for (f, r), feats in zip(tasks, results):
            for mtid, (gene, n) in feats.items():
                for trait in traits:
                    rows.append({
                        "qtl_row_id": "__".join([r["region_safe"], "EUR", trait, f["source"], f["tissue"], mtid]),
                        "region_safe": r["region_safe"], "ancestry": "EUR", "trait": trait, "source": f["source"],
                        "tissue": f["tissue"], "qtd": f["qtd"], "gene_id": gene, "molecular_trait_id": mtid,
                        "chr38": r["chr38"], "start38": str(r["start38"]), "end38": str(r["end38"]),
                        "n_qtl_variants_in_window": str(n)})
    return rows


def write_manifest(rows, out):
    check_schema(COLUMNS)
    rows = sorted(rows, key=lambda r: r["qtl_row_id"])
    if len({r["qtl_row_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate qtl_row_id")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(out) + ".tmp")
    with open(tmp, "w", newline="") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            fh.write("\t".join(r[c] for c in COLUMNS) + "\n")
    os.replace(tmp, out)


def downloaded_files(manifest=DL_MANIFEST, root=DL_ROOT):
    with open(manifest, newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    out = []
    for r in rows:
        path = Path(root) / r["qtd"] / os.path.basename(r["url"])
        if path.stat().st_size != int(r["size_bytes"]):
            raise RuntimeError(f"{path} size {path.stat().st_size} != manifest {r['size_bytes']}")
        out.append({"qtd": r["qtd"], "source": SOURCE_LABEL[r["source"]], "tissue": r["tissue"], "path": str(path)})
    return sorted(out, key=lambda f: (f["source"], f["tissue"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--downloads-manifest", default=str(DL_MANIFEST))
    ap.add_argument("--downloads-root", default=str(DL_ROOT))
    ap.add_argument("--scope", choices=SCOPES, help="default: review_decisions.yaml qtl_scope, else full")
    ap.add_argument("--tabix", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args(argv)
    scope = a.scope or default_scope()
    frozen, src = frozen_tissues()
    files = scope_filter(downloaded_files(a.downloads_manifest, a.downloads_root), scope, frozen)
    regions, traits = admissible_regions(), eur_traits()
    rows = build_rows(files, regions, traits, a.tabix, a.jobs)
    write_manifest(rows, a.out)
    feats = {(r["region_safe"], r["source"], r["tissue"], r["molecular_trait_id"]) for r in rows}
    print(f"scope={scope} frozen_tissues={len(frozen)} ({src}) files={len(files)} regions={len(regions)} "
          f"traits={len(traits)} features={len(feats)} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
