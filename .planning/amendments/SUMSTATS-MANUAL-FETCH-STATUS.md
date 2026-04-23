# SUMSTATS Manual-Fetch Status Tracker

Live tracker for the portal-navigation and DUA-gated sources enumerated in
[SUMSTATS-MANUAL-FETCH.md](./SUMSTATS-MANUAL-FETCH.md). Carter updates the
checkboxes as each source lands. The scripted-URL queue (27 files, 40.4 GB)
is complete — see [SUMSTATS-SCRIPTED-FETCH-COMPLETE.md](./SUMSTATS-SCRIPTED-FETCH-COMPLETE.md).

Track B M1 closes when every row below resolves (fetched | DUA-approved |
explicitly deferred with rationale).

## Portal-navigation queue (no DUA)

| # | Source | Trait × Ancestry | Destination | ETA | Status | Fetched on | Notes |
|---|---|---|---|---|---|---|---|
| 1 | GIANT Yengo 2018 | BMI × EUR | `data/raw/sumstats_v2/GIANT2018/BMI/EUR/` | 15s | ⬜ | — | single file; right-click save-as |
| 2 | Loh 2022 | BMI × {EUR, AFR} | `data/raw/sumstats_v2/Loh2022/BMI/{EUR,AFR}/` | ~5 min | ⬜ | — | Loh-vs-Yengo primary-source decision pending Carter |
| 3 | PAGE Wojcik 2019 | BMI × AFR | `data/raw/sumstats_v2/PAGE2019/BMI/AFR/` | ~5 min | ⬜ | — | verify dbGaP-DUA requirement before fetch |
| 4 | DIAMANTE 2022 | T2D × {TRANS, EUR, EAS, SAS} | `data/raw/sumstats_v2/DIAMANTE2022/T2D/{…}/` | ~5 min | ⬜ | — | AFR + HIS NOT YET RELEASED — quarterly recheck |
| 5 | GIGASTROKE 2022 | stroke × {TRANS, EUR, AFR, EAS, SAS} | `data/raw/sumstats_v2/GIGASTROKE2022/stroke/{…}/` | ~15 min | ⬜ | — | JS-rendered portal, 5 per-ancestry accessions |
| 6 | GBMI 2022 | asthma × {MULTI, EUR, AFR} | `data/raw/sumstats_v2/GBMI2022/asthma/{…}/` | ~10 min | ⬜ | — | phenotype manifest via Google Sheets |
| 7 | MAGIC 2021 | HbA1c × {TRANS, EUR, AFR, EAS, SAS, HIS} | `data/raw/sumstats_v2/MAGIC2021/HbA1c/{…}/` | variable | ⬜ | — | FTP (port 21) — test NCSU HPC egress first |

## DUA-gated queue

| # | Source | Trait × Ancestry | Destination | DUA | Submitted on | Approved on | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 8 | MVP BP Giri 2019 | SBP × AFR | `data/raw/sumstats_v2/MVP2019/BP/AFR/` | dbGaP phs001672 | — | — | ⬜ not initiated | 4–8 week lead time; research-purpose text adaptable from AOU-LD-PIPELINE.md |

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

## Update protocol

Set the checkbox and the `Fetched on` / `Approved on` date when a row resolves.
For deferrals, switch to 🚫 and write a one-line rationale. Commit each batch
of updates with `docs(amendments): M1 manual-fetch status — {summary}`.

When all rows reach a terminal state, update
[PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](./PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md)
§3 M1 row to `complete` and route to /gsd-plan-phase for M1 harmonization +
LDSC-munge PLAN.
