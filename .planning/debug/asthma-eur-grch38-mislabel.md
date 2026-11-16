---
status: awaiting_human_verify
trigger: "asthma-eur-grch38-mislabel: pinned data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz (sha256 22b28075...) is GRCh38 but labelled GRCh37 (BUILD column + config/ta_r4/data_sources.yaml)"
created: 2026-11-10
updated: 2026-11-16
---

## Current Focus

hypothesis: CONFIRMED — asthma.EUR is GBMI GRCh38, never lifted; legacy harmonizer stamps the target build
test: Carter 2026-11-16 chose A (repro arms keep original inputs; corrected inputs -> production arms only; disclosure DRAFT), B (Slurm profile for bin/r4_fire.sh, lands before the W4a lock and changes the fire surface the lock covers), C (BMI legacy-fit non-reproducibility, after the rebuild)
expecting: rebuilt variants_r4 byte-identical to measure_asthma_fix/catalogs/r4; contamination 0; panels pass manifest checks; live pin test RED -> GREEN after manifest update
next_action: CHECKPOINT — decide how the Slurm fire surface pins the OpenBLAS kernel (constraint cascadelake vs OPENBLAS_CORETYPE) before the W4a lock

## Symptoms

expected: asthma.EUR positions are GRCh37 like every other Track A / ta-r4 harmonized file.
actual: rsid join (orchestrator, 2026-11-10): vs asthma.AFR.grch38_backup 100.00% same chr+pos (11,011,821 shared); vs lifted asthma.AFR 0.86% same pos; vs bmi.EUR GRCh37 0.91% same pos. Anchors rs429358 19:44908684, rs7412 19:44908822, rs9939609 16:53786615 = GRCh38. BUILD column says GRCh37 (also wrong in AFR grch38 backup).
errors: none — silent mislabel.
reproduction: rsid-position joins (scratchpad *.rs files).
started: GBMI release is GRCh38; liftover_asthma_afr.sh lifted only AFR. asthma.EUR.tsv.bgz mtime Apr 16 2026; .tbi Feb 11 2026 (stale index).

## Eliminated

- hypothesis: C — BMI legacy fits differ run-to-run because of OpenBLAS thread count
  evidence: OPENBLAS_NUM_THREADS 1/2/8 (threads verified in /proc/self/status) x 2 reps give bitwise-identical PIPs within a node type (cascadelake 6/6, broadwell 6/6); site /etc/profile.d/hpc.sh exports OMP_NUM_THREADS=1, so the earlier runs were single-threaded anyway
  timestamp: 2026-11-16
- hypothesis: C — genuine run-to-run randomness
  evidence: no seed/sampling in run_susie_rss.R; every repeat on the same node type is bitwise identical (16 of 16 pairs)
  timestamp: 2026-11-16

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
- timestamp: 2026-11-10
  checked: catalog rebuild reproducibility control (measure_asthma_fix/catalogs/control, workflow env python_stats 8f7292f9)
  found: rebuilding variants_legacy/APOL1 from the ORIGINAL 8 files reproduces the pinned sha 1cd2ffd0 only in the workflow's file order (config traits: bmi, t2d EUR, t2d AFR, hypertension, asthma EUR, asthma AFR, stroke EUR, stroke AFR); other orders give 6dd7c3b2 (dedup keep=first).
  implication: rebuild method validated by identity before use.
- timestamp: 2026-11-10
  checked: rebuilt catalogs (12 legacy + 31 r4) in measure_asthma_fix/catalogs/ vs current; contamination = catalog positions present only in the GRCh38 asthma.EUR file and in none of the 8 corrected files (contamination.tsv)
  found: old 669,105/1,571,591 = 42.58% (per region 30-50%, NC_IRF4 0); new 0/1,044,219. Correct asthma.EUR positions missing from catalog: old 65-22,808 per region, new 0.
- timestamp: 2026-11-10
  checked: 144 measurement fits outside the workflow (measure_asthma_fix/fits, fit_cmds.txt = commands.fit_command with sumstats/catalog/output substituted; all rc 0): repro_routeC semantics (legacy panel, snp_id join) asthma.EUR x 12 + 4 other EUR traits x 12 x {old,new catalog}; A3_1kg semantics (EUR_1kg_r4 panel, allele-aware, cap after LD) asthma x 4 claim regions + 4 traits x 4 x {old,new}. fit_summary.tsv, oldcat_vs_newcat.tsv, rds_compare.tsv
  found: corrected asthma.EUR panel-match fraction (ld_overlap / window): repro SH2B3 0.183 (was 0.038), MC4R 0.339 (0.0035), APOL1 0.320 (0.012), FTO 0.376 (0.353), CXADR 0.351 (0.354); A3 SH2B3 0.188, MC4R 0.339, APOL1 0.326, FTO 0.377. Controls: t2d.EUR (the other dense imputed file) repro 0.26-0.44, A3 0.25-0.40; hypertension/stroke/bmi repro 0.97-1.00, A3 0.85-0.88. Corrected asthma.EUR credible sets (purity 0.5 / JSON): repro SH2B3 0/0, MC4R 0/0, APOL1 0/0, FTO 9/9 singletons (non_converged), CXADR 0/0; A3 SH2B3 0, MC4R 0, APOL1 0, FTO 1 (95 variants). Existing mislabelled record (JSON = unfiltered sets): SH2B3 1 CS/140 (0 at purity 0.5), MC4R 1/5 (0), APOL1 1/43 (0), FTO 6 (6), CXADR 10 x ~4,510 (0).
  implication: the Fig 1B "SH2B3 asthma.EUR flagship 1 CS/140" was an impure set on mislocated data; corrected data give 0 CS at SH2B3, MC4R, APOL1 in both routes.
- timestamp: 2026-11-10
  checked: non-asthma fits, old vs new catalog
  found: repro_routeC (snp_id join): hypertension 12/12, stroke 12/12, t2d 12/12 JSON-identical; bmi 5/12 identical, all 11 fitted have the same variant set; determinism control (bmi SLC2A9 and SH2B3 re-run on the SAME old catalog) also differs (SLC2A9 5 vs 3 CS, max |dPIP| 0.125) -> bmi legacy fits are not run-to-run reproducible, the catalog is not shown to change them. A3_1kg (allele-aware catalog join): hypertension 0/4, stroke 0/4, t2d 0/4 identical, bmi 3/4: the contaminated catalog REMOVED other traits' variants, e.g. FTO t2d 5,860 -> 8,417, hypertension 1,785 -> 2,292, stroke 1,858 -> 2,416; SH2B3 hypertension 2 CS -> 1, FTO t2d CS sizes unchanged in count.
  implication: catalogs keep one row per rsid (collect_region_variants primary_key = SNP_ID, keep first): GRCh38 asthma.EUR rows, earlier in file order, evicted the GRCh37 rows of the same rsid (mechanism inferred from code; effect measured). Production (r4 route) fits of EVERY trait would have been affected; legacy-route repro fits of hypertension/stroke/t2d are not.
- timestamp: 2026-11-16
  checked: which python r4_catalog actually runs: `{PYTHON_BIN}` = sys.executable = smoke_dev python3.11 (pandas 3.0.2), not the declared python_stats env (pandas 2.2.3). Control (Slurm 1938110): legacy APOL1 from the ORIGINAL 8 files in workflow order with smoke_dev python
  found: sha 1cd2ffd0 == pinned == the python_stats control
  implication: CORRECTS the 2026-11-10 entry: the 6dd7c3b2 mismatch was file order, not env; the workflow rule as written reproduces the pinned catalogs.
- timestamp: 2026-11-16
  checked: B — config/ta_r4/cluster_slurm/{config.yaml,status.sh}; bin/r4_fire.sh now passes --profile config/ta_r4/cluster_slurm (logs data/r4/logs/slurm). tests/ta_r4/test_slurm_profile.py runs real snakemake on the committed profile with fake sbatch/sacct recording argv
  found: RED first (fire script still on cluster_lsf: 1 failed, 12 passed), GREEN after the switch. Negative controls in the test: profile without -t, without set-resources, without -A each fail the checker. Status script maps COMPLETED/RUNNING/PENDING/TIMEOUT/OUT_OF_MEMORY/FAILED/CANCELLED/NODE_FAIL correctly. Sizing from LSF logs (data/r4/logs/lsf, 1,872 jobs): r4_run_finemap max 2243 s and 27 GB RSS while 8 GB was requested (LSF did not enforce; Slurm does) -> finemap 48000 MB / 180 min; r4_panel_ukb_native max 846 s -> 120 min; everything else max <= 421 s -> default 60 min / rule mem_mb. Rules never measured (sim, qtl, coloc_pair): default 60 min; a timeout is reported failed by status.sh, not hung. Rscript: every rule that calls it has a conda env (plink.yml, r_coloc.yml) or an absolute path (R4_R2_RSCRIPT); jobs get --export=ALL (conda on PATH, isolated CONDARC/HOME from r4_fire.sh). Dry-run via the fire script: exactly 91 jobs (31 r4_catalog, 20 r4_panel_afr_1kg, 10 r4_identity_payload_afr, 30 r4_panel_ukb_native), no repro or other panel output.
  implication: B changes the fire surface the W4a/W4b lock covers (config/ta_r4 and bin/r4_fire.sh are LOCKED_PATHS; test_lock_gate R4_DEPENDENCIES now names cluster_slurm/config.yaml and status.sh). Must be committed before the lock.
- timestamp: 2026-11-16
  checked: which panels read a catalog (ta_r4_panels*.smk)
  found: variants_r4 -> AFR661_1kg_r4, AFR504_1kg_r4 (--extract range), AFR661_identity_r4 (from AFR661), EUR_ukb337k_r4 (native positions). variants_legacy -> k2d_identity and legacy AFR repro panels (repro only). EUR_1kg_r4, EUR_identity_r4 and both isect panels read no catalog.
  implication: under A, rebuild variants_r4 + those 4 panel sets only; variants_legacy, k2d and every repro output stay as pinned. Production fits cannot run before the lock (r4_lock_gate fails closed: no R4-LOCK.json / W4b-T3 sign-off).
- timestamp: 2026-11-16
  checked: rebuild via `bash bin/r4_fire.sh repro repro_routeC <91 targets>` on Slurm (commit bc5231c6 profile; log measure_asthma_fix/rebuild/fire.log); old variants_r4 backed up to measure_asthma_fix/rebuild/old_variants_r4 (SHA256SUMS)
  found: 91 of 91 steps, 0 errors. variants_r4 31/31 byte-identical to measure_asthma_fix/catalogs/r4. Contamination on the workflow catalogs (rebuild/contamination_workflow.tsv): 0 in every region (old 411-133,180 per region); correct asthma.EUR positions missing: 0 everywhere. NC_IRF4 catalog byte-unchanged (no asthma.EUR rows in its window). Catalog n_rows old->new: e.g. SH2B3 12,716->11,114, MC4R 17,382->14,940, APOL1 10,991->8,380, FTO 15,315->14,410, HLA 321,079->302,753. Manifests regenerated by rebuild/regen_manifests.py (panel_manifest.write_manifest: symmetric, diag 1, finite; UKB stats columns re-joined; headers unchanged): legacy catalog rows byte-unchanged; source/build/n_samples/ld_source etc. unchanged; only md5/sha256/size/n_var (+UKB n_pairs_zero_filled, n_var_dropped_allele_mismatch) move. n_var old->new: AFR661_1kg_r4 (= AFR661_identity_r4) 9p21 11,869->11,945, APOE 11,383->11,488, APOL1 1,875->1,878, BMI_5q13_3 21,323->21,468, CXADR 8,945->9,033, FTO 3,670->3,677, MC4R 3,252->3,255, PYHIN1 20,818->21,048, SH2B3 2,551->2,566, SLC2A9 15,114->15,458; AFR504_1kg_r4 9p21 11,724->11,802, APOE 11,305->11,418, APOL1 1,887->1,891, BMI_5q13_3 21,154->21,302, CXADR 8,795->8,886, FTO 3,638->3,645, MC4R 3,237->3,240, PYHIN1 20,686->20,913, SH2B3 2,553->2,568, SLC2A9 14,939->15,282; EUR_ukb337k_r4 29 of 30 grow (+7 to +1,319; SH2B3 2,606->2,765, MC4R 3,830->3,910, APOL1 2,313->2,378, FTO 4,008->4,140, HLA 34,361->35,680), NC_IRF4 968 sha unchanged; allele-mismatch drops fall in 26 regions (e.g. SLC2A9 159->113).
  implication: every panel gains variants (correct GRCh37 rsid rows previously evicted by GRCh38 asthma rows are now in the catalog); no panel lost its build/QC properties.
- timestamp: 2026-11-16
  checked: tests/ta_r4/test_live_pins.py (new, r4_heavy: all 43 catalogs + the 4 catalog-derived panel manifests vs disk sha256)
  found: RED before the manifest update (catalogs: 31 missing during the fire, then 30 of 43 sha mismatches after it; the 12 legacy + NC_IRF4 matched); GREEN after (Slurm 1939777: 5 passed)
  implication: pins updated; legacy (repro) catalogs verified unchanged by the same test.
- timestamp: 2026-11-16
  checked: C — bmi.EUR SLC2A9_urate repro_routeC command (measure_asthma_fix/bmi_determinism; base_cmd.txt, run.sh, run2.sh, compare.R, compare_cascadelake_ref.tsv). Slurm 1939048 (cascadelake c025n04), 1939049 (broadwell c202n07): OPENBLAS_NUM_THREADS 1/2/8 x 2 reps; 1940706 (haswell c207n10) x 2; 1940707 (cascadelake c021n04, OPENBLAS_CORETYPE=Haswell, OpenBLAS reports "Core: Haswell") x 2. Env r_coloc (OpenBLAS 0.3.34 pthreads, DYNAMIC_ARCH)
  found: all fits non_converged at niter 100. cascadelake (AVX-512) x6: 5 CS (1,1,1,2,2), ELBO -939909.8796082428, PIPs bitwise == the pinned repro_routeC fit and == the earlier c020 run. broadwell x6, haswell x2: 3 CS (1,2,2), ELBO -939964.8935116064, bitwise == the earlier c205 run; max |dPIP| vs cascadelake 0.125. cascadelake with the Haswell kernel forced: 3 CS, bitwise == the AVX2 nodes.
  implication: ROOT CAUSE (C): OpenBLAS runtime kernel dispatch by CPU type (SkylakeX/AVX-512 vs Haswell/AVX2 kernels round differently); a non-converged IBSS fit (stopped at max_iter 100) carries the difference into credible sets. Not threads, not randomness, not inputs. Deterministic per kernel. The pinned repro outputs reproduce only under the AVX-512 kernel (LSF hosts c001-c019 are not in the Slurm partition; their CPU type is not measurable now, but their outputs match cascadelake bitwise). The new Slurm profile can place a fit on any of cascadelake (28 nodes), broadwell (39), haswell (45) -> repro re-fires and non-converged production fits would depend on node placement. Needs a decision (kernel pin) before the lock.

## Resolution

root_cause: GBMI 2021 asthma is GRCh38. src/legacy/region_analysis/scripts/harmonize_sumstats.py stamps BUILD = config genome_build (GRCh37) with no source-build check and no liftover; liftover_asthma_afr.sh lifted only AFR, so asthma.EUR.tsv.bgz kept GRCh38 coordinates under a GRCh37 label, copied into config/ta_r4/data_sources.yaml (build: GRCh37) and the sha pin.
fix: (strand + repoint, after Carter approval) liftover script complements minus-strand SNVs / drops minus-strand non-SNVs; new pins data/r4/sumstats/asthma.{EUR,AFR}.grch37_lifted_strand.tsv.bgz; paths.sumstats_path routes r4-route asthma to them; data_sources.yaml + sumstats_r4_sha256.tsv updated. (earlier, landed pre-checkpoint) harmonizer refuses when the dataset declares source_build != --build (config/datasets.yaml gbmi_asthma source_build: GRCh38); GRCh37 lift written as a NEW file data/r4/sumstats/asthma.EUR.grch37_lifted.tsv.bgz; position-measured build test over the 8 Track A files. NOT done (checkpoint): repoint paths.sumstats_path / data_sources.yaml / sha pin; any re-fit; any OSF/claim edit.
verification: see Evidence (identity, rsid 100% vs native GRCh37, negative controls, REF check, RED->GREEN tests).
files_changed: [src/legacy/region_analysis/scripts/harmonize_sumstats.py, src/legacy/region_analysis/scripts/dataset_config.py, config/datasets.yaml, src/legacy/region_analysis/scripts/liftover_sumstats_hg38_to_hg19.sh, src/python/ta_r4/sumstats_build.py, tests/ta_r4/fixtures/build_anchors_grch37_grch38.tsv, tests/ta_r4/test_sumstats_build.py, tests/ta_r4/test_harmonizer_source_build.py]
