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


# ---- 15.8f2 (Carter Q-158AEIW Hold): complement check of asthma EUR EAF against four EUR files and 1000G EUR. ----
AGREE_TOL = 0.1
COMPLEMENT_TOL = 0.1
DELTA_MIN = 0.2
SENSITIVITY_TOLS = (0.05, 0.10, 0.15)
EUR_REFERENCES = (("t2d", "EUR"), ("hypertension", "EUR"), ("bmi", "EUR"), ("stroke", "EUR"))
EAFC_SOURCES = ("asthma", "t2d", "hypertension", "bmi", "stroke", "1kg")
EAFC_PATTERNS = ("agree", "complement", "other", "unavailable")
EAFC_ONEKG_MATCHES = ("exact", "swapped", "ambiguous", "none", "no_af")
EAFC_GROUPS = ("flipped", "unflipped")
EAFC_CLASSES = ("SNV", "indel", "palindromic_SNV")
EAFC_VERDICTS = ("lt3_sources", "all_agree", "mixed") + tuple(f"{s}_outlier" for s in EAFC_SOURCES)
EAFC_VERDICTS_1KG = EAFC_VERDICTS + ("outlier_without_1kg",)
EAFC_ROWSETS = ("complement_t2d", "asthma_outlier", "t2d_outlier", "asthma_outlier_with_1kg", "t2d_outlier_with_1kg")
EAFC_FIT_TRAITS = ("asthma", "t2d")
RAW_HEADER = ["#CHR", "POS", "REF", "ALT", "rsid", "all_meta_AF", "inv_var_meta_beta", "inv_var_meta_sebeta",
              "inv_var_meta_p", "inv_var_het_p", "direction", "N_case", "N_ctrl", "n_dataset", "n_bbk", "is_strand_flip",
              "is_diff_AF_gnomAD"]
COMPLEMENT_COLUMNS = [
    "region_safe", "CHR", "POS", "SNP_ID", "REF", "ALT", "REF_oriented", "ALT_oriented", "group", "class", "EAF",
    "EAF_t2d", "EAF_hypertension", "EAF_bmi", "EAF_stroke", "EAF_1kg", "onekg_match", "onekg_nearby_indel", "class_t2d",
    "class_hypertension", "class_bmi", "class_stroke", "pattern_t2d", "pattern_hypertension", "pattern_bmi",
    "pattern_stroke", "pattern_1kg", "n_sources", "verdict", "verdict_with_1kg", "verdict_tol_0.05", "verdict_tol_0.15",
    "indel_kind", "anchored", "left_aligned_grch38", "in_repeat_grch38", "input_line", "strand", "CHR_GRCh38",
    "POS_GRCh38", "REF_GRCh38", "ALT_GRCh38", "EAF_GRCh38", "raw_match", "raw_all_meta_AF", "raw_is_strand_flip",
    "raw_is_diff_AF_gnomAD", "chain_eaf_kept", "region_lead_snp", "n_prod_fit_keys_asthma", "n_prod_fit_keys_t2d",
    "n_prod_variant_sets_asthma", "n_prod_variant_sets_t2d"]
CROSSTAB_COLUMNS = ["table", "group", "class", "stratum", "reference", "value", "n", "denominator"]


def eaf_pattern(e, r, agree_tol=AGREE_TOL, complement_tol=COMPLEMENT_TOL) -> str:
    """agree iff |e - r| <= agree_tol; complement iff |e + r - 1| <= complement_tol and |e - r| > DELTA_MIN; other
    otherwise; unavailable if either is None. agree is tested first."""
    if e is None or r is None:
        return "unavailable"
    if abs(e - r) <= agree_tol:
        return "agree"
    if abs(e + r - 1) <= complement_tol and abs(e - r) > DELTA_MIN:
        return "complement"
    return "other"


def verdict(eafs, agree_tol=AGREE_TOL, complement_tol=COMPLEMENT_TOL) -> str:
    """Symmetric over the sources with an EAF: lt3_sources / all_agree / <S>_outlier (S complement to every other
    source and every pair of the others agree) / mixed."""
    a = [s for s, x in eafs.items() if x is not None]
    if len(a) < 3:
        return "lt3_sources"

    def pat(s, t):
        return eaf_pattern(eafs[s], eafs[t], agree_tol, complement_tol)

    pairs = [(s, t) for i, s in enumerate(a) for t in a[i + 1:]]
    if all(pat(s, t) == "agree" for s, t in pairs):
        return "all_agree"
    out = [s for s in a
           if all(pat(s, t) == "complement" for t in a if t != s)
           and all(pat(x, y) == "agree" for x, y in pairs if s not in (x, y))]
    return f"{out[0]}_outlier" if len(out) == 1 else "mixed"


def verdict_with_1kg(eafs, agree_tol=AGREE_TOL, complement_tol=COMPLEMENT_TOL) -> str:
    """verdict(); an outlier verdict counts only if 1000G has an EAF and is not the outlier (it is then among the
    agreeing sources), else outlier_without_1kg."""
    v = verdict(eafs, agree_tol, complement_tol)
    if not v.endswith("_outlier"):
        return v
    s = v[: -len("_outlier")]
    return v if s != "1kg" and eafs.get("1kg") is not None else "outlier_without_1kg"


def onekg_eaf(ref, alt, records):
    """(onekg_match, EAF of alt) from the 1000G records at the row's POS: (POS, REF, ALT list, EUR_AF list).
    exact: VCF REF == ref and alt in ALT -> EUR_AF[i]; swapped: VCF REF == alt and ref in ALT -> 1 - sum(EUR_AF)
    (the frequency of the VCF REF); > 1 match -> ambiguous; none -> none; missing / '.' EUR_AF -> no_af.
    Symbolic ALTs (<...>) never match."""
    ref, alt = ref.strip().upper(), alt.strip().upper()
    hits = []
    for _pos, vref, alts, afs in records:
        vref = vref.upper()
        for i, x in enumerate(alts):
            x = x.upper()
            if x.startswith("<"):
                continue
            if vref == ref and x == alt:
                hits.append(("exact", i, alts, afs))
            elif vref == alt and x == ref:
                hits.append(("swapped", i, alts, afs))
    if not hits:
        return ("none", None)
    if len(hits) > 1:
        return ("ambiguous", None)
    kind, i, alts, afs = hits[0]
    if len(afs) != len(alts):
        return ("no_af", None)
    if kind == "exact":
        return ("no_af", None) if afs[i] in ("", ".") else ("exact", float(afs[i]))
    if any(x in ("", ".") for x in afs):
        return ("no_af", None)
    af = [float(x) for x in afs]
    return ("swapped", 1 - sum(af))


def _onekg_window(vcf_dir, tabix, chrom, start, end) -> dict:
    """{POS: [(POS, REF, ALT list, EUR_AF list), ...]} of the 1000G Phase 3 records in [start, end] (23 -> X)."""
    c = _bare(chrom)
    out = {}
    cmd = [tabix, os.path.join(vcf_dir, f"chr{c}.vcf.gz"), f"{c}:{start}-{end}"]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as p:
        for ln in p.stdout:
            f = ln.split("\t", 8)
            af = []
            for kv in f[7].split(";"):
                if kv.startswith("EUR_AF="):
                    af = kv[len("EUR_AF="):].split(",")
                    break
            pos = int(f[1])
            out.setdefault(pos, []).append((pos, f[3], f[4].split(","), af))
    if p.returncode:
        raise RuntimeError(f"tabix exit {p.returncode}: {cmd}")
    return out


def onekg_nearby_indel(ref, alt, pos, window_records) -> str:
    """true iff a non-symbolic 1000G record within [pos - 20, pos + len(ref) + 20] has |len(REF) - len(ALT[i])| equal
    to the row's."""
    d = abs(len(ref) - len(alt))
    for q in range(int(pos) - 20, int(pos) + len(ref) + 21):
        for _p, vref, alts, _af in window_records.get(q, ()):
            if any(not x.startswith("<") and abs(len(vref) - len(x)) == d for x in alts):
                return TRUE
    return FALSE


def indel_form(ref, alt) -> dict:
    """indel_kind (insertion / deletion / other), anchored (min length 1 and first bases equal), S = longer[1:]."""
    longer = alt if len(alt) > len(ref) else ref
    kind = "insertion" if len(alt) > len(ref) else "deletion" if len(alt) < len(ref) else "other"
    anchored = kind != "other" and min(len(ref), len(alt)) == 1 and ref[0].upper() == alt[0].upper()
    return {"indel_kind": kind, "anchored": TRUE if anchored else FALSE, "S": longer[1:].upper()}


def left_aligned(ref, alt, anchor_match) -> str:
    """Anchored and GRCh38 REF match only (else undetermined): true iff REF[0] != S[-1] (no left shift possible)."""
    f = indel_form(ref, alt)
    if f["anchored"] != TRUE or anchor_match != TRUE:
        return UND
    return TRUE if ref[0].upper() != f["S"][-1] else FALSE


def in_repeat(ref, alt, chrom38, pos38, fasta, samtools) -> str:
    """Anchored only (else undetermined): the len(S) GRCh38 bases right after the event equal S. insertion: bases
    [pos38 + 1, pos38 + len(S)]; deletion: [pos38 + len(REF), pos38 + len(REF) + len(S) - 1]."""
    f = indel_form(ref, alt)
    if f["anchored"] != TRUE:
        return UND
    s = f["S"]
    start = int(pos38) + 1 if f["indel_kind"] == "insertion" else int(pos38) + len(ref)
    b = grch38_bases(chrom38, start, len(s), fasta, samtools)
    if b is None:
        return UND
    return TRUE if b == s else FALSE


def _row_class3(ref, alt):
    if so.is_palindromic(ref, alt):
        return "palindromic_SNV"
    return "SNV" if len(ref) == 1 and len(alt) == 1 else "indel"


def all_rows(repo, tabix, vcf_dir) -> list[dict]:
    """Every asthma EUR oriented row of the r4 windows with row_class != absent and numeric EAF (palindromic rows
    kept), in _join order, with the EAF / class of each EUR reference at the same oriented key (last row wins on a
    duplicate key), 1000G EUR (exact allele key) and the patterns and verdicts."""
    win = so.windows(repo)
    cats = so.catalog_keys_by_region(win, repo)
    out = []
    for rs, c, s, e in win:
        refs = {}
        for t, a in EUR_REFERENCES:
            eaf, cnt, cls = {}, {}, {}
            r_src = _rows(repo, tabix, so.source_path(t, a), c, s, e)
            r_ori = _rows(repo, tabix, so.oriented_path(t, a), c, s, e)
            assert len(r_src) == len(r_ori), (t, rs)
            for fs_, fo_ in zip(r_src, r_ori):
                k = norm_key(*fo_[:4])
                eaf[k] = fo_[7]
                cnt[k] = cnt.get(k, 0) + 1
                cls[k] = so.row_class(fs_, cats[rs])
            refs[t] = (eaf, cnt, cls)
        g1k = _onekg_window(os.path.join(repo, vcf_dir), tabix, c, s, e)
        src_rows = _rows(repo, tabix, so.source_path("asthma", "EUR"), c, s, e)
        ori_rows = _rows(repo, tabix, so.oriented_path("asthma", "EUR"), c, s, e)
        assert len(src_rows) == len(ori_rows)
        for fs, fo in zip(src_rows, ori_rows):
            cl = so.row_class(fs, cats[rs])
            v = _num(fo[7])
            if cl == "absent" or v is None:
                continue
            k = norm_key(*fo[:4])
            row = {"region_safe": rs, "CHR": fs[0], "POS": fs[1], "SNP_ID": fs[9], "REF": fs[2], "ALT": fs[3],
                   "REF_oriented": fo[2], "ALT_oriented": fo[3],
                   "group": "flipped" if cl == "swapped_only" else "unflipped", "class": _row_class3(fs[2], fs[3]),
                   "EAF": fo[7], "_EAF_source": fs[7], "_key": k}
            eafs = {"asthma": v}
            dup = {}
            for t, _a in EUR_REFERENCES:
                raw = refs[t][0].get(k)
                row[f"EAF_{t}"] = "" if raw is None else raw
                row[f"class_{t}"] = refs[t][2].get(k, "")
                eafs[t] = None if raw is None else _num(raw)
                n = refs[t][1].get(k, 0)
                dup[t] = "absent" if n == 0 else "single" if n == 1 else "duplicated"
            m, e1 = onekg_eaf(fo[2], fo[3], g1k.get(int(fo[1]), []))
            eafs["1kg"] = e1
            row["EAF_1kg"] = e1
            row["onekg_match"] = m
            row["onekg_nearby_indel"] = (onekg_nearby_indel(fo[2], fo[3], int(fo[1]), g1k)
                                         if row["class"] == "indel" and m == "none" else "")
            for t in EAFC_SOURCES[1:]:
                row[f"pattern_{t}"] = eaf_pattern(v, eafs[t])
            row["n_sources"] = sum(x is not None for x in eafs.values())
            row["verdict"] = verdict(eafs)
            row["verdict_with_1kg"] = verdict_with_1kg(eafs)
            row["_ptol"] = {}
            for tol in SENSITIVITY_TOLS:
                row[f"verdict_tol_{tol:.2f}"] = verdict(eafs, tol, tol)
                row["_ptol"][tol] = {t: eaf_pattern(v, eafs[t], tol, tol) for t in EAFC_SOURCES[1:]}
            row["_eafs"] = eafs
            row["_dup"] = dup
            out.append(row)
    return out


def per_row_index(rows) -> list[int]:
    """Indices of the rows with |EAF - EAF_ref| > DELTA_MIN against at least one source."""
    return [i for i, r in enumerate(rows)
            if any(x is not None and abs(r["_eafs"]["asthma"] - x) > DELTA_MIN
                   for s, x in r["_eafs"].items() if s != "asthma")]


def input_fields(input_bgz, lines) -> dict:
    """{file line number (header = 1): fields} for the wanted lines of the harmonized input, one pass."""
    out = {}
    with gzip.open(input_bgz, "rt", newline="") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        assert hdr == so.HEADER, hdr
        for n, ln in enumerate(fh, start=2):
            if n in lines:
                out[n] = ln.rstrip("\n").split("\t")
    assert set(out) == set(lines), "input lines missing"
    return out


def raw_fields(raw_gz, positions) -> dict:
    """{(CHR, POS): [raw field lists]} of the GBMI raw rows at the wanted GRCh38 positions (CHR text as the
    harmonized input writes it; 23 = X), one streaming pass; header asserted."""
    out = {}
    with gzip.open(raw_gz, "rt", newline="") as fh:
        h = fh.readline().rstrip("\n").split("\t")
        if h != RAW_HEADER:
            raise RuntimeError(f"GBMI raw header {h}")
        for ln in fh:
            f = ln.rstrip("\n").split("\t")
            c = "23" if f[0] in ("X", "chrX") else f[0].removeprefix("chr")
            k = (c, int(f[1]))
            if k in positions:
                out.setdefault(k, []).append(f)
    return out


def indel_forms(rows, grch38, fasta, samtools) -> dict:
    """{row index: indel_kind, anchored, grch38_ref_match, left_aligned_grch38, in_repeat_grch38} for every indel,
    on the GRCh38 REF/ALT (equal to the lifted-source REF/ALT for indels; asserted)."""
    out = {}
    for i, r in enumerate(rows):
        if r["class"] != "indel":
            continue
        g = grch38[i]
        if g["strand"] != "+" or (g["REF_GRCh38"], g["ALT_GRCh38"]) != (r["REF"], r["ALT"]):
            raise RuntimeError(f"indel {r['CHR']}:{r['POS']}:{r['REF']}:{r['ALT']} not + strand with equal alleles")
        ref, alt = g["REF_GRCh38"], g["ALT_GRCh38"]
        m38 = ref_match(ref, grch38_bases(g["CHR_GRCh38"], int(g["POS_GRCh38"]), len(ref), fasta, samtools))
        f = indel_form(ref, alt)
        out[i] = {"indel_kind": f["indel_kind"], "anchored": f["anchored"], "grch38_ref_match": m38,
                  "left_aligned_grch38": left_aligned(ref, alt, m38),
                  "in_repeat_grch38": in_repeat(ref, alt, g["CHR_GRCh38"], int(g["POS_GRCh38"]), fasta, samtools)}
    return out


def rowsets(rows) -> dict:
    """{rowset: [row index]}: non-palindromic rows complementary to t2d, and the asthma / t2d outlier rows among them
    (verdict, and verdict_with_1kg)."""
    base = [i for i, r in enumerate(rows) if r["class"] != "palindromic_SNV" and r["pattern_t2d"] == "complement"]
    return {"complement_t2d": base,
            "asthma_outlier": [i for i in base if rows[i]["verdict"] == "asthma_outlier"],
            "t2d_outlier": [i for i in base if rows[i]["verdict"] == "t2d_outlier"],
            "asthma_outlier_with_1kg": [i for i in base if rows[i]["verdict_with_1kg"] == "asthma_outlier"],
            "t2d_outlier_with_1kg": [i for i in base if rows[i]["verdict_with_1kg"] == "t2d_outlier"]}


def complement_query_keys(rows) -> list[str]:
    """CHR:POS:REF:ALT of the lifted-source key and its swap of every complement_t2d row (pilot membership query)."""
    out = []
    for i in rowsets(rows)["complement_t2d"]:
        c, p, ref, alt = norm_key(rows[i]["CHR"], rows[i]["POS"], rows[i]["REF"], rows[i]["ALT"])
        out += [f"{c}:{p}:{ref}:{alt}", f"{c}:{p}:{alt}:{ref}"]
    return sorted(set(out))


def _kstr(k):
    return ":".join(str(x) for x in k)


def _read_tsv_dicts(path, skip_comment=False):
    with open(path, newline="") as fh:
        lines = fh.read().split("\n")
    assert lines[-1] == "", path
    lines = lines[:-1]
    if skip_comment:
        assert lines[0].startswith("#"), path
        lines = lines[1:]
    return list(csv.DictReader(lines, delimiter="\t"))


def exposure_data(repo, rows, panel_keys_tsv, members_tsv) -> dict:
    """Stored inputs and outputs only: production asthma / t2d EUR fit keys with their eligibility and variant sets
    (r4 catalog of the region and the arm's fit panel, by key or its swap), admissible pairs, arm paths, the pre-lock
    pilot fits and their names-only credible-set members (members_tsv), regions_r4.csv lead_snp."""
    from ta_r4 import arms as _arms
    from ta_r4 import measure_fit_eligibility as mfe
    from ta_r4 import paths as _paths

    man = os.path.join(repo, _paths.MAN)
    keys = [k for k in mfe.fit_keys(repo) if k[1] in EAFC_FIT_TRAITS and k[2] == "EUR"]
    elig = {(r["arm"], r["trait"], r["ancestry"], r["region_safe"]): r["eligible"]
            for r in _read_tsv_dicts(os.path.join(man, "w3f_fit_eligibility.tsv"))}
    pk_rows = _read_tsv_dicts(panel_keys_tsv)
    assert pk_rows and list(pk_rows[0]) == ["panel_path", "key"], panel_keys_tsv
    pk = {}
    for r in pk_rows:
        pk.setdefault(r["panel_path"], set()).add(r["key"])
    win = so.windows(repo)
    cats = so.catalog_keys_by_region(win, repo)
    panel_of = {}
    for k in keys:
        pp = _paths.panel_path(k[0], k[3], "EUR")
        if pp not in pk:
            raise RuntimeError(f"no variant list for the fit panel {pp} of {k}")
        panel_of[k] = pp
    in_vs = {k: set() for k in keys}
    n_keys, n_vs = [], []
    for i, r in enumerate(rows):
        kk = r["_key"]
        sw = (kk[0], kk[1], kk[3], kk[2])
        nk, nv = {}, {}
        for t in EAFC_FIT_TRAITS:
            cover = [k for k in keys if k[1] == t and k[3] == r["region_safe"]]
            nk[t] = len(cover)
            for k in cover:
                if kk in cats[k[3]] and (_kstr(kk) in pk[panel_of[k]] or _kstr(sw) in pk[panel_of[k]]):
                    in_vs[k].add(i)
            nv[t] = sum(1 for k in cover if i in in_vs[k])
        n_keys.append(nk)
        n_vs.append(nv)
    import yaml

    src = yaml.safe_load(open(os.path.join(repo, "config/ta_r4/data_sources.yaml")))["sources"]
    prov = []
    for t in EAFC_SOURCES[:-1]:
        oriented = so.oriented_path(t, "EUR")
        (s,) = [s for s in src.values() if isinstance(s, dict)
                and (s.get("r4_oriented") or {}).get("path") == oriented]
        lf = s.get("lifted_from")
        rawp = f"data/raw/region_analysis/sumstats/{t}.EUR.raw.gz"
        rawv = (f"{rawp} ({os.path.getsize(os.path.join(repo, rawp))} bytes)"
                if os.path.exists(os.path.join(repo, rawp)) else "absent")
        prov.append((f"{t}.EUR", s["name"], s["build"], "" if not lf else f"{lf['path']} ({lf['build']})", rawv))
    g1k = src["onekg_phase3_vcf"]
    prov.append(("1kg.EUR", g1k["name"], g1k["build"], "", "not applicable"))
    pairs = [r for r in mfe._manifest(repo) if r["ancestry"] == "EUR"
             and ({r["trait_a"], r["trait_b"]} & set(EAFC_FIT_TRAITS))]
    arm_paths = [(a, t, _paths.sumstats_path(t, "EUR", a)) for a in _arms.ARMS if "EUR" in _arms.arm_ancestries(a)
                 for t in EAFC_FIT_TRAITS]
    pilot_rows = _read_tsv_dicts(os.path.join(man, "prelock_pilot_fits.tsv"), skip_comment=True)
    fits = [(r["path"], r["trait"]) for r in pilot_rows
            if r["kind"] == "rds" and r["trait"] in EAFC_FIT_TRAITS and r["ancestry"] == "EUR"]
    mem_rows = _read_tsv_dicts(members_tsv)
    members = {}
    for r in mem_rows:
        assert list(r) == ["fit_path", "member_key"], members_tsv
        members.setdefault(r["fit_path"], set()).add(r["member_key"])
    assert set(members) <= {p for p, _ in fits}, "member rows for a fit not in prelock_pilot_fits.tsv"
    lead = {}
    with open(os.path.join(repo, _paths.regions_csv()), newline="") as fh:
        for r in csv.DictReader(fh):
            lead[so.safe_region_id(r["region_id"])] = r["lead_snp"]
    return {"keys": keys, "elig": {k: elig.get(k, "not_listed") for k in keys}, "panel_of": panel_of,
            "in_vs": in_vs, "n_keys": n_keys, "n_vs": n_vs, "pairs": pairs, "arm_paths": arm_paths, "fits": fits,
            "members": members, "lead": lead, "provenance": prov, "regions": [w[0] for w in win]}


def _is_member(row, member_keys):
    c, p, ref, alt = norm_key(row["CHR"], row["POS"], row["REF"], row["ALT"])
    return f"{c}:{p}:{ref}:{alt}" in member_keys or f"{c}:{p}:{alt}:{ref}" in member_keys


def complement_rows(rows, idx, grch38, inputs, raw, forms, exposure) -> list[dict]:
    """Per-row manifest rows (rows[i] for i in idx) with the source chain (GBMI raw -> harmonized GRCh38 -> lifted ->
    oriented), indel form and exposure. Raises on a chain row that breaks the lifted or oriented rule."""
    from decimal import Decimal, localcontext

    out = []
    for i in idx:
        r = rows[i]
        g = grch38[i]
        ref38, alt38 = g["REF_GRCh38"], g["ALT_GRCh38"]
        want = (ref38, alt38) if g["strand"] == "+" else (ref38.translate(_COMP), alt38.translate(_COMP))
        if want != (r["REF"], r["ALT"]):
            raise RuntimeError(f"lifted vs input alleles break the strand rule at row {i}")
        if r["group"] == "flipped":
            ok = (r["REF_oriented"], r["ALT_oriented"]) == (r["ALT"], r["REF"])
            with localcontext() as ctx:
                ctx.prec = 200
                ok = ok and Decimal(r["EAF"]) + Decimal(r["_EAF_source"]) == 1
        else:
            ok = (r["REF_oriented"], r["ALT_oriented"], r["EAF"]) == (r["REF"], r["ALT"], r["_EAF_source"])
        if not ok:
            raise RuntimeError(f"oriented vs lifted breaks the {r['group']} rule at row {i}")
        f_in = inputs[g["input_line"]]
        hits = raw.get((g["CHR_GRCh38"], int(g["POS_GRCh38"])), [])
        ex = [h for h in hits if (h[2], h[3]) == (ref38, alt38)]
        sw = [h for h in hits if (h[2], h[3]) == (alt38, ref38)]
        if len(ex) == 1 and not sw:
            rm, h = "exact", ex[0]
        elif len(sw) == 1 and not ex:
            rm, h = "swapped", sw[0]
        elif ex or sw:
            rm, h = "multiple", None
        else:
            rm, h = "absent", None
        kept = UND if rm != "exact" else (TRUE if float(h[5]) == float(f_in[7]) else FALSE)
        fm = forms.get(i, {})
        lead = exposure["lead"].get(r["region_safe"], "")
        row = {c: r.get(c, "") for c in COMPLEMENT_COLUMNS}
        row.update({
            "EAF_1kg": "" if r["EAF_1kg"] is None else repr(r["EAF_1kg"]), "n_sources": str(r["n_sources"]),
            "indel_kind": fm.get("indel_kind", ""), "anchored": fm.get("anchored", ""),
            "left_aligned_grch38": fm.get("left_aligned_grch38", ""), "in_repeat_grch38": fm.get("in_repeat_grch38", ""),
            "input_line": str(g["input_line"]), "strand": g["strand"], "CHR_GRCh38": g["CHR_GRCh38"],
            "POS_GRCh38": g["POS_GRCh38"], "REF_GRCh38": ref38, "ALT_GRCh38": alt38, "EAF_GRCh38": f_in[7],
            "raw_match": rm, "raw_all_meta_AF": "" if h is None else h[5],
            "raw_is_strand_flip": "" if h is None else h[15], "raw_is_diff_AF_gnomAD": "" if h is None else h[16],
            "chain_eaf_kept": kept,
            "region_lead_snp": "no_snp_id" if r["SNP_ID"] in ("", "NA") else (TRUE if r["SNP_ID"] == lead else FALSE),
            "n_prod_fit_keys_asthma": str(exposure["n_keys"][i]["asthma"]),
            "n_prod_fit_keys_t2d": str(exposure["n_keys"][i]["t2d"]),
            "n_prod_variant_sets_asthma": str(exposure["n_vs"][i]["asthma"]),
            "n_prod_variant_sets_t2d": str(exposure["n_vs"][i]["t2d"])})
        out.append(row)
    return out


def render_complement_manifest(rows) -> str:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(COMPLEMENT_COLUMNS)
    for r in rows:
        w.writerow([r[c] for c in COMPLEMENT_COLUMNS])
    return buf.getvalue()


def render_complement_crosstab(rows, per_row, exposure) -> str:
    """Counts with denominators over ALL joined rows (chain over the per-row rows); within each (table, group,
    class, stratum, reference) block the values sum to the denominator, except the exposure tables."""
    out = []

    def block(table, group, cls, stratum, reference, values, items):
        items = list(items)
        n = len(items)
        cnt = {}
        for x in items:
            cnt[x] = cnt.get(x, 0) + 1
        extra = sorted(set(cnt) - set(values))
        for v in list(values) + extra:
            out.append([table, group, cls, stratum, reference, v, cnt.get(v, 0), n])
        assert sum(cnt.values()) == n

    def sel(g, c):
        return [r for r in rows if r["group"] == g and r["class"] == c]

    for g in EAFC_GROUPS:
        for c in EAFC_CLASSES:
            rs_ = sel(g, c)
            for ref in EAFC_SOURCES[1:]:
                block("pattern", g, c, "all", ref, EAFC_PATTERNS, (r[f"pattern_{ref}"] for r in rs_))
            for st in (">0.2", "<=0.2"):
                sub = [r for r in rs_ if r["_eafs"]["t2d"] is not None
                       and ((abs(r["_eafs"]["asthma"] - r["_eafs"]["t2d"]) > 0.2) == (st == ">0.2"))]
                for ref in EAFC_SOURCES[1:]:
                    block("pattern", g, c, st, ref, EAFC_PATTERNS, (r[f"pattern_{ref}"] for r in sub))
            for tol in (0.05, 0.15):
                for ref in EAFC_SOURCES[1:]:
                    block(f"pattern_tol_{tol:.2f}", g, c, "all", ref, EAFC_PATTERNS, (r["_ptol"][tol][ref] for r in rs_))
            comp = [r for r in rs_ if r["pattern_t2d"] == "complement"]
            for st, sub in (("all", rs_), ("complement_t2d", comp)):
                block("verdict", g, c, st, "all", EAFC_VERDICTS, (r["verdict"] for r in sub))
                block("verdict_with_1kg", g, c, st, "all", EAFC_VERDICTS_1KG, (r["verdict_with_1kg"] for r in sub))
                block("n_sources", g, c, st, "all", [str(k) for k in range(1, 7)], (str(r["n_sources"]) for r in sub))
            for tol in (0.05, 0.15):
                ctol = [r for r in rs_ if r["_ptol"][tol]["t2d"] == "complement"]
                for st, sub in (("all", rs_), ("complement_t2d", ctol)):
                    block(f"verdict_tol_{tol:.2f}", g, c, st, "all", EAFC_VERDICTS,
                          (r[f"verdict_tol_{tol:.2f}"] for r in sub))
            block("onekg_match", g, c, "all", "1kg", EAFC_ONEKG_MATCHES, (r["onekg_match"] for r in rs_))
            block("per_row_selection", g, c, "all", "any_source", ("selected", "not_selected"),
                  ("selected" if max(abs(r["_eafs"]["asthma"] - x) for x in r["_eafs"].values() if x is not None)
                   > DELTA_MIN else "not_selected" for r in rs_))
            for ref, _a in EUR_REFERENCES:
                block("duplicate_reference_key", g, c, "all", ref, ("single", "duplicated", "absent"),
                      (r["_dup"][ref] for r in rs_))
    # reference provenance (data_sources.yaml; raw file presence under data/raw/region_analysis/sumstats)
    for t, name, build, lifted, rawf in exposure.get("provenance", ()):
        for field, val in (("name", name), ("build", build), ("lifted_from", lifted), ("raw_file", rawf)):
            out.append(["reference_provenance", "all", "all", field, t, val, 1, 1])
    # indel form, every indel of the join
    for g in EAFC_GROUPS:
        ind = [r for r in rows if r["group"] == g and r["class"] == "indel"]
        strata = {}
        for r in ind:
            s = (f"{r['indel_kind']}|anchored={r['anchored']}|left_aligned={r['left_aligned_grch38']}|"
                 f"in_repeat={r['in_repeat_grch38']}")
            strata.setdefault(s, []).append(r)
        for s in sorted(strata):
            for ref in ("t2d", "1kg"):
                block("indel_form", g, "indel", s, ref, EAFC_PATTERNS, (r[f"pattern_{ref}"] for r in strata[s]))
    # source chain, per-row rows, stratum = verdict
    for g in EAFC_GROUPS:
        for c in EAFC_CLASSES:
            pr = [r for r in per_row if r["group"] == g and r["class"] == c]
            for v in sorted({r["verdict"] for r in pr}):
                sub = [r for r in pr if r["verdict"] == v]
                block("chain", g, c, v, "raw_match", ("exact", "swapped", "multiple", "absent"),
                      (r["raw_match"] for r in sub))
                block("chain", g, c, v, "chain_eaf_kept", (TRUE, FALSE, UND), (r["chain_eaf_kept"] for r in sub))
                block("chain", g, c, v, "raw_is_diff_AF_gnomAD", ("yes", "no", ""),
                      (r["raw_is_diff_AF_gnomAD"] for r in sub))
                block("chain", g, c, v, "raw_is_strand_flip", ("yes", "no", ""), (r["raw_is_strand_flip"] for r in sub))
    # exposure (counts with their own stated denominators)
    sets = rowsets(rows)
    for rset in EAFC_ROWSETS:
        idx = sets[rset]
        for rg in exposure["regions"]:
            out.append(["exposure_region", "all", "all", rg, rset, "rows",
                        sum(1 for i in idx if rows[i]["region_safe"] == rg), len(idx)])
        for k in exposure["keys"]:
            arm, t, _a, rg = k
            inw = [i for i in idx if rows[i]["region_safe"] == rg]
            inv = [i for i in inw if i in exposure["in_vs"][k]]
            st = f"{arm}|{t}|{rg}"
            out.append(["exposure_fit_key", "in_window", "all", st, rset, exposure["elig"][k], len(inw), len(idx)])
            out.append(["exposure_fit_key", "in_variant_set", "all", st, rset, exposure["elig"][k], len(inv), len(idx)])
        for p in exposure["pairs"]:
            out.append(["exposure_pair", "all", "all", p["row_id"], rset, f"{p['trait_a']}_vs_{p['trait_b']}",
                        sum(1 for i in idx if rows[i]["region_safe"] == p["region_safe"]), len(idx)])
        for t in EAFC_FIT_TRAITS:
            tf = [fp for fp, ft in exposure["fits"] if ft == t]
            for fp in tf:
                mk = exposure["members"].get(fp, set())
                out.append(["exposure_pilot", t, "all", fp, rset, "member",
                            sum(1 for i in idx if _is_member(rows[i], mk)), len(idx)])
            anyf = set().union(*(exposure["members"].get(fp, set()) for fp in tf)) if tf else set()
            out.append(["exposure_pilot", t, "all", "any_fit", rset, "member",
                        sum(1 for i in idx if _is_member(rows[i], anyf)), len(idx)])
            out.append(["exposure_pilot", t, "all", "fits", rset, "fits_with_a_member",
                        sum(1 for fp in tf if any(_is_member(rows[i], exposure["members"].get(fp, set()))
                                                  for i in idx)), len(tf)])
    for arm, t, pth in exposure["arm_paths"]:
        out.append(["exposure_arm_path", "all", "all", arm, t, pth, 1, 1])
    buf = io.StringIO(newline="")
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(CROSSTAB_COLUMNS)
    for r in out:
        assert int(r[6]) <= int(r[7]), r
        w.writerow(r)
    return buf.getvalue()


def complement_manifests(repo, tabix, vcf_dir, fasta, samtools, input_bgz, lifted_bed, raw_gz, panel_keys_tsv,
                         members_tsv):
    """(all_rows, per_row manifest rows, exposure): all_rows -> grch38_rows for every indel and per-row row (one
    lifted.bed pass) -> input_fields -> raw_fields -> indel forms, chain, exposure."""
    rows = all_rows(repo, tabix, vcf_dir)
    idx = per_row_index(rows)
    need = sorted(set(idx) | {i for i, r in enumerate(rows) if r["class"] == "indel"})
    g = grch38_rows([rows[i] for i in need], input_bgz, lifted_bed)
    grch38 = dict(zip(need, g))
    forms = indel_forms(rows, grch38, fasta, samtools)
    for i, f in forms.items():
        rows[i].update(f)
    inputs = input_fields(input_bgz, {grch38[i]["input_line"] for i in idx})
    raw = raw_fields(raw_gz, {(grch38[i]["CHR_GRCh38"], int(grch38[i]["POS_GRCh38"])) for i in idx})
    exposure = exposure_data(repo, rows, panel_keys_tsv, members_tsv)
    per_row = complement_rows(rows, idx, grch38, inputs, raw, forms, exposure)
    return rows, per_row, exposure
