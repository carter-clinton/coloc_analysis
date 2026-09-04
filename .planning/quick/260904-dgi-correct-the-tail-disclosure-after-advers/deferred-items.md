# Deferred items — quick-260904-dgi

Recorded, **not fixed here**. Each entry states what would discharge it.

---

## 1. ⭐ PART D — MEASURE the pairs-per-deletion distribution in the tail (THIS DECIDES A3)

**Status:** QUEUED, NOT EXECUTED. ⛔ **CARTER FIRES. NEVER AN AGENT.**

> **MEASURE the pairs-per-deletion distribution in the tail** from
> `/home/jupyter/occ_measure/pcs_tail_verdicts.tsv` (already on the VM; **no re-run, no
> genotypes** — reads the emitted TSV only). Group tail rows by `del_vid` and report the
> cluster-size distribution. Design effect ≈ `1 + (c−1)·ICC`. **THIS DECIDES** whether the
> observed overdispersion is parent-region heterogeneity or a within-window cluster effect.
> **Until measured, Finding 2's magnitude is NOT attributable.**

**Why it is load-bearing.** `260904-dgi` withdrew the claim that non-independence cannot create
dispersion. The simulation that was cited tested **BETWEEN-window** duplication, which provably
cannot inflate `E[chi2/dof]`. The operative dependence is **WITHIN-window**, and an average of
**two co-moving pairs per occluding deletion reproduces the observed 1.99 exactly with ZERO
parent-rate heterogeneity**. The structure is known to be present — **22.9%** of tail pairs are
deletion-deletion neighbours (**564 of 2461**) — but its *cluster-size distribution* has never
been measured, so the two explanations are not yet distinguished.

**Discharge:** one measurement, then restate Finding 2's magnitude in `osf_deviations.md` §(2)
and §(7) and in the courier, either attributing the dispersion or reporting the design-effect
correction. No code change is required to obtain it.

---

## 2. The withdrawn-policy docstring defect — **TWO files** (`tcujq`), still DEFERRED

**Status:** DEFERRED, unchanged by this task. **Touches `src/`; this task is DOCS-ONLY**
(`git status --porcelain -- src tests` EMPTY at commit time).

| file | lines | what it says |
|---|---|---|
| `src/python/condition_ld_matrix.py` | `:4`, `:153` | cites `osf-amendment-afr-native-ld-nan-psd-2026-07-03.md` (OSF `tcujq`) as **PRE-REGISTERING** the NaN→0 policy |
| `src/python/write_conditioned_ld_npz.py` | `:4`, `:17`, `:85` | calls the same ceiling **"pre-registered"** |

`.planning/osf_deviations.md:133`/`:166` record that the 2026-07-10 update (OSF `trsx5`)
**withdraws exactly that policy**. Accurate label: *"parameter of a withdrawn policy, retained in
a frozen module, not called in production."*

**Discharge:** one task fixing **both** files **plus a named enforcer test seen RED first**. An
edit alone is a belief; a test that has been observed failing is a guard.

⚠ It is now the **ONLY** outstanding item of the original three repo fixes — items 1 and 2 were
completed by `260903-ict`. `.planning/HANDOFF.json`'s key was renamed from
`three_repo_fixes_QUEUED_NOT_DONE` to `repo_fixes_status` by this task to stop asserting
otherwise.

---

## 3. The four missing STATE.md quick-task rows

`260828-uej`, `260831-kw8`, `260901-l55`, `260901-rvu` have no row in
`.planning/STATE.md`'s Quick Tasks Completed table. **Out of scope by this task's hard
constraint 9** and deliberately NOT backfilled.

**Discharge:** a separate quick that writes each row from that task's own SUMMARY.

---

## 4. F-6 — the Spearman CI convention: what was decided, by whom, and what the alternative was

**Decided, not deferred.** Recorded here because a convention that is not written down is how
the defect happened in the first place.

**The conflict.** `260904-dgi`'s own `CONTENT-SPEC.md` (A7, line 108) quoted the CI for
`rho +0.004` as `[-0.428, +0.435]` while asserting in the same clause that *"|rho| up to 0.446 is
INSIDE this CI"*. `0.446 > 0.435`. Measured diagnosis: `[-0.428, +0.435]` is **Fisher-z**
(`SE = 1/sqrt(n-3)`, the Pearson formula) and `0.446` is **Bonett-Wright**
(`SE = 1.03/sqrt(n-3)`). One sentence, two conventions.

**Adjudication — Carter, 2026-09-04: BONETT-WRIGHT throughout.** These are rank correlations, so
plain Fisher-z is the wrong formula; Bonett-Wright is the standard Spearman interval; and it is
the **WIDER** interval, which is the conservative direction for a correction whose entire subject
is overclaiming.

**The alternative exists and is named so this is not re-litigated silently:** plain Fisher-z is
narrower and is what the spec carried. If a future reader prefers it, the change must be made
**everywhere at once and named inline**, never mixed.

**The actual fix was naming it.** Every Spearman CI in the disclosure and the courier now carries
*"95% CI, Fisher z with the Bonett-Wright Spearman standard error 1.03/sqrt(n-3)"* inline, so a
referee can reproduce the interval. The numbers alone were never the bug.

---

## 5. F-7 / C6 — the planner-added scope, and its disposition

**DONE, not dropped.** `CONTENT-SPEC.md` PART C named five hygiene items and did **not** name the
live-state files. Measurement showed `.planning/HANDOFF.json` and `.planning/STATE.md`'s live
block carried **the same refuted claims** PART A removes, and those are the files a resuming
session reads first.

Corrected in place (they are current-state files, not historical logs). Executed with **two sites
beyond the plan's enumeration**, both found by the guard rather than by reading:
`seth_round2_outcome_2026_09_03.leave_one_out_STANDS` (the A5 claim) and `do_not[6]`
(*"DO register the negative result"*, the A7 claim).

⚠ **The historical log rows were deliberately NOT touched** — `STATE.md`'s Quick Tasks table
(including the `260903-ict` row at `:2354`) describes what past tasks did. Rewriting it would
falsify the log, which is the same reason C5 uses a dated SUPERSEDED clause instead of an edit.
