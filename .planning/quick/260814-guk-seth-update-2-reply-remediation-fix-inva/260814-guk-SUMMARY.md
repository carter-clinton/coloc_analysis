---
phase: quick-260814-guk
plan: 01
subsystem: fire-surface + live record
tags: [trsx5, pre-registration, fire-gate, seth, disclosure, negative-control]
requires: [260812-ox1 runbook package, 260813-t21 producer gates]
provides:
  - size-first trsx5 adjudication card at all five sites
  - READY-TO-FIRE item 6b (the fire-blocking gate, previously absent)
  - R4-COVERAGE disclosure obligation with remedy path
  - 260814-guk-verify.sh (generic hex-run length invariant, mutation-proven)
  - reply-to-Seth courier package
affects: [m3-04c Task 3 fire path, HANDOFF.json, STATE.md, deferred-items.md]
tech-stack:
  added: []
  patterns: [generic-length-invariant-over-expected-value-list, committed-named-baseline-instead-of-moving-git-ref, paired-positive-negative-control]
key-files:
  created:
    - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh
    - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-baseline.txt
    - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-REPLY-TO-SETH.md
  modified:
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
    - .planning/HANDOFF.json
    - .planning/STATE.md
    - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
decisions:
  - "Size-first adjudication adopted wholesale (Seth's safest formulation): a byte count cannot be mistranscribed into a false pass, so the hash is demoted to confirmation."
  - "F1/P6 are GENERIC hex-run length invariants, deliberately not expected-hash lists — an expected-hash list is blind to the truncation class by construction."
  - "DECLINED the checker's optional R9 (byte-pinning STATE.md:1702) — the orchestrator edits that exact line immediately after execution, so the pin would be green once and red forever after."
metrics:
  duration: ~50 min
  tasks: 3
  commits: 3
  checks: 26 (10 fire / 8 record / 8 reply)
  completed: 2026-08-14
---

# Quick Task 260814-guk: Seth UPDATE #2 Remediation Summary

**One-liner:** The trsx5 pre-fire gate carried a 31-character "md5" that could never
match, making its STOP-truncated branch structurally incapable of firing one step
before a $385–1,084 irreversible spend; all five executable/live copies were rewritten
**size-first**, the missing fire-blocking gate was added to Carter's primary checklist
as item 6b, Seth's R3 ceilings and R4 coverage-gap disclosure were recorded, and the
whole surface is now held by a generic hex-run **length** invariant proven able to fail.

## What shipped

| Task | Commit | Substance |
|---|---|---|
| 1 | `28294aa` | size-first card at all three runbook sites + READY-TO-FIRE item 6b + R3/R4 vocabulary + the checker |
| 2 | `16d6e80` | dated corrections in HANDOFF.json (gate field + status) and STATE.md line 34; `R4-COVERAGE` registered; containment baseline pinned |
| 3 | `fbc5d19` | reply-to-Seth courier package |

Nothing pushed (the orchestrator pushes). `$0`, zero perimeter contact, nothing fired.

## Evidence required by `<verification>` (a green nobody has seen fail is not evidence)

### 1. Pre-edit RED of `verify.sh fire` — the checker was written FIRST

Run before touching any runbook file. **F1 caught the actual shipped defect:**

```
FAIL  F1 [AGENT-PROMPT] hex run(s) in the card block are not 32 chars:
  len=31  c19e8b2ad7cd6a45fee1d668d8a9cf9
FAIL  F1 [READY-TO-FIRE] card block is empty or under 5 lines — heading not found, invariant would be VACUOUS
FAIL  F2 [AGENT-PROMPT] card block is missing c19be8b2ad7cd6a45fee1d668d8a9cf9
FAIL  F2 [BROWSER-PASTE] card block is missing 425d925a88ab474ec2396cbea25e665c
FAIL  F2 [BROWSER-PASTE] card block is missing c19be8b2ad7cd6a45fee1d668d8a9cf9
FAIL  F2 [READY-TO-FIRE] card block is missing 28ecdb3160833da80cfa25952f76415b
FAIL  F2 [READY-TO-FIRE] card block is missing 425d925a88ab474ec2396cbea25e665c
FAIL  F2 [READY-TO-FIRE] card block is missing c19be8b2ad7cd6a45fee1d668d8a9cf9
PASS  F3  every advisory-hash line is attributed (Seth + unverified) within a 4-line window
FAIL  F4 [AGENT-PROMPT] card is HASH-FIRST: 9,758 first appears on block line 7, 28ecdb31 on 7 (need strictly before)
FAIL  F4 [BROWSER-PASTE] card is HASH-FIRST: 9,758 first appears on block line 4, 28ecdb31 on 4 (need strictly before)
FAIL  F4 [READY-TO-FIRE] card block lacks a 9,758 mention or the canonical hash
FAIL  F5  invalid literal still on the fire surface: full=1 prefix=2 (both must be 0)
PASS  F6  anchor re-derived: 9758 / 28ecdb3160833da80cfa25952f76415b on the working tree AND at ac4c990
FAIL  F7  missing one of '## 6.' / '## 6b' / '## 7.' in READY-TO-FIRE (6=102 6b= 7=108)
FAIL  F8 [AGENT-PROMPT] vocabulary block is missing '60.0'   (+ 51.2 / Seth / 102,421)
FAIL  F8 [READY-TO-FIRE] vocabulary block is missing '60.0'  (+ 51.2 / Seth / 102,421)
FAIL  F9 [AGENT-PROMPT] cost block does not read cost-per-bankable-region
FAIL  F9 [READY-TO-FIRE] cost block does not read cost-per-bankable-region
FAIL  F9 [BROWSER-PASTE] cost block does not read cost-per-bankable-region
PASS  F10 the retired framing appears 0 times in the runbooks

RESULT: FAILURES PRESENT (section: fire)   EXIT=1
```

Note F1's second line: an unmatched heading yields an **empty** block, and an empty
block passes a length invariant trivially. That non-vacuity guard was built in from
the start, and it fired.

### 2. F1 mutation negative control — OBSERVED RED (mandatory, and the point)

F1's logic is exposed as the `_hexlen` sub-mode, so the control exercises the
**shipped code path**, not a re-implementation. Run with a **paired positive
control** so the FAIL is attributable to the mutation and nothing else:

```
### POSITIVE CONTROL (unmutated, cleaned copy) ###
PASS  _hexlen(.../card_clean.txt): every hex run >=20 chars is exactly 32 (lines with runs: 2)
exit=0

### diff of the one-character mutation ###
7c7
<   28ecdb3160833da80cfa25952f76415b (9,758 bytes)  = repo canonical paste block
---
>   8ecdb3160833da80cfa25952f76415b (9,758 bytes)  = repo canonical paste block

### NEGATIVE CONTROL (one hex char deleted) ###
FAIL  _hexlen(.../card_mutated.txt): hex run(s) present that are not 32 chars:
  len=31  8ecdb3160833da80cfa25952f76415b
exit=1
```

(The pre-existing 31-char literal was stripped from the scratch copy first, so the
control is unambiguous: the two files differ by exactly one character.)

**P6 was independently controlled too** — deleting one character from
`425d925a88ab474ec2396cbea25e665c` in a scratch copy of the reply makes P6's logic
report `len=31`, proving the narrow exemption (below) did not neuter the check:

```
  P6 WOULD FAIL: len=31  425d925a88ab474ec2396cbea25e65c
```

### 3. `verify.sh all` observed NON-ZERO at the end of Task 1

`EXIT_FIRE=0` and `EXIT_ALL=1` at Task 1 close — the record and reply sections were
genuinely red then, so the final `all` green (26/26) is not vacuous.

### Final gate

```
bash 260814-guk-verify.sh all   -> 26/26 PASS, exit 0
python3 -c "import json;json.load(open('.planning/HANDOFF.json'))" -> exit 0
git status --short -- src/ tests/ config/ Snakefile docs/manuscript/ -> 0 lines
```

## Complete list of edited sites

**Fire surface (executable cards, all rewritten size-first):**
1. `260812-ox1-AGENT-PROMPT.md` STEP 6b — 4-element card in the file's plain-text register.
2. `260812-ox1-BROWSER-PASTE.md` §6b — markdown register, `[RUNBOOK]`/`[DERIVED @HEAD]` provenance preserved.
3. `260812-ox1-READY-TO-FIRE.md` **item 6b (NEW)** — self-contained, inserted between items 6 and 7, **items 7–11 unrenumbered** (AGENT-PROMPT STEP 10 and BROWSER-PASTE §7 cite "item 7" by number).

**Other runbook edits:**
4. AGENT-PROMPT STAGE C HOLD LIFTED — R3 ceilings.
5. AGENT-PROMPT STEP 9 GATE — cost-per-bankable-region.
6. BROWSER-PASTE cost-refinement gate — cost-per-bankable-region (scope addition, see Deviations).
7. READY-TO-FIRE §10 Deferral vocabulary — R3 ceilings + extended post-fire disclosure duty (methods/limitations placement, remedy path, retired framing).
8. READY-TO-FIRE item 11-C — cost-per-bankable-region.
9. READY-TO-FIRE "Contents:" line — no longer contradicted by the added item.

**Live record:**
10. `HANDOFF.json` `gates.trsx5_posted_body` — size-first, `c19e8b2` gone, dated `⚠ CORRECTED 2026-08-14` in the `gates.m3_04b` house style.
11. `HANDOFF.json` `status` — ONE dated superseding clause on top; the 2026-08-14 close body preserved verbatim.
12. `STATE.md` line 34 — corrected in place **as a single line**, so all downstream line numbers (incl. 1702) are preserved.
13. `deferred-items.md` — `R4-COVERAGE` appended under a new dated header.

**Deliberately NOT touched:** `HANDOFF.json` `resume_on_reconnect[0]` (D4 — byte-verified unchanged by R4), `STATE.md:1702` Session Continuity (the orchestrator's edit), the trsx5 **ledger** (the contest stays open), the PRE-FIRE 1b signature lines.

Diff containment, measured: `STATE.md @@ -34 +34 @@` only; `HANDOFF.json @@ -9 +9 @@` and `@@ -73 +73 @@` only.

## Deviations from Plan

### 1. [Rule 1 — plan-internal contradiction] P6 vs D7's mandated 31-char quotation

- **Found during:** Task 3.
- **Issue:** P6 as written requires *every* hex run ≥20 chars in the reply to be 32 or 40. D7 item 1 (and the must_have "Seth has a courier package that confirms the 31-char count firsthand") requires the reply to quote the invalid 31-character literal verbatim — that IS the firsthand confirmation Seth asked for. As specified the two are jointly unsatisfiable.
- **Fix:** the narrowest resolution that preserves both, and is *stronger* than a blanket exemption: P6 exempts **only** the one known-invalid literal, **and** additionally asserts that every line carrying it also carries the count `31` (i.e. it may appear only where presented as the defect, never as an anchor). Every other off-length run still fails.
- **Proven non-vacuous:** the P6 negative control above.
- **Verified:** the literal occurs exactly once in the reply, at line 15, on the `wc -c # -> 31` line.

### 2. [Stated scope addition, per the plan's own instruction] BROWSER-PASTE cost-refinement gate

D6 names two cost-relabel sites; the BROWSER-PASTE **cost-refinement gate** paragraph is a third live instance of the identical claim in the same document family. Left uncorrected it re-creates exactly the divergent-copy class `DEC-2026-08-12` consolidated against. Applied and named here as the plan directed — recorded as a **stated** scope addition, not a silent one. F9 now checks all three sites.

### 3. [Rule 1 — self-inflicted, caught by the checker] F10 fired on my own edit

Writing READY-TO-FIRE §10's retirement sentence, I reproduced the retired phrase verbatim on the fire surface, and F10 (which I had written ~20 minutes earlier) went red on it. Corrected: READY-TO-FIRE now states the prohibition **without** reproducing the phrase and points at `R4-COVERAGE`, where it is quoted once and only once inside its own retirement (R8 asserts that match line also says `RETIRED`). This is a live instance of the project's standing lesson that freshly-authored guards deserve *more* scrutiny than inherited ones — here the guard earned its keep against its own author.

### 4. Checker cosmetics folded in while writing (not scope changes)

- `260814-guk-baseline.txt` was omitted from Task 2's `files` element though Step 1 creates it — created and committed as the steps say.
- The plan's stray unlabeled `9.` between F8 and F10 is implemented and reported as **F9**.

## DELIBERATE DECLINE — the checker's optional R9 (byte-pinning `STATE.md:1702`)

**Not added, as a decision rather than an omission.** R9 would have md5-pinned
`STATE.md:1702` in the baseline. The orchestrator edits *that exact line* immediately
after this execution (the Session Continuity refresh), so the pin would be green
exactly once and red forever after — the project's fixed-pin timebomb class
(`[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]`, the seventh
structurally-incapable assertion of the 2026-08 arc, which we wrote ourselves). The
containment property R9 was reaching for is already held by R5 (frontmatter 1–24
md5-pinned) plus R6 (no diff hunk targets a line ≤ 24), neither of which decays.
Line 1702 is additionally protected in practice because the STATE.md edit was made
**in place as a single line**, leaving the total line count unchanged (`wc -l` = 2456
before and after; the in-place assertion used Python's `split("\n")`, which reports
2457 because of the trailing newline — same file, two conventions, reconciled here
rather than shipped as a bare number).

## Threat register — dispositions honoured

`T-guk-01` size-first (F4) · `T-guk-02` generic length invariant, mutation-proven (F1/P6) · `T-guk-03` attribution containment (F3) · `T-guk-04` dated bodies preserved (R3/R4) · `T-guk-05` frontmatter pinned + non-vacuity pair (R5/R6) · `T-guk-06` docs-only, 0 files under `src/ tests/ config/ Snakefile docs/manuscript/`, no pytest, no perimeter contact · `T-guk-07` ledger accepted-open (P8) · `T-guk-08` third copy accepted with recorded rationale, drift detected mechanically (F1–F5 over all three copies).

## Known Stubs

None. No placeholder values, no unwired data paths — this task produced documents and
one checker, all of which execute against real files.

## Threat Flags

None. No new network endpoint, auth path, file-access pattern or schema change; the
only new executable is a read-only local checker that touches no credentials and makes
no network or perimeter calls.

## Carter-facing state after this task

The fire is still **staged, gated and unfired**. What changed is that the instrument
Carter runs before committing $385–1,084 can now actually fail. Unchanged and still
his alone: the trsx5 download (item 6b), the PRE-FIRE 1b signature, and the fire
itself. **An agent never fires it.** The trsx5 ledger entry remains **un-annotated**
toward either lineage. `260814-guk-REPLY-TO-SETH.md` is couriable as-is.

## Self-Check: PASSED

All 4 created files verified present on disk; all 3 commit hashes (`28294aa`, `16d6e80`, `fbc5d19`) verified in `git log`; `verify.sh all` re-run 26/26 PASS; 0 files changed under `src/ tests/ config/ Snakefile docs/manuscript/`; 3 commits unpushed as required. One number reconciled during self-check (STATE.md line count, `wc -l` 2456 vs `split("\n")` 2457) rather than shipped unreconciled.
