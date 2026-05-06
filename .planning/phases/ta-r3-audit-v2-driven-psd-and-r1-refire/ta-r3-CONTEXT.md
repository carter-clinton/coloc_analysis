# ta-r3 phase CONTEXT: audit-V2-driven PSD-regularized SH2B3 re-fit + R1 trait-pair coloc.susie cache-invalidated re-fire

**Phase scope:** HPC-side compute work that produces substrate the Cowork-side v5 *Genome Medicine* manuscript revision (audit items A1, A2, A3, A6-stats, A7, A8, A9 — explicitly OUT of phase scope) draws on. After W5 closeout, a `/gsd-quick 260504-XXX-ta-r3-cowork-handoff` ships artifacts back to Cowork for v5 bundle ship.

**Honest-framing lock (per `.planning/feedback_original_research_framing.md`):** Frame as "audit-driven re-analysis," NOT "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot". The manuscript md5 (`MANUSCRIPT-MD5-AT-ENTRY` below) MUST stay stable through this phase; manuscript edits OUT of scope.

**OSF amendment:** [.planning/amendments/osf-amendment-r3-2026-05-04.md](../../amendments/osf-amendment-r3-2026-05-04.md) — locks lambda sweep + W1 outcome branches + W2 outcome branches + W3 conditional gate.

**Manuscript md5 lock semantics:**

- `MANUSCRIPT-MD5-AT-ENTRY: 2a57c1a061f0c66988a55d1d6600efdf`
  - Captured 2026-05-05 at phase entry from `docs/manuscript/id-vs-ref-LD.md` after the inline `wc -c`/`md5sum` invocation. Replaces the stale literal `63fd81385590ffc8d23d45a0f0598959` referenced in the W1-PLAN.md `must_haves.truths` block (drift between plan-mode and execute-mode; planner-side md5 was cached against an older snapshot of the manuscript).
  - Lock-at-entry semantic: every task's acceptance criteria asserts md5 unchanged from this value. If a task observes drift, it surfaces as a Rule 1 deviation in the SUMMARY.md.

---

## Decisions

### D-TA-R3-OSF-COVERAGE: OVERRIDDEN at 2026-05-05T13:49:10Z

**Status:** OVERRIDDEN — operator override 2026-05-05; the OSF amendment posting hard gate has been intentionally bypassed for this phase.

**D-TA-R3-OSF-OVERRIDE-RATIONALE:** operator override 2026-05-05 — amendment text committed locally at `.planning/amendments/osf-amendment-r3-2026-05-04.md`; OSF posting deferred; W5 closeout will flag for Cowork-side disclosure decision.

**Pre-execute hard gate disposition:** The original plan required this token to read `COVERED at <timestamp>` before any LSF dispatch fired. The override accepts the deviation (recorded in `.planning/osf_deviations.md`) and permits Task 2 dispatch without OSF-side posting. The amendment text is locally committed and reviewable; W5 closeout Brief will explicitly flag this deviation to Cowork-side for v5 disclosure decision (whether to post the amendment retroactively or fold the disclosure into the v5 cover letter).

**Permitted under OVERRIDDEN disposition:**
- W1 Task 1 (mkdir + CONTEXT.md scaffold + LD pathology inspection) — read-only / local-only; no LSF.
- W1 Task 2 (LSF dispatch of 15 PSD-regularized SuSiE-RSS fits) — fires under override; no further gate beyond explicit-path commit hygiene.
- W1 Task 3 (harvest + branch classification) — deferred to `/gsd-resume-work` (fire-and-forget pattern; harvest is a separate execute pass after `bjobs` clears).

**Verification at override time:**
- `git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l` returns 3 (commits remain ancestors)
- Amendment text on disk: `.planning/amendments/osf-amendment-r3-2026-05-04.md` (committed locally)
- Override entry appended to `.planning/osf_deviations.md` under "Deviations (OSF amendment required)"
- DECISIONS.md row landed: `DEC-2026-05-05-XX: OSF amendment posting deferred for TA-R3 audit-v2-driven phase; operator override; W5 closeout follow-up`

---

### D-TA-R3-W1-BRANCH_PSD_FIRM: BRANCH_PSD_FIRM (Wave 1 outcome)

**Recorded:** 2026-05-06T (Wave 1 Task 3 harvest pass)

**Primary lambda:** 0.01 (smallest lambda where all 3 of bmi, hypertension, stroke per-trait fits converged).

**Per-trait convergence at primary lambda:**

| trait | converged | n_CS | niter |
|---|---|---|---|
| bmi | TRUE | 10 | 221 |
| hypertension | TRUE | 7 | 715 |
| stroke | TRUE | 6 | 264 |
| asthma | TRUE | 0 | 2 |
| t2d | TRUE | 5 | 30 |

**Canonical-pair coloc.susie PP.H4 at primary lambda:**

| pair | PP.H4 | Threshold class |
|---|---|---|
| bmi_vs_hypertension | 1.000000 | SURVIVE_GE_0.8 |
| hypertension_vs_stroke | 1.000000 | SURVIVE_GE_0.8 |
| hypertension_vs_t2d | 1.000000 | SURVIVE_GE_0.8 |

**Detailed numerics:** [results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv](../../../results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv)

**W3 gate implication:** `D-TA-R3-W3-GATE = FIRES`
- FIRM or PARTIAL → W3 fires (R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR)
- COLLAPSE → W3 SKIPPED (anchor itself fails; parity moot; record `D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME`)
- NON_CONVERGE → W3 DEFERRED_TO_TRACK_B (deeper LD-panel-vs-GWAS-cohort mismatch)

**Cowork-side branch (informational; manuscript edits OUT of phase scope):** Per OSF amendment paragraph (c), the manuscript v5 narrative branches:
- **FIRM (this outcome) → SH2B3 anchor empirically supported under regularized LD; report lambda + PSD diagnostic + converged-status disclosure**
- PARTIAL → reframe SH2B3 from Tier-A to Tier-B; revise abstract + discussion
- COLLAPSE → SH2B3 no longer Tier-A; report prior-literature PP=1.0 anchor as not surviving matched-LD with PSD regularization
- NON_CONVERGE → disclose deeper LD-panel-vs-GWAS-cohort mismatch; defer to Track B (in-sample LD via UKB/AoU EUR)

---

### D-TA-R3-W2-BRANCH_R1_STRUCTURAL: BRANCH_R1_STRUCTURAL (Wave 2 outcome)

**Recorded:** 2026-05-06T14:25:00Z

**HEAD ancestors verified:** 069b34f + 7d54183 + 02c4404 (3/3 in `git log` at W2 dispatch time; verified at re-fire start AND post-fire commit time)

**Pre-refire baseline:**

| metric | count |
|---|---|
| total_pair_rows | 37 |
| non_empty_PP.H4_rows (pre-W2, all) | 5 |
| R1_non_empty_PP.H4_rows (pre-W2; the 28 R1 trait-pairs) | 0 / 28 (matches audit-V2 §HQ#2(iii) "28/28 empty" claim) |
| SH2B3_R2_non_empty_PP.H4_rows (pre-W2; the 9 R2 trait-pairs) | 5 / 9 (BMI–HTN, HTN–stroke, HTN–T2D, stroke–T2D, BMI–T2D non-empty; 4 R2 rows structurally collapsed at niter=1000) |
| coloc_summary.tsv md5 (pre-W2) | `558fca45ac37d901028c64429cdecc12` (matches W7 baseline at `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` L2) |

**Post-refire status:**

| metric | count |
|---|---|
| total_pair_rows | 37 (unchanged) |
| non_empty_PP.H4_rows (post-W2, all) | 5 (Δ=0 vs pre-W2) |
| R1_non_empty_PP.H4_rows (post-W2) | **0 / 28 (Δ=0; UNCHANGED from pre-W2 baseline)** |
| SH2B3_R2_non_empty_PP.H4_rows (post-W2; risk register row 4 preservation check) | 5 / 9 (Δ=0; ≥9 floor satisfied at row level — all 9 R2 rows still present in summary) |
| coloc_summary.tsv md5 (post-W2) | `85ab5aa2ca4b54e0edf2a48dc4c61258` (md5 SHIFTED; W5 closeout will append successor row to `md5_baseline.tsv`) |

**Detailed numerics:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv](ta-r3-W2-post_refire_outcome.tsv)

**Per-JSON failure-mode characterization:** All 28 R1 JSONs produced under HEAD code (with the variant-ID-format-fix commits 069b34f + 7d54183 + 02c4404 as ancestors) return `status = "no_signal"` with `n_cs_a = 0` or `n_cs_b = 0` (or both). The variant-ID matcher works correctly — coloc.susie reads pre-fitted SuSiE-RSS objects from `results/fine_mapping/susie/{trait}.{ancestry}.{region}.fit.rds` and returns no_signal because the upstream Layer-1 fits resolve no credible set on at least one trait at that region × ancestry. Layer-2 attrition is therefore upstream of the variant-ID matcher; the falsification test on the cache-staleness alternative does NOT falsify (re-running under HEAD code with all 3 fix commits as ancestors produces 28/28 empty PP, identical to pre-W2 disk state). FTO_16q12 AFR asthma_vs_t2d is a representative case: trait_b (T2D) has n_cs_b=4 credible sets, but trait_a (asthma) has n_cs_a=0 — coloc.susie has no credible-set pair to test even though one side resolves a non-empty CS.

**Cowork-side narrative branch (informational; manuscript edits OUT of phase scope):** Per OSF amendment paragraph (e), the manuscript v5 narrative branches:

- BRANCH_R1_BUG → Layer-2-attrition-under-matched-LD framing empirically refuted; new PP rows reported in manuscript Table 3 with variant-ID-format-fix commit hashes cited as the propagation gap (NOT this outcome)
- **BRANCH_R1_STRUCTURAL (this outcome) → Layer-2-attrition framing empirically supported; the variant-ID-format-fix commits 069b34f + 7d54183 + 02c4404 cited as a falsification test that did not falsify; manuscript Table 3 + Discussion §"Layer-2 colocalization-feasibility yield" + Discussion §"Identity-LD Inflation" framing survives the reviewer-defensible re-application of the fix commits to the full 28-pair set; the "fixes applied to SH2B3 only" reviewer objection is closed (the fixes were re-applied under HEAD code; the empty-PP rows are structural, not propagation gaps).**

**W3 gate implication:** Already resolved by W1 outcome at the upstream gate (`D-TA-R3-W3-GATE = FIRES`, driven by `D-TA-R3-W1-BRANCH_PSD_FIRM`; W3 gate is W1-driven, NOT W2-driven). W2 outcome flows to manuscript narrative ONLY; does NOT change W3 gate disposition. R2 canonical-pair parity at FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 (EUR) proceeds at the next plan independent of W2 result.

**Honest-framing-lock invariant verification:**

| anchor | md5 |
|---|---|
| MANUSCRIPT-MD5-AT-ENTRY (W2) | `2a57c1a061f0c66988a55d1d6600efdf` |
| MANUSCRIPT-MD5-AT-EXIT (W2) | `2a57c1a061f0c66988a55d1d6600efdf` |
| Drift | NONE — lock holds for full Wave 2 (3 atomic commits + .gitignore allowlist edit; manuscript untouched) |

---

### D-TA-R3-W3-GATE: FIRES (driven by W1 = BRANCH_PSD_FIRM)

**Resolved:** 2026-05-06 (Wave 1 Task 3 harvest pass)

**Disposition:** FIRES — W1 returned `BRANCH_PSD_FIRM` at primary lambda=0.01 with all 3 canonical-pair PP.H4 = 1.000000. SH2B3 12q24 EUR qualifies as a comparator anchor under PSD-regularized LD; W3 R2 canonical-pair parity at FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 (EUR) is informative and proceeds per OSF amendment paragraph (f).

---

### D-TA-R3-W4-GATE: PENDING (default DEFERRED_TO_FOOTNOTE; only fires if Cowork-side decides cheap A9 footnote insufficient)

**Status:** PENDING — default disposition is `DEFERRED_TO_FOOTNOTE`.

---

## Reused Existing Substrate

- [src/legacy/region_analysis/scripts/run_susie_rss.R](../../../src/legacy/region_analysis/scripts/run_susie_rss.R) — z-score derivation at line 466 (`subset[, z := BETA / SE]`); fitter pattern reused by W1's new PSD-regularized script
- [config/bsub_wrapper.sh](../../../config/bsub_wrapper.sh) — sets -W per queue (serial=5760 min via `*` default case); W1+W2+W3 use it via the same pattern as ta-sh2b3-W1-PLAN.md
- [.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv](../ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv) — W5 appends successor rows (NOT overwrite)
- Commits in HEAD: `069b34f` (variant-ID matcher in run_qtl_coloc.R), `7d54183` (LD-panel-rsid override in run_susie_rss.R), `02c4404` (max_iterations -> max_iter)
