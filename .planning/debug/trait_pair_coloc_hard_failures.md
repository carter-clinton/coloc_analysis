---
session: trait_pair_coloc_hard_failures
status: fixed
opened: 2026-04-21
closed: 2026-04-21
stage: recovery_plan_stage_1d
parent_plan: .planning/phases/02-3-way-qtl-colocalization/RECOVERY_PLAN.md
predecessor_session: .planning/debug/multitrait_coloc_empty.md
hypothesis: Cross-trait SNP naming drift inside coloc.susie() — port fix from commit 931a9c8
next_action: Awaiting human verification (see Resolution).
---

## Current Focus

hypothesis: CONFIRMED. The 4 failing pairs are exactly the set `bmi × {hypertension, stroke, t2d}`. The `bmi.EUR.tsv.bgz` sumstats carry real rsids in SNP_ID (e.g. `rs2073813`), while `hypertension.EUR`, `stroke.EUR`, and `t2d.EUR` carry `chr:pos` strings (e.g. `1:752566`). `run_susie_rss.R:522-529` then hands `coloc:::annotate_susie` two different naming vocabularies. The resulting `.fit.rds` files have `colnames(alpha)` in different alphabets, and `intersect()` on them returns 0 variants. coloc.bf_bf returns a stub with NULL $summary; then `ret$summary[, :=(...)]` in `coloc.susie` errors.

test: Port rsid-aware alignment from commit 931a9c8 into `src/snakemake/scripts/run_coloc_susie.R`. Strategy: load the region sumstats for both traits, build a rsid ↔ chr:pos lookup from CHR/POS/SNP_ID columns, and rewrite each fit's colnames(alpha)/names(pip)/names(cs) to a common key (`chr:pos`, chosen because it's build-invariant and derivable from both sumstats when rsid is absent).

expecting: All 4 pairs should fire to coloc.susie without error. Scientific outcome unknowable a priori — some may land as `status="success"` with PP.H4 > 0, others may land as `status="no_signal"` if the rewritten credible sets don't pairwise-overlap.

next_action: Implement the alignment. Re-fire all 4 pairs. Re-run summarize + assign_tiers.

## Symptoms

expected: Each of the 4 manifest pairs should produce a JSON at `results/multitrait/coloc_susie/{pair_id}.json`, either `status="success"` with numeric PP.H4, or `status="no_signal"` / `status="error"` with diagnostic info.

actual: Zero JSON output for these 4 pairs on the 2026-04-20 first-production run. The 54/58 other pairs produced JSONs (51 no_signal + 3 success), so the rule and its infrastructure work — the crash is pair-specific. Failing pairs:
- APOE_19q13__EUR__bmi_vs_hypertension
- FTO_16q12__EUR__bmi_vs_t2d
- SH2B3_12q24__EUR__bmi_vs_hypertension
- SH2B3_12q24__EUR__bmi_vs_stroke

errors: Stage 1 debugger attributed to `run_susie_rss.R:520-529` choosing rsid vs chr:pos independently per trait. Variant-ID format mismatch between the two SuSiE fits causes coloc.susie() to error when aligning.

reproduction: `snakemake --cores 2 --use-conda --rerun-triggers=mtime results/multitrait/coloc_susie/SH2B3_12q24__EUR__bmi_vs_hypertension.json`

started: 2026-04-20 T1 Phase 2 first-production run. First end-to-end run of trait-pair coloc.susie; had never produced output before Stage 1 unblocking (commit 604938b).

## Evidence

- timestamp: 2026-04-21 step 1 (reference-commit diff review)
  checked: `git show 931a9c8` — the QTL coloc rsid fix
  found: Fix pattern is: detect rsid column → prefer rsid as match key → strip sentinel `"null"` colnames (appended by `coloc::annotate_susie` when L > n_cs) → pass aligned SNP names through to `coloc`'s dataset list. Applied to `src/snakemake/scripts/run_qtl_coloc.R`.
  implication: The ref fix worked by aligning two DIFFERENT object types (SuSiE fit vs TSV) via rsid. Our case aligns two SuSiE fits, so the fit-side rewrite strategy is analogous but slightly different in mechanics — we can't rely on a "rsid column" being present in the fit; we need to re-derive it from source sumstats.

- timestamp: 2026-04-21 step 2 (direct fit inspection — SH2B3 bmi vs hypertension)
  checked: `readRDS("results/fine_mapping/susie/bmi.EUR.SH2B3_12q24.fit.rds")` and `.../hypertension.EUR.SH2B3_12q24.fit.rds`
  found:
    - bmi.EUR.SH2B3_12q24: 172 variants, colnames like `rs7961935`, `rs7978821`, `rs3184504` (CS1 hit)
    - hypertension.EUR.SH2B3_12q24: 601 variants, colnames like `12:111400006`, `12:111400116`, `12:111865049` (CS1 hit)
    - `intersect(colnames(bmi$alpha), colnames(hyp$alpha)) == 0`
    - Both fits are converged, have non-zero credible sets (1 and 10 respectively)
  implication: Confirmed the two fits use completely different naming alphabets. The data is there to colocalize (same chromosome region, ~hundreds of variants each) — they just can't find each other via string match.

- timestamp: 2026-04-21 step 3 (pattern check across all 4 failing pairs + control)
  checked: All four failing pairs + the SH2B3 hypertension_vs_stroke success control
  found:
    - APOE_19q13 bmi_vs_hypertension: bmi=rsid(1319), hyp=chr:pos(5245), intersect=0
    - FTO_16q12 bmi_vs_t2d: bmi=rsid(701), t2d=chr:pos(5370), intersect=0
    - SH2B3_12q24 bmi_vs_stroke: bmi=rsid(172), stroke=chr:pos(634), intersect=0
    - SH2B3_12q24 hypertension_vs_stroke (CONTROL): both=chr:pos, intersect=594 → succeeded (PP.H4=1.0)
  implication: 100% of hard failures are bmi-paired. 100% of non-bmi pairs succeed (or fail gracefully to no_signal). The naming mismatch is the sole crash mechanism.

- timestamp: 2026-04-21 step 4 (sumstats-source confirmation)
  checked: Column 7 (SNP_ID) of each harmonized sumstats file
  found:
    - bmi.EUR.tsv.bgz: SNP_ID = real rsid (`rs2073813`)
    - asthma.EUR.tsv.bgz: SNP_ID = real rsid (`rs755466349`)
    - hypertension.EUR.tsv.bgz: SNP_ID = `chr:pos` string (`1:752566`)
    - stroke.EUR.tsv.bgz: SNP_ID = `chr:pos` string (`1:729679`)
    - t2d.EUR.tsv.bgz: SNP_ID = `chr:pos` string (`1:13668`)
  implication: Root cause is upstream of SuSiE — it's in the per-trait sumstats ingestion. bmi + asthma have rsid-populated SNP_ID; hypertension/stroke/t2d have chr:pos-populated SNP_ID. `run_susie_rss.R:522-529` honestly reflects this: takes SNP_ID as the naming source when it's non-empty. The drift is inherent to the heterogeneous source catalog. All sumstats have CHR and POS columns — which means `chr:pos` is a universally derivable common key.

- timestamp: 2026-04-21 step 5 (coloc.susie crash reproduction)
  checked: `coloc::coloc.susie(fit_bmi, fit_hyp)` inside Rscript with both SH2B3 fits loaded
  found: Errors with `"Check that is.data.table(DT) == TRUE. Otherwise, :=, ':='(...) and let(...) are defined for use in j, once only and in particular ways."` — exactly the Stage 1 prediction (coloc.bf_bf returns a stub with NULL $summary; the subsequent `ret$summary[, :=(...)]` call errors because the NULL is not a data.table).
  implication: The rule-level failure mode is a bare R error exit — no JSON is written. The fix must either (a) emit an error JSON on this specific error, (b) rewrite variant names before calling coloc.susie so the crash never happens, or (c) both. We will do (b) as the primary fix (it's a real recovery, not just a diagnostic band-aid) and add light (a) for defense-in-depth.

- timestamp: 2026-04-21 step 6 (fit-level rewrite strategy — chosen approach)
  checked: What metadata is available inside the `.fit.rds` to drive an alignment
  found: Fit contains `$alpha` (L × n_snps matrix, colnames = current SNP names), `$pip` (named vector), `$sets$cs` (named integer positions). No chr/pos/rsid table is embedded. Therefore we must re-derive the mapping from an external source — the original sumstats files (`data/processed/sumstats_harmonized/{trait}.{ancestry}.tsv.bgz`), which all contain CHR, POS, SNP_ID. Manifest already carries trait_a/trait_b/ancestry/base_region/path_a/path_b — path_a/b point at the Phase 1 susie JSONs from which we can derive the sumstats path (or we can resolve it directly from config).
  implication: Plan: in `run_coloc_susie.R`, before calling coloc.susie, (1) read each fit's sumstats-source path from its companion `.json` (same basename); (2) for the region's chrom/start/end, load CHR, POS, SNP_ID from the sumstats (bgzf-indexed, single-region read is cheap); (3) build a mapping `current_name → chr:pos` keyed on SNP_ID; (4) rewrite colnames(alpha), names(pip), names(sets$cs) to the common `chr:pos` key in both fits; (5) drop sentinel `"null"` colnames; (6) call coloc.susie on the rewritten fits.

## Eliminated

<!-- Appended as hypotheses are disproved -->

## Resolution

root_cause: Stage 1 debugger's Stage-1b carryover hypothesis was confirmed with direct fit inspection. `run_susie_rss.R:522-529` picks per-fit SNP names based on the populated-ness of the source sumstats' `SNP_ID` column: real rsids when present, else `chr:pos`. The harmonized sumstats catalog is heterogeneous in this respect — `bmi.EUR` and `asthma.EUR` carry real rsids; `hypertension.EUR`, `stroke.EUR`, and `t2d.EUR` carry `chr:pos` strings. Every `bmi × {hypertension,stroke,t2d}` pair therefore produces two SuSiE fits with zero-overlap colnames in `$alpha`, `$lbf_variable`, etc. `coloc::coloc.bf_bf` returns an empty stub (`data.table(nsnps=NA)`, no `$summary` field); `coloc::coloc.susie` then crashes on `ret$summary[, :=(...)]` against NULL, which propagates up as a bare R error and aborts the rule before any JSON is written. All 4 hard failures are exactly the `bmi × {hypertension,stroke,t2d}` pairs on EUR regions that survived the tier3 gate.

fix: Ported the rsid-aware alignment pattern from commit 931a9c8 (QTL coloc) to `src/snakemake/scripts/run_coloc_susie.R`. Strategy differs in mechanics because both inputs here are SuSiE fits (not a fit + TSV), so we drive the rewrite from the source sumstats. For each fit:
  1. Locate the companion `.json` (same basename as `.fit.rds`) written by `run_susie_rss.R` — carries `sumstats` path, `chrom`, `start`, `end`.
  2. Load CHR, POS, SNP_ID for that chrom/start/end window from the harmonized sumstats (`data.table::fread` via `R.utils` gz plugin — already added to `r_coloc` env in commit `a7d4eac`).
  3. Build a `SNP_ID → chr:pos` map and rewrite `colnames(fit$alpha)`, `colnames(fit$lbf_variable)`, `colnames(fit$mu)`, `colnames(fit$mu2)`, `names(fit$pip)`, and per-CS `names(fit$sets$cs[[i]])` to chr:pos keys.
  4. Drop columns with no sumstats map (keeps coloc's `"null"` sentinel untouched; preserves CS-referenced columns with original names if unmapped).
  5. Rebuild CS integer indices against the column-pruned matrices.
  6. Call `coloc.susie` on the rewritten fits, wrapped in `tryCatch`. If it still errors or returns NULL, emit a structured error JSON with `status="error"` rather than crashing out (defense-in-depth).

Also added:
- `status="no_posterior"` label for pairs where `coloc.bf_bf` returns valid rows (numeric `nsnps`/`hit1`/`hit2`) but NA PPs due to the `overlap too small between datasets: too few snps with high posterior` warning. Previously the code would `which.max(NA_vec)` and emit a broken best-row.
- Relaxed posterior-sum QC to only check complete (non-NA) rows, so the "no_posterior" path doesn't throw a sum-deviation warning.

verification:
  - **Criterion 1 (all 4 JSONs land):** PASS. All 4 previously-failing pair IDs now have JSON output:
    - `APOE_19q13__EUR__bmi_vs_hypertension.json` (status=no_posterior, 20 pairs)
    - `FTO_16q12__EUR__bmi_vs_t2d.json` (status=no_posterior, 14 pairs)
    - `SH2B3_12q24__EUR__bmi_vs_hypertension.json` (status=success, **PP.H4=1.0**, hit=12:111884608)
    - `SH2B3_12q24__EUR__bmi_vs_stroke.json` (status=success, PP.H3=0.9986, PP.H4=0.0001)
  - **Criterion 2 (valid status field):** PASS. Statuses: 2 success + 2 no_posterior. Both are non-crash outcomes with populated schema.
  - **Criterion 3 (report PP.H4 for successes):** `SH2B3 bmi↔hypertension PP.H4=1.0` (strongly colocalized, NEW finding); `SH2B3 bmi↔stroke PP.H4=0.0001` (distinct signals, PP.H3=0.9986).
  - **Criterion 4 (assign_tiers runs cleanly):** PASS. No KeyError. Output: `results/qtl_coloc/tier_assignments.tsv` (12 rows), `pph4_threshold_sweep.tsv` (4 rows).
  - **Criterion 5 (tier transitions):** No tier transitions occurred. SH2B3_12q24 EUR now shows `best_gwas_pph4=1.0` (reflecting the strongest of 2 success pairs at that locus), but `best_qtl_pph4=0.0` so it remains Tier C. This is scientifically correct: Tier A requires both GWAS-coloc AND QTL-coloc at the same region, and no QTL signal survived coloc at SH2B3. The new evidence strengthens confidence in the SH2B3 GWAS locus without upgrading its overall Tier.

**Scientific bonus (not requested but surfaced):** The 3 SH2B3_12q24 EUR success pairs triangulate two distinct causal signals ~26 kb apart: hypertension and bmi colocalize at `12:111884608` (PP.H4=1.0); hypertension and stroke colocalize at `12:111910219` (PP.H4=1.0); but bmi and stroke do NOT colocalize (PP.H3=0.999, PP.H4<0.001) because they map to different signals. This is a biologically-meaningful 3-trait fine-mapping pattern consistent with two independent genetic effects at SH2B3.

files_changed:
- src/snakemake/scripts/run_coloc_susie.R (major edit: added rewrite_fit_to_chrpos() machinery; added tryCatch + error JSON + no_posterior status; relaxed PP-sum QC to skip NA rows).
- .planning/debug/trait_pair_coloc_hard_failures.md (this file, investigation log).
