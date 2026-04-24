# Novelty Cross-Reference Catalog Lock (M0 Route B snapshot)

This directory holds the **comparator catalog lock manifest** pre-registered in [ROADMAP.md](../../.planning/ROADMAP.md) M5 success criterion #4 and [REQUIREMENTS.md](../../.planning/REQUIREMENTS.md) REQ-CATALOG-VERSION-LOCK. The purpose of the lock is to defeat the reviewer objection, flagged in [Amendment §7.2](../../.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md), that catalog drift between submission and revision can convert a locus from "novel" to "not novel" without any analytical change.

Five novel-variant discovery classes (Classes 1–4 primary + Class 5 supplementary) reference five comparator catalogs:

| Class | Comparator catalogs used |
|---|---|
| 1 — Joint-signal novelty | GWAS Catalog (single-trait GWS hits within ±500 kb) |
| 2 — Ancestry-specific novelty | GWAS Catalog (prior GWS) |
| 3 — Secondary-signal novelty | GWAS Catalog (prior GWS within ±100 kb) |
| 4 — Pleiotropy-class novelty | Pickrell 2016 supplement + Watanabe 2019 GWAS Atlas + Open Targets Genetics L2G (top-3) |
| 5 — Functional-mechanism novelty (supplementary) | ClinVar (pathogenic calls) + primary-literature triage |

## Schema — `catalog_lock_manifest.tsv`

Tab-separated. 7 columns, 1 header row, 5 data rows (one per comparator catalog).

| Column | Type | Description |
|---|---|---|
| `name` | string | Stable catalog identifier (lowercase, underscores). Used as a primary key. Must be unique within the file. |
| `version` | string | Version string. For feeds with release tags, use the tag (e.g., `2026-04-20_weekly_release`). For one-shot supplements, use a provenance-anchored identifier (e.g., `pmc_PMC5207801_NIHMS780506-supplement-2`). Use `pending_M5_pin` for deferred rows. |
| `url` | string | Stable retrieval URL. For M0-locked rows this is the URL the SHA-256 was computed against. For M5-deferred rows this is the best-known canonical URL as of 2026-04-24 — M5 must verify and replace if drift has occurred. |
| `sha256` | string (hex, 64 chars) | SHA-256 of the raw downloaded bytes (pre-decompression). Empty for M5-deferred rows. |
| `fetched_date` | YYYY-MM-DD | UTC date the file was fetched. Empty for M5-deferred rows. |
| `size_bytes` | integer | File size in bytes (from `stat --printf='%s'`). Empty for M5-deferred rows. |
| `status` | enum | `M0-locked` (snapshot complete, SHA-256 populated) or `M5-deferred` (retrieval postponed to M5 cross-reference date). |

## M0 / M5 lock policy

- **M0-locked** rows are frozen today (2026-04-24). Their SHA-256 values are referenced in the OSF amendment and any deviation from these hashes during M5 novelty calls must be surfaced in the manuscript methods.
- **M5-deferred** rows have a documented URL and best-known version string but no hash. At M5 they are fetched, hashed, and flipped to `M5-locked` (a new status value), and the manifest is re-committed. **Rationale for deferring:** the "Small catalogs now, defer large to M5" policy chosen by Carter on 2026-04-24 — keeps the M0 scope pre-registration-anchored without pulling forward substantial M5 download/extraction work.
- **Do not overwrite** an M0-locked row at M5. If ClinVar (the sole M0-locked catalog) has drifted by M5, add a *new* row with `status=M5-locked` and a dated `version` field; keep the M0 row as historical provenance.

## Exact retrieval commands (reproducibility)

### ClinVar — `clinvar_variant_summary` (M0-locked, 2026-04-24)

```bash
cd data/catalogs/
curl -fsSL -o variant_summary.txt.gz \
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
sha256sum variant_summary.txt.gz
stat --printf='%s\n' variant_summary.txt.gz
```

Expected:
- SHA-256: `3be9939676e44a79e906dd167caec45e6e871be55db1a4ddb9269ebf0828e58e`
- size_bytes: `436222584`
- Last-Modified (server): `Mon, 20 Apr 2026 10:18:43 GMT` → encoded as `version=2026-04-20_weekly_release`
- Uncompressed: 3,904,792,091 bytes, 8,920,417 rows, 44 TSV columns

ClinVar is a live feed that rolls over weekly. Re-running the command on a later date will almost certainly produce a different SHA-256. This is expected; the M0 lock is valid only for the `fetched_date` snapshot.

### Pickrell 2016 supplement — `pickrell2016_supplement` (M5-deferred)

**Why M5-deferred despite the file being ~82 KB:** the NCBI PMC supplementary file endpoint at `https://pmc.ncbi.nlm.nih.gov/articles/instance/5207801/bin/NIHMS780506-supplement-2.txt` is gated by a JavaScript proof-of-work challenge that sets a `cloudpmc-viewer-pow` cookie; `curl` alone cannot bypass it. The OA-package fallback at `ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/fe/19/PMC5207801.tar.gz` returned by the PMC OAI endpoint was also inaccessible from this host on 2026-04-24. Rather than solve the POW in an ad-hoc script during M0, the file is deferred to M5.

**M5 retrieval recipe (try in order):**
1. Browser download from <https://pmc.ncbi.nlm.nih.gov/articles/PMC5207801/> — the "Associated Data" panel lists `NIHMS780506-supplement-2.txt`. Save, move to this directory, then `sha256sum` + `stat`.
2. Fallback: `curl` with headless-chromium-generated POW cookie (see pmc-cloudpmc-viewer POW algorithm in the page source).
3. Fallback: direct from the Nature Genetics article landing page <https://www.nature.com/articles/ng.3570> (Supplementary Information panel) — Nature's static-content CDN URL is cookie-free.
4. Fallback: request from corresponding author (Joseph K. Pickrell) or retrieve from a Zenodo/Figshare mirror if one is located.

Paper citation: Pickrell JK et al. (2016). Detection and interpretation of shared genetic influences on 42 human traits. *Nat Genet* 48(7):709–717. DOI `10.1038/ng.3570`. PMID `27182965`. PMCID `PMC5207801`.

### GWAS Catalog associations — `gwas_catalog_associations` (M5-deferred)

EBI releases monthly. The `downloads/alternative` endpoint returns the current-release "all associations" TSV (ontology-annotated).

**M5 recipe:**
```bash
curl -fsSL -o gwas_catalog_associations.tsv \
    "https://www.ebi.ac.uk/gwas/api/search/downloads/alternative"
# Also capture the release tag from the sibling page:
curl -fsSL "https://www.ebi.ac.uk/gwas/docs/file-downloads" | grep -i 'release'
```

At M5, record the release tag (e.g., `r2026-XX-XX`) in the `version` field before hashing.

### Open Targets Genetics L2G — `opentargets_genetics_l2g` (M5-deferred)

Open Targets Platform (which absorbed OT Genetics in 2024) releases quarterly. The L2G outputs are partitioned parquet files under `output/etl/parquet/l2gGoldStandard/` or `output/etl/parquet/l2g/`.

**M5 recipe:**
```bash
# Determine latest release version first:
curl -fsSL "https://platform.opentargets.org/downloads" | grep -i 'release'
# Sync the L2G parquet partition for that release:
rsync -av "rsync://ftp.ebi.ac.uk/pub/databases/opentargets/platform/<release>/output/etl/parquet/l2g/" \
    opentargets_l2g/
# Then hash the partition as a single tarball (for a single SHA-256 anchor):
tar -cf opentargets_l2g_<release>.tar opentargets_l2g/
sha256sum opentargets_l2g_<release>.tar
```

Record `version=<release>` (e.g., `26.03`) in the manifest.

### Watanabe 2019 GWAS Atlas — `watanabe2019_gwas_atlas` (M5-deferred)

CTG Lab at VU Amsterdam hosts the atlas at <https://atlas.ctglab.nl/>. The bulk-download page lists export files (trait-level summary CSV, cross-trait associations).

**M5 recipe:**
1. Visit <https://atlas.ctglab.nl/about/download> and identify the current "export date" tag.
2. Download the cross-trait associations export (likely named `atlas_export_<YYYYMMDD>.zip` or similar).
3. `sha256sum` + `stat` on the downloaded archive.
4. Record `version=export_<YYYYMMDD>` in the manifest.

Paper citation: Watanabe K et al. (2019). A global overview of pleiotropy and genetic architecture in complex traits. *Nat Genet* 51(9):1339–1348.

## M5 handoff checklist

At the M5 cross-reference date, run the following in order and commit atomically:

1. For each row where `status == M5-deferred`: execute the retrieval recipe above, record the new `version`, `url` (if drifted), `sha256`, `fetched_date`, `size_bytes`, and flip `status` → `M5-locked`.
2. Re-verify the ClinVar M0-locked row: re-fetch and compare SHA-256. If identical, update `fetched_date` only and set `status=M5-verified`. If different, add a new row `clinvar_variant_summary_m5` with the new hash and leave the M0 row unchanged.
3. Recompute manifest line/column shape: must still be 7 columns per row, unique `name`, no missing SHA-256 on locked rows.
4. Commit: `data(catalogs): M5 lock — populate SHA-256 for deferred catalogs + re-verify ClinVar`.
5. Update the OSF amendment text file ([.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md](../../.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md)) to reference the commit hash of the M5 lock.

## Known constraints

- **Public data only.** Per [CLAUDE.md](../../CLAUDE.md) and [PROJECT.md](../../.planning/PROJECT.md): no wet-lab, no proprietary catalogs, no industry DUAs required for these comparators.
- **No novelty calls stored here.** This directory holds the catalogs and the lock manifest *only*. Novelty-call outputs (per-class TSVs) land under `results/novelty/` per the M2–M5 ROADMAP deliverables.
- **SHA-256 of raw downloaded bytes, not decompressed content.** For `.gz` files, hash the `.gz`, not the inflated `.txt`. This lets a reviewer fetch the URL and verify the hash in one step without knowing the decompression recipe.
