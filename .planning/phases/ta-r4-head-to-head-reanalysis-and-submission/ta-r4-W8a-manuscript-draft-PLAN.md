---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 23
slug: W8a-manuscript-draft
type: execute
wave: 23
depends_on: ["ta-r4-W7-aggregation-figures"]
files_modified:
  - src/python/ta_r4/render_manuscript.py
  - tests/ta_r4/test_render_manuscript.py
  - tests/ta_r4/test_manuscript_r4.py
  - docs/manuscript/r4/id-vs-ref-LD-r4.template.md
  - docs/manuscript/id-vs-ref-LD-r4.md
  - docs/manuscript/r4/supplementary_reproducibility.md
  - docs/manuscript/r4/references.bib
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SUSIE-RSS-POLICY
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "A fresh manuscript exists at docs/manuscript/id-vs-ref-LD-r4.md, rendered from a template whose result numbers come ONLY from {{tbl:...}} / {{man:...}} placeholders resolved against committed tables and manifests; the render fails on any unresolved placeholder (D-08)"
    - "docs/manuscript/id-vs-ref-LD.md is unchanged by W8a/W8b: checked by an acceptance command in these two plans only, never by a permanent test (a fixed-SHA whole-file pin turns red forever after any later legitimate edit; memory feedback_fixed_sha_whole_file_pin_is_a_timebomb; checker W11)"
    - "Main text is 4,000-5,000 words (Abstract <= 250) in a neutral format; the headline is the pre-registered branch from branch_outcomes.tsv; coloc.abf (A1) and identity LD (A2) are never conflated (D-01, D-08, D-09)"
    - "Known factual errors of the old draft are corrected from measured values: 12 curated regions of which 10 are admissible in EUR (HLA_6p21, BMI_Xq24 inadmissible); the EUR panel n measured from the .fam; the AFR reference actually used (1000G AFR 661 primary / 504 sensitivity; the original Track A had no AFR real-LD panel); the SH2B3 PP.H4 provenance as measured in W3b (D-17, D-20, D-24, D-25)"
    - "The Methods carries a rewritten allele-orientation note (the E-2 finding, fix and measured before/after), replacing the retired osf-correction-v2 text; BMI allele restoration is disclosed (D-06, D-18, D-19)"
    - "Main text contains no .planning paths, commit hashes or DEC ids, and none of pivot/revision/salvage/audit-driven; process provenance lives in docs/manuscript/r4/supplementary_reproducibility.md (D-08, framing rule)"
  artifacts:
    - path: "docs/manuscript/id-vs-ref-LD-r4.md"
      provides: "rendered fresh draft"
      min_lines: 150
    - path: "docs/manuscript/r4/id-vs-ref-LD-r4.template.md"
      provides: "the source of truth for prose; numbers are placeholders"
    - path: "docs/manuscript/r4/supplementary_reproducibility.md"
      provides: "commits, DEC ids, OSF links, manifests, env lockfiles, how to re-run"
    - path: "src/python/ta_r4/render_manuscript.py"
      provides: "placeholder resolver against committed tables/manifests"
  key_links:
    - from: "docs/manuscript/r4/id-vs-ref-LD-r4.template.md"
      to: "docs/manuscript/r4/tables/*.tsv"
      via: "{{tbl:<file>:<row-key>:<column>}} placeholders"
      pattern: "\\{\\{tbl:"
---

<objective>
Wave 8a writes the fresh ~4,500-word manuscript from the R4 results. Every result number is bound
to a committed table by a renderer, so prose cannot drift from data. The process provenance moves
to a supplementary reproducibility note, and the old draft is used only as source material.

Purpose: D-08, D-09 (neutral format; no preprint), D-17/D-18/D-19/D-20/D-24/D-25 corrections, D-01 terminology.
Output: renderer + tests, template, rendered draft, supplementary note, bibliography.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W7-RESULTS.md
@.planning/amendments/osf-amendment-r4-FINAL.md
@docs/manuscript/id-vs-ref-LD.md

<interfaces>
Tables: docs/manuscript/r4/tables/*.tsv (status=FINAL header comment); figures: docs/manuscript/r4/figures/fig{1..5}.{pdf,png}
Manifests: .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/*.tsv; config/ta_r4/trait_manifest.tsv
Structure (research §Manuscript guidance): Abstract <= 250 · Introduction ~700 · Methods ~1,500 · Results ~1,500 · Discussion ~900;
  5 figures + 3 tables main (T1 data, T2 agreement/reclassification at 0.8/0.5, T3 E-2 frozen vs fixed), rest supplementary
Reusable from the old draft: background on coloc assumptions, GWAS source descriptions and DOIs (verify vintages), the negative-control
  rationale, references (Wallace 2020/2021, Zou 2022, Benner 2017, Weissbrod 2020). NOT reusable: any number, "systematically inflates",
  .planning/commit/DEC references, "50 regions", n=661/503 claims, "pivot" wording (line 1 of the old draft)
Phase-start commit for the old-draft invariant: 055f159c
Carter's W7 manuscript instructions: signoffs/W7-T3.yaml `instructions` (verify with `python -m ta_r4.signoff verify W7-T3` before starting)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Placeholder renderer (TDD)</name>
  <files>src/python/ta_r4/render_manuscript.py, tests/ta_r4/test_render_manuscript.py</files>
  <read_first>
    - docs/manuscript/r4/tables/ (headers; the row-key column of each table)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ (header formats)
  </read_first>
  <behavior>
    - `{{tbl:branch_outcomes.tsv:contrast=A2_vs_A3,ancestry=EUR,p12_key=p12_primary:branch}}` resolves to the cell value; a multi-key row selector must match exactly one row (0 or >1 → RenderError)
    - `{{tbl:...:col|fmt=.3f}}` formats numbers; `|fmt=pct1` gives one-decimal percent; `|fmt=sci2` gives 2-significant-figure scientific notation
    - `{{man:<manifest>.tsv:<selector>:<col>}}` resolves against $MAN files; `{{cfg:<yaml path>:<dotted.key>}}` resolves against config/ta_r4/*.yaml
    - An unknown file, column or selector → RenderError naming the placeholder. Any `{{` left after rendering → RenderError
    - The renderer refuses a table whose header lacks `status=FINAL` (negative control with a DRAFT fixture)
  </behavior>
  <action>0. Precondition: `cd src/python && $PY -m ta_r4.signoff verify W7-T3` exits 0; non-zero → STOP. Then: tests RED (paste), implement, GREEN. CLI: `python -m ta_r4.render_manuscript --template T --out O --repo .`. The rendered output has a first-line HTML comment carrying the template sha256 and render UTC.</action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_render_manuscript.py -q</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; the SUMMARY shows RED and the DRAFT-table negative control
  </acceptance_criteria>
  <done>Prose numbers can only come from committed FINAL tables.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Write the template, the supplementary reproducibility note and the bibliography; render; manuscript checks</name>
  <files>docs/manuscript/r4/id-vs-ref-LD-r4.template.md, docs/manuscript/id-vs-ref-LD-r4.md, docs/manuscript/r4/supplementary_reproducibility.md, docs/manuscript/r4/references.bib, tests/ta_r4/test_manuscript_r4.py</files>
  <read_first>
    - docs/manuscript/id-vs-ref-LD.md (source material only; never edit)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W7-RESULTS.md and the W7 LOG entry (Carter's instructions)
    - .planning/amendments/osf-amendment-r4-FINAL.md (Methods must match the pre-registration; deviations stated)
    - config/ta_r4/trait_manifest.tsv; manifests/panels_*.tsv; manifests/bmi_allele_restoration_report.tsv; manifests/known_answer_sh2b3.tsv
    - memory feedback_original_research_framing, project_track_a_handle
  </read_first>
  <behavior>
    test_manuscript_r4.py (the properties checked are literal text properties of the manuscript, so text scans are the right instrument; each scan has a negative-control fixture):
    - the rendered file has no `{{`; the template's Abstract and Results sections contain no bare decimal numbers outside placeholders, except whitelisted literals (the thresholds 0.5/0.7/0.8/0.9, years, citation numbers)
    - main-text word count (Abstract through Discussion, excluding tables, figure legends and references) is within [4000, 5000]; the Abstract is <= 250 words
    - main text has no match for `\.planning/`, `\bDEC-\d{4}`, or `\b[0-9a-f]{7,40}\b` tokens that are git objects (verify each candidate with `git cat-file -e`, so hex-looking data does not false-positive), and no `\b(pivot|revision|salvage|audit-driven)\b` (case-insensitive)
    - the strings "50 curated regions" and "50 regions" are absent; the region count sentence is rendered from the regions file / pair manifest via placeholders
    - the headline sentence in the Abstract contains the rendered branch value for each confirmatory contrast
    - the terms "coloc.abf" and "identity LD" never appear in the same sentence as an equivalence (check: no sentence matches `coloc\.abf[^.]*\b(i\.e\.|equivalent|=)\b[^.]*identity`)
  </behavior>
  <action>
    1. Write the template in a neutral format: title, authors (Carter K. Clinton, NCSU ASHES Lab,
       ORCID 0000-0003-2669-8200), Abstract, Introduction, Methods (data; LD panels; arms;
       fine-mapping policy; colocalization; estimands and decision rules as pre-registered, with
       the OSF link; known-answer controls; simulation; allele-orientation note; deviations), Results
       (headline branch first, then E1–E8, AFR, QTL, frozen-vs-fixed), Discussion (what the branch
       means and doesn't; limitations including reference mismatch and panel size per Zou 2022; the
       inadmissible regions), Data availability, Code availability (GitHub repo; OSF az52u/pvb5j),
       References, Figure legends, and Tables 1–3 as placeholders. Every result number is a
       placeholder. Prose is written to the branch; it does not argue for inflation unless the
       branch is INFLATION_SUPPORTED.
    2. `supplementary_reproducibility.md`: commits per wave (from the LOG), DEC ids, the OSF
       record, every manifest path with row counts, env lockfiles, `bin/r4_fire.sh` invocations, the
       known-answer tables, and the brief-blind review records.
    3. `references.bib`: verify each DOI resolves (WebFetch `https://doi.org/<doi>` and check the
       title). Record unverifiable entries in the LOG; do not invent any.
    4. Tests RED, then render with
       `python -m ta_r4.render_manuscript --template docs/manuscript/r4/id-vs-ref-LD-r4.template.md --out docs/manuscript/id-vs-ref-LD-r4.md --repo .`,
       iterate on the text until GREEN. Negative control: put "pivot" in a tmp copy of the rendered
       file and observe the framing test go RED.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_manuscript_r4.py tests/ta_r4/test_render_manuscript.py -q</automated>
  </verify>
  <acceptance_criteria>
    - all checks pass; the SUMMARY reports the measured main-text and Abstract word counts and pastes the Abstract
    - acceptance-only (not a test): `git diff --quiet 055f159c -- docs/manuscript/id-vs-ref-LD.md; echo $?` prints 0. This check is scoped to W8a/W8b; no test file contains the sha
  </acceptance_criteria>
  <done>A fresh, table-bound, correctly framed draft exists.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W8a)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W8a`, commit type `docs`.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git status --porcelain -- docs/manuscript && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - docs/manuscript changes are committed (porcelain shows nothing for the plan's files); pushed
  </acceptance_criteria>
  <done>W8a committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| tables → prose | hand-typed numbers drift from the data |
| old draft → new draft | inherited false facts and framing |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W8a-01 | Tampering | numbers in prose | mitigate | placeholder renderer against FINAL tables; bare-decimal check on Abstract/Results |
| T-r4-W8a-02 | Repudiation | inherited errors (50 regions, n claims, SH2B3 provenance) | mitigate | explicit absence checks + placeholders from manifests |
| T-r4-W8a-03 | Information disclosure | internal provenance in the main text | mitigate | the provenance-token scan with git-object verification; a supplementary note instead |
</threat_model>

<verification>
Renderer tests and manuscript checks pass, with negative controls observed. The old draft is untouched (acceptance command, W8a/W8b only).
</verification>

<success_criteria>
The manuscript states exactly what the pre-registered analysis found, with every number traceable
to a committed table.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W8a-manuscript-draft-SUMMARY.md`
</output>
