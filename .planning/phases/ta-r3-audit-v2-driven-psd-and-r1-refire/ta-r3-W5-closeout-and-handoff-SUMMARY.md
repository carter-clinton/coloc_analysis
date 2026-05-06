---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 5
slug: W5-closeout-and-handoff
status: DONE
subsystem: track-a-audit-driven-re-analysis
tags: [audit-v2-driven, w5-closeout, phase-final, cowork-handoff, osf-override-disclosure, md5-baseline-successor-rows, verification-d1-d13, honest-framing-lock]
requires:
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (W1-W4 outcome tokens)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W{1,2,3,4}-*-SUMMARY.md (4 prior-wave SUMMARYs)
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (W7 baseline; append-only per Pitfall 5)
  - .planning/amendments/osf-amendment-r3-2026-05-04.md (paste-ready amendment text; OSF web-UI posting OVERRIDDEN)
  - .planning/osf_deviations.md (OSF override deviation log)
  - docs/manuscript/id-vs-ref-LD.md (honest-framing-lock manuscript; md5 2a57c1a061f0c66988a55d1d6600efdf at entry = exit)
provides:
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md (D1-D13 PASS/WARN/FAIL JSON evidence; 12 PASS + 1 WARN at D9 OSF override)
  - .planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md (Cowork-side handoff brief; phase summary + decision tokens + commit hashes + LSF job IDs + md5 invariants + Cowork-side TODO list)
  - .planning/quick/260506-epz-ta-r3-cowork-handoff/STATE.md (handoff scaffold state for next Cowork session)
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (8 ta-r3 successor rows appended; W7 baseline preserved)
  - .planning/osf_deviations.md (W5 closeout entry consolidating override; surfaces (a)/(b) decision paths)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W5-PHASE-CLOSURE block appended)
  - .planning/STATE.md (frontmatter stopped_at + last_updated + last_activity refreshed)
  - .planning/ROADMAP.md (Track-A-R3 status COMPLETE; 5 PLAN.md files enumerated)
affects:
  - Cowork-side v5 *Genome Medicine* submission session — receives substrate for A1-A9 manuscript edits + bundle ship + OSF outcome-branch follow-up update + (per Disclosure decision) retroactive OSF posting OR v5-cover-letter pre-registration-timing limitation
tech-stack:
  added: []
  patterns:
    - md5_baseline.tsv successor row append-only (Pitfall 5; never overwrite W7 baseline)
    - VERIFICATION.md PASS/WARN/FAIL JSON-style evidence per dimension (mirrors ta-sh2b3-VALIDATION.md C-row table; sibling pattern with {00,01,05,09,m1,m2,m3}-VERIFICATION.md)
    - Cowork-side handoff brief (informational handoff; phase commit range + LSF job IDs + md5 invariants + artifact paths + TODO list)
    - D9 WARN dimension surfacing OSF override for downstream Cowork-side disclosure routing decision (rigor-defensible (a)/(b) paths enumerated)
    - Honest-framing-lock invariant verification at every wave gate AND phase entry/exit (manuscript md5 byte-identical end-to-end)
    - Multi-terminal git staging discipline (explicit paths only; never `git add .` / `-A`)
key-files:
  created:
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md
    - .planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md
    - .planning/quick/260506-epz-ta-r3-cowork-handoff/STATE.md
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W5-closeout-and-handoff-SUMMARY.md (this file)
  modified:
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (8 ta-r3 successor rows appended; 30 -> 38 lines; W7 baseline rows preserved verbatim per Pitfall 5)
    - .planning/osf_deviations.md (W5 closeout entry consolidating OSF override; surfaces 2 rigor-defensible disclosure paths for Cowork side)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W5-PHASE-CLOSURE block appended)
    - .planning/STATE.md (stopped_at + last_updated + last_activity refreshed; phase-complete state with all 5 wave outcomes summarized)
    - .planning/ROADMAP.md (Track-A-R3 status: scaffolded -> COMPLETE; Plans line enumerates 5 PLAN.md files)
  untouched_critical:
    - docs/manuscript/id-vs-ref-LD.md (md5 2a57c1a061f0c66988a55d1d6600efdf at entry = exit; honest-framing-lock invariant)
    - results/qtl_coloc/tier_assignments.tsv (md5 17ff46db... UNCHANGED; W4 DEFERRED path; no successor row needed)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md (amendment text on disk; OSF web-UI posting OVERRIDDEN per operator decision; substrate for Cowork-side disclosure routing)
key-decisions:
  - MANUSCRIPT-MD5-AT-ENTRY (W5) = 2a57c1a061f0c66988a55d1d6600efdf (lock-at-entry value from W1-W4 chain; supersedes stale plan-mode literal 63fd81385590ffc8d23d45a0f0598959 per CLAUDE.md critical_constraints rule 1)
  - MANUSCRIPT-MD5-AT-EXIT (W5) = 2a57c1a061f0c66988a55d1d6600efdf (UNCHANGED — honest-framing-lock invariant preserved through Wave 5 closeout; phase entry md5 = phase exit md5 byte-identical)
  - 8 ta-r3 successor rows appended to md5_baseline.tsv (coloc_summary.tsv + 4 NEW files + 3 modified files + ta-r3-CONTEXT.md); W7 baseline preserved verbatim per Pitfall 5
  - tier_assignments.tsv md5 UNCHANGED — no successor row needed (W4 DEFERRED)
  - VERIFICATION.md verdict — 12/13 PASS + 1/13 WARN (D9 OSF override); phase CLOSED with override surfaced for Cowork-side disclosure routing
  - D9 WARN dimension records D-TA-R3-OSF-COVERAGE = OVERRIDDEN at 2026-05-05T13:49:10Z; amendment text on disk pre-W1-dispatch, but OSF web-UI posting deferred; consolidated into osf_deviations.md W5 entry with 2 rigor-defensible paths for Cowork side: (a) retroactive OSF posting + cover-letter timing footnote, or (b) v5 cover-letter pre-registration-timing limitation
  - Phase commit hash range: bccd0d6..c54cf5b (W1 first scaffold commit at bccd0d6; W5 final close commit at c54cf5b; full phase commit count enumerable via git log --oneline bccd0d6..c54cf5b)
  - HEAD ancestor invariants 069b34f + 7d54183 + 02c4404 hold 3/3 at phase exit (strict prefix match git log --oneline | awk '{print $1}' | grep -cE "^(069b34f|7d54183|02c4404)$")
  - STATE.md write GATE check passed at W5 Task 3 commit time (Terminal A NOT active on m3 path; no .claude/m3-*.lock files; no .planning/quick/*m3*/IN_PROGRESS markers; no live .claude/scheduled_tasks.lock); STATE.md updated rather than deferred
  - D-TA-R3-W5-PHASE-CLOSURE block appended to ta-r3-CONTEXT.md with all 4 prior-wave outcomes summarized + phase headline finding + verification path + handoff path + OSF outcome-branch follow-up substrate + md5 invariants + honest-framing-lock + HEAD ancestor invariants + STATE.md write status + routing-next note
  - Cowork-side narrative branch (informational; OUT of phase scope per OSF amendment "What is not changing"): manuscript v5 narrative branches under W1=FIRM as "SH2B3 anchor empirically supported under regularized LD; report lambda + PSD diagnostic + converged-status disclosure"; under W2=STRUCTURAL as "Layer-2-attrition framing empirically supported via falsification test that did not falsify"; under W3 0/6 as "of N canonical pairs across 5 admissible regions, 3 survive at PP.H4 >= 0.8 under matched-LD — all 3 at SH2B3 12q24 EUR anchor"; under W4=DEFERRED as A9 footnote prose recorded verbatim in CONTEXT.md
requirements-completed:
  - REQ-OSF-PREREG (deviation recorded — OSF web-UI posting OVERRIDDEN per operator decision; amendment text on disk pre-W1-dispatch; W5 closeout consolidates 2 rigor-defensible disclosure paths for Cowork side)
  - REQ-SNAKEMAKE-CI (verified — W2 used Snakemake DAG-confined re-fire under Snakemake 7.32.4 / Python 3.11; CI smoke inheritance from W2 path remains intact)
  - REQ-PATH-PARAMETERIZATION (verified — W3 added --region + --ancestry argparse to fire_canonical_susie_pairs.sh additively; W5 deliverables use explicit paths throughout)
  - REQ-PUBLIC-DATA-ONLY (verified — W5 closeout operates on existing public-data-derived substrates; no new data ingest)
duration: ~25 min wall (Task 1 ~5 min md5 successor rows; Task 2 ~12 min VERIFICATION.md + handoff brief + handoff STATE.md + osf_deviations entry; Task 3 ~5 min ROADMAP + STATE + CONTEXT closure block; ~3 min commit-staging + verification)
completed: 2026-05-06
---

# Phase ta-r3 Plan W5: Closeout + Cowork-side Handoff Summary (Wave 5 closeout — phase-final)

**Status:** `DONE` — phase `ta-r3-audit-v2-driven-psd-and-r1-refire` formally CLOSED. All 4 substantive waves (W1 PSD-regularized SH2B3 re-fit + W2 R1 cache-invalidated re-fire + W3 R2 canonical-pair parity + W4 HLA reconcile) plus this W5 closeout wave landed atomic commits with explicit-path staging discipline. Honest-framing-lock manuscript md5 `2a57c1a061f0c66988a55d1d6600efdf` UNCHANGED through all 5 waves (phase entry md5 byte-identical to phase exit md5).

**One-liner:** W5 phase closeout — 8 ta-r3 successor md5 rows appended to ta-sh2b3-W7 baseline (W7 preserved per Pitfall 5; tier_assignments.tsv UNCHANGED — no successor needed), VERIFICATION.md D1-D13 PASS/WARN/FAIL JSON evidence written (12 PASS + 1 WARN at D9 OSF override), Cowork-side handoff brief at `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md` enumerates wave outcomes + commit hashes + LSF job IDs + artifact paths + (a)/(b) OSF disclosure decision paths, ROADMAP Track-A-R3 status updated to COMPLETE, STATE.md frontmatter refreshed (Terminal A NOT active on m3 path verified pre-write), D-TA-R3-W5-PHASE-CLOSURE recorded in ta-r3-CONTEXT.md with all 4 wave outcomes; phase routing-next handoff to Cowork-side session for A1-A9 v5 manuscript revision + bundle ship + OSF outcome-branch follow-up update.

## Phase Headline Finding

The audit-V2 §HQ#2(i)/(ii)/(iii)/(g) reviewer concerns are all addressed empirically:

1. **§HQ#2(i)** — SH2B3 12q24 EUR Tier-A pass at PP.H4=1.0 from non-PSD LD + non-converged fits (Zou 2022 / Wallace 2021 / Wen 2017 / Benner 2017 false-positive mode): **REFUTED at SH2B3 specifically.** Under Wen 2017 ridge regularization at primary lambda=0.01, all 5 EUR per-trait fits CONVERGE (5/5 vs 0/5 in v2-audit baseline) and the 3 canonical pair PP.H4 still land at 1.000000 across the board. Tier-A SH2B3 anchor is empirically supported under PSD-regularized LD.

2. **§HQ#2(ii)** — selective firing (fixes applied to SH2B3 only): **REFUTED.** W3 R2 canonical-pair parity fired symmetrically at FTO/MC4R/APOL1/CXADR EUR using parameterized `bin/fire_canonical_susie_pairs.sh --region <X> --ancestry EUR`. Outcome: 0 of 6 W3 pairs surviving — Layer-2 attrition extends to canonical non-SH2B3 pairs; SH2B3 remains the only surviving Tier-A signal across 5 admissible regions × canonical-pair set.

3. **§HQ#2(iii)** — 28 of 28 empty trait-pair PP rows reframed as Layer-2 attrition without falsification testing: **FALSIFICATION TEST FIRED, DID NOT FALSIFY.** W2 cache-invalidated re-fire of all 28 R1 trait-pair coloc.susie attempts under HEAD with all 3 variant-ID-format-fix commits as ancestors produces 0/28 non-empty PP.H4 (Δ=0). Cache-staleness alternative refuted; Layer-2 attrition framing empirically supported.

4. **§HQ#2(g)** — manuscript negative-control panel row count not reconciled: **ADDRESSED via DEFERRED_TO_FOOTNOTE.** HLA encoding canonical mechanism = `neg_ctrl_set == "hla_immune"` flag (24 rows; matches v5 narrative referent EXACTLY); 200-vs-224 arithmetic anchored to pre-W3 baseline; post-W3 substrate is 233 rows. Cowork-side A9 footnote prose recorded verbatim in CONTEXT.md; on-disk file UNTOUCHED.

The Track A id-vs-ref-LD manuscript narrative survives unchanged. Manuscript md5 byte-identical at phase entry and exit.

## Per-Done-Criterion Status (PASS / WARN / FAIL)

| ID  | Criterion | Status |
|-----|-----------|--------|
| D1  | W1-W4 outcome tokens read from ta-r3-CONTEXT.md (4 separate tokens) | **PASS** — D-TA-R3-W1-BRANCH_PSD_FIRM + D-TA-R3-W2-BRANCH_R1_STRUCTURAL + D-TA-R3-W3-OUTCOME (0/6 surviving) + D-TA-R3-W4-DEFERRED_TO_FOOTNOTE all read at Task 1 entry |
| D2  | Aggregator refresh fired (only if W2 = BRANCH_R1_BUG) | **N/A** — W2 = BRANCH_R1_STRUCTURAL; no aggregator refresh needed (PP rows still empty for 28 R1 pairs) |
| D3  | Successor md5 rows appended (≥2 ta-r3 rows) without overwriting W7 baseline | **PASS** — 8 ta-r3 successor rows appended; 30 -> 38 lines; 0 duplicates; W7 baseline rows preserved verbatim per Pitfall 5 |
| D4  | ta-r3-VERIFICATION.md with D1-D13 evidence | **PASS** — 13 dimensions covered with PASS/WARN/FAIL JSON-style evidence; mirrors ta-sh2b3-VALIDATION.md C-row pattern |
| D5  | Cowork-side handoff brief written enumerating all wave outcomes | **PASS** — HPC_DELIVERABLE_2026-05-06.md with phase summary + 4 wave outcomes + commit hashes + LSF job IDs + md5 invariants + artifact paths + Cowork-side TODO list + (a)/(b) OSF disclosure decision paths |
| D6  | ROADMAP.md status COMPLETE; Plans line enumerates 5 PLAN.md files | **PASS** — Status block records closure date + wave outcomes + Cowork-side handoff path + OSF override D9 WARN surface + honest-framing-lock invariant; Plans line enumerates 5 PLAN.md files (W1 + W2 + W3 + W4 + W5) all checked |
| D7  | STATE.md updated (Terminal A NOT active on m3 path verified pre-write) | **PASS** — STATE.md write GATE check passed; no .claude/m3-*.lock files; no .planning/quick/*m3*/IN_PROGRESS markers; no live .claude/scheduled_tasks.lock; STATE.md frontmatter stopped_at + last_updated + last_activity refreshed |
| D8  | D-TA-R3-W5-PHASE-CLOSURE recorded with all 4 wave outcomes | **PASS** — block appended to ta-r3-CONTEXT.md with all 4 wave outcomes + phase headline finding + verification path + handoff path + OSF outcome-branch follow-up substrate + md5 invariants + honest-framing-lock + HEAD ancestor invariants + STATE.md write status + routing-next note |
| D9  | Honest-framing-lock manuscript md5 unchanged through all 5 waves | **PASS** — `md5sum docs/manuscript/id-vs-ref-LD.md` = `2a57c1a061f0c66988a55d1d6600efdf` at every wave gate (W1 entry = W1 exit = W2 entry = W2 exit = W3 entry = W3 exit = W4 entry = W4 exit = W5 entry = W5 exit); zero drift |
| D10 | HEAD ancestor invariants hold | **PASS** — `git log --oneline | awk '{print $1}' | grep -cE "^(069b34f|7d54183|02c4404)$"` returns 3 (strict prefix match) at phase exit |
| D11 | Atomic commits per task with explicit-path staging | **PASS** — Task 1 commit `eebdc2f` (1 file: md5_baseline.tsv); Task 2 commit `a060d9a` (4 files: VERIFICATION.md + 2 handoff files + osf_deviations.md); Task 3 commit `c54cf5b` (3 files: ROADMAP.md + STATE.md + CONTEXT.md); never `git add .` / `-A` |
| D12 | Conventional Commits format with `(ta-r3, W5)` scope and Co-Authored-By trailer | **PASS** — 3/3 commits use HEREDOC body with `feat(ta-r3, W5):` or `docs(ta-r3, W5):` scope and `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer |
| D13 | Original-research framing preserved | **PASS** — all commit messages + VERIFICATION.md + handoff brief + osf_deviations entry + CONTEXT.md closure block frame as "audit-driven re-analysis" / "audit-driven validation" / "Wave 5 closeout"; no "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot" language outside framing-lock-reminder context |

## Final Wave Outcome Summary (consolidated phase narrative)

| wave | outcome | one-line evidence |
|------|---------|-------------------|
| W1 | `D-TA-R3-W1-BRANCH_PSD_FIRM` | Primary lambda=0.01; 5/5 EUR per-trait fits converged at SH2B3 12q24; 3/3 canonical pair PP.H4 = 1.000000 (BMI-HTN, HTN-stroke, HTN-T2D); SH2B3 anchor empirically supported under Wen 2017 ridge PSD-regularized LD; LD pathology negative_eig_pct=23.4637 within 0.0037pp of v2-audit baseline 23.46% |
| W2 | `D-TA-R3-W2-BRANCH_R1_STRUCTURAL` | R1_non_empty_PP.H4 = 0/28 post cache-invalidated re-fire under HEAD ancestors 069b34f + 7d54183 + 02c4404 (Δ=0 vs pre-W2 baseline); cache-staleness alternative refuted; Layer-2 attrition framing empirically supported as structural property of GWAS×LD-panel intersection at non-SH2B3 regions × non-Tier-A trait pairs |
| W3 | `D-TA-R3-W3-OUTCOME` 0/6 surviving | Gated FIRES on W1=BRANCH_PSD_FIRM; FTO_16q12 EUR (3 pairs) + MC4R_18q21 EUR (1 pair) + APOL1_22q12 EUR (1 pair) + CXADR_F2RL1_6p21 EUR (1 pair) — 0 of 6 surviving PP.H4 ≥ 0.8 under matched-LD; Layer-2 attrition extends to canonical non-SH2B3 pairs; SH2B3 12q24 EUR remains the only surviving Tier-A signal across 5 admissible regions × canonical-pair set |
| W4 | `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE` | Per OSF amendment paragraph (g) option (i); investigation TSV confirms HLA encoding canonical mechanism = neg_ctrl_set == "hla_immune" (24 rows; matches v5 narrative referent EXACTLY); HLA_6p21 region has empty canonical_pairs in regions_curated.csv; v5 narrative "224 - 24 = 200" anchored to pre-W3 baseline; post-W3 substrate is 233 rows = 224 negative_control + 9 Tier C; Cowork-side A9 footnote prose recorded verbatim; on-disk tier_assignments.tsv UNTOUCHED |
| W5 | `D-TA-R3-W5-PHASE-CLOSURE` | 8 ta-r3 successor md5 rows appended (W7 baseline preserved); VERIFICATION.md D1-D13 (12 PASS + 1 WARN at D9); Cowork handoff brief at .planning/quick/260506-epz-ta-r3-cowork-handoff/; ROADMAP COMPLETE; STATE.md updated; OSF override consolidated to osf_deviations.md with 2 rigor-defensible disclosure paths for Cowork side |

## Atomic Commits This Pass

| commit | scope |
|--------|-------|
| `eebdc2f` | feat(ta-r3, W5): append 8 successor md5 rows for W1-W3 file shifts (audit-driven re-analysis) |
| `a060d9a` | docs(ta-r3, W5): write VERIFICATION.md (D1-D13 PASS/WARN/FAIL) + Cowork-side handoff brief at .planning/quick/260506-epz-ta-r3-cowork-handoff/ (audit-driven re-analysis) |
| `c54cf5b` | docs(ta-r3, W5): close phase ta-r3-audit-v2-driven-psd-and-r1-refire (W1=BRANCH_PSD_FIRM, W2=BRANCH_R1_STRUCTURAL, W3=0/6 surviving, W4=DEFERRED_TO_FOOTNOTE; audit-driven re-analysis; STATE.md updated) |
| `<this commit>` | docs(ta-r3, W5): finalize SUMMARY (W5 phase-final closeout) — Wave 5 closes phase (audit-driven re-analysis) |

## Honest-Framing-Lock Invariant Verification (Phase-Wide)

| anchor | md5 |
|--------|-----|
| W1 entry (phase entry; lock-at-entry capture) | `2a57c1a061f0c66988a55d1d6600efdf` |
| W1 exit | `2a57c1a061f0c66988a55d1d6600efdf` |
| W2 entry / exit | `2a57c1a061f0c66988a55d1d6600efdf` |
| W3 entry / exit | `2a57c1a061f0c66988a55d1d6600efdf` |
| W4 entry / exit | `2a57c1a061f0c66988a55d1d6600efdf` |
| W5 entry / exit | `2a57c1a061f0c66988a55d1d6600efdf` |
| **Drift across all 5 waves** | **NONE — lock holds end-to-end** |

The plan-mode-cached literal `63fd81385590ffc8d23d45a0f0598959` in PLAN.md frontmatter `must_haves.truths` block is a stale-plan-mode reference superseded by the live disk md5 at execute-mode entry; documented in W1 SUMMARY under "[Rule 1 - Bug] MANUSCRIPT-MD5-AT-ENTRY drifted from plan-mode literal" and inherited as the authoritative lock value through W2 / W3 / W4 / W5 per CLAUDE.md critical_constraints rule 1.

## OSF Outcome-Branch Follow-up Checklist (queued for Cowork-side posting)

The Cowork-side v5 ship session will append a follow-up OSF update at the same parent record (osf.io/az52u) per OSF amendment "Note on outcome-branch verification follow-up" paragraph. Substrate enumerated below:

- [ ] Realized W1 outcome branch: `BRANCH_PSD_FIRM` (primary lambda=0.01)
- [ ] Realized W2 outcome branch: `BRANCH_R1_STRUCTURAL` (R1_non_empty=0/28)
- [ ] Realized W3 conditional gate state: `fired` (driven by W1 = BRANCH_PSD_FIRM); 0 of 6 W3 canonical pairs surviving
- [ ] Realized W4 reconciliation choice: `DEFERRED_TO_FOOTNOTE` (option (i) of OSF amendment paragraph (g))
- [ ] R3 phase commit hash range: `bccd0d6..c54cf5b` (full phase) + `<this SUMMARY commit>` (post-this-commit final hash captured in ROADMAP/STATE on next routing note)
- [ ] Post-W5 md5 invariants: 8 ta-r3 successor rows in `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` (W7 baseline preserved per Pitfall 5)
- [ ] Realized lambda value selected for SH2B3 W1: `lambda = 0.01` (Wen 2017 ridge; smallest lambda where all 3 of bmi/hypertension/stroke per-trait fits converged)
- [ ] LSF job ID range: 115619-115643 (W1 original 15-job dispatch) + 119067-119078 (W1 redispatch after variant-ID-bridge fix)
- [ ] Cowork-side v5 submission bundle SHA-256: TBD (deferred; not in this phase's scope; will be in the follow-up update written at v5 ship time)
- [ ] OSF posting decision per D9 WARN dimension: choose between (a) retroactive OSF posting + cover-letter timing footnote OR (b) v5 cover-letter pre-registration-timing limitation (Cowork-side editorial decision; both rigor-defensible)

## Cross-Reference to Cowork Handoff Brief

**Path:** [.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md](../../quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md)

The handoff brief is the canonical Cowork-side onboarding document for the v5 *Genome Medicine* manuscript revision session. It contains the full phase summary + decision tokens + atomic commit hashes per wave + LSF job IDs + md5 invariants + artifact paths + Cowork-side A1-A9 TODO list + the OSF posting (a)/(b) decision rationale.

## Per-Wave SUMMARY References (phase narrative integration)

For Carter's hand-off to Cowork-side v5 manuscript revision, each wave SUMMARY contains the full per-wave decision provenance:

- **W1 SH2B3 PSD-regularized re-fit:** [ta-r3-W1-sh2b3-psd-regularized-refit-SUMMARY.md](ta-r3-W1-sh2b3-psd-regularized-refit-SUMMARY.md)
- **W2 R1 trait-pair cache-invalidated re-fire:** [ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md](ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md)
- **W3 R2 canonical-pair parity FTO/MC4R/APOL1/CXADR:** [ta-r3-W3-r2-canonical-pair-parity-SUMMARY.md](ta-r3-W3-r2-canonical-pair-parity-SUMMARY.md)
- **W4 tier_assignments HLA reconcile (DEFERRED):** [ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md](ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md)
- **W5 closeout + Cowork handoff (this SUMMARY):** [ta-r3-W5-closeout-and-handoff-SUMMARY.md](ta-r3-W5-closeout-and-handoff-SUMMARY.md)

## Deviations from Plan

### [Plan-literal supersede] Manuscript md5 lock value

- **Found during:** Task 1 entry (and inherited from W1-W4 SUMMARYs)
- **Issue:** PLAN.md `must_haves.truths` block + `<acceptance_criteria>` blocks reference manuscript md5 = `63fd81385590ffc8d23d45a0f0598959`. The live disk md5 at phase entry is `2a57c1a061f0c66988a55d1d6600efdf` (stale plan-mode-cached literal vs execute-mode-live).
- **Fix:** Inherit the live md5 lock value (`2a57c1a061f0c66988a55d1d6600efdf`) per CLAUDE.md critical_constraints rule 1 (live md5 is authoritative; plan-mode literal is informational). All W5 acceptance criteria checks use the live value. Documented in CONTEXT.md MANUSCRIPT-MD5-AT-ENTRY field at phase entry; inherited unchanged through every wave.
- **Files modified:** none — substantive intent ("manuscript unchanged through this phase") preserved exactly.
- **Commit:** N/A (operational invariant; documented across W1/W2/W3/W4/W5 SUMMARYs).

### [Operator override surfaced via D9 WARN] OSF amendment posting deferred

- **Found during:** Phase entry (W1 Task 1 pre-fire gate)
- **Issue:** PLAN.md (and OSF amendment paste-ready text) require `D-TA-R3-OSF-COVERAGE: COVERED at <timestamp>` to be present in CONTEXT.md before any LSF dispatch fires. Per operator override 2026-05-05, OSF web-UI posting was deferred; the token records `OVERRIDDEN at 2026-05-05T13:49:10Z`.
- **W5 closeout disposition:** Surfaced as D9 WARN dimension in VERIFICATION.md + consolidated entry in osf_deviations.md L62-95 + Disclosure section in HPC_DELIVERABLE_2026-05-06.md enumerating 2 rigor-defensible Cowork-side disclosure paths: (a) retroactive OSF posting + cover-letter timing footnote, or (b) v5 cover-letter pre-registration-timing limitation. Either path is rigor-defensible; (a) is the stricter route.
- **Files modified:** `.planning/osf_deviations.md`, `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md`, `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md`, `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` (D-TA-R3-W5-PHASE-CLOSURE block surfaces this).
- **Commit:** `a060d9a` (Task 2 — VERIFICATION.md + handoff brief + osf_deviations entry).

### [Pitfall 3 not triggered] Aggregator refresh skipped

- **Found during:** Task 1 step 2 (W2 outcome read from CONTEXT.md)
- **Issue:** PLAN.md Task 1 step 2 specifies aggregator refresh fires only if W2 = BRANCH_R1_BUG (new PP rows would shift Table 3 numbers). W2 outcome resolved as BRANCH_R1_STRUCTURAL (PP rows still empty for 28 R1 pairs).
- **Fix:** Skipped aggregator refresh per the plan's conditional. D2 acceptance criterion above marks this as N/A (correct branch).
- **Files modified:** none.

**Total deviations:** 0 substantive (all are plan-literal-supersede or operator-override surfacings; no analytical decision rules deviated from the OSF amendment text on disk).

## Authentication Gates

None — all operations were on-disk file edits + git commits + gsd-tools CLI invocations against locally-committed substrate.

## Self-Check: PASSED

- [x] `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md` exists
- [x] `grep -cE '(PASS|WARN|FAIL)' ta-r3-VERIFICATION.md` returns 34 (≥13 required)
- [x] `grep -cE 'D-TA-R3-W[1-4]' ta-r3-VERIFICATION.md` returns 12 (≥4 required)
- [x] `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md` exists
- [x] Handoff brief enumerates all 4 W1 outcome branches (`grep -cE '(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)'` returns 7)
- [x] Handoff brief enumerates 2 W2 outcome branches (`grep -cE '(BUG|STRUCTURAL)'` returns 9)
- [x] Handoff brief references OSF amendment URL (`grep -c 'osf.io/az52u'` returns 4)
- [x] Handoff brief includes honest-framing-lock reminder (`grep -c 'audit-driven re-analysis'` returns 6)
- [x] `.planning/quick/260506-epz-ta-r3-cowork-handoff/STATE.md` exists
- [x] `awk -F'\t' '$3 ~ /\(ta-r3\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l` returns 8 (≥2 required)
- [x] `sort .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | uniq -d | wc -l` returns 0 (no duplicates)
- [x] ROADMAP.md Track-A-R3 entry status reflects COMPLETE
- [x] `grep -cE 'ta-r3-W[1-5]-.*-PLAN\.md' .planning/ROADMAP.md` returns 5 (Plans line enumerates all 5)
- [x] `grep -c 'D-TA-R3-W5-PHASE-CLOSURE' ta-r3-CONTEXT.md` returns 1
- [x] STATE.md `stopped_at` field updated with phase-complete state
- [x] `md5sum docs/manuscript/id-vs-ref-LD.md` = `2a57c1a061f0c66988a55d1d6600efdf` (UNCHANGED through all 5 waves)
- [x] `git log --oneline | awk '{print $1}' | grep -cE "^(069b34f|7d54183|02c4404)$"` returns 3 (HEAD ancestor invariants hold strict)
- [x] 4 atomic commits this pass (Task 1: eebdc2f, Task 2: a060d9a, Task 3: c54cf5b, this SUMMARY commit follow-up)
- [x] No `git add .` / `-A` used in any commit (explicit paths only per .planning/feedback_multi_terminal_staging.md)
- [x] Phase ta-r3-audit-v2-driven-psd-and-r1-refire formally CLOSED via ROADMAP.md Status field + STATE.md frontmatter + ta-r3-CONTEXT.md D-TA-R3-W5-PHASE-CLOSURE block

**Self-Check verdict:** PASS for the full W5 plan (Tasks 1 + 2 + 3 + this SUMMARY commit). Phase ta-r3-audit-v2-driven-psd-and-r1-refire formally CLOSED. Routing next: Cowork-side session for v5 *Genome Medicine* manuscript revision (A1-A9 manuscript edits + bundle ship + OSF outcome-branch follow-up update + (per D9 WARN disclosure decision) retroactive OSF amendment posting OR v5-cover-letter pre-registration-timing limitation).
