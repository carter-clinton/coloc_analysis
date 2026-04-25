# SUMSTATS Manual-Fetch Status Tracker

Live tracker for the portal-navigation and DUA-gated sources enumerated in
[SUMSTATS-MANUAL-FETCH.md](./SUMSTATS-MANUAL-FETCH.md). Carter updates the
checkboxes as each source lands. The scripted-URL queue (27 files, 40.4 GB)
is complete — see [SUMSTATS-SCRIPTED-FETCH-COMPLETE.md](./SUMSTATS-SCRIPTED-FETCH-COMPLETE.md).

Track B M1 closes when every row below resolves (fetched | DUA-approved |
explicitly deferred with rationale).

**Last refreshed:** 2026-04-24 (see Refresh log below)

## Portal-navigation queue (no DUA)

| # | Source | Trait × Ancestry | Destination | ETA | Status | Fetched on | Notes |
|---|---|---|---|---|---|---|---|
| 1 | GIANT Yengo 2018 | BMI × EUR | `data/raw/sumstats_v2/GIANT2018/BMI/EUR/` | 15s | ⬜ | — | single file; right-click save-as. 2026-04-24 scan: destination directory absent; 0/1 files present. |
| 2 | Loh 2022 | BMI × {EUR, AFR} | `data/raw/sumstats_v2/Loh2022/BMI/{EUR,AFR}/` | ~5 min | ⬜ | — | Loh-vs-Yengo primary-source decision pending Carter. 2026-04-24 scan: EUR + AFR destination dirs absent; 0/2 ancestries landed. |
| 3 | PAGE Wojcik 2019 | BMI × AFR | `data/raw/sumstats_v2/PAGE2019/BMI/AFR/` | ~5 min | ⬜ | — | verify dbGaP-DUA requirement before fetch. 2026-04-24 scan: destination directory absent; 0/1 files present. |
| 4 | DIAMANTE 2022 | T2D × {TRANS, EUR, EAS, SAS} | `data/raw/sumstats_v2/DIAMANTE2022/T2D/{…}/` | ~5 min | ⬜ | — | AFR + HIS NOT YET RELEASED — quarterly recheck. 2026-04-24 scan: TRANS/EUR/EAS/SAS destination dirs all absent; 0/4 ancestries landed. |
| 5 | GIGASTROKE 2022 | stroke × {TRANS, EUR, AFR, EAS, SAS} | `data/raw/sumstats_v2/GIGASTROKE2022/stroke/{…}/` | ~15 min | ⬜ | — | JS-rendered portal, 5 per-ancestry accessions. 2026-04-24 scan: TRANS/EUR/AFR/EAS/SAS destination dirs all absent; 0/5 ancestries landed. |
| 6 | GBMI 2022 | asthma × {MULTI, EUR, AFR} | `data/raw/sumstats_v2/GBMI2022/asthma/{…}/` | ~10 min | ⬜ | — | phenotype manifest via Google Sheets. 2026-04-24 scan: MULTI/EUR/AFR destination dirs all absent; 0/3 ancestries landed. |
| 7 | MAGIC 2021 | HbA1c × {TRANS, EUR, AFR, EAS, SAS, HIS} | `data/raw/sumstats_v2/MAGIC2021/HbA1c/{…}/` | variable | ⬜ | — | FTP (port 21) — test NCSU HPC egress first. 2026-04-24 scan: TRANS/EUR/AFR/EAS/SAS/HIS destination dirs all absent; 0/6 ancestries landed. |

## DUA-gated queue

| # | Source | Trait × Ancestry | Destination | DUA | Submitted on | Approved on | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 8 | MVP BP Giri 2019 | SBP × AFR | `data/raw/sumstats_v2/MVP2019/BP/AFR/` | dbGaP phs001672 | — | — | ⬜ not initiated | 4–8 week lead time; research-purpose text adaptable from AOU-LD-PIPELINE.md. 2026-04-24 scan: destination directory absent (expected — DUA not yet initiated). |

## Already-downloaded (no fetch required)

| # | Source | Trait × Ancestry | Local path | Status | Notes |
|---|---|---|---|---|---|
| 9 | Evangelou 2018 | SBP × EUR | `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz` | ✅ landed (T1 spine) | GRCh37; verify build before re-use |

## Legend

- ⬜ not started
- ⏳ in progress / awaiting approval
- ✅ complete
- 🚫 deferred (rationale required in Notes)
- ❌ failed / unavailable (fallback source required)

## Wave 0 pre-flight probes (2026-04-25)

Three probe outcomes from `tests/m1/wave0_probes.sh` that gate downstream
M1 wave behavior. Captured during `/gsd-execute-phase m1` Wave 0 Task 2
(plan `m1-00-preflight-and-environment-PLAN.md`).

### Probe 1 — MAGIC FTP port-21 egress

- **Probe URL:** `ftp://ftp.sanger.ac.uk/pub/`
- **HTTPS control:** `https://magicinvestigators.org/downloads/`
- **Verdict:** ✅ **PASS** — FTP egress works from current shell context.
- **Downstream impact:** Wave 1 (m1-01) MAGIC HbA1c row 7 (6 ancestries)
  may fetch via FTP; the SUMSTATS-UPGRADE §5 Tier-1 fallback (HTTPS
  portal mirror) is not required.
- **Caveat:** Probe ran in the executor's shell; final Wave 1 fires via
  `bsub` on a compute node. If a compute-node-side FTP block is
  discovered at fire-time, retreat to the HTTPS portal at
  `magicinvestigators.org/downloads/` per the documented fallback.

### Probe 2 — GWAS-Catalog Giri 2019 summary availability (D-06 primary)

- **Probe URL:** `https://www.ebi.ac.uk/gwas/publications/30578418`
- **HTML body size:** 63,005 bytes
- **GCST accession hits:** none (zero matches for `GCST[0-9]{6,}`)
- **Verdict:** ❌ **NO-SUMMARY-FOUND** — Giri 2019 sumstats are NOT
  publicly available on GWAS-Catalog as of 2026-04-25.
- **Downstream impact:** Wave 1 (m1-01) row 13 (MVP-Giri SBP × AFR)
  triggers the **D-06 fallback path: AoU Researcher Workbench AFR-SBP
  derivation** per CONTEXT D-07 (M1 scope expansion documented in
  DEC-2026-04-24-02). Wave 1 marks row 13 status = **DEFERRED** with a
  `.placeholder` file pointing to the AoU derivation SOP at
  `AOU-LD-PIPELINE.md` §2 P1–P7. M1 closeout does NOT block on AFR-SBP;
  the 45×45 LDSC matrix becomes 44×44 until the AoU artifact lands.
- **Carter action (out of band):** Initiate AoU Workbench AFR-SBP
  derivation reusing the AOU-LD-PIPELINE §2 P1–P7 scaffolding when
  bandwidth allows.

### Probe 3 — LDSC 2-trait --rg smoke benchmark

- **Pair tested:** `bmi_EUR.sumstats.gz` ↔ `hypertension_EUR.sumstats.gz`
  (pre-existing pre-pivot munged files at
  `results/pathway/ldsc_partitioned/munged/`).
- **LDSC env:** `.snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python`
  (the snakemake-cached LDSC env with bitarray + numpy=1.26.4 +
  pandas=2.2.1; smoke_dev base lacks bitarray — Rule 3 auto-fix).
- **Reference LD:** `data/external/ldscore/eur_w_ld_chr/` (symlinked to
  Phase 5 staged copy at `data/reference/ldsc/eur_w_ld_chr/`).
- **Wall time (real):** 13.77 seconds (rounded `PAIR_WALL_SECONDS = 13`)
- **LDSC log:** 3,661 bytes; "Summary of Genetic Correlation Results"
  table emitted with all expected columns including `gcov_int`.
- **Verdict:** ✅ **PASS** — pair wall 13s (≪ 15 min/pair budget).
- **Downstream impact:** Wave 3 (m1-03) proceeds at full `--jobs`
  density. The 44 star-topology ldsc.py --rg invocations (one per
  focal trait against trailing trait list, N-1 pairs each) total
  ~990 unique pairs at ~14s/pair ≈ 3.9 hours of pure LDSC compute,
  trivially fits within the long-queue 240 h ceiling. The dynamic
  `--jobs` computation in `m1-03-T2` may use `PAIR_WALL_SECONDS=13`
  from `tests/m1/wave0_probes.log`.

### Reference data staged

- `data/external/liftover/hg38ToHg19.over.chain.gz` — 1,246,411 bytes,
  gzip-valid; SHA-256 `14a712e8e147d9fc8e9d87d51977b46f6f8ddb93efbe5d0843d86b6205f587b1`
  (UCSC golden-path direct fetch).
- `data/external/ldscore/eur_w_ld_chr` — symlink to
  `data/reference/ldsc/eur_w_ld_chr/` (Phase 5 staged copy from 2026-04-14
  via Zenodo URL-rot workaround per `feedback_url_rot_workarounds.md`).
  46 files (chr1..22 .l2.ldscore.gz + .l2.M_5_50 + extras).
- `data/external/ldscore/w_hm3.snplist` — symlink to
  `data/reference/ldsc/w_hm3.snplist`. Line count: 1,217,312 (~1.2M).
- **Note on LDSC URL rot:** Direct curl of the 2026-04-22 plan-spec'd
  Broad URLs (`data.broadinstitute.org/alkesgroup/LDSCORE/eur_w_ld_chr.tar.bz2`
  and `.../w_hm3.snplist.bz2`) returned HTTP 404. Workaround per
  `feedback_url_rot_workarounds.md`: reuse the Phase 5 staged copy at
  `data/reference/ldsc/` (originally fetched from Zenodo 14993076).
  Symlinks under `data/external/ldscore/` give the M1 pipeline the
  plan-spec'd path without duplicating ~1 GB of bytes.

## Refresh log

### 2026-04-24 — quick/260424-j6c

- Scope: Route C manual-fetch status refresh; no new downloads, no DUA actions, no pipeline changes.
- Scanned 23 expected destinations under `data/raw/sumstats_v2/` for rows 1–8.
- 0 destinations exist on disk; 0 destinations have ≥1 file.
- New SHA-256 locks this refresh: 0.
- Prior canonical SHA-256 values preserved verbatim where present (0 pre-existing locks in prior STATUS.md; nothing to preserve).
- Row-level delta:
  - row 1 GIANT2018/BMI/EUR: dir_absent, still_pending (0/1 files present).
  - row 2 Loh2022/BMI/{EUR,AFR}: both EUR + AFR dirs absent, still_pending (0/2 ancestries landed).
  - row 3 PAGE2019/BMI/AFR: dir_absent, still_pending (0/1 files present).
  - row 4 DIAMANTE2022/T2D/{TRANS,EUR,EAS,SAS}: all 4 ancestry dirs absent, still_pending (0/4 ancestries landed; AFR + HIS remain upstream-gated).
  - row 5 GIGASTROKE2022/stroke/{TRANS,EUR,AFR,EAS,SAS}: all 5 ancestry dirs absent, still_pending (0/5 ancestries landed).
  - row 6 GBMI2022/asthma/{MULTI,EUR,AFR}: all 3 ancestry dirs absent, still_pending (0/3 ancestries landed).
  - row 7 MAGIC2021/HbA1c/{TRANS,EUR,AFR,EAS,SAS,HIS}: all 6 ancestry dirs absent, still_pending (0/6 ancestries landed; FTP egress from NCSU HPC still untested).
  - row 8 MVP2019/BP/AFR: dir_absent, still_pending — expected state; dbGaP phs001672 DUA not yet initiated.
- Net progress since prior snapshot: none. Manual-fetch queue remains fully pending across all 8 rows (rows 1–7 portal-navigation + row 8 DUA-gated).
- Scratch artifact: `/tmp/260424-j6c-manual-fetch-scan.tsv` (not committed).

## Update protocol

Set the checkbox and the `Fetched on` / `Approved on` date when a row resolves.
For deferrals, switch to 🚫 and write a one-line rationale. Commit each batch
of updates with `docs(amendments): M1 manual-fetch status — {summary}`.

When all rows reach a terminal state, update
[PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](./PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md)
§3 M1 row to `complete` and route to /gsd-plan-phase for M1 harmonization +
LDSC-munge PLAN.
