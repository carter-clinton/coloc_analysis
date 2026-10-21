---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 18
slug: W6-qtl-layer
type: execute
wave: 18
depends_on: ["W5c"]
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_coloc_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_tiers_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Every row of config/ta_r4/qtl_manifest.tsv has exactly one output under each of QTL_A3, QTL_A2 (fixed code: allele-aware join + --qtl-orient true; production, gated) and QTL_legacy (pre-fix argv; repro), proven by the per-group coverage check (D-06, D-07, D-22)"
    - "QTL_A3/QTL_A2 rows carry qtl_orient_* counters that reconcile to the bridged row count; QTL_legacy rows carry none (pre-fix)"
    - "Aggregates and tier assignments (assign_tiers.py --sweep over {0.5, 0.7, 0.8, 0.9}) exist per QTL arm and are sha256-manifested"
    - "Fallback rows are labelled fallback_abf with a reason; no coloc_susie row has n_cs 0 on either side (D-02)"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_coloc_sha256.tsv"
      provides: "sha256 of every QTL row JSON per arm"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_tiers_sha256.tsv"
      provides: "sha256 of the aggregate + tier + sweep tables per arm"
  key_links:
    - from: "config/ta_r4/qtl_manifest.tsv"
      to: "data/r4/results/QTL_*/qtl/*.json"
      via: "run_qtl_group_r4.py coverage check"
      pattern: "coverage"
---

<objective>
Wave 6 runs the pre-registered QTL-colocalization layer in the fixed configurations (A3, A2) and
the pre-fix configuration (legacy). This produces the QTL side of the E-2 before/after and the
identity effect on GWAS×QTL coloc (D-22). Coverage is exact against the static manifest.

Purpose: D-06, D-07, D-22, D-02.
Output: QTL JSONs, aggregates and tiers for three QTL arms, plus manifests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3e-qtl-harmonize-and-group-runner-SUMMARY.md

<interfaces>
Rules (W3e): r4_qtl_group (wildcards qtl_arm, region, source, qtd), r4_qtl_aggregate, r4_qtl_tiers; targets R4_QTL_TARGETS(qtl_arm)
Invocations: QTL_A3 under `bin/r4_fire.sh production A3_1kg`; QTL_A2 under `production A2_identity`; QTL_legacy under `repro repro_routeL`
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Gate + code-state re-check; fire the three QTL arms; per-group coverage</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_coloc_sha256.tsv</files>
  <read_first>
    - the W5a PLAN Task 1 (gate + code-state check)
    - src/snakemake/rules/ta_r4_qtl.smk; src/python/ta_r4/run_qtl_group_r4.py
  </read_first>
  <action>
    Repeat the gate and code-state checks; STOP on failure. Dry-run each QTL arm. The expected group
    job count equals the distinct (region, source, qtd) groups in the manifest; paste it. Fire,
    monitor by listing `.done` files, and confirm "Nothing to be done" after. Each group job already
    exits 1 on a coverage mismatch. Afterwards also run a global check:
    `find data/r4/results/<qtl_arm>/qtl -name '*.json' | wc -l` == manifest rows, for each arm.
    Write the sha256 manifest with arm, rel_path and sha256.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && for a in QTL_A3 QTL_A2 QTL_legacy; do echo $a $(find data/r4/results/$a/qtl -name '*.json' | wc -l); done && awk 'NR>1' config/ta_r4/qtl_manifest.tsv | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - each arm's JSON count equals the manifest row count (all four numbers printed)
    - the manifest has 3 × the manifest-row count of data rows
  </acceptance_criteria>
  <done>The QTL layer ran exhaustively in three configurations.</done>
</task>

<task type="auto">
  <name>Task 2: Orientation-counter reconciliation, fallback check, aggregates and tiers</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_tiers_sha256.tsv</files>
  <read_first>
    - src/python/assign_tiers.py; src/python/aggregate_qtl_coloc.py; config/pph4_thresholds.yaml
  </read_first>
  <action>
    1. Over QTL_A3 and QTL_A2 JSONs: assert that for every row,
       `qtl_orient_exact + qtl_orient_flipped + qtl_orient_dropped_palindromic + qtl_orient_dropped_mismatch + qtl_orient_dropped_unparseable` == the row's bridged count.
       Over QTL_legacy: assert those keys are absent. Over all three: assert no `coloc_susie` row
       has n_cs 0 on either side. Write a short Python check inline in the SUMMARY, with its output.
    2. Fire `r4_qtl_aggregate` and `r4_qtl_tiers` per arm. Write `qtl_tiers_sha256.tsv`.
    3. Log only counts (rows per method, per tier) — no PP.H4 contrasts before W7.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ls data/r4/results/QTL_A3/qtl_tiers* data/r4/results/QTL_A2/qtl_tiers* data/r4/results/QTL_legacy/qtl_tiers* 2>&1 | head -12</automated>
  </verify>
  <acceptance_criteria>
    - the reconciliation check prints 0 violations for each of the three assertions (output pasted)
    - tier + sweep tables exist for all three arms and are in the manifest
  </acceptance_criteria>
  <done>QTL aggregates and tiers exist with verified orientation accounting.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W6)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W6`, commit type `feat`.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git fsck --connectivity-only 2>&1 | tail -2 && git log -1 --format=%s</automated>
  </verify>
  <acceptance_criteria>
    - fsck clean; committed with explicit paths; pushed
  </acceptance_criteria>
  <done>W6 committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| QTL results → tiers | missing rows or mis-oriented betas change tier counts |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W6-01 | Tampering | row loss | mitigate | per-group + global coverage vs the static manifest |
| T-r4-W6-02 | Tampering | orientation accounting | mitigate | counter reconciliation per row; legacy keys absent |
| T-r4-W6-03 | Elevation of privilege | QTL production pre-posting | mitigate | gate re-check; gated rules |
</threat_model>

<verification>
Exact coverage in three arms. Orientation counters reconcile. Tiers manifested.
</verification>

<success_criteria>
The QTL layer's fixed-vs-pre-fix and identity-vs-real contrasts are complete and verified.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W6-qtl-layer-SUMMARY.md`
</output>
