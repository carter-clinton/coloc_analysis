---
status: resolved
resolved_at: 2026-04-20T15:06:10Z
trigger: "t1_phase2_first_production (Stage A only) — Phase 2 QTL coloc first-production has never fired; Snakemake DAG has three architectural gaps (no all_qtl_coloc target, no parse-time QTL_COLOC_OUTPUTS enumeration, aggregate_qtl_coloc depends only on manifest not per-id JSONs)."
created: 2026-04-20
updated: 2026-04-20 (Stage B.5 audit + eQTL smoke complete; sQTL/sc-eQTL/pQTL smokes blocked; child session qtl_coloc_snp_name_mismatch resolved too_few_snps follow-on bug)
child_session: .planning/debug/qtl_coloc_snp_name_mismatch.md
---

## Current Focus

hypothesis: Stage B.5 audit complete. Manifest builder + r_coloc env fixes land. eQTL smoke SUCCEEDED end-to-end with the Ensembl ID fix (2601 variants harmonized; valid JSON output). sQTL/sc-eQTL/pQTL smokes are BLOCKED on prerequisites (raw data missing from disk; pQTL further blocked on Synapse auth token). Separate latent bug surfaced in eQTL smoke: run_qtl_coloc.R reports `too_few_snps — Cannot extract SNP names from GWAS fit` (downstream of harmonization, independent of Stage B.5 scope).
test: Regenerated manifest (1243 rows; gwas_trait=hypertension; eQTL/sQTL/sc-eQTL gene_id=ENSG; pQTL gene_id=symbol); ran eQTL smoke live; dry-ran other three smokes.
expecting: Checkpoint back with honest triage. Do NOT attempt to download 3-5 GB of sQTL data or hit Synapse without explicit approval.
next_action: Commit code changes (manifest builder + env) + debug-log update, then checkpoint back.

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

- timestamp: 2026-04-20 (Stage A committed)
  checked: 3 atomic commits to main branch
  found: (1) `118bd67` fix(t1-phase2): wire all_qtl_coloc target + parse-time QTL_COLOC_OUTPUTS enumeration (Snakefile + qtl_coloc.smk, +139/-2). (2) `028b50a` fix(t1-phase2): resolve pre-existing wildcard bugs in qtl_download.smk (+50/-7). (3) `42580cf` docs(debug): t1-phase2 first-production Stage A investigation log (+129 new file). All commits include Co-Authored-By footer per project convention. No pre-commit hook failures. No amends, no force-push.
  implication: Stage A landed cleanly on main.

- timestamp: 2026-04-20 (Stage B smoke dry-run pre-flight)
  checked: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake -n --use-conda results/qtl_coloc/FTO_16q12_FTO_gtex_eqtl_Adipose_Subcutaneous.json`
  found: DAG resolves clean — 2 jobs total (harmonize_eqtl_region jobid 26 + run_qtl_coloc jobid 0). No download scheduled: GTEx file `data/raw/gtex_v8/Adipose_Subcutaneous.all.tsv.gz` (3.6 GB) and `.tbi` already on disk. SuSiE fit `bmi.EUR.FTO_16q12.fit.rds` present (104 KB). LD ref `EUR/FTO_16q12.rds` present (124 KB). Wildcards: dataset_id=Adipose_Subcutaneous, gene_id=FTO, region=FTO_16q12. Exit 0.
  implication: Stage A wiring is correct end-to-end for this row. Ready to fire real data.

- timestamp: 2026-04-20 (Stage B smoke live execution — FAILED, 2 distinct bugs)
  checked: `snakemake --cores 2 --use-conda results/qtl_coloc/FTO_16q12_FTO_gtex_eqtl_Adipose_Subcutaneous.json`, full log at logs/stage_b_smoke_20260420_105614.log
  found: harmonize_eqtl_region completed in 18s but wrote 0 variants ("WARNING: No variants after harmonization for FTO / Adipose_Subcutaneous"). Output file `data/processed/qtl_harmonized/eqtl/Adipose_Subcutaneous/FTO/FTO_16q12.harmonized.tsv.gz` is header-only (1 line, 117 bytes). run_qtl_coloc then halted with `Error in fread(opt$qtl_sumstats): To read gz files directly, fread() requires 'R.utils' package which cannot be found.` Output JSON never produced.
  implication: Two distinct pre-existing bugs, both latent because Phase 2 had never fired:
    * BUG-2B-1 (manifest-data / harmonize): manifest populates `gene_id` column with gene SYMBOL ("FTO"). `src/python/harmonize_eqtl.py` line 59 docstring + line 109 logic expect ENSEMBL ID ("ENSG00000140718"). Verified: GTEx file format has `gene_id=ENSG00000225630`-style IDs in its `gene_id` column. Symbol-vs-Ensembl mismatch → zero matches → empty harmonized file. Fix is either: (a) change `build_qtl_coloc_manifest.py` to emit Ensembl IDs in the `gene_id` column (requires a gene-symbol→Ensembl mapping table — same class as htn/stroke alias fix); OR (b) teach `harmonize_eqtl.py` to do symbol→Ensembl resolution at filter time (couples the script to a mapping dependency).
    * BUG-2B-2 (env / packaging): `envs/r_coloc.yml` missing `r-r.utils`. `data.table::fread()` delegates gz reading to R.utils::gunzip(). Fix is one-liner addition to the YAML dependency list, then snakemake --use-conda will rebuild the env hash. Low-risk.
  error-class: BUG-2B-1 is DATA-LAYER (parallel in class to the already-documented htn/stroke trait-alias bug — both are instances of build_qtl_coloc_manifest.py emitting the "wrong identifier convention" for downstream consumers). BUG-2B-2 is ENV/PACKAGING (trivially fixable). NEITHER is caused by Stage A. Both would have been surfaced by any first-fire of Phase 2 regardless of wiring approach.

## Stage B.5 Audit (Task 1): build_qtl_coloc_manifest.py column-by-column

Audit performed 2026-04-20 against:
- src/python/build_qtl_coloc_manifest.py (manifest builder; 245 lines)
- src/python/harmonize_eqtl.py (eQTL consumer)
- src/python/harmonize_sqtl.py (sQTL consumer; imports core from harmonize_eqtl)
- src/python/harmonize_pqtl.py (pQTL consumer)
- src/python/harmonize_onek1k.py (sc-eQTL consumer; imports harmonize_eqtl)
- src/snakemake/rules/qtl_coloc.smk (downstream dispatcher)
- src/snakemake/rules/qtl_download.smk (harmonize_*_region rules)
- config/pipeline.yaml (trait_ancestries, traits list)
- config/regions_curated_grch38.csv (source of region, gene, trait data)
- data/raw/gtex_v8/Adipose_Subcutaneous.all.tsv.gz header (real GTEx schema)
- data/processed/ld_reference/EUR/*.rds (LD reference file names)
- data/processed/qtl_harmonized/gtex_tissue_n_lookup.json (tissue N source)
- results/fine_mapping/susie/*.fit.rds (Phase 1 output file names)
- config/qtl_sources.yaml (source definitions)

### BUG-AUDIT-01: gwas_trait uses short codes; downstream expects long names

- **Column:** `gwas_trait`
- **Manifest value example:** `htn`, `bmi`, `t2d`, `asthma` (from regions CSV trait_list column, first trait selected)
- **Downstream consumer 1:** pipeline.yaml `traits:` and `trait_ancestries:` keys → `hypertension`, `bmi`, `t2d`, `asthma`, `stroke` (LONG names)
- **Downstream consumer 2:** Phase 1 SuSiE fit filenames at results/fine_mapping/susie/ → only `hypertension.*.fit.rds`, `stroke.*.fit.rds`, etc. exist; no `htn.*.fit.rds`.
- **Manifest rows affected:** 565 (`htn`) — blocks all coloc invocations on those rows.
- **Alias map required:** htn → hypertension. Also: "stroke?" (from APOL1's "stroke?" region entry — already partially sanitized but the `?` removal at L170 converts it to "stroke" cleanly, so unaffected). Also: "cad" and "ckd" and "obesity" appear as SECOND/THIRD traits in region trait_list (SH2B3_12q24=htn;stroke;cad, APOL1_22q12=htn;ckd;stroke?, CXADR_F2RL1_6p21=htn;obesity) — but the manifest builder only uses traits[0] (line 156: `gwas_trait = traits[0] if traits else "unknown"`) so those never appear in gwas_trait.
- **Fix location:** build_qtl_coloc_manifest.py — add `TRAIT_ALIASES = {"htn": "hypertension"}` map; apply at line 156.

### BUG-AUDIT-02: gene_id uses symbols; harmonize_eqtl.py + harmonize_sqtl.py expect Ensembl IDs

- **Column:** `gene_id`
- **Manifest value example:** `FTO`, `MC4R`, `SH2B3`, `APOL1`, `PYHIN1`, `CXADR`, `F2RL1`, `CDKN2A`, `APOE`, `HLA`, `SLC2A9` (11 unique symbols; from regions CSV gene column)
- **Downstream consumer 1:** harmonize_eqtl.py line 110-112 — filters GTEx gene_id column by prefix match (`df["gene_id"].str.split(".").str[0] == gene_prefix`). GTEx gene_id column contains Ensembl IDs (verified: `ENSG00000225630`, `ENSG00000187583`, etc. in Adipose_Subcutaneous.all.tsv.gz header peek). Prefix of "FTO".split(".")[0] = "FTO" never matches "ENSG00000140718", so every eQTL row produces empty harmonized file.
- **Downstream consumer 2:** harmonize_sqtl.py lines 104-111 — identical filter logic on gene_id column. Same bug.
- **Downstream consumer 3:** harmonize_onek1k.py via harmonize_eqtl delegate (line 134-143) — same bug.
- **Manifest rows affected:** All 1232 gtex_eqtl + gtex_sqtl + onek1k_sceqtl rows (all 1243 − 11 ukbppp_pqtl).
- **Alias map required:** Symbol → Ensembl ID for the 11 gene symbols used by regions_curated_grch38.csv. Note: symbols like "HLA" and "CXADR" do not cleanly map to single Ensembl IDs (HLA is a multi-gene locus; CXADR and F2RL1 are two separate genes — regions CSV separates them with "/").
- **Required mapping (manual curation since no GENCODE GTF on disk — verified by `find /data -name "*gencode*" -o -name "*.gtf*"` returns only test fixtures):**
    - FTO → ENSG00000140718
    - MC4R → ENSG00000166603
    - SH2B3 → ENSG00000111252
    - APOL1 → ENSG00000100342
    - PYHIN1 → ENSG00000163564
    - CXADR → ENSG00000154639
    - F2RL1 → ENSG00000164251
    - CDKN2A → ENSG00000147889 (canonical; CDKN2B is ENSG00000147883 in same locus)
    - APOE → ENSG00000130203
    - HLA → (NO SINGLE MAPPING — sentinel; HLA region has ~40 genes; use HLA-A as proxy = ENSG00000206503, but flag as "multi-gene locus — audit will require manual review post-smoke")
    - SLC2A9 → ENSG00000109107
- **Fix location:** build_qtl_coloc_manifest.py — add hard-coded GENE_SYMBOL_TO_ENSEMBL dict at module top; apply when building row (store Ensembl in `gene_id`, optionally preserve symbol in a new `gene_symbol` column for traceability — but this changes fieldnames, could break downstream readers that hard-code columns; start conservative and only add `gene_symbol` if safely additive).

### BUG-AUDIT-03: gene_id for pQTL uses SYMBOL; UKB-PPP download script expects protein_name (which IS a symbol-like token)

- **Column:** `gene_id` for ukbppp_pqtl rows
- **Manifest value example:** Same 11 gene SYMBOLS (manifest builder treats all sources identically in _genes_for_region)
- **Downstream consumer 1:** qtl_download.smk harmonize_pqtl_region rule line 307 — passes `{wildcards.gene_id}` as `--protein-name` to harmonize_pqtl.py. This is USED as-is by UKB-PPP to look up protein-named Synapse files. UKB-PPP names proteins by HGNC symbol (e.g., `discovery_chr16_FTO.gz` for FTO). Fortunately, symbols ARE valid protein names for UKB-PPP.
- **Downstream consumer 2:** harmonize_pqtl.py line 202-212 — `_load_protein_ensembl_map()` is supposed to convert protein_name to Ensembl. That map lives at `data/external/ukbppp_protein_to_ensembl.tsv` which DOES NOT EXIST on disk (`data/external/` only contains `liftover/`). harmonize_pqtl.py line 79-84 warns and falls back to protein_name as gene_id. Output harmonized TSV will have `gene_id=FTO` not ENSG.
- **Implication:** pQTL rows are internally consistent (all 11 use symbols) but inconsistent with eQTL/sQTL/sc-eQTL rows (which will now emit ENSG after BUG-AUDIT-02 fix). Downstream aggregator aggregate_qtl_coloc.py reads per-id JSON `gene_id` field — mismatch between sources would break gene_tissue_matrix cross-source aggregation.
- **Manifest rows affected:** 11 ukbppp_pqtl rows.
- **Fix location:** Two choices:
    (a) Apply the same GENE_SYMBOL_TO_ENSEMBL fix in manifest builder for ALL sources (pQTL rows get ENSG) AND update harmonize_pqtl.py to accept Ensembl as --protein-name AND translate back to symbol for file lookup. (Invasive.)
    (b) Keep pQTL rows carrying SYMBOL (since UKB-PPP files are symbol-named) and add a second column `ensembl_gene_id` that all rows populate, used by downstream aggregation. (Less invasive but requires wider downstream changes.)
    (c) Accept the inconsistency: pQTL rows emit SYMBOL, eQTL/sQTL/sc-eQTL emit ENSG. Downstream must handle both. (Pragmatic but fragile.)
- **Recommendation:** (c) for now — minimize scope. Document in Stage B.5 commit message that gene_id is polymorphic by qtl_source. Gate on pQTL smoke passing to verify assumption. If the pQTL smoke later requires ENSG, upgrade to (a) in a follow-up.
- **Complication: no SYNAPSE_AUTH_TOKEN in env.** Any attempt to download UKB-PPP data will fail. This means Task 4 cannot fire the pQTL smoke end-to-end unless Carter sets SYNAPSE_AUTH_TOKEN first. Per checkpoint constraint "If Synapse auth is missing for pQTL smoke: checkpoint back with env-var names needed; don't invent credentials" — capture this as a blocker and checkpoint back before Task 5 commits.

### BUG-AUDIT-04: Two regions dropped silently (gene=NA → empty gene list → zero rows)

- **Column:** row-production side-effect of `_genes_for_region()`
- **Regions CSV rows with `gene=NA`:** BMI_5q13.3 and BMI_Xq24 (both from G4 AA_admixture; lead_snp="NA" too). 
- **Manifest builder behavior:** _genes_for_region line 108-113 returns empty list when gene field is "NA" or empty. Line 113's fallback `[region.get("region_id", "unknown")]` is a dead branch because the check at line 112 returns `[]` explicitly (`return genes if genes else [...]` — NOT a direct return; the if-else returns the fallback). Wait: re-reading L113: `return genes if genes else [region.get("region_id", "unknown")]`. So if genes is `[]`, it returns `[region_id]`. But the line 105-106 check says `if not gene_field or gene_field.upper() == "NA": return []` — hard-returns empty list BEFORE reaching the fallback. So yes, BMI_5q13.3 and BMI_Xq24 produce ZERO manifest rows.
- **Expected rows missing:** 12 regions × 4 sources × (49 eQTL + 49 sQTL + 14 sc-eQTL + 1 pQTL tissues) = per-region expected row count 113. Missing 2 regions = 226 missing rows.
- **Observed manifest:** 10 regions × 113 rows = 1130 — but actual count is 1243. Discrepancy: each region's row count varies by tissue (CXADR_F2RL1 has 2 genes so gets 2× rows: 228 rows vs others at 113). Verified: CXADR_F2RL1_6p21 row count = 98 gtex_eqtl + 98 gtex_sqtl + 28 onek1k_sceqtl + 2 ukbppp_pqtl = 226 rows. Other 9 regions × 113 = 1017 + 226 = 1243. ✓
- **Expected with gene=NA regions:** If BMI_5q13.3 and BMI_Xq24 are kept (with fallback gene=region_id), +226 rows → 1469 total. But NONE of those rows would coloc successfully anyway because there's no Ensembl ID for "BMI_5q13.3" — the region represents a gene desert + potential transcript that we haven't mapped.
- **Decision:** LEAVE AS-IS. Dropping NA-gene regions from the QTL manifest is scientifically correct — no gene means no cis-QTL to coloc against. But update fallback at L113 to be dead code (delete it for clarity) and log the dropped region list explicitly. LOW-PRIORITY — not a fix-blocker for Stage B.5.

### BUG-AUDIT-05: tissue_n sourced from gtex_tissue_n_lookup.json — applies to GTEx only; OneK1K + pQTL get 0

- **Column:** `tissue_n`
- **Manifest value for pQTL:** `0` (pQTL tissue is "plasma"; not in gtex_tissue_n_lookup.json; fallback to source_cfg.get("sample_size", 0). qtl_sources.yaml has `ukbppp_pqtl.sample_size: 54219` at line 53. Let me verify this works: line 159 `tissue_n = tissue_n_lookup.get(tissue, source_cfg.get("sample_size", 0))`. For pQTL, tissue="plasma", lookup misses → falls back to `source_cfg.get("sample_size", 0)` = 54219. So pQTL rows should have tissue_n=54219.
- **Manifest value for sc-eQTL:** OneK1K cell types (CD4_NC, Mono_C, etc.) not in gtex_tissue_n_lookup.json. Fallback to `source_cfg.get("sample_size", 0)` = 982 (onek1k_sceqtl.sample_size). So sc-eQTL rows should have tissue_n=982.
- **Verified in current manifest:** FTO row 1 has tissue_n=581 (matches Adipose_Subcutaneous's GTEx N). Spot-checking required for pQTL/sc-eQTL rows — do those actually have 54219 / 982 populated? Will verify when regenerated.
- **Implication:** No bug, but worth spot-check after regeneration. If fallback logic silently emits 0 for pQTL/sc-eQTL, coloc.susie will reject those rows (N=0 invalid).

### BUG-AUDIT-06: harmonized_qtl_path path structure matches rule output paths (after Stage A fixes)

- **Column:** `harmonized_qtl_path`
- **Manifest builder construction (L183-187):** `{harmonized_dir}/{data_type_dir}/{dataset_id}/{gene_id}/{region_id}.harmonized.tsv.gz`
- **Where data_type_dir = source_name after stripping "gtex_" / "ukbppp_" / "onek1k_" prefix:** eqtl, sqtl, pqtl, sceqtl.
- **Rule outputs after Stage A fixes:**
  - harmonize_eqtl_region: `{QTL_HARMONIZED_DIR}/eqtl/{dataset_id}/{gene_id}/{region}.harmonized.tsv.gz` ✓
  - harmonize_sqtl_region: `{QTL_HARMONIZED_DIR}/sqtl/{dataset_id}/{gene_id}/{region}.harmonized.tsv.gz` ✓
  - harmonize_pqtl_region: `{QTL_HARMONIZED_DIR}/pqtl/{tissue}/{gene_id}/{region}.harmonized.tsv.gz` — uses `{tissue}` not `{dataset_id}`.
    - Manifest writes `{dataset_id}/{gene_id}/{region}` → for pQTL, manifest builder sets `dataset_id = tissue = "plasma"`. So path becomes `pqtl/plasma/FTO/FTO_16q12.harmonized.tsv.gz`. Rule output wildcards: `{tissue}=plasma`, `{gene_id}=FTO`, `{region}=FTO_16q12`. Path matches. ✓
  - harmonize_onek1k_region: `{QTL_HARMONIZED_DIR}/sceqtl/{cell_type}/{gene_id}/{region}.harmonized.tsv.gz` — uses `{cell_type}`.
    - Manifest writes `{dataset_id}/{gene_id}/{region}` → for sc-eQTL, manifest builder sets `dataset_id = tissue = cell_type` (L182: `dataset_id = tissue`). So path becomes `sceqtl/CD4_NC/FTO/FTO_16q12.harmonized.tsv.gz`. Rule output wildcards: `{cell_type}=CD4_NC`. Path matches. ✓
- **Verdict:** Paths match after Stage A. No bug.

### BUG-AUDIT-07: gwas_fit_path embeds gwas_trait — breaks on htn rows (same root cause as BUG-AUDIT-01)

- **Column:** `gwas_fit_path`
- **Manifest builder (L174-177):** `{results_root}/fine_mapping/susie/{gwas_trait}.{ancestry}.{region_id}.fit.rds`
- **With `gwas_trait=htn`:** Path resolves to `results/fine_mapping/susie/htn.EUR.APOL1_22q12.fit.rds` — NOT present on disk. Phase 1 produced `hypertension.EUR.APOL1_22q12.fit.rds`.
- **Implication:** Downstream run_qtl_coloc jobs for 565 htn rows will fail at input-resolution with `MissingInputException`.
- **Fix:** Fixed automatically by BUG-AUDIT-01 (trait alias map applied before path construction).

### BUG-AUDIT-08: ld_matrix_path embeds region — region naming is consistent

- **Column:** `ld_matrix_path`
- **Manifest builder (L178-181):** `{ld_reference}/{ancestry}/{region_id}.rds`
- **Regions on disk under data/processed/ld_reference/EUR/:** `9p21_CDKN2A.rds`, `APOE_19q13.rds`, `APOL1_22q12.rds`, `CXADR_F2RL1_6p21.rds`, `FTO_16q12.rds`, `HLA_6p21.rds`, `MC4R_18q21.rds`, `PYHIN1_1q23.rds`, `SH2B3_12q24.rds`, `SLC2A9_urate.rds` — 10 files. NO `BMI_5q13_3.rds` or `BMI_Xq24.rds` in ld_reference/EUR — but Phase 1 SuSiE fits DO include `bmi.EUR.BMI_5q13_3.fit.rds` (underscores), so LD must exist elsewhere, or Phase 1 used a different LD source for those.
- **Region naming:** Regions CSV `BMI_5q13.3` (with DOT before 3). Phase 1 fit file uses `BMI_5q13_3` (UNDERSCORE). Manifest builder writes region_id verbatim from CSV → would emit `BMI_5q13.3` → LD lookup would fail AND Phase 1 fit filename lookup would fail.
- **Mitigation:** But these two regions already have `gene=NA` so manifest drops them (BUG-AUDIT-04). So naming issue is moot for the manifest. However if we fix BUG-AUDIT-04 later (add fallback), we'd hit this naming inconsistency.
- **Implication:** No bug surfaces for Stage B.5. Note for future: if reinstating NA-gene regions, need separate region_id sanitizer to convert `.` → `_` for filesystem-safe naming.

### BUG-AUDIT-09: Manifest dataset_id for pQTL = "plasma" (string) — harmonize_pqtl_region rule expects tissue wildcard = "plasma"

- Resolved in BUG-AUDIT-06 — path structure matches.

### BUG-AUDIT-10: ancestry hardcoded to "EUR" everywhere (line 122)

- **Column:** `ancestry`
- **Manifest builder:** _ancestry_for_region always returns "EUR".
- **Implication:** No AFR coloc rows, no cross-ancestry Phase 2 output. This is PLANNED per the script comment ("GTEx is EUR-only. AFR-ancestry QTL data is limited; we include EUR as primary."). Matches pipeline.yaml trait_ancestries (bmi: [EUR] etc.).
- **Verdict:** No bug. Aligns with project scope (T1 is EUR-only first-production; AFR is T2).

### BUG-AUDIT-11: sdy fallback to 1.0 when None — pQTL must estimate, shouldn't pass 1.0

- **Column:** `sdy`
- **Manifest builder (L131-133):** `sdy = source_cfg.get("sdY", source_cfg.get("sdy", 1.0))`. If None, set to 1.0.
- **qtl_sources.yaml ukbppp_pqtl:** `sdY: null` (line 55). So pQTL rows get sdy=1.0 in the manifest.
- **Downstream:** qtl_coloc.smk harmonize_pqtl_region rule line 296 hardcodes `sdy="estimate"` — overrides the manifest value at rule level. So the manifest's `sdy=1.0` is never used for pQTL harmonization. But the `sdy` column is ALSO consumed by run_qtl_coloc via `_qtl_manifest_field(wc, "sdy")` at qtl_coloc.smk:291 — that would pass `--sdy 1.0` to the R coloc script for pQTL, ignoring the estimate that harmonize_pqtl.py emits per-variant.
- **Investigation needed:** Does run_qtl_coloc.R read sdY from the harmonized TSV's sdY column (populated by harmonize_pqtl.py), or from the --sdy CLI arg? If from TSV — no bug. If from CLI — pQTL coloc will use wrong sdY=1.0 constant. Not blocking for Stage B.5 smoke (can defer to post-smoke diagnostic), but flag.
- **Recommendation:** OUT OF SCOPE for this commit. Flag for Carter in checkpoint.

## Stage B.5 Fix Plan (Task 2)

**Design principle:** Fix at the MANIFEST BUILDER (single source of truth). Do not couple harmonize scripts to new alias dependencies.

### Fix 1: Add TRAIT_ALIASES map in build_qtl_coloc_manifest.py
- One-line dict at module top: `TRAIT_ALIASES = {"htn": "hypertension"}`
- Apply at gwas_trait assignment (line 156): `gwas_trait = TRAIT_ALIASES.get(traits[0], traits[0]) if traits else "unknown"`
- Self-contained; no new file dependencies.
- Resolves BUG-AUDIT-01, BUG-AUDIT-07 (downstream of it).

### Fix 2: Add GENE_SYMBOL_TO_ENSEMBL map in build_qtl_coloc_manifest.py — scoped per-source
- Hard-coded dict at module top for the 11 symbols in regions_curated_grch38.csv.
- Apply ONLY for non-pQTL sources (keep pQTL rows carrying SYMBOL per BUG-AUDIT-03 recommendation (c)).
- Implementation: inside the source loop, add `use_ensembl = source_name != "ukbppp_pqtl"`. When use_ensembl is True, map gene symbol → ENSG; when False, keep symbol as-is. Log a WARNING when a symbol has no mapping so future region additions surface loudly.
- Self-contained; no new file dependencies. No GENCODE GTF required.
- Resolves BUG-AUDIT-02 (resolves eQTL, sQTL, sc-eQTL symbol → Ensembl).

### Fix 3: Add `r-r.utils` to envs/r_coloc.yml
- One-line addition to dependencies list: `- r-r.utils=2.12.3` (latest stable in conda-forge).
- Snakemake --use-conda will rebuild env hash on next invocation.
- Resolves BUG-2B-2.

### Deferred (documented, not fixed in Stage B.5)
- BUG-AUDIT-03 polymorphic gene_id by qtl_source (pQTL=symbol, others=ENSG). Accept and document.
- BUG-AUDIT-05 tissue_n for non-GTEx — verify correct after regeneration; fix only if broken.
- BUG-AUDIT-11 sdy passing path for pQTL. Flag for Carter.

### Checkpoint-back gate before Task 4
- If the pQTL smoke row requires Synapse auth and SYNAPSE_AUTH_TOKEN is not set, halt at Task 4 and checkpoint back with env-var name. Do NOT invent or guess tokens.

## Stage B.5 Execution Evidence

- timestamp: 2026-04-20 (manifest fixes implemented)
  checked: build_qtl_coloc_manifest.py — added TRAIT_ALIASES = {"htn": "hypertension"}; GENE_SYMBOL_TO_ENSEMBL dict (11 genes); SOURCES_REQUIRING_ENSEMBL set; _normalize_trait() and _resolve_gene_identifier() helpers. Added `gene_symbol` column to output schema (additive — preserves original symbol for traceability; csv.DictReader consumers unaffected because they key by header name).
  found: Edit clean. No line changes to downstream consumers.
  implication: Single source-of-truth fix at manifest boundary. pQTL rows keep gene SYMBOL (per BUG-AUDIT-03 scoped-out decision); all other sources get Ensembl ID.

- timestamp: 2026-04-20 (env fix implemented)
  checked: envs/r_coloc.yml — added `r-r.utils=2.12.3` line to dependencies.
  found: Edit clean. snakemake --use-conda will rebuild env hash next invocation.
  implication: Resolves BUG-2B-2.

- timestamp: 2026-04-20 (manifest regenerated)
  checked: `snakemake --cores 1 --use-conda --force results/qtl_coloc/qtl_coloc_manifest.tsv` → 1243 rows written.
  found:
    - Row count: 1244 (1 header + 1243 data), unchanged from pre-fix (11 genes × 12 regions × 4 sources logic unchanged; just identifier translation).
    - gwas_trait distribution: `hypertension: 565, bmi: 226, t2d: 226, asthma: 226` (NO `htn` — verified fix).
    - gene_id distribution by qtl_source: gtex_eqtl/gtex_sqtl/onek1k_sceqtl all emit ENSG; ukbppp_pqtl emits SYMBOL (verified intentional per BUG-AUDIT-03).
    - tissue_n spot-check: pQTL=54219 (sample_size from config); sc-eQTL=982 (OneK1K sample size); GTEx eQTL ranges 73-706 (lookup JSON values). All valid (>0).
    - Header: new `gene_symbol` column inserted between `gene_id` and `region` (additive; non-breaking).
  implication: Manifest is now internally consistent and aligned with downstream conventions.

- timestamp: 2026-04-20 (new r_coloc conda env built)
  checked: mamba env create via snakemake --use-conda invoked by first run_qtl_coloc attempt. Env built at .snakemake/conda/c076b33c5dbe13cadce27be08e3ec22a_/ (1.6 GB).
  found: R.utils package present in .snakemake/conda/c076b33c5dbe13cadce27be08e3ec22a_/lib/R/library/R.utils.
  implication: BUG-2B-2 resolved end-to-end.

- timestamp: 2026-04-20 (eQTL smoke SUCCESS)
  checked: `snakemake --cores 2 --use-conda --rerun-triggers=mtime results/qtl_coloc/FTO_16q12_ENSG00000140718_gtex_eqtl_Adipose_Subcutaneous.json`. Full log: logs/stage_b5_smoke_eqtl_20260420_114706.log.
  found:
    - harmonize_eqtl_region wrote **2601 variants** to `data/processed/qtl_harmonized/eqtl/Adipose_Subcutaneous/ENSG00000140718/FTO_16q12.harmonized.tsv.gz` (vs. 0 before Ensembl fix — confirms BUG-AUDIT-02 resolution).
    - run_qtl_coloc completed and wrote `results/qtl_coloc/FTO_16q12_ENSG00000140718_gtex_eqtl_Adipose_Subcutaneous.json` with `status: too_few_snps, message: Cannot extract SNP names from GWAS fit, n_snps_overlap: 0`. Harmonized TSV has 2601 rows but SNP names couldn't be matched to the SuSiE fit's SNP roster at coloc time.
  implication: **End-to-end pipeline SUCCESS** in the sense that Phase 2 fired cleanly with valid structured output. But a NEW latent downstream issue surfaced in run_qtl_coloc.R: the GWAS SuSiE fit RDS does not expose SNP names in a way the R script recognizes. This is a separate bug class from Stage B.5 (which was scoped to the manifest builder and env packaging). Possibilities:
    * (a) The SuSiE fit was built without named variants (Phase 1 shortcut); need to re-build with explicit variant naming.
    * (b) run_qtl_coloc.R expects a specific named-attribute on the fit object that differs between coloc.susie versions.
    * (c) Variant ID format mismatch between harmonized TSV (`chr16_53766288_C_T`) and the SuSiE fit's internal variant index (likely uses `16:53766288_C/T` or similar).
    This is a run_qtl_coloc.R-layer issue, NOT a manifest-layer issue. Out of scope for Stage B.5. Flag for Carter in checkpoint.
    **UPDATE 2026-04-20 15:06 UTC:** Resolved in child debug session `.planning/debug/qtl_coloc_snp_name_mismatch.md`. Root cause was hypothesis (a) with a specific mechanism: Phase 1 `run_susie_rss.R` called `coloc:::annotate_susie` with an unnamed identity LD matrix (built via `diag(nrow(subset))` for every region that hit the `variants_exceed_threshold` LD sentinel — which is universal in T1 EUR). `annotate_susie` internally fails on unnamed LD because `.susie_setld` indexes by credible-set names. Fix: name the identity R matrix before the annotate_susie call (+12 lines). Coupled fix at Phase 2 run_qtl_coloc.R: match GWAS vs QTL via rsid (build-invariant) + handle the LD .rds list structure (+74/-25 lines). Ten affected Phase 1 fits regenerated (bmi.EUR.FTO_16q12 during debug verification, plus asthma.EUR.FTO_16q12, bmi.EUR.APOE_19q13, bmi.EUR.BMI_5q13_3, hypertension.EUR.APOE_19q13, hypertension.EUR.SH2B3_12q24, stroke.EUR.9p21_CDKN2A, stroke.EUR.SH2B3_12q24, t2d.AFR.FTO_16q12, t2d.EUR.FTO_16q12 post-checkpoint). eQTL smoke end-to-end: status=no_qtl_cs, n_snps_overlap=698 (was 0), pipeline fully functional.

- timestamp: 2026-04-20 (sQTL/sc-eQTL/pQTL smoke BLOCKERS identified)
  checked: dry-run + on-disk data inventory:
    - `data/raw/gtex_v8_sqtl/` → does not exist (no sQTL raw data on disk).
    - `data/raw/onek1k/` → does not exist (no sc-eQTL raw data on disk).
    - `data/raw/ukbppp/` → does not exist (no pQTL raw data on disk).
    - `env | grep SYNAPSE` → NO `SYNAPSE_AUTH_TOKEN` set.
  found:
    - **sQTL smoke:** Would trigger `download_sqtl_catalogue` rule (3-5 GB download). MORE CRITICALLY, manifest uses `dataset_id=Adipose_Subcutaneous` for sQTL rows, but eQTL Catalogue sQTL files are indexed by QTD IDs (e.g., QTD000568 for Adipose_Subcutaneous sQTL). The download URL `ftp://.../Adipose_Subcutaneous/Adipose_Subcutaneous.all.tsv.gz` would 404. **This is a NEW latent bug: BUG-AUDIT-12 — manifest builder `_tissues_for_source` returns tissue names as dataset_ids, but sQTL (and sc-eQTL) need QTD IDs in that column.** Requires a tissue-name → QTD-ID lookup. Similar class to GENE_SYMBOL_TO_ENSEMBL. Beyond Stage B.5 scope (would require extending the fix + potential eQTL Catalogue metadata pull).
    - **sc-eQTL smoke:** Would trigger `download_onek1k_cell_type` (~1 GB). `download_onek1k.py` requires a cached `eqtl_catalogue_dataset_map.json` mapping cell_type → QTD ID. That file does not exist on disk (only gtex_tissue_n_lookup.json exists in data/processed/qtl_harmonized/). Same error class as sQTL: cell_type is NOT a valid QTD ID.
    - **pQTL smoke:** Would trigger `download_ukbppp_protein`. `download_ukbppp.py` line 58 raises RuntimeError("No Synapse auth token provided. Set SYNAPSE_AUTH_TOKEN environment variable or pass --auth-token.") when env var missing. BLOCKED.
  implication: Multi-source smoke cannot complete without (a) user setting SYNAPSE_AUTH_TOKEN AND (b) a new fix campaign to add tissue/cell_type → QTD-ID mapping in the manifest builder (analogous to the Ensembl fix). Per checkpoint constraint "Do NOT reflexively fix — surface the error class and let orchestrator decide", halt here.
    Current evidence is sufficient to justify Stage B.5 commits (manifest builder fix + env fix + eQTL smoke) — eQTL smoke end-to-end is a qualitative proof-of-concept for the manifest-layer fixes applied.


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

root_cause: (Stage A) Three Snakemake DAG spec gaps (per plan) + two pre-existing rule-level wildcard bugs in qtl_download.smk + one pre-existing data-acquisition gap (OpenTargets L2G) + one pre-existing transitive dependency between Phase 5 and Phase 2 that made Phase 5 "silently work" on an empty Phase 2 summary + one pre-existing manifest-data trait-naming inconsistency. All pre-existing issues were latent because Phase 2 had never fired. (Stage B.5) Adds gene_symbol→Ensembl, trait alias, and env/packaging fixes surfaced by audit.

fix: Applied in three files (Stage A) + two more (Stage B.5):

Stage A (already committed):
1. Snakefile — rule all_qtl_coloc + parse-time enumeration.
2. qtl_coloc.smk — QTL_COLOC_OUTPUTS, L2G gating, polymorphic manifest lookup.
3. qtl_download.smk — _pqtl_download_input, _onek1k_download_input, path structure fixes.

Stage B.5 (pending):
4. build_qtl_coloc_manifest.py — TRAIT_ALIASES + GENE_SYMBOL_TO_ENSEMBL maps.
5. envs/r_coloc.yml — add r-r.utils.

verification: Stage A verified (see Verification Summary). Stage B.5 to verify via: (a) manifest regeneration row-count + `gwas_trait` + `gene_id` spot-checks; (b) one smoke per QTL source end-to-end with JSON output containing numeric PP.H4.

commits:
  stage_a:
    - 118bd67  fix(t1-phase2): wire all_qtl_coloc target + parse-time QTL_COLOC_OUTPUTS enumeration
    - 028b50a  fix(t1-phase2): resolve pre-existing wildcard bugs in qtl_download.smk
    - 42580cf  docs(debug): t1-phase2 first-production Stage A investigation log
  stage_b5: (pending)

files_changed:
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/Snakefile (Stage A)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/qtl_coloc.smk (Stage A)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/qtl_download.smk (Stage A)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/debug/t1_phase2_first_production.md (this file)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/build_qtl_coloc_manifest.py (Stage B.5 pending)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/envs/r_coloc.yml (Stage B.5 pending)

stage_b_artifacts:
  - logs/stage_b_smoke_20260420_105614.log (full smoke log)
  - data/processed/qtl_harmonized/eqtl/Adipose_Subcutaneous/FTO/FTO_16q12.harmonized.tsv.gz (header-only, 117 bytes, empty harmonization — will be replaced post-fix)
  - results/qtl_coloc/FTO_16q12_FTO_gtex_eqtl_Adipose_Subcutaneous.json (NOT CREATED — run_qtl_coloc halted)

scope_notes:
  - Plan's "files you will modify" listed only Snakefile and qtl_coloc.smk. Scope expanded to include qtl_download.smk (two rules fixed) because the dry-run verification command required it to exit cleanly, and the bugs fixed in qtl_download.smk are in the same class as the plan's stated bugs (wildcard / input-resolution gaps exposed by never-fired rules).
  - Plan's step 3 (strengthen aggregate_qtl_coloc.input) was revised from "in the rule" to "in the top-level all_qtl_coloc target" — verified necessary by all_pathway regression.
  - Verification 3's DAG semantics changed slightly (summary target alone no longer triggers per-id coloc). Canonical Phase 2 firing via `all_qtl_coloc` is fully correct.
  - Stage B smoke deliberately scoped to ONE row per checkpoint constraint. Did NOT attempt reflexive fix of BUG-2B-1 or BUG-2B-2. Stage B.5 scope per Carter's approval: audit + manifest builder fix + env fix + 4 per-source smokes. No Stage C launch.
  - Stage B.5 CAVEAT: pQTL smoke may require SYNAPSE_AUTH_TOKEN env var. If not set at Task 4 time, checkpoint back rather than fabricate credentials.
