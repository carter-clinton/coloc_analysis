#!/usr/bin/env python3
"""Guard for 260908-uer — the Rao-Scott ESTIMATOR correction.

Every assertion here is designed to be runnable BEFORE the edit (where it must go
RED) and AFTER (where it must go GREEN). That pre-edit RED run IS the negative
control: a check that cannot fail on the real file is not evidence.

Usage:
    python3 guard.py [--file PATH] [--baseline-head531 PATH]

Exit 0 = all PASS, exit 1 = any FAIL.
"""

import argparse
import re
import subprocess
import sys

DOC = ".planning/osf_deviations.md"
BASELINE_COMMIT = "f650dd8"
FROZEN_LINES = 531

# Corrected figures that MUST be present in the (10b) section.
PRESENT_IN_10B = ["1.675", "0.0326", "1.579", "0.0517", "1.988", "1.241", "0.2171"]

# Superseded figures. These must NOT survive anywhere in the document EXCEPT
# inside the allow-listed paragraphs that exist precisely to name them.
SUPERSEDED = ["1.652", "0.0366", "1.564", "0.0556", "1.969"]

# Paragraphs permitted to contain superseded figures, keyed by a stable lead
# phrase (normalized + casefolded). Scoping is by REGION, not by per-value
# exception: any superseded figure outside these paragraphs is a FAIL.
ALLOWED_PARAGRAPH_ANCHORS = [
    "an earlier draft of this table estimated the pooled rate once from all 21 regions",
    "the courier's 1.99 was right and this table's 1.969 was the artifact",
]

# Figures that involve no pooled-rate choice and must not move, with their
# committed occurrence counts.
UNCHANGED_COUNTS = {"1.494248": 3, "0.728930": 4, "1.360272": 6}

results = []


def record(ok, name, detail=""):
    results.append((ok, name, detail))


def normalize(text):
    """Collapse markdown emphasis and ALL whitespace, then casefold.

    A literal grep has been blind on this file before: bold markers split a
    phrase, and hard-wrapping splits it across a newline. Normalizing removes
    both failure modes.
    """
    text = text.replace("—", "--").replace("–", "-")
    text = re.sub(r"[*_`>]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.casefold()


def section_10b(lines):
    """Return (start_idx, end_idx) of the #### (10b) section, 0-based, end exclusive."""
    start = None
    for i, ln in enumerate(lines):
        if normalize(ln).startswith("#### (10b)"):
            start = i
            break
    if start is None:
        return None
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("#### "):
            return (start, j)
    return (start, len(lines))


def paragraphs_with_lines(lines):
    """Yield (paragraph_text, [1-based line numbers])."""
    buf, nums = [], []
    for i, ln in enumerate(lines, start=1):
        if ln.strip() == "":
            if buf:
                yield ("\n".join(buf), nums)
            buf, nums = [], []
        else:
            buf.append(ln)
            nums.append(i)
    if buf:
        yield ("\n".join(buf), nums)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DOC)
    ap.add_argument("--baseline-head531", default=None)
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as fh:
        raw = fh.read()
    lines = raw.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    # ---- CHECK 1: lines 1..531 byte-identical to the baseline commit --------
    if args.baseline_head531:
        with open(args.baseline_head531, "rb") as fh:
            baseline = fh.read()
    else:
        baseline = subprocess.run(
            ["git", "show", f"{BASELINE_COMMIT}:{DOC}"],
            capture_output=True, check=True,
        ).stdout
        baseline = b"\n".join(baseline.split(b"\n")[:FROZEN_LINES]) + b"\n"

    current_head = b"\n".join(raw.encode("utf-8").split(b"\n")[:FROZEN_LINES]) + b"\n"
    record(
        current_head == baseline,
        f"FROZEN lines 1-{FROZEN_LINES} byte-identical to {BASELINE_COMMIT}",
        f"baseline {len(baseline)} B vs current {len(current_head)} B",
    )

    # ---- locate (10b) ------------------------------------------------------
    bounds = section_10b(lines)
    record(bounds is not None, "section (10b) located")
    if bounds is None:
        return finish()
    s, e = bounds
    sec_norm = normalize("\n".join(lines[s:e]))

    # ---- CHECK 2: corrected figures PRESENT in (10b) -----------------------
    for val in PRESENT_IN_10B:
        record(val in sec_norm, f"PRESENT in (10b): {val}")

    record("not established" in sec_norm, "PRESENT in (10b): NOT ESTABLISHED")

    # ---- CHECK 3: status unchanged ----------------------------------------
    record(
        "drafted -- not posted" in normalize(raw),
        "STATUS unchanged: DRAFTED -- NOT POSTED",
    )

    # ---- CHECK 4: superseded figures confined to the allow-listed paras ----
    allowed_lines = set()
    anchors_found = []
    for text, nums in paragraphs_with_lines(lines):
        n = normalize(text)
        for anchor in ALLOWED_PARAGRAPH_ANCHORS:
            if anchor in n:
                allowed_lines.update(nums)
                anchors_found.append(anchor)
    for anchor in ALLOWED_PARAGRAPH_ANCHORS:
        record(
            anchor in anchors_found,
            f"allow-list paragraph exists: '{anchor[:45]}...'",
        )

    for val in SUPERSEDED:
        stray = [
            i for i, ln in enumerate(lines, start=1)
            if val in ln and i not in allowed_lines
        ]
        record(
            not stray,
            f"SUPERSEDED {val} confined to the correction note",
            f"stray at lines {stray}" if stray else "",
        )

    # ---- CHECK 5: (10b) TABLE itself carries no superseded figure ----------
    table = [ln for ln in lines[s:e] if ln.lstrip().startswith("|")]
    record(bool(table), "(10b) table rows located", f"{len(table)} rows")
    tnorm = normalize("\n".join(table))
    for val in SUPERSEDED:
        record(val not in tnorm, f"ABSENT from the corrected table: {val}")

    # ---- CHECK 6: clustering figures must not move -------------------------
    for val, want in UNCHANGED_COUNTS.items():
        got = raw.count(val)
        record(got == want, f"UNCHANGED {val} count == {want}", f"got {got}")

    # ---- CHECK 7: DOCS-ONLY ------------------------------------------------
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", "src", "tests"],
        capture_output=True, text=True,
    ).stdout.strip()
    record(dirty == "", "DOCS-ONLY: src/ and tests/ clean", dirty)

    # ---- CHECK 8: the LIVE state docs agree with the corrected table --------
    # These carry the same straddle and would otherwise contradict the source.
    for live, must_have in (
        (".planning/STATE.md", ["0.0326", "0.0517", "0.2171", "1.241"]),
        (".planning/HANDOFF.json", ["0.0326", "0.0517", "0.2171", "1.988", "1.675"]),
    ):
        try:
            body = open(live, encoding="utf-8").read()
        except OSError as exc:
            record(False, f"live pin readable: {live}", str(exc))
            continue
        nbody = normalize(body)
        for val in must_have:
            record(val in nbody, f"LIVE PIN {live} carries {val}")

    # The unrelated AFR/EUR pass ratio 1.972 in STATE.md is NOT a Rao-Scott
    # figure and must survive untouched. Same literal, opposite disposition
    # from HANDOFF's 1.972 -- which is why this is pinned explicitly.
    state = open(".planning/STATE.md", encoding="utf-8").read()
    record(
        state.count("1.972") == 3,
        "STATE.md unrelated AFR/EUR ratio 1.972 preserved (3 sites)",
        f"got {state.count('1.972')}",
    )

    # ---- CHECK 9: HANDOFF.json is still parseable and stably formatted -----
    try:
        import json
        raw_h = open(".planning/HANDOFF.json", encoding="utf-8").read()
        parsed = json.loads(raw_h)
        record(True, "HANDOFF.json parses as JSON")
        record(
            json.dumps(parsed, indent=2) == raw_h,
            "HANDOFF.json formatting unchanged (indent=2, no trailing NL)",
        )
    except Exception as exc:  # noqa: BLE001
        record(False, "HANDOFF.json parses as JSON", str(exc))

    return finish()


def finish():
    failed = [r for r in results if not r[0]]
    for ok, name, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
