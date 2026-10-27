---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W2b-afr-and-ukb-panels
subsystem: AFR secondary-arm LD panels + UKB 337k EUR sensitivity panels (native, isect) + matched 1000G isect panels
tags: [ta-r4, d-03, d-04, d-07, d-10, d-20, e6, pitfall-10, pitfall-12, panels, known-answer]
requires: [ta-r4-W2a-eur-panels-catalogs-identity]
provides:
  - src/snakemake/rules/ta_r4_panels_afr_ukb.smk (r4_panel_afr_1kg, r4_identity_payload_afr, r4_panel_afr_legacy, r4_panel_ukb_native, r4_panel_ukb_isect, r4_w2b_afr_all, r4_w2b_ukb_all)
  - src/python/ta_r4/ukb337k_tiles.py (fetch, triangle-safe load, region assembly, D.R.D orientation, native/isect builders, .rds I/O)
  - data/r4/ld/{AFR661_1kg_r4, AFR504_1kg_r4, AFR661_identity_r4, legacy_repro/AFR, EUR_ukb337k_r4, EUR_ukb337k_isect_r4, EUR_1kg_isect_r4}
  - manifests afr_samples_sha256 / panels_AFR661_1kg_r4 / panels_AFR504_1kg_r4 / panels_AFR661_identity_r4 / panels_legacy_repro_AFR / ukb337k_tiles_sha256 / panels_EUR_ukb337k_r4 / panels_EUR_ukb337k_isect_r4 / panels_EUR_1kg_isect_r4
affects: [W2c (HM3 / ukb_native decision; 4 native panels > 16,000 variants; AFR BMI/PYHIN1 > 16,000), W3a (repro_routeC AFR panels = 12 placeholders), W5a (AFR661/AFR504/A3_ukb/isect panels)]
tech-stack:
  added: []
  patterns: [UKB tile R = M + M.T (diag 0.5 stored), isect panels share one variants frame, mixed-orientation sign agreement as the discriminating orientation check]
key-files:
  created:
    - src/snakemake/rules/ta_r4_panels_afr_ukb.smk
    - src/python/ta_r4/ukb337k_tiles.py
    - tests/ta_r4/test_ukb_tile_loader.py
    - tests/ta_r4/test_ukb_tile_triangle.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/{afr_samples_sha256,panels_AFR661_1kg_r4,panels_AFR504_1kg_r4,panels_AFR661_identity_r4,panels_legacy_repro_AFR,ukb337k_tiles_sha256,panels_EUR_ukb337k_r4,panels_EUR_ukb337k_isect_r4,panels_EUR_1kg_isect_r4}.tsv
  modified:
    - config/ta_r4/cluster_lsf/cluster_config.yaml
    - src/python/ta_r4/fetch_verified.py (zip magic)
    - tests/ta_r4/test_fetch_verified.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "The previous session's AFR outputs were kept, not rebuilt: every one was checked against the plan by content (sample IIDs, .bim, symmetry/diag, identity frames, placeholders) and all checks passed."
  - "UKB covering tiles are chosen among tiles whose .npz exists (HEAD); chr6 26-33 Mb .npz return 404, which leaves a 28-33 Mb hole in the HLA native panel."
  - "Sign agreement on the real tile is also asserted on mixed-orientation pairs: the overall rate cannot detect a missing D.R.D when most variants flip."
  - "Isect panels drop palindromic A/T and C/G variants, as the plan specifies (orientation cannot be read from the alleles)."
  - "HM3 restriction / ukb_native handling NOT chosen (Carter, W2c)."
metrics:
  duration: "~3h40m (2026-10-27 12:05-15:45 EDT) on top of the stopped session's uncommitted WIP"
  completed: 2026-10-27
  tasks: 3
---

# Phase ta-r4 Plan W2b: AFR and UKB panels Summary

W2b puts the AFR secondary-arm panels and the UKB 337k reference-mismatch sensitivity substrate on /rs1. AFR has 10
AFR661 + 10 AFR504 plink panels, 10 matched AFR661 identity payloads and 12 legacy AFR reproduction panels; all 12
legacy panels are `use_identity` placeholders, exactly as the frozen builder wrote them. UKB has 30 native panels
(29 + HLA_6p21), 29 isect panels re-oriented to the 1000G REF/ALT, and the 29 matched 1000G isect panels.
The UKB loader is proven on a real tile: diag == 1 exactly and sign agreement with 1000G EUR of 0.999953 (1.0 on
mixed-orientation pairs). Both isect classes carry identical variants frames in 29/29 regions.

## Commits

| Task | Commit | Content |
|---|---|---|
| 1 | `37a391e4` | AFR rules + 4 AFR panel manifests + afr_samples_sha256; cluster mem; fetch_verified zip magic |
| 2 | `f6d637aa` | ukb337k_tiles.py loader, unit tests, real-tile live gate (mixed-pair assertion added), tile manifest (35 rows) |
| 3 | `fa91305f` | UKB native/isect rules + builders + tests, 41 more tile files, 3 UKB panel manifests |
| fix | `0e621884` | no /rs1 literal in ukb337k_tiles (RED: test_no_rs1_or_share_literals…), tile manifest keyed by `file` (RED: test_manifests_parse), UKB rules in envs/r_coloc.yml |
| fix | `1d900305` | dropped include-time region-count raises (RED: 4/6 toy e2e in HEAVY) |
| close | wave-close commit | LOG, STATE, ROADMAP, this SUMMARY |

The orchestrator's mid-wave checkpoint `3c6c942c` (HANDOFF/STATE/.continue-here only) sits between `0e621884` and `1d900305`.

## Resume handling

- The two working-tree deletions `.planning/quick/260511-aou-w2-oom-fix/forensics/2026-05-04-stage8-regionpool-oom/{11_hail_current_run.log,12_hail_prior_run.log}` were restored with `git checkout --`; they were not committed.
- Nothing from the previous session was trusted on presence. Each artifact was checked as below.

## Task 1: AFR panels (verified by content)

- Samples: `wc -l` gives AFR504 **504** and AFR661 **661**. AFR504 is byte-identical to `AFR.samples` (sha256 97ff9e57…).
  The added ASW+ACB set has 157 IIDs and 0 overlap with the 504; AFR661 == sort -u(504 ∪ 157). Panel populations in AFR661: ACB 96, ASW 61, ESN 99,
  GWD 113, LWK 99, MSL 85, YRI 108 (504 = the five continental). Two columns, FID == IID on all 661 rows.
  Every plink `.fam` IID set equals its sample list (SH2B3 checked for both panels), and all 20 plink logs say "661 people" / "504 people".
- R4 panels (20): manifest n_var == plink `.bim` rows, POS/ALT/REF == `.bim` V4/V5/V6 (`identical()`), 20/20 TRUE.
  max_asym 0, max |diag-1| 0, all finite, has_ref_alt true, n_samples 661 / 504. AFR661 identity payloads: variants
  `identical()` to AFR661_1kg_r4 10/10, identity_exact true 10/10. The SLC2A9 payload was rebuilt by the previous session after an
  LSF loss (423614); it passes the same checks.

| region | AFR661 n_var | AFR504 n_var |
|---|---|---|
| 9p21_CDKN2A | 11869 | 11724 |
| APOE_19q13 | 11383 | 11305 |
| APOL1_22q12 | 1875 | 1887 |
| BMI_5q13_3 | **21323** | **21154** |
| CXADR_F2RL1_6p21 | 8945 | 8795 |
| FTO_16q12 | 3670 | 3638 |
| MC4R_18q21 | 3252 | 3237 |
| PYHIN1_1q23 | **20818** | **20686** |
| SH2B3_12q24 | 2551 | 2553 |
| SLC2A9_urate | 15114 | 14939 |

- FINDING (`data/r4/findings/afr_panel_size.tsv`, 4 rows): BMI_5q13_3 and PYHIN1_1q23 exceed 16,000 in both AFR panels.
  `too_many_variants` in run_susie_rss.R fires on the sumstats ∩ panel subset (finemap.smk `susie_max_variants` 16000), so these fits will report it if the overlap is also above 16,000.
- Legacy AFR: **12** panels. Source: TRACK-A-FROZEN-NUMBERS.md:64 says "96 total Stage 2 real-LD fits; 36 AFR fits",
  and IDENTITY-LD-K2D-FIT-SUMMARY.tsv has the AFR fits as 3 traits × 12 regions (each region 3 rows). **12/12 are `use_identity` placeholders**
  (`status variants_exceed_threshold`, R NULL). Each variants frame has as many rows as its legacy catalog (e.g. SH2B3 12716), and every catalog
  has > 6000 unique positions (smallest APOL1 9134). That is the frozen builder's behaviour with LD_MAX_VARIANTS unset.
- Manifests 10/10/10/12 rows; md5_mismatches [] for all four. chmod a-w applies to all 42 AFR .rds. Dry-run `r4_w2b_afr_all`: "Nothing to be done".

## Task 2: UKB loader (TDD) and real-tile gate

Whether the previous session saw RED is unknown, so RED was re-derived. Every sabotage below was applied in place
with `PYTHONDONTWRITEBYTECODE=1`, after deleting `ukb337k_tiles.*.pyc`. Each was restored, and the restore was checked with `cmp` and sha256.

- Module absent → `ERROR tests/ta_r4/test_ukb_tile_loader.py`, `1 error in 0.90s` (collection).
- Halving `(R + R.T)/2` for half_diag → 7 RED (`test_lower_triangle_half_diag`, `test_upper_triangle_half_diag`, `test_variants_frame`,
  `test_keep_subset`, the 3 assemble tests).
- orient without D.R.D → 3 RED (`test_orient_known_answer`, `test_orient_follows_reference_order`, `test_orient_counts_variants_absent_from_reference`).
- overlap disagreement check off → `test_assemble_disagreement_raises` RED; palindromes kept → `test_orient_drops_allele_mismatch_and_palindromes` RED;
  zero-fill count off → 2 RED; REF/ALT labels swapped → `test_variants_frame` RED.
- Turning off the diagonal-convention check alone gave 24 passed, and so did turning off the post-transform diag check alone: the two guards back each other up.
  With both off, 3 RED (`test_other_diagonal_refused[diag0..2]`).
- GREEN 24 passed (unit, before Task 3 additions). numpy 2.4.4, scipy 1.17.1, pandas 3.0.2 (smoke_dev Python 3.11; scipy present, no conda env needed).

Live gate (bsub, 3 GB max), tile `chr12_111000001_114000001` (.npz float32, 16514 × 16514, 136,364,344 nnz, `lower_half_diag`):

```
sign agreement 21409/21410 = 0.999953 over 745 shared variants (n_flipped 717); mixed-orientation pairs 154/154 = 1.000000
4 passed in 45.02s
tile  panel  n_var_1kg  n_var_shared  n_flipped  n_dropped_allele_mismatch  n_dropped_palindromic  n_pairs_abs_r_gt_0.5  n_agree  rate  n_pairs_mixed  n_agree_mixed  rate_mixed
chr12_111000001_114000001  EUR_1kg_r4/SH2B3_12q24  895  745  717  2  140  21410  21409  0.999953  154  154  1.000000
```

- Live negative control, halving in load_tile + full_diagonal: `FAILED test_real_tile_diag_exactly_one`, `FAILED test_real_tile_symmetric_in_blocks`,
  `FAILED test_sign_agreement_with_1000g_eur`, `3 failed, 1 passed`. The pass is `test_halving_transform_breaks_diag`, which asserts that the halved diag != 1.
- **Finding about the gate itself:** with D.R.D removed, the plan's ≥ 0.90 overall agreement still passed (**0.992760**). 717/745 variants flip, which is nearly a
  global flip, and a global flip preserves pairwise signs. I added the mixed-orientation assertion (pairs with exactly one flipped variant, the only pairs whose sign D.R.D changes).
  The same control then gives `mixed-orientation pairs 0/154 = 0.000000` → `FAILED test_sign_agreement_with_1000g_eur`.
- Tile manifest: 35 rows at T2. Re-measured: size and ETag equal a fresh HEAD, and sha256/md5 equal disk, 35/35.

## Task 3: UKB panels

- Tiles: all 121 tiles intersecting the 30 regions were HEADed. **7 `.npz` return 404**: chr6 26–28, 27–30, 28–31, 29–32, 30–33, 31–34 and 32–35 Mb. The `.gz`
  files exist for 4 of them. Covering tiles are chosen from the 114 existing `.npz` files: 36 tiles, of which 31 needed an `.npz` and 5 needed both files → 41 files
  fetched (5 in parallel, 43.3 GB). Manifest **76 rows = 39 gz + 37 npz**. All 76 have size and ETag equal to HEAD and sha256 equal to disk. `file` is now column 1.
- New tests RED first: `4 failed, 24 passed` (`test_assemble_allowed_drops_allele_mismatch`, `test_build_native`, `test_build_isect_known_answer`,
  `test_build_isect_rds_frames_identical`, all AttributeError) → GREEN. Controls: allowed filter off → 2 RED; isect without D.R.D →
  `test_build_isect_known_answer` RED; UKB isect written with a different frame → `test_build_isect_rds_frames_identical` RED;
  zero-filled mask ignored → initially **no test failed** (the original fixture had no strong zero-filled pair). I added
  `test_build_isect_sign_agreement_skips_zero_filled`, and the same control then turns it RED. `add_stats_columns` was written before its test (an order
  slip); its control, the missing-stats check off, makes `test_add_stats_columns` RED. Unit file total: 30 passed.
- Fires: #1 hung at 49/60 (LSF exit-255 "Cannot open your job file" losses; 6 counted at the time). The rule input `ukb337k_tiles.py` had been edited while #1 ran, so I deleted every
  output and rebuilt (#2, hung at 53/60 on more exit-255 losses, then #3 7/7). #2 was byte-identical to #1 (122/122 md5). The two fixes in `0e621884` changed
  the code again, so I deleted everything and rebuilt again (#4). #4 stopped at **52/60** because 7 jobs (426460, 426470, 426473, 426478, 426493, 426498, 426501) were lost
  to exit-255 before their script ran. Snakemake gets no `.jobfailed` for those, so it waited. No LSF job was alive, so I stopped it (TERM, then KILL → exit 137),
  checked that the lock held only UKB paths, unlocked, and ran #5: `8 of 8 steps (100%) done`. Final dry-run: "Nothing to be done". #4+#5 against #2: **147/147 md5 identical**.
- Rscript under Snakemake: all 59 #4/#5 UKB jobs logged `Activating conda environment: …/smk_job_envs/ta_r4/0f3436279d4146c376747a0ea5bfd4bf_`.
  That env's `.yaml` is byte-identical (`cmp`) to `envs/r_coloc.yml`; its `bin/Rscript` is R 4.4.2, the same version as the /rs1 r_coloc Rscript used before. No
  job logged a Traceback or "no Rscript", and the outputs are byte-identical to the build that used the pinned path.
- Counts: native **30**, isect **29**, 1000G isect **29** (`ls | wc -l`). Manifests 30/29/29 rows; matrix 88/88, asym 0, |diag-1| 0, finite, has_ref_alt
  true; md5_mismatches [] ×3. n_samples is NA for UKB (337k is the published figure; it cannot be measured from the tiles) and 489 for 1000G isect. Extra columns:
  tiles, n_tiles, n_pairs_zero_filled, n_var_dropped_allele_mismatch (+ n_var_dropped_palindromic, n_var_dropped_ambiguous, n_flipped, n_var_ref for isect).
- Sum n_var: native 182,019; isect 71,769 (both classes); n_var_ref sums to 86,035 = W2a's EUR_1kg_r4 total.
- `find data/processed/ld_reference -newer data/r4/ld/EUR_1kg_r4 -print | wc -l` → 0 (the directory does not exist). chmod a-w: 222 .rds under data/r4/ld, 0 writable.

### Native n_var (`data/r4/findings/ukb_native_panel_size.tsv`)

4 of 30 exceed 16,000: **HLA_6p21 34,361** (3 tiles; 293,039,198 zero-filled pairs; the 28–33 Mb hole), **PYHIN1_1q23 26,050** (3 tiles,
45,317,232 zero-filled), **BMI_5q13_3 24,121** (3 tiles, 36,769,777 zero-filled), **SLC2A9_urate 16,752** (1 tile). The other 26 are ≤ 13,647 and each sits in one tile with 0 zero-filled pairs.
The native SNP_ID is the UKB `rsid` field: 174,352 match `^rs[0-9]+$`; 7,667 are `chr:pos_A1_A2` style (e.g. `12:111404993_CT_C`).

### Isect: frame equality and per-region orientation

R `identical(x$variants, y$variants)` TRUE **29/29**, and `identical()` on CHR/POS/REF/ALT TRUE 29/29. n_ukb == n_1kg in every region.
Sign agreement is over |r_1kg| > 0.5 pairs that share a tile. An independent file-level recount over all pairs gives the same n_agree in 29/29. It gives the same pair count in 28/29; PYHIN1 has
1 more pair, a zero-filled pair with |r_1kg| > 0.5 that the build excluded.

| region | n_var_ref | n_var | n_flipped | allele mism. | palin. | zero-filled | pairs | agree | rate | mixed | agree mixed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 9p21_CDKN2A | 7576 | 6081 | 5133 | 11 | 1405 | 0 | 266937 | 266885 | 0.999805 | 52140 | 52136 |
| APOE_19q13 | 7734 | 6447 | 5317 | 7 | 1176 | 0 | 161860 | 161790 | 0.999568 | 38565 | 38563 |
| APOL1_22q12 | 1335 | 1120 | 1014 | 2 | 199 | 0 | 46255 | 45806 | 0.990293 | 1531 | 1530 |
| BMI_5q13_3 | 14025 | 11885 | 10262 | 21 | 2066 | 8635830 | 519594 | 519562 | 0.999938 | 78327 | 78327 |
| CXADR_F2RL1_6p21 | 6113 | 5091 | 4395 | 8 | 925 | 0 | 137285 | 137182 | 0.999250 | 25076 | 25074 |
| FTO_16q12 | 2404 | 2067 | 1821 | 2 | 323 | 0 | 37491 | 37491 | 1.000000 | 4180 | 4180 |
| MC4R_18q21 | 2229 | 1880 | 1580 | 5 | 332 | 0 | 40823 | 40770 | 0.998702 | 9357 | 9357 |
| NC_ABO | 288 | 253 | 201 | 0 | 34 | 0 | 6906 | 6906 | 1.000000 | 2342 | 2342 |
| NC_FUT1_FUT2 | 228 | 195 | 163 | 1 | 31 | 0 | 5821 | 5821 | 1.000000 | 1253 | 1253 |
| NC_IRF4 | 564 | 490 | 348 | 0 | 67 | 0 | 7586 | 7586 | 1.000000 | 2275 | 2275 |
| NC_KEL | 262 | 229 | 225 | 1 | 30 | 0 | 6149 | 6149 | 1.000000 | 0 | 0 |
| NC_MC1R | 1141 | 946 | 861 | 0 | 182 | 0 | 37671 | 37581 | 0.997611 | 1388 | 1388 |
| NC_NULL_01 | 1096 | 927 | 782 | 1 | 156 | 0 | 22631 | 22631 | 1.000000 | 4492 | 4492 |
| NC_NULL_02 | 1166 | 984 | 852 | 0 | 181 | 0 | 24113 | 24113 | 1.000000 | 4048 | 4048 |
| NC_NULL_03 | 780 | 658 | 501 | 0 | 118 | 0 | 43699 | 43699 | 1.000000 | 11641 | 11641 |
| NC_NULL_04 | 952 | 797 | 757 | 2 | 147 | 0 | 22025 | 22025 | 1.000000 | 1163 | 1163 |
| NC_NULL_05 | 890 | 760 | 686 | 0 | 122 | 0 | 23729 | 23729 | 1.000000 | 2580 | 2580 |
| NC_NULL_06 | 1530 | 1259 | 1249 | 1 | 263 | 0 | 210910 | 210910 | 1.000000 | 2982 | 2982 |
| NC_NULL_07 | 1212 | 991 | 786 | 0 | 208 | 0 | 30950 | 30950 | 1.000000 | 6246 | 6246 |
| NC_NULL_08 | 940 | 784 | 609 | 1 | 156 | 0 | 36452 | 36452 | 1.000000 | 10791 | 10791 |
| NC_NULL_09 | 1053 | 876 | 670 | 2 | 166 | 0 | 22397 | 22397 | 1.000000 | 7892 | 7892 |
| NC_NULL_10 | 1151 | 934 | 819 | 0 | 210 | 0 | 28477 | 28476 | 0.999965 | 6658 | 6658 |
| NC_OCA2_HERC2 | 1476 | 1271 | 935 | 2 | 187 | 0 | 48999 | 48990 | 0.999816 | 11273 | 11273 |
| NC_RH | 257 | 212 | 142 | 1 | 41 | 0 | 2647 | 2644 | 0.998867 | 678 | 678 |
| NC_SLC24A5 | 1120 | 938 | 779 | 1 | 176 | 0 | 17482 | 17482 | 1.000000 | 4535 | 4535 |
| NC_TYR | 1715 | 1421 | 1114 | 1 | 277 | 0 | 116580 | 116566 | 0.999880 | 38632 | 38627 |
| PYHIN1_1q23 | 15236 | 12746 | 10361 | 20 | 2349 | 11390426 | 520678 | 520621 | 0.999891 | 140507 | 140505 |
| SH2B3_12q24 | 895 | 745 | 717 | 2 | 140 | 0 | 21410 | 21409 | 0.999953 | 154 | 154 |
| SLC2A9_urate | 10667 | 8782 | 6804 | 14 | 1735 | 0 | 984562 | 984463 | 0.999899 | 328148 | 328138 |

Lowest rate: APOL1 0.990293. Lowest mixed rate: APOL1 0.999347. NC_KEL has no mixed strong pair. The SH2B3 row equals the T2 live gate exactly.
n_var_ref − n_var does not decompose exactly into the drop columns (range −1..136): those columns count UKB-side variants, and a reference row can be absent from UKB. No "not in UKB" count is claimed.

## Wave close

- QUICK `330 passed, 50 deselected`. Wall times: 74.6 s, 62.6 s and 73.5 s on three runs, and one run of 144.5 s under login-node load (load avg 4.9).
  Re-timed at 74.6 s. Slowest: test_import_isolation 12.6 s, so no new r4_heavy marks.
- HEAVY `46 passed, 4 skipped` (14m26s, bsub) = W2a's 42 + the 4 real-tile tests. The skips are the W5a/W5b live gates. The first HEAVY run was
  `4 failed` (test_snakemake_toy_e2e: include-time raise in the new smk) → fixed in `1d900305` → toy e2e `6 passed`.
- Freeze pins `39 passed`.
- FULL `1804 passed, 50 skipped` (29m54s, junit `data/r4/logs/full_W2b.xml`). The first FULL attempt hit the 30-min LSF default run limit and was resubmitted with `-W 600`.
  Joined BY NAME against `full_W2a.xml`: common 1819, **removed 0, changed 0, added 35** (ukb_tile_loader 30, ukb_tile_triangle 4,
  fetch_verified 1; all passed); 1819 + 35 = 1854 ids, 1769 + 35 = 1804 passed, 50 + 0 = 50 skipped.
  tests/m3 1299 (1265/34) → 1299 (1265/34); phase1 38 → 38; phase2 137 → 137; ta_r4 345 → 380.
- sparse_parent_benchmark.tsv restored (`git checkout --`). Frozen files 0-diff vs e8aa84a8: run_susie_rss.R, run_coloc_susie.R, Snakefile,
  config/pipeline.yaml, finemap.smk, envs/r_coloc.yml, Snakefile.ta_r4.
- Shared conda cache `/rs1/.../conda_pkgs`: 2188 entries, listing sha256 f094b37d9a72…, 0 archives, both before and after (= W2a). The UKB rules reuse the existing
  r_coloc job env (0f343627…), so no new env was solved.

## Deviations from Plan

1. **[Rule 2] Discriminating orientation gate.** The overall ≥ 0.90 sign agreement passed with D.R.D removed (0.992760). I added a mixed-pair assertion (RED 0/154 under the same control).
2. **[Rule 1] HLA tile coverage.** The previous session chose tiles by `.gz` existence; chr6 26–28/27–30 `.gz` exist but their `.npz` do not. Coverage now requires both files in the tile manifest.
3. **[Rule 1] /rs1 literal + manifest key** (pre-existing tests RED): see `0e621884`. **[Rule 1] include-time raises** broke the toy e2e: `1d900305`.
4. **Rebuilt UKB twice** because the declared code input changed (once during a fire, once for the fixes). All three builds are byte-identical where comparable.
5. Stats extra columns are joined by `ukb337k_tiles.add_stats_columns` after `panel_manifest.py` writes the base manifest (panel_manifest's column set is fixed).
6. Sign agreement excludes zero-filled pairs (no tile measured them); n_pairs_zero_filled is reported alongside.
7. Memory: native 48,000 MB, isect 32,000 MB in cluster_config (the profile reads cluster.mem_mb); measured n_var² × 8 B ≤ 9.4 GB.

## Open decisions for Carter (not chosen)

- Carried: hypertension.EUR sdY (W2c); stroke.AFR checksum mismatch; pre-W4 chr:pos vs rsid fit-name handling; HM3 restriction / ukb_native (W2c-T4).
- New input to HM3/ukb_native: 4 native UKB panels > 16,000 (HLA 34,361, PYHIN1 26,050, BMI_5q13_3 24,121, SLC2A9 16,752); AFR661/504 BMI_5q13_3 and PYHIN1 > 16,000.
- New input to the SNP_ID decision: native UKB SNP_IDs are 174,352 rsid + 7,667 `chr:pos_A1_A2`; isect panels carry the 1000G rsids.
- New: the HLA native panel has no LD for 28–33 Mb (UKB publishes no `.npz` there); it is exploratory only (D-24).
- New: isect drops palindromes, so the isect comparison covers 71,769 of the 86,035 EUR_1kg_r4 variants (83.4%).

## Known Stubs

None.

## Threat Flags

None. The only network traffic was anonymous HTTPS HEAD/GET to the public S3 bucket listed in data_sources.yaml (T-r4-W2b-01 mitigated: size + ETag + sha256). Every write is under data/r4.

## Self-Check: PASSED

Commits 37a391e4, f6d637aa, fa91305f, 0e621884, 1d900305 exist; all created code/test files and the three findings TSVs exist; md5_mismatches [] for all 7 W2b manifests.
