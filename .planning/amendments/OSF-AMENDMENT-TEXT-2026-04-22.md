# OSF Amendment — Paste-Ready Text (Route B genome-wide reframe)

> **This file is the posting artifact.** The design rationale for the amendment
> lives in [PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md).
> This file contains ONLY the OSF web-UI paste-ready body, bracketed by
> `--- PASTE INTO OSF FROM HERE ---` / `--- PASTE ENDS HERE ---` markers.

---

## Pre-Paste Reference (do NOT paste this block)

| Field | Value |
|---|---|
| Target OSF project | [osf.io/az52u](https://osf.io/az52u) |
| Amendment kind | Body text of a new registered amendment record on the parent project. |
| Original pre-registration being amended | [osf.io/pvb5j](https://osf.io/pvb5j) (DOI `10.17605/OSF.IO/PVB5J`), posted 2026-04-10. |
| Supersedes-but-incorporates | Phase 1 closeout amendment posted 2026-04-13 at `osf.io/az52u` (distal-gene expansion, PDF only, no local source). Not retracted; this amendment extends it. |
| Posting gate | M1 sumstats harmonization COMPLETE with per-trait SHA-256 checksums frozen. BEFORE any MTAG or CPASSOC discovery run executes in M2. Per Amendment §9.1 — "Carter confirmed this sequencing." |
| Catalog lock manifest | [`data/catalogs/catalog_lock_manifest.tsv`](../../data/catalogs/catalog_lock_manifest.tsv) — M0 snapshot commit `0a1339e` (ClinVar locked, 4 catalogs M5-deferred). |
| Expected posting date | `2026-[M1 completion month]` — fill in before paste. |
| Attachment | Optional: attach PDF export of [PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md) as supplementary material if OSF form allows. |

**Pre-paste checklist (work top-to-bottom before submitting the OSF form):**

1. Fill the `2026-[M1 completion month]` placeholder in the Date field with the actual M1 completion date (`YYYY-MM-DD`).
2. Replace the `<M1 commit hash>` placeholder in the "What is not changing" paragraph with the HEAD commit hash of the M1 closeout.
3. Replace the `<M5-locked catalog commit hash>` placeholder with the commit hash from the M5 lock-refresh commit (at M5, when the M5-deferred rows in `catalog_lock_manifest.tsv` are populated with SHA-256). If posting at end of M1 before M5 runs, leave as `<M5 lock commit hash TBD>` and add a one-line note at the bottom of the amendment: "Catalog lock commit hash will be added as a follow-up OSF update at M5 cross-reference date; the URL path to the manifest is stable."
4. Verify the `data/catalogs/catalog_lock_manifest.tsv` reference in Paragraph 5 still has the ClinVar SHA-256 `3be9939676e44a79e906dd167caec45e6e871be55db1a4ddb9269ebf0828e58e` (it will, unless the M0 snapshot has been intentionally rewritten).

---

--- PASTE INTO OSF FROM HERE ---

**Amendment to pre-registration osf.io/pvb5j: genome-wide pleiotropy discovery expansion**

**Date:** 2026-[M1 completion YYYY-MM-DD]

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of amendment:** This amendment expands the scope of the coloc_analysis pre-registration from a candidate-locus analysis across 5 traits to a genome-wide, joint-signal, multi-trait analysis across 9 traits in EUR and AFR ancestries with two co-equal pre-registered scientific aims: (i) cross-trait pleiotropy discovery, and (ii) novel single-trait and joint-signal variant discovery. The original candidate-locus analysis is retained as a pre-specified methods-validation subset and will be reported separately (see "Track A" below).

**Motivation:** The original candidate-locus design identified 50 hand-curated regions tiled into 205 analysis windows around 8 seed pleiotropic loci drawn from published cross-trait literature. Fine-mapping and colocalization within this set quantifies the replication rate of prior claims under current best-practice methods (SuSiE-RSS with real, matched-ancestry LD), which is informative but does not itself support discovery-level inference about the broader genomic architecture of pleiotropy. Non-circular discovery requires genome-wide region generation using multi-trait methods (MTAG, Turley et al. 2018, *Nature Genetics*; CPASSOC, Zhu et al. 2015, *American Journal of Human Genetics*).

**Expanded trait inventory (9 traits × 2 ancestries, 18 trait-ancestry combinations):**

1. BMI — Yengo 2022 EUR; PAGE + All of Us AFR. Continuous, inverse-rank-normal transformed.
2. Type 2 diabetes — DIAMANTE 2022 (Mahajan et al., *Nature*). Trans-ancestry case-control.
3. Stroke — GIGASTROKE 2022 (Mishra et al., *Nature*). Trans-ancestry all-stroke case-control.
4. Systolic blood pressure — Evangelou 2018 EUR (*Nature Genetics*); Giri 2020 AFR in MVP (*Hypertension*). Continuous.
5. Asthma — GBMI 2022 (Zhou et al., *Cell Genomics*). Trans-ancestry pooled adult + child.
6. Coronary artery disease — Aragam 2022 EUR (*Nature Genetics*). Case-control.
7. Lipids — GLGC 2021 (Graham et al., *Nature*) multi-ancestry. LDL-C primary; HDL, TG, TC secondary.
8. Estimated glomerular filtration rate — CKDGen 2019 (Wuttke et al., *Nature Genetics*) multi-ancestry continuous.
9. Hemoglobin A1c — MAGIC 2021 (Chen et al., *Nature Genetics*) multi-ancestry continuous.

**New analytical commitments:**

(a) Per-ancestry PLINK clumping (p < 5 × 10⁻⁸, r² < 0.01, 1 Mb window) with MTAG and CPASSOC novel loci added to the union region list for downstream fine-mapping.

(b) MTAG with LDSC-intercept-based `--overlap` correction for UK Biobank and MVP cohort overlap, with the `max_FDR` filter enabled to control constant-covariance assumption violations.

(c) Two-stage colocalization: coloc (approximate-Bayes-factor triage) followed by SuSiE-RSS on regions with PP.H4 > 0.5, with region-level PP.H4 false-discovery-rate correction reported alongside raw posteriors.

(d) HyPrColoc for shared-architecture inference across three or more traits.

(e) PolyFun baselineLF2 functional priors for rescue of underpowered credible sets.

(f) All of Us Controlled Tier Whole Genome Sequencing (~100,000 AFR individuals) as the AFR LD reference panel, computed inside the All of Us Researcher Workbench with only summary-level LD matrices exported per the All of Us data-egress policy. This replaces 1000 Genomes AFR (N = 661) as the AFR LD default — an approximately 150-fold sample size upgrade.

(g) Locus-to-gene (L2G) scores from Open Targets Genetics (Mountjoy 2021, *Nature Genetics*) and Borzoi (Linder 2024, *Nature Genetics*) deep-learning variant effect predictions for gene-level and variant-level prioritization on Tier A signals.

**Pre-registered novel-variant discovery aim:** In addition to cross-trait pleiotropy claims, this analysis pre-registers four operational definitions of variant-level novelty, each with a locked comparator catalog. Catalog versions, download URLs, SHA-256 checksums, and fetch dates are tracked in the companion repository at `data/catalogs/catalog_lock_manifest.tsv` (M0 snapshot 2026-04-24 locks ClinVar `2026-04-20_weekly_release` with SHA-256 `3be9939676e44a79e906dd167caec45e6e871be55db1a4ddb9269ebf0828e58e`; the Pickrell 2016 supplement, GWAS Catalog, Open Targets Genetics L2G, and Watanabe 2019 GWAS Atlas are pinned by URL + best-known version at M0 and will be fetched and SHA-256-locked at the M5 cross-reference date, commit hash `<M5-locked catalog commit hash>`). The four operational definitions:

(i) **Novel joint-signal loci** = (MTAG p < 5 × 10⁻⁸) OR (CPASSOC p < 5 × 10⁻⁸), AND no contributing single-trait association at p < 5 × 10⁻⁸ within ±500 kb per GWAS Catalog v_lock.

(ii) **Novel ancestry-specific loci (AFR)** = AFR PP.H4 ≥ 0.8 with credible-set size ≤ 25, OR AFR single-trait lead variant at p < 5 × 10⁻⁸ with no overlapping EUR signal at p < 1 × 10⁻⁵ within ±500 kb.

(iii) **Novel pleiotropy loci** = cross-trait PP.H4 ≥ 0.8 (pairwise coloc) or HyPrColoc PP ≥ 0.8 (three or more traits), AND not reported as cross-trait shared in {Pickrell 2016 *Nature Genetics* supplement, Watanabe 2019 GWAS Atlas, Open Targets Genetics L2G top-3 gene assignments} at v_lock.

(iv) **Novel secondary-signal loci** = SuSiE-RSS credible-set index ≥ 2 with credible-set purity ≥ 0.5 and PIP_max ≥ 0.5, AND lead variant of secondary credible set not within ±100 kb of a prior GWAS Catalog v_lock entry for the same trait.

Functional-mechanism novelty driven by Borzoi and Enformer top-decile scores cross-referenced against ClinVar v_lock is reported as supplementary mechanistic context, not a primary novelty claim.

**Track A (pre-specified methods-validation subset):** The original 50-region candidate-locus analysis has been completed and will be published as a separate short-form methods paper reporting the fraction of published cross-trait pleiotropy claims in the candidate set that survive real, matched-ancestry LD re-analysis. Track A is pre-specified validation ahead of Track B discovery and does not involve any data-dependent region reselection.

**What is superseded by this amendment:**

- Candidate-locus design → genome-wide, hypothesis-agnostic region generation.
- 5 traits (BMI, type 2 diabetes, hypertension, stroke, asthma) → 9 traits (above list adds systolic blood pressure, coronary artery disease, lipids, estimated glomerular filtration rate, and hemoglobin A1c).
- Identity-LD / mismatched-ancestry LD → real, matched-ancestry LD with All of Us AFR Whole Genome Sequencing as the AFR reference panel.
- Single-trait discovery only → MTAG + CPASSOC joint-signal discovery plus HyPrColoc triangulation.
- Post-hoc novelty comparison → pre-registered novelty definitions against locked comparator catalogs (SHA-256 in the companion manifest).

**What is not changing:**

- Pre-registration discipline. Hypotheses, thresholds, comparator catalogs, and analytical commitments are fixed before discovery execution. Any deviation during execution is logged in `.planning/osf_deviations.md` and disclosed in the manuscript's "Deviations from pre-registration" section.
- Multi-method triangulation. Colocalization, Mendelian randomization, and selection analyses remain the triangulation scaffold; MTAG + CPASSOC extend rather than replace this approach.
- Ancestry-stratified analysis plan: trans-ancestry discovery followed by ancestry-stratified replication and concordance testing. AFR is a co-equal ancestry, not a post-hoc extension.
- Public-data-only commitment. No wet-lab validation, no proprietary industry datasets, no PI-specific cohort access beyond standard academic DUAs.
- Snakemake-pinned pipeline with conda environment specifications will be released alongside the manuscript.
- OSF deposit of all post-registration outputs: harmonized summary statistics checksums, credible sets, colocalization posteriors, novelty calls, and figure-generating scripts.
- Hold-out replication commitment: independent cohorts (FinnGen R12, GBMI, MVP dbGaP phs001672, All of Us Controlled Tier, BBJ PheWeb-JP, Pan-UKBB) remain as the replication strata for Tier A signals.
- CC0 1.0 Universal license on all pre-registration and post-registration artifacts.

**Expected timeline:** This amendment is posted at the end of M1 (sumstats harmonization complete; per-trait SHA-256 checksums frozen at repository commit `<M1 commit hash>`). M2–M6 follow. The full milestone table and per-phase success criteria are available in the companion repository at `.planning/ROADMAP.md`; the amendment design rationale is at `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`.

--- PASTE ENDS HERE ---

---

## Post-Paste Reference (do NOT paste this block)

**Verification checklist after OSF posting:**

1. Confirm OSF assigned a timestamp to the amendment and the timestamp precedes any commit containing M2 MTAG or CPASSOC analysis outputs. If timestamp-precedence is violated, post a subsequent deviation log entry immediately in `.planning/osf_deviations.md`.
2. Copy the OSF amendment record URL (e.g., `osf.io/<record-id>`) back into the local repository at `.planning/osf_deviations.md` under a new dated entry.
3. Tag the repository commit that represents the M1 closeout + amendment-post gate with `git tag M1-OSF-AMENDMENT-POSTED-YYYY-MM-DD`.
4. Append a new entry to [DECISIONS.md](../DECISIONS.md) (`DEC-YYYY-MM-DD-XX: OSF amendment posted at osf.io/<record-id>; M2 discovery gate cleared.`).
5. Update [STATE.md](../STATE.md) Session Continuity to mark Route B Step 3.3 as completed.

**If any M1 commitment changes before this amendment is posted** (e.g., a trait source is swapped due to DUA fall-through):

- Pause the OSF posting.
- Update the relevant trait row in this file's "Expanded trait inventory" paragraph.
- Re-run the pre-paste checklist above.
- If the change affects novelty-class definitions, update the corresponding paragraph and the comparator catalog manifest accordingly.

**Rollback:** Do not delete this file. If the amendment is posted and later retracted, add a superseded-by pointer at the top of this file to the new amendment record. OSF amendments are append-only by design.
