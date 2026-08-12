---
phase: quick/260811-tf3
plan: 01
subsystem: decision-record
tags: [e2, sr4, decisions, handoff, disclosure, track-a, id-vs-ref-ld, m3, docs-only]
baseline_rev: 0e7e309
branch: m3-W2-aou-deltas
requires:
  - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/ (the two draft framings + their green harness)
  - .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md (the SR4 evidence)
provides:
  - DEC-2026-08-11-e2-framing-correction (E-2 obligation (3) DISCHARGED)
  - DEC-2026-08-11-sr4-disposition (SR4-OPEN answered NEVER ACTUALLY FROZEN)
  - a paste-ready SELECTED PAIR proven byte-identical to its oku sources
affects:
  - .planning/DECISIONS.md
  - .planning/HANDOFF.json
  - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
tech-stack:
  added: []
  patterns: [red-first clause harness, fixture-only negative controls, structural JSON containment walker, machine-splice extraction with cmp proof]
key-files:
  created:
    - .planning/quick/260811-tf3-record-carter-decisions-e-2-framing-b-co/260811-tf3-check.sh
    - .planning/quick/260811-tf3-record-carter-decisions-e-2-framing-b-co/260811-tf3-SELECTED-PAIR-correction.md
  modified:
    - .planning/DECISIONS.md
    - .planning/HANDOFF.json
    - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
decisions:
  - E-2 is framed as B (CORRECTION); the matched pair ms-correction + osf-correction is selected; obligation (3) DISCHARGED, (1) and (2) remain Carter's external actions
  - SR4-OPEN is answered NEVER ACTUALLY FROZEN; the handoff language is corrected, no drift review, NO NEW PIN created
metrics:
  tasks: 3
  commits: 3
  clauses: 25
  negative_controls_observed_red: 13
  files_changed: 6
  completed: 2026-08-11
---

# Quick 260811-tf3: Record Carter's two 2026-08-11 decisions — Summary

Carter's two in-session decisions of 2026-08-11 now exist on all three surfaces
the resume path reads, recorded behind a red-first clause harness whose every
gate was observed failing on a fixture copy before it was trusted green.

## The two decisions, as landed

| DEC id | Landed at | One-line decision |
|---|---|---|
| `DEC-2026-08-11-e2-framing-correction` | `.planning/DECISIONS.md:1252` | E-2's disclosure is framed as **B — CORRECTION**, selecting the matched pair `ms-correction` + `osf-correction`; this **discharges obligation (3)** of `DEC-2026-08-07-e2-orientation-disposition`, while (1) manuscript placement and (2) OSF posting remain Carter's external actions. |
| `DEC-2026-08-11-sr4-disposition` | `.planning/DECISIONS.md:1374` | SR4-OPEN is answered **NEVER ACTUALLY FROZEN**; the handoff's "frozen/pinned at `bf16289`" language was wrong and is corrected, not defended. No drift review, and **no new pin** is created. |

Both entries carry the delegation instruction verbatim, the axis guard (framing B
is **not** disposition option B — the code is still not changed), the
journal-policy **pre-placement verification step**, and, for SR4, **both**
contrary-evidence caveats stated rather than smoothed.

## Commits

| Task | Commit | What landed |
|---|---|---|
| 1 | `b18c730` | `dec` clause group + the two appended `DECISIONS.md` entries (and the PLAN.md, previously uncommitted) |
| 2 | `afd78f2` | `handoff` clause group + `HANDOFF.json` (2 array entries) + `deferred-items.md` (3 insertions) |
| 3 | `960d911` | `pair` clause group + the machine-spliced SELECTED-PAIR file |

## RED-first accounting

Every group was written and **observed failing** before its edit existed. The
plan required this; the numbers below are what was observed, not what was
expected.

| Group | Observed RED before the edit | Clauses that passed trivially at that point |
|---|---|---|
| `dec` | `DEC-03`, `DEC-04`, `DEC-05`, `DEC-06`, `DEC-07`, `DEC-08` — 6 FAILs | `DEC-01`, `DEC-02`, `DEC-09` — vacuous with nothing appended; reported as such, **not** counted as evidence |
| `handoff` | `HJ-03`, `HJ-04`, `HJ-06`, `HJ-07`, `HJ-08` — 5 FAILs | `HJ-01`, `HJ-02`, `HJ-05` — vacuous before the edits |
| `pair` | `SP-00` — file-absence as a **LOUD FAILURE**, not a skip | none |

### Negative controls — 13 observed red, 0 defeated, 0 too broad

All fixtures are COPIES under `mktemp -d`. No control ever mutated
`DECISIONS.md`, `HANDOFF.json` or `deferred-items.md`.

| Control | Fixture mutation | Fired |
|---|---|---|
| NC-D1 | one line deleted mid-baseline | `DEC-01` (byte prefix) |
| NC-D1b | same fixture | `DEC-02` (zero deleted lines) |
| NC-D2 | SR4 heading removed from the appended region | `DEC-03` |
| NC-D3 | journal-policy lines removed from the appended region | `DEC-05` **ALONE** ✅ |
| NC-H1 | final `}` removed from a JSON **copy** | `HJ-01` (the parse gate) |
| NC-H2 | out-of-scope `.phase` mutated | `HJ-02`, naming `.phase` |
| NC-H3 | entry `[0]` rewritten instead of appended | `HJ-04` (prefix broken) |
| NC-H4 | one line deleted from `deferred-items.md` | `HJ-05` |
| NC-H5 | E-2 citation **moved** below the superseded `Logged:` line | `HJ-07` (177 vs 176) |
| NC-H6 | entry `[2]` prefixed with junk | `HJ-03` **ALONE** ✅ |
| NC-P1 | `18.41` → `1.841` inside the `ms-correction` block | `SP-02` at byte 596, line 8 |
| NC-P2 | journal-policy lines deleted | `SP-05` **ALONE** ✅ |
| NC-P3 | one `PASTE-END` marker removed | `SP-01` (and `SP-02`, as predicted) |

Positive controls (`NC-0`) green in all three groups: 9 / 8 / 8 clauses.

## Gate results, as measured

**Append-only — `.planning/DECISIONS.md`**
`git diff --numstat 0e7e309 HEAD` → **`252  0`**. Deletion column **0**. The
baseline also survives as a byte-exact prefix (`DEC-01`, `cmp` over the first
115,258 bytes).

**Insertions-only — `deferred-items.md`**
`git diff --numstat 0e7e309 HEAD` → **`99  0`**. Deletion column **0**. An
independent check in the insert script confirmed every original line still
present, in order (1,034 → 1,133 lines).

**JSON validity — `.planning/HANDOFF.json`**
`json.load` exits **0** under `smoke_dev/bin/python`. `HJ-01` green.

**Containment — `.planning/HANDOFF.json`**
The structural walker reports `DIFFERING PATHS` = exactly
`.carter_decisions_outstanding[0]` and `[2]`; **`OUT-OF-SCOPE PATHS: (none)`**.
Raw numstat is `2  2` — precisely two physical lines rewritten out of 132.
Entry `[0]` is a **pure append**: 971 → 2,577 chars with the baseline text
surviving as a byte-exact prefix. Entry `[2]` replaced: 544 → 2,590 chars.

**Byte identity — the SELECTED-PAIR file (`SP-02`, the load-bearing clause)**
Both bodies `cmp` **clean** against a fresh extraction taken at run time from the
read-only oku drafts with the same extractor the oku harness uses.
`ms-correction` = 15 lines / 1,180 bytes; `osf-correction` = 34 lines / 6,322
bytes — matching the plan's measured floors exactly. The file was built by
machine splice, never retyped.

**Inherited evidence** — `./260811-oku-check-drafts.sh` was re-run at execution
time and exited **0** (**29 PASS / 0 FAIL**, observed). That exit code is
recorded inside the SELECTED-PAIR file rather than copied from the plan.

**Final state:** full harness **25 clauses green** across all three groups;
`--self-test` **0 defeated / 0 too-broad** controls.
`git diff --name-only 0e7e309 HEAD` lists **exactly** the four allowed paths and
nothing else. `.planning/amendments/` and `results/` show **zero** modified
tracked files.

## Deviations from plan

### 1. [DISCLOSED IN PLAN — Rule 2] The SR4 banner insertion into `deferred-items.md`

The plan's Task 2 Step 3 flags this itself as "a deliberate, disclosed addition
beyond the literal content list". It was applied. Without it, `DECISIONS.md` and
`HANDOFF.json` would both say SR4-OPEN is decided while `deferred-items.md` —
the file the handoff *points readers to* — would still say *"THE QUESTION FOR
CARTER — not answered here."* It is a **pure insertion** of one blockquote; a
single-hunk revert if the orchestrator objects. The superseded `Status: OPEN`
line and the "QUESTION FOR CARTER" text are both preserved verbatim, and the
banner says on its face that they are superseded.

### 2. [Rule 1 - Bug] `HJ-03`'s prefix check was structurally incapable of its job

**Found during:** Task 2, on the first `--only handoff` run after the edits.
**Issue:** the clause tested the required prefix with `head -c 30` — 30 **bytes**
— but `✅ SR4-OPEN — DECIDED 2026-08-11` is **35 bytes** in UTF-8 (`✅` and `—`
are 3 bytes each). The clause truncated its own needle and went **RED against
correct data**.
**Fix:** replaced with `grep -q '^…'` anchored on the one-line entry, which is an
exact starts-with test. A byte-count prefix test on UTF-8 prose is the same
"structurally incapable assertion" class this project has been bitten by
repeatedly, so the repair got its own permanent negative control, **NC-H6**,
which prefixes entry `[2]` with junk while leaving every required token present —
so only the anchoring can be what fires. NC-H6 was **observed red, alone**.
**Commit:** `afd78f2`.

### 3. [Rule 1 - Bug] The one-line fold did not squeeze whitespace

**Found during:** Task 1, pre-append lint of the entry text.
**Issue:** `tr '\n' ' '` alone folds a phrase wrapped as `**negative\n  control**`
into `**negative   control**` — three spaces — so a clause searching for
`negative control` silently never matches. **Measured:** the `DEC-08` term was
found **0** times before the fix and **1** time after.
**Fix:** `fold_region()` now also squeezes whitespace runs, and the header
documents why the squeeze is load-bearing rather than cosmetic.
**Commit:** `b18c730`.

### 4. [Process, no outcome difference] All three clause groups were authored in Task 1

The plan sequences Tasks 2 and 3 as *extending* the harness. All three groups
were instead written up front in Task 1. The substantive requirement is
unaffected and was preserved exactly: each group was still run and **observed
RED before its own edit existed** (`--only handoff` before the Task 2 edits;
`--only pair` before the file existed). Noted for accuracy, not as a shortcut.

### 5. [Execution note] A scratch-script assertion crashed after writing HANDOFF.json

A leftover no-op assertion in my scratch edit script raised **after** the file
had already been written. Rather than re-run — which would have **double-appended**
to entry `[0]` — `HANDOFF.json` was restored with `git checkout`, confirmed
byte-identical to baseline (empty numstat), the assertion removed, and the edit
re-applied from clean. No repo artifact was affected.

## Deferred, disclosed rather than silently absorbed

Both were named in the plan's `<explicitly_out_of_scope>` and are **not** fixed
here.

1. **`HANDOFF.json`'s `status`, `headline` and `wave` strings are deliberately
   stale.** They still describe SR4-OPEN as outstanding and the E-2 obligations
   as three-undischarged. They are byte-identical to baseline because the
   constraint was "targeted edits to the two `carter_decisions_outstanding`
   entries; preserve every other byte", and `HJ-02` mechanically enforces exactly
   that — those fields differing would have **failed** the containment gate. The
   next session-close refresh should pick them up.
2. **`.planning/STATE.md:15` and `.planning/ROADMAP.md:1077`** still assert
   `ld_npz_to_rds.R` is frozen/unchanged when it is **+313 / −62**. Out of write
   scope here; registered as the named follow-up inside
   `DEC-2026-08-11-sr4-disposition` and inside `HANDOFF.json`'s new entry `[2]`,
   so it cannot be lost. ⚠ The dated historical `>` blocks are **NOT** correction
   sites and were left alone deliberately.

## What did NOT happen

Nothing was posted to OSF. No manuscript file was created, opened or touched. No
posted OSF amendment body was edited or re-posted. No source-freeze pin was added
— `PY_FROZEN_RELS` and `tests/m3/test_source_freeze_pins.py` are untouched.
Obligations (1) and (2) discharge **only** by Carter's external actions, and
every artifact written here says so on its face (`SP-04`, `SP-08` assert it).

## Invariants and their enforcers

Per `[[feedback_a_claimed_invariant_needs_a_named_enforcer]]`, each claim above
is paired with the thing that fails when it breaks. Nothing here is asserted on
belief.

| Invariant | Named enforcer |
|---|---|
| `DECISIONS.md` is append-only vs `0e7e309` | `260811-tf3-check.sh` `DEC-01` (byte prefix) + `DEC-02` (zero `^<`) |
| `HANDOFF.json` stays parseable | `HJ-01` |
| Only `[0]` and `[2]` changed in `HANDOFF.json` | `HJ-02` containment walker |
| `[0]` was appended, not rewritten | `HJ-04` prefix check |
| `deferred-items.md` deleted nothing | `HJ-05` |
| The dispositions sit adjacent to what they supersede | `HJ-07`, `HJ-08` (line-order clauses) |
| The paste bodies are verbatim | `SP-02` `cmp` vs a fresh extraction |
| The baseline cannot silently move | `BG-01` / `BG-02`, which exit 3 rather than re-pin |

⚠ **Scope limit of the enforcers.** They run only when someone runs
`260811-tf3-check.sh`; nothing in CI invokes it. They are a task-local acceptance
harness, not a standing repository gate — stated so no future reader mistakes
them for one.
