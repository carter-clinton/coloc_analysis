---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 3
slug: W3-checkpoint-human-verify
status: COMPLETE
created: 2026-04-30
updated: 2026-04-30
---

# Wave 3 — checkpoint:human-verify outcome-branch (Wave 3)

## Outcome

**Branch selected:** `BRANCH_C_SURVIVE` (recorded via `/gsd-execute-phase` resume signal "c").

**Decision token:** `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` (CONTEXT.md addendum, commit `9323c5d`).

**Wave 6 narrative branch:** "SH2B3 anchor flips from collapse to validated" (per W3 PLAN branch C template).

## Wave 2 disk-number evidence presented to Carter

| Pair | PP.H4 | Threshold class |
|------|-------|----------------|
| **bmi_vs_hypertension (CANONICAL)** | **1.0** | **SURVIVE_GE_0.8** (rs3184504, nsnps=168) |
| **hypertension_vs_stroke (CANONICAL)** | **1.0** | **SURVIVE_GE_0.8** |
| hypertension_vs_t2d | 1.0 | SURVIVE_GE_0.8 |
| bmi_vs_t2d | 4.3081e-27 | COLLAPSE_BELOW_0.5 (PP.H3=1) |
| stroke_vs_t2d | 0 | COLLAPSE_BELOW_0.5 (PP.H3=0.9976) |
| asthma_vs_bmi / asthma_vs_hypertension / asthma_vs_stroke | NA | MISSING (no_signal; n_cs_a=0) |
| bmi_vs_stroke | NA | MISSING (no_posterior; 39 pairs computed) |

BMI–HTN PP.H4 = 1.0 ≫ 0.8 → unambiguous BRANCH_C.

## Substantive interpretation

The canonical SH2B3 BMI–HTN colocalization is **robust to reference-LD pathology**. Even with W1.5-audit-documented panel deficiencies (weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage) AND non-converged SuSiE-RSS Δ-ELBO (post-bug-fix at honest niter=1000), the canonical claim still produces PP.H4 = 1.0 at rs3184504. This is a positive result for the literature and a strong test for reference-LD-induced inflation: the original Stage 2 expectation (collapse under matched-LD) is **inverted** at SH2B3.

## D-TA-Wave3-thresholds applied

Per [W3 PLAN][1] line 70 thresholds:
- (a) BRANCH_A_COLLAPSE: PP.H4 < 0.5
- (b) BRANCH_B_PARTIAL: PP.H4 ∈ [0.5, 0.8)
- (c) BRANCH_C_SURVIVE: PP.H4 ≥ 0.8 ← **selected**

[1]: ta-sh2b3-W3-checkpoint-human-verify-PLAN.md

## Self-Check

- [x] **C8** — Wave 2 PP.H4 outcomes presented + Carter selected branch + decision recorded as `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` in CONTEXT.md addendum (under `<decisions>` block, after `D-TA-Wave2-outcomes`).
- [x] Atomic commit landed (`9323c5d`).
- [x] No narrative writes in Wave 3 (gate is decision-only; invariant 2 preserved). `docs/manuscript/track_a_pivot.md` md5 = `28be687fc2c5c48f1234f88461c5f4e9` (unchanged across W3).
- [x] `TRACK-A-FROZEN-NUMBERS.md` md5 = `9d0405a4db95655b1be7401883d22165` (unchanged across W3).
- [x] PLAN automated verification PASSES: `grep -qE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)"` returns ≥ 1 hit + no manuscript modifications in HEAD~1..HEAD.

## Wave 4 readiness

`{wave3_branch} = BRANCH_C_SURVIVE` is now bound for Wave 6 narrative substitution. Wave 4 (cache invalidation + Snakemake re-fire) is independent of `{wave3_branch}` (depends only on D-TA-04-DIAGNOSTIC=RSID + W0 foundations); Wave 4 is **ready to dispatch**.

## Open framing question (deferred to Wave 6)

Carter has not yet selected a Wave 6 §Headline framing strategy from the three offered:
1. Lead with the survival result (BMI–HTN survives under LD-pathological reference)
2. Lead with the W1.5 panel-pathology audit (LD reference is broken; downstream non-convergence is consequential)
3. Pair both in §Headline + §Methods + Fig 3 disclosure-column (default agent suggestion)

Recorded in `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` for Wave 6 to consume; not blocking.
