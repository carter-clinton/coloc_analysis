---
title: "Annotate-forward the courier's live `phi > 1.3` sentence — scope-limited, not corrected; the byte-frozen appendix left untouched"
task: 260908-u5k
date: 2026-09-08
type: quick
scope: DOCS-ONLY
src_tests_touched: false
posted: false
---

# `260908-u5k` — SUMMARY

**One line.** One additive `⚠ SCOPE-LIMITED 2026-09-08` paragraph was inserted into the
**LIVE BODY** of the courier record immediately after the `phi > 1.3` sentence; the sentence
itself is **UNEDITED**, its identical twin inside the **byte-frozen VERBATIM APPENDIX** is
**BYTE-UNMOVED** (proved, with a negative control seen RED), and the two **live** pins that
recorded the courier's whole-file md5 were refreshed because the edit moved it.

## The distinction this task turns on

**Re-splice is for text that was FALSE when written. Annotate-forward is for text that was
TRUE but whose scope has since narrowed.** This was the second case, so nothing was
corrected and nothing was re-spliced.

The sentence at courier `:140` — *"The dispersion is robust in **DIRECTION** (every
correction gives phi > 1.3) but **POORLY DETERMINED in magnitude**, and **its significance is
not robust to the choice of overlap correction.**"* — was scoped to the **OVERLAP**
corrections that existed on 2026-09-02. It remains true for those. What changed is that a
**new** correction set now exists: the **design-corrected** figures (`1.931 / 1.652 / 1.564 /
1.249`), whose minimum falls **below 1.3**. A reader would now take the sentence as a general
robustness claim it no longer supports. The annotation carries that; the sentence carries
none of it.

## What changed (3 files, all under `.planning/`)

| file | change | numstat |
| --- | --- | --- |
| `.planning/debug/260902-COURIER-…-disagreement.md` | +1 blank line, +7-line annotation after `:141` | `8 / 0` |
| `.planning/STATE.md` | courier **Record** pin refreshed (was a now-false md5) | `7 / 1` |
| `.planning/HANDOFF.json` | 2 string leaves: `/run2_step2_2026_09_02/record` refreshed, `/status` annotated forward | `2 / 2` |

**`git status --porcelain -- src tests` was EMPTY** before and after. No OSF contact, no Seth
contact, no VM, no push, no re-derivation of any number.

## The annotation, as inserted (courier `:143-149`)

It was **not retyped**: it was extracted programmatically from `CONTENT-SPEC.md` (md5
`6c7aff555bae9ec2ca6a6de1904c951b`), dedented by exactly the spec's 2-space quoting, and
inserted verbatim.

```
⚠ **SCOPE-LIMITED 2026-09-08.** That "phi > 1.3" statement was scoped to the OVERLAP
corrections available on 2026-09-02 (2.36 / 1.97 / 1.99 / 1.52). It is TRUE for those and
is left unedited for that reason. It does NOT extend to the DESIGN-CORRECTED figures,
which did not exist when it was written: after correcting for the measured within-window
clustering (ICC 0.729, c_eff 1.494), the corrections give 1.931 / 1.652 / 1.564 / **1.249**,
and the last falls BELOW 1.3. See the 2026-09-08 entry in `.planning/osf_deviations.md`:
**Finding 2 is NOT ESTABLISHED.**
```

Every number in it was checked against `.planning/osf_deviations.md` **before** insertion:
the design-corrected column `1.931 / 1.652 / 1.564 / 1.249` is the §(10b) Rao-Scott table
verbatim; `ICC 0.729` / `c_eff 1.494` are `0.728930` / `1.494248` rounded; and
*"Finding 2 is NOT ESTABLISHED"* is §(10b)'s own heading and conclusion.

## Measurements

| quantity | before | after |
| --- | --- | --- |
| courier lines | 613 | **621** |
| courier md5 | `ce6791344916c6ebebacfadbb808c702` | **`f52b76ce73b5f83d03a6e09e2822563f`** |
| courier bytes | 40944 | 41513 (**+569, all inserted**) |
| **appendix bytes** | **14119** | **14119 — UNMOVED** |
| **appendix md5** | **`e4cb947823dd758ec2bd32667b788391`** | **`e4cb947823dd758ec2bd32667b788391` — UNMOVED** |
| splice source md5 | `34199ab125727f28c7f7b2d910e2005a` | unchanged, file untouched |

## Verification — and every green was seen RED first

The enforcer is committed, not merely claimed: **`guard.py`** and **`pin_check.py`** in this
task directory. Both **normalize** (strip markdown emphasis — asterisk, underscore, backtick,
`>`, `#` — and collapse whitespace) and **lowercase**
before every phrase check, because a literal case-sensitive grep has been blind to live text
in these files five separate times.

| # | assertion | result | seen RED by |
| --- | --- | --- | --- |
| V1 | appendix bytes == splice source `## ARTIFACTS`→EOF | ✅ PASS (14119 B, `e4cb9478…` both sides) | **NC-A** |
| V2 | appendix md5 pinned at `e4cb9478…`, 14119 B | ✅ PASS | **NC-A** |
| V3 | exactly 1 BEGIN + 1 END marker | ✅ PASS (1/1) | — |
| V4 | original sentence intact in LIVE BODY (n=1) | ✅ PASS | **NC-B** |
| V5 | original sentence intact in APPENDIX (n=1) | ✅ PASS | **NC-A** |
| V6 | 7 annotation-unique phrases present in LIVE BODY, exactly once each | ✅ PASS | **pre-edit baseline** |
| V7 | those same 7 phrases **ABSENT** from the APPENDIX (n=0 each) | ✅ PASS | — |
| V8 | `.planning/osf_deviations.md` count: body 2 (1 pre-existing + 1 new), appendix 1 (pre-existing) | ✅ PASS | **pre-edit baseline** |
| V9 | **identity transform**: deleting exactly the inserted bytes reproduces the pre-edit file **byte-for-byte** | ✅ `True` | — |
| V10 | `git diff --numstat` on the courier is `8 / 0` — **zero deletions** | ✅ PASS | — |
| V11 | live pins in `STATE.md` + `HANDOFF.json` carry the **on-disk** md5 and line count | ✅ GREEN | **NC-C** |
| V12 | `HANDOFF.json` still parses; **exactly 2** string leaves changed; key set identical | ✅ PASS | — |
| V13 | `git status --porcelain -- src tests` | ✅ **EMPTY** | — |

**Negative controls, each run and each observed RED:**

- **NC-A** — one character flipped **inside the appendix** (`DIRECTION`→`DIRECTIOM`) on a copy:
  V1 RED (`a3b8ecf1…` ≠ `e4cb9478…`), V2 RED, V5 RED.
- **NC-B** — appendix untouched, the **live** sentence mutated (`1.3`→`1.9`) on a copy: V4 RED
  while **V1 stayed PASS**. This is the control that matters: it proves the splice check and
  the sentence check are **independent assertions**, not one proxy standing in for both.
- **NC-C** — `pin_check.py` fed a fabricated digest: all four pin assertions RED.

V9 is preferred over any count-based check by design: a **must-be-identity transform** is
strictly stronger than a must-match count.

## Deviation — Rule 1/2, and it was NOT in the spec

**The edit moved the courier's whole-file md5, and that md5 was pinned in LIVE state.**
Measured after the insertion: `ce6791344916c6ebebacfadbb808c702` / 613 lines appeared in six
places. They are **not** all the same kind of claim:

| location | kind | action |
| --- | --- | --- |
| `.planning/STATE.md:162` **Record:** | **LIVE pointer** — describes the file *as it is* | **refreshed**, history retained inline |
| `.planning/HANDOFF.json` `/run2_step2…/record` | **LIVE pointer** | **refreshed**, history retained inline |
| `.planning/HANDOFF.json` `/status` ("left BYTE-IDENTICAL") | **DATED claim by `260908-tnd`** — true when written | **left standing, annotated forward** |
| `260904-dgi-SUMMARY.md:310`, `260908-tnd/SUMMARY.md:97`, `260903-ict/deferred-items.md:75` | **dated task records** | **untouched** |

Leaving the two live pointers asserting a now-false digest would have handed the next agent a
file that fails its own recorded invariant. Refreshing them is the same annotate-forward
principle applied one level up — and the dated records got exactly the treatment the appendix
got: none.

## What was NOT done

- The `phi > 1.3` sentence was **not** rewritten, softened, or hedged.
- The **VERBATIM APPENDIX** was **not** touched — no re-splice, no supersession note inside it.
  Its md5 is cited in committed artifacts; editing it to "fix" a **true** sentence would break
  a published anchor for nothing.
- `260902-vsp/CONTENT-SPEC.md` (the splice source) was **not** edited — this is not a
  fix-at-source case, so the `ee3af4b` pattern deliberately does **not** apply.
- Nothing under `src/` or `tests/`. Nothing posted. Nothing pushed. Nothing fired.
- The `1.97` vs `1.99` provenance question raised by the spec's parenthetical was **not**
  investigated — see `deferred-items.md` **D1**. It is pre-existing and does not bear on the
  annotation's claim (all four figures exceed `1.3` under every rounding in the record).

## Status

`DRAFTED — NOT POSTED` is unchanged by this task. The courier remains an in-repo record;
nothing about the posting decision moved.
