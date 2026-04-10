# ROADMAP.md

Phase index for the coloc_analysis manuscript revision. Tier assignments
are locked per `DECISIONS.md` "Scope tier". Phase numbering follows
`Revision_Plan.md`.

Legend: **T1** = must-ship spine. **T2** = conditional on Checkpoint #1
(end of T1). **T3** = conditional on Checkpoint #2 (end of T2). **M** =
manuscript work (runs in parallel with later phases).

---

## Milestone: Pre-revision → submission-ready revision

| # | Phase | Tier | Status | Depends on | Maps to REQ |
|---|---|---|---|---|---|
| **0** | Data access + infrastructure | T1 | planned | — | REQ-1, REQ-9, REQ-12 |
| **1** | coloc.susie fine-mapping spine | T1 | not started | Phase 0 | REQ-2 |
| **2** | 3-way QTL colocalization | T1 | not started | Phase 1, Track 0a DUAs | REQ-3, REQ-7 |
| **5** | Pathway + partitioned heritability | T1 | not started | Phase 1 | REQ-7 |
| **9** | Replication in independent cohorts | T1 | not started | Phases 1, 2, Track 0a DUAs | — |
| **CP#1** | **Checkpoint #1** (end of T1 — go/no-go for T2) | — | — | Phases 0, 1, 2, 5, 9 | REQ-11 |
| **3** | Mendelian randomization | T2 | gated | CP#1 | REQ-4 |
| **4** | Matched-N cross-ancestry concordance | T2 | gated | CP#1 | — |
| **8** | Cross-ancestry PRS (PRS-CSx) | T2 | gated | CP#1 | REQ-6, REQ-8 |
| **CP#2** | **Checkpoint #2** (end of T2 — go/no-go for T3) | — | — | Phases 3, 4, 8 | REQ-11 |
| **6** | Selection scans + polygenic selection | T3 | gated | CP#2 | REQ-5 |
| **7** | Single-cell + EpiMap + ABC | T3 | gated | CP#2 | — |
| **10** | Deep-learning variant effect + MPRA overlap | T3 | gated | CP#2 | — |
| **11** | Manuscript + figures + submission | M | in parallel | Phase 9 onward | REQ-8, REQ-10 |

---

## Phase detail

### Phase 0 — Data access + infrastructure (T1)

Runs as **two parallel sub-tracks**.

**Track 0a — DUA applications (non-blocking):**
- UK Biobank (main), UKB-PPP, deCODE pQTL, FinnGen (latest release), MVP,
  All of Us (Researcher Workbench), BBJ, Pan-UKBB.
- Tracked in `.planning/data_access.md`.
- Does **not** block any later phase until a specific DUA-gated slice is
  reached.

**Track 0b — Infrastructure (blocks Phase 1):**
1. Fix corrupted supplementary tables (Table 1, 3, S4) per `Revision_Plan.md` §10.
2. Audit DIAMANTE T2D dedup (resolve the 76 / 63% / 26 denominator mismatch).
3. Drop KCNJ11 asthma-HTN Tier-1 signal (n_SNPs=6 < ≥50 threshold).
4. Ingest new ancestry GWAS sumstats: AFR BMI (Gurdasani 2019), AFR HTN
   (Hoffmann), AFR T2D expansion, EAS (BBJ), Hispanic (PAGE / HCHS).
5. Parameterize legacy hardcoded paths via `config/pipeline.yaml` (REQ-12).
6. Pin conda envs under `envs/*.yml` with exact versions (REQ-9).
7. Build Snakemake skeleton with per-trait/ancestry schema validation.
8. Build the **toy 3-locus subset** for nightly CI smoke test (REQ-9).
9. OSF pre-registration submission.
10. Repoint / remove the broken `harmonized_fixed` symlink (already done at
    bootstrap — remains in the archived shadow dirs).
11. Track 0a DUA application tracker live.

### Phase 1 — coloc.susie fine-mapping spine (T1)

1. SuSiE-RSS fine-mapping per trait × ancestry. Seeds from
   `src/legacy/region_analysis/scripts/run_susie_rss.R`.
2. **Complex-region policy:** convergence handling, `L` cap rules,
   `min_abs_corr` sensitivity sweep (REQ-2).
3. coloc.susie on credible-set pairs — **replaces `coloc.abf`** in both
   `src/legacy/region_analysis/scripts/run_coloc.R` and
   `src/legacy/genome_wide/scripts/run_coloc_genomewide.R`.
4. Sensitivity sweep on coloc prior `p12 ∈ {1e-6, 1e-5, 1e-4}`.
5. Output: credible sets + per-pair PP.H4 + per-locus fine-mapping QC report.

### Phase 2 — 3-way QTL colocalization (T1, highest-leverage)

1. GTEx v8 eQTL coloc per tissue, cross-referenced to Open Targets Locus2Gene.
2. UKB-PPP + deCODE pQTL coloc *(blocked on Track 0a DUAs)*.
3. sQTL coloc (GTEx sQTL).
4. Single-cell eQTL coloc (OneK1K, CLUES) — cell-type resolved.
5. Causal gene × tissue × cell-type matrix assembly.
6. **PP.H4 threshold sweep** (REQ-3) across `{0.5, 0.7, 0.8, 0.9}`.
7. **Negative controls** (REQ-7): HLA, pigmentation, eye-color gene sets.
8. Tier A / B / C confidence assignment with reported threshold dependence.

### Phase 5 — Pathway + partitioned heritability (T1)

*Phase 5 is promoted ahead of 3 and 4 because it's part of the T1 spine.*

1. MAGMA gene-based + gene-set enrichment.
2. g:Profiler with **discoverability-matched null** (per-trait background).
3. LDSC partitioned heritability — % heritability per pathway, per trait.
4. LDSC-SEG tissue-specific heritability.
5. HESS local genetic covariance between trait pairs.
6. Permutation null for the colocalization gene list.
7. **Negative-control pathway set** (REQ-7).

### Phase 9 — Replication in independent cohorts (T1)

1. FinnGen replication *(DUA-gated)*.
2. GBMI replication.
3. MVP replication *(DUA-gated)*.
4. All of Us replication *(DUA-gated)*.
5. BBJ replication *(DUA-gated)*.
6. Replication-adjusted effect sizes + hold-out replication tables.

---

### Checkpoint #1 — End of T1 spine

**Produces:** `.planning/checkpoints/T1_review.md` with:
- Tier A signals that survived the PP.H4 sweep + replication.
- Ancestry-level power retention under matched-N preview expectations.
- Go / no-go decision for T2 phases with explicit evidence.
- Submission target: AJHG (T1 alone) vs. Nat Genet pivot (proceed to T2).

**No T2 phase is planned until this file exists with a "go" verdict.**

---

### Phase 3 — Mendelian randomization (T2, gated)

1. IVW + MR-Egger + weighted median (baseline triangulation).
2. MR-PRESSO + MR-CAUSE (outlier robustness).
3. Steiger filtering.
4. Locus-specific MR using coloc.susie credible sets as instruments.
5. **Weak-instrument mitigation** (REQ-4): MR-RAPS for AFR/EAS, trans-
   ancestry MR, explicit ancestry-specific vs. trans-ancestry choice.
6. Bidirectional causal graph across trait pairs.

Seeds from `src/legacy/region_analysis/scripts/create_mr_design.py` +
`src/legacy/region_analysis/workflow/rules/mr.smk` (both currently stubs).

### Phase 4 — Matched-N cross-ancestry concordance (T2, gated)

**Replaces the broken Table 2.**

1. Down-sample EUR to match AFR N; 100× bootstrap concordance.
2. Expected detection probability under Hou et al. 2023 null.
3. TRACTOR for AFR-American ancestry-stratified effects.
4. LDSC cross-ancestry `r_g` as global benchmark.
5. Ancestry-specific variant testing.
6. **New Table 2:** power-corrected concordance replacing the old
   incomparable-trait-pair comparison.

### Phase 8 — Cross-ancestry PRS (T2, gated)

1. PRS-CSx training in EUR.
2. Transfer to AFR / EAS / Hispanic.
3. Pathway-restricted vs. genome-wide PRS comparison.
4. **Discrimination:** R², AUC (REQ-6).
5. **Calibration:** Hosmer-Lemeshow, calibration slope + intercept (REQ-6).
6. **Clinical utility:** NRI, decision-curve analysis, net benefit (REQ-6).
7. **Equity-vs-accuracy trade-off** quantification (REQ-8).

Seeds from `src/legacy/region_analysis/scripts/create_pgs_manifest.py` +
`src/legacy/region_analysis/workflow/rules/pgs.smk` (both currently stubs).

---

### Checkpoint #2 — End of T2

**Produces:** `.planning/checkpoints/T2_review.md` with:
- Are T1+T2 results a Nature Genetics story or a Nature Metabolism story?
- Is T3 worth the schedule risk?
- Updated journal target decision.

**No T3 phase is planned until this file exists.**

---

### Phase 6 — Selection scans + polygenic selection (T3, gated)

1. iHS, SDS, PBS, XP-EHH across 1000G + HGDP.
2. Pathway-level enrichment of selection signatures.
3. Thrifty-gene and antagonistic-pleiotropy hypothesis tests.
4. **Pre-specified fallback framing** (REQ-5) — written **before**
   execution — that reframes the narrative around locus-level signals if
   the polygenic test is null.

### Phase 7 — Single-cell + EpiMap + ABC (T3, gated)

1. Cell-type-resolved eQTL integration.
2. Roadmap / EpiMap chromatin state overlap.
3. ABC enhancer-gene linking model.
4. CELLECT / scDRS enrichment.

### Phase 10 — Deep-learning variant effect + MPRA overlap (T3, gated)

1. Enformer inference per credible-set variant.
2. Borzoi inference.
3. Sei regulatory activity.
4. AlphaMissense coding-variant scores.
5. Overlap with public MPRA datasets (Abell 2022, Tewhey 2016).
6. Composite functional-evidence score per variant.

---

### Phase 11 — Manuscript + figures + submission (M, parallel)

Runs in parallel with Phase 9 onward.

1. Figure regeneration (Figures 1-6 from new data).
2. New Table 2 (matched-N) + regenerated Tables 1, 3.
3. Methods rewrite — one subsection per analytical phase.
4. Response-to-reviewers framework (pre-submission, forces rigor).
5. **Equity-as-trade-off framing** reconciled across abstract / intro /
   discussion (REQ-8).
6. Target journal selection cover letters (REQ-10).
7. OSF final registration update + data deposit.
8. GitHub repo public release + Zenodo DOI.
9. Submission package assembly.
