# REQUIREMENTS.md

Testable acceptance criteria for the two-track original research program.
Track B milestone coverage maps via Amendment §3 M0–M6; Track A finalization
inherits the pre-pivot REQs that are still load-bearing. Each requirement
names its source (Amendment section or carried-forward pre-pivot origin),
a rule, and an acceptance test. Phase plans produced by `/gsd-plan-phase`
must reference the REQ IDs they satisfy.

Authoritative source for Track B scope expansion:
[`.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`](amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md).
AoU LD pipeline spec:
[`.planning/amendments/AOU-LD-PIPELINE.md`](amendments/AOU-LD-PIPELINE.md).

**Legend:**

- **[B]** = Track B requirement (Amendment §3 milestone)
- **[A]** = Track A requirement (pre-pivot, carried forward)
- **[AB]** = Shared by both tracks

---

## Preserved pre-pivot REQs (carried forward)

### REQ-SNAKEMAKE-CI [AB]

**Source:** Pre-pivot REQ-9; `GSD_BRIEFING.md` §5.2 gap #9.

**Rule:** The Snakemake pipeline must run end-to-end on a toy 3-locus subset
nightly (or on every merge to `main`). Environments must be pinned via
`envs/*.yml` files. Containers (Docker + Singularity) must be built and
published. Every Track B milestone (M0–M6) registers its new Snakemake
rules into the existing skeleton; Track A inherits the existing rule set.

**Acceptance:** `tests/toy_3locus/` exists with toy sumstats and a minimal
config override. `snakemake --snakefile tests/toy_3locus/Snakefile.test
--cores 2 --use-conda` completes in under 15 minutes. A GitHub Actions
workflow (or a cron-scheduled LSF job) runs it on schedule and records
pass/fail in `.planning/ci_status.md`.

---

### REQ-PUBLIC-DATA-ONLY [AB]

**Source:** Carter directive per `CLAUDE.md`; pre-pivot `DECISIONS.md`
2026-04-09 entry "Public-data-only policy".

**Rule:** Every GWAS / QTL / single-cell / reference dataset used in this
project must be publicly available or available under standard academic
DUAs. No wet-lab work, no industry data, no proprietary sources. This
enforces the AoU controlled-tier pathway (summary-only export per Amendment
§3 M3) as the AFR-LD provider.

**Acceptance:** Every data source added to `config/data_sources.yaml` has a
`license` field and a `public: true` field. DUAs count as public for this
purpose as long as they are open to academic researchers.

---

### REQ-SUSIE-RSS-POLICY [A]

**Source:** Pre-pivot REQ-2; `GSD_BRIEFING.md` §5.2 gap #2;
`Revision_Plan.md` Phase 1.

**Rule:** SuSiE default `L=10` gives up to 100 credible-set pair comparisons
per region. The pipeline ships an explicit policy for: (a) convergence
failures, (b) regions that hit the `L` cap, (c) `min_abs_corr` sensitivity,
(d) how to downweight or collapse coincident credible sets. Track A data
depends on this policy; Track B inherits it at M4 SuSiE-RSS runs.

**Acceptance:** `config/susie_policy.yaml` exists, is loaded by
`src/snakemake/rules/finemap.smk`, and is referenced in the methods
section of both Track A and Track B manuscripts. A sensitivity sweep on
`min_abs_corr` (≥3 values) is reported for complex regions as a
supplementary table.

---

### REQ-NEGATIVE-CONTROLS [AB]

**Source:** Pre-pivot REQ-7; `GSD_BRIEFING.md` §5.2 gap #7.

**Rule:** At least three negative-control gene / pathway sets must be tested
in coloc and pathway enrichment outputs and must not show spurious
colocalization or enrichment. Standard choices: HLA (immune), pigmentation
genes (OCA2, SLC24A5, MC1R), blood-group genes (ABO, FUT1/FUT2). Verified
in Stage 2 (224 negative-control rows, all null per
`TRACK-A-FROZEN-NUMBERS.md` §Negative-control). Track B M4 inherits this
gate at genome-wide scale.

**Acceptance:** `config/negative_controls.yaml` exists with ≥3 gene sets
and matching pathway sets. Coloc output includes a negative-control row in
the tier table. Pathway enrichment output includes a negative-control row
in every enrichment table. All sets null (PP.H4 < threshold; enrichment
q > 0.05) in the final report.

---

### REQ-PATH-PARAMETERIZATION [AB]

**Source:** Pre-pivot REQ-12.

**Rule:** All path references go through `config/pipeline.yaml`. No
hardcoded absolute paths in `src/R`, `src/python`, `src/snakemake`, or
`config/`.

**Acceptance:**
`grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config`
returns 0 matches. Snakemake runs end-to-end on the toy-3-locus dataset
(REQ-SNAKEMAKE-CI) with only `config/pipeline.yaml` values resolved.

---

### REQ-OSF-PREREG [AB]

**Source:** Pre-pivot REQ-11 (tier gating) re-scoped; Amendment §9.

**Rule:** Every Track B discovery claim must be pre-registered on OSF
before execution. The M2 MTAG / CPASSOC discovery phase is BLOCKED until
the OSF amendment per Amendment §9 is publicly posted at osf.io/pvb5j and
cross-linked from the existing amendment record at osf.io/az52u. Track A
inherits the root pre-registration at osf.io/pvb5j (DOI
10.17605/OSF.IO/PVB5J).

**Acceptance:** OSF amendment PDF saved under `.planning/amendments/`
with filename pattern `osf-amendment-m0-2026-04-XX.pdf` (date finalized
on submission). M2 Snakemake target `run_mtag_overlap` has a guard that
refuses to execute until the amendment PDF is present.

---

### REQ-PP.H4-THRESHOLD-SWEEP [A]

**Source:** Pre-pivot REQ-3; Phase 2 artifacts.

**Rule:** Track A reports tier counts across PP.H4 ∈ {0.5, 0.7, 0.8, 0.9}.
Track B M4 reports region-level PP.H4 FDR correction instead (REQ-TWO-STAGE-COLOC
below).

**Acceptance:** `config/pph4_thresholds.yaml` exists; Track A supplementary
tables include a sensitivity figure showing tier counts at each threshold.

---

### REQ-EQUITY-FRAMING [B]

**Source:** Pre-pivot REQ-8; `GSD_BRIEFING.md` §5.2 gap #8;
`Revision_Plan.md` §2 / §3.9.

**Rule:** The manuscript must not claim "equitable polygenic risk prediction"
or analogous cross-ancestry parity as a win. Ancestry-stratified results
are framed as quantified trade-offs. AFR numbers are reported at
power-corrected detection probability. Applies to Track B M6 manuscript.

**Acceptance:** `docs/methods/equity_framing.md` exists and is referenced
from abstract, intro, and discussion of the Track B manuscript draft. The
discussion cites explicit numbers for AFR vs. EUR on both accuracy and
calibration metrics.

---

## New Track B requirements (Amendment §§3, 5, 6, 7)

The Track B novel-variant discovery aim is organized into five operationally
defined novelty classes per Amendment §7.1 (joint-signal, AFR-specific,
secondary-independent, pleiotropy-class, functional-mechanism). Each
novelty class is encoded as its own REQ (REQ-NOVELTY-CLASS-1 through
REQ-NOVELTY-CLASS-5) with acceptance tests tied to Amendment §7.1
thresholds and to the locked comparator-catalog manifest
(REQ-CATALOG-VERSION-LOCK).


### REQ-TRAIT-INVENTORY [B]

**Source:** Amendment §4.

**Rule:** Track B analyzes 9 traits × up to 2 ancestries per the locked
Amendment §4 table: BMI, T2D, stroke, SBP, asthma, CAD, lipids (LDL
primary; HDL/TG/TC secondary), eGFR, HbA1c. Ancestry coverage follows §4
column "Ancestry" (EUR primary for all nine; AFR via ancestry-stratified
subfiles from DIAMANTE-AFR, GIGASTROKE-AA, Giri 2019 MVP-AFR, GBMI-AFR,
GLGC-AFR, CKDGen-AFR / Morris 2019, MAGIC-AFR, PAGE / Loh 2022 BMI-AFR,
Aragam 2022 CAD-AFR where released). Phenotype definitions locked per §4
"Phenotype lock" column (stroke = all-stroke, not ischemic-only; LDL-C
continuous primary; eGFR creatinine-based continuous). M1 verifies
ancestry and sample-overlap flags per trait.

**Acceptance:** `config/trait_inventory.yaml` enumerates 9 traits ×
ancestry coverage per Amendment §4; harmonized sumstats exist for every
(trait, ancestry) cell listed before M2 begins.

---

### REQ-MTAG-OVERLAP [B]

**Source:** Amendment §3 M2, §6, §10 risk row on MTAG overlap.

**Rule:** MTAG (Turley 2018) applied with `--overlap` using the LDSC
pairwise intercept matrix for UKB / MVP cohort overlap correction.
`max_FDR` filter per Turley 2018 to control constant-covariance-assumption
violation. mtCOJO (Zhu 2018) sensitivity check on top-N MTAG-novel loci
where overlap is extreme.

**Acceptance:** LDSC pairwise rg intercept matrix exists for all 9-trait
ancestry-stratified pairs; MTAG output tables include `max_FDR` column;
≥1 mtCOJO sensitivity table exists for MTAG-novel loci.

---

### REQ-CPASSOC-ORTHOGONAL [B]

**Source:** Amendment §3 M2, §6.

**Rule:** CPASSOC (Zhu 2015) SHom / SHet statistics applied as orthogonal
joint-signal test (does not assume constant covariance) for cross-method
corroboration of MTAG novel loci.

**Acceptance:** CPASSOC per-locus output tables exist; MTAG ∩ CPASSOC
intersection is reported as the high-confidence Class 1 (joint-signal)
novelty subset per REQ-NOVELTY-CLASS-1.

---

### REQ-TWO-STAGE-COLOC [B]

**Source:** Amendment §3 M4.

**Rule:** Two-stage coloc: fast ABF-coloc (Giambartolomei 2014) genome-wide
first as triage filter; SuSiE-RSS (Wallace 2020; Zou 2022) only on regions
with PP.H4 > 0.5. Region-level PP.H4 FDR correction on the combined table.

**Acceptance:** Pipeline produces per-region ABF PP.H4 column and
SuSiE-RSS outputs restricted to PP.H4 > 0.5 regions; FDR-corrected
region table exists.

---

### REQ-HYPRCOLOC-MULTI [B]

**Source:** Amendment §3 M4, §6, §10 HyPrColoc risk row.

**Rule:** HyPrColoc (Foley 2021) applied for simultaneous colocalization
across ≥3 traits, capped at 3–5 traits per block per §10 risk mitigation.
Sensitivity check against pairwise coloc on all pairs within each
HyPrColoc block.

**Acceptance:** HyPrColoc output with `regional_prob ≥ 0.8` tables;
pairwise-coloc sensitivity table for each ≥3-trait block.

---

### REQ-POLYFUN-RESCUE [B]

**Source:** Amendment §3 M4, §6; Weissbrod 2020.

**Rule:** PolyFun baselineLF2 functional priors (Weissbrod 2020) applied
to SuSiE credible sets for rescue of underpowered signals, especially in
AFR where N is lower.

**Acceptance:** Rescued credible-set table labeled with PolyFun vs
uniform-prior PIP; rescue count reported per ancestry.

---

### REQ-L2G-GENE-PRIORITIZATION [B]

**Source:** Amendment §3 M5, §6; Mountjoy 2021.

**Rule:** Open Targets Locus2Gene (Mountjoy 2021) applied as a secondary
gene-prioritization axis independent of coloc / eQTL.

**Acceptance:** Per-Tier-A credible-set L2G top-3 gene column in the
gene-prioritization table.

---

### REQ-BORZOI-VARIANT-EFFECT [B]

**Source:** Amendment §3 M5, §6; Linder 2024.

**Rule:** Borzoi variant-effect scoring applied to Tier A credible-set
variants with per-tissue-track scores. Linder 2024 training-distribution
caveats documented; Class 5 functional-mechanism novelty treated as
supplementary context, not primary claim, per Amendment §7.3.

**Acceptance:** Borzoi per-variant tissue-specific score column for every
Tier A credible-set variant; methods-paragraph caveat present.

---

### REQ-NOVELTY-CLASS-1 [B]

**Source:** Amendment §7.1 Class 1 operational definition.

**Rule:** Joint-signal novelty via MTAG / CPASSOC. Operational definition:
(MTAG p < 5e-8 OR CPASSOC p < 5e-8) AND max(single-trait p) ≥ 5e-8 AND no
single-trait GWS hit within ±500 kb in GWAS Catalog v_lock. High-confidence
subset = MTAG ∩ CPASSOC.

**Acceptance:** `joint_signal_novel.tsv` exists with one row per claimed
locus and columns for MTAG p, CPASSOC p, max single-trait p, nearest
GWAS Catalog v_lock entry, confidence tier.

---

### REQ-NOVELTY-CLASS-2 [B]

**Source:** Amendment §7.1 Class 2 operational definition.

**Rule:** AFR-specific novelty. Operational definition: AFR PP.H4 ≥ 0.8
with |CS| ≤ 25 AND (no overlapping EUR coloc signal at the same locus OR
AFR lead variant has MAF_AFR ≥ 0.01 with MAF_EUR < 0.005).

**Acceptance:** `afr_specific_novel.tsv` with AFR PP.H4, AFR CS size,
EUR-overlap flag, MAF_AFR, MAF_EUR per claimed locus.

---

### REQ-NOVELTY-CLASS-3 [B]

**Source:** Amendment §7.1 Class 3 operational definition; §10 secondary-signal
LD-sensitivity risk row.

**Rule:** Secondary-independent credible-set novelty. Operational definition:
SuSiE-RSS CS index ≥ 2 AND CS purity ≥ 0.5 AND PIP_max(CS) ≥ 0.5 AND lead
variant of CS index ≥ 2 not within ±100 kb of prior GWAS Catalog v_lock
entry for the same trait. Cross-panel LD-sensitivity parity check per
Amendment §10 risk row: secondary CSs that appear in one LD panel but not
another are downgraded.

**Acceptance:** `secondary_signals.tsv` with region, CS index, purity,
PIP_max, lead variant, nearest GWAS Catalog v_lock entry. Cross-panel
parity-check column present.

---

### REQ-NOVELTY-CLASS-4 [B]

**Source:** Amendment §7.1 Class 4 operational definition.

**Rule:** Pleiotropy-class novelty. Operational definition: cross-trait
PP.H4 ≥ 0.8 (pairwise) or HyPrColoc regional_prob ≥ 0.8 (≥3 traits) AND
not present as cross-trait shared in {Pickrell 2016 supplement, Watanabe
2019 GWAS Atlas, Open Targets L2G top-3} as locked on M5 cross-reference
date.

**Acceptance:** `pleiotropy_novel.tsv` with trait-pair-locus rows, PP.H4 /
regional_prob, Pickrell-2016 status, Watanabe-2019 status, L2G top-3 status.

---

### REQ-NOVELTY-CLASS-5 [B]

**Source:** Amendment §7.1 Class 5, §7.3 (supplementary scope).

**Rule:** Functional-mechanism novelty (SUPPLEMENTARY, not primary claim).
Operational definition: max-tissue Borzoi / Enformer score in top decile
across the credible set AND no ClinVar pathogenic / likely-pathogenic entry
AND no primary-literature functional characterization (PubMed search via
mcp__claude_ai_PubMed).

**Acceptance:** `functional_novel.tsv` reported as supplementary; methods
paragraph explicitly labels Class 5 as supplementary.

---

### REQ-CATALOG-VERSION-LOCK [B]

**Source:** Amendment §7.2, §10 catalog-drift risk row.

**Rule:** All comparator catalog versions (GWAS Catalog, Pickrell 2016,
Watanabe 2019, Open Targets L2G, ClinVar) locked at the M5 cross-reference
date with SHA-256 checksums and download URLs reported in the manuscript
supplement. Delta-analysis between lock-date and submission-date catalogs
if catalog drift occurs during review.

**Acceptance:** `catalog_lock_manifest.tsv` exists with catalog name,
version, download URL, SHA-256, lock-date.

---

### REQ-AOU-LD-EGRESS [B]

**Source:** Amendment §3 M3, §5; `AOU-LD-PIPELINE.md` §§7, 13.

**Rule:** Track B AFR LD reference is built inside the All of Us Researcher
Workbench (Terra) from controlled-tier WGS (~60–95k AFR post-QC). Only
summary-level artifacts (LD matrix + AF metadata) exported per AoU
data-egress policy. No individual-level data leaves the Workbench. Zero
cells computed from <20 participants (trivially satisfied at n ≈ 60k AFR).
AoU P&P draft registered before any Dataproc compute; RPS filed per
`AOU-LD-PIPELINE.md` §2.1; export request categorized as aggregate summary
statistics with written AoU classification (per AOU-LD-PIPELINE Amendment
§10 risk R1).

**Acceptance:** AoU P&P draft registration filed; RPS approved; AoU egress
classification in writing; per-region `.npz` LD files + AF metadata land
on GPFS under `data/processed/ld_reference/AFR_aou/`; conversion to `.rds`
per `AOU-LD-PIPELINE.md` §8.2.

---

### REQ-AOU-LD-VALIDATION [B]

**Source:** `AOU-LD-PIPELINE.md` §9.

**Rule:** Before any AoU-derived LD is admitted to production DAGs, the
four-check validation protocol passes on a 10-region dev subset:
(1) known-locus LD pattern matches published AFR figures;
(2) AoU EUR vs 1000G EUR entry-wise r ≥ 0.97 for MAF ≥ 0.05;
(3) SuSiE-RSS converges on 16q12 BMI AFR with CS size ≤ 30 and lead
    PIP ≥ 0.1;
(4) AoU-AFR vs identity-placeholder A/B documented for the 10 regions.

**Acceptance:** `.planning/phases/m3-aou-afr-ld-panel-build/validation/`
contains check outputs; validation memo committed before scale-up.

---

### REQ-REPLICATION-HOLDOUT [B]

**Source:** Amendment §3 M6.

**Rule:** Hold-out replication on FinnGen R13+ / Pan-UKBB / MVP release n+1
where available for Tier A claimed loci and novel-variant classes 1–4.

**Acceptance:** Per-class replication table with point estimate, 95% CI,
sign agreement, and post-hoc power per replication cohort.

---

## REQ ID cross-reference

| REQ ID | Milestone(s) | Track | Prior-pivot origin |
|---|---|---|---|
| REQ-SNAKEMAKE-CI | M0, M1, M2, M3, M4, M5, M6, Track-A-finalization | AB | pre-pivot REQ-9 |
| REQ-PUBLIC-DATA-ONLY | M0, M1, M2, M3, M4, M5, M6, Track-A-finalization | AB | pre-pivot DECISIONS 2026-04-09 |
| REQ-SUSIE-RSS-POLICY | M4, Track-A-finalization | A | pre-pivot REQ-2 |
| REQ-NEGATIVE-CONTROLS | M4, Track-A-finalization | AB | pre-pivot REQ-7 |
| REQ-PATH-PARAMETERIZATION | M0, M1, M2, M3, M4, M5, M6, Track-A-finalization | AB | pre-pivot REQ-12 |
| REQ-OSF-PREREG | M2, Track-A-finalization | AB | pre-pivot REQ-11 re-scoped |
| REQ-PP.H4-THRESHOLD-SWEEP | Track-A-finalization | A | pre-pivot REQ-3 |
| REQ-EQUITY-FRAMING | M6 | B | pre-pivot REQ-8 |
| REQ-TRAIT-INVENTORY | M1 | B | new (Amendment §4) |
| REQ-MTAG-OVERLAP | M2 | B | new (Amendment §3 M2) |
| REQ-CPASSOC-ORTHOGONAL | M2 | B | new (Amendment §3 M2) |
| REQ-TWO-STAGE-COLOC | M4 | B | new (Amendment §3 M4) |
| REQ-HYPRCOLOC-MULTI | M4 | B | new (Amendment §3 M4) |
| REQ-POLYFUN-RESCUE | M4 | B | new (Amendment §3 M4) |
| REQ-L2G-GENE-PRIORITIZATION | M5 | B | new (Amendment §3 M5) |
| REQ-BORZOI-VARIANT-EFFECT | M5 | B | new (Amendment §3 M5) |
| REQ-NOVELTY-CLASS-1 | M2 | B | new (Amendment §7.1 Class 1) |
| REQ-NOVELTY-CLASS-2 | M4 | B | new (Amendment §7.1 Class 2) |
| REQ-NOVELTY-CLASS-3 | M4 | B | new (Amendment §7.1 Class 3) |
| REQ-NOVELTY-CLASS-4 | M5 | B | new (Amendment §7.1 Class 4) |
| REQ-NOVELTY-CLASS-5 | M5 | B | new (Amendment §7.1 Class 5, §7.3) |
| REQ-CATALOG-VERSION-LOCK | M5 | B | new (Amendment §7.2, §10) |
| REQ-AOU-LD-EGRESS | M3 | B | new (AOU-LD-PIPELINE.md §§7, 13) |
| REQ-AOU-LD-VALIDATION | M3 | B | new (AOU-LD-PIPELINE.md §9) |
| REQ-REPLICATION-HOLDOUT | M6 | B | new (Amendment §3 M6) |
