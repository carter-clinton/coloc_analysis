---
status: awaiting_human_verify
trigger: "9 of 15 LSF jobs in ta-r3 W1 PSD-regularized SuSiE-RSS dispatch failed identically with `Error: length(overlap) > 0 is not TRUE` at src/R/regularization/refit_sh2b3_psd_regularized.R:123"
created: 2026-05-06T04:18:18Z
updated: 2026-05-06T04:50:00Z
---

## Current Focus

hypothesis: CONFIRMED. Variant-ID convention drift: sumstats SNP_ID is chr:pos (e.g. "12:111000057") for hypertension/stroke/t2d but rsid (e.g. "rs7957299") for asthma/bmi. LD-ref $variants$SNP_ID is 100% rsid (895/895). Naive `intersect(rownames(R), sub$SNP_ID)` at refit_sh2b3_psd_regularized.R:122 returns 0 for chr:pos sumstats. The (CHR, POS) tuple is the cross-convention bridge — present in BOTH sumstats and LD-ref $variants.
test: Apply CHR/POS-keyed bridge inside fitter (mirroring the structural pattern from commits 069b34f/7d54183 but specialized for the per-position-tuple LD-variants table available here). Write failing-test-first regression covering all 5 traits.
expecting: (1) failing test runs cleanly on current fitter and reproduces stopifnot error for hypertension/stroke/t2d; (2) after fix, all 5 traits resolve to 100% rsid SNP_IDs and pass overlap > 0 stopifnot; (3) inline smoke on hypertension/lambda=0.001 lands a .fit.rds in <30s.
next_action: Implement bridge logic + failing test + apply fix + smoke + redispatch 9 jobs

## Symptoms

expected: All 15 PSD-regularized SuSiE-RSS fits land on disk under results/fine_mapping_psd_regularized/{trait}.EUR.SH2B3_12q24.lambda{lambda}.fit.rds (5 EUR traits × 3 lambda values).

actual: Only 6 of 15 fits landed. asthma × {0.001, 0.01, 0.1} and bmi × {0.001, 0.01, 0.1} succeeded. hypertension × {0.001, 0.01, 0.1}, stroke × {0.001, 0.01, 0.1}, t2d × {0.001, 0.01, 0.1} all failed identically with `Error: length(overlap) > 0 is not TRUE`.

errors: Failure at `stopifnot(length(overlap) > 0)` at src/R/regularization/refit_sh2b3_psd_regularized.R:123. asthma/bmi sumstats use rsid SNP_ID; hypertension/stroke/t2d sumstats use chr:pos SNP_ID; LD-ref $variants$SNP_ID = rsid only → naive intersect → empty.

reproduction:
```bash
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/regularization/refit_sh2b3_psd_regularized.R --trait hypertension --lambda 0.001 --method ridge --out /tmp/hypertension_test.fit.rds
# fails in ~3s
```

started: First introduced 2026-05-05T15:15:41Z (commit bccd0d6 scaffolded fitter; smoke-test was on bmi which masked bug)

## Eliminated

(none yet — bug already triaged in symptoms; investigation will confirm via direct reproduction)

## Evidence

- timestamp: 2026-05-06T04:18:18Z
  checked: knowledge-base.md
  found: Direct match on entry `qtl_coloc_snp_name_mismatch` (2026-04-20) — same class of bug (chr:pos vs rsid drift). Prior fix at commits 069b34f (run_qtl_coloc.R: try three candidate keys + pick max overlap) + 7d54183 (run_susie_rss.R: override chr:pos SNP_IDs with LD-side rsids when LD has clean rsid).
  implication: This is a recurrence of the same structural defect introduced by NEW W1 fitter scaffolded in bccd0d6. The two prior fixes are NOT a callable utility — they are inline patches inside their respective scripts. Need to inline the same bridge in refit_sh2b3_psd_regularized.R.

- timestamp: 2026-05-06T04:18:30Z
  checked: src/R/regularization/refit_sh2b3_psd_regularized.R lines 80-128
  found: Line 87-88 sets `rownames(R) <- ld_variants$SNP_ID` (rsid). Line 122 does naive `intersect(rownames(R), sub[[snpcol]])` with NO chr:pos<->rsid bridge. Line 123 stopifnot fires when overlap is empty.
  implication: Bug is exactly where reported. Fix must operate BEFORE line 122 — bridge sub$SNP_ID to LD-side rsids using (CHR, POS) tuple BEFORE the intersect.

- timestamp: 2026-05-06T04:18:45Z
  checked: zcat data/processed/sumstats_harmonized/{trait}.EUR.tsv.bgz | head -4 (chr12, 111-113Mb)
  found: asthma: SNP_ID=rs7304705, rs561466184, rs55710421. bmi: SNP_ID=rs7957299, rs1265742, rs16940902. hypertension: SNP_ID=12:111000057, 12:111002311, 12:111002958. stroke: SNP_ID=12:111000057, 12:111002311, 12:111002610. t2d: SNP_ID=12:111000026, 12:111000027, 12:111000029.
  implication: Confirms 2-of-5 traits use rsid (asthma/bmi → success), 3-of-5 use chr:pos (hypertension/stroke/t2d → fail). Conventions per trait are stable across the SH2B3 region (no mixed-convention rows).

- timestamp: 2026-05-06T04:19:02Z
  checked: readRDS("data/processed/ld_reference/EUR/SH2B3_12q24.rds") via Rscript
  found: $R is 895x895; $variants has columns SNP_ID,CHR,POS,A1,A2; $variants$SNP_ID is 895/895 rsids (rs7961935, rs7978821, rs7956942, rs4766438, rs4766439...); $variants$CHR=12 throughout; $variants$POS = 111400006, 111400116, 111400127... (GRCh37 12q24 Mb range).
  implication: The (CHR, POS) tuple bridges 100% of LD variants. (Note: pos_lo=111e6 in fitter <= 111400006 — region matches, no edge case.)

- timestamp: 2026-05-06T04:19:30Z
  checked: git show 069b34f + git show 7d54183
  found: 069b34f generalized run_qtl_coloc.R matcher to try {rsid, chrpos, variant_id} and pick max overlap. 7d54183 in run_susie_rss.R overrides subset$SNP_ID with LD-panel rsids when LD has rsids and sumstats has chr:pos. Neither is exposed as a reusable function.
  implication: Best fix here mirrors 7d54183 pattern: build a (CHR, POS) -> rsid map from ld_variants, then for sumstats rows whose SNP_ID is non-rsid (or unmatched against LD rsids), look up rsid via (CHR, POS). Then proceed with intersect.

- timestamp: 2026-05-06T04:19:45Z
  checked: ls /rs1/researchers/c/ckclinto/conda_envs/{la_multitrait_r,r_coloc,rstats-nyabg}/lib/R/library/ for {testthat, susieR, data.table, optparse}
  found: la_multitrait_r has susieR+data.table+optparse but NOT testthat; rstats-nyabg has testthat+data.table but NOT susieR; r_coloc has data.table+susieR+optparse but NOT testthat. No env contains all four.
  implication: Regression test will use base-R `stopifnot()` style instead of testthat — keeps env-stack pristine, runs in la_multitrait_r alongside the fitter, and matches the minimal assertion style needed (just verifying overlap > 0 across all 5 traits).

- timestamp: 2026-05-06T04:20:00Z
  checked: logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log + logs/sh2b3_psd_refit/115619.out (LSF env block)
  found: Original dispatch was direct bsub loop (no committed wrapper script). Per dispatch log header: queue=serial -W=5760 mem=32 GB -n 1. Per LSF .out: each job ran on c023n01, executed under cwd=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis, command body = `Rscript src/R/regularization/refit_sh2b3_psd_regularized.R --trait <T> --lambda <L> --method ridge --out results/fine_mapping_psd_regularized/<T>.EUR.SH2B3_12q24.lambda<L>.fit.rds`. Wall=0.2-1.5s for successful runs; ~3s for failures.
  implication: Redispatch can replicate the exact bsub flags inline. The 9 redispatch jobs must overwrite the existing failed-status outputs (none landed for those 9 cells) so no cleanup needed.

- timestamp: 2026-05-06T04:35:00Z
  checked: smoke test of bridged fitter on hypertension/lambda=0.001
  found: WROTE /tmp/hypertension_smoke.fit.rds; n_snps=589, dropped=1887, n_CS=4, converged=FALSE, niter=1000, wall=47.8s. Susie fit object structurally complete (alpha, mu, mu2, KL, lbf, ..., sets, pip). 589 matches commit 7d54183's prior-fix expected count exactly.
  implication: Bridge resolves the original failure mode. converged=FALSE at lambda=0.001 is expected — that's exactly the pathology the lambda sweep is designed to characterize; W1 PLAN's branch decision matrix accepts that as a Branch-A/B input.

- timestamp: 2026-05-06T04:36:30Z
  checked: re-run of asthma/lambda=0.001 + bmi/lambda=0.001 against the existing landed fits at results/fine_mapping_psd_regularized/
  found: bmi unchanged (n_snps=170, n_CS=10, converged=FALSE — identical to landed). asthma drifts by +1 SNP (was 700, now 701) because the bridge rescued one asthma sumstats row whose original SNP_ID was non-rsid but whose (CHR, POS) matched an LD-ref rsid.
  implication: Per `feedback_rigor_over_speed` memory, the rigorous choice is to re-fit asthma × 3 lambda alongside the 9 failed redispatch — so all 15 fits in the W1 grid are produced under the bridged code path. bmi can be skipped (binary-identical). Redispatch grows from 9 to 12 jobs (asthma × 3 + hypertension/stroke/t2d × 3 each).

## Resolution

root_cause: Variant-ID convention drift between harmonized sumstats and per-region 1KG-EUR LD reference. The W1 fitter scaffolded in commit bccd0d6 (src/R/regularization/refit_sh2b3_psd_regularized.R) does a naive `intersect(rownames(R), sub$SNP_ID)` at line 122 with no chr:pos<->rsid bridge, then hard-fails at `stopifnot(length(overlap) > 0)` at line 123 when the sumstats use chr:pos SNP_IDs (hypertension/stroke/t2d harmonized sumstats) but the LD-ref carries 100% rsids (SH2B3_12q24.rds: 895 rsids / 895 variants). Asthma + bmi sumstats happen to use rsids and bypassed the bug at first dispatch. Same class of bug previously fixed in commits 069b34f (run_qtl_coloc.R) + 7d54183 (run_susie_rss.R) on 2026-04-21 — now extracted as a reusable utility instead of inline.

fix: (a) Extract chr:pos<->rsid bridge as src/R/regularization/snp_id_bridge.R::bridge_snp_id_to_ld_ref(). Behavior contract: never regresses overlap; bridges ONLY when sumstats SNP_ID is chr:pos (^[0-9XY]+:[0-9]+$) or NA/blank AND LD-ref has a clean rsid (^rs[0-9]+$) for the same (CHR, POS) tuple. Idempotent and non-mutating on the caller's data.table. (b) Wire bridge_snp_id_to_ld_ref() into refit_sh2b3_psd_regularized.R between sumstats region-subset and the existing intersect() gate. No changes to regularization math, susieR call, or output schema. (c) Add tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R as a failing-test-first regression that exercises the bridge across all 5 EUR traits at SH2B3_12q24.

verification:
  - bridge alone (regression test): asthma 700->701, bmi 170->170, hypertension 0->589, stroke 0->622, t2d 0->863. PASS.
  - fitter end-to-end smoke (post-fix, hypertension/lambda=0.001): WROTE /tmp/hypertension_smoke.fit.rds; n_snps=589 (matches commit 7d54183 prior-fix expected count exactly), n_CS=4, niter=1000, converged=FALSE, wall=47.8s. converged=FALSE at lambda=0.001 is expected lambda-sweep pathology per W1 PLAN Branch-A/B classification.
  - asthma re-run vs landed: bmi binary-identical (n_snps=170, n_CS=10); asthma drifts +1 SNP (700->701) due to bridge rescuing one previously-non-rsid asthma row. NOT a regression — strict superset. Per `feedback_rigor_over_speed` memory, asthma × 3 redispatched alongside the 9 chr:pos failures so all 15 fits use the same bridged code path; bmi × 3 skipped (binary-identical).
  - 12 LSF jobs redispatched 2026-05-06T04:45:15Z under serial queue, IDs 119067-119078 (asthma+hypertension+stroke+t2d × 3 lambdas each); bsub flags identical to original dispatch (queue=serial -W 5760 -n 1 -R "rusage[mem=32]"). bjobs confirms RUN/PEND state.
  - HUMAN-VERIFY step (PARTIALLY SATISFIED — programmatic): all 12 redispatched jobs drained ~2026-05-06T04:50:00Z (~5 min post-dispatch). bjobs -J 'ta_r3_W1_*' returns "Job is not found". All 15 .fit.rds present at results/fine_mapping_psd_regularized/. Per-trait grid (n_snps stable across lambdas):
      asthma:       n=701  nCS=0   it=2     converged=T  (all 3 lambdas; no signal expected)
      bmi:          n=170  nCS=10  it={1000,221,57}  converged={F,T,T}
      hypertension: n=589  nCS={4,7,7}  it={1000,715,45}  converged={F,T,T}
      stroke:       n=622  nCS={4,6,7}  it={859,264,46}  converged={T,T,T}
      t2d:          n=863  nCS=5   it={33,30,29}  converged=T  (all 3 lambdas)
    These convergence patterns are exactly what the W1 PLAN Branch-A/B/C/D decision matrix is designed to discriminate over; the bug-fix is structural (variant-ID bridging), not numerical, and the lambda-sweep behavior is the legitimate science-grade signal the OSF amendment was pre-registered to characterize.
  - HUMAN-VERIFY step (REMAINING — workflow): user confirms via the next /gsd-resume-work that W1 Task 3 (coloc.susie at canonical pairs + Branch-A/B/C/D classification + W1 SUMMARY finalization) executes cleanly off the bridged fits. That harvest is OUT OF SCOPE for this debug session per Carter's directive; control returns to the orchestrator.

files_changed:
  - tests/testthat-phase1/test_refit_sh2b3_psd_snp_id_bridge.R  (NEW; commit 728d760; failing-test-first regression)
  - src/R/regularization/snp_id_bridge.R                         (NEW; commit ad19818; reusable bridge utility)
  - src/R/regularization/refit_sh2b3_psd_regularized.R           (MODIFIED; commit ad19818; bridge wired in)
  - logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log            (MODIFIED; this commit; redispatch addendum)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W1-sh2b3-psd-regularized-refit-SUMMARY.md  (MODIFIED; this commit; bug-fix addendum; status field UNCHANGED at LSF_DISPATCHED_AWAITING_HARVEST per scope guard)
  - .planning/STATE.md                                           (MODIFIED; this commit; stopped_at refreshed)
  - .planning/debug/ta_r3_w1_snp_id_overlap_zero.md              (NEW; this commit; debug session record)
