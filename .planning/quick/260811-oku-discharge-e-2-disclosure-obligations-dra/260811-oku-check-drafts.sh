#!/usr/bin/env bash
# 260811-oku-check-drafts.sh
#
# Numbers-fidelity + framing-completeness acceptance harness for the three E-2
# disclosure DRAFT deliverables in this quick directory.
#
#   ./260811-oku-check-drafts.sh [--only ms|osf|surface] [--self-test]
#
# Exit 0 = every clause passed. Non-zero = at least one clause failed, or a
# required deliverable file is absent (absence is a LOUD FAILURE, never a skip).
#
# ---------------------------------------------------------------------------
# GREP DIALECT — MEASURED ON THIS NODE UNDER THE REAL SCRIPT INTERPRETER.
#
# This script runs under its own shebang, so `grep` resolves to /usr/bin/grep =
# **GNU grep 3.6** (measured 2026-08-11 on the NC State node). Under GNU grep
# 3.6 the boundary form `\b0\.00\b` was measured correct in BOTH directions:
#   MATCHES  : "anchor tiles 0.00% and", "0.00 at line start", "ends with 0.00"
#   NOMATCHES: "20.33", "10.005", "20.00%"
# The same `\b` form is used for `\b195\b` and `\b206\b` (measured: matches
# "195 of 206 regions", does not match "1955").
#
# ⚠ PROVENANCE CORRECTION. The PLAN for this task asserted that grep here is
# "ugrep 7.5.0" and that `(^|[^0-9])0\.00([^0-9]|$)` nomatches. That
# measurement came from an interactive CLI *wrapper* on the planning agent's
# shell (`type grep` -> wrapper), NOT from the node's script-execution
# interpreter. A script run via its shebang gets /usr/bin/grep (GNU grep 3.6),
# under which BOTH the old and the new pattern behave correctly. The `\b` form
# is kept because it is the clearer of the two and is independently verified
# above -- but do NOT propagate the ugrep claim. If you change the dialect,
# re-measure both directions: a boundary pattern that silently never matches is
# a clause structurally incapable of its job.
#   [[feedback_green_assertion_needs_a_negative_control]]
#
# ⚠ EVERY CLAUSE IS LINE-SCOPED. grep is line-oriented, so a required
# MULTI-WORD phrase must not be hard-wrapped across a newline in a deliverable:
# "not comparable", "not discharged", "exact + flipped", "no pre-registered
# number", "new supplementary file", "append-only", "Track A's frozen numbers",
# and SURF-02's Carter + choice/call/decision sentence must each sit on ONE
# line. This was itself discovered by a self-test control going red on a
# fixture whose preamble wrapped "not / comparable".
# ---------------------------------------------------------------------------

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MS_FILE="$SCRIPT_DIR/260811-oku-e2-manuscript-limitation-drafts.md"
OSF_FILE="$SCRIPT_DIR/260811-oku-e2-osf-entry-drafts.md"
SURF_FILE="$SCRIPT_DIR/260811-oku-e2-framing-decision-surface.md"

FAILS=0

pass()    { printf 'PASS %-8s %s\n' "$1" "$2"; }
fail()    { printf 'FAIL %-8s %s -- %s\n' "$1" "$2" "$3"; FAILS=$((FAILS + 1)); }
verdict() { # id desc problems
  if [ -z "$3" ]; then pass "$1" "$2"; else fail "$1" "$2" "$3"; fi
}

require_file() { # clause_id path
  if [ ! -f "$2" ]; then
    fail "$1" "deliverable file present" "file not found: $2"
    return 1
  fi
  return 0
}

extract_block() { # file block_id -> block body on stdout (marker lines removed)
  awk -v id="$2" '
    { line = $0; sub(/^[ \t]+/, "", line); sub(/[ \t]+$/, "", line) }
    line == "<!-- PASTE-BEGIN: " id " -->" { inb = 1; next }
    line == "<!-- PASTE-END: "   id " -->" { inb = 0; next }
    inb { print }
  ' "$1"
}

has()     { printf '%s\n' "$2" | grep -qE -- "$1"; }   # pattern, text
file_has(){ grep -qE -- "$1" "$2"; }                   # pattern, file

# ---------------------------------------------------------------------------
# clause group: ms
# ---------------------------------------------------------------------------
group_ms() {
  local f="$1"
  require_file "MS-00" "$f" || return
  local ids=(ms-limitation ms-correction)
  local id prob b w nb ne p

  prob=""
  for id in "${ids[@]}"; do
    nb=$(grep -cF -- "<!-- PASTE-BEGIN: $id -->" "$f")
    ne=$(grep -cF -- "<!-- PASTE-END: $id -->" "$f")
    [ "$nb" = "1" ] || prob="$prob $id:begin=$nb"
    [ "$ne" = "1" ] || prob="$prob $id:end=$ne"
  done
  verdict "MS-01" "both paste blocks present exactly once" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    w=$(extract_block "$f" "$id" | wc -w)
    { [ "$w" -ge 120 ] && [ "$w" -le 200 ]; } || prob="$prob $id:${w}words"
  done
  verdict "MS-02" "each block is 120-200 words" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    has '^[[:space:]]*#' "$b" && prob="$prob $id:markdown-header"
    has '\|'             "$b" && prob="$prob $id:table-pipe"
  done
  verdict "MS-03" "journal-ready prose: no headers, no tables inside a block" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    for p in '0\.06' '0\.07' '2\.74' '\b0\.00\b' '20\.33' '18\.41' '23\.80' 'APOL1_22q12' 'FTO_16q12'; do
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  verdict "MS-04" "every per-region number + the SH2B3 anchor-vs-tile3 split" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    for p in '17\.82' '38\.68' '\b195\b' '\b206\b'; do
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  verdict "MS-05" "corpus context: median, max, 195 of 206" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    for p in 'identity' 'use_identity' 'byte-identical' 'bookkeeping'; do
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  verdict "MS-06" "identity-LD-stub caveat in every block" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    has 'bindable|exact \+ flipped|transposed' "$b" || prob="$prob $id:no-denominator"
  done
  verdict "MS-07" "the denominator is stated in every block" "$prob"

  prob=""
  if file_has '5\.29' "$f"; then
    file_has 'dragged' "$f" || prob="$prob file:no-dragged-down-statement"
    for id in "${ids[@]}"; do
      b=$(extract_block "$f" "$id")
      if has '5\.29' "$b"; then
        has '18\.41' "$b" || prob="$prob $id:pooled-without-18.41"
        has '23\.80' "$b" || prob="$prob $id:pooled-without-23.80"
      fi
    done
  fi
  verdict "MS-08" "the pooled 5.29% is never quoted alone" "$prob"

  prob=""
  grep -qiE -- '\b(revisions?|salvage|cleanup)\b' "$f" && prob="file:non-original-research-framing-word"
  verdict "MS-09" "original-research framing (no revision/salvage/cleanup)" "$prob"

  prob=""
  for p in '46/182' '25\.3' 'fixture' 'CHR:POS' 'flip' 'palindrom' 'BETA' 'not comparable|NOT comparable' 'E-4' '207'; do
    file_has "$p" "$f" || prob="$prob file:missing($p)"
  done
  verdict "MS-10" "fixture correction, mechanism, consequences, E-4, 207 catalogs" "$prob"

  prob=""
  for p in 'DRAFT' 'not discharged'; do
    file_has "$p" "$f" || prob="$prob file:missing($p)"
  done
  verdict "MS-11" "states DRAFT + not discharged on its face" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: osf
# ---------------------------------------------------------------------------
group_osf() {
  local f="$1"
  require_file "OSF-00" "$f" || return
  local ids=(osf-limitation osf-correction)
  local id prob b w nb ne p

  prob=""
  for id in "${ids[@]}"; do
    nb=$(grep -cF -- "<!-- PASTE-BEGIN: $id -->" "$f")
    ne=$(grep -cF -- "<!-- PASTE-END: $id -->" "$f")
    [ "$nb" = "1" ] || prob="$prob $id:begin=$nb"
    [ "$ne" = "1" ] || prob="$prob $id:end=$ne"
  done
  verdict "OSF-01" "both OSF paste blocks present exactly once" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    w=$(extract_block "$f" "$id" | wc -w)
    [ "$w" -ge 250 ] || prob="$prob $id:${w}words"
  done
  verdict "OSF-02" "each OSF block is at least 250 words" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    has '^[[:space:]]*#' "$b" && prob="$prob $id:markdown-header"
  done
  verdict "OSF-03" "no markdown header inside an OSF paste body" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    for p in '0\.06' '0\.07' '2\.74' '\b0\.00\b' '20\.33' '18\.41' '23\.80' 'APOL1_22q12' 'FTO_16q12'; do
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  verdict "OSF-04" "every per-region number + the SH2B3 anchor-vs-tile3 split" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    for p in '17\.82' '38\.68' '\b195\b' '\b206\b'; do
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  verdict "OSF-05" "corpus context: median, max, 195 of 206" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    for p in 'identity' 'use_identity' 'byte-identical' 'bookkeeping'; do
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  verdict "OSF-06" "identity-LD-stub caveat in every block" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    has 'bindable|exact \+ flipped|transposed' "$b" || prob="$prob $id:no-denominator"
  done
  verdict "OSF-07" "the denominator is stated in every block" "$prob"

  prob=""
  if file_has '5\.29' "$f"; then
    file_has 'dragged' "$f" || prob="$prob file:no-dragged-down-statement"
    for id in "${ids[@]}"; do
      b=$(extract_block "$f" "$id")
      if has '5\.29' "$b"; then
        has '18\.41' "$b" || prob="$prob $id:pooled-without-18.41"
        has '23\.80' "$b" || prob="$prob $id:pooled-without-23.80"
      fi
    done
  fi
  verdict "OSF-08" "the pooled 5.29% is never quoted alone" "$prob"

  prob=""
  grep -qiE -- '\b(revisions?|salvage|cleanup)\b' "$f" && prob="file:non-original-research-framing-word"
  verdict "OSF-09" "original-research framing (no revision/salvage/cleanup)" "$prob"

  prob=""
  for p in '46/182' '25\.3' 'fixture' 'CHR:POS' 'flip' 'palindrom' 'BETA' 'not comparable|NOT comparable' 'E-4' '207'; do
    file_has "$p" "$f" || prob="$prob file:missing($p)"
    for id in "${ids[@]}"; do
      b=$(extract_block "$f" "$id")
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  verdict "OSF-10" "fixture correction, mechanism, consequences, E-4, 207 -- file AND every block" "$prob"

  prob=""
  for p in 'DRAFT' 'not discharged'; do
    file_has "$p" "$f" || prob="$prob file:missing($p)"
  done
  verdict "OSF-11" "states DRAFT + not discharged on its face" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    for p in 'az52u' 'pvb5j'; do
      has "$p" "$b" || prob="$prob $id:missing($p)"
    done
  done
  grep -qi -- 'append-only' "$f"            || prob="$prob file:missing(append-only)"
  grep -qi -- 'new supplementary file' "$f" || prob="$prob file:missing(new supplementary file)"
  verdict "OSF-12" "append-only NEW-supplementary-file semantics on az52u, prereg pvb5j named" "$prob"

  prob=""
  for id in "${ids[@]}"; do
    b=$(extract_block "$f" "$id")
    printf '%s\n' "$b" | grep -qi -- 'no pre-registered number' \
      || prob="$prob $id:missing(no pre-registered number)"
    has 'TRACK-A-FROZEN-NUMBERS|Track A.s frozen numbers' "$b" \
      || prob="$prob $id:missing(Track A frozen numbers)"
  done
  verdict "OSF-13" "no pre-registered number moved; Track A frozen numbers untouched" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: surface
# ---------------------------------------------------------------------------
group_surface() {
  local f="$1"
  require_file "SURF-00" "$f" || return
  local prob p

  prob=""
  file_has '^#{1,6}[[:space:]].*LIMITATION' "$f" || prob="$prob file:no-LIMITATION-heading"
  file_has '^#{1,6}[[:space:]].*CORRECTION' "$f" || prob="$prob file:no-CORRECTION-heading"
  verdict "SURF-01" "both framings appear as headings" "$prob"

  prob=""
  file_has 'Recommendation' "$f" || prob="$prob file:no-Recommendation"
  file_has 'Carter[^\n]*(choice|call|decision)|(choice|call|decision)[^\n]*Carter' "$f" \
    || prob="$prob file:choice-not-named-as-Carters"
  verdict "SURF-02" "a recommendation is given and the choice is named as Carter's" "$prob"

  prob=""
  file_has 're-analys|regenerat' "$f"          || prob="$prob file:no-CORRECTION-obligation"
  file_has 'no re-analysis|without re-analysis' "$f" || prob="$prob file:no-LIMITATION-obligation"
  verdict "SURF-03" "both framings' obligations are stated" "$prob"

  prob=""
  for p in '0\.06' '0\.07' '2\.74' '\b0\.00\b' '20\.33' '18\.41' '23\.80' 'APOL1_22q12' 'FTO_16q12' '17\.82' '38\.68' '\b195\b' '\b206\b' 'E-4' 'identity'; do
    file_has "$p" "$f" || prob="$prob file:missing($p)"
  done
  verdict "SURF-04" "the full per-region set, the corpus stats, E-4 and the identity caveat" "$prob"

  prob=""
  if file_has '5\.29' "$f"; then
    file_has 'dragged' "$f" || prob="$prob file:no-dragged-down-statement"
    file_has '18\.41'  "$f" || prob="$prob file:pooled-without-18.41"
    file_has '23\.80'  "$f" || prob="$prob file:pooled-without-23.80"
  fi
  grep -qiE -- '\b(revisions?|salvage|cleanup)\b' "$f" && prob="$prob file:non-original-research-framing-word"
  verdict "SURF-05" "pooled-alone guard + original-research framing guard" "$prob"
}

run_group() { # name file  -- runs in a subshell when captured
  case "$1" in
    ms)      group_ms      "$2" ;;
    osf)     group_osf     "$2" ;;
    surface) group_surface "$2" ;;
  esac
  [ "$FAILS" -eq 0 ]
}

# ---------------------------------------------------------------------------
# --self-test : the negative controls. Runnable with NO deliverable present.
# ---------------------------------------------------------------------------
self_test() {
  local d
  d="$(mktemp -d "${TMPDIR:-/tmp}/oku-selftest.XXXXXX")" || return 2
  trap 'rm -rf "$d"' RETURN

  # NOTE: the fixture keeps each control-targeted sentence on ONE line, both
  # because the clauses are line-scoped and so a control can delete exactly the
  # sentence it means to delete.
  cat > "$d/preamble.txt" <<'PRE'
# SELF-TEST FIXTURE -- synthetic, not a deliverable

This is a DRAFT fixture whose only purpose is to prove that this harness can fail. It is not discharged and it is not a disclosure.
File-level context: the previously quoted 46/182 = 25.3% figure was a synthetic acceptance fixture and not a measurement of anything real.
The pre-o7o join matched on CHR:POS with the alleles ignored; the allele-aware join flips the z rather than dropping the pair, and drops palindromic sites.
Reported BETA and SE do not move, but posterior inclusion probabilities and credible sets regenerated afterwards are not comparable to earlier ones.
The code-side change is coupled to E-4. The measurement covered 207 region variant catalogs.
PRE

  cat > "$d/blockA.txt" <<'BLKA'
Across the five regions on which the Track A colocalization results depend, the share of bindable variants whose reference and alternate alleles are transposed between the region variant catalog and the panel variant frame is 0.06% at CXADR_F2RL1_6p21, 0.07% at MC4R_18q21 and 2.74% at SH2B3_12q24, whose md5-pinned anchor tiles are 0.00% while its third tile is 20.33%, rising to 18.41% at APOL1_22q12 and 23.80% at FTO_16q12.
Pooled over the same set the figure is 5.29%, which is dragged down by the two clean large regions and must not be read on its own.
Across the wider corpus, 195 of the 206 measured regions carry at least one transposed pair, with a per-region median of 17.82% and a maximum of 38.68%.
Every panel measured is an identity-LD stub, built with use_identity set and with its ancestry directories byte-identical, so these counts describe variant bookkeeping and nothing more.
BLKA

  cat > "$d/blockB.txt" <<'BLKB'
Across the five regions on which the Track A colocalization results depend, the share of bindable variants whose reference and alternate alleles are transposed between the region variant catalog and the panel variant frame was measured at 0.06% for CXADR_F2RL1_6p21, 0.07% for MC4R_18q21 and 2.74% for SH2B3_12q24, whose md5-pinned anchor tiles are 0.00% while its third tile reaches 20.33%, rising to 18.41% for APOL1_22q12 and 23.80% for FTO_16q12.
Across the wider corpus, 195 of the 206 measured regions carry at least one transposed pair, with a per-region median of 17.82% and a maximum of 38.68%.
The join that produced those bindings ignored the alleles entirely, so a transposed pair could enter the reference panel carrying an unflipped association statistic at that coordinate.
Every panel measured is an identity-LD stub, built with use_identity set and with its ancestry directories byte-identical, so these counts describe variant bookkeeping and nothing more.
BLKB

  assemble() { # out blockA blockB
    {
      cat "$d/preamble.txt"
      printf '\n## Framing A -- LIMITATION\n\n'
      printf '<!-- PASTE-BEGIN: ms-limitation -->\n'
      cat "$2"
      printf '<!-- PASTE-END: ms-limitation -->\n'
      printf '\n## Framing B -- CORRECTION\n\n'
      printf '<!-- PASTE-BEGIN: ms-correction -->\n'
      cat "$3"
      printf '<!-- PASTE-END: ms-correction -->\n'
    } > "$1"
  }

  local st_fail=0

  # ---- positive control: the untouched fixture must be GREEN -----------------
  assemble "$d/base.md" "$d/blockA.txt" "$d/blockB.txt"
  local out rc
  out="$(run_group ms "$d/base.md")"; rc=$?
  printf '\n=== NC-0 (positive control): untouched fixture must PASS ===\n%s\nexit=%d\n' "$out" "$rc"
  if [ "$rc" -ne 0 ]; then
    printf 'SELF-TEST ERROR: the base fixture does not satisfy the ms clause group.\n'
    st_fail=1
  fi

  # ---- helper: assert a mutated fixture goes RED on a named clause ----------
  expect_red() { # label file clause sole(yes|no)
    local label="$1" file="$2" clause="$3" sole="$4" o r nfail
    o="$(run_group ms "$file")"; r=$?
    nfail=$(printf '%s\n' "$o" | grep -c '^FAIL ')
    printf '\n=== %s : expect %s to go RED%s ===\n' "$label" "$clause" \
      "$([ "$sole" = yes ] && printf ' (and ONLY %s)' "$clause")"
    printf '%s\n' "$o" | grep '^FAIL ' || printf '(no FAIL lines -- CONTROL DEFEATED)\n'
    printf 'exit=%d  fail_clauses=%d\n' "$r" "$nfail"
    if [ "$r" -eq 0 ]; then
      printf 'SELF-TEST ERROR: %s PASSED. The clause is structurally incapable of its job.\n' "$label"
      st_fail=1
      return
    fi
    if ! printf '%s\n' "$o" | grep -q "^FAIL $clause "; then
      printf 'SELF-TEST ERROR: %s failed, but not on %s.\n' "$label" "$clause"
      st_fail=1
    fi
    if [ "$sole" = yes ] && [ "$nfail" -ne 1 ]; then
      printf 'SELF-TEST ERROR: %s was expected to fail ONLY %s, but %d clauses failed.\n' \
        "$label" "$clause" "$nfail"
      st_fail=1
    fi
  }

  # NC-1 -- a WRONG number (18.41 -> 1.841) in the correction block.
  sed 's/18\.41/1.841/' "$d/blockB.txt" > "$d/nc1B.txt"
  assemble "$d/nc1.md" "$d/blockA.txt" "$d/nc1B.txt"
  expect_red "NC-1 (18.41 corrupted to 1.841)" "$d/nc1.md" "MS-04" yes

  # NC-2 -- the pooled figure quoted with the per-region numbers deleted.
  {
    printf 'Across the five regions on which the Track A colocalization results depend, a small share of bindable variants have reference and alternate alleles that are transposed between the region variant catalog and the panel variant frame, and the exposure is uneven across those regions.\n'
    grep -v 'whose reference and alternate alleles are transposed' "$d/blockA.txt"
  } > "$d/nc2A.txt"
  assemble "$d/nc2.md" "$d/nc2A.txt" "$d/blockB.txt"
  expect_red "NC-2 (pooled 5.29% quoted, per-region numbers deleted)" "$d/nc2.md" "MS-08" no

  # NC-2b -- the pooled figure kept, the dragged-down statement removed.
  #          Isolates MS-08: this is the ONLY mutation that fires it alone.
  assemble "$d/nc2b.md" "$d/blockA.txt" "$d/blockB.txt"
  sed -i 's/dragged/pulled/g' "$d/nc2b.md"
  expect_red "NC-2b (pooled 5.29% kept, 'dragged down' statement removed)" "$d/nc2b.md" "MS-08" yes

  # NC-3 -- the identity-LD-stub caveat deleted (whole sentence, one line).
  {
    grep -v 'identity-LD stub' "$d/blockA.txt"
    printf 'The measurement was read-only, cost nothing and made no perimeter contact, and it is reported here with no further qualification of any kind, which is the entire point of this negative control.\n'
  } > "$d/nc3A.txt"
  assemble "$d/nc3.md" "$d/nc3A.txt" "$d/blockB.txt"
  expect_red "NC-3 (identity-LD-stub caveat deleted)" "$d/nc3.md" "MS-06" yes

  # NC-4 -- an over-long block (>= 240 words).
  cp "$d/blockB.txt" "$d/nc4B.txt"
  while [ "$(wc -w < "$d/nc4B.txt")" -lt 240 ]; do
    printf 'The measurement was performed read-only on the NC State tree at no cost and with no perimeter contact of any kind.\n' >> "$d/nc4B.txt"
  done
  assemble "$d/nc4.md" "$d/blockA.txt" "$d/nc4B.txt"
  expect_red "NC-4 (240-word block)" "$d/nc4.md" "MS-02" yes

  # NC-5 -- the SH2B3 anchor 0.00% figure silently OMITTED, everything else intact.
  sed 's/anchor tiles are 0\.00% while its third tile reaches 20\.33%/anchor tiles are clean while its third tile reaches 20.33%/' \
      "$d/blockB.txt" > "$d/nc5B.txt"
  assemble "$d/nc5.md" "$d/blockA.txt" "$d/nc5B.txt"
  expect_red "NC-5 (SH2B3 anchor 0.00% omitted; SH2B3 still 2.74%, tile 3 still 20.33%)" \
    "$d/nc5.md" "MS-04" yes

  printf '\n=== SELF-TEST VERDICT ===\n'
  if [ "$st_fail" -eq 0 ]; then
    printf 'SELF-TEST PASSED: every negative control was OBSERVED red on its named clause.\n'
    return 0
  fi
  printf 'SELF-TEST FAILED: at least one control did not behave as required (see above).\n'
  return 1
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
ONLY=""
DO_SELF_TEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --only)      ONLY="${2:-}"; shift 2 ;;
    --only=*)    ONLY="${1#--only=}"; shift ;;
    --self-test) DO_SELF_TEST=1; shift ;;
    -h|--help)
      printf 'usage: %s [--only ms|osf|surface] [--self-test]\n' "$(basename "$0")"
      exit 0 ;;
    *)
      printf 'unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

if [ "$DO_SELF_TEST" -eq 1 ]; then
  self_test
  exit $?
fi

case "$ONLY" in
  "")        group_ms "$MS_FILE"; group_osf "$OSF_FILE"; group_surface "$SURF_FILE" ;;
  ms)        group_ms "$MS_FILE" ;;
  osf)       group_osf "$OSF_FILE" ;;
  surface)   group_surface "$SURF_FILE" ;;
  *)         printf 'unknown --only value: %s (expected ms|osf|surface)\n' "$ONLY" >&2; exit 2 ;;
esac

printf '\n%d clause failure(s).\n' "$FAILS"
[ "$FAILS" -eq 0 ]
