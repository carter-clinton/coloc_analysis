"""Panel manifests (memory-bounded .rds inspection through Rscript) and the D-12a known-answer checks.

    python -m ta_r4.panel_manifest manifest --panel-dir D --ancestry EUR --source S --build GRCh37 \
        --n-samples N --out M [--rscript R]
    python -m ta_r4.panel_manifest known-answers --out data/r4/findings/panel_known_answers.tsv [--rscript R]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import subprocess
import sys
from pathlib import Path

from ta_r4 import paths as r4paths

TOL = 1e-8
ABS_TOL = 1e-12
SH2B3_LEGACY_N_VAR = 895
COLS = ["ancestry", "region_safe", "path", "md5", "sha256", "size_bytes", "n_var", "n_samples", "build", "source",
        "has_ref_alt", "r_kind", "identity_exact", "max_asym", "max_diag_dev", "all_finite", "ld_source"]
FINDING_COLS = ["check", "ancestry", "region_safe", "expected", "observed", "status", "detail"]
MANIFESTS = {
    "legacy_repro": r4paths.panel_manifest_path("repro_routeC", "EUR"),
    "EUR_1kg_r4": r4paths.panel_manifest_path("A3_1kg", "EUR"),
    "EUR_identity_r4": r4paths.panel_manifest_path("A2_identity", "EUR"),
    "k2d_identity": r4paths.panel_manifest_path("repro_k2d_routeC", "EUR"),
}


class ManifestError(RuntimeError):
    pass


_INSPECT_R = r"""
a <- commandArgs(TRUE); blk <- as.integer(a[1])
for (p in a[-1]) {
  x <- readRDS(p); v <- x$variants
  hra <- all(c("REF", "ALT") %in% names(v))
  src <- if (is.null(x$ld_source)) "NA" else as.character(x$ld_source)
  if (is.null(x$R)) {
    out <- c(nrow(v), "null", "NA", "NA", "NA", "NA")
  } else {
    R <- x$R; n <- nrow(R)
    if (ncol(R) != n || nrow(v) != n) stop(sprintf("%s: R %dx%d vs %d variants", p, n, ncol(R), nrow(v)))
    asym <- 0; fin <- TRUE; ident <- TRUE
    dd <- max(abs(diag(R) - 1))
    for (s in seq(1, n, by = blk)) {
      e <- min(n, s + blk - 1); B <- R[s:e, , drop = FALSE]; k <- e - s + 1
      fin <- fin && all(is.finite(B))
      if (fin) asym <- max(asym, max(abs(B - t(R[, s:e, drop = FALSE]))))
      ident <- ident && all(B[cbind(seq_len(k), s:e)] == 1) && sum(B != 0) == k
    }
    out <- c(n, "matrix", tolower(ident), if (fin) sprintf("%.3e", asym) else "NA",
             if (is.finite(dd)) sprintf("%.3e", dd) else "NA", tolower(fin))
  }
  cat(paste(c(p, out, tolower(hra), src), collapse = "\t"), "\n", sep = "")
}
"""

_COMPARE_R = r"""
a <- commandArgs(TRUE); blk <- as.integer(a[1]); mode <- a[2]
x <- readRDS(a[3]); y <- readRDS(a[4])
if (mode == "abs") {
  nx <- nrow(x$R); ny <- nrow(y$R)
  same_ids <- nx == ny && identical(as.character(x$variants$SNP_ID), as.character(y$variants$SNP_ID)) &&
    identical(as.integer(x$variants$POS), as.integer(y$variants$POS))
  md <- NA
  if (same_ids) {
    md <- 0
    for (s in seq(1, nx, by = blk)) {
      e <- min(nx, s + blk - 1)
      md <- max(md, max(abs(abs(x$R[s:e, , drop = FALSE]) - abs(y$R[s:e, , drop = FALSE]))))
    }
  }
  cat(nx, ny, tolower(same_ids), if (is.na(md)) "NA" else sprintf("%.3e", md), sep = "\t"); cat("\n")
} else {
  cat(tolower(identical(x$variants, y$variants)), nrow(x$variants), nrow(y$variants), sep = "\t"); cat("\n")
}
"""


def _rscript(rscript):
    return rscript or os.environ.get("RSCRIPT", "Rscript")


def _digests(path):
    md5, sha = hashlib.md5(), hashlib.sha256()
    with open(path, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 20), b""):
            md5.update(buf)
            sha.update(buf)
    return md5.hexdigest(), sha.hexdigest()


def _run_r(code, args, rscript):
    p = subprocess.run([_rscript(rscript), "-e", code, *map(str, args)], capture_output=True, text=True)
    if p.returncode != 0:
        raise ManifestError(f"Rscript failed: {p.stderr.strip()[-2000:]}")
    return [line.split("\t") for line in p.stdout.splitlines() if line.strip()]


def inspect(paths, rscript=None, block=2000):
    """One dict per .rds (n_var, r_kind, identity_exact, max_asym, max_diag_dev, all_finite, has_ref_alt)."""
    out = {}
    for f in _run_r(_INSPECT_R, [block, *paths], rscript):
        p, n, kind, ident, asym, dd, fin, hra, src = f
        out[p] = dict(n_var=n, r_kind=kind, identity_exact=ident, max_asym=asym, max_diag_dev=dd,
                      all_finite=fin, has_ref_alt=hra, ld_source=src)
    return out


def _check(rec, p):
    if rec["r_kind"] != "matrix":
        return
    if rec["all_finite"] != "true":
        raise ManifestError(f"{p}: R is not all finite")
    if float(rec["max_asym"]) > TOL:
        raise ManifestError(f"{p}: R not symmetric within {TOL} (max {rec['max_asym']})")
    if float(rec["max_diag_dev"]) > TOL:
        raise ManifestError(f"{p}: diag != 1 within {TOL} (max {rec['max_diag_dev']})")


def _rel(p, root):
    p = Path(p)
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def write_manifest(panel_dir, ancestry, source, build, n_samples, out, rscript=None, block=2000, root=None):
    """Append one row per {panel_dir}/*.rds; (ancestry, region_safe) must stay unique. Nothing written on error."""
    root = Path(root) if root else Path.cwd()
    files = sorted(Path(panel_dir).glob("*.rds"))
    if not files:
        raise ManifestError(f"no .rds under {panel_dir}")
    out = Path(out)
    rows = []
    if out.exists():
        with open(out, newline="") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
    seen = {(r["ancestry"], r["region_safe"]) for r in rows}
    recs = inspect([str(f) for f in files], rscript, block)
    for f in files:
        key = (ancestry, f.stem)
        if key in seen:
            raise ManifestError(f"duplicate key {key} in {out}")
        seen.add(key)
        rec = recs[str(f)]
        _check(rec, f)
        md5, sha = _digests(f)
        rows.append(dict(ancestry=ancestry, region_safe=f.stem, path=_rel(f, root), md5=md5, sha256=sha,
                         size_bytes=str(f.stat().st_size), n_samples=str(n_samples), build=build, source=source,
                         **rec))
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows


def _rows(manifest):
    with open(manifest, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def md5_mismatches(manifest, root=None):
    """[(ancestry, region_safe, manifest_md5, disk_md5)] for rows whose file differs (or is missing)."""
    root = Path(root) if root else Path.cwd()
    bad = []
    for r in _rows(manifest):
        p = Path(r["path"])
        p = p if p.is_absolute() else root / p
        got = _digests(p)[0] if p.is_file() else "MISSING"
        if got != r["md5"]:
            bad.append((r["ancestry"], r["region_safe"], r["md5"], got))
    return bad


def known_answers(root, out, rscript=None, block=2000):
    """D-12a checks; every check instance is one row of `out`. Only sh2b3_legacy_n_var may be a FINDING."""
    root = Path(root)
    man = {k: _rows(root / v) for k, v in MANIFESTS.items()}
    rows = []

    def add(check, anc, reg, exp, obs, ok, detail="", finding=False):
        rows.append(dict(check=check, ancestry=anc, region_safe=reg, expected=exp, observed=obs,
                         status="PASS" if ok else ("FINDING" if finding else "FAIL"), detail=detail))

    for k, v in MANIFESTS.items():
        bad = {(a, r): got for a, r, _, got in md5_mismatches(root / v, root)}
        for r in man[k]:
            got = bad.get((r["ancestry"], r["region_safe"]), r["md5"])
            add("md5", r["ancestry"], r["region_safe"], r["md5"], got, got == r["md5"], k)

    r4 = {r["region_safe"]: r for r in man["EUR_1kg_r4"]}
    for leg in man["legacy_repro"]:
        reg = leg["region_safe"]
        n4, nl, same, md = _run_r(_COMPARE_R, [block, "abs", root / r4[reg]["path"], root / leg["path"]],
                                  rscript)[0]
        add("n_var_equal", "EUR", reg, nl, n4, n4 == nl and same == "true", f"same_snp_id_pos={same}")
        add("abs_r_equal", "EUR", reg, f"<={ABS_TOL:g}", md, md != "NA" and float(md) <= ABS_TOL)

    for idr in man["EUR_identity_r4"]:
        reg = idr["region_safe"]
        same, ni, n4 = _run_r(_COMPARE_R, [block, "variants", root / idr["path"], root / r4[reg]["path"]],
                              rscript)[0]
        add("identity_variants_identical", "EUR", reg, "true", same,
            same == "true" and idr["identity_exact"] == "true", f"n={ni}/{n4} identity_exact={idr['identity_exact']}")

    for k, want in (("EUR_1kg_r4", "true"), ("legacy_repro", "false")):
        for r in man[k]:
            add("has_ref_alt", r["ancestry"], r["region_safe"], want, r["has_ref_alt"], r["has_ref_alt"] == want, k)

    sh = next(r for r in man["legacy_repro"] if r["region_safe"] == "SH2B3_12q24")
    add("sh2b3_legacy_n_var", "EUR", "SH2B3_12q24", str(SH2B3_LEGACY_N_VAR), sh["n_var"],
        sh["n_var"] == str(SH2B3_LEGACY_N_VAR), "ta-sh2b3-W1.5-ld-audit.md", finding=True)

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FINDING_COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest")
    for k in ("--panel-dir", "--ancestry", "--source", "--build", "--n-samples", "--out"):
        m.add_argument(k, required=True)
    m.add_argument("--rscript")
    k = sub.add_parser("known-answers")
    k.add_argument("--out", required=True)
    k.add_argument("--rscript")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "manifest":
            if a.ancestry not in ("EUR", "AFR"):
                raise ManifestError(f"--ancestry must be EUR or AFR, got {a.ancestry}")
            rows = write_manifest(a.panel_dir, a.ancestry, a.source, a.build, a.n_samples, a.out, a.rscript)
            print(f"{a.out}: +{len(rows)} rows total")
        else:
            rows = known_answers(Path.cwd(), a.out, a.rscript)
            for r in rows:
                if r["status"] != "PASS":
                    print("\t".join(r.values()))
            print(f"{a.out}: {len(rows)} checks, {sum(r['status'] == 'PASS' for r in rows)} PASS")
    except ManifestError as e:
        print(f"PANEL_MANIFEST_REFUSED: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
