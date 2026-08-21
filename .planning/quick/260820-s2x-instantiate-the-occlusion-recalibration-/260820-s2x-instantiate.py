#!/usr/bin/env python3
"""
260820-s2x-instantiate.py — the substitution engine for the occlusion-gate
recalibration amendment.

WHY A SCRIPT AND NOT A HAND EDIT.
  Every one of the 13 slot values in
  .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  must be traceable to a record that is in git, not to a number an agent typed.
  This script PARSES the banked site-basis sweep record — it does not accept the
  Class-M values as arguments — so the banked file is the source, by construction.
  Hand-typing a number into the amendment is forbidden by the plan; this is the
  only sanctioned path in.

WHY IT RECONCILES BEFORE IT WRITES.
  An aggregate can agree while its components are wrong. The printed
  SITE-BASIS SUMMARY line is therefore re-derived from the 21-row per-region
  table in the SAME file (min / median / robust sigma = 1.4826 * MAD / max, plus
  the mean of the inflation column) and every statistic must agree before a
  single byte is written. Any mismatch aborts and writes nothing.

WHY 0.5056% AND NOT 0.5055%.
  CEILING_3X_MEDIAN_PCT is taken AS PRINTED. It was computed upstream from the
  UNROUNDED median, so 3 * 0.1685 = 0.5055 differs from the printed 0.5056 by
  0.0001 — inside the guard's TOL_PCT of 0.001. The reconciliation below is an
  INSIDE-TOLERANCE check, deliberately not an equality check, and the printed
  value is what lands in the file.

Usage:
  python3 260820-s2x-instantiate.py <amendment_path> \
      --pre-execute-commit <40-hex> --posting-date YYYY-MM-DD
"""

import argparse
import re
import statistics
import sys

# The banked record. Hard-coded (not an argument) because it IS the source.
SOURCE = ".planning/debug/260820-site-basis-sweep-results-as-received.md"

# Reconciliation tolerances. Percentages print at 4 dp upstream, so a 1-ulp
# print difference is 0.0001; inflation prints at 2 dp across 21 rows.
TOL_RECON_PCT = 0.0001
TOL_RECON_INFL = 0.005
# The guard's own tolerances, reused for the two upstream-rounded quantities.
TOL_PCT = 0.001
TOL_RATIO = 0.02

N_REGIONS = 21

# The guard's filled-value patterns, restated here so THIS script — not the
# guard — is the first thing to notice a bad render.
GUARD_PATTERNS = {
    "SITE_MIN_PCT": r"^  SITE_MIN_PCT = [0-9]+\.[0-9]+%$",
    "SITE_MEDIAN_PCT": r"^  SITE_MEDIAN_PCT = [0-9]+\.[0-9]+%$",
    "SITE_MAX_PCT": r"^  SITE_MAX_PCT = [0-9]+\.[0-9]+%$",
    "SITE_ROBUST_SIGMA_PCT": r"^  SITE_ROBUST_SIGMA_PCT = [0-9]+\.[0-9]+%$",
    "MEAN_ROW_SITE_INFLATION": r"^  MEAN_ROW_SITE_INFLATION = [0-9]+\.[0-9]+x$",
    "MED_PLUS_3SIG_PCT": r"^  MED_PLUS_3SIG_PCT = [0-9]+\.[0-9]+%$",
    "MED_PLUS_4SIG_PCT": r"^  MED_PLUS_4SIG_PCT = [0-9]+\.[0-9]+%$",
    "TWO_X_MEDIAN_PCT": r"^  TWO_X_MEDIAN_PCT = [0-9]+\.[0-9]+%$",
    "TWO_X_MAX_PCT": r"^  TWO_X_MAX_PCT = [0-9]+\.[0-9]+%$",
    "CEILING_3X_MEDIAN_PCT": r"^  CEILING_3X_MEDIAN_PCT = [0-9]+\.[0-9]+%$",
    "CEILING_MARGIN_X": r"^  CEILING_MARGIN_X = [0-9]+\.[0-9]+x$",
    "POSTING_DATE": r"^  POSTING_DATE = 20[0-9]{2}-[0-9]{2}-[0-9]{2}$",
    "PRE_EXECUTE_COMMIT": r"^  PRE_EXECUTE_COMMIT = [0-9a-f]{7,40}$",
}

ROSTER = list(GUARD_PATTERNS)


def die(msg):
    print("ABORT: " + msg, file=sys.stderr)
    sys.exit(1)


def parse_summary(text):
    """The four verbatim summary lines are the SOLE Class-M source."""
    m = re.search(
        r"SITE-BASIS SUMMARY n=(\d+):\s*min=([0-9.]+)%\s*median=([0-9.]+)%\s*"
        r"max=([0-9.]+)%;\s*robust_sigma\(1\.4826\*MAD\)=([0-9.]+)%",
        text,
    )
    if not m:
        die("SITE-BASIS SUMMARY line not found in " + SOURCE)
    n = int(m.group(1))
    if n != N_REGIONS:
        die("summary says n=%d, expected n=%d" % (n, N_REGIONS))

    c = re.search(r"CANDIDATE CEILING \(Seth C3, 3x site-basis median\):\s*([0-9.]+)%", text)
    if not c:
        die("CANDIDATE CEILING line not found in " + SOURCE)

    g = re.search(r"margin over observed site-basis max:\s*([0-9.]+)x", text)
    if not g:
        die("margin-over-max line not found in " + SOURCE)

    i = re.search(r"mean row/site inflation across sample:\s*([0-9.]+)x", text)
    if not i:
        die("mean row/site inflation line not found in " + SOURCE)

    return {
        "SITE_MIN_PCT": float(m.group(2)),
        "SITE_MEDIAN_PCT": float(m.group(3)),
        "SITE_MAX_PCT": float(m.group(4)),
        "SITE_ROBUST_SIGMA_PCT": float(m.group(5)),
        "CEILING_3X_MEDIAN_PCT": float(c.group(1)),
        "CEILING_MARGIN_X": float(g.group(1)),
        "MEAN_ROW_SITE_INFLATION": float(i.group(1)),
    }


def parse_table(text):
    """21 data rows: region_id n_rows n_sites occ_rows occ_sites row% site% infl."""
    rows = []
    for line in text.splitlines():
        m = re.match(
            r"^\s+(m2_region_\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+"
            r"([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*$",
            line,
        )
        if m:
            rows.append(
                {
                    "region_id": m.group(1),
                    "site_frac_pct": float(m.group(7)),
                    "inflation": float(m.group(8)),
                }
            )
    if len(rows) != N_REGIONS:
        die("per-region table yielded %d data rows, expected %d" % (len(rows), N_REGIONS))
    return rows


def reconcile(parsed, rows):
    """Recompute the aggregates from the components. Abort on any disagreement."""
    frac = [r["site_frac_pct"] for r in rows]
    infl = [r["inflation"] for r in rows]
    med = statistics.median(frac)
    mad = statistics.median([abs(x - med) for x in frac])
    recomputed = {
        "SITE_MIN_PCT": min(frac),
        "SITE_MEDIAN_PCT": med,
        "SITE_MAX_PCT": max(frac),
        "SITE_ROBUST_SIGMA_PCT": 1.4826 * mad,
        "MEAN_ROW_SITE_INFLATION": sum(infl) / len(infl),
    }

    print("RECONCILIATION — printed summary vs recomputed from the %d-row table" % N_REGIONS)
    print("  %-24s %12s %12s %10s %8s %s" % ("STATISTIC", "PRINTED", "RECOMPUTED", "DELTA", "TOL", "VERDICT"))
    bad = []
    for k, v in recomputed.items():
        tol = TOL_RECON_INFL if k == "MEAN_ROW_SITE_INFLATION" else TOL_RECON_PCT
        d = abs(parsed[k] - v)
        ok = d <= tol
        if not ok:
            bad.append(k)
        print("  %-24s %12.6f %12.6f %10.6f %8.4f %s"
              % (k, parsed[k], v, d, tol, "OK" if ok else "MISMATCH"))

    # The two upstream-rounded quantities: inside-tolerance, NOT equality.
    d_ceil = abs(parsed["CEILING_3X_MEDIAN_PCT"] - 3 * med)
    ok_ceil = d_ceil <= TOL_PCT
    if not ok_ceil:
        bad.append("CEILING_3X_MEDIAN_PCT")
    print("  %-24s %12.6f %12.6f %10.6f %8.4f %s"
          % ("CEILING_3X_MEDIAN_PCT", parsed["CEILING_3X_MEDIAN_PCT"], 3 * med,
             d_ceil, TOL_PCT, "OK (printed value kept)" if ok_ceil else "MISMATCH"))

    ratio = parsed["CEILING_3X_MEDIAN_PCT"] / max(frac)
    d_marg = abs(parsed["CEILING_MARGIN_X"] - ratio)
    ok_marg = d_marg <= TOL_RATIO
    if not ok_marg:
        bad.append("CEILING_MARGIN_X")
    print("  %-24s %12.6f %12.6f %10.6f %8.4f %s"
          % ("CEILING_MARGIN_X", parsed["CEILING_MARGIN_X"], ratio,
             d_marg, TOL_RATIO, "OK" if ok_marg else "MISMATCH"))

    if bad:
        die("reconciliation FAILED for: %s — nothing written" % ", ".join(bad))
    print("RECONCILIATION: OK — every printed aggregate re-derives from its components")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("amendment")
    ap.add_argument("--pre-execute-commit", required=True)
    ap.add_argument("--posting-date", required=True)
    args = ap.parse_args()

    src_text = open(SOURCE).read()
    parsed = parse_summary(src_text)
    rows = parse_table(src_text)
    reconcile(parsed, rows)

    # Derived — the draft's own formulas (draft lines 74-79). Never hand-typed.
    med = parsed["SITE_MEDIAN_PCT"]
    sig = parsed["SITE_ROBUST_SIGMA_PCT"]
    mx = parsed["SITE_MAX_PCT"]
    derived = {
        "MED_PLUS_3SIG_PCT": med + 3 * sig,
        "MED_PLUS_4SIG_PCT": med + 4 * sig,
        "TWO_X_MEDIAN_PCT": 2 * med,
        "TWO_X_MAX_PCT": 2 * mx,
    }

    source_of = {}
    values = {}
    for k, v in parsed.items():
        values[k] = ("%.2fx" % v) if k.endswith("_X") or k.endswith("_INFLATION") else ("%.4f%%" % v)
        source_of[k] = "parsed"
    for k, v in derived.items():
        values[k] = "%.4f%%" % v
        source_of[k] = "derived"
    values["PRE_EXECUTE_COMMIT"] = args.pre_execute_commit
    source_of["PRE_EXECUTE_COMMIT"] = "argv"
    values["POSTING_DATE"] = args.posting_date
    source_of["POSTING_DATE"] = "argv"

    missing = [k for k in ROSTER if k not in values]
    if missing:
        die("no value produced for: %s" % ", ".join(missing))
    extra = [k for k in values if k not in ROSTER]
    if extra:
        die("value produced for a name not on the roster: %s" % ", ".join(extra))

    # Render check BEFORE writing: every rendered ledger line must satisfy the
    # guard's own anchored filled-value pattern.
    for k in ROSTER:
        line = "  %s = %s" % (k, values[k])
        if not re.match(GUARD_PATTERNS[k], line):
            die("rendered ledger line %r does not match the guard pattern %r"
                % (line, GUARD_PATTERNS[k]))
    print("RENDER CHECK: OK — all %d rendered ledger lines match their guard patterns" % len(ROSTER))
    print()

    # Substitute.
    text = open(args.amendment).read()
    n_open = text.count("{{")
    n_close = text.count("}}")
    if n_open == 0:
        die("input carries zero '{{' — it is already instantiated; refusing to run twice")
    if n_open != n_close:
        die("input has %d '{{' but %d '}}' — malformed sentinels" % (n_open, n_close))

    counts = {}
    for k in ROSTER:
        token = "{{%s}}" % k
        c = text.count(token)
        if c < 1:
            die("slot %s has ZERO occurrences in the input" % k)
        counts[k] = c
        text = text.replace(token, values[k])

    total = sum(counts.values())
    if total != n_open or total != n_close:
        die("substitution total %d != '{{' count %d / '}}' count %d — an unnamed "
            "sentinel exists" % (total, n_open, n_close))

    if "{{" in text or "}}" in text:
        die("sentinel delimiters survive substitution — refusing to write")

    with open(args.amendment, "w") as fh:
        fh.write(text)

    after = open(args.amendment).read()
    if after.count("{{") or after.count("}}"):
        die("post-write readback still shows sentinel delimiters")

    print("SUBSTITUTION LEDGER — %s" % args.amendment)
    print("  %-24s | %-42s | %11s | %s" % ("SLOT", "VALUE", "OCCURRENCES", "SOURCE"))
    for k in ROSTER:
        print("  %-24s | %-42s | %11d | %s" % (k, values[k], counts[k], source_of[k]))
    print("  %-24s | %-42s | %11d | %s"
          % ("TOTALS", "13 slots", total, "pre-count '{{'=%d '}}'=%d, post-count 0/0"
             % (n_open, n_close)))


if __name__ == "__main__":
    main()
