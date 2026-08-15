---
phase: quick-260815-i2v
plan: 01
subsystem: courier-record
tags: [courier, seth, lineage, osf-remediation, refuted-hypothesis, fire-held]
requires: [260814-u9p-LINEAGE-DIFF-149.md, 260814-u9p-REPLY-TO-SETH.md, 260814-guk-verify.sh]
provides: [260815-i2v-REPLY-TO-SETH-lineage-reconciled.md]
affects: [.planning/quick/260815-i2v-courier-reply-to-seth-149-byte-lineage-d/]
tech-stack:
  added: []
  patterns: [transcribe-never-re-derive, gate-proved-by-negative-control, full-digest-invariant-32-64]
key-files:
  created:
    - .planning/quick/260815-i2v-courier-reply-to-seth-149-byte-lineage-d/260815-i2v-REPLY-TO-SETH-lineage-reconciled.md
    - .planning/quick/260815-i2v-courier-reply-to-seth-149-byte-lineage-d/260815-i2v-PLAN.md
    - .planning/quick/260815-i2v-courier-reply-to-seth-149-byte-lineage-d/260815-i2v-GATE-CONTROLS.md
  modified: []
decisions:
  - "The u9p no-64-char-hex rule is INVERTED here: the full 64-char sha256 arrived complete and the reply carries it unabbreviated; truncation is forbidden."
  - "Our own formatting-strip hypothesis is reported REFUTED in its own lettered section, not as a footnote under the good news."
  - "Independence binds harder after two dead hypotheses: no characterization of the posted 9,695-B body is sent before Seth publishes his."
metrics:
  duration: ~12 min
  tasks: 1
  files: 3
  completed: 2026-08-15
---

# Quick 260815-i2v: Courier reply to Seth — 149-byte lineage delta reconciled Summary

Courier-out reply banked in-repo closing the 149-byte lineage delta as **reconciled exactly**
(prose byte-identical; `76 + 74 + 2 = 152`, `152 - 3 = 149`) and reporting **our own**
formatting-strip hypothesis as **REFUTED** by a 72-candidate sweep with zero hits, with the
hand-count error that motivated it named plainly.

## What was done

One document written, gated, and committed atomically:
`.planning/quick/260815-i2v-courier-reply-to-seth-149-byte-lineage-d/260815-i2v-REPLY-TO-SETH-lineage-reconciled.md`
(156 non-blank lines; min was 70).

Sections (a)-(g) as specified by the plan:

- **(a)** Re-send arrival verified at every step — 8 chunk md5s, 13,212 `body.b64` chars,
  9,907 decoded, md5 + full sha256 matched. Chunked-with-per-chunk-md5 credited
  non-perfunctorily; noted the `{32, 64}` hex-run widening landed *before* his anchor needed it.
- **(b)** ★ The 149 bytes reconcile exactly; prose **byte-identical**; all 11 headers and the
  four inline-value fields identical; Seth credited for the structural-map correction; the
  decomposition table and closing arithmetic line reproduced literal-exact; the "whichever
  lineage is true, the science is the same" consequence stated; the *"What is withdrawn"*
  bullet asymmetry and the 3 `awk`-boundary bytes disclosed.
- **(c)** ⛔ Our hypothesis **REFUTED** — direct-candidate table (H5/H6/H7 vs target H3), the
  72-candidate sweep with zero md5 matches, zero size-only matches, nothing reaching 9,695 B;
  the hand-count error reported without softening (44 correct; bullets counted 9, actually
  12 ours / 13 his; 150-vs-149 and 62-vs-63 near-agreements were partly luck from two errors
  of opposite sign cancelling; the earlier draft missed the 3 boundary bytes).
- **(d)** Two sweeps, two directions, still an **unexplained third body**.
- **(e)** Independence reaffirmed and stated as binding **harder**, not less.
- **(f)** Fire **HELD**, obligation-(2) **HELD**, STOP verdict unchanged (adjudicated on
  **size alone**), new OSF version never a silent swap.
- **(g)** Nothing further needed from Seth until Carter ships the 9,695-B body; **size-first
  on arrival**.

Every number and digest was **transcribed** from the plan's HASH/NUMBER tables. Nothing was
re-measured; the banked 9,907-B body was never opened, decoded, or normalized by this task.

## Verification

| check | result |
|---|---|
| Plan `<automated>` block | **exit 0** — V1, `_hexlen`, V2, V3, V4, V5, V6, V7, V8 all PASS |
| `260814-guk-verify.sh fire` (pre-write baseline) | 10/10 ALL CHECKS PASSED |
| `260814-guk-verify.sh fire` (post-commit) | **10/10 ALL CHECKS PASSED** — unregressed |
| Untouchables (`STATE.md`, `ROADMAP.md`, three §6b cards) | `git status --porcelain` **empty** |
| Commits for this quick | exactly **1** — `840c986` |
| Pushed | **no** — 1 unpushed commit on `m3-W2-aou-deltas`; orchestrator pushes |
| Cost / network | **$0**, zero network, zero OSF, zero perimeter contact, nothing fired |

The gate earned its keep: **V6 fired RED on the first run** because the rule sentence
*"A hand count that agrees with a measurement is still not a measurement"* had been
line-wrapped and was therefore not present as a contiguous literal. Fixed by promoting it to
its own blockquote line. That is a live demonstration that the coverage checks are not
decorative — the same class of defect (a claim that reads correctly to a human but does not
match when measured) is exactly what this whole investigation is about.

## Deviations from Plan

None. The plan executed as written. The single mid-task correction (V6 RED → rule sentence
un-wrapped) was the gate working as designed, inside Task 1, before staging — not a deviation
from the plan's instructions.

## Known Stubs

None.

## Threat Flags

None. No new network endpoint, auth path, file-access pattern, or schema change; the task
wrote one markdown document and committed three markdown files.

## Notes for the orchestrator

- This SUMMARY is **uncommitted** by design (single-commit constraint; closeout, STATE.md and
  the push belong to the orchestrator).
- `git log origin/HEAD..HEAD | wc -l` reports 1302 because `origin/HEAD` tracks `main`; the
  branch-relative check `git log origin/m3-W2-aou-deltas..HEAD` shows exactly **1** unpushed
  commit, which is `840c986`.

## Self-Check: PASSED

- FOUND: `260815-i2v-REPLY-TO-SETH-lineage-reconciled.md`
- FOUND: `260815-i2v-PLAN.md`
- FOUND: `260815-i2v-GATE-CONTROLS.md`
- FOUND: commit `840c986`
