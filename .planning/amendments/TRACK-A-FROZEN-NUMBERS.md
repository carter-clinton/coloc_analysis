# Track A — Frozen Numbers (Stage 2 real-LD, 2026-04-22 production fire)

**Frozen on**: 2026-04-23
**Sources**: [results/fine_mapping/finemap_summary.tsv](../../results/fine_mapping/finemap_summary.tsv), [results/multitrait/coloc_summary.tsv](../../results/multitrait/coloc_summary.tsv), [results/qtl_coloc/tier_assignments.tsv](../../results/qtl_coloc/tier_assignments.tsv), [results/qtl_coloc/](../../results/qtl_coloc/) per-ID JSONs
**Purpose**: single source of truth for the Track A manuscript abstract, results, tables, and the OSF amendment (Route B Step 3.3). Any downstream doc that cites these numbers must cite them verbatim from this file.

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

Identity-LD baseline (pre-Stage-2): **12 / 96 non-empty credible sets (12.5%)** per prior STATE.md session continuity.

**Headline yield delta**: 12/96 → 51/96 = **4.25× fold increase in non-empty CS yield under real 1000G EUR LD vs identity-LD fallback.**

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

**Draft discrepancy** (track_a_pivot.md Section 3 cites "1,446 attempted pairwise tests included 861 computational failures"): the 1,446 / 861 numbers refer to an older/broader run and do not match Stage 2 artifacts on disk. Current counts above are the authoritative Stage 2 values. Update the abstract + results accordingly.

---

## Tier assignments (QTL coloc — run_qtl_coloc.R, per-ID)

| Tier | Count | Ancestry breakdown |
|---|---|---|
| Tier A | **0** | — |
| Tier B | **0** | — |
| Tier C | **9** | 4 AFR + 5 EUR |
| negative_control | 224 | 224 EUR (none AFR this run) |
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

## Negative-control behavior

224 negative-control rows. Category breakdown:
- cosmetic (MC1R, OCA2/HERC2, IRF4, SLC24A5, TYR): **120**
- blood_group (ABO, FUT1/FUT2, KEL, RH): **80**
- hla_immune: **24**

All 224 returned empty coloc or Tier C; **no negative-control region reached Tier A or Tier B**. Pre-specified negative-control behavior **matched as predicted**.

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

All abstract, results, and table numbers in [docs/manuscript/track_a_pivot.md](../../docs/manuscript/track_a_pivot.md) must cite values from this file verbatim. The OSF amendment (Route B Step 3.3) must cite identical values. If any Stage 2 re-run changes these numbers, update this file first, then propagate downstream.

**Reconciliation log** (append as updates land):

| Date | Change | Reason |
|---|---|---|
| 2026-04-23 | Initial freeze from Stage 2 production fire | Step 2.1 of approved plan (snappy-humming-pine.md) |
| 2026-04-23 | track_a_pivot.md numeric reconciliation: removed all 1,446 / 861 citations; replaced with disk-verified Stage 2 splits (28 trait-pair coloc.susie / 1,274 QTL-coloc / 32 successes / 1,005 too_few_snps / 224 negative-controls). Abstract, Methods §Data Harmonization, Methods §Harmonization-Pipeline Diagnostics, Methods §Negative-Control Loci, Results §Headline, Results §SH2B3 case study, Results §Pipeline Diagnostics, Results §Negative-Control Performance, Discussion §Overall, Discussion §Strengths (3), Discussion §Limitations (5), Discussion §Conclusions (1), Table 3 SH2B3 rows, Figure 1 caption all updated. | Step 2.2.a–d partial execution |
| 2026-04-23 | **Open scope gap flagged**: SH2B3 EUR canonical trait-pairs (BMI–hypertension, hypertension–stroke) that reached PP.H4 = 1.00 under Stage 1d identity-LD are **absent from the Stage 2 `coloc.susie` output manifest**. Only `SH2B3_12q24__EUR__asthma_vs_t2d` was run. Manuscript now frames this as "absent from manifest, consistent with credible-set collapse, pre-registered re-fire supplementary analysis." A targeted Stage 2 re-fire on the canonical SH2B3 pairs is required to fully close the flagship claim. Owner: Carter (LSF decision). | Step 2.2.d deviation |
| 2026-04-23 | **Remaining Track A manuscript edit passes** (not yet executed, per approved plan Step 2.2.b–f): Introduction rewrite (Section 4.5), full Results §Pathway re-compute from `results/pathway/` outputs, References additions (Wallace 2021, Zou 2022, Weissbrod 2020, Benner 2017), 3 figure build scripts under `src/R/figures/`, bioRxiv submission. These will land in subsequent `/gsd-quick` sessions. | Plan-track-A open items |
