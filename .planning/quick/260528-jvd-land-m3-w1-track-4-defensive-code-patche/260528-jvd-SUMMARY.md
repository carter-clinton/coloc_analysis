---
quick_id: 260528-jvd
description: Land m3-W1 Track 4 defensive-code patches for empty-MT catastrophe
mode: quick
date: 2026-05-28
status: complete
disposition: SUCCESS
commits:
  - 59e914b  # patch 1/7 — RED tests for _validate_checkpoint_populated
  - 86c8a56  # patch 2/7 — GREEN _validate_checkpoint_populated helper
  - 4c75ca2  # patch 3/7 — swap resume-gate from _has_checkpoint to validated
  - 88ab0c5  # patch 4/7 — post-write count_rows/count_cols assertions
  - 9b4317f  # patch 5/7 — AOU-1 bucket-state assertion cells 3.5/4.5/5.5
  - 4b321c2  # patch 6/7 — closeout checklist STEP 3 entries/ verification
  - bfe5f0e  # patch 7/7 — D-M3-10 decision token in m3-CONTEXT.md
related_artifacts:
  - .planning/debug/m3-W1-empty-mt-catastrophe.md (root-cause analysis source)
  - .planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md §Track 4 (patch list source)
  - .planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-SUMMARY.md (refactor that introduced the unsafe _has_checkpoint resume gate)
---

# SUMMARY — Quick Task 260528-jvd

## Outcome

All 7 m3-W1 Track 4 defensive-code patches landed as atomic commits with TDD discipline. RED→GREEN→REFACTOR sequence preserved (Task 1 = failing tests against a not-yet-existent helper; Task 2 = helper making tests pass; Tasks 3-7 = behavior + integration). All 38 pure-Python tests in `tests/m3/test_aou_ld_panel_local.py` pass after every commit (no regression at any patch boundary). 11 live-Hail tests SKIP gracefully (Hail not installed in smoke_dev; per `[[project_python_311_pin]]`).

Net behavior change at the resume gate of `src/python/aou_ld_panel.py:load_qc_cohort()`:

| MT state                          | Pre-patch resume-gate     | Post-patch resume-gate                  |
|-----------------------------------|---------------------------|-----------------------------------------|
| populated MT, valid sidecar       | RESUME (correct)          | RESUME (preserved)                      |
| _SUCCESS-absent MT                | FRESH (correct)           | FRESH (preserved)                       |
| **_SUCCESS + empty entries (W1)** | **RESUME (catastrophe)**  | **WARN + auto_fresh (defended)**        |
| _SUCCESS + orphan (no sidecar)    | WARN + auto_fresh         | WARN + auto_fresh (preserved)           |
| sidecar mismatch                  | RuntimeError              | RuntimeError (preserved)                |

Net behavior change at the write sites: every `mt.checkpoint()` returns into `_assert_checkpoint_nonempty(mt, uri, phase=...)` which forces `count_rows() + count_cols()` Spark jobs and raises RuntimeError on zero. Cell 7's lazy `count_rows()` would have caught the W1 catastrophe 36h earlier — this builds the check INSIDE `load_qc_cohort` so every MT write self-validates, not just the final one some downstream cell happens to query. Cost: ~10-30 sec per checkpoint × 3 = ~1-2 min per cohort, trivial against a 60+ h monolithic-run baseline.

Net behavior change at the notebook layer: AOU-1 Cells 3.5, 4.5, 5.5 fire `gsutil du -s` against `entries/entries/parts/` and assert > 1 GB before downstream cells define cohorts on top. A stub MT in Cell 3 now halts the notebook before Cell 4 fires the AFR sensitivity cohort on top of empty cohort lineage — the exact misordering that compounded the W1 catastrophe over 65h.

Net behavior change at the closeout layer: STEP 3 of `WAVE-1-CLOSEOUT-CHECKLIST.md` now verifies entries-dir size + adds a belt-and-suspenders Hail read-probe from a fresh Python subprocess (NOT the original kernel — JVM-cached IR masked the W1 catastrophe). Pass criteria upgraded to require `entries/: OK (X.YZ GB)` with X.YZ > 1.0 alongside `_SUCCESS: OK` + `metadata: OK`.

Net behavior change at the decision layer: D-M3-10 in `m3-CONTEXT.md` locks the contents-validated verification protocol as a phase-level requirement spanning Waves 1+2+4+5. No new `_has_checkpoint(ckpt_*)` callers may be introduced for resume-gate semantics.

## Per-patch summary

| # | Commit  | Title                                                              | Files                                                                              | LOC delta |
|---|---------|--------------------------------------------------------------------|------------------------------------------------------------------------------------|-----------|
| 1 | 59e914b | RED regression tests for _validate_checkpoint_populated            | tests/m3/test_aou_ld_panel_local.py                                                | +86       |
| 2 | 86c8a56 | _validate_checkpoint_populated helper                              | src/python/aou_ld_panel.py                                                         | +94       |
| 3 | 4c75ca2 | swap _has_checkpoint→_validate_checkpoint_populated in resume gate | src/python/aou_ld_panel.py                                                         | +26 / -3  |
| 4 | 88ab0c5 | post-write count_rows/count_cols assertions at 3 mt.checkpoint sites | src/python/aou_ld_panel.py                                                         | +53       |
| 5 | 9b4317f | AOU-1 bucket-state assertion cells 3.5 / 4.5 / 5.5                 | .planning/notebooks/AOU-1_template.ipynb                                           | +156      |
| 6 | 4b321c2 | closeout checklist STEP 3 verifies entries/ size not just _SUCCESS | .planning/WAVE-1-CLOSEOUT-CHECKLIST.md                                             | +59 / -11 |
| 7 | bfe5f0e | D-M3-10 decision token: contents-validated MT write protocol       | .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md                           | +9        |

## Verification gates (must_haves vs reality)

1. **_validate_checkpoint_populated helper exists** — `src/python/aou_ld_panel.py:493` defines the helper; cross-references both new memories in the docstring. PASS.
2. **Auto-resume state machine uses the new helper at both intermediate-check sites** — `grep -n "_validate_checkpoint_populated(ckpt_" src/python/aou_ld_panel.py` returns 2 hits (line 655 + 683); the surviving `_has_checkpoint(ckpt_*)` calls are the explicit catastrophe-pattern guards (commented as such). PASS.
3. **Each of 3 mt.checkpoint() sites has post-write count_rows/count_cols assertion** — `grep -c "_assert_checkpoint_nonempty" src/python/aou_ld_panel.py` returns 4 (1 def + 3 callers). PASS.
4. **3 new regression tests exist in test_aou_ld_panel_local.py** — tests named per PLAN.md (`test_validate_checkpoint_populated_rejects_stub_entries`, `test_validate_checkpoint_populated_rejects_empty_entries_dir`, `test_has_checkpoint_vs_validate_diverge_on_stub_mt`); all PASS post-helper. PASS.
5. **AOU-1_template.ipynb has 3 new bucket-state assertion cells (3.5/4.5/5.5)** — `python3 -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb'));src=' '.join(' '.join(c['source']) for c in nb['cells']); print(sum(f'Cell {l} — Mandatory' in src for l in ('3.5','4.5','5.5')))"` returns 3. PASS.
6. **WAVE-1-CLOSEOUT-CHECKLIST.md STEP 3 verifies entries/ size not just _SUCCESS** — `grep -c "entries/entries/parts" .planning/WAVE-1-CLOSEOUT-CHECKLIST.md` returns ≥1; CRITICAL callout added at top of STEP 3 + Hail read-probe block added at bottom. PASS.
7. **D-M3-10 decision block in m3-CONTEXT.md** — `grep -c "D-M3-10" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` returns 2 (header + assumption #10 echo). PASS.

## Test sweep evidence

```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_aou_ld_panel_local.py --no-header -q
.....................................sssssssss.ss                        [100%]
38 passed, 11 skipped in 0.42s
```

The 11 skipped tests are the live-Hail tests (`@_require_hail()`); they will run on the next AoU env that has Hail installed. Per `[[project_python_311_pin]]`, smoke_dev intentionally has no Hail.

## Branch / commit chain

Branch: `main` (per project memory `[[project_state]]`: `git.isolation: branch`; not worktree; gsd-quick init returned `branch_name: null`).

```
$ git log --oneline 7e165dd..HEAD
bfe5f0e decision(m3-W1): D-M3-10 MT write verification protocol (Track 4 patch 7/7)
4b321c2 docs(m3-W1): closeout checklist STEP 3 verifies entries/ size not just _SUCCESS (Track 4 patch 6/7)
9b4317f feat(m3-W1): AOU-1 bucket-state assertion cells 3.5/4.5/5.5 (Track 4 patch 5/7)
88ab0c5 feat(m3-W1): post-write count_rows/count_cols assertions at 3 mt.checkpoint() sites (Track 4 patch 4/7)
4c75ca2 fix(m3-W1): swap _has_checkpoint→_validate_checkpoint_populated in resume gate (Track 4 patch 3/7)
86c8a56 feat(m3-W1): _validate_checkpoint_populated helper (Track 4 patch 2/7)
59e914b test(m3-W1): RED regression tests for _validate_checkpoint_populated (Track 4 patch 1/7)
```

The closing docs commit (PLAN.md + this SUMMARY.md + STATE.md row + STATE.md last_updated/last_activity) follows as a separate commit per `/gsd-quick` workflow Step 8.

## What this DOES NOT change

- AoU env state — env was deleted end-of-Session-2 per Carter; no recreation triggered by these patches.
- Track A submission lane — untouched per `[[track_a_submission_in_progress]]` + `[[feedback_stop_asking_track_a]]`.
- Track 1 (AoU credit recovery ticket) — patches are independent of Abby Doyle / AoU engineering response; the ticket exchange continues in parallel.
- Track 2 (1000G AFR safety-net pivot decision) — patches apply REGARDLESS of which LD substrate Wave 2 ends up using; do NOT predetermine the decision.
- Track 3 (NCSU v7→v8 forensic investigation) — already complete per Session 2 update; patches do not depend on its conclusion.
- LSF queue jobs, M2 manifest, M4/M5 downstream pipelines — none touched.
- Pre-catastrophe W2 design-delta commits (`e3c29e7..822d47d`) — preserved verbatim; the post-write assertions land at deeper code sites and do not interfere with the per-region LD compute paths.

## What this UNBLOCKS

- Any future MT-writing fire (chr22 smoke, full cohort rebuild on credit-recovered AoU compute, 1000G AFR-substrate Wave 2 dev fire that still writes intermediate MTs for ancestry filter / sample QC reproducibility) is now self-validating. The catastrophe class cannot recur silently — it would either raise loudly inside `load_qc_cohort` (post-write assertion) or halt the notebook (bucket-state assertion) or fail the closeout (entries-dir verification).
- The W1 catastrophe lessons are now baked into the M3 decision graph (D-M3-10) so future Wave plans (Wave 2 LD compute, Wave 4 production fire, Wave 5 closeout) inherit the protocol without re-deriving it.

## Open items deferred to future tasks

- Live-Hail integration test for the new `_assert_checkpoint_nonempty()` (would need a Hail install + a synthetic empty-MT fixture; per project memory, smoke_dev has no Hail and AoU env is deleted).
- chr22-smoke notebook variant with sub-1GB threshold cells (when chr22 smoke is fired; the AOU-1 template comment flags the override path).
- AOU-2 (per-region LD compute) + AOU-4 (validation memo) notebook bucket-state assertions — D-M3-10 mandates these but the notebooks are out-of-scope for this quick task (they consume MT reads, not new writes).
- Memory bake for the new D-M3-10 decision — optional; the existing 2 catastrophe memories already cover the underlying class.

## Total cost

- Compute: $0 (all patches NCSU-side; no AoU compute).
- Wall-time: single Carter-Claude session, ~45 min including planning + 7 atomic commits.
- Net lines: +543 / -14 across 6 files.
