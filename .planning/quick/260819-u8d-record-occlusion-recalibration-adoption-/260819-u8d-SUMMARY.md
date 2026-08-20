---
phase: quick-260819-u8d
plan: 01
subsystem: pre-registration
tags: [osf, amendment, occlusion, clause-d, anomaly-gate, calibration, guard, placeholder-sentinel, m3-07]

requires:
  - phase: quick-260819 (fire-morning adjudication arc)
    provides: the 21-region row-basis sweep, the §5/§4 supplement, Seth's VERDICT and C1/C2/C3 convergence, PENDING PASTE #3
provides:
  - DEC-2026-08-19-occlusion-recalibration-adopted in .planning/DECISIONS.md (the branch adoption, five commitments, measured basis, unchanged-list)
  - two append-only HANDOFF gate-ledger clauses recording the new OSF obligation and the do-not-touch posture on _OCCLUSION_ANOMALY_FRACTION
  - a paste-ready, fully slot-sentinelled OSF amendment-update draft (uninstantiated by construction)
  - the separate §6 same-position collinearity note
  - 260819-u8d-placeholder-guard.sh + its seen-red/seen-green controls transcript
affects: [PENDING PASTE #3 instantiation, Seth brief-blind review of the amendment, the m3 AoU LD fire, OSF posting]

tech-stack:
  added: []
  patterns:
    - "Named slot sentinels + a SLOT_LEDGER: every unmeasured number is a grep-able double-brace token, and the ledger makes DELETING a slot (rather than filling it) detectable"
    - "Must-be-identity arithmetic verification instead of must-match counts (six derived identities, tolerance derived from print precision)"
    - "Count-identity verbatim-quote enforcement against a file:line source of truth, not a substring threshold"
    - "Vacuity floor first in every guard section (file bytes, marker count + order, paste-block bytes)"

key-files:
  created:
    - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md
    - .planning/amendments/note-same-position-collinearity-2026-08-19.md
    - .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
    - .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-guard-controls-transcript.txt
  modified:
    - .planning/DECISIONS.md
    - .planning/HANDOFF.json

key-decisions:
  - "CALIBRATION branch adopted; NORMALIZATION branch withdrawn (a .bim row is biallelic by construction, so same-position rows are the obligatory representation)"
  - "Anomaly gate re-defined on occluded SITES (representation-invariant); exclusion accounting stays on ROWS; both numbers reported"
  - "Ceiling = 3x the measured SITE-BASIS median, purpose-anchored, with an explicit never-calibrate-to-pass clause on the public record"
  - "Numbers instantiate ONCE from PENDING PASTE #3; the draft is basis-agnostic until then"
  - "The amendment is a corrected empirical claim (wrong by ~38x on frequency), posted as a NEW OSF file — never a silent swap"
  - "The §6 same-position collinearity caveat is recorded in its own note, not folded into the amendment"

patterns-established:
  - "An obligation with no failing check lapses silently: every drafting obligation here has a named enforcer that was seen red before its green was trusted"
  - "Fake-value control copies live in the scratchpad ONLY, carry a shouting banner, and the tracked tree is grepped for leaks"

requirements-completed: [DEC-2026-08-19-occlusion-recalibration-adopted]

duration: 16min
completed: 2026-08-19
---

# Quick 260819-u8d: Record the occlusion-recalibration adoption + draft the amendment package — Summary

**Carter's one-word adoption is now in the ledger with all five commitments, and the OSF correction exists as a paste-ready body in which every unmeasured number is a grep-able slot sentinel guarded by an enforcer observed red eight ways and green three — so the draft physically cannot reach OSF uninstantiated.**

## Performance

- **Duration:** ~16 min
- **Started:** 2026-08-20T02:19:40Z
- **Completed:** 2026-08-20T02:36:00Z (approx.)
- **Tasks:** 3 of 3
- **Files modified:** 6 committed (+1 uncommitted summary, by instruction)

## Accomplishments

- **The adoption is recorded where a future session will look for it.** `DEC-2026-08-19-occlusion-recalibration-adopted` carries Carter's verbatim `"adopt"` (21:45 EDT), the five adopted commitments, every measured literal with an explicit basis label, the §8 provenance, the `:45` false-sentence record, the enumerated unchanged-list, the honest n=21-of-276 limitation, and cross-refs to all five banked transcripts. No future session has to re-derive the adjudication from chat.
- **Both HANDOFF gate ledgers were extended append-only**, so the dated state of knowledge is preserved rather than overwritten: `gates.osf_pre_registration` now records a SECOND open OSF obligation (alongside the still-open Check-2 amendment-update, which it does not discharge), and `gates.producer_pre_fire_gates` records that `_OCCLUSION_ANOMALY_FRACTION` is row-basis, premise-dead, and NOT editable in code until the amendment is POSTED.
- **A complete paste-ready amendment package exists** — factual correction, corrected empirical claim, evidence, the recalibrated clause (d) with purpose/metric/accounting/ceiling/derivation/no-calibrate-to-pass/limitation, Seth's §8 verbatim, methods provenance, and an enumerated unchanged-list — plus the prepared `osf_deviations.md` entry marked NOT-YET-APPENDED, outside the paste markers.
- **The enforcer is real, not aspirational.** `260819-u8d-placeholder-guard.sh` fails today on the two sections it must fail on, and its every check has been observed failing on a deliberately broken input.

## Task Commits

1. **Task 1: Record the adoption — DECISIONS.md entry + HANDOFF.json gate notes** — `5b6779d` (docs)
2. **Task 2: Draft the amendment package + the separate §6 collinearity note** — `c5337d1` (docs)
3. **Task 3: Build the placeholder guard and prove it red before trusting it green** — `e99e001` (docs)

No plan-metadata commit was made: per the execution constraints this SUMMARY is left **uncommitted**, and `STATE.md` / `ROADMAP.md` were deliberately not touched.

## Files Created/Modified

- `.planning/DECISIONS.md` — appended `DEC-2026-08-19-occlusion-recalibration-adopted`; the prior 2,143 lines are byte-identical (verified by `startswith` against `HEAD~1`).
- `.planning/HANDOFF.json` — exactly two gate strings extended, each a strict prefix-extension; every other key deep-equal to the pre-edit copy; `json.dumps(indent=2, ensure_ascii=False)` still reproduces the file byte-exactly and there is still no trailing newline.
- `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md` — 411 lines / 28,342 B; one PASTE opener at line 100 before one closer at line 338; paste block ~16.3 KB; 13 slot sentinels; 13-line SLOT_LEDGER; `(site basis)` x5 and `(row basis)` x4 inside the block.
- `.planning/amendments/note-same-position-collinearity-2026-08-19.md` — 80 lines; the standalone §6 record (observation, measured scale, what it is NOT, the SuSiE near-collinearity consideration, RETAINED disposition, explicit NOT-POSTED status line).
- `.planning/quick/260819-u8d-.../260819-u8d-placeholder-guard.sh` — 319 lines; sections `draft | paste-ready | arith | quote | all`; vacuity floor first in every section; `arith` and `quote` as embedded `python3` blocks in the same file.
- `.planning/quick/260819-u8d-.../260819-u8d-guard-controls-transcript.txt` — 311 lines; verbatim command, output and exit code for all 11 controls.

## The red-then-green guard sequence — BOTH OBSERVED, not assumed

Against the **real, uninstantiated draft**:

| Section | Exit | State |
|---|---|---|
| `draft` | 0 | **GREEN** — the draft-state checks are satisfied by the artifact as committed |
| `quote` | 0 | **GREEN** — 4/4 non-blank source lines of Seth's §8 carried verbatim, by count identity |
| `paste-ready` | 1 | **RED** — 29 opening + 29 closing sentinel delimiters remain, basename still carries `XX`, and all 13 ledger lines fail their anchored filled-value patterns |
| `arith` | 1 | **RED, loudly** — "cannot verify — draft not instantiated", naming all 13 unfilled ledger values. It does not skip. |

Against a **fully instantiated control copy** (scratchpad only, shouting banner, arithmetically self-consistent invented values):

| Section | Exit | State |
|---|---|---|
| `paste-ready` | 0 | **GREEN** |
| `arith` | 0 | **GREEN** — all six identities hold and the ordering holds |

**Eight red controls and three green controls, every exit code measured by re-execution (not read off the transcript):**

- `R1` `paste-ready` on the real draft → 1. The headline red; the state the guard exists for.
- `R2` `arith` on the real draft → 1, with the explicit "cannot verify" message.
- `R3` `draft` and `paste-ready` on an EMPTY file → 1, 1. Vacuity floor fires.
- `R4` `draft` on a copy with the paste block gutted to 58 B (markers intact) → 1. An emptied block is not silently green.
- `R5` `paste-ready` on an instantiated copy with ONE slot DELETED rather than filled (`  SITE_MAX_PCT = ` left value-less) → 1, naming `SITE_MAX_PCT`. Deletion is not instantiation.
- `R6` `arith` on an instantiated copy with `CEILING_3X_MEDIAN_PCT` perturbed to 0.4500% → 1, naming BOTH broken identities (the ceiling and the margin ratio).
- `R7` `quote` on a copy with one word altered inside the §8 blockquote ("deepest" → "deeper") → 1, reporting count identity 3/4.
- `R8` `paste-ready` on the fully instantiated copy renamed so its basename still carries `XX` → 1. Instantiated content alone is not sufficient.
- `G1` `draft` on the real draft → 0. `G2` `quote` on the real draft → 0. `G3` `paste-ready` + `arith` on the instantiated copy → 0, 0.

A verification pass reconstructed all of these from scratch in a fresh temp directory and re-ran the guard against each, asserting both the exit codes and the specific failure MESSAGES (so a red for the wrong reason would have been caught). 13 executions, 13 matches.

## The 13-slot roster — instantiate from this table, do not re-derive it

**Class M — instantiated ONCE from PENDING PASTE #3 stdout (11 slots):**

| Slot | Source | Rendered form |
|---|---|---|
| `{{SITE_MIN_PCT}}` | sweep `SITE-BASIS SUMMARY … min=` | `0.1102%` |
| `{{SITE_MEDIAN_PCT}}` | sweep `… median=` | `0.1330%` |
| `{{SITE_MAX_PCT}}` | sweep `… max=` | `0.2500%` |
| `{{SITE_ROBUST_SIGMA_PCT}}` | sweep `robust_sigma(1.4826*MAD)=` | `0.0300%` |
| `{{MEAN_ROW_SITE_INFLATION}}` | sweep `mean row/site inflation` | `1.45x` |
| `{{MED_PLUS_3SIG_PCT}}` | DERIVED = median + 3·sigma | `0.2230%` |
| `{{MED_PLUS_4SIG_PCT}}` | DERIVED = median + 4·sigma | `0.2530%` |
| `{{TWO_X_MEDIAN_PCT}}` | DERIVED = 2·median | `0.2660%` |
| `{{TWO_X_MAX_PCT}}` | DERIVED = 2·max | `0.5000%` |
| `{{CEILING_3X_MEDIAN_PCT}}` | sweep `CANDIDATE CEILING …` = 3·median | `0.3990%` |
| `{{CEILING_MARGIN_X}}` | sweep `margin over observed site-basis max` | `1.60x` |

**Class P — instantiated at posting time by Carter (2 slots):** `{{POSTING_DATE}}` (`2026-08-21` shape), `{{PRE_EXECUTE_COMMIT}}` (7-40 hex chars).

The "rendered form" column shows **SHAPE ONLY**. Those digits are illustrative and are not values. The real values come from PENDING PASTE #3 and from nowhere else. Substitute each slot ONCE everywhere it occurs, including its SLOT_LEDGER line, then rename the file so its basename no longer contains `XX`.

## What is still open, and what discharges it

- **PENDING PASTE #3 (`.planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md`) is the SINGLE remaining input** before Seth's brief-blind review of this draft. It is a ~2-2.5 h read-only VM run; the VM must be STARTED first and STOPPED after; the harness cross-check (region 1 must reproduce `n_occluded_rows == 231` exactly) discards all results if it fails.
- **`paste-ready` AND `arith` must BOTH be GREEN before any OSF paste.** The exact invocation is recorded inside the amendment's own drafting notes:
  `bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all <amendment>`
- **`.planning/osf_deviations.md` is deliberately NOT appended.** It is byte-unchanged and was never staged. The prepared entry text lives inside the amendment file, below the closing paste marker, marked `⚠ NOT-YET-APPENDED`, with `<TO BE FILLED AT POSTING>` markers for the GUID, URL, timestamp and gate commit. **The event that discharges this: Carter posts the amendment to `osf.io/az52u` as a NEW supplementary file and has the file URL, GUID and authoritative UTC timestamp in hand.** Only then is the entry appended — and only then may `_OCCLUSION_ANOMALY_FRACTION` be changed in code.
- **`trsx5` must still show exactly 1 revision after posting.** The correction is a new dated record in the chain, never an in-place edit of a posted body.

## Deviations from Plan

**None on substance — the plan executed as written.** Three procedural notes:

1. **SUMMARY.md left uncommitted, by explicit instruction.** The plan's `files_modified` lists seven files and its verification block expects `git diff --name-only HEAD~3 HEAD` to show seven; it shows **six**, because this summary is deliberately untracked. `STATE.md` and `ROADMAP.md` were likewise deliberately not updated.
2. **`260819-u8d-PLAN.md` was not committed.** It is not in the plan's `files_modified`, and committing it would have added an eighth path to the diff the plan's own verification enumerates. It remains untracked for the orchestrator to handle.
3. **Task 3's verification was hardened beyond the plan's text** (per the execution constraints): rather than grepping the transcript for `R5`-`R8`/`G3` labels, a verification pass CONSTRUCTED every broken copy plus the fully instantiated copy from scratch in a fresh temp directory, re-ran the guard against each, and asserted both exit codes and the specific failure messages. No control is believed on transcript trust.

## Threat-model dispositions honoured

| Threat | How it was mitigated here |
|---|---|
| T-u8d-01 sentinels or `XX` filename reaching OSF | `paste-ready` observed RED on the real draft (R1) and on the XX-renamed instantiated copy (R8) |
| T-u8d-02 slot deleted rather than filled | SLOT_LEDGER + anchored patterns; observed RED (R5) |
| T-u8d-03 the §8 provenance softened in transit | `quote` count identity against verdict lines 102-107; observed RED on a one-word change (R7) |
| T-u8d-04 derived numbers hand-computed wrong | six must-be-identity relations; observed RED on a perturbed ceiling (R6) |
| T-u8d-05 control copy mistaken for the real draft | copies confined to the scratchpad with a shouting banner; the tracked `.planning` tree greps clean for the banner string |
| T-u8d-06 HANDOFF gate history overwritten | append-only string extension; prefix-preservation + deep-equality of every other key verified against a pre-edit copy |
| T-u8d-07 draft read as authorization to change code or contact OSF | DRAFT-ONLY banner at the top of the amendment; the producer-gate clause states the constant is not editable until POSTED; no `src/`, `tests/`, `config/`, `Snakefile` path appears in any of the three commits |
| T-u8d-09 a guard check made vacuous | vacuity floors first in every section; observed RED on an empty file (R3) and a gutted paste block (R4) |

## Self-Check: PASSED

All seven claimed paths exist on disk:

```
FOUND: .planning/DECISIONS.md
FOUND: .planning/HANDOFF.json
FOUND: .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md
FOUND: .planning/amendments/note-same-position-collinearity-2026-08-19.md
FOUND: .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
FOUND: .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-guard-controls-transcript.txt
FOUND: .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-SUMMARY.md
```

All three claimed commits exist in the object store: `5b6779d`, `c5337d1`, `e99e001`.

Plan-level verification, re-run after the last commit: `draft` exit 0, `quote` exit 0,
`paste-ready` exit 1, `arith` exit 1; HANDOFF round-trip `True` with no trailing newline;
`git diff --name-only HEAD~3 HEAD` lists exactly the six committed files and nothing else;
both `osf_deviations.md` files UNTOUCHED; the posted July amendment UNTOUCHED; no path under
`tests/`, `src/`, `config/`, `Snakefile`, `STATE.md` or `ROADMAP.md` in any of the three commits.
Nothing was pushed.
