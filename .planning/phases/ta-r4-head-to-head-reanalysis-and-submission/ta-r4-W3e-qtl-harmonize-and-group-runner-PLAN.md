---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15
slug: W3e-qtl-harmonize-and-group-runner
type: execute
wave: 15
depends_on: ["ta-r4-W3d-estimators-and-branch-classifier"]
files_modified:
  - src/snakemake/rules/ta_r4_qtl.smk
  - src/python/ta_r4/run_qtl_group_r4.py
  - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
  - tests/ta_r4/test_qtl_group_runner.py
  - tests/ta_r4/test_coloc_pair_r4.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_harmonized_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "Every (source, QTD, region) slice in config/ta_r4/qtl_manifest.tsv is harmonized with the shipped harmonize_eqtl.py / harmonize_sqtl.py into data/r4/qtl/harmonized/ (pre-gate data processing, D-05) with a sha256 manifest"
    - "One group runner executes all manifest rows of a (qtl_arm, region, source, QTD) group: qtl arms are QTL_A3 (A3_1kg fits, EUR_1kg_r4 panel, --ld-allele-join true, --qtl-orient true), QTL_A2 (A2_identity fits, EUR_identity_r4 payload, same flags) and QTL_legacy (repro_routeL fits, legacy_repro panel, --ld-allele-join false, --qtl-orient false — the pre-fix side for E7) (D-06, D-22)"
    - "When the GWAS fit or the QTL fit has no credible set, the runner records method fallback_abf computed by run_coloc_pair_r4.R --mode qtl_abf on the bridged variant set with the yaml priors; fallback rows are never labelled coloc_susie (D-02 applied to the QTL layer)"
    - "The runner's output row ids equal the manifest rows of its group exactly (coverage check fails on any missing or extra row)"
    - "QTL_A3 and QTL_A2 group jobs are production (gated); QTL_legacy is repro"
  artifacts:
    - path: "src/python/ta_r4/run_qtl_group_r4.py"
      provides: "group runner calling run_qtl_coloc.R per row + qtl_abf fallback + coverage check"
    - path: "src/snakemake/rules/ta_r4_qtl.smk"
      provides: "r4_qtl_harmonize, r4_qtl_group, r4_qtl_aggregate, r4_qtl_tiers rules + targets"
  key_links:
    - from: "run_qtl_group_r4.py"
      to: "src/snakemake/scripts/run_qtl_coloc.R --qtl-orient"
      via: "subprocess per manifest row"
      pattern: "qtl-orient"
    - from: "run_qtl_group_r4.py"
      to: "run_coloc_pair_r4.R --mode qtl_abf"
      via: "fallback when n_cs == 0 on either side"
      pattern: "qtl_abf"
---

<objective>
Wave 3e prepares the QTL layer before the OSF post. It harmonizes the QTL inputs (data processing,
which D-05 allows pre-gate) and builds and tests the group runner. The runner executes every
pre-registered QTL row under the fixed (A3, A2) and pre-fix (legacy) configurations, with the D-02
fallback applied consistently. All QTL analysis code is then frozen before pre-registration.

Purpose: D-06 (QTL side of E-2), D-07, D-22, D-02.
Output: harmonized QTL slices + manifest, the group runner, the qtl_abf mode, rules, tests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2c-qtl-downloads-manifest-and-panel-review-SUMMARY.md

<interfaces>
Harmonizers (shipped; do not edit): src/python/harmonize_eqtl.py, src/python/harmonize_sqtl.py
  CLI per qtl_download.smk:166-205 / :259-305: --input --region-chr --region-start --region-end --gene-id --tissue-name
  --tissue-n --qtl-source-config config/qtl_sources.yaml --output; conda envs/qtl_processing.yml (restored in W0a; lockfile in W0b2)
run_qtl_coloc.R CLI (qtl_coloc.smk:480-497): --gwas-fit --qtl-sumstats --ld-matrix --qtl-source --tissue --gene-id --region
  --ancestry --sdy --sample-size --policy --ld-allele-join --variant-list --output, plus --qtl-orient (W1)
Tiering: src/python/assign_tiers.py (--input --gwas-coloc --pph4-config --output --sweep --sweep-output); aggregation: src/python/aggregate_qtl_coloc.py
QTL manifest (W2c): config/ta_r4/qtl_manifest.tsv (qtl_row_id, region_safe, ancestry, trait, source, tissue, qtd, gene_id, molecular_trait_id, ...)
Tissue N lookup: qtl_download.smk build_tissue_n_lookup (mirror its source of tissue_n)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Harmonize every manifest slice (pre-gate) with a sha256 manifest</name>
  <files>src/snakemake/rules/ta_r4_qtl.smk, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_harmonized_sha256.tsv</files>
  <read_first>
    - src/snakemake/rules/qtl_download.smk lines 150-305 (tissue N lookup; harmonize rules)
    - src/python/harmonize_eqtl.py and src/python/harmonize_sqtl.py (output columns: are variant_id, rsid and GRCh37 coords retained?)
    - config/ta_r4/qtl_manifest.tsv (head)
  </read_first>
  <action>
    In `ta_r4_qtl.smk`, add rule `r4_qtl_harmonize`. It runs one job per (source, qtd, region),
    looping in its shell over the group's distinct gene/feature ids from the manifest and calling
    the shipped harmonizer once per id. Output: a group `.done` file plus the per-id files under
    `data/r4/qtl/harmonized/{source}/{qtd}/{gene_id}/{region}.harmonized.tsv.gz`. It runs in
    `envs/qtl_processing.yml` through the R4 conda prefix, as stage repro (pre-gate). Fire it
    through `bin/r4_fire.sh repro repro_routeC` (dry-run first). Track progress by counting files.
    Write `$MAN/qtl_harmonized_sha256.tsv`. Reconcile: harmonized file count == distinct
    (source, qtd, feature, region) rows in the manifest. Each empty-output case is listed with the
    harmonizer's message, never re-run with different parameters.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && find data/r4/qtl/harmonized -name '*.harmonized.tsv.gz' | wc -l && cut -f1,5,7,8 config/ta_r4/qtl_manifest.tsv | tail -n +2 | awk -F'\t' '{print $2"|"$3"|"$4}' | sort -u | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - the two counts printed are equal (column indices confirmed against the header in the SUMMARY), or the difference equals the listed empty-output cases
    - `awk 'NR>1' $MAN/qtl_harmonized_sha256.tsv | wc -l` equals the harmonized file count
  </acceptance_criteria>
  <done>QTL inputs are harmonized and manifested on /rs1.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: qtl_abf fallback mode + group runner (TDD) + gated group/aggregate/tier rules</name>
  <files>src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_qtl.smk, tests/ta_r4/test_qtl_group_runner.py, tests/ta_r4/test_coloc_pair_r4.py</files>
  <read_first>
    - src/snakemake/scripts/run_qtl_coloc.R (whole: the bridge between GWAS GRCh37 rows and QTL GRCh38 rows; the JSON keys incl. status for no-CS cases)
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R (W0d/W3c)
    - src/python/assign_tiers.py, src/python/aggregate_qtl_coloc.py (input expectations)
    - tests/phase2/test_run_qtl_coloc.py (fixture patterns for QTL inputs)
  </read_first>
  <behavior>
    - run_coloc_pair_r4.R --mode qtl_abf --sumstats-a GWAS --qtl-sumstats Q --variant-list CATALOG ... bridges rows exactly as run_qtl_coloc.R does. It runs coloc.abf with the yaml priors (beta/varbeta; QTL type quant, sdY from --sdy) and writes method fallback_abf with the bridged n_snps. Fixture: 6 bridged variants → n_snps 6; PP values equal a direct coloc.abf call
    - The group runner, on a fixture group (2 features × 2 traits), writes 4 row JSONs. The row whose GWAS fit has 0 CS has method fallback_abf with fallback_reason "gwas_n_cs==0". The row with 0 QTL CS has "qtl_n_cs==0". The rest have method coloc_susie
    - Coverage: output ids == manifest ids for the group. A test that deletes one output and re-runs the coverage check gets a failure naming the missing id (negative control)
    - QTL_legacy invokes run_qtl_coloc.R with `--ld-allele-join false` and no `--qtl-orient` token (exact pre-fix argv), checked by inspecting the recorded argv in each row JSON's `argv` field written by the runner
    - The W0d tests still pass after adding the mode
  </behavior>
  <action>
    1. RED: write the tests and paste the failures. Tests that run `run_qtl_coloc.R` or the frozen
       fit script are marked `r4_heavy`.
    2. Add `--mode qtl_abf` to `run_coloc_pair_r4.R`. It reuses `coloc_pair_core`'s abf path; the
       bridge logic is replicated as a function with a differential test against run_qtl_coloc.R's
       bridge on the same fixture (same bridged id set).
    3. `run_qtl_group_r4.py` (CLI `--qtl-arm --region --source --qtd --manifest --out-dir`):
       - Map qtl_arm → (fit arm, panel path via ta_r4.paths, flags) as in the must_haves.
       - For each manifest row: call `$RSCRIPT run_qtl_coloc.R ...`; parse its JSON; decide
         fallback from its n_cs fields (or the GWAS fit's n_CS); call qtl_abf if needed.
       - Write `{out_dir}/{qtl_row_id}.json` with keys `qtl_arm, method, argv, priors, ...` merged
         from the R output.
       - At the end, run the coverage check (exit 1 on mismatch).
    4. `ta_r4_qtl.smk`:
       - Rule `r4_qtl_group`, wildcards (qtl_arm, region, source, qtd). Input: the gate for
         QTL_A3/QTL_A2 (the gate input function keys on the qtl_arm → its fit arm's stage). Output
         `data/r4/results/{qtl_arm}/qtl/{region}.{source}.{qtd}.done`.
       - Rule `r4_qtl_aggregate`: runs `aggregate_qtl_coloc.py` over the arm's JSONs.
       - Rule `r4_qtl_tiers`: runs `assign_tiers.py --sweep` with `config/pph4_thresholds.yaml`.
       - Target lists `R4_QTL_TARGETS(qtl_arm)`.
    5. Dry-run proof: `bash bin/r4_fire.sh production A3_1kg -n <one QTL_A3 group target>` exits
       non-zero at the fire script's `verify-online` step (sentinel absent); the same for a
       QTL_legacy target under `repro repro_routeL` lists jobs (no gate). Also add a fixture-repo
       test (r4_heavy, reusing `make_fixture_repo`) that a QTL_A3 group target dry-run without a
       sentinel fails with OsfGateError at DAG time, so the in-rule gate is proven independently of
       the fire script.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_coloc_pair_r4.py tests/phase2/test_run_qtl_coloc.py -q</automated>
  </verify>
  <acceptance_criteria>
    - all pass; the SUMMARY shows the RED run and the coverage negative control
    - the two dry-run outcomes (gate refusal for QTL_A3; job listing for QTL_legacy) are pasted
  </acceptance_criteria>
  <done>The QTL layer runner is tested, gated where production, and applies D-02 consistently.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W3e)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W3e`, commit type `feat`. The LOG records the commit sha (the last analysis-code commit cited by the W4a amendment).</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - tests/ta_r4 green; tests/m3, phase1 and phase2 unchanged against the baseline; committed; pushed
  </acceptance_criteria>
  <done>W3e committed and pushed. All analysis code is frozen ahead of W4a.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| QTL row outcomes → row set | dropping rows that fail would bias tiers |
| fixed vs pre-fix configuration | E7 needs the exact pre-fix argv, not an approximation |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3e-01 | Repudiation | silent QTL row loss | mitigate | per-group coverage check vs the static manifest; exit 1 on mismatch |
| T-r4-W3e-02 | Tampering | pre-fix route mis-specified | mitigate | the recorded argv per row; a test asserts the exact legacy flags |
| T-r4-W3e-03 | Elevation of privilege | QTL production before the posting | mitigate | gate input on QTL_A3/QTL_A2 rules; dry-run refusal observed |
</threat_model>

<verification>
Harmonized counts reconciled. The runner is tested (fallback, coverage, argv). The gate is effective on QTL production.
</verification>

<success_criteria>
The QTL layer can run exhaustively over the pre-registered rows in fixed and pre-fix configurations
with consistent fallback handling, and all of its code is frozen before the OSF post.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3e-qtl-harmonize-and-group-runner-SUMMARY.md`
</output>
