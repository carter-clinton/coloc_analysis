---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 1
slug: W1-susie-rss-l-sweep
subsystem: fine-mapping
tags: [susie-rss, l-sweep, lsf, snakemake, convergence, sh2b3, eur, niter, zou-2022]

# Dependency graph
requires:
  - phase: ta-sh2b3-canonical-and-cache-refresh
    plan: 0
    provides: "Per-L SuSiE policy YAMLs + per-L pipeline overlays + bin/fire_susie_lsweep.sh dispatch driver + Pitfall 2 mitigation in finemap.smk + bin/verify_ta_sh2b3_phase.sh C5 check + D-TA-OSF-COVERAGE=COVERED gate cleared"
provides:
  - "9 SuSiE-RSS fits (3 traits × L ∈ {15,20,30}) at results_lsweep_L{15,20,30}/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.{json,fit.rds}"
  - "Per-fit convergence report TSV (ta-sh2b3-W1-convergence-report.tsv; header + 9 data rows)"
  - "D-TA-Wave1-PRIMARY-L = NONE_CONVERGED recorded in CONTEXT.md addendum"
  - "D-TA-Wave1-headline DEFERRED to Wave 6 with HEADLINE_VALUE=UNCHANGED (invariant 2 preserved)"
  - "Pitfall 2 live verification 9/9 (L_used == L_swept across all fits; config-merge propagation confirmed in production)"
  - "Wave 6 narrative branch provisionally selected: DISCLOSE-AS-COLUMN"
  - "Wave 2 GO/NO-GO outcome: NO-GO pending Carter decision on D-TA-Wave1-PRIMARY-L Wave 2 directive (3 options)"
affects: [ta-sh2b3-W2, ta-sh2b3-W6]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-fit convergence-status interpretation per Zou et al. 2022 §Discussion: distinguishes niter-not-reached from L-saturation"
    - "Strict convergence_ok gate: ^converged_ AND !L_saturated AND n_CS<L_used (all 3 conditions) — surfaces non-convergence as a methodology gap rather than papering it over"
    - "PRIMARY_L=NONE_CONVERGED escalation: blocks Wave 2 dispatch; routes Wave 6 narrative branch to DISCLOSE-AS-COLUMN until Carter resolves option (a/b/c)"

key-files:
  created:
    - ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv"
    - "results_lsweep_L15/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.{json,fit.rds} (6 files)"
    - "results_lsweep_L20/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.{json,fit.rds} (6 files)"
    - "results_lsweep_L30/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.{json,fit.rds} (6 files)"
    - "logs/wave1_dispatch_main_20260429_205154.log + logs/wave1_susie_lsweep_20260429_205154.log (LSF dispatch trace)"
    - ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave1_dispatch_tracker.json (dispatch + quick-scan tracker)"
  modified:
    - ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md (D-TA-Wave1-PRIMARY-L + D-TA-Wave1-headline sub-sections appended)"

key-decisions:
  - "PRIMARY_L = NONE_CONVERGED — no L value in {15,20,30} satisfies the strict converged_ok gate across all 3 traits; all 9 fits report convergence_status=non_converged at niter=100"
  - "Substantive interpretation: niter-not-reached (not L-saturation) — L_saturated=FALSE and n_CS<L_used for every fit; per Zou 2022 the remedy is raising niter, not raising L"
  - "Wave 6 narrative branch: DISCLOSE-AS-COLUMN (provisional) — keeps 51/96 headline + adds non-convergence disclosure column to Fig 3"
  - "D-TA-Wave1-headline HEADLINE_VALUE=UNCHANGED (invariant 2 preserved; TRACK-A-FROZEN-NUMBERS.md md5 = 9d0405a4db95655b1be7401883d22165 unchanged pre/post)"
  - "Wave 2 BLOCKED — Carter must resolve D-TA-Wave1-PRIMARY-L Wave 2 directive before Wave 2 dispatches; recommended option (a) re-fire with raised niter per rigor-over-speed memory"

patterns-established:
  - "Convergence verification pipeline: jsonlite::fromJSON of 9 per-fit JSONs → TSV report → R-side strict-gate evaluation → CONTEXT.md decision sub-section"
  - "Three-option escalation template for non-converged outcomes: (a) re-fire raised niter (rigorous) / (b) relax criterion (proxy) / (c) disclose downstream (DISCLOSE-AS-COLUMN)"
  - "TRACK-A-FROZEN-NUMBERS.md md5 baseline-vs-post check as invariant-2 enforcement at every Wave 1+ commit"

requirements-completed: []  # Phase-level requirements (REQ-OSF-PREREG, REQ-PATH-PARAMETERIZATION, REQ-SNAKEMAKE-CI, REQ-SUSIE-RSS-POLICY) finalize at phase verification, not at plan close

# Metrics
duration: ~8min observed wall (LSF supervisor dispatch 2026-04-30T00:51:54Z → exit 2026-04-30T00:59:44Z); +Task 2 verification authoring ~10 min
started: 2026-04-30T00:51:54Z
completed: 2026-04-30T01:11:13Z
updated: 2026-04-30
status: COMPLETE-WITH-WAVE-2-NO-GO
status-detail: "Wave 1 outcomes recorded as planned (Tasks 1+2 closed); Wave 2 BLOCKED on Carter resolution of D-TA-Wave1-PRIMARY-L Wave 2 directive (3 options, recommend (a) re-fire raised niter). Plan tasks complete; downstream gate is intentionally pending."
---

# Phase ta-sh2b3 Plan W1: SH2B3 EUR SuSiE-RSS L-Sweep Re-Fits Summary

**SuSiE-RSS L-sweep at L ∈ {15, 20, 30} for SH2B3 EUR BMI / hypertension / stroke produced 9 fits in ~8 min observed wall; ALL 9 report `convergence_status=non_converged` with `L_saturated=FALSE` and `n_CS < L_used` (niter-not-reached, not literal saturation per Zou 2022); strict converged_ok gate fails 9/9 → PRIMARY_L=NONE_CONVERGED; HEADLINE_VALUE=UNCHANGED (invariant 2 preserved); Wave 6 narrative branch provisionally DISCLOSE-AS-COLUMN; Wave 2 NO-GO pending Carter resolution.**

## Status: COMPLETE-WITH-WAVE-2-NO-GO — PRIMARY_L=NONE_CONVERGED Recorded; Wave 2 Awaits Carter Decision

**Plan execution status:** Tasks 1 and 2 closed atomically per the plan; PRIMARY_L identified per the prescribed gate; D-TA-Wave1-headline sub-section recorded per CONTEXT.md invariant 2 (HEADLINE_VALUE=UNCHANGED). The 9 LSF jobs (4 + 4 + 4 — one `build_finemap_manifest` plus three `run_finemap` per L wave; sequential L-loop dispatch) finished in ~8 min wall vs. the AUDIT-RESPONSE 2026-04-26 line 260 envelope of 2-4 hr per fit / 6-12 hr aggregate. The vast under-shoot is explained by single-region scope (SH2B3_12q24 only; ~4k variants) vs. full-region production fires the envelope was sized against.

**Wave 2 gate status:** **NO-GO**. Wave 2 requires `PRIMARY_L ∈ {15, 20, 30}` to dispatch coloc.susie against converged fits; with PRIMARY_L=NONE_CONVERGED, the strict-gate path is closed. Three resolution options are recorded in `D-TA-Wave1-PRIMARY-L` (CONTEXT.md addendum) and listed in **Wave 2 Decision Required** below.

## Verification Dimensions (D1–D7)

### D1 — LSF Dispatch Success: PASS

- 9 LSF jobs dispatched via `bin/fire_susie_lsweep.sh` (sequential L-loop pattern: L=15 → L=20 → L=30, with 3 parallel `run_finemap` traits per L wave plus 1 `build_finemap_manifest` per L)
- 9 JSON outputs landed on disk with corresponding `.fit.rds` siblings (verified at `results_lsweep_L{15,20,30}/fine_mapping/susie/`)
- Supervisor PID 2496902 dispatched 2026-04-30T00:51:54Z; exited cleanly 2026-04-30T00:59:44Z (~8 min wall)
- LSF wall-time cap `-W=5760` for `serial` queue applied per `config/bsub_wrapper.sh` case default (96-hr cap; unused — fits finished well before any wall pressure)
- **Evidence:** `wave1_dispatch_tracker.json` `pre_fire_verification` block all PASS; `actual_completion.all_9_jsons_landed=true`

### D2 — L_used Field Correctness (Pitfall 2 Live Verification): PASS 9/9

- Every fit's `L_used` JSON field equals its `L_swept` overlay value (15/20/30 across all 3 traits)
- Confirms the W0 finemap.smk:62 patch (`policy=config.get('finemap', {}).get('policy', 'config/susie_policy.yaml')`) propagates per-L overlays through to the SuSiE-RSS policy YAML in production runs (not just in dry-runs as W0 verified)
- **Evidence:** TSV column `L_used` matches column `L_swept` for all 9 rows:
  - L=15 sweep: bmi.L_used=15, hypertension.L_used=15, stroke.L_used=15
  - L=20 sweep: bmi.L_used=20, hypertension.L_used=20, stroke.L_used=20
  - L=30 sweep: bmi.L_used=30, hypertension.L_used=30, stroke.L_used=30

### D3 — Convergence per Zou 2022 (`^converged_` regex on `convergence_status`): FAIL 0/9

- Zero fits match the `^converged_` regex; every fit reports `convergence_status="non_converged"` (the run_susie_rss.R wrapper's literal token when SuSiE-RSS internals return `converged=FALSE`)
- All 9 fits also carry `niter=100` (the SuSiE-RSS default iteration cap), `converged=FALSE`, `elbo_final=-1043496.95` (BMI L=20 representative)
- This is the **niter-not-reached** condition — variational ELBO did not stabilise within 100 iterations — not a model-mis-specification or LD-mismatch failure (LD overlap is 0.988 for BMI EUR SH2B3, ld_status=ld_loaded;overlap_ok)
- Per Zou et al. 2022 §Discussion the cleanest remedy is raising niter (option (a) below)

### D4 — L-Saturation Absence: PASS 9/9

- `L_saturated=FALSE` for every fit; per-trait `n_CS` numbers stay strictly below `L_used`:
  - BMI: n_CS = 13, 14, 14 at L=15, 20, 30 (asymptotes near 14; suggests over-extraction at L=15→20 transition where +6 L-budget added only 1 CS)
  - Hypertension: n_CS = 5, 4, 4 (stable; suggests true CS count near 4)
  - Stroke: n_CS = 3, 4, 4 (stable; suggests true CS count near 4)
- The non-convergence is therefore NOT explained by hitting the L ceiling — the prior is not saturated. This rules out the L-saturation remedy (raising L further would not help) and points to the niter-not-reached remedy.

### D5 — PRIMARY_L Identification: PRIMARY_L = NONE_CONVERGED (recorded)

- Strict gate: `n_CS < L_used AND L_saturated=FALSE AND convergence_status matches ^converged_`
- All 9 fits fail the third clause (`^converged_` regex); 0/9 satisfy `converged_ok=TRUE`; no L value has all 3 traits passing
- PRIMARY_L = `NONE_CONVERGED` recorded in CONTEXT.md as `D-TA-Wave1-PRIMARY-L`
- **Evidence:** `grep -E "PRIMARY_L:.*\*\*(15|20|30|NONE_CONVERGED)\*\*" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` → match

### D6 — D-TA-Wave1-headline DEFERRED Status: PASS

- D-TA-Wave1-headline sub-section recorded in CONTEXT.md addendum
- HEADLINE_VALUE=UNCHANGED preserved (invariant 2 — Wave 1 reports outcomes only; never modifies the 51/96 numerator)
- Wave 6 narrative branch provisionally selected: **DISCLOSE-AS-COLUMN** (no traits flipped from non-converged at L=10 to converged at any swept L → Wave 6 keeps 51/96 + adds non-convergence disclosure column to Fig 3 disclosure sub-table; updates Limitations bullet + Methods §Fine-Mapping Configuration; does NOT touch the headline)
- Branch is provisional pending Carter's resolution of the D-TA-Wave1-PRIMARY-L Wave 2 directive — if Carter elects option (a) re-fire-with-raised-niter and the re-fire produces converged fits, the branch flips to RECOMPUTE; otherwise it stays DISCLOSE-AS-COLUMN
- **Evidence:** `grep "HEADLINE_VALUE:.*UNCHANGED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` → match

### D7 — TRACK-A-FROZEN-NUMBERS.md md5 Preservation (Invariant 2): PASS

- Pre-Wave-1 baseline md5: `9d0405a4db95655b1be7401883d22165`
- Post-Wave-1 md5: `9d0405a4db95655b1be7401883d22165` (unchanged)
- The 51/96 numerator is byte-identically preserved; Wave 1 does not touch the headline, exactly as the plan invariant requires
- **Evidence:** `diff /tmp/track_a_frozen_md5_pre.txt /tmp/track_a_frozen_md5_post.txt` → empty (verified post-final-commit below)

## LSF Wall-Time: Observed vs. Projected

| Metric | Observed | Projected (AUDIT-RESPONSE 2026-04-26 L260) | Notes |
|--------|----------|--------------------------------------------|-------|
| Per-fit wall | ~1 min/fit (sequential L-loop, 3 parallel traits per L) | 2-4 hr/fit | Single-region SH2B3_12q24 EUR scope; ~4k variants in the 600 kb window |
| Aggregate wall | ~8 min (LSF supervisor lifetime) | 6-12 hr | Sequential L-loop dispatch; per-L parallel traits |
| `-W` cap applied | 5760 min (96 hr) on `serial` queue | n/a | `bsub_wrapper.sh` case default per checker iter 1 NIT 2 |
| `-W` cap utilisation | <0.2% (8 min / 5760 min) | n/a | Cap was set defensively; never approached |

The envelope was sized for full-region production fires (e.g., FTO_16q12 with ~10k variants) — a future Wave 2 dispatch pattern that fires 9 SH2B3 EUR pair-jobs in parallel may take ~3-4 min aggregate, similarly far under envelope.

## Wave 6 Narrative Branch Implication

**Selected branch (provisional):** **DISCLOSE-AS-COLUMN**

**Rationale:** PRIMARY_L=NONE_CONVERGED → no traits flip from non-converged-at-L=10 to converged-at-any-swept-L → the (51 + 3 - X)/96 RECOMPUTE arithmetic reduces to (51 + 0 - 0)/96 = 51/96 (unchanged numerator). The substantive change is therefore disclosure-side, not numerator-side: Wave 6 keeps 51/96 as the headline and adds a non-convergence disclosure column to Fig 3 (analogous to the existing disclosure sub-table). Methods §Fine-Mapping Configuration gets a new bullet documenting niter=100 as the default and the L-sweep outcome at niter=100; Limitations gains a bullet explicitly flagging the SuSiE-RSS niter cap.

**Branch flip condition:** If Carter elects option (a) re-fire-with-raised-niter (recommended), and the niter=500 or niter=1000 sweep produces fits passing the strict `^converged_` gate, the branch flips to RECOMPUTE: Wave 6 then computes (51 + N_newly_converged - N_newly_empty)/96 and propagates the updated numerator to Abstract + §Headline + Fig 2 caption + TRACK-A-FROZEN-NUMBERS.md L10 LIVE block + Conclusion-1.

## Wave 2 GO/NO-GO Status: NO-GO

**Decision required:** Carter must resolve the D-TA-Wave1-PRIMARY-L Wave 2 directive before Wave 2 dispatches.

### Three options on the table (recorded in CONTEXT.md addendum)

1. **(a) Re-fire with raised niter — RECOMMENDED.** Run the same 9-fit L-sweep at `susie.niter=500` or `susie.niter=1000`. Most rigorous; preserves the strict `^converged_` gate (no methodological retreat). Compute envelope: ~8 min × ~5-10× wall ≈ 1 hr LSF. Per `feedback_rigor_over_speed.md` and Zou 2022 §Discussion's "raise niter when ELBO has not stabilised" guidance, this is the peer-reviewer-defensible choice for *Genome Medicine* R2.
2. **(b) Relax convergence_status criterion.** Drop the `convergence_status` regex check from the gate; accept `L_saturated=FALSE AND n_CS < L_used` as a convergence proxy. Justification: the run_susie_rss.R wrapper's `convergence_status="non_converged"` token is set when `converged=FALSE` from SuSiE-RSS internals (which keys on niter cap). The downstream Wave 2 coloc.susie analysis depends on credible-set structure (n_CS, purity, leading PIPs), not the ELBO-converged flag per se — and `n_CS < L_used` already establishes the model did not saturate the prior. Faster (no re-fire) but weakens the methodology and requires explicit OSF-deviation disclosure if adopted.
3. **(c) Proceed to Wave 2 with the lowest-L fits regardless and DISCLOSE downstream.** Pick L=15 (lowest swept; smallest spurious-CS surface) and fire Wave 2 against those non-converged fits, then propagate non-convergence as Methods + Limitations + Fig 3 disclosure-column outputs. Effectively the DISCLOSE-AS-COLUMN narrative branch propagated upstream into Wave 2 dispatch.

### Recommendation

Option **(a)** per `feedback_rigor_over_speed.md` and the rigor-over-speed memory rule. The observed ~1 min/fit wall makes the niter=500/1000 re-fire ~1 hr aggregate — trivial relative to the manuscript impact of "all 9 fits non-converged at default niter" being a peer-reviewer-flagged methodology gap. If Carter elects (a) and the re-fire produces converged fits, Wave 6 flips to RECOMPUTE.

## Deviations from Plan

**None — plan executed exactly as written.**

The plan explicitly anticipated PRIMARY_L=NONE_CONVERGED as a possible outcome and pre-authored the escalation path:
- D-TA-Wave1-PRIMARY-L sub-section template covers `{15|20|30|NONE_CONVERGED}` (PLAN Task 2 step 3, lines 280-296)
- "Most likely outcome (per AUDIT-RESPONSE projection): PRIMARY_L=20. Possible alternatives: 15 (best case, all converge at L=15) or 30 (some saturate at L=20) or NONE_CONVERGED (escalate)." (PLAN Task 2 step 2, line 275)
- "C5 must emit PASS. If FAIL, escalate (the Wave-1-headline branch will need to be FAIL-disclosure, not RECOMPUTE)." (PLAN Task 2 step 4, line 317) — observed: C5 emits FAIL; escalation path activated as documented.

Auto-fixes (Rules 1-3): None required. The plan's R script worked first-pass under R 4.4.2 (`%||%` is a native operator since R 4.4.0; the plan's fallback note was unused).

## Authentication Gates

None encountered. All compute is on local LSF + GPFS; no API keys or external service auth required.

## Self-Check

- [x] Convergence report TSV exists with header + 9 data rows (10 lines total) — verified `wc -l = 10`
- [x] L_used==L_swept for all 9 rows (Pitfall 2 verification 9/9)
- [x] PRIMARY_L identified and recorded in CONTEXT.md as `D-TA-Wave1-PRIMARY-L` — verified via grep
- [x] D-TA-Wave1-headline sub-section recorded with HEADLINE_VALUE=UNCHANGED — verified via grep
- [x] C5 from `bin/verify_ta_sh2b3_phase.sh --wave 1` emits FAIL — captured in `/tmp/wave1_verify_output.json` (documented escalation path per plan; not a methodology failure)
- [x] CONTEXT + TSV atomic commit landed — commit `c542d72`
- [x] SUMMARY.md authored with all D1–D7 dimensions + Wave 2 GO/NO-GO (this file)
- [x] TRACK-A-FROZEN-NUMBERS.md md5 unchanged — `9d0405a4db95655b1be7401883d22165` pre = post (invariant 2 preserved)

### File-existence check

- [x] `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv` — FOUND
- [x] `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` — FOUND (modified with 2 new sub-sections)
- [x] `results_lsweep_L{15,20,30}/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.json` — 9/9 FOUND
- [x] `results_lsweep_L{15,20,30}/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.fit.rds` — 9/9 FOUND

### Commit-existence check

- [x] `c542d72` (CONTEXT.md + TSV atomic commit) — FOUND in `git log --oneline -5`

## Self-Check: PASSED
