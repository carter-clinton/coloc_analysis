---
status: awaiting_human_verify
trigger: "The catastrophe-defense layer probes entries/entries/parts/, which does NOT exist on a real Hail 0.2.135 MatrixTable. Real entry data is at entries/rows/parts/. find_and_fix with TDD."
created: 2026-06-03T23:19:27Z
updated: 2026-06-03T23:19:27Z
---

## Current Focus

hypothesis: All path-based catastrophe-defense probes hardcode `entries/entries/parts/`, a phantom subpath. Real Hail 0.2.135 MTs store entry row-group payload at `entries/rows/parts/`. Fixing the path at every functional site (src probe, auto-resume kill-mtime check, tests, notebook du-floor cells) restores the secondary path-based layer without touching the load-bearing count-based gate.
test: TDD RED -> build populated stub at REAL path -> `_validate_checkpoint_populated` returns False under current code (RED) -> fix path -> GREEN. Plus hail-gated ground-truth test writing a small real MT.
expecting: RED confirmed (False on populated real-path stub) before fix; GREEN after; hail-gated test SKIPs on smoke_dev (no Hail).
next_action: write RED tests, capture failure, fix src, re-run GREEN.

## Symptoms

expected: du-floor / checkpoint-populated checks should probe the path where Hail actually writes entry data, so they pass on populated MTs and fail on empty ones.
actual: every check probes `entries/entries/parts/`, absent on a real Hail MT -> `gsutil du` returns 0 / `_validate_checkpoint_populated` returns False on a genuinely populated MT. Blocked Gate B #3 cohort_summary TSV (Cell 5.5 false-positive).
errors: AssertionError in AOU-1 notebook Cell 5.5 (du-floor 0 bytes on a real 3.25 GB EUR MT).
reproduction: run any du-floor cell or `_validate_checkpoint_populated` against a real populated Hail MT -> wrong-path -> 0 bytes / False.
started: latent since the Track-4 patches (2026-05-28); first exercised against a REAL populated MT at Gate B #3 (2026-06-03).

## Diagnosis (COMPLETE — provided by caller)

root_cause: Real Hail 0.2.135 MatrixTable on-disk layout puts entry data under `<mt>/entries/rows/parts/`, NOT `<mt>/entries/entries/parts/`. Carter verified LIVE at Gate B #3: EUR `mt_eur_qc.mt` = 3.25 GB total, 3.24 GB at `entries/rows/parts/`, `entries/entries/parts/` ABSENT. The bug is FAIL-SAFE (wrong path -> false-positive on du-floor / `_validate_checkpoint_populated` returns False -> force-recompute; never passes an empty MT as populated), so it did NOT compromise correctness. Load-bearing gate is the count-based `_assert_checkpoint_nonempty` (path-independent, CORRECT, must stay unchanged). The path-based secondary layer is non-functional and blocks real runs (Gate-C blocker) + tests validate the phantom path (false confidence).

## Exhaustive Site List (grep `entries/entries` whole repo, 2026-06-03)

### FUNCTIONAL sites to FIX (path is load-bearing for a real probe)
- src/python/aou_ld_panel.py:775  — `_validate_checkpoint_populated` probe: `entries_dir_uri = f"{uri}/entries/entries/parts"` (the live bug)
- src/python/aou_ld_panel.py:1210 — auto-resume/forensics kill-mtime check: `entries_parts_dir = f"{uri.rstrip('/')}/entries/entries/parts"`
- src/python/aou_ld_panel.py:1226 — path-substring filter: `"/entries/entries/parts" in str(e.get("path", ""))`
- src/python/aou_ld_panel.py:741, 745, 746, 958, 1127 — docstrings/comments referencing the path (fix for accuracy)
- tests/m3/test_aou_ld_panel_local.py:857 — `_make_stub_mt` builds entries at `entries/entries/parts` (inside :839 builder; refs at :828/:845/:872 comments)
- tests/m3/test_aou_ld_panel_local.py:1426 — `_mk_listing` builds forensic listing at `entries/entries/parts/`
- .planning/notebooks/AOU-0.5-mechanism-probe_template.ipynb:99,102 — du-floor cell
- .planning/notebooks/AOU-1_template.ipynb:131,148,166,201,218,236,271,288,306 — 3 du-floor cells (3.5/4.5/5.5)
- .planning/notebooks/AOU-0-precheck_template.ipynb:16,202,204,210,212 — precheck du cell
- .planning/notebooks/AOU-1-chr22-smoke_template.ipynb:213,234,293,314,373,394 — 3 smoke du-floor cells
- .planning/notebooks/AOU-2-AOU-4-TRACK-4-PATTERN.md:60 — pattern doc

### HISTORICAL/FORENSIC docs — DO NOT ALTER (record the catastrophe as observed; the phantom path WAS the recorded forensic signature at the time and any rewrite would falsify the historical record)
- .planning/STATE.md (catastrophe narrative + Gate-C-blocker entry, lines 2/6, 30, 52, 56, 546)
- .planning/WAVE-1-CLOSEOUT-CHECKLIST.md:95,97,112,114,116,142
- .planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md + AOU-SUPPORT-FOLLOWUP-DRAFT.md
- .planning/quick/260528-l8r-.../ABBY-MIGRATION-CLARIFICATION-DRAFT.md + 260528-l8r-PLAN.md
- .planning/quick/260528-jvd-.../{PLAN,SUMMARY}.md
- .planning/quick/260601-u1b-.../{PLAN,TIERED-VALIDATION-RUNBOOK}.md
- .planning/debug/m3-W1-empty-mt-catastrophe.md (root-cause analysis as recorded)
- .planning/debug/resolved/m3-gateb-nano-sample-axis-collapse.md (already-resolved; records the bug discovery)
- .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md:153,155,157,315 (D-M3-10 decision narrative)

NOTE: `grep -rn "entries/rows"` over the repo returned ZERO functional hits before this fix (only STATE.md + resolved debug doc narrative) — confirms the correct path was never used anywhere.

## Eliminated

(none — diagnosis was provided complete; this is a fix-only session)

## Evidence

- timestamp: 2026-06-03T23:19:27Z
  checked: `grep -rn "entries/entries" .` + `grep -rn "entries/rows" .`
  found: 8 functional src sites + 4 test sites + notebook cells in 4 .ipynb + 1 pattern doc; ZERO functional `entries/rows` hits. Historical docs separated out.
  implication: complete site inventory established; fix scope confirmed.
- timestamp: 2026-06-03T23:19:27Z
  checked: src/python/aou_ld_panel.py:773-801 (`_validate_checkpoint_populated`)
  found: probe builds `f"{uri}/entries/entries/parts"`; file:// branch uses pathlib iterdir over that dir; gs:// branch uses hl.hadoop_ls. Returns False if dir absent -> on a real MT the dir is always absent -> always False (fail-safe false-positive).
  implication: this is the live Gate-C blocker; single string is wrong.
- timestamp: 2026-06-03T23:19:27Z
  checked: tests/m3 fixture builders + hail-gate pattern (`_require_hail()` = `pytest.importorskip("hail")`); `synthetic_mt_path` fixture builds a real Balding-Nichols MT via build_synthetic_mt.py.
  found: `_make_stub_mt` (:839) builds entries at the phantom path; tests assert False on it (still correct post-fix because empty). `synthetic_mt_path` gives a real MT for the ground-truth hail-gated test.
  implication: TDD plan = build populated stub at REAL path (RED on old code) + hail-gated real-MT test.

## RED Evidence (Step 1, 2026-06-03)

Against UNFIXED src (probe at `entries/entries/parts`):
```
test_validate_checkpoint_populated_accepts_real_path_populated_mt FAILED
  AssertionError: populated MT at entries/rows/parts/ must validate True
  assert False is True
test_validate_checkpoint_populated_rejects_empty_real_path_mt    PASSED (catastrophe still caught)
test_validate_checkpoint_populated_rejects_empty_entries_dir     PASSED (builder converted to real path)
test_validate_checkpoint_populated_rejects_stub_entries          PASSED
test_has_checkpoint_vs_validate_diverge_on_stub_mt               PASSED
1 failed, 4 passed
```
RED confirmed: the populated real-path MT validates False under the phantom-path probe.

## GREEN Evidence (Step 2-7, 2026-06-03)

After fixing the 3 functional path strings in src (probe :775, kill-mtime check :1210, substring filter :1226) + docstrings/comments:
```
test_validate_checkpoint_populated_accepts_real_path_populated_mt PASSED  (was RED)
test_validate_checkpoint_populated_rejects_empty_real_path_mt     PASSED
test_validate_checkpoint_populated_rejects_empty_entries_dir      PASSED
test_validate_checkpoint_populated_rejects_stub_entries           PASSED
test_has_checkpoint_vs_validate_diverge_on_stub_mt                PASSED
all 16 capture-forensics + path tests PASSED
```
Full tests/m3 sweep (smoke_dev, no Hail): **124 passed, 30 skipped, 0 failed.**
- New hail-gated ground-truth test `test_real_hail_mt_entries_layout_and_validate_populated`
  SKIPs on smoke_dev (via `_require_hail` = `pytest.importorskip("hail")`); will RUN on AoU/any Hail env.
- `_assert_checkpoint_nonempty` (count-based load-bearing gate) UNCHANGED — confirmed absent from src diff.
- Sample-axis call-rate guard (9f0c837), colon fix (a96f2cf), driver-collect fix (e23c081: `_n_partitions`/`read_matrix_table`/`repartition`) UNCHANGED — none appear in src diff.

## Resolution

root_cause: `entries/entries/parts/` is a phantom subpath; real Hail 0.2.135 entry payload is at `entries/rows/parts/`. (Diagnosis complete; RED-confirmed; GREEN-verified.) FAIL-SAFE bug: wrong path -> always-False on populated MTs -> Gate-C blocker; never passed an empty MT as populated, so correctness was never compromised (the count-based `_assert_checkpoint_nonempty` was the real gate throughout).
fix: Corrected `entries/entries/parts` -> `entries/rows/parts` at all 3 functional src probe sites + docstrings/comments; converted test fixtures (`_make_stub_mt`, `_mk_listing`) to the real path; added a RED-first populated-real-path test + empty-real-path test + a hail-gated ground-truth test that writes a real Hail MT and asserts entries live at `entries/rows/parts/` (and the phantom path is absent); fixed du-floor cells + print strings in all 4 AoU notebooks; fixed the TRACK-4-PATTERN.md doc; bundled the `/home/jupyter` hardcode cleanup (portable `os.path.expanduser("~/coloc_analysis/...")`) in AOU-1/AOU-0.5/AOU-1-chr22-smoke/AOU-2 Cell 1b + AOU-0-precheck CLONE/print.
verification: NCSU pure-Python: RED captured then GREEN (124 passed/30 skipped/0 failed). Notebooks JSON + nbformat round-trip OK. AWAITING live Gate-C: du-floor cells must pass against a real multi-GB MT on the AoU cluster (the part that cannot be exercised NCSU-side). Status held at awaiting_human_verify; NOT moved to resolved/.
files_changed: [src/python/aou_ld_panel.py, tests/m3/test_aou_ld_panel_local.py, .planning/notebooks/AOU-1_template.ipynb, .planning/notebooks/AOU-0.5-mechanism-probe_template.ipynb, .planning/notebooks/AOU-1-chr22-smoke_template.ipynb, .planning/notebooks/AOU-0-precheck_template.ipynb, .planning/notebooks/AOU-2_per_region_ld.ipynb, .planning/notebooks/AOU-2-AOU-4-TRACK-4-PATTERN.md, .planning/debug/m3-entries-path-phantom-subpath.md]
