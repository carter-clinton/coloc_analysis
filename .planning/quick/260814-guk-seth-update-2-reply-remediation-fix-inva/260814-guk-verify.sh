#!/usr/bin/env bash
# ============================================================================
# 260814-guk-verify.sh — re-runnable checker for quick task 260814-guk
#
#   usage:  bash 260814-guk-verify.sh {fire|record|reply|all}
#           bash 260814-guk-verify.sh _hexlen <file>   # F1's logic, standalone
#
#   exit 0 = every check in the requested section PASSED
#   exit 1 = at least one check FAILED
#
# Sections
#   fire   — the three executable runbook files (the trsx5 adjudication card)
#   record — the live record fields (HANDOFF.json / STATE.md / deferred-items)
#   reply  — the reply-to-Seth courier package
#
# ---------------------------------------------------------------------------
# WHY F1/P6 ARE GENERIC LENGTH INVARIANTS AND NOT AN EXPECTED-HASH LIST
# ---------------------------------------------------------------------------
# The defect this task exists to remove was a 31-character "md5" in the card
# Carter runs before a $385-1,084 irreversible spend. An md5 is 32 characters,
# so the STOP-truncated branch could never fire — a comparison structurally
# incapable of firing. An expected-hash list is BLIND to that class (the wrong
# string simply is not in the list, and nothing looks). A LENGTH invariant over
# every hex run catches it, and catches the NEXT truncation too, including one
# nobody predicted.
#
# F1's logic is exposed as the `_hexlen` sub-mode so the mutation negative
# control exercises the REAL code path rather than a re-implementation of it.
# A green here is evidence ONLY because `_hexlen` has been SEEN to go red on a
# one-character deletion. See the SUMMARY for the observed failure text.
#
# ---------------------------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------------------------
# WIDENED 2026-08-14 (`quick-260814-u9p`) per Seth's correction — the accepted
# hex-run lengths are now {32, 64}, not {32} alone. A 64-character sha256
# anchor is LEGITIMATE, and the pre-widening invariant would have rejected one:
# observed firsthand before the edit, a file carrying a single 64-char run went
# RED through this very `_hexlen` sub-mode. Rejecting real anchors is not
# strictness, it is a false positive that pressures the wrong repair.
#
# ⛔ FORBIDDEN REPAIR: truncating a sha256 to 32 characters to satisfy the old
# rule. That manufactures the EXACT silent-mismatch class this invariant exists
# to catch — a digest that is structurally incapable of matching anything, in a
# card read before an irreversible spend. Widen the invariant; never shorten the
# anchor.
#
# Paid for with negative controls, run through the shipped `_hexlen` path (never
# a re-implementation): 31-char RED, 63-char RED, 32-char GREEN, 64-char GREEN,
# with the pre-edit 64-char RED captured first so the greens are evidence rather
# than assertion. Re-runnable at any time via
# `.planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-verify.sh controls`.
#
# NOT CHANGED by this widening: `P6` in section `reply` carries its own inline
# allow-list (32 or 40, plus the narrow labelled 31-char exemption) scoped to the
# guk-era reply document, whose contents are fixed and known. It is DELIBERATELY
# untouched — its exemption is a statement about one specific document, not a
# general length rule, and widening it would loosen a guard that has nothing to
# do with sha256 anchors.
# ============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$ROOT" || exit 2

OX1="$ROOT/.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r"
AP="$OX1/260812-ox1-AGENT-PROMPT.md"
BP="$OX1/260812-ox1-BROWSER-PASTE.md"
RF="$OX1/260812-ox1-READY-TO-FIRE.md"
HJ="$ROOT/.planning/HANDOFF.json"
SM="$ROOT/.planning/STATE.md"
DI="$ROOT/.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md"
BASE="$HERE/260814-guk-baseline.txt"
REPLY="$HERE/260814-guk-REPLY-TO-SETH.md"

MD5_CANON="28ecdb3160833da80cfa25952f76415b"   # repo-canonical paste block, 9,758 B
MD5_SETH="425d925a88ab474ec2396cbea25e665c"    # Seth-complete lineage, 9,907 B (we do NOT hold it)
MD5_ADVISORY="c19be8b2ad7cd6a45fee1d668d8a9cf9" # Seth-reported via the OSF API; ADVISORY ONLY
BAD31="c19e8b2ad7cd6a45fee1d668d8a9cf9"        # the 31-char defect; must be gone from the fire surface

AMEND=".planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md"
AWKP='/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}'

RC=0
pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; RC=1; }

# block FILE START_RE END_RE  -> prints [START_RE line .. line before END_RE]
block() {
  awk -v s="$2" -v e="$3" 'BEGIN{p=0} (p && $0 ~ e){exit} ($0 ~ s){p=1} p{print}' "$1"
}

# hexlen_bad : stdin -> one line per hex run (>=20 chars) whose length is
#              NEITHER 32 (md5) NOR 64 (sha256).   [widened 2026-08-14, see CHANGELOG]
hexlen_bad() {
  grep -oE '[0-9a-f]{20,}' | awk '{ if (length($0) != 32 && length($0) != 64) printf "  len=%d  %s\n", length($0), $0 }'
}

has() { grep -qF -- "$2" <<<"$1"; }

# ---------------------------------------------------------------------------
# _hexlen sub-mode : run F1's invariant against an arbitrary file (the mutation
# negative control uses THIS, so the control tests the shipped logic).
# ---------------------------------------------------------------------------
if [ "${1:-}" = "_hexlen" ]; then
  tgt="${2:?_hexlen needs a file}"
  [ -s "$tgt" ] || { echo "FAIL  _hexlen: $tgt missing or empty"; exit 1; }
  bad="$(hexlen_bad <"$tgt")"
  nrun="$(grep -coE '[0-9a-f]{20,}' "$tgt" || true)"
  if [ -n "$bad" ]; then
    echo "FAIL  _hexlen($tgt): hex run(s) present that are neither 32 (md5) nor 64 (sha256):"
    echo "$bad"
    exit 1
  fi
  echo "PASS  _hexlen($tgt): every hex run >=20 chars is 32 (md5) or 64 (sha256) (lines with runs: $nrun)"
  exit 0
fi

# ===========================================================================
# SECTION: fire
# ===========================================================================
section_fire() {
  echo "--- section: fire -------------------------------------------------"

  local ap_card bp_card rf_card
  ap_card="$(block "$AP" '^STEP 6b' '^STEP 7')"
  bp_card="$(block "$BP" '^## 6b'   '^## 7')"
  rf_card="$(block "$RF" '^## 6b'   '^## 7[.]')"

  # -- F1: generic hex-run length invariant over each card block -------------
  # NON-VACUITY GUARD FIRST: an unmatched heading yields an EMPTY block, and an
  # empty block passes a length invariant trivially. That would be the very
  # defect class this file exists to detect, so an empty/short block is a FAIL.
  local f1=0 name blk bad
  for name in AGENT-PROMPT BROWSER-PASTE READY-TO-FIRE; do
    case "$name" in
      AGENT-PROMPT)  blk="$ap_card" ;;
      BROWSER-PASTE) blk="$bp_card" ;;
      READY-TO-FIRE) blk="$rf_card" ;;
    esac
    if [ "$(printf '%s\n' "$blk" | grep -c . || true)" -lt 5 ]; then
      fail "F1 [$name] card block is empty or under 5 lines — heading not found, invariant would be VACUOUS"
      f1=1; continue
    fi
    bad="$(printf '%s\n' "$blk" | hexlen_bad)"
    if [ -n "$bad" ]; then
      fail "F1 [$name] hex run(s) in the card block are neither 32 (md5) nor 64 (sha256):"
      printf '%s\n' "$bad"
      f1=1
    fi
  done
  [ $f1 -eq 0 ] && pass "F1  every hex run >=20 chars inside all three card blocks is 32 (md5) or 64 (sha256) (generic invariant)"

  # -- F2: the three expected literals are present in each card block --------
  local f2=0
  for name in AGENT-PROMPT BROWSER-PASTE READY-TO-FIRE; do
    case "$name" in
      AGENT-PROMPT)  blk="$ap_card" ;;
      BROWSER-PASTE) blk="$bp_card" ;;
      READY-TO-FIRE) blk="$rf_card" ;;
    esac
    for h in "$MD5_CANON" "$MD5_SETH" "$MD5_ADVISORY"; do
      has "$blk" "$h" || { fail "F2 [$name] card block is missing $h"; f2=1; }
    done
  done
  [ $f2 -eq 0 ] && pass "F2  all three card blocks carry 28ecdb31 / 425d925a / c19be8b2"

  # -- F3: attribution containment for the advisory hash --------------------
  # Every line carrying the advisory value must sit in a 4-line window (match
  # line + 3 following) naming Seth AND flagging it unverified.
  local f3=0 f n win
  for f in "$AP" "$BP" "$RF"; do
    while IFS=: read -r n _; do
      [ -n "$n" ] || continue
      win="$(sed -n "${n},$((n+3))p" "$f")"
      if ! { has "$win" "Seth" && grep -q 'nverified' <<<"$win"; }; then
        fail "F3 [$(basename "$f"):$n] advisory hash is not attributed to Seth + marked unverified within 4 lines"
        f3=1
      fi
    done < <(grep -nF -- "$MD5_ADVISORY" "$f" || true)
  done
  [ $f3 -eq 0 ] && pass "F3  every advisory-hash line is attributed (Seth + unverified) within a 4-line window"

  # -- F4: size-first ordering ----------------------------------------------
  local f4=0 lsize lhash
  for name in AGENT-PROMPT BROWSER-PASTE READY-TO-FIRE; do
    case "$name" in
      AGENT-PROMPT)  blk="$ap_card" ;;
      BROWSER-PASTE) blk="$bp_card" ;;
      READY-TO-FIRE) blk="$rf_card" ;;
    esac
    lsize="$(printf '%s\n' "$blk" | grep -nE '9,?758' | head -1 | cut -d: -f1)"
    lhash="$(printf '%s\n' "$blk" | grep -nF -- "$MD5_CANON" | head -1 | cut -d: -f1)"
    if [ -z "$lsize" ] || [ -z "$lhash" ]; then
      fail "F4 [$name] card block lacks a 9,758 mention or the canonical hash"
      f4=1
    elif [ "$lsize" -ge "$lhash" ]; then
      fail "F4 [$name] card is HASH-FIRST: 9,758 first appears on block line $lsize, 28ecdb31 on $lhash (need strictly before)"
      f4=1
    fi
  done
  [ $f4 -eq 0 ] && pass "F4  every card adjudicates SIZE-FIRST (9,758 precedes 28ecdb31 on an earlier line)"

  # -- F5: negative control on the invalid literal --------------------------
  local n_bad n_pref
  n_bad="$(cat "$AP" "$BP" "$RF" | grep -cF -- "$BAD31" || true)"
  n_pref="$(cat "$AP" "$BP" "$RF" | grep -cF -- "c19e8b2" || true)"
  if [ "$n_bad" -eq 0 ] && [ "$n_pref" -eq 0 ]; then
    pass "F5  the 31-char literal AND the bare prefix c19e8b2 are GONE from all three runbook files (0 / 0)"
  else
    fail "F5  invalid literal still on the fire surface: full=$n_bad prefix=$n_pref (both must be 0)"
  fi

  # -- F6: anchor re-derivation, working tree AND ac4c990 -------------------
  local wc_now md5_now wc_ref md5_ref
  wc_now="$(awk "$AWKP" "$AMEND" | wc -c | tr -d ' ')"
  md5_now="$(awk "$AWKP" "$AMEND" | md5sum | cut -d' ' -f1)"
  wc_ref="$(git show "ac4c990:$AMEND" | awk "$AWKP" | wc -c | tr -d ' ')"
  md5_ref="$(git show "ac4c990:$AMEND" | awk "$AWKP" | md5sum | cut -d' ' -f1)"
  if [ "$wc_now" = "9758" ] && [ "$md5_now" = "$MD5_CANON" ] \
     && [ "$wc_ref" = "9758" ] && [ "$md5_ref" = "$MD5_CANON" ]; then
    pass "F6  anchor re-derived: 9758 / $MD5_CANON on the working tree AND at ac4c990"
  else
    fail "F6  anchor re-derivation MISMATCH: worktree $wc_now/$md5_now ; ac4c990 $wc_ref/$md5_ref"
  fi

  # -- F7: item ordering in READY-TO-FIRE, no renumbering -------------------
  local l6 l6b l7 f7=0 k lk prev
  l6="$(grep -n '^## 6[.]' "$RF" | head -1 | cut -d: -f1)"
  l6b="$(grep -n '^## 6b' "$RF" | head -1 | cut -d: -f1)"
  l7="$(grep -n '^## 7[.]' "$RF" | head -1 | cut -d: -f1)"
  if [ -z "$l6" ] || [ -z "$l6b" ] || [ -z "$l7" ]; then
    fail "F7  missing one of '## 6.' / '## 6b' / '## 7.' in READY-TO-FIRE (6=$l6 6b=$l6b 7=$l7)"
    f7=1
  elif [ "$l6" -ge "$l6b" ] || [ "$l6b" -ge "$l7" ]; then
    fail "F7  heading order is wrong: '## 6.'=$l6 '## 6b'=$l6b '## 7.'=$l7 (need 6 < 6b < 7)"
    f7=1
  fi
  prev="${l7:-0}"
  for k in 8 9 10 11; do
    lk="$(grep -n "^## ${k}[.]" "$RF" | head -1 | cut -d: -f1)"
    if [ -z "$lk" ]; then
      fail "F7  heading '## ${k}.' is MISSING — items 7-11 must keep their original numbers"
      f7=1
    elif [ "$lk" -le "$prev" ]; then
      fail "F7  heading '## ${k}.' is out of order (line $lk after $prev)"
      f7=1
    else
      prev="$lk"
    fi
  done
  [ $f7 -eq 0 ] && pass "F7  READY-TO-FIRE order is 6 -> 6b -> 7 -> 8 -> 9 -> 10 -> 11 with NO renumbering"

  # -- F8: R3 ceiling numbers in BOTH deferral-vocabulary blocks ------------
  local f8=0 vb tok
  for name in AGENT-PROMPT READY-TO-FIRE; do
    if [ "$name" = "AGENT-PROMPT" ]; then
      vb="$(block "$AP" 'STAGE C HOLD LIFTED' '^STEP 10 ')"
    else
      vb="$(block "$RF" '^[*][*]Deferral vocabulary' '^## 11[.]')"
    fi
    if [ "$(printf '%s\n' "$vb" | grep -c . || true)" -lt 4 ]; then
      fail "F8 [$name] deferral-vocabulary block not found (would be VACUOUS)"
      f8=1; continue
    fi
    for tok in '0.0005' '60.0' '51.2' 'Seth'; do
      has "$vb" "$tok" || { fail "F8 [$name] vocabulary block is missing '$tok'"; f8=1; }
    done
    printf '%s\n' "$vb" | grep -qE '102,?421' || { fail "F8 [$name] vocabulary block is missing 102,421"; f8=1; }
  done
  [ $f8 -eq 0 ] && pass "F8  both deferral-vocabulary blocks carry Seth's R3 ceilings (0.0005 / 60.0 / 51.2 / 102,421)"

  # -- F9: cost relabel at all three sites ----------------------------------
  local f9=0 cb
  for name in AGENT-PROMPT READY-TO-FIRE BROWSER-PASTE; do
    case "$name" in
      AGENT-PROMPT)  cb="$(block "$AP" '^STEP 9 ' 'STAGE C HOLD LIFTED')" ;;
      READY-TO-FIRE) cb="$(block "$RF" '^- [*][*]C —' '^- [*][*]D —')" ;;
      BROWSER-PASTE) cb="$(block "$BP" '^[*][*]Cost-refinement gate' '^[*][*]Stage C')" ;;
    esac
    if [ "$(printf '%s\n' "$cb" | grep -c . || true)" -lt 2 ]; then
      fail "F9 [$name] cost block not found (would be VACUOUS)"
      f9=1; continue
    fi
    printf '%s\n' "$cb" | grep -qiE 'cost[- ]per[- ]bankable[- ]region' \
      || { fail "F9 [$name] cost block does not read cost-per-bankable-region"; f9=1; }
  done
  [ $f9 -eq 0 ] && pass "F9  cost-per-bankable-region appears in AGENT-PROMPT STEP 9, READY-TO-FIRE 11-C and BROWSER-PASTE's cost gate"

  # -- F10: retired framing appears nowhere on the fire surface -------------
  local n1 n2
  n1="$(cat "$AP" "$BP" "$RF" | grep -ci 'nothing scientific is lost' || true)"
  n2="$(cat "$AP" "$BP" "$RF" | grep -ci 'nothing is lost' || true)"
  if [ "$n1" -eq 0 ] && [ "$n2" -eq 0 ]; then
    pass "F10 the retired framing ('nothing scientific is lost' / 'nothing is lost') appears 0 times in the runbooks"
  else
    fail "F10 retired framing present: 'nothing scientific is lost'=$n1 'nothing is lost'=$n2 (both must be 0)"
  fi
}

# ===========================================================================
# SECTION: record
# ===========================================================================
jget() { python3 -c "import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]] if len(sys.argv)<4 else json.load(open(sys.argv[1]))[sys.argv[2]][int(sys.argv[3])])" "$@"; }
basefield() { grep -E "^$1 " "$BASE" 2>/dev/null | head -1 | awk '{print $2}'; }

section_record() {
  echo "--- section: record -----------------------------------------------"

  # -- R1: HANDOFF.json still parses ----------------------------------------
  if python3 -c "import json;json.load(open('$HJ'))" 2>/dev/null; then
    pass "R1  HANDOFF.json is valid JSON"
  else
    fail "R1  HANDOFF.json does NOT parse"
    echo "     (remaining record checks read fields from it and will be unreliable)"
  fi

  # -- R2: the live gate field ----------------------------------------------
  local gate r2=0
  gate="$(python3 -c "import json;print(json.load(open('$HJ'))['gates']['trsx5_posted_body'])" 2>/dev/null || echo '')"
  if [ -z "$gate" ]; then
    fail "R2  gates.trsx5_posted_body is missing/unreadable"
  else
    for tok in "$MD5_ADVISORY" '9,758' '9,907' 'CORRECTED 2026-08-14'; do
      has "$gate" "$tok" || { fail "R2  gates.trsx5_posted_body is missing '$tok'"; r2=1; }
    done
    if has "$gate" "c19e8b2"; then
      fail "R2  gates.trsx5_posted_body STILL carries the invalid prefix c19e8b2"; r2=1
    fi
    [ $r2 -eq 0 ] && pass "R2  gates.trsx5_posted_body is size-first, dated, and free of c19e8b2"
  fi

  # -- R3: status corrected on top, dated body PRESERVED --------------------
  local st
  st="$(python3 -c "import json;print(json.load(open('$HJ'))['status'])" 2>/dev/null || echo '')"
  if [[ "$st" == "⚠ CORRECTED 2026-08-14"* ]] && has "$st" 'SESSION CLOSE 2026-08-14.'; then
    pass "R3  status opens with the dated ⚠ CORRECTED 2026-08-14 clause AND preserves 'SESSION CLOSE 2026-08-14.'"
  else
    fail "R3  status must START with '⚠ CORRECTED 2026-08-14' and still contain 'SESSION CLOSE 2026-08-14.'"
  fi

  # -- R4: resume_on_reconnect[0] byte-unchanged vs the PINNED baseline ------
  local want got
  want="$(basefield handoff_resume0_md5)"
  got="$(python3 -c "import json,hashlib;print(hashlib.md5(json.load(open('$HJ'))['resume_on_reconnect'][0].encode()).hexdigest())" 2>/dev/null || echo 'ERR')"
  if [ -z "$want" ]; then
    fail "R4  baseline file missing or has no handoff_resume0_md5 — the pin is a BELIEF, not a gate ($BASE)"
  elif [ "$want" = "$got" ]; then
    pass "R4  resume_on_reconnect[0] is byte-unchanged vs the committed baseline ($want)"
  else
    fail "R4  resume_on_reconnect[0] CHANGED: baseline=$want now=$got (D4 says do not touch it)"
  fi

  # -- R5: STATE.md frontmatter lines 1-24 byte-identical --------------------
  local fwant fgot
  fwant="$(basefield state_frontmatter_1_24_md5)"
  fgot="$(sed -n '1,24p' "$SM" | md5sum | cut -d' ' -f1)"
  if [ -z "$fwant" ]; then
    fail "R5  baseline file missing state_frontmatter_1_24_md5"
  elif [ "$fwant" = "$fgot" ]; then
    pass "R5  STATE.md lines 1-24 are byte-identical to the pinned baseline ($fwant)"
  else
    fail "R5  STATE.md FRONTMATTER MOVED: baseline=$fwant now=$fgot (lines 1-24 are untouchable)"
  fi

  # -- R6: non-vacuity pair for R5 ------------------------------------------
  # R5's green is evidence ONLY because R6 can fail: the body block must have
  # genuinely changed, and no diff hunk may target a line <= 24.
  local lwant lgot esha r6=0 hunkmin
  lwant="$(basefield state_line34_md5)"
  lgot="$(sed -n '34p' "$SM" | md5sum | cut -d' ' -f1)"
  esha="$(basefield entry_sha)"
  if [ -z "$lwant" ]; then
    fail "R6  baseline file missing state_line34_md5"; r6=1
  elif [ "$lwant" = "$lgot" ]; then
    fail "R6  STATE.md line 34 is UNCHANGED — the trsx5-contest block was not edited, so R5 is vacuous"; r6=1
  fi
  if [ -n "$esha" ]; then
    hunkmin="$(git diff -U0 "$esha" -- .planning/STATE.md 2>/dev/null \
      | grep -oE '^@@ -[0-9]+' | grep -oE '[0-9]+' | sort -n | head -1)"
    if [ -n "$hunkmin" ] && [ "$hunkmin" -le 24 ]; then
      fail "R6  a STATE.md diff hunk targets line $hunkmin (<= 24) — the frontmatter fence was touched"; r6=1
    fi
  else
    fail "R6  baseline file missing entry_sha"; r6=1
  fi
  [ $r6 -eq 0 ] && pass "R6  STATE.md line 34 DID change and no diff hunk targets a line <= 24 (R5 is non-vacuous)"

  # -- R7: STATE.md carries the corrected value + the dated clause ----------
  local r7=0 l34
  grep -qF -- "$MD5_ADVISORY" "$SM" || { fail "R7  STATE.md does not carry $MD5_ADVISORY"; r7=1; }
  grep -qF -- 'CORRECTED 2026-08-14' "$SM" || { fail "R7  STATE.md has no 'CORRECTED 2026-08-14' clause"; r7=1; }
  l34="$(sed -n '34p' "$SM")"
  if has "$l34" 'c19e8b2'; then
    fail "R7  STATE.md line 34 STILL carries the invalid prefix c19e8b2"; r7=1
  fi
  [ $r7 -eq 0 ] && pass "R7  STATE.md carries the corrected advisory value + dated clause; line 34 is free of c19e8b2"

  # -- R8: R4-COVERAGE registered ------------------------------------------
  local r8=0 tok
  for tok in 'R4-COVERAGE' '48.5' '10.5' '--ld-window'; do
    grep -qF -- "$tok" "$DI" || { fail "R8  deferred-items.md is missing '$tok'"; r8=1; }
  done
  local nret nretired
  nret="$(grep -ci 'nothing scientific is lost' "$DI" || true)"
  nretired="$(grep -i 'nothing scientific is lost' "$DI" | grep -c 'RETIRED' || true)"
  if [ "$nret" -eq 0 ]; then
    fail "R8  deferred-items.md never states the retired framing, so nothing retires it"; r8=1
  elif [ "$nret" -ne "$nretired" ]; then
    fail "R8  'nothing scientific is lost' appears on $nret line(s) but only $nretired also say RETIRED"; r8=1
  fi
  [ $r8 -eq 0 ] && pass "R8  R4-COVERAGE registered with 10.5% / 48.5 Mb / --ld-window remedy; retired framing survives only inside its retirement"
}

# ===========================================================================
# SECTION: reply
# ===========================================================================
section_reply() {
  echo "--- section: reply ------------------------------------------------"

  # -- P1: exists and substantive -------------------------------------------
  local n
  if [ ! -f "$REPLY" ]; then
    fail "P1  $REPLY does not exist"
    return
  fi
  n="$(wc -l <"$REPLY" | tr -d ' ')"
  if [ "$n" -ge 60 ]; then pass "P1  REPLY-TO-SETH.md exists and is $n lines (>= 60)"
  else fail "P1  REPLY-TO-SETH.md is only $n lines (need >= 60)"; fi

  # -- P2: answers his four items -------------------------------------------
  local p2=0 tok
  for tok in 'BLOCKING' 'R1' 'R3' 'R4'; do
    grep -qF -- "$tok" "$REPLY" || { fail "P2  reply never mentions '$tok'"; p2=1; }
  done
  [ $p2 -eq 0 ] && pass "P2  reply answers BLOCKING / R1 / R3 / R4"

  # -- P3: the anchor transcript --------------------------------------------
  local p3=0
  for tok in 'PASTE INTO OSF FROM HERE' '9758' "$MD5_CANON" 'ac4c990'; do
    grep -qF -- "$tok" "$REPLY" || { fail "P3  reply is missing transcript marker '$tok'"; p3=1; }
  done
  [ $p3 -eq 0 ] && pass "P3  reply carries the verbatim anchor re-derivation (awk / 9758 / 28ecdb31 / ac4c990)"

  # -- P4: request (a) writes OUT OF REPO -----------------------------------
  local p4=0 nin
  grep -qF -- 'trsx5-canonical-9758' "$REPLY" || { fail "P4  reply never names trsx5-canonical-9758"; p4=1; }
  grep -qF -- '$HOME' "$REPLY" || { fail "P4  reply gives no \$HOME (out-of-repo) output path"; p4=1; }
  nin="$(grep -c 'trsx5-canonical.*\.planning/\|\.planning/.*trsx5-canonical' "$REPLY" || true)"
  if [ "$nin" -ne 0 ]; then
    fail "P4  reply writes the canonical body under .planning/ on $nin line(s) — that is a committed drift surface"; p4=1
  fi
  [ $p4 -eq 0 ] && pass "P4  request (a) produces trsx5-canonical-9758 under \$HOME, never inside .planning/"

  # -- P5: explicit non-possession of the 9,907 body ------------------------
  local p5=0
  grep -qF -- '9,907' "$REPLY" || { fail "P5  reply never states the 9,907 figure"; p5=1; }
  grep -qiE 'do not hold|we do not have|cannot compute' "$REPLY" \
    || { fail "P5  reply has no explicit non-possession sentence for the 9,907 body"; p5=1; }
  [ $p5 -eq 0 ] && pass "P5  reply states plainly that we do not hold the 9,907 body and cannot compute the diff"

  # -- P6: the F1 invariant, one document later -----------------------------
  # NARROW, DELIBERATE EXEMPTION: the courier package must quote the invalid
  # 31-char literal verbatim (that IS the firsthand confirmation Seth asked
  # for), so it is exempt HERE and nowhere else — and only on a line that also
  # carries the count 31, i.e. only where it is presented as the defect rather
  # than as an anchor. Every OTHER off-length run still fails.
  local bad p6=0 nlit nlab
  bad="$(grep -oE '[0-9a-f]{20,}' "$REPLY" | awk -v ok="$BAD31" '{ if ($0 != ok && length($0) != 32 && length($0) != 40) printf "  len=%d  %s\n", length($0), $0 }')"
  if [ -n "$bad" ]; then
    fail "P6  hex run(s) in the reply are neither 32 (md5) nor 40 (SHA-1):"
    printf '%s\n' "$bad"; p6=1
  fi
  nlit="$(grep -cF -- "$BAD31" "$REPLY" || true)"
  nlab="$(grep -F -- "$BAD31" "$REPLY" | grep -c '31' || true)"
  if [ "$nlit" -ne "$nlab" ]; then
    fail "P6  the invalid literal appears on $nlit line(s) but only $nlab present it with its 31-char count"; p6=1
  fi
  [ $p6 -eq 0 ] && pass "P6  every hex run is 32 or 40 chars, except the invalid literal quoted only where labelled 31"

  # -- P7: cost relabel carried to Seth -------------------------------------
  if grep -qiE 'cost[- ]per[- ]bankable[- ]region' "$REPLY"; then
    pass "P7  reply carries the cost-per-bankable-region relabel"
  else
    fail "P7  reply does not carry the cost-per-bankable-region relabel"
  fi

  # -- P8: the ledger stays neutral -----------------------------------------
  if grep -qiE 'un-annotated|stays neutral' "$REPLY"; then
    pass "P8  reply states the trsx5 ledger stays un-annotated/neutral until the download adjudicates"
  else
    fail "P8  reply must state the ledger stays un-annotated (or stays neutral) pending adjudication"
  fi
}

# ===========================================================================
case "${1:-}" in
  fire)   section_fire ;;
  record) section_record ;;
  reply)  section_reply ;;
  all)    section_fire; echo; section_record; echo; section_reply ;;
  *) echo "usage: bash $(basename "$0") {fire|record|reply|all}" >&2; exit 2 ;;
esac

echo
if [ $RC -eq 0 ]; then echo "RESULT: ALL CHECKS PASSED (section: ${1})"; else echo "RESULT: FAILURES PRESENT (section: ${1})"; fi
exit $RC
