---
phase: quick-260817-vbu
plan: 01
subsystem: planning-records
tags: [trsx5, osf, gate-release, adjudication, enforcer, negative-controls, courier]
requires:
  - .planning/quick/260817-vbu-.../260817-vbu-SETH-COURIER-reconstruction-as-received.md
  - .planning/quick/260817-vbu-.../260817-vbu-replication-transcript.txt
  - .planning/quick/260814-u9p-.../260814-u9p-seth-lineage-9907.txt (at 3684413)
provides:
  - "gates.trsx5_posted_body: third dated RESOLVED sub-entry (append-only, 3 readings visible)"
  - "DEC-2026-08-17-trsx5-gate-released"
  - "STEP 6b card adjudicating SIZE-FIRST against 9,695 in all three ox1 runbooks"
  - "260817-vbu-verify.sh — the named live enforcer (V0-V7), every check seen red"
  - "260817-vbu-REPLY-TO-SETH-replication-confirmed.md — the confirmation courier"
affects:
  - .planning/HANDOFF.json
  - .planning/DECISIONS.md
  - .planning/STATE.md
  - 260812-ox1 AGENT-PROMPT / BROWSER-PASTE / READY-TO-FIRE
  - 260814-guk-verify.sh (header comment only)
tech-stack:
  added: []
  patterns:
    - "append-only ledger with a NAMED mechanical enforcer (guk record R2)"
    - "non-vacuity check FIRST (V0) before any content assertion over an extracted block"
    - "negative controls driven through the SHIPPED sub-modes, never a re-implementation"
    - "BEFORE/AFTER enforcer baselines with written attribution for every flipped verdict"
key-files:
  created:
    - .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh
    - .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-controls-transcript.txt
    - .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-guk-before-after.txt
    - .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-REPLY-TO-SETH-replication-confirmed.md
  modified:
    - .planning/HANDOFF.json
    - .planning/DECISIONS.md
    - .planning/STATE.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
    - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh
decisions:
  - "DEC-2026-08-17-trsx5-gate-released — the trsx5 adjudication is RESOLVED and the fire gate is RELEASED on substance (Carter, 22:32 EDT)"
  - "Re-post NOT taken — Seth withdrew 're-post required'; legibility, not a correction"
  - "Obligation-(2) posting FREED by the release but STILL DEFERRED to manuscript submission day (DEC-2026-08-12-e2-p1-closing-sentence)"
  - "guk's `fire` section is SUPERSEDED, not fixed — its red is expected and attributed"
metrics:
  duration: "~35 min (BEFORE baseline 23:05 EDT → Task 3 commit 23:40 EDT)"
  tasks: 3
  commits: 3
  files_changed: 16
  completed: 2026-08-17
---

# Quick 260817-vbu: Release the trsx5 Gate, Bank the RESOLVED Adjudication Summary

The trsx5 fire gate is RELEASED on substance and the adjudication is RESOLVED: the posted
9,695-B OSF body is a byte-exact plain-text rendering of the complete 9,907-B lineage,
replicated firsthand from the git object store on the first attempt with no fitting — and
all three copies of the STEP 6b card now adjudicate SIZE-FIRST against 9,695 behind a named
enforcer that has been seen to fail.

⛔ **AN AGENT MUST NEVER FIRE THE LOOP.**

## What Was Done

| Task | What | Commit |
|---|---|---|
| 1 | Ledger / decision / state surfaces — third dated `RESOLVED 2026-08-17` sub-entry appended, RELEASED status, new resume `#0`, two annotated `do_not` items, `DEC-2026-08-17-trsx5-gate-released`, new STATE.md LATEST block; four previously-untracked artifacts staged | `0bfa873` |
| 2 | STEP 6b card rewritten to the 9,695 anchor in all three ox1 runbooks; `260817-vbu-verify.sh` (V0-V7) written and driven red 6 ways; guk header marked SUPERSEDED (comments only); BEFORE/AFTER + attribution | `45381f0` |
| 3 | Confirmation courier to Seth (89 lines) | `3ff9b2f` |

**$0 spent. Nothing fired. Zero OSF contact. Zero perimeter contact. No network. Nothing
pushed by an executor.** `git status --porcelain src/ tests/ config/ Snakefile` = empty;
`git diff HEAD~3..HEAD -- . ':(exclude).planning'` = empty; no worktree used; every commit
staged with explicit paths.

## 1. Verbatim Observed RED for Every Negative Control

A green is evidence only after the same check has been **seen** to lose. Every control was
driven through the **shipped** `_card` / `_artifact` sub-modes of `260817-vbu-verify.sh`
(never a re-implementation); every mutated copy lived in the session scratchpad and nothing
under `.planning/` was mutated. Full transcript:
`260817-vbu-controls-transcript.txt` (129 lines).

**NC-0 — GREEN DIFFERENTIAL** (so the reds below are differential, not universal):

```
PASS  V0 [nc0.md] card block is non-vacuous (51 non-empty lines)
PASS  V1 [nc0.md] adjudicates SIZE-FIRST (9,695 on block line 11 precedes the md5 on 20)
PASS  V2 [nc0.md] card block carries BOTH verified digests (md5 32-char + sha256 64-char)
PASS  V3 [nc0.md] every hex run >=20 chars in the card block is 32 (md5) or 64 (sha256)
PASS  V4 [nc0.md] card block carries ADJUDICATED-RESOLVED 2026-08-17 + the decision id
PASS  V5 [nc0.md] historical anchors 9,758 / 9,907 retained AND labelled SUPERSEDED
RESULT: ALL CHECKS PASSED   EXIT=0
```

**NC-1 — V3, one hex character deleted from the card's md5** (the failure text prints the
observed length, which is the whole point of a length invariant over a hash allow-list):

```
FAIL  V3 [nc1.md] hex run(s) in the card block are neither 32 (md5) nor 64 (sha256):
  len=31  c19be8b2ad7cd6a45fee1d668d8a9cf
```

**NC-2 — V1, the pre-md5 `9,695` line moved to AFTER the md5 line:**

```
FAIL  V1 [nc2.md] card is HASH-FIRST: 9,695 first appears on block line 20, c19be8b2ad7cd6a45fee1d668d8a9cf9 on 19 (need strictly before)
```

**NC-3 — V4, the dated adjudication string deleted (2 occurrences):**

```
FAIL  V4 [nc3.md] card block is missing the dated string 'ADJUDICATED-RESOLVED 2026-08-17'
```

**NC-4 — V0, block collapsed by a bogus end-heading regex:**

```
FAIL  V0 [nc0.md] card block has 1 non-empty line(s) (need >= 8) — heading not found or card gutted; every check below would be VACUOUS
```

**NC-4b — V0, block genuinely emptied by a non-matching start regex** (added beyond the
plan's six; the empty-block case is the purer form of the vacuity class):

```
FAIL  V0 [nc0.md] card block has 0 non-empty line(s) (need >= 8) — heading not found or card gutted; every check below would be VACUOUS
```

**NC-5 — V6, ONE byte flipped with the size UNCHANGED at 9,695** — proving V6 is not
size-only. `dd` reported `1 byte copied`; `wc -c` still read 9695:

```
FAIL  V6 md5 MISMATCH: 855cf5208af95fbe1bb54a0b706b0add (want c19be8b2ad7cd6a45fee1d668d8a9cf9)
FAIL  V6 sha256 MISMATCH: a63e05d0c8d6cba467d0a5b0ce1ce3aec9d3ff2b7fc3141cd592eeed3090ddc1 (want 1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4)
```

V2, V5 and V7 were not driven red by a dedicated control; they are pure substring presence
checks whose non-vacuity is guarded by V0 (recorded here as a limitation, not claimed as
tested).

## 2. BEFORE / AFTER guk Verdicts — Every Changed Check Attributed

Full evidence: `260817-vbu-guk-before-after.txt` (170 lines, BEFORE captured **before any
edit**).

| Section | Check | BEFORE | AFTER | Attribution |
|---|---|---|---|---|
| fire | F1, F2, F4, F5, F6, F7, F8, F9, F10 | PASS | PASS | unchanged |
| fire | **F3** | **PASS** | **FAIL** ×3 | **INTENDED SUPERSESSION** — see below |
| record | R1, R2, R5, R6, R7, R8 | PASS | PASS | unchanged; **no new reds** |
| record | R3 | FAIL | FAIL | PRE-EXISTING (the 2026-08-16 close already replaced `status`); verdict and reason unchanged |
| record | R4 | FAIL | FAIL | PRE-EXISTING (the 2026-08-16 close already prepended `resume_on_reconnect[0]`); verdict unchanged, observed md5 moved `d0fd2139…` → `06ec0b14…` because Task 1 prepended the 2026-08-17 `#0` |
| reply | P1-P8 | PASS | PASS | unchanged (this task did not touch the guk-era reply) |

**F3, the one flipped verdict, at exactly three sites** —
`260812-ox1-AGENT-PROMPT.md:110`, `260812-ox1-BROWSER-PASTE.md:131`,
`260812-ox1-READY-TO-FIRE.md:146`. F3 requires every line carrying
`c19be8b2ad7cd6a45fee1d668d8a9cf9` to sit in a 4-line window naming "Seth" and containing
"nverified". That was correct for the superseded two-body card, where the value was a
Seth-reported OSF-API read behind a sign-in wall. The 2026-08-17 adjudication makes it a
**verified** anchor — Carter measured it himself at STEP 6b on 2026-08-16, and our
replication lands on it independently — so the new card states the opposite of what F3 pins.
A card still reading "Seth-reported, unverified" beside the pass condition would be **false**.
The three flagged lines were checked by hand and are exactly the three **"gate PASSES"**
lines, one per runbook copy — i.e. precisely the lines whose semantics the adjudication
changed, and no others.

This is a supersession rather than a regression because it is **dated and named**: the guk
header now carries `SUPERSEDED 2026-08-17`, names its successor, and the live enforcer
`260817-vbu-verify.sh all` is **GREEN** over the same three card blocks with every check
seen red first. **`record` R2 — the append-only enforcer on `gates.trsx5_posted_body` — is
still green after the third sub-entry was appended**, which is the mechanical proof that the
2026-08-13 and 2026-08-14 readings were neither deleted nor reordered.

## 3. What Is UNBLOCKED, What Is Still DEFERRED, and the Ordered Carter-Only Next Steps

**UNBLOCKED**
- The AoU LD fire, at the **Step 3 GATE**. PRE-FIRE 1b is **already signed** (`2f0b607`) and
  must not be re-signed. Staged ramp unchanged: Stage A region-1 → Stage B 4-region →
  **measured** cost gate → Stage C 276.
- The independence constraint on our characterization of the posted body (Seth published
  first) — the confirmation courier may now be sent.

**STILL DEFERRED / STILL BINDING**
- **Obligation-(2) posting** is *freed by the gate release* but **REMAINS DEFERRED to
  manuscript submission day** per `DEC-2026-08-12-e2-p1-closing-sentence`. This decision does
  not move that deadline.
- **No credit backstop** behind runbook GATE 1 (`DEC-2026-08-16-aou-credit-request-denied`) —
  Stage B's measured extrapolation must carry the Stage-C go/no-go. An overrun is
  unrecoverable, not reimbursable.
- The re-post is **not taken** (optional legibility). If ever revisited: a NEW OSF VERSION,
  never a silent swap.

**ORDERED CARTER-ONLY NEXT STEPS**
1. `git push` origin (orchestrator/Carter — an executor never pushes).
2. Send `260817-vbu-REPLY-TO-SETH-replication-confirmed.md` to Seth.
3. Re-paste `260812-ox1-AGENT-PROMPT.md` to the AoU browser agent — it stood down **at** the
   Step 3 GATE and the STEP 6b card it reads has **changed**.
4. Step 3 GATE in the Workbench UI: environment EXISTS, is STOPPED, sits on a **Reattachable**
   persistent disk → START.
5. Steps 4-10: the staged ramp, with the measured cost gate before Stage C.

⚠ At STEP 6b the card now adjudicates against **9,695 first**; **9,758 or 9,907 observed at
download time is ITSELF a STOP** (the posted record would have changed since adjudication).
Liveness arbiter for the fire remains the GCS `.npz` object listing climbing to 276 — not the
kernel light, not `_SUCCESS`.

⛔ **AN AGENT MUST NEVER FIRE THE LOOP.**

## Deviations from Plan

**No Rule 1-4 deviations.** Three recorded observations, none requiring a fix:

**1. [Observation] The plan's §B says HANDOFF.json has 36 top-level keys; measured 40.**
Nothing depended on the count — the pinned dump recipe was re-proven byte-identical on a
no-op round-trip *before* any mutation (the actual guard), and the resulting diff was 6
insertions / 5 deletions against a 69 KB file. Recorded because an unreconciled count in an
`<interfaces>` block is a claim, and this one was wrong.

**2. [Strengthening] NC-1 deletes the LAST hex character, not a middle one.** Deleting the
`b` at index 3 would have reproduced the retired 31-char defect literal exactly; the last-char
deletion yields an equally 31-char run without injecting that literal anywhere. NC-4b was
added beyond the plan's six controls because a bogus *end* regex collapses the block to one
line, while a non-matching *start* regex empties it — both are the vacuity class and both are
now recorded red.

**3. [Plan-internal inconsistency, worked around] The plan's `<verification>` block chains
`260814-guk-verify.sh record &&`,** which can never pass: the plan's own §C measures R3 and R4
as pre-existing reds that must NOT be fixed. The sections were therefore run separately and
`record` was adjudicated on the rule the plan actually states — *no NEW reds* — which holds.

## Threat Flags

None. This task added no network endpoint, no auth path, no file-access pattern and no schema
change. The one trust boundary it touches (repo record → irreversible spend) is the boundary
the plan's `<threat_model>` already registers, and T-vbu-01/02/03/05 mitigations were all
implemented as specified (V1-V5, append-only + R2, V6 re-hash, BEFORE/AFTER attribution).

## Known Stubs

None.

## Verification

```
bash …/260817-vbu-verify.sh all                → RESULT: ALL CHECKS PASSED (exit 0)
bash …/260814-guk-verify.sh reply              → ALL CHECKS PASSED
bash …/260814-guk-verify.sh record             → R3/R4 red (PRE-EXISTING), 6/8 green
bash …/260814-guk-verify.sh fire               → F3 red ×3 (EXPECTED SUPERSESSION), 9/10 green
python3 -m json.tool .planning/HANDOFF.json    → JSON OK
sed -n '1,24p' .planning/STATE.md | md5sum     → fe245157bb7a442431898c26229e7fb9 (pinned)
git status --porcelain src/ tests/ config/ Snakefile   → empty
git diff --stat HEAD~3..HEAD -- . ':(exclude).planning' → empty
git log --name-only -3 | grep -c 'tests/m3/sparse_parent_benchmark.tsv' → 0
git log --oneline -3 | grep -c 'docs(quick-260817-vbu)' → 3
```

## Self-Check: PASSED

All five created files exist on disk with the plan's `min_lines` satisfied
(`260817-vbu-verify.sh` 219 ≥ 120; controls transcript 129 ≥ 30; before/after 170 ≥ 40;
reply 89 ≥ 45). All three commit hashes resolve in `git log --all`
(`0bfa873`, `45381f0`, `3ff9b2f`). All three `key_links` from the plan frontmatter are
present: READY-TO-FIRE names `260817-vbu-verify.sh`; `260817-vbu-verify.sh` carries the
sha256 anchor `1ba83e4e…`; `260814-guk-verify.sh` names its successor. The
`### Quick Tasks Completed` table in STATE.md was NOT touched (0 hits in the 3-commit diff)
— the orchestrator owns it, together with this SUMMARY and the STATE.md quick-task row,
both of which are deliberately left UNCOMMITTED. `ROADMAP.md` was not updated, per scope.
