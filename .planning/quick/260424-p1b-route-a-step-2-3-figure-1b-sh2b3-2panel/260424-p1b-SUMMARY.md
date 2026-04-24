---
quick_id: 260424-p1b
phase: quick-260424-p1b
title: "Route A Step 2.3 — Figure 1B: SH2B3 flagship + Tier-C rescued locus, ggplot-custom CS-membership panels (real-LD only)"
date: 2026-04-24
status: complete
tags:
  - track-a
  - figures
  - manuscript
  - original-research
  - real-ld-only
---

## Outcome

Built Figure 1B as a 2-panel vertical composite (ggplot + gggenes + patchwork)
under `docs/manuscript/figures/fig1b_locus_panels.{pdf,png}` rendered via
`la_multitrait_r` conda env, committed atomically alongside the manuscript
caption patch at `docs/manuscript/track_a_pivot.md:291`. Scope = Option D
("install packages + build with real-LD only") per the 2026-04-24 Terminal A
routing decision: the identity-vs-real per-SNP overlay is explicitly deferred
to a follow-on `/gsd-quick` now that `k2d` has landed its identity-LD JSONs
(see §Handoff).

Zero "revision" / "cleanup" / "fix" language in any committed artifact;
framing remains original research (identity-vs-real LD audit at anchor loci).

## Panels (locked)

**Panel 1 — SH2B3 12q24 flagship** (`asthma.EUR.SH2B3_12q24`):

- Region `chr12:111,400,000–112,000,000` (600 kb; `start`/`end` from JSON)
- 1 CS, 140 variants in CS, 4,454 regional association rows plotted
- Genes in window (4): *CUX2*, *FAM109A*, *SH2B3*, *ATXN2*
- Annotation surfaces the locked scalar: Stage 1 identity-LD `PP.H4 = 1.00`
  at canonical leads rs3184504 / rs10774625 for BMI–HTN + HTN–stroke →
  Stage 2 real-LD `n_cs_a = 0` at those trait pairs (collapse)

**Panel 2 — FTO 16q12 rescued Tier C** (`bmi.EUR.FTO_16q12`):

- Region `chr16:53,800,000–54,400,000` (600 kb)
- 10 CS (7 high-PIP singletons + 1 CS of 5 + 2 CS of 2), 701 regional rows
- Genes in window (2): *FTO*, *IRX3*
- 49 variants y-capped at `-log10(P) = 30` (all at the 5′ FTO BMI signal
  near rs1421085 / rs1558902 / rs17817449; marked with filled triangles)

**Rescued-locus selection provenance** (emitted at runtime, full log in
`.planning/quick/260424-p1b-.../render_provenance.log` on re-run):

- Candidate pool: 9 Tier C signals from `results/qtl_coloc/tier_assignments.tsv`
- Criterion: highest `best_qtl_pph4` × (converged=TRUE) × (L_saturated=FALSE)
  × (n_cs > 0); tie-broken by smallest `min_cs_size` → highest `max_top_pip`
- Winner: **FTO_16q12 × bmi.EUR** (best_qtl_pph4 = 0.3099 for *IRX3* /
  Pancreas, GTEx eQTL). BMI chosen over asthma / t2d at same region because
  BMI is the canonical FTO phenotype and the 10-CS structure has the
  cleanest singleton-PIP profile.

## Environment

Installed into `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/`
(additive; reversible; no Snakemake env-file committed):

- CRAN install: `patchwork` 1.x, `ggrepel` 0.9.x (succeeded)
- conda-forge install (CRAN commonmark build failed on host):
  `r-commonmark` 2.0.0, `r-litedown` 0.9, `r-markdown` 2.0,
  `r-gridtext` 0.1.6, `r-ggfittext` 0.10.3, `r-gggenes` 0.6.0
- Side-effects: `ca-certificates` → 2026.4.22, `openssl` → 3.6.2

Post-install verification (all TRUE): `gggenes`, `patchwork`, `ggrepel`,
`ggfittext`, `gridtext`, `markdown`, `commonmark`, `jsonlite`.

A dedicated `envs/r_figures.yml` is still the correct long-term move (flagged
as a low-priority handoff in [260424-lpy-SUMMARY.md](../260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md)) but is not required for this figure to build reproducibly.

## Verification

- `Rscript src/R/figures/fig1b_locus_panels.R` exits 0.
- `docs/manuscript/figures/fig1b_locus_panels.pdf` = 221 KB (cairo_pdf, 170×200 mm).
- `docs/manuscript/figures/fig1b_locus_panels.png` = 1.5 MB (600 dpi, same dims).
- `grep -n "TCF7L2\|KCNJ11\|ABCC8" docs/manuscript/track_a_pivot.md:291` →
  the L291 Figure 1B caption no longer lists *TCF7L2* / *KCNJ11* / *ABCC8*
  as secondary-anchor candidates (the two surviving mentions at L166 / L170
  are unrelated biological-context references in the Introduction / Results
  bulk and are intentionally preserved).
- `grep "flagship\|rescued Tier C"` in L291 → present (new 2-panel language).
- Visual render inspected: 2 stacked assoc+gene panels, CS colouring
  consistent, capped-variant triangles visible, subtitles fit within plot
  width, caption fits on 3 lines.

## Deliverables

| Artifact | Path |
|---|---|
| R script | [`src/R/figures/fig1b_locus_panels.R`](../../../src/R/figures/fig1b_locus_panels.R) |
| PDF | [`docs/manuscript/figures/fig1b_locus_panels.pdf`](../../../docs/manuscript/figures/fig1b_locus_panels.pdf) |
| PNG | [`docs/manuscript/figures/fig1b_locus_panels.png`](../../../docs/manuscript/figures/fig1b_locus_panels.png) |
| Caption patch | [`docs/manuscript/track_a_pivot.md:291`](../../../docs/manuscript/track_a_pivot.md) |
| Quick PLAN | [`260424-p1b-PLAN.md`](./260424-p1b-PLAN.md) |

## Handoff

1. **k2d identity-LD JSONs have landed.** `results_identity_ld/fine_mapping/susie/*.json`
   is now populated (52 JSONs at time of check; `bjobs` shows no unfinished
   jobs). The PLAN.md's deferred overlay pass is now unblocked. A follow-on
   `/gsd-quick` should:

   - Re-open `src/R/figures/fig1b_locus_panels.R`; locate the `TODO-K2D`
     comment in `build_locus()` (single insertion point).
   - Add a second `geom_point` layer on each assoc sub-panel plotting the
     identity-LD z-stats (or -log10(P) from the same harmonized sumstats
     joined against the identity-LD `pip` vector from
     `results_identity_ld/fine_mapping/susie/{trait}.{ancestry}.{region}.json`)
     with `shape = 4` (cross) so identity-LD points sit under the real-LD
     circles visually. Update the caption in `track_a_pivot.md:291` to drop
     the "Identity-LD per-SNP overlay is deferred" clause and replace with
     the overlay description.
   - Confirm the SH2B3 narrative on the figure: the identity-LD trace
     should show a high-PIP cluster at the canonical leads rs3184504 /
     rs10774625 (`chr12:111884608` / `chr12:111885573`) that disappears
     under real-LD. If the identity-LD SH2B3 asthma × EUR fit *also*
     produced a wide low-PIP CS (possible given the 147-variant overlap
     fraction at 0.038), state that explicitly in the caption.

2. **Figure 1A (identity-vs-real PP.H4 scatter).** Separate `/gsd-quick`
   now unblocked for the same reason: per-fit identity-LD PP.H4 values are
   extractable from `results_identity_ld/multitrait/coloc_susie/*.json`.

3. **Figure 3 (survival forest plot).** Also unblocked by k2d.

4. **Figure caption numbering.** Confirmed consistent with the post-mqo /
   post-k2f manuscript layout: Figure 1 Panel A + Panel B in one caption
   paragraph; Figure 2 / 3 / 4 / 5 unchanged. No L293–L297 edits made.

5. **Aesthetic follow-on.** Figure 1B uses `theme_classic(base_size = 8)`
   to match the fig2_cs_yield.R convention, but at 170×200 mm the text is
   sized for full-width two-column display, not single-column. When we
   finalize the manuscript layout, re-render at 85 mm × N mm (single-column)
   or confirm double-column placement. Decide at bioRxiv assembly (Step 2.4).

6. **Gene-track source.** Currently using MAGMA `NCBI37.3.gene.loc` which
   lists RefSeq-annotated genes only (one row per gene, no isoforms). A
   follow-on pass can substitute GENCODE basic v19 (GRCh37) for full-isoform
   gene models if manuscript reviewers request isoform-level detail. Not
   required for bioRxiv submission.

## Framing guardrail

All committed prose uses the original-research framing per
[feedback_original_research_framing.md](../../../../home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/feedback_original_research_framing.md). Zero instances of "revision" / "cleanup" / "fix" / "machine learning" / "ML" in the caption patch, R script, or PLAN / SUMMARY. The phrase "pending the pre-registered SH2B3 identity-LD re-fire" reflects the OSF amendment language, not a rework framing.
