---
gsd_state_version: 1.0
milestone: m0
milestone_name: m0-pivot-scaffolding
status: post_pivot_m0_in_flight
stopped_at: "M0 pivot scaffolding in flight: 6 amendment docs committed, sumstats v2 download driver + manifest committed, Track A first-pass draft committed (bde60e2). Stage 2 drivers + STATE.md refresh + Phase 03 archive committed by this hygiene pass. Remaining M0: PROJECT/ROADMAP/REQUIREMENTS/DECISIONS rewrites per Amendment §12 + OSF amendment posted (gates M2 per §9.1). Stage 2 production fire 2026-04-22 AM via bin/fire_phase2_stage2_refit.sh produced 51/96 real-LD credible sets (up from 12/96 identity-LD baseline), 0 Tier A, SH2B3 x asthma EUR identity-LD PP.H4=1.0 collapsed to n_cs_a=0 under real-LD — motivating pivot from candidate-locus design to genome-wide joint-signal discovery across 9 traits x 2 ancestries."
last_updated: "2026-04-24T17:48:00.000Z"
last_activity: 2026-04-24
progress:
  total_milestones: 7
  completed_milestones: 0
  current_milestone: m0
  current_milestone_percent: 70
  total_phases: 7
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 10
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-09; scheduled for Amendment §12 rewrite during M0 closeout)

**Core value (post-2026-04-22 reframe):** Dual-aim genome-wide study across 9 complex traits × 2 ancestries: (i) cross-trait pleiotropy discovery via MTAG + CPASSOC + HyPrColoc joint-signal inference with ancestry-matched real LD; (ii) novel-variant discovery across 5 pre-registered novelty classes (joint-signal, ancestry-specific, secondary-signal, pleiotropy-class, functional-mechanism). Authoritative scope: `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`.

**Current focus:** M0 — pivot scaffolding (this hygiene pass + remaining PROJECT/ROADMAP/REQUIREMENTS/DECISIONS rewrites + OSF amendment posting) in foreground; Track A manuscript push (Route A) + sumstats v2 downloads (Route C) in parallel.

## Current Position

**Pivot adopted 2026-04-22.** Project reframed from candidate-locus design (50 hand-curated regions, circular by construction per Amendment §2.3) to **genome-wide joint-signal discovery across 9 traits × 2 ancestries** (Amendment §§2, 4). Milestone sequence M0–M6 replaces the prior T1/T2/T3 tier structure.

**Stage 2 fire numerics (2026-04-22 AM, `bin/fire_phase2_stage2_refit.sh`):**

- 51/96 non-empty real-LD credible sets — 4.25× yield vs 12/96 identity-LD baseline.
- 0 Tier A signals at genome-wide-significance thresholds.
- Flagship SH2B3 × asthma EUR coloc: identity-LD PP.H4 = 1.0 → real-LD n_cs_a = 0 (Benner 2017 identity-LD inflation, now demonstrated on a canonical-literature signal).
- 861 hard failures in the pairwise trait-pair sweep (to be quantified in Track A frozen-numbers pass).

**Two-track split:**

- **Track A** — short-form real-LD audit paper of the candidate-locus design. Venue ladder: *Genome Medicine* → *AJHG* short report → *Bioinformatics* Applications Note. First-pass draft landed 2026-04-23 (commit `bde60e2`) at `docs/manuscript/track_a_pivot.md`. Strategy in `.planning/amendments/TRACK-A-PIVOT.md`.
- **Track B** — genome-wide 9-trait × 2-ancestry joint-signal discovery with MTAG + CPASSOC + HyPrColoc + PolyFun + All-of-Us controlled-tier AFR WGS LD panel (~100k AFR). Target: *Nature Genetics*. Planning lives under `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §§3, 5, 6, 7.

**Four parallel routes** (per `/home/ckclinto/.claude/plans/snappy-humming-pine.md`):

- **Route A** — Track A manuscript push: freeze Tier counts → Section 4.1–4.20 edits → figures → bioRxiv.
- **Route B** — M0 closeout: PROJECT.md / ROADMAP.md / REQUIREMENTS.md / DECISIONS.md rewrites per Amendment §12, then OSF amendment posted (hard gate on M2 per Amendment §9.1).
- **Route C** — Track B M1 sumstats upgrade: `bin/download_sumstats_v2.sh` driver already running on URL-fetchable sources (Aragam 2022, CKDGen 2019, GLGC 2021 landed); manual-fetch queue in `.planning/amendments/SUMSTATS-MANUAL-FETCH.md` awaits Carter portal actions.
- **Route D** — this hygiene pass (Step 0; fills the gap between 2026-04-21 stale state and the pivot-era repo).

**M0 progress: ~70% complete.** Done: this hygiene commit cluster + 6 amendment docs (`PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe`, `TRACK-A-PIVOT`, `SUMSTATS-UPGRADE.md` + `.tsv`, `AOU-LD-PIPELINE`, `SUMSTATS-MANUAL-FETCH`) + sumstats driver + Track A first-pass draft. Outstanding: PROJECT / ROADMAP / REQUIREMENTS / DECISIONS rewrites + OSF amendment PDF posted.

See `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3 for the full M0–M6 milestone sequence.

Progress: █░░░░░░░░░ 10% (M0 ~70% of 1/7 milestones)

### Archived (pre-pivot — T1 spine completed; artifacts reusable per Amendment §8)

The following narrative reflects the project state immediately before the 2026-04-22 reframe. Phases 0/1/2/5/9 outputs are preserved and repurposed as Track A inputs + Track B candidate-locus validation subset per Amendment §8 — not discarded.

Phase: 02 (3-way-qtl-colocalization) — RECOVERY Stage 2 narrow validation COMPLETE, awaiting user LSF fire
Plan: RECOVERY — `.planning/phases/02-3-way-qtl-colocalization/RECOVERY_PLAN.md` (4 stages; Stages 1, 1d, 3-first-pass, 2-narrow DONE)
Status: recovery_stage_2_awaiting_fire -> Carter fires production re-fit -> Stage 4 (CP#1-final decision)
Last activity: 2026-04-21

**Recovery trigger (2026-04-20):** Phase 2 first-production returned 0 Tier A / 0 Tier B / 0 Tier C from 1,010 colocalizations. Root causes (structural, not biological): (1) trait-pair coloc never fired — `coloc_summary.tsv` = 1 byte; (2) only 12/96 Phase 1 SuSiE fits have credible sets; (3) gene-scope mismatch — manifest maps one gene per region, causal gene is often distal (FTO->IRX3/IRX5). Signing CP#1-final on this state would declare a biological null on an input artifact. See `.planning/session_summaries/2026-04-20_phase2_first_production.md`.

**Recovery progress (authored 2026-04-21, updated 2026-04-21 23:50):**
- ✅ **Stage 1 (Z):** `/gsd-debug multitrait_coloc_empty` — RESOLVED. trait-pair coloc wired; filter_finemap_summary accepts status ∈ {"success","ok"} (commit 604938b).
- ✅ **Stage 1d:** `/gsd-debug trait_pair_coloc_hard_failures` — RESOLVED. chr:pos/rsid naming drift in coloc.susie (commit 335f514). SH2B3 EUR bmi↔hypertension PP.H4=1.0 and htn↔stroke PP.H4=1.0 at canonical leads.
- ✅ **Stage 2:** `/gsd-debug susie_credible_set_yield` — NARROW VALIDATION COMPLETE. Identity-LD fallback fixed via 1000G EUR plink panel (5 commits a6e3214 / 6de9a88 / 7d54183 / 9102466 / 1635d37 + provenance 0948a76). SH2B3_12q24 EUR now produces 4 purity=1.0 CS at published leads. **BLOCKED on Carter firing LSF production re-fit** (cmd sequence in .planning/debug/susie_credible_set_yield.md "CHECKPOINT REACHED"). Agent id a4908644fca7f85d9 still live for continuation. (NOTE 2026-04-22: the LSF production re-fit subsequently fired via `bin/fire_phase2_stage2_refit.sh` — returned 51/96 real-LD CS, 0 Tier A, triggering the 2026-04-22 genome-wide reframe. Recovery narrative is now historical.)
- ✅ **Stage 3 first-pass (Y):** FTO+IRX3 and SH2B3+ATXN2 distal-gene additions (commit 05c968b, pre-registered in .planning/DECISIONS.md + OSF pending). FTO_16q12 EUR IRX3/Pancreas produced best_qtl_pph4=0.3099 -- below Tier thresholds. BRAP + IRX5 deferred to second-pass pending Stage 2 re-fit results.
- ⏳ **Stage 4:** `/gsd-execute-phase` tail + `/gsd-verify-work` + CP#1-final decision [2-3 hrs, after LSF fire]. (NOTE 2026-04-22: CP#1-final reframed by pivot; Stage 4 closure subsumed by Track A manuscript push and M0 closeout.)

**Post-LSF fire decision matrix (per RECOVERY_PLAN Step 4.3):** Tier A >= 5 -> continue T2 (MR + PGS + Nature Genetics narrative); 3-4 -> continue T2 with pQTL expansion; 1-2 -> targeted investigation (all 49 GTEx tissues + pQTL); 0 -> AJHG fallback (genuine null after fixing all three structural gaps). (NOTE 2026-04-22: observed 0 Tier A → triggered pivot to Track A real-LD audit (Genome Medicine / AJHG short report / Bioinformatics) + Track B genome-wide discovery (Nature Genetics). See Amendment §2.2.)

**Scope caveat for CP#1-final framing:** Stage 2 fix covers 10 EUR autosomal curated regions. HLA_6p21 + BMI_Xq24 + all AFR regions remain on the legacy identity-LD fallback (the LDSC-landed 1000G panel is EUR-autosomal-only). AFR Tier A candidates are handicapped pending a matched-ancestry LD panel; worth flagging in the CP#1 framing / limitations section. (NOTE 2026-04-22: superseded — AFR LD panel now sourced from All-of-Us controlled-tier WGS (~100k) per Amendment §5; 1000G AFR N=661 deprecated as the AFR default.)

**T1 spine status:** Phases 0/1/2/5/9 code-complete; Launch15 drained 9/9 (2026-04-19) — pathway branch CLOSED. CP#1-final is blocked on Phase 2 recovery (this plan). (NOTE 2026-04-22: T1 spine outputs repurposed as Track A inputs + Track B candidate-locus validation subset per Amendment §8; CP#1-final retired as a gate.)

Legacy progress: ██░░░░░░░░ 17% (pre-pivot T1 frame)

## Performance Metrics

**Velocity:**

- Total plans completed: 15
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 02 | 5 | - | - |
| 05 | 5 | - | - |
| 09 | 5 | - | - |

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
| Phase 09 P01 | 23min | 3 tasks | 16 files |
| Phase 09 P02 | 11min | 5 tasks | 14 files |
| Phase 09 P03 | 13 | 2 tasks | 7 files |
| Phase 09 P04 | 18min | 2 tasks | 8 files |
| Phase 09 P05 | 7min | 2 tasks | 11 files |
| Phase 04 P01 | 8min | 4 tasks | 14 files |
| Phase 04 P02 | 8min | 3 tasks | 6 files |
| Phase 04 P04 | 14min | 4 tasks | 7 files |
| Phase 04 P03 | 8min | 2 tasks | 6 files |
| Phase 04 P05 | 7min | 4 tasks | 9 files |

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
- [Phase 09]: MVP phs001672 enumerated: T2D + quantitative BP released; stroke/asthma/BMI NOT_RELEASED (resolves RESEARCH A1)
- [Phase 09]: MVP genome build is GRCh38 (not GRCh37 as plan draft); liftover_required flipped true
- [Phase 09]: MVP column_map uses dbGaP GWAS-central schema (|β| + Coded Allele) not REGENIE; harmonizer must reconstruct signed β
- [Phase 09]: configfile: directive takes string literal; path is project-root-relative (matches top-level Snakefile)
- [Phase 09]: workflow.basedir resolves to project root; envs/ paths use Path(workflow.basedir)/'envs'/... (no .parent.parent)
- [Phase 09]: [Phase 09-02]: Schema-dispatching MVP harmonizer supports BOTH REGENIE-style (fixture) AND dbGaP GWAS-central (real phs001672); _detect_schema() routes on observed columns
- [Phase 09]: [Phase 09-02]: dbGaP signed BETA reconstructed from |β| + Coded Allele orientation via reconstruct_signed_beta() — sign=+1 when coded==EA, -1 when coded==OA
- [Phase 09]: [Phase 09-02]: Inline liftover per harmonizer (not a standalone rule); obsolete liftover_replication_sumstats rule removed; outputs write directly to harmonized_grch37/ aligning with 09-03 consumer paths
- [Phase 09]: [Phase 09-02]: Added liftover_coordinates helper to liftover.py (pyliftover-backed, lru_cache(maxsize=4)); avoids subprocess-per-row with the existing liftover_sumstats batch path
- [Phase 09]: [Phase 09-02]: Project convention sys.path.insert + flat-name imports used throughout (plan draft's from src.python.X would require __init__.py and conflict with phase2/phase5 test patterns)
- [Phase 09]: [Phase 09-02]: GBMI harmonizer B-2 guard raises ValueError with expected-vs-observed columns listed when an ancestry stratum's prefix columns are absent; prevents silent empty AFR panel output
- [Phase 09]: [Phase 09-03]: Panel-driven manifest routing — build_replication_manifest reads config['panels'] directly so new cohorts appear in manifest via YAML change, not Python edit
- [Phase 09]: [Phase 09-03]: BBJ generalization gated by signal_scope='tier_ab_only' at config level (D-05c) — not hardcoded in Python
- [Phase 09]: [Phase 09-03]: run_replication_susie reuses Phase-1 susie_policy.yaml verbatim (D-08); simplified 2-stage retry ladder (vs Phase-1's 3-stage) because discovery fit has already been stabilised upstream
- [Phase 09]: [Phase 09-03]: winnerscurse pinned SHA 2ed00bb (amandaforde/winnerscurse); lazy-install via remotes::install_github on first run_fiqt.R call — no manual post-conda step (r-remotes already in envs/r_coloc.yml from Phase 0)
- [Phase 09]: [Phase 09-03]: se_FIQT column is passthrough=raw SE — winnerscurse emits only beta_FIQT; stable 2-col addition documents that SE of the corrected estimator equals raw SE to first order (formal shrinkage would need parametric bootstrap per row)
- [Phase 09]: [Phase 09-03]: FIQT tests require multi-row BH context — single-row inputs at z=1.5 cannot exhibit shrinkage (BH is a no-op at n=1); tests use focal signal + 100-row null background
- [Phase 09]: [Phase 09-04]: Single tryCatch wrapping both readRDS + coloc.susie (T-09-16 uniform failure surface)
- [Phase 09]: [Phase 09-04]: Failure-path coloc JSON emits same sweep keys as success-path (no branching downstream)
- [Phase 09]: [Phase 09-04]: Per-cohort (not per-signal) output for compute_per_cohort_effect_size_test (single-source Bonferroni denominator)
- [Phase 09]: [Phase 09-04]: metafor::rma.uni(method='FE') over hand-rolled IVW (matches textbook to 4 decimals; gives QE/I^2 for free)
- [Phase 09]: [Phase 09-04]: IVW meta groups by (signal_id, cohort_ancestry); is_generalization=TRUE (BBJ) excluded per D-05c (T-09-17)
- [Phase 09]: [Phase 09-04]: collect_replication_effect_sizes.py materialized as standalone I-5 producer (plan iteration 2 revision)
- [Phase 09]: [Phase 09-04]: .rds fixtures committed via .gitignore exception (tests/**/fixtures/*.rds) for deterministic CI
- [Phase 09]: [Phase 09-04]: posthoc_power returns NaN on invalid input (distinguishes 'could not compute' from zero power)
- [Phase 09]: [Phase 09-05]: COJO --cojo-slct depends on pathway.smk .baseline_download_done (not .download_ldsc_baseline.done — plan draft's assumed flag path differs from pathway.smk's emit)
- [Phase 09]: [Phase 09-05]: I-3 per-cohort sample_overlap_flag implemented via KNOWN_OVERLAP_PAIRS dict with ('*', cohort) wildcard fallback; 6 cohorts (incl. bbj) emit flag columns for QC traceability
- [Phase 09]: [Phase 09-05]: Gotcha #1 COJO-N=503 caveat enforced at 3 layers (shell WARN stderr / pytest assertion on '4000'+'WARN' tokens / methods-doc narrative); COJO framed TIER-2 supplementary, not primary replication
- [Phase 09]: [Phase 09-05]: Added aggregate_per_cohort_combined rule to unblock ivw_meta_aggregate (Plan 09-04) + assemble_replication_holdout_supplementary (Plan 09-05) — Plan 09-04 docstring promised aggregator but no rule produced it (Rule 2 fix)
- [Phase 04]: bootstrap_fits_root on /rs1 allocation to avoid GPFS quota pressure
- [Phase 04]: NCSU LSF standard queue: 1024 concurrent slots per user (resolves A-1 compute concern)
- [Phase 04]: Root tests/conftest.py created with phase4/5/9 markers (no root conftest existed)
- [Phase 04]: SE-inflation formula: SE_matched = SE_EUR * sqrt(N_EUR / N_AFR) per D-01a; Phase 1 run_susie_rss.R reused verbatim via subprocess; AFR .fit.rds held immutably fixed per D-01c
- [Phase 04]: BH-FDR applied across all 35 r_g tests jointly (D-04c); SE>0.3 flagged not excluded (A-2); D-05 NCP framework is original-research construction (B-2 resolution)
- [Phase 04]: Tier A criterion: max(pph4)>=0.8 AND any(pph4>=threshold) across signal rows; Jaccard over union of all CS variants per dataset
- [Phase 04]: H7 verdict uses >= semantics at 20pp boundary (boundary = power_artifact); frozen in test
- [Phase 04]: Per-bootstrap retention emitted as additional output from existing retention rule (not separate rule)
- [Phase 04]: Negative-control test uses pytest.skip when tier_assignments.tsv absent or lacks is_negative_control column
- [Phase 02 first-production, 2026-04-20]: `rule all_qtl_coloc` lists `QTL_COLOC_PER_ID_JSONS` directly (not via `aggregate_qtl_coloc.input`) so Phase 2 firing is explicit and does not transitively break `all_pathway` (Phase 5 relies on empty tier_assignments → aggregate_qtl_coloc must stay manifest-only input)
- [Phase 02 first-production, 2026-04-20]: Manifest builder is single source of truth for identifier conventions — `TRAIT_ALIASES` (htn→hypertension) + `GENE_SYMBOL_TO_ENSEMBL` (11 genes) applied at manifest-build time, not at harmonize-time. Downstream scripts stay decoupled.
- [Phase 02 first-production, 2026-04-20]: pQTL rows keep gene SYMBOL as `gene_id` (UKB-PPP file naming uses symbols); eQTL/sQTL/sc-eQTL emit ENSG. Polymorphic by `qtl_source`. `gene_symbol` column added for traceability (additive, non-breaking).
- [Phase 02 first-production, 2026-04-20]: NEW `BUG-AUDIT-12` surfaced — sQTL + sc-eQTL downloads expect eQTL-Catalogue QTD IDs; manifest emits tissue/cell-type names. Scoped OUT of Stage B.5. Next manifest-builder campaign.

### Pending Todos

None yet.

### Blockers/Concerns

- DEF-01-04: GRCh38 liftover of config/regions_curated.csv required before build_hgdp_1kg_ld can execute end-to-end. Resolution targeted at Plan 01-04 or 01-05.
- DEF-RO7-01: `build_ld_rds` in `src/snakemake/rules/ld_reference.smk` requires `data/raw/1kg/TRANS.samples` which no rule produces. Pre-existing. Surfaced during Phase 5 smoke dry-run. Blocks g:Profiler branch + all_pathway aggregate.
- DEF-RO7-02: pathway.smk expand() iterates `config.trait_ancestries` beyond what's harmonized on disk; `harmonize_sumstats` raises on missing combos (e.g., bmi/AFR). Blocks per-branch smoke testing of MAGMA / LDSC partitioned / LDSC-SEG / HESS.
- DEF-RO7-03: `config/pipeline.yaml` `paths.harmonized_sumstats` points to wrong dir (`data/processed/sumstats_harmonized` vs actual `data/processed/region_analysis/sumstats_harmonized_fixed/`). Will surface after DEF-RO7-02 is resolved.
- **Decision 2026-04-13:** Phase 5 real-data smoke testing deferred to Phase 9 planning window. Pathway.smk DAG wiring confirmed correct (RO7); remaining blockers are all upstream/config issues surfaced by deeper DAG resolution. Will re-address when Phase 0/1/2 data paths are re-exercised for replication cohorts. Details: `.planning/quick/260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps/deferred-items.md`.
- DEF-09-02-01: Pre-existing phase2 test collection failures in 3 files (ModuleNotFoundError: tests). Not caused by Wave 2; logged in deferred-items.md
- **BUG-Phase2-too-few-snps (active):** `run_qtl_coloc.R` can't match SNP names between harmonized TSV (`chr16_53766288_C_T`) and Phase 1 SuSiE fit's internal variant roster. 3 hypotheses in `.planning/debug/t1_phase2_first_production.md` (unnamed variants / coloc.susie API drift / variant-ID format). PRIMARY blocker for CP#1-final real numerics.
- **BUG-AUDIT-12 (active):** Manifest emits tissue/cell-type names where sQTL + sc-eQTL eQTL-Catalogue downloads expect QTD IDs. Requires lookup table. Scoped out of Stage B.5.
- **BUG-AUDIT-11 (active):** sdy passing path for pQTL — `--sdy 1.0` hardcoded in coloc CLI may override per-variant estimate from harmonize_pqtl.py. Needs investigation post-smoke.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260413-ro7 | Fix Phase 5 Snakemake DAG wiring gaps | 2026-04-13 | bfb04f8 | [260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps](./quick/260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps/) |
| 260413-vtk | Fix 3 file-path bugs in Phase 9 plans | 2026-04-14 | ea9ddd2 | [260413-vtk-fix-3-file-path-bugs-in-phase-9-plans](./quick/260413-vtk-fix-3-file-path-bugs-in-phase-9-plans/) |
| 260414-clp | Fix genome-build config mismatch (Finding 1 from Phase 9 smoke) | 2026-04-14 | fb61c40 | [260414-clp-fix-genome-build-config-mismatch-in-phas](./quick/260414-clp-fix-genome-build-config-mismatch-in-phas/) |
| 260414-qhr | Fix Phase 0 download rule idempotency (LDSC baseline preflight + MAGMA binary symlink) | 2026-04-14 | e936aea | [260414-qhr-fix-phase-0-download-rule-idempotency-1-](./quick/260414-qhr-fix-phase-0-download-rule-idempotency-1-/) |
| 260414-qsk | Batch idempotency guards across 3 remaining Phase 0 download rules (magma_ref + ldsc_seg + hess_panel) | 2026-04-14 | 8b66203 | [260414-qsk-batch-idempotency-hardening-across-4-rem](./quick/260414-qsk-batch-idempotency-hardening-across-4-rem/) |
| 260414-rbv | Fix Phase 5 conda env path bug in pathway.smk (3-level `..` escaped project root; surfaced live by `--use-conda`) | 2026-04-14 | 0f1f248 | [260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa](./quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/) |
| 260414-tmq | Batch fix Phase 5 bugs from bmi.EUR magma_fdr scout (30 script-path `..` escapes + r-msigdbr added to gprofiler.yml + in-place env augment) | 2026-04-14 | 2414ea9, e193896 | [260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm](./quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/) |
| scout-260414-bmi-magma | bmi.EUR magma_fdr scout (halted 2/8 jobs; magma_annotate produced 107 MB real output; 9 Phase 5 issues found) | 2026-04-14 | 04f3629 | [260414-bmi-magma-scout](./quick/260414-bmi-magma-scout/) |
| 260414-uqf | Update download_msigdb for msigdbr 26 API + KEGG_LEGACY pick; relax r-msigdbr/r-base pins (closes scout issue #8) | 2026-04-14 | 9cc6d49 | [260414-uqf-update-download-msigdb-rule-for-msigdbr-](./quick/260414-uqf-update-download-msigdb-rule-for-msigdbr-/) |
| 260414-v4r | Pre-stage Yengo BMI: cnsgenomics throttle blocked download; pivoted to mtime-touch on existing harmonized .bgz; scout DAG 8→4 jobs (closes scout issue #9 functionally) | 2026-04-15 | _no-code_ | [260414-v4r-pre-stage-yengo-2018-bmi-eur-sumstats-ma](./quick/260414-v4r-pre-stage-yengo-2018-bmi-eur-sumstats-ma/) |
| 260414-vro | Accept SNP_ID column alias in run_magma.py (closes scout bug #10 surfaced in v8) | 2026-04-14 | 7a3aa5a | _code-only_ |
| 260414-ww3 | Resume bmi.EUR magma_fdr scout v8 — docs-only; scout v9 already reached 3/3 after vro, producing bmi_EUR_geneset_fdr.tsv (9617 rows; top hit CUSTOM_APPETITE_REGULATION q=7.25e-11). MAGMA branch of Phase 5 proven end-to-end on real data. | 2026-04-15 | _docs_ | [260414-ww3-resume-bmi-eur-magma-fdr-scout-v8-re-lau](./quick/260414-ww3-resume-bmi-eur-magma-fdr-scout-v8-re-lau/) |
| 260414-wzy | Env yml hardening: dropped `defaults` channel from 6 yamls (python_stats, magma, ldsc_py3, plink, qtl_processing, r_coloc); hess_py27 kept (Py2.7 only on defaults). New `bin/setup-envs.sh` with direct-mamba fallback for libmamba 2.5 interop bug. envs/README.md rewritten with pitfalls section. Closes scout issues #4/#5/#6/#7. | 2026-04-15 | 60d3c2f | [260414-wzy-env-yml-hardening-remove-defaults-channe](./quick/260414-wzy-env-yml-hardening-remove-defaults-channe/) |
| 260423-nzu | Post-pivot hygiene: commit Stage 2 drivers, refresh STATE.md, archive Phase 03 MR plans | 2026-04-23 | 11b75ad..ca018b4 | [260423-nzu-post-pivot-hygiene-commit-stage-2-driver](./quick/260423-nzu-post-pivot-hygiene-commit-stage-2-driver/) |
| 260423-osk | Route B M0 closeout: rewrite PROJECT/ROADMAP/REQUIREMENTS to M0–M6; append 5 DECISION entries | 2026-04-23 | d9c9905..880fc36 | [260423-osk-route-b-m0-closeout-rewrite-project-road](./quick/260423-osk-route-b-m0-closeout-rewrite-project-road/) |
| 260424-mxp | Route B M0 follow-through: lock ClinVar SHA-256 + scaffold 4 M5-deferred catalog rows in data/catalogs/catalog_lock_manifest.tsv; promote Amendment §9.3 to standalone OSF paste-ready text (posting gated on M1 per §9.1) | 2026-04-24 | 0a1339e..fd1836e | [260424-mxp-draft-osf-amendment-snapshot-novelty-catalog](./quick/260424-mxp-draft-osf-amendment-snapshot-novelty-catalog/) |
| 260424-j6c | Route C sumstats manual-fetch status refresh: reconcile SUMSTATS-MANUAL-FETCH-STATUS.md against 2026-04-24 disk state; all 23 Track B M1 destinations still absent; 0 new SHA-256 locks; static manifest untouched | 2026-04-24 | 98604aa | [260424-j6c-route-c-sumstats-manual-fetch-status-ref](./quick/260424-j6c-route-c-sumstats-manual-fetch-status-ref/) |
| 260424-j64 | Route A Step 2.2.b Introduction R1 for track_a_pivot.md — align to TRACK-A-PIVOT.md §4.5 (swap opaque ²⁰⁻²² ref range to `[Wallace 2021] [Zou 2022] [Weissbrod 2020]` inline placeholders resolve-at-2.2.f; add §4.5 P3 "can *produce* apparent overlap" inflection); zero forbidden terms in Intro. Walk-through brief for remaining Route A steps 2.2.e/2.2.f/2.3/2.4 at `NEXT-STEPS.md` | 2026-04-24 | 9c28f83 | [260424-j64-route-a-step-2-2-b-introduction-rewrite-](./quick/260424-j64-route-a-step-2-2-b-introduction-rewrite-/) |

## Session Continuity

Last session: 2026-04-24T15:10:00Z
Stopped at: Route B M0 is now fully shipped on `main` — both the scaffolding rewrite (260423-osk, d9c9905..880fc36) and the M0 follow-through (260424-mxp, 0a1339e..fd1836e) are merged. `data/catalogs/catalog_lock_manifest.tsv` locks ClinVar `2026-04-20_weekly_release` with SHA-256 `3be993...58e`; the remaining 4 comparators (Pickrell 2016 supplement, GWAS Catalog, Open Targets Genetics L2G, Watanabe 2019 GWAS Atlas) are M5-deferred with URL + version anchors. `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` holds the paste-ready OSF body behind `--- PASTE INTO OSF FROM HERE ---` markers with 3 intentional placeholders (M1 completion date, M1 commit hash, M5 lock commit hash). Remaining Route B human-action items: **(1) Route B Step 3.3 — Carter manually paste the amendment into osf.io/az52u at M1 closeout** (now fully unblocked: paste-ready text + ClinVar anchor on main; follow the pre-paste checklist at the top of OSF-AMENDMENT-TEXT-2026-04-22.md), then append DEC entry + STATE.md row + repo tag `M1-OSF-AMENDMENT-POSTED-YYYY-MM-DD`; **(2) M5 catalog lock refresh** — at M5 cross-reference date, populate SHA-256 for the 4 deferred catalogs per `data/catalogs/README.md` handoff. Also still outstanding from snappy-humming-pine: Route A Step 2.2.b/e/f (Introduction + Discussion + References rewrites), 2.3 (3 figure scripts), 2.4 (bioRxiv preprint).

**2026-04-24 resume (parsed-plotting-lynx.md):** `/gsd-resume-work` executed; status loaded; no `HANDOFF.json` / `.continue-here` / interrupted agents. Carter picked three parallel routes for this session — **R1 (Route A manuscript push)** + **R3 (Route C sumstats manual-fetch status refresh)** + **R4 (M1 planning kickoff via `/gsd-discuss-phase m1-sumstats-upgrade-and-harmonization`)**. R2 (OSF pre-paste) explicitly deferred to M1 closeout per Amendment §9.1. Routing plan at `/home/ckclinto/.claude/plans/parsed-plotting-lynx.md`. Recommended serial order if single-terminal: R3 → R4 → R1; or fire in separate terminals (file sets are disjoint; STATE.md + DECISIONS.md writes must serialize).

### This session (2026-04-22 → 2026-04-23) — Pivot adoption + M0 scaffolding + hygiene

- **2026-04-22 AM:** Stage 2 production fire via `bin/fire_phase2_stage2_refit.sh` (51/96 real-LD credible sets, 0 Tier A, SH2B3 × asthma EUR identity-LD → real-LD collapse). Aggregator follow-up via `bin/followup_phase2_stage2_aggregators.sh` at 20:02 UTC.
- **2026-04-22:** Pivot adopted. 6 amendment docs authored under `.planning/amendments/`: `PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`, `TRACK-A-PIVOT.md`, `SUMSTATS-UPGRADE.md` + `.tsv`, `AOU-LD-PIPELINE.md`, `SUMSTATS-MANUAL-FETCH.md`.
- **2026-04-22 / 2026-04-23:** `bin/download_sumstats_v2.sh` driver + manifest committed (`cb2ed78`, `92a64ce`); Track A first-pass manuscript draft committed (`bde60e2`) at `docs/manuscript/track_a_pivot.md`.
- **2026-04-23:** Post-pivot hygiene via `/gsd-quick 260423-nzu` — Stage 2 drivers committed (11b75ad), STATE.md refreshed (0aa7030), Phase 03 MR plans archived as superseded by M5 (ca018b4).
- **2026-04-23 (later):** Route C M1 kickoff docs — SUMSTATS-MANUAL-FETCH-STATUS.md tracker + SUMSTATS-SCRIPTED-FETCH-COMPLETE.md note (f6d037a). All 27 scripted-URL sumstats downloads confirmed on-disk (40.4 GB, no stubs).
- **2026-04-23 (later):** Route A Step 2.1 — [TRACK-A-FROZEN-NUMBERS.md](./amendments/TRACK-A-FROZEN-NUMBERS.md) locked from Stage 2 artifacts (20b2a6a). Key numerics: 51/96 CS (vs 12/96 identity-LD, 4.25× yield), 0 Tier A / 0 Tier B / 9 Tier C (best PP.H4=0.3099 at FTO_16q12 EUR IRX3/Pancreas), 224 negative-control rows, 1274 QTL-coloc attempts (32 success = 2.5%). Flagged discrepancy: draft's 1446 / 861 pairwise-test claim does not match disk.
- **2026-04-23 (later):** Route A Step 2.2.a/c/d — `docs/manuscript/track_a_pivot.md` numeric reconciliation (05a701a). All 1446 / 861 citations removed; replaced with disk-verified Stage 2 splits. SH2B3 flagship reframed honestly — canonical BMI–hypertension / hypertension–stroke trait-pairs (PP.H4 = 1.00 under Stage 1d identity-LD) are absent from Stage 2 `coloc.susie` output manifest (consistent with credible-set collapse); supplementary re-fire pre-registered.
- **2026-04-23 (later):** Route B Step 3.1 via `/gsd-quick 260423-osk` — rewrote 4 planning docs to M0–M6 (d9c9905, cbbc6ae, 995275c, 880fc36). Pre-pivot Phase 00–11 archived verbatim in ROADMAP under `## Pre-pivot spine`. 5 new DECISIONS entries cover: candidate-locus abandonment, 9-trait phenotype locks, MTAG+CPASSOC selection, AoU-AFR egress-aware LD, two-track publication strategy.
- **Next (subsequent sessions):** Route A Step 2.2.b/e/f + 2.3 + 2.4 (Introduction rewrite, Discussion rewrite, References, 3 figure R scripts, bioRxiv preprint). Route B Step 3.3 OSF amendment submission (Carter web-UI action; gates M2). Route B Step 3.2 final STATE.md refresh once OSF posted. Then /gsd-plan-phase M1-sumstats-upgrade once ROADMAP entries route correctly.
- **Next:** Route A (Track A manuscript edits + Tier-count freeze) in foreground; Route C (sumstats downloads) ticking in background; Route B (M0 closeout — PROJECT/ROADMAP/REQUIREMENTS/DECISIONS rewrites + OSF amendment) gated on Route A Tier-count freeze.

### Archived sessions (pre-pivot)

All entries below pre-date the 2026-04-22 pivot. Retained for forensic traceability and because some procedural content (Phase 0 idempotency fixes, LDSC custom-LD-score fixes, env yml hardening) is still load-bearing on the T1 spine artifacts that Track A will cite.

### This session (2026-04-20) — Resume routing + Option 1/2/3 chain

1. **Plan approved** — `/home/ckclinto/.claude/plans/elegant-sprouting-sunrise.md` (3-option routing). Carter picked "all of the above, in order".
2. **STATE.md refresh** (this edit) — closes the 2026-04-17 → 2026-04-20 gap. See "Launch10-15 drain" and "Phase 2 Stage A/B.5" entries below.
3. **Option 1 next:** `/gsd-debug qtl_coloc_snp_name_mismatch` — see `.planning/debug/t1_phase2_first_production.md` for the handoff hypotheses (unnamed variants on SuSiE fit / coloc.susie API drift / variant-ID format mismatch).

### Launch10-15 drain (2026-04-17 → 2026-04-19)

Launch10-14 progressively fixed HESS/LDSC-partitioned/LDSC-SEG/SVD rank-deficiency bugs. Commits `030130b`..`a78f4d1`. Launch15 drained 9/9 on 2026-04-19. **Pathway branch CLOSED.** Only CP#1-final blocker is Phase 2 first-production.

### T1 Phase 2 first-production debug (2026-04-20)

- **Stage A** (commits `118bd67`, `028b50a`, `42580cf`): added `rule all_qtl_coloc` + parse-time `QTL_COLOC_OUTPUTS`; fixed pre-existing wildcard bugs in `qtl_download.smk` (`harmonize_pqtl_region` + `harmonize_onek1k_region`); polymorphic `_qtl_manifest_row_by_wildcards()`; conditional L2G gating. All three plan-prescribed verifications PASS. No regression in `all_pathway`.
- **Stage B.5** (commits `f8b784b`, `a7d4eac`, `07cf83a`): added `TRAIT_ALIASES = {"htn": "hypertension"}` + `GENE_SYMBOL_TO_ENSEMBL` (11 genes) in `build_qtl_coloc_manifest.py`, added `r-r.utils` to `envs/r_coloc.yml`. Manifest regenerated (1243 rows; gwas_trait distribution: hypertension 565, bmi 226, t2d 226, asthma 226 — NO `htn`).
- **eQTL smoke END-TO-END SUCCESS:** FTO/Adipose_Subcutaneous/bmi.EUR/16q12 → 2601 variants harmonized, valid JSON. BUT coloc returned `status: too_few_snps` / `n_snps_overlap: 0` — NEW downstream blocker in `run_qtl_coloc.R` (SNP-name format mismatch between harmonized TSV `chr16_53766288_C_T` and Phase 1 SuSiE fit). 3 hypotheses documented.
- **sQTL/sc-eQTL/pQTL smokes BLOCKED** on: (a) raw data not staged (`data/raw/gtex_v8_sqtl/`, `data/raw/onek1k/`, `data/raw/ukbppp/` missing); (b) NEW `BUG-AUDIT-12` — manifest emits tissue/cell-type names where sQTL + sc-eQTL downloads expect eQTL-Catalogue QTD IDs; (c) no `SYNAPSE_AUTH_TOKEN` for pQTL. Scoped OUT of Stage B.5 per checkpoint constraint.

### Archived prior session (2026-04-17 PM) — Phase 3 planning commit

1. **Phase 3 planning batch committed** — `2eb364f docs(phase-03): complete planning batch — 5 waves + validation contract` (7 files, +2248/-4). ROADMAP.md updated, 5 PLANs + 03-VALIDATION.md landed. Execution gated on CP#1-final (T1 first-production completion).

2. **T1 Launch10 status** (inspected 2026-04-17 14:20 EDT):
   - `logs/t1_production_relaunch10.log` modified 14:17:56 — actively writing
   - Progress: **225/287 steps (78%)**, 5 LSF jobs RUN in serial queue (job IDs 734688, 734652, 734719, 734717, 734726 submitted 11:33–11:34)
   - **Residual errors (4 rule types × 7 = 28 failed steps):**
     - `hess_combine` × 7 (asthma_stroke_EUR, t2d_asthma_EUR, plus 5 more pairs)
     - `ldsc_seg_gene_expr` × 7
     - `ldsc_seg_chromatin` × 7
     - `ldsc_partitioned_h2` × 7
     - plus `summarize_coloc_results` × 1, `ldsc_munge` × 1
   - Two latest HEAD commits targeting HESS (`385cadf` strip `_chr{chrom}` from out_prefix, `d33e1f6` LDSC weights repoint) were in scope but 7 hess_combine failures persist — needs separate diagnosis
   - Estimated ~2 hr to completion at ~2 min/job observed cadence

3. **Launch8/9/10 timeline now clear** (memory was stale — listed Launch9 as staged-but-not-fired):
   - Launch8: completed 2026-04-17 01:19 (Apr 16 PM start)
   - Launch9: completed 2026-04-17 11:29 (ran overnight after 4 pre-Launch9 fixes)
   - Launch10: started ~11:34 today after `385cadf` + `d33e1f6` landed, still running

### Recommended next-session moves

1. **Wait for Launch10 to drain** (est. ~2 hr from 14:20), or monitor via `tail -f logs/t1_production_relaunch10.log`.
2. **If Launch10 exits with the 28 failed steps unresolved:** 4 systematic bugs remain. Route to `/gsd-debug t1_launch10_failures` with the 4 rule types as in-scope. Likely candidates: `hess_combine` still not finding combined output (maybe `format_hess` output path vs `hess_combine` input path mismatch), LDSC-SEG and LDSC-partitioned-h2 may share a root cause in the custom annot pipeline.
3. **Once T1 clean:** Reissue CP#1-final with Tier A signal counts. Then `/clear` and `/gsd-execute-phase 3` (planning batch from this session).

### Earlier sessions (archived for reference)

### Previous session (2026-04-16 PM) — T1 Production Bug-Fix Sprint (archived)

**9 pipeline bugs diagnosed and fixed** across 5 commits + 3 in-place tool patches:

| # | Bug | Root Cause | Fix | Commit |
|---|-----|-----------|-----|--------|
| 1 | LDSC custom LD scores (22 failures) | `w_hm3.snplist` 3-col TSV, LDSC reads with comma sep | Extract 1-col SNP file | `04ea1cc` |
| 2 | HESS `--local-rhog` arg order | nargs=2 expects FILES, not chrom | `--local-rhog F1 F2 --chrom N` | `04ea1cc` |
| 3 | LDSC-SEG `.ldcts` path | Rule joined nonexistent subdir | Direct path + preserve subdirs in rewriter | `04ea1cc` |
| 4 | HESS sumstats missing CHR+BP | HESS requires 7 cols, we output 5 | Add CHR+BP from input | `5c0548b` |
| 5 | LDSC munge bmi.EUR no REF/ALT | Yengo 2018 lacks allele columns | Make REF/ALT optional, dummy alleles | `072de08` |
| 6 | LDSC munge chr:pos SNP IDs | 5 traits use chr:pos, not rsIDs | Build chr:pos→rsID lookup from 1kG bim (10M entries) | `bd789c1` |
| 7 | Dense-region SuSiE MissingOutput | R script skips but doesn't write .fit.rds | Write placeholder .fit.rds for skipped regions | `4efb9f8` |
| 8 | g:Profiler no HTTPS on compute | Compute nodes lack outbound internet | Switch to R gprofiler2 fallback (`--use-r`) + fix conda env | `4efb9f8` |
| 9 | HESS AFR no LD panel | AFR plink bfiles not staged | Scope HESS to EUR-only via `hess_ancestries` config | `4efb9f8` |

Plus 3 in-place patches to `tools/ldsc/ldsc.py` (Py3 compat):

- `"wb"` → `"w"` for `.M` and `.M_5_50` file writes
- `traceback.format_exc(ex)` → `traceback.format_exc()`
- `sumstats.cell_type_specific` → `sumstats.estimate_cell_type_specific_heritability`

**Relaunch7 results** (27 completions from relaunch6 + 19 from relaunch7):

- MAGMA: 8/8 COMPLETE (all trait×ancestry through FDR)
- SuSiE: 93/96 JSON + 96 .fit.rds (3 dense-region still running)
- LDSC custom LD scores: 18/22 chroms (chr 1-4 failed before in-place fix)
- LDSC munge: 2/8 (asthma_AFR + asthma_EUR; others blocked by chr:pos or REF/ALT)

**Relaunch8 launched** (PID 3962749, `logs/t1_production_relaunch8.log`):

- 394 jobs targeting `all_pathway`
- HESS: 220 EUR-only (was 286)
- LDSC: 5 LD score chroms + 8 munge (rsID remapping) + 8 h2 + 16 SEG
- SuSiE: 96 re-runs (updated R script with .fit.rds placeholder)
- g:Profiler: 1 enrichment + 1 negative controls (R fallback)

### Previous session (2026-04-15 PM)

1. **Phase 4 research (B → A → C priority, F1 verdict-table format, G3 alternatives-no-pick policy)** — gsd-phase-researcher returned:
   - **B-1 CONFIRMED** — SE-inflation bootstrap (Zou 2022 SuSiE-RSS + MultiSuSiE 2025 support independent-Z + fixed-R refit)
   - **B-2 CONTESTED** — D-05 Hou 2023 citation error: PMC10403901 resolves to PMC11120833 = *radmix* paper, no NCP framework. OSF pre-reg does not name Hou → internal CONTEXT.md fix, not an OSF deviation
   - **B-3 CONTESTED** — 20pp H7 threshold has no literature precedent; defensible only because pre-registered (changing requires OSF amendment)
   - **A-1 CONTESTED** — compute envelope scales 5-60 weeks depending on LSF concurrent-core quota; pilot run (100 fits ≈ 1 hr) needed before full launch
   - **A-2 CONTESTED** — standard LDSC cannot compute cross-ancestry r_g per author FAQ; need **S-LDXR / Popcorn / cov-LDSC**. AFR sample sizes (stroke ~24k, asthma ~15k) above 5k minimum but SE>0.3 expected
   - **C-1 SUPERSEDED** — Pan-UKBB AFR BMI (N~6k) → **MVP phs002453 (N~55.5k, dbGaP public 2024-07-22)** or **AoU BMI AFR (N~54.9k)**, both ~9× larger; SE-inflation goes from 10.8× (noise-dominated) to 3.55× (comparable to other 4 traits)
   - Open: Mahajan 2022 §6 SE-inflation PDF verification; MVP phs002453 DAR status; D-05 NCP framework original source (Hou 2019? Hormozdiari 2020? Pasaniuc-Price 2017? this study's construction?); NCSU LSF concurrent-core quota

### Recommended next-session moves (in order)

1. **`/gsd-discuss-phase 4`** — resolve B-2 / A-2 / C-1 amendments to 04-CONTEXT.md. Menu picks come from the alternatives column of 04-RESEARCH.md §Verdict Table. Do NOT touch B-1 / B-3 (B-1 CONFIRMED; B-3 pre-reg-locked). A-1 becomes a planning-layer pilot-run task, not a CONTEXT amendment.
2. **Before discuss-phase**, resolve 2 researcher-unreachable questions: (a) verify MVP phs002453 DAR status (open vs DAR-gated) via dbGaP; (b) check NCSU LSF concurrent-core quota to calibrate A-1 pilot estimate.
3. After discuss-phase → **`/gsd-plan-phase 4`** — references amended CONTEXT.md + RESEARCH.md.
4. In parallel: **first-production LSF launch** of T1 Phases 0→1→2 end-to-end — required to produce Tier A signal counts for CP#1-final. Does not block Phase 4 planning.
5. After first-production T1 completes → reissue **CP#1-final** with numeric Tier A counts + cross-ancestry concordance magnitude.

### Earlier in this session (2026-04-15 AM)

1. **ww3** — bmi.EUR magma_fdr scout closed (v9 reached 3/3; 9617 FDR rows; top hit CUSTOM_APPETITE_REGULATION q=7.25e-11). Commit `7f97a20`.
2. **wzy** — Env yml hardening: `defaults` channel dropped from 6 yamls, `bin/setup-envs.sh` added with direct-mamba fallback for libmamba 2.5 interop bug, envs/README.md rewritten with 4-item Pitfalls section. Closes scout issues #4/#5/#6/#7. Commit `60d3c2f`.
3. **Phase 5 validation audit** — Retroactive `05-VALIDATION.md` reconciled: 8→10 task rows, all ⬜→✅ green (100/100 pytest pass in 53.2s), Manual-Only expanded 3→10 with scout-gap integration. Commit `489d6af`.
4. **CP#1 interim review** — `.planning/checkpoints/T1_review.md` issued with conditional-go verdict. T2 research + planning authorized in parallel with T1 first-production LSF launch. Decision rule for submission target (NG vs AJHG) recorded pre-data at 3 Tier A thresholds.

### Earlier in this session (2026-04-14 PM)

### Finding 2026-04-14 PM — Phase 0 idempotency gap

Dry-run inspection of Phase A narrow-scout targets revealed:

- `download_ldsc_baseline` rule (src/snakemake/rules/pathway.smk:180-237) re-fetches 4 large tarballs (~5 GB total) from `broad-alkesgroup-ukbb-ld.s3.amazonaws.com` + GCS `requester-pays` paths. Manually-staged data IS on disk (`data/reference/ldsc/baselineLD.{1..22}.{annot.gz,l2.M,l2.M_5_50}`, `data/reference/ldsc/eur_w_ld_chr/w_hm3.snplist`, `data/reference/ldsc/w_hm3.snplist`) but the rule's flag file `data/reference/ldsc/.baseline_download_done` doesn't exist, so Snakemake re-runs.
- `download_magma_binary` rule expects `tools/magma_v1.10/magma` which doesn't exist; Carter's manual download landed at `data/reference/magma/magma`. Path mismatch + JS-gated CNCR upstream.
- `harmonize_sumstats` chains `download_sumstats` for 8 trait/ancestry combos (bmi.EUR, t2d.EUR, t2d.AFR, hypertension.EUR, asthma.EUR, asthma.AFR, stroke.EUR, stroke.AFR). Raw sumstats not on disk. Multiple URL-rot risk.
- Existing harmonized .bgz files (Feb 11 timestamps, ~2.3 GB at `data/processed/region_analysis/sumstats_harmonized_fixed/`) would be overwritten because `config/datasets.yaml` mtime is newer.

**Decision:** No real-data execution until Phase 0 download rules are made idempotent (skip-if-on-disk semantics) AND the magma binary path is reconciled. Routed to `/gsd-quick`.

### What landed during 2026-04-14 sessions

**Phase 9 closeout:**

- 5/5 plans executed + verified (`human_needed` for real-data UAT)
- Code review: 13/13 critical+warning findings fixed (commits 57bd450..94333af)
- Security audit: 22/22 threats closed (T-09-01 re-disposed `mitigate` → `accept` per HPC + open-public + HTTPS justification, see 09-SECURITY.md)
- Strategy A pre-flight smoke: TCF7L2/T2D × 4 cohorts PASS, β=0.23-0.32 same-direction GWAS-significant (see 09-SMOKE.md)
- 4 quick tasks executed: 260413-ro7 (DAG wiring), 260413-vtk (file path bugs), 260414-clp (genome build config) + Option β trait_ancestries trim (commit 084d22f)

**Phase 0 first-production data infrastructure (this session, 2026-04-14):**

- 1kG Phase 3 VCFs chr1-22 + chrX (~17 GB) downloaded via NCBI mirror (EBI URL was broken — workaround captured) — `data/raw/1kg/vcf/`
- LDSC reference data (~17 GB extracted): baseline v2.2 ldscores + bedfiles (bzip2-mislabeled-as-tgz pitfall handled), plinkfiles (1000G EUR), weights HM3 (EUR + EAS), frq, snplist, eur_w_ld_chr, Multi_tissue_gene_expr + chromatin (LDSC-SEG) — `data/reference/ldsc/` (Carter manually downloaded from Zenodo + scp'd; Broad GCS requires auth)
- MAGMA 4 files (570 MB): static binary v1.10, NCBI37.3 gene loc, g1000_eur (bed/bim/fam), dbsnp151.synonyms — `data/reference/magma/` (Carter manually downloaded from CNCR + scp'd; CNCR uses JS gate that blocks curl)
- HESS partition bed files (EUR/AFR/EAS, from Bitbucket ldetect-data) — `data/reference/hess/partition/`
- HESS LD panel — symlink farm `data/reference/hess/ld_panel/EUR/chr{1..22}.{bed,bim,fam}` → LDSC's 1000G_EUR_Phase3_plink/ extracted plinkfiles (66 symlinks; same data, different naming convention)
- HESS source code cloned to `tools/hess/`
- DEF-RO7-03 fix on disk: symlink `data/processed/sumstats_harmonized` → `region_analysis/sumstats_harmonized_fixed`

**Resumption pointers:**

- `.planning/phases/09-replication-in-independent-cohorts/09-PHASE0-LAUNCH.md` — full Phase 0 launch report + 5 URL-rot findings
- `.planning/phases/09-replication-in-independent-cohorts/09-SMOKE.md` — Phase 9 pre-flight smoke report (TCF7L2/T2D × 4 cohorts) + 4 findings
- `.planning/phases/09-replication-in-independent-cohorts/09-HUMAN-UAT.md` — 3 deferred items for real-data execution

**Open items (all deferred, none blocking):**

- `data/raw/1kg/TRANS.samples` generator — VCFs exist, panel file exists, just need a script to produce sample-list union (DEF-RO7-01)
- t2d.TRANS Phase 1 SuSiE rule wiring — config drops TRANS for t2d during smoke; `results/fine_mapping/susie/*.TRANS.*.json` rule path needs investigation
- Missing trait×ancestry ingestion: bmi/AFR + bmi/EAS + hypertension/AFR + hypertension/HIS + stroke/EAS + t2d/EAS — Phase 0 D-20 work
- `config/pipeline.yaml` `onekg.ftp_base` cosmetic update from broken EBI to working NCBI mirror

**Recommended next-session moves (in order):**

1. Narrow real-data execution: `snakemake harmonize_sumstats download_msigdb` etc. — exercises a few rules against real data, ~10-30 min, catches latent runtime bugs
2. Or: target a single Phase 5 branch end-to-end (e.g., `snakemake magma_fdr` for EUR traits) — ~30-60 min compute
3. Or: full LSF launch of `snakemake all_pathway --cores N` — multi-hour compute, first-production
4. Address open items above as they become blocking

Resume file: (retired — 2026-04-22 pivot; see `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3)

## Phase 0 Closeout Artifacts (2026-04-10)

- **Code review fixes:** 8 findings fixed in commits 6e3dc66..81ab1eb, report at .planning/phases/00-data-access-infrastructure/00-REVIEW-FIX.md (commit 1d5ed54)
- **UKB-PPP Synapse access:** Carter certified 2026-04-10 (15/15 quiz), syn51364943 accessible, s3://ukbiobank.opendata.sagebase.org/ confirmed (commit 8b846b9)
- **FinnGen R12 registration:** submitted 2026-04-10 via elomake.helsinki.fi, actual release is R12 (not R13/R14 as earlier research assumed), bucket finngen-public-data-r12 (commit e912c0c)
- **deCODE portal verification:** email-gated ephemeral download link mechanism, 24,271 SOMAmer files / ~24 TB total (vs 4,907 aptamers in README — anomaly flagged for Phase 2). Ferkingstad 2021 confirmed. 3 test files downloaded to /rs1/researchers/c/ckclinto/coloc_analysis/data/raw/decode_pqtl/ (CRYBB2, RAF1, ZNF41 — all 909-910 MB, gzip-intact). README schema bug: actual column 9 is `minus_log10_pval` not `min_log10_pval`. Commits 4ce2972, 12ec691, 0901230
- **OSF pre-registration:** DOI 10.17605/OSF.IO/PVB5J, public (no embargo), submitted 2026-04-10, linked project osf.io/az52u. Title: "Mechanistic resolution of pleiotropy at cardiometabolic loci...". Framed as original hypothesis-driven research per feedback memory. Draft at .planning/osf_prereg_draft.md. Commits e459563, 18995f0
- **CI smoke test scaffolding:** dry-run verified 2026-04-10T23:14:00Z (29 jobs, 11 rules). 5 scaffolding bugs caught and fixed: (1) validate() schema path, (2-4) 3 include: paths, (5) FINEMAP_OUTPUTS/SUMMARY definition order. Python 3.13 + Snakemake 7.32.4 PEP 701 incompatibility discovered — dev env at /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/ (Python 3.11 + snakemake 7.32.4 + pulp<2.8). First real execution deferred to Phase 1. Commit c213f58
- **Security audit:** SECURED 10/10 threats closed. Report at .planning/phases/00-data-access-infrastructure/00-SECURITY.md. 3 accepted risks (AR-00-01 config non-secrets, AR-00-02 portal registrations, AR-00-03 UCSC chain file). Commit 2030821
