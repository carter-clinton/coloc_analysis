---
phase: m1
plan: 01
subsystem: sumstats-upgrade-and-harmonization
plan_id: m1-01-portal-fetches-and-aragam-route
tags: [m1, wave1, downloads, aragam, sha256, deferred-rows, magic-ftp, gigastroke-d02]
dependency-graph:
  requires:
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-00-preflight-and-environment-SUMMARY.md
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (rows updated by m1-00)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH.md (portal protocols)
    - bin/download_sumstats_v2.sh (existing inline 27-row driver — extended in T1)
    - data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt (Wave 0 D-03 audit)
  provides:
    - bin/download_sumstats_v2.sh extended with --manifest, --manifest-stdin, PENDING_* sentinel, DIAMANTE_COOKIE env
    - config/download_manifest_m1_portal.tsv (22 rows × 10 cols)
    - src/snakemake/rules/m1_download.smk (path-parameterized per-source-tag rule + aggregator)
    - src/python/freeze_sha256_manifest.py (deterministic SHA-256 manifest writer)
    - tests/m1/test_freeze_sha256_manifest.py (4/4 PASS)
    - data/raw/sumstats_v2/sha256_manifest.tsv (45 data rows + header, 48.1 GB total)
    - .planning/amendments/sha256_manifest_m1_frozen.tsv (OSF-paste-ready committed copy per D-13)
    - 12 newly landed raw sumstats files (4.42 GB) under data/raw/sumstats_v2/
    - 3 newly inflated Aragam files (~6.96 GB) under data/raw/sumstats_v2/Aragam2022/CAD/
    - 6 .deferred placeholder markers (Loh×2 D-01, GBMI×3 portal, Klarin×1 D-03 fallback)
  affects:
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Wave 1 fire log section appended)
    - config/pipeline.yaml (paths.raw_sumstats_v2 key added)
tech-stack:
  added:
    - none — reused existing curl + xargs + Python 3.11 + bash stack
  patterns:
    - PENDING_* URL sentinel writes .deferred placeholder (driver returns 0; batch continues)
    - requires_cookie_env column → fetch_one prepends `-b "$VAR"` curl arg; unset env → MANUAL ACTION + return 0
    - --manifest (header-skipped TSV) and --manifest-stdin (single-row pipe) flags coexist with no-arg inline mode
    - SHA-256 freeze with --no-mtime + skip-glob → byte-identical output across reruns (OSF reproducibility)
key-files:
  created:
    - config/download_manifest_m1_portal.tsv (22 portal rows × 10 columns)
    - src/snakemake/rules/m1_download.smk
    - src/python/freeze_sha256_manifest.py
    - tests/m1/test_freeze_sha256_manifest.py
    - .planning/amendments/sha256_manifest_m1_frozen.tsv (committed OSF-paste copy)
  modified:
    - bin/download_sumstats_v2.sh (extended with --manifest / --manifest-stdin / PENDING_* / cookie env)
    - config/pipeline.yaml (paths.raw_sumstats_v2 key added)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Wave 1 fire log section)
  staged-on-disk-not-committed:
    - data/raw/sumstats_v2/sha256_manifest.tsv (data/ gitignored; OSF-paste copy is in .planning/amendments/)
    - 12 newly landed raw sumstats files (data/ gitignored per project policy)
    - 3 inflated Aragam2022 tsv/gz files (data/ gitignored)
    - 6 .deferred placeholder markers under data/raw/sumstats_v2/
decisions:
  - GIANT URL rot resolution → giant-consortium.web.broadinstitute.org/images/c/c8/ (was 2/2f/, 404)
  - PAGE 2019 URL resolution → ftp.ebi.ac.uk GCST008025/WojcikG_PMID_invn_rbmi_alls.gz (was hypothetical PAGE_BMI_AFR_ALL_2019-06.tsv path)
  - GBMI 3 rows converted to PENDING_PORTAL_GBMI sentinel (Wix JS-rendered portal, no clean direct URL discoverable in this fire)
  - Klarin 2018 row converted to PENDING_D03_FALLBACK_RESOLUTION sentinel (DOI 10.1038/s41591-018-0090-y resolved to a different paper; AFR-stratified MVP CAD file location unresolved at fire time)
  - DIAMANTE 4 rows AWAITING_COOKIE (driver MANUAL ACTION return 0 — non-fatal; Carter cookie capture is a re-fire-only step)
  - sha256 manifest --skip-glob extended to exclude sha256_manifest.tsv itself + failures.log (otherwise re-runs see different file sizes for the manifest — non-deterministic)
metrics:
  duration_minutes: 39
  task_count: 2
  files_created: 5
  files_modified: 3
  commits: 3
completed: 2026-04-25
---

# Phase M1 Plan 01: Portal Fetches and Aragam Route Summary

Wave 1 closeout: extended the proven `bin/download_sumstats_v2.sh`
xargs -P 5 driver with a manifest-driven mode + PENDING_* sentinel +
DIAMANTE cookie env support, authored a 22-row portal-fetch manifest,
fired in two passes (URL rot triggered Rule 3 corrections + PENDING_*
re-routing), unzipped the Aragam 2022 ZIP per D-03 branch (b), and
froze a 45-row deterministic SHA-256 manifest of the entire raw tree
totaling 48.1 GB. 12 of 22 portal rows LANDED; 6 marked DEFERRED with
.deferred placeholders; 4 DIAMANTE rows AWAITING_COOKIE (non-fatal,
re-fire only). M1 closeout does not block on the deferred rows; Wave
2a/2b harmonizers proceed on the 12 + 27 pre-existing files.

## What Was Built

### Extended download driver (`bin/download_sumstats_v2.sh`)

Backward-compatible extensions — original no-arg invocation still
fires the inline 27-row GLGC/CKDGen/Aragam manifest unchanged
(40.4 GB previously landed, idempotent skip-if-non-empty preserved).

New surface:

| Flag                  | Behavior                                                                                                       |
| --------------------- | -------------------------------------------------------------------------------------------------------------- |
| `--manifest <path>`   | Read 10-col TSV (header skipped); xargs -P 5 dispatch over rows.                                               |
| `--manifest-stdin`    | Read a single header-less TSV row from stdin (used by Snakemake per-source-tag wrapper rule).                  |
| `--help`              | Print usage including cookie env vars + sentinel doc.                                                          |

Schema columns (10 total):
`source_tag, url, target_dir, filename, requires_cookie_env, sha256_expected, trait, ancestry, consortium, year`

Sentinel handling: when `url` matches `PENDING_*`, the driver writes a
`.deferred` placeholder in the target dir, prints a `DEFERRED` log
line, and returns 0. This pattern matches the existing Wave 0 D-06
deferral idiom (Giri 2019).

Cookie augmentation: when `requires_cookie_env` names an env var
(e.g. `DIAMANTE_COOKIE`), the curl call prepends
`-b "${!cookie_env_name}"`. If the env var is unset, the driver
prints `MANUAL ACTION REQUIRED` with the exact capture protocol +
re-fire instruction and returns 0 (does NOT fail the batch).

### Wave 1 portal manifest (`config/download_manifest_m1_portal.tsv`)

22 data rows + 1 header. Coverage:

| # rows | Source                | Trait × Ancestry                         | Notes                                                         |
| ------ | --------------------- | ---------------------------------------- | ------------------------------------------------------------- |
| 1      | GIANT 2018 Yengo      | BMI EUR                                  | URL fix in Pass 2 (giant-consortium.web... new host)          |
| 2      | Loh 2022              | BMI EUR + AFR                            | PENDING_D01_ACCESSION sentinel; D-01 unresolved               |
| 1      | PAGE 2019 Wojcik      | BMI AFR                                  | URL fix in Pass 2 (EBI GCST008025 + WojcikG_PMID file)        |
| 4      | DIAMANTE 2022         | T2D TRANS + EUR + EAS + SAS              | DIAMANTE_COOKIE env required — AWAITING_COOKIE                |
| 4      | GIGASTROKE 2022       | stroke TRANS + EUR + AFR + EAS           | D-02 integer-locked GCSTs (90104534/9/49/44); all LANDED      |
| 3      | GBMI 2022             | asthma MULTI + EUR + AFR                 | PENDING_PORTAL_GBMI sentinel; Wix JS portal (no direct URL)   |
| 6      | MAGIC 2021            | HbA1c TRANS + EUR + AFR + EAS + SAS + HIS | All LANDED via HTTPS portal (Wave 0 Probe 1 FTP also OK)     |
| 1      | Klarin 2018 (D-03 fb) | CAD AFR                                  | PENDING_D03_FALLBACK_RESOLUTION sentinel; KP4CD/Zenodo TBD    |

Row 13 of SUMSTATS-UPGRADE.tsv (Giri 2019 MVP-AFR-SBP) is **not** in
this manifest — Wave 0 Probe 2 NO-SUMMARY-FOUND triggered
DEC-2026-04-24-02 D-06 fallback (AoU derivation in M2). Carter signed
off on AoU AFR-SBP fallback computed in M2, not M1.

### Snakemake rule (`src/snakemake/rules/m1_download.smk`)

Path-parameterized through `config["paths"]["raw_sumstats_v2"]`
(added to `config/pipeline.yaml`). One `m1_download_portal_row`
rule per source_tag (wildcard expansion); emits per-tag completion
flag at `{raw_sumstats_v2}/.download_complete.{source_tag}` so Wave
2 harmonizers can fire as each source lands (D-14 harmonize-as-ready).
`m1_download_all` aggregator rule depends on all source_tag flags.

Manifest discovery walks up to find `config/pipeline.yaml`, so the
rule loads regardless of which Snakefile includes it. Conda directive
points at `envs/m1-download.yml` (staged in m1-00). Resources block
sets `runtime=2880` (standard queue wall ceiling per
`feedback_lsf_queues`).

### SHA-256 freezer (`src/python/freeze_sha256_manifest.py`)

Streams 1 MiB chunks, sorts files lexicographically by POSIX
relative path, writes header + data rows. Default `--skip-glob`
excludes `*.partial`, `*.deferred`, `.download_complete*`. With
`--no-mtime`, two invocations produce byte-identical TSV (OSF-paste
reproducibility per D-13). 4/4 unit tests PASS.

In production we extended the skip-glob to also exclude
`sha256_manifest.tsv` (the manifest file itself) and `failures.log`
(driver-emitted error log, sometimes 0 bytes) — without these
exclusions, re-runs see the new manifest as input and produce a
slightly different size, breaking byte-identical determinism.

## Wave 1 Fire Outcomes

Two driver passes were required.

### Pass 1 (02:17:18) — discovery of URL rot

| Row                          | Pre-flight URL                                                                                                       | Outcome   | Action                                                                          |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------- |
| GIANT2018_BMI_EUR            | `portals.broadinstitute.org/.../images/2/2f/...`                                                                     | HTTP 404  | URL rot — old host redirects to new domain at different image hash              |
| PAGE2019_BMI_AFR             | `ebi.ac.uk/gwas/publications/31217584` (HTML page, not a file)                                                       | HTTP 404  | wrong URL — needed FTP path to GCST008025                                       |
| GBMI2022_asthma_{MULTI,EUR,AFR} | `gbmi-sumstats.s3.amazonaws.com/...`                                                                              | HTTP 404 ×3 | bucket name guess wrong — GBMI portal is Wix-rendered; no clean direct URL    |
| Klarin2018_CAD_AFR           | `ebi.ac.uk/.../GCST005001-GCST006000/GCST005195/Klarin2018_MVP-AFR-CAD_GCST005195.tsv.gz`                            | HTTP 404  | wrong filename — GCST005195 holds CAD_UKBIOBANK.gz (not the AFR-stratified file) |
| DIAMANTE × 4                  | (cookie-required)                                                                                                    | MANUAL ACTION | DIAMANTE_COOKIE env unset — driver returned 0; non-fatal                    |
| Loh2022 × 2                  | `PENDING_D01_ACCESSION`                                                                                              | DEFERRED  | as designed — `.deferred` placeholders written                                  |
| GIGASTROKE × 4 (LANDED)       | EBI FTP integer-locked GCSTs                                                                                         | OK        | 270 — 419 MB each                                                               |
| MAGIC × 6 (LANDED)            | HTTPS portal                                                                                                          | OK        | 97 — 278 MB each                                                                |

### Rule 3 deviations applied (URL rot per `feedback_url_rot_workarounds`)

**[Rule 3 — URL rot] GIANT 2018 BMI/EUR URL fix.**
- Issue: `portals.broadinstitute.org/collaboration/giant/images/2/2f/Meta-analysis_Locke_et_al%2BUKBiobank_2018_UPDATED.txt.gz` returned HTTP 404 after 301 redirect to `giant-consortium.web.broadinstitute.org/images/2/2f/...`.
- Fix: scraped the new portal's index page (`/index.php/GIANT_consortium_data_files`) for the actual link, found `/images/c/c8/` (different hash). Updated manifest URL.
- Verification: `curl -sI ...c/c8/...` returned 200 OK + Content-Length 46,754,937 B.

**[Rule 3 — URL rot] PAGE 2019 BMI/AFR URL fix.**
- Issue: `ebi.ac.uk/gwas/publications/31217584` is the publication HTML page, not a file.
- Fix: queried GWAS-Catalog REST API by PubMed 31217584 → found GCST008025 with `fullPvalueSet=True` → directory listing showed `WojcikG_PMID_invn_rbmi_alls.gz`. Updated manifest URL to FTP path.
- Verification: file landed (1,252,504,421 B; sha 719f474a425f...).

**[Rule 3 — URL rot routing-to-deferred] GBMI ×3.**
- Issue: GBMI portal at `globalbiobankmeta.org/resources` is a Wix-rendered JS site with no scrapable direct URLs. Tried 6 candidate buckets (gbmi-sumstats, gbmi-public, humangenomics, alkesgroup, etc.); all 404. EBI accession GCST90255667 is registered for the multi-ancestry meta but `fullPvalueSet=False`.
- Fix: converted all 3 GBMI rows to `PENDING_PORTAL_GBMI` sentinel. Driver writes `.deferred` markers; Carter resume-action queue documents portal navigation as next step.
- Verification: `.deferred` markers present at 3 GBMI dirs; M1 closeout does not block on these.

**[Rule 3 — URL rot routing-to-deferred] Klarin 2018 D-03 fallback.**
- Issue: DOI `10.1038/s41591-018-0090-y` (cited in m1-00 SUMMARY for the D-03 fallback) actually resolves to a different paper (lung fibrosis, not MVP CAD AFR). The genuine Klarin et al MVP CAD paper has not been precisely located via Crossref / GWAS-Catalog REST in this session. The true MVP-AFR-CAD file lives behind KP4CD, an author Zenodo deposit, or a CHARGE consortium DUA.
- Fix: converted to `PENDING_D03_FALLBACK_RESOLUTION` sentinel. Documented in Carter resume-action queue.

### Pass 2 (02:23:35) — re-fire with corrected manifest

All correctable URLs landed; sentinels emitted markers; idempotent
SKIPs on already-landed Pass 1 files.

### Final landing inventory (45 rows in frozen manifest)

| Source                  | Files | Bytes (sum)         | Notes                                              |
| ----------------------- | ----- | ------------------- | -------------------------------------------------- |
| GLGC 2021 lipids        | 24    | ~37 GB              | pre-existing (Wave 0 inherited; no new fetches)    |
| CKDGen 2019 eGFR        | 2     | ~325 MB             | pre-existing                                       |
| Aragam 2022             | 5     | ~10 GB              | ZIP + 3 inflated tsv/gz + audit manifest from W0   |
| GIANT 2018 BMI          | 1     | 47 MB               | NEW Wave 1 (URL rot fix)                           |
| GIGASTROKE 2022 stroke  | 4     | ~1.27 GB            | NEW Wave 1 (D-02 integer-locked GCSTs)             |
| MAGIC 2021 HbA1c        | 6     | ~1.34 GB            | NEW Wave 1 (HTTPS portal; FTP egress also confirmed) |
| PAGE 2019 BMI           | 1     | 1.25 GB             | NEW Wave 1 (URL rot fix via GCST API)              |
| `download_manifest.tsv` | 1     | 6 KB                | inline-mode driver provenance (kept)               |
| `README.txt`            | 1     | 184 B               | original raw_sumstats_v2 README                    |
| **Total**               | **45**| **48.1 GB**         | byte-identical reruns confirmed                    |

### Aragam D-03 branch verdict

**Branch (b) confirmed.** Wave 0 enumeration (in `data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt`) showed no AFR-specific file inside the ZIP:
- `CAD_GWAS_BBJ_meta.tsv` (3.0 GB; EAS / BBJ component)
- `CAD_GWAS_SEX_STRATIFIED.txt.gz` (1.1 GB; EUR sex-stratified)
- `CAD_GWAS_primary_discovery_meta.tsv` (3.1 GB; trans-ancestry primary discovery)

Wave 1 Task 2 unzipped the ZIP successfully (3 files inflated; ZIP retained for provenance). The Klarin 2018 fallback row remains in the manifest as `PENDING_D03_FALLBACK_RESOLUTION` until Carter locates the AFR-stratified MVP-CAD file.

## Auth Gates / Human Actions

Two true human-action gates surfaced and were handled non-fatally
(driver `return 0` keeps batch flowing):

1. **DIAMANTE × 4 cookie capture (~5 min Carter active).** Resume by
   visiting `https://diagram-consortium.org/downloads.html`,
   accepting ToS, copying DIAGRAM cookies from DevTools → Application →
   Cookies into `name1=value1; name2=value2; ...`, then on HPC:
   `export DIAMANTE_COOKIE="..."` and re-fire
   `bash bin/download_sumstats_v2.sh --manifest config/download_manifest_m1_portal.tsv`
   (idempotent; only the 4 DIAMANTE rows will fetch).

2. **GBMI × 3 portal navigation (~10 min).** Resume by visiting
   `https://www.globalbiobankmeta.org/resources`, click through to
   the phenotype manifest (Google Sheets embedded), locate per-ancestry
   asthma direct URLs, and either (a) update the manifest TSV with
   resolved URLs and re-fire, or (b) drop the files manually into the
   per-ancestry target dirs and re-run the SHA-256 freeze.

Two architectural / D-decisions also remain open (both already
documented in CONTEXT and in this SUMMARY's deferred-row table):

3. **Loh 2022 × 2 D-01 accession resolution.** Carter must resolve
   the GWAS-Catalog accession for the Loh 2022 BMI sumstats before
   Wave 2a can harmonize.
4. **Klarin 2018 D-03 fallback URL.** Carter must locate the
   MVP-AFR-CAD AFR-stratified file (KP4CD database / author Zenodo
   deposit / CHARGE DUA path).

5. **Giri 2019 MVP-AFR-SBP** (DEC-2026-04-24-02; row 13 of
   SUMSTATS-UPGRADE.tsv). NOT in this manifest. Carter initiates AoU
   Researcher Workbench AFR-SBP derivation per AOU-LD-PIPELINE.md
   §2 P1–P7 when bandwidth allows. LDSC matrix becomes 44×44 until
   the AoU artifact lands.

These do not block M1 closeout; Wave 2a/2b harmonizers proceed on
the 12 newly LANDED + 27 pre-existing files (39 total processable
sumstats today).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — URL rot] GIANT 2018 BMI/EUR URL fix.**
- Found during: Task 2 Pass 1.
- Issue: Plan-spec'd URL returned HTTP 404 after redirect.
- Fix: scraped new portal index, updated manifest URL to `/images/c/c8/`.
- Files modified: `config/download_manifest_m1_portal.tsv`.
- Commit: `362de7e`.

**2. [Rule 3 — URL rot] PAGE 2019 BMI/AFR URL fix.**
- Found during: Task 2 Pass 1.
- Issue: Plan-spec'd URL was a publication HTML page, not a file.
- Fix: GWAS-Catalog REST API → GCST008025 → `WojcikG_PMID_invn_rbmi_alls.gz`.
- Files modified: `config/download_manifest_m1_portal.tsv`.
- Commit: `362de7e`.

**3. [Rule 3 — URL rot routing-to-deferred] GBMI × 3.**
- Found during: Task 2 Pass 1.
- Issue: GBMI portal Wix-rendered; no scrapable direct URL; 6 bucket guesses all 404.
- Fix: converted to `PENDING_PORTAL_GBMI` sentinel; documented Carter resume-action.
- Files modified: `config/download_manifest_m1_portal.tsv`, `SUMSTATS-MANUAL-FETCH-STATUS.md`.
- Commit: `362de7e`.

**4. [Rule 3 — URL rot routing-to-deferred] Klarin 2018 D-03 fallback.**
- Found during: Task 2 Pass 1.
- Issue: m1-00 cited DOI 10.1038/s41591-018-0090-y resolves to a different paper; AFR-CAD file location unresolved.
- Fix: converted to `PENDING_D03_FALLBACK_RESOLUTION` sentinel; documented Carter resume-action.
- Files modified: `config/download_manifest_m1_portal.tsv`, `SUMSTATS-MANUAL-FETCH-STATUS.md`.
- Commit: `362de7e`.

**5. [Rule 2 — missing critical functionality] sha256 manifest self-exclusion.**
- Found during: Task 2 determinism verification.
- Issue: Default `--skip-glob` excludes `*.partial`, `*.deferred`, `.download_complete*` but not `sha256_manifest.tsv` itself. Re-run #2 sees the manifest from re-run #1 with a new size, breaking byte-identical determinism (the OSF-paste reproducibility requirement per D-13).
- Fix: extended `--skip-glob` to include `sha256_manifest.tsv,failures.log` at the manifest-freeze invocation. Two consecutive runs with this skip-glob produce byte-identical TSV (verified via `diff`).
- Files modified: invocation of `freeze_sha256_manifest.py` (no source change to the tool — its skip-glob is configurable and already supports this).
- Commit: `362de7e`.

### Decisions deviating from plan suggestion

**6. Manifest row count = 22, not "17" cited in plan front-matter.**
- Plan objective: "Fetch the remaining 17 portal-gated sumstats rows".
- Actual: 22 rows in `config/download_manifest_m1_portal.tsv`.
- Reason: plan body Task 1 enumerates Yengo (1) + Loh (2) + PAGE (1) + DIAMANTE (4) + GIGASTROKE (4) + GBMI (3) + MAGIC (6) + Klarin (1) = **22 rows**, not 17. The "17" in the front-matter was outdated bookkeeping. The 22-row count is the correct one and is what the plan body Task 1 action block prescribes.

**7. SHA-256 manifest 45 data rows (not "27 + N").**
- Plan success criteria: "data/raw/sumstats_v2/sha256_manifest.tsv has >= 27 (pre-existing) + landed-count + 1 header rows".
- Actual: 45 data rows + 1 header = 46 lines. Breakdown: 27 pre-existing + 12 newly LANDED + 3 Aragam-unzip + 2 provenance (`download_manifest.tsv` + `README.txt`) + 1 audit-trail (`aragam_zip_manifest.txt`) = 45.
- Reason: Aragam unzipping inflated 1 ZIP into 1 ZIP + 3 sibling files; these are 3 net new files in the tree. The provenance / audit-trail files are tiny but real artifacts and pass the skip-glob.

## Commits

| Task | Commit  | Title                                                                                          |
| ---- | ------- | ---------------------------------------------------------------------------------------------- |
| T1 (RED)   | `49a555e` | test(m1-01): add failing tests for freeze_sha256_manifest deterministic writer                |
| T1 (GREEN) | `4815a4d` | feat(m1-01): wave-1 portal download driver + manifest + Snakemake rule + sha256 freezer       |
| T2         | `362de7e` | feat(m1-01): wave-1 portal sumstats fired + Aragam unzipped + sha256 manifest frozen          |

## Wave 1 Verification Gate

```
test -f config/download_manifest_m1_portal.tsv               # PASS
test -s bin/download_sumstats_v2.sh                          # PASS
test -f src/snakemake/rules/m1_download.smk                  # PASS
test -f src/python/freeze_sha256_manifest.py                 # PASS
pytest tests/m1/test_freeze_sha256_manifest.py               # 4/4 PASS
test -f data/raw/sumstats_v2/sha256_manifest.tsv             # PASS
[ wc -l < .../sha256_manifest.tsv >= 28 ]                    # 46 lines ≥ 28 PASS
test -f .planning/amendments/sha256_manifest_m1_frozen.tsv   # PASS
ls data/raw/sumstats_v2/Aragam2022/CAD/*.tsv                 # PASS (3 inflated)
test -f .../Aragam2022/aragam_zip_manifest.txt               # PASS (audit trail)
grep -rE "/rs1/researchers|/gpfs_common" <4 m1 wave-1 files> # 0 matches PASS
```

## Downstream Wave Consequences

| Wave / Plan          | Consequence                                                                                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Wave 2a (m1-02a)     | Continuous-trait harmonizers can fire on: GLGC×24, CKDGen×2, GIANT×1, MAGIC×6, PAGE×1, Aragam (TRANS+EUR_sex_strat from unzipped tsv) — minus Loh×2 (DEFERRED), GBMI is binary→Wave 2b. |
| Wave 2b (m1-02b)     | Case-control harmonizers fire on: GIGASTROKE×4, Aragam (TRANS+EAS from unzipped tsv) — minus DIAMANTE×4 (AWAITING_COOKIE), GBMI×3 (DEFERRED), Klarin×1 (DEFERRED). |
| Wave 3 (m1-03)       | LDSC star-topology --rg matrix = 44×44 (45 minus Giri). When DIAMANTE cookies + GBMI portal + Loh D-01 + Klarin D-03 all resolve and re-fire, matrix expands to 50×50 (47 + 3 added GBMI ancestries — minus Giri). |
| Wave 4 (m1-04)       | trait_inventory.yaml schema enforced; entries flagged as DEFERRED until corresponding `.deferred` markers are removed.                                  |

## Self-Check: PASSED

All claimed artifacts present on disk and all 3 task commits resolved
in `git log`. Verification run 2026-04-25T06:39Z:

- 5/5 created files FOUND (`config/download_manifest_m1_portal.tsv`,
  `src/snakemake/rules/m1_download.smk`,
  `src/python/freeze_sha256_manifest.py`,
  `tests/m1/test_freeze_sha256_manifest.py`,
  `.planning/amendments/sha256_manifest_m1_frozen.tsv`)
- 3/3 modified files FOUND (`bin/download_sumstats_v2.sh`,
  `config/pipeline.yaml`, `.planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md`)
- 12/12 newly-LANDED raw sumstats files FOUND on disk under `data/raw/sumstats_v2/`
- 6/6 `.deferred` placeholder markers FOUND on disk
- 3/3 task commits FOUND in `git log` (`49a555e`, `4815a4d`, `362de7e`)
- Wave 1 verification gate: ALL PASS
- Pytest: 4 passed in 0.29s (deterministic SHA-256 contract)
- Path-parameterization gate: 0 hardcoded paths in 4 M1 wave-1 source files
- Determinism gate: two `--no-mtime` invocations of `freeze_sha256_manifest.py`
  produce byte-identical output (`diff` empty)
