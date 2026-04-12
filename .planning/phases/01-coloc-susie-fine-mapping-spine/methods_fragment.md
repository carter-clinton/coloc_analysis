# Phase 1 Methods Fragment -- coloc.susie Fine-Mapping Spine

Prepared for Phase 11 manuscript assembly. This fragment replaces the coloc.abf
methodology language in the original draft. Phase 1 establishes the fine-mapping spine
that enables downstream QTL coloc (Phase 2), pathway heritability (Phase 5),
and replication (Phase 9).

Original research framing: this is Carter K. Clinton's hypothesis-driven
cross-ancestry colocalization study at the ASHES Lab, NCSU. Phase 1 converts
the analysis from a descriptive pleiotropy catalog into a mechanistically resolved
cross-ancestry framework by replacing the single-variant ABF coloc backend with
multi-signal SuSiE-based fine-mapping and colocalization.

## SuSiE-RSS fine-mapping

Fine-mapping uses SuSiE-RSS (Wang et al. 2020; Zou et al. 2022) via the susieR R
package (v0.14.2) with the default Sum of Single Effects model L=10, coverage=0.95,
and the retry ladder specified in config/susie_policy.yaml (primary fit at
max_iterations=100; retry at max_iterations=200; regularization with
ld_regularization_eps=1e-4; terminal non-converged state retained for QC review
but excluded from Tier 1). Per-region fits are persisted as .fit.rds files so
coloc.susie consumes them without re-fitting, a substantial cost saving relative to
the susie_rss dispatch default.

## Pairwise colocalization

Pairwise coloc uses coloc::coloc.susie (coloc v5.2.3) against the cached SuSiE
fit objects. Output is a pairwise PP.H4 posterior per credible-set pair; the
best pairwise row (max PP.H4.abf) is surfaced in a legacy-compatible JSON schema
alongside the full pairwise array (susie_pairs) for downstream consumption.
Per-variant SNP.PP.H4 is interpreted conditionally on the pairwise PP.H4 > 0.5
(coloc vignette a06_SuSiE).

## Sensitivity analyses

The min_abs_corr sweep at {0.1, 0.5, 0.9} is computed post-hoc via
susie_get_cs(fit, min_abs_corr=...) -- no refit, zero cost. Results are reported
as a supplementary sensitivity table for the four pre-specified complex regions
and for any additional data-flagged regions (L_saturated or n_CS >= 3 at default
min_abs_corr=0.5).

## LD reference panels

A hybrid per-ancestry LD strategy is used:

- **EUR:** Weissbrod et al. 2020 UKBB-LD tiled reference panel (AWS Open Data
  Registry s3://broad-alkesgroup-ukbb-ld/UKBB_LD/), constructed from
  approximately 337,000 unrelated UK Biobank "white British" participants.
  Panel is tiled into 2,763 x 3 Mb windows; per-region submatrices are
  extracted via numpy/scipy with anonymous HTTPS S3 access. For the HLA_6p21
  region (chr6:25000000-35000000, ~10 Mb), the panel spans multiple tiles and
  cross-tile LD is unavailable. A block-diagonal approximation is used,
  flagged in output metadata as ld_source="ukbb_ld_tiled_block_diagonal", and
  surfaced prominently (red) in the per-locus QC dashboard. This is a known
  limitation of tile-partitioned LD references.

- **AFR:** HGDP+1kG merged panel (gnomAD v3.1.2 phased haplotypes v2; public
  HTTPS). AFR samples (n = 1003 in metadata, 986 after BCF reconciliation)
  are extracted from the gnomAD metadata table; per-curated-region BCF slices
  are streamed via bcftools and LD is computed locally via plink2
  --r-phased square.

- **EAS, SAS, AMR:** 1000 Genomes Phase 3 (legacy Phase 0 panel). AMR panel
  sample size (n ~ 347) is the smallest of the five ancestries; this is
  disclosed as a methods caveat.

### UKBB-LD substitution note (OSF amendment)

The OSF pre-registration (DOI 10.17605/OSF.IO/PVB5J, submitted 2026-04-10)
locks in "Pan-UKBB in-sample LD" for EUR. This was revised during Phase 1
implementation (2026-04-11) to use Weissbrod 2020 UKBB-LD tiled reference
(G6 locked decision) rather than Pan-UKBB raw BlockMatrix. Justification:

1. **Same underlying cohort.** UKBB-LD tiled is computed from ~337K UK
   Biobank "white British" individuals -- the same underlying EUR cohort as
   Pan-UKBB's in-sample LD.
2. **Operational tractability.** UKBB-LD is ~170 GB NPZ format; Pan-UKBB raw
   BlockMatrix is ~14.1 TB and requires Hail/Java. UKBB-LD fits inside a
   standard conda environment with numpy + scipy + boto3.
3. **Alignment with modern fine-mapping stacks.** echoLD, mapgen, and PolyFun
   all use this exact dataset as their EUR LD backbone.

Phase 2 may revisit the Pan-UKBB raw BlockMatrix option if the HLA block-diagonal
limitation has a material impact on HLA-trait colocalization results.

## Complex regions scope

Four of six pre-specified complex regions are analyzed in Phase 1:
9p21_CDKN2A, APOE_19q13, HLA_6p21, SLC2A9_urate. The OSF pre-reg originally
listed six regions; LPA/KIV-2 and the chr8 inversion are deferred to Phase 2
pending lipid and allergic-disease sumstats ingestion. The decision to narrow
from six to four is documented here as an OSF amendment against
DOI 10.17605/OSF.IO/PVB5J.

## Per-locus QC dashboard

All fine-mapping runs produce a D1 (z-score sanity: KS test, max|z|, lambda_GC)
+ D2 (convergence diagnostics: converged flag, niter, elbo_final, status from
retry ladder) + D3 (LD quality via susieR::kriging_rss n_outliers and max logLR)
+ D4 (credible-set purity and effective size via the post-hoc min_abs_corr
sweep using susie_get_cs) set of QC fields, aggregated into a single Quarto HTML
dashboard at results/finemap/qc_dashboard.html. Rows with non-converged status
or HLA block-diagonal LD are highlighted for manual review.

## OSF amendment text

Amendment against OSF DOI 10.17605/OSF.IO/PVB5J:

> Phase 1 of the registered analysis ("coloc.susie fine-mapping spine") is
> implemented with two deliberate methodological refinements relative to the
> pre-registered methods section:
>
> 1. **EUR LD reference substitution.** Pan-UKBB raw BlockMatrix in-sample LD
>    is replaced by Weissbrod et al. 2020 UKBB-LD tiled reference
>    (s3://broad-alkesgroup-ukbb-ld/UKBB_LD/), which is computed from the same
>    ~337K UK Biobank EUR cohort at per-3Mb tile granularity. This preserves
>    the scientific intent (in-sample EUR LD) while reducing compute and storage
>    requirements by two orders of magnitude. The HLA_6p21 region spans multiple
>    tiles and is handled via a block-diagonal approximation, flagged in the
>    per-locus QC dashboard and reported here as a known limitation.
>
> 2. **Complex-region scope.** Four of six pre-specified complex regions are
>    analyzed in Phase 1 (9p21_CDKN2A, APOE_19q13, HLA_6p21, SLC2A9_urate).
>    LPA/KIV-2 and the chr8 inversion region are deferred to Phase 2 pending
>    ingestion of lipid and allergic-disease sumstats, respectively.
>
> Both refinements are documented in .planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md
> and version-controlled in the project repository. Neither affects the primary
> T1 spine conclusions.

## Software and versions

- R 4.4.2
- susieR 0.14.2 (susie_rss for SuSiE-RSS fine-mapping)
- coloc 5.2.3 (coloc.susie for multi-signal colocalization)
- Snakemake 7.32.4 (pinned for Python 3.11 compatibility; PEP 701 incompatibility
  with Python 3.13 is a known issue)
- plink2 v2.00a5 or newer
- bcftools 1.21
- numpy 1.26, scipy 1.13, pandas 2.2, boto3 1.34
- Quarto 1.5.x (or R Markdown fallback)

## Regenerated expected results

tests/toy_3locus/expected/expected_results.yaml was regenerated from the first
real Phase 1 run on 2026-04-12 (see wave5_smoke_run.log). The toy dataset uses
synthetic fixture data for self-contained CI testing; real-data regression
baselines will be established when production data is populated.
