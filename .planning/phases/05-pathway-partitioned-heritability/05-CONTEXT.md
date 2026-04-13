# Phase 5: Pathway + Partitioned Heritability - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the ad-hoc fold-enrichment from the original manuscript with multi-method, properly null-controlled pathway analysis tied to heritability. This is the T1 pathway spine that converts "genes at pleiotropic loci are enriched for metabolic pathways" from a hand-waving claim into a statistically defensible result with FDR-corrected p-values, heritability fractions, tissue-specific enrichment, and local genetic covariance.

Scope includes: MAGMA gene-based + gene-set enrichment, g:Profiler with discoverability-matched background, LDSC partitioned heritability per pathway, LDSC-SEG tissue-specific heritability enrichment, HESS/rho-HESS local genetic covariance, permutation null for colocalization gene lists, and negative-control pathway validation (REQ-7).

Consumes: Phase 1 coloc.susie results (.fit.rds), Phase 2 gene x tissue x cell-type matrix, Phase 2 tier assignments, config/negative_controls.yaml gene sets. Requires full GWAS summary statistics for all 5 traits.

</domain>

<decisions>
## Implementation Decisions

### D-01: Pathway databases for MAGMA gene-set enrichment
- **D-01a:** Standard 4 databases: KEGG, Reactome, GO Biological Process, MSigDB Hallmark. These are the field standard per de Leeuw 2015 and cover >15,000 gene sets. FDR correction across all sets per trait.
- **D-01b:** 8 custom cardiometabolic pathway sets included alongside standard 4: insulin signaling, appetite regulation, glucose metabolism, fatty acid metabolism, inflammation, vascular tone, lipid transport, energy storage. These test the core "pathway-defined metabolic syndrome" thesis directly. Joint FDR correction with standard sets.
- **D-01c:** GWAS Catalog trait-associated gene sets NOT included — inflates test burden without adding mechanistic insight. Standard + custom sets are sufficient.

### D-02: HESS/rho-HESS scope
- **D-02a:** HESS included in Phase 5 (not deferred). Computes local genetic covariance — quantifies how much trait-pair genetic correlation concentrates at colocalized loci vs the polygenic background. This is the strongest test of whether the "pathway-defined metabolic syndrome" claim is real.
- **D-02b:** Run rho-HESS per trait pair x ancestry. Moderate compute cost (~1 run per trait pair x ancestry).
- **D-02c:** Compare HESS local covariance at pleiotropic loci vs genome-wide average. Report as ratio or z-score.

### D-03: g:Profiler background design
- **D-03a:** 5-trait union background: genes within 500 kb of any genome-wide significant SNP across ALL 5 traits (BMI, T2D, hypertension, stroke, asthma). This is the conservative Reimand 2019 standard — controls for "this gene was discoverable because it was near a GWAS hit for anything."
- **D-03b:** Electronic GO annotation filtering enabled (removes computationally inferred annotations, keeping only experimentally validated).
- **D-03c:** Input gene list: colocalization-derived genes from Phase 2 tier assignments (Tier A + B genes, i.e., genes with PP.H4 >= 0.8 for at least one QTL source).

### D-04: LDSC baseline model
- **D-04a:** Baseline v2.2 (Gazal 2017): 97 annotations including coding, UTR, promoter, enhancer, H3K marks, DHS, FANTOM5. Current field standard.
- **D-04b:** EUR LD scores from 1000G Phase 3. Multi-ancestry LD scores (S-LDXR) not used — adds complexity without clear benefit for the T1 submission.
- **D-04c:** Custom pathway gene sets added as binary annotations on top of the baseline model. Each pathway set is a 0/1 annotation: SNPs within 100 kb of any gene in the set.

### D-05: LDSC-SEG tissue annotations
- **D-05a:** GTEx v8 53-tissue RNA-seq gene expression annotations AND Roadmap Epigenomics chromatin state annotations. This is the Finucane 2018 standard.
- **D-05b:** Test whether pleiotropic loci preferentially fall in tissues shared between trait pairs (e.g., pancreas for BMI-T2D, vascular smooth muscle for hypertension-stroke).
- **D-05c:** Single-cell annotations (OneK1K, Tabula Sapiens) NOT included in Phase 5. Phase 7 (single-cell + EpiMap + ABC) handles cell-type resolution if T3 is triggered.

### D-06: Negative controls (REQ-7 extension)
- **D-06a:** Reuse Phase 2 negative control gene sets (HLA immune, cosmetic, blood group) from config/negative_controls.yaml for pathway enrichment testing.
- **D-06b:** All 3 negative-control sets must produce enrichment q > 0.05 in every enrichment test (MAGMA, g:Profiler, LDSC partitioned). This is the REQ-7 acceptance criterion for Phase 5.
- **D-06c:** Permutation null: 1000 random gene sets matched for length, LD, and MAF against the colocalization-derived gene list. Existing sample_null_loci.py (Phase 2) provides the matching infrastructure — extend to gene-set-level matching.

### D-07: Software versions
- **D-07a:** MAGMA v1.10 (de Leeuw 2015, latest stable as of 2025).
- **D-07b:** g:Profiler via official REST API (gprofiler2 R package or Python client).
- **D-07c:** LDSC v1.0.1 (Bulik-Sullivan 2015, Python 2/3 compatible fork if needed).
- **D-07d:** HESS from Shi et al. 2017 GitHub (Python).
- **D-07e:** All tools pinned in conda env specs per REQ-9.

</decisions>

<specifics>
## User Specifics

- The 8 custom cardiometabolic pathways must be defined as a separate annotation file (not embedded in code). Gene lists curated from literature (insulin signaling = INSR, IRS1, IRS2, PIK3CA, AKT1, AKT2, etc. per standard KEGG pathway definitions).
- Legacy pathway_enrichment_genomewide.py (src/legacy/) has 19 hand-curated pathways with 3 categories — these may partially overlap with the 8 custom sets but are NOT directly reusable (no statistical test, no null).
- The "pathway-defined metabolic syndrome" thesis is the core mechanistic claim of the paper. Phase 5 must produce evidence that either supports or refutes it — not assume it's true.

</specifics>

<deferred>
## Deferred Ideas

- Multi-ancestry LD scores (S-LDXR) for cross-ancestry partitioned heritability — revisit at Phase 9 replication or Checkpoint #1.
- Single-cell tissue annotations for LDSC-SEG — handled by Phase 7 (T3) if triggered.
- PASCAL pathway-level summary statistics — mentioned in Revision_Plan software list but not in success criteria. Could add as supplementary in Phase 11.
- Per-trait g:Profiler backgrounds (separate background per trait) — could be a supplementary sensitivity analysis in the manuscript.

</deferred>

<canonical_refs>
## Canonical References

These files MUST be read by downstream agents (researcher, planner):

- Revision_Plan.md (lines 185-204) — Phase 5 detailed spec with methods and expected outputs
- GSD_BRIEFING.md (gap #7) — Negative control requirement for pathway enrichment
- .planning/REQUIREMENTS.md (REQ-7) — Negative-control acceptance criteria for Phase 5
- config/negative_controls.yaml — Phase 2 negative control gene sets (reuse for Phase 5)
- config/pph4_thresholds.yaml — PP.H4 threshold config (defines Tier A/B/C input to gene list)
- src/python/sample_null_loci.py — Phase 2 null locus sampler (extend for gene-set matching)
- src/python/assign_tiers.py — Tier assignment logic (input gene list comes from Tier A+B)
- src/python/build_gene_tissue_matrix.py — Gene-tissue matrix (Phase 5 validates tissue specificity via LDSC-SEG)
- src/legacy/region_analysis/genome_wide_analysis/scripts/pathway_enrichment_genomewide.py — Legacy pathway enrichment (what we're replacing)

Key papers:
- de Leeuw 2015 PLoS Comput Biol (MAGMA)
- Reimand 2019 Nat Protoc (g:Profiler best practices)
- Finucane 2015 Nat Genet (LDSC partitioned heritability)
- Finucane 2018 Nat Genet (LDSC-SEG)
- Gazal 2017 Nat Genet (baseline v2.2)
- Shi 2017 AJHG (HESS)
- Bulik-Sullivan 2015 Nat Genet (LDSC)

</canonical_refs>
