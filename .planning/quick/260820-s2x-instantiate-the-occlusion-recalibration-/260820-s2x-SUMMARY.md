---
phase: quick-260820-s2x
plan: 01
subsystem: pre-registration
tags: [osf, amendment, occlusion, clause-d, anomaly-gate, calibration, guard, slot-instantiation, narrative-audit, seth-courier, m3-07]

requires:
  - phase: quick-260819-u8d
    provides: the slot-sentinelled amendment draft, the placeholder guard, and the adoption decision record
provides:
  - the banked site-basis sweep record (fifth and final supporting record; all five now tracked)
  - the instantiated, narrative-audited amendment at its instantiation-dated basename, guard all exit 0
  - a substitution engine that parses the banked record rather than accepting numbers as arguments
  - a guard transcript carrying two greens and four reds across three named negative controls
  - a brief-blind courier to Seth carrying byte anchors he can verify himself
affects: [m3-07 OSF gate, Seth review round 4, Carter posting step, occlusion gate remediation, Stage A]

tech-stack:
  added: []
  patterns:
    - "Class-M values enter a public-record artifact only through a script that PARSES the banked source"
    - "aggregate/component reconciliation before any write (an aggregate can agree while its components are wrong)"
    - "per-control signature strings in a sectioned transcript, because a whole-file grep cannot tell controls apart"
    - "content-identity assertion on a cosmetic rewrap (token sequence must be byte-identical before/after)"

key-files:
  created:
    - .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
    - .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-guard-transcript.txt
    - .planning/debug/260820-COURIER-TO-SETH-instantiated-amendment.md
    - .planning/debug/260820-site-basis-sweep-results-as-received.md
  modified:
    - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md

key-decisions:
  - "CEILING_3X_MEDIAN_PCT carried AS PRINTED at 0.5056%, not recomputed to 0.5055% — the printed value came from the unrounded median and the delta is inside the guard's tolerance"
  - "A8: no site-basis sentence added to section (c) — duplicating literals invites drift; the site-basis figures are stated once, labelled, in (d)"
  - "A18(ii): only the project-side copy path filled; every OSF-observed marker (GUID, URL, UTC timestamp, posted filename, post-time commit) left as <TO BE FILLED AT POSTING>"
  - "Audit edits applied by a scratchpad script that PARSES the file's own SLOT_LEDGER, so no site-basis literal and no relation ratio was hand-typed"
  - "Six paragraphs rewrapped under a must-be-identity token assertion rather than trusted to eyeballing"

patterns-established:
  - "Pattern: a green is recorded in the same artifact as the reds that license it, sectioned so each control proves its own claim"
  - "Pattern: a cosmetic transform is gated by an identity assertion, not by review"

requirements-completed:
  - DEC-2026-08-19-occlusion-recalibration-adopted
  - OSF-AMEND-OCCLUSION-INSTANTIATE

duration: ~20min
completed: 2026-08-20
---

# quick-260820-s2x: Instantiate the Occlusion-Recalibration Amendment Summary

**The occlusion-gate recalibration amendment is instantiated from the banked site-basis sweep by script (never a hand-typed digit), its derivation prose is audited onto the relations that actually hold on site basis — median+4σ moved from BELOW the observed maximum to 1.03x ABOVE it — and `guard all` exits 0 on a file whose own pre-instantiation red was re-observed first.**

## Performance

- **Duration:** ~20 min (20:44 -> 21:04 EDT; commits at 20:48:59 / 20:57:03 / 20:58:20)
- **Tasks:** 3/3
- **Files created:** 4 · **Files modified:** 1 (plus the rename)
- **Commits:** 3 (`88899d6`, `e59af9f`, `13b4543`)

## Accomplishments

- Banked `.planning/debug/260820-site-basis-sweep-results-as-received.md` — the fifth supporting record the amendment's pre-paste checklist requires. All five are now tracked, so the amendment's sole Class-M source is reproducible from the repo alone and not from chat.
- Renamed the amendment off the `XX` placeholder with `git mv` (rename detected at R093, history follows).
- Instantiated all 13 slots (29 sentinel occurrences) via `260820-s2x-instantiate.py`.
- Audited 18 register items against the site-basis relations; 16 text edits applied, all with verbatim before/after below.
- Recorded two greens (pre- and post-audit) and four reds, each control with its own signature message.
- Wrote a 63-line brief-blind courier carrying `wc -c` and `md5sum` anchors computed after the amendment's final commit.

---

## 1. Substitution ledger (script stdout, verbatim)

```
SUBSTITUTION LEDGER — .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  SLOT                     | VALUE                                      | OCCURRENCES | SOURCE
  SITE_MIN_PCT             | 0.1345%                                    |           2 | parsed
  SITE_MEDIAN_PCT          | 0.1685%                                    |           2 | parsed
  SITE_MAX_PCT             | 0.2698%                                    |           2 | parsed
  SITE_ROBUST_SIGMA_PCT    | 0.0274%                                    |           2 | parsed
  MEAN_ROW_SITE_INFLATION  | 1.18x                                      |           3 | parsed
  MED_PLUS_3SIG_PCT        | 0.2507%                                    |           2 | derived
  MED_PLUS_4SIG_PCT        | 0.2781%                                    |           2 | derived
  TWO_X_MEDIAN_PCT         | 0.3370%                                    |           2 | derived
  TWO_X_MAX_PCT            | 0.5396%                                    |           2 | derived
  CEILING_3X_MEDIAN_PCT    | 0.5056%                                    |           3 | parsed
  CEILING_MARGIN_X         | 1.87x                                      |           2 | parsed
  POSTING_DATE             | 2026-08-21                                 |           3 | argv
  PRE_EXECUTE_COMMIT       | 8638ed37c1431ea73566fd03ad1541ba95416fe4   |           2 | argv
  TOTALS                   | 13 slots                                   |          29 | pre-count '{'+'{'=29 '}'+'}'=29, post-count 0/0
```

The per-slot occurrence counts and the total of 29 reproduce the PLAN's pre-registered census
exactly. The script MEASURED them and asserted `sum(replacements) == pre-count == post-count-of-zero`;
the PLAN's table was the expectation, never the script's input. The four DERIVED values also
reproduce the PLAN's pre-registered expectations (0.2507% / 0.2781% / 0.3370% / 0.5396%), so a
script producing anything else would have been loudly wrong.

> The `TOTALS` line above is transcribed with the double-brace delimiters split (`'{'+'{'`) so
> that this SUMMARY does not itself contain a slot sentinel. The script's real stdout prints
> them normally.

## 2. Reconciliation — printed summary vs recomputed from the 21 per-region rows

Verbatim script stdout. Nothing was written until every line below read OK.

```
RECONCILIATION — printed summary vs recomputed from the 21-row table
  STATISTIC                     PRINTED   RECOMPUTED      DELTA      TOL VERDICT
  SITE_MIN_PCT                 0.134500     0.134500   0.000000   0.0001 OK
  SITE_MEDIAN_PCT              0.168500     0.168500   0.000000   0.0001 OK
  SITE_MAX_PCT                 0.269800     0.269800   0.000000   0.0001 OK
  SITE_ROBUST_SIGMA_PCT        0.027400     0.027428   0.000028   0.0001 OK
  MEAN_ROW_SITE_INFLATION      1.180000     1.180476   0.000476   0.0050 OK
  CEILING_3X_MEDIAN_PCT        0.505600     0.505500   0.000100   0.0010 OK (printed value kept)
  CEILING_MARGIN_X             1.870000     1.873981   0.003981   0.0200 OK
RECONCILIATION: OK — every printed aggregate re-derives from its components
RENDER CHECK: OK — all 13 rendered ledger lines match their guard patterns
```

`CEILING_3X_MEDIAN_PCT` is the printed **0.5056%**, not a recomputed 0.5055%: it was computed
upstream from the unrounded median, the delta is 0.0001 percentage points, and the check is an
inside-tolerance check by design rather than an equality check.

## 3. Audit register — all 18 items dispositioned

Line numbers are in the FINAL file. Every edit below was applied by a scratchpad script that
parses the file's own `SLOT_LEDGER` and computes each relation ratio from those parsed values,
so no site-basis literal and no ratio in the new prose was hand-typed.

### A1 — line 5 — **CHANGED**

BEFORE
```
> **The body below is UNINSTANTIATED.** Every quantity that the site-basis re-measurement
> (PENDING PASTE #3) must supply is a named double-brace slot sentinel, not a number. The
> enforcer `260819-u8d-placeholder-guard.sh` (section `all`) is the gate that must be GREEN
> before any paste; it is RED today by design, and its red is the guard working.
```
AFTER
```
> **The body below is INSTANTIATED.** Every quantity the site-basis re-measurement had to
> supply was substituted from the banked sweep record
> `.planning/debug/260820-site-basis-sweep-results-as-received.md` by
> `.planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py`,
> which PARSES that record rather than taking the numbers as arguments; no value was
> hand-typed. The enforcer `260819-u8d-placeholder-guard.sh` (section `all`) is the gate that
> must be GREEN before any paste, and it is GREEN on this file. That green is evidence only
> because this file's own reds were re-observed: the pre-instantiation version, a perturbed
> arithmetic identity, and a ledger value deleted rather than filled, all at exit 1 and
> transcribed verbatim in
> `.planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-guard-transcript.txt`.
> INSTANTIATED IS NOT POSTED — the banner above still governs.
```
The DRAFT — NOT POSTED banner at lines 1-3 is byte-untouched.

### A2 — line 21 — **CHANGED**

BEFORE
```
> finds the check from this artifact rather than from memory; the amendment argument follows
> this file when it is renamed at posting):
> `bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md`
```
AFTER
```
> finds the check from this artifact rather than from memory; the rename off the `XX`
> placeholder has happened, so the argument below is this file's own current path):
> `bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md`
```

### A3 — line 49 — **CHANGED**

BEFORE
```
| Pre-execute commit gate | `8638ed37c1431ea73566fd03ad1541ba95416fe4` — fill with the HEAD of `m3-W2-aou-deltas` at posting time, and confirm no gate-constant change has landed. |
```
AFTER
```
| Pre-execute commit gate | `8638ed37c1431ea73566fd03ad1541ba95416fe4` — the HEAD of `m3-W2-aou-deltas` at INSTANTIATION time, captured before the first commit of the instantiating task. RE-CONFIRMED AT POSTING: re-read HEAD, confirm no `_OCCLUSION_ANOMALY_FRACTION` or gate-constant change has landed since, and update this value if the branch has advanced. |
```

### A4 — line 50 — **CHANGED**

BEFORE
```
| Expected posting date | `2026-08-21` |
```
AFTER
```
| Expected posting date | `2026-08-21` — **PROVISIONAL**. If posting slips this is a one-token edit at each of its three occurrences (this row, its SLOT_LEDGER line, and the paste block's **Date:** line) plus a `guard all` re-run. The BASENAME does not change: the `2026-08-20` in the filename records the INSTANTIATION date, which is a different quantity from the posting date. A mismatch between the two is expected, not an error. |
```
The three occurrences named are measured, not assumed: lines 50, 69, 124.

### A5 — line 73 onward — **CHANGED** (two edits, A5 and A5b)

BEFORE (head)
```
**Instantiation instructions (do NOT paste this block).**

1. Run PENDING PASTE #3 (`.planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md`) on the
   VM and paste its stdout verbatim. The harness cross-check must hold: region 1 must
   reproduce `n_occluded_rows == 231` exactly, or all results are discarded.
2. Read the eleven Class-M values off that stdout. Seven come directly from the printed
   `SITE-BASIS SUMMARY`, `CANDIDATE CEILING`, `margin over observed site-basis max` and
   `mean row/site inflation` lines; four are DERIVED by these formulas:
```
AFTER (head)
```
**Instantiation record — what was PERFORMED (do NOT paste this block).**

1. PENDING PASTE #3 (`.planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md`) was run on
   the VM and its stdout banked verbatim at
   `.planning/debug/260820-site-basis-sweep-results-as-received.md`. The harness cross-check
   HELD: region 1 reproduced `n_occluded_rows == 231` exactly, with the assert preceding the
   summary, so no result was discarded.
2. The eleven Class-M values were read off that banked record BY SCRIPT. Seven came directly
   from the printed `SITE-BASIS SUMMARY`, `CANDIDATE CEILING`, `margin over observed
   site-basis max` and `mean row/site inflation` lines; four were DERIVED by these formulas:
```
BEFORE (tail, steps 3-6)
```
3. Substitute each Class-M slot **ONCE, everywhere it occurs**, including its SLOT_LEDGER
   line. Percentage slots render as `0.1234%`; the two ratio slots render as `1.23x`.
4. Fill the two Class-P slots at posting time: `POSTING_DATE` as `2026-08-21` shape,
   `PRE_EXECUTE_COMMIT` as the 7-40 hex-character HEAD.
5. Rename this file so its basename no longer contains the `XX` date placeholder — the guard
   FAILS while `XX` remains in the basename.
6. Run the guard's `paste-ready` and `arith` sections and require GREEN on both. Do not paste
   otherwise.
```
AFTER (tail, steps 3-6)
```
   The same script re-derived min / median / robust sigma / max and the mean row/site
   inflation from the banked record's own 21-row per-region table and required each to agree
   with the printed summary BEFORE writing anything — an aggregate can agree while its
   components are wrong. `CEILING_3X_MEDIAN_PCT` is carried AS PRINTED, because it was
   computed upstream from the unrounded median; three times the 4-decimal median differs from
   it by 0.0001 percentage points, inside the guard's tolerance.
3. Each Class-M slot was substituted **ONCE, everywhere it occurred**, including its
   SLOT_LEDGER line, and the script asserted that the number of replacements equalled the
   file's pre-substitution slot-sentinel count and that none survived. Percentage slots render
   as `0.1234%`; the two ratio slots render as `1.23x`.
4. The two Class-P slots were filled at instantiation, not at posting: `POSTING_DATE`
   provisionally, and `PRE_EXECUTE_COMMIT` as the full 40-hex HEAD captured before the
   instantiating task's first commit. Both are re-confirmed at posting.
5. This file was renamed with `git mv`, so its basename no longer contains the `XX` date
   placeholder and its history follows the rename — the guard FAILS while `XX` remains in the
   basename, and that failure was re-observed on the pre-rename copy as a negative control.
6. The guard's `paste-ready` and `arith` sections were run and are GREEN, as are `draft` and
   `quote`; section `all` exits 0. Do not paste otherwise.
```
Step 6's "Do not paste otherwise" is kept. The rendering EXAMPLE `0.1234%` is kept, and it is
one of the two literals in the census exemption set.

### A6 — line 142 — **STANDS**

`…measured here as 1.18x on average across the sample.` Post-substitution read-through: true
against the banked `mean row/site inflation across sample: 1.18x`. No edit.

### A7 — line 181 — **STANDS**

`Geometric occlusion at **0.1323% to 0.3527% of rows (row basis)**` — the ROW label is intact
and adjacent to both literals.

### A8 — lines 199-203 — **STANDS (decision recorded)**

Every literal in *The measured distribution (row basis).* (0.1323% / 0.1888% / 0.3527% /
0.0393%) sits under the paragraph's own `(row basis)` head. **Decision: no site-basis sentence
added to (c).** Rationale: the four site-basis figures are already stated once, each with a
`(site basis)` label, in (d); a second copy in (c) would create two places for the same number
to live and the census would then have to police both. Duplicating a literal is the drift
mechanism this amendment exists to correct, so the default was kept.

### A9 — line 248 — **CHANGED**

BEFORE
```
*Ceiling.* `n_occluded_sites <= 0.5056% x n_sites` — that is, **3x the
measured site-basis median** of 0.1685% (site basis) — giving
1.87x margin over the observed site-basis maximum of 0.2698% (site
basis). The measured site-basis minimum is 0.1345% (site basis) and the robust sigma
is 0.0274% (site basis).
```
AFTER
```
*Ceiling.* `n_occluded_sites <= 0.5056% x n_sites` — that is, **3x the measured site-basis
median** of 0.1685% (site basis), or 0.005056 expressed as a bare fraction, since the
withdrawn ceiling was written as a fraction and this one is written as a percentage. It
gives 1.87x margin over the observed site-basis maximum of 0.2698% (site basis). The
measured site-basis minimum is 0.1345% (site basis) and the robust sigma is 0.0274% (site
basis).
```
Every clause confirmed true. The bare-fraction gloss was added because the withdrawn ceiling
was a fraction (`0.0005`) and the new one is a percentage (`0.5056%`); without it a reviewer
comparing 0.5056 against 0.0005 reads a 1000x change that is not there. The fraction is
computed from the ledger, not typed.

### A10 — line 259 — **STANDS, sharpened**

BEFORE
```
| median + 3 sigma_rob | 0.2507% | REJECT — at or below the observed maximum; a normal region would defer. |
```
AFTER
```
| median + 3 sigma_rob | 0.2507% | REJECT — 0.93x of the observed site-basis maximum, i.e. BELOW it; a normal region would defer. |
```
The claim was already true on site basis (0.2507% < 0.2698%); the ratio makes the table uniform.

### A11 — line 260 — **CHANGED (pre-identified as CHANGE REQUIRED)**

BEFORE
```
| median + 4 sigma_rob | 0.2781% | REJECT — still calibrated to the sample's spread, not to the purpose. |
```
AFTER
```
| median + 4 sigma_rob | 0.2781% | REJECT — 1.03x the observed site-basis maximum, so it hugs the sample edge: calibrated to the sample's spread and to where this sample happened to stop, not to the gate's purpose, and leaving nothing for an unmeasured upper tail. |
```
This is the item the whole task exists for. On ROW basis median+4σ sat BELOW the observed max
(0.98x) and the old rationale fitted. On SITE basis it sits at 1.03x, ABOVE it, so the
rationale becomes Seth's own reason for rejecting 2x-median at 1.07x. The REJECT verdict is
unchanged.

### A12 — line 261 — **CHANGED**

BEFORE
```
| 2x median | 0.3370% | REJECT — too tight for n=21; leaves no room for an unmeasured upper tail. |
```
AFTER
```
| 2x median | 0.3370% | REJECT — too tight for n=21; leaves no room for an unmeasured upper tail. Its margin on site basis is 1.25x the observed site-basis maximum, NOT the 1.07x of the row-basis derivation. |
```
The 1.07x is retained only as an explicitly row-labelled contrast, so no reader carries it across.

### A13 — lines 262-263 — **CHANGED (ordering confirmed NOT inverted)**

Ordering check first: 2x observed max **0.5396%** still sits ABOVE 3x median **0.5056%**
(delta 0.0340 percentage points), as it did on row basis. No inversion, so no STOP. The check
is also an assertion in the audit script, which aborts before writing if it ever fails.

BEFORE
```
| 2x observed max | 0.5396% | CANDIDATE — but anchored on where the sample happened to stop. |
| **3x median** | **0.5056%** | **ADOPTED.** |
```
AFTER
```
| 2x observed max | 0.5396% | CANDIDATE — 2.00x the observed site-basis maximum by construction, but anchored on where the sample happened to stop. |
| **3x median** | **0.5056%** | **ADOPTED** — 1.87x the observed site-basis maximum, anchored on a location statistic rather than on a sample edge. |
```

### A14 — line 265 — **CHANGED**

BEFORE
```
extending the sample moves the ceiling only if the population's centre moves; the resulting
margin over the observed maximum respects an upper tail that has not been measured; and it
```
AFTER
```
extending the sample moves the ceiling only if the population's centre moves; the resulting
1.87x margin over the observed site-basis maximum respects an upper tail that has not been
measured; and it
```
(Subsequently rewrapped; see §5.) The margin is now explicit and consistent with A9.

### A15 — line 270 — **STANDS**

`the same derivation applied to the row-basis distribution gives 3 x 0.1888% = **0.5664% (row
basis)**`. Arithmetic verified: 3 × 0.1888 = 0.5664 ✓. The `(row basis)` label is adjacent and
the following clause already says the site-basis figure is the one the gate uses and the
row-basis figure is reported only for reconcilability — so it cannot read as a second gate.

### A16 — line 274 — **CHANGED**

BEFORE
```
the sample. A ceiling at 8x or 10x the withdrawn constant also passes 21/21, and both are
REJECTED precisely because they would have been chosen for clearing the data — the original
error inverted. That 3x-median happens to pass 21/21 is a CONSEQUENCE of the derivation and
never its justification.
```
AFTER
```
the sample. A ceiling at 8x or 10x the withdrawn constant — that is 0.4% or 0.5% of
rows (row basis), the withdrawn 0.0005 being a row-basis fraction — also clears every region
in the row-basis distribution reported in (c), and both are REJECTED precisely because they
would have been chosen for clearing the data — the original error inverted. That 3x-median
happens to pass 21/21 is a CONSEQUENCE of the derivation and never its justification; the
same is true on site basis, where the adopted ceiling of 0.5056% (site basis) sits above the
observed site-basis maximum of 0.2698% (site basis) and so would spuriously defer 0 of the
21 sampled regions. That 0/21 is a consequence of the derivation, and is stated here as one;
it is not a reason for the multiplier and was not used as one.
```
Claim confirmed: 8 × 0.0005 = 0.004 = **0.4% of rows**, and the row-basis maximum 0.3527% is
below it, so 8x does clear 21/21 on row basis. The row basis label is now explicit so 0.4% is
not read as site basis. The row-basis maximum is referenced rather than restated, for the same
anti-duplication reason as A8. The site-basis 0/21 consequence is stated as a consequence and
is explicitly disclaimed as a reason.

### A17 — lines 305-312 (§8 verbatim) and line 314 — **STANDS, UNTOUCHED**

The four non-blank source lines of `260819-SETH-VERDICT-adjudication-confirmed-as-received.md:102-107`
are carried verbatim; the guard's `quote` section reports **4/4** in every run in the
transcript, before and after the audit. Line 314's `Both figures in that block are on the
**(row basis)** convention.` is intact, so 0.0059% and 0.2255% remain labelled. The posted-record
parenthetical is untouched.

### A18 — lines 410 and 425 — **CHANGED (two sub-items)**

**(i) line 425 — the stale "re-measurement pending" clause.**

BEFORE
```
  / robust sigma 0.0393%, 21/21 deferring at 0.0005, with the site-basis re-measurement
  supplying the gate's own number.
```
AFTER
```
  / robust sigma 0.0393%, 21/21 deferring at 0.0005, plus the site-basis re-measurement of
  the same 21 regions: site basis min 0.1345% / median 0.1685% / max 0.2698% / robust sigma
  0.0274% (site basis). The gate's own ceiling is 3x that site-basis median = 0.5056% (site
  basis), 1.87x the observed site-basis maximum.
```
All five values reuse the ledger exactly (they are read from it, not typed).

**(ii) line 410 — the `<TO BE FILLED AT POSTING>` markers.**

BEFORE
```
- **Project-side copy:** `.planning/amendments/osf-amendment-occlusion-gate-recalibration-<TO BE FILLED AT POSTING>.md`.
```
AFTER
```
- **Project-side copy:** `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md` (knowable now; the instantiation-dated basename does not move at posting).
```
Every OSF-observed marker was LEFT unfilled, deliberately, and each decision is recorded:

| Marker | Line | Decision | Why |
|---|---|---|---|
| entry heading date | 396 | LEFT | posting date, Carter-observed |
| OSF file GUID | 398 | LEFT | Carter-observed at the OSF file page |
| OSF file URL | 399 | LEFT | Carter-observed |
| posted filename | 400 | LEFT | OSF-side name, not knowable now |
| authoritative UTC timestamp | 407 | LEFT | from the OSF Recent Activity entry only |
| pre-execute gate commit at post time | 411 | LEFT | must be re-read at posting, not at instantiation |
| project-side copy path | 410 | **FILLED** | knowable now; the basename is the instantiation date |

`.planning/osf_deviations.md` and `.planning/amendments/osf_deviations.md` are both
byte-unchanged and unstaged — this block is TEXT inside the amendment only.

## 4. Guard evidence table

| Run | Section | Target | Exit | Observed message (signature) |
|---|---|---|---|---|
| GREEN | `all` | the instantiated file | **0** | `GUARD all: GREEN` (draft 13 ledger lines, `(site basis)` ×5, `(row basis)` ×4; paste-ready 13/13 filled patterns; arith 6/6 identities + ordering; quote 4/4 verbatim) |
| NC-1a | `paste-ready` | pre-instantiation version at its `XX` basename, from `git show 8638ed3:…-XX.md` | **1** | `FAIL: paste-ready: 29 opening and 29 closing sentinel delimiters remain — the body is UNINSTANTIATED and MUST NOT be pasted` **and** `FAIL: paste-ready: basename still carries the XX date placeholder: osf-amendment-occlusion-gate-recalibration-2026-08-XX.md` |
| NC-1b | `arith` | same file | **1** | `FAIL: arith: cannot verify — draft not instantiated; these ledger values are still sentinels or blank: …` (all 13) |
| NC-2 | `arith` | instantiated copy, ledger `SITE_MAX_PCT` perturbed to `0.2500%` | **1** | `FAIL: arith: TWO_X_MAX_PCT == 2*SITE_MAX_PCT BROKEN (0.5396 vs 0.5000%, |d|=0.0396 > tol 0.0010)` **and** `FAIL: arith: CEILING_MARGIN_X == CEILING_3X_MEDIAN_PCT / SITE_MAX_PCT BROKEN (1.8700 vs 2.0224x, |d|=0.1524 > tol 0.0200)` — and ONLY those two; ordering still holds, so the green on those two identities is load-bearing |
| NC-3 | `paste-ready` | instantiated copy, `SITE_MIN_PCT` ledger VALUE blanked | **1** | `FAIL: paste-ready: ledger line SITE_MIN_PCT does not match its filled-value pattern` — exactly ONE ledger-line failure, and the `draft` line count stays 13, so deletion-instead-of-instantiation is caught by the pattern and not by the count |
| POST-AUDIT | `all` | the audited file | **0** | `GUARD all: GREEN` — `(site basis)` ×8, `(row basis)` ×5, quote still 4/4 |

Transcript: `.planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-guard-transcript.txt`
(231 lines; five `### `-headed sections — GREEN / NC-1 / NC-2 / NC-3 / POST-AUDIT — carrying
two `EXIT=0` lines, the pre-audit green and the post-audit re-run, and four `EXIT=1` lines,
NC-1's two plus NC-2 and NC-3). All four counts measured, not asserted.

**Why the sections are named.** A whole-file `grep EXIT=1` cannot distinguish these controls:
NC-1's `paste-ready` emits a ledger-line failure for all 13 slots, including the one NC-3 is
supposed to be the sole source of. The verify therefore extracts each `### ` section and checks
that section's own signature, and asserts NC-3 shows exactly one ledger-line failure. That
check was run and passed on the real transcript, twice — once after Task 1 and once after the
POST-AUDIT section was appended.

**Fake-value controls never leaked.** Both fake copies live only in the session scratchpad and
carry `FAKE NUMBERS - GUARD CONTROL ONLY - NEVER POST` as their FIRST LINE. The check is a
first-line scan over tracked and untracked `.planning/` files (a bare `git grep "FAKE NUMBERS"`
would false-fail, because the string legitimately appears as prose in the u8d controls
transcript, in the PLAN, in the transcript's own preamble, and in this SUMMARY). Both scans
printed nothing. NC-1 carries no banner by design: it is real historical content from git, not
invented numbers.

## 5. Line-wrap repair (recorded, because it touched the artifact)

The substitution and the audit edits left ragged wrapping — short orphan lines and one
124-column line — in five prose paragraphs and one deviations bullet. Those were rewrapped at
92 columns by a scratchpad script that asserts the whitespace-separated **token sequence is
identical before and after**, so the transform provably cannot change a word or a number; it
can only move line breaks. It also asserts the four §8 verbatim lines survive, that no sentinel
delimiter exists, and that the ledger line count stays 13. Six regions changed, max column went
from 124 to 92, and the only remaining >100-column prose lines in the file are the two §8
verbatim lines, which are untouchable by contract.

## 6. Byte anchors

| Artifact | `wc -c` | `md5sum` |
|---|---|---|
| `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md` | **31685** | **b8f9a978c9bdbc7892f97b5d90cf9d27** |
| `.planning/debug/260820-COURIER-TO-SETH-instantiated-amendment.md` | 3212 | c917b1a1e0bd97c4b619249d74139ff9 |

The amendment anchors were computed AFTER Task 2's commit (`e59af9f`, working tree clean for
that path) and written into the courier; Task 3's verify recomputed both and required a match,
so a stale anchor would have failed the gate rather than travelled to Seth.

## 7. The posting-date rule (stated explicitly)

- `POSTING_DATE = 2026-08-21` is **PROVISIONAL**.
- If posting slips it is a one-token edit at each of its three measured occurrences — the
  pre-paste table row (line 50), the `SLOT_LEDGER` line (line 69), and the paste block's
  `**Date:**` line (line 124) — plus a `guard all` re-run.
- The BASENAME date `2026-08-20` is the **instantiation** date. It does NOT move. A mismatch
  between basename and posting date is expected, not an error, and the amendment now says so
  in its own text.
- `PRE_EXECUTE_COMMIT = 8638ed37c1431ea73566fd03ad1541ba95416fe4` is HEAD at instantiation,
  captured before this task's first commit. It is **re-confirmed at posting**: re-read HEAD,
  confirm no gate-constant change has landed, update if the branch has advanced.

## 8. What remains open

1. **Seth's brief-blind review** of the instantiated text, via
   `.planning/debug/260820-COURIER-TO-SETH-instantiated-amendment.md`. He states his own five
   dispositions before reading ours; the byte anchors let him confirm he is attacking the
   committed bytes.
2. **Carter posts** — as a NEW supplementary file on `osf.io/az52u`, never as a new version of
   `trsx5`. AN AGENT MUST NEVER FIRE.
3. **The deviations entry is appended** to `.planning/osf_deviations.md` only once the GUID,
   URL and authoritative UTC timestamp are in hand; the six remaining
   `<TO BE FILLED AT POSTING>` markers are filled at that moment.
4. **Only then** may `_OCCLUSION_ANOMALY_FRACTION` change in code, and only to the site-basis
   metric and ceiling pre-registered above. It stays `0.0005` until posting.
5. Then the remediation batch, then Stage A.

## Deviations from Plan

### Auto-fixed / judgement items

**1. [Rule 1 - Bug] Escaped a literal `%` in the audit script's format string**
- **Found during:** Task 2
- **Issue:** the A18(i) replacement text contained `0.0393%` inside a `%`-formatted string, which raised `ValueError: unsupported format character ','`.
- **Fix:** escaped it as `%%`. Caught by the script aborting before any write; the amendment was never touched in the failed run.
- **Files modified:** scratchpad script only.

**2. [Rule 2 - Correctness] Added the bare-fraction gloss to the ceiling sentence (A9)**
- **Issue:** the withdrawn ceiling is a fraction (`0.0005`) and the new one is a percentage (`0.5056%`). A reviewer comparing the two numerals without the units reads a 1000x change that does not exist. This is the same units/basis confusion class the amendment exists to correct.
- **Fix:** added `or 0.005056 expressed as a bare fraction, since the withdrawn ceiling was written as a fraction and this one is written as a percentage`. The fraction is computed from the ledger.

**3. [Rule 1 - Bug] Rewrapped six paragraphs whose wrapping this task had itself broken**
- **Issue:** substitution and audit edits left short orphan lines and one 124-column line in an artifact about to go to an adversarial reviewer.
- **Fix:** rewrap gated by a token-sequence identity assertion (see §5), not by eyeballing.

**4. [Plan overshoot, corrected] Courier first drafted at 69 lines**
- The PLAN's budget is "under ~60 lines; hard cap 75". The first draft was 69 — inside the hard cap but over the target. Tightened to **63** and the Task 3 commit was amended (nothing was pushed). 63 is 3 over the soft target; recorded here rather than silently accepted.

### Divergence from the PLAN's `<output>` block, on the launching agent's instruction

The PLAN's `<output>` says to commit the PLAN and SUMMARY together in a fourth
`docs(quick-260820-s2x): plan + summary` commit, and the executor's default flow updates
`STATE.md` and `ROADMAP.md`. The launching agent's constraints for this run explicitly override
both: **leave the SUMMARY uncommitted; do NOT update the STATE.md quick-task row or
ROADMAP.md.** Those instructions were followed, so this run has **three** commits and the
PLAN + SUMMARY remain untracked in the working tree. Flagged here so the difference is a
recorded decision rather than an omission.

### Not deviations

- No authentication gates were hit.
- The guard was NOT edited (`260819-u8d-placeholder-guard.sh` last changed in `e99e001`, yesterday). Guard and draft never disagreed, so the STOP condition never fired.
- A13's ordering-inversion STOP did not fire: 2x-max still sits above 3x-median.

## Known Stubs

None in the code sense. The six `<TO BE FILLED AT POSTING>` markers in the amendment's prepared
deviations block are deliberate and enumerated in §3/A18(ii) with the reason each is not
knowable before Carter posts; they sit BELOW the paste closer, so they cannot reach OSF from
this file.

## Threat Flags

None. No network endpoint, auth path, file-access pattern or schema at a trust boundary was
created or modified; every change is documentation under `.planning/`.

## Self-Check: PASSED

Files claimed, verified present on disk:

- `.planning/debug/260820-site-basis-sweep-results-as-received.md` — FOUND (54 lines)
- `.planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py` — FOUND (282 lines)
- `.planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-guard-transcript.txt` — FOUND (231 lines)
- `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md` — FOUND (440 lines, 31685 B)
- `.planning/debug/260820-COURIER-TO-SETH-instantiated-amendment.md` — FOUND (63 lines, 3212 B)

Commits claimed, verified in `git log`: `88899d6`, `e59af9f`, `13b4543` — all FOUND.

Counts in this SUMMARY were re-measured after it was written, and three were wrong on the
first pass (transcript length 186 -> **231**; "one green" -> **two**, because the POST-AUDIT
re-run adds a second `EXIT=0`; "four-section transcript" -> **five** sections). They are
corrected above. A count is a claim; this is the reconciliation.

`.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/osf_deviations.md` and
`.planning/amendments/osf_deviations.md`: byte-unchanged and unstaged. No `src/`, `tests/`,
`config/` or `Snakefile` path appears in any of the three commits. The guard script's last
commit is still `e99e001` (2026-08-19) — it was not edited.
