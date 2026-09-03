---
task: 260903-ict
title: Correct two false passages in the RUN 2 courier record (fix at source, re-splice) and append the tail DISCLOSURE
mode: quick
type: summary
status: COMPLETE
branch: m3-W2-aou-deltas
docs_only: true
pushed: false
posted: false
fired: false
cost: $0
date: 2026-09-03
---

# 260903-ict — SUMMARY

DOCS-ONLY. One commit, no push. **Nothing was posted; no agent contacted OSF or Seth; no VM, no
Dataproc, no gcloud/gsutil, no network. $0.** `src/` and `tests/` untouched.

---

## 1. Task 1 — the four anchors, pinned before anything was edited

⚠ **The spec changed again after the plan was written.** The plan pins this task's
`CONTENT-SPEC.md` at `20d3b287c3f5bbea5104d79f67b710a8` / 225 / 14917. The coordinator supplied
superseding anchors, and the file on disk matched **the new ones**:

| file | expected (as executed) | measured | verdict |
|---|---|---|---|
| `260903-ict/CONTENT-SPEC.md` (**this task's spec**) | `d31d7cc2314b6a8bed3884e4ce5340be` / 226 / 14977 | `d31d7cc2314b6a8bed3884e4ce5340be` / 226 / 14977 | ✅ |
| courier record | `e2c0b5443bf82a12940d492fefb1f282` / 491 / 30995 | `e2c0b5443bf82a12940d492fefb1f282` / 491 / 30995 | ✅ |
| `260902-vsp/CONTENT-SPEC.md` (**splice SOURCE**) | `5bfbfadffd7a7383e6e9c7047e0c983a` / 158 / 10729 | `5bfbfadffd7a7383e6e9c7047e0c983a` / 158 / 10729 | ✅ |
| `.planning/osf_deviations.md` | `c37ccbd34e5af67663413d1dd264e0ae` / 530 / 40052 | `c37ccbd34e5af67663413d1dd264e0ae` / 530 / 40052 | ✅ |
| `260903-ict-PLAN.md` | `f50be8dacf4857ee0b1e632e9666fe2d` | `f50be8dacf4857ee0b1e632e9666fe2d` | ✅ |

All four (five, with the plan) matched. Nothing was edited before this gate.

**Snapshots** taken into scratch as the `cmp` baselines: `courier.orig.md`, `vsp_spec.orig.md`,
`osf_deviations.orig.md`, `STATE.orig.md`. Scratch only; never committed.

---

## 2. Task 1D — F-1's six zero-counts, re-proven in this executor's own shell

Measured case-insensitively across all 491 lines of the courier, **before** any edit:

| pattern | hits | required |
|---|---|---|
| `collaps` | **0** | 0 |
| `parent` | **0** | 0 |
| `2\.62` | **0** | 0 |
| `leave.one.out` | **0** | 0 |
| `2\.48` | **0** | 0 |
| `0\.0063` | **0** | 0 |

F-1 holds. **PART A2 is a pure ADDITION, not a strike** — the collapse-to-parents argument was
never written into this record. It lived only in `.planning/STATE.md:54` and in correspondence.

## 3. Task 1E — F-2's staleness, re-proven in-shell

`pre-registered value` = **0** in the whole record and **0** in the appendix. The appendix reads
*"the three COMPLETION-CHECK values (see that section — they are NOT a pre-registration)"* — read
directly at `260902-vsp/CONTENT-SPEC.md`'s `## HONEST LIMITATIONS`. The note at courier 290–294 was
therefore describing a state that **no longer existed**, so PART A3 deleted a dead note, not a live
one.

`LIVE CONTRADICTION` pre-fix: **2 hits** — line 296 (body heading) and line 450 (inside the verbatim
appendix), exactly as F-2 predicted.

---

## 4. F-2 REVERSED from r1 — the `ee3af4b` pattern was applied, not a supersession note

r1 proposed leaving the appendix's false copy standing behind a note, citing the record's own
290–294 note as precedent. **That precedent was stale and the r1 remedy was rejected.** Applied
instead, in three steps:

1. **Fixed AT SOURCE** — `260902-vsp/CONTENT-SPEC.md`'s `## ACTION ITEM` section (lines 117–124)
   replaced with `## CORRECTION — the 0.0005 "contradiction" was FALSE; the two constants are
   unrelated`. The `## ARTIFACTS` splice anchor at line 7 is byte-identical.
2. **RE-SPLICED BY SCRIPT** — markers located by pattern, not line number (Task 3 had changed the
   body's length). Nothing was retyped.
3. **RE-VERIFIED and RE-ANCHORED.**

### Byte-equality evidence, before and after

| | bytes | sha256 | equal to source `## ARTIFACTS`→EOF |
|---|---|---|---|
| **pre-fix** (Task 1C) | 10472 | `3a8371b08a78f7b22d9173a297aaa40b50def6144c4cf55c54599ff0571dcfa8` | **True** |
| **post-splice** (Task 4) | 11490 | `3a26095ef4f4a44d0828b3bbb465630f242c3d5b3902911c41c0c6264ed796ef` | **True** |

Exactly one `BEGIN VERBATIM APPENDIX` and one `END VERBATIM APPENDIX`; `## ARTIFACTS` appears
exactly once inside the region. **Byte-equality survived re-anchoring**, which is the point: it is a
means (proof nothing was re-keyed), not an end.

**RESULT: `LIVE CONTRADICTION` = 0 in the WHOLE record, appendix included, and 0 in the splice
source.** No exception was carved for the correction's own prose — the construction rule kept the
banned string out of it entirely.

### ⚠ One plan number disagreed with the tree, recorded not reconciled

The plan's Task 1C states the pre-fix appendix region is **10427 B**. Measured: **10472 B**. The
sha256 prefix the plan gives (`3a8371b0…`) **matches exactly**, and the byte-equality assertion
returned True — so the planner and this executor hashed the same bytes; `10427` is a digit
transposition in the plan's prose. Not silently smoothed: recorded here, in `deferred-items.md` §4,
and it changed no decision (Task 4 superseded that anchor anyway).

---

## 5. F-5 — the spec editing artifact, and how it was resolved

The plan flagged that the r1 spec's PART A2 carried a leftover fragment reading *"…ADD 'merging
correlated units should REMOVE manufactured dispersion; it increased to 2.62x; …' — STRIKE THE
ARGUMENT, KEEP THE CONCLUSION. Replace with:"* — which, read literally, instructs adding the false
argument.

**The planner's flag was correct, and the coordinator closed it at source.** The spec on disk
(`d31d7cc2…`, 226 lines) now reads *"ADD EXACTLY THE INDENTED BLOCK BELOW AND NOTHING ELSE"* plus an
explicit prohibition on introducing the refuted argument in order to refute it. This **converges
with** the plan's F-5 resolution ("add only the indented Replace-with block"), so the instruction is
unchanged in substance; the spec now says it directly rather than requiring interpretation.

**Executed accordingly:** only the four indented paragraphs were added, plus one disposition
sentence. The struck argument and the `2.62` statistic were not written anywhere.

`2.62` still appears at spec line 39 — inside the *measured zero-count line* documenting that the
number does not appear in the courier. That is task metadata, not content, and it was **not**
copied. Guard G-A2 confirms `2.62` = **0** hits file-wide in the record.

---

## 6. What changed, file by file

### PART A1 — `260902-vsp/CONTENT-SPEC.md` (splice SOURCE)

Lines 117–124 replaced. The correction states: the two `0.0005` values are different, unrelated
constants; `_OCCLUSION_ANOMALY_FRACTION` (`d9fbc63`) was the occlusion gate — withdrawn and
**REMOVED** (0 hits in `src/`/`tests/`), replaced by the posted `mk7ze` pair
(`OCCLUSION_SITE_FRACTION_CEILING = 0.005056`, `OCCLUSION_INFLATION_CEILING = 3.42`);
`condition_ld_matrix.py`'s `ceiling_frac` is the LD-matrix NaN-zeroing ceiling and that file contains
`occlu` **zero** times; therefore `pairwise_completeness_scan.py:45` is CORRECT; ROOT CAUSE stated;
the `tcujq` docstring defect recorded as DEFERRED.

### PART A1 body + PART A3 — the courier record

- **Deleted** courier lines 289–294: the blank line plus the stale wording note. Exactly one blank
  line now separates *"…No consoling clause is appended."* from the next heading. **No replacement
  note was added.**
- **Replaced** courier lines 296–313 with `## CORRECTION — THE 0.0005 ACTION ITEM WAS FALSE; THE TWO
  CONSTANTS ARE UNRELATED`, in the courier's bolded-markdown style, same substance as the source.
  The DOCS-ONLY sentence (`git status --porcelain -- src tests` is empty at commit time) was kept —
  still true, still load-bearing. The deferred defect is recorded with its **full two-file scope**.
- **Re-spliced** the appendix (Task 4). Nothing at or after the BEGIN marker was hand-edited.

### PART A2 — the courier record

New subsection `### WHAT DOES AND DOES NOT ESTABLISH THE HETEROGENEITY`, inserted immediately after
FINDING 2 and before FINDING 3. Carries: the collapse test **does not discriminate** (raises
dispersion in **65%** of runs, median **+3.6%**, under the rival hypothesis too); the valid
refutation (equal parent rates + duplication → **0.98**, so non-independence cannot **create**
dispersion); leave-one-out retained (**1.99–2.48**, worst p **0.0063**); reader-facing translation
(**CV ≈ 0.20**, ~**20%**); and one disposition sentence recording that the withdrawn test was ours
and was never in this record. The FINDING 2 table and the **+0.886** power clause are untouched; the
headline stays **1.99x**.

### PART B — `.planning/osf_deviations.md`

**PURE APPEND.** One blank line then the entry, nine blocks, every number copied not recomputed
(`6.3e-3` and `0.0063` each left in the notation the spec uses in its own place). Marked
**`**Status:** DRAFTED — NOT POSTED; placement and posting are Carter's.`** near the top; **no
`**Posted:**` lead anywhere** (the token `Posted:` appears **0** times in the new region); no invented
GUID. `mk7ze` / `trsx5` / `tcujq` are named only as existing posted records being cited.

### PART C — `.planning/STATE.md`

- One `| 260903-ict |` row, 7 pipes / 6 cells, inserted immediately after the `260902-vsp` row.
- Line 45's courier pin refreshed.
- The "Three repo fixes QUEUED" block: items 1 and 2 marked **DONE by this task**, item 3 left
  **QUEUED** and **widened** to both files with a named-enforcer requirement.
- Line 54 corrected: the collapse argument is **WITHDRAWN** (it does not discriminate) rather than
  "must be STRUCK", with the measured note that it was never in the courier.

---

## 7. Every pin this task moved, and its new value

| pin | was | now |
|---|---|---|
| courier line **23** (splice-source md5/bytes/lines) | `20fb7fa058b0e0c03ff669706f534349` / 10672 B / 157 lines (already stale since `ee3af4b`) | `619426a0157d199c711a4d771023330a` / **11747** B / **173** lines |
| courier line **34** ("the 10672-B one") — **⚠ not named in the plan; found during execution** | `10672`-B | `11747`-B |
| `.planning/STATE.md:45` (courier md5 + line count) | 491 lines / `e2c0b5443bf82a12940d492fefb1f282` | **542** lines / `c8525e2665e98cfa9d3d0f1c4266429d` |
| appendix splice anchor | 10472 B / `3a8371b0…` | **11490** B / `3a26095e…` |

### Post-task anchors (true as of this commit)

| file | md5 | lines | bytes |
|---|---|---|---|
| courier record | `c8525e2665e98cfa9d3d0f1c4266429d` | 542 | 34644 |
| `260902-vsp/CONTENT-SPEC.md` | `619426a0157d199c711a4d771023330a` | 173 | 11747 |
| `.planning/osf_deviations.md` | `beb34d0bad73950113739bffb3188dd6` | 669 | 49423 |
| `.planning/STATE.md` | `2b05879ba99a7d063ca39991c33c4146` | 3122 | 1040930 |

---

## 8. Guard battery — every guard GREEN on the real tree, every negative control **observed RED**

| id | guard | GREEN (real tree) | negative control | RED observed |
|----|---|---|---|---|
| G-A1 | `live contradiction` = 0, **WHOLE courier**, case-insensitive | **0** ✅ | reinsert the old heading into `courier.negctl.md` | **1** ✅ RED |
| G-A1b | `live contradiction` = 0 in the splice **source** | **0** ✅ | reinsert the sentence into a scratch copy of the source | **1** ✅ RED |
| G-A2 | `2\.62` = 0, whole courier | **0** ✅ | insert `overdispersion rose to 2.62x` | **1** ✅ RED |
| G-A3 | body carries 1.99 / 2.48 / 0.0063 / 0.98 / 65% / 3.6% / 0.886 | 5 / 1 / 1 / 1 / 1 / 1 / 2 ✅ | delete `2.48` and `0.0063` from the negctl | body 2.48=**0**, 0.0063=**0** ✅ RED |
| G-A4 | appendix byte-equal to corrected source; exactly one BEGIN + one END | **True**, 11490 B, `3a26095e…`; 1 / 1 ✅ | flip one char **inside** the appendix region | **False** ✅ RED |
| G-A5 | `One wording note` = 0 | **0** ✅ | reinsert the note | **1** ✅ RED |
| G-B1 | `cmp head -530` vs the Task-1 snapshot | **IDENTICAL** ✅ | flip one byte on line 100 of `osf.negctl.md` | **cmp DIFFERS** ✅ RED |
| G-B2 | new region has `DRAFTED — NOT POSTED`, 0 `^**Posted:**` | 1 / **0** ✅ | add a `**Posted:** OSF file xxxxx` line | **1** ✅ RED |
| G-C1 | `git status --porcelain -- src tests` EMPTY | **empty** ✅ | `touch src/python/__negctl_probe.py` | `?? src/python/__negctl_probe.py` ✅ RED (removed; re-confirmed empty) |
| G-C2 | `git status --porcelain -- .planning/amendments/` EMPTY | **empty** ✅ | covered by G-C1's demonstration of the idiom | — |
| G-E1 | old courier md5 = 0 hits outside this task's directory | **0** outside / **6** inside (PLAN + spec only) ✅ | the in/out split itself demonstrates the scope is real, not vacuous | — |
| G-E2 | courier line 23's pin == live `md5sum`/`wc` of the source | pin `619426a0…`/11747/173 == live `619426a0…`/11747/173 ✅ | point a scratch pin at `deadbeef…` | **mismatch** ✅ RED |

### ⚠ A negative control that was WRONG and had to be re-aimed — reported, not hidden

**G-A4's first control did NOT go red.** It mutated `t.index("## ARTIFACTS")` — the **first**
occurrence in the file, which is in the **body** (the string occurs 5× file-wide), not inside the
spliced region. Byte-equality correctly stayed `True`, because nothing in the region had changed.
**The guard was right; my probe was aimed at the wrong bytes.** Re-aimed to an offset provably
inside the region (`i < k < j`, offset 23204 of the span 23004..34447), the control went **RED**
(`BYTE-EQUAL = False`) while the real tree stayed **GREEN**. A control that cannot fail proves
nothing — this one nearly shipped as a green-that-cannot-fail.

### Confirmed by READING, not by grep (a grep matches text, not meaning)

Both were read in full in context:

- The new heterogeneity subsection **nowhere asserts** that collapsing to parents *removed*
  manufactured dispersion, and **nowhere asserts** that a rise demonstrates parent-level
  heterogeneity. It says the test is non-discriminating in **both** directions and withdraws it, and
  attributes the conclusion to Seth's `0.98` argument instead.
- The re-spliced appendix's correction reads correctly in context, under `## ALSO BANK` and before
  `## SCOPE CAVEATS`, in the source file's plain/indented style.
- No dangling reference to the removed section survives: `ACTION ITEM` now appears **once** in the
  courier, inside the new CORRECTION heading; `contradiction` appears twice, both legitimate (the
  unrelated provenance note at line 30, and the correction's own quoted-and-negated use).

---

## 9. Deviations from the plan — all recorded, none silent

1. **Spec anchors superseded (coordinator-supplied).** Executed against
   `d31d7cc2314b6a8bed3884e4ce5340be` / 226 / 14977, not the plan's `20d3b287…` / 225 / 14917.
   Verified all three before touching anything. Substance unchanged (see §5).
2. **A second, unnamed pin was found and refreshed — courier line 34** ("the anchor that governs
   this record is the **10672**-B one"). The plan's F-3a names only line 23. Line 34 pins the same
   subject, was already stale from `ee3af4b`, and this task moved it again. **A pin whose subject
   has moved is a false invariant** (the plan's own R-09), so it was refreshed to `11747`-B. This is
   the plan's stated principle applied to a target the plan did not enumerate.
3. **The STATE.md commit-SHA cell is `(this commit)`, not an amended SHA.** The plan says to write a
   placeholder and `git commit --amend` once. **`--amend` changes the SHA**, so any SHA written
   before the amend is wrong *after* it — the cell cannot be self-referentially correct by that
   route. `(this commit)` is the file's own existing convention (used by the `260902-vsp` and
   `260824-fast-env-stop` rows). One commit total, as required.
4. **A superseding clause was added to the `260902-vsp` STATE row.** That row asserts *"the 0.0005
   bound is a LIVE CONTRADICTION"* as fact. Leaving a known-false claim uncontradicted in the live
   navigation document, in a task whose purpose is to correct exactly that claim, is a correctness
   defect. The row's historical description was **not** rewritten (that would falsify the log);
   a dated `⛔ SUPERSEDED IN ONE PART, 2026-09-03 by 260903-ict` clause was appended to it, matching
   the convention already used at STATE.md:76. Every other finding in that row stands unchanged.
5. **Plan Task 1C's `10427 B` disagrees with the measured `10472 B`.** Recorded, not reconciled
   (§4). The sha256 matches exactly and the equality assertion held, so it is a plan-prose
   transposition, not a tree fact. It changed no decision.

**No Rule-4 (architectural) situation arose. No guard was loosened.** The one time a guard looked
like it might need an exception, the answer was the plan's: the construction rules kept the banned
strings out of the correction's prose entirely, so no exception was needed.

---

## 10. Deferred — recorded, not fixed

Full detail in `deferred-items.md`:

1. **The withdrawn-policy docstring defect — TWO files.** `condition_ld_matrix.py:4`, `:153` and
   `write_conditioned_ld_npz.py:4`, `:17`, `:85`. Touches `src/`. Discharge requires **both** files
   **plus a named enforcer test** — an edit alone is belief, not an invariant.
2. **The four missing STATE quick-task rows** (`260828-uej`, `260831-kw8`, `260901-l55`,
   `260901-rvu`) — out of scope by explicit instruction; **not** backfilled.
3. **F-3a is CLOSED, not deferred** — recorded so it is not re-opened.
4. The plan's `10427 B` prose typo (§4).

`.planning/debug/m3-producer-unbounded-dense-read.md` was left **untracked**, as instructed.

---

## 11. Final state

- `git status --porcelain -- src tests` → **EMPTY**
- `git status --porcelain -- .planning/amendments/` → **EMPTY**
- Tracked files modified: exactly **4** (courier, splice source, `osf_deviations.md`, `STATE.md`),
  plus this task's new directory added explicitly by path.
- **Explicit git paths only.** No `git add -A`, no `git add .`. No GPFS loose-object error was
  encountered, so the recovery recipe was not needed.
- **One commit. NOT PUSHED.**
- Nothing posted. No OSF contact. No message sent to Seth. No VM, no fire, **$0**.

---

## Self-Check: PASSED

- `260903-ict-SUMMARY.md` — FOUND
- `deferred-items.md` — FOUND
- `260903-ict-PLAN.md` — FOUND (committed)
- `CONTENT-SPEC.md` — FOUND (committed)
- the commit exists and is HEAD of `m3-W2-aou-deltas` (verified by `git log`). ⚠ **No SHA is
  written here or in STATE.md's row** — this single commit was amended once to carry this
  self-check, and any SHA recorded before an amend is wrong after it. STATE.md uses the file's
  own `(this commit)` convention for the same reason.
- one commit only: `git rev-list --count 67d7db1..HEAD` = **1**
- `git status --porcelain -- src tests` re-run post-commit → **EMPTY**
- appendix byte-equality re-run post-commit → **True**
- `osf_deviations.md` pure-append re-run post-commit → **IDENTICAL**
- `.planning/debug/m3-producer-unbounded-dense-read.md` → still `??` untracked
- **NOT PUSHED.** ⚠ The branch is now **5 commits ahead of `origin/m3-W2-aou-deltas`**
  (this one, plus `67d7db1`, `ee3af4b`, `8ab73fc`, `b16bc2b`). Flagged to Carter — pushing is
  out of scope for this task.
