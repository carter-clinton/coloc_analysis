# Phase 2: 3-way QTL colocalization - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the causal gene x tissue x cell-type matrix through eQTL, pQTL, and sQTL colocalization with PP.H4 threshold sweep, negative controls, and tiered confidence assignment. This is the highest-leverage T1 phase — it converts raw coloc signals from Phase 1 into gene-level mechanistic assignments. Consumes Phase 1 `.fit.rds` outputs directly via `coloc::coloc.susie()`.

Scope includes: GTEx v8 eQTL (54 tissues) + UKB-PPP pQTL (cis-only) + GTEx v8 sQTL + OneK1K single-cell eQTL (14 immune cell types) + Open Targets Locus2Gene cross-reference + PP.H4 threshold sweep (REQ-3) + negative controls (REQ-7) + LPA/KIV-2 complex region reintroduction.

</domain>

<decisions>
## Implementation Decisions

### D-01: QTL data sources and scoping
- **D-01a:** GTEx v8 eQTL (54 tissues) as the backbone. All tissues, all loci — wide-net discovery, post-hoc filtering.
- **D-01b:** UKB-PPP pQTL (Sun et al. 2023, ~2,923 proteins, Synapse) as the primary pQTL source. cis-pQTL only, within the coloc window per locus. Sample size (~54K) and structured download justify selection over deCODE.
- **D-01c:** GTEx v8 sQTL included. Adds splice-level mechanistic layer (exon-skipping, intron retention).
- **D-01d:** deCODE pQTL (Ferkingstad 2021, ~4,907 aptamers) deferred to Phase 9 replication. Rationale: 24 TB ephemeral downloads, column-name bug (README says `min_log10_pval`, actual is `minus_log10_pval`), and overlapping coverage with UKB-PPP at the loci of interest. Slots cleanly into replication without touching the main pipeline.
- **D-01e:** OneK1K (Yazar 2022) single-cell eQTL included — all 14 immune cell types. Broad trigger: always run on all loci regardless of bulk GTEx results. A locus with both a bulk pancreas eQTL and a monocyte-specific OneK1K signal is more interesting than either alone. An unexpected basophil or pDC hit at a metabolic locus would be a finding.
- **D-01f:** OneK1K hits at PP.H4 >= 0.8 are tier-eligible. The tier system is QTL-source-agnostic — what matters is whether the causal gene and tissue/cell-type are resolved, not which dataset resolved them.

### D-02: Tier assignment logic
- **D-02a:** Primary operating threshold: PP.H4 >= 0.8 (Wallace 2021 convention, field expectation at AJHG/Nat Genet).
- **D-02b:** Sweep at {0.5, 0.7, 0.8, 0.9} reported as a supplementary sensitivity table showing tier count shifts per threshold. Not used for primary assignment.
- **D-02c:** Tier definitions are mechanistic and QTL-source-agnostic:
  - **Tier A:** Trait-trait coloc + QTL coloc resolves causal gene AND tissue/cell-type (PP.H4 >= 0.8 for both). QTL source can be GTEx eQTL, UKB-PPP pQTL, GTEx sQTL, or OneK1K.
  - **Tier B:** Trait-trait coloc + QTL evidence in at least one tissue but not all lines converge at >= 0.8.
  - **Tier C:** Trait-trait coloc only (no QTL support at the operating threshold).
- **D-02d:** `config/pph4_thresholds.yaml` to be created with sweep values and primary threshold.

### D-03: Tissue/protein filtering strategy
- **D-03a:** Wide-net with post-hoc filtering. All 54 GTEx tissues for all loci. Pre-filtering by biological hypothesis defeats the purpose of letting data assign causal tissues. An unexpected tissue hit is exactly the finding that differentiates Nature Genetics from confirmatory analysis.
- **D-03b:** pQTL: cis-only within the coloc window. No genome-wide pQTL sweeps.
- **D-03c:** Compute cost (hours vs. days on HPC) is not a meaningful constraint when timeline is not binding.

### D-04: Negative control design
- **D-04a:** Three curated gene/pathway sets:
  1. **HLA-immune** — known to produce false positives from long-range LD; tests the complex-region policy.
  2. **Cosmetic/non-cardiometabolic** — merged pigmentation + eye-color genes (OCA2, SLC24A5, MC1R, TYR, HERC2, IRF4). OCA2/HERC2 overlap makes them effectively one set.
  3. **Blood group antigens** — ABO, RH, FUT, KEL. Clean negative: well-mapped loci, strong GWAS signals, zero cardiometabolic mechanism, distinct LD structure from cosmetic loci.
- **D-04b:** Null threshold: PP.H4 < 0.8 (the primary operating threshold). A negative control should fail to reach Tier A. Requiring < 0.1 is unnecessarily strict and HLA will almost certainly violate it due to LD artifacts.
- **D-04c:** 100-1000 distance-matched random null loci for empirical calibration. Matched on gene density, LD block size, and MAF. The three curated sets test biological specificity; the matched nulls test statistical calibration. Together they answer different questions.
- **D-04d:** `config/negative_controls.yaml` to be created with all three curated sets + matched-null specification.

### D-05: Open Targets Locus2Gene integration
- **D-05a:** Independent corroborating evidence, NOT a hard validation gate. A concordance rate ("X% of Tier A assignments match L2G top gene") is a strong validation paragraph. Making L2G a gate means inheriting their training biases (distance-to-gene dominates L2G scores, penalizing distal enhancer-driven assignments).
- **D-05b:** Disagreements are findings, not failures. A well-resolved distal enhancer locus where three-way coloc points to a non-nearest gene is a story.
- **D-05c:** Bulk download (version-pinned Parquet from GCS) for reproducibility. No live API dependency.

### D-06: Complex regions
- **D-06a:** LPA/KIV-2 (6q25-26) brought back into Phase 2. Existing BMI-T2D anchor (PP.H4 = 0.990, rank 7 from Phase 1). KIV-2 copy number LD complexity flagged in complex-region policy; use HGDP+1kG AFR LD panel from Phase 1.
- **D-06b:** chr8 inversion (8p23.1) stays deferred. Primary biological motivation is allergic/atopic disease, not in current trait set. Running QTL coloc there without the right GWAS anchor produces a result disconnected from central narrative.
- **D-06c:** Update `config/susie_policy.yaml` complex_regions.pre_specified to include LPA/KIV-2 (5 regions total for Phase 2).

### Claude's Discretion
- QTL data harmonization pipeline design (column mapping, coordinate liftover if needed)
- Snakemake rule architecture for tissue-level dispatch (manifest pattern from Phase 1 coloc.smk)
- OneK1K data preprocessing pipeline details
- Distance-matched null loci sampling algorithm and parameter choices (within 100-1000 range)
- Open Targets L2G version selection and Parquet parsing approach

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 1 outputs (consumed by Phase 2)
- `src/snakemake/scripts/run_coloc_susie.R` — Phase 1 coloc output schema (JSON + .fit.rds); Phase 2 extends this schema
- `src/snakemake/rules/coloc.smk` — Manifest-driven dispatch pattern (lines 29-80); template for tissue-level coloc loops
- `config/susie_policy.yaml` — SuSiE policy reused for QTL fine-mapping; complex_regions list to be extended with LPA
- `.planning/phases/01-coloc-susie-fine-mapping-spine/01-CONTEXT.md` — Phase 1 locked decisions (G1-G6)
- `.planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md` — Phase 1 methods for Phase 11 continuity

### Project-level
- `Revision_Plan.md` §Phase 2 (lines 115-138) — mechanistic-resolution requirements, 3-way coloc spec
- `GSD_BRIEFING.md` §5.2 gaps #3, #7 — PP.H4 threshold sweep and negative controls
- `.planning/REQUIREMENTS.md` REQ-3 (PP.H4 sweep) and REQ-7 (negative controls)
- `.planning/data_access.md` — QTL data source access status (GTEx, UKB-PPP, deCODE)

### Config files to create or extend
- `config/datasets.yaml` — extend with GTEx/UKB-PPP/OneK1K entry stanzas
- `config/pph4_thresholds.yaml` — create: sweep {0.5, 0.7, 0.8, 0.9}, primary 0.8
- `config/negative_controls.yaml` — create: 3 curated sets + matched-null spec

### External data documentation
- deCODE column-name bug: README says `min_log10_pval`, actual column 9 is `minus_log10_pval` (documented in Phase 0 closeout)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Manifest-driven dispatch** (`coloc.smk` lines 29-80): `_coloc_manifest_row()` and `_fit_rds_for()` pattern directly applicable to tissue-level QTL coloc loops
- **coloc.susie output schema** (`run_coloc_susie.R` lines 88-146): JSON with PP.H0-H4, hit1/hit2, idx1/idx2. Extend with `qtl_source`, `qtl_tissue`, `mechanistic_tier` columns
- **SuSiE policy loader**: Already integrated in `run_susie_rss.R`; reuse for QTL fine-mapping
- **Filter/tier logic** (`filter_finemap_summary.py`): Extend for QTL-informed tier assignment; don't rewrite
- **QC dashboard aggregator** (`src/snakemake/scripts/aggregate_qc.py`): Pattern for QTL-level aggregation
- **Config schema validation** (`schemas/*.yaml` with `validate()`): Follow same convention for new config files

### Established Patterns
- **Snakemake rule chaining**: finemap.smk output -> coloc.smk input via manifest. Same pattern for GWAS fit -> QTL coloc.
- **Per-ancestry LD handling**: `{LD_REF_DIR}/{ancestry}/{region}.rds` pattern from Phase 1 ld_reference.smk
- **Conda env pinning**: `envs/*.yml` with exact versions; new env needed for pQTL/eQTL processing tools
- **Config-driven analysis**: All thresholds, paths, and parameters in YAML; no hardcoded constants

### Integration Points
- Phase 1 `.fit.rds` files are the primary input (SuSiE fitted objects per trait x ancestry x region)
- `config/pipeline.yaml` trait/ancestry matrix defines the analysis scope
- `src/snakemake/rules/multitrait.smk` pair manifest feeds the trait-pair dimension
- `results/finemap/` directory structure for output organization

</code_context>

<specifics>
## Specific Ideas

- **OneK1K as mechanistic differentiator:** When a pleiotropic locus shows both a bulk GTEx tissue hit AND a cell-type-specific OneK1K hit, report both — the intersection is more interesting than either alone. This is the asthma-metabolic axis story.
- **LPA/KIV-2 reintroduction:** PP.H4 = 0.990 for BMI-T2D already exists from Phase 1. Adding pQTL coloc at this locus directly strengthens a finding already being reported. Flag KIV-2 copy number LD complexity in output metadata.
- **L2G disagreement as narrative:** A distal enhancer locus where three-way coloc assigns a non-nearest gene while L2G picks the nearest gene is a finding worth featuring, not a QC failure.
- **Empirical null distribution:** The 100-1000 distance-matched null loci produce a null PP.H4 distribution for pathway enrichment that's far more convincing than three hand-picked gene sets alone.

</specifics>

<deferred>
## Deferred Ideas

- **deCODE pQTL integration** — deferred to Phase 9 replication. If reviewer requests broader aptamer coverage, deCODE slots in without pipeline changes.
- **chr8 inversion (8p23.1)** — deferred pending allergic-disease GWAS sumstats ingestion. No current trait anchor.
- **Broad single-cell eQTL catalogs beyond OneK1K** — CLUES, other scRNA-seq cohorts. Only pursue if OneK1K yields notable cell-type-specific hits that warrant replication.
- **hyprcoloc multi-trait colocalization** — Revision_Plan mentions this but it's a distinct analytical approach (simultaneous multi-trait, not pairwise). Could be Phase 2 or its own phase.

</deferred>

---

*Phase: 02-3-way-qtl-colocalization*
*Context gathered: 2026-04-12*
