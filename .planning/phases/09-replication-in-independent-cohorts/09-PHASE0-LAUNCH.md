---
date: 2026-04-14
context: Phase 0 data infrastructure first-production launch attempt
status: PARTIAL — 1kG VCFs complete; 3 reference-data sources blocked by URL rot
---

# Phase 0 Data Infrastructure First-Production Launch

## Summary

Attempted to launch Phase 0 reference data downloads in parallel background
to unblock Phase 5 + Phase 9 production. Result: **1kG Phase 3 VCFs landed
successfully (15 GB, ~70 sec wall-clock via 5-way parallel xargs)**, but
3 of 4 download-rule URL families are dead. URL audit + replacement is
required before Phase 5 reference data can land.

## What landed (READY for downstream phases)

### 1kG Phase 3 VCFs — `data/raw/1kg/vcf/`

22 autosomal VCFs + tabix indices, downloaded from **NCBI mirror** (alternative
to broken EBI path).

| Item | Size | Source |
|------|------|--------|
| chr1.vcf.gz – chr22.vcf.gz | 15 GB total | `https://ftp.ncbi.nlm.nih.gov/1000genomes/ftp/release/20130502/` |
| chr*.vcf.gz.tbi (22 files) | ~3 MB total | NCBI mirror (same path) |
| `data/raw/1kg/integrated_call_samples.panel` | 55 KB | EBI (panel URL still works) |

**Phase 1 implication:** `download_1kg_vcf` rule expectations satisfied.
Phase 1 LD reference build (`build_ld_rds`) can proceed once Phase 1 also
gets sample lists (DEF-RO7-01 — `TRANS.samples` still missing).

**Required config update:** `config/pipeline.yaml` `onekg.ftp_base` should
point to `https://ftp.ncbi.nlm.nih.gov/1000genomes/ftp/release/20130502`
(NCBI mirror) instead of the broken EBI path
`https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502`. One-line config fix.

## Findings — URL rot at scale

### Finding 5 — Broad GCS reference data requires authentication (LDSC + LDSC-SEG)

**HEAD-checked URLs (all returned 400 Bad Request):**
- `https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/weights_hm3_no_hla.tgz`
- `https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/1000G_Phase3_frq.tgz`
- `https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/1000G_Phase3_plinkfiles.tgz`
- `https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/w_hm3.snplist.bz2`
- `https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/Multi_tissue_gene_expr.tgz`
- `https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/Multi_tissue_chromatin.tgz`

**Diagnosis:** GCS bucket name `broad-alkesgroup-public-requester-pays` is
literally a requester-pays bucket — anonymous HTTPS returns 400. Requires
authenticated `gsutil` access with billing project header
(`-u {project_id}`), or an alternate anonymous mirror.

**Affected:** Phase 5 LDSC partitioned heritability + LDSC-SEG (3 of 6
Phase 5 analytical components) cannot run. Phase 9 COJO (D-04c
supplementary) also blocked since it requires
`1000G_Phase3_plinkfiles.tgz`.

**Resolution paths:**
- (a) Set up GCS authentication — `gcloud auth login` + project-billing config + `gsutil cp -u $PROJ`
- (b) Use Zenodo mirror — Zenodo record `10515792` (and others) hosts
  baseline LD scores; per-file URL audit needed
- (c) Use `ldsc-zenodo` package or similar community-maintained mirror

**Recommended:** (b) — Zenodo is the canonical academic-mirror; URLs are
stable; no authentication needed.

### Finding 6 — Broad S3 baselineLD URL returns 404

**Affected URL:**
- `https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/baselineLD_v2.2_ldscores.tgz`

**Diagnosis:** Bucket `broad-alkesgroup-ukbb-ld` exists for UKBB-LD
(separate dataset) but does not house the baseline LD scores. The plan
research used a stale URL.

**Affected:** Phase 5 partitioned heritability (`download_ldsc_baseline`
rule) cannot run.

**Resolution:** Find current canonical URL — most likely Zenodo record
or migrate to alternate Broad bucket. Same URL audit task as Finding 5.

### Finding 7 — UCLA Box HESS panel URLs returned 404 (expired)

**Affected URLs (both 404):**
- `https://ucla.box.com/shared/static/l8cjbl5fkge7plsb96xybnrjmhbmsgq5.gz`
- `https://ucla.box.com/shared/static/6pzgep7kuy0e3t4t1dpyk9mgpizlt28j.gz`

**Diagnosis:** Box "shared static" links can expire when the owner
revokes the share or the Box account is deactivated. These URLs were cited
in Phase 5 RESEARCH.md from the HESS GitHub repo.

**Affected:** Phase 5 HESS local genetic covariance + Phase 9 HESS-related
COJO references blocked.

**Resolution:** Visit HESS GitHub (huwenboshi/hess) for current LD panel
download instructions. Likely moved to Zenodo or Google Drive.

### Finding 8 — CNCR (MAGMA) serves JS-redirect HTML, not files

**Affected URLs (HEAD returns 200 but body is HTML splash page, ~132 KB):**
- `https://ctg.cncr.nl/software/MAGMA/prog/magma_v1.10_static.zip`
- `https://ctg.cncr.nl/software/MAGMA/aux_files/NCBI37.3.gene.loc.gz`
- `https://ctg.cncr.nl/software/MAGMA/ref_data/g1000_eur.zip`
- `https://ctg.cncr.nl/software/MAGMA/aux_files/dbsnp151.synonyms.zip`

**Diagnosis:** CNCR website now uses JavaScript-based redirects/auth gates
that curl cannot follow. Even with browser User-Agent, the response is the
same 132-KB splash HTML. The CNCR research group may have moved MAGMA hosting.

**Affected:** Phase 5 MAGMA gene-set enrichment + COJO (uses MAGMA's
g1000_eur reference). Effectively blocks 2 of 6 Phase 5 components.

**Resolution:** Find alternate MAGMA distribution — Possibilities:
- GitHub mirrors (search "MAGMA-software")
- Zenodo deposit (some authors mirror tools)
- Direct email request to CNCR lab
- Use MAGMA via a conda package if one exists

**Recommended:** Check bioconda for `magma-software` or similar.

### Finding 9 — EBI 1000 Genomes path restructured

**Affected URLs (404):**
- `https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr{N}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz`

**Diagnosis:** EBI restructured 1000 Genomes hosting. The `release/20130502/`
date-prefixed VCF path no longer serves the integrated VCFs. The panel file
in the same directory still exists.

**Workaround applied:** Switched to NCBI mirror at
`https://ftp.ncbi.nlm.nih.gov/1000genomes/ftp/release/20130502/` — same files,
working endpoint. All 22 VCFs downloaded successfully (15 GB).

**Required config update:** `config/pipeline.yaml` `onekg.ftp_base` should
be updated to NCBI mirror. One-line config fix.

## Forward work — proposed follow-up tasks

### Quick task #1: Update onekg.ftp_base config (5 min)

Change `config/pipeline.yaml`:
```yaml
onekg:
  ftp_base: "https://ftp.ncbi.nlm.nih.gov/1000genomes/ftp/release/20130502"  # was EBI; NCBI works
```

Verify by `snakemake download_1kg_vcf --dry-run` resolves cleanly.

### Quick task #2: Phase 5 reference URL audit (1-2 hours)

Audit each broken URL family and update `pathway.smk` + any config:
- LDSC baseline + weights + frq + plinkfiles + hapmap3 → identify Zenodo or alt mirror
- LDSC-SEG Multi_tissue annotations → same
- HESS LD panel → check huwenboshi/hess GitHub for current path
- MAGMA binary + refs → find alt distribution (bioconda? GitHub mirror?)

For each: HEAD-check → update URL in `pathway.smk` rules → grep-verify → small commit.

### Quick task #3: Defer DEF-RO7-01 (TRANS.samples) one more iteration

DEF-RO7-01 (Phase 1 build_ld_rds needs `data/raw/1kg/TRANS.samples`) was
deferred to Phase 9. With 1kG VCFs now landed, the next blocker for Phase 1
LD building is the missing TRANS sample list. The 1kG panel file IS landed
(`integrated_call_samples.panel`), so a small Python or awk script could
generate `TRANS.samples` as the union of EUR+AFR+EAS+AMR sample IDs.

## Disk usage after launch

```
data/raw/1kg/                     15 GB  (1kG VCFs + indices + panel)
data/raw/replication/             5.0 GB (FinnGen + MVP + BBJ T2D, from earlier smoke)
data/reference/                   0    (MAGMA stubs cleared after URL-rot diagnosis)
TOTAL                             20 GB

Available on /rs1:                29 TB
```

## What this attempt validates

- ✓ Parallel curl + xargs strategy works well (15 GB across 22 files in ~70 sec via 5-way parallelism — saturated NCBI bandwidth)
- ✓ NCBI 1000 Genomes mirror is a viable alternative to EBI's broken path
- ✓ 1kG infrastructure is unblocked for Phase 1 LD reference building (modulo TRANS.samples + EBI→NCBI config update)
- ✗ Phase 5 reference data downloads need a URL audit before any further compute can be queued
- ✗ MAGMA distribution channel needs alt mirror identification

## Recommended next sequence

1. **Quick task: `onekg.ftp_base` config swap** (5 min) — unblocks Phase 1 dry-run
2. **Quick task: Phase 5 reference URL audit** (1-2 hours, can be a research-mode quick task) — unblocks Phase 5 + Phase 9 COJO
3. **Quick task: TRANS.samples generator** (15 min) — closes DEF-RO7-01
4. After (1)-(3) land: launch Phase 1 LD reference build (2-4 hours of compute) — first real Phase 1 run
5. After Phase 1: launch Phase 2 QTL coloc, then Phase 5, then full Phase 9 production
