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
