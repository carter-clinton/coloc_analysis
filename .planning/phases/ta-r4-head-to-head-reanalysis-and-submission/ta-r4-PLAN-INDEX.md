# ta-r4 — Plan index, shared conventions, decision coverage

**Phase:** ta-r4-head-to-head-reanalysis-and-submission
**Planned:** 2026-10-21 (gsd-planner, standard mode); **revised** 2026-10-21 (plan-check iteration 1: B1–B6, W1–W16; iteration 2: confirmatory-set blocker, W-1..W-5)
**Inputs:** ta-r4-CONTEXT.md (D-01..D-28, LOCKED), ta-r4-RESEARCH.md, ta-r4-VALIDATION.md,
ta-r4-INVENTORY-2026-10-21.md, ta-r4-LOG.md

Every plan in this phase reads this file. §A–§E are binding on every executor.

---

## Plan list and execution order

Waves run **strictly in sequence**. Every plan appends to `ta-r4-LOG.md`, and same-wave plans
may not share a modified file, so there is no same-wave parallelism. That is deliberate: one
executor on a shared multi-terminal GPFS tree (D-16).

The research's W-labels are kept as file-name prefixes. The E-2 code (research W2) runs **before**
the panel builds (research W1), because the R4 EUR panel needs `plink_ld_to_rds.R --emit-ref-alt`.
Plans are therefore labelled in execution order, and the `wave:` frontmatter is authoritative.
`depends_on` uses plan ids (file name minus `-PLAN.md`).

| wave | plan file | research wave | Carter checkpoint (all `checkpoint:human-action`) | autonomous |
|---|---|---|---|---|
| 1 | ta-r4-W0a-storage-envs-survivors-PLAN.md | W0 | — | yes |
| 2 | ta-r4-W0b1-arms-paths-overlays-signoff-PLAN.md | W0 | — | yes |
| 3 | ta-r4-W0b2-pair-manifest-osf-gate-workflow-PLAN.md | W0 | — | yes |
| 4 | ta-r4-W0c-receipts-validators-enforcers-PLAN.md | W0 | — | yes |
| 5 | ta-r4-W0d-pair-coloc-r4-script-PLAN.md | W0 | — | yes |
| 6 | ta-r4-W1-e2-orientation-tdd-PLAN.md | W2 | — | yes |
| 7 | ta-r4-W2a-eur-panels-catalogs-identity-PLAN.md | W1 | — | yes |
| 8 | ta-r4-W2b-afr-and-ukb-panels-PLAN.md | W1 | — | yes |
| 9 | ta-r4-W2c-qtl-downloads-manifest-and-panel-review-PLAN.md | W1b | W2c-T4 data facts + ukb_native + qtl_scope | no |
| 10 | ta-r4-W2d-apply-review-decisions-PLAN.md | W1b | — (applies W2c-T4) | yes |
| 11 | ta-r4-W3a-known-answer-routes-PLAN.md | W3 | — | yes |
| 12 | ta-r4-W3b-sh2b3-known-answer-and-findings-PLAN.md | W3 | W3b-T3 known-answer findings | no |
| 13 | ta-r4-W3c-simulation-harness-PLAN.md | (E8 code, pre-lock) | — | yes |
| 14 | ta-r4-W3d-estimators-and-branch-classifier-PLAN.md | (E1–E8, confirmatory contrast_stats, coverage + aggregation code, pre-lock) | — | yes |
| 15 | ta-r4-W3e-qtl-harmonize-and-group-runner-PLAN.md | (W6 prep, pre-lock) | — | yes |
| 15.1 | ta-r4-W3f-producer-cap-fit-names-early-exit-PLAN.md | W3f fix-up (review N1, N2, N8; DEC entries) | — | yes |
| 15.2 | ta-r4-W3f-lock-paths-input-sha-in-job-gate-PLAN.md | W3f fix-up (N3, N4, N5, T1) | — | yes |
| 15.3 | ta-r4-W3f-signflip-region-floor-coverage-PLAN.md | W3f fix-up (N7 sign-flip + n_regions_min, N6) | — | yes |
| 15.4 | ta-r4-W3f-reporting-widening-qtl-sim-PLAN.md | W3f fix-up (N8 drops, N9, N10, N12, N14) | — | yes |
| 15.5 | ta-r4-W3f-eligibility-measurement-and-draft-PLAN.md | W3f fix-up (N1 recount, N7 region proxy, DRAFT, sha). Stopped 2026-11-16 at a Rule-4 checkpoint (duplicate catalog keys); Task 1 code f33a582c + partial DRAFT c3e42237 stand; remaining work COMPLETE 2026-11-18 after 15.5a (re-measured, eligibility manifest, DRAFT (k); SUMMARY; not pushed; [2026-11-19: pushed, e8e18e15]) | — | yes |
| 15.5a | ta-r4-W3f-catalog-dupkey-producer-and-guard-PLAN.md | W3f gap closure (r4 catalogs one row per normalized allele key; flag-gated run_susie_rss.R duplicate-key guard; rebuild + re-pin; no push) | — | yes |
| 15.5b | ta-r4-W3f-ukb-panels-biallelic-PLAN.md | W3f gap closure (15.5a M2: UKB native panels keep the single SNV at a multi-variant CHR:POS, else drop the position; no --snps-only; Carter a1 2026-11-18; rebuild + re-pin 30 panels; M2 → 0; A3_ukb eligibility + DRAFT; no push) | — | yes |
| 15.5c | ta-r4-W3f-trackb-pins-indent-PLAN.md | W3f gap closure (tests/m3 K-1 pins ignore leading whitespace after the N1 re-indent; the one N1 emit line allowed; Carter 2026-11-19 Q1 + Q3 A; test file only; 15.6 FULL scope for the W4a renames; no push) | — | yes |
| 15.6 | ta-r4-W3f-review-suite-and-close-PLAN.md | W3f fix-up (brief-blind re-review, FULL, records, W4a depends_on). COMPLETE 2026-11-19: review 23 findings (6 DRAFT fixed, 12 OPEN for Carter); W4a depends_on edited; push withheld (orchestrator) | — | yes |
| 15.7a | ta-r4-W3f-runtime-config-guard-PLAN.md | W3f 15.7 gap closure (review F1: production fire refuses config/profile overrides; every production job checks the resolved config digest, CPU type and OpenBLAS env, and records them; commits the 15.7 planning set + Carter reply; no push). COMPLETE 2026-11-20: c015a4e4, 420aa998; FULL 2,587 = 2,534 P / 53 S / 0 F reconciled per id; not pushed | — | yes |
| 15.7b | ta-r4-W3f-completeness-by-identity-PLAN.md | W3f 15.7 gap closure (F4 simulation completeness by replicate id, cell labels, seed and config sha; F6 QTL rows reconciled against qtl_manifest at aggregation; F7 empty / non-finite QTL coloc.susie → method none; reusable id reconciliation; no push). COMPLETE 2026-11-20: 5fce26a8; FULL 2,618 = 2,565 P / 53 S / 0 F reconciled per id vs full_15_7a.xml (+31, 0 changes); not pushed | — | yes |
| 15.7c | ta-r4-W3f-cross-purity-variant-resolution-PLAN.md | W3f 15.7 gap closure (F10 cross-panel purity resolves CS members through the fit's own panel by position + alleles; shared R variant matcher extracted from the N2 code; no push). COMPLETE 2026-11-20: e1422df1; names rebuilt 20/20 exact on the pilot fits; FULL 2,636 = 2,583 P / 53 S / 0 F reconciled per id vs full_15_7b.xml (+18, 7 declared spec updates passed → passed, 0 changes); not pushed | — | yes |
| 15.7d | ta-r4-W3f-a1-allvars-secondary-PLAN.md | W3f 15.7 gap closure (F12 A1 allvars secondary table, EUR + AFR; no push). COMPLETE 2026-11-20: 1cf179d1; FULL 2,642 = 2,589 P / 53 S / 0 F reconciled per id vs full_15_7c.xml (−1 declared rename _19_ → _20_, +7, 1 declared spec update passed → passed, 0 changes); not pushed | — | yes |
| 15.7e | ta-r4-W3f-none-rows-denominators-PLAN.md | W3f 15.7 gap closure (F8 negative-control rates by method; F11 pair-level no-CS keeps the completed side; Carter Q-DEN = A known states only; no push). COMPLETE 2026-11-20: 699fdb23, 8d272492; FULL 2,654 = 2,601 P / 53 S / 0 F reconciled per id vs full_15_7d.xml (+12, 1 declared spec update passed → passed, 0 changes); not pushed | Q-DEN reply file (gate, not a signoff) | yes |
| 15.7f | ta-r4-W3f-purity-determinism-PLAN.md | W3f 15.7 gap closure (F2 exact credible-set purity, GWAS and QTL; Carter Q-F2 = A (third D-28 lift of run_susie_rss.R) and Q-F2Q = i; no push). COMPLETE 2026-11-21: 29de2a4d, c3c76ba2, 57ddb59d, 38e4080d (R_CODE_REF → 57ddb59), b11b10b6; pilot flips 0 of 109; FULL 2,667 = 2,614 P / 53 S / 0 F reconciled per id vs full_15_7e.xml (+13, 3 declared spec updates passed → passed, 0 changes); not pushed | Q-F2 reply file | yes |
| 15.7g | ta-r4-W3f-qtl-sweep-gwas-pph4-PLAN.md | W3f 15.7 gap closure (F3 QTL PP.H4 sweep uses the GWAS PP.H4 wherever a GWAS table is given, Track B included, plus NaN GWAS → below_threshold; the no-table sweep kept as the logged legacy rule; Carter Q-F3 = B, Q-F3B = A; no push). COMPLETE 2026-11-21: 90cf52d7, 7405ba4a; Track B count not measurable (no artifact; md5 search 0 hits); QTL_legacy tiers not moved by the sweep fix (synthetic, 0 violations; W6 tripwire); FULL 2,678 = 2,625 P / 53 S / 0 F reconciled per id vs full_15_7f.xml (+11, 1 declared spec update passed → passed, 0 changes); not pushed | Q-F3 reply file | yes |
| 15.7h | ta-r4-W3f-null-window-reselection-PLAN.md | W3f 15.7 gap closure (F9 null-window selection re-run on the production inputs; fetch 6 UKB tiles; rebuild the 8 changed NC_NULL catalogs and panels; Carter Q-F9 = A; no push). COMPLETE 2026-11-21: 6fffde86, 0e6dda24, 350cd9b9; 2,886 candidates, 8 of 10 windows changed; 6 tiles fetched + verified (76 → 88 rows); 8 windows rebuilt and re-pinned row by row, 702/822 other files byte-identical; PASTE (c) UKB counts 30 / 6 / 12 / 16,843 (Carter 2026-11-21 Q2 a); FULL 2,682 = 2,629 P / 53 S / 0 F reconciled per id vs full_15_7g.xml (+4, 1 declared spec update passed → passed, 0 changes); not pushed | Q-F9 reply file | yes |
| 15.7h2 | ta-r4-W3f-proxy-asthma-refit-PLAN.md | W3f 15.7 (n_regions_min option D: region-contribution proxy re-run with exact purity on the scored matrix over the 4 non-asthma EUR traits; 20 asthma pilot commands run (12 fits, 8 early exits), kept as pre-lock pilot fits only; floor stays 7; Carter Q-PROXY, Q-PROXYA B, Q-PROXYB A, Q-NREG, Q-PURITY A, Q-MEMK2D, Q-DROPASTHMA; no push). COMPLETE 2026-11-22: d1498dff, f1f17bef, 265434df, 563f4753, bcd0310a, 688a6220, 4f3d692a, dd5eb803; proxy (Slurm 2039595) = job 2037096's 69 non-asthma rows, byte-identical to the committed proxy table (A1 8/1/1, A2 3/2/5); production variants_r4 GRCh37 (Slurm 2039532); 12 pilot fits (24 files) for 15.7i; FULL 2,691 = 2,638 P / 53 S / 0 F reconciled per id vs full_15_7h.xml (+9, 0 changes); not pushed | Q-PURITY, Q-MEMK2D, Q-DROPASTHMA reply files | yes |
| 15.7i | ta-r4-W3f-pilot-fit-disclosure-PLAN.md | W3f 15.7 gap closure (F15 pre-lock pilot-fit disclosure + committed pilot-fit manifest; recount including 15.7h2's fits; v2 if unchanged, else STOP for Carter's v3 approval; Carter Q-F15 = A, Q-F15W; no push). COMPLETE 2026-11-24: b343872f, 42f3eb9c, ac61c486, 46e0b1fe; recount 146 → 166 / 108 → 128, 39 early exits; Carter Q-F15V3 "v3 + all early exits (Recommended)"; manifests/prelock_pilot_fits.tsv (366 files); FULL 2,694 = 2,641 P / 53 S / 0 F reconciled per id vs full_15_7h2.xml (+3, 0 changes; Slurm 2083696); not pushed | 15.7i-T2 human-action (Q-F15V3 answered 2026-11-24) | yes |
| 15.7j | ta-r4-W3f-15-7-review-suite-and-close-PLAN.md | W3f 15.7 close (DRAFT (m)/Pre-Paste; brief-blind Codex re-review; FULL reconciled per id vs full_W3f.xml; HANDOFF w4a_checkpoint; no push). COMPLETE 2026-11-25: 99ab219d + records; review 14 findings = 14 rows (DRAFT fixed 7, OPEN code 2: R4, R6, rejected 1, noted 4); R2–R7 and the Q-F3N premise decided by Carter 2026-11-24/25 → 15.8 (HANDOFF W3f157_*); 15.7h/15.7h2 SUMMARY id lists completed (orchestrator sign-off 2026-11-25); FULL 2,694 = 2,641 P / 53 S / 0 F (Slurm 2086699, cascadelake) = 2,555 + 140 − 1 vs full_W3f.xml, identical to full_15_7i.xml; W4a depends_on left for 15.8f; not pushed | — | yes |
| 15.8a | ta-r4-W3f-collector-drop-audit-PLAN.md | W3f 15.8 gap closure (R2 collector drops audited: replay identity vs collect_region_variants.py on all r4 regions, every dropped row classified, per-region manifest; STOP for Carter if any allele key is lost; DRAFT (c); commits the Q-157J reply, the five 2026-11-25 replies, the 15.8 planning set and the DEC; no push). COMPLETE 2026-11-25 (B path): 159c06ad, 06b68482, 8da7bfbe + records; replay identity 31/31; 1,598,153 = 875,225 kept + 722,928 dropped, 0 other; 162,724 lost-key rows (67,626 keys, 65,753 swapped) → Q-158R2 = Carter D (harmonize r4 sumstats orientation) → new plan 15.8a2; no test 7, no DRAFT (c) edit, R2 OPEN until 15.8a2; FULL 2,700 = 2,647 P / 53 S / 0 F (Slurm 2093289, cascadelake) reconciled per id vs full_15_7j.xml (+6, 0 changes); not pushed | Q-157J reply file; 15.8a-T2 human-action (Q-158R2 answered D 2026-11-25) | no |
| 15.8a2 | ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md | W3f 15.8 gap closure (Carter Q-158R2 D: the 8 r4 sumstats inputs written in the r4 catalog's orientation (Q-158OR A), A/T and C/G flipped by allele key (Q-158PAL A); one oriented copy each under data/r4/sumstats/*.r4_oriented.tsv.bgz, sha256-pinned; identities: swapped_only == 0 in 248/248 trait × region rows, flips == the 15.8a audit's swapped-present rows (159,969), absent == 2,755, verify_unflip per line, idempotent; catalogs, panels and data/processed unchanged; no consumer switched; commits the Q-158OR, Q-158PAL, Q-158EL replies and the DEC; no push). COMPLETE 2026-11-25: 1298b511, 859458f9 + records; 159,969 rows flipped (28,637 A/T-C/G) of 1,598,153 window rows; swapped_only 0 in 248/248; flips == 15.8a audit per source file; 12 duplicate keys before = after; verify_unflip and idempotence 8/8; 16 pins appended; FULL 2,714 = 2,661 P / 53 S / 0 F (Slurm 2094979, cascadelake) reconciled per id vs full_15_8a.xml (+14, 0 changes) | Q-158R2, Q-158OR, Q-158PAL reply files | no |
| 15.8a3 | ta-r4-W3f-sumstats-orientation-consumers-PLAN.md | W3f 15.8 gap closure (r4 production consumers switched to the oriented sumstats; catalog builders and pre-lock pilots keep the original inputs; catalog fixed point on all 31 regions (rebuilt from the oriented files, byte-identical), else STOP for Carter; no catalog or panel re-pinned; no push). COMPLETE 2026-11-25: 9b5876c9, 50a7bad9 + records; 8 production arms × 8 pairs → `.r4_oriented.` (64 path changes), repro arms and QTL_legacy unchanged; r4_catalog_raw, the 15.8a audit and ASTHMA_PILOT_SUMSTATS read the catalog sources; fixed point 31/31 byte-identical (raw / final / dropped; Slurm 2096913), no Q-158FP; 106 catalog / manifest / panel sha256 before == after; 5 declared spec updates; NCs (a)-(e), fixed-point NC, test 7 and 8 NCs RED; FULL 2,722 = 2,669 P / 53 S / 0 F (Slurm 2097342, cascadelake) reconciled per id vs full_15_8a2.xml (+8, 0 changes); not pushed | Q-158FP not asked (31/31 equal) | no |
| 15.8a4 | ta-r4-W3f-sumstats-orientation-eligibility-and-draft-PLAN.md | W3f 15.8 gap closure (post-restriction variant counts and the 16,000 cap re-measured on the oriented inputs (Carter Q-158EL A), eligibility table re-pinned only behind identities; DRAFT states the orientation step, its counts and the collector audit; closes R2; no push). COMPLETE 2026-11-25: 5fb24630, cda233a8, 8d8b7bb6 + records; gates rc 0 (Q-158EL added to gate_158a2.sh, 4 NCs exit 2); eligibility re-measured at cap 0, Slurm 2099709 83/83 COMPLETED, run list == the 83 pinned measured keys; identities (a) 732/732 (b) 26/26 (c) 83/83 (d) (e) 83/83; change set == Q-158EL set (t2d AFR × BMI_5q13_3 in AFR661_A3 / AFR661_A2 / AFR504_A3: 16,966 / 16,966 / 16,841; PYHIN1_1q23 15,832 / 15,718 under); not eligible 10 → 13; w3f_fit_eligibility.tsv re-pinned (4a07d89c… → 1058dd64…); DRAFT (c) inputs / oriented sha256 / orientation step / collector audit, (i), measured-counts row; FULL Slurm 2100181 2,728 = 2,675 P / 53 S / 0 F, check_15_8a4.py vs full_15_8a3.xml PASS (+6, 0 changes); R2 RESOLVED (15.8a2-a4) | Q-158EL reply file; Q-158EL2 only if the measured set differs | no |
| 15.8b | ta-r4-W3f-openblas-pin-and-guard-PLAN.md | W3f 15.8 gap closure (R6: measured job-env BLAS; libopenblas pinned in envs/r_coloc.yml only + exact pin file + job-env lock manifest; job_guard refuses another BLAS; env rebuilt with pkgs_dirs isolated and proven identical by package list and libopenblas sha256, no fit run, else STOP for Carter; DRAFT (k); Carter Q-158R6S; no push). COMPLETE 2026-11-26: e47b6a83, cd96833e, b113fcba, e852040a, 99949f41, c54f6412, 3e37c63a + records; env D 516ec209…_ built from the pin file and IDENTITY_OK before any guard code (222/222 URL#md5, libopenblas .so sha256 f1424288…572b), conda_pkgs unchanged; `--blas-pinned` on the 5 r_coloc rules (derived from each rule's conda directive, Q-158R6G A), aggregate/tiers record not_checked; DRAFT (k) as Q-158KW; D-11 fix 3e37c63a (job_env_dir prefix required, tests read bin/r4_fire.sh; FULL 2106909 1 F superseded); FULL Slurm 2108889 2,744 = 2,691 P / 53 S / 0 F, check_15_8b.py vs full_15_8a4.xml PASS (+16, 0 changes, 11 declared passed -> passed) | Q-158R6S reply file; Q-158R6 only on a difference | no |
| 15.8c | ta-r4-W3f-qtl-json-full-precision-PLAN.md | W3f 15.8 gap closure (R4: exact round-trip for every r4 thresholded writer: run_qtl_coloc.R I(17) behind --json-full-precision, default off, Track B byte-identical; run_coloc_pair_r4.R I(17); simulation posteriors %.17g; QTL_A3/QTL_A2 on, QTL_legacy off; DRAFT (l); Carter Q-158DIG A; no push). COMPLETE 2026-11-26: dc4d8156, eca81966, 635ffc1c + records; gates Q-157J + Q-158DIG rc 0; writers_15_8c.tsv (digits=NA/fwrite 8.07%, I(17)/%.17g 100% of 10^5 doubles; no thresholded writer outside the plan list); 8 new tests (RED 6F/2P; 7 NCs each fail, md5-restored); declared: test_purity_determinism::test_qtl_default_path_unchanged_without_the_flag, test_coloc_pair_r4::test_qtl_abf_pp_equal_direct_coloc_abf (:323 oracle digits=NA -> I(17)); FULL Slurm 2110960 2,752 = 2,699 P / 53 S / 0 F, check_15_8c.py vs full_15_8b.xml PASS (+8, 0 changes, 2 declared passed -> passed) | Q-158DIG reply file | yes |
| 15.8c2 | ta-r4-W3f-qtl-legacy-rule-and-e7-rounding-PLAN.md | W3f 15.8 gap closure (Q-F3NL: --nan-gwas-below-threshold for QTL_A3/QTL_A2 only, QTL_legacy keeps the earlier rule, W6 tripwire superseded; Q-158E7R: E7 matched-rounding columns from QTL_A3 tiers on 4-decimal posteriors; DRAFT (l)/E7; no push) | Q-F3NL, Q-158E7R reply files | yes |
| 15.8d | ta-r4-W3f-e7-filtered-cs-counts-PLAN.md | W3f 15.8 gap closure (R3: E7 earlier side = purity-filtered counts, JSON count kept labelled; exact-purity identity on the 96 earlier fits, else STOP; fit_cs_json_vs_rds.tsv locked (LOCKED_PATHS 29 → 30); DRAFT (e)/(m); no push) | Q-157J (gate); Q-158R3 only on a difference | no |
| 15.8e | ta-r4-W3f-multikey-fatal-and-chronology-PLAN.md | W3f 15.8 gap closure (R5 multi-key cross-purity member fatal, after counting multi-key members of the production-panel pilot fits with resolve_fit_names only; R7 Purpose as gated production vs pilot fitting, wording sha256-pinned; Carter Q-158R7; no push) | Q-158R7 reply file; Q-158R5 only if non-zero | no |
| 15.8f | ta-r4-W3f-15-8-review-suite-and-close-PLAN.md | W3f 15.8 close (DRAFT (m)/Pre-Paste; brief-blind Codex re-review; FULL reconciled per id vs full_15_7j.xml; HANDOFF w4a_checkpoint W3f157_* keys; W4a depends_on; no push) | — | yes |
| 16 | ta-r4-W4a-amendment-draft-review-locks-PLAN.md | W4 | W4a-T3 lock values + draft approval | no |
| 17 | ta-r4-W4b-amendment-final-and-posting-gate-PLAN.md | W4 | W4b-T3 lock confirmation (+ lock gate) | no |
| 18 | ta-r4-W5a-eur-production-fits-PLAN.md | W5 | — (code gate) | yes |
| 19 | ta-r4-W5b-eur-production-coloc-PLAN.md | W5 | — (code gate) | yes |
| 20 | ta-r4-W5c-afr-secondary-and-simulation-run-PLAN.md | W5 | — (code gate) | yes |
| 21 | ta-r4-W6-qtl-layer-PLAN.md | W6 | — (code gate) | yes |
| 22 | ta-r4-W7-aggregation-figures-PLAN.md | W7 | W7-T3 results | no |
| 23 | ta-r4-W8a-manuscript-draft-PLAN.md | W8 | — | yes |
| 24 | ta-r4-W8b-adversarial-review-PLAN.md | W8 | W8b-T3 submission candidate | no |
| 25 | ta-r4-W9-submission-prep-PLAN.md | W9 | W9-T1 venue; W9-T4 submitted (+ code sentinels) | no |

W3f (waves 15.1–15.6) is a gap-closure fix-up added 2026-11-04 after the W4a brief-blind review
(`ta-r4-W4-AMENDMENT-REVIEW-as-received.md`) and Carter's decisions (DEC-2026-11-04-ta-r4-w3f-fix-all,
DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor). Plan 15.1 lifts §B.6 (D-28) once, for the N1 cap move only, and only after a DEC quotes Carter's explicit
unfreeze reply (DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze); without it 15.1 stops. W4a depended on 15.6; 15.7j left its depends_on unchanged because 15.8f sets it (orchestrator, 2026-11-25).

**15.7 (added 2026-11-20).** The 15.6 brief-blind re-review left 12 production blockers (HANDOFF
`w4a_checkpoint.production_blockers.W3f_F1…W3f_F15`). Carter chose "Plan 15.7 code fix-up (Recommended)"
(`W3f-carter-15-6-push-and-15-7-reply-2026-11-20.txt`, committed by 15.7a; DEC-2026-11-20-ta-r4-w3f-15-7-code-fixup).
Order 15.7a → 15.7h → 15.7h2 → 15.7i → 15.7j, strictly sequential. 15.7e–15.7i gate on Carter's 2026-11-20 replies (each gate re-checks the file).
Shared protocol, binding on every 15.7 plan:
- Scratch `Q=data/r4/tmp/w3f/q157/` (15.7a creates it).
- **Reply gate.** One question per file: `$P/W3f-carter-15-7-<QID>-reply-<YYYY-MM-DD>.txt`, LF line endings,
  exactly two lines: `Question <QID> (<YYYY-MM-DD>): <question as presented>` then
  `Carter reply (verbatim, selected option): <option label>`; an optional third line `Carter note (verbatim): …` is
  allowed. The QID and date in line 1 must equal the file name's. `$PY $Q/gate_reply.py <QID> --question <text>
  --sha256 <hex> <allowed label>…` (built and negative-controlled in 15.7a) matches the file name exactly (Q-F2 never
  matches Q-F2Q), requires exactly one such file, refuses CRLF, a malformed or mismatched Question line, a date
  mismatch, extra or missing lines, a question text different from `--question`, a sha256 different from `--sha256`,
  and a label not byte-equal to an allowed one; it prints the label and sha256, else exits 2. A free-text answer uses
  line 2 `Carter reply (verbatim): <text>` and is gated with `--free-text <exact text>` instead of labels. A gated plan
  whose gate fails STOPs before any edit. Answers given on 2026-11-20: Q-F2 A, Q-F2Q i, Q-F3 B, Q-F3B A, Q-DEN A,
  Q-F9 A, Q-F15 A, Q-F15W "Clarify to the 20 fits" (wording v2:
  `W3f-carter-15-7-Q-F15-wording-as-approved-v2-2026-11-20.txt`; v1 is superseded and kept), Q-PROXY "Add to 15.7j",
  Q-NREG free text "yes, A and add D to 15.7j and keep 7" (n_regions_min stays 7), Q-PROXYA "B: Run the 20 asthma fits"
  (the proxy re-run moves from 15.7j to 15.7h2, before 15.7i, so the F15 recount includes its 20 pilot fits; 15.7i stops
  for a v3 F15 wording if the recount differs from v2). Each gated plan carries its
  question text and file sha256 in a `<question>` block. Q-PROXYB "A: Run as planned (Recommended)" (15.7h2 unchanged). 15.7a commits all fifteen decision files with the
  planning set.
- **Close.** `$Q/close.sh <tag>` (15.7a; a copy of `data/r4/tmp/w3f/close_W3f.sh`: QUICK, HEAVY, PINS, FULL, junit
  `$Q/full_<tag>.xml`) runs under `sbatch -p compute -A clintonlab_cpu -q normal -t 03:00:00 --mem=48G
  --constraint=cascadelake` (full_W3f.xml ran on cascadelake c025n04). Each plan reconciles per id with
  `data/r4/tmp/w3f/ukbbi/junit_cmp.py <base> <new>` and its own `$Q/check_<tag>.py`, which exits non-zero on: a
  removed id other than the plan's declared renames; added ids ≠ the plan's `<new_tests>`; an outcome change on a
  pre-existing id; any failure; totals ≠ base + N_new. Base chain: `data/r4/tmp/w3f/full_W3f.xml` (2,555 = 2,502 P /
  53 S / 0 F) → `$Q/full_15_7a.xml` → … ; 15.7j reconciles the cumulative change against full_W3f.xml.
- **Pre-existing tests** may be edited only in fixture builders, or where a test asserts the exact defect the plan
  fixes (named by id in the plan, with the reason). Their ids and passed outcomes stay. Anything else is STOP. Every
  15.7 SUMMARY has a `## Declared spec updates` section listing those ids one per line (or `none`); 15.7j's
  cumulative check reads them from there.
- **DRAFT.** Each plan rewrites only the DRAFT sentence(s) describing the behaviour it changes (old string asserted
  unique, one script) and re-runs `tests/ta_r4/test_amendment_text.py`; 15.7j does (m), the Pre-Paste OPEN row and the
  review.
- Each plan closes without `git push`; decision_rules.yaml stays `locked: false`; no production fit, OSF posting,
  W4a-T3 lock or n_regions_min change; no re-pin except of an artifact the plan rebuilt or a file it was authorized
  to change, each named in the plan.

**15.8 (added 2026-11-25).** The 15.7j brief-blind re-review left R2–R6 open (code), R7 optional and the Q-F3N
premise open. Carter's Q-157J reply (`W3f-carter-15-7j-open-items-reply-2026-11-24.txt`, sha256 805afcd8…) and his
2026-11-25 replies Q-158DIG, Q-158R6S, Q-158E7R, Q-F3NL and Q-158R7 (`W3f-carter-15-8-<QID>-reply-2026-11-25.txt`)
are committed by 15.8a (DEC-2026-11-24-ta-r4-w3f-15-8-open-items). Order 15.8a → 15.8b → 15.8c → 15.8c2 → 15.8d →
15.8e → 15.8f, strictly sequential. The shared protocol is in 15.8a's `<protocol>` block: reply gates by staging copy
(the 15.7 gate tool unchanged), `Q8=data/r4/tmp/w3f/q158`, FULL under Slurm `--constraint=cascadelake -t 04:00:00`
with the base chain from full_15_7j.xml (2,694 = 2,641 P / 53 S / 0 F), one junit id per new test, junit-form id lists
in every SUMMARY, and the same bans as 15.7. W4a's depends_on is set by 15.8f.
Amended 2026-11-25 (15.8a2–a4, Carter's Q-158R2 D, Q-158OR A, Q-158PAL A, Q-158EL A): order 15.8a → 15.8a2 → 15.8a3 → 15.8a4 → 15.8b → 15.8c → 15.8c2 → 15.8d → 15.8e → 15.8f, strictly sequential. Base chain (expected totals; each plan uses the actual totals read from its base file): full_15_7j.xml 2,694 → full_15_8a.xml 2,700 (no test 7) → full_15_8a2.xml 2,714 → full_15_8a3.xml 2,722 → full_15_8a4.xml 2,728 → full_15_8b.xml 2,739 → full_15_8c.xml 2,747 → full_15_8c2.xml 2,753 → full_15_8d.xml 2,759 → full_15_8e.xml 2,761 (= 2,708 P / 53 S / 0 F). Amended 2026-11-26 (15.8b had 16 new tests, not 11): full_15_8b.xml 2,744 → full_15_8c.xml 2,752 → full_15_8c2.xml 2,758 → full_15_8d.xml 2,764 → full_15_8e.xml 2,766 → 15.8f 2,768; 15.8f reconciles cumulatively against full_15_7j.xml over the nine 15.8a–e SUMMARYs.

**15.5a (added 2026-11-17).** Plan 15.5 found every r4 fit would carry duplicated variants. The r4 catalogs
list one CHR:POS:REF:ALT under two or three SNP_IDs (248,257 extra rows of 877,756). Carter chose "1. Fix both ends
(recommended)." (`W3f-carter-dupkey-fix-reply-2026-11-17.txt`). 15.5a lifts §B.6 (D-28) once more, for the
flag-gated duplicate-key guard only, under DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze.
Order: 15.5 Tasks 1 (code) and 2 (partial) done → **15.5a** → 15.5 remainder → 15.6 (whose `depends_on` on 15.5
now means 15.5 completed after 15.5a). The 15.5 remainder is:
- Task 1 steps 2–4, re-run on the rebuilt catalogs (cascadelake);
- `w3f_fit_eligibility.tsv`;
- Task 2 item 7, the (k) measured-count clause; the Pre-Paste OPEN duplicate-key row resolved; and (c)/(m) for the
  15.5a commits;
- Task 3 and its SUMMARY.
That remainder depends on 15.5a. 15.5a does not push; the 15.5 remainder's §C pushes.
15.5a does not fix `run_coloc_pair_r4.R:440` (DUPLICATE_KEYS on a shared CHR:POS) or the UKB native multi-allelic
sites. It measures them per fit (M2), with sumstats duplicates as M1. Any non-zero M1/M2 is a Rule-4 decision for Carter:
an OPEN row in the DRAFT Pre-Paste that **gates the W4a-T3 lock**. The 15.5 remainder carries that row unresolved.

**Rigor upgrades over the research decomposition** (rigor-over-speed rule; recorded here so they are
visible to Carter):
1. The **estimators, the confirmatory row set and stats→category rules (`decision_rules.yaml`
   `confirmatory:` + `estimands.contrast_stats`), the outcome-branch classifier, the coloc coverage
   tool and the aggregation entry point `run_aggregation.py` (E1–E8)**, the **E8
   simulation harness** and the **QTL group runner** (W3c–W3e) are written and tested **before** the
   lock (W4b). The amendment cites the commit hashes of the analysis code and of the locked configs
   (W4b commit A), and W5a–W6 refuse to fire if any analysis file differs from the lock commit
   (enforced by `ta_r4.r4_lock_gate`: `LOCKED_PATHS`, lock record `$P/R4-LOCK.json`). The
   analysis is frozen before any production data exists.
2. The **QTL-coloc manifest** is generated from the downloaded data and committed **before** the
   lock (W4b), alongside the trait-pair manifest; its scope is Carter's pre-registered choice among
   outcome-independent filters, with a measured cost per option. Row sets cannot depend on arm outcomes.
3. The production gate is the **git lock** (`ta_r4.r4_lock_gate`, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf). Production
   passes only if `$P/R4-LOCK.json` is git-tracked and committed, its `lock_sha` (W4b commit A) is an
   ancestor of HEAD, the three configs are `locked: true` at `lock_sha`, no `LOCKED_PATHS` file differs
   from `lock_sha` (committed, working copy or untracked), and Carter's W4b-T3 sign-off records the same
   `lock_sha`. Offline: no network, no environment-variable bypass. OSF posting is optional.
4. **Brief-blind adversarial review of the amendment's public text** (W4a) as well as of the
   manuscript (W8b), because OSF posting is public and irreversible (memory
   `feedback_internal_validation_cannot_catch_misspecified_premise`).
5. **Every manuscript number is bound to a committed FINAL table** through a placeholder renderer
   (W8a). Prose cannot drift from data.
6. The **branch classifier is total and ordered**: all 36 combinations of the decision inputs map to
   exactly one pre-registered branch by a stated precedence. The 8 combinations the research table
   leaves uncovered use four explicit `partial_rule` keys that Carter locks in W4a.
7. **Every Carter judgement is a `checkpoint:human-action`** whose reply must parse as
   `carter-approved YYYY-MM-DD` + required keys (`ta_r4.signoff`); the configuration states that
   depend on those judgements are enforced by `tests/ta_r4/test_signoffs.py`.
8. A **third admissible negative-control set** (10 GWAS-null windows, deterministic seeded rule)
   satisfies REQ-NEGATIVE-CONTROLS, because the config's third set (HLA) is inadmissible (D-24).

---

## §A Shared constants (use these literal values)

```bash
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
P=.planning/phases/ta-r4-head-to-head-reanalysis-and-submission      # phase dir (repo-relative)
MAN=$P/manifests                                                     # committed sha256/md5/dims manifests
SIGNOFFS=$P/signoffs                                                 # Carter sign-offs (ta_r4.signoff)
R4ROOT=/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4              # durable storage (D-11)
# repo-relative symlink: data/r4 -> $R4ROOT   (created by bin/r4_link_storage.sh)
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake   # 7.32.4, Python 3.11 — the ONLY snakemake
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11
RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript   # R 4.4.2, susieR 0.14.2, coloc 5.2.3
R4_CONDA_PREFIX=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4
R4_CONDARC=$R4_CONDA_PREFIX/condarc     # pkgs_dirs: [$R4_CONDA_PREFIX/pkgs]  (isolates `conda clean --tarballs`)
# bin/r4_fire.sh also exports CONDA_PKGS_DIRS=$R4_CONDA_PREFIX/pkgs HOME=$R4_CONDA_PREFIX/home (CONDARC alone does not isolate; W0a);
# channel_priority flexible (envs/plink.yml is unsatisfiable under strict; W0b2); conda-frontend conda
R4_PLINK=$R4_CONDA_PREFIX/55c377a7e8fce799d92381bcc5138d7f_/bin/plink   # PLINK v1.90b6.21 (W0b2 env solve)
QUICK="$PY -m pytest tests/ta_r4 -x -q -m 'not r4_heavy'"          # per task; must stay < 120 s
HEAVY="$PY -m pytest tests/ta_r4 -q -m r4_heavy -rs"               # per wave: live gates, Snakemake runs, frozen-script e2e
FULL="$PY -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q"
export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH        # node / conda for GSD tooling only
```

- **`r4_heavy` marker** (registered in `tests/ta_r4/conftest.py`, W0a): any test that runs `$SMK`,
  runs the frozen `run_susie_rss.R`, or reads `data/r4/results/`. Task-level `<verify>` commands
  that name a test file run it regardless of the marker.
- **R4 Snakefile:** `Snakefile.ta_r4` at the repo root (standalone; the main `Snakefile` is never
  edited; see W0b2). Invoke it only through `bin/r4_fire.sh <stage> <arm> <targets...>`, which loads
  `config/pipeline.yaml` + `config/ta_r4/overlay_base.yaml` + `config/ta_r4/overlay_<arm>.yaml`,
  sets `--conda-prefix $R4_CONDA_PREFIX`, `CONDARC=$R4_CONDARC` and
  `--profile config/ta_r4/cluster_lsf`, and for production runs `r4_lock_gate check` first.
- **Arms (overlay names):** `A3_1kg`, `A2_identity`, `A3_ukb`, `A3_ukb_isect`, `A3_1kg_isect`, `AFR661_A3`,
  `AFR661_A2`, `AFR504_A3`, `repro_routeC`, `repro_routeL`, `repro_k2d_routeC`,
  `repro_k2d_routeL`, `repro_sh2b3_r2` (13 arms: 8 production, 5 repro). A1 is a coloc-only arm (no fits). There is no `AFR504_A2`: A2 depends only on the variant frame, so the 504-sample sensitivity is A3-only. `A3_ukb` points at `EUR_ukb337k_r4` or, if Carter chooses HM3 at W2c, `EUR_ukb337k_hm3_r4` (W2d).
- **Result globs:** only through `ta_r4.paths.result_dirs("fits" | "coloc")` (production arms from ARMS; coloc adds `A1_EUR`, `A1_AFR`). Never a hand-written arm list.
- **Stages:** `repro` (exempt from the gate) and `production` (gated by the lock gate, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf).
- **Traits (EUR):** asthma, bmi, hypertension, stroke, t2d → 10 unordered pairs.
  **Traits (AFR):** asthma, stroke, t2d → 3 pairs.
- **Admissible EUR regions (10):** FTO_16q12, MC4R_18q21, SH2B3_12q24, APOL1_22q12, PYHIN1_1q23,
  CXADR_F2RL1_6p21, BMI_5q13_3 (safe id of `BMI_5q13.3`), 9p21_CDKN2A, APOE_19q13, SLC2A9_urate.
  **Not admissible (D-24):** HLA_6p21 (UKB exploratory fits only; no coloc row), BMI_Xq24 (chrX; no panel).
- **Negative-control regions (19, EUR):** cosmetic 5 (NC_OCA2_HERC2, NC_SLC24A5, NC_MC1R, NC_TYR, NC_IRF4),
  blood_group 4 (NC_ABO, NC_RH, NC_FUT1_FUT2, NC_KEL), gwas_null 10 (NC_NULL_01..NC_NULL_10, re-selected in W3f 15.7h on the production inputs;
  GRCh37 250-kb tiles 1:99750001, 1:232000001, 2:202500001, 3:34000001, 3:191500001, 6:82750001,
  11:21500001, 13:42000001, 13:71000001, 14:49250001 (start; end = start + 249999); the W0b2 draw is kept as
  `null_windows_selection.superseded-2026-10-21.tsv`).
  `regions_r4.csv` = 12 + 19 = 31 rows; `pair_manifest.tsv` = 346 rows, 320 admissible (290 EUR, 30 AFR).
- **Confirmatory analysis (pre-lock, W3d; orchestrator default under the rigor rule, Carter may change it at W4a-T3):**
  rows = primary curated EUR admissible rows (10 regions × 10 pairs = 100), p12_primary, A1 varset
  matched, reference A3_1kg; bootstrap clusters = those 10 regions (never the 29 incl. NC);
  CI / McNemar / kappa / n_both on the both-have-CS subset at PP.H4 ≥ 0.8. Negative-control rows are a
  pre-specified specificity analysis and never feed the classifier; AFR, p12_sensitivity, A1-allvars,
  UKB/isect and repro rows are descriptive.
- **Panel manifests and receipts** are keyed by (ancestry, region_safe); the file comes from
  `ta_r4.paths.panel_manifest_path(arm, ancestry)`. Repro (legacy_any) fits with no legacy panel run
  as the frozen fire did (no panel input; receipt `present: false`, `ld_source_class: missing`).
- **`data/r4`** is gitignored by W0a (it was not, measured 2026-10-21).
- **Priors:** single source `config/ta_r4/coloc_priors.yaml` (p1 = p2 = 1e-4; p12 primary 5e-6,
  sensitivity 1e-5; final values locked in W4b from Carter's W4a sign-off).

## §B Standing rules (binding; from Carter's memory rules and CONTEXT)

1. `git add` **explicit paths only**. Never `-A`, `.`, or a directory glob. Commit on the current
   branch (`m3-W2-aou-deltas`). **No branch switching** (D-16).
2. **RED first.** Every new test is committed or run RED before the implementation, and its
   negative control is **observed failing**. Paste the failing output into the plan SUMMARY. A green
   assertion that was never seen red is not evidence.
3. **Behaviour, not text.** No grep-of-source as a PASS/FAIL gate. Use imports, `ast`, exit codes,
   parsed JSON/TSV values and pytest outcomes. (Exception: banned words and internal paths in public
   text are literal properties of that text.)
4. **A count is a claim.** Every count in a LOG entry, SUMMARY or manifest is reconciled
   arithmetically against its parts, and computed by a command whose output is pasted.
5. **Durable storage (D-11).** Every R4 data/output byte lives under `data/r4/` (realpath on /rs1).
   Every produced artifact class gets a sha256 manifest TSV committed under `$MAN/`.
6. **Code freeze (D-28).** `src/legacy/region_analysis/scripts/run_susie_rss.R` is never edited.
   `tests/m3/test_source_freeze_pins.py` must stay green in every wave.
   *[2026-11-19, W3f 15.6] Lifted once for N1 (cap after LD restriction, flag default false) by
   DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze on Carter's explicit reply (6c6e9546, 1f771281), and once
   more for the flag-gated duplicate-key guard by DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze (13b0821c);
   otherwise in force; R_CODE_REF re-pinned to 13b0821 (3f4d0cb9).*
   *[2026-11-21, W3f 15.7f] Lifted a third time for exact credible-set purity (`--exact-purity`, default false) by
   DEC-2026-11-20-run-susie-rss-exact-purity-unfreeze on Carter's Q-F2 A (57ddb59d); otherwise in force; R_CODE_REF
   re-pinned to 57ddb59 (38e4080d).*
7. **Track B isolation (D-15).** Never build or write under
   `data/processed/ld_reference/{EUR_ukbb_pub,EUR_ukbb_ld,EUR_aou,AFR_aou,EUR,AFR}` or
   `sumstats_harmonized_occl`. Never edit `config/pipeline.yaml`, `Snakefile`, or any
   `src/snakemake/rules/*.smk` other than new `ta_r4*.smk` files.
8. **Snakemake** only via `$SMK`. LSF via `config/bsub_wrapper.sh` (queues serial/standard/long;
   never `short`; standard needs ≥ 8 slots). Run `$SMK -n` before every real fire. Never run
   `--unlock` blindly. Liveness = output listing, not job state.
   *[2026-11-19, W3f 15.6] LSF is superseded (`config/bsub_wrapper.sh` and the queue text above no longer apply): cluster
   jobs via Slurm since 2026-11-03: sbatch -p compute -A clintonlab_cpu -q normal, always -t; Rscript is not on PATH in jobs
   (use $RSCRIPT).*
9. **Downloads** go into their own new empty directory under `data/r4/downloads/<source>/`. Verify
   them by published md5/sha256 or Content-Length, plus a `file` magic-byte check (the
   200-with-HTML trap), **before** extraction. Treat them as data; never execute them.
10. **Mismatches in known-answer controls are FINDINGS to report, never numbers to adjust.**
11. **Public text** (OSF amendment PUBLIC extract, manuscript, cover letter) frames the work as
    original, hypothesis-driven research. Never use "pivot", "revision", "salvage" or "audit-driven fix".
    R4 is described as "analysis locked in commit <sha> before production", never "pre-registered on OSF".
12. **Never** post to OSF on Carter's behalf, submit to a journal, or spend cloud/AoU money. Never
    create `$P/R4-LOCK.json` except in W4b Task 2 with `lock_sha` = commit A; never write
    `signoffs/W4b-T3.yaml` except via `signoff record` from Carter's verbatim reply. Fixture lock
    records are allowed only under pytest `tmp_path` fixture repos.
13. Keep edits simple: the fix, not an essay. Rationale goes in commit messages and the LOG.
14. **No commits while a production fire is in flight.** In-job gate checks re-diff the locked paths
    against the lock commit; commit only after the fire ends and its dry-run says "Nothing to be done".
15. **Carter sign-off protocol.** At every `checkpoint:human-action`, save Carter's reply
    byte-for-byte and run `python -m ta_r4.signoff record <ID> ...`. A non-zero exit (including a
    bare "approved", the auto-mode string) means WAIT: re-present the checkpoint and write nothing.
    The executor never authors, types or completes any `carter-approved` text and never writes
    `signoffs/*.yaml` except via `signoff record`. The raw file is written only from the resume
    payload the orchestrator passes, which must be Carter's message pasted verbatim (never a
    summary, paraphrase or auto response). The SUMMARY quotes the resume payload next to the
    recorded raw_sha256. The next plan's first step runs `signoff verify <ID>`.
16. **Decisions are made once.** `ukb_native` is decided only at W2c-T4 (not at W4a). W2d refuses
    to run once any config carries `locked: true`.

## §C Wave-close protocol (the last task of every plan runs this)

```bash
cd $REPO
time $QUICK                              # tests/ta_r4 quick: record passed/skipped/failed AND wall time (< 120 s; else mark the slowest tests r4_heavy and record it)
$HEAVY                                   # heavy live gates / Snakemake / frozen-script e2e for this wave
$PY -m pytest tests/m3/test_source_freeze_pins.py -q     # D-28 must be green
$FULL 2>&1 | tail -5                      # record ids/passed/skipped/failed vs the W0a baseline
git status --porcelain -- <every path in files_modified>   # inspect; stage nothing else
git fsck --connectivity-only 2>&1 | tail -3     # BEFORE commit: must report no broken/missing links
git add <explicit paths>                 # never -A / .
git commit -m "<type>(ta-r4-<label>): <summary>

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
git fsck --connectivity-only 2>&1 | tail -3     # AFTER commit: still clean
git push origin HEAD                     # D-16: push after each wave; tags need: git push origin <tag>
```

Then append a dated entry to `$P/ta-r4-LOG.md` (what ran, counts with reconciliation, commit
sha, push result, QUICK wall time) and refresh the 2026-10-21 Track A block of `.planning/STATE.md`
(memory `feedback_state_md_keep_current`). Commit both in the same or an immediately following
explicit-path commit, then push.

The full-suite rule: **0 removed test ids, 0 outcome changes in `tests/m3`**, and only additions
in `tests/ta_r4`. The baseline is the W0a re-measurement (last recorded 1299 ids / 1265 passed /
34 skipped / 0 failed at 2026-09-19). Any change to a pre-existing outcome is a STOP-and-report.

If `git fsck` reports missing objects (before or after the commit), follow memory
`reference_gpfs_git_object_store_loss` (mirror clone from origin, repack, copy the pack) **before**
committing again. Never `reset`.

## §D Checkpoint rule under `--auto --chain` / `mode: yolo`

Verified against `~/.claude/get-shit-done/workflows/execute-phase.md` (auto-mode checkpoint
handling): `checkpoint:human-verify` is auto-approved with the response "approved";
`checkpoint:decision` auto-selects its first option; **only `checkpoint:human-action` stops** and
is presented to Carter. Therefore:

- **Every** checkpoint whose outcome is Carter's judgement or action is `checkpoint:human-action`:
  W2c-T4, W3b-T3, W4a-T3, W4b-T3, W7-T3, W8b-T3, W9-T1, W9-T4. This phase has no
  `human-verify` or `decision` checkpoints.
- The resume token is `carter-approved YYYY-MM-DD` on the first line, followed by the checkpoint's
  required `key: value` lines (`ta_r4.signoff.SCHEMAS`). The auto path cannot produce it; a bare
  "approved" is WAIT (§B.15).
- **Code-level sentinels** back the checkpoints that change state:
  - Lock gate (`r4_lock_gate`, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf): production rules raise at DAG time and in every job
    unless the lock record, lock commit, locked configs, locked paths and W4b-T3 `lock_sha` all agree.
    A wrongly passed checkpoint still cannot start production.
  - `tests/ta_r4/test_signoffs.py` (W0b1): `review_decisions.yaml` ⇒ valid W2c-T4; any locked
    config ⇒ valid W4a-T3 with equal values; tracked lock record ⇒ valid W4b-T3 with equal `lock_sha`; venue overlay ⇒ valid
    W9-T1; checked W9 ROADMAP line ⇒ valid W9-T4.
  - `render_manuscript --venue-overlay` refuses without a valid W9-T1; estimand outputs are FINAL
    only with locked configs + valid W4a-T3 + the offline gate passing.
  - The next plan after W3b, W7 and W8b starts with `signoff verify <ID>`.
  - W2d refuses to run after the lock; W7 refuses to aggregate unless the lock diff (incl.
    `run_aggregation.py`) is empty.

## §E Requirement mapping

| REQ | Plans |
|---|---|
| REQ-PUBLIC-DATA-ONLY | W0a (`config/ta_r4/data_sources.yaml` with `license` + `public: true`), W2a, W2b, W2c, W2d (HM3 list entry), W8a (Data availability), W9 |
| REQ-SUSIE-RSS-POLICY | W0b1 (policy files), W3a (repro policy), W5a (production policy, disclosed), W7 (`min_abs_corr` sweep table), W8a (Methods) |
| REQ-OSF-PREREG | W0b1 (sign-off sentinels), W0b2 (original gate), quick-261028-kkg (lock gate), W4a (amendment + locks), W4b (lock commit A + lock record + W4b-T3), W5a–W6 (gate exercised), W9 |
| REQ-SNAKEMAKE-CI | W0a (env restore), W0b2 (`Snakefile.ta_r4` dry-run tests, lockfiles), W0d (toy 3-locus `--use-conda` end-to-end), every plan (suite) |
| REQ-PATH-PARAMETERIZATION | W0a (symlink + literal scan over config/ta_r4, src/python/ta_r4, src/snakemake/scripts/ta_r4, src/snakemake/rules/ta_r4_*.smk, Snakefile.ta_r4), W0b1 (paths module) |
| REQ-PP.H4-THRESHOLD-SWEEP (supporting) | W3d, W7 |
| REQ-NEGATIVE-CONTROLS (supporting) | W0b2 (three admissible sets: cosmetic, blood_group, gwas_null), W4a (disclosed), W5b, W7 |

---

## Decision coverage matrix (D-01..D-28)

| D | Plan(s) / task | Coverage | Notes |
|---|---|---|---|
| D-01 three arms, identical inputs | W0b1 T1 (arm overlays), W0c T2 (matched-set enforcer), W0d T1–T2 (A1 / coloc.susie), W2a T2 (A2 payload from the A3 frame), W2b T3 (isect re-orientation), W5a, W5b | Full | A1 ≠ "identity LD" stated in W8a |
| D-02 fallback_abf labelled; no-CS rate reported | W0d T1–T2 (`test_fallback_labelled`), W3d (E4 no-CS rate), W5b, W7 | Full | |
| D-03 1000G primary + A3-UKB sensitivity | W2a T2, W2b T2–T3, W2d T1, W5a | Full | |
| D-04 UKB under separate path | W2b T3 (`data/r4/ld/EUR_ukb337k_*`), W2d (hm3 dir), W0b2 T3 (isolation test) | Full | |
| D-05 analysis locked before production (lock gate, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf) | W4a, W4b T3, W0b2 T2–T3 (gate), W5a/W5b/W5c/W6 T1 (gate + code-state re-check) | Full | |
| D-06 E-2 fix TDD + before/after + new DEC | W0a T3 (DEC), W1 T1–T3, W3e (QTL_A3/A2 orient on; QTL_legacy pre-fix), W6, W3d + W7 (E7 table), W8a (Methods note) | Full | |
| D-07 exhaustive EUR 10×10 + QTL; AFR secondary | W0b2 T1 (pair manifest), W2c T2 + W2d T2 (QTL manifest + scope), W5a–W5c, W3e, W6 | Full | |
| D-08 fresh 4–5k draft; supplementary provenance; brief-blind review | W8a, W8b | Full | new path `docs/manuscript/id-vs-ref-LD-r4.md` |
| D-09 venue after results; neutral format; no preprint | W8a (neutral), W9 T1 (human-action venue) | Full | |
| D-10 regenerate everything | W2a, W2b, W2c, W3a, W5a–W6 | Full | |
| D-11 /rs1 storage + committed sha256 manifests | W0a T1–T2, §B.5 in every plan, W0a T1 (`test_storage_on_rs1`) | Full | |
| D-12 known answers before comparison | W2a T2–T3 (a: panel md5 + dims), W3a, W3b (b) | Full | mismatches = findings; W3b §(8) records the measured cause of the 28 empty R1 rows (ROADMAP R1_STRUCTURAL item) |
| D-13 no silent identity fallback; named test | W0c T1–T2 (globs from ARMS incl. A3_1kg_isect), W5a, W5c, W6 | Full | `tests/ta_r4/test_no_silent_identity.py` |
| D-14 AFR + identity overlays; restore qtl_processing.yml | W0a T2, W0b1 T1 | Full | |
| D-15 Track B isolation | W0b2 T3, §B.7, full `tests/m3` every wave | Full | |
| D-16 no branch switch; explicit staging; push per wave | §B.1, §C; W0a T2 tag `ta-r4-pre-baseline` pushed explicitly | Full | |
| D-17 SH2B3 exact-R2 known answer + L10 separate | W3b | Full | |
| D-18 BMI REF/ALT restored, checksum-pinned, match-rate report, disclosed | W1 T1, W4a, W8a | Full | |
| D-19 osf-correction-v2 retired unposted; R4 amendment carries E-2 | W0a T3 (DEC), W4a, W8a | Full | |
| D-20 AFR 661 primary, 504 sensitivity | W2b T1, W5c | Full | |
| D-21 A1 matched primary + all-variants secondary | W0d T1, W5b | Full | |
| D-22 QTL under A2 and A3 | W3e (runner), W6 (run) | Full | plus the legacy pre-fix route for E7 |
| D-23 E8 simulation, pre-registered secondary | W3c (harness), W4a (registered), W5c T3 (run), W7 | Full | |
| D-24 HLA / BMI_Xq24 inadmissible; HLA-UKB exploratory | W0b2 T1 (manifest `admissible` column), W2b T3, W5a, W7 (`hla_exploratory.tsv`) | Full | HLA UKB fits are exploratory and produce **no coloc row**: no admissible 1000G comparator exists, so no head-to-head is defined |
| D-25 measured n, trait type, sdY | W2a T1–T3 (panel + trait manifests), W2c T4 (Carter answers), W4a | Full | |
| D-26 E1–E8 + five branches; κ / n_both locked by Carter | W3d T1 (estimators, `confirmatory:` block + contrast_stats, total ordered classifier, 8 partial_rule combos), W3d T3 (run_aggregation, pre-lock), W4a (e)/(f) rendered from the yaml + T3 (Carter locks), W4b T1 (configs), W7 T1 (frozen code run) | Full | confirmatory set = 100 primary curated EUR rows, 10 clusters (orchestrator default; Carter may change at W4a-T3) |
| D-27 lock record; production refuses without it (lock gate, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf) | W0b2 T2–T3, W4b, W5a T1 | Full | |
| D-28 no edit to run_susie_rss.R | §B.6; `test_source_freeze_pins` in every §C | Full | |

No decision is partial. No deferred idea (AoU-AFR-LD Track A re-analysis, newer GWAS vintages)
appears in any plan.
