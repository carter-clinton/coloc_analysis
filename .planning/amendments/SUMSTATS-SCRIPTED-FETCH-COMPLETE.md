# SUMSTATS v2 scripted-fetch complete

**Status**: ✅ All 27 scripted-URL downloads landed.
**Driver**: [bin/download_sumstats_v2.sh](../../bin/download_sumstats_v2.sh) (committed `cb2ed78`, `xargs -n 1` fix `92a64ce`).
**Destination**: [data/raw/sumstats_v2/](../../data/raw/sumstats_v2/)
**Window**: fired between 2026-04-22 and 2026-04-23 per session continuity.

## Inventory

| Source | Files | Size range | Notes |
|---|---|---|---|
| GLGC 2021 lipids (Graham) | 24 | 705 MB – 762 MB | LDL/HDL/TC/TG × {TRANS, EUR, AFR, SAS, EAS, HIS} |
| CKDGen 2019 eGFR (Wuttke) | 2 | 141 MB (TRANS), 184 MB (EUR) | |
| Aragam 2022 CAD | 1 | 142 MB (zip) | needs unzip before harmonization |
| **Total** | **27** | **40.4 GB total** | mean 1.50 GB / file |

## Integrity

- `find data/raw/sumstats_v2 -type f ... -size -1M` returns zero rows (no stub files).
- Manifest line count (`wc -l data/raw/sumstats_v2/download_manifest.tsv`) = 27, matches file count on disk.
- Downloader is idempotent (skip-if-non-empty), so re-firing is safe.

## Next actions for M1

1. Manual-fetch queue — see [SUMSTATS-MANUAL-FETCH-STATUS.md](./SUMSTATS-MANUAL-FETCH-STATUS.md).
2. Unzip Aragam 2022 before harmonization (Aragam_2022_CARDIoGRAM_CAD_GWAS.zip).
3. Harmonization + LDSC-munge PLAN — deferred to a dedicated `/gsd-plan-phase M1-sumstats-upgrade` session after Route B (M0 closeout) rewrites ROADMAP.md with the M0–M6 phase entries.

## Provenance

Scripted sources cover the 27 directly-downloadable URLs in
[SUMSTATS-UPGRADE.tsv](./SUMSTATS-UPGRADE.tsv). Portal / DUA-gated sources
are tracked separately in [SUMSTATS-MANUAL-FETCH.md](./SUMSTATS-MANUAL-FETCH.md)
with live status at [SUMSTATS-MANUAL-FETCH-STATUS.md](./SUMSTATS-MANUAL-FETCH-STATUS.md).
