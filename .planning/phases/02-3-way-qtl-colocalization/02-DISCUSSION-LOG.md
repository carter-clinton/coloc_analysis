# Phase 2: 3-way QTL colocalization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 02-3-way-qtl-colocalization
**Areas discussed:** QTL data scoping, Tier assignment logic, Tissue/protein filtering, Negative control design, Open Targets L2G integration, Deferred complex regions

---

## QTL Data Scoping

| Option | Description | Selected |
|--------|-------------|----------|
| GTEx eQTL + one pQTL + sQTL | Balanced; sufficient for Tier A/B with gene + tissue + splice evidence | ✓ |
| GTEx eQTL + both pQTL + sQTL | Maximal protein coverage but deCODE 24 TB logistics challenge | |
| GTEx eQTL + UKB-PPP only | Leaner; skip sQTL and deCODE | |

**User's choice:** Option 1 with additions: OneK1K (Yazar 2022) single-cell eQTL for all 14 immune cell types, scoped as targeted layer on all loci (broad trigger). UKB-PPP as primary pQTL source (larger sample ~54K vs deCODE ~35K, manageable download). deCODE deferred to Phase 9 replication.

**Follow-up — pQTL source selection:**

| Option | Description | Selected |
|--------|-------------|----------|
| UKB-PPP primary | Synapse, ~2,923 proteins, ~54K samples, structured download | ✓ |
| deCODE primary | ~4,907 aptamers, ~35K samples, 24 TB ephemeral links | |

**User's rationale:** UKB-PPP's sample size advantage, manageable download, coverage of major druggable targets. deCODE slots cleanly into Phase 9 without pipeline changes if reviewer requests broader coverage.

---

## Tier Assignment Logic

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep-as-sensitivity-table | One operating threshold for primary; sweep as supplementary figure | ✓ |
| Sweep-as-tier-modifier | Tier assignment threshold-dependent; main table shows all four thresholds | |

**User's choice:** Approach 1 with primary threshold 0.8. Wallace 2021 convention, field expectation, keeps main table stable and readable. Sweep at {0.5, 0.7, 0.9} in supplementary showing tier count shifts.

---

## Tissue/Protein Filtering Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Hypothesis-driven pre-filter | 8-12 tissues per trait; cheaper but may miss unexpected signals | |
| Wide-net post-hoc filtering | All 54 GTEx tissues, all loci; lets data assign tissues | ✓ |
| Hybrid (Tier A/B loci only) | All tissues but only for strong trait-trait coloc loci | |

**User's choice:** Option 2. "The whole point of Phase 2 is to discover which tissues and genes drive pleiotropy." Pre-filtering defeats discovery purpose. Hours vs. days on HPC not meaningful when timeline isn't a constraint.

---

## Negative Control Design

**Null threshold:**

| Option | Description | Selected |
|--------|-------------|----------|
| PP.H4 < 0.5 | Very liberal (below chance) | |
| PP.H4 < 0.8 | Matches primary operating threshold | ✓ |
| PP.H4 < 0.1 | Strong null | |

**User's rationale:** Negative control should fail to reach Tier A. PP.H4 < 0.1 too strict; HLA will violate due to LD artifacts.

**Distance-matched nulls:**

| Option | Description | Selected |
|--------|-------------|----------|
| Include | 100-1000 loci matched on gene density, LD block size, MAF | ✓ |
| Skip | Three curated sets sufficient for REQ-7 | |

**User's rationale:** Curated sets test biological specificity; matched nulls test statistical calibration. Together they answer different questions.

**Gene set construction:**

| Option | Description | Selected |
|--------|-------------|----------|
| Keep pigmentation + eye-color separate | Two sets with OCA2/HERC2 overlap noted | |
| Merge into cosmetic + add blood group | One merged set + ABO/RH/FUT/KEL as third | ✓ |

**User's rationale:** OCA2/HERC2 overlap makes them effectively one set. Blood group antigens are clean: well-mapped, strong GWAS, zero cardiometabolic mechanism, distinct LD.

---

## Open Targets / Locus2Gene Integration

**Validation role:**

| Option | Description | Selected |
|--------|-------------|----------|
| Hard validation gate | Must match L2G top gene or flagged | |
| Independent corroborating evidence | Report concordance rate; disagreements are findings | ✓ |

**Data access:**

| Option | Description | Selected |
|--------|-------------|----------|
| Live GraphQL API | Convenient but fragile for reproducibility | |
| Bulk download (Parquet) | Version-pinned, reproducible, heavier to parse | ✓ |

**User's rationale:** L2G gate inherits distance-to-gene training bias, penalizing distal enhancer assignments. Disagreement at a well-resolved locus is a story, not a problem.

---

## Deferred Complex Regions

| Option | Description | Selected |
|--------|-------------|----------|
| Bring both back | LPA + chr8 inversion | |
| Keep both deferred | Wait for Phase 9 | |
| LPA only | LPA has BMI-T2D anchor; chr8 needs allergic-disease GWAS | ✓ |

**User's choice:** Option 3. LPA earns its spot: PP.H4 = 0.990 for BMI-T2D (rank 7), KIV-2 LD manageable with complex-region policy + HGDP+1kG AFR panel. Chr8 inversion stays out — primary motivation is allergic/atopic disease, not in trait set.

---

## OneK1K Integration Depth

**Cell types:**

| Option | Description | Selected |
|--------|-------------|----------|
| Curated 5-7 types | CD4/CD8 T, NK, monocytes, B cells | |
| All 14 types | Negligible compute difference at few loci | ✓ |

**Trigger condition:**

| Option | Description | Selected |
|--------|-------------|----------|
| Strict (PP.H4 < 0.5 all GTEx) | Only truly blank loci | |
| Moderate (PP.H4 < 0.8 all GTEx) | No Tier A bulk hit | |
| Broad (always run) | Additional evidence layer on all loci | ✓ |

**Tier integration:**

| Option | Description | Selected |
|--------|-------------|----------|
| Upgrades tier | Cell-type eQTL at PP.H4 >= 0.8 meets Tier A definition | ✓ |
| Separate annotation only | Report without tier impact | |

**User's rationale:** Consistent with wide-net discovery logic. Tier system is evidence-agnostic — resolution of causal gene + tissue matters, not which dataset resolved it.

---

## Claude's Discretion

- QTL data harmonization pipeline design
- Snakemake rule architecture for tissue-level dispatch
- OneK1K preprocessing pipeline details
- Distance-matched null sampling algorithm (within 100-1000 range)
- Open Targets L2G version selection and Parquet parsing

## Deferred Ideas

- deCODE pQTL → Phase 9 replication
- chr8 inversion → pending allergic-disease GWAS
- Broad single-cell eQTL catalogs beyond OneK1K
- hyprcoloc multi-trait colocalization (distinct approach, may warrant own phase)
