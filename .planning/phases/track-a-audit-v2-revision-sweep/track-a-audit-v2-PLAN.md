---
phase: track-a-audit-v2-revision-sweep
plan: 01
type: execute
wave: 0
depends_on: []
autonomous: true
interactive: false
requirements: [REQ-TRACK-A-AUDIT-V2-CLOSURE]
task_count: 14
estimated_duration_hours: 6
source_of_truth: .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md
files_modified:
  - docs/manuscript/track_a_pivot.md
  - docs/manuscript/figures/fig_s2_paired_fit_composition.R
  - docs/manuscript/figures/fig_s2_paired_fit_composition.png
  - .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  - .planning/DECISIONS.md
  - .planning/STATE.md
must_haves:
  truths:
    - All targets disk-verified as still-residual; pre-closed items skipped
    - All 14 commits atomic, byte-attestable, gate-verified
    - HQ#2 supplementary analysis runs locally, no LSF
    - SUPERSEDED-block preservation: when revising, annotate prior text rather than deleting
    - Carter framing: "previously cited X / matched-coverage Y" pattern; original-research framing
    - bioRxiv-submission-ready manuscript by completion
  forbidden_tokens:
    - "credible-set collapse precluding"
    - "manufactures PP.H4"
    - "four of five non_converged"
    - "lost (pair absent"
no_lsf: true
no_data_egress: true
---

# PLAN — Track A Audit V2 Revision Sweep

## Objective

Implement all residual findings from `.planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md` autonomously. Deliver bioRxiv-submission-ready manuscript. Audit V2's full text is the authoritative spec; this PLAN.md is the executable adapter.

## Pre-flight disk-state map (verified 2026-04-27)

The audit V2 was written against snapshot `b3ee506`. Disk-state inspection at HEAD confirms several audit-cited "drifts" are already closed. Tasks below scope only the actually-residual items.

| Audit V2 item | Disk state at HEAD | Action |
|---|---|---|
| L28 Abstract "credible-set collapse precluding" | ALREADY uses `not executed` / `missing run` | SKIP (verify forbidden-token grep returns 0) |
| L216 Discussion opener | ALREADY uses `not executed` | SKIP (Task 5 may still trim "structural inflation" overstatement) |
| L280–281 Table 3 "lost" | ALREADY uses `not executed` | SKIP (verify forbidden-token grep returns 0) |
| L297 Fig 3 caption "four of five" | ALREADY says `three of five` | SKIP (verify forbidden-token grep returns 0) |
| L148 §3.4 "Wang et al. 2020²⁹" | STILL incorrect (ref 29 = Wallace 2021) | Task 1 |
| L82 Methods audit-narrative | STILL contaminated | Task 2 |
| L254 Conclusion 1 "credible-set composition collapse" | STILL present | Task 3 (HQ#3 reframe) |
| L356 Decision-Pending item 4 | STILL present | Task 4 |
| L218–220 Discussion "manufactures PP.H4" | needs disk-check | Task 5 |
| Abstract+Headline FTO 0.3099 QTL caveat | STILL absent | Task 6 |
| Fig S7 "exploratory" framing | STILL present | Task 7 |
| Methods L-saturation disclosure | STILL absent | Task 8 |
| Eval 2(a) niter=100 identity-LD twist | STILL not absorbed in §3.4 | Task 9 |
| HQ#2 paired-fit composition Fig S2 | new build | Task 10 |
| TRACK-A-AUDIT-RESPONSE V2 closure flips | needed | Task 11 |
| TRACK-A-FROZEN-NUMBERS.md HQ#2 scalars | needed (after Task 10) | Task 12 |
| DECISIONS.md new entries | needed | Task 13 |
| Slug docs (PLAN/AUDIT/SUMMARY) | needed | Task 14 |

---

## Tasks

### Task 1 (QI#1) — Fix citation at §3.4 L148

**File:** `docs/manuscript/track_a_pivot.md`
**Line:** 148
**Change:** Remove `Wang et al. 2020²⁹; ` from the parenthetical citation pair `(Wang et al. 2020²⁹; Zou et al. 2022²⁰)`. Result: `(Zou et al. 2022²⁰)`. Reference ²⁹ in this manuscript is Wallace 2021 (verified at L321); Wang 2020 is not in the reference list. The simpler path is to drop the wrong-numbered cite; Zou 2022²⁰ already covers the SuSiE convergence-theory point.
**Acceptance:**
  - `grep -c "Wang et al. 2020" docs/manuscript/track_a_pivot.md` returns `0`
  - `grep -c "Zou et al. 2022²⁰" docs/manuscript/track_a_pivot.md` ≥ existing count
  - Surrounding lines (L147, L149) byte-identical pre vs post
**Commit:** `revise(track-a-v2-qi1): remove erroneous Wang-2020-29 citation at §3.4 L148 (ref 29 = Wallace 2021; Zou 2022-20 already covers convergence-theory point)`

### Task 2 (QI#2) — Move audit-process narrative out of Methods L82

**File:** `docs/manuscript/track_a_pivot.md`
**Source line:** 82 (Methods §Fine-Mapping Integration)
**Target:** new Discussion subsection `### Audit-driven comparator tightening` inserted between `### Identity-LD Inflation and Its Mechanism` (L218) and `### Reframing of Cardiometabolic Pleiotropy Claims` (L222). Or, simpler: append to existing §Identity-LD Inflation. Use whichever position requires fewer surrounding-line edits.
**Text to relocate** (parenthetical at L82):
  > "(An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline; that freeze covered only 2 of 10 admissible regions on the identity-LD branch and is not the appropriate matched-coverage comparator. We tightened the comparator to k2d full-coverage and the inflation magnitude shifted from 4.25× to 1.06×.)"
**Replacement at L82:** Either delete the parenthetical (cleanest — Methods then describes only the analysis as it stands, with provenance pointer to OSF deviation log) or replace with a one-liner pointer: `(comparator-tightening provenance documented in Discussion §Audit-driven comparator tightening and OSF deviation log osf.io/az52u)`. Pick the pointer-replacement for traceability.
**Acceptance:**
  - L82 contains pointer-only language (one sentence max)
  - Relocated text appears in Discussion under appropriate subsection heading
  - `grep -c "We tightened the comparator" docs/manuscript/track_a_pivot.md` returns exactly `1` (the relocated copy, not duplicated)
**Commit:** `revise(track-a-v2-qi2): move audit-process narrative out of Methods §Fine-Mapping Integration L82 to Discussion §Audit-driven comparator tightening`

### Task 3 (HQ#3) — Reframe Conclusion 1 to method-namespace-correct language

**File:** `docs/manuscript/track_a_pivot.md`
**Line:** 254
**Current text:** Begins `1. **Identity-LD coloc.abf fine-mapping inflates cross-trait PP.H4 at curated cardiometabolic loci primarily through structural credible-set composition rather than count-level yield.**`
**Replacement (audit V2 drop-in language):**
  > `1. **Replacement of identity-LD with matched 1000G EUR LD under SuSiE-RSS + coloc.susie at admissible curated cardiometabolic loci does not materially change credible-set count (1.06× yield ratio) but produces structural posterior shifts.** At admissible EUR autosomal regions under the matched-coverage k2d full-coverage comparator, SuSiE-RSS + real 1000G EUR LD yielded 51/96 non-empty credible sets vs 48/95 under identity-LD (1.06-fold count-level differential). The structural shifts (PIP redistribution, lead-variant rank instability, non-convergence at three of five SH2B3 EUR real-LD fits, ld_overlap_fraction = 0 at the headline FTO_16q12 EUR Tier-C signal) are quantified in supplementary Figure S2 across all 48 paired non-empty fits. At these 50 curated loci, no cross-trait colocalization signal reaches Tier A or Tier B under real-LD coloc.susie — in contrast to the multiple PP.H4 ≥ 0.8 claims in the published coloc.abf-under-identity-LD literature, which were not directly tested in this audit because the canonical SH2B3 EUR BMI–hypertension and hypertension–stroke trait-pairs were not executed under Stage 2 coloc.susie (cf. Results §SH2B3 case study and Figure 3).`
**Acceptance:**
  - L254 begins with `1. **Replacement of identity-LD` (or matching new-claim opener)
  - Conclusion 1 no longer contains: `coloc.abf fine-mapping inflates`, `credible-set composition collapse`
  - Conclusion 1 contains: `SuSiE-RSS + coloc.susie`, `1.06-fold`, `Figure S2`
  - Conclusions 2+ unchanged (verify byte-identical L255+)
**Commit:** `revise(track-a-v2-hq3): reframe Conclusion 1 to method-namespace-correct SuSiE-RSS+coloc.susie language per audit V2 §HQ#3`

### Task 4 (QI#3) — Delete stale Decision-Pending item 4 + renumber

**File:** `docs/manuscript/track_a_pivot.md`
**Lines:** 356 (delete), 357–360 (renumber 5→4, 6→5, 7→6, 8→7)
**Acceptance:**
  - L356 of new file no longer references `identity-LD comparator branch output at admissible regions`
  - Decision-Pending list ends at item 7 (was 8)
  - Items renumbered consistently
**Commit:** `revise(track-a-v2-qi3): delete stale Decision-Pending item 4 (k2d re-fire answered the question) + renumber 5-8 to 4-7`

### Task 5 — Trim "manufactures PP.H4" / "structural inflation" overstatement

**File:** `docs/manuscript/track_a_pivot.md`
**Lines:** 218–222 (Discussion §Identity-LD Inflation and Its Mechanism)
**Action:**
  1. Disk-grep for tokens: `manufactures`, `manufactured PP.H4`, `manufacture`. If present, replace with calibrated language: `produces structural posterior shifts in` / `redistributes`.
  2. Reframe `the structural inflation mechanism — non-convergence ... — is what propagates into the cross-trait PP.H4 reassignment` to be conditioned on Figure S2 quantification: `the structural posterior-shift mechanism (Figure S2) — non-convergence ..., low ld_overlap_fraction at the FTO Tier-C signal, partial-overlap warnings on surviving fits — propagates into the cross-trait PP.H4 reassignment that we observe at admissible loci`.
  3. Honest-framing addition: insert one sentence acknowledging that count-level yield differential is statistically indistinguishable: `at the count level, identity-LD vs real-LD CS yield is statistically indistinguishable in this curated set (51/96 vs 48/95).`
**Acceptance:**
  - `grep -ic "manufactur" docs/manuscript/track_a_pivot.md` returns `0`
  - L218–222 contains `Figure S2` reference + `statistically indistinguishable` framing
**Commit:** `revise(track-a-v2-eval1-residual): trim "manufactures PP.H4" overstatement + condition structural-inflation framing on Figure S2 quantification`

### Task 6 (New Issue 4) — Add QTL-coloc data-quality caveat to FTO 0.3099 callouts

**File:** `docs/manuscript/track_a_pivot.md`
**Sites:**
  - Abstract L28 (search for `PP.H4 = 0.3099`)
  - Headline Result L138 (search for `PP.H4 = 0.3099`)
  - Conclusion FTO callout (if present after Task 3 reframe)
**Action:** Append parenthetical caveat at each site: `(subject to the 78.9% QTL-coloc too_few_snps caveat documented in Methods §Harmonization-Pipeline Diagnostics and Limitations bullet 5; structural variant-ID-mismatch fix may incompletely propagate)`.
**Acceptance:**
  - All three sites contain the caveat parenthetical
  - `grep -c "subject to the 78.9% QTL-coloc" docs/manuscript/track_a_pivot.md` ≥ 3
**Commit:** `revise(track-a-v2-newissue4): add QTL-coloc data-quality caveat to FTO 0.3099 callouts at Abstract+Headline+Conclusion`

### Task 7 (New Issue 5) — Promote Fig S7 framing

**File:** `docs/manuscript/track_a_pivot.md`
**Action:** Find Fig S7 caption / mention. Replace `exploratory methodology-validation` (or `exploratory`-adjacent framing) with: `Methodology-validation finding: 55% (33/60) of admissible Stage 2 EUR fits sit below the Benner et al. 2017 calibration threshold (ld_overlap_fraction < 0.5), a discovery-grade observation about LD-reference quality across this curated locus set.`
**Acceptance:**
  - Fig S7 caption no longer uses `exploratory methodology-validation`
  - Caption contains `55%`, `33/60`, `Benner et al. 2017 calibration threshold`
**Commit:** `revise(track-a-v2-newissue5): promote Fig S7 framing from exploratory to methodology-validation finding (55% of EUR fits below Benner 2017 threshold)`

### Task 8 (New Issue 6) — Add Methods L-saturation prose disclosure

**File:** `docs/manuscript/track_a_pivot.md`
**Target:** Methods §Fine-Mapping Integration (around L76–84) or §Identity-LD vs Real-LD Comparison Design (L92–98). Pick whichever already has nearest L-saturation context.
**Insertion text:**
  > `Eleven of 95 identity-LD k2d-rerun fits (`results_identity_ld/fine_mapping/susie/`) carry the canonical L-saturation fingerprint cs_sizes = "3;3;3;3;3;3;3;3;3;4" (the SuSiE purity-filter minimum saturated at L = 10), the signature Zou et al. 2022²⁰ §Discussion warns against. An L-sweep re-fit (L = 20 or L = 30) of these fits is pre-registered as supplementary work; the L = 10 numbers reported here are L-saturated and conservatively interpretable as lower bounds on credible-set yield.`
**Acceptance:**
  - Methods section contains `Eleven of 95 identity-LD` + `L-saturation fingerprint` + `pre-registered as supplementary work`
**Commit:** `revise(track-a-v2-newissue6): add Methods L-saturation prose disclosure for 11 of 95 identity-LD fits`

### Task 9 (Eval 2(a) twist) — Integrate niter=100 identity-LD non-convergence finding into §3.4

**File:** `docs/manuscript/track_a_pivot.md`
**Lines:** 148 (after Task 1 lands)
**Action:** Insert between the existing "3 of 5 SH2B3 EUR traits returned `convergence_status = non_converged`" sentence and the "SuSiE-RSS posterior credible sets are theoretically meaningful only at convergence" sentence:
  > `The Figure 3 disclosure subtable additionally reveals that under identity-LD at SH2B3 EUR, BMI / hypertension / stroke also ran to niter = 100 (the iteration cap; the SuSiE-RSS implementation marks these "converged" but the Wang et al. JRSS-B 2020 §3.2 convergence definition treats niter = max_iter as non-convergence). The honest read is that **at SH2B3 EUR, no SuSiE-RSS fit at L = 10 reaches a stable posterior under either LD reference for BMI / hypertension / stroke** — strengthening the methodological-constraint framing rather than weakening it.`
**Acceptance:**
  - L148 paragraph contains `niter = 100` + `under either LD reference` + reference to Figure 3 disclosure subtable
  - §3.4 still ends with the existing pre-registered re-fire roadmap
**Commit:** `revise(track-a-v2-eval2a-twist): integrate niter=100 identity-LD non-convergence finding into §3.4 strengthening methodological-constraint framing`

### Task 10 (HQ#2) — Build supplementary Figure S2 paired-fit composition analysis

**This is the only substantial new build.** Audit V2 §HQ#2 specifies the analysis explicitly:

> "paired-fit comparison of (PIP-of-top-variant, lead-variant rank, credible-set member overlap) between identity-LD and real-LD across all 48 paired non-empty fits ... computable from the on-disk JSONs in `results/fine_mapping/susie/*.json` and `results_identity_ld/fine_mapping/susie/*.json`, without re-firing SuSiE."

**Steps:**

1. **New script:** `docs/manuscript/figures/fig_s2_paired_fit_composition.R`
   - Read 96 JSONs from `results/fine_mapping/susie/`
   - Read 95 JSONs from `results_identity_ld/fine_mapping/susie/`
   - Match on `{trait}_{ancestry}_{region}` keys
   - Filter to 48 paired non-empty fits (both branches have n_cs >= 1)
   - Per pair compute:
     - `pip_top_identity` and `pip_top_real` (PIP of top variant in CS#1)
     - `lead_variant_rank_identity` and `lead_variant_rank_real` (rank of canonical lead variant if known; else top-PIP variant rank)
     - `cs_overlap_jaccard` (Jaccard index of variants in CS#1 between identity-LD and real-LD)
   - Render 3-panel figure:
     - Panel A: scatter of pip_top_identity vs pip_top_real (diagonal = no shift)
     - Panel B: histogram of lead-variant-rank deltas
     - Panel C: histogram of CS overlap Jaccard
   - Output: `docs/manuscript/figures/fig_s2_paired_fit_composition.png` (300 DPI, ~12 cm × 10 cm)
   - Output: also write `docs/manuscript/figures/fig_s2_paired_fit_composition_summary.tsv` with per-pair scalars (47 + 1 header rows)

2. **Run script:** Use the existing R env (`la_multitrait_r` per project memory) — the script must work with currently-installed packages (jsonlite, dplyr, ggplot2, patchwork). If a package is missing, fall back to base R.

3. **Locked summary scalars** (compute and output to figure header / `_summary.tsv`):
   - Median PIP-top shift
   - 95% CI of CS overlap Jaccard
   - Fraction of pairs with lead-variant-rank stability (rank delta = 0)

4. **Manuscript integration:** Add Figure S2 reference + caption to `docs/manuscript/track_a_pivot.md`. Place in supplementary section near Fig S7. Caption should disk-cite each scalar.

**Acceptance:**
  - Script runs to completion without errors
  - PNG written, non-zero size, valid PNG header
  - Summary TSV has 48 + 1 rows
  - Manuscript references Figure S2 in at least 2 places (Conclusion 1, Discussion §Identity-LD Inflation)

**Commit:** `feat(track-a-v2-hq2): build Figure S2 paired-fit composition analysis (PIP shift + lead-rank delta + CS overlap Jaccard) across 48 paired non-empty SuSiE-RSS fits`

### Task 11 — Flip TRACK-A-AUDIT-RESPONSE-2026-04-26.md rows to V2-CLOSED

**File:** `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md`
**Action:** For each audit V2 item closed by this slug (Tasks 1–10), update the closure tracker row with:
  - Status: `V2-CLOSED`
  - Commit pointer: SHA from this slug's commits
  - Date: `2026-04-27`
**Items to flip:**
  - Eval 1 residual ("manufactures PP.H4")
  - QI#1 (citation), QI#2 (Methods narrative), QI#3 (decision-pending)
  - HQ#2 (paired-fit composition)
  - HQ#3 (Conclusion reframe)
  - New Issues 4, 5, 6
  - Eval 2(a) twist
**Acceptance:** All 10 items show `V2-CLOSED` with commit SHAs.
**Commit:** `revise(track-a-v2-tracker): flip TRACK-A-AUDIT-RESPONSE rows to V2-CLOSED with commit pointers`

### Task 12 — Refresh TRACK-A-FROZEN-NUMBERS.md with HQ#2 paired-fit scalars

**File:** `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`
**Action:** Append new locked-scalar block at end (preserve all prior blocks verbatim per SUPERSEDED pattern):
  - Median PIP-top shift (from Task 10 output)
  - 95% CI of CS overlap Jaccard
  - Fraction lead-variant-rank stable
  - Reference to `docs/manuscript/figures/fig_s2_paired_fit_composition_summary.tsv`
**Acceptance:** New block appended; prior blocks (live + SUPERSEDED 2026-04-25) byte-identical.
**Commit:** `revise(track-a-v2-frozen): append HQ#2 paired-fit composition locked scalars block`

### Task 13 — Emit DECISIONS.md entries

**File:** `.planning/DECISIONS.md`
**New entries:**
  - `DEC-2026-04-27-01`: HQ#3 Conclusion 1 method-namespace reframe — coloc.abf → SuSiE-RSS+coloc.susie. Rationale: audit V2 Eval 5 attribution-error finding.
  - `DEC-2026-04-27-02`: HQ#2 paired-fit composition supplementary analysis — locked scalars in TRACK-A-FROZEN-NUMBERS.md L<N>; Figure S2.
  - `DEC-2026-04-27-03`: Audit V2 sweep complete; manuscript bioRxiv-submission-ready. Pre-registered re-fire items (HQ#2(i) L=20 SH2B3, HQ#2(iii) canonical pairs, Eval 2(b) L-saturation re-fire) remain DEFERRED-COMPUTE.
**Acceptance:** All 3 entries appended; section count increment matches.
**Commit:** `docs(track-a-v2-decisions): record DEC-2026-04-27-01/02/03 for HQ#3 reframe + HQ#2 supplementary + V2 sweep close`

### Task 14 — Slug docs (PLAN/AUDIT/SUMMARY)

**File:** `.planning/phases/track-a-audit-v2-revision-sweep/track-a-audit-v2-PLAN.md` (this file — already exists)
**New files:**
  - `.planning/phases/track-a-audit-v2-revision-sweep/track-a-audit-v2-AUDIT.md` (post-execution audit; gate-by-gate verification log)
  - `.planning/phases/track-a-audit-v2-revision-sweep/track-a-audit-v2-SUMMARY.md` (slug-summary doc following project convention)
  - STATE.md row: append "Quick Tasks Completed" entry under Session Continuity
  - ROADMAP.md: mark `Track-A-finalization` row as `audit V2 sweep landed 2026-04-27` (do not touch milestone-table layout)
**Acceptance:**
  - PLAN.md exists at the path
  - AUDIT.md present with 14-task gate verification log
  - SUMMARY.md present with commit-ladder + closure summary
  - STATE.md row added (no other STATE.md sections modified)
  - ROADMAP.md `Track-A-finalization` row marker updated
**Commit:** `docs(track-a-v2-final): record STATE/ROADMAP/PLAN/AUDIT/SUMMARY for Track A audit V2 revision sweep`

---

## Verification gates (post all 14 tasks)

1. `grep -c "credible-set collapse precluding\|manufactures PP.H4\|four of five non_converged" docs/manuscript/track_a_pivot.md` returns `0` for each forbidden token.
2. `grep -c "Wang et al. 2020" docs/manuscript/track_a_pivot.md` returns `0`.
3. `git log --oneline -20` shows 14 atomic commits prefixed `revise(track-a-v2-*)` / `feat(track-a-v2-*)` / `docs(track-a-v2-*)`.
4. `Rscript docs/manuscript/figures/fig_s2_paired_fit_composition.R` exits 0 (re-run for determinism check).
5. `file docs/manuscript/figures/fig_s2_paired_fit_composition.png` reports valid PNG.
6. AUDIT-RESPONSE tracker shows 10 V2-CLOSED rows added to existing closures.
7. `git status --short` ends at the expected untracked-file set (no orphan working-tree drift).

## Error-recovery protocol

- Per-task gate failure → roll the offending commit, diagnose, re-attempt up to 3 times.
- If a task hits an irreducible blocker, commit a `WIP-blocked-track-a-v2-task-N` checkpoint with diagnosis text and continue to next independent task. Do NOT abort the whole sweep.
- HQ#2 figure build is the highest-risk task; if R fails, fall back to Python (`pandas + matplotlib`) before declaring blocked.

## Out of scope (DEFERRED to future slugs)

- HQ#2(i): SH2B3 EUR L=20 SuSiE-RSS re-fit (requires LSF, Carter compute slot).
- HQ#2(iii): canonical BMI–hypertension / hypertension–stroke `coloc.susie` runs against the L=20 re-fits.
- Eval 2(b): L-saturation L=20 or L=30 re-fire for the 11 identity-LD fits.
- HQ#2(ii): drop-or-flag non-converged fits in yield counts (Carter design call).
- OSF amendment refresh (Track A submission-tomorrow timing makes this a post-submission v2 follow-on).
- All [EXTRACT: …] table placeholders in Tables 1/2/3/4 (separate slug; not gating bioRxiv submission per Carter judgment).

These are correctly flagged in TRACK-A-AUDIT-RESPONSE-2026-04-26.md and will be revisited post-submission.
