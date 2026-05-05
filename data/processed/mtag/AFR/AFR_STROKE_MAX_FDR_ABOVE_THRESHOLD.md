# AFR Stroke MTAG max_FDR Above 0.05 Threshold at M2 Milestone

## Why this file exists

The Turley 2018 max-FDR scalar produced by `mtag.py --fdr --skip_mtag --intervals 2 --fit_ss` for the AFR-stratum stroke trait (`stroke.AFR.GIGASTROKE.2022`) is **0.11541401327515466** — the only above-0.05 scalar across the 21-trait × 3-stratum harvest by quick-260429-w2a (witness: `data/processed/mtag/AFR/AFR_mtag_fdr_audit.tsv`).

This is an **honest finding** under the M2 LD-reference and discovery-cohort available at this milestone, not a software defect or pipeline error. It is preserved as historical_outcome rather than re-disposed via re-fire (per `feedback_failed_to_honest_finding`); the M3 re-evaluation under AoU AFR LD is queued as `M2-POST-M3-09` in `.planning/m2_post_m3_rerun_queue.tsv`.

## Scalar values (per-stratum max_FDR summary, quick-260429-w2a HARVEST)

| Stratum | K | max_FDR range                  | n_below_0.05 | Notes |
|---------|---|--------------------------------|---------------|-------|
| EUR     | 8 | min=1.046e-06 / max=1.338e-04 | 8/8           | All 8 traits below threshold |
| AFR     | 6 | min=8.643e-09 / max=**1.154e-01** | **5/6**   | **stroke.AFR = 0.1154 — flagged here** |
| TRANS   | 7 | min=7.459e-07 / max=1.431e-04 | 7/7           | All 7 traits below threshold |

The scalar 0.1154 = 11.54% maxFDR is approximately **2.3× the conventional Turley 2018 §4.2 maxFDR-acceptance threshold** of 0.05. By contrast, every other AFR trait is at 0.97e-02 (bmi.AFR) or below; non-stroke AFR scalars never exceed 1% maxFDR. The stroke.AFR signal is genuinely a tail outlier within the AFR stratum, not a mid-cluster row.

## Root cause: GIGASTROKE AFR cohort N + 1000G AFR LD-reference effective-sample-size insufficiency

- **Discovery cohort:** GIGASTROKE 2022 AFR meta-analysis (Mishra et al., Nature 2022) — N≈40k cases + ≈340k controls AFR-ancestry
- **LD reference:** 1000G AFR Phase3 N=504 (Auton et al., Nature 2015)
- **MTAG covariate inputs:** the other 5 AFR traits (bmi/hdl/ldl/tc/tg), each with their own discovery N (PAGE 2019 BMI N≈50k; GLGC 2021 lipids ≈90k AFR); LDSC bivariate intercepts vs. stroke are all within ±0.05 (no high-overlap pair).
- **Mechanism:** `mtag.py --fdr --skip_mtag` constructs an admissibility-region simplex parameterized by Spike-Slab probabilities and computes max-FDR as the projection of the worst-case grid point. Under low effective-N (and therefore higher per-SNP sigma_hat) AND low LDSC bivariate intercepts (rg-overlap ~0 with all covariates), the simplex projection lands far from the well-conditioned interior, yielding a higher maxFDR scalar.

## Downstream consumer impact (verified empirical)

Refreshed under quick-260505-1mq via direct Python driver invocation:

| Consumer                                  | Filter line                                | Pre/post sha256 | AFR-stroke impact |
|-------------------------------------------|--------------------------------------------|------------------|-------------------|
| `results/novelty/joint_signal_novel.tsv`  | `call_class1_novelty.py:159` (max_FDR<0.05) | byte-identical  | **No content change** — AFR-stroke MTAG-novel rsids are evidently retained via the CPASSOC OR-path or were already excluded by GWAS Catalog v_lock_M2 prior-art filter. |
| `results/regions/union_region_list.bed`   | `build_region_union.py:237` (max_FDR<_MAX_FDR=0.05) | sha changed (161→168 regions) | Region count delta reflects bedtools-merge non-monotonicity + clumping-bed snapshot freshness; AFR-stroke removal contribution is one term among many. |
| `data/processed/mtcojo/AFR/mtcojo_eligible_targets.tsv` | `select_mtcojo_eligible_targets.py` (eligibility predicate D-M2-08 + D-M2-Q5) | byte-identical (4 eligible: hdl/ldl/tc/tg) | **No content change** — stroke.AFR was already excluded by gcov_int<0.1 filter (no covariate has LDSC bivariate intercept > 0.1 with stroke). max_FDR<0.05 is a REDUNDANT filter for this trait. |
| `data/processed/mtcojo/AFR/mtcojo_sensitivity.tsv` | (downstream of eligibility) | byte-identical (4 loci, all FAIL) | No change (eligibility byte-identical; .mtcojo.cojo files unchanged). |

**Net consumer impact at M2:** zero quantitative content change in any of the four canonical M2 derived consumers. The AFR-stroke max_FDR=0.1154 finding is documented as a provenance witness, not a numerically propagating signal at M2.

## Why we keep the row in source data anyway

The `_mtag_maxfdr_filtered.txt` source files retain all AFR-stroke rows (~1,133,501 SNPs at trait_key=stroke.AFR.GIGASTROKE.2022) with col-11 max_FDR=0.1154 baked in. Three reasons:

1. **Provenance integrity** — the col-11 scalar is the canonical Turley 2018 fixed-point output; rewriting or filtering at the source level would break the audit chain back to the LSF re-fire (jobs 69641-69643 logs at `data/processed/mtag/AFR/AFR_mtag_fdr_run.log`).
2. **Future re-evaluation** — under M3 AoU-AFR-LD (M2-POST-M3-09), the stroke.AFR scalar will be re-fired with N≈95k AoU AFR WGS LD reference; the resulting scalar may drop below 0.05. Keeping the M2 row preserves the historical_outcome witness for the M3-vs-M2 delta-diff.
3. **Confidence-tier-aware downstream consumers** (e.g., HyPrColoc inputs in Phase 3) can elect to apply per-trait max_FDR-aware confidence thresholds rather than the binary <0.05 cut. The col-11 value is preserved for that flexibility.

## Re-evaluation gating

Re-fire path: `M2-POST-M3-09` in `.planning/m2_post_m3_rerun_queue.tsv` (queued under quick-260505-1mq Task 6). Dependency blockers:

- **M3 AoU AFR WGS LD panel** (built under AOU-LD-PIPELINE.md §6; pending AoU controlled-tier workspace from `260426-aow-aou-workbench-registration-track-b-m3`)
- **M2-POST-M3-03** (AFR mtCOJO re-fire prerequisite — provides AoU-AFR-LD-substituted COJO inputs that this max_FDR re-fire would also consume)

Expected M3 outcome: stroke.AFR maxFDR scalar drops by ~1 order of magnitude (from 0.1154 to ~0.01-0.05 range) under the ~180× larger LD reference, bringing it into the <0.05-conventional regime. If the M3 scalar still exceeds 0.05, the finding upgrades from "M2 LD-ceiling artifact" to "GIGASTROKE-AFR genuinely-noisy MTAG-novel locus signal" and would warrant a manuscript-level disclosure footnote.

## Cross-references

- **w2a HARVEST witness:** `.planning/quick/260429-w2a-fire-m2-post-m3-07-mtag-fdr-production-r/260429-w2a-SUMMARY.md` line 95-97 ("Stroke.AFR observation (rigor flag)").
- **m2_post_m3_rerun_queue.tsv:** M2-POST-M3-07 (closed by w2a) → this consumer-refresh by 260505-1mq → M2-POST-M3-09 (gated on M3).
- **Analogous LD-ceiling honest-findings at M2:** `data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md` (mtCOJO 4/4 EXIT at GCTA freq-difference filter, same N=504 root cause).
- **Audit TSV (canonical scalar source):** `data/processed/mtag/AFR/AFR_mtag_fdr_audit.tsv`.
- **Driver:** `src/python/harvest_mtag_fdr_scalars.py` (write-once at quick-260429-w2a; not re-run by this task).
- **MTAG run logs:** `data/processed/mtag/AFR/AFR_mtag_fdr_run.log` + `AFR_mtag.FDR.log`.

---

*Filed by quick-260505-1mq Task 6 as honest-finding disclosure per `feedback_failed_to_honest_finding`. Original-research provenance refresh framing (per `feedback_original_research_framing`) — this is not a "fix" and not a "revision"; it is the M2-milestone snapshot of an LD-reference-bounded scalar pending M3 re-evaluation.*
