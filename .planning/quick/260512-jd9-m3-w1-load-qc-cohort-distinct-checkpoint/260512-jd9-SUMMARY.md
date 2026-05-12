---
phase: m3-aou-afr-ld-panel-build
plan: 260512-jd9
type: execute
wave: 1
mode: quick
status: COMPLETE
completed: 2026-05-12T18:10:15Z
commit: 36e8062
parent_commit: 8cc6f64
branch: main
pushed_to: origin/main
subject_token: m3-W1-checkpoint-suffix
framing: audit-driven re-analysis (pre-existing bug surfaced)
files_modified:
  - src/python/aou_ld_panel.py
  - tests/m3/test_aou_ld_panel_local.py
  - .planning/STATE.md
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
tdd_evidence:
  red_log: /tmp/m3-W1-checkpoint-suffix-RED.log
  green_log: /tmp/m3-W1-checkpoint-suffix-GREEN.log
  final_log: /tmp/m3-W1-checkpoint-suffix-FINAL.log
  red_result: "4 failed, 10 deselected — all 4 with ImportError: cannot import name '_qc_checkpoint_uri'"
  green_result: "4 passed, 10 deselected"
  final_result: "10 passed, 4 skipped (live-hail tests gracefully skip without hail locally)"
---

# Quick Task 260512-jd9: m3-W1 load_qc_cohort distinct-checkpoint suffix

**One-liner:** Audit-driven re-analysis surfaced a pre-existing producer/consumer drift in `load_qc_cohort()`'s checkpoint-URI construction (ignored `sensitivity` flag, silently overwrote primary AFR checkpoint when sensitivity=True fired) — remediated under TDD via a reusable `_qc_checkpoint_uri` helper + 4 regression-guard tests, committed atomically with STATE.md refresh, and pushed to `origin/main` mid-flight during the in-flight AOU-1 notebook Cell 3 run so Carter's `git pull` will land the fix before Cell 4 fires.

## Bug Surfaced

**Where:** `src/python/aou_ld_panel.py:251` (pre-rebase line numbering)
```python
ckpt = f"gs://{bucket}/ld/mt_{ancestry}_qc.mt"   # BUG: ignored `sensitivity`
mt = mt.checkpoint(ckpt, overwrite=True)
```

**When caught:** 2026-05-12 during the W1 AOU-1 cohort-definition notebook fire on the AoU Workbench. Cell 3 (primary AFR, sensitivity=False) was running on Dataproc at the time of detection (started 2026-05-12T17:21:28Z, ~45-90 min envelope). Without remediation, Cell 4 (sensitivity=True) would have silently overwritten Cell 3's checkpoint at the shared `mt_afr_qc.mt` URI with `overwrite=True`.

**How caught:** The W1 must_have explicitly requires three distinct MTs — `mt_afr_qc.mt` (primary AFR) + `mt_afr_pca_selfid_qc.mt` (sensitivity AFR per D-M3-07) + `mt_eur_qc.mt` (EUR parity per D-M3-01). Three downstream consumers (AOU-1 Cell 7 cohort_summary table, AOU-2 per_region_ld.ipynb, AOU-4 validation.ipynb) already reference the canonical `mt_afr_pca_selfid_qc.mt` path, but the producer `load_qc_cohort` was the drift point — the `sensitivity` flag was a no-op for checkpoint URI construction.

## Patch Summary

Three edits to `src/python/aou_ld_panel.py`:

1. **Helper extracted** (per [[feedback_extract_reusable_utilities]]) — top-level `_qc_checkpoint_uri(bucket, ancestry, sensitivity) -> str` inserted just before `load_qc_cohort`:
   ```python
   def _qc_checkpoint_uri(bucket: str, ancestry: str, sensitivity: bool) -> str:
       suffix = "_pca_selfid_qc" if sensitivity else "_qc"
       return f"gs://{bucket}/ld/mt_{ancestry}{suffix}.mt"
   ```

2. **Line-251 swap** — inline f-string replaced with helper call (sensitivity now honored):
   ```python
   ckpt = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
   mt = mt.checkpoint(ckpt, overwrite=True)
   ```

3. **Module docstring step 8 update** — preserves audit-trail truth that the docstring matches executable code:
   ```
   8. mt = mt.checkpoint(_qc_checkpoint_uri(bucket, ancestry, sensitivity))
      # path: gs://${WORKSPACE_BUCKET}/ld/mt_{ancestry}[_pca_selfid]_qc.mt
   ```

Four regression-guard tests added to `tests/m3/test_aou_ld_panel_local.py` (static-source section, after `test_gitignore_has_explicit_aou_entries`, before live-hail divider):
- `test_qc_checkpoint_uri_primary_afr` — pins `mt_afr_qc.mt` for sensitivity=False
- `test_qc_checkpoint_uri_sensitivity_afr` — pins `mt_afr_pca_selfid_qc.mt` for sensitivity=True
- `test_qc_checkpoint_uri_eur_primary` — pins `mt_eur_qc.mt` for EUR parity
- `test_qc_checkpoint_uri_distinct_paths_regression` — **load-bearing regression guard**: AFR primary != AFR sensitivity (prevents this bug class from recurring)

## TDD Evidence

**RED step** (`/tmp/m3-W1-checkpoint-suffix-RED.log`):
```
collected 14 items / 10 deselected / 4 selected
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_primary_afr FAILED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_sensitivity_afr FAILED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_eur_primary FAILED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_distinct_paths_regression FAILED
E       ImportError: cannot import name '_qc_checkpoint_uri' from 'aou_ld_panel'
======================= 4 failed, 10 deselected in 4.62s =======================
```
Confirmed: exactly 4 failures, all with the canonical `ImportError: cannot import name '_qc_checkpoint_uri'` signature. RED phase locked in TDD discipline before any production-code edits.

**GREEN step** (`/tmp/m3-W1-checkpoint-suffix-GREEN.log`):
```
collected 14 items / 10 deselected / 4 selected
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_primary_afr PASSED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_sensitivity_afr PASSED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_eur_primary PASSED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_distinct_paths_regression PASSED
======================= 4 passed, 10 deselected in 0.03s =======================
```

**Full-file final** (`/tmp/m3-W1-checkpoint-suffix-FINAL.log`, run post-rebase to confirm no merge-resolution regression):
```
collected 14 items
6 existing static-source tests PASSED
4 new qc_checkpoint_uri tests PASSED
4 live-hail tests SKIPPED (no hail locally — graceful degrade)
======================== 10 passed, 4 skipped in 0.22s =========================
```

**Plan-grep invariants:**
- `grep -c "_qc_checkpoint_uri" src/python/aou_ld_panel.py` = **3** (helper def + line-251 callsite + docstring reference) ✓ (>= 3 required)
- `grep -c "_pca_selfid_qc" src/python/aou_ld_panel.py` = **2** (helper suffix branch + docstring path comment) ✓ (>= 1 required)
- `grep -c "def test_qc_checkpoint_uri" tests/m3/test_aou_ld_panel_local.py` = **4** ✓ (exactly 4 required)

## Count-Accounting Nit (Not a Regression)

The PLAN.md anticipated "7 existing + 4 new = 11 static-source tests" but the actual count is **6 existing + 4 new = 10**. The existing static-source tests in the file at execution time are: `test_env_yaml_pins_python_311`, `test_r_env_yaml_has_reticulate`, `test_canonical_ordering_split_before_variant_qc`, `test_uses_verified_env_var_names`, `test_static_ast_calls_present`, `test_gitignore_has_explicit_aou_entries` — six, not seven. The substantive invariant (zero FAILED, all existing static tests still pass, all 4 new tests pass) holds. The plan's literal count was off by one; the patch is sound.

## Commit + Push Confirmation

- **Commit hash (post-rebase):** `36e8062ef06571cead4e9f88551cf8746266be6c`
- **Pre-rebase hash:** `f3bd72a` (rebased atop `8cc6f64` from origin/main — origin had a fresh m3-W2 RegionPool OOM remediation commit that did NOT touch the 3 files in this commit; rebase was clean, no conflicts)
- **Parent on origin:** `8cc6f64` (fix(m3-aou-afr-ld-panel): re-apply m3-W2 Hail RegionPool OOM remediation)
- **HEAD == origin/main:** ✓ confirmed via `git rev-parse HEAD` == `git rev-parse origin/main`
- **Subject token:** `(m3-W1-checkpoint-suffix)` ✓
- **Framing:** body contains "audit-driven re-analysis" (x2); zero forbidden tokens (`cleanup`, `revision`, `salvage`) per [[feedback_original_research_framing]]
- **Staging discipline:** explicit `git add` of 3 files per [[feedback_multi_terminal_staging]] (NEVER `git add .` / `-A` on GPFS shared tree); out-of-scope `.claude/settings.json` + `.planning/config.json` modifications left unstaged and stashed/restored cleanly through the rebase

## STATE.md Refresh

Per [[feedback_state_md_keep_current]], STATE.md was refreshed atomically in the same commit:
- Frontmatter `last_updated` advanced from `2026-05-12T00:00:00.000Z` to `2026-05-12T18:10:15.000Z`
- Frontmatter `last_activity` confirmed at `2026-05-12`
- New "Mid-flight remediation note" paragraph appended in the 2026-05-12 Session Continuity entry (after the existing pre-fire halt-and-surface entry's Resume file line); references the quick plan path, the 3 patch edits, the 4 regression tests, the TDD evidence, and the commit token

The "Quick Tasks Completed" TABLE ROW is NOT added here — the orchestrator (`/gsd-quick` workflow Step 8) adds that row in a separate docs commit.

## Caveats / Follow-ups

1. **NCSU template notebook drift (separate follow-up):** `.planning/notebooks/AOU-1_template.ipynb` Cell 1 still uses the older `init_hail()` wrapper invocation (does not thread `spark_conf=` per DEC-2026-05-04-01 `spark.executor.cores=1` patch). The AoU-side notebook (Carter's live Workbench instance) already has the spark_conf patch. The NCSU template is read-only reference; a separate `/gsd-quick` after Cell 3 lands should sync it. (Confirmed via plan instructions: the AOU-1_template.ipynb Cell-7 already references `mt_afr_pca_selfid_qc.mt`, so its consumer-side expectations are correct — only the producer-side Cell 1 needs sync.)

2. **AOU-1_template.ipynb Cell-7 consumer alignment:** Already references the canonical `mt_afr_pca_selfid_qc.mt` path — this patch closes the producer/consumer drift, so the template's Cell 7 will read the correct sensitivity-cohort checkpoint going forward.

## Carter Next-Action

Before Cell 4 fires in the AoU workspace:

```bash
# In the AoU workspace terminal (after Cell 3 completes):
cd /path/to/coloc_analysis  # AoU workspace clone
git pull origin main
```

This will land commit `36e8062` (the patched `_qc_checkpoint_uri` helper) in the AoU workspace clone. Cell 4 (sensitivity=True AFR cohort) will then write to `gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt` instead of silently overwriting Cell 3's `mt_afr_qc.mt` checkpoint.

## Honest-Framing Statement

This work is **audit-driven re-analysis of a pre-existing producer/consumer drift bug**, not cleanup, revision, or salvage. The bug was latent in the original `load_qc_cohort` implementation from the m3-W1 driver build; the W1 fire surfaced it before any silent-overwrite damage occurred. The TDD discipline (RED first with observed ImportError; GREEN second with observed 4-pass) preserves an executable audit trail of the remediation.

## Self-Check: PASSED

- [x] src/python/aou_ld_panel.py contains `_qc_checkpoint_uri` (3 occurrences: helper def + callsite + docstring reference)
- [x] tests/m3/test_aou_ld_panel_local.py contains 4 new `test_qc_checkpoint_uri_*` tests
- [x] .planning/STATE.md frontmatter `last_updated` advanced + Session Continuity mid-flight note appended
- [x] Commit `36e8062` exists in local git log AND on origin/main (HEAD == origin/main confirmed)
- [x] Subject token `(m3-W1-checkpoint-suffix)` present in commit subject
- [x] Body contains `audit-driven re-analysis`; zero forbidden tokens (cleanup, revision, salvage)
- [x] Push to origin/main landed before Cell 4 fires (timestamp 2026-05-12T18:10:15Z; Cell 3 envelope ends ~18:06-18:51Z)
- [x] 4 new tests PASS; 6 existing static-source tests PASS; 4 live-hail tests SKIP gracefully; zero FAILED
- [x] No new files committed beyond the 3 declared in `files_modified`
- [x] Explicit `git add` paths used (no `git add .` / `-A`)
