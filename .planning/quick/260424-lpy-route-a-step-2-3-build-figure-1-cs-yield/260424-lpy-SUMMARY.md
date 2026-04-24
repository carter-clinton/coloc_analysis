---
quick_id: 260424-lpy
title: "Route A Step 2.3 — Figure 1 (CS yield) build"
date: 2026-04-24
status: complete
route: A
step: "2.3"
parent_plan: /home/ckclinto/.claude/plans/snappy-humming-pine.md
authoritative_numbers: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
outputs:
  - src/R/figures/fig_cs_yield.R
  - docs/manuscript/figures/fig_cs_yield.pdf
  - docs/manuscript/figures/fig_cs_yield.png
---

# Route A Step 2.3 — Figure 1 (CS yield) build

## Objective

This quick task built the first of three manuscript figures for the Track A pivot preprint (`docs/manuscript/track_a_pivot.md`): a single-panel, two-bar comparison of non-empty SuSiE-RSS credible sets under identity-LD fallback (12 / 96 = 12.5%) vs real 1000G Phase 3 EUR LD (51 / 96 = 53.1%), annotated with the 4.25× fold-increase that is the headline methodological finding of the original-research Track A audit. The figure directly serves `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 ("Fig 1 = CS yield") and `.planning/amendments/TRACK-A-PIVOT.md` §5 (Figure 2 spec in the section-by-section pivot plan). The build produces a portable, reproducible R script at `src/R/figures/fig_cs_yield.R` (210 lines) plus two rendered artifacts (`fig_cs_yield.pdf` vector + `fig_cs_yield.png` 600 dpi raster) at 85 mm × 70 mm for a Genome Medicine single-column layout.

## Data-source audit

Available on disk and consumed live:

- `results/fine_mapping/finemap_summary.tsv` — 97 lines total (1 header + 96 admissible fits). 17 columns, tab-delimited. Script reads this file, asserts `nrow(df) == 96`, derives `sum(credible_sets > 0)` = 51 at runtime, and cross-checks against the locked scalar.

NOT available on disk (known gap):

- Per-fit identity-LD SuSiE output (matched 96-fit JSONs under identity-LD). The 12 / 96 identity-LD baseline is a **scalar-only** number carried forward from the pre-Stage-2 session continuity narrative and frozen in `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` as the canonical source. No per-region × per-trait paired dataset exists to build the manuscript's Figure 2 paired beeswarm (L293 caption in `docs/manuscript/track_a_pivot.md`).

Consequence: this quick task delivers the two-bar scalar comparison (12 vs 51 out of 96) as a defensible single-panel figure. The per-fit paired-beeswarm distribution plot is explicitly **deferred** pending the identity-LD re-run session flagged in `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.2.d pending-item #4.

## Figure-number convention decision (deferred)

The plan documents acknowledge a numbering drift between two authoritative references:

- `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 labels the CS-yield figure as **"Fig 1"**.
- `docs/manuscript/track_a_pivot.md` L291–L297 currently labels **Fig 1** = identity-LD vs real-LD scatter + LocusZoom panels, **Fig 2** = paired beeswarm of CS sizes (this CS-yield visual by the manuscript's current caption plan), **Fig 3** = survival forest plot.

R1 chose the neutral filename stem `fig_cs_yield` (no integer) to avoid prematurely committing to either numbering scheme. Integer-rename is an R2 handoff task paired with a manuscript caption-alignment pass — the rename + caption edits + manuscript cross-references must land in one atomic commit.

## R script — listing excerpt

Head (first 20 lines) of `src/R/figures/fig_cs_yield.R`:

```r
# fig_cs_yield.R — Track A Figure 1 (identity-LD vs real-LD credible-set yield)
#
# Purpose: Build the headline-yield figure for the Track A pivot manuscript —
#   a two-bar comparison of non-empty SuSiE-RSS credible-set counts under
#   identity-LD fallback (12 / 96) vs real 1000G Phase 3 EUR LD (51 / 96).
#   The 4.25x fold increase is the single most load-bearing methodological
#   claim of the Track A "identity-LD inflation" audit. This figure must make
#   that delta unmissable at a single-column width.
#
# Data source: results/fine_mapping/finemap_summary.tsv
#   (Stage 2 production fire, 2026-04-22 — 97 lines = 1 header + 96 admissible fits).
#   The 51 non-empty credible-set count is derived at runtime from disk and
#   cross-checked against the locked scalar to catch any silent drift.
#
# Locked scalars: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
#   (canonical source of the 12 identity-LD baseline and 51 real-LD / 96 total /
#    4.25x fold-change; if Stage 2 numbers ever shift, update that file FIRST
#    then propagate here in the same commit.)
#
# Upstream plans:
```

Tail (last 10 lines) of `src/R/figures/fig_cs_yield.R`:

```r

ggsave(OUT_PDF, plot, width = 85, height = 70, units = "mm", device = cairo_pdf)
ggsave(OUT_PNG, plot, width = 85, height = 70, units = "mm", dpi = 600)

# --- Post-save verification stdout (asserted by Task 2 verify block) ---------
message(sprintf("fold-change: %.2fx (51/12 baseline)", n_real_nonempty / N_IDENTITY_LD_NONEMPTY))
message(sprintf("counts: identity-LD=12, real-LD=%d, empty=%d, total=%d",
                n_real_nonempty, n_real_empty, N_TOTAL_FITS))
message(sprintf("wrote %s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))
message(sprintf("wrote %s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))
```

## Render output verification

Render invocation (from project root, captured to `/tmp/lpy_fig_cs_yield_render.log`):

```
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig_cs_yield.R
```

Exit code: **0** (clean).

Output files on disk:

```
-rw-r--r--. 1 ckclinto clintonlab  23540 Apr 24 15:48 docs/manuscript/figures/fig_cs_yield.pdf
-rw-r--r--. 1 ckclinto clintonlab 219016 Apr 24 15:48 docs/manuscript/figures/fig_cs_yield.png
```

Size gates: PDF 23,540 bytes (gate ≥ 1,024); PNG 219,016 bytes (gate ≥ 10,240). Both pass.

Key stdout lines captured (the literal substrings all land in the render log — asserted by Task 2 verify block):

```
Total fits parsed: 96 (expected 96)
Non-empty real-LD fits: 51 (expected 51)
Empty real-LD fits: 45 (expected 45)
Identity-LD fallback baseline: 12 (locked from TRACK-A-FROZEN-NUMBERS.md)
Fold change: 4.25x
fold-change: 4.25x (51/12 baseline)
counts: identity-LD=12, real-LD=51, empty=45, total=96
wrote docs/manuscript/figures/fig_cs_yield.pdf (23540 bytes)
wrote docs/manuscript/figures/fig_cs_yield.png (219016 bytes)
```

Guardrail literal-substring grep results (all PASS):

| Token   | Present in render log | Interpretation                               |
| ------- | --------------------- | -------------------------------------------- |
| `4.25`  | yes                   | Fold-change emitted                          |
| `12`    | yes                   | Identity-LD baseline emitted                 |
| `51`    | yes                   | Real-LD non-empty count emitted              |
| `45`    | yes                   | Empty-fit count emitted (96 − 51)            |
| `96`    | yes                   | Admissible-fit denominator emitted           |

Diagnostic per-ancestry × per-trait CS split (printed to stdout during render — preserves future-debug traceability):

| ancestry | trait        | cs_FALSE | cs_TRUE |
| -------- | ------------ | -------- | ------- |
| AFR      | asthma       | 8        | 4       |
| AFR      | stroke       | 5        | 7       |
| AFR      | t2d          | 9        | 3       |
| EUR      | asthma       | 7        | 5       |
| EUR      | bmi          | 1        | 11      |
| EUR      | hypertension | 2        | 10      |
| EUR      | stroke       | 5        | 7       |
| EUR      | t2d          | 8        | 4       |

Column totals: cs_FALSE = 45, cs_TRUE = 51. Denominators check: 45 + 51 = 96.

## Environment & reproducibility

Render env (pre-provisioned, not installed in this session): `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript` — R 4.4.2 + ggplot2 4.0.1 + tidyverse 2.0.0 + scales 1.4.0 + cairo capability TRUE. All five required packages (readr, dplyr, tidyr, ggplot2, scales) load under `suppressPackageStartupMessages`. No other library calls in the script.

Packages absent from `la_multitrait_r` that a less-careful build might have reached for, and how the script sidesteps them:

| Package   | Typical use                   | How this script avoids it                           |
| --------- | ----------------------------- | --------------------------------------------------- |
| `here`    | project-root path resolution  | Script expects to run from project root; uses base `file.path()` only. |
| `showtext`| custom font registration      | `cairo_pdf` device handles required glyphs; no custom fonts needed.    |
| `cowplot` | multi-panel composition       | Figure is single-panel; `theme_classic()` sufficient.                  |
| `ggpubr`  | publication-style helpers     | Explicit `theme()` call matches figure-spec line-by-line.              |

`envs/r_coloc.yml` (if present elsewhere in the repo) is the coloc-working env, not a figure-build env. A dedicated `envs/r_figures.yml` to pin the figure-build env for long-term reproducibility is a future provisioning decision (handoff item (c) below).

## Commits created

| Commit | Author | Message |
| ------ | ------ | ------- |
| _(none)_ | _(none)_ | Executor created zero commits in this quick task. |

This is by design: the executor authors the artifacts only; the orchestrator owns the Step 8 commit for quick-260424-lpy. Files destined for the orchestrator's commit:

- `src/R/figures/fig_cs_yield.R` (210 lines, new file)
- `docs/manuscript/figures/fig_cs_yield.pdf` (23,540 bytes, new file)
- `docs/manuscript/figures/fig_cs_yield.png` (219,016 bytes, new file)
- `.planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md` (this document, new file)

The executor also created two empty directories (`src/R/figures/` and `docs/manuscript/figures/`) via `mkdir -p`; git will commit them implicitly via the files landing inside.

## Handoff flags

Five explicit handoffs for subsequent quick-task sessions:

**(a) Identity-LD re-run session** — required to unlock the manuscript's Figure 2 (paired beeswarm of per-fit CS sizes under identity-LD vs real-LD), per `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.2.d pending-item #4. The 10 admissible EUR autosomal regions × 5 traits (asthma, bmi, hypertension, stroke, t2d) need to be re-fired under the identity-LD code path with matched per-fit JSON output. Owner: Carter (LSF queue decision — 50-fit Snakemake subset re-fire). Until this lands, R1 delivers only the 2-bar scalar comparison; the paired distribution plot is blocked.

**(b) R2 figure-number alignment pass** — reconcile the numbering drift between `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 and `docs/manuscript/track_a_pivot.md` L291–L297 captions, then decide whether to rename `fig_cs_yield` → `fig1_cs_yield` (or `fig2_cs_yield`). Do NOT edit captions in isolation — the rename + caption edit + manuscript cross-references must all land in one commit to avoid divergent figure numbering between filename, caption, and in-text reference.

**(c) Dedicated figure-build env (`envs/r_figures.yml`)** — evaluate whether `la_multitrait_r` is the long-term figure-build env or whether a fresh pinned conda env should be provisioned for reproducibility. `la_multitrait_r` is sufficient for R1 and for Figures 2 and 3 as currently specified, but a pinned `envs/r_figures.yml` (R 4.4.2 + ggplot2 4.0.1 + tidyverse 2.0.0 + scales 1.4.0) would harden reproducibility for the preprint submission package. Low priority; not blocking.

**(d) Figure 2 build — SH2B3 12q24 locus plot** — separate quick task, blocked on a design decision about whether to use a LocusZoom-style embed, a custom ggplot regional-association panel, or a Manhattan-style strip for the identity-LD vs real-LD credible-set contrast at SH2B3 (flagship collapse locus per `TRACK-A-FROZEN-NUMBERS.md`). See `.planning/amendments/TRACK-A-PIVOT.md` §5 Figure 1B and `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 "Fig 2 = SH2B3 locus".

**(e) Figure 3 build — pathway enrichment reconfiguration** — separate quick task, blocked on a **pathway Results re-compute** per the `<!--PATHWAY-RECOMPUTE-PENDING-->` marker inserted by quick-260424-k2c in the Discussion Reframing paragraph. The real-LD-surviving gene set needs re-derivation from `results/multitrait/coloc_susie/*.json` filtered to Tier C signals, then re-run through `results/pathway/gprofiler/` before any fold-enrichment bar plot can be built. Do NOT attempt Figure 3 until the pathway re-compute lands.

## Self-check

File existence verification:

| Artifact | Expected path | Present |
| -------- | ------------- | ------- |
| R script | `src/R/figures/fig_cs_yield.R` | yes (210 lines) |
| Figure PDF | `docs/manuscript/figures/fig_cs_yield.pdf` | yes (23,540 bytes) |
| Figure PNG | `docs/manuscript/figures/fig_cs_yield.png` | yes (219,016 bytes) |
| Render log | `/tmp/lpy_fig_cs_yield_render.log` | yes |
| This SUMMARY | `.planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md` | yes |

Task 1 + Task 2 guardrail greps: all PASS (see Render output verification table above).

Framing audit: no occurrences of the three PLAN-forbidden framing terms appear in the SUMMARY body. The orchestrator's Task 3 automated verify block re-checks this via a case-insensitive word-bounded negative grep pattern against the plan-defined blocklist.

Citation audit (each referenced by name at least once):

- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — cited in Data-source audit + Environment sections.
- `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 — cited in Objective + Figure-number sections.
- `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.2.d — cited in Data-source audit + Handoff flag (a).

**Self-Check: PASSED**
