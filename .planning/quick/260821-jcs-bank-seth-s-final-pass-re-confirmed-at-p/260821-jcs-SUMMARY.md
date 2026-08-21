---
phase: quick-260821-jcs
plan: 01
subsystem: pre-registration
tags: [osf, amendment, occlusion, posting-prep, re-confirmation, class-p, pre-execute-commit, guard, seth-final-pass, posting-card, m3-07]

requires:
  - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  - .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
  - .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
  - .planning/debug/260820-site-basis-sweep-results-as-received.md
  - .planning/debug/260819-occ-measure-sweep-results-as-received.md
provides:
  - Seth's final pass banked as the seventh supporting record
  - PRE_EXECUTE_COMMIT advanced to d45db42 by engine Class-P force substitution
  - Carter-drivable posting card with fresh anchors
affects:
  - .planning/STATE.md
  - .planning/HANDOFF.json

tech-stack:
  added: []
  patterns:
    - "Class-P slot values are machine-owned tokens; prose must never carry a literal copy of one"
    - "2-cell negative-control matrix on the same fixture path, for red attribution"

key-files:
  created:
    - .planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md
    - .planning/debug/260821-POSTING-CARD-for-carter.md
  modified:
    - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
    - .planning/STATE.md
    - .planning/HANDOFF.json

decisions:
  - "The re-confirmation date in prose is written as the unsubstitutable form '21 August 2026', never the literal token 2026-08-21, because Class-P blind-replaces that token document-wide with a dynamic-only fence"
  - "260821-jam (a duplicate of this task from a parallel terminal) was NOT edited; routing it is a human decision"

metrics:
  duration: ~14 min
  completed: 2026-08-21
---

# Quick 260821-jcs: Bank Seth's Final Pass + Execute RE-CONFIRMED AT POSTING — Summary

Seth's final pass (no blocking objection) is banked as the seventh supporting record, the
amendment's own standing RE-CONFIRMED-AT-POSTING instruction was **executed rather than quoted**
(gate hash advanced to `d45db42` through the engine's Class-P pass, not by hand), and Carter has a
posting card he can drive alone — **with the posted body byte-identical throughout**.

**The single hard invariant held at every commit:** the paste block is
**22,945 B / `422f1f28d6a3b76c7657fadec05a0237`**, measured four times — before the engine, after
the engine, after the prose edits, and at the final pushed HEAD.

---

## 1. The precondition, re-measured (not assumed)

The amendment's row says: *"re-read HEAD, confirm no `_OCCLUSION_ANOMALY_FRACTION` or
gate-constant change has landed since, and update this value if the branch has advanced."*
**Confirm, then update — in that order.** Captured after Task 1's commit and before the engine ran:

```
NEWHEAD=d45db429b3fa6c1f08989c418de911a1fe15fbf2  NEWSHORT=d45db42
```

`git log --oneline 2689cae..HEAD` — 5 commits, all docs-only:

```
d45db42 docs(debug): bank Seth's final pass as-received — no blocking objection; seventh supporting record
241515b docs(handoff): 2026-08-21 MORNING close — amendment instantiated/attacked/revised, guard green ...
cd0cdfd docs(quick-260820-u6i): close-out — SUMMARY/VERIFICATION (verifier 10/10, 2x2 matrix + fresh NC re-executed) ...
a364d19 docs(quick-260820-u6i): reply courier to Seth — count-vs-fraction fix, permissiveness pre-emption ...
b4263e7 docs(quick-260820-u6i): answer Seth's attack — 1.18x named a COUNT ratio with the measured 1.12x fraction ratio ...
```

`git diff --stat 2689cae HEAD -- src/ tests/ config/` — **EMPTY** (zero lines of output):

```
$ git diff --stat 2689cae HEAD -- src/ tests/ config/
$ git diff --stat 2689cae HEAD -- src/ tests/ config/ | wc -l
0
```

The shipped constant, untouched:

```
$ grep -n '_OCCLUSION_ANOMALY_FRACTION = 0.0005' src/python/run_native_ld_panel.py
133:_OCCLUSION_ANOMALY_FRACTION = 0.0005
```

Only after all four passed did the gate value move.

---

## 2. Anchors — before and after

| Artifact | BEFORE | AFTER | Verdict |
| --- | --- | --- | --- |
| Amendment, whole file | 42,213 B / `e1b4a11d18ad2907af4f0a93fd5747d2` / 591 lines | 42,715 B / `45453596402874bf6c52ae490241eb86` / 594 lines | changed (prose outside the markers) |
| **Amendment, paste block** | **22,945 B / `422f1f28d6a3b76c7657fadec05a0237`** | **22,945 B / `422f1f28d6a3b76c7657fadec05a0237`** | **IDENTICAL — the invariant** |
| `.planning/osf_deviations.md` | `dd3806312977513a8727463ec3a032df` | `dd3806312977513a8727463ec3a032df` | byte-unchanged |
| Banked record | — | 7,770 B / `20921ab9426c2169a2753749d3800934` / 70 lines | `cmp` silent vs scratchpad source |

Census on the final file:

| Check | Value | Required |
| --- | --- | --- |
| `grep -c '2689cae'` | 0 | 0 |
| `grep -c 'd45db429b3fa6c1f08989c418de911a1fe15fbf2'` | 2 | 2 |
| `grep -c '{{'` / `grep -c '}}'` | 0 / 0 | 0 / 0 |
| `grep -c '2026-08-21'` | 3 | 3 |
| `grep -c '2026-08-20'` | 4 | 4 (unchanged) |
| `grep -c '\bsix\b'` | 3 | 3 (the NaN pairs only) |
| `grep -c 'seven supporting records'` | 1 | 1 |
| `guard all` exit | 0 | 0 |

The new hash was re-resolved **independently** of the document, by
`git log --format=%H --grep='bank Seth.s final pass as-received' -1`, and matched — closing
T-jcs-02 (a hash with no provenance).

The amendment diff touched exactly four hunks — lines 63, 92, 140-143, 158-163 — **every one of
them before the opener marker at line 167**. The `POSTING_DATE` ledger line did not appear in the
diff at all, because its Class-P substitution was a value-preserving no-op.

---

## 3. Deviations from Plan

### [Rule 1 - Bug] The plan's own prescribed prose contradicted the plan's own assertion

**Found during:** Task 2 STEP F.

**Issue:** The plan's replacement text for prose edits (a) and (b) each contained the literal token
`2026-08-21`. Applying them as written took `grep -c '2026-08-21'` from 3 to **5**, colliding
head-on with the plan's own STEP F / verify assertion `== 3`. Same shape as the `2689cae` trap the
plan anticipated in T-jcs-04, but for the posting date, which the plan did not anticipate.

**Why it was not merely cosmetic.** I read the engine before choosing a side. `force_substitute_class_p`
does a **blind document-wide `text.replace(cur, new)`** on the literal date token, and its only
guard is *dynamic*:

```python
n_before = text.count(cur)
text = text.replace(cur, new)
n_after = text.count(new)
if n_after != n_before:  die(...)
```

Because the fence compares after-count to before-count, **extra prose copies pass it silently** —
the engine would have rewritten them without complaint. The engine's one hard-coded PROBE protects
only the `2026-08-20` instantiation date. And the posting card's own if-it-slips rule makes a
future `--posting-date` pass a **live, expected event**, not a hypothetical. So a prose copy of the
token would have been silently rewritten, turning the true statement *"re-read at the 2026-08-21
posting-prep re-confirmation"* into the false *"...at the 2026-08-22 posting-prep re-confirmation"*.
The re-confirmation date is a historical fact, not a provisional slot value.

**Fix:** rewrote both prose sentences to the unsubstitutable form **"21 August 2026"**. The
assertion was **not** loosened. The date token now appears only at its three machine-owned slots
(line 64 row, line 91 ledger, line 171 paste-block `**Date:**`). Documented on the posting card so
the next re-confirmation preserves the property.

**Files modified:** the amendment (prose only, outside the markers). **Commit:** `4487a18`.

### [Wording precision, not a rule] Gate-row commit enumeration

The plan's template read *"every commit between that value and this one is docs-only (…, `d45db42`)"*
while listing `d45db42` — which **is** "this one". Written as *"every commit from that value up to
and including this one is docs-only"* so the sentence matches the list it carries. `2689cae` appears
nowhere in the result, as T-jcs-04 requires.

### [Out of scope — NOT fixed] `260821-jam` is a duplicate of this task

`.planning/quick/260821-jam-bank-seth-final-pass-as-7th-record-pre-p/260821-jam-PLAN.md` carries the
**same objective** as this task, from a parallel terminal on this shared GPFS tree. Its commits
(`36006c5`, `41349e2`, `4307278`) touch **only its own PLAN.md** — it has executed no artifact work;
every artifact here is `260821-jcs`'s. Its own reconcile message reads *"the 7th record landed from
a parallel terminal"*, i.e. it observed this task's `d45db42`.

Its plan still REQUIREs the amendment's **pre-task** anchors (`42,213 B / 591 lines / e1b4a11d…`) at
lines 124, 279, 321 — which `4487a18` legitimately superseded. It would go red on a stale pin.
**Not fixed deliberately:** editing a live parallel terminal's plan is exactly the collision
`feedback_multi_terminal_staging` was baked to prevent. Logged to `deferred-items.md`; needs a human
routing call. The 15 paste-block anchors jam pins are **unchanged and still correct**.

---

## 4. Seen-red evidence (both controls RE-EXECUTED in this task)

Each control is a 2-cell matrix on the **same fixture path**, so the red is attributable. Fixtures
lived only in `<scratchpad>/260821-jcs-NEGATIVE-CONTROL-DO-NOT-COMMIT/`;
`git status --porcelain | grep -c '260821-jcs-NEGATIVE'` = **0** throughout.

### NC-1 — a re-introduced `{{SLOT}}` sentinel must drive `guard all` red

**GREEN cell** — unperturbed copy, same path, same basename:

```
$ bash <guard> all $NC/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
PASS: vacuity: paste block 23001 B (floor 3000 B)
PASS: quote: source range ...:102-107 yields 4 non-blank lines
PASS: quote: count identity holds: 4/4 source lines carried verbatim
GUARD all: GREEN
NC1-GREEN EXIT=0
```

**RED cell** — exactly one ledger line perturbed back to a sentinel
(`CEILING_3X_MEDIAN_PCT = 0.5056%` → `{{CEILING_3X_MEDIAN_PCT}}`):

```
perturbed 1 ledger line -> sentinel
FAIL: paste-ready: 1 opening and 1 closing sentinel delimiters remain — the body is UNINSTANTIATED and MUST NOT be pasted
PASS: paste-ready: basename carries no XX date placeholder: osf-amendment-occlusion-gate-recalibration-2026-08-20.md
FAIL: paste-ready: ledger line CEILING_3X_MEDIAN_PCT does not match its filled-value pattern (^  CEILING_3X_MEDIAN_PCT = [0-9]+\.[0-9]+%$) — filled wrongly, or DELETED instead of filled
FAIL: arith: cannot verify — draft not instantiated; these ledger values are still sentinels or blank: CEILING_3X_MEDIAN_PCT
GUARD all: RED
NC1-RED EXIT=1
```

### NC-2 — one perturbed per-region value must drive the engine's RECONCILIATION red

Perturbation, asserted to be exactly one line (`diff | grep -c '^[<>]'` = **2**):

```
BEFORE:     m2_region_00042         43690   41515   119  112  0.2724  0.2698  1.06
AFTER :     m2_region_00042         43690   41515   119  112  0.2724  0.2599  1.06
```

**GREEN cell** — same command, unperturbed banked source:

```
$ python3 <engine> --dry-run
  SITE_MAX_PCT                 0.269800     0.269800   0.000000   0.0001 OK
RECONCILIATION: OK — every printed aggregate re-derives from its components
NC2-GREEN EXIT=0
```

**RED cell** — the documented control mode:

```
$ python3 <engine> --dry-run --control-source $NC/site-basis-PERTURBED.md
*** NEGATIVE CONTROL MODE — WRITE PATH DISABLED ***
RECONCILIATION — printed summary vs recomputed from the 21-row table
  STATISTIC                     PRINTED   RECOMPUTED      DELTA      TOL VERDICT
  SITE_MIN_PCT                 0.134500     0.134500   0.000000   0.0001 OK
  SITE_MEDIAN_PCT              0.168500     0.168500   0.000000   0.0001 OK
  SITE_MAX_PCT                 0.269800     0.259900   0.009900   0.0001 MISMATCH
  SITE_ROBUST_SIGMA_PCT        0.027400     0.027428   0.000028   0.0001 OK
  MEAN_ROW_SITE_INFLATION      1.180000     1.180476   0.000476   0.0050 OK
  CEILING_3X_MEDIAN_PCT        0.505600     0.505500   0.000100   0.0010 OK (printed value kept)
  CEILING_MARGIN_X             1.870000     1.945364   0.075364   0.0200 MISMATCH
NC2-RED EXIT=1
```

The red names exactly the predicted failure: the printed `max=0.2698%` no longer re-derives from
its own column. A global `sed` would have rewritten the summary too and defeated the control; the
perturbation was scoped to the single table row.

---

## 5. Commits

| Commit | Subject |
| --- | --- |
| `d45db42` | docs(debug): bank Seth's final pass as-received — no blocking objection; seventh supporting record |
| `4487a18` | docs(amendment): RE-CONFIRMED AT POSTING — PRE_EXECUTE_COMMIT advanced to d45db42 by engine Class-P pass; paste block byte-identical (422f1f28…) |
| `996797d` | docs(debug): posting card for Carter — az52u NEW-file upload, fresh anchors, post-upload captures, if-it-slips rule |
| `da7f86e` | docs(quick-260821-jcs): close-out — Seth's final pass banked, RE-CONFIRMED AT POSTING executed (engine Class-P, paste block byte-identical), posting card ready; NEXT = Carter posts |

Interleaved on the branch by the parallel terminal: `36006c5`, `41349e2`, `4307278` (all
`260821-jam`, all touching only that task's own PLAN.md).

**Final HEAD after push:** `da7f86e205838545ef581517dc7ed072db6f8a57`
**`origin == local`:** confirmed (`git rev-parse HEAD` == `git rev-parse origin/m3-W2-aou-deltas`)
**`git status -sb`:** `## m3-W2-aou-deltas...origin/m3-W2-aou-deltas` — 0 dirty tracked `.planning/` paths

---

## 6. Nothing was posted and nothing was fired

- Zero OSF contact of any kind. Carter posts; an agent never does.
- Zero AoU / VM / cluster action. $0 spent.
- `src/`, `tests/`, `config/` byte-unchanged across the whole span (`git diff --stat` empty).
- `.planning/osf_deviations.md` byte-unchanged at `dd3806312977513a8727463ec3a032df` — the prepared
  deviation entry remains **prepared and un-appended**, as designed.
- `HANDOFF.gates.*` deliberately untouched and asserted unchanged; the gate moves in the record
  task, after posting.

---

## Status

```
measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires.
```

---

## Appendix 1 — engine `--second-pass` stdout, VERBATIM (exit 0)

```
$ python3 .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py \
        --second-pass \
        .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
        --pre-execute-commit d45db429b3fa6c1f08989c418de911a1fe15fbf2 --posting-date 2026-08-21
ENGINE EXIT=0

RECONCILIATION — printed summary vs recomputed from the 21-row table
  source: .planning/debug/260820-site-basis-sweep-results-as-received.md
  STATISTIC                     PRINTED   RECOMPUTED      DELTA      TOL VERDICT
  SITE_MIN_PCT                 0.134500     0.134500   0.000000   0.0001 OK
  SITE_MEDIAN_PCT              0.168500     0.168500   0.000000   0.0001 OK
  SITE_MAX_PCT                 0.269800     0.269800   0.000000   0.0001 OK
  SITE_ROBUST_SIGMA_PCT        0.027400     0.027428   0.000028   0.0001 OK
  MEAN_ROW_SITE_INFLATION      1.180000     1.180476   0.000476   0.0050 OK
  CEILING_3X_MEDIAN_PCT        0.505600     0.505500   0.000100   0.0010 OK (printed value kept)
  CEILING_MARGIN_X             1.870000     1.873981   0.003981   0.0200 OK
RECONCILIATION: OK — every printed aggregate re-derives from its components

ROW-BASIS RECONCILIATION — printed summary vs recomputed from the 21 `frac=` values
  source: .planning/debug/260819-occ-measure-sweep-results-as-received.md
  STATISTIC                     PRINTED   RECOMPUTED      DELTA      TOL VERDICT
  ROW_MIN_PCT                  0.132300     0.132300   0.000000   0.0001 OK
  ROW_MEDIAN_PCT               0.188800     0.188800   0.000000   0.0001 OK
  ROW_MAX_PCT                  0.352700     0.352700   0.000000   0.0001 OK
ROW-BASIS RECONCILIATION: OK — the row median re-derives from its own components

PRE-REGISTERED RENDER EXPECTATIONS (260820-u6i-PLAN.md)
  FRACTION_RATIO_X         computed 1.12x      expected 1.12x      OK
  INFLATION_CEILING_3X_X   computed 3.42x      expected 3.42x      OK
  INFLATION_MARGIN_X       computed 1.91x      expected 1.91x      OK
  INFLATION_MAX_X          computed 1.79x      expected 1.79x      OK
  INFLATION_MEDIAN_X       computed 1.14x      expected 1.14x      OK
  INFLATION_MIN_X          computed 1.04x      expected 1.04x      OK
  INFLATION_ROBUST_SIGMA_X computed 0.0890x    expected 0.0890x    OK
  ROW_MEDIAN_PCT           computed 0.1888%    expected 0.1888%    OK
PRE-REGISTERED EXPECTATIONS: OK — all 8 rendered strings byte-identical

RENDER CHECK: OK — 21 of 21 rendered ledger lines match their guard patterns

CLASS-M DRIFT VERIFY — every already-filled ledger value must be byte-identical to the value just computed from the banked records
  VERIFIED-IN-PLACE  SITE_MIN_PCT             = 0.1345%
  VERIFIED-IN-PLACE  SITE_MEDIAN_PCT          = 0.1685%
  VERIFIED-IN-PLACE  SITE_MAX_PCT             = 0.2698%
  VERIFIED-IN-PLACE  SITE_ROBUST_SIGMA_PCT    = 0.0274%
  VERIFIED-IN-PLACE  MEAN_ROW_SITE_INFLATION  = 1.18x
  VERIFIED-IN-PLACE  MED_PLUS_3SIG_PCT        = 0.2507%
  VERIFIED-IN-PLACE  MED_PLUS_4SIG_PCT        = 0.2781%
  VERIFIED-IN-PLACE  TWO_X_MEDIAN_PCT         = 0.3370%
  VERIFIED-IN-PLACE  TWO_X_MAX_PCT            = 0.5396%
  VERIFIED-IN-PLACE  CEILING_3X_MEDIAN_PCT    = 0.5056%
  VERIFIED-IN-PLACE  CEILING_MARGIN_X         = 1.87x
  VERIFIED-IN-PLACE  ROW_MEDIAN_PCT           = 0.1888%
  VERIFIED-IN-PLACE  FRACTION_RATIO_X         = 1.12x
  VERIFIED-IN-PLACE  INFLATION_MIN_X          = 1.04x
  VERIFIED-IN-PLACE  INFLATION_MEDIAN_X       = 1.14x
  VERIFIED-IN-PLACE  INFLATION_MAX_X          = 1.79x
  VERIFIED-IN-PLACE  INFLATION_ROBUST_SIGMA_X = 0.0890x
  VERIFIED-IN-PLACE  INFLATION_CEILING_3X_X   = 3.42x
  VERIFIED-IN-PLACE  INFLATION_MARGIN_X       = 1.91x
CLASS-M DRIFT VERIFY: OK — 19 already-filled measured value(s) unmoved

CLASS-P FORCE-SUBSTITUTION — argv-sourced slots, replaced at EVERY occurrence (they are DEFINED to move; the pre-paste table commits to re-confirming both at posting)
  FORCE-SUBSTITUTED POSTING_DATE         2026-08-21 -> 2026-08-21  (3 occurrence(s); '2026-08-20' count 4 unchanged across the replace)
  FORCE-SUBSTITUTED PRE_EXECUTE_COMMIT   2689cae… -> d45db42…  (2 occurrence(s); '2026-08-20' count 4 unchanged across the replace)

SUBSTITUTION LEDGER — .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  SLOT                     | VALUE                                      | OCCURRENCES | SOURCE
  SITE_MIN_PCT             | 0.1345%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  SITE_MEDIAN_PCT          | 0.1685%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  SITE_MAX_PCT             | 0.2698%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  SITE_ROBUST_SIGMA_PCT    | 0.0274%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  MEAN_ROW_SITE_INFLATION  | 1.18x                                      |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  MED_PLUS_3SIG_PCT        | 0.2507%                                    |           0 | derived [VERIFIED-IN-PLACE]
  MED_PLUS_4SIG_PCT        | 0.2781%                                    |           0 | derived [VERIFIED-IN-PLACE]
  TWO_X_MEDIAN_PCT         | 0.3370%                                    |           0 | derived [VERIFIED-IN-PLACE]
  TWO_X_MAX_PCT            | 0.5396%                                    |           0 | derived [VERIFIED-IN-PLACE]
  CEILING_3X_MEDIAN_PCT    | 0.5056%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  CEILING_MARGIN_X         | 1.87x                                      |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  ROW_MEDIAN_PCT           | 0.1888%                                    |           0 | parsed (row sweep) [VERIFIED-IN-PLACE]
  FRACTION_RATIO_X         | 1.12x                                      |           0 | derived (cross-basis) [VERIFIED-IN-PLACE]
  INFLATION_MIN_X          | 1.04x                                      |           0 | column stat (site sweep) [VERIFIED-IN-PLACE]
  INFLATION_MEDIAN_X       | 1.14x                                      |           0 | column stat (site sweep) [VERIFIED-IN-PLACE]
  INFLATION_MAX_X          | 1.79x                                      |           0 | column stat (site sweep) [VERIFIED-IN-PLACE]
  INFLATION_ROBUST_SIGMA_X | 0.0890x                                    |           0 | column stat (site sweep) [VERIFIED-IN-PLACE]
  INFLATION_CEILING_3X_X   | 3.42x                                      |           0 | derived [VERIFIED-IN-PLACE]
  INFLATION_MARGIN_X       | 1.91x                                      |           0 | derived [VERIFIED-IN-PLACE]
  POSTING_DATE             | 2026-08-21                                 |           0 | argv [FORCE-SUBSTITUTED (argv)]
  PRE_EXECUTE_COMMIT       | d45db429b3fa6c1f08989c418de911a1fe15fbf2   |           0 | argv [FORCE-SUBSTITUTED (argv)]
  TOTALS                   | 21 slots                                   |           0 | pre-count '{{'=0 '}}'=0, post-count 0/0
```

**19 VERIFIED-IN-PLACE / 0 SUBSTITUTED / 2 FORCE-SUBSTITUTED, exit 0** — exactly as the plan
predicted.

## Self-Check: PASSED

All 4 claimed files exist on disk; all 4 claimed commits resolve in `git log --all`;
the engine appendix, both RED transcripts, the final HEAD and the status line are present in this
SUMMARY. Every anchor in section 2 was re-measured at the final pushed HEAD, not carried forward
from an earlier step.
