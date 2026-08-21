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
    - "Seth's final pass is banked as the seventh supporting record with its substance verbatim: the NON-BLANK content below the record's `---` separator has md5 972fbac405a9a5073ea0bd366da2dc34 — identical in content AND in order to the staged transcription, no paraphrase. The two renderings differ ONLY in blank-line placement (both 54 lines / 6,665 B; identical line multiset), and the committed artifact is left byte-untouched."
    - "The amendment is paste-gated GREEN at HEAD: the guard's `all` section exits 0 and zero `{{` slot sentinels remain."
    - "Nothing was posted and nothing was fired: _OCCLUSION_ANOMALY_FRACTION is still 0.0005 at src/python/run_native_ld_panel.py:133, git diff --stat 2689cae..HEAD -- src/ tests/ config/ is empty, and no OSF or VM contact of any kind occurred."
    - "The pre-paste checklist's record count is now TRUE: it says SEVEN supporting records and all seven paths are tracked by git."
    - "Everything is on origin: git status -sb reports no `ahead` marker after the push."
  artifacts:
    - path: ".planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md"
      provides: "The SEVENTH supporting record — Seth's final pass, no blocking objection, banked verbatim under a house-style provenance header. ALREADY COMMITTED at d45db42 by a parallel terminal; this plan VERIFIES and RECONCILES it, it does not re-create it."
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

PRE_EXECUTE_COMMIT to write = 241515b5023b2fae52c0ff3a137f566ac4566a5d
  This is HEAD *immediately before the first commit of this posting-prep task* — which is the
  quantity the pre-paste table row is defined to carry. It is NOT current HEAD: while this plan
  was being written a parallel terminal committed d45db42 (banking Seth's final pass) and this
  plan itself committed 36006c5, so HEAD has advanced past it. Do NOT "correct" the value to
  current HEAD — 241515b is the tree Seth's clearance was given against, and the banked record
  says so in its own header ("the amendment he read is the 42,213 B / e1b4a11d... file at commit
  241515b"). Both later commits are docs-only; re-prove that, do not assume it.
PRE-EMPTED WORK: .planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
  ALREADY EXISTS and is committed (d45db42, 70 lines / 7,770 B / md5 20921ab9426c2169a2753749d3800934,
  `---` separator at line 15). Its body is NOT byte-identical to the staged transcription, but its
  NON-BLANK content is identical in content and order (md5 972fbac405a9a5073ea0bd366da2dc34, both
  54 lines / 6,665 B, identical line multiset) — the two differ ONLY in blank-line placement.
  Task 1 is therefore a VERIFY-AND-RECONCILE task, not a write.
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
  <name>Task 1: Verify and reconcile the already-banked seventh supporting record</name>
  <files>.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md</files>
  <action>
PRE-EMPTED — READ THIS FIRST. While this plan was being written, a parallel terminal banked Seth's
final pass and committed it as `d45db42`. The record EXISTS and is TRACKED. This task therefore
VERIFIES and RECONCILES it. It does NOT re-create it, and it does NOT rewrite it. Re-banking a
committed record to satisfy a plan's md5 would be repairing the check instead of the artifact.

The reconciliation is already characterized (do not take this on trust — re-run it): the committed
body and the staged transcription have IDENTICAL NON-BLANK CONTENT IN IDENTICAL ORDER and an
identical multiset of lines; both are 54 lines / 6,665 B; they differ ONLY in blank-line placement.
So the substantive invariant is a non-blank-content identity, not a whole-file md5.

```
F=.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad
SETH="$SCRATCH/seth-final-pass-verbatim.md"
SEP=$(awk '/^---$/{print NR; exit}' "$F")            # the provenance-header separator; expect 15
BODY() { tail -n +$((SEP+1)) "$F" | grep -v '^[[:space:]]*$'; }
NB()   { grep -v '^[[:space:]]*$' "$1"; }
```

(a) PROVENANCE — `git ls-files --error-unmatch "$F"`; `git log --oneline -1 -- "$F"` (expect
    `d45db42`); `wc -c -l "$F"`; `md5sum "$F"`. Record all four. Expect 70 lines / 7,770 B /
    `20921ab9426c2169a2753749d3800934` and `SEP=15`; if `SEP` is not the provenance separator,
    STOP — the file's shape changed and the checks below would be measuring the wrong region.

(b) STAGED SOURCE — `wc -c -l "$SETH"; md5sum "$SETH"` -> 6,665 B / 54 lines /
    `6ddb3fb56c269303f1478c976a6d6509`. If the staged file is gone or moved, say so plainly and
    fall back to (c)'s absolute md5 alone; do NOT invent a substitute source.

(c) SUBSTANCE IDENTITY — the decisive check:
    `BODY | md5sum` MUST be `972fbac405a9a5073ea0bd366da2dc34`, and
    `NB "$SETH" | md5sum` MUST be the same value. A must-be-identity comparison, chosen over a
    must-look-similar reading.

(d) CHARACTERIZE THE DELTA, do not hide it. Run and transcribe:
    * `diff <(NB "$SETH") <(BODY)` -> EMPTY (identical content, identical order)
    * `diff <(sort "$SETH") <(tail -n +$((SEP+1)) "$F" | sort)` -> report the result; the only
      permissible difference is blank lines
    * `diff "$SETH" <(tail -n +$((SEP+1)) "$F")` -> NON-empty; quote it, and state in the SUMMARY
      that every hunk is a blank line moving position (plus the one-position move of the
      `fraction ratio = count ratio x (n_sites / n_rows)` line relative to its blank neighbours),
      with net zero lines and net zero bytes.
    Conclusion to record: the committed record is substantively verbatim; the whole-file md5 differs
    from the staged copy for whitespace-layout reasons only. Neither rendering is privileged —
    Seth supplied no byte anchors — so the COMMITTED one stands and is not disturbed.

(e) COMPLETENESS — confirm by `grep -c -F` that the record carries, in header or body:
    `measurement banked; amendment drafted, NOT posted` (his verbatim status line);
    `never posts and never fires`; `two-part change`; `1.1205`; `3.42x`; `1.91x`;
    `I would not have it softened` (his ask that the section-4 self-attribution stand);
    `Seventh supporting record`. Report each count.
    If and ONLY if something required is genuinely absent, append it to the PROVENANCE HEADER
    (above the `---`) — never to the body — and commit by explicit path with
    `docs(quick-260821-jam): complete the provenance header on the seventh record`. Otherwise this
    task produces NO commit, and that is the correct outcome.

(f) Confirm the working tree is untouched by this task: `git diff --quiet HEAD -- "$F"` exits 0.
  </action>
  <verify>
    <automated>F=.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md; SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad; SEP=$(awk '/^---$/{print NR; exit}' "$F"); git ls-files --error-unmatch "$F" >/dev/null && test "$(tail -n +$((SEP+1)) "$F" | grep -v '^[[:space:]]*$' | md5sum | cut -d' ' -f1)" = 972fbac405a9a5073ea0bd366da2dc34 && diff <(grep -v '^[[:space:]]*$' "$SCRATCH/seth-final-pass-verbatim.md") <(tail -n +$((SEP+1)) "$F" | grep -v '^[[:space:]]*$') >/dev/null && grep -q -F 'measurement banked; amendment drafted, NOT posted' "$F" && grep -q -F 'I would not have it softened' "$F" && git diff --quiet HEAD -- "$F" && echo PASS</automated>
  </verify>
  <done>
`.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md` is confirmed tracked at
`d45db42`; the non-blank content below its `---` separator has md5
`972fbac405a9a5073ea0bd366da2dc34` and diffs EMPTY in content and order against the staged
transcription; the whole-file delta is characterized in the SUMMARY as blank-line placement only,
with the three diffs quoted; the completeness greps are recorded; the record carries Seth's verbatim
status line and his "I would not have it softened" ask. The committed artifact was NOT rewritten and
the working tree is clean for that path.
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
    2. `git log --oneline 2689cae..HEAD` — LIST whatever is there rather than pinning a count: at
       planning time it was b4263e7, a364d19, cd0cdfd, 241515b (the four that superseded `2689cae`),
       plus d45db42 (the banked seventh record) and 36006c5 (this plan). Every one must be docs-only.
       Prove it, do not assume it: `git diff --stat 2689cae HEAD -- src/ tests/ config/ | wc -l`
       -> 0; `grep -n '_OCCLUSION_ANOMALY_FRACTION = 0.0005' src/python/run_native_ld_panel.py`
       -> hit at line 133.
       NOTE for step (e)(i): the phrase "advanced by four docs-only commits" describes the span
       `2689cae`..`241515b` specifically, and is exactly true. Do not "update" it to the current
       total — the pre-paste row records why `2689cae` was superseded BY `241515b`, not how far the
       branch has run since.
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

Plus, per Task 1's proof: the NON-BLANK content of the banked record below its `---` separator has
md5 `972fbac405a9a5073ea0bd366da2dc34` and diffs EMPTY against the staged transcription's non-blank
content, in order.

Every green above must be paired with a red seen this session: NC-1 (the guard catches a sentinel),
NC-2 (the Class-P replace really moves exactly 2 occurrences), NC-3 (the paste-block md5 really
changes when a byte inside the block changes). A green with no observed red is not evidence.
</verification>

<success_criteria>
- Seth's final pass is the SEVENTH committed supporting record (landed `d45db42`), verified rather
  than re-created: its non-blank content is identical in content and order to the staged
  transcription (md5 `972fbac4...`), the whole-file delta is characterized as blank-line placement
  only, and the record carries the no-transfer-risk provenance, the four dispositions, his two
  NOT-asserted-done items, his "I would not have it softened" ask and his verbatim status line.
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
- Task 1's reconciliation: the three diffs, the `972fbac4...` substance identity, the
  completeness greps, and the explicit statement that the committed record was not rewritten.
- Task 2's before / after-engine / after-prose anchor triples (whole-file and paste-block).
- The engine's dry-run and real SUBSTITUTION LEDGER stdout, verbatim, including the CLASS-P block.
- NC-1 / NC-2 / NC-3: command, output, exit code, and the quoted failing line for each.
- The FINAL anchors as published in the posting card.
- The `2689cae` short-form prose mention count with line numbers, explicitly characterized as
  historical references rather than slot values.
</output>
