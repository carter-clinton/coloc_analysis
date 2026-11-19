---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5b
slug: W3f-ukb-panels-biallelic
subsystem: ta-r4 UKB native LD panels / fit eligibility / OSF amendment DRAFT
tags: [ta-r4, W3f, M2, UKB, multi-allelic, DUPLICATE_KEYS, DRAFT]
requires: [ta-r4-W3f-catalog-dupkey-producer-and-guard, ta-r4-W3f-eligibility-measurement-and-draft]
provides: [ukb_native_multiallelic module, 30 rebuilt EUR_ukb337k_r4 panels, ukb_native_multiallelic_resolved.tsv, re-pinned panels_EUR_ukb337k_r4.tsv, A3_ukb eligibility rows on the rebuilt panels, DRAFT M2 row RESOLVED]
affects: [ta-r4-W3f-review-suite-and-close (15.6), W4a-T3 lock]
tech-stack:
  added: []
  patterns: [producer-side resolution of multi-variant CHR:POS after the catalog filter, exact R-submatrix identity check against a verified backup, tile-membership re-derivation of zero-filled pairs]
key-files:
  created:
    - src/python/ta_r4/ukb_native_multiallelic.py
    - tests/ta_r4/test_ukb_native_multiallelic.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb_native_multiallelic_resolved.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-m2-biallelic-ukb-reply-2026-11-18.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-ukb-no-snps-only-reply-2026-11-18.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-ukb-a1-keep-snv-reply-2026-11-18.txt
  modified:
    - .planning/DECISIONS.md
    - src/snakemake/rules/ta_r4_panels_afr_ukb.smk
    - tests/ta_r4/test_live_pins.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - "DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1 (Carter): UKB native panels keep the single SNV at a multi-variant CHR:POS, else drop the position; no --snps-only"
  - "Native stats n_var and n_pairs_zero_filled describe the final (post-resolution) panel; other build_native stats are unchanged"
metrics:
  completed: 2026-11-19
  tasks: 3
---

# Phase ta-r4 Plan 15.5b: W3f UKB native panels, one variant per CHR:POS Summary

The UKB native builder now resolves every CHR:POS that holds more than one variant. If exactly one of them is an ACGT
SNV, that SNV is kept; otherwise the position is dropped. The 30 native panels were rebuilt on Slurm: 38 positions in
15 panels, 31 kept SNVs, 45 dropped variants. Each rebuilt panel is the old one with rows and columns removed, exactly.
M2 is 0 of 145 A3_ukb fits. A3_ukb eligibility was re-measured, and the DRAFT's M2 row is RESOLVED. Nothing is pushed.

## Commits

| Task | Commit | What |
|---|---|---|
| 1 DEC | 5ca20376 | DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1 + the three reply files |
| 1 code | 526fd5c7 | `ukb_native_multiallelic.py`, rule wiring, tests (T-a..T-i) |
| 2 | 3c1ed352 | rebuilt panels re-pinned: `panels_EUR_ukb337k_r4.tsv`, `ukb_native_multiallelic_resolved.tsv`, live pins |
| 3 | 07dae0c0 | `w3f_fit_eligibility.tsv` A3_ukb rows; DRAFT |
| 3 docs | (this commit) | LOG, STATE, this SUMMARY |

## Task 1: DEC, resolver, wiring

- Reply sha256s match the plan (4d0b2241…, 38f9bfdc…, 597b6602…); `od -c` of the two one-liners as expected. Inserted
  with `cat`. Every non-empty reply line passes `grep -F -x`, and each file is a byte substring of DECISIONS.md. NC: an
  altered line does not match. The diff is 44 added, 0 removed.
- QUICK baseline before the test file existed (Slurm 1985965): 738P/2S.
- RED: 10 non-heavy tests failed (9 on the missing module, which the `tests/ta_r4/__init__.py` shadowing reports as
  `ImportError: cannot import name 'ukb_native_multiallelic'`; T-h on the unchanged rule shell). T-f failed on the same
  import in Slurm 1986099, reached only after its "UKB carries both rows" and catalog asserts had passed. GREEN: 10/10
  on the login node, T-f in Slurm 1986169.
- Negative controls (`data/r4/tmp/w3f/ukbbi/nc_t1.txt`; each restored sha256-identical):

| NC | Mutation | Tests failed |
|---|---|---|
| NC-1 | no-op resolver | T-a, T-a2, T-b, T-c, keyed, T-g, T-i |
| NC-2 | a2, drop every n ≥ 2 | T-a, T-a2, keyed, T-g, T-i; T-f (Slurm 1986252) |
| NC-3 | keep the first SNV if any | T-c |
| NC-4 | `--snps-only` semantics | T-d, keyed, T-g, T-i |
| NC-5 | SNV = length 1 only | T-a2 |
| NC-7 | resolve raw tile variants before the catalog filter | T-g, T-i |
| NC-6 | rule shell back to `ukb337k_tiles build-native` | T-h |
| NC-8 (added) | kept rows reversed | T-a, T-d, T-e, keyed, T-g |

- Control dry-run (Slurm 1986341, 324 targets): `r4_panel_ukb_native 30` and nothing else. Code and params listings
  over the 264 non-native targets were empty. A control (Slurm 1986415) showed the same filter printing the native rds
  files, so the empty listing is not vacuous. `--forcerun r4_panel_ukb_isect` listed 29 (+ `r4_gate_probe` 1).

## Task 2: backup, rebuild, identity, re-pin, M2

- 28T free. Backup (Slurm 1986444): EUR_ukb337k_r4 30 and native stats 30, each verified against its live origin, plus
  the committed manifest. pre_untouched.sha256 = 359 files = 29 × 4 (EUR_1kg, EUR_identity, both isect) + 10 × 3 (AFR)
  + 22 legacy_repro + 24 k2d + 31 × 3 (variants_r4, _raw, _dropped) + 12 variants_legacy + 29 isect stats + 33 manifests.
  `restore.sh --verify-only` (Slurm 1986510): backup and live 100% OK.
- Manifest reproduction (Slurm 1986511): `cmp` with the committed manifest is byte-identical.
- Recount of the live panels before the fire (Slurm 1986512): every component equals the planning table (30 regions,
  38 positions / 76 variants, 31 / 7 / 0, every position n = 2, every to-be-dropped variant an indel, PYHIN1
  1:160680184 = rs184461353 A/G + rs143145026, 17,116 indels), and the resolver agrees in 30/30.
- Fire: Slurm 1986672..1986701, `30 of 30 steps (100%) done`, 30/30 COMPLETED 0:0. Post-fire dry-run (Slurm 1987086)
  over all 324 targets plus the 30 sidecars: "Nothing to be done". Code and params listings empty; forcerun control 29.
- Identity (Slurm 1987087), all components:

| Check | Result |
|---|---|
| variants new == old minus audit `dropped`, same order | 30/30 |
| `np.array_equal(R_new, R_old[keep][:, keep])` | 30/30 |
| duplicated (CHR, POS) in new | 0 in 30/30 |
| remaining variant at each one_snv position is the SNV | 15/15 changed |
| n_var | 189,945 − 45 = 189,900 |
| dropped | 45 = 31 (one_snv indels) + 14 (2 × 7 no_snv) |
| indels | 17,116 → 17,071 |
| regions | 15 changed + 15 unchanged |
| audit | 76 = 31 kept_snv + 45 dropped; PYHIN1 rs184461353 kept_snv, rs143145026 dropped |
| n_pairs_zero_filled old / new re-derived from `assemble_region(return_filled=True)` | 15/15 / 15/15 |
| other stats columns equal the old stats | 30/30 |
| (d) pre_untouched.sha256 | 359/359 OK |

- Per-region reconciliation (planning table = measurement):

| region | n_var | one_snv | no_snv | kept_snv | dropped | new n_var |
|---|---|---|---|---|---|---|
| 9p21_CDKN2A | 14,242 | 2 | 1 | 2 | 4 | 14,238 |
| APOE_19q13 | 13,461 | 4 | 1 | 4 | 6 | 13,455 |
| BMI_5q13_3 | 25,160 | 4 | 0 | 4 | 4 | 25,156 |
| CXADR_F2RL1_6p21 | 10,999 | 3 | 0 | 3 | 3 | 10,996 |
| HLA_6p21 | 35,680 | 1 | 3 | 1 | 7 | 35,673 |
| MC4R_18q21 | 3,910 | 1 | 0 | 1 | 1 | 3,909 |
| NC_NULL_01 | 1,780 | 0 | 1 | 0 | 2 | 1,778 |
| NC_NULL_04 | 1,898 | 1 | 0 | 1 | 1 | 1,897 |
| NC_NULL_06 | 2,522 | 2 | 0 | 2 | 2 | 2,520 |
| NC_NULL_07 | 2,351 | 2 | 0 | 2 | 2 | 2,349 |
| NC_NULL_08 | 1,661 | 1 | 0 | 1 | 1 | 1,660 |
| NC_OCA2_HERC2 | 2,919 | 1 | 0 | 1 | 1 | 2,918 |
| NC_SLC24A5 | 2,325 | 1 | 0 | 1 | 1 | 2,324 |
| PYHIN1_1q23 | 27,276 | 6 | 1 | 6 | 8 | 27,268 |
| SLC2A9_urate | 17,982 | 2 | 0 | 2 | 2 | 17,980 |
| total (30 panels) | 189,945 | 31 | 7 | 31 | 45 | 189,900 |

- Re-pin: 15 rows change (md5, sha256, size_bytes, n_var). n_pairs_zero_filled moves in the 3 multi-tile regions: BMI
  39,910,644 → 39,894,525; HLA 315,752,919 → 315,626,462; PYHIN1 49,845,520 → 49,809,122. The 15 unchanged panels are
  byte-identical to their old pins. 4 new columns. `git diff t2_start..HEAD -- $MAN` lists exactly the 2 files.
- Live pins. `test_catalog_derived_panels_match_manifest[EUR_ukb337k_r4]` was RED before the re-pin (Slurm 1987088:
  `15 of 30 inputs failed verification`, the 15 changed regions). NC-L1 (Slurm 1987388, backup panels): one-per-chrpos
  failed 15 / passed 15, and the PYHIN1 test failed. LIVE (Slurm 1987562): 30/30, PYHIN1 pass, reconcile 30/30.
  NC-L2 (one PYHIN1 kept_snv row deleted from a tmp copy): reconcile failed 1 / passed 29. Task 2 verify (Slurm
  1987641): 280 passed.
- M2 re-run with the unchanged script (Slurm 1987089):
  - A3_ukb: m2_chrpos_extra == 0 in 145/145 new-catalog fits (MC4R_18q21, PYHIN1_1q23, NC_NULL_06 asthma: 0); 0 of 815
    overall.
  - The 1,340 non-A3_ukb rows equal 15.5a's (sorted lines). Non-UKB panel rows are identical; UKB native chrpos_extra
    is 34 → 0.
  - The 15.5a validation holds for non-A3_ukb at 68/68. For A3_ukb it is 9/15 against the old-panel run_susie_rss counts,
    as expected: the 6 mismatches are fits whose subset lost 1–4 dropped variants. On the new panels it is 15/15 against
    the Task 3 measurement (below).
  - A3_ukb M3 deltas vs 15.5a (information): restricted_rows fell in 22 new-catalog fits (sum −37, max −4); 3 fits lost
    their M2 extra row. ov_snp_id_set / bridge fell in 10 new-catalog fits (−14), ov_chrpos_set in 3 (−3),
    ov_chrpos_bridge in 2 (−2). Nothing rose.

## Task 3: eligibility, DRAFT, close

- Run list: 15 A3_ukb keys of `run_list()` = 5 traits × {BMI_5q13_3 25,156; PYHIN1_1q23 27,268; SLC2A9_urate 17,980}.
  Array Slurm 1987407 (cascadelake, 1 h, 32G): 15/15 COMPLETED 0:0. summarise() accepted all 15 (early exits, no
  lbf_variable). No file under data/r4/results is newer than run.sh. Driver: `data/r4/tmp/w3f/ukbbi/elig.py` (the
  module's CLI has no arm filter). The other 68 measured rows come from the 15.5 measurement through the same
  summarise(), and the table is rebuilt with eligibility_table().
- Eligibility: 815 rows = 83 measured + 732 bound, 10 not eligible. A3_ukb: 145 = 15 measured + 130 bound; not eligible
  4 → 4. 70 A3_ukb lines change (panel_n_var and panel_sha256 in 14 admissible changed regions × 5 traits; n_variants in
  6 measured rows). The other 670 lines are byte-identical (`cmp`). A3_ukb n_variants == the 15.5b m123 restricted_rows
  15/15, and n_variants_pre_ld == joined_rows 15/15.
  - asthma × PYHIN1_1q23 A3_ukb: 22,083 → 22,080 (−3, within the −8 bound).
  - Other measured changes: asthma BMI 20,637 → 20,635, asthma SLC2A9 14,264 → 14,263, t2d BMI 17,440 → 17,437,
    t2d PYHIN1 18,942 → 18,938, t2d SLC2A9 12,041 → 12,040.
- DRAFT:
  - Panel-size row: UKB native 35,673 / 27,268 / 25,156 / 17,980, re-read from the manifest; cites 3c1ed352.
  - Measured-count row: the A3_ukb clause re-measured (1987407); count unchanged at 4 of 145.
  - M2 OPEN → RESOLVED row.
  - Analysis-code row and (m) list: + 526fd5c7, 3c1ed352, `src/python/ta_r4/ukb_native_multiallelic.py`.
  - PASTE (c): the disclosure (31 positions; 7 positions / 14 variants removed; 17,071 indels kept).
  - The (k) count clause is unchanged, because its A3_ukb number (4 of 145 / 14 of 100) did not move.
  - confirmatory_sha256 recomputed: 9fa410aa…88d5, unchanged. test_amendment_text: 21P/2S; no test pinned UKB numbers.
  - NC: "a salvage" inserted into the new sentence makes `test_draft_extract_framing` fail; the file was restored
    sha256-identical. Extract 4,127 → 4,208 words.
- Wave close: QUICK (Slurm 1987855): 748P/2S, 154.1 s pytest / 171.5 s wall (over the 120 s budget, carried to 15.6); per id vs the pre-test baseline 1985965 (738P/2S): 0 removed, 10 added, 0 outcome changes. PINS 39P. HEAVY 306P/5S, 1,962 s; vs `elig_20261118/heavy_15_5.xml` (244P/5S): 0 removed, 62 added (the 61 live pins + T-f), 0 outcome changes. FULL (Slurm 1987856, 3,512 s): 2,535 ids = 2,480P + 53S + 2F; vs `elig_20261118/full_15_5.xml` (2,463 = 2,408P/53S/2F): 0 removed, 72 added (all tests/ta_r4: 10 + 62), 0 outcome changes, tests/m3 0. The 2 failures are the deferred tests/m3 test_variant_catalog_fallback_legacy_semantics pair (15.6); not fixed. tests/m3/sparse_parent_benchmark.tsv timing rewrite restored to HEAD.

## Deviations from Plan

1. **[Rule 2] n_pairs_zero_filled for the final panel.** build_native's stats count zero-filled pairs over the
   pre-drop frame. The new module recomputes them for the kept rows from per-tile 4-key membership. The identity job
   re-derived both values from `assemble_region(return_filled=True)` (15/15). n_var is likewise the final count.
   Other stats keys are build_native's.
2. **[Rule 2] Extra tests and controls.** T-i (CLI writes rds + stats + audit), a CHR-keyed/order test, NC-8 for T-e, and
   a control proving the empty `--list-code-changes` filter can print.
3. **[Rule 1] Live-pin test bug, first draft.** The reconcile test used `.sum()` on an empty object Series (regions
   with no audit rows) and raised ValueError (Slurm 1987388). Fixed to a plain count; LIVE and NC-L2 were rerun (1987562).
4. **A3_ukb M2 validation.** The 15.5a 83/83 validation compares with run_susie_rss counts on the old panels. It can
   only reproduce exactly where nothing was dropped: 68/68 non-A3_ukb and 9/15 A3_ukb. The A3_ukb validation on the new
   panels is the Task 3 measurement, at 15/15.
5. **Eligibility driver.** `elig.py` wraps the module's own functions, because its `plan` / `summarise` CLI covers all
   83 keys.
6. **FULL baseline.** FULL was compared with the 15.5 FULL (`elig_20261118/full_15_5.xml`), as the brief directs; the
   plan text names the older 15.5a XML.
7. **No push**, per the brief.

## Known Stubs

None.

## Threat Flags

None. No new network, auth or trust-boundary surface. The audit sidecars live under data/r4 (D-11).

## Self-Check: PASSED

Files: the module, its test, ukb_native_multiallelic_resolved.tsv, the three reply files and this SUMMARY were found. Commits 5ca20376, 526fd5c7, 3c1ed352 and 07dae0c0 were found, all ancestors of HEAD. Every changed path is in files_modified. ukb337k_tiles.py, run_coloc_pair_r4.R, run_susie_rss.R and catalogs_sha256.tsv are unchanged, and no other panels_*.tsv changed. Nothing was pushed.
