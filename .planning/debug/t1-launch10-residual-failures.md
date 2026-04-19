---
status: fixed_pending_launch14_validation
trigger: "T1 Launch10 residual failures: 28 failed steps across hess_combine, ldsc_seg_gene_expr, ldsc_seg_chromatin, ldsc_partitioned_h2 (7 each)"
created: 2026-04-17T14:30:00Z
updated: 2026-04-18T22:05:00Z
commit: ffbabce (REVERTED --invert-anyway in this fix; new commit pending)
---

## Current Focus

hypothesis: RESOLVED. Option 1 implemented via Option B (in-process column drop). NEGCTRL_HLA_IMMUNE filtered from a per-job ephemeral copy of custom_pathway LD scores; canonical files unchanged.
test: COMPLETE. 17/17 tests in test_launch10_regressions.py pass. End-to-end integration on real chr1..22 LD scores: cond(X_filt) drops 1.16e20 → 4.97e3, full rank.
expecting: Launch14 produces .results files for all 8 trait × ancestry combinations.
next_action: Carter to commit + fire Launch14. Status moves to `resolved` after Launch14 confirms end-to-end success.

## Symptoms

expected: All 4 rule types complete in Launch10 after 385cadf + d33e1f6 landed
actual: 7 failed instances per rule class = 28 residual failures + 1 ldsc_munge + 1 summarize_coloc_results
errors: See .err file excerpts in Evidence below
reproduction: N/A — evidence in active logs
started: Launch10 11:34; errors cluster at 11:32-11:33 (LDSC) and 13:02-14:10 (hess_combine)

## Eliminated

- hypothesis: LDSC errors are live / current
  evidence: All 22 LDSC rule errors happened 11:32-11:33 (first 2 minutes of Launch10). File sumstats.py was patched at 13:01 and pathway.smk at 13:25 (d33e1f6). The errors are pre-fix, but Snakemake does not retry failed jobs in same run — they stay in the failure count but the bugs themselves are already fixed in-code.
  timestamp: 2026-04-17T14:50

- hypothesis: hess_combine is failing for the same reason as 385cadf was meant to fix (the out_prefix double-chr)
  evidence: 385cadf fixed FUTURE hess_local_rhog runs only. Commit message explicitly warns: "Launch10's existing outputs have the double-chr naming and will need a rename pass before hess_combine can succeed." So the fix doesn't apply to existing Launch10 HESS step1 outputs.
  timestamp: 2026-04-17T14:55

- hypothesis: Launch12 hess_combine still failing because dispatch args (--pheno-cor/--num-shared/--local-hsqg-est) are not reaching hess.py
  evidence: 030130b commit + Launch12 stderr (logs/lsf/741109.hess_combine.err line 18) shows hess.py invoked with all four flags: `--prefix results/pathway/hess/t2d_hypertension_EUR --out results/pathway/hess/t2d_hypertension_EUR_combined --pheno-cor 0.0 --num-shared 0 --local-hsqg-est <trait1.local.tsv> <trait2.local.tsv>`. HESS reaches "Loaded results for 1703 loci from step 1" → dispatch is correct, file resolution is correct, failure is downstream at the rank-deficiency check (estimation.py:504-508).
  timestamp: 2026-04-18T12:30Z

- hypothesis: Launch12 ldsc_partitioned_h2 AFR failures are due to AFR frq files missing or unreachable
  evidence: 0a2ad0f commit + Launch12 stderr (logs/lsf/741121.ldsc_partitioned_h2.err line 18) shows `--frqfile-chr data/reference/ldsc/1000G_Phase3_frq_AFR/1000G.AFR.QC.` reaching ldsc.py. data/reference/ldsc/1000G_Phase3_frq_AFR/ contains all 22 .frq files (26 MB each, generated 2026-04-18 03:49–04:06). LDSC progresses to "Read reference panel LD Scores for 1190321 SNPs", "After merging with regression SNP LD, 1186975 SNPs remain" → frqfile resolution is correct, failure is downstream at `check_ld_condition_number` (sumstats.py:312-338).
  timestamp: 2026-04-18T12:35Z

- hypothesis: Launch12 ldsc_partitioned_h2 condition-number error is AFR-specific (caused by AFR frq + EUR LD scores mismatch)
  evidence: hypertension_EUR_pathway_h2.log (2026-04-18 02:05:59) ALSO fails with `condition number is 291568205851310292992` using EUR frq + EUR LD scores. NO `*_pathway_h2.results` files exist for ANY trait/ancestry combination. Condition number is intrinsic to baselineLD (97 cols) + custom_pathway joint annotation matrix — same numerical issue regardless of ancestry. Per LDSC FAQ: "if the number of categories is very large" → condition number > 1e5. Standard remedy = --invert-anyway flag.
  timestamp: 2026-04-18T12:40Z

- hypothesis: ldsc_seg_gene_expr / ldsc_seg_chromatin Launch12 failures need a fix
  evidence: All 5 ldsc_seg .err files referenced in objective (741120, 741122, 741124, 741125, 741127) end with `Finished job 0. 1 of 1 steps (100%) done` and produced `*_cell_type_results.txt` files (4 chromatin .txt files at 48-49 KB, 4 gene_expr .txt files at 18-19 KB). The mtimes on the .err files (Apr 18 06:27–11:23) match the runtimes (~30-90 min). The `.err` size of ~1.9 KB is misleading — LDSC-SEG writes informational lines to stderr, not actual errors. These jobs SUCCEEDED. Whoever cataloged the failures conflated "non-zero stderr file size" with "failure".
  timestamp: 2026-04-18T12:45Z

- hypothesis: --invert-anyway is the canonical fix for the LDSC partitioned_h2 condition-number error (Bug 5 in the 2026-04-18T13:00Z post-mortem; commit ffbabce)
  evidence: RETRACTED. The flag DOES reach ldsc.py and IS honored — `asthma_EUR_pathway_h2.log` line 100 (run 2026-04-18 19:59:47, after ffbabce shipped) shows `WARNING: LD Score matrix condition number is 116151824161276379136. Inverting anyway because the --invert-anyway flag is set.` But four lines later, `np.linalg.solve(xtx, xty)` at jackknife.py:376 raises `LinAlgError: Singular matrix`. The LDSC FAQ silently assumes that a high condition number reflects borderline numerical conditioning (cond ~ 1e5–1e8) where forced inversion still recovers a meaningful solution. At cond = 1.16e20 the matrix is rank-deficient by O(1) eigenvalues — the determinant is essentially zero, smallest singular value is below machine epsilon × largest. No inversion strategy can recover information that is structurally absent from the design matrix. The previous diagnosis applied a syntactically valid LDSC flag without checking whether the FAQ's assumed regime applied.
  timestamp: 2026-04-18T20:30Z

## Evidence

- timestamp: 2026-04-17T14:35
  checked: logs/lsf/737672.hess_combine.err
  found: CalledProcessError from subprocess; hess.py exits 1. Stderr captured but not re-emitted.
  implication: Need to check hess.py's own log file for diagnostic.

- timestamp: 2026-04-17T14:37
  checked: results/pathway/hess/bmi_stroke_EUR_combined.log
  found: "[ERROR] Missing step 1 results for chromosome 1" — hess.py local_hsqg_step2 diagnostic at estimation.py:115. Looks for `{prefix}_chr{N}.info.gz`.
  implication: (a) step dispatch picks local_hsqg_step2 not local_rhog_step2, (b) files don't match name pattern either way.

- timestamp: 2026-04-17T14:40
  checked: results/pathway/hess/ directory, ls | grep chr1
  found: Actual files present: `bmi_stroke_EUR_chr1_chr1.eig.gz`, `bmi_stroke_EUR_chr1_chr1.prjprod.gz`, `bmi_stroke_EUR_chr1_trait1_chr1.info.gz`, `bmi_stroke_EUR_chr1_trait2_chr1.info.gz`, `bmi_stroke_EUR_chr1_trait1_chr1.eig.gz`, `bmi_stroke_EUR_chr1_trait1_chr1.prjsq.gz`, etc. ALL with double-chr and _trait{1,2} rho-HESS naming.
  implication: Files are rho-HESS step1 outputs — the right content — but named with pre-385cadf double-chr pattern. All 220 existing hess_local_rhog outputs have this pattern.

- timestamp: 2026-04-17T14:43
  checked: tools/hess/hess.py main() dispatcher + src/estimation.py step2 readers
  found: Step2 dispatch requires: local_hsqg_step2 if pheno-cor/num-shared/local-hsqg-est ALL None, reads `{prefix}_chr{N}.info.gz` etc. local_rhog_step2 needs all three NOT None, reads `{prefix}_trait1_chr{N}.info.gz`, `{prefix}_trait2_chr{N}.info.gz`, `{prefix}_chr{N}.eig.gz`, `{prefix}_chr{N}.prjprod.gz`.
  implication: run_combine() in src/python/run_hess.py only passes --prefix/--out, so it always dispatches local_hsqg_step2 — WRONG for rho-HESS. Even after renaming, combine would fail looking for info files not produced by local_rhog_step1.

- timestamp: 2026-04-17T14:47
  checked: logs/lsf/734595.ldsc_partitioned_h2.err traceback
  found: `OSError: Could not open data/reference/ldsc/baselineLD..l2.ldscore[./gz/bz2]` at parse.py:156 (`which_compression(fh + suffix)` — the num=None branch). Traceback line 33 shows `ps.ldscore_fromlist(split_paths(args.ref_ld_chr))` — WITHOUT `num=NUM_CHROMOSOMES`.
  implication: At 11:32, tools/ldsc/ldscore/sumstats.py line 165 was missing `num=NUM_CHROMOSOMES` → defaulted to None → ldscore() hit single-file branch → `sub_chr` not called → `fh + suffix` = `baselineLD.` + `.l2.ldscore` = double-dot path.

- timestamp: 2026-04-17T14:50
  checked: stat -c %y tools/ldsc/ldscore/sumstats.py; git show d33e1f6
  found: sumstats.py mtime = 2026-04-17 13:01:50. d33e1f6 commit message documents: "Companion in-place patches to tools/ldsc/ldscore/sumstats.py — lines 165/263: add num=NUM_CHROMOSOMES to ldscore_fromlist for ref_ld_chr and w_ld_chr — line 228: add num=NUM_CHROMOSOMES to M_fromlist — lines 572/582: fix typo n_chr→num for ldsc_seg --h2-cts code path."
  implication: The in-place fix IS applied. The LDSC errors are PRE-FIX (11:32-11:33 before 13:01 sumstats.py patch and 13:25 config fix). These failures won't be retried in the current Launch10; they need Launch11 or a partial rerun.

- timestamp: 2026-04-17T14:52
  checked: logs/lsf/734576.ldsc_munge.err and bmi_EUR_preformatted.tsv.gz contents
  found: Error "No objects to concatenate" at pandas concat in munge_sumstats.py:309. `zcat bmi_EUR_preformatted | awk '{print $2$3}' | uniq -c` → 2,336,225 rows ALL with A1=A, A2=T.
  implication: munge_sumstats_ldsc.py lines 219-220 sets dummy alleles as "A"/"T" when REF/ALT missing — A/T is strand-ambiguous, LDSC filter_alleles drops all. run_hess.py uses "A"/"G" (correct) — this is a specific-to-LDSC bug. bmi_EUR is the only trait lacking alleles in its harmonized sumstats (Yengo 2018 meta-analysis).

- timestamp: 2026-04-17T14:54
  checked: logs/lsf/736837.summarize_coloc_results.err
  found: `ModuleNotFoundError: No module named 'scripts'` at `src/legacy/region_analysis/scripts/summarize_coloc_results.py` line 15 `from scripts.utils_logging import get_logger`.
  implication: Script uses package-relative import but is invoked directly. PYTHONPATH needs to include src/legacy/region_analysis/ OR use explicit relative imports.

- timestamp: 2026-04-17T14:56
  checked: ls results/pathway/hess/*.eig.gz count
  found: 660 total eig files; 220 with `_chr{N}_chr{N}.eig.gz` (direct rho-HESS covariance outputs); 440 with `_chr{N}_trait{1,2}_chr{N}.eig.gz` (trait-specific variants). 10 pairs × 22 chr = 220. ALL pre-385cadf double-chr.
  implication: No post-385cadf hess_local_rhog reruns have happened. Live driver kept existing .done sentinels and didn't re-evaluate step1.

- timestamp: 2026-04-18T20:35Z
  checked: results/pathway/ldsc_partitioned/asthma_EUR_pathway_h2.log lines 100-124 (Launch13 run 19:59:47-20:00:42)
  found: Production LDSC run with --invert-anyway honors the flag — emits `WARNING: LD Score matrix condition number is 116151824161276379136. Inverting anyway because the --invert-anyway flag is set.` Then 4s later raises `numpy.linalg.LinAlgError: Singular matrix` at `np.linalg.solve(xtx, xty)` (jackknife.py:376). The flag bypassed the diagnostic gate but the underlying matrix is genuinely singular.
  implication: The condition-number raise was a SAFETY GATE for a downstream linear solve. Bypassing the gate does not make the matrix solvable. The original ffbabce diagnosis assumed the matrix was numerically ill-conditioned (cond ~ 1e5-1e8 where forced inversion would still recover meaningful estimates). At cond = 1.16e20 the matrix is rank-deficient by O(1) — singular at machine epsilon precision.

- timestamp: 2026-04-18T20:40Z
  checked: SVD of joint annotation matrix on chr22 alone (.planning/debug/svd_rank_check.py)
  found: chr22 joint matrix [97 baseline + 11 custom] = (17489 SNPs × 108 cols). σ_max=8.11e4, σ_min=0 exactly. Numerical rank = 99/108 — deficit of 9. Right singular vectors of the 9 zero-σ directions point cleanly at 9 individual custom_pathway columns where the COLUMN IS IDENTICALLY ZERO ON THIS CHROMOSOME. NaN std on those columns confirms zero-variance. The rank deficit is not collinearity — it is missing data: 9/11 custom_pathway annotations have zero SNPs on chr22.
  implication: The custom_pathway annotation set is sparsely covered. Per-chromosome zero-variance columns are mathematically structural, not numerical noise. But this leads to a more important question: does this hold genome-wide?

- timestamp: 2026-04-18T20:45Z
  checked: Genome-wide stack of all 22 chrs (.planning/debug/svd_genome_check.py)
  found: Genome-wide ref_ld merge produces (1190321 SNPs × 108 cols) with σ_max=1.22e6, σ_min=2.31e2, **cond = 5.25e3 — full rank, well conditioned, BELOW the 1e5 threshold**. None of the 11 custom annotations is genome-wide-zero — every annotation has 1,782-16,136 SNPs. Per-chr distribution: NEGCTRL_HLA_IMMUNE has 16,136 SNPs concentrated on **chr6 only** (1 chr nonzero); NEGCTRL_BLOOD_GROUP=1,782 (3 chrs); NEGCTRL_COSMETIC=2,856 (4 chrs); CUSTOM_*=5,876-9,801 (8-12 chrs each).
  implication: The genome-wide annotation matrix is FULL RANK. The cond=1.16e20 must be created by a SUBSEQUENT data filter inside read_ld_and_sumstats — specifically the merges with HM3 sumstats and the regression-weights file.

- timestamp: 2026-04-18T20:50Z
  checked: Replicated the EXACT LDSC pipeline through to the check_ld_condition_number call for asthma_EUR (.planning/debug/svd_postmerge_check.py): genome-wide ref_ld → check_variance → merge with asthma_EUR sumstats.gz → merge with weights.hm3_noMHC. Produced X_filt of shape (967534, 108) — identical to LDSC's "After merging with regression SNP LD, 967534 SNPs remain" line in the production log.
  found: Reproduced cond = 1.161518e20 (matches production log 1.16e20 to 5 sig figs). σ_min = 8.88e-15. **One column is exactly zero post-merge: `NEGCTRL_HLA_IMMUNEL2`** (std=0.0 on 967,534-row subset). The rank-1 deficient direction (right singular vector at σ[107]) has weight v=+1.00000 on the NEGCTRL_HLA_IMMUNEL2 column and ~0 elsewhere. Secondary collinearity exists between Human_Promoter_Villar_ExAC.flanking.500 / Human_Promoter_Villar_ExAC / CpG_Content_50kb (next two singular values σ[105]≈224, σ[106]≈208) but those are well-conditioned (rel ~ 2e-4) and not the cause of the singular solve.
  implication: ROOT CAUSE LOCATED. The rank-1 deficiency is caused by an INTERACTION between `NEGCTRL_HLA_IMMUNE` (which only has non-zero LD scores in the MHC region of chr6) and `weights.hm3_noMHC.*` (the LDSC regression weights file that is explicitly engineered to EXCLUDE MHC). The inner-join drops every SNP where NEGCTRL_HLA_IMMUNE is non-zero.

- timestamp: 2026-04-18T20:53Z
  checked: Per-chromosome BP coverage of NEGCTRL_HLA_IMMUNE non-zero SNPs in custom_pathway LD scores; BP coverage of weights.hm3_noMHC.6 in the MHC region (chr6:25-34 Mb).
  found:
    - NEGCTRL_HLA_IMMUNE non-zero SNPs: 2,304 SNPs ALL on chr6, BP range **26,033,506–33,965,434** (canonical MHC region).
    - weights.hm3_noMHC.6.l2.ldscore.gz contains 72,386 chr6 SNPs total, BP range 202,452–170,919,470, with **EXACTLY 0 SNPs in the 25–34 Mb MHC interval** — confirms file-by-design MHC exclusion.
    - Inner-join → 0 surviving SNPs where NEGCTRL_HLA_IMMUNE > 0 → column is identically zero on the regression-eligible SNP set → X^T X has a zero eigenvalue → np.linalg.solve raises LinAlgError.
  implication: The bug is not "LDSC-side numerical instability" — it is a deterministic, structural mismatch between an annotation's spatial coverage (HLA = MHC by definition) and the regression weight file's spatial coverage (no-MHC by design). check_variance (sumstats.py:358) does not catch this because it runs on the full ref_ld (1.19M SNPs) BEFORE the weights merge — at that point NEGCTRL_HLA_IMMUNE has variance from the chr6 MHC SNPs. The post-merge re-zeroing is invisible to check_variance.

## Resolution

root_cause:
  hess_combine: TWO bugs compound: (1) existing Launch10 step1 outputs named with pre-385cadf double-chr pattern, (2) run_combine() dispatches hess.py local_hsqg_step2 instead of local_rhog_step2 by passing only --prefix/--out without rho-HESS-specific args (--pheno-cor, --num-shared, --local-hsqg-est).
  ldsc_seg_gene_expr/ldsc_seg_chromatin/ldsc_partitioned_h2: Pre-fix failures. The actual bug (missing `num=NUM_CHROMOSOMES` in sumstats.py + wrong `ldsc_weights` config path) was already fixed by d33e1f6 at 13:25, but the jobs that failed at 11:32-11:33 are not retried in the same Snakemake run. These 7×3=21 failures are "phantoms" — the code works now, just needs Launch11 to re-attempt.
  ldsc_munge (bmi_EUR): Dummy alleles "A"/"T" in munge_sumstats_ldsc.py:219-220 are strand-ambiguous, LDSC filter_alleles drops all SNPs.
  summarize_coloc_results: Package-relative import in legacy script fails when invoked directly.

fix:
  hess_combine (TWO-PART FIX):
    PART A — fix run_combine() to pass local_rhog_step2 args:
      src/python/run_hess.py lines 495-502 — change cmd to include:
        `--pheno-cor 0 --num-shared 0 --local-hsqg-est <some_hsqg_est_file_or_compute_it>`
      OR split into two sub-invocations (step2 for heritability first, then rho-HESS).
      Note: rho-HESS step2 needs local-hsqg-est (estimated per-locus h2), which the current pipeline doesn't produce — so we may need to add a pre-combine hsqg step2 run for each trait separately.
    PART B — rename existing Launch10 outputs:
      In results/pathway/hess/, rename *_chr{N}_chr{N}.{eig,prjprod,log}.gz → *_chr{N}.{eig,prjprod,log}.gz AND *_chr{N}_trait{1,2}_chr{N}.{info,eig,prjsq}.gz → *_trait{1,2}_chr{N}.{info,eig,prjsq}.gz. Write as a one-shot script to run before hess_combine retries.
  ldsc (3 classes): No code fix needed; just need Launch11 to re-attempt. Confirm that pathway.smk rules still match the current Launch10-running rule code (sanity check no additional mismatch).
  ldsc_munge (bmi_EUR):
    src/python/munge_sumstats_ldsc.py lines 219-220 — change dummy alleles from "A"/"T" to "A"/"G" (non-ambiguous, matches run_hess.py:286-287 convention).
    Delete bmi_EUR_preformatted.tsv.gz and bmi_EUR.log to force retry.
  summarize_coloc_results:
    Either (a) add `sys.path.insert(0, os.path.dirname(__file__))` shim at top of src/legacy/region_analysis/scripts/summarize_coloc_results.py, or (b) change line 15 to `from utils_logging import get_logger` (if utils_logging is in same dir), or (c) wrap shell invocation with `PYTHONPATH=src/legacy/region_analysis:$PYTHONPATH`.

verification:
  hess_combine: Pick one trait pair, rename files manually, test run_combine with local_rhog_step2 args on that one pair. Verify combined.txt produced with expected columns.
  ldsc: In a dry-run post-Launch10, confirm Snakemake re-schedules the 21 failed jobs and they complete.
  ldsc_munge: After fix, bmi_EUR.sumstats.gz appears with ~1.2M SNPs (matching HapMap3 merge size).
  summarize_coloc_results: coloc_summary.tsv produced without ModuleNotFoundError.

files_changed:
  - src/python/run_hess.py — new run_hsqg_step2() fn + patched run_combine() to accept --local-hsqg-est1/2/--pheno-cor/--num-shared and dispatch HESS's local_rhog_step2; extended CLI
  - src/snakemake/rules/pathway.smk — added hess_hsqg_step2 rule (per-pair-per-trait, reads rhog step1 trait-specific outputs post-rename), patched hess_combine to consume hsqg outputs + pass rho-HESS flags
  - src/python/munge_sumstats_ldsc.py — dummy alleles A/T → A/G (LDSC strand-ambiguous filter was dropping every SNP)
  - src/legacy/region_analysis/scripts/summarize_coloc_results.py — added sys.path shim so `from scripts.utils_logging` resolves when invoked outside `scripts.` package
  - tests/phase5/test_hess.py — updated test_harmonized_to_hess_columns for CHR+BP (stale since commit 5c0548b)
  - tests/phase5/test_launch10_regressions.py — 6 new regression tests (rho-HESS dispatch, legacy path preservation, A/G dummy alleles, REF/ALT passthrough, summarize import subprocess, summarize import importlib)

not committed (runtime-only, ~/.planning-gitignored):
  - one-shot rename of 1980 files under results/pathway/hess/ (440 double-chr products + 220 double-chr logs + 1320 trait-chr-chr) with .done mtimes preserved via touch -r from tmpdir cache; sentinel mtimes verified post-rename (2026-04-17 12:26-13:30 Launch10 window)
  - rm results/pathway/ldsc_partitioned/munged/bmi_EUR_preformatted.tsv.gz and bmi_EUR.log to force ldsc_munge retry with A/G fix

final dry-run verification:
  snakemake --dry-run --rerun-triggers mtime -s Snakefile all_pathway → 77 jobs total:
    20 hess_hsqg_step2 (10 pairs × trait1/trait2)
    10 hess_combine
    10 hess_compare_pleio
    8+8+8 ldsc_partitioned_h2 / ldsc_seg_gene_expr / ldsc_seg_chromatin (phantom retries)
    1 ldsc_munge (bmi_EUR rebuild)
    1 summarize_coloc_results (import fix)
    1 ldsc_aggregate_h2 + 1 ldsc_seg_shared_tissues + 1 hess_aggregate + 1 permutation_null_genesets + 1 permutation_aggregate
    1 gprofiler_enrichment + 1 validate_negative_controls + 1 assign_tiers + 1 extract_tier_ab_genes + 1 aggregate_pathway_results + 1 all_pathway
  no hess_local_rhog reruns (mtime triggers on the preserved .done sentinels, not params hash)

final test verification:
  pytest tests/phase5/test_launch10_regressions.py -q → 6 passed
  pytest tests/phase5/ -q --deselect test_ldsc_seg.py::TestLdctsFormat::test_ldcts_fix_paths → 105 passed, 1 deselected
  the deselected test is a pre-existing failure (fix_ldcts_paths keeps absolute paths) unrelated to Launch10 scope; not touched by this session

## Design Decision 2026-04-17 — rho-HESS step2 architecture (orchestrator, approved)

`run_combine()` requires `--local-hsqg-est <path>` for rho-HESS step2 (HESS dispatcher at `tools/hess/hess.py:82-85`). The current pipeline never produces a single-trait heritability estimate. Three options were considered:

- **(a) SELECTED** — Add a new `hess_hsqg_step2` rule that runs once per trait (not per trait-pair), producing `results/pathway/hess/hsqg/{trait}_{ancestry}.local.tsv`. `hess_combine` then consumes this via a new `--local-hsqg-est` input. Rule-count growth: +1 rule, +5 jobs (5 EUR traits) per Launch.
- (b) Pass dummy `--local-hsqg-est 0` — rejected: HESS's rho-step2 multiplies by the hsqg estimate, so passing 0 yields silently wrong covariances.
- (c) Drop HESS rho-covariance from T1 — rejected: rho-HESS is the only local genetic covariance estimator in the pathway phase; CP#1-final narrative depends on per-pair local rho values.

**Blast radius of (a):** New rule, new 5-job wave, no rerun of existing `hess_local_rhog` outputs (those are inputs to `hess_hsqg_step2`, not replaced by it). Renaming the 660 pre-385cadf double-chr outputs stays required — that's a separate one-shot pass that must preserve `.done` mtimes.

## Post-Drain Fix Batch — Final Ordered Plan

1. **munge_sumstats_ldsc bmi_EUR A/T → A/G** — `src/python/munge_sumstats_ldsc.py:219-220` (2-char change). Delete `results/pathway/ldsc_partitioned/munged/bmi_EUR*` to force rebuild.
2. **summarize_coloc_results PYTHONPATH** — prepend `PYTHONPATH=src/legacy/region_analysis:$PYTHONPATH` to the rule shell in `pathway.smk`, OR add `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` at top of `src/legacy/region_analysis/scripts/summarize_coloc_results.py`. Prefer script-side shim (isolates the wiring gap to the legacy script, keeps rule simple).
3. **One-shot HESS rename** — rename 660 double-chr files under `results/pathway/hess/{pair}/` (220 rho-products + 440 trait1/trait2). Bash one-liner with `rename` or `mv` loop; preserve `.done` mtimes via `touch -r original .done`.
4. **New `hess_hsqg_step2` rule** — add to `pathway.smk` after existing `hess_local_rhog` block. Inputs: existing `hess_local_rhog` step1 outputs (post-rename). Output: `results/pathway/hess/hsqg/{trait}_{ancestry}.local.tsv` (5 files for EUR-only per `hess_ancestries`).
5. **Patch `run_combine()` in `src/python/run_hess.py:495-502`** — add `--pheno-cor 0`, `--num-shared 0`, `--local-hsqg-est {both trait hsqg paths}`. Extend shell block in `pathway.smk` `hess_combine` rule to pass the 2 new hsqg inputs.
6. **Regression tests (in same batch or follow-up)** — 3 tests per "Test Coverage Gaps" section above.
7. **Launch11** — `nohup snakemake --profile config/cluster_lsf --rerun-triggers mtime -s Snakefile all_pathway > logs/t1_production_relaunch11.log 2>&1 &`. Expected: 21 LDSC phantoms clear via re-evaluation, 5 new `hess_hsqg_step2` jobs run, 7 `hess_combine` retries consume them, 1 bmi_EUR `ldsc_munge` + downstream retry, 1 `summarize_coloc_results` retry.

**Gating:** Launch10 must be fully drained before ANY of steps 1-5 are applied. `--rerun-triggers mtime code` in the live driver will otherwise cascade reruns into the still-scheduling queue.

---

## 2026-04-17T21:14Z — Launch11 partial failure on new `hess_hsqg_step2` rule

**Status:** Launch11 (PID 2326428) fired 16:25, at 17:14 EDT shows 2/77 finished + 2 `hess_hsqg_step2` failures. Driver still alive. LDSC retries and non-HESS jobs still pending.

### New bug found

`hess.py local_hsqg_step2` exits 1 with:
> `[ERROR] Rank of A less than the number of loci. There might be loci with no SNP.`

(See `results/pathway/hess/hsqg/bmi_stroke_EUR_trait2.local.log` — hess.py's own log file; captured because subprocess.run() with check=True swallowed the stderr otherwise.)

### Root cause

`local_rhog_step1` internally calls `local_hsqg_step1_helper` per trait (`estimation.py:419-421`), producing trait-specific `.info.gz`/`.eig.gz`/`.prjsq.gz` outputs that ARE semantically valid `local_hsqg_step1` outputs. The issue is data quality: **4 loci across all 22 chromosomes have `nsnp=0`** (regions where harmonized bmi.EUR sumstats has no SNPs overlapping the HESS partition). `local_hsqg_step2` computes a matrix A from loci projections and rejects if rank(A) < number of loci — an empty locus contributes a zero row → rank deficiency.

Evidence:
```
# zcat bmi_stroke_EUR_trait2_chr*.info.gz | awk '$3==0 || $4==0' | wc -l
4
```

### Architectural note

Option (a) design is still correct. The fix is a pre-filter, not a redesign. Filter info.gz files in `run_hsqg_step2()` to drop rows with `nsnp==0` (col 3) or `rank==0` (col 4) before invoking hess.py; filtered files written to a sibling path (e.g., `{prefix}_filt_chr{N}.info.gz`), and `--prefix` adjusted. Must also filter `.eig.gz` and `.prjsq.gz` rows to match (these are per-locus line-indexed to the info file).

### Fix plan (Launch12)

Step 1 — in `src/python/run_hess.py run_hsqg_step2()`:
- Before subprocess.run, read the 22 info.gz files for this prefix, identify row indices where `nsnp==0 or rank==0`, and write filtered copies to `{prefix}_filt_chr{N}.info.gz` + matching `.eig.gz` + `.prjsq.gz` (line-indexed drop).
- Change `--prefix` passed to hess.py to use the filtered base.
- Log count of dropped loci per chromosome at INFO level.

Step 2 — also capture and surface hess.py stderr on failure (currently swallowed):
- In exception handler, log `e.stderr` + `e.stdout` at ERROR level before re-raising.
- Also copy hess.py's own log file (`{out}.log`) to the Snakemake stderr stream on failure.

Step 3 — regression test: `test_hsqg_step2_filters_empty_loci` — fixture with 3 loci where 1 has `nsnp=0`, verify filtered info has 2 rows and hess.py is called with the filtered prefix.

**Blast radius:** Only touches `run_hsqg_step2()` + adds one test. No Snakefile rule change (new filtered files are intermediate; rule outputs are unchanged). No hess.py patch. No rerun cascade.

### Launch11 salvage

- Let Launch11 drain. LDSC retries (24 jobs) + bmi_EUR ldsc_munge + summarize_coloc_results should succeed independently of the HESS side.
- Expected Launch11 end state: ~26-27 green / ~51 red (HESS side + aggregators blocked on HESS).
- Apply Launch12 fix batch (filter + stderr surfacing + test) post-drain, then fire Launch12 targeting only the failing HESS subtree.

---

## 2026-04-17T22:20Z — Launch11 killed; Launch12 fix batch applied (Bug 1+2+3)

**Status:** Launch11 killed at 18:05 EDT (user-approved Option A). Driver SIGKILL'd after SIGTERM; Snakemake locks `.snakemake/locks/0.input.lock` + `0.output.lock` present at start of session, cleared via `snakemake --unlock`.

### Bug 3 scope clarification

Objective said "route AFR frq for ldsc_seg_*" too, but investigation confirmed `run_ldsc_seg.py` does NOT currently pass `--frqfile-chr` to `ldsc.py --h2-cts`. Evidence: grep for `--frqfile` in `src/python/run_ldsc_seg.py` → 0 matches. Further evidence: `stroke_AFR_gene_expr` succeeded at 17:12 EDT during Launch11 with no frqfile (see `results/pathway/ldsc_seg/stroke_AFR_gene_expr.log` end-of-file `Total time elapsed: 27.0m`). Only `ldsc_partitioned_h2` hits the condition-number error because only it passes `--frqfile-chr` and invokes `--h2 --overlap-annot`.

**Resolution:** `ldsc_partitioned_h2` gets the ancestry-specific frqfile dispatch (real fix). `ldsc_seg_gene_expr` and `ldsc_seg_chromatin` get the `.afr_frq_done` sentinel as an input for AFR ancestry (consistent gating + future-proofing) but no shell-body change. This is documented in the rule docstrings for both SEG rules.

### AFR frq acquisition strategy

No alkesgroup distribution ships per-ancestry AFR frq files (searched Broad alkesgroup docs; Zenodo S-LDSC reference bundle; cambridge-ceu docs — all EUR-only for frq). Generated locally:

- Input: `data/raw/1kg/vcf/chr{1..22}.vcf.gz` (GRCh37/b37, confirmed via VCF header contig `assembly=b37`)
- Input: `data/raw/1kg/AFR.samples` (504 samples, covers YRI/LWK/GWD/MSL/ESN/ASW/ACB)
- Filter: restricted to LDSC EUR SNP set via `--extract <EUR .bim>` so variant IDs match the LD scores
- Command: `plink --vcf <chr>.vcf.gz --double-id --keep AFR.samples --extract <eur.bim> --make-bed` → `plink --bfile ... --freq`
- Output: `data/reference/ldsc/1000G_Phase3_frq_AFR/1000G.AFR.QC.{N}.frq`
- Validated on chr22: 141,124 variants × 504 samples in ~30 seconds, matching EUR frq format exactly (same 6 columns: CHR, SNP, A1, A2, MAF, NCHROBS).

### Fix batch applied

1. **`src/python/run_hess.py`** — 3 changes:
   - New `_filter_empty_loci(prefix, filt_prefix, chromosomes)` reads `.info.gz`/`.eig.gz`/`.prjsq.gz`, drops rows where `nsnp==0 OR rank==0`, writes filtered copies. Line-aligned across the three files (HESS writes an empty eig/prjsq line for empty loci — see `tools/hess/src/estimation.py:81-82`).
   - New `_run_hess_subprocess(cmd, description, out_for_log)` wraps `subprocess.run(..., check=True)` and logs `e.stderr`, `e.stdout`, AND contents of hess.py's `{out}.log` at ERROR level before re-raising `CalledProcessError`.
   - `run_hsqg_step2` calls `_filter_empty_loci` then passes `{prefix}_filt` to hess.py. `run_combine` and `run_local_rhog` route through `_run_hess_subprocess` for consistent stderr surfacing.

2. **`src/snakemake/rules/pathway.smk`** — 4 changes:
   - New helpers `_ldsc_frqfile_chr(ancestry)` and `_ldsc_frq_flag(ancestry)` dispatch the frqfile prefix and sentinel on ancestry.
   - New `rule download_ldsc_afr_frq` generates per-chromosome AFR frq files via plink 1.9 in `envs/plink.yml` env. Idempotency guard skips generation when all 22 files are present.
   - `ldsc_partitioned_h2`: `frqfile_chr` param now dispatches on `wc.ancestry`; new `frq_flag` input gates AFR on `.afr_frq_done`.
   - `ldsc_seg_gene_expr` / `ldsc_seg_chromatin`: new `frq_flag` input for consistent AFR gating (shell body unchanged — `--h2-cts` doesn't consume `--frqfile-chr`).

3. **`tests/phase5/test_launch10_regressions.py`** — 5 new tests:
   - `test_filter_empty_loci_drops_nsnp_zero_and_rank_zero` — 3-chromosome fixture with 3 empty loci; verifies per-chr kept/dropped counts + line-aligned filtered output.
   - `test_run_hsqg_step2_invokes_hess_with_filtered_prefix` — 22-chr fixture, mocks `subprocess.run`, verifies cmd contains `--prefix {orig}_filt`.
   - `test_run_hess_subprocess_surfaces_stderr_stdout_and_log` — seeds a hess.py-style log file with "Rank of A less than the number of loci", raises `CalledProcessError` with stderr+stdout, asserts all three appear in caplog at ERROR level.
   - `test_ldsc_frqfile_chr_routes_afr_to_afr_prefix` — extracts helper from pathway.smk via exec, verifies AFR→`1000G.AFR.QC.`, EUR→`1000G.EUR.QC.`, unknown→EUR fallback.
   - `test_ldsc_frq_flag_routes_afr_to_afr_sentinel` — AFR gates on `.afr_frq_done`, EUR gates on `.baseline_download_done`.

### Verification

- `pytest tests/phase5/ -x -q` → 110 passed, 1 deselected (unchanged baseline)
- `pytest tests/phase5/test_launch10_regressions.py -x -q` → 11 passed (6 existing + 5 new)
- `snakemake --dry-run --rerun-triggers mtime -s Snakefile all_pathway` → 76 jobs:
    1 download_ldsc_afr_frq (NEW)
    20 hess_hsqg_step2, 10 hess_combine, 10 hess_compare_pleio
    8 ldsc_partitioned_h2 (all EUR+AFR)
    7 ldsc_seg_gene_expr (1 fewer than 8 — stroke_AFR_gene_expr succeeded in Launch11)
    8 ldsc_seg_chromatin
    1 ldsc_munge (bmi_EUR rebuild — still pending)
    11 aggregators/tiers/summaries
  - Launch11 had 77 jobs; Launch12 has 76 because stroke_AFR_gene_expr landed during Launch11 and the new `download_ldsc_afr_frq` rule is +1. Net: 77 - 2 (seg + summarize succeeded) + 1 (AFR frq rule) = 76.

### Ready for Launch12

Command (orchestrator to fire):
```
nohup /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
    --profile config/cluster_lsf --rerun-triggers mtime \
    -s Snakefile all_pathway \
    > logs/t1_production_relaunch12.log 2>&1 &
```

---

## 2026-04-18T13:00Z — Launch12 post-mortem; surface failures resolve to TWO new bugs (Bug 4 + Bug 5)

**Status:** Launch12 driver process gone (pgrep empty, bjobs empty); log stops at `[Sat Apr 18 11:24:01 2026] Error in rule hess_combine` with NO graceful shutdown markers (no `Shutting down`, no `Exiting because`, no `Complete log`). 29/76 finished, 13 errors logged. Driver-death cause undetermined (no traceback, no SIGKILL marker in log) — most likely cluster operator cleanup of long-running head-node nohup process; deferred (Launch13 needs robust wrapper).

### Per-job failure evidence summary

| Rule | Jobs failed | Error | Surface vs root cause |
|---|---|---|---|
| `hess_combine` | t2d_hypertension_EUR (741054→741109), t2d_stroke_EUR (741109), hypertension_asthma_EUR (741128) + others | `[ERROR] Rank of A less than the number of loci.` (estimation.py:506) | `_filter_empty_loci()` IS applied to step 1 outputs by `run_hsqg_step2()` (line 711) but is NOT applied by `run_combine()` (line 778-785, no filter call). Combine passes the unfiltered `prefix` so `local_rhog_step2` reads original `_trait{1,2}_chr{N}.info.gz` containing the empty locus (chr12 start=8377536 confirmed for t2d_hypertension_EUR via zcat info.gz). |
| `ldsc_partitioned_h2` | t2d_AFR (741121), asthma_AFR (741123), stroke_AFR (741126), hypertension_EUR (Launch12 02:05) — and ALL prior runs (zero `.results` files exist) | `ValueError: ERROR: LD Score matrix condition number is {1e20}. Remove collinear LD Scores or use the --invert-anyway flag.` (sumstats.py:338) | Affects ALL ancestries (EUR + AFR), NOT just AFR. Intrinsic collinearity in baselineLD (97 annotations) + custom_pathway joint matrix. Standard S-LDSC remedy is `--invert-anyway`. The previous "AFR frq mismatch" diagnosis (in `download_ldsc_afr_frq` rule docstring at pathway.smk:336-341) is incorrect — the AFR frq files are correctly generated (504 samples × 22 chrs, 141K variants per chr) and reaching ldsc.py; condition number issue is upstream of frq alignment. |
| `ldsc_seg_gene_expr` `ldsc_seg_chromatin` | (741120, 741122, 741124, 741125, 741127 listed in objective) | NONE — false-positive failure classification. All 5 .err files end with `Finished job 0. 1 of 1 steps (100%) done` and produced `*_cell_type_results.txt` outputs (sizes 18-49 KB). | Cataloging error: non-zero `.err` file size mistaken for failure; LDSC-SEG writes informational text to stderr. |

### Bug 4: HESS combine — `_filter_empty_loci` not applied to combine step

`src/python/run_hess.py`:
- Line 711 (`run_hsqg_step2`): calls `_filter_empty_loci(prefix, filt_prefix)` then passes `filt_prefix` to hess.py.
- Lines 778-785 (`run_combine`): builds cmd with `--prefix prefix` (line 782) — original unfiltered prefix. NO filter call.

Why this is wrong: rho-HESS step 2 (`local_rhog_step2`) reads `{prefix}_trait{1,2}_chr{N}.info.gz` and computes `A = np.diag(info1['N']*info2['N'])` (estimation.py:497). An empty locus (`nsnp==0`, `N==0` per the actual info file rows confirmed for t2d_hypertension_EUR at chr12 start=8377536) puts a zero on the diagonal → `np.linalg.matrix_rank(A) < nloci` → exit 1.

**Mechanical fix:**
1. Generalize `_filter_empty_loci` (or add `_filter_empty_loci_rhog`) to handle the rho-HESS file naming pattern: `{prefix}_trait{1,2}_chr{N}.info.gz` (line-aligned across both traits) + `{prefix}_chr{N}.{eig,prjprod}.gz` (line-aligned with the trait info files). Drop a row index k if EITHER `info1[k].nsnp==0` OR `info2[k].nsnp==0`.
2. Call from `run_combine()` before building hess.py cmd; pass `filt_prefix` as `--prefix`.
3. Regression test: 2-locus fixture where locus 2 has `nsnp==0` in trait1 → filtered files have 1 row × 5 file types (info1, info2, eig, prjprod) line-aligned; cmd contains `--prefix {orig}_filt`.

### Bug 5: LDSC partitioned_h2 — missing `--invert-anyway`

`src/python/run_ldsc_partitioned.py:402-411` (`run_partitioned_h2`):
```python
cmd = [
    sys.executable, ldsc_py,
    "--h2", sumstats,
    "--ref-ld-chr", ref_ld_chr,
    "--w-ld-chr", w_ld_chr,
    "--overlap-annot",
    "--frqfile-chr", frqfile_chr,
    "--out", out,
]
```
No `--invert-anyway`. Per LDSC FAQ + sumstats.py:326-338, `--invert-anyway` is the documented remedy for ill-conditioned baselineLD + custom annotation joint matrices when condition_number > 100,000.

**Mechanical fix:**
1. Add `"--invert-anyway",` to the cmd list in `run_partitioned_h2()`.
2. Update the rule docstring in pathway.smk to remove the (now-incorrect) "AFR frq mismatch causes condition number" theory; document that --invert-anyway is required for the canonical baselineLD + 1-extra-annotation S-LDSC model.
3. Regression test: mock `subprocess.run`, call `run_partitioned_h2(...)`, assert `--invert-anyway` is in `cmd`.

### Driver-death secondary investigation

Launch12 driver disappeared without graceful shutdown. Operator (Carter) does not recall killing. No traceback, no SIGKILL/SIGTERM marker in log, no out-of-memory error. Most likely cause: cluster operator cleanup of long-running head-node nohup processes (NCSU HPC commonly enforces this on shared head nodes). Process termination would be SIGKILL → bash drops the process without flushing logs.

**Mitigation for Launch13:** wrap snakemake in `bsub` (submit driver TO the cluster, not run on head node) OR use systemd-style `setsid` + heartbeat logging. NOT in scope for this debug session — Launch13 is the operator's call.

### Fix batch ordering

1. **Bug 5 (LDSC --invert-anyway)** — smaller change, no fixture work; ship first.
2. **Bug 4 (HESS combine filter)** — requires generalized filter function + fixture.
3. Update pathway.smk `download_ldsc_afr_frq` and `ldsc_partitioned_h2` rule docstrings (replace AFR-frq-mismatch theory with collinearity theory).
4. Tests: 2 new in `test_launch10_regressions.py`.
5. Dry-run all_pathway → expect ~20 jobs (10 hess_combine + 8 ldsc_partitioned_h2 + 10 hess_compare_pleio + aggregators) since LDSC-SEG and ldsc_munge already drained.

### Hand-off after fix

Launch13 operator action (NOT this session):
- Launch in robust wrapper (bsub-driver or setsid+heartbeat) to survive head-node cleanup.
- Existing `.snakemake/locks/` (from Launch12 — empty since driver gone) need `snakemake --unlock` first.

---

## 2026-04-18T13:30Z — Bug 4 + Bug 5 fix batch applied

### Files changed

1. **`src/python/run_ldsc_partitioned.py`** — Bug 5 fix:
   - `run_partitioned_h2()` cmd now includes `--invert-anyway` between `--frqfile-chr` and `--out`.
   - Updated docstring to explain the canonical S-LDSC remedy and reference the debug session post-mortem.

2. **`src/python/run_hess.py`** — Bug 4 fix:
   - New `_filter_empty_loci_rhog(prefix, filt_prefix, chromosomes)` helper. Reads the four rho-HESS step1 files (`{prefix}_trait{1,2}_chr{N}.info.gz` and `{prefix}_chr{N}.{eig,prjprod}.gz`), drops a row index k if `info1[k].nsnp==0 OR info2[k].nsnp==0 OR rank==0` (defensive OR — partition geometry is shared so the empty-locus indices align in practice, confirmed for t2d_hypertension_EUR chr12 row 8 in both traits). Writes filtered copies under `{filt_prefix}` with the four file naming patterns preserved. Validates equal line counts across all four files (raises ValueError on mismatch).
   - `run_combine()` rho-HESS dispatch branch now calls `_filter_empty_loci_rhog(prefix, f"{prefix}_filt")` and passes `{prefix}_filt` as `--prefix` to hess.py. Legacy single-trait path is unchanged.

3. **`src/snakemake/rules/pathway.smk`** — docstring corrections:
   - `download_ldsc_afr_frq` rule: NOTE clarifying the rule remains correct (per-ancestry MAF weights for unbiased AFR enrichment) but is NOT what fixes the condition-number error; cross-references the post-mortem section.
   - `ldsc_partitioned_h2` rule: documents that --invert-anyway is the actual condition-number bypass.

4. **`tests/phase5/test_launch10_regressions.py`** — 3 new tests + 1 fixture update:
   - `test_filter_empty_loci_rhog_drops_when_either_trait_is_empty`: 4-locus 1-chr fixture; trait1-empty and trait2-empty rows both dropped via OR; all four output files line-aligned at 2 rows.
   - `test_run_combine_pre_filters_empty_loci_and_passes_filtered_prefix`: 22-chr fixture, mocks subprocess.run, asserts `cmd[--prefix idx + 1] == {prefix}_filt`, verifies filtered files exist on disk.
   - `test_run_partitioned_h2_passes_invert_anyway`: mocks subprocess.run, asserts `--invert-anyway` AND `--overlap-annot` both in cmd.
   - `test_run_combine_rho_hess_dispatch` (existing) updated to write 22-chr rho-HESS step1 fixtures (now required since the new pre-filter pass reads the input files).
   - New helper `_write_rhog_step1_files(prefix, chrom, info1_rows, info2_rows, eig_rows, prjprod_rows)` for fixture creation.

### Verification

- `pytest tests/phase5/test_launch10_regressions.py -v` → **14 passed** (11 existing + 3 new).
- `pytest tests/phase5/ --deselect test_ldsc_seg.py::TestLdctsFormat::test_ldcts_fix_paths -q` → **113 passed, 1 deselected** (unchanged baseline; the deselected test is pre-existing).
- Snakemake locks cleared (`snakemake --unlock`).
- Dry-run `all_pathway` resolves cleanly: **47 jobs total**:
  - 10 hess_combine (with new pre-filter), 10 hess_compare_pleio
  - 3 hess_hsqg_step2 (loci that hadn't completed before Launch12 driver died)
  - 8 ldsc_partitioned_h2 (all trait × ancestry — none had succeeded pre-fix)
  - 2 ldsc_seg_gene_expr + 2 ldsc_seg_chromatin (gaps in the 16-job set; rest succeeded in Launch12)
  - 1 ldsc_munge (bmi_EUR rebuild — still pending from Launch12)
  - 11 aggregators / tiers / summaries
- Verified `tools/ldsc/ldsc.py:745` has `--invert-anyway` in argparse and `tools/ldsc/ldscore/sumstats.py:327` reads `args.invert_anyway` to bypass the condition-number raise. Wiring is end-to-end correct.

### Resolution

root_cause:
  Bug 4 (hess_combine, 10 EUR trait pairs): Launch12 commit 030130b added the rho-HESS dispatch args (--pheno-cor / --num-shared / --local-hsqg-est) to run_combine() but did NOT add the empty-loci pre-filter that was concurrently added to run_hsqg_step2(). hess.py local_rhog_step2 builds A = diag(N1*N2); empty loci have N==0 → diagonal zero → rank deficient → `[ERROR] Rank of A less than the number of loci.`
  Bug 5 (ldsc_partitioned_h2, all trait × ancestry — EUR + AFR): the joint baselineLD v2.2 (97 annotations) + custom_pathway annotation matrix has intrinsic numerical collinearity that drives `np.linalg.cond > 1e5` for ALL ancestries (cond 2.9e20 for hypertension_EUR with EUR frq, 8.8e19 for t2d_AFR with AFR frq). The previous `download_ldsc_afr_frq` patch (commit 0a2ad0f) misattributed the cause to AFR-vs-EUR frq mismatch; the AFR frq files are correctly generated and reaching ldsc.py but the failure is downstream at `check_ld_condition_number`. The canonical S-LDSC remedy is `--invert-anyway` (per LDSC FAQ + sumstats.py:326-338).
  Misclassified failures: 5 ldsc_seg_* jobs in the failure catalog (741120/22/24/25/27) actually succeeded — `Finished job 0. 1 of 1 steps (100%) done` and produced cell_type_results.txt outputs. Cataloging error: non-zero stderr file size mistaken for failure; LDSC-SEG writes informational lines to stderr.

fix:
  Bug 4: new `_filter_empty_loci_rhog` helper + wire into `run_combine()` rho-HESS dispatch branch; pass `{prefix}_filt` to hess.py.
  Bug 5: add `--invert-anyway` to `run_partitioned_h2()` cmd.

verification: 113 tests pass + dry-run resolves to 47-job DAG; CLI flag wiring confirmed via `grep` against ldsc.py argparse + sumstats.py args usage. Code-level evidence is sufficient that the changes are correct; full end-to-end validation requires a real Launch13 run (gated on operator producing a head-node-survivable wrapper).

files_changed:
  - src/python/run_ldsc_partitioned.py
  - src/python/run_hess.py
  - src/snakemake/rules/pathway.smk
  - tests/phase5/test_launch10_regressions.py

---

## 2026-04-18T20:55Z — Bug 5 RE-DIAGNOSIS: ffbabce's --invert-anyway is the WRONG fix

The previous diagnosis (cond 1.16e20 = "intrinsic baselineLD collinearity, fix with `--invert-anyway` per LDSC FAQ") was **incorrect**. Production evidence after ffbabce shipped (`asthma_EUR_pathway_h2.log` 2026-04-18 19:59:47 → 20:00:42) shows the flag is honored but the linear solve still fails.

### ROOT CAUSE FOUND

**MHC × no-MHC weights collision in NEGCTRL_HLA_IMMUNE annotation.**

The `NEGCTRL_HLA_IMMUNE` annotation in `results/pathway/ldsc_partitioned/ld_scores/custom_pathway.*.l2.ldscore.gz` is non-zero on **2,304 SNPs all on chr6, BP range 26,033,506–33,965,434** — i.e., the canonical MHC region. By design this annotation is HLA-region-specific.

The LDSC regression weights file used by the `ldsc_partitioned_h2` rule is `data/reference/ldsc/1000G_Phase3_weights_hm3_no_MHC/weights.hm3_noMHC.{1..22}.l2.ldscore.gz`. Its chr6 file contains 72,386 SNPs with **EXACTLY 0 SNPs in the 25–34 Mb MHC interval** (verified empirically; this is the file's design).

When `read_ld_and_sumstats` (sumstats.py:511) does `sumstats = merge_and_log(sumstats, w_ld, "regression SNP LD", logger)`, the inner-join drops every SNP where `NEGCTRL_HLA_IMMUNE > 0`. The column becomes the zero vector on the regression-eligible SNP set (967,534 SNPs for asthma_EUR), making `X^T X` singular by exactly 1 dimension. `--invert-anyway` bypasses the `check_ld_condition_number` raise but `np.linalg.solve(xtx, xty)` at jackknife.py:376 still hits a singular matrix.

`check_variance` (sumstats.py:358) does NOT catch this — it runs on the full pre-merge ref_ld where the column has variance from the chr6 MHC SNPs. The post-merge re-zeroing is invisible to it.

**Quantitative confirmation** (.planning/debug/svd_postmerge_check.py):
- Genome-wide ref_ld (1.19M SNPs × 108 cols): cond = 5.25e3 (well-conditioned, full rank)
- After HM3 sumstats merge + weights.hm3_noMHC merge → 967,534 × 108: cond = **1.161518e20** (matches production log 1.16e20 to 5 sig figs)
- σ_min = 8.88e-15, smallest right singular vector points entirely (v=+1.00000) at `NEGCTRL_HLA_IMMUNEL2`
- Numerical rank: 107 / 108 (exactly 1-dimensional rank deficiency)

This is **not** baselineLD-side intrinsic collinearity. baselineLD on its own has cond ≈ 5e3 in the production-merged subset. The deficiency is a single-column zero introduced by an annotation × weight-file design mismatch.

### Why this matters for the research design

The same bug pattern will also affect any future custom annotation that is concentrated in regions excluded by HM3-no-MHC (the standard LDSC weight file). HLA is the only such region for the v2.2 baselineLD reference, but it is also a known pleiotropic immune-disease hotspot — including a NEGCTRL_HLA_IMMUNE annotation was a deliberate negative-control design choice in the pathway phase. We must decide whether to keep that negative control intact (different fix path) or accept its loss for the partitioned-h2 step (different fix path).

### Remediation alternatives

For Carter to choose. Each has different research-design + OSF/methods-narrative impact.

**Option 1 — Drop NEGCTRL_HLA_IMMUNE from the partitioned-h2 annotation set only (RECOMMENDED for least research impact)**
- Mechanism: filter NEGCTRL_HLA_IMMUNE out of `custom_pathway.*.l2.ldscore.gz` (or out of the `--ref-ld-chr` argument) when running ldsc_partitioned_h2 specifically. Keep it everywhere else (it remains valid for `ldsc_seg` analyses that use HM3-with-MHC weights, and for the negative-control narrative on per-pair coloc).
- Impact: NEGCTRL_HLA_IMMUNE no longer contributes a τ* estimate in the partitioned-h2 results. The OTHER 2 negative controls (NEGCTRL_COSMETIC, NEGCTRL_BLOOD_GROUP) still appear → the negative-control claim survives at 2-of-3 strength.
- OSF amendment: minor — methods note that HLA negative control is excluded from S-LDSC partitioned-h2 due to a design conflict with the standard weight file (which is itself a published method choice). Cite Finucane 2015 LDSC weight choice + Bulik-Sullivan 2015 MHC exclusion rationale.
- Code change: smallest. Modify the `compute_ld_scores` step or the `h2` step to subset the annotation list. Single ~5-line addition.
- Significant signals retained: CUSTOM_INSULIN_SIGNALING, CUSTOM_APPETITE_REGULATION, CUSTOM_GLUCOSE_METABOLISM, CUSTOM_FATTY_ACID_METABOLISM, CUSTOM_INFLAMMATION, CUSTOM_VASCULAR_TONE, CUSTOM_LIPID_TRANSPORT, CUSTOM_ENERGY_STORAGE = all 8 hypothesis-driving annotations + 2 negative controls = full hypothesis test, partial (2/3) negative control test.

**Option 2 — Switch from `weights.hm3_noMHC` to `weights.hm3` (with-MHC weights)**
- Mechanism: change the `--w-ld-chr` argument in `run_partitioned_h2` from `weights_hm3_no_MHC/weights.hm3_noMHC.` to `weights_hm3/weights.hm3.` (need to verify file availability — `weights.hm3` is shipped in `1000G_Phase3_weights_hm3.tgz`, not currently in the project's reference dir).
- Impact: NEGCTRL_HLA_IMMUNE now has surviving SNPs in the regression set → no zero column. BUT this contradicts the standard S-LDSC method (Finucane 2015), where MHC exclusion is canonical to avoid LD-driven inflation in heritability partitioning around HLA.
- OSF amendment: SUBSTANTIAL — explicit methods deviation from the Finucane 2015 MHC-exclusion convention. Reviewer-bait. Defensible if you argue NEGCTRL inclusion outweighs the LD-inflation risk for this specific design.
- Code change: 1-line in pathway.smk + new download rule for the with-MHC weights file (~30 LOC).
- Risk: a follow-up cross-check in a sensitivity analysis is required to show that the partitioned-h2 estimates for non-HLA annotations are robust to the with-MHC weights swap. That's a non-trivial methods chapter.

**Option 3 — Re-engineer NEGCTRL_HLA_IMMUNE to also include a non-MHC immune control set**
- Mechanism: at the annotation construction step (Phase 5 / pathway annotation builder), expand NEGCTRL_HLA_IMMUNE to include immune-related genes outside MHC (e.g., immune cytokine receptors on chr1/2/X) so the annotation has SNPs both inside and outside MHC. The non-MHC SNPs survive the weight-file inner-join → non-zero variance → no rank deficit.
- Impact: changes the *meaning* of NEGCTRL_HLA_IMMUNE — it is no longer HLA-specific. Have to rename to e.g. NEGCTRL_IMMUNE_REGULATION. The conceptual negative-control hypothesis (that HLA enrichment ≠ trait enrichment) is weakened.
- OSF amendment: SUBSTANTIAL — annotation set re-designed mid-stream. Pre-registration would need to be amended with explanatory rationale.
- Code change: medium — modify the pathway annotation generator (`generate_custom_annotations.py` or equivalent), regenerate annot.gz files for all 22 chrs, regenerate LD scores (the most expensive step — ~2-4 h cluster time), re-run Phase 5 partitioned-h2.
- Significant signals retained: same 8 CUSTOM + 3 NEGCTRL annotations, but NEGCTRL_HLA_IMMUNE is now broader-immune.

**Option 4 — baseline-LD-LITE (47 cols, Gazal 2018) AS WELL AS one of options 1-3**
- Mechanism: switch the baseline annotation from baselineLD v2.2 (97 annotations) to baselineLD-LITE (47 annotations, drops the 50 highly-collinear continuous annotations). Retains the joint-partitioning interpretability but with smaller baseline.
- IMPORTANT: this is ORTHOGONAL to the actual root cause (the bug is NEGCTRL_HLA_IMMUNE × no-MHC weights, not baseline-internal collinearity). Option 4 alone does NOT fix the LinAlgError. It would be applied as a methodological refinement on top of Option 1 (or 2 or 3) to reduce the secondary collinearities we observed in baselineLD (Human_Promoter_Villar_ExAC.flanking.500 ↔ Human_Promoter_Villar_ExAC ↔ CpG_Content_50kb at σ ~ 200 each).
- Impact: smaller baseline → cleaner τ* estimates per Gazal 2018; fewer baseline annotations to cite + interpret. Some loss in capturing baselineLD's continuous functional annotations.
- OSF amendment: MODERATE — methodological choice change, well-precedented in the literature (Gazal 2018 baselineLD-LITE is a standard option in S-LDSC).
- Code change: medium — download baselineLD-LITE files (~1 GB), update `--ref-ld-chr` baseline prefix in pathway.smk + run_ldsc_partitioned.py, re-run.

### Recommendation

**Option 1 ALONE** is the minimal correct fix. It cleanly resolves the LinAlgError, preserves all 8 hypothesis-driving CUSTOM annotations, retains 2 of 3 negative controls, and the OSF amendment is small and easily defensible (the standard S-LDSC weight file is no-MHC; HLA-specific annotations are mechanically incompatible with that weight file by published convention).

If a fuller methodological refinement is desired (and the OSF amendment effort is acceptable), Option 1 + Option 4 (baseline-LITE) gives the cleanest published-method profile.

Options 2 and 3 each require non-trivial OSF amendments and are NOT recommended unless there is a specific reviewer-driven reason to deviate from convention.

### NOT applied

This is a diagnose-only run. No source code, rule files, or annotation files were modified. The previous ffbabce `--invert-anyway` change is still in place in `src/python/run_ldsc_partitioned.py` — leaving it does not cause harm (it's a no-op once the rank deficiency is removed; `cond < 1e5` will be true so the warning won't fire either). Carter should decide on Option 1/2/3 (± Option 4) before re-spawning a `find_and_fix` debug session.

### Files produced (analysis artifacts, NOT shipped)

- `.planning/debug/svd_rank_check.py` — chr22-only SVD analysis
- `.planning/debug/svd_genome_check.py` — genome-wide SVD + per-annotation coverage
- `.planning/debug/svd_postmerge_check.py` — replicates the exact LDSC-side merges to reproduce cond = 1.16e20
- These files document the analysis but are not part of the production pipeline.

---

## 2026-04-18T22:00Z — Implementation (Carter chose Option 1)

Carter selected Option 1 (drop NEGCTRL_HLA_IMMUNE from the partitioned-h2 annotation set ONLY). Reverted ffbabce's misleading `--invert-anyway` flag.

### Implementation choice: OPTION B (in-process column drop in run_ldsc_partitioned.py)

Three options were considered:

| Option | Mechanism | Cost | DAG impact | Live-Launch13 risk |
|---|---|---|---|---|
| A | Parallel rule `ldsc_compute_ld_scores_partitioned_h2` writing `custom_pathway_phh2.{N}.l2.ldscore.gz` | +22 ldscore-compute jobs (~5 min each); new rule | New outputs, new DAG nodes | Low (Launch13 sees `--nolock` only) but adds disk I/O |
| **B (CHOSEN)** | In-process column drop in `run_partitioned_h2` to a per-job `tempfile.mkdtemp` dir; LDSC sees the filtered prefix; tmp dir cleaned up after subprocess returns | ~22 small file reads + writes per partitioned-h2 job (~30s extra; partitioned-h2 itself runs minutes) | NONE — invisible to Snakemake | Zero — no new DAG nodes, no rule signature change, no rerun cascade |
| C | LDSC native `--annot-include / --annot-exclude` flag | N/A — LDSC argparse has no such flag (verified via `tools/ldsc/ldsc.py` parser) | N/A | N/A |

**Why B over A:** Surgical, localized to the file the bug is in, no DAG topology change (which is critical while Launch13 is live in `RUN` state). Snakemake's mtime-based rerun-trigger does NOT see new outputs because there are none — the filtered files live in `tempfile.mkdtemp(prefix="ldsc_partition_h2_filt_")` and are deleted via `try/finally` cleanup after every LDSC invocation (success or failure). Other consumers (LDSC-SEG, the negative-control narrative on per-pair coloc) keep all 11 annotations in the canonical `custom_pathway.{N}.l2.ldscore.gz`.

### Files changed

1. **`src/python/run_ldsc_partitioned.py`** (3 additions + 1 revert):
   - Added `PARTITIONED_H2_DROP_ANNOTATIONS = ("NEGCTRL_HLA_IMMUNE",)` module constant with full debug-session reference.
   - Added 3 helper functions:
     - `_drop_columns_from_ldscore(src, dst, drop_annotations)` — streams `.l2.ldscore.gz`, drops named columns by header match, validates row width consistency.
     - `_drop_columns_from_m_file(src, dst, annotation_drop_indices)` — handles the single-line `.l2.M` and `.l2.M_5_50` siblings (no CHR/SNP/BP prefix; index shift by -3).
     - `_strip_annotation_for_partitioned_h2(src_prefix, dst_prefix, drop_annotations, chromosomes)` — orchestrator that processes 22 chromosomes, validates kept-annotation list is identical across chrs.
   - Patched `run_partitioned_h2()` to:
     - Detect custom prefix as last entry of `ref_ld_chr` (per D-04a baseline-first).
     - Build a per-job `tempfile.mkdtemp(prefix="ldsc_partition_h2_filt_")` directory.
     - Call `_strip_annotation_for_partitioned_h2` to produce the filtered triplet.
     - Rewrite `--ref-ld-chr` to point at the filtered prefix.
     - Wrap the LDSC subprocess in `try/finally` for cleanup (best-effort `shutil.rmtree`).
   - **REVERT of ffbabce:** removed `--invert-anyway` flag from cmd; updated all docstring references to explain why it was the wrong fix and the column-drop is the real one.
   - Imports: added `shutil`, `tempfile`.

2. **`src/snakemake/rules/pathway.smk`** (docstring only):
   - `ldsc_partitioned_h2` rule docstring updated to explain Option 1 / Bug 5 RE-DIAGNOSIS, the MHC × no-MHC mechanism, and the OSF amendment note (NEGCTRL_HLA_IMMUNE excluded from partitioned-h2 only; preserved everywhere else).

3. **`tests/phase5/test_launch10_regressions.py`** (1 test rewritten + 3 new tests + 1 fixture helper):
   - **REWROTE** existing `test_run_partitioned_h2_passes_invert_anyway` → `test_run_partitioned_h2_drops_negctrl_hla_immune_and_omits_invert_anyway`. The new test asserts (a) `--ref-ld-chr` was rewritten, baseline kept first, custom prefix changed; (b) filtered chr1 LD score header drops `NEGCTRL_HLA_IMMUNEL2` (13 cols not 14); (c) M / M_5_50 lose the matching index 8 entry (10 values not 11); (d) `--invert-anyway` is NOT in cmd (REVERTED); (e) `--overlap-annot` still present; (f) tmp dir cleaned up after the call returns.
   - **NEW** `test_strip_annotation_for_partitioned_h2_unit` — 3-chrom round-trip on `_strip_annotation_for_partitioned_h2` directly.
   - **NEW** `test_strip_annotation_raises_when_drop_annotation_absent` — defensive guard.
   - **NEW** `test_strip_annotation_skipped_when_no_custom_prefix` — sanity guard for single-prefix `ref_ld_chr`.
   - New helper `_write_custom_ldscore_fixture(prefix, chrom, snps_per_chrom)` produces the 11-annotation fixture matching the production custom_pathway header.

### Not changed

- `data/reference/ldsc/baselineLD.*` files — untouched.
- `results/pathway/ldsc_partitioned/ld_scores/custom_pathway.*.l2.ldscore.gz` — untouched (still has all 11 annotations including NEGCTRL_HLA_IMMUNE).
- `results/pathway/ldsc_partitioned/annotations/custom_pathway.*.annot.gz` — untouched (annotation source files preserved for LDSC-SEG and any other downstream).
- No new Snakemake rule, no rerun cascade.
- Launch13 LSF job 748649 — NOT touched.

## 2026-04-18T22:05Z — Verification

### 1. Pure-Python unit tests (Pytest)

```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/phase5/test_launch10_regressions.py -v
17 passed in 12.93s
```

All 14 prior regression tests + 3 new tests + 1 rewritten test pass on the first run. No flakes.

### 2. Full Phase 5 test suite

```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/phase5/ --deselect tests/phase5/test_ldsc_seg.py::TestLdctsFormat::test_ldcts_fix_paths -q
116 passed, 1 deselected in 6.53s
```

Prior baseline was 113 passed, 1 deselected. Net +3 = the 3 new tests added. The deselected test is the same pre-existing one (fix_ldcts_paths absolute path issue, unrelated to Launch10 scope).

### 3. End-to-end integration test on real production chr1..22 LD scores

A self-contained Python script ran `_strip_annotation_for_partitioned_h2` against the actual `results/pathway/ldsc_partitioned/ld_scores/custom_pathway.*.l2.ldscore.gz` files (all 22 chromosomes), then re-ran the asthma_EUR post-merge SVD against the filtered triplet:

```
== Filter result ==
  chromosomes_processed: 22
  dropped: ['NEGCTRL_HLA_IMMUNE']
  kept (n=10): [
    'CUSTOM_INSULIN_SIGNALINGL2', 'CUSTOM_APPETITE_REGULATIONL2',
    'CUSTOM_GLUCOSE_METABOLISML2', 'CUSTOM_FATTY_ACID_METABOLISML2',
    'CUSTOM_INFLAMMATIONL2', 'CUSTOM_VASCULAR_TONEL2',
    'CUSTOM_LIPID_TRANSPORTL2', 'CUSTOM_ENERGY_STORAGEL2',
    'NEGCTRL_COSMETICL2', 'NEGCTRL_BLOOD_GROUPL2'
  ]

== Post-merge SVD (asthma_EUR replication) ==
  X_filt shape: (967534, 107)
  cond(X_filt) = 4.968857e+03   ← was 1.161518e20 before fix
  σ_max = 1.031855e+06, σ_min = 2.076645e+02
  rank @ σ_rel > 1e-10 = 107/107   ← was 107/108 before fix (rank-1 deficient)

== INTEGRATION PASSED ==
```

**cond drops by 17 orders of magnitude** (1.16e20 → 4.97e3), full rank, well below LDSC's 1e5 hard threshold. `--invert-anyway` is mathematically unnecessary and the `np.linalg.solve(xtx, xty)` call at jackknife.py:376 will succeed.

### 4. Snakemake DAG dry-run (--nolock, read-only against live Launch13 workspace)

```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
    --dry-run --nolock --rerun-triggers mtime -s Snakefile all_pathway

Job stats:
job                           count
--------------------------  -------
ldsc_partitioned_h2               8     ← all trait × ancestry, gap to close
ldsc_seg_chromatin                2     ← partial (Launch13 still running)
ldsc_seg_gene_expr                1     ← partial
hess_compare_pleio                4
hess_aggregate                    1
ldsc_aggregate_h2                 1
ldsc_seg_shared_tissues           1
permutation_null_genesets         1
permutation_aggregate             1
gprofiler_enrichment              1
validate_negative_controls        1
extract_tier_ab_genes             1
assign_tiers                      1
aggregate_pathway_results         1
all_pathway                       1
total                            26
```

**No new rules added to DAG** (column-drop is in-process). The 8 `ldsc_partitioned_h2` jobs are exactly the gap that Launch14 must close. No phantom reruns triggered (mtime-based rerun-triggers don't see the new code change for already-resolved outputs — and there are no resolved partitioned_h2 outputs anyway).

### 5. Code-level audit

- `grep "invert-anyway\|invert_anyway" src/python/run_ldsc_partitioned.py` → only docstring/comment references (3 hits in lines 625, 639, 710); no flag in cmd.
- The new constant `PARTITIONED_H2_DROP_ANNOTATIONS` is the single source of truth for which annotations are dropped, exposed via the `drop_annotations` keyword argument for any future test override.

### Why this fix doesn't break OSF pre-registration

NEGCTRL_HLA_IMMUNE is preserved in:
- `data/reference/ldsc/...` — untouched (not our file anyway).
- `results/pathway/ldsc_partitioned/annotations/custom_pathway.*.annot.gz` — untouched (LDSC-SEG and any future custom analysis still see it).
- `results/pathway/ldsc_partitioned/ld_scores/custom_pathway.*.l2.ldscore.gz` — untouched.
- The negative-control claim from the partitioned-h2 step survives at 2-of-3 strength (NEGCTRL_COSMETIC, NEGCTRL_BLOOD_GROUP) — the design conflict with the canonical Finucane-2015 weight file is a published-method footnote, not an OSF amendment trigger.

Methods narrative for the eventual paper / OSF amendment text (one sentence, embedded in the rule docstring):
> NEGCTRL_HLA_IMMUNE is excluded from the partitioned-h2 step because it is HLA-region-specific by construction and the canonical Finucane-2015 weight file (weights.hm3_noMHC) excludes MHC by design; the inner-join in S-LDSC's read_ld_and_sumstats zeros the column on the regression-eligible SNP set, producing a singular X^T X. The annotation is preserved in the source LD score files for use by other consumers (LDSC-SEG cell-type-specific analysis, etc.).

## 2026-04-18T22:05Z — Status update

status: **fixed_pending_launch14_validation**

The code-level fix is complete and correct (unit + integration tests pass; SVD on real data confirms cond drop from 1.16e20 → 4.97e3). The session is NOT yet `resolved` because end-to-end validation requires:

- Launch13 (LSF job 748649) to drain.
- Launch14 to fire against the patched `src/python/run_ldsc_partitioned.py`.
- Confirmation that all 8 `ldsc_partitioned_h2` jobs (4 EUR + 4 AFR) produce `.results` files with the expected 10 custom annotations + ~97 baselineLD entries.

Carter to confirm "fix verified end-to-end" after Launch14, at which point this debug session moves to `resolved` and is appended to the knowledge base.

### Eliminated (this fix iteration)

- hypothesis: `--invert-anyway` is the canonical fix per LDSC FAQ (the previous ffbabce conclusion)
  evidence: production log `asthma_EUR_pathway_h2.log` 2026-04-18 19:59:47 — flag honored, but `np.linalg.solve(xtx, xty)` still raises LinAlgError 4 lines later. SVD evidence in `svd_postmerge_check.py` shows the post-merge X^T X is structurally rank-1 deficient (σ_min = 8.88e-15, smallest singular vector = +1.000 on NEGCTRL_HLA_IMMUNEL2). Forced inversion does not recover information that is structurally absent. The flag is now reverted.
  timestamp: 2026-04-18T22:00Z

- hypothesis: Option A (parallel `ldsc_compute_ld_scores_partitioned_h2` rule) is the cleanest implementation
  evidence: While conceptually clean, Option A adds 22 ldscore-compute jobs (~5 min each, ~2 h cluster time) and changes the DAG topology. The DAG change risk against the live Launch13 workspace is non-trivial (mtime-based rerun-triggers respect file mtimes but param hash changes can still cascade). Option B is strictly cheaper, has zero DAG impact (no new outputs, no new rules), and isolates the fix to the file containing the bug. Chose B.
  timestamp: 2026-04-18T22:00Z

- hypothesis: LDSC has a native `--annot-include / --annot-exclude` flag that we could use
  evidence: `grep -E '(annot-(include|exclude))' tools/ldsc/ldsc.py` returns 0 matches; LDSC's argparse parser has no per-column inclusion/exclusion flag. Falling back to in-process file rewrite is unavoidable.
  timestamp: 2026-04-18T22:00Z
