# Phase 3: Mendelian Randomization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-16
**Phase:** 03-mendelian-randomization
**Areas discussed:** Hypothesis scope & directionality, Ancestry strategy (REQ-4), Instrument selection from SuSiE, Method triangulation & reporting

---

## Hypothesis scope & directionality

### Trait pair scope

| Option | Description | Selected |
|--------|-------------|----------|
| All 10 pairs, bidirectional (Recommended) | Test all 20 directions (10 pairs x 2). Pre-register expected directions from literature. | ✓ |
| Biologically motivated subset only | Only pairs with prior causal evidence. Reduces compute. | |
| All 10 pairs, forward only | One direction per pair based on literature priors. | |

**User's choice:** All 10 pairs, bidirectional

### Mediation handling

| Option | Description | Selected |
|--------|-------------|----------|
| Flag but don't formally test mediation | Note triangular paths in discussion only. | |
| Include MVMR for key triangles | Add MVMR for 2-3 triangular paths. | ✓ |
| Formal network MR | Full mediation analysis. Substantial scope. | |

**User's choice:** Include MVMR for key triangles

### MVMR triangle selection

| Option | Description | Selected |
|--------|-------------|----------|
| BMI → Stroke adjusting for HTN | Tests BP mediation of BMI→Stroke. | ✓ |
| BMI → T2D adjusting for HTN | Tests independence from BP pathway. | ✓ |
| HTN → T2D adjusting for BMI | Tests independence from adiposity. | ✓ |

**User's choice:** All three triangles selected.

---

## Ancestry strategy (REQ-4)

### Primary ancestry approach

| Option | Description | Selected |
|--------|-------------|----------|
| Ancestry-specific primary, trans-ancestry sensitivity (Recommended) | EUR primary, AFR/EAS MR-RAPS, Lyon 2023 as sensitivity. | ✓ |
| Trans-ancestry primary (Lyon 2023) | Pool instruments across ancestries as primary. | |
| EUR-only primary, non-EUR as replication | EUR only primary, simplest. | |

**User's choice:** Ancestry-specific primary, trans-ancestry sensitivity

### Missing ancestry-trait combinations

| Option | Description | Selected |
|--------|-------------|----------|
| EUR-only for incomplete pairs, document gaps | Run EUR-only where non-EUR GWAS unavailable. Document in methods. | ✓ |
| Use Pan-UKBB proxies | Use Pan-UKBB multi-ancestry as proxy. | |
| Exclude incomplete pairs entirely | Only test where matched-ancestry exists. | |

**User's choice:** EUR-only for incomplete pairs, document gaps

---

## Instrument selection from SuSiE

### Instrument extraction method

| Option | Description | Selected |
|--------|-------------|----------|
| Lead SNP per credible set (Recommended) | One SNP per CS (highest PIP). Standard approach. | ✓ |
| All SNPs in 95% credible set | All CS variants, weight by PIP. | |
| LD-clumped variants from credible sets | Start with CS, clump at r² < 0.01. | |

**User's choice:** Lead SNP per credible set

### Complex region handling

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude from primary, include in sensitivity | Remove HLA/APOE/LPA/9p21, sensitivity includes them. | |
| Include all, flag in diagnostics | Keep all, let MR-PRESSO/CAUSE detect outliers. | ✓ |
| Exclude entirely | Drop from all analyses. | |

**User's choice:** Include all, flag in diagnostics

### F-statistic threshold

| Option | Description | Selected |
|--------|-------------|----------|
| F > 10 (standard threshold) | Drop instruments below F=10. | |
| No threshold, report all F-stats | Include all, report distribution. Let MR-RAPS handle. | ✓ |
| F > 10 primary, F > 5 sensitivity | Primary F>10, relax for non-EUR. | |

**User's choice:** No threshold, report all F-stats

---

## Method triangulation & reporting

### Disagreement decision rule

| Option | Description | Selected |
|--------|-------------|----------|
| Majority rule (3+ of 5 agree) | Call causal if ≥3 methods significant same direction. | ✓ |
| IVW primary, others as sensitivity | IVW primary estimate, others assess bias. | |
| Weighted evidence framework | Score each method, aggregate into tiers. | |

**User's choice:** Majority rule (3+ of 5 agree)

### Steiger directionality

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, apply Steiger filtering (Recommended) | Flag instruments failing Steiger test. Standard in bidirectional MR. | ✓ |
| Report Steiger but don't filter | Compute but don't exclude. | |
| Skip Steiger | Not needed if testing both directions. | |

**User's choice:** Yes, apply Steiger filtering

### Causal graph format

| Option | Description | Selected |
|--------|-------------|----------|
| Directed graph with edge weights | Nodes=traits, edges=effects. Main-text figure. | |
| Evidence matrix (table format) | 10x2 table. Supplementary only. | |
| Both graph and matrix | Graph as Figure 5, matrix as Supplementary Table. | ✓ |

**User's choice:** Both graph and matrix

### Multiple testing correction

| Option | Description | Selected |
|--------|-------------|----------|
| Bonferroni across 20 directed tests (Recommended) | p < 0.0025. MVMR separate. | ✓ |
| FDR (BH) across all tests | Less conservative. | |
| No correction, report nominal | Let triangulation guard against false positives. | |

**User's choice:** Bonferroni across 20 directed tests

---

## Claude's Discretion

- R package choices within TwoSampleMR/MR-CAUSE/MRPRESSO ecosystem
- Exact MVMR implementation
- Diagnostic plot selection
- Steiger flagging visualization

## Deferred Ideas

- Formal network MR / Bayesian mediation — full path analysis (own phase)
- Drug-target MR — translational framing via gene-tissue coloc proxies
