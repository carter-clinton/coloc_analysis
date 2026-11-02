---
status: diagnosed
trigger: "ta-r4-w3-status-split-and-r1-fto: #5 status split 44/22 vs frozen 48/18; #6 R1 28/28 empty vs 6 FTO EUR pairs non-empty both sides in reproduced fits"
created: 2026-11-02
updated: 2026-11-02
mode: find_root_cause_only (MEASURE ONLY, §B.10)
---

## Current Focus

hypothesis: #5 CONFIRMED = LD-input difference at FTO_16q12 EUR (April fire used the identity placeholder RDS). #6 CONFIRMED = R1 read different fits (V4 rebuild of 2026-04-30), and its n_cs claim was not measured.
test: done (aggregate reconciliation against the 04-25 per-fit figure snapshot; coloc replay on reproduced FTO fits, LSF 481827)
expecting: n/a
next_action: none — diagnosis returned to caller; no code or frozen number changed

## Symptoms

expected: (#5) frozen real-LD Stage-2 split 48 ok / 18 non_converged / 24 too_many_variants / 6 no_variants (TRACK-A-FROZEN-NUMBERS.md:180-188). (#6) R1 record: all 28 R1 trait-pair coloc JSONs no_signal with n_cs_a=0 OR n_cs_b=0 (ta-r3-W2 SUMMARY :25, :66).
actual: (#5) 44/22/24/6 in both Route C and Route L, identical per fit. (#6) 6 FTO_16q12 EUR pairs have .fit.rds sets on both sides (r1_structural_crosscheck.tsv).
errors: none (data mismatch)
reproduction: $MAN/known_answer_W3a.tsv; data/r4/results/repro_route{C,L}/fine_mapping/susie; $MAN/r1_structural_crosscheck.tsv
started: frozen fire ~2026-04-22; R1 refire ta-r3 W2 ~2026-05; reproduction 2026-10-29

## Eliminated

- hypothesis: (#5 a) R env drift (openblas 0.3.32->0.3.34, Matrix 1.7-5->1.7-6) flipped 4 fits at the max_iter boundary
  evidence: 19/22 non_converged fits end with ELBO steps >= 14 (tol 1e-3), only htn APOL1 is near the boundary (2.3e-3); and the April/reproduced difference is fully accounted for by the FTO LD input, leaving nothing for env drift to explain. Not needed; not tested by refit (the 04-22 env is purged and unrecoverable).
  timestamp: 2026-11-02
- hypothesis: (#5 c) frozen 48/18 used a different status rule or counted retries
  evidence: summarize_finemap_results.py at 3dd76df copies JSON `status` verbatim; the 04-25 figure (independent script, same JSONs) gives the same 48/24/18/6.
  timestamp: 2026-11-02
- hypothesis: (#5 d) nondeterminism
  evidence: Route C = Route L 96/96, max dPIP 0; SH2B3 rds md5-identical to April; exact reconciliation via FTO leaves no residual.
  timestamp: 2026-11-02
- hypothesis: (#5 b, other inputs) sumstats/policy drift
  evidence: sumstats mtimes 2026-04-16, bmi.EUR sha256 = frozen; policy last committed 2026-04-12.
  timestamp: 2026-11-02
- hypothesis: (#6) run_coloc_susie.R alignment empties credible sets after reading fit$sets
  evidence: rewrite keeps every CS-referenced column; replay on the 10 reproduced FTO EUR pairs (both envs) reports n_cs_a/n_cs_b equal to the .fit.rds counts in 10/10.
  timestamp: 2026-11-02
- hypothesis: (#6) mismatch #1 (JSON credible_sets vs purity-filtered fit$sets) explains the 6 pairs
  evidence: all 4 involved FTO fits are non_converged, where JSON = rds (22/22 equal in fit_cs_json_vs_rds.tsv); #1 can only make rds <= JSON.
  timestamp: 2026-11-02

## Evidence

- timestamp: 2026-11-02
  checked: ELBO trajectories of the 22 reproduced non_converged fits (repro_routeC .fit.rds; script data/r4/tmp/debug_w3_split/elbo.R, run under /rs1/.../conda_envs/r_coloc)
  found: all 22 at niter 100, ELBO monotone increasing (0 negative steps). Final step size (tol 1e-3): 19/22 have last delta >= 14 (up to 3.7e4); 3 small: hypertension.EUR.APOL1_22q12 2.3e-3, asthma.EUR.FTO_16q12 5.6e-2, bmi.EUR.APOE_19q13 7.3e-2. asthma FTO and bmi APOE are already known to match the frozen/04-21 record as non_converged.
  implication: only 1 fit (htn APOL1) is plausibly within ULP-rounding reach of the max_iter boundary. Rounding-level env drift (BLAS/Matrix) predicts at most ~1 flip, not 4. (Caveat: stored fit is the ladder's fit3 (regularized); fit1 trajectory not stored.)

- timestamp: 2026-11-02
  checked: the 3dd76df retry ladder (run_susie_rss.R:30-60) and policy (config/susie_policy.yaml 100/200)
  found: ladder passes `max_iterations=`, which susieR 0.14.2 ignores (falls to max_iter 100); fit1 and fit2 are therefore the same call; fit3 = R + 1e-4 I. Status "ok" iff any of the 3 converges in 100 iterations.
  implication: frozen and reproduced runs share the same effective algorithm given the same susieR; a status difference requires different inputs, a different susieR/numeric stack, or a different count.

- timestamp: 2026-11-02
  checked: env provenance. Frozen fire = bin/fire_phase2_stage2_refit.sh (11b75ad7), profile config/cluster_lsf use-conda, rule run_finemap conda envs/r_coloc.yml (modified a7d4eace 2026-04-20, so the env was solved on/after 04-20). Repo .snakemake/conda/* envs: conda-meta and R library contents purged (only bslib/package.json files left in f2752ef). Named env /rs1/.../conda_envs/r_coloc: conda-meta/history single entry 2026-04-14 (no r.utils, so it is NOT the 04-20+ solve). ta_r4 env 0f3436..: susieR 0.14.2 and r-base 4.4.2 equal; differs on libopenblas 0.3.32->0.3.34, r-matrix 1.7_5->1.7_6, gcc runtime 15->16, rcpparmadillo, etc.
  implication: the exact 04-22 env is unrecoverable; the closest available proxy is the 04-14 named env (April-vintage openblas/Matrix).

- timestamp: 2026-11-02
  checked: input mtimes. data/processed/sumstats_harmonized/{asthma,bmi,hypertension,stroke,t2d}.{EUR,AFR}.tsv.bgz all mtime 2026-04-16 08:09 (before the fire); bmi.EUR sha256 c914e16b = frozen per bmi_allele_restoration_report. config/susie_policy.yaml last commit 2026-04-12. LD panels legacy_repro rebuilt 2026-10-26 (originals purged); SH2B3 .fit.rds md5-identical to the pre-swap Stage-2 files (3 fits) and 10 FTO+SH2B3 04-21 fits match.
  implication: sumstats/policy drift ruled out by mtime/hash; LD/catalog drift ruled out only for SH2B3 and FTO (the other 8 regions' April panels/catalogs cannot be compared byte-wise).

- timestamp: 2026-11-02
  checked: #6 provenance. logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log: R1 refire 2026-05-06 10:14 read results/fine_mapping/susie/{trait}.{anc}.{region}.fit.rds. That namespace had been fully rebuilt 2026-04-30 by the ta-sh2b3 W4 V4 dispatch (c8ee71a0: "96/96 .fit.rds mtimes > V4 dispatch", post-02c4404 max_iter fix, niter up to 1000; SH2B3 md5s 053444fe->462ada6a etc.).
  implication: R1 did NOT read 04-22-semantics (iter-100) Stage-2 fits; it read V4 fits.

- timestamp: 2026-11-02
  checked: logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log (2026-05-06 11:00, 45 min after R1, same results/fine_mapping/susie namespace) + survivor JSONs data/r4/known_answer_survivors/results/multitrait/coloc_susie_R2_FTO/
  found: V4 FTO EUR n_cs: bmi 7, hypertension 0, t2d 2 ("n_cs_a= 7 n_cs_b= 0" bmi_vs_htn; "n_cs_a= 0 n_cs_b= 2" htn_vs_t2d; bmi_vs_t2d 7x2 -> coloc.susie errored, status error). Reproduced iter-100 .fit.rds: bmi 3, hypertension 5, t2d 7.
  implication: the fits differ between R1 and the reproduction. Under V4 fits htn FTO is empty -> the 3 htn-containing pairs of the 6 are no_signal in R1.

- timestamp: 2026-11-02
  checked: committed R1 coloc_summary.tsv (git show d9707dfa:results/multitrait/coloc_summary.tsv), FTO EUR rows
  found: asthma_vs_bmi PP.H0=-2.2204e-16, asthma_vs_t2d PP.H0=-2.2204e-16, bmi_vs_t2d PP.H0=0, H1-H4 empty; all other R1 rows fully empty. The no_signal branch of run_coloc_susie.R (d9707dfa = c0f02b6 blob) writes an all-NA summary, so a non-NA PP.H0 cannot come from no_signal.
  implication: in R1, 3 FTO EUR pairs reached coloc.susie (n_cs_a>0 AND n_cs_b>0). The record's "all 28 no_signal, n_cs_a=0 OR n_cs_b=0" (ta-r3-W2 SUMMARY :25/:66) is contradicted by its own committed summary for these 3 pairs; what was actually measured was R1_non_empty_PP.H4 = 0/28 (post_refire_outcome.tsv).

- timestamp: 2026-11-02
  checked: per-fit snapshot of the APRIL Stage-2 fits that survives in git: 1e4b071e (2026-04-25, quick 260425-wa2) docs/manuscript/figures/fig_h3_ld_overlap_dose_response.{png,pdf} + src/R/figures/fig_h3_ld_overlap_dose_response.R, built from results/fine_mapping/susie/*.json before the 04-30 V4 overwrite. Copies in data/r4/tmp/debug_w3_split/fig_h3_0425.*. Render log (260425-wa2-SUMMARY.md:40-50, :71): status 48/24/18/6; 60 EUR fits = 41 numeric ld_overlap_fraction (35 ld_loaded + 6 ld_status variants_exceed_threshold with ld_of 0) + 19 NA; 33 EUR fits < 0.5 (NA->0); script stopifnot "FTO_16q12 EUR min_ld_overlap_fraction drifted from 0" PASSED. Panel A: no non_converged (red) point below x = 0.97; the x~0 cluster carries ok points at ~10, ~10, ~10, 2, 1, 1, 1 CS.
  found (same scalars on the reproduced repro_routeC EUR JSONs): 41 numeric + 19 NA (equal); 40 ld_loaded + 1 ld_missing + 0 variants_exceed_threshold (April 35 + 6); 30 below 0.5 (April 33); FTO EUR min ld_of 0.353 (April 0, asserted). Reproduced FTO EUR: asthma nc 6 CS ld_of 0.353, bmi nc 3 CS 0.997, htn nc 5 CS 0.989, stroke ok 1 CS 0.987, t2d nc 7 CS 0.442.
  implication: in the April fire all 5 FTO_16q12 EUR fits ran on the identity placeholder RDS (ld_status variants_exceed_threshold, ld_of 0), not the real 1000G panel the reproduction uses.

- timestamp: 2026-11-02
  checked: survivor identity-LD FTO fits (data/r4/known_answer_survivors/.planning/debug/stage2_narrow_validation/identity_fits/, the pre-fix 04-21 placeholder-LD fits) and src/R/figures/fig1b_locus_panels.R:33-35 ("Real-LD overlap at FTO_16q12 EUR Stage 2 fit: ld_overlap_fraction = 0 (ld_status = variants_exceed_threshold)"; bmi FTO "10 CS").
  found: identity FTO EUR fits all status ok, converged_primary: asthma 10 CS, bmi 10, htn 2, stroke 1, t2d 10 — matching the April x~0 cluster (10,10,10,2,1 + asthma APOL1 1 + asthma MC4R 1 = 7 ok points). Real-LD (reald_fits, = reproduction) give 4 non_converged.
  implication: arithmetic reconciliation, every scalar exact:
    status: reproduced 44 ok / 22 nc; move asthma/bmi/htn/t2d.EUR.FTO_16q12 nc -> ok => 48 / 18 (= frozen). stroke FTO ok either way.
    non-empty: FTO CS identity 10/10/2/1/10, real 6/3/5/1/7, all >0 either way => 51 unchanged (= frozen).
    ld_loaded 40 - 5 FTO = 35 (= April); below-0.5 30 + 3 (bmi 0.997, htn 0.989, stroke 0.987 -> 0) = 33 (= April); FTO min ld_of 0 (= April assertion).
  So the 4 are asthma/bmi/hypertension/t2d .EUR.FTO_16q12, and the cause is an LD-input difference (hypothesis b), not env drift or nondeterminism.

- timestamp: 2026-11-02
  checked: replay of run_coloc_susie.R (d9707dfa = c0f02b6 blob; copy at data/r4/tmp/debug_w3_split/run_coloc_susie_d9707dfa.R) on the 10 reproduced repro_routeL FTO_16q12 EUR pairs, LSF 481827. Ran in two envs: ta_r4 r_coloc (R.utils present, so the chr:pos rewrite runs, as in R1's --use-conda env) and la_multitrait_r (no R.utils, rewrite skipped, as in R2). Outputs in data/r4/tmp/debug_w3_split/coloc_fto_routeL{,_noRutils}/.
  found: n_cs_a/n_cs_b = .fit.rds counts in 10/10 pairs in both envs (asthma 6, bmi 3, htn 5, stroke 0, t2d 7). R.utils env: asthma_vs_bmi no_posterior (PP.H0 0, H4 null); the other 5 both-nonzero pairs end in error, because the rewrite maps htn/t2d fits only 6/1833 and 8/2372 (their names are LD-panel rsids from the 7d54183 override, the sumstats SNP_ID is chr:pos), so the intersect is 0. Without R.utils: bmi_vs_htn, bmi_vs_t2d and htn_vs_t2d succeed (PP.H4 0); the asthma pairs are no_posterior. 4 stroke pairs no_signal.
  implication: the alignment step does not empty sets; the 6-pair difference has to come from different fits. no_posterior writes a non-null PP.H0 with null H1-H4, which is the shape of the 3 R1 FTO rows.

## Resolution

root_cause: |
  #5: The frozen 04-22 Stage-2 fire fitted all 5 FTO_16q12 EUR traits on the identity-placeholder LD RDS
  (ld_status variants_exceed_threshold, ld_overlap_fraction 0), whereas the reproduction (and the 04-21 narrow
  validation) uses the real 1000G EUR FTO panel. Under identity LD asthma/bmi/hypertension/t2d.EUR.FTO_16q12 converge
  (ok; 10/10/2/10 CS); under real LD they are non_converged at iter 100 (6/3/5/7 CS). stroke FTO is ok either way.
  This moves exactly 4 fits ok->non_converged and leaves non-empty 51 unchanged; it also reproduces the April
  ld_loaded 35, below-0.5 33, and FTO min ld_of 0 scalars. Why the canonical data/processed/ld_reference/EUR/FTO_16q12.rds
  was still a placeholder at fire time (fire driver says FTO was "already rebuilt during narrow validation" and so
  excluded it from build_ld_rds_1kg_eur) is NOT measured: the RDS and fire log are purged.
  #6: R1 (ta-r3 W2, 2026-05-06 10:14) read results/fine_mapping/susie after the 2026-04-30 V4 rebuild, not
  04-22-semantics fits. In those V4 fits FTO EUR had bmi 7 / hypertension 0 / t2d 2 sets (R2-parity log 45 min later,
  same namespace), versus reproduced 3/5/7. So the 3 hypertension FTO pairs were no_signal in R1. The other 3
  (asthma_vs_bmi, asthma_vs_t2d, bmi_vs_t2d) had sets on both sides in R1 too. Its committed coloc_summary.tsv has
  non-null PP.H0 for them, which is the no_posterior shape (the replay gives the same shape), not no_signal. The
  record's "all 28 no_signal, n_cs_a=0 OR n_cs_b=0" was never measured; the measured quantity was non-empty PP.H4 0/28.
fix: (not in scope; diagnose only)
verification: arithmetic reconciliation exact on 5 independent scalars (#5); replay LSF 481827 (#6)
files_changed: []
