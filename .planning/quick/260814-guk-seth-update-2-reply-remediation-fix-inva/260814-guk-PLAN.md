---
phase: quick-260814-guk
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh
  - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-baseline.txt
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
  - .planning/HANDOFF.json
  - .planning/STATE.md
  - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
  - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-REPLY-TO-SETH.md
autonomous: true
requirements: [D1, D2, D3, D4, D5, D6, D7]

must_haves:
  truths:
    - "Every executable trsx5 card adjudicates on BYTE COUNT FIRST: any size other than 9,758 or 9,907 is a STOP by itself, with no hash comparison required or permitted to overrule it."
    - "No executable card carries a hash literal that is not exactly 32 hex characters; the invalid 31-char string appears nowhere outside the 260814-guk task directory."
    - "The corrected 32-char short-body md5 appears ONLY as an advisory, attributed to Seth via the OSF API and marked unverified-by-us — never as an adjudication anchor."
    - "The 9,758 / 28ecdb31 PASS anchor carries its firsthand re-derivation (the awk extraction, exclusive of both marker lines) at every executable site."
    - "Carter's primary checklist (READY-TO-FIRE.md) lists the fire-blocking trsx5 gate as item 6b, positioned between item 6 and item 7, with no renumbering of items 7-11."
    - "Both deferral-vocabulary blocks carry Seth's R3 ceiling figures (0.0005 x n_var, strict >, 60.0 at the 120,000 cap, 51.2 at region-1's 102,421, region 1 ~10x under) with attribution."
    - "The square-mode deferral set is registered as a disclosable ancestry-specific COVERAGE GAP with a recorded remedy path; the framing 'nothing scientific is lost' appears nowhere as a live claim."
    - "The Stage-B cost extrapolation reads as cost-per-BANKABLE-region, never cost-per-region-of-276, at every site that states it."
    - "HANDOFF.json is valid JSON and its live trsx5 gate field carries the corrected value plus a dated 2026-08-14 correction; the dated 2026-08-14 close bodies are preserved, not rewritten."
    - "Seth has a courier package that confirms the 31-char count firsthand, quotes the new card in full, and states plainly that we cannot compute the 149-byte diff without his body."
  artifacts:
    - path: ".planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh"
      provides: "Three-section checker (fire | record | reply | all) with a generic hex-run length invariant"
      min_lines: 60
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
      provides: "STEP 6b size-first card; R3 numbers in the STAGE-C-HOLD paragraph; STEP 9 cost relabel"
      contains: "ADJUDICATE ON THE BYTE COUNT FIRST"
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md"
      provides: "Section 6b size-first card; cost-refinement-gate relabel"
      contains: "9,907"
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md"
      provides: "New item 6b (the missing fire-blocking gate); R3 numbers + R4 disclosure note in section 10; item 11-C cost relabel"
      contains: "## 6b"
    - path: ".planning/HANDOFF.json"
      provides: "Corrected live gate field + one dated correction clause atop status; still valid JSON"
      contains: "c19be8b2ad7cd6a45fee1d668d8a9cf9"
    - path: ".planning/STATE.md"
      provides: "Corrected trsx5-contest block (body-side, line ~34) with a dated correction; frontmatter lines 1-24 byte-identical"
      contains: "c19be8b2ad7cd6a45fee1d668d8a9cf9"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md"
      provides: "R4-COVERAGE registration: coverage gap + disclosure obligation + remedy path"
      contains: "R4-COVERAGE"
    - path: ".planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-REPLY-TO-SETH.md"
      provides: "Courier package answering BLOCKING / R1 / R3 / R4 and both of Seth's requests"
      min_lines: 60
  key_links:
    - from: "260812-ox1-AGENT-PROMPT.md STEP 6b"
      to: "the two size anchors 9758 / 9907"
      via: "size-first adjudication clause preceding any hash"
      pattern: "9,?758"
    - from: "260812-ox1-READY-TO-FIRE.md item 6b"
      to: "item ordering 6 -> 6b -> 7"
      via: "heading insertion without renumbering"
      pattern: "^## 6b"
    - from: ".planning/HANDOFF.json gates.trsx5_posted_body"
      to: "the corrected card"
      via: "dated 2026-08-14 correction clause naming the size-first rewrite"
      pattern: "CORRECTED 2026-08-14"
    - from: ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md R4-COVERAGE"
      to: "the remedy path (banded mode / overlapping sub-windows)"
      via: "bounded-not-permanent clause"
      pattern: "--ld-window"
    - from: "260814-guk-REPLY-TO-SETH.md"
      to: "the D3 anchor re-derivation transcript"
      via: "verbatim awk + wc -c + md5sum block"
      pattern: "PASTE INTO OSF FROM HERE"
---

<objective>
Remediate Seth's 2026-08-14 reply to UPDATE #2: fix the BLOCKING transcription defect
in the trsx5 adjudication card (a 31-character "md5" that can never match, so the
STOP-truncated branch could never fire), rewrite every executable card size-first, add
the missing fire-blocking gate to Carter's primary checklist, record Seth's R3 ceiling
numbers and register R4 as a disclosure obligation with a remedy path, and produce the
reply-to-Seth courier package.

Purpose: the instrument Carter will actually run before committing $385-1,084 is
currently structurally incapable of firing its protective branch. This is the project's
recurring "assertion that cannot fail" class, one step before an irreversible spend.

Output: 3 runbook files corrected, 3 record surfaces corrected, 1 new deferred item, 1
courier package, 1 re-runnable checker.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-CONTEXT.md
@.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-SETH-REPLY.md
@.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
@.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
@.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
@CLAUDE.md

<facts_verified_at_planning_time>
<!-- Re-derived firsthand 2026-08-14 by the planner. The executor may re-run these to  -->
<!-- confirm, but must NOT need to discover them. -->

printf 'c19e8b2ad7cd6a45fee1d668d8a9cf9'  | wc -c  ->  31   (INVALID; shipped 2026-08-13)
printf 'c19be8b2ad7cd6a45fee1d668d8a9cf9' | wc -c  ->  32   (Seth-corrected, advisory only)
printf '28ecdb3160833da80cfa25952f76415b' | wc -c  ->  32
printf '425d925a88ab474ec2396cbea25e665c' | wc -c  ->  32

D3 anchor re-derivation (working tree AND `git show ac4c990:$F`, both identical):
  F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
  awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | wc -c
    -> 9758
  awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | md5sum
    -> 28ecdb3160833da80cfa25952f76415b

COMPLETE SITE MAP for the invalid string (repo-wide grep, excluding .git and the
260814-guk task dir): exactly ONE hit — AGENT-PROMPT.md:101. The bare prefix
`c19e8b2` additionally appears at BROWSER-PASTE.md:113, HANDOFF.json:9 (status),
HANDOFF.json:24 (resume_on_reconnect[0]), HANDOFF.json:73 (gates.trsx5_posted_body),
STATE.md:34, STATE.md:1702. `.claude/skills/aou-ld-pipeline/` carries ZERO hash sites
(checked) — there is no fifth executable copy.

STATE.md frontmatter fence: `---` at line 1 and line 24. Body starts at line 25. The
trsx5-contest block is line 34. Session Continuity is line 1702 (NOT this task's).

HANDOFF.json is valid JSON today (python3 json.load exit 0).

READY-TO-FIRE.md heading order today: `## 1.` :22, `## 2.` :33, `## 3.` :61, `## 4.` :69,
`## 5.` :89, `## 6.` :102, `## 7.` :108, `## 8.` :136, `## 9.` :161, `## 10.` :176,
`## 11.` :219. Inserting `## 6b` before `## 7.` requires NO renumbering — and must not
cause any, because AGENT-PROMPT STEP 10 and BROWSER-PASTE section 7 both cite "item 7"
by number.

The phrase "nothing scientific is lost" does not currently appear in any runbook file;
D6's retirement of that framing is therefore a FORWARD prohibition to enforce, not a
string to delete.

deferred-items.md is 1145 lines; its last section is `## SR4-OPEN`. R4-COVERAGE appends
after it under a new dated `# Deferred items — ... quick-260814-guk` header.

HANDOFF.json live-field correction precedent to match (gates.m3_04b):
  "✅ COMPLETE 2026-08-03. ... ⚠ CORRECTED 2026-08-12 (quick-260812-09a, C-HIGH): this
   field previously ended with the clause '...', which is the RETRACTED claim. It is
   STRICKEN here rather than ..."
</facts_verified_at_planning_time>

<canonical_card_substance>
<!-- D2, rendered. Every executable site must carry THIS SUBSTANCE. Wording and     -->
<!-- formatting adapt to each file's register (D2 + Claude's Discretion); the ORDER  -->
<!-- of the four elements does not: download -> size-first -> hashes-confirm ->      -->
<!-- advisory. Do NOT reproduce the 31-character literal in any executable card:     -->
<!-- describe it ("a 31-character transcription"). Re-emitting it would re-create    -->
<!-- the false-comparison surface this task exists to remove.                        -->

1. DOWNLOAD. Carter downloads https://osf.io/az52u/files/trsx5 (the FILE, not the
   page), then reports BOTH, verbatim: `wc -c` and `md5sum` of the downloaded file.

2. ADJUDICATE ON THE BYTE COUNT FIRST. A byte count cannot be mistranscribed into a
   false pass; a hash can. Any size OTHER than 9,758 or 9,907 is a STOP BY ITSELF — no
   hash comparison is required, and none may overrule it. The posted body is truncated
   or otherwise anomalous; the fire is HELD until a complete body is re-posted and
   recorded. Report bytes + md5 verbatim either way.

3. HASHES THEN CONFIRM WHICH KNOWN BODY IT IS.
   - 9,758 bytes -> expect md5 `28ecdb3160833da80cfa25952f76415b` = the repo-canonical
     paste block -> the gate PASSES, proceed.
     If it is 9,758 bytes but the md5 DIFFERS: STOP — same size, different content is
     its own anomaly. Report verbatim.
   - 9,907 bytes -> expect md5 `425d925a88ab474ec2396cbea25e665c` = the methodologist's
     complete lineage -> STOP-reconcile the lineages before firing.

   PROVENANCE of the 9,758 anchor (firsthand, re-derived 2026-08-14 on the working tree
   AND at `ac4c990`, both identical; the extraction EXCLUDES both marker lines):
     F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
     awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | wc -c
     awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | md5sum
   The 9,907 / 425d925a anchor is Seth-reported; we do NOT hold that body.

4. ADVISORY ONLY — never an adjudication anchor. Seth reports the truncated body's md5
   as `c19be8b2ad7cd6a45fee1d668d8a9cf9` (32 chars, read from the OSF API; UNVERIFIED
   BY US — the file sits behind a sign-in wall). Do not adjudicate on it. The version of
   this card shipped 2026-08-13 carried a 31-character transcription of that value; an
   md5 is 32 characters, so that comparison could never fire the STOP-truncated branch.
   Counted firsthand 2026-08-14 and rewritten size-first for exactly that reason.
   The ledger stays UN-ANNOTATED toward either lineage until this download adjudicates.
</canonical_card_substance>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Rewrite the fire surface size-first, add runbook item 6b, land R3/R4 vocabulary — and build the checker that could have caught this</name>
  <files>
.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh (new)
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
  </files>
  <action>
**Step 1 — write the checker FIRST and observe it RED.** Create
`.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh`,
`bash`-only (no pytest — this task is docs-only and pytest rewrites
`tests/m3/sparse_parent_benchmark.tsv`). Interface:
`bash 260814-guk-verify.sh {fire|record|reply|all}`, exit 0 = all checks in the
section PASS, non-zero otherwise, one `PASS`/`FAIL` line per check.

Section `fire` checks (all must be implemented; each must be able to FAIL):

  F1. **The generic length invariant — this is the check that would have caught the
      defect.** For each of the three runbook files, extract the card block by heading
      range (AGENT-PROMPT: `^STEP 6b` through the line before `^STEP 7`; BROWSER-PASTE:
      `^## 6b` through the line before `^## 7`; READY-TO-FIRE: `^## 6b` through the line
      before `^## 7\.`). Inside each block, extract every maximal hex run of length >= 20
      (`grep -oE '[0-9a-f]{20,}'`) and assert EVERY ONE is exactly 32 characters. Do not
      hard-code which hashes to expect for this check — a generic invariant catches the
      next truncation too, including one nobody predicted.
  F2. Each card block contains, literally: `28ecdb3160833da80cfa25952f76415b`,
      `425d925a88ab474ec2396cbea25e665c`, `c19be8b2ad7cd6a45fee1d668d8a9cf9`.
  F3. **Attribution containment.** Every line matching the advisory hash must sit in a
      4-line window (the match line + 3 following) that contains both `Seth` and
      `nverified` (case-tolerant on the leading U). Zero matches anywhere in the three
      files that fail this.
  F4. **Size-first ordering.** In each card block, the first occurrence of `9,758` or
      `9758` must appear on a LINE STRICTLY BEFORE the first occurrence of
      `28ecdb3160833da80cfa25952f76415b`. (A hash-first card fails this.)
  F5. **Negative control on the invalid literal.** `grep -c 'c19e8b2ad7cd6a45fee1d668d8a9cf9'`
      over the three runbook files == 0, AND `grep -c 'c19e8b2'` over the three runbook
      files == 0 (the bare prefix must be gone from the fire surface entirely).
  F6. **Anchor re-derivation, re-run not trusted.** Run the D3 awk extraction on the
      working tree and on `git show ac4c990:$F`; assert `wc -c` == 9758 and `md5sum` ==
      `28ecdb3160833da80cfa25952f76415b` for BOTH.
  F7. **Item ordering.** `grep -n '^## ' READY-TO-FIRE.md` yields `## 6.` then `## 6b`
      then `## 7.` in that order, and the headings `## 7.` through `## 11.` are still
      present and still carry their original numbers (no renumbering).
  F8. **R3 numbers present in BOTH vocabulary blocks** (AGENT-PROMPT's STAGE C HOLD
      LIFTED paragraph and READY-TO-FIRE section 10's Deferral vocabulary paragraph):
      each must contain `0.0005`, `60.0`, `51.2`, `102,421` (or `102421`), and `Seth`.
  9.  **Cost relabel** — `cost-per-bankable-region` (case-insensitive, hyphen-tolerant)
      appears in AGENT-PROMPT STEP 9's GATE sentence, in READY-TO-FIRE item 11-C, and in
      BROWSER-PASTE's Cost-refinement gate paragraph.
  F10. **Retired framing.** `nothing scientific is lost` and `nothing is lost` appear
      ZERO times across the three runbook files.

Sections `record` and `reply` are specified in Tasks 2 and 3; **write them now, in this
same file**, so that at the end of Task 1 `bash 260814-guk-verify.sh all` exits NON-ZERO
(proving those sections are not vacuous) while `bash 260814-guk-verify.sh fire` is the
one that must go green.

Run `bash 260814-guk-verify.sh fire` BEFORE editing any runbook file and record the
observed RED output in the SUMMARY. A green you have never seen fail is not evidence.

**Step 2 — the mutation negative control (mandatory, and it is the point).** Copy the
AGENT-PROMPT card block to
`$SCRATCH/card_mutated.txt` (use the session scratchpad dir, NOT /tmp), delete exactly
one hex character from `28ecdb3160833da80cfa25952f76415b` inside the copy, run check F1's
logic against the mutated copy, and CONFIRM IT REPORTS FAIL. Record the observed failure
text in the SUMMARY. If F1 passes on a 31-character hash, F1 is the same defect class it
was written to detect — stop and fix F1 before continuing.

**Step 3 — AGENT-PROMPT.md.** Three edits:
 (a) Replace STEP 6b (lines ~91-103, from `STEP 6b — GATE:` up to but NOT including
     `STEP 7 —`) with the four-element card of `<canonical_card_substance>`, in this
     file's plain-text `STEP N — ... RUN: / EXPECT:` register (no markdown fences; this
     file is pasted into a browser agent). Keep the existing justification sentence
     ("trsx5 is the pre-registration the fire executes and a truncated posted body is
     unanswerable after output is banked") and keep it a GATE.
 (b) In the `✅ STAGE C HOLD LIFTED` paragraph (~:161-173), append the R3 numbers:
     the clause-(d) anomaly threshold is `0.0005 x n_var` with a STRICT `>` (defer only
     when the occluded count strictly EXCEEDS it) — at the pinned 120,000 cap that is
     **60.0** variants; at region 1's n_var 102,421 it is **51.2**; region 1's expected
     ~5 occlusions sit ~10x under. Attribute: "ceiling figures per Seth's 2026-08-14
     review".
 (c) In STEP 9's GATE sentence (~:154-156, "Then GATE: Carter takes these
     wall_min/peak_ram numbers back to his planning side for the measured cost
     extrapolation (45 small / 203 medium / 28 large) BEFORE Stage C"), add the D6-3
     relabel: Stage B's worst case is `m2_region_00071`, the largest SQUARE-FEASIBLE
     region, so the extrapolation covers ONLY the square-feasible class — read it as
     **cost-per-BANKABLE-region, never cost-per-region-of-276** (per Seth's 2026-08-14
     review).

**Step 4 — BROWSER-PASTE.md.** Two edits:
 (a) Replace section `## 6b` (lines ~107-117, up to but NOT including `## 7 —`) with the
     same card substance in this file's markdown register (fenced blocks, `⚠`/bold
     emphasis, `[RUNBOOK]`/`[DERIVED @HEAD]` provenance discipline preserved — the card
     is `[RUNBOOK]` content).
 (b) In the **Cost-refinement gate** paragraph (~:236-238), apply the same
     cost-per-bankable-region relabel as Step 3(c). D6 names two relabel sites; this is a
     THIRD live instance of the identical claim in the same document family, and leaving
     it uncorrected re-creates exactly the divergent-copy class DEC-2026-08-12
     consolidated against. Apply it, and name the addition in the SUMMARY.

**Step 5 — READY-TO-FIRE.md.** Three edits:
 (a) INSERT a new `## 6b` section between `## 6. GATE 1 — cost/credit eyeball` (:102-106)
     and `## 7. PRE-FIRE 1b ...` (:108). RENUMBER NOTHING. Heading suggestion:
     `## 6b. THE trsx5 BYTE CHECK — GATES THE FIRE (added 2026-08-14, Seth escalation)`.
     Body: the FULL card substance, self-contained (this file is Carter's primary
     checklist and must not require opening another file), in this file's register
     (fenced commands, `⚠`/bold, the interpretation table style of item 8 is a good fit
     for the three size branches). Include verbatim: this gate BLOCKS THE FIRE and
     obligation-(2) posting; and the ledger stays UN-ANNOTATED toward either lineage
     until the download adjudicates. Add one sentence recording WHY a third copy exists
     despite drift risk: the size-first design makes a mistranscribed hash unable to
     false-pass, and a fire-blocking gate absent from "the only list" is the divergence
     class DEC-2026-08-12 consolidated against.
     Also update the file's `**Contents: ONLY Carter's remaining items, in fire order.**`
     line (:16) if needed so it is no longer contradicted.
 (b) In section 10's **Deferral vocabulary** paragraph (:207-217): add the R3 numbers
     exactly as in Step 3(b), and EXTEND the existing "Post-fire disclosure duty (note
     only)" sentence per D6-R4-placement-2 — the square-mode deferral set is ALSO a
     methods/limitations disclosure, an ancestry-specific COVERAGE GAP and not merely an
     internal deferral status; it belongs alongside the occlusion disclosure in the form
     "N regions exceeding n_var X were not converted in square mode; affected span M Mb"
     with the ACTUAL post-fire numbers; and the remedy path is recorded so the gap is
     bounded-not-permanent (the frozen producer already supports banded mode, `--r gz`
     with an `--ld-window-*` bound, and large regions can be split into overlapping
     sub-windows — NEITHER before this fire). Point at `R4-COVERAGE` in
     `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` (Task 2 registers
     it). State that the framing "nothing scientific is lost" is RETIRED and must not be
     repeated.
 (c) In item 11-C's egress/cost language (:221-223), add the cost-per-bankable-region
     relabel: the egress plan and its size/cost extrapolation cover the BANKED
     (square-feasible) set, not 276.

**Step 6.** Run `bash 260814-guk-verify.sh fire` — must exit 0, every check PASS. Then
run `bash 260814-guk-verify.sh all` — must exit NON-ZERO (record and reply sections still
red; this is the non-vacuity proof for Tasks 2-3).

**Step 7.** Commit with EXPLICIT PATHS ONLY (never `-A`, never `.` — GPFS multi-terminal
rule):
`git add .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md`
then commit
`fix(260814-guk): size-first trsx5 card at every executable site + runbook item 6b + R3/R4 vocabulary`.
DO NOT PUSH (the orchestrator pushes at the end).

CONSTRAINTS: zero changes under `src/`, `tests/`, `config/`, `Snakefile`,
`docs/manuscript/`. No pytest. No perimeter contact (no gsutil/gcloud/bq/wb, not even
read-only). Do not annotate the trsx5 ledger toward either lineage. Do not fill the
PRE-FIRE 1b signature lines.
  </action>
  <verify>
    <automated>bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh fire; test $? -eq 0 && ! bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh all</automated>
    <automated>git status --short -- src/ tests/ config/ Snakefile docs/manuscript/ | wc -l | grep -qx 0</automated>
  </verify>
  <done>
`verify.sh fire` exits 0 with all 10 checks PASS; `verify.sh all` exits non-zero. The
F1 mutation negative control was OBSERVED RED and its output is quoted in the SUMMARY.
The pre-edit RED run of `verify.sh fire` is quoted in the SUMMARY. Zero files changed
under src/, tests/, config/, Snakefile, docs/manuscript/. One atomic commit, explicit
paths, not pushed.
  </done>
</task>

<task type="auto">
  <name>Task 2: Dated corrections in the live record fields + register R4-COVERAGE</name>
  <files>
.planning/HANDOFF.json
.planning/STATE.md
.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
  </files>
  <action>
**Step 1 — pin the containment baseline BEFORE editing anything.** A moving git ref is
not a usable baseline here (the orchestrator refreshes STATE.md:1702 after this task, so
`git diff HEAD` would go red later for an unrelated reason). Write a COMMITTED, NAMED
baseline instead — run this BEFORE the first edit to HANDOFF.json or STATE.md:

```
D=.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva
{
  echo "# 260814-guk containment baseline - captured BEFORE any Task 2 edit."
  echo "entry_sha $(git rev-parse HEAD)"
  echo "state_frontmatter_1_24_md5 $(sed -n '1,24p' .planning/STATE.md | md5sum | cut -d' ' -f1)"
  echo "state_line34_md5 $(sed -n '34p' .planning/STATE.md | md5sum | cut -d' ' -f1)"
  echo "handoff_resume0_md5 $(python3 -c "import json,hashlib;print(hashlib.md5(json.load(open('.planning/HANDOFF.json'))['resume_on_reconnect'][0].encode()).hexdigest())")"
} > "$D/260814-guk-baseline.txt"
```

Add `260814-guk-baseline.txt` to this task's commit. It is the named enforcer for R4-R6;
without it those checks are a belief, not a gate.

**Step 2 — `.planning/HANDOFF.json`, THREE surgical edits. Edit it as JSON via a
python3 script (read, mutate the three string values, write with
`json.dump(..., ensure_ascii=False, indent=2)`) OR by careful in-place string edit —
either way it MUST still be valid JSON and MUST NOT reflow unrelated fields.**
 (a) `gates.trsx5_posted_body` (LIVE gate field — correct in place, dated). Replace the
     3-hash card fragment so the adjudication reads SIZE-FIRST and the wrong prefix
     `c19e8b2` is GONE from this field. Substance: any size other than 9,758 or 9,907 is
     a STOP by itself; 9,758 + `28ecdb3160833da80cfa25952f76415b` = repo-canonical =
     PASS; 9,907 + `425d925a88ab474ec2396cbea25e665c` = Seth-complete = STOP-reconcile;
     advisory only, `c19be8b2ad7cd6a45fee1d668d8a9cf9` is Seth-reported via the OSF API
     and UNVERIFIED BY US. Append a dated correction clause in the house style of
     `gates.m3_04b`: `⚠ CORRECTED 2026-08-14 (quick-260814-guk): this field previously
     carried a 31-character transcription of the short-body md5 — an md5 is 32
     characters, so that comparison could never fire the STOP-truncated branch. The card
     is now SIZE-FIRST at every executable site.` Keep the existing
     BYTE-LEVEL-CONTESTED / do-not-annotate-the-ledger sentences.
 (b) `status` (:9) — the dated 2026-08-14 close record. **Do NOT rewrite the body.** Add
     ONE dated superseding clause at the TOP of the field, matching the existing style
     of the `wave` field's superseding preamble, e.g.
     `⚠ CORRECTED 2026-08-14 (quick-260814-guk): the 3-hash card quoted below carried an
     invalid 31-character short-body md5 and is SUPERSEDED by the size-first card in the
     260812-ox1 runbook files (adjudicate on 9,758 / 9,907 bytes FIRST). The close body
     below is preserved verbatim, not rewritten. || ` followed by the original text
     beginning `SESSION CLOSE 2026-08-14.` unchanged.
 (c) `resume_on_reconnect[0]` — **DO NOT TOUCH.** D4 is explicit: the new STATE.md
     continuity refresh + quick-task row carry the correction forward. Verify it is
     byte-identical to HEAD afterwards.
 Then: `python3 -c "import json;json.load(open('.planning/HANDOFF.json'))"` must exit 0.

**Step 3 — `.planning/STATE.md`, ONE edit.** Correct the `**⚠ THE trsx5 CONTEST (do not
lose this):**` block at line ~34 (body-side, LIVE instruction block) to the same
size-first substance as 2(a), with the wrong prefix replaced by the corrected advisory
value + its attribution, plus a dated `⚠ CORRECTED 2026-08-14 (quick-260814-guk): ...`
clause naming the 31-char defect by description. **HARD CONSTRAINT: lines 1-24 are the
frontmatter fence and are UNTOUCHABLE (byte-identity gate; the YAML is
pre-existing-unparseable).** Do not touch line 1702 (Session Continuity — the
orchestrator's edit, deliberately not this task's, to avoid a collision). Do not rewrite
any dated historical `>` block.

**Step 4 — `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`.** APPEND at
end of file (currently 1145 lines, last section `## SR4-OPEN`) a new dated header
`# Deferred items — discovered during quick-260814-guk execution (2026-08-14)` and one
new entry `## R4-COVERAGE — the square-mode deferral set is an ancestry-specific COVERAGE
GAP requiring methods/limitations disclosure`, in the register of the existing entries
(Logged / Status / measured facts / why deferred / remedy / not blocking). Content:
 - **Logged:** 2026-08-14 (quick-260814-guk, from Seth's 2026-08-14 R4).
   **Status: REGISTERED as a DISCLOSURE OBLIGATION — not blocking the fire.**
 - The gap: est. ~29 / 276 = **10.5%** of regions defer at the 120,000 `--max-n-var`
   cap; bankable target ~247; largest deferred span **48.5 Mb**. ⚠ These are **Seth's
   estimates**; the ACTUAL numbers emerge at fire time from the panel TSV's
   `deferred_infeasible_square` rows and MUST replace them before anything is published.
 - The obligation: disclose as a **methods/limitations** item alongside the occlusion
   disclosure, in the form "N regions exceeding n_var X were not converted in square
   mode; affected span M Mb", with the actual post-fire numbers.
 - ⚠ **The framing "nothing scientific is lost" is RETIRED — do not repeat it.** It is
   true of this pipeline as currently built and FALSE as a statement about the science:
   those regions carry real loci with real association signal, and an undisclosed
   ancestry-specific coverage hole is the reviewer question that cannot be answered
   later ("why does your AFR panel omit the largest regions?").
 - **The remedy path, so the gap is bounded and not permanent:** the frozen producer
   ALREADY supports banded mode (`--r gz` with an `--ld-window-*` bound), and large
   regions can be split into overlapping sub-windows. **NEITHER happens before this
   fire** — recording the path is what makes the deferral honest, not a commitment to
   run it now.
 - Cross-references: READY-TO-FIRE section 10's post-fire disclosure note; the Stage-B
   cost gate now reads cost-per-BANKABLE-region.

**Step 5 — verify.** `bash .planning/quick/260814-guk-.../260814-guk-verify.sh record`
must exit 0. Implement its section `record` (written in Task 1) as:
  R1. `python3 -c "import json;json.load(open('.planning/HANDOFF.json'))"` exits 0.
  R2. `gates.trsx5_posted_body` contains `c19be8b2ad7cd6a45fee1d668d8a9cf9`, `9,758`,
      `9,907`, `CORRECTED 2026-08-14`, and does NOT contain `c19e8b2`.
  R3. `status` STARTS WITH a `⚠ CORRECTED 2026-08-14` clause AND still contains the
      original opener `SESSION CLOSE 2026-08-14.` (body preserved).
  R4. `resume_on_reconnect[0]` UNCHANGED: its md5, recomputed now, EQUALS
      `handoff_resume0_md5` in `260814-guk-baseline.txt`.
  R5. **Frontmatter byte-identity:** `sed -n '1,24p' .planning/STATE.md | md5sum`
      EQUALS `state_frontmatter_1_24_md5` in the baseline file.
  R6. **Non-vacuity pair for R5** (R5's green is evidence only because R6 can fail):
      `sed -n '34p' .planning/STATE.md | md5sum` DIFFERS from `state_line34_md5` in the
      baseline file — i.e. the trsx5-contest block was genuinely edited. Additionally
      assert no `git diff $entry_sha -- .planning/STATE.md` hunk header targets a line
      <= 24.
  R7. STATE.md contains `c19be8b2ad7cd6a45fee1d668d8a9cf9` and `CORRECTED 2026-08-14`;
      the line-34 block does NOT contain `c19e8b2`.
  R8. deferred-items.md contains `R4-COVERAGE`, `48.5`, `10.5`, `--ld-window`,
      `nothing scientific is lost` (present ONLY inside the explicit RETIRED sentence —
      assert the match line also contains `RETIRED`).

**Step 6.** Commit, explicit paths only:
`git add .planning/HANDOFF.json .planning/STATE.md .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-baseline.txt`
message: `docs(260814-guk): dated trsx5 corrections in the live record fields + register R4-COVERAGE`.
DO NOT PUSH.
  </action>
  <verify>
    <automated>bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh record</automated>
    <automated>python3 -c "import json;json.load(open('.planning/HANDOFF.json'));print('JSON OK')"</automated>
  </verify>
  <done>
`verify.sh record` exits 0 (R1-R8 PASS) against the COMMITTED `260814-guk-baseline.txt`,
not a moving git ref. HANDOFF.json parses. STATE.md lines 1-24 are md5-identical to the
pinned baseline while the line-34 md5 demonstrably CHANGED (both asserted, so neither is
vacuous). `resume_on_reconnect[0]` and STATE.md:1702 are
byte-unchanged. R4-COVERAGE is registered with its remedy path and the retired-framing
prohibition. One atomic commit, explicit paths, not pushed.
  </done>
</task>

<task type="auto">
  <name>Task 3: Reply-to-Seth courier package</name>
  <files>
.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-REPLY-TO-SETH.md
  </files>
  <action>
Create the courier package Carter will send to Seth. Register: same as
`260814-guk-SETH-REPLY.md` — a direct technical reply, no ceremony, no hedging. It answers
Seth's four items in HIS order, then his two requests. Required content (D7):

 1. **BLOCKING — confirmed, not taken on faith.** State that the defect was COUNTED
    firsthand on 2026-08-14 (`printf 'c19e8b2ad7cd6a45fee1d668d8a9cf9' | wc -c` -> 31 —
    quoting the invalid string here is fine and useful; this is a courier document, not
    an executable card) and that it was fixed at EVERY site, listing them: AGENT-PROMPT
    STEP 6b, BROWSER-PASTE section 6b, READY-TO-FIRE new item 6b, HANDOFF.json
    `gates.trsx5_posted_body`, STATE.md's trsx5-contest block. Say plainly that his
    escalation was right and that the branch that protects the record could not have
    fired. Name the class: a comparison structurally incapable of firing — the same class
    this project has now hit repeatedly. **Quote the new card text IN FULL** (the
    READY-TO-FIRE item 6b version is the best one to quote — self-contained). State that
    his safest formulation was ADOPTED wholesale: size-first, hashes confirm only.
 2. **R1** — his withdrawal noted and accepted; the gate stands on the narrower
    records-integrity ground alone (do not bank output while the public record's contents
    are unknown), and we are not restating the stronger claim.
 3. **R3** — his ceiling figures are now in BOTH runbook deferral-vocabulary blocks:
    `0.0005 x n_var`, strict `>`; 60.0 at the 120,000 cap; 51.2 at region 1's 102,421;
    region 1's ~5 occlusions ~10x under. Attributed to his 2026-08-14 review.
 4. **R4** — registered as `R4-COVERAGE` in the phase deferred-items file; QUOTE the
    registered entry (or its substance) so he can check it says what he asked for:
    a methods/limitations disclosure obligation with the actual post-fire numbers, the
    remedy path recorded (banded mode `--r gz` + `--ld-window-*`; overlapping
    sub-windows; neither pre-fire), and the framing "nothing scientific is lost"
    explicitly RETIRED. Also: the Stage-B cost gate is relabelled
    **cost-per-bankable-region**, never cost-per-region-of-276, at all three sites that
    state it.
 5. **The anchor re-derivation transcript (D3)** — verbatim, so he can see the
    28ecdb31 / 9,758 anchor is mechanical and not asserted: the `F=` assignment, the two
    `awk ... | wc -c` / `| md5sum` lines, their outputs (`9758`,
    `28ecdb3160833da80cfa25952f76415b`), and the statement that `git show ac4c990:$F`
    gives byte-identical results and that the extraction EXCLUDES both marker lines.
 6. **His request (a) — the canonical 9,758-byte block.** Give Carter the exact command
    to produce it on demand, pre- or post-download (it is our own already-public text, so
    it does not wait on the adjudication):

    ```
    F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
    awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" > "$HOME/trsx5-canonical-9758.txt"
    wc -c   "$HOME/trsx5-canonical-9758.txt"    # must print 9758
    md5sum  "$HOME/trsx5-canonical-9758.txt"    # must print 28ecdb3160833da80cfa25952f76415b
    ```

    ⚠ Write the output OUTSIDE the repo (`$HOME`, as above) and state WHY in one line:
    a committed second copy of the canonical body would be a drift surface, and the
    amendment file is deliberately the single source. Do NOT create this file in this
    task — the command is the deliverable.
 7. **His request (b) — the 149-byte diff. Say what is true: WE DO NOT HOLD his
    9,907-byte body.** Grep-verified: only its md5 appears anywhere in our records. So we
    cannot compute the diff, and we are not going to promise one we cannot produce. Ask
    him to courier the 9,907-byte body (or its exact source); on receipt we produce the
    byte-level diff and send it back regardless of what the download shows.
 8. **Restate the standing positions:** the ledger's trsx5 entry stays UN-ANNOTATED
    toward either lineage until Carter's authenticated download adjudicates; an agent
    never fires the loop; nothing else is blocking from our side either.

Implement `verify.sh` section `reply` (written in Task 1):
  P1. The file exists and is >= 60 lines.
  P2. It contains all four section markers: `BLOCKING`, `R1`, `R3`, `R4`.
  P3. It contains the anchor transcript markers: `PASTE INTO OSF FROM HERE`, `9758`,
      `28ecdb3160833da80cfa25952f76415b`, `ac4c990`.
  P4. It contains `trsx5-canonical-9758` and `$HOME` (the out-of-repo output path) and
      does NOT contain a command writing that file anywhere under `.planning/`.
  P5. It contains an explicit non-possession sentence for the 9,907 body — assert both
      `9,907` and one of `do not hold` / `we do not have` / `cannot compute`.
  P6. Every hex run >= 20 chars in the file is length 32 or 40 (md5 or git SHA-1) — the
      same generic length invariant as F1, one document later.
  P7. `cost-per-bankable-region` (hyphen/case tolerant) appears.
  P8. The file does NOT create or claim a ledger annotation — assert it contains
      `un-annotated` or `stays neutral`.

Then run `bash .planning/quick/260814-guk-.../260814-guk-verify.sh all` — **must exit 0**
(all three sections green; this is the task-set gate).

Commit, explicit paths only:
`git add .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-REPLY-TO-SETH.md .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh`
message: `docs(260814-guk): reply-to-Seth courier package (BLOCKING confirmed + R1/R3/R4 + both requests answered)`.
DO NOT PUSH.
  </action>
  <verify>
    <automated>bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh all</automated>
  </verify>
  <done>
`verify.sh all` exits 0 — fire, record and reply sections all green, and the `all` run was
observed NON-ZERO at the end of Task 1, so the green is not vacuous. REPLY-TO-SETH.md
answers BLOCKING / R1 / R3 / R4 and both of Seth's requests, quotes the new card in full
and the anchor re-derivation verbatim, and states plainly that we cannot compute the
149-byte diff without his body. No canonical-body copy was committed to the repo. One
atomic commit, explicit paths, not pushed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo record -> Carter's irreversible action | The runbook card is the sole instrument between the record and a $385-1,084 non-refundable spend; a defect here is not caught downstream |
| Seth (external agent, no repo access) -> our record | Every value he supplies arrives couriered and unverifiable by us (OSF sits behind a sign-in wall) |
| our record -> Seth / the public OSF record | Anything we assert back becomes part of a record we will be held to |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-guk-01 | Tampering | trsx5 card adjudication branch | mitigate | Size-first adjudication (D2): a byte count cannot be mistranscribed into a false pass; the hash comparison is demoted to confirmation and can no longer be the sole gate. Enforced by verify.sh F4 (size mention must precede the hash). |
| T-guk-02 | Tampering | any hash literal in any card | mitigate | verify.sh F1/P6: a GENERIC hex-run length invariant over the card blocks (every run >= 20 chars must be exactly 32), proven able to fail by the Task-1 mutation negative control. Catches the next truncation, not just this one. |
| T-guk-03 | Spoofing | Seth-reported values presented as our own anchors | mitigate | The corrected 32-char value is ADVISORY ONLY and must appear inside a 4-line attribution window naming Seth and "unverified" (verify.sh F3). The 9,907/425d925a anchor is labelled Seth-reported everywhere. |
| T-guk-04 | Repudiation | the dated 2026-08-14 close record | mitigate | D4: dated bodies preserved verbatim; corrections land as dated clauses only. Enforced by verify.sh R3/R4 (status body opener still present; resume_on_reconnect[0] byte-identical to the task-entry revision). |
| T-guk-05 | Tampering | STATE.md frontmatter (byte-identity gate, unparseable YAML) | mitigate | verify.sh R5 md5-pins lines 1-24 against the task-entry revision; R6 pairs it with a non-vacuity assertion that the body block DID change and no hunk targets a line <= 24. |
| T-guk-06 | Denial of service | the fire path | mitigate | Docs-only: zero changes under src/, tests/, config/, Snakefile, docs/manuscript/ (asserted in Task 1's verify). No pytest run (it rewrites a tracked benchmark TSV). No perimeter contact. No agent fires anything. |
| T-guk-07 | Information disclosure | the trsx5 lineage contest | accept | The task deliberately does NOT annotate the ledger toward either lineage; the contest stays open until Carter's authenticated download adjudicates. Asserted in verify.sh P8. |
| T-guk-08 | Elevation of privilege | third copy of the card in READY-TO-FIRE (drift surface) | accept | Accepted with a recorded rationale (D5): size-first removes the false-pass mode that made copies dangerous, and a fire-blocking gate absent from Carter's only checklist is the worse failure. verify.sh F1-F5 run over all three copies, so drift is detected mechanically. |
</threat_model>

<verification>
Task-set gate (run from the repo root):

```
bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh all   # exit 0
python3 -c "import json;json.load(open('.planning/HANDOFF.json'))"                                  # exit 0
git status --short -- src/ tests/ config/ Snakefile docs/manuscript/                                 # empty
git log --oneline -3                                                                                 # 3 atomic commits, none pushed
```

Evidence that must appear in the SUMMARY (a green nobody has seen fail is not evidence):
- the pre-edit RED output of `verify.sh fire`;
- the observed FAIL text of the F1 mutation negative control;
- the observed NON-ZERO `verify.sh all` at the end of Task 1.
</verification>

<success_criteria>
- No executable trsx5 card can reach a PASS without a 9,758-or-9,907 byte count; the
  31-char literal is gone from the entire fire surface and from both live record fields.
- READY-TO-FIRE.md lists the fire-blocking gate as item 6b between items 6 and 7, with
  items 7-11 unrenumbered.
- Seth's R3 ceilings are in both vocabulary blocks; R4 is registered as R4-COVERAGE with
  its remedy path; "nothing scientific is lost" survives only inside its own retirement.
- The Stage-B cost gate reads cost-per-bankable-region at all three sites that state it.
- HANDOFF.json is valid JSON; dated 2026-08-14 bodies preserved; STATE.md lines 1-24
  byte-identical; STATE.md:1702 untouched (orchestrator's).
- REPLY-TO-SETH.md is couriable as-is and promises nothing we cannot compute.
- Three atomic commits, explicit paths, nothing pushed.
</success_criteria>

<output>
After completion, create
`.planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-SUMMARY.md`
carrying the three evidence items named in `<verification>`, the complete list of edited
sites, and any deviation (in particular: the BROWSER-PASTE cost-refinement paragraph is a
D6-adjacent THIRD relabel site added by this plan — record it as a stated scope addition,
not a silent one).
</output>
