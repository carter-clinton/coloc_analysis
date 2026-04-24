---
quick_id: 260424-k2f
phase: quick-260424-k2f
plan: 01
title: "Route A — Populate Figure 4 + Figure 5 legend entries (resolve 3-vs-5-figures mismatch; manuscript now aligns with TRACK-A-PIVOT.md §5 canonical 5-figure + S1–S6 roster)"
status: complete
completed: "2026-04-24T17:35:00-04:00"
requirements:
  - ROUTE-A-FIGURE-LEGEND-COMPLETE
  - ROUTE-A-SPEC-MANUSCRIPT-ALIGN
tags:
  - track-a
  - manuscript
  - figure-legends
  - spec-alignment
  - original-research
dependency_graph:
  requires:
    - .planning/amendments/TRACK-A-PIVOT.md §5 (canonical 5-figure + S1–S6 spec)
    - .planning/quick/260424-mqo-route-a-r2-figure-number-alignment-recon/260424-mqo-SUMMARY.md (re-asserted 5-figure claim)
    - .planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-SUMMARY.md (empirical Tier A+B=0 result shapes Figure 4/5 content)
  provides:
    - 5-figure + S1–S6 Figure legends block in `docs/manuscript/track_a_pivot.md`
    - Figure 4 legend anchored to k2e zero-gene result with demotion of identity-LD enrichment to Figure S5
    - Figure 5 legend anchored to k2e Tier C descriptors (APOL1, IRX3, ATXN2) as sparse-by-design annotation
  affects:
    - Route A Step 2.4 bioRxiv preprint package (complete Figure legends block; no missing entries)
    - Route A Step 2.3 figure-builders (Fig 4 / Fig 5 R-script specs now have legend text to align to when the scripts are written post-k2d)
    - Future pathway-recompute handoffs: none — k2e resolved L222, k2f aligns Figure legends to same zero-gene finding; Discussion + Results + Figure block all internally consistent on real-LD Tier A+B = 0
key_files:
  created:
    - .planning/quick/260424-k2f-route-a-populate-figure-4-and-5-legends-res/260424-k2f-PLAN.md
    - .planning/quick/260424-k2f-route-a-populate-figure-4-and-5-legends-res/260424-k2f-SUMMARY.md
  modified:
    - docs/manuscript/track_a_pivot.md (+4 lines; 2 new Figure legend paragraphs between Figure 3 and Figure S1–S6)
decisions:
  - "Resolution direction: populate the manuscript legend block to match the spec, NOT retract the mqo claim. The mqo claim ('5-figure + S1–S6 supplementary roster') was correct per `.planning/amendments/TRACK-A-PIVOT.md` §5. The manuscript was the artifact that needed updating — its legend block was incomplete at 3 figures + S1–S6. This quick fills the gap by transcribing spec content into legend prose, anchored to the k2e empirical null."
  - "Figure 4 panel content under real-LD: spec-level 'two-panel pathway-category distribution + fold-enrichment bar on real-LD-surviving gene set'. Under k2e empirical constraint (Tier A+B = 0), the main-text enrichment panel is not computable at threshold. Resolution: mark Figure 4 as 'withdrawn at threshold / demoted to Figure S5' in the legend. Figure S5 is already reserved by §5 for the identity-LD pathway enrichment (as contrast). Track B is flagged as the appropriate setting for a populated main-text Figure 4 once the genome-wide real-LD re-analysis lands."
  - "Figure 5 panel content under real-LD: spec-level 'regulatory/coding/mixed donut (A) + annotation-aggregated scorecard bar (B)'. Under k2e empirical constraint, the Tier A+B scorecard subset (panel B) is empty; the legend restricts panel B to Tier C descriptors (3 named genes APOL1/IRX3/ATXN2) and frames this as descriptive annotation — NOT predictive discovery — with drug-target status labelled as reference annotation from OMIM/ChEMBL/DGIdb (not claimed as discovery). The visible sparsity IS the figure's argument."
  - "Framing discipline preserved per CLAUDE.md user-profile rule: original research; zero 'revision' / 'cleanup' / 'fix-up' / 'machine learning' / bareword ML instances in the new legend text (verified via awk+grep). The term 'revise' appears only when quoting the §5 spec's own verb ('Figure 4 (revise)') as a method descriptor."
metrics:
  duration_minutes: ~10
  tasks_completed: 1
  paragraphs_inserted: 2 (Figure 4 + Figure 5 legends)
  paragraphs_no_op: Figure 1 + Figure 2 + Figure 3 + Figure S1–S6 (byte-identical)
  files_modified: 1
  files_created: 2 (PLAN + SUMMARY)
  total_figure_legends_before: 4 (1, 2, 3, S1–S6)
  total_figure_legends_after: 6 (1, 2, 3, 4, 5, S1–S6)
  spec_alignment: canonical TRACK-A-PIVOT.md §5 5-figure + S1–S6 roster now matched by manuscript
---

# Phase quick-260424-k2f Plan 01: Figure 4 + Figure 5 legend population Summary

## Objective

Resolved the 3-figures-vs-5-figures mismatch between `.planning/amendments/TRACK-A-PIVOT.md` §5 (canonical 5-figure + S1–S6 roster, reaffirmed by 260424-mqo commits 08944a8..7bb7d8c) and `docs/manuscript/track_a_pivot.md` L289–L297 (legend block had only 3 numbered figure entries + S1–S6 — Figures 4 and 5 missing). The resolution direction is to POPULATE the manuscript, not retract the spec or mqo claim: both spec and mqo are correct at 5 figures; the manuscript's legend block was simply incomplete.

Ground-truth content for the new Figure 4 and Figure 5 legends comes from two sources:
1. `.planning/amendments/TRACK-A-PIVOT.md` §5 (lines 202–210) for the canonical two-panel structures (Figure 4: pathway-category + fold-enrichment; Figure 5: variant-mechanism donut + annotation scorecard bar).
2. `260424-k2e-SUMMARY.md` (commit b7c9310) for the empirical real-LD constraint: Tier A+B = 0 genes; Tier C = 9 rows with only 3 named resolving genes (APOL1 PP.H4 = 0.013, IRX3 PP.H4 = 0.310, ATXN2 PP.H4 = 0.052; all below 0.5 threshold).

Both new legend entries explicitly anchor to the k2e zero-gene finding, so the manuscript is now internally consistent across Results §Pathway Enrichment Analysis (L190), Discussion §Reframing (L222), and Figure legends (L293 Figure 4 + L295 Figure 5) on the real-LD null.

## Per-edit outcome

| Action | Location | Outcome | Words added |
| --- | --- | --- | --- |
| Insert Figure 4 legend | between Figure 3 and Figure S1–S6 | "withdrawn at threshold / demoted to Figure S5" framing; anchors to k2e zero-gene finding; points to Track B as appropriate setting for populated main-text Figure 4 | ~140 words |
| Insert Figure 5 legend | between new Figure 4 and Figure S1–S6 | "partial, descriptive only" framing; panel A = regulatory/coding/mixed donut; panel B = Tier C scorecard (APOL1/IRX3/ATXN2); drug-target labelled as reference annotation; sparsity as the figure's argument | ~160 words |
| No change | Figure 1, Figure 2, Figure 3, Figure S1–S6 | byte-identical | 0 |

## Before / after diff (Figure legends section)

**Before** (L289–L297, 4 legend paragraphs):

> ## Figure legends
>
> **Figure 1.** Identity-LD vs real-LD comparison at admissible EUR autosomal regions. (A) Scatter ... (B) Regional association panels ...
>
> **Figure 2.** Credible-set yield under each LD condition. Two-bar comparison ... **4.25× fold-increase** ...
>
> **Figure 3.** Survival forest plot (NEW). For each previously-reported PP.H4 ≥ 0.8 signal ... colored: survived (green), lost (red), rescued (blue), both-null (gray) ...
>
> **Figure S1–S6.** Supplementary figures covering ...

**After** (L289–L299, 6 legend paragraphs — two new insertions in bold):

> ## Figure legends
>
> **Figure 1.** Identity-LD vs real-LD comparison ... (unchanged)
>
> **Figure 2.** Credible-set yield under each LD condition ... (unchanged)
>
> **Figure 3.** Survival forest plot (NEW) ... (unchanged)
>
> **Figure 4.** Pathway enrichment on the real-LD–surviving signal set — **withdrawn at threshold / demoted to Figure S5**. The canonical spec (`.planning/amendments/TRACK-A-PIVOT.md` §5) calls for a two-panel pathway-category distribution + fold-enrichment bar computed on the real-LD–surviving gene set, with the identity-LD parallel as Figure S5. The real-LD Tier A + Tier B gene set at the manuscript's confidence threshold (GWAS PP.H4 ≥ 0.8 AND QTL PP.H4 ≥ 0.5) contains zero genes (0 Tier A + 0 Tier B; 9 Tier C with only 3 named resolving genes — APOL1, IRX3, ATXN2 — all at PP.H4 < 0.5), making the main-text enrichment panel non-computable at threshold. See Results §Pathway Enrichment Analysis. The identity-LD pathway enrichment (the original pre-pivot Figure 4) is retained as Figure S5 for contrast; the genome-wide real-LD re-analysis on upgraded sumstats with an All-of-Us–derived AFR LD panel (Track B, in preparation) is the appropriate setting in which to produce a populated main-text Figure 4.
>
> **Figure 5.** Variant mechanism + annotation-aggregated candidate-gene scorecard at real-LD–surviving pleiotropic loci — **partial, descriptive only**. (A) Regulatory / coding / mixed variant-mechanism donut at real-LD–surviving lead variants (CADD / PolyPhen-2 / SIFT / GTEx eQTL annotation aggregation; descriptive proportions only, not a predictive model). (B) Annotation-aggregated candidate-gene scorecard bar at Table 2 genes. Per the k2e pathway re-compute finding, the real-LD Tier A + Tier B scorecard subset is empty at the manuscript's confidence threshold; panel B therefore reports only Tier C descriptors (3 named resolving genes: APOL1 on cultured fibroblasts PP.H4 = 0.013; IRX3 on pancreas PP.H4 = 0.310; ATXN2 on adrenal gland PP.H4 = 0.052) as descriptive annotation, explicitly NOT as predictive discovery. Existing annotated drug-target status at these loci (OMIM / ChEMBL / DGIdb sources) is labelled in-panel as reference annotation inherited from public pharmacology databases; this study does NOT claim drug-target discovery or indication expansion. Both panels are intentionally sparse under real-LD — the visible emptiness at the Tier A+B level is the figure's argument, consistent with the §Discussion "primarily an LD-inflation artifact" framing.
>
> **Figure S1–S6.** Supplementary figures covering ... (unchanged)

## Guardrail verification results

| Check | Expected | Observed | Pass |
| --- | --- | --- | --- |
| Figure 1 legend paragraph count | 1 | 1 | ✅ |
| Figure 2 legend paragraph count | 1 | 1 | ✅ |
| Figure 3 legend paragraph count | 1 | 1 | ✅ |
| Figure 4 legend paragraph count (NEW) | 1 | 1 | ✅ |
| Figure 5 legend paragraph count (NEW) | 1 | 1 | ✅ |
| Figure S1–S6 legend paragraph count | 1 | 1 | ✅ |
| Total `^\*\*Figure [0-9S]` count in file | 6 | 6 | ✅ |
| k2e zero-gene anchor in new legends | ≥ 1 | 2 (one each in Figure 4 + Figure 5) | ✅ |
| Figure 4 legend mentions pathway + S5 | ≥ 1 | 1 | ✅ |
| Figure 5 legend mentions variant mechanism + scorecard | ≥ 1 | 1 | ✅ |
| Forbidden framing in legend block (L289–L305) | 0 | 0 | ✅ |
| `'3-figure'` residual in manuscript | 0 | 0 | ✅ |
| Stage 2 real-LD artifacts md5 4/4 | all OK | 4/4 OK | ✅ |
| k2d LSF fire state unaffected | PID 830748 running | PID 830748 running (37:41 → 40+ min elapsed) | ✅ |

## Deviations from Plan

**None.** The planned insertion of 2 new legend paragraphs landed cleanly at the intended line positions with no collisions against the Figure 1/2/3/S1–S6 content. All 14 guardrail checks pass on first run.

## Authentication gates

None. Pure manuscript-prose edit.

## Handoff notes

### For Route A Step 2.3 Fig 4 + Fig 5 R-script builders (future /gsd-quick)

The Figure 4 and Figure 5 legends now exist as specifications that any downstream R-script implementation must honor:

- **Fig 4 R script (not yet written)**: should render a placeholder panel or a "Figure non-computable at threshold; see Figure S5" redirect notice. The S5 identity-LD enrichment plot is a separate downstream task once gprofiler identity-LD runs are available (k2d fire produces identity-LD SuSiE outputs; identity-LD pathway enrichment would need its own invocation on the identity-LD surviving gene set, a different gene list from the real-LD one audited in k2e).
- **Fig 5 R script (not yet written)**: should render panel A from CADD/PolyPhen/SIFT/GTEx annotations on real-LD lead variants (n = 51 non-empty credible sets, one lead per CS) and panel B as a 3-bar scorecard at APOL1/IRX3/ATXN2 Tier C genes only, with drug-target annotation labelled as reference-only.

### For Route A Step 2.4 (bioRxiv preprint package)

- Figure legends section is now complete: 5 numbered figures + S1–S6 supplementary = 6 legend paragraphs.
- No remaining placeholders at the figure-level other than the Figure 4/5 R-script outputs themselves (which are separate build tasks, not legend-prose gaps).
- Manuscript is internally consistent on the real-LD null (L190 Results + L222 Discussion + L293 Figure 4 + L295 Figure 5 all cite zero Tier A+B).

### For Nyquist-style audits (general)

- Spec-to-manuscript gap detection: The audit path that found this gap was (a) read `.planning/amendments/TRACK-A-PIVOT.md` §5 canonical roster, (b) count `^\*\*Figure ` entries in `docs/manuscript/track_a_pivot.md`, (c) compare. The mismatch became visible at `4 legend paragraphs` (1, 2, 3, S1–S6) vs `5 numbered + 1 supplementary = 6 expected` entries. Any future spec-to-manuscript alignment audits can use this pattern.

## Commits made

**None inside this editor session yet.** The orchestrator performs a single consolidated commit: `docs(quick-260424-k2f): Route A populate Figure 4 + Figure 5 legends (resolve 3-vs-5-figures mismatch; align with TRACK-A-PIVOT.md §5)`.

Files to commit:
- `docs/manuscript/track_a_pivot.md` (+4 lines)
- `.planning/quick/260424-k2f-route-a-populate-figure-4-and-5-legends-res/260424-k2f-PLAN.md`
- `.planning/quick/260424-k2f-route-a-populate-figure-4-and-5-legends-res/260424-k2f-SUMMARY.md`
- `.planning/STATE.md` (row append)

## Files changed

### Modified
- `docs/manuscript/track_a_pivot.md` — 2 new Figure legend paragraphs inserted between Figure 3 and Figure S1–S6 (net +4 lines with blank-line separators).
- `.planning/STATE.md` — Quick Tasks Completed table row append.

### Created
- `.planning/quick/260424-k2f-route-a-populate-figure-4-and-5-legends-res/260424-k2f-PLAN.md`
- `.planning/quick/260424-k2f-route-a-populate-figure-4-and-5-legends-res/260424-k2f-SUMMARY.md`

### Not modified (verified byte-identical)
- Figure 1 / Figure 2 / Figure 3 / Figure S1–S6 legend paragraphs (L291, L293, L295, L299 in pre-edit numbering)
- All Stage 2 real-LD artifacts (md5 4/4 preserved)
- `.planning/amendments/TRACK-A-PIVOT.md` §5 (canonical spec unchanged)
- `.planning/quick/260424-mqo-.../` (the claim stands as correct)
- `.planning/quick/260424-k2e-.../` (the empirical result stands as correct)

## Self-Check: PASSED

- `[✓]` 5 numbered Figure legend paragraphs (Figure 1/2/3/4/5) + 1 Figure S1–S6 paragraph = 6 total (was 4)
- `[✓]` Figure 4 legend anchored to k2e zero-gene finding + Track B forward-pointer + Figure S5 demotion
- `[✓]` Figure 5 legend anchored to k2e Tier C 3-gene descriptors + sparse-by-design framing + drug-target as reference annotation only
- `[✓]` No forbidden framing terms in new prose (revision / cleanup / fix-up / machine learning / bare ML)
- `[✓]` Stage 2 real-LD artifacts byte-identical (md5 4/4)
- `[✓]` k2d LSF fire (PID 830748) unaffected by manuscript-prose edit
- `[✓]` mqo claim now accurate against manuscript (5-figure + S1–S6 roster present)
- `[✓]` Manuscript internally consistent: L190 Results + L222 Discussion + L293 Figure 4 + L295 Figure 5 all cite zero Tier A+B under real-LD
