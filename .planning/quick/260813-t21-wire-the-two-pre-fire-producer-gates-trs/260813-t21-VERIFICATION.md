---
phase: quick-260813-t21
verified: 2026-08-13T22:30:00-04:00
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
re_verification: false
---

# Quick 260813-t21: Wire the two pre-fire producer gates — Verification Report

**Goal:** Both missing pre-fire producer gates (trsx5 clause-(d) occlusion anomaly gate + `--max-n-var` feasibility ceiling) live in `run_native_ld_panel.py`'s square path, TDD RED-first, Stage-C hold lifted in the three 260812-ox1 runbook docs.
**Verified:** 2026-08-13 (post-execution; commits 08dea40 / d9fbc63 / 269dec5, HEAD = 269dec5)
**Status:** PASSED
**Re-verification:** No — initial verification.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Over-fraction square region DEFERS (`deferred_occlusion_anomaly`), nothing excluded, no excludelist/manifest/plink/upload, loop continues | ✓ VERIFIED | Gate 2 at `src/python/run_native_ld_panel.py:853-861` returns BEFORE the `if occluded_ids:` excludelist/manifest block (:862) and before `build_plink_ld_command` (:907). `test_occlusion_anomaly_gate_defers_never_excludes` PASSED in my re-run (asserts no excludelist anywhere, 1 plink call for region 2 only, no region-1 cp, res[1] ok) |
| 2 | Over-ceiling region DEFERS (`deferred_infeasible_square: n_var=N > ceiling=M`) BEFORE occlusion detect, no plink, loop continues | ✓ VERIFIED | Gate 1 at :830-836, immediately after `_window_bim_n_var` (:815) and before the `raw_rows` parse (:837) / `detect_occluded_variants` (:842). Ordering proven by `test_feasibility_ceiling_runs_before_occlusion_detect` (spy count 0 when infeasible; built-in control count 1) — PASSED in my re-run |
| 3 | `--max-n-var` default equals `m3_convert_max_n_var`, pinned by a YAML-reading test | ✓ VERIFIED | `config/pipeline.yaml:393` = 120000; `_DEFAULT_MAX_N_VAR = 120000` (:143); `test_max_n_var_default_pins_consumer_ceiling` does `yaml.safe_load` on the real file and compares captured kwargs (:2390-2393) — PASSED in my re-run |
| 4 | `--fail-fast` semantics UNCHANGED (halts on any non-'ok', now incl. deferrals), documented in help text only | ✓ VERIFIED | d9fbc63 diff: the `if fail_fast ... raise RegionGateError` line (:1161-1162) untouched; ONLY the `--fail-fast` help string gained the deferral sentence. `test_fail_fast_halts_on_deferral` PASSED (RegionGateError, zero plink calls) |
| 5 | Sub-ceiling occluded region keeps FULL exclude-in-lockstep behavior | ✓ VERIFIED | `test_occlusion_anomaly_gate_open_at_subceiling_rate` (1/2001, ceiling 1.0005) + `test_occlusion_anomaly_gate_boundary_strict_greater` (1/2000, ceiling 1.0 exactly, strict >) + all 9 pinned lockstep tests PASSED in my re-runs |
| 6 | Both deferral paths keep `n_dropped_occluded`/`n_var` None; panel row appended under unchanged 9-col header | ✓ VERIFIED | Result dict initialized with None (:782-788); both gates return early without touching those keys; both call `append_panel_row` (:835, :860) before return. `_PANEL_COLUMNS` unchanged (9 columns). Tests 1 and 4 assert both properties — PASSED |
| 7 | tests/m3 = 914/31/0; tests/phase2 = 136/1/0; skips exactly 31 and 1 | ✓ VERIFIED | tests/phase2 RE-RUN by verifier: `136 passed, 1 skipped in 2.16s`. tests/m3 full suite NOT re-run (per verification protocol); evidence log records `914 passed, 31 skipped (838.74s)`; corroborated by `--collect-only` = 945 collected (914+31) and commit timing (GREEN 21:28:59 → docs 21:55:37 = 26.6 min, covers the ~14-min suite + mutation runs) |
| 8 | Hold blocks REPLACED by dated lifted notes; READY-TO-FIRE item 10 carries deferral vocabulary + clause-(d) disclosure duty | ✓ VERIFIED | Range diff 8cbb537..HEAD shows exactly ONE hunk per doc: AGENT-PROMPT hold paragraph replaced; BROWSER-PASTE section retitled `## ✅ STAGE C HOLD LIFTED (2026-08-13)` (body opens "✅ Lifted 2026-08-13, commit d9fbc63" — the documented Rule-1 reconciliation keeping grep -c = 1); READY-TO-FIRE gains one paragraph inside item 10 (:176-218) with the vocabulary + "Post-fire disclosure duty ... at STEP E/F time" |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/python/run_native_ld_panel.py` | `_OCCLUSION_ANOMALY_FRACTION` = 0.0005 module constant, `_DEFAULT_MAX_N_VAR` = 120000, `--max-n-var` flag, two gates in square path | ✓ VERIFIED | Constants at :133/:143 with clause-(d) + diagnosis citations; gates at :830/:853; argparse at :1196-1203 |
| `tests/m3/test_run_native_ld_panel.py` | Section 19 with 7 gate tests, contains `deferred_occlusion_anomaly` | ✓ VERIFIED | Section 19 at :2121-2419; all 7 tests present; `-k` selection collects exactly 7 |
| `260812-ox1-BROWSER-PASTE.md` | Hold replaced by dated LIFTED note with SHA + vocabulary | ✓ VERIFIED | `STAGE C HOLD LIFTED` ×1, `d9fbc63` ×1, stale hold text ×0 |
| `260813-t21-SUMMARY.md` | RED/GREEN/mutation evidence + suite counts + SHAs | ✓ VERIFIED | Full evidence log present; internally consistent (see spot-checks) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `main()` argparse `--max-n-var` | `process_region(max_n_var=...)` | `run_native_ld_panel(max_n_var=...)` | ✓ WIRED | :1219 → :1117 → :1158 → :726; default `_DEFAULT_MAX_N_VAR` at every hop |
| `process_region` square path | `_OCCLUSION_ANOMALY_FRACTION` | MODULE-GLOBAL lookup at eval time | ✓ WIRED | `len(occluded_ids) > _OCCLUSION_ANOMALY_FRACTION * pre_window_n_var` (:853) — plain name reference inside the function body, never a default-arg capture; the 9 monkeypatch pins depend on this and pass |
| `test_max_n_var_default_pins_consumer_ceiling` | `config/pipeline.yaml` `m3_convert_max_n_var` | `yaml.safe_load` in the test | ✓ WIRED | :2390-2393 reads the real YAML; config:393 = 120000; test PASSED |

### Feat-Commit Scope Audit (d9fbc63)

- Driver diff: EXACTLY (A) the two commented constants, (B) `process_region` keyword param, (C) Gate 1 in the LOCKED position/format, (D) Gate 2 in the LOCKED position/format, (E) threading + `--max-n-var` argparse + `--fail-fast` help-text sentence. Nothing else.
- Test diff in d9fbc63: EXACTLY 9 × 3-line pin blocks (`monkeypatch.setattr(drv, "_OCCLUSION_ANOMALY_FRACTION", 0.5)` + 2 comment lines), landing in exactly the 9 tests the plan names (:1665, :1688, :1710, :1738, :1780, :1928, :1972, :2030, :2097 — 5 in section 16, 4 in section 18).
- Status f-strings match the plan's LOCKED formats byte-for-byte.

### Clause-(d) Fidelity

Amendment :61: fires when the count "exceeds 0.05 percent" (pass condition `n_excluded ≤ 0.0005 × n_var`); the region "is NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation."

- Strict `>` ⇔ "exceeds": ✓ (`count == ceiling` stays on the exclude path — boundary test pins this, mutation `>` → `>=` proven red).
- Defer-not-exclude: ✓ — the anomaly path writes NO excludelist, NO manifest, runs NO plink, uploads NO region artifact (gate returns at :861, before all of them; test 1 asserts each absence).
- Disclosed: ✓ — panel row appended on the deferral path (status string carries counts) + stderr line; post-fire deviation-disclosure duty noted in READY-TO-FIRE item 10.
- Fraction 0.0005 = 0.05 percent: ✓.

### Test Verification (verifier re-runs, 2026-08-13)

| Run | Command (smoke_dev python) | Result |
|-----|---------------------------|--------|
| 7 new tests | `pytest tests/m3/test_run_native_ld_panel.py -k "anomaly_gate or feasibility_ceiling or max_n_var_default or fail_fast_halts_on_deferral" -q` | **7 passed**, 63 deselected (3.64s) |
| Plan verify selection | two files, full plan `-k` | **15 passed**, 59 deselected (2.96s) — matches the recorded GREEN verbatim |
| 9 pinned tests by exact name | `-k "<9 names or-joined>"` | **9 passed**, 61 deselected (1.59s) |
| tests/phase2 | `pytest tests/phase2 -q` | **136 passed, 1 skipped** (2.16s) |
| tests/m3 collection | `--collect-only -q` | **945 collected** = 914 + 31 (corroborates the recorded full-suite block without re-running it) |

`git checkout -- tests/m3/sparse_parent_benchmark.tsv` run after the pytest invocations (file was already clean).

### Pin-Removal Loudness (reasoned from code, no edits)

Without a pin, the region-1 fixture (5 occluded / 11 = 45%) trips Gate 2 (5 > 0.0005 × 11 = 0.0055) → the region defers with `deferred_occlusion_anomaly` → each pinned test's assertions (status "ok", excludelist exists, `--exclude` in argv, `.npz` verifies, manifests uploaded) fail loudly. The pin (fraction 0.5: 5 > 5.5 is False) works ONLY because the gate reads the module global at evaluation time — confirmed in the diff.

### Negative-Control Spot-Check (recorded evidence vs code)

Mutation (ii) claim: `>` → `>=` reds EXACTLY `test_occlusion_anomaly_gate_boundary_strict_greater` at `:2289` with `deferred_occlusion_anomaly: 1 occluded of 2000 (ceiling 1)`. Reconciled: the boundary fixture is 1999 plain + 1 deletion → n_var 2000, ceiling int(0.0005 × 2000) = 1; with `>=`, 1 >= 1.0 fires; the sub-ceiling test stays green (1 >= 1.0005 is False) — so single-red is arithmetically forced. `:2289` is the current file's `assert res[0]["status"] == "ok"` line. Mutation (i) (fraction → 1e-9) double-red with "(ceiling 0)" likewise reconciles (int(1e-9 × 2000) = 0). Both consistent.

### Frozen-Surface / Sweep Audit

| Surface | Check | Result |
|---------|-------|--------|
| 3 PY_FROZEN_RELS (`plink_ld_to_npz.py`, `condition_ld_matrix.py`, `occlusion_span_filter.py`) | `git diff 8cbb537..HEAD` | 0 lines |
| `src/legacy/region_analysis/scripts/run_susie_rss.R` | `git diff 8cbb537..HEAD` | 0 lines |
| `.planning/DECISIONS.md` | `git diff 8cbb537..HEAD` | 0 lines (empty — no new decision, matching `decisions: []`) |
| Range file set | `git diff --stat 8cbb537..HEAD` | Exactly the declared set: driver, test file, 3 ox1 docs, HANDOFF.json, t21 PLAN/CONTEXT/SUMMARY. STATE.md absent = documented deviation 1 (orchestrator-reserved) |
| HANDOFF.json | full diff | One line: baseline 907 → 914 with provenance chain; phase2 line + skip rule untouched |

### Runbook-Doc Byte Checks

| Check | AGENT-PROMPT | BROWSER-PASTE | READY-TO-FIRE |
|-------|-------------|---------------|---------------|
| `grep -c "STAGE C HOLD LIFTED"` | 1 | 1 | 0 (item-10 paragraph, by design) |
| `grep -c "ADDITIONALLY HELD\|Wait for the repo update"` | 0 | 0 | 0 |
| carries `d9fbc63` | 1 | 1 | 1 |
| `grep -c 'gs://$'` (never-prefix violation) | 0 | 0 | 0 |
| Poll / never-prefix / 276-not-a-pass-bar regions | untouched (single hunk only) | untouched (single hunk only) | untouched (single hunk only) |

The 276-not-a-pass-bar phrasing and the WORKSPACE_BUCKET never-prefix content remain present in all applicable files; the range diff contains no hunk touching them.

### Zero Perimeter

- Range diff of the two code files: no unmocked `gsutil`/`gcloud`/`bq`/`wb` invocation in added lines — the only gs interactions in the new tests go through `_MockGsutil` via `monkeypatch.setattr(drv, "_run_gsutil", ...)`.
- Verifier's own runs: pytest + git + grep only; $0, no perimeter contact.

### Anti-Patterns Found

None. No TODO/FIXME/placeholder in the added code; no stubbed handlers; the SUMMARY's "Known Stubs: None" claim holds.

### Deviations (documented, accepted)

1. STATE.md not updated in commit 3 — orchestrator-reserved surface; SUMMARY documents the handoff. Not a gap.
2. BROWSER-PASTE note body opens "✅ Lifted ..." instead of repeating the heading phrase — required to satisfy the plan's own `grep -c = 1` verify gate; content otherwise identical. Not a gap.
3. RED test 5's observed failure mode was the TypeError against the pre-implementation signature rather than the plan-predicted spy-count failure — recorded honestly in the SUMMARY; the 5-red/2-green split held. Not a gap.

### Gaps Summary

None. All 8 must-have truths verified; both gates live in the LOCKED positions with the LOCKED status strings; clause-(d) semantics faithful to the amendment text; the carried-back-number pin enforces producer/consumer ceiling equality via a real YAML read; frozen surfaces 0-diff; runbook byte-checks all green; zero perimeter contact.

---

_Verified: 2026-08-13T22:30:00-04:00_
_Verifier: Claude (gsd-verifier)_
