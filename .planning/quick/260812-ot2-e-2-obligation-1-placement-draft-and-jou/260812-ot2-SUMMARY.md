---
phase: quick-260812-ot2
plan: 01
subsystem: planning-docs
tags: [e-2, track-a, manuscript-placement, journal-selection, decisions-ledger]
requires: []
provides:
  - "Placement-ready SPEC for ms-correction-v2 (byte-verified paste block, P-1/P-2 fork)"
  - "Nature-first journal-selection memo with per-venue pre-placement-check column"
  - "DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip ledger entry"
affects: [carter-placement-of-e2-obligation-1, venue-selection]
key-files:
  created:
    - .planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-placement-draft-ms-correction-v2.md
    - .planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-journal-selection-memo.md
  modified:
    - .planning/DECISIONS.md (append-only, +80/-0)
decisions:
  - "DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip: obligation (1) prepped placement-ready + Nature-first venue re-target; obligation (2) SKIPPED by direction (DEFERRED, NOT DISCHARGED)"
metrics:
  duration: "9 min"
  completed: "2026-08-12"
  tasks: 3
  files: 3
---

# Quick Task 260812-ot2: E-2 obligation (1) placement draft + journal-selection memo Summary

Placement-ready SPEC for `ms-correction-v2` (paste block cmp-proven byte-identical
to the v2 pair, negative control observed red first) + Nature-first journal ladder
memo with honest top-3 + one appended DECISIONS.md entry recording both 2026-08-12
directives; obligation (2) stays UNDISCHARGED by explicit record.

## Deliverables

| Deliverable | Path | Commit |
|---|---|---|
| Placement SPEC (8 sections; byte-locked paste block; P-1/P-2 fork; Limitations pointer; verification record; stale-header note) | `.planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-placement-draft-ms-correction-v2.md` | `3acc77d` |
| Journal-selection memo (Nature-first ladder; 11-venue table incl. pre-placement-check column; conditional Track-A-pending paragraph; sources + flags) | `.planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-journal-selection-memo.md` | `0572a67` |
| Ledger entry `DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip` (append-only, +80/-0) | `.planning/DECISIONS.md` | `aca9138` |

## Observed verification outputs

**Task 1 — the byte gate, negative control FIRST (observed red before green was
trusted):**

- Machine extraction of the `ms-correction-v2` block from the v2 source:
  **15 lines / 3,429 bytes** — exactly the planner's measurement.
- NEGATIVE CONTROL: one-character perturbation (line 2, `We` → `Xe`) of a
  scratchpad copy (never committed); same cmp shape against the source
  extraction → observed output:
  `/dev/fd/63 [scratchpad]/ms-block-perturbed.txt differ: byte 40, line 2`,
  **exit=1 (RED)**.
- GREEN run on the committed draft: `cmp` of the two anchored sed extractions →
  **BYTE-IDENTICAL** (exit 0).
- Marker uniqueness in the draft: `grep -cx` = **1** for each of
  PASTE-BEGIN / PASTE-END.
- Number/framing greps: pooled-figure grep exit=1 (absent); the s-word pipeline
  empty (only the paste block's own negated form, filtered as required); the
  r-word grep exit=1 (absent).
- Full plan gate → **TASK1-PASS**.

**Task 2:** all nine presence greps green; no E-2 figure pattern anywhere; no
forbidden framing word anywhere → **TASK2-PASS**.

**Task 3:** entry present; cross-ref to `DEC-2026-08-11-e2-framing-correction`
present; UNDISCHARGED/NOT DISCHARGED stated in the entry; commit numstat
deletions = **0** (append-only proven) → **TASK3-PASS**.

**Plan-level:** `git status --porcelain` over `docs/manuscript/ src/ tests/
config/ Snakefile results/ .planning/amendments/` shows only the pre-existing
untracked `results/track_a_aggregations/phase5_overview.tsv` (present in the
git status snapshot before this task started; untouched). Each of the three
commits staged exactly its declared explicit path. Other quick dirs
(260811-oku/tf3/rcw, 260812-09a) untouched. `docs/manuscript/id-vs-ref-LD.md`
byte-unchanged (porcelain-clean at every task gate).

## Decision coverage (CONTEXT.md LOCKED items → deliverable sections)

- No-agent-edits rule → SPEC §1 + verified porcelain-clean manuscript (T-ot2-05).
- Byte-lock → SPEC §4 (machine-extracted block) + §7 (recorded cmp + red control) (T-ot2-01).
- (2)-skip + coherence consequence → SPEC §5 (P-1 recommended / P-2 marked variant) + ledger entry §Directive 2 and §fork (T-ot2-02).
- Memo scope (Nature-first, honest ranking, pre-placement column, conditional-pending, flags) → memo §1–§6 (T-ot2-03: status asserted nowhere).
- Number/framing rules → greps in all three verify gates, all green.
- Process constraints → explicit-path staging on all three commits; DECISIONS.md +80/-0 (T-ot2-04); $0; zero perimeter contact; nothing posted.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None — all three deliverables are complete documents; no placeholder content,
no unwired data.

## Threat Flags

None — no new security-relevant surface; docs-only changes on the declared
paths.

## Commits

- `3acc77d` — docs(quick-260812-ot2): placement-ready SPEC for ms-correction-v2 — byte-verified paste block, P-1/P-2 closing fork
- `0572a67` — docs(quick-260812-ot2): journal-selection memo — Nature-first ladder, honest fit ranking, per-venue pre-placement check
- `aca9138` — docs(quick-260812-ot2): ledger — DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip (obligation (2) deferred, not discharged; Nature-first venue re-target; P-1/P-2 fork)

## Standing next step

**Carter's, never an agent's:** place `ms-correction-v2` into
`docs/manuscript/id-vs-ref-LD.md` per the SPEC (a <=2-minute action), choosing
**P-1 (recommended)** or **P-2** for the closing sentence at placement; venue
actions follow the memo's Nature-first ladder. Then the m3-04c Task 3 fire
gate sequence — owned by Carter, never an agent. Obligation (2) remains
UNDISCHARGED (deferred by direction); its discharge condition is unchanged.

## Self-Check: PASSED

- All three deliverable files exist on disk; `.planning/DECISIONS.md` present.
- All three commits (`3acc77d`, `0572a67`, `aca9138`) exist; each commit's
  tree and blobs verified readable (`git cat-file -e` + `git show` OK).
- The perturbed negative-control copy exists only in the session scratchpad;
  never staged, never committed (`git status` clean of it).
- ⚠ Pre-existing repo observation (NOT caused by this task, flagged for the
  standing GPFS recovery recipe): history walks that diff older commits hit
  `fatal: unable to read tree` on at least two historical tree objects
  (`978258f9…`, `cb69d8c0…`) — the known recurring GPFS loose-object-loss
  pattern. All objects of this task's three commits verify intact.
