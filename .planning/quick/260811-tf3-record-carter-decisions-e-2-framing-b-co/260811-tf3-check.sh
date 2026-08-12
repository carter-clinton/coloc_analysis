#!/usr/bin/env bash
# 260811-tf3-check.sh
#
# Acceptance harness for quick task 260811-tf3 -- recording Carter's two
# 2026-08-11 decisions (E-2 framing = B/CORRECTION; SR4-OPEN = NEVER ACTUALLY
# FROZEN) onto the three surfaces the resume path actually reads.
#
#   ./260811-tf3-check.sh [--only dec|handoff|pair] [--self-test [dec|handoff|pair]]
#
# Exit 0 = every clause in the selected group(s) passed. Non-zero = at least one
# clause failed, or a required file is absent (absence is a LOUD FAILURE, never
# a skip), or the baseline guard tripped.
#
# ---------------------------------------------------------------------------
# WHY THIS FILE EXISTS AT ALL
#
# Green is evidence ONLY if you have seen it fail
# ([[feedback_green_assertion_needs_a_negative_control]]). Every clause group
# below is written and OBSERVED RED before its edit lands, and every group ships
# fixture-based negative controls under --self-test. Two of those controls
# (NC-D3, NC-P2) must fire on their named clause ALONE: a control that reddens
# three clauses proves nothing about the one it names.
#
# ⚠ FIXTURES ARE COPIES. No control ever mutates .planning/DECISIONS.md,
# .planning/HANDOFF.json or deferred-items.md. The JSON parse gate in particular
# is proven red on a deliberately broken COPY -- never on the real resume file.
#
# ---------------------------------------------------------------------------
# GREP DIALECT. This script runs under its own shebang, so `grep` resolves to
# /usr/bin/grep (GNU grep 3.6 on this node -- the same measurement recorded in
# 260811-oku-check-drafts.sh, which corrected an earlier "ugrep" provenance
# claim that came from an interactive shell wrapper rather than the script
# interpreter). Do not propagate the ugrep claim.
#
# ⚠ LINE SCOPING. grep is line-oriented. Prose in DECISIONS.md is hard-wrapped,
# so a required multi-word phrase can straddle a newline. Content-presence
# clauses (DEC-04..DEC-08, SP-04..SP-08) are therefore asserted against a
# ONE-LINE FOLD of the region under test, and each such clause says so in its
# comment. Structural clauses that must see real lines (DEC-01/02/03/09,
# HJ-05..HJ-08, SP-01/02/03) are asserted line-scoped.
#
# ⚠ THE FOLD ALSO SQUEEZES WHITESPACE RUNS, and that is load-bearing rather than
# cosmetic. `tr '\n' ' '` alone is NOT enough: a phrase wrapped as
#   "a **negative\n  control** OBSERVED red"
# folds to "**negative   control**" -- three spaces -- and a clause searching for
# "negative control" silently never matches. That is a clause structurally
# incapable of its stated job, which is the failure class this project has been
# bitten by repeatedly. Measured on the real entry text during execution: the
# DEC-08 `negative control` term was found 0 times before this squeeze was added
# and 1 time after. See fold_region().
# ---------------------------------------------------------------------------

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../../.." && pwd)"

#: DIFFERENTIAL SUBSTRATE -- the pre-task HEAD. NEVER re-pin.
BASELINE_REV="0e7e309"

PY="/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python"

DEC_REL=".planning/DECISIONS.md"
HJ_REL=".planning/HANDOFF.json"
DEF_REL=".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md"

OKU_DIR="$SCRIPT_DIR/../260811-oku-discharge-e-2-disclosure-obligations-dra"
MS_SRC="$OKU_DIR/260811-oku-e2-manuscript-limitation-drafts.md"
OSF_SRC="$OKU_DIR/260811-oku-e2-osf-entry-drafts.md"
PAIR_FILE="$SCRIPT_DIR/260811-tf3-SELECTED-PAIR-correction.md"

# Markers that say "this group's edit has already landed in the working tree".
DEC_MARK='DEC-2026-08-11-sr4-disposition'
HJ_MARK='SR4-OPEN — DECIDED 2026-08-11'
DEF_MARK='E-2 FRAMING DECIDED'

FAILS=0
SELFTEST_FAILS=0

pass()    { printf 'PASS %-8s %s\n' "$1" "$2"; }
fail()    { printf 'FAIL %-8s %s -- %s\n' "$1" "$2" "$3"; FAILS=$((FAILS + 1)); }
verdict() { # id desc problems
  if [ -z "$3" ]; then pass "$1" "$2"; else fail "$1" "$2" "$3"; fi
}

require_file() { # clause_id path
  if [ ! -f "$2" ]; then
    fail "$1" "required file present" "file not found: $2"
    return 1
  fi
  return 0
}

# extract_block -- byte-identical to 260811-oku-check-drafts.sh::extract_block.
# The sub() calls strip whitespace from the MARKER MATCH ONLY; block bytes are
# printed untouched. This sameness is what lets the tf3 extraction inherit the
# oku harness's clause evidence by identity instead of by re-assertion.
extract_block() { # file block_id -> block body on stdout (marker lines removed)
  awk -v id="$2" '
    { line = $0; sub(/^[ \t]+/, "", line); sub(/[ \t]+$/, "", line) }
    line == "<!-- PASTE-BEGIN: " id " -->" { inb = 1; next }
    line == "<!-- PASTE-END: "   id " -->" { inb = 0; next }
    inb { print }
  ' "$1"
}

# fold_region -- stdin -> one line, with every run of spaces/tabs squeezed to a
# single space. See the LINE SCOPING note in the header for why the squeeze is
# not optional.
fold_region() { tr '\n' ' ' | tr -s ' \t' ' '; }

appended_region() { # baseline_file current_file -> the bytes beyond the baseline
  local n
  n=$(wc -c < "$1")
  tail -c "+$((n + 1))" "$2"
}

# missing_patterns FILE PATTERN... -> space-joined list of patterns not found
missing_patterns() {
  local f="$1"; shift
  local miss="" p
  for p in "$@"; do
    grep -qE -- "$p" "$f" || miss="$miss [$p]"
  done
  printf '%s' "$miss"
}

missing_patterns_i() { # case-insensitive variant
  local f="$1"; shift
  local miss="" p
  for p in "$@"; do
    grep -qiE -- "$p" "$f" || miss="$miss [$p]"
  done
  printf '%s' "$miss"
}

# ---------------------------------------------------------------------------
# BASELINE GUARD -- runs first on EVERY invocation.
#
# T-tf3-07: a stale baseline is the only way this harness can grade its own edit
# against itself. Two independent assertions, and a trip is fatal (exit 3), not
# a FAIL line -- there is nothing meaningful to measure against a bad substrate.
#
#   BG-01  the baseline blobs must NOT already contain this task's markers.
#          (Always applicable. This is the assertion that would catch a
#          "helpful" re-pin of BASELINE_REV to a post-edit commit.)
#   BG-02  for each file whose group has NOT yet been executed -- detected by
#          the absence of its marker in the working tree, not by a flag file --
#          the working tree must still be identical to the baseline.
# ---------------------------------------------------------------------------

BASE_DIR=""

setup_baselines() {
  BASE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/tf3-baseline.XXXXXX")"
  local rel name
  for rel in "$DEC_REL" "$HJ_REL" "$DEF_REL"; do
    name="$(basename "$rel")"
    if ! git -C "$REPO" show "$BASELINE_REV:$rel" > "$BASE_DIR/$name" 2>/dev/null; then
      printf 'FATAL: cannot materialize baseline %s:%s\n' "$BASELINE_REV" "$rel"
      exit 3
    fi
  done
}

baseline_guard() {
  local problems=""

  # BG-01 -- baseline predates this task's edits.
  grep -qF -- "$DEC_MARK" "$BASE_DIR/DECISIONS.md" \
    && problems="$problems [baseline DECISIONS.md already carries $DEC_MARK]"
  grep -qF -- "$HJ_MARK" "$BASE_DIR/HANDOFF.json" \
    && problems="$problems [baseline HANDOFF.json already carries $HJ_MARK]"
  grep -qF -- "$DEF_MARK" "$BASE_DIR/deferred-items.md" \
    && problems="$problems [baseline deferred-items.md already carries $DEF_MARK]"

  if [ -n "$problems" ]; then
    printf 'FATAL BG-01  baseline %s predates this task -- %s\n' "$BASELINE_REV" "$problems"
    printf '  BASELINE_REV is a DIFFERENTIAL SUBSTRATE. Do NOT re-pin it.\n'
    exit 3
  fi
  pass "BG-01" "baseline $BASELINE_REV carries none of this task's markers"

  # BG-02 -- unexecuted groups must still be clean against the baseline.
  local rel mark pair stale=""
  for pair in "$DEC_REL|$DEC_MARK" "$HJ_REL|$HJ_MARK" "$DEF_REL|$DEF_MARK"; do
    rel="${pair%%|*}"; mark="${pair##*|}"
    if ! grep -qF -- "$mark" "$REPO/$rel" 2>/dev/null; then
      if [ -n "$(git -C "$REPO" diff --numstat "$BASELINE_REV" -- "$rel")" ]; then
        stale="$stale [$rel differs from baseline but carries no tf3 marker]"
      fi
    fi
  done
  if [ -n "$stale" ]; then
    printf 'FATAL BG-02  stale baseline on an unexecuted file -- %s\n' "$stale"
    printf '  Refusing to grade an edit against a substrate that already moved.\n'
    exit 3
  fi
  pass "BG-02" "every not-yet-executed file is still identical to $BASELINE_REV"
}

# ---------------------------------------------------------------------------
# clause group: dec
#   group_dec <baseline_DECISIONS.md> <current_DECISIONS.md>
# Takes FILE PATHS, never git refs, so --self-test can hand it fixture pairs.
# ---------------------------------------------------------------------------

group_dec() {
  local base="$1" cur="$2"
  require_file "DEC-00" "$base" || return
  require_file "DEC-00" "$cur"  || return

  local d; d="$(mktemp -d "${TMPDIR:-/tmp}/tf3-dec.XXXXXX")"
  local n; n=$(wc -c < "$base")

  # DEC-01 -- append-only, byte prefix.
  local p=""
  head -c "$n" "$cur" > "$d/prefix.bin"
  cmp -s "$d/prefix.bin" "$base" || p="first $n bytes of current differ from the baseline (NOT an append)"
  verdict "DEC-01" "append-only: baseline survives as a byte-exact prefix" "$p"

  # DEC-02 -- zero deleted lines (catches mid-file rewrites a prefix check can miss).
  p=""
  local dels; dels=$(diff "$base" "$cur" | grep -c '^<')
  [ "$dels" -eq 0 ] || p="$dels deleted/modified baseline lines"
  verdict "DEC-02" "zero deleted or modified baseline lines" "$p"

  appended_region "$base" "$cur" > "$d/region.txt"
  fold_region < "$d/region.txt" > "$d/fold.txt"

  # DEC-03 -- exactly one heading each, at line start. LINE-SCOPED by design.
  p=""
  local h1='## 2026-08-11 — DEC-2026-08-11-e2-framing-correction'
  local h2='## 2026-08-11 — DEC-2026-08-11-sr4-disposition'
  local c1 c2
  c1=$(grep -cF -- "$h1" "$d/region.txt"); c2=$(grep -cF -- "$h2" "$d/region.txt")
  [ "$c1" -eq 1 ] || p="$p [e2 heading count=$c1, want 1]"
  [ "$c2" -eq 1 ] || p="$p [sr4 heading count=$c2, want 1]"
  grep -qE '^## 2026-08-11 — DEC-2026-08-11-e2-framing-correction' "$d/region.txt" \
    || p="$p [e2 heading not at line start]"
  grep -qE '^## 2026-08-11 — DEC-2026-08-11-sr4-disposition' "$d/region.txt" \
    || p="$p [sr4 heading not at line start]"
  verdict "DEC-03" "both entry headings present exactly once at line start" "$p"

  # DEC-04..DEC-08 are asserted against the ONE-LINE FOLD of the appended region
  # (see LINE SCOPING note in the header): the entries are hard-wrapped prose.

  # DEC-04 -- the E-2 entry carries its identifying content.
  p="$(missing_patterns "$d/fold.txt" \
        'framing B' 'CORRECTION' 'ms-correction' 'osf-correction' \
        'Based on your recommendation' 'obligation \(3\)' 'DISCHARGED' \
        'az52u' 'osf_deviations\.md' 'DEC-2026-08-07-e2-orientation-disposition')"
  verdict "DEC-04" "E-2 entry: framing, selected pair, delegation, obligation (3)" "$p"

  # DEC-05 -- the journal-policy PRE-PLACEMENT step is present as a step.
  p="$(missing_patterns_i "$d/fold.txt" 'journal' 'polic' \
        'pre-placement|before placement' 'placement')"
  verdict "DEC-05" "E-2 entry: journal-policy check recorded as a PRE-PLACEMENT step" "$p"

  # DEC-06 -- the axis guard (framing B is not disposition option B).
  p="$(missing_patterns "$d/fold.txt" 'option A' 'framing B')"
  grep -qiE 'code is (still )?not changed' "$d/fold.txt" \
    || p="$p [code is (still )?not changed]"
  verdict "DEC-06" "E-2 entry: axis guard -- option A stands, only framing moved" "$p"

  # DEC-07 -- the numbers guard.
  p="$(missing_patterns_i "$d/fold.txt" 'identity' 'bookkeeping')"
  if grep -qE '5\.29' "$d/fold.txt"; then
    p="$p$(missing_patterns "$d/fold.txt" 'dragged' '18\.41' '23\.80')"
  fi
  verdict "DEC-07" "E-2 entry: identity-stub caveat; 5.29% never quoted alone" "$p"

  # DEC-08 -- the SR4 entry carries its evidence and its caveats.
  p="$(missing_patterns "$d/fold.txt" \
        'NEVER ACTUALLY FROZEN' '260811-pmv' 'f78bbc1' '399c50f' '2b13dce' \
        'bf16289' '2bda675' 'status report' 'pipeline\.schema\.yaml' \
        'source_freeze\.py' 'negative control')"
  grep -qiE 'no new pin' "$d/fold.txt" || p="$p [no new pin]"
  verdict "DEC-08" "SR4 entry: evidence by path+commit, both caveats, no new pin" "$p"

  # DEC-09 -- standing original-research framing guard. LINE-SCOPED (word-based).
  p=""
  local bad; bad=$(grep -ciE '\b(revisions?|salvage|cleanup)\b' "$d/region.txt")
  [ "$bad" -eq 0 ] || p="$bad line(s) use forbidden framing words (revision/salvage/cleanup)"
  verdict "DEC-09" "original-research framing: no revision/salvage/cleanup" "$p"

  rm -rf "$d"
}

# ---------------------------------------------------------------------------
# clause group: handoff
#   group_handoff <base_json> <cur_json> <base_deferred> <cur_deferred>
# ---------------------------------------------------------------------------

group_handoff() {
  local bj="$1" cj="$2" bd="$3" cd="$4"
  require_file "HJ-00" "$bj" || return
  require_file "HJ-00" "$cj" || return
  require_file "HJ-00" "$bd" || return
  require_file "HJ-00" "$cd" || return

  local d; d="$(mktemp -d "${TMPDIR:-/tmp}/tf3-hj.XXXXXX")"

  # HJ-01 -- THE GATE. A HANDOFF.json that does not parse is a broken resume path.
  local p="" parsed=0
  if "$PY" -c 'import json,sys; json.load(open(sys.argv[1]))' "$cj" > "$d/parse.log" 2>&1; then
    parsed=1
  else
    p="json.load failed: $(head -c 200 "$d/parse.log" | tr '\n' ' ')"
  fi
  verdict "HJ-01" "HANDOFF.json parses as JSON" "$p"

  # HJ-02 -- structural containment: ONLY [0] and [2] may differ.
  p=""
  if [ "$parsed" -eq 1 ]; then
    if ! "$PY" - "$bj" "$cj" > "$d/walk.txt" 2>&1 <<'PYEOF'
import json, sys
old = json.load(open(sys.argv[1])); new = json.load(open(sys.argv[2]))
def walk(a, b, path=""):
    if type(a) is not type(b): yield path; return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b: yield f"{path}.{k}"
            else: yield from walk(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b): yield f"{path}[len {len(a)}->{len(b)}]"; return
        for i, (x, y) in enumerate(zip(a, b)): yield from walk(x, y, f"{path}[{i}]")
    elif a != b: yield path
diffs = sorted(walk(old, new))
allowed = {".carter_decisions_outstanding[0]", ".carter_decisions_outstanding[2]"}
extra = [d for d in diffs if d not in allowed]
print("DIFFERING PATHS:", diffs or "(none)")
print("OUT-OF-SCOPE PATHS:", extra or "(none)")
sys.exit(1 if extra else 0)
PYEOF
    then
      p="$(grep 'OUT-OF-SCOPE' "$d/walk.txt" | tr '\n' ' ')"
      [ -n "$p" ] || p="containment walker errored: $(head -c 200 "$d/walk.txt" | tr '\n' ' ')"
    fi
  else
    p="skipped: current HANDOFF.json does not parse (see HJ-01)"
  fi
  verdict "HJ-02" "containment: only carter_decisions_outstanding[0] and [2] differ" "$p"

  # Materialize the three entries (old and new) for the string clauses.
  local entries_ok=0
  if [ "$parsed" -eq 1 ]; then
    if "$PY" - "$bj" "$cj" "$d" <<'PYEOF' 2>/dev/null
import json, sys
b = json.load(open(sys.argv[1]))["carter_decisions_outstanding"]
c = json.load(open(sys.argv[2]))["carter_decisions_outstanding"]
out = sys.argv[3]
assert len(b) == 3 and len(c) == 3, f"array length {len(b)} -> {len(c)}, want 3"
for i in range(3):
    open(f"{out}/b{i}.txt", "w").write(b[i])
    open(f"{out}/c{i}.txt", "w").write(c[i])
PYEOF
    then entries_ok=1; fi
  fi

  # HJ-03 -- entry [2] is the SR4 disposition, not the open question.
  p=""
  if [ "$entries_ok" -eq 1 ]; then
    head -c 30 "$d/c2.txt" | grep -qF -- '✅ SR4-OPEN — DECIDED 2026-08-11' \
      || p="$p [entry [2] does not START with '✅ SR4-OPEN — DECIDED 2026-08-11']"
    p="$p$(missing_patterns "$d/c2.txt" \
          'NEVER ACTUALLY FROZEN' 'DEC-2026-08-11-sr4-disposition' '260811-pmv' \
          '2bda675' 'pipeline\.schema\.yaml' 'source_freeze\.py')"
    grep -qiE 'no new pin' "$d/c2.txt" || p="$p [no new pin]"
  else
    p="skipped: cannot read carter_decisions_outstanding (see HJ-01)"
  fi
  verdict "HJ-03" "carter_decisions_outstanding[2]: SR4-OPEN flipped to a decision" "$p"

  # HJ-04 -- entry [0] was APPENDED to, never rewritten.
  p=""
  if [ "$entries_ok" -eq 1 ]; then
    if ! "$PY" - "$d/b0.txt" "$d/c0.txt" <<'PYEOF' 2>/dev/null
import sys
old = open(sys.argv[1], "rb").read(); new = open(sys.argv[2], "rb").read()
sys.exit(0 if new.startswith(old) else 1)
PYEOF
    then p="$p [baseline entry [0] is NOT a byte-exact prefix of the new entry [0] -- text was overwritten]"; fi
    "$PY" - "$d/b0.txt" "$d/c0.txt" "$d/tail0.txt" <<'PYEOF' 2>/dev/null
import sys
old = open(sys.argv[1], "rb").read(); new = open(sys.argv[2], "rb").read()
tail = new[len(old):] if new.startswith(old) else new
open(sys.argv[3], "wb").write(tail)
PYEOF
    p="$p$(missing_patterns "$d/tail0.txt" \
          'DEC-2026-08-11-e2-framing-correction' 'framing B' 'ms-correction' \
          'osf-correction' 'az52u' 'osf_deviations\.md' '\(1\)' '\(2\)' '\(3\)')"
  else
    p="skipped: cannot read carter_decisions_outstanding (see HJ-01)"
  fi
  verdict "HJ-04" "carter_decisions_outstanding[0]: pure append, obligations restated" "$p"

  # HJ-05 -- deferred-items.md is INSERTIONS ONLY. Byte-prefix does not apply:
  # these are mid-file insertions by design, so zero-deleted-lines is the gate.
  p=""
  local dels; dels=$(diff "$bd" "$cd" | grep -c '^<')
  [ "$dels" -eq 0 ] || p="$dels deleted/modified baseline lines in deferred-items.md"
  verdict "HJ-05" "deferred-items.md: zero deleted or modified lines" "$p"

  # HJ-06 -- deferred-items.md carries both dispositions.
  p="$(missing_patterns "$cd" \
        'DEC-2026-08-11-e2-framing-correction' 'DEC-2026-08-11-sr4-disposition' \
        'E-2 FRAMING DECIDED' '✅ DISPOSED 2026-08-11')"
  verdict "HJ-06" "deferred-items.md: both 2026-08-11 dispositions recorded" "$p"

  # HJ-07 -- E-2 ADJACENCY. The update must sit INSIDE the E-2 banner, so a
  # reader hits it before the superseded "THREE OBLIGATIONS SURVIVE" claim can
  # be read alone. LINE-SCOPED: this clause is about line ORDER.
  p=""
  local upd_ln log_ln
  upd_ln=$(grep -nF -- 'DEC-2026-08-11-e2-framing-correction' "$cd" | head -1 | cut -d: -f1)
  log_ln=$(grep -nF -- '**Logged:** 2026-08-06 (quick-260805-w7u)' "$cd" | head -1 | cut -d: -f1)
  if [ -z "$upd_ln" ] || [ -z "$log_ln" ]; then
    p="anchor not found (update=${upd_ln:-NONE} logged=${log_ln:-NONE})"
  elif [ "$upd_ln" -ge "$log_ln" ]; then
    p="first E-2 update citation at line $upd_ln is NOT before the superseded Logged line at $log_ln"
  fi
  verdict "HJ-07" "E-2 update sits inside the banner, above the superseded claim" "$p"

  # HJ-08 -- SR4 ADJACENCY. The banner must sit between the heading and the
  # superseded 'Status: OPEN' Logged line.
  p=""
  local hd_ln ban_ln slog_ln
  hd_ln=$(grep -nF -- '## ⚠ SR4-OPEN' "$cd" | head -1 | cut -d: -f1)
  ban_ln=$(grep -nF -- '✅ DISPOSED 2026-08-11' "$cd" | head -1 | cut -d: -f1)
  slog_ln=$(grep -nF -- '**Logged:** 2026-08-06 (`quick-260806-sr4`)' "$cd" | head -1 | cut -d: -f1)
  if [ -z "$hd_ln" ] || [ -z "$ban_ln" ] || [ -z "$slog_ln" ]; then
    p="anchor not found (heading=${hd_ln:-NONE} banner=${ban_ln:-NONE} logged=${slog_ln:-NONE})"
  elif [ "$ban_ln" -le "$hd_ln" ] || [ "$ban_ln" -ge "$slog_ln" ]; then
    p="banner line $ban_ln is not between heading $hd_ln and logged $slog_ln"
  fi
  verdict "HJ-08" "SR4 banner sits between its heading and the superseded status" "$p"

  rm -rf "$d"
}

# ---------------------------------------------------------------------------
# clause group: pair
#   group_pair <selected_pair_file>
# The source blocks are ALWAYS re-extracted from the read-only oku drafts at run
# time -- never cached, never retyped.
# ---------------------------------------------------------------------------

group_pair() {
  local pf="$1"
  require_file "SP-00" "$pf"      || return
  require_file "SP-00" "$MS_SRC"  || return
  require_file "SP-00" "$OSF_SRC" || return

  local d; d="$(mktemp -d "${TMPDIR:-/tmp}/tf3-pair.XXXXXX")"

  # SP-01 -- both selected blocks are delimited exactly once. LINE-SCOPED.
  local p="" id c
  for id in ms-correction osf-correction; do
    c=$(grep -cF -- "<!-- PASTE-BEGIN: $id -->" "$pf")
    [ "$c" -eq 1 ] || p="$p [PASTE-BEGIN $id count=$c, want 1]"
    c=$(grep -cF -- "<!-- PASTE-END: $id -->" "$pf")
    [ "$c" -eq 1 ] || p="$p [PASTE-END $id count=$c, want 1]"
  done
  verdict "SP-01" "both correction blocks delimited exactly once" "$p"

  # SP-02 -- ★ BYTE IDENTITY. The load-bearing clause: it is what makes the oku
  # harness's clause evidence transfer to this file BY IDENTITY rather than by
  # re-assertion. Same extractor, same sources, cmp.
  p=""
  extract_block "$pf"      ms-correction  > "$d/pair_ms.txt"
  extract_block "$MS_SRC"  ms-correction  > "$d/src_ms.txt"
  extract_block "$pf"      osf-correction > "$d/pair_osf.txt"
  extract_block "$OSF_SRC" osf-correction > "$d/src_osf.txt"
  local cmpout
  if ! cmpout=$(cmp "$d/pair_ms.txt" "$d/src_ms.txt" 2>&1); then
    p="$p [ms-correction differs: $cmpout]"
  fi
  if ! cmpout=$(cmp "$d/pair_osf.txt" "$d/src_osf.txt" 2>&1); then
    p="$p [osf-correction differs: $cmpout]"
  fi
  [ -s "$d/pair_ms.txt" ]  || p="$p [ms-correction extraction is EMPTY]"
  [ -s "$d/pair_osf.txt" ] || p="$p [osf-correction extraction is EMPTY]"
  verdict "SP-02" "★ both bodies byte-identical to a fresh oku extraction" "$p"

  # SP-03 -- the unselected halves are absent. MARKER-SCOPED: prose that merely
  # NAMES ms-limitation / osf-limitation is expected and fine.
  p=""
  for id in ms-limitation osf-limitation; do
    c=$(grep -cF -- "<!-- PASTE-BEGIN: $id -->" "$pf")
    [ "$c" -eq 0 ] || p="$p [unselected block $id is present ($c)]"
  done
  verdict "SP-03" "unselected limitation blocks absent" "$p"

  fold_region < "$pf" > "$d/fold.txt"

  # SP-04..SP-08 use the ONE-LINE FOLD (see LINE SCOPING note in the header).

  # SP-04 -- destinations and discharge conditions are on the file's face.
  p="$(missing_patterns "$d/fold.txt" \
        'az52u' 'osf_deviations\.md' 'DEC-2026-08-11-e2-framing-correction' \
        'Track A' 'new supplementary file' 'append-only' \
        'obligation \(1\)' 'obligation \(2\)' 'obligation \(3\)')"
  grep -qiE 'no agent posts' "$d/fold.txt" || p="$p [no agent posts]"
  verdict "SP-04" "destinations, discharge conditions and the no-agent-posts rule" "$p"

  # SP-05 -- the pre-placement journal-policy check.
  p="$(missing_patterns_i "$d/fold.txt" 'journal' 'polic' \
        'pre-placement|before placement' 'placement')"
  verdict "SP-05" "pre-placement journal-policy check present" "$p"

  # SP-06 -- original-research framing guard. LINE-SCOPED (word-based).
  p=""
  local bad; bad=$(grep -ciE '\b(revisions?|salvage|cleanup)\b' "$pf")
  [ "$bad" -eq 0 ] || p="$bad line(s) use forbidden framing words"
  verdict "SP-06" "original-research framing: no revision/salvage/cleanup" "$p"

  # SP-07 -- the pooled figure is never alone.
  p=""
  if grep -qE '5\.29' "$d/fold.txt"; then
    p="$(missing_patterns "$d/fold.txt" 'dragged')"
  fi
  verdict "SP-07" "pooled 5.29% never appears without its 'dragged down' bound" "$p"

  # SP-08 -- the file states on its face that it discharges nothing by existing.
  p="$(missing_patterns "$d/fold.txt" 'DISCHARGED')"
  if ! grep -E 'Carter' "$pf" | grep -qE 'external'; then
    p="$p [no single line carries both 'Carter' and 'external']"
  fi
  verdict "SP-08" "(1) and (2) named UNDISCHARGED and Carter's external actions" "$p"

  rm -rf "$d"
}

# ---------------------------------------------------------------------------
# NEGATIVE CONTROLS -- all fixtures are COPIES under mktemp -d. The real
# DECISIONS.md / HANDOFF.json / deferred-items.md are NEVER mutated.
# ---------------------------------------------------------------------------

check_control() { # name expected_clause alone(yes|no) output
  local name="$1" cid="$2" alone="$3" out="$4"
  local nfail nnamed
  nfail=$(printf '%s\n' "$out"  | grep -c '^FAIL ')
  nnamed=$(printf '%s\n' "$out" | grep -c "^FAIL $cid[[:space:]]")
  printf '  %-8s expect RED on %s%s\n' "$name" "$cid" \
    "$([ "$alone" = yes ] && printf ' (and ALONE)' || printf '')"
  if [ "$nfail" -eq 0 ]; then
    printf '    (no FAIL lines -- CONTROL DEFEATED)\n'
    SELFTEST_FAILS=$((SELFTEST_FAILS + 1))
    return
  fi
  printf '%s\n' "$out" | grep '^FAIL ' | sed 's/^/    /'
  if [ "$nnamed" -eq 0 ]; then
    printf '    ==> CONTROL DEFEATED: %s did not fire\n' "$cid"
    SELFTEST_FAILS=$((SELFTEST_FAILS + 1))
  elif [ "$alone" = yes ] && [ "$nfail" -ne 1 ]; then
    printf '    ==> CONTROL TOO BROAD: %d clauses fired, want exactly 1 (%s)\n' "$nfail" "$cid"
    SELFTEST_FAILS=$((SELFTEST_FAILS + 1))
  else
    printf '    ==> OBSERVED RED on %s\n' "$cid"
  fi
}

check_positive() { # name output
  local name="$1" out="$2"
  local nfail; nfail=$(printf '%s\n' "$out" | grep -c '^FAIL ')
  printf '  %-8s expect GREEN on the real files\n' "$name"
  if [ "$nfail" -eq 0 ]; then
    printf '    ==> GREEN (%d clauses passed)\n' "$(printf '%s\n' "$out" | grep -c '^PASS ')"
  else
    printf '%s\n' "$out" | grep '^FAIL ' | sed 's/^/    /'
    printf '    ==> POSITIVE CONTROL FAILED\n'
    SELFTEST_FAILS=$((SELFTEST_FAILS + 1))
  fi
}

selftest_dec() {
  printf '\n--- self-test: dec (fixtures are COPIES; the real file is never touched) ---\n'
  local d; d="$(mktemp -d "${TMPDIR:-/tmp}/tf3-selftest.XXXXXX")"
  cp "$BASE_DIR/DECISIONS.md" "$d/base.md"
  cp "$REPO/$DEC_REL"         "$d/cur.md"

  check_positive "NC-0" "$(group_dec "$d/base.md" "$d/cur.md" 2>&1)"

  # NC-D1 -- a deleted line INSIDE the baseline region.
  sed '500d' "$d/cur.md" > "$d/d1.md"
  check_control "NC-D1" "DEC-01" no "$(group_dec "$d/base.md" "$d/d1.md" 2>&1)"
  check_control "NC-D1b" "DEC-02" no "$(group_dec "$d/base.md" "$d/d1.md" 2>&1)"

  # NC-D2 -- the SR4 heading removed from the appended region only.
  cp "$d/base.md" "$d/d2.md"
  appended_region "$d/base.md" "$d/cur.md" \
    | grep -vF -- '## 2026-08-11 — DEC-2026-08-11-sr4-disposition' >> "$d/d2.md"
  check_control "NC-D2" "DEC-03" no "$(group_dec "$d/base.md" "$d/d2.md" 2>&1)"

  # NC-D3 -- the journal-policy sentence removed from the appended region only.
  # Must fire DEC-05 ALONE: a control that reddens three clauses proves nothing
  # about the one it names.
  cp "$d/base.md" "$d/d3.md"
  appended_region "$d/base.md" "$d/cur.md" | grep -viE 'polic' >> "$d/d3.md"
  check_control "NC-D3" "DEC-05" yes "$(group_dec "$d/base.md" "$d/d3.md" 2>&1)"

  rm -rf "$d"
}

selftest_handoff() {
  printf '\n--- self-test: handoff (fixtures are COPIES; the real files are never touched) ---\n'
  local d; d="$(mktemp -d "${TMPDIR:-/tmp}/tf3-selftest.XXXXXX")"
  cp "$BASE_DIR/HANDOFF.json"       "$d/base.json"
  cp "$REPO/$HJ_REL"                "$d/cur.json"
  cp "$BASE_DIR/deferred-items.md"  "$d/base.md"
  cp "$REPO/$DEF_REL"               "$d/cur.md"

  check_positive "NC-0" "$(group_handoff "$d/base.json" "$d/cur.json" "$d/base.md" "$d/cur.md" 2>&1)"

  # NC-H1 -- the JSON parse gate, proven on a deliberately broken COPY.
  sed '$d' "$d/cur.json" > "$d/h1.json"
  check_control "NC-H1" "HJ-01" no \
    "$(group_handoff "$d/base.json" "$d/h1.json" "$d/base.md" "$d/cur.md" 2>&1)"

  # NC-H2 -- an OUT-OF-SCOPE value mutated.
  "$PY" - "$d/cur.json" "$d/h2.json" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
d["phase"] = "MUTATED-BY-NC-H2"
json.dump(d, open(sys.argv[2], "w"), ensure_ascii=False, indent=2)
PYEOF
  check_control "NC-H2" "HJ-02" no \
    "$(group_handoff "$d/base.json" "$d/h2.json" "$d/base.md" "$d/cur.md" 2>&1)"

  # NC-H3 -- entry [0] REWRITTEN rather than appended.
  "$PY" - "$d/cur.json" "$d/h3.json" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
a = d["carter_decisions_outstanding"]
a[0] = a[0].split(". ", 1)[1]          # drop the first sentence -> prefix broken
json.dump(d, open(sys.argv[2], "w"), ensure_ascii=False, indent=2)
PYEOF
  check_control "NC-H3" "HJ-04" no \
    "$(group_handoff "$d/base.json" "$d/h3.json" "$d/base.md" "$d/cur.md" 2>&1)"

  # NC-H4 -- a deleted line in deferred-items.md.
  sed '500d' "$d/cur.md" > "$d/h4.md"
  check_control "NC-H4" "HJ-05" no \
    "$(group_handoff "$d/base.json" "$d/cur.json" "$d/base.md" "$d/h4.md" 2>&1)"

  # NC-H5 -- the E-2 update citation MOVED below the superseded Logged line.
  # A pure move of an INSERTED line: nothing from the baseline is deleted, so
  # HJ-05 stays green and the adjacency clause is what has to catch it.
  awk -v cite='DEC-2026-08-11-e2-framing-correction' \
      -v logline='**Logged:** 2026-08-06 (quick-260805-w7u)' '
    { if (!moved && index($0, cite) > 0) { saved = $0; moved = 1; next }
      print
      if (moved == 1 && !done && index($0, logline) > 0) { print saved; done = 1 } }
  ' "$d/cur.md" > "$d/h5.md"
  check_control "NC-H5" "HJ-07" no \
    "$(group_handoff "$d/base.json" "$d/cur.json" "$d/base.md" "$d/h5.md" 2>&1)"

  rm -rf "$d"
}

selftest_pair() {
  printf '\n--- self-test: pair (fixtures are COPIES; the oku sources are read-only) ---\n'
  local d; d="$(mktemp -d "${TMPDIR:-/tmp}/tf3-selftest.XXXXXX")"
  cp "$PAIR_FILE" "$d/cur.md" 2>/dev/null || { printf '  (SELECTED-PAIR file absent -- nothing to control)\n'; SELFTEST_FAILS=$((SELFTEST_FAILS+1)); return; }

  check_positive "NC-0" "$(group_pair "$d/cur.md" 2>&1)"

  # NC-P1 -- a number corrupted INSIDE the ms-correction block.
  sed '/PASTE-BEGIN: ms-correction/,/PASTE-END: ms-correction/s/18\.41/1.841/' \
    "$d/cur.md" > "$d/p1.md"
  check_control "NC-P1" "SP-02" no "$(group_pair "$d/p1.md" 2>&1)"

  # NC-P2 -- the journal-policy sentence deleted. Must fire SP-05 ALONE.
  grep -viE 'polic' "$d/cur.md" > "$d/p2.md"
  check_control "NC-P2" "SP-05" yes "$(group_pair "$d/p2.md" 2>&1)"

  # NC-P3 -- a PASTE-END marker removed.
  grep -vF -- '<!-- PASTE-END: ms-correction -->' "$d/cur.md" > "$d/p3.md"
  check_control "NC-P3" "SP-01" no "$(group_pair "$d/p3.md" 2>&1)"

  rm -rf "$d"
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

ONLY=""
SELFTEST=""
SELFTEST_GROUP=""

while [ $# -gt 0 ]; do
  case "$1" in
    --only)
      ONLY="${2:-}"; shift 2 ;;
    --self-test)
      SELFTEST=1
      case "${2:-}" in
        dec|handoff|pair) SELFTEST_GROUP="$2"; shift 2 ;;
        *) shift ;;
      esac ;;
    -h|--help)
      printf 'usage: %s [--only dec|handoff|pair] [--self-test [dec|handoff|pair]]\n' "$0"
      exit 0 ;;
    *)
      printf 'unknown argument: %s\n' "$1"; exit 2 ;;
  esac
done

case "${ONLY:-all}" in
  all|dec|handoff|pair) ;;
  *) printf 'unknown group: %s\n' "$ONLY"; exit 2 ;;
esac

setup_baselines
trap 'rm -rf "$BASE_DIR"' EXIT

printf '=== 260811-tf3 acceptance harness ===\n'
printf 'repo:     %s\n' "$REPO"
printf 'baseline: %s\n' "$BASELINE_REV"
printf '\n--- baseline guard ---\n'
baseline_guard

if [ -n "$SELFTEST" ]; then
  case "${SELFTEST_GROUP:-all}" in
    dec)     selftest_dec ;;
    handoff) selftest_handoff ;;
    pair)    selftest_pair ;;
    all)     selftest_dec; selftest_handoff; selftest_pair ;;
  esac
  printf '\n=== self-test: %d defeated/too-broad control(s) ===\n' "$SELFTEST_FAILS"
  [ "$SELFTEST_FAILS" -eq 0 ] || exit 1
  exit 0
fi

if [ "${ONLY:-all}" = all ] || [ "$ONLY" = dec ]; then
  printf '\n--- clause group: dec ---\n'
  group_dec "$BASE_DIR/DECISIONS.md" "$REPO/$DEC_REL"
fi

if [ "${ONLY:-all}" = all ] || [ "$ONLY" = handoff ]; then
  printf '\n--- clause group: handoff ---\n'
  group_handoff "$BASE_DIR/HANDOFF.json" "$REPO/$HJ_REL" \
                "$BASE_DIR/deferred-items.md" "$REPO/$DEF_REL"
fi

if [ "${ONLY:-all}" = all ] || [ "$ONLY" = pair ]; then
  printf '\n--- clause group: pair ---\n'
  group_pair "$PAIR_FILE"
fi

printf '\n=== %d FAIL(s) ===\n' "$FAILS"
[ "$FAILS" -eq 0 ] || exit 1
exit 0
