---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5b
slug: W3f-ukb-panels-biallelic
type: execute
wave: 15.5b
depends_on: ["ta-r4-W3f-catalog-dupkey-producer-and-guard", "ta-r4-W3f-eligibility-measurement-and-draft"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-m2-biallelic-ukb-reply-2026-11-18.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-ukb-no-snps-only-reply-2026-11-18.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-ukb-a1-keep-snv-reply-2026-11-18.txt
  - .planning/DECISIONS.md
  - src/python/ta_r4/ukb_native_multiallelic.py
  - src/snakemake/rules/ta_r4_panels_afr_ukb.smk
  - tests/ta_r4/test_ukb_native_multiallelic.py
  - tests/ta_r4/test_live_pins.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb_native_multiallelic_resolved.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - tests/ta_r4/test_amendment_text.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-ukb-panels-biallelic-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SUSIE-RSS-POLICY
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "Every EUR_ukb337k_r4 native panel holds at most one variant per CHR:POS. At a position with 2+ variants of which exactly one is an SNV (single-base REF and ALT, both in ACGT), that SNV is kept and the rest are dropped. At a position with 2+ variants and zero or 2+ SNVs, all of them are dropped. Single-variant positions are untouched, indels included (Carter: a1, no --snps-only)"
    - "Each rebuilt panel's R equals the old panel's R restricted to the kept rows, exactly; the variants frame equals the old frame minus the dropped rows in the same order; 76 variants at 38 positions in 15 regions are resolved into 31 kept_snv + 45 dropped (31 one-SNV positions, 7 no-SNV positions, 0 multi-SNV positions), reconciled per region"
    - "PYHIN1_1q23 1:160680184 keeps rs184461353 (A/G) and drops rs143145026 (the 14-bp indel), as the 1000G AFR661 panel does"
    - "Every non-UKB-native panel, catalog, isect panel, isect stats file and non-UKB manifest is byte-identical before and after; a dry-run over their targets lists 0 jobs"
    - "M2 on the rebuilt panels: 0 of 145 A3_ukb fits carry a duplicated CHR:POS in the post-restriction subset; every non-A3_ukb row of the M1/M2/M3 table equals 15.5a's"
    - "A3_ukb eligibility (15 measured fits) is re-measured with the 15.5 module on the rebuilt panels; the A3_ukb rows of w3f_fit_eligibility.tsv, the DRAFT (k) count clause and the Pre-Paste panel-size and count rows show the new numbers; the M2 OPEN row is replaced by a resolved row; the DRAFT states the rule follows 1000G at SNV+indel sites, drops the 7 no-SNV positions, and keeps indels elsewhere (1000G panels are SNV-only)"
  artifacts:
    - path: "src/python/ta_r4/ukb_native_multiallelic.py"
      provides: "resolve_multiallelic_positions(R, v) and the build-native entry point the native rule now calls"
    - path: "tests/ta_r4/test_ukb_native_multiallelic.py"
      provides: "RED-first fixture tests (SNV+indel keeps SNV; indel+indel drops both; SNV+SNV drops both; lone indel kept; real PYHIN1 1:160680184), R submatrix exactness, rule wiring"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv"
      provides: "30 rows re-pinned (md5, sha256, size, n_var) plus n_sites_multiallelic / n_sites_kept_snv / n_sites_dropped_all / n_var_dropped_multiallelic columns"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb_native_multiallelic_resolved.tsv"
      provides: "one row per variant at a multi-variant position (region_safe, CHR, POS, SNP_ID, REF, ALT, n_at_pos, n_snv, class, action ∈ {kept_snv, dropped}); 76 rows = 31 kept_snv + 45 dropped"
  key_links:
    - from: "src/snakemake/rules/ta_r4_panels_afr_ukb.smk::r4_panel_ukb_native"
      to: "src/python/ta_r4/ukb_native_multiallelic.py"
      via: "shell: -m ta_r4.ukb_native_multiallelic build-native"
      pattern: "ta_r4.ukb_native_multiallelic build-native"
    - from: "src/python/ta_r4/ukb_native_multiallelic.py"
      to: "src/python/ta_r4/ukb337k_tiles.py::build_native / write_rds / _write_stats"
      via: "import; ukb337k_tiles.py itself is not edited, so r4_panel_ukb_isect is not re-triggered"
      pattern: "from ta_r4 import ukb337k_tiles"
---

<objective>
Gap closure for the 15.5a M2 finding, per Carter (three replies, 2026-11-18): (a) biallelic-only UKB panels; no
`--snps-only`; a1, keep the SNV. The UKB-native panel builder resolves every CHR:POS that carries more than one variant:
- exactly one SNV there → keep it and drop the rest;
- otherwise → drop the position.

The 30 native panels are rebuilt and re-pinned, M2 goes to 0, and A3_ukb eligibility and the DRAFT are updated.

Purpose: `run_coloc_pair_r4.R:439-440` refuses DUPLICATE_KEYS on CHR:POS. Three A3_ukb asthma.EUR fits hit it. The fix
goes in the panel producer, not in coloc.
Output: new builder module + tests, 30 rebuilt panels, re-pinned manifest, resolution audit manifest, updated
eligibility rows and DRAFT, DEC entry.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-catalog-dupkey-producer-and-guard-SUMMARY.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-eligibility-measurement-and-draft-SUMMARY.md
@.planning/amendments/osf-amendment-r4-DRAFT.md

Standing rules: PLAN-INDEX §A, §B (explicit-path staging only, never `git add .`/`-A`; RED first with observed
negative controls; pin behaviour, not text; a count is a claim, reconcile by component), §C wave close **without
`git push`**.

Slurm only: `sbatch -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t <limit> --mem=<m>`, always
`-t`. Rscript is not on PATH in jobs; use `$RSCRIPT` (absolute). Snakemake only through `bin/r4_fire.sh` (uses `$SMK`
and the `config/ta_r4/cluster_slurm` profile). Every r4_heavy pytest, panel read, the rebuild, the measurement and M2
run inside sbatch, never on the login node. Python: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11`.
Scratch: `data/r4/tmp/w3f/ukbbi/` (W=that path below).

**Forbidden:** push; production fits; repro re-fire; OSF posting; the W4a-T3 lock; n_regions_min; any edit to
`src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R`, `src/python/ta_r4/ukb337k_tiles.py`, the 1000G / AFR / identity /
isect panels, the catalogs (`catalogs_sha256.tsv`), `run_susie_rss.R`, Track B (`tests/m3` code paths, `variants_legacy`).
Nothing under `data/r4/results`.

**Carter's decisions (record; quote byte-for-byte via `cat`, never retype):**
- `W3f-carter-m2-biallelic-ukb-reply-2026-11-18.txt`, sha256 `4d0b22414174958ee942d7a536955f7a8e08ff522b4cc34d7927bbf8f2028738`:
```text
go with (a), biallelic-only UKB panels
```
- `W3f-carter-ukb-no-snps-only-reply-2026-11-18.txt`, sha256 `38f9bfdcd051c3437827666e12f6c7f765ea1b1296c2cc6f9b922b256dedd7db`:
```text
biallelic only, no --snps-only
```
- `W3f-carter-ukb-a1-keep-snv-reply-2026-11-18.txt`, sha256 `597b6602b975dc9661d1acf2ad552a92997b202677b6f0dd3c1e33056d9bd177`:
```text
Question (2026-11-18): For the UKB panel fix (plan 15.5b): at the 31 positions where UKB has an SNV and an indel, should the panel keep the SNV, as 1000G effectively does (a1), or drop both variants (a2)? Both options fix the coloc CHR:POS stop.

Carter reply (verbatim, selected option): a1: keep the SNV (Recommended)
```

**The rule (per CHR:POS of the assembled native variant frame, after `build_native`'s catalog allele filter):**
- SNV := len(REF) == 1 and len(ALT) == 1 and REF ∈ {A,C,G,T} and ALT ∈ {A,C,G,T}.
- n_at_pos == 1 → keep it, whatever its type. Indels stay (no `--snps-only`).
- n_at_pos ≥ 2 and exactly one SNV → keep that SNV and drop the others (class `one_snv`).
- n_at_pos ≥ 2 and zero SNVs → drop all of them (class `no_snv`).
- n_at_pos ≥ 2 and two or more SNVs → drop all of them (class `multi_snv`). This is not a "prefer SNV" tie-break:
  with 2+ SNVs there is no single SNV to keep.

Why this follows 1000G at SNV+indel positions: PLINK `--biallelic-only strict` skips VCF *records* with 2+ ALT
alleles. 1000G Phase 3 stores an SNV and an indel at one position as two one-ALT records (measured: 1:160680184 G/A
+ G/GCCCGGGTTATATAA; 6:81514622 A/AGATG + A/G). `--snps-only just-acgt` then drops the indel and keeps the SNV:
AFR661_1kg_r4 PYHIN1_1q23 `.bim` has rs184461353 at 160680184. EUR_1kg_r4 is built from the LDSC 1000G.EUR.QC
bfiles without these flags; those bfiles have 0 indels and 0 duplicated positions (planner: chr1, 6, 18; the plan
checker: all 9,997,231 genome-wide bim rows, 0 non-ACGT-SNV alleles and 0 duplicated CHR:POS). The
remaining difference, to disclose: UKB panels keep indels at single-variant positions.

**Planning measurements (re-derive from the real panel files in Task 2; do not copy).**
Method:
- I replicated `build_native`'s selection from the tile `.gz` variant lists and the catalogs, without matrices. It
  reproduces every native stats `n_var` (30/30).
- Its 38 multi-variant positions include every duplicated CHR:POS that 15.5a measured on the real `.rds` files
  (`data/r4/tmp/w3f/dupkey/m123_panels.tsv`, 14 regions; that column lists at most 5 keys) plus the checker's HLA 4.
- The alleles come from the tiles.

Results:
- Totals over the 30 panels: n_var 189,945; 38 multi-variant positions, every one with exactly 2 variants
  (76 variants) → `one_snv` 31, `no_snv` 7, `multi_snv` 0.
- Kept 31 SNVs; dropped 45 = 31 indels at one_snv positions + 14 at no_snv positions. Every dropped variant is an indel.
- New n_var 189,900. Indels 17,116 → 17,071.
- Resolution manifest: 76 rows = 31 kept_snv + 45 dropped. Changed regions: 15.

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
| **total** | **189,945 (30 panels)** | **31** | **7** | **31** | **45** | **189,900** |

  The 7 no_snv positions each carry one rsid twice:
  - REF/ALT-swapped twins of the same indel: APOE 19:45030908 rs141810580; HLA 6:27493970 rs71546548, 6:33110578
    rs573601892, 6:34364092 rs544743846.
  - Two representations of one deletion: PYHIN1 1:161316535 rs57728204 (CAAAA/CA, CAAA/C).
  - Two different deletions under one rsid: 9p21 9:21997479 rs767353455; NC_NULL_01 1:99541424 rs145643692.

  Under the rule all 7 are dropped (information only).

  The three M2 sites are all one_snv:
  - MC4R 18:56541713 keeps rs201041665 T/G;
  - PYHIN1 1:160680184 keeps rs184461353 A/G;
  - NC_NULL_06 6:81514622 keeps rs544554403 G/A.

  Information only, not acted on: 414 more positions hold one variant in the panel but more than one in the UKB tiles,
  because the catalog filter removed the others. The rule is panel-level, so they stay.
- Consumers (grep-verified at planning):
  - `panels_EUR_ukb337k_r4.tsv`: written by `ta_r4.panel_manifest manifest`, then `ukb337k_tiles.add_stats_columns`
    joins `data/r4/ld/work/ukb337k/native/*.stats.tsv`. It is read by `validate_r4_fits` (receipt md5 vs manifest
    row), the finemap rule input and `test_live_pins` (`CATALOG_DERIVED` includes EUR_ukb337k_r4).
  - LOCKED_PATHS (`r4_lock_gate.py`) covers `manifests/panels_*.tsv`, `src/python/ta_r4` and the rule files. The lock
    is not yet taken, so nothing needs re-signing.
  - The input-sha-in-job gate (`commands.verify_command`) hashes sumstats and catalogs only, **not panels**. No
    catalog changes, so it is unaffected.
  - The A3_ukb arm (`arms.py`, `overlay_A3_ukb.yaml`) keeps the same path. No A3_ukb fits exist (`data/r4/results`
    has only the repro dirs).
  - The 15.5 measurement module `measure_fit_eligibility.run_list` reads panel `n_var` from the manifest.
  - The QTL bridge is **not** a consumer: its fit arms are A3_1kg, A2_identity and repro_routeL.
  - The simulation uses `EUR_ukb337k_isect_r4`, not native, so it is unaffected.
- Why a new module: `r4_panel_ukb_isect` lists `ukb337k_tiles.py` as an input, so editing that file would re-trigger
  the 58 isect targets on mtime. Isect panels already hold one UKB row per 1000G row (15.5a: 0 duplicates).
</context>

<interfaces>
src/python/ta_r4/ukb337k_tiles.py (read-only here):
  region_tiles(chrom, start, end) -> [(npz, gz)]; read_tile_variants(gz) -> DataFrame[SNP_ID, CHR, POS, REF, ALT]
  build_native(tile_list, chrom, start, end, catalog_tsv) -> (R ndarray n×n, v DataFrame[SNP_ID, CHR, POS, REF, ALT], st dict)
  write_rds(R, variants, out, ld_source, region_id, ancestry, ref_alt_source, rscript)
  write_native_panel uses ld_source "ukb337k_native", ref_alt_source "ukb_allele2_allele1" — reuse both literals
  _write_stats(path, region_safe, tiles, st); add_stats_columns(manifest, stats_dir, cols); read_rds(path, rscript, tmpdir)
  main(): subcommand build-native --region-id --region-safe --chr --start --end --stats --catalog --out
tests/ta_r4/test_ukb_tile_loader.py: _write_tile(tmp_path, name, M, pos, a1, a2, chrom) synthetic tile writer (reuse for the fixture)
src/snakemake/rules/ta_r4_panels_afr_ukb.smk::r4_panel_ukb_native (lines ~169-196): input tiles/catalog/code; output rds + stats; mem_mb 48000
data/r4/tmp/w3f/dupkey/targets.py: target sets r4cat legacycat repro k2d afr1kg afrid ukbnative ukbstats (extend for isect / EUR_1kg / EUR_identity)
data/r4/tmp/w3f/dupkey/measure_m123.R: the 15.5a M1/M2/M3 measurement (validated 83/83); output m123_fits.tsv
src/python/ta_r4/measure_fit_eligibility.py: the 15.5 module (measurement_argv, run_list, summarise, bound_row) — read its CLI and 15.5's SUMMARY for the exact invocation
</interfaces>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Precondition, DEC, RED-first multi-allelic resolver (a1), wiring and control dry-run</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-m2-biallelic-ukb-reply-2026-11-18.txt, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-ukb-no-snps-only-reply-2026-11-18.txt, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-ukb-a1-keep-snv-reply-2026-11-18.txt, .planning/DECISIONS.md, src/python/ta_r4/ukb_native_multiallelic.py, src/snakemake/rules/ta_r4_panels_afr_ukb.smk, tests/ta_r4/test_ukb_native_multiallelic.py</files>
  <read_first>
    - src/python/ta_r4/ukb337k_tiles.py (whole file), src/snakemake/rules/ta_r4_panels_afr_ukb.smk lines 145-230
    - tests/ta_r4/test_ukb_tile_loader.py (synthetic tile helpers)
    - .planning/DECISIONS.md, the two DEC-2026-11-17 entries (format to mirror)
    - 15.5's SUMMARY (must exist; see step 0)
  </read_first>
  <behavior>
    - resolve_multiallelic_positions(R, v) -> (R_kept, v_kept, audit, stats). Positions are keyed by (str(CHR),
      int(POS)) and the rule in <context> is applied. R_kept == R[np.ix_(keep, keep)] exactly. v_kept is v without the
      dropped rows, in original order, index reset. audit has one row per variant at an n_at_pos ≥ 2 position, with
      columns n_at_pos, n_snv, class ∈ {one_snv, no_snv, multi_snv} and action ∈ {kept_snv, dropped}. stats =
      {n_sites_multiallelic, n_sites_kept_snv, n_sites_dropped_all, n_var_dropped_multiallelic}
    - T-a: SNV G/T + indel G/GT at one POS → the SNV is kept, the indel dropped, and R_kept still holds the SNV's row/column
    - T-a2: SNV A/G + a single-base non-ACGT row A/* at one POS → the `*` row is not an SNV (n_snv = 1, class one_snv),
      so A/G is kept and A/* dropped
    - T-b: indel+indel at one POS (e.g. A/AAAAC and AAAAC/A, the measured swap pattern) → both dropped
    - T-c: SNV+SNV at one POS (A/C and A/G) → both dropped (class multi_snv)
    - T-d: a lone indel C/CA at its own POS → kept; a lone SNV → kept
    - T-e: no multi-variant position → outputs equal inputs (array_equal, frame_equal), stats all 0, audit empty
    - T-f (real data, r4_heavy, skip if the tiles are absent): read the PYHIN1_1q23 UKB tile variant lists with
      `ukb337k_tiles.read_tile_variants`. Keep the rows at 1:160680184 whose allele key is in the r4 catalog, and pass
      them with an identity R. The kept row is rs184461353 A/G; rs143145026 is dropped. First assert that UKB carries
      both rows. If UKB lacks rs184461353, the test fails with that message rather than skipping.
    - T-g: build_native_multiallelic(tiles, chrom, start, end, catalog) on synthetic tiles equals build_native + the
      resolver, and its stats dict carries the build_native keys plus the four new keys. The fixture must include a
      position where the raw tile list has 2 variants (an SNV and an indel) but the catalog allele filter keeps only
      one of them (the indel). That variant must be kept, and the position must not be counted as multi-allelic
      (catches resolving before the catalog filter; 414 such tile-only positions exist in the real data)
    - T-h, rule wiring: r4_panel_ukb_native invokes `ta_r4.ukb_native_multiallelic build-native` and lists the new
      module as an input; r4_panel_ukb_isect still invokes `ta_r4.ukb337k_tiles build-isect`. Check the parsed rule
      objects (Snakemake workflow API or ast), not docstrings.
  </behavior>
  <action>
    0. **Precondition (STOP if not met).**
       - `ta-r4-W3f-eligibility-measurement-and-draft-SUMMARY.md` and `manifests/w3f_fit_eligibility.tsv` must both be
         committed (`git log -1 -- <path>` non-empty). If either is not, STOP and report "15.5 not closed".
       - `git status --porcelain` must show none of the files_modified paths modified by another session. The three
         reply files may be untracked; that is expected. Anything else → STOP.
    1. **DEC before any code edit (per 15.1 / 15.5a).**
       - Verify the three reply files against the sha256s in <context>. For the two one-liners also check `od -c`.
         Any mismatch → STOP.
       - Append to `.planning/DECISIONS.md`. It is append-only: `git diff` must show 0 removed lines. Heading:
         `## 2026-11-18 — DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1: UKB native panels keep the single SNV at a multi-variant CHR:POS, else drop the position; no --snps-only (Carter)`.
       - The entry contains:
         - the decider;
         - all three file paths and sha256s, each reply in a ```text block inserted with `cat <file>`;
         - the 15.5a M2 options: (a) biallelic-only UKB panels; (b) coloc keys on the full allele key; (c) drop the
           indel in the affected fits only;
         - the a1/a2 sub-question as quoted in the third file;
         - the rule from <context>, including that multi_snv positions are dropped (not a tie-break);
         - the 1000G comparison and the remaining difference (UKB keeps indels at single-variant positions);
         - scope: the native builder + the 30 native panels + manifest/stats + the A3_ukb eligibility rows + the DRAFT;
         - not authorized: run_coloc_pair_r4.R, the 1000G/AFR/identity/isect panels, catalogs, Track B;
         - "lifts nothing under D-28".
       - Verify every line of each reply with `grep -F -x -f <reply> .planning/DECISIONS.md`. Use `grep -F -x` per
         non-empty line for the multi-line file.
       - Commit the DEC with the three reply files, staging exactly those four paths.
    2. Write `sha256sum src/python/ta_r4/ukb337k_tiles.py src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R` to
       `$W/start_code.sha256`. Run the QUICK baseline in sbatch (`-t 00:30:00`) **before** the new test file exists,
       and save it to `$W/baseline.txt`.
    3. RED: write tests/ta_r4/test_ukb_native_multiallelic.py per <behavior>. T-f is marked r4_heavy; the rest are
       unmarked. Run all of them, T-f inside sbatch. Each must fail on `ModuleNotFoundError: ta_r4.ukb_native_multiallelic`
       or on the unchanged rule shell. Paste to `$W/red.txt`.
    4. GREEN: create src/python/ta_r4/ukb_native_multiallelic.py with:
       - `is_snv`;
       - `resolve_multiallelic_positions`;
       - `build_native_multiallelic`: ukb337k_tiles.build_native, then the resolver, then merged stats;
       - `write_native_multiallelic_panel`: writes with ukb337k_tiles.write_rds using ld_source "ukb337k_native" and
         ref_alt_source "ukb_allele2_allele1", both unchanged; also writes the audit to
         `<stats stem>.multiallelic_resolved.tsv` next to the stats file;
       - `main()` with a `build-native` subcommand that takes the same arguments as ukb337k_tiles build-native.

       Do not edit ukb337k_tiles.py. Edit r4_panel_ukb_native only:
       - add input `code_ma="src/python/ta_r4/ukb_native_multiallelic.py"`;
       - add output `resolved=UKB_STATS.replace("{kind}", "native").replace(".stats.tsv", ".multiallelic_resolved.tsv")`;
       - change the shell module to `ta_r4.ukb_native_multiallelic`.
       All tests pass.
    5. Negative controls. Restore each one sha256-identical and paste the results to `$W/nc_t1.txt`. Each test above
       must be failed by at least one control:
       - NC-1, no-op resolver: T-a, T-b and T-c fail.
       - NC-2, drop every position with n ≥ 2 (option a2): T-a and T-f fail.
       - NC-3, generic prefer-SNV tie-break (keep the first SNV if any): T-c fails.
       - NC-4, `--snps-only` semantics (drop every non-SNV): T-d fails (lone indel).
       - NC-5, SNV test without the ACGT check (len == 1 only): T-a2 fails (the position then has 2 "SNVs" and is
         dropped).
       - NC-7, resolver applied to the raw tile variants before the catalog filter: T-g fails (the lone catalog
         indel is dropped).
       - NC-6, rule shell reverted to `ta_r4.ukb337k_tiles build-native`: T-h fails.
    6. Control dry-run (sbatch, `-t 00:30:00`): `bash bin/r4_fire.sh repro repro_routeC -n <targets>`.
       - Build the target list in `$W/targets.py`, extended from `data/r4/tmp/w3f/dupkey/targets.py`. It covers:
         - UKB native rds + stats (30 + 30);
         - every UKB isect and 1000G isect panel + isect stats (29 + 29 + 29);
         - EUR_1kg_r4, EUR_identity_r4, AFR661/AFR504/AFR661_identity;
         - the legacy repro and k2d panels;
         - all r4 and legacy catalogs.
       - Expected: `r4_panel_ukb_native 30` and 0 jobs for every other rule.
       - `--list-code-changes` and `--list-params-changes` over the non-native targets must both print nothing.
       - Non-vacuity control: `--forcerun r4_panel_ukb_isect` lists 29.
       - Any other count → STOP.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_ukb_native_multiallelic.py -q -rs -m "not r4_heavy" && git diff --quiet HEAD -- src/python/ta_r4/ukb337k_tiles.py src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R && sha256sum -c data/r4/tmp/w3f/ukbbi/start_code.sha256 && grep -c "DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1" .planning/DECISIONS.md</automated>
  </verify>
  <done>
    - The DEC and the three reply files are committed, each reply byte-matched.
    - T-a, T-a2 and T-b to T-h went RED and then GREEN, with T-f run in sbatch. NC-1 to NC-7 each failed as stated.
    - ukb337k_tiles.py and run_coloc_pair_r4.R are unchanged.
    - The dry-run lists exactly 30 r4_panel_ukb_native jobs, 0 for any other rule, and empty code/params listings.
    - Code commit: the module, the rule file and the test file, staged explicitly.
  </done>
</task>

<task type="auto">
  <name>Task 2: Back up, rebuild the 30 native panels on Slurm, prove the rebuild is an exact row/column deletion, re-pin, M2</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb_native_multiallelic_resolved.tsv, tests/ta_r4/test_live_pins.py</files>
  <read_first>
    - data/r4/tmp/w3f/dupkey/backup.sh (pattern), 15.5a SUMMARY "Task 3"
    - .planning/debug/resolved/asthma-eur-grch38-mislabel.md (the exact panel_manifest + add_stats_columns invocation used for panels_EUR_ukb337k_r4.tsv)
    - tests/ta_r4/test_live_pins.py, data/r4/tmp/w3f/dupkey/measure_m123.R
  </read_first>
  <action>
    1. **Backup with scripted restore** (sbatch, `-t 01:00:00`). `df -h /rs1/researchers/c/ckclinto` must show ≥ 40 GB
       free, else STOP.
       - First `git rev-parse HEAD > $W/t2_start_sha`.
       - `$W/backup.sh` copies with `cp -a`:
         - `data/r4/ld/EUR_ukb337k_r4/` → `$W/old/EUR_ukb337k_r4/`;
         - `data/r4/ld/work/ukb337k/native/` → `$W/old/native_stats/`;
         - the committed `panels_EUR_ukb337k_r4.tsv` → `$W/old/`.

         It writes SHA256SUMS for each copy, verifies each against its live origin, and refuses if `$W/old` exists.
       - Record `$W/pre_untouched.sha256` over:
         - every file under data/r4/ld/{EUR_1kg_r4, EUR_identity_r4, EUR_1kg_isect_r4, EUR_ukb337k_isect_r4, AFR661_1kg_r4, AFR504_1kg_r4, AFR661_identity_r4, legacy_repro, k2d_identity, variants_r4, variants_r4_raw, variants_r4_dropped, variants_legacy};
         - data/r4/ld/work/ukb337k/isect/;
         - every `$MAN/*.tsv` except panels_EUR_ukb337k_r4.tsv and w3f_fit_eligibility.tsv.
       - `$W/restore.sh`:
         1. scancel only the job ids listed in `$W/fire_jobids.txt` (never by name pattern; other sessions run `r4.*`
            jobs), then wait until `squeue -j <those ids>` lists none of them;
         2. `cp -a` the backups back;
         3. `sha256sum -c` them, which must be 100% OK;
         4. reset nothing and revert no commits.

         Exercise its verification half now; it must be 100% OK. Any later STOP runs restore.sh and reports.
    2. **Manifest reproduction control** (before the fire). Regenerate the manifest from the *current* panels into
       `$W/manifest_repro.tsv` with the exact committed invocation: `python -m ta_r4.panel_manifest manifest ...`, then
       `add_stats_columns` with cols `tiles, n_tiles, n_pairs_zero_filled, n_var_dropped_allele_mismatch`. Run it in
       sbatch with `$RSCRIPT`. `cmp` it to the committed manifest: it must be byte-identical, else STOP.
    3. **Real-panel recount, before the fire** (one sbatch job, `-t 01:00:00 --mem=96G`, `$W/recount.py`). Read the live
       panels, which at this point equal the verified backup, with `ukb337k_tiles.read_rds`. Read one region at a time
       and free each before the next (PYHIN1 is 27k², HLA 35k²). For each region list the multi-variant positions,
       n_at_pos, n_snv and class, and compare to the <context> table component by component:
       - positions and variants per region;
       - one_snv / no_snv / multi_snv = 31 / 7 / 0;
       - every position has exactly 2 variants;
       - every to-be-dropped variant is an indel;
       - PYHIN1 1:160680184 carries rs184461353 A/G and rs143145026.

       Any differing component → STOP before the fire and report both numbers. Do not edit the table to match.
    4. **Fire** via `bin/r4_fire.sh repro repro_routeC <30 native rds targets>` (cascadelake profile), logging to
       `$W/fire.log`. Append every Slurm job id the fire submits to `$W/fire_jobids.txt` as it is submitted (from
       fire.log), so restore.sh can cancel exactly those. Done =
       - `30 of 30 steps (100%) done`;
       - all 30 Slurm jobs `COMPLETED 0:0`;
       - the Task 1 target-list dry-run (controls included) prints `Nothing to be done`.

       Judge liveness by the output listing.
    5. **Identity checks**, one sbatch job (`-t 02:00:00 --mem=96G`). Write `$W/identity.py` and paste each result.
       The recount was done in step 3 and is not repeated here.
       - (a) For each of the 30 regions, comparing new (live) to old (`$W/old/...`):
         - the new variants == the old variants minus the audit's `dropped` rows, in the same order;
         - `np.array_equal(R_new, R_old[np.ix_(keep, keep)])`, exact, not allclose;
         - 0 duplicated (CHR, POS) in the new panel;
         - at every one_snv position the remaining variant is the SNV.
       - (b) Totals:
         - Σ new n_var = 189,900 = 189,945 − 45;
         - dropped = 31 (one_snv indels) + 14 (2 × 7 no_snv);
         - indels 17,116 → 17,071;
         - 15 regions changed, 15 unchanged in content.
       - (c) The audit sidecars together equal 76 rows: 31 kept_snv + 45 dropped. PYHIN1 1:160680184 has rs184461353
         kept_snv and rs143145026 dropped.
       - (d) `sha256sum -c $W/pre_untouched.sha256` passes at 100%.
    6. **Re-pin.**
       - Regenerate panels_EUR_ukb337k_r4.tsv with the step-2 recipe, with cols extended by
         `n_sites_multiallelic, n_sites_kept_snv, n_sites_dropped_all, n_var_dropped_multiallelic`.
       - Write `$MAN/ukb_native_multiallelic_resolved.tsv`: columns region_safe, CHR, POS, SNP_ID, REF, ALT, n_at_pos,
         n_snv, class, action; 76 rows, sorted by region, POS, action.
       - `git diff --stat $MAN` must show exactly these 2 files.
    7. **Live pins.** Extend tests/ta_r4/test_live_pins.py (r4_heavy), with a module constant `UKB_NATIVE_DIR`:
       - `test_ukb_native_one_variant_per_chrpos[region]`: read each panel's `variants` via `ukb337k_tiles.read_rds`
         and assert no duplicated (CHR, POS).
       - `test_ukb_native_resolution_audit_reconciles`: per region,
         - manifest n_var + n_var_dropped_multiallelic == the pre-drop count;
         - audit `dropped` rows == n_var_dropped_multiallelic;
         - audit `kept_snv` rows == n_sites_kept_snv;
         - every kept_snv row is an SNV present in the panel;
         - every dropped row is absent from it.
       - `test_ukb_native_pyhin1_160680184_keeps_rs184461353`: the panel has exactly one variant at 1:160680184, and
         it is rs184461353 A/G.

       RED first, with `UKB_NATIVE_DIR` monkeypatched to `$W/old/EUR_ukb337k_r4`:
       - NC-L1: the one-per-chrpos test fails in the 15 changed regions and passes in the other 15;
       - the PYHIN1 test fails.

       Then GREEN on the live panels. NC-L2: delete one kept_snv row from a tmp copy of the audit; the reconcile
       test fails. The existing `test_catalog_derived_panels_match_manifest[EUR_ukb337k_r4]` must be seen RED before
       the re-pin and GREEN after.
    8. **M2 re-run** (sbatch, `-t 00:30:00`). Run measure_m123.R unchanged, writing `$W/m123_fits.tsv`. Confirm the
       83/83 reproduction validation lines first. Then:
       - A3_ukb: m2_chrpos_extra == 0 in 145/145 fits ("new" catalog rows), including MC4R_18q21, PYHIN1_1q23 and
         NC_NULL_06 asthma.EUR;
       - every non-A3_ukb row matches `data/r4/tmp/w3f/dupkey/m123_fits.tsv` (compare sorted lines). A difference →
         STOP.

       Report the A3_ukb M3 deltas vs 15.5a as information.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test -x "${RSCRIPT:?RSCRIPT unset}" && sbatch --wait --export=ALL -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 01:30:00 --mem=32G -o data/r4/tmp/w3f/ukbbi/verify_t2_%j.out --wrap "cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test -x \"\$RSCRIPT\" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_live_pins.py tests/ta_r4/test_ukb_native_multiallelic.py tests/ta_r4/test_ukb_tile_loader.py tests/ta_r4/test_ukb_tile_triangle.py tests/ta_r4/test_lock_gate.py tests/ta_r4/test_in_job_gate.py -q -rs" && tail -5 data/r4/tmp/w3f/ukbbi/verify_t2_*.out && sha256sum --quiet -c data/r4/tmp/w3f/ukbbi/pre_untouched.sha256 && diff <(git diff --name-only "$(cat data/r4/tmp/w3f/ukbbi/t2_start_sha)" HEAD -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ | sort) <(printf '%s\n' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb_native_multiallelic_resolved.tsv | sort)</automated>
  </verify>
  <done>
    - Backup verified; restore.sh exercised.
    - The manifest recipe reproduced the committed bytes.
    - The recount from the real old panels matches the table component by component.
    - The fire reached 30 of 30, and the follow-up dry-run said "Nothing to be done".
    - (a)–(d) passed with exact R equality for all 30 regions.
    - The manifest and resolution audit are committed with test_live_pins.py (explicit paths). Live-pin RED → GREEN;
      NC-L1 and NC-L2 were observed.
    - M2 A3_ukb = 0/145; the non-A3_ukb rows match 15.5a.
  </done>
</task>

<task type="auto">
  <name>Task 3: Re-measure A3_ukb eligibility, update the eligibility manifest and DRAFT, close (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, tests/ta_r4/test_amendment_text.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-ukb-panels-biallelic-SUMMARY.md</files>
  <read_first>
    - src/python/ta_r4/measure_fit_eligibility.py and 15.5's SUMMARY (the exact run-list, sbatch array and summarise invocation)
    - the committed w3f_fit_eligibility.tsv (columns, row order)
    - DRAFT Pre-Paste rows "Panel n_var > 16,000", "Measured post-restriction counts", the M2 OPEN row, the (k) count
      clause, and the PASTE-block (c) LD-panel sentence; tests/ta_r4/test_amendment_text.py
  </read_first>
  <action>
    1. **Run list.** `measure_fit_eligibility.run_list` restricted to arm A3_ukb, on the re-pinned manifest.
       - Expected: 15 = 5 traits × {BMI_5q13_3 25,156; PYHIN1_1q23 27,268; SLC2A9_urate 17,980}, each still > 16,000.
       - Print the list. Any other count → STOP.
       - Run the 15.5 no-fit measurement (cap 0, outputs only under `$W/elig/`) as one sbatch array
         (`--constraint=cascadelake -t 01:00:00 --mem=32G`). Wait by output listing (15 JSONs).
       - Run summarise(); it must raise if any RDS was fitted.
    2. **Eligibility rows.** Rewrite only the A3_ukb rows of w3f_fit_eligibility.tsv:
       - the 15 measured rows from summarise();
       - every A3_ukb bound row with its new panel n_var.

       Keep the column order and row order.
       - Control: with the A3_ukb rows removed, the file is byte-identical before and after (filter on the arm column, `cmp`).
       - Reconcile in the LOG: A3_ukb rows = measured 15 + bound; eligible count old → new; asthma × PYHIN1_1q23 A3_ukb
         post-restriction n_variants old → new (expect a decrease of at most 8).
    3. **DRAFT edits.** These are outside the PASTE block unless stated. The §B.11 public-text rules and the
       internal-content scan apply inside it.
       - Pre-Paste "Panel n_var > 16,000" row, UKB native values: HLA_6p21 35,673; PYHIN1_1q23 27,268; BMI_5q13_3
         25,156; SLC2A9_urate 17,980. Re-read them from the manifest; these are planning values. Cite the rebuild commit.
       - "Measured post-restriction counts" row and the (k) count clause: change only the A3_ukb counts from step 2.
       - Replace the M2 OPEN row with a RESOLVED row:
         - Carter 2026-11-18, a1 + no `--snps-only` (DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1);
         - 38 multi-variant positions in 15 panels: 31 keep their single SNV, 7 without a single SNV are removed
           (45 variants removed);
         - M2 0/145 (Slurm id);
         - `$MAN/ukb_native_multiallelic_resolved.tsv`.

         It no longer gates W4a-T3. Keep the DEC reference.
       - PASTE block, the (c) LD-panel sentence: add the disclosure, with re-derived numbers. Where a UK Biobank native
         panel holds more than one variant at a position, the single SNV is kept and the others are removed, following
         the 1000 Genomes builds at SNV/indel positions (31 positions). The 7 positions with more than one variant and
         no single SNV are removed entirely (14 variants). Unlike the 1000 Genomes panels, which contain SNVs only, UK
         Biobank panels retain insertions/deletions at single-variant positions (17,071).
       - (m) frozen-paths / commit list: add this plan's commits and `src/python/ta_r4/ukb_native_multiallelic.py`.
       - confirmatory_sha256 must be unchanged (decision_rules.yaml is untouched): recompute it with the Pre-Paste
         command and compare.
       - test_amendment_text must pass. If a test pins the old UKB numbers, observe it RED, then update only those
         expectations, citing the DEC.
    4. **Wave close** per §C, **without push**.
       - QUICK + PINS + HEAVY in sbatch.
       - FULL in sbatch, compared per id to `data/r4/tmp/w3f/dupkey/full_15_5a.xml`. Expected: the added ids are the
         new tests, 0 removed, 0 outcome changes. The 2 pre-existing tests/m3 failures in deferred-items.md stay; do
         not fix them.
       - Restore any test side-effect file (e.g. tests/m3/sparse_parent_benchmark.tsv) to HEAD.
    5. **Records.**
       - LOG entry "2026-11-18 W3f 15.5b" with every count, Slurm id and reconciliation.
       - STATE.md RESUME block: 15.5b done; next 15.6.
       - SUMMARY.
       - Commit with explicit paths. Nothing pushed.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py tests/ta_r4/test_measure_fit_eligibility.py -q -rs && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import csv; r=[x for x in csv.DictReader(open('.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv'),delimiter='\t') if x['arm']=='A3_ukb']; print(len(r), sum(x['method']=='measured' for x in r), sum(x['eligible']=='false' for x in r))" && ! grep -n "OPEN (blocks the lock; Carter decision; W3f 15.5a M2)" .planning/amendments/osf-amendment-r4-DRAFT.md && git status --porcelain -- src tests .planning/amendments .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests</automated>
  </verify>
  <done>
    - The 15 A3_ukb fits were measured in no-fit mode. Only the A3_ukb rows of the eligibility manifest changed
      (control cmp).
    - The DRAFT carries the new UKB numbers, the resolved M2 row, the a1 disclosure and the commit shas.
      confirmatory_sha256 is unchanged.
    - FULL was compared per id.
    - LOG, STATE and SUMMARY are committed. Nothing pushed.
  </done>
</task>

</tasks>

<enforcers>
| must_have | enforcer (fails when broken) | negative control (observed failing) |
|---|---|---|
| SNV+indel keeps the SNV | T-a | NC-2 (a2 drop-all), NC-1 (no-op) |
| indel+indel drops both | T-b | NC-1 |
| SNV+SNV drops both (no tie-break) | T-c | NC-3 (prefer-first-SNV), NC-1 |
| lone indel kept (no --snps-only) | T-d | NC-4 (snps-only) |
| SNV means single-base ACGT | T-a2 | NC-5 (length-only SNV test) |
| real PYHIN1 1:160680184 keeps rs184461353 | T-f (tiles) + test_live_pins PYHIN1 test (panel) | NC-2; live test against the backup panel |
| resolution is after the catalog filter | T-g (tile-only multi position) | NC-7 |
| native rule uses the new builder; isect rule untouched | T-h | NC-6 |
| live panels ≤ 1 variant per CHR:POS | test_live_pins::test_ukb_native_one_variant_per_chrpos | NC-L1 (backup: 15 fail) |
| audit == resolution | test_live_pins::test_ukb_native_resolution_audit_reconciles | NC-L2 (kept_snv row deleted) |
| panels == manifest | test_live_pins::test_catalog_derived_panels_match_manifest[EUR_ukb337k_r4] | RED observed before the re-pin |
| non-UKB-native bytes unchanged | `sha256sum -c pre_untouched.sha256` + dry-run 0 jobs + empty code/params listings | `--forcerun r4_panel_ukb_isect` lists 29 |
| rebuild is a pure deletion | identity.py exact `np.array_equal` per region | — (identity check) |
| M2 = 0 on A3_ukb | measure_m123.R m2_chrpos_extra over 145 fits | 15.5a's run on the same script = 3 |
| other eligibility rows unchanged | `cmp` of the non-A3_ukb lines | — |
</enforcers>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| builder → pinned panels | the rebuild rewrites pinned production inputs |
| DRAFT → OSF | public text (not posted here) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f5b-01 | Tampering | non-UKB panels / catalogs | mitigate | ukb337k_tiles.py not edited; dry-run 0 jobs + empty code/params listings for every non-native target; pre_untouched.sha256 re-check |
| T-r4-W3f5b-02 | Tampering | EUR_ukb337k_r4 panels | mitigate | verified backup + restore.sh (cancels only this fire's recorded job ids); real-panel recount of the live panels (== backup) as step 3, before the fire; exact R-submatrix identity; re-pin only after reconciliation |
| T-r4-W3f5b-03 | Repudiation | decision record | mitigate | three replies byte-verified (sha256; od -c for the one-liners) and inserted with cat; committed before code |
| T-r4-W3f5b-04 | Information disclosure | DRAFT PASTE block | mitigate | §B.11 internal-content scan; test_amendment_text |
| T-r4-W3f5b-05 | Elevation of privilege | measurement | mitigate | 15.5 module: cap 0, tmp-only outputs, summarise() raises on a fitted RDS; no production fire |
</threat_model>

<verification>
- test_ukb_native_multiallelic, test_live_pins, test_amendment_text and test_measure_fit_eligibility are green; QUICK/PINS/HEAVY/FULL per §C.
- `git diff <start>..HEAD --name-only` ⊆ files_modified. ukb337k_tiles.py, run_coloc_pair_r4.R, catalogs_sha256.tsv and every other panels_*.tsv are unchanged.
- No push: `git log origin/m3-W2-aou-deltas..HEAD` lists this plan's commits locally only.
</verification>

<success_criteria>
- All 30 UKB native panels hold ≤ 1 variant per CHR:POS.
- The single SNV is kept at 31 positions and 7 no-SNV positions are dropped (45 variants, audited). Indels at
  single-variant positions are kept.
- M2 = 0/145 A3_ukb fits; the 15.5a M2 gate row is resolved.
- A3_ukb eligibility is re-measured (15 fits). The DRAFT numbers and disclosure match the manifests.
- Non-UKB inputs are byte-identical.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-ukb-panels-biallelic-SUMMARY.md`
</output>
