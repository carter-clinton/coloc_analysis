# Deferred items — quick-260903-ict

Recorded, **not fixed here**. Each entry states what would discharge it.

---

## 1. The withdrawn-policy docstring defect — **TWO files**, not one (plan F-4)

**Status:** DEFERRED. Touches `src/`, and this task is DOCS-ONLY
(`git status --porcelain -- src tests` EMPTY at commit time).

**What is wrong.** Two modules label the NaN→0 zeroing ceiling as *pre-registered*, citing an
amendment that a later posted update **withdrew**:

| file | lines | what it says |
|---|---|---|
| `src/python/condition_ld_matrix.py` | `:4`, `:153` | cites `osf-amendment-afr-native-ld-nan-psd-2026-07-03.md` (OSF `tcujq`) as **PRE-REGISTERING** the NaN→0 policy |
| `src/python/write_conditioned_ld_npz.py` | `:4`, `:17`, `:85` | calls the same ceiling **"pre-registered"** |

`.planning/osf_deviations.md:133` and `:166` record that the 2026-07-10 update (OSF `trsx5`)
**withdraws exactly that policy**.

**Accurate label:** *"parameter of a withdrawn policy, retained in a frozen module, not called in
production."*

**⚠ This is NOT the same thing as the `0.0005` claim this task corrected.** The `0.0005`
"contradiction" was FALSE — two unrelated constants. This defect is REAL and separate: it is a
withdrawn-vs-pre-registered **labelling** error, not a value conflict.

**Discharge:** one task that fixes **both** files **plus a named enforcer test**. An edit alone is
not enough — a claimed invariant with no named enforcer is belief only, and this repo has already
been bitten by pin claims that nothing enforced. The enforcer must be seen RED before it is
trusted, and must pin behaviour (import/AST/exit code), not source text: a grep gate matches text,
not meaning.

---

## 2. Four missing STATE.md quick-task rows

`260828-uej`, `260831-kw8`, `260901-l55`, `260901-rvu` have no `### Quick Tasks Completed` row.

Carried forward from `260902-vsp`'s `deferred-items.md`. **Out of scope by explicit instruction**
(this task's hard constraint 7: append ONE row, for `260903-ict`, and do NOT backfill).

**Discharge:** a separate STATE-hygiene task that appends the four rows from their own SUMMARYs.

---

## 3. F-3a is **CLOSED**, not deferred — recorded so it is not re-opened

The courier's splice-source pin was refreshed by this task (Task 3), because Task 2 moved the
source anyway. Both places that pinned it now carry the true post-task values:

- courier line **23** — `619426a0157d199c711a4d771023330a`, 11747 B, 173 lines
- courier line **34** — "the **11747**-B one" (this second pin was **not named in the plan**; it was
  found during execution, was already stale from `ee3af4b` at `10672`, and was refreshed for the
  same reason as line 23: a pin whose subject has moved is a false invariant)

`.planning/STATE.md:45`'s courier pin was likewise refreshed to `c8525e2665e98cfa9d3d0f1c4266429d`,
542 lines.

**Nothing to do. Do not re-open.**

---

## 4. Residual, recorded rather than silently left: the plan's stated pre-fix appendix byte count

The plan's Task 1C states the pre-fix appendix region is **10427 B**, sha256 `3a8371b0…`.
Measured in this executor's shell: **10472 B**, sha256
`3a8371b08a78f7b22d9173a297aaa40b50def6144c4cf55c54599ff0571dcfa8`.

The **sha256 prefix matches exactly**, and the byte-equality assertion (appendix region == source
`## ARTIFACTS`→EOF) returned **True**, so the region hashed by the planner and the region extracted
here are the same bytes. `10427` is a digit transposition of `10472` in the plan's prose only.

Not reconciled silently: recorded here and in the SUMMARY. Nothing downstream depends on it — Task
4 superseded that anchor with `11490 B` / `3a26095e…`.

**Discharge:** none required; it is a plan-prose typo, not a tree fact.
