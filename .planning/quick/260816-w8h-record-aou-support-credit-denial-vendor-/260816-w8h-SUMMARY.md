---
phase: 260816-w8h
plan: 01
subsystem: planning-record
tags: [aou, support-ticket-57144, credit-denial, fire-surface, skill, decisions]
requires: []
provides:
  - "DEC-2026-08-16-aou-credit-request-denied (DECISIONS.md)"
  - "NO CREDIT BACKSTOP note at READY-TO-FIRE item 6 / GATE 1"
  - "vendor-confirmed annotation on aou-ld-pipeline invariant 1"
affects:
  - ".planning/DECISIONS.md"
  - ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md"
  - ".claude/skills/aou-ld-pipeline/SKILL.md"
tech-stack:
  added: []
  patterns: ["vendor position recorded separately from our reading", "fire-surface edit gated by byte-identity + F1-F10"]
key-files:
  created: []
  modified:
    - ".planning/DECISIONS.md"
    - ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md"
    - ".claude/skills/aou-ld-pipeline/SKILL.md"
decisions:
  - "AoU credit request DENIED, final — no appeal will be pursued; the ~$2,100 is spent"
  - "Their mt.checkpoint() sentence ACCEPTED as independent corroboration; the rest UNACCEPTED"
  - "Repro-example offer DECLINED-BY-LAPSE (targets the killed Hail producer)"
metrics:
  tasks: 3
  commits: 3
  files_changed: 3
  lines_added: 88
  lines_deleted: 0
  cost_usd: 0
  completed: 2026-08-16
---

# Quick 260816-w8h: Record AoU Support Credit Denial (Vendor Position vs Our Reading) Summary

AoU support ticket 57144 denied the compute-credit request as final, and the denial
letter's own `mt.checkpoint()` sentence independently corroborates the `_SUCCESS`
root cause we reached forensically on 2026-05-21 — recorded as the vendor's
position (not adopted), with the corroborated part propagated to the skill
invariant and the no-backstop consequence propagated to fire GATE 1.

## What Was Done

Three doc edits, one atomic commit each, explicit-path staging, $0, nothing fired.

| Task | What | Commit | Diff |
| ---- | ---- | ------ | ---- |
| 1 | `DEC-2026-08-16-aou-credit-request-denied` appended to `.planning/DECISIONS.md` | `eef7fd7` | `77 0` (pure append, single hunk `@@ -1949,0 +1950,77 @@`) |
| 2 | `NO CREDIT BACKSTOP` note in `260812-ox1-READY-TO-FIRE.md` item 6 (GATE 1) | `4b70343` | `5 0` (single hunk `@@ -110,0 +111,5 @@`) |
| 3 | vendor-confirmed sub-bullet under `SKILL.md` invariant 1 | `60e602e` | `6 0` (single hunk `@@ -19,0 +20,6 @@`) |

## The Fire Surface (Task 2 — the risky one)

**Result: unregressed. No revert was needed.** All four dry-run-proven values were
reproduced exactly, so the executed edit is byte-equivalent to the planner's proven one.

| Check | BEFORE (re-captured, not assumed) | AFTER | Verdict |
| ----- | --------------------------------- | ----- | ------- |
| 6b card block md5 (script-identical awk extraction) | `a8d18f664fbfd0d7e281ee05f3accd4c` | `a8d18f664fbfd0d7e281ee05f3accd4c` | **IDENTICAL** |
| 6b card block line count | 60 | 60 | identical |
| `git diff --numstat` | — | `5	0` | matches proven |
| hunk shape | — | single `@@ -110,0 +111,5 @@` | matches proven |
| guk `fire` section | `ALL CHECKS PASSED`, F1–F10 PASS (10/10) | `ALL CHECKS PASSED`, F1–F10 PASS (10/10) | **10/10** |

The BEFORE baseline was captured on a clean tree *before any edit in this task*, so
"unregressed" is a comparison rather than a hope. The guk `fire` section was re-run a
second time after Task 3 (closeout net) and still printed
`RESULT: ALL CHECKS PASSED (section: fire)` with F1–F10 all PASS.

Negative-control spot checks on the runbook after the edit: `nothing is lost` = 0 (F10),
`c19e8b2` = 0 (F5), `NO CREDIT BACKSTOP` = 1, heading order still
6 → 6b → 7 → 8 → 9 → 10 → 11 with no renumbering (F7). The note sits strictly ABOVE
`## 6b`, which is what kept the card block byte-identical and F1/F4 green.

## Substance Recorded

**Their position (recorded, not adopted).** Denial is final — no credits or refunds for
compute charges from user-run analyses. Their load-bearing sentence is transcribed
verbatim: *"Hail's mt.checkpoint() will still write a dataset and produce _SUCCESS
markers even if the underlying MatrixTable being checkpointed is empty."* Plus their
job-configuration/scale critique, the paused/resumed + lost-logs story, the
validate-on-smaller-subsets recommendation, and the repro-example offer.

**Our reading (separately headed, labelled as ours).**
1. ★ ACCEPTED — their sentence independently corroborates the root cause we reached
   forensically on 2026-05-21, *before* the ticket was filed. Upgrades
   `feedback_aou_success_marker_not_evidence_of_data` and
   `feedback_hail_checkpoint_contract_violation` from "our forensics" to
   "our forensics, confirmed by the platform team."
2. ⚠ UNACCEPTED — their two explanations are in tension: if `checkpoint()` stamps
   `_SUCCESS` over empty contents by design, the pause/resume + lost-logs story is
   superfluous to explaining what we saw.
3. ⚠ UNACCEPTED — the custom-Spark-config critique is soft: `hl.init(spark_conf=...)`
   is silently overridden on YARN, which is exactly why the `PYSPARK_SUBMIT_ARGS` route
   existed. A documented workaround, not gratuitous tuning. Now moot (Hail producer dead).
4. Their framing is explicitly NOT the accepted account of the catastrophe.
5. Their forward recommendation is already implemented by the staged ramp
   (Stage A → Stage B 4-region incl. worst case `m2_region_00071` → measured gate → Stage C 276).

**Repro-example offer: DECLINED-BY-LAPSE**, with the reason on the record (targets the
killed Hail producer; superseded by native-plink) so the decline is a decision, not a
silent omission. Flagged as the first thing to re-open if the Hail producer is revived.

**Operational consequence.** An operator standing at GATE 1 now reads that there is no
money backstop behind it: an overrun is unrecoverable, not reimbursable, so Stage B's
*measured* extrapolation carries the Stage-C go/no-go.

## must_haves Verification

| Truth | Evidence |
| ----- | -------- |
| Vendor determination on the record as THEIR position, our reading separate | `### THEIR POSITION` = 1, `### OUR READING` = 1 in DECISIONS.md |
| Corroborated part marked corroborated; rest UNACCEPTED | items 1 (★ ACCEPTED) vs 2/3 (⚠ UNACCEPTED) in OUR READING |
| Repro offer recorded DECLINED-BY-LAPSE with reason | `DECLINED-BY-LAPSE` = 1 |
| Operator at GATE 1 learns there is no credit backstop | `NO CREDIT BACKSTOP` = 1 in READY-TO-FIRE item 6 |
| Skill invariant can cite vendor confirmation | `ticket 57144` = 1, `Platform-team CONFIRMED 2026-07-24` = 1 in SKILL.md |
| Fire surface byte-unregressed | card md5 identical; guk fire 10/10 (twice) |

**key_links:** `DEC-2026-08-16-aou-credit-request-denied` resolves from all three files
(DECISIONS.md = 1, READY-TO-FIRE.md = 1, SKILL.md = 1).

## Deviations from Plan

None — plan executed exactly as written. No Rule 1–4 deviations, no auth gates, no
checkpoints. Task 2's revert branch was not taken because the fire section never
regressed.

## Guardrails Honored

- Docs-only, **$0**, no network / OSF / perimeter contact, nothing fired, nothing authorized.
- Explicit-path `git add` only — never `git add .` / `-A` on this GPFS shared tree.
- `.planning/STATE.md` (836 KB) never read and never touched; `.planning/ROADMAP.md` untouched
  (`git status --porcelain` on both = empty). Orchestrator owns them.
- Not pushed — 3 commits ahead of `origin/m3-W2-aou-deltas`, left for the orchestrator.
- No GPFS `invalid object` / `Error building trees` occurred; all three commits clean.

## Known Stubs

None.

## Self-Check: PASSED

- `.planning/DECISIONS.md` — FOUND, heading present exactly once
- `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md` — FOUND, note present exactly once
- `.claude/skills/aou-ld-pipeline/SKILL.md` — FOUND, annotation present exactly once
- Commits `eef7fd7`, `4b70343`, `60e602e` — all FOUND in `git log`
- Working tree clean for all three target files; STATE.md / ROADMAP.md unmodified
