---
phase: quick-260820-u6i
plan: 01
subsystem: pre-registration
tags: [osf, amendment, occlusion, clause-d, anomaly-gate, multiplicity, companion-gate, count-vs-fraction, guard, slot-instantiation, seth-attack, m3-07]
requires:
  - .planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md
  - .planning/debug/260820-site-basis-sweep-results-as-received.md
  - .planning/debug/260819-occ-measure-sweep-results-as-received.md
provides:
  - "21-slot revised occlusion-gate recalibration amendment, guard-GREEN, answering Seth's §2/§3/§4/§6"
  - "additions-only guard extension: 8 roster slots, one *_X pattern arm, three identities + an ordering check at TOL_X 0.01"
  - "instantiation engine modes: --dry-run, --second-pass (Class-M verify / Class-P force-substitute), --control-source"
  - "20-section guard transcript: 5 greens, 17 reds, completed 2x2 guard/document matrix"
  - "reply courier to Seth with post-commit byte anchors"
affects:
  - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  - .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
  - .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
tech-stack:
  added: []
  patterns:
    - "pre-registered rendered-string expectations as a substitute for reconciliation when a statistic has no printed upstream aggregate"
    - "Class-M (measured, drift-abort) vs Class-P (argv-sourced, force-substituted) slot classes"
    - "additions-only enforcer extension, MEASURED by `git diff --numstat` deletions == 0 on a single-file commit"
key-files:
  created:
    - .planning/quick/260820-u6i-revise-the-instantiated-amendment-per-se/260820-u6i-guard-transcript.txt
    - .planning/debug/260820-COURIER-TO-SETH-revision-reply.md
  modified:
    - .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
    - .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
    - .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py
    - .planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md
decisions:
  - "INFLATION_ROBUST_SIGMA slot renamed INFLATION_ROBUST_SIGMA_X and rendered at 4 dp"
  - "collinearity note split home: SUBSTANCE inside the paste block, repo PATH in the internal deviations block only"
  - "0.5664% (row basis) deliberately NOT converted to a slot"
  - "PRE_EXECUTE_COMMIT ADVANCED 8638ed3 -> 2689cae under reading (b), at both occurrences"
  - "ragged line wrapping left as-is rather than re-opening the byte anchors for a cosmetic fix"
metrics:
  duration: "~35 min"
  completed: 2026-08-20
---

# quick-260820-u6i: Revise the Instantiated Amendment per Seth's Attack — Summary

Closed all four of Seth's work items and machine-checked every new claim: 1.18x is now named a
COUNT ratio that does not convert between the two percentages (the measured fraction ratio is
1.12x, with the `fraction ratio = count ratio x (n_sites/n_rows)` mechanism), the permissiveness
comparison is pre-empted row-against-row, clause (d) became a disjunction with a 3.42x
multiplicity companion ceiling (3 x the measured median 1.14x, 1.91x margin over the observed
1.79x), and the collinearity note has a checkable home. The guard grew from 13 to 21 slots
strictly additively — its commit's `git diff --numstat` deletions field is literally `0` — with
each new identity seen RED in isolation before its green was trusted.

## What was executed

| Task | Commit | Contents |
|---|---|---|
| 1a — guard extension | `9a9f51f` | 8 roster slots by `ROSTER+=`, one `*_X)` pattern arm, three identities + an ordering check at `TOL_X = 0.01`, header CHANGELOG. **Guard-only commit; deletions field `0`.** |
| 1b — engine + attack + transcript | `2689cae` | `SOURCE_ROW`, companion column statistics, `EXPECTED_RENDER`, `--dry-run` / `--second-pass` / `--control-source`; Seth's attack banked as the sixth supporting record; 17 controls transcribed. |
| 2 — amendment revision | `b4263e7` | 24 register edits, `--second-pass` re-instantiation, census, 2x2 matrix completed. |
| 3 — reply courier | `a364d19` | 49-line courier with post-commit anchors and the advanced/superseded gate hashes. |

Measured start state (all as pre-registered in the PLAN, re-measured before any edit):
`PRE = 154de167a025ebb2c347b564c5970e3d63e76ca5`; amendment 31,685 B /
`b8f9a978c9bdbc7892f97b5d90cf9d27`; 13 ledger-pattern lines; `0.1888` at lines 199, 271, 424;
`guard all` EXIT=0; the attack record untracked. `SCRATCH` =
`…/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/u6i`. `PRE_REV` (HEAD before any Task 2 edit)
= `2689cae0c0c0666012bf451fcdd10924661bcf02`.

> **Note on `PRE` vs the PLAN's "HEAD f47d9a5".** `f47d9a5` was HEAD when the plan was *written*;
> two commits landed on top of it before execution — the plan itself (`9371278`) and its own
> revision 1/2 (`154de16`). The amendment blob, its byte anchors, its ledger-line count and its
> `0.1888` line numbers were all re-measured and matched the PLAN exactly, so nothing about the
> artifact under revision had moved. `PRE` is therefore `154de16`, and that is the tree MATRIX-A
> reads the pre-extension guard from.

## Byte anchors

| | Bytes | md5 |
|---|---|---|
| Before this task | 31,685 | `b8f9a978c9bdbc7892f97b5d90cf9d27` |
| After (committed `b4263e7`) | 42,213 | `e1b4a11d18ad2907af4f0a93fd5747d2` |

## Decisions recorded, with rationale

**1. `INFLATION_ROBUST_SIGMA` → `INFLATION_ROBUST_SIGMA_X`, rendered at 4 dp.** The brief named
the slot without the `_X` suffix. It carries the suffix so a SINGLE new `*_X)` arm in the guard's
filled-value dispatch covers all six inflation/ratio slots — which is what keeps the extension to
one inserted arm and keeps the fail-closed `*)` arm ("no filled-value pattern defined for $s")
intact, so a future slot with an unrecognised suffix still FAILS rather than passing silently.
The 4 dp render is the one deviation from the engine's `%.2fx`: at 2 dp the value 0.089 collapses
to `0.09x` and the quantity is destroyed. The guard's `*_X` pattern `[0-9]+\.[0-9]+x` accepts both
widths, so this needed no guard special case.

**2. The collinearity note's SPLIT home.** Its substance is inside the paste block (a new
*Limitation — near-collinearity at same-position rows* paragraph); its exact repo path lives
ONLY in the NOT-YET-APPENDED deviations block, below the paste closer. Rationale: a posted OSF
record must be self-contained — a public reader cannot resolve `.planning/…`, and the note itself
declares "INTERNAL RECORD. NOT part of any OSF amendment and NOT posted". The verify asserts both
directions: the path is present below the closer and ABSENT anywhere at or above it.

**3. `0.5664% (row basis)` deliberately NOT converted to a slot.** It is pre-existing, was audited
at s2x A15, is arithmetically transparent (3 x 0.1888 = 0.5664 exactly), sits in the census ROW
set with its label, and every added slot enlarges the roster the guard must carry. Decision
recorded; slot not added. (The same reasoning kept `0.1685%` a literal in the new §2 sentence,
where the PLAN's R7 text writes it as one.)

**4. Class-P force-substitution outcome — `PRE_EXECUTE_COMMIT` ADVANCED.**
`8638ed37c1431ea73566fd03ad1541ba95416fe4` (`8638ed3`) →
`2689cae0c0c0666012bf451fcdd10924661bcf02` (`2689cae`). This is not a choice this task made: the
pre-paste row's own standing instruction is "RE-CONFIRMED AT POSTING: re-read HEAD, confirm no
`_OCCLUSION_ANOMALY_FRACTION` or gate-constant change has landed since, and update this value if
the branch has advanced." The branch HAS advanced (Task 1 landed two commits), so the row
instructs exactly this update; pinning the stale hash would leave the gate commit pointing at a
tree that predates the guard and engine this revision depends on. Both occurrences (the
SLOT_LEDGER line and the pre-paste table row) moved together **by construction** — force
substitution is document-wide — and the verify asserts the new hash occurs exactly twice, the
superseded literal zero times, and `POSTING_DATE`'s `2026-08-21` exactly three times. The prose
was updated to follow the number (R17a/R17b), and the RE-CONFIRMED-AT-POSTING sentence was kept
verbatim, because that sentence is the standing authority for the advance.

**5. Ragged line wrapping left as-is (deferred, cosmetic).** Substituting a `{{SLOT}}` sentinel
with a shorter rendered value leaves some source lines short of the 90-column fill. Markdown
reflows soft-wrapped paragraphs, so the OSF-rendered output is byte-for-byte unaffected.
Re-wrapping would move the file's bytes AFTER the courier's `wc -c`/`md5sum` anchors were
computed and committed, forcing a re-open of two commits for zero rendered difference. Declined:
a cosmetic fix is not a licence to re-open a freeze.

## Execution notes (two, both recorded rather than hidden)

**A. Composite `--second-pass` modes.** The PLAN's Step 2 expects the 11 pre-existing Class-M
slots to report `VERIFIED-IN-PLACE` and the 8 new slots `SUBSTITUTED`. Three pre-existing Class-M
slots (`MEAN_ROW_SITE_INFLATION`, `CEILING_3X_MEDIAN_PCT`, `CEILING_MARGIN_X`) legitimately do
BOTH: their ledger lines already carry filled values (verified byte-identical against the freshly
computed values, drift-abort armed) AND the register's new prose introduced fresh sentinels for
them (R7, R8, R4, R9). The engine therefore reports them as `VERIFIED-IN-PLACE+SUBSTITUTED`,
which is strictly stronger than either alone: all 11 pre-existing Class-M values were drift-verified,
and none moved. See the ledger below.

**B. `2026-08-20` occurrence count is checked DYNAMICALLY, never against a hard-coded 3.** The
PLAN's S7 pre-registered `PRE_EXECUTE_COMMIT` 2 / `2026-08-21` 3 / `2026-08-20` 3 as a
START-OF-TASK sanity check — all three were confirmed on the live file before any edit. R1's own
revision note then legitimately adds a fourth `2026-08-20`. The engine's Class-P guard asserts the
probe's count is unchanged **across the same replace operation** (observed: `4 → 4` for both
Class-P slots), which is the invariant that actually matters; a hard-coded 3 would have aborted
the mode on prose this same task was required to add.

## Scope discipline

No OSF contact. Nothing posted, nothing fired. `_OCCLUSION_ANOMALY_FRACTION` is still
`0.0005` at `src/python/run_native_ld_panel.py:133` and no file under `src/`, `tests/`, `config/`
or `Snakefile` was modified or staged. `.planning/osf_deviations.md`, `.planning/STATE.md`,
`.planning/ROADMAP.md` and `.planning/amendments/note-same-position-collinearity-2026-08-19.md`
are byte-unchanged. The DRAFT-NOT-POSTED banner is intact. All four commits touch `.planning/`
only. No scratch banner ("FAKE NUMBERS…" / "GUARD FIXTURE…") appears on the first line of any
tracked file; all 12 control copies, the 21-slot fixture and the pre-extension-guard OLDROOT live
in the session scratchpad.

## Deviations from plan

None beyond the two execution notes above, both of which are refinements the PLAN's own CHECKER
ADVISORY anticipated (note B) or that follow necessarily from the register's own edits (note A).
No Rule 1-4 deviation was triggered; no auto-fix was required.

---

<!-- APPENDICES BELOW ARE MACHINE-EMITTED VERBATIM — do not retype -->

## Appendix 1 — REVISION REGISTER (all 17 items dispositioned; 24 edits)

Line numbers are as-of-edit, in the file state each edit was applied to. Every item is
CHANGED; none STANDS and none hit STOP. Numbers entered ONLY as `{{SLOT}}` sentinels —
no number was hand-typed into the amendment at any point.

| Item | Line | Verdict | What moved |
|---|---|---|---|
| R1 | 23 | CHANGED | revision note + Seth's status line verbatim (his line 104) |
| R2 | 58 | CHANGED | third change named |
| R3 | 129 | CHANGED | five -> six, attack record named |
| R4 | 396 | CHANGED | both conditions named; single-metric reading closed off |
| R5 | 82 | CHANGED | 8 sentinel ledger lines after CEILING_MARGIN_X, Class-P last; 21 total |
| R6a | 102 | CHANGED | eleven -> nineteen |
| R6b | 111 | CHANGED | companion derivations added to the formula block |
| R6c | 122 | CHANGED | column-statistic + second-source + pre-registered-render provenance |
| R6d | 138 | CHANGED | 4-dp render exception recorded; the 0.1234% census exemption is untouched |
| R17a | 63 | CHANGED | prose follows the number under reading (b); the RE-CONFIRMED sentence is kept verbatim |
| R17b | 139 | CHANGED | instantiation-record item 4 follows the same reading |
| R16 | 177 | CHANGED | companion named; UNCHANGED enumeration intact |
| R7 | 188 | CHANGED | 1.18x named a COUNT ratio, non-converting, with the measured fraction ratio + mechanism |
| R14a | 262 | CHANGED | occurrence 1 of 3 -> sentinel |
| R14b | 334 | CHANGED | occurrence 2 of 3 -> sentinel; 0.5664% deliberately NOT slotted (see SUMMARY) |
| R8 | 308 | CHANGED | three per-region quantities + mean-vs-median disambiguation |
| R9 | 319 | CHANGED | gate stated as a disjunction; pseudo-code indented 4 spaces (see T-u6i-07) |
| R10 | 332 | CHANGED | new sub-paragraph between *Ceiling.* and *Derivation...* |
| R11 | 395 | CHANGED | Seth's §3 pre-emption, row against row, '0.5%' not '0.5000%' |
| R12 | 407 | CHANGED | n=21 caveat extended to both ceilings; collinearity caveat by SUBSTANCE (path stays internal) |
| R15 | 478 | CHANGED | no fourth branch, stated explicitly |
| R13a | 561 | CHANGED | occurrence 3 of 3 -> sentinel (R14 (iii)) |
| R13b | 565 | CHANGED | RECALIBRATES bullet extended with the companion condition and its measured basis |
| R13c | 581 | CHANGED | collinearity note given its specific, checkable home — path INTERNAL only |

### Verbatim BEFORE / AFTER for every CHANGED item

#### R1 — line 23 — revision note + Seth's status line verbatim (his line 104)

BEFORE:

```
> `.planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-guard-controls-transcript.txt`.

# OSF Amendment-Update
```

AFTER:

```
> `.planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-guard-controls-transcript.txt`.

> **REVISION — 2026-08-20.** The body below was REVISED after instantiation, against the
> adversarial attack banked at
> `.planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md`. Four passages
> moved: the basis-conventions paragraph, the no-calibrate-to-pass paragraph, the clause-(d)
> ceiling (which gained a companion condition), and the limitation paragraph. The revised
> body was re-instantiated by the SAME engine in `--second-pass` mode — every number below
> still entered by script from a banked record and none was hand-typed — and re-verified by
> the extended enforcer, whose green and whose sixteen reds are transcribed verbatim in
> `.planning/quick/260820-u6i-revise-the-instantiated-amendment-per-se/260820-u6i-guard-transcript.txt`.
> The s2x transcript referenced above is RETAINED: it is the history of the FIRST
> instantiation, not a stale claim about this one.
> Status line for the record, in the reviewer's own words:
> measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires

# OSF Amendment-Update
```

#### R2 — line 58 — third change named

BEFORE:

```
and its ceiling (0.0005 of rows → 3x the measured site-basis median). |
```

AFTER:

```
and its ceiling (0.0005 of rows → 3x the measured site-basis median); (3) the clause-(d) gate gains a COMPANION condition on the occluded-site row/site inflation ratio, so a region that is anomalous in multiplicity alone is no longer invisible to it. |
```

#### R3 — line 129 — five -> six, attack record named

BEFORE:

```
3. Confirm the five supporting records are committed: the two Seth transcripts, the 21-region
   sweep, the §5/§4 supplement, and the site-basis sweep results.
```

AFTER:

```
3. Confirm the six supporting records are committed: the two Seth transcripts, the 21-region
   sweep, the §5/§4 supplement, the site-basis sweep results, and the banked attack on the
   instantiated draft
   (`.planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md`).
```

#### R4 — line 396 — both conditions named; single-metric reading closed off

BEFORE:

```
6. ONLY THEN may `_OCCLUSION_ANOMALY_FRACTION` be changed in code, and only to the
   site-basis metric and ceiling pre-registered above.
```

AFTER:

```
6. ONLY THEN may `_OCCLUSION_ANOMALY_FRACTION` be changed in code, and only to the
   TWO-CONDITION gate pre-registered above: BOTH the site-basis metric with its
   {{CEILING_3X_MEDIAN_PCT}} ceiling AND the companion condition on the occluded-site
   row/site inflation ratio at {{INFLATION_CEILING_3X_X}}. Shipping the site-basis condition
   alone is NOT authorised by this amendment — that is the single-metric gate this
   revision replaced, and it is multiplicity-blind.
```

#### R5 — line 82 — 8 sentinel ledger lines after CEILING_MARGIN_X, Class-P last; 21 total

BEFORE:

```
  CEILING_MARGIN_X = 1.87x
  POSTING_DATE = 2026-08-21
```

AFTER:

```
  CEILING_MARGIN_X = 1.87x
  ROW_MEDIAN_PCT = {{ROW_MEDIAN_PCT}}
  FRACTION_RATIO_X = {{FRACTION_RATIO_X}}
  INFLATION_MIN_X = {{INFLATION_MIN_X}}
  INFLATION_MEDIAN_X = {{INFLATION_MEDIAN_X}}
  INFLATION_MAX_X = {{INFLATION_MAX_X}}
  INFLATION_ROBUST_SIGMA_X = {{INFLATION_ROBUST_SIGMA_X}}
  INFLATION_CEILING_3X_X = {{INFLATION_CEILING_3X_X}}
  INFLATION_MARGIN_X = {{INFLATION_MARGIN_X}}
  POSTING_DATE = 2026-08-21
```

#### R6a — line 102 — eleven -> nineteen

BEFORE:

```
2. The eleven Class-M values were read off that banked record BY SCRIPT. Seven came directly
   from the printed `SITE-BASIS SUMMARY`, `CANDIDATE CEILING`, `margin over observed
   site-basis max` and `mean row/site inflation` lines; four were DERIVED by these formulas:
```

AFTER:

```
2. The nineteen Class-M values were read off the banked records BY SCRIPT. Seven came
   directly from the printed `SITE-BASIS SUMMARY`, `CANDIDATE CEILING`, `margin over
   observed site-basis max` and `mean row/site inflation` lines; the rest were DERIVED, or
   computed as column statistics, by these formulas:
```

#### R6b — line 111 — companion derivations added to the formula block

BEFORE:

```
TWO_X_MAX_PCT         = 2 * SITE_MAX_PCT
```
```

AFTER:

```
TWO_X_MAX_PCT         = 2 * SITE_MAX_PCT
INFLATION_CEILING_3X_X = 3 * INFLATION_MEDIAN_X
INFLATION_MARGIN_X     = INFLATION_CEILING_3X_X / INFLATION_MAX_X
FRACTION_RATIO_X       = ROW_MEDIAN_PCT / SITE_MEDIAN_PCT
```
```

#### R6c — line 122 — column-statistic + second-source + pre-registered-render provenance

BEFORE:

```
   it by 0.0001 percentage points, inside the guard's tolerance.
3. Each Class-M slot
```

AFTER:

```
   it by 0.0001 percentage points, inside the guard's tolerance.

   `INFLATION_MIN_X`, `INFLATION_MEDIAN_X`, `INFLATION_MAX_X` and `INFLATION_ROBUST_SIGMA_X`
   (1.4826 x MAD) are computed by the same script from that banked table's OWN eighth
   column, the per-region row/site inflation at occluded sites. `ROW_MEDIAN_PCT` comes from
   the SECOND banked record — the row-basis sweep at
   `.planning/debug/260819-occ-measure-sweep-results-as-received.md` — whose printed summary
   is itself reconciled against that file's own 21 per-region fractions before anything is
   written, on the same principle. Those four column statistics have NO printed upstream
   aggregate to reconcile against, so they are checked instead against PRE-REGISTERED
   RENDERED STRINGS, fixed in the revising task's plan before the code that computes them
   was written — a must-be-identity string comparison, chosen deliberately over a
   must-be-close numeric one.
3. Each Class-M slot
```

#### R6d — line 138 — 4-dp render exception recorded; the 0.1234% census exemption is untouched

BEFORE:

```
as `0.1234%`; the two ratio slots render as `1.23x`.
```

AFTER:

```
as `0.1234%`; ratio slots render as `1.23x`, with one deliberate exception — `INFLATION_ROBUST_SIGMA_X` renders at FOUR decimals, because at two its value collapses to `0.09x` and the quantity is destroyed.
```

#### R17a — line 63 — prose follows the number under reading (b); the RE-CONFIRMED sentence is kept verbatim

BEFORE:

```
| Pre-execute commit gate | `8638ed37c1431ea73566fd03ad1541ba95416fe4` — the HEAD of `m3-W2-aou-deltas` at INSTANTIATION time, captured before the first commit of the instantiating task. RE-CONFIRMED AT POSTING:
```

AFTER:

```
| Pre-execute commit gate | `8638ed37c1431ea73566fd03ad1541ba95416fe4` — the HEAD of `m3-W2-aou-deltas` captured before the first commit of the REVISING task. It SUPERSEDED the first instantiation's value when the branch advanced, on the standing authority of the next sentence. RE-CONFIRMED AT POSTING:
```

#### R17b — line 139 — instantiation-record item 4 follows the same reading

BEFORE:

```
4. The two Class-P slots were filled at instantiation, not at posting: `POSTING_DATE`
   provisionally, and `PRE_EXECUTE_COMMIT` as the full 40-hex HEAD captured before the
   instantiating task's first commit. Both are re-confirmed at posting.
```

AFTER:

```
4. The two Class-P slots are argv-sourced rather than measured, and are DEFINED to move:
   `POSTING_DATE` is provisional, and `PRE_EXECUTE_COMMIT` is the full 40-hex HEAD captured
   before the REVISING task's first commit — it advanced from the first instantiation's
   value when the branch advanced, which is exactly what the pre-paste table's standing
   RE-CONFIRMED-AT-POSTING instruction requires. Both are re-confirmed at posting. The
   re-instantiation engine force-substitutes them at EVERY occurrence, so the SLOT_LEDGER
   line and the pre-paste table row cannot drift apart.
```

#### R16 — line 177 — companion named; UNCHANGED enumeration intact

BEFORE:

```
occluded variant is treated moves; what moves is the numerical gate that decides when a
region's occlusion count is anomalous, and one factual sentence that was wrong.
```

AFTER:

```
occluded variant is treated moves; what moves is the numerical gate that decides when a
region's occlusion count is anomalous — its metric, its ceiling, and the addition of a
companion condition on occluded-site multiplicity, so the gate is not blind to a region that
excludes a pathological number of rows at an ordinary number of sites — and one factual
sentence that was wrong.
```

#### R7 — line 188 — 1.18x named a COUNT ratio, non-converting, with the measured fraction ratio + mechanism

BEFORE:

```
k same-position rows, so row-basis counts exceed site-basis counts by a
representation-dependent factor — measured here as 1.18x on average across the sample. Every
percentage in this document carries its basis label explicitly. Mixing them is the single
easiest way to misread this amendment.
```

AFTER:

```
k same-position rows, so row-basis COUNTS exceed site-basis COUNTS.

The measured size of that excess is {{MEAN_ROW_SITE_INFLATION}}: the mean across the sample
of occluded ROWS divided by occluded SITES. It is a COUNT ratio and nothing else. **It does
NOT convert between the two percentages.** Both fractions carry denominators that also
differ — a region's `n_rows` exceeds its `n_sites` — so applying a count ratio to a fraction
OVERSHOOTS. The measured ratio of the two medians is {{FRACTION_RATIO_X}}: row-basis median
{{ROW_MEDIAN_PCT}} (row basis) over site-basis median 0.1685% (site basis). The mechanism is
one line —

    fraction ratio = count ratio x (n_sites / n_rows)

— and in region 1, n_rows / n_sites = 102,421 / 96,708 = 1.059. Asserting the count ratio of
a fraction is a quantity measured on one object asserted about another: the same defect class
as the error this amendment corrects, and it is fixed here rather than left for a reader to
trip over.

The standing practice removes the need to convert at all: every percentage in this document
carries its basis label explicitly, and both figures are restated wherever both matter.
Mixing them is the single easiest way to misread this amendment.
```

#### R14a — line 262 — occurrence 1 of 3 -> sentinel

BEFORE:

```
*The measured distribution (row basis).* min **0.1323%**, median **0.1888%**, max **0.3527%**,
```

AFTER:

```
*The measured distribution (row basis).* min **0.1323%**, median **{{ROW_MEDIAN_PCT}}**, max **0.3527%**,
```

#### R14b — line 334 — occurrence 2 of 3 -> sentinel; 0.5664% deliberately NOT slotted (see SUMMARY)

BEFORE:

```
0.1888% = **0.5664% (row basis)**
```

AFTER:

```
{{ROW_MEDIAN_PCT}} = **0.5664% (row basis)**
```

#### R8 — line 308 — three per-region quantities + mean-vs-median disambiguation

BEFORE:

```
manifest's audit purpose. **Both numbers are reported for every region**, together with the
measured mean row/site inflation of 1.18x across the sample.
```

AFTER:

```
manifest's audit purpose. **Three numbers are reported for every region**: its occluded-SITE
fraction (site basis), its occluded-ROW count (row basis), and that region's OWN row/site
inflation at occluded sites — the third being the quantity the companion condition below
tests.

Mean and median are different anchors here, and the distinction is worth stating outright.
The SAMPLE MEAN inflation across the 21 sampled regions is {{MEAN_ROW_SITE_INFLATION}}, and
that is the reported summary figure. The companion gate is NOT anchored on it. The gate's
anchor is the MEDIAN, {{INFLATION_MEDIAN_X}}, chosen because the site-fraction ceiling is
anchored on a median too and the two ceilings must be derived by the same rule.
```

#### R9 — line 319 — gate stated as a disjunction; pseudo-code indented 4 spaces (see T-u6i-07)

BEFORE:

```
*Ceiling.* `n_occluded_sites <= 0.5056% x n_sites` — that is, **3x the measured site-basis
median** of 0.1685% (site basis), or 0.005056 expressed as a bare fraction, since the
withdrawn ceiling was written as a fraction and this one is written as a percentage. It
gives 1.87x margin over the observed site-basis maximum of 0.2698% (site basis). The
measured site-basis minimum is 0.1345% (site basis) and the robust sigma is 0.0274% (site
basis).
```

AFTER:

```
*Ceiling.* A region is DEFERRED when EITHER condition holds:

    (i)   n_occluded_sites  >  {{CEILING_3X_MEDIAN_PCT}} x n_sites
    (ii)  n_occluded_rows / n_occluded_sites  >  {{INFLATION_CEILING_3X_X}}

Condition (i) is the site-fraction ceiling: `n_occluded_sites <= 0.5056% x n_sites` — that
is, **3x the measured site-basis median** of 0.1685% (site basis), or 0.005056 expressed as
a bare fraction, since the withdrawn ceiling was written as a fraction and this one is
written as a percentage. It gives {{CEILING_MARGIN_X}} margin over the observed site-basis
maximum of 0.2698% (site basis). The measured site-basis minimum is 0.1345% (site basis) and
the robust sigma is 0.0274% (site basis). Condition (ii) is the companion condition on
multiplicity, derived by the same rule and stated in full immediately below.
```

#### R10 — line 332 — new sub-paragraph between *Ceiling.* and *Derivation...*

BEFORE:

```
*Derivation, including what was rejected and why.*
```

AFTER:

```
*Companion condition on multiplicity (why a site gate needs one).* Site basis was chosen
BECAUSE it is multiplicity-invariant — a row-basis gate fires differently on identical
biology depending only on how the caller split multiallelics. But invariance cuts both ways:
invariant means BLIND. A region can sit at a perfectly normal site-basis rate while excluding
a pathological number of rows.

The illustration, with both bases labelled. A region occluding approximately 0.17% of its
sites (site basis) — near the measured median — whose occluded sites happen to sit at the
observed maximum multiplicity of 21 would exclude approximately 3.4% of its rows (row basis),
and would sail through a site-only gate reading an entirely ordinary number. A region whose
occluded sites are systematically high-multiplicity IS a representation anomaly, which is
precisely the class clause (d) exists to catch.

The companion ceiling is derived by the SAME rule as the main one. Across the 21 sampled
regions the measured row/site inflation at occluded sites is min {{INFLATION_MIN_X}}, median
{{INFLATION_MEDIAN_X}}, max {{INFLATION_MAX_X}}, robust sigma (1.4826 x MAD)
{{INFLATION_ROBUST_SIGMA_X}}. The companion ceiling is three times the MEDIAN,
{{INFLATION_CEILING_3X_X}} — anchored on a location statistic rather than on a sample edge,
exactly as the site-fraction ceiling is — leaving {{INFLATION_MARGIN_X}} margin over the
observed maximum.

No-calibrate-to-pass applies to the companion in full. The multiplier was fixed by the rule,
not chosen for what it clears. That the companion also defers 0 of the 21 sampled regions is
a CONSEQUENCE of the derivation and is stated here as one; it was not a reason for the
multiplier and was not used as one. Re-widening the companion ceiling in response to a firing
region is prohibited without a further amendment, exactly as for the site-fraction ceiling.

Provenance, stated plainly rather than buried: this blind spot was raised by the project's
external methodological reviewer, as a correction to his OWN earlier recommendation of the
site-basis metric. It is closed here rather than disclosed as a limitation, because a
disclosed blind spot still ships a detector that cannot see the anomaly class it exists to
catch.

*Derivation, including what was rejected and why.*
```

#### R11 — line 395 — Seth's §3 pre-emption, row against row, '0.5%' not '0.5000%'

BEFORE:

```
investigated, not the gate widened. Re-widening this ceiling in response to a firing region
is prohibited without a further amendment.
```

AFTER:

```
investigated, not the gate widened. Re-widening this ceiling in response to a firing region
is prohibited without a further amendment.

Note, before a reader finds it: the adopted ceiling is numerically slightly MORE permissive
than the rejected 10x-withdrawn candidate. Compared row against row, the adopted ceiling's
row-basis restatement is 0.5664% (row basis) against 0.5% of rows (row basis) for 10x the
withdrawn constant. The objection to 8x and 10x is not that they are too loose; it is that
they would have been SELECTED for clearing the sample. The adopted value being more
permissive while still rejecting them is exactly the point: the derivation is independent of
what passes.
```

#### R12 — line 407 — n=21 caveat extended to both ceilings; collinearity caveat by SUBSTANCE (path stays internal)

BEFORE:

```
systematic-by-span and the distribution is flat across size classes, but the upper tail is
unmeasured. A full 276-region sweep is approximately 39 hours of virtual-machine time (8.6
minutes per region, measured) and is deliberately NOT spent ahead of this amendment. Every
region computes its own occlusion count during the production run, so the complete
distribution folds in at closeout and is reported there against this ceiling.
```

AFTER:

```
systematic-by-span and the distribution is flat across size classes, but the upper tail is
unmeasured. That caveat applies to BOTH conditions: the inflation distribution behind the
companion ceiling was measured on the same 21 regions, and its upper tail is likewise
unmeasured. A full 276-region sweep is approximately 39 hours of virtual-machine time (8.6
minutes per region, measured) and is deliberately NOT spent ahead of this amendment. Every
region computes its own occlusion count AND its own occluded-site inflation during the
production run, so both complete distributions fold in at closeout and are reported there
against both conditions.

*Limitation — near-collinearity at same-position rows.* Fine-mapping at multiallelic sites
carries near-collinear predictors. A `.bim` row is biallelic by construction, so one
k-allelic site renders as k same-position rows whose dosages are structurally
anti-correlated; this is a known property of split-multiallelic representation, not a defect
of this pipeline. A credible set whose members share a `(CHR, POS)` should therefore be read
as ONE site with unresolved allele identity, not as k independent signals. The caveat is
recorded as a separate dated methods note in the project record and is carried into the
manuscript's limitations.
```

#### R15 — line 478 — no fourth branch, stated explicitly

BEFORE:

```
- **The three pre-registered outcome branches**, reproduced unchanged:
  BRANCH_AFR_OCC_NONE, BRANCH_AFR_OCC_EXCLUDED, BRANCH_AFR_OCC_DEFERRED.
```

AFTER:

```
- **The three pre-registered outcome branches**, reproduced unchanged:
  BRANCH_AFR_OCC_NONE, BRANCH_AFR_OCC_EXCLUDED, BRANCH_AFR_OCC_DEFERRED. The companion
  condition introduces NO fourth branch and NO new token: a region deferred by EITHER the
  site-fraction ceiling or the multiplicity companion routes to the SAME
  `BRANCH_AFR_OCC_DEFERRED`, and the defer-not-exclude protocol is untouched.
```

#### R13a — line 561 — occurrence 3 of 3 -> sentinel (R14 (iii))

BEFORE:

```
  systematic-by-span 21-region sample, row basis min 0.1323% / median 0.1888% / max 0.3527%
```

AFTER:

```
  systematic-by-span 21-region sample, row basis min 0.1323% / median {{ROW_MEDIAN_PCT}} / max 0.3527%
```

#### R13b — line 565 — RECALIBRATES bullet extended with the companion condition and its measured basis

BEFORE:

```
  basis), 1.87x the observed site-basis maximum. Provenance of the withdrawn constant
```

AFTER:

```
  basis), 1.87x the observed site-basis maximum. The gate ALSO gains a COMPANION condition
  on the occluded-site row/site inflation ratio, because a site-basis metric is
  multiplicity-invariant and therefore multiplicity-BLIND: measured across the same 21
  regions, inflation min {{INFLATION_MIN_X}} / median {{INFLATION_MEDIAN_X}} / max
  {{INFLATION_MAX_X}} / robust sigma {{INFLATION_ROBUST_SIGMA_X}}; companion ceiling = 3x the
  median = {{INFLATION_CEILING_3X_X}}, leaving {{INFLATION_MARGIN_X}} margin over the observed
  maximum. A region deferring on EITHER condition routes to the same BRANCH_AFR_OCC_DEFERRED
  token — no fourth branch. Provenance of the withdrawn constant
```

#### R13c — line 581 — collinearity note given its specific, checkable home — path INTERNAL only

BEFORE:

```
- **Amends:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) via osf.io/az52u file trsx5.
```

AFTER:

```
- **Known limitation recorded alongside:** same-position collinearity caveat recorded at
  .planning/amendments/note-same-position-collinearity-2026-08-19.md; fine-mapping at
  multiallelic sites carries near-collinear predictors; known split-representation property,
  not a defect. That note is an INTERNAL RECORD — not part of any OSF amendment and not
  posted. Its SUBSTANCE is disclosed inside the posted text's limitation paragraph; only its
  repo PATH lives here, because a posted OSF record must be self-contained and a public
  reader cannot resolve a `.planning/` path.
- **Amends:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) via osf.io/az52u file trsx5.
```

## Appendix 2 — `--second-pass` SUBSTITUTION LEDGER (stdout, verbatim)

Command:

```
python3 .planning/quick/260820-s2x-instantiate-the-occlusion-recalibration-/260820-s2x-instantiate.py \
        --second-pass \
        .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
        --pre-execute-commit 2689cae0c0c0666012bf451fcdd10924661bcf02 --posting-date 2026-08-21
```

EXIT=0. 11 Class-M `VERIFIED-IN-PLACE`, 8 new `SUBSTITUTED`, 2 Class-P
`FORCE-SUBSTITUTED (argv)`; 33 sentinel substitutions == pre-count `{{`=33 == `}}`=33;
post-count 0/0.

```
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
CLASS-M DRIFT VERIFY: OK — 11 already-filled measured value(s) unmoved

CLASS-P FORCE-SUBSTITUTION — argv-sourced slots, replaced at EVERY occurrence (they are DEFINED to move; the pre-paste table commits to re-confirming both at posting)
  FORCE-SUBSTITUTED POSTING_DATE         2026-08-21 -> 2026-08-21  (3 occurrence(s); '2026-08-20' count 4 unchanged across the replace)
  FORCE-SUBSTITUTED PRE_EXECUTE_COMMIT   8638ed3… -> 2689cae…  (2 occurrence(s); '2026-08-20' count 4 unchanged across the replace)

SUBSTITUTION LEDGER — .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  SLOT                     | VALUE                                      | OCCURRENCES | SOURCE
  SITE_MIN_PCT             | 0.1345%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  SITE_MEDIAN_PCT          | 0.1685%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  SITE_MAX_PCT             | 0.2698%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  SITE_ROBUST_SIGMA_PCT    | 0.0274%                                    |           0 | parsed (site sweep) [VERIFIED-IN-PLACE]
  MEAN_ROW_SITE_INFLATION  | 1.18x                                      |           2 | parsed (site sweep) [VERIFIED-IN-PLACE+SUBSTITUTED]
  MED_PLUS_3SIG_PCT        | 0.2507%                                    |           0 | derived [VERIFIED-IN-PLACE]
  MED_PLUS_4SIG_PCT        | 0.2781%                                    |           0 | derived [VERIFIED-IN-PLACE]
  TWO_X_MEDIAN_PCT         | 0.3370%                                    |           0 | derived [VERIFIED-IN-PLACE]
  TWO_X_MAX_PCT            | 0.5396%                                    |           0 | derived [VERIFIED-IN-PLACE]
  CEILING_3X_MEDIAN_PCT    | 0.5056%                                    |           2 | parsed (site sweep) [VERIFIED-IN-PLACE+SUBSTITUTED]
  CEILING_MARGIN_X         | 1.87x                                      |           1 | parsed (site sweep) [VERIFIED-IN-PLACE+SUBSTITUTED]
  ROW_MEDIAN_PCT           | 0.1888%                                    |           5 | parsed (row sweep) [SUBSTITUTED]
  FRACTION_RATIO_X         | 1.12x                                      |           2 | derived (cross-basis) [SUBSTITUTED]
  INFLATION_MIN_X          | 1.04x                                      |           3 | column stat (site sweep) [SUBSTITUTED]
  INFLATION_MEDIAN_X       | 1.14x                                      |           4 | column stat (site sweep) [SUBSTITUTED]
  INFLATION_MAX_X          | 1.79x                                      |           3 | column stat (site sweep) [SUBSTITUTED]
  INFLATION_ROBUST_SIGMA_X | 0.0890x                                    |           3 | column stat (site sweep) [SUBSTITUTED]
  INFLATION_CEILING_3X_X   | 3.42x                                      |           5 | derived [SUBSTITUTED]
  INFLATION_MARGIN_X       | 1.91x                                      |           3 | derived [SUBSTITUTED]
  POSTING_DATE             | 2026-08-21                                 |           0 | argv [FORCE-SUBSTITUTED (argv)]
  PRE_EXECUTE_COMMIT       | 2689cae0c0c0666012bf451fcdd10924661bcf02   |           0 | argv [FORCE-SUBSTITUTED (argv)]
  TOTALS                   | 21 slots                                   |          33 | pre-count '{{'=33 '}}'=33, post-count 0/0
EXIT=0
```

## Appendix 3 — the additions-only evidence (verbatim)

`git diff --numstat 9a9f51f^ 9a9f51f -- <guard>`:

```
64	0	.planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh
```

Added 64, **deleted 0**. The commit contains exactly one file (the guard). `TOL_RATIO = 0.02`
and the fail-closed `*)` arm are both still present, asserted by the verify block.

## Appendix 4 — the control table (20 sections, 5 greens / 17 reds)

| Section | Exit | Signature string observed (verbatim; the load-bearing one where a section has several) |
|---|---|---|
| `DRY-RUN` | EXIT=0 | `PRE-REGISTERED EXPECTATIONS: OK — all 8 rendered strings byte-identical` |
| `G-NEW` | EXIT=0 | `GUARD all: GREEN` |
| `MATRIX-A` | EXIT=0 | `GUARD all: GREEN` |
| `NC-0` | EXIT=1 | `draft: roster name absent from file: INFLATION_MIN_X` (x8) + `draft: SLOT_LEDGER carries 13 ledger lines, want 21` |
| `NC-A` | EXIT=1 | `INFLATION_CEILING_3X_X == 3*INFLATION_MEDIAN_X BROKEN` |
| `NC-B` | EXIT=1 | `INFLATION_MARGIN_X == INFLATION_CEILING_3X_X / INFLATION_MAX_X BROKEN` |
| `NC-C` | EXIT=1 | `FRACTION_RATIO_X == ROW_MEDIAN_PCT / SITE_MEDIAN_PCT BROKEN` |
| `NC-D` | EXIT=1 | `inflation ordering BROKEN` |
| `NC-E` | EXIT=1 | `paste-ready: ledger line INFLATION_CEILING_3X_X does not match its filled-value pattern` |
| `NC-F` | EXIT=1/EXIT=1 | `draft: SLOT_LEDGER carries 20 ledger lines, want 21` (draft) + `paste-ready: ledger line FRACTION_RATIO_X does not match its filled-value pattern` |
| `NC-G` | EXIT=1 | `PRE-REGISTERED EXPECTATION FAILED for INFLATION_MIN_X` |
| `REG-1` | EXIT=1/EXIT=1 | `paste-ready: basename still carries the XX date placeholder: osf-amendment-occlusion-gate-recalibration-2026-08-XX.md` + (arith) `SLOT_LEDGER is missing lines: …` — KNOWN CHANGE |
| `REG-2` | EXIT=1 | `TWO_X_MAX_PCT == 2*SITE_MAX_PCT BROKEN` **and** `CEILING_MARGIN_X == CEILING_3X_MEDIAN_PCT / SITE_MAX_PCT BROKEN` — both s2x NC-2 signatures reproduced |
| `REG-3` | EXIT=1 | `paste-ready: ledger line SITE_MIN_PCT does not match its filled-value pattern` |
| `REG-4` | EXIT=1 | `vacuity: file under byte floor (0 B < 6000 B): /gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/u6i/reg_4_empty.md` |
| `REG-5` | EXIT=1 | `vacuity: PASTE opener occurs 0 time(s), want exactly 1` |
| `REG-6` | EXIT=1 | `quote: source line NOT carried verbatim: 'measured : 231 per 102,421 = 0.2255%    -> premise low by` |
| `SECOND-PASS` | EXIT=0 | `PRE-REGISTERED EXPECTATIONS: OK — all 8 rendered strings byte-identical` |
| `MATRIX-B` | EXIT=1 | `draft: SLOT_LEDGER carries 21 ledger lines, want 13` |
| `MATRIX-C` | EXIT=0 | `GUARD all: GREEN` |

### The two EXPECTED, DOCUMENTED behaviour changes — neither hidden, neither "fixed"

1. **REG-2 and REG-3 are REBASED onto the 21-slot fixture**, not run against the tracked
   13-slot file. Against the extended guard a 13-slot file fails `arith` at
   `SLOT_LEDGER is missing lines: INFLATION_MIN_X, …` and exits BEFORE the identity checks, so
   the s2x NC-2/NC-3 signatures could not have appeared at all. Rebasing is what makes
   "identical behaviour" a meaningful claim rather than a coincidence. Both original signature
   strings reproduce exactly against the extended guard.
2. **REG-1's `arith` MESSAGE changed** from `cannot verify — draft not instantiated` to
   `SLOT_LEDGER is missing lines: INFLATION_MIN_X, INFLATION_MEDIAN_X, INFLATION_MAX_X,
   INFLATION_ROBUST_SIGMA_X, INFLATION_CEILING_3X_X, INFLATION_MARGIN_X, FRACTION_RATIO_X,
   ROW_MEDIAN_PCT` — a 13-slot file is missing 8 roster lines before it can be judged
   uninstantiated. Same exit code (1), different message. Recorded as a KNOWN CHANGE.

### Isolation of the new checks

- **NC-A** breaks only `INFLATION_CEILING_3X_X == 3*INFLATION_MEDIAN_X`; the ordering check
  still PASSES (`inflation ordering holds (min 1.04x <= median 1.50x <= max 1.79x)`).
- **NC-D** breaks only the ordering (no identity uses the minimum).
- **NC-E** and **REG-3** each produce EXACTLY ONE `does not match its filled-value pattern`
  failure, which is what proves the new `*_X)` arm is load-bearing rather than decorative.
- **NC-F** trips `draft: SLOT_LEDGER carries 20 ledger lines, want 21` — the roster growth is
  load-bearing through `sec_draft`'s EXISTING count check, with no edit to `sec_draft`.
- **NC-G** perturbs one inflation cell (1.04 → 1.02) chosen so the sample MEAN moves by
  0.02/21 = 0.00095, INSIDE `TOL_RECON_INFL` (0.005): `reconcile()` still passes, so the
  PRE-REGISTERED RENDER expectation is unambiguously the check that fires, and exactly one
  expectation breaks (`computed 1.02x, expected 1.04x`).

## Appendix 5 — the completed 2x2 guard/document matrix

|  | PRE-REVISION file (13 slots) | REVISED file (21 slots) |
|---|---|---|
| **PRE-EXTENSION guard** (`git show 154de16:<guard>`) | **GREEN** — MATRIX-A | **RED** — MATRIX-B (`draft: SLOT_LEDGER carries 21 ledger lines, want 13`) |
| **EXTENDED guard** (`9a9f51f`) | **RED** — NC-0 (`draft: roster name absent from file: INFLATION_MIN_X`, …) | **GREEN** — MATRIX-C |

Only the diagonal is green, which is the correct shape: each enforcer blesses only the document
generation it was written for. MATRIX-B's red is load-bearing — it proves the stale 13-slot guard
CANNOT bless the revised document, so a future session cannot validate this file with the wrong
enforcer. The brief's phrase "the pre-revision version still GREEN too" is true ONLY under the
PRE-EXTENSION guard; under the extended guard the pre-revision file is correctly RED, and that
red is NC-0.

## Appendix 6 — census output (verbatim, exit 0)

```
SITE seen: ['0.0274%', '0.1345%', '0.1685%', '0.2507%', '0.2698%', '0.2781%', '0.3370%', '0.5056%', '0.5396%']
ROW seen: ['0.0059%', '0.0393%', '0.1323%', '0.1888%', '0.2255%', '0.3527%', '0.5664%']
EXEMPT seen: ['0.0068%', '0.1234%']
CENSUS OK — exemption set unchanged at 2 literals; 7 new x-literals present
```

The 4-decimal EXEMPTION SET is byte-identical to the s2x register and was NOT grown by this
task: exactly `{0.0068%, 0.1234%}`. The seven new literals end in `x`, not `%`, so the census
regex `\d+\.\d{4}%` never sees them. §3 writes `0.5%` (never `0.5000%`) and the §4b
illustration is at 2 dp (`approximately 0.17%` / `approximately 3.4%`). Both forbidden strings —
`0.1988%` (Seth's wrong-answer demo) and `1.42x` (his superseded run-collapse estimate) — are
ABSENT from the amendment.

## Appendix 7 — closing status line, verbatim

measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires

## Self-Check: PASSED

All seven artifacts exist on disk and all four commits (`9a9f51f`, `2689cae`, `b4263e7`, `a364d19`) resolve in `git log --all`. Transcript 894 lines (min 200); courier 49 lines (cap 50).
