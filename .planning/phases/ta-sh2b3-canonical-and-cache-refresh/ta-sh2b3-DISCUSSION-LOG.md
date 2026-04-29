# Phase ta-sh2b3-canonical-and-cache-refresh — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in [ta-sh2b3-CONTEXT.md](./ta-sh2b3-CONTEXT.md) — this log preserves the alternatives considered.

**Date:** 2026-04-28
**Phase:** ta-sh2b3-canonical-and-cache-refresh
**Mode:** power-mode (`/gsd-discuss-phase --power`-equivalent; recommended via command-args because Q-01 D-TA-01 may need ssh login02 round-trip and Q-07 D-TA-05 needs ~30 min on OSF portal)
**Areas discussed:** Foundations (Wave 0); Issue 1 — SH2B3 EUR SuSiE-RSS re-fits; Issue 1 — Canonical-pair scope; Issue 2 — Variant-ID cache propagation refresh; OSF pre-registration coverage; Track A nickname rename
**Resolution:** Carter accepted all 13 recommended defaults via interactive chat at 2026-04-28T22:42:00-04:00 ("Accept all recommendations")
**Question file:** [ta-sh2b3-QUESTIONS.json](./ta-sh2b3-QUESTIONS.json) (committed `b2590d9`; finalized at 22:42 with all 13 `answer` fields populated)

---

## Section 1 — Foundations (Wave 0)

### Q-01 — Source repo absolute path on cluster

**Context surfaced in question:** GPFS interactive mount `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` and cluster-canonical `/rs1/researchers/c/ckclinto/coloc_analysis/` are the same physical filesystem. The submission-bundle `build_log.txt` cites `Build host: login02.hpc.ncsu.edu` (one of several login nodes; login03 used for prior Stage 1d narrow-validation tests). The actual repo path used by every prior LSF fire (Phase 0 smoke_dev, deCODE pQTL ingest, k2d 2026-04-24 identity-LD re-fire, Stage 2 2026-04-22 production fire, submission bundle 2026-04-28) appears to be `/rs1/researchers/c/ckclinto/coloc_analysis/`.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | `/rs1/researchers/c/ckclinto/coloc_analysis/` (recommended; consistent with all 4+ prior LSF fires) | ✓ |
| (b) | `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` (the GPFS mount path used interactively from this shell; same filesystem) | |
| (c) | `/share/clintonlab/ckclinto/coloc_analysis/` (only if a /share/ mirror exists for login02) | |
| (d) | Custom path (specify in chat_more) | |

**User's choice:** (a) — `/rs1/researchers/c/ckclinto/coloc_analysis/`
**Notes:** Locked under D-TA-01 in CONTEXT.md. Wave 0 verifies via `[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ] && cd /rs1/... && git rev-parse HEAD` matches GPFS HEAD; all subsequent `bsub` invocations use absolute `/rs1/...` paths.

---

## Section 2 — Issue 1: SH2B3 EUR SuSiE-RSS re-fits (D-TA-02 + audit-V2 HQ#2(ii) headline)

### Q-02 — L value for SH2B3 EUR per-trait re-fits

**Context surfaced:** Three of five SH2B3 EUR per-trait SuSiE-RSS fits are non-converged at L=10 / niter=100 (Wang et al. 2020 §Discussion iteration-cap regime). Audit-V2 §HQ#2(i) marked DEFERRED-COMPUTE pending an LSF slot — this phase fires it. Compute envelope per AUDIT-RESPONSE 2026-04-26 line 260: ~2–4 hours wall time on `serial` queue with `la_multitrait_r` env at L=20 (3-trait sweep).

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | L=20 single-shot (Zou 2022 default; ~3× compute over L=10) | |
| (b) | L-sweep {15, 20, 30} pre-registered supplementary (recommended; ~9× compute; produces sensitivity evidence) | ✓ |
| (c) | L=20 with conditional-extension to L=30 if n_CS == L (saturation indicator) | |
| (d) | Other (specify) | |

**User's choice:** (b) — L-sweep {15, 20, 30} pre-registered supplementary
**Notes:** Locked under D-TA-02 in CONTEXT.md. Already pre-registered in `track_a_pivot.md` Methods §Fine-Mapping Configuration; OSF coverage to be verified in Wave 0 per D-TA-05 Q-07. Generates Supplementary Methods table per Zou 2022 recommendation.

### Q-03 — Headline numerator decision when L=20 lands (HQ#2(ii) DEFERRED-DESIGN)

**Context surfaced:** Currently the manuscript's 51/96 yield headline pools the 18 non-converged fits with the 33 converged ones. Audit-V2 Eval 2(a) flagged this as "non-convergence treated as data". AUDIT-RESPONSE 2026-04-26 line 280 confirms this is "a framing choice that materially shifts the Abstract / Headline Result / Fig 2 / TRACK-A-FROZEN-NUMBERS.md LIVE block — not a routine prose edit".

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Decide post-Wave-1 from observed convergence outcome (recommended; outcome-driven) | ✓ |
| (b) | Keep 51/96 with caveat in place (don't recompute regardless of L=20 outcome) | |
| (c) | Drop non-converged fits from numerator regardless (most rigorous; commits to 33/96 baseline) | |
| (d) | Other (e.g., dual reporting: keep 51/96 + add 33/96 as Supplementary) | |

**User's choice:** (a) — Decide post-Wave-1 from observed convergence outcome
**Notes:** Locked under D-TA-Wave1-headline in CONTEXT.md. Plan must NOT pre-commit to a numerator value before Wave 1 fires. Wave 1 SUMMARY.md must report per-trait convergence-status outcomes at chosen L explicitly; do NOT update headline numerator in Wave 1. Wave 6 task: based on Wave 1 + Wave 2 outcomes, EITHER recompute 51/96 OR add non-convergence disclosure column.

---

## Section 3 — Issue 1: Canonical-pair coloc.susie scope (D-TA-03 + Wave 3 gate)

### Q-04 — Canonical-pair coloc.susie scope

**Context surfaced:** Already on disk: `SH2B3_12q24__EUR__asthma_vs_t2d` (1 pair). Full SH2B3 EUR trait-pair lattice = 10 pairs (5 traits choose 2). FTO_16q12 EUR has all 10 pairs in Stage 2 manifest — symmetry target. Wave 2 LSF compute scales linearly with pair count (~2 hr per pair on `serial` queue with `la_multitrait_r` env, conservatively ~18 hr for 9 pairs).

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | MINIMUM — BMI–HTN + HTN–stroke (2 new pairs; tests just the canonical literature claims) | |
| (b) | RECOMMENDED — 9 new pairs (full SH2B3 EUR lattice minus already-on-disk asthma–t2d) | ✓ |
| (c) | MAXIMUM — also re-fire FTO_16q12 EUR + MC4R_18q21 EUR + APOE_19q13 + CXADR_F2RL1_6p21 against post-L=20 fits | |
| (d) | Other | |

**User's choice:** (b) — 9 new pairs (full SH2B3 EUR trait-pair lattice)
**Notes:** Locked under D-TA-03 in CONTEXT.md. Symmetrizes Table 3 SH2B3 row with FTO_16q12. Both BMI–HTN and HTN–stroke (the two canonical literature pairs at PP.H4 = 1.00 under Stage 1d identity-LD) are included. MAXIMUM cross-region replication (alternative c) deferred to a separate phase per <deferred> in CONTEXT.md.

### Q-05 — PP.H4 outcome-branch threshold for Wave 3 human-verify gate

**Context surfaced:** Manuscript currently uses Tier B = 0.5 / Tier A = 0.8 throughout (per AUDIT-RESPONSE TRACK-A-FROZEN-NUMBERS L143 "Threshold preservation"). Lowering thresholds to surface FTO Tier-C 0.3099 signal was rejected as out of scope during quick-260427-e8n.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Standard manuscript thresholds: collapse <0.5 / partial 0.5–0.8 / survive ≥0.8 (recommended; preserves Tier B/A; no OSF amendment) | ✓ |
| (b) | Lower bar: collapse <0.3 / partial 0.3–0.7 / survive ≥0.7 (requires OSF amendment) | |
| (c) | Higher bar: collapse <0.5 / partial 0.5–0.95 / survive ≥0.95 (matches the original PP.H4=1.00 claim more strictly) | |
| (d) | Other | |

**User's choice:** (a) — Standard manuscript thresholds (Tier B = 0.5, Tier A = 0.8)
**Notes:** Locked under D-TA-Wave3-thresholds in CONTEXT.md. Three honest outcome branches: (a) BMI–HTN reference-LD `PP.H4 < 0.5` → identity-LD canonical claim does NOT survive matched-LD; flagship demonstrated collapse; strongest finding. (b) `PP.H4 ∈ [0.5, 0.8)` → partial survival; calibration finding. (c) `PP.H4 ≥ 0.8` → canonical claim holds up under matched-LD; SH2B3 anchor flips from "collapse" to "validated".

---

## Section 4 — Issue 2: Variant-ID cache propagation refresh (D-TA-04)

### Q-06 — Cache-layer scope for Issue 2 re-fire

**Context surfaced:** QTL-coloc compute envelope: ~1,274 attempts × ~30 sec ≈ ~10 hr at 50 cores LSF. SuSiE-RSS layer adds ~5 hr if needed. PASS criterion: `too_few_snps` drops materially from 1,005 (target ≤200; `success` + `no_qtl_cs` counts rise). FAIL criterion: stays ~1,000 → SuSiE-RSS layer was the actual problem; root-cause investigation triggered, do NOT proceed to Wave 6.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | DIAGNOSTIC-DRIVEN (recommended) — Wave 0 picks; Wave 4 scope decided by SuSiE-RSS variant-ID format check | ✓ |
| (b) | CONSERVATIVE-BOTH — re-fire both layers regardless (~15 hr total) | |
| (c) | FAST-QTL-ONLY — re-fire only QTL-coloc; if Wave 4 PASS criterion fails, fallback to Wave 4.5 SuSiE-RSS re-fire | |
| (d) | Other | |

**User's choice:** (a) — DIAGNOSTIC-DRIVEN (Wave 0 picks)
**Notes:** Locked under D-TA-04 in CONTEXT.md. Wave 0 reads 3 sample SuSiE-RSS JSONs; rsid → QTL-coloc only (~10 hr); chr:pos → both layers (~15 hr); mixed → escalate to CONSERVATIVE-BOTH. PLAN.md must include both code paths and an explicit Wave-0 diagnostic gate.

---

## Section 5 — OSF pre-registration coverage (D-TA-05)

### Q-07 — OSF coverage for D-TA-02 (L value) + D-TA-03 (canonical-pair scope)

**Context surfaced:** Methods §Fine-Mapping Configuration in `track_a_pivot.md` states "an L-sweep re-fit at L ∈ {15, 20, 30} is pre-registered as a follow-on supplementary analysis". AUDIT-RESPONSE 2026-04-26 line 269 says HQ#2(iii) is "pre-registered in TRACK-A-FROZEN-NUMBERS.md". Both need OSF-portal verification (in-tree draft ≠ OSF deposit).

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Wave 0 verifies, then proceeds (recommended if pre-reg already covers) | ✓ |
| (b) | Post OSF amendment NOW pre-emptively (Carter on OSF portal, ~30 min) | |
| (c) | Defer the OSF check entirely until Wave 1 has produced results (risky — retroactive amendment) | |
| (d) | Other (e.g., split: verify L-sweep + amend canonical-pair only) | |

**User's choice:** (a) — Wave 0 verifies, then proceeds
**Notes:** Locked under D-TA-05 in CONTEXT.md. Wave 0 task: Carter opens `osf.io/pvb5j` Methods + `osf.io/az52u` closeout PDF in browser; greps for "L-sweep" + "{15, 20, 30}" + "canonical pair" + "BMI-HTN" + "HTN-stroke"; records outcome as `D-TA-OSF-COVERAGE-XX` in CONTEXT.md addendum. If covered: Wave 1 cleared. If uncovered: Carter posts amendment on OSF portal; Wave 1 hard-blocked until amendment confirmed live.

### Q-08 — OSF treatment of cache invalidation re-fire (D-TA-04)

**Context surfaced:** Cache invalidation re-fires with the SAME code (`069b34f` + `7d54183`) + SAME data + SAME params — only the cache state changes. This is methodologically a 'cache hygiene fix', not a new analysis. Per Carter's command-args explicitly, this 'should be a deviation-log entry, NOT a pre-reg amendment'.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Deviation-log entry only (recommended; appended to .planning/amendments/osf_deviations.md or osf.io/az52u closeout addendum) | ✓ |
| (b) | Pre-reg amendment via osf.io/pvb5j (treat as new analysis) | |
| (c) | Both — deviation-log entry + brief pre-reg amendment note (max traceability) | |
| (d) | Other | |

**User's choice:** (a) — Deviation-log entry only
**Notes:** Locked under D-TA-Cache-OSF in CONTEXT.md. Wave 7 closeout task appends `osf_deviations.md` entry with discovery date, root cause, invalidation rationale, before/after numerics, commit pointers, OSF deposit cross-reference.

---

## Section 6 — Track A nickname rename (D-TA-06)

### Q-09 — Rename `docs/manuscript/track_a_pivot.md` → `docs/manuscript/id-vs-ref-LD.md`?

**Context surfaced:** Affects ~12+ in-tree references: every R figure-builder script (`scripts/R/figures/*.R`), every aggregator (`scripts/R/aggregators/*.R`), the submission-bundle build script, the locked-scalar block headers, and any test fixtures. The rename + reference-fix-up is non-trivial (~30-60 min Wave 6 task with grep+sed+verify md5 round-trip).

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | YES — rename to docs/manuscript/id-vs-ref-LD.md (recommended) | ✓ |
| (b) | NO — keep docs/manuscript/track_a_pivot.md (path is internal; only prose framing matters) | |
| (c) | YES with a different target name (e.g., docs/manuscript/track_a_id_vs_ref_LD.md preserving Track A prefix) | |

**User's choice:** (a) — YES rename to `docs/manuscript/id-vs-ref-LD.md`
**Notes:** Locked under D-TA-06 in CONTEXT.md. Aligns path with locked manuscript title and project_track_a_handle.md memory.

### Q-10 — Rename `.planning/amendments/TRACK-A-PIVOT.md` → `ID-VS-REF-LD-STRATEGY.md`?

**Context surfaced:** `.planning/` is internal-only (gitignored from public release scope per memory). The 'pivot' wording in the filename refers to the 2026-04-22 strategic event itself (project-strategy pivot from candidate-locus to genome-wide design), not to Track A as a publication.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | YES — rename to ID-VS-REF-LD-STRATEGY.md (recommended; matches the Track A nickname) | ✓ |
| (b) | NO — keep TRACK-A-PIVOT.md (internal-only; ‘pivot’ in name = strategic event, not publication framing) | |
| (c) | YES with a different target name (e.g., ID-VS-REF-LD-PUBLICATION-STRATEGY.md, TRACK-A-STRATEGY.md) | |

**User's choice:** (a) — YES rename to `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`
**Notes:** Locked under D-TA-06 in CONTEXT.md. Cleaner separation between strategic-event docs (PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md kept) and Track-A-publication strategy doc.

### Q-11 — Rename `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`?

**Context surfaced:** Carter's command-args explicitly flagged this as 'optional rename (Carter's call; TRACK-A- prefix may stay)'. The file is the canonical numerics source-of-truth referenced in 4+ places (manuscript locked-scalar block, R-script headers, OSF amendment, Track A SUMMARY).

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | NO — keep TRACK-A-FROZEN-NUMBERS.md (recommended; ‘TRACK-A-’ prefix is Carter-specified; widely cross-referenced) | ✓ |
| (b) | YES — rename to ID-VS-REF-LD-FROZEN-NUMBERS.md | |
| (c) | YES with a different target name | |

**User's choice:** (a) — NO keep `TRACK-A-FROZEN-NUMBERS.md`
**Notes:** Locked under D-TA-06 in CONTEXT.md. Saves an extra reference-fix-up round-trip across manuscript + R scripts + OSF amendment + Track A SUMMARY (4+ citation sites). The file's role as numerics source-of-truth is independent of the publication's nickname.

### Q-12 — Rename `bin/build_track_a_submission_bundle.sh`?

**Context surfaced:** 488-line bash builder; built the current frozen submission-bundle commit `cacdbfe`. Mixed-case in shell scripts is unusual; snake_case is conventional. Per Carter's command-args: 'snake_case for shell' suggests `build_id_vs_ref_ld_submission_bundle.sh` (all lowercase).

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | YES — rename to bin/build_id_vs_ref_ld_submission_bundle.sh (snake_case, all lowercase; recommended) | ✓ |
| (b) | YES — rename to bin/build_id_vs_ref_LD_submission_bundle.sh (mixed case to match the LD acronym) | |
| (c) | NO — keep bin/build_track_a_submission_bundle.sh | |
| (d) | Other | |

**User's choice:** (a) — YES rename to `bin/build_id_vs_ref_ld_submission_bundle.sh` (lowercase snake_case)
**Notes:** Locked under D-TA-06 in CONTEXT.md. Conventional shell-script naming; matches the rest of the `bin/` directory (every other script uses lowercase snake_case).

### Q-13 — Rename timing — when does the rename + reference-fix-up wave fire?

**Context surfaced:** Wave 6 already touches every file in scope (Methods + Results + Discussion + Limitations + Abstract + Conclusion-1 + captions + tables + R-script headers + locked-scalar blocks). Bundling the rename costs zero extra waves.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Wave 6 — bundle rename with manuscript narrative updates (recommended; zero extra waves) | ✓ |
| (b) | Wave 0.5 — dedicated rename wave inserted before Wave 1 | |
| (c) | Wave 6.5 — dedicated post-narrative wave, rename + reference fix-ups separated from Wave 6 prose | |
| (d) | Other (e.g., split: Wave 0.5 for non-manuscript paths + Wave 6 for manuscript) | |

**User's choice:** (a) — Wave 6 bundled rename
**Notes:** Locked under D-TA-Wave-6-timing in CONTEXT.md. Wave 6 PLAN.md structure: ordered task list with rename + reference-fix-up tasks first (mechanical, zero-narrative), then narrative atomic-update tasks (per-file commit). Each task has its own atomic commit per the no-`/gsd-quick`-shortcuts invariant.

---

## Claude's Discretion

None. Carter accepted all 13 recommended defaults; no decisions deferred to Claude.

---

## Deferred Ideas (mentioned during discussion or surfaced from alternatives)

See [ta-sh2b3-CONTEXT.md](./ta-sh2b3-CONTEXT.md) `<deferred>` section for the full list. Summary:

- MAXIMUM cross-region replication (Q-04 alt c) — its own phase
- Threshold-lowering to 0.3 (Q-05 alt b) — rejected during quick-260427-e8n
- Pre-emptive OSF amendment for all sub-decisions (Q-07 alt b) — verify-then-amend chosen instead
- Cache-invalidation pre-reg amendment (Q-08 alts b/c) — deviation-log only chosen
- TRACK-A-FROZEN-NUMBERS.md rename (Q-11 alts b/c) — deferred for stability
- bin/ mixed-case (Q-12 alt b) — lowercase snake_case chosen for shell convention
- Wave 0.5 / Wave 6.5 dedicated rename waves (Q-13 alts b/c) — Wave 6 bundled
- Terminal A capacity for M2-POST-M3-08 mtCOJO re-fire / sumstats Route C — file-disjoint; can stack while this phase fires

---

*Power-mode discuss-phase audit trail. Generated 2026-04-28T22:42:00-04:00.*
*Mode: `accept-all-recommendations` (Carter, interactive chat). All 13 questions answered.*
*Question file: [ta-sh2b3-QUESTIONS.json](./ta-sh2b3-QUESTIONS.json) (commit `b2590d9`).*
*Locked decisions: [ta-sh2b3-CONTEXT.md](./ta-sh2b3-CONTEXT.md).*
