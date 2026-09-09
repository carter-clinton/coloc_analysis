#!/usr/bin/env python3
"""u5k guard: splice byte-equality + normalized case-insensitive phrase checks.

Every phrase check normalizes (strips markdown emphasis, collapses whitespace)
and lowercases before matching. A literal case-sensitive grep has been blind to
live text in these files five separate times.
"""
import hashlib
import re
import subprocess
import sys

COURIER = ".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md"
SRC = ".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md"
BEGIN = b"<!-- BEGIN VERBATIM APPENDIX"
END = b"<!-- END VERBATIM APPENDIX -->"

EMPH = re.compile(r"[*_`>#]")
WS = re.compile(r"\s+")


def norm(s):
    """Strip markdown emphasis, collapse whitespace, lowercase."""
    return WS.sub(" ", EMPH.sub("", s)).strip().lower()


def split_courier(path):
    """-> (live_body_bytes, appendix_content_bytes, n_begin, n_end)"""
    raw = open(path, "rb").read()
    n_begin = raw.count(BEGIN)
    n_end = raw.count(END)
    if n_begin != 1 or n_end != 1:
        return None, None, n_begin, n_end
    b0 = raw.index(BEGIN)
    b_eol = raw.index(b"\n", b0) + 1
    e0 = raw.index(END)
    live = raw[:b0]
    appendix = raw[b_eol:e0]
    return live, appendix, n_begin, n_end


def splice_source(path):
    raw = open(path, "rb").read()
    i = raw.index(b"\n## ARTIFACTS")
    return raw[i + 1:]


def run(courier=COURIER, src=SRC, label="", expect_all_green=True):
    results = []
    live, appendix, nb, ne = split_courier(courier)
    results.append(("markers: exactly 1 BEGIN + 1 END", nb == 1 and ne == 1, f"{nb}/{ne}"))
    if live is None:
        return results

    slice_src = splice_source(src)
    eq = appendix == slice_src
    results.append(("appendix bytes == splice source '## ARTIFACTS'->EOF", eq,
                    f"appendix {len(appendix)}B md5 {hashlib.md5(appendix).hexdigest()} | "
                    f"source {len(slice_src)}B md5 {hashlib.md5(slice_src).hexdigest()}"))

    nlive, napp = norm(live.decode()), norm(appendix.decode())

    # the original sentence: unedited, present in BOTH body and appendix
    sent = norm("The dispersion is robust in DIRECTION (every correction gives phi > 1.3) but "
                "POORLY DETERMINED in magnitude, and its significance is not robust to the "
                "choice of overlap correction.")
    results.append(("original sentence intact in LIVE BODY", nlive.count(sent) == 1, f"n={nlive.count(sent)}"))
    results.append(("original sentence intact in APPENDIX", napp.count(sent) == 1, f"n={napp.count(sent)}"))

    # the annotation: present in the live body, ABSENT from the appendix

    # pinned appendix identity (recorded PRE-edit, must be unmoved)
    import hashlib as _h
    results.append(("appendix md5 unmoved (e4cb9478..., 14119 B)",
                    _h.md5(appendix).hexdigest() == "e4cb947823dd758ec2bd32667b788391" and len(appendix) == 14119,
                    f"{_h.md5(appendix).hexdigest()} / {len(appendix)}B"))

    # phrases UNIQUE to the annotation -> must appear in the live body, never in the appendix
    for phrase in ["SCOPE-LIMITED 2026-09-08",
                   "2.36 / 1.97 / 1.99 / 1.52",
                   "1.931 / 1.652 / 1.564 / 1.249",
                   "ICC 0.729, c_eff 1.494",
                   "falls BELOW 1.3",
                   "See the 2026-09-08 entry in .planning/osf_deviations.md",
                   "Finding 2 is NOT ESTABLISHED"]:
        p_ = norm(phrase)
        results.append((f"LIVE BODY has (x1): {phrase!r}", nlive.count(p_) == 1, f"n={nlive.count(p_)}"))
        results.append((f"APPENDIX lacks:     {phrase!r}", napp.count(p_) == 0, f"n={napp.count(p_)}"))

    # the osf path pre-existed ONCE in each half; after the edit the body must carry exactly 2
    op = norm(".planning/osf_deviations.md")
    results.append(("LIVE BODY osf-path count == 2 (1 pre-existing + 1 new)", nlive.count(op) == 2, f"n={nlive.count(op)}"))
    results.append(("APPENDIX osf-path count == 1 (pre-existing, untouched)", napp.count(op) == 1, f"n={napp.count(op)}"))

    return results


def report(results, label):
    ok = all(r[1] for r in results)
    print(f"===== {label}: {'GREEN' if ok else 'RED'} =====")
    for name, passed, detail in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}  ({detail})")
    return ok


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else COURIER
    s = sys.argv[2] if len(sys.argv) > 2 else SRC
    lab = sys.argv[3] if len(sys.argv) > 3 else "guard"
    sys.exit(0 if report(run(c, s), lab) else 1)
