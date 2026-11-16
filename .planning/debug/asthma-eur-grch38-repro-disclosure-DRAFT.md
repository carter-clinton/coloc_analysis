# DRAFT disclosure — asthma.EUR inputs behind the reproduction arms (not posted; OSF DRAFT body not edited)

Decision A (Carter 2026-11-16): the four reproduction arms keep their original inputs; corrected inputs feed the production arms only. Source: `.planning/debug/asthma-eur-grch38-mislabel.md`.

Proposed text:

> The GBMI 2021 asthma EUR summary statistics used by the earlier analysis (sha256 `22b2807551ca6a5967fa67ba81c7546cc66a7f3b9d0055cd23ddd8d2b3eda137`) carry GRCh38 coordinates although they were labelled GRCh37; only the AFR file had been lifted. Position checks at 658 GRCh37/GRCh38 anchor variants place 657 of 657 informative anchors on GRCh38 (all other inputs: GRCh37). Every earlier asthma EUR fit therefore read a region window shifted by the GRCh37→GRCh38 offset (panel-matched fraction 0.003–0.038 at MC4R, APOL1 and SH2B3, against 0.18–0.34 on corrected data), and the earlier variant catalogs carry these GRCh38 positions. The reproduction results in (h) reproduce the earlier computation on its original inputs, including these mislocated asthma EUR inputs; they are a check of computational reproducibility, not of the earlier asthma EUR findings. On corrected (lifted, strand-checked) asthma EUR data, the SH2B3_12q24, MC4R_18q21 and APOL1_22q12 asthma EUR fits have 0 purity-filtered credible sets. The SH2B3 PP.H4 = 1.0 pairs (BMI–hypertension, hypertension–stroke, hypertension–type 2 diabetes) do not involve asthma. Production analyses use asthma EUR and AFR files lifted to GRCh37 with strand correction (sha256 `49edfc54…` EUR, `8828df14…` AFR; full values in `sumstats_r4_sha256.tsv`) and variant catalogs rebuilt from them.

Open items for whoever edits the OSF DRAFT (not done here):
- (c) still pins asthma EUR `22b28075…` and asthma AFR `c9a723f3…`; the production route now reads the strand-corrected lifts.
- The earlier pinned asthma AFR file also lacked all chrX rows (the AFR lift wrote `chr23` into the BED); every trait is `no_variants` at BMI_Xq24, so no fit changes.
- Legacy-route non-asthma reproduction fits (hypertension, stroke, type 2 diabetes) are JSON-identical on old vs corrected catalogs; BMI legacy fits are not run-to-run reproducible on identical inputs (investigated separately), so the catalog effect on BMI is not shown.
