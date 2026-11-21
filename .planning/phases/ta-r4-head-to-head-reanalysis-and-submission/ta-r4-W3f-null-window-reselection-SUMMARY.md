---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7h
slug: W3f-null-window-reselection
subsystem: ta-r4 GWAS-null negative-control windows / UKB tiles / NC_NULL catalogs and EUR panels / OSF amendment DRAFT
tags: [ta-r4, W3f, 15.7, F9, negative-controls, UKB, DRAFT]
requires: [ta-r4-W3f-qtl-sweep-gwas-pph4]
provides: [null-window selection on the production inputs, superseded selection kept, 6 UKB tiles + 12 manifest rows, 8 rebuilt NC_NULL catalogs and 40 EUR panels re-pinned row by row, NC_NULL eligibility rows, DRAFT Pre-Paste/(c)/(l)]
affects: [ta-r4-W3f-proxy-asthma-refit (15.7h2), ta-r4-W3f-15-7-review-suite-and-close (15.7j), W4a-T3 lock]
tech-stack:
  added: []
  patterns: [driver identity on the superseded inputs before trusting it on new ones, per-row re-pin after the recipe reproduces every other row byte for byte, whole-tree before/after sha256 snapshot]
key-files:
  created:
    - tests/ta_r4/test_null_windows_production_pool.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/null_windows_selection.superseded-2026-10-21.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7h-repin-and-draft-reply-2026-11-21.txt
  modified:
    - .planning/DECISIONS.md
    - src/python/ta_r4/select_null_windows.py
    - tests/ta_r4/test_null_windows.py
    - config/ta_r4/regions_r4.csv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/null_windows_selection.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb337k_tiles_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_unique_key.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb_native_multiallelic_resolved.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_r4.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_identity_r4.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_isect_r4.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_isect_r4.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - "DEC-2026-11-20-ta-r4-null-window-reselection (Carter, Q-F9 A): selection re-run on the production inputs, rule and seed unchanged; superseded draw kept and disclosed"
  - "Carter 2026-11-21 Q1 'Commit them (Recommended)': catalogs_r4_unique_key.tsv and ukb_native_multiallelic_resolved.tsv re-pinned (8-window rows only)"
  - "Carter 2026-11-21 Q2 '(a) Fix line 80 now (Recommended)': PASTE (c) UKB counts from the rebuilt panels; Pre-Paste line 33 (dated 15.5b record) unchanged"
metrics:
  completed: 2026-11-21
  tasks: 3
---

# Phase ta-r4 Plan 15.7h: W3f null-window re-selection on the production inputs Summary

The GWAS-null windows are now a seeded draw (seed 20261021, rule unchanged) from the 2,886-candidate pool the
corrected inputs define. The superseded 2,865-candidate draw is kept and disclosed. 2 windows (NC_NULL_07, NC_NULL_09)
are unchanged; the 8 others were rebuilt from 6 newly fetched, checksum-verified public UKB tiles and the on-disk 1000G
EUR bfiles, and only their manifest rows were re-pinned. Every other catalog and panel is byte-identical. No fit was run
on a null window. Nothing is pushed.

## Commits

| Task | Commit | What |
|---|---|---|
| 1 DEC | 6fffde86 | DEC-2026-11-20-ta-r4-null-window-reselection (Q-F9 reply quoted verbatim) |
| 1 | 0e6dda24 | driver `path`-keyed manifests; 4 tests; new selection; superseded selection; 12 tile rows |
| 2 | 350cd9b9 | regions_r4.csv; 8 manifests re-pinned (8-window rows); eligibility; declared spec update; DRAFT; PLAN-INDEX §A; Carter 15.7h reply file |
| 3 | (this commit) | LOG, STATE, PLAN-INDEX COMPLETE, this SUMMARY |

## Task 1: gate, driver identity, re-selection, tiles

- Gate `gate_reply.py Q-F9`: "A: Re-run the selection on the production inputs (Recommended)", c2cc9915…cc089, rc 0.
- Driver: `manifest_sha256()` accepts `path`-keyed manifests (trailing-component match); `relative_path` manifests by
  file name as before; conflicting or absent → None → exit 2. No rule change.
- Identity (Slurm 2017268): superseded inputs, checked against `sumstats_r4_sha256.tsv` by path → byte-identical to the
  superseded selection, candidates 352c77ec…dcce9.
- Production (Slurm 2017289): 2,886 candidates (a0067cc7…9b37, byte-equal to the planning probe); vs the old pool 2,745
  shared / 120 dropped / 141 added; all 10 old windows remain candidates. Window map (old → new):
  01 1:99500001 → 1:99750001; 02 1:218750001 → 1:232000001; 03 2:190000001 → 2:202500001; 04 3:30750001 → 3:34000001;
  05 3:178250001 → 3:191500001; 06 6:81500001 → 6:82750001; 07 11:21500001 same; 08 13:38500001 → 13:42000001;
  09 13:71000001 same; 10 14:49000001 → 14:49250001.
- Feasibility: missing tiles = the 6 in the plan; bfiles for 1, 2, 3, 6, 11, 13, 14 present; region_tiles of the 20 other
  autosomal regions unchanged by the new rows (0 of 20).
- Compute nodes cannot reach S3 (Slurm 2017274, curl rc 28); fetched on login02 with `fetch_tile`, nice, one tile at a
  time: 6,470,831,032 bytes in 90 s. Re-verified from disk (Slurm 2017319): size, md5, sha256, magic and ETag 12/12
  (.npz multipart ETag reproduced with 32 MiB parts). Tile manifest 76 → 88; first 77 lines byte-identical.

## Task 2: rebuild, re-pin, eligibility, DRAFT

- regions_r4.csv re-emitted: 8 rows; equals `regions_r4_text()`; pair_manifest.tsv unchanged.
- Fire `bin/r4_fire.sh repro repro_routeC` over 88 targets: dry-run 48 jobs (8 windows × 6 rules); Slurm 2017707–2017862,
  48/48 COMPLETED 0:0; post-fire dry-run "Nothing to be done". Old artifacts backed up (`$Q/c157h/old_nc_null/`, 128 files).
- Byte identity (pre Slurm 2017291 / post 2017920; 822 files under data/r4/ld + manifests + config/ta_r4): 702
  identical; 117 changed files are the 8 windows' artifacts, 3 are the named files; 0 added/removed; NC_NULL_07/09 32/32.
- Re-pin (Slurm 2017965): the recipe reproduced every other row byte for byte (catalogs 35/35, unique_key 23/23,
  EUR_1kg 21/21, identity 21/21, 1kg_isect 21/21, ukb native 22/22, ukb_isect 21/21, resolved 66 rows), then only the 8
  windows' rows were replaced; 0 changed lines outside them in all 8 files. Live pins 160 passed (Slurm 2020806).
- Eligibility (Slurm 2018025, cascadelake): run list 83 (no NC_NULL key); 815 rows = 83 measured + 732 bound, 10 not
  eligible (unchanged); 250 NC_NULL rows bound (max panel n_var 2,349); 200 rows of the 8 windows change, 616 other
  lines identical; no results file newer than the job. DRAFT (k) unchanged.
- DRAFT: Pre-Paste null-window row (line 42) and (l) (line 126) per the plan; PASTE (c) line 80 (Carter Q2 a):
  31 → 30 positions, 7 / 14 → 6 / 12, 17,071 → 16,843, derived in Slurm 2021384 from all 30 rebuilt panels; the same
  script on the pre-rebuild panels reproduces 31 / 7 / 14 / 17,071. Line 33 unchanged. test_amendment_text 21 P / 2 S.
- Task 2 verify (Slurm 2020806): 61 passed, 2 skipped.

## Task 3: FULL

- FULL Slurm 2021566 (cascadelake c020n01, HEAD 350cd9b9): QUICK 851 P / 2 S; HEAVY 330 P / 5 S; PINS 39 P; FULL
  2,682 = 2,629 P / 53 S / 0 F. vs full_15_7g.xml (`junit_cmp.py`): 0 removed, +4 (all tests/ta_r4, all passed), 0
  outcome changes, tests/m3 0; declared spec update passed → passed; the 4 other selection-touching ids passed in both.
  `$Q/check_15_7h.py` CHECK PASS rc 0; its 3 NCs (base as new; synthetic failure on the declared id; on
  test_regions_r4_is_rebuilt_from_sources) each CHECK FAIL, rc 1 (`$Q/check_15_7h_nc.txt`).

## RED → GREEN and negative controls

- RED (Slurm 2017257): tests 1, 2 `KeyError: 'relative_path'`; test 3 failed; test 4 RED (NC_NULL_02) after the
  re-selection, before the fetch. GREEN: Slurm 2017268, 2017310.
- NC-1 superseded min_p mutated → tests 1, 3 fail; NC-2 canonical = superseded → tests 2, 3 fail (Slurm 2017530);
  NC-4 pre-fetch tile manifest → test 4 fails; NC-5 conflicting `path` row → None, driver rc 2; NC-D / NC-D2 "salvage"
  inserted in each new DRAFT sentence → test_draft_extract_framing fails; NC-L HEAD catalogs_sha256 → live pin fails on
  exactly the 8 windows. Each mutated file restored sha256-identical.

## Declared spec updates

tests.ta_r4.test_null_windows::test_real_selection_reproduces_committed

## Deviations from Plan

1. **[Rule 3, Carter-approved] Two manifests outside `files_modified` re-pinned.** catalogs_r4_unique_key.tsv and
   ukb_native_multiallelic_resolved.tsv describe the rebuilt raw/dropped catalogs and native audit sidecars;
   test_live_pins requires them. Only the 8 windows' rows changed. Approved by Carter 2026-11-21 Q1 "Commit them
   (Recommended)", `W3f-carter-15-7h-repin-and-draft-reply-2026-11-21.txt` (sha256 5256b58d…9c60).
2. **[Carter-approved] DRAFT PASTE (c) line 80 updated** (not named in the plan) because the rebuild moved its UKB
   counts; Carter Q2 "(a) Fix line 80 now (Recommended)", same reply file.
3. **Order:** the superseded copy was made before the RED run, so test 1's RED isolated the KeyError.
4. **Fetch on the login node** (compute nodes cannot reach S3), as the plan's fallback allows.
5. **Re-pin memory:** the first re-pin job (Slurm 2017926, 16G) ran out of memory on the HLA UKB panel and wrote
   nothing; re-run at 64G (2017965).
6. **Tile ETag format:** `fetch_tile` writes the ETag with its quotes; the existing rows were rewritten without quotes in
   0e621884. pandas reads both identically; `ukb337k_tiles.py` (a Snakemake code input) was not changed.
7. **Session interruption:** the run stopped at ~07:27 when the parent restarted and was resumed with Carter's approval;
   every uncommitted edit was re-checked against `$Q/c157h` records and sacct before commit 3.
8. No push.

## Known Stubs

None.

## Threat Flags

None. The S3 download is the planned trust boundary (T-r4-157h-01), mitigated as planned plus the multipart ETag check.

## Self-Check: PASSED

Commits 6fffde86, 0e6dda24, 350cd9b9 are ancestors of HEAD; the test file, superseded selection, Carter 15.7h reply file and this SUMMARY exist. Every changed path since 63083a1d is in files_modified or one of the two Carter-approved manifests and the reply file. src/tests/config clean after FULL. decision_rules.yaml locked: false. Nothing pushed.
