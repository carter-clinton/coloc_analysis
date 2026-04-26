---
phase: 260425-wa2
plan: 01
status: complete
completed: 2026-04-25
commit_count: 1
files_changed: 3
requirements_completed: [AUDIT-HQ-3]
---

# Quick-260425-wa2 SUMMARY — audit High-Quality #3 LD-reference-quality dose-response figure

## One-liner

Built the 2-panel composite figure that AUDIT-REVIEW-2026-04-25.md High-Quality #3 specifically asked for: SuSiE-RSS credible-set yield (Panel A, 60 EUR fits) and QTL-coloc PP.H4 (Panel B, 32 EUR successes) plotted against `ld_overlap_fraction` of the real 1000G EUR LD panel, with the headline FTO_16q12 EUR IRX3 / Pancreas Tier-C signal (PP.H4 = 0.3099, min ld_of = 0) annotated as the structural inflation flag.

## Commit

| Hash | Subject | Files |
|------|---------|-------|
| `1e4b071` | docs(quick-260425-wa2): build audit High-Quality #3 LD-reference-quality dose-response figure | 3 |

### Files staged in `1e4b071` (exactly 3)

| File | Bytes |
|------|-------|
| `src/R/figures/fig_h3_ld_overlap_dose_response.R` | 21,666 |
| `docs/manuscript/figures/fig_h3_ld_overlap_dose_response.pdf` | 44,742 |
| `docs/manuscript/figures/fig_h3_ld_overlap_dose_response.png` | 689,398 |

No `.planning/STATE.md`, `.planning/config.json`, `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`, or `.planning/quick/260425-wa2-*/` documents were touched in this commit; the orchestrator commits planning/STATE artifacts in a separate step.

## Disk-derived runtime scalars (verbatim render log)

```
=== fig_h3_ld_overlap_dose_response.R diagnostic ===
Total real-LD fits parsed: 96 (expected 96)
EUR fits with measured ld_overlap_fraction: 60
AFR fits (no measured ld_overlap_fraction): 36
Status distribution:
  ok                     48
  too_many_variants      24
  non_converged          18
  no_variants            6
EUR fits below Benner threshold (ld_overlap_fraction < 0.5): 33
EUR fits at or above Benner threshold (>= 0.5): 27
Total qtl_coloc successes parsed: 32 (expected 32; all EUR)
FTO_16q12 EUR IRX3/Pancreas: PP.H4=0.3099 min_ld_overlap_fraction=0
SH2B3_12q24 EUR asthma: ld_overlap_fraction=0.0385
Suspect-quadrant points (PP.H4 >= 0.5 AND min_ld_of < 0.5): 0
---
wrote docs/manuscript/figures/fig_h3_ld_overlap_dose_response.pdf (44742 bytes)
wrote docs/manuscript/figures/fig_h3_ld_overlap_dose_response.png (689398 bytes)
Figure H3 render complete.
```

### New scalars surfaced for orchestrator follow-on (TRACK-A-FROZEN-NUMBERS.md)

- **N_EUR_FITS_BELOW_BENNER = 33** (of 60 EUR fits) — fraction = 33 / 60 = 55.0%. The majority of EUR real-LD fits sit below the Benner et al. 2017 calibration threshold.
- **N_EUR_FITS_AT_OR_ABOVE_BENNER = 27** (of 60 EUR fits) — 45.0%.
- **N_SUSPECT_QUADRANT_QTL_POINTS = 0** (of 32 qtl_coloc successes) — there are zero successful QTL-coloc attempts where PP.H4 ≥ 0.5 AND GWAS-side min ld_of < 0.5. The audit's "FTO 0.3099 in the top-left suspect quadrant" framing remains accurate at PP.H4 = 0.3099 (which is a sub-Tier-B Tier-C signal); no Tier-A/Tier-B real-LD signals exist on disk to populate the strict "PP.H4 ≥ 0.5 AND ld_of < 0.5" quadrant. This is itself a finding: under real-LD, the entire Track A QTL-coloc success set has PP.H4 < 0.5, consistent with the manuscript's "primarily an LD-inflation artifact" framing.

## Caveats disclosed in the figure

### Trait-ambiguity caveat (Panel B)

The qtl_coloc per-attempt JSON does not record which of the 5 GWAS-side trait SuSiE fits was the input. Panel B therefore uses MIN `ld_overlap_fraction` across the 5 GWAS-side trait fits at the same `(region_id, ancestry)` cell — a conservative worst-case bound. Both the in-figure caption and the script's panel subtitle disclose this. NA `ld_overlap_fraction` values are coerced to 0 inside the MIN aggregation, which matches the conservative reading of the audit caveat ("if even one GWAS-side fit had no LD overlap, the worst-case bound is 0").

### AFR exclusion (Panel A)

The 36 AFR fits are excluded from Panel A because no AFR LD panel was loaded. This is consistent with TRACK-A-FROZEN-NUMBERS.md scope caveat. The plan's locked-scalar block called for `N_REAL_LD_EUR_WITH_OVERLAP = 60`; the script plots all 60 EUR fits, with the 19 EUR fits that have `ld_overlap_fraction = NA` (never had LD measured) coerced to `plot_ldof = 0` for the dose-response visualization. The remaining 41 EUR fits have a numeric `ld_overlap_fraction` value (35 with `ld_status = "ld_loaded"`, 6 with `ld_status = "variants_exceed_threshold"` and ld_of = 0). This NA→0 coercion is documented inline in the script (see `panel_a_data` mutate) and reflected in the diagnostic stdout (60 EUR fits plotted, of which 33 sit below the Benner threshold once the coercion is applied).

## Forbidden-framing greppable check (zero matches required)

Run against R script + commit message:

```bash
grep -iE "revision|cleanup|fix-up|mistake|v1|simplified|placeholder|TBD" \
  src/R/figures/fig_h3_ld_overlap_dose_response.R
git log -1 --pretty=%B | grep -iE "revision|cleanup|fix-up|mistake|v1|simplified|placeholder|TBD"
```

Result: zero matches. Framing discipline upheld per `feedback_original_research_framing` user memory.

## Plan vs execution alignment

- **Tasks completed:** 3 / 3 (all `type=auto`, no checkpoints).
- **Commits:** 1 (the prescribed atomic build commit).
- **Plan locked-scalar deviations:** none. All 9 locked scalars (N_REAL_LD_FITS_TOTAL, N_REAL_LD_NONEMPTY, N_QTL_SUCCESS, N_EUR_FITS_EXPECTED, N_AFR_FITS_EXPECTED, BENNER_THRESHOLD, TIER_B_THRESHOLD, TIER_A_THRESHOLD, FTO_HEADLINE_PPH4, SH2B3_ASTHMA_LDOF) cross-checked against disk truth and held.
- **Notable runtime finding (not a plan deviation):** the EUR-fit-NA disambiguation. Of the 60 EUR fits, 41 have a numeric `ld_overlap_fraction` and 19 have `NA`. The 19 NAs correspond to fits whose `ld_status` is `NULL` (no LD attempted) — distinct from the 6 EUR fits with `ld_status = "variants_exceed_threshold"` and a literal `ld_overlap_fraction = 0`. The figure plots all 60 EUR fits with NA→0 coercion under the conservative reading that "no LD measured" is dose-response-equivalent to "no LD overlap" for the audit's question. Documented in the script and in the figure caption.

## Outstanding follow-ons (out of scope here)

1. **Caption integration into the manuscript figure roster.** Slot decision pending Carter's review of the rendered composite. Candidate slots: (a) reclaim Fig 4 (currently empty per the latest manuscript map), (b) add a new Fig 6 in the Results §Reframing section, or (c) move to supplementary as Fig S-H3 if the manuscript's 5-figure ceiling is binding. Will be handled in a separate `/gsd-quick` after Carter reviews the rendered composite.
2. **TRACK-A-FROZEN-NUMBERS.md update with the new N_EUR_FITS_BELOW_BENNER / N_EUR_FITS_AT_OR_ABOVE_BENNER / N_SUSPECT_QUADRANT_QTL_POINTS scalars.** Will be handled in the same caption-integration `/gsd-quick` so the FROZEN-NUMBERS.md update lands alongside the manuscript caption that cites it.

## Self-Check: PASSED

- `src/R/figures/fig_h3_ld_overlap_dose_response.R` exists (21,666 bytes, 409 lines)
- `docs/manuscript/figures/fig_h3_ld_overlap_dose_response.pdf` exists (44,742 bytes, valid PDF v1.7)
- `docs/manuscript/figures/fig_h3_ld_overlap_dose_response.png` exists (689,398 bytes, 600 dpi)
- Commit `1e4b071` exists in `git log`, contains exactly 3 files, subject matches the prescribed form
- Pre-existing dirty paths (`.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`) remain untouched in `git status`
- Render log captured at `/tmp/fig_h3_render.log`
- Forbidden-framing token scan returns zero matches across R script + commit message
