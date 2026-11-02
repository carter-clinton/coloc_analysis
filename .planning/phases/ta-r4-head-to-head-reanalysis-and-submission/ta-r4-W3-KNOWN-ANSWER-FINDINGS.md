# ta-r4 W3 known-answer findings (W2a, W2b, W3a, W3b)

Input to the W4a amendment §(h). These are known-answer controls run before any production fit (D-12, D-17).
Mismatches are stated as findings. No number here was tuned, filtered or re-run toward a frozen value (§B.10).
Paths are repo-relative; `$P` = `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission`, `$MAN` = `$P/manifests`,
`data/r4` = /rs1 durable storage (D-11).

## (1) Panels

| Fact | Value | Source |
|---|---|---|
| 1000G Phase 3 EUR panel n (from the `.fam`) | 489 (not 503) | `$P/ta-r4-W2a-eur-panels-catalogs-identity-SUMMARY.md:66` |
| Live panel gate | 181/181 PASS: md5 92 + has_ref_alt 39 + identity_variants_identical 29 + n_var_equal 10 + abs_r_equal 10 + sh2b3_legacy_n_var 1 | `data/r4/findings/panel_known_answers.tsv` (sha256 49ae7890…) |
| Legacy-identical EUR panels vs R4 panels, 10 shared regions | n_var equal 10/10; max abs(R) difference 0.000e+00 in 10/10 (threshold 1e-12) | `data/r4/findings/panel_known_answers.tsv` rows `n_var_equal` / `abs_r_equal` |
| SH2B3_12q24 legacy EUR panel | 895 variants (= ta-sh2b3-W1.5 audit) | `data/r4/findings/panel_known_answers.tsv` row `sh2b3_legacy_n_var`; W2a SUMMARY:52 |
| AFR panel n | AFR661 661, AFR504 504 | `$P/ta-r4-W2b-afr-and-ukb-panels-SUMMARY.md:71` |
| AFR panels above susie_max_variants 16000 | BMI_5q13_3 (21323 / 21154) and PYHIN1_1q23 (20818 / 20686), AFR661 / AFR504 | `data/r4/findings/afr_panel_size.tsv` (4 rows) |
| Legacy AFR reproduction panels | 12/12 are `use_identity` placeholders, as the frozen builder wrote them | W2b SUMMARY:96 |
| UKB 337k native panels | 30; 4 above 16000: BMI_5q13_3 24121, HLA_6p21 34361, PYHIN1_1q23 26050, SLC2A9_urate 16752 | `data/r4/findings/ukb_native_panel_size.tsv`; W2b SUMMARY:151 |
| UKB vs 1000G EUR sign agreement (tile chr12_111000001_114000001, SH2B3) | 21409/21410 = 0.999953 over 745 shared variants; mixed-orientation pairs 154/154 = 1.000000 | `data/r4/findings/ukb_tile_sign_agreement.tsv` |

## (2) Route C vs Route L

Route L = the 3dd76df `run_susie_rss.R` (blob 75f2d34); Route C = current code under reproduction semantics (iter-100).

| Comparison | Equal | Differ | Total | Source |
|---|---|---|---|---|
| real-LD fits (status, n_CS, cs_sizes, variant ids, max abs dPIP ≤ 1e-10) | 96 | 0 | 96 | `$MAN/known_answer_W3a.tsv`; W3a SUMMARY:124 |
| k2d identity fits | 95 | 0 | 95 | W3a SUMMARY:125 |

max abs dPIP = 0 on all 131 fits with a PIP vector (66 real-LD + 65 k2d); the 60 early exits (30 + 30) have none
(W3a SUMMARY:130). No code drift is detected under reproduction semantics.

## (3) k2d per-fit agreement (vs `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`)

| Field | Equal | Differ | Total | Source |
|---|---|---|---|---|
| status | 95 | 0 | 95 | W3a SUMMARY:126 |
| n_CS | 95 | 0 | 95 | W3a SUMMARY:127 |
| cs_sizes | 47 | 48 | 95 | W3a SUMMARY:128 |

FINDING: the record's cs_sizes column is the length of the label `CS<i>`, not the set size: `3` for CS1–CS9 and `4` for CS10,
on 95/95 rows. The 48 differences are exactly the 48 non-empty fits (W3a SUMMARY:146-149). Per-fit set sizes cannot be checked
against this record. The record lacks bmi.EUR.APOE_19q13 (95 of 96; TRACK-A-FROZEN-NUMBERS.md:26).

## (4) Stage-2 real-LD aggregate reproduction (vs `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md:180-188`)

| | ok | non_converged | too_many_variants | no_variants | total | non-empty |
|---|---|---|---|---|---|---|
| reproduced (C = L) | 44 | 22 | 24 | 6 | 96 | 51 |
| frozen | 48 | 18 | 24 | 6 | 96 | 51 |

Source: W3a SUMMARY:137-138. k2d aggregates 65 / 24 / 6 and non-empty 48/95 equal the record (W3a SUMMARY:140).

- FINDING: 4 more fits are non_converged than the frozen split. Measured 2026-11-02 (`.planning/debug/ta-r4-w3-status-split-and-r1-fto.md`):
  the 4 are asthma/bmi/hypertension/t2d.EUR.FTO_16q12. The 04-22 fire fitted all 5 FTO_16q12 EUR traits on the
  identity-placeholder LD RDS (ld_status variants_exceed_threshold, ld_overlap_fraction 0); on the real 1000G EUR panel these 4
  are non_converged (stroke FTO is ok either way). Reconciliation, exact: 44 + 4 = 48 ok, 22 − 4 = 18 non_converged, non-empty 51
  unchanged; ld_loaded 40 − 5 = 35, below-0.5 30 + 3 = 33, FTO min ld_overlap_fraction 0 (all = the 04-25 figure snapshot,
  1e4b071e). Why the FTO RDS was still a placeholder at fire time is not measured. Surviving per-fit evidence: bmi.EUR.APOE_19q13
  non_converged n_CS 6 = frozen (1/1); 10 surviving 04-21 narrow-validation fits (FTO + SH2B3 EUR, a pre-fire run) match 10/10
  (W3a SUMMARY:150-153). TRACK-A-FROZEN-NUMBERS.md ERRATA E4.
- FINDING (record tension): TRACK-A-FROZEN-NUMBERS.md:72 calls asthma the "sole ok SH2B3 EUR fit". Both routes give
  t2d.EUR.SH2B3_12q24 ok as well (JSON n_CS 9; `$MAN/known_answer_W3a.tsv`), consistent with :222. Asthma
  ld_overlap_fraction 0.0385 is reproduced (W3a SUMMARY:154-156).
- FINDING (new in W3b; `$MAN/fit_cs_json_vs_rds.tsv`, 96 rows): the frozen "non-empty" count uses the fit JSON's
  `credible_sets`. coloc.susie reads `length(fit$sets$cs)` from the `.fit.rds`. The two differ on 29 fits, all status ok, and
  always JSON > rds. By JSON, 51/96 fits are non-empty; by `.fit.rds` sets, 25/96. 26 fits are non-empty by JSON and empty by
  `.fit.rds`. Reconciliation: 22 non_converged (all equal) + 44 ok (15 equal, 29 differ) + 30 early exits (no `$sets`) = 96;
  51 − 26 = 25.
- Caveat (carried from W3a): Routes C and L ran in the same R env (`envs/r_coloc.yml` under the ta_r4 conda prefix, susieR
  0.14.2). C ≡ L measures code drift only. Environment drift since 04-22 was not tested; it is no longer needed to explain the
  4-fit difference, which the FTO LD input accounts for exactly (debug file, "Eliminated"). New partial evidence from W3b: the Route C and Route L `.fit.rds` for bmi/hypertension/stroke EUR
  SH2B3 are md5-identical (053444fe… / 3d4b62cf… / 494ea177…) to the Stage-2 files recorded before the R2 swap
  (`.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave2_dispatch_tracker.json:33-35`). That is 3 fits, all
  non_converged, none of them known to be among the 4. The env question stays open.

## (5) SH2B3 R2-exact reproduction (the known answer, D-17)

Configuration reproduced: bmi/hypertension/stroke EUR L=15 fits with `run_susie_rss.R` at 02c4404 and
`config/susie_policy_L15.yaml` at that commit (max_iter_primary 500, max_iter_retry 1000); asthma/t2d = Stage-2 L=10
(Route L); coloc by `run_coloc_susie.R` at c0f02b6 under the la_multitrait_r Rscript (the R2 dispatcher's,
`bin/fire_canonical_susie_pairs_W2_strategy3.sh:11`), coloc.susie package-default priors, the legacy_repro panel and
legacy catalog. Provenance evidence is in `$P/ta-r4-LOG.md` (2026-10-29 W3b). Code sha256: `$MAN/legacy_code_sha256.tsv`.

Per pair (`$MAN/known_answer_sh2b3.tsv`, R2_exact rows; frozen = `results/multitrait/coloc_susie_R2/<pair>.json`):

| pair | status | PP.H4 reproduced | PP.H4 frozen | abs diff | n_cs a × b | match |
|---|---|---|---|---|---|---|
| asthma_vs_bmi | no_signal | NA | NA | NA | 0 × 13 | true |
| asthma_vs_hypertension | no_signal | NA | NA | NA | 0 × 5 | true |
| asthma_vs_stroke | no_signal | NA | NA | NA | 0 × 3 | true |
| bmi_vs_hypertension | success | 1.000000e+00 | 1.000000e+00 | 0 | 13 × 5 | true |
| bmi_vs_stroke | no_posterior | NA | NA | NA | 13 × 3 | true |
| bmi_vs_t2d | success | 4.308100e-27 | 4.308100e-27 | 0 | 13 × 5 | true |
| hypertension_vs_stroke | success | 1.000000e+00 | 1.000000e+00 | 0 | 5 × 3 | true |
| hypertension_vs_t2d | success | 1.000000e+00 | 1.000000e+00 | 0 | 5 × 5 | true |
| stroke_vs_t2d | success | 0.000000e+00 | 0.000000e+00 | 0 | 3 × 5 | true |

- Match 9 + differ 0 = 9 (match = abs diff ≤ 1e-6, or both NA, plus equal status, nsnps, hit1, hit2, n_cs_a, n_cs_b).
- All 9 reproduced JSONs are byte-identical to the frozen R2 JSONs (`cmp`, 9/9; sha256 in `$MAN/fits_repro_sh2b3_sha256.tsv`).
- Fingerprint, bmi_vs_hypertension, field by field against `ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md:102`:
  n_cs_a 13 = 13, n_cs_b 5 = 5, nsnps 168 = 168, hit1 rs3184504 = rs3184504, hit2 rs3184504 = rs3184504 (5/5).
- L15 fits (`data/r4/results/repro_sh2b3_r2/fine_mapping/susie/`): n_CS bmi 13, hypertension 5, stroke 3 = 13/5/3
  (`.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv`, L15 rows, niter 1000);
  ld_overlap 170/589/622 = 170/589/622 (`data/r4/known_answer_survivors/results_lsweep_L15.preNiter500.bak.20260429_213644/`
  JSONs). All 3 are status non_converged at niter 1000 and L_used 15, as recorded. Their policy_hash 456efb68… equals the
  hash in the surviving `results_lsweep_L15.preFix.bak.20260429_215312` JSONs (the same 500/1000 policy file).
- FINDING (provenance record): TRACK-A-FROZEN-NUMBERS.md:361 cites `.fit.rds` md5s 462ada6a… / 8255c1ac… / a041eecc… as
  the "V4 niter=1000 fits backing R2". Commit c8ee71a0 (2026-04-30) wrote those md5s for the W4 V4 Stage-2 rebuild
  ("bmi: 053444fe… -> 462ada6a…"), which ran after the R2 coloc (dispatch 2026-04-29 23:43, W2 SUMMARY:63). The
  reproduced L15 fits have md5 903782e2… / 3dc6fe83… / 4c539b5a…, and their coloc output is byte-identical to R2. Likewise
  :357 cites `bin/fire_canonical_susie_pairs.sh` + commit b3395d9 for the R2 fire; b3395d9 is a W4 V4 dispatch record
  (2026-04-30 10:25), and the R2 dispatcher was `bin/fire_canonical_susie_pairs_W2_strategy3.sh` (W2 SUMMARY:29, :159).
- FINDING (method detail): in the R2 coloc the chr:pos name-alignment step did not run. `fread` of the `.bgz` sumstats
  needs R.utils, which la_multitrait_r lacks, so the script logged "skipping chr:pos rewrite" (18/18 W3b coloc logs,
  `data/r4/logs/sh2b3_{r2,L10}/`). The fits matched on the LD-panel rsid names (`run_susie_rss.R` override, 7d54183b).

## (6) SH2B3 L10 / iter-100 — separate measurement, not the known answer

Route C Stage-2 fits (L=10, effective max_iter 100: the pre-02c4404 `max_iterations` argument fell through to the susieR
default, `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md:218`; JSON `niter`
bmi/hypertension/stroke 100, asthma 3, t2d 33 in `data/r4/results/repro_routeC/fine_mapping/susie/`) for all 5 traits,
same coloc script and env (`$MAN/known_answer_sh2b3.tsv`, L10_iter100 rows; no frozen comparison):

| pair | status | PP.H4 | nsnps | hit1 / hit2 | n_cs a × b |
|---|---|---|---|---|---|
| asthma_vs_bmi | no_signal | NA | NA | NA | 0 × 8 |
| asthma_vs_hypertension | no_signal | NA | NA | NA | 0 × 4 |
| asthma_vs_stroke | no_signal | NA | NA | NA | 0 × 2 |
| bmi_vs_hypertension | success | 1.000000e+00 | 168 | rs3184504 / rs3184504 | 8 × 4 |
| bmi_vs_stroke | no_posterior | NA | 170 | rs3184504 / rs10774625 | 8 × 2 |
| bmi_vs_t2d | success | 5.093100e-29 | 170 | rs3184504 / rs3809272 | 8 × 5 |
| hypertension_vs_stroke | success | 1.000000e+00 | 583 | rs10774625 / rs10774625 | 4 × 2 |
| hypertension_vs_t2d | success | 3.094300e-08 | 589 | rs3184504 / rs10774624 | 4 × 5 |
| stroke_vs_t2d | success | 0.000000e+00 | 622 | rs10774625 / rs79061463 | 2 × 5 |

Against R2 the PP.H4 ≥ 0.8 class differs on 1 of the 5 numeric pairs: hypertension_vs_t2d is 1.0 under R2 and 3.1e-08
under L10/iter-100. bmi_vs_hypertension (1.0 at rs3184504) and hypertension_vs_stroke (1.0) hold under both.

## (7) Implications to state in the amendment

1. The SH2B3 bmi–hypertension PP.H4 = 1.0 is reproduced byte-for-byte only in its R2 configuration (L=15, max_iter 500/1000, non_converged bmi/htn/stroke fits + Stage-2 L=10 asthma/t2d); state that provenance (D-17). (§5; `$MAN/known_answer_sh2b3.tsv`, `$MAN/fits_repro_sh2b3_sha256.tsv`)
2. Under standard L=10 / iter-100, bmi–hypertension and hypertension–stroke are also 1.0, but hypertension–t2d is 3.1e-08; the htn–t2d result depends on the configuration. (§6; `$MAN/known_answer_sh2b3.tsv` L10_iter100 rows)
3. The frozen 51/96 non-empty count counts JSON credible sets; coloc.susie sees 25/96 non-empty `.fit.rds` sets. Define "credible set" by what coloc reads and report the per-arm no-CS rate on that definition (E4). The producer defect is item 10. (§4; `$MAN/fit_cs_json_vs_rds.tsv`)
4. The frozen real-LD status split (48/18) is not reproduced (44/22). The 4 are asthma/bmi/hypertension/t2d.EUR.FTO_16q12: the 04-22 fire fitted FTO_16q12 EUR on the identity-placeholder LD RDS. (§4; W3a SUMMARY:137-138; `.planning/debug/ta-r4-w3-status-split-and-r1-fto.md`; frozen-file ERRATA E4)
5. The k2d record's cs_sizes column is a label-length artefact and must not be cited for set sizes. (§3; W3a SUMMARY:146-149)
6. TRACK-A-FROZEN-NUMBERS.md:72 ("sole ok") contradicts :222 and the reproduction (t2d ok). (§4; `$MAN/known_answer_W3a.tsv`)
7. TRACK-A-FROZEN-NUMBERS.md:357 and :361 attribute the R2 result to a later commit and later fits; cite c0f02b6 / 02c4404 and `$MAN/fits_repro_sh2b3_sha256.tsv`. (§5)
8. The R2 coloc ran without the chr:pos name alignment (R.utils absent); variant matching relied on panel rsids. (§5; `data/r4/logs/sh2b3_{r2,L10}/`)
9. R1 (2026-05-06) read the 2026-04-30 V4 fits, not 04-22-semantics fits. Its mechanism sentence ("n_cs_a=0 OR n_cs_b=0") was not measured: 3 FTO EUR pairs (asthma_vs_bmi, asthma_vs_t2d, bmi_vs_t2d) reached coloc.susie (no_posterior shape). The measured R1 fact is non-empty PP.H4 0/28. On the reproduced fits, 6 FTO EUR pairs have sets on both sides. (§8; `$MAN/r1_structural_crosscheck.tsv`; `.planning/debug/ta-r4-w3-status-split-and-r1-fto.md`; frozen-file ERRATA E6)
10. `run_susie_rss.R:1158` computes the JSON `credible_sets` with `susie_get_cs(fit)` (no Xcorr, so no purity filter), while `fit$sets` in the `.fit.rds` is purity-filtered at min_abs_corr 0.5. Status: fix pending Carter's D-28 decision (quick-261102-log Task 2). (§4; `$MAN/fit_cs_json_vs_rds.tsv`)
11. Open, not fixed: fits carry LD-panel rsid names (7d54183b override) while sumstats `SNP_ID` is chr:pos; with R.utils present, `run_coloc_susie.R`'s chr:pos rewrite maps 6/1833 (htn) and 8/2372 (t2d) FTO EUR variants and the intersect is 0. (`.planning/debug/ta-r4-w3-status-split-and-r1-fto.md`, LSF 481827 replay; frozen-file ERRATA E7)

## (8) R1_STRUCTURAL re-examination

Measured cause, as recorded (`.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md`):

- `:25` — "results/multitrait/coloc_susie/*.json (28 R1 JSONs re-fired under HEAD; status="no_signal", n_cs_a=0 OR n_cs_b=0; gitignored — regenerable from manifest + HEAD code)"
- `:66` — "Per-JSON failure mode: status="no_signal" / n_cs_a=0 OR n_cs_b=0 (Layer-1 SuSiE-RSS attrition cascades to Layer-2 coloc.susie no_signal; variant-ID matcher works correctly upstream-of structural credible-set vacancy)"

Cross-check of the 28 pairs in `ta-r3-W2-r1-targets.tsv` against the reproduced Stage-2 fits (Route C = Route L;
`$MAN/r1_structural_crosscheck.tsv`, 28 rows):

| n_CS source | ≥ 1 side zero | both sides non-zero | total |
|---|---|---|---|
| fit JSON credible_sets (`$MAN/known_answer_W3a.tsv` n_cs_C = n_cs_L) | 14 | 14 | 28 |
| `.fit.rds` `$sets$cs`, what run_coloc_susie.R reads (Route L) | 22 | 6 | 28 |

- The coloc-visible count reproduces the recorded mechanism for 22 of 28 pairs.
- FINDING: 6 pairs have credible sets on both sides in the reproduced `.fit.rds`: FTO_16q12 EUR asthma_vs_bmi (6 × 3),
  asthma_vs_hypertension (6 × 5), asthma_vs_t2d (6 × 7), bmi_vs_hypertension (3 × 5), bmi_vs_t2d (3 × 7),
  hypertension_vs_t2d (5 × 7). The R1 JSONs were purged. The cause of the difference was not measured at W3b; measured
  2026-11-02, see `.planning/debug/ta-r4-w3-status-split-and-r1-fto.md`.
- Measured cause: R1 (2026-05-06 10:14) read `results/fine_mapping/susie` after the 2026-04-30 V4 rebuild (c8ee71a0). V4 FTO
  EUR n_cs were bmi 7 / hypertension 0 / t2d 2, against reproduced 3 / 5 / 7 (`logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log`,
  via the debug file). So the 3 hypertension pairs were no_signal in R1. The other 3 (asthma_vs_bmi, asthma_vs_t2d, bmi_vs_t2d)
  have non-null PP.H0 with null H1–H4 in `d9707dfa:results/multitrait/coloc_summary.tsv`, the no_posterior shape: they reached
  coloc.susie. The recorded mechanism was not measured; the measured R1 fact is non-empty PP.H4 0/28.
- On the JSON count, 14 pairs would not be empty on either side. The JSON-vs-`.fit.rds` difference in §4 accounts for
  the 8 pairs between 14 and 22.
- Pre-specified handling: D-02 (`$P/ta-r4-CONTEXT.md:38-41`). When either trait has 0 credible sets under an arm, the
  outcome is `coloc.abf` on the same region, labelled `fallback_abf`, never pooled with `coloc.susie`, and the per-arm
  no-CS rate is reported (E4).
