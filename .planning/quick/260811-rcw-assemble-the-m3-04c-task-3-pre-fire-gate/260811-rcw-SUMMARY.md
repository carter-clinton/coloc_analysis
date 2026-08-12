---
phase: quick/260811-rcw
plan: 01
subsystem: m3-04c-pre-fire-gate
tags: [m3, m3-04c, pre-fire, gate-review, aou, ld-panel, evidence, docs-only]
anchor_commit: c4dc410
commits:
  - 5bd21b9  # T1 -- evidence.log (verbatim) + evidence.tsv, 20 checks
  - 4b2a754  # T2 -- the PRE-FIRE GATE REVIEW, seven sections
  - 50f4950  # T3 -- reconciliation, 7 defects fixed
requires:
  - phase: m3-aou-afr-ld-panel-build
    provides: "m3-04c Task 3 (PLAN :1302-1536), m3-04c-BLAST-RADIUS.md, HANDOFF.json 2026-08-07, the aou-ld-pipeline skill"
provides:
  - "260811-rcw-PRE-FIRE-GATE-REVIEW.md -- the single current-state surface Carter reads before deciding whether to fire"
  - "260811-rcw-evidence.log -- 20 verbatim check blocks + 3 context blocks, every command with its real output and rc"
  - "260811-rcw-evidence.tsv -- 8 columns x 20 rows, machine-readable, every command traceable to a `$ ` line in the log"
affects: [m3-04c-task-3, aou-ld-fire, e-2, sr4-open, blocker-d]
tech-stack:
  added: []
  patterns:
    - "the TSV's `command` column is EXTRACTED from the log's `$ ` line, so a row cannot claim a command the log does not contain"
    - "CONTEXT-* log blocks carry supporting evidence without polluting the checked-count invariant"
    - "enumeration counts are scoped to the sections they describe, so the record-of-the-count is not a subject of the count"
key-files:
  created:
    - .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.log
    - .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.tsv
    - .planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md
  modified: []
decisions:
  - "NONE RECORDED. This task verifies and collates; it fires nothing, decides nothing, authorizes nothing. Every disposition remains Carter's."
metrics:
  duration: "~75 min"
  completed: 2026-08-11
  checks: "20 of 20 PASS, 0 FAIL, 0 RED"
  cost: "$0, NC State only, ZERO perimeter contact, zero LSF"
---

# quick/260811-rcw: m3-04c Task 3 PRE-FIRE GATE REVIEW Summary

**Carter can now open ONE file and see what is green, what is his to check in-perimeter, what is
his to decide, and what the fire's outputs will and will not be usable for — with every local
number traceable to a command whose real output sits beside it, and every seam between the four
layered records shown rather than merged.**

---

## The verdict as shipped

> **VERDICT:** All agent-verifiable preconditions GREEN as of 2026-08-11 at c4dc410; every remaining item is Carter's gate-time check or Carter's decision.

Anchored to commit **`c4dc410`** (2026-08-11 19:52:46 -0400), branch `m3-W2-aou-deltas` (`L-01`).
The line is **derived, not asserted**: all 20 rows of `260811-rcw-evidence.tsv` carry verdict
`PASS`, which is the condition the plan attaches to the GREEN form. Had any row been non-PASS the
NOT-READY form would have shipped instead, naming each failing `check_id`.

**It covers the agent-verifiable preconditions ONLY.** It says nothing about the perimeter facts
(§4), the PRE-FIRE decisions (§5), or the open items that bound usage (§6). **It is not a
recommendation to fire.**

## Suite results as observed

| Suite | Observed | Baseline (HANDOFF `suite_baselines`, 2026-08-07) | Skip rule |
|---|---|---|---|
| `tests/m3` (`L-03`) | **902 passed / 31 skipped / 0 failed** in 927.71s (0:15:27) | 902 / 31 / 0 | **HELD — exactly 31** |
| `tests/phase2` (`L-04`) | **136 passed / 1 skipped / 0 failed** in 1.85s | 136 / 1 / 0 | **HELD — exactly 1** |

**No count moved**, so no reconciliation against the intervening commits was owed. It was
performed anyway as supporting context: the range `b02707a..HEAD` is **15 commits, all under
`.planning/`, touching 0 files under `src/`, `tests/`, `config/` or `Snakefile`** (log blocks
`CONTEXT-A`, `CONTEXT-B`) — which is what a docs-only arc should look like, and is why a moved
passed-count would have been a loud FAIL rather than a number to adopt.

**The `tests/m3` suite ran EXACTLY ONCE** across the whole plan — provable: the log contains
exactly **1** line matching `^\$ .*-m pytest tests/m3 -q$`. (`L-13` and `L-14` are single-FILE
invocations the plan mandates separately, not re-runs.)

## Non-PASS checks

**NONE. 20 of 20 PASS, 0 FAIL, 0 RED.** No RED block appears in the review because the evidence
did not produce one. Notably: the four **behavioural** read-path tests all **RAN** rather than
skipped (rolled call by name in §3), which is the check that would have exposed a green-looking
suite with its only behavioural assertions silently skipped.

## Divergences found between the layered records, and how each was resolved

Resolved **by recency**, with the winner named and the seam shown. The plan enumerated four; the
reconciliation found **four more**.

| # | Divergence | Winner |
|---|---|---|
| 1 | HANDOFF's frozen narrative rows (`panel_reachability` "⛔ OPEN", `blocker1_ld_read_path` "NOT YET IMPLEMENTED", 2026-08-04/05) vs **its own** `blast_radius_gate_ledger` + `blocker_a/c` CLOSED (2026-08-07) | The 2026-08-07 ledger — **and corroborated by measurement**: `L-11`/`L-12`/`L-13`/`L-14` show the remedy implemented and enforced. "NOT YET IMPLEMENTED" is false today |
| 2 | HANDOFF `gates.m3_04c` "548P/31S/0F" vs **its own** `suite_baselines` 902/31/0 | `suite_baselines` — corroborated exactly by `L-03` |
| 3 | The skill's Wave-2 table describes the **KILLED** Hail A.3 producer (CR-01, the lowering hang, "322 cells", "44 egress bundles", 161×2 regions) | **Split by row.** GATE 2/3 SUPERSEDED by `run_native_ld_panel.py` (native plink, AFR-only, **276** regions per `L-17`, egress ≤22 groups); **GATE 0 / GATE 1 / GATE 1.5 remain LIVE AND VALID** and were not discarded |
| 4 | Blast radius's fire row (blocked by A/C/D) vs HANDOFF's ledger (A/B/C CLEAR, D PARTIAL) | HANDOFF (2026-08-07) |
| 5 **(new)** | BLOCKER-D magnitudes: blast radius 45.6 GB–1.1 TB vs HANDOFF 22.8/67.3/~553 GB | HANDOFF — **and the seam explained**: re-derived, the two sets differ by exactly the float64→float32 factor of 2. **Same regions, not disagreeing measurements** |
| 6 **(new)** | The m3-04c PLAN's own acceptance criterion (`:1518`) names `m2_region_00040__sub00` for SH2B3; the shipped crosswalk says `__sub14` (`L-18`) | The shipped crosswalk — `__sub00` is the **66 Mb off-target** id the 2026-08-05b replan corrected |
| 7 **(new)** | PLAN cites `allow_degraded` at `config/pipeline.yaml:266`; measured it is at `:295` | The measured tree (value unchanged: `False`) |
| 8 **(new)** | **The older records' line numbers have drifted as a CLASS**, including the SuSiE quality gate STEP A sends Carter to read (PLAN `:184`, blast radius `:216` → measured **`:500`**) | The measured tree at `c4dc410`. Every line number in the review was re-anchored before it was written |

## Reconciliation log (Task 3) — what was wrong and what it now says

**Seven defects found and fixed.** The pass was not a formality.

1. **A wrong number in the reader-facing table.** `L-06` "928 lines" → **"926 output lines, of
   which 148 are rule names"**. Cause: an off-by-one in my own throwaway `awk`. Corrected in
   **both** the review and the TSV.
2. **The SuSiE quality-gate line — the one STEP A sends Carter to read.** `run_susie_rss.R:184`
   (PLAN) / `:216` (blast radius) → **`:500`**, thresholds loaded `:713-716`.
3. **`provenance_source` scalar assignment.** `assemble_occlusion_catalog.py:202` → **`:230`**.
4. **The GRCh38 varid citation** (what makes degraded reconstruction recoverable).
   `run_native_ld_panel.py:391-400` → **`:507`**.
5. **The `gs://` upload set** (the proof the manifest is not uploaded). `:922-938` → **`:922`
   (`if ok:`) with uploads at `:925-926` / `:929` / `:935-937`**.
6. **Manifest-write attribution.** `:822` *writes* the manifest → `:822` **CALLS**
   `append_occlusion_rows` inside the best-effort `try:` at `:821`; the write is
   **`occlusion_manifest.py:203-208`**.
7. **An off-by-one I introduced.** HANDOFF `verified_this_session_firsthand[7]` → **`[8]`** for
   the identity-LD caveat (`[7]` is the 100×-error entry). Caught by parsing the JSON array
   rather than trusting the eye. *(The checker's note that the retraction is at `[5]`, not `[6]`,
   was applied — the review cites `[5]`.)*

**Re-performed and found CORRECT (26 arithmetic claims):** all eight E-2 percentages and their
two column sums (`66,480` exact / `3,714` flipped both reconcile), with the ratio-vs-percent trap
re-derived explicitly (`333/1638 = 0.2033` → **20.33%**, not 0.20%); `153 + 123 = 276`;
`276 × 2 = 552`; `276+276+1+22 = 575`; the BLOCKER-D float64↔float32 factor of exactly 2 against
the `120000` ceiling (SH2B3 75,497 clears; MC4R n ≈ 129,711 and FTO/HLA 363k–372k do not);
`263 h ÷ 24 ≈ 11 days`; `312 h = 13 days`; `523,169 ÷ 600,000 = 87.2%`; corpus pooled
`31,152 / 745,534 = 4.18%`; the panel TSV's **9** columns with `n_dropped_occluded` at index
**7** — re-parsed with `ast` after a naive comma-split gave a wrong 12 (the `_PANEL_COLUMNS`
block carries commas inside comments).

**Enumeration counts are explicitly scoped** to §0–§7, because the reconciliation section adds
numbers of its own; a whole-file recount gives 961/189/68/83 and would otherwise read as a
self-contradiction.

## Safety statements, each with the check that proves it

| Statement | Proof |
|---|---|
| **ZERO perimeter contact.** No `gsutil`, `gcloud`, `bq` or `wb` — not even read-only | `grep -cE '^\$ .*(gsutil\|gcloud\|bq \|wb )' 260811-rcw-evidence.log` = **0**. Asserted in Task 1's and Task 3's automated verify |
| **NOTHING WAS FIRED.** No cluster or VM was started, stopped, resumed or described | Same grep (all four CLIs forbidden outright); no task in this plan has a fire step, and no verify can pass by firing anything |
| **`src/`, `tests/`, `config/`, `Snakefile` UNCHANGED** | `git status --porcelain -- src tests config Snakefile` **EMPTY** at `L-02` (before), `L-20` (after), and again post-commit |
| **Writes confined to the quick directory** | `git diff --name-only c4dc410..HEAD` returns **only** the three deliverables |
| **`tests/m3/sparse_parent_benchmark.tsv` restored, never committed** | `git checkout --` inside `L-20`; the file is absent from all three commits |
| **Nothing fabricated to make a check pass** | `L-15`/`L-16` **expect absence** (`ABSENT`, `0`), so there was nothing to manufacture; no fake `.rds` touched, no absent data dir created |
| **$0** | All 20 checks are local NC-State reads plus two pytest runs and two snakemake dry-runs |

## Deviations from plan (disclosed)

1. **Backgrounded suite execution — an accepted execution-mechanics amendment** (directed by the
   orchestrator). This environment caps a synchronous shell call at 10 minutes; `tests/m3` takes
   ~15. It was launched **once**, redirected to a file, and polled to completion. **Backgrounding
   is a delivery mechanism, NOT a second run** — stated in the log header and provable from the
   single matching `$ ` line.
2. **`git add -f` for `260811-rcw-evidence.log`** (Rule 3 — blocking issue). `.gitignore:95` is a
   blanket `*.log`, so the plan's mandated artifact could not otherwise be committed. Overridden
   for **one explicit path only**, following the six `.log` files already tracked under
   `.planning/`. No `git add -A` / `git add .` was used anywhere.
3. **Three per-task commits instead of the plan's single Task-3 commit** (per the orchestrator's
   "atomic commits" instruction). Task 3's automated verify still passes: the last commit subject
   contains `260811-rcw` and the quick directory is clean.
4. **Three `CONTEXT-*` log blocks added** beyond the 20 checks, so that supporting claims (the
   commit range, the panel-TSV column contract) name a real command with real output instead of
   resting on recollection. They are deliberately **not** `L-NN` and **not** TSV rows, so the
   20-check invariant is untouched.

*This SUMMARY is intentionally left uncommitted; the orchestrator handles the docs commit.*

## What remains outstanding — for Carter

**Gate-time perimeter checks (§4)** — none of these can be measured from NC State:
the bucket `.npz` count (last known **0/276**), the VM state (last known **STOPPED, not
deleted**, `n1-standard-32` — ⚠ read the **disk-type label** before any destructive env action),
the stale `gs://` panel TSV rotation, and the real-`.bim` validation (⚠ carrying an **OPEN**
0-vs-1-based index-origin question that would validate the wrong rows if settled wrongly).
**Liveness is the GCS `.npz` object listing climbing to 276 — NOT the kernel light, NOT
`_SUCCESS`.**

**PRE-FIRE decisions (§5)** — PRE-FIRE 1 (the manifest has no path out of the perimeter; the
per-region-file remedy is preferred) and **PRE-FIRE 1b, the `allow_degraded` dead-end**: three
reachable branches, and the chosen one must be **written down BEFORE STEP B and re-read at
STEP E**, because branch (ii) is only diagnosable after the fire.

**Open items that BOUND USAGE rather than block the fire (§6)** — **BLOCKER-D above all**: the
fire banks `.npz` that **cannot be converted** for the large regions, so STEP E and the STEP G
read-path proof are demonstrable only on the convertible subset (SH2B3 `__sub14`). Also: the
three **undischarged** E-2 disclosure obligations (drafts ready in `260811-oku`, incl. the OPEN
LIMITATION-vs-CORRECTION question), **SR4-OPEN** (dossier ready in `260811-pmv`; disposition
Carter's), the OSF Check-2 amendment-update, the never-run 4-check validation protocol, the
identity-LD caveat, and findings E/G as inert-but-correct.

**⛔ AN AGENT MUST NEVER FIRE THE BILLED LOOP.** Nothing in this arc authorizes it.

## Self-Check: PASSED

- `260811-rcw-evidence.log` — FOUND (1,214 lines)
- `260811-rcw-evidence.tsv` — FOUND (21 lines = header + 20 rows)
- `260811-rcw-PRE-FIRE-GATE-REVIEW.md` — FOUND (589 lines; floor is 180)
- Commits `5bd21b9`, `4b2a754`, `50f4950` — all FOUND in `git log`
- Task 1 gate `EVIDENCE_OK`, Task 2 gate `REVIEW_OK` (re-run after the Task 3 edits), Task 3 gate
  `RECONCILED_AND_COMMITTED` — all green, with the quick-dir-clean clause re-verified **from the
  repo root** after its first run emitted a bad-path warning that could have made it a false green
