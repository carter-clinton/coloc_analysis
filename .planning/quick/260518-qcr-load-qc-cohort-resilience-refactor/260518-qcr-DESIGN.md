# 260518-qcr — `load_qc_cohort` algorithmic resilience refactor — DESIGN

**Status:** approved 2026-05-18 by Carter (brainstorming Q1-Q5 walkthrough); spec review pending; implementation deferred to post-spec-approval per [[feedback_rigor_over_speed]].

**Framing:** audit-driven re-analysis (per [[feedback_original_research_framing]]); NOT a cleanup/revision/salvage.

**Audit-trail commit:** TBD on commit of this spec.

**Related artifacts:**
- [src/python/aou_ld_panel.py:201-315](../../../src/python/aou_ld_panel.py#L201-L315) — `load_qc_cohort` function targeted for refactor
- [tests/m3/test_aou_ld_panel_local.py](../../../tests/m3/test_aou_ld_panel_local.py) — existing 16-test TDD suite to extend
- [.planning/amendments/AOU-LD-PIPELINE.md §11.0](../../amendments/AOU-LD-PIPELINE.md) — empirically-derived cluster sizing spec (committed 2026-05-17, d6f2748)
- `gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/forensics/*.20260518T164046Z.*` — Cell 3 12h-stall forensic artifacts

---

## 1. Background

### 1.1 Why this refactor is needed

m3-aou-afr-ld-panel-build Wave 1 (cohort definition for AFR primary + AFR sensitivity self-ID + EUR parity) has fired three times across two sessions. Outcomes:

| Fire | Cluster | Wall time | Outcome | Sunk cost |
|---|---|---|---|---|
| 2026-05-14 first fire | 16× n1-highmem-4 (64 vCPU; under-sized) | 33+h disconnect + 14.6h orphan-wedge | FAILED (websocket-drop orphan + cluster under-sized) | ~$165-180 |
| 2026-05-17 re-fire | same under-sized cluster | 3h 30min halted | HALTED on cluster-mis-sizing diagnosis | ~$17 |
| 2026-05-18 re-fire (this session) | 16× n1-highmem-16 (256 vCPU; correctly sized) | ~12h to Stage 19 commit | partial — Cell 3 (AFR primary) only; Cells 4-7 unfired | ~$237 (Cell 3 alone) |

Empirical observations from the 2026-05-18 fire (the correctly-sized cluster):
- **Chr22 smoke test** ran cleanly in 12.3 min — 3.57× speedup vs the under-sized cluster, confirming the 256-vCPU sizing is appropriate
- **Cell 3 (AFR primary) at full scale** took ~22 hours despite cluster sizing being correct
- **Stage 19** of Cell 3 dispatched 4090 tasks; took ~22h to complete with bimodal task velocity (slow start ~58 min/task-wave, accelerated to ~128 tasks/min in steady state)
- **YARN diagnostics** confirmed cluster fully utilized throughout (256/256 containers held, ~6.7% driver CPU, no failed tasks)
- **hail.log** went silent at 02:54:57 UTC then ~21:16:01 UTC — driver-log silence during executor-bound work is expected per Hail design

### 1.2 Root-cause hypothesis

The bimodal task velocity (slow start, fast finish) is strongly consistent with **partition skew** from `naive_coalesce(2048)` at step 5 of `load_qc_cohort`. naive_coalesce merges adjacent native partitions WITHOUT shuffling — on AoU's v8 WGS multiMT, this produces a few enormous post-merge partitions (heavy chromosomes) and many small ones (light chromosomes / final-chunk overflow). Spark schedules heavy partitions first → bimodal latency.

Secondary concern: load_qc_cohort has **no intermediate checkpoints**. The function is essentially monolithic — read MT → filter → split → sample_qc → variant_qc → write. A single executor crash anywhere from step 7 to step 11 forfeits all prior work. The 22h Cell 3 fire was effectively unprotected against mid-fire failure.

### 1.3 Cost trajectory without refactor

Empirical extrapolation from the 2026-05-18 fire:
- Cell 3 (AFR primary) at 22h = ~$420 on the correctly-sized cluster
- Cell 4 (AFR sensitivity, ~60% sample count after extra filter) = ~$250
- Cell 5 (EUR parity, ~3× AFR sample count) = ~$1140
- **All 3 Wave-1 ancestries: ~$1810**

Plus failure mode: any executor crash mid-fire → lose hours of work + restart from scratch. With a 22h cell, the probability of any failure during the cell is non-trivial.

---

## 2. Approved design decisions (Q1-Q5)

| ID | Question | Resolution |
|---|---|---|
| Q1 | Refactor scope | **Internal refactor** of `load_qc_cohort` in `src/python/aou_ld_panel.py`. All callers (AOU-1 notebook Cells 3/4/5, future CLI use) benefit transparently. Function signature extended (new kwargs); existing callers continue to work. |
| Q2 | Checkpoint count + placement | **2 intermediate checkpoints**: after step 6 (post-split_multi_hts) and after step 9 (post-sample-QC + het filter). Each is a natural snapshot boundary protecting an independent expensive phase. |
| Q3 | Partitioning strategy | **Hybrid**: keep `naive_coalesce(2048)` at step 5 (cheap upstream operations don't benefit from balanced partitions); add `mt.repartition(2048)` immediately before writing intermediate 1 (forces a balancing shuffle; subsequent heavy QC operations run on the balanced layout). The repartition shuffle cost is amortized into the checkpoint write that was already required by Q2. |
| Q4 | Resumability | **Auto-detect with sidecar metadata sanity check**: each intermediate checkpoint writes a JSON sidecar recording all QC parameters + git commit SHA + Hail version + timestamp. On entry, function checks for existing intermediates (deepest first); if sidecar matches current call's parameters, resume from there; if mismatched, raise `RuntimeError` with diagnostic. `force_fresh=True` parameter bypasses auto-resume. |
| Q5 | Validation strategy | **Unit tests + chr22 smoke + auto-resume verification**: ~10 new TDD tests; chr22-only smoke that exercises the FULL refactored pipeline (writes 3 outputs to a `/ld_smoke/` scratch path); 2nd-fire on same env to verify auto-resume hits intermediate 2 and completes in <5 min. |

---

## 3. Architecture

### 3.1 New helper functions

```python
def _intermediate_checkpoint_uri(bucket: str, ancestry: str,
                                  phase: str, sensitivity: bool) -> str:
    """Return gs://{bucket}/ld/intermediate/mt_{ancestry}{_sens}_{phase}.mt
    
    phase ∈ {"post_split", "post_sample_qc"}
    """

def _sidecar_uri(checkpoint_uri: str) -> str:
    """Return checkpoint_uri + '.meta.json'"""

def _collect_provenance(ancestry: str, sensitivity: bool,
                         source_mt_path: str, phase: str) -> dict:
    """Build the JSON-serializable provenance dict for sidecar write."""

def _write_sidecar(uri: str, provenance: dict) -> None:
    """Write JSON sidecar at uri (uses hl.hadoop_open or gsutil)."""

def _read_sidecar(uri: str) -> dict | None:
    """Read JSON sidecar; return dict or None if absent."""

def _validate_sidecar(sidecar: dict, provenance: dict) -> tuple[bool, str]:
    """Compare sidecar against current provenance dict.
    Returns (matches: bool, diagnostic: str).
    Mismatched parameters are listed in the diagnostic for resume rejection.
    """

def _has_checkpoint(uri: str) -> bool:
    """Check for {uri}/_SUCCESS marker (definitive completion signal)."""
```

### 3.2 Modified `load_qc_cohort` signature

```python
def load_qc_cohort(
    mt_path: str,
    ancestry: str,
    *,
    sensitivity: bool = False,
    ancestry_table_path: str | None = None,
    relateds_table_path: str | None = None,
    workspace_bucket: str | None = None,
    skip_checkpoint: bool = False,
    force_fresh: bool = False,        # NEW: bypass auto-resume; overwrite intermediates
    interval_filter: str | None = None,  # NEW: chr filter for smoke tests
) -> "hl.MatrixTable":
```

Existing kwargs preserved for backwards compatibility with current tests and CLI. New kwargs are keyword-only (after `*`).

### 3.3 Bucket layout

```
gs://${WORKSPACE_BUCKET}/ld/
├── mt_afr_qc.mt                                    # final (existing)
├── mt_afr_pca_selfid_qc.mt                         # final sensitivity (existing)
├── mt_eur_qc.mt                                    # final EUR (existing)
└── intermediate/                                   # NEW
    ├── mt_afr_post_split.mt
    ├── mt_afr_post_split.mt.meta.json
    ├── mt_afr_post_sample_qc.mt
    ├── mt_afr_post_sample_qc.mt.meta.json
    ├── mt_afr_pca_selfid_post_split.mt
    ├── mt_afr_pca_selfid_post_split.mt.meta.json
    ├── mt_afr_pca_selfid_post_sample_qc.mt
    ├── mt_afr_pca_selfid_post_sample_qc.mt.meta.json
    ├── mt_eur_post_split.mt
    ├── mt_eur_post_split.mt.meta.json
    ├── mt_eur_post_sample_qc.mt
    └── mt_eur_post_sample_qc.mt.meta.json
```

Smoke test uses parallel structure under `/ld_smoke/` instead of `/ld/`.

### 3.4 Sidecar metadata schema

```json
{
  "ancestry": "afr",
  "sensitivity": false,
  "phase": "post_split",
  "source_mt_path": "gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt",
  "params": {
    "MIN_CALL_RATE_SAMPLE": 0.98,
    "MIN_MAF_INTERNAL": 0.005,
    "MAX_MAF": 0.995,
    "MIN_CALL_RATE_VARIANT": 0.95,
    "MIN_HWE_PVALUE": 1e-06,
    "HET_HOM_SD_BAND": 3.0,
    "KING_KINSHIP_THRESHOLD": 0.0442
  },
  "ancestry_preds_path": "gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv",
  "relateds_path": "gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv",
  "cdr_version": "v8",
  "git_commit_sha": "779fe84abc123...",
  "hail_version": "0.2.134-952ae203dbbe",
  "timestamp_utc": "2026-05-18T17:32:00.000Z",
  "schema_version": 1
}
```

`schema_version: 1` reserves room for forward-compatible additions; sidecar reader must reject unknown schema versions explicitly rather than silently treating them as version 1.

### 3.5 Control flow with auto-resume

```
ENTRY: load_qc_cohort(mt_path, ancestry, sensitivity=..., force_fresh=..., ...)

if not skip_checkpoint:
    Compute URIs:
        ckpt_post_split = _intermediate_checkpoint_uri(bucket, ancestry, "post_split", sensitivity)
        ckpt_post_sqc   = _intermediate_checkpoint_uri(bucket, ancestry, "post_sample_qc", sensitivity)
        final_ckpt      = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
    Build provenance dict for current call.

if force_fresh OR skip_checkpoint:
    state = "FRESH"
elif _has_checkpoint(ckpt_post_sqc):
    sidecar = _read_sidecar(_sidecar_uri(ckpt_post_sqc))
    matches, diag = _validate_sidecar(sidecar, provenance_at_phase("post_sample_qc"))
    if matches:
        state = "RESUME_FROM_POST_SAMPLE_QC"
    else:
        raise RuntimeError(f"Stale intermediate at {ckpt_post_sqc}: {diag}. Use force_fresh=True to overwrite.")
elif _has_checkpoint(ckpt_post_split):
    sidecar = _read_sidecar(_sidecar_uri(ckpt_post_split))
    matches, diag = _validate_sidecar(sidecar, provenance_at_phase("post_split"))
    if matches:
        state = "RESUME_FROM_POST_SPLIT"
    else:
        raise RuntimeError(f"Stale intermediate at {ckpt_post_split}: {diag}. Use force_fresh=True to overwrite.")
else:
    state = "FRESH"

print(f"[load_qc_cohort] state={state} ancestry={ancestry} sensitivity={sensitivity}")

# Phase 1: read + filter + split (steps 1-6 in current code)
if state == "FRESH":
    mt = hl.read_matrix_table(mt_path)
    if interval_filter is not None:
        mt = hl.filter_intervals(mt, [hl.parse_locus_interval(interval_filter, reference_genome="GRCh38")])
    # ancestry filter (step 2)
    # relateds anti-join (step 3)
    # sensitivity filter (step 4)
    mt = mt.naive_coalesce(2048)
    mt = hl.split_multi_hts(mt)
    # Q3: repartition for balanced QC phase before checkpoint
    mt = mt.repartition(2048)
    if not skip_checkpoint:
        mt = mt.checkpoint(ckpt_post_split, overwrite=force_fresh)
        _write_sidecar(_sidecar_uri(ckpt_post_split),
                       _collect_provenance(ancestry, sensitivity, mt_path, "post_split"))
        print(f"[load_qc_cohort] wrote intermediate 1: {ckpt_post_split}")
elif state == "RESUME_FROM_POST_SPLIT":
    mt = hl.read_matrix_table(ckpt_post_split)
    print(f"[load_qc_cohort] resumed from intermediate 1: {ckpt_post_split}")
elif state == "RESUME_FROM_POST_SAMPLE_QC":
    mt = hl.read_matrix_table(ckpt_post_sqc)
    print(f"[load_qc_cohort] resumed from intermediate 2: {ckpt_post_sqc}")
    # SKIP to phase 3 below

# Phase 2: sample QC + het filter (steps 7-9 in current code)
if state in ("FRESH", "RESUME_FROM_POST_SPLIT"):
    mt = hl.sample_qc(mt, name="sqc")
    mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)
    het_stats = mt.aggregate_cols(hl.agg.stats(mt.sqc.r_het_hom_var))
    if het_stats.stdev is not None and het_stats.stdev > 0:
        lo = het_stats.mean - HET_HOM_SD_BAND * het_stats.stdev
        hi = het_stats.mean + HET_HOM_SD_BAND * het_stats.stdev
        mt = mt.filter_cols((mt.sqc.r_het_hom_var >= lo) & (mt.sqc.r_het_hom_var <= hi))
    if not skip_checkpoint:
        mt = mt.checkpoint(ckpt_post_sqc, overwrite=force_fresh)
        _write_sidecar(_sidecar_uri(ckpt_post_sqc),
                       _collect_provenance(ancestry, sensitivity, mt_path, "post_sample_qc"))
        print(f"[load_qc_cohort] wrote intermediate 2: {ckpt_post_sqc}")

# Phase 3: variant QC + final filter + final checkpoint (steps 10-12)
mt = hl.variant_qc(mt, name="vqc")
mt = mt.filter_rows(
    (mt.vqc.AF[1] >= MIN_MAF_INTERNAL) &
    (mt.vqc.AF[1] <= MAX_MAF) &
    (mt.vqc.call_rate >= MIN_CALL_RATE_VARIANT) &
    (mt.vqc.p_value_hwe >= MIN_HWE_PVALUE)
)
if "filters" in mt.row:
    mt = mt.filter_rows(hl.len(mt.filters) == 0)

if not skip_checkpoint:
    mt = mt.checkpoint(final_ckpt, overwrite=True)
    print(f"[load_qc_cohort] wrote final: {final_ckpt}")

return mt
```

---

## 4. Error handling

| Scenario | Behavior | Recovery |
|---|---|---|
| Sidecar mismatch (param differs from current call) | `RuntimeError` with diagnostic naming the specific differing parameter(s) | Caller passes `force_fresh=True` to overwrite, OR fixes the parameter mismatch |
| Sidecar absent but MT exists at intermediate path | Treat as orphan; raise `RuntimeError` (refuse to use unverified MT) | Caller deletes the orphan MT or passes `force_fresh=True` |
| Sidecar present but malformed JSON or wrong schema_version | `RuntimeError` with parse diagnostic | Caller fixes/deletes sidecar |
| GCS write failure during intermediate checkpoint | Hail's native exception propagates; no internal retry | Caller-level retry policy (e.g., re-fire the cell — auto-resume will pick up the prior successful intermediate if any) |
| `force_fresh=True` | Bypass all auto-resume checks; `overwrite=True` on all intermediate writes | N/A — explicit user override |
| `skip_checkpoint=True` (test path) | Skip ALL checkpoints (intermediate + final); function returns lazy MT for in-memory test assertions | Existing test pattern preserved; no resume logic exercised |

The mismatch diagnostic format is engineered to surface the relevant parameter immediately:

```
RuntimeError: Stale intermediate at gs://.../intermediate/mt_afr_post_split.mt:
  sidecar.params.MIN_CALL_RATE_SAMPLE = 0.95
  current call MIN_CALL_RATE_SAMPLE = 0.98
  mismatch on 1 parameter(s)
Use force_fresh=True to overwrite, or fix the parameter mismatch.
```

---

## 5. Testing plan

### 5.1 Unit tests added to `tests/m3/test_aou_ld_panel_local.py`

**6 pure-Python tests (no Hail dependency; run in normal `pytest tests/m3/`):**

1. `test_intermediate_checkpoint_uri_format` — verify URI format for both phases × both sensitivity flags × both AFR/EUR ancestries (8 combinations)
2. `test_sidecar_uri_format` — verify sidecar = checkpoint + `.meta.json`
3. `test_collect_provenance_includes_required_fields` — provenance dict has all 11 required keys
4. `test_validate_sidecar_accepts_matching` — identical provenance → `(True, "")`
5. `test_validate_sidecar_rejects_mismatched_ancestry` — different ancestry → `(False, diagnostic)`; diagnostic mentions "ancestry"
6. `test_validate_sidecar_rejects_mismatched_thresholds` — different MIN_CALL_RATE_SAMPLE → `(False, diagnostic)`; diagnostic mentions the threshold name

**4 live-Hail tests (SKIP without hail; run in `pytest --hail tests/m3/` mode):**

7. `test_load_qc_cohort_auto_resume_from_post_split` — fire once on synthetic MT (writes intermediate 1 + 2 + final); delete intermediate 2; fire again → expect resume from intermediate 1 (verified via captured stdout containing "resumed from intermediate 1")
8. `test_load_qc_cohort_auto_resume_from_post_sample_qc` — fire once; fire again unchanged → expect resume from intermediate 2 (deepest available)
9. `test_load_qc_cohort_force_fresh_bypasses_auto_resume` — fire once; fire again with `force_fresh=True` → expect FRESH state (stdout) and overwritten intermediates (timestamps advance)
10. `test_load_qc_cohort_raises_on_sidecar_mismatch` — fire once; manually edit sidecar to change ancestry; fire again → expect `RuntimeError` with "ancestry" in diagnostic

**Total test count:** 16 existing → 26 after. All existing tests must still pass (refactor preserves behavior for fresh runs).

### 5.2 chr22 smoke test on AoU

A new short smoke cell inserted between Cell 1b and Cell 3 of the AOU-1 template (or fired ad-hoc in scratch_bootstrap):

```python
import os
from aou_ld_panel import load_qc_cohort

# Fresh fire — exercises full pipeline on chr22 subset
mt_smoke = load_qc_cohort(
    mt_path=os.environ['WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH'],
    ancestry='afr',
    sensitivity=False,
    workspace_bucket=os.environ['WORKSPACE_BUCKET'].removeprefix('gs://') + '/ld_smoke',
    interval_filter='chr22',
    force_fresh=True,
)
print(f"chr22 smoke MT: {mt_smoke.count()}")
print(f"Expect 3 outputs at /ld_smoke/ : intermediate 1, intermediate 2, final")
```

**Expected on first fire** (~15-30 min):
- stdout shows `state=FRESH`
- 3 outputs written: `mt_afr_post_split.mt`, `mt_afr_post_sample_qc.mt`, `mt_afr_qc.mt` (all under `/ld_smoke/ld/` and `/ld_smoke/ld/intermediate/`)
- Each intermediate has matching `.meta.json` sidecar

**Second fire of the same cell (without `force_fresh`)** (~3-5 min):
- stdout shows `state=RESUME_FROM_POST_SAMPLE_QC`
- Only variant_qc + final write executed
- Final MT byte-identical (or content-identical) to first fire

**Smoke artifacts persist** in `gs://.../ld_smoke/` as a permanent regression fixture — re-smoke after any future refactor for ~$3 verification.

### 5.3 Validation gate before re-firing Wave-1 cohort definition

The refactor is ready for Cells 3-5 re-fire only when ALL of:
- ✅ All 26 unit tests pass on HPC (`pytest tests/m3/test_aou_ld_panel_local.py`)
- ✅ chr22 smoke fresh fire produces all 3 outputs + correct sidecars
- ✅ chr22 smoke resume fire completes in <5 min from intermediate 2
- ✅ Spec doc reviewed (this design) and Carter-approved
- ✅ Refactor commit pushed to origin and AoU-clone updated

---

## 6. Out of scope (explicitly deferred)

### 6.1 EUR-specific scaling decisions

EUR parity has ~3× the AFR sample count (~150K vs ~50K). Even with the refactor's partition rebalancing and intermediate checkpoints, EUR compute scales linearly with samples × variants. Empirical AFR-refactored timing is needed before deciding whether EUR needs:
- Same cluster (16× n1-highmem-16) at proportionally longer wall time
- Larger cluster (e.g., 32× n1-highmem-16 = 512 vCPU) for EUR specifically
- Per-chromosome chunking (Q3 Option D) for EUR only

Decision will be made after refactored AFR Cell 3 completes empirically.

### 6.2 Per-chromosome chunking (Q3 Option D)

Defers to future quick-fix iteration if the refactored hybrid-partitioning approach (Q3 Option C) empirically still has problematic wall times for EUR. Per-chromosome chunking would rewrite `load_qc_cohort` to loop over chr1-22, write per-chr MTs, union at end. More invasive change with more test surface; out of scope unless empirically needed.

### 6.3 AOU-1 template Cell 3/4/5 modifications

The template cells continue to call `load_qc_cohort(...)` with one cell per ancestry. The refactor preserves the function's existing call shape — the template DOES NOT need modification beyond the optional `force_fresh=True` flag for explicit re-runs. Per-cell evaluation cadence is an operational practice (run Cell 3 → evaluate → run Cell 4 → evaluate → ...) not a code change.

### 6.4 Variant_qc internals

The variant_qc + MAF/HWE/call_rate filter (steps 10-11) is preserved unchanged. The empirical evidence pointed at partition skew + lack of intermediate checkpoints as the bottleneck — variant_qc itself appears to work correctly. If post-refactor profiling shows variant_qc is the new bottleneck, that's a follow-up.

### 6.5 AOU-2 template `gs://gs://` bug pattern follow-up

AOU-2 template has the same `gs://gs://` malformed-URI pattern that was fixed in `load_qc_cohort` (commit 779fe84). Deferred to a separate quick-fix task; out of scope for this refactor.

---

## 7. Implementation order (high-level)

Full task breakdown is the responsibility of the writing-plans skill (next phase). High-level sequence:

1. **TDD red phase** — write the 6 pure-Python tests first (helper functions + sidecar contract); confirm RED (ImportError / AssertionError).
2. **Helper functions** — implement `_intermediate_checkpoint_uri`, `_sidecar_uri`, `_collect_provenance`, `_write_sidecar`, `_read_sidecar`, `_validate_sidecar`, `_has_checkpoint`. Confirm GREEN on tests 1-6.
3. **TDD red phase 2** — write the 4 live-Hail tests (resume scenarios); confirm RED (function doesn't have new kwargs yet).
4. **Refactor `load_qc_cohort`** — add `force_fresh` + `interval_filter` kwargs; implement the 3-state control flow (FRESH / RESUME_FROM_POST_SPLIT / RESUME_FROM_POST_SAMPLE_QC); wire repartition + intermediate writes + sidecar writes. Confirm GREEN on tests 7-10 + all 16 existing tests still pass.
5. **Atomic commit** — `feat(m3-W1-qc-cohort-resilience): intermediate checkpoints + sidecar auto-resume + balanced repartition -- audit-driven re-analysis`. Single commit per [[feedback_multi_terminal_staging]].
6. **Push to origin** via cherry-pick on push-fix branch (per established 779fe84 pattern).
7. **AoU clone update** — `git pull origin main` on the AoU env.
8. **chr22 smoke fire** — first fire (FRESH) + second fire (RESUME). Verify both pass.
9. **Production fire** — Cells 3 → 4 → 5 with per-cell evaluation cadence per Carter's directive. Each cell completion verified via bucket `_SUCCESS` markers before next cell fires.

---

## 8. Success criteria

The refactor is successful when:
- **Resilience**: A mid-fire failure does not require re-doing all prior work. Empirically tested via the smoke test resume path.
- **Reproducibility**: Sidecar metadata provides an audit trail mapping each MT to the exact code + parameters that produced it. Required for reviewer-defensible original-research framing per [[feedback_original_research_framing]].
- **Performance**: Wave-1 (Cells 3-5) total wall time on a correctly-sized 256-vCPU cluster is bounded such that all 3 cohort MTs land within a single working session (target: ≤24h total, ideally ≤12h).
- **Cost ceiling**: Wave-1 cohort definition total spend (across all cells, including retries) does not exceed $500 once the refactor is in place. Per-ancestry expected cost: $50-150.
- **Safety**: Sidecar mismatch detection prevents silently using stale intermediates with old parameters. Verified via test 10.
- **No regression**: All 16 existing TDD tests pass. No change to final MT schema or content for any of the 3 ancestries (refactor is algorithmic resilience, not algorithmic semantics).

---

**End of DESIGN.**
