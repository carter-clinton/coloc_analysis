---
phase: quick-260821-jcs
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: pre-registration
tags: [osf, amendment, occlusion, posting-prep, re-confirmation, class-p, pre-execute-commit, guard, seth-final-pass, posting-card, m3-07]

files_modified:
  - .planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
  - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  - .planning/debug/260821-POSTING-CARD-for-carter.md
  - .planning/STATE.md
  - .planning/HANDOFF.json
  - .planning/quick/260821-jcs-bank-seth-s-final-pass-re-confirmed-at-p/260821-jcs-PLAN.md
  - .planning/quick/260821-jcs-bank-seth-s-final-pass-re-confirmed-at-p/260821-jcs-SUMMARY.md

autonomous: true

requirements:
  - DEC-2026-08-19-occlusion-recalibration-adopted
  - OSF-AMEND-OCCLUSION-BANK-SETH-FINAL-PASS
  - OSF-AMEND-OCCLUSION-RECONFIRM-AT-POSTING
  - OSF-AMEND-OCCLUSION-POSTING-CARD

user_setup: []

must_haves:
  truths:
    - "The body Carter pastes is byte-identical to the body Seth verified: the region between the two PASTE markers, exclusive of both, is still 22,945 B / md5 422f1f28d6a3b76c7657fadec05a0237 at EVERY commit this task makes."
    - "The amendment's own standing RE-CONFIRMED-AT-POSTING instruction has been EXECUTED, not merely quoted: PRE_EXECUTE_COMMIT is the 40-hex HEAD as of after Seth's final pass was banked, it appears at exactly its two occurrences, and it got there through the engine's Class-P force substitution — no agent typed a hash into the document."
    - "The precondition the instruction names was re-measured rather than assumed: every commit between the superseded gate hash and the new one is docs-only, the src/ tests/ config/ diff across that span is empty, and the shipped `_OCCLUSION_ANOMALY_FRACTION = 0.0005` is untouched."
    - "Seth's final pass is in git byte-identical to the transcription Carter's paste produced (cmp silent against the scratchpad source), and the amendment's pre-paste checklist now counts SEVEN supporting records and names its path — while the three 'six NaN pairs' statements, a different quantity, are untouched."
    - "POSTING_DATE is still 2026-08-21 at exactly three occurrences and it moved through the engine's argv, not a hand edit; the amendment's instantiation-date basename and its in-text 2026-08-20 references did not move with it."
    - "The green is evidence because it was seen red IN THIS TASK: a re-introduced {{SLOT}} sentinel drives `guard all` to a non-zero exit on the same fixture that exits 0 unperturbed, and a single perturbed per-region table value drives the engine's RECONCILIATION to a non-zero exit on the same command that exits 0 unperturbed."
    - "Carter can post without an agent in the loop: the posting card carries the fresh anchors, the Mac-side scp + awk + md5 commands, the NEW-file-on-az52u procedure with the trsx5 prohibition, the four post-upload captures the prepared deviation entry needs, what to paste back, and the if-it-slips rule that routes a date change through the engine rather than a hand edit."
    - "Nothing was posted and nothing was fired: no OSF contact, no VM action, `src/ tests/ config/` untouched, `.planning/osf_deviations.md` byte-unchanged, and the status line 'an agent never posts and never fires' is carried into the card."
  artifacts:
    - path: ".planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md"
      provides: "The seventh supporting record — Seth's final pass, as received, banked by copy not by re-typing"
      contains: "no blocking objection"
      min_lines: 60
    - path: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      provides: "The re-confirmed amendment: advanced Class-P gate hash, corrected provenance prose, seven-record checklist, paste block byte-frozen"
      contains: "RE-CONFIRMED AT POSTING"
    - path: ".planning/debug/260821-POSTING-CARD-for-carter.md"
      provides: "Human-driven posting procedure with anchors, Mac commands, OSF steps, post-upload captures, if-it-slips rule"
      contains: "422f1f28d6a3b76c7657fadec05a0237"
      min_lines: 60
    - path: ".planning/STATE.md"
      provides: "New 2026-08-21 AFTERNOON top block; the MORNING block demoted to superseded-in-place"
      contains: "2026-08-21 AFTERNOON"
    - path: ".planning/HANDOFF.json"
      provides: "New resume_on_reconnect[0] carrying the re-confirmation, the fresh anchors and the post-then-record-then-remediate order"
      contains: "260821-POSTING-CARD-for-carter.md"
  key_links:
    - from: "git HEAD after the Task-1 banking commit"
      to: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      via: "260820-s2x-instantiate.py --second-pass Class-P force substitution at both occurrences"
      pattern: "PRE_EXECUTE_COMMIT = [0-9a-f]{40}"
    - from: ".planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md"
      to: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      via: "pre-paste checklist item 3 — seven supporting records, path named"
      pattern: "260821-SETH-FINAL-PASS-no-blocking-objection-as-received\\.md"
    - from: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      to: ".planning/debug/260821-POSTING-CARD-for-carter.md"
      via: "paste-block extraction anchors carried onto the card for Mac-side re-verification"
      pattern: "422f1f28d6a3b76c7657fadec05a0237"
    - from: ".planning/debug/260821-POSTING-CARD-for-carter.md"
      to: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      via: "OSF upload filename carries the POSTING date, matching the prepared deviation entry's template; the repo basename keeps the INSTANTIATION date"
      pattern: "osf-amendment-occlusion-gate-recalibration-2026-08-21\\.md"
    - from: ".planning/STATE.md + .planning/HANDOFF.json"
      to: ".planning/debug/260821-POSTING-CARD-for-carter.md"
      via: "the RESUME sequence points at the card as Carter's next action"
      pattern: "260821-POSTING-CARD-for-carter\\.md"
---

<objective>
Bank Seth's final pass (no blocking objection) as the seventh supporting record, EXECUTE the
amendment's own standing RE-CONFIRMED-AT-POSTING instruction by advancing `PRE_EXECUTE_COMMIT`
through the engine's Class-P pass, correct the three prose statements that the advance makes
untrue, and write Carter a posting card he can drive alone.

Purpose: the amendment carries a rule about itself — "re-read HEAD, confirm no gate-constant
change has landed since, and update this value if the branch has advanced." The branch HAS
advanced, by docs-only commits, and banking Seth's verdict adds one more. A rule that is quoted
but not executed at the moment it applies is exactly the class of lapsed obligation this whole
amendment package exists to prevent. This task executes it, and does so through the engine
because a hash typed by an agent has no provenance.

Output: one banked record, one re-confirmed amendment whose POSTED BODY DID NOT MOVE, one
posting card, and a STATE/HANDOFF handoff that names the post → record → remediate → Stage A
order.

The single hard invariant, restated because everything else is subordinate to it: the paste
block stays **22,945 B / `422f1f28d6a3b76c7657fadec05a0237`**. That identity is the proof that
Carter posts exactly the bytes Seth verified. If it moves, this task has failed regardless of
what else went green.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/quick/260821-jcs-bank-seth-s-final-pass-re-confirmed-at-p/260821-jcs-BRIEF.md
@.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
@.planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
@.planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
@.planning/debug/260820-site-basis-sweep-results-as-received.md
@.planning/quick/260820-u6i-revise-the-instantiated-amendment-per-se/260820-u6i-SUMMARY.md

<interfaces>
<!-- Every contract, path, anchor and command this task needs. Measured read-only at plan time,
     2026-08-21, at HEAD 241515b, tree clean, origin == local. Do NOT go hunting in the
     codebase for these; they are here. Re-measure them, do not re-derive them. -->

REPO ROOT (all relative paths below are from here; the engine hard-codes its source paths
relative to the repo root, so it MUST be invoked from there):
  /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

SCRATCHPAD (all negative-control fixtures live here — NEVER in the repo tree):
  /gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad

THE AMENDMENT (the one file this task edits under .planning/amendments/):
  .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  PRE-TASK anchors, measured at plan time — assert these BEFORE any edit:
    whole file  42,213 B / e1b4a11d18ad2907af4f0a93fd5747d2 / 591 lines
    paste block 22,945 B / 422f1f28d6a3b76c7657fadec05a0237   <- INVARIANT, must not move
  Line map (may shift by the prose edits; locate by content, never by number):
    63   pre-paste table row  | Pre-execute commit gate | `<40-hex>` — … RE-CONFIRMED AT POSTING: …
    64   pre-paste table row  | Expected posting date | `2026-08-21` — **PROVISIONAL**. …
    91   SLOT_LEDGER          POSTING_DATE = 2026-08-21
    92   SLOT_LEDGER          PRE_EXECUTE_COMMIT = <40-hex>
    139-145 instantiation record item 4 (the Class-P paragraph)
    157  pre-paste checklist item 3 ("the six supporting records")
    164  --- PASTE INTO OSF FROM HERE ---     <- marker, EXCLUSIVE of the block
    168  **Date:** 2026-08-21                 <- INSIDE the block; only the engine touches it
    498  --- PASTE ENDS HERE ---              <- marker, EXCLUSIVE of the block
    499+ Post-Paste Reference + the PREPARED, NOT-YET-APPENDED deviations entry
  Occurrence census at plan time:
    2689cae0c0c0666012bf451fcdd10924661bcf02 : 2   (line 63 row, line 92 ledger)
    '2689cae' (any form)                     : 2   (the same two — the short form appears NOWHERE)
    '2026-08-21'                             : 3   (line 64 row, line 91 ledger, line 168 Date)
    '{{'                                     : 0
    '\bsix\b'                                : 4   (157 checklist; 215/230/555 = the six NaN PAIRS)

PASTE-BLOCK EXTRACTION (the exact awk — marker lines excluded by construction):
  awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' <amendment>

THE ENGINE (do NOT edit it; this task is a CONSUMER):
  .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
  Class-M (19 MEASURED slots) under --second-pass: an already-filled ledger value is VERIFIED
    byte-identical against fresh recomputation from the banked records; ANY drift ABORTS.
  Class-P (POSTING_DATE, PRE_EXECUTE_COMMIT) are argv-sourced and FORCE-SUBSTITUTED document-wide.
  Banked sources, hard-coded (not arguments) — that is the point:
    .planning/debug/260820-site-basis-sweep-results-as-received.md   (site basis + inflation col)
    .planning/debug/260819-occ-measure-sweep-results-as-received.md  (row basis)
  Write invocation (this task's):
    python3 .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py \
            --second-pass \
            .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
            --pre-execute-commit <NEW-40-HEX> --posting-date 2026-08-21
  Control invocation (forces --dry-run; write path disabled; cannot be combined with --second-pass):
    python3 <engine> --dry-run --control-source <perturbed copy of the site-basis record>
  Expected stdout sections: RECONCILIATION → ROW-BASIS RECONCILIATION → PRE-REGISTERED RENDER
    EXPECTATIONS → RENDER CHECK (21 of 21) → CLASS-M DRIFT VERIFY → Class-P FORCE-SUBSTITUTED.
  EXPECTED THIS RUN: 19 VERIFIED-IN-PLACE, 0 SUBSTITUTED, 2 FORCE-SUBSTITUTED, exit 0.

THE GUARD (do NOT edit it; this task is a CONSUMER):
  bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh \
       all .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  Sections: draft | paste-ready | arith | quote | all. Exit 0 = every check PASSED.
  It locates the PASTE markers by grep, not by line number, so prose edits OUTSIDE the markers
  do not perturb it. It counts SLOT_LEDGER lines by an anchored `NAME = value` pattern; the
  checklist prose this task edits does not match that pattern.

THE SOURCE TO BANK (transcribed byte-faithfully at plan time; cp it, never re-type it):
  <SCRATCHPAD>/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
  7,770 B / 20921ab9426c2169a2753749d3800934 / 70 lines

REPO FACTS re-measured at plan time (re-measure, do not trust):
  HEAD                     241515b5023b2fae52c0ff3a137f566ac4566a5d
  branch                   m3-W2-aou-deltas ; origin == local
  git log --oneline 2689cae..HEAD   241515b, cd0cdfd, a364d19, b4263e7   (4, all docs-only)
  git diff --stat 2689cae HEAD -- src/ tests/ config/    EMPTY
  src/python/run_native_ld_panel.py:133  _OCCLUSION_ANOMALY_FRACTION = 0.0005

NEGATIVE-CONTROL PERTURBATION TARGET (site-basis record, per-region table, 4-space indent;
columns: region_id n_rows n_sites occ_rows occ_sites row_frac_pct site_frac_pct inflation):
      m2_region_00042         43690   41515   119  112  0.2724  0.2698  1.06
  Perturb the 7th field (site_frac_pct) 0.2698 -> 0.2599 on THAT ROW ONLY. The printed summary
  line `max=0.2698%` then no longer re-derives from its own column and RECONCILIATION aborts.
  A GLOBAL sed would also rewrite the summary, keeping them consistent and DEFEATING the control.

MAC-SIDE (for the posting card; Carter drives, no agent):
  login  ckclinto@login.hpc.ncsu.edu
  dest   /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/
  hashing is macOS `md5`, NOT `md5sum`
  OSF filename carries the POSTING date: osf-amendment-occlusion-gate-recalibration-2026-08-21.md
  Repo basename keeps the INSTANTIATION date: …-2026-08-20.md. These are DIFFERENT quantities.
  The hand-paste precedent that must not repeat: .planning/osf_deviations.md lines 190-300.
</interfaces>
</context>

<constraints>
DOCS-ONLY. This task is a consumer of the engine and the guard, not an author of either.
- FORBIDDEN: any edit under `src/`, `tests/`, `config/`, `Snakefile`, the ox1 runbooks, the
  posted July amendment, `.planning/osf_deviations.md`, `.planning/ROADMAP.md`.
- FORBIDDEN: editing `260820-s2x-instantiate.py` or `260819-u8d-placeholder-guard.sh`. If the
  engine aborts or the guard goes red on something that is not a declared step of this plan,
  STOP AND REPORT. Do not repair either tool to make this task pass.
- FORBIDDEN: any OSF contact of any kind. An agent never posts. Carter posts.
- FORBIDDEN: any AoU / VM / cluster action. An agent never fires. Nothing in this task costs money.
- FORBIDDEN: hand-typing or hand-editing a NUMBER inside the amendment. Every value in the
  SLOT_LEDGER, every measured quantity, `POSTING_DATE` and `PRE_EXECUTE_COMMIT` all move ONLY
  through the engine. Prose OUTSIDE the PASTE markers may be hand-edited, and only as this plan
  specifies. Inside the markers: nothing by hand, ever.

⚠ THE ONE TRAP THAT WILL BITE. The prose edit must enumerate the docs-only commits BETWEEN the
old gate hash and the new one — and the verification asserts `grep -c '2689cae' <amendment>` == 0.
Those are compatible ONLY if the new prose never writes the string `2689cae` (in any length) and
never quotes a command containing it. Enumerate the commits AFTER it (b4263e7, a364d19, cd0cdfd,
241515b, plus the banking commit — read them from `git log --oneline 2689cae..HEAD`, do not
assume the list) and refer to the superseded value as "the revising task's value". If you write
`2689cae` into the file, the verify fails and the fix is a second edit, not a loosened assertion.

ORDERING (get this exactly right — it is the difference between a re-confirmation and a lie):
  1. Task 1 commits the banked verdict.
  2. THEN `git rev-parse HEAD` — that 40-hex is `PRE_EXECUTE_COMMIT`.
  3. THEN the engine writes it into the amendment.
  4. THEN the amendment-editing commit.
  The gate hash must be the HEAD *after* banking and *before* the amendment edit. Capturing it
  before step 1, or after step 4, both produce a hash the document's own sentence does not describe.

POSTING_DATE stays `2026-08-21` at all three occurrences. It is nonetheless passed to the engine
explicitly (`--posting-date 2026-08-21`): Class-P is force-substituted from argv, so omitting it
is not "leaving it alone", it is an error. The substitution is a value-preserving no-op and the
engine will report 3 occurrences.

GPFS / staging:
- No worktrees. Explicit-path staging ONLY — never `git add .`, never `git add -A`. The tree
  carries ~15 untracked results/backup directories that must stay untracked.
- GPFS object-store contingency: if a commit fails with "invalid object" / "Error building
  trees", run the guarded `git hash-object -w` recovery loop over the staged paths and retry the
  commit ONCE. Twice failing = STOP and report.

Evidence discipline:
- A green is evidence ONLY if it has been seen red. Both negative controls are RE-EXECUTED in
  this task, on fixtures built in this task, with the command and the non-zero exit transcribed
  into the SUMMARY. A transcript copied from a previous task's SUMMARY does not satisfy this.
- Each control is a 2-cell matrix on the SAME fixture path: unperturbed → exit 0, perturbed →
  non-zero. One cell alone does not attribute the red.
- Control fixtures live in the scratchpad and are NEVER staged.

Commits: exactly the messages this plan gives, atomic, explicit paths. Task 5's `git push` is
explicitly authorised by the BRIEF for this task (the usual "an executor never pushes" rule is
suspended here by the orchestrator's instruction, and only here).
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Bank Seth's final pass as the seventh supporting record, by copy and not by re-typing</name>

  <files>
.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md   (create — cp target)
  </files>

  <action>
Seth's verdict has already been transcribed byte-faithfully, with an as-received provenance
header, into the session scratchpad. Prose survives a re-type; byte anchors do not, and this file
is about to become the seventh entry in a checklist that a public record depends on. So it is
banked by `cp` and proven by `cmp`, never by opening it in an editor.

1. Assert the source is the file this plan measured, BEFORE copying:

```
SRC=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
wc -c "$SRC"; wc -l "$SRC"; md5sum "$SRC"
```

   Expect 7770 B / 70 lines / `20921ab9426c2169a2753749d3800934`. If ANY of the three differs,
   STOP AND REPORT — the source moved since planning and the thing you would bank is not the
   thing that was reviewed. Do not "fix" it forward.

2. Copy and prove byte-identity. `cmp` must print NOTHING and exit 0:

```
DST=.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
cp "$SRC" "$DST"
cmp "$SRC" "$DST"; echo "CMP EXIT=$?"
wc -c "$DST"; wc -l "$DST"; md5sum "$DST"
```

3. Do NOT edit the banked body — not the headings, not the provenance header, not a reflow, not
   a trailing newline. Its two load-bearing properties for downstream steps are that Seth
   verified both file anchors himself against the Mac repo copy (so this is the first review on
   the thread with no transfer risk), and that he names two things explicitly NOT his: Carter
   posts, and the POSTING_DATE re-confirmation. Both are honoured by Tasks 2 and 3.

4. Confirm nothing else got swept in, then commit with EXPLICIT paths only:

```
git status --porcelain -- .planning/debug/ | head
git add .planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
git commit -m "docs(debug): bank Seth's final pass as-received — no blocking objection; seventh supporting record"
git rev-parse HEAD
```

   Record that HEAD — it is the input to Task 2 step 1. Do NOT run any other `git add`.
  </action>

  <verify>
    <automated>
DST=.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
SRC=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
cmp "$SRC" "$DST" && echo "CMP: identical"
test "$(md5sum < "$DST" | cut -d' ' -f1)" = "20921ab9426c2169a2753749d3800934" && echo "MD5: OK"
test "$(wc -c < "$DST")" -eq 7770 && echo "SIZE: OK"
git log -1 --name-only --oneline
git diff --stat HEAD~1 HEAD -- src/ tests/ config/ | wc -l   # MUST print 0
A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$A" | md5sum   # 422f1f28d6a3b76c7657fadec05a0237
    </automated>
  </verify>

  <done>
`.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md` is committed,
`cmp`-identical to the scratchpad source, 7,770 B / `20921ab9426c2169a2753749d3800934` / 70 lines;
the commit touches that one path and nothing under `src/ tests/ config/`; the amendment is
untouched and its paste block still hashes `422f1f28d6a3b76c7657fadec05a0237`; the post-commit
HEAD 40-hex is recorded for Task 2.
  </done>
</task>

<task type="auto">
  <name>Task 2: Execute the RE-CONFIRMED-AT-POSTING rule — advance PRE_EXECUTE_COMMIT by engine, correct the three prose statements it makes untrue, and see both controls red</name>

  <files>
.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md   (engine write + 3 prose edits outside the markers)
&lt;SCRATCHPAD&gt;/260821-jcs-NEGATIVE-CONTROL-DO-NOT-COMMIT/                        (control fixtures — NEVER staged)
  </files>

  <action>
**STEP A — re-measure the precondition the amendment's own sentence asserts.** The instruction is
"re-read HEAD, confirm no `_OCCLUSION_ANOMALY_FRACTION` or gate-constant change has landed since,
and update this value if the branch has advanced." Confirm, then update — in that order.

```
NEWHEAD=$(git rev-parse HEAD)          # the HEAD *after* Task 1's commit
NEWSHORT=$(git rev-parse --short=7 HEAD)
echo "NEWHEAD=$NEWHEAD  NEWSHORT=$NEWSHORT"
git log --oneline 2689cae..HEAD                                   # expect 5 lines: 4 prior + Task 1's
git diff --stat 2689cae HEAD -- src/ tests/ config/               # MUST be EMPTY
git diff --stat 2689cae HEAD -- src/ tests/ config/ | wc -l       # MUST print 0
grep -n '_OCCLUSION_ANOMALY_FRACTION = 0.0005' src/python/run_native_ld_panel.py
```

If the diff is NON-empty, or the constant grep misses, STOP AND REPORT: the precondition fails
and the gate hash must NOT advance — a gate commit that spans a code change is worse than a stale
one. Capture all four outputs verbatim; they go in the SUMMARY.

**STEP B — pre-edit anchors, so the invariant has a before as well as an after.**

```
A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
PB() { awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$1"; }
wc -c "$A"; md5sum "$A"; wc -l "$A"        # expect 42213 / e1b4a11d18ad2907af4f0a93fd5747d2 / 591
PB "$A" | wc -c; PB "$A" | md5sum          # expect 22945 / 422f1f28d6a3b76c7657fadec05a0237
grep -c '2689cae' "$A"; grep -c '2026-08-21' "$A"; grep -c '2026-08-20' "$A"; grep -c '{{' "$A"
```

Record the `2026-08-20` count — the engine has an internal PROBE that this instantiation-date
count is not disturbed by the Class-P replace, and you will re-assert it independently after.

**STEP C — run the engine. This is the only sanctioned way a hash enters the document.**
From the repo root (the engine's banked sources are repo-root-relative):

```
python3 .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py \
        --second-pass \
        .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
        --pre-execute-commit "$NEWHEAD" --posting-date 2026-08-21
echo "ENGINE EXIT=$?"
```

Expected: `RECONCILIATION: OK`, `ROW-BASIS RECONCILIATION: OK`, `PRE-REGISTERED EXPECTATIONS: OK`,
`RENDER CHECK: OK — 21 of 21`, **19 VERIFIED-IN-PLACE, 0 SUBSTITUTED, 2 FORCE-SUBSTITUTED**,
exit 0. `POSTING_DATE` force-substitutes 2026-08-21 → 2026-08-21 across 3 occurrences (a
value-preserving no-op, and it is still reported); `PRE_EXECUTE_COMMIT` force-substitutes across
2 occurrences.

Capture stdout VERBATIM into the SUMMARY, in the shape 260820-u6i-SUMMARY.md Appendix 2 used.
If the engine ABORTS on Class-M drift, STOP AND REPORT — that would mean a measured value in the
document no longer matches the banked record, which is a finding, not an obstacle.

**STEP D — assert the census, including the invariant.** Every one of these is re-executed and
printed, not asserted in prose:

```
grep -c '2689cae0c0c0666012bf451fcdd10924661bcf02' "$A"   # 0
grep -c '2689cae' "$A"                                    # 0  (short form too)
grep -c "$NEWHEAD" "$A"                                   # 2
grep -c "$NEWSHORT" "$A"                                  # >=2 is fine here (the 40-hex contains it)
grep -c '{{' "$A"; grep -c '}}' "$A"                      # 0 and 0
grep -c '2026-08-21' "$A"                                 # 3
grep -c '2026-08-20' "$A"                                 # unchanged from STEP B
PB "$A" | wc -c                                           # 22945    <- INVARIANT
PB "$A" | md5sum                                          # 422f1f28d6a3b76c7657fadec05a0237  <- INVARIANT
bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all "$A"; echo "GUARD EXIT=$?"   # 0
```

**STEP E — the three prose corrections.** Hand edits, ALL outside the PASTE markers, NONE of them
touching a number. Locate each by content, not by line number.

⚠ Before you write: the string `2689cae` must not appear anywhere in the result (STEP D asserts
count 0). Name the superseded value as "the revising task's value", and enumerate the commits
that came AFTER it, reading the actual list from `git log --oneline 2689cae..HEAD` — at plan time
that was `b4263e7`, `a364d19`, `cd0cdfd`, `241515b`, and Task 1's commit will be the fifth. Read
it; do not transcribe this plan's list on faith.

(a) The pre-paste table row `| Pre-execute commit gate | …`. The backticked 40-hex at the start
    of the row was written by the ENGINE — do not retype it, do not touch it; edit only the
    descriptive sentences after the em-dash. Target text (with `<SHAn>` from the log above):

```
| Pre-execute commit gate | `<engine-written 40-hex — leave exactly as the engine left it>` — the HEAD of `m3-W2-aou-deltas` re-read at the 2026-08-21 posting-prep re-confirmation, immediately after Seth's final pass was banked. It SUPERSEDED the revising task's value under the standing authority of the next sentence: every commit between that value and this one is docs-only (`<SHA1>`, `<SHA2>`, `<SHA3>`, `<SHA4>`, `<SHA5>`), the `src/ tests/ config/` diff across that span is empty, and the shipped `_OCCLUSION_ANOMALY_FRACTION` is unchanged. RE-CONFIRMED AT POSTING: re-read HEAD, confirm no `_OCCLUSION_ANOMALY_FRACTION` or gate-constant change has landed since, and update this value if the branch has advanced. |
```

    The final sentence (RE-CONFIRMED AT POSTING: …) is the STANDING instruction and must survive
    VERBATIM, character for character — it is the authority the next re-confirmation will use.

(b) Instantiation record item 4, the Class-P paragraph. Currently it says `PRE_EXECUTE_COMMIT`
    "is the full 40-hex HEAD captured before the REVISING task's first commit — it advanced from
    the first instantiation's value when the branch advanced". That is now a description of a
    superseded value. Replace those two clauses only, leaving the rest of item 4 (including the
    force-substitution sentence) intact:

```
4. The two Class-P slots are argv-sourced rather than measured, and are DEFINED to move:
   `POSTING_DATE` is provisional, and `PRE_EXECUTE_COMMIT` is the full 40-hex HEAD re-read at each
   re-confirmation — most recently at the 2026-08-21 posting-prep pass, after Seth's final pass was
   banked; it advanced from the first instantiation's value, and again from the revising task's,
   each time the branch advanced, which is exactly what the pre-paste table's standing
   RE-CONFIRMED-AT-POSTING instruction requires. Both are re-confirmed at posting. The
   re-instantiation engine force-substitutes them at EVERY occurrence, so the SLOT_LEDGER
   line and the pre-paste table row cannot drift apart.
```

(c) Pre-paste checklist item 3 — "six" becomes "seven" and the new path is appended:

```
3. Confirm the seven supporting records are committed: the two Seth transcripts, the 21-region
   sweep, the §5/§4 supplement, the site-basis sweep results, the banked attack on the
   instantiated draft
   (`.planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md`), and Seth's final
   pass
   (`.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md`).
```

    ⛔ Do NOT touch the other three "six" occurrences (inside and after the paste block). Those
    are the six NaN PAIRS — a different quantity entirely, and two of them are inside the frozen
    block. After the edit: `grep -c '\bsix\b'` == 3 and `grep -c 'seven supporting records'` == 1.

**STEP F — re-assert everything after the hand edits.** Prose edits are exactly where a frozen
block gets nicked, so the invariant is checked again, not assumed to have survived:

```
PB "$A" | wc -c; PB "$A" | md5sum        # 22945 / 422f1f28d6a3b76c7657fadec05a0237  <- AGAIN
grep -c '2689cae' "$A"                   # 0
grep -c "$NEWHEAD" "$A"                  # 2
grep -c '{{' "$A"                        # 0
grep -c '2026-08-21' "$A"                # 3
grep -c '\bsix\b' "$A"                   # 3
grep -c 'seven supporting records' "$A"  # 1
bash <guard> all "$A"; echo "GUARD EXIT=$?"   # 0
wc -c "$A"; md5sum "$A"; wc -l "$A"      # NEW whole-file anchors — record them, Task 3 needs them
git diff --stat -- "$A"                  # inspect: only outside-the-markers lines + the 2 hash lines
```

**STEP G — the two negative controls, RE-EXECUTED HERE.** Both run as 2-cell matrices on the same
fixture path so the red is attributable. Fixtures live in the scratchpad and are never staged.

```
NC=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/260821-jcs-NEGATIVE-CONTROL-DO-NOT-COMMIT
mkdir -p "$NC"
printf 'Fixtures in this directory carry DELIBERATELY PERTURBED values.\nThey are negative controls for quick task 260821-jcs. NEVER commit them.\n' > "$NC/README-NEGATIVE-CONTROL.txt"
```

NC-1 — a re-introduced slot sentinel must drive the guard red. Keep the basename identical to the
real file so the guard's basename check is not a confounding cause of the red:

```
cp "$A" "$NC/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
# GREEN CELL (attribution): the unperturbed copy at the same path
bash <guard> all "$NC/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"; echo "NC1-GREEN EXIT=$?"   # expect 0
# perturb ONE ledger line back to a sentinel
python3 - "$NC/osf-amendment-occlusion-gate-recalibration-2026-08-20.md" <<'PY'
import sys
p = sys.argv[1]
t = open(p).read()
old = "  CEILING_3X_MEDIAN_PCT = 0.5056%"
new = "  CEILING_3X_MEDIAN_PCT = {{CEILING_3X_MEDIAN_PCT}}"
assert t.count(old) == 1, "expected exactly one ledger line to perturb, found %d" % t.count(old)
open(p, "w").write(t.replace(old, new))
print("perturbed 1 ledger line -> sentinel")
PY
# RED CELL
bash <guard> all "$NC/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"; echo "NC1-RED EXIT=$?"     # MUST be non-zero
```

NC-2 — a single perturbed per-region table value must drive the engine's RECONCILIATION red:

```
S=.planning/debug/260820-site-basis-sweep-results-as-received.md
cp "$S" "$NC/site-basis-PERTURBED.md"
python3 - "$NC/site-basis-PERTURBED.md" <<'PY'
import sys, re
p = sys.argv[1]
lines = open(p).read().split("\n")
hits = [i for i, l in enumerate(lines) if l.startswith("    m2_region_00042 ")]
assert len(hits) == 1, "expected exactly one m2_region_00042 table row, found %d" % len(hits)
i = hits[0]
before = lines[i]
lines[i] = before.replace("0.2698", "0.2599")          # 7th field, this row only
assert lines[i] != before
open(p, "w").write("\n".join(lines))
print("BEFORE:", before)
print("AFTER :", lines[i])
PY
diff "$S" "$NC/site-basis-PERTURBED.md" | grep -c '^[<>]'      # MUST be 2 — exactly one changed line
# GREEN CELL (attribution): same command, unperturbed source
python3 <engine> --dry-run; echo "NC2-GREEN EXIT=$?"                                   # expect 0
# RED CELL
python3 <engine> --dry-run --control-source "$NC/site-basis-PERTURBED.md"; echo "NC2-RED EXIT=$?"   # MUST be non-zero
```

The NC-2 red must name a RECONCILIATION failure (the printed `max=0.2698%` no longer re-derives
from its own column). Transcribe all four cells — command, output tail, exit code — into the
SUMMARY. If either RED cell exits 0, the check it is supposed to prove is not actually enforcing;
STOP AND REPORT rather than proceeding on an unproven green.

Confirm no control fixture leaked into the repo: `git status --porcelain | grep -c 260821-jcs-NEGATIVE` must be 0.

**STEP H — commit.** Fold the prose edits into this commit (the BRIEF permits it), substituting
the real short hash for `<short>` and keeping the `…` character:

```
git add .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
git commit -m "docs(amendment): RE-CONFIRMED AT POSTING — PRE_EXECUTE_COMMIT advanced to <short> by engine Class-P pass; paste block byte-identical (422f1f28…)"
git status --porcelain -- .planning/ | head
```
  </action>

  <verify>
    <automated>
A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
PB() { awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$1"; }
test "$(PB "$A" | wc -c)" -eq 22945 && echo "PASTE SIZE: OK"
test "$(PB "$A" | md5sum | cut -d' ' -f1)" = "422f1f28d6a3b76c7657fadec05a0237" && echo "PASTE MD5: OK"
test "$(grep -c '2689cae' "$A")" -eq 0 && echo "OLD HASH GONE: OK"
NEWHEAD=$(git log --format=%H --grep='bank Seth.s final pass as-received' -1)
test "$(grep -c "$NEWHEAD" "$A")" -eq 2 && echo "NEW HASH x2: OK"
test "$(grep -c '{{' "$A")" -eq 0 && test "$(grep -c '}}' "$A")" -eq 0 && echo "NO SENTINELS: OK"
test "$(grep -c '2026-08-21' "$A")" -eq 3 && echo "POSTING_DATE x3: OK"
test "$(grep -c '\bsix\b' "$A")" -eq 3 && echo "SIX->NaN-PAIRS-ONLY: OK"
test "$(grep -c 'seven supporting records' "$A")" -eq 1 && echo "SEVEN RECORDS: OK"
grep -c '260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md' "$A"
bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all "$A"; echo "GUARD EXIT=$?"
git diff --stat 2689cae HEAD -- src/ tests/ config/ | wc -l    # 0
grep -c '_OCCLUSION_ANOMALY_FRACTION = 0.0005' src/python/run_native_ld_panel.py
git status --porcelain | grep -c '260821-jcs-NEGATIVE'         # 0
md5sum .planning/osf_deviations.md                              # MUST still be dd3806312977513a8727463ec3a032df
    </automated>
  </verify>

  <done>
`PRE_EXECUTE_COMMIT` is the post-banking HEAD 40-hex at both of its occurrences and got there via
the engine (19 VERIFIED-IN-PLACE / 0 SUBSTITUTED / 2 FORCE-SUBSTITUTED, exit 0, stdout captured);
`2689cae` appears nowhere; `POSTING_DATE` is 2026-08-21 at three occurrences; zero sentinels;
`guard all` exits 0 both before and after the prose edits; the paste block is 22,945 B /
`422f1f28d6a3b76c7657fadec05a0237` at every check; the three prose statements now describe the
value the document actually carries and the checklist counts seven records and names the new path;
the three "six NaN pairs" statements are untouched; both negative controls were re-executed here
as 2-cell matrices with the red cells exiting non-zero; `.planning/osf_deviations.md`,
`src/`, `tests/` and `config/` are byte-unchanged; one commit, explicit paths.
  </done>
</task>

<task type="auto">
  <name>Task 3: Write Carter's posting card, hand off through STATE + HANDOFF, and push</name>

  <files>
.planning/debug/260821-POSTING-CARD-for-carter.md                                        (create)
.planning/STATE.md                                                                       (new top block; demote the MORNING block)
.planning/HANDOFF.json                                                                   (new resume_on_reconnect[0])
.planning/quick/260821-jcs-bank-seth-s-final-pass-re-confirmed-at-p/260821-jcs-SUMMARY.md (create)
  </files>

  <action>
**STEP A — the posting card.** Written for a human driving a browser with no agent in the loop.
Use the FRESH whole-file anchors recorded at Task 2 STEP F. Required contents, in this order:

(i) ANCHORS.
    - Whole file: `<fresh wc -c>` B / `<fresh md5sum>` / `<fresh wc -l>` lines, at commit `<Task-2 short SHA>`.
    - What actually gets posted — the paste block: **22,945 B / `422f1f28d6a3b76c7657fadec05a0237`**.
      State plainly that this is the byte-identity Seth verified, that it did not move during the
      re-confirmation, and that if the Mac-side extraction disagrees with it Carter must STOP and
      not upload.
    - `PRE_EXECUTE_COMMIT` = `<new 40-hex>`; POSTING_DATE = 2026-08-21.

(ii) MAC-SIDE COMMANDS (macOS: `md5`, NOT `md5sum`):

```
scp ckclinto@login.hpc.ncsu.edu:/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
    /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/

cd /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/

awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' \
    osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
    > osf-amendment-occlusion-gate-recalibration-2026-08-21.md

wc -c osf-amendment-occlusion-gate-recalibration-2026-08-21.md    # must read 22945
md5   osf-amendment-occlusion-gate-recalibration-2026-08-21.md    # must read 422f1f28d6a3b76c7657fadec05a0237
```

    Call out the two-filenames point explicitly, because conflating them is the easy mistake: the
    UPLOADED file carries the POSTING date (`…-2026-08-21.md`, matching the prepared deviation
    entry's template), the REPO file keeps the INSTANTIATION date (`…-2026-08-20.md`). A mismatch
    between them is expected, not an error.

(iii) THE OSF PROCEDURE.
    - `osf.io/az52u` → Files → UPLOAD `osf-amendment-occlusion-gate-recalibration-2026-08-21.md`
      as a **NEW file**.
    - ⛔ NEVER "upload new version" on `trsx5`. `trsx5` must still show exactly 1 revision
      (2026-07-10 13:32) afterwards — append-only, a new dated record, never a silent swap.
    - ⛔ NEVER paste the text into a wiki or a text box. Upload the FILE. The 2026-07-10
      hand-paste is precisely how `trsx5`'s body came out as a re-rendered lineage
      (`.planning/osf_deviations.md` lines 190-300); a file upload cannot re-render markup.

(iv) POST-UPLOAD CAPTURES — the four values the prepared, NOT-YET-APPENDED deviation entry needs:
    1. the new file's GUID and its URL;
    2. the authoritative UTC timestamp from OSF **Recent Activity** — NOT the file page's "Date
       created", which is the PARENT record's creation date (2026-04-10, osf.io/pvb5j);
    3. re-download the posted file and `md5` it — must read `422f1f28d6a3b76c7657fadec05a0237`
       (this closes the loop: what OSF stores == what Seth verified);
    4. confirm `trsx5` still shows exactly **1** revision.

(v) WHAT TO PASTE BACK to the NCSU session so the record step can run: those four captures
    verbatim, plus the observed filename. Name what happens next with them — the record quick
    task appends the prepared entry to `.planning/osf_deviations.md`, banks
    `DEC-2026-08-21-occlusion-recalibration-posted`, sets `HANDOFF.gates.osf_pre_registration`,
    and tags the record commit.

(vi) IF IT SLIPS. If posting does not happen on 2026-08-21, do **NOT** hand-edit the date. Ask the
    session to re-run the engine's Class-P pass with the new `--posting-date` (all three
    occurrences move together, by construction), re-run `guard all`, and re-issue the anchors.
    A hand edit would move the paste block and break the byte-identity this card is built on.

End the card with this line VERBATIM, byte for byte:

```
measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires.
```

**STEP B — STATE.md.** Insert a NEW block immediately ABOVE the `## 2026-08-21 MORNING — SESSION
CLOSE` heading, and demote that heading's `(★ RESUME HERE — LATEST ★)` marker to
`(SUPERSEDED by the 2026-08-21 AFTERNOON block above; preserved in place)` — the same
demote-in-place convention every earlier block uses. Do NOT rewrite the YAML frontmatter. The new
block must carry:
    - headline: Seth's final pass RECEIVED and BANKED (no blocking objection; seventh supporting
      record), the pre-paste re-confirmation DONE;
    - the new `PRE_EXECUTE_COMMIT` (short + full), the fresh whole-file anchors, and the unchanged
      paste-block anchor 22,945 B / `422f1f28d6a3b76c7657fadec05a0237`;
    - that the advance went through the engine's Class-P pass and both negative controls were
      re-executed red;
    - `POSTING_DATE` still 2026-08-21;
    - ▶ RESUME, in order: (1) **Carter posts** from
      `.planning/debug/260821-POSTING-CARD-for-carter.md` (agent never posts); (2) the **record**
      quick task — append the prepared deviation entry with GUID/URL/UTC,
      `DEC-2026-08-21-occlusion-recalibration-posted`, `HANDOFF.gates.osf_pre_registration`, tag
      the record commit; (3) the **remediation batch** — the TWO-CONDITION gate, site-basis
      ceiling 0.5056% **AND** inflation 3.42x, BOTH (amendment Post-Paste item 6 and Seth's
      closing line; shipping the ceiling alone is not authorised); (4) **Stage A**;
    - the status line, and ⛔ AN AGENT MUST NEVER FIRE.

**STEP C — HANDOFF.json.** Prepend a NEW `resume_on_reconnect[0]` string and relabel the existing
#0 as superseded, matching the in-file convention (`> #0 (2026-08-21 AFTERNOON — SUPERSEDES every
earlier #0). …`). Preserve the file's existing 2-space-indent, one-string-per-line formatting —
do NOT reserialise the whole document. Also update the top-level `"timestamp"` to this session's
UTC. Content mirrors STEP B, and MUST name `.planning/debug/260821-POSTING-CARD-for-carter.md`.
Do NOT touch `gates.*` — the gate moves in the record task, after posting, not now.

```
python3 -c "import json;json.load(open('.planning/HANDOFF.json'));print('valid json')"
python3 -c "import json;print(json.load(open('.planning/HANDOFF.json'))['resume_on_reconnect'][0][:200])"
```

**STEP D — the SUMMARY.** `260821-jcs-SUMMARY.md` MUST carry, at minimum:
    - the engine stdout VERBATIM (Appendix, u6i Appendix-2 shape);
    - the four STEP-A precondition outputs (log, empty diff, constant grep, HEAD);
    - the SEEN-RED evidence: all four control cells, command + output tail + exit code;
    - before/after anchors for BOTH the whole file and the paste block, with the paste block
      shown identical across the task;
    - the final HEAD after push, and `origin == local`.

**STEP E — commit and push.** Two commits, explicit paths:

```
git add .planning/debug/260821-POSTING-CARD-for-carter.md
git commit -m "docs(debug): posting card for Carter — az52u NEW-file upload, fresh anchors, post-upload captures, if-it-slips rule"

git add .planning/STATE.md .planning/HANDOFF.json \
        .planning/quick/260821-jcs-bank-seth-s-final-pass-re-confirmed-at-p/260821-jcs-PLAN.md \
        .planning/quick/260821-jcs-bank-seth-s-final-pass-re-confirmed-at-p/260821-jcs-SUMMARY.md
git commit -m "docs(quick-260821-jcs): close-out — Seth's final pass banked, RE-CONFIRMED AT POSTING executed (engine Class-P, paste block byte-identical), posting card ready; NEXT = Carter posts"

git push
git rev-parse HEAD; git rev-parse origin/m3-W2-aou-deltas    # MUST be equal
git status --porcelain -- .planning/ | head
```

Push is SSH — no PAT. Note that `git push` does not push tags; there is no tag in this task (the
tag belongs to the record task, after posting). Report the final HEAD.
  </action>

  <verify>
    <automated>
C=.planning/debug/260821-POSTING-CARD-for-carter.md
test -f "$C" && wc -l "$C"
grep -c '422f1f28d6a3b76c7657fadec05a0237' "$C"                       # >=2 (anchor + re-download check)
grep -c '22945\|22,945' "$C"                                          # >=1
grep -c 'osf-amendment-occlusion-gate-recalibration-2026-08-21.md' "$C"   # >=1 (OSF filename)
grep -c 'osf-amendment-occlusion-gate-recalibration-2026-08-20.md' "$C"   # >=1 (repo basename)
grep -c 'ckclinto@login.hpc.ncsu.edu' "$C"; grep -c 'Recent Activity' "$C"; grep -c 'trsx5' "$C"
grep -c 'md5sum' "$C"                                                 # 0 on the Mac-side commands (macOS uses md5)
grep -Fc 'measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires.' "$C"   # 1
grep -c '2026-08-21 AFTERNOON' .planning/STATE.md                     # >=1
grep -c 'SUPERSEDED by the 2026-08-21 AFTERNOON block above' .planning/STATE.md   # 1
grep -c '260821-POSTING-CARD-for-carter.md' .planning/STATE.md .planning/HANDOFF.json
python3 -c "import json;json.load(open('.planning/HANDOFF.json'));print('HANDOFF: valid json')"
A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$A" | md5sum   # 422f1f28...
awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' "$A" | wc -c    # 22945
bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all "$A"; echo "GUARD EXIT=$?"
git diff --stat 2689cae HEAD -- src/ tests/ config/ | wc -l           # 0
md5sum .planning/osf_deviations.md                                    # dd3806312977513a8727463ec3a032df
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/m3-W2-aou-deltas)" && echo "PUSHED: origin == local"
git status --porcelain -- .planning/ | grep -v '^??' | wc -l          # 0 = clean for tracked .planning paths
    </automated>
  </verify>

  <done>
`.planning/debug/260821-POSTING-CARD-for-carter.md` exists and carries all six required sections —
fresh + paste-block anchors, the Mac `scp`/`awk`/`wc -c`/`md5` sequence, the NEW-file-on-az52u
procedure with both prohibitions (no trsx5 re-version, no wiki paste) and the 2026-07-10
precedent, the four post-upload captures with the Recent-Activity-not-Date-created warning, the
paste-back list, the if-it-slips engine route — and ends with the status line verbatim. STATE.md
carries a new 2026-08-21 AFTERNOON top block with the MORNING block demoted in place;
HANDOFF.json is valid JSON with a new `resume_on_reconnect[0]` naming the card; the SUMMARY
carries the engine stdout, the four seen-red control cells, before/after anchors and the final
HEAD; both commits landed with explicit paths; `git push` succeeded and `origin == local`; the
paste block still hashes `422f1f28d6a3b76c7657fadec05a0237`, `guard all` still exits 0,
`osf_deviations.md` is byte-unchanged, and nothing under `src/ tests/ config/` moved.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|---|---|
| chat → repo | Seth's final pass arrives as relayed text; it becomes the seventh entry in a checklist a public record depends on. |
| git HEAD → amendment | A commit hash crosses from the VCS into a pre-registration document that asserts a property of the span it names. |
| draft → OSF | The amendment is one Carter action from a permanent public record; nothing downstream re-checks the bytes. |
| repo (GPFS) → Mac → OSF | The posted body travels over `scp` and a browser upload, both outside any check this repo runs. |
| perturbed fixture → tracked tree | Two deliberately-wrong files exist on disk for the duration of the negative controls. |
| session → external world | Every forbidden action (OSF contact, VM fire, code change) lives on the far side of this boundary. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|---|---|---|---|---|
| T-jcs-01 | Tampering | The paste block — a prose edit outside the markers nicks the frozen body and Carter posts bytes Seth never saw | mitigate | The 22,945 B / `422f1f28d6a3b76c7657fadec05a0237` identity is re-measured with the marker-exclusive awk at Task 1 verify, Task 2 STEP D (post-engine), Task 2 STEP F (post-prose-edit) and Task 3 verify — four times, on both sides of every edit. The Mac-side extraction re-checks it a fifth time before upload. |
| T-jcs-02 | Spoofing | `PRE_EXECUTE_COMMIT` — an agent types a plausible 40-hex, and a hash with no provenance certifies a code-state claim | mitigate | The hash enters ONLY through the engine's Class-P force substitution from argv; the plan forbids retyping the backticked hash during the prose edit; verify asserts the document's hash equals the SHA of the banking commit resolved independently by `git log --grep`, at exactly 2 occurrences. |
| T-jcs-03 | Repudiation | The gate row asserts "docs-only since" while a code change actually landed in the span | mitigate | `git diff --stat 2689cae HEAD -- src/ tests/ config/` is executed and required EMPTY before the advance and again in both verifies; `_OCCLUSION_ANOMALY_FRACTION = 0.0005` is grepped in the shipped file; a non-empty diff is a STOP, not a note. |
| T-jcs-04 | Tampering | The prose edit writes `2689cae` into the file, colliding with the `grep -c '2689cae' == 0` assertion, and the cheapest escape is loosening the assertion | mitigate | The collision is named in `<constraints>` before the edit is described, the replacement text is supplied already phrased around it ("the revising task's value"), and the enumeration is defined as the commits AFTER it read live from `git log`. Loosening the assertion is explicitly not an option; a second edit is. |
| T-jcs-05 | Repudiation | A green guard / green engine run is trusted although neither has been seen fail on this document today | mitigate | Both controls are RE-EXECUTED in-task as 2-cell matrices on the same fixture path (unperturbed → 0, perturbed → non-zero), with both perturbations asserted to be exactly one line; a RED cell exiting 0 is a STOP. Transcripts go in the SUMMARY. |
| T-jcs-06 | Information disclosure | A perturbed control fixture is later read as a real record, or worse, committed | mitigate | Fixtures live only in the session scratchpad, in a directory named `260821-jcs-NEGATIVE-CONTROL-DO-NOT-COMMIT` with a README banner; `git status --porcelain \| grep -c 260821-jcs-NEGATIVE` is asserted 0; staging is explicit-path only, never `git add -A`. |
| T-jcs-07 | Elevation of privilege | An agent posts to OSF, fires the AoU loop, or flips the code constant "while it is in there" | mitigate | Scope forbids all three; the card is written for Carter's hands only and repeats "an agent never posts and never fires" verbatim; verify asserts `src/ tests/ config/` unchanged across the whole span and `osf_deviations.md` byte-identical at `dd3806312977513a8727463ec3a032df`; the gate flip is deferred to the record task, after posting. |
| T-jcs-08 | Tampering | The instantiation-date `2026-08-20` references (or the basename) are dragged along by the POSTING_DATE force-substitution | mitigate | The engine carries an internal PROBE asserting the instantiation-date count is unchanged across the replace; the plan independently records `grep -c '2026-08-20'` before and after and requires equality; `POSTING_DATE` is asserted at exactly 3 occurrences. |
| T-jcs-09 | Denial of service (of the record) | The checklist's "six"→"seven" edit also rewrites the three "six NaN pairs" statements — two of which are INSIDE the frozen block — silently corrupting a different quantity | mitigate | The three protected occurrences are named in the plan, the edit is specified as a targeted single-item replacement, and verify asserts `grep -c '\bsix\b'` == 3 (down from 4) with `seven supporting records` == 1; T-jcs-01's paste-block md5 catches any in-block change outright. |
| T-jcs-10 | Repudiation | The posted OSF file and the repo file differ, or the wrong filename is uploaded, and the deviation entry then records something untrue | mitigate | The card pins the two filenames side by side with the reason they differ, requires a re-download + `md5` == `422f1f28…` as an explicit post-upload capture, and requires the `trsx5`-still-1-revision check; the OSF filename in the card matches the prepared deviation entry's template exactly. |
</threat_model>

<verification>
Re-execute, do not read. Every one of these is a command with an expected value.

1. `guard all` on the final amendment exits **0**.
2. Paste block (marker-exclusive awk): **22,945 B** and md5 **`422f1f28d6a3b76c7657fadec05a0237`**.
3. `grep -c '2689cae' <amendment>` == **0**; `grep -c "$NEWHEAD" <amendment>` == **2**.
4. `grep -c '{{' <amendment>` == **0**; `grep -c '2026-08-21' <amendment>` == **3**.
5. `grep -c '\bsix\b'` == **3**; `grep -c 'seven supporting records'` == **1**; the new record's
   path appears in the checklist.
6. `cmp` between the scratchpad source and the banked record is **silent**; banked file is
   **7,770 B / `20921ab9426c2169a2753749d3800934`**.
7. `git diff --stat 2689cae HEAD -- src/ tests/ config/` is **empty**;
   `_OCCLUSION_ANOMALY_FRACTION = 0.0005` still present in `src/python/run_native_ld_panel.py`.
8. `.planning/osf_deviations.md` md5 is still **`dd3806312977513a8727463ec3a032df`**.
9. Both negative controls were run **in this task**: NC-1 (re-introduced `{{SLOT}}` → `guard all`
   non-zero) and NC-2 (one perturbed per-region table value → engine `--dry-run --control-source`
   RECONCILIATION failure, non-zero), each with its matching green cell, all four transcribed.
10. `.planning/HANDOFF.json` parses as JSON and its `resume_on_reconnect[0]` is the new AFTERNOON
    entry naming the posting card.
11. Posting card contains the paste-block anchor, both filenames, the Mac commands (`md5`, no
    `md5sum`), the trsx5 prohibition, the Recent-Activity timestamp warning, and the verbatim
    status line.
12. `git status` clean for tracked `.planning/` paths; `git rev-parse HEAD` ==
    `git rev-parse origin/m3-W2-aou-deltas`; no control fixture staged.
</verification>

<success_criteria>
- Seth's final pass is banked byte-identically and counted as the seventh supporting record, with
  its path named in the pre-paste checklist.
- The amendment's own RE-CONFIRMED-AT-POSTING rule was EXECUTED: precondition re-measured, gate
  hash advanced by the engine at both occurrences, three prose statements corrected to describe
  the value the document now carries, standing instruction preserved verbatim.
- The posted body did not move: 22,945 B / `422f1f28d6a3b76c7657fadec05a0237` at every commit.
- `guard all` exits 0 on the final file, and that green is backed by two reds seen today.
- Carter has a card he can execute alone, and STATE + HANDOFF name the order after it: post →
  record → remediate (BOTH conditions) → Stage A.
- Nothing was posted, nothing was fired, no code changed, `osf_deviations.md` byte-unchanged,
  `origin == local` at close.
</success_criteria>

<output>
After completion, create
`.planning/quick/260821-jcs-bank-seth-s-final-pass-re-confirmed-at-p/260821-jcs-SUMMARY.md`
carrying, at minimum:
- Appendix: the engine `--second-pass` stdout VERBATIM (u6i Appendix-2 shape) with its exit code.
- Appendix: the four negative-control cells — command, output tail, exit code — for NC-1 and NC-2.
- The precondition evidence: `git log --oneline 2689cae..HEAD`, the empty `git diff --stat`, the
  constant grep, and the captured 40-hex.
- Anchors table: whole file BEFORE (42,213 B / `e1b4a11d18ad2907af4f0a93fd5747d2`) → AFTER
  (measured), and paste block BEFORE == AFTER (22,945 B / `422f1f28d6a3b76c7657fadec05a0237`).
- The final HEAD after `git push` and confirmation that `origin == local`.
- The status line: measurement banked; amendment drafted, not posted; code constant unchanged;
  fire HELD; an agent never posts and never fires.
</output>
