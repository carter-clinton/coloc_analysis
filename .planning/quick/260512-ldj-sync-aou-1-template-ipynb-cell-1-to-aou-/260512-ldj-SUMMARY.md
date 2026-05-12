---
phase: quick-260512-ldj
plan: 01
subsystem: m3-aou-afr-ld-panel-build / notebooks-reference-template
tags:
  - audit-driven-re-analysis
  - stale-template-sync
  - aou-yarn
  - pyspark-submit-args
  - hl-init
  - m3-w1
  - reproducibility
  - reviewer-audit-trail
requirements_completed:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
dependency_graph:
  requires:
    - 36e8062  # m3-W1-checkpoint-suffix (quick 260512-jd9; _qc_checkpoint_uri helper that Cell 1b imports)
    - 8cc6f64  # m3-W2 naive_coalesce(2048) (DEC-2026-05-04-01 v8 partition-explosion OOM remediation; pairs with Cell 1a cores=1 lever)
  provides:
    - "AOU-1_template.ipynb (NCSU canonical reference) reproducibility — out-of-box AoU-working init pattern for future re-fires / reviewer audit"
  affects:
    - .planning/notebooks/AOU-1_template.ipynb  # 8 cells -> 9 cells (cell[1] split into Cell 1a + Cell 1b; cell[0] markdown appended)
    - .planning/STATE.md                        # frontmatter last_updated + Session Continuity follow-on paragraph
tech_stack:
  added: []  # no new deps; pure-stdlib import os in Cell 1a; existing hail import in Cell 1b
  patterns:
    - "PYSPARK_SUBMIT_ARGS env-var injection BEFORE pyspark/hail import — spark-submit-boundary conf precedence beats AoU YARN's cluster-locked spark-defaults.conf"
    - "Direct hl.init() (NOT through init_hail wrapper) with belt-and-suspenders spark_conf dict for portability"
    - "Pre-compute cores=='1' binding-verification assert with restart-kernel guidance — halts before any executor allocation if lever stops working"
    - "Python helper script for .ipynb JSON edit (pre/post-state asserts + round-trip JSON validation) over hand-edit of brittle JSON escape sequences"
key_files:
  created:
    - /tmp/sync_aou1_cell1.py  # ephemeral helper; verbatim source preserved in Appendix below for reproducibility
  modified:
    - .planning/notebooks/AOU-1_template.ipynb
    - .planning/STATE.md
decisions:
  - "Edit via Python helper script with pre/post-state asserts, NOT hand-edit of the brittle JSON escape sequences (Jupyter cell source arrays); helper aborts cleanly if re-run against an already-patched file (8-cells pre-state assertion fails)"
  - "Cell 1b imports _qc_checkpoint_uri and prints AFR primary / AFR sensitivity / EUR parity URIs to confirm commit 36e8062 (quick 260512-jd9) is live in the AoU clone BEFORE Cell 3+ fire — belt-and-suspenders patch verification beyond the cores==1 assert"
  - "cell[0] markdown title received the sync-note paragraph (NOT a separate new markdown cell) — keeps the title block + provenance + init-pattern rationale in a single header for reviewer audit trail"
  - "Single atomic commit covers .ipynb + STATE.md per [[feedback_state_md_keep_current]]; SUMMARY.md / PLAN.md commit deferred to orchestrator Step 8"
metrics:
  duration_minutes: ~15
  files_changed: 2
  cells_pre_sync: 8
  cells_post_sync: 9
  net_cells_added: 1
  commit_hash: 5389a88
  pushed_to_origin: true
completed_date: 2026-05-12
---

# Quick 260512-ldj: Sync AOU-1_template.ipynb Cell 1 to AoU YARN init pattern — Summary

NCSU canonical reference template `.planning/notebooks/AOU-1_template.ipynb` Cell 1 synced from a stale `init_hail()` wrapper-routed `spark_conf=dict` invocation (silently dropped by AoU's Dataproc + YARN cluster) to the empirically-confirmed-working `PYSPARK_SUBMIT_ARGS` env-var injection lever + direct `hl.init` call with `cores == '1'` binding-verification assert. Audit-driven re-analysis closeout deliverable; reviewer / future-Carter consuming this .ipynb will now get the AoU-working init pattern out-of-box.

## Bug Surface

**Stale producer (NCSU template) ↔ working consumer (AoU live notebook) drift.**

Per the `feedback_aou_dataproc_pyspark_submit_args` memory baked earlier this session (2026-05-12): on AoU's Dataproc + YARN cluster (driver hostname pattern `all-of-us-*.us-central1-a.c.terra-vpc-sc-*.internal`), `hl.init(spark_conf={"spark.executor.cores": "1"})` does NOT override the cluster's `spark-defaults.conf` — Hail's dict-supplied Spark conf gets silently dropped/ignored for executor-allocation properties like `spark.executor.cores` and `spark.executor.memory`. The working lever is `PYSPARK_SUBMIT_ARGS="--conf spark.executor.cores=1 pyspark-shell"` set BEFORE any pyspark or hail import (via `os.environ[...]` in a notebook cell that fires first). This injects the conf at the spark-submit boundary, which beats spark-defaults.conf in Spark's config precedence order.

The pre-sync Cell 1 of the NCSU reference template called `init_hail(spark_conf={"spark.executor.cores": "1"})` (the wrapper at `src/python/aou_ld_panel.py:121-143` — whose `spark_conf` forwarding is internally correct, but downstream-broken on AoU YARN). Re-firing this template on AoU as-is would have hit the same RegionPool OOM at v8's ~290k partition count that DEC-2026-05-04-01 was meant to remediate. The AoU-side live notebook already had the working pattern patched in manually earlier this session; this sync brings the NCSU canonical reference into alignment so future re-fires / reviewer reproduction start from a known-good init layer.

**NOT blocker-clearing for the current session** — Carter's AoU-side notebook is already running with the working pattern (Cell 3 primary AFR fire started 2026-05-12T17:21:28Z on AoU Dataproc). This sync is reproducibility / future re-fires / reviewer audit trail.

## Cell-Count Delta

| Phase | cell[0] | cell[1] | cell[2] | cell[3] | cell[4] | cell[5] | cell[6] | cell[7] | cell[8] | Total |
|-------|---------|---------|---------|---------|---------|---------|---------|---------|---------|-------|
| Pre-sync (8 cells) | md (title + provenance) | code (stale `init_hail()`) | code (Cell 3 Primary AFR) | code (Cell 4 AFR sensitivity) | code (Cell 5 EUR parity) | code (Cell 6 disjoint check) | code (Cell 7 cohort summary TSV) | md (closing notes) | — | 8 |
| Post-sync (9 cells) | md (title + provenance + APPENDED sync-note paragraph) | code (Cell 1a: `PYSPARK_SUBMIT_ARGS` injection) | code (Cell 1b: direct `hl.init` + cores=='1' assert + `_qc_checkpoint_uri` patch-verify) | code (Cell 3 Primary AFR — UNCHANGED) | code (Cell 4 AFR sensitivity — UNCHANGED) | code (Cell 5 EUR parity — UNCHANGED) | code (Cell 6 disjoint check — UNCHANGED) | code (Cell 7 cohort summary TSV — UNCHANGED) | md (closing notes — UNCHANGED) | 9 |

Net delta: **1 cell deleted (old cell[1] stale init_hail), 2 cells inserted (new Cell 1a + Cell 1b), net +1**. Cells 3-8 (formerly 2-7) byte-identical to pre-sync state.

## Edit Strategy

Python helper script `/tmp/sync_aou1_cell1.py` rather than hand-edit of the brittle JSON escape sequences in Jupyter cell `source` arrays. The script:

1. Loads `.planning/notebooks/AOU-1_template.ipynb` via `json.load`.
2. **Pre-state asserts** (abort cleanly if violated, leaving .ipynb untouched):
   - `len(nb['cells']) == 8` (refuses to double-apply against an already-patched file).
   - `nb['cells'][1]['cell_type'] == 'code'`.
   - `'init_hail()' in ''.join(nb['cells'][1]['source'])` (confirms target-cell identity before edit).
3. Constructs Cell 1a + Cell 1b as new code-cell dicts (matching the schema of the existing cells: `cell_type`, `execution_count`, `metadata`, `outputs`, `source` as list of `\n`-terminated lines per Jupyter convention).
4. Appends the sync-note paragraph to `nb['cells'][0]['source']` (markdown title cell).
5. Replaces `nb['cells'][1]` with `[cell_1a, cell_1b]` via list slice assignment: `nb['cells'][1:2] = [cell_1a, cell_1b]`.
6. **Post-state asserts**:
   - `len(nb['cells']) == 9`.
   - `'PYSPARK_SUBMIT_ARGS' in cell[1].source`.
   - `'spark.executor.cores=1' in cell[1].source` (env-var --conf flag).
   - `'hl.init(' in cell[2].source`.
   - `'spark.executor.cores' in cell[2].source` (spark_conf dict key).
   - `'assert cores' in cell[2].source` (binding-verification assert).
   - `'_qc_checkpoint_uri' in cell[2].source` (commit 36e8062 patch verification).
   - `'feedback_aou_dataproc_pyspark_submit_args' in cell[0].source` (sync-note memory cross-ref).
   - `'init_hail()' not in json.dumps(nb)` (old wrapper-routed call fully removed).
7. Writes back with `json.dump(nb, f, indent=1, ensure_ascii=False)` + trailing newline (Jupyter `indent=1` convention; `ensure_ascii=False` preserves em-dashes in the existing cells' source).
8. Re-loads the written file and re-asserts cell count (round-trip JSON validation).

The pre/post-state asserts gate the write — any unexpected state aborts before writing.

## Verification Evidence

All structural greps and JSON validity checks PASS:

| Check | Expected | Actual |
|-------|----------|--------|
| `json.load` cell count | 9 | 9 |
| `grep -c "PYSPARK_SUBMIT_ARGS"` | >= 1 | 7 |
| `grep -c "spark.executor.cores"` | >= 2 | 5 |
| `grep -c "_qc_checkpoint_uri"` | >= 1 | 6 |
| `grep -c "init_hail()"` | == 0 | 0 |
| `grep -c "feedback_aou_dataproc_pyspark_submit_args"` | >= 2 | 2 |
| `grep -c "hl.init("` | >= 1 | 3 |
| `grep -c "load_qc_cohort"` | >= 4 | 6 |
| `grep -c "len(overlap) == 0"` | >= 1 | 1 (RESEARCH O5 regression guard) |
| `python3 -c "import json; json.load(open('.planning/notebooks/AOU-1_template.ipynb'))"` | exit 0 | exit 0 |

**PLAN-vs-reality anomaly (1, in-spec):** PLAN.md `<verification>` item #6 expected `grep -c "naive_coalesce(2048)" == 0`. Actual count = 2 (cited in Cell 1a comment AND Cell 1b comment as part of the pairing-explanation cross-reference per the canonical pattern memory + PLAN.md `<patch_design>` source bodies which contain the literal text). The cited references are pattern documentation, not invocations (the actual `naive_coalesce(2048)` call lives in `aou_ld_panel.py:218` and fires inside `load_qc_cohort`). Both cell source bodies were taken verbatim from PLAN.md per its `Cell 1a + Cell 1b source — VERBATIM from PLAN.md <patch_design>` directive. The cross-reference comments are reviewer-friendly and reviewer-defensible; substantively load-bearing checks all hold.

## Commit + Push

**Commit:** `5389a88dddacd84e8f4ad22a58fa3d00a117031e`

**Subject:** `feat(m3-W1-template-pyspark-submit-args-sync): NCSU AOU-1 template synced to AoU-working init pattern — audit-driven re-analysis`

**Stat:**
```
 .planning/STATE.md                       |  4 +-
 .planning/notebooks/AOU-1_template.ipynb | 90 ++++++++++++++++++++++++++++----
 2 files changed, 82 insertions(+), 12 deletions(-)
```

**Push:** `d7a221a..5389a88  main -> main` (origin/main).

**Post-push verify:** `git log origin/main..HEAD` returns empty (push confirmed clean).

**Multi-terminal staging compliance:** Staged via explicit `git add .planning/notebooks/AOU-1_template.ipynb .planning/STATE.md` per [[feedback_multi_terminal_staging]] — zero collision with the 13+ untracked files in other terminals (`.claude/settings.json` drift / `.planning/config.json` drift / W4 supervisor orphan tracker / 260429-utt bjobs.tsv / 260501-wdn aggregator dir / 260502-lsk PLAN.md / results/track_a_aggregations/phase5_overview.tsv / 6 lsweep backup dirs / targeted_rerun_* dirs all UNTOUCHED).

**Honest-framing-lock gate:** Commit subject + body use "audit-driven re-analysis" / "stale-template sync" framing per [[feedback_original_research_framing]]. Forbidden-token grep on commit message returns 0 hits for `cleanup` / `revision` / `salvage` / "fix the wrapper". (The word "fix" appears in `fix_*` / Pitfall references inside file paths quoted in the body, not as the action verb; commit-subject Conventional-Commits prefix is `feat()`, not `fix()`.)

## Cross-References

| Anchor | Tag | Role |
|--------|-----|------|
| `36e8062` | m3-W1-checkpoint-suffix (quick 260512-jd9) | Predecessor — extracted `_qc_checkpoint_uri` helper that Cell 1b imports + prints to verify patch is live in AoU clone before Cell 3+ fires |
| `8cc6f64` | m3-W2 naive_coalesce(2048) | DEC-2026-05-04-01 v8 partition-explosion OOM remediation; pairs with Cell 1a's `cores=1` PYSPARK_SUBMIT_ARGS lever to close the OOM end-to-end |
| `DEC-2026-05-04-01` | v8 OOM remediation decision | Originating decision driving the `spark.executor.cores=1` requirement; pre-sync Cell 1 had this in the wrapper-routed `init_hail()` call but the dict path was silently dropped on AoU YARN |

| Memory | Role |
|--------|------|
| `feedback_aou_dataproc_pyspark_submit_args` | Canonical pattern (Cell 1a + Cell 1b cell-paste-ready source); baked 2026-05-12 from the empirical confirmation earlier this session |
| `feedback_original_research_framing` | Commit body framing — "audit-driven re-analysis" / "stale-template sync"; NOT "fix" / "cleanup" / "revision" / "salvage" |
| `feedback_state_md_keep_current` | STATE.md atomic-commit refresh in same commit as the .ipynb edit |
| `feedback_multi_terminal_staging` | Explicit `git add` paths; never `git add .` / `-A` on GPFS shared tree |
| `feedback_extract_reusable_utilities` | Predecessor 260512-jd9 applied this pattern; this task does NOT extract a new utility (template-sync is not a code-bug class — it's an audit-trail sync) |
| `feedback_rigor_over_speed` | Pre/post-state asserts in the helper script + round-trip JSON validation + binding-verification assert in Cell 1b are all the "halt and verify" pattern rather than "trust and proceed" |

## Carter Next-Action

**None required for this task** — Carter's AoU-side notebook is already running with the working pattern this session. Future re-fires or reviewer reproductions of M3 Wave 1 (anyone running `git clone` + opening `.planning/notebooks/AOU-1_template.ipynb`) will now get the AoU-working init pattern out-of-box.

**If Carter restarts the AoU-side notebook kernel for any reason this session**, the working pattern is already applied AoU-side; the NCSU sync does not affect the running session. If Carter pulls the latest NCSU commits into the AoU workspace (e.g., between Cell 3 and Cell 4 to pick up `36e8062`), this sync's commit `5389a88` will also land — and the AoU-side notebook's Cell 1 manually-patched contents will be overwritten by the canonical version, which is **identical in behavior** but with a more thorough patch-verification block (cell[2]'s `_qc_checkpoint_uri` print loop is new). No re-run required; the assertion guard means a stale-conf re-fire would halt cleanly.

## Self-Check: PASSED

- `.planning/notebooks/AOU-1_template.ipynb` exists; cell count = 9. **FOUND.**
- `.planning/STATE.md` updated (frontmatter `last_updated` advanced + Session Continuity follow-on paragraph). **FOUND.**
- Commit `5389a88` in `git log --oneline -5`. **FOUND.**
- `origin/main..HEAD` empty (push confirmed). **FOUND.**
- All 9 structural verification checks PASS (1 documented in-spec anomaly: `naive_coalesce(2048)` count = 2 due to canonical-pattern cross-reference comments in Cell 1a + Cell 1b source per PLAN.md verbatim spec).

---

## Appendix A — Helper Script Source (verbatim `/tmp/sync_aou1_cell1.py`)

```python
#!/usr/bin/env python3
"""
sync_aou1_cell1.py — Quick task 260512-ldj helper.

Loads .planning/notebooks/AOU-1_template.ipynb, asserts pre-state
(8 cells; cell[1] = stale init_hail() call), constructs Cell 1a
(PYSPARK_SUBMIT_ARGS injection) + Cell 1b (direct hl.init + cores=1
assert + _qc_checkpoint_uri patch verification), appends a sync-note
paragraph to cell[0] markdown, replaces cell[1] with [cell_1a, cell_1b]
via list slice assignment (8 -> 9 cells; old cell[1] deleted; 2 new
cells inserted; cells 2-7 untouched), asserts post-state, and writes
back with indent=1 (Jupyter convention) + ensure_ascii=False.

Per canonical pattern memory feedback_aou_dataproc_pyspark_submit_args
(baked 2026-05-12). Pairs with naive_coalesce(2048) in
aou_ld_panel.py:218 (DEC-2026-05-04-01; anchor commit 8cc6f64) to clear
v8 partition-explosion RegionPool OOM on AoU YARN.
"""
import json
import sys
from pathlib import Path

NB_PATH = Path(".planning/notebooks/AOU-1_template.ipynb")


# ---------------------------------------------------------------------------
# Cell sources (verbatim per PLAN.md <patch_design>)
# ---------------------------------------------------------------------------

CELL_1A_SOURCE = """# Cell 1a — Force Spark executor resources at the spark-submit boundary.
# CANONICAL PATTERN (per .planning/memory feedback_aou_dataproc_pyspark_submit_args
# baked 2026-05-12): on AoU's Dataproc + YARN cluster, hl.init(spark_conf=dict) is
# silently overridden by the cluster's spark-defaults.conf — the dict path doesn't
# beat YARN's executor-allocation policy. PYSPARK_SUBMIT_ARGS injected BEFORE any
# pyspark/hail import IS honored because it applies at the spark-submit boundary
# (highest Spark conf precedence).
#
# This cell MUST run before any other pyspark/hail import in the notebook.
# Pairs with naive_coalesce(2048) in aou_ld_panel.py:218 (DEC-2026-05-04-01
# v8 partition-explosion OOM remediation; anchor commit 8cc6f64).
import os
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--conf spark.executor.cores=1 "
    "--conf spark.executor.memory=5g "
    "--conf spark.driver.cores=1 "
    "pyspark-shell"
)
print("PYSPARK_SUBMIT_ARGS set:", os.environ["PYSPARK_SUBMIT_ARGS"])
"""

CELL_1B_SOURCE = """# Cell 1b — Initialize Hail with spark_conf threading + verify executor.cores=1.
# Calls hl.init directly (NOT through init_hail wrapper) because the wrapper's
# spark_conf path is known broken on AoU YARN; the PYSPARK_SUBMIT_ARGS lever
# from Cell 1a is what actually binds the conf. The spark_conf dict here is
# belt-and-suspenders for portability — preserves the conf-by-dict path for
# environments where it works (local Spark, standalone clusters), while AoU
# binds via the env-var lever.
import sys
sys.path.insert(0, "/home/jupyter/coloc_analysis/src/python")
import hail as hl
hl.init(
    default_reference="GRCh38",
    log="/tmp/hail.log",
    quiet=True,
    spark_conf={
        "spark.executor.cores": "1",
        "spark.executor.memory": "5g",
        "spark.driver.cores": "1",
    },
)
# Pull cohort helpers AFTER Hail backend is up (so any aou_ld_panel-side
# Hail-dependent imports succeed):
from aou_ld_panel import load_qc_cohort, ANCESTRY_FIELD, KING_KINSHIP_THRESHOLD, _qc_checkpoint_uri

# Verify the patches are live (cores=1 confirms PYSPARK_SUBMIT_ARGS bound;
# _qc_checkpoint_uri import confirms commit 36e8062 is in the AoU clone):
sc_conf = hl.spark_context().getConf()
cores = sc_conf.get('spark.executor.cores')
assert cores == '1', (
    f"PYSPARK_SUBMIT_ARGS lever did not bind — got cores={cores}, expected '1'. "
    f"DO NOT proceed to Cell 3+ — the v8 partition-explosion OOM config is NOT live. "
    f"Action: Kernel menu → Restart Kernel; then re-fire Cell 1a + Cell 1b."
)
print("=== HAIL INIT ===")
print(f"  Hail version          : {hl.__version__}")
print(f"  spark.executor.cores  : {cores}  OK")
print(f"  spark.executor.memory : {sc_conf.get('spark.executor.memory')}")
print(f"  spark.driver.cores    : {sc_conf.get('spark.driver.cores')}")
print(f"  spark.master          : {sc_conf.get('spark.master')}")
print()
print("=== ENV ===")
print(f"  WORKSPACE_BUCKET = {os.environ['WORKSPACE_BUCKET']}")
print(f"  GOOGLE_PROJECT   = {os.environ['GOOGLE_PROJECT']}")
print(f"  WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH = {os.environ['WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH']}")
print()
print("=== PATCH VERIFICATION (commit 36e8062 — m3-W1-checkpoint-suffix; quick 260512-jd9) ===")
print(f"  AFR primary URI     : {_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr', False)}")
print(f"  AFR sensitivity URI : {_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr', True)}")
print(f"  EUR parity URI      : {_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'eur', False)}")
"""

MARKDOWN_SYNC_NOTE = """

**Init pattern (per `feedback_aou_dataproc_pyspark_submit_args` memory, baked 2026-05-12):** Cell 1a sets `PYSPARK_SUBMIT_ARGS` before any pyspark/hail import — this is the only lever that honors `spark.executor.cores=1` on AoU YARN. Cell 1b calls `hl.init()` directly (bypassing the `init_hail` wrapper whose `spark_conf=dict` path is silently dropped on YARN). Together, they pair with `naive_coalesce(2048)` in `aou_ld_panel.py:218` to clear the v8 partition-explosion RegionPool OOM (DEC-2026-05-04-01). Patch-verification at end of Cell 1b: prints checkpoint URIs from `_qc_checkpoint_uri` (commit 36e8062 / quick 260512-jd9) to confirm both the cores=1 lever AND the distinct sensitivity/primary checkpoint paths are live before any compute fires.
"""


def source_to_lines(source_text: str) -> list:
    """Convert a Python source string into Jupyter cell source (list of \\n-terminated
    lines, last line WITHOUT trailing newline — matches Jupyter convention)."""
    lines = source_text.splitlines(keepends=True)
    # Strip trailing newline from final line per nbformat convention.
    if lines and lines[-1].endswith("\\n"):
        lines[-1] = lines[-1].rstrip("\\n")
    return lines


def make_code_cell(source_text: str) -> dict:
    """Build a code cell dict matching the schema used by the existing
    cells in AOU-1_template.ipynb (nbformat 4.5)."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_to_lines(source_text),
    }


def main() -> int:
    if not NB_PATH.exists():
        print(f"ERROR: {NB_PATH} does not exist", file=sys.stderr)
        return 2

    with NB_PATH.open() as f:
        nb = json.load(f)

    # --- Pre-state assertions ---
    assert len(nb["cells"]) == 8, (
        f"pre-state: expected 8 cells, got {len(nb['cells'])} "
        f"(template may already be patched — refusing to double-apply)"
    )
    assert nb["cells"][1]["cell_type"] == "code", (
        f"pre-state: expected cell[1] to be code, got {nb['cells'][1]['cell_type']}"
    )
    cell1_src = "".join(nb["cells"][1]["source"])
    assert "init_hail()" in cell1_src or "init_hail(" in cell1_src, (
        f"pre-state: expected cell[1] to contain init_hail() call; got:\\n{cell1_src[:200]}"
    )
    print(f"OK pre-state: 8 cells; cell[1] contains init_hail() call")

    # --- Build new cells ---
    cell_1a = make_code_cell(CELL_1A_SOURCE)
    cell_1b = make_code_cell(CELL_1B_SOURCE)

    # --- Append sync-note to cell[0] markdown ---
    md_src = nb["cells"][0]["source"]
    sync_lines = MARKDOWN_SYNC_NOTE.splitlines(keepends=True)
    if md_src and not md_src[-1].endswith("\\n"):
        md_src[-1] = md_src[-1] + "\\n"
    if sync_lines and sync_lines[-1].endswith("\\n"):
        sync_lines[-1] = sync_lines[-1].rstrip("\\n")
    md_src.extend(sync_lines)
    nb["cells"][0]["source"] = md_src

    # --- Replace cell[1] (single stale init_hail cell) with [cell_1a, cell_1b] ---
    nb["cells"][1:2] = [cell_1a, cell_1b]

    # --- Post-state assertions ---
    assert len(nb["cells"]) == 9
    new_1a = "".join(nb["cells"][1]["source"])
    new_1b = "".join(nb["cells"][2]["source"])
    assert "PYSPARK_SUBMIT_ARGS" in new_1a
    assert "spark.executor.cores=1" in new_1a
    assert "hl.init(" in new_1b
    assert "spark.executor.cores" in new_1b
    assert "assert cores" in new_1b
    assert "_qc_checkpoint_uri" in new_1b
    md_after = "".join(nb["cells"][0]["source"])
    assert "feedback_aou_dataproc_pyspark_submit_args" in md_after
    full_src = json.dumps(nb)
    assert "init_hail()" not in full_src
    print("OK post-state: 9 cells; Cell 1a (PYSPARK_SUBMIT_ARGS) + Cell 1b (hl.init + verify) + cell[0] markdown sync-note")

    # --- Write back (indent=1 = Jupyter convention; ensure_ascii=False preserves em-dashes) ---
    with NB_PATH.open("w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\\n")

    # --- Round-trip JSON validation ---
    with NB_PATH.open() as f:
        nb2 = json.load(f)
    assert len(nb2["cells"]) == 9
    print(f"OK round-trip: {NB_PATH} valid JSON, 9 cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Helper script execution log (2026-05-12T~19:25Z):**
```
OK pre-state: 8 cells; cell[1] contains init_hail() call
OK post-state: 9 cells; Cell 1a (PYSPARK_SUBMIT_ARGS) + Cell 1b (hl.init + verify) + cell[0] markdown sync-note
OK round-trip: .planning/notebooks/AOU-1_template.ipynb valid JSON, 9 cells
```
