---
task: 260908-uer
title: Correct the Rao-Scott table's ESTIMATOR — the pooled rate must come from the regions under test
type: quick / DOCS-ONLY
date: 2026-09-08
branch: m3-W2-aou-deltas
baseline: f650dd8
status: COMPLETE
posting_status: DRAFTED — NOT POSTED (unchanged)
files-modified:
  - .planning/osf_deviations.md
  - .planning/STATE.md
  - .planning/HANDOFF.json
src-tests-touched: NONE
---

# 260908-uer — the ESTIMATOR was wrong; the CONCLUSION is not

**One-liner:** the §(10b) Rao-Scott table estimated the pooled POST rate once from all 21
regions and reused that fixed value for every subset; a chi-square test of homogeneity among
k groups must estimate the rate **from the groups under test**. Four figures moved, the
conclusion did not, and the p-value straddle that makes Finding 2 **NOT ESTABLISHED** got
**tighter**.

## The defect

For a homogeneity test the null is that *the regions under test* share a common rate. Fixing
the rate externally (at the all-21 value) is a different test. This was an error in the
analysis script that produced the table, **not** a transcription fault by the executor that
banked it, and it is recorded as such in the document.

## The correction

| chr15 overlap treatment | uncorr. phi | p | DESIGN-CORRECTED phi | p |
| --- | --- | --- | --- | --- |
| all 21 windows | 2.362 | 5.4e-4 | 1.931 | 0.0074 |
| drop `00060__sub13` (HEADLINE) | **1.988** | **0.0063** | **1.675** | **0.0326** |
| drop `00060__sub12` (MIRROR) | **1.992** | **0.0062** | **1.579** | **0.0517** |
| drop BOTH chr15 windows | **1.518** | **0.0732** | **1.241** | **0.2171** |

The all-21 row is **unchanged**, which is the expected signature of this bug: for the full
set, the subset estimator *is* the all-21 estimator. Only the three subsets moved.

**Conclusion unchanged and sharper.** The straddle is now **0.0326 vs 0.0517** — tighter
around 0.05 than the **0.0366 vs 0.0556** it replaces. Two interchangeable overlap treatments
still land on opposite sides of the threshold, so Finding 2 remains **NOT ESTABLISHED** and
the non-robustness is if anything better demonstrated. `phi > 1.2 throughout` still holds
(minimum 1.241).

## ⭐ The corrected numbers were independently corroborated by the tree before I wrote them

I did not recompute anything, and the spec instructed me to STOP if a corrected value
disagreed with the tree. The opposite happened — §(7) of the same file has carried the
matching figures since before §(10b) existed:

| §(7), pre-existing | corrected §(10b) | superseded §(10b) |
| --- | --- | --- |
| leave-one-**WINDOW**-out worst case **1.99 at p 0.0063** (`:834`, "its minimum is the headline itself") | **1.988 / 0.0063** | 1.969 / 0.0071 |
| leave-one-**PARENT**-out worst case **p 0.073** (`:838`, removing parent `00060` removes both chr15 windows) | **1.518 / 0.0732** | 1.535 / 0.0678 |

`p 0.0063` was already an exact string in the file at line 834. The superseded column matched
**neither** row; the corrected column matches **both**. The bug was isolated to the table
added on 2026-09-08 — §(7)'s uncorrected figures were always computed correctly.

## `260908-u5k` D1 — CLOSED, and the COURIER was the right side

D1 flagged §(10b)'s **1.969** against the courier's **1.99** and correctly declined to
adjudicate. **Resolved: the courier was right; §(10b) carried the fixed-rate artifact.** The
correct value is **1.988**. Recorded in `.planning/osf_deviations.md` §(10b) (the paragraph
beginning *"A DISCREPANCY STANDING IN THE RECORD IS CLOSED…"*) and in this task's
`deferred-items.md`.

⚠ **`260908-u5k`'s own deferred-items.md was NOT edited** — dated task record, and D1 was
true when written. Recording the closure in my own record + the authoritative document was
the judgement call the spec left open.

## Scope

**Edited (3 files, all docs):**

- `.planning/osf_deviations.md` — §(10b) table + lead-in + straddle sentence + the
  "indistinguishable" parenthetical + the conclusion blockquote; the **three restatements** of
  the same straddle elsewhere in the entry (the discharge bullet, §(7), §(8)); plus a new
  correction note and the D1 resolution.
- `.planning/STATE.md` — live pins at the top RESUME block and the finding-2 SUPERSEDED
  blockquote, incl. the design-corrected minimum `1.249 → 1.241`; plus an estimator-correction
  marker.
- `.planning/HANDOFF.json` — `.status` (full table + correction note), `.headline`,
  `.resume_on_reconnect[0]`.

**NOT touched:** `src/`, `tests/` (porcelain empty, verified); `tcujq` (stays DEFERRED); the
2026-09-02 courier; all dated `.planning/quick/*` records; the byte-frozen appendix;
`osf_deviations.md` lines 1-531. Status stays **DRAFTED — NOT POSTED**. No push, no OSF/Seth/VM
contact.

## Verification — 40 checks, every one seen RED

`guard.py` in this directory. It is written to run **before** the edit (where it must fail)
as well as after — that pre-edit RED run *is* the negative control, since a check that cannot
fail is not evidence.

- **Pre-edit run: 9/40 PASS (19 of the then-defined 28 RED).** That covers all PRESENT
  checks, both allow-list anchors, all 5 confinement checks and all 5 table-absence checks.
- **Post-edit run: 40/40 PASS.**
- **Mutation negative controls** for every check that was green pre-edit:
  NC-A frozen prefix · NC-B clustering-figure counts · NC-C status string · NC-D
  `NOT ESTABLISHED` · NC-E dirty `src/` · NC-G STATE live pins + preserved-ratio ·
  NC-H/NC-I HANDOFF values, formatting and parseability · NC-J `(10b)` heading ·
  NC-K table rows. All observed RED.
- `cmp` on lines 1-531 vs `git show f650dd8:` → **identical**, with its own mutated-copy
  negative control showing DIFFER.

### Guard design notes

- **Normalization is load-bearing, and I proved it.** All phrase checks strip markdown
  emphasis, collapse whitespace and casefold. Demonstrated (NC-F) on a hostile string where a
  bolded, line-wrapped anchor is invisible to literal substring matching (`False`) but found by
  the guard (`True`).
- **The ABSENT guard is scoped to a REGION, not carved as a per-value exception.** The spec
  anticipated that superseded figures legitimately survive in the sentence that names them.
  Rather than exempting values, the guard asserts that **every** file-wide occurrence of a
  superseded figure lies inside one of two allow-listed paragraphs (identified by stable lead
  phrases), and separately that the corrected table contains **none** of them. That is
  strictly stronger than guarding the table alone: it caught the three restatements at lines
  574 / 631 / 846 that a table-only guard would have missed.

## ⚠ Two near-misses worth recording

**1. A negative control failed for the wrong reason and nearly indicted a good check.** My
first dirty-`src/` probe was `src/.__uer_nc_probe.tmp`; the guard stayed green. The guard was
fine — `.gitignore:182` matches `*.tmp`, so my *probe* was invisible. Re-run with
`src/uer_nc_probe.txt`, the check went RED correctly. The error's apparent cause was not the
measurement.

**2. A `grep` loop with unescaped dots produced three phantom hits.** `grep -n "1.564"` and
`"1.535"` matched STATE.md lines 2010 / 2430 / 2394 as regex wildcards; literal Python
matching showed those strings **do not occur** there at all. In the same sweep, `1.972` *does*
occur literally in STATE.md three times — as the **AFR/EUR pass ratio**
(`2,865,513 / 1,453,157 = 1.972`), entirely unrelated to the Rao-Scott mirror value. So the
identical literal `1.972` needed **opposite** dispositions in two files: rewritten to `1.992`
in HANDOFF.json, preserved untouched in STATE.md. The guard now pins
`STATE.md.count("1.972") == 3` explicitly. (Also confirmed: interactive `grep` here is a
`ugrep` wrapper that rejected a bounded-repetition pattern — I used Python for all literal
audits.)

## Deviations from spec

None to the numbers — every corrected figure was taken from the spec and none disagreed with
the tree. Two judgement calls the spec left to me, both stated above: (a) the three in-file
restatements were aligned rather than left contradicting the corrected table, since they are
restatements of it and not true-when-written claims; (b) the D1 closure was recorded in this
task's record and in §(10b) rather than by writing to `260908-u5k`'s dated record.

## Deferred

See `deferred-items.md`: the courier's `260908-u5k` annotation carries three superseded
figures (its load-bearing claim `1.241 < 1.3` still holds; deferred because editing a dated
communication record would also break STATE.md's `621 lines / f52b76ce…` hash pin, both
re-measured this session and still holding); dated `260908-tnd` / `260908-u5k` records quote
the superseded table by design; `tcujq` stays DEFERRED.

## Self-Check: PASSED

- `guard.py` 40/40 PASS on the committed tree.
- `cmp` lines 1-531 vs `f650dd8` — identical.
- `git status --porcelain -- src tests` — empty.
- `HANDOFF.json` parses and round-trips byte-identically at `indent=2`.
- Live line pins `osf_deviations.md:133` / `:166` re-measured and still resolve to the trsx5
  NaN→0 **withdrawal** text; both sit inside the frozen prefix and were not moved.
