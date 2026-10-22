"""D-18: restore REF/ALT/EAF onto the frozen bmi.EUR sumstats from the same Yengo 2018 release.

restore: join frozen rows to the source on (CHR, POS, SNP_ID); a row is kept only when the source BETA equals
+/- the frozen BETA and SE and P are equal, each at the frozen string's precision. Kept rows carry the frozen
strings unchanged. Both inputs are sha256-checked against the m1 manifest before any parsing (exit 2).
pin: re-verify inputs against the m1 manifest and write a path/sha256/bytes/role TSV for inputs + outputs.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import os
import random
import subprocess
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

CLASSES = ("exact", "flipped", "value_mismatch", "unjoined")
OUT_HEADER = ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N", "SNP_ID", "TRAIT", "ANCESTRY", "BUILD"]


class ManifestError(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path):
    with open(path) as fh:
        return {r["relative_path"]: r["sha256"] for r in csv.DictReader(fh, delimiter="\t")}


def verify(paths, manifest_path):
    man = load_manifest(manifest_path)
    out = {}
    for p in paths:
        name = Path(p).name
        if name not in man:
            raise ManifestError(f"{name}: not in {manifest_path}")
        got = sha256_file(p)
        if got != man[name]:
            raise ManifestError(f"{name}: sha256 {got} != manifest {man[name]}")
        out[str(p)] = got
    return out


def _tol(s):
    """Half a unit in the last place of the decimal string s (mantissa precision for scientific notation)."""
    s = s.strip().lower()
    mant, _, exp = s.partition("e")
    d = len(mant.split(".", 1)[1]) if "." in mant else 0
    return Decimal(5).scaleb(int(exp or 0) - d - 1)


def same(frozen, source, sign=1):
    try:
        return abs(Decimal(frozen) - sign * Decimal(source)) <= _tol(frozen)
    except InvalidOperation:
        return False


def classify(fz, src):
    """fz: dict BETA/SE/P (frozen strings); src: dict BETA/SE/P. -> (class, sign_uninformative)."""
    if not (same(fz["SE"], src["SE"]) and same(fz["P"], src["P"])):
        return "value_mismatch", False
    plus, minus = same(fz["BETA"], src["BETA"], 1), same(fz["BETA"], src["BETA"], -1)
    if plus:
        return "exact", minus
    if minus:
        return "flipped", False
    return "value_mismatch", False


def _flip_eaf(eaf):
    try:
        return str(Decimal(1) - Decimal(eaf))
    except InvalidOperation:
        return "NA"


def _reader(path):
    fh = gzip.open(path, "rt", newline="")
    return fh, csv.reader(fh, delimiter="\t")


def _index_source(path):
    fh, rd = _reader(path)
    with fh:
        hdr = next(rd)
        ix = {c: hdr.index(c) for c in ("CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF")}
        idx = {}
        for r in rd:
            rec = tuple(r[ix[c]] for c in ("EA", "OA", "BETA", "SE", "P", "EAF"))
            cands = idx.setdefault((r[ix["CHR"]], r[ix["BP"]], r[ix["SNP"]]), [])
            if rec not in cands:
                cands.append(rec)
    return idx


def restore(frozen, source, out_tsv):
    """Write the uncompressed restored TSV. Returns (counts, kept) with kept = [(key, REF, ALT)]."""
    src = _index_source(source)
    counts = {f"n_{c}": 0 for c in CLASSES}
    counts.update(n_frozen=0, n_sign_uninformative=0, n_ambiguous_source=0)
    kept = []
    fh, rd = _reader(frozen)
    with fh, open(out_tsv, "w", newline="") as oh:
        hdr = next(rd)
        w = csv.writer(oh, delimiter="\t", lineterminator="\n")
        w.writerow(OUT_HEADER)
        for r in rd:
            counts["n_frozen"] += 1
            f = dict(zip(hdr, r))
            key = (f["CHR"], f["POS"], f["SNP_ID"])
            cands = src.get(key)
            if not cands:
                counts["n_unjoined"] += 1
                continue
            if len(cands) > 1:
                counts["n_ambiguous_source"] += 1
                counts["n_value_mismatch"] += 1
                continue
            ea, oa, beta, se, p, eaf = cands[0]
            cls, uninf = classify(f, {"BETA": beta, "SE": se, "P": p})
            counts[f"n_{cls}"] += 1
            if cls == "value_mismatch":
                continue
            counts["n_sign_uninformative"] += uninf
            ref, alt, eaf_out = (oa, ea, eaf) if cls == "exact" else (ea, oa, _flip_eaf(eaf))
            w.writerow([f["CHR"], f["POS"], ref, alt, f["BETA"], f["SE"], f["P"], eaf_out, f["N"], f["SNP_ID"],
                        f["TRAIT"], f["ANCESTRY"], f["BUILD"]])
            kept.append((key, ref, alt))
    counts["n_kept"] = counts["n_exact"] + counts["n_flipped"]
    return counts, kept


def raw_crosscheck(raw, kept, n, seed):
    """Fraction of a seeded sample of kept rows whose raw Tested_Allele equals the assigned ALT (recorded, not gated)."""
    pick = sorted(random.Random(seed).sample(range(len(kept)), min(n, len(kept))))
    want = {kept[i][0] for i in pick}
    alleles = {}
    fh, rd = _reader(raw)
    with fh:
        hdr = [c.strip() for c in next(rd)]
        ix = {c: hdr.index(c) for c in ("CHR", "POS", "SNP", "Tested_Allele", "Other_Allele")}
        for r in rd:
            key = tuple(r[ix[c]].strip() for c in ("CHR", "POS", "SNP"))
            if key in want:
                alleles.setdefault(key, (r[ix["Tested_Allele"]].strip().upper(), r[ix["Other_Allele"]].strip().upper()))
    res = dict(raw_n_sampled=len(pick), raw_n_alt_match=0, raw_n_ref_match=0, raw_n_absent=0, raw_n_other=0)
    for i in pick:
        key, ref, alt = kept[i]
        a = alleles.get(key)
        if a is None:
            res["raw_n_absent"] += 1
        elif a[0] == alt.upper() and a[1] == ref.upper():
            res["raw_n_alt_match"] += 1
        elif a[0] == ref.upper() and a[1] == alt.upper():
            res["raw_n_ref_match"] += 1
        else:
            res["raw_n_other"] += 1
    present = res["raw_n_sampled"] - res["raw_n_absent"]
    res["raw_alt_match_rate"] = f"{res['raw_n_alt_match'] / present:.6f}" if present else "NA"
    return res


def _bgzip_tabix(tsv, out, bgzip, tabix):
    with open(out, "wb") as oh:
        subprocess.run([bgzip, "-c", str(tsv)], stdout=oh, check=True)
    subprocess.run([tabix, "-f", "-s", "1", "-b", "2", "-e", "2", "-S", "1", str(out)], check=True)


def cmd_restore(a):
    shas = verify([a.frozen, a.source], a.manifest)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tsv = out.with_name(out.name + ".tmp.tsv")
    try:
        counts, kept = restore(a.frozen, a.source, tsv)
        _bgzip_tabix(tsv, out, a.bgzip, a.tabix)
    finally:
        if tsv.exists():
            tsv.unlink()
    rows = [("n_frozen", counts["n_frozen"], "data rows in the frozen file")]
    rows += [(f"n_{c}", counts[f"n_{c}"], "class") for c in CLASSES]
    rows += [("n_kept", counts["n_kept"], "exact + flipped; rows in the output"),
             ("n_sign_uninformative", counts["n_sign_uninformative"], "kept as exact; BETA equal to 0 at frozen precision"),
             ("n_ambiguous_source", counts["n_ambiguous_source"], "counted in value_mismatch; >1 distinct source rows"),
             ("sha256_frozen", shas[str(a.frozen)], Path(a.frozen).name),
             ("sha256_source", shas[str(a.source)], Path(a.source).name),
             ("sha256_out", sha256_file(out), out.name),
             ("sha256_out_tbi", sha256_file(f"{out}.tbi"), out.name + ".tbi")]
    if a.raw:
        res = raw_crosscheck(a.raw, kept, a.raw_sample, a.seed)
        note = f"{Path(a.raw).name} sha256 {sha256_file(a.raw)}; seed {a.seed}; recorded, not gated"
        rows += [(k, v, note) for k, v in res.items()]
    with open(a.report, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["metric", "value", "note"])
        w.writerows(rows)


def cmd_pin(a):
    shas = verify(a.inputs, a.manifest)
    rows = [(str(p), shas[str(p)], os.path.getsize(p), "input") for p in a.inputs]
    rows += [(str(p), sha256_file(p), os.path.getsize(p), "output") for p in a.outputs]
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["path", "sha256", "bytes", "role"])
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("restore")
    for k in ("--frozen", "--source", "--manifest", "--out", "--report", "--bgzip", "--tabix"):
        r.add_argument(k, required=True)
    r.add_argument("--raw")
    r.add_argument("--raw-sample", type=int, default=10000)
    r.add_argument("--seed", type=int, default=20261021)
    p = sub.add_parser("pin")
    p.add_argument("--manifest", required=True)
    p.add_argument("--inputs", nargs="+", required=True)
    p.add_argument("--outputs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        (cmd_restore if a.cmd == "restore" else cmd_pin)(a)
    except ManifestError as e:
        print(f"REFUSED (sha256): {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
