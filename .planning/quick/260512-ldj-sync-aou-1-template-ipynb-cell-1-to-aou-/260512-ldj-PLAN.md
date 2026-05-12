---
phase: quick-260512-ldj
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/notebooks/AOU-1_template.ipynb
  - .planning/STATE.md
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION

must_haves:
  truths:
    - "AOU-1_template.ipynb Cell 1 (init_hail) is split into two cells: a Cell 1a that sets PYSPARK_SUBMIT_ARGS BEFORE any pyspark/hail import, and a Cell 1b that calls hl.init directly (NOT through the init_hail wrapper, whose spark_conf=dict path is silently dropped on AoU YARN per feedback_aou_dataproc_pyspark_submit_args memory baked 2026-05-12)."
    - "Cell 1a writes os.environ['PYSPARK_SUBMIT_ARGS'] with --conf spark.executor.cores=1 --conf spark.executor.memory=5g --conf spark.driver.cores=1 pyspark-shell — the lever that binds executor allocation at the spark-submit boundary, beating AoU's cluster-locked spark-defaults.conf."
    - "Cell 1b calls hl.init(default_reference='GRCh38', log='/tmp/hail.log', quiet=True, spark_conf={...}) with belt-and-suspenders dict-conf for portability to local/standalone Spark; pairs with naive_coalesce(2048) in aou_ld_panel.py:218 (DEC-2026-05-04-01 v8 partition-explosion OOM remediation; anchor commit 8cc6f64)."
    - "Cell 1b includes a binding-verification assert: sc_conf.get('spark.executor.cores') == '1' — if FAILS, raises AssertionError with restart-kernel guidance and halts before any compute cell fires."
    - "Cell 1b also verifies commit 36e8062 (m3-W1-checkpoint-suffix; quick 260512-jd9) is live by importing _qc_checkpoint_uri and printing AFR primary / AFR sensitivity / EUR parity checkpoint URIs (distinct paths confirm the suffix patch is in the AoU clone)."
    - "Cells 2-7 (existing primary AFR / sensitivity AFR / EUR parity / disjoint check / cohort summary / closing markdown) are NOT modified — the only producer/consumer drift was at the init layer, now closed."
    - "Total cell count goes from 8 → 9 (1 cell deleted from old layout, 2 cells inserted; net +1)."
    - "The opening markdown cell (cell[0]) is appended with a sync note explaining the Cell 1a/1b split rationale, citing the canonical pattern memory and the v8 OOM pairing — reviewer-friendly audit trail."
    - "Commit subject carries the (m3-W1-template-pyspark-submit-args-sync) token; body uses stale-template sync / audit-driven re-analysis framing per feedback_original_research_framing (NOT fix / cleanup / revision)."
    - "STATE.md is refreshed in the same atomic commit (per feedback_state_md_keep_current — don't defer atomic refresh)."
    - "Commit is pushed to origin/main (consistency with prior 260512-jd9 push pattern)."
  artifacts:
    - path: ".planning/notebooks/AOU-1_template.ipynb"
      provides: "Updated reference template with PYSPARK_SUBMIT_ARGS-injection Cell 1a + direct-hl.init+verify Cell 1b; Carter mirrors into AoU workspace for future re-fires / reviewer audit trail"
      contains: "PYSPARK_SUBMIT_ARGS"
      min_cells: 9
    - path: ".planning/STATE.md"
      provides: "Atomic refresh recording the template-sync as a closed quick task in the Quick Tasks table"
    - path: "/tmp/sync_aou1_cell1.py"
      provides: "Python helper script (loads .ipynb JSON, mutates cells list, writes back) documented in SUMMARY.md for reproducibility — preferred over hand-edit of brittle JSON escape sequences"
  key_links:
    - from: ".planning/notebooks/AOU-1_template.ipynb cell[1] (Cell 1a)"
      to: ".planning/notebooks/AOU-1_template.ipynb cell[2] (Cell 1b)"
      via: "os.environ[PYSPARK_SUBMIT_ARGS] set BEFORE Cell 1b's import hail as hl"
      pattern: "PYSPARK_SUBMIT_ARGS"
    - from: ".planning/notebooks/AOU-1_template.ipynb cell[2] (Cell 1b)"
      to: ".planning/notebooks/AOU-1_template.ipynb cell[3+] (cohort cells, formerly cell[2+])"
      via: "load_qc_cohort imported in Cell 1b after hl.init; consumed by primary AFR / sensitivity AFR / EUR parity cells"
      pattern: "load_qc_cohort"
    - from: ".planning/notebooks/AOU-1_template.ipynb cell[2] (Cell 1b assert)"
      to: "src/python/aou_ld_panel.py:218 naive_coalesce(2048)"
      via: "cores=1 binding verified BEFORE compute → pairs with naive_coalesce to clear v8 partition-explosion RegionPool OOM (DEC-2026-05-04-01)"
      pattern: "spark.executor.cores"
---

<objective>
Sync NCSU reference template `.planning/notebooks/AOU-1_template.ipynb` Cell 1 (init_hail) to the canonical AoU YARN init pattern empirically confirmed working 2026-05-12 and memorialized in the `feedback_aou_dataproc_pyspark_submit_args` memory. The current Cell 1 calls `init_hail()` (the wrapper whose `spark_conf=dict` path is silently dropped by AoU Dataproc + YARN), which would OOM the cluster's RegionPool at v8's ~290k partition count if naively re-fired. The fix is structural: split Cell 1 into a Cell 1a that sets `PYSPARK_SUBMIT_ARGS` BEFORE any pyspark/hail import (the only lever AoU YARN honors), and a Cell 1b that calls `hl.init` directly with belt-and-suspenders `spark_conf` dict + a binding-verification assert that halts before compute if `cores != 1`. Pairs with `naive_coalesce(2048)` in `aou_ld_panel.py:218` (DEC-2026-05-04-01) to close v8 OOM end-to-end.

Purpose: Reproducibility / future re-fires / reviewer audit trail. Carter's AoU-side notebook is already running with the working pattern in the current session; this sync brings the NCSU canonical template into alignment so the next re-fire (or any reviewer reproducing the analysis) starts from a known-good init layer. NOT time-pressured — this is stale-template sync, not blocker-clearing.

Output: Updated `.ipynb` (8 cells → 9 cells), STATE.md atomic refresh, single commit with `(m3-W1-template-pyspark-submit-args-sync)` token, pushed to origin/main.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/notebooks/AOU-1_template.ipynb
@.planning/phases/m3-aou-afr-ld-panel-build/m3-01-W1-aou-cohort-and-hard-gates-PLAN.md

<applicable_memory>
- feedback_aou_dataproc_pyspark_submit_args (canonical pattern; cell-paste-ready Cell 1a + Cell 1b structure) — APPLY VERBATIM
- feedback_original_research_framing (commit body framing — "audit-driven re-analysis" / "stale-template sync"; NOT "fix" / "cleanup" / "revision" / "salvage")
- feedback_state_md_keep_current (STATE.md atomic-commit refresh in same commit as the .ipynb edit)
- feedback_multi_terminal_staging (explicit `git add` paths; never `git add .` / `-A` on GPFS)
</applicable_memory>

<interfaces>
<!-- Current AOU-1_template.ipynb cell layout (HEAD d7a221a, verified 2026-05-12): -->

cell[0] (markdown) — title + provenance block
cell[1] (code)     — init_hail() call (THIS IS THE STALE CELL — to be split)
cell[2] (code)     — Cell 3 Primary AFR cohort (load_qc_cohort, ancestry=afr, sensitivity=False)
cell[3] (code)     — Cell 4 AFR sensitivity cohort (load_qc_cohort, ancestry=afr, sensitivity=True)
cell[4] (code)     — Cell 5 EUR parity cohort (load_qc_cohort, ancestry=eur, sensitivity=False)
cell[5] (code)     — Cell 6 Disjoint-cohort sanity check (assert overlap == 0)
cell[6] (code)     — Cell 7 Cohort-summary TSV
cell[7] (markdown) — closing notes

<!-- Post-sync target layout (9 cells): -->

cell[0] (markdown) — title + provenance block + APPENDED Cell 1a/1b rationale note
cell[1] (code)     — NEW Cell 1a: PYSPARK_SUBMIT_ARGS injection (BEFORE any pyspark/hail import)
cell[2] (code)     — NEW Cell 1b: hl.init direct call + spark_conf dict + cores=1 assert + _qc_checkpoint_uri patch verification
cell[3] (code)     — (was cell[2]) Cell 3 Primary AFR cohort — UNCHANGED
cell[4] (code)     — (was cell[3]) Cell 4 AFR sensitivity cohort — UNCHANGED
cell[5] (code)     — (was cell[4]) Cell 5 EUR parity cohort — UNCHANGED
cell[6] (code)     — (was cell[5]) Cell 6 Disjoint-cohort sanity check — UNCHANGED
cell[7] (code)     — (was cell[6]) Cell 7 Cohort-summary TSV — UNCHANGED
cell[8] (markdown) — (was cell[7]) closing notes — UNCHANGED

<!-- Helper imports the new Cell 1b consumes (already exported by Wave 0 driver per anchor commit 36e8062): -->

src/python/aou_ld_panel.py exports:
- load_qc_cohort(mt_path: str, ancestry: str, sensitivity: bool = False) -> hl.MatrixTable
- ANCESTRY_FIELD: str
- KING_KINSHIP_THRESHOLD: float
- _qc_checkpoint_uri(workspace_bucket: str, ancestry: str, sensitivity: bool) -> str   # commit 36e8062

<!-- Note: init_hail is NO LONGER imported in the new Cell 1b — Cell 1b calls hl.init directly, bypassing the wrapper. -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Split AOU-1_template.ipynb Cell 1 into Cell 1a (PYSPARK_SUBMIT_ARGS) + Cell 1b (hl.init direct + verify); append cell[0] markdown sync note; refresh STATE.md; commit + push</name>
  <files>.planning/notebooks/AOU-1_template.ipynb, .planning/STATE.md</files>
  <action>
    Write the updated `.ipynb` via a Python helper script (NOT a direct text-edit of the brittle JSON — escape sequences in Jupyter cell source arrays make hand-editing error-prone). Steps:

    **Step A — Write helper script to /tmp/sync_aou1_cell1.py:**

    The script:
    1. Loads `.planning/notebooks/AOU-1_template.ipynb` via `json.load`.
    2. Asserts current state: `len(nb['cells']) == 8` AND `nb['cells'][1]['cell_type'] == 'code'` AND `'init_hail()' in ''.join(nb['cells'][1]['source'])` (sanity guard against re-running against an already-patched file).
    3. Constructs Cell 1a as a new dict: `{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [...Cell 1a source as list of lines per Jupyter convention, each line ending with \n except the last...]}`.
    4. Constructs Cell 1b as a new dict with the same skeleton + Cell 1b source body.
    5. Appends a sync-note paragraph to `nb['cells'][0]['source']` (the title markdown). Append text:
       ```
       \n\n**Init pattern (per `feedback_aou_dataproc_pyspark_submit_args` memory, baked 2026-05-12):** Cell 1a sets `PYSPARK_SUBMIT_ARGS` before any pyspark/hail import — this is the only lever that honors `spark.executor.cores=1` on AoU YARN. Cell 1b calls `hl.init()` directly (bypassing the `init_hail` wrapper whose `spark_conf=dict` path is silently dropped on YARN). Together, they pair with `naive_coalesce(2048)` in `aou_ld_panel.py:218` to clear the v8 partition-explosion RegionPool OOM (DEC-2026-05-04-01). Patch-verification at end of Cell 1b: prints checkpoint URIs from `_qc_checkpoint_uri` (commit 36e8062 / quick 260512-jd9) to confirm both the cores=1 lever AND the distinct sensitivity/primary checkpoint paths are live before any compute fires.\n
       ```
       (Use Python triple-quoted-string + `.splitlines(keepends=True)` to produce a Jupyter-conformant list of `\n`-terminated lines; append to `cells[0]['source']`.)
    6. Builds new `cells` list: `[cells[0], cell_1a, cell_1b, cells[2], cells[3], cells[4], cells[5], cells[6], cells[7]]` (8 input cells → 9 output cells; old cell[1] deleted; two new cells inserted in its place; cells 2-7 unchanged).
    7. Writes back to `.planning/notebooks/AOU-1_template.ipynb` via `json.dump(nb, fp, indent=1, ensure_ascii=False)`. (`indent=1` matches Jupyter's default; preserves diff-readability.)
    8. Re-loads and re-asserts post-state: `len(nb['cells']) == 9`, `'PYSPARK_SUBMIT_ARGS' in ''.join(cells[1]['source'])`, `'hl.init(' in ''.join(cells[2]['source'])`, `"spark.executor.cores" == '1'" in ''.join(cells[2]['source']) or "assert cores == '1'" in ''.join(cells[2]['source'])`.

    **Cell 1a source body (verbatim per feedback_aou_dataproc_pyspark_submit_args canonical pattern):**

    ```python
    # Cell 1a — Force Spark executor resources at the spark-submit boundary.
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
    ```

    **Cell 1b source body (direct hl.init + belt-and-suspenders spark_conf dict + cores=1 assert + commit 36e8062 patch verification):**

    ```python
    # Cell 1b — Initialize Hail with spark_conf threading + verify executor.cores=1.
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
    ```

    **Step B — Run the helper script:**

    ```bash
    python3 /tmp/sync_aou1_cell1.py
    ```

    The script's own assertions enforce pre/post-state correctness; if any assert fires, the script aborts before write — `.ipynb` is left untouched.

    **Step C — Structural verification (commands listed in <verify>):**

    Run the four structural checks (cell count == 9, PYSPARK_SUBMIT_ARGS grep, spark.executor.cores grep, hl.init grep). If ANY fails: re-inspect the helper script and the produced .ipynb; do NOT commit a partial sync.

    **Step D — Refresh STATE.md:**

    Per [[feedback_state_md_keep_current]]: append a new row to the Quick Tasks table (or update the existing 260512-ldj row if Carter pre-staged one) recording:
    - Quick ID: 260512-ldj
    - Status: CLOSED
    - Subject: "Sync AOU-1_template.ipynb Cell 1 to AoU YARN init pattern (PYSPARK_SUBMIT_ARGS lever + direct hl.init + cores=1 verify)"
    - Commit token: (m3-W1-template-pyspark-submit-args-sync)
    - Pairs with: anchor commit 36e8062 (260512-jd9 _qc_checkpoint_uri suffix patch) + DEC-2026-05-04-01 (v8 partition-explosion OOM remediation)

    Do NOT alter unrelated STATE.md rows. Re-read STATE.md first to find the correct insertion point.

    **Step E — Commit (per [[feedback_multi_terminal_staging]] — explicit paths only):**

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    git add .planning/notebooks/AOU-1_template.ipynb .planning/STATE.md
    git commit -m "docs(m3-W1-template-pyspark-submit-args-sync): stale-template sync — AOU-1_template.ipynb Cell 1 → AoU YARN init pattern

Audit-driven re-analysis closeout deliverable (quick 260512-ldj). NCSU canonical
template was stale at Cell 1: a single \`init_hail()\` call whose
\`spark_conf=dict\` path is silently dropped by AoU's Dataproc + YARN cluster
(empirically confirmed 2026-05-12; canonicalized in
\`feedback_aou_dataproc_pyspark_submit_args\` memory). Re-firing this template
on AoU as-is would hit RegionPool OOM at v8's ~290k partition count.

Sync splits Cell 1 into two cells per the canonical pattern:
  - Cell 1a: \`os.environ['PYSPARK_SUBMIT_ARGS']\` set BEFORE any pyspark/hail
    import — the only lever AoU YARN honors (binds at spark-submit boundary,
    beats cluster-locked spark-defaults.conf).
  - Cell 1b: \`hl.init\` called directly with belt-and-suspenders
    \`spark_conf\` dict + cores==1 assert + \`_qc_checkpoint_uri\` import
    verification (confirms commit 36e8062 / quick 260512-jd9 is live in
    the AoU clone before compute fires).

Pairs with \`naive_coalesce(2048)\` in \`aou_ld_panel.py:218\` (DEC-2026-05-04-01;
anchor commit 8cc6f64) to clear the v8 partition-explosion RegionPool OOM
end-to-end.

Cells 2-7 (cohort definition, sensitivity, EUR parity, disjoint check, summary)
UNCHANGED — the only producer/consumer drift was at the init layer.

Reproducibility / future re-fires / reviewer audit trail. Not blocker-clearing:
Carter's AoU-side notebook is already running with the working pattern this
session.

Pre: 8 cells; Post: 9 cells (1 deleted, 2 inserted, net +1).
STATE.md refresh atomic per feedback_state_md_keep_current.
"
    git push origin main
    ```

    Note: NO Co-Authored-By trailer requested for this commit (quick-task convention; matches prior 260512-jd9 commit style — verify against `git log --format=fuller -1 36e8062` if uncertain).

    **Step F — Post-push verification:**

    ```bash
    git log -1 --stat --format="%H %s"
    ```

    Confirm: HEAD subject contains `(m3-W1-template-pyspark-submit-args-sync)`; stats show 2 files changed (`.planning/notebooks/AOU-1_template.ipynb` + `.planning/STATE.md`).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; python3 -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb')); assert len(nb['cells']) == 9, f'expected 9 cells, got {len(nb[\"cells\"])}'; src=''.join(nb['cells'][1]['source']); assert 'PYSPARK_SUBMIT_ARGS' in src, 'Cell 1a missing PYSPARK_SUBMIT_ARGS'; assert 'spark.executor.cores=1' in src, 'Cell 1a missing cores=1 flag'; src2=''.join(nb['cells'][2]['source']); assert 'hl.init(' in src2, 'Cell 1b missing hl.init call'; assert 'spark.executor.cores' in src2, 'Cell 1b missing spark_conf dict'; assert 'assert cores' in src2 or \"assert sc_conf\" in src2, 'Cell 1b missing cores==1 assert'; assert '_qc_checkpoint_uri' in src2, 'Cell 1b missing commit 36e8062 patch verification'; print('OK: 9 cells; Cell 1a + Cell 1b present; assert + patch-verify wired')" &amp;&amp; grep -c "PYSPARK_SUBMIT_ARGS" .planning/notebooks/AOU-1_template.ipynb &amp;&amp; test "$(grep -c 'spark.executor.cores' .planning/notebooks/AOU-1_template.ipynb)" -ge 2 &amp;&amp; git log -1 --format="%s" | grep -q "m3-W1-template-pyspark-submit-args-sync"</automated>
  </verify>
  <done>
    - `.planning/notebooks/AOU-1_template.ipynb` has 9 cells.
    - cell[1] is Cell 1a (PYSPARK_SUBMIT_ARGS injection; pure-stdlib `import os` only — no pyspark/hail import).
    - cell[2] is Cell 1b (direct `hl.init` + spark_conf dict + cores=1 assert + `_qc_checkpoint_uri` import verification with printed URIs for AFR primary / AFR sensitivity / EUR parity).
    - cell[0]'s markdown source has the appended sync-note paragraph citing `feedback_aou_dataproc_pyspark_submit_args` + `naive_coalesce(2048)` pairing + commit 36e8062 patch-verify.
    - Cells 3-8 (formerly 2-7) are byte-identical to pre-sync state.
    - STATE.md Quick Tasks table records 260512-ldj as CLOSED with commit token.
    - Single commit with `(m3-W1-template-pyspark-submit-args-sync)` token + audit-driven re-analysis / stale-template sync framing in body; staged via explicit `git add` paths (no `-A` / `.`).
    - Push to origin/main confirmed by `git log -1 --stat` showing 2 files changed.
    - `python3 -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb')); assert len(nb['cells']) == 9"` exits 0.
    - `grep -c "PYSPARK_SUBMIT_ARGS" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1.
    - `grep -c "spark.executor.cores" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 2 (env-var arg in Cell 1a + spark_conf dict key in Cell 1b).
    - Helper script `/tmp/sync_aou1_cell1.py` is documented (verbatim source) in the trailing SUMMARY.md for reproducibility (NOT committed to repo — /tmp is ephemeral).
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| NCSU GPFS ↔ AoU workspace | The .ipynb is a TEMPLATE committed NCSU-side; Carter manually mirrors content into the AoU workspace bucket. NO data crosses this boundary — only Jupyter cell source (code text). |
| .ipynb cell[0] markdown ↔ reviewer audit | The sync-note paragraph references private memory file names (`feedback_aou_dataproc_pyspark_submit_args`) but contains no PII / no controlled data / no AoU participant identifiers. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-ldj-01 | Tampering | .ipynb JSON edit via Python helper script | mitigate | Helper script asserts pre-state (8 cells, init_hail present in cell[1]) BEFORE write — re-running against an already-patched file aborts cleanly. Helper asserts post-state (9 cells, PYSPARK_SUBMIT_ARGS in cell[1], hl.init in cell[2], cores==1 assert in cell[2]) AFTER write — corrupt outputs abort before commit. |
| T-ldj-02 | Repudiation | Commit attribution | accept | Standard `(m3-W1-template-pyspark-submit-args-sync)` token + audit-driven re-analysis body framing per [[feedback_original_research_framing]]; user has not requested Co-Authored-By trailer for this quick-task class (matches prior 260512-jd9 commit style). |
| T-ldj-03 | Information disclosure | Cell 1b printed env vars (WORKSPACE_BUCKET / GOOGLE_PROJECT) | accept | These are AoU workspace identifiers, NOT secrets. Printed at notebook execution time only, inside the AoU workspace's Jupyter kernel — never written to NCSU side. Static .ipynb source (committed) contains only the `os.environ[...]` reads, no actual values. |
| T-ldj-04 | Denial of service | Re-firing template on AoU after sync | mitigate | The cores==1 assert in Cell 1b is the DoS guard: if PYSPARK_SUBMIT_ARGS lever ever stops binding (Hail upgrade, AoU cluster config change), Cell 1b raises AssertionError BEFORE any compute cell fires — preventing the v8 RegionPool OOM that was the original threat. |
</threat_model>

<verification>
**Plan-level checks (post Task 1):**

1. `python3 -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb')); assert len(nb['cells']) == 9, f'got {len(nb[\"cells\"])}'; print('OK 9 cells')"` exits 0.
2. `grep -c "PYSPARK_SUBMIT_ARGS" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1.
3. `grep -c "spark.executor.cores" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 2 (env-var --conf arg in Cell 1a + spark_conf dict key in Cell 1b).
4. `grep -c "hl.init(" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1 (direct hl.init call in Cell 1b, replacing the wrapper-routed init_hail() call).
5. `grep -c "_qc_checkpoint_uri" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1 (commit 36e8062 patch verification import in Cell 1b).
6. `grep -c "naive_coalesce(2048)" .planning/notebooks/AOU-1_template.ipynb` returns 0 (the pairing is referenced in comments / markdown but NOT re-invoked in the template — it lives in aou_ld_panel.py:218 and fires inside load_qc_cohort).
7. `grep -c "feedback_aou_dataproc_pyspark_submit_args" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 2 (cited in Cell 1a comment, Cell 1b comment, AND cell[0] markdown sync-note).
8. `grep -c "load_qc_cohort" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 4 (1 import in Cell 1b + 3 invocations in cells 3, 4, 5 — primary AFR / sensitivity AFR / EUR parity, unchanged from pre-sync).
9. `grep -c "len(overlap) == 0" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1 (RESEARCH O5 disjoint check, unchanged from pre-sync — regression guard).
10. `git log -1 --format="%s" | grep -q "m3-W1-template-pyspark-submit-args-sync"` exits 0.
11. `git log -1 --stat` shows `.planning/notebooks/AOU-1_template.ipynb` + `.planning/STATE.md` (exactly 2 files in the commit).
12. `git log origin/main..HEAD` returns empty (push to origin/main confirmed).
</verification>

<success_criteria>
- Cell 1 of `.planning/notebooks/AOU-1_template.ipynb` is split into Cell 1a (PYSPARK_SUBMIT_ARGS injection) + Cell 1b (direct hl.init + spark_conf dict + cores==1 assert + commit 36e8062 patch verification) per the canonical pattern from [[feedback_aou_dataproc_pyspark_submit_args]].
- Cell 1a fires BEFORE any pyspark/hail import (cell[1] in the new layout); Cell 1b is cell[2].
- Cells 3-8 (formerly 2-7) are byte-identical to pre-sync state — verified by `grep -c "load_qc_cohort" >= 4`, `grep -c "len(overlap) == 0" >= 1`, `grep -c "cohort_summary_m3.tsv" >= 1`.
- cell[0] markdown has the appended sync-note paragraph.
- STATE.md Quick Tasks table records 260512-ldj as CLOSED with the (m3-W1-template-pyspark-submit-args-sync) commit token.
- Single atomic commit with audit-driven re-analysis / stale-template sync framing in body (per [[feedback_original_research_framing]]); staged via explicit `git add` paths (per [[feedback_multi_terminal_staging]]).
- Push to origin/main confirmed by `git log origin/main..HEAD` empty.
- The .ipynb is reproducible / future-re-fire-ready / reviewer-audit-ready — does NOT need to be executed NCSU-side; the template is the artifact.
</success_criteria>

<output>
After completion, create `.planning/quick/260512-ldj-sync-aou-1-template-ipynb-cell-1-to-aou-/260512-ldj-SUMMARY.md` recording:
- Pre-sync cell layout (8 cells; cell[1] = stale init_hail() call) → post-sync cell layout (9 cells; cell[1] = Cell 1a PYSPARK_SUBMIT_ARGS; cell[2] = Cell 1b hl.init + verify)
- Verbatim source of `/tmp/sync_aou1_cell1.py` (helper script; /tmp is ephemeral, so the source is preserved in the SUMMARY for reproducibility)
- Commit hash + push confirmation (output of `git log -1 --format="%H %s"` + `git log origin/main..HEAD` empty)
- Cross-refs to anchor commits: `36e8062` (m3-W1-checkpoint-suffix; quick 260512-jd9), `8cc6f64` (DEC-2026-05-04-01 v8 partition-explosion OOM remediation; naive_coalesce(2048) in aou_ld_panel.py:218)
- Cross-refs to applicable memory: `feedback_aou_dataproc_pyspark_submit_args` (canonical pattern; baked 2026-05-12), `feedback_original_research_framing`, `feedback_state_md_keep_current`, `feedback_multi_terminal_staging`
- Note: NOT blocker-clearing for the current session — Carter's AoU-side notebook is already running with the working pattern. This sync is for reproducibility / future re-fires / reviewer audit trail.
</output>
