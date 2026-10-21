---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 21
slug: W8b-adversarial-review
type: execute
wave: 21
depends_on: ["W8a"]
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W8-MANUSCRIPT-REVIEW-as-received.md
  - docs/manuscript/r4/id-vs-ref-LD-r4.template.md
  - docs/manuscript/id-vs-ref-LD-r4.md
  - docs/manuscript/r4/supplementary_reproducibility.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "A brief-blind adversarial review (Codex CLI) received ONLY the rendered manuscript and the instruction to attack every claim against the repository's code, tables and manifests; its output is banked verbatim with the prompt sha256 (D-08)"
    - "Every finding has a disposition (verified against file:line → fixed in the template and re-rendered, or rejected with evidence); the finding count equals the disposition-row count"
    - "After remediation the W8a checks still pass, and the old draft is still unchanged"
    - "Carter reviews the submission candidate at a blocking checkpoint whose first option is WAIT"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W8-MANUSCRIPT-REVIEW-as-received.md"
      provides: "verbatim review + disposition table"
  key_links:
    - from: "review findings"
      to: "docs/manuscript/r4/id-vs-ref-LD-r4.template.md"
      via: "fixes applied to the template only; re-render"
      pattern: "render_manuscript"
---

<objective>
Wave 8b has the rendered manuscript attacked by a reviewer who has not seen the plan, the record or
the summaries. The reviewer checks every claim against the code and data, so no mis-specified
premise reaches Carter or a journal. Carter then reviews the submission candidate.

Purpose: D-08 (brief-blind adversarial review before Carter sees a submission candidate); memory feedback_internal_validation_cannot_catch_misspecified_premise.
Output: review record with dispositions, a remediated template/render, Carter's sign-off.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@docs/manuscript/id-vs-ref-LD-r4.md

<interfaces>
Codex CLI: memory reference_codex_cli_for_gsd_review (the only working external reviewer on this node)
Renderer: python -m ta_r4.render_manuscript --template docs/manuscript/r4/id-vs-ref-LD-r4.template.md --out docs/manuscript/id-vs-ref-LD-r4.md --repo .
Checks: tests/ta_r4/test_manuscript_r4.py, tests/ta_r4/test_render_manuscript.py
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Brief-blind Codex review against the repository; bank it verbatim</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W8-MANUSCRIPT-REVIEW-as-received.md</files>
  <read_first>
    - memory reference_codex_cli_for_gsd_review, reference_byte_faithful_artifact_transfer
  </read_first>
  <action>
    Run Codex CLI non-interactively at the repo root. Its prompt is the rendered manuscript plus this
    instruction: "You are a hostile reviewer for a genetics methods journal. For every factual,
    numerical and methodological claim, locate the code, table or manifest in this repository that
    supports it and report every claim that is contradicted, unsupported, overstated, or that
    conflates coloc.abf with identity-LD SuSiE. Also check that the stated pre-registration matches
    .planning/amendments/osf-amendment-r4-FINAL.md. Cite file:line for every finding."
    Do NOT provide the CONTEXT, RESEARCH, LOG, SUMMARYs or results report. Bank the output verbatim
    under a 3-line header (date, exact command, prompt sha256). Verify the banked file's body sha256
    equals the sha256 of the captured stdout.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && head -3 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W8-MANUSCRIPT-REVIEW-as-received.md</automated>
  </verify>
  <acceptance_criteria>
    - the header holds the date, command and prompt sha256; the body's sha256 equals the captured stdout's sha256 (both printed)
  </acceptance_criteria>
  <done>An independent attack on the manuscript is on record.</done>
</task>

<task type="auto">
  <name>Task 2: Disposition every finding; remediate in the template; re-render; re-check; wave-close (W8b)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W8-MANUSCRIPT-REVIEW-as-received.md, docs/manuscript/r4/id-vs-ref-LD-r4.template.md, docs/manuscript/id-vs-ref-LD-r4.md, docs/manuscript/r4/supplementary_reproducibility.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - each file:line the review cites
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    Append a disposition table after the verbatim body (never edit the body). Columns: finding id,
    claim, what the code/table actually shows (file:line, measured), disposition (fixed / rejected),
    and the change made. Fixes go into the TEMPLATE only (or the supplementary note), followed by a
    re-render. Never hand-edit the rendered file. A finding that reveals an analysis error (not a
    prose error) is NOT fixed here: record it as a deviation to raise with Carter at Task 3.
    Re-run the W8a checks. Then run §C with label `W8b`, commit type `docs`.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_manuscript_r4.py tests/ta_r4/test_render_manuscript.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the finding count equals the disposition-row count (both printed); the W8a checks pass; committed; pushed
  </acceptance_criteria>
  <done>The manuscript survived a brief-blind review with every finding dispositioned.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 3: Carter reads the submission candidate</name>
  <what-built>A fresh ~4.5k-word manuscript rendered from FINAL tables, a supplementary reproducibility note, and the brief-blind review record with dispositions.</what-built>
  <how-to-verify>
    1. Read `docs/manuscript/id-vs-ref-LD-r4.md` and `docs/manuscript/r4/supplementary_reproducibility.md`.
    2. Read the disposition table in `ta-r4-W8-MANUSCRIPT-REVIEW-as-received.md`, especially any analysis-level deviation.
    3. Confirm the scientific accuracy and framing, or list the edits.
  </how-to-verify>
  <options>
    - option-wait (FIRST, the default under auto-mode): WAIT. Stop and hand back to Carter.
    - option-approved: Carter types "approved" or his edits. Edits are applied to the template, re-rendered and re-checked; the chain continues to W9 only after his explicit "approved".
  </options>
  <resume-signal>"approved", or edits. Anything else = WAIT.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>Present the documents. Record Carter's response verbatim, dated; commit with an explicit path; push.</action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git log -1 --format=%s -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</automated></verify>
  <acceptance_criteria>
    - the LOG quotes Carter's W8 decision with a date
  </acceptance_criteria>
  <done>Carter has approved the submission candidate, or the edits are recorded.</done>
  <read_first>
    - docs/manuscript/id-vs-ref-LD-r4.md
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| internal record → public manuscript | internal validation cannot catch a mis-specified premise |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W8b-01 | Repudiation | unsupported claims | mitigate | a brief-blind review against the code; every finding dispositioned with file:line |
| T-r4-W8b-02 | Tampering | review record altered | mitigate | verbatim banking with a sha256 equality check; dispositions appended, never edited into the body |
| T-r4-W8b-03 | Tampering | hand-edited rendered numbers | mitigate | fixes go into the template only; re-render; checks re-run |
</threat_model>

<verification>
Review banked verbatim. Dispositions complete. Checks pass. Carter's decision recorded.
</verification>

<success_criteria>
The submission candidate has survived an independent adversarial check and Carter's read.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W8b-adversarial-review-SUMMARY.md`
</output>
