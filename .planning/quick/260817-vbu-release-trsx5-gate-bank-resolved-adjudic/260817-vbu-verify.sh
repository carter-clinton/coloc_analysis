#!/usr/bin/env bash
# ============================================================================
# 260817-vbu-verify.sh — the LIVE enforcer for the STEP 6b trsx5 card
#
#   usage:  bash 260817-vbu-verify.sh {card|artifact|all}
#           bash 260817-vbu-verify.sh _card <file> <start_re> <end_re>  # V0-V5
#           bash 260817-vbu-verify.sh _artifact <file>                  # V6
#
#   exit 0 = every check in the requested section PASSED
#   exit 1 = at least one check FAILED
#
# Sections
#   card     — V0-V5 over the §6b card block in all three 260812-ox1 runbooks
#   artifact — V6 (re-hash of the banked 9,695-B body) + V7 (guk supersession note)
#
# ---------------------------------------------------------------------------
# WHY THIS FILE EXISTS, AND WHY V0 COMES FIRST
# ---------------------------------------------------------------------------
# It supersedes the `fire` section of 260814-guk-verify.sh, which encodes the
# retired TWO-BODY card ({9,758, 9,907}, with c19be8b2... as a Seth-reported
# ADVISORY value). That adjudication is RESOLVED as of 2026-08-17
# (DEC-2026-08-17-trsx5-gate-released): the posted 9,695-B body is a byte-exact
# plain-text rendering of the COMPLETE 9,907-B lineage, and c19be8b2... is now a
# VERIFIED anchor measured independently on both sides. A red `fire` section
# against the NEW card is therefore EXPECTED and is NOT a defect.
#
# V0 IS FIRST ON PURPOSE. Every other check here reads a block extracted by a
# heading regex. If a heading is renamed, the extractor returns an EMPTY block,
# and an empty block satisfies every content assertion below it TRIVIALLY — the
# card Carter reads before a $385-1,084 irreversible spend could be deleted
# outright and this file would go green. That silent-vacuity class is exactly
# what this file exists to catch, so a short or empty block is a FAIL, checked
# BEFORE anything else.
#
# A GREEN HERE IS EVIDENCE ONLY BECAUSE THE CONTROLS WERE SEEN RED. Each check
# was driven to failure through the SHIPPED `_card` / `_artifact` sub-modes —
# never a re-implementation — and the verbatim red output is recorded in
# 260817-vbu-controls-transcript.txt (NC-0 green differential, NC-1 V3 len=31,
# NC-2 V1 hash-first, NC-3 V4, NC-4 V0 vacuity, NC-5 V6 digest-at-same-size).
# Before trusting a green from this file, read that transcript.
#
# ⛔ FORBIDDEN REPAIR (inherited from guk, restated because it still binds):
# never truncate a sha256 to satisfy a digest check. The invariant is {32, 64}.
# Widen the invariant; never shorten the anchor.
# ============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$ROOT" || exit 2

OX1="$ROOT/.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r"
AP="$OX1/260812-ox1-AGENT-PROMPT.md"
BP="$OX1/260812-ox1-BROWSER-PASTE.md"
RF="$OX1/260812-ox1-READY-TO-FIRE.md"
GUK="$ROOT/.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh"
BODY="$HERE/260817-vbu-trsx5-posted-9695-reconstructed.txt"

# --- the adjudicated anchors (2026-08-17) -----------------------------------
MD5_POSTED="c19be8b2ad7cd6a45fee1d668d8a9cf9"                                     # 32
SHA_POSTED="1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4"     # 64
SIZE_POSTED="9695"

RC=0
pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; RC=1; }

# block FILE START_RE END_RE -> prints [START_RE line .. line before END_RE]
# (byte-identical to guk's extractor; the card regexes are reused verbatim)
block() {
  awk -v s="$2" -v e="$3" 'BEGIN{p=0} (p && $0 ~ e){exit} ($0 ~ s){p=1} p{print}' "$1"
}

# hexlen_bad : stdin -> one line per hex run (>=20 chars) that is neither 32 nor 64
hexlen_bad() {
  grep -oE '[0-9a-f]{20,}' | awk '{ if (length($0) != 32 && length($0) != 64) printf "  len=%d  %s\n", length($0), $0 }'
}

has() { grep -qF -- "$2" <<<"$1"; }

# ===========================================================================
# card_checks NAME BLOCK  ->  V0 .. V5 against one extracted card block
# ===========================================================================
card_checks() {
  local name="$1" blk="$2"
  local nlines bad lsize lhash v

  # -- V0: NON-VACUITY, FIRST ------------------------------------------------
  nlines="$(printf '%s\n' "$blk" | grep -c . || true)"
  if [ "$nlines" -lt 8 ]; then
    fail "V0 [$name] card block has $nlines non-empty line(s) (need >= 8) — heading not found or card gutted; every check below would be VACUOUS"
    return
  fi
  pass "V0 [$name] card block is non-vacuous ($nlines non-empty lines)"

  # -- V1: SIZE-FIRST ORDERING ----------------------------------------------
  lsize="$(printf '%s\n' "$blk" | grep -nE '9,?695' | head -1 | cut -d: -f1)"
  lhash="$(printf '%s\n' "$blk" | grep -nF -- "$MD5_POSTED" | head -1 | cut -d: -f1)"
  if [ -z "$lsize" ] || [ -z "$lhash" ]; then
    fail "V1 [$name] card block lacks a 9,695 mention (line='${lsize:-none}') or the posted md5 (line='${lhash:-none}')"
  elif [ "$lsize" -ge "$lhash" ]; then
    fail "V1 [$name] card is HASH-FIRST: 9,695 first appears on block line $lsize, $MD5_POSTED on $lhash (need strictly before)"
  else
    pass "V1 [$name] adjudicates SIZE-FIRST (9,695 on block line $lsize precedes the md5 on $lhash)"
  fi

  # -- V2: both verified digests present ------------------------------------
  v=0
  has "$blk" "$MD5_POSTED" || { fail "V2 [$name] card block is missing the md5 $MD5_POSTED"; v=1; }
  has "$blk" "$SHA_POSTED" || { fail "V2 [$name] card block is missing the sha256 $SHA_POSTED"; v=1; }
  [ $v -eq 0 ] && pass "V2 [$name] card block carries BOTH verified digests (md5 32-char + sha256 64-char)"

  # -- V3: hex-run length invariant {32, 64} --------------------------------
  bad="$(printf '%s\n' "$blk" | hexlen_bad)"
  if [ -n "$bad" ]; then
    fail "V3 [$name] hex run(s) in the card block are neither 32 (md5) nor 64 (sha256):"
    printf '%s\n' "$bad"
  else
    pass "V3 [$name] every hex run >=20 chars in the card block is 32 (md5) or 64 (sha256)"
  fi

  # -- V4: the dated adjudication + the decision id -------------------------
  v=0
  has "$blk" 'ADJUDICATED-RESOLVED 2026-08-17' \
    || { fail "V4 [$name] card block is missing the dated string 'ADJUDICATED-RESOLVED 2026-08-17'"; v=1; }
  has "$blk" 'DEC-2026-08-17-trsx5-gate-released' \
    || { fail "V4 [$name] card block is missing the decision id 'DEC-2026-08-17-trsx5-gate-released'"; v=1; }
  [ $v -eq 0 ] && pass "V4 [$name] card block carries ADJUDICATED-RESOLVED 2026-08-17 + the decision id"

  # -- V5: supersession legibility ------------------------------------------
  # The historical anchors must NOT be deleted (a reader must be able to see why
  # 9,758 / 9,907 used to be a pass), and they must be visibly labelled so they
  # cannot be mistaken for live pass values.
  v=0
  has "$blk" '9,758' || { fail "V5 [$name] historical anchor 9,758 was DELETED from the card block"; v=1; }
  has "$blk" '9,907' || { fail "V5 [$name] historical anchor 9,907 was DELETED from the card block"; v=1; }
  printf '%s\n' "$blk" | grep -qi 'SUPERSEDED' \
    || { fail "V5 [$name] card block never says SUPERSEDED — 9,758/9,907 could be read as live pass values"; v=1; }
  [ $v -eq 0 ] && pass "V5 [$name] historical anchors 9,758 / 9,907 retained AND labelled SUPERSEDED"
}

# ===========================================================================
# artifact_checks FILE  ->  V6 (size + both digests)
# ===========================================================================
artifact_checks() {
  local f="$1" n m s v=0
  if [ ! -f "$f" ]; then
    fail "V6 banked body $f does NOT exist"
    return
  fi
  n="$(wc -c <"$f" | tr -d ' ')"
  m="$(md5sum "$f" | cut -d' ' -f1)"
  s="$(sha256sum "$f" | cut -d' ' -f1)"
  [ "$n" = "$SIZE_POSTED" ] || { fail "V6 size MISMATCH: $n bytes (want $SIZE_POSTED)"; v=1; }
  [ "$m" = "$MD5_POSTED" ]  || { fail "V6 md5 MISMATCH: $m (want $MD5_POSTED)"; v=1; }
  [ "$s" = "$SHA_POSTED" ]  || { fail "V6 sha256 MISMATCH: $s (want $SHA_POSTED)"; v=1; }
  [ $v -eq 0 ] && pass "V6 banked body re-hashes to the adjudicated anchors: $n B / $m / $s"
}

# ===========================================================================
# sub-modes — the negative controls drive THESE, not a re-implementation
# ===========================================================================
if [ "${1:-}" = "_card" ]; then
  f="${2:?_card needs <file>}"; sre="${3:?_card needs <start_re>}"; ere="${4:?_card needs <end_re>}"
  [ -f "$f" ] || { echo "FAIL  _card: $f missing"; exit 1; }
  card_checks "$(basename "$f")" "$(block "$f" "$sre" "$ere")"
  echo
  if [ $RC -eq 0 ]; then echo "RESULT: ALL CHECKS PASSED (_card $f)"; else echo "RESULT: FAILURES PRESENT (_card $f)"; fi
  exit $RC
fi

if [ "${1:-}" = "_artifact" ]; then
  artifact_checks "${2:?_artifact needs <file>}"
  echo
  if [ $RC -eq 0 ]; then echo "RESULT: ALL CHECKS PASSED (_artifact)"; else echo "RESULT: FAILURES PRESENT (_artifact)"; fi
  exit $RC
fi

# ===========================================================================
section_card() {
  echo "--- section: card (V0-V5 x 3 runbook copies) ----------------------"
  # extraction regexes reused VERBATIM from 260814-guk-verify.sh section_fire
  card_checks AGENT-PROMPT  "$(block "$AP" '^STEP 6b' '^STEP 7')"
  card_checks BROWSER-PASTE "$(block "$BP" '^## 6b'   '^## 7')"
  card_checks READY-TO-FIRE "$(block "$RF" '^## 6b'   '^## 7[.]')"
}

section_artifact() {
  echo "--- section: artifact (V6-V7) -------------------------------------"

  # -- V6: re-hash the banked reconstruction --------------------------------
  artifact_checks "$BODY"

  # -- V7: the superseded enforcer says so, with a date and a successor -----
  local v=0
  if [ ! -f "$GUK" ]; then
    fail "V7 the superseded enforcer $GUK is missing"
  else
    grep -qF -- 'SUPERSEDED 2026-08-17' "$GUK" \
      || { fail "V7 260814-guk-verify.sh header carries no dated 'SUPERSEDED 2026-08-17' note"; v=1; }
    grep -qF -- '260817-vbu-verify.sh' "$GUK" \
      || { fail "V7 260814-guk-verify.sh does not name its successor 260817-vbu-verify.sh"; v=1; }
    [ $v -eq 0 ] && pass "V7 260814-guk-verify.sh carries the dated supersession note naming 260817-vbu-verify.sh"
  fi
}

case "${1:-}" in
  card)     section_card ;;
  artifact) section_artifact ;;
  all)      section_card; echo; section_artifact ;;
  *) echo "usage: bash $(basename "$0") {card|artifact|all}" >&2
     echo "       bash $(basename "$0") _card <file> <start_re> <end_re>" >&2
     echo "       bash $(basename "$0") _artifact <file>" >&2
     exit 2 ;;
esac

echo
if [ $RC -eq 0 ]; then echo "RESULT: ALL CHECKS PASSED (section: ${1})"; else echo "RESULT: FAILURES PRESENT (section: ${1})"; fi
exit $RC
