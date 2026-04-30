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
  - "9 SuSiE-RSS fits (3 traits × L ∈ {15,20,30}) at results_lsweep_L{15,20,30}/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.{json,fit.rds} (V2 niter=1000; v1 niter=100 preserved at .preNiter500.bak.20260429_213644 + buggy-attempt-v2-pre-fix preserved at .preFix.bak.20260429_215312)"
  - "Per-fit convergence report TSV V2 (ta-sh2b3-W1-convergence-report.tsv; header + 9 data rows; niter=1000 column added); v1 preserved at ta-sh2b3-W1-convergence-report-niter100.tsv"
  - "D-TA-Wave1-PRIMARY-L = NONE_CONVERGED recorded in CONTEXT.md addendum (v1); D-TA-Wave1-PRIMARY-L-V2 also = NONE_CONVERGED recorded after option-a re-fire"
  - "D-TA-Wave1-headline DEFERRED to Wave 6 with HEADLINE_VALUE=UNCHANGED (invariant 2 preserved across BOTH fires)"
  - "D-TA-Wave1-headline-V2 records V2 outcome locking DISCLOSE-AS-COLUMN narrative branch (was provisional in v1)"
  - "Pre-existing run_susie_rss.R argument-naming bug discovered + fixed mid-task (commit 02c4404); affects all SuSiE-RSS fits in the project's history (silent niter=100 cap regardless of policy YAML)"
  - "Pitfall 2 live verification 9/9 (L_used == L_swept across all fits; config-merge propagation confirmed in production for both v1 and V2)"
  - "Wave 6 narrative branch LOCKED: DISCLOSE-AS-COLUMN (V2 outcome resolves v1 provisional)"
  - "Wave 2 GO/NO-GO outcome: STILL NO-GO after V2; Carter option-a exhausted; pending escalation to option (b)/(c)/(d)"
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
  - "v1 (niter=100): PRIMARY_L = NONE_CONVERGED — no L value satisfies the strict converged_ok gate; v1 attributed this to niter-not-reached at niter=100 cap"
  - "v1 (niter=100) substantive interpretation: niter-not-reached (not L-saturation) — L_saturated=FALSE and n_CS<L_used for every fit; per Zou 2022 the remedy is raising niter, not raising L"
  - "v1 Wave 6 narrative branch: DISCLOSE-AS-COLUMN (provisional, pending Carter option-a outcome)"
  - "V2 (niter=500/1000, post-bug-fix): PRIMARY_L = NONE_CONVERGED unchanged — but 9/9 fits at niter=1000 still non-converged, falsifying v1 niter-not-reached hypothesis"
  - "V2 substantive interpretation: LD-mismatch instability (NOT niter-not-reached) — full retry-ladder exhausted at niter=1000 with regularized LD; n_CS stable across niter sweep; susieR diagnostic warns 'check consistency between summary statistics and LD matrix'"
  - "V2 pre-existing bug discovered + fixed: run_susie_rss.R:38 was passing max_iterations to susie_rss (which has no such formal); susie_suff_stat default max_iter=100 was silently used regardless of policy YAML; commit 02c4404 corrects to max_iter=max_it"
  - "V2 Wave 6 narrative branch: DISCLOSE-AS-COLUMN LOCKED (was provisional in v1; V2 falsification of niter remedy locks the disclosure path)"
  - "V2 Wave 2 BLOCKED — Carter option-a exhausted; remaining options (b) relax criterion, (c) DISCLOSE-AS-COLUMN at lowest-L, or new (d) investigate LD-mismatch"
  - "D-TA-Wave1-headline HEADLINE_VALUE=UNCHANGED (invariant 2 preserved across BOTH fires; TRACK-A-FROZEN-NUMBERS.md md5 = 9d0405a4db95655b1be7401883d22165 unchanged)"

patterns-established:
  - "Convergence verification pipeline: jsonlite::fromJSON of 9 per-fit JSONs → TSV report → R-side strict-gate evaluation → CONTEXT.md decision sub-section"
  - "Three-option escalation template for non-converged outcomes: (a) re-fire raised niter (rigorous) / (b) relax criterion (proxy) / (c) disclose downstream (DISCLOSE-AS-COLUMN)"
  - "TRACK-A-FROZEN-NUMBERS.md md5 baseline-vs-post check as invariant-2 enforcement at every Wave 1+ commit"

requirements-completed: []  # Phase-level requirements (REQ-OSF-PREREG, REQ-PATH-PARAMETERIZATION, REQ-SNAKEMAKE-CI, REQ-SUSIE-RSS-POLICY) finalize at phase verification, not at plan close

# Metrics
duration: ~8min observed wall v1 (LSF supervisor dispatch 2026-04-30T00:51:54Z → exit 2026-04-30T00:59:44Z); +Task 2 verification authoring ~10 min; +V2 re-fire ~35min wall (2026-04-30T02:26:04Z dispatch → 2026-04-30T03:01:39Z exit) + bug-discovery + bug-fix + V2 verification authoring ~30 min
started: 2026-04-30T00:51:54Z
completed: 2026-04-30T01:11:13Z (v1); 2026-04-30T03:01:39Z (V2 re-fire complete)
updated: 2026-04-29
status: COMPLETE-WITH-WAVE-2-NO-GO-V2
status-detail: "v1 outcomes recorded as planned (Tasks 1+2 closed; commits c542d72+214e04f). V2 re-fire (Carter option-a) executed 2026-04-29: max_iter raised 100/200->500/1000 (commit 9c87157); pre-existing run_susie_rss.R argument-naming bug surfaced + auto-fixed (commit 02c4404); 9/9 fits re-fired at niter=1000 (full retry ladder exhausted) STILL non-converged, falsifying v1 niter-not-reached hypothesis. PRIMARY_L (V2)=NONE_CONVERGED. Wave 6 narrative branch DISCLOSE-AS-COLUMN now LOCKED (was provisional). Wave 2 BLOCKED on Carter escalation to option (b)/(c) or new option (d) LD-mismatch investigation. TRACK-A-FROZEN-NUMBERS.md md5=9d0405a4db95655b1be7401883d22165 invariant preserved across both fires."
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

---

## Re-fire (niter=500/1000) outcome — Carter option-a — V2

**Re-fire fired:** 2026-04-29 by `bin/fire_susie_lsweep.sh` after Carter selected option (a) from the W1 GO/NO-GO checkpoint per `feedback_rigor_over_speed.md`. Re-fire is in-place on the original Wave 1 plan (Plan counter unchanged at 1/8); represents a tuning-parameter + bug-fix iteration on the same plan, not a new plan.

**Wall sequence (V2):**
- 21:37:24 — config/susie_policy_L{15,20,30}.yaml patched (max_iter_primary 100→500, max_iter_retry 200→1000); commit `9c87157`
- 21:38:24 → 21:45:21 — first re-fire attempt (supervisor PID 2631034, dispatch TS=20260429_213824, ~7 min wall) PRODUCED BUGGY OUTPUT (all niter=100 with n_CS values byte-identical to v1)
- 21:48:00 — argument-naming bug isolated; root-cause analysis identified `max_iterations` mis-named (susieR::susie_rss has no `max_iterations` formal — forwards `...` to susie_suff_stat whose iteration cap is `max_iter` default 100)
- 21:51:00 — Rule 1 auto-fix applied to `src/legacy/region_analysis/scripts/run_susie_rss.R:38`; commit `02c4404`
- 21:53:12 — buggy V2 attempt outputs preserved at `results_lsweep_L*.preFix.bak.20260429_215312/`
- 21:53:21 → 21:58 — second re-fire attempt (supervisor PID 2678661, dispatch TS=20260429_215321) — supervisor hung at 3/4 of L=15 wave because LSF transient infrastructure failure (job 67759 EXIT: "Cannot open your job file: /home/ckclinto/.lsbatch/1777514043.67759 — Exited.") + snakemake stalled waiting on a job LSF had killed (Rule 3 auto-fix scope: hung supervisor blocks task)
- 22:24:34 — hung supervisor + snakemake child SIGKILL'd; .snakemake/locks/ unlocked via `snakemake --unlock`
- 22:26:04 → 23:01:39 — third re-fire attempt (supervisor PID 2747125, dispatch TS=20260429_215321 — re-using the same dispatch TS), idempotent rerun via Snakemake's `--rerun-incomplete` covered remaining 7 fits (1 L=15 stroke + 3 L=20 + 3 L=30); ~35 min wall
- 23:04 — V2 convergence verification authored; CONTEXT.md V2 sub-sections appended; commit `c428d2c`

**Pre-fire Pitfall 2 dry-run (V2):** PASS — Snakemake dry-run confirmed `config/susie_policy_L15.yaml` (the patched niter=500/1000 file) is named as the policy input for `run_finemap`. Config-merge propagation works at production scale.

**Per-fit niter=500/1000 outcomes (V2 TSV, niter=1000 across all 9 fits — full retry-ladder exhausted):**

| trait | L=15 n_CS | L=20 n_CS | L=30 n_CS | converged_ok | L_saturated |
|-------|-----------|-----------|-----------|--------------|-------------|
| bmi | 13 (=v1) | **15** (v1: 14, +1 CS) | **15** (v1: 14, +1 CS) | FALSE 9/9 | FALSE 9/9 |
| hypertension | 5 (=v1) | 4 (=v1) | 4 (=v1) | FALSE 9/9 | FALSE 9/9 |
| stroke | 3 (=v1) | 4 (=v1) | 4 (=v1) | FALSE 9/9 | FALSE 9/9 |

**PRIMARY_L (V2):** **NONE_CONVERGED** — same outcome as v1 by name, but materially stronger in evidence (niter ladder genuinely exhausted, not falsely capped at 100).

**D1–D7 dimensions (V2 — only D3, D5, D6 and ladder-budget descriptors flip; D1, D2, D4, D7 unchanged):**

- **D1 LSF Dispatch Success (V2):** PASS — 9 LSF jobs dispatched + completed across 3 fire attempts (1 transient LSF infrastructure failure at L=15 stroke jobid 67759 recovered idempotently via `--rerun-incomplete`); 9 JSON outputs landed on disk
- **D2 L_used Field Correctness (V2):** PASS 9/9 — Pitfall 2 propagation verified again at niter=1000 production scale
- **D3 Convergence per Zou 2022 (V2):** FAIL 0/9 — but the V2 failure mode is materially different from v1: the IBSS algorithm now genuinely runs to niter=1000 with regularized LD before failing, rather than being capped at 100 by the silent argument-naming bug. The susieR runtime warnings explicitly cite "IBSS algorithm did not converge in 1000 iterations!" + "WARNING: matrix R is not positive semidefinite" — diagnostic of LD-mismatch, NOT niter-not-reached
- **D4 L-Saturation Absence (V2):** PASS 9/9 — `L_saturated=FALSE` and `n_CS < L_used` for every fit (BMI's 13/15/15 still well below 15/20/30 ceilings; hypertension 5/4/4 stable; stroke 3/4/4 stable)
- **D5 PRIMARY_L Identification (V2):** PRIMARY_L=NONE_CONVERGED — recorded in CONTEXT.md as `D-TA-Wave1-PRIMARY-L-V2`
- **D6 D-TA-Wave1-headline DEFERRED Status (V2):** PASS — `D-TA-Wave1-headline-V2` recorded with HEADLINE_VALUE=UNCHANGED (invariant 2 preserved); Wave 6 narrative branch DISCLOSE-AS-COLUMN now LOCKED (was provisional in v1)
- **D7 TRACK-A-FROZEN-NUMBERS.md md5 Preservation (V2):** PASS — pre-V2-re-fire md5 `9d0405a4db95655b1be7401883d22165` byte-identical post-V2-final-commit (verified via `diff /tmp/track_a_frozen_md5_pre_v2.txt /tmp/track_a_frozen_md5_post_v2.txt` empty)

**Substantive interpretation (V2 supersedes v1):** v1 hypothesized SuSiE-RSS was hitting the niter=100 cap and the remedy was raising niter; V2 falsifies this. Even at niter=1000 with the regularized-LD retry, ELBO does not stabilize. n_CS and L_saturated stay nearly invariant across the niter sweep (BMI L=20/30 picks up +1 CS at L=20 and L=30 respectively; the rest are byte-identical). The most likely remaining explanation is **LD-mismatch instability** between the 1000G EUR LD reference and the harmonized sumstats at SH2B3_12q24, surfaced both in the susieR diagnostic message and in the per-fit `WARNING: matrix R is not positive semidefinite` runtime stderr. SH2B3_12q24 is in a Stage 2 admissible (non-fallback) region, but ELBO-instability is a known LD-reference-quality signature per Benner et al. 2017 AJHG 101:539–551 (the H3 dose-response figure block in `TRACK-A-FROZEN-NUMBERS.md` already records that 33/60 = 55% of EUR Stage 2 fits sit below the Benner `ld_overlap_fraction = 0.5` threshold).

**Wave 6 narrative branch (V2):** **DISCLOSE-AS-COLUMN — LOCKED.**

Wave 6 keeps 51/96 as the headline. Methods §Fine-Mapping Configuration gains a sub-section documenting the V2 retry-ladder exhaustion + the pre-existing argument-naming bug + the LD-mismatch interpretation. Limitations gains a bullet flagging SuSiE-RSS ELBO-instability at SH2B3_12q24 EUR under the 1000G EUR LD reference. Fig 3 disclosure column documents the per-trait non-convergence at the V2 niter=1000 budget. The (51 + 3 - X)/96 RECOMPUTE arithmetic is moot under V2 (X=0 newly converged → numerator unchanged at 51); the substantive change is disclosure-side, not numerator-side.

**Wave 2 GO/NO-GO (V2):** **STILL NO-GO.**

The strict `^converged_` gate path remains closed; Carter's option (a) is now exhausted (the rigorous rigor-over-speed remedy did not flip the outcome — it ruled out niter-not-reached as the cause). Three paths forward remain (recorded in `D-TA-Wave1-PRIMARY-L-V2`):
- (b) Relax convergence_status criterion (accept `L_saturated=FALSE AND n_CS < L_used` as a convergence proxy; explicit OSF-deviation disclosure).
- (c) Proceed with lowest-L fits + DISCLOSE downstream (DISCLOSE-AS-COLUMN propagated upstream into Wave 2 dispatch).
- (d) NEW — Investigate LD-mismatch as the substantive cause; re-build / re-load 1000G EUR LD via the full per-region pipeline, OR test SH2B3_12q24 with an alternative LD reference. Most rigorous reading per `feedback_rigor_over_speed.md` but requires Wave 0-level infrastructure work (out of W1 scope; would be a NEW wave in a follow-up plan).

## Deviations from Plan (V2 re-fire)

### Auto-fixed Issues

**1. [Rule 1 - Bug] Pre-existing argument-naming bug in run_susie_rss.R retry-ladder helper**
- **Found during:** V2 re-fire Step 7 (post-fire `niter` field inspection on the buggy first attempt revealed niter=100 in all 9 fits despite the patched policy YAMLs setting max_iter_primary=500/max_iter_retry=1000)
- **Issue:** `run_susie_with_ladder()` at `src/legacy/region_analysis/scripts/run_susie_rss.R:38` was passing `max_iterations = max_it` to `susieR::susie_rss()`. susieR 0.14.2's `susie_rss` has no `max_iterations` formal — it forwards `...` to `susie_suff_stat()`, whose iteration cap is named `max_iter` (default 100). The mis-named argument was silently swallowed by `...` and ignored; every SuSiE-RSS fit in the project's history has been running with susie_suff_stat's default max_iter=100 regardless of any policy YAML setting. This pre-dates the ta-sh2b3 phase by an unknown amount.
- **Fix:** Renamed the argument: `max_iterations = max_it` → `max_iter = max_it`. Added an in-line comment block explaining the formal-name mismatch + the discovery context. Verified against `susieR::susie_rss` and `susieR::susie_suff_stat` formals in la_multitrait_r conda env.
- **Files modified:** `src/legacy/region_analysis/scripts/run_susie_rss.R` (1 line + 7-line explanatory comment block)
- **Commit:** `02c4404` (fix(ta-sh2b3, W1): max_iterations -> max_iter in susie_rss call)
- **Scope justification:** Directly blocks the current task — Carter's option-a re-fire was meaningless without the cap actually being lifted. The bug surfaced because we were the first task to depend on the cap value. Methods §Fine-Mapping Configuration prose must update for Wave 6 to reflect that "niter=100 default" was the *bug-default*, not an honest niter=100 outcome.

**2. [Rule 3 - Blocking] Hung supervisor after transient LSF infrastructure failure**
- **Found during:** V2 re-fire Step 6 (post-fix re-fire monitoring; supervisor PID 2678661 stalled at "3 of 4 steps (75%) done" indefinitely after L=15 stroke jobid 67759 hit `Cannot open your job file: /home/ckclinto/.lsbatch/1777514043.67759 — Exited.`)
- **Issue:** LSF infrastructure-level transient failure on a single job; Snakemake's cluster_lsf profile polls for `*.jobfinished` / `*.jobfailed` flag files and did not reliably detect the LSF EXIT, leaving the supervisor stuck waiting indefinitely
- **Fix:** SIGKILL'd the hung supervisor + snakemake child; `snakemake --unlock` cleared stale `.snakemake/locks/` files; re-fired via the same `bin/fire_susie_lsweep.sh` (Snakemake's `--rerun-incomplete` covered the remaining 7 fits idempotently; supervisor PID 2747125 ran to clean exit at 23:01:39)
- **Files modified:** none (transient infra issue; runtime workaround)
- **Commits:** none (no code change)
- **Scope justification:** Directly blocks the current task; the LSF failure is a known transient (`/home/ckclinto/.lsbatch/` NFS hiccup, consistent with `system_codex_tmp_redirect.md` memory which already documents `/home/ckclinto` quota/access fragility on this cluster)

### OSF deviations log entries (Wave 7 closeout consumes these)

1. **niter raise 100/200 → 500/1000** (tuning-parameter change; pre-registered "SuSiE-RSS" wording preserves the algorithm; commit `9c87157`)
2. **Pre-existing argument-naming bug fix in run_susie_rss.R** (code-level fix; reveals v1 niter=100 was bug-default not honest; affects how Methods §Fine-Mapping Configuration describes the iteration policy; commit `02c4404`)

## V2 Self-Check

- [x] Three per-L policy YAMLs patched: max_iter_primary 100→500, max_iter_retry 200→1000 — verified `grep -E "max_iter_primary|max_iter_retry" config/susie_policy_L{15,20,30}.yaml` shows 500/1000 across all 3
- [x] Three .preNiter500.bak.20260429_213644.yaml backup files preserve niter=100 originals — verified `ls -la config/susie_policy_L*.preNiter500.bak.20260429_213644.yaml` shows 3 files
- [x] Niter-100 fit outputs preserved at `results_lsweep_L*.preNiter500.bak.20260429_213644/` — verified `ls -d results_lsweep_L*.preNiter500.bak.20260429_213644/` shows 3 dirs
- [x] Bug-revealing buggy-V2-pre-fix outputs preserved at `results_lsweep_L*.preFix.bak.20260429_215312/` (audit traceability) — verified `ls -d results_lsweep_L*.preFix.bak.20260429_215312/` shows 3 dirs
- [x] YAML patch atomic commit landed — `9c87157` (verified via `git log --oneline | head`)
- [x] Bug-fix atomic commit landed — `02c4404`
- [x] Pitfall 2 dry-run confirmed config-merge propagation at production scale (V2)
- [x] Re-fire fired via nohup; supervisor PID 2747125 exited cleanly at 23:01:39
- [x] All 9 expected JSONs present on disk — verified `ls results_lsweep_L{15,20,30}/fine_mapping/susie/*.json | wc -l = 9`
- [x] All 9 .fit.rds siblings present — verified `ls results_lsweep_L{15,20,30}/fine_mapping/susie/*.fit.rds | wc -l = 9`
- [x] All 9 fits report `niter=1000` (full retry-ladder exhausted; not the v1 false niter=100)
- [x] V1 TSV preserved at `ta-sh2b3-W1-convergence-report-niter100.tsv`; new V2 TSV at canonical name `ta-sh2b3-W1-convergence-report.tsv`
- [x] D-TA-Wave1-PRIMARY-L-V2 + D-TA-Wave1-headline-V2 sub-sections appended to CONTEXT.md (NOT modifying v1 sub-sections; preserved historical record)
- [x] CONTEXT + V2 TSV + preserved-v1 TSV atomic commit landed — `c428d2c`
- [x] SUMMARY.md updated in-place with new "Re-fire (niter=500/1000) outcome" section (NOT modifying v1 sections)
- [x] TRACK-A-FROZEN-NUMBERS.md md5 invariant preserved across V2 re-fire — `9d0405a4db95655b1be7401883d22165` byte-identical pre/post (will be re-verified in Step 13)
- [x] C5 verification harness output captured: PRIMARY_L=NONE_CONVERGED → FAIL (documented escalation path); PRIMARY_L=15 → FAIL detail per-trait (`/tmp/wave1_verify_v2_*.json`)

## V2 Self-Check: PASSED
