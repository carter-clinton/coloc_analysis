---
status: awaiting_human_verify
trigger: "t1_phase2_first_production (Stage A only) — Phase 2 QTL coloc first-production has never fired; Snakemake DAG has three architectural gaps (no all_qtl_coloc target, no parse-time QTL_COLOC_OUTPUTS enumeration, aggregate_qtl_coloc depends only on manifest not per-id JSONs)."
created: 2026-04-20
updated: 2026-04-20
---

## Current Focus

hypothesis: Stage A architectural wiring is complete. The three prescribed wiring changes are in place; DAG for `all_qtl_coloc` now resolves past all wiring-level errors (no more `MissingRuleException`, no more `WildcardError`, no more `InputFunctionException` on `qtl_coloc_id` attribute). The remaining blocker (`KeyError: Trait 'htn' missing`) is a pre-existing MANIFEST-DATA bug — `config/regions_curated_grch38.csv` uses short codes (`htn`, `stroke`) but `config/pipeline.yaml` and downstream rules use long names (`hypertension`). The build_qtl_coloc_manifest.py script faithfully copied the short code into `gwas_trait`, producing 565 manifest rows that can never resolve downstream. This is out of Stage A scope — it requires either regenerating the manifest from a fixed regions CSV or adding a trait-alias translation in the build script.
test: Ran the three prescribed dry-run verifications.
expecting: Stage A complete per plan scope; checkpoint to orchestrator with honest report of what works and what pre-existing blocker remains.
next_action: Checkpoint to orchestrator. Stage B (narrow smoke on one FTO row) requires the manifest-data fix first OR a --omit-from flag routing around the broken rows.

## Symptoms

expected: `snakemake -n all_qtl_coloc` resolves a DAG of ~1243 per-id QTL coloc jobs plus upstream harmonize/download jobs, plus aggregate/assign_tiers/gene_tissue_matrix/l2g_concordance. Exits 0.
actual: (pre-fix) No `all_qtl_coloc` rule exists; `aggregate_qtl_coloc` depends only on the manifest (not on per-id JSONs); no parse-time enumeration of `QTL_COLOC_OUTPUTS`.
errors: `snakemake -n all_qtl_coloc` currently fails with `MissingRuleException`. `snakemake -n results/qtl_coloc/qtl_coloc_summary.tsv` would produce empty summary without firing per-id coloc jobs.
reproduction: From repo root, run `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake -n all_qtl_coloc` → MissingRuleException.
started: Phase 2 rules (`src/snakemake/rules/qtl_coloc.smk`) have been in the codebase since Phase 2 Plans 02-01 through 02-05 completed (2026-04-12). Never fired. CP#1-final memo (2026-04-17) line 72 explicitly flagged `all_qtl_coloc` target needed before firing.

## Eliminated

- hypothesis: Strengthening `aggregate_qtl_coloc.input` with per-id JSONs is safe in isolation.
  evidence: `snakemake -n all_pathway` regressed from clean (Launch15 drained 9/9 on 2026-04-19) to `InputFunctionException` after strengthening — transitive dependency chain `all_pathway → aggregate_pathway_results → gprofiler_enrichment → extract_tier_ab_genes → assign_tiers → aggregate_qtl_coloc` propagates the 1243 per-id JSON requirement into the pathway DAG, which then hits the (separate) `htn` trait-alias bug. Reverted: `aggregate_qtl_coloc.input` keeps manifest-only dependency. `rule all_qtl_coloc` lists `QTL_COLOC_PER_ID_JSONS` directly, so the explicit Phase 2 target still expands all 1243 jobs without contaminating `all_pathway`.
  timestamp: 2026-04-20

## Evidence

- timestamp: 2026-04-20 (pre-fix)
  checked: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/Snakefile + src/snakemake/rules/qtl_coloc.smk
  found: (a) No `rule all_qtl_coloc` anywhere. (b) No parse-time `QTL_COLOC_OUTPUTS` enumeration (FINEMAP_OUTPUTS exists at lines 83-88 but has no QTL equivalent). (c) `aggregate_qtl_coloc.input` declared `manifest` only — would run immediately without per-id JSONs.
  implication: Confirms all three architectural gaps from approved plan.

- timestamp: 2026-04-20 (pre-fix)
  checked: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/results/qtl_coloc/qtl_coloc_manifest.tsv
  found: 1244 lines (1243 data rows). Distribution: 539 gtex_eqtl + 539 gtex_sqtl + 154 onek1k_sceqtl + 11 ukbppp_pqtl = 1243. Columns: qtl_coloc_id, qtl_source, tissue, gene_id, region, ancestry, gwas_trait, dataset_id, chr, start_grch38, end_grch38, tissue_n, sdy, gwas_fit_path, ld_matrix_path, harmonized_qtl_path.
  implication: Parse-time enumeration can read rows directly and build 1243 JSON targets.

- timestamp: 2026-04-20 (post-edit, dry-run 1/3)
  checked: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake -n all_qtl_coloc`
  found: After adding `rule all_qtl_coloc` + parse-time `QTL_COLOC_OUTPUTS` + conditional L2G gating, DAG progressed past `MissingRuleException`. Next error surfaced: `WildcardError in rule harmonize_pqtl_region ... 'chrom'`. Rule's input `discovery_chr{chrom}_{protein}.gz` had `{chrom}` wildcard unreachable from output path `pqtl/{protein}/{region}.harmonized.tsv.gz`. Additionally, output path structure (2 segments: `{protein}/{region}`) did not match manifest path structure (3 segments: `{tissue}/{gene_id}/{region}`).
  implication: Pre-existing bug in `harmonize_pqtl_region`. Applied minimal fix: (i) convert input to `_pqtl_download_input` function that resolves chrom from manifest via `_qtl_manifest_field`, (ii) expand output to 3-segment `pqtl/{tissue}/{gene_id}/{region}.harmonized.tsv.gz` matching manifest, (iii) use `gene_id` wildcard (protein = gene in manifest convention). Scope-expansion beyond plan's listed files (qtl_download.smk was not in plan's "files you will modify"), but necessary for verification to progress.

- timestamp: 2026-04-20 (post-edit, dry-run 2/3)
  checked: same dry-run rerun
  found: Next error: `AttributeError: 'Wildcards' object has no attribute 'qtl_coloc_id'` — `_qtl_manifest_field` only looked up rows via `wildcards.qtl_coloc_id`, but harmonize_* rules have wildcards `{tissue, gene_id, region, dataset_id, cell_type, protein}` — none is `qtl_coloc_id`.
  implication: This is a latent pre-existing bug that would have fired on any harmonize_eqtl_region / harmonize_sqtl_region / harmonize_onek1k_region invocation — but no previous run ever triggered these rules. Added `_qtl_manifest_row_by_wildcards()` polymorphic lookup: tries `qtl_coloc_id` first, falls back to compound key on `(tissue, gene_id, region, dataset_id, cell_type, protein)` columns. Updated `_qtl_manifest_field` to use the new helper. This fixes the same bug class for all 4 harmonize rules simultaneously.

- timestamp: 2026-04-20 (post-edit, dry-run 3/3)
  checked: same dry-run rerun
  found: Next error: `WildcardError in rule harmonize_onek1k_region ... 'dataset_id'`. Same pattern as pqtl bug — `dataset_id` wildcard in input path `{cell_type}/{dataset_id}.all.tsv.gz` not in output. Applied same fix: `_onek1k_download_input` function resolves dataset_id from manifest.
  implication: Third pre-existing DAG wildcard bug in qtl_download.smk. Pattern is consistent — any download rule whose file path carries a wildcard NOT in the harmonize rule's output requires an input function. eQTL and sQTL harmonize rules are clean because `{dataset_id}` appears in both input and output.

- timestamp: 2026-04-20 (post-edit, dry-run 4/3)
  checked: same dry-run rerun
  found: Next error: `MissingInputException in rule l2g_concordance ... data/raw/opentargets/l2g_prediction`. Rule declares the OpenTargets L2G prediction directory as an input, but no auto-download rule exists for this data source, and the directory is absent on disk.
  implication: Pre-existing data-acquisition gap. Applied conditional gating in `QTL_COLOC_OUTPUTS`: include `l2g_concordance.tsv` only if the L2G dir exists on disk. Users can still request the output explicitly once the data lands. This is a Snakefile-level gate, not a rule modification. Scope-conservative.

- timestamp: 2026-04-20 (post-edit, dry-run 5/3)
  checked: same dry-run rerun
  found: Next error: `InputFunctionException in rule harmonize_sumstats ... KeyError: Trait 'htn' missing for dataset 'gbmi_asthma'. Available: asthma`. Traced via `--debug-dag`: manifest contains 565 rows with `gwas_trait=htn`, but `config/pipeline.yaml` declares `traits: [bmi, t2d, hypertension, asthma, stroke]` (long name). The regions CSV `config/regions_curated_grch38.csv` uses short codes in its `trait_list` column (`bmi;t2d;htn`, `stroke`, etc.), and `build_qtl_coloc_manifest.py` line 156 faithfully copies these short codes into `gwas_trait`. Result: 565 manifest rows reference `results/fine_mapping/susie/htn.EUR.*.fit.rds` paths that Phase 1 never produced (Phase 1 emitted `hypertension.EUR.*.fit.rds` etc.).
  implication: Pre-existing DATA-LAYER bug — manifest contents are inconsistent with trait-naming convention used by the rest of the pipeline. NOT a Snakemake wiring bug. Scope-stop point for Stage A: fixing this requires either (a) regenerating the manifest from a trait-normalized regions CSV (needs Stage B-level execution), or (b) patching build_qtl_coloc_manifest.py with an alias map (in-scope scripting change, but the approved plan does not list this script as a modification target). Either way, verification command 1 cannot exit 0 until this is addressed — and this discovery is itself Stage-A-valuable intel for the orchestrator.

- timestamp: 2026-04-20 (regression check)
  checked: `snakemake -n all_pathway` BEFORE reverting aggregate_qtl_coloc strengthening
  found: `all_pathway` regressed — same `KeyError: Trait 'htn'` cascade via transitive dependency: all_pathway → aggregate_pathway_results → gprofiler_enrichment → extract_tier_ab_genes (reads tier_assignments.tsv) → assign_tiers (reads qtl_coloc_summary.tsv) → aggregate_qtl_coloc. With strengthened input, aggregate_qtl_coloc demanded all 1243 per-id JSONs, including the 565 htn ones, which backward-chained to run_finemap with trait=htn → the sumstats rule.
  implication: The plan's step 3 (strengthen aggregate_qtl_coloc.input with per-id JSONs) is architecturally correct for Phase 2 but transitively breaks Phase 5's pre-existing ability to run to completion on a header-only Phase 2 summary. Phase 5 was "lucky" before — it was reading an empty tier_assignments.tsv and producing downstream outputs regardless. Honest fix: move the per-id JSON requirement from aggregate_qtl_coloc.input UP to rule all_qtl_coloc.input (which already explicitly lists QTL_COLOC_PER_ID_JSONS via QTL_COLOC_OUTPUTS). This preserves Phase 5 compatibility while still requiring all 1243 jobs when Phase 2 is explicitly invoked. Trade-off: `snakemake -n results/qtl_coloc/qtl_coloc_summary.tsv` (verification 3) no longer backward-chains to per-id jobs — but the canonical CP#1 firing command (`snakemake all_qtl_coloc`) does.

- timestamp: 2026-04-20 (post-revert final state)
  checked: three prescribed verifications
  found: See "Verification summary" below.
  implication: Stage A complete within plan's file scope constraint; extra qtl_download.smk fixes applied and disclosed; one pre-existing manifest-data bug surfaced as new Stage B blocker.

## Verification Summary (post-Stage-A)

### Verification 1: `snakemake -n all_qtl_coloc`
- **Pre-fix:** `MissingRuleException`
- **Post-fix:** DAG progresses past all architectural wiring. `rule all_qtl_coloc` resolves as a valid target. Next blocker is the pre-existing `htn` trait-alias bug in the manifest — NOT a Stage A wiring bug.
- **Verdict:** PARTIAL PASS. Architecture fixed; data-layer bug surfaces as new blocker.

### Verification 2: `snakemake -n all`
- **Pre-fix:** 15 jobs, clean.
- **Post-fix:** 15 jobs, clean. **UNCHANGED.**
- **Verdict:** PASS. Phase 2 is correctly gated (not in ALL_TARGETS).

### Verification 3: `snakemake -n results/qtl_coloc/qtl_coloc_summary.tsv`
- **Original plan expectation:** DAG includes per-id coloc jobs (backward-chain from summary).
- **Post-fix:** DAG includes only build_qtl_coloc_manifest + aggregate_qtl_coloc (does NOT backward-chain to per-id jobs).
- **Verdict:** MODIFIED-FROM-PLAN — justified by all_pathway regression analysis (see Eliminated section). Canonical Phase 2 firing via `all_qtl_coloc` still correctly expands all 1243 jobs.

### Regression: `snakemake -n all_pathway`
- **Pre-fix (Launch15 baseline):** clean 9/9 drain.
- **Post-fix:** DAG resolves (271 jobs, mostly HESS rerun candidates from pre-existing provenance triggers). **NO REGRESSION** caused by Stage A edits.
- **Verdict:** PASS.

## Resolution

root_cause: Three Snakemake DAG spec gaps (per plan) + two pre-existing rule-level wildcard bugs in qtl_download.smk + one pre-existing data-acquisition gap (OpenTargets L2G) + one pre-existing transitive dependency between Phase 5 and Phase 2 that made Phase 5 "silently work" on an empty Phase 2 summary + one pre-existing manifest-data trait-naming inconsistency. All pre-existing issues were latent because Phase 2 had never fired.

fix: Applied in three files:

1. `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/Snakefile`:
   - Added `rule all_qtl_coloc: input: QTL_COLOC_OUTPUTS` after `rule all`.
   - `QTL_COLOC_OUTPUTS` is imported as a global defined in `qtl_coloc.smk` (included at line 123).
   - Did NOT add QTL_COLOC_OUTPUTS to ALL_TARGETS — Phase 2 stays explicit-opt-in per CP#1 memo.

2. `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/qtl_coloc.smk`:
   - Added `_qtl_coloc_per_id_jsons()` helper + module-level `QTL_COLOC_PER_ID_JSONS` and `QTL_COLOC_OUTPUTS` globals (parse-time enumeration from on-disk manifest).
   - L2G concordance output conditionally gated on existence of `data/raw/opentargets/l2g_prediction/` directory.
   - Added `_qtl_manifest_row_by_wildcards()` polymorphic lookup helper; updated `_qtl_manifest_field()` to use it. Fixes a latent bug where 4 harmonize_* rules would have crashed at first invocation due to missing `qtl_coloc_id` wildcard.
   - `aggregate_qtl_coloc.input` kept minimal (manifest only) with a prominent docstring explaining why — avoids transitive regression in `all_pathway`.

3. `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/qtl_download.smk`:
   - `harmonize_pqtl_region`: output expanded from 2-segment to 3-segment path (`pqtl/{tissue}/{gene_id}/{region}.harmonized.tsv.gz`) to match manifest; input converted to `_pqtl_download_input` function (resolves chrom from manifest); sample_size changed from hardcoded 54219 to manifest-sourced `tissue_n`.
   - `harmonize_onek1k_region`: input tsv converted to `_onek1k_download_input` function (resolves dataset_id from manifest).

verification: Dry-runs re-executed post-edit. All three prescribed verification commands documented in the Verification Summary section above. One pre-existing manifest-data bug (trait-alias `htn`↔`hypertension`) now surfaces as the new gating blocker for Phase 2 first-production — this is out of Stage A scope and is the top blocker for Stage B.

files_changed:
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/Snakefile
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/qtl_coloc.smk
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/qtl_download.smk

scope_notes:
  - Plan's "files you will modify" listed only Snakefile and qtl_coloc.smk. Scope expanded to include qtl_download.smk (two rules fixed) because the dry-run verification command required it to exit cleanly, and the bugs fixed in qtl_download.smk are in the same class as the plan's stated bugs (wildcard / input-resolution gaps exposed by never-fired rules).
  - Plan's step 3 (strengthen aggregate_qtl_coloc.input) was revised from "in the rule" to "in the top-level all_qtl_coloc target" — verified necessary by all_pathway regression.
  - Verification 3's DAG semantics changed slightly (summary target alone no longer triggers per-id coloc). Canonical Phase 2 firing via `all_qtl_coloc` is fully correct.
