#!/usr/bin/env python3
"""
260820-s2x-instantiate.py — the substitution engine for the occlusion-gate
recalibration amendment.

WHY A SCRIPT AND NOT A HAND EDIT.
  Every one of the 21 slot values in
  .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  must be traceable to a record that is in git, not to a number an agent typed.
  This script PARSES the banked sweep records — it does not accept the
  Class-M values as arguments — so the banked files are the source, by
  construction. Hand-typing a number into the amendment is forbidden by the
  plan; this is the only sanctioned path in.

WHY IT RECONCILES BEFORE IT WRITES.
  An aggregate can agree while its components are wrong. The printed
  SITE-BASIS SUMMARY line is therefore re-derived from the 21-row per-region
  table in the SAME file (min / median / robust sigma = 1.4826 * MAD / max, plus
  the mean of the inflation column) and every statistic must agree before a
  single byte is written. Any mismatch aborts and writes nothing. The same
  discipline is applied to the SECOND banked record (the row-basis sweep).

WHY 0.5056% AND NOT 0.5055%.
  CEILING_3X_MEDIAN_PCT is taken AS PRINTED. It was computed upstream from the
  UNROUNDED median, so 3 * 0.1685 = 0.5055 differs from the printed 0.5056 by
  0.0001 — inside the guard's TOL_PCT of 0.001. The reconciliation below is an
  INSIDE-TOLERANCE check, deliberately not an equality check, and the printed
  value is what lands in the file.

CHANGELOG
  2026-08-20, quick-260820-u6i — EXTENSION for the multiplicity companion gate
  raised in the banked Seth attack
  (.planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md §4).
  * 8 NEW SLOTS, none of them an argument, none hand-typed:
      INFLATION_MIN_X / INFLATION_MEDIAN_X / INFLATION_MAX_X /
      INFLATION_ROBUST_SIGMA_X  — min, median, max and 1.4826*MAD of the
      `inflation` (8th) column of the banked site-basis per-region table;
      INFLATION_CEILING_3X_X    = 3 * INFLATION_MEDIAN_X;
      INFLATION_MARGIN_X        = INFLATION_CEILING_3X_X / INFLATION_MAX_X;
      ROW_MEDIAN_PCT            — parsed from the SECOND banked record, the
                                  ROW-basis sweep, and reconciled against that
                                  file's own 21 per-region `frac=` values;
      FRACTION_RATIO_X          = ROW_MEDIAN_PCT / SITE_MEDIAN_PCT.
  * SECOND BANKED SOURCE: SOURCE_ROW, hard-coded for the same reason SOURCE is.
  * The four inflation column statistics have NO printed upstream aggregate to
    reconcile against (unlike the site-fraction summary), so they get a
    different and stronger check instead: EXPECTED_RENDER, a set of
    PRE-REGISTERED RENDERED STRINGS fixed in 260820-u6i-PLAN.md before this
    code was written. A must-be-identity string comparison is used deliberately
    in preference to a must-be-close numeric one.
  * RENDER EXCEPTION: every x-ratio renders at 2 dp (`%.2fx`) EXCEPT
    INFLATION_ROBUST_SIGMA_X, which renders at 4 dp (`%.4fx`). At 2 dp its value
    0.089 collapses to `0.09x`, which destroys the quantity. The guard's `*_X)`
    filled-value pattern accepts both widths, so this needs no guard special
    case. (The planning brief called this slot INFLATION_ROBUST_SIGMA; it is
    named ..._X here so a SINGLE `*_X)` arm covers all six inflation/ratio
    slots and the guard's fail-closed `*)` arm survives untouched.)
  * TWO NEW MODES: --dry-run (computes, reconciles, renders, prints, writes
    NOTHING) and --second-pass (re-instantiation of an ALREADY-instantiated
    document). The "refusing to run twice" safety check is NOT deleted — it is
    gated behind --second-pass.
  * NEGATIVE-CONTROL SOURCE OVERRIDES: --control-source / --control-row-source
    make EXPECTED_RENDER falsifiable. Either one FORCES --dry-run, so "a real
    run cannot be pointed at a different file" is preserved.

CLASS-M vs CLASS-P — the distinction that makes --second-pass work.
  Class-M (19 MEASURED slots) are computed from the banked records. Under
  --second-pass a Class-M slot with sentinels is substituted; a Class-M slot
  whose ledger line already carries a filled value is VERIFIED byte-identical
  against the freshly computed value and any drift ABORTS the run.
  Class-P (POSTING_DATE, PRE_EXECUTE_COMMIT) are argv-sourced and are DEFINED
  to move: the amendment's own pre-paste table commits to re-confirming both at
  posting. They are therefore FORCE-SUBSTITUTED document-wide at every
  occurrence. Applying the Class-M drift-abort to them would deadlock the mode
  on its first real use, because any later HEAD is necessarily a different hash.

Usage:
  python3 260820-s2x-instantiate.py <amendment_path> \
      --pre-execute-commit <40-hex> --posting-date YYYY-MM-DD [--second-pass]
  python3 260820-s2x-instantiate.py --dry-run
  python3 260820-s2x-instantiate.py --dry-run --control-source <perturbed copy>
"""

import argparse
import re
import statistics
import sys

# The banked records. Hard-coded (not arguments) because they ARE the sources.
SOURCE = ".planning/debug/260820-site-basis-sweep-results-as-received.md"
SOURCE_ROW = ".planning/debug/260819-occ-measure-sweep-results-as-received.md"

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

# quick-260820-u6i — the 8 companion-gate slots, ADDED (the 13 above are untouched).
GUARD_PATTERNS.update({
    "ROW_MEDIAN_PCT": r"^  ROW_MEDIAN_PCT = [0-9]+\.[0-9]+%$",
    "FRACTION_RATIO_X": r"^  FRACTION_RATIO_X = [0-9]+\.[0-9]+x$",
    "INFLATION_MIN_X": r"^  INFLATION_MIN_X = [0-9]+\.[0-9]+x$",
    "INFLATION_MEDIAN_X": r"^  INFLATION_MEDIAN_X = [0-9]+\.[0-9]+x$",
    "INFLATION_MAX_X": r"^  INFLATION_MAX_X = [0-9]+\.[0-9]+x$",
    "INFLATION_ROBUST_SIGMA_X": r"^  INFLATION_ROBUST_SIGMA_X = [0-9]+\.[0-9]+x$",
    "INFLATION_CEILING_3X_X": r"^  INFLATION_CEILING_3X_X = [0-9]+\.[0-9]+x$",
    "INFLATION_MARGIN_X": r"^  INFLATION_MARGIN_X = [0-9]+\.[0-9]+x$",
})

# Argv-sourced, not measured. They are DEFINED to move; see the CHANGELOG note.
CLASS_P = ("POSTING_DATE", "PRE_EXECUTE_COMMIT")

# Ledger order as it appears in the amendment (R5 of 260820-u6i-PLAN.md): the 11
# measured site-basis slots, then the 8 companion-gate slots, then Class-P last.
ROSTER = [k for k in GUARD_PATTERNS if k not in CLASS_P] + list(CLASS_P)
assert set(ROSTER) == set(GUARD_PATTERNS) and len(ROSTER) == 21

# Slots that render at 4 dp rather than 2 dp. See the CHANGELOG's RENDER EXCEPTION.
FOUR_DP_X = ("INFLATION_ROBUST_SIGMA_X",)

# PRE-REGISTERED RENDERED STRINGS. Fixed in
# .planning/quick/260820-u6i-revise-the-instantiated-amendment-per-se/260820-u6i-PLAN.md
# (<interfaces>, "THE 8 NEW SLOTS") BEFORE this code existed. A script that
# computes anything else is loudly wrong; the comparison is byte-exact on the
# RENDERED string, deliberately, rather than numeric-and-close.
EXPECTED_RENDER = {
    "INFLATION_MIN_X": "1.04x", "INFLATION_MEDIAN_X": "1.14x", "INFLATION_MAX_X": "1.79x",
    "INFLATION_ROBUST_SIGMA_X": "0.0890x", "INFLATION_CEILING_3X_X": "3.42x",
    "INFLATION_MARGIN_X": "1.91x", "FRACTION_RATIO_X": "1.12x", "ROW_MEDIAN_PCT": "0.1888%",
}

DRY_PLACEHOLDER = "<DRY-RUN PLACEHOLDER — argv not supplied>"


def die(msg):
    print("ABORT: " + msg, file=sys.stderr)
    sys.exit(1)


def parse_summary(text, src):
    """The four verbatim summary lines are the SOLE site-basis Class-M source."""
    m = re.search(
        r"SITE-BASIS SUMMARY n=(\d+):\s*min=([0-9.]+)%\s*median=([0-9.]+)%\s*"
        r"max=([0-9.]+)%;\s*robust_sigma\(1\.4826\*MAD\)=([0-9.]+)%",
        text,
    )
    if not m:
        die("SITE-BASIS SUMMARY line not found in " + src)
    n = int(m.group(1))
    if n != N_REGIONS:
        die("summary says n=%d, expected n=%d" % (n, N_REGIONS))

    c = re.search(r"CANDIDATE CEILING \(Seth C3, 3x site-basis median\):\s*([0-9.]+)%", text)
    if not c:
        die("CANDIDATE CEILING line not found in " + src)

    g = re.search(r"margin over observed site-basis max:\s*([0-9.]+)x", text)
    if not g:
        die("margin-over-max line not found in " + src)

    i = re.search(r"mean row/site inflation across sample:\s*([0-9.]+)x", text)
    if not i:
        die("mean row/site inflation line not found in " + src)

    return {
        "SITE_MIN_PCT": float(m.group(2)),
        "SITE_MEDIAN_PCT": float(m.group(3)),
        "SITE_MAX_PCT": float(m.group(4)),
        "SITE_ROBUST_SIGMA_PCT": float(m.group(5)),
        "CEILING_3X_MEDIAN_PCT": float(c.group(1)),
        "CEILING_MARGIN_X": float(g.group(1)),
        "MEAN_ROW_SITE_INFLATION": float(i.group(1)),
    }


def parse_table(text, src):
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
        die("per-region table in %s yielded %d data rows, expected %d"
            % (src, len(rows), N_REGIONS))
    return rows


def parse_row_summary(text, src):
    """quick-260820-u6i — the ROW-basis sweep's own SUMMARY line: ROW_MEDIAN_PCT's source."""
    m = re.search(
        r"SUMMARY n=(\d+):\s*frac\s*min=([0-9.]+)%\s*median=([0-9.]+)%\s*max=([0-9.]+)%",
        text,
    )
    if not m:
        die("row-basis SUMMARY line not found in " + src)
    n = int(m.group(1))
    if n != N_REGIONS:
        die("row-basis summary says n=%d, expected n=%d" % (n, N_REGIONS))
    return {
        "ROW_MIN_PCT": float(m.group(2)),
        "ROW_MEDIAN_PCT": float(m.group(3)),
        "ROW_MAX_PCT": float(m.group(4)),
    }


def parse_row_table(text, src):
    """The row sweep's own 21 per-region `frac=` values — the components."""
    fracs = [float(x) for x in re.findall(r"frac=([0-9.]+)%", text)]
    if len(fracs) != N_REGIONS:
        die("row-basis per-region table in %s yielded %d frac values, expected %d"
            % (src, len(fracs), N_REGIONS))
    return fracs


def reconcile_row(parsed_row, fracs, src):
    """Same discipline as reconcile(): an aggregate can agree while components are wrong."""
    recomputed = {
        "ROW_MIN_PCT": min(fracs),
        "ROW_MEDIAN_PCT": statistics.median(fracs),
        "ROW_MAX_PCT": max(fracs),
    }
    print("ROW-BASIS RECONCILIATION — printed summary vs recomputed from the %d `frac=` values"
          % N_REGIONS)
    print("  source: %s" % src)
    print("  %-24s %12s %12s %10s %8s %s"
          % ("STATISTIC", "PRINTED", "RECOMPUTED", "DELTA", "TOL", "VERDICT"))
    bad = []
    for k, v in recomputed.items():
        d = abs(parsed_row[k] - v)
        ok = d <= TOL_RECON_PCT
        if not ok:
            bad.append(k)
        print("  %-24s %12.6f %12.6f %10.6f %8.4f %s"
              % (k, parsed_row[k], v, d, TOL_RECON_PCT, "OK" if ok else "MISMATCH"))
    if bad:
        die("row-basis reconciliation FAILED for: %s — nothing written" % ", ".join(bad))
    print("ROW-BASIS RECONCILIATION: OK — the row median re-derives from its own components")
    print()


def reconcile(parsed, rows, src):
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
    print("  source: %s" % src)
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


def companion_stats(rows):
    """quick-260820-u6i — the multiplicity companion gate, from the inflation column.

    These four column statistics have NO printed upstream aggregate to reconcile
    against, so EXPECTED_RENDER (pre-registered rendered strings) is their check.
    """
    infl = [r["inflation"] for r in rows]
    i_med = statistics.median(infl)
    i_mad = statistics.median([abs(x - i_med) for x in infl])
    i_max = max(infl)
    ceiling = 3 * i_med
    if i_max == 0:
        die("inflation column maximum is 0 — INFLATION_MARGIN_X undefined")
    return {
        "INFLATION_MIN_X": min(infl),
        "INFLATION_MEDIAN_X": i_med,
        "INFLATION_MAX_X": i_max,
        "INFLATION_ROBUST_SIGMA_X": 1.4826 * i_mad,
        "INFLATION_CEILING_3X_X": ceiling,
        "INFLATION_MARGIN_X": ceiling / i_max,
    }


def render(k, v):
    if k.endswith("_PCT"):
        return "%.4f%%" % v
    if k in FOUR_DP_X:
        return "%.4fx" % v
    return "%.2fx" % v


def force_substitute_class_p(text, led_before, values, report):
    """Class-P is argv-sourced and DEFINED to move: replace at EVERY occurrence.

    A blind document-wide string replace is a sharp tool, so each replace is
    fenced: refuse on an empty/sentinel current value; count the OLD literal
    before, assert the NEW literal occurs exactly that many times after, assert
    the OLD literal is gone (unless old == new), and assert the untouched
    INSTANTIATION date's occurrence count is unchanged ACROSS THE SAME REPLACE
    (dynamic before/after — never a hard-coded expected count, because prose
    added by the same task may legitimately change the absolute number).
    """
    PROBE = "2026-08-20"  # the INSTANTIATION date; must never be disturbed
    for k in CLASS_P:
        cur = led_before.get(k)
        if cur is None:
            die("cannot force-substitute %s: no SLOT_LEDGER line found for it" % k)
        cur = cur.strip()
        if not cur:
            die("refusing to force-substitute %s: its current ledger value is EMPTY" % k)
        if "{{" in cur or "}}" in cur:
            die("refusing to force-substitute %s: its current ledger value is still a "
                "sentinel (%r) — run the first-pass instantiation instead" % (k, cur))
        new = values[k]
        n_before = text.count(cur)
        if n_before < 1:
            die("force-substitution of %s found ZERO occurrences of its current ledger "
                "value %r" % (k, cur))
        probe_before = text.count(PROBE)
        text = text.replace(cur, new)
        probe_after = text.count(PROBE)
        n_after = text.count(new)
        if n_after != n_before:
            die("force-substitution of %s replaced %d occurrence(s) but the new value now "
                "occurs %d time(s)" % (k, n_before, n_after))
        if cur != new and text.count(cur) != 0:
            die("force-substitution of %s left %d occurrence(s) of the superseded literal %r"
                % (k, text.count(cur), cur))
        if probe_after != probe_before:
            die("force-substitution of %s disturbed the untouched instantiation date %s "
                "(%d -> %d occurrences across the same replace)"
                % (k, PROBE, probe_before, probe_after))
        report[k] = {
            "mode": "FORCE-SUBSTITUTED (argv)",
            "n": n_before,
            "old": cur,
            "probe": probe_before,
        }
        print("  FORCE-SUBSTITUTED %-20s %s -> %s  (%d occurrence(s); '%s' count %d "
              "unchanged across the replace)"
              % (k, cur if len(cur) <= 12 else cur[:7] + "…", new if len(new) <= 12 else new[:7] + "…",
                 n_before, PROBE, probe_before))
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("amendment", nargs="?")
    ap.add_argument("--pre-execute-commit")
    ap.add_argument("--posting-date")
    ap.add_argument("--dry-run", action="store_true",
                    help="compute, reconcile, render and print; write NOTHING")
    ap.add_argument("--second-pass", action="store_true",
                    help="re-instantiate an already-instantiated document: Class-M is "
                         "sentinel-or-verify, Class-P is force-substituted")
    ap.add_argument("--control-source",
                    help="NEGATIVE CONTROL ONLY: override the banked site-basis record. "
                         "Forces --dry-run.")
    ap.add_argument("--control-row-source",
                    help="NEGATIVE CONTROL ONLY: override the banked row-basis record. "
                         "Forces --dry-run.")
    args = ap.parse_args()

    control = bool(args.control_source or args.control_row_source)
    dry_run = args.dry_run or control
    if control:
        if args.second_pass:
            die("a negative-control source cannot be combined with a write mode "
                "(--second-pass); the control modes exist to make EXPECTED_RENDER "
                "falsifiable, not to write")
        print("*** NEGATIVE CONTROL MODE — WRITE PATH DISABLED ***")
        print("*** site-basis source : %s" % (args.control_source or SOURCE))
        print("*** row-basis source  : %s" % (args.control_row_source or SOURCE_ROW))
        print()

    if not dry_run:
        if not args.amendment:
            die("an amendment path is required unless --dry-run is given")
        if not args.pre_execute_commit or not args.posting_date:
            die("--pre-execute-commit and --posting-date are required unless --dry-run")

    src_path = args.control_source or SOURCE
    src_row_path = args.control_row_source or SOURCE_ROW

    src_text = open(src_path).read()
    parsed = parse_summary(src_text, src_path)
    rows = parse_table(src_text, src_path)
    reconcile(parsed, rows, src_path)

    row_text = open(src_row_path).read()
    parsed_row = parse_row_summary(row_text, src_row_path)
    fracs = parse_row_table(row_text, src_row_path)
    reconcile_row(parsed_row, fracs, src_row_path)

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

    # quick-260820-u6i — the companion gate and the two cross-basis quantities.
    companion = companion_stats(rows)
    row_median = parsed_row["ROW_MEDIAN_PCT"]
    if med == 0:
        die("SITE_MEDIAN_PCT is 0 — FRACTION_RATIO_X undefined")
    companion["ROW_MEDIAN_PCT"] = row_median
    companion["FRACTION_RATIO_X"] = row_median / med

    source_of = {}
    values = {}
    for k, v in parsed.items():
        values[k] = render(k, v)
        source_of[k] = "parsed (site sweep)"
    for k, v in derived.items():
        values[k] = render(k, v)
        source_of[k] = "derived"
    for k, v in companion.items():
        values[k] = render(k, v)
    source_of["ROW_MEDIAN_PCT"] = "parsed (row sweep)"
    source_of["FRACTION_RATIO_X"] = "derived (cross-basis)"
    for k in ("INFLATION_MIN_X", "INFLATION_MEDIAN_X", "INFLATION_MAX_X",
              "INFLATION_ROBUST_SIGMA_X"):
        source_of[k] = "column stat (site sweep)"
    source_of["INFLATION_CEILING_3X_X"] = "derived"
    source_of["INFLATION_MARGIN_X"] = "derived"

    class_p_placeholder = {}
    for k, argval in (("PRE_EXECUTE_COMMIT", args.pre_execute_commit),
                      ("POSTING_DATE", args.posting_date)):
        if argval:
            values[k] = argval
            source_of[k] = "argv"
        else:
            values[k] = DRY_PLACEHOLDER
            source_of[k] = "argv (NOT SUPPLIED — dry run)"
            class_p_placeholder[k] = True

    missing = [k for k in ROSTER if k not in values]
    if missing:
        die("no value produced for: %s" % ", ".join(missing))
    extra = [k for k in values if k not in ROSTER]
    if extra:
        die("value produced for a name not on the roster: %s" % ", ".join(extra))

    # PRE-REGISTERED EXPECTATIONS — byte-exact on the rendered string. This is
    # the check that stands in for the reconciliation the column statistics
    # cannot have; see the CHANGELOG.
    print("PRE-REGISTERED RENDER EXPECTATIONS (260820-u6i-PLAN.md)")
    bad_expect = []
    for k in sorted(EXPECTED_RENDER):
        got, want = values[k], EXPECTED_RENDER[k]
        verdict = "OK" if got == want else "MISMATCH"
        if got != want:
            bad_expect.append(k)
        print("  %-24s computed %-10s expected %-10s %s" % (k, got, want, verdict))
    for k in bad_expect:
        print("FAIL: PRE-REGISTERED EXPECTATION FAILED for %s: computed %s, expected %s"
              % (k, values[k], EXPECTED_RENDER[k]))
    if bad_expect:
        die("PRE-REGISTERED EXPECTATION FAILED for %s — nothing written"
            % ", ".join(bad_expect))
    print("PRE-REGISTERED EXPECTATIONS: OK — all %d rendered strings byte-identical"
          % len(EXPECTED_RENDER))
    print()

    # Render check BEFORE writing: every rendered ledger line must satisfy the
    # guard's own anchored filled-value pattern.
    checked = 0
    for k in ROSTER:
        if class_p_placeholder.get(k):
            continue
        line = "  %s = %s" % (k, values[k])
        if not re.match(GUARD_PATTERNS[k], line):
            die("rendered ledger line %r does not match the guard pattern %r"
                % (line, GUARD_PATTERNS[k]))
        checked += 1
    print("RENDER CHECK: OK — %d of %d rendered ledger lines match their guard patterns%s"
          % (checked, len(ROSTER),
             " (%d Class-P placeholder(s) skipped under --dry-run)"
             % len(class_p_placeholder) if class_p_placeholder else ""))
    print()

    counts = {}
    modes = {}
    verified = []
    n_open = n_close = 0
    total = 0

    if dry_run and not args.amendment:
        for k in ROSTER:
            counts[k] = 0
            modes[k] = "DRY-RUN (no document read)"
    else:
        text = open(args.amendment).read()
        n_open = text.count("{{")
        n_close = text.count("}}")
        if n_open != n_close:
            die("input has %d '{{' but %d '}}' — malformed sentinels" % (n_open, n_close))
        if n_open == 0 and not args.second_pass:
            die("input carries zero '{{' — it is already instantiated; refusing to run twice")

        led_before = dict(re.findall(r"(?m)^  ([A-Z0-9_]+) = (.*)$", text))

        # --- Class-M: sentinel-or-verify. Drift on a MEASURED slot aborts. ------
        if args.second_pass:
            print("CLASS-M DRIFT VERIFY — every already-filled ledger value must be "
                  "byte-identical to the value just computed from the banked records")
            for k in ROSTER:
                if k in CLASS_P:
                    continue
                cur = led_before.get(k)
                if cur is None or "{{" in cur or not cur.strip():
                    continue
                if cur.strip() != values[k]:
                    die("DRIFT — SLOT_LEDGER carries %s = %r but the banked records compute "
                        "%r. A measured value that moved, or was hand-edited, aborts the run."
                        % (k, cur.strip(), values[k]))
                verified.append(k)
                print("  VERIFIED-IN-PLACE  %-24s = %s" % (k, cur.strip()))
            print("CLASS-M DRIFT VERIFY: OK — %d already-filled measured value(s) unmoved"
                  % len(verified))
            print()

        # --- sentinel substitution (Class-M, and any Class-P that still has one) -
        for k in ROSTER:
            token = "{{%s}}" % k
            c = text.count(token)
            if c < 1:
                if not args.second_pass:
                    die("slot %s has ZERO occurrences in the input" % k)
                counts[k] = 0
                continue
            counts[k] = c
            text = text.replace(token, values[k])

        total = sum(counts.values())
        if args.second_pass:
            if total != n_open or total != n_close:
                die("substitution total %d != '{{' count %d / '}}' count %d — an unnamed "
                    "sentinel exists" % (total, n_open, n_close))
        else:
            if total != n_open or total != n_close:
                die("substitution total %d != '{{' count %d / '}}' count %d — an unnamed "
                    "sentinel exists" % (total, n_open, n_close))

        # --- Class-P: ALWAYS force-substituted, document-wide -------------------
        p_report = {}
        if args.second_pass:
            print("CLASS-P FORCE-SUBSTITUTION — argv-sourced slots, replaced at EVERY "
                  "occurrence (they are DEFINED to move; the pre-paste table commits to "
                  "re-confirming both at posting)")
            text = force_substitute_class_p(text, led_before, values, p_report)
            print()

        if "{{" in text or "}}" in text:
            die("sentinel delimiters survive substitution — refusing to write")

        for k in ROSTER:
            bits = []
            if counts.get(k):
                bits.append("SUBSTITUTED")
            if k in verified:
                bits.insert(0, "VERIFIED-IN-PLACE")
            if k in p_report:
                bits = [p_report[k]["mode"]]
            modes[k] = "+".join(bits) if bits else "UNTOUCHED"

        if dry_run:
            print("*** DRY RUN — %s NOT written ***" % args.amendment)
            print()
        else:
            with open(args.amendment, "w") as fh:
                fh.write(text)
            after = open(args.amendment).read()
            if after.count("{{") or after.count("}}"):
                die("post-write readback still shows sentinel delimiters")

    print("SUBSTITUTION LEDGER — %s" % (args.amendment or "(dry run, no document)"))
    print("  %-24s | %-42s | %11s | %s" % ("SLOT", "VALUE", "OCCURRENCES", "SOURCE"))
    for k in ROSTER:
        src = source_of[k]
        if modes.get(k) and modes[k] not in ("UNTOUCHED",):
            src = "%s [%s]" % (src, modes[k])
        print("  %-24s | %-42s | %11d | %s" % (k, values[k], counts.get(k, 0), src))
    print("  %-24s | %-42s | %11d | %s"
          % ("TOTALS", "%d slots" % len(ROSTER), total,
             "pre-count '{{'=%d '}}'=%d, post-count 0/0" % (n_open, n_close)))


if __name__ == "__main__":
    main()
