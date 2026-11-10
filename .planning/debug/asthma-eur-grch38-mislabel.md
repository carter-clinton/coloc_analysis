---
status: fixing
trigger: "asthma-eur-grch38-mislabel: pinned data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz (sha256 22b28075...) is GRCh38 but labelled GRCh37 (BUILD column + config/ta_r4/data_sources.yaml)"
created: 2026-11-10
updated: 2026-11-10
---

## Current Focus

hypothesis: CONFIRMED — asthma.EUR is GBMI GRCh38, never lifted; legacy harmonizer stamps the target build
test: Carter approved items 1-3 (claims HOLD). Strand-corrected lifts pinned for the r4 route; measurement fits outside the workflow (measure_asthma_fix/) with rebuilt catalogs
expecting: catalog contamination ~0; asthma.EUR panel-match like controls; non-asthma fits unchanged by the catalog swap
next_action: catalog rebuild (control first) -> 144 measurement fits -> checkpoint on legacy-route / repro-arm overwrite and the missing Slurm runner

## Symptoms

expected: asthma.EUR positions are GRCh37 like every other Track A / ta-r4 harmonized file.
actual: rsid join (orchestrator, 2026-11-10): vs asthma.AFR.grch38_backup 100.00% same chr+pos (11,011,821 shared); vs lifted asthma.AFR 0.86% same pos; vs bmi.EUR GRCh37 0.91% same pos. Anchors rs429358 19:44908684, rs7412 19:44908822, rs9939609 16:53786615 = GRCh38. BUILD column says GRCh37 (also wrong in AFR grch38 backup).
errors: none — silent mislabel.
reproduction: rsid-position joins (scratchpad *.rs files).
started: GBMI release is GRCh38; liftover_asthma_afr.sh lifted only AFR. asthma.EUR.tsv.bgz mtime Apr 16 2026; .tbi Feb 11 2026 (stale index).

## Eliminated

## Evidence

- timestamp: 2026-11-10
  checked: src/snakemake/rules/sumstats.smk harmonize_sumstats -> src/legacy/region_analysis/scripts/harmonize_sumstats.py:324
  found: BUILD column = `--build {config.genome_build}` (the TARGET build, GRCh37); the harmonizer never lifts and never reads a source build. config/datasets.yaml gbmi_asthma declares no build. M1 rule harmonize_gbmi_asthma (with b38->b37 lift) writes asthma.*.GBMI.2022.GRCh37.tsv.bgz, which does not exist on disk.
  implication: SOURCE of the label: any GRCh38 dataset passed through this harmonizer is stamped GRCh37.
- timestamp: 2026-11-10
  checked: fit JSONs data/r4/results/*/fine_mapping/susie (scratchpad fit_table_eur.tsv); 4 repro arms x 12 EUR regions; no production-arm fits exist yet
  found: repro_routeC asthma.EUR panel-overlap fraction ld_overlap/n_window: APOL1 45/3913=0.012, MC4R 16/4571=0.003, SH2B3 147/3818=0.038, FTO 1803/5106=0.353, CXADR 4930/13915=0.354; 6 regions too_many_variants (window 17k-119k); BMI_Xq24 no_variants. Controls same region (bmi/htn/stroke EUR): 0.97-1.00. t2d.EUR (also dense) 0.26-0.44. All joins snp_id (allele_aware False). CS reported by asthma.EUR: APOL1 1, MC4R 1, SH2B3 1, FTO 6, CXADR 10 (routeC).
  implication: every existing asthma.EUR fit used a window shifted by the GRCh37->38 offset; CS positions written are GRCh38.
- timestamp: 2026-11-10
  checked: claims (STATE.md quick 260424-p1b, 260425-ie0; OSF DRAFT (h); measure_fit_eligibility REGRESSION_KEYS)
  found: Track A Fig 1B panel 1 = "SH2B3 12q24 asthma.EUR flagship (only non-collapsed real-LD CS, 1 CS / 140 variants)"; Fig 3 SH2B3 forest row asthma 0->1; Fig3 caption cites asthma x t2d no_signal. OSF DRAFT pins asthma EUR sha 22b28075 and (h) names L=10 asthma fits in the SH2B3 9/9 reproduction. REGRESSION_KEYS includes (A3_1kg, asthma, EUR, PYHIN1_1q23). SH2B3 PP.H4=1.0 headline pairs (bmi-htn, htn-stroke, htn-t2d) do NOT involve asthma.
  implication: headline PP.H4 anchor unaffected; Fig 1B panel 1 + Fig 3 asthma row + every asthma.EUR coloc row are built on mislocated data.
- timestamp: 2026-11-10
  checked: new src/python/ta_r4/sumstats_build.py over 658 anchors (1kG GRCh37 ID+SNV verified, GBMI native GRCh38 pos)
  found: hits GRCh37/GRCh38: asthma.EUR 1/657; asthma.AFR 657/0; bmi.EUR 658/0; hypertension.EUR 646/0; stroke.EUR 656/0; stroke.AFR 356/1; t2d.EUR 658/3; t2d.AFR 658/0. tests/ta_r4/test_sumstats_build.py RED on sumstats_asthma_EUR only (assert 'GRCh38' == 'GRCh37'), 7 passed.
  implication: only asthma.EUR is mislabelled among the 8.
- timestamp: 2026-11-10
  checked: legacy variant catalogs data/r4/ld/variants_legacy/<region>.tsv (r4_catalog rule = union of the 8 Track A sumstats in the window) vs pinned / lifted asthma.EUR window keys (chr:pos:REF:ALT, either orientation); scratchpad region_impact.tsv
  found: catalog contains ~99.5% of the PINNED (GRCh38) asthma window keys (MC4R 5361/5374, SH2B3 4439/4454, APOL1 4663/4674); BMI_Xq24 asthma contributes 35 (CHR 23 vs X). Rsids shared between pinned and correct (lifted) windows: MC4R 0/6228, APOL1 68/3947, SH2B3 957/4681, FTO 4839/6063.
  implication: catalogs (legacy + r4) carry asthma GRCh38 positions as spurious variants (catalog is only a fit-time restriction / k2d identity variant list; 1kG/UKB panels are built from plink/tiles, not from it). At MC4R and APOL1 the existing asthma fits contain essentially none of the correct-window variants.
- timestamp: 2026-11-10
  checked: liftover (Slurm 1797696) via new src/legacy/region_analysis/scripts/liftover_sumstats_hg38_to_hg19.sh = AFR method (UCSC liftOver md5 e40fe17f, hg38ToHg19 chain md5 ff3031d9, 1-bp BED keyed by line, default minMatch)
  found: input 27,892,702 = lifted 27,849,453 + unmapped 43,249 (all "#Deleted in new"); lifted = kept 27,845,280 + non-canonical contig 1,187 + chromosome change 2,986 (dropped, logged in work/dropped_rows.tsv; AFR lift KEPT both kinds: 1,005 contig rows, 147 X / 19 Y). 208 duplicate CHR:POS:REF:ALT keys after lift (work/duplicate_keys.txt), kept. Output data/r4/sumstats/asthma.EUR.grch37_lifted.tsv.bgz sha256 272a05006376c25aebe7939ea24d5cb7a1bfb147feed0cb9990b7173ee20af60, 27,845,280 rows.
  implication: 99.83% retained.
- timestamp: 2026-11-10
  checked: verification (Slurm 1797818, outputs data/r4/sumstats/liftover_asthma_EUR/verify/)
  found: (identity) md5 of sorted non-coordinate columns 3-13 of lifted == original minus dropped rows (b33ae578 both). (rsid) lifted vs lifted asthma.AFR: 10,657,486 shared, 10,657,486 same chr+pos (100.000000%, 0 non-matches); lifted vs GIANT BMI native GRCh37 (independent of liftOver): 1,852,819 shared, 100.000000%. NEGATIVE CONTROL unlifted: 91,304/10,658,464 (0.857%) and 16,907/1,853,501 (0.912%). Anchors rs429358 19:45411941, rs7412 19:45412079, rs9939609 16:53820527 present; 19:44908684 absent. (REF vs 1kG GRCh37, autosomes) lifted EUR at a 1kG site 21,330,654: exact 98.78%, swapped 0.18%, complement 0.11%, complement_swapped 0.002%, mismatch 0.93%; AFR-lift baseline 19,386,931: 99.56 / 0.14 / 0.086 / 0.002 / 0.21; unlifted EUR: only 1,015,009/27,096,526 (3.7%) at a 1kG site, exact 284,442 (28% of those). Build test: lifted 657/0 GRCh37.
  implication: lift correct by a non-circular identity; REF consistent with GRCh37 at AFR-like rates (EUR mismatch 0.93% vs 0.21% characterized separately).
- timestamp: 2026-11-10
  checked: asthma.EUR.tsv.bgz.tbi (Feb 11) vs fresh index of the same bytes
  found: md5 differ (c9760dac vs 3e601ae0) but tabix query output identical on 3 test regions; AFR stale .tbi query == full scan on SH2B3 window.
  implication: stale-index flag is real (mtime/bytes) but queries agree; low risk.
- timestamp: 2026-11-10
  checked: chr22 non-matches vs 1kG (verify/mm/), and strand-aware liftOver of the same BED (verify job 1798071, strand/)
  found: chr22 EUR 2,824 non-matching of 368,205 (AFR 593/263,717): 1,913 bi-allelic-1kG SNVs, of which 1,839 share the 1kG REF with a different ALT and 1,828 have EAF<0.01 (rare tri-allelic sites absent from 1kG), 17 complements. Strand-aware lift: identical mapping; 44,652 of 27,849,453 lifted rows land on minus-strand chain blocks (REF/ALT left uncomplemented, as in the AFR lift) = the genome-wide complement classes (24,272 + 482 at 1kG sites).
  implication: excess EUR mismatch is rare multi-allelic content, not lift error. 44,652 minus-strand rows carry opposite-strand alleles in BOTH asthma lifts — decision item.
- timestamp: 2026-11-10
  checked: r4 catalogs data/r4/ld/variants_r4 (31 regions) vs positions of the other 7 Track A files; AFR661/AFR504 panel .bim (built from r4 catalog positions)
  found: positions present ONLY because of pinned asthma.EUR: FTO 5,458/13,456; MC4R 5,298/13,929; SH2B3 4,387/10,483; APOL1 4,614/9,131; HLA 133,483/305,364 (39-50% of every region's catalog). Lifted asthma positions missing from the catalog: 984-22,818 per region. AFR 1kG panels: 0-16 variants per region at those positions (negligible). UKB native panels (catalog positions + allele-set match) NOT measured.
  implication: catalogs must be rebuilt after a repoint (and any catalog-derived panel: UKB native, k2d identity, AFR 1kG), which moves their sha pins.
- timestamp: 2026-11-10
  checked: strand-aware lift (Slurm 1798361 EUR, 1798362 AFR from asthma.AFR.grch38_backup) + verify 1798566 (liftover_strand/verify/)
  found: EUR 27,892,702 = 43,249 unmapped + 1,187 contig + 2,986 chr-change + 1,677 minus-strand non-SNV dropped + 27,843,603 kept (41,167 minus-strand SNVs complemented, 7,000 of them A/T|C/G, listed). AFR 20,274,980 = 39,441 + 1,006 + 1,716 + 912 + 20,231,905 kept (22,936 complemented, 3,948 palindromic). Independent awk re-derivation (complement minus rows, drop dropped rows) md5 == output for both (EUR ebab3e70, AFR dd023ae4). Exact vs 1kG: EUR 98.7805% -> 98.9144%, AFR 99.5630% -> 99.6658%; minus-strand subsets EUR 2.03% -> 94.71%, AFR 0.89% -> 96.85%; residual complement class 24,272 -> 343 (EUR), 16,645 -> 61 (AFR). Same chr+pos: EUR vs AFR 10,992,346/10,992,346, EUR vs GIANT BMI 1,852,819/1,852,819, AFR vs GIANT BMI 1,844,557/1,844,557. NEGATIVE CONTROL: complementing 258,878 plus-strand SNVs (POS%100==0) drops EUR exact to 97.9854% and complement class to 168,632. sha256 EUR 49edfc54..., AFR 8828df14....
  implication: strand step correct; accepted.
- timestamp: 2026-11-10
  checked: pinned asthma.AFR.tsv.bgz (19,695,660 rows) vs new AFR lift (20,231,905) vs backup (20,274,980), keyed on CHR,POS,BETA,SE,P,EAF,N,SNP_ID (afr_diff/)
  found: pinned-only 3,634 = exactly the new lift's contig + chr-change + minus non-SNV drops; new-only 539,879 = all CHR 23. Every pinned row's values occur in the backup.
  implication: liftover_asthma_afr.sh wrote "chr23" into the BED (absent from the chain), so the pinned AFR silently lost all of chrX. The new AFR keeps chrX as CHR 23 (BMI_Xq24 region is "X": every trait is no_variants there anyway, pre-existing).
- timestamp: 2026-11-10
  checked: rebuild of legacy catalog APOL1 from the ORIGINAL 8 files with smoke_dev python
  found: sha 6dd7c3b2 != pinned 1cd2ffd0 (allele case and same-position row order differ: unstable sort/dedup is pandas-version dependent)
  implication: catalogs must be rebuilt with the workflow env python_stats (8f7292f9...); control rerun with it.

## Resolution

root_cause: GBMI 2021 asthma is GRCh38. src/legacy/region_analysis/scripts/harmonize_sumstats.py stamps BUILD = config genome_build (GRCh37) with no source-build check and no liftover; liftover_asthma_afr.sh lifted only AFR, so asthma.EUR.tsv.bgz kept GRCh38 coordinates under a GRCh37 label, copied into config/ta_r4/data_sources.yaml (build: GRCh37) and the sha pin.
fix: (strand + repoint, after Carter approval) liftover script complements minus-strand SNVs / drops minus-strand non-SNVs; new pins data/r4/sumstats/asthma.{EUR,AFR}.grch37_lifted_strand.tsv.bgz; paths.sumstats_path routes r4-route asthma to them; data_sources.yaml + sumstats_r4_sha256.tsv updated. (earlier, landed pre-checkpoint) harmonizer refuses when the dataset declares source_build != --build (config/datasets.yaml gbmi_asthma source_build: GRCh38); GRCh37 lift written as a NEW file data/r4/sumstats/asthma.EUR.grch37_lifted.tsv.bgz; position-measured build test over the 8 Track A files. NOT done (checkpoint): repoint paths.sumstats_path / data_sources.yaml / sha pin; any re-fit; any OSF/claim edit.
verification: see Evidence (identity, rsid 100% vs native GRCh37, negative controls, REF check, RED->GREEN tests).
files_changed: [src/legacy/region_analysis/scripts/harmonize_sumstats.py, src/legacy/region_analysis/scripts/dataset_config.py, config/datasets.yaml, src/legacy/region_analysis/scripts/liftover_sumstats_hg38_to_hg19.sh, src/python/ta_r4/sumstats_build.py, tests/ta_r4/fixtures/build_anchors_grch37_grch38.tsv, tests/ta_r4/test_sumstats_build.py, tests/ta_r4/test_harmonizer_source_build.py]
