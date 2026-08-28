# Quick Task 260826-qq9 — SUMMARY

**Completed:** 2026-08-28
**Base:** `352ac9e` → **HEAD `1333f3f`**
**Branch:** `m3-W2-aou-deltas` (no worktree isolation — GPFS constraint)

## Goal

`src/python/pairwise_completeness_scan.py` read `config/ld_regions.tsv` on
`region_id` alone. The manifest's real key is **(region_id × ancestry)** — 553
lines = 1 header + 276 regions × {AFR, EUR}. So `--region-ids <21 ids>` selected
**42 windows**, not 21, and the 2026-08-26 STEP 3 sweep was inflated **8×** at the
row level.

## Commits

| Task | Hash | What |
|---|---|---|
| T1 | `d8f4d54` | Read the manifest on its real key; `--ancestry` (default `AFR`) |
| T2 | `5078cdc` | Duplicated `region_id` RAISES at iterator AND driver; the two POOLED denominators reconciled by identity |
| T3 | `021f26f` | Bank the contaminated sweep, reconcile its denominators, PRE-REGISTER the re-run's answer |
| T4 | `1333f3f` | **Correction** — layer 3 IS testable; the "no committed test can reach it" claim was wrong |

⚠ **T1–T3 were executed by a background skill-runner** concurrent with the
foreground orchestration (the known `gsd-quick` double-run hazard,
`feedback_gsd_quick_skill_runs_workflow_twice`). Timing confirms it ran the
**final, twice-checked plan** (commits 19:59 / 20:06 / 20:24 vs the plan's last
revision at 19:48). No second writer was live at verification time. The executor
produced no SUMMARY; **this file was written by the orchestrator from
independently re-verified facts, not from the runner's report.**

## The mechanism, end to end

`iter_bim_windows` built `specs` as a **LIST** and `out` as a **DICT keyed on
region_id**, appending each matching `.bim` row once per matching spec → rows 2×.
Deletion × partner enumeration over a doubled row list → pairs 4×. The driver
wrote `summaries[region_id]` **last-wins** while `all_results` **accumulated** →
two passes → **8×** in the emitted TSV. The stdout table iterated the LIST while
looking up the DICT → every region printed twice.

Of the 21 swept regions, 12 had identical AFR/EUR bounds (exact duplication) and
9 (`__subNN`) had the AFR window **strictly inside** the EUR window (±2 Mb pad),
so duplication was **non-uniform** — which is why the inflation was 1.972×, not
2.000×.

## Verification (all re-run by the orchestrator, not taken on report)

| Check | Result |
|---|---|
| `_read_regions_tsv` on the real manifest | **276**, was 552 |
| `--ancestry EUR` selects EUR bounds | pass |
| `DEFAULT_ANCESTRY` / parser default | `AFR` both |
| STEP 3 PENDING PASTE needs no edit | `--ancestry` count **0** |
| Duplicate-id guard | raises on identical **and** differing bounds |
| Single-id CONTROL | still returns 6 rows |
| Ancestry predicate vs production | agrees **5/5**, incl. disputed `'  AFR  ' → False` |
| Frozen surfaces vs `352ac9e` | **0-line diff** |
| Non-scanner collect | **1054**, unchanged |
| Scanner file collect | 80 → 100 (T1–T3) → **101** (T4) |
| **tests/m3** | **1122 passed / 33 skipped / 0 failed** |

**Suite reconciliation, component-exact:** 1101 (baseline) + 20 (T1–T3) = 1121,
+ 1 (T4) = **1122**. Scanner-file delta +20 matches exactly 20 new top-level
`def test_`; the parametrize expansion (5 extra items) is unchanged on both sides.

## Negative controls observed

1. **T1(b) — the masking**, reproduced independently by the orchestrator: a naive
   `parts[index]` goes **RED standalone** (`IndexError`) while staying **GREEN
   through `_read_regions_tsv`**, because `_REGIONS_TSV_ANCESTRY_COL` (6) <
   `_REGIONS_TSV_END_COL` (15) and the length guard drops short rows first. This
   is why `_tsv_field` is a named module-level function, not an inline expression.
2. **T4 — layer 3**, observed twice (before and after the comment edits): deleting
   `if region_id in summaries: raise` makes the new test **RED**.

## Judgment calls worth recording

**The executor refused to "improve" the production contract.** The plan specified
`.strip().upper()` on both sides; `run_native_ld_panel._filter_ancestry` does
**not** strip. A stripping mirror would disagree with the real contract on
`'  AFR  '`. `_matches_ancestry` is a byte-faithful mirror and whitespace
tolerance lives one layer up in `_tsv_field`. Verified: 5/5 agreement.

**The code is stronger than the plan asked for.** The plan required the two POOLED
denominators be labelled. The code instead **reconciles them by identity and
raises before `write_tsv`**, so a disagreeing instrument leaves no output at all
(`feedback_aggregate_agreement_hides_component_errors` — prefer a must-be-identity
transform over a must-match count).

**T4 corrects a claim I had endorsed.** T1–T3 asserted, in three places, that layer
3 admits no committed test. That holds for the naive front-door test and does not
generalise: testing the innermost layer of a defense-in-depth stack *requires*
disabling the outer ones. One `monkeypatch.setattr` on the shared module-global
neutralises layers 1 and 2. The new test attributes the raise by the traceback's
**final frame**, so green cannot mean "some other layer stopped it." When layer 3
is deleted, the **POOLED denominator identity** catches the duplication instead —
4 summary rows against 8 emitted — the same 2× inflation that corrupted the sweep,
in miniature. Layer 3 is the **earliest** catch and the only one naming the
region_id, not "unreachable redundancy."

## Known gate defect (not blocking)

T2's gate `test "$(grep -c 'basis: per-region summaries' …)" -ge 3` returns **2**
against **correct** code: the third string is line-wrapped across two source
lines. All three POOLED lines do carry a basis. This is the fourth brittle-grep in
this task (after `--nonfounders`, `NOT BANKED`, `1 xfailed`) — baked as
`feedback_grep_gate_matches_text_not_meaning`. The gate should assert on rendered
stdout, not source text.

## What this does NOT establish

**The re-run has not happened.** No prevalence, no boundary width, no
partial-confounding tail size. The pre-registered prediction is committed in
`.planning/debug/260826-PCS-…-prereg-prediction.md` **before** the repaired
instrument runs: 15 undefined rows, 13 distinct pairs, 10/3, offsets
`{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`. A mismatch is a finding to report, never
a number to adjust. Adjudication with Seth is **brief-blind**.
