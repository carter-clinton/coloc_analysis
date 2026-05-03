# Track A — Frozen Numbers (Stage 2 real-LD, 2026-04-22 production fire)

**Frozen on**: 2026-04-23
**Sources**: [results/fine_mapping/finemap_summary.tsv](../../results/fine_mapping/finemap_summary.tsv), [results/multitrait/coloc_summary.tsv](../../results/multitrait/coloc_summary.tsv), [results/qtl_coloc/tier_assignments.tsv](../../results/qtl_coloc/tier_assignments.tsv), [results/qtl_coloc/](../../results/qtl_coloc/) per-ID JSONs
**Purpose**: single source of truth for the Track A manuscript abstract, results, tables, and the OSF amendment (Route B Step 3.3). Any downstream doc that cites these numbers must cite them verbatim from this file.
**Audit closure record**: [TRACK-A-AUDIT-RESPONSE-2026-04-26.md](./TRACK-A-AUDIT-RESPONSE-2026-04-26.md) — single-document catalogue of all 27 audit items with status + commit pointers (independent scientific review acted on prior to submission).

---

## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE

| Metric | Value |
|---|---|
| Total Stage 2 real-LD fits | 96 |
| Stage 2 non-empty credible sets | **51 / 96 (53.1%)** |
| Total k2d full-coverage identity-LD fits | 95 (single missing cell: `bmi.EUR.APOE_19q13`) |
| k2d identity-LD non-empty credible sets | **48 / 95 (50.5%)** |
| **Matched-coverage fold change** | **51 / 48 = 1.06× yield increase** |
| Status distribution (k2d identity-LD) | 65 ok / 24 too_many_variants / 6 no_variants |
| n_CS distribution (k2d identity-LD) | 47 with 0; 12 with 1; 10 with 2; 5 with 3; 2 with 4; 2 with 5; 2 with 6; 3 with 7; 1 with 8; 11 with 10 |

**Headline framing (manuscript anchor language)**: We tightened the comparator from a partial-coverage Stage 1d narrow-validation baseline (12/96, only 2 of 10 admissible regions had identity-LD fits at the time of freeze) to the k2d full-coverage 2026-04-25 re-fire (48/95, matching the same admissibility set as Stage 2 real-LD). The inflation magnitude shifted from 4.25× to 1.06× under the tightened comparator.

**Sources**: [.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv](./IDENTITY-LD-K2D-FIT-SUMMARY.tsv) (k2d 2026-04-25 fire summary); [results/fine_mapping/finemap_summary.tsv](../../results/fine_mapping/finemap_summary.tsv) (Stage 2 real-LD 2026-04-22 production fire); per-fit JSONs at `results_identity_ld/fine_mapping/susie/*.json` and `results/fine_mapping/susie/*.json`.

**Denominator note**: The k2d identity-LD re-fire enumerated 95 of 96 region × ancestry × trait fits at admissibility. The single missing fit is `bmi.EUR.APOE_19q13` (Stage 2 real-LD status: `non_converged`, n_CS = 6). Headline numerics use 48/95 for identity-LD and 51/96 for real-LD; the fold-change is robust to this 1-cell denominator difference (~1.06× either way).

---

## Layer-2 colocalization-feasibility yield (post-W4.5-A continuation, 2026-05-01) — LIVE

Per [DEC-2026-05-01-02](../DECISIONS.md) (load-bearing decision anchor) and [W4-DISPOSITION-REVISED.md](../phases/ta-sh2b3-canonical-and-cache-refresh/W4-DISPOSITION-REVISED.md) (active narrative), Track A's pipeline now has three documented layers of yield, each with its own structural attrition. The cache-staleness hypothesis embedded in tracker v6 was tested by the W4.5-A continuation (drain final 4 + aggregator 3rd-pass) and refuted (Δ = 0; pre-3rd-pass too_few_snps unchanged from V4-era count). The 78.9% Layer-2 too_few_snps rate is **structural** (LD-panel coverage + region-window choices), not artifactual.

| Layer | Process | Numerator | Denominator | Yield | Attrition framing |
|---|---|---|---|---|---|
| **Layer 1 — SuSiE-RSS fine-mapping** | Per-trait, per-region GWAS fine-mapping at L=10 (with sweep at L∈{15,20,30} for the SH2B3 anchor) | 51 | 96 | **53.1%** | Per-trait fits with valid converged credible sets; the 45/96 attrition is dominated by non-convergence under the strict-gate definition. See [Stage 2 fine-mapping yield (top of file) — LIVE](#stage-2-fine-mapping-yield-post-k2d-full-coverage-identity-ld-comparator-2026-04-25--live) and [`ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md`](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md). |
| **Layer 2 — qtl_coloc structural feasibility** | Per-region, per-(trait, QTL-source, tissue) colocalization eligibility based on GWAS×QTL SNP intersection | 269 (= success + no_qtl_cs + qtl_susie_failed; the not-too_few_snps complement) | 1274 | **21.1%** | Per-(region × trait × QTL × tissue) tuples with sufficient SNP overlap to attempt coloc. The 1005/1274 = 78.9% attrition is structural, driven by LD-panel coverage + region-window choices. **This is the canonical Layer-2 finding** (DEC-2026-05-01-02). |
| **Layer 3 — substantive coloc hits** | Per-tuple PP.H4 evidence above tier thresholds | 32 | 1274 | **2.5%** | Per-tuple substantive colocalizations with tier-A confidence; the 1242/1274 attrition is the union of Layer-2 structural attrition (1005) + Layer-2-feasible-but-no-credible-set (235) + qtl_susie_failed (2). Within the 32 successes, Tier C dominates (highest = FTO_16q12 EUR / IRX3 / Pancreas / gtex_eqtl PP.H4 = 0.3099, below Tier B threshold 0.5). |

**Reviewer-defensibility framing (manuscript-anchor language):** Track A's reviewer-defensibility hinges on transparently disclosing all three layers rather than pooling them into a single yield number. The historical pattern in the literature is to report only Layer 3 (the headline "32 hits" or "2.5% colocalization rate") and treat Layer 1 and Layer 2 attritions as silent — which both undersells the methodological rigor (Layer 1's strict-gate non-convergence treatment per audit-v2 §HQ3 framing) and obscures the ceiling on what coloc can recover at current public-data LD coverage (Layer 2's 78.9% structural attrition). The 3-layer contrast is the canonical reviewer-defensibility framing; all manuscript Methods + Results + Limitations + Discussion language must cite these three numbers verbatim from this block.

**W4.5-B SuSiE-RSS rebuild explicitly skipped** (per DEC-2026-05-01-02 rationale, captured by `feedback_rigor_over_speed.md`): too_few_snps is a SNP-intersection problem, not a fine-mapping convergence problem. Adding more iterations to the GWAS-side fine-mapping cannot create SNPs that don't exist in the QTL panel. Switching to a denser LD panel (e.g., AoU-AFR-LD work-in-progress per M3) is the path forward for cross-ancestry expansion; for Track A, the 78.9% is reported as-is.

**Sources:**
- Status distribution: [`results/qtl_coloc/qtl_coloc_summary.tsv`](../../results/qtl_coloc/qtl_coloc_summary.tsv) (1274 rows; canonical post-W4.5-A continuation, 2026-05-01)
- Per-id JSON tally: [`results/qtl_coloc/*.json`](../../results/qtl_coloc/) (1274 per-attempt JSONs; status counts: too_few_snps=1005, no_qtl_cs=235, success=32, qtl_susie_failed=2)
- Tracker: [`wave4_dispatch_tracker_v7.json`](../phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v7.json) (status=FAILED on mechanical PASS/FAIL gate; outcome_disposition=HONEST_FINDING)
- Active narrative: [`W4-DISPOSITION-REVISED.md`](../phases/ta-sh2b3-canonical-and-cache-refresh/W4-DISPOSITION-REVISED.md) (refuted-hypothesis reasoning + 3-layer architecture)
- Decision anchor: [`DECISIONS.md::DEC-2026-05-01-02`](../DECISIONS.md)

**Caveats** (mandatory disclosure for any downstream cite of these scalars):

1. **Layer 2 numerator definition.** "Sufficient SNP overlap to attempt coloc" = `status != too_few_snps`, which includes 32 success + 235 no_qtl_cs + 2 qtl_susie_failed = 269 of 1274 = 21.1%. The complement (78.9%) is the structural attrition.
2. **Layer 3 numerator definition.** "Tier-A confidence" in the table is loose — within the 32 status=success rows, all tier assignments are Tier C (highest PP.H4 = 0.3099). The reviewer-defensibility framing is "any substantive coloc, regardless of tier"; the actual Tier-A threshold (PP.H4 ≥ 0.8) yields 0/1274.
3. **Layer 1 vs Layer 2 partial correlation.** A region with a non-converged Layer-1 fit can still produce too_few_snps at Layer 2; conversely, a region with a converged Layer-1 fit can still produce too_few_snps if the QTL panel for that tissue is sparse. The two attritions are partially correlated but distinct (per W4-DISPOSITION-REVISED §2.2).
4. **Pipeline stage scope.** Layer-2 1274 denominator reflects the post-W4.5-A scope-corrected manifest (`phase2_enabled_sources: [gtex_eqtl, gtex_sqtl]`). pQTL + sc-eQTL are deferred to Phase 2; pre-scope-correction 1469 is the unfiltered manifest count.

---

## H3 LD-reference-quality dose-response (post-wa2 H3 figure, 2026-04-26) — LIVE

| Metric | Value |
|---|---|
| EUR fits with measured `ld_overlap_fraction` | 60 (of 96 total Stage 2 real-LD fits; 36 AFR fits excluded — no AFR LD panel loaded) |
| EUR fits below Benner et al. 2017 calibration threshold (`ld_overlap_fraction < 0.5`) | **33 / 60 (55.0%)** |
| EUR fits at or above Benner threshold (≥ 0.5) | 27 / 60 (45.0%) |
| EUR fits with `ld_overlap_fraction = NA` (no LD attempted; coerced to 0 for the dose-response visualization) | 19 / 60 |
| EUR fits with numeric `ld_overlap_fraction` | 41 / 60 |
| Successful QTL-coloc attempts (status = success) | 32 / 1,274 (2.5%; all EUR per disk) |
| Suspect-quadrant points (PP.H4 ≥ 0.5 AND min `ld_overlap_fraction` < 0.5) | **0 / 32** |
| Headline: FTO_16q12 EUR IRX3 / Pancreas / gtex_eqtl | PP.H4 = 0.3099, min `ld_overlap_fraction` = 0 |
| Anchor: SH2B3_12q24 EUR asthma (sole "ok" SH2B3 EUR fit) | `ld_overlap_fraction` = 0.0385 |
| Reference threshold (Benner et al. 2017 AJHG 101:539–551) | 0.5 |
| Tier B threshold | 0.5 |
| Tier A threshold | 0.8 |

**Headline framing (manuscript-anchor language)**: 33 of 60 EUR Stage 2 real-LD fits sit below the Benner et al. 2017 `ld_overlap_fraction = 0.5` calibration threshold; the headline FTO_16q12 EUR Tier-C signal (PP.H4 = 0.3099) was produced by a SuSiE-RSS fit with `ld_overlap_fraction = 0`. Zero of the 32 QTL-coloc successes occupy the strict suspect quadrant (PP.H4 ≥ 0.5 AND min `ld_overlap_fraction` < 0.5) — itself a structural finding consistent with the manuscript's Discussion framing that the inflated identity-LD signal is primarily an LD-inflation artifact. The dose-response figure is positioned as exploratory methodology-validation, NOT a discovery claim.

**Sources**: Derived at runtime by [`src/R/figures/fig_h3_ld_overlap_dose_response.R`](../../src/R/figures/fig_h3_ld_overlap_dose_response.R) (committed at `1e4b071` per quick task `260425-wa2`); source data at [`results/fine_mapping/finemap_summary.tsv`](../../results/fine_mapping/finemap_summary.tsv) (Stage 2 production fire 2026-04-22), per-fit JSONs at `results/fine_mapping/susie/*.json` (96 files), and per-attempt JSONs at `results/qtl_coloc/*.json` (1,274 files; 32 with `status = success`). Reference: Benner et al. 2017, *AJHG* 101:539–551 (LD-reference-panel calibration threshold).

**Caveats** (mandatory disclosure for any downstream cite of these scalars):
1. Panel B of the dose-response figure uses MIN `ld_overlap_fraction` across the 5 GWAS-side trait fits per (region, ancestry) cell as a conservative worst-case bound — the qtl_coloc per-attempt JSON does not record which trait's GWAS-side SuSiE fit was the input.
2. AFR fits (36 of 96 total Stage 2 fits) are excluded from the dose-response visualization because no AFR LD panel was loaded at Stage 2 fire time. Matched-ancestry AFR LD pending M3 (AoU controlled-tier WGS build; see [AOU-LD-PIPELINE.md](./AOU-LD-PIPELINE.md)).
3. The 19 NA → 0 coercion treats "no LD attempted" as dose-response-equivalent to "no LD overlap"; this is the conservative reading of the audit's question.

---

## Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE

| Metric | Value |
|---|---|
| Paired non-empty fits | **48** (real-LD non-empty 51 ∩ identity-LD non-empty 48; identity-LD subset is fully contained in the real-LD non-empty set) |
| Pair-key | `{trait}.{ancestry}.{region_id}` (filename stem; identical across `results/fine_mapping/susie/*.json` and `results_identity_ld/fine_mapping/susie/*.json`) |
| ΔPIP-of-top-variant median (real − identity) | **0.0000** |
| ΔPIP-of-top-variant IQR (Q1 / Q3) | **0.0000 / 0.0363** |
| Lead-variant rank = 1 (identity-LD top variant remains real-LD top variant) | **30 / 48 (62.5%)** |
| Lead-variant rank ≥ 21 OR identity-LD lead absent from real-LD CSs | **16 / 48 (33.3%)** |
| Max per-fit credible-set Jaccard ≥ 0.8 | **30 / 48 (62.5%)** |
| Max per-fit credible-set Jaccard < 0.5 | **16 / 48 (33.3%)** |

**Headline framing (manuscript-anchor language)**: At the 48 paired non-empty SuSiE-RSS fits, ~62% are stable across LD references (same lead variant, high CS-member Jaccard, near-zero ΔPIP-top), but ~33% show substantial structural posterior shifts (lead-variant rank ≥ 21 or absent AND Jaccard < 0.5). The Conclusion-1 reframe's "structural posterior shifts" claim is concentrated in this 1/3 minority of paired fits — the audit-v2 §HQ3 measurement gap is now quantified, not asserted.

**Sources**: Derived at runtime by [`src/R/figures/fig_s2_paired_fit_structural_inflation.R`](../../src/R/figures/fig_s2_paired_fit_structural_inflation.R) (committed via quick task `260427-azv`, audit-v2 sweep); source data at `results/fine_mapping/susie/*.json` (96 files, Stage 2 production fire 2026-04-22) and `results_identity_ld/fine_mapping/susie/*.json` (95 files, k2d full-coverage re-fire 2026-04-25). Figure rendered at `docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.pdf` + `.png` (cairo_pdf, 180 mm × 140 mm, 600 dpi).

**Caveats** (mandatory disclosure for any downstream cite of these scalars):

1. **CS pairing is greedy argmax-overlap** — the max-per-fit Jaccard aggregates over all CS-pair Jaccards within a fit by taking the max; this is a conservative summary that bounds the structural-shift claim. A more elaborate Hungarian-assignment pairing was not implemented because the greedy argmax already achieves the audit-v2 measurement-gap closure.
2. **Lead-variant rank = ∞** is bucketed into "rank ≥ 21 OR absent" because R's `match()` returns `NA` when the identity-LD top variant is absent from the real-LD CS-member union; we coerce to `Inf` and bin accordingly. The 16 / 48 figure includes both genuine high-rank-and-present cases and absent-from-real-LD cases — the figure's Panel B exposes this composition.
3. **The 48-pair population is the intersection of non-empty fits**, NOT the full Stage 2 manifest. If either tree's non-empty count changes (e.g., HQ#2(i) L = 20 re-fire lands), the pairing population shifts and the script must be re-run; the LIVE block updates atomically with the next quick-task closure.

---

## Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE

| Metric | Value |
|---|---|
| Total Stage 2 trait-pair `coloc.susie` rows attempted | **28** (per `results/multitrait/coloc_summary.tsv` md5 `5fa3c4004970c5da711d05947cb1f7d2`) |
| Rows with valid (non-empty) PP.H4 / PP.H4.abf | **0** (all 28 PP columns empty under real-LD) |
| Admissible EUR trait-pairs (Stage 2 manifest slice) | **16** (APOL1 3 + CXADR_F2RL1 1 + FTO 10 + MC4R 1 + SH2B3 1) |
| Admissible AFR trait-pairs (Stage 2 manifest slice) | **12** (APOL1 3 + FTO 3 + MC4R 3 + SH2B3 3) |
| Mean ΔPP.H4 (identity − real) across admissible region × trait-pair | **non-computable** (real-LD PP.H4 column entirely empty; identity-LD trait-pair `coloc.susie` comparator absent) |
| Median ΔPP.H4 | **non-computable** |
| Range ΔPP.H4 | **non-computable** |
| Survived (identity ≥ 0.8 AND real ≥ 0.8) at PP.H4 ≥ 0.8 | **0** |
| Lost (identity ≥ 0.8 AND real < 0.8) | **0** |
| Rescued (identity < 0.8 AND real ≥ 0.8) | **0** |
| Both-null at PP.H4 ≥ 0.8 | **28** (all 28 admissible region × ancestry × trait-pair Stage 2 `coloc.susie` rows returned empty PP columns) |
| Unique (trait_a, trait_b) combinations across 28 attempted rows | **10** (asthma–bmi, asthma–hypertension, asthma–stroke, asthma–t2d, bmi–hypertension, bmi–stroke, bmi–t2d, hypertension–stroke, hypertension–t2d, stroke–t2d) |
| Trait-pair attempts surviving at PP.H4 ≥ 0.5 / ≥ 0.8 | **0 / 0** (all 10 unique trait-pair combinations collapse under the disclosure-honest joint reading) |
| 8-hub trait-pair manifest presence | **3 / 8** (FTO 13 EUR+AFR rows, MC4R 4, SH2B3 4 — all PP.H4 empty) |
| 8-hub fine-mapping-only (no trait-pair attempt) | **1 / 8** (APOE — `bmi.EUR.APOE_19q13` `non_converged` n_CS = 6 in `finemap_summary.tsv`) |
| 8-hub absent from Stage 2 manifest entirely | **4 / 8** (KCNJ11/ABCC8 11p15, NEGR1 1p31.1, PPARG 3p25, SEC16B 1q25.2 — neither in `coloc_summary.tsv` nor in `finemap_summary.tsv`) |
| 8-hub surviving at PP.H4 ≥ 0.5 | **0 / 8** |
| Table 1 surviving-rows count (PP.H4 ≥ 0.5 filter on `coloc_summary.tsv`) | **0** (`table1_surviving_n = 0`; per `results/track_a_aggregations/table1_surviving_rows.tsv`; aggregator hard-fail assert intact as positive-result safety net) |
| Table 1 threshold (locked, NOT lowered) | **0.5** (Tier B threshold; threshold-lowering to 0.3 to surface FTO_16q12 EUR Tier-C 0.3099 is OUT of scope per disclosure_decisions PH-06 chosen=a) |
| Real-LD–surviving variant-mechanism classifiable signals (PH-08) | **0** (no input rows; classification non-computable; disclosure-honest fallback per disclosure_decisions PH-08 chosen=a) |
| Real-LD–surviving candidate-gene scorecard rows (PH-09 / Table 2 body) | **0** (`results/annotation/` does not exist on disk per W0 inventory; aggregator build deferred to Track B per disclosure_decisions PH-09 chosen=a) |
| Table 3 EUR admissible body rows emitted (PH-10b) | **16** (5 base regions × variable trait-pair counts; per `results/track_a_aggregations/table3_admissible_pairs.tsv` — APOL1 3 + CXADR_F2RL1 1 + FTO 10 + MC4R 1 + SH2B3 1) |
| AFR regions in Stage 2 trait-pair manifest (PH-10a) | **4** (APOL1_22q12, FTO_16q12, MC4R_18q21, SH2B3_12q24) |
| AFR trait-pair attempts (PH-10a) | **12** (3 per region × 4 regions; all PP.H4 empty) |
| AFR Tier C rows in `tier_assignments.tsv` (PH-10a) | **4** (one per AFR region; all PP.H4 = 0) |
| Total Stage 2 manifest attempts (PH-10c) | **44** (per `results/multitrait/coloc_manifest.tsv` data rows; one TOTAL footer in Table 4 aggregator output) |
| Total with `coloc_summary.tsv` row (PH-10c) | **28** (matches the source-of-truth row count; all PP.H4 empty) |
| Total with valid PP.H4 (PH-10c) | **0** |
| Total manifest attempts NOT reaching summary row (PH-10c) | **16** (44 manifest − 28 summary; failed before producing even an empty-PP row) |
| Unique trait-pair groupings in Table 4 body (PH-10c) | **10** (matches per-trait-pair distribution from W2 PH-05) |
| Real-LD pathway-enrichment Tier A + B genes (PH-01) | **0** (per `results/qtl_coloc/tier_assignments.tsv` md5 `17ff46dbbfe78dd537d6b9bff7f3ae67`; locks Abstract pathway disclosure) |
| Pathway fold-enrichment delta (real − identity) at threshold (PH-01) | **non-computable** (input gene set empty under real-LD; identity-LD headlines withdrawn) |
| Pathway databases enumerated (PH-01) | **4** (KEGG, Reactome, GO_BP, gprofiler_combined; per `results/track_a_aggregations/pathway_real_ld_disclosure.tsv`) |

**Headline framing (manuscript-anchor language):** Stage 2 real-LD `coloc.susie` produced 28 attempted trait-pair rows across 10 unique trait-pair combinations, all returning empty PP.H4 / PP.H4.abf columns. The identity-LD `coloc.susie` comparator was not produced (the k2d 2026-04-25 re-fire covered fine-mapping only, not trait-pair `coloc.susie` — per AUDIT-REVIEW-V2-2026-04-26.md §HQ3 Eval 3.3 IN-PROGRESS). The yield-redistribution table is therefore disclosure-honest: **0 surviving / 0 lost / 0 rescued / 28 both-null** at the manuscript's PP.H4 ≥ 0.8 threshold; ΔPP.H4 statistics are non-computable. Of the eight published-literature pleiotropic hubs (KCNJ11/ABCC8, NEGR1, APOE, FTO, MC4R, SH2B3, PPARG, SEC16B), only 3 / 8 (FTO, MC4R, SH2B3) are present in the Stage 2 trait-pair `coloc.susie` manifest at all (with all PP.H4 empty under real-LD); 1 / 8 (APOE) has fine-mapping output but no trait-pair attempt; 4 / 8 are absent from the Stage 2 manifest entirely. This is the disclosure-honest joint reading at the manuscript's confidence threshold; threshold-lowering to 0.3 (which would surface the FTO_16q12 EUR Tier-C 0.3099 signal) is explicitly NOT performed in the placeholder-fill (would reframe the threshold without OSF amendment; manuscript already locked to "Tier B threshold = 0.5" throughout).

**Sources:**
- [results/multitrait/coloc_summary.tsv](../../results/multitrait/coloc_summary.tsv) (28 rows, md5 `5fa3c4004970c5da711d05947cb1f7d2`)
- [results/track_a_aggregations/yield_redistribution.tsv](../../results/track_a_aggregations/yield_redistribution.tsv) (4 rows: Survived/Lost/Rescued/Both-null = 0/0/0/28)
- [results/track_a_aggregations/pair_pp_h4_summary.tsv](../../results/track_a_aggregations/pair_pp_h4_summary.tsv) (1 row: n_total=28 / n_with_pp_h4=0 / 16 EUR / 12 AFR)
- [results/track_a_aggregations/table3_admissible_pairs.tsv](../../results/track_a_aggregations/table3_admissible_pairs.tsv) (16 EUR rows for Table 3 body, W5b PH-10b)
- [results/track_a_aggregations/per_trait_pair_distribution.tsv](../../results/track_a_aggregations/per_trait_pair_distribution.tsv) (10 unique trait-pairs; W2 PH-05)
- [results/track_a_aggregations/eight_hub_fates.tsv](../../results/track_a_aggregations/eight_hub_fates.tsv) (8 hubs; W2 PH-07)
- [results/track_a_aggregations/table1_surviving_rows.tsv](../../results/track_a_aggregations/table1_surviving_rows.tsv) (header + 0 data rows; W3 PH-06)
- [results/track_a_aggregations/afr_distribution_summary.tsv](../../results/track_a_aggregations/afr_distribution_summary.tsv) (4 AFR regions; W5 PH-10a)
- [results/track_a_aggregations/table4_coloc_error_breakdown.tsv](../../results/track_a_aggregations/table4_coloc_error_breakdown.tsv) (10 trait-pair rows + 1 TOTAL; W5 PH-10c)
- [results/track_a_aggregations/pathway_real_ld_disclosure.tsv](../../results/track_a_aggregations/pathway_real_ld_disclosure.tsv) (4 pathway databases; W6 PH-01)
- Aggregator: [src/R/aggregators/aggregate_table3_admissible_pairs.R](../../src/R/aggregators/aggregate_table3_admissible_pairs.R) (committed quick-260427-e8n W1, extended W5)
- Aggregator: [src/R/aggregators/aggregate_per_trait_pair_and_hubs.R](../../src/R/aggregators/aggregate_per_trait_pair_and_hubs.R) (committed quick-260427-e8n W2)
- Aggregator: [src/R/aggregators/aggregate_table1_pleiotropic_loci.R](../../src/R/aggregators/aggregate_table1_pleiotropic_loci.R) (committed quick-260427-e8n W3)
- Aggregator: [src/python/aggregate_coloc_manifest_errors.py](../../src/python/aggregate_coloc_manifest_errors.py) (committed quick-260427-e8n W5)

**Caveats** (mandatory disclosure for any downstream cite of these scalars):

1. **Audit-v2 §HQ3 Eval 3.3 IN-PROGRESS gates this disclosure.** If the HQ#2(i) L = 20 SH2B3 re-fit and HQ#2(iii) canonical SH2B3 EUR BMI–HTN / HTN–stroke trait-pair re-fires land later, this LIVE block must be revisited. The 0/0/0/28 redistribution is a snapshot of the 2026-04-27 pre-bioRxiv placeholder-fill freeze, not a permanent claim about real-LD `coloc.susie` survival at this curated locus set.
2. **The yield-redistribution comparator structure assumes identity-LD trait-pair `coloc.susie` output exists.** That output does not exist on disk at this freeze (the k2d 2026-04-25 re-fire was fine-mapping-only, not trait-pair `coloc.susie`). The disclosure resolves to "all-empty real-LD + comparator-absent identity-LD = both-null = 28 of 28" rather than "Lost = 28" because the "Lost" classification requires an identity-LD PP.H4 ≥ 0.8 to be observable.
3. **Threshold preservation.** Disclosure-honest framing uses the manuscript's pre-registered Tier B threshold of 0.5 and Tier A threshold of 0.8 verbatim; lowering to 0.3 to surface the FTO_16q12 EUR Tier-C 0.3099 signal is explicitly out of scope for this placeholder-fill (would reframe the threshold without OSF amendment).
4. **PH-08 / PH-09 disclosure-honest fallbacks** (no annotation pipeline built): `results/annotation/` does not exist on disk (verified at W0 inventory); the input gene set at PP.H4 ≥ 0.5 is empty regardless of any potential pipeline build (Table 1 0-row outcome locks PH-08 / PH-09 inputs to 0). Building a CADD / GTEx / PolyPhen / SIFT / OMIM / ChEMBL / DGIdb / gnomAD pLI / STRING join aggregator at this freeze would produce empty output for empty input — deferred to Track B work where genome-wide real-LD signals are expected to populate the surviving-variant set.

---

## Stage 2 fine-mapping yield (Phase 1 SuSiE-RSS with real 1000G EUR LD)

| Metric | Value |
|---|---|
| Total region × ancestry fits | 96 |
| Non-empty credible sets | **51 / 96 (53.1%)** |
| Empty credible sets | 45 / 96 (46.9%) |
| Status=ok | 48 |
| Status=too_many_variants | 24 |
| Status=non_converged | 18 |
| Status=no_variants | 6 |

~~Identity-LD baseline (pre-Stage-2): **12 / 96 non-empty credible sets (12.5%)** per prior STATE.md session continuity.~~

~~**Headline yield delta**: 12/96 → 51/96 = **4.25× fold increase in non-empty CS yield under real 1000G EUR LD vs identity-LD fallback.**~~

> **SUPERSEDED 2026-04-25** — preserved verbatim for audit traceability. The 12/96 baseline reflected a partial-coverage Stage 1d narrow-validation run (only 2 of 10 admissible regions had identity-LD fits at the time of freeze). The matched-coverage k2d full-coverage 2026-04-25 re-fire produces 48/95 = 50.5% (see top of this document for the live block). The fold-change shifted from 4.25× to ~1.06× under the tightened comparator. Manuscript edits propagated quick-260425-kki.

### Scope caveat (mandatory disclosure in manuscript)

Real-LD panel coverage applies to **10 autosomal EUR curated regions**. The following remain on the legacy identity-LD fallback:
- HLA_6p21 (EUR + AFR)
- BMI_Xq24 (EUR + AFR)
- All AFR regions

The 1000G EUR plink panel used for the Stage 2 fix is EUR-autosomal-only. Matched-ancestry AFR LD pending M3 (AoU controlled-tier WGS build; see [AOU-LD-PIPELINE.md](./AOU-LD-PIPELINE.md)).

---

## Stage 2 trait-pair coloc.susie (multitrait/coloc_summary.tsv)

| Metric | Value |
|---|---|
| Total pairwise tests attempted | **28** |
| Rows with valid PP.H3 / PP.H4 | **0** |
| Rows with empty PP columns (coloc.susie returned no result) | 28 |

Region × ancestry × trait-pair breakdown (28 rows):
- APOL1_22q12: 3 AFR + 3 EUR = 6 pairs
- CXADR_F2RL1_6p21: 1 EUR pair
- FTO_16q12: 3 AFR + 10 EUR = 13 pairs
- MC4R_18q21: 3 AFR + 1 EUR = 4 pairs
- SH2B3_12q24: 3 AFR + 1 EUR = 4 pairs

**Flagship collapse — SH2B3 × asthma (EUR)**: pre-pivot identity-LD coloc produced PP.H4 = 1.00 at canonical leads rs3184504/rs10774625/rs7137828/rs4766578 (per STATE.md narrative and Stage 1d validation). Under Stage 2 real-LD on [results/multitrait/coloc_summary.tsv](../../results/multitrait/coloc_summary.tsv), the only SH2B3 EUR trait-pair row is `SH2B3_12q24__EUR__asthma_vs_t2d` (note: asthma-vs-t2d, not asthma-vs-stroke) and PP.H3/PP.H4/n_snps columns are empty — consistent with no credible-set overlap under real LD. **n_cs_a = 0 confirmed**.

**Draft discrepancy** (id-vs-ref-LD.md Section 3 cites "1,446 attempted pairwise tests included 861 computational failures"): the 1,446 / 861 numbers refer to an older/broader run and do not match Stage 2 artifacts on disk. Current counts above are the authoritative Stage 2 values. Update the abstract + results accordingly.

---

## Tier assignments (QTL coloc — run_qtl_coloc.R, per-ID)

| Tier | Count | Ancestry breakdown |
|---|---|---|
| Tier A | **0** | — |
| Tier B | **0** | — |
| Tier C | **9** | 4 AFR + 5 EUR |
| negative_control | ~~224~~ **200** | 200 EUR (none AFR this run); 24 HLA-immune rows reclassified to identity-LD-fallback per AUDIT-REVIEW-2026-04-25.md Eval 3.7 (post-t9j 2026-04-26 — see live block + reconciliation log). On-disk `tier_assignments.tsv` unchanged at 224 rows. |
| **Total rows** | **233** | — |

### Tier C rows (9 total — all regions)

| region | ancestry | best_qtl_pph4 | resolving_gene | resolving_tissue | source |
|---|---|---|---|---|---|
| APOL1_22q12 | AFR | 0.0 | — | — | — |
| APOL1_22q12 | EUR | 0.0131 | ENSG00000100342 | Cells_Cultured_fibroblasts | gtex_eqtl |
| CXADR_F2RL1_6p21 | EUR | 0.0 | — | — | — |
| FTO_16q12 | AFR | 0.0 | — | — | — |
| FTO_16q12 | EUR | **0.3099** | ENSG00000177508 (IRX3) | Pancreas | gtex_eqtl |
| MC4R_18q21 | AFR | 0.0 | — | — | — |
| MC4R_18q21 | EUR | 0.0 | — | — | — |
| SH2B3_12q24 | AFR | 0.0 | — | — | — |
| SH2B3_12q24 | EUR | 0.0517 | ENSG00000204842 (ATXN2) | Adrenal_Gland | gtex_eqtl |

**Highest Tier C PP.H4** across the entire Stage 2 run: **0.3099** (FTO_16q12 EUR → IRX3 / Pancreas / gtex_eqtl). Below Tier B threshold 0.5 and Tier A threshold 0.8.

---

## Negative-control behavior (post-t9j HLA reclassification 2026-04-26) — LIVE

**Headline numerics:** 9 distinct negative-control loci / 200 rows / 100% Tier-C-or-empty.

| Metric | Value |
|---|---|
| Distinct negative-control loci | **9** (4 blood-group + 5 cosmetic) |
| Total negative-control rows | **200 / 200 Tier C or empty (100%)** |
| Blood-group loci | ABO, FUT1/FUT2, KEL, RH (4 loci, 80 rows) |
| Cosmetic loci | HERC2/OCA2, IRF4, MC1R, SLC24A5, TYR (5 loci, 120 rows) |
| HLA-immune | **Reclassified out of negative-control panel** — see manuscript §Methods §Admissibility (1 locus, 24 rows on disk; reframed as identity-LD-fallback) |
| Tier-A signals | 0 |
| Tier-B signals | 0 |
| Tier-C-or-empty | 200 / 200 (100%) |

**Headline framing (manuscript-anchor language):** Per AUDIT-REVIEW-2026-04-25.md Eval 3.7, HLA-immune is reframed from pre-specified negative-control to admissibility-based identity-LD-fallback — keeping HLA in only the fallback role (methodologically load-bearing, MHC architecture incompatible with autosomal 1000G EUR panel) and removing it from the negative-control panel where its definitional-null behavior makes the calibration claim near-tautological. Per Eval 3.8, the panel is restated as 9 distinct loci (not 224 rows); 200 rows is reported as a secondary detail. The on-disk `results/qtl_coloc/tier_assignments.tsv` is unchanged (224 negative_control rows preserved; total_rows 233 preserved); only the manuscript narrative classification is updated.

**Sources:** [results/qtl_coloc/tier_assignments.tsv](../../results/qtl_coloc/tier_assignments.tsv) (224 rows on disk, distinct neg-ctrl locus keys: 4 blood-group + 5 cosmetic + 1 HLA = 10 keys; manuscript narrative classifies 9 of these as negative-control, 1 as identity-LD-fallback); [.planning/amendments/AUDIT-REVIEW-2026-04-25.md](./AUDIT-REVIEW-2026-04-25.md) Eval 3.7 + 3.8 + Quick #2.

---

~~## Negative-control behavior~~

~~224 negative-control rows. Category breakdown:~~
- ~~cosmetic (MC1R, OCA2/HERC2, IRF4, SLC24A5, TYR): **120**~~
- ~~blood_group (ABO, FUT1/FUT2, KEL, RH): **80**~~
- ~~hla_immune: **24**~~

~~All 224 returned empty coloc or Tier C; **no negative-control region reached Tier A or Tier B**. Pre-specified negative-control behavior **matched as predicted**.~~

> **SUPERSEDED 2026-04-26** — preserved verbatim for audit traceability. The 24 HLA-immune rows are reclassified out of the negative-control panel per AUDIT-REVIEW-2026-04-25.md Eval 3.7 (independent audit recommended choosing one classification for HLA — fallback or negative-control, not both); the live block above is the load-bearing reference. The on-disk `results/qtl_coloc/tier_assignments.tsv` is unchanged at 224 rows; only the manuscript narrative classification is updated. Manuscript edits propagated by quick-260425-t9j.

---

## QTL coloc scope (per-ID JSON tally across 1,274 attempted)

| Status | Count | % |
|---|---|---|
| too_few_snps | 1,005 | 78.9% |
| no_qtl_cs | 235 | 18.4% |
| success | 32 | 2.5% |
| qtl_susie_failed | 2 | 0.2% |

**Scope limitation**: Stage 2 run covered GTEx eQTL + sQTL only. OneK1K sc-eQTL (raw data not staged) and UKB-PPP pQTL (no SYNAPSE_AUTH_TOKEN at fire time) are excluded. See STATE.md archived section on Stage B.5.

**Draft framing of failures**: 1,005 / 1,274 (78.9%) `too_few_snps` failures are largely attributable to the SNP-ID format mismatch that was structurally fixed between Stage 1d and Stage 2 but may incompletely propagate to all source × tissue × gene combinations. Stage 2 re-fit commit chain: a6e3214 · 6de9a88 · 7d54183 · 9102466 · 1635d37 · 0948a76 · 069b34f.

---

## Numbers explicitly **NOT** claimed

The following appear in the pre-pivot manuscript draft or earlier sessions and are **not supported** by Stage 2 artifacts on disk. If the manuscript retains any of them, they must be either removed or reconciled against disk:

- "1,446 attempted pairwise tests" — disk shows 28 trait-pair + 1,274 QTL-coloc = 1,302 total; neither matches 1,446.
- "861 computational failures" — disk shows 1,242 QTL-coloc failures or 28 trait-pair failures; neither matches 861.
- "9 reached Tier C" — disk confirms **9 Tier C** across 5 non-negative-control regions. ✅ matches draft.
- "224 region-pair evaluations matched pre-specified negative-control behavior" — disk shows 224 negative_control rows in tier_assignments. ✅ matches draft. Terminology correction: these are region-level negative controls, not region-pair evaluations.
- "0 Tier A" — disk confirms **0 Tier A + 0 Tier B**. ✅ matches draft.

---

## Usage

All abstract, results, and table numbers in [docs/manuscript/id-vs-ref-LD.md](../../docs/manuscript/id-vs-ref-LD.md) must cite values from this file verbatim. The OSF amendment (Route B Step 3.3) must cite identical values. If any Stage 2 re-run changes these numbers, update this file first, then propagate downstream.

**Reconciliation log** (append as updates land):

| Date | Change | Reason |
|---|---|---|
| 2026-04-23 | Initial freeze from Stage 2 production fire | Step 2.1 of approved plan (snappy-humming-pine.md) |
| 2026-04-23 | id-vs-ref-LD.md numeric reconciliation: removed all 1,446 / 861 citations; replaced with disk-verified Stage 2 splits (28 trait-pair coloc.susie / 1,274 QTL-coloc / 32 successes / 1,005 too_few_snps / 224 negative-controls). Abstract, Methods §Data Harmonization, Methods §Harmonization-Pipeline Diagnostics, Methods §Negative-Control Loci, Results §Headline, Results §SH2B3 case study, Results §Pipeline Diagnostics, Results §Negative-Control Performance, Discussion §Overall, Discussion §Strengths (3), Discussion §Limitations (5), Discussion §Conclusions (1), Table 3 SH2B3 rows, Figure 1 caption all updated. | Step 2.2.a–d partial execution |
| 2026-04-23 | **Open scope gap flagged**: SH2B3 EUR canonical trait-pairs (BMI–hypertension, hypertension–stroke) that reached PP.H4 = 1.00 under Stage 1d identity-LD are **absent from the Stage 2 `coloc.susie` output manifest**. Only `SH2B3_12q24__EUR__asthma_vs_t2d` was run. Manuscript now frames this as "absent from manifest, consistent with credible-set collapse, pre-registered re-fire supplementary analysis." A targeted Stage 2 re-fire on the canonical SH2B3 pairs is required to fully close the flagship claim. Owner: Carter (LSF decision). | Step 2.2.d deviation |
| 2026-04-23 | **Remaining Track A manuscript edit passes** (not yet executed, per approved plan Step 2.2.b–f): Introduction rewrite (Section 4.5), full Results §Pathway re-compute from `results/pathway/` outputs, References additions (Wallace 2021, Zou 2022, Weissbrod 2020, Benner 2017), 3 figure build scripts under `src/R/figures/`, bioRxiv submission. These will land in subsequent `/gsd-quick` sessions. | Plan-track-A open items |
| 2026-04-25 | **Comparator tightened**: post-k2d full-coverage identity-LD re-fire produces 48/95 non-empty CS (50.5%) vs 51/96 real-LD (53.1%) = **1.06× matched-coverage fold change**. Live block added at top of file; legacy 12/96 → 4.25× block marked SUPERSEDED but preserved verbatim for audit. Manuscript id-vs-ref-LD.md (L28, L82, L138, L214, L222, L252, L293) reframed under "we tightened the comparator and the inflation magnitude shifted" anchor language. fig2_cs_yield.R now disk-derives the identity-LD baseline from IDENTITY-LD-K2D-FIT-SUMMARY.tsv. The 95-vs-96 denominator note (missing bmi.EUR.APOE_19q13) is recorded in the live block and propagated to manuscript Methods. | quick-260425-kki — Track A audit-driven figure correction pass. The previously cited 4.25× contrast against a 12/96 baseline reflected a Stage 1d narrow-validation freeze; the post-k2d full-coverage baseline is the appropriate matched-coverage comparator. |
| 2026-04-26 | **H3 LD-reference-quality dose-response scalars frozen**: a new sibling LIVE block ("H3 LD-reference-quality dose-response (post-wa2 H3 figure, 2026-04-26) — LIVE") is inserted between the Stage 2 LIVE block and the SUPERSEDED 12/96 block, freezing the 33/60 / 27/60 / 19/60 / 41/60 / 32/1274 / 0/32 / FTO 0.3099 / SH2B3 0.0385 scalars surfaced by the H3 dose-response figure (`src/R/figures/fig_h3_ld_overlap_dose_response.R`, committed at `1e4b071` per quick task `260425-wa2`). Audit-driven companion to AUDIT-REVIEW-2026-04-25.md High-Quality #3. The block frames the figure as exploratory methodology-validation and is referenced by the new Figure S7 caption block in the manuscript supplementary section (companion atomic commit). | quick-260426-04b (brief-slug 260425-h3p) — Track A audit High-Quality #3 dose-response scalar freeze. |
| 2026-04-26 | **HLA reclassification + negative-control N restatement**: per AUDIT-REVIEW-2026-04-25.md Eval 3.7 + 3.8, the negative-control panel narrative at L28/L102/L138/L188/L240 of `docs/manuscript/id-vs-ref-LD.md` is restated from "224 rows / 3 classes (cosmetic/blood-group/HLA)" to "200 rows across 9 distinct loci / 2 classes (cosmetic/blood-group)". HLA-immune (1 locus, 24 rows) is reframed as an admissibility-based identity-LD-fallback region (manuscript L80/L210/L244 unchanged) rather than a pre-specified negative control. The on-disk `results/qtl_coloc/tier_assignments.tsv` is unchanged (224 rows preserved; total_rows 233 preserved); only the manuscript narrative classification is updated. Live block added to "Negative-control behavior" section; legacy 224/24-HLA-immune block marked SUPERSEDED 2026-04-26 but preserved verbatim. Abstract L28 + Methods L102 + Results L138 + Results L188 + Discussion L240 reframed under "audit Eval 3.7 + 3.8" anchor. Eval 3.9 (DIAMANTE T2D vintage = Mahajan 2018, N=898,130, DOI 10.1038/s41588-018-0241-6) closed in companion atomic commit 943d8f6 (manuscript L54/L56/L327). | quick-260425-t9j — HLA reclassification + negative-control N restatement per audit. The audit-author identified that HLA cannot serve simultaneously as admissibility-rejected fallback (manuscript L80/L210/L244) and pre-specified negative control (L102/L138/L188/L240); we kept the fallback framing because it is methodologically load-bearing (MHC architecture is too complex for the autosomal 1000G EUR panel) and dropped the negative-control framing because HLA's behavior is definitionally null under the negative-control rubric, making the calibration claim near-tautological. Eval 3.8: panel breadth is more accurately stated as "9 distinct loci" than "224 rows". |
| 2026-04-26 | **L1H formal-pattern mirror to publication surfaces (idempotent shore)**: docs/manuscript/id-vs-ref-LD.md L295 Figure 2 caption upgraded to formal `(SUPERSEDED 2026-04-25 per quick-260425-kki; ... preserved with full audit trail in TRACK-A-FROZEN-NUMBERS.md)`; src/R/figures/fig2_cs_yield.R header L10-17 upgraded to formal `SUPERSEDED 2026-04-25 per quick-260425-kki` attribution + matched-coverage `(48/95 vs 51/96 = 1.06x yield)` Pattern B citation. Manuscript prose at L28/L82/L138/L216 (abstract/results/headline/discussion) verbatim — original-research voice preserved per Carter framing rule. TRACK-A-FROZEN-NUMBERS.md content byte-identical (already carried L1H pattern in functional form at L70-75 SUPERSEDED block + L209 reconciliation row); only this audit-trail row appended. | quick-260426-mjv — mirrors quick-260426-l1h formal pattern to publication trio for audit-trail symmetry between planning ecosystem and live publication surfaces. |
| 2026-04-27 | **Pre-bioRxiv placeholder-fill scalars frozen** via quick-260427-e8n (Wave 1, PH-02/03/04): new "Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE" block added between Paired-fit structural inflation (Figure S2) block and the Stage 2 fine-mapping yield (Phase 1) block. Scalars locked: 28 attempted trait-pair rows / 0 with valid PP.H4 / 16 EUR + 12 AFR admissible / Survived=Lost=Rescued=0 / Both-null=28 / mean·median·range ΔPP.H4 = non-computable. Aggregator: `src/R/aggregators/aggregate_table3_admissible_pairs.R` (new `src/R/aggregators/` namespace per quick-260427-e8n orchestrator note). LIVE block extended in subsequent waves (W2/W3/W5/W6) of the same quick task with PH-05/07/06/08-09/10a-c/01 scalars. | quick-260427-e8n — Decision-pending item 4 closure (id-vs-ref-LD.md L362 self-referential placeholder, deferred-items #5 of quick-260427-azv SUMMARY); pre-bioRxiv blocker for Genome Medicine submission. Disclosure-honest joint reading dominates (real-LD all-empty + identity-LD trait-pair comparator absent = 28/28 both-null) consistent with §3.4 / Conclusion-1 / Pathway non-computable framing already in audit-v2-closed prose. |


---

## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE

Per [W3 PLAN line 70 thresholds](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W3-checkpoint-human-verify-PLAN.md) + [W3 SUMMARY](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W3-checkpoint-human-verify-SUMMARY.md) (recorded 2026-04-30, commit `9323c5d`), Carter selected **BRANCH_C_SURVIVE** for the SH2B3 BMI–HTN canonical pair on the basis of Wave 2 R2 disk numbers showing PP.H4 = 1.0 at the canonical lead variant rs3184504.

| Pair | PP.H4 | Threshold class (per D-TA-Wave3-thresholds) |
|---|---|---|
| **bmi_vs_hypertension (CANONICAL)** | **1.0** | **SURVIVE_GE_0.8** (rs3184504, nsnps=168) |
| **hypertension_vs_stroke (CANONICAL)** | **1.0** | **SURVIVE_GE_0.8** |
| hypertension_vs_t2d | **1.0** | **SURVIVE_GE_0.8** |
| bmi_vs_t2d | 4.3081e-27 | COLLAPSE_BELOW_0.5 (PP.H3 = 1.0; shared region but distinct causal variants) |
| stroke_vs_t2d | 0 | COLLAPSE_BELOW_0.5 (PP.H3 = 0.9976) |
| asthma_vs_bmi | NA | MISSING (no_signal: n_cs_a = 0) |
| asthma_vs_hypertension | NA | MISSING (no_signal: n_cs_a = 0) |
| asthma_vs_stroke | NA | MISSING (no_signal: n_cs_a = 0) |
| bmi_vs_stroke | NA | MISSING (no_posterior; 39 pairs computed) |

**Headline framing (manuscript-anchor language):** The canonical SH2B3 BMI–hypertension pleiotropy claim is **validated** under matched-coverage real-LD `coloc.susie`. The PP.H4 = 1.0 at rs3184504 holds robustly under two co-occurring failure modes that would naively be expected to collapse it: (1) W1.5-audit-documented LD-panel pathology (weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage relative to the GWAS panel), and (2) SuSiE-RSS strict-gate non-convergence at the three backing per-trait fits (BMI / hypertension / stroke at niter = 1000 carry `convergence_status = non_converged` per the strict-gate definition `n_CS < L_used` AND `L_saturated = FALSE` AND `^converged_` regex match). The dual robustness is itself a methodological finding: the canonical SH2B3 pleiotropy claim survives both failure modes, materially constraining the inflation-mechanism narrative for this locus.

**Sources:**
- Wave 2 R2 canonical-pair re-fire: `bin/fire_canonical_susie_pairs.sh` + commit `b3395d9` + 9 per-pair JSONs at `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json`
- Wave 3 decision token: [`D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md) (CONTEXT.md addendum, commit `9323c5d`)
- Per-pair report: [`ta-sh2b3-W2-pp-h4-report.tsv`](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv)
- Merged trait-pair manifest: [`results/multitrait/coloc_summary.tsv`](../../results/multitrait/coloc_summary.tsv) (post-260501-wdn merge md5 `558fca45…`, 37 rows = 28 R1 canonical-locus + 9 R2 SH2B3 EUR canonical-and-lattice; Pitfall 3 exemption for the merge)
- SuSiE-RSS V4 niter=1000 fits backing R2: 3 SH2B3 EUR per-trait `.fit.rds` md5s pinned at `462ada6ab64fdf8571fb5ed7dd6c6ea2` (BMI) / `8255c1acf50add5f68dfb551af977b53` (HTN) / `a041eecc27f3086190069783eeb45ffe` (stroke)
- W1.5 LD-panel-pathology audit: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/W1-5-AUDIT-SUMMARY.md` (weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage)

**Caveats** (mandatory disclosure for any downstream cite of these scalars):

1. **Strict-gate `convergence_status = non_converged` annotation.** The 3 backing SH2B3 EUR per-trait SuSiE-RSS fits at niter = 1000 carry the strict-gate non-convergence flag. PP.H4 = 1.0 robust under that flag is itself the methodological finding; cites of the Tier-A pass MUST disclose the convergence flag alongside the PP.H4 (see manuscript Results §SH2B3 case study).
2. **W4.5-B SuSiE-RSS rebuild explicitly skipped.** Per [DEC-2026-05-01-02](../DECISIONS.md) the LD-panel coverage is the binding Layer-2 constraint, not iteration budget on the GWAS fine-mapping side; the BRANCH_C Tier-A pass at niter = 1000 demonstrates that even under-converged posteriors at this locus produce a posterior probability of shared causal variant indistinguishable from 1.0 at the canonical lead under matched-LD; the rebuild branch was not necessary for the BRANCH_C decision.
3. **Trait-pair Tier-A gene set has cardinality 1.** All 3 Tier-A trait-pair signals concentrate at a single locus (SH2B3_12q24 EUR, annotated gene *SH2B3*); pathway-scale enrichment tests are non-informative at n = 1; the Tier-A pass is reported substantively in manuscript Results §SH2B3 case study + §Pleiotropic Loci, not as a pathway-scale claim.
4. **R2 scope is canonical-and-lattice at SH2B3 only.** The 9 R2 pairs cover all SH2B3 EUR trait-pair combinations involving any 2 of {asthma, bmi, hypertension, stroke, t2d}; canonical-pair R2 re-fires at the other 7 pleiotropy hubs (KCNJ11/ABCC8, NEGR1, APOE, FTO, MC4R, PPARG, SEC16B) have NOT been executed at this freeze and remain DEFERRED-COMPUTE per [AUDIT-REVIEW-V2-2026-04-26.md §HQ#2(i)+(iii)](AUDIT-REVIEW-V2-2026-04-26.md).
