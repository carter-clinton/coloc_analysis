---
phase: quick-260821-jam
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: pre-registration
tags: [osf, amendment, occlusion, clause-d, seth-final-pass, pre-paste, pre-execute-commit, class-p, guard, posting-card, m3-07]

files_modified:
  - .planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
  - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  - .planning/debug/260821-POSTING-CARD-occlusion-recalibration.md
  - .planning/STATE.md
  - .planning/HANDOFF.json
  - .planning/quick/260821-jam-bank-seth-final-pass-as-7th-record-pre-p/260821-jam-PLAN.md
  - .planning/quick/260821-jam-bank-seth-final-pass-as-7th-record-pre-p/260821-jam-SUMMARY.md

autonomous: true

requirements:
  - DEC-2026-08-19-occlusion-recalibration-adopted
  - OSF-AMEND-OCCLUSION-BANK-SETH-FINAL-PASS
  - OSF-AMEND-OCCLUSION-PREPASTE-RECONFIRMATION
  - OSF-AMEND-OCCLUSION-POSTING-CARD

user_setup: []

must_haves:
  truths:
    - "The body Seth cleared is byte-identical after the task: the paste block extracted strictly between the two marker lines is 22,945 B / md5 422f1f28d6a3b76c7657fadec05a0237 at HEAD, exactly as it was before the task touched the file."
    - "The pre-execute commit gate now pins the branch tip Seth's final pass was banked against: the full 40-hex literal 241515b5023b2fae52c0ff3a137f566ac4566a5d occurs exactly TWICE in the amendment (the pre-paste table row and its SLOT_LEDGER line), and the superseded 40-hex literal 2689cae0c0c0666012bf451fcdd10924661bcf02 occurs ZERO times."
    - "Both Class-P occurrences moved together BY THE ENGINE, not by hand: the run's SUBSTITUTION LEDGER stdout is transcribed in the SUMMARY showing PRE_EXECUTE_COMMIT FORCE-SUBSTITUTED at 2 occurrences and POSTING_DATE force-substituted to the same string it already held."
    - "Seth's final pass is banked verbatim: the body of .planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md below its provenance header has md5 6ddb3fb56c269303f1478c976a6d6509 — byte-identical to the staged transcription, no paraphrase."
    - "The amendment is paste-gated GREEN at HEAD: the guard's `all` section exits 0 and zero `{{` slot sentinels remain."
    - "Nothing was posted and nothing was fired: _OCCLUSION_ANOMALY_FRACTION is still 0.0005 at src/python/run_native_ld_panel.py:133, git diff --stat 2689cae..HEAD -- src/ tests/ config/ is empty, and no OSF or VM contact of any kind occurred."
    - "The pre-paste checklist's record count is now TRUE: it says SEVEN supporting records and all seven paths are tracked by git."
    - "Everything is on origin: git status -sb reports no `ahead` marker after the push."
  artifacts:
    - path: ".planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md"
      provides: "The SEVENTH supporting record — Seth's final pass, no blocking objection, banked verbatim under a house-style provenance header"
      contains: "No blocking objection remains"
      min_lines: 60
    - path: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      provides: "The amendment with its pre-paste re-confirmation executed: PRE_EXECUTE_COMMIT moved to the posting-prep HEAD by the engine, prose made true, checklist at seven records, paste block untouched"
      contains: "241515b5023b2fae52c0ff3a137f566ac4566a5d"
    - path: ".planning/debug/260821-POSTING-CARD-occlusion-recalibration.md"
      provides: "Carter's turnkey posting card: scp, macOS md5 verification against the final anchors, the awk paste-body extraction, the NEW-file-not-a-trsx5-revision OSF sequence, what to paste back, and the DON'Ts"
      contains: "osf.io/az52u"
      min_lines: 40
  key_links:
    - from: ".planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py"
      to: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      via: "--second-pass Class-P force-substitution moving PRE_EXECUTE_COMMIT at every occurrence"
      pattern: "PRE_EXECUTE_COMMIT = 241515b5023b2fae52c0ff3a137f566ac4566a5d"
    - from: ".planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh"
      to: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      via: "guard all — exit 0 is the paste gate"
      pattern: "GUARD all: GREEN"
    - from: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      to: ".planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md"
      via: "pre-paste checklist item 3, which now names seven supporting records including this one"
      pattern: "260821-SETH-FINAL-PASS-no-blocking-objection-as-received\\.md"
    - from: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      to: ".planning/debug/260821-POSTING-CARD-occlusion-recalibration.md"
      via: "final whole-file + paste-block byte anchors computed after the amendment's last commit"
      pattern: "422f1f28d6a3b76c7657fadec05a0237"
    - from: "src/python/run_native_ld_panel.py"
      to: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      via: "the posting gate — the constant must still be 0.0005 when the amendment is posted"
      pattern: "_OCCLUSION_ANOMALY_FRACTION = 0.0005"
---

<objective>
Bank Seth's FINAL PASS as the seventh supporting record, execute the amendment's OWN
pre-paste re-confirmation (including moving `PRE_EXECUTE_COMMIT` by the engine because the
branch has advanced four docs-only commits), and hand Carter a posting card so he can post
today.

Purpose: the amendment's pre-paste table carries a STANDING instruction — "RE-CONFIRMED AT
POSTING: re-read HEAD … and update this value if the branch has advanced." Seth's final pass
repeats it in his own words ("same discipline needed at posting: re-read HEAD, and if the
branch has advanced again, move both"). That instruction is now due. This task executes it
mechanically, with the engine rather than a hand edit, so the two occurrences cannot drift
apart — and proves that the 22,945-byte body Seth cleared did not move a single byte while
we did it.

Output: a seventh banked record; a re-confirmed amendment whose gate commit pins the tree
Seth's clearance was given against; refreshed byte anchors; a turnkey posting card; STATE and
HANDOFF updated; everything on origin.

DOCS-ONLY. No code change. AN AGENT NEVER POSTS TO OSF AND NEVER FIRES.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
@.planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md
@.planning/quick/260820-u6i-revise-the-instantiated-amendment-per-se/260820-u6i-SUMMARY.md

<facts>
<!-- All verified read-only at planning time, 2026-08-21 ~13:50 EDT. Do not re-derive from -->
<!-- memory; re-measure with the commands below and REQUIRE these values.                  -->

HEAD at task start   = 241515b5023b2fae52c0ff3a137f566ac4566a5d (branch m3-W2-aou-deltas, == origin)
AMEND                = .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
AMEND whole-file     = 42,213 B / 591 lines / md5 e1b4a11d18ad2907af4f0a93fd5747d2
PASTE block          = 22,945 B / md5 422f1f28d6a3b76c7657fadec05a0237
  extraction (EXCLUSIVE of both marker lines; markers at lines 164 and 498):
    awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$AMEND"
PRE_EXECUTE_COMMIT   = 2689cae0c0c0666012bf451fcdd10924661bcf02 at line 63 (pre-paste table row)
                       and line 92 (SLOT_LEDGER). Both OUTSIDE the paste block. Prose at line 140.
POSTING_DATE         = 2026-08-21 at lines 64, 91 (outside) and 168 (`**Date:** 2026-08-21`, INSIDE
                       the paste block). Posting is TODAY, so the value does not change; the engine
                       force-substitutes it to the identical string, net zero bytes.
Branch advanced since 2689cae by four DOCS-ONLY commits: b4263e7, a364d19, cd0cdfd, 241515b.
  `git diff --stat 2689cae HEAD -- src/ tests/ config/` is EMPTY (0 lines).
  `_OCCLUSION_ANOMALY_FRACTION = 0.0005` is at src/python/run_native_ld_panel.py:133.
SCRATCH              = /gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad
SETH_STAGED          = $SCRATCH/seth-final-pass-verbatim.md — 6,665 B / 54 lines /
                       md5 6ddb3fb56c269303f1478c976a6d6509
ENGINE               = .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
GUARD                = .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
Six records already committed under .planning/debug/:
  260819-SETH-VERDICT-adjudication-confirmed-as-received.md
  260819-SETH-C1C2C3-convergence-as-received.md
  260819-occ-measure-sweep-results-as-received.md
  260819-supplement-results-as-received.md
  260820-site-basis-sweep-results-as-received.md
  260820-SETH-ATTACK-instantiated-amendment-as-received.md
Carter's Mac: ssh ckclinto@login.hpc.ncsu.edu ; local dest
  /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/
  macOS has `md5` (prints `MD5 (file) = hash`), NOT `md5sum`.
OSF: project osf.io/az52u. The July amendment is file GUID `trsx5` and MUST remain at exactly
  1 revision before and after. The new amendment posts as a NEW file.
</facts>

<engine_contract>
<!-- Read off the engine source at planning time so the executor need not explore. -->

  python3 "$ENGINE" --second-pass "$AMEND" \
          --pre-execute-commit <40-hex> --posting-date YYYY-MM-DD [--dry-run]

Under `--second-pass`:
  * CLASS-M (19 measured slots) — each already-filled ledger value is recomputed from the two
    banked records and compared BYTE-IDENTICALLY. Any drift ABORTS. Prints `VERIFIED-IN-PLACE`.
  * CLASS-P (POSTING_DATE, PRE_EXECUTE_COMMIT) — argv-sourced and DEFINED to move. Replaced
    document-wide via `text.replace(old_ledger_value, new)`, fenced by: refuse if the current
    ledger value is empty or still a sentinel; assert the new literal occurs exactly as many times
    as the old did; assert the superseded literal is GONE (skipped when old == new); assert the
    count of the INSTANTIATION date `2026-08-20` is unchanged across the same replace. Prints
    `FORCE-SUBSTITUTED <slot> <old-> -> <new->  (N occurrence(s); ...)`.
  * `--dry-run` performs every read, every verify and every force-substitution IN MEMORY, prints
    `*** DRY RUN — <path> NOT written ***`, and writes NOTHING.
  * The replace matches the FULL 40-hex ledger literal. A 7-hex short form in prose is invisible
    to it — which is why the prose may safely name `8638ed3` and `2689cae` as history.

Guard: `bash "$GUARD" {draft|paste-ready|arith|quote|all} "$AMEND"` prints `GUARD <section>: GREEN`
and exits 0, or `RED` and exits non-zero.
  * `paste-ready` FAILS on any surviving `{{`/`}}`, on an `XX` in the BASENAME (so a copy used for
    a negative control MUST keep the real basename), and on any ledger line that stops matching its
    anchored filled-value pattern.
  * `draft` counts ledger lines with `grep -c -E '^  [A-Z0-9_]+ = '` and requires EXACTLY 21.
    No edit in this task may add or remove a line matching that pattern.
  * `quote` reads a repo-relative source of truth, so always run the guard from the repo root.
</engine_contract>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Bank Seth's final pass as the seventh supporting record</name>
  <files>.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md</files>
  <action>
Bank Seth's verdict VERBATIM under a house-style provenance header. Verbatim means byte-exact: the
proof below is an md5 of the appended region, not a reading.

STEP 1 — verify the staged transcription BEFORE using it:

```
SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad
SETH="$SCRATCH/seth-final-pass-verbatim.md"
wc -c -l "$SETH"; md5sum "$SETH"
```

REQUIRE 6665 bytes / 54 lines / md5 `6ddb3fb56c269303f1478c976a6d6509`. Any mismatch means STOP,
write nothing, report. A transcription you did not anchor is a transcription you cannot bank.

STEP 2 — compose the header. Imitate the provenance style of
`.planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md` lines 1-11: an H1 title
line, a blank line, then a single `>` blockquote. The header MUST carry:

  * received 2026-08-21 ~13:42 EDT, pasted by Carter into the NCSU session;
  * that it answers the revision-reply courier
    `.planning/debug/260820-COURIER-TO-SETH-revision-reply.md` (3,629 B / md5
    `6724c59289450399ef5d1900220440d4`) on the revised amendment (42,213 B / md5
    `e1b4a11d18ad2907af4f0a93fd5747d2`);
  * the fact that distinguishes this pass from every earlier one: Seth verified BOTH anchors
    HIMSELF by reading Carter's local Mac copy of the repo rather than through the paste channel,
    so this pass carries NO TRANSFER RISK — a first on this thread;
  * `AS-RECEIVED transcription; Seth supplied no byte anchors of his own.`;
  * net state: section 2 (count-vs-fraction) CLEARED — he recomputed 0.1888/0.1685 = 1.1205 and
    1.18 x (96,708/102,421) = 1.1142; section 3 (permissiveness pre-emption) CLEARED —
    3 x 0.1888 = 0.5664; section 6 (the collinearity note's home) CLEARED — the path string occurs
    once and sits after `--- PASTE ENDS HERE ---`; section 4 (companion inflation gate) ADOPTED and
    independently verified — 3 x 1.14 = 3.42x, 3.42/1.79 = 1.91x, med+3sigma = 1.407 and
    med+4sigma = 1.496 both below the observed max 1.79 (the SAME rejection pattern as the site
    basis), and a mean-anchored ceiling would have been LOOSER at 3.54x;
  * NO BLOCKING OBJECTION REMAINS;
  * his explicit ask that the section-4 self-attribution — that this corrects his OWN earlier
    recommendation — NOT be softened;
  * his PRE_EXECUTE_COMMIT check (8638ed3 -> 2689cae verified at 2 occurrences / 0 stale) and his
    standing instruction "same discipline needed at posting: re-read HEAD, and if the branch has
    advanced again, move both" — noting that quick-260821-jam Task 2 IS that instruction executing;
  * the guard 2x2 accepted;
  * the TWO items he explicitly does NOT assert are done: (1) Carter posts — an agent never posts,
    the pre-paste checklist is the gate; (2) POSTING_DATE slip handling;
  * his closing authorization: after posting, the code constant change is authorized ONLY as the
    TWO-PART change (the pre-registered site-basis metric AND the companion inflation condition),
    never the ceiling alone;
  * his status line VERBATIM: `measurement banked; amendment drafted, NOT posted;
    _OCCLUSION_ANOMALY_FRACTION still 0.0005 in code; fire HELD; an agent never posts and never
    fires.`

STEP 3 — build the file so the body is provably untouched. Write ONLY the header first (ending with
a blank line, then a `---` separator line, then a blank line), count its lines, then append the
staged file with `cat`:

```
OUT=.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
# ... write header + blank + '---' + blank into "$OUT" (quoted heredoc) ...
N=$(wc -l < "$OUT")            # header line count, INCLUDING the --- separator and blanks
cat "$SETH" >> "$OUT"
echo "header lines: $N"
tail -n +$((N+1)) "$OUT" | md5sum      # MUST be 6ddb3fb56c269303f1478c976a6d6509
```

If the tail md5 differs, the body was mangled — restore and redo. Do NOT "fix" it by editing the
body. Record `$N` in the SUMMARY so the proof is reproducible.

STEP 4 — commit, explicit path only (GPFS: NEVER `git add -A` or `git add .`):

```
git add .planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
git commit -m "docs(quick-260821-jam): bank Seth FINAL PASS — no blocking objection, 7th supporting record"
```
  </action>
  <verify>
    <automated>OUT=.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md; SEP=$(awk '/^---$/{print NR; exit}' "$OUT"); tail -n +$((SEP+2)) "$OUT" | md5sum | grep -q '^6ddb3fb56c269303f1478c976a6d6509' && git ls-files --error-unmatch "$OUT" >/dev/null && git diff --quiet HEAD -- "$OUT" && echo PASS</automated>
  </verify>
  <done>
`.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md` is committed; the
region below its `---` separator has md5 `6ddb3fb56c269303f1478c976a6d6509`; the header states the
no-transfer-risk provenance, the four section dispositions, the two NOT-asserted-done items, the
two-part-change authorization, and Seth's verbatim status line; the SUMMARY records the header line
count. Working tree otherwise untouched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Execute the pre-paste re-confirmation — engine moves PRE_EXECUTE_COMMIT, paste block proven byte-identical</name>
  <files>.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md</files>
  <action>
This is the amendment's own standing instruction executing. Run the steps IN ORDER and capture
EVERY command's output verbatim into the SUMMARY — the transcript IS the evidence.

```
AMEND=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
ENGINE=.planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
GUARD=.planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
PB() { awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$1"; }
```
Run everything from the repo root — the guard's `quote` section resolves a repo-relative source.

(a) BEFORE ANCHORS — `wc -c -l "$AMEND"`, `md5sum "$AMEND"`, `PB "$AMEND" | wc -c`,
    `PB "$AMEND" | md5sum`. REQUIRE 42213 B / 591 lines / `e1b4a11d18ad2907af4f0a93fd5747d2` and
    22945 B / `422f1f28d6a3b76c7657fadec05a0237`. Mismatch means STOP.

(b) PRE-PASTE CHECKLIST, items 1-3:
    1. `bash "$GUARD" all "$AMEND"; echo "EXIT=$?"` -> GREEN / EXIT=0.
    2. `git log --oneline 2689cae..HEAD` (expect the four docs-only commits b4263e7, a364d19,
       cd0cdfd, 241515b — list them); `git diff --stat 2689cae HEAD -- src/ tests/ config/ | wc -l`
       -> 0; `grep -n '_OCCLUSION_ANOMALY_FRACTION = 0.0005' src/python/run_native_ld_panel.py`
       -> hit at line 133.
    3. `git ls-files` must return all SEVEN record paths (the six listed in <facts> plus Task 1's
       file). Run one `git ls-files --error-unmatch` per path and show each resolved; a missing
       path means STOP.

(c) ENGINE — DRY RUN FIRST, then the real run. The 40-hex is HEAD at task start:

```
python3 "$ENGINE" --second-pass "$AMEND" \
        --pre-execute-commit 241515b5023b2fae52c0ff3a137f566ac4566a5d \
        --posting-date 2026-08-21 --dry-run ; echo "EXIT=$?"
```
    EXPECT: `RECONCILIATION: OK`, `ROW-BASIS RECONCILIATION: OK`, PRE-REGISTERED EXPECTATIONS OK,
    `CLASS-M DRIFT VERIFY: OK — 19 already-filled measured value(s) unmoved`, a CLASS-P block with
    `FORCE-SUBSTITUTED PRE_EXECUTE_COMMIT 2689cae- -> 241515b-  (2 occurrence(s); '2026-08-20'
    count N unchanged ...)` and `FORCE-SUBSTITUTED POSTING_DATE 2026-08-21 -> 2026-08-21
    (3 occurrence(s); ...)`, then `*** DRY RUN — ... NOT written ***`, EXIT=0. Anything else means
    STOP and report; do not proceed to the write.
    Then the identical command WITHOUT `--dry-run`; EXIT=0. Paste the full SUBSTITUTION LEDGER
    table into the SUMMARY.

(d) AFTER-ENGINE CHECKS (before any prose edit):
    * `grep -c '2689cae0c0c0666012bf451fcdd10924661bcf02' "$AMEND"` -> 0
    * `grep -n '241515b5023b2fae52c0ff3a137f566ac4566a5d' "$AMEND"` -> exactly 2 hits, at the
      pre-paste table row (line 63) and the SLOT_LEDGER line (line 92)
    * `grep -c '2026-08-21' "$AMEND"` -> 3, unchanged (lines 64, 91, 168)
    * `PB "$AMEND" | wc -c` -> 22945 and `PB "$AMEND" | md5sum` -> `422f1f28d6a3b76c7657fadec05a0237`
      — STILL. This is the decisive invariant: the body Seth cleared did not move.
    * `wc -c "$AMEND"` -> still 42213 (40-hex replaced by 40-hex, date by the same date); the
      whole-file md5 is NEW — record it.

(e) THREE PROSE EDITS, ALL OUTSIDE THE PASTE BLOCK. Use content-anchored edits (line numbers move).
    Change nothing else. Do not add or remove any line matching `^  [A-Z0-9_]+ = ` (the guard's
    `draft` section requires exactly 21 ledger lines).

    NEVER RETYPE THE 40-HEX. The engine wrote it; the two occurrences it created are the only
    places it may appear. In prose refer to the current value as "the value carried in this row" /
    "the value in the pre-paste table row above". History may name the SHORT forms `8638ed3` and
    `2689cae`, which the engine's full-literal replace cannot see.

    (i) Pre-paste table row (line 63). Replace ONLY the descriptive clause
        "— the HEAD of `m3-W2-aou-deltas` captured before the first commit of the REVISING task.
        It SUPERSEDED the first instantiation's value when the branch advanced, on the standing
        authority of the next sentence."
        with a clause TRUE of the new value: the HEAD of `m3-W2-aou-deltas` captured before the
        first commit of the POSTING-PREP task of 2026-08-21 (quick `260821-jam`), immediately after
        Seth's final pass was banked; it superseded `2689cae` (which had itself superseded
        `8638ed3`) because the branch advanced by four docs-only commits.
        KEEP the following sentence VERBATIM, unchanged, in place:
        "RE-CONFIRMED AT POSTING: re-read HEAD, confirm no `_OCCLUSION_ANOMALY_FRACTION` or
        gate-constant change has landed since, and update this value if the branch has advanced."

    (ii) Instantiation-record item 4 prose (line 140 region). Replace
         "the full 40-hex HEAD captured before the REVISING task's first commit — it advanced from
         the first instantiation's value when the branch advanced"
         with the analogous true statement: the full 40-hex HEAD captured before the POSTING-PREP
         task's first commit — it has now advanced TWICE, `8638ed3` -> `2689cae` -> the value
         carried in the pre-paste table row above, each time by the engine's document-wide Class-P
         force-substitution rather than by hand.

    (iii) Pre-paste checklist item 3 (line 157 region). "the six supporting records" -> "the seven
          supporting records", and append Seth's final pass to the enumeration by name and path:
          `.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md`.

(f) AFTER-PROSE ANCHORS — the FINAL anchors Task 3 will publish:
    * `PB "$AMEND" | wc -c` -> 22945 and `PB "$AMEND" | md5sum` ->
      `422f1f28d6a3b76c7657fadec05a0237`. If this moved, a prose edit escaped the markers — REVERT
      and redo.
    * `wc -c -l "$AMEND"` and `md5sum "$AMEND"` -> record as the FINAL anchors.
    * `bash "$GUARD" all "$AMEND"; echo "EXIT=$?"` -> GREEN / EXIT=0.
    * `grep -c '{{' "$AMEND"` -> 0.
    * `grep -c -E '^  [A-Z0-9_]+ = ' "$AMEND"` -> 21.
    * `grep -c '2689cae0c0c0666012bf451fcdd10924661bcf02' "$AMEND"` -> 0 (the full literal is gone).
      `grep -n '2689cae' "$AMEND"` -> the SHORT-form prose mentions only; state the exact count and
      the line numbers in the SUMMARY, and say plainly that these are historical references in
      prose, not slot values. Do NOT re-run the engine after the prose edit; if you do, it must
      still exit 0 and the paste-block md5 must be re-proved.

(g) NEGATIVE CONTROLS — fresh, re-executed this session, on COPIES under `$SCRATCH` only. Never
    perturb the in-tree file. Each copy goes in its own subdirectory so the BASENAME is preserved
    (the guard fails on a basename carrying `XX`, and a renamed copy would confound the control).
    Run each, transcribe command + output + exit code into the SUMMARY, then delete the copy.

    NC-1 (the guard actually catches an un-instantiated slot):
      `mkdir -p "$SCRATCH/nc1" && cp "$AMEND" "$SCRATCH/nc1/"`; in the COPY replace ONE filled
      ledger value with its sentinel, e.g. `SITE_MEDIAN_PCT = 0.1685%` -> `SITE_MEDIAN_PCT =
      {{SITE_MEDIAN_PCT}}`; run
      `bash "$GUARD" all "$SCRATCH/nc1/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"; echo "EXIT=$?"`
      -> EXIT non-zero. QUOTE the failing `FAIL: paste-ready: ...` line verbatim. Then
      `rm -rf "$SCRATCH/nc1"`.

    NC-2 (the Class-P force-substitution is real and hits exactly 2 occurrences):
      `mkdir -p "$SCRATCH/nc2" && cp "$AMEND" "$SCRATCH/nc2/"`; run the engine `--second-pass`
      against the COPY with a DIFFERENT 40-hex, `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
      (`--posting-date 2026-08-21`), first `--dry-run` (show the `FORCE-SUBSTITUTED
      PRE_EXECUTE_COMMIT ... (2 occurrence(s)...)` line and the `NOT written` line), then for real
      on the copy; then on the COPY:
      `grep -c '241515b5023b2fae52c0ff3a137f566ac4566a5d'` -> 0 and
      `grep -c 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'` -> 2. Then `rm -rf "$SCRATCH/nc2"`.
      Re-assert afterwards that the IN-TREE file still greps 2 for the real 40-hex — the control
      must not have leaked.

    NC-3 (the paste-block invariant is a real check, not a tautology):
      `mkdir -p "$SCRATCH/nc3" && cp "$AMEND" "$SCRATCH/nc3/"`; find the `**Date:** 2026-08-21`
      line INSIDE the paste block on the COPY (`grep -n` it, take the occurrence between the two
      markers) and change that ONE line's date to `2026-08-22` with a line-numbered `sed -i`;
      recompute `PB <copy> | md5sum` -> MUST differ from `422f1f28d6a3b76c7657fadec05a0237`. Print
      both md5s side by side. Then `rm -rf "$SCRATCH/nc3"`.

(h) COMMIT — explicit path only, the amendment ALONE:

```
git add .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
git commit -m "docs(quick-260821-jam): pre-paste re-confirmation — PRE_EXECUTE_COMMIT 2689cae→241515b by engine, seven records, paste block byte-identical (422f1f28)"
```
    Then re-run `PB "$AMEND" | md5sum` at HEAD one last time and record it. If the FINAL whole-file
    anchors changed between (f) and the commit, recompute and use the post-commit values.
  </action>
  <verify>
    <automated>AMEND=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md; PBMD5=$(awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$AMEND" | md5sum | cut -d' ' -f1); test "$PBMD5" = 422f1f28d6a3b76c7657fadec05a0237 && test "$(grep -c '241515b5023b2fae52c0ff3a137f566ac4566a5d' "$AMEND")" -eq 2 && test "$(grep -c '2689cae0c0c0666012bf451fcdd10924661bcf02' "$AMEND")" -eq 0 && test "$(grep -c -E '^  [A-Z0-9_]+ = ' "$AMEND")" -eq 21 && test "$(grep -c '{{' "$AMEND")" -eq 0 && bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all "$AMEND" >/dev/null && grep -q 'seven supporting records' "$AMEND" && git diff --quiet HEAD -- "$AMEND" && echo PASS</automated>
  </verify>
  <done>
The amendment at HEAD: paste block 22,945 B / md5 `422f1f28d6a3b76c7657fadec05a0237` (unmoved); the
full 40-hex `241515b5023b2fae52c0ff3a137f566ac4566a5d` at exactly 2 positions and
`2689cae0c0c0666012bf451fcdd10924661bcf02` at 0; 3 occurrences of `2026-08-21`; 21 ledger lines;
0 sentinels; guard `all` EXIT=0; the checklist reads "seven supporting records" and names the Task 1
path; the prose at the table row and at item 4 is true of the new value, with the
RE-CONFIRMED-AT-POSTING sentence verbatim. The SUMMARY carries the dry-run and real SUBSTITUTION
LEDGER stdout, the before/after anchors, and NC-1/NC-2/NC-3 each with command, output and exit code.
Committed, amendment path only.
  </done>
</task>

<task type="auto">
  <name>Task 3: Posting card, STATE + HANDOFF refresh, push to origin</name>
  <files>.planning/debug/260821-POSTING-CARD-occlusion-recalibration.md, .planning/STATE.md, .planning/HANDOFF.json</files>
  <action>
(a) WRITE THE POSTING CARD — `.planning/debug/260821-POSTING-CARD-occlusion-recalibration.md`,
    written for Carter at a terminal, top to bottom, with the FINAL anchors from Task 2(f)/(h)
    substituted in as LITERALS (never a placeholder). Sections:

    1. TRANSFER — one copy-pasteable line, run ON THE MAC:
```
scp ckclinto@login.hpc.ncsu.edu:/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/
```
    2. VERIFY ON THE MAC —
       `cd /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/`, then `wc -c` and
       `md5` (macOS: `md5`, NOT `md5sum`; it prints `MD5 (file) = hash`) on the whole file, which
       must equal the FINAL whole-file anchors. Then extract the paste body:
```
awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' \
    osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
    > osf-amendment-occlusion-gate-recalibration-2026-08-21-POST.md
wc -c osf-amendment-occlusion-gate-recalibration-2026-08-21-POST.md
md5   osf-amendment-occlusion-gate-recalibration-2026-08-21-POST.md
```
       REQUIRE `22945` and `422f1f28d6a3b76c7657fadec05a0237`. Mismatch means STOP, do not post,
       report back. State that the `-POST.md` file is the ONLY thing that goes to OSF — the
       pre-paste reference block, the SLOT_LEDGER, the instantiation record and the checklist all
       live ABOVE the opening marker and must NOT be uploaded.
    3. POST — go to `osf.io/az52u` -> Files -> upload the `-POST.md` as a NEW file, named
       `osf-amendment-occlusion-gate-recalibration-2026-08-21.md`. NEVER use "upload new version"
       on `trsx5`. After upload: confirm `trsx5` STILL shows exactly 1 revision (2026-07-10 13:32).
       Open the new file, copy its GUID and URL, note the upload timestamp in UTC from its
       info/revisions panel, and if OSF displays a checksum/md5 for the stored file, copy that too.
    4. PASTE BACK INTO THE NCSU SESSION — five items: (i) new file GUID; (ii) full URL; (iii) upload
       timestamp in UTC; (iv) `trsx5` revision count after the upload; (v) the OSF-served md5 if
       shown.
    5. DON'TS — an agent never posts and never fires; no hand edits to the amendment (the enforcers
       cannot see an edit made on the Mac); if posting slips past 2026-08-21, STOP and request the
       engine's Class-P `POSTING_DATE` move on the NCSU side (all THREE occurrences move together,
       followed by a `guard all` re-run and refreshed anchors) — NEVER a one-token hand edit; the
       AoU environment stays STOPPED; nothing fires; `_OCCLUSION_ANOMALY_FRACTION` stays 0.0005
       until the amendment is posted AND the two-part change is planned.

(b) STATE.md — replace the top resume block. Do NOT append a Quick Tasks row: the orchestrator's
    Step 7 owns that table and adding one here would double-count.
    * Demote the current top block: change its trailing `(★ RESUME HERE — LATEST ★)` to
      `(SUPERSEDED by the 2026-08-21 AFTERNOON block above; preserved in place)`.
    * Insert a NEW block immediately above it, headed
      `## 2026-08-21 AFTERNOON — ...  (★ RESUME HERE — LATEST ★)`, stating: Seth's FINAL PASS banked
      as the SEVENTH supporting record (no blocking objection; he verified both anchors himself off
      Carter's local copy, so no transfer risk); the pre-paste re-confirmation DONE;
      `PRE_EXECUTE_COMMIT` moved `2689cae` -> `241515b-` BY THE ENGINE at both occurrences;
      `POSTING_DATE` re-confirmed to 2026-08-21 (unchanged); the amendment is READY TO POST; paste
      block 22,945 B / `422f1f28d6a3b76c7657fadec05a0237` UNCHANGED; whole-file = the FINAL anchors;
      guard `all` GREEN; `_OCCLUSION_ANOMALY_FRACTION` still 0.0005 in code; nothing running, VM
      stopped, $0.
    * A `**▶ NEXT:**` line — (i) Carter posts the NEW file on `osf.io/az52u` per
      `.planning/debug/260821-POSTING-CARD-occlusion-recalibration.md` (`trsx5` untouched, still
      exactly 1 revision); (ii) the record quick task (`.planning/osf_deviations.md` entry +
      DEC-posted + HANDOFF gate closed) once Carter pastes back GUID/URL/UTC; (iii) the remediation
      batch (two-condition producer gate, oracle re-derivation, `fire_verifier` semantics, runbook
      EXPECTs, suite re-baseline) — AFTER posting only; (iv) Stage A. AN AGENT NEVER POSTS AND NEVER
      FIRES.
    * Refresh the `last_updated` and `last_activity` frontmatter fields at the top of the file.
      Leave the long historical `status` field alone.

(c) HANDOFF.json — PREPEND a new `resume_on_reconnect[0]`. The entries are plain STRINGS in the
    existing `"> #0 (...)"` shape; keep that shape. Content: everything in (b) plus BOTH anchor
    pairs (whole-file and paste-block) and the posting-card path, marked as SUPERSEDING the previous
    #0. Do a TARGETED textual insertion — a full `json.load`/`json.dump` round-trip would reformat
    the whole file, which mixes `\u`-escaped and literal non-ASCII:

```
python3 - <<'PY'
import json
p = ".planning/HANDOFF.json"
raw = open(p, encoding="utf-8").read()
entry = json.dumps("> #0 (2026-08-21 AFTERNOON ...)", ensure_ascii=False)   # full text here
m = '  "resume_on_reconnect": [\n'
assert raw.count(m) == 1
open(p, "w", encoding="utf-8").write(raw.replace(m, m + "    " + entry + ",\n", 1))
PY
python3 -m json.tool .planning/HANDOFF.json > /dev/null && echo JSON-OK
python3 -c "import json;d=json.load(open('.planning/HANDOFF.json'));print(len(d['resume_on_reconnect']));print(d['resume_on_reconnect'][0][:120])"
```
    Expect 16 entries and the new one at index 0. Also update the top-level `"timestamp"` field to
    the current UTC time. Verify the diff is bounded: `git diff --stat .planning/HANDOFF.json` must
    show a small line count, not a whole-file rewrite — if it does not, revert and redo.

(d) COMMIT + PUSH — explicit paths only:

```
git add .planning/STATE.md .planning/HANDOFF.json .planning/debug/260821-POSTING-CARD-occlusion-recalibration.md
git commit -m "docs(quick-260821-jam): posting card + handoff — amendment READY TO POST, Carter posts, agent never posts"
git push
git status -sb | head -1
```
    The first line of `git status -sb` must show NO `ahead` marker (origin is SSH; no PAT needed).
    If the GPFS object store drops loose objects mid-commit, follow the recovery recipe in
    HANDOFF.json's `gpfs_object_store_recovery_recipe` and retry — never work around it by
    re-staging with `-A`.

Zero OSF contact of any kind in this task: no browser, no API, no upload, no check of the live site.
Zero VM/perimeter contact. The card is written FOR Carter; it is not executed.
  </action>
  <verify>
    <automated>test -f .planning/debug/260821-POSTING-CARD-occlusion-recalibration.md && grep -q '422f1f28d6a3b76c7657fadec05a0237' .planning/debug/260821-POSTING-CARD-occlusion-recalibration.md && grep -q 'osf.io/az52u' .planning/debug/260821-POSTING-CARD-occlusion-recalibration.md && grep -q 'trsx5' .planning/debug/260821-POSTING-CARD-occlusion-recalibration.md && python3 -m json.tool .planning/HANDOFF.json >/dev/null && python3 -c "import json,sys;d=json.load(open('.planning/HANDOFF.json'));sys.exit(0 if '2026-08-21 AFTERNOON' in d['resume_on_reconnect'][0] else 1)" && grep -q '2026-08-21 AFTERNOON' .planning/STATE.md && git diff --quiet HEAD -- .planning/STATE.md .planning/HANDOFF.json .planning/debug/260821-POSTING-CARD-occlusion-recalibration.md && ! git status -sb | head -1 | grep -q 'ahead' && echo PASS</automated>
  </verify>
  <done>
The posting card exists and carries the scp line, the macOS `md5` verification against the FINAL
anchors, the awk `-POST.md` extraction with its 22945 / `422f1f28d6a3b76c7657fadec05a0237` STOP-gate,
the NEW-file-not-a-trsx5-revision sequence with the 1-revision post-check, the five paste-back items
and the DON'Ts. STATE.md's top block is the 2026-08-21 AFTERNOON ★ RESUME HERE ★ block and the
previous block is marked SUPERSEDED; no Quick Tasks row was added. HANDOFF.json is valid JSON with
the new entry at `resume_on_reconnect[0]` and a bounded diff. All three files are committed by
explicit path and pushed; `git status -sb` shows no `ahead`.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Seth (external reviewer) -> repo | Prose arriving through a paste channel, banked as a permanent record |
| Repo -> OSF (public, append-only, irreversible) | The paste block becomes a public pre-registration record the moment Carter uploads it |
| Repo (NCSU/GPFS) -> Carter's Mac -> OSF | The bytes traverse two hops before posting; only anchors survive the trip |
| Agent -> OSF / AoU perimeter | HARD BOUNDARY — an agent never posts and never fires |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-jam-01 | Tampering | The paste block Seth cleared | mitigate | `awk` extraction md5 `422f1f28...` asserted BEFORE the engine, AFTER the engine, AFTER the prose edits and at HEAD; NC-3 proves the assertion can fail |
| T-jam-02 | Tampering | `PRE_EXECUTE_COMMIT` drifting between its 2 occurrences | mitigate | Moved ONLY by the engine's document-wide Class-P force-substitution, which asserts old-count == new-count and old-literal-gone; never a hand edit; NC-2 proves it hits exactly 2 |
| T-jam-03 | Repudiation | "Seth cleared it" asserted without evidence | mitigate | Verdict banked verbatim, body md5 `6ddb3fb5...` proven against the staged transcription; the header records that HE verified both anchors off the local repo copy |
| T-jam-04 | Information disclosure | Internal `.planning/` paths or the SLOT_LEDGER reaching the public OSF record | mitigate | Only the `-POST.md` extraction (strictly between the markers) is uploaded; the posting card says so explicitly; Seth verified the collinearity path sits after `--- PASTE ENDS HERE ---` |
| T-jam-05 | Elevation of privilege | An agent posting to OSF or firing the AoU pipeline | mitigate | Task 3 writes a card FOR Carter and executes nothing; zero OSF and zero perimeter contact is a stated constraint of every task |
| T-jam-06 | Tampering | Overwriting `trsx5` with "upload new version" instead of posting a NEW file | mitigate | The card names the trap twice and adds a post-upload check that `trsx5` still shows exactly 1 revision |
| T-jam-07 | Spoofing | A stale or altered file reaching OSF after two transfer hops | mitigate | Whole-file AND paste-block anchors re-verified on the Mac with `md5` before upload; a mismatch is a hard STOP |
| T-jam-08 | Denial of service | GPFS loose-object loss aborting a commit mid-task | accept | Known and recoverable; HANDOFF.json carries the recovery recipe; each task is a single explicit-path commit so a retry is cheap |
| T-jam-09 | Tampering | A POSTING_DATE slip repaired by a one-token hand edit, drifting the 3 occurrences | mitigate | The card forbids it and routes any slip back to the engine's Class-P pass plus `guard all` |
</threat_model>

<verification>
At HEAD after all three tasks, from the repo root:

```
AMEND=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
PB() { awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$1"; }

PB "$AMEND" | wc -c                                            # 22945
PB "$AMEND" | md5sum                                           # 422f1f28d6a3b76c7657fadec05a0237
grep -c '241515b5023b2fae52c0ff3a137f566ac4566a5d' "$AMEND"    # 2
grep -c '2689cae0c0c0666012bf451fcdd10924661bcf02' "$AMEND"    # 0
grep -c '2026-08-21' "$AMEND"                                  # 3
grep -c '{{' "$AMEND"                                          # 0
grep -c -E '^  [A-Z0-9_]+ = ' "$AMEND"                         # 21
bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all "$AMEND"; echo "EXIT=$?"   # GREEN / 0
grep -n '_OCCLUSION_ANOMALY_FRACTION = 0.0005' src/python/run_native_ld_panel.py                                                       # :133
git diff --stat 2689cae HEAD -- src/ tests/ config/ | wc -l    # 0
git status -sb | head -1                                       # no 'ahead'
python3 -m json.tool .planning/HANDOFF.json > /dev/null; echo "EXIT=$?"                                                                # 0
```

Plus, per Task 1's proof: the region of the banked record below its `---` separator has md5
`6ddb3fb56c269303f1478c976a6d6509`.

Every green above must be paired with a red seen this session: NC-1 (the guard catches a sentinel),
NC-2 (the Class-P replace really moves exactly 2 occurrences), NC-3 (the paste-block md5 really
changes when a byte inside the block changes). A green with no observed red is not evidence.
</verification>

<success_criteria>
- Seth's final pass is the SEVENTH committed supporting record, its body byte-identical to the
  staged transcription (md5 `6ddb3fb5...`), under a house-style provenance header recording the
  no-transfer-risk provenance, the four dispositions, his two NOT-asserted-done items and his
  verbatim status line.
- The amendment's own standing pre-paste instruction has been executed: `PRE_EXECUTE_COMMIT` pins
  `241515b5023b2fae52c0ff3a137f566ac4566a5d` at both occurrences, moved by the engine; the
  superseded 40-hex literal is gone; `POSTING_DATE` re-confirmed to 2026-08-21.
- The 22,945-byte body Seth cleared is byte-identical (`422f1f28d6a3b76c7657fadec05a0237`) — proven
  before the engine, after the engine, after the prose edits, and at HEAD.
- The three prose statements the move made false are true again; the checklist says SEVEN records
  and names the new one; nothing else in the file changed.
- Guard `all` exits 0; 0 sentinels; 21 ledger lines.
- Carter has a turnkey posting card and can post today without asking a question.
- STATE.md and HANDOFF.json point at the posting step; everything is on origin.
- `_OCCLUSION_ANOMALY_FRACTION` is untouched at 0.0005; no `src/`, `tests/` or `config/` file was
  modified; zero OSF contact; zero perimeter contact; nothing fired.
</success_criteria>

<output>
After completion, create
`.planning/quick/260821-jam-bank-seth-final-pass-as-7th-record-pre-p/260821-jam-SUMMARY.md`
carrying, at minimum:
- Task 1's header line count and the tail-md5 proof.
- Task 2's before / after-engine / after-prose anchor triples (whole-file and paste-block).
- The engine's dry-run and real SUBSTITUTION LEDGER stdout, verbatim, including the CLASS-P block.
- NC-1 / NC-2 / NC-3: command, output, exit code, and the quoted failing line for each.
- The FINAL anchors as published in the posting card.
- The `2689cae` short-form prose mention count with line numbers, explicitly characterized as
  historical references rather than slot values.
</output>
