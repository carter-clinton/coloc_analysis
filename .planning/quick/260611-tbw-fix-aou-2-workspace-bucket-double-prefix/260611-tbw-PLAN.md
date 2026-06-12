---
phase: quick-260611-tbw
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/notebooks/AOU-2_per_region_ld.ipynb
  - tests/m3/test_aou_ld_panel_local.py
autonomous: true
requirements: [GAP-C3]
tags: [aou, ld, notebook, bucket-prefix, regression]

must_haves:
  truths:
    - "AOU-2 cell 3 normalizes WORKSPACE_BUCKET to bare form via the existing _normalize_bucket helper and binds it to WB"
    - "AOU-2 cell 4 reads both cohort MTs from gs://{WB}/ld/... (single gs:// prefix, no double-prefix)"
    - "AOU-2 cell 6 builds OUT_BUCKET_AFR / OUT_BUCKET_EUR from gs://{WB}/ld/... (single gs:// prefix)"
    - "The notebook remains valid JSON / valid nbformat"
    - "pytest tests/m3/test_aou_ld_panel_local.py passes, including _normalize_bucket regression coverage"
  artifacts:
    - path: ".planning/notebooks/AOU-2_per_region_ld.ipynb"
      provides: "AOU-2 LD notebook with normalized bucket references in cells 3/4/6"
      contains: "_normalize_bucket"
    - path: "tests/m3/test_aou_ld_panel_local.py"
      provides: "_normalize_bucket regression tests (prefix-strip, bare passthrough, trailing-slash, idempotence)"
      contains: "test_normalize_bucket_strips_prefix"
  key_links:
    - from: ".planning/notebooks/AOU-2_per_region_ld.ipynb (cell 3)"
      to: "aou_ld_panel._normalize_bucket"
      via: "import + WB = _normalize_bucket(os.environ['WORKSPACE_BUCKET'])"
      pattern: "_normalize_bucket"
    - from: ".planning/notebooks/AOU-2_per_region_ld.ipynb (cells 4, 6)"
      to: "WB"
      via: "f-string gs://{WB}/ld/..."
      pattern: "gs://\\{WB\\}/ld/"
---

<objective>
Fix the latent WORKSPACE_BUCKET double-prefix bug in the AOU-2 per-region LD notebook (`.planning/notebooks/AOU-2_per_region_ld.ipynb`).

AoU ships `$WORKSPACE_BUCKET` already `gs://`-prefixed (and AOU-1's baked Cell-1a'' override sets the prefixed `gs://rw-migration-aou-rw-476cdac2`). AOU-2's cell-3/4/6 f-strings do `f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/..."`, producing malformed `gs://gs://.../ld/...` URIs — every read (cell 4) and write (cell 6) path is wrong. The fix reuses the panel's own `_normalize_bucket` helper (the exact pattern the CLI uses at `aou_ld_panel.py:2474`) so the f-strings prepend the protocol exactly once. This closes documented "gap C3" (AOU-2 does not pin/normalize WORKSPACE_BUCKET) before the Wave 2 LD fire.

Purpose: prevent a guaranteed path failure on the first AOU-2 fire — every cohort read and every .npz/BlockMatrix write would target a double-prefixed URI.
Output: corrected notebook (3 cells) + confirmed/extended regression coverage for `_normalize_bucket`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@CLAUDE.md
@.planning/notebooks/AOU-2_per_region_ld.ipynb
@src/python/aou_ld_panel.py
@tests/m3/test_aou_ld_panel_local.py

<interfaces>
<!-- The reusable helper this fix wires in. Form-agnostic: handles prefixed,
     bare, trailing-slash, and gs:/// inputs. Pure function, no validation. -->

From src/python/aou_ld_panel.py:405-433:
```python
def _normalize_bucket(bucket: str) -> str:
    """Normalize a bucket reference to bare-name form.
    AoU's $WORKSPACE_BUCKET includes the gs:// protocol prefix; URI builders
    assume bare form. Strips an optional gs:// prefix and leading/trailing slashes."""
    return bucket.removeprefix("gs://").strip("/")
```

Canonical caller pattern this fix mirrors (aou_ld_panel.py:2474-2476):
```python
ws = _normalize_bucket(_require_env("WORKSPACE_BUCKET"))
out_bucket = f"gs://{ws}/ld/{anc_upper}_aou"
```

AOU-2 cell-3 current import line (extend in place):
```python
from aou_ld_panel import init_hail, compute_region_ld, MAF_THRESHOLD_EXPORT, read_final_cohort_mt
```
</interfaces>

<prior_work>
The `_normalize_bucket` regression suite ALREADY EXISTS in tests/m3/test_aou_ld_panel_local.py
(lines 279-324, from the 2026-05-14 m3-W1-bucket-prefix-defensive quick task):
- test_normalize_bucket_strips_prefix  (gs://X -> X)
- test_normalize_bucket_keeps_bare     (X -> X)
- test_normalize_bucket_strips_trailing_slash  (X/ and gs://X/ -> X)
- test_normalize_bucket_idempotent     (f(f(x)) == f(x))
- test_normalize_bucket_handles_malformed_extra_slash  (gs:///X -> X)

These already satisfy every assertion the task asks for (a/b/c + trailing slash).
DO NOT duplicate them. Task 2 is CONFIRM-and-optionally-extend with an
AOU-2-specific guard, not a fresh suite.
</prior_work>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Normalize WORKSPACE_BUCKET in AOU-2 cells 3/4/6 (nbformat-preserving edit)</name>
  <files>.planning/notebooks/AOU-2_per_region_ld.ipynb</files>
  <action>
Edit the notebook using a small nbformat-preserving Python snippet (nbformat 5.10.4 is
available at /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python). Read the
notebook with nbformat.read(..., as_version=4), mutate ONLY the three code cells below
by string-replacing their source, then nbformat.write back. Do NOT touch any other cell.
Do NOT bump execution_count or alter outputs (these are dev-fire cells; leave their
existing execution_count/outputs as-is — only the `source` field changes).

Identify the three target code cells by a unique substring of their current source
(robust to cell-index drift; do NOT rely on positional index):

1. CELL 3 (import + init): the cell whose source contains
   `from aou_ld_panel import init_hail, compute_region_ld, MAF_THRESHOLD_EXPORT, read_final_cohort_mt`
   - Add `_normalize_bucket` to that import line:
     `from aou_ld_panel import init_hail, compute_region_ld, MAF_THRESHOLD_EXPORT, read_final_cohort_mt, _normalize_bucket`
   - Immediately AFTER the `init_hail()` line, insert exactly one new line:
     `WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"])  # gap C3: AoU $WORKSPACE_BUCKET is gs://-prefixed; normalize to bare so the f-strings below don't double-prefix`

2. CELL 4 (cohort reads): the cell whose source contains `mt_afr = read_final_cohort_mt(`
   - Change the two reads from `f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_afr_qc.mt"`
     and `...mt_eur_qc.mt"` to:
     `mt_afr = read_final_cohort_mt(f"gs://{WB}/ld/mt_afr_qc.mt")`
     `mt_eur = read_final_cohort_mt(f"gs://{WB}/ld/mt_eur_qc.mt")`
   - Leave the print() line unchanged.

3. CELL 6 (output buckets): the cell whose source contains `OUT_BUCKET_AFR = `
   - Change to:
     `OUT_BUCKET_AFR = f"gs://{WB}/ld/AFR_aou"`
     `OUT_BUCKET_EUR = f"gs://{WB}/ld/EUR_aou"`
   - Leave the rest of cell 6 (the loop, log write) unchanged.

Use exact-string replacement (assert the old substring is present before replacing; raise
if a target is not found exactly once, so a silent no-op can't slip through). The Workbench
clean/smudge filter is Workbench-side only and does NOT apply on this HPC repo, so a normal
nbformat write is fine. Do NOT run the notebook (VPC-SC walls all AoU data ops from this HPC node).
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import nbformat,sys; nb=nbformat.read('.planning/notebooks/AOU-2_per_region_ld.ipynb',as_version=4); src=chr(10).join(c.source for c in nb.cells); assert 'read_final_cohort_mt, _normalize_bucket' in src, 'import not extended'; assert 'WB = _normalize_bucket(os.environ[' in src, 'WB binding missing'; assert src.count('f\"gs://{WB}/ld/') >= 4, 'WB f-strings missing (need cell4 x2 + cell6 x2)'; assert 'gs://{os.environ[' not in src, 'old double-prefix f-string still present'; nbformat.validate(nb); print('NOTEBOOK OK')"</automated>
  </verify>
  <done>Notebook is valid nbformat; cell 3 imports + binds WB; cells 4 and 6 use `gs://{WB}/ld/...` (4 occurrences); zero remaining `gs://{os.environ[...]` double-prefix f-strings; no other cell changed.</done>
</task>

<task type="auto">
  <name>Task 2: Confirm/extend _normalize_bucket regression coverage and run the suite</name>
  <files>tests/m3/test_aou_ld_panel_local.py</files>
  <action>
The `_normalize_bucket` regression tests ALREADY EXIST (lines 279-324: strips_prefix,
keeps_bare, strips_trailing_slash, idempotent, handles_malformed_extra_slash). They cover
every assertion the task requested. DO NOT duplicate them.

Add ONE focused AOU-2-specific guard test that asserts the production bucket value used by
AOU-1's baked override normalizes correctly and round-trips into a single-prefix URI — this
ties the test suite to the exact value that surfaced the bug. Append after the existing
`test_normalize_bucket_handles_malformed_extra_slash` block:

```python
def test_normalize_bucket_aou2_production_value_single_prefix():
    """REGRESSION GUARD (gap C3, 260611-tbw): AOU-2 cells 3/4/6 build cohort-read and
    LD-output URIs from $WORKSPACE_BUCKET, which AoU (and AOU-1's baked Cell-1a'' override)
    ship as the gs://-prefixed 'gs://rw-migration-aou-rw-476cdac2'. Normalizing then
    re-prefixing must yield a SINGLE gs:// (not the gs://gs://.../ld/... double-prefix the
    notebook produced before this fix)."""
    from aou_ld_panel import _normalize_bucket
    wb = _normalize_bucket("gs://rw-migration-aou-rw-476cdac2")
    assert wb == "rw-migration-aou-rw-476cdac2"
    uri = f"gs://{wb}/ld/mt_afr_qc.mt"
    assert uri == "gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt"
    assert uri.count("gs://") == 1
```

Then run the suite with the project python. Note: the module top-level `importorskip("hail")`
gates only the hail-dependent tests; the `_normalize_bucket` tests are pure-python and run
regardless. Run from the repo root.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_aou_ld_panel_local.py -k normalize_bucket -v 2>&1 | tail -20</automated>
  </verify>
  <done>The new `test_normalize_bucket_aou2_production_value_single_prefix` plus the five pre-existing `_normalize_bucket` tests all pass (6 passed); no test duplication introduced.</done>
</task>

</tasks>

<verification>
- Notebook is valid nbformat (`nbformat.validate`) and only cells 3/4/6 changed.
- No `gs://{os.environ[...]}` double-prefix f-string remains anywhere in the notebook.
- `_normalize_bucket` regression suite (existing 5 + new AOU-2 guard) passes under the project python.
- Notebook NOT executed (VPC-SC; HPC node has no AoU data access) — by design.
</verification>

<success_criteria>
- AOU-2 cells 3/4/6 produce single-prefix `gs://rw-migration-aou-rw-476cdac2/ld/...` URIs (no double-prefix), via the shared `_normalize_bucket` helper — matching the panel CLI pattern at `aou_ld_panel.py:2474`.
- `pytest tests/m3/test_aou_ld_panel_local.py -k normalize_bucket` passes.
- Gap C3 (AOU-2 forgot to normalize WORKSPACE_BUCKET) closed before the Wave 2 LD fire.
- Git staging uses explicit paths only (no `git add -A` on this GPFS tree).
</success_criteria>

<output>
After completion, create `.planning/quick/260611-tbw-fix-aou-2-workspace-bucket-double-prefix/260611-tbw-SUMMARY.md`.

Commit with explicit paths only:
`git add .planning/notebooks/AOU-2_per_region_ld.ipynb tests/m3/test_aou_ld_panel_local.py`
then commit: `fix(aou-2): normalize WORKSPACE_BUCKET to close gs://gs:// double-prefix (gap C3)`
</output>
