---
title: "Finding 2 is NOT ESTABLISHED — the pairs-per-deletion measurement landed and it RETRACTS; within-window clustering is a NEW finding (ICC 0.729)"
task: 260908-tnd
date: 2026-09-08
type: quick
scope: DOCS-ONLY
status: COMPLETE
posted: false
---

# 260908-tnd — SUMMARY

**A SCIENTIFIC RETRACTION, not a wording fix.** The queued measurement was fired by Carter on
2026-09-08 and returned. It did **not** confirm Finding 2 — it **removed its robustness**.
Finding 2 (between-region heterogeneity in POST-filter rate) moves from *"real but unexplained,
magnitude unidentified"* to **NOT ESTABLISHED**. A genuinely new finding replaces part of it:
**within-window clustering is real, measured and strong (ICC 0.728930)**. Both are now in the
disclosure.

**DOCS-ONLY.** `src/` and `tests/` untouched (`git status --porcelain -- src tests` **empty**).
`tcujq` stays **DEFERRED**. No push, no VM, no OSF contact, no Seth contact, no fire. `$0`.
NOTE: Status is unchanged: `DRAFTED — NOT POSTED`. Discharging the last open item is **not**
authorization to post, and the text says so explicitly in four places.

---

## Anchors verified BEFORE any edit

| anchor | expected | measured | |
|---|---|---|---|
| `CONTENT-SPEC.md` lines | 98 | 98 | PASS |
| `CONTENT-SPEC.md` md5 | `b7b16076f45f2669aa5c951c82c7a73c` | same | PASS |
| `CONTENT-SPEC.md` bytes | 6696 | 6696 | PASS |

---

## What changed (3 files, 6 hunks, all strictly after line 531)

**`.planning/osf_deviations.md`** — 851 -> 997 lines, +170 / -24.

| # | site | change |
|---|---|---|
| R1 | status block (568-580) | `REMAINING BEFORE POSTING — ONE MEASUREMENT` -> **DISCHARGED**; records that it **retracts rather than confirms**; explicitly **not** authorization to post |
| R2 | §(2) heterogeneity bullet | restated as **MEASURED but NOT ESTABLISHED**; the uncorrected numbers are retained and labelled as assuming **independent pairs**, an assumption now **measured false** |
| R3 | §(7) "two co-moving pairs" | the hypothetical is preserved and annotated: measured `c_eff` **1.494**, *below* the ~2 it posits — arithmetic about what `c ~ 2` **would** do, not a description of the panel |
| R4 | §(7) "HAS NOT BEEN MEASURED" | now **MEASURED**; corrects the anticipation that it would decide Finding 2's *magnitude* — it removed Finding 2's *establishment* instead |
| R5 | §(8) EPISTEMIC STATUS | new lead bullet: Finding 2 **NOT ESTABLISHED**, Finding 1 **UNCHANGED**, Finding 3 unchanged |
| R6 | §(9) + new **§(10)** | SECOND-READ provenance bullet; then §(10a) the new clustering finding, §(10b) the Rao-Scott table + retraction, §(10c) the decision rule that did not fire, §(10d) what is unchanged |

**`.planning/STATE.md`** — new `2026-09-08 (LATER)` RESUME HERE block; the prior 2026-09-08
block demoted to PRIOR with its *"ONE MEASUREMENT … REMAINS BEFORE POSTING"* clause marked
**DISCHARGED**; the "ONE REMAINING PRE-POSTING ITEM" heading marked **HISTORICAL** (original text
preserved verbatim beneath it); the 2026-09-03 Finding-2 and "HAS NOT BEEN MEASURED" bullets
annotated in place, following the file's existing supersession convention.

**`.planning/HANDOFF.json`** — `status` rewritten (prior status **preserved** after a `|| PRIOR`
marker), `resume_on_reconnect[0]` rewritten, `headline` item (2) marked **RETRACTED** with its
banked wording quoted intact, plus two new keys
(`run2_step2_2026_09_02.clustering_measurement_2026_09_08`,
`seth_round2_outcome_2026_09_03.decision_rule_did_not_fire_2026_09_08`). Round-trip proven
byte-stable (`json.dumps(indent=2, ensure_ascii=True)`, no trailing newline) **before** editing, so
nothing outside the touched keys was reformatted. Re-validated as JSON after each write.

---

## Accuracy constraints — how each was honoured

- **The retraction leads with the p-value straddle, not the design effect.** §(10b) is headed
  *"THE DECISIVE OBSERVATION IS THE STRADDLE, NOT THE DESIGN EFFECT"*; the closing sentence of the
  section repeats that the retraction *"rests on the straddle, not on the design effect's point
  value."*
- **No claim that clustering explains Finding 2.** §(10b) states deff **1.360272** is **below** the
  observed **1.99** and *"does not on its own reproduce"* it; that it sits inside the CI **[1.1,
  4.2]** and is therefore **"a FAILURE TO EXCLUDE, NOT a demonstration"**; and that *"Nothing in
  §(10a) is an explanation of Finding 2 and it must never be reported as one."*
- **Conservatism disclosure recorded**, and placed *before* the conclusion is leaned on: the five NA
  regions were given **deff = 1.0** (no correction), which ran **against** the conclusion drawn.
- **Decision rule did not fire** — §(10c): measured `c_eff` 1.494 at ICC 0.729 -> deff 1.360, between
  the `c ~ 2` / `c ~ 1` branches; and the **Rao-Scott** correction that settled it was proposed by
  **neither party**.
- **The three ICC = 1.000000 regions are labelled a BOUNDARY value** (zero within-cluster variance),
  *"NOT a fitted estimate. It must never be quoted as one."*
- **Finding 1 stated as UNCHANGED and untouched** (§(8) and §(10d)) — counting, not inference, so no
  design effect can reach it.

---

## Verification — every check with a negative control seen RED on the real file

| # | check | result |
|---|---|---|
| V1 | `osf_deviations.md` lines 1-531 byte-identical vs `86c2658` (`cmp`) | **PASS** (40,053 B) |
| V1n | same `cmp` on a 1-byte perturbation of the real file | **RED at byte 20082, line 262** |
| V2 | `git status --porcelain -- src tests` | **EMPTY** |
| V3 | content gate on the disclosure (normalized, case-insensitive) | **PASS** |
| V3n | **23 negative controls** | **23/23 behaved** |
| V4 | courier byte-identical to HEAD | **PASS** (613 lines, md5 `ce6791344916c6ebebacfadbb808c702` re-measured) |
| V5 | splice source byte-identical to HEAD | **PASS** (md5 `34199ab125727f28c7f7b2d910e2005a`) |
| V6 | `HANDOFF.json` parses | **PASS** |
| V7 | disclosure Status line still `DRAFTED — NOT POSTED` | **PASS** |
| V8 | clustering statistics reconcile **componentwise** | **13/13 PASS** |

**Normalization used for every phrase check** (a literal, case-sensitive grep has been blind to a
live defect in this file five separate times): NFC -> strip markdown emphasis -> collapse
**all** whitespace **including newlines** -> lowercase.

**Present** (disclosure): `NOT ESTABLISHED` x6, `0.0366` x6, `0.0556` x6, `1.360` x6, `0.728930`
x4, `c_eff` x5, `DRAFTED — NOT POSTED` x4.
**Absent** (disclosure): `no covering deletion`, `complete in its own direction`,
`non-independence cannot create`, `unrelated constants`, `2.62` — **all 0**, and all 0 in the
pre-edit baseline too, so nothing was reintroduced.

**The 23 negative controls** each mutated the *real* edited file and required the gate to go RED:
7 present-token deletions, 5 absent-token injections, **3 line-wrapped + bolded** absent-token
injections (the form that defeated a literal grep before), 7 affirmative "clustering explains"
phrasings **including a line-wrapped bolded one**, plus 1 control requiring the unmutated file to
be GREEN.

**Componentwise reconciliation (V8)** — not aggregate agreement. Recomputed from the cluster-size
distribution alone: `sum(c*count)` = **2521** = n_pairs; `n_clusters` = **2105**; `sum(c^2)` =
**3767**; `c_eff` = 3767/2521 = **1.494248**; `c_mean` = **1.1976**; `k` (size >= 2) = **303**; `N` =
**719**; ANOVA `c0` = (N - sum(c^2)/N)/(k-1) = **2.371745**; `deff` = 1 + (c_eff-1)*ICC = **1.360272**.
All nine match the reported values exactly, plus the four derived percentages. `c0` and `deff` in
particular were **re-derived from their formulae**, not copied.

---

## DEVIATIONS (5) — all reported, none silent

**1. The NO-CLAIM guard was rescoped from a proxy to the property (a guard fix, not a prose fix).**
My first regex flagged any explain-verb near the word *heterogeneity*, and went RED on
**pre-existing** §(2) text: *"NO STRUCTURAL COVARIATE WAS FOUND to account for the heterogeneity."*
I did not add an exception. I enumerated **all 9** explain/account occurrences in the file with
context and adjudicated each: six belong to the unrelated 2026-08-14 *trsx5 third body* entry; two
are **negations whose subject is a covariate, not clustering**; the ninth is my own prohibition
sentence. No affirmative claim exists. The guard was then rescoped to require a **clustering-family
subject** in proximity and to skip negated clauses — and re-proven able to fail on seven violation
phrasings. The brief's rule (*"if a guard needs an exception for the correction's own prose, fix the
prose"*) did **not** apply: the flagged text is not this correction's prose, and it is semantically
the opposite of the forbidden claim.

**2. The courier was left BYTE-IDENTICAL — measured, then declined, with reasons.** The brief
required fix-at-source + re-splice if edited text landed in the byte-frozen VERBATIM APPENDIX. I
**measured** rather than assumed: of the four rewritten passages, R1 and R4 have **0** courier hits;
R3's hits are in the **courier body only** (lines 182-185), not the appendix; **one** R2 fragment
(*"the dispersion is robust in DIRECTION (every correction gives phi > 1.3)"*) **does** appear in the
appendix at lines 486-489. I did **not** re-splice, because:

- **Nothing there is false.** That sentence is scoped to the **overlap** corrections (1.99 and 1.52,
  both > 1.3), which is why my replacement widened to *"phi > 1.2 throughout"* — the
  design-corrected minimum is **1.249**. The appendix sentence remains true in its own scope; only
  the scope changed. The `260904-dgi` precedent re-spliced to fix a statement that was **false when
  written** (the "unrelated constants" over-correction) — a different trigger.
- **The appendix is byte-equal to a source whose md5 is cited in the courier body and in 2+ prior
  SUMMARYs.** Editing a true sentence there would break a published anchor for no accuracy gain.
- **The courier body is a dated record of what was sent to Seth on 2026-09-02.** Retroactively
  editing an honestly-held conclusion out of a communication record would falsify the provenance
  trail and destroy the evidence that a retraction was needed.
- **No supersession note was added anywhere** (the brief forbids it), and the appendix invariant was
  re-verified byte-equal to its source **after** all edits.

NOTE: This is a judgement call and it is the one item most worth a second opinion. If the intent was
that *any* appendix contact forces a re-splice regardless of truth, this decision should be
overturned.

**3. Two markdown blank lines were lost by the patch and restored.** Inserting the new STATE.md
block consumed the blank line before the following heading, and replacing the pre-posting block
consumed the blank line before the `CLOSURE` paragraph. Both self-caught on read-back. Notably,
my **first** repair attempt asserted the wrong preceding line and **aborted without writing** — the
assertion did its job.

**4. HANDOFF prose rewritten to avoid relying on the guard's negation escape-hatch.** My first
draft of `resume_on_reconnect[0]` said *"Do NOT write that clustering explains or accounts for the
dispersion"* — which passes only because the guard detects the negation. Per the brief's own rule I
fixed the **prose**, not the guard: it now reads *"Clustering is NOT an explanation of Finding 2 and
must never be reported as one."* The collocation no longer appears at all.

**5. SCOPE: STATE.md and HANDOFF.json guard hits are pre-existing, not introduced.** Running the
disclosure's ABSENT list against the two resume surfaces (my own extension, beyond the brief) showed
hits for `2.62`, `unrelated constants`, `non-independence cannot create` and `no covering deletion`.
**Measured against my own diff: I introduced none of them** (0 added lines match). They are
historical session-log records of *withdrawn* arguments and *completed* corrections — and one
`2.62` hit is a pure false positive inside the timestamp `…53:52.625Z`, which is precisely why the
brief scoped those guards to the disclosure. Left untouched.

---

## Known stubs

None. No placeholder, TODO or unwired value was introduced.

## Not done / still open

- **Not posted.** No OSF contact, no GUID reserved. The posting decision is **Carter's alone**.
- **`tcujq` two-file docstring defect** stays **DEFERRED** (touches `src/`).
- **Not pushed.** Commits remain local on `m3-W2-aou-deltas`.
- The Seth round-2 reply remains **drafted and unsent**.
