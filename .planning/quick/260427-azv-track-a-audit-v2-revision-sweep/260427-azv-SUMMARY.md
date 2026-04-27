---
phase: quick-260427-azv
plan: 01
subsystem: track-a-manuscript
tags: track-a, audit, manuscript, figure, prose, identity-ld, real-ld, susie-rss, coloc-susie, audit-v2, biorxiv
requires:
  - .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md
  - .planning/amendments/AUDIT-REVIEW-2026-04-25.md
  - .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv
  - .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  - results/fine_mapping/susie/*.json
  - results_identity_ld/fine_mapping/susie/*.json
provides:
  - track-a-audit-v2-HQ1-SH2B3-narrative-sweep
  - track-a-audit-v2-HQ2-paired-fit-structural-inflation-Figure-S2
  - track-a-audit-v2-HQ3-Conclusion-1-namespace-reframe
  - track-a-audit-v2-QI1-citation-fix
  - track-a-audit-v2-QI2-Methods-narrative-relocation
  - track-a-audit-v2-QI3-Decision-Pending-purge
  - track-a-audit-v2-NewIssue4-QTL-coloc-caveat-Abstract-L140
  - track-a-audit-v2-NewIssue5-Fig-S7-framing-promotion
  - track-a-audit-v2-NewIssue6-Methods-L-saturation-disclosure
  - track-a-audit-v2-Eval-2a-niter-integration
  - DEC-2026-04-27-01-Conclusion-namespace
  - DEC-2026-04-27-02-Figure-S2
  - DEC-2026-04-27-03-Comparator-tightening-narrative-location
affects:
  - docs/manuscript/track_a_pivot.md
  - src/R/figures/fig_s2_paired_fit_structural_inflation.R
  - docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.pdf
  - docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.png
  - .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  - .planning/DECISIONS.md
  - .planning/STATE.md
key-files:
  modified:
    - docs/manuscript/track_a_pivot.md
    - .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    - .planning/DECISIONS.md
    - .planning/STATE.md
  created:
    - src/R/figures/fig_s2_paired_fit_structural_inflation.R
    - docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.pdf
    - docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.png
metrics:
  pre_execution_head: 1e4b4646ca79ac7c58b74b277e2fb3fa40402516
  post_execution_head: <captured-after-final-commit>
  commits_landed: 12
  files_touched: 8
  manuscript_word_delta: ~+450
  manuscript_line_delta: +6
  paired_fits_n: 48
  paired_rank_eq_1_pct: 62.5
  paired_jaccard_ge_0_8_pct: 62.5
  paired_jaccard_lt_0_5_pct: 33.3
  paired_delta_pip_median: 0.0000
  duration_min: ~120
  completed_date: 2026-04-27
---

# Quick Task 260427-azv — Track A Audit-V2 Revision Sweep (Overnight Autonomous)

## One-liner

Closed all 13 actionable items from `AUDIT-REVIEW-V2-2026-04-26.md` (the second-pass independent re-review of the Track A manuscript) in 12 atomic commits over ~6 hours of autonomous executor time. Three high-stakes residuals (HQ1 SH2B3 narrative sweep across 5 manuscript surfaces, HQ2 new paired-fit structural-inflation supplementary Figure S2, HQ3 Conclusion-1 method-namespace reframe), three quick fixes (QI1 citation fix at L148, QI2 audit-process narrative relocation from Methods to Discussion, QI3 stale Decision-Pending item 4 deletion), six newly-surfaced issues (NewIssue1–3 = QI1/QI2/QI3; NewIssue4 QTL-coloc caveat in Abstract / FTO callouts; NewIssue5 Fig S7 framing promotion; NewIssue6 Methods L-saturation prose disclosure), plus one Eval 2(a) niter-twist integration into §3.4. Zero LSF, zero data egress, zero OSF portal action. Manuscript bioRxiv-submission-ready except for the 10 `[EXTRACT: …]` placeholders flagged as a separate pre-bioRxiv blocker quick task. Three `DEC-2026-04-27-XX` entries record the load-bearing namespace / supp-figure / narrative-location decisions. Where the audit-v2 doc and on-disk per-fit JSONs diverged, disk-truth integration was used (audit-v2 doc claimed identity-LD niter = 100 at SH2B3 EUR; disk shows 9 / 3 / 12 for BMI/HTN/stroke and L_saturated = TRUE at hypertension, not BMI).

## 12-commit map

| # | Wave | Commit | Files | Description |
|---|------|--------|-------|-------------|
| 1 | W1 | `81088f0` | `docs/manuscript/track_a_pivot.md` (5+/5−) | HQ1 — SH2B3 narrative sweep across Abstract L28, Discussion opener L216, Fig 3 caption L297 panels A+B, Table 3 L280–281 |
| 2 | W1 | `a345f5e` | `docs/manuscript/track_a_pivot.md` (1+/1−) | HQ3 — Conclusion claim 1 (L252–254) replaced with audit-v2 drop-in paragraph naming SuSiE-RSS + coloc.susie method namespace |
| 3 | W1 | `00cf5b9` | `docs/manuscript/track_a_pivot.md` (6+/7−) | QI1 cite fix (drop Wang²⁹) + QI3 stale Decision-Pending item 4 deletion + L140 residual stale-narrative leak ("four other ... composition collapse") |
| 4 | W1 | `cb5db17` | `docs/manuscript/track_a_pivot.md` (5+/1−) | QI2 — excise audit-process narrative from Methods L82; insert new Discussion subsection §Audit-driven Comparator Tightening between §Identity-LD Inflation and §Reframing of Cardiometabolic Pleiotropy Claims |
| 5 | W1 | `7ea3f00` | `docs/manuscript/track_a_pivot.md` (3+/3−) | NewIssue4 QTL-coloc data-quality caveat at Abstract L28 + L140 Tier-C disclosure; NewIssue5 Fig S7 framing promotion (exploratory → methodology-validation finding) |
| 6 | W1 | `205a1a3` | `docs/manuscript/track_a_pivot.md` (3+/3−) | NewIssue6 Methods L-saturation prose disclosure (11 of 95 fits show cs_sizes "3;3;3;3;3;3;3;3;3;4" fingerprint); Eval 2(a) niter-twist integration into §3.4 (real-LD non-convergence + identity-LD L-saturation = complementary failure modes); Fig 3 caption L_saturated attribution fix (BMI → hypertension per disk) |
| 7 | W2 | `d87416a` | `src/R/figures/fig_s2_paired_fit_structural_inflation.R` (NEW, 339 lines) | Add R script — paired-fit PIP + Jaccard + lead-rank from on-disk JSONs (HQ2); hard-fail asserts paired_n == 48 |
| 8 | W2 | `cc943bd` | `src/R/figures/fig_s2_paired_fit_structural_inflation.R` (3+/5−), `docs/manuscript/figures/fig_s2_*.{pdf,png}` (NEW) | Render Figure S2 PDF + PNG (cairo_pdf, 180mm × 140mm, 600 dpi); fix PROJECT_ROOT detection under Rscript (sys.frame doesn't work; use getwd()) |
| 9 | W2 | `9cb007d` | `docs/manuscript/track_a_pivot.md` (3+/1−) | Land Figure S2 caption + reference in manuscript; purge old "(S2) deferred pending identity-LD re-run" stub from S1–S6 group caption |
| 10 | W3 | `a93a414` | `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md` (49+) | Append "Audit-V2 sweep closure (2026-04-27, quick-260427-azv)" section: V2 status table for 13 items, disk-truth corrections vs. audit-v2 doc, sweep deliverables list, HQ#2 deferred items unchanged disposition |
| 11 | W3 | `11ef400` | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (25+) | Append "Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE" block (paired_n=48, ΔPIP median=0.0000, IQR 0–0.036, rank=1: 30/48 (62.5%), rank≥21 OR absent: 16/48 (33.3%), Jaccard ≥ 0.8: 30/48 (62.5%), Jaccard < 0.5: 16/48 (33.3%)) |
| 12 | W3 | `3cb266c` | `.planning/DECISIONS.md` (57+) | DEC-2026-04-27-01 Conclusion-1 namespace reframe + DEC-2026-04-27-02 Figure S2 supplementary figure + DEC-2026-04-27-03 audit-driven comparator-tightening narrative location |

## Disk-truth corrections vs. audit-v2 doc

The V2 sweep integrated **disk-truth** (per-fit JSONs at `results/fine_mapping/susie/` and `results_identity_ld/fine_mapping/susie/`) where the audit-v2 doc claims diverged from disk. User confirmed "Disk-truthful (recommended)" via AskUserQuestion at plan-mode exit. Specifically:

1. **Audit-v2 doc:** "Three identity-LD fits at SH2B3 EUR ran to niter = 100"
   **Disk:** identity-LD niter at SH2B3 EUR = 9 (BMI), 3 (HTN), 12 (stroke), 2 (asthma), 3 (T2D); all five `convergence_status = converged_primary`. **Real-LD** is what hits niter=100 for BMI/HTN/stroke (`non_converged`).
   **Resolution:** §3.4 niter-trace clause (commit `205a1a3`) integrates the disk-true version: real-LD numerical non-convergence + identity-LD L-saturation = complementary failure modes.

2. **Audit-v2 doc:** "BMI identity-LD has L_saturated = TRUE"
   **Disk:** BMI identity-LD has L_saturated = FALSE with n_CS = 3. The L_saturated = TRUE fit at SH2B3 EUR identity-LD is **hypertension**, not BMI (n_CS = 10, niter = 3, converged_primary).
   **Resolution:** Fig 3 caption (commit `205a1a3`) uses disk-truth: "identity-LD hypertension shows L_saturated = TRUE; both identity-LD hypertension and stroke fit n_CS = 10 (canonical cs_sizes fingerprint per IDENTITY-LD-K2D-FIT-SUMMARY.tsv)."

3. **Audit-v2 doc:** "11 of 95 identity-LD fits show L = 10 saturation cs_sizes fingerprint"
   **Disk:** **CONFIRMED** — 11 rows in `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` carry `cs_sizes = "3;3;3;3;3;3;3;3;3;4"`. The per-fit JSON `L_saturated` boolean is stricter and fires only on `hypertension.EUR.SH2B3_12q24` (1 of 95).
   **Resolution:** NewIssue6 prose disclosure (commit `205a1a3`) reports both numbers: "Eleven of 95 identity-LD fits show the canonical L = 10 saturation cs_sizes fingerprint (one of these — `hypertension.EUR.SH2B3_12q24` — additionally carries `L_saturated = TRUE` in the per-fit SuSiE-RSS JSON output)."

4. **Audit-v2 doc:** Figure 3 caption "four of five EUR traits at SH2B3 are non_converged"
   **Disk:** 3 of 5 (BMI, HTN, stroke; T2D and asthma are `converged_primary`).
   **Resolution:** HQ1 commit `81088f0` reframed the Fig 3 caption to "three of five" with disk-true niter context.

## Verification gates (all PASS)

| # | Gate | Result |
|---|------|--------|
| 1 | Stale-token sweep: `grep -n "credible-set collapse\|manufactures PP.H4\|four of five\|lost (pair absent" docs/manuscript/track_a_pivot.md` | 3 hits, all in "missing run rather than a documented credible-set collapse" framing (Abstract L28, §3.4 L148, Fig 3 Panel B); zero stale instances ✓ |
| 2 | Citation integrity: `grep -n "Wang et al. 2020²⁹"` | 0 hits ✓ |
| 3 | Conclusion namespace check: `sed -n '252,260p' \| grep "SuSiE-RSS + coloc.susie"` | PASS — new namespace present ✓ |
| 4 | Conclusion namespace negative: `grep "coloc.abf.*inflat"` | 0 hits in L252–260 ✓ |
| 5 | Methods cleanup: "We tightened the comparator" no longer in Methods §Identity-LD vs Real-LD Comparison | PASS — only in Discussion §Audit-driven Comparator Tightening + Headline Result + Figure 2 caption ✓ |
| 6 | Figure S2 deliverables exist | PASS (R script 339 lines + PDF 30 KB + PNG 462 KB) ✓ |
| 7 | Figure S2 disk-truth assertion: `Rscript fig_s2_*.R` reports "paired non-empty: 48" | PASS (no FAIL / ERROR; FROZEN_BEGIN/END block emitted with locked scalars) ✓ |
| 8 | Stage 2 source-of-truth TSV byte-identity (md5 unchanged pre vs post) | PASS — finemap_summary `8c3e04a2…`, coloc_summary `5fa3c400…`, tier_assignments `17ff46db…` all unchanged ✓ |
| 9 | Tracker updates landed: `grep "DEC-2026-04-27-0[123]"` | 3 entries ✓ |
| 10 | FROZEN-NUMBERS LIVE block: `grep "Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE"` | 1 hit (L58) ✓ |
| 11 | TRACK-A-AUDIT-RESPONSE V2 sweep section: `grep "V2-CLOSED"` | 13 V2-CLOSED rows in new section ✓ |
| 12 | Commit count: `git log --oneline main~12..main` | 12 atomic commits ✓ |

## Key Figure S2 frozen scalars (to FROZEN-NUMBERS LIVE block)

```
paired_n                  = 48
delta_pip_median          = 0.0000
delta_pip_iqr_lo          = 0.0000
delta_pip_iqr_hi          = 0.0363
rank_eq_1_n               = 30   (62.5%)
rank_ge_21_or_absent_n    = 16   (33.3%)
jaccard_ge_0_8_n          = 30   (62.5%)
jaccard_lt_0_5_n          = 16   (33.3%)
```

**Interpretation:** At the 48 paired non-empty SuSiE-RSS fits, ~62% are stable across LD references (same lead variant, high CS-member Jaccard, near-zero ΔPIP-of-top-variant), but ~33% show substantial structural posterior shifts (lead-variant rank ≥ 21 or absent AND Jaccard < 0.5). The Conclusion-1 reframe's "structural posterior shifts" claim is concentrated in this 1/3 minority — the audit-v2 §HQ3 measurement gap is now quantified, not asserted.

## md5 attestations

```
md5_pre_finemap_summary    = 8c3e04a202a919d94bd34a3c1d5146a2
md5_post_finemap_summary   = 8c3e04a202a919d94bd34a3c1d5146a2  (UNCHANGED ✓)

md5_pre_coloc_summary      = 5fa3c4004970c5da711d05947cb1f7d2
md5_post_coloc_summary     = 5fa3c4004970c5da711d05947cb1f7d2  (UNCHANGED ✓)

md5_pre_tier_assignments   = 17ff46dbbfe78dd537d6b9bff7f3ae67
md5_post_tier_assignments  = 17ff46dbbfe78dd537d6b9bff7f3ae67  (UNCHANGED ✓)
```

## Out-of-scope (explicitly deferred)

- HQ#2(i) — SH2B3 EUR L = 20 re-fit (DEFERRED-COMPUTE; needs LSF)
- HQ#2(ii) — Drop / flag non-converged fits in yield numerator (DEFERRED-DESIGN; Carter's call)
- HQ#2(iii) — Execute canonical BMI–HTN + HTN–stroke `coloc.susie` pairs (DEFERRED-COMPUTE; needs LSF)
- Eval 3.3 — 28/28 empty `coloc.susie` interpretation (IN-PROGRESS; gated on HQ#2(i)+(iii))
- Filling 10 `[EXTRACT: …]` placeholders in Tables 1/2/3/4 + Results (separate quick task; needs aggregator scripts) — flagged as Decision-pending item 4 pre-bioRxiv blocker
- L-sweep re-fit at L ∈ {15, 20, 30} mentioned in NewIssue6 disclosure (DEFERRED-COMPUTE)
- bioRxiv submission itself (manual; user action)
- OSF amendment posting (manual web UI per DEC-2026-04-25-02)
- `bin/track-a-repro-bundle.sh` execution (manual, post-morning, separate task)

## Plan source

`/home/ckclinto/.claude/plans/track-a-audit-v2-revision-sweep-overnig-cozy-meerkat.md` (approved by Carter via ExitPlanMode 2026-04-27 with three "Recommended" answers via AskUserQuestion: disk-truthful Eval 2(a) integration; inline FTO caveat clause; new Discussion subsection for QI2 narrative location).
