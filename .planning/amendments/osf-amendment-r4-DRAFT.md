# OSF Amendment — R4 head-to-head analysis plan (DRAFT, NOT POSTED)

> DRAFT written in ta-r4 W4a. The public text is `extract()` of this file (`src/python/ta_r4/extract_paste_block.py`):
> only the lines strictly between the two marker lines. Lock values are `‹CARTER-LOCK: …›` placeholders until
> Carter's W4a-T3 sign-off; W4b copies this file to `osf-amendment-r4-FINAL.md` with the locked values.
> Posting is optional (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf) and is Carter's alone.

---

## Pre-Paste Reference (do NOT paste this block)

Every number in the body is copied from a committed file named here. `$P` = `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission`, `$MAN` = `$P/manifests`.

| Body item | Value | Source |
|---|---|---|
| Target | osf.io/az52u (supplementary file, M1/R3 pattern); root registration osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) | R3 exemplar |
| Gate wording | "analysis locked in commit <sha> before production"; never "pre-registered on OSF" | DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf |
| Arms, overlays | A1, A2_identity, A3_1kg, A3_ukb, A3_ukb_isect, A3_1kg_isect, AFR661_A3, AFR661_A2, AFR504_A3 | `src/python/ta_r4/arms.py`, `$P/ta-r4-PLAN-INDEX.md` §A |
| Pair manifest | 346 rows; admissible 320 = EUR 290 (100 primary + 190 negative control) + AFR 30; inadmissible 26 = HLA_6p21 13 + BMI_Xq24 13 | `config/ta_r4/pair_manifest.tsv` (pandas groupby, W4a LOG) |
| EUR n | 489 (22 `.fam`, 489 distinct FID/IID) | `$P/ta-r4-W2-REVIEW-PACKET.md` §1; `$MAN/panels_EUR_1kg_r4.tsv` n_samples |
| AFR n | 661 = 504 + ASW 61 + ACB 96; 504 sensitivity | `$MAN/afr_samples_sha256.tsv` |
| Sumstats sha256 | 8 inputs + restored BMI | `$MAN/sumstats_r4_sha256.tsv` |
| 1000G EUR plink | Zenodo 10515792, md5 a7773ab485827b533cb300c76356d76b | `config/ta_r4/data_sources.yaml` |
| UKB LD | Weissbrod 2020 UKB 337k British-ancestry LD (not Pan-UKBB, `used: false`); 76 tiles sha256 | `config/ta_r4/data_sources.yaml`; `$MAN/ukb337k_tiles_sha256.tsv` |
| BMI restoration | 2,336,269 / 2,327,244 / 0 / 0 / 9,025 (3,844 A/T + 5,181 C/G) / 23,896 / 10,000 of 10,000 | `$MAN/bmi_allele_restoration_report.tsv`; W1 SUMMARY |
| Trait types, sdY | asthma/stroke/t2d cc; bmi quant sdY 1; hypertension (SBP) quant sdY 20.7 | `config/ta_r4/trait_manifest.tsv`; `signoffs/W2c-T4.yaml` |
| W2c decisions | ukb_native: native; qtl_scope: full | `config/ta_r4/review_decisions.yaml`; `signoffs/W2c-T4.yaml` |
| UKB native > 16,000 | HLA_6p21 34,361; PYHIN1_1q23 26,050; BMI_5q13_3 24,121; SLC2A9_urate 16,752 | `$P/ta-r4-W2-REVIEW-PACKET.md` §6 |
| AFR > 16,000 | BMI_5q13_3 21,323/21,154; PYHIN1_1q23 20,818/20,686 | REVIEW-PACKET §5 |
| Confirmatory block | rendered by `render_confirmatory(decision_rules.yaml)`; 100 rows / 10 clusters | W3d SUMMARY ("Real manifest") |
| Truth table | 36 = 18 + 3 + 3 + 2 + 2 + 8 partial_rule | W3d SUMMARY |
| Simulation | 10 regions × 5 scenarios × 2 gen panels × 200 reps; n_per_trait 100000; causal_z 7; window 1000; seed_base 20261021 | `config/ta_r4/simulation.yaml`; W3c SUMMARY Deviation 1 (`n` → `n_per_trait`) |
| p12 | Wallace 2020 PLoS Genet 16:e1008720 (quotes in LOG, 2026-11-04 W4a) | W4a LOG |
| Known answers | §(1)–(8) | `$P/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md` |
| JSON credible-set fix | 53106f8f; W3a/W3b not re-run | DEC-2026-11-03-run-susie-rss-json-cs-purity-unfreeze |
| Null windows | rule `window=250000 pmax=1e-05 min_variants=200 n_select=10 seed=20261021`, 2,865 candidates | `$MAN/null_windows_selection.tsv`; `src/python/ta_r4/select_null_windows.py` |
| NC rows | cosmetic 50, blood_group 40, gwas_null 100; ABO 10 rows `reported_stroke_association_verify` | `config/ta_r4/pair_manifest.tsv` |
| QTL | 23,310 features (eQTL 21,149 + sQTL 2,161) × 5 traits = 116,550 rows; 899 groups per arm | `$MAN/qtl_harmonized_sha256.tsv`; `config/ta_r4/qtl_manifest.tsv`; W3e SUMMARY |
| Policies | production `config/susie_policy.yaml` (L 10, max_iter 100 / retry 200); reproduction `config/ta_r4/susie_policy_repro_iter100.yaml` (retry 100) | `src/python/ta_r4/arms.py` |
| Analysis-code commits | W0d 99e05961, c536547c; W1 fb0a5b5c, 4896e011, e7224a91; W3c 0efac930; W3d db2bf8c9, 83b3240d, bd551895, aef3be84; W3e 4d27ac00, 0ca16af9; 53106f8f | `git merge-base --is-ancestor` (W4a LOG) |
| Frozen paths | `r4_lock_gate.LOCKED_PATHS` (18 entries) | `python -m ta_r4.r4_lock_gate paths` |
| OPEN (W4a review, blocks the lock) | 16,000 cap applies before panel restriction → early-exit fits stop pairs (N1); lock omits config/susie_policy.yaml, config/pipeline.yaml and 4 QTL inputs (N3); no runtime input sha256 (N4); gate at DAG time only (N5); aggregation lacks a coverage guard (N6); McNemar row independence, no minimum regions (N7); QTL fallback rows dropped from the aggregate (N12); simulation identity refit and pooling (N14); data_sources.yaml AFR T2D label (T1) | `$P/ta-r4-W4-AMENDMENT-REVIEW-as-received.md` disposition table |
| OPEN (blocks the lock) | fit-name alignment: production coloc refuses rsid-named fits vs chr:pos sumstats (`UNMAPPED_FIT_NAMES`, measured W4a on repro_routeC SH2B3 hypertension × stroke) | W0d SUMMARY "Decision needed"; W4a LOG |

**Pre-paste checklist (work top-to-bottom; nothing here is pasted):**

1. Carter's W4a-T3 sign-off verifies (`python -m ta_r4.signoff verify W4a-T3`).
2. W4b replaces every `‹CARTER-LOCK: …›` with the locked value, including the lock commit sha; FINAL has none left.
3. `python -m ta_r4.extract_paste_block --in FINAL --out PUBLIC`; `test_amendment_text.py` passes with FINAL/PUBLIC checks run.
4. Every commit sha in (m) is an ancestor of HEAD.
5. Posting is optional; if Carter posts PUBLIC, record the URL and timestamp in `.planning/osf_deviations.md`.

---

--- PASTE INTO OSF FROM HERE ---

**Amendment to pre-registration osf.io/pvb5j: identity-LD versus reference-LD colocalization at curated cardiometabolic pleiotropy loci — head-to-head analysis plan (R4)**

**Date:** ‹CARTER-LOCK: posting date›

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Status of this plan:** the analysis plan, configuration and code below are fixed by the analysis locked in commit ‹CARTER-LOCK: lock commit sha› before production. Production runs are refused unless an offline gate, checked when a production run is constructed, finds that the lock commit is an ancestor of the running code and that no frozen file in (m) has changed. Known-answer controls, data acquisition and panel construction ran before the lock and are reported below.

**Purpose:** to fix, before any production fit exists, the arms, estimands, decision rules, outcome branches, simulation design, negative controls and known-answer results of a matched comparison of linkage-disequilibrium (LD) handling in cross-trait colocalization.

**New analytical commitments:**

(a) **Hypothesis.** We test whether LD handling changes cross-trait colocalization calls at curated cardiometabolic pleiotropy loci. "Identity LD inflates colocalization" is one of five pre-specified outcomes, not a premise.

(b) **Arms.** All arms use identical summary statistics, regions, priors and SuSiE policy. A1: `coloc.abf` (single causal variant; uses no LD matrix). A2 (`A2_identity`): SuSiE-RSS with R = I followed by `coloc.susie`. A3 (`A3_1kg`, reference): SuSiE-RSS with 1000 Genomes Phase 3 EUR LD followed by `coloc.susie`. A1 is not "identity LD": it assumes one causal variant per trait and reads no LD at all, whereas A2 fine-maps multiple signals under an identity matrix. A1 vs A3 compares the common literature method with fine-mapped colocalization; A2 vs A3 isolates the LD matrix. Sensitivity arms: `A3_ukb` (UK Biobank LD, native variant sets), `A3_ukb_isect` and `A3_1kg_isect` (both panels restricted to their shared variants). Secondary ancestry arm: AFR on 1000 Genomes AFR (`AFR661_A3`, `AFR661_A2`, `AFR504_A3`).

(c) **Data.** Five EUR traits (asthma, BMI, hypertension, stroke, type 2 diabetes; 10 unordered pairs) and three AFR traits (asthma, stroke, type 2 diabetes; 3 pairs). Inputs (sha256 recorded before production): asthma EUR, GBMI 2021, `22b2807551ca6a5967fa67ba81c7546cc66a7f3b9d0055cd23ddd8d2b3eda137`; asthma AFR, GBMI 2021, `c9a723f3c900797692f54c6df5ae547840131f79a9a7891490d1670fc09a5c30`; BMI EUR, Yengo 2018, `c914e16b6b4e3264993c39db141090856e7e7fcdd1cad69405b04a2384acd9a0`; hypertension EUR, Evangelou 2018 systolic blood pressure, `a740bb261b58cbb9f284139dd0012cb7fc01df24095e9a14833118fac6eba78f`; stroke EUR, METASTROKE (Traylor 2012), `4dafe6152375b57e9b82033e92a3327df8a39f08fcea5dd3c86fda67394c3cd9`; stroke AFR, GIGASTROKE AFR GCST90104553 (small vessel stroke), `bf08ef2831b03a160857ef420ea448eeb38fac94a68b74359840d28e5d070384`; type 2 diabetes EUR, DIAMANTE 2022, `7cf7723ae0a6e6d05780d76ad53f922ec3a130c47ea38db26b1001911d6e4e8f`; type 2 diabetes AFR, T2DGGI (Suzuki 2024, effective N), `23347618a0cb31bd995aa49155ec933b276544e12f71e76279a66493eeb0470c`. The BMI file lacked allele columns; REF and ALT were restored from the same Yengo 2018 release (`0147fbcd0d12cc917f9c2babe8e6a462b3c51ce7ff885999f310c445c32b6587`) by a checksum-pinned script: of 2,336,269 rows, 2,327,244 joined on position and SNP identifier with BETA, SE and P equal at the stored precision (the output keeps the original strings), 0 were flipped, 0 had value mismatches, and 9,025 palindromic rows (3,844 A/T, 5,181 C/G) absent from the source were dropped; 23,896 rows with BETA = 0 are kept; in a 10,000-row check against the raw GIANT file the restored ALT equals the tested allele in 10,000 of 10,000. Restored file: `2f87e771c5a20660611c3de5e737f6ab29ec66d45f1a62302532e6dc3bc5b1b4`. Trait types for `coloc.abf`: asthma, stroke and type 2 diabetes case-control; BMI quantitative, sdY 1 (inverse-rank-normal units); hypertension quantitative (the file is systolic blood pressure in mmHg), sdY 20.7 (UK Biobank + BiLEVE SD, Evangelou 2018 Supplementary Table 1a). LD panels: 1000 Genomes Phase 3 EUR (LDSC plink release, Zenodo 10515792, md5 `a7773ab485827b533cb300c76356d76b`; n = 489 from the `.fam`), built with `--keep-allele-order` and REF/ALT taken from the same run's `.bim`; 1000 Genomes AFR, n = 661 (504 continental + ASW 61 + ACB 96), with the 504 continental samples as sensitivity; UK Biobank 337k British-ancestry LD (Weissbrod et al. 2020), used as native per-region panels (`ukb_native: native`) assembled from LD tiles (per-tile sha256 recorded); variant pairs not covered by any tile are set to 0 (for example 8,635,830 pairs in the BMI_5q13_3 intersection panel). Per-panel md5, sha256, variant count and, for 1000 Genomes panels, sample count are recorded in the committed panel manifests listed in (m).

(d) **Matched variants and the zero-credible-set fallback.** A2's identity payload is built from A3's variant frame, so A2 and A3 fit identical variant sets. A1 (primary, `matched`) runs on the intersection of the two A3 fits' variants; A1 on all region summary-statistic variants matched on position and unordered alleles (`allvars`) is a secondary row (rows lacking alleles match on position only). When either trait has zero credible sets under an arm, that row's outcome is `coloc.abf` on the same arm's variant set, labelled `fallback_abf`; by construction it equals A1 on that set. Fallback and `coloc.susie` values are never pooled silently: every estimand is reported on the subset where the arm produced `coloc.susie` and on all rows with fallback labelled, and the per-arm no-credible-set rate is a reported result. "Credible set" means the purity-filtered sets that `coloc.susie` reads (min_abs_corr 0.5). Fits still non-converged after the retry ladder in (k) are retained and enter colocalization. Fits that exit before fitting (no variants, or more than 16,000 variants) are handled by ‹CARTER-LOCK: early-exit fit rule; the current code stops the pair›. Fit variant names are aligned to summary statistics by the rule ‹CARTER-LOCK: fit-name alignment rule; the current code refuses rsid-named fits against chr:pos summary statistics›.

(e) **Estimands.** Unit: one (region, ancestry, trait-pair) row of the static pair manifest. Region statistic S: for `coloc_susie` rows the maximum PP.H4 over credible-set pairs; for `fallback_abf` and A1 rows PP.H4. E1 (primary): Δ = S(X) − S(A3_1kg) for X ∈ {A1_matched, A2_identity}; median and mean with region-cluster bootstrap 95% CI; paired sign test (descriptive). E2: 2×2 agreement at PP.H4 ≥ 0.8 (primary) and 0.5 (secondary) and over {0.5, 0.7, 0.8, 0.9}; Cohen's κ; exact two-sided McNemar test with b = X calls H4 and A3 does not, c = the reverse. E3: cross-tabulation between arms of the argmax hypothesis (H0–H4) of the row's reported PP vector (for `coloc_susie` rows, the credible-set pair with the maximum PP.H4; ties take the first). E4: per fit, number and size of credible sets and L saturation; for fits with status ok, cross-evaluated purity (A2 sets scored against the 1000G R; `A3_1kg_isect` and `A3_ukb_isect` sets scored against each other's R); per-arm no-credible-set rate, defined per pair row (either trait with zero sets) over all rows of that arm. E5: `estimate_s_rss` λ̂ (continuous; no cut-off) and kriging outlier counts (logLR > 2 and |z| > 2) per A3 and A3-UKB fit. E6: A3-UKB vs A3, on native variant sets and on the intersection-matched sets: the both-have-CS paired summary of E1 per p12 key, with median variant counts per side. E7: earlier-pipeline reproduction vs R4 A3 for fit yields, the SH2B3 pairs and QTL tiers, with flipped share = flipped / (exact + flipped) per region on the fine-mapping side and per QTL row output on the QTL side. E8: simulation calibration (g). The confirmatory analysis is exactly:

- Contrasts: A1_matched_vs_A3_1kg, A2_identity_vs_A3_1kg; reference arm A3_1kg.
- Row set: pair-manifest rows with row_class = primary, ancestry = EUR, admissible = true, p12_key = p12_primary, a1_varset = matched.
- Bootstrap clusters: region_safe of the confirmatory rows.
- Both-have-CS subset per contrast (A2_identity_vs_A3_1kg: both methods coloc_susie; A1_matched_vs_A3_1kg: A3 method coloc_susie).
- Confidence interval: median_delta_pph4 on the both_have_cs subset by region_cluster_bootstrap_percentile, 10000 resamples, seed 20261021, level 0.95.
- McNemar test and Cohen's kappa: on the both_have_cs subset; a call is region_stat >= threshold_primary (threshold_primary = 0.8; region statistic for coloc_susie rows = pp_h4_max).
- n_both: the size of the both_have_cs subset.
- Categories (alpha = 0.025): n_both_ok: n_both >= n_both_min. ci: pos if ci_lo > 0; neg if ci_hi < 0; else incl0. mcnemar: sig_X_gt_A3 if p < alpha and b > c; sig_A3_gt_X if p < alpha and c > b; else ns. kappa_ok: kappa >= kappa_cut; if kappa undefined, observed_agreement == 1.
- Classifier precedence (first match wins): n_both, ci_includes_0, ci_mcnemar_agree, partial_rule.
- Never classifier inputs: negative_control rows (pre-specified specificity analysis); AFR rows (secondary); p12_sensitivity; A1 allvars; A3_ukb / A3_ukb_isect / A3_1kg_isect (E6); repro arms.

The row set is the 10 admissible curated EUR regions × 10 trait pairs = 100 rows, clustered by those 10 regions. alpha = 0.025 is a Bonferroni split over the two contrasts. A CI bound equal to 0 is `incl0`. Everything outside this block is descriptive.

(f) **Decision rule.** Cut-offs: kappa_cut = ‹CARTER-LOCK: kappa_cut, proposed 0.6›; n_both_min = ‹CARTER-LOCK: n_both_min, proposed 10›; p12 (primary) = ‹CARTER-LOCK: p12_primary, proposed 5×10⁻⁶›, p12 sensitivity 1×10⁻⁵, p1 = p2 = 1×10⁻⁴ for every arm. p12 = 5×10⁻⁶ follows Wallace (2020, PLoS Genet 16:e1008720), whose simulations suggest the coloc default of 10⁻⁵ "may be overly liberal" and that 5×10⁻⁶ "may be a more generally robust choice"; the same paper's closing summary prints 5×10⁻⁵, which we note. Each contrast is classified into exactly one branch, applying the steps in the order above: NON_INFORMATIVE if n_both < n_both_min; else, if the CI includes 0, NO_SYSTEMATIC_DIFFERENCE when kappa_ok and HETEROGENEOUS otherwise; else INFLATION_SUPPORTED if ci = pos and mcnemar = sig_X_gt_A3, DEFLATION if ci = neg and mcnemar = sig_A3_gt_X; else the partial rule below. NO_SYSTEMATIC_DIFFERENCE is not an equivalence test: it records a CI that includes 0 with agreement at or above kappa_cut. All 36 category combinations map to one branch (18 NON_INFORMATIVE, 3 NO_SYSTEMATIC_DIFFERENCE, 3 HETEROGENEOUS, 2 INFLATION_SUPPORTED, 2 DEFLATION, 8 by partial rule).

| ci | mcnemar | kappa_ok | branch |
|---|---|---|---|
| pos | ns | true | ‹CARTER-LOCK: partial_rule.ci_pos_mcnemar_ns, proposed HETEROGENEOUS› |
| pos | ns | false | same key |
| pos | sig_A3_gt_X | true | ‹CARTER-LOCK: partial_rule.ci_pos_mcnemar_opposite, proposed HETEROGENEOUS› |
| pos | sig_A3_gt_X | false | same key |
| neg | ns | true | ‹CARTER-LOCK: partial_rule.ci_neg_mcnemar_ns, proposed HETEROGENEOUS› |
| neg | ns | false | same key |
| neg | sig_X_gt_A3 | true | ‹CARTER-LOCK: partial_rule.ci_neg_mcnemar_opposite, proposed HETEROGENEOUS› |
| neg | sig_X_gt_A3 | false | same key |

All five branches are publishable. The two contrasts are classified and reported separately; no single branch is chosen across them.

(g) **Simulation (E8, secondary).** For each of the 10 admissible regions, a window of 1,000 contiguous panel variants centred on the panel midpoint (all variants if fewer) is taken from the intersection-matched panels. z-scores are drawn independently for the two traits as z ~ N(R s, R) from a PSD-clipped generation matrix R, with s = 7 at each causal variant and n = 100,000 per trait (config key `n_per_trait`; a bare `n:` key is read as FALSE by R's YAML parser, so it was renamed before any run). Scenarios: H0 (no causal variant), H4 (one shared causal variant) and H3 (distinct causal variants with r² in [0.25, 0.35], [0.55, 0.65] or [0.85, 0.95] under the fitting panel). Generation panels: 1000G EUR and UK Biobank (reference mismatch); the fitting panel is always 1000G EUR. 200 replicates per cell; seed = 20261021 + the cell's position in a fixed sorted order. A1, A2 and A3 run through the same fitting and colocalization code as the real data at p12 primary; as in the fitting script, a fit that the ladder cannot produce is refitted with R = I. Reported: share of replicates with S ≥ 0.8 per arm, scenario and generation panel (false-H4 under H0/H3, true-H4 under H4), pooling `coloc_susie` and `fallback_abf` rows, with Wilson 95% intervals; cells with no qualifying causal pair are counted, never filled in.

(h) **Known-answer results (before the lock).** All 181 checks on the 1000G EUR, identity and earlier panels passed; the rebuilt 1000G EUR panels equal the earlier panels in variant count and |R| in all 10 shared regions. The earlier fits labelled real-LD (96; the AFR ones had used placeholder identity panels) and identity-LD fits (95) were reproduced by two routes, the current fitting code under reproduction semantics and the code at the time of the earlier fire, with equal status, credible-set counts, variant identities and PIPs (max |ΔPIP| = 0); credible-set counts also match the earlier identity-LD record in 95 of 95 fits, whose set-size column records label length rather than size. The earlier real-LD status split (48 ok / 18 non-converged) reproduces as 44 / 22: the four FTO_16q12 EUR fits (asthma, BMI, hypertension, type 2 diabetes) were originally fitted on a placeholder LD file and do not converge on the real panel. The earlier "51 of 96 non-empty fits" counted the fit JSON's unfiltered credible sets; `coloc.susie` reads purity-filtered sets, of which 25 of 96 fits have any. The fitting script's JSON now writes the purity-filtered sets (commit 53106f8f; fitted objects unchanged); the reproduction outputs were not re-run, so the current route's JSON differs from the earlier route's JSON on fits with impure sets. SH2B3_12q24 EUR: the reported PP.H4 = 1.0 (BMI–hypertension, hypertension–stroke, hypertension–type 2 diabetes) reproduces byte-for-byte (9 of 9 pair outputs) only in its actual configuration: L = 15 fits at max_iter 500/1000 for BMI, hypertension and stroke (all non-converged), L = 10 fits for asthma and type 2 diabetes, `coloc.susie` with package-default priors. Under standard L = 10 with effective max_iter 100, BMI–hypertension and hypertension–stroke remain 1.0 but hypertension–type 2 diabetes is 3.1×10⁻⁸. In the earlier 28 empty trait-pair rows at four other regions, the measured fact is non-empty PP.H4 in 0 of 28; on the reproduced fits 22 of 28 have zero purity-filtered credible sets on at least one side, and of the other 6 (all FTO_16q12), 3 hypertension pairs had zero sets in the fits read at the time and 3 reached `coloc.susie` without a posterior. The `fallback_abf` rule in (d) is the pre-specified handling of the zero-set case.

(i) **Allele orientation.** In the earlier pipeline the EUR summary-statistics-to-panel join matched on position without alleles, and the orientation computed by the allele-aware QTL join was recorded but not applied to QTL effect estimates. In R4, EUR panels carry REF/ALT, the EUR join is allele-aware (exact or swapped four-key match; palindromic sites dropped), and QTL betas are signed to the panel ALT using the QTL's own alleles (exact, flipped, palindromic and mismatched rows counted). All R4 arms run on this code. E7 reports the earlier-pipeline reproduction beside the R4 values, with flipped shares per region.

(j) **Inadmissible regions.** HLA_6p21 and BMI_Xq24 have no admissible 1000G comparator (BMI_Xq24 is on chromosome X, for which no panel exists) and are reported as inadmissible. HLA_6p21 UK Biobank fits are exploratory, reported descriptively, and produce no colocalization row because the pair manifest marks HLA_6p21 inadmissible.

(k) **SuSiE policy.** GWAS fits, production: L = 10, coverage 0.95, a three-step ladder (max_iter 100; retry at max_iter 200, which current code honours; then ridge-regularized R with ε = 1×10⁻⁴), fits still non-converged retained and flagged, min_abs_corr 0.5 (sweep 0.1/0.5/0.9 reported), estimate_residual_variance at the susieR 0.14.2 default (FALSE). A fit is skipped as `too_many_variants` when the trait's variants after the variant-catalog join, before restriction to the panel, exceed 16,000. QTL fine-mapping uses `coloc::runsusie` defaults with one retry at max_iter 200. Reproduction controls use the earlier effective max_iter 100 and are never estimand inputs.

(l) **Negative controls and QTL scope.** Negative controls are a pre-specified specificity analysis (share of rows with S ≥ 0.8 per set and arm) and never classifier inputs: 5 pigmentation loci (OCA2/HERC2, SLC24A5, MC1R, TYR, IRF4), 4 blood-group loci (ABO, RH, FUT1/FUT2, KEL) and 10 GWAS-null windows, each × 10 EUR pairs = 190 rows. Null windows: GRCh37 autosomal 250-kb tiles, excluding tiles within 1 Mb of any curated or pigmentation/blood-group region and the HLA region, with minimum P ≥ 1×10⁻⁵ across all 8 summary-statistic files and ≥ 200 variants in each EUR file; 10 of the 2,865 candidates drawn uniformly with seed 20261021. ABO has a reported stroke association (not verified here), so its 10 rows carry a caveat. Null windows are expected, not guaranteed, to yield few credible sets; the arm-discriminating calibration is (g). QTL layer (`qtl_scope: full`): GTEx v8 eQTL and sQTL via the eQTL Catalogue, 49 tissues, every gene (eQTL) or splice junction (sQTL) with data in the 10 admissible regions: 23,310 features (region × source × tissue × gene or junction) × 5 EUR traits = 116,550 rows, run under A3 and A2 (the earlier-pipeline QTL fitting and orientation, run on the same junction-level inputs, is a descriptive E7 comparator). sQTL are harmonized per junction; the earlier layer harmonized per gene, mixing junctions of multi-junction genes. QTL rows with no credible set are labelled `fallback_abf` in their per-row outputs and are not tiered; rows below the 50-variant bridge floor are kept with method `none`. QTL `coloc.susie` uses the package priors, which equal the p12 primary above.

(m) **What is not changing.** Public data only; multi-arm triangulation; append-only deviation reporting; earlier registrations stand. Analysis code: 99e05961, c536547c (pair colocalization), fb0a5b5c, 4896e011, e7224a91 (allele orientation), 0efac930 (simulation), db2bf8c9, 83b3240d, bd551895, aef3be84 (estimands, classifier, coverage, aggregation), 4d27ac00, 0ca16af9 (QTL layer), 53106f8f (credible-set output). Frozen at the lock commit (checked when a production run is started): `src/snakemake/scripts/ta_r4`, `src/python/ta_r4`, `src/snakemake/rules/ta_r4_*.smk`, `config/ta_r4`, `Snakefile.ta_r4`, `bin/r4_fire.sh`, `src/legacy/region_analysis/scripts/run_susie_rss.R`, `src/snakemake/scripts/plink_ld_to_rds.R`, `src/snakemake/scripts/run_qtl_coloc.R`, `src/snakemake/scripts/ld_allele_join.R`, `src/python/assign_tiers.py`, `src/python/aggregate_qtl_coloc.py`, `src/python/harmonize_eqtl.py`, `src/python/harmonize_sqtl.py`, `src/python/ld_read_path.py`, `src/python/ld_panel.py`, `envs`, and the panel manifests `manifests/panels_*.tsv`.

--- PASTE ENDS HERE ---

---

## Post-Paste Reference (do NOT paste this block)

- If posted: URL + OSF timestamp → `.planning/osf_deviations.md` (new dated entry); the timestamp is informational (the gate is the git lock).
- Any change after the lock is a deviation: log it in `.planning/osf_deviations.md` before acting.
- Do not delete this file; a superseding amendment gets a pointer at the top.
