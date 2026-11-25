"""r4 sumstats in the r4 catalog's orientation (W3f 15.8a2; Carter Q-158R2 D, Q-158OR A, Q-158PAL A;
DEC-2026-11-25-ta-r4-sumstats-orientation).

The fit's catalog join (run_susie_rss.R) is exact on CHR:POS:REF:ALT, so a sumstats row written the other way round
from its region's r4 catalog never reaches a fit. Each sumstats row in an r4 region window is classified against that
region's catalog on the normalized allele key (collector_drop_audit.norm_key; swapped = (chr, pos, ALT, REF)):
  exact          key in the catalog, swapped key not
  swapped_only   swapped key in the catalog, key not       -> flipped
  both           both in the catalog
  absent         neither, or REF/ALT unusable ("", NA, N, -)
A flip exchanges the REF and ALT strings, toggles the BETA sign on the string (a zero BETA unchanged) and sets
EAF := 1 - EAF in exact decimal arithmetic (NA/empty unchanged); every other byte of the line, every other line and
every line outside the windows is unchanged. A/T and C/G SNPs follow the same rule (Q-158PAL A).

  python -m ta_r4.sumstats_orient harmonize --trait T --anc A --bgzip B --tabix X --report JSON
  python -m ta_r4.sumstats_orient verify-unflip --trait T --anc A --report JSON
  python -m ta_r4.sumstats_orient measure --files F... --tabix X --out TSV      (F = trait:anc:path)
  python -m ta_r4.sumstats_orient pin --manifest manifests/sumstats_r4_sha256.tsv
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

from ta_r4 import paths
from ta_r4.collector_drop_audit import catalog_keys, norm_key, r4_regions
from ta_r4.commands import safe_region_id

HEADER = ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N", "SNP_ID", "TRAIT", "ANCESTRY", "BUILD"]
CLASSES = ("exact", "swapped_only", "both", "absent")
OUT_DIR = f"{paths.R4}/sumstats"
#: The 8 r4 catalog inputs in collector order (CATALOG_SUMSTATS["r4"], config/pipeline.yaml order), typed: the
#: sources of the oriented copies. Tests 9, 11, 14 and the harmonize CLI read this constant, never paths.sumstats_path,
#: so 15.8a3's switch of sumstats_path cannot repoint them at the oriented files.
CATALOG_SOURCES = (
    ("bmi", "EUR", "data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz"),
    ("t2d", "EUR", "data/processed/sumstats_harmonized/t2d.EUR.tsv.bgz"),
    ("t2d", "AFR", "data/processed/sumstats_harmonized/t2d.AFR.tsv.bgz"),
    ("hypertension", "EUR", "data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz"),
    ("asthma", "EUR", "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz"),
    ("asthma", "AFR", "data/r4/sumstats/asthma.AFR.grch37_lifted_strand.tsv.bgz"),
    ("stroke", "EUR", "data/processed/sumstats_harmonized/stroke.EUR.tsv.bgz"),
    ("stroke", "AFR", "data/processed/sumstats_harmonized/stroke.AFR.tsv.bgz"),
)
SUMSTATS_MANIFEST = f"{paths.MAN}/sumstats_r4_sha256.tsv"
CATALOGS_MANIFEST = f"{paths.MAN}/catalogs_sha256.tsv"
_UNUSABLE = {"", "NA", "N", "-"}
_PAL = {"AT", "TA", "CG", "GC"}
_I = {c: i for i, c in enumerate(HEADER)}
_KEEP = [i for i in range(len(HEADER)) if HEADER[i] not in ("REF", "ALT", "BETA", "EAF")]


class OrientError(RuntimeError):
    pass


def oriented_path(trait, anc) -> str:
    return paths.oriented_sumstats_path(trait, anc)


def source_path(trait, anc) -> str:
    for t, a, p in CATALOG_SOURCES:
        if (t, a) == (trait, anc):
            return p
    raise OrientError(f"{trait}.{anc} is not a catalog source")


def classify(key, catalog_keys) -> str:
    swapped = (key[0], key[1], key[3], key[2])
    e, s = key in catalog_keys, swapped in catalog_keys
    if e and not s:
        return "exact"
    if s and not e:
        return "swapped_only"
    return "both" if e else "absent"


def is_palindromic(ref, alt) -> bool:
    r, a = ref.strip().upper(), alt.strip().upper()
    return len(r) == 1 and len(a) == 1 and r + a in _PAL


def _usable(ref, alt):
    return ref.strip().upper() not in _UNUSABLE and alt.strip().upper() not in _UNUSABLE


def _toggle_beta(beta):
    try:
        d = Decimal(beta)
    except InvalidOperation:
        raise OrientError(f"non-numeric BETA {beta!r} on a row to flip") from None
    if beta != beta.strip() or not d.is_finite():
        raise OrientError(f"BETA {beta!r} on a row to flip")
    if d == 0:
        return beta
    if beta.startswith("-"):
        return beta[1:]
    if beta.startswith("+"):
        return "-" + beta[1:]
    return "-" + beta


def _one_minus(eaf):
    if eaf == "" or eaf.upper() == "NA":
        return eaf
    try:
        d = Decimal(eaf)
    except InvalidOperation:
        raise OrientError(f"non-numeric EAF {eaf!r} on a row to flip") from None
    if eaf != eaf.strip() or not d.is_finite() or d < 0 or d > 1:
        raise OrientError(f"EAF {eaf!r} outside [0, 1] on a row to flip")
    with localcontext() as ctx:
        ctx.prec = 200
        return str(Decimal(1) - d)


def flip_fields(f: list[str]) -> list[str]:
    """REF<->ALT, BETA sign toggled on the string, EAF := 1 - EAF (Decimal); the other fields identical."""
    if len(f) != len(HEADER):
        raise OrientError(f"{len(f)} fields, expected {len(HEADER)}")
    g = list(f)
    g[_I["REF"]], g[_I["ALT"]] = f[_I["ALT"]], f[_I["REF"]]
    g[_I["BETA"]] = _toggle_beta(f[_I["BETA"]])
    g[_I["EAF"]] = _one_minus(f[_I["EAF"]])
    return g


def windows(repo=".") -> list[tuple[str, str, int, int]]:
    """(region_safe, chr, start, end) of the r4 catalogs, regions_r4.csv order, bounds inclusive."""
    repo = Path(repo)
    want = set(r4_regions(repo))
    out = []
    with open(repo / paths.regions_csv(), newline="") as fh:
        for r in csv.DictReader(fh):
            rs = safe_region_id(r["region_id"])
            if rs in want:
                c = str(r["chr"]).replace("chr", "").replace("CHR", "")
                out.append((rs, c, int(float(r["start"])), int(float(r["end"]))))
    if sorted(w[0] for w in out) != sorted(want):
        raise OrientError("regions_r4.csv and catalogs_sha256.tsv disagree on the r4 regions")
    return out


def catalog_keys_by_region(wins, repo=".") -> dict:
    return {w[0]: catalog_keys(Path(repo) / paths.catalog_path("r4", w[0])) for w in wins}


def _by_chr(wins):
    d = defaultdict(list)
    for rs, c, s, e in wins:
        d[str(c)].append((s, e, rs))
    return d


def _window_of(f, bychr):
    c = f[0].strip()
    for pre in ("chr", "CHR"):
        if c.startswith(pre):
            c = c[len(pre):]
            break
    ws = bychr.get(c)
    if not ws:
        return None
    try:
        pos = int(f[1])
    except ValueError:
        raise OrientError(f"non-integer POS {f[1]!r} on chromosome {c}") from None
    for s, e, rs in ws:
        if s <= pos <= e:
            return rs
    return None


def _split(line, lineno):
    eol = "\n" if line.endswith("\n") else ""
    f = line[: len(line) - len(eol)].split("\t")
    if len(f) != len(HEADER):
        raise OrientError(f"line {lineno}: {len(f)} fields, expected {len(HEADER)}")
    return f, eol


def row_class(f, cat):
    if not _usable(f[2], f[3]):
        return "absent"
    return classify(norm_key(f[0], f[1], f[2], f[3]), cat)


def _open_text(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", newline="")
    return open(path, newline="")


def _dups(counter):
    return sum(v - 1 for v in counter.values() if v > 1)


def _numeric(x):
    try:
        return float(x)
    except ValueError:
        return None


def harmonize(src, out_tsv, windows, catalog_keys_by_region) -> dict:
    """Write src (gzip TSV) to out_tsv (plain TSV) with the swapped_only rows flipped; counts per region."""
    bychr = _by_chr(windows)
    reg = {w[0]: Counter() for w in windows}
    kb, ka = defaultdict(Counter), defaultdict(Counter)
    sid_b, sid_a = defaultdict(lambda: defaultdict(set)), defaultdict(lambda: defaultdict(set))
    n_lines = n_flipped = 0
    try:
        with _open_text(src) as fh, open(out_tsv, "w", newline="") as oh:
            head = fh.readline()
            if head.rstrip("\n").split("\t") != HEADER:
                raise OrientError(f"{src}: header {head.rstrip()!r} != {HEADER}")
            oh.write(head)
            for lineno, line in enumerate(fh, start=2):
                f, eol = _split(line, lineno)
                n_lines += 1
                rs = _window_of(f, bychr)
                if rs is None:
                    oh.write(line)
                    continue
                cls = row_class(f, catalog_keys_by_region[rs])
                c = reg[rs]
                c["n_rows"] += 1
                c[cls] += 1
                key = norm_key(f[0], f[1], f[2], f[3])
                kb[rs][key] += 1
                sid = f[_I["SNP_ID"]]
                if cls == "swapped_only":
                    g = flip_fields(f)
                    n_flipped += 1
                    c["n_flipped"] += 1
                    if is_palindromic(f[2], f[3]):
                        c["n_flipped_palindromic"] += 1
                        e = _numeric(f[_I["EAF"]])
                        if e is not None and 0.4 <= e <= 0.6:
                            c["n_flipped_palindromic_eaf_0.4_0.6"] += 1
                    after = (key[0], key[1], key[3], key[2])
                    oh.write("\t".join(g) + eol)
                else:
                    after = key
                    oh.write(line)
                ka[rs][after] += 1
                if sid and sid != "NA":
                    if cls in ("exact", "both"):
                        sid_b[rs][sid].add(key)
                    if cls != "absent":
                        sid_a[rs][sid].add(after)
        for rs in reg:
            new = [k for k, v in ka[rs].items() if v > 1 and v > kb[rs].get(k, 0)]
            if new:
                k = sorted(new)[0]
                raise OrientError(f"{src}: flipping creates a duplicate allele key in {rs} at {k[0]}:{k[1]} "
                                  f"({len(new)} new duplicate keys)")
    except BaseException:
        if os.path.exists(out_tsv):
            os.unlink(out_tsv)
        raise
    regions = {}
    for w in windows:
        rs, c = w[0], reg[w[0]]
        regions[rs] = {k: c[k] for k in ("n_rows",) + CLASSES + (
            "n_flipped", "n_flipped_palindromic", "n_flipped_palindromic_eaf_0.4_0.6")}
        regions[rs].update(dup_keys_before=_dups(kb[rs]), dup_keys_after=_dups(ka[rs]),
                           multikey_sid_before=sum(len(v) > 1 for v in sid_b[rs].values()),
                           multikey_sid_after=sum(len(v) > 1 for v in sid_a[rs].values()))
    return {"src": str(src), "n_lines": n_lines, "n_window_rows": sum(r["n_rows"] for r in regions.values()),
            "n_flipped": n_flipped, "regions": regions}


# ---- verify_unflip: an independent re-read; shares no classification or flip code with harmonize ----

def _vkey(f):
    up = lambda x: x.strip().upper()
    return (up(f[0]).removeprefix("CHR"), int(f[1]), up(f[2]), up(f[3]))


def _vflip_ok(s, o):
    if len(o) != len(s):
        return False
    if o[2] != s[3] or o[3] != s[2]:
        return False
    if any(o[i] != s[i] for i in _KEEP):
        return False
    b, ob = s[4], o[4]
    if Decimal(b) == 0:
        if ob != b:
            return False
    elif not ((b.startswith("-") and ob == b[1:]) or (not b.startswith("-") and ob == "-" + b.removeprefix("+"))):
        return False
    e, oe = s[7], o[7]
    if e == "" or e.upper() == "NA":
        return oe == e
    with localcontext() as ctx:
        ctx.prec = 200
        return Decimal(oe) + Decimal(e) == 1


def verify_unflip(src, out, windows, catalog_keys_by_region) -> dict:
    """Each out line is the src line, or (only on a swapped_only row) the src line flipped; no new duplicate key."""
    spans = [(str(c), s, e, rs) for rs, c, s, e in windows]
    kb, ka = defaultdict(Counter), defaultdict(Counter)
    per = {w[0]: Counter() for w in windows}
    n = n_flip = 0
    with _open_text(src) as a, _open_text(out) as b:
        ha, hb = a.readline(), b.readline()
        if ha != hb or ha.rstrip("\n").split("\t") != HEADER:
            raise OrientError("verify_unflip: header differs")
        while True:
            x, y = a.readline(), b.readline()
            if not x and not y:
                break
            n += 1
            if not x or not y:
                raise OrientError(f"verify_unflip: line count differs at data line {n}")
            s = x.rstrip("\n").split("\t")
            chrom = s[0].strip().upper().removeprefix("CHR")
            rs = None
            for c, st, en, r in spans:
                if c == chrom and st <= int(s[1]) <= en:
                    rs = r
                    break
            if rs is None:
                if x != y:
                    raise OrientError(f"verify_unflip: data line {n} outside the windows changed")
                continue
            cat = catalog_keys_by_region[rs]
            k = _vkey(s)
            swap = (k[0], k[1], k[3], k[2])
            unusable = k[2] in _UNUSABLE or k[3] in _UNUSABLE
            swapped_only = (not unusable) and swap in cat and k not in cat
            kb[rs][k] += 1
            if swapped_only:
                if x.endswith("\n") != y.endswith("\n"):
                    raise OrientError(f"verify_unflip: data line {n} line ending changed")
                o = y.rstrip("\n").split("\t")
                if not _vflip_ok(s, o):
                    raise OrientError(f"verify_unflip: data line {n} ({rs}) is not the flip of its source line")
                if _vkey(o) not in cat or _vkey(o) != swap:
                    raise OrientError(f"verify_unflip: data line {n} ({rs}) flipped key not exact in the catalog")
                ka[rs][swap] += 1
                per[rs]["n_flipped"] += 1
                n_flip += 1
            else:
                if x != y:
                    raise OrientError(f"verify_unflip: data line {n} ({rs}) changed but is not swapped_only")
                ka[rs][k] += 1
            per[rs]["n_rows"] += 1
    for rs in per:
        new = [k for k, v in ka[rs].items() if v > 1 and v > kb[rs].get(k, 0)]
        if new:
            raise OrientError(f"verify_unflip: {len(new)} new duplicate allele keys in {rs}")
        per[rs]["dup_keys_before"] = _dups(kb[rs])
        per[rs]["dup_keys_after"] = _dups(ka[rs])
    return {"n_lines": n, "n_flipped": n_flip, "regions": {rs: dict(c) for rs, c in per.items()}}


def measure(files, windows, catalog_keys_by_region, tabix) -> list[dict]:
    """Per window x file (window-major, files in the given order): orient_by_fit.tsv columns + palindromic counts.
    files = [(trait, anc, path)]; rows read by tabix on the window."""
    out = []
    for rs, c, s, e in windows:
        cat = catalog_keys_by_region[rs]
        for t, a, p in files:
            txt = subprocess.run([tabix, str(p), f"{c}:{s}-{e}"], capture_output=True, text=True, check=True).stdout
            cnt = Counter()
            for line in txt.splitlines():
                f = line.split("\t")
                if len(f) != len(HEADER):
                    raise OrientError(f"{p}: {len(f)} fields in a tabix row")
                cls = row_class(f, cat)
                cnt["n_rows"] += 1
                cnt[cls] += 1
                if cls == "swapped_only" and is_palindromic(f[2], f[3]):
                    cnt["sp"] += 1
                    v = _numeric(f[_I["EAF"]])
                    if v is not None and 0.4 <= v <= 0.6:
                        cnt["spm"] += 1
            row = {"region": rs, "trait": t, "ancestry": a, "n_rows": cnt["n_rows"]}
            row.update({k: cnt[k] for k in CLASSES})
            row.update({"swapped_only_palindromic": cnt["sp"], "swapped_only_palindromic_eaf_0.4_0.6": cnt["spm"]})
            out.append(row)
    return out


# ---- CLI ----

def check_out_path(out, repo, sources=CATALOG_SOURCES):
    """Refuse any output whose repo-relative normalized path is not under data/r4/sumstats/, or is an input."""
    repo = os.path.abspath(str(repo))
    rel = os.path.normpath(os.path.relpath(os.path.abspath(os.path.join(repo, str(out))), repo))
    if not rel.startswith(OUT_DIR + os.sep):
        raise OrientError(f"output {out!r} ({rel}) is not under {OUT_DIR}/")
    if rel in {os.path.normpath(p) for _, _, p in sources} or rel.endswith(".tbi"):
        raise OrientError(f"output {out!r} is an input path")
    return rel


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _version(tool):
    r = subprocess.run([tool, "--version"], capture_output=True, text=True)
    return (r.stdout or r.stderr).splitlines()[0] if (r.stdout or r.stderr) else ""


def _verify_inputs(repo, src, wins):
    from ta_r4 import verify_inputs as vi

    cwd = os.getcwd()
    os.chdir(repo)
    try:
        vi.verify([src], [SUMSTATS_MANIFEST])
        vi.verify([paths.catalog_path("r4", w[0]) for w in wins], [CATALOGS_MANIFEST])
    except vi.InputIntegrityError as e:
        raise OrientError(f"input sha256: {e}") from None
    finally:
        os.chdir(cwd)


def cmd_harmonize(a):
    repo = Path(a.repo).resolve()
    rel = check_out_path(a.out or oriented_path(a.trait, a.anc), repo)
    src = source_path(a.trait, a.anc)
    wins = windows(repo)
    _verify_inputs(repo, src, wins)
    out = repo / rel
    tsv = out.with_name(out.name + ".tmp.tsv")
    try:
        rep = harmonize(repo / src, tsv, wins, catalog_keys_by_region(wins, repo))
        with open(out, "wb") as oh:
            subprocess.run([a.bgzip, "-c", str(tsv)], stdout=oh, check=True)
        subprocess.run([a.tabix, "-f", "-s", "1", "-b", "2", "-e", "2", "-S", "1", str(out)], check=True)
    finally:
        if tsv.exists():
            tsv.unlink()
    rep.update(trait=a.trait, ancestry=a.anc, src=src, out=rel, sha256_src=_sha256(repo / src),
               sha256_out=_sha256(out), sha256_out_tbi=_sha256(f"{out}.tbi"),
               bgzip=a.bgzip, bgzip_version=_version(a.bgzip), tabix=a.tabix, tabix_version=_version(a.tabix))
    with open(a.report, "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
        fh.write("\n")


def cmd_verify_unflip(a):
    repo = Path(a.repo).resolve()
    src = source_path(a.trait, a.anc)
    wins = windows(repo)
    _verify_inputs(repo, src, wins)
    rep = verify_unflip(repo / src, repo / oriented_path(a.trait, a.anc), wins, catalog_keys_by_region(wins, repo))
    rep.update(trait=a.trait, ancestry=a.anc, src=src, out=oriented_path(a.trait, a.anc))
    with open(a.report, "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
        fh.write("\n")


def cmd_measure(a):
    repo = Path(a.repo).resolve()
    files = [tuple(x.split(":", 2)) for x in a.files]
    wins = windows(repo)
    rows = measure([(t, an, repo / p) for t, an, p in files], wins, catalog_keys_by_region(wins, repo), a.tabix)
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def cmd_pin(a):
    repo = Path(a.repo).resolve()
    man = repo / a.manifest
    with open(man, newline="") as fh:
        have = {r["path"] for r in csv.DictReader(fh, delimiter="\t")}
    new = []
    for t, an, _ in CATALOG_SOURCES:
        for p in (oriented_path(t, an), oriented_path(t, an) + ".tbi"):
            if p in have:
                raise OrientError(f"{p} is already in {a.manifest}")
            new.append((p, _sha256(repo / p), os.path.getsize(repo / p), "output"))
    raw = open(man, "rb").read()
    if not raw.endswith(b"\n"):
        raise OrientError(f"{a.manifest} has no final newline")
    with open(man, "a", newline="") as fh:
        csv.writer(fh, delimiter="\t", lineterminator="\n").writerows(new)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("harmonize")
    for k in ("--trait", "--anc", "--bgzip", "--tabix", "--report"):
        h.add_argument(k, required=True)
    h.add_argument("--out", help="default oriented_path(T, A); must be under data/r4/sumstats/")
    v = sub.add_parser("verify-unflip")
    for k in ("--trait", "--anc", "--report"):
        v.add_argument(k, required=True)
    m = sub.add_parser("measure")
    m.add_argument("--files", nargs="+", required=True)
    m.add_argument("--tabix", required=True)
    m.add_argument("--out", required=True)
    p = sub.add_parser("pin")
    p.add_argument("--manifest", required=True)
    for s in (h, v, m, p):
        s.add_argument("--repo", default=".")
    a = ap.parse_args(argv)
    fn = {"harmonize": cmd_harmonize, "verify-unflip": cmd_verify_unflip, "measure": cmd_measure, "pin": cmd_pin}
    try:
        fn[a.cmd](a)
    except OrientError as e:
        print(f"OrientError: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
