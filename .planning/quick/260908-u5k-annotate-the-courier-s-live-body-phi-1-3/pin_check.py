#!/usr/bin/env python3
"""Do the LIVE-state pins actually describe the file on disk? (normalized, case-insensitive)"""
import hashlib, pathlib, re, sys

EMPH = re.compile(r"[*_`>#]"); WS = re.compile(r"\s+")
norm = lambda s: WS.sub(" ", EMPH.sub("", s)).strip().lower()

C = pathlib.Path(".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md")
raw = C.read_bytes()
md5 = sys.argv[1] if len(sys.argv) > 1 else hashlib.md5(raw).hexdigest()   # arg = negative control
lines = raw.count(b"\n")
print(f"on disk: {lines} lines, md5 {md5}")

ok = True
for p in [".planning/STATE.md", ".planning/HANDOFF.json"]:
    t = norm(pathlib.Path(p).read_text())
    has_new = md5 in t and f"{lines} lines" in t
    stale_as_current = "613 lines, md5 ce6791344916c6ebebacfadbb808c702" in t and md5 not in t
    print(f"  [{'PASS' if has_new else 'FAIL'}] {p}: carries current md5 + line count")
    print(f"  [{'PASS' if not stale_as_current else 'FAIL'}] {p}: stale pin not left as the only value")
    ok &= has_new and not stale_as_current
print("PIN CHECK:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
