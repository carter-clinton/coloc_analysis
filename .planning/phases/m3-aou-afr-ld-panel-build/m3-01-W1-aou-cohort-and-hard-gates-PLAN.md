---
phase: m3-aou-afr-ld-panel-build
plan: 01
type: execute
wave: 1
depends_on: ["00"]
files_modified:
  - .planning/notebooks/AOU-1_template.ipynb
  - src/python/aou_ld_panel.py
  - .planning/amendments/aou-egress-audit-log.md
  - .planning/amendments/aou-egress-classification-ruling.eml
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-PUBLIC-DATA-ONLY
  - REQ-AOU-LD-VALIDATION

must_haves:
  truths:
    - "AoU workspace exists in portal (Carter pasted from AOU-WORKBENCH-REGISTRATION.md); DUS approved; RPS approved; billing profile attached; P&P draft registered."
    - "AoU egress classification of variant×variant LD matrices as aggregate summary statistics is in writing (the R1 hard gate per AOU-LD-PIPELINE.md §12) — captured as both .planning/amendments/aou-egress-classification-ruling.eml AND a row in .planning/amendments/aou-egress-audit-log.md HARD GATE table."
    - "Carter signoff on Open Issue O1 (D-M3-09) committed at end of Wave 0 (precondition; verified by gate)."
    - "AoU AUX path verification: gsutil ls gs://fc-aou-datasets-controlled/v7/.../aux/ancestry/ from inside the workspace confirms the actual ancestry_preds filename; if differs from RESEARCH Q9 inferred path, src/python/aou_ld_panel.py constant ANCESTRY_PREDS_PATH updated AND committed BEFORE any cohort fire."
    - "AOU-1 cohort-definition notebook lands at .planning/notebooks/AOU-1_template.ipynb (NCSU reference copy; Carter mirrors into AoU workspace) and emits two checkpointed MTs (mt_afr_qc.mt + mt_afr_pca_selfid.mt for D-M3-07 sensitivity AND mt_eur_qc.mt for D-M3-01 EUR parity)."
    - "Cohort sanity check fires: len(set(afr_samples) & set(eur_samples)) == 0 (RESEARCH O5)."
    - "Per-cohort N is recorded in the egress audit log (NOT a row, but referenced in the upcoming Wave 2 dev-fire cohort-summary table)."
  artifacts:
    - path: ".planning/notebooks/AOU-1_template.ipynb"
      provides: "Reference Jupyter notebook for AoU-side AOU-1 cohort-definition fire (Carter mirrors into the AoU workspace bucket)"
      min_lines: 60
    - path: ".planning/amendments/aou-egress-classification-ruling.eml"
      provides: "Carter-archived AoU support email or PDF capturing the variant×variant LD classification ruling (HARD GATE for Wave 1+ Dataproc spend)"
    - path: ".planning/amendments/aou-egress-audit-log.md"
      provides: "Wave 0 placeholder ruling row replaced with the actual ruling (date / classifier / ruling text / document link)"
      contains: "Aggregate summary statistic"
    - path: "src/python/aou_ld_panel.py"
      provides: "Wave 0 driver MAY be updated with verified ANCESTRY_PREDS_PATH if the Wave 1 gsutil ls verification reveals a different filename than the RESEARCH Q9 inferred path"
  key_links:
    - from: ".planning/notebooks/AOU-1_template.ipynb"
      to: "src/python/aou_ld_panel.py"
      via: "from aou_ld_panel import init_hail, load_qc_cohort"
      pattern: "load_qc_cohort"
    - from: "AoU portal egress request"
      to: ".planning/amendments/aou-egress-audit-log.md"
      via: "Carter manual archive of ruling email + audit log row update"
      pattern: "Aggregate summary statistic"
---

<objective>
Wave 1 fires the entire Carter human-action gate stack that BLOCKS Wave 1+ AoU Dataproc spend. Six gates per AOU-LD-PIPELINE.md §2 P1-P7 + §12 R1, plus a one-shot AoU `gsutil ls` verification of the inferred ancestry-preds path (RESEARCH O3), plus the AOU-1 cohort-definition notebook that emits the three checkpointed MatrixTables (`mt_afr_qc.mt` + `mt_afr_pca_selfid.mt` for D-M3-07 sensitivity + `mt_eur_qc.mt` for D-M3-01 EUR parity). NO production cell-fire happens here — this wave proves the workspace, the gate stack, and the cohort definition.

Purpose: Land the irreversible commitments (DUS, RPS, P&P draft, egress ruling) that govern every subsequent compute step, and produce the cohort substrate that Wave 2 dev-fire consumes.

Output: 6 portal-action gates closed (each with audit-log evidence), 1 cohort-definition notebook template (mirrored to AoU workspace), 3 checkpointed MTs in the AoU bucket, and a written egress classification ruling archived NCSU-side.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md
@.planning/amendments/AOU-LD-PIPELINE.md
@.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md

<interfaces>
<!-- Wave 0 deliverables that Wave 1 consumes verbatim. -->

src/python/aou_ld_panel.py exports (Wave 0 Task 3):
- init_hail(default_reference="GRCh38", log_path="/tmp/hail.log") -> None
- load_qc_cohort(mt_path: str, ancestry: str, sensitivity: bool=False) -> hl.MatrixTable
- compute_region_ld(region_row: dict, mt_source: hl.MatrixTable, out_bucket: str) -> dict
- main()

Constants (Wave 0):
- WORKSPACE_BUCKET, GOOGLE_PROJECT, WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH (env vars)
- RELATED_SAMPLES_PATH = "gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv"
- ANCESTRY_PREDS_PATH = "gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv"  (INFERRED — Wave 1 verifies)

AOU-LD-PIPELINE.md §2 P1-P7 prerequisite checklist (the 6 gates):
- P1 — Workspace creation
- P2 — DUS approved
- P3 — RPS approved (template language at AOU-WORKBENCH-REGISTRATION.md §10)
- P4 — Billing profile attached
- P6 — P&P draft registered
- P12 R1 — Egress classification in writing (HARD GATE for compute spend)

D-M3-07 sensitivity-cohort pattern:
mt_afr_pca = filter to ancestry_pred == 'afr' + kinship + sample QC  (primary)
mt_afr_pca_selfid = mt_afr_pca.filter(self_report.contains('Black or African American'))  (sensitivity)

D-M3-01 EUR parity cohort:
mt_eur = filter to ancestry_pred == 'eur' + kinship + sample QC; checkpoint to gs://${WORKSPACE_BUCKET}/ld/mt_eur_qc.mt
</interfaces>
</context>

<tasks>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 1: AoU 6-gate human-action stack — Carter portal action — BLOCKS all downstream compute</name>
  <files>.planning/amendments/aou-egress-audit-log.md, .planning/amendments/aou-egress-classification-ruling.eml</files>
  <read_first>
    - .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md (518-line paste-ready document; 13 portal-section headers)
    - .planning/amendments/AOU-LD-PIPELINE.md §2 P1-P7 (lines 18-41) + §12 R1 (lines 488-505)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decisions D-M3-01 (EUR parity inside AoU) + D-M3-07 (PCA-primary ancestry) — these define the registration framing
  </read_first>
  <action>See &lt;human_gate&gt; block. This task is a Carter human-action checkpoint; no agent action. The agent's role is to verify acceptance_criteria after Carter completes the gate.</action>
  <human_gate>
    <gate>AOU 6-gate prerequisite stack (P1, P2, P3, P4, P6, R1)</gate>
    <description>
      The single largest M3 risk per AOU-LD-PIPELINE.md §12 R1: AoU could classify variant × variant LD matrices as "derived individual-level data" (NOT exportable). Until classified in writing as "aggregate summary statistics" (or equivalent), NO Dataproc compute should fire. This gate captures all six AoU prerequisites in a single Carter human-action block (cheaper to fire all six in one portal session than scatter across 6 task gates).

      Six required gates:

      Gate P1 — AoU workspace creation:
      - Action: Carter logs into AoU Researcher Workbench at researchallofus.org/workbench, creates a new workspace, and pastes content from .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md section by section (13 portal-section headers; Track A is OUT of this workspace).
      - Evidence: screenshot + workspace URL.

      Gate P2 — DUS approval:
      - Action: AoU portal Data Use Statement signoff inside the new workspace.
      - Evidence: portal screenshot showing "DUS Approved" status; date.

      Gate P3 — RPS approval:
      - Action: File Research Purpose Statement using template language from AOU-WORKBENCH-REGISTRATION.md §10 (community-considerations framing per D-M3-07).
      - Evidence: AoU-issued RPS approval email or portal status screenshot.

      Gate P4 — Billing profile attached:
      - Action: Attach ASHES Lab GCP credit profile (or personal GCP profile) to the workspace.
      - Evidence: portal screenshot showing billing-active state.

      Gate P6 — P&P draft registration:
      - Action: File Publications & Presentations draft entry in AoU portal P&P module.
      - Evidence: P&P draft ID returned by AoU.

      Gate R1 (CRITICAL HARD GATE) — Egress classification of variant × variant LD matrices in writing:
      - Action: Carter submits AoU support request citing AOU-LD-PIPELINE.md §13 framing language. Specifically requests AoU support to classify variant × variant LD matrices computed from n >= 60k AFR (and n >= 130k EUR) participants as "aggregate summary statistics" exportable under the standard AoU egress mechanism. Cite the n >= 20-suppression-floor argument (every cell of the matrix is computed from ALL n participants, so no cell is computed from < 20 participants — trivially clears the floor).
      - Evidence: archive AoU support response email / PDF / portal ruling letter to .planning/amendments/aou-egress-classification-ruling.eml. ALSO update .planning/amendments/aou-egress-audit-log.md HARD GATE row with: Date (ISO-8601), Classifier (AoU support case ID), Ruling text (verbatim quote from AoU response), Document link.

      Without Gate R1 closed and the ruling row updated in the audit log, NO compute fires.
    </description>
    <unblocks>Task 2 (AoU AUX path verification) and Task 3 (AOU-1 cohort definition fire)</unblocks>
    <how-to-resolve>
      1. Open AoU portal; close Gates P1, P2, P3, P4, P6 in one session (~2-3 hours of portal navigation including DUS / RPS reading + signoff).
      2. Submit AoU support email for Gate R1 with the §13 framing language pre-templated in AOU-LD-PIPELINE.md.
      3. Wait for AoU response (typical 2-5 business days per AoU support SLA).
      4. When ruling email arrives: archive to .planning/amendments/aou-egress-classification-ruling.eml; update HARD GATE row in .planning/amendments/aou-egress-audit-log.md (replace PENDING placeholder with actual ruling text); commit with token (m3-W1-T1) in subject.
      5. Type "approved" to resume; OR describe blocker if AoU returns "derived individual-level data" classification (which would trigger the §12 R1 fallback path — compute LD inside AoU + run SuSiE inside AoU, only export credible-set tables; treated as out-of-scope phase replan, not a Wave 1 task).
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f .planning/amendments/aou-egress-classification-ruling.eml &amp;&amp; grep -c "Aggregate summary statistic" .planning/amendments/aou-egress-audit-log.md &amp;&amp; grep -c "PENDING" .planning/amendments/aou-egress-audit-log.md</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/amendments/aou-egress-classification-ruling.eml` exits 0 (file exists with size > 0).
    - `wc -c .planning/amendments/aou-egress-classification-ruling.eml` returns ≥ 500 (non-trivial content).
    - `grep -c "Aggregate summary statistic" .planning/amendments/aou-egress-audit-log.md` returns ≥ 1 (HARD GATE row updated).
    - `grep -c "PENDING" .planning/amendments/aou-egress-audit-log.md` returns 0 (Wave 0 placeholder replaced).
    - `grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" .planning/amendments/aou-egress-audit-log.md | head -1` returns a valid ISO-8601 date in the HARD GATE row.
    - Git log shows a commit with `(m3-W1-T1)` token in the subject line.
  </acceptance_criteria>
  <done>
    All 6 gates closed in writing. AoU egress classification ruling archived to .eml file. HARD GATE row in audit log carries the actual classification (NOT placeholder text). Workspace is fired up + billing-attached + P&P-registered. Wave 1+ Dataproc spend is now legally + operationally unblocked.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: AoU AUX path verification — gsutil ls + driver constant update if drift</name>
  <files>src/python/aou_ld_panel.py</files>
  <read_first>
    - src/python/aou_ld_panel.py constants section (top of file) — verify ANCESTRY_PREDS_PATH and RELATED_SAMPLES_PATH match the actual AoU bucket layout
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "O3 — Wave 0 ancestry preds path verification" (lines 748-752) — INFERRED-vs-VERIFIED note
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q8 — AoU ancestry_pred field name verification" (lines 360-376) — confirms field name (ancestry_pred) and value set
  </read_first>
  <action>See &lt;human_gate&gt; block. This task is a Carter human-action checkpoint; no agent action. The agent's role is to verify acceptance_criteria after Carter completes the gate.</action>
  <human_gate>
    <gate>Verify inferred AUX paths are real BEFORE any compute fires</gate>
    <description>
      RESEARCH Q9 confirmed `relatedness_flagged_samples.tsv` lives at `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/relatedness/`. The ancestry-preds path was INFERRED from the same pattern at `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv`. This MUST be verified live from inside the AoU workspace BEFORE Task 3 fires the AOU-1 cohort.

      Carter action (5 minutes inside AoU):
      1. Open a Jupyter notebook in the M3 workspace.
      2. Run shell cell: `gsutil ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/`
      3. Confirm `ancestry/` and `relatedness/` subdirectories exist.
      4. Run `gsutil ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/`
      5. Confirm a file matching `*ancestry*.tsv` exists; capture the EXACT filename (likely `ancestry_preds.tsv` per RESEARCH Q9, but possibly `ancestry_predictions.tsv` or `ancestry_predictions_C2025Q1.tsv` etc.)
      6. Same for `gsutil ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/relatedness/`. Confirm `relatedness_flagged_samples.tsv` exists.
      7. If ANCESTRY_PREDS_PATH in src/python/aou_ld_panel.py differs from the actual filename: update the constant; commit with token (m3-W1-T2) in subject.
      8. If paths match: type "approved" — no commit needed.
    </description>
    <unblocks>Task 3 (AOU-1 cohort definition fire)</unblocks>
    <how-to-resolve>
      1. Run the 4 gsutil ls commands listed above inside an AoU Jupyter notebook.
      2. Compare against RESEARCH Q9 hardcoded paths in src/python/aou_ld_panel.py.
      3. If drift: update the constant + commit + type "approved".
      4. If match: type "approved" with no code change.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; grep -c "ANCESTRY_PREDS_PATH" src/python/aou_ld_panel.py &amp;&amp; grep -c "relatedness_flagged_samples.tsv" src/python/aou_ld_panel.py</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "ANCESTRY_PREDS_PATH" src/python/aou_ld_panel.py` returns ≥ 1 (constant still defined).
    - `grep -c "relatedness_flagged_samples.tsv" src/python/aou_ld_panel.py` returns ≥ 1 (verified path).
    - If `git log --oneline -10 src/python/aou_ld_panel.py` shows a `(m3-W1-T2)` commit: the new path is captured. If no such commit: the inferred path was correct (verbal "approved" reply suffices).
    - `pytest tests/m3/test_aou_ld_panel_local.py -v` STILL passes (regression check — driver still importable).
  </acceptance_criteria>
  <done>
    AUX paths verified live. ANCESTRY_PREDS_PATH and RELATED_SAMPLES_PATH in src/python/aou_ld_panel.py are EITHER unchanged from Wave 0 (if RESEARCH Q9 inference was correct) OR updated to match the actual AoU v7 paths. Wave 1 Task 3 unblocked.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: AOU-1 cohort definition notebook + 3 cohort MTs (AFR primary, AFR sensitivity, EUR parity)</name>
  <files>.planning/notebooks/AOU-1_template.ipynb</files>
  <read_first>
    - src/python/aou_ld_panel.py (Wave 0 deliverable; load_qc_cohort signature)
    - .planning/amendments/AOU-LD-PIPELINE.md §3.1 (lines 46-63) AFR-ancestry inclusion logic + §3.2 (lines 64-67) self-report sensitivity check + §3.4 (lines 79-82) EUR sensitivity cohort
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Recommended aou_ld_panel.py ordering" (lines 124-141) — canonical 9-step driver invocation
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "O5 — AoU EUR cohort relatedness with AFR cohort" (lines 758-762) — sanity-check disjoint cohorts
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decisions D-M3-01 (EUR parity) + D-M3-07 (PCA-primary + sensitivity check)
  </read_first>
  <action>
    Create `.planning/notebooks/AOU-1_template.ipynb` (Jupyter notebook; NCSU reference copy — Carter mirrors into AoU workspace bucket; this version is committed for reproducibility but NOT actually fired NCSU-side). Cells:

    Cell 1 (markdown): "# AOU-1 — Cohort definition. Phase M3 / Wave 1. Drives load_qc_cohort() from src/python/aou_ld_panel.py against the AoU v7 controlled-tier WGS MatrixTable. Emits 3 checkpointed MTs for Wave 2 dev fire."

    Cell 2 (code):
    ```python
    import os, sys
    sys.path.insert(0, "/home/jupyter/coloc_analysis/src/python")
    from aou_ld_panel import init_hail, load_qc_cohort, ANCESTRY_FIELD, KING_KINSHIP_THRESHOLD
    init_hail()
    print(f"WORKSPACE_BUCKET = {os.environ['WORKSPACE_BUCKET']}")
    print(f"GOOGLE_PROJECT = {os.environ['GOOGLE_PROJECT']}")
    print(f"WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH = {os.environ['WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH']}")
    ```

    Cell 3 (code) — Primary AFR cohort:
    ```python
    mt_afr = load_qc_cohort(
        mt_path=os.environ["WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"],
        ancestry="afr",
        sensitivity=False,
    )
    n_afr = mt_afr.count_cols()
    n_var_afr = mt_afr.count_rows()
    print(f"AFR PCA cohort: {n_afr} samples, {n_var_afr} variants")
    # Already checkpointed to gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt by load_qc_cohort()
    ```

    Cell 4 (code) — AFR sensitivity cohort (D-M3-07):
    ```python
    mt_afr_selfid = load_qc_cohort(
        mt_path=os.environ["WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"],
        ancestry="afr",
        sensitivity=True,
    )
    n_afr_selfid = mt_afr_selfid.count_cols()
    print(f"AFR PCA + self-id Black/AA cohort: {n_afr_selfid} samples (subset of AFR PCA cohort)")
    # Checkpoint at gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt
    ```

    Cell 5 (code) — EUR parity cohort (D-M3-01):
    ```python
    mt_eur = load_qc_cohort(
        mt_path=os.environ["WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"],
        ancestry="eur",
        sensitivity=False,
    )
    n_eur = mt_eur.count_cols()
    print(f"EUR PCA cohort: {n_eur} samples")
    # Checkpoint at gs://${WORKSPACE_BUCKET}/ld/mt_eur_qc.mt
    ```

    Cell 6 (code) — Disjoint-cohort sanity check (RESEARCH O5):
    ```python
    afr_samples = mt_afr.s.collect()
    eur_samples = mt_eur.s.collect()
    overlap = set(afr_samples) & set(eur_samples)
    assert len(overlap) == 0, f"AFR and EUR cohorts overlap by {len(overlap)} samples; investigate!"
    print(f"OK: AFR and EUR cohorts disjoint ({len(afr_samples)} + {len(eur_samples)} samples)")
    ```

    Cell 7 (code) — Cohort-summary table for the validation memo:
    ```python
    import pandas as pd
    cohort_summary = pd.DataFrame({
        "cohort": ["AFR_pca", "AFR_pca_selfid", "EUR_pca"],
        "n_samples": [n_afr, n_afr_selfid, n_eur],
        "n_variants": [n_var_afr, mt_afr_selfid.count_rows(), mt_eur.count_rows()],
        "kinship_threshold": [KING_KINSHIP_THRESHOLD] * 3,
        "ancestry_field": [ANCESTRY_FIELD] * 3,
        "checkpoint_path": [
            f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_afr_qc.mt",
            f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_afr_pca_selfid_qc.mt",
            f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_eur_qc.mt",
        ],
    })
    cohort_summary.to_csv("cohort_summary_m3.tsv", sep="\t", index=False)
    print(cohort_summary)
    ```

    Cell 8 (markdown): "## Output: 3 checkpointed MTs in workspace bucket. Mirror cohort_summary_m3.tsv to NCSU GPFS at .planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv after Wave 2 dev fire signoff (Wave 5 close-out task)."
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; python -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb')); cells=nb['cells']; print(f'cell count: {len(cells)}'); assert len(cells) >= 8, 'expected >= 8 cells'; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/notebooks/AOU-1_template.ipynb` exits 0.
    - `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb')); assert len(nb['cells']) >= 8; print('OK')"` prints OK.
    - `grep -c "ancestry=\"afr\"" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 2 (primary + sensitivity).
    - `grep -c "ancestry=\"eur\"" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1 (D-M3-01 EUR parity).
    - `grep -c "sensitivity=True" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1 (D-M3-07).
    - `grep -c "len(overlap) == 0" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1 (RESEARCH O5 disjoint check).
    - `grep -c "mt_afr_qc.mt\\|mt_eur_qc.mt\\|mt_afr_pca_selfid" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 3 (all three checkpoint paths).
    - `grep -c "cohort_summary_m3.tsv" .planning/notebooks/AOU-1_template.ipynb` returns ≥ 1 (output table for validation memo).
  </acceptance_criteria>
  <done>
    AOU-1 notebook template exists at .planning/notebooks/AOU-1_template.ipynb. Carter manually mirrors into AoU workspace + fires AOU-1 (Dataproc spend; ~30-60 min wall on n1-highmem-16 driver). Three checkpoint MTs land in workspace bucket. cohort_summary_m3.tsv records cohort N values. AFR/EUR cohorts verified disjoint. Wave 2 dev fire substrate ready.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU controlled-tier WGS ↔ AoU workspace | Individual-level WGS data accessed via AoU MatrixTable; computation isolated to workspace; cohort-summary TSV is the only summary artifact. |
| AoU workspace ↔ NCSU GPFS | NO data crosses this boundary in Wave 1. Cohort summary stays inside AoU until Wave 5 close-out; the 3 checkpointed MTs are workspace-bucket artifacts only. |
| AoU support email ↔ .planning/amendments/ | Egress classification ruling email is the legal basis for all subsequent egress; archived NCSU-side as .eml file. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3-EGR-W1 | Information disclosure | Wave 1 cohort definition produces individual-level MTs in workspace bucket | mitigate | All 3 checkpointed MTs live ONLY at gs://${WORKSPACE_BUCKET}/ld/ inside the AoU workspace. cohort_summary_m3.tsv is the ONLY artifact mirrored to NCSU (and only at Wave 5; not at Wave 1). The egress classification ruling (Task 1 R1 gate) governs whether this is permitted at all. |
| T-M3-AUTH-W1 | Authorization | AoU portal action stack | mitigate | Carter is the sole authenticated user (eRA Commons + AoU). DUS / RPS / billing all bind the workspace to Carter individually. No agent autonomously triggers portal actions. |
| T-M3-S2-W1 | Reproducibility / provenance | Cohort summary numbers | mitigate | cohort_summary_m3.tsv records: cohort name, N samples, N variants, kinship threshold (0.0442 verbatim from D-M3-07), ancestry field name, checkpoint path. AOU-1 notebook is committed NCSU-side as the canonical recipe (Carter mirrors verbatim into the workspace). |
| T-M3-EGR-RULING | Information disclosure | aou-egress-classification-ruling.eml | accept | Email content is non-PII (a classification ruling, not data); committed to private NCSU repo; cited in OSF amendment trail at osf.io/az52u. |
</threat_model>

<verification>
**Wave 1 phase-level checks (post all 3 tasks):**

1. `test -f .planning/amendments/aou-egress-classification-ruling.eml` AND `wc -c .planning/amendments/aou-egress-classification-ruling.eml` > 500.
2. `grep -c "PENDING" .planning/amendments/aou-egress-audit-log.md` returns 0 (Wave 0 placeholder fully replaced).
3. `grep -c "Aggregate summary statistic" .planning/amendments/aou-egress-audit-log.md` ≥ 1.
4. `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-1_template.ipynb')); assert len(nb['cells']) >= 8" && echo OK`
5. `pytest tests/m3 -x` STILL passes (regression check — Task 2 path update did not break Wave 0 tests).
6. AoU portal screenshot: workspace shown as DUS-approved + RPS-approved + billing-active + P&P-draft (Carter visual verify).
</verification>

<success_criteria>
- All 6 AoU prerequisite gates closed in writing (P1, P2, P3, P4, P6, R1).
- Egress classification ruling archived at .planning/amendments/aou-egress-classification-ruling.eml.
- HARD GATE row in audit log replaces the Wave 0 PENDING placeholder with actual ruling text.
- AUX paths verified live (Task 2); ANCESTRY_PREDS_PATH constant either confirmed or updated.
- AOU-1 cohort-definition notebook lands at .planning/notebooks/AOU-1_template.ipynb with ≥ 8 cells.
- 3 checkpointed MTs (mt_afr_qc.mt + mt_afr_pca_selfid_qc.mt + mt_eur_qc.mt) exist in workspace bucket (verifiable inside AoU; not directly verifiable NCSU-side).
- cohort_summary_m3.tsv records per-cohort N, kinship threshold, ancestry field, checkpoint paths.
- AFR / EUR cohorts confirmed disjoint (assert in Cell 6).
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-01-W1-aou-cohort-and-hard-gates-SUMMARY.md` recording:
- All 6 gates closed (P1 / P2 / P3 / P4 / P6 / R1)
- Egress classification ruling outcome (paste verbatim quote)
- Per-cohort N (AFR_pca / AFR_pca_selfid / EUR_pca)
- AUX path verification result (paths confirmed unchanged OR updated to ___)
- 3 checkpoint MT paths in workspace bucket
- AoU credit consumption to date (cluster-hours used)
</output>
