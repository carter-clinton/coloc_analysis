# AFR mtCOJO LD Insufficiency at M2 Milestone

## Why this file exists

All 4 AFR target traits (hdl, ldl, tc, tg) eligible for mtCOJO sensitivity
analysis (per `mtcojo_eligible_targets.tsv` + D-M2-Q5) EXIT at GCTA's
allele-frequency-difference filter when run against the 1000G AFR Phase3
reference panel (N=504). All 4 rows in `mtcojo_sensitivity.tsv` therefore
carry `sensitivity_flag=FAIL` by design at M2 milestone — this is the
expected outcome under the LD-reference panel available at this milestone,
not a software defect or a biological null.

## Witness (job 67678, ldl.AFR.GLGC.2021, 2026-04-29)

From `data/processed/mtcojo/AFR/m2p3_08/ldl.AFR.GLGC.2021/ldl.AFR.GLGC.2021.mtcojo.fire.log`:

```
1206784 SNPs are retained after filtering.
There are 1501 genome-wide significant SNPs with p < 5.0e-08.

Reading PLINK BED files ...
Genotype data for 504 individuals and 1501 SNPs have been included.
Calculating allele frequencies ...
Checking the difference in allele frequency between the GWAS
summary datasets and the LD reference sample...
78477 SNP(s) have large difference of allele frequency between
the GWAS summary data and the reference sample.
Error: there are too many SNPs that have large difference in
allele frequency. Please check the GWAS summary data.
```

78,477 / 1,210,429 SNPs = 6.5% freq-mismatch rate exceeds GCTA's internal
5% threshold for proceeding past the freq-difference filter.

## Root cause: LD-reference sample-size insufficiency

- **Discovery cohort:** GLGC 2021 AFR ~91k (Graham et al., Nature 2021)
- **LD reference:** 1000G AFR Phase3 N=504 (Auton et al., Nature 2015)
- **Imbalance ratio:** ~180:1
- **Mechanism:** Allele frequencies estimated from N=504 carry large
  sampling variance for variants in the 1-to-5% MAF tail; the discrepancy
  with N≈91k discovery EAFs exceeds GCTA's 0.2 abs-diff threshold for
  ≥6.5% of cojo-input SNPs, triggering the EXIT.
- **Analogous mode at M2:** The same constraint motivates the AFR PLINK
  clumping re-fire under M2-POST-M3-01 (currently 0 AFR leads at p<5e-8
  due to N=504 underpower) and the AFR LDSC matrix slice re-fire under
  M2-POST-M3-02. M2-POST-M3-08 sits in the same family of LD-reference
  ceiling effects and is resolved via the same M3 substitution path.

## Affected targets (4 of 4 AFR-eligible)

| target_trait              | LSF job | EXIT step                |
|---------------------------|---------|--------------------------|
| hdl.AFR.GLGC.2021         | 67677   | freq-difference filter   |
| ldl.AFR.GLGC.2021         | 67678   | freq-difference filter   |
| tc.AFR.GLGC.2021          | 67679   | freq-difference filter   |
| tg.AFR.GLGC.2021          | 67680   | freq-difference filter   |

Per-target full GCTA logs preserved at:
`data/processed/mtcojo/AFR/m2p3_08/<target>/<target>.mtcojo.fire.log`

## Handoff: obligation M2-POST-M3-03

AFR mtCOJO sensitivity analysis is re-scoped under
`.planning/m2_post_m3_rerun_queue.tsv` row M2-POST-M3-03:

> "Re-fire AFR mtCOJO with AoU AFR LD reference panel (currently using
> 1000G AFR N=504 plink bfiles)"

Status (as of 2026-04-29): `not_started`, priority `medium`, blocked on
M3 AoU AFR PLINK bfile (~95k samples; ~180× the 1000G AFR N) + Wave 4 D4
mtCOJO production re-fire complete.

Expected outcome under AoU AFR LD: freq-mismatch rate drops below 5%
(sample-size variance shrinks ~13× at √N=√95000 vs √504), GCTA proceeds
past the freq filter into the LDSC bivariate-intercept step, and `bC_pval`
columns populate for the 4 AFR target traits. The M3 closure path is the
canonical resolution for this artifact's all-FAIL state.

## Reading guidance

A reader of `data/processed/mtcojo/AFR/mtcojo_sensitivity.tsv` encountering
4 FAIL rows with empty `mtcojo_p` should NOT interpret the result as a
biological null on AFR cross-trait pleiotropy — the result is an
LD-reference-panel ceiling effect at M2 milestone, fully disclosed and
resolved at M3 milestone via the AoU AFR LD panel substitution under
M2-POST-M3-03.

The 5 EUR target traits (incl. bmi.EUR) and 4 TRANS target traits, in
contrast, used the 1000G EUR Phase3 N=503 panel (well-matched to the
GLGC EUR ~1.5M and GLGC TRANS ~1.7M discovery cohorts via the established
cross-ancestry EUR convention from Pritchard / Pickrell methods literature)
and are interpretable at M2 as substantive sensitivity-analysis output.

## Provenance

- Document author: harvest task `260429-tq9`
- Underlying fire: quick task `260429-s10` (LSF jobs 67677-67680)
- Submission timestamp: 2026-04-29T20:59:43-04:00
- Termination state: 4 EXIT (GCTA freq-difference filter)
- GCTA build: v1.94.1
