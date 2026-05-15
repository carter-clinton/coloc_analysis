---
phase: m3-aou-afr-ld-panel-build
plan: 260514-npb
type: execute
wave: 1
mode: quick
status: COMPLETE
completed: 2026-05-15T01:45:00Z
commit_hpc: 243ebae  # HPC main lineage
commit_origin: 779fe84  # cherry-picked onto origin/main lineage (clean fast-forward)
parent_commit_origin: 7ddafb6
branch: main
pushed_to: origin/main
subject_token: m3-W1-bucket-prefix-defensive
framing: audit-driven re-analysis (pre-existing producer/consumer drift at helper-notebook integration boundary)
files_modified:
  - src/python/aou_ld_panel.py
  - tests/m3/test_aou_ld_panel_local.py
  - .planning/notebooks/AOU-1_template.ipynb
  - .planning/STATE.md
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
tdd_evidence:
  red_log: /tmp/m3-W1-bucket-prefix-RED.log
  green_log: /tmp/m3-W1-bucket-prefix-GREEN.log
  red_result: "6 FAILED, 14 deselected -- 5 ImportError on _normalize_bucket + 1 AssertionError empirically reproducing the gs://gs:// double-prefix bug"
  green_result: "16 PASSED, 4 SKIPPED (live-hail tests skip gracefully without hail locally)"
aou_side_verification:
  status: GREEN
  evidence: "Cell 1b PATCH VERIFICATION block emitted single-gs:// URIs (gs://fc-secure-f72fd8d8-.../ld/mt_*.mt), NOT gs://gs://gs://-prefixed double-protocol form. cores=1 OK assert PASSED. Hail 0.2.134 attached to fresh 16-worker Dataproc cluster."
  cell_3_status: GREENLIT (fired post-verification)
forensic_artifacts:
  - "gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/forensics/AOU-1_cohort_definition.ipynb.pre-bucket-prefix-fix.bak.20260515T012956Z (autosaved-with-malformed-output state from prior Cell 1b run; reviewer-verifiable evidence of the bug we just fixed)"
  - "gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/forensics/2c6dbee-forensic-20260515T012956Z/ (commit object + reflog metadata for AoU clone's stale origin/main ref, preserved before hard-reset reconciliation)"
---

# Quick Task 260514-npb: m3-W1 bucket-prefix defensive normalization

**One-liner:** Audit-driven re-analysis surfaced a pre-existing producer/consumer drift at the helper-notebook integration boundary: `_qc_checkpoint_uri(bucket, ...)` (extracted 2026-05-12 by 260512-jd9) expected bare bucket name per its test contract, but AOU-1 template Cell 1b + Cell 7 callers passed AoU's prefixed `$WORKSPACE_BUCKET` env var (`gs://fc-secure-...`), producing malformed `gs://gs://fc-secure-.../ld/mt_*.mt` double-protocol-prefix URIs. Remediated under TDD via defensive `_normalize_bucket` utility + 6 regression tests, committed atomically with STATE.md refresh, pushed to origin/main, and empirically verified GREEN on AoU Workbench (Cell 1b PATCH VERIFICATION block now emits single-`gs://` URIs).

## Bug Surfaced

**Where:** `src/python/aou_ld_panel.py:160` (pre-fix line numbering)
```python
def _qc_checkpoint_uri(bucket: str, ancestry: str, sensitivity: bool) -> str:
    suffix = "_pca_selfid_qc" if sensitivity else "_qc"
    return f"gs://{bucket}/ld/mt_{ancestry}{suffix}.mt"  # BUG: prepends gs:// unconditionally
```

**How it surfaced:** AOU-1 Cell 1b PATCH VERIFICATION (added by 260512-ldj specifically to catch this class of issue before compute fire):
```python
print(f"  AFR primary URI     : {_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr', False)}")
```
With `os.environ['WORKSPACE_BUCKET']` = `gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a` (AoU-set, prefixed), the f-string substitution produces:
```
gs:// + gs://fc-secure-f72fd8d8-.../  -> gs://gs://fc-secure-f72fd8d8-.../ld/mt_afr_qc.mt
```
Empirically confirmed via Cell 5 of scratch_bootstrap_260514.ipynb on AoU side (using `repr()` to disambiguate Jupyter rendering artifact that initially read as 3-slash).

**Why production-critical:** `load_qc_cohort` at `aou_ld_panel.py:275` uses the same helper for the actual checkpoint write path. Cell 3 fire (primary AFR cohort) under the prior bare-only contract would have written to a malformed URI -- either failed at the GCS-write boundary (best case, fail-loud) or silently landed in a wrong prefix interpretation (worst case). The 260512-ldj PATCH VERIFICATION block caught this at the helper-print boundary BEFORE any compute spend.

**Why 260512-jd9 tests didn't catch it:** All 4 existing tests pass bare `"test-bucket"` -- exactly per the documented helper contract. No test asserted the notebook->helper integration with the AoU-runtime-prefixed env var. Classic test-gap at the integration boundary; today's quick adds 6 tests to close that gap.

## Blast Radius (full grep + cross-file trace)

**Same-bug call sites in production code (BOTH FIXED in this commit):**
1. `aou_ld_panel.py:160` -- `_qc_checkpoint_uri` helper (production write path via load_qc_cohort line 275)
2. `aou_ld_panel.py:513` -- CLI main() BlockMatrix-write `out_bucket = f"gs://{ws}/ld/{anc_upper}_aou"` (Wave-2 production path; same `f"gs://{prefixed-bucket}/..."` pattern)

**Same-bug notebook display sites (FIXED via Cell 7 refactor in this commit):**
3. `.planning/notebooks/AOU-1_template.ipynb:184-186` -- Cell 7 cohort_summary inline f-strings (3 sites)

**Same-bug Wave-2 surface (DEFERRED -- separate follow-up /gsd-quick):**
4. `.planning/notebooks/AOU-2_per_region_ld.ipynb:51-52` -- read paths
5. `.planning/notebooks/AOU-2_per_region_ld.ipynb:64-65` -- OUT_BUCKET_AFR/EUR write-path construction
6. `.planning/notebooks/AOU-2_per_region_ld.ipynb:134-136` -- gsutil shell commands with bash-style interpolation

**Same-bug doc-comment cleanup (DEFERRED -- separate follow-up /gsd-quick):**
7. `.planning/notebooks/AOU-1_template.ipynb:114, 132, 150` -- misleading `gs://${WORKSPACE_BUCKET}/...` bash-style documentation (documentation only, not executable)

**Defensive-contract reference (NOT affected; opposite pattern):**
- `aou_ld_panel.py:438-439` -- `_upload_to_gcs` correctly asserts prefixed input + strips. This is the architectural-inconsistency root cause of the producer/consumer drift across the codebase: mixed contracts (`_qc_checkpoint_uri` expected bare; `_upload_to_gcs` expects prefixed). Today's fix harmonizes by making `_qc_checkpoint_uri` defensive (accepts both).

## Fix Applied

**1. `_normalize_bucket(bucket: str) -> str` extracted (defensive utility):**
```python
def _normalize_bucket(bucket: str) -> str:
    """Normalize a bucket reference to bare-name form.

    AoU's $WORKSPACE_BUCKET env var includes the gs:// protocol prefix
    (e.g. gs://fc-secure-XXX); local tests, CLI flag inputs, and other
    call sites historically pass bare bucket names. URI builders in this
    module assume bare form so they can unambiguously prepend the protocol.
    This helper makes callers tolerant of either input form: strips an
    optional gs:// prefix and any leading/trailing slashes. Pure function;
    no validation (callers handle empty-input cases on their own).

    Closes the producer/consumer drift at the helper boundary surfaced
    2026-05-14 during AOU-1 Wave 1 fire on AoU Workbench (quick task
    260514-m3-W1-bucket-prefix-defensive), where the AOU-1 notebook
    caller pattern _qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], ...)
    produced malformed gs://gs://fc-secure-.../ld/mt_*.mt URIs under the
    prior bare-only contract.
    """
    return bucket.removeprefix("gs://").strip("/")
```

**2. `_qc_checkpoint_uri` wired to use it (line 178 post-fix):**
```python
return f"gs://{_normalize_bucket(bucket)}/ld/mt_{ancestry}{suffix}.mt"
```

**3. CLI `main()` wired to use it (line 553 post-fix):**
```python
ws = _normalize_bucket(_require_env("WORKSPACE_BUCKET"))
out_bucket = f"gs://{ws}/ld/{anc_upper}_aou"
```

**4. AOU-1 template Cell 7 refactored:**
- Before: `f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_afr_qc.mt"` (3 inline f-strings)
- After: `_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr', False)` (3 helper calls)
- Edit performed via Python helper script with pre/post-state asserts + round-trip JSON validation (per 260512-ldj edit-script pattern; safer than hand-edit of brittle nbformat JSON escapes).

## TDD Trace

**RED step** (`/tmp/m3-W1-bucket-prefix-RED.log`):
```
6 failed, 14 deselected in 2.43s

tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_strips_prefix FAILED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_keeps_bare FAILED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_strips_trailing_slash FAILED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_idempotent FAILED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_handles_malformed_extra_slash FAILED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_accepts_prefixed_bucket FAILED

AssertionError: bare vs prefixed inputs must produce identical canonical URI;
got bare='gs://test-bucket/ld/mt_afr_qc.mt',
prefixed='gs://gs://test-bucket/ld/mt_afr_qc.mt'
```
5 of 6 fail with `ImportError: cannot import name '_normalize_bucket'` (helper didn't exist yet). 1 fails with the exact assertion that empirically proves the bug locally.

**GREEN step** (`/tmp/m3-W1-bucket-prefix-GREEN.log`):
```
16 passed, 4 skipped in 0.05s

tests/m3/test_aou_ld_panel_local.py::test_env_yaml_pins_python_311 PASSED
[...all 6 static-source tests...]
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_primary_afr PASSED
[...all 4 existing 260512-jd9 regressions...]
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_strips_prefix PASSED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_keeps_bare PASSED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_strips_trailing_slash PASSED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_idempotent PASSED
tests/m3/test_aou_ld_panel_local.py::test_normalize_bucket_handles_malformed_extra_slash PASSED
tests/m3/test_aou_ld_panel_local.py::test_qc_checkpoint_uri_accepts_prefixed_bucket PASSED
[...4 live-hail tests SKIP gracefully without hail...]
```

## Commit + Push

- **HPC commit:** `243ebae fix(m3-W1-bucket-prefix-defensive): defensive bucket normalization in _qc_checkpoint_uri -- audit-driven re-analysis`
- **Cherry-picked to origin/main:** `779fe84` (clean fast-forward `7ddafb6..779fe84 push-fix -> main`)
- **Files staged via explicit `git add <path>`** per [[feedback_multi_terminal_staging]] (4 files; pre-existing dirty paths NOT staged: .claude/settings.json, .planning/config.json, untracked Track A artifacts).
- **Push reconciliation:** HPC and origin had divergent commit lineages with identical content (separate session-management finding; non-blocking, content-equivalent). Worked around via cherry-pick onto push-fix branch off origin/main, then `git push origin push-fix:main` as a clean fast-forward. AoU clone then hard-reset to origin/main after forensic-preserving its stale `2c6dbee` ref in bucket /forensics/.

## AoU-Side Verification (GREEN)

**Replay sequence executed on AoU Workbench (scratch_bootstrap_260514.ipynb cells 7-8 + JupyterLab UI):**
1. Forensic-preserve AoU clone's stale `2c6dbee` commit metadata to `gs://.../forensics/2c6dbee-forensic-<TS>/`.
2. `git fetch origin + git reset --hard origin/main` -> aligned clone to new remote tip `779fe84`.
3. `cp .planning/notebooks/AOU-1_template.ipynb -> /home/jupyter/workspaces/colocanalysis/AOU-1_cohort_definition.ipynb` (Layer 1: Welder mount disk).
4. `gsutil cp` -> bucket notebooks/AOU-1 (Layer 2: explicit per Welder architecture, since CLI writes to mount path don't auto-sync to bucket).
5. 3-layer md5 verification: ALL MATCH (new canonical md5 `61804eca0a5c22150a8890d97ae4948e`).
6. Cell 7 fix verified in workspace AOU-1: uses `_qc_checkpoint_uri(os.environ` helper calls, NOT inline f-strings.
7. JupyterLab: `File -> Close and Halt` on AOU-1 tab; reopen via file panel; `Kernel -> Restart Kernel`.
8. Cell 1a fire: emitted `PYSPARK_SUBMIT_ARGS set: --conf spark.executor.cores=1 --conf spark.executor.memory=5g --conf spark.driver.cores=1 pyspark-shell` (single-line confirmation).
9. Cell 1b fire (~30-60s Spark attach to fresh 16-worker Dataproc cluster): `cores=1 OK` assert passed; **PATCH VERIFICATION block emitted single-gs:// URIs**:
   ```
   AFR primary URI     : gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/mt_afr_qc.mt
   AFR sensitivity URI : gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/mt_afr_pca_selfid_qc.mt
   EUR parity URI      : gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/mt_eur_qc.mt
   ```
   No `gs://gs://` double-prefix. Fix empirically verified live on AoU production environment.
10. Cell 3 (primary AFR cohort, `load_qc_cohort(ancestry='afr', sensitivity=False)`) GREENLIT for fire post-verification.

## Forensic Artifacts Preserved

Per [[feedback_aou_use_persistent_disk]] Rule 1-Dataproc (durable storage to workspace bucket, since AoU Dataproc envs only support Standard disk that's erased on env Delete):

1. **`gs://fc-secure-f72fd8d8-.../forensics/AOU-1_cohort_definition.ipynb.pre-bucket-prefix-fix.bak.20260515T012956Z`** -- autosaved-with-malformed-output state of workspace AOU-1 captured BEFORE the post-fix canonical was cp'd over it. This .bak embeds the literal `gs://gs://fc-secure-...` malformed URIs in its Cell 1b output cell -- reviewer-verifiable evidence of the bug we just fixed.

2. **`gs://fc-secure-f72fd8d8-.../forensics/2c6dbee-forensic-20260515T012956Z/`** -- 4 files documenting AoU clone's stale `2c6dbee` commit object + reflog snapshot before the hard-reset reconciliation. Audit trail preservation of what was discarded from the AoU clone's local history (even though `2c6dbee` content is equivalent to `7ddafb6` on the new origin lineage).

## Deferred to Follow-Up

Tracked for separate /gsd-quick after Wave 1 Cell 3-7 lands:

1. **AOU-2 template Wave-2 surface fixes:** Same bug pattern at AOU-2 lines 51-52 (read paths), 64-65 (OUT_BUCKET write paths), 134-136 (gsutil shell commands). MTs not yet built; can't validate end-to-end yet. Natural gate before Wave 2 fires.
2. **AOU-1 template doc-comment cleanup:** Lines 114/132/150 misleading `gs://${WORKSPACE_BUCKET}/...` bash-style documentation. Trivial change; fold into AOU-2 follow-up.
3. **AOU-2 / AOU-4 dirty execution-output state on AoU clone:** Carried from prior session; `git checkout --` likely correct disposition before Wave-2 fire.
4. **HPC vs origin/main divergent commit lineage:** Separate session-management investigation. Both have identical project content; why does origin keep getting rewritten between sessions?
5. **Explicit BM-out_bucket regression test:** Carter's suggestion during grep blast-radius diagnostic. Line-513 fix currently covered transitively by `_normalize_bucket` behavior tests; explicit integration test would be belt-and-suspenders. Fold into AOU-2 follow-up.

## Cross-References

- **Predecessor:** 260512-jd9 (`_qc_checkpoint_uri` helper extraction; introduced the bare-only contract that this fix makes defensive). Commit `36e8062`.
- **Predecessor:** 260512-ldj (AOU-1 template Cell 1a/1b PYSPARK_SUBMIT_ARGS init pattern; the PATCH VERIFICATION block added by this commit is what surfaced today's bug at the helper-print boundary before compute spend). Commit `5389a88`.
- **Decision anchor:** DEC-2026-05-04-01 (spark.executor.cores=1 + naive_coalesce(2048) v8 partition-explosion OOM remediation; this fix preserves that anchor's reproducibility surface).
- **Memory baked this session:** [[feedback_aou_disk_type_check]], [[feedback_aou_use_persistent_disk]] (Welder mount architecture + Rule 1-Dataproc canonical workspace-notebook write workflow).
- **PLAN.md:** `.planning/quick/260514-npb-m3-w1-bucket-prefix-defensive/260514-npb-PLAN.md`
- **TDD logs:** `/tmp/m3-W1-bucket-prefix-RED.log`, `/tmp/m3-W1-bucket-prefix-GREEN.log` (HPC side).

## Honest-Framing Note

Per [[feedback_original_research_framing]]: this work is **audit-driven re-analysis** of a pre-existing producer/consumer drift at the helper-notebook integration boundary, surfaced empirically by the Wave 1 PATCH VERIFICATION block that was added by 260512-ldj precisely for this class of issue. The bug existed in the codebase since 260512-jd9 (2026-05-12) extracted the helper with bare-only test coverage; today's Wave 1 fire was the first time a caller passed the AoU-runtime-prefixed env var through the helper, and the verification design caught it before any cluster-hours were burned on a malformed checkpoint write. That is original-research methodological rigor working as designed -- not "cleanup," "revision," "salvage," or "fix-it."
