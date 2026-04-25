---
phase: quick-260425-kki
plan: 01
subsystem: docs/manuscript + planning/amendments + src/R/figures
tags: [track-a, manuscript, comparator-tightening, figure-correction, data-quality-disclosure, framing-lock]
dependency-graph:
  requires:
    - .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (k2d 2026-04-25 fire summary)
    - results/fine_mapping/finemap_summary.tsv (Stage 2 real-LD)
    - results/fine_mapping/susie/{trait}.EUR.{region}.json (per-fit JSONs)
    - results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json
  provides:
    - matched-coverage 48/95 vs 51/96 = 1.06x baseline (live)
    - fig2_cs_yield disk-derived render
    - fig3 disclosure sub-table panel
    - Tier-C ld_overlap_fraction = 0 surface at FTO_16q12 EUR
    - 95-vs-96 denominator audit trail
  affects:
    - docs/manuscript/track_a_pivot.md (8 substantive sites)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (live block + reconciliation row)
    - .planning/amendments/TRACK-A-PIVOT.md (10 ghost-numeric purges)
tech-stack:
  added:
    - tibble + jsonlite + tidyr in fig3 disclosure extractor
  patterns:
    - disk-derived assertions (fig2 stops if k2d count drifts from 48L; lockstep
      with TRACK-A-FROZEN-NUMBERS.md)
    - SUPERSEDED-with-strikethrough preservation pattern for audit traceability
key-files:
  created: []
  modified:
    - src/R/figures/fig2_cs_yield.R (140 lines diffed; disk-derived baseline)
    - src/R/figures/fig3_sh2b3_eur_collapse_forest.R (168 lines diffed; sub-table panel)
    - docs/manuscript/figures/fig2_cs_yield.pdf (cairo_pdf 24277 bytes)
    - docs/manuscript/figures/fig2_cs_yield.png (600 dpi 227876 bytes)
    - docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf (cairo_pdf 40664 bytes)
    - docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png (600 dpi 722541 bytes)
    - docs/manuscript/track_a_pivot.md (8 reframe sites)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (live block + reconciliation row)
    - .planning/amendments/TRACK-A-PIVOT.md (10 ghost-numeric replacements)
decisions:
  - "Comparator tightened: 12/96 -> 4.25x SUPERSEDED; live baseline is 48/95 -> 51/96 = 1.06x (matched-coverage k2d full-coverage)"
  - "fig2 R script disk-derives identity-LD baseline from IDENTITY-LD-K2D-FIT-SUMMARY.tsv at runtime (no hardcoded 12L)"
  - "fig3 sub-table panel surfaces ld_overlap_fraction + susie_status + L_saturated; existing forest panels unchanged"
  - "FTO_16q12 EUR Tier-C ld_overlap_fraction = 0 finding is now load-bearing in manuscript Tier-C disclosure paragraph"
  - "T10 (HLA double-classification) DEFERRED — three-option matrix preserved for user direction"
metrics:
  duration: ~50 minutes (3 waves, 4 atomic commits)
  completed: 2026-04-25
---

# Phase quick-260425-kki Plan 01: Track A audit-driven figure correction pass — Summary

**One-liner:** Tightened the matched-coverage Stage 2 fine-mapping yield comparator from a partial-coverage Stage 1d narrow-validation 12/96 baseline (4.25x) to the k2d full-coverage 2026-04-25 re-fire 48/95 baseline (1.06x); surfaced the buried Tier-C ld_overlap_fraction = 0 finding at FTO_16q12 EUR; purged 10 ghost numerics from the planning amendment.

**Anchor language (manuscript-locked):** "we tightened the comparator and the inflation magnitude shifted." This phrase appears verbatim at L138 of `docs/manuscript/track_a_pivot.md` and near-verbatim at L82 (Methods §Identity-LD vs Real-LD Comparison: "We tightened the comparator to k2d full-coverage and the inflation magnitude shifted from 4.25× to 1.06×").

---

## 1. Disk-truth shift

| Source | Denominator | Non-empty CS | % | Notes |
|---|---|---|---|---|
| `results/fine_mapping/finemap_summary.tsv` (Stage 2 real-LD, 2026-04-22) | 96 | 51 | 53.1% | column `credible_sets` (count) |
| `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` (k2d full-coverage identity-LD, 2026-04-25) | 95 | 48 | 50.5% | column `n_CS` |
| **Matched-coverage fold change** | — | — | — | **51 / 48 = 1.0625x ≈ 1.06x** |

**SUPERSEDED 2026-04-25** (preserved verbatim in TRACK-A-FROZEN-NUMBERS.md): the prior 12/96 (12.5%) -> 51/96 = 4.25x contrast reflected a partial-coverage Stage 1d narrow-validation freeze (only 2 of 10 admissible regions on the identity-LD branch). The 12/96 baseline is preserved with strike-through and SUPERSEDED markup for audit traceability — not deleted.

**Denominator note:** the k2d identity-LD re-fire enumerated 95 of 96 fits at admissibility. The single missing cell is `bmi.EUR.APOE_19q13` (Stage 2 real-LD status: `non_converged`, n_CS = 6), absent from the k2d Snakemake manifest input. The fold-change is robust to this 1-cell denominator difference: 50.5% -> 53.1% under either denominator choice.

---

## 2. Atomic commits landed

| # | Wave | Commit | Subject | Files |
|---|---|---|---|---|
| 1 | W1 (Priority 1) | `884eb3d` | docs(quick-260425-kki): tighten Stage 2 fine-mapping yield comparator against k2d full-coverage identity-LD re-fire | src/R/figures/fig2_cs_yield.R + docs/manuscript/figures/fig2_cs_yield.{pdf,png} + .planning/amendments/TRACK-A-FROZEN-NUMBERS.md + docs/manuscript/track_a_pivot.md (5 files) |
| 2 | W2 (Priority 2) | `89a63e2` | docs(quick-260425-kki): surface ld_overlap_fraction + susie_status data-quality on Fig 3 + Tier-C reporting | src/R/figures/fig3_sh2b3_eur_collapse_forest.R + docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.{pdf,png} + docs/manuscript/track_a_pivot.md (4 files) |
| 3 | W3 (Priority 3f) | `58a5e2d` | docs(quick-260425-kki): purge 1,446 / 861 ghost numerics from TRACK-A-PIVOT.md amendment | .planning/amendments/TRACK-A-PIVOT.md (1 file) |
| 4 | W3 (Priority 3h) | `f0451b0` | docs(quick-260425-kki): document 95 vs 96 denominator and missing bmi.EUR.APOE_19q13 fit | docs/manuscript/track_a_pivot.md (1 file) |

**Total: 4 atomic commits.** T10 (Priority 3g — HLA double-classification) DEFERRED. T5 (Priority 1) is independently load-bearing — if W2 (T8) and W3 (T9, T11) had not landed, T5 alone would have made the manuscript honest.

**Stage 2 commit-hash anchors at L146/L148** (`6de9a88`, `a6e3214`, `7d54183`, `1635d37`) PRESERVED — they're audit anchor commits and unaffected by the comparator tightening.

---

## 3. Missing AUDIT-REVIEW-2026-04-25.md (audit-trail note)

**The user brief references `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` as the source of truth for this work, but that file does not exist on disk.** The user's brief itself was the working spec for this task. Future readers of this commit cluster should treat the Priority 1–3 brief as the audit document until/unless an AUDIT-REVIEW-2026-04-25.md is committed retrospectively.

---

## 4. Deferred Task 10 — HLA double-classification (Priority 3(g))

**This task was DEFERRED.** No commit produced; HLA framing in the manuscript is UNCHANGED.

The user brief Priority 3(g) instruction "(g) HLA double-classification — pick fallback OR negative-control, remove from the other" reflects an audit-author judgment that the orchestrator did not have full context on. The manuscript currently frames HLA as both (a) admissibility-rejected (falls back to identity-LD; L80, L208, L242) and (b) a pre-registered negative control (L102, L138, L186, L238). The orchestrator's read is that these are NOT mutually exclusive — admissibility is about LD branch, negative-control is about expected-truth status. The audit document `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` is missing from disk; without it the audit author's intended single-classification is unknown.

### HLA framing question (deferred from quick-260425-kki Priority 3(g))

**Question for user:** which framing should HLA carry?

| Option | Description | Trade-off |
|---|---|---|
| 1 | Keep both (status quo, orchestrator's read) | Most accurate technical description; risks reviewer confusion if read as a category error |
| 2 | HLA is fallback only — drop the negative-control framing | Simpler narrative; loses the calibration-evidence value of HLA's null behavior |
| 3 | HLA is negative-control only — drop the fallback framing | Cleaner negative-control story; loses the LD-branch admissibility disclosure |

**Recommended path:** schedule a separate `/gsd-quick` task once user direction is received. The audit reframe (Priorities 1–3f, 3h) does not depend on resolving this and has been completed.

---

## 5. Deferred upstream-compute follow-ons (out-of-scope per user brief constraints)

These are recorded in SUMMARY.md per the user brief output spec (item 4); they are NOT executed in this commit cluster. Each requires either an LSF compute slot or a strategic decision:

1. **SH2B3 EUR L=20 re-fit on BMI / hypertension / stroke** — Terminal A LSF compute slot. The three non_converged fits at L=10 may converge at L=20; this informs the structural composition analysis and the canonical SH2B3 trait-pair coloc.susie re-fire.

2. **SH2B3 canonical trait-pair coloc.susie runs** (BMI×hypertension, hypertension×stroke). Currently the Stage 2 manifest only contains `SH2B3_12q24__EUR__asthma_vs_t2d`; the canonical pairs are absent (consistent with credible-set collapse on partner traits). A targeted re-fire is pre-registered in TRACK-A-FROZEN-NUMBERS.md L133 and remains gated on the L=20 re-fit decision.

3. **PIP-shift / lead-variant rank composition analysis** (`TODO-COMPOSITION-FOLLOWON` marker installed in Abstract at L28). Surfaces the structural credible-set composition difference between identity-LD and real-LD beyond the count-level 1.06x; gated on the L=20 re-fit landing.

4. **Pathway-enrichment recompute** on the corrected signal set (post any of the above re-fits altering the Tier-A/B/C inventory).

5. **Submission venue decision.** The 1.06x framing materially shifts the manuscript's headline magnitude. Carter should re-evaluate whether the current target (Genome Medicine original research article) remains the best fit, vs alternatives like a Bioinformatics Applications Note focused on the LD-framework methods contribution. This is a `/gsd-discuss-phase` decision, not implementation.

6. **HLA double-classification (Priority 3(g))** — see §4 above for the structured deferred question.

---

## 6. Phase-level verification gates — all 10 PASSED

| # | Gate | Result |
|---|---|---|
| 1 | No live 4.25-fold citations in track_a_pivot.md | PASS |
| 2 | fig2 disk-derived (no `N_IDENTITY_LD_NONEMPTY <- 12L`; reads IDENTITY-LD-K2D-FIT-SUMMARY.tsv) | PASS |
| 3 | fig2_cs_yield.{pdf,png} re-rendered (24277 / 227876 bytes; cairo_pdf, 600 dpi) | PASS |
| 4 | fig3 sub-table panel ("Per-fit data-quality disclosure" present in R script) | PASS |
| 5 | Tier-C FTO ld_overlap_fraction = 0 + variants_exceed_threshold surfaced in manuscript | PASS |
| 6 | TRACK-A-FROZEN-NUMBERS.md updated (live block + SUPERSEDED 2026-04-25) | PASS |
| 7 | Ghost numerics fully purged from TRACK-A-PIVOT.md (zero "1,446" / "1446" / "861" hits) | PASS |
| 8 | 95-vs-96 denominator and missing `bmi.EUR.APOE_19q13` documented in manuscript | PASS |
| 9 | Atomic commit count: 4 (T5 + T8 + T9 + T11; T10 deferred) | PASS |
| 10 | Framing-lock zero-tokens check on commit messages (no revision/cleanup/fix-up/mistake/etc.) | PASS |

---

## 7. Files modified — one-line per file

| File | Change |
|---|---|
| `src/R/figures/fig2_cs_yield.R` | Replaced hardcoded 12L identity-LD baseline with disk-derived read of IDENTITY-LD-K2D-FIT-SUMMARY.tsv; locked-scalar block now asserts 48L / 95L; FOLD_CHANGE_EXPECTED literal removed (computed from disk); plot annotation, subtitle, caption, post-save stdout all reframed under matched-coverage 1.06x. |
| `docs/manuscript/figures/fig2_cs_yield.pdf` | Cairo_pdf re-rendered at 85x70 mm with 48/95 vs 51/96 bars and "1.06x yield (matched-coverage)" annotation; 24277 bytes. |
| `docs/manuscript/figures/fig2_cs_yield.png` | 600 dpi re-rendered matching the PDF; 227876 bytes. |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | New "## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE" block at top with 48/95 / 51/96 / 1.06x / status distribution / denominator note; legacy 12/96 -> 4.25x block strike-through with "SUPERSEDED 2026-04-25" preservation; reconciliation log gains 2026-04-25 row. |
| `docs/manuscript/track_a_pivot.md` | Eight substantive sites: Abstract L28 (matched-coverage + TODO-COMPOSITION-FOLLOWON marker), Methods §Identity-LD Comparison L82 (anchor language + 95-vs-96 denominator), Methods §Admissibility L80 (95-of-96 reconciliation, T11), Headline Result L138 ("we tightened the comparator and the inflation magnitude shifted" verbatim), Tier-C disclosure paragraph (FTO ld_overlap_fraction = 0 + SH2B3 0.0385 + Figure 3 cross-ref), Discussion §Strengths L214 (structural reframe), Discussion §Pathway L222 (composition reframe), Conclusions L252 (count-vs-structural reframe), Figure 2 caption L293/295 (full reframe). |
| `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` | Added disclosure-columns extractor (`extract_disclosure()`) reading per-trait JSON for both LD branches; cross-checks convergence_status against EXPECTED_REAL_STATUS; new sub-table panel `p_disclosure` rendered as third row of patchwork composition; PDF/PNG dimensions expanded 110 mm -> 160 mm vertical. Existing EXPECTED_ID_CS / EXPECTED_REAL_CS / EXPECTED_REAL_STATUS scalars unchanged. |
| `docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf` | Cairo_pdf re-rendered at 180x160 mm with new bottom disclosure panel; 40664 bytes. |
| `docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png` | 600 dpi re-rendered matching the PDF; 722541 bytes. |
| `.planning/amendments/TRACK-A-PIVOT.md` | 10 ghost-numeric replacements at L37, L41, L80, L104, L125, L134, L181, L257, L267, L375 — all "1,446" / "861" tokens replaced with disk-truth Stage 2 numerics (1,302 attempted analyses = 28 trait-pair coloc.susie + 1,274 QTL-coloc; 1,005 too_few_snps; 78.9% failure rate). L125 additionally absorbs the W1 comparator tightening (51/96 vs 48/95 = 1.06x). |

Audit artifacts under `.planning/quick/260425-kki-track-a-audit-driven-figure-correction-p/` (not staged in the executor's atomic commits; orchestrator handles the docs commit):
- `260425-kki-PLAN.md` (the working plan)
- `260425-kki-SUMMARY.md` (this file)
- `fig2_render.log` (R stdout from T2 render)
- `fig3_render.log` (R stdout from T6 render)
- `tierC_disclosure.log` (R stdout from T7 Tier-C extraction)
- `tierC_disclosure.tsv` (Tier-C per-row ld_overlap_fraction TSV)

---

## 8. Manuscript reframe site coverage (T4 + T7 + T11)

All 7 plan-locked sites + 1 added Tier-C disclosure paragraph + 1 added Methods §Admissibility denominator note. The post-edit line numbers shift slightly because the inserted prose adds ~200 words across the file; the substantive content at each plan-locked site:

| Original line | Post-edit line | Section | Reframe applied |
|---|---|---|---|
| L28 | L28 | Abstract | matched-coverage 48/95 vs 51/96 = 1.06x; TODO-COMPOSITION-FOLLOWON marker installed; superseded 12/96 explicitly named as "earlier freeze" |
| L82 | L82 | Methods §Identity-LD vs Real-LD Comparison | "We tightened the comparator to k2d full-coverage and the inflation magnitude shifted from 4.25× to 1.06×"; 95-vs-96 denominator note; missing bmi.EUR.APOE_19q13 named |
| L138 | L138 | Results §Headline | "We tightened the comparator and the inflation magnitude shifted" (verbatim anchor language); structural-vs-count framing; cross-ref to §SH2B3 + §Pathway |
| (new) | L140 | Results §Tier-C disclosure (T7) | FTO_16q12 EUR ld_overlap_fraction = 0 + ld_status = variants_exceed_threshold; SH2B3 EUR asthma 3.85% overlap; cross-ref to Figure 3 sub-table |
| L214 | L216 | Discussion §Strengths | Count-level 1.06x is modest; structural (non-convergence + ld_overlap_fraction = 0 + canonical-pair absence) is the load-bearing inflation signal |
| L222 | L224 | Discussion §Pathway reframing | Composition shifts even when count-level yield is comparable (48/95 vs 51/96) |
| L252 | L254 | Conclusions | Structural credible-set composition rather than count-level yield is the inflation mechanism |
| L293 | L295 | Figure 2 caption | 48/95 vs 51/96 = 1.06x; 95-vs-96 denominator; Stage 1d narrow-validation 12/96 named as superseded |
| (new) | L80 | Methods §Admissibility (T11) | 95-of-96 reconciliation appended at admissibility paragraph; bmi.EUR.APOE_19q13 named |

**Stage 2 commit-hash anchors at L146/L148** (`6de9a88`, `a6e3214`, `7d54183`, `1635d37`) verified preserved (4/4 hits via `grep -c`).

---

## 9. STATE.md row (proposal for orchestrator)

For the orchestrator's STATE.md update:

```
| 2026-04-25 | quick-260425-kki Track A audit-driven figure correction pass | 4 atomic commits: 884eb3d (W1 Priority 1, comparator tightening: 12/96 -> 4.25x SUPERSEDED, live 48/95 -> 51/96 = 1.06x; fig2 disk-derived; TRACK-A-FROZEN-NUMBERS.md live block + reconciliation row; manuscript 7 sites reframed) ; 89a63e2 (W2 Priority 2, ld_overlap_fraction + susie_status data-quality on Fig 3 + Tier-C; FTO_16q12 EUR ld_overlap_fraction = 0 surfaced) ; 58a5e2d (W3 Priority 3f, 10 ghost-numeric purges from TRACK-A-PIVOT.md) ; f0451b0 (W3 Priority 3h, 95-vs-96 denominator note + missing bmi.EUR.APOE_19q13 named in Methods §Admissibility). T10 (HLA double-classification, Priority 3g) DEFERRED with three-option matrix preserved in SUMMARY for user direction. AUDIT-REVIEW-2026-04-25.md not on disk; user brief was working spec. Upstream-compute follow-ons recorded: SH2B3 L=20 re-fit, canonical SH2B3 trait-pair coloc.susie, PIP-shift composition analysis (TODO-COMPOSITION-FOLLOWON marker installed), pathway recompute, submission venue decision (1.06x may shift target Genome Medicine -> Bioinformatics Applications Note). |
```

`stopped_at` proposal: `Completed 260425-kki Track A audit reframe; 4 commits 884eb3d..f0451b0; ready for user review of HLA double-classification three-option matrix and upstream-compute follow-on prioritization.`

---

## Self-Check: PASSED

- All 4 commit hashes verified present in `git log`: `884eb3d`, `89a63e2`, `58a5e2d`, `f0451b0`.
- All 4 modified figure files exist and exceed size thresholds: fig2.pdf 24277 > 10240; fig2.png 227876 > 51200; fig3.pdf 40664 > 10240; fig3.png 722541 > 51200.
- All 10 phase-level verification gates pass.
- Zero forbidden-framing tokens in any commit message body (greppable check).
- Five files in T5 commit, four in T8 commit, one in T9 commit, one in T11 commit — all atomic per priority as planned.
- T10 deferred with structured question; no commit produced for it as planned.
