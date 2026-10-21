"""Deterministic GWAS-null window selection (third admissible negative-control set).

Conditions on GWAS P-values and variant counts only, never on any arm outcome.
Also renders config/ta_r4/regions_r4.csv (`--emit-regions`).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import math
import sys
from pathlib import Path

import numpy as np
import yaml

NC_IDS = {
    "OCA2/HERC2": "NC_OCA2_HERC2", "SLC24A5": "NC_SLC24A5", "MC1R": "NC_MC1R", "TYR": "NC_TYR",
    "IRF4": "NC_IRF4", "ABO": "NC_ABO", "RH": "NC_RH", "FUT1/FUT2": "NC_FUT1_FUT2", "KEL": "NC_KEL",
}
NC_SETS = ("cosmetic", "blood_group")
FLANK = 1_000_000
AUTOSOMES = {str(c) for c in range(1, 23)}


def tile_index(pos: int, window: int) -> int:
    return (pos - 1) // window


def tile_bounds(k: int, window: int) -> tuple[int, int]:
    return k * window + 1, (k + 1) * window


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def exclusion_zones(regions_curated, nc_doc) -> list[tuple[int, int, int]]:
    """(chr, start, end) zones: curated regions (any ancestry) and cosmetic/blood_group +/- 1 Mb, plus HLA."""
    zones = []
    with open(regions_curated, newline="") as fh:
        for r in csv.DictReader(fh):
            c = r["chr"].replace("chr", "")
            if c in AUTOSOMES:
                zones.append((int(c), int(float(r["start"])) - FLANK, int(float(r["end"])) + FLANK))
    sets = nc_doc["curated_sets"]
    for name in NC_SETS:
        for r in sets[name]["regions_grch37"]:
            zones.append((int(r["chr"]), int(r["start"]) - FLANK, int(r["end"]) + FLANK))
    hla = sets["hla_immune"]["region_grch37"]
    zones.append((int(hla["chr"]), int(hla["start"]), int(hla["end"])))
    return zones


def _trait_anc(path) -> tuple[str, str]:
    parts = Path(path).name.split(".")
    return parts[0], parts[1]


def scan(path, window, count):
    """Per-tile min P (and variant count when `count`) for one sumstats file."""
    minp, nvar = {}, {}
    with gzip.open(path, "rt", newline="") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        ic, ip, iq = header.index("CHR"), header.index("POS"), header.index("P")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            c = f[ic].replace("chr", "")
            if c not in AUTOSOMES:
                continue
            try:
                p = float(f[iq])
            except ValueError:
                continue
            if not math.isfinite(p):
                continue
            key = (int(c), (int(f[ip]) - 1) // window)
            if p < minp.get(key, math.inf):
                minp[key] = p
            if count:
                nvar[key] = nvar.get(key, 0) + 1
    return minp, nvar


def _fmt_p(p: float) -> str:
    return f"{p:.6g}"


def select(args) -> int:
    expected = {}
    with open(args.sha256_manifest, newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            expected[r["relative_path"]] = r["sha256"]
    input_sha = {}
    for p in args.sumstats:
        got = sha256_file(p)
        if expected.get(Path(p).name) != got:
            print(f"sha256 mismatch for {p}: manifest {expected.get(Path(p).name)} != {got}", file=sys.stderr)
            return 2
        input_sha[Path(p).name] = got

    with open(args.negative_controls) as fh:
        zones = exclusion_zones(args.regions_curated, yaml.safe_load(fh))

    minp: dict = {}
    counts: dict[str, dict] = {}
    for p in args.sumstats:
        trait, anc = _trait_anc(p)
        mp, nv = scan(p, args.window, anc == "EUR")
        for k, v in mp.items():
            if v < minp.get(k, math.inf):
                minp[k] = v
        if anc == "EUR":
            counts[trait] = nv
    eur_traits = sorted(counts)

    cands = []
    for key in sorted(minp):
        c, k = key
        s, e = tile_bounds(k, args.window)
        if any(zc == c and s <= zb and e >= za for zc, za, zb in zones):
            continue
        if minp[key] < args.pmax:
            continue
        nv = [counts[t].get(key, 0) for t in eur_traits]
        if min(nv) < args.min_variants:
            continue
        cands.append((c, s, e, nv, minp[key]))

    if len(cands) < args.n_select:
        print(f"only {len(cands)} candidates < {args.n_select}", file=sys.stderr)
        return 3
    idx = np.random.default_rng(args.seed).choice(len(cands), args.n_select, replace=False)
    chosen = sorted((cands[i] for i in idx), key=lambda x: (x[0], x[1]))

    head = ["chr", "start", "end"] + [f"n_var_{t}" for t in eur_traits] + ["min_p"]
    buf = io.StringIO()
    buf.write("\t".join(head) + "\n")
    for c, s, e, nv, mp in cands:
        buf.write("\t".join(map(str, [c, s, e, *nv])) + f"\t{_fmt_p(mp)}\n")
    Path(args.candidates_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.candidates_out).write_text(buf.getvalue())

    out = io.StringIO()
    out.write("\t".join(["region_id"] + head) + "\n")
    for i, (c, s, e, nv, mp) in enumerate(chosen, 1):
        out.write("\t".join(map(str, [f"NC_NULL_{i:02d}", c, s, e, *nv])) + f"\t{_fmt_p(mp)}\n")
    out.write(f"# n_candidates\t{len(cands)}\n")
    out.write(f"# candidates_sha256\t{sha256_file(args.candidates_out)}\n")
    out.write(f"# rule\twindow={args.window} pmax={args.pmax:g} min_variants={args.min_variants} "
              f"n_select={args.n_select} seed={args.seed}\n")
    for name in sorted(input_sha):
        out.write(f"# input_sha256\t{name}\t{input_sha[name]}\n")
    Path(args.selected_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.selected_out).write_text(out.getvalue())
    return 0


def regions_r4_text(regions_curated, negative_controls, selection) -> str:
    """12 curated rows verbatim + 9 cosmetic/blood_group rows + 10 NC_NULL rows."""
    text = Path(regions_curated).read_text()
    if not text.endswith("\n"):
        text += "\n"
    with open(negative_controls) as fh:
        sets = yaml.safe_load(fh)["curated_sets"]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for name in NC_SETS:
        for r in sets[name]["regions_grch37"]:
            w.writerow([NC_IDS[r["gene"]], "EUR", r["chr"], r["start"], r["end"], "NA", r["gene"], "",
                        "negative_control", ""])
    with open(selection) as fh:
        rows = list(csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t"))
    for r in rows:
        w.writerow([r["region_id"], "EUR", r["chr"], r["start"], r["end"], "NA", "NA", "",
                    "negative_control_gwas_null", ""])
    return text + buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sumstats", nargs="+")
    ap.add_argument("--sha256-manifest")
    ap.add_argument("--regions-curated", required=True)
    ap.add_argument("--negative-controls", required=True)
    ap.add_argument("--window", type=int, default=250_000)
    ap.add_argument("--pmax", type=float, default=1e-5)
    ap.add_argument("--min-variants", type=int, default=200)
    ap.add_argument("--n-select", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20261021)
    ap.add_argument("--candidates-out")
    ap.add_argument("--selected-out")
    ap.add_argument("--emit-regions", metavar="OUT",
                    help="write regions_r4.csv from --selected-out (an existing selection); no scan")
    args = ap.parse_args(argv)
    if args.emit_regions:
        Path(args.emit_regions).write_text(
            regions_r4_text(args.regions_curated, args.negative_controls, args.selected_out))
        return 0
    if not (args.sumstats and args.sha256_manifest and args.candidates_out and args.selected_out):
        ap.error("--sumstats, --sha256-manifest, --candidates-out and --selected-out are required")
    return select(args)


if __name__ == "__main__":
    sys.exit(main())
