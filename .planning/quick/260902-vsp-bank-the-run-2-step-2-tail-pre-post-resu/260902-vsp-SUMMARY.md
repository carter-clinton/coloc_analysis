---
phase: quick-260902-vsp
plan: 01
subsystem: m3-afr-ld-panel
tags: [bank-a-result, courier-to-seth, docs-only, pre-vs-post-filter, partial-confounding-tail, heterogeneity, definitional-disagreement, informative-carriers-no-floor, completion-check-not-a-prereg, nothing-fired, vm-stopped]

requires:
  - phase: quick-260901-rvu
    provides: "the tool that computes the PRE/POST split and the carrier distribution, and the 260901 PENDING PASTE runbook that governs RUN 2 STEP 2"
  - phase: quick-260826-qq9
    provides: "RUN 1's genuine pre-registration (260826 §(e)), confirmed 5/5 + histogram with ZERO adjustments on 2026-09-01"
provides:
  - "the banked RUN 2 STEP 2 result: the DEFINED-row tail is PRE-filter DOMINANT with a POST-filter RESIDUAL in every one of the 21 regions"
  - "the courier to Seth, in the same file, self-contained for a reader who was not in the session"
  - "a VERBATIM APPENDIX proven byte-equal at verification time to CONTENT-SPEC.md '## ARTIFACTS'..EOF — so no number was retyped"
  - "a precise two-pre-registration attribution: the three completion-check values are an INVARIANT CHECK, not a pre-registration"
  - "the 0.0005 live contradiction as an ACTION ITEM with four path:line citations, FLAGGED not fixed"
  - "SUPERSEDED 2026-09-04 (260904-dgi): that alleged contradiction was FALSE (withdrawn by 260903-ict), and the first correction then OVERSHOT — the constants are distinct and uncoupled at runtime but share a documented common origin"
affects: [m3-afr-ld-panel, seth-consultation, pcs-sweep, osf-preregistration]

tech-stack:
  added: []
  patterns:
    - "script-spliced verbatim appendix + a checker that re-reads BOTH files at verification time (byte-equality, not a length check)"
    - "prose-scoped ordering rule, so the appendix's own ordering is not 'fixed' to satisfy a headline rule"
    - "a banned-substring guard for a claim the record must NOT make (FLAG-1), scoped to the prose region"

key-files:
  created:
    - .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
    - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md
    - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
  modified:
    - .planning/STATE.md

key-decisions:
  - "The three values 3094 / 0 / 0 are recorded as a COMPLETION CHECK / INVARIANT CHECK and NOT as a pre-registration, and a prose-scoped banned-substring guard enforces it. 3094 was already measured in the smoke and carried forward; the two zeros follow by construction."
  - "The two pre-registrations are named separately and never merged: RUN 1's 260826 §(e) (genuine, CONFIRMED 5/5 + histogram, ZERO adjustments, containing NONE of the three values) and the 260901 PENDING PASTE (governs THIS run, deliberately states NO expected value, quoted and presented as a STRENGTH)."
  - "The spec's residual pre-correction phrase 'the three pre-registered values' inside its HONEST LIMITATIONS paragraph is reproduced UNEDITED in the appendix, because byte-equality is the guarantee that no number was retyped. It is annotated explicitly in the record's own HONEST LIMITATIONS section rather than silently smoothed."
  - "The plan's checker constants were updated to the corrected spec anchor and the renamed sections. The plan's Co-Authored-By clause was replaced because it was buggy, not because the trailer was wrong."

metrics:
  tasks_completed: 3
  files_created: 3
  files_modified: 1
  commits: 2
  completed: 2026-09-02
---

# Quick 260902-vsp: bank RUN 2 STEP 2 (tail PRE- vs POST-filter) Summary

The RUN 2 STEP 2 result is banked in the repo, in one self-contained file that is
simultaneously the bank record and the courier to Seth. **Seth has NOT been contacted.**
**Nothing was fired.** The VM stays STOPPED. $0.

## The result, in one line

The 3,094 DEFINED rows with `carriers_lost_frac >= 0.9` are **both** PRE-filter and
POST-filter — **PRE-filter dominant (2560 PRE / 534 POST of 3094 rows, POST 17.26%), with a POST-filter
residual present in every one of the 21 regions carrying tail rows.**

## The record

| property | value |
| --- | --- |
| path | `.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md` |
| size | 30938 B, 490 lines |
| md5 | `25ece5f3c724434d4f34b2b7025d50f9` |
| `###` subsections | 6 (the six scope caveats, each its own subsection) |
| source spec | `CONTENT-SPEC.md`, md5 `20fb7fa058b0e0c03ff669706f534349`, 10672 B, 157 lines |

## THE SPEC ANCHOR WAS VERIFIED BEFORE ANYTHING WAS WRITTEN

All three corrected anchors matched exactly, measured first:

```
md5   20fb7fa058b0e0c03ff669706f534349
bytes 10672
lines 157
```

The plan's STOP gate pinned the SUPERSEDED anchor (`d10acca5ca2b6c15548bb50d5c11bc43`,
8248 B, 124 lines). Per the brief this is a deliberate at-source correction, not drift, and
the record states so in its own provenance paragraph so the committed plan does not read as
a contradiction against the committed spec.

## Appendix byte-equality: GREEN

The appendix was spliced BY SCRIPT (anchor matched as a STRING, `## ARTIFACTS (on the AoU
VM, not in this repo)`; no hardcoded line numbers) and the checker re-reads BOTH files at
verification time:

```
GREEN — record structure, appendix byte-equality, headline ordering and all load-bearing
strings verified
```

10371 characters of slice, byte-equal. No number was retyped.

## RED observations (a green assertion is evidence ONLY if it has been seen fail)

**Six REDs observed, all on the REAL record / REAL tree. Nothing was inherited from the
planner's fixture observations.**

**NC-1 — one digit flipped inside the appendix (`3094` -> `3095`), on a scratchpad copy:**

```
RED (1):
  - APPENDIX IS NOT BYTE-EQUAL to CONTENT-SPEC '## ARTIFACTS'..EOF (got 10371 chars, want 10371)
```

⚠ **Identical character counts on both sides.** A length check alone would have passed this.
The byte comparison is what caught it.

**NC-2 — prose headline ordering inverted (first `1.99` and first `2.36` swapped), on a
scratchpad copy:**

```
RED (1):
  - prose leads with 2.36 before 1.99 — headline must be the REDUCED figure
```

**NC-3 — the `260902-vsp` STATE.md row deleted, on a scratchpad copy:**

```
RED (1):
  - expected exactly ONE 260902-vsp row, got 0
```

**NC-4 — the `260902-vsp` row moved ABOVE the `260826-qq9` row, on a scratchpad copy:**

```
RED (1):
  - 260902-vsp row must sit immediately after the 260826-qq9 row
```

All four scratchpad copies were deleted after use. The real record and the real tree were
re-checked GREEN after each control run.

**Two further REDs fired on the REAL artifacts during authoring — reported because they are
the same class of failure the project has baked feedback about:**

**R-5 — the FLAG-1 prose guard fired on my own negation sentence.** I added a guard that the
prose must not contain `pre-registered 3094`. It went RED on the sentence *"No sentence
anywhere claims that file pre-registered 3094 / 0 / 0"* — a sentence that MEANS the opposite
of what the guard bans. A grep gate matches text, not meaning. **I reworded the record rather
than weakening the guard**, because the guard is worth more than the phrasing.

**R-6 — a load-bearing token was destroyed by a line wrap.** `deferred-items.md` went RED on
`missing 'NO EXPECTED VALUE IS STATED'` because my prose had wrapped it as `### NO EXPECTED
VALUE\nIS STATED`. Unwrapped and re-run GREEN. Same failure mode as the baked
`feedback_grep_gate_matches_text_not_meaning` memory.

## STATE.md

Exactly ONE row appended, immediately after the `260826-qq9` row (found by string match, not
by hardcoded line number; it landed at line 2301). Six cells, no literal `|` anywhere in the
Description — the `pair_key` `9776035|9776036` was omitted from the row and is carried by the
record instead.

**Pure insertion, proven:**

```
 .planning/STATE.md | 1 +
 1 file changed, 1 insertion(+)
deleted lines: 0
```

The four missing rows (`260828-uej`, `260831-kw8`, `260901-l55`, `260901-rvu`) were **NOT**
backfilled — deliberately, per the brief. Nothing else in STATE.md was edited: no
`last_activity` frontmatter, no narrative section, no `HANDOFF.json`, and **no
`gsd-tools state *` command was run**, because every one of those would have edited lines
outside the single permitted insertion point.

## Deviations from Plan

### D1 [Rule 3 — blocking] The plan's checker pinned the SUPERSEDED spec anchor

**Found during:** Task 1, STEP 1.
**Issue:** the plan's automated checker hardcodes `d10acca5ca2b6c15548bb50d5c11bc43` / 8248 B
and would have `sys.exit`ed on the corrected spec.
**Fix:** the checker constants were updated to `20fb7fa058b0e0c03ff669706f534349` / 10672 B,
and a **third** assertion on the 157-line count was ADDED (the plan checked only md5 and
bytes). The corrected anchor was verified against the tree BEFORE any file was written.

### D2 [Rule 3 — blocking] The required section `## PRE-REGISTERED VALUES` no longer exists

**Found during:** Task 1, STEP 2.
**Issue:** the corrected spec replaced `## PRE-REGISTERED VALUES` with `## COMPLETION CHECK`
plus a new `## THE TWO PRE-REGISTRATIONS`. The plan's checker required the old heading, and
writing a section under that name would have made the record assert exactly what FLAG-1
forbids.
**Fix:** the record carries `## COMPLETION CHECK — THREE VALUES, ALL THREE PASS, AND THEY ARE
NOT A PRE-REGISTRATION` and `## THE TWO PRE-REGISTRATIONS — NAMED SEPARATELY, NEVER MERGED`.
The checker's required-heading list was updated to match. **14 `##` sections are now
required, not 13.**

### D3 [Rule 2 — missing critical guard] Added a prose-scoped banned-substring check

**Found during:** Task 1 verification.
**Issue:** the plan's checker could confirm what the record SAYS but nothing enforced what it
must NOT say — the single thing FLAG-1 exists to prevent.
**Fix:** the checker now fails if the PROSE region contains `three pre-registered values` or
`pre-registered 3094`. It is prose-scoped on purpose: the appendix contains the first of
those phrases and must not be touched. **This guard fired RED on the real record (R-5 above)
and changed the text.** The same guard was added to the STATE.md row check.

### D4 [Rule 1 — bug] The plan's `Co-Authored-By` verification clause was broken

**Found during:** Task 3 verification.
**Issue:** `git log -1 --format=%B | tail -1` reads a **blank** line, because `%B` appends a
trailing newline. The clause fails on any commit, correct trailer or not.
**Fix:** verified against the **raw commit object** instead — `git cat-file commit HEAD |
tail -3` shows the trailer as the genuine final line — plus `git log -1
--format='%(trailers:key=Co-Authored-By,valueonly)'` parsing it as a real trailer. The
corrected clause was itself given a negative control (a fabricated `subject\n\nbody\n`
message) and went **RED as expected**. **The trailer was correct all along; the checker was
not.**

### D5 [scope] `deferred-items.md` carries a third entry the plan did not enumerate

The plan asked for two DEFERRED entries plus the FLAG-1 report. The FLAG-1 entry additionally
records the spec's residual `"the three pre-registered values"` phrase inside its own HONEST
LIMITATIONS paragraph, reproduced unedited in the appendix and annotated in the record. See
FLAG-3 below.

## FLAGS FOR CARTER — reported, NOT reconciled

**FLAG-1 (the planner's, RESOLVED at source, honoured here).** The record names both
pre-registrations separately. RUN 1's `260826` §(e) is stated as genuine and CONFIRMED 5/5 +
the offset histogram with ZERO adjustments on 2026-09-01, and verified to contain **zero
occurrences** of `n_tail_rows_in`, `n_tail_rows_out_of_scope` or `n_defined_rows_out_of_scope`
(measured: 0 / 0 / 0). The `260901` PENDING PASTE's `### NO EXPECTED VALUE IS STATED` block at
`:211-216` is quoted in full and presented as a **STRENGTH**. No sentence anywhere in the
record, the STATE.md row or the commit message calls `3094 / 0 / 0` a pre-registration, and a
guard enforces it.

**FLAG-2 (the planner's).** Four quick tasks still have no STATE.md `Quick Tasks Completed`
row. Not backfilled — recorded in `deferred-items.md`. ⚠ Additionally measured while placing
the new row: the table's existing `260826-qq9` row carries only **3** cells, not 6. That is
PRE-EXISTING, was NOT touched, and belongs with the backfill.

**FLAG-3 (NEW — mine).** `CONTENT-SPEC.md`'s own `## HONEST LIMITATIONS` paragraph still
contains the pre-correction phrase **"the three pre-registered values"**. It is now the only
place in the committed artifact set that calls them one. It is reproduced UNEDITED in the
appendix, because byte-equality is the whole guarantee that no number was retyped; the record
annotates it explicitly and states the COMPLETION CHECK section governs. **Correcting that
phrase would move the spec's md5 and invalidate the anchor this record was built against —
that is Carter's decision, not a silent tidy.**

## Deferred

⚠ **SUPERSEDED 2026-09-04 (`260904-dgi`).** The alleged contradiction was FALSE and was
withdrawn by `260903-ict`; `260904-dgi` then found that correction **overshot** — the two
constants are distinct live parameters with no runtime coupling, **but they are not
unrelated**: mk7ze records that the occlusion gate reused *"the same fractional gate as the
withdrawn ceiling, re-purposed to exclusions"*, so the shared value has a documented common
origin. The courier heading cited here no longer exists. **The historical description below
is left unedited on purpose** — rewriting it would falsify the log.

1. **The `0.0005` LIVE CONTRADICTION** — `pairwise_completeness_scan.py:45` calls it
   withdrawn; `write_conditioned_ld_npz.py:17` calls it pre-registered; it is the live default
   at `condition_ld_matrix.py:120` and `write_conditioned_ld_npz.py:64`. All four verified
   present in the tree at execution time. **FLAGGED, NOT FIXED.** Discharge: a separate quick
   that decides, makes the docstrings agree, and lands a **named enforcer test**.
2. **The four missing STATE.md rows** — discharge: a separate quick that writes each row from
   that task's own SUMMARY.

## Scope gate: docs-only held

```
git status --porcelain -- src tests            -> EMPTY
git status --porcelain -- .planning/amendments  -> EMPTY
git diff HEAD~1 --name-only -- src tests .planning/amendments -> EMPTY
predecessor records (260901 / 260826 / 260825)  -> zero diff
.planning/debug/m3-producer-unbounded-dense-read.md -> still UNTRACKED, never staged
```

The staged set was proven equal to the intended five paths by `diff` against a literal list
before committing. No `git add -A`, no `git add .`.

## Commits

| commit | what |
| --- | --- |
| `b16bc2b` | the work: record + CONTENT-SPEC + deferred-items + PLAN + the STATE.md row — **exactly five paths**, `Co-Authored-By` trailer as the final line |
| (close-out) | this SUMMARY |

The work commit is the ONE commit the plan pinned, and `git diff HEAD~1 --name-only` was
verified equal to the five intended paths **at that commit**. This SUMMARY is a separate
close-out commit, matching the repo's own precedent (`260901-rvu`, `260901-l55`), so the work
commit's verified five-path property is preserved.

**NOTHING WAS PUSHED.**

## Nothing fired

Zero AoU VM, Dataproc, `gcloud`, `gsutil`, OSF or network contact. **$0.** The VM stays
STOPPED and no step here suggests starting it. `.planning/amendments/` untouched; the posted
July amendment never opened. **Seth has NOT been contacted — the courier exists in the repo;
sending it is Carter's call.**

## Self-Check: PASSED

All six claimed files exist on disk; the claimed commit `b16bc2b` exists in `git log --all`;
the record's claimed md5 `25ece5f3c724434d4f34b2b7025d50f9` and size 30938 B / 490 lines were
re-measured; the STATE.md row is at line 2301; and BOTH checkers were re-run GREEN against the
committed tree after the commit.
