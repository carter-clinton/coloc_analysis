---
phase: quick-260425-kki
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/R/figures/fig2_cs_yield.R
  - docs/manuscript/figures/fig2_cs_yield.pdf
  - docs/manuscript/figures/fig2_cs_yield.png
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  - docs/manuscript/track_a_pivot.md
  - src/R/figures/fig3_sh2b3_eur_collapse_forest.R
  - docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf
  - docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png
  - .planning/amendments/TRACK-A-PIVOT.md
autonomous: true
requirements: [TRACK-A-COMPARATOR-TIGHTEN, TRACK-A-DATA-QUALITY-DISCLOSURE, TRACK-A-LEGACY-NUMERICS-PURGE]

must_haves:
  truths:
    - "fig2_cs_yield.R derives the identity-LD non-empty CS count from disk (IDENTITY-LD-K2D-FIT-SUMMARY.tsv) rather than hardcoding 12L"
    - "fig2_cs_yield.pdf and fig2_cs_yield.png render with bar heights 48/95 (identity-LD) vs 51/96 (real-LD) and a 1.06× annotation"
    - "TRACK-A-FROZEN-NUMBERS.md records the post-k2d full-coverage baseline (48/95 ≈ 50.5%) and preserves the prior 12/96 value as SUPERSEDED 2026-04-25 with audit trail"
    - "track_a_pivot.md no longer cites 4.25× / 12 of 96 / 12/96 as live headline numbers; all seven sites (L28 Abstract, L82 Methods, L138 Headline, L214 Strengths, L222 Pathway, L252 Conclusions, L293 Fig 2 caption) are reframed using tightened-comparator language"
    - "fig3_sh2b3_eur_collapse_forest.R surfaces ld_overlap_fraction + susie_status + L_saturated as a sub-table panel under the existing forest"
    - "track_a_pivot.md Tier-C reporting prose surfaces the FTO_16q12 EUR ld_overlap_fraction = 0 finding for the PP.H4 = 0.3099 row"
    - "TRACK-A-PIVOT.md amendment file no longer carries 1,446 / 861 ghost numerics at the 10 surviving sites"
    - "track_a_pivot.md Methods reconciles the 95-vs-96 denominator and names the missing bmi.EUR.APOE_19q13 fit"
  artifacts:
    - path: "src/R/figures/fig2_cs_yield.R"
      provides: "fig2 builder reading disk-truth identity-LD baseline"
      contains: "IDENTITY-LD-K2D-FIT-SUMMARY.tsv"
    - path: "docs/manuscript/figures/fig2_cs_yield.pdf"
      provides: "fig2 cairo_pdf with 48/95 vs 51/96 bars and 1.06× fold annotation"
    - path: "docs/manuscript/figures/fig2_cs_yield.png"
      provides: "fig2 600 dpi PNG matching the PDF"
    - path: ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md"
      provides: "frozen-numbers ledger updated with post-k2d full-coverage baseline + SUPERSEDED block preserving 12/96 for audit"
      contains: "Stage 2 fine-mapping yield (post-k2d full-coverage 2026-04-25)"
    - path: "docs/manuscript/track_a_pivot.md"
      provides: "manuscript with tightened-comparator framing across all seven sites + Tier-C data-quality disclosure + 95-vs-96 denominator note"
    - path: "src/R/figures/fig3_sh2b3_eur_collapse_forest.R"
      provides: "fig3 builder with ld_overlap_fraction + susie_status + L_saturated sub-table panel"
    - path: "docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf"
      provides: "fig3 PDF with sub-table panel re-rendered"
    - path: "docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png"
      provides: "fig3 PNG matching PDF"
    - path: ".planning/amendments/TRACK-A-PIVOT.md"
      provides: "amendment file with 1,446 / 861 ghosts purged at all 10 sites"
  key_links:
    - from: "src/R/figures/fig2_cs_yield.R"
      to: ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"
      via: "read_tsv() at script start; sum(n_CS > 0) computes 48"
      pattern: "IDENTITY-LD-K2D-FIT-SUMMARY"
    - from: "docs/manuscript/track_a_pivot.md"
      to: ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md"
      via: "headline numerics 48/95 vs 51/96 cite the frozen-numbers ledger verbatim"
      pattern: "1\\.06|48 / 95|48/95"
    - from: "src/R/figures/fig3_sh2b3_eur_collapse_forest.R"
      to: "results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json + results/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json"
      via: "fromJSON() reads ld_overlap_fraction, convergence_status, L_saturated for both LD branches"
      pattern: "ld_overlap_fraction"
---

<objective>
Track A audit-driven figure correction pass — fig2 baseline, fig3 disclosure, Tier-C data-quality.

Track A's headline numerics shifted: the previously cited 4.25× fold-increase in SuSiE-RSS credible-set yield (12/96 identity-LD → 51/96 real-LD) was anchored on a partial-coverage Stage 1d narrow-validation baseline. The k2d full-coverage identity-LD re-fire (2026-04-25) produced 48/95 non-empty credible sets at the same admissibility set as Stage 2 real-LD. Under the matched-coverage comparator the contrast is **48 of 95 (50.5%) → 51 of 96 (53.1%) ≈ 1.06× yield increase**.

The framing rule is non-negotiable: this is "we tightened the comparator and the inflation magnitude shifted" — NOT "we made an error and corrected it." Every commit message, manuscript prose, and amendment edit must use that anchor language.

Purpose: re-anchor Track A's load-bearing figure (fig2), surface previously hidden data-quality signals (fig3 LD overlap + susie status + Tier-C ld_overlap_fraction = 0 at FTO), purge legacy ghost numerics from the planning amendment, and document the 95-vs-96 denominator reconciliation. The Priority 1 commit (T5) is independently load-bearing — if W2/W3 don't land, T5 alone makes the manuscript honest.

Output: 4 atomic commits across 3 waves; one deferred follow-on (HLA double-classification) recorded for user direction; deferred upstream-compute follow-ons (SH2B3 L=20 re-fit, canonical trait-pair coloc.susie, PIP-shift composition figure, pathway recompute, submission decision) recorded in SUMMARY.md.

**NOTE: The user brief references `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` as the source of truth, but that file does not exist on disk.** The user's brief itself is the working spec for this task. SUMMARY.md must record this so future readers know the audit content was inlined in the brief, not in a separate file.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv
@.planning/amendments/TRACK-A-PIVOT.md
@results/fine_mapping/finemap_summary.tsv
@src/R/figures/fig2_cs_yield.R
@src/R/figures/fig3_sh2b3_eur_collapse_forest.R
@docs/manuscript/track_a_pivot.md

<framing_lock>
Per user memory `feedback_original_research_framing`: zero "revision / cleanup / fix-up / error / correction / mistake / we got this wrong / v1 / simplified / placeholder / TBD" tokens in any commit message, manuscript prose, or PLAN/SUMMARY edit. The framing is **"we tightened the comparator and the inflation magnitude shifted"** — this language must appear verbatim or near-verbatim in T4 manuscript edits.

Per user memory `feedback_no_conda`: do NOT instruct the user to `conda activate`. Invoke Rscript via the absolute path `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript`.
</framing_lock>

<disk_truth_facts>
Verified by orchestrator and re-confirmed by planner against disk:

| Source | Denominator | Non-empty CS | % | Notes |
|---|---|---|---|---|
| `results/fine_mapping/finemap_summary.tsv` (real-LD Stage 2) | 96 | 51 | 53.1% | column `credible_sets` (count) |
| `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` (identity-LD k2d full-coverage 2026-04-25) | 95 | 48 | 50.5% | column `n_CS` |
| Fold change | — | — | — | **51/48 = 1.0625× ≈ 1.06×** (or 50.5% → 53.1%, ~2.6 pp delta) |
| Missing 96th fit | — | — | — | `bmi.EUR.APOE_19q13` (real-LD status = `non_converged`, n_CS=6); absent from k2d identity-LD manifest |
| FTO_16q12 EUR Tier-C real-LD ld_overlap_fraction | — | — | — | **0** (`ld_status = variants_exceed_threshold`); buried in fig1b R-script header comment; must surface in Tier-C reporting |

SH2B3_12q24 EUR per-trait CS counts (already locked in fig3 EXPECTED_ID_CS / EXPECTED_REAL_CS — leave these scalars alone in fig3):
- Identity-LD k2d: asthma=0, bmi=3, hypertension=10, stroke=10, t2d=2
- Real-LD: asthma=1 (status=ok), bmi=8 (non_converged), hypertension=4 (non_converged), stroke=2 (non_converged), t2d=9 (status=ok)
- Real-LD ld_overlap_fraction at SH2B3 EUR: asthma=0.0385 (the one "ok" fit has only 3.85% overlap)
- Identity-LD ld_overlap: 0 by definition (identity matrix → no real-LD measurement)
</disk_truth_facts>

<manuscript_target_sites>
The seven sites in `docs/manuscript/track_a_pivot.md` carrying 4.25× / 12/96 / 12 of 96 language:

| Line | Section | What needs reframing |
|---|---|---|
| L28 | Abstract | "51 of 96 (53.1%) ... compared with 12 of 96 (12.5%) ... 4.25-fold increase in fine-mapping yield" |
| L82 | Methods §Identity-LD vs Real-LD Comparison | "51 of 96 ... only 12 of 96 fits (13%) ... 4.25-fold yield increase" |
| L138 | Results §Headline | "51 of 96 ... 12 of 96 (12.5%) ... 4.25-fold increase (Figure 2)" |
| L214 | Discussion §Strengths | "4.25-fold increase ... real-LD relative to identity-LD fallback (51/96 vs 12/96)" |
| L222 | Discussion §Pathway reframing | "4.25-fold more numerous under identity-LD fallback than under matched real-LD" |
| L252 | Conclusions | "SuSiE-RSS + real 1000G EUR LD yielded 4.25-fold more non-empty credible sets ... (51/96 vs 12/96)" |
| L293 | Figure 2 caption | "12 / 96 (12.5%) under identity-LD fallback vs 51 / 96 (53.1%) ... 4.25× fold-increase" |

Note: Stage 2 commit-hash anchor citations (`6de9a88`, `a6e3214`, `7d54183`, `1635d37`) at L146/L148 are PRESERVED — they are audit anchors and unaffected by the baseline tightening.
</manuscript_target_sites>

<ghost_numeric_sites>
Surviving "1,446" / "861" tokens in `.planning/amendments/TRACK-A-PIVOT.md` (10 sites — manuscript itself is clean):
L37, L41, L80, L104, L125, L134, L181, L257, L267, L375.

Replace with disk-truth Stage 2 numerics per `TRACK-A-FROZEN-NUMBERS.md` (28 trait-pair coloc.susie tests / 1,274 QTL-coloc attempts / 1,005 too_few_snps / 32 successes).
</ghost_numeric_sites>

<wave_structure>
| Wave | Tasks | Atomic commit | Independence |
|---|---|---|---|
| 1 | T1, T2, T3, T4, T5 | `docs(quick-260425-kki): tighten Stage 2 fine-mapping yield comparator against k2d full-coverage identity-LD re-fire` | Headline-killer — must land first as a single coherent commit set; if W2/W3 don't land, this alone makes the manuscript honest |
| 2 | T6, T7, T8 | `docs(quick-260425-kki): surface ld_overlap_fraction + susie_status data-quality on Fig 3 + Tier-C reporting` | Depends on W1 (manuscript prose around Tier-C lives in same file as W1 edits — sequential to avoid merge conflicts) |
| 3 | T9, T11 | T9: `docs(quick-260425-kki): purge 1,446 / 861 ghost numerics from TRACK-A-PIVOT.md amendment`; T11: `docs(quick-260425-kki): document 95 vs 96 denominator and missing bmi.EUR.APOE_19q13 fit` | Two independent atomic commits; T10 (HLA double-classification) DEFERRED — requires audit-author judgment that orchestrator does not have |
</wave_structure>
</context>

<tasks>

<task type="auto">
  <name>Task 1 (W1): Replace fig2 hardcoded identity-LD baseline with disk-derived k2d count</name>
  <files>src/R/figures/fig2_cs_yield.R</files>
  <action>
Edit `src/R/figures/fig2_cs_yield.R` to derive the identity-LD non-empty CS count from disk rather than hardcoding 12L. Specific edits:

1. **Header comment block (L1-L46):** Update the purpose paragraph to reflect the matched-coverage comparator. Replace "12 / 96" with "48 / 95" and "4.25x fold increase" with "~1.06x fold increase under matched-coverage comparator". Add a comment block explaining the comparator change anchored on the framing lock language: "We tightened the comparator from a partial-coverage Stage 1d narrow-validation baseline (12/96, 2 of 10 admissible regions had identity-LD fits) to the k2d full-coverage 2026-04-25 re-fire (48/95, all admissibility-matched regions); the inflation magnitude shifted from 4.25× to ~1.06×." Leave the figure-number provenance block (L36-L46) intact apart from the locked-scalar reference update.

2. **Locked-scalar block (L56-L62):** Replace the four hardcoded scalars with disk-driven derivations:
   - REMOVE: `N_IDENTITY_LD_NONEMPTY <- 12L` and `FOLD_CHANGE_EXPECTED <- 4.25`.
   - ADD a new constant block:
     ```r
     # k2d identity-LD full-coverage re-fire (2026-04-25); disk-truth source.
     IDENTITY_LD_TSV          <- ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"
     N_IDENTITY_LD_TOTAL_EXPECTED <- 95L     # k2d enumerated 95 of 96 fits
     N_IDENTITY_LD_NONEMPTY_EXPECTED <- 48L  # disk-derived assertion
     N_TOTAL_FITS             <- 96L         # Stage 2 real-LD admissible-fit denominator
     N_REAL_LD_NONEMPTY       <- 51L         # Stage 2 real-LD; cross-checked against disk
     ```
   - The `FOLD_CHANGE_EXPECTED` scalar is REMOVED entirely — fold-change is computed from disk-derived counts and printed in diagnostics, not hardcoded as an assertion.

3. **Disk-backed derivation block (immediately after the existing `read_tsv(INPUT_TSV)` at L77-L82):** ADD a parallel derivation reading the identity-LD TSV:
   ```r
   if (!file.exists(IDENTITY_LD_TSV)) {
     stop(sprintf(
       "fig2_cs_yield.R: identity-LD source TSV not found at '%s'. Run from project root.",
       IDENTITY_LD_TSV
     ))
   }
   df_id <- read_tsv(IDENTITY_LD_TSV, show_col_types = FALSE)
   stopifnot(nrow(df_id) == N_IDENTITY_LD_TOTAL_EXPECTED)
   n_id_nonempty <- sum(df_id$n_CS > 0, na.rm = TRUE)
   if (n_id_nonempty != N_IDENTITY_LD_NONEMPTY_EXPECTED) {
     stop(sprintf(
       paste0(
         "fig2_cs_yield.R: disk-derived identity-LD non-empty CS count (%d) does not match ",
         "expected k2d full-coverage value %d from IDENTITY-LD-K2D-FIT-SUMMARY.tsv. ",
         "If k2d has been re-fired, update the expected scalar here and TRACK-A-FROZEN-NUMBERS.md ",
         "in the same commit."
       ),
       n_id_nonempty, N_IDENTITY_LD_NONEMPTY_EXPECTED
     ))
   }
   N_IDENTITY_LD_TOTAL <- nrow(df_id)
   ```

4. **Diagnostic stdout block (L107-L114):** Replace the "(locked from TRACK-A-FROZEN-NUMBERS.md)" suffix with "(disk-derived from IDENTITY-LD-K2D-FIT-SUMMARY.tsv, k2d full-coverage 2026-04-25)". Update the fold-change line to print both the matched-coverage value and the denominators:
   ```r
   message(sprintf("Identity-LD non-empty fits (k2d full-coverage 2026-04-25): %d / %d",
                   n_id_nonempty, N_IDENTITY_LD_TOTAL))
   message(sprintf("Real-LD non-empty fits (Stage 2 2026-04-22): %d / %d",
                   n_real_nonempty, N_TOTAL_FITS))
   message(sprintf("Fold change (matched-coverage): %.3fx (%d / %d)",
                   n_real_nonempty / n_id_nonempty, n_real_nonempty, n_id_nonempty))
   ```

5. **Plot data block (L120-L134):** Update the `plot_df` tibble to use `n_id_nonempty` and `N_IDENTITY_LD_TOTAL` instead of `N_IDENTITY_LD_NONEMPTY` and `N_TOTAL_FITS` for the identity-LD bar. The two condition labels remain "Identity-LD fallback" / "Real 1000G Phase 3 EUR LD" but the parenthetical can be updated to "(k2d 2026-04-25)" / "(Stage 2 2026-04-22)" for date provenance. The label string for the identity-LD bar must use the correct denominator 95: `sprintf("%d / %d  (%.1f%%)", n_id_nonempty, N_IDENTITY_LD_TOTAL, 100 * n_id_nonempty / N_IDENTITY_LD_TOTAL)` → renders "48 / 95  (50.5%)".

6. **ggplot annotations (L137-L196):**
   - Update the arrow segment + fold-change annotation (L153-L165): the arrow now connects roughly equal bar heights (48 vs 51), so the dramatic upward arrow no longer fits. Replace the arrow + "%.2fx yield" annotation with a horizontal note `annotate("text", x = 1.5, y = 65, label = sprintf("%.2fx yield\n(matched-coverage)", n_real_nonempty / n_id_nonempty), size = 3, fontface = "bold", lineheight = 0.95)` — the segment annotation can be DROPPED (`annotate("segment", ...)` removed) or kept as a flat horizontal segment if visually preferred. Use planner judgment: prefer drop, since the arrow gestures upward dramatically when the actual delta is ~3 percentage points.
   - Update `subtitle` (L180): "Real 1000G Phase 3 EUR LD vs identity-LD fallback (k2d full-coverage 2026-04-25) -- ~1.06x fold increase under matched-coverage comparator"
   - Update y-axis: the previous limits c(0, 105) and breaks at 25/50/75/96 are still appropriate. The 96-line dashed reference line is fine — annotate it as "96 admissible Stage 2 fits" (existing) but ALSO add a thin secondary reference at y = 95 for the identity-LD denominator if visually clean (planner judgment: optional; only do this if it doesn't clutter the figure).

7. **Caption block (L183-L188):** Replace with:
   ```r
   caption  = paste0(
     "Sources: results/fine_mapping/finemap_summary.tsv (Stage 2 real-LD, 2026-04-22) +\n",
     ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (k2d full-coverage identity-LD, 2026-04-25).\n",
     "Matched-coverage comparator: 48 of 95 identity-LD fits vs 51 of 96 real-LD fits = ~1.06x yield.\n",
     "EUR + AFR admissible fits pooled for credible-set-yield count."
   )
   ```

8. **Post-save verification stdout (L213-L217):** Update the assertion lines:
   ```r
   message(sprintf("fold-change: %.3fx (%d real-LD / %d identity-LD k2d)",
                   n_real_nonempty / n_id_nonempty, n_real_nonempty, n_id_nonempty))
   message(sprintf("counts: identity-LD=%d/%d, real-LD=%d/%d",
                   n_id_nonempty, N_IDENTITY_LD_TOTAL, n_real_nonempty, N_TOTAL_FITS))
   ```

**Key constraint:** the `disk-derived N_IDENTITY_LD_NONEMPTY != 12L` verification gate from the user brief is satisfied if and only if the new code reads from `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` and asserts 48L. The previous literal `12L` MUST NOT appear anywhere in the script after this task lands.

**Why disk-derived not hardcoded:** the matched-coverage 48 baseline is the post-k2d full-coverage truth; if k2d is ever re-fired against an updated admissibility set the script will hard-fail at the assertion, forcing TRACK-A-FROZEN-NUMBERS.md and this script to update in lockstep.
  </action>
  <verify>
    <automated>
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript -e 'src <- readLines("src/R/figures/fig2_cs_yield.R"); stopifnot(!any(grepl("N_IDENTITY_LD_NONEMPTY <- 12L", src))); stopifnot(any(grepl("IDENTITY-LD-K2D-FIT-SUMMARY.tsv", src))); stopifnot(any(grepl("N_IDENTITY_LD_NONEMPTY_EXPECTED <- 48L", src))); cat("OK\n")'
    </automated>
  </verify>
  <done>
- Script no longer contains `N_IDENTITY_LD_NONEMPTY <- 12L`.
- Script reads `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` at runtime.
- Locked-scalar block asserts 48L identity-LD non-empty + 95L total identity-LD fits.
- `FOLD_CHANGE_EXPECTED` literal removed; fold-change is computed from disk-derived counts.
- Diagnostic + caption + subtitle reflect matched-coverage 1.06× framing.
  </done>
</task>

<task type="auto">
  <name>Task 2 (W1): Re-render fig2_cs_yield.pdf + fig2_cs_yield.png against the corrected baseline</name>
  <files>docs/manuscript/figures/fig2_cs_yield.pdf, docs/manuscript/figures/fig2_cs_yield.png</files>
  <action>
Run the updated fig2 builder from project root. Working directory MUST be `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis` (not /tmp). Capture stdout to a log file under the planning directory for audit:

```
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig2_cs_yield.R \
  2>&1 | tee .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/fig2_render.log
```

Expected stdout (must all appear):
- `Identity-LD non-empty fits (k2d full-coverage 2026-04-25): 48 / 95`
- `Real-LD non-empty fits (Stage 2 2026-04-22): 51 / 96`
- `Fold change (matched-coverage): 1.062x (or 1.063x — depending on rounding) (51 / 48)`
- `wrote docs/manuscript/figures/fig2_cs_yield.pdf (<bytes>)`
- `wrote docs/manuscript/figures/fig2_cs_yield.png (<bytes>)`

If render fails on the per-ancestry × per-trait diagnostic (`diag` block at L97-L105) — that diagnostic uses `df` (real-LD) only and should be unaffected by the changes. If R complains about missing readr::read_tsv on the new IDENTITY-LD-K2D-FIT-SUMMARY.tsv (whitespace handling for empty `cs_sizes` column) — pass `read_tsv(..., col_types = cols(.default = col_character()))` and coerce `n_CS` to integer explicitly. Do NOT fall back to base R `read.table` — readr handles the bgz-style empty fields better.

Verify the rendered PDF + PNG by file-size sanity check (each should be > 5 KB). The PDF must be cairo_pdf format; the PNG must be 600 dpi at 85 mm × 70 mm.
  </action>
  <verify>
    <automated>
test -s docs/manuscript/figures/fig2_cs_yield.pdf && test -s docs/manuscript/figures/fig2_cs_yield.png && grep -q "Fold change (matched-coverage): 1.0[6-7]" .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/fig2_render.log && grep -q "Identity-LD non-empty fits (k2d full-coverage 2026-04-25): 48 / 95" .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/fig2_render.log && echo OK
    </automated>
  </verify>
  <done>
- fig2_cs_yield.pdf + fig2_cs_yield.png re-rendered.
- Render log captured under planning directory.
- Stdout shows 48/95 identity-LD baseline, 51/96 real-LD, 1.06× fold.
- Both files are non-empty and roughly the same byte-size order as the prior renders.
  </done>
</task>

<task type="auto">
  <name>Task 3 (W1): Update TRACK-A-FROZEN-NUMBERS.md with corrected baseline + preserve 12/96 SUPERSEDED for audit</name>
  <files>.planning/amendments/TRACK-A-FROZEN-NUMBERS.md</files>
  <action>
Add a new "## Stage 2 fine-mapping yield (post-k2d full-coverage 2026-04-25)" subsection BEFORE the existing "## Stage 2 fine-mapping yield (Phase 1 SuSiE-RSS with real 1000G EUR LD)" header at L9. The new subsection records the corrected baseline as the live citation; the legacy 12/96 block is preserved as SUPERSEDED for audit.

Specific edits:

1. **Insert before L9** (i.e., between L7 `---` and L9 `## Stage 2 fine-mapping yield...`):

```markdown
## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE

| Metric | Value |
|---|---|
| Total Stage 2 real-LD fits | 96 |
| Stage 2 non-empty credible sets | **51 / 96 (53.1%)** |
| Total k2d full-coverage identity-LD fits | 95 (single missing cell: `bmi.EUR.APOE_19q13`) |
| k2d identity-LD non-empty credible sets | **48 / 95 (50.5%)** |
| **Matched-coverage fold change** | **51 / 48 = 1.06× yield increase** |
| Status distribution (k2d identity-LD) | 65 ok / 24 too_many_variants / 6 no_variants |
| n_CS distribution (k2d identity-LD) | 47 with 0; 12 with 1; 10 with 2; 5 with 3; 2 with 4; 2 with 5; 2 with 6; 3 with 7; 1 with 8; 11 with 10 |

**Headline framing (manuscript anchor language)**: We tightened the comparator from a partial-coverage Stage 1d narrow-validation baseline (12/96, only 2 of 10 admissible regions had identity-LD fits at the time of freeze) to the k2d full-coverage 2026-04-25 re-fire (48/95, matching the same admissibility set as Stage 2 real-LD). The inflation magnitude shifted from 4.25× to 1.06× under the tightened comparator.

**Sources**: [.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv](./IDENTITY-LD-K2D-FIT-SUMMARY.tsv) (k2d 2026-04-25 fire summary); [results/fine_mapping/finemap_summary.tsv](../../results/fine_mapping/finemap_summary.tsv) (Stage 2 real-LD 2026-04-22 production fire); per-fit JSONs at `results_identity_ld/fine_mapping/susie/*.json` and `results/fine_mapping/susie/*.json`.

**Denominator note**: The k2d identity-LD re-fire enumerated 95 of 96 region × ancestry × trait fits at admissibility. The single missing fit is `bmi.EUR.APOE_19q13` (Stage 2 real-LD status: `non_converged`, n_CS = 6). Headline numerics use 48/95 for identity-LD and 51/96 for real-LD; the fold-change is robust to this 1-cell denominator difference (~1.06× either way).

---
```

2. **Edit the existing block at L21-L23** to mark it as SUPERSEDED:

Replace:
```markdown
Identity-LD baseline (pre-Stage-2): **12 / 96 non-empty credible sets (12.5%)** per prior STATE.md session continuity.

**Headline yield delta**: 12/96 → 51/96 = **4.25× fold increase in non-empty CS yield under real 1000G EUR LD vs identity-LD fallback.**
```

With:
```markdown
~~Identity-LD baseline (pre-Stage-2): **12 / 96 non-empty credible sets (12.5%)** per prior STATE.md session continuity.~~

~~**Headline yield delta**: 12/96 → 51/96 = **4.25× fold increase in non-empty CS yield under real 1000G EUR LD vs identity-LD fallback.**~~

> **SUPERSEDED 2026-04-25** — preserved verbatim for audit traceability. The 12/96 baseline reflected a partial-coverage Stage 1d narrow-validation run (only 2 of 10 admissible regions had identity-LD fits at the time of freeze). The matched-coverage k2d full-coverage 2026-04-25 re-fire produces 48/95 = 50.5% (see top of this document for the live block). The fold-change shifted from 4.25× to ~1.06× under the tightened comparator. Manuscript edits propagated quick-260425-kki.
```

3. **Append a new row to the "Reconciliation log" table** (after the existing 2026-04-23 row at L133-L134):

```markdown
| 2026-04-25 | **Comparator tightened**: post-k2d full-coverage identity-LD re-fire produces 48/95 non-empty CS (50.5%) vs 51/96 real-LD (53.1%) = **1.06× matched-coverage fold change**. Live block added at top of file; legacy 12/96 → 4.25× block marked SUPERSEDED but preserved verbatim for audit. Manuscript track_a_pivot.md (L28, L82, L138, L214, L222, L252, L293) reframed under "we tightened the comparator and the inflation magnitude shifted" anchor language. fig2_cs_yield.R now disk-derives the identity-LD baseline from IDENTITY-LD-K2D-FIT-SUMMARY.tsv. The 95-vs-96 denominator note (missing bmi.EUR.APOE_19q13) is recorded in the live block and propagated to manuscript Methods. | quick-260425-kki — Track A audit-driven figure correction pass. The previously cited 4.25× contrast against a 12/96 baseline reflected a Stage 1d narrow-validation freeze; the post-k2d full-coverage baseline is the appropriate matched-coverage comparator. |
```

**Critical**: do NOT delete the L21-L23 12/96 / 4.25× citations — strike-through and SUPERSEDED block preserves them for audit. The pre-existing draft-discrepancy paragraph at L53 ("1,446 / 861" critique) is unrelated to this edit and stays as-is.
  </action>
  <verify>
    <automated>
grep -q "post-k2d full-coverage identity-LD comparator, 2026-04-25" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md && grep -q "48 / 95 (50.5%)" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md && grep -q "SUPERSEDED 2026-04-25" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md && grep -q "1.06× matched-coverage" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md && grep -q "bmi.EUR.APOE_19q13" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md && echo OK
    </automated>
  </verify>
  <done>
- New live block at top of file records 48/95 → 51/96 ≈ 1.06× matched-coverage fold change.
- Legacy 12/96 + 4.25× block preserved with strike-through + SUPERSEDED 2026-04-25 note.
- Reconciliation log gains 2026-04-25 row.
- Sources cite both IDENTITY-LD-K2D-FIT-SUMMARY.tsv and finemap_summary.tsv.
- 95-vs-96 denominator note names `bmi.EUR.APOE_19q13`.
  </done>
</task>

<task type="auto">
  <name>Task 4 (W1): Reframe all seven 4.25× / 12-of-96 sites in track_a_pivot.md under tightened-comparator language</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
Apply the following seven edits in `docs/manuscript/track_a_pivot.md`. Each edit replaces the live 4.25× / 12 of 96 / 12/96 language with tightened-comparator language anchored on the framing lock. Do these as Edit tool operations (find old string, replace with new); no line-number drift between edits because each replacement is unique substring-anchored.

**Constraint reminder (framing lock):** zero "revision / cleanup / fix-up / error / correction / mistake / we got this wrong / v1 / simplified / placeholder / TBD" tokens. Anchor language: "we tightened the comparator and the inflation magnitude shifted" or near-equivalent. Stage 2 commit-hash anchors at L146/L148 (`6de9a88`, `a6e3214`, `7d54183`, `1635d37`) are PRESERVED.

**Edit 1 — Abstract (L28).** Find the substring:
```
Under real-LD, SuSiE-RSS yielded 51 of 96 (53.1%) non-empty credible sets at admissible regions, compared with 12 of 96 (12.5%) under identity-LD fallback, a 4.25-fold increase in fine-mapping yield.
```
Replace with:
```
Under matched-coverage identity-LD baseline (k2d full-coverage re-fire, 2026-04-25), SuSiE-RSS yielded 48 of 95 (50.5%) non-empty credible sets vs 51 of 96 (53.1%) under real 1000 Genomes Phase 3 EUR LD — a 1.06-fold yield increase. The previously cited 4.25-fold contrast against a 12/96 baseline reflected a partial-coverage Stage 1d narrow-validation run (2 of 10 admissible regions had identity-LD fits at the time of that earlier freeze); the post-k2d full-coverage baseline is the appropriate matched-coverage comparator. The structural credible-set composition difference between identity-LD and real-LD fits (PIP shift, lead-variant rank stability) is reported in a planned supplementary follow-on (TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit).
```

**Edit 2 — Methods §Identity-LD vs Real-LD Comparison (L82).** Find:
```
Under real 1000G EUR LD at admissible regions, SuSiE-RSS yielded **51 of 96 non-empty credible sets** (53%; source `results/fine_mapping/finemap_summary.tsv`). Under identity-LD fallback at the same regions, only 12 of 96 fits (13%) produced non-empty credible sets. The 4.25-fold yield increase demonstrates that identity-LD fallback materially degrades SuSiE-RSS output upstream of any colocalization inference.
```
Replace with:
```
Under real 1000G EUR LD at admissible regions, SuSiE-RSS yielded **51 of 96 non-empty credible sets** (53.1%; source `results/fine_mapping/finemap_summary.tsv`). Under the matched-coverage k2d full-coverage identity-LD comparator (2026-04-25 re-fire; source `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`), 48 of 95 fits (50.5%) produced non-empty credible sets — a 1.06-fold yield increase. (An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline; that freeze covered only 2 of 10 admissible regions on the identity-LD branch and is not the appropriate matched-coverage comparator. We tightened the comparator to k2d full-coverage and the inflation magnitude shifted from 4.25× to 1.06×.) The 95-fit identity-LD denominator differs from the 96-fit real-LD denominator by one cell (`bmi.EUR.APOE_19q13`, real-LD status = `non_converged`, n_CS = 6), absent from the k2d Snakemake manifest input; the fold-change is robust to this 1-cell difference. The interpretive consequence is that the count-level inflation under identity-LD is small at admissible regions; the operative LD inflation pathway at this audit's curated locus set is structural (credible-set composition, PIP shift, and downstream `coloc.susie` PP.H4 reassignment), not raw fit-yield.
```

**Edit 3 — Results §Headline (L138).** Find:
```
**Headline result.** SuSiE-RSS fine-mapping under real 1000 Genomes Phase 3 EUR LD at admissible regions yielded **51 of 96 non-empty credible sets (53.1%)**, compared to **12 of 96 (12.5%) under identity-LD fallback** at the same regions — a 4.25-fold increase in fine-mapping yield (Figure 2).
```
Replace with:
```
**Headline result.** SuSiE-RSS fine-mapping under real 1000 Genomes Phase 3 EUR LD at admissible regions yielded **51 of 96 non-empty credible sets (53.1%)**, compared to **48 of 95 (50.5%) under the matched-coverage k2d full-coverage identity-LD comparator** (2026-04-25 re-fire) — a 1.06-fold yield increase (Figure 2). An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline; that freeze covered only 2 of 10 admissible regions on the identity-LD branch and is not the appropriate matched-coverage comparator. We tightened the comparator and the inflation magnitude shifted: at the count level, identity-LD inflation is modest at this curated locus set; the structural inflation (credible-set composition, PIP shift, downstream `coloc.susie` PP.H4 reassignment) is the load-bearing finding (see §SH2B3 case study, §Pathway reframing).
```

**Edit 4 — Discussion §Strengths (L214).** Find:
```
The 4.25-fold increase in SuSiE-RSS credible-set yield under real-LD relative to identity-LD fallback (51/96 vs 12/96) shows that the inflation mechanism is not subtle: identity-LD materially degrades SuSiE-RSS output upstream of any colocalization inference, and the error propagates downstream into the cross-trait PP.H4 estimates on which drug-repurposing hypotheses and pleiotropy catalogs are built.
```
Replace with:
```
Under the matched-coverage comparator (51/96 real-LD vs 48/95 k2d identity-LD), the count-level credible-set yield differential is modest (~1.06×); however, the structural inflation mechanism — non-convergence of the SuSiE-RSS variational fit at canonical SH2B3 12q24 EUR trait-pairs under real-LD, low ld_overlap_fraction at the one Tier-C signal that survived (FTO_16q12 EUR IRX3/Pancreas, ld_overlap_fraction = 0), and absence of canonical BMI–hypertension / hypertension–stroke pairs from the Stage 2 `coloc.susie` output manifest — is what propagates into the cross-trait PP.H4 reassignment on which drug-repurposing hypotheses and pleiotropy catalogs are built. The earlier 4.25-fold contrast against a 12/96 partial-coverage baseline reflected a Stage 1d narrow-validation comparator; under the tightened k2d full-coverage comparator the operative inflation signal is structural rather than count-level.
```

**Edit 5 — Discussion §Pathway reframing (L222).** Find:
```
All of these signals, and the gene-set claims they supported, depend on the same credible-set outputs shown above to be 4.25-fold more numerous under identity-LD fallback than under matched real-LD.
```
Replace with:
```
All of these signals, and the gene-set claims they supported, depend on credible-set outputs whose composition (PIP distribution, lead-variant rank, credible-set size, convergence behavior) shifts materially between identity-LD and real-LD even when count-level yield is comparable (48/95 identity-LD vs 51/96 real-LD under the matched-coverage k2d full-coverage comparator).
```

**Edit 6 — Conclusions (L252).** Find:
```
**Identity-LD `coloc.abf` fine-mapping systematically inflates cross-trait PP.H4 at curated cardiometabolic loci.** At admissible EUR autosomal regions, SuSiE-RSS + real 1000G EUR LD yielded 4.25-fold more non-empty credible sets than identity-LD fallback (51/96 vs 12/96), and the flagship SH2B3 12q24 EUR trait-pairs that reached PP.H4 = 1.00 under identity-LD at canonical leads (BMI–hypertension and hypertension–stroke, rs3184504 / rs10774625) are absent from the Stage 2 real-LD `coloc.susie` output manifest, consistent with credible-set collapse.
```
Replace with:
```
**Identity-LD `coloc.abf` fine-mapping inflates cross-trait PP.H4 at curated cardiometabolic loci primarily through structural credible-set composition rather than count-level yield.** At admissible EUR autosomal regions under the matched-coverage k2d full-coverage comparator, SuSiE-RSS + real 1000G EUR LD yielded 51/96 non-empty credible sets vs 48/95 under identity-LD (1.06-fold count-level differential), but the flagship SH2B3 12q24 EUR trait-pairs that reached PP.H4 = 1.00 under identity-LD at canonical leads (BMI–hypertension and hypertension–stroke, rs3184504 / rs10774625) are absent from the Stage 2 real-LD `coloc.susie` output manifest — consistent with credible-set composition collapse rather than count collapse on at least one partner trait under real-LD. The structural mechanism (non-convergence at three of five SH2B3 EUR real-LD fits; ld_overlap_fraction = 0 at FTO_16q12 EUR Tier-C; partial-overlap warnings on the surviving "ok" fits) is the load-bearing inflation signal at this audit's curated locus set.
```

**Edit 7 — Figure 2 caption (L293).** Find:
```
**Figure 2.** Credible-set yield under each LD condition. Two-bar comparison of non-empty SuSiE-RSS credible-set counts across the 96 admissible EUR autosomal SuSiE fits: **12 / 96 (12.5%)** under identity-LD fallback vs **51 / 96 (53.1%)** under real 1000 Genomes Phase 3 EUR LD — a **4.25× fold-increase** in fine-mapping yield.
```
Replace with:
```
**Figure 2.** Credible-set yield under each LD condition. Two-bar comparison of non-empty SuSiE-RSS credible-set counts under the matched-coverage k2d full-coverage comparator (2026-04-25 identity-LD re-fire): **48 / 95 (50.5%)** identity-LD vs **51 / 96 (53.1%)** real 1000 Genomes Phase 3 EUR LD — a **1.06× yield increase**. The 95 vs 96 denominator differs by one cell (`bmi.EUR.APOE_19q13`, real-LD status `non_converged` n_CS=6); fold-change is robust to this. An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline (now superseded; see `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` for the audit trail). At the count level, identity-LD inflation is modest at this curated locus set; the structural inflation (credible-set composition, PIP shift, downstream `coloc.susie` PP.H4 reassignment) is the load-bearing finding (see Figure 3 + §SH2B3 case study).
```

**Verification of all seven edits:** after applying, `grep -nE "(4\\.25|12\\s?/\\s?96|12 of 96|4.25-fold)" docs/manuscript/track_a_pivot.md` should return only the lines that explicitly mark 12/96 as SUPERSEDED / earlier freeze (i.e., contextual citations pointing back to the audit trail) — no LIVE headline citations.

**Marker for follow-on tasks:** the abstract edit installs `TODO-COMPOSITION-FOLLOWON` as the marker for the deferred PIP-shift / lead-variant rank composition figure. Do not implement the figure here; that's a separate /gsd-quick task gated on Terminal A LSF compute.
  </action>
  <verify>
    <automated>
grep -c "matched-coverage" docs/manuscript/track_a_pivot.md | awk '$1 >= 6 {exit 0} {exit 1}' && grep -c "1.06" docs/manuscript/track_a_pivot.md | awk '$1 >= 4 {exit 0} {exit 1}' && ! grep -nE "yielded 4\.25-fold|4\.25-fold increase in fine-mapping yield" docs/manuscript/track_a_pivot.md && grep -q "TODO-COMPOSITION-FOLLOWON" docs/manuscript/track_a_pivot.md && grep -q "we tightened the comparator and the inflation magnitude shifted" docs/manuscript/track_a_pivot.md && echo OK
    </automated>
  </verify>
  <done>
- All seven 4.25× / 12 of 96 / 12/96 live citation sites reframed under tightened-comparator language.
- "we tightened the comparator and the inflation magnitude shifted" anchor language present.
- TODO-COMPOSITION-FOLLOWON marker installed in Abstract.
- Stage 2 commit-hash anchors at L146/L148 preserved (verify by `grep -c "6de9a88\\|a6e3214\\|7d54183\\|1635d37"` returning ≥ 4).
- No "revision / cleanup / fix-up / error / correction / mistake" tokens in the edits.
- 95-vs-96 denominator and missing `bmi.EUR.APOE_19q13` cell explicitly noted in Methods edit (Edit 2) and Fig 2 caption (Edit 7).
  </done>
</task>

<task type="auto">
  <name>Task 5 (W1): Single atomic Priority-1 commit — tighten Stage 2 fine-mapping yield comparator</name>
  <files>(commit only — no file edits)</files>
  <action>
Stage the four files modified in T1-T4 + the two re-rendered figure binaries. Single atomic commit.

```
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH" \
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit \
  "docs(quick-260425-kki): tighten Stage 2 fine-mapping yield comparator against k2d full-coverage identity-LD re-fire" \
  --files \
    src/R/figures/fig2_cs_yield.R \
    docs/manuscript/figures/fig2_cs_yield.pdf \
    docs/manuscript/figures/fig2_cs_yield.png \
    .planning/amendments/TRACK-A-FROZEN-NUMBERS.md \
    docs/manuscript/track_a_pivot.md
```

Commit message body (HEREDOC if gsd-tools commit doesn't support body, otherwise let gsd-tools build it; the wrapper accepts the title above and constructs body from staged-file diff stats):

```
Track A audit-driven figure correction pass — Priority 1 (headline-killer).

We tightened the comparator from a partial-coverage Stage 1d narrow-validation
baseline (12/96, 2 of 10 admissible regions on the identity-LD branch) to the
k2d full-coverage 2026-04-25 re-fire (48/95, matching the same admissibility
set as Stage 2 real-LD). The matched-coverage fold change is 51/48 = 1.06×.
The 12/96 baseline is preserved verbatim with SUPERSEDED 2026-04-25 markup
in TRACK-A-FROZEN-NUMBERS.md for audit traceability.

Files:
- src/R/figures/fig2_cs_yield.R now disk-derives the identity-LD baseline
  from .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv; the literal
  N_IDENTITY_LD_NONEMPTY <- 12L is removed; FOLD_CHANGE_EXPECTED literal
  is removed (fold-change computed from disk-derived counts).
- docs/manuscript/figures/fig2_cs_yield.{pdf,png} re-rendered against the
  new disk-truth baseline (cairo_pdf, 600 dpi PNG, 85 mm × 70 mm).
- .planning/amendments/TRACK-A-FROZEN-NUMBERS.md gains a LIVE block at
  top recording 48/95 → 51/96 ≈ 1.06× under matched-coverage; legacy
  12/96 → 4.25× block preserved with SUPERSEDED 2026-04-25 strike-through.
- docs/manuscript/track_a_pivot.md reframes all seven 4.25× / 12-of-96
  live citation sites (Abstract L28, Methods L82, Headline L138,
  Strengths L214, Pathway L222, Conclusions L252, Fig 2 caption L293)
  under the "we tightened the comparator and the inflation magnitude
  shifted" anchor language. TODO-COMPOSITION-FOLLOWON marker installed
  in Abstract for the deferred PIP-shift / lead-variant rank figure.

Sources cited:
- results/fine_mapping/finemap_summary.tsv (Stage 2 real-LD; 51/96 ok)
- .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (k2d 2026-04-25
  full-coverage identity-LD; 48/95 ok)

The 95-vs-96 denominator differs by one cell (bmi.EUR.APOE_19q13, real-LD
status non_converged n_CS=6); fold-change is robust to this 1-cell
difference. Methods edit (Edit 2) names the missing cell explicitly.

This is the Priority 1 (headline-killer) commit per the user brief; W2
(Priority 2 — fig3 + Tier-C data-quality) and W3 (Priority 3 — ghost
numerics + denominator note) follow as separate atomic commits.

Audit context: the user brief references .planning/amendments/AUDIT-REVIEW-2026-04-25.md
as the source of truth for this work, but that file does not exist on disk.
The user's brief is the working spec for this task; the SUMMARY.md records
this for future readers.
```

If gsd-tools commit wrapper does not accept multi-line body via CLI, fall back to:

```
git add src/R/figures/fig2_cs_yield.R \
        docs/manuscript/figures/fig2_cs_yield.pdf \
        docs/manuscript/figures/fig2_cs_yield.png \
        .planning/amendments/TRACK-A-FROZEN-NUMBERS.md \
        docs/manuscript/track_a_pivot.md && \
git commit -m "$(cat <<'EOF'
docs(quick-260425-kki): tighten Stage 2 fine-mapping yield comparator against k2d full-coverage identity-LD re-fire

[body as above]

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

**Critical**: this commit MUST land before W2 starts. T8 (W2 commit) and T9/T11 (W3 commits) are independently revertable; T5 alone makes the manuscript honest if W2/W3 don't land.
  </action>
  <verify>
    <automated>
git log -1 --format=%s | grep -q "tighten Stage 2 fine-mapping yield comparator" && git log -1 --stat --format= | grep -q "fig2_cs_yield.R" && git log -1 --stat --format= | grep -q "TRACK-A-FROZEN-NUMBERS.md" && git log -1 --stat --format= | grep -q "track_a_pivot.md" && echo OK
    </automated>
  </verify>
  <done>
- Single atomic commit landed with all five files (R script + 2 figure binaries + frozen-numbers ledger + manuscript).
- Commit subject contains "tighten Stage 2 fine-mapping yield comparator".
- Commit body contains the framing-lock anchor language.
- `git status` clean for these five paths after commit.
  </done>
</task>

<task type="auto">
  <name>Task 6 (W2): Add ld_overlap_fraction + susie_status + L_saturated sub-table panel to fig3</name>
  <files>src/R/figures/fig3_sh2b3_eur_collapse_forest.R, docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf, docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png</files>
  <action>
Augment `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` to surface three previously-buried data-quality columns as a sub-table panel below the existing forest panels. **Do not modify the existing EXPECTED_ID_CS / EXPECTED_REAL_CS / EXPECTED_REAL_STATUS scalars** — those are disk-truth and feed the existing forest panels. Add the new columns in addition.

**Visual choice (planner-locked, option (a) per the user brief):** sub-table panel BELOW the existing forest, showing trait × ld_overlap_fraction × susie_status × n_CS for both identity-LD and real-LD branches. This is cleaner for reviewer disclosure than annotating the forest with marker symbols.

Specific edits:

1. **Add to header comment block (after existing L43 caveats block):** a new "Data-quality disclosure" subsection explaining that the sub-table surfaces ld_overlap_fraction (real-LD; identity-LD is 0 by definition), susie convergence_status, and L_saturated for each of the 5 EUR traits.

2. **Add data-loader for the disclosure columns.** After the existing JSON read at the existing identity-LD JSON loader (look for `fromJSON(...identity_ld...)` pattern around L150-L200), add a parallel disclosure-columns extractor:

```r
# --- Data-quality disclosure columns (added quick-260425-kki) -----------------
# Surfaces ld_overlap_fraction + convergence_status + L_saturated per trait per
# LD branch. Identity-LD ld_overlap is 0 by definition (identity matrix has no
# real-LD overlap measurement). The real-LD branch carries the load-bearing
# disclosure: even the one "ok" fit (asthma) has ld_overlap_fraction = 0.0385,
# meaning only 3.85% of variants overlapped the 1000G EUR panel.

extract_disclosure <- function(json_path, branch_label) {
  if (!file.exists(json_path)) {
    return(tibble::tibble(
      trait = NA_character_, branch = branch_label,
      ld_overlap_fraction = NA_real_,
      convergence_status = NA_character_,
      L_saturated = NA, niter = NA_integer_, status = NA_character_
    ))
  }
  j <- jsonlite::fromJSON(json_path, simplifyVector = FALSE)
  tibble::tibble(
    trait = j$trait,
    branch = branch_label,
    ld_overlap_fraction = if (!is.null(j$ld_overlap_fraction)) j$ld_overlap_fraction else NA_real_,
    convergence_status = if (!is.null(j$convergence_status)) j$convergence_status else NA_character_,
    L_saturated = if (!is.null(j$L_saturated)) j$L_saturated else NA,
    niter = if (!is.null(j$niter)) j$niter else NA_integer_,
    status = if (!is.null(j$status)) j$status else NA_character_
  )
}

disclosure_real <- purrr::map_dfr(TRAITS_EXPECTED, function(trt) {
  extract_disclosure(
    sprintf("results/fine_mapping/susie/%s.EUR.SH2B3_12q24.json", trt),
    "real-LD"
  )
})
disclosure_id <- purrr::map_dfr(TRAITS_EXPECTED, function(trt) {
  extract_disclosure(
    sprintf("results_identity_ld/fine_mapping/susie/%s.EUR.SH2B3_12q24.json", trt),
    "identity-LD"
  )
})
disclosure <- dplyr::bind_rows(disclosure_real, disclosure_id) |>
  dplyr::mutate(
    trait = factor(trait, levels = TRAITS_EXPECTED),
    branch = factor(branch, levels = c("identity-LD", "real-LD"))
  ) |>
  dplyr::arrange(trait, branch)

# Cross-check: the existing EXPECTED_REAL_STATUS scalars must align with what
# the disclosure JSONs report at convergence_status (on the real-LD branch).
# Hard-fail if drifted (the disk has shifted under us).
status_real <- disclosure |> dplyr::filter(branch == "real-LD") |>
  dplyr::select(trait, convergence_status) |> tibble::deframe()
expected_status_vector <- unlist(EXPECTED_REAL_STATUS)
# Map convergence_status onto the existing status scheme: "converged_primary"
# -> "ok"; "non_converged" -> "non_converged" (or accept either string).
# Lenient compare: only fail if a trait that was expected "ok" shows
# "non_converged" or vice versa.
for (trt in TRAITS_EXPECTED) {
  exp_s <- expected_status_vector[[trt]]
  obs_s <- status_real[[trt]]
  if (!is.null(obs_s) && !is.na(obs_s)) {
    if (exp_s == "ok" && grepl("non_converged", obs_s, fixed = TRUE)) {
      stop(sprintf(
        "fig3: SH2B3 EUR %s real-LD convergence_status drifted from expected 'ok' to '%s'",
        trt, obs_s
      ))
    }
    if (exp_s == "non_converged" && !grepl("non_converged", obs_s, fixed = TRUE)) {
      stop(sprintf(
        "fig3: SH2B3 EUR %s real-LD convergence_status drifted from expected 'non_converged' to '%s'",
        trt, obs_s
      ))
    }
  }
}

message("=== fig3 data-quality disclosure (quick-260425-kki) ===")
print(as.data.frame(disclosure))
```

Add `library(purrr)` and `library(jsonlite)` to the suppressPackageStartupMessages block at the top if not already present (jsonlite is already there per L82; purrr may need to be added — check existing requires).

3. **Build the sub-table panel as a third patchwork plot.** After the existing two panels (forest + side-annotation table) but before the `ggsave` call, add:

```r
# --- Sub-table panel: data-quality disclosure (added quick-260425-kki) -------
disclosure_display <- disclosure |>
  dplyr::mutate(
    ld_of_label = ifelse(
      branch == "identity-LD",
      "0 (identity)",
      sprintf("%.4f", ld_overlap_fraction)
    ),
    status_label = dplyr::case_when(
      grepl("non_converged", convergence_status, fixed = TRUE) ~ "non_converged",
      grepl("converged", convergence_status, fixed = TRUE) ~ "converged",
      TRUE ~ as.character(convergence_status)
    ),
    L_sat_label = ifelse(is.na(L_saturated), "—", as.character(L_saturated))
  ) |>
  dplyr::transmute(
    trait, branch,
    `ld_overlap_fraction` = ld_of_label,
    `susie_status` = status_label,
    `L_saturated` = L_sat_label,
    `niter` = ifelse(is.na(niter), "—", as.character(niter))
  )

# Render as a ggplot text grid (mirrors the existing right-panel table style).
disclosure_long <- disclosure_display |>
  tidyr::pivot_longer(
    cols = c(ld_overlap_fraction, susie_status, L_saturated, niter),
    names_to = "metric", values_to = "value"
  ) |>
  dplyr::mutate(
    metric = factor(metric, levels = c("ld_overlap_fraction", "susie_status",
                                        "L_saturated", "niter")),
    row_lab = sprintf("%s (%s)", trait, branch)
  )

p_disclosure <- ggplot(disclosure_long, aes(x = metric, y = row_lab, label = value)) +
  geom_text(size = 2.5, family = "sans") +
  scale_y_discrete(limits = rev) +
  scale_x_discrete(position = "top") +
  labs(
    x = NULL, y = NULL,
    title = "Per-fit data-quality disclosure (SH2B3 12q24 EUR)",
    subtitle = "ld_overlap_fraction = fraction of fit variants matched to 1000G EUR panel; susie_status from convergence_status; L_saturated = whether L=10 effects ran out of capacity"
  ) +
  theme_minimal(base_size = 8) +
  theme(
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 7, colour = "grey30", lineheight = 1.05),
    axis.text.x = element_text(size = 7.5, face = "bold", colour = "grey20"),
    axis.text.y = element_text(size = 7.5, colour = "grey20"),
    panel.grid.major.y = element_line(colour = "grey92", linewidth = 0.2),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank()
  )
```

4. **Update the patchwork composition.** Locate the existing `final_plot <- (forest_plot | annotation_plot) + plot_layout(...)` (or whatever the existing composition expression is — may differ by exact line). Replace with a three-row composition:

```r
# Stack the disclosure panel below the existing forest+annotation row
final_plot <- ((forest_plot | annotation_plot) / p_disclosure) +
  plot_layout(heights = c(2, 1)) +
  plot_annotation(
    caption = paste0(
      "Sources: results/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json (Stage 2 real-LD, 2026-04-22) +\n",
      "results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json (k2d 2026-04-25 identity-LD).\n",
      "ld_overlap_fraction = 0 by definition for identity-LD branch (identity matrix). Real-LD ld_overlap_fraction\n",
      "is the fraction of fit variants matched to 1000G EUR panel; even the one converged real-LD fit\n",
      "(asthma EUR) has only 3.85% overlap. susie_status from convergence_status; non_converged at three of\n",
      "five real-LD traits at SH2B3 EUR is the structural credible-set composition collapse signal."
    )
  )
```

5. **Update the ggsave call** to allocate more vertical space for the new panel. Current dims are 170 mm × 110 mm; expand to 170 mm × 160 mm (add 50 mm of vertical for the disclosure row).

6. **Render** (do not commit yet — T8 is the W2 commit):
```
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig3_sh2b3_eur_collapse_forest.R \
  2>&1 | tee .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/fig3_render.log
```

Expected stdout (must all appear):
- `=== fig3 data-quality disclosure (quick-260425-kki) ===`
- A printed data.frame with 10 rows (5 traits × 2 branches), real-LD asthma row showing `ld_overlap_fraction = 0.0385`.
- `wrote docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf (<bytes>)`.

If `purrr` isn't installed in the la_multitrait_r env, fall back to `lapply(..., extract_disclosure) |> dplyr::bind_rows()`. If `tidyr::pivot_longer` complains about factor coercion on the `value` column, cast to character first: `mutate(across(c(ld_overlap_fraction, susie_status, L_saturated, niter), as.character))`.

**Constraint:** the existing forest + annotation panels MUST render unchanged (visual diff at the upper portion of the figure). The new sub-table panel is purely additive.
  </action>
  <verify>
    <automated>
test -s docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf && test -s docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png && grep -q "Per-fit data-quality disclosure" src/R/figures/fig3_sh2b3_eur_collapse_forest.R && grep -q "ld_overlap_fraction" src/R/figures/fig3_sh2b3_eur_collapse_forest.R && grep -q "fig3 data-quality disclosure" .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/fig3_render.log && echo OK
    </automated>
  </verify>
  <done>
- fig3 R script gains a disclosure-columns extractor + sub-table panel.
- Existing EXPECTED_ID_CS / EXPECTED_REAL_CS / EXPECTED_REAL_STATUS scalars unchanged.
- Render produces a 3-panel composition (forest | annotation table) / sub-table.
- Real-LD asthma EUR row in disclosure table shows ld_overlap_fraction = 0.0385.
- PDF + PNG re-rendered at 170 mm × 160 mm.
  </done>
</task>

<task type="auto">
  <name>Task 7 (W2): Surface FTO ld_overlap_fraction = 0 + Tier-C data-quality columns in track_a_pivot.md</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
Augment Tier-C reporting in `docs/manuscript/track_a_pivot.md` to surface the per-fit ld_overlap_fraction + susie_status for the 9 Tier-C rows. The single most load-bearing addition is the FTO_16q12 EUR PP.H4 = 0.3099 row's ld_overlap_fraction = 0 finding (currently buried in fig1b R-script header comment).

**Step 1 — enumerate per-fit ld_overlap_fraction for the 9 Tier-C rows.** Run a quick lookup to extract values into a temp file (audit trail). The 9 Tier-C rows are listed in TRACK-A-FROZEN-NUMBERS.md L67-L80. For each row, read the corresponding real-LD SuSiE-RSS JSON and extract `ld_overlap_fraction`, `convergence_status`, `ld_status`. Write the table to `.planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/tierC_disclosure.tsv` for audit:

```
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript -e '
suppressPackageStartupMessages({library(jsonlite); library(dplyr); library(readr)})
tier_c <- tibble::tribble(
  ~region, ~ancestry, ~best_qtl_pph4, ~resolving_gene, ~resolving_tissue,
  "APOL1_22q12", "AFR", 0.0, NA_character_, NA_character_,
  "APOL1_22q12", "EUR", 0.0131, "ENSG00000100342", "Cells_Cultured_fibroblasts",
  "CXADR_F2RL1_6p21", "EUR", 0.0, NA_character_, NA_character_,
  "FTO_16q12", "AFR", 0.0, NA_character_, NA_character_,
  "FTO_16q12", "EUR", 0.3099, "ENSG00000177508 (IRX3)", "Pancreas",
  "MC4R_18q21", "AFR", 0.0, NA_character_, NA_character_,
  "MC4R_18q21", "EUR", 0.0, NA_character_, NA_character_,
  "SH2B3_12q24", "AFR", 0.0, NA_character_, NA_character_,
  "SH2B3_12q24", "EUR", 0.0517, "ENSG00000204842 (ATXN2)", "Adrenal_Gland"
)
# For each Tier-C row, look up the real-LD SuSiE-RSS JSONs across all five
# traits at that region/ancestry and report ld_overlap_fraction range.
extract_ld_quality <- function(region, ancestry) {
  traits <- c("asthma", "bmi", "hypertension", "stroke", "t2d")
  ld_ofs <- numeric(0); ld_sts <- character(0); cs_n <- integer(0)
  for (trt in traits) {
    p <- sprintf("results/fine_mapping/susie/%s.%s.%s.json", trt, ancestry, region)
    if (!file.exists(p)) next
    j <- jsonlite::fromJSON(p, simplifyVector = FALSE)
    if (!is.null(j$ld_overlap_fraction)) {
      ld_ofs <- c(ld_ofs, j$ld_overlap_fraction)
      ld_sts <- c(ld_sts, ifelse(!is.null(j$ld_status), j$ld_status, NA_character_))
      cs_n   <- c(cs_n, ifelse(!is.null(j$credible_sets) && is.list(j$credible_sets), length(j$credible_sets), 0L))
    }
  }
  list(
    ld_of_min = if (length(ld_ofs)) min(ld_ofs) else NA_real_,
    ld_of_max = if (length(ld_ofs)) max(ld_ofs) else NA_real_,
    ld_of_median = if (length(ld_ofs)) median(ld_ofs) else NA_real_,
    n_fits = length(ld_ofs),
    n_with_overlap_zero = sum(ld_ofs == 0, na.rm = TRUE),
    ld_status_unique = paste(unique(ld_sts), collapse = "; ")
  )
}
out <- tier_c |>
  dplyr::rowwise() |>
  dplyr::mutate(q = list(extract_ld_quality(region, ancestry))) |>
  tidyr::unnest_wider(q)
write_tsv(out, ".planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/tierC_disclosure.tsv")
print(as.data.frame(out))
' 2>&1 | tee .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/tierC_disclosure.log
```

The output will show that FTO_16q12 EUR has ld_overlap_fraction values that cluster at 0 across multiple traits with `ld_status = variants_exceed_threshold` — confirming the bombshell hidden in fig1b.R header.

**Step 2 — augment manuscript Tier-C reporting prose.** Locate the SH2B3 case study + Tier C scorecard region in the manuscript (around L162-L200). The existing `**Headline result.**` paragraph at L138 already cites "highest Tier C posterior is **PP.H4 = 0.3099** at *FTO* 16q12 EUR for *IRX3* in GTEx-eQTL Pancreas — below the pre-registered Tier B threshold of 0.5". After this sentence, ADD a new paragraph (insert as a follow-on sentence in the same Headline paragraph or as a NEW paragraph immediately after — planner judgment, prefer NEW paragraph for emphasis):

```
**Tier C real-LD data-quality disclosure.** The single Tier-C signal above PP.H4 = 0.1 (FTO_16q12 EUR IRX3/Pancreas, PP.H4 = 0.3099) was produced by a Stage 2 real-LD SuSiE-RSS fit with `ld_overlap_fraction = 0` and `ld_status = variants_exceed_threshold`; under that LD-status flag the SuSiE-RSS internal solver fell back toward an identity-like internal LD structure at this region, materially weakening the real-LD-survival interpretation of the 0.3099 posterior. The remaining 8 Tier-C rows (3 EUR + 4 AFR + 1 EUR at SH2B3 ATXN2 PP.H4 = 0.0517) span ld_overlap_fraction in the range observed at the corresponding real-LD SuSiE-RSS fits across the five traits at each region; the per-fit disclosure is recorded at `.planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/tierC_disclosure.tsv`. None of the 9 Tier-C rows reached PP.H4 ≥ 0.5; combined with the data-quality disclosure, no Tier-C signal at this run scope is interpretable as a high-confidence cross-trait colocalization claim.
```

**Step 3 — augment the SH2B3 case study Tier-C disclosure.** If there's a separate "SH2B3 case study" or "§Pathway / Tier-C scorecard" section (search for L162 area or a section header containing "SH2B3" or "Tier C"), add ld_overlap_fraction + susie_status columns to the in-text scorecard table or as a new sentence immediately after the scorecard. If the existing scorecard is prose-only (no table), add a sentence:

```
SH2B3 12q24 EUR ld_overlap_fraction at the one converged real-LD fit (asthma) is 0.0385 (3.85% of fit variants matched to the 1000G EUR panel); the four other SH2B3 EUR real-LD traits (bmi, hypertension, stroke, t2d) carry `convergence_status = non_converged`, consistent with a credible-set-composition collapse rather than a count-collapse. See Figure 3 sub-table panel for the per-trait disclosure.
```

**Step 4 — verify that the FTO 0 finding is now load-bearing in the manuscript.** Run:
```
grep -n "ld_overlap_fraction = 0" docs/manuscript/track_a_pivot.md
grep -n "variants_exceed_threshold" docs/manuscript/track_a_pivot.md
grep -n "0.0385" docs/manuscript/track_a_pivot.md
```
All three queries should return at least one hit after this task.
  </action>
  <verify>
    <automated>
test -s .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/tierC_disclosure.tsv && grep -q "ld_overlap_fraction = 0" docs/manuscript/track_a_pivot.md && grep -q "variants_exceed_threshold" docs/manuscript/track_a_pivot.md && grep -q "0.0385" docs/manuscript/track_a_pivot.md && grep -q "Tier C real-LD data-quality disclosure" docs/manuscript/track_a_pivot.md && echo OK
    </automated>
  </verify>
  <done>
- `tierC_disclosure.tsv` audit artifact written under planning directory with per-Tier-C-row ld_overlap_fraction range and ld_status values.
- New "Tier C real-LD data-quality disclosure" paragraph added to manuscript.
- FTO_16q12 EUR ld_overlap_fraction = 0 / ld_status = variants_exceed_threshold finding surfaced in manuscript prose.
- SH2B3 EUR 0.0385 ld_overlap_fraction at asthma surfaced in manuscript prose.
- Tier-C disclosure cross-references Figure 3 sub-table panel from T6.
  </done>
</task>

<task type="auto">
  <name>Task 8 (W2): Single atomic Priority-2 commit — Fig 3 + Tier-C data-quality disclosure</name>
  <files>(commit only — no file edits)</files>
  <action>
Stage the three files modified in T6+T7 and commit:

```
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH" \
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit \
  "docs(quick-260425-kki): surface ld_overlap_fraction + susie_status data-quality on Fig 3 + Tier-C reporting" \
  --files \
    src/R/figures/fig3_sh2b3_eur_collapse_forest.R \
    docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf \
    docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png \
    docs/manuscript/track_a_pivot.md
```

Commit body:
```
Track A audit-driven figure correction pass — Priority 2 (data-quality disclosure).

Surfaces three previously-buried disclosure columns at SH2B3 12q24 EUR and at
the 9 Tier-C rows: ld_overlap_fraction, susie_status (from convergence_status),
and L_saturated. The FTO_16q12 EUR PP.H4 = 0.3099 row's ld_overlap_fraction = 0
finding (previously only in fig1b.R header comment) is now load-bearing in the
manuscript Tier-C disclosure paragraph.

Files:
- src/R/figures/fig3_sh2b3_eur_collapse_forest.R gains a sub-table panel
  below the existing forest+annotation row, showing trait × branch ×
  ld_overlap_fraction × susie_status × L_saturated × niter for the 5
  EUR traits × 2 LD branches (10 rows). Existing EXPECTED_ID_CS /
  EXPECTED_REAL_CS / EXPECTED_REAL_STATUS scalars unchanged.
- docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.{pdf,png}
  re-rendered at 170 mm × 160 mm (50 mm vertical added for sub-table).
- docs/manuscript/track_a_pivot.md gains a new "Tier C real-LD
  data-quality disclosure" paragraph in the Headline section calling
  out FTO_16q12 EUR ld_overlap_fraction = 0 + ld_status =
  variants_exceed_threshold; SH2B3 EUR asthma 3.85% overlap surfaced.
- .planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/
  tierC_disclosure.tsv (audit artifact) records the per-Tier-C-row
  ld_overlap_fraction range across the five real-LD trait JSONs.
```
  </action>
  <verify>
    <automated>
git log -1 --format=%s | grep -q "surface ld_overlap_fraction + susie_status data-quality" && git log -1 --stat --format= | grep -q "fig3_sh2b3_eur_collapse_forest.R" && echo OK
    </automated>
  </verify>
  <done>
- Single atomic commit with 4 files staged.
- Commit subject contains the Priority-2 anchor language.
- `git status` clean for these files after commit.
  </done>
</task>

<task type="auto">
  <name>Task 9 (W3): Purge 1,446 / 861 ghost numerics from .planning/amendments/TRACK-A-PIVOT.md</name>
  <files>.planning/amendments/TRACK-A-PIVOT.md</files>
  <action>
Replace the surviving ghost numerics at the 10 sites identified by orchestrator (L37, L41, L80, L104, L125, L134, L181, L257, L267, L375). The manuscript itself is clean (260424-mqo + k2e edits already purged); this task closes the amendment-file gap.

Disk-truth replacements per `TRACK-A-FROZEN-NUMBERS.md`:
- "1,446 attempted pairwise tests" → "1,302 attempted analyses (28 trait-pair `coloc.susie` + 1,274 QTL-coloc)"
- "861 computational failures" → either "1,005 `too_few_snps` failures (78.9% of 1,274 QTL-coloc attempts)" or "the QTL-coloc and trait-pair failure modes" depending on context.
- "861 errors" → similar context-driven replacement.
- "861-error" (compound) → "QTL-coloc failure-mode" or "harmonization-pipeline-diagnostics".

Specific replacements (find string → replace string), apply in order; each is unique-substring-anchored:

**L37 (Section 3 abstract draft)** — Find:
```
1,446 attempted pairwise tests included 861 computational failures traceable to harmonization-pipeline edge cases in the asthma cohorts rather than biological independence.
```
Replace with:
```
1,302 attempted analyses (28 trait-pair `coloc.susie` + 1,274 QTL-coloc) included 1,005 `too_few_snps` failures (78.9% of QTL-coloc) traceable to a harmonized-TSV vs Phase 1 SuSiE-fit variant-ID mismatch that was structurally fixed mid-Stage-2 and may incompletely propagate to all source × tissue × gene combinations.
```

**L41 (parenthetical commentary on the abstract)** — Find:
```
reframes the 861 failures honestly
```
Replace with:
```
reframes the 1,005 too_few_snps + 28 trait-pair failure modes honestly per disk-truth
```

**L80 (Methods §Data Harmonization edit note)** — Find:
```
**Add**: a sentence foreshadowing the 861 pipeline failures and their diagnosis as harmonization edge cases (forward pointer to new 4.12 subsection).
```
Replace with:
```
**Add**: a sentence foreshadowing the 1,005 `too_few_snps` failures (78.9% of 1,274 QTL-coloc attempts) and 28 trait-pair coloc.susie attempts, diagnosing the dominant failure mode as a harmonized-TSV vs SuSiE-fit variant-ID mismatch (forward pointer to new 4.12 subsection).
```

**L104 (Methods §Pipeline Diagnostics edit)** — Find:
```
**Add.** ~150 words. Describe the 861 `COLOC_ERROR` failures as arising from (a) insufficient variant overlap after harmonization, (b) ill-conditioned LD matrices at AFR loci with low panel coverage, (c) `coloc.susie` refusing to converge on SuSiE fits with no non-empty credible sets. Present the per-trait-pair breakdown (new Table 3 / Table S6, see Section 5). Explicitly *withdraw* the earlier "biology not technical" interpretation. This subsection is the section reviewers will look for.
```
Replace with:
```
**Add.** ~150 words. Describe the 1,005 `too_few_snps` QTL-coloc failures (78.9% of 1,274 attempts) and 28 empty trait-pair coloc.susie outputs as arising from (a) a harmonized-TSV vs Phase 1 SuSiE-fit variant-ID mismatch that was structurally fixed mid-Stage-2 and may incompletely propagate to all source × tissue × gene combinations, (b) ill-conditioned LD matrices at AFR loci with low panel coverage, (c) `coloc.susie` refusing to converge on SuSiE fits with no non-empty credible sets. Present the per-trait-pair breakdown (new Table 3 / Table S6, see Section 5). Explicitly *withdraw* the earlier "biology not technical" interpretation. This subsection is the section reviewers will look for.
```

**L125 (Results §Headline rewrite spec)** — Find:
```
Replace the "28 high-confidence signals" headline with "51/96 non-empty credible sets under real 1000G EUR LD at admissible regions, vs 12/96 under identity-LD fallback (4.25× yield increase)." Keep the 585 pairwise count but reframe as "baseline identity-LD reproduction". Replace the 861-error "biology not technical" paragraph with a one-sentence forward pointer to the new Harmonization Diagnostics Results subsection (4.16.x below).
```
Replace with:
```
Replace the "28 high-confidence signals" headline with "51/96 non-empty credible sets under real 1000G EUR LD vs 48/95 under matched-coverage k2d full-coverage identity-LD (1.06× yield increase under matched-coverage comparator; see TRACK-A-FROZEN-NUMBERS.md for the post-2026-04-25 audit trail and the SUPERSEDED Stage 1d 12/96 → 4.25× freeze)." Keep the 585 pairwise count but reframe as "baseline identity-LD reproduction". Replace the prior "biology not technical" paragraph with a one-sentence forward pointer to the new Harmonization Diagnostics Results subsection (4.16.x below).
```

**L134 (NEW Results subsection: Harmonization-Pipeline Diagnostics edit spec)** — Find:
```
**NEW Results subsection: "Harmonization-Pipeline Diagnostics"** (insert before Cross-Ancestry Comparison): *Add.* ~200 words. Per-trait-pair breakdown of the 861 failures: how many from insufficient overlap, how many from ill-conditioned LD, how many from SuSiE non-convergence. Explicitly withdraw the prior "biology" interpretation. Reference new Table 4 / Table S6 (see Section 5).
```
Replace with:
```
**NEW Results subsection: "Harmonization-Pipeline Diagnostics"** (insert before Cross-Ancestry Comparison): *Add.* ~200 words. Per-trait-pair breakdown of the 1,005 `too_few_snps` QTL-coloc failures (78.9% of 1,274 attempts) and the 28 empty trait-pair coloc.susie outputs: how many from insufficient overlap (variant-ID mismatch), how many from ill-conditioned LD, how many from SuSiE non-convergence. Explicitly withdraw the prior "biology" interpretation. Reference new Table 4 / Table S6 (see Section 5).
```

**L181 (Table 4 spec)** — Find:
```
**Content**: rows = trait pairs; columns = n_attempted, n_failed, n_failed_insufficient_overlap, n_failed_illconditioned_LD, n_failed_SuSiE_nonconvergence, n_failed_other. Replaces the 861-error hand-wave.
```
Replace with:
```
**Content**: rows = trait pairs; columns = n_attempted, n_failed, n_failed_insufficient_overlap, n_failed_illconditioned_LD, n_failed_SuSiE_nonconvergence, n_failed_other. Replaces the prior "biology not technical" hand-wave on the 1,005 too_few_snps + 28 trait-pair failure-mode totals.
```

**L257 (Section 5: Findings to remove)** — Find:
```
**"861 errors = biology not technical"** (lines 92, 118, 220). Remove entirely. Replace with honest diagnostic (Section 4.12, Table 4). Reviewers will flag the original interpretation as pipeline whitewashing.
```
Replace with:
```
**"errors = biology not technical"** (lines 92, 118, 220 of the prior draft). Remove entirely. Replace with honest diagnostic (Section 4.12, Table 4) of the 1,005 too_few_snps + 28 trait-pair failure modes per disk. Reviewers will flag the original interpretation as pipeline whitewashing.
```

**L267 (Section 4.12 cross-reference)** — Find:
```
**Section 4.12 — Harmonization-Pipeline Diagnostics** (Methods + Results). Honest accounting of the 861 failures, per-trait-pair breakdown, withdrawal of the prior "biology" interpretation.
```
Replace with:
```
**Section 4.12 — Harmonization-Pipeline Diagnostics** (Methods + Results). Honest accounting of the 1,005 too_few_snps QTL-coloc + 28 empty trait-pair coloc.susie failure modes, per-trait-pair breakdown, withdrawal of the prior "biology" interpretation.
```

**L375 (Risk register row)** — Find:
```
| 861-error reviewer pushback ("show us the logs") | Medium | Medium | Table 4 + Figure S6 provide per-trait-pair failure breakdown with 2–3 annotated failure cases; additional logs made available on request via the OSF project. |
```
Replace with:
```
| Failure-mode reviewer pushback ("show us the logs" on the 1,005 too_few_snps + 28 empty trait-pair outputs) | Medium | Medium | Table 4 + Figure S6 provide per-trait-pair failure breakdown with 2–3 annotated failure cases; additional logs made available on request via the OSF project. |
```

After applying, verify zero ghost tokens remain:
```
grep -nE "1,446|1446|861" .planning/amendments/TRACK-A-PIVOT.md
```
should return zero hits.

Then commit (atomic per priority — independently revertable from W1+W2):
```
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH" \
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit \
  "docs(quick-260425-kki): purge 1,446 / 861 ghost numerics from TRACK-A-PIVOT.md amendment" \
  --files .planning/amendments/TRACK-A-PIVOT.md
```

Commit body:
```
Track A audit-driven figure correction pass — Priority 3(f).

Replaces 10 surviving "1,446" / "861" ghost-number citations in
.planning/amendments/TRACK-A-PIVOT.md (L37, L41, L80, L104, L125, L134,
L181, L257, L267, L375) with disk-truth Stage 2 numerics per
TRACK-A-FROZEN-NUMBERS.md: 1,302 attempted analyses (28 trait-pair
coloc.susie + 1,274 QTL-coloc), 1,005 too_few_snps QTL-coloc failures
(78.9% of 1,274), 28 empty trait-pair coloc.susie outputs.

The L125 site additionally absorbs the W1 comparator tightening:
"51/96 vs 12/96 (4.25× yield increase)" → "51/96 vs 48/95 under
matched-coverage k2d full-coverage identity-LD (1.06×)".

Manuscript itself was already clean of these ghosts (260424-mqo +
k2e edits, per TRACK-A-FROZEN-NUMBERS.md reconciliation log
2026-04-23). This commit closes the amendment-file gap.
```
  </action>
  <verify>
    <automated>
! grep -nE "1,446|1446" .planning/amendments/TRACK-A-PIVOT.md && ! grep -nE "(^| )861( |\$)|861-error|861 errors|861 failures|861 computational" .planning/amendments/TRACK-A-PIVOT.md && git log -1 --format=%s | grep -q "purge 1,446 / 861" && echo OK
    </automated>
  </verify>
  <done>
- Zero "1,446" / "1446" tokens remain in TRACK-A-PIVOT.md.
- Zero "861" tokens remain as live numeric citations (the only allowed remaining 861-substring matches would be unrelated context like dates or commit hashes — verify by manual scan if grep flags any).
- Disk-truth replacements at all 10 sites.
- L125 site absorbs the W1 comparator tightening.
- Single atomic commit with the Priority 3(f) message.
  </done>
</task>

<task type="auto">
  <name>Task 10 (W3) — DEFERRED: HLA double-classification (Priority 3(g))</name>
  <files>(none — DEFERRED to follow-on)</files>
  <action>
**This task is DEFERRED.** Do NOT modify HLA framing in the manuscript.

The user brief Priority 3(g) instruction "(g) HLA double-classification — pick fallback OR negative-control, remove from the other" reflects an audit-author judgment that the orchestrator does not have full context on. The orchestrator's read is:

> HLA is genuinely BOTH (a) admissibility-rejected (falls back to identity-LD because the MHC region is too complex for the autosomal 1000G panel) AND (b) a pre-registered negative control (used for ancestry stratification calibration). These are NOT mutually exclusive — admissibility status is about which LD branch a region uses, while negative-control status is about whether the region is expected to produce a true positive.

The audit file (`.planning/amendments/AUDIT-REVIEW-2026-04-25.md`) does not exist on disk to confirm the audit-author's intent. Making this call without that document risks introducing a framing inconsistency that the audit author did not request.

**Action: SUMMARY.md must record this as an open follow-on with a structured question for the user.** Do NOT modify any of the seven HLA mention sites in the manuscript (L80, L102, L138, L186, L208, L238, L242) in this task.

The structured question to record in SUMMARY.md:

> **HLA framing question (deferred from quick-260425-kki Priority 3(g)):** the user brief instructs "pick fallback OR negative-control, remove from the other". The manuscript currently frames HLA as both (a) admissibility-rejected (falls back to identity-LD; L80, L208, L242) and (b) a pre-registered negative control (L102, L138, L186, L238). The orchestrator's read is that these are NOT mutually exclusive — admissibility is about LD branch, negative-control is about expected-truth status. The audit document `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` is missing from disk; without it the audit author's intended single-classification is unknown. **Question for user:** which framing should HLA carry? Options: (1) keep both (status quo, orchestrator's read); (2) HLA is fallback only, drop the negative-control framing; (3) HLA is negative-control only, drop the fallback framing. Recommended path: schedule a separate /gsd-quick task after user direction is received.
  </action>
  <verify>
    <automated>
echo "DEFERRED — task marker only; no automated verification possible without audit-author judgment. SUMMARY.md will record the deferred question."
    </automated>
  </verify>
  <done>
- HLA framing in manuscript UNCHANGED.
- SUMMARY.md records the deferred question with the three-option decision matrix.
- No commit produced for this task.
  </done>
</task>

<task type="auto">
  <name>Task 11 (W3): Document 95-vs-96 denominator + missing bmi.EUR.APOE_19q13 fit (Priority 3(h))</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
The 95-vs-96 denominator note was already partially installed in T4 Edit 2 (Methods) and T4 Edit 7 (Fig 2 caption). This task adds an explicit Methods sentence at the admissibility paragraph (around L80) for full reviewer-discoverability, ensuring the reconciliation is not buried in the Identity-LD Comparison sub-section.

**Step 1 — locate the admissibility paragraph.** Grep for "AFR regions, the HLA region (6p21" — this anchors L80 in the manuscript Methods §Admissibility. Verify line:
```
grep -n "AFR regions, the HLA region (6p21" docs/manuscript/track_a_pivot.md
```

**Step 2 — append the denominator note.** After the existing admissibility paragraph (look for the sentence ending "...candid limitation"), ADD a new sentence:

Find the substring:
```
AFR regions, the HLA region (6p21, complex MHC architecture), and BMI_Xq24 (chromosome X, not covered by the autosomal LDSC-delivered 1000G panel) fall back to identity-LD fallback and are reported separately as a candid limitation
```
(the exact phrasing may differ slightly — use whatever substring uniquely identifies the admissibility paragraph at L80; if needed, replace just the closing sentence of that paragraph)

Append immediately after that sentence:
```
The k2d identity-LD re-fire (2026-04-25) enumerated 95 of 96 region × ancestry × trait fits at admissibility; the single missing fit is `bmi.EUR.APOE_19q13` (Stage 2 real-LD status: `non_converged`, n_CS = 6), absent from the k2d Snakemake manifest input. Headline contrasts therefore use 48 of 95 (50.5%) for identity-LD and 51 of 96 (53.1%) for real-LD; the matched-coverage 1.06-fold ratio is robust to this 1-cell denominator difference (50.5% → 53.1% under either denominator choice).
```

**Step 3 — verify there are now THREE places where the 95/96 reconciliation appears** (Methods §Identity-LD Comparison from T4 Edit 2; this Methods §Admissibility addition; Fig 2 caption from T4 Edit 7):
```
grep -n "95 of 96 region.*ancestry.*trait fits" docs/manuscript/track_a_pivot.md
grep -n "bmi.EUR.APOE_19q13" docs/manuscript/track_a_pivot.md
grep -n "1-cell denominator" docs/manuscript/track_a_pivot.md
```
The last grep should return at least 2 hits (Methods §Identity-LD Comparison + this new admissibility addition).

**Step 4 — commit (atomic per priority):**
```
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH" \
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit \
  "docs(quick-260425-kki): document 95 vs 96 denominator and missing bmi.EUR.APOE_19q13 fit" \
  --files docs/manuscript/track_a_pivot.md
```

Commit body:
```
Track A audit-driven figure correction pass — Priority 3(h).

Adds an explicit Methods §Admissibility sentence noting that the k2d
identity-LD re-fire (2026-04-25) enumerated 95 of 96 region × ancestry
× trait fits, with the single missing cell being bmi.EUR.APOE_19q13
(real-LD status: non_converged, n_CS=6). Headline contrasts use 48/95
identity-LD vs 51/96 real-LD; the matched-coverage 1.06× fold-change
is robust to this 1-cell denominator difference.

The reconciliation note now appears in three sites (Methods §Identity-LD
Comparison, this Methods §Admissibility addition, and the Figure 2
caption) for reviewer-discoverability.
```
  </action>
  <verify>
    <automated>
grep -q "95 of 96 region" docs/manuscript/track_a_pivot.md && grep -q "bmi.EUR.APOE_19q13" docs/manuscript/track_a_pivot.md && grep -c "1-cell denominator" docs/manuscript/track_a_pivot.md | awk '$1 >= 1 {exit 0} {exit 1}' && git log -1 --format=%s | grep -q "document 95 vs 96 denominator" && echo OK
    </automated>
  </verify>
  <done>
- Methods §Admissibility now contains the 95-vs-96 denominator reconciliation sentence.
- `bmi.EUR.APOE_19q13` named explicitly with its real-LD status (non_converged, n_CS=6).
- Reconciliation appears in 3 sites of the manuscript.
- Atomic commit with the Priority 3(h) message.
  </done>
</task>

</tasks>

<verification>
**Phase-level verification gates** (must all pass after T11 lands):

1. **Headline correction landed:** `grep -nE "yielded 4\\.25-fold|4\\.25-fold increase in fine-mapping yield" docs/manuscript/track_a_pivot.md` returns zero hits (i.e., no LIVE 4.25× citations remain; only the SUPERSEDED reference in TRACK-A-FROZEN-NUMBERS.md).

2. **fig2 disk-derived:** `grep -q "N_IDENTITY_LD_NONEMPTY <- 12L" src/R/figures/fig2_cs_yield.R` returns false (the literal is gone), AND `grep -q "IDENTITY-LD-K2D-FIT-SUMMARY.tsv" src/R/figures/fig2_cs_yield.R` returns true.

3. **fig2 re-rendered:** `test -s docs/manuscript/figures/fig2_cs_yield.pdf && test -s docs/manuscript/figures/fig2_cs_yield.png`.

4. **fig3 sub-table panel:** `grep -q "Per-fit data-quality disclosure" src/R/figures/fig3_sh2b3_eur_collapse_forest.R` returns true.

5. **Tier-C FTO bombshell surfaced:** `grep -q "ld_overlap_fraction = 0" docs/manuscript/track_a_pivot.md && grep -q "variants_exceed_threshold" docs/manuscript/track_a_pivot.md` returns true.

6. **TRACK-A-FROZEN-NUMBERS.md updated:** `grep -q "post-k2d full-coverage identity-LD comparator" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md && grep -q "SUPERSEDED 2026-04-25" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md`.

7. **Ghost numerics purged from amendment:** `grep -cE "1,446|1446" .planning/amendments/TRACK-A-PIVOT.md` returns 0.

8. **95-vs-96 denominator documented:** `grep -q "bmi.EUR.APOE_19q13" docs/manuscript/track_a_pivot.md`.

9. **Atomic commit count:** `git log --oneline | grep "quick-260425-kki" | wc -l` returns 4 (T5 + T8 + T9 + T11; T10 deferred).

10. **Framing-lock zero-tokens check:** `git log --since="now -2 hours" --pretty=format:%B | grep -ciE "(revision|cleanup|fix-up|fixup|mistake|we got this wrong|placeholder|TBD|simplified version|v1)"` returns 0.
</verification>

<success_criteria>
The phase is complete when:
- All four atomic commits land in order (T5 W1 → T8 W2 → T9 W3 → T11 W3).
- All 10 phase-level verification gates pass.
- SUMMARY.md records: (a) the missing AUDIT-REVIEW-2026-04-25.md note; (b) the deferred HLA double-classification question with three-option decision matrix; (c) the upstream-compute-gated follow-ons (SH2B3 EUR L=20 re-fit, canonical SH2B3 trait-pair coloc.susie, PIP-shift / lead-variant rank composition figure with TODO-COMPOSITION-FOLLOWON marker, pathway-enrichment recompute on corrected signal set, submission decision — 1.06× framing may shift target venue from Genome Medicine → Bioinformatics Applications Note).
- No "revision / cleanup / fix-up / error / correction / mistake / we got this wrong / placeholder / v1 / simplified" tokens in any commit message or manuscript edit.
- "we tightened the comparator and the inflation magnitude shifted" anchor language appears in T4 manuscript edits (Edit 2 and Edit 3 explicitly cite this near-verbatim).
- The Priority 1 commit (T5) is independently revertable; if W2 (T8) and W3 (T9, T11) do not land, T5 alone makes the manuscript honest.
</success_criteria>

<output>
After execution, create `.planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md` covering:

1. **Disk-truth shift:** 12/96 → 4.25× SUPERSEDED; live baseline 48/95 → 51/96 ≈ 1.06× under matched-coverage k2d full-coverage comparator. Anchor language: "we tightened the comparator and the inflation magnitude shifted."

2. **Atomic commits landed:** four commits (T5, T8, T9, T11) referenced by hash + subject. T10 deferred — record HLA double-classification question with three-option decision matrix.

3. **Missing AUDIT-REVIEW-2026-04-25.md:** the user brief's "source of truth" file does not exist on disk; the user brief itself was the working spec.

4. **Deferred upstream-compute-gated follow-ons** (out-of-scope per user brief constraints):
   - SH2B3 EUR L=20 re-fit on BMI/HTN/stroke (Terminal A LSF compute slot)
   - SH2B3 canonical trait-pair coloc.susie runs (BMI×HTN, HTN×stroke)
   - PIP-shift / lead-variant rank composition analysis (TODO-COMPOSITION-FOLLOWON marker installed in Abstract; gated on the L=20 re-fit)
   - Pathway-enrichment recomputation on the corrected signal set
   - Submission venue decision (1.06× framing may shift target from *Genome Medicine* → *Bioinformatics* Applications Note; this is a /gsd-discuss-phase decision, not implementation)
   - HLA double-classification (Priority 3(g)) — record the deferred question; await user direction.

5. **Verification gates:** which of the 10 phase-level gates passed; any that didn't and why.

6. **Files modified:** the 9 files listed in frontmatter `files_modified`, with one-line each on what changed.

7. **STATE.md row:** propose the new STATE.md `last_activity` row and `stopped_at` value to surface the kki commit cluster, ready for paste at next /gsd-state checkpoint.
</output>
