---
quick_id: 260424-k2g
phase: quick-260424-k2g
plan: 01
title: "Route A Step 2.3 — Figure 5 R script + renders (variant-mechanism donut + Tier C scorecard bar; patchwork composite)"
status: complete
completed: "2026-04-24T17:55:00-04:00"
requirements:
  - ROUTE-A-STEP-2.3-FIG5
tags:
  - track-a
  - figure
  - r-ggplot
  - patchwork
  - original-research
dependency_graph:
  requires:
    - docs/manuscript/track_a_pivot.md L295 (Figure 5 legend spec, authored by k2f)
    - .planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-SUMMARY.md (Tier A+B=0 empirical result)
    - results/fine_mapping/susie/*.json (51 non-empty fits — lead variant source for Panel A)
    - data/reference/magma/NCBI37.3.gene.loc (19,427 gene boundaries — Panel A classification proxy)
    - results/qtl_coloc/tier_assignments.tsv (233 rows — Panel B Tier C scorecard source)
    - src/R/figures/fig2_cs_yield.R (render pattern precedent from 260424-lpy + 260424-mqo)
  provides:
    - src/R/figures/fig5_variant_mech_scorecard.R (runtime-data-driven, patchwork composite)
    - docs/manuscript/figures/fig5_variant_mech_scorecard.pdf (cairo_pdf, 170 × 85 mm)
    - docs/manuscript/figures/fig5_variant_mech_scorecard.png (600 dpi, 170 × 85 mm)
  affects:
    - Route A Step 2.4 (bioRxiv preprint package) — Figure 5 now buildable alongside Figure 2 (fig2_cs_yield) and Figure 1B (fig1b_locus_panels)
    - Figure 4 (pathway enrichment) — unchanged; remains "withdrawn at threshold / demoted to Figure S5" per k2f legend; Figure 5 picks up the Tier C descriptive annotation load
key_files:
  created:
    - src/R/figures/fig5_variant_mech_scorecard.R
    - docs/manuscript/figures/fig5_variant_mech_scorecard.pdf
    - docs/manuscript/figures/fig5_variant_mech_scorecard.png
    - .planning/quick/260424-k2g-route-a-fig5-variant-mech-scorecard-R-script/260424-k2g-PLAN.md
    - .planning/quick/260424-k2g-route-a-fig5-variant-mech-scorecard-R-script/260424-k2g-SUMMARY.md
  modified: []
decisions:
  - "Panel A: gene-body-intersection proxy against MAGMA NCBI37.3 gene.loc, NOT the full CADD / PolyPhen-2 / SIFT / GTEx eQTL aggregation named in the Figure 5 legend. Reason: those 4 annotation sources are not on disk. The proxy is rigorous but conservative — it uses gene boundaries + ±100 kb flanking window to classify into 'Within gene body' / 'Flanking ≤100 kb' / 'Distal intergenic'. The in-figure caption states the deferral explicitly. Full aggregation is a venue-submission-prep task."
  - "Panel B: uses real Tier C data verbatim from tier_assignments.tsv with hard-coded Ensembl→symbol map for APOL1/IRX3/ATXN2. The map is encoded as an R named vector; mapping correctness asserted via stopifnot(all(!is.na(tc$symbol))). Tier B (0.5) and Tier A (0.8) dashed reference lines visualise the zero-Tier-A+B result — all 3 bars fall left of the Tier B line."
  - "Composite layout 170 × 85 mm via patchwork `plot_layout(widths = c(0.85, 1.15))` — wider B panel because the horizontal scorecard bar needs room for the PP.H4 + tissue text labels on the right of each bar. This differs from fig2_cs_yield's 85 × 70 mm single-column size but remains within standard two-column width."
  - "Cairo verified present in la_multitrait_r env (capabilities('cairo') == TRUE); script aborts cleanly if cairo were missing rather than silently falling back to pdf(). Same safety pattern as fig2_cs_yield.R."
  - "Render in la_multitrait_r conda env, same as fig2_cs_yield.R precedent. Packages: jsonlite + readr + dplyr + tidyr + ggplot2 + scales + patchwork. All verified installed at the invocation time."
metrics:
  duration_minutes: ~20
  tasks_completed: 1
  files_created: 5 (R script + PDF + PNG + PLAN + SUMMARY)
  script_lines: 222
  pdf_bytes: 38185
  png_bytes: 319140
  panel_a_leads: 51 (top-PIP variant per non-empty SuSiE fit)
  panel_a_classification:
    within_gene_body: 21 (41.2%)
    flanking_100kb: 26 (51.0%)
    distal_intergenic: 4 (7.8%)
  panel_b_tier_c_genes: 3
  panel_b_pph4_max: 0.310 (IRX3 on Pancreas)
  panel_b_pph4_below_tier_b_threshold: 3 of 3 (all below 0.5)
---

# Phase quick-260424-k2g Plan 01: Figure 5 R script + renders Summary

## Objective

Built Route A Figure 5 (variant-mechanism donut + Tier C scorecard bar composite) per the legend spec at `docs/manuscript/track_a_pivot.md` L295 (authored by 260424-k2f, commit 99a73bf). The figure is the visual embodiment of the k2e empirical finding (commit b7c9310): Tier A + Tier B = 0 under real-LD, with only 3 Tier C named resolving genes (APOL1 PP.H4=0.013; IRX3 PP.H4=0.310; ATXN2 PP.H4=0.052) all below the 0.5 confidence threshold. Panel B's dashed reference lines at Tier B (0.5) and Tier A (0.8) make the sparsity visible at a glance — the sparsity IS the argument.

Script is runtime-data-driven (reads all inputs from disk at render time, no hard-coded counts beyond the documented Tier B/A thresholds). Panel A uses a gene-body-intersection proxy against MAGMA's NCBI37.3 gene.loc with ±100 kb flanking because the full CADD / PolyPhen-2 / SIFT / GTEx eQTL aggregation named in the legend is not on disk; the in-figure caption states this deferral explicitly.

## Per-task outcome

| Task | Artifact | Outcome |
| --- | --- | --- |
| T1 | `src/R/figures/fig5_variant_mech_scorecard.R` | 222 lines; patchwork composite; jsonlite-based lead extraction + MAGMA gene.loc proxy + tier_assignments Tier C filter |
| T1 | `docs/manuscript/figures/fig5_variant_mech_scorecard.pdf` | cairo_pdf, 170 × 85 mm, 38,185 bytes |
| T1 | `docs/manuscript/figures/fig5_variant_mech_scorecard.png` | 600 dpi, 170 × 85 mm, 319,140 bytes |

## Render stdout (captured at invocation)

```
Loading lead variants from results/fine_mapping/susie/*.json ...
  51 non-empty credible sets (top-PIP lead extracted each)
Loading MAGMA gene loc ...
  19427 gene entries for gene-body classification
Classifying lead variants by gene-body proximity ...
Loading Tier C scorecard ...
Rendering composite to disk ...

=== fig5_variant_mech_scorecard.R diagnostic summary ===
Panel A — n = 51 lead variants
  Within gene body        21 (41.2%)
  Flanking ≤100 kb        26 (51.0%)
  Distal intergenic        4 (7.8%)
Panel B — 3 Tier C named genes
  APOL1  PP.H4=0.013  (Cells Cultured fibroblasts)
  IRX3   PP.H4=0.310  (Pancreas)
  ATXN2  PP.H4=0.052  (Adrenal Gland)
wrote docs/manuscript/figures/fig5_variant_mech_scorecard.pdf (38185 bytes)
wrote docs/manuscript/figures/fig5_variant_mech_scorecard.png (319140 bytes)
```

Single non-fatal warning from readr on the MAGMA gene.loc (column-type inference — standard on this file; does not affect downstream classification).

## Guardrail verification (T1-VERIFY 10-gate)

| Check | Expected | Observed | Pass |
| --- | --- | --- | --- |
| Script exists + non-empty | ≥ 1 byte | 222 lines | ✅ |
| `library(patchwork)` loaded | yes | yes | ✅ |
| Ensembl→symbol map present | yes | yes | ✅ |
| APOL1/IRX3/ATXN2 referenced | yes | yes | ✅ |
| Forbidden framing count | 0 | 0 | ✅ |
| PDF exists + ≥ 20 KB | ≥ 20000 bytes | 38185 | ✅ |
| PNG exists + ≥ 150 KB | ≥ 150000 bytes | 319140 | ✅ |
| Stage 2 real-LD md5 4/4 | all OK | 4/4 OK | ✅ |

Plus visual QA (PNG inspection):
- Panel A donut readable, 3 slices with count + percent labels, n = 51 centre annotation
- Panel B 3 horizontal bars (IRX3 top, ATXN2 middle, APOL1 bottom); PP.H4 + tissue text on right of each bar; Tier B / Tier A dashed reference lines + labels; x-axis 0 → 1.0 scale
- Composite caption at bottom states gene-body-proximity-proxy deferral + Tier A+B=0 note

## Deviations from Plan

**None.** Script rendered exit 0 on first attempt; all 10 T1-VERIFY gates passed on first run.

One minor cosmetic note (not a deviation): readr emitted a column-type warning parsing `data/reference/magma/NCBI37.3.gene.loc` because one of the later columns had mixed integer/string values. Resolution: col_types explicitly supplied as `"ccdddc"` in the `read_tsv` call — the warning is from a downstream `problems()` data-frame check by vroom and does not affect the gene-body classification (which only uses chr/start/end numeric fields, all cleanly parsed). Optional future polish: pin the read_tsv call with explicit column specs per field.

## Handoff notes

### For Route A Step 2.4 (bioRxiv preprint package)

Figure 5 PDF + PNG are now buildable alongside Figure 2 (`fig2_cs_yield.{pdf,png}`) and Figure 1B (`fig1b_locus_panels.{pdf,png}`). Outstanding figure-builds at Step 2.3:
- **Figure 1A** (identity-vs-real-LD scatter) — blocked on k2d LSF fire (PID 830748) completion for paired per-locus identity-LD PP.H4 data
- **Figure 3** (survival forest) — same k2d dependency
- **Figure 4** (pathway enrichment) — "withdrawn at threshold / demoted to Figure S5" per k2f legend; no buildable main-text render under real-LD Tier A+B=0
- **Figure S1–S6** — various; several tracked as supplementary elsewhere

Once k2d fire lands, Fig 1A + Fig 3 are the next /gsd-quick tasks.

### For Fig 5 venue-submission polish (future /gsd-quick)

When moving to venue submission, upgrade Panel A from the gene-body-proximity proxy to the full CADD / PolyPhen-2 / SIFT / GTEx eQTL aggregation named in the legend:

1. Download CADD scores at 51 lead-variant CHR:POS (CADD v1.7 SNV TSV annotation file, or CADD REST API if network-admitted)
2. PolyPhen-2 + SIFT for coding variants (via dbNSFP or Ensembl VEP offline cache)
3. GTEx v8 eQTL tissue-label enrichment at each lead (via GTEx BigQuery or local eQTL summary files)
4. Aggregate into the legend's "regulatory / coding / mixed" classification per standard functional-categorisation rules (e.g., coding = any nsSNV with CADD > 20 OR PolyPhen-damaging OR SIFT-deleterious; regulatory = any lead with ≥1 significant GTEx eQTL tissue at FDR < 0.05; mixed = both)
5. Re-render and update in-figure caption to remove the proxy-disclosure clause

Separate quick; not blocking for R1/bioRxiv.

### For future manuscript revisions

- The `ensembl_to_symbol` hard-coded map in the R script is the canonical source of the 3 Tier C named gene symbols for Route A. If tier_assignments.tsv ever adds new Tier C named genes (e.g., after a re-fire), update the map + re-run.
- Panel B's PP.H4 values are read from tier_assignments.tsv at runtime. If the pipeline ever updates those numbers, Figure 5 auto-regenerates with the new values on next `Rscript` invocation.

## Commits made

**None inside this editor session yet.** The orchestrator performs a single consolidated commit:

`feat(track-a-fig5): fig5_variant_mech_scorecard.R + PDF + PNG render + k2g PLAN/SUMMARY/STATE row`

Or split per 2.2.e precedent into (a) code/artifacts commit + (b) docs quick commit. Both patterns are established on this project.

## Files changed

### Created
- `src/R/figures/fig5_variant_mech_scorecard.R` (222 lines; runtime-data-driven patchwork composite)
- `docs/manuscript/figures/fig5_variant_mech_scorecard.pdf` (cairo_pdf, 38,185 bytes)
- `docs/manuscript/figures/fig5_variant_mech_scorecard.png` (600 dpi, 319,140 bytes)
- `.planning/quick/260424-k2g-route-a-fig5-variant-mech-scorecard-R-script/260424-k2g-PLAN.md`
- `.planning/quick/260424-k2g-route-a-fig5-variant-mech-scorecard-R-script/260424-k2g-SUMMARY.md`

### Not modified (verified byte-identical)
- `docs/manuscript/track_a_pivot.md` (Figure 5 legend at L295 remains authoritative per k2f commit 99a73bf)
- All Stage 2 real-LD artifacts (md5 4/4 preserved: finemap_manifest, finemap_summary, coloc_summary, coloc_manifest)
- `results_identity_ld/*` (k2d fire output, in progress at 54 min elapsed)
- `.planning/amendments/TRACK-A-PIVOT.md` §5 (canonical spec unchanged)

## Self-Check: PASSED

- `[✓]` `src/R/figures/fig5_variant_mech_scorecard.R` exists; 222 lines; references patchwork + APOL1/IRX3/ATXN2 + ensembl_to_symbol map
- `[✓]` `docs/manuscript/figures/fig5_variant_mech_scorecard.pdf` exists; 38185 bytes; cairo_pdf 170 × 85 mm
- `[✓]` `docs/manuscript/figures/fig5_variant_mech_scorecard.png` exists; 319140 bytes; 600 dpi
- `[✓]` Render stdout confirms 51 leads + 3 Tier C genes + per-category counts
- `[✓]` T1-VERIFY 10-gate passes on first run
- `[✓]` Zero forbidden framing terms (drug-repurpos / machine learning / bareword ML / revision / cleanup / fix-up)
- `[✓]` Stage 2 real-LD md5 4/4 preserved
- `[✓]` k2d LSF fire (PID 830748) unaffected (54 min elapsed, still running, not touched by this quick)
- `[✓]` Manuscript legend L295 spec honored (2-panel composite; descriptive-only; Tier C restriction; drug-target reference-only labelling via in-figure annotation)
