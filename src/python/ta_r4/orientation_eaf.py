"""Diagnostic only (W3f 15.8f; Carter Q-158AEI, Q-158AEIM): the 15.8a2 EAF join of the oriented r4 sumstats, per-row
detail of asthma EUR's flipped rows and an unflipped control sample, and their REF read against GRCh38 and the 1000
Genomes Phase 3 GRCh37 records. Returns data; it writes nothing, filters nothing and is not read by the analysis path.
Tool and reference paths are arguments; repo paths are repo-relative under ``repo``.

Tri-state values are "true" / "false" / "undetermined" (Kleene logic for k_and / k_not).
"""
from __future__ import annotations

import csv
import gzip
import io
import os
import random
import statistics
import subprocess

from ta_r4 import sumstats_orient as so
from ta_r4.collector_drop_audit import norm_key

# reference file of each (trait, ancestry) for the EAF join (15.8a2 identities.py)
REF = {"EUR": ("t2d", "EUR"), ("t2d", "AFR"): ("asthma", "AFR"), ("stroke", "AFR"): ("asthma", "AFR"),
       ("asthma", "AFR"): ("t2d", "AFR")}
EAF_COMMENT = ("# diagnostic, not a filter: |EAF - reference EAF| on the oriented files, non-palindromic rows with "
               "numeric EAF in both, joined on the oriented CHR:POS:REF:ALT key within the 31 r4 windows (15.8a2)\n")
EAF_HEADER = ["trait", "ancestry", "class", "reference_file", "n", "median_abs_delta_eaf", "n_above_0.2"]
TRUE, FALSE, UND = "true", "false", "undetermined"
_COMP = str.maketrans("ACGTacgt", "TGCAtgca")


def _num(x):
    try:
        v = float(x)
        return v if v == v else None
    except ValueError:
        return None


def _rows(repo, tabix, path, c, s, e):
    txt = subprocess.run([tabix, os.path.join(repo, path), f"{c}:{s}-{e}"], capture_output=True, text=True,
                         check=True).stdout
    return [ln.split("\t") for ln in txt.splitlines()]


def _ref_of(t, a):
    ref = REF.get((t, a), REF[a] if a == "EUR" else None)
    return None if ref == (t, a) else ref


def _join(repo, tabix, only=None):
    """Yield (trait, anc, cls, reference_file, region_safe, source_fields, oriented_fields, eaf, eaf_ref_raw, delta)
    for every row the 15.8a2 EAF diagnostic counts, in its order."""
    win = so.windows(repo)
    cats = so.catalog_keys_by_region(win, repo)
    for t, a, p in so.CATALOG_SOURCES:
        ref = _ref_of(t, a)
        if ref is None or (only is not None and (t, a) != only):
            continue
        ref_file = so.oriented_path(*ref)
        for rs, c, s, e in win:
            refrows = {norm_key(*f[:4]): f[7] for f in _rows(repo, tabix, ref_file, c, s, e)}
            src_rows = _rows(repo, tabix, p, c, s, e)
            ori_rows = _rows(repo, tabix, so.oriented_path(t, a), c, s, e)
            assert len(src_rows) == len(ori_rows)
            for fs, fo in zip(src_rows, ori_rows):
                cls = so.row_class(fs, cats[rs])
                if cls == "absent" or so.is_palindromic(fs[2], fs[3]):
                    continue
                raw = refrows.get(norm_key(*fo[:4]))
                v, rv = _num(fo[7]), (None if raw is None else _num(raw))
                if v is None or rv is None:
                    continue
                yield (t, a, "flipped" if cls == "swapped_only" else "unflipped", ref_file, rs, fs, fo, v, raw,
                       abs(v - rv))


def eaf_diffs(repo: str, tabix: str) -> dict:
    """{(trait, anc, cls, reference_file): [abs_delta, ...]} as 15.8a2 identities.py."""
    diffs = {}
    for t, a, cls, ref_file, *_rest, d in _join(repo, tabix):
        diffs.setdefault((t, a, cls, ref_file), []).append(d)
    return diffs


def render_eaf_manifest(diffs: dict) -> str:
    """Exact text of manifests/sumstats_r4_orientation_eaf.tsv."""
    buf = io.StringIO(newline="")
    buf.write(EAF_COMMENT)
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(EAF_HEADER)
    for t, a, _ in so.CATALOG_SOURCES:
        for cls in ("flipped", "unflipped"):
            for k, v in diffs.items():
                if k[:3] == (t, a, cls):
                    w.writerow([t, a, cls, k[3], len(v), f"{statistics.median(v):.4f}", sum(x > 0.2 for x in v)])
    return buf.getvalue()


def eaf_rows(repo, tabix, trait, anc, cls) -> list[dict]:
    """The rows eaf_diffs counts for (trait, anc, cls), same order, with their fields."""
    out = []
    for t, a, c, _ref, rs, fs, fo, _v, raw, d in _join(repo, tabix, only=(trait, anc)):
        if c != cls:
            continue
        out.append({"region_safe": rs, "CHR": fs[0], "POS": fs[1], "SNP_ID": fs[9], "REF": fs[2], "ALT": fs[3],
                    "REF_oriented": fo[2], "ALT_oriented": fo[3],
                    "class": "SNV" if len(fs[2]) == 1 and len(fs[3]) == 1 else "indel",
                    "EAF": fo[7], "EAF_reference": raw, "abs_delta_eaf": d})
    return out


def flipped_rows(repo, tabix, trait="asthma", anc="EUR") -> list[dict]:
    return eaf_rows(repo, tabix, trait, anc, "flipped")


def _stratum(r):
    return f"{r['class']}{'>0.2' if r['abs_delta_eaf'] > 0.2 else '<=0.2'}"


def control_sample(rows, seed=20261127, n_per_stratum=2000) -> list[dict]:
    """Strata class x (abs_delta_eaf > 0.2): every row of a > 0.2 stratum; from each <= 0.2 stratum
    random.Random(seed).sample(rows sorted by (CHR, POS, REF, ALT, SNP_ID), min(n, N)). Output in input order; each
    row carries stratum and stratum_n (population size)."""
    by = {}
    for i, r in enumerate(rows):
        by.setdefault(_stratum(r), []).append(i)
    keep = set()
    for s, idx in by.items():
        if s.endswith(">0.2"):
            keep.update(idx)
            continue
        idx = sorted(idx, key=lambda i: (int(rows[i]["CHR"]), int(rows[i]["POS"]), rows[i]["REF"], rows[i]["ALT"],
                                         rows[i]["SNP_ID"], i))
        keep.update(random.Random(seed).sample(idx, min(n_per_stratum, len(idx))))
    return [dict(rows[i], stratum=_stratum(rows[i]), stratum_n=len(by[_stratum(rows[i])])) for i in sorted(keep)]


def _ucsc(chrom):
    c = str(chrom)
    return "chrX" if c == "23" else (c if c.startswith("chr") else f"chr{c}")


def grch38_rows(rows, input_bgz: str, lifted_bed: str) -> list[dict]:
    """Per row: input_line, strand, CHR_GRCh38, POS_GRCh38, REF_GRCh38, ALT_GRCh38, found through the lift's own
    record (lifted.bed: name = input line, end = lifted POS, strand col 6). Raises unless exactly one candidate."""
    want = {(_ucsc(r["CHR"]), int(r["POS"])) for r in rows}
    cand = {}
    with open(lifted_bed) as fh:
        for ln in fh:
            f = ln.rstrip("\n").split("\t")
            k = (f[0], int(f[2]))
            if k in want:
                cand.setdefault(k, []).append((int(f[3]), f[5]))
    lines = {n for v in cand.values() for n, _ in v}
    src = {}
    with gzip.open(input_bgz, "rt", newline="") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        assert hdr == so.HEADER, hdr
        for n, ln in enumerate(fh, start=2):
            if n in lines:
                src[n] = ln.rstrip("\n").split("\t")
    assert set(src) == lines, "lifted.bed names input lines that are not in the input"
    out = []
    for r in rows:
        hits = []
        for n, strand in cand.get((_ucsc(r["CHR"]), int(r["POS"])), []):
            f = src[n]
            if f[9] != r["SNP_ID"]:
                continue
            ref, alt = (f[2], f[3]) if strand == "+" else (f[2].translate(_COMP), f[3].translate(_COMP))
            if (ref, alt) == (r["REF"], r["ALT"]):
                hits.append((n, strand, f))
        if len(hits) != 1:
            raise RuntimeError(f"{len(hits)} GRCh38 input rows for lifted row {r['CHR']}:{r['POS']}:{r['REF']}:"
                               f"{r['ALT']} {r['SNP_ID']}")
        n, strand, f = hits[0]
        out.append(dict(r, input_line=n, strand=strand, CHR_GRCh38=f[0], POS_GRCh38=f[1], REF_GRCh38=f[2],
                        ALT_GRCh38=f[3]))
    return out


def _bare(chrom):
    c = str(chrom)
    c = c[3:] if c.startswith("chr") else c
    return "X" if c == "23" else c


def grch38_bases(chrom, pos, length, fasta: str, samtools: str) -> str | None:
    """Uppercased GRCh38 bases at [pos, pos+length-1]; None (undetermined) if the contig is absent, the span passes
    the contig end, or a base is N."""
    c = _bare(chrom)
    lens = {}
    with open(f"{fasta}.fai") as fh:
        for ln in fh:
            f = ln.split("\t")
            lens[f[0]] = int(f[1])
    end = int(pos) + int(length) - 1
    if c not in lens or int(pos) < 1 or end > lens[c]:
        return None
    txt = subprocess.run([samtools, "faidx", fasta, f"{c}:{pos}-{end}"], capture_output=True, text=True,
                         check=True).stdout
    seq = "".join(txt.splitlines()[1:]).upper()
    if len(seq) != int(length) or "N" in seq:
        return None
    return seq


def bases_from_records(pos: int, length: int, records: list[tuple[int, str]]) -> str:
    """The bases at [pos, pos+length-1] from (record POS, REF) pairs: only the REF bases that fall inside the span;
    '.' where no record covers. Records covering one position must agree (else ValueError)."""
    out = ["."] * length
    for rpos, ref in records:
        for i, base in enumerate(ref):
            j = rpos + i - pos
            if 0 <= j < length:
                base = base.upper()
                if out[j] == ".":
                    out[j] = base
                elif out[j] != base:
                    raise ValueError(f"records disagree at {pos + j}: {out[j]} vs {base}")
    return "".join(out)


def grch37_bases(chrom, pos, length, vcf_dir: str, tabix: str) -> str:
    """bases_from_records over the 1000G Phase 3 records tabix returns for the span (CHR 23 -> chrX.vcf.gz, contig X)."""
    c = _bare(chrom)
    end = int(pos) + int(length) - 1
    txt = subprocess.run([tabix, os.path.join(vcf_dir, f"chr{c}.vcf.gz"), f"{c}:{pos}-{end}"], capture_output=True,
                         text=True, check=True).stdout
    recs = []
    for ln in txt.splitlines():
        f = ln.split("\t", 5)
        recs.append((int(f[1]), f[3]))
    return bases_from_records(int(pos), int(length), recs)


def ref_match(ref: str, bases: str | None) -> str:
    """true if every base is covered and equal to ref; false if any covered base differs; else undetermined."""
    if bases is None:
        return UND
    ref = ref.upper()
    if len(ref) != len(bases):
        raise ValueError(f"length {len(ref)} vs {len(bases)}")
    if any(b != "." and b != r for r, b in zip(ref, bases)):
        return FALSE
    return UND if "." in bases else TRUE


def k_and(a: str, b: str) -> str:
    for x in (a, b):
        if x not in (TRUE, FALSE, UND):
            raise ValueError(x)
    if FALSE in (a, b):
        return FALSE
    return TRUE if a == b == TRUE else UND


def k_not(a: str) -> str:
    return {TRUE: FALSE, FALSE: TRUE, UND: UND}[a]
