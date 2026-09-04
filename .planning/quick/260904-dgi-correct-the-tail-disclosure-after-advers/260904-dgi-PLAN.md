---
task: 260904-dgi
title: Correct the tail disclosure after a 5-reviewer adversarial review — 5 blockers + 6 highs, fixed at source and re-spliced
mode: quick
type: execute
branch: m3-W2-aou-deltas
worktree: none            # GPFS constraint — worktrees disabled project-wide
docs_only: true           # src/ and tests/ MUST be untouched at commit time
# Task 5 is a NARROW blocking checkpoint (F-10, one rounding digit). F-6 itself is RESOLVED.
autonomous: false
push: false               # commit only
revision: 2                # r2: F-6 RESOLVED (Bonett-Wright); F-7 approved; F-10 opened

files_modified:
  - .planning/osf_deviations.md                                                              # PART A — EDITS the existing entry at :532-669
  - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md      # splice SOURCE — fix at source per ee3af4b
  - .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
  - .planning/HANDOFF.json                                                                    # C1, C4, C6
  - .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md                              # C1
  - .planning/STATE.md                                                                        # C3, C6, quick-task row, pins
  - .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/deferred-items.md      # C2
  - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md      # C5
  - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-SUMMARY.md  # C5
  - .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/260904-dgi-PLAN.md
  - .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/260904-dgi-SUMMARY.md
  - .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/deferred-items.md

files_frozen:
  - src/**                    # DOCS-ONLY gate — the two-file tcujq docstring defect stays DEFERRED
  - tests/**                  # DOCS-ONLY gate
  - .planning/amendments/**   # posted OSF bodies — NEVER edited in-repo, read-only evidence
  - .planning/osf_deviations.md lines 1-531   # the pre-registration chain above the entry

must_haves:
  truths:
    - "Every mk7ze citation in the disclosure names the POSTED line, with the repo-draft line carried alongside."
    - "No artifact claims residual undefined-r is EXCLUSIVELY at negative offsets."
    - "No artifact makes the bare claim that non-independence cannot create dispersion."
    - "No artifact claims the downstream predicate is COMPLETE IN ITS OWN DIRECTION."
    - "No artifact claims mk7ze makes NO claim whatsoever, or registers a negative result."
    - "No artifact calls the two 0.0005 constants unrelated."
    - "The heterogeneity is reported with its CI and its non-robust significance, not as a bare 1.99x."
    - "The leave-one-out is reported at PARENT level, where it is not significant at worst case."
    - "osf_deviations.md lines 1-531 are byte-identical."
    - "The disclosure is still DRAFTED — NOT POSTED."
    - "src/ and tests/ are untouched."
    - "Every pin this task moves is refreshed to a MEASURED post-task value."
    - "Every Spearman CI in the disclosure is Bonett-Wright AND names its convention inline."
  artifacts:
    - path: ".planning/osf_deviations.md"
      provides: "the corrected tail disclosure, entry at :532-EOF"
    - path: ".planning/quick/260902-vsp-.../CONTENT-SPEC.md"
      provides: "corrected splice source (B1 + A4/A7/A8)"
    - path: ".planning/debug/260902-COURIER-...md"
      provides: "corrected courier body + re-spliced appendix"
    - path: ".planning/quick/260904-dgi-.../deferred-items.md"
      provides: "PART D queued measurement + report-only findings"
  key_links:
    - from: "courier appendix (BEGIN..END markers)"
      to: ".planning/quick/260902-vsp-.../CONTENT-SPEC.md from '## ARTIFACTS' to EOF"
      via: "byte-equal splice, re-verified after the source fix"
    - from: "courier lines 23 and 34"
      to: "splice source md5 / bytes / lines"
      via: "pin refreshed to MEASURED post-task values"
    - from: ".planning/STATE.md:45, .planning/HANDOFF.json:209, .continue-here.md:15"
      to: "courier md5 / line count"
      via: "pin refreshed to MEASURED post-task values (C1 — five sites, not three)"
---

<objective>
DOCS-ONLY. One commit, no push. Nothing is posted; nothing is sent.

A 5-reviewer adversarial review (Codex CLI + 4 blind investigators) found **5 blocker-level
and 6 high-level** false or overclaimed statements in a published-bound disclosure. This task
corrects them.

**PART A** — 13 corrections to the tail disclosure, `.planning/osf_deviations.md` entry at
`:532-669`. This **EDITS AN EXISTING ENTRY**; the 531 lines above it must not move.
**PART B** — the same statistical restatements in the courier record, plus the B1
over-correction. Anything inside the byte-frozen VERBATIM APPENDIX is fixed **AT SOURCE** and
**RE-SPLICED** (the `ee3af4b` pattern), never masked behind a supersession note.
**PART C** — repo hygiene: five pin sites (not three), a stale "closed" declaration, a
0-hit claim its own commit falsified, a queued-fix list that is two-thirds done, and a
superseded `LIVE CONTRADICTION` assertion left standing in the 260902-vsp log.
**PART D** — queue the one measurement that settles A3. Carter fires; never an agent.

Purpose: the record asserts things that are false (a citation scheme off by 167 lines; a
prediction our own STATE.md already falsified), things that are unidentified presented as
determined (a bare 1.99x whose significance is not robust), and a negative result that is an
underpowered null. Correcting them before posting is the entire point of drafting first.
</objective>

<authority>
`CONTENT-SPEC.md` in this task directory is THE authoritative content.

**STOP GATE — all three must match:**

| property | value |
|---|---|
| md5 | `f9ef450f89c5cab9109ee4e9fed27788` |
| lines | 230 |
| bytes | 15524 |

Verified at plan time. **Every replacement text in it was reproduced in-session. Copy them;
do not recompute or re-derive any number.** If a number appears to disagree with the tree:
STOP, record it, report it. Never reconcile silently.

⚠ **THE SPEC IS WRONG ON THREE CONFIDENCE INTERVALS AND IS SUPERSEDED ON THEM.** CONTENT-SPEC
A7/A8 quote Fisher-z intervals; the governing convention is Bonett-Wright. See **F-6**, which
records the adjudication, the superseding values, and the required deviation note. One
third-decimal digit remains open — see **F-10** and the narrow checkpoint at Task 5.
</authority>

<hard_constraints>
1. **DOCS-ONLY.** `git status --porcelain -- src tests` EMPTY at commit time. The two-file
   `tcujq` docstring defect stays DEFERRED.
2. **`.planning/osf_deviations.md` PART A EDITS AN EXISTING ENTRY (`:532-669`).** That is
   permitted and required. **Lines 1-531 must be byte-identical afterwards, proven by `cmp`,
   not by eyeball.** Pinned at plan time: `head -531` → md5
   `c46967d9a8c67a37663453c6f86da82a`, 40053 B.
3. **The disclosure stays `DRAFTED — NOT POSTED`.** No OSF contact, no Seth contact, no GUID
   reserved, ever. Never edit anything under `.planning/amendments/` — those are posted
   bodies and this task's read-only evidence.
4. **Do not recompute any statistic.** Copy from the spec.
5. **Fix at source and re-splice; do NOT add a supersession note.** That policy is superseded
   (`ee3af4b`, re-affirmed by `260903-ict` F-2).
6. **Explicit git paths only. NEVER `git add -A` / `git add .`** (shared GPFS tree). No push.
7. **PART C1: MEASURE at the end.** The courier's line count and md5 change again in THIS
   task. Write the measured value; never copy the spec's example (`542` / `c8525e26` is the
   PRE-task value and will be wrong).
8. Leave `.planning/debug/m3-producer-unbounded-dense-read.md` and the other pre-existing
   untracked paths untracked. Do not touch `results*`, `targeted_rerun_*`.
9. Do **not** backfill the four missing STATE quick-task rows (`260828-uej`, `260831-kw8`,
   `260901-l55`, `260901-rvu`). They stay deferred.
</hard_constraints>

<planning_findings>
Measured at plan time in this repo. Stated here so the executor does not rediscover them
mid-edit — and so the guards are not designed against the wrong shape.

### ✅ F-0 — EVERY TREE PREMISE THE SPEC ASSERTS WAS VERIFIED AT PLAN TIME

The spec's corrections rest on claims about the tree. All were checked. None failed.

| spec claim | measured |
|---|---|
| A1: mk7ze repo lines **168-500** → md5 `13a49f543cabcc27ce9f1e589783c060`, **22,945 B**, **333 lines** | ✅ exact |
| A1: the repo file is **598** lines; line 1 reads `DRAFT — NOT POSTED`; `--- PASTE ENDS HERE ---` at :501 | ✅ |
| A1: repo :275 is the "observable NaN requires complete-case zero variance" sentence | ✅ |
| A1: repo :467 is `Clause (a), the occlusion criterion` | ✅ (→ posted 300) |
| A2: `260824-STAGE-B-HALT-region57-...md:62-70` records the +1 case, `chr15:20394741:AT:A` span_end 20394742 vs partner 20394743 | ✅ |
| A2: `STATE.md:287` already says "−1 mirror of `m2_region_00057`'s +1 … EITHER side" | ✅ |
| A3: 22.9% deletion-deletion neighbours (564 of 2461) | ✅ courier :270, appendix :514 |
| A6: `pairwise_completeness_scan.py:40-45` — "(a) prevalence (b) boundary width and whether it is one-sided (c) … **n = 1 supplies none of them**" | ✅ lines 40-45 |
| A9: raw-panel NaN-raise contract at repo :488-489 | ✅ (→ posted 321-322) |
| A10: `undefined` occurs **exactly once** in the posted body, repo :249 | ✅ (→ posted 82); and exactly once in the whole 598-line file |
| A10: `defined row` / `finite r` / `degraded` / `precision` / `SE(` all **0** in the posted body | ✅ all 0 |
| A12(a): `fire-morning-occlusion-oracle-vs-geometry.md:227-233` — "Every NaN-producing pair is geometrically occluded" | ✅ |
| A12(b): `m3_region1_nan_geometry_verdict.md` pair 4 = **`disjoint`** at :20, discussion :30-37 | ✅ |
| A12(b): mk7ze repo :271 "a settled 5-member expectation" | ✅ |
| B1: mk7ze repo :438 "calibrated against observed NaN count"; :445 "the same fractional gate as the withdrawn ceiling, re-purposed to exclusions" | ✅ both |
| A13: `0.0072` / 40,000-resample is **new** — 0 prior hits in `.planning` | ✅ |

**The posted-line map is therefore PROVEN, not asserted: posted = repo − 167.**

### ⛔ F-1 — NAIVE GREP GUARDS GO GREEN ON TWO LIVE FALSE CLAIMS. NORMALIZE OR FAIL.

This was measured, not feared. Two of the brief's own banned phrases are **invisible** to a
literal grep in the exact files they must be removed from:

| banned phrase | literal `grep -i` | why it misses |
|---|---|---|
| `COMPLETE IN ITS OWN DIRECTION` | **0 hits** in `osf_deviations.md` | it is **line-wrapped** at `:573-574`: `…COMPLETE IN ITS OWN` / newline / `DIRECTION across 21 regions…` |
| `cannot CREATE dispersion` | **0 hits** in the courier | it is **markdown-bolded** at `:167`: `Non-independence cannot **CREATE** dispersion` |

Both claims are LIVE. A literal-grep guard would have passed this task while shipping them.

**MANDATORY: every banned-phrase guard runs on a NORMALIZED stream** — strip markdown
emphasis (`*`, `_`, backtick) and smart quotes, fold en/em dashes to `-`, collapse all
whitespace **including newlines** to single spaces, lowercase. The normalizer is written once
in Task 1 (`$SCRATCH/guard.py`) and reused everywhere; it was validated at plan time to find
all six live hits.

⚠ A third form was also found: the courier heading `:316` reads `THE TWO CONSTANTS ARE
UNRELATED` — which does **not** contain the substring `unrelated constants`. The guard must
match **both word orders**.

### ⛔ F-2 — A4's SENSITIVITY TABLE REINTRODUCES `2.62`, WHICH `260903-ict` PERMANENTLY BANNED

CONTENT-SPEC A4 lines 67-73 include `merge to 19 parents  phi 2.623  p 2.0e-4`.

`260903-ict` established `2.62` as **the struck collapse-to-parents argument's fingerprint**
and enforced `0 hits file-wide` in the courier (its guard G-A2). Copying A4's evidence table
verbatim into any artifact would resurrect it.

**RESOLUTION — copy the `REPLACE WITH:` block ONLY.** For A2, A3, A4, A5, A7, A8, A9 and A11
the spec gives an evidence block followed by an indented `REPLACE WITH:` block. **Only the
`REPLACE WITH:` block is content.** The evidence blocks are the planner/reviewer's working —
recorded in the SUMMARY, never pasted into an artifact.

Verified: none of the `REPLACE WITH:` blocks contains `2.62`. `260903-ict`'s G-A2 is
**carried forward unchanged** into this task's battery (G-06).

### ⛔ F-3 — THE `cannot create dispersion` GUARD MUST BE SUBJECT-SCOPED, NOT SUBSTRING-SCOPED

A3's own replacement text opens: *"BETWEEN-window duplication cannot create dispersion
(simulated 0.98 under equal parent rates)."* That sentence is **correct and required**. A
substring ban on `cannot create dispersion` would fire on the correction itself.

Per the brief, the answer is not an exception — it is to **scope the guard to the property**.
The false claim's fingerprint is its **SUBJECT**:

- ⛔ BANNED (normalized): `non-independence cannot create`
- ✅ ALLOWED: `between-window duplication cannot create dispersion`
- ✅ ALLOWED: `it does not follow that non-independence cannot: within-window clustering can and does`

Verified at plan time: the allowed sentence normalizes to `…non-independence cannot: within-
window…` — the `:` separates it from any `create`, so the banned pattern cannot match it.
The guard needs **no exception clause**, and the construction rule below keeps it that way.

### ⛔ F-4 — `line 467` AND `line 275` CANNOT BE BANNED OUTRIGHT; A1 REQUIRES CITING BOTH FORMS

A1's ⚠ mandates: *"Cite BOTH forms so a reader can check either: `mk7ze line 108 (repo draft
line 275)`."* So `line 275` and `line 467` **must survive** in the correction.

**RESOLUTION — a counting identity, not a substring ban.** The banned property is citing
these as *posted / mk7ze* lines. So:

```
count("line 467") == count("repo draft line 467")      # every occurrence is qualified
count("line 275") == count("repo draft line 275")
```

This is strictly stronger than a substring ban (it cannot be satisfied by deletion alone, and
it fails the moment an unqualified citation reappears), and its negative control is trivial:
write `at line 467` without the qualifier and the identity breaks.

Measured at plan time — **UNQUALIFIED** occurrences today:
`osf_deviations.md` → `line 467` ×1, `line 275` ×2 · `HANDOFF.json` → `line 275` ×1 ·
`STATE.md` → `line 275` ×3 · `.continue-here.md` → `line 275` ×1.

### ⚠ F-5 — C1's "TWO SITES" IS ACTUALLY FIVE, AND `260903-ict`'s GUARD LET TWO ESCAPE

`260903-ict`'s G-E1 was `grep -rn <old-md5> .planning --include=*.md`. **`.planning/HANDOFF.json`
is not a `.md` file**, so it escaped the guard and still pins the courier at the two-generations-old
`491 lines, md5 e2c0b544…`. `.continue-here.md` escaped for a different reason: it writes the md5
**truncated** as `` `e2c0b544…` ``, which the full-md5 grep could not see.

Complete site list, measured at plan time:

| # | site | pins | state |
|---|---|---|---|
| 1 | `.planning/STATE.md:45` | 542 / `c8525e26…` | current, will go stale in THIS task |
| 2 | `.planning/HANDOFF.json:209` | 491 / `e2c0b544…` | **stale by two generations** |
| 3 | `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md:15` | 491 / `e2c0b544…` | **stale by two generations** |
| 4 | courier `:23` | source `619426a0…` / 11747 B / 173 | current, moves in Task 2 |
| 5 | courier `:34` | "the **11747**-B one" | current, moves in Task 2 |

**This task's guard must be extension-agnostic and must match truncated md5 prefixes.**

### ✅ F-6 — RESOLVED BY CARTER. BONETT-WRIGHT THROUGHOUT, AND THE SPEC IS SUPERSEDED.

**The conflict (found at plan time).** CONTENT-SPEC A7 quoted the CI for `rho +0.004` as
`[-0.428, +0.435]` while asserting in the same clause *"|rho| up to 0.446 is INSIDE this CI"*.
0.446 > 0.435 — the clause cited a value outside the interval it was written against. Measured
diagnosis: `[-0.428, +0.435]` is Fisher-z (`SE = 1/sqrt(n-3)`); `0.446` is Bonett-Wright
(`SE = 1.03/sqrt(n-3)`). One sentence, two conventions.

**ADJUDICATION (Carter, 2026-09-04).** Use **BONETT-WRIGHT for every Spearman CI in the
disclosure**, because these are rank correlations and plain Fisher-z is the Pearson formula;
Bonett-Wright is the standard Spearman interval; and it is the **WIDER** interval, which is the
conservative direction for a correction whose whole subject is overclaiming. Carter records the
origin as his own: the statistical audit used Bonett-Wright consistently, and CONTENT-SPEC A7
was written by substituting self-computed Fisher-z values beside the audit's `0.446`.

### ⛔ F-6a — RECORDED DEVIATION: CONTENT-SPEC A7/A8 ARE **WRONG** ON THREE CIs

Hard constraint 4 says copy from the spec. **For these three intervals the spec is superseded
and MUST NOT be copied.** This is a recorded deviation, not a silent substitution — the SUMMARY
must state it in these terms.

| rho | ⛔ CONTENT-SPEC (Fisher-z, WRONG) | ✅ USE (Bonett-Wright) |
|---|---|---|
| `+0.004` | `[-0.428, +0.435]` (A7 :108) | **`[-0.440, +0.446]`** |
| `+0.173` | `[-0.280, +0.563]` (A8 :122) | **`[-0.292, +0.572]`** |
| `-0.199` | `[-0.581, +0.255]` (A7 :106) | **`[-0.590, +0.267]`** ⚠ see F-10 |
| `-0.201` | `[-0.59, +0.27]` (A7 :107) | **`[-0.591, +0.266]`** |

⚠ Because the interval widens, **`"|rho| up to 0.446 is inside this CI"` is now CORRECT** and is
retained. That clause was the symptom; it turns out to have been the surviving-correct half.

All four values were re-derived at plan time and reproduce exactly under
`tanh(atanh(rho) +/- 1.96 * 1.03/sqrt(18))` at three decimals. They are used because they were
independently checked, not because they were supplied.

### ⛔ F-6b — NAME THE CONVENTION IN THE TEXT. THIS IS THE ACTUAL FIX.

An **unnamed** convention is what let two of them into one sentence. Every place a Spearman CI
appears, the disclosure and the courier must carry the convention inline, e.g.:

> `95% CI, Fisher z with the Bonett-Wright Spearman standard error 1.03/sqrt(n-3)`

**A presence guard (G-15) enforces the convention string.** A referee can then reproduce the
interval; today they cannot, and that is the defect the numbers were only a symptom of.

### ⚠ F-10 — ONE THIRD-DECIMAL DIGIT IS STILL OPEN. **NARROW BLOCKING CHECKPOINT (Task 5).**

For `rho -0.199` the supplied corrected upper bound is **`+0.268`**. Measured at plan time:

```
tanh(atanh(-0.199) + 1.96*1.03/sqrt(18)) = 0.26747718   ->  3dp = 0.267
```

**`0.26747718` is below `0.2675`, so it rounds to `0.267`, not `0.268`.** The statistical
audit's own reported value — quoted in the same adjudication as `[-0.590, +0.267]` — **agrees
with the measurement.** Two independent sources say `0.267`; one line of the adjudication says
`0.268`.

The other three supplied values are exact at 3dp (`+0.004` -> `[-0.440, +0.446]`;
`+0.173` -> `[-0.292, +0.572]`; `-0.201` -> `[-0.591, +0.266]`), so this is an isolated
rounding slip, not a convention problem.

⛔ **The executor does NOT choose.** This is one digit in a published-bound disclosure, and
"never reconcile silently" does not have a size threshold — the table above is exactly the
arithmetic reconciliation that memory says to run *before* freezing a number. Task 5 asks one
question and resumes.

### ℹ F-7 — PLANNER-ADDED SCOPE (C6). FLAGGED, NOT SMUGGLED.

PART C names five hygiene items. It does **not** name `HANDOFF.json:212` / `:215` / `:224` /
`:225` or the `STATE.md` live block at `:42-66` — yet measurement shows these carry the **same
refuted claims PART A removes**:

| site | carries |
|---|---|
| `HANDOFF.json:212` | `non-independence CANNOT CREATE dispersion` (A3) |
| `HANDOFF.json:215` (`seth_asks_1_2_3`) | `DO register the negative result` (A7) |
| `HANDOFF.json:224` (`OPEN_QUESTION_BACK_TO_SETH`) | `mk7ze line 275` (A1) |
| `HANDOFF.json:225` | `EXCLUSIVELY at negative offsets` (A2) **and** `COMPLETE IN ITS OWN DIRECTION` (A6) |
| `STATE.md:42` | bare `1.99×` (A4) · `:43` `+0.173` independence (A8) |
| `STATE.md:53` | `Non-independence cannot *create* dispersion` (A3) |
| `STATE.md:55` | `Leave-one-out STANDS … 1.99–2.48, worst-case p 0.0063` (A5) |
| `STATE.md:56` | `do register the negative result` (A7) |
| `STATE.md:61-62` | survivor-geometry framing (A2/A6) · `:66` `mk7ze line 275` (A1) |

These are **live-state files a resuming session reads first**, not historical logs. Leaving
them would (a) recreate the false-invariant pattern this repo has been bitten by repeatedly,
and (b) force the banned-phrase guards to carry file-level exceptions — the anti-pattern the
brief explicitly forbids.

**Recommended: DO IT (Task 8).** It is docs-only, bounded to enumerated lines, and it makes
the guards whole-artifact-set. It is isolated in **one deletable task** so the coordinator can
drop it without disturbing anything else. If dropped, the guard file-set in Task 10 shrinks to
match and the SUMMARY must record the exception. **The executor must record C6 as a
planner-added deviation either way.**

### ℹ F-8 — A5's RANGE `1.52-2.49` IS NOT DERIVABLE FROM ITS 3-ROW EXCERPT

A5 lists three parent-level LOO fits (max shown `2.412`) but states the range as `1.52-2.49`.
The three rows are an explicit excerpt of 19 fits, not the full set — so this is **not** a
contradiction. **Copy `1.52-2.49` as given. Do not "reconcile" it to `2.41`.** Recorded so
the executor does not treat it as an F-6-class conflict.

### ℹ F-9 — WHAT LIVES IN THE APPENDIX vs THE BODY (decides what needs a re-splice)

Measured. The appendix is spliced from `260902-vsp/CONTENT-SPEC.md` `## ARTIFACTS`→EOF.

| item | splice SOURCE (→ appendix) | courier BODY |
|---|---|---|
| A3 `cannot CREATE` | 0 | **1** (`:167`) |
| A4 bare `1.99` | **2** (`:70`, `:73`) | **4** |
| A5 `leave-one-out` | 0 | **1** (`:172`) |
| A7 `UNEXPLAINED` / `+0.886` | **1** / **1** (`:75-79`) | **2** |
| A8 `+0.173` | **1** (`:87-90`) | **3** |
| B1 `unrelated` | **2** (`:117`, `:120`) | **2** (`:316`, `:320`) |

⇒ **Source edits: B1, A4, A7, A8.** (A3 and A5 are body-only — no source edit needed for
them.) Then one script re-splice carries all four into the appendix.

Splice anchors verified at plan time: BEGIN marker at courier `:374`, END at `:542`,
`## ARTIFACTS` at source `:7` (inside the spliced region, so source fixes propagate).
</planning_findings>

<tasks>

<task type="auto" id="1">
  <name>Task 1: STOP GATE — pin anchors, snapshot originals, build the normalizing guard, arm negative controls</name>
  <files>(reads only; writes only under the scratchpad)</files>
  <action>
Set and create the scratch dir, and export it so later tasks can reuse it:

```
export SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/260904-dgi
mkdir -p "$SCRATCH"
```

**A. Pin SIX anchors. ANY mismatch = STOP, edit nothing, report.**

| file | md5 | lines | bytes |
|---|---|---|---|
| `260904-dgi-.../CONTENT-SPEC.md` (**this task's spec**) | `f9ef450f89c5cab9109ee4e9fed27788` | 230 | 15524 |
| `.planning/osf_deviations.md` | `beb34d0bad73950113739bffb3188dd6` | 669 | — |
| `…/260902-vsp-.../CONTENT-SPEC.md` (**splice SOURCE**) | `619426a0157d199c711a4d771023330a` | 173 | 11747 |
| courier record | `c8525e2665e98cfa9d3d0f1c4266429d` | 542 | 34644 |
| `.planning/HANDOFF.json` | `124beac35e03a809528ce2bec905bcc0` | 226 | — |
| `.planning/STATE.md` | `2b05879ba99a7d063ca39991c33c4146` | 3122 | — |

**Plus the frozen-prefix anchor** (the load-bearing one for hard constraint 2):
`head -531 .planning/osf_deviations.md | md5sum` → **`c46967d9a8c67a37663453c6f86da82a`**,
`| wc -c` → **40053**.

**B. Snapshot originals** into `$SCRATCH/` as `osf_deviations.orig.md`, `vsp_spec.orig.md`,
`courier.orig.md`, `HANDOFF.orig.json`, `STATE.orig.md`, plus
`osf_head531.orig` (= `head -531 .planning/osf_deviations.md`). Scratch only — never committed.
`osf_head531.orig` is the `cmp` baseline for G-02.

**C. Re-prove the posted-line map (F-0) in this executor's own shell.** Do not take it from
the plan:

```
sed -n '168,500p' .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md > "$SCRATCH/mk7ze_posted.md"
md5sum "$SCRATCH/mk7ze_posted.md"   # MUST be 13a49f543cabcc27ce9f1e589783c060
wc -l -c "$SCRATCH/mk7ze_posted.md" # MUST be 333 / 22945
```
Any mismatch ⇒ **STOP**: A1's entire citation rewrite rests on this and on nothing else.

**D. Write `$SCRATCH/guard.py`** (F-1 — MANDATORY, not optional). It normalizes, then reports
every banned pattern count plus the two F-4 counting identities, for each file given on argv.
Exit non-zero if any count is non-zero.

```python
#!/usr/bin/env python3
import re, sys, pathlib
def norm(t):
    t = re.sub(r'[*_`‘’]', '', t)                    # md emphasis + smart quotes
    t = t.replace('‑','-').replace('–','-').replace('—','-')   # dashes -> '-'
    t = re.sub(r'\s+', ' ', t)                                 # collapse ALL whitespace incl newlines
    return t.lower()
BANNED = {
  "exclusively-neg-offsets":  r"exclusively at negative offsets",
  "bare-cannot-create":       r"non-independence cannot create",
  "complete-own-direction":   r"complete in its own direction",
  "no-claim-whatsoever":      r"no claim whatsoever",
  "register-neg-result":      r"register (this as )?(a|the) negative result",
  "unrelated-constants":      r"unrelated constants|constants are unrelated",
  "598-line-posted":          r"598-line posted",
  "stronger-unexamined-null": r"stronger than an unexamined null",
  "f6-pending":               r"f-6 pending",
}
bad = 0
for f in sys.argv[1:]:
    t = norm(pathlib.Path(f).read_text(encoding="utf-8"))
    hits = {k: len(re.findall(v, t)) for k, v in BANNED.items()}
    for n in ("467", "275"):                                   # F-4 counting identity
        hits[f"unqualified-line-{n}"] = (len(re.findall(rf"line {n}", t))
                                         - len(re.findall(rf"repo draft line {n}", t)))
    nz = {k: v for k, v in hits.items() if v}
    print(("FAIL " if nz else "OK   ") + f, nz or "")
    bad += bool(nz)
sys.exit(1 if bad else 0)
```

**E. Prove the normalizer is NECESSARY** (this is the negative control for the guard *design*
itself — a guard you have never seen catch something is not evidence). On the UNEDITED tree:

| pattern | literal `grep -i` | normalized |
|---|---|---|
| `complete in its own direction` in `osf_deviations.md` | must be **0** | must be **1** |
| `non-independence cannot create` in the courier | must be **0** | must be **1** |

If the normalized counts are not 1, the normalizer is broken — **STOP**.

**F. Record the PRE-fix splice equality** so the re-splice is provably a re-splice, not a
retype: extract the courier region between the BEGIN marker line and the `END` marker and
assert it is byte-equal to source `## ARTIFACTS`→EOF. Record its byte length and sha256.
Locate the markers **BY PATTERN, never by line number**.

**G. Arm negative controls.** Copy each original to `*.negctl.*` in `$SCRATCH`. Task 10
mutates only these. **Never mutate a tracked file for a negative control.**
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
md5sum .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/CONTENT-SPEC.md \
       .planning/osf_deviations.md \
       .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md \
       .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
       .planning/HANDOFF.json .planning/STATE.md
# expect: f9ef450f89c5cab9109ee4e9fed27788 / beb34d0bad73950113739bffb3188dd6 /
#         619426a0157d199c711a4d771023330a / c8525e2665e98cfa9d3d0f1c4266429d /
#         124beac35e03a809528ce2bec905bcc0 / 2b05879ba99a7d063ca39991c33c4146
head -531 .planning/osf_deviations.md | md5sum    # expect c46967d9a8c67a37663453c6f86da82a
head -531 .planning/osf_deviations.md | wc -c     # expect 40053
sed -n '168,500p' .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md | md5sum
# expect 13a49f543cabcc27ce9f1e589783c060
grep -ci "complete in its own direction" .planning/osf_deviations.md   # expect 0 (literal — F-1 proof)
python3 "$SCRATCH/guard.py" .planning/osf_deviations.md                # expect FAIL, complete-own-direction=1
    </automated>
  </verify>
  <done>Six anchors + the frozen-prefix anchor + the mk7ze posted-body anchor all match; snapshots and negative-control copies staged; `guard.py` exists and was proven to find two hits a literal grep misses; pre-fix splice equality confirmed True.</done>
</task>

<task type="auto" id="2">
  <name>Task 2: PART B — B1, A4, A7, A8 AT SOURCE in the splice spec (step 1 of the ee3af4b pattern)</name>
  <files>.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md</files>
  <action>
Four edits. Match this file's plain/indented style (it is **not** the courier's bolded
markdown). Line numbers are pre-edit; **work top-down or re-locate by heading after each edit.**

**Edit 1 — B1, lines 117-139** (the `## CORRECTION — the 0.0005 "contradiction" was FALSE;
the two constants are unrelated` section, stopping before the blank line preceding
`## SCOPE CAVEATS` at 141).

The heading and the body both call the constants **unrelated**. That is the over-correction.
Replace with CONTENT-SPEC **B1's `REPLACE WITH:` block**, in substance:

  - New heading: `## CORRECTION — the 0.0005 "contradiction" was FALSE; the constants are DISTINCT but SHARE AN ORIGIN`
  - The two current `0.0005` occurrences are **DISTINCT LIVE PARAMETERS with NO RUNTIME
    COUPLING**: `_OCCLUSION_ANOMALY_FRACTION` is removed from `src/` and `tests/` (0 hits) and
    `pairwise_completeness_scan.py:45` is correct to call the occlusion bound withdrawn.
  - ⚠ **But they are NOT "unrelated"**: mk7ze records that the occlusion gate reused *"the same
    fractional gate as the withdrawn ceiling, re-purposed to exclusions"* — so the shared value
    has a documented **COMMON ORIGIN**. Cite mk7ze **posted :271 / :278** (repo draft :438 /
    :445) using the F-4 both-forms convention.
  - The original ACTION ITEM was wrong to call this a live contradiction; **the first
    correction was wrong to call the constants unrelated.**
  - **KEEP** the surviving true content: the posted replacement gate
    (`OCCLUSION_SITE_FRACTION_CEILING = 0.005056`, `OCCLUSION_INFLATION_CEILING = 3.42`, both in
    `src/python/occlusion_gate_constants.py`); `condition_ld_matrix.py`'s `ceiling_frac = 0.0005`
    is the LD-matrix NaN-zeroing ceiling and that file contains `occlu` **zero** times; the
    ROOT CAUSE sentence; and the DEFERRED `tcujq` docstring paragraph.

**Edit 2 — A4, lines 67-74** (`## FINDING 2`). The block currently ends
`overdispersion 1.99   <-- QUOTE THIS ONE` with a bare ⚠ note. Append CONTENT-SPEC **A4's
`REPLACE WITH:` block**: the CI `~1.1-4.2`, `chi2 37.78, dof 19, p 6.3e-3`, the
drop-both-chr15-windows estimate **1.52 (p 0.073)**, and the sentence that the dispersion is
robust in DIRECTION (every correction gives phi > 1.3) but **POORLY DETERMINED in magnitude,
and its significance is not robust to the choice of overlap correction**.

⛔ **F-2: do NOT paste A4's sensitivity table.** `merge to 19 parents phi 2.623` would
resurrect `2.62`, which `260903-ict` banned file-wide and this task's G-06 still enforces.
The all-21 `2.36` figure already present at `:68` is fine and stays.

**Edit 3 — A7, lines 75-79** (`UNEXPLAINED — no structural covariate accounts for it:` plus
the `+0.886` clause). Replace with CONTENT-SPEC **A7's `REPLACE WITH:` block**: the three rho
values **with their CIs**, the power statement (80% power only for `|rho| >~ 0.61`, 24% power
at rho 0.30), *"This is an UNDERPOWERED NULL, not a negative result"*, and the sentence that
the `+0.886` comparison is a **count against its own exposure** and does not calibrate power
for a size-normalized rate.

⚠ **F-6/F-6a — the spec's CIs here are WRONG and must NOT be copied.** Write the
**Bonett-Wright** intervals: `-0.199` -> **`[-0.590, +0.267]`** (⚠ F-10, see below),
`-0.201` -> **`[-0.591, +0.266]`**, `+0.004` -> **`[-0.440, +0.446]`**. Because the interval
widens, the clause *"|rho| up to 0.446 is inside this CI"* is now **CORRECT** — keep it.
⚠ **F-6b — NAME THE CONVENTION inline**, once in this section:
`95% CI, Fisher z with the Bonett-Wright Spearman standard error 1.03/sqrt(n-3)`. G-15 guards it.
⚠ **F-10 — the `-0.199` upper bound is the ONE open digit.** Leave the literal marker
`F-6 PENDING` in place of `+0.267`/`+0.268` and fill it in Task 5. Do not guess.
(`guard.py` counts this marker, so it cannot be forgotten.)

**Edit 4 — A8, lines 87-90** (`INDEPENDENT of PRE/POST: spearman(...) = +0.173` and the ⚠
"Do NOT support independence with the PRE-vs-POST 2x2" note). Replace with CONTENT-SPEC **A8's
`REPLACE WITH:` block**: no association was **DETECTED** (rho +0.173, **Bonett-Wright CI
`[-0.292, +0.572]`** — ⛔ NOT the spec's Fisher-z `[-0.28, +0.56]`, superseded per F-6a —
p 0.45; 2x2 chi2 p 0.088); **BOTH are underpowered at n=21 and NEITHER establishes
independence**; and the ⚠ **recorded against ourselves** paragraph — the rho is the WEAKER of
the two (p 0.45 vs p 0.088), so steering to it was itself an absence-of-evidence error.

⚠ **CONSTRUCTION RULE — load-bearing for G-01..G-07.** This text lands in the appendix by
splice. It MUST NOT contain, in any case or markdown form:
`unrelated constants` · `constants are unrelated` · `non-independence cannot create` ·
`exclusively at negative offsets` · `complete in its own direction` · `no claim whatsoever` ·
`register (this as) a/the negative result` · `stronger than an unexamined null` · `2.62` · an
**unqualified** `line 275` / `line 467`.
**If a guard later needs an exception for this prose, the prose broke the rule: fix the prose,
not the guard.**

`## ARTIFACTS` at line 7 must stay byte-identical — it is the splice anchor. Do not touch it.

**Then record the source's POST-fix anchors** (md5 / bytes / lines) for Task 3's pin refresh.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
P=.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
python3 "$SCRATCH/guard.py" "$P"        # expect only f6-pending non-zero at this stage
grep -c "^## ARTIFACTS" "$P"            # expect 1 (splice anchor intact)
grep -c "2\.62" "$P"                    # expect 0  (F-2)
for p in "1.1-4.2" "0.073" "0.088" "COMMON ORIGIN" "F-6 PENDING" "1.03/sqrt(n-3)" "0.446" "0.572"; do
  printf '%-18s => ' "$p"; grep -ci -- "$p" "$P"; done   # each >=1  (G-15 convention string included)
grep -c "0\.435\|\[-0\.28, +0\.56\]" "$P"   # superseded Fisher-z: expect 0
md5sum "$P"; wc -l -c "$P"              # record POST-fix anchors for Task 3
    </automated>
  </verify>
  <done>Source carries the B1 common-origin correction and the A4/A7/A8 restatements; the only non-zero guard count is the intentional `F-6 PENDING` marker; `2.62` absent; `## ARTIFACTS` anchor byte-identical; post-fix anchors recorded.</done>
</task>

<task type="auto" id="3">
  <name>Task 3: PART B — courier BODY edits (A3, A4, A5, A7, A8, B1) and refresh the two source pins</name>
  <files>.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md</files>
  <action>
All edits are strictly **BEFORE** the `<!-- BEGIN VERBATIM APPENDIX` marker (currently `:374`).
The appendix is handled by Task 4's script splice, **never by hand**. Line numbers are
pre-edit; re-locate by heading after each edit.

**Edit 1 — A4, `## FINDING 2` at `:133-144`.** The headline paragraph at `:135-136` ends
*"overdispersion 1.99x. This is the figure to quote."* Extend it with A4's `REPLACE WITH:`
block (CI `~1.1-4.2`; drop-both-chr15 **1.52, p 0.073**; robust in DIRECTION, poorly
determined in MAGNITUDE, significance not robust to the overlap correction). ⛔ No `2.62`.

**Edit 2 — A7, the `UNEXPLAINED` block at `:146-155`.** Replace with A7's `REPLACE WITH:`
block, with the **Bonett-Wright** CIs per F-6a (`-0.201` -> `[-0.591, +0.266]`, `+0.004` ->
`[-0.440, +0.446]`) and the convention named inline per F-6b. ⛔ Do NOT copy the spec's Fisher-z
`[-0.581, +0.255]` / `[-0.428, +0.435]`. Insert the `F-6 PENDING` marker **only** for the
`-0.199` upper bound (F-10; Task 5 fills it).

**Edit 3 — A3, inside `### WHAT DOES AND DOES NOT ESTABLISH THE HETEROGENEITY`, `:167-170`**
(the `**THE VALID REFUTATION — Seth's, not ours.** Non-independence cannot **CREATE**
dispersion…` paragraph). Replace with A3's `REPLACE WITH:` block:

  - BETWEEN-window duplication cannot create dispersion (simulated **0.98** under equal parent
    rates). **It does NOT follow that non-independence cannot: WITHIN-window clustering can and
    does.**
  - An average of **two co-moving pairs per occluding deletion reproduces the observed 1.99
    EXACTLY with zero parent-rate heterogeneity.**
  - The pairs-per-deletion distribution in the tail **HAS NOT BEEN MEASURED**, so the observed
    dispersion is **NOT yet attributable** to parent-region heterogeneity rather than to a
    cluster design effect.
  - Note the operative structure is measured in this very record: **22.9%** of tail pairs are
    deletion-deletion neighbours (`564 of 2461`, SCOPE CAVEAT (2)).

  ⛔ **DELETE**, do not soften: the claim that this is *"STRONGER than an unexamined null
  because both artifact explanations were eliminated"*. One was eliminated; the more plausible
  one was never tested. In the courier this appears as *"This is the argument that carries the
  conclusion."* at `:170` — that sentence must go.

  ⚠ **Keep** the surrounding `does not discriminate` / `65%` / `+3.6%` / CV≈0.20 material that
  `260903-ict` added. This task narrows one claim inside that subsection; it does not undo it.

**Edit 4 — A5, `**STILL VALID AND RETAINED.** Leave-one-out over 21 fits…` at `:172-173`.**
Replace with A5's `REPLACE WITH:` block: leave-one-WINDOW-out gives 1.99-2.48 **but does not
address influence** (the two chr15 windows shield each other; the LOO minimum **is** the
headline); leave-one-PARENT-out over the **19 distinct parent regions** ranges **1.52-2.49**
with worst-case **p 0.073** — parent **00060** is influential enough that its removal renders
the heterogeneity **non-significant at alpha 0.05**.
⚠ Per **F-8**, copy `1.52-2.49` exactly. Do not reconcile it against A5's 3-row excerpt.

**Edit 5 — A8, `## FINDING 3` independence paragraph at `:194-199`.** Replace with A8's
`REPLACE WITH:` block, including the ⚠ **recorded against ourselves** paragraph. The existing
text says *"The independence claim leans on the rho"* — that is the exact inversion A8
corrects; it must go.

**Edit 6 — B1 body, `## CORRECTION — THE 0.0005 ACTION ITEM WAS FALSE; THE TWO CONSTANTS ARE
UNRELATED` at `:316-350`.** Same substance as Task 2's Edit 1, in the courier's bolded-markdown
style. New heading e.g.
`## CORRECTION — THE 0.0005 ACTION ITEM WAS FALSE, AND THE FIRST CORRECTION OVERSHOT`.
⚠ `:320` reads *"…**different, unrelated constants**, and nothing in the tree conflicts."* —
the `unrelated` claim **and** the heading must both go. Keep the DOCS-ONLY sentence and the
DEFERRED `tcujq` paragraph.

**Edit 7 — F-5 pin refresh, `:23` and `:34`.** Both pin the splice source. Write Task 2's
**post-fix** anchors (md5 / bytes / lines) at `:23`, and the matching byte count at `:34`
(currently *"the 11747-B one"*). A pin whose subject has moved is a false invariant.

⚠ **Same CONSTRUCTION RULE as Task 2** applies to all seven edits.
⛔ Do **NOT** hand-edit anything at or after the `BEGIN VERBATIM APPENDIX` marker.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
awk '/^<!-- BEGIN VERBATIM APPENDIX/{exit} {print}' "$F" > "$SCRATCH/courier.body"
python3 "$SCRATCH/guard.py" "$SCRATCH/courier.body"   # expect only f6-pending non-zero
grep -c "2\.62" "$F"                                   # G-06 carried forward: expect 0 FILE-WIDE
for p in "1.1-4.2" "1.52" "0.073" "0.088" "HAS NOT BEEN MEASURED" "22.9" "F-6 PENDING" \
         "1.03/sqrt(n-3)" "0.446" "0.572"; do
  printf '%-24s => ' "$p"; grep -c -- "$p" "$SCRATCH/courier.body"; done   # each >=1
grep -c "0\.435\|\[-0\.28, +0\.56\]\|\[-0\.581, +0\.255\]" "$SCRATCH/courier.body"   # expect 0
grep -c "carries the conclusion" "$SCRATCH/courier.body"   # expect 0 (A3 deletion)
grep -c "leans on the rho"       "$SCRATCH/courier.body"   # expect 0 (A8 inversion removed)
sed -n '23p;34p' "$F"                                      # pins show Task 2 post-fix values
    </automated>
  </verify>
  <done>All six statistical/B1 body corrections in place; the two deleted overclaims are 0 hits; `2.62` still 0 file-wide; both source pins refreshed to Task 2's measured values; nothing at or after the BEGIN marker was hand-edited.</done>
</task>

<task type="auto" id="4">
  <name>Task 4: PART B — re-splice the appendix from the corrected source, BY SCRIPT</name>
  <files>.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md</files>
  <action>
Step 3 of the `ee3af4b` pattern. **Spliced by script, never retyped** — that is what makes
byte-equality evidence that no number was re-keyed.

⚠ **Locate the markers by PATTERN, not by line number.** Task 3 changed the body's length, so
374/542 are stale.

```python
import pathlib
F = pathlib.Path(".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md")
P = pathlib.Path(".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md")
BEGIN = "<!-- BEGIN VERBATIM APPENDIX (byte-equal to CONTENT-SPEC.md from '## ARTIFACTS' to EOF) -->\n"
END   = "<!-- END VERBATIM APPENDIX -->"
c = F.read_text(encoding="utf-8"); s = P.read_text(encoding="utf-8")
spec = s[s.index("## ARTIFACTS"):]
i = c.index(BEGIN) + len(BEGIN); j = c.index(END, i)
F.write_text(c[:i] + spec + c[j:], encoding="utf-8")
```

Then **re-verify and re-anchor**:
1. Re-extract the appendix region; assert **byte-equal** to `spec`. Record the new byte length
   and sha256 — they SUPERSEDE the Task 1F pre-fix values.
2. Run `guard.py` on the **WHOLE** courier file — only `f6-pending` may be non-zero. This is
   the moment the banned-phrase guards become satisfiable file-wide.
3. Sanity: exactly one `BEGIN VERBATIM APPENDIX`, one `END VERBATIM APPENDIX`, and
   `## ARTIFACTS` exactly once inside the appendix region (a true replacement, not a
   duplication or truncation).
4. Record the courier's post-splice md5 / line count / byte count. **These are provisional** —
   Task 5 may edit the courier again to fill the `F-6 PENDING` markers. The pins in Tasks 7 and
   8 must be measured **after** Task 5, not here.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
grep -c "BEGIN VERBATIM APPENDIX" "$F"   # expect 1
grep -c "END VERBATIM APPENDIX" "$F"     # expect 1
python3 "$SCRATCH/guard.py" "$F"         # expect only f6-pending non-zero
python3 - <<'PY'
import pathlib
F=pathlib.Path(".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md")
P=pathlib.Path(".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md")
BEGIN="<!-- BEGIN VERBATIM APPENDIX (byte-equal to CONTENT-SPEC.md from '## ARTIFACTS' to EOF) -->\n"
END="<!-- END VERBATIM APPENDIX -->"
c=F.read_text(encoding="utf-8"); s=P.read_text(encoding="utf-8")
i=c.index(BEGIN)+len(BEGIN); j=c.index(END,i); reg=c[i:j]
print("SPLICE BYTE-EQUAL:", reg==s[s.index("## ARTIFACTS"):], len(reg), "B")
print("ARTIFACTS in region:", reg.count("## ARTIFACTS"))
PY
    </automated>
  </verify>
  <done>Appendix re-spliced by script and byte-equal to the corrected source; exactly one BEGIN/END pair and one `## ARTIFACTS` inside the region; only `f6-pending` non-zero on the whole-file guard; new splice anchors recorded.</done>
</task>

<task type="checkpoint:decision" id="5" gate="blocking">
  <name>Task 5: NARROW CHECKPOINT (F-10) — confirm one third-decimal digit, then fill the F-6 markers</name>
  <files>.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md, .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md, .planning/osf_deviations.md</files>
  <decision>
For `rho -0.199` under Bonett-Wright, is the 95% CI upper bound **`+0.267`** or **`+0.268`**?

F-6 itself is RESOLVED (Bonett-Wright throughout, convention named inline). This is the only
open item, and it is one digit.
  </decision>
  <context>
Measured at plan time, and re-measurable in one line:

```
tanh(atanh(-0.199) + 1.96*1.03/sqrt(18)) = 0.26747718   ->  3dp = 0.267
```

`0.26747718 < 0.2675`, so it rounds to **`0.267`**.

- The **statistical audit** reported `[-0.590, +0.267]` — agrees with the measurement.
- The **adjudication's "recomputed in-session" line** supplied `[-0.590, +0.268]`.

The other three values are exact at 3dp, so this is an isolated rounding slip rather than a
convention problem. Nothing else in the plan depends on it.

Why this is worth a stop at all: this number is going into a published-bound disclosure whose
entire subject is overclaiming, and "never reconcile silently" has no size threshold. The
alternative — an executor quietly picking the one it likes — is precisely the failure mode.
  </context>
  <options>
    <option id="option-267">
      <name>+0.267 — follow the measurement and the audit</name>
      <pros>Arithmetically correct at 3dp; matches the audit's own reported value; two independent sources agree.</pros>
      <cons>Departs from the literal "use these verbatim" instruction by one digit.</cons>
    </option>
    <option id="option-268">
      <name>+0.268 — follow the adjudication verbatim</name>
      <pros>Honors the instruction exactly as written; the disclosure is marginally more conservative.</pros>
      <cons>Contradicts the measurement and the audit; a referee reproducing the interval would get 0.267.</cons>
    </option>
    <option id="option-4dp">
      <name>Report all four CIs at 4dp and sidestep the rounding entirely</name>
      <pros>The question disappears; maximum reproducibility for a referee.</pros>
      <cons>Inconsistent with the 3dp precision used everywhere else in the entry.</cons>
    </option>
  </options>
  <resume-signal>Select: option-267, option-268, or option-4dp.</resume-signal>
  <action>
**Before pausing**, present the F-10 measurement above and state plainly that the executor has
not chosen and will not choose.

**After the decision**, write the confirmed value and replace every `F-6 PENDING` marker — in
the splice source, in the courier body, and in `osf_deviations.md` if already written — with
the Bonett-Wright interval **and its named convention** (F-6b).

⚠ If the splice **source** was among them, **re-run Task 4's splice script** and re-verify
byte-equality. Do not hand-edit the appendix.

Record in the SUMMARY, as recorded deviations and not as silent substitutions:
  - **F-6** — the two-convention conflict, the adjudication (Bonett-Wright), and its author.
  - **F-6a** — that CONTENT-SPEC A7/A8 are **WRONG** on three CIs and were deliberately NOT
    copied, listing spec-value vs used-value for each.
  - **F-6b** — that the convention is now named inline and guarded (G-15).
  - **F-10** — the digit, the measurement, and who confirmed it.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
grep -rc "F-6 PENDING" \
  .planning/osf_deviations.md \
  .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
# ALL must be 0 after resolution
# the superseded Fisher-z values must NOT appear anywhere in the artifact set
grep -rn "0\.435\|\[-0\.280, +0\.563\]\|\[-0\.581, +0\.255\]" \
  .planning/osf_deviations.md \
  .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md | wc -l   # expect 0
    </automated>
  </verify>
  <done>The F-10 digit was presented with its measurement and NOT chosen by the executor; the confirmed value and its author are recorded; every `F-6 PENDING` marker is filled with a Bonett-Wright interval carrying its named convention; none of the three superseded Fisher-z intervals appears in the artifact set; if the source changed, the appendix was re-spliced and re-verified byte-equal.</done>
</task>

<task type="auto" id="6">
  <name>Task 6: PART A — rewrite the disclosure entry, osf_deviations.md :532-669 (A1 through A13)</name>
  <files>.planning/osf_deviations.md</files>
  <action>
**This EDITS AN EXISTING ENTRY.** Lines **1-531 must not move** — hard constraint 2. The entry
begins at `:532` (`## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure…`); `:531` is
blank and is the last frozen line.

**Safe edit idiom (recommended):** write the new entry to `$SCRATCH/entry.new.md`, then

```
head -531 .planning/osf_deviations.md > "$SCRATCH/out"
cat "$SCRATCH/entry.new.md" >> "$SCRATCH/out"
mv "$SCRATCH/out" .planning/osf_deviations.md
```

This makes the frozen prefix a copy, not an edit, and G-02 then proves it.

⛔ **NOT-POSTED discipline is unchanged.** `**Status:** DRAFTED — NOT POSTED; placement and
posting are Carter's.` stays near the top. No `**Posted:**` lead. No invented GUID.

Apply all 13 corrections. **Copy the `REPLACE WITH:` block ONLY** — never the evidence block
above it (F-2).

**A1 — every mk7ze citation (BLOCKER).** Posted = repo − 167, proven in Task 1C.
Rewrite, using the both-forms convention `mk7ze line N (repo draft line M)` (F-4):
  - §(4) heading and body: `mk7ze line 275` → **`mk7ze line 108 (repo draft line 275)`**
  - `clause (a) at line 467` → **`clause (a) at mk7ze line 300 (repo draft line 467)`**
  - §(5): `sweep of the 598-line posted body` → **`sweep of the 333-line posted body`**, with
    the note that **598 is the REPO DRAFT file** (line 1 reads `DRAFT — NOT POSTED`; lines
    502-598 are post-posting status material), and that **the sweep's CONCLUSION is unaffected**
    — zero hits over the superset implies zero over the subset — **but the sentence stated a
    false fact about what was posted.**
  ⚠ **Every** `line 275` / `line 467` in this entry must carry the `repo draft` qualifier.
  G-04 is a counting identity and will catch any that do not.

**A2 — the registered prediction is FALSIFIED (BLOCKER).** Replace the `:578-580` prediction
with A2's `REPLACE WITH:` block. It must be explicitly **SAMPLE-SCOPED**, must name
`m2_region_00057`'s **+1** as **ALREADY KNOWN out-of-sample**, must state that the residual
class sits immediately adjacent to the REF span on **EITHER side**, and that **production
tests the rate on both sides**. Cite `260824-STAGE-B-HALT-region57-...md:62-70` and
`STATE.md:287`. ⛔ Never write `EXCLUSIVELY at negative offsets` unqualified.

**A3 — "non-independence cannot CREATE dispersion" is FALSE (BLOCKER).** At `:638-640`.
Replace with A3's `REPLACE WITH:` block, including that the pairs-per-deletion distribution
**HAS NOT BEEN MEASURED** and the dispersion is therefore **NOT yet attributable**.
⛔ **DELETE** the claim that this is *"STRONGER than an unexamined null because both artifact
explanations were eliminated"* — one was eliminated; the more plausible one was never tested.

**A4 — the heterogeneity magnitude is UNIDENTIFIED (BLOCKER).** Replace the bare `1.99x` at
`:556` with A4's `REPLACE WITH:` block. ⛔ No sensitivity table, no `2.62` (F-2).

**A5 — the leave-one-out does not rule out an influential unit (BLOCKER).** At `:639-640`.
Replace with A5's `REPLACE WITH:` block. Copy `1.52-2.49` exactly (F-8).

**A6 — "COMPLETE IN ITS OWN DIRECTION" is overclaimed from n=1 (BLOCKER).** At `:573-575`
(**line-wrapped** — F-1). Replace with A6's `REPLACE WITH:` block, including the citation to
the scanner's own docstring `pairwise_completeness_scan.py:40-45` and its statement that
**n=1 supplies neither prevalence, boundary width, nor one-sidedness.**

**A7 — the negative result becomes an UNDERPOWERED NULL (HIGH).** Replace §(7)'s
*"**Register this as a negative result.**"* (`:637`) with A7's `REPLACE WITH:` block.

⛔ **F-6a — the spec's three CIs in A7/A8 are WRONG and must NOT be copied.** Use Bonett-Wright:
`-0.199` -> **`[-0.590, F-6 PENDING]`** (F-10, Task 5 fills the upper bound),
`-0.201` -> **`[-0.591, +0.266]`**, `+0.004` -> **`[-0.440, +0.446]`**. The interval widens, so
*"|rho| up to 0.446 is inside the interval"* is **CORRECT** and is retained.
⚠ **F-6b — NAME THE CONVENTION** inline, once:
`95% CI, Fisher z with the Bonett-Wright Spearman standard error 1.03/sqrt(n-3)`. G-15 guards it.

⛔ Do NOT register a negative result. ⛔ Do NOT pre-register a dispersion figure (that ⛔ at
`:641` is correct and stays).

**A8 — the rho +0.173 independence claim, and OUR OWN INVERSION (HIGH).** At `:562`. Replace
with A8's `REPLACE WITH:` block **including the ⚠ recorded-against-ourselves paragraph**.
⛔ **F-6a: write the Bonett-Wright CI `[-0.292, +0.572]`, NOT the spec's Fisher-z
`[-0.280, +0.563]`.** Carry the convention clause here too if this CI is stated separately.

**A9 — "NO claim whatsoever" is too broad (HIGH).** At `:605`. Replace with A9's `REPLACE
WITH:` block, and cite the retained raw-panel NaN-raise contract at
**mk7ze lines 321-322 (repo draft lines 488-489)**.

**A10 — the silence sweep missed the word that matters (HIGH).** In §(5): **ADD `undefined`
to the recorded sweep terms** and state the finding explicitly — it occurs **EXACTLY ONCE** in
the posted body, at **mk7ze line 82 (repo draft line 249)**: *"The exclusion policy for an
occluded variant is unaffected: its LD is structurally undefined"*. State that this is a
**DIRECTIONAL** claim (occluded ⇒ LD undefined) running the **OTHER way** from the tail
finding, so it is **not falsified** — but it is disclosed as swept and considered, **not
silently omitted.**

**A11 — "(recorded as pre-registered here)" cannot be true (HIGH).** At `:578`. Replace with
A11's `REPLACE WITH:` block: a **prospective production prediction, to be pre-registered IF
AND WHEN this disclosure is posted, and posted BEFORE production testing**; it is **post hoc
relative to the 21-region scan and is not a pre-registration today.**

**A12 — the two SCOPING REPAIRS that strengthen §(4)** (reviewer-identified, adopted):
  (a) **ADD the provenance of line 275**: it descends from
      `.planning/debug/fire-morning-occlusion-oracle-vs-geometry.md:227-233`, whose conclusion
      was stated **BROADLY** — *"Every NaN-producing pair is geometrically occluded"*. State
      that plainly: claiming a scope for a sentence while withholding its own drafting record
      is the weakest available position, and **mk7ze §(e) set the house standard of carrying
      provenance verbatim.**
  (b) **ADD region-1 pair 4**: `.planning/amendments/m3_region1_nan_geometry_verdict.md:20,30-37`
      records a NaN pair whose geometry is **`disjoint`** — a NaN pair with **NO covering
      deletion**, documented **BEFORE posting** and **DELIBERATELY EXCLUDED** from the 5-member
      expectation set (mk7ze **line 104 (repo draft line 271)**: *"a settled 5-member
      expectation"* against **SIX** observed NaN pairs). This converts *"the narrow reading is
      grammatically available"* into *"the narrow reading is what the expectation set was
      actually built on."*

**A13 — FREE WIN: the permutation confirmation.** Add to §(2) or §(7): 40,000-resample Monte
Carlo permutation test, **p = 0.0072** (asymptotic chi-square p 6.3e-3; the asymptotic value is
mildly anti-conservative, conclusion unchanged). ⚠ Include the caveat verbatim: the test
**permutes PAIRS and therefore assumes exchangeable independent pairs — it validates the
asymptotics, NOT the independence assumption at issue in the clustering caveat above.**

⚠ **CONSTRUCTION RULE** — the same banned list as Task 2 applies to every word written here.
⚠ Do not "improve" a number, do not round, do not convert `6.3e-3` to `0.0063` or back — copy
the notation the spec uses in each place.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
head -531 .planning/osf_deviations.md > "$SCRATCH/osf.head531"
cmp "$SCRATCH/osf.head531" "$SCRATCH/osf_head531.orig" && echo "G-02 FROZEN PREFIX OK"
python3 "$SCRATCH/guard.py" .planning/osf_deviations.md    # expect ALL zero (F-6 already resolved)
tail -n +532 .planning/osf_deviations.md > "$SCRATCH/osf.entry"
for p in "DRAFTED — NOT POSTED" "mk7ze line 108" "mk7ze line 300" "333-line" "1.1-4.2" \
         "1.52" "0.073" "m2_region_00057" "undefined" "0.0072" "disjoint" "0.088" \
         "1.03/sqrt(n-3)" "0.446" "0.572" "0.266"; do
  printf '%-24s => ' "$p"; grep -c -- "$p" "$SCRATCH/osf.entry"; done   # each >=1 (G-15 included)
# G-16: none of the three SUPERSEDED Fisher-z intervals may appear
grep -c "0\.435\|\[-0\.280, +0\.563\]\|\[-0\.581, +0\.255\]" "$SCRATCH/osf.entry"   # expect 0
grep -c '^\*\*Posted:\*\*' "$SCRATCH/osf.entry"     # expect 0
grep -c "2\.62" "$SCRATCH/osf.entry"                # expect 0 (F-2)
git status --porcelain -- .planning/amendments/     # expect EMPTY
    </automated>
  </verify>
  <done>`cmp` reports lines 1-531 byte-identical; the entry still reads DRAFTED — NOT POSTED with no `**Posted:**` lead; all 13 corrections present with their presence markers; every banned phrase 0 on the normalized stream; `.planning/amendments/` untouched.</done>
</task>

<task type="auto" id="7">
  <name>Task 7: PART C1-C5 + PART D — five pin sites, the stale closure, the falsified 0-hit claim, the queued-fix list, the superseded log entry</name>
  <files>.planning/HANDOFF.json, .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md, .planning/STATE.md, .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/deferred-items.md, .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md, .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-SUMMARY.md, .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/deferred-items.md</files>
  <action>
⛔ **MEASURE FIRST.** The courier is final only after Tasks 4 and 5. Before writing any pin:

```
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
md5sum "$F"; wc -l -c "$F"
```
**Write THAT value.** `542` / `c8525e26…` is the PRE-task value and is now wrong — hard
constraint 7. The spec's own C1 text calls it out as an example, not a value.

**C1 — refresh ALL FIVE pin sites (F-5), not the two the spec names.**

| # | site | write |
|---|---|---|
| 1 | `.planning/STATE.md:45` | measured md5 + line count |
| 2 | `.planning/HANDOFF.json:209` (`record` key) | measured md5 + line count |
| 3 | `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md:15` | measured md5 (truncated form is fine) + line count |
| 4 | courier `:23` | **already done in Task 3** — re-verify it still equals the live source |
| 5 | courier `:34` | **already done in Task 3** — re-verify |

⚠ `HANDOFF.json` must remain valid JSON.

**C2 — `260903-ict/deferred-items.md`, item 3.** It declares *"F-3a is **CLOSED** … **Do not
re-open**"* while listing only **3** of the **5** sites. Correct it to name all five (F-5),
and add why two escaped: `HANDOFF.json` is not a `.md` file so the `--include=*.md` guard never
saw it, and `.continue-here.md` writes the md5 **truncated** so the full-md5 grep could not
match it. **This is a live-status correction, not a rewrite of history** — the claim "closed"
was false when written and is being made true.

**C3 — `.planning/STATE.md:54`.** It asserts `collaps`/`parent`/`2.62`/`leave-one-out`/`2.48`/
`0.0063` are *"all 0 hits across its 491 lines"*. Measured in the courier **now**:

| term | hits |
|---|---|
| `collaps` | 0 |
| `parent` | **5** |
| `2.62` | 0 |
| `leave-one-out` | **1** |
| `2.48` | **1** |
| `0.0063` | **1** |

`9ce807f` — the commit that wrote the sentence — **introduced four of the six itself.** Add an
**AS-OF qualifier** naming the pre-`9ce807f` state (e.g. *"measured 2026-09-03 against the
pre-`9ce807f` courier, 491 lines"*) **and** note that `9ce807f`'s own PART A2 addition then
introduced `parent`, `leave-one-out`, `2.48` and `0.0063`. Do not delete the finding — the
finding (the argument was never in the record) is true; only its 0-hit evidence went stale.

**C4 — `.planning/HANDOFF.json:220`, key `three_repo_fixes_QUEUED_NOT_DONE`.** Fixes 1 and 2
**are DONE** (by `260903-ict`). Rename the key (e.g. `repo_fixes_status`) or restate its
contents so items 1 and 2 read DONE with their commit, and **fix 3 — the two-file `tcujq`
docstring defect — is the only one still queued**, with its **wider two-file scope**
(`condition_ld_matrix.py:4`,`:153` and `write_conditioned_ld_npz.py:4`,`:17`,`:85`).
`STATE.md:68-72` already says this; HANDOFF has not caught up.

**C5 — the `260902-vsp` log. ADD A DATED SUPERSEDED CLAUSE. DO NOT REWRITE THE HISTORY.**
Three sites still assert the `0.0005` **LIVE CONTRADICTION** as fact:
  - `260902-vsp/deferred-items.md:7` (the item-1 heading)
  - `260902-vsp/260902-vsp-SUMMARY.md:17` (the `banked` frontmatter line)
  - `260902-vsp/260902-vsp-SUMMARY.md:250-256` (the Deferred item)

Add, at each, a dated clause of the form:

> ⚠ **SUPERSEDED 2026-09-04 (`260904-dgi`).** The alleged contradiction was FALSE and was
> withdrawn by `260903-ict`; `260904-dgi` then found that correction **overshot** — the two
> constants are distinct live parameters with no runtime coupling, **but they are not
> unrelated**: mk7ze records that the occlusion gate reused *"the same fractional gate as the
> withdrawn ceiling, re-purposed to exclusions"*, so the shared value has a documented common
> origin. The courier heading cited here no longer exists. **The historical description below
> is left unedited on purpose** — rewriting it would falsify the log.

⚠ **CONSTRUCTION RULE:** the clause must not itself contain `unrelated constants` or
`constants are unrelated`. `"not unrelated"` is fine and is verified clean.

**PART D — queue the measurement that settles A3.** Write
`.planning/quick/260904-dgi-.../deferred-items.md`. Record, verbatim in substance:

> **MEASURE the pairs-per-deletion distribution in the tail** from
> `/home/jupyter/occ_measure/pcs_tail_verdicts.tsv` (already on the VM; **no re-run, no
> genotypes**, reads the emitted TSV only). Group tail rows by `del_vid` and report the
> cluster-size distribution. Design effect ≈ `1 + (c−1)·ICC`. **THIS DECIDES** whether the
> observed overdispersion is parent-region heterogeneity or a within-window cluster effect.
> **Until measured, Finding 2's magnitude is NOT attributable.**
> ⛔ **CARTER FIRES. NEVER AN AGENT.** Not executed here.

Also carry forward into the same file:
  1. The **two-file `tcujq` docstring defect** — still DEFERRED, touches `src/`. Discharge: one
     task fixing both files **plus a named enforcer test seen RED first**.
  2. The **four missing STATE quick-task rows** (`260828-uej`, `260831-kw8`, `260901-l55`,
     `260901-rvu`) — out of scope by hard constraint 9.
  3. **F-6's adjudication** (Task 5) — what was decided, by whom, and that the alternative
     convention exists.
  4. **F-7 / C6's disposition** — done or dropped, and why.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
MD5=$(md5sum "$F" | cut -d' ' -f1); LN=$(wc -l < "$F"); echo "MEASURED courier: $MD5 / $LN lines"
for f in .planning/STATE.md .planning/HANDOFF.json .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md; do
  printf '%-72s md5? ' "$f"; grep -c -- "${MD5:0:8}" "$f"; done   # each >=1
grep -rn "e2c0b544\|c8525e26" .planning 2>/dev/null | grep -v "^\.planning/quick/26090[234]-" | wc -l   # expect 0
python3 -c "import json;json.load(open('.planning/HANDOFF.json'));print('HANDOFF.json VALID')"
grep -c "SUPERSEDED 2026-09-04" .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-SUMMARY.md   # each >=1
DD=.planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/deferred-items.md
grep -c "pcs_tail_verdicts.tsv" "$DD"; grep -c "CARTER FIRES" "$DD"   # each >=1
    </automated>
  </verify>
  <done>All five pin sites carry the MEASURED post-task courier value; `HANDOFF.json` is still valid JSON; the two stale md5s appear only inside historical task dirs; C2 names five sites with the reason two escaped; C3 carries an AS-OF qualifier and the four terms its own commit introduced; C4 shows 1-2 DONE and 3 queued with its two-file scope; C5's dated SUPERSEDED clause is at all three sites with the history unedited; PART D queued with CARTER FIRES.</done>
</task>

<task type="auto" id="8">
  <name>Task 8: PLANNER-ADDED (F-7 / C6) — clear the same refuted claims from the live-state files</name>
  <files>.planning/HANDOFF.json, .planning/STATE.md</files>
  <action>
⚠ **THIS TASK IS NOT IN CONTENT-SPEC. It is planner-added (F-7) and MUST be recorded as a
deviation in the SUMMARY.** It is deliberately isolated so the coordinator can delete it
without touching anything else — **if dropped, remove `HANDOFF.json` and `STATE.md` from
Task 10's guard file-set and record the exception.**

**Why:** measurement shows these two live-state files carry the **same refuted claims** PART A
removes. They are what a resuming session reads first. Leaving them recreates the
false-invariant pattern, and it would force the banned-phrase guards to carry file-level
exceptions — the anti-pattern the brief forbids.

**Correct in place** (these are current-state files, not historical logs — the C5
add-a-SUPERSEDED-clause idiom does **not** apply here; C3 already establishes
"restate or qualify" as the idiom for STATE.md):

| site | claim | correction |
|---|---|---|
| `HANDOFF.json:212` (`seth_conceded`) | `non-independence CANNOT CREATE dispersion` | A3: BETWEEN-window duplication cannot; WITHIN-window clustering can and does; **not yet attributable** pending PART D |
| `HANDOFF.json:215` (`seth_asks_1_2_3`) | `DO register the negative result` | A7: an **UNDERPOWERED NULL**, not a negative result |
| `HANDOFF.json:224` (`OPEN_QUESTION_BACK_TO_SETH`) | `mk7ze line 275` | A1: `mk7ze line 108 (repo draft line 275)` |
| `HANDOFF.json:225` (`survivor_geometry_PROMOTE_TO_HEADLINE`) | `EXCLUSIVELY at negative offsets` **and** `COMPLETE IN ITS OWN DIRECTION` | A2 + A6: sample-scoped; `m2_region_00057`'s +1 is known out-of-sample; **not proof of predicate completeness** |
| `STATE.md:42` | bare `1.99×` | A4: add the CI and the non-robust significance |
| `STATE.md:43` | `Independent of PRE/POST at ρ +0.173` | A8: **no association DETECTED**; neither test establishes independence |
| `STATE.md:53` | `Non-independence cannot *create* dispersion` | A3 |
| `STATE.md:55` | `Leave-one-out STANDS — 1.99–2.48, worst p 0.0063` | A5: parent-level LOO **1.52-2.49, worst p 0.073** — not significant at worst case |
| `STATE.md:56` | `do register the negative result` | A7 |
| `STATE.md:61-62` | survivor-geometry framing | A2 + A6 |
| `STATE.md:66` | `mk7ze line 275` | A1 both-forms |

⚠ **Do NOT touch `STATE.md:2354`** — the `260903-ict` quick-task row. That is a **historical
log row** describing what that task did; rewriting it would falsify the log. Its `491 lines`
and `unrelated constants` are historical statements about a past state. **This is the one
place the guard file-set must be line-scoped**, and Task 10's guard for `STATE.md` therefore
runs on the live block above `### Quick Tasks Completed` only.

⚠ Keep `HANDOFF.json` valid JSON. Keep every corrected key's meaning attributable — where a
claim was Seth's, say so; this task narrows the claims, it does not reassign authorship.

⚠ **CONSTRUCTION RULE** applies here too.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
python3 -c "import json;json.load(open('.planning/HANDOFF.json'));print('VALID JSON')"
python3 "$SCRATCH/guard.py" .planning/HANDOFF.json      # expect ALL zero
python3 - <<'PY'
import pathlib, os
t = pathlib.Path(".planning/STATE.md").read_text(encoding="utf-8")
i = t.index("### Quick Tasks Completed")
pathlib.Path(os.environ["SCRATCH"] + "/STATE.live").write_text(t[:i], encoding="utf-8")
print("live block bytes:", i)
PY
python3 "$SCRATCH/guard.py" "$SCRATCH/STATE.live"       # expect ALL zero
grep -c "^| 260903-ict |" .planning/STATE.md            # expect 1 (historical row untouched)
    </automated>
  </verify>
  <done>`HANDOFF.json` is valid JSON with all four keys corrected and 0 banned hits; `STATE.md`'s live block has 0 banned hits; the `260903-ict` historical row is untouched; the deviation is recorded for the SUMMARY.</done>
</task>

<task type="auto" id="9">
  <name>Task 9: STATE.md quick-task row for 260904-dgi</name>
  <files>.planning/STATE.md</files>
  <action>
**One row.** Insert immediately after the `260903-ict` row (currently `:2354`), before the
blank line preceding `## Session Continuity` (`:2355`). This is a **mid-file insert** —
STATE.md is 3122 lines and continues well past the table.

Match the existing shape **exactly**: **7 pipes / 6 cells**, ending with the directory link.
Copy `260903-ict`'s literal shape rather than the header's nominal one.

```
| 260904-dgi | **<description>** | 2026-09-04 | <commit-sha> | Inline (docs-only; fixed at source + re-spliced; frozen-prefix proven by cmp; all negative controls observed RED) | [260904-dgi-correct-the-tail-disclosure-after-advers](./quick/260904-dgi-correct-the-tail-disclosure-after-advers/) |
```

The description must state: a 5-reviewer adversarial review found **5 blockers + 6 highs**;
the mk7ze citation scheme was **off by 167 lines** (posted = repo − 167, proven against the
posted body's own md5) so `line 275`→**108**, `line 467`→**300** (which does not exist in 333
lines), `598-line`→**333-line**; the registered prediction was **falsified by our own
STATE.md:287** and is now sample-scoped; **the bare dispersion refutation was false** —
within-window clustering can create dispersion, and the pairs-per-deletion distribution is
**unmeasured**, so Finding 2's magnitude is **not yet attributable**; the bare **1.99x** now
carries **CI ~1.1-4.2** and the disclosure that the **drop-both-chr15 estimate is 1.52,
p 0.073 — not significant**; the window-level LOO was replaced by a **parent-level LOO
(1.52-2.49, worst p 0.073)** because the two chr15 windows shield each other and the LOO
minimum was the headline itself; the **own-direction completeness** and **blanket-silence**
overclaims withdrawn; the negative result is now an **UNDERPOWERED NULL**; **our own inversion
recorded against us** (we steered from p 0.088 to p 0.45 while lecturing about absence of
evidence); the silence sweep gained the word it missed — **`undefined`, exactly once at mk7ze
line 82**; the courier's `unrelated` **over-correction** fixed **at source and re-spliced**
(mk7ze records a **documented common origin**); **five** courier pin sites refreshed (not the
three `260903-ict` closed — `HANDOFF.json` escaped an `--include=*.md` guard and
`.continue-here.md` a full-md5 grep); PART D queued (**Carter fires**); nothing posted, no OSF
or Seth contact, no VM, `$0`, `src/`+`tests/` untouched.

⚠ The description is a **historical log row**, so it may quote a withdrawn phrase as a "was"
value — but it sits inside the Quick Tasks table, which Task 10's `STATE.md` guard excludes by
construction. Do not let that licence leak into the live block.

The commit SHA is known only after Task 10. Write a placeholder and `git commit --amend`
**once** — one commit total; do not create a second commit for the SHA.

⛔ Do NOT backfill `260828-uej`, `260831-kw8`, `260901-l55`, `260901-rvu` (hard constraint 9).
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
grep -c "^| 260904-dgi |" .planning/STATE.md   # expect 1
awk -F'|' '/^\| 260904-dgi \|/{print "cells:", NF-2}' .planning/STATE.md   # expect 6
grep -c "^| 260828-uej |\|^| 260831-kw8 |\|^| 260901-l55 |\|^| 260901-rvu |" .planning/STATE.md  # expect 0
    </automated>
  </verify>
  <done>Exactly one `260904-dgi` row with 6 cells / 7 pipes, inserted after the `260903-ict` row; no rows backfilled.</done>
</task>

<task type="auto" id="10">
  <name>Task 10: Full verification battery with negative controls SEEN RED, then ONE commit</name>
  <files>(verification only, then git commit)</files>
  <action>
**Every guard runs GREEN on the real tree, and its negative control runs on a scratch copy and
MUST be observed RED. A green assertion you have never seen fail is not evidence.** Paste both
outcomes into the SUMMARY. **Never mutate a tracked file for a negative control** — mutate
`$SCRATCH/*.negctl.*` only.

**GUARD FILE-SET** (all banned-phrase guards run the **normalized** stream via `guard.py` — F-1):
`osf_deviations.md` · courier · `260902-vsp/CONTENT-SPEC.md` (splice source) · `HANDOFF.json` ·
`$SCRATCH/STATE.live` (STATE.md above `### Quick Tasks Completed`).

**EXCLUDED, with the reason stated in the SUMMARY:**
`.planning/quick/260902-vsp*`, `260903-ict*`, `260904-dgi*` and `STATE.md`'s Quick Tasks table.
These are **the log**. Rewriting them would falsify the record — the same reason C5 uses a
dated SUPERSEDED clause instead of an edit. **This is scoping to record-directories, NOT an
exception for the correction's own prose:** within the guard file-set the construction rule
forbids the banned strings outright, so no guard needs an exception. **If the executor finds
itself wanting one, the prose broke its construction rule — fix the prose, not the guard.**

| id | guard (GREEN on real tree) | negative control (MUST go RED) |
|----|---------------------------|-------------------------------|
| G-01 | normalized `exclusively at negative offsets` = **0** across the file-set | reinsert the old prediction into `osf.negctl.md` → ≥1 |
| G-02 | `cmp head -531 osf_deviations.md` vs `osf_head531.orig` → **identical** | flip one byte on line 100 of `osf.negctl.md` → `cmp` differs |
| G-03 | normalized `non-independence cannot create` = **0** (F-3, subject-scoped) | insert the bolded form into `courier.negctl.md` → ≥1. **Also prove the guard does NOT fire on the allowed sentence** `between-window duplication cannot create dispersion` |
| G-04 | `count("line 467") == count("repo draft line 467")` **and** the same for `line 275`, across the file-set (F-4) | write `clause (a) at line 467` unqualified into `osf.negctl.md` → identity breaks |
| G-05 | normalized `complete in its own direction`, `no claim whatsoever`, `register (this as) (a\|the) negative result`, `unrelated constants`, `constants are unrelated`, `598-line posted`, `stronger than an unexamined null` all = **0** | reinsert each into the matching `*.negctl.*` → ≥1 each. ⚠ **G-05 must be seen RED specifically on the LINE-WRAPPED `COMPLETE IN ITS OWN` / newline / `DIRECTION` form and on the BOLDED form** — that is the whole reason the normalizer exists |
| G-06 | `2.62` = **0** file-wide in the courier (`260903-ict`'s guard, carried forward — F-2) | insert `merge to 19 parents phi 2.623` into `courier.negctl.md` → ≥1 |
| G-07 | appendix region **byte-equal** to source `## ARTIFACTS`→EOF; exactly one BEGIN and one END marker | change one character inside `courier.negctl.md`'s appendix → equality fails |
| G-08 | presence: `mk7ze line 108`, `mk7ze line 300`, `333-line`, `1.1-4.2`, `1.52`, `0.073`, `m2_region_00057`, `undefined`, `0.0072`, `0.088`, and the Bonett-Wright bounds `0.446` / `0.572` / `0.266` all ≥1 in the disclosure entry | delete `0.0072` and `1.1-4.2` from `osf.negctl.md` → presence check fails |
| G-09 | the stale courier md5s `e2c0b544` / `c8525e26` appear **0** times outside `.planning/quick/26090[234]-*` (extension-agnostic, prefix-aware — F-5) | point `HANDOFF.negctl.json` back at `e2c0b544` → count ≥1 |
| G-10 | every pin site carries the **MEASURED** post-task courier md5 | point a scratch pin at a wrong md5 → mismatch |
| G-11 | `git status --porcelain -- src tests` **EMPTY** | `touch src/python/__negctl_probe.py` → non-empty; then `rm` and re-confirm empty |
| G-12 | `git status --porcelain -- .planning/amendments/` **EMPTY** | (covered by G-11's demonstration of the idiom) |
| G-13 | `F-6 PENDING` = **0** everywhere | (covered by Task 5's verify) |
| G-14 | `HANDOFF.json` parses as JSON | truncate a brace in `HANDOFF.negctl.json` → parse fails |
| G-15 | **F-6b convention string** `1.03/sqrt(n-3)` appears ≥1 wherever a Spearman CI is stated (disclosure entry AND courier) | delete the clause from `osf.negctl.md` → presence check fails |
| G-16 | **F-6a**: the three SUPERSEDED Fisher-z intervals `+0.435`, `[-0.280, +0.563]`, `[-0.581, +0.255]` appear **0** times in the artifact set | reinsert `[-0.428, +0.435]` into `osf.negctl.md` → count ≥1 |

⚠ **G-05's line-wrap/bold negative control is the single most important one in this battery.**
It is the empirical proof that this task's guards would not have repeated `260903-ict`'s
escape. Run it explicitly and paste the RED output.

⚠ **RE-VALIDATE THE NORMALIZER AFTER THE EDITS, NOT ONLY BEFORE.** Task 1E proved it finds
all six live hits on the unedited tree. Re-run that same proof now against the `*.negctl.*`
copies: **a normalizer that has silently stopped matching is indistinguishable from a
successful fix.** Both readings must be in the SUMMARY — found-6-before, and still-finds-6
on the negative controls after.

**Also confirm by READING (a grep matches text, not meaning):**
  - The disclosure nowhere claims the residual is one-sided in the population, nowhere claims
    the LOO rules out an influential unit, and nowhere presents 1.99x as determined.
  - A12(a) and A12(b) genuinely **strengthen** §(4) rather than being bolted on.
  - The re-spliced appendix reads correctly in context.
  - `HANDOFF.json`'s corrected keys still attribute Seth's arguments to Seth.
**State in the SUMMARY that this was checked by reading — do not claim a grep proved it.**

**Write the SUMMARY** at `.planning/quick/260904-dgi-.../260904-dgi-SUMMARY.md`: the Task-1
anchor table; the F-0 premise table re-proven in-shell; the F-1 normalizer necessity proof
(both literal-0 / normalized-1 measurements, **before AND after**); the **F-6 adjudication** —
the two-convention conflict, the measured shape, Bonett-Wright, and who chose it; **F-6a as an
explicit recorded deviation** — that CONTENT-SPEC A7/A8 are WRONG on three CIs and were
deliberately NOT copied, tabulated spec-value vs used-value; **F-6b** (convention named +
guarded); **F-10** (the digit, the measurement, who confirmed it); the F-2 resolution (evidence
blocks not pasted); the **F-7 / C6 planner-added deviation** and its disposition; every pin moved with its
old and new value; the guard table with **both green and RED outcomes**; the deferred items;
and the statement that **nothing was posted, no OSF or Seth contact was made, no VM was
started, `$0` spend.**

**Commit — ONE commit, explicit paths, NO push, NO `git add -A`.**

```
git add .planning/osf_deviations.md \
        .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md \
        .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
        .planning/HANDOFF.json \
        .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md \
        .planning/STATE.md \
        .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/deferred-items.md \
        .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md \
        .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-SUMMARY.md \
        .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/CONTENT-SPEC.md \
        .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/260904-dgi-PLAN.md \
        .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/260904-dgi-SUMMARY.md \
        .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/deferred-items.md
```

Afterwards `git status --porcelain` must still show the pre-existing untracked paths
(`.planning/debug/m3-producer-unbounded-dense-read.md`, `results*`, `targeted_rerun_*`, …) and
`git log --oneline -1` exactly one new commit. **Do not push.**

⚠ **If `git commit` fails with `invalid object` / `Error building trees`** — the known GPFS
loose-object loss. Recipe from `.planning/HANDOFF.json` (`gpfs_object_store_recovery_recipe`):
for each `git ls-files -s` entry test `git cat-file -e <sha>`; for misses re-hash the intact
working-tree file via `git hash-object -w <path>`; then commit. The recipe normally says push —
**this task is NO PUSH, so flag to Carter instead.** Never work around it with `git add -A`.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
git status --porcelain -- src tests               # MUST be empty
git status --porcelain -- .planning/amendments/   # MUST be empty
cmp <(head -531 .planning/osf_deviations.md) "$SCRATCH/osf_head531.orig" && echo "G-02 GREEN"
python3 "$SCRATCH/guard.py" .planning/osf_deviations.md \
  .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md \
  .planning/HANDOFF.json "$SCRATCH/STATE.live"    # ALL zero, exit 0
# G-16 superseded Fisher-z sweep across the artifact set
grep -rn "0\.435\|\[-0\.280, +0\.563\]\|\[-0\.581, +0\.255\]" \
  .planning/osf_deviations.md \
  .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md | wc -l   # expect 0
# G-15 convention string present in BOTH the disclosure entry and the courier
grep -c "1.03/sqrt(n-3)" .planning/osf_deviations.md \
  .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md   # each >=1
git log --oneline -1
git status --porcelain | grep -c "^ M\|^M "       # expect 0
    </automated>
  </verify>
  <done>All sixteen guards GREEN on the real tree and every negative control observed RED — including G-05 on the line-wrapped and bolded forms; the frozen prefix proven identical by `cmp`; SUMMARY written with the F-6 adjudication and the F-7 deviation recorded; exactly one commit on `m3-W2-aou-deltas`; `src`/`tests`/`amendments` clean; pre-existing untracked paths still untracked; nothing pushed.</done>
</task>

</tasks>

<commit_message>
Use exactly this, via `git commit -F <file>` (the body contains characters a shell `-m` chain
will mangle):

```
docs(quick-260904-dgi): correct the tail disclosure after a 5-reviewer adversarial review — 5 blockers and 6 highs, fixed AT SOURCE and re-spliced, still DRAFTED — NOT POSTED

A 5-reviewer adversarial review (Codex CLI + 4 blind investigators) of the 2026-09-03 tail
disclosure found 5 blocker-level and 6 high-level false or overclaimed statements. This
commit corrects them in the disclosure, in the courier record, and in the live-state files.
Nothing is posted. No OSF contact, no Seth contact, no VM, $0.

A1 (BLOCKER) — EVERY mk7ze line citation was WRONG: they cited repo-draft lines of a 598-line
DRAFT file, not the 333-line posted body. Proven, not asserted: repo lines 168-500 reproduce
mk7ze's exact OSF md5 13a49f543cabcc27ce9f1e589783c060, 22,945 B, 333 lines, so posted =
repo - 167. "line 275" -> mk7ze line 108; "clause (a) at line 467" -> mk7ze line 300 (467
DOES NOT EXIST in 333 lines); "the 598-line posted body" -> the 333-line posted body. Both
forms are now cited so a reader can check either. The silence sweep's CONCLUSION is
unaffected — zero hits over the superset implies zero over the subset — but the sentence
stated a false fact about what was posted.

A2 (BLOCKER) — the registered prediction was FALSIFIED by data we already held. It claimed
residual undefined-r EXCLUSIVELY at negative offsets; m2_region_00057 carries a POSITIVE
offset case (chr15:20394741:AT:A span_end 20394742 x chr15:20394743:T:C, one base past the
span end, downstream, un-occluded, measured 2026-08-24) and our own STATE.md:287 already
concluded the residual class sits adjacent to the REF span on EITHER side. The prediction is
now explicitly SAMPLE-SCOPED, names the known out-of-sample counterexample, and says
production tests the rate on both sides.

A3 (BLOCKER) — the claim that non-independence cannot create dispersion is FALSE. The 0.98
simulation tested BETWEEN-window duplication, which provably cannot inflate E[chi2/dof] and
was guaranteed to return ~1.0 before it ran. The operative dependence is WITHIN-window: pairs
sharing an occluding deletion do not flip independently, and 22.9% of tail pairs are
deletion-deletion neighbours by this record's own measurement. An average of two co-moving
pairs per occluding deletion reproduces the observed 1.99 EXACTLY with ZERO parent-rate
heterogeneity. The pairs-per-deletion distribution HAS NOT BEEN MEASURED, so Finding 2's
magnitude is NOT yet attributable. Deleted: the claim that this was stronger than an
unexamined null because both artifact explanations were eliminated — one was eliminated; the
more plausible one was never tested.

A4 (BLOCKER) — the heterogeneity magnitude is UNIDENTIFIED. The bare 1.99x now carries its
95% CI (~1.1-4.2), and discloses that under the more conservative drop-both-chr15-windows
treatment the estimate is 1.52 at p 0.073 — NOT significant. Robust in DIRECTION, poorly
determined in MAGNITUDE, and its significance is not robust to the choice of overlap
correction.

A5 (BLOCKER) — the leave-one-out did not rule out an influential unit. The window-level LOO
CANNOT remove parent 00060 (its two windows shield each other) and its minimum, 1.988, IS the
headline — it reported the same deletion twice as independent corroboration. Replaced with a
leave-one-PARENT-out over the 19 distinct parents: 1.52-2.49, worst-case p 0.073. Parent
00060 is influential enough that its removal renders the heterogeneity non-significant at
alpha 0.05.

A6 (BLOCKER) — the claim that the downstream predicate is complete in its own direction was
overclaimed from n=1, and the scanner's own docstring (pairwise_completeness_scan.py:40-45)
says n=1 supplies neither prevalence, boundary width, nor one-sidedness. Restated as support
for a prospective falsification check, not proof of predicate completeness.

A7-A11 (HIGH) — the negative result becomes an UNDERPOWERED NULL (at n=21 the design has 80%
power only for |rho| >~ 0.61 and 24% power at rho 0.30, so it excludes only STRONG
correlates, and |rho| up to 0.446 sits inside the interval for the cleanest of them), and the rho=+0.886 comparison is disclosed as a count against its own exposure
that does not calibrate power for a size-normalized rate. The rho +0.173 independence claim
becomes "no association DETECTED", with our own inversion recorded against us: we steered
from the 2x2 (p 0.088) to the rho (p 0.45) while lecturing about absence of evidence — the
correction was itself an absence-of-evidence error. The blanket claim that mk7ze says nothing
at all is narrowed (it DOES retain a raw-panel NaN-raise contract at posted :321-322). The
silence sweep gained the word it missed: "undefined" occurs EXACTLY ONCE in the posted body,
at mk7ze line 82 — a DIRECTIONAL claim running the other way from the tail finding, so not
falsified, but disclosed as swept rather than silently omitted. "(recorded as pre-registered
here)" is withdrawn: the entry is DRAFTED — NOT POSTED and the prediction is post hoc
relative to the 21-region scan.

A12-A13 — two adopted scoping repairs that STRENGTHEN the mk7ze scope argument: the sentence's
own drafting record (fire-morning-occlusion-oracle-vs-geometry.md:227-233) stated the
conclusion BROADLY, and region-1 pair 4 is a NaN pair with geometry `disjoint` — no covering
deletion, documented BEFORE posting and deliberately excluded from the 5-member expectation
set. That converts "the narrow reading is grammatically available" into "the narrow reading
is what the expectation set was actually built on." Plus a 40,000-resample permutation test
(p 0.0072), with the caveat that it permutes PAIRS and so validates the asymptotics, NOT the
independence assumption at issue in the clustering caveat.

PART B — the courier carries the same claims, and the 0.0005 correction had OVERSHOT. The
constants are distinct live parameters with no runtime coupling, but they are NOT unrelated:
mk7ze itself records that the occlusion gate reused "the same fractional gate as the
withdrawn ceiling, re-purposed to exclusions", so the shared value has a documented COMMON
ORIGIN. The original action item was wrong to call it a live contradiction; the first
correction overshot in the other direction. Fixed AT SOURCE in 260902-vsp's CONTENT-SPEC.md
and RE-SPLICED BY SCRIPT into the verbatim appendix, then re-verified byte-equal and
re-anchored — no supersession note.

PART C — repo hygiene. C1 turned out to be FIVE pin sites, not two: HANDOFF.json escaped
260903-ict's guard because it is not a .md file, and .continue-here.md escaped because it
writes the md5 truncated. Both were two generations stale. All five now carry the MEASURED
post-task value. C2 corrects a "CLOSED — do not re-open" declaration that enumerated 3 of 5
sites. C3 adds an AS-OF qualifier to a STATE.md 0-hit claim that its own commit falsified —
9ce807f introduced four of the six terms it declared absent. C4 marks repo fixes 1 and 2 DONE
with only the two-file tcujq docstring defect still queued. C5 adds a dated SUPERSEDED clause
to the 260902-vsp log without rewriting its historical description.

PART D — queued, NOT executed: measure the pairs-per-deletion distribution in the tail from
pcs_tail_verdicts.tsv (already on the VM; reads the emitted TSV only, no re-run, no
genotypes). This DECIDES whether the observed overdispersion is parent-region heterogeneity
or a within-window cluster design effect. CARTER FIRES, never an agent.

RECORDED DEVIATION — CONTENT-SPEC IS WRONG ON THREE CONFIDENCE INTERVALS AND WAS NOT COPIED.
The spec's A7/A8 quoted Fisher-z intervals (SE = 1/sqrt(n-3)) beside a Bonett-Wright bound
(0.446) drawn from the statistical audit — one sentence, two conventions, which is how a value
outside its own stated interval got in. Adjudicated by Carter: use BONETT-WRIGHT throughout,
because these are rank correlations, plain Fisher-z is the Pearson formula, and Bonett-Wright is
both the standard Spearman interval and the WIDER one — the conservative direction for a
correction whose subject is overclaiming. Superseded and NOT copied:

  rho +0.004   spec [-0.428, +0.435]   ->  used [-0.440, +0.446]
  rho +0.173   spec [-0.280, +0.563]   ->  used [-0.292, +0.572]
  rho -0.199   spec [-0.581, +0.255]   ->  used [-0.590, +0.267]
  rho -0.201   spec [-0.59,  +0.27 ]   ->  used [-0.591, +0.266]

All four were re-derived here and reproduce under tanh(atanh(rho) +/- 1.96*1.03/sqrt(18)); they
are used because they were independently checked, not because they were supplied. One supplied
digit did NOT reproduce — the -0.199 upper bound measures 0.26747718, which rounds to 0.267 and
not 0.268, matching the audit's own reported value — and it was confirmed rather than silently
reconciled. Because the interval widens, "|rho| up to 0.446 is inside this CI" turned out to be
correct and was retained: the clause that exposed the conflict was the surviving-correct half.

THE ACTUAL FIX IS NAMING THE CONVENTION. Every Spearman CI in the disclosure and the courier now
carries "95% CI, Fisher z with the Bonett-Wright Spearman standard error 1.03/sqrt(n-3)" inline,
enforced by a presence guard. An unnamed convention is what let two of them into one sentence,
and a referee can now reproduce the interval rather than guess at it.

Method notes. Two of the banned phrases were INVISIBLE to a literal grep in the exact files
they had to be removed from: the own-direction completeness claim is line-wrapped in
osf_deviations.md, and the dispersion claim is markdown-bolded in the courier. All
banned-phrase guards therefore run on a normalized stream (markdown stripped, whitespace
collapsed across newlines, lowercased), and the normalizer was proven to find both hits a
literal grep misses before any edit was made. The mk7ze line citations could not be banned
outright — A1 requires citing both forms — so they are guarded by a counting identity
(count("line 467") == count("repo draft line 467")), which is strictly stronger than a
substring ban. Guards are scoped to record-directories, never to the correction's own prose;
within the guard file-set the construction rule forbids the banned strings outright.

osf_deviations.md lines 1-531 are byte-identical, proven by cmp — the pre-registration chain
above the edited entry did not move. src/ and tests/ UNTOUCHED; the two-file tcujq docstring
defect remains DEFERRED. Not pushed.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```
</commit_message>
