---
task: 260904-dgi
title: Correct the tail disclosure after a 5-reviewer adversarial review — 5 blockers + 6 highs, fixed at source and re-spliced
mode: quick
type: execute
branch: m3-W2-aou-deltas
date: 2026-09-04
docs_only: true
pushed: false
status: COMPLETE
banked:
  - "every mk7ze citation now names the POSTED line (posted = repo draft − 167, PROVEN against the posted body's own md5), with the repo-draft line carried alongside"
  - "the registered prediction is SAMPLE-SCOPED — it was falsified by data we already held (STATE.md:287 + m2_region_00057's +1)"
  - "the dispersion refutation is NARROWED — within-window clustering CAN create dispersion, and the pairs-per-deletion distribution is UNMEASURED, so Finding 2's magnitude is NOT yet attributable"
  - "the bare 1.99x now carries its CI and the drop-both-chr15 estimate 1.52 (p 0.073, not significant)"
  - "the window-level leave-one-out is replaced by a parent-level LOO (1.52-2.49, worst p 0.073)"
  - "the negative result becomes an UNDERPOWERED NULL; our own absence-of-evidence inversion is recorded against us"
  - "every Spearman CI is Bonett-Wright AND names its convention inline — the numbers alone were never the bug"
  - "the disclosure is still DRAFTED — NOT POSTED"
deviations:
  - "F-6a — CONTENT-SPEC A7/A8 are WRONG on three Fisher-z CIs and were deliberately NOT copied (recorded, not silent)"
  - "F-10 — the one supplied digit that did not reproduce was CONFIRMED BY MEASUREMENT against a one-digit instruction; the measurement won"
  - "F-7 / C6 — planner-added scope (live-state files), executed, plus TWO sites beyond the plan's enumeration found by the guard"
  - "the F-6 PENDING placeholder was never written — the checkpoint was resolved before execution reached it"
affects: [osf-preregistration, seth-consultation, m3-afr-ld-panel, pcs-sweep]
---

# quick-260904-dgi — Correct the tail disclosure after a 5-reviewer adversarial review

**One-liner:** A 5-reviewer adversarial review found 5 blocker-level and 6 high-level false or
overclaimed statements in a publication-bound disclosure; all are corrected in the disclosure, the
courier record and the live-state files, with the courier's byte-frozen appendix fixed **at source
and re-spliced** rather than masked. **Nothing was posted. No OSF contact, no Seth contact, no VM,
`$0`.**

---

## 1. STOP GATE — every anchor matched (Task 1)

| file | expected md5 | measured | lines/bytes |
|---|---|---|---|
| `260904-dgi/CONTENT-SPEC.md` | `f9ef450f…` | ✅ exact | 230 / 15524 |
| `.planning/osf_deviations.md` | `beb34d0b…` | ✅ exact | 669 |
| `260902-vsp/CONTENT-SPEC.md` (splice source) | `619426a0…` | ✅ exact | 173 / 11747 |
| courier record | `c8525e26…` | ✅ exact | 542 / 34644 |
| `.planning/HANDOFF.json` | `124beac3…` | ✅ exact | 226 |
| `.planning/STATE.md` | `2b05879b…` | ✅ exact | 3122 |
| **frozen prefix** `head -531 osf_deviations.md` | `c46967d9…` | ✅ exact | 40053 B |

**F-0 posted-line map re-proven in the executor's own shell, not taken from the plan:**
`sed -n '168,500p'` of the amendment reproduces mk7ze's posted md5
`13a49f543cabcc27ce9f1e589783c060`, **333 lines / 22,945 B**. Repo file is 598 lines, line 1 reads
`DRAFT — NOT POSTED`, paste boundary at repo `:501`. **Posted = repo draft − 167.** Every A1/A9/A10/
A12/B1 cited line was additionally spot-read and matched.

---

## 2. ⛔ F-1 — THE NORMALIZER, MEASURED BEFORE **AND** AFTER

This is the discipline the task exists to demonstrate. Two live false claims score **ABSENT** to a
literal grep in the exact files they had to be removed from.

**BEFORE any edit (unedited tree):**

| pattern | literal `grep -i` | normalized |
|---|---|---|
| `complete in its own direction` in `osf_deviations.md` | **0** | **1** ✅ (line-wrapped at `:573-574`) |
| `non-independence cannot create` in the courier | **0** | **1** ✅ (markdown-bolded at `:167`) |

Full normalized census on the unedited tree: **31 banned hits** across the five-file set, matching
the plan's F-4/F-5/F-7 measurements exactly (osf `line 467` ×1 / `line 275` ×2; HANDOFF `line 275`
×1; STATE `line 275` ×3).

**AFTER all edits, re-run against the `*.negctl.*` copies** — because *a normalizer that has
silently stopped matching is indistinguishable from a real fix*:

- literal grep on the originals: still **0 / 0** (the trap is still live)
- normalized census on the originals: **31 hits, identical to the before reading** ✅
- `guard.py` exit status on the negctl set: **1 (RED)** ✅

⇒ The green on the real tree is a real fix, not a broken guard.

**Implementation note.** `guard.py` calls `sys.exit()` at module level, so importing it to reuse
`norm()` would terminate the caller. The reuse helpers load it with `compile()`/`exec()` on source
**read at call time**, which also sidesteps the `.pyc`-staleness trap: the single `norm()` used by
every check is the guard's own, never a retyped copy.

---

## 3. RECORDED DEVIATION — the spec is WRONG on three CIs and was NOT copied (F-6 / F-6a / F-6b)

Hard constraint 4 says copy from the spec. **For these three intervals the spec is superseded and
was deliberately not copied. This is a recorded deviation, not a silent substitution.**

**The conflict.** CONTENT-SPEC A7 (`:108`) quoted `rho +0.004` as `[-0.428, +0.435]` while
asserting in the same clause *"|rho| up to 0.446 is INSIDE this CI"*. `0.446 > 0.435`. Measured
diagnosis: the interval is **Fisher-z** (`SE = 1/sqrt(n-3)`, the Pearson formula) and `0.446` is
**Bonett-Wright** (`SE = 1.03/sqrt(n-3)`). One sentence, two conventions.

**Adjudication (Carter, 2026-09-04): BONETT-WRIGHT throughout** — these are rank correlations,
plain Fisher-z is the Pearson formula, Bonett-Wright is the standard Spearman interval, and it is
the **WIDER** one: the conservative direction for a correction whose subject is overclaiming.

| rho | ⛔ CONTENT-SPEC (Fisher-z, WRONG) | ✅ USED (Bonett-Wright) |
|---|---|---|
| `+0.004` | `[-0.428, +0.435]` | **`[-0.440, +0.446]`** |
| `+0.173` | `[-0.280, +0.563]` | **`[-0.292, +0.572]`** |
| `-0.199` | `[-0.581, +0.255]` | **`[-0.590, +0.267]`** |
| `-0.201` | `[-0.59, +0.27]` | **`[-0.591, +0.266]`** |

**All four were re-derived independently in this session** under
`tanh(atanh(rho) ± 1.96·1.03/sqrt(18))` and reproduce exactly at 3dp. The Fisher-z contrast was
also computed and reproduces the spec's three wrong values exactly — confirming the diagnosis
rather than assuming it. **They are used because they were independently checked, not because they
were supplied.**

⚠ Because the interval **widens**, *"|rho| up to 0.446 is inside this CI"* is now **CORRECT** and
was retained. The clause that exposed the conflict turned out to be the surviving-correct half.

**F-6b — naming the convention is the actual fix.** Every Spearman CI in the disclosure and the
courier now carries *"95% CI, Fisher z with the Bonett-Wright Spearman standard error
1.03/sqrt(n-3)"* inline, enforced by presence guard **G-15**. An unnamed convention is what let two
of them into one sentence; a referee can now reproduce every interval.

### F-10 — the one open digit: **resolved by MEASUREMENT against a one-digit instruction**

The adjudication supplied `+0.268` for the `rho -0.199` upper bound. Measured:

```
tanh(atanh(-0.199) + 1.96*1.03/sqrt(18)) = 0.26747718   ->  3dp = 0.267
```

`0.26747718 < 0.2675`, so it rounds to **`0.267`**, and the statistical audit independently
reported `0.267`. Carter re-derived it in-session, confirmed **option-267**, and recorded that his
`+0.268` was a transcription slip on his part rather than a convention difference.

**Recorded as instructed: the checkpoint was resolved by MEASUREMENT against a one-digit
instruction, and the measurement won.** Stopping on one digit was correct — the artifact is
publication-bound and its subject is overclaiming. *(Memory precedent: "a count is a claim — scope
it and reconcile it"; the arithmetic reconciliation is exactly what should run before freezing a
number.)*

⚠ **Deviation from the plan's mechanics:** because the checkpoint was resolved **before** execution
reached Task 2, the literal `F-6 PENDING` placeholder was **never written**; the confirmed value
was written directly. G-13 (`F-6 PENDING` = 0 everywhere) is therefore satisfied **by
construction** rather than by a fill step. Its negative control was still run and observed RED.

---

## 4. What was corrected

### PART A — the disclosure (`.planning/osf_deviations.md`, entry now at `:532-EOF`)

| id | correction |
|---|---|
| **A1** ⛔ | Every mk7ze citation was a **repo-draft** line of a 598-line DRAFT file. `line 275`→**108**, `clause (a) at line 467`→**300** (which **does not exist** in 333 lines), `598-line`→**333-line**. Both forms now cited. The sweep's *conclusion* was unaffected (zero over a superset implies zero over the subset) — but the sentence stated a false fact about what was posted. |
| **A2** ⛔ | The registered prediction was **falsified by data we already held**: `m2_region_00057`'s **+1** and our own `STATE.md:287`. Now explicitly **SAMPLE-SCOPED**, naming the known out-of-sample counterexample; production tests both sides. |
| **A3** ⛔ | *"non-independence cannot create dispersion"* is **FALSE**. The 0.98 simulation tested **BETWEEN**-window duplication, which provably cannot inflate `E[chi2/dof]`. **WITHIN**-window clustering can and does; two co-moving pairs per occluding deletion reproduces 1.99 exactly at **zero** heterogeneity. The pairs-per-deletion distribution **has not been measured** ⇒ magnitude **not yet attributable**. The *"stronger than an unexamined null"* claim is **deleted**, not softened. |
| **A4** ⛔ | Bare `1.99x` → **1.99x (95% CI ~1.1-4.2; chi2 37.78, dof 19, p 6.3e-3)**, plus the drop-both-chr15 estimate **1.52 (p 0.073)** — robust in DIRECTION, poorly determined in MAGNITUDE, significance **not** robust to the overlap correction. |
| **A5** ⛔ | Window-level LOO **cannot** remove parent `00060` (its two chr15 windows shield each other) and its minimum **is** the headline. Replaced by leave-one-**PARENT**-out over 19 parents: **1.52-2.49, worst p 0.073** — non-significant at worst case. |
| **A6** ⛔ | Own-direction completeness **withdrawn as overclaimed from n=1**, citing the scanner's own docstring (`pairwise_completeness_scan.py:40-45`): n=1 supplies neither prevalence, boundary width, nor one-sidedness. |
| **A7** | The negative result becomes an **UNDERPOWERED NULL** (80% power only for \|rho\| ≳ 0.61; 24% at rho 0.30). The `+0.886` comparison is disclosed as a **count against its own exposure**. |
| **A8** | The rho `+0.173` independence claim becomes *"no association **DETECTED**"*, with the ⚠ **recorded-against-ourselves** paragraph: we steered from p **0.088** to p **0.45** while lecturing about absence of evidence. |
| **A9** | The blanket *"mk7ze says nothing at all"* narrowed — it **does** retain a raw-panel NaN-raise contract at **mk7ze lines 321-322 (repo draft 488-489)**. |
| **A10** | The silence sweep gained the word it missed: **`undefined`**, **exactly once** in the posted body at **mk7ze line 82 (repo draft 249)** — a **DIRECTIONAL** claim running the other way, so **not falsified**, but disclosed as swept rather than silently omitted. |
| **A11** | *"(recorded as pre-registered here)"* **withdrawn** — the entry is DRAFTED — NOT POSTED and the prediction is post hoc relative to the 21-region scan. |
| **A12** | Two adopted **scoping repairs that strengthen** §(4): (a) the sentence's own drafting record, whose conclusion was stated **BROADLY**, carried verbatim; (b) region-1 **pair 4**, geometry **`disjoint`**, documented **before posting** and deliberately excluded from the *"settled 5-member expectation"* against **six** observed NaN pairs — converting *"grammatically available"* into *"what the expectation set was built on."* |
| **A13** | 40,000-resample permutation test **p = 0.0072**, with the caveat **verbatim**: it permutes PAIRS, so it validates the **asymptotics**, not the independence assumption at issue in the clustering caveat. |

**F-2 honoured:** only the `REPLACE WITH:` blocks were copied. The evidence blocks (which contain
`merge to 19 parents phi 2.623`) were **never pasted into any artifact** — `2.62` remains **0 hits
file-wide** in the courier, carrying `260903-ict`'s G-A2 forward unchanged.

**F-8 honoured:** `1.52-2.49` copied exactly, not "reconciled" against A5's 3-row excerpt.

### PART B — the courier (`ee3af4b` pattern: fix at source → re-splice → re-anchor)

Seven body edits (A3, A4, A5, A7, A8, B1, and the pin refresh), all strictly **before** the BEGIN
marker. Four source edits (B1, A4, A7, A8) in `260902-vsp/CONTENT-SPEC.md`, then **one script
re-splice**. **No supersession note was added anywhere.**

- **B1 over-correction fixed.** The constants are **distinct live parameters with no runtime
  coupling**, but they are **not** unrelated: mk7ze records the occlusion gate reused *"the same
  fractional gate as the withdrawn ceiling, re-purposed to exclusions"* (**mk7ze line 278**, repo
  draft line 445) and that 0.0005 was *"calibrated against observed NaN count"* (**line 271**, repo
  draft 438) ⇒ a documented **COMMON ORIGIN**. The original action item was wrong to call it a live
  contradiction; **the first correction was wrong in the mirror-image direction.**
- **Splice verified byte-equal both before and after**, markers located **by pattern** (line 374/542
  went stale the moment the body changed). Pre-fix region sha256
  `3a26095e…` (11,490 B) → post-fix `bc702733…` (14,119 B). Exactly one BEGIN, one END, one
  `## ARTIFACTS` inside the region.
- **Both source pins refreshed** (`:23`, `:34`) to the measured post-fix source:
  `34199ab125727f28c7f7b2d910e2005a`, **14376 B, 201 lines**.

### PART C — repo hygiene

| item | before | after |
|---|---|---|
| **C1** pin site 1 `STATE.md:45` | 542 / `c8525e26…` | **613 / `ce679134…`** (MEASURED post-task) |
| **C1** pin site 2 `HANDOFF.json` `record` | 491 / `e2c0b544…` (**stale by 2 generations**) | **613 / `ce679134…`** |
| **C1** pin site 3 `.continue-here.md:15` | 491 / `e2c0b544…` (**stale by 2 generations**) | **613 / `ce679134…`** |
| **C1** pin sites 4-5 courier `:23`/`:34` | `619426a0…` / 11747 B | **`34199ab1…` / 14376 B / 201 lines** |
| **C2** `260903-ict/deferred-items.md` item 3 | *"CLOSED … do not re-open"*, **3 of 5** sites | **all 5 named**, with why two escaped |
| **C3** `STATE.md:54` | *"all 0 hits across its 491 lines"* | **AS-OF qualifier** + names the four terms `9ce807f` itself introduced |
| **C4** `HANDOFF.json` | `three_repo_fixes_QUEUED_NOT_DONE` | **`repo_fixes_status`** — 1 & 2 DONE, only the two-file `tcujq` defect queued |
| **C5** three `260902-vsp` sites | assert the `0.0005` LIVE CONTRADICTION as fact | **dated SUPERSEDED clause added; historical description left unedited on purpose** |

**Why C1 was five sites, not two (F-5):** `HANDOFF.json` escaped `260903-ict`'s guard because it
is **not a `.md` file** and the guard was `--include=*.md`; `.continue-here.md` escaped because it
writes the md5 **truncated** (`` `e2c0b544…` ``), which a full-md5 grep cannot match. This task's
guard is extension-agnostic and prefix-aware. *(Memory precedent: "a claimed invariant needs a
named enforcer" and "a count is a claim".)*

### PART D — queued, NOT executed

Measure the pairs-per-deletion distribution in the tail from
`/home/jupyter/occ_measure/pcs_tail_verdicts.tsv` (already on the VM; reads the emitted TSV only —
no re-run, no genotypes). **THIS DECIDES** whether the overdispersion is parent-region
heterogeneity or a within-window cluster design effect. ⛔ **CARTER FIRES. NEVER AN AGENT.**

---

## 5. DEVIATIONS — all recorded, none silent

1. **F-6a (planned, and honoured as a deviation):** CONTENT-SPEC A7/A8 are **WRONG** on three CIs.
   Deliberately **not copied**; Bonett-Wright used and independently re-derived. Tabulated in §3.
2. **F-10 (checkpoint):** resolved by **measurement** against a one-digit instruction; the
   measurement won. The `F-6 PENDING` placeholder was consequently never written (see §3).
3. **F-7 / C6 — planner-added scope, EXECUTED.** `CONTENT-SPEC` PART C never named the live-state
   files, yet `HANDOFF.json` and `STATE.md`'s live block carried **the same refuted claims** PART A
   removes, and those are what a resuming session reads first. Corrected in place.
4. **Two sites beyond even the plan's C6 enumeration**, both found by the guard rather than by
   reading: `seth_round2_outcome_2026_09_03.leave_one_out_STANDS` (the A5 claim) and `do_not[6]`
   (*"DO register the negative result"*, the A7 claim). Corrected for the same reason.
5. **Three construction-rule self-catches** — in each case the *prose* was fixed, never the guard:
   - I quoted the banned phrase *"the 598-line posted body"* verbatim while describing its
     withdrawal → rephrased.
   - I wrote the CI range with an **en dash** (`1.1–4.2`), so the literal presence check for
     `1.1-4.2` read **0** → changed to ASCII. *(Exactly the "a grep gate matches text, not meaning"
     failure mode; caught by the guard, not by eye.)*
   - I quoted the stale md5 literals in my own HANDOFF pin text, breaking G-09 → rephrased.
6. **Historical logs deliberately NOT rewritten:** `STATE.md`'s Quick Tasks table (incl. the
   `260903-ict` row) and the `260902-vsp` / `260903-ict` task dirs. C5 uses a dated SUPERSEDED
   clause for exactly this reason — rewriting them would falsify the record.
7. **Not done, by hard constraint:** the two-file `tcujq` docstring defect stays **DEFERRED**
   (touches `src/`); the four missing STATE quick-task rows were **not** backfilled.
8. **The STATE row's commit cell reads `(this commit)`, and the planned `git commit --amend` to
   substitute a literal SHA was deliberately NOT performed.** The plan asked for a placeholder
   followed by one amend. That procedure is **self-defeating**: `git commit --amend` rewrites the
   commit, so a literal SHA written *before* the amend is not the SHA of the commit that ends up
   containing it — the row would pin a hash the commit does not have. `(this commit)` is
   self-referential and therefore always true, and it is exactly what the two neighbouring rows
   (`260902-vsp`, `260903-ict`) carry, satisfying the plan's other instruction to copy
   `260903-ict`'s literal shape. Recorded rather than silently chosen. *(Memory precedent: "a
   fixed-SHA whole-file pin is a timebomb" and "a claimed invariant needs a named enforcer".)*

---

## 6. VERIFICATION — sixteen guards GREEN, every negative control seen RED

**Guard file-set:** `osf_deviations.md` · courier · `260902-vsp/CONTENT-SPEC.md` · `HANDOFF.json` ·
`STATE.md` above `### Quick Tasks Completed`.
**Excluded, and why:** `260902-vsp*` / `260903-ict*` / `260904-dgi*` task dirs and STATE's Quick
Tasks table — **these are the log**. This is scoping to record-directories, **not** an exception
for the correction's own prose: within the file-set the construction rule forbids the banned
strings outright, so **no guard carries an exception clause**.

| id | guard | GREEN on real tree | negative control | RED? |
|----|---|---|---|---|
| G-01 | `exclusively at negative offsets` = 0 | ✅ | reinsert the old prediction | ✅ RED |
| G-02 | `cmp head -531` vs original | ✅ byte-identical | flip one byte on line 100 | ✅ RED |
| G-03 | `non-independence cannot create` = 0 | ✅ | reinsert the **BOLDED** form | ✅ RED |
| G-03b | allowed sentence must NOT fire | ✅ **stays GREEN** | `between-window duplication cannot create dispersion` | ✅ GREEN (subject-scoped) |
| G-04 | `count("line N") == count("repo draft line N")` | ✅ | unqualified `line 467` | ✅ RED |
| G-05 | 7 banned phrases = 0 | ✅ | **LINE-WRAPPED** form (literal grep: **0 hits**) | ✅ **RED** |
| G-05 | " | ✅ | each of: no-claim-whatsoever, register-neg, unrelated, 598, unexamined-null | ✅ RED ×5 |
| G-06 | `2.62` = 0 file-wide in courier | ✅ | insert `phi 2.623` | ✅ RED |
| G-07 | appendix byte-equal + 1 BEGIN/1 END | ✅ | one char inside the appendix | ✅ RED |
| G-08 | 14 presence markers in the entry | ✅ | delete `0.0072` + `1.1-4.2` | ✅ RED |
| G-09 | stale md5s outside historical dirs = 0 | ✅ | point pin back at `e2c0b544` | ✅ RED |
| G-10 | pins carry the MEASURED md5 | ✅ 3/3 | wrong md5 in a pin | ✅ RED |
| G-11 | `git status -- src tests` EMPTY | ✅ | `touch src/python/__negctl_probe.py` | ✅ RED (then removed, re-confirmed empty) |
| G-12 | `git status -- .planning/amendments/` EMPTY | ✅ | (G-11 demonstrates the idiom) | — |
| G-13 | `F-6 PENDING` = 0 | ✅ | reinsert the marker | ✅ RED |
| G-14 | `HANDOFF.json` parses | ✅ | truncate the closing brace | ✅ RED |
| G-15 | convention string present in BOTH | ✅ (osf 2, courier 4) | delete the clause | ✅ RED |
| G-16 | 3 superseded Fisher-z CIs = 0 | ✅ | reinsert `[-0.428, +0.435]` | ✅ RED |

⚠ **G-05's line-wrap control is the load-bearing one.** With the false claim reinserted in its
line-wrapped form, `grep -ci "complete in its own direction"` reports **0 hits** while the
normalized guard goes **RED**. That is the empirical proof this task's guards would not have
repeated `260903-ict`'s escape.

**Checked by READING, not by grep** (a grep matches text, not meaning) — confirmed that the
disclosure nowhere claims the residual is one-sided in the population, nowhere claims the LOO rules
out an influential unit, and nowhere presents 1.99x as determined; that A12(a)/(b) genuinely
strengthen §(4) rather than being bolted on; that the re-spliced appendix reads correctly in
context; and that `HANDOFF.json`'s corrected keys still attribute Seth's arguments to Seth (*"The
BETWEEN-window half is still HIS refutation and is still correct; the general claim was ours to
overreach"*).

---

## 7. Final measured anchors

| file | md5 | lines |
|---|---|---|
| `.planning/osf_deviations.md` | `b188cba86eaeeef2365569c5a3949225` | 778 |
| `260902-vsp/CONTENT-SPEC.md` (splice source) | `34199ab125727f28c7f7b2d910e2005a` | 201 |
| courier record | `ce6791344916c6ebebacfadbb808c702` | 613 |
| `.planning/HANDOFF.json` | `8ce159fcf467912ee55175ce67c747b5` | 226 |
| `.planning/STATE.md` | `f3b78edac93212600d8222c9adc649cb` | 3123 |

Frozen prefix `head -531 .planning/osf_deviations.md` → `c46967d9a8c67a37663453c6f86da82a`,
40053 B — **unchanged, proven by `cmp`.**

---

## 8. Scope statement

**Nothing was posted.** No OSF contact, no Seth contact, no GUID reserved. `.planning/amendments/`
untouched. No VM started, **`$0` spend**. `src/` and `tests/` **UNTOUCHED**
(`git status --porcelain -- src tests` empty). One commit on `m3-W2-aou-deltas`, **not pushed**.
