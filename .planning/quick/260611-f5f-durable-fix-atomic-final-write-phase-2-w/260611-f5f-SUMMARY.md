---
phase: 260611-f5f
plan: 01
subsystem: m3-aou-ld-panel / durable-fix atomic-final-write
tags: [m3-W2, durable-fix, read-gate, tdd, aou-2]
requires:
  - "src/python/aou_ld_panel.py::_final_is_trustworthy (Phase 1, commit f931446)"
provides:
  - "src/python/aou_ld_panel.py::read_final_cohort_mt — gate-then-read wrapper that raises before any Hail read on an untrustworthy final"
  - "AOU-2 cell 4 reads both final MTs through the gate (read-side hole closed)"
affects:
  - ".planning/notebooks/AOU-2_per_region_ld.ipynb (cell 3 import + cell 4 reads)"
  - ".planning/phases/m3-aou-afr-ld-panel-build/DURABLE-FIX-DESIGN-atomic-final-write.md (item 1 DONE)"
tech-stack:
  added: []
  patterns:
    - "gate-then-read: call the contents-only trust gate and RAISE before import hail / hl.read_matrix_table"
key-files:
  created: []
  modified:
    - "src/python/aou_ld_panel.py"
    - "tests/m3/test_aou_ld_panel_local.py"
    - ".planning/notebooks/AOU-2_per_region_ld.ipynb"
    - ".planning/phases/m3-aou-afr-ld-panel-build/DURABLE-FIX-DESIGN-atomic-final-write.md"
decisions:
  - "Gate runs BEFORE import hail so the reject path is fully unit-testable without a live Hail; the populated branch's only remaining failure is the absence of Hail, not the gate."
metrics:
  tasks: 2
  files: 4
  duration: "~12 min"
  completed: 2026-06-11
---

# Phase 260611-f5f Plan 01: durable-fix atomic-final-write Phase 2 item 1 — read-side consumer wiring Summary

Closed the read-side hole of the durable atomic-final-write contract: added `read_final_cohort_mt(uri)` — a gate-then-read wrapper that calls the Phase-1 contents-only gate `_final_is_trustworthy(uri)` and RAISES a loud, actionable `RuntimeError` (naming the uri + the `force_fresh=False` finalize-only recovery) BEFORE any `import hail` / `hl.read_matrix_table` — and wired it into AOU-2 cell 4 for both `mt_afr_qc.mt` and `mt_eur_qc.mt`, the only direct final-MT reader (AOU-4 reads only AOU-2 `.rds` products).

## What changed

- **`src/python/aou_ld_panel.py`** — new `read_final_cohort_mt(uri)` immediately after `_final_is_trustworthy`. Gate-and-raise runs before `import hail`; the raise message names the uri and the `force_fresh=False` recovery path. Returns `hl.read_matrix_table(uri)` only when the gate passes.
- **`tests/m3/test_aou_ld_panel_local.py`** — two RED→GREEN tests:
  - `test_read_final_cohort_mt_raises_on_empty_success_only` — empty-final catastrophe stub (`_make_stub_mt(..., with_entries_dir=True)`) → `pytest.raises(RuntimeError)`, asserting the uri and `force_fresh=False` appear in the message.
  - `test_read_final_cohort_mt_gate_passes_on_populated` — populated MT → asserts `_final_is_trustworthy(...) is True` (the reject path provably does not fire on a good final; `read_final_cohort_mt` not invoked because the populated branch hits Hail, unavailable locally).
- **`.planning/notebooks/AOU-2_per_region_ld.ipynb`** — cell 3 import adds `read_final_cohort_mt`; cell 4 replaces both bare `hl.read_matrix_table` final reads with `read_final_cohort_mt`. Exactly 3 lines changed, no nbformat whole-file churn (no `git checkout -f` needed).
- **`DURABLE-FIX-DESIGN-atomic-final-write.md`** — § Implementation status: PHASE 2 item 1 marked DONE (names `read_final_cohort_mt`, notes AOU-2 cell 4 was the only direct final-MT reader). Items 2 (chr22 smoke) + 3 (`file://` footgun) stay PENDING/deferred.

## TDD evidence (RED → GREEN)

RED (before `read_final_cohort_mt` existed):
```
>       from aou_ld_panel import read_final_cohort_mt
E       ImportError: cannot import name 'read_final_cohort_mt' from 'aou_ld_panel'
...
FAILED tests/m3/test_aou_ld_panel_local.py::test_read_final_cohort_mt_raises_on_empty_success_only
FAILED tests/m3/test_aou_ld_panel_local.py::test_read_final_cohort_mt_gate_passes_on_populated
2 failed, 108 passed, 19 skipped in 0.95s
```

GREEN (after implementing it):
```
110 passed, 19 skipped in 0.69s
```

Task 2 wiring verify:
```
WIRED_OK
```

Final full-suite (`tests/m3/test_aou_ld_panel_local.py`): **110 passed, 19 skipped, 0 failed**.

## Deviations from Plan

None — plan executed exactly as written. (The plan's Test A specified `_make_stub_mt(mt_dir, with_entries_dir=True)` for the catastrophe-signature fixture; that fixture exists in the test file and yields `_final_is_trustworthy False`, matching the plan's behavior spec.)

## Explicit Non-Goals (untouched, as required)

- chr22 smoke (item 2) — left PENDING (needs the live cluster; GATE 1).
- `_qc_checkpoint_uri` `file://` footgun (item 3) — left deferred (latent, inert in production).
- No cluster / gsutil / notebook-execution action taken.

## Self-Check: PASSED

- `src/python/aou_ld_panel.py::read_final_cohort_mt` — FOUND
- AOU-2 cell 4 wired (`read_final_cohort_mt` ×3 in notebook, no bare final `hl.read_matrix_table`) — FOUND (WIRED_OK)
- Design doc item 1 DONE — FOUND
- Two new tests pass; full `tests/m3` GREEN — FOUND
