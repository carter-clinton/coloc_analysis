"""UKB 337k LD tiles (Weissbrod et al. / PolyFun; s3://broad-alkesgroup-ukbb-ld/UKBB_LD, hg19): verified fetch,
triangle-safe load, overlapping-tile region assembly, D.R.D re-orientation to a reference panel, .rds I/O.

Stored convention (PolyFun finemapper.load_ld_npz: R += R.T; assert diag == 1): one triangle with diag 0.5.
The legacy download_ukbb_ld_tiles.py loader used (M + M.T) / 2, which halves every r (Pitfall 10); not used here.
Labels: ALT := allele1, REF := allele2.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

from ta_r4 import fetch_verified as _fv
from ta_r4 import paths as r4paths
from ta_r4.fetch_verified import fetch_verified

BASE_URL = "https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/"
DOWNLOAD_DIR = f"{_fv.DOWNLOADS_ROOT}/ukb337k"
TILE_MANIFEST = f"{r4paths.MAN}/ukb337k_tiles_sha256.tsv"
TILE_COLS = ["tile", "file", "url", "size_bytes", "etag", "md5", "sha256", "fetched_utc"]
TILE_STEP, TILE_SPAN = 1_000_000, 3_000_000
OVERLAP_TOL = 1e-6
PALINDROMIC = ({"A", "T"}, {"C", "G"})
RSCRIPT_R4 = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"


class TileConventionError(ValueError):
    pass


class TileDisagreementError(ValueError):
    pass


# --- tile geometry ---------------------------------------------------------------------------------------------------
def _bounds(name):
    _, s, e = name.split("_")
    return int(s), int(e)


def tile_names_for(chrom, start, end):
    """Tiles chr{c}_{s}_{e} (s = k*1e6 + 1, e = s + 3e6) whose window intersects [start, end]."""
    out = []
    for k in range(0, int(end) // TILE_STEP + 1):
        s = k * TILE_STEP + 1
        e = s + TILE_SPAN
        if e >= start and s <= end:
            out.append(f"chr{chrom}_{s}_{e}")
    return out


def covering_tiles(chrom, start, end, available=None):
    """The intersecting tiles (only those in `available`, if given) minus those whose window clipped to the region
    lies inside another kept tile's. Equal clipped windows keep the tile centred closest to the region (then the
    lowest start)."""
    mid = (start + end) / 2
    cand = []
    for n in tile_names_for(chrom, start, end):
        if available is not None and n not in available:
            continue
        s, e = _bounds(n)
        cand.append((max(s, start), min(e, end), abs((s + e) / 2 - mid), s, n))
    cand.sort(key=lambda c: (c[2], c[3]))
    kept = []
    for c in cand:
        if not any(k[0] <= c[0] and c[1] <= k[1] for k in kept):
            kept = [k for k in kept if not (c[0] <= k[0] and k[1] <= c[1])] + [c]
    return [c[4] for c in sorted(kept, key=lambda c: c[3])]


def tile_paths(name, root=DOWNLOAD_DIR):
    root = Path(root)
    return root / name / "npz" / f"{name}.npz", root / name / "gz" / f"{name}.gz"


# --- fetch -----------------------------------------------------------------------------------------------------------
def _head(url):
    if not url.startswith("https://"):
        raise ValueError(f"url must start with https://: {url}")
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=120) as r:
        return int(r.headers["Content-Length"]), r.headers.get("ETag", "")


def _manifest_rows(manifest):
    p = Path(manifest)
    if not p.is_file() or p.stat().st_size == 0:
        return []
    return pd.read_csv(p, sep="\t", dtype=str).to_dict("records")


def fetch_tile(name, dest_root=DOWNLOAD_DIR, manifest=TILE_MANIFEST, downloads_root=_fv.DOWNLOADS_ROOT,
               exts=("gz", "npz")):
    """HEAD (Content-Length + ETag), then fetch_verified(size=Content-Length; md5 = a single-part ETag), then one
    manifest row per file. A file already on disk must already have its manifest row with the same size."""
    if not re.fullmatch(r"chr[0-9XY]+_\d+_\d+", name):
        raise ValueError(f"bad tile name {name!r}")
    npz, gz = tile_paths(name, dest_root)
    for ext, path, magic in (("gz", gz, ("gzip",)), ("npz", npz, ("zip",))):
        if ext not in exts:
            continue
        fname = f"{name}.{ext}"
        if path.is_file():
            rows = [r for r in _manifest_rows(manifest) if r["file"] == fname]
            if len(rows) != 1 or int(rows[0]["size_bytes"]) != path.stat().st_size:
                raise RuntimeError(f"{path} exists without a matching manifest row in {manifest}")
            continue
        url = BASE_URL + fname
        size, etag = _head(url)
        bare = etag.strip('"')
        md5 = bare if re.fullmatch(r"[0-9a-f]{32}", bare) else None
        res = fetch_verified(url, path.parent, md5=md5, size=size, magic=magic, downloads_root=downloads_root)
        man = Path(manifest)
        new = not man.exists() or man.stat().st_size == 0
        with open(man, "a") as fh:
            if new:
                fh.write("\t".join(TILE_COLS) + "\n")
            fh.write("\t".join([name, fname, url, str(res["size"]), etag, res["md5"], res["sha256"],
                                _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")]) + "\n")
    return npz, gz


# --- load ------------------------------------------------------------------------------------------------------------
def read_tile_variants(gz):
    raw = pd.read_csv(gz, sep=r"\s+", dtype={"rsid": str, "chromosome": str, "allele1": str, "allele2": str})
    return pd.DataFrame({
        "SNP_ID": raw["rsid"].to_numpy(),
        "CHR": raw["chromosome"].str.replace("chr", "", regex=False).to_numpy(),
        "POS": raw["position"].astype(np.int64).to_numpy(),
        "REF": raw["allele2"].to_numpy(),
        "ALT": raw["allele1"].to_numpy(),
    })


def tile_convention(M):
    """lower/upper_half_diag (one triangle, diag 0.5), lower/upper_unit_diag (one triangle, diag 1), symmetric."""
    d = M.diagonal()
    coo = M.tocoo()
    nz = coo.data != 0
    lower = bool(np.any((coo.row > coo.col) & nz))
    upper = bool(np.any((coo.row < coo.col) & nz))
    side = "lower" if not upper else ("upper" if not lower else None)
    if np.all(d == 0.5):
        if side is None:
            raise TileConventionError("diag 0.5 with both triangles stored")
        return f"{side}_half_diag"
    if np.all(d == 1):
        if side is not None:
            return f"{side}_unit_diag"
        if (abs(M - M.T) > 0).nnz == 0:
            return "symmetric"
        raise TileConventionError("diag 1 with both triangles stored but not symmetric")
    raise TileConventionError(f"diagonal is neither all 0.5 nor all 1 (min {d.min()}, max {d.max()})")


def full_diagonal(M):
    """The diagonal of the full R the stored matrix stands for (float64)."""
    d = M.diagonal().astype(np.float64)
    return d + d if tile_convention(M).endswith("half_diag") else d


def load_tile(npz_path, gz_path, keep=None):
    """(R float64 n x n, variants) for the tile, or for the variant rows `keep` (tile order)."""
    M = sp.load_npz(npz_path)
    conv = tile_convention(M)
    v = read_tile_variants(gz_path)
    if len(v) != M.shape[0]:
        raise TileConventionError(f"{gz_path}: {len(v)} variants vs matrix {M.shape}")
    if keep is None:
        sub = M.toarray()
    else:
        keep = np.unique(np.asarray(keep, dtype=np.int64))
        csr = M.tocsr()
        sub = csr[keep][:, keep].toarray()
        v = v.iloc[keep]
    R = sub.astype(np.float64)
    del sub
    if conv == "symmetric":
        pass
    elif conv.endswith("half_diag"):
        R = R + R.T
    else:
        d = np.diag(R).copy()
        R = R + R.T
        R[np.diag_indices_from(R)] -= d
    if not np.array_equal(np.diag(R), np.ones(R.shape[0])):
        raise TileConventionError(f"{npz_path}: diag != 1 after the {conv} transform")
    return R, v.reset_index(drop=True)


def assemble_region(tile_list, chrom, start, end, keep_positions=None):
    """One R over the union of the tiles' variants in [start, end] (optionally only keep_positions). Each pair's r
    comes from a tile containing both; overlapping tiles must agree within OVERLAP_TOL; pairs in no common tile = 0."""
    keep_positions = None if keep_positions is None else set(int(p) for p in keep_positions)
    per_tile, frames = [], []
    for npz, gz in tile_list:
        v = read_tile_variants(gz)
        m = (v["CHR"] == str(chrom)) & (v["POS"] >= start) & (v["POS"] <= end)
        if keep_positions is not None:
            m &= v["POS"].isin(keep_positions)
        loc = np.flatnonzero(m.to_numpy())
        sel = v.iloc[loc]
        if sel.duplicated(["CHR", "POS", "REF", "ALT"]).any():
            raise ValueError(f"{gz}: duplicate (CHR, POS, REF, ALT) rows")
        per_tile.append((npz, gz, loc, sel))
        frames.append(sel)
    union = (pd.concat(frames, ignore_index=True).drop_duplicates(["CHR", "POS", "REF", "ALT"])
             .sort_values("POS", kind="stable").reset_index(drop=True))
    key = {k: i for i, k in enumerate(zip(union["CHR"], union["POS"], union["REF"], union["ALT"]))}
    n = len(union)
    R = np.zeros((n, n))
    filled = np.zeros((n, n), dtype=bool)
    max_diff = 0.0
    for npz, gz, loc, sel in per_tile:
        if len(loc) == 0:
            continue
        g = np.array([key[k] for k in zip(sel["CHR"], sel["POS"], sel["REF"], sel["ALT"])])
        Rt, _ = load_tile(npz, gz, keep=loc)
        ix = np.ix_(g, g)
        old, f = R[ix], filled[ix]
        if f.any():
            diff = float(np.max(np.abs(old[f] - Rt[f])))
            max_diff = max(max_diff, diff)
            if diff > OVERLAP_TOL:
                raise TileDisagreementError(f"{npz}: overlapping r differs by {diff:.3g} > {OVERLAP_TOL}")
        R[ix] = Rt
        filled[ix] = True
        del Rt, old, f
    if not filled[np.diag_indices(n)].all():
        raise ValueError("a variant without its own diagonal")
    n_zero = int((n * n - int(filled.sum())) // 2)
    stats = {"n_tiles": sum(1 for t in per_tile if len(t[2])), "n_var": n, "n_pairs_zero_filled": n_zero,
             "max_overlap_abs_diff": max_diff}
    return R, union, stats


# --- orientation -----------------------------------------------------------------------------------------------------
def orient_to_reference(R, variants, ref_variants):
    """Keep variants present in ref_variants (CHR:POS + the same unordered allele pair, not palindromic, unique), in
    reference order, with s_i = +1 if ALT == ALT_ref else -1 and R' = D.R.D. The returned frame is ref_variants' rows."""
    ref = ref_variants.reset_index(drop=True)
    at = {}
    for j, (c, p) in enumerate(zip(ref["CHR"].astype(str), ref["POS"].astype(np.int64))):
        at.setdefault((c, int(p)), []).append(j)
    st = {"n_in": len(variants), "n_var_not_in_reference": 0, "n_var_dropped_allele_mismatch": 0,
          "n_var_dropped_palindromic": 0, "n_var_dropped_ambiguous": 0}
    pick = []
    for i, (c, p, a, b) in enumerate(zip(variants["CHR"].astype(str), variants["POS"].astype(np.int64),
                                         variants["REF"], variants["ALT"])):
        cand = at.get((c, int(p)), [])
        if not cand:
            st["n_var_not_in_reference"] += 1
            continue
        alleles = {a, b}
        match = [j for j in cand if {ref.at[j, "REF"], ref.at[j, "ALT"]} == alleles]
        if not match:
            st["n_var_dropped_allele_mismatch"] += 1
        elif alleles in PALINDROMIC:
            st["n_var_dropped_palindromic"] += 1
        elif len(match) > 1:
            st["n_var_dropped_ambiguous"] += 1
        else:
            pick.append((match[0], i, 1.0 if b == ref.at[match[0], "ALT"] else -1.0))
    js = [t[0] for t in pick]
    dup = {j for j in js if js.count(j) > 1}
    if dup:
        st["n_var_dropped_ambiguous"] += sum(1 for t in pick if t[0] in dup)
        pick = [t for t in pick if t[0] not in dup]
    pick.sort()
    ii = np.array([t[1] for t in pick], dtype=np.int64)
    s = np.array([t[2] for t in pick])
    Ro = R[np.ix_(ii, ii)] * np.outer(s, s)
    st["n_out"] = len(pick)
    st["n_flipped"] = int((s < 0).sum())
    return Ro, ref.iloc[[t[0] for t in pick]].reset_index(drop=True), st


# --- .rds I/O --------------------------------------------------------------------------------------------------------
def default_rscript():
    for c in (os.environ.get("RSCRIPT"), RSCRIPT_R4, shutil.which("Rscript")):
        if c and Path(c).is_file():
            return c
    return None


_WRITE_R = r"""
a <- commandArgs(TRUE); n <- as.integer(a[1]); blk <- 1000L
R <- matrix(0, n, n)
con <- file(a[2], "rb")
for (s in seq(1L, n, by = blk)) { e <- min(n, s + blk - 1L); R[, s:e] <- readBin(con, "double", n * (e - s + 1L), size = 8L, endian = "little") }
close(con)
v <- read.table(a[3], header = TRUE, sep = "\t", quote = "", comment.char = "", colClasses = strsplit(a[9], ",")[[1]],
                stringsAsFactors = FALSE)
if (nrow(v) != n) stop(sprintf("%d variants vs n = %d", nrow(v), n))
obj <- list(R = R, variants = v, ld_source = a[5], region_id = a[6], ancestry = a[7])
attr(obj, "ref_alt_source") <- a[8]
saveRDS(obj, paste0(a[4], ".part"))
stopifnot(file.rename(paste0(a[4], ".part"), a[4]))
"""

_READ_R = r"""
a <- commandArgs(TRUE); x <- readRDS(a[1]); n <- nrow(x$R); blk <- 1000L
if (is.null(x$R) || nrow(x$variants) != n) stop("no R or size mismatch")
write.table(x$variants, a[3], sep = "\t", quote = FALSE, row.names = FALSE)
con <- file(a[2], "wb")
for (s in seq(1L, n, by = blk)) { e <- min(n, s + blk - 1L); writeBin(as.double(x$R[, s:e]), con, size = 8L, endian = "little") }
close(con)
"""


def _run_r(code, args, rscript):
    rs = rscript or default_rscript()
    if rs is None:
        raise RuntimeError("no Rscript")
    p = subprocess.run([rs, "-e", code, *map(str, args)], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Rscript failed: {p.stderr.strip()[-2000:]}")


def write_rds(R, variants, out, ld_source, region_id="", ancestry="EUR", ref_alt_source="", rscript=None):
    """list(R, variants, ld_source, region_id, ancestry) via Rscript saveRDS; R passes as raw little-endian float64."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = R.shape[0]
    if R.shape != (n, n) or len(variants) != n:
        raise ValueError(f"R {R.shape} vs {len(variants)} variants")
    cls = ",".join("integer" if c == "POS" else "character" for c in variants.columns)
    with tempfile.TemporaryDirectory(dir=out.parent, prefix=".w_") as td:
        f64, tsv = Path(td) / "R.f64", Path(td) / "v.tsv"
        np.asarray(R, dtype="<f8").T.tofile(f64)  # column-major
        variants.to_csv(tsv, sep="\t", index=False)
        _run_r(_WRITE_R, [n, f64, tsv, out, ld_source, region_id, ancestry, ref_alt_source or "NA", cls], rscript)
    return out


def read_rds(path, rscript=None, tmpdir=None):
    """(R float64, variants) of a panel .rds (CHR as str, POS as int64)."""
    with tempfile.TemporaryDirectory(dir=tmpdir) as td:
        f64, tsv = Path(td) / "R.f64", Path(td) / "v.tsv"
        _run_r(_READ_R, [path, f64, tsv], rscript)
        v = pd.read_csv(tsv, sep="\t", dtype=str, keep_default_na=False)
        v["POS"] = v["POS"].astype(np.int64)
        n = len(v)
        R = np.fromfile(f64, dtype="<f8").reshape((n, n), order="F")
    return R, v


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("tiles", nargs="+")
    f.add_argument("--exts", default="gz,npz")
    a = ap.parse_args(argv)
    if a.cmd == "fetch":
        for t in a.tiles:
            print(*fetch_tile(t, exts=tuple(a.exts.split(","))), sep="\t")
    return 0


if __name__ == "__main__":
    sys.exit(main())
