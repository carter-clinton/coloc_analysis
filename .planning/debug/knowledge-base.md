# GSD Debug Knowledge Base

Resolved debug sessions. Used by `gsd-debugger` to surface known-pattern hypotheses at the start of new investigations.

---

## qtl_coloc_snp_name_mismatch — Phase 2 coloc reports too_few_snps / n_snps_overlap=0 despite harmonized variants
- **Date:** 2026-04-20
- **Error patterns:** too_few_snps, Cannot extract SNP names from GWAS fit, n_snps_overlap=0, annotate_susie, no 'dimnames' attribute for array, variants_exceed_threshold, identity LD, fit.rds pip NULL, alpha colnames NULL
- **Root cause:** TWO compounding defects. (1) run_susie_rss.R called coloc:::annotate_susie with an unnamed identity LD matrix built via diag(nrow(subset)) when the LD reference was flagged variants_exceed_threshold (universal in T1 EUR). annotate_susie internally calls .susie_setld which indexes LD by credible-set names — this errored on unnamed LD and the surrounding tryCatch silently returned the un-annotated fit. 10 of 40 fits affected (only those with >=1 credible set). (2) run_qtl_coloc.R assumed GWAS and QTL share a variant naming convention (they don't — rsid vs chr_pos_ref_alt across builds) and that the LD .rds is a bare matrix (it's a list with {R, variants, use_identity, status}).
- **Fix:** (a) In run_susie_rss.R, attach snp_names as dimnames(R) before annotate_susie when R is unnamed. (b) In run_qtl_coloc.R, match via qtl_df$rsid (build-invariant) and handle LD .rds as list with R populated / use_identity / bare matrix. Regenerate the 10 affected Phase 1 fits via targeted `snakemake --cores N` on the specific .fit.rds targets.
- **Files changed:** src/legacy/region_analysis/scripts/run_susie_rss.R, src/snakemake/scripts/run_qtl_coloc.R
---

