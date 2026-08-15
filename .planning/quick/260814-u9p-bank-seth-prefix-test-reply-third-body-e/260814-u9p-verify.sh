#!/usr/bin/env bash
# ============================================================================
# 260814-u9p-verify.sh — re-runnable checker for quick task 260814-u9p
#
#   usage:  bash 260814-u9p-verify.sh {controls|ledger|reply|all}
#
#   exit 0 = every check in the requested section PASSED
#   exit 1 = at least one check FAILED
#
#   COST / BLAST RADIUS: $0. This script is READ-ONLY against the repo. It makes
#   NO NETWORK CALLS, contacts NO OSF endpoint, touches NO perimeter (no AoU, no
#   GCS, no gcloud), fires nothing, and pushes nothing. Its only writes are to a
#   private `mktemp -d` scratch directory that is removed on exit.
#
# Sections
#   controls — the hex-run invariant widening in 260814-guk-verify.sh: negative
#              controls at 31/63 (RED) and 32/64 (GREEN) driven through the
#              SHIPPED `_hexlen` sub-mode, plus a structural guard against a
#              silent revert, plus the guk `fire` gate at 10/10.
#   ledger   — the RECHARACTERIZED 2026-08-14 sub-entry in .planning/osf_deviations.md
#              (append-only vs 50dc51d, content, and preservation of the reading
#              it falsifies).
#   reply    — the courier-in verbatim record (byte-exact) and the reply to Seth.
#
# ---------------------------------------------------------------------------
# WHY THE CONTROLS RUN THE GUK SCRIPT INSTEAD OF RE-IMPLEMENTING ITS LOGIC
# ---------------------------------------------------------------------------
# The widening this task performs is a LOOSENING of a safety invariant that
# guards a card read before a $385-1,084 irreversible spend. A loosening is only
# safe if you have SEEN what it still rejects. So the controls invoke
# `260814-guk-verify.sh _hexlen` — the real shipped code path — rather than a
# local copy of the same awk. A copy would go green even if the shipped function
# were reverted, silently, tomorrow. The structural check (C6) exists for the
# same reason from the other direction: it reads the shipped function's own
# length condition and fails if either 32 or 64 disappears from it.
#
# Observed before this script existed, against the UNMODIFIED guk script:
#   _hexlen(len64.txt) -> FAIL, "len=64 deadbeef..."  (exit 1)
# That RED is why the 64-char GREEN below is evidence and not an assertion.
# ============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$ROOT" || exit 2

GUK="$ROOT/.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh"
OSF_REL=".planning/osf_deviations.md"
OSF="$ROOT/$OSF_REL"
VERB_REL=".planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-SETH-REPLY-VERBATIM.md"
VERB="$ROOT/$VERB_REL"
REPLY="$HERE/260814-u9p-REPLY-TO-SETH.md"

# --- transcribed hashes (HASH TABLE, quick-260814-u9p PLAN). Never re-derived. --
H1="c19be8b2ad7cd6a45fee1d668d8a9cf9"   # posted trsx5 body, 9,695 B (Carter's download)
H2="425d925a88ab474ec2396cbea25e665c"   # Seth's complete lineage, 9,907 B (we do NOT hold the body)
H3="a81c22d95e7b83488c015357445f3482"   # head -c 9695 of SETH's body  -> != H1  (ask-#1 = NO)
H4="6b75e660e52413e4cbec116f315590b6"   # head -c 9695 of OUR canonical -> != H1  (tgf, negative)
H5="28ecdb3160833da80cfa25952f76415b"   # repo-canonical paste block, 9,758 B @ ac4c990
H6="c19e8b2ad7cd6a45fee1d668d8a9cf9"    # the historical 31-CHAR DEFECT literal
X1="40831cdebcc71de21cd536fa"           # ⚠ DISPLAY-TRUNCATED sha256 (24 chars). NOT AN ANCHOR.
                                        #   Never pad it, never complete it, never verify with it.
VERB_MD5="47a017bf8753b147f498dea97cc64338"   # courier-in pin: 5,763 B / 62 lines
PIN="50dc51d"                                 # ledger append-only baseline (ADJUDICATED sub-entry)

ADJ_HEAD="### ADJUDICATED 2026-08-14"
REC_HEAD="### RECHARACTERIZED 2026-08-14"

RC=0
pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; RC=1; }

TMPD="$(mktemp -d)" || { echo "FATAL: cannot create scratch dir" >&2; exit 2; }
trap 'rm -rf "$TMPD"' EXIT

# block FILE HEADING -> [HEADING line .. line before the next '### ' or '---']
mdblock() {
  awk -v h="$2" '
    index($0, h) == 1 && !p { p=1; print; next }
    p && (/^### / || /^---[[:space:]]*$/) { exit }
    p { print }
  ' "$1"
}

# ===========================================================================
# SECTION: controls
# ===========================================================================
section_controls() {
  echo "--- section: controls ---------------------------------------------"

  if [ ! -f "$GUK" ]; then
    fail "C0  the guk verifier is missing: $GUK"
    return
  fi

  # -- C1: control PREMISE. A wrong-length control would make every result -----
  # below meaningless, so a premise failure is a FAIL, never a skip.
  local s64 s63 s32 s31 c1=0 pair want s
  s64="$(printf 'deadbeef%.0s' $(seq 1 8))"   # synthetic, obviously not a real anchor
  s63="${s64%?}"
  s32="$H5"                                    # a real md5 (32)
  s31="$H6"                                    # the historical 31-char defect
  for pair in "64:$s64" "63:$s63" "32:$s32" "31:$s31"; do
    want="${pair%%:*}"; s="${pair#*:}"
    if [ "${#s}" != "$want" ]; then
      fail "C1  CONTROL PREMISE WRONG: expected length $want, got ${#s} — the controls below cannot be trusted"
      c1=1
    fi
  done
  if [ $c1 -ne 0 ]; then return; fi
  pass "C1  control premise holds: the four control strings are exactly 64 / 63 / 32 / 31 chars"

  # -- C2: materialize the controls (one hex run per file) --------------------
  # The comment line carries no hex run >= 20 chars, so each file tests exactly
  # one length and nothing else.
  for pair in "64:$s64" "63:$s63" "32:$s32" "31:$s31"; do
    want="${pair%%:*}"; s="${pair#*:}"
    { echo "# synthetic control - not an anchor"; echo "$s"; } > "$TMPD/len${want}.txt"
  done
  pass "C2  four single-run control files written to a private scratch dir (removed on exit)"

  # -- C3/C4: the four controls, through the SHIPPED _hexlen sub-mode ---------
  local L expect out ec c34=0
  for L in 31 63 32 64; do
    case "$L" in
      31|63) expect=1 ;;   # RED  — off-length runs must still be rejected
      32|64) expect=0 ;;   # GREEN — md5 and sha256 are both legitimate
    esac
    out="$(bash "$GUK" _hexlen "$TMPD/len${L}.txt" 2>&1)"; ec=$?
    if [ "$ec" -ne "$expect" ]; then
      fail "C3  control len=$L returned exit $ec, expected $expect ($( [ "$expect" = 1 ] && echo RED || echo GREEN ))"
      printf '      %s\n' "$out"
      c34=1
    fi
  done
  if [ $c34 -eq 0 ]; then
    pass "C3  negative controls hold: 31 RED, 63 RED (off-length runs still rejected)"
    pass "C4  positive controls hold: 32 GREEN (md5), 64 GREEN (sha256) — the widening is real"
  fi

  # -- C5: the fire gate is unregressed --------------------------------------
  local fout fec
  fout="$(bash "$GUK" fire 2>&1)"; fec=$?
  if [ "$fec" -eq 0 ] && grep -qF 'ALL CHECKS PASSED' <<<"$fout"; then
    pass "C5  guk 'fire' section is unregressed by the widening (exit 0, ALL CHECKS PASSED)"
  else
    fail "C5  guk 'fire' section REGRESSED (exit $fec) — the fire card gate must stay green:"
    printf '%s\n' "$fout" | sed 's/^/      /'
  fi

  # -- C6: structural guard against a silent revert --------------------------
  # C3/C4 would go green again if someone narrowed the function back to {32}
  # ONLY if they also deleted this task's controls. C6 reads the shipped
  # function's own length condition, so a revert goes red structurally too.
  local hb
  hb="$(awk '/^hexlen_bad\(\)[[:space:]]*\{/{p=1} p{print} p&&/^\}/{exit}' "$GUK")"
  if [ "$(printf '%s\n' "$hb" | grep -c . || true)" -lt 2 ]; then
    fail "C6  hexlen_bad() not found in $GUK — the structural check would be VACUOUS"
  elif printf '%s\n' "$hb" | grep -qF 'length($0) != 32' \
       && printf '%s\n' "$hb" | grep -qF 'length($0) != 64'; then
    pass "C6  hexlen_bad()'s length condition names BOTH 32 and 64 (a silent revert goes red here)"
  else
    fail "C6  hexlen_bad()'s length condition no longer names both 32 and 64 — widening reverted?"
    printf '%s\n' "$hb" | sed 's/^/      /'
  fi
}

# ===========================================================================
# SECTION: ledger
# ===========================================================================
section_ledger() {
  echo "--- section: ledger -----------------------------------------------"

  if [ ! -f "$OSF" ]; then
    fail "L0  $OSF_REL does not exist"
    return
  fi

  # -- L1: APPEND-ONLY vs the pin. The load-bearing check. -------------------
  # .planning/osf_deviations.md is reviewer-facing: a DELETED line here is a
  # disclosure defect, including deletion of the reading this task falsifies.
  # If the pin cannot be resolved the guarantee cannot be evaluated — that is a
  # LOUD FAIL, never a silent pass.
  local ns dels
  if ! git cat-file -e "${PIN}^{commit}" 2>/dev/null; then
    fail "L1  the pin $PIN cannot be resolved in this repo — the APPEND-ONLY guarantee CANNOT BE EVALUATED"
  else
    ns="$(git diff --numstat "$PIN" -- "$OSF_REL" 2>/dev/null)"
    if [ -z "$ns" ]; then
      dels=0
    else
      dels="$(printf '%s\n' "$ns" | awk 'NR==1{print $2}')"
    fi
    if [ "$dels" = "0" ]; then
      pass "L1  APPEND-ONLY holds: 0 deleted lines in $OSF_REL vs $PIN"
    else
      fail "L1  $dels line(s) DELETED from $OSF_REL vs $PIN — this entry must be a pure append"
      printf '      %s\n' "$ns"
    fi
  fi

  # -- L2: the new heading exists and sits AFTER the ADJUDICATED heading ------
  local ladj lrec
  ladj="$(grep -nF -- "$ADJ_HEAD" "$OSF" | head -1 | cut -d: -f1)"
  lrec="$(grep -nF -- "$REC_HEAD" "$OSF" | head -1 | cut -d: -f1)"
  if [ -z "$lrec" ]; then
    fail "L2  no '$REC_HEAD' heading found in $OSF_REL"
  elif [ -z "$ladj" ]; then
    fail "L2  no '$ADJ_HEAD' heading found — adjacency cannot be established"
  elif [ "$lrec" -le "$ladj" ]; then
    fail "L2  RECHARACTERIZED (line $lrec) does not follow ADJUDICATED (line $ladj)"
  else
    pass "L2  RECHARACTERIZED 2026-08-14 heading is present (line $lrec) and follows ADJUDICATED (line $ladj)"
  fi

  # -- L3: NON-VACUITY. An empty block passes every content check trivially. ---
  local blk nblk
  blk="$(mdblock "$OSF" "$REC_HEAD")"
  nblk="$(printf '%s\n' "$blk" | grep -c . || true)"
  if [ "$nblk" -lt 25 ]; then
    fail "L3  the RECHARACTERIZED block is only $nblk non-blank lines (need >= 25) — content checks would be VACUOUS"
    return
  fi
  pass "L3  the RECHARACTERIZED block is substantive ($nblk non-blank lines, >= 25)"

  # -- L4: every hash present and every hex run legitimate --------------------
  local l4=0 h
  for h in "$H1" "$H2" "$H3" "$H4" "$H5"; do
    grep -qF -- "$h" <<<"$blk" || { fail "L4  the block is missing the md5 literal $h"; l4=1; }
  done
  printf '%s\n' "$blk" > "$TMPD/ledger_block.txt"
  if ! bash "$GUK" _hexlen "$TMPD/ledger_block.txt" >"$TMPD/l4.out" 2>&1; then
    fail "L4  hex-run length invariant FAILED on the RECHARACTERIZED block:"
    sed 's/^/      /' "$TMPD/l4.out"
    l4=1
  fi
  [ $l4 -eq 0 ] && pass "L4  the block carries H1-H5 in full and every hex run >=20 chars in it is 32 or 64"

  # -- L5: the findings are actually stated -----------------------------------
  local l5=0 tok
  for tok in 'UNEXPLAINED THIRD BODY' 'FALSIFIED' 'RECOMMENDATION' 'NEW OSF VERSION'; do
    grep -qiF -- "$tok" <<<"$blk" || { fail "L5  the block never says '$tok'"; l5=1; }
  done
  for tok in '9,600' '9,919' '9,912' '5fd58a5' '0f3c68b' '212'; do
    grep -qF -- "$tok" <<<"$blk" || { fail "L5  the block is missing the sweep token '$tok'"; l5=1; }
  done
  [ $l5 -eq 0 ] && pass "L5  the block states the third-body finding, the falsification, the recommendation label, the new-OSF-version rule, and Seth's sweep numbers"

  # -- L6: the STOP verdict is explicitly UNCHANGED ---------------------------
  if grep -qiE 'stands? UNCHANGED|verdict.*unchanged' <<<"$blk"; then
    pass "L6  the block states the STOP verdict of the ADJUDICATED sub-entry stands unchanged"
  else
    fail "L6  the block does not state that the STOP verdict is unchanged (a recharacterization is not a reversal)"
  fi

  # -- L7: PRESERVATION. The falsified reading must survive verbatim. ---------
  # Project norm: preserve, date, supersede — never rewrite history. A
  # recharacterization that quietly deleted the thing it falsifies would be the
  # worst version of this entry.
  local adjblk
  adjblk="$(mdblock "$OSF" "$ADJ_HEAD")"
  if grep -qF -- "most plausibly belongs to Seth's" <<<"$adjblk"; then
    pass "L7  the falsified reading (\"most plausibly belongs to Seth's\") is PRESERVED in the ADJUDICATED block above"
  else
    fail "L7  the ADJUDICATED block no longer carries \"most plausibly belongs to Seth's\" — history was rewritten, not appended to"
  fi

  # -- L8: the truncated sha256 stays OUT of the public-facing ledger ---------
  # X1 is a 24-char display truncation with zero verification value. In a
  # reviewer-facing record it can only ever be mistaken for an anchor.
  local nx
  nx="$(grep -cF -- "$X1" "$OSF" || true)"
  if [ "$nx" -eq 0 ]; then
    pass "L8  the display-truncated sha256 ($X1...) appears 0 times in $OSF_REL"
  else
    fail "L8  the display-truncated sha256 appears on $nx line(s) of $OSF_REL — it is not an anchor and does not belong in the ledger"
  fi
}

# ===========================================================================
# SECTION: reply
# ===========================================================================
section_reply() {
  echo "--- section: reply ------------------------------------------------"

  # -- V1: BYTE-EXACT courier-in, worktree AND object store -------------------
  local v1=0 wt_md5 ob_md5 dstat
  if [ ! -f "$VERB" ]; then
    fail "V1  the courier-in record is missing: $VERB_REL"
    v1=1
  else
    wt_md5="$(md5sum "$VERB" | cut -d' ' -f1)"
    [ "$wt_md5" = "$VERB_MD5" ] || { fail "V1  worktree copy md5=$wt_md5, expected $VERB_MD5 — the verbatim record was EDITED"; v1=1; }
    if git cat-file -e "HEAD:$VERB_REL" 2>/dev/null; then
      ob_md5="$(git show "HEAD:$VERB_REL" 2>/dev/null | md5sum | cut -d' ' -f1)"
      [ "$ob_md5" = "$VERB_MD5" ] || { fail "V1  object-store copy at HEAD md5=$ob_md5, expected $VERB_MD5"; v1=1; }
    else
      fail "V1  $VERB_REL is not committed at HEAD — byte-exactness cannot be proved from the object store"
      v1=1
    fi
    dstat="$(git diff HEAD --stat -- "$VERB_REL" 2>/dev/null)"
    [ -z "$dstat" ] || { fail "V1  worktree differs from HEAD for the verbatim record: $dstat"; v1=1; }
  fi
  [ $v1 -eq 0 ] && pass "V1  courier-in is byte-exact: md5 $VERB_MD5 in the worktree AND from the git object store at HEAD"

  # -- V2: the verbatim fences survive ---------------------------------------
  # ⚠ NO HEX-LENGTH INVARIANT IS RUN OVER THIS FILE, DELIBERATELY. It contains
  # two 24-character hex runs (Seth's own display-truncated sha256). Those are
  # CORRECT: the file is a faithful transcript of what he wrote, and a courier-in
  # record that has been "repaired" is no longer a courier-in record. Anyone who
  # sees those 24-char runs and reaches for a fix is about to destroy evidence.
  local v2=0
  if [ -f "$VERB" ]; then
    grep -qF -- '--- VERBATIM BODY BEGINS ---' "$VERB" || { fail "V2  the courier-in record lost its BEGINS fence"; v2=1; }
    grep -qF -- '--- VERBATIM BODY ENDS ---'   "$VERB" || { fail "V2  the courier-in record lost its ENDS fence"; v2=1; }
    [ $v2 -eq 0 ] && pass "V2  the courier-in record still carries both verbatim fences (no hexlen check is run over it, by design)"
  else
    fail "V2  the courier-in record is missing"
  fi

  # -- V3: the reply exists and is substantive --------------------------------
  if [ ! -f "$REPLY" ]; then
    fail "V3  $(basename "$REPLY") does not exist"
    return
  fi
  local n
  n="$(wc -l <"$REPLY" | tr -d ' ')"
  if [ "$n" -ge 60 ]; then pass "V3  REPLY-TO-SETH.md exists and is $n lines (>= 60)"
  else fail "V3  REPLY-TO-SETH.md is only $n lines (need >= 60)"; fi

  # -- V4: coverage of (a)-(e) ------------------------------------------------
  local v4=0 tok
  for tok in 'NEVER ARRIVED' 'seth_courier_9907_body_for_hpc.md' 're-send' '64-char' \
             'WIDENED' '{32, 64}' 'unexplained third body' 'HELD' 'new OSF version' \
             'size-first' '9,695' '9,907' '149' '212' 'FALSIFIED' 'RECOMMENDATION'; do
    grep -qiF -- "$tok" "$REPLY" || { fail "V4  the reply never says '$tok'"; v4=1; }
  done
  for tok in 31 63 32 64; do
    grep -qE "(^|[^0-9])${tok}([^0-9]|$)" "$REPLY" || { fail "V4  the reply never reports control length $tok"; v4=1; }
  done
  [ $v4 -eq 0 ] && pass "V4  the reply covers (a) courier never arrived + re-send, (b) the widening and its controls, (c) sequencing, (d) what is held, (e) the falsification"

  # -- V5: hex invariant, with ONE narrow and LABELLED exemption --------------
  # The truncated sha256 may appear only where it is presented as unusable: on a
  # line that also carries the ellipsis AND a truncation warning. Anywhere else
  # it reads as an anchor, which is exactly the silent-mismatch class we are
  # trying to avoid manufacturing.
  local bad v5=0 nlit nlab
  bad="$(grep -oE '[0-9a-f]{20,}' "$REPLY" \
        | awk -v ok="$X1" '{ if ($0 != ok && length($0) != 32 && length($0) != 64) printf "  len=%d  %s\n", length($0), $0 }')"
  if [ -n "$bad" ]; then
    fail "V5  hex run(s) in the reply are neither 32 (md5) nor 64 (sha256), and are not the labelled truncation:"
    printf '%s\n' "$bad"; v5=1
  fi
  nlit="$(grep -cF -- "$X1" "$REPLY" || true)"
  nlab="$(grep -F -- "$X1" "$REPLY" | grep -F '…' | grep -cE 'TRUNCATED|truncated' || true)"
  if [ "$nlit" -ne "$nlab" ]; then
    fail "V5  the truncated sha256 appears on $nlit line(s) but only $nlab carry BOTH the ellipsis and a truncation warning"
    v5=1
  fi
  [ $v5 -eq 0 ] && pass "V5  every hex run in the reply is 32 or 64, except the truncated sha256 on $nlit line(s), each carrying its ellipsis + truncation warning"

  # -- V6: SCOPED STRICTNESS — no 64-char run may appear in THIS document -----
  # We hold no legitimate sha256 to transcribe here (the only one offered to us
  # arrived truncated). So a 64-char run in this reply could only have been
  # invented or padded, and V6 forbids it outright even though V5 would allow a
  # real one. The 32-char count must be > 0 so V6 cannot pass on an empty file.
  local n64 n32
  n64="$(grep -oE '[0-9a-f]{20,}' "$REPLY" | awk 'length($0)==64' | wc -l | tr -d ' ')"
  n32="$(grep -oE '[0-9a-f]{20,}' "$REPLY" | awk 'length($0)==32' | wc -l | tr -d ' ')"
  if [ "$n64" -eq 0 ] && [ "$n32" -gt 0 ]; then
    pass "V6  the reply carries $n32 md5 run(s) and ZERO 64-char runs (no padded or invented sha256 could have slipped in)"
  else
    fail "V6  expected 0 sha256-length runs and >0 md5 runs in the reply; got 64-char=$n64, 32-char=$n32"
  fi

  # -- V7: all five transcribed hashes are present in full --------------------
  local v7=0 h
  for h in "$H1" "$H2" "$H3" "$H4" "$H5"; do
    grep -qF -- "$h" "$REPLY" || { fail "V7  the reply is missing the md5 literal $h"; v7=1; }
  done
  [ $v7 -eq 0 ] && pass "V7  all five hashes (H1-H5) appear in full in the reply"

  # -- V8: the 31-char defect literal has no business in THIS document --------
  # The guk reply quoted it deliberately (it was the firsthand confirmation Seth
  # asked for). This one has no such reason, so its count must be 0.
  local n31
  n31="$(grep -cF -- "$H6" "$REPLY" || true)"
  if [ "$n31" -eq 0 ]; then
    pass "V8  the 31-char defect literal appears 0 times in the reply (it has no role in this document)"
  else
    fail "V8  the 31-char defect literal appears on $n31 line(s) of the reply — remove it"
  fi
}

# ===========================================================================
case "${1:-}" in
  controls) section_controls ;;
  ledger)   section_ledger ;;
  reply)    section_reply ;;
  all)      section_controls; echo; section_ledger; echo; section_reply ;;
  *) echo "usage: bash $(basename "$0") {controls|ledger|reply|all}" >&2; exit 2 ;;
esac

echo
if [ $RC -eq 0 ]; then echo "RESULT: ALL CHECKS PASSED (section: ${1})"; else echo "RESULT: FAILURES PRESENT (section: ${1})"; fi
exit $RC
