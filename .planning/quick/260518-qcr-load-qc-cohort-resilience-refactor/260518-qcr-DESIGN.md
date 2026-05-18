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
                                  phase: str, sensitivity: bool,
                                  interval_filter: str | None = None) -> str:
    """Return gs://{bucket}/ld/intermediate/mt_{ancestry}{_sens}_{phase}{_interval}.mt
    
    phase ∈ {"post_split", "post_sample_qc"}
    interval_filter: when set (e.g., "chr22"), URI gets a "_{interval}" suffix
    that path-isolates smoke intermediates from production intermediates.
    Production fires (interval_filter=None) produce paths WITHOUT the suffix;
    smoke fires produce paths WITH the suffix. Path-level disambiguation +
    sidecar param-level check provides defense in depth against silent
    smoke/production collision.
    """

def _sidecar_uri(checkpoint_uri: str) -> str:
    """Return checkpoint_uri + '.meta.json'"""

def _collect_provenance(ancestry: str, sensitivity: bool,
                         source_mt_path: str,
                         interval_filter: str | None = None) -> dict:
    """Build the JSON-serializable provenance dict for sidecar write.
    
    Does NOT include the 'phase' field — phase is added by _write_sidecar
    at write time so that the SAME provenance dict can be written to both
    post_split and post_sample_qc sidecars (the only difference being phase).
    
    Conservative semantics: ALL QC parameters are included regardless of
    which phase consumes them. Any parameter change invalidates ALL
    intermediates for this (ancestry, sensitivity, interval_filter) combo.
    """

def _write_sidecar(uri: str, provenance: dict, phase: str) -> None:
    """Write JSON sidecar at uri. Adds 'phase' field to the provenance dict
    before serialization. Atomicity note: caller must invoke this AFTER the
    matching mt.checkpoint() returns successfully (see §4 ordering policy).
    """

def _read_sidecar(uri: str) -> dict | None:
    """Read JSON sidecar; return dict or None if absent.
    Raises RuntimeError on malformed JSON or unknown schema_version.
    """

def _validate_sidecar(sidecar: dict, provenance: dict) -> tuple[bool, str]:
    """Compare sidecar against current provenance dict.
    
    Compares ALL fields EXCEPT 'phase' (which legitimately differs between
    the two sidecar files for a single fire). Mismatched fields are listed
    in the diagnostic for resume rejection.
    
    Returns (matches: bool, diagnostic: str).
    """

def _has_checkpoint(uri: str) -> bool:
    """Check for {uri}/_SUCCESS marker (definitive completion signal).
    
    GCS object existence is strongly consistent (per Google's 2020 consistency
    model upgrade — all read-after-write operations on individual objects are
    strongly consistent). _SUCCESS marker existence is therefore safe as the
    auto-resume gate. False-negative due to list-operation eventual-consistency
    edge cases would result in redundant work (re-firing a completed phase),
    not corruption.
    """
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

**Production fires** (`interval_filter=None`):

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

**Smoke fires** (`interval_filter="chr22"`): same structure BUT with `_chr22` suffix on every intermediate path AND the smoke writes to a scratch `workspace_bucket` (recommended: `${WORKSPACE_BUCKET}/ld_smoke`):

```
gs://${WORKSPACE_BUCKET}/ld_smoke/
├── mt_afr_qc.mt                                    # smoke final (chr22-only data)
└── intermediate/
    ├── mt_afr_post_split_chr22.mt
    ├── mt_afr_post_split_chr22.mt.meta.json
    ├── mt_afr_post_sample_qc_chr22.mt
    └── mt_afr_post_sample_qc_chr22.mt.meta.json
```

**Path-level isolation rationale (addresses Issue #2 from spec review v1):**

The `_chr22` URI suffix means that even if a smoke fire is accidentally directed at the production `workspace_bucket`, its intermediates land at `mt_afr_post_split_chr22.mt` — DIFFERENT from production `mt_afr_post_split.mt`. A subsequent full-genome production fire CANNOT auto-resume from a chr22-suffixed intermediate (URI doesn't exist at the production path). Combined with the sidecar param-level check (`interval_filter: "chr22"` vs `null`), this provides defense in depth against silent smoke/production collision.

### 3.4 Sidecar metadata schema

Both post_split and post_sample_qc sidecars share the same schema. The ONLY field that legitimately differs between the two sidecars for a single fire is `phase`. All other fields are identical.

```json
{
  "ancestry": "afr",
  "sensitivity": false,
  "interval_filter": null,
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

Field notes:
- `interval_filter` is `null` for production fires, `"chr22"` (or other chr filter) for smoke fires. **Mandatory field** — sidecar mismatch detection requires it to disambiguate smoke intermediates from production. Addresses Issue #2 from spec review v1.
- `phase` is added by `_write_sidecar(uri, provenance_dict, phase)` at write time; not part of the `_collect_provenance(...)` return value. This permits the same provenance dict to be written to both intermediate sidecars (with phase differing per call).
- `_validate_sidecar` compares all fields EXCEPT `phase`. Mismatched fields are listed in the resulting diagnostic.
- `schema_version: 1` reserves room for forward-compatible additions; sidecar reader MUST reject unknown schema versions explicitly rather than silently treating them as version 1.

### 3.5 Control flow with auto-resume

```
ENTRY: load_qc_cohort(mt_path, ancestry, sensitivity=..., interval_filter=None, force_fresh=..., ...)

if not skip_checkpoint:
    # Compute URIs (interval_filter affects suffix for path-level isolation)
    ckpt_post_split = _intermediate_checkpoint_uri(bucket, ancestry, "post_split", sensitivity, interval_filter)
    ckpt_post_sqc   = _intermediate_checkpoint_uri(bucket, ancestry, "post_sample_qc", sensitivity, interval_filter)
    final_ckpt      = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
    # Build single shared provenance dict for current call (NO 'phase' field)
    provenance = _collect_provenance(ancestry, sensitivity, mt_path, interval_filter)

if force_fresh OR skip_checkpoint:
    state = "FRESH"
elif _has_checkpoint(ckpt_post_sqc):
    sidecar = _read_sidecar(_sidecar_uri(ckpt_post_sqc))
    if sidecar is None:
        # Orphan MT (checkpoint succeeded, sidecar write failed in prior fire).
        # Auto-recover: print WARN, treat as FRESH, allow overwrite of orphan.
        print(f"[load_qc_cohort] WARN: orphan MT at {ckpt_post_sqc} (sidecar absent); auto-force-fresh recovery")
        state = "FRESH"
        auto_fresh = True
    else:
        matches, diag = _validate_sidecar(sidecar, provenance)
        if matches:
            state = "RESUME_FROM_POST_SAMPLE_QC"
        else:
            raise RuntimeError(f"Stale intermediate at {ckpt_post_sqc}: {diag}. Use force_fresh=True to overwrite, or fix the parameter mismatch.")
elif _has_checkpoint(ckpt_post_split):
    sidecar = _read_sidecar(_sidecar_uri(ckpt_post_split))
    if sidecar is None:
        print(f"[load_qc_cohort] WARN: orphan MT at {ckpt_post_split} (sidecar absent); auto-force-fresh recovery")
        state = "FRESH"
        auto_fresh = True
    else:
        matches, diag = _validate_sidecar(sidecar, provenance)
        if matches:
            state = "RESUME_FROM_POST_SPLIT"
        else:
            raise RuntimeError(f"Stale intermediate at {ckpt_post_split}: {diag}. Use force_fresh=True to overwrite, or fix the parameter mismatch.")
else:
    state = "FRESH"

# Effective overwrite flag for intermediate writes
overwrite_flag = force_fresh or auto_fresh

print(f"[load_qc_cohort] state={state} ancestry={ancestry} sensitivity={sensitivity} interval_filter={interval_filter}")

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
        # Sidecar atomicity: write checkpoint FIRST, then sidecar.
        # Crash window between these two writes leaves an orphan MT that
        # the next fire detects (sidecar absent) and auto-force-fresh's.
        mt = mt.checkpoint(ckpt_post_split, overwrite=overwrite_flag)
        _write_sidecar(_sidecar_uri(ckpt_post_split), provenance, phase="post_split")
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
        mt = mt.checkpoint(ckpt_post_sqc, overwrite=overwrite_flag)
        _write_sidecar(_sidecar_uri(ckpt_post_sqc), provenance, phase="post_sample_qc")
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

**Notes on the control flow:**

- **No `provenance_at_phase()` helper** — the single `provenance` dict (without `phase` field) is used for BOTH sidecar comparisons and BOTH sidecar writes. `_write_sidecar` adds the `phase` field at write time. `_validate_sidecar` ignores the `phase` field at compare time. (Addresses Issue #1 from spec review v1.)
- **`overwrite_flag` invariant** — Phase 2 only writes intermediate 2 when state ∈ {FRESH, RESUME_FROM_POST_SPLIT}. In both cases, auto-resume would have selected RESUME_FROM_POST_SAMPLE_QC if intermediate 2 existed with valid sidecar. The only intermediate-2-exists case when Phase 2 actually writes is the auto-fresh orphan-recovery path (sidecar absent). `overwrite_flag = force_fresh or auto_fresh` correctly handles this. (Addresses Issue #3 from spec review v1.)
- **Sidecar atomicity** — Order is: checkpoint write → sidecar write. Crash window between the two leaves an orphan MT; next fire detects sidecar absence and auto-force-fresh's (with WARN print). Trade-off: simpler implementation, predictable recovery, occasional re-do of one phase on crash-during-sidecar-write. Alternative (`.meta.json.pending` + atomic rename) is more complex; deferred unless empirically needed. (Addresses Issue #4 from spec review v1.)

---

## 4. Error handling

| Scenario | Behavior | Recovery |
|---|---|---|
| Sidecar mismatch (param differs from current call) | `RuntimeError` with diagnostic naming the specific differing parameter(s) | Caller passes `force_fresh=True` to overwrite, OR fixes the parameter mismatch |
| Sidecar absent BUT MT exists at intermediate path (orphan from prior crash) | **Auto-recover**: print `WARN` to stdout, set `state=FRESH` with `auto_fresh=True`, overwrite the orphan MT on next intermediate write | None required — function self-heals. Trade-off: prior phase work re-done. |
| Sidecar present but malformed JSON or unknown `schema_version` | `RuntimeError` with parse diagnostic | Caller fixes/deletes sidecar |
| GCS write failure during intermediate checkpoint | Hail's native exception propagates; no internal retry | Caller-level retry policy (e.g., re-fire the cell — auto-resume will pick up the prior successful intermediate if any; orphan-recovery handles the partial-write case) |
| `force_fresh=True` | Bypass all auto-resume checks; `overwrite=True` on all intermediate writes | N/A — explicit user override |
| `skip_checkpoint=True` (test path) | Skip ALL checkpoints (intermediate + final); function returns lazy MT for in-memory test assertions | Existing test pattern preserved; no resume logic exercised |
| `interval_filter` set with default `workspace_bucket` (would point at production `/ld/`) | No automatic refusal — but URI-suffix isolation (`_chr22`) means smoke intermediates land at distinct paths from production. Sidecar `interval_filter` field ensures mismatch detection. | Recommended: callers passing `interval_filter` SHOULD also pass an explicit smoke `workspace_bucket` (e.g., `${WORKSPACE_BUCKET}/ld_smoke`); the URI suffix + sidecar field provide defense in depth even when this convention is forgotten. |
| `interval_filter` is malformed (e.g., `"chrXX"`, `"chr22:abc-def"`, unparseable contig name) | Passed straight to `hl.parse_locus_interval(interval_filter, reference_genome="GRCh38")`; Hail's native parse error propagates (e.g., `HailException` or `FatalError` with parser diagnostic) | Caller fixes the malformed string. Fail-loud is intentional — no silent fallback to "treat as no filter." |

The mismatch diagnostic format is engineered to surface the relevant parameter immediately:

```
RuntimeError: Stale intermediate at gs://.../intermediate/mt_afr_post_split.mt:
  sidecar.params.MIN_CALL_RATE_SAMPLE = 0.95
  current call MIN_CALL_RATE_SAMPLE = 0.98
  mismatch on 1 parameter(s)
Use force_fresh=True to overwrite, or fix the parameter mismatch.
```

**Sidecar / checkpoint write-order policy (addresses Issue #4 from spec review v1):**

Order: `mt.checkpoint(uri, ...)` FIRST, then `_write_sidecar(uri, provenance, phase)`. Rationale:
- Hail's `checkpoint()` writes data atomically (final `_SUCCESS` marker is the commit signal).
- The `_write_sidecar()` call is a separate non-atomic operation. A process crash in the gap window leaves an orphan MT (data complete, sidecar missing).
- Orphan recovery: next fire detects `_has_checkpoint(uri) and _read_sidecar(uri) is None` → prints `WARN`, treats as FRESH, overwrites orphan in next intermediate write.
- Cost of this design: one phase of work is re-done on crash-during-sidecar-write. Acceptable for the simplicity gain.
- Alternative considered: `.meta.json.pending` + atomic rename for true atomicity. Deferred — more complex, marginal benefit given infrequent crash window.

**Phase-2 overwrite invariant (addresses Issue #3 from spec review v1):**

Phase 2 only writes intermediate 2 when `state ∈ {FRESH, RESUME_FROM_POST_SPLIT}`. In both states, the auto-resume logic in §3.5 would have selected `RESUME_FROM_POST_SAMPLE_QC` if intermediate 2 already existed with a valid sidecar. The only paths reaching Phase 2 with intermediate 2 already existing on disk are:
- `force_fresh=True` (user override) → `overwrite=True` is correct
- `auto_fresh=True` (orphan recovery) → `overwrite=True` is correct
- Otherwise: intermediate 2 does not exist → `overwrite=False` writes cleanly

The expression `overwrite_flag = force_fresh or auto_fresh` captures this invariant correctly.

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

All live-Hail tests use a `tmp_path`-scoped `file://` URI as the `workspace_bucket` (consistent with existing `skip_checkpoint=False` test fixture pattern). Synthetic MT is the existing `tests/m3/fixtures/synthetic_mt/` (D-M3-06 dev mirror, loaded via the session-scoped fixture in `tests/m3/conftest.py`). Intermediate MTs are deleted between sub-fires via `shutil.rmtree(tmp_path / "intermediate" / "mt_afr_post_sample_qc.mt")` for test 7 (since MT directories on local FS are plain directory trees, not GCS objects).

7. `test_load_qc_cohort_auto_resume_from_post_split` — fire once on synthetic MT (writes intermediate 1 + 2 + final); `shutil.rmtree` the intermediate 2 directory; fire again → expect resume from intermediate 1 (verified via captured stdout containing "resumed from intermediate 1") (addresses Issue #6 from spec review v1)
8. `test_load_qc_cohort_auto_resume_from_post_sample_qc` — fire once; fire again unchanged → expect resume from intermediate 2 (deepest available)
9. `test_load_qc_cohort_force_fresh_bypasses_auto_resume` — fire once; fire again with `force_fresh=True` → expect FRESH state (stdout) and overwritten intermediates (timestamps advance)
10. `test_load_qc_cohort_raises_on_sidecar_mismatch` — fire once; manually edit sidecar to change ancestry; fire again → expect `RuntimeError` with "ancestry" in diagnostic

**Plus 1 additional test added for v2 (orphan-MT auto-recovery):**

11. `test_load_qc_cohort_auto_recovers_from_orphan_mt` — fire once; `shutil.rmtree` the intermediate 1 sidecar (`mt_afr_post_split.mt.meta.json`) but leave the MT directory; fire again with same params → expect `state=FRESH` and stdout `WARN` line mentioning orphan and auto-force-fresh recovery (verifies the §4 atomicity policy is correctly implemented)

**Total test count:** 16 existing → 27 after. All existing tests must still pass (refactor preserves behavior for fresh runs with `skip_checkpoint=True`).

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
- ✅ All 27 unit tests pass on HPC (`pytest tests/m3/test_aou_ld_panel_local.py`)
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

### 6.6 Sidecar utility extraction to `src/python/_checkpoint_sidecar.py`

The sidecar read/write/validate triad (`_collect_provenance`, `_write_sidecar`, `_read_sidecar`, `_validate_sidecar`) is a candidate for promotion to a standalone reusable utility module if any other M3 component (AOU-2 per-region LD, AOU-4 validation, future Wave-3 work) needs the same resume contract. For THIS refactor, the helpers live inside `aou_ld_panel.py` (no premature abstraction per [[feedback_extract_reusable_utilities]] — extract on second usage, not first). Flag carried forward for the next M3 component that needs it.

### 6.7 Sidecar atomicity via `.meta.json.pending` + atomic rename

Per spec review v1 issue #4: the chosen design is "write checkpoint, then write sidecar, recover orphans on next fire." An alternative is `.meta.json.pending` + atomic rename for true atomicity at the cost of one extra write + one rename per sidecar. Deferred unless empirically needed (orphan recovery is observable through the WARN print; if it fires frequently we revisit).

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
- **Smoke wall-clock budget assertion** (regression guard): chr22 smoke FRESH fire MUST complete in ≤ 30 minutes on the canonical 256-vCPU cluster (the 2026-05-18 baseline was 12.3 min for aggregate_cols only; the full-pipeline refactored smoke should complete in 15-30 min). chr22 smoke RESUME fire (2nd call from same intermediates) MUST complete in ≤ 5 minutes. These wall-clock thresholds are encoded as time-budgeted assertions in the smoke procedure so future regressions surface immediately. (Per spec review v1 impl note.)

---

## 9. CHANGELOG

### v2.1 (this version) — 2026-05-18 (post spec-review cycle 2)

Spec review cycle 2 verdict: APPROVED. Two LOW notes addressed as micro-amendments:

- §5.3 count typo: "26 unit tests pass" → "27 unit tests pass" (canonical count is 16 existing + 11 new = 27). ✓
- §4 error-handling table: added explicit row for malformed `interval_filter` documenting that Hail's native parse error propagates (fail-loud is intentional). ✓

### v2 — 2026-05-18 (post spec-review cycle 1)

Addresses spec review v1 cycle feedback:

- **Issue #1 (HIGH)** — phase-mismatch bug. Removed `provenance_at_phase()` reference in §3.5; clarified that `_collect_provenance` returns a single shared dict (no phase field) used for BOTH sidecars; `_write_sidecar` adds the phase field at write time; `_validate_sidecar` ignores phase field at compare time. Adopted conservative "all params must match for any resume" semantics. ✓
- **Issue #2 (HIGH)** — `interval_filter` unsafe. Added `interval_filter` parameter to `_intermediate_checkpoint_uri`; URI gets a `_{interval}` suffix when set (path-level isolation between smoke and production). Added `interval_filter` field to sidecar schema (param-level mismatch detection). Documented soft guardrail in §4 recommending explicit smoke `workspace_bucket`. ✓
- **Issue #3 (MEDIUM)** — `overwrite` semantics on resume-from-post-split. Documented Phase-2 overwrite invariant explicitly in §4: `overwrite_flag = force_fresh or auto_fresh` captures all paths reaching Phase 2 with intermediate 2 existing on disk. ✓
- **Issue #4 (MEDIUM)** — sidecar atomicity. Specified write order (checkpoint first, then sidecar) in §3.5 and §4. Added orphan-recovery semantics: sidecar-absent-but-MT-exists triggers auto-force-fresh with WARN print, not RuntimeError. Cost: one phase of work re-done on crash-during-sidecar-write window. Alternative `.meta.json.pending` + rename deferred to §6.7. ✓
- **Issue #5 (LOW)** — GCS consistency. Added consistency note to `_has_checkpoint` docstring in §3.1; false-negative produces redundant work not corruption. ✓
- **Issue #6 (LOW)** — test 7 deletion mechanism. Added explicit `shutil.rmtree` instruction + `tmp_path`-scoped `file://` URI pattern in §5.1. ✓

Plus implementation notes from review:
- Added test 11 for orphan-MT auto-recovery scenario (verifies §4 atomicity policy). ✓
- Added §6.6 deferring sidecar utility extraction to a second-use trigger per [[feedback_extract_reusable_utilities]]. ✓
- Added §6.7 deferring `.meta.json.pending` atomic-rename alternative. ✓
- Added wall-clock budget regression guard to §8 success criteria. ✓

### v1 — 2026-05-18 (initial)

Initial spec capturing Q1-Q5 approved decisions from the brainstorming-skill walkthrough. Committed at `aab73a2`.

---

**End of DESIGN v2.**
