# MVP dbGaP phs001672 Analysis Sub-Accession Inventory

**Phase 9 Plan 01 Task 1 artifact.** Resolves RESEARCH Assumption A1 and Open
Question 1: which of our 5 target traits (T2D, hypertension, stroke, asthma,
BMI) are actually released under the open-access phs001672 MVP sumstats tranche.

**Source:** `https://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/analyses/`
(enumerated 2026-04-14; 335 `pha*.txt` analysis files total).
**Method:** Range-request the first 2000 bytes of each `phs001672.pha*.txt` to
pull the dbGaP metadata header (`# Name`, `# Description`, `# Human genome
build`), then grep for trait keywords across Name + Description.

---

## Summary table

| Phase 9 trait | Availability | Primary pha IDs | Build |
|---|---|---|---|
| T2D | **CONFIRMED** (DIAMANTE 2022 + MVP-only) | 4943 AFR / 4944 EAS / 4945 EUR / 4946 HIS / 4947 TRANS | GRCh38 |
| Hypertension | **CONFIRMED (quantitative BP proxy only)** | 4730 DBP-TRANS / 4731 PP-TRANS / 4732 SBP-TRANS / 5040 DBP-EUR / 5041 PP-EUR / 5042 SBP-EUR | GRCh38 |
| Stroke | **NOT_RELEASED_AS_OF_2026-04** (only T2D-conditioned ischemic-stroke interaction; no main-effect stroke GWAS) | (pha005247 = T2D×IS interaction only; not usable for replication) | N/A |
| Asthma | **NOT_RELEASED_AS_OF_2026-04** | — | N/A |
| BMI | **NOT_RELEASED_AS_OF_2026-04** | (pha013060/pha013064 are OSA_AdjBMI, not standalone BMI) | N/A |

**Action for config/replication_cohorts.yaml:**
- T2D → use all 4 ancestry strata (EUR, AFR, HIS, TRANS) from DIAMANTE 2022 meta tranche.
- Hypertension → use quantitative BP (SBP primary, DBP/PP sensitivity) with explicit
  `note` that MVP has no binary HTN endpoint; BBJ uses SBP as well (matches).
- Stroke, asthma, BMI → `status: NOT_RELEASED_AS_OF_2026-04`, `action: exclude_from_MVP_cohort_column`.
  Replication for these traits falls to FinnGen R12 + GBMI + BBJ instead.

**Genome build correction:** All MVP phs001672 sumstats are build **GRCh38**, not
GRCh37 as the plan's draft YAML assumed. YAML updated accordingly; harmonization
rules (Plan 09-02) must liftover MVP → GRCh37 (same as FinnGen R12, BBJ v3).

---

## T2D (CONFIRMED)

### Primary — DIAMANTE Consortium + MVP 2022 (Vujkovic et al.)
Multi-biobank meta-analysis, published 2022. Build GRCh38, dbSNP 141.

| pha ID | Ancestry | Cases | Controls | Total N | Citation |
|---|---|---|---|---|---|
| pha004943.1 | AFR (African-American) | 24,646 | 31,446 | 56,092 | Vujkovic 2022 |
| pha004944.1 | EAS (Asian) | 46,511 | 169,776 | 216,287 | Vujkovic 2022 |
| pha004945.1 | EUR (European) | 148,726 | 965,732 | 1,114,458 | Vujkovic 2022 |
| pha004946.1 | HIS (Hispanic) | 8,616 | 11,829 | 20,445 | Vujkovic 2022 |
| pha004947.1 | TRANS (multi-ethnic) | 228,499 | 1,178,783 | 1,407,282 | Vujkovic 2022 |

FTP URL template: `https://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/analyses/phs001672.pha{NNNN}.txt`

### Supplementary — MVP-only T2D (released 2023)
Same phenotype, MVP-only (no external biobank contribution). Smaller N,
useful for hold-out cross-validation if DIAMANTE-meta introduces
sample-overlap concerns with Phase 1 discovery.

| pha ID | Ancestry | Cases | Controls |
|---|---|---|---|
| pha005054 | AFR | 23,305 | 30,140 |
| pha005055 | EAS | 893 | 1,560 |
| pha005056 | EUR | 69,869 | 127,197 |

Not used in Plan 09-01 YAML primary panel; flagged for Phase 9 Plan 09-03 as
optional sensitivity panel.

---

## Hypertension → Blood pressure quantitative proxy (CONFIRMED)

MVP phs001672 has NO binary hypertension (HTN) GWAS released. Instead it
releases three quantitative BP traits, each in both transethnic and
EUR-only flavors. **Decision: use SBP as primary proxy for HTN; DBP + PP as
sensitivity.** This matches BBJ hum0197-v3 (also quantitative SBP, no binary
HTN). Cross-cohort meta-analysis with FinnGen `I9_HYPTENSESS` (binary) will
require separate effect-scale handling — discovery-cohort-conditional
z-score harmonization rather than raw β meta, per RESEARCH §11 / D-04b.

| pha ID | Trait | Ancestry | Citation |
|---|---|---|---|
| pha004730.1 | DBP | TRANS | Giri 2019 / MVP 2020 |
| pha004731.1 | PP | TRANS | Giri 2019 / MVP 2020 |
| pha004732.1 | SBP (primary) | TRANS | Giri 2019 / MVP 2020 |
| pha005040.1 | DBP | EUR-only | MVP 2023 |
| pha005041.1 | PP | EUR-only | MVP 2023 |
| pha005042.1 | SBP (primary) | EUR-only | MVP 2023 |

FTP URL template: `https://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/analyses/phs001672.pha{NNNN}.txt`

---

## Stroke (NOT_RELEASED)

phs001672 contains **pha005247** ("Cardiometabolic"): a T2D-conditioned
ischemic-stroke-interaction analysis, not a main-effect stroke GWAS. Only β
and p-value for the SNP×T2D interaction coefficient are reported (per its
own metadata). This is not suitable for replicating a discovery-stage
main-effect coloc signal.

**Action:** exclude MVP from the stroke replication panel. Use FinnGen
`I9_STR_EXH` + BBJ `IS` (ischemic-only sensitivity) + GBMI stroke endpoint
instead.

---

## Asthma (NOT_RELEASED)

No phs001672 analysis file matches asthma on Name or Description.

**Action:** exclude MVP from the asthma replication panel. Use FinnGen
`J10_ASTHMA` + BBJ `As` + GBMI asthma endpoint instead.

---

## BMI (NOT_RELEASED)

No standalone BMI GWAS in phs001672. pha013060 / pha013064 are
OSA_AdjBMI (obstructive sleep apnea BMI-adjusted, not a BMI phenotype).

**Action:** exclude MVP from the BMI replication panel. Use BBJ `BMI` as
primary replication; GIANT Yengo 2022 as cross-biobank layer (already marked
EXCLUDED from GBMI as GBMI does not include BMI in its 14 flagship
endpoints). FinnGen R12 also marked EXCLUDED for BMI because FinnGen
endpoints are disease codes; BMI unavailable as quantitative lab value.

---

## Verification commands

```bash
# Re-enumerate pha IDs (should return 335 as of 2026-04-14):
curl -s https://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/analyses/ \
  | grep -oP 'pha\d+' | sort -u | wc -l

# Verify a known T2D pha file metadata header:
curl -s --range 0-2000 \
  https://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/analyses/phs001672.pha004945.txt \
  | grep -E '^# (Name|Description|Human genome)'
```

---

**Status:** Task 1 Step 1 complete. Consumed by `config/replication_cohorts.yaml`
Step 2 and `tests/phase9/test_cohort_ingest.py::test_mvp_phs_enumeration`.
