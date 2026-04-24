---
phase: quick-260424-lpy
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/R/figures/fig_cs_yield.R
  - docs/manuscript/figures/fig_cs_yield.pdf
  - docs/manuscript/figures/fig_cs_yield.png
  - .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md
autonomous: true
requirements:
  - ROUTE-A-STEP-2.3-FIG1
user_setup: []

must_haves:
  truths:
    - "An R script exists at src/R/figures/fig_cs_yield.R that reads results/fine_mapping/finemap_summary.tsv, cross-checks row count == 96, and derives the 51 non-empty credible-set count at runtime rather than hard-coding it."
    - "The identity-LD scalar baseline (12 / 96 non-empty credible sets) is encoded as a named R constant with an inline comment citing .planning/amendments/TRACK-A-FROZEN-NUMBERS.md as the canonical source."
    - "The script renders docs/manuscript/figures/fig_cs_yield.pdf (cairo_pdf device) + fig_cs_yield.png (600 dpi) at 85 mm × ~70 mm dimensions suitable for a Genome Medicine single-column figure."
    - "The rendered figure annotates the fold-change (4.25×), both absolute counts (12/96 and 51/96), and both percentages (12.5% and 53.1%) so a reviewer can verify the headline-yield delta from the figure alone."
    - "The figure caption in labs(caption=) cites both data sources by name: results/fine_mapping/finemap_summary.tsv and TRACK-A-FROZEN-NUMBERS.md."
    - "The script prints an intermediate per-ancestry × per-trait diagnostic table to stdout during render so future-Carter can debug yield splits without re-running SuSiE."
    - "A SUMMARY.md exists at .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md with ≥8 section headers + YAML frontmatter, flagging (a) Figure-2 paired-beeswarm blocking on identity-LD re-run, (b) figure-number convention drift vs manuscript captions deferred to R2, (c) handoff list for Fig 2 / Fig 3 / envs/r_figures.yml provisioning / identity-LD re-run session."
  artifacts:
    - path: "src/R/figures/fig_cs_yield.R"
      provides: "Reproducible Fig 1 (CS yield) R build script"
      min_lines: 60
      contains: "N_IDENTITY_LD_NONEMPTY <- 12"
    - path: "docs/manuscript/figures/fig_cs_yield.pdf"
      provides: "Vector PDF of Figure 1 for manuscript + preprint"
      min_bytes: 1024
    - path: "docs/manuscript/figures/fig_cs_yield.png"
      provides: "Raster PNG of Figure 1 for quick-preview + bioRxiv cover"
      min_bytes: 10240
    - path: ".planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md"
      provides: "Quick-task closeout with handoff flags"
  key_links:
    - from: "src/R/figures/fig_cs_yield.R"
      to: "results/fine_mapping/finemap_summary.tsv"
      via: "readr::read_tsv on the 97-line (header + 96 fits) canonical Stage 2 output"
      pattern: "read_tsv.*results/fine_mapping/finemap_summary.tsv"
    - from: "src/R/figures/fig_cs_yield.R"
      to: ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md"
      via: "Inline comment citing the 12 scalar baseline + labs(caption=) citation"
      pattern: "TRACK-A-FROZEN-NUMBERS"
    - from: "docs/manuscript/figures/fig_cs_yield.pdf"
      to: "docs/manuscript/track_a_pivot.md Figure 1 caption"
      via: "Manuscript Fig 1 caption alignment deferred to R2 (stem is neutral 'fig_cs_yield'; integer-rename at R2)"
      pattern: "fig_cs_yield"
---

<objective>
Route A Step 2.3 — build the first of three manuscript figures: the identity-LD vs real-LD credible-set yield plot (12/96 → 51/96, 4.25× fold increase). This is the headline-yield figure for the Track A pivot manuscript (`docs/manuscript/track_a_pivot.md`) per `.planning/amendments/TRACK-A-PIVOT.md` §5 Figure 2 spec and `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 "Fig 1 = CS yield".

Purpose: Give reviewers a single-panel visual that (a) makes the 4.25× fold increase in non-empty SuSiE credible sets under real 1000G Phase 3 EUR LD vs identity-LD fallback unmissable at a glance, (b) preserves the 96-fit denominator as visible context (not just the numerators), and (c) carries the citation trail back to the frozen-numbers file so the figure is trivially re-derivable if Stage 2 numbers ever shift.

Output: one portable R script (`src/R/figures/fig_cs_yield.R`) + two rendered artifacts (PDF + PNG at 85 mm figure width). Neutral filename stem `fig_cs_yield` — the integer Figure-number alignment against `docs/manuscript/track_a_pivot.md` L291–L297 captions is deferred to a later R2 caption-alignment pass because the manuscript captions currently label Fig 1 as the scatter + LocusZoom panels (disagreeing with snappy-humming-pine §2.3).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/amendments/TRACK-A-PIVOT.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@docs/manuscript/track_a_pivot.md

<interfaces>
<!-- Data-source schema the executor will consume. Spot-checked by planner. -->
<!-- Source: results/fine_mapping/finemap_summary.tsv (tab-delimited, 97 lines = 1 header + 96 fits). -->

Columns (17 total, in order):
  1. trait              — character  (e.g. "asthma", "bmi", "hypertension", ...)
  2. ancestry           — character  ("AFR" | "EUR")
  3. method             — character  ("susie")
  4. region_id          — character  (e.g. "FTO_16q12", "SH2B3_12q24", ...)
  5. status             — character  ("ok" | "too_many_variants" | "non_converged" | "no_variants")
  6. credible_sets      — integer    (count of non-empty credible sets for this fit; 0 means empty-fit)
  7. credible_set_sizes — character  (semicolon-delimited "CS{i}:size{i}" tokens; empty string when credible_sets == 0)
  8. variants_in_cs     — integer    (sum of CS sizes; 0 when credible_sets == 0)
  9. pip_nonzero        — integer
 10. top_chr            — integer (empty when credible_sets == 0)
 11. top_pos            — integer (empty when credible_sets == 0)
 12. top_pip            — double  (empty when credible_sets == 0)
 13. top_beta           — double  (empty when credible_sets == 0)
 14. top_se             — double  (empty when credible_sets == 0)
 15. sumstats           — character (path to harmonized sumstats input)
 16. ld_dir             — character (path to LD reference used; in this Stage-2 file, data/processed/ld_reference)
 17. output_path        — character (path to per-fit SuSiE JSON on disk)

Derivation the script must perform at runtime:
  df <- readr::read_tsv("results/fine_mapping/finemap_summary.tsv", show_col_types = FALSE)
  stopifnot(nrow(df) == 96)  # frozen denominator
  n_real_nonempty <- sum(df$credible_sets > 0, na.rm = TRUE)   # expect 51
  n_real_empty    <- sum(df$credible_sets == 0 | is.na(df$credible_sets))  # expect 45
  stopifnot(n_real_nonempty + n_real_empty == 96)

Locked scalars (from TRACK-A-FROZEN-NUMBERS.md — do NOT re-derive from disk; encode as constants):
  N_TOTAL_FITS            <- 96L    # Stage 2 admissible-fit denominator
  N_IDENTITY_LD_NONEMPTY  <- 12L    # identity-LD fallback baseline; pre-Stage-2
  N_REAL_LD_NONEMPTY      <- 51L    # Stage 2 real-LD expected value (cross-checked against disk)
  FOLD_CHANGE_EXPECTED    <- 4.25   # 51 / 12 = 4.25

R-environment availability (probed by planner against /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript):
  R version 4.4.2       — OK
  tidyverse 2.0.0       — OK (provides dplyr 1.1.4, readr 2.1.6, ggplot2 4.0.1)
  scales 1.4.0          — OK
  here                  — MISSING (do NOT library(here); use base-R relative paths from project root)
  showtext              — MISSING (do NOT use; cairo_pdf handles any Unicode without extra fonts)
  cowplot               — MISSING (do NOT use; theme_classic()/theme_minimal() is sufficient for this figure)
  ggpubr                — MISSING (do NOT use; base ggplot2 is sufficient)

Render command:
  /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig_cs_yield.R
Working directory: project root (/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis)
</interfaces>

<figure_spec>
<!-- Concrete design the R script must implement. No ambiguity, no taste calls left for the executor. -->

Type: 2-bar vertical bar chart (ordered categorical x-axis).
Geom: geom_col with width ≈ 0.6.

x-axis levels (order matters — identity first, real second, left-to-right):
  1. "Identity-LD fallback\n(pre-Stage-2)"
  2. "Real 1000G Phase 3 EUR LD\n(Stage 2)"

y-axis: integer count of non-empty credible sets (range 0 to 96; expand to show 96 denominator).
  - Add a horizontal dashed reference line at y = 96 with a right-aligned text annotation "96 admissible fits (denominator)".

Bar annotations (geom_text above each bar, vjust = -0.5):
  - Bar 1: "12 / 96  (12.5%)"
  - Bar 2: "51 / 96  (53.1%)"

Fold-change annotation (single geom_text or annotate centered over the two bars, y = ~75):
  - "4.25× yield\nunder real-LD"
  - Optional arrow segment from bar 1 top to bar 2 top to reinforce the comparison.

Fills: distinguishable but not chart-junk. Recommended — identity-LD bar a muted gray (#8A8A8A), real-LD bar a stronger blue (#3B6AA0). Do not use ggplot default rainbow palette.

Title:      "SuSiE-RSS credible-set yield across 96 admissible fits"
Subtitle:   "Real 1000G Phase 3 EUR LD vs identity-LD fallback — 4.25× fold increase"
Caption:    "Source: results/fine_mapping/finemap_summary.tsv (Stage 2, 2026-04-22 production fire).\nIdentity-LD scalar baseline from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (canonical).\nEUR + AFR admissible fits pooled for credible-set-yield count."
y-axis label: "Non-empty credible sets (count)"
x-axis label: "LD reference panel"

Theme: theme_classic(base_size = 9) — small base size because figure is 85 mm wide (single column).
  - Adjust plot.title / plot.subtitle sizes explicitly if theme_classic leaves them too large.
  - plot.caption size = 6.5, color = "grey30".
  - axis.text.x size = 8, lineheight = 0.9 (two-line x-labels).

Output dimensions:
  - PDF:  ggsave("docs/manuscript/figures/fig_cs_yield.pdf", plot, width = 85, height = 70, units = "mm", device = cairo_pdf)
  - PNG:  ggsave("docs/manuscript/figures/fig_cs_yield.png", plot, width = 85, height = 70, units = "mm", dpi = 600)

Pre-save assertion: require cairo_pdf availability (capabilities("cairo")). If FALSE, error with a message naming the missing capability; do NOT fall back to pdf() because that device has poorer font handling for Unicode superscripts that the caption/subtitle may eventually contain.

Diagnostic print before render (helps future debug):
  message("=== fig_cs_yield.R diagnostic ===")
  message(sprintf("Total fits parsed: %d (expected 96)", nrow(df)))
  message(sprintf("Non-empty real-LD fits: %d (expected 51)", n_real_nonempty))
  message(sprintf("Empty real-LD fits: %d (expected 45)", n_real_empty))
  message(sprintf("Identity-LD fallback baseline: %d (locked from TRACK-A-FROZEN-NUMBERS.md)", N_IDENTITY_LD_NONEMPTY))
  message(sprintf("Fold change: %.2fx", n_real_nonempty / N_IDENTITY_LD_NONEMPTY))
  print(df |> dplyr::count(ancestry, trait, has_cs = credible_sets > 0) |> tidyr::pivot_wider(names_from = has_cs, values_from = n, values_fill = 0L))
  message("=== writing outputs ===")
  message(sprintf("  %s", out_pdf))
  message(sprintf("  %s", out_png))

Post-save print (for verify automation):
  message(sprintf("wrote PDF: %s (%d bytes)", out_pdf, file.size(out_pdf)))
  message(sprintf("wrote PNG: %s (%d bytes)", out_png, file.size(out_png)))

No other geoms. No ML/tier overlays. No negative-control overlays. This is the CS-yield figure only — Fig 2 (paired beeswarm) and Fig 3 (pathway) are separate quicks.
</figure_spec>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Author src/R/figures/fig_cs_yield.R</name>
  <files>src/R/figures/fig_cs_yield.R</files>
  <action>
Create a new R script at `src/R/figures/fig_cs_yield.R` implementing the figure spec above exactly. First, `mkdir -p src/R/figures` (the directory does not yet exist — `src/R/` has only `utils/`).

**Script structure (top-to-bottom):**

1. **Header docstring** (≥15 lines, `#` comments):
   - First line: `# fig_cs_yield.R — Track A Figure 1 (identity-LD vs real-LD credible-set yield)`
   - Purpose one-liner
   - Citation lines:
     - `# Data source: results/fine_mapping/finemap_summary.tsv (Stage 2, 2026-04-22 production fire)`
     - `# Locked scalars: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (canonical source of the 12 identity-LD baseline)`
     - `# Upstream plans: .planning/amendments/TRACK-A-PIVOT.md §5; /home/ckclinto/.claude/plans/snappy-humming-pine.md §2.3`
   - Output declaration: `docs/manuscript/figures/fig_cs_yield.pdf` + `.png`
   - Render env: `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript` (R 4.4.2, ggplot2 4.0.1, tidyverse 2.0.0, scales 1.4.0)
   - Invocation example (from project root):
     `# /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig_cs_yield.R`
   - Author / date line: `# Carter K. Clinton — 2026-04-24 (quick-260424-lpy)`
   - "Figure-number note" line: `# Filename stem is neutral ('fig_cs_yield') pending manuscript caption-alignment pass (R2).`

2. **Library imports** — ONLY these (probed to be present in la_multitrait_r):
   ```r
   suppressPackageStartupMessages({
     library(readr)
     library(dplyr)
     library(tidyr)
     library(ggplot2)
     library(scales)
   })
   ```
   Do NOT import `here`, `showtext`, `cowplot`, `ggpubr` — they are missing from la_multitrait_r. Use base-R `file.path()` for paths.

3. **Constants block** (named, documented, the spec-locked scalars):
   ```r
   # Locked scalars from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
   N_TOTAL_FITS           <- 96L
   N_IDENTITY_LD_NONEMPTY <- 12L   # pre-Stage-2 identity-LD fallback baseline
   N_REAL_LD_NONEMPTY     <- 51L   # Stage 2 expected; cross-checked against disk below
   FOLD_CHANGE_EXPECTED   <- 4.25  # 51 / 12

   INPUT_TSV <- "results/fine_mapping/finemap_summary.tsv"
   OUT_DIR   <- "docs/manuscript/figures"
   OUT_PDF   <- file.path(OUT_DIR, "fig_cs_yield.pdf")
   OUT_PNG   <- file.path(OUT_DIR, "fig_cs_yield.png")
   ```

4. **Input validation + derivation**:
   - Assert `file.exists(INPUT_TSV)` with informative error.
   - Read with `read_tsv(INPUT_TSV, show_col_types = FALSE)`.
   - `stopifnot(nrow(df) == N_TOTAL_FITS)` — fail loud if Stage-2 denominator ever drifts.
   - Derive `n_real_nonempty <- sum(df$credible_sets > 0, na.rm = TRUE)`.
   - Derive `n_real_empty <- N_TOTAL_FITS - n_real_nonempty`.
   - Cross-check: `stopifnot(n_real_nonempty == N_REAL_LD_NONEMPTY)` with a message that if this fails, the script AND TRACK-A-FROZEN-NUMBERS.md both need updating in the same commit.

5. **Diagnostic table** — per-ancestry × trait split (printed to stdout, not plotted):
   ```r
   diag <- df |>
     mutate(has_cs = credible_sets > 0) |>
     count(ancestry, trait, has_cs) |>
     tidyr::pivot_wider(names_from = has_cs, values_from = n, values_fill = 0L,
                        names_prefix = "cs_")
   message("=== per-ancestry × per-trait CS-yield split (Stage 2 real-LD) ===")
   print(as.data.frame(diag))
   ```

6. **Plot data**:
   ```r
   plot_df <- tibble::tibble(
     condition = factor(c("Identity-LD fallback\n(pre-Stage-2)",
                          "Real 1000G Phase 3 EUR LD\n(Stage 2)"),
                        levels = c("Identity-LD fallback\n(pre-Stage-2)",
                                   "Real 1000G Phase 3 EUR LD\n(Stage 2)")),
     n_nonempty = c(N_IDENTITY_LD_NONEMPTY, n_real_nonempty),
     label      = c(sprintf("%d / %d  (%.1f%%)",
                            N_IDENTITY_LD_NONEMPTY, N_TOTAL_FITS,
                            100 * N_IDENTITY_LD_NONEMPTY / N_TOTAL_FITS),
                    sprintf("%d / %d  (%.1f%%)",
                            n_real_nonempty, N_TOTAL_FITS,
                            100 * n_real_nonempty / N_TOTAL_FITS))
   )
   ```

7. **ggplot build** — implement exactly the `<figure_spec>` block above:
   - `geom_col(aes(fill = condition), width = 0.6, show.legend = FALSE)`
   - `geom_text(aes(label = label), vjust = -0.6, size = 2.8)`
   - `geom_hline(yintercept = N_TOTAL_FITS, linetype = "dashed", colour = "grey50", linewidth = 0.3)`
   - `annotate("text", x = 2.45, y = N_TOTAL_FITS, label = "96 admissible fits", hjust = 1, vjust = -0.5, size = 2.6, colour = "grey30")` — but ensure annotation stays inside the plot panel (may need `coord_cartesian(clip = "off")` + `plot.margin` bump).
   - Fold-change annotation: `annotate("text", x = 1.5, y = 75, label = sprintf("%.2f× yield\nunder real-LD", n_real_nonempty / N_IDENTITY_LD_NONEMPTY), size = 3, fontface = "bold", lineheight = 0.95)`
   - Optional arrow: `annotate("segment", x = 1.1, xend = 1.9, y = 15, yend = 55, arrow = arrow(length = unit(2, "mm")), colour = "grey40", linewidth = 0.3)` — place it so it does not collide with the "75" fold-change text.
   - `scale_y_continuous(limits = c(0, 105), breaks = c(0, 25, 50, 75, 96), expand = expansion(mult = c(0, 0.02)))`
   - `scale_fill_manual(values = c("Identity-LD fallback\n(pre-Stage-2)" = "#8A8A8A", "Real 1000G Phase 3 EUR LD\n(Stage 2)" = "#3B6AA0"))`
   - `labs(title = "SuSiE-RSS credible-set yield across 96 admissible fits", subtitle = "Real 1000G Phase 3 EUR LD vs identity-LD fallback — 4.25× fold increase", x = "LD reference panel", y = "Non-empty credible sets (count)", caption = "Source: results/fine_mapping/finemap_summary.tsv (Stage 2, 2026-04-22 production fire). Identity-LD scalar baseline from .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (canonical). EUR + AFR admissible fits pooled for credible-set-yield count.")`
   - `theme_classic(base_size = 9)` + explicit `theme(plot.title = element_text(size = 10, face = "bold"), plot.subtitle = element_text(size = 8.5, colour = "grey25"), plot.caption = element_text(size = 6.5, colour = "grey30", hjust = 0, lineheight = 1.0), axis.text.x = element_text(size = 8, lineheight = 0.9), plot.margin = margin(t = 5, r = 8, b = 5, l = 5))`

8. **Save + stdout verification**:
   - `dir.create(OUT_DIR, recursive = TRUE, showWarnings = FALSE)`
   - Assert `capabilities("cairo")` is TRUE; error if not.
   - `ggsave(OUT_PDF, plot, width = 85, height = 70, units = "mm", device = cairo_pdf)`
   - `ggsave(OUT_PNG, plot, width = 85, height = 70, units = "mm", dpi = 600)`
   - Final stdout block (required for Task 2 verification — these literal strings are asserted):
     - `message(sprintf("fold-change: %.2fx (51/12 baseline)", n_real_nonempty / N_IDENTITY_LD_NONEMPTY))` — must emit the literal substring `4.25`
     - `message(sprintf("counts: identity-LD=12, real-LD=%d, empty=%d, total=%d", n_real_nonempty, n_real_empty, N_TOTAL_FITS))` — must emit the literals `12`, `51`, `45`, `96`
     - `message(sprintf("wrote %s (%d bytes)", OUT_PDF, file.size(OUT_PDF)))`
     - `message(sprintf("wrote %s (%d bytes)", OUT_PNG, file.size(OUT_PNG)))`

9. **Exit 0** — no explicit `quit()` needed; Rscript returns 0 if no error thrown.

**What NOT to do:**
- Do NOT invoke Snakemake, do NOT touch other figures, do NOT edit the manuscript.
- Do NOT add `library(here)`, `library(showtext)`, `library(cowplot)`, `library(ggpubr)` — these are missing from la_multitrait_r.
- Do NOT write to anywhere outside `src/R/figures/` (script) and `docs/manuscript/figures/` (outputs).
- Do NOT commit — the orchestrator owns Step 8 commits.
- Do NOT rename the manuscript's Figure 1/2/3 captions to match snappy-humming-pine §2.3 numbering — that is deferred to a separate R2 alignment task. This plan uses the neutral stem `fig_cs_yield` precisely to avoid premature integer numbering.
  </action>
  <verify>
    <automated>test -f src/R/figures/fig_cs_yield.R &amp;&amp; [ "$(wc -l &lt; src/R/figures/fig_cs_yield.R)" -ge 60 ] &amp;&amp; grep -q 'TRACK-A-FROZEN-NUMBERS' src/R/figures/fig_cs_yield.R &amp;&amp; grep -q 'results/fine_mapping/finemap_summary.tsv' src/R/figures/fig_cs_yield.R &amp;&amp; grep -cE 'N_IDENTITY_LD_NONEMPTY[[:space:]]*&lt;-[[:space:]]*12' src/R/figures/fig_cs_yield.R | grep -qx 1 &amp;&amp; grep -q 'cairo_pdf' src/R/figures/fig_cs_yield.R &amp;&amp; grep -q 'stopifnot(nrow(df) == N_TOTAL_FITS)' src/R/figures/fig_cs_yield.R &amp;&amp; ! grep -qE '^[[:space:]]*library\((here|showtext|cowplot|ggpubr)\)' src/R/figures/fig_cs_yield.R</automated>
  </verify>
  <done>
- `src/R/figures/fig_cs_yield.R` exists and has ≥60 lines.
- Contains citations to TRACK-A-FROZEN-NUMBERS.md and results/fine_mapping/finemap_summary.tsv.
- Encodes `N_IDENTITY_LD_NONEMPTY <- 12` exactly once.
- Uses `cairo_pdf` device; asserts `capabilities("cairo")`.
- Hard-fails if `nrow(df) != 96`.
- Does NOT import any of the missing packages (here / showtext / cowplot / ggpubr).
  </done>
</task>

<task type="auto">
  <name>Task 2: Render figure (PDF + PNG) via la_multitrait_r</name>
  <files>docs/manuscript/figures/fig_cs_yield.pdf, docs/manuscript/figures/fig_cs_yield.png</files>
  <action>
Render the figure by invoking the la_multitrait_r Rscript binary directly (no env activation; per the user's feedback memory "Don't tell user to conda activate"):

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig_cs_yield.R 2>&1 | tee /tmp/lpy_fig_cs_yield_render.log
```

Requirements:
- Working directory must be the project root (the script uses relative paths like `results/fine_mapping/finemap_summary.tsv` and `docs/manuscript/figures/`).
- Capture stdout/stderr to `/tmp/lpy_fig_cs_yield_render.log` so the log can be inspected by the verify block.
- On success, the log must contain the literal substrings `4.25`, `12`, `51`, `45`, `96` (per the stdout spec in Task 1 step 8).
- On success, both output files must exist with non-trivial sizes:
  - PDF ≥ 1 KB (vector output should be a few KB minimum)
  - PNG ≥ 10 KB (600 dpi 85 × 70 mm raster should be several tens of KB)
- Post-render, optionally probe PDF page size: `pdfinfo docs/manuscript/figures/fig_cs_yield.pdf 2>/dev/null | grep -E 'Page size'` — if `pdfinfo` is not installed, skip silently.

**Render-failure contingency (executor judgement call, must be documented in SUMMARY.md):**

If the Rscript invocation fails (missing package, permission, font issue, etc.):
1. Capture the full stderr in `/tmp/lpy_fig_cs_yield_render.log`.
2. Do NOT fake the output files — do not create empty PDF/PNG placeholders.
3. Proceed to Task 3 (SUMMARY.md) with a "RENDER-DEFERRED" section citing the exact error + the log path, so future-Carter can re-render from a working R env after fixing the env gap. The R script itself still lands on disk (Task 1 is independent).
4. Flag the env-gap as a handoff item: whether `la_multitrait_r` needs patching, or whether a separate `envs/r_figures.yml` should be provisioned.

**Expected happy-path outcome:**
- `docs/manuscript/figures/fig_cs_yield.pdf` — ~5–15 KB vector PDF
- `docs/manuscript/figures/fig_cs_yield.png` — ~30–80 KB 600 dpi raster
- Stdout log contains the diagnostic table + all four locked numbers (12, 51, 45, 96) + the fold change (4.25x) + both `wrote <path> (<N> bytes)` lines.
  </action>
  <verify>
    <automated>test -f docs/manuscript/figures/fig_cs_yield.pdf &amp;&amp; test -f docs/manuscript/figures/fig_cs_yield.png &amp;&amp; [ "$(stat -c %s docs/manuscript/figures/fig_cs_yield.pdf)" -ge 1024 ] &amp;&amp; [ "$(stat -c %s docs/manuscript/figures/fig_cs_yield.png)" -ge 10240 ] &amp;&amp; grep -q '4.25' /tmp/lpy_fig_cs_yield_render.log &amp;&amp; grep -q '51' /tmp/lpy_fig_cs_yield_render.log &amp;&amp; grep -q '12' /tmp/lpy_fig_cs_yield_render.log &amp;&amp; grep -q '45' /tmp/lpy_fig_cs_yield_render.log &amp;&amp; grep -q '96' /tmp/lpy_fig_cs_yield_render.log</automated>
  </verify>
  <done>
- Both `docs/manuscript/figures/fig_cs_yield.pdf` (≥ 1 KB) and `docs/manuscript/figures/fig_cs_yield.png` (≥ 10 KB) exist.
- Render log `/tmp/lpy_fig_cs_yield_render.log` contains `4.25`, `12`, `51`, `45`, `96`.
- Script exited 0.
- **Render-deferred branch**: if render fails, R script still exists on disk, the log is captured, and SUMMARY.md documents the exact error + env-gap handoff. Executor must NOT fabricate output files.
  </done>
</task>

<task type="auto">
  <name>Task 3: Author 260424-lpy-SUMMARY.md</name>
  <files>.planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md</files>
  <action>
Author the quick-task closeout summary at `.planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md`. This is the handoff artifact — the orchestrator reads it at Step 7/8 and future-Carter reads it on resume.

**Required frontmatter (YAML, between triple-dash delimiters):**

```yaml
---
quick_id: 260424-lpy
title: "Route A Step 2.3 — Figure 1 (CS yield) build"
date: 2026-04-24
status: complete   # or "render-deferred" if Task 2 failed
route: A
step: "2.3"
parent_plan: /home/ckclinto/.claude/plans/snappy-humming-pine.md
authoritative_numbers: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
outputs:
  - src/R/figures/fig_cs_yield.R
  - docs/manuscript/figures/fig_cs_yield.pdf
  - docs/manuscript/figures/fig_cs_yield.png
---
```

**Required section headers (≥8 — use exactly these h2 headings):**

1. `## Objective` — one paragraph: what figure was built, why, linking to snappy-humming-pine.md §2.3 + TRACK-A-PIVOT.md §5. Frame as **original research** per the feedback memory — never "revision", "cleanup", or "fix".

2. `## Data-source audit` — document what's available and what isn't:
   - Available: `results/fine_mapping/finemap_summary.tsv` (97 lines = 1 header + 96 fits), confirms 51 non-empty CS runtime-derived.
   - NOT available: per-fit identity-LD SuSiE output. The 12/96 identity-LD baseline is a **locked scalar** from TRACK-A-FROZEN-NUMBERS.md only; no per-fit paired dataset exists to build the manuscript's Figure 2 paired beeswarm (L293 caption).
   - Consequence: R1 delivers the two-bar scalar comparison (12 vs 51 out of 96). The paired-beeswarm per-fit plot is explicitly deferred pending identity-LD re-run.

3. `## Figure-number convention decision (deferred)` — document the drift:
   - snappy-humming-pine.md §2.3 labels the CS-yield figure as "Fig 1".
   - `docs/manuscript/track_a_pivot.md` L291–L297 currently label Fig 1 = scatter + LocusZoom panels, Fig 2 = paired beeswarm (this CS-yield visual by the manuscript's current caption plan), Fig 3 = survival forest.
   - R1 chose the neutral filename stem `fig_cs_yield` (no integer) to avoid prematurely committing to either numbering scheme.
   - Integer-rename is an R2 handoff task paired with a manuscript caption-alignment pass.

4. `## R script — listing excerpt` — first 20 lines + last 10 lines of `src/R/figures/fig_cs_yield.R` (to document what was written without forcing future-Carter to open the file).

5. `## Render output verification` — enumerate:
   - Whether render succeeded.
   - Output file existence + sizes (`ls -la docs/manuscript/figures/fig_cs_yield.*`).
   - Key stdout lines captured from `/tmp/lpy_fig_cs_yield_render.log` (fold change, counts, byte sizes).
   - If render FAILED: capture the exact error + path to the full log; flag that the R script is on disk regardless.

6. `## Environment & reproducibility` — document:
   - Render env: `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript` (R 4.4.2 + ggplot2 4.0.1 + tidyverse 2.0.0 + scales 1.4.0).
   - Packages that were missing from la_multitrait_r and how the script sidesteps them: here / showtext / cowplot / ggpubr — all avoided.
   - `envs/r_coloc.yml` is the coloc-working env, not a figure-build env; a dedicated `envs/r_figures.yml` is a future provisioning task (handoff item).

7. `## Commits created` — empty table; state explicitly that this quick task creates no commits; orchestrator handles Step 8 commits. Note the file paths that will land in the commit: the R script, the two figure outputs, and this SUMMARY.md.

8. `## Handoff flags` — explicit bulleted handoffs for future sessions:
   - (a) **Identity-LD re-run session** required to unlock manuscript Figure 2 (paired beeswarm of per-fit CS sizes under identity-LD vs real-LD), per snappy-humming-pine.md §2.2.d pending item #4. Owner: Carter (LSF decision on 10-region × 5-trait Snakemake subset re-fire).
   - (b) **R2 figure-number alignment pass**: reconcile `docs/manuscript/track_a_pivot.md` L291–L297 Figure 1/2/3 captions against snappy-humming-pine §2.3 numbering, then decide whether to rename `fig_cs_yield` → `fig1_cs_yield` (or `fig2_cs_yield`). Do NOT change captions in isolation — the rename + caption edit + manuscript cross-references must land in one commit.
   - (c) **Dedicated figure-build env** (`envs/r_figures.yml`): evaluate whether la_multitrait_r is the long-term figure-build env or whether a fresh pinned env should be provisioned for reproducibility. Low priority; la_multitrait_r is sufficient for R1.
   - (d) **Figure 2 build** (SH2B3 12q24 locus plot) — separate quick, blocked on a decision about whether to use LocusZoom, a custom ggplot, or Manhattan-style layout (see TRACK-A-PIVOT.md §5 Figure 1B and snappy-humming-pine §2.3 "Fig 2 = SH2B3 locus").
   - (e) **Figure 3 build** (pathway enrichment) — separate quick, blocked on pathway Results re-compute per the `<!--PATHWAY-RECOMPUTE-PENDING-->` marker inserted by quick 260424-k2c in the Discussion Reframing paragraph.

Additional hygiene:
- Confirm zero forbidden terms ("revision", "cleanup", "fix") in the SUMMARY body. Frame everything as original research.
- Cite TRACK-A-FROZEN-NUMBERS.md + snappy-humming-pine.md §2.3 + snappy-humming-pine.md §2.2.d each by name (verify with grep).

**Do NOT:**
- Update STATE.md — that is the orchestrator's concern at Step 7/8.
- Update ROADMAP.md — explicitly excluded per planning_context constraints.
- Create commits — the orchestrator owns Step 8 commits.
  </action>
  <verify>
    <automated>test -f .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md &amp;&amp; [ "$(grep -c '^## ' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md)" -ge 8 ] &amp;&amp; head -1 .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md | grep -qx '---' &amp;&amp; grep -q 'TRACK-A-FROZEN-NUMBERS' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md &amp;&amp; grep -q 'snappy-humming-pine' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md &amp;&amp; grep -qE '§2\.3' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md &amp;&amp; grep -qE '§2\.2\.d' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md &amp;&amp; ! grep -qiE '\b(revision|cleanup|\bfix\b)\b' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md</automated>
  </verify>
  <done>
- `.planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md` exists.
- ≥ 8 `## ` section headers.
- YAML frontmatter present (first line is `---`).
- References TRACK-A-FROZEN-NUMBERS.md, snappy-humming-pine.md §2.3, snappy-humming-pine.md §2.2.d each by name.
- Zero occurrences of forbidden terms (revision / cleanup / fix).
- All 5 handoff flags (a–e) present in the `## Handoff flags` section.
  </done>
</task>

</tasks>

<verification>
Overall quick-task completeness after all 3 tasks:

```bash
# R script exists and is non-trivial
test -f src/R/figures/fig_cs_yield.R && wc -l src/R/figures/fig_cs_yield.R

# Figure artifacts rendered
ls -la docs/manuscript/figures/fig_cs_yield.pdf docs/manuscript/figures/fig_cs_yield.png

# Numbers traceable in render log
grep -E '4\.25|^.*(51|12|45|96).*' /tmp/lpy_fig_cs_yield_render.log | head -20

# SUMMARY.md handoff artifact present
test -f .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md
grep -c '^## ' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md

# No forbidden framing
! grep -qiE '\b(revision|cleanup|\bfix\b)\b' .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md
```

Render-deferred variant (if Task 2 fails): figure artifacts absent is ACCEPTABLE provided SUMMARY.md has a `## Render output verification` section that explicitly flags render-deferred + cites the log path + identifies the env gap.
</verification>

<success_criteria>
- `src/R/figures/fig_cs_yield.R` exists, ≥60 lines, uses only packages present in la_multitrait_r (readr / dplyr / tidyr / ggplot2 / scales), encodes the 12 baseline as `N_IDENTITY_LD_NONEMPTY <- 12`, cites TRACK-A-FROZEN-NUMBERS.md + the finemap_summary.tsv source, uses cairo_pdf device, and asserts `nrow(df) == 96`.
- `docs/manuscript/figures/fig_cs_yield.pdf` + `.png` exist with non-trivial sizes (or render-deferred branch documented in SUMMARY.md with log path + error).
- Render stdout log contains 4.25, 12, 51, 45, 96 as literal substrings.
- SUMMARY.md has ≥8 section headers, YAML frontmatter, 5 handoff flags, zero forbidden-framing terms, cites TRACK-A-FROZEN-NUMBERS.md + snappy-humming-pine.md §2.3 + §2.2.d by name.
- No commits created by the executor (orchestrator owns Step 8).
- No edits to STATE.md or ROADMAP.md.
</success_criteria>

<output>
After completion:
- Artifacts to commit at orchestrator Step 8: `src/R/figures/fig_cs_yield.R`, `docs/manuscript/figures/fig_cs_yield.pdf`, `docs/manuscript/figures/fig_cs_yield.png`, `.planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md`.
- Commit message framing (orchestrator will author): original-research framing per CLAUDE.md feedback memory. Example: `docs(quick-260424-lpy): build Track A Figure 1 — identity-LD vs real-LD credible-set yield (12/96 → 51/96, 4.25× fold)`. NOT "revision", "cleanup", or "fix".
- SUMMARY.md resides at: `.planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md`.
</output>
