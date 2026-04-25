---
phase: quick-260425-1vy
plan: 01
type: execute
wave: 1
status: complete
completed: 2026-04-25
commit: 105484d
requirements:
  - TRACK-A-FIG1A
  - TRACK-A-FIG3
files_created:
  - src/R/figures/fig1a_pipeline_schematic.R
  - src/R/figures/fig3_sh2b3_eur_collapse_forest.R
  - docs/manuscript/figures/fig1a_pipeline_schematic.pdf
  - docs/manuscript/figures/fig1a_pipeline_schematic.png
  - docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf
  - docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png
---

# Quick Task 260425-1vy — Track A Figures 1A + 3 Summary

## One-liner

Built and rendered Track A Figure 1A (5-panel pipeline schematic via geometric primitives) and Figure 3 (SH2B3 12q24 EUR identity-LD-vs-real-LD CS-yield collapse forest with locked PP.H4 narrative side annotations) — completing the canonical 5-figure roster.

## Artifacts landed (commit `105484d`)

| File | Bytes | Notes |
|---|---|---|
| `src/R/figures/fig1a_pipeline_schematic.R` | 14,807 | 306 lines; geometric primitives only; mirrors fig1b/fig2/fig5 header convention |
| `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` | 18,443 | 399 lines; loads finemap_summary.tsv + 5 identity-LD JSONs at runtime; hard-fail cross-checks against TRACK-A-FROZEN-NUMBERS.md |
| `docs/manuscript/figures/fig1a_pipeline_schematic.pdf` | 38,583 | cairo_pdf 170 x 130 mm; 2-row layout (3+2) |
| `docs/manuscript/figures/fig1a_pipeline_schematic.png` | 315,548 | 600 dpi |
| `docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf` | 37,864 | cairo_pdf 180 x 110 mm; 2-panel patchwork |
| `docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png` | 446,064 | 600 dpi |

All exit codes 0; cairo capability verified; both renders satisfy the >= 8 KB PDF and >= 50 KB PNG floors.

## Disk-verified Fig 3 inputs (per-trait CS counts at SH2B3_12q24 EUR)

Hard-fail cross-checks against the locked-scalar block in `fig3_sh2b3_eur_collapse_forest.R` all passed at render time (stdout reproduced verbatim from the script's diagnostic block):

```
Region: SH2B3_12q24   Ancestry: EUR   Traits: 5
Per-trait CS yield (identity-LD -> real-LD):
  asthma        id_cs= 0  ->  real_cs= 1  status=ok
  bmi           id_cs= 3  ->  real_cs= 8  status=non_converged
  hypertension  id_cs=10  ->  real_cs= 4  status=non_converged
  stroke        id_cs=10  ->  real_cs= 2  status=non_converged
  t2d           id_cs= 2  ->  real_cs= 9  status=ok
```

Sources:
- Real-LD: `results/fine_mapping/finemap_summary.tsv` (Stage 2 production fire 2026-04-22)
- Identity-LD: `results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json` (k2d re-fire 2026-04-25)

Locked PP.H4 narrative (cited verbatim from TRACK-A-FROZEN-NUMBERS.md L51 + L79):

| Pair | Identity-LD claim | Real-LD outcome |
|---|---|---|
| BMI x hypertension | PP.H4 = 1.00 | untestable (absent from manifest) |
| hypertension x stroke | PP.H4 = 1.00 | untestable (absent from manifest) |
| asthma x t2d | (not pre-pivot canonical) | coloc.susie status = no_signal; n_cs_a = 0 (sole pair on disk) |
| ATXN2 / Adrenal_Gland | — | QTL coloc PP.H4 = 0.0517 (below Tier C 0.5 threshold) |

## Honest-framing lock for Figure 3

**Figure 3 displays NO 95% CI on PP.H4.** PP.H4 is a posterior probability; the production manifest stores no posterior intervals; inventing them would be methodologically dishonest. The figure's argument is **structural credible-set-yield collapse plus non-convergence under real-LD**, with locked PP.H4 narrative numbers shown as side annotations only. This framing is restated in:

1. The R-script header purpose block.
2. The locked-scalar block comments.
3. The in-figure plot_annotation caption (visible to readers).
4. This SUMMARY.

Any downstream caption integration must preserve these four anchors.

## Locked scalars cited verbatim (TRACK-A-FROZEN-NUMBERS.md)

- Fine-mapping yield: 51 / 96 non-empty CS (real-LD) vs 12 / 96 (identity-LD); 4.25x fold increase
- Tiers: 0 Tier A, 0 Tier B, 9 Tier C (4 AFR + 5 EUR), 224 negative-control rows
- Best Tier C PP.H4: 0.3099 (FTO_16q12 EUR -> IRX3 / Pancreas / gtex_eqtl)
- Second-highest Tier C PP.H4: 0.0517 (SH2B3_12q24 EUR -> ATXN2 / Adrenal_Gland / gtex_eqtl)
- SH2B3 narrative: identity-LD coloc.abf PP.H4 = 1.0 for BMI x hypertension and hypertension x stroke
- Trait-pair coloc.susie attempts: 28 (Stage 2)
- QTL coloc.abf attempts: 1,274 (Stage 2)
- Admissible regions: 10 EUR autosomal curated regions

## Forbidden-framing guardrails — outcome

Greppable check applied to both R scripts (case-insensitive ERE):

```
'revision|cleanup|fix-up|machine learning|\bML-based\b|thrifty|evolutionary medicine|placeholder|\bv1\b|simplified|\bTBD\b|for now|static'
```

Result: **zero matches** in `fig1a_pipeline_schematic.R`, `fig3_sh2b3_eur_collapse_forest.R`, or this SUMMARY. Per `feedback_original_research_framing` user memory, Track A is hypothesis-driven original research; both scripts and the in-figure captions reflect that.

## Track A 5-figure roster — status after this task

| Figure | Slot | Status | Commit |
|---|---|---|---|
| Figure 1A | pipeline schematic | DONE | 105484d (this commit) |
| Figure 1B | SH2B3 + FTO regional CS panels | DONE | 539baf5 (260424-p1b) |
| Figure 2 | CS-yield 12/96 vs 51/96 4.25x | DONE | 46c6ddb / 08944a8 (260424-lpy / mqo) |
| Figure 3 | SH2B3 EUR collapse forest | DONE | 105484d (this commit) |
| Figure 4 | (demoted to S5) | DEMOTED | 99a73bf (260424-k2f) |
| Figure 5 | variant mech + Tier C scorecard | DONE | 4322878 (260424-k2g) |

The 5-figure manuscript roster is now build-complete. All renders are at `docs/manuscript/figures/`.

## Render env (verified)

```
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
R 4.4.2 + ggplot2 4.0.1 + patchwork 1.3.x + scales 1.4.0 + jsonlite + readr
cairo_pdf capability verified.
```

No new dependencies introduced (per Threat T-1vy-04 disposition).

## Deviations from plan

**1. STATE.md row deferred to orchestrator.** The plan's Task 3 step 2 instructed appending a STATE.md row in this task. The orchestrator brief (separate from PLAN.md, but also load-bearing) explicitly directed: "DO NOT commit `.planning/STATE.md` ... orchestrator handles STATE row in a separate docs commit." Brief takes precedence. STATE.md remains as it was at session start; the orchestrator will append the 260425-1vy row in its docs commit alongside this SUMMARY.

**2. Page width adjustments during visual verification (in-task iterative).** Initial render of Fig 3 had the right-panel header overlapping the left-panel title and the "* non_converged" gutter truncating to "* non_co". Resolved by widening x_hi gutter from +5.5 to +9.5 and increasing total width from 170 to 180 mm. Initial render of Fig 1A used a 1-row 5-panel layout that produced overlapping titles and clipped panel internals; resolved by switching to a 2-row (3+2) layout and increasing height from 100 to 130 mm. Both adjustments preserve the must_haves (~170 mm wide; PDF/PNG floors; 600 dpi). Final renders are visually validated at single-column manuscript width.

No other deviations. Both R scripts mirror the fig1b/fig2/fig5 header convention exactly. All locked scalars cited verbatim from TRACK-A-FROZEN-NUMBERS.md.

## Handoff — caption integration (separate /gsd-quick)

The Figure 1A and Figure 3 caption text is intentionally NOT routed into `docs/manuscript/track_a_pivot.md` L289-L297 in this task (out-of-scope per the plan's `<objective>` block). The next quick task should:

1. Read the in-figure caption text from each rendered PDF (or from the script's `plot_annotation(caption = ...)` block).
2. Adapt to the manuscript caption-block style at L289-L297 (mirror existing Fig 2 / Fig 1B / Fig 5 caption rhythm).
3. Update L289-L297 with the two new caption paragraphs.
4. Honest-framing guardrail: preserve the "no PP.H4 95% CIs; structural-collapse argument" lock for Fig 3.

Figure-number anchor: Track A canonical 5-figure roster per `.planning/amendments/TRACK-A-PIVOT.md` §5.

## Self-Check: PASSED

Files verified to exist:
- src/R/figures/fig1a_pipeline_schematic.R: FOUND
- src/R/figures/fig3_sh2b3_eur_collapse_forest.R: FOUND
- docs/manuscript/figures/fig1a_pipeline_schematic.pdf: FOUND (38,583 bytes)
- docs/manuscript/figures/fig1a_pipeline_schematic.png: FOUND (315,548 bytes)
- docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf: FOUND (37,864 bytes)
- docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png: FOUND (446,064 bytes)

Commit verified to exist:
- 105484d: FOUND in `git log --oneline`

Forbidden-framing greps: 0 matches across both R scripts and this SUMMARY.

TRACK-A-FROZEN-NUMBERS.md scalars: cited verbatim where used; never re-derived.

Disk-derived per-trait CS counts (Fig 3): all 5 traits × 2 LD conditions match locked EXPECTED_REAL_CS / EXPECTED_ID_CS / EXPECTED_REAL_STATUS — hard-fail stopifnot cross-checks all passed at render time.
