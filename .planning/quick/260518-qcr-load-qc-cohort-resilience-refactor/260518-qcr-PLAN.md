# 260518-qcr — `load_qc_cohort` algorithmic resilience refactor — IMPLEMENTATION PLAN

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `load_qc_cohort` in [src/python/aou_ld_panel.py](../../../src/python/aou_ld_panel.py) to add intermediate checkpoints + sidecar metadata + balanced repartitioning so Wave-1 cohort definition (Cells 3-5) is resumable and resilient to mid-fire failures.

**Architecture:** Internal refactor of the function with 7 new private helpers (`_intermediate_checkpoint_uri`, `_sidecar_uri`, `_collect_provenance`, `_write_sidecar`, `_read_sidecar`, `_validate_sidecar`, `_has_checkpoint`). Two intermediate checkpoints (post-split, post-sample-QC); hybrid partitioning (naive_coalesce + repartition); auto-resume with JSON sidecar parameter sanity check.

**Tech Stack:** Python 3.11 · Hail 0.2.134 · pytest · Spark/YARN on AoU Dataproc

**Approved spec:** [.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-DESIGN.md](260518-qcr-DESIGN.md) (v2.1, commit 3cb659c)

**Framing:** audit-driven re-analysis (per [[feedback_original_research_framing]]); NOT cleanup/revision/fix/salvage.

---

## File Structure

This refactor touches exactly 2 files:

| File | Action | Lines affected |
|---|---|---|
| `src/python/aou_ld_panel.py` | Modify | ~140-315 (add helpers between line 198 and line 201; modify `load_qc_cohort` body) |
| `tests/m3/test_aou_ld_panel_local.py` | Modify | Append 6 pure-Python tests after existing helper tests (~line 185); append 5 live-Hail tests after existing live-Hail tests (~end of file) |

**New helper placement** in `aou_ld_panel.py`: insert all 7 helpers between `_qc_checkpoint_uri` (ends ~line 198) and `load_qc_cohort` (starts ~line 201). This keeps the helper cluster together for readability.

**Test placement** in `test_aou_ld_panel_local.py`:
- Pure-Python tests (6 new): append after `test_qc_checkpoint_uri_accepts_prefixed_bucket` (existing helper-test cluster ends here)
- Live-Hail tests (5 new): append at end of file, after `test_compute_region_ld_skipped_few_variants`

---

## Pre-task setup

- [ ] **Step 1: Verify working tree state**

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
git status --short
git log --oneline -3
```

Expected: branch `main`, recent commits include `3cb659c` (DESIGN v2.1) and `4f6014b` (DESIGN v2). Working tree may have other tracked changes (`.planning/config.json`, results files) but `src/python/aou_ld_panel.py` and `tests/m3/test_aou_ld_panel_local.py` should be clean.

- [ ] **Step 2: Verify test suite baseline (16 existing tests pass)**

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
pytest tests/m3/test_aou_ld_panel_local.py -v 2>&1 | tail -20
```

Expected: 12 PASSED + 4 SKIPPED (live-Hail tests skip without `pytest --hail` flag and/or Hail import availability). All non-skip tests pass.

- [ ] **Step 3: Pin git commit SHA for sidecar provenance test fixture**

```bash
git rev-parse HEAD
```

Save the SHA — implementation will reference this in `_collect_provenance()` git_commit_sha field via runtime `git rev-parse` invocation; tests will mock it.

---

## Phase 1: Helper functions (pure-Python tests, TDD)

### Task 1: `_intermediate_checkpoint_uri` helper

**Files:**
- Modify: `src/python/aou_ld_panel.py:198` (insert new function after `_qc_checkpoint_uri`)
- Modify: `tests/m3/test_aou_ld_panel_local.py:185` (append test after `test_qc_checkpoint_uri_accepts_prefixed_bucket`)

- [ ] **Step 1: Write the failing test**

Append to `tests/m3/test_aou_ld_panel_local.py` after line 185:

```python
def test_intermediate_checkpoint_uri_post_split_afr_primary():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split.mt"


def test_intermediate_checkpoint_uri_post_sample_qc_afr_sensitivity():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_sample_qc", True)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_pca_selfid_post_sample_qc.mt"


def test_intermediate_checkpoint_uri_eur_no_sensitivity():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "eur", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_eur_post_split.mt"


def test_intermediate_checkpoint_uri_with_interval_filter_chr22():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_split", False, "chr22")
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split_chr22.mt"


def test_intermediate_checkpoint_uri_accepts_prefixed_bucket():
    """Defensive: bucket may arrive as 'gs://...' (per _normalize_bucket contract)."""
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("gs://fc-secure-XXX", "afr", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split.mt"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_intermediate_checkpoint_uri_post_split_afr_primary -v 2>&1 | tail -5
```

Expected: FAIL with `ImportError: cannot import name '_intermediate_checkpoint_uri' from 'aou_ld_panel'`

- [ ] **Step 3: Write minimal implementation**

Insert into `src/python/aou_ld_panel.py` after `_qc_checkpoint_uri` (ends ~line 198):

```python
def _intermediate_checkpoint_uri(bucket: str, ancestry: str, phase: str,
                                  sensitivity: bool,
                                  interval_filter: str | None = None) -> str:
    """Construct an intermediate-checkpoint URI inside /ld/intermediate/.

    Args:
        bucket: Workspace bucket (bare-name or gs://-prefixed; normalized
            via :func:`_normalize_bucket`).
        ancestry: "afr" or "eur".
        phase: "post_split" or "post_sample_qc".
        sensitivity: When True, appends "_pca_selfid" before phase suffix
            (matches the existing _qc_checkpoint_uri convention).
        interval_filter: When set (e.g., "chr22" for smoke), appends
            "_{interval}" to the URI for path-level isolation between
            smoke and production paths. Defense in depth alongside
            sidecar-level mismatch detection. Per DESIGN §3.3.

    Examples:
        >>> _intermediate_checkpoint_uri("bkt", "afr", "post_split", False)
        'gs://bkt/ld/intermediate/mt_afr_post_split.mt'
        >>> _intermediate_checkpoint_uri("bkt", "afr", "post_split", True, "chr22")
        'gs://bkt/ld/intermediate/mt_afr_pca_selfid_post_split_chr22.mt'
    """
    sens_suffix = "_pca_selfid" if sensitivity else ""
    interval_suffix = f"_{interval_filter}" if interval_filter else ""
    return (
        f"gs://{_normalize_bucket(bucket)}/ld/intermediate/"
        f"mt_{ancestry}{sens_suffix}_{phase}{interval_suffix}.mt"
    )
```

- [ ] **Step 4: Run tests to verify all 5 pass**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v -k intermediate_checkpoint_uri 2>&1 | tail -10
```

Expected: 5 PASSED.

- [ ] **Step 5: Verify no regression on existing tests**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v 2>&1 | tail -5
```

Expected: 17 PASSED + 4 SKIPPED (was 12 PASSED + 4 SKIPPED before; +5 new).

- [ ] **Step 6: Commit**

```bash
git add src/python/aou_ld_panel.py tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): _intermediate_checkpoint_uri helper -- audit-driven re-analysis

Adds URI builder for intermediate checkpoints inside /ld/intermediate/.
Includes optional interval_filter parameter for path-level isolation between
smoke and production fires (DESIGN §3.1, §3.3).

5 new pure-Python tests cover: post_split + AFR primary; post_sample_qc + AFR
sensitivity; EUR; interval_filter=chr22; bucket-prefix defensive (gs:// accepted).

Test count: 16 existing + 5 new = 21; 17 PASSED + 4 SKIPPED.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: `_sidecar_uri` helper

**Files:**
- Modify: `src/python/aou_ld_panel.py` (insert after `_intermediate_checkpoint_uri`)
- Modify: `tests/m3/test_aou_ld_panel_local.py` (append after Task 1 tests)

- [ ] **Step 1: Write the failing test**

```python
def test_sidecar_uri_format():
    from aou_ld_panel import _sidecar_uri
    checkpoint_uri = "gs://bkt/ld/intermediate/mt_afr_post_split.mt"
    assert _sidecar_uri(checkpoint_uri) == "gs://bkt/ld/intermediate/mt_afr_post_split.mt.meta.json"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_sidecar_uri_format -v 2>&1 | tail -3
```

Expected: FAIL `ImportError: cannot import name '_sidecar_uri'`.

- [ ] **Step 3: Write minimal implementation**

```python
def _sidecar_uri(checkpoint_uri: str) -> str:
    """Sidecar JSON path is the checkpoint URI + '.meta.json'.

    Hail MT checkpoints are directories (containing _SUCCESS + parquet
    parts); the sidecar lives as a sibling JSON file at the same parent
    level. The '.meta.json' extension is chosen to avoid colliding with
    any Hail/Spark-managed files inside the MT directory tree.
    """
    return checkpoint_uri + ".meta.json"
```

- [ ] **Step 4: Run test, verify PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_sidecar_uri_format -v 2>&1 | tail -3
```

Expected: PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/aou_ld_panel.py tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): _sidecar_uri helper -- audit-driven re-analysis

Trivial URI builder: appends '.meta.json' to a checkpoint URI for the
co-located sidecar JSON file per DESIGN §3.1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: `_collect_provenance` helper

**Files:**
- Modify: `src/python/aou_ld_panel.py` (insert after `_sidecar_uri`)
- Modify: `tests/m3/test_aou_ld_panel_local.py`

- [ ] **Step 1: Write the failing test**

```python
def test_collect_provenance_includes_required_fields():
    from aou_ld_panel import _collect_provenance
    prov = _collect_provenance(
        ancestry="afr",
        sensitivity=False,
        source_mt_path="gs://src/path.mt",
        interval_filter=None,
    )
    # Top-level fields (phase intentionally absent — added by _write_sidecar)
    assert prov["ancestry"] == "afr"
    assert prov["sensitivity"] is False
    assert prov["source_mt_path"] == "gs://src/path.mt"
    assert prov["interval_filter"] is None
    assert "phase" not in prov  # phase added at write time
    assert prov["schema_version"] == 1
    # Nested params dict has all 7 thresholds from DESIGN §3.4
    assert prov["params"]["MIN_CALL_RATE_SAMPLE"] == 0.98
    assert prov["params"]["MIN_MAF_INTERNAL"] == 0.005
    assert prov["params"]["MAX_MAF"] == 0.995
    assert prov["params"]["MIN_CALL_RATE_VARIANT"] == 0.95
    assert prov["params"]["MIN_HWE_PVALUE"] == 1e-06
    assert prov["params"]["HET_HOM_SD_BAND"] == 3.0
    assert prov["params"]["KING_KINSHIP_THRESHOLD"] == 0.0442
    # CDR metadata
    assert prov["cdr_version"] == "v8"
    assert prov["ancestry_preds_path"].endswith("ancestry_preds.tsv")
    assert prov["relateds_path"].endswith("relatedness_flagged_samples.tsv")
    # Git + timestamp + hail_version present (don't assert exact values)
    assert "git_commit_sha" in prov
    assert "timestamp_utc" in prov
    assert "hail_version" in prov
```

- [ ] **Step 2: Run test, verify FAIL**

Expected: `ImportError: cannot import name '_collect_provenance'`.

- [ ] **Step 3: Write minimal implementation**

```python
def _collect_provenance(ancestry: str, sensitivity: bool,
                         source_mt_path: str,
                         interval_filter: str | None = None) -> dict:
    """Collect provenance metadata for sidecar write.

    Builds the JSON-serializable dict that becomes the sidecar contents.
    DOES NOT include 'phase' field — that is added by _write_sidecar at
    write time so the same provenance dict can be written to both
    post_split and post_sample_qc sidecars.

    Per DESIGN §3.4: conservative semantics — all QC parameters are
    captured regardless of which phase consumes them. Any parameter
    change invalidates ALL intermediates for the same (ancestry,
    sensitivity, interval_filter) tuple.
    """
    import datetime
    import subprocess

    # Best-effort: capture git SHA. Falls back to "unknown" if not a git
    # checkout (e.g., tests in tmp_path that don't preserve git context).
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(Path(__file__).parent.parent.parent),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        sha = "unknown"

    # Best-effort: capture hail version. Falls back if hail not importable.
    try:
        import hail as hl
        hv = hl.__version__
    except ImportError:
        hv = "unknown"

    return {
        "ancestry": ancestry,
        "sensitivity": sensitivity,
        "interval_filter": interval_filter,
        "source_mt_path": source_mt_path,
        "params": {
            "MIN_CALL_RATE_SAMPLE": MIN_CALL_RATE_SAMPLE,
            "MIN_MAF_INTERNAL": MIN_MAF_INTERNAL,
            "MAX_MAF": MAX_MAF,
            "MIN_CALL_RATE_VARIANT": MIN_CALL_RATE_VARIANT,
            "MIN_HWE_PVALUE": MIN_HWE_PVALUE,
            "HET_HOM_SD_BAND": HET_HOM_SD_BAND,
            "KING_KINSHIP_THRESHOLD": KING_KINSHIP_THRESHOLD,
        },
        "ancestry_preds_path": ANCESTRY_PREDS_PATH,
        "relateds_path": RELATED_SAMPLES_PATH,
        "cdr_version": CDR_VERSION,
        "git_commit_sha": sha,
        "hail_version": hv,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "schema_version": 1,
    }
```

- [ ] **Step 4: Run test, verify PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_collect_provenance_includes_required_fields -v 2>&1 | tail -3
```

Expected: PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/aou_ld_panel.py tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): _collect_provenance helper -- audit-driven re-analysis

Builds the JSON-serializable provenance dict for sidecar writes per DESIGN
§3.4. Captures all 7 QC threshold parameters + CDR metadata + git SHA + hail
version + timestamp + schema_version. Phase field intentionally absent
(added by _write_sidecar at write time).

Best-effort git rev-parse and hail import — fall back to "unknown" if
unavailable (tests in tmp_path; environments without hail).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: `_write_sidecar` and `_read_sidecar` helpers (paired)

**Files:**
- Modify: `src/python/aou_ld_panel.py`
- Modify: `tests/m3/test_aou_ld_panel_local.py`

- [ ] **Step 1: Write failing test for round-trip**

```python
def test_write_read_sidecar_round_trip(tmp_path):
    from aou_ld_panel import _write_sidecar, _read_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar_path = tmp_path / "test_sidecar.meta.json"
    _write_sidecar(f"file://{sidecar_path}", prov, phase="post_split")
    read_back = _read_sidecar(f"file://{sidecar_path}")
    assert read_back is not None
    # Phase added at write time
    assert read_back["phase"] == "post_split"
    # Other fields preserved
    assert read_back["ancestry"] == "afr"
    assert read_back["sensitivity"] is False
    assert read_back["params"]["MIN_CALL_RATE_SAMPLE"] == 0.98


def test_read_sidecar_returns_none_when_absent(tmp_path):
    from aou_ld_panel import _read_sidecar
    nonexistent = tmp_path / "nope.meta.json"
    assert _read_sidecar(f"file://{nonexistent}") is None


def test_read_sidecar_rejects_unknown_schema_version(tmp_path):
    from aou_ld_panel import _read_sidecar
    import json
    sidecar_path = tmp_path / "bad_schema.meta.json"
    sidecar_path.write_text(json.dumps({"schema_version": 999, "ancestry": "afr"}))
    with pytest.raises(RuntimeError, match="schema_version"):
        _read_sidecar(f"file://{sidecar_path}")
```

- [ ] **Step 2: Run tests, verify FAIL**

Expected: 3 FAIL with `ImportError`.

- [ ] **Step 3: Write minimal implementation**

```python
def _write_sidecar(uri: str, provenance: dict, phase: str) -> None:
    """Write provenance JSON sidecar at uri.

    Adds 'phase' field to a copy of provenance before serialization so
    the input dict is not mutated (caller may reuse it for the next
    phase's sidecar in the same load_qc_cohort fire).

    Order matters: callers MUST invoke this AFTER the matching
    mt.checkpoint() returns successfully. Per DESIGN §4 atomicity policy:
    a crash window between checkpoint write and sidecar write leaves an
    orphan MT; next fire detects sidecar absence and auto-force-fresh's.

    Args:
        uri: Sidecar URI. Local-FS tests pass "file:///path/to/sidecar.meta.json";
            production AoU passes "gs://bucket/ld/intermediate/mt_*.mt.meta.json".
        provenance: Output of _collect_provenance (does NOT include 'phase').
        phase: One of {"post_split", "post_sample_qc"}.
    """
    import json
    # Use Hail's hadoop_open for unified file:// / gs:// handling
    import hail as hl
    payload = {**provenance, "phase": phase}
    with hl.hadoop_open(uri, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def _read_sidecar(uri: str) -> dict | None:
    """Read provenance JSON sidecar at uri.

    Returns:
        Parsed dict on success, None if the sidecar file does not exist.

    Raises:
        RuntimeError: if the sidecar exists but has malformed JSON or
            an unknown schema_version. Loud failure is intentional —
            silently treating bad sidecars as schema_version=1 risks
            using stale-format metadata.
    """
    import json
    import hail as hl
    try:
        with hl.hadoop_open(uri, "r") as f:
            content = f.read()
    except (FileNotFoundError, OSError):
        return None
    # hail.hadoop_open also raises generic exceptions on missing GCS objects;
    # broad-catch path-existence failures and return None.
    if not content:
        return None
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Sidecar at {uri} is malformed JSON: {e}")
    sv = parsed.get("schema_version")
    if sv != 1:
        raise RuntimeError(
            f"Sidecar at {uri} has unknown schema_version={sv!r}; "
            f"expected 1. Refusing to interpret as known schema."
        )
    return parsed
```

**Note:** Replace the `try: except (FileNotFoundError, OSError)` block with `hl.hadoop_exists(uri)` check if it works better with Hail's filesystem abstraction. Some Hail versions raise different exception types for missing GCS objects — test the pattern that actually works.

- [ ] **Step 4: Run tests, verify all 3 PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v -k sidecar 2>&1 | tail -8
```

Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/aou_ld_panel.py tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): _write_sidecar + _read_sidecar helpers -- audit-driven re-analysis

JSON sidecar I/O via hl.hadoop_open (unified file:// / gs:// handling).

_write_sidecar adds 'phase' field at write time without mutating the input
provenance dict (caller may reuse it for the second phase's sidecar).
Atomicity policy: caller invokes AFTER mt.checkpoint() returns; crash
window between is recovered on next fire (DESIGN §4).

_read_sidecar returns None on absent, raises RuntimeError on malformed
JSON or unknown schema_version. Loud failure prevents silent stale-format
interpretation.

Per DESIGN §3.1; 3 new tests (round-trip; absent → None; unknown schema_version → raise).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: `_validate_sidecar` helper

**Files:**
- Modify: `src/python/aou_ld_panel.py`
- Modify: `tests/m3/test_aou_ld_panel_local.py`

- [ ] **Step 1: Write failing tests**

```python
def test_validate_sidecar_accepts_matching():
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar = {**prov, "phase": "post_split"}  # simulates what _write_sidecar produces
    matches, diag = _validate_sidecar(sidecar, prov)
    assert matches is True
    assert diag == ""


def test_validate_sidecar_rejects_mismatched_ancestry():
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov_afr = _collect_provenance("afr", False, "gs://src/path.mt")
    prov_eur = _collect_provenance("eur", False, "gs://src/path.mt")
    sidecar = {**prov_afr, "phase": "post_split"}
    matches, diag = _validate_sidecar(sidecar, prov_eur)
    assert matches is False
    assert "ancestry" in diag.lower()


def test_validate_sidecar_rejects_mismatched_thresholds(monkeypatch):
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    import aou_ld_panel
    prov_a = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar = {**prov_a, "phase": "post_split"}
    monkeypatch.setattr(aou_ld_panel, "MIN_CALL_RATE_SAMPLE", 0.95)
    prov_b = _collect_provenance("afr", False, "gs://src/path.mt")
    matches, diag = _validate_sidecar(sidecar, prov_b)
    assert matches is False
    assert "MIN_CALL_RATE_SAMPLE" in diag


def test_validate_sidecar_ignores_phase_field():
    """phase legitimately differs between post_split + post_sample_qc sidecars for
    the same fire — _validate_sidecar must ignore it during comparison."""
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar_a = {**prov, "phase": "post_split"}
    sidecar_b = {**prov, "phase": "post_sample_qc"}
    assert _validate_sidecar(sidecar_a, prov)[0] is True
    assert _validate_sidecar(sidecar_b, prov)[0] is True


def test_validate_sidecar_ignores_timestamp_and_git_sha():
    """timestamp_utc and git_commit_sha legitimately drift across runs of the
    same parameters — they're audit metadata, not invalidation triggers."""
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar = {**prov, "phase": "post_split",
               "timestamp_utc": "1970-01-01T00:00:00.000Z",
               "git_commit_sha": "deadbeef"}
    assert _validate_sidecar(sidecar, prov)[0] is True
```

- [ ] **Step 2: Run tests, verify FAIL**

Expected: 5 FAIL with `ImportError`.

- [ ] **Step 3: Write minimal implementation**

```python
# Fields that legitimately differ between sidecar and current call.
# Excluded from _validate_sidecar comparison.
_SIDECAR_COMPARE_EXCLUDE_FIELDS = frozenset({
    "phase",            # phase is per-sidecar; not a fire-level parameter
    "timestamp_utc",    # write time; drifts across runs of same params
    "git_commit_sha",   # audit metadata; non-breaking code changes ok
    "hail_version",     # build-environment; ok to drift across runs
})


def _validate_sidecar(sidecar: dict, provenance: dict) -> tuple[bool, str]:
    """Compare sidecar against current provenance dict.

    Returns:
        (True, "") if all relevant fields match.
        (False, diagnostic_str) if any relevant field differs. The
        diagnostic enumerates the mismatched field names + values for
        each side (sidecar vs current).

    Comparison rules per DESIGN §3.4 + v2 CHANGELOG:
        - All top-level fields are compared EXCEPT those in
          _SIDECAR_COMPARE_EXCLUDE_FIELDS (phase, timestamp_utc,
          git_commit_sha, hail_version).
        - 'params' dict is compared element-by-element. Any threshold
          difference is a mismatch.

    Conservative semantics: ANY divergence outside the excluded set
    invalidates the intermediate. Caller passes force_fresh=True to
    override.
    """
    mismatches = []
    # Top-level fields
    sidecar_keys = set(sidecar.keys()) - _SIDECAR_COMPARE_EXCLUDE_FIELDS
    provenance_keys = set(provenance.keys()) - _SIDECAR_COMPARE_EXCLUDE_FIELDS
    for k in sorted(sidecar_keys | provenance_keys):
        if k == "params":
            continue  # handled separately below
        sv = sidecar.get(k, "<absent>")
        pv = provenance.get(k, "<absent>")
        if sv != pv:
            mismatches.append(f"  {k}: sidecar={sv!r} current={pv!r}")
    # Params dict
    sidecar_params = sidecar.get("params", {})
    provenance_params = provenance.get("params", {})
    for k in sorted(set(sidecar_params.keys()) | set(provenance_params.keys())):
        sv = sidecar_params.get(k, "<absent>")
        pv = provenance_params.get(k, "<absent>")
        if sv != pv:
            mismatches.append(f"  params.{k}: sidecar={sv!r} current={pv!r}")
    if not mismatches:
        return True, ""
    diag = (
        f"mismatch on {len(mismatches)} field(s):\n"
        + "\n".join(mismatches)
    )
    return False, diag
```

- [ ] **Step 4: Run tests, verify all 5 PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v -k validate_sidecar 2>&1 | tail -8
```

Expected: 5 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/python/aou_ld_panel.py tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): _validate_sidecar helper -- audit-driven re-analysis

Compares sidecar metadata against current provenance for resume safety.
All top-level fields + all params dict entries are compared EXCEPT the
excluded set (phase, timestamp_utc, git_commit_sha, hail_version) which
legitimately drift across runs of the same parameters.

Diagnostic lists every mismatched field with sidecar-vs-current values
for surface-able error messages in the RuntimeError raise path.

Per DESIGN §3.1 + §3.4. 5 new tests: matching; mismatched ancestry;
mismatched threshold (via monkeypatch); phase-ignored; timestamp+git-sha-ignored.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: `_has_checkpoint` helper

**Files:**
- Modify: `src/python/aou_ld_panel.py`
- Modify: `tests/m3/test_aou_ld_panel_local.py`

- [ ] **Step 1: Write failing tests**

```python
def test_has_checkpoint_returns_false_when_absent(tmp_path):
    from aou_ld_panel import _has_checkpoint
    nonexistent = tmp_path / "nope.mt"
    assert _has_checkpoint(f"file://{nonexistent}") is False


def test_has_checkpoint_returns_true_when_success_marker_present(tmp_path):
    from aou_ld_panel import _has_checkpoint
    mt_dir = tmp_path / "fake.mt"
    mt_dir.mkdir()
    (mt_dir / "_SUCCESS").write_text("")
    assert _has_checkpoint(f"file://{mt_dir}") is True


def test_has_checkpoint_returns_false_when_mt_dir_exists_but_no_success(tmp_path):
    """An MT directory with parquet files but no _SUCCESS marker is an
    incomplete write (e.g., previous run was interrupted). _has_checkpoint
    must distinguish this from a complete checkpoint."""
    from aou_ld_panel import _has_checkpoint
    mt_dir = tmp_path / "partial.mt"
    mt_dir.mkdir()
    (mt_dir / "part-00000.parquet").write_text("fake parquet")
    # no _SUCCESS file
    assert _has_checkpoint(f"file://{mt_dir}") is False
```

- [ ] **Step 2: Run tests, verify FAIL**

Expected: 3 FAIL with `ImportError`.

- [ ] **Step 3: Write minimal implementation**

```python
def _has_checkpoint(uri: str) -> bool:
    """Check for {uri}/_SUCCESS marker (definitive completion signal).

    Hail's mt.checkpoint() writes parquet files into the MT directory
    and finalizes with an atomic _SUCCESS marker. Existence of the
    _SUCCESS marker is the definitive "this checkpoint was written
    successfully" signal — partial writes (interrupted, crashed) leave
    parquet shards but no _SUCCESS.

    GCS object existence is strongly consistent (Google's 2020
    consistency model upgrade — read-after-write on individual objects).
    False-negative due to list-operation eventual-consistency edge cases
    would result in redundant work (re-firing a completed phase), not
    corruption.
    """
    import hail as hl
    success_marker_uri = f"{uri}/_SUCCESS"
    try:
        return hl.hadoop_is_file(success_marker_uri)
    except Exception:
        # Defensive: any filesystem error during the existence check
        # is treated as "checkpoint not present" — safer to redo work
        # than to assume a checkpoint that may not actually exist.
        return False
```

- [ ] **Step 4: Run tests, verify all 3 PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v -k has_checkpoint 2>&1 | tail -8
```

Expected: 3 PASSED.

- [ ] **Step 5: Verify full pure-Python test suite still green**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v 2>&1 | tail -8
```

Expected: 33 PASSED + 4 SKIPPED. (16 original + 5 task-1 + 1 task-2 + 1 task-3 + 3 task-4 + 5 task-5 + 3 task-6 = 16 + 18 new = 34 pure-Python tests... wait, that's 34. Let me recount.)

Recount: Tasks 1-6 added 5 + 1 + 1 + 3 + 5 + 3 = 18 new pure-Python tests. 16 original + 18 new = 34 total pure-Python tests. Plus 4 live-Hail SKIPS = 38 total.

Actually, this exceeds the spec's "6 pure-Python tests" count. The spec listed 6 representative tests; the implementation expanded each into multiple focused cases. This is a strengthening of coverage, not scope creep. Document in commit.

Expected: 34 PASSED + 4 SKIPPED.

- [ ] **Step 6: Commit**

```bash
git add src/python/aou_ld_panel.py tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): _has_checkpoint helper -- audit-driven re-analysis

Checks for {uri}/_SUCCESS marker via hl.hadoop_is_file. Definitive
"this checkpoint completed atomically" signal per Hail/Spark conventions.
Partial writes (parquet shards without _SUCCESS) correctly return False.

Defensive: any filesystem error during the existence check is treated as
"checkpoint not present" — safer to redo work than risk false positive.

Per DESIGN §3.1. 3 new tests: absent path; _SUCCESS present; partial MT dir
(parquet without _SUCCESS).

Pure-Python test count milestone: 34 PASSED + 4 SKIPPED (all 7 helpers
landed; live-Hail tests pending Tasks 10-14).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 2: Refactor `load_qc_cohort` function body

### Task 7: Add new kwargs `force_fresh` + `interval_filter` to signature (no behavior change yet)

**Files:**
- Modify: `src/python/aou_ld_panel.py:201` (`load_qc_cohort` signature only)

- [ ] **Step 1: Read current load_qc_cohort signature and docstring**

```bash
sed -n '201,230p' src/python/aou_ld_panel.py
```

- [ ] **Step 2: Update signature to add keyword-only `force_fresh` + `interval_filter`**

Modify the function signature in `src/python/aou_ld_panel.py` (currently spans lines ~201-205) to:

```python
def load_qc_cohort(mt_path: str, ancestry: str, sensitivity: bool = False,
                   ancestry_table_path: str | None = None,
                   relateds_table_path: str | None = None,
                   workspace_bucket: str | None = None,
                   skip_checkpoint: bool = False,
                   *,
                   force_fresh: bool = False,
                   interval_filter: str | None = None,
                   ) -> "hl.MatrixTable":
```

Note the `*,` to make the new kwargs keyword-only.

Also update the docstring's Args section to add:
```
        force_fresh: When True, bypass auto-resume checks; overwrite any
            existing intermediates. Default False (auto-resume active).
            Per DESIGN §3.5 + §4.
        interval_filter: When set (e.g., "chr22"), filter source MT to
            this interval right after read_matrix_table. Used by smoke
            tests for path-isolated execution; produces URI-suffixed
            intermediates. Default None (no filter; production fire).
            Per DESIGN §3.5.
```

- [ ] **Step 3: Run full test suite, verify no regression**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v 2>&1 | tail -5
```

Expected: still 34 PASSED + 4 SKIPPED. (kwarg-only additions don't break existing callers.)

- [ ] **Step 4: Commit**

```bash
git add src/python/aou_ld_panel.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): add force_fresh + interval_filter kwargs to load_qc_cohort -- audit-driven re-analysis

Adds two new keyword-only parameters to load_qc_cohort's signature without
changing function body (auto-resume logic comes in Task 8). Signature
extension only; existing callers still work (kwargs are after `*` and
default to safe values).

Per DESIGN §3.2.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Implement auto-resume detection in load_qc_cohort

**Files:**
- Modify: `src/python/aou_ld_panel.py` (insert auto-resume block early in load_qc_cohort body, ~after line 238 where existing code reads anc_path / rel_path)

- [ ] **Step 1: Identify insertion point**

```bash
sed -n '231,245p' src/python/aou_ld_panel.py
```

The auto-resume block should be inserted AFTER the SUPPORTED_ANCESTRIES check (`if ancestry not in ...`) and AFTER the anc_path/rel_path defaults are resolved, but BEFORE the existing read_matrix_table call (currently at ~line 242).

- [ ] **Step 2: Add auto-resume state machine**

Insert the following block after the `rel_path = ...` line and BEFORE `# Step 1: load the AoU MT`:

```python
    # Resilience refactor: compute intermediate-checkpoint URIs + auto-resume
    # state machine (DESIGN §3.5).
    state = "FRESH"
    auto_fresh = False
    ckpt_post_split = None
    ckpt_post_sqc = None
    provenance = None
    if not skip_checkpoint:
        bucket = workspace_bucket or os.environ.get("WORKSPACE_BUCKET")
        if not bucket:
            raise RuntimeError("WORKSPACE_BUCKET not set; cannot checkpoint")
        ckpt_post_split = _intermediate_checkpoint_uri(
            bucket, ancestry, "post_split", sensitivity, interval_filter)
        ckpt_post_sqc = _intermediate_checkpoint_uri(
            bucket, ancestry, "post_sample_qc", sensitivity, interval_filter)
        provenance = _collect_provenance(
            ancestry, sensitivity, mt_path, interval_filter)

        if not force_fresh:
            # Check deepest intermediate first (post_sample_qc) — if it's
            # present with valid sidecar, we skip both Phase 1 and Phase 2.
            if _has_checkpoint(ckpt_post_sqc):
                sidecar = _read_sidecar(_sidecar_uri(ckpt_post_sqc))
                if sidecar is None:
                    # Orphan: MT present but sidecar absent (crash window between
                    # the two writes in a prior fire). Auto-recover.
                    print(f"[load_qc_cohort] WARN: orphan MT at {ckpt_post_sqc} "
                          f"(sidecar absent); auto-force-fresh recovery")
                    auto_fresh = True
                else:
                    matches, diag = _validate_sidecar(sidecar, provenance)
                    if matches:
                        state = "RESUME_FROM_POST_SAMPLE_QC"
                    else:
                        raise RuntimeError(
                            f"Stale intermediate at {ckpt_post_sqc}: {diag}\n"
                            f"Use force_fresh=True to overwrite, or fix the "
                            f"parameter mismatch."
                        )
            elif _has_checkpoint(ckpt_post_split):
                sidecar = _read_sidecar(_sidecar_uri(ckpt_post_split))
                if sidecar is None:
                    print(f"[load_qc_cohort] WARN: orphan MT at {ckpt_post_split} "
                          f"(sidecar absent); auto-force-fresh recovery")
                    auto_fresh = True
                else:
                    matches, diag = _validate_sidecar(sidecar, provenance)
                    if matches:
                        state = "RESUME_FROM_POST_SPLIT"
                    else:
                        raise RuntimeError(
                            f"Stale intermediate at {ckpt_post_split}: {diag}\n"
                            f"Use force_fresh=True to overwrite, or fix the "
                            f"parameter mismatch."
                        )

    # Effective overwrite flag for intermediate writes
    overwrite_flag = force_fresh or auto_fresh
    print(f"[load_qc_cohort] state={state} ancestry={ancestry} "
          f"sensitivity={sensitivity} interval_filter={interval_filter}")
```

- [ ] **Step 3: Run full test suite, verify no regression on existing tests**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v 2>&1 | tail -5
```

Expected: still 34 PASSED + 4 SKIPPED. The new block is unreachable for `skip_checkpoint=True` callers (the existing live-Hail test uses skip_checkpoint), so no behavior change observable.

- [ ] **Step 4: Commit**

```bash
git add src/python/aou_ld_panel.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): auto-resume state machine in load_qc_cohort -- audit-driven re-analysis

Adds the FRESH / RESUME_FROM_POST_SPLIT / RESUME_FROM_POST_SAMPLE_QC state
detection block at the head of load_qc_cohort body, before the existing
read_matrix_table call. Sets up bucket URIs, provenance dict, and
overwrite_flag for the subsequent phase writes.

Behavior change: NONE yet for callers using skip_checkpoint=True (the state
machine is gated behind `if not skip_checkpoint:`). Live-Hail tests with
skip_checkpoint=False will start exercising the new logic in Task 10+.

Per DESIGN §3.5.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Refactor function body into 3 phases with intermediate checkpoint writes

**Files:**
- Modify: `src/python/aou_ld_panel.py` (rewrite the function body from `# Step 1: load the AoU MT` to the existing final checkpoint)

This is the largest single change. Steps below explicitly enumerate the rewrite.

- [ ] **Step 1: Read the existing function body**

```bash
sed -n '240,316p' src/python/aou_ld_panel.py
```

Confirm the current body has 8 numbered steps + checkpoint write.

- [ ] **Step 2: Replace the existing body with the Phase 1 / Phase 2 / Phase 3 structure**

Replace lines from `# Step 1: load the AoU MT` (was ~line 241) through the existing final `return mt` (was ~line 316) with:

```python
    # Phase 1: read + filter + split (former steps 1-6)
    if state == "FRESH":
        # Step 1: load the AoU MT (or local synthetic MT)
        mt = hl.read_matrix_table(mt_path)

        # Apply interval filter for smoke tests (no-op for production fires)
        if interval_filter is not None:
            mt = hl.filter_intervals(
                mt,
                [hl.parse_locus_interval(interval_filter, reference_genome="GRCh38")],
            )

        # Step 2: cohort filter on ancestry_pred
        if ANCESTRY_FIELD in mt.col:
            mt = mt.filter_cols(mt[ANCESTRY_FIELD] == ancestry)
        else:
            anc_ht = hl.import_table(anc_path, key="research_id",
                                     types={"research_id": hl.tstr})
            mt = mt.annotate_cols(**{ANCESTRY_FIELD: anc_ht[mt.s][ANCESTRY_FIELD]})
            mt = mt.filter_cols(mt[ANCESTRY_FIELD] == ancestry)

        # Step 3: anti-join against flagged-relateds
        try:
            rel_ht = hl.import_table(rel_path, key="sample_id",
                                     types={"sample_id": hl.tstr})
            mt = mt.anti_join_cols(rel_ht)
        except Exception as e:
            print(f"WARN: relateds table unavailable ({rel_path}): {e}; "
                  f"skipping anti_join", file=sys.stderr)

        # Step 4: optional sensitivity filter
        if sensitivity and "self_report" in mt.col:
            mt = mt.filter_cols(mt.self_report.contains("Black or African American"))

        # Step 5: naive_coalesce (cheap upstream coalesce; DEC-2026-05-04-01)
        mt = mt.naive_coalesce(2048)

        # Step 6: split_multi_hts BEFORE variant_qc (canonical ordering)
        mt = hl.split_multi_hts(mt)

        # Q3 hybrid: repartition for balanced QC phase before writing intermediate 1.
        # The shuffle cost amortizes into the GCS write that was already required.
        mt = mt.repartition(2048)

        # Intermediate 1 checkpoint + sidecar (DESIGN §3.5 atomicity policy:
        # checkpoint write FIRST, then sidecar write).
        if not skip_checkpoint:
            mt = mt.checkpoint(ckpt_post_split, overwrite=overwrite_flag)
            _write_sidecar(_sidecar_uri(ckpt_post_split), provenance, phase="post_split")
            print(f"[load_qc_cohort] wrote intermediate 1: {ckpt_post_split}")
    elif state == "RESUME_FROM_POST_SPLIT":
        mt = hl.read_matrix_table(ckpt_post_split)
        print(f"[load_qc_cohort] resumed from intermediate 1: {ckpt_post_split}")
    elif state == "RESUME_FROM_POST_SAMPLE_QC":
        mt = hl.read_matrix_table(ckpt_post_sqc)
        print(f"[load_qc_cohort] resumed from intermediate 2: {ckpt_post_sqc}")

    # Phase 2: sample QC + het filter (former steps 7-9)
    if state in ("FRESH", "RESUME_FROM_POST_SPLIT"):
        # Step 7: sample_qc + call_rate >= 0.98
        mt = hl.sample_qc(mt, name="sqc")
        mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)

        # Step 8: heterozygosity ±3 SD (within ancestry-filtered cohort)
        het_stats = mt.aggregate_cols(hl.agg.stats(mt.sqc.r_het_hom_var))
        if het_stats.stdev is not None and het_stats.stdev > 0:
            lo = het_stats.mean - HET_HOM_SD_BAND * het_stats.stdev
            hi = het_stats.mean + HET_HOM_SD_BAND * het_stats.stdev
            mt = mt.filter_cols((mt.sqc.r_het_hom_var >= lo) &
                                (mt.sqc.r_het_hom_var <= hi))

        # Intermediate 2 checkpoint + sidecar
        if not skip_checkpoint:
            mt = mt.checkpoint(ckpt_post_sqc, overwrite=overwrite_flag)
            _write_sidecar(_sidecar_uri(ckpt_post_sqc), provenance, phase="post_sample_qc")
            print(f"[load_qc_cohort] wrote intermediate 2: {ckpt_post_sqc}")

    # Phase 3: variant_qc + filters + final checkpoint (former steps 10-12)
    mt = hl.variant_qc(mt, name="vqc")
    mt = mt.filter_rows(
        (mt.vqc.AF[1] >= MIN_MAF_INTERNAL) &
        (mt.vqc.AF[1] <= MAX_MAF) &
        (mt.vqc.call_rate >= MIN_CALL_RATE_VARIANT) &
        (mt.vqc.p_value_hwe >= MIN_HWE_PVALUE)
    )

    # Drop AoU-flagged variants (filters non-empty)
    if "filters" in mt.row:
        mt = mt.filter_rows(hl.len(mt.filters) == 0)

    # Final checkpoint to workspace bucket
    if not skip_checkpoint:
        ckpt = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
        mt = mt.checkpoint(ckpt, overwrite=True)
        print(f"[load_qc_cohort] wrote final: {ckpt}")

    return mt
```

Note: The `bucket` variable is set inside the `if not skip_checkpoint:` block in Task 8. For the final checkpoint to work, ensure `bucket` is in scope here (it is, since both blocks live in the same function scope).

- [ ] **Step 3: Run full test suite, verify existing live-Hail tests still pass**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v 2>&1 | tail -10
```

Expected: 34 PASSED + 4 SKIPPED still. The existing live-Hail tests use `skip_checkpoint=True` so all intermediate-checkpoint code paths are skipped; the function still returns the same lazy MT for downstream assertions.

Optionally, run with hail to exercise the new code path on synthetic MT:
```bash
HAIL_AVAILABLE=1 pytest tests/m3/test_aou_ld_panel_local.py::test_aou_driver_loads_synthetic_mt -v 2>&1 | tail -10
```

(Skipped if hail not installed locally; equivalent to running on AoU.)

- [ ] **Step 4: Commit**

```bash
git add src/python/aou_ld_panel.py
git commit -m "$(cat <<'EOF'
feat(m3-W1-qc-cohort-resilience): refactor load_qc_cohort body into Phase 1/2/3 with intermediate checkpoints -- audit-driven re-analysis

Rewrites the function body to split the former 8-step linear pipeline into
three phases with intermediate checkpoint writes between them:

  Phase 1 (former steps 1-6): read + ancestry filter + relateds anti-join +
    sensitivity filter + naive_coalesce + split_multi_hts + repartition(2048)
    -> write intermediate 1 (mt_*_post_split.mt)

  Phase 2 (former steps 7-9): sample_qc + call_rate filter + het ±3 SD filter
    -> write intermediate 2 (mt_*_post_sample_qc.mt)

  Phase 3 (former steps 10-12): variant_qc + MAF/HWE/call_rate filter +
    drop AoU-flagged variants -> final checkpoint (mt_*_qc.mt; existing path)

The repartition(2048) between split_multi_hts and intermediate 1 is the
hybrid-partitioning fix (DESIGN §3 Q3) addressing the 2026-05-18 Cell 3
empirical observation of partition-skew-induced bimodal task velocity.

Each Phase 1/Phase 2 path is conditional on the `state` set by Task 8's
auto-resume state machine. Phase 3 runs in all states.

Checkpoint write -> sidecar write order is intentional (DESIGN §4 atomicity
policy). Crash window between the two is recovered on next fire via the
orphan-MT auto-force-fresh path.

Existing 34 PASSED + 4 SKIPPED test count unchanged (existing live-Hail
tests use skip_checkpoint=True; intermediate-write paths exercised by new
live-Hail tests in Tasks 10-14).

Per DESIGN §3.5.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 3: Live-Hail tests for the new behaviors

These tests require Hail to be importable. They use the `synthetic_mt_path` fixture from `tests/m3/conftest.py` (D-M3-06 dev mirror) and `tmp_path`-scoped `file://` URIs for the `workspace_bucket` parameter.

### Task 10: Test 7 — `test_load_qc_cohort_auto_resume_from_post_split`

**Files:**
- Modify: `tests/m3/test_aou_ld_panel_local.py` (append after existing live-Hail tests at end of file)

- [ ] **Step 1: Write the test**

Append at end of file (after `test_compute_region_ld_skipped_few_variants`):

```python
@pytest.fixture
def synthetic_bucket(tmp_path):
    """File:// URI emulating a workspace bucket for live-Hail tests."""
    bucket_dir = tmp_path / "bucket"
    bucket_dir.mkdir()
    return f"file://{bucket_dir}"


def test_load_qc_cohort_auto_resume_from_post_split(
    synthetic_mt_path: Path, synthetic_bucket: str, tmp_path, capsys
):
    """Fire once (writes intermediate 1+2+final); delete intermediate 2; fire
    again -> expect resume from intermediate 1 (Phase 1 skipped, Phase 2 + 3
    re-run). Per DESIGN §5.1 test 7 + Issue #6 fix (shutil.rmtree pattern)."""
    import shutil
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    # First fire: FRESH state, writes all 3 checkpoints
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,  # ensure fresh start for this test
    )
    captured = capsys.readouterr()
    assert "state=FRESH" in captured.out

    # Delete intermediate 2 (post_sample_qc) — leave intermediate 1 + sidecar intact
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int2_dir = bucket_path / "ld" / "intermediate" / "mt_afr_post_sample_qc.mt"
    int2_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_sample_qc.mt.meta.json"
    assert int2_dir.exists(), "first fire should have written intermediate 2"
    shutil.rmtree(int2_dir)
    int2_sidecar.unlink()

    # Second fire: should resume from intermediate 1
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        # force_fresh defaults to False — auto-resume active
    )
    captured = capsys.readouterr()
    assert "state=RESUME_FROM_POST_SPLIT" in captured.out
    assert "resumed from intermediate 1" in captured.out
```

- [ ] **Step 2: Run the test, verify PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_load_qc_cohort_auto_resume_from_post_split -v 2>&1 | tail -10
```

Expected: PASSED (if hail available) or SKIPPED (if not). On HPC with Hail installed: PASSED. On a system without Hail: SKIPPED via `_require_hail`.

- [ ] **Step 3: Commit**

```bash
git add tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
test(m3-W1-qc-cohort-resilience): auto_resume_from_post_split live-Hail test -- audit-driven re-analysis

Verifies the RESUME_FROM_POST_SPLIT path in load_qc_cohort's state machine.
First fire writes intermediate 1+2+final on synthetic MT; deletes intermediate
2 (shutil.rmtree on MT dir + sidecar.unlink); second fire detects intermediate
1 still present and matching, resumes from there.

synthetic_bucket fixture provides tmp_path-scoped file:// URI for the
workspace_bucket parameter (consistent with existing test pattern).

Per DESIGN §5.1 test 7 + §3.5 control flow.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 11: Test 8 — `test_load_qc_cohort_auto_resume_from_post_sample_qc`

- [ ] **Step 1: Write the test**

```python
def test_load_qc_cohort_auto_resume_from_post_sample_qc(
    synthetic_mt_path: Path, synthetic_bucket: str, capsys
):
    """Fire once; fire again unchanged -> expect resume from intermediate 2
    (deepest available; Phase 1 + Phase 2 skipped, only Phase 3 re-runs)."""
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    capsys.readouterr()  # clear

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
    )
    captured = capsys.readouterr()
    assert "state=RESUME_FROM_POST_SAMPLE_QC" in captured.out
    assert "resumed from intermediate 2" in captured.out
```

- [ ] **Step 2: Run + verify PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_load_qc_cohort_auto_resume_from_post_sample_qc -v 2>&1 | tail -5
```

Expected: PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
test(m3-W1-qc-cohort-resilience): auto_resume_from_post_sample_qc live-Hail test -- audit-driven re-analysis

Verifies the RESUME_FROM_POST_SAMPLE_QC path (deepest auto-resume target).
Second fire of an unmodified load_qc_cohort call against existing intermediates
hits intermediate 2 and skips both Phase 1 and Phase 2; only Phase 3 re-runs.

Per DESIGN §5.1 test 8.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 12: Test 9 — `test_load_qc_cohort_force_fresh_bypasses_auto_resume`

- [ ] **Step 1: Write the test**

```python
def test_load_qc_cohort_force_fresh_bypasses_auto_resume(
    synthetic_mt_path: Path, synthetic_bucket: str, capsys
):
    """force_fresh=True must bypass the auto-resume detection even when valid
    intermediates exist. Verifies the user-override semantic in DESIGN §4."""
    import time
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int1_mt = bucket_path / "ld" / "intermediate" / "mt_afr_post_split.mt"
    initial_mtime = int1_mt.stat().st_mtime
    time.sleep(1.1)  # ensure st_mtime difference detectable on coarse FS
    capsys.readouterr()  # clear

    # Second fire with force_fresh=True — should NOT resume; should overwrite
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    captured = capsys.readouterr()
    assert "state=FRESH" in captured.out
    # Intermediate 1 was overwritten (mtime advanced)
    new_mtime = int1_mt.stat().st_mtime
    assert new_mtime > initial_mtime, (
        f"force_fresh should overwrite intermediate 1 (old mtime={initial_mtime}, "
        f"new mtime={new_mtime})"
    )
```

- [ ] **Step 2: Run + verify PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_load_qc_cohort_force_fresh_bypasses_auto_resume -v 2>&1 | tail -5
```

Expected: PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
test(m3-W1-qc-cohort-resilience): force_fresh_bypasses_auto_resume live-Hail test -- audit-driven re-analysis

Verifies the force_fresh=True user-override path. Even when valid intermediates
exist on disk, force_fresh bypasses auto-resume detection and re-runs all
phases (intermediate 1 mtime advances; state=FRESH in stdout).

Per DESIGN §5.1 test 9 + §4 error-handling table.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 13: Test 10 — `test_load_qc_cohort_raises_on_sidecar_mismatch`

- [ ] **Step 1: Write the test**

```python
def test_load_qc_cohort_raises_on_sidecar_mismatch(
    synthetic_mt_path: Path, synthetic_bucket: str
):
    """Sidecar parameter mismatch -> RuntimeError with informative diagnostic.
    Verifies the safety guard against silently using stale-parameter intermediates."""
    import json
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )

    # Manually edit the intermediate-2 sidecar to flip ancestry to "eur"
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int2_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_sample_qc.mt.meta.json"
    sc = json.loads(int2_sidecar.read_text())
    sc["ancestry"] = "eur"  # mismatch with the next call's ancestry="afr"
    int2_sidecar.write_text(json.dumps(sc, indent=2, sort_keys=True))

    # Second fire — auto-resume should detect mismatch and raise
    with pytest.raises(RuntimeError, match=r"(?i)ancestry"):
        load_qc_cohort(
            mt_path=str(synthetic_mt_path),
            ancestry="afr",
            sensitivity=False,
            workspace_bucket=synthetic_bucket.removeprefix("file://"),
        )
```

- [ ] **Step 2: Run + verify PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_load_qc_cohort_raises_on_sidecar_mismatch -v 2>&1 | tail -5
```

Expected: PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
test(m3-W1-qc-cohort-resilience): raises_on_sidecar_mismatch live-Hail test -- audit-driven re-analysis

Verifies the sidecar-mismatch RuntimeError safety guard. After a successful
fire, the test manually edits the intermediate-2 sidecar to flip ancestry
from "afr" to "eur"; the next load_qc_cohort call with ancestry="afr" must
raise RuntimeError with "ancestry" in the diagnostic.

Per DESIGN §5.1 test 10 + §4 error-handling table.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 14: Test 11 — `test_load_qc_cohort_auto_recovers_from_orphan_mt`

- [ ] **Step 1: Write the test**

```python
def test_load_qc_cohort_auto_recovers_from_orphan_mt(
    synthetic_mt_path: Path, synthetic_bucket: str, capsys
):
    """Sidecar-absent-but-MT-exists is an orphan from a prior crash window
    between checkpoint write and sidecar write. Auto-recovery: print WARN,
    treat as FRESH, overwrite the orphan. Per DESIGN §4 atomicity policy."""
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    capsys.readouterr()  # clear

    # Delete intermediate-1 sidecar but leave MT directory (orphan state)
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int1_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_split.mt.meta.json"
    int1_mt = bucket_path / "ld" / "intermediate" / "mt_afr_post_split.mt"
    assert int1_sidecar.exists() and int1_mt.exists(), "setup precondition"
    int1_sidecar.unlink()
    assert int1_mt.exists(), "MT directory should still exist after sidecar removal"

    # Also need to delete intermediate-2 (else auto-resume picks deepest valid)
    int2_mt = bucket_path / "ld" / "intermediate" / "mt_afr_post_sample_qc.mt"
    int2_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_sample_qc.mt.meta.json"
    import shutil
    shutil.rmtree(int2_mt)
    int2_sidecar.unlink()

    # Second fire: should detect orphan intermediate 1, WARN, auto-force-fresh
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
    )
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "orphan MT" in captured.out
    assert "state=FRESH" in captured.out
```

- [ ] **Step 2: Run + verify PASS**

```bash
pytest tests/m3/test_aou_ld_panel_local.py::test_load_qc_cohort_auto_recovers_from_orphan_mt -v 2>&1 | tail -5
```

Expected: PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/m3/test_aou_ld_panel_local.py
git commit -m "$(cat <<'EOF'
test(m3-W1-qc-cohort-resilience): auto_recovers_from_orphan_mt live-Hail test -- audit-driven re-analysis

Verifies the orphan-MT auto-recovery path. An MT-present-but-sidecar-absent
state simulates the crash window between mt.checkpoint() returning and the
subsequent _write_sidecar() call in a prior fire. The next fire must:
  - Print WARN to stdout naming the orphan path
  - Set state=FRESH with auto_fresh=True
  - Overwrite the orphan on the next intermediate write

Per DESIGN §5.1 test 11 + §4 atomicity policy (added in v2 to address
spec review v1 Issue #4).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 4: Verification and final commit

### Task 15: Full test suite verification + cumulative summary commit

**Files:**
- Read only: `src/python/aou_ld_panel.py`, `tests/m3/test_aou_ld_panel_local.py`

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/m3/test_aou_ld_panel_local.py -v 2>&1 | tail -25
```

Expected: 39 PASSED (16 original + 18 new pure-Python + 5 new live-Hail with Hail available) + 4 SKIPPED (or fewer skipped if HPC has Hail) OR 34 PASSED + 9 SKIPPED (without Hail).

**Acceptance gate:** at least 34 PASSED + 9 SKIPPED on a system without Hail; OR 39 PASSED + 4 SKIPPED on a system with Hail. The 16 originally-passing pure-Python tests MUST still pass.

- [ ] **Step 2: Run a quick lint check**

```bash
python -m py_compile src/python/aou_ld_panel.py
echo "Exit code: $?"
```

Expected: exit 0. (We're checking only for syntactic correctness — the project doesn't use a strict linter in this directory.)

- [ ] **Step 3: Verify commit history is clean and well-described**

```bash
git log --oneline -20
```

Expected: 14 new commits (Tasks 1-14 each produce one commit) in linear order on top of `3cb659c` (the v2.1 DESIGN). All commit messages follow the `feat(m3-W1-qc-cohort-resilience):` or `test(m3-W1-qc-cohort-resilience):` convention.

- [ ] **Step 4: No final summary commit (the per-task commits ARE the audit trail)**

Per [[feedback_multi_terminal_staging]] and the project's atomic-commit convention, do not create a summary commit. Each task's commit is the audit-trail entry.

- [ ] **Step 5: Push to origin (NOT automatic — surface to user)**

The push to origin is the next step but requires explicit user authorization. Surface to Carter:

> "Implementation complete. All 14 tasks committed locally. 27+ tests passing (16 original + 18 new pure-Python + 5 new live-Hail). Ready to push to origin via the established cherry-pick-on-push-fix-branch pattern (per 779fe84 precedent). Authorize push?"

---

## Out-of-scope handoff for next session

After the implementation is pushed to origin:

1. **AoU clone update on the env Carter will provision for re-fire** — `git pull origin main` on `/home/jupyter/coloc_analysis`.

2. **chr22 smoke test on AoU** — fire the smoke cell from DESIGN §5.2 (twice: fresh + resume). Verify wall-clock budget assertions (fresh ≤ 30 min, resume ≤ 5 min on 256-vCPU cluster) per DESIGN §8.

3. **Production EUR fire (Cell 5 only)** — with refactored code, fire `load_qc_cohort(ancestry='eur', sensitivity=False, ...)`. Per Path C′ context, AFR primary + AFR sensitivity are expected to already exist from this session's pre-refactor fire.

4. **Wave-1 complete bundled push** — accumulate fc1a94f (260514-npb docs not yet pushed) + this refactor's commits + final STATE.md Wave-1-complete update; cherry-pick onto push-fix branch off origin/main; fast-forward push (same procedure as 779fe84).

---

## Notes for the executor

- **Hail availability**: HPC's `/rs1/researchers/c/ckclinto/conda_envs/m3-aou-dev/` env may have Hail installed; `which python && python -c 'import hail'` confirms. If yes, live-Hail tests run. If no, they SKIP gracefully (the `_require_hail()` helper in the test file handles this).
- **Spec authority**: DESIGN.md at commit `3cb659c` is the authoritative source. Any conflict between this PLAN and DESIGN → defer to DESIGN.
- **TDD discipline**: do not skip the RED phase (failing test before implementation). The RED step is the regression guard — it proves the test actually tests something.
- **Sidecar import path**: `_write_sidecar` and `_read_sidecar` use `hl.hadoop_open` which works for both `file://` (tests) and `gs://` (production). Do NOT special-case the URI scheme in the helpers; let Hail's filesystem abstraction handle it.

---

**End of PLAN.**
