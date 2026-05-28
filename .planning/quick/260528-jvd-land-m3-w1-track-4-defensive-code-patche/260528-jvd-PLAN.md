---
quick_id: 260528-jvd
description: Land m3-W1 Track 4 defensive-code patches per HANDOFF + debug analysis
mode: quick
date: 2026-05-28
status: ready_for_execution
must_haves:
  truths:
    - "_validate_checkpoint_populated(uri) helper exists in src/python/aou_ld_panel.py and verifies _SUCCESS + entries/entries/parts/ contents + Hail count_rows>0"
    - "auto-resume state machine at aou_ld_panel.py:554 and :572 calls _validate_checkpoint_populated() instead of _has_checkpoint() — stub MT with _SUCCESS but empty entries no longer triggers RESUME"
    - "Each of the 3 mt.checkpoint() write sites (lines ~641, ~667, ~687) has a post-write assertion that count_rows()>0 AND count_cols()>0 before continuing"
    - "3 new regression tests exist in tests/m3/test_aou_ld_panel_local.py: test_validate_checkpoint_populated_rejects_stub_entries, test_validate_checkpoint_populated_rejects_empty_entries_dir, test_has_checkpoint_vs_validate_diverge_on_stub_mt"
    - "AOU-1_template.ipynb has 3 new bucket-state assertion cells (3.5 / 4.5 / 5.5) between load_qc_cohort calls that gsutil-du-assert entries/entries/parts/ size > minimum threshold"
    - "WAVE-1-CLOSEOUT-CHECKLIST.md STEP 3 verifies entries/ size, not just _SUCCESS marker"
    - "m3-CONTEXT.md has new D-M3-10 decision block documenting the new verification protocol (cross-references catastrophe + memories)"
  artifacts:
    - .planning/quick/260528-jvd-land-m3-w1-track-4-defensive-code-patche/260528-jvd-PLAN.md
    - .planning/quick/260528-jvd-land-m3-w1-track-4-defensive-code-patche/260528-jvd-SUMMARY.md
    - src/python/aou_ld_panel.py
    - tests/m3/test_aou_ld_panel_local.py
    - .planning/notebooks/AOU-1_template.ipynb
    - .planning/WAVE-1-CLOSEOUT-CHECKLIST.md
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
  key_links:
    - .planning/debug/m3-W1-empty-mt-catastrophe.md (root-cause analysis — patches 1-7 specified in §Fix Strategy)
    - .planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md (§Track 4 — patch list)
    - .planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-SUMMARY.md (refactor that introduced the unsafe _has_checkpoint() resume gate)
---

# PLAN — Track 4 defensive-code patches (m3-W1 empty-MT catastrophe)

## Goal

Land 7 defensive-code patches so any future fire (AoU credit-recovered OR grant-funded OR another researcher) cannot reproduce the m3-W1 silent empty-MT pattern. These patches are INDEPENDENT of the LD-panel pivot decision (Track 2) and the AoU credit claim (Track 1) — apply REGARDLESS of which substrate path Wave 2 ends up taking.

**Root failure being defended against:**
Hail's `mt.checkpoint()` writes `_SUCCESS` based on driver-side task-completion accounting, NOT contents validation. Under aggressive `spark.executor.cores=1/mem=5g` profile (needed for v8 partition explosion), an executor can silently truncate after writing Parquet schema footers but before writing entries row-group payloads, leaving a populated-looking MT directory with zero actual data. The 2026-05-21 inspection of `gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt/` exposed this: `_SUCCESS` present + 2,045 partition stubs (~35 bytes each = Parquet footer size) + `entries/entries/parts/` absent + `count_rows()=0` + `count_cols()=0`. The refactored `load_qc_cohort` at HEAD does NOT defend against this — `_has_checkpoint()` only checks `_SUCCESS` existence, so a stub MT triggers `RESUME_FROM_POST_SAMPLE_QC` and Phase 3 fires `variant_qc` on an empty MT, producing another empty `_SUCCESS`-marked MT. Patches break the contract: `_validate_checkpoint_populated()` checks `_SUCCESS` + entries-dir presence + minimum-byte-size, and post-write assertions raise loudly inside `load_qc_cohort` when Hail returns from `mt.checkpoint()` with empty contents.

## Tasks (7 atomic commits, TDD-disciplined)

### Task 1 (RED) — Add 3 failing regression tests for _validate_checkpoint_populated

**files:**
- tests/m3/test_aou_ld_panel_local.py

**action:**
Append 3 tests after the `test_has_checkpoint_*` block (line 382):

1. `test_validate_checkpoint_populated_rejects_stub_entries(tmp_path)` — creates a fake MT directory with `_SUCCESS` + `rows/rows/parts/part-00000-X.parquet` of size 35 bytes (Parquet footer stub) + NO `entries/entries/parts/` directory; asserts `_validate_checkpoint_populated` returns False.
2. `test_validate_checkpoint_populated_rejects_empty_entries_dir(tmp_path)` — same as above but with an EMPTY `entries/entries/parts/` directory present; asserts False.
3. `test_has_checkpoint_vs_validate_diverge_on_stub_mt(tmp_path)` — creates the catastrophe-pattern stub MT; asserts `_has_checkpoint()` returns True AND `_validate_checkpoint_populated()` returns False (documents the contract diverge).

Tests use `file://` URI pattern, `tmp_path` fixture. RED state: imports `_validate_checkpoint_populated` which does not exist → ImportError on test collection.

**verify:**
- `pytest tests/m3/test_aou_ld_panel_local.py -k validate_checkpoint_populated --collect-only` → collection succeeds (or errors on missing import — that IS the RED state)
- `pytest tests/m3/test_aou_ld_panel_local.py -k "validate_checkpoint_populated or diverge_on_stub_mt"` → fails (ImportError or AssertionError)

**done:** atomic commit `test(m3-W1): RED regression tests for _validate_checkpoint_populated (Track 4 patch 1/7)`

### Task 2 (GREEN) — Add _validate_checkpoint_populated() helper

**files:**
- src/python/aou_ld_panel.py (insert helper between `_has_checkpoint` at line 449 and `load_qc_cohort` at line 481)

**action:**
Add `_validate_checkpoint_populated(uri: str, *, min_entries_bytes: int = 1024) -> bool`:
- First check `_has_checkpoint(uri)` — returns False if `_SUCCESS` absent (preserves existing contract).
- Then check `entries/entries/parts/` directory exists AND contains ≥1 file > `min_entries_bytes` (default 1 KB filters out 35-byte Parquet footer stubs).
- Scheme dispatch matches `_has_checkpoint`: `file://` uses `pathlib`, all other URIs defer to `hl.hadoop_ls` + `hl.hadoop_is_dir`.
- Defensive `try/except`: any FS error → returns False (safer to redo work than assume populated checkpoint that may not exist).
- Docstring cross-references `[[feedback_aou_success_marker_not_evidence_of_data]]` + `[[feedback_hail_checkpoint_contract_violation]]` memories.

**verify:**
- 3 Task 1 tests now PASS (`pytest tests/m3/test_aou_ld_panel_local.py -k "validate_checkpoint_populated or diverge_on_stub_mt"` → 3 passed)
- All other existing tests still pass: `pytest tests/m3/test_aou_ld_panel_local.py -k "not (validate_checkpoint or diverge_on_stub_mt or compute_region_ld or aou_driver or synthetic_mt or auto_resume or auto_recovers or force_fresh_bypasses or sidecar_mismatch)"` — all pure-Python tests still GREEN

**done:** atomic commit `feat(m3-W1): _validate_checkpoint_populated helper (Track 4 patch 2/7)`

### Task 3 — Swap _has_checkpoint() → _validate_checkpoint_populated() in auto-resume

**files:**
- src/python/aou_ld_panel.py (lines 554, 572)

**action:**
Replace `if _has_checkpoint(ckpt_post_sqc):` (line 554) with `if _validate_checkpoint_populated(ckpt_post_sqc):` and `elif _has_checkpoint(ckpt_post_split):` (line 572) with `elif _validate_checkpoint_populated(ckpt_post_split):`. A stub MT (`_SUCCESS` present + empty entries) now FAILS the resume gate → state machine falls through to `auto_fresh = True` recovery path (via the existing "MT present but sidecar absent" code path — _validate returns False for stub, the elif chain skips, state stays FRESH, write proceeds with `overwrite=overwrite_flag` which is False unless force_fresh). Better: explicitly log WARN + set `auto_fresh = True` when `_has_checkpoint(uri)` returns True but `_validate_checkpoint_populated(uri)` returns False (stub-MT case).

**verify:**
- All existing pure-Python tests still pass: `pytest tests/m3/test_aou_ld_panel_local.py -k "checkpoint_uri or normalize_bucket or sidecar or validate_checkpoint_populated"` — all GREEN
- Grep confirms no stale `_has_checkpoint(ckpt_` calls remain in `load_qc_cohort` body: `grep "_has_checkpoint(ckpt_" src/python/aou_ld_panel.py` → 0 hits

**done:** atomic commit `fix(m3-W1): replace _has_checkpoint with _validate_checkpoint_populated in auto-resume (Track 4 patch 3/7)`

### Task 4 — Add post-write count_rows/count_cols assertions at 3 mt.checkpoint() sites

**files:**
- src/python/aou_ld_panel.py (lines ~641, ~667, ~687 — intermediate 1, intermediate 2, final)

**action:**
After each `mt = mt.checkpoint(uri, overwrite=...)` call, insert a post-write contents assertion:
```python
# Post-write contents validation — defense against the W1 empty-MT
# catastrophe (Hail _SUCCESS contract violation; see
# [[feedback_hail_checkpoint_contract_violation]]).
_n_rows = mt.count_rows()
_n_cols = mt.count_cols()
if _n_rows == 0 or _n_cols == 0:
    raise RuntimeError(
        f"checkpoint at {uri} returned empty MT: "
        f"{_n_rows} rows × {_n_cols} cols. Hail's mt.checkpoint() "
        f"wrote _SUCCESS but contents are missing. See "
        f".planning/debug/m3-W1-empty-mt-catastrophe.md."
    )
```
Apply to all 3 sites: ckpt_post_split, ckpt_post_sqc, final ckpt. NOT a soft assert — raise loudly. Cell 7's `count_rows()` would have caught the W1 failure 36h earlier; this builds that check INSIDE `load_qc_cohort`.

**verify:**
- Pure-Python tests still pass: `pytest tests/m3/test_aou_ld_panel_local.py -k "checkpoint_uri or normalize_bucket or sidecar or validate_checkpoint_populated"` — GREEN
- Grep confirms 3 post-write blocks: `grep -c "checkpoint at .* returned empty MT" src/python/aou_ld_panel.py` → 3

**done:** atomic commit `feat(m3-W1): post-write count_rows/count_cols assertions at 3 mt.checkpoint() sites (Track 4 patch 4/7)`

### Task 5 — Insert Cell 3.5 / 4.5 / 5.5 bucket-state assertion cells in AOU-1_template.ipynb

**files:**
- .planning/notebooks/AOU-1_template.ipynb

**action:**
Insert 3 new code cells immediately after Cells 3, 4, 5 (the load_qc_cohort calls). Each cell fires `gsutil du -s` against the bucket URI matching the prior cell's ancestry/sensitivity, asserts entries-dir size > 1 GB (population threshold; sensitivity cohorts smallest at ~5-20 GB; primary AFR ~10-40 GB; EUR ~20-100 GB), prints OK line. Cell template per debug §Fix Strategy.3:
```python
# Cell N.5 — Mandatory post-write bucket-contents validation.
# m3-W1-empty-mt-catastrophe regression guard.
# See .planning/debug/m3-W1-empty-mt-catastrophe.md + memories
# [[feedback_aou_success_marker_not_evidence_of_data]] +
# [[feedback_hail_checkpoint_contract_violation]].
import subprocess
from aou_ld_panel import _qc_checkpoint_uri
bucket_uri = _qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr', False)  # match cell args
r = subprocess.run(
    ['gsutil', 'du', '-s', bucket_uri + '/entries/entries/parts/'],
    capture_output=True, text=True
)
assert r.returncode == 0, f"bucket inspection failed: {r.stderr}"
size_bytes = int(r.stdout.split()[0])
assert size_bytes > 10**9, (
    f"MT entries at {bucket_uri} is only {size_bytes} bytes — "
    f"expected GB-scale (catastrophe regression guard). Stop here; "
    f"do NOT proceed to next cell."
)
print(f"OK: {bucket_uri} populated ({size_bytes / 10**9:.1f} GB)")
```
3 variants: (3.5) afr primary, (4.5) afr sensitivity, (5.5) eur primary. nbformat 4 minor 5; cell type "code"; empty outputs/execution_count nulls.

**verify:**
- `python3 -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb')); src=' '.join(' '.join(c['source']) for c in nb['cells']); print('Cell 3.5 marker:', 'Cell 3.5' in src); print('Cell 4.5 marker:', 'Cell 4.5' in src); print('Cell 5.5 marker:', 'Cell 5.5' in src)"` → all True
- nbformat round-trip clean: `python3 -c "import nbformat; nbformat.validate(nbformat.read('.planning/notebooks/AOU-1_template.ipynb', as_version=4))"` → no error

**done:** atomic commit `feat(m3-W1): AOU-1 bucket-state assertion cells 3.5/4.5/5.5 (Track 4 patch 5/7)`

### Task 6 — Update WAVE-1-CLOSEOUT-CHECKLIST.md STEP 3 to verify entries/ size

**files:**
- .planning/WAVE-1-CLOSEOUT-CHECKLIST.md (STEP 3 block starting line 91)

**action:**
Replace the existing `_SUCCESS` + `metadata.json.gz` listing loop with a stronger verification that ALSO checks `entries/entries/parts/` size. Add explicit failure-mode note: "_SUCCESS alone is NOT sufficient — see m3-W1 catastrophe 2026-05-21 + memory [[feedback_aou_success_marker_not_evidence_of_data]]". Pass criteria upgraded: `entries/` > 1 GB AND `gsutil cat metadata.json.gz | gunzip` parses with canonical Hail keys. Add WARN block: "If _SUCCESS present but entries/ small/absent, this is the empty-MT catastrophe pattern; bucket data is unusable; do NOT mark Wave-1 complete."

**verify:**
- `grep -c "entries/entries/parts" .planning/WAVE-1-CLOSEOUT-CHECKLIST.md` → ≥ 1
- `grep -c "feedback_aou_success_marker_not_evidence_of_data\|m3-W1 catastrophe" .planning/WAVE-1-CLOSEOUT-CHECKLIST.md` → ≥ 1

**done:** atomic commit `docs(m3-W1): closeout checklist STEP 3 verifies entries/ size not just _SUCCESS (Track 4 patch 6/7)`

### Task 7 — Add D-M3-10 decision token to m3-CONTEXT.md

**files:**
- .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md (append to `<decisions>` block before `</decisions>`, after D-M3-09)

**action:**
Append `D-M3-10: MT write verification protocol — contents-validated, not _SUCCESS-only` decision block. Format matches existing D-M3-XX entries (Decision + Why + How to apply). Cross-reference: catastrophe debug + 2 new memories + Track 4 patch list. Make explicit: any future MT write touchpoint (Wave 1 rebuild, Wave 2 LD outputs, Wave 4 production fire) MUST go through `_validate_checkpoint_populated()` OR equivalent contents-validation gate. No new code-side `_has_checkpoint()` callers may be introduced.

Also append echo entry to `<assumptions>` block (per the D-M3-03/D-M3-09 echo pattern documented at line 305-306).

**verify:**
- `grep -c "^### D-M3-10" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` → 1
- `grep -c "D-M3-10" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` → ≥ 2 (header + assumption echo)

**done:** atomic commit `decision(m3-W1): D-M3-10 MT write verification protocol (Track 4 patch 7/7)`

## Verify-mode (closeout, not a separate task)

After all 7 commits:
1. `git log --oneline -8` → 7 new atomic commits with `(m3-W1)` tokens + the `(Track 4 patch N/7)` suffix
2. `pytest tests/m3/test_aou_ld_panel_local.py -k "validate_checkpoint or diverge_on_stub or checkpoint_uri or normalize_bucket or sidecar or canonical_ordering or static_ast or gitignore or env_yaml or r_env" -v` → all GREEN (no regression)
3. Final docs commit (STATE.md row + SUMMARY.md) via gsd-tools commit pipeline

## Out of scope

- Live-Hail tests (the 5 resilience tests at lines 494-681 + a new test_load_qc_cohort_post_write_assertion_fires): SKIPPED here. Live-Hail tests need a Hail install. Per [[project_python_311_pin]], no Hail in smoke_dev; AoU env is deleted. The post-write assertion will fire on the AoU side at next fire; pure-Python regression coverage is sufficient guard for this landing.
- chr22 smoke test (Live AoU validation): blocked on Track 1 (credit recovery) or future grant funding. Patches MUST land BEFORE chr22 smoke or any rebuild.
- AOU-2 / AOU-4 notebook bucket-state assertions: separate concern (their inputs are MT reads, not new MT writes). Track 5 / future quick task.
- Memory bake for the new D-M3-10 decision: optional follow-on (the existing 2 catastrophe memories already cover the underlying class).
- Track A artifacts (per [[track_a_submission_in_progress]] + [[feedback_stop_asking_track_a]]): explicit DO-NOT-TOUCH.
