"""Measure a harmonized sumstats file's genome build from its positions (never from its BUILD column).

Anchors are SNVs with native GRCh37 (1000G Phase 3 VCF) and native GRCh38 (GBMI release) positions.
An anchor is hit in a build when the file has a row at that build's chr:pos whose {REF, ALT} equals the
anchor's alleles (any row at that position when the file has no allele columns).
"""
from __future__ import annotations

import csv
import gzip
import os
import subprocess
import tempfile
from pathlib import Path

ANCHORS = Path(__file__).resolve().parents[3] / "tests/ta_r4/fixtures/build_anchors_grch37_grch38.tsv"
BUILDS = ("GRCh37", "GRCh38")
POS_COL = {"GRCh37": "pos_grch37", "GRCh38": "pos_grch38"}


def load_anchors(path=ANCHORS):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _header(path):
    with gzip.open(path, "rt") as fh:
        return fh.readline().rstrip("\n").split("\t")


def build_hits(path, tabix, anchors=None):
    """{build: number of anchors hit at that build's position}."""
    anchors = load_anchors() if anchors is None else anchors
    hdr = _header(path)
    ci, pi = hdr.index("CHR"), hdr.index("POS")
    al = (hdr.index("REF"), hdr.index("ALT")) if {"REF", "ALT"} <= set(hdr) else None
    out = {}
    for build in BUILDS:
        want = {(a["chr"], a[POS_COL[build]]): {a["ref_1kg"].upper(), a["alt_1kg"].upper()} for a in anchors}
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as fh:
            for c, p in sorted(want):
                fh.write(f"{c}\t{p}\t{p}\n")
            reg = fh.name
        try:
            p = subprocess.run([tabix, "-R", reg, str(path)], capture_output=True, text=True)
        finally:
            os.unlink(reg)
        if p.returncode != 0:
            raise RuntimeError(f"tabix failed on {path}: {p.stderr.strip()}")
        hit = set()
        for line in p.stdout.splitlines():
            f = line.split("\t")
            k = (f[ci], f[pi])
            if k in want and (al is None or {f[al[0]].upper(), f[al[1]].upper()} == want[k]):
                hit.add(k)
        out[build] = len(hit)
    return out


def infer_build(hits, min_hits=50, max_other_frac=0.05):
    """GRCh37 / GRCh38 when one build has >= min_hits and the other <= max_other_frac of the total."""
    tot = sum(hits.values())
    for b in BUILDS:
        other = tot - hits[b]
        if hits[b] >= min_hits and other <= max_other_frac * tot:
            return b
    return "indeterminate"
