# PROJECT.md — coloc_analysis

> **North-star documents:** [`Revision_Plan.md`](../Revision_Plan.md) (559-line
> revision strategy) and [`GSD_BRIEFING.md`](../GSD_BRIEFING.md) (independent
> evaluation + T1/T2/T3 tiering + 11 gaps). Read both before touching anything
> else. Everything in this file is a condensed restatement of those two.

## Who

**Author / sole owner:** Carter K. Clinton, ASHES Lab, North Carolina State
University. **Solo author.** No internal co-author review. Rigor comes from
multi-method triangulation, pre-registration (OSF), and hold-out replication.

## What

Cross-ancestry colocalization analysis of **5 cardiometabolic traits** (BMI,
type 2 diabetes, hypertension, stroke, asthma) at **~50 pleiotropic loci**. The
draft manuscript (`ajhg_manu_v10.pdf`) uses coloc.abf with EUR-heavy GWAS and a
small AFR fragment. A self-review plus independent Claude review both
concluded the current methods are weak for a high-impact venue. This project
is the revision.

**Target journals (in ranked order):**
Nature Genetics → American Journal of Human Genetics → Nature Metabolism →
Cell Genomics → Genome Medicine.

## Where

| Path | Role |
|---|---|
| `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` | **Canonical repo** (this directory). Git root. GSD state lives under `.planning/`. |
| `/rs1/researchers/c/ckclinto/coloc_analysis/` | Upstream data root. Symlinked from `data/` and `results/legacy/`. 77 GB historical backup tarball lives here. |
| `/rs1/researchers/c/ckclinto/miniconda3/` | Miniconda3 install. `gsd-tools` conda env has the GSD plugin. |
| NCSU HPC (LSF scheduler) | Compute. `bsub` for job submission. |
| GPFS `/gpfs_common/` | Shared filesystem. **Worktree isolation is known-bad here — use `mode: solo` with `git.isolation: branch` in GSD.** |

## Why (in one paragraph)

The current manuscript frames the study as a pleiotropy catalog. A competent
reviewer at Nature Genetics / AJHG will flag: (1) single-causal-variant
assumption via coloc.abf, (2) ad-hoc pathway enrichment without a formal
statistical test, (3) cross-ancestry concordance mixing incomparable trait
pairs at the same locus, (4) corrupted supplementary tables with inconsistent
signal counts, (5) no replication in independent cohorts, (6) no causal
direction test (MR), (7) no formal selection-scan test of the evolutionary
medicine hypothesis, and (8) a hand-weighted ML scorecard with no train/test
split. The revision converts the paper from a descriptive catalog into a
**mechanistically resolved cross-ancestry framework** with three integrated
spines: coloc.susie + 3-way QTL coloc → causal gene + tissue assignment;
bidirectional MR → causal direction; matched-N cross-ancestry + LDSC
partitioned heritability + selection scans → rigorous evolutionary / equity
story.

## Constraints

- **100% public data.** No wet-lab, no functional validation, no proprietary
  or industry datasets. Standard academic DUAs for UK Biobank, UKB-PPP,
  deCODE, FinnGen, MVP, All of Us, BBJ, Pan-UKBB, etc.
- **Solo author.** Rigor must come from multi-method triangulation,
  pre-registration on OSF, Snakemake-pinned pipeline, hold-out replication —
  not from internal QC.
- **Timeline is not a binding constraint.** Rigor and impact matter more than
  speed. Do not compress phases to save time.
- **No web/JS stack.** Relevant stack is R (`coloc`, `susieR`, `TwoSampleMR`,
  `MRPRESSO`, `hyprcoloc`), Python (LDSC, PRS-CSx, selscan, Enformer / Borzoi
  inference), bash, Snakemake, conda. Skip any skill pack aimed at React /
  Next / Vite / TypeScript.
- **Data access lead times are the real critical path.** UKB-PPP, deCODE,
  FinnGen, MVP, All of Us, BBJ, Pan-UKBB require DUAs that take weeks to
  months. These must run in parallel with Phase 0 from Day 1 (REQ-1).
- **GPFS filesystem.** Do **not** use worktree isolation. GSD mode is
  `solo` with `git.isolation: branch`.

## Goals for this GSD-managed revision

1. Execute all **T1 spine phases** (Phase 0 → 1 → 2 → 5 → 9) to the
   acceptance bar of AJHG minimum / Nature Genetics ambition.
2. At **Checkpoint #1** (end of T1), decide whether to proceed with T2
   (Phases 3, 4, 8) for a Nature Genetics pitch or submit to AJHG with T1.
3. At **Checkpoint #2** (end of T2), decide whether to add T3 (Phases 6, 7,
   10) for Nat Genet cover-letter hooks or submit to Nature Metabolism /
   Cell Metabolism with T1+T2.
4. Close every one of the 11 gaps in `GSD_BRIEFING.md` §5.2 via the
   requirements in `REQUIREMENTS.md`.
5. Deliver a reproducible GitHub release with Zenodo DOI, Snakemake pipeline
   + pinned conda envs + Docker/Singularity containers, OSF pre-registration,
   and a hold-out replication table.

## Current status

**Phase 0 (Data Access & Infrastructure):** Complete. Snakemake skeleton with
CI smoke test, data access DUAs (UKB-PPP, FinnGen, deCODE), OSF pre-registration.

**Phase 1 (SuSiE Fine-Mapping):** Complete. coloc.susie pipeline with EUR
(UKBB-LD) and AFR (HGDP+1kG) LD panels, 3-step retry ladder, pairwise SuSiE
coloc, sweep/summary dashboard.

**Phase 2 (3-way QTL Colocalization):** Complete (2026-04-13). Full QTL coloc
pipeline: GTEx v8 eQTL (49 tissues) + sQTL + UKB-PPP pQTL + OneK1K sc-eQTL
(14 immune cell types). Unified run_qtl_coloc.R with manifest-driven dispatch.
PP.H4 threshold sweep {0.5, 0.7, 0.8, 0.9} (REQ-3). Negative controls — 3
curated sets + 500 distance-matched nulls (REQ-7). Tier A/B/C confidence
assignment. Open Targets L2G concordance. Gene x tissue x cell-type matrix.
136 tests passing. 4 human verification items deferred to real-data execution.

**Phase 5 (Pathway + Partitioned Heritability):** Complete (2026-04-13). Multi-method
pathway enrichment replacing ad-hoc fold-enrichment: MAGMA gene-based + gene-set
enrichment, g:Profiler with discoverability-matched 5-trait union background (Reimand
2019), LDSC partitioned heritability per pathway (baseline v2.2), LDSC-SEG tissue-
specific enrichment (GTEx 53-tissue + Roadmap chromatin), HESS/rho-HESS local genetic
covariance with pleiotropic vs background z-test. Negative controls (HLA, cosmetic,
blood group) validated across all methods (REQ-7). 1000 permutation null gene sets
matched for size/LD/MAF. Cross-method aggregator with consensus ranking. Methods
fragment with 6 canonical citations. 100 tests passing. 37 Snakemake rules.

Last updated: 2026-04-13
