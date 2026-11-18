---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5a
slug: W3f-catalog-dupkey-producer-and-guard
subsystem: ta-r4 variant catalogs / frozen fitting script
tags: [ta-r4, W3f, catalog, duplicate-keys, run_susie_rss, D-28, re-pin]
requires: [ta-r4-W3f-reporting-widening-qtl-sim]
provides: [r4 catalogs one row per normalized allele key, --require-unique-allele-key guard, re-pinned catalogs_sha256 r4 rows, catalogs_r4_unique_key.tsv]
affects: [ta-r4-W3f-eligibility-measurement-and-draft (15.5 remainder), W4a-T3 lock (new OPEN row), W6 QTL layer (M3 flag)]
tech-stack:
  added: []
  patterns: [line-level dedup with byte-preserving audit file, flag-gated frozen-script guard, shared-clone pre/post differential]
key-files:
  created:
    - src/python/ta_r4/catalog_unique_key.py
    - tests/ta_r4/test_catalog_unique_key.py
    - tests/ta_r4/test_unique_allele_key_guard.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_unique_key.tsv
  modified:
    - .planning/DECISIONS.md
    - src/python/ta_r4/paths.py
    - src/snakemake/rules/ta_r4_panels.smk
    - src/legacy/region_analysis/scripts/run_susie_rss.R
    - src/python/ta_r4/commands.py
    - tests/ta_r4/test_json_cs_equals_fit_sets.py
    - tests/m3/test_source_freeze_pins.py
    - tests/ta_r4/test_live_pins.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - DEC-2026-11-17-ta-r4-catalog-unique-allele-key (r4 catalogs one row per normalized CHR:POS:REF:ALT; rsid-first choice rule; dropped rows audited)
  - DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze (D-28 lifted once; flag default false)
metrics:
  completed: 2026-11-18
  tasks: 3
---

# Phase ta-r4 Plan 15.5a: r4 catalog duplicate-key producer fix + run_susie_rss.R guard Summary

The 31 r4 variant catalogs now hold one row per normalized CHR:POS:REF:ALT (877,756 -> 629,499 rows; every dropped
row kept byte-for-byte in `variants_r4_dropped/`), `run_susie_rss.R --require-unique-allele-key true` stops any R4 fit
whose panel-restricted subset still repeats a key, `R_CODE_REF` names the guard commit, and every catalog-derived panel
rebuilt byte-identical. Nothing pushed.

## Commits

| Task | Commit | What |
|---|---|---|
| 1 step 0 | c6c450fc | DECISIONS.md: the two DEC-2026-11-17 entries (append-only; reply file was already committed in 79ff8dc2) |
| 1 | e9c0d400 | producer `ta_r4.catalog_unique_key`, `paths.catalog_raw_path` / `catalog_dropped_path`, rule split, tests |
| 2 | 13b0821c | `run_susie_rss.R --require-unique-allele-key`, `commands.fit_command` argv, guard tests, json_cs spec update |
| 2 | 3f4d0cb9 | `R_CODE_REF` 1f77128 -> 13b0821 |
| 3 | 30b13692 | catalogs_sha256.tsv (30 r4 rows), catalogs_r4_unique_key.tsv, test_live_pins.py, DRAFT Pre-Paste OPEN row |
| 3 | (docs commit with this SUMMARY) | LOG entry, STATE.md RESUME block, this SUMMARY |

A commit by another session (e3a69e48, "docs(handoff): session close — 15.5a executing", HANDOFF.json / STATE.md /
.continue-here.md) landed between c6c450fc and e9c0d400. It is linear history; I did not touch HANDOFF.json.

## Precondition (Task 1 step 0)

- reply sha256 `72a6254ade39b0180b241725be2bf4d981ae1fc2f5b8a5a303a496bce8846653`; `od -c` = `1. Fix both ends (recommended).\n`.
- hand-back sha256 `cb52ce1a8ad5b7e8dd4020ad064e022b7998bdeca2716be5eb6806423f0d5ebd`; lines 109-111 copied with `sed -n` into the DEC
  (verified by `grep -F -x -f`: 3/3 lines present).
- DEC heading count 2; `git diff` of DECISIONS.md had 0 removed lines.

## Task 1 — producer

- Baseline before any edit (Slurm 1959890): QUICK 719P/2S + in_job_gate/armed_e2e 26P, 747 ids (`baseline_t1.txt`).
  The first baseline attempt (1957105) collected my just-written RED test under `-x`; I discarded it
  (`baseline_t1.CONTAMINATED.txt`), moved the two new files aside and re-ran it.
- RED (`red_t1.txt`): `18 failed in 1.71s`, every one `ModuleNotFoundError: No module named 'ta_r4.catalog_unique_key'`.
- GREEN: 18 passed.
- Negative controls (each restored sha256-identical to b3909a68…6613, `nc_p_t1.txt`):
  - NC-P1 (no strip/upper): 5 failed (b, c, i, multiset/key-set, stats).
  - NC-P2 (CHR:POS key): 4 failed (d, e, multiset/key-set, stats).
  - NC-P3 (chr:pos ranked above rs): 4 failed (a, b, c, f).
  - NC-P4 (pandas re-serialise): 4 failed (no-dup byte identity, no-trailing-newline, multiset, input order).
- After the rule split (Slurm 1959941): 737P/2S + 26P; per-id diff vs baseline = 18 additions (the new file), 0 changes.
- Dry-run (catalog + control targets): r4_catalog_raw 31, r4_catalog_unique 31, total 62; 0 jobs for the 12 legacy
  catalogs, 22 repro_routeC panels and 24 k2d targets. `--list-code-changes` and `--list-params-changes` over the
  control targets printed nothing (the outputs have .snakemake metadata, so the listings were not vacuous).

## Task 2 — guard

- RED (Slurm 1959972): 7 failed / 1 passed. Optparse: `long flag "require-unique-allele-key" is invalid`; argv case
  `assert 0 == 1` (flag absent). The passing one was the flag-absent differential (live script == 1f77128 code).
- GREEN (Slurm 1960033): 89 passed / 1 failed; the failure was `test_command_runs_the_frozen_script`'s
  `git diff --quiet HEAD -- run_susie_rss.R`, i.e. the uncommitted edit. After the commit, the Task 2 verify job
  (Slurm 1960833; guard, cap_after_panel, json_cs, pins, ld_read_path, finemap_receipt, armed_e2e): 94 passed.
- Negative controls (Slurm 1960058; each restored sha256-identical):
  - NC-G1 (guard after the cap): `test_guard_runs_before_cap` failed.
  - NC-G2 (silent dedup `subset <- subset[!duplicated(k)]`): dup-catalog and sumstats-dup cases failed (the fit then
    died later on "orientation vector is out of step", not on DUPLICATE_ALLELE_KEYS).
  - NC-G3 (flag dropped from fit_command): argv case failed.
  - NC-G4 (default "true"): differential [None] failed, [false] passed.
- Pins: RED 2 failed / 37 passed (`test_run_susie_rss_whole_file_code_is_frozen`, `test_the_k3_comment_fix_did_not_move_the_code_pin`
  clause i) -> GREEN 39 passed after the re-pin. K3_PRE_FIX_REF / K3_FIX_REF unchanged.
- Differential VOLATILE fields: none. The JSON dicts are compared whole and the RDS by md5; the script writes no timing
  field and every path argument is repo-relative.
- Pre-existing frozen-script suites (step 6), Slurm 1960133: at e9c0d400 (a `git clone --shared` in the scratchpad
  with data symlinks) and at HEAD, 165 passed / 1 skipped each, per-id identical.

## Task 3 — rebuild, verify, re-pin, measure

- Space: 28T free on /rs1. Backup (Slurm 1960208): every copy's SHA256SUMS verified against its live origin
  (old_variants_r4 31; AFR661/AFR504/identity 10 each; EUR_ukb337k_r4 30; native stats 30; AFR work dirs 70 + 70, an
  addition to the plan's list because the fire rewrites them); pre_panels.sha256 (90) == backup sums;
  pre_untouched.sha256 203 files.
- Dry-run: r4_catalog_raw 31, r4_catalog_unique 31, r4_panel_afr_1kg 20, r4_identity_payload_afr 10,
  r4_panel_ukb_native 30 = 122. Control listings empty. Fire: `122 of 122 steps (100%) done`; Slurm 1960869..1961081,
  122 jobs COMPLETED 0:0. Post-fire dry-run over all 179 targets (controls included): "Nothing to be done".
- Identity checks (Slurm 1961192), all components equal the planning measurement:

| Check | Result |
|---|---|
| (a) raw sha256 == old pins | 31/31 |
| (b) kept + dropped == raw multiset; key sets equal | 31/31; 31/31 |
| raw rows | 877,756 |
| dropped exact + case_ws | 248,251 + 6 = 248,257 |
| kept | 629,499 = 877,756 − 248,257 |
| groups | 248,239 pairs + 9 triples = 248,248; extra 248,239 + 2×9 = 248,257 |
| SNP_ID forms | {chr:pos, rs} 248,234 / {chr:pos, rs, rs} 9 / {rs, rs} 5 = 248,248 |
| kept row not first occurrence | 234,677 of 248,248 groups |
| normalized duplicates in kept | 0 |
| CHR:POS extra | 294,400 raw -> 46,143 kept at 46,132 sites |
| catalogs with duplicates | 30 of 31; BMI_Xq24 kept == raw bytes |
| empty SNP_ID / in a dup group | 14,799 / 0 |
| whitespace cells / lowercase-allele rows | 0 / 17 |
| (d) panel .rds + UKB stats byte-identical | 90/90 |
| (e) untouched files | 203/203 |

- Re-pin: catalogs_sha256.tsv 30 r4 rows changed, 0 legacy rows (BMI_Xq24 row unchanged). catalogs_r4_unique_key.tsv
  31 rows; totals equal (c). No panel manifest changed.
- test_live_pins (r4_heavy): RED (Slurm 1961205) 2 failed / 35 passed — `30 of 43 inputs failed verification` and
  catalogs_r4_unique_key.tsv absent. GREEN 99 passed. NC-L1 (uniqueness test pointed at old_variants_r4): 30 failed /
  1 passed. NC-L2 (FTO_16q12 16:53800387 G/A rs12446228 dropped from a tmp copy): kept+dropped==raw and key-set tests
  both failed. I split the first draft's single test into three so the key-set test is observed failing on its own
  (in the first draft the multiset assert fired first).

### M1 / M2 / M3 (Slurm 1961203, 9 min; scripts in `data/r4/tmp/w3f/dupkey/`, not committed)

- Reproduction validated on old_variants_r4: restricted rows == measured n_variants 83/83, distinct == n_variants_distinct 83/83.
- 815 production fits. Post-restriction 4-key duplicates: old catalogs 1,167,258 extra rows in 815/815 fits; rebuilt 0.
- **M1:** 0 of 175 (trait, ancestry, region) windows.
- **M2:** 3 of 815 fits, 1 extra row each, all A3_ukb asthma.EUR: MC4R_18q21 18:56541713, PYHIN1_1q23 1:160680184,
  NC_NULL_06 6:81514622. Panel level: EUR_ukb337k_r4 34 sites in 14 of the 29 measured regions; every 1kg, identity
  and isect panel 0. Checker `multi.pkl`: 38 sites in 15 regions = 34/14 + HLA_6p21 4 sites (no admissible HLA fit).
  The plan text says 18 regions; the checker's own artifact says 15. Of the 6 asthma both-allele sites, 3 reach the fit
  subset; at BMI_5q13_3, NC_SLC24A5 and SLC2A9_urate one allele is a palindromic SNV that the allele-aware panel join drops.
  - FLAG FOR CARTER (Rule 4): M2 A3_ukb asthma.EUR MC4R_18q21 n=1 keys=18:56541713
  - FLAG FOR CARTER (Rule 4): M2 A3_ukb asthma.EUR PYHIN1_1q23 n=1 keys=1:160680184
  - FLAG FOR CARTER (Rule 4): M2 A3_ukb asthma.EUR NC_NULL_06 n=1 keys=6:81514622
  - DRAFT Pre-Paste OPEN row added (outside the PASTE block; gates W4a-T3). test_amendment_text 21P/2S.
- **M3:** the best-space bridged overlap fell in 39 of 815 fits (sum 1,529,761 -> 1,525,405), rose in 0: A3_ukb t2d 29
  (−4,316, max −735) and asthma NC_ABO / NC_TYR in 5 EUR arms (−8 per arm). Two measured causes: mixed rsid / chr:pos
  fit names (A3_ukb t2d 9p21: 498 chr:pos + 9,111 rs; snp_id space 7,851 -> 7,440, chr:pos space only the 498), and the
  14 rsid-to-smaller-rsid drops (NC_ABO 8, NC_TYR 1). FLAG FOR CARTER (M3). This approximates `ld_allele_join_indices`.

### Wave close (§C without push)

- QUICK (Slurm 1961268): 738 passed / 2 skipped, 173.4 s (over the 120 s budget; already carried to 15.6).
- PINS 39 passed. HEAVY 244 passed / 5 skipped in 1,897 s.
- FULL (Slurm 1961269): 2,463 ids = 2,408 passed + 53 skipped + 2 failed, 2,937 s. Compared with the W4a baseline
  (`data/r4/tmp/w4a/full_W4a.xml`, 2,069 = 2,017P + 52S): 400 ids added (all tests/ta_r4), 6 removed, 2 outcome changes
  (both tests/m3). **The acceptance line "0 removed ids, 0 tests/m3 outcome changes" is not met, and neither cause is
  15.5a's:**
  - the 2 failures (`test_variant_catalog_fallback_legacy_semantics::test_the_five_must_not_move_sites_are_byte_identical[too_many_variants_payload]`,
    `::test_the_symbol_scoped_diff_is_exactly_one_removed_line`) pass at 4a1b9d4a (11P) and fail from 6c6e9546 (15.1 N1
    cap move) on, including e9c0d400 before the guard, with the same assertion text. FULL was not run in 15.1–15.5;
  - the 6 removed ids are already absent at e9c0d400.
  Both are logged in `deferred-items.md` for Carter / 15.6 and not fixed here. The timing rewrite that the run made to
  tests/m3/sparse_parent_benchmark.tsv was restored to HEAD.

## Deviations from Plan

1. **[Rule 3] Baseline re-run.** The first baseline collected the new RED test; re-run with the new files moved aside.
2. **[Rule 2] Extra backup.** `data/r4/ld/work/{AFR661,AFR504}_1kg_r4/` (70 files each) backed up and verified, because
   r4_panel_afr_1kg rewrites them.
3. **[Rule 1] Live-pin test split.** One combined test became three so NC-L2 shows the key-set test failing by itself.
4. **Step-6 "before" run** used a shared clone at e9c0d400 rather than a checkout in the main tree, because three of
   the five suites compare the script with `git show HEAD`.
5. **15.5 PLAN frontmatter** was already committed in 79ff8dc2, so there was nothing to commit for it.
6. **Plan numbers corrected by measurement:** UKB multi-allelic sites span 15 regions, not 18; 3 of the predicted 6
   asthma sites reach a fit (palindromic alleles), so M2 = 3 fits, not "4 confirmatory".

## Out of scope, for Carter

- 11 non-duplicate lowercase-allele rows in the r4 catalogs (17 − 6 twins). They are probably excluded from the UKB native
  panels by the case-sensitive `_allele_keys`. Not touched.
- `variants_legacy` keeps 29,363 normalized duplicate rows (planning measurement). Track B allele-aware fits read them. Unchanged (D-15).

## Pins changed

- `R_CODE_REF`: 1f77128 -> 13b0821.
- catalogs_sha256.tsv: 30 r4 rows (n_rows, size_bytes, md5, sha256). For example, 9p21_CDKN2A sha256
  462a355e…a0a0 -> 5e17c5e5…5902. Every old -> new value is in `git diff 3f4d0cb9 30b13692`.
- New: catalogs_r4_unique_key.tsv (31 rows).

## Known Stubs

None.

## Threat Flags

None. No new network, auth or trust-boundary surface. The new audit dirs `variants_r4_raw/` and `variants_r4_dropped/`
live under data/r4 (D-11).

## Self-Check: PASSED

Files: catalog_unique_key.py, both new test files, catalogs_r4_unique_key.tsv, this SUMMARY: found. Commits c6c450fc, e9c0d400, 13b0821c, 3f4d0cb9, 30b13692: found. `R_CODE_REF = "13b0821"`: present.
