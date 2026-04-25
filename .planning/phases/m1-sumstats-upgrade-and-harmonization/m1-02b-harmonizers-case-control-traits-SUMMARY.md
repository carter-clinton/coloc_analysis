---
phase: m1
plan: 02b
subsystem: sumstats-upgrade-and-harmonization
plan_id: m1-02b-harmonizers-case-control-traits
tags: [m1, wave2b, harmonize, diamante, gigastroke, aragam, gbmi, evangelou, liftover, sha256-manifest, tabix-sort]
dependency-graph:
  requires:
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-00-preflight-and-environment-SUMMARY.md
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-01-portal-fetches-and-aragam-route-SUMMARY.md
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-02a-harmonizers-continuous-traits-SUMMARY.md
    - data/raw/sumstats_v2/GIGASTROKE2022/stroke/{TRANS,EUR,AFR,EAS}/ (Wave 1 fetched)
    - data/raw/sumstats_v2/Aragam2022/CAD/CAD_GWAS_{primary_discovery_meta,BBJ_meta}.tsv (Wave 1 unpacked)
    - data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt (Wave 0 D-03 audit)
    - data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz (pre-pivot T1-spine input)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (D-02-locked GCST accessions; phenotype rows)
    - data/external/liftover/hg38ToHg19.over.chain.gz (Wave 0 staged)
    - src/python/sumstats_utils.py (CANONICAL_COLS + filter_palindromic_ambiguous + liftover_to_grch37 + validate_canonical_frame)
    - src/python/m1_raw_glob.py (resolve_raw_for + DEFERRED_SENTINEL)
    - src/python/freeze_sha256_manifest.py (D-13 deterministic writer)
  provides:
    - src/python/harmonize_diamante.py (T2D × {TRANS,EUR,EAS,SAS}; rejects AFR/HIS)
    - src/python/harmonize_gigastroke.py (all-stroke × {TRANS,EUR,AFR,EAS}; D-02 integer-lock guard)
    - src/python/harmonize_aragam.py (CAD × {TRANS,EUR,EAS} + Klarin 2018 fallback codepath)
    - src/python/verify_evangelou_sbp.py (D-16 rename of pre-pivot SBP-EUR T1-spine file)
    - src/python/harmonize_gbmi.py extension (--liftover-chain b38->b37 with Pitfall #7 guard)
    - src/snakemake/rules/m1_harmonize.smk extension (16 new rules — see DAG matrix)
    - tests/m1/ +5 modules + 5 fixtures (24 contract tests, 100% pass)
    - 6 GIGASTROKE/Aragam harmonized .tsv.bgz + .tbi + .parquet quadruples on disk
    - sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.{tsv.bgz,tbi,parquet,qc.json} D-16 outputs on disk
    - data/processed/sumstats_harmonized/sha256_manifest.tsv (42 rows, deterministic)
    - .planning/amendments/sha256_manifest_harmonized_m1.tsv (OSF-paste mirror per D-13)
  affects:
    - data/processed/sumstats_harmonized/ (7 new D-16-named harmonized files + sha256_manifest.tsv)
    - data/processed/sumstats_harmonized_parquet/ (7 new parquets)
    - data/processed/sumstats_harmonized/qc_log/ (7 new qc.json sidecars)
    - .planning/phases/m1-.../deferred-items.md (DEF-M1-02b-01 Aragam EUR sex-stratified)
tech-stack:
  added:
    - none (reused pandas 2.2.3 + pyarrow 18.1.0 + r_coloc bgzip/tabix from Phase 5)
  patterns:
    - Defensive D-02 integer-lock guard at module load (placeholder substring check)
    - D-03 branch routing via aragam_zip_manifest.txt content scan (a vs b)
    - Source-specific harmonize_deferred_* rules (DUA gating + branch routing) coexist with universal .deferred-marker guard
    - Pitfall #7 liftover chain guard (basename must contain hg38ToHg19)
    - Tabix-required CHR/BP sort post-palindromic-filter (numeric, drops non-autosomal)
    - Synthesize SNP=chr:bp:OA:EA when raw lacks variant_id (GIGASTROKE 2022 schema)
    - Per-ancestry total N pulled from SUMSTATS-UPGRADE.tsv when raw lacks per-row n column
key-files:
  created:
    - src/python/harmonize_diamante.py (242 LoC)
    - src/python/harmonize_gigastroke.py (267 LoC)
    - src/python/harmonize_aragam.py (348 LoC)
    - src/python/verify_evangelou_sbp.py (208 LoC)
    - tests/m1/test_harmonize_diamante.py (7 cases)
    - tests/m1/test_harmonize_gigastroke.py (4 cases)
    - tests/m1/test_harmonize_aragam.py (6 cases)
    - tests/m1/test_harmonize_gbmi_liftover.py (4 cases)
    - tests/m1/test_verify_evangelou_sbp.py (3 cases)
    - tests/m1/fixtures/diamante_head.tsv
    - tests/m1/fixtures/gigastroke_head.tsv
    - tests/m1/fixtures/aragam_head.tsv
    - tests/m1/fixtures/klarin2018_mvp_afr_head.tsv
    - tests/m1/fixtures/gbmi_b38_head.tsv (+ .tsv.gz)
    - tests/m1/fixtures/evangelou_b37_head.tsv
    - .planning/amendments/sha256_manifest_harmonized_m1.tsv
  modified:
    - src/python/harmonize_gbmi.py (+--liftover-chain flag; +29 lines net)
    - src/snakemake/rules/m1_harmonize.smk (+~280 lines: 16 new rules + 5 helpers)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/deferred-items.md (DEF-M1-02b-01)
  staged-on-disk-not-committed:
    - 6 newly-built GIGASTROKE/Aragam harmonized .tsv.bgz + .tbi + .parquet (gitignored under data/)
    - sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.{tsv.bgz,tbi,parquet,qc.json} (gitignored)
    - data/processed/sumstats_harmonized/sha256_manifest.tsv (gitignored; OSF-paste copy is committed)
    - 4 .deferred markers backfilled at data/raw/sumstats_v2/DIAMANTE2022/T2D/{TRANS,EUR,EAS,SAS}/ (cookie-pending; Rule 3)
decisions:
  - DEF-M1-02b-01 raised — Aragam ZIP CAD_GWAS_SEX_STRATIFIED.txt.gz is per-sex stratified, not pooled-EUR; schema mismatch -> EUR cell DEFERRED; M2 work item to author harmonize_aragam_sex_strat
  - GIGASTROKE 2022 raw schema discovery: only 11 columns; no variant_id and no n columns; harmonizer synthesizes SNP=chr:bp:OA:EA + per-ancestry total N from SUMSTATS-UPGRADE.tsv
  - Sort step required for tabix: harmonized output sorted by numeric CHR + BP before bgzip; non-autosomal rows dropped silently (LDSC ignores them anyway)
  - DIAMANTE .deferred markers backfilled (Rule 3) — Wave 1 m1-01 driver returned 0 on AWAITING_COOKIE without writing markers; backfilled so universal-guard pattern works in Snakemake DAG
metrics:
  duration_minutes: 80
  task_count: 2
  files_created: 16
  files_modified: 3
  commits: 6
completed: 2026-04-25
---

# Phase M1 Plan 02b: Harmonizers (Case-Control Traits) Summary

Wave 2b closeout: authored 3 case-control harmonizer modules (DIAMANTE
T2D, GIGASTROKE all-stroke, Aragam CAD with Klarin 2018 fallback);
extended the existing Phase 09 `harmonize_gbmi.py` with an opt-in
b38→b37 liftover branch (RESEARCH Pitfall #4 + #7 chain-direction
guard); authored `verify_evangelou_sbp.py` to schema-verify and
D-16-rename the pre-pivot SBP-EUR T1-spine file; froze a deterministic
secondary SHA-256 manifest of the 42 harmonized artifacts for D-13
reproducibility. Combined with m1-02a (continuous-trait harmonizers),
this completes the Wave 2 "harmonize-as-ready" surface for M1.

Production-fire numerics on real raw inputs: 6 of 6 attempted ancestries
landed harmonized .tsv.bgz + .tbi + .parquet + .qc.json quadruples
(GIGASTROKE × 4 + Aragam × 2). Total wall time 7m56s for the 6-way
parallel `xargs -P 6` re-fire (post-sort-fix round 2). All 24 plan-level
contract tests pass; full M1 pytest tree stays green at 61/2 skip.

## What Was Built

### 3 case-control harmonizer modules (857 LoC across them)

| Module | Cells | LoC | Key behavior |
|--------|-------|-----|--------------|
| `harmonize_diamante.py` | T2D × {TRANS,EUR,EAS,SAS}; AFR+HIS rejected | 242 | N column prefers `N_effective`; falls back to `4 / (1/N_case + 1/N_control)`; AFR + HIS strata raise `SystemExit` with TSV-row-8 + row-11 dua_pending citation |
| `harmonize_gigastroke.py` | all-stroke × {TRANS,EUR,AFR,EAS} | 267 | Defensive D-02 integer-lock guard at module load via `_reload_filenames()`; testable via `monkeypatch._TSV`. Real GIGASTROKE files lack `variant_id` and `n` columns — synthesizes `SNP=chr:bp:OA:EA` + pulls per-ancestry total N from `SUMSTATS-UPGRADE.tsv` rows 14–17. |
| `harmonize_aragam.py` | CAD × {TRANS,EUR,EAS} + Klarin fallback | 348 | `_branch_for_afr()` reads `aragam_zip_manifest.txt`; returns 'a' iff any AFR/AA/African substring present, else 'b'. `harmonize_aragam(ancestry='AFR')` raises `NotImplementedError` on branch (b). Sibling `harmonize_aragam_klarin2018()` handles MVP-AFR-CAD when the Klarin file lands (CHROM/POS/ID/REF/ALT/AF/BETA/SE/P + `N=N_case+N_ctrl` if both present, else fallback `N=8500`). |

Each emits the canonical D-09 quadruple (`.tsv.gz` intermediate
[Snakemake bgzips → `.tsv.bgz` + tabix-indexes], `.parquet` snappy
mirror, `.qc.json` sidecar with `n_input`, `n_palindromic_dropped`,
`n_maf_below_threshold`, `n_output`, `phenotype_lock`,
`n_source` provenance, `snp_source` provenance).

### `harmonize_gbmi.py` — Phase 09 module extended (Pitfall #4 + #7)

Added a single `--liftover-chain` CLI argument + matching keyword
parameter on `harmonize_gbmi_sumstats()`. When the flag is set:
1. Pitfall #7 guard fires — `chain_path.name` MUST contain
   `"hg38ToHg19"` or `ValueError` is raised. Prevents silent
   wrong-direction lift.
2. Calls `sumstats_utils.liftover_to_grch37(df, chain_file, ...)`
   between the column rename + the palindromic filter; dropped
   rows are tracked in the returned `qc` dict
   (`n_liftover_input`, `n_liftover_lifted`, `n_liftover_dropped`,
   `liftover_drop_rate` — same shape as Yengo Loh-variant codepath).

When the flag is **not** set, behavior is byte-identical to the
Phase 09 v1 (no liftover; existing 4/4 pytest cases still pass —
verified post-edit).

Line-116 comment updated:
> "GBMI flagship releases 2020-2021 are GRCh37; M1 2022 release is
> GRCh38 and requires --liftover-chain per DEC-2026-04-24-01.
> See Pitfall #4."

Also fixed pandas `compression='gzip'` → `'infer'` on input read so
non-gzipped fixture inputs work (Rule 1).

### `verify_evangelou_sbp.py` — D-16 rename of pre-pivot SBP-EUR

208 LoC. Reads pre-pivot `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz`
(13-col schema: `CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT
ANCESTRY BUILD`), renames to canonical 10-col schema
(`POS→BP, ALT→EA, REF→OA, SNP_ID→SNP`; drops trailing
`TRAIT/ANCESTRY/BUILD`), validates via
`sumstats_utils.validate_canonical_frame`, then enforces b37
chromosome-length invariants:

```python
CHR_MAX_B37 = {1: 249250621, 2: 243199373, ..., 22: 51304566}
TOL_BP = 1000  # forgive ~1kb rounding at chromosome ends
```

Any `BP > CHR_MAX_B37[chr] + TOL_BP` triggers `AssertionError`
("File may be b38 — aborting rename") and **no** target file is
written. EAF ∈ [0,1] and P ∈ [0,1] checked similarly.

On pass: copies the source bgzipped TSV byte-for-byte to D-16 name
(`sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz`), copies the
`.tbi` sibling, builds the canonical-10-col `.parquet` snappy mirror,
writes `.qc.json` with `phenotype_lock="SBP continuous (mmHg),
medication-adjusted"` + `d16_name` + `build_verified="GRCh37"` +
`schema_valid=true`.

Live-fire on real Evangelou pre-pivot file (Task 2 step B): **7,160,657
rows verified b37**; D-16 outputs landed (4 files: `.tsv.bgz`, `.tbi`,
`.parquet` 145.7MB, `.qc.json`).

### Snakemake rules added to `m1_harmonize.smk`

Total Wave 2 a + b leaf jobs: **49** (28 Wave 2a + 16 Wave 2b new + 1
Evangelou verify + 1 sha256-freeze + 2 aggregators + 1 m1_harmonize_all):

```
Wave 2b new rules:
- harmonize_diamante_t2d (4 ancestries via wildcard: TRANS|EUR|EAS|SAS)
- harmonize_deferred_diamante_afr  (TSV row 8 dua_pending)
- harmonize_deferred_diamante_his  (TSV row 11 dua_pending)
- harmonize_diamante_all           (aggregator)
- harmonize_gigastroke_stroke (4 ancestries via wildcard)
- harmonize_gigastroke_all         (aggregator)
- harmonize_aragam_cad     (3 ancestries: TRANS|EUR|EAS — but EUR resolves to DEFERRED per DEF-M1-02b-01)
- harmonize_deferred_aragam_cad_afr (D-03 branch (b) — Klarin pending)
- harmonize_aragam_all             (aggregator)
- harmonize_gbmi_asthma            (3 ancestries: MULTI|EUR|AFR; mandatory --liftover-chain CHAIN_B38_TO_B37)
- harmonize_gbmi_asthma_all        (aggregator)
- verify_evangelou_sbp             (D-16 rename gate)
- m1_freeze_harmonized_sha256_manifest (D-13 reproducibility freeze + mirror)
- m1_harmonize_all                 (top-level aggregator)
```

Each harmonize rule prepends the universal `_DEFERRED_GUARD` shell
prelude (W8 fix option A from m1-02a) so any `.deferred` marker
upstream routes the rule to a no-op `.deferred` output marker.
Source-specific `harmonize_deferred_*` rules (DIAMANTE AFR + HIS,
CAD-AFR Klarin) are RETAINED per the design contract — they encode
DUA gating + branch routing that is independent of the universal
sentinel-marker path.

DAG dry-run: 49 jobs total (matches plan target). Verified via
`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake -s
.m1_smoke_02b_snakefile.tmp --dry-run --cores 1`.

### Tests (5 modules, 24 cases, 5 fixtures)

| Module | Cases | Fixtures | Status |
|--------|-------|----------|--------|
| `test_harmonize_diamante.py` | 7 (4 ancestry parametrize + 2 deferred AFR/HIS rejection + 1 N_effective preference) | diamante_head.tsv | ✅ all PASS |
| `test_harmonize_gigastroke.py` | 4 (TRANS schema + invalid ancestry + module-load filenames + monkeypatch placeholder guard via _reload_filenames) | gigastroke_head.tsv | ✅ all PASS |
| `test_harmonize_aragam.py` | 6 (branch (a)/(b)/missing-manifest + TRANS schema + AFR-branch-b NotImplementedError + Klarin fallback) | aragam_head.tsv, klarin2018_mvp_afr_head.tsv | ✅ all PASS |
| `test_harmonize_gbmi_liftover.py` | 4 (no-liftover Phase 09 regression + argparse presence + wrong-direction guard + smoke with staged chain) | gbmi_b38_head.tsv.gz | ✅ all PASS |
| `test_verify_evangelou_sbp.py` | 3 (b37 fixture pass + chr1:260M b38 fail + EAF>1 fail) | evangelou_b37_head.tsv | ✅ all PASS |

`pytest tests/m1/test_harmonize_*.py tests/m1/test_verify_evangelou_sbp.py`:
**24 passed in 2.47s**. Full m1 suite runs at **61 passed, 2 skipped**
(skips are baseline; no regression from m1-02a's 37/2).

Phase 09 GBMI regression suite (`tests/phase9/test_harmonize_gbmi.py`)
remains green at **4/4 PASS** — confirms `--liftover-chain` flag
addition is backward-compatible.

## Production fire — 6 ancestries landed

```
[05:45:57] START stroke.{TRANS,EUR,AFR,EAS}.GIGASTROKE  (4 jobs)
[05:45:57] START cad.{TRANS,EAS}.Aragam                  (2 jobs)
[05:53:53] DONE all 6 ancestries — 7m56s wall (xargs -P 6)
```

Per-ancestry harmonized counts (raw → canonical-10-col output):

| Source       | Ancestry | n_input    | n_palindromic | n_maf<0.005 | n_output   | Wall (mm:ss) |
|--------------|----------|------------|---------------|-------------|------------|--------------|
| GIGASTROKE   | TRANS    |  7,588,358 |        34,007 |           0 |  7,554,351 | ~4:09        |
| GIGASTROKE   | EUR      |  7,511,476 |        28,367 |           0 |  7,483,109 | ~4:04        |
| GIGASTROKE   | AFR      | 10,831,840 |        29,759 |           0 | 10,802,081 | ~5:54        |
| GIGASTROKE   | EAS      |  6,789,909 |        29,650 |           0 |  6,760,259 | ~3:40        |
| Aragam       | TRANS    | 20,073,070 |        32,221 |   7,462,575 | 12,578,274 | ~7:17        |
| Aragam       | EAS      | 20,804,423 |        35,013 |   7,291,557 | 13,477,853 | ~7:56        |
| Evangelou    | EUR      |  7,160,657 |  (preserved) |           0 |  7,160,657 |  ~0:30 (rename only) |

All 6 outputs have all 22 autosomes indexed by tabix (`tabix -l` returns
1..22 for each).

## D-09/D-13/D-16 coverage matrix

| Trait        | TRANS | EUR | AFR | EAS | SAS | HIS | Provenance |
|--------------|-------|-----|-----|-----|-----|-----|------------|
| **t2d**      | LANDED-WAITING_COOKIE† | LANDED-WAITING_COOKIE† | DEFERRED (DUA) | LANDED-WAITING_COOKIE† | LANDED-WAITING_COOKIE† | DEFERRED (DUA) | DIAMANTE 2022 |
| **stroke**   | LANDED ✓ | LANDED ✓ | LANDED ✓ | LANDED ✓ | (not in inventory) | (not in inventory) | GIGASTROKE 2022 |
| **cad**      | LANDED ✓ | DEFERRED (DEF-M1-02b-01 sex-strat) | DEFERRED (D-03 branch (b) Klarin pending) | LANDED ✓ | (not in inventory) | (not in inventory) | Aragam 2022 (TRANS+EAS); Klarin 2018 fallback (AFR) |
| **asthma**   | DEFERRED (PORTAL_GBMI) | DEFERRED (PORTAL_GBMI) | DEFERRED (PORTAL_GBMI) | (not in inventory) | (not in inventory) | (not in inventory) | GBMI 2022 (b38; --liftover-chain ready) |
| **sbp**      | (not in inventory) | LANDED ✓ (D-16 rename) | (D-06 fallback to AoU) | (not in inventory) | (not in inventory) | (not in inventory) | Evangelou 2018 (pre-pivot T1-spine) |

† DIAMANTE 4 released ancestries are AWAITING_COOKIE — Snakemake rule
definitions are AUTHORED + tested via fixture; production fire is
gated by the `.deferred` marker the universal guard catches at fire
time. When Carter captures the DIAMANTE_COOKIE env and re-fires
`bin/download_sumstats_v2.sh --manifest config/download_manifest_m1_portal.tsv`,
the markers are removed and the harmonize rules become un-blocked.

Plan-level **N = current freeze 47 minus DEFERRED**:
- LANDED on disk: 5 (Wave 2b) + Evangelou-D-16 + 28 Wave 2a (m1-02a) = **34 cells harmonized**
- DEFERRED for Wave 3 munge gate: DIAMANTE×4 (cookie) + GBMI×3 (portal) + Loh×2 (D-01) + DIAMANTE-AFR/HIS×2 (DUA) + CAD-AFR×1 (Klarin pending) + CAD-EUR×1 (sex-strat) + AFR-SBP×1 (D-06 AoU fallback) = **14 cells deferred**
- Wave 3 LDSC matrix at M1 closeout: **34×34** (with reduced cells until cookie/portal/AoU resolve).

## Secondary harmonized SHA-256 manifest (D-13)

Frozen via `freeze_sha256_manifest.py --root data/processed/sumstats_harmonized
--out data/processed/sumstats_harmonized/sha256_manifest.tsv --no-mtime
--skip-glob "*.deferred,sha256_manifest.tsv,.all_harmonize_complete,.m1_harmonize_continuous_all.complete"`.

- **Row count:** 42 (header + 42 data rows).
- **Mirror:** `.planning/amendments/sha256_manifest_harmonized_m1.tsv` (43 lines including header — committed for OSF paste reproducibility per D-13).
- **Meta-hash (sha256-of-the-manifest-file):** `ad01c5b4d26918de08d6465a0c8c1ba5749681e992a3a0c904ff3ba6f024b8f6`
- **Determinism gate:** two consecutive `--no-mtime` runs produce
  byte-identical TSV (`diff data/.../sha256_manifest.tsv
  /tmp/rerun_manifest.tsv` → empty). Re-running M1 on identical raw
  inputs MUST yield identical harmonized outputs; this manifest is
  the reference for that check.

The manifest covers:
- 6 newly-landed Wave 2b case-control outputs (GIGASTROKE × 4 + Aragam × 2)
  — each as 3 sibling rows (.tsv.bgz, .tbi, .parquet).
- 1 newly-built Evangelou D-16 rename (4 sibling rows).
- pre-existing pre-pivot harmonized files (Track A inputs per Amendment §8) —
  asthma.{EUR,AFR,AFR_grch38_backup}, hypertension.EUR, stroke.{EUR,AFR,AFR.tsv.gz},
  t2d.{EUR,AFR}, bmi.EUR (legacy filenames before D-16; preserved per Amendment §8).
- 7 qc_log/*.qc.json sidecars from this Wave.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking issue] DIAMANTE `.deferred` markers backfilled.**
- **Found during:** Snakemake DAG dry-run after Task 1 GREEN. The
  `harmonize_diamante_t2d` rule's `params.raw = lambda wc:
  resolve_raw_for(...)` raised `AssertionError: expected exactly 1
  raw file for DIAMANTE2022_T2D_SAS/SAS, found 0` for all 4
  ancestries — DIAMANTE dirs were empty.
- **Issue:** m1-01 (Wave 1) `bin/download_sumstats_v2.sh` driver
  emits `MANUAL ACTION REQUIRED ... return 0` for the AWAITING_COOKIE
  cookie-pending case but does NOT write a `.deferred` marker (the
  marker is only written for `PENDING_*` URL sentinels). Without the
  marker, `m1_raw_glob.resolve_raw_for` cannot route to the universal
  guard → DAG fails to load.
- **Fix:** Backfilled `data/raw/sumstats_v2/DIAMANTE2022/T2D/{TRANS,EUR,EAS,SAS}/.deferred`
  markers with Carter-resume protocol (visit DIAGRAM portal, capture
  cookies, `export DIAMANTE_COOKIE=...`, re-fire driver). Markers
  contain pre-formatted resume-action steps.
- **Files modified:** 4 `.deferred` markers under
  `data/raw/sumstats_v2/DIAMANTE2022/T2D/*/` (gitignored under data/).
- **Commit:** `91e2c89` (Task 1 GREEN, alongside the harmonizer).

**2. [Rule 1 — Bug] Tabix requires CHR/BP-sorted input.**
- **Found during:** Production fire (round 1) after first set of
  harmonized .tsv.bgz files were produced. `tabix -s 1 -b 2 -e 2 -S 1
  -f` errored:
  ```
  [E::hts_idx_push] Chromosome blocks not continuous
  tbx_index_build3 failed: ...stroke.TRANS.GIGASTROKE.2022.GRCh37.tsv.bgz
  ```
- **Issue:** GIGASTROKE raw .tsv.gz files are NOT chromosome-sorted
  (the file head shows chr5 first; chromosomes interleaved). Without
  an explicit sort, tabix cannot build a contiguous-block index.
  Aragam files are RVTESTS-sorted naturally but we want a defensive
  sort across ALL sources.
- **Fix:** Added a CHR/BP sort step in each of the 3 case-control
  harmonizers, just before `_emit_dual_artifacts`:
  ```python
  df["_chr_sort"] = pd.to_numeric(df["CHR"], errors="coerce")
  df = df.dropna(subset=["_chr_sort"]).sort_values(
      ["_chr_sort", "BP"]
  ).drop(columns=["_chr_sort"]).reset_index(drop=True)
  ```
  Drops rows whose CHR is non-numeric (X/Y/MT) since the LDSC
  panel ignores them anyway. Sort is stable + numeric (chr10 follows
  chr9, not chr1).
- **Files modified:** `src/python/harmonize_diamante.py`,
  `src/python/harmonize_gigastroke.py`, `src/python/harmonize_aragam.py`.
- **Commit:** `7892c09`. Round-2 production re-fire (post-fix) all
  6 jobs finished in 7m56s wall.

**3. [Rule 1 — Bug] pandas `compression='infer'` doesn't recognize `.bgz`.**
- **Found during:** Live-fire of `verify_evangelou_sbp.py` on
  `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz` —
  raised `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b
  in position 1` (pandas attempting to read the bgzip magic bytes
  as UTF-8).
- **Issue:** Pandas `compression='infer'` recognizes `.gz` but not
  `.bgz`. The bgzip files are gzip-compatible at the stream level
  (single concatenated gzip blocks), so pandas can read them with
  explicit `compression='gzip'`.
- **Fix:** Added a suffix check at the top of
  `verify_evangelou_sbp.verify_and_rename`:
  ```python
  src_name = str(source).lower()
  if src_name.endswith((".bgz", ".gz", ".bgzip", ".tsv.bgz", ".tsv.gz")):
      comp = "gzip"
  else:
      comp = "infer"
  df_raw = pd.read_csv(source, sep="\t", compression=comp, low_memory=False)
  ```
- **Files modified:** `src/python/verify_evangelou_sbp.py`.
- **Commit:** `9ab782d`.

**4. [Rule 2 — Add missing critical functionality] DEF-M1-02b-01: Aragam EUR sex-stratified.**
- **Found during:** Production-fire schema probe of
  `data/raw/sumstats_v2/Aragam2022/CAD/CAD_GWAS_SEX_STRATIFIED.txt.gz`
  (the file presumed to be the Aragam EUR pooled subset per
  SUMSTATS-UPGRADE.tsv row 22 expected_filename `Aragam2022_EUR_subset.tsv`).
- **Issue:** The file is per-sex stratified, NOT pooled-EUR. Schema
  is `rs_number reference_allele other_allele eaf beta se beta_95L
  beta_95U z p_value log10_p_value q_statistic q_p_value i2 n_studies
  n_samples effects male_eaf male_beta male_se ...
  female_eaf female_beta female_se ...`. The pooled-EUR subset is
  apparently NOT released as a separate file in the ZIP.
- **Fix (this plan):** Removed `"EUR": "CAD_GWAS_SEX_STRATIFIED.txt.gz"`
  from `ARAGAM_RAW_FILES` in `m1_harmonize.smk`. The
  `harmonize_aragam_cad` rule for `ancestry=EUR` now resolves to
  `DEFERRED_SENTINEL` via `_aragam_raw_glob` → universal guard fires
  → emits `.deferred` placeholder + `.qc.json` sentinel.
- **Fix (M2 work item):** Author `harmonize_aragam_sex_strat` to
  emit two outputs (`cad.EUR-male`, `cad.EUR-female`) + a pooled
  `cad.EUR` derived via inverse-variance meta of the two. Logged
  as DEF-M1-02b-01 in `deferred-items.md`.
- **Files modified:** `src/snakemake/rules/m1_harmonize.smk`
  (`ARAGAM_RAW_FILES` dict),
  `.planning/phases/m1-.../deferred-items.md` (new section).
- **Commit:** `9ab782d`.

### Decisions deviating from plan suggestion

**5. GIGASTROKE schema differs from plan-spec (Rule 2 — auto-fix).**
- The plan documented expected GIGASTROKE columns as
  `variant_id, chromosome, base_pair_location, effect_allele,
  other_allele, effect_allele_frequency, beta, standard_error,
  p_value, n, n_cases, n_controls`.
- Discovery from `zcat .../GCST90104539_buildGRCh37.tsv.gz | head -1`:
  actual schema is **only 11 columns** —
  `chromosome, base_pair_location, effect_allele_frequency, beta,
  standard_error, p_value, odds_ratio, ci_lower, ci_upper,
  effect_allele, other_allele`. NO `variant_id`. NO `n`.
- Fix: harmonizer synthesizes `SNP = chr:bp:OA:EA` (canonical
  chr:bp:ref:alt convention) and pulls per-ancestry total N from
  `SUMSTATS-UPGRADE.tsv` rows 14–17 (locked at m1-00 D-02).
  Optional fields are STILL honored if the input ships them
  (e.g., the test fixture provides `variant_id` and the harmonizer
  uses it, recording `snp_source="variant_id"` in qc.json).
- Implication: M1 harmonized stroke files have synthetic SNP IDs
  (chr1:752566:G:A style); LDSC munge / MTAG / coloc downstream
  must accept these. M1-03 LDSC munge on a smoke pair will verify.

**6. Aragam EUR cell DEFERRED for M1; M2 work item.**
- Documented as DEF-M1-02b-01 (deviation #4 above). Wave 3 LDSC
  matrix excludes `cad.EUR` until the M2 sex-aware harmonizer lands.
  Track B's CAD-EUR coverage comes from the TRANS file marginalization
  (acceptable since EUR is ~85% of TRANS per SUMSTATS-UPGRADE.tsv
  row 22 cohort_overlap_notes).

**7. Source-specific `harmonize_deferred_*` rules retained per design contract.**
- Plan W8 fix specified retaining source-specific ad-hoc DEFERRED
  rules (DIAMANTE AFR/HIS DUA-pending, CAD-AFR Klarin pending) even
  after the universal `.deferred`-marker guard pattern took over for
  PENDING_* sentinels. This plan retains:
  - `harmonize_deferred_diamante_afr` (TSV row 8 dua_pending)
  - `harmonize_deferred_diamante_his` (TSV row 11 dua_pending)
  - `harmonize_deferred_aragam_cad_afr` (D-03 branch (b) Klarin pending)
- These encode source-specific fallback logic (DUA gating, branch
  routing) independent of the sentinel-marker path; emit `.deferred`
  output markers with rich human-readable provenance.

## Auth Gates / Human Actions

Three carry-forward Carter-resume actions remain, all logged in
m1-01 SUMMARY but ledger-relevant for downstream un-blocking:

1. **DIAMANTE × 4 cookie capture (~5 min Carter active)** — visit
   `https://diagram-consortium.org/downloads.html`, accept ToS, copy
   cookies via DevTools → Application → Cookies, then on HPC:
   `export DIAMANTE_COOKIE="..." && bash bin/download_sumstats_v2.sh
   --manifest config/download_manifest_m1_portal.tsv` (idempotent).
   Once raw files land, the `.deferred` markers under
   `data/raw/sumstats_v2/DIAMANTE2022/T2D/*/` are removed and
   `harmonize_diamante_t2d` Snakemake rule fires for each ancestry.

2. **GBMI × 3 portal navigation (~10 min Carter active)** — visit
   `https://www.globalbiobankmeta.org/resources`, navigate to the
   asthma phenotype manifest (Google Sheets embedded), locate
   per-ancestry asthma direct URLs. Either update the manifest TSV
   with resolved URLs and re-fire, or drop files manually and remove
   the `.deferred` markers. Once raw files are in place, the
   `harmonize_gbmi_asthma` Snakemake rule fires with mandatory
   `--liftover-chain CHAIN_B38_TO_B37` (the rule plumbing is
   committed and tested).

3. **Klarin 2018 D-03 fallback URL** — Carter must locate the
   MVP-AFR-CAD AFR-stratified file (KP4CD database / author Zenodo
   deposit / CHARGE DUA path). Once located, replace the
   `harmonize_deferred_aragam_cad_afr` rule with a real
   `harmonize_aragam_cad_afr_klarin` rule that calls
   `harmonize_aragam_klarin2018()` (the function is authored and
   tested in `harmonize_aragam.py`).

These do NOT block M1 closeout; Wave 3 (m1-03 munge + LDSC rg)
proceeds on the 34 LANDED cells.

## Wave 2b Verification Gate

```bash
pytest tests/m1/test_harmonize_diamante.py \
       tests/m1/test_harmonize_gigastroke.py \
       tests/m1/test_harmonize_aragam.py \
       tests/m1/test_harmonize_gbmi_liftover.py \
       tests/m1/test_verify_evangelou_sbp.py -x --tb=short
                                                         # 24/24 PASS

test -f src/python/harmonize_diamante.py                  # PASS
test -f src/python/harmonize_gigastroke.py                # PASS
test -f src/python/harmonize_aragam.py                    # PASS
test -f src/python/verify_evangelou_sbp.py                # PASS
grep -q "liftover-chain" src/python/harmonize_gbmi.py     # PASS
grep -q "hg38ToHg19" src/python/harmonize_gbmi.py         # PASS
grep -q "verify_evangelou_sbp" src/snakemake/rules/m1_harmonize.smk
                                                         # PASS
grep -q "m1_freeze_harmonized_sha256_manifest" src/snakemake/rules/m1_harmonize.smk
                                                         # PASS
! grep -rE "/share/clintonlab|/rs1/researchers|/gpfs_common" \
    src/python/harmonize_{diamante,gigastroke,aragam}.py \
    src/python/verify_evangelou_sbp.py
                                                         # 0 hits — PASS

snakemake -s .m1_smoke_02b_snakefile.tmp --dry-run --cores 1 --quiet
                                                         # 49 jobs DAG loaded — PASS

# Production fire round-2 (post-sort-fix)
ls data/processed/sumstats_harmonized/{stroke,cad}.*.{GIGASTROKE,Aragam}.2022.GRCh37.tsv.bgz
                                                         # 6 files — PASS
for f in data/processed/sumstats_harmonized/{stroke,cad}.*.{GIGASTROKE,Aragam}.2022.GRCh37.tsv.bgz; do
  /rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/tabix -l "$f" | wc -l  # all 22
done                                                     # PASS

test -f data/processed/sumstats_harmonized/sha256_manifest.tsv
                                                         # PASS
test -f .planning/amendments/sha256_manifest_harmonized_m1.tsv
                                                         # PASS
diff /tmp/rerun_manifest.tsv data/processed/sumstats_harmonized/sha256_manifest.tsv
                                                         # empty — D-13 byte-identical PASS

pytest tests/phase9/test_harmonize_gbmi.py               # 4/4 PASS — Phase 09 regression
```

→ **EXIT 0** (all gates pass). Pytest full m1: **61 passed, 2 skipped**
(skips are explicit + expected baseline from m1-00). Phase 09
regression: 4 passed.

## Commits

| Task | Commit  | Title                                                                                  | Files |
| ---- | ------- | -------------------------------------------------------------------------------------- | ----- |
| T1 (RED)   | `57b4411` | test(m1-02b): add failing tests for case-control harmonizers (DIAMANTE/GIGASTROKE/Aragam) | 7     |
| T1 (GREEN) | `91e2c89` | feat(m1-02b): add 3 case-control harmonizers + Snakemake rules                            | 4     |
| T2 (RED)   | `1afa9f9` | test(m1-02b): add failing tests for GBMI liftover branch + Evangelou SBP verify           | 5     |
| T2 (GREEN) | `9ab782d` | feat(m1-02b): GBMI b38->b37 liftover branch + verify_evangelou_sbp + sha256 manifest rules | 4     |
| T2 (FIX)   | `7892c09` | fix(m1-02b): sort harmonized output by CHR/BP for tabix indexing                          | 3     |
| T2 (data)  | `229930a` | data(m1-02b): freeze secondary harmonized SHA-256 manifest (D-13 reproducibility artifact) | 1     |

## Downstream Wave Consequences

| Wave / Plan          | Consequence                                                                                                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Wave 3 (m1-03)       | Munges 34 of 47 inventory cells (28 m1-02a + 5 GIGASTROKE/Aragam + 1 Evangelou-D-16). LDSC star-topology --rg matrix becomes 34×34 until cookie/portal/AoU resolutions land. Smoke pair test in m1-03-T1 should validate that synthesized chr:bp:OA:EA SNP IDs from GIGASTROKE flow cleanly through `munge_sumstats.py`. |
| Wave 4 (m1-04)       | Reads the 34 `.qc.json` sidecars (11 from Wave 2b including Evangelou) per D-12 to render Quarto QC HTMLs. Sidecar keys consumed: `n_input`, `n_output`, `n_palindromic_dropped`, `n_maf_below_threshold`, `phenotype_lock`, `snp_source` (new — provenance for synthesized vs raw SNP IDs), `n_source` (new — N-column provenance for case-control), `liftover_drop_rate` (when applicable; e.g. GBMI asthma post-resolve). |
| M2 (MTAG/CPASSOC)    | Consumes the dual-emit `.parquet` mirrors for fast variant-set alignment. CAD-EUR carry-forward via TRANS marginalization until the M2 sex-aware Aragam harmonizer (DEF-M1-02b-01) lands. T2D-AFR/HIS deferred until DIAGRAM resolves DUA. |
| M2/M3 (post-cookie)  | When DIAMANTE_COOKIE is captured, the 4 `.deferred` markers under `data/raw/sumstats_v2/DIAMANTE2022/T2D/*/` are removed by the m1-01 driver re-fire; `harmonize_diamante_t2d` rule fires for each ancestry; LDSC matrix expands toward 38×38. |
| Track A (manuscript) | Pre-pivot pre-D-16 harmonized files (`hypertension.EUR.tsv.bgz`, `stroke.{EUR,AFR}.tsv.bgz`, `t2d.{EUR,AFR}.tsv.bgz`, `bmi.EUR.tsv.bgz`, `asthma.{EUR,AFR}.tsv.bgz`) are PRESERVED unchanged per Amendment §8 — re-read by Track A figure builders without modification. The new D-16-named files are ADDITIVE and consumed only by Track B M2+. |

## Threat Flags

None — pure data-transformation plan with no new network/auth/file-IO
trust boundaries. The Pitfall #7 chain-direction guard is a
data-correctness control (prevents silent wrong-direction lift), not
a security control. The DIAMANTE_COOKIE cookie env handling is the
same idiom from m1-01 (driver-level), unchanged this plan.

## Self-Check: PASSED

All claimed artifacts present on disk and all 6 task commits resolved
in `git log`. Verification run 2026-04-25T05:55Z:

- 16/16 created files FOUND (4 modules + 5 tests + 6 fixtures + 1 manifest mirror)
- 3/3 modified files FOUND (harmonize_gbmi.py, m1_harmonize.smk, deferred-items.md)
- 6/6 task commits FOUND in `git log` (`57b4411`, `91e2c89`, `1afa9f9`, `9ab782d`, `7892c09`, `229930a`)
- Wave 2b verification gate: EXIT 0
- Pytest full m1: 61 passed, 2 skipped (no regression from m1-02a's 37/2)
- Phase 09 GBMI regression: 4/4 PASS
- Snakemake DAG loads: 49 jobs (28 Wave 2a + 16 Wave 2b + 5 misc) — PASS
- Path-parameterization gate: 0 hardcoded paths in 4 new harmonizer .py files — PASS
- D-09 dual-emit verified on 6 production GIGASTROKE/Aragam files — PASS
- D-13 byte-identical re-run determinism: `diff` empty across two `--no-mtime` invocations — PASS
- D-16 filename convention verified for all 7 newly-built files (sbp + 4 stroke + 2 cad) — PASS
- Tabix index integrity: all 6 newly-built `.tsv.bgz` files report 22 chromosomes via `tabix -l` — PASS
