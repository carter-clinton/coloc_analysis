---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 2
slug: W2-r1-trait-pair-coloc-refire
status: DONE
subsystem: track-a-audit-driven-re-analysis
tags: [audit-v2-driven, r1-trait-pair-coloc-refire, cache-invalidated-refire, snakemake, layer-2-attrition, branch-r1-structural, falsification-test, closeout]
requires:
  - results/multitrait/coloc_manifest.tsv
  - results/multitrait/coloc_susie/ (28 R1 JSONs from prior phase; mv-backup at coloc_susie.preFix.bak.20260506_141119Z/)
  - results/multitrait/coloc_susie_R2/ (9 SH2B3 R2 JSONs; preserved untouched)
  - results/fine_mapping/susie/{trait}.{ancestry}.{region}.fit.rds (Layer-1 SuSiE-RSS fits read by run_coloc_susie.R)
  - .planning/amendments/osf-amendment-r3-2026-05-04.md (W2 outcome-branch decision matrix; AUTHORITATIVE)
  - .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md (HQ#2(iii) finding)
  - HEAD ancestor commits 069b34f + 7d54183 + 02c4404 (variant-ID-format-fix substrate)
  - /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake (Snakemake 7.32.4 / Python 3.11)
provides:
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W2-BRANCH_R1_STRUCTURAL recorded; PENDING placeholder removed)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv (28 R1 R-pair manifest; strict-correct R2 exclusion via comm -23)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv (pre-W2 metrics; 0/28 R1 non-empty PP.H4; matches audit-V2 §HQ#2(iii) baseline)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt (post-W2 md5 = 85ab5aa2ca4b54e0edf2a48dc4c61258; SHIFTED from W7 baseline 558fca45ac37d901028c64429cdecc12)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv (post-W2 metrics + computed branch)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-backup-path.txt (rollback sentinel)
  - results/multitrait/coloc_summary.tsv (rebuilt 37-row merge of R1 + R2 dirs; W5 closeout will append md5 successor row to md5_baseline.tsv)
  - results/multitrait/coloc_susie/*.json (28 R1 JSONs re-fired under HEAD; status="no_signal", n_cs_a=0 OR n_cs_b=0; gitignored — regenerable from manifest + HEAD code)
  - results/multitrait/coloc_susie.preFix.bak.20260506_141119Z/ (timestamped mv-backup of pre-W2 R1 cache; gitignored; rollback path preserved on disk)
  - logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log (Snakemake invocation + finished-job tally + exit code 0)
affects:
  - downstream W3 (R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR EUR) — UNAFFECTED (W3 gate is W1-driven; W2 outcome flows to manuscript narrative only, NOT to W3 gate disposition)
  - downstream W4 (HLA reconcile + tier reassignment) — INDEPENDENT
  - downstream W5 (closeout brief + Cowork handoff) — must surface BRANCH_R1_STRUCTURAL for v5 manuscript narrative branch + append post-W2 md5 successor row to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (NOT overwrite per OSF amendment "What is not changing" §md5 invariant rule)
tech-stack:
  added: []
  patterns:
    - Snakemake DAG-confined execution via `--until <rule>` (avoids upstream all-rule pollution)
    - W5-style inline-pandas merge of two parallel cache namespaces (R1 + R2; R2 wins on collision)
    - Falsification-test-by-replay (re-run prior empty-PP outputs under HEAD with fix-commits as ancestors; structural failure mode survives → BRANCH_R1_STRUCTURAL)
    - Pitfall 5 timestamped mv-backup (NOT rm; rollback preserved on disk)
    - .gitignore allowlist for new namespace artifacts (parity with W1 fine_mapping_psd_regularized/ pattern)
    - HEAD ancestor invariant verification at gate (strict prefix match `^(069b34f|7d54183|02c4404)$` on `git log --oneline | awk '{print $1}'`)
key-files:
  created:
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-backup-path.txt
    - results/multitrait/coloc_summary.tsv (force-allowlisted; commit-tracked)
    - results/multitrait/coloc_susie/*.json (28 R1 JSONs; gitignored — regenerable)
    - results/multitrait/coloc_susie.preFix.bak.20260506_141119Z/ (28 JSONs; gitignored — rollback)
    - logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md (this file; closeout)
  modified:
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W2-BRANCH_R1_STRUCTURAL resolved; PENDING placeholder removed)
    - .gitignore (W2 namespace allowlist for coloc_summary.tsv + r1_refire_dispatch.log)
    - .planning/STATE.md (stopped_at refresh + last_updated + last_activity per feedback_state_md_keep_current.md memory)
    - .planning/ROADMAP.md (plan progress for ta-r3-W2 → completed via gsd-tools roadmap update-plan-progress)
key-decisions:
  - MANUSCRIPT-MD5-AT-ENTRY (W2) = 2a57c1a061f0c66988a55d1d6600efdf (lock-at-entry value from W1 closeout; overrides stale plan-mode literal 63fd8138... per CLAUDE.md critical_constraints rule 1)
  - MANUSCRIPT-MD5-AT-EXIT (W2) = 2a57c1a061f0c66988a55d1d6600efdf (UNCHANGED — honest-framing-lock invariant preserved through Wave 2 closeout)
  - Pre-W2 R1_non_empty_PP.H4 = 0 of 28 (matches audit-V2 §HQ#2(iii) "28/28 empty" baseline claim)
  - Post-W2 R1_non_empty_PP.H4 = 0 of 28 (Δ=0; UNCHANGED from pre-W2 — falsification test does not falsify)
  - SH2B3 R2 rows preserved 9/9 (5 of 9 with non-empty PP.H4; risk register row 4 satisfied)
  - coloc_summary.tsv md5 SHIFTED 558fca45ac37d901028c64429cdecc12 → 85ab5aa2ca4b54e0edf2a48dc4c61258 (intentional; W5 appends successor row to md5_baseline.tsv, NOT overwrite)
  - D-TA-R3-W2-BRANCH_R1_STRUCTURAL at primary OSF-amendment-paragraph-(e) decision matrix (R1 non-empty = 0 → STRUCTURAL)
  - Per-JSON failure mode: status="no_signal" / n_cs_a=0 OR n_cs_b=0 (Layer-1 SuSiE-RSS attrition cascades to Layer-2 coloc.susie no_signal; variant-ID matcher works correctly upstream-of structural credible-set vacancy)
  - W3 gate (D-TA-R3-W3-GATE = FIRES) is W1-driven (BRANCH_PSD_FIRM); W2 outcome flows to manuscript narrative ONLY; does NOT change W3 gate disposition
  - Cowork-side narrative branch implication (informational; OUT of phase scope): STRUCTURAL → manuscript v5 Layer-2-attrition framing survives reviewer-defensible re-application of fix commits to full 28-pair set
requirements-completed:
  - REQ-SNAKEMAKE-CI (DONE — 28/28 jobs ran via Snakemake LSF profile under conda envs)
  - REQ-PATH-PARAMETERIZATION (DONE — explicit target paths via R1 manifest awk; no hard-coded pair lists)
  - REQ-PUBLIC-DATA-ONLY (verified — 1000G EUR + AFR LD ref + harmonized public sumstats; all public)
duration: 32 min wall (Task 1: ~5 min target identification + baseline + backup; Task 2: ~9 min Snakemake re-fire + ~2 min summary rebuild; Task 3: ~6 min branch classification + CONTEXT.md edit + commit; ~10 min context loading + verify)
completed: 2026-05-06
---

# Phase ta-r3 Plan W2: R1 Trait-Pair coloc.susie Cache-Invalidated Re-fire Summary (Wave 2 closeout — D-TA-R3-W2-BRANCH_R1_STRUCTURAL)

**Status:** `DONE` — Wave 2 closes with `BRANCH_R1_STRUCTURAL` per OSF amendment 2026-05-04 paragraph (e) decision matrix. R1_non_empty_PP.H4 = 0 of 28 post-refire (Δ=0 vs pre-W2 baseline) under HEAD code with all 3 variant-ID-format-fix commits (069b34f + 7d54183 + 02c4404) as ancestors. The Layer-2-attrition-under-matched-LD framing is empirically supported as a structural property of the GWAS×LD-panel intersection at non-SH2B3 regions × non-Tier-A trait pairs — NOT a propagation gap of the fix commits.

**One-liner:** Audit-driven cache-invalidated re-fire of 28 R1 trait-pair coloc.susie attempts under HEAD code with the variant-ID-format-fix commits 069b34f + 7d54183 + 02c4404 as ancestors produces 0 of 28 non-empty PP.H4 rows — identical to the pre-W2 baseline of 0/28 from the audit-V2 §HQ#2(iii) finding — refuting the cache-staleness alternative and empirically supporting the manuscript's Layer-2-attrition framing; SH2B3 R2 floor of 9 rows in coloc_summary.tsv preserved (risk register row 4); manuscript md5 invariant preserved through 3 atomic commits + 1 .gitignore allowlist edit.

## Execution Timeline

- **Start:** 2026-05-06T14:05:21Z (Task 1 dispatch begin; pre-fire HARD GATE checks)
- **End:** 2026-05-06T14:40:37Z (Task 3 commit + outcome.tsv lands; SUMMARY commit shortly after)
- **Duration:** ~35 min wall (Task 1 ~5 min; Task 2 dispatch ~9 min Snakemake + ~2 min summary rebuild; Task 3 ~6 min outcome compute + CONTEXT edit; remainder context loading + verify + commit)
- **Tasks executed:** 3/3 (all complete)
- **Files created/modified:** 10 created + 4 modified (per key-files frontmatter)
- **Atomic commits this pass:** 3

## Per-Done-Criterion Status (PASS / WARN / FAIL)

| ID  | Criterion | Status |
|-----|-----------|--------|
| D1  | Pre-fire HEAD ancestor + LSF wrapper gate | **PASS** (HEAD ancestors 069b34f + 7d54183 + 02c4404 verified 3/3 via strict prefix match `^(<hash>)$`; bsub_wrapper.sh case statement enforces -W=5760 for serial via `*` default; W1 outcome resolved BRANCH_PSD_FIRM in CONTEXT.md) |
| D2  | 28 R1 R-pair targets identified | **PASS** — 28 disk-resident R1 pair_ids cross-checked against coloc_manifest.tsv; strict-correct R2 exclusion via `comm -23` of `coloc_susie/` ∖ `coloc_susie_R2/` (NOT regex `^SH2B3_12q24__EUR__`); 4 SH2B3 R1 entries (3 AFR + 1 EUR `asthma_vs_t2d`) correctly retained per manuscript L138 breakdown 16 EUR + 12 AFR |
| D3  | R1 cache backed up to timestamped path (Pitfall 5) | **PASS** — `mv` (NOT rm) to `results/multitrait/coloc_susie.preFix.bak.20260506_141119Z/` (28 JSONs); rollback path preserved on disk; sentinel at `ta-r3-W2-backup-path.txt` |
| D4  | Snakemake re-fire dispatched with required flag set | **PASS** — `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Snakemake 7.32.4 / Python 3.11 per `project_python_311_pin.md`); flags `--profile config/cluster_lsf --use-conda --conda-prefix .snakemake/conda --jobs 50 --keep-going --rerun-incomplete --latency-wait 120 --forcerun run_coloc_susie --until run_coloc_susie`; exit code 0; 28/28 jobs finished cleanly |
| D5  | coloc_summary.tsv rebuilt with md5 shift | **PASS** — pre-W2 md5 `558fca45ac37d901028c64429cdecc12` → post-W2 md5 `85ab5aa2ca4b54e0edf2a48dc4c61258` (SHIFTED; W5 closeout appends successor row to `md5_baseline.tsv`); rebuild via inline-pandas W5-style merge of R1 + R2 dirs (37 rows = 28 R1 + 9 R2); R2 wins on collision per W5 SUMMARY semantics |
| D6  | SH2B3 R2 rows preserved (risk register row 4) | **PASS** — 9 SH2B3 R2 JSONs in `coloc_susie_R2/` UNTOUCHED (count=9 at start AND end of W2); 9 SH2B3 R2 rows present in rebuilt summary (5 with non-empty PP.H4 = same as pre-W2; 4 row-level placeholders for the structurally-collapsed pairs at niter=1000) |
| D7  | W2 outcome branch classified per OSF amendment paragraph (e) | **PASS** — `BRANCH_R1_STRUCTURAL` (R1_non_empty_PP.H4_rows = 0 of 28; Layer-2-attrition framing empirically supported; cache-staleness alternative refuted) |
| D8  | LSF wall-time observed vs projected | **PASS** — projected ~30 min wall (envelope ~10-30 min/pair × 28 pairs / 50 LSF slots); observed ~9 min wall (Snakemake 28-job run from 2026-05-06T14:13:00Z to 2026-05-06T14:22:17Z); most jobs were no-ops in coloc.susie sense (status=no_signal returns quickly when n_cs_a=0 or n_cs_b=0) |
| D9  | Manuscript md5 invariant | **PASS** (md5 = `2a57c1a061f0c66988a55d1d6600efdf` at entry AND exit; lock-at-entry semantic preserved through Wave 2 closeout; manuscript edits OUT of phase scope) |
| D10 | W3 GO/NO-GO status | **GO (already FIRES; W1-driven)** — `D-TA-R3-W3-GATE = FIRES` was resolved at W1 closeout (driven by `BRANCH_PSD_FIRM`); W2 outcome flows to manuscript narrative only; does NOT change W3 gate disposition |
| D11 | Honest-framing-lock invariant preservation | **PASS** (md5 unchanged through 3 atomic commits + 1 .gitignore allowlist edit; no manuscript edits; framing language used: "audit-driven re-analysis" / "falsification test that did not falsify") |

## Falsification-test Result Detail

**Hypothesis under test (audit-V2 §HQ#2(iii)):** The 28-of-28 empty PP.H3/PP.H4 rows at non-SH2B3 trait-pairs in `coloc_summary.tsv` reflect either (a) a propagation gap in the variant-ID-format-fix commits 069b34f + 7d54183 + 02c4404 (these were re-applied to SH2B3 R2 but never to the 28 non-SH2B3 pairs), OR (b) structural Layer-2 attrition at the GWAS×LD-panel SNP intersection that no variant-ID-format fix can rescue.

**Pre-registered decision rule (OSF amendment 2026-05-04 paragraph (e)):**
- `BRANCH_R1_BUG` if R1 non-empty PP.H4 ≥ 1 post-refire (cache-staleness; the fix commits unblock previously-empty rows)
- `BRANCH_R1_STRUCTURAL` if R1 non-empty PP.H4 = 0 post-refire (Layer-2-attrition; the fix commits work correctly but cannot rescue rows whose upstream credible-sets are vacant)

**Empirical result:** R1_non_empty_PP.H4_rows = 0 / 28 post-refire (Δ=0 vs pre-W2 baseline of 0/28). All 28 R1 JSONs return `status = "no_signal"` with `n_cs_a = 0` OR `n_cs_b = 0` (or both). The variant-ID matcher works correctly — coloc.susie reads pre-fitted SuSiE-RSS objects from `results/fine_mapping/susie/{trait}.{ancestry}.{region}.fit.rds` and returns no_signal because the upstream Layer-1 fits resolve no credible set on at least one trait at that region × ancestry.

**Decision:** **BRANCH_R1_STRUCTURAL.** The cache-staleness alternative is refuted. The Layer-2-attrition framing in the manuscript Discussion §"Layer-2 colocalization-feasibility yield" + Discussion §"Identity-LD Inflation" + Limitations bullet 5 survives the reviewer-defensible re-application of the fix commits.

**Why this is a publishable result, not a null:** The audit-V2 §HQ#2(iii) reviewer objection was that the 28/28 empty-PP narrative reads as result-conditional analysis selection (fixes applied to SH2B3 only). This W2 closes that objection: the fix commits ARE re-applied to the full 28-pair set; the empty-PP rows persist; the structural framing is empirically supported. A counter-factual `BRANCH_R1_BUG` outcome would have produced new PP rows in the 28 R1 cells under HEAD code and refuted the manuscript's Layer-2-attrition narrative. Both branches were pre-registered in the OSF amendment paragraph (e) BEFORE this re-fire executed; the empirical realization is BRANCH_R1_STRUCTURAL.

**Representative R1 failure mode:**

| pair_id | trait_a | trait_b | n_cs_a | n_cs_b | coloc.susie status |
|---|---|---|---|---|---|
| APOL1_22q12__EUR__asthma_vs_stroke | asthma | stroke | 0 | 0 | no_signal |
| FTO_16q12__AFR__asthma_vs_t2d | asthma | t2d | 0 | 4 | no_signal (Layer-1 attrition asymmetric: t2d has 4 CS but asthma has 0; coloc.susie has no CS-pair to test) |

The FTO_16q12 AFR asthma_vs_t2d cell illustrates the structural pattern: even when one side has non-empty credible sets, the partner side's vacancy is the binding constraint. Cross-region: 0 of 28 R1 pair-rows have BOTH n_cs_a ≥ 1 AND n_cs_b ≥ 1 — the binding constraint is upstream Layer-1 fine-mapping convergence at non-Tier-A regions × non-canonical trait combinations.

## LSF Dispatch Manifest (28 R1 R-pair targets)

Recorded at `logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log`. Snakemake confined the DAG to `run_coloc_susie` via `--until run_coloc_susie` (28 forced jobs + 14 upstream-dependency steps that were already up-to-date = 42 DAG steps; only the 28 forced jobs actually executed code). Wall envelope per-job: <1 min (status=no_signal returns quickly when CS vacancy short-circuits coloc.susie).

| pair_id | n_cs_a | n_cs_b | status | PP.H4 |
|---|---|---|---|---|
| APOL1_22q12__AFR__asthma_vs_stroke | 0 | 0 | no_signal | (empty) |
| APOL1_22q12__AFR__asthma_vs_t2d | 0 | 0 | no_signal | (empty) |
| APOL1_22q12__AFR__stroke_vs_t2d | 0 | 0 | no_signal | (empty) |
| APOL1_22q12__EUR__asthma_vs_stroke | 0 | 0 | no_signal | (empty) |
| APOL1_22q12__EUR__asthma_vs_t2d | 0 | 0 | no_signal | (empty) |
| APOL1_22q12__EUR__stroke_vs_t2d | 0 | 0 | no_signal | (empty) |
| CXADR_F2RL1_6p21__EUR__bmi_vs_stroke | (var) | (var) | no_signal | (empty) |
| FTO_16q12__AFR__asthma_vs_stroke | (var) | (var) | no_signal | (empty) |
| FTO_16q12__AFR__asthma_vs_t2d | 0 | 4 | no_signal | (empty) |
| FTO_16q12__AFR__stroke_vs_t2d | (var) | (var) | no_signal | (empty) |
| FTO_16q12__EUR__asthma_vs_bmi | (var) | (var) | no_signal | (empty) |
| ... (17 more R1 pairs) | | | no_signal | (empty) |

Full per-pair table available in `results/multitrait/coloc_susie/*.json` (gitignored — regenerable from manifest + HEAD code via the same Snakemake invocation).

## Atomic commits (Wave 2 closeout)

| commit    | scope                                                                                                     |
| --------- | --------------------------------------------------------------------------------------------------------- |
| `03716d9` | feat(ta-r3, W2): identify 28 R1 R-pair targets + pre-W2 baseline + R1 cache mv-backup (audit-driven re-analysis) |
| `d9707df` | feat(ta-r3, W2): cache-invalidate + Snakemake re-fire 28 R1 trait-pair coloc.susie targets (audit-driven re-analysis; HEAD = 069b34f + 7d54183 + 02c4404) |
| `03335a4` | docs(ta-r3, W2): record D-TA-R3-W2-BRANCH_R1_STRUCTURAL (audit-driven re-analysis; R1 non-empty=0/28, SH2B3 R2 non-empty=5/9) |
| (this)    | docs(ta-r3, W2): finalize SUMMARY + STATE.md / ROADMAP.md refresh — Wave 2 closeout (audit-driven re-analysis) |

All 4 commits use explicit-path staging (per `.planning/feedback_multi_terminal_staging.md` memory; never `git add .` / `-A`). The Co-Authored-By trailer is on each commit per CLAUDE.md GSD enforcement.

## Deviations from Plan

### [Rule 1 - Plan literal] PLAN safety check `^SH2B3_12q24__EUR__` is too aggressive

- **Found during:** Task 1 step 2 (R1 target identification).
- **Issue:** PLAN literal at L274 + L283 used the regex `^SH2B3_12q24__EUR__` to verify "no SH2B3 R2 pair_ids leaked into the R1 target list." The intent is "exclude the 9 R2 pair_ids that live in `coloc_susie_R2/`." But the regex `^SH2B3_12q24__EUR__` matches BROADER than the 9 R2 pair_ids — it also matches the 1 SH2B3 EUR R1 pair `asthma_vs_t2d` which legitimately lives in `coloc_susie/` (R1 cache, NOT R2 cache; this is one of the audit-V2 "28 R1 trait-pair attempts at non-SH2B3 regions" set per manuscript L138 breakdown "16 EUR (... + SH2B3_12q24 × 1 EUR) + 12 AFR (... + SH2B3_12q24 × 3 AFR) = 28").
- **Fix:** Replaced the regex predicate with a strict-correct set-difference predicate via `comm -23 <(R1_disk_pairs) <(R2_disk_pairs)`. This produces exactly 28 R1 target pair_ids that are on disk in `coloc_susie/` but NOT in `coloc_susie_R2/`. The 4 SH2B3 R1 entries (3 AFR + 1 EUR `asthma_vs_t2d`) are correctly retained in the target list per the manuscript's documented breakdown.
- **Files modified:** `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv` (28 rows; correct count).
- **Verification:** `comm -12 <(awk -F'\t' 'NR>1 {print $NF}' ta-r3-W2-r1-targets.tsv | sort) <(ls results/multitrait/coloc_susie_R2/*.json | sed 's|.*/||;s|\.json$||' | sort)` returns 0 lines (NO R2 pair_ids in target list).
- **Commit:** `03716d9`

### [Rule 1 - Plan literal] Manuscript md5 acceptance-criteria literal `63fd8138...` is stale

- **Found during:** Task 1 step 1 pre-fire gate verification.
- **Issue:** PLAN acceptance-criteria literal at multiple sites (Task 1 + Task 2 + Task 3) asserts `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`. The actual on-disk md5 at W2 entry is `2a57c1a061f0c66988a55d1d6600efdf` — the lock-at-entry value captured at W1 closeout per the W1 SUMMARY's `MANUSCRIPT-MD5-AT-ENTRY drifted from plan-mode literal` deviation block. The W2 PLAN was authored against the same stale plan-mode literal as the W1 PLAN.
- **Fix:** Per CLAUDE.md critical_constraints rule 1 ("If the PLAN's automated verify steps reference the stale literal, override the md5 check to use the live `2a57c1a061f0c66988a55d1d6600efdf` value"), all md5-equality checks in this Wave 2 execution use the live value. The substantive intent ("manuscript unchanged through this phase") is preserved; the literal is a definitional refresh.
- **Files modified:** none (plan-literal note; no on-disk fix needed).
- **Verification:** md5 at W2 entry AND exit = `2a57c1a061f0c66988a55d1d6600efdf` (unchanged; lock holds for full Wave 2).
- **Commit:** N/A (operational; documented here for audit trail)

### [Rule 1 - Plan literal] Snakemake all-rule pollution under `--forcerun run_coloc_susie`

- **Found during:** Task 2 step 2 dry-run inspection.
- **Issue:** PLAN literal at L335-345 runs `snakemake --forcerun run_coloc_susie [28 explicit JSON targets]` without confining the DAG. A Snakefile-level `all` rule treats those targets as members of a larger graph, pulling in 14 unrelated rules (build_pgs_manifest, run_mr_placeholder, run_multitrait_placeholder, run_pgs_placeholder, summarize_hyprcoloc, augment_coloc_summary, etc.) into the DAG. With `--allowed-rules run_coloc_susie` Snakemake aborts with `MissingInputException` because the all-rule's other inputs are missing.
- **Fix:** Used `--until run_coloc_susie` to confine forced execution to that rule. The DAG still contains 42 reachable steps but only the 28 forced jobs actually execute code; the upstream 14 are existing-output-as-up-to-date short-circuits. Snakemake exits 0 cleanly.
- **Files modified:** none (operational decision).
- **Verification:** `grep -c "Finished job" logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log` returns 28 (all forced run_coloc_susie targets); `grep "exit code: 0" logs/...` returns one match.
- **Commit:** `d9707df`

### [Rule 2 - Missing Critical] coloc_summary.tsv rebuild requires merge of 2 cache namespaces

- **Found during:** Task 2 step 5 inspection of `summarize_coloc_results` Snakemake rule.
- **Issue:** PLAN literal at L389-396 calls `snakemake --forcerun summarize_coloc_results results/multitrait/coloc_summary.tsv`. But that rule reads ONLY `--coloc-dir results/multitrait/coloc_susie/` (one dir; reads from the manifest). The pre-W2 37-row coloc_summary.tsv was built by the ta-sh2b3 W5 inline-pandas merge that read BOTH `coloc_susie/` AND `coloc_susie_R2/` and merged them into a 37-row TSV (28 R1 + 9 R2). Re-running `summarize_coloc_results` would have produced a smaller / different summary that drops the 9 SH2B3 R2 rows — violating the PLAN's risk register row 4 ("9 SH2B3 R2 rows in coloc_summary.tsv preserved").
- **Fix:** Replicated the W5 inline-pandas merge approach (read both dirs; R2 wins on collision; matches W5 SUMMARY semantics). This is documented in `.planning/quick/260501-wdn-w5-aggregator-figure-refresh-frozen-numb/260501-wdn-SUMMARY.md` L110. The inline merge is committed as part of the dispatch log (the Python heredoc body). 37 rows produced; SH2B3 R2 floor preserved at row level.
- **Files modified:** `results/multitrait/coloc_summary.tsv` (rebuilt under merge; pre-W2 md5 → post-W2 md5 SHIFTED).
- **Verification:** `awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l` returns 9 (R2 rows preserved); 5 of 9 with non-empty PP.H4 (matches pre-W2 baseline).
- **Commit:** `d9707df`

### [Rule 2 - Missing Critical] .gitignore allowlist for results/multitrait/coloc_summary.tsv + W2 dispatch log

- **Found during:** Task 2 step 8 commit-staging.
- **Issue:** `.gitignore` line 88 has `results/*` blanket-ignore. Without an explicit allowlist for the rebuilt `coloc_summary.tsv` and the dispatch log, downstream waves (W5 closeout) and verifier passes would be unable to trace the artifact + W2 atomic commit chain. The PLAN literal at L441-443 contemplates this contingency (`grep -n "results/multitrait/coloc_susie" .gitignore || git add results/multitrait/coloc_susie/*.json`) — but only for the per-pair JSONs, NOT for the load-bearing `coloc_summary.tsv` itself. Per `.planning/feedback_rigor_over_speed.md`, commit-tracking is the rigor-preferred default.
- **Fix:** Added allowlist lines to `.gitignore`: `!results/multitrait` + `results/multitrait/*` + `!results/multitrait/coloc_summary.tsv` + `!logs/ta_r3_W2_r1_refire` + `logs/ta_r3_W2_r1_refire/*` + `!logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log`. Per-pair JSONs in `coloc_susie/` and `coloc_susie_R2/` REMAIN gitignored (regenerable; large; matches W1 + Stage 2 conventions). The W2 namespace allowlist parallels the W1 `fine_mapping_psd_regularized` pattern.
- **Files modified:** `.gitignore`
- **Verification:** `git check-ignore results/multitrait/coloc_summary.tsv` returns NOT IGNORED; `git check-ignore results/multitrait/coloc_susie/APOL1_22q12__EUR__asthma_vs_stroke.json` returns IGNORED (correct — per-pair JSONs stay regenerable).
- **Commit:** `d9707df`

### [Rule 1 - Plan literal] HEAD ancestor grep is loose (false-positive on commit-message string mention)

- **Found during:** Final invariant verification post-Task-2 commit.
- **Issue:** PLAN acceptance-criteria literal at multiple sites uses `git log --oneline | grep -cE '069b34f|7d54183|02c4404'`. The Task 2 commit message itself contains the string "HEAD = 069b34f + 7d54183 + 02c4404" — which causes the grep to count 4, not 3, when run after Task 2 commits. This is a false-positive on string mention, not an invariant violation.
- **Fix:** Use the strict prefix predicate `git log --oneline | awk '{print $1}' | grep -cE '^(069b34f|7d54183|02c4404)$'` which counts only the actual commit-hash prefixes at the start of oneline output. Returns 3 (correct).
- **Files modified:** none (verification refinement; no on-disk fix needed).
- **Verification:** Strict count = 3. The 3 commits ARE HEAD ancestors and remain so throughout W2. The PLAN's loose grep is a false-positive concern that does not affect the substantive invariant.
- **Commit:** N/A (audit-trail note)

**Total deviations:** 3 plan-literal Rule 1 fixes (R2 exclusion regex, manuscript-md5 stale literal, ancestor-grep false positive) + 2 Rule 2 missing-critical adds (W5-style merge for summary rebuild, .gitignore allowlist for new namespace artifacts) + 1 operational decision (Snakemake `--until` to confine DAG). **Impact:** plan-literal bugs would have caused the W2 acceptance criteria to fail mechanically (false negatives) or, in the case of the summary-rebuild rule choice, would have violated risk register row 4 by dropping the 9 SH2B3 R2 rows. Net result: all 11 done-criteria PASS; W2 closes cleanly with BRANCH_R1_STRUCTURAL recorded in CONTEXT.md.

## Authentication Gates

None — all operations were on-cluster compute against locally-committed substrate. The Snakemake LSF profile dispatch ran inside the existing user session; no portal logins, API tokens, or credential refreshes were involved.

## Self-Check: PASSED

- [x] `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv` exists with 28 data rows
- [x] `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv` exists
- [x] `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt` exists with `85ab5aa2ca4b54e0edf2a48dc4c61258` payload
- [x] `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv` exists with `computed_W2_branch=BRANCH_R1_STRUCTURAL` row
- [x] `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-backup-path.txt` exists with `coloc_susie.preFix.bak.20260506_141119Z` sentinel
- [x] `results/multitrait/coloc_summary.tsv` rebuilt; md5 = `85ab5aa2ca4b54e0edf2a48dc4c61258` (≠ `558fca45ac37d901028c64429cdecc12` baseline)
- [x] `results/multitrait/coloc_susie/*.json` count = 28 (re-fired R1 JSONs under HEAD code)
- [x] `results/multitrait/coloc_susie.preFix.bak.20260506_141119Z/*.json` count = 28 (pre-W2 backup intact)
- [x] `results/multitrait/coloc_susie_R2/*.json` count = 9 (UNTOUCHED throughout W2)
- [x] `logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log` exists; non-empty; contains `exit code: 0` line
- [x] HEAD ancestors strict-count = 3 (commits 069b34f + 7d54183 + 02c4404 verified at start AND end of W2 via `^(<hash>)$` prefix match)
- [x] `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` contains `D-TA-R3-W2-BRANCH_R1_STRUCTURAL`; PENDING placeholder removed
- [x] `D-TA-R3-W3-GATE = FIRES` block UNCHANGED in CONTEXT.md (W3 gate is W1-driven; W2 outcome flows to manuscript narrative only)
- [x] Manuscript md5 = `2a57c1a061f0c66988a55d1d6600efdf` at entry AND exit (lock-at-entry value preserved)
- [x] 3 atomic Wave-2 commits at HEAD: `03716d9` (Task 1) + `d9707df` (Task 2) + `03335a4` (Task 3)
- [x] All commits use explicit-path staging (no `git add .` / `-A`); Co-Authored-By trailer present
- [x] No prior-wave artifacts modified except the W2-specific new block in CONTEXT.md (W1 SUMMARY UNCHANGED; W1 fits UNCHANGED; W3 gate token UNCHANGED)

**Self-Check verdict:** PASS for the full W2 plan (Tasks 1 + 2 + 3 + closeout SUMMARY + STATE.md + ROADMAP.md refresh). Wave 2 closeout complete; W3 gate already FIRES (W1-driven; this wave does not change it); manuscript narrative branch implication is informational and OUT of phase scope.

## Threat Flags

None — W2 dispatched via existing Snakemake rule (`run_coloc_susie`) against existing in-tree LD references and harmonized sumstats. The audit's HQ#2(iii) finding's falsification test is itself the subject of W2; no new network endpoints, auth paths, file access patterns, or schema changes were introduced. The .gitignore allowlist edit is a process change (commit-tracking) not a security-surface change.
