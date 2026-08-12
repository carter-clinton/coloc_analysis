#!/usr/bin/env bash
# 260812-09a-check-review.sh
#
# Acceptance harness for the CORRECTED rcw PRE-FIRE gate review
# (.planning/quick/260811-rcw-…/260811-rcw-PRE-FIRE-GATE-REVIEW.md).
#
#   ./260812-09a-check-review.sh [--only poll|bar|items|anchors|log] [--self-test]
#
# Exit 0 = every clause passed. Non-zero = at least one clause failed, or the
# reviewed file is absent (absence is a LOUD FAILURE, never a skip).
#
# ---------------------------------------------------------------------------
# WHAT THIS HARNESS IS FOR
#
# The document it grades is the LAST THING CARTER READS before a ~11-day /
# $385-1,084 billed fire. The 2026-08-11/12 five-way review found that its
# liveness-poll command FALSE-PASSED its own pre-fire check:
# `gsutil ls gs://${WORKSPACE_BUCKET}/...` double-prefixes (the variable already
# carries `gs://` per SKILL.md:43), so gsutil errors to stderr, stdout is empty,
# and `wc -l` prints 0 -- the same 0 the pre-fire row EXPECTS, and the same 0
# that reads a healthy fire as dead.
#
# The load-bearing clause here is therefore not "a corrected command exists
# somewhere" but "the corrected command sits at EVERY POINT OF USE, and the
# broken form survives nowhere as an instruction."
#
# ---------------------------------------------------------------------------
# GREP DIALECT -- same discipline as 260812-09a-check-v2-pair.sh.
#
# Runtime is /usr/bin/grep = GNU grep 3.6 (measured 2026-08-11/12 on the NC
# State node) because this script executes through its own shebang. The `ugrep`
# an interactive agent shell shows for `grep` is a CLI WRAPPER ARTIFACT and is
# not the runtime dialect; do not propagate it.
#
# D4-07 FORBIDDEN CONSTRUCT: a POSIX ERE bracket expression containing the two
# characters backslash and n means the SET {backslash, n}, not "not a newline".
# This script contains none; clause LOG-04 greps THIS FILE to prove it, with the
# needle assembled at run time so the guard cannot self-match.
#
# ⚠ THE DOUBLE-PREFIX NEEDLE IS ALSO ASSEMBLED AT RUN TIME. If this script
# contained the literal broken command, a naive repo-wide grep for the defect
# would hit the harness that forbids it.
# ---------------------------------------------------------------------------

set -uo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
REVIEW_DEFAULT="$REPO_ROOT/.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md"

# Assembled, never written literally (see header).
BUCKET="rw-migration-aou-rw-476cdac2"
# ⚠ The COMMAND CORE is matched, not the whole pipeline, because a markdown TABLE
# CELL must escape the pipe as `\|`. Matching the full "… | wc -l" would silently
# under-count the §4 row-1 occurrence and let a point of use go ungraded --
# exactly the "a count is a claim" failure this task exists to fix. The `wc -l`
# completion is asserted separately by POLL-02b.
GOOD_POLL="gsutil ls gs://${BUCKET}/ld/AFR_aou/*.npz"
BAD_PREFIX="gs://\${WORKSPACE_BUCKET}"
CHANGELOG_HEAD="## Corrections (2026-08-12)"

FAILS=0
pass()    { printf 'PASS %-9s %s\n' "$1" "$2"; }
fail()    { printf 'FAIL %-9s %s -- %s\n' "$1" "$2" "$3"; FAILS=$((FAILS + 1)); }
verdict() { if [ -z "$3" ]; then pass "$1" "$2"; else fail "$1" "$2" "$3"; fi; }

require_file() {
  if [ ! -f "$2" ]; then fail "$1" "reviewed file present" "file not found: $2"; return 1; fi
  return 0
}

file_hasF() { grep -qF -- "$1" "$2"; }
file_has()  { grep -qE -- "$1" "$2"; }
countF()    { grep -cF -- "$1" "$2"; }

# section_text FILE START_PATTERN END_PATTERN -> the lines strictly between
section_text() {
  awk -v s="$2" -v e="$3" '
    index($0, s) > 0 { inb = 1 }
    inb && index($0, e) > 0 && NR > start { inb = 0 }
    inb { print }
  ' "$1"
}

# live_text FILE -> everything BEFORE the dated changelog. Absence clauses run
# here, because the changelog's job is to QUOTE what was removed; grading the
# whole file would make an honest changelog entry indistinguishable from a
# surviving defect.
live_text() { awk -v h="$CHANGELOG_HEAD" 'index($0, h) > 0 { exit } { print }' "$1"; }

# marked_context FILE NEEDLE WINDOW MARKER... -> 0 if EVERY line carrying NEEDLE
# has at least one MARKER within +/- WINDOW lines. Implements "present nowhere
# except inside an explicitly-marked warning CONTEXT" (context, not line: a
# multi-line warning block legitimately puts the marker on a neighbouring line).
marked_context() {
  local file="$1" needle="$2" win="$3"; shift 3
  # ⚠ Markers are joined with "|" because awk splits on "|" below. Joining with
  # "$*" (spaces) collapsed every marker into ONE unmatchable string and made
  # this guard silently vacuous -- caught by its own control, not by review.
  local joined; printf -v joined '%s|' "$@"; joined="${joined%|}"
  awk -v needle="$needle" -v win="$win" -v markers="$joined" '
    { line[NR] = $0 }
    END {
      nm = split(markers, mk, "|")
      bad = 0
      for (i = 1; i <= NR; i++) {
        if (index(line[i], needle) == 0) continue
        ok = 0
        lo = i - win; if (lo < 1) lo = 1
        hi = i + win; if (hi > NR) hi = NR
        for (j = lo; j <= hi && !ok; j++)
          for (k = 1; k <= nm; k++)
            if (index(line[j], mk[k]) > 0) { ok = 1; break }
        if (!ok) { bad++; printf "line %d: %s\n", i, substr(line[i], 1, 90) }
      }
      exit (bad ? 1 : 0)
    }' "$file"
}

# ---------------------------------------------------------------------------
# clause group: poll -- the corrected command at EVERY point of use (B-BLOCKER-1)
# ---------------------------------------------------------------------------
group_poll() {
  local f="$1" prob n site sect
  require_file "POLL-00" "$f" || return

  # The three points of use, identified by an anchor unique to each.
  # 1) the §4 bucket-.npz-count row      2) the liveness-arbiter block
  # 3) STEP B
  prob=""
  for site in \
      '| Bucket `.npz` count |' \
      '### ⚠ THE LIVENESS ARBITER FOR THE FIRE' \
      '### STEP B — THE FIRE'; do
    file_hasF "$site" "$f" || prob="$prob missing-site($site)"
  done
  verdict "POLL-01" "all three points of use are present in the document" "$prob"

  prob=""
  n=$(countF "$GOOD_POLL" "$f")
  [ "$n" -ge 3 ] || prob="$prob literal-bucket-form-appears-${n}x-need>=3"
  verdict "POLL-02" "the PRIMARY literal-bucket poll command appears at all three sites" "$prob"

  prob=""
  n=$(grep -F -- "$GOOD_POLL" "$f" | grep -cE 'wc -l')
  [ "$n" -ge 3 ] || prob="$prob only-${n}-occurrence(s)-complete-the-pipeline-into-wc-l"
  verdict "POLL-02b" "each occurrence completes into 'wc -l' (markdown-escaped or plain)" "$prob"

  # site-scoped: the liveness block and STEP B must each carry it themselves
  prob=""
  sect="$(section_text "$f" '### ⚠ THE LIVENESS ARBITER FOR THE FIRE' '## §5 — THE CARTER-ONLY SEQUENCE')"
  printf '%s\n' "$sect" | grep -qF -- "$GOOD_POLL" || prob="$prob liveness-block-lacks-command"
  printf '%s\n' "$sect" | grep -qF -- 'NEVER PREFIX IT' || prob="$prob liveness-block-lacks-warning"
  sect="$(section_text "$f" '### STEP B — THE FIRE' '### STEP C —')"
  printf '%s\n' "$sect" | grep -qF -- "$GOOD_POLL" || prob="$prob stepB-lacks-command"
  printf '%s\n' "$sect" | grep -qF -- 'NEVER PREFIX IT' || prob="$prob stepB-lacks-warning"
  sect="$(section_text "$f" '| Bucket `.npz` count |' '| VM state |')"
  printf '%s\n' "$sect" | grep -qF -- "$GOOD_POLL" || prob="$prob s4row1-lacks-command"
  printf '%s\n' "$sect" | grep -qF -- 'NEVER PREFIX IT' || prob="$prob s4row1-lacks-warning"
  verdict "POLL-03" "each point of use carries the command AND the never-prefix warning ITSELF" "$prob"

  prob=""
  file_hasF 'gsutil ls "${WORKSPACE_BUCKET}/ld/AFR_aou/"*.npz | wc -l' "$f" \
    || prob="$prob no-correctly-quoted-env-alternate"
  verdict "POLL-04" "the env-variable alternate is present and correctly quoted" "$prob"

  # The broken form may appear ONLY inside an explicitly-marked warning CONTEXT
  # (+/- 4 lines), never as a bare instruction.
  prob=""
  local unmarked
  unmarked="$(marked_context "$f" "$BAD_PREFIX" 4 \
      'NEVER PREFIX IT' 'double-prefix' 'expands to' 'FALSE-PASS')" \
    || prob="$prob unmarked-double-prefixed-form: $(printf '%s' "$unmarked" | tr '\n' ';')"
  verdict "POLL-05" "the double-prefixed form survives NOWHERE as an instruction" "$prob"

  prob=""
  file_hasF '260611-tbw' "$f" || prob="$prob no-prior-art-citation"
  file_hasF 'gap C3' "$f" || prob="$prob no-gap-C3-citation"
  file_hasF 'run_native_ld_panel.py:925-926' "$f" || prob="$prob no-producer-path-verification"
  verdict "POLL-06" "the defect class is cited (quick-260611-tbw gap C3) and the producer path verified" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: bar -- 276 is not a pass bar (B-HIGH-1)
# ---------------------------------------------------------------------------
group_bar() {
  local f="$1" prob sect
  require_file "BAR-00" "$f" || return

  prob=""
  sect="$(section_text "$f" '### ⚠ THE LIVENESS ARBITER FOR THE FIRE' '## §5 — THE CARTER-ONLY SEQUENCE')"
  printf '%s\n' "$sect" | grep -qF -- '276 IS NOT A PASS BAR' || prob="$prob liveness-block-lacks-caveat"
  printf '%s\n' "$sect" | grep -qF -- 'partial bank' || prob="$prob liveness-block-lacks-partial-bank"
  sect="$(section_text "$f" '### STEP B — THE FIRE' '### STEP C —')"
  printf '%s\n' "$sect" | grep -qF -- '276 IS NOT A PASS BAR' || prob="$prob stepB-lacks-caveat"
  printf '%s\n' "$sect" | grep -qF -- 'partial bank' || prob="$prob stepB-lacks-partial-bank"
  verdict "BAR-01" "the no-276-pass-bar caveat is in BOTH the liveness paragraph and STEP B" "$prob"

  prob=""
  file_hasF 'verify_failed' "$f" || prob="$prob no-verify_failed-mechanism"
  file_hasF 'continues' "$f" || prob="$prob no-loop-continues-mechanism"
  file_hasF ':1503-1504' "$f" || prob="$prob no-PLAN-anchor-for-the-caveat"
  verdict "BAR-02" "the caveat is grounded: verify_failed never uploads, the loop continues" "$prob"

  prob=""
  file_hasF 'climbing to 276' "$f" && prob="$prob absolute-276-liveness-phrasing-survives"
  verdict "BAR-03" "liveness is phrased as climbing TOWARD 276, not TO 276" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: items -- the refreshed open-items table (B-MEDIUM-1/2/3/4)
# ---------------------------------------------------------------------------
group_items() {
  local f="$1" prob
  require_file "ITEM-00" "$f" || return

  prob=""
  file_hasF 'DEC-2026-08-11-e2-framing-correction' "$f" || prob="$prob no-e2-framing-DEC"
  file_hasF 'DEC-2026-08-11-sr4-disposition' "$f" || prob="$prob no-sr4-DEC"
  file_hasF 'ROW REFRESHED 2026-08-12' "$f" || prob="$prob refresh-not-dated"
  file_hasF 'Obligation (3) is ✅ DISCHARGED' "$f" || prob="$prob obligation-3-not-marked-discharged"
  file_hasF "Obligations (1) and (2) remain ⛔ UNDISCHARGED" "$f" || prob="$prob obligations-1-2-not-open"
  verdict "ITEM-01" "the E-2 and SR4 rows carry their DEC ids and the dated refresh" "$prob"

  prob=""
  file_hasF '260812-09a-SELECTED-PAIR-correction-v2.md' "$f" || prob="$prob v2-pair-not-named-as-current"
  file_hasF 'superseded history' "$f" || prob="$prob v1-not-marked-superseded"
  verdict "ITEM-02" "the E-2 row points at the v2 pair as the current outgoing text" "$prob"

  prob=""
  live_text "$f" | grep -qF -- '<panel-uri>' && prob="$prob placeholder-survives-in-the-live-document"
  file_hasF "gs://${BUCKET}/ld/AFR_aou/m3-W2-native-plink-panel.tsv" "$f" || prob="$prob derived-URI-absent"
  file_hasF '_DEFAULT_PANEL_NAME' "$f" || prob="$prob derivation-not-recorded"
  verdict "ITEM-03" "the panel-TSV placeholder is replaced by a URI derived from the producer" "$prob"

  prob=""
  file_hasF 'NO RUNNABLE COMMAND IS GIVEN HERE, AND THAT IS THE HONEST STATE' "$f" \
    || prob="$prob bim-row-not-honestly-labelled"
  file_hasF '0- vs 1-based index origin' "$f" || prob="$prob bim-row-open-question-missing"
  verdict "ITEM-04" "the real-.bim row is honestly labelled with its OPEN index-origin question" "$prob"

  prob=""
  [ "$(countF 'LAST-KNOWN (dated record; not re-verifiable from NC State)' "$f")" -ge 3 ] \
    || prob="$prob fewer-than-three-last-known-labels"
  file_hasF 'Fire-time re-verification NOT required' "$f" || prob="$prob no-reverification-ruling"
  file_hasF 'Row 5 (ADDED 2026-08-12, B-MEDIUM-4)' "$f" || prob="$prob no-cohort-MT-recheck-row"
  file_hasF 'count_cols' "$f" || prob="$prob cohort-recheck-lacks-invariant-1-form"
  verdict "ITEM-05" "the three §2 rows carry last-known labels; the cohort-MT recheck row exists" "$prob"

  prob=""
  file_hasF '**(9) ⚠ ADDED 2026-08-12 (B-MEDIUM-5)' "$f" || prob="$prob no-branch-divergence-item"
  file_hasF 'code-correct reading' "$f" || prob="$prob no-code-correct-reading"
  file_hasF 'allow_partial_manifest' "$f" || prob="$prob branch-ii-flag-not-named"
  verdict "ITEM-06" "the PLAN branch (ii)/(iii) contradiction is recorded with the code-correct reading" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: anchors -- B-LOW-1..4, corrected anchors present, stale ones gone
# ---------------------------------------------------------------------------
group_anchors() {
  local f="$1" prob
  require_file "ANCH-00" "$f" || return

  prob=""
  file_hasF 'occlusion_manifest.py:195-196' "$f" || prob="$prob missing(occlusion_manifest.py:195-196)"
  file_hasF ':716-718' "$f" || prob="$prob missing(run_susie_rss.R:716-718)"
  file_hasF 'INSIDE A DOCSTRING' "$f" || prob="$prob varid-line-not-marked-as-docstring"
  verdict "ANCH-01" "B-LOW-1: the three corrected anchors are present" "$prob"

  # The superseded anchors may survive ONLY inside an explicit correction CONTEXT
  # (+/- 6 lines). This is what caught two residual stale anchors buried in the
  # review's own 2026-08-11 reconciliation log during this task.
  prob=""
  local n unmarked
  for n in 'occlusion_manifest.py:203-208' ':713-716'; do
    unmarked="$(marked_context "$f" "$n" 6 \
        'previously cited' 'earlier text' 'ITSELF CORRECTED' 'CORRECTED 2026-08-12' 'excluded')" \
      || prob="$prob live-stale-anchor($n): $(printf '%s' "$unmarked" | tr '\n' ';')"
  done
  verdict "ANCH-02" "the superseded anchors survive only inside an explicit correction note" "$prob"

  prob=""
  live_text "$f" | grep -qF -- 'four `test_negative_control_pre_change' \
    && prob="$prob four-negative-controls-claim-survives-in-the-live-document"
  file_hasF 'plus **three**' "$f" || prob="$prob three-not-stated"
  file_hasF ':935' "$f" || prob="$prob missing(:935)"
  file_hasF ':1018' "$f" || prob="$prob missing(:1018)"
  file_hasF ':1296' "$f" || prob="$prob missing(:1296)"
  verdict "ANCH-03" "B-LOW-2: three negative-control tests, named by line" "$prob"

  prob=""
  file_hasF 'A FILE-WIDE GREP, NOT A RULE-SCOPED ONE' "$f" || prob="$prob L-11-not-rescoped"
  file_hasF 'test_run_finemap_shell_passes_the_declared_ld_matrix' "$f" || prob="$prob L-13-scoped-proof-not-named"
  file_hasF 'A CONFIG-VALUE READ ONLY' "$f" || prob="$prob L-09-not-rescoped"
  file_hasF 'm3_convert_npz_rds.smk:132' "$f" || prob="$prob L-09-enforcement-chain-not-named"
  file_hasF 'ld_npz_to_rds.R:272' "$f" || prob="$prob L-09-R-fail-fast-not-named"
  verdict "ANCH-04" "B-LOW-3: L-11 and L-09 labels claim exactly what their commands prove" "$prob"

  prob=""
  file_hasF 'BLIND TO A MISSING DIRECTORY' "$f" || prob="$prob L-16-not-annotated"
  file_hasF '2>/dev/null' "$f" || prob="$prob L-16-redirect-not-shown"
  verdict "ANCH-05" "B-LOW-4: L-16's missing-directory blindness is annotated" "$prob"
}

# ---------------------------------------------------------------------------
# clause group: log -- the dated changelog + this harness's own hygiene
# ---------------------------------------------------------------------------
group_log() {
  local f="$1" prob p forbidden sect
  require_file "LOG-00" "$f" || return

  prob=""
  file_hasF '## Corrections (2026-08-12)' "$f" || prob="$prob no-dated-changelog-section"
  verdict "LOG-01" "the dated Corrections (2026-08-12) section exists" "$prob"

  prob=""
  sect="$(section_text "$f" '## Corrections (2026-08-12)' '@@NO-SUCH-END@@')"
  for p in 'B-BLOCKER-1' 'B-HIGH-1' 'B-MEDIUM-1' 'B-MEDIUM-2' 'B-MEDIUM-3' 'B-MEDIUM-4' \
           'B-MEDIUM-5' 'B-LOW-1' 'B-LOW-2' 'B-LOW-3' 'B-LOW-4'; do
    printf '%s\n' "$sect" | grep -qF -- "$p" || prob="$prob changelog-missing($p)"
  done
  verdict "LOG-02" "the changelog names EVERY finding ID" "$prob"

  prob=""
  sect="$(section_text "$f" '## Corrections (2026-08-12)' '@@NO-SUCH-END@@')"
  printf '%s\n' "$sect" | grep -qF -- 'are UNCHANGED' || prob="$prob anchor-not-declared-unchanged"
  printf '%s\n' "$sect" | grep -qF -- 'corrections layer over a dated' || prob="$prob not-declared-a-corrections-layer"
  printf '%s\n' "$sect" | grep -qF -- 'the measured value won' || prob="$prob re-anchoring-disagreements-not-disclosed"
  printf '%s\n' "$sect" | grep -qF -- 'zero perimeter contact' || prob="$prob no-zero-perimeter-restatement"
  verdict "LOG-03" "the changelog states the re-anchoring discipline and the unchanged 2026-08-11 anchor" "$prob"

  prob=""
  printf 'UNDISCHARGED\n' | grep -qE '\bDISCHARGED\b' && prob="$prob boundary-self-matches-UN-form"
  printf 'DISCHARGED\n'   | grep -qE '\bDISCHARGED\b' || prob="$prob boundary-fails-on-bare-form"
  forbidden="$(printf '[^%s]' '\n')"
  grep -qF -- "$forbidden" "$SCRIPT_PATH" && prob="$prob D4-07-forbidden-bracket-construct-in-this-script"
  verdict "LOG-04" "grep dialect verified at run time + no forbidden bracket construct in this script" "$prob"

  # The review must not have acquired a perimeter invocation: every gsutil/gcloud
  # occurrence must be inside a fenced block or a table cell handed to Carter,
  # and the document must still declare zero contact.
  prob=""
  file_hasF 'ZERO perimeter contact was made in' "$f" || prob="$prob zero-contact-claim-removed"
  file_hasF 'instructions for' "$f" || prob="$prob commands-not-declared-as-instructions"
  verdict "LOG-05" "the document still declares zero perimeter contact and Carter-only commands" "$prob"
}

run_group() {
  case "$1" in
    poll)    group_poll    "$2" ;;
    bar)     group_bar     "$2" ;;
    items)   group_items   "$2" ;;
    anchors) group_anchors "$2" ;;
    log)     group_log     "$2" ;;
    all)     group_poll "$2"; group_bar "$2"; group_items "$2"; group_anchors "$2"; group_log "$2" ;;
  esac
  [ "$FAILS" -eq 0 ]
}

# ---------------------------------------------------------------------------
# --self-test : controls on fixture COPIES. The real review is NEVER mutated.
# ---------------------------------------------------------------------------
ST_FAIL=0
expect_red() { # label group file clause sole(yes|no)
  local label="$1" grp="$2" file="$3" clause="$4" sole="$5" o r nfail
  o="$(run_group "$grp" "$file")"; r=$?
  nfail=$(printf '%s\n' "$o" | grep -c '^FAIL ')
  printf '\n=== %s : expect %s to go RED%s ===\n' "$label" "$clause" \
    "$([ "$sole" = yes ] && printf ' (and ONLY %s)' "$clause")"
  printf '%s\n' "$o" | grep '^FAIL ' || printf '(no FAIL lines -- CONTROL DEFEATED)\n'
  printf 'exit=%d  fail_clauses=%d\n' "$r" "$nfail"
  if [ "$r" -eq 0 ]; then
    printf 'SELF-TEST ERROR: %s PASSED -- CONTROL DEFEATED.\n' "$label"; ST_FAIL=1; return
  fi
  if ! printf '%s\n' "$o" | grep -q "^FAIL $clause "; then
    printf 'SELF-TEST ERROR: %s failed, but not on %s.\n' "$label" "$clause"; ST_FAIL=1
  fi
  if [ "$sole" = yes ] && [ "$nfail" -ne 1 ]; then
    printf 'SELF-TEST ERROR: %s was expected to fail ONLY %s, but %d clauses failed.\n' \
      "$label" "$clause" "$nfail"; ST_FAIL=1
  fi
}

self_test() {
  local d base out rc
  if [ ! -f "$REVIEW_DEFAULT" ]; then
    printf 'SELF-TEST FAILED: the reviewed file is absent (%s).\n' "$REVIEW_DEFAULT"; return 2
  fi
  d="$(mktemp -d "${TMPDIR:-/tmp}/review-selftest.XXXXXX")" || return 2
  trap 'rm -rf "$d"' RETURN
  base="$d/base.md"; cp "$REVIEW_DEFAULT" "$base"

  out="$(run_group all "$base")"; rc=$?
  printf '\n=== NC-0 (positive control): the corrected review must PASS every group ===\n%s\nexit=%d\n' "$out" "$rc"
  [ "$rc" -eq 0 ] || { printf 'SELF-TEST ERROR: the base fixture fails its own clauses.\n'; ST_FAIL=1; }

  # ---- poll ---------------------------------------------------------------
  # NC-1 THE NAMED CONTROL: reintroduce the double-prefixed poll form as an
  #      instruction (no warning marker on the line).
  cp "$base" "$d/nc1.md"
  printf '\n| Bucket check (reintroduced) | last-known | `gsutil ls %s/ld/AFR_aou/*.npz \\| wc -l` | 0 |\n' \
    "$BAD_PREFIX" >> "$d/nc1.md"
  expect_red "NC-1 (poll: double-prefixed form reintroduced as an instruction)" poll "$d/nc1.md" "POLL-05" yes

  # NC-2 the corrected command removed from STEP B only (site-scoping).
  cp "$base" "$d/nc2.md"
  awk -v good="$GOOD_POLL" '
    index($0, "### STEP B — THE FIRE") > 0 { inb = 1 }
    inb && index($0, "### STEP C —") > 0 { inb = 0 }
    inb && index($0, good) > 0 { next }
    { print }' "$base" > "$d/nc2.md"
  expect_red "NC-2 (poll: command deleted from STEP B only)" poll "$d/nc2.md" "POLL-03" no

  # NC-3 the never-prefix warning stripped everywhere.
  cp "$base" "$d/nc3.md"
  sed -i 's|NEVER PREFIX IT|never mind|g' "$d/nc3.md"
  expect_red "NC-3 (poll: the never-prefix warning removed)" poll "$d/nc3.md" "POLL-03" no

  # ---- bar ----------------------------------------------------------------
  # NC-4 the no-276-pass-bar caveat removed from the liveness block only.
  cp "$base" "$d/nc4.md"
  awk '
    index($0, "### ⚠ THE LIVENESS ARBITER FOR THE FIRE") > 0 { inb = 1 }
    inb && index($0, "## §5 — THE CARTER-ONLY SEQUENCE") > 0 { inb = 0 }
    inb && index($0, "276 IS NOT A PASS BAR") > 0 { next }
    { print }' "$base" > "$d/nc4.md"
  expect_red "NC-4 (bar: caveat deleted from the liveness block only)" bar "$d/nc4.md" "BAR-01" yes

  # NC-5 the absolute "climbing to 276" phrasing reintroduced.
  cp "$base" "$d/nc5.md"
  sed -i 's|climbing toward 276|climbing to 276|g' "$d/nc5.md"
  expect_red "NC-5 (bar: absolute 'climbing to 276' phrasing reintroduced)" bar "$d/nc5.md" "BAR-03" yes

  # ---- items --------------------------------------------------------------
  # NC-6 the panel-URI placeholder restored.
  cp "$base" "$d/nc6.md"
  sed -i "s|gs://${BUCKET}/ld/AFR_aou/m3-W2-native-plink-panel.tsv|<panel-uri>|g" "$d/nc6.md"
  expect_red "NC-6 (items: <panel-uri> placeholder restored)" items "$d/nc6.md" "ITEM-03" no

  # NC-7 the E-2 row reverted to 'all three UNDISCHARGED'.
  cp "$base" "$d/nc7.md"
  sed -i 's|Obligation (3) is ✅ DISCHARGED|All three obligations remain open|g' "$d/nc7.md"
  expect_red "NC-7 (items: obligation (3) no longer marked discharged)" items "$d/nc7.md" "ITEM-01" yes

  # NC-8 the cohort-MT recheck row deleted.
  cp "$base" "$d/nc8.md"
  sed -i '/Row 5 (ADDED 2026-08-12, B-MEDIUM-4)/d' "$d/nc8.md"
  expect_red "NC-8 (items: the cohort-MT gate-time recheck row deleted)" items "$d/nc8.md" "ITEM-05" yes

  # ---- anchors ------------------------------------------------------------
  # NC-9 a corrected anchor reverted to its stale value, with no correction note.
  cp "$base" "$d/nc9.md"
  sed -i 's|occlusion_manifest.py:195-196|occlusion_manifest.py:203-208|g' "$d/nc9.md"
  expect_red "NC-9 (anchors: the manifest-write anchor reverted to :203-208)" anchors "$d/nc9.md" "ANCH-01" no

  # NC-10 the 'four negative controls' claim reintroduced.
  cp "$base" "$d/nc10.md"
  sed -i 's|plus \*\*three\*\*|plus four|; s|`test_negative_control_pre_change_\*` tests (`:935`|`test_negative_control_pre_change_*` tests (`:935`|' "$d/nc10.md"
  sed -i 's|plus four$|plus four `test_negative_control_pre_change_* tests|' "$d/nc10.md"
  expect_red "NC-10 (anchors: the 'three' count removed)" anchors "$d/nc10.md" "ANCH-03" no

  # NC-11 L-11's rescoping annotation removed.
  cp "$base" "$d/nc11.md"
  sed -i 's|A FILE-WIDE GREP, NOT A RULE-SCOPED ONE|scoped|g' "$d/nc11.md"
  expect_red "NC-11 (anchors: L-11 rescoping annotation removed)" anchors "$d/nc11.md" "ANCH-04" yes

  # ---- log ----------------------------------------------------------------
  # NC-12 a finding ID dropped from the changelog.
  cp "$base" "$d/nc12.md"
  sed -i 's|^| 11 | \*\*B-LOW-4\*\* |.*$|| 11 | (row removed by control) | |g' "$d/nc12.md" 2>/dev/null || true
  sed -i '/| 11 | \*\*B-LOW-4\*\*/d' "$d/nc12.md"
  sed -i 's|B-LOW-4)|B-LOW-x)|g' "$d/nc12.md"
  expect_red "NC-12 (log: the B-LOW-4 row dropped from the changelog)" log "$d/nc12.md" "LOG-02" no

  # NC-13 the changelog heading removed (undated corrections).
  cp "$base" "$d/nc13.md"
  sed -i 's|## Corrections (2026-08-12)|## Corrections|' "$d/nc13.md"
  expect_red "NC-13 (log: the changelog heading undated)" log "$d/nc13.md" "LOG-01" no

  # NC-14 the zero-perimeter-contact declaration removed.
  cp "$base" "$d/nc14.md"
  sed -i 's|ZERO perimeter contact was made in|some perimeter contact was made in|g' "$d/nc14.md"
  expect_red "NC-14 (log: the zero-perimeter-contact declaration removed)" log "$d/nc14.md" "LOG-05" yes

  printf '\n=== SELF-TEST VERDICT ===\n'
  printf 'controls: NC-1 NC-2 NC-3 (poll) | NC-4 NC-5 (bar) | NC-6 NC-7 NC-8 (items) | NC-9 NC-10 NC-11 (anchors) | NC-12 NC-13 NC-14 (log)\n'
  if [ "$ST_FAIL" -eq 0 ]; then
    printf 'SELF-TEST PASSED: every negative control was OBSERVED RED on its named clause, in every clause group.\n'
    return 0
  fi
  printf 'SELF-TEST FAILED: at least one control did not behave as required (see above).\n'
  return 1
}

# ---------------------------------------------------------------------------
ONLY=""; DO_SELF_TEST=0; REVIEW="$REVIEW_DEFAULT"
while [ $# -gt 0 ]; do
  case "$1" in
    --only)      ONLY="${2:-}"; shift 2 ;;
    --only=*)    ONLY="${1#--only=}"; shift ;;
    --self-test) DO_SELF_TEST=1; shift ;;
    --file)      REVIEW="${2:-}"; shift 2 ;;
    -h|--help)   printf 'usage: %s [--only poll|bar|items|anchors|log] [--file PATH] [--self-test]\n' "$(basename "$0")"; exit 0 ;;
    *) printf 'unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

if [ "$DO_SELF_TEST" -eq 1 ]; then self_test; exit $?; fi

case "$ONLY" in
  ""|all)  group_poll "$REVIEW"; group_bar "$REVIEW"; group_items "$REVIEW"; group_anchors "$REVIEW"; group_log "$REVIEW" ;;
  poll)    group_poll    "$REVIEW" ;;
  bar)     group_bar     "$REVIEW" ;;
  items)   group_items   "$REVIEW" ;;
  anchors) group_anchors "$REVIEW" ;;
  log)     group_log     "$REVIEW" ;;
  *) printf 'unknown --only value: %s\n' "$ONLY" >&2; exit 2 ;;
esac

printf '\n%d clause failure(s).\n' "$FAILS"
[ "$FAILS" -eq 0 ]
