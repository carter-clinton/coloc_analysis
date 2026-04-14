---
gsd_state_version: 1.0
milestone: v3.1.2
milestone_name: milestone
status: verifying
stopped_at: Completed 05-05-PLAN.md (aggregation + permutation null). Phase 5 complete (5/5 plans).
last_updated: "2026-04-13T21:45:34.308Z"
last_activity: 2026-04-13
progress:
  total_phases: 12
  completed_phases: 4
  total_plans: 20
  completed_plans: 20
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-09)

**Core value:** Convert the manuscript from a descriptive pleiotropy catalog into a mechanistically resolved cross-ancestry framework with three integrated analytical spines (coloc.susie + QTL coloc, bidirectional MR, matched-N cross-ancestry + selection scans).
**Current focus:** Phase 05 — pathway-partitioned-heritability

## Current Position

Phase: 9
Plan: Not started
Status: Phase complete — ready for verification
Last activity: 2026-04-13 — Completed quick task 260413-ro7: Fix Phase 5 Snakemake DAG wiring gaps

Progress: ██░░░░░░░░ 17%

## Performance Metrics

**Velocity:**

- Total plans completed: 10
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 02 | 5 | - | - |
| 05 | 5 | - | - |

**Recent Trend:**

- Last 5 plans: —
- Trend: —

*Updated after each plan completion*
| Phase 00 P01 | 11min | 2 tasks | 10 files |
| Phase 00 P03 | 17min | 2 tasks | 11 files |
| Phase 00 P04 | 14min | 3 tasks | 7 files |
| Phase 01 P01 | 18min | 10 tasks | 17 files |
| Phase 01 P02 | 11 | 5 tasks | 9 files |
| Phase 01 P03 | 19 | 4 tasks | 9 files |
| Phase 01 P04 | 22 | 5 tasks | 8 files |
| Phase 01 P05 | 12min | 4 tasks | 5 files |
| Phase 02 P01 | 8min | 2 tasks | 17 files |
| Phase 02 P02 | 7min | 2 tasks | 8 files |
| Phase 02 P03 | 9min | 2 tasks | 9 files |
| Phase 02 P04 | 6min | 1 tasks | 4 files |
| Phase 02 P05 | 10min | 3 tasks | 11 files |
| Phase 05 P01 | 14min | 3 tasks | 22 files |
| Phase 05 P02 | 11min | 2 tasks | 6 files |
| Phase 05 P03 | 7min | 2 tasks | 5 files |
| Phase 05 P04 | 6min | 2 tasks | 3 files |
| Phase 05 P05 | 20min | 2 tasks | 6 files |

## Accumulated Context

### Decisions

Decisions are logged in .planning/DECISIONS.md (8 decisions as of 2026-04-09).
Recent decisions affecting current work:

- Scope tier: T1 spine first, T2/T3 gated at checkpoints
- Data access: 6 of 8 sources are open-access sumstats; All of Us Controlled Tier already credentialed (sumstats exportable, individual-level stays on Workbench)
- UK Biobank main DUA deferred to not-needed-unless status
- [Phase 00]: Removed hardcoded rscript_bin; fixed Snakemake version pin from 8.* to 7.32.4; used =version conda format for HPC portability
- [Phase 00]: Refactored rules delegate to legacy scripts rather than duplicating logic; all rscript_bin refs removed
- [Phase 00]: DIAMANTE T2D dedup audit: position-level dedup is methodologically sound; 167K count unverifiable from existing artifacts
- [Phase 00]: KCNJ11 confirmed absent from seed regions (only in coloc results with 6 variants < 50 threshold)
- [Phase 00]: Snakefile.test reuses production rules via include directives -- no test-specific rule duplication (D-04)
- [Phase 00]: CI smoke test defaults to dry-run; --full-run flag after data population
- [Phase 00]: Expected PP.H4 regression values are approximate placeholders pending first real data run (T-00-09)
- [Phase 01]: [Phase 01-01]: A6 dispatch resolved via annotate_susie branch (NOT runsusie — plan pre-spec was factually wrong about runsusie signature); annotate_susie(fit, snp_names, R) applied before saveRDS so Wave 3 coloc.susie consumes .fit.rds directly
- [Phase 01]: [Phase 01-01]: Structured 3-step retry ladder (primary -> max_iter_retry -> regularized LD) in run_susie_with_ladder helper; final identity-LD fallback preserved from prior behavior
- [Phase 01]: [Phase 01-01]: Test environment bolted via .r_lib_phase1/ CRAN testthat on la_multitrait_r conda env (envs/r_coloc.yml deferred to DEF-01-02 in Wave 2/3)
- [Phase 01]: [Phase 01-02]: UKBB-LD NPZ schema is scipy.sparse coo_matrix (not upper-triangle flat 'R' as the plan pre-spec assumed); downloader uses scipy.sparse.load_npz().toarray() and drops --npz-key-name CLI flag
- [Phase 01]: [Phase 01-02]: New rules must use absolute LD_BUILD_ENV = str(Path(workflow.basedir) / 'envs' / 'ld_build.yml') to sidestep DEF-01-01; documented pattern for Plan 01-03 to reuse
- [Phase 01]: [Phase 01-02]: Scratch dir /rs1/scratch does not exist on this cluster (954 MB root stub); real ckclinto allocation at /rs1/researchers/c/ckclinto/ukbb_ld_scratch (29 TB) is the default in config + CLI
- [Phase 01]: [Phase 01-03]: Scope B pilot chosen (11 autosomal regions) -- compute not the binding constraint (17 GB empirical vs 100 GB worst case) but GRCh38/GRCh37 build mismatch is. DEF-01-04 tracks the liftover gate.
- [Phase 01]: [Phase 01-03]: Metadata URL corrected to release/3.1/secondary_analyses/hgdp_1kg/metadata_and_qc/gnomad_meta_v1.tsv; plan pre-spec path release/3.1.2/pca/... returns 404. Region column is hgdp_tgp_meta.Genetic.region (dot-separated Hail export), not genetic_region.
- [Phase 01]: [Phase 01-03]: AFR sample count is 1003 metadata / 986 BCF-reconciled on the v2 panel (plan's ~730 was a 1kG-only estimate); Task 1-03-03 test bounds widened to 950-1010.
- [Phase 01]: [Phase 01-03]: Snakemake params values wrapped in lambdas so '{chrom}' in BCF filename template is not misread as a wildcard; pattern documented for future rule authors.
- [Phase 01]: 01-04: Strategy A (delete legacy rule + redirect consumers) over Strategy B (in-place shell swap) for multitrait.smk rewire — physically separates coloc_susie/ from stale legacy coloc/ cache (T-1-05 mitigation)
- [Phase 01]: 01-04: Pattern 6 Option A compat layer — best-pairwise (max PP.H4.abf) row promoted to top-level 'summary'; full pairwise list in 'susie_pairs' — preserves byte-identical compatibility with augment_coloc_summary.py
- [Phase 01]: [Phase 01-05]: Tasks 2+4 merged -- aggregator + sweep table built in single commit; ld_source/ld_matrix dual-key tolerance (Rule 1 auto-fix); Quarto/RMarkdown fallback in dashboard rule; pyyaml added to env for policy parsing
- [Phase 02]: pyliftover installed into smoke_dev for actual coordinate liftover; chain file tamper-checked at >100KB
- [Phase 02]: QTL fixture generator uses seed=42, 150 rows per file, 1 signal variant per region for coloc detection
- [Phase 02]: run_qtl_coloc.R fits SuSiE on QTL side (runsusie suffix=2) then calls coloc.susie; GWAS fit pre-fitted from Phase 1
- [Phase 02]: Manifest builder cross-joins ALL QTL sources from config (not just eQTL); sQTL/pQTL/sc-eQTL rows appear once harmonized files exist
- [Phase 02]: harmonize_eqtl.py pandas fallback when pysam unavailable; tabix path optimal but not required
- [Phase 02]: LOG10P clipped to [0, 300] to handle edge-case negative values; real REGENIE LOG10P is non-negative but clipping prevents invalid pvalues > 1.0
- [Phase 02]: sQTL reuses harmonize_eqtl core logic (_read_eqtl_file, write_harmonized); pQTL gene_id resolved via protein-to-Ensembl lookup table for reproducibility
- [Phase 02]: UKB-PPP auth via SYNAPSE_AUTH_TOKEN env var only; .synapseConfig in .gitignore; Synapse + S3 unsigned fallback download pattern
- [Phase 02]: OneK1K eQTL Catalogue format reuses harmonize_eqtl() directly (identical column schema); cell_type maps to tissue column; dual-source download with QTS000038 primary / onek1k.org S3 fallback
- [Phase 02]: assign_tier() is a pure function of (gwas_pph4, qtl_pph4, threshold) enforcing QTL-source-agnostic design (D-02c)
- [Phase 02]: Negative control coloc reuses run_qtl_coloc.R via manifest-based dispatch (same format as qtl_coloc_manifest.tsv)
- [Phase 02]: L2G concordance uses fuzzy substring matching on studyLocusId; disagreements annotated as findings per D-05b
- [Phase 05]: HESS env uses defaults channel first (conda-forge dropped Python 2.7)
- [Phase 05]: sumstats_utils.py shared module prevents effective-N reimplementation across methods
- [Phase 05]: Placeholder analysis rules use pass in run block for Snakemake compatibility
- [Phase 05]: Phase 5 tests define PROJECT_ROOT locally to avoid missing tests/__init__.py dependency
- [Phase 05]: requests imported at module level with try/except for test mockability
- [Phase 05]: MAGMA annotate runs once per genome build (shared across traits)
- [Phase 05]: FDR correction via statsmodels multipletests BH across all gene sets jointly per trait (D-01a/D-01b)
- [Phase 05]: g:Profiler REST API default + R fallback; no_iea=True for IEA exclusion (D-03b)
- [Phase 05]: Always --overlap-annot in LDSC h2; baseline v2.2 first in --ref-ld-chr (D-04a); post-munge SNP validation at 500K threshold; Bonferroni shared tissue analysis (D-05b)
- [Phase 05]: .ldcts path rewriting extracts basenames + prepends local annot_dir (T-05-13); AST-based shell=True detection in tests
- [Phase 05]: Python 2.7 HESS invoked via subprocess list args only (T-05-18); Z=BETA/SE with NaN rejection (T-05-19); GRCh37 build validation via reference SNPs (T-05-17)
- [Phase 05]: TRAIT_PAIRS computed at Snakemake load time from config trait_ancestries intersection; hess_py27 for HESS rules, magma for Python 3 steps
- [Phase 05]: 3-criterion gene set matching (length, LD complexity, MAF) per D-06c; maf_reference and ld_score_reference REQUIRED
- [Phase 05]: Fixed 4 conda+run incompatibilities in pathway.smk for Snakemake 7.32.4 (magma_fdr, hess_format_sumstats, hess_negative_controls, gprofiler_negative_controls)
- [Phase 05]: Consensus ranking: n_methods_significant desc + geometric mean p asc; empirical p = (n_exceed+1)/(n_total+1)
- [Quick RO7 2026-04-13]: Phase 5 DAG wiring gap closed — consumer rules now depend on download-rule flag files (commit bfb04f8); pre-existing ld_reference.smk / sumstats.smk issues logged as DEF-RO7-01 and deferred.

### Pending Todos

None yet.

### Blockers/Concerns

- DEF-01-04: GRCh38 liftover of config/regions_curated.csv required before build_hgdp_1kg_ld can execute end-to-end. Resolution targeted at Plan 01-04 or 01-05.
- DEF-RO7-01: `build_ld_rds` in `src/snakemake/rules/ld_reference.smk` requires `data/raw/1kg/TRANS.samples` which no rule produces. Pre-existing. Surfaced during Phase 5 smoke dry-run. Blocks g:Profiler branch + all_pathway aggregate.
- DEF-RO7-02: pathway.smk expand() iterates `config.trait_ancestries` beyond what's harmonized on disk; `harmonize_sumstats` raises on missing combos (e.g., bmi/AFR). Blocks per-branch smoke testing of MAGMA / LDSC partitioned / LDSC-SEG / HESS.
- DEF-RO7-03: `config/pipeline.yaml` `paths.harmonized_sumstats` points to wrong dir (`data/processed/sumstats_harmonized` vs actual `data/processed/region_analysis/sumstats_harmonized_fixed/`). Will surface after DEF-RO7-02 is resolved.
- **Decision 2026-04-13:** Phase 5 real-data smoke testing deferred to Phase 9 planning window. Pathway.smk DAG wiring confirmed correct (RO7); remaining blockers are all upstream/config issues surfaced by deeper DAG resolution. Will re-address when Phase 0/1/2 data paths are re-exercised for replication cohorts. Details: `.planning/quick/260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps/deferred-items.md`.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260413-ro7 | Fix Phase 5 Snakemake DAG wiring gaps | 2026-04-13 | bfb04f8 | [260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps](./quick/260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps/) |

## Session Continuity

Last session: 2026-04-13T21:31:30.036Z
Stopped at: Completed 05-05-PLAN.md (aggregation + permutation null). Phase 5 complete (5/5 plans).
Resume file: None

## Phase 0 Closeout Artifacts (2026-04-10)

- **Code review fixes:** 8 findings fixed in commits 6e3dc66..81ab1eb, report at .planning/phases/00-data-access-infrastructure/00-REVIEW-FIX.md (commit 1d5ed54)
- **UKB-PPP Synapse access:** Carter certified 2026-04-10 (15/15 quiz), syn51364943 accessible, s3://ukbiobank.opendata.sagebase.org/ confirmed (commit 8b846b9)
- **FinnGen R12 registration:** submitted 2026-04-10 via elomake.helsinki.fi, actual release is R12 (not R13/R14 as earlier research assumed), bucket finngen-public-data-r12 (commit e912c0c)
- **deCODE portal verification:** email-gated ephemeral download link mechanism, 24,271 SOMAmer files / ~24 TB total (vs 4,907 aptamers in README — anomaly flagged for Phase 2). Ferkingstad 2021 confirmed. 3 test files downloaded to /rs1/researchers/c/ckclinto/coloc_analysis/data/raw/decode_pqtl/ (CRYBB2, RAF1, ZNF41 — all 909-910 MB, gzip-intact). README schema bug: actual column 9 is `minus_log10_pval` not `min_log10_pval`. Commits 4ce2972, 12ec691, 0901230
- **OSF pre-registration:** DOI 10.17605/OSF.IO/PVB5J, public (no embargo), submitted 2026-04-10, linked project osf.io/az52u. Title: "Mechanistic resolution of pleiotropy at cardiometabolic loci...". Framed as original hypothesis-driven research per feedback memory. Draft at .planning/osf_prereg_draft.md. Commits e459563, 18995f0
- **CI smoke test scaffolding:** dry-run verified 2026-04-10T23:14:00Z (29 jobs, 11 rules). 5 scaffolding bugs caught and fixed: (1) validate() schema path, (2-4) 3 include: paths, (5) FINEMAP_OUTPUTS/SUMMARY definition order. Python 3.13 + Snakemake 7.32.4 PEP 701 incompatibility discovered — dev env at /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/ (Python 3.11 + snakemake 7.32.4 + pulp<2.8). First real execution deferred to Phase 1. Commit c213f58
- **Security audit:** SECURED 10/10 threats closed. Report at .planning/phases/00-data-access-infrastructure/00-SECURITY.md. 3 accepted risks (AR-00-01 config non-secrets, AR-00-02 portal registrations, AR-00-03 UCSC chain file). Commit 2030821
