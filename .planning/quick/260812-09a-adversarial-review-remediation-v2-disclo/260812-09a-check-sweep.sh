#!/usr/bin/env bash
# 260812-09a-check-sweep.sh
#
# Acceptance harness for the PART C record-surface sweep of quick-260812-09a.
#
#   ./260812-09a-check-sweep.sh [--only json|dec|state|cont|skill|road|claims] \
#                               [--root DIR] [--self-test]
#
# Exit 0 = every clause passed. Non-zero = at least one clause failed, or a
# required file is absent (absence is a LOUD FAILURE, never a skip).
#
# ---------------------------------------------------------------------------
# WHAT THIS GRADES
#
#   json   HANDOFF.json parses (json.load) AND a CONTAINMENT WALKER proves the
#          changed JSON paths are EXACTLY the intended set -- every other value
#          structurally identical to the 42c060e baseline.
#   dec    DECISIONS.md is APPEND-ONLY by BYTE PREFIX (the first N bytes, N =
#          the baseline byte length, are byte-identical) and 0 deleted lines,
#          and the DEC-2026-08-12 entry carries its required parts.
#   state  STATE.md FRONTMATTER is BYTE-IDENTICAL to the baseline (both-empty
#          case guarded), the protected dated '>' blocks survive verbatim, and
#          the body annotations are present.
#   cont   .continue-here.md demote convention: a new dated block on top, the
#          old marker RETITLED not deleted, and ZERO deleted historical lines.
#   skill  SKILL.md: every pre-existing gate row token still present (NO
#          deletions) plus the dated 2026-08-12 banners.
#   road   ROADMAP.md's ld_npz_to_rds.R "frozen/unchanged" claims corrected.
#   claims PER-CLAIM RESIDUAL ASSERTION: for each (claim_id, file), the number
#          of UN-ANNOTATED hits in the tree equals the number of
#          disposition=left rows recorded in the sweep TSV.
#
# ---------------------------------------------------------------------------
# DIALECT / HYGIENE -- same discipline as the sibling harnesses.
#
# Runtime is /usr/bin/grep = GNU grep 3.6 via this script's shebang; the `ugrep`
# an interactive agent shell shows is a CLI WRAPPER ARTIFACT, not the runtime
# dialect. D4-07: no POSIX ERE bracket expression in this file contains the two
# characters backslash+n (which GNU grep reads as the SET {backslash, n}, NOT
# "not a newline"). Clause JSON-04 greps THIS FILE to prove it, with the needle
# assembled at run time so the guard cannot self-match.
#
# ⚠ THE SWEEP TSV IS TAB-SEPARATED AND NOT CSV-QUOTED. Its excerpts contain
# quote characters; a QUOTE_MINIMAL csv reader MERGES rows (130 rows read back
# as 118 during authoring -- a silent under-count). Everything here splits on
# TAB. [[feedback_a_count_is_a_claim_scope_and_reconcile]]
#
# ⚠ EVERY CONTROL RUNS ON FIXTURE COPIES under --root. The real tree is never
# mutated by --self-test.
# ---------------------------------------------------------------------------

set -uo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BASE_REV="42c060e"
QUICK_REL=".planning/quick/260812-09a-adversarial-review-remediation-v2-disclo"
TSV_REL="$QUICK_REL/260812-09a-stale-claim-sweep.tsv"

FAILS=0
pass()    { printf 'PASS %-10s %s\n' "$1" "$2"; }
fail()    { printf 'FAIL %-10s %s -- %s\n' "$1" "$2" "$3"; FAILS=$((FAILS + 1)); }
# ⚠ A whitespace-only problem string is NOT a problem. A helper that emits a bare
# newline turned every python-backed clause red once during authoring -- a guard
# reporting on NOISE is as broken as one that reports nothing.
verdict() {
  local p; p="$(printf '%s' "$3" | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
  if [ -z "$p" ]; then pass "$1" "$2"; else fail "$1" "$2" "$p"; fi
}

# --------------------------------------------------------------------------
# python helper (written once, at start-up)
# --------------------------------------------------------------------------
PYH="$(mktemp "${TMPDIR:-/tmp}/sweep-helper.XXXXXX.py")"
trap 'rm -f "$PYH"' EXIT
cat > "$PYH" <<'PYEOF'
import sys, os, json, re, subprocess, collections
cmd, root, repo, base, TSV_REL = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]

def baseline(rel):
    return subprocess.run(['git','-C',repo,'show', base + ':' + rel],
                          capture_output=True, check=True).stdout

def P(rel): return os.path.join(root, rel)

def out(*msgs):
    for m in msgs: print(m)

if cmd == 'json_parse':
    try:
        json.load(open(P('.planning/HANDOFF.json'), encoding='utf-8'))
    except Exception as e:
        out('parse-error(%s)' % type(e).__name__); sys.exit(0)
    sys.exit(0)

if cmd == 'json_contain':
    INTENDED = {
      ('timestamp',), ('timestamp_reason_2026_08_12',), ('resume_entry_point',),
      ('resume_on_reconnect',), ('headline',), ('carter_decisions_outstanding',),
      ('gates','m3_04b'), ('gates','m3_04c'), ('gates','panel_reachability'),
      ('gates','aou_loop_refire'), ('gates','blocker1_ld_read_path'),
    }
    try:
        cur = json.load(open(P('.planning/HANDOFF.json'), encoding='utf-8'))
    except Exception as e:
        out('unparseable(%s)' % type(e).__name__); sys.exit(0)
    b = json.loads(baseline('.planning/HANDOFF.json'))
    diffs = []
    def walk(a, c, path=()):
        if type(a) is not type(c): diffs.append(path); return
        if isinstance(a, dict):
            for k in set(a) | set(c):
                if k not in a or k not in c: diffs.append(path + (k,)); continue
                walk(a[k], c[k], path + (k,))
        elif isinstance(a, list):
            if len(a) != len(c): diffs.append(path); return
            for i,(x,y) in enumerate(zip(a,c)): walk(x, y, path + (i,))
        elif a != c: diffs.append(path)
    walk(b, cur)
    bad = [p for p in diffs if not any(p[:len(i)] == i for i in INTENDED)]
    for p in bad: out('unintended-change%s' % (list(p),))
    # the demote must be a demote, not a delete
    r = cur.get('resume_on_reconnect', [])
    rb = b.get('resume_on_reconnect', [])
    if not (len(r) == len(rb) + 1): out('resume_on_reconnect-not-prepended-by-exactly-one')
    if not (len(r) > 1 and r[1].startswith('▶ #0-PRIOR (2026-08-07')):
        out('old-entry-0-not-demoted-in-place')
    if r[2:] != rb[1:]: out('older-entries-not-byte-identical')
    if 'all 7 pinned files 0-line diff.' in cur.get('gates',{}).get('m3_04b',''):
        out('retracted-clause-still-live-in-gates.m3_04b')
    sys.exit(0)

if cmd == 'dec_append_only':
    b = baseline('.planning/DECISIONS.md')
    cur = open(P('.planning/DECISIONS.md'), 'rb').read()
    if len(cur) < len(b): out('file-shrank'); sys.exit(0)
    if cur[:len(b)] != b: out('byte-prefix-differs-from-baseline')
    nb = b.decode('utf-8', 'replace').split('\n')
    nc = cur.decode('utf-8', 'replace').split('\n')
    if nc[:len(nb)] != nb: out('baseline-lines-not-preserved-verbatim')
    sys.exit(0)

if cmd == 'state_frontmatter':
    b = baseline('.planning/STATE.md').decode('utf-8', 'replace').split('\n')
    c = open(P('.planning/STATE.md'), encoding='utf-8').read().split('\n')
    def fm(lines):
        if not lines or lines[0].strip() != '---': return None
        for i in range(1, len(lines)):
            if lines[i].strip() == '---': return '\n'.join(lines[:i+1])
        return None
    fb, fc = fm(b), fm(c)
    # both-empty case GUARDED: a missing fence is a FAILURE, not a vacuous pass
    if fb is None: out('baseline-has-no-frontmatter-fence')
    if fc is None: out('current-has-no-frontmatter-fence')
    if fb is not None and fc is not None and fb != fc: out('frontmatter-bytes-differ')
    if fb is not None and len(fb) == 0: out('frontmatter-empty-refusing-vacuous-pass')
    # protected dated '>' blocks must survive verbatim
    cur_text = '\n'.join(c)
    for n in (266, 278, 297, 301, 311, 349, 362):
        ln = b[n-1]
        if not ln.startswith('>'): out('baseline-line-%d-not-a-protected-block' % n); continue
        if ln not in cur_text: out('protected-block-line-%d-lost' % n)
    sys.exit(0)

if cmd == 'cont_demote':
    b = baseline('.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md').decode('utf-8','replace').split('\n')
    c = open(P('.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md'), encoding='utf-8').read()
    cl = c.split('\n')
    if '2026-08-12' not in c: out('no-dated-2026-08-12-block')
    if '★★ LATEST — SUPERSEDES every block below ★★' not in c: out('no-LATEST-marker')
    # the new block must be ABOVE the demoted one
    try:
        i12 = next(i for i,l in enumerate(cl) if '2026-08-12' in l and 'LATEST' in l)
        i07 = next(i for i,l in enumerate(cl) if '2026-08-07 SESSION CLOSE' in l)
        if not i12 < i07: out('2026-08-12-block-not-above-the-2026-08-07-block')
    except StopIteration:
        out('could-not-locate-both-blocks')
    if '2026-08-07 SESSION CLOSE (SUPERSEDED by the 2026-08-12 block above)' not in c:
        out('2026-08-07-marker-not-retitled-in-place')
    # ZERO deleted historical body lines: every non-frontmatter baseline line survives
    lost = [n for n,ln in enumerate(b[9:], start=10)
            if ln.strip() and ln not in c
            and '★★ LATEST' not in ln]
    for n in lost[:6]: out('historical-line-%d-deleted' % n)
    sys.exit(0)

if cmd == 'skill_nodelete':
    b = baseline('.claude/skills/aou-ld-pipeline/SKILL.md').decode('utf-8','replace').split('\n')
    c = open(P('.claude/skills/aou-ld-pipeline/SKILL.md'), encoding='utf-8').read()
    # every pre-existing gate/row token must still be present somewhere
    TOKENS = ['GATE 1.5', 'GATE 0', 'GATE 1', 'GATE 2', 'GATE 3',
              '322 = 161 M2 regions × 2 ancestries', 'Egress = 44 export requests',
              'RULED PASS 2026-04-28', 'CLEARED 2026-06-12',
              'cohort_summary 3 rows', 'BLOCKED on CR-01', 'FIRED 2026-06-12 → PAUSED']
    for t in TOKENS:
        if t not in c: out('deleted-historical-token(%s)' % t)
    for t in ['BANNER 2026-08-12', 'RETIRED PRODUCER (banner 2026-08-12)',
              '[LIVE 2026-08-12]', 'run_native_ld_panel.py', '276']:
        if t not in c: out('missing-banner-element(%s)' % t)
    # GATE 0 / 1 / 1.5 must be marked LIVE; GATE 2 / 3 marked retired
    for ln in c.split('\n'):
        if ln.startswith('- ✅ **GATE 1.5**') and '[LIVE 2026-08-12' not in ln: out('GATE-1.5-not-marked-live')
        if ln.startswith('- ✅ **GATE 0**')   and '[LIVE 2026-08-12' not in ln: out('GATE-0-not-marked-live')
        if ln.startswith('- ✅ **GATE 1**')   and '[LIVE 2026-08-12' not in ln: out('GATE-1-not-marked-live')
        if ln.startswith('- 🟠 **GATE 2**')  and 'RETIRED PRODUCER' not in ln: out('GATE-2-not-marked-retired')
        if ln.startswith('- 🔴 **GATE 3**')  and 'RETIRED PRODUCER' not in ln: out('GATE-3-not-marked-retired')
    sys.exit(0)

if cmd == 'claims_residual':
    tsv = P(TSV_REL) if os.path.exists(P(TSV_REL)) else os.path.join(repo, TSV_REL)
    rows = [l.rstrip('\n').split('\t') for l in open(tsv, encoding='utf-8') if not l.startswith('#')]
    hdr, rows = rows[0], rows[1:]
    if hdr[0] != 'claim_id' or len(hdr) != 7: out('tsv-header-malformed'); sys.exit(0)
    bad = [r for r in rows if len(r) != 7]
    if bad: out('tsv-has-%d-malformed-rows' % len(bad)); sys.exit(0)
    if len(rows) < 20: out('tsv-too-small(%d rows)' % len(rows))
    pats = {}
    for r in rows: pats.setdefault(r[0], r[1])
    left = collections.Counter((r[0], r[2]) for r in rows if r[5] == 'left')
    import glob
    SURF = sorted(set(
        glob.glob(os.path.join(root, '.planning/*.md')) +
        glob.glob(os.path.join(root, '.planning/*.json')) +
        glob.glob(os.path.join(root, '.planning/phases/m3-aou-afr-ld-panel-build/*.md')) +
        [os.path.join(root, '.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md')] +
        glob.glob(os.path.join(root, '.claude/skills/*/SKILL.md'))))
    SURF = [p for p in SURF if os.path.isfile(p)]
    MARK = re.compile(r'2026-08-12')
    # SAME scope exclusion as the generator: DECISIONS.md is swept UP TO the
    # DEC-2026-08-12 heading. That entry is the RECORD OF the enumeration, not a
    # subject of it; counting it would be circular (it quotes every stale claim in
    # order to register it). The two must agree or the assertion is meaningless.
    DEC_CUT = '## 2026-08-12 — DEC-2026-08-12-adversarial-review-remediation'
    for cid, pat in sorted(pats.items()):
        rx = re.compile(pat)
        got = collections.Counter()
        for f in SURF:
            rel = os.path.relpath(f, root)
            lines = open(f, encoding='utf-8', errors='replace').read().split('\n')
            if rel.endswith('DECISIONS.md'):
                for _i, _l in enumerate(lines):
                    if _l.startswith(DEC_CUT): lines = lines[:_i]; break
            for i, ln in enumerate(lines, 1):
                if not rx.search(ln): continue
                lo, hi = max(0, i-7), min(len(lines), i+6)
                if any(MARK.search(x) for x in lines[lo:hi]): continue
                got[(cid, rel)] += 1
        want = {k: v for k, v in left.items() if k[0] == cid}
        for k in set(got) | set(want):
            if got.get(k, 0) != want.get(k, 0):
                out('%s residual mismatch in %s: un-annotated=%d recorded-left=%d'
                    % (cid, k[1], got.get(k, 0), want.get(k, 0)))
    sys.exit(0)

out('unknown-command:' + cmd)
PYEOF

# Problems go to STDOUT. stderr is NOT merged: a python warning read as a clause
# failure once during authoring, which is noise masquerading as a finding. A
# non-zero exit is surfaced explicitly instead, so a crash still cannot pass.
pyh() {
  local o rc err
  err="$(mktemp "${TMPDIR:-/tmp}/pyh-err.XXXXXX")"
  o="$(python3 "$PYH" "$1" "$ROOT" "$REPO_ROOT" "$BASE_REV" "$TSV_REL" 2>"$err")"; rc=$?
  if [ "$rc" -ne 0 ]; then
    printf 'helper-exited-%d: %s\n' "$rc" "$(tr '\n' ' ' < "$err" | cut -c1-300)"
  fi
  [ -n "$o" ] && printf '%s\n' "$o"
  rm -f "$err"
}

file_hasF() { grep -qF -- "$1" "$2"; }

# --------------------------------------------------------------------------
# clause groups
# --------------------------------------------------------------------------
group_json() {
  local prob f="$ROOT/.planning/HANDOFF.json"
  if [ ! -f "$f" ]; then fail "JSON-00" "HANDOFF.json present" "not found: $f"; return; fi

  prob="$(pyh json_parse | tr '\n' ' ')"
  verdict "JSON-01" "HANDOFF.json parses (json.load)" "$prob"

  prob="$(pyh json_contain | tr '\n' ' ')"
  verdict "JSON-02" "containment walker: changed JSON paths are EXACTLY the intended set" "$prob"

  prob=""
  file_hasF '2026-08-12' "$f" || prob="$prob no-dated-2026-08-12-content"
  file_hasF 'DEC-2026-08-11-e2-framing-correction' "$f" || prob="$prob resume-does-not-route-to-e2-DEC"
  file_hasF 'DEC-2026-08-11-sr4-disposition' "$f" || prob="$prob resume-does-not-route-to-sr4-DEC"
  file_hasF '260812-09a-adversarial-review-remediation-v2-disclo' "$f" || prob="$prob resume-does-not-route-to-this-task"
  file_hasF '260811-rcw-PRE-FIRE-GATE-REVIEW.md' "$f" || prob="$prob resume-does-not-route-to-the-fire-surface"
  file_hasF '⚠ STALE 2026-08-12' "$f" || prob="$prob no-dated-STALE-markers-on-superseded-gate-rows"
  verdict "JSON-03" "the resume surface routes to the current decisions and surfaces" "$prob"

  prob=""
  printf 'UNDISCHARGED\n' | grep -qE '\bDISCHARGED\b' && prob="$prob boundary-self-matches-UN-form"
  printf 'DISCHARGED\n'   | grep -qE '\bDISCHARGED\b' || prob="$prob boundary-fails-on-bare-form"
  local forbidden; forbidden="$(printf '[^%s]' '\n')"
  grep -qF -- "$forbidden" "$SCRIPT_PATH" && prob="$prob D4-07-forbidden-bracket-construct-in-this-script"
  verdict "JSON-04" "grep dialect verified at run time + no forbidden bracket construct here" "$prob"
}

group_dec() {
  local prob f="$ROOT/.planning/DECISIONS.md"
  if [ ! -f "$f" ]; then fail "DEC-00" "DECISIONS.md present" "not found: $f"; return; fi

  prob="$(pyh dec_append_only | tr '\n' ' ')"
  verdict "DEC-01" "DECISIONS.md is APPEND-ONLY by byte prefix against $BASE_REV" "$prob"

  prob=""
  file_hasF 'DEC-2026-08-12-adversarial-review-remediation' "$f" || prob="$prob no-DEC-2026-08-12-entry"
  file_hasF 'Codex CLI v0.141.0' "$f" || prob="$prob review-record-missing"
  file_hasF 'What it CLEARED is load-bearing' "$f" || prob="$prob clears-not-recorded"
  verdict "DEC-02" "the DEC-2026-08-12 entry records the five-way review, including its CLEARS" "$prob"

  prob=""
  file_hasF 'THE ONE CANONICAL RESIDUAL / STALE-SITE TABLE' "$f" || prob="$prob no-canonical-table"
  file_hasF '260812-09a-stale-claim-sweep.tsv' "$f" || prob="$prob table-not-sourced-from-the-TSV"
  file_hasF 'SUPERSEDES the three divergent lists' "$f" || prob="$prob supersession-not-stated"
  local cid
  for cid in C1 C2 C3 C4 C5 C6 C7 C8 C9 C10; do
    grep -qF -- "| **$cid** |" "$f" || prob="$prob canonical-table-missing($cid)"
  done
  verdict "DEC-03" "the ONE canonical stale-site table is present and covers all ten claims" "$prob"

  prob=""
  file_hasF '0e7e309' "$f" || prob="$prob sr4-grep-restatement-not-scoped-to-its-measurement-commit"
  file_hasF 'self-reference by the disposition entry' "$f" || prob="$prob self-reference-not-explained"
  file_hasF 'does not weaken the disposition' "$f" || prob="$prob restatement-not-bounded"
  verdict "DEC-04" "the SR4 grep restatement is SCOPED (0 at 0e7e309, >=1 at HEAD by self-reference)" "$prob"

  prob=""
  file_hasF '4 observed-red of 29' "$f" || prob="$prob oku-caveat-figure-missing"
  file_hasF 'task-local and was never in CI' "$f" || prob="$prob oku-caveat-scope-missing"
  file_hasF 'SUMMARY and VERIFICATION are deliberately NOT' "$f" || prob="$prob closed-oku-record-not-declared-untouched"
  verdict "DEC-05" "the oku task-local-harness caveat is recorded (4 of 29, ms group, never CI)" "$prob"

  prob=""
  file_hasF 'ONE ITEM REPORTED RATHER THAN FIXED' "$f" || prob="$prob unfixable-item-not-reported"
  file_hasF 'STAND UNCHANGED AND ARE NOT REOPENED' "$f" || prob="$prob standing-decisions-not-declared"
  verdict "DEC-06" "the reported-not-fixed item and the two standing decisions are declared" "$prob"
}

group_state() {
  local prob f="$ROOT/.planning/STATE.md"
  if [ ! -f "$f" ]; then fail "STATE-00" "STATE.md present" "not found: $f"; return; fi

  prob="$(pyh state_frontmatter | tr '\n' ' ')"
  verdict "STATE-01" "STATE.md frontmatter byte-identical + protected '>' blocks intact" "$prob"

  prob=""
  file_hasF 'SUPERSEDED 2026-08-12' "$f" || prob="$prob no-dated-supersession-annotations"
  file_hasF 'ANSWERED: never frozen' "$f" || prob="$prob sr4-bullet-not-annotated"
  file_hasF 'Obligation (3) is DISCHARGED' "$f" || prob="$prob obligation-3-not-annotated"
  file_hasF 'was falsified 17 commits later' "$f" || prob="$prob the-range-added-line-not-annotated"
  verdict "STATE-02" "the RESUME-HERE bullets and the oku line carry dated supersessions" "$prob"

  prob=""
  file_hasF 'gated at selection time by' "$f" || prob="$prob oku-enforced-by-not-rescoped"
  [ "$(grep -cF -- 'gated at selection time by' "$f")" -ge 2 ] || prob="$prob only-one-oku-surface-rescoped"
  grep -qF -- 'enforced by `260811-oku-check-drafts.sh`' "$f" && prob="$prob oku-overclaim-survives"
  grep -qF -- 'enforced by a 29-clause harness' "$f" && prob="$prob oku-ledger-overclaim-survives"
  verdict "STATE-03" "both oku 'enforced by' surfaces are rescoped to selection-time gating" "$prob"

  prob=""
  file_hasF 'REFRESHED 2026-08-12' "$f" || prob="$prob session-continuity-not-refreshed"
  file_hasF 'INSIDE the `---` fence' "$f" || prob="$prob frontmatter-defects-not-recorded-body-side"
  file_hasF '+313/−62' "$f" || file_hasF '+313 / −62' "$f" || prob="$prob ld_npz_to_rds-drift-not-stated"
  verdict "STATE-04" "Session Continuity refreshed; the frontmatter defects recorded body-side" "$prob"
}

group_cont() {
  local prob f="$ROOT/.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md"
  if [ ! -f "$f" ]; then fail "CONT-00" ".continue-here.md present" "not found: $f"; return; fi
  prob="$(pyh cont_demote | tr '\n' ' ')"
  verdict "CONT-01" "prepend-demote convention: new dated block on top, old marker retitled, no deletions" "$prob"

  prob=""
  file_hasF 'status: adversarial_review_REMEDIATED' "$f" || prob="$prob status-frontmatter-not-updated"
  file_hasF 'DO NOT PLACE OR' "$f" || file_hasF 'do not place or post them' "$f" || prob="$prob v1-not-marked-do-not-post"
  file_hasF '260811-rcw' "$f" || prob="$prob fire-surface-not-named"
  verdict "CONT-02" "the new block names the v2 pair, the corrected fire surface and the status" "$prob"
}

group_skill() {
  local prob f="$ROOT/.claude/skills/aou-ld-pipeline/SKILL.md"
  if [ ! -f "$f" ]; then fail "SKILL-00" "SKILL.md present" "not found: $f"; return; fi
  prob="$(pyh skill_nodelete | tr '\n' ' ')"
  verdict "SKILL-01" "no historical row deleted; GATE 0/1/1.5 LIVE, GATE 2/3 marked retired" "$prob"
}

group_road() {
  local prob f="$ROOT/.planning/ROADMAP.md"
  if [ ! -f "$f" ]; then fail "ROAD-00" "ROADMAP.md present" "not found: $f"; return; fi
  prob=""
  file_hasF 'CORRECTED 2026-08-12' "$f" || prob="$prob no-dated-correction"
  [ "$(grep -cF -- 'CORRECTED 2026-08-12' "$f")" -ge 2 ] || prob="$prob only-one-roadmap-site-corrected"
  file_hasF 'NOT frozen and was never frozen' "$f" || file_hasF 'NOT frozen and never was' "$f" \
    || prob="$prob claim-not-corrected"
  file_hasF 'DEC-2026-08-11-sr4-disposition' "$f" || prob="$prob decision-not-cited"
  verdict "ROAD-01" "both ROADMAP ld_npz_to_rds.R 'frozen/unchanged' claims are corrected" "$prob"
}

group_claims() {
  local prob t="$ROOT/$TSV_REL"
  if [ ! -f "$t" ] && [ ! -f "$REPO_ROOT/$TSV_REL" ]; then
    fail "CLAIM-00" "sweep TSV present" "not found: $t"; return
  fi
  prob=""
  local src="$t"; [ -f "$src" ] || src="$REPO_ROOT/$TSV_REL"
  grep -qF 'claim_id' "$src" || prob="$prob no-header"
  local n; n=$(grep -cv '^#' "$src")
  [ "$n" -ge 21 ] || prob="$prob only-${n}-lines"
  grep -qF 'SURFACES SCANNED' "$src" || prob="$prob scope-not-stated-in-the-header"
  grep -qF 'does NOT follow symlinks' "$src" || prob="$prob symlink-caveat-missing"
  verdict "CLAIM-01" "the sweep TSV exists, is headed, and states its reproducible scope" "$prob"

  prob="$(pyh claims_residual | tr '\n' ' ')"
  verdict "CLAIM-02" "per (claim, file), un-annotated hits == the recorded disposition=left rows" "$prob"
}

run_group() {
  case "$1" in
    json) group_json ;; dec) group_dec ;; state) group_state ;;
    cont) group_cont ;; skill) group_skill ;; road) group_road ;;
    claims) group_claims ;;
    all) group_json; group_dec; group_state; group_cont; group_skill; group_road; group_claims ;;
  esac
  [ "$FAILS" -eq 0 ]
}

# --------------------------------------------------------------------------
# --self-test : controls on a FIXTURE COPY of the tree. The real tree is never
# mutated.
# --------------------------------------------------------------------------
ST_FAIL=0
REAL_ROOT="$REPO_ROOT"

mkfixture() { # dest
  local d="$1"
  mkdir -p "$d/.planning/phases/m3-aou-afr-ld-panel-build" "$d/.claude/skills/aou-ld-pipeline" "$d/$QUICK_REL"
  cp "$REPO_ROOT/.planning/HANDOFF.json"   "$d/.planning/"
  cp "$REPO_ROOT/.planning/DECISIONS.md"   "$d/.planning/"
  cp "$REPO_ROOT/.planning/STATE.md"       "$d/.planning/"
  cp "$REPO_ROOT/.planning/ROADMAP.md"     "$d/.planning/"
  cp "$REPO_ROOT/.planning/phases/m3-aou-afr-ld-panel-build/".*.md \
     "$d/.planning/phases/m3-aou-afr-ld-panel-build/" 2>/dev/null
  cp "$REPO_ROOT/.planning/phases/m3-aou-afr-ld-panel-build/"*.md \
     "$d/.planning/phases/m3-aou-afr-ld-panel-build/" 2>/dev/null
  cp "$REPO_ROOT/.claude/skills/aou-ld-pipeline/SKILL.md" "$d/.claude/skills/aou-ld-pipeline/"
  cp "$REPO_ROOT/$TSV_REL" "$d/$QUICK_REL/"
  cp "$REPO_ROOT/.planning/"*.md "$d/.planning/" 2>/dev/null
  cp "$REPO_ROOT/.planning/"*.json "$d/.planning/" 2>/dev/null
}

expect_red() { # label group root clause sole
  local label="$1" grp="$2" rt="$3" clause="$4" sole="$5" o r nfail
  o="$(ROOT="$rt" run_group "$grp")"; r=$?
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
    printf 'SELF-TEST ERROR: %s expected to fail ONLY %s, but %d clauses failed.\n' "$label" "$clause" "$nfail"
    ST_FAIL=1
  fi
}

self_test() {
  local d out rc
  d="$(mktemp -d "${TMPDIR:-/tmp}/sweep-selftest.XXXXXX")" || return 2
  trap 'rm -rf "$d"; rm -f "$PYH"' EXIT

  mkfixture "$d/base"
  out="$(ROOT="$d/base" run_group all)"; rc=$?
  printf '\n=== NC-0 (positive control): the untouched fixture tree must PASS every group ===\n%s\nexit=%d\n' "$out" "$rc"
  [ "$rc" -eq 0 ] || { printf 'SELF-TEST ERROR: the base fixture fails its own clauses.\n'; ST_FAIL=1; }

  # NC-1  a DELETED DECISIONS.md byte -> the append-only byte-prefix gate.
  mkfixture "$d/nc1"
  python3 -c "
import sys
p=sys.argv[1]; b=open(p,'rb').read()
open(p,'wb').write(b[:5000] + b[5001:])
" "$d/nc1/.planning/DECISIONS.md"
  expect_red "NC-1 (a single DECISIONS.md byte deleted)" dec "$d/nc1" "DEC-01" no

  # NC-2  a HANDOFF value mutated OUTSIDE the intended paths -> containment walker.
  mkfixture "$d/nc2"
  python3 -c "
import json,sys
p=sys.argv[1]; d=json.load(open(p,encoding='utf-8'))
d['do_not'][0] = d['do_not'][0] + ' (mutated by a negative control)'
open(p,'w',encoding='utf-8').write(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
" "$d/nc2/.planning/HANDOFF.json"
  expect_red "NC-2 (a HANDOFF value mutated outside the intended paths)" json "$d/nc2" "JSON-02" yes

  # NC-3  a MUTATED STATE.md FRONTMATTER byte -> the byte-identity gate.
  mkfixture "$d/nc3"
  python3 -c "
import sys
p=sys.argv[1]; L=open(p,encoding='utf-8').read().split('\n')
L[6]=L[6].replace('2026-08-04T13:15:00.000Z','2026-08-12T00:00:00.000Z')
open(p,'w',encoding='utf-8').write('\n'.join(L))
" "$d/nc3/.planning/STATE.md"
  expect_red "NC-3 (one STATE.md frontmatter byte mutated)" state "$d/nc3" "STATE-01" yes

  # NC-4  a DELETED SKILL.md historical row -> the no-deletion gate.
  mkfixture "$d/nc4"
  python3 -c "
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
t=t.replace('322 = 161 M2 regions × 2 ancestries','(row deleted by a negative control)')
open(p,'w',encoding='utf-8').write(t)
" "$d/nc4/.claude/skills/aou-ld-pipeline/SKILL.md"
  expect_red "NC-4 (a SKILL.md historical row deleted)" skill "$d/nc4" "SKILL-01" yes

  # NC-5  a BROKEN JSON comma -> the parse gate.
  mkfixture "$d/nc5"
  # ⚠ This control was DEFEATED on its first authoring: it deleted the SPACE before
  # "phase" instead of the COMMA, and the JSON stayed valid, so the parse gate stayed
  # green and looked correct. Delete the actual separating comma, and ASSERT the
  # mutation really did break the parse before trusting the control.
  python3 -c "
import sys, json
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
i=t.index('\"phase\":'); j=t.rindex(',', 0, i)
t2=t[:j]+t[j+1:]
try:
    json.loads(t2); raise SystemExit('CONTROL SETUP FAILED: the mutated JSON still parses')
except SystemExit: raise
except Exception: pass
open(p,'w',encoding='utf-8').write(t2)
" "$d/nc5/.planning/HANDOFF.json" || { printf 'SELF-TEST ERROR: NC-5 setup failed.\n'; ST_FAIL=1; }
  expect_red "NC-5 (a comma removed from HANDOFF.json)" json "$d/nc5" "JSON-01" no

  # NC-6  a RE-INSERTED stale claim, un-annotated -> the per-claim residual assertion.
  mkfixture "$d/nc6"
  printf '\n\nSTATUS NOTE (negative control): ZERO Carter decisions outstanding; SR4-OPEN remains a question.\n' \
    >> "$d/nc6/.planning/ROADMAP.md"
  expect_red "NC-6 (a stale claim re-inserted un-annotated)" claims "$d/nc6" "CLAIM-02" no

  # NC-7  the .continue-here.md old marker left UN-DEMOTED -> the demote convention.
  mkfixture "$d/nc7"
  python3 -c "
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
t=t.replace('2026-08-07 SESSION CLOSE (SUPERSEDED by the 2026-08-12 block above)',
            '2026-08-07 SESSION CLOSE (★★ LATEST — SUPERSEDES every block below ★★)')
open(p,'w',encoding='utf-8').write(t)
" "$d/nc7/.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md"
  expect_red "NC-7 (the 2026-08-07 marker left un-demoted)" cont "$d/nc7" "CONT-01" yes

  # NC-8  the ROADMAP correction reverted.
  mkfixture "$d/nc8"
  python3 -c "
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
t=t.replace('NOT frozen and was never frozen','frozen as stated').replace('NOT frozen and never was','frozen as stated')
open(p,'w',encoding='utf-8').write(t)
" "$d/nc8/.planning/ROADMAP.md"
  expect_red "NC-8 (the ROADMAP frozen-claim correction reverted)" road "$d/nc8" "ROAD-01" yes

  # NC-9  the canonical table stripped from the DEC entry.
  mkfixture "$d/nc9"
  python3 -c "
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
t=t.replace('THE ONE CANONICAL RESIDUAL / STALE-SITE TABLE','a list of sites')
open(p,'w',encoding='utf-8').write(t)
" "$d/nc9/.planning/DECISIONS.md"
  expect_red "NC-9 (the canonical stale-site table heading removed)" dec "$d/nc9" "DEC-03" yes

  # NC-10 the retracted clause restored to the LIVE gates.m3_04b field.
  mkfixture "$d/nc10"
  python3 -c "
import json,sys
p=sys.argv[1]; d=json.load(open(p,encoding='utf-8'))
d['gates']['m3_04b']='✅ COMPLETE 2026-08-03. tests/m3 444P/31S/0F; all 7 pinned files 0-line diff.'
open(p,'w',encoding='utf-8').write(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
" "$d/nc10/.planning/HANDOFF.json"
  expect_red "NC-10 (the retracted 0-line-diff clause restored to a LIVE field)" json "$d/nc10" "JSON-02" no

  # NC-11 the oku 'enforced by' overclaim restored in STATE.md.
  mkfixture "$d/nc11"
  python3 -c "
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
t=t.replace('gated at selection time by** \`260811-oku-check-drafts.sh\`','enforced by \`260811-oku-check-drafts.sh\`')
open(p,'w',encoding='utf-8').write(t)
" "$d/nc11/.planning/STATE.md"
  expect_red "NC-11 (the oku 'enforced by' overclaim restored)" state "$d/nc11" "STATE-03" no

  printf '\n=== SELF-TEST VERDICT ===\n'
  printf 'controls: NC-1 dec-byte | NC-2 walker | NC-3 frontmatter | NC-4 skill-row | NC-5 json-parse | NC-6 residual | NC-7 demote | NC-8 roadmap | NC-9 canonical-table | NC-10 retracted-clause | NC-11 oku-overclaim\n'
  if [ "$ST_FAIL" -eq 0 ]; then
    printf 'SELF-TEST PASSED: every negative control was OBSERVED RED on its named clause, in every clause group.\n'
    return 0
  fi
  printf 'SELF-TEST FAILED: at least one control did not behave as required (see above).\n'
  return 1
}

# --------------------------------------------------------------------------
ONLY=""; DO_SELF_TEST=0; ROOT="$REPO_ROOT"
while [ $# -gt 0 ]; do
  case "$1" in
    --only)      ONLY="${2:-}"; shift 2 ;;
    --only=*)    ONLY="${1#--only=}"; shift ;;
    --root)      ROOT="${2:-}"; shift 2 ;;
    --self-test) DO_SELF_TEST=1; shift ;;
    -h|--help)   printf 'usage: %s [--only json|dec|state|cont|skill|road|claims] [--root DIR] [--self-test]\n' "$(basename "$0")"; exit 0 ;;
    *) printf 'unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

if [ "$DO_SELF_TEST" -eq 1 ]; then self_test; exit $?; fi

case "$ONLY" in
  ""|all) group_json; group_dec; group_state; group_cont; group_skill; group_road; group_claims ;;
  json)   group_json ;;   dec)   group_dec ;;   state)  group_state ;;
  cont)   group_cont ;;   skill) group_skill ;; road)   group_road ;;
  claims) group_claims ;;
  *) printf 'unknown --only value: %s\n' "$ONLY" >&2; exit 2 ;;
esac

printf '\n%d clause failure(s).\n' "$FAILS"
[ "$FAILS" -eq 0 ]
