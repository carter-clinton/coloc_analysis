#!/usr/bin/env bash
#
# 260819-u8d-placeholder-guard.sh — the enforcer for the occlusion-gate recalibration
# amendment draft.
#
# 1. WHAT IT ENFORCES AND WHY IT EXISTS.
#    The amendment body at
#    .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md is
#    drafted BEFORE the site-basis measurement exists. Every quantity that measurement
#    must supply is a named double-brace slot sentinel, so the body physically cannot
#    reach OSF carrying an unmeasured number — provided something FAILS while a sentinel
#    remains. That something is this script. An obligation with no failing check lapses
#    silently; this file is what stops that happening here.
#
# 2. `paste-ready` AND `arith` ARE EXPECTED RED IN DRAFT STATE.
#    Today the draft is uninstantiated, so `paste-ready` exits 1 (sentinels present,
#    basename still carries the XX date placeholder) and `arith` exits 1 ("cannot verify
#    — draft not instantiated"). That red is the guard WORKING, not a defect. Do not
#    "fix" it. `draft` and `quote` are expected GREEN today.
#
# 3. GREEN HERE IS EVIDENCE ONLY BECAUSE THE CONTROLS WERE SEEN RED.
#    Eight red controls (R1-R8) and three green controls (G1-G3) were executed and
#    transcribed verbatim — command, output, exit code — in the sibling file
#    260819-u8d-guard-controls-transcript.txt. Every check in this script has been
#    observed failing on a deliberately broken input before its pass was trusted.
#
# 4. FORBIDDEN REPAIR.
#    NEVER satisfy a check by deleting a slot sentinel instead of filling it, by
#    loosening the anchored filled-value patterns, by widening the arithmetic tolerance,
#    or by trimming the verbatim provenance quote. If a check is itself wrong, fix the
#    CHECK and re-run its control until it is seen red again.
#
#
# 5. CHANGELOG.
#    2026-08-20, quick-260820-u6i — EXTENSION, STRICTLY ADDITIVE. It adds 8 roster slots
#    (ROW_MEDIAN_PCT plus the seven companion-gate x-ratios), exactly ONE new `*_X)`
#    filled-value pattern arm in `paste-ready`, THREE new arithmetic identities and ONE new
#    ordering check in `arith`, at an explicitly stated x-ratio tolerance TOL_X = 0.01
#    (an unstated tolerance is an unfalsifiable check, so it is stated).
#    NO existing check was removed, renamed, loosened or given a wider tolerance: TOL_PCT
#    stays 0.001, TOL_RATIO stays 0.02, the fail-closed `*)` arm stays, the verbatim quote
#    range stays. The roster grew by `ROSTER+=` and NEEDED by `NEEDED +=`, and the new
#    identities were INSERTED before `sys.exit(rc)`, precisely so this file's own commit
#    diff carries ZERO deleted lines — that `git diff --numstat` field is the enforceable
#    form of "strictly additive", and it was MEASURED rather than asserted.
#    Growing the roster to 21 automatically requires 21 SLOT_LEDGER lines through
#    sec_draft's EXISTING count check; no new code was needed for that.
#    Each new identity was seen RED in isolation on a perturbed scratch copy, and every
#    pre-existing control (u8d R1-R8, s2x NC-1..NC-3) was re-run against THIS extended
#    guard. All of it — command, full output, exit code — is transcribed verbatim in
#    .planning/quick/260820-u6i-revise-the-instantiated-amendment-per-se/260820-u6i-guard-transcript.txt
# Usage: bash 260819-u8d-placeholder-guard.sh {draft|paste-ready|arith|quote|all} <amendment_path>
# Exit 0 = every check in the requested section PASSED. Exit 1 = at least one FAILED.
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
QUOTE_SRC="$REPO_ROOT/.planning/debug/260819-SETH-VERDICT-adjudication-confirmed-as-received.md"
QUOTE_FROM=102   # 1-indexed, inclusive
QUOTE_TO=107     # 1-indexed, inclusive

OPENER="--- PASTE INTO OSF FROM HERE ---"
CLOSER="--- PASTE ENDS HERE ---"
MIN_FILE_BYTES=6000
MIN_BLOCK_BYTES=3000

ROSTER=(SITE_MIN_PCT SITE_MEDIAN_PCT SITE_MAX_PCT SITE_ROBUST_SIGMA_PCT
        MEAN_ROW_SITE_INFLATION MED_PLUS_3SIG_PCT MED_PLUS_4SIG_PCT TWO_X_MEDIAN_PCT
        TWO_X_MAX_PCT CEILING_3X_MEDIAN_PCT CEILING_MARGIN_X POSTING_DATE
        PRE_EXECUTE_COMMIT)

# quick-260820-u6i — the companion-gate slots, APPENDED so the literal above is not
# rewritten (zero-deletion extension). sec_draft's ledger-line count check now demands 21
# ledger lines automatically, with no edit to sec_draft.
ROSTER+=(INFLATION_MIN_X INFLATION_MEDIAN_X INFLATION_MAX_X INFLATION_ROBUST_SIGMA_X
         INFLATION_CEILING_3X_X INFLATION_MARGIN_X FRACTION_RATIO_X ROW_MEDIAN_PCT)

RC=0
BLOCK=""
BLOCK_BYTES=0

pass_() { echo "PASS: $*"; }
fail_() { echo "FAIL: $*"; RC=1; }

usage() {
  echo "usage: $(basename "$0") {draft|paste-ready|arith|quote|all} <amendment_path>" >&2
  exit 2
}

# ---------------------------------------------------------------------------
# VACUITY FLOOR — runs FIRST in every section. An empty or gutted file satisfies
# every content assertion trivially; that silent-vacuity class is exactly what this
# guard exists to catch (controls R3 and R4).
# ---------------------------------------------------------------------------
vacuity() {
  local f="$1" bytes no nc lo lc
  if [ ! -f "$f" ]; then fail_ "vacuity: file does not exist: $f"; return 1; fi
  bytes=$(wc -c < "$f" | tr -d '[:space:]')
  if [ "$bytes" -lt "$MIN_FILE_BYTES" ]; then
    fail_ "vacuity: file under byte floor ($bytes B < $MIN_FILE_BYTES B): $f"; return 1
  fi
  pass_ "vacuity: file present, $bytes B (floor $MIN_FILE_BYTES B)"

  no=$(grep -o -F -- "$OPENER" "$f" | wc -l | tr -d '[:space:]')
  nc=$(grep -o -F -- "$CLOSER" "$f" | wc -l | tr -d '[:space:]')
  if [ "$no" -ne 1 ]; then fail_ "vacuity: PASTE opener occurs $no time(s), want exactly 1"; return 1; fi
  if [ "$nc" -ne 1 ]; then fail_ "vacuity: PASTE closer occurs $nc time(s), want exactly 1"; return 1; fi
  lo=$(grep -n -F -- "$OPENER" "$f" | head -1 | cut -d: -f1)
  lc=$(grep -n -F -- "$CLOSER" "$f" | head -1 | cut -d: -f1)
  if [ "$lo" -ge "$lc" ]; then
    fail_ "vacuity: opener at line $lo is not before closer at line $lc"; return 1
  fi
  pass_ "vacuity: exactly one opener (line $lo) before exactly one closer (line $lc)"

  BLOCK=$(sed -n "${lo},${lc}p" "$f")
  BLOCK_BYTES=$(printf '%s' "$BLOCK" | wc -c | tr -d '[:space:]')
  if [ "$BLOCK_BYTES" -lt "$MIN_BLOCK_BYTES" ]; then
    fail_ "vacuity: paste block under byte floor ($BLOCK_BYTES B < $MIN_BLOCK_BYTES B)"; return 1
  fi
  pass_ "vacuity: paste block $BLOCK_BYTES B (floor $MIN_BLOCK_BYTES B)"
  return 0
}

# ---------------------------------------------------------------------------
# draft — the checks that must be GREEN while the body is still uninstantiated.
# ---------------------------------------------------------------------------
sec_draft() {
  local f="$1" s miss=0 nled nsb nrb
  echo "== section: draft =="
  vacuity "$f" || return 1

  for s in "${ROSTER[@]}"; do
    if ! grep -q -F -- "$s" "$f"; then fail_ "draft: roster name absent from file: $s"; miss=1; fi
  done
  [ "$miss" -eq 0 ] && pass_ "draft: all ${#ROSTER[@]} roster names present"

  if grep -q -F -- "SLOT_LEDGER" "$f"; then
    pass_ "draft: SLOT_LEDGER block present"
  else
    fail_ "draft: SLOT_LEDGER block absent — the ledger is what makes a DELETED slot detectable"
  fi
  nled=$(grep -c -E '^  [A-Z0-9_]+ = ' "$f")
  if [ "$nled" -eq "${#ROSTER[@]}" ]; then
    pass_ "draft: SLOT_LEDGER carries exactly $nled ledger lines"
  else
    fail_ "draft: SLOT_LEDGER carries $nled ledger lines, want ${#ROSTER[@]}"
  fi

  nsb=$(printf '%s' "$BLOCK" | grep -o -F -- "(site basis)" | wc -l | tr -d '[:space:]')
  nrb=$(printf '%s' "$BLOCK" | grep -o -F -- "(row basis)"  | wc -l | tr -d '[:space:]')
  if [ "$nsb" -ge 3 ]; then pass_ "draft: '(site basis)' labelled $nsb times in the paste block (floor 3)"
  else fail_ "draft: '(site basis)' appears only $nsb time(s) in the paste block, want >= 3"; fi
  if [ "$nrb" -ge 3 ]; then pass_ "draft: '(row basis)' labelled $nrb times in the paste block (floor 3)"
  else fail_ "draft: '(row basis)' appears only $nrb time(s) in the paste block, want >= 3"; fi
}

# ---------------------------------------------------------------------------
# paste-ready — EXPECTED RED until PENDING PASTE #3 has been substituted in.
# ---------------------------------------------------------------------------
sec_paste_ready() {
  local f="$1" nb ne base s pat
  echo "== section: paste-ready =="
  vacuity "$f" || return 1

  nb=$(grep -o -F -- '{{' "$f" | wc -l | tr -d '[:space:]')
  ne=$(grep -o -F -- '}}' "$f" | wc -l | tr -d '[:space:]')
  if [ "$nb" -eq 0 ] && [ "$ne" -eq 0 ]; then
    pass_ "paste-ready: zero slot-sentinel delimiters remain"
  else
    fail_ "paste-ready: $nb opening and $ne closing sentinel delimiters remain — the body is UNINSTANTIATED and MUST NOT be pasted"
  fi

  base=$(basename "$f")
  case "$base" in
    *XX*) fail_ "paste-ready: basename still carries the XX date placeholder: $base" ;;
    *)    pass_ "paste-ready: basename carries no XX date placeholder: $base" ;;
  esac

  for s in "${ROSTER[@]}"; do
    case "$s" in
      MEAN_ROW_SITE_INFLATION|CEILING_MARGIN_X) pat="^  ${s} = [0-9]+\.[0-9]+x$" ;;
      POSTING_DATE)       pat="^  POSTING_DATE = 20[0-9]{2}-[0-9]{2}-[0-9]{2}$" ;;
      PRE_EXECUTE_COMMIT) pat="^  PRE_EXECUTE_COMMIT = [0-9a-f]{7,40}$" ;;
      # quick-260820-u6i: the six inflation/ratio slots. INSERTED BEFORE *_PCT) and AFTER
      # the explicit MEAN_ROW_SITE_INFLATION|CEILING_MARGIN_X arm, so first-match-wins
      # leaves CEILING_MARGIN_X's behaviour bit-identical. Accepts both the 2 dp and the
      # 4 dp render width (INFLATION_ROBUST_SIGMA_X renders at 4 dp, deliberately).
      *_X)                pat="^  ${s} = [0-9]+\.[0-9]+x$" ;;
      *_PCT)              pat="^  ${s} = [0-9]+\.[0-9]+%$" ;;
      *)                  fail_ "paste-ready: no filled-value pattern defined for $s"; continue ;;
    esac
    if grep -q -E -- "$pat" "$f"; then
      pass_ "paste-ready: ledger line $s matches its filled-value pattern"
    else
      fail_ "paste-ready: ledger line $s does not match its filled-value pattern ($pat) — filled wrongly, or DELETED instead of filled"
    fi
  done
}

# ---------------------------------------------------------------------------
# arith — the six derived identities plus ordering. Never skips.
# ---------------------------------------------------------------------------
sec_arith() {
  local f="$1"
  echo "== section: arith =="
  vacuity "$f" || return 1
  python3 - "$f" <<'PY'
import re, sys

TOL_PCT   = 0.001   # percentage points; inputs print at 4 dp, so worst-case propagated
                    # rounding is 4*0.00005 + 0.00005 = 0.00025 — 4x headroom. Deliberately
                    # NOT written 0.0005, to avoid visual confusion with the dead constant.
TOL_RATIO = 0.02

NEEDED = ["SITE_MIN_PCT","SITE_MEDIAN_PCT","SITE_MAX_PCT","SITE_ROBUST_SIGMA_PCT",
          "MEAN_ROW_SITE_INFLATION","MED_PLUS_3SIG_PCT","MED_PLUS_4SIG_PCT",
          "TWO_X_MEDIAN_PCT","TWO_X_MAX_PCT","CEILING_3X_MEDIAN_PCT","CEILING_MARGIN_X",
          "POSTING_DATE","PRE_EXECUTE_COMMIT"]

# quick-260820-u6i — APPENDED, not rewritten. TOL_X is a NEW constant for the x-ratio
# identities added below; TOL_RATIO above is UNTOUCHED and is not widened by this
# extension. 0.01 because every operand renders at 2 dp, so worst-case propagated rounding
# on a ratio of order 3.4/1.8 is about 0.004 — comfortably inside it.
NEEDED += ["INFLATION_MIN_X","INFLATION_MEDIAN_X","INFLATION_MAX_X",
           "INFLATION_ROBUST_SIGMA_X","INFLATION_CEILING_3X_X","INFLATION_MARGIN_X",
           "FRACTION_RATIO_X","ROW_MEDIAN_PCT"]
TOL_X = 0.01

rc = 0
def ok(m):   print("PASS: arith: " + m)
def bad(m):
    global rc
    print("FAIL: arith: " + m); rc = 1

txt = open(sys.argv[1]).read()
led = dict(re.findall(r"(?m)^  ([A-Z0-9_]+) = (.*)$", txt))

missing = [k for k in NEEDED if k not in led]
if missing:
    bad("SLOT_LEDGER is missing lines: %s" % ", ".join(missing))
    sys.exit(1)
ok("SLOT_LEDGER parsed, all %d roster lines present" % len(NEEDED))

unfilled = [k for k in NEEDED if "{{" in led[k] or "}}" in led[k] or not led[k].strip()]
if unfilled:
    bad("cannot verify — draft not instantiated; these ledger values are still sentinels or "
        "blank: %s" % ", ".join(unfilled))
    sys.exit(1)

def num(key, suffix):
    v = led[key].strip()
    if not v.endswith(suffix):
        bad("%s = %r does not end in %r" % (key, v, suffix)); raise SystemExit(1)
    try:
        return float(v[:-len(suffix)])
    except ValueError:
        bad("%s = %r is not numeric" % (key, v)); raise SystemExit(1)

mn   = num("SITE_MIN_PCT", "%")
med  = num("SITE_MEDIAN_PCT", "%")
mx   = num("SITE_MAX_PCT", "%")
sig  = num("SITE_ROBUST_SIGMA_PCT", "%")
p3   = num("MED_PLUS_3SIG_PCT", "%")
p4   = num("MED_PLUS_4SIG_PCT", "%")
x2m  = num("TWO_X_MEDIAN_PCT", "%")
x2mx = num("TWO_X_MAX_PCT", "%")
c3   = num("CEILING_3X_MEDIAN_PCT", "%")
marg = num("CEILING_MARGIN_X", "x")
infl = num("MEAN_ROW_SITE_INFLATION", "x")
ok("MEAN_ROW_SITE_INFLATION parsed as %.2fx (no identity; reported quantity)" % infl)

def ident(name, lhs, rhs, tol, unit):
    d = abs(lhs - rhs)
    if d <= tol:
        ok("%s holds (%.4f vs %.4f%s, |d|=%.4f <= tol %.4f)" % (name, lhs, rhs, unit, d, tol))
    else:
        bad("%s BROKEN (%.4f vs %.4f%s, |d|=%.4f > tol %.4f)" % (name, lhs, rhs, unit, d, tol))

ident("MED_PLUS_3SIG_PCT == SITE_MEDIAN_PCT + 3*SITE_ROBUST_SIGMA_PCT", p3, med + 3*sig, TOL_PCT, "%")
ident("MED_PLUS_4SIG_PCT == SITE_MEDIAN_PCT + 4*SITE_ROBUST_SIGMA_PCT", p4, med + 4*sig, TOL_PCT, "%")
ident("TWO_X_MEDIAN_PCT == 2*SITE_MEDIAN_PCT",                          x2m, 2*med,      TOL_PCT, "%")
ident("TWO_X_MAX_PCT == 2*SITE_MAX_PCT",                                x2mx, 2*mx,      TOL_PCT, "%")
ident("CEILING_3X_MEDIAN_PCT == 3*SITE_MEDIAN_PCT",                     c3, 3*med,       TOL_PCT, "%")
if mx == 0:
    bad("CEILING_MARGIN_X == CEILING_3X_MEDIAN_PCT / SITE_MAX_PCT undefined (SITE_MAX_PCT is 0)")
else:
    ident("CEILING_MARGIN_X == CEILING_3X_MEDIAN_PCT / SITE_MAX_PCT",   marg, c3/mx,      TOL_RATIO, "x")

if mn <= med <= mx:
    ok("ordering holds (min %.4f%% <= median %.4f%% <= max %.4f%%)" % (mn, med, mx))
else:
    bad("ordering BROKEN (min %.4f%%, median %.4f%%, max %.4f%%)" % (mn, med, mx))

# quick-260820-u6i — the multiplicity companion gate's three identities plus the
# inflation ordering check. Inserted immediately before sys.exit(rc); nothing above moved.
imn   = num("INFLATION_MIN_X", "x")
imed  = num("INFLATION_MEDIAN_X", "x")
imx   = num("INFLATION_MAX_X", "x")
isig  = num("INFLATION_ROBUST_SIGMA_X", "x")
ic3   = num("INFLATION_CEILING_3X_X", "x")
imarg = num("INFLATION_MARGIN_X", "x")
fr    = num("FRACTION_RATIO_X", "x")
rmed  = num("ROW_MEDIAN_PCT", "%")
ok("INFLATION_ROBUST_SIGMA_X parsed as %.4fx (reported dispersion; no identity)" % isig)
ident("INFLATION_CEILING_3X_X == 3*INFLATION_MEDIAN_X", ic3, 3*imed, TOL_X, "x")
if imx == 0:
    bad("INFLATION_MARGIN_X == INFLATION_CEILING_3X_X / INFLATION_MAX_X undefined (INFLATION_MAX_X is 0)")
else:
    ident("INFLATION_MARGIN_X == INFLATION_CEILING_3X_X / INFLATION_MAX_X", imarg, ic3/imx, TOL_X, "x")
if med == 0:
    bad("FRACTION_RATIO_X == ROW_MEDIAN_PCT / SITE_MEDIAN_PCT undefined (SITE_MEDIAN_PCT is 0)")
else:
    ident("FRACTION_RATIO_X == ROW_MEDIAN_PCT / SITE_MEDIAN_PCT", fr, rmed/med, TOL_X, "x")
if imn <= imed <= imx:
    ok("inflation ordering holds (min %.2fx <= median %.2fx <= max %.2fx)" % (imn, imed, imx))
else:
    bad("inflation ordering BROKEN (min %.2fx, median %.2fx, max %.2fx)" % (imn, imed, imx))

sys.exit(rc)
PY
  [ $? -ne 0 ] && RC=1
  return 0
}

# ---------------------------------------------------------------------------
# quote — the provenance paragraph is carried VERBATIM. Count identity, not a threshold.
# ---------------------------------------------------------------------------
sec_quote() {
  local f="$1"
  echo "== section: quote =="
  vacuity "$f" || return 1
  python3 - "$f" "$QUOTE_SRC" "$QUOTE_FROM" "$QUOTE_TO" <<'PY'
import sys, pathlib
amend, src, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rc = 0
def ok(m):   print("PASS: quote: " + m)
def bad(m):
    global rc
    print("FAIL: quote: " + m); rc = 1

p = pathlib.Path(src)
if not p.exists():
    bad("source of truth missing: %s" % src); sys.exit(1)
lines = [l.strip() for l in p.read_text().splitlines()[lo-1:hi] if l.strip()]
if not lines:
    bad("source range %s:%d-%d yielded ZERO non-blank lines — the check would be vacuous"
        % (src, lo, hi))
    sys.exit(1)
ok("source range %s:%d-%d yields %d non-blank lines" % (p.name, lo, hi, len(lines)))

a = pathlib.Path(amend).read_text()
hit = 0
for l in lines:
    if l in a:
        hit += 1
    else:
        bad("source line NOT carried verbatim: %r" % (l[:110] + ("..." if len(l) > 110 else "")))
if hit == len(lines):
    ok("count identity holds: %d/%d source lines carried verbatim" % (hit, len(lines)))
else:
    bad("count identity FAILS: %d/%d source lines carried verbatim" % (hit, len(lines)))
sys.exit(rc)
PY
  [ $? -ne 0 ] && RC=1
  return 0
}

[ $# -eq 2 ] || usage
SECTION="$1"
FILE="$2"

case "$SECTION" in
  draft)       sec_draft "$FILE" ;;
  paste-ready) sec_paste_ready "$FILE" ;;
  arith)       sec_arith "$FILE" ;;
  quote)       sec_quote "$FILE" ;;
  all)         sec_draft "$FILE"; sec_paste_ready "$FILE"; sec_arith "$FILE"; sec_quote "$FILE" ;;
  *)           usage ;;
esac

if [ "$RC" -eq 0 ]; then echo "GUARD ${SECTION}: GREEN"; else echo "GUARD ${SECTION}: RED"; fi
exit "$RC"
