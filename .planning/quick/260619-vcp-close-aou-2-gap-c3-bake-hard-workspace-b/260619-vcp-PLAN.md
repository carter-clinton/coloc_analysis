---
phase: quick-260619-vcp
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/notebooks/AOU-2_per_region_ld.ipynb
  - tests/m3/test_aou_ld_panel_local.py
autonomous: true
requirements: [AOU-2-GAP-C3]
subsystem: m3-aou-ld-panel-build
tags: [aou, dataproc, hail, notebook, env-guards, workspace-bucket, nbformat, tdd]

must_haves:
  truths:
    - "A fresh AoU clone of AOU-2_per_region_ld.ipynb self-pins WORKSPACE_BUCKET to the canonical bucket BEFORE the bucket is read, so every Cell [6] MT read + Cell [8] LD write resolves to gs://rw-migration-aou-rw-476cdac2 (not the cloned-mybucket 404 placeholder)."
    - "If the bind is still polluted, the pin cell hard-fails IN-KERNEL (assert) instead of silently writing to the dead bucket (the empty-output catastrophe class)."
    - "A guard test FAILS before the notebook edit (RED) and PASSES after (GREEN), pinning both the hard-assign literal and the pin-before-read ordering."
  artifacts:
    - path: ".planning/notebooks/AOU-2_per_region_ld.ipynb"
      provides: "New WORKSPACE_BUCKET hard-override code cell between the Q-RS2 executor-config cell and the imports/_normalize_bucket cell"
      contains: 'os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"'
    - path: "tests/m3/test_aou_ld_panel_local.py"
      provides: "Notebook-loading guard test for the AOU-2 gap-C3 pin (hard-assign + pin-before-read ordering + cloned-mybucket assert)"
      contains: "def test_aou2_workspace_bucket_hard_pin"
  key_links:
    - from: ".planning/notebooks/AOU-2_per_region_ld.ipynb pin cell"
      to: "Cell [5] WB = _normalize_bucket(os.environ['WORKSPACE_BUCKET'])"
      via: "os.environ mutation that binds before the read (pin-cell index < read-cell index)"
      pattern: 'os\.environ\["WORKSPACE_BUCKET"\] = "gs://rw-migration-aou-rw-476cdac2"'
---

<objective>
Close AOU-2 gap C3 (SKILL.md "Baked-vs-manual edit table"): bake a HARD `WORKSPACE_BUCKET`
`os.environ` override into `.planning/notebooks/AOU-2_per_region_ld.ipynb` so a fresh AoU
clone self-pins the canonical bucket `gs://rw-migration-aou-rw-476cdac2` rather than the
`gs://cloned-mybucket-<project>` 404 placeholder a saved/duplicated Dataproc template injects.

Purpose: in a fresh/cloned AoU kernel the raw `$WORKSPACE_BUCKET` is the dead `cloned-mybucket`
placeholder. AOU-2 currently reads `WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"])`
(Cell [5]) with NO hard-set, so every Cell [8] LD `.npz`/`.bm` write and every Cell [6] MT read
would resolve to the dead bucket → lost writes / read-of-nothing (the empty-output catastrophe
class). AOU-1 already closed this in Cell 1a'' (quick 260606-qc1, commit 29d0a1f); AOU-2 is the
last open gap-C3 row. Carter chose to close it DURABLY (bake) rather than rely on a per-clone
manual pin.

Output: AOU-2 notebook gains a new pin cell (14 → 15 cells); a RED-first guard test in
tests/m3/test_aou_ld_panel_local.py.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.claude/skills/aou-ld-pipeline/SKILL.md

<!-- The AOU-1 Cell 1a'' HARD-override pattern to MIRROR (AOU-2-scoped: bucket only, NO WGS path). -->
<!-- From .planning/notebooks/AOU-1_template.ipynb, cell id e761fc87: -->
```python
# Cell 1a'' — env pins (HARD override; defeats saved-template 404 placeholder pollution).
# ... comment naming feedback_aou_cluster_template_bucket_pollution ...
import os
os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"
os.environ["WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"] = (
    "gs://vwb-aou-datasets-controlled/v8/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt"
)
print("WORKSPACE_BUCKET =", os.environ["WORKSPACE_BUCKET"])
```
<!-- AOU-2 scope: bucket ONLY. Do NOT set WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH — AOU-2 reads MTs, not the WGS multiMT. -->

<!-- AOU-2 raw-JSON facts (verified this session): nbformat 4.5; 14 cells; EVERY cell currently -->
<!-- LACKS an `id` field (the Read tool shows synthetic display ids that are NOT in the JSON). -->
<!-- Insert point: AFTER index 4 (code: `import os` + Q-RS2 PYSPARK_SUBMIT_ARGS) and -->
<!-- BEFORE index 5 (code: `import os, sys, pandas as pd, hail as hl` + -->
<!-- `WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"])`). The pin MUST bind before that read. -->

<!-- The precedent (quick 260606-qc1 / commit 29d0a1f) that baked AOU-1's identical guard: -->
<!-- edit via a one-off plain-`json` script (NOT nbformat.write — the Workbench clean/smudge filter -->
<!-- churns the whole file on nbformat.write). New cell gets a fresh 8-hex id + `metadata: {}`. -->
<!-- WATCH-OUT: AOU-1's baseline cells also lacked ids; 260606-qc1 had to backfill ids on the -->
<!-- pre-existing cells too or the clean/smudge filter re-dirties them (MissingIDFieldWarning). -->
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED — notebook guard test for the AOU-2 gap-C3 hard pin</name>
  <files>tests/m3/test_aou_ld_panel_local.py</files>
  <behavior>
    New test `test_aou2_workspace_bucket_hard_pin` that:
    - Loads `.planning/notebooks/AOU-2_per_region_ld.ipynb` via `json.load` (PROJECT_ROOT-relative;
      PROJECT_ROOT is already defined at module top). NO nbformat dependency — plain json + the
      existing `pathlib.Path`.
    - Builds a per-cell list of `(index, "".join(cell["source"]))` for `cell_type == "code"` cells.
    - (a) HARD-ASSIGN present: asserts SOME cell source contains the EXACT literal
      `os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"`. Record its index as `pin_idx`.
    - (a') NOT setdefault: asserts the pin cell does NOT contain a `.setdefault(` CALL on
      WORKSPACE_BUCKET — i.e. assert `'os.environ.setdefault("WORKSPACE_BUCKET"' not in pin_src`
      AND `"os.environ.setdefault('WORKSPACE_BUCKET'" not in pin_src`. (Substring `setdefault` may
      legitimately appear in an explanatory comment — match the CALL form, mirroring the 260606-qc1
      resolution where a crude `'setdefault' not in src` check was a planning-time imprecision.)
    - (b) PIN-BEFORE-READ ordering: find the index of the cell whose source contains
      `_normalize_bucket(os.environ["WORKSPACE_BUCKET"])` as `read_idx`; assert `pin_idx < read_idx`
      (STRICTLY less — the pin must bind before the bucket is read).
    - (c) PLACEHOLDER ASSERT present in the pin cell: assert the pin cell source contains the
      substring `cloned-mybucket` (the in-kernel guard that hard-fails a still-polluted bind).
    Test must read the notebook from disk each run (no caching) so it tracks the edit.
  </behavior>
  <action>
APPEND a new test function `test_aou2_workspace_bucket_hard_pin` to
`tests/m3/test_aou_ld_panel_local.py`. Place it near the other `_normalize_bucket` / gap-C3 tests
(e.g. just after `test_normalize_bucket_aou2_production_value_single_prefix` ~line 339), under a
short section comment block:
`# ----- AOU-2 notebook gap-C3 WORKSPACE_BUCKET hard-pin guard (260619-vcp) -----`.

There is currently NO test that loads the AOU-2 notebook JSON — this test ADDS that harness; do
NOT assume a loader exists. Use plain `json` (add `import json` at module top only if not already
imported — it is used elsewhere in the file as `_json`/`json`; reuse the existing import, do not
duplicate). Resolve the notebook as
`PROJECT_ROOT / ".planning" / "notebooks" / "AOU-2_per_region_ld.ipynb"`.

Assertion messages must be specific and name gap C3 + the pin-before-read contract so a future RED
is self-explanatory. Example skeleton (adapt, do not blindly paste):

```python
def test_aou2_workspace_bucket_hard_pin():
    """gap C3 (260619-vcp): AOU-2 must HARD-pin WORKSPACE_BUCKET to the canonical
    bucket BEFORE Cell [5] reads it, so a fresh AoU clone never writes to the
    gs://cloned-mybucket-<project> 404 placeholder (lost-writes catastrophe class).
    Mirrors AOU-1 Cell 1a'' (quick 260606-qc1). See feedback_aou_cluster_template_bucket_pollution."""
    import json
    nb_path = PROJECT_ROOT / ".planning" / "notebooks" / "AOU-2_per_region_ld.ipynb"
    nb = json.loads(nb_path.read_text())
    code_cells = [(i, "".join(c.get("source", [])))
                  for i, c in enumerate(nb["cells"]) if c.get("cell_type") == "code"]
    HARD = 'os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"'
    pins = [(i, s) for i, s in code_cells if HARD in s]
    assert pins, (
        "AOU-2 gap C3: no cell hard-assigns WORKSPACE_BUCKET to the canonical bucket "
        f"({HARD!r}). A fresh AoU clone would resolve $WORKSPACE_BUCKET to the "
        "gs://cloned-mybucket-<project> 404 placeholder -> lost writes."
    )
    pin_idx, pin_src = pins[0]
    assert 'os.environ.setdefault("WORKSPACE_BUCKET"' not in pin_src and \
           "os.environ.setdefault('WORKSPACE_BUCKET'" not in pin_src, (
        "WORKSPACE_BUCKET pin must be a HARD os.environ[...] = ... assignment, "
        "NOT setdefault (setdefault is unsafe — a polluted placeholder survives)."
    )
    reads = [i for i, s in code_cells
             if '_normalize_bucket(os.environ["WORKSPACE_BUCKET"])' in s]
    assert reads, "AOU-2 read cell (_normalize_bucket(os.environ[...])) not found"
    read_idx = reads[0]
    assert pin_idx < read_idx, (
        f"AOU-2 pin cell (index {pin_idx}) must come BEFORE the bucket-read cell "
        f"(index {read_idx}) — pin-before-read ordering; otherwise Cell [5] reads the "
        "un-pinned placeholder."
    )
    assert "cloned-mybucket" in pin_src, (
        "pin cell must include the cloned-mybucket no-placeholder assert so a "
        "still-polluted bind hard-fails in-kernel instead of silently writing to the dead bucket."
    )
```
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_aou_ld_panel_local.py::test_aou2_workspace_bucket_hard_pin -x -q</automated>
  </verify>
  <done>Test exists and FAILS (RED) against the un-edited 14-cell notebook — the failing assertion is the missing HARD-assign (pins == []). Commit RED: `test(260619-vcp): RED — AOU-2 gap-C3 WORKSPACE_BUCKET hard-pin guard`.</done>
</task>

<task type="auto">
  <name>Task 2: GREEN — bake the WORKSPACE_BUCKET hard-override cell into AOU-2 (surgical raw-JSON)</name>
  <files>.planning/notebooks/AOU-2_per_region_ld.ipynb</files>
  <action>
Insert ONE new code cell into `.planning/notebooks/AOU-2_per_region_ld.ipynb` via a one-off plain
`json` script (NOT nbformat.write — the Workbench clean/smudge filter churns the whole file on
nbformat.write; the 260606-qc1 precedent used plain `json`).

POSITION: AFTER index 4 (the `import os` + Q-RS2 `PYSPARK_SUBMIT_ARGS` executor-config cell) and
BEFORE index 5 (the `import os, sys, pandas as pd, hail as hl` + `WB = _normalize_bucket(...)`
cell). The new cell becomes index 5; the old index 5 shifts to 6, etc. Cell count 14 → 15.

NEW CELL CONTENT (mirror AOU-1 Cell 1a'' but AOU-2-scoped — bucket ONLY, NO WGS path). Source:

```python
# AOU-2 env pin (gap C3) — HARD WORKSPACE_BUCKET override; defeats saved-template 404 pollution.
# A fresh/cloned AoU Dataproc template can inject a dead gs://cloned-mybucket-<project> placeholder
# into $WORKSPACE_BUCKET. AOU-2's next cell reads WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"]);
# without this pin every Cell [8] LD .npz/.bm write + Cell [6] MT read would resolve to the dead
# bucket -> LOST WRITES (the empty-output catastrophe class). setdefault is UNSAFE (a polluted
# placeholder survives) -> hard-assign the verified canonical bucket. Scope: bucket ONLY (AOU-2 reads
# MTs, not the WGS multiMT, so do NOT set WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH here).
# Mirrors AOU-1 Cell 1a'' (quick 260606-qc1). See feedback_aou_cluster_template_bucket_pollution.
import os
os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"
print("WORKSPACE_BUCKET =", os.environ["WORKSPACE_BUCKET"])
assert "cloned-mybucket" not in os.environ["WORKSPACE_BUCKET"], (
    "WORKSPACE_BUCKET is still the cloned-mybucket 404 placeholder — the hard pin above "
    "did not take. HALT: every LD write/read would land in the dead bucket (lost outputs). "
    "Fix the bind before proceeding (see feedback_aou_cluster_template_bucket_pollution)."
)
```

CRITICAL nbformat-fidelity requirements (from the 260606-qc1 precedent):
- The NEW cell must carry a fresh 8-hex `id` (e.g. `uuid.uuid4().hex[:8]`) and `metadata: {}`,
  `cell_type: "code"`, `execution_count: null`, `outputs: []`.
- The `source` MUST be a list of strings split on newlines WITH the trailing `\n` on every line
  except the last (the nbformat convention; match how existing code cells store `source`).
- EVERY OTHER cell stays BYTE-IDENTICAL: do NOT touch any existing cell's `source`, `metadata`,
  `outputs`, or `execution_count`. The 14 existing cells currently have NO `id` field — leave them
  exactly as-is UNLESS the post-write working-tree check (below) shows the clean/smudge filter
  re-dirties them; only then backfill fresh 8-hex ids on the pre-existing id-less cells (the
  260606-qc1 Rule-3 fix) — id backfill only, never source/metadata.
- Preserve `nbformat` (4) and `nbformat_minor` (5) and any top-level `metadata`.
- Do NOT execute the notebook (VPC-SC; cannot run from NCSU — and the assert would need a live AoU
  env). This is a static content edit only.

After writing, re-parse the file as JSON to confirm: 15 cells; the new cell at index 5 with a fresh
8-hex id; index 4 and (old) index 5 sources unchanged; new cell index < the
`_normalize_bucket(os.environ["WORKSPACE_BUCKET"])` cell index.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_aou_ld_panel_local.py::test_aou2_workspace_bucket_hard_pin -x -q</automated>
  </verify>
  <done>The guard test from Task 1 now PASSES (GREEN). Notebook re-parses as valid nbformat 4.5 JSON with exactly 15 cells; the new pin cell (index 5) hard-assigns `gs://rw-migration-aou-rw-476cdac2`, prints it, and asserts `cloned-mybucket` absence; the pin index is strictly less than the `_normalize_bucket(os.environ[...])` read-cell index; all OTHER cell sources byte-identical to HEAD (verify with a `git show HEAD:.planning/notebooks/AOU-2_per_region_ld.ipynb` source diff). Working tree clean after edit (clean/smudge did not re-dirty). Commit GREEN: `feat(260619-vcp): GREEN — bake AOU-2 gap-C3 WORKSPACE_BUCKET hard pin`.</done>
</task>

<task type="auto">
  <name>Task 3: Full tests/m3 regression + explicit-path commit</name>
  <files>tests/m3/test_aou_ld_panel_local.py, .planning/notebooks/AOU-2_per_region_ld.ipynb</files>
  <action>
Run the FULL m3 suite to confirm no regression (the AOU-2 file baseline this session was 118
passed / 19 skipped; the full tests/m3 baseline is 204 passed / 0 failed / 30 skipped — the new
test adds +1 pass → expect 205 passed / 0 failed / 30 skipped, give or take environment-skips).

```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q
```

Confirm 0 failures and the new `test_aou2_workspace_bucket_hard_pin` is among the passes.

COMMIT DISCIPLINE (GPFS — see CLAUDE.md + feedback_multi_terminal_staging):
- EXPLICIT-PATH `git add` ONLY. Stage EXACTLY these two paths:
  `git add .planning/notebooks/AOU-2_per_region_ld.ipynb tests/m3/test_aou_ld_panel_local.py`
- NEVER `git add -A` / `git add .` — the working tree has pre-existing clutter that MUST NOT be
  staged: `.claude/settings.json`, `tests/m3/sparse_parent_benchmark.tsv` (pre-modified),
  `results_lsweep_*`, `targeted_rerun_*`, `.planning/phases/ta-sh2b3-.../wave4_*.json`,
  `.planning/quick/260429-*`, `.planning/quick/260501-*`, `.planning/quick/260502-*`,
  `results/track_a_aggregations/phase5_overview.tsv`.
- If Tasks 1 and 2 were committed separately (RED then GREEN), this task's commit is just the
  STATE.md / planning-doc refresh + the full-suite confirmation; if RED+GREEN were not yet
  committed, stage the two paths and commit them now. Keep the RED-before-GREEN history if feasible
  (two commits), but a single squashed `feat(260619-vcp)` commit is acceptable if the RED commit
  was skipped.
- Run on branch `m3-W2-aou-deltas` (current). Do NOT branch, do NOT push (the orchestrator pushes —
  see post-task note).
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q 2>&1 | tail -3</automated>
  </verify>
  <done>Full tests/m3 reports 0 failures and includes the new pass; both edited files committed to `m3-W2-aou-deltas` via explicit-path `git add` (no clutter staged, no `-A`); working tree shows only the pre-existing unrelated untracked/modified clutter (no accidental staging).</done>
</task>

</tasks>

<verification>
- `pytest tests/m3/test_aou_ld_panel_local.py::test_aou2_workspace_bucket_hard_pin` FAILS before the
  notebook edit (RED) and PASSES after (GREEN).
- AOU-2 notebook: 15 cells; new pin cell at index 5 with a fresh 8-hex id; hard-assign literal
  `gs://rw-migration-aou-rw-476cdac2`; `cloned-mybucket` assert present; pin-before-read ordering.
- All other AOU-2 cells byte-identical to HEAD (source diff via `git show HEAD:...`).
- Full tests/m3: 0 failures (expect ~205 passed / 30 skipped).
- Commit on `m3-W2-aou-deltas`, explicit-path staging only, no clutter, no push.
</verification>

<success_criteria>
- gap C3 closed for AOU-2: a fresh AoU clone of AOU-2_per_region_ld.ipynb self-pins
  `WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2` BEFORE the bucket is read, with an in-kernel
  `cloned-mybucket` assert as the loud failure guard.
- RED-first guard test pins the hard-assign literal, the not-setdefault contract, the
  pin-before-read ordering, and the placeholder assert.
- No regression (full tests/m3 green); notebook not executed; GPFS commit discipline honored.
</success_criteria>

<post_task_orchestrator>
IMPORTANT — after the executor commits, the ORCHESTRATOR (not the executor) MUST `git push` to
origin so the AoU Workbench `git clone` target picks up the baked pin. origin =
https://github.com/carter-clinton/coloc_analysis ; the AoU Workbench clones this repo for the
Wave 2 / Wave 4 fires (memory: project_repo_url + reference_aou_rw2_mirror_vpcsc). The default
branch is already `m3-W2-aou-deltas` (SKILL.md branch trap — flipped 2026-06-11), so a fresh clone
lands on the working line and gets the new cell. The executor does NOT push; the orchestrator does.
Also update SKILL.md's "Baked-vs-manual edit table" gap-C3 row from "GAP (manual) ⚠️" to
"BAKED" + commit sha (orchestrator or a follow-up quick — call out, do not silently leave the table
stale).
</post_task_orchestrator>

<output>
After completion, create `.planning/quick/260619-vcp-close-aou-2-gap-c3-bake-hard-workspace-b/260619-vcp-SUMMARY.md`
</output>
