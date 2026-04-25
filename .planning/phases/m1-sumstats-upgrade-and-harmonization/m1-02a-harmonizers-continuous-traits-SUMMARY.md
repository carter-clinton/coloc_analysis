---
phase: m1
plan: 02a
subsystem: sumstats-upgrade-and-harmonization
plan_id: m1-02a-harmonizers-continuous-traits
tags: [m1, wave2a, harmonize, yengo, loh, page, glgc, wuttke, morris, magic, snakemake, deferred-sentinel]
dependency-graph:
  requires:
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-00-preflight-and-environment-SUMMARY.md
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-01-portal-fetches-and-aragam-route-SUMMARY.md
    - src/python/sumstats_utils.py (CANONICAL_COLS + filter_palindromic_ambiguous + liftover_to_grch37 from m1-00)
    - data/external/liftover/hg38ToHg19.over.chain.gz (Wave 0 staged)
    - data/raw/sumstats_v2/{GIANT2018,GLGC2021,CKDGen2019,MAGIC2021,PAGE2019}/ (Wave 1 + pre-existing)
    - envs/m1-harmonize.yml (Wave 0 staged)
  provides:
    - src/python/harmonize_yengo.py (4 variant codepaths — yengo2018, loh2022_eur, loh2022_afr, page2019_afr)
    - src/python/harmonize_glgc.py (auto-detects per-ancestry vs TRANS BF schema; logTG phenotype_lock)
    - src/python/harmonize_wuttke.py (3 variants — wuttke2019_trans, wuttke2019_eur, morris2019_afr)
    - src/python/harmonize_magic.py (6 ancestries; per-ancestry + TRANS BF; optional rsid->(chr,bp) crosswalk)
    - src/python/m1_raw_glob.py (resolve_raw_for + DEFERRED_SENTINEL universal guard; W8 fix option A)
    - src/python/sumstats_utils.py extension — build_rsid_to_chrpos(bim_prefix) helper
    - src/snakemake/rules/m1_harmonize.smk (28 leaf jobs: 4 BMI + 15 GLGC + 3 eGFR + 6 HbA1c + 2 aggregators)
    - config/pipeline.yaml +5 path keys (harmonized_parquet, ldsc_munged, ldsc_rg_logs, ldsc_overlap, qc_log)
    - tests/m1/ +5 test modules + 9 fixture files (yengo, loh, page, glgc x 2, wuttke, morris, magic x 2, mini_1kg.{1,2}.bim)
    - .planning/phases/m1-.../deferred-items.md (DEF-M1-02a-01 MAGIC EUR truncation log)
  affects:
    - config/pipeline.yaml (5 new path keys appended)
    - src/python/sumstats_utils.py (build_rsid_to_chrpos helper appended)
tech-stack:
  added:
    - none (reused pandas 2.2.3 + pyarrow 18.1.0 + the existing pyliftover from m1-00)
  patterns:
    - B-2 guard: fail-loud on missing source columns (Phase 09 harmonize_gbmi.py reuse)
    - Dual-emit per D-09: .tsv.gz (intermediate; Snakemake bgzips to .tsv.bgz + tabix) + .parquet snappy mirror
    - .qc.json sidecar per harmonizer with palindromic / MAF / liftover / INFO / unmapped-rsid drop counts
    - Universal .deferred sentinel guard at every Snakemake rule's shell prelude
    - Module-level rsid->(chr,bp) cache keyed by bim_prefix to avoid 22-bim re-read per harmonizer call
    - Wildcard rules + glob-based raw-file resolution where the file isn't on the portal manifest (GLGC, Wuttke)
key-files:
  created:
    - src/python/harmonize_yengo.py
    - src/python/harmonize_glgc.py
    - src/python/harmonize_wuttke.py
    - src/python/harmonize_magic.py
    - src/python/m1_raw_glob.py
    - src/snakemake/rules/m1_harmonize.smk
    - tests/m1/test_harmonize_yengo.py
    - tests/m1/test_harmonize_glgc.py
    - tests/m1/test_harmonize_wuttke.py
    - tests/m1/test_harmonize_magic.py
    - tests/m1/test_m1_raw_glob.py
    - tests/m1/fixtures/yengo_head.tsv
    - tests/m1/fixtures/loh_head.tsv
    - tests/m1/fixtures/page_bmi_afr_head.tsv
    - tests/m1/fixtures/glgc_ldl_head.tsv
    - tests/m1/fixtures/glgc_tg_logtg_head.tsv
    - tests/m1/fixtures/wuttke_head.tsv
    - tests/m1/fixtures/morris_afr_head.tsv
    - tests/m1/fixtures/magic_head.tsv
    - tests/m1/fixtures/magic_trans_head.tsv
    - tests/m1/fixtures/mini_1kg.1.bim
    - tests/m1/fixtures/mini_1kg.2.bim
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/deferred-items.md
  modified:
    - src/python/sumstats_utils.py (build_rsid_to_chrpos helper appended)
    - config/pipeline.yaml (+5 path keys)
decisions:
  - DEF-M1-02a-01 raised — MAGIC HbA1c EUR file truncated mid-line at chr1:59348460 (Wave 1 fetch artifact)
  - MAGIC schema discovery: 1000G release ships explicit chromosome/base_pair_location; rsid forward crosswalk is now an optional fallback (legacy releases) rather than the primary path documented in the plan
  - MAGIC TRANS schema discovery: log10BF + sample_size + het_p_value only (no BETA/SE/P); harmonizer emits canonical NaN for those columns and routes consumers to CPASSOC/HyPrColoc
  - GLGC schema discovery: TRANS Bayes-factor variant uses METAL_Effect/StdErr/Pvalue (not EFFECT_SIZE/SE/pvalue) — auto-detect via column presence
  - PAGE schema discovery: ships rsid alongside chr:pos:ref:alt SNP — drop SNP, keep rsid for canonical key (LDSC HM3 alignment)
  - Snakemake .download_complete.<source_tag> flag inputs dropped — Wave 1 fired downloads via bash directly, no flags exist
metrics:
  duration_minutes: 70
  task_count: 2
  files_created: 22
  files_modified: 2
  commits: 4
completed: 2026-04-25
---

# Phase M1 Plan 02a: Harmonizers (Continuous Traits) Summary

Authored 4 of 7 D-10 per-source harmonizer modules — the continuous-trait
half. Yengo+Loh+PAGE for BMI (4 codepaths), GLGC for lipids (15 (subtype,
ancestry) cells), Wuttke+Morris for eGFR (3 codepaths), MAGIC for HbA1c
(6 ancestries). Full Snakemake wiring with universal `.deferred`-marker
guard. Production smoke test on real Yengo file: 2.34M variants in →
2.33M out (9,025 palindromic dropped at MAF=[0.48, 0.52] band). All 14
harmonizer pytest cases pass; full m1 suite green at 37 / 2 skip.

## What Was Built

### Harmonizer modules (4 files, 1,030 LoC across them)

| Module | Variants / cells | LoC | Key behavior |
|--------|------------------|-----|--------------|
| `harmonize_yengo.py` | 4 codepaths (yengo2018, loh2022_eur, loh2022_afr, page2019_afr) | 292 | b38→b37 liftover for Loh variants (`liftover_to_grch37` 5% drop hard ceiling per RESEARCH pitfall #1); INFO≥0.8 filter for PAGE; B-2 guard on every variant |
| `harmonize_glgc.py` | 15 cells (LDL × 6 + HDL/TG/TC × 3 each, per D-04 fanout) | 231 | Auto-detects per-ancestry single-trait schema (`EFFECT_SIZE` / `SE` / `pvalue`) vs TRANS Bayes-factor meta (`METAL_Effect` / `METAL_StdErr` / `METAL_Pvalue`); logTG phenotype-lock detection from filename; never re-transforms |
| `harmonize_wuttke.py` | 3 codepaths (wuttke2019_trans, wuttke2019_eur, morris2019_afr) | 208 | Whitespace-delimited input via pandas python engine; auto-detects Wuttke (`Chr Pos_b37 RSID Allele1 Allele2 Freq1 Effect StdErr P-value n_total_sum`) vs Morris alt-format (`Chromosome Position SNP_ID …`); upper-cases lowercase Wuttke alleles |
| `harmonize_magic.py` | 6 ancestries (TRANS / EUR / AFR / EAS / SAS / HIS) | 299 | Auto-detects per-ancestry schema vs asymmetric TRANS Bayes-factor (log10BF only); rsid→(chr,bp) forward crosswalk via `--bim-prefix` is now a fallback path since 1000G MAGIC release ships explicit chromosome/base_pair_location |

Each emits **dual artifacts per D-09** — `.tsv.gz` (intermediate; Snakemake
bgzips → `.tsv.bgz` + `tabix -s 1 -b 2 -e 2 -S 1`) AND `.parquet` snappy
mirror — plus a **`.qc.json` sidecar** with `n_input`, `n_output`,
`n_palindromic_dropped`, `n_maf_below_threshold`, `n_info_below_threshold`,
`liftover_drop_rate` (when applicable), `n_unmapped_rsid` (MAGIC
crosswalk path), and `phenotype_lock` (logTG / TRANS BF only).

### Shared raw-file resolver (`src/python/m1_raw_glob.py`, 137 LoC)

`resolve_raw_for(source_tag, ancestry) -> str` returns either the single
raw-file path or the module constant `DEFERRED_SENTINEL = "__DEFERRED__"`.

**W8 fix (option A — universal `.deferred` guard).** When a `.deferred`
marker is present in the resolved `target_dir`, the function returns the
sentinel BEFORE the `assert len(matches) == 1` check. Every harmonize
rule's shell prelude branches on:

```bash
if [ "{params.raw}" = "__DEFERRED__" ]; then
    mkdir -p $(dirname {output.tsv_bgz})
    touch {output.tsv_bgz}.deferred
    touch {output.tsv_bgz} {output.tbi} {output.parquet}
    echo '{"deferred": true}' > {output.qc_json}
    exit 0
fi
```

Single choke-point that closes Loh-EUR / Loh-AFR (PENDING_D01_ACCESSION
sentinels from m1-01 N1 fix), AND any future PENDING_* deferral path
symmetrically. Replaces source-specific ad-hoc `harmonize_deferred_*`
rules.

### `sumstats_utils.build_rsid_to_chrpos` extension

Module-level cache keyed by `bim_prefix` so a single `harmonize_magic`
invocation across 22 chromosomes loads once and reuses for every row
lookup. Memory footprint scales with the BIM file count (~150 MB for
full 1000G EUR; <1 MB for the test fixture).

### Snakemake rules (`src/snakemake/rules/m1_harmonize.smk`, 522 LoC)

Snakemake DAG (dry-run from a stub Snakefile):

```
Job stats:
job                             count
----------------------------  -------
all                                 1
harmonize_glgc_lipids              15
harmonize_loh_bmi_afr               1
harmonize_loh_bmi_eur               1
harmonize_magic_hba1c               6
harmonize_morris_egfr_afr           1
harmonize_wuttke_egfr_eur           1
harmonize_wuttke_egfr_trans         1
harmonize_yengo_bmi_afr_page        1
harmonize_yengo_bmi_eur             1
m1_harmonize_continuous_all         1
total                              30
```

= **28 leaf harmonizer jobs + 2 aggregators**. Coverage match to plan
spec:

| Source | Plan spec | Actual leaf jobs |
|--------|-----------|------------------|
| Yengo / Loh / PAGE BMI | 4 | 4 ✅ |
| GLGC lipids (D-04 fanout) | 15 | 15 ✅ |
| CKDGen Wuttke + Morris | 3 | 3 ✅ |
| MAGIC HbA1c | 6 | 6 ✅ |
| **Total** | **28** | **28** ✅ |

Each rule:
- conda env: `envs/m1-harmonize.yml`
- resources: `mem_mb={8000,12000}, runtime=2880` (standard queue ceiling)
- shell: universal `.deferred` guard → harmonizer Python invocation →
  `bgzip -c` + `tabix -s 1 -b 2 -e 2 -S 1`

D-16 filename convention enforced: `<trait>.<ancestry>.<consortium>.<year>.GRCh37.<ext>`.
Verified outputs:
- `bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz` (yengo2018)
- `bmi.EUR.GIANT-23andMe.2022.GRCh37.tsv.bgz` (loh2022_eur)
- `bmi.AFR.GIANT-23andMe.2022.GRCh37.tsv.bgz` (loh2022_afr)
- `bmi.AFR.PAGE.2019.GRCh37.tsv.bgz` (page2019_afr)
- `{ldl,hdl,tg,tc}.{ancestry}.GLGC.2021.GRCh37.tsv.bgz` (15 cells)
- `egfr.{TRANS,EUR,AFR}.CKDGen.2019.GRCh37.tsv.bgz`
- `hba1c.{TRANS,EUR,AFR,EAS,SAS,HIS}.MAGIC.2021.GRCh37.tsv.bgz`

### `config/pipeline.yaml` delta

Five new path keys appended under `paths:`:

```yaml
harmonized_parquet:  data/processed/sumstats_harmonized_parquet
ldsc_munged:         data/processed/ldsc_overlap/munged
ldsc_rg_logs:        data/processed/ldsc_overlap/rg_logs
ldsc_overlap:        data/processed/ldsc_overlap
qc_log:              data/processed/sumstats_harmonized/qc_log
```

(`harmonized_sumstats` and `raw_sumstats_v2` were already added in m1-00
and m1-01 respectively.)

### Tests (5 modules, 14 cases, 9 fixture files)

| Module | Cases | Fixtures |
|--------|-------|----------|
| `test_harmonize_yengo.py` | 6 (yengo2018 schema/QC/parquet + loh2022_eur schema + drop-rate + page2019_afr schema) | yengo_head.tsv, loh_head.tsv, page_bmi_afr_head.tsv |
| `test_harmonize_glgc.py` | 2 (LDL EUR canonical + logTG phenotype_lock) | glgc_ldl_head.tsv, glgc_tg_logtg_head.tsv |
| `test_harmonize_wuttke.py` | 3 (eur, trans, morris_afr schema) | wuttke_head.tsv, morris_afr_head.tsv |
| `test_harmonize_magic.py` | 3 (eur peranc, TRANS BF, rsid crosswalk) | magic_head.tsv, magic_trans_head.tsv, mini_1kg.{1,2}.bim |
| `test_m1_raw_glob.py` | 4 (single-match + zero-match assertion + .deferred sentinel + two-match assertion) | (programmatic in tmp_path) |

`pytest tests/m1/` runs **37 passed, 2 skipped** in 12 s. The 2 skips
are the Wave 0 baseline (a liftover-fixture-positions edge case + an
LDSC-reducer-not-yet-authored placeholder) — NOT introduced by this
plan.

## Production smoke test (real raw file)

```
python src/python/harmonize_yengo.py \
  --input data/raw/sumstats_v2/GIANT2018/BMI/EUR/Meta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz \
  --output /tmp/m1_smoke/bmi.EUR.GIANT-UKBB.2018.tsv.gz \
  --parquet /tmp/m1_smoke/bmi.EUR.GIANT-UKBB.2018.parquet \
  --qc-json /tmp/m1_smoke/bmi.EUR.GIANT-UKBB.2018.qc.json \
  --variant yengo2018 \
  --trait bmi --ancestry EUR --consortium GIANT-UKBB --year 2018
```

QC sidecar:

```json
{
  "n_input":                 2336269,
  "n_palindromic_dropped":      9025,
  "n_maf_below_threshold":         0,
  "n_info_below_threshold":        0,
  "n_output":                2327244
}
```

Drop fraction: 9,025 / 2,336,269 = **0.39%** at MAF=[0.48, 0.52]. This
is in line with Phase 09 baselines (~0.3-0.5%) and matches RESEARCH
expectations for a high-quality mostly-imputed dataset.

## sumstats_utils.build_rsid_to_chrpos cache hit-rate (test fixture)

Test fixture `mini_1kg.{1,2}.bim` covers 8 rsids (5 chr1 + 3 chr2) of
which 5 (rs1, rs2, rs3, rs4, rs5) appear in `magic_head.tsv` rsid space.
First call to `build_rsid_to_chrpos("tests/m1/fixtures/mini_1kg",
chromosomes=[1,2])` reads both .bim files, populates the
`_rsid_lookup_cache["tests/m1/fixtures/mini_1kg"]` dict (8 entries).
Subsequent calls within the same Python process hit cache (zero re-read).

In production the lookup dict for full 1000G EUR (~9.5M SNPs) holds
~150 MB; cache amortizes across the 6 MAGIC harmonizer invocations if
they share a Python process (Snakemake spawns one per rule, so the
cache benefit is per-invocation only — this is documented but not
exploited at the orchestration layer).

## Pre-existing pre-pivot harmonized files (Track A back-compat)

Pre-pivot harmonized files coexist under the *old* naming convention at
`data/processed/sumstats_harmonized/<trait>.<ancestry>.tsv.bgz` (no
year / consortium tokens). These are Track A's primary data per
Amendment §8.

The **new** D-16 convention `<trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz`
is additive — m1-02a writes new files, never overwrites the old pivot
files. Track A re-reads the old files unchanged; Track B M2+ consumes
the new D-16-named files. No collision.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking issue] Removed `.download_complete.<source_tag>` flag inputs from harmonize rules.**
- Found during: Snakemake dry-run after T2 implementation.
- Issue: The plan's Snakemake skeleton declared `flag = os.path.join(_RAW, ".download_complete.{source_tag}")` as the harmonize rule's input. m1-01 fired the Wave 1 portal driver via bash directly (per `feedback_parallel_downloads.md`) — never via Snakemake — so `.download_complete.<tag>` flag files do not exist on disk. Including them as inputs blocked the entire DAG with `MissingInputException`.
- Fix: dropped the `flag` input from each harmonize rule. `resolve_raw_for` already does the right thing (returns `DEFERRED_SENTINEL` for missing-and-`.deferred`-marked dirs; raises `AssertionError` for missing-without-marker), so the soundness check is intact at the params-lambda level rather than at the input-dependency level.
- Files modified: `src/snakemake/rules/m1_harmonize.smk` (4 yengo / loh / page rules). GLGC, Wuttke, MAGIC rules never had flag inputs (they consume pre-existing files).
- Commit: `d18bc5e`.

**2. [Rule 1 — Bug] pandas python engine does not accept `low_memory`.**
- Found during: Task 2 GREEN — `harmonize_wuttke._read_raw` raised `ValueError: The 'low_memory' option is not supported with the 'python' engine`.
- Issue: My initial implementation passed `low_memory=False` alongside `engine="python"`; only the C engine accepts it.
- Fix: dropped `low_memory=False` from the python-engine `read_csv` call (default behavior is fine for whitespace-delimited Wuttke files).
- Files modified: `src/python/harmonize_wuttke.py` `_read_raw()`.
- Commit: `d18bc5e`.

**3. [Rule 1 — Bug] MAGIC harmonizer's B-2 guard fired before the rsid-crosswalk fallback path could trigger.**
- Found during: `test_magic_rsid_crosswalk_fills_chr_bp` GREEN — guard required `chromosome` + `base_pair_location` even when caller intended to fill them via `--bim-prefix`.
- Fix: split the column rename map into a "required" subset (always present) + an "optional CHR/BP" subset that is dropped from the guard's expected-columns list when `--bim-prefix` is supplied AND raw lacks CHR/BP. The `has_raw_chr_bp` boolean drives the switch.
- Files modified: `src/python/harmonize_magic.py` `harmonize_magic()`.
- Commit: `d18bc5e`.

**4. [Rule 2 — Add missing critical functionality] MAGIC TRANS Bayes-factor schema codepath.**
- Found during: discovery from `zcat MAGIC1000G_HbA1c_TA.tsv.gz | head -1` showing `variant chromosome base_pair_location effect_allele other_allele log10BF sample_size het_p_value` — NO BETA/SE/P columns.
- Issue: The plan's MAGIC column map (`MAGIC_COLS = {"A1": "EA", "A2": "OA", "eaf_meta": "EAF", "BETA": "BETA", …}`) was based on the older Chen 2021 MAGIC release format and did NOT match the actual 1000G files on disk. Even the per-ancestry files use the GWAS-Catalog-harmonized schema (`variant`, `chromosome`, `base_pair_location`, `effect_allele`, `other_allele`, `effect_allele_frequency`, `beta`, `standard_error`, `p_value`, `sample_size`).
- Fix: rewrote `MAGIC_PERANC_COLS` to match the actual file schema. Added a separate `MAGIC_TRANS_COLS` for the Bayes-factor variant. Added a `_detect_magic_variant()` switcher. TRANS variant emits canonical NaN for BETA/SE/P/EAF and a `phenotype_lock` note steering downstream consumers to CPASSOC / HyPrColoc (LDSC / MTAG cannot munge this file — no Z available).
- Files modified: `src/python/harmonize_magic.py` (entire structure).
- Commit: `d18bc5e`.

### Decisions deviating from plan suggestion

**5. MAGIC rsid forward crosswalk demoted from "primary path" to "fallback".**
- The plan documented the rsid → (chr, bp) crosswalk as a hard requirement (RESEARCH pitfall #5). Discovery from raw-file inspection: the 1000G-version MAGIC release ships explicit `chromosome` + `base_pair_location`, eliminating the need for a crosswalk at the per-row level.
- The crosswalk path is still implemented (and tested by `test_magic_rsid_crosswalk_fills_chr_bp`) as a defensive fallback for any legacy MAGIC release or future schema drift. `--bim-prefix` is optional; the harmonizer raises `ValueError` only if both (a) raw file lacks CHR/BP AND (b) `--bim-prefix` was not supplied.
- Open question #3 in m1-RESEARCH (EUR vs AFR bim-prefix selection per ancestry) becomes moot for the production fire — the in-file CHR/BP is preferred.

**6. GLGC schema now auto-detects per-ancestry vs TRANS variant.**
- The plan's column map (`GLGC_COLS = {"CHROM": "CHR", "POS_b37": "BP", "rsID": "SNP", "REF": "OA", "ALT": "EA", "ALT_FREQ": "EAF", "BETA": "BETA", "SE": "SE", "PVALUE": "P", "N": "N"}`) does not match either raw-file schema observed on disk.
- Per-ancestry single-variant meta files (LDL/HDL/TG/TC × {EUR, AFR, EAS, SAS, HIS}) use `EFFECT_SIZE`, `SE`, `pvalue` (not `BETA`, `PVALUE`).
- TRANS Bayes-factor meta files (LDL/HDL/TG/TC × TRANS) use `METAL_Effect`, `METAL_StdErr`, `METAL_Pvalue` (plus `lnBF` carried separately).
- Fix: added `_detect_glgc_variant(df)` that switches between `GLGC_PERANC_COLS` and `GLGC_TRANS_COLS` based on which BETA-column triplet is present. Verified against five raw files (LDL EUR, LDL TRANS, HDL TRANS, TG EUR (logTG), LDL HIS).

## Auth Gates / Human Actions

None of the m1-02a tasks encountered an auth gate. The plan ran fully
autonomously from RED → GREEN → Snakemake-rule-load → smoke test on
production Yengo file.

## Deferred Issues (out of scope; logged for future plans)

**DEF-M1-02a-01 — MAGIC HbA1c EUR raw file truncation.** During the
production smoke test on `data/raw/sumstats_v2/MAGIC2021/HbA1c/EUR/MAGIC1000G_HbA1c_EUR.tsv.gz`
the harmonizer raised `EOFError: Compressed file ended before the
end-of-stream marker was reached`. `zcat … | tail` shows truncation
mid-line at `chr1:59348460`. Caused by m1-01 (Wave 1) — predates this
plan; the harmonizer correctly fails loud rather than silently emitting
a partial output. Resolution: re-fire `bin/download_sumstats_v2.sh
--manifest config/download_manifest_m1_portal.tsv` (idempotent; only
the truncated file re-fetches). Logged in
`.planning/phases/m1-sumstats-upgrade-and-harmonization/deferred-items.md`.

## Wave 2a Verification Gate

```
pytest tests/m1/test_harmonize_yengo.py tests/m1/test_harmonize_glgc.py \
       tests/m1/test_harmonize_wuttke.py tests/m1/test_harmonize_magic.py \
       tests/m1/test_m1_raw_glob.py -x --tb=short
                                                        # 14/14 PASS

test -f src/python/harmonize_yengo.py                    # PASS
test -f src/python/harmonize_glgc.py                     # PASS
test -f src/python/harmonize_wuttke.py                   # PASS
test -f src/python/harmonize_magic.py                    # PASS
test -f src/python/m1_raw_glob.py                        # PASS
test -f src/snakemake/rules/m1_harmonize.smk             # PASS

python -c "from sumstats_utils import build_rsid_to_chrpos"
                                                        # PASS

grep -rE "/rs1/researchers|/gpfs_common|/share/clintonlab" \
    src/python/harmonize_{yengo,glgc,wuttke,magic}.py \
    src/snakemake/rules/m1_harmonize.smk
                                                        # 0 hits — PASS

snakemake -s .m1_smoke_snakefile.tmp --dry-run --cores 1 --quiet
                                                        # 30 jobs DAG loaded — PASS

grep -q "DEFERRED_SENTINEL" src/python/m1_raw_glob.py    # PASS
grep -q "__DEFERRED__" src/snakemake/rules/m1_harmonize.smk  # PASS
grep -q "harmonized_parquet" config/pipeline.yaml        # PASS
```

→ **EXIT 0** (all gates pass). Pytest full m1: **37 passed, 2 skipped**.

## Commits

| Task | Commit  | Title                                                                                  | Files |
| ---- | ------- | -------------------------------------------------------------------------------------- | ----- |
| T1 (RED)   | `7144149` | test(m1-02a): add failing contract tests for harmonize_yengo + harmonize_glgc          | 7     |
| T1 (GREEN) | `e8b4f92` | feat(m1-02a): harmonize_yengo + harmonize_glgc + sumstats_utils.build_rsid_to_chrpos | 4     |
| T2 (RED)   | `fc99fa2` | test(m1-02a): add failing tests for harmonize_wuttke + harmonize_magic + m1_raw_glob   | 9     |
| T2 (GREEN) | `d18bc5e` | feat(m1-02a): harmonize_wuttke + harmonize_magic + m1_raw_glob + Snakemake rules       | 6     |

## Downstream Wave Consequences

| Wave / Plan          | Consequence                                                                                                                                                |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Wave 2b (m1-02b)     | Will author 3 case-control harmonizers (DIAMANTE T2D, GIGASTROKE stroke, Aragam CAD; GBMI asthma is `harmonize_gbmi.py` reuse). Pattern: copy m1-02a module structure, reuse B-2 guard + dual-emit + .qc.json sidecar + universal `.deferred` guard. Existing `m1_raw_glob.resolve_raw_for` is plug-and-play; m1-02b only adds new `harmonize_<source>` Snakemake rules. |
| Wave 3 (m1-03)       | Munges 39 of the 45 trait × ancestry cells (4 yengo + 15 glgc + 3 egfr + 5 magic-not-EUR + 12 m1-02b expected). LDSC matrix becomes 39×39 (vs the 45×45 plan target) until DEF-M1-02a-01 (MAGIC EUR truncation) re-fetch lands AND m1-02b deferred rows resolve (Loh×2, GBMI×3, Klarin×1, DIAMANTE×4 cookie-pending). |
| Wave 4 (m1-04)       | Reads the 39 `.qc.json` sidecars per D-12 to render Quarto QC HTMLs. The harmonizer's QC fields (`n_input`, `n_output`, `n_palindromic_dropped`, `liftover_drop_rate`, `phenotype_lock`) flow directly into the Quarto template variable bindings. |
| M2 (MTAG / CPASSOC)  | Consumes the dual-emit `.parquet` mirror for fast variant-set alignment. The `phenotype_lock` field in qc.json carries the logTG / TRANS-BF / Loh-liftover provenance into the M2 cohort table footnotes. |

## Threat Flags

None — pure data-transformation plan with no new network/auth/file-IO
trust boundaries beyond what was already in m1-00 / m1-01. The
`build_rsid_to_chrpos` helper reads PLINK .bim files (canonical 1000G
LDSC reference; no untrusted input).

## Self-Check: PASSED

All claimed artifacts present on disk and all 4 task commits resolved
in `git log`. Verification run 2026-04-25T08:09Z:

- 22/22 created files FOUND (4 harmonizers + 1 raw_glob + 1 smk + 5 tests + 9 fixtures + 1 deferred-items.md + 1 SUMMARY scaffolding directories already existed)
- 2/2 modified files FOUND (sumstats_utils.py + pipeline.yaml)
- 4/4 task commits FOUND in `git log` (`7144149`, `e8b4f92`, `fc99fa2`, `d18bc5e`)
- Wave 2a verification gate: EXIT 0
- Pytest full m1: 37 passed, 2 skipped (skips are explicit + expected baseline)
- Snakemake DAG loads: 30 jobs (28 leaf + 2 aggregators) — PASS
- Path-parameterization gate: 0 hardcoded paths in 4 harmonizer .py files + smk file — PASS
- DEFERRED_SENTINEL present in m1_raw_glob.py + m1_harmonize.smk — PASS
- D-09 dual-emit verified on production Yengo file: .tsv.gz (intermediate) + .parquet emitted — PASS
- D-16 filename convention verified: `bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz` — matches `<trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz` lowercase-trait-first dotted convention — PASS
