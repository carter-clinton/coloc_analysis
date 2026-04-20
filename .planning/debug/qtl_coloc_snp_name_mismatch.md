---
status: resolved
resolved_at: 2026-04-20T15:06:10Z
trigger: "qtl_coloc_snp_name_mismatch — run_qtl_coloc.R returns status=too_few_snps / n_snps_overlap=0 / message='Cannot extract SNP names from GWAS fit' for FTO/Adipose_Subcutaneous/bmi.EUR.FTO_16q12 eQTL smoke despite 2601 harmonized variants and existing .fit.rds. Spawned from parent debug .planning/debug/t1_phase2_first_production.md (awaiting_human_verify). Last-mile blocker for T1 Phase 2 first-production / CP#1-final."
created: 2026-04-20
updated: 2026-04-20
---

## Current Focus

hypothesis: ROOT CAUSE CONFIRMED. Hypothesis (a) — SuSiE fit was built without named variants — but with a specific mechanism: in run_susie_rss.R the `annotate_susie` call FAILED at `.susie_setld` because the LD matrix `R` passed in was an unnamed identity matrix. The region `FTO_16q12` had `use_identity=TRUE` + `variants_exceed_threshold` status in its LD .rds file, so the main loop fell back to `R <- diag(nrow(subset))` (no dimnames). `coloc:::annotate_susie` then internally called `coloc:::.susie_setld(res$sets$cs, LD)` which indexes `ld[stmp[[i]], stmp[[j]]]` by name → errored with `"no 'dimnames' attribute for array"` → `tryCatch` kept the un-annotated fit → saveRDS wrote fit with NULL names.
test: Grepped logs/lsf/*.run_finemap.err — found exact message: `"No LD matrix found for FTO_16q12 (EUR). Falling back to identity."` followed by `"annotate_susie failed (no 'dimnames' attribute for array); saving un-annotated fit."` in both job 727218 and 733010 stderr. Inspected LD .rds file: `R=NULL, use_identity=TRUE, status="variants_exceed_threshold"`.
expecting: Fix at run_susie_rss.R annotate_susie call site — name the identity R matrix before passing to annotate_susie. The variant_id format issue (c) is ALSO real (see BUG-2 below) but becomes moot because we control the naming convention at the Phase 1 annotate_susie site. We can choose a variant_id scheme that matches the harmonized TSV (`chr16_53766288_C_T`) instead of the current `16:53766288` scheme.
next_action: (1) Add the naming-identity fix to run_susie_rss.R, (2) rebuild ONLY the single `bmi.EUR.FTO_16q12.fit.rds` to avoid polluting other regions, (3) re-fire the eQTL smoke verification command.

## Symptoms

expected: `run_qtl_coloc.R` with eQTL smoke inputs (harmonized TSV with 2601 variants + .fit.rds + LD .rds + manifest row) produces JSON with status="ok" (success) and numeric PP.H4.abf.
actual: JSON produced. status="too_few_snps". message="Cannot extract SNP names from GWAS fit". n_snps_overlap=0.
errors: No exception. Graceful fallback at run_qtl_coloc.R:131-134 — `if (is.null(gwas_snps)) write_status_json("too_few_snps", "Cannot extract SNP names from GWAS fit")`. Upstream extraction at L124-129: tries `colnames(gwas_fit$alpha)` first, falls back to `names(gwas_fit$pip)`. Both returning NULL means the fit has neither column names on alpha nor names on pip.
reproduction: cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --cores 2 --use-conda --rerun-triggers=mtime results/qtl_coloc/FTO_16q12_ENSG00000140718_gtex_eqtl_Adipose_Subcutaneous.json
started: Phase 2 has never completed end-to-end before 2026-04-20 eQTL smoke. This is the FIRST run of run_qtl_coloc.R on real data. No prior baseline exists.

## Eliminated

- hypothesis: (b) coloc.susie version attribute mismatch / API drift.
  evidence: `coloc::packageVersion() == 5.2.3`; `coloc:::annotate_susie` body is clean 6-line implementation that sets `names(res$pip) = snp`, `colnames(res$alpha) = c(snp, "null")`, `colnames(res$lbf_variable) = c(snp, "null")`. `run_qtl_coloc.R` checks BOTH `colnames(gwas_fit$alpha)` AND `names(gwas_fit$pip)` — either would work. Issue is not the extraction logic; the fit truly has no names.
  timestamp: 2026-04-20

## Evidence

- timestamp: 2026-04-20
  checked: `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.snakemake/conda/c076b33c5dbe13cadce27be08e3ec22a_/bin/Rscript` on bmi.EUR.FTO_16q12.fit.rds
  found: class=susie; top-level names = alpha/mu/mu2/KL/lbf/lbf_variable/sigma2/V/pi/null_index/XtXr/converged/elbo/niter/X_column_scale_factors/intercept/sets/pip. `names(f$pip) == NULL`. `colnames(f$alpha) == NULL`. `colnames(f$lbf_variable) == NULL`. `dim(f$alpha) == 10 x 701`. `length(f$pip) == 701`. `f$sets$cs` = list of 7 items named L1..L7 — each item is bare integer INDEX (e.g., `L1: int 25`), NOT a named integer (`L1: int 25 ; names(L1)[1] = "16:53813367"`).
  implication: Fit is truly un-annotated. Neither naming path succeeded at save-time. No attribute-location ambiguity.

- timestamp: 2026-04-20
  checked: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/logs/lsf/727218.run_finemap.err + logs/lsf/733010.run_finemap.err (both Phase 1 jobs that wrote bmi.EUR.FTO_16q12.fit.rds)
  found: Both logs contain: (i) `No LD matrix found for FTO_16q12 (EUR). Falling back to identity.` (ii) `annotate_susie failed (no 'dimnames' attribute for array); saving un-annotated fit.`
  implication: run_susie_rss.R line 436 fallback fired → `R <- diag(nrow(subset))` produced unnamed identity. Line 530-535 tryCatch swallowed the `.susie_setld` error → fit saved un-annotated. This is the PROXIMATE root cause.

- timestamp: 2026-04-20
  checked: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/data/processed/ld_reference/EUR/FTO_16q12.rds (via Rscript readRDS + inspect)
  found: List with components: `R=NULL`, `variants=data.frame(15316 rows, cols CHR/POS/REF/ALT/SNP_ID)`, `use_identity=TRUE`, `status="variants_exceed_threshold"`.
  implication: The LD reference pipeline flagged this region as too-large (15316 variants) and explicitly stored a sentinel "use identity matrix" record. load_ld_matrix (run_susie_rss.R L143-145) correctly identified this and returned R=NULL with status passed through. The identity-fallback at L436 is EXPECTED behavior for variant-exceeding regions.

- timestamp: 2026-04-20
  checked: `coloc:::annotate_susie` + `coloc:::.susie_setld` function bodies (coloc v5.2.3)
  found: `annotate_susie(res, snp, LD)` at last line calls `res$sld = .susie_setld(res$sets$cs, LD)`. `.susie_setld` indexes `ld[stmp[[i]], stmp[[j]]]^2` where `stmp = lapply(s, names)` — uses credible-set variant NAMES as indices into LD matrix. If LD has no dimnames → `"no 'dimnames' attribute for array"` error.
  implication: Fix must either (a) give the identity R matrix dimnames before passing to annotate_susie, or (b) skip `.susie_setld` when LD is identity (but that would require refactoring annotate_susie or calling it in a way that omits sld). Option (a) is strictly smaller-surface — one line of `dimnames(R) <- list(snp_names, snp_names)` before the annotate_susie call.

- timestamp: 2026-04-20 (harmonized TSV format cross-check — hypothesis (c) relevance)
  checked: `zcat FTO_16q12.harmonized.tsv.gz | head`
  found: variant_id column format: `chr16_53766288_C_T`. Columns: variant_id, beta, se, maf, position, N, sdY, gene_id, tissue, pvalue, rsid, chromosome. `rsid` column is populated (e.g., `rs9940278`).
  implication: The harmonized TSV's variant_id is `chr16_POS_REF_ALT`. The current annotate_susie call in run_susie_rss.R (L522-528) uses EITHER `subset$SNP_ID` (which from LD file's variants dataframe would be rsids like `rs75823063` or coords like `16:53800200`) OR fallback `sprintf("%s:%s", subset$CHR, subset$POS)` = `16:53766288`. NEITHER matches QTL variant_id format. So EVEN IF annotate_susie succeeds, the `intersect(gwas_snps, qtl_snps)` at run_qtl_coloc.R:137 would still produce 0 overlap unless names are standardized to a common format. Both sides must agree on a scheme.

- timestamp: 2026-04-20 (Phase 1 sumstats variant_id format — determining the canonical scheme)
  checked: will sample bmi.EUR.tsv.bgz to determine the native Phase 1 variant_id format.

- timestamp: 2026-04-20 (harmonize_eqtl.py variant_id construction)
  checked: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/harmonize_eqtl.py L134: `out["variant_id"] = df[variant_col].values` (verbatim GTEx column). qtl_sources.yaml declares `gtex_eqtl.variant_id_format = "chr{chrom}_{pos}_{ref}_{alt}"`. Raw GTEx header: first column is `variant` with values like `chr1_13550_G_A`. Harmonized TSV has `rsid` column populated for 2599/2601 rows (>=99.9%).
  implication: QTL variant_id is `chr{chrom}_{pos}_{ref}_{alt}` GRCh38. Rsid is available as a parallel column. Rsid is the cleanest cross-build common key.

- timestamp: 2026-04-20 (Phase 1 sumstats)
  checked: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz header
  found: Columns `CHR POS BETA SE P N SNP_ID TRAIT ANCESTRY BUILD`. `BUILD=GRCh37`. In FTO_16q12 region (CHR=16, POS 53800000-54400000 in GRCh37): 701 rows, all 701 have rsid in SNP_ID column.
  implication: Phase 1 side operates on GRCh37 coordinates with full rsid coverage. run_susie_rss.R L522-528 uses SNP_ID as snp_names (fallback CHR:POS). So when annotate_susie succeeds, fit has rsid names (confirmed by inspection of bmi.EUR.MC4R_18q21.fit.rds: `colnames(f$alpha) = rs8089678, rs12605506, ...`). Rsid IS the shared identifier between Phase 1 and Phase 2 — works across genome builds.

- timestamp: 2026-04-20 (LD rds structure universal survey)
  checked: All 12 files under data/processed/ld_reference/EUR/*.rds via Rscript loop.
  found: ALL 12 files have `R=NULL, use_identity=TRUE, status="variants_exceed_threshold"`. Every file has a `variants` dataframe (15316 rows for FTO) with CHR/POS/REF/ALT/SNP_ID columns, GRCh37 coordinates.
  implication: The identity-fallback path in run_susie_rss.R fires for EVERY region. This means the annotate_susie bug is universal — not unique to FTO.

- timestamp: 2026-04-20 (Phase 1 unnamed fit survey)
  checked: loop over all 40 .fit.rds files in results/fine_mapping/susie/ — inspected `colnames(fit$alpha)` and `names(fit$pip)`.
  found: 10 fits are UNNAMED: asthma.EUR.FTO_16q12, bmi.EUR.APOE_19q13, bmi.EUR.BMI_5q13_3, bmi.EUR.FTO_16q12, hypertension.EUR.APOE_19q13, hypertension.EUR.SH2B3_12q24, stroke.EUR.9p21_CDKN2A, stroke.EUR.SH2B3_12q24, t2d.AFR.FTO_16q12, t2d.EUR.FTO_16q12. The rest ARE named.
  implication: annotate_susie fails specifically when (i) LD is identity (no dimnames) AND (ii) ≥1 credible set exists (so `.susie_setld` actually tries to index LD by CS names). Regions with 0 CS escape because `.susie_setld` short-circuits at `if (!length(stmp)) return(0)`. Explains why MC4R_18q21 has names (0 CS) but FTO_16q12 doesn't (7 CS).

- timestamp: 2026-04-20 (variant-ID format cross-check)
  checked: Phase 1 coord build vs Phase 2 coord build.
  found: Phase 1 sumstats are GRCh37. Regions_curated.csv `start/end` columns are GRCh37. LD reference variants dataframe has GRCh37 positions (rs9939609 at 53820527 = GRCh37 pos). Harmonized QTL TSV uses GRCh38 positions (`chr16_53766288_C_T`; rs9939609 at GRCh38 = 53786615). Cross-build position mismatch: CANNOT naively compare POS across them. BUT rsid is build-invariant → rsid is the correct match key.
  implication: A rsid-based match strategy in run_qtl_coloc.R is the robust fix. Pos-based match would require build harmonization, which is a much bigger refactor (all downstream already assumes GRCh38 for Phase 2 paths but GRCh37 for Phase 1 data).

## Fix Design (two-sided, minimum invasive)

### Fix 1: run_susie_rss.R — ensure annotate_susie always succeeds
- **Location:** src/legacy/region_analysis/scripts/run_susie_rss.R, immediately before line 531 `coloc:::annotate_susie(fit, snp_names, R)`.
- **Change:** Add `dimnames(R) <- list(snp_names, snp_names)` when R is unnamed. This allows `.susie_setld` to index `ld[stmp[[i]], stmp[[j]]]` even with identity R.
- **Surface area:** 3 lines. No behavioral change for non-identity LD (which already had names). No change to downstream coloc.susie semantics (sld matrix content is symbolic per-CS anyway).
- **Scope:** Affects all 10 unnamed fits universally. But we only need the FTO fit for this smoke; other fits can be regenerated lazily or in a follow-up.

### Fix 2: run_qtl_coloc.R — use rsid matching + handle LD list structure
- **Location:** src/snakemake/scripts/run_qtl_coloc.R, lines 136-141 (SNP matching) and 153-158 (LD loading).
- **Change A (SNP matching):** Change `qtl_snps <- qtl_df$variant_id` → `qtl_snps <- qtl_df$rsid`. GWAS fit names are rsids (post Fix 1); QTL rsid column is populated 99.9%. Rsid is build-invariant.
- **Change B (LD loading):** Read .rds; if it's a list with `use_identity=TRUE` OR R=NULL, build a named identity matrix dimnames=overlap_snps. If it's a list with `R` populated, use obj$R. If it's a bare matrix, use directly. Preserve existing check for `rownames(ld_full) %||% colnames(ld_full)`.
- **Surface area:** ~20 lines. No change to coloc.susie call semantics. Regression-safe for non-list LD inputs (not currently used in T1 but future-proofed).

### Fix 3: rebuild the single affected fit
- **Location:** invoke Phase 1 on ONLY `bmi.EUR.FTO_16q12.fit.rds`.
- **Command:** `snakemake --cores 2 --use-conda --force results/fine_mapping/susie/bmi.EUR.FTO_16q12.fit.rds` (or equivalent; delete old fit first to force).
- **Surface:** Regenerates 1 file. Preserves all other fits.
- **Side-effect:** Other 9 unnamed fits remain broken until regenerated — but per scope constraint "do NOT re-run all of Phase 1", this is acceptable; out-of-scope for this debug.

### Fix order
Apply Fix 1 (Phase 1 source) → Fix 3 (rebuild fit) → Fix 2 (Phase 2 source) → verify. Order matters because verification command triggers Phase 2 rule which reads fit produced by Fix 3.

## Resolution

root_cause: TWO compounding defects:
  (1) run_susie_rss.R L531 called `coloc:::annotate_susie(fit, snp_names, R)` where R was an unnamed identity matrix built via `diag(nrow(subset))` whenever the LD reference pipeline had flagged the region as "variants_exceed_threshold" (a universal state for all 12 EUR regions in this project because their variant counts all exceed LD_MAX_VARIANTS=6000). `annotate_susie` internally calls `.susie_setld(res$sets$cs, LD)` which indexes LD by credible-set NAMES — which errors on unnamed LD with "no 'dimnames' attribute for array". The `tryCatch` at L530 swallowed this error and saved the un-annotated fit, producing a .fit.rds with NULL `names($pip)` and NULL `colnames($alpha)`. Observable in 10/40 fits — the ones with at least one credible set (fits with 0 CS escaped because `.susie_setld` short-circuits on empty input).
  (2) run_qtl_coloc.R assumed (a) GWAS fit variants and QTL variant_ids share a naming convention, and (b) the LD .rds at `data/processed/ld_reference/EUR/*.rds` is a bare matrix with dimnames. Neither assumption holds. GWAS fits encode variants by rsid (GRCh37-derived from sumstats SNP_ID column); harmonized QTL TSVs encode variants as `chr{chrom}_{pos}_{ref}_{alt}` (GRCh38). The LD .rds is a LIST with components `{R, variants, use_identity, status}`; for variant-exceeding regions `R=NULL, use_identity=TRUE`. Even after fix (1), run_qtl_coloc.R would fail at `ld_full <- readRDS(opt$ld_matrix); rownames(ld_full)` because `rownames(list)` is NULL.

fix: Two-file minimal change:

1. `src/legacy/region_analysis/scripts/run_susie_rss.R` — added `if (is.null(dimnames(R)) && nrow(R) == length(snp_names)) dimnames(R) <- list(snp_names, snp_names)` immediately before the annotate_susie call (L529-540 range). Guards with length check to preserve correct behavior for any future LD inputs that ARE already named. No behavioral change for previously-working fits. Fixes annotate_susie for all future Phase 1 runs.

2. `src/snakemake/scripts/run_qtl_coloc.R` — restructured Section 3 (SNP matching) and Section 4 (LD load/subset), L120-189:
   - Drop sentinel `"null"` column that coloc::annotate_susie appends to alpha when the fit has fewer CS than L (keeps overlap honest).
   - Match via `qtl_df$rsid` when the rsid column is populated (build-invariant); fall back to `qtl_df$variant_id` otherwise. Log the match_key used.
   - Handle LD .rds as (a) list with R matrix + variants (use obj$R, derive rownames from obj$variants$SNP_ID if missing), (b) list with use_identity=TRUE or R=NULL (construct named identity matrix over overlap_snps), (c) bare matrix (legacy/future, require dimnames).
   - Drop path that assumed LD variant NAMES must intersect overlap when LD is identity (the identity is built TO overlap_snps, so intersection is trivial by construction).
   - Use `overlap_snps` (not `qtl_df$variant_id`) as the `snp` field of the coloc dataset list, keeping the rsid convention consistent end-to-end.

3. Regenerated `results/fine_mapping/susie/bmi.EUR.FTO_16q12.fit.rds` — single-file rebuild via Phase 1 rule. The other 9 unnamed fits (`asthma.EUR.FTO_16q12`, `bmi.EUR.APOE_19q13`, `bmi.EUR.BMI_5q13_3`, `hypertension.EUR.APOE_19q13`, `hypertension.EUR.SH2B3_12q24`, `stroke.EUR.9p21_CDKN2A`, `stroke.EUR.SH2B3_12q24`, `t2d.AFR.FTO_16q12`, `t2d.EUR.FTO_16q12`) are left un-regenerated per scope constraint ("do NOT re-run all of Phase 1"); they will need to be regenerated in a separate task before Phase 2 can fire on those regions/traits. This is a KNOWN-INCOMPLETE condition captured in the followup section below.

verification: Ran the exact parent-specified verification command:
  `snakemake --cores 2 --use-conda --rerun-triggers=mtime results/qtl_coloc/FTO_16q12_ENSG00000140718_gtex_eqtl_Adipose_Subcutaneous.json`
Outcome:
  - Exit 0 ✓
  - JSON file produced at expected path ✓
  - status = "no_qtl_cs" (NOT "too_few_snps"). The parent's stated "success sentinel" candidate `ok` does not exist in the script; real sentinels are `success`, `no_qtl_cs`, `no_gwas_cs`, `too_few_snps`, `qtl_dataset_invalid`, `qtl_susie_failed`. `no_qtl_cs` is a valid biological outcome (QTL signal has no credible set on this tissue).
  - n_snps_overlap = 698 (expected positive integer on the hundreds-to-thousands order ✓)
  - n_cs_gwas = 7 (GWAS fit has 7 credible sets — the same 7 observed in bmi.EUR.FTO_16q12.json) ✓
  - n_cs_qtl = 0 (QTL min p-value = 1.24e-06 in Adipose_Subcutaneous; zero variants reach genome-wide significance; SuSiE correctly finds no credible set). This is the biological truth for FTO eQTL in Adipose_Subcutaneous — FTO's strong eQTLs are in brain tissues. Not a pipeline bug.

Evidence the SNP-name-mismatch bug itself is fully resolved:
  BEFORE: `status=too_few_snps, n_snps_overlap=0, message="Cannot extract SNP names from GWAS fit"` → pipeline never reached coloc.
  AFTER:  `status=no_qtl_cs, n_snps_overlap=698, n_cs_gwas=7, n_cs_qtl=0` → pipeline ran end-to-end: GWAS fit had 7 named credible sets, 698 variants overlapped via rsid, LD identity handled, coloc::check_dataset passed, coloc::runsusie converged, coloc.susie reported no QTL CS.

The parent's verification criterion "PP.H4.abf returns a NUMERIC value in [0,1]" was NOT met by the specific row tested (FTO in Adipose_Subcutaneous) because n_cs_qtl=0, but this is a data-signal outcome, not a pipeline failure. To fully exercise PP.H4 production would require testing a (tissue, trait, region) combination where both sides have strong fine-mapped signals — this is a biological selection, not a fix verification. Within the scope constraint ("If PASS on FTO, do NOT launch the other 538 gtex_eqtl rows"), this single-row verification is the scoped maximum.

files_changed:
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/legacy/region_analysis/scripts/run_susie_rss.R (+12 lines: dimnames guard before annotate_susie)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/scripts/run_qtl_coloc.R (+74/-25 lines: rsid matching, LD list handling, identity fallback)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/results/fine_mapping/susie/bmi.EUR.FTO_16q12.fit.rds (regenerated via Phase 1 rule; now 106KB, has named pip/alpha)
  - /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/results/fine_mapping/susie/bmi.EUR.FTO_16q12.json (regenerated alongside fit; updated elbo / variant set same as prior run within numerical tolerance)

known_incomplete:
  - (RESOLVED) The 9 other Phase 1 fits were regenerated after checkpoint approval on 2026-04-20 15:01-15:05 UTC via a single targeted `snakemake --cores 4 --use-conda results/fine_mapping/susie/{9 fits}.fit.rds` invocation (no `--forceall`; upstream deps were already up-to-date, so only 14 steps total fired, of which 9 were run_finemap). All 9 now have `names(pip)` non-NULL, `colnames(alpha)` non-NULL, and named credible sets — verified via Rscript loop. List: asthma.EUR.FTO_16q12 (8 CS), bmi.EUR.APOE_19q13 (4 CS), bmi.EUR.BMI_5q13_3 (6 CS), hypertension.EUR.APOE_19q13 (5 CS), hypertension.EUR.SH2B3_12q24 (10 CS), stroke.EUR.9p21_CDKN2A (5 CS), stroke.EUR.SH2B3_12q24 (8 CS), t2d.AFR.FTO_16q12 (4 CS), t2d.EUR.FTO_16q12 (2 CS). This was IN SCOPE per orchestrator/Carter directive (9 targeted fits != all of Phase 1's 40 fits). Prevents `too_few_snps` from recurring across the 225+ manifest rows that reference these fits in future Phase 2 smokes.
  - Post-regeneration regression check: re-ran `snakemake --cores 2 --use-conda --rerun-triggers=mtime results/qtl_coloc/FTO_16q12_ENSG00000140718_gtex_eqtl_Adipose_Subcutaneous.json` — JSON identical to prior good run (status=no_qtl_cs, n_snps_overlap=698, n_cs_gwas=7, n_cs_qtl=0). No regression from regenerations or Phase 1 source-level fix.
  - The r_coloc env print NULL at startup — a harmless side effect of the `%||%` return when opt$gwas_fit lacks some attribute path; does not affect correctness.
  - sQTL/sc-eQTL/pQTL smokes remain blocked on their own pre-existing issues (raw data missing; pQTL further blocked on Synapse token), as documented in the parent session. This fix unblocks eQTL end-to-end, not the others.
