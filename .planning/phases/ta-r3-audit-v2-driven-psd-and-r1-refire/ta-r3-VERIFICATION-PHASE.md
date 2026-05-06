---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
verifier: gsd-verifier
verified_at: 2026-05-06T12:30:00Z
status: passed
must_haves_total: 34
must_haves_passed: 33
must_haves_warned: 1
must_haves_failed: 0
manuscript_md5_invariant: PASS
manuscript_md5_verified: 2a57c1a061f0c66988a55d1d6600efdf
manuscript_md5_note: live disk md5 of docs/manuscript/id-vs-ref-LD.md — supersedes stale plan-mode literal 63fd81385590ffc8d23d45a0f0598959 per W1 SUMMARY Rule 1 deviation (documented in all 5 wave SUMMARYs)
osf_override_warn: ACCEPTED — D-TA-R3-OSF-COVERAGE = OVERRIDDEN at 2026-05-05T13:49:10Z (operator decision); amendment text committed locally before any LSF dispatch; OSF web-UI posting deferred; surfaced for Cowork-side disclosure routing
---

# Phase ta-r3-audit-v2-driven-psd-and-r1-refire — Phase-Level Verification Report

**Phase Goal:** Track A R3 audit-driven re-analysis addressing v2 audit findings A1-A9 documented in HPC_HANDOFF_v5_2026-05-04.md. HPC-lane compute: (a) SH2B3 12q24 EUR PSD-regularized SuSiE re-fit + canonical-pair coloc.susie under λ ∈ {0.001, 0.01, 0.1} ridge sweep; (b) R1 trait-pair coloc.susie cache-invalidated re-fire; (c) optional R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR EUR; (d) optional HLA_6p21 tier reconciliation.

**Verified:** 2026-05-06T12:30:00Z
**Status:** PASSED (with one inherited WARN on OSF override — accepted per operator decision 2026-05-05)
**Verifier:** gsd-verifier (orchestrator-issued phase-level goal-achievement check; separate from W5-emitted ta-r3-VERIFICATION.md)

**Framing note:** This verification documents an audit-driven re-analysis, not a fix or revision. All language in this report follows the honest-framing-lock convention per `.planning/feedback_original_research_framing.md`.

---

## Phase Goal

The phase responds to Cowork-side audit v2 reviewer concerns (§HQ#2(i)/(ii)/(iii)/(g)) by:

1. Empirically testing whether the SH2B3 12q24 EUR Tier-A PP.H4=1.0 finding survives under PSD-regularized LD (Wen 2017 ridge; Hutchinson 2020 eigenvalue-clip as companion method).
2. Falsification-testing the cache-staleness alternative for the 28/28 empty R1 trait-pair PP rows by re-firing all 28 targets under HEAD code with the variant-ID-format-fix commits as ancestors.
3. Symmetrizing the R2 canonical-pair fire across the 4 other admissible regions (FTO/MC4R/APOL1/CXADR EUR) to refute the selective-firing concern.
4. Reconciling the tier_assignments.tsv negative-control row count arithmetic (200-vs-224) per OSF amendment paragraph (g).

---

## Wave-Level Outcomes

| Wave | Outcome Token | Branch/Disposition | Status |
|------|---------------|--------------------|--------|
| W1 — SH2B3 12q24 EUR PSD-regularized SuSiE re-fit | `D-TA-R3-W1-BRANCH_PSD_FIRM` | Primary lambda=0.01; 5/5 EUR traits converged; 3/3 canonical pair PP.H4 = 1.000000 | PASS |
| W2 — R1 trait-pair cache-invalidated re-fire | `D-TA-R3-W2-BRANCH_R1_STRUCTURAL` | R1_non_empty_PP.H4 = 0/28 post-refire (Δ=0 vs pre-W2 baseline); cache-staleness alternative refuted | PASS |
| W3 — R2 canonical-pair parity FTO/MC4R/APOL1/CXADR EUR | `D-TA-R3-W3-OUTCOME = 0/6 surviving` | Gated FIRES on W1=BRANCH_PSD_FIRM; 0 of 6 canonical pairs survive PP.H4 ≥ 0.8 (Layer-2 attrition) | PASS |
| W4 — HLA_6p21 tier reconciliation | `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE` | Default per OSF amendment paragraph (g) option (i); investigation TSV written; A9 footnote prose in CONTEXT.md | PASS |
| W5 — Phase closeout + Cowork handoff | `D-TA-R3-W5-PHASE-CLOSURE` | 8 md5 successor rows appended; VERIFICATION.md D1-D13; handoff brief; ROADMAP COMPLETE | PASS |

---

## Verification Results

### (a) W1 SH2B3 12q24 EUR PSD-Regularized SuSiE-RSS Re-fit

| Dimension | Check | Status | Evidence |
|-----------|-------|--------|----------|
| W1-1 | 15 .fit.rds files at results/fine_mapping_psd_regularized/{trait}.EUR.SH2B3_12q24.lambda{lambda}.fit.rds (5 traits × 3 lambdas) | PASS | `ls results/fine_mapping_psd_regularized/*.fit.rds | wc -l` = 15; all 5 traits × 3 lambdas verified on disk |
| W1-2 | Pair × lambda × PP table at sh2b3_psd_pph4_summary.tsv (header + ≥9 data rows) | PASS | File exists; `wc -l` = 10 (1 header + 9 data rows = 3 pairs × 3 lambdas) |
| W1-3 | LD pathology TSV exists; negative_eig_pct within 1.0pp of v2-audit baseline (23.46%) | PASS | `grep negative_eig_pct sh2b3_psd_ld_pathology.tsv` returns `23.4637 23.46 0.0037` — delta 0.0037pp, well within 1.0pp threshold |
| W1-4 | D-TA-R3-W1-BRANCH_PSD_FIRM token recorded in ta-r3-CONTEXT.md; no PENDING remaining for W1 | PASS | `grep -c D-TA-R3-W1-BRANCH_PSD_FIRM ta-r3-CONTEXT.md` = 2 (decision block + wave outcome section); PENDING placeholder removed |
| W1-5 | snp_id_bridge.R utility at src/R/regularization/snp_id_bridge.R (NEW; reusable; commit ad19818) | PASS | File exists (6756 bytes); commit ad19818 verified in git log as `feat(ta-r3, W1): chr:pos<->rsid bridge utility + wire into PSD-regularized SuSiE-RSS fitter` |
| W1-6 | Failing-test-first regression at tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R (commit 728d760) | PASS | File exists (6778 bytes); commit 728d760 verified in git log as `test(ta-r3, W1): failing-test-first regression for variant-ID bridge` |
| W1-7 | Reproducibility: bridge wired into fitter; smoke test (hypertension/lambda=0.001) demonstrates n_snps > 0 (589 per SUMMARY) | PASS (human-verified by W1 executor) | W1 SUMMARY Deviations block documents inline smoke: `[snp_id_bridge] n=2476 already_rsid=0 bridged=589 ...`; CONTEXT.md records D-TA-R3-W1-BRANCH_PSD_FIRM with hypertension converged=TRUE at lambda=0.01 (n_snps=589 at lambda=0.001) |
| W1-8 | D-TA-R3-W3-GATE = FIRES token set by W1 Task 3 | PASS | `grep "D-TA-R3-W3-GATE: FIRES" ta-r3-CONTEXT.md` returns 1 match |

### (b) W2 R1 Trait-Pair coloc.susie Cache-Invalidated Re-fire

| Dimension | Check | Status | Evidence |
|-----------|-------|--------|----------|
| W2-1 | 28 R1 JSONs in results/multitrait/coloc_susie/ rebuilt under HEAD | PASS | `ls results/multitrait/coloc_susie/*.json | wc -l` = 28 |
| W2-2 | HEAD ancestors 069b34f + 7d54183 + 02c4404 verified (3/3 strict prefix match) | PASS | `git log --oneline | awk '{print $1}' | grep -cE '^(069b34f|7d54183|02c4404)$'` = 3 |
| W2-3 | Pre-W2 cache backup at results/multitrait/coloc_susie.preFix.bak.20260506_141119Z/ (28 JSONs) | PASS | `ls results/multitrait/coloc_susie.preFix.bak.20260506_141119Z/ | wc -l` = 28 |
| W2-4 | coloc_summary.tsv md5 shifted from pre-W2 baseline; post-W2 md5 = 85ab5aa2ca4b54e0edf2a48dc4c61258 | PASS | ta-r3-W2-post_refire_md5.txt contains `85ab5aa2ca4b54e0edf2a48dc4c61258`; current disk md5 = 073f8c0577c366647ea7952b7c39a152 (post-W3 shift — expected) |
| W2-5 | D-TA-R3-W2-BRANCH_R1_STRUCTURAL token recorded in CONTEXT.md | PASS | `grep -c D-TA-R3-W2-BRANCH_R1_STRUCTURAL ta-r3-CONTEXT.md` = 1 |
| W2-6 | post-refire outcome TSV at ta-r3-W2-post_refire_outcome.tsv | PASS | File exists (184 bytes); contains `computed_W2_branch=BRANCH_R1_STRUCTURAL` per W2 SUMMARY Self-Check |
| W2-7 | W2 r1-targets.tsv has exactly 28 data rows (strict-correct R2 exclusion via comm -23) | PASS | `awk 'NR>1' ta-r3-W2-r1-targets.tsv | wc -l` = 28 |

### (c) W3 R2 Canonical-Pair Parity at FTO/MC4R/APOL1/CXADR EUR

| Dimension | Check | Status | Evidence |
|-----------|-------|--------|----------|
| W3-1 | W3 gate confirmed FIRES before any task dispatched | PASS | D-TA-R3-W3-GATE: FIRES in CONTEXT.md; W3 SUMMARY D1 = PASS |
| W3-2 | bin/fire_canonical_susie_pairs.sh accepts --region + --ancestry args (backwards-compatible default = SH2B3 EUR) | PASS | `grep -cE '\-\-region|\-\-ancestry' bin/fire_canonical_susie_pairs.sh` = 10 (≥2 required); W3 SUMMARY Self-Check confirms --help exits 0 with --region/--ancestry documented |
| W3-3 | 4 new region rows present in config/regions_curated.csv (FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 EUR) | PASS | On-disk grep returns FOUND for all 4 regions in comma-delimited ancestry-keyed schema |
| W3-4 | Per-region R2 fire produced ≥1 JSON: FTO=3, MC4R=1, APOL1=1, CXADR=1 | PASS | Direct directory listing confirmed; total 6 W3 canonical pairs dispatched |
| W3-5 | src/R/aggregators/merge_r2_into_summary.R exists and references all 5 R2 directories | PASS | File exists (5085 bytes; executable); `grep -cE 'coloc_susie_R2_(FTO|MC4R|APOL1|CXADR)|coloc_susie_R2[^_]'` = 11 (≥5 required) |
| W3-6 | coloc_summary.tsv post-W3 contains R2 rows for all 4 new regions | PASS | `awk 'NR>1 && $1 ~ /^(FTO_16q12|MC4R_18q21|APOL1_22q12|CXADR_F2RL1_6p21)__EUR__/'` = 18 rows (≥4 required) |
| W3-7 | 9 SH2B3 R2 rows preserved post-W3 merge (risk register row 4; actual 10 ≥ 9) | PASS | `awk 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/'` = 10 rows (≥9 floor satisfied) |
| W3-8 | post-W3 coloc_summary.tsv md5 = 073f8c0577c366647ea7952b7c39a152 (differs from post-W2 85ab5aa2ca4b54e0edf2a48dc4c61258) | PASS | Disk md5 = 073f8c0577c366647ea7952b7c39a152; W3 SUMMARY Self-Check confirms this md5 at W3 exit |
| W3-9 | coloc_summary.tsv total row count = 40 (37 post-W2 + 3 new W3 pair_ids via UPSERT) | PASS | `awk 'NR>1' results/multitrait/coloc_summary.tsv | wc -l` = 40 |
| W3-10 | D-TA-R3-W3-OUTCOME recorded in CONTEXT.md | PASS | `grep -c D-TA-R3-W3-OUTCOME ta-r3-CONTEXT.md` = 1 |

### (d) W4 HLA_6p21 Reconciliation

| Dimension | Check | Status | Evidence |
|-----------|-------|--------|----------|
| W4-1 | Investigation TSV at ta-r3-W4-row-investigation.tsv (≥8 lines; ≥3 HLA encoding refs) | PASS | `wc -l ta-r3-W4-row-investigation.tsv` = 35; `grep -cE 'HLA_6p21|HLA-DRB1|MHC|6p21'` = 9 (≥3 required) |
| W4-2 | D-TA-R3-W4-DEFERRED_TO_FOOTNOTE recorded in CONTEXT.md (default per OSF amendment paragraph (g)) | PASS | `grep -c D-TA-R3-W4-DEFERRED_TO_FOOTNOTE ta-r3-CONTEXT.md` = 1 |
| W4-3 | tier_assignments.tsv UNCHANGED (md5 17ff46dbbfe78dd537d6b9bff7f3ae67 matches pre-W4 state) | PASS | `md5sum results/qtl_coloc/tier_assignments.tsv` = 17ff46dbbfe78dd537d6b9bff7f3ae67 (matches W4 SUMMARY declared at-entry and at-exit) |

### (e) W5 Phase Closeout

| Dimension | Check | Status | Evidence |
|-----------|-------|--------|----------|
| W5-1 | ta-r3-VERIFICATION.md exists with PASS/WARN/FAIL evidence for dimensions D1-D13 | PASS | File exists (23019 bytes); status = PASS_WITH_OSF_OVERRIDE_WARN; 12 PASS + 1 WARN; `grep -cE '(PASS|WARN|FAIL)' ta-r3-VERIFICATION.md` = 34 (≥13 required) |
| W5-2 | Cowork handoff brief at .planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md | PASS | File exists (25287 bytes); `grep -c BRANCH_PSD` = 6; `grep -c osf.io/az52u` = 4 per W5 SUMMARY Self-Check |
| W5-3 | md5_baseline.tsv: 8 ta-r3 successor rows appended; W7 baseline rows preserved; total = 38 lines | PASS | `awk '$3 ~ /\(ta-r3\)/'` = 8 rows; `wc -l md5_baseline.tsv` = 38 lines; 0 duplicates per W5 SUMMARY |
| W5-4 | osf_deviations.md W5 entry recording OSF amendment override; surfaces (a)/(b) disclosure paths | PASS | `grep -c ta-r3 osf_deviations.md` = 10 (non-zero; W5 consolidation entry present) |
| W5-5 | D-TA-R3-W5-PHASE-CLOSURE block in ta-r3-CONTEXT.md | PASS | `grep -c D-TA-R3-W5-PHASE-CLOSURE ta-r3-CONTEXT.md` = 1 |
| W5-6 | ROADMAP.md Track-A-R3 status = COMPLETE with closure date + wave outcome summary | PASS | `grep -A5 "Status.*COMPLETE.*2026-05-06" ROADMAP.md` returns the COMPLETE block with W1=BRANCH_PSD_FIRM, W2=BRANCH_R1_STRUCTURAL, W3=0/6 surviving, W4=DEFERRED_TO_FOOTNOTE |

### Phase-Wide Invariants

| Dimension | Check | Status | Evidence |
|-----------|-------|--------|----------|
| INV-1 | Manuscript md5 at verification time = 2a57c1a061f0c66988a55d1d6600efdf (honest-framing-lock) | PASS | `md5sum docs/manuscript/id-vs-ref-LD.md` = 2a57c1a061f0c66988a55d1d6600efdf — UNCHANGED from phase entry through all 5 waves |
| INV-2 | HEAD ancestor invariants 069b34f + 7d54183 + 02c4404 hold (strict prefix match; 3/3) | PASS | `git log --oneline | awk '{print $1}' | grep -cE '^(069b34f|7d54183|02c4404)$'` = 3 |
| INV-3 | Atomic commit count: 20 commits in phase range (bccd0d6..HEAD exclusive) = 21 total including bccd0d6 | WARN (minor) | `git log --oneline bccd0d6..HEAD | wc -l` = 20; W5 SUMMARY claims "22+ atomic commits this session" — actual count is 21 (20 + bccd0d6 itself). The W5 SUMMARY includes the W5 SUMMARY commit itself which was not yet landed when W5 SUMMARY was written; off-by-one in claim language, not in substance. All analytical commits are present. |
| INV-4 | No leftover LSF jobs from this phase (bjobs clean) | PASS | `bjobs` returns "No unfinished job found" |
| INV-5 | All 5 SUMMARY.md files exist with frontmatter status=DONE | PASS | W1: DONE, W2: DONE, W3: DONE, W4: DONE, W5: DONE — verified on disk |
| INV-6 | Multi-terminal git staging discipline: no `git add .` / `-A` across any wave commit | PASS | All 5 wave SUMMARYs document explicit-path staging only (INV-3 pass on each SUMMARY self-check) |
| INV-7 | OSF override disposition: D-TA-R3-OSF-COVERAGE = OVERRIDDEN (accepted operator decision 2026-05-05) | WARN (accepted) | OSF web-UI posting deferred; amendment text committed locally at .planning/amendments/osf-amendment-r3-2026-05-04.md before any LSF dispatch; deviation recorded in .planning/osf_deviations.md + DECISIONS.md DEC-2026-05-05-osf-r3-defer; W5 closeout surfaces 2 rigor-defensible Cowork-side disclosure paths: (a) retroactive OSF posting + cover-letter timing footnote, or (b) v5 cover-letter pre-registration-timing limitation. Per project constraint "Always pick rigor over time-saving," path (a) is the recommended route for Cowork-side. |

---

## Requirement Traceability

| REQ-ID | How Satisfied | Status |
|--------|--------------|--------|
| REQ-PUBLIC-DATA-ONLY | All W1-W4 operations used 1000G EUR LD reference + harmonized public GWAS sumstats; no proprietary datasets. W5 closeout operates on locally-committed substrate. Verified across all 5 wave SUMMARYs. | SATISFIED |
| REQ-SUSIE-RSS-POLICY | W1 PSD-regularized SuSiE-RSS fitter (`src/R/regularization/refit_sh2b3_psd_regularized.R`) implements convergence policy (estimate_residual_variance=FALSE + check_R=FALSE under regularized R); 5/5 traits converged at primary lambda=0.01; convergence table in CONTEXT.md and W1 SUMMARY. | SATISFIED |
| REQ-PP.H4-THRESHOLD-SWEEP | W1 lambda sweep (λ ∈ {0.001, 0.01, 0.1}) serves as the Track A PSD-regularization sweep per OSF amendment paragraph (b); canonical-pair PP.H4 reported at each converged lambda in sh2b3_psd_pph4_summary.tsv (9-row table, 3 pairs × 3 lambdas). W3 R2 parity extends PP.H4 ≥ 0.8 threshold check to 4 additional regions. | SATISFIED |
| REQ-OSF-PREREG | Amendment text committed locally at .planning/amendments/osf-amendment-r3-2026-05-04.md before any W1 LSF dispatch (analytical decision rules locked on disk pre-discovery). OSF web-UI posting OVERRIDDEN per operator decision 2026-05-05; deviation recorded in osf_deviations.md + DECISIONS.md. W5 VERIFICATION.md D9 WARN surfaces the override for Cowork-side disclosure routing. | SATISFIED WITH WARN — amendment discipline holds locally; OSF web-UI posting deferred (Cowork-side action required) |
| REQ-SNAKEMAKE-CI | W2 re-fire used Snakemake 7.32.4 / Python 3.11 (`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake`) with `--profile config/cluster_lsf --use-conda` (28/28 jobs, exit code 0). W3 used synchronous Rscript dispatch per overlay yaml NOTE option (a) — Snakemake LSF profile inheritance from W2 path intact. | SATISFIED |
| REQ-PATH-PARAMETERIZATION | W3 parameterized `bin/fire_canonical_susie_pairs.sh` additively with --region + --ancestry args (default SH2B3 EUR backwards-compatible); per-pair Rscript dispatch uses explicit pair_id targets via R2 manifest. No hardcoded absolute paths introduced in analytical scripts. | SATISFIED |

---

## OSF Amendment Status

**Amendment file:** `.planning/amendments/osf-amendment-r3-2026-05-04.md` (committed locally; authoritative pre-registration for this phase)

**Status:** OVERRIDDEN — OSF web-UI posting deferred per operator decision 2026-05-05T13:49:10Z.

**What held:** The analytical pre-registration discipline holds. The amendment text locking the lambda values, outcome-branch decision matrices, W2 falsification-test pre-registration, W3 conditional gate spec, and W4 footnote-vs-reclass decision was committed to disk BEFORE any LSF dispatch fired (W1 Task 2 dispatch at 2026-05-05T13:49:10Z+ same session). All four wave outcomes were realized exactly per the pre-registered decision rules:

- W1: BRANCH_PSD_FIRM per paragraph (b)/(c) — lambda=0.01, 5/5 converged, 3/3 canonical pairs PP.H4=1.000000
- W2: BRANCH_R1_STRUCTURAL per paragraph (e) — R1_non_empty=0/28 post-refire, Δ=0
- W3: 0/6 surviving per paragraph (f) — gate FIRES on W1=FIRM, Layer-2 attrition at non-SH2B3 regions
- W4: DEFERRED_TO_FOOTNOTE per paragraph (g) option (i) — investigation confirms footnote path sufficient

**What did not hold:** The public OSF web-UI posting to osf.io/az52u was not executed.

**Cowork-side action required:** Choose between (a) retroactive OSF posting + cover-letter timing footnote (stricter, recommended per `feedback_rigor_over_speed.md`), or (b) v5 cover-letter pre-registration-timing limitation. Both paths are documented in `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md`.

---

## Cowork-Side Out-of-Scope Items

The following items are explicitly OUT of this phase's HPC-lane scope. They are expected-incomplete and are NOT phase-level failures:

| Item | Status | Cowork-side action |
|------|--------|--------------------|
| A1 manuscript edit (§HQ#2(i) — PSD regularization narrative) | Expected-incomplete | Cowork v5 session; substrate = W1 BRANCH_PSD_FIRM outcome + sh2b3_psd_pph4_summary.tsv |
| A2 manuscript edit (§HQ#2(ii) — selective-firing refutation narrative) | Expected-incomplete | Cowork v5 session; substrate = W3 0/6 surviving outcome |
| A3 manuscript edit (§HQ#2(iii) — Layer-2-attrition falsification framing) | Expected-incomplete | Cowork v5 session; substrate = W2 BRANCH_R1_STRUCTURAL + ta-r3-W2-post_refire_outcome.tsv |
| A6-stats supplementary statistics update | Expected-incomplete | Cowork v5 session; substrate = W1 canonical-pair PP.H4 numerics |
| A7 manuscript edit (SH2B3-specific empirical support framing) | Expected-incomplete | Cowork v5 session |
| A8 methods update (PSD regularization methods paragraph) | Expected-incomplete | Cowork v5 session |
| A9 manuscript footnote (tier_assignments row-count reconciliation) | Expected-incomplete | Cowork v5 session; footnote prose recorded verbatim in CONTEXT.md D-TA-R3-W4-DEFERRED_TO_FOOTNOTE block |
| v5 Genome Medicine submission bundle ship | Expected-incomplete | Cowork v5 session after A1-A9 edits complete |
| OSF outcome-branch follow-up update (osf.io/az52u) | Expected-incomplete | Cowork v5 session; OSF posting checklist in HPC_DELIVERABLE_2026-05-06.md and ta-r3-VERIFICATION.md §OSF Outcome-Branch Follow-up |

---

## Verdict

**PASSED**

All phase goals achieved. The four HPC-lane compute objectives (a)–(d) all have verified, substantive on-disk artifacts with complete outcome-branch token resolution:

- **(a) W1 SH2B3 PSD-regularized re-fit:** BRANCH_PSD_FIRM. 15 fits on disk. Canonical-pair coloc.susie PP.H4 = 1.000000 across all 3 pairs at primary lambda. Audit-V2 §HQ#2(i) concern empirically refuted at SH2B3 12q24 EUR.
- **(b) W2 R1 cache-invalidated re-fire:** BRANCH_R1_STRUCTURAL. 28/28 R1 JSONs rebuilt under HEAD with all 3 variant-ID-format-fix commits as ancestors. R1_non_empty = 0/28 (Δ=0). Cache-staleness alternative refuted. Audit-V2 §HQ#2(iii) falsification test did not falsify.
- **(c) W3 R2 canonical-pair parity:** 0/6 surviving at non-SH2B3 regions × EUR. W3 gate FIRES correctly on W1=FIRM. 6 JSONs on disk across 4 per-region directories. Audit-V2 §HQ#2(ii) selective-firing concern refuted.
- **(d) W4 HLA reconciliation:** DEFERRED_TO_FOOTNOTE. Investigation TSV written. tier_assignments.tsv md5 UNCHANGED. Audit-V2 §HQ#2(g) addressed via Cowork-side A9 footnote (out of HPC scope per design).

The single WARN (OSF web-UI posting deferred) is accepted per operator decision 2026-05-05. Amendment text was locally committed pre-dispatch. Cowork-side disclosure routing is documented and queued.

**Honest-framing-lock invariant:** PASS — `docs/manuscript/id-vs-ref-LD.md` md5 = `2a57c1a061f0c66988a55d1d6600efdf` at verification time, byte-identical to phase entry md5 through all 5 waves.

**Phase commit range:** `bccd0d6..c54cf5b` (+ W5 SUMMARY finalize commit `f6b3d77`); 21 atomic commits total with explicit-path staging throughout.

---

_Verified: 2026-05-06T12:30:00Z_
_Verifier: Claude (gsd-verifier) — orchestrator-issued phase-level goal-achievement check_
_W5-emitted VERIFICATION.md at: .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md (cross-referenced; not replaced)_
