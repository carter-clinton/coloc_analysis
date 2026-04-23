# AOU-LD-PIPELINE — All of Us Ancestry-Matched LD Reference for coloc_analysis

**Status**: Draft amendment (2026-04-22)
**Owner**: Carter K. Clinton (NCSU ASHES Lab)
**Scope**: Track B infrastructure, M1a (prerequisite for M4 genome-wide fine-mapping)
**Supersedes (partially)**: identity-placeholder AFR LD fallback used in Stage 2 narrow validation (2026-04-22)

---

## 1. Purpose and rationale

The existing fine-mapping pipeline uses the 1000 Genomes Phase 3 AFR superpopulation (n=661) as the LD reference for African-ancestry summary statistics. This reference is chronically miscalibrated for two independent reasons. First, n=661 produces LD matrix entries with standard errors on the order of 1/sqrt(n) ≈ 0.04 per off-diagonal element — large enough that SuSiE-RSS, which treats the LD matrix as fixed and known, will frequently either fail to converge or emit inflated credible-set sizes. Second, 1000G AFR is a panel of continental African reference samples (YRI, LWK, ESN, GWD, MSL, ACB, ASW), whose allele-frequency spectrum and haplotype structure diverge materially from the admixed African-American populations that dominate the modern GWAS cohorts we will colocalize against (MVP, AoU itself, PAGE, UK Biobank AFR-like). The mismatch was made concrete in the 2026-04-22 Stage 2 real-LD narrow validation: EUR regions received real 1000G EUR LD and converged cleanly, while every AFR region had to remain on the identity-placeholder fallback because no fit-for-purpose AFR panel was available in-tree.

Using All of Us v7 controlled-tier WGS to build the AFR LD panel buys three things: (a) an ancestry-matched reference whose sample composition is, by construction, the same population as one of our target GWAS (AoU itself) and a near-match for MVP/PAGE African-American cohorts; (b) ~150× the sample size (target ~80–95k AFR post-QC vs 661); (c) the option to additionally build an AoU-derived EUR panel for cross-ancestry sensitivity analysis against 1000G EUR. What it costs: multi-week workspace setup, non-trivial Dataproc compute time (5–7 days wall clock for ~3000 regions at target parallelism), AoU export review for every summary-level output, and a hard dependency on AoU's publication-disclosure policy. It also introduces a methodological novelty — very few published coloc pipelines use AoU-derived LD — which is either an asset for Nature Genetics or a reviewer hazard depending on how defensively we write the methods.

---

## 2. Prerequisites

Everything below must exist before any Dataproc minutes are spent.

| # | Prerequisite | Status | Owner |
|---|---|---|---|
| P1 | Active AoU controlled-tier access (eRA Commons → AoU Researcher Workbench link) | Carter confirms active | Carter |
| P2 | Registered AoU workspace with approved Data Use Statement (DUS) | TODO | Carter |
| P3 | Research Purpose Statement (RPS) with public description, scientific goals, anticipated outcomes, community considerations | TODO — template in §2.1 | Carter |
| P4 | Workspace billing / funding source (AoU credits or personal GCP billing profile) | TODO — confirm whether ASHES Lab credits cover controlled-tier compute | Carter |
| P5 | Local dev mirror: `conda env` with `hail==0.2.x`, `pyspark`, `google-cloud-storage`, matching the AoU default image version, for offline pipeline development against a tiny toy MT | TODO | Carter |
| P6 | Publications & Presentations (P&P) draft registration in the AoU Researcher Workbench submitted **before** any manuscript submission | TODO — registers at draft stage, updated at submission | Carter |
| P7 | `aou_workbench_client` / Terra `gsutil` familiarity for bucket I/O (read-only smoke test against a public AoU demo workspace recommended) | TODO | Carter |

### 2.1 RPS template language (colocalization LD reference)

> **Public description.** This project builds ancestry-matched linkage-disequilibrium (LD) reference matrices from All of Us whole-genome sequence data to enable statistically valid cross-ancestry colocalization and Bayesian fine-mapping of GWAS loci. Existing public LD panels for populations of African ancestry (e.g., 1000 Genomes Phase 3 AFR, n=661) are underpowered and demographically mismatched for the admixed African-American populations that make up a growing share of contemporary GWAS and biobanks, including All of Us itself. Accurate LD is a precondition for every major fine-mapping method (SuSiE-RSS, FINEMAP, PAINTOR), and without an ancestry-matched reference, African-ancestry GWAS signals cannot be resolved to putative causal variants with the same confidence afforded European-ancestry signals.
>
> **Scientific goals.** (a) Compute per-region LD correlation matrices from ≥80,000 All of Us participants of genetically-inferred African ancestry, at ~1500–3000 ~2 Mb fine-mapping windows defined by independent GWAS associations in the target traits. (b) Optionally compute an AoU European-ancestry parallel panel for cross-ancestry sensitivity analysis. (c) Export the aggregate LD matrices as summary-level files for use in downstream coloc/fine-mapping.
>
> **Anticipated outcomes.** Improved credible-set resolution for African-ancestry signals at colocalized GWAS × cis-eQTL/pQTL loci; methods disclosure describing the AoU-derived LD panel and its validation against 1000G references. No individual-level genotypes or phenotypes will be exported, and no cell counts below 20 will be emitted in any aggregate.
>
> **Community considerations.** This work directly addresses the underrepresentation of African-ancestry populations in post-GWAS fine-mapping by contributing ancestry-matched methodology. Participants of African ancestry in All of Us will benefit from the resulting fine-mapping resolution at loci relevant to traits disproportionately affecting their communities. All outputs are summary statistics; no participant is identifiable.

---

## 3. Ancestry cohort definition in AoU

### 3.1 AFR-ancestry inclusion logic

AoU provides two independent ancestry signals:

1. **PCA-based genetic ancestry**. In the `cb_search_person` table there is a field `ancestry_pred` (or equivalently `pca_ancestry_category` depending on CDR version — **needs verification against current AoU documentation**) giving one of `afr`, `amr`, `eas`, `eur`, `sas`, `mid`, `oth` based on AoU's internal PCA pipeline trained against a 1000G + HGDP reference.
2. **Self-reported race/ethnicity**. Fields `race` and `ethnicity` in the person-level table, harmonized to OMB categories.

Primary inclusion for the AFR panel:

```
ancestry_pred == 'afr'
  AND NOT (related to another included sample at KING kinship ≥ 0.088)
  AND sample_qc.call_rate >= 0.98
  AND sample_qc.heterozygosity within ± 3 SD of AFR-subset mean
```

The kinship threshold of 0.088 corresponds to the standard "up to and including third-degree relatives" cutoff (KING coefficient 2^(−9/2) ≈ 0.0442 is second-degree; 0.088 is first/second boundary; many LD pipelines use 0.0442 — **needs verification which AoU recommends**; we will adopt the more conservative 0.0442 and document the choice). Related-pair pruning preserves the sample with higher call rate (standard KING `--unrelated` greedy pass). AoU publishes a precomputed relatedness table per CDR release; we use that rather than re-running KING.

### 3.2 Self-report cross-check (sensitivity only)

We will not *require* self-reported African American identification — that excludes participants who are AFR-predominant by genetic ancestry but self-identify differently, and doing so would under-sample admixed populations which are precisely what we need. Instead, we compute the LD matrix on the PCA-based AFR cohort and run a sensitivity fit on the subset who **also** self-report Black/African American, to quantify whether restricting to self-ID materially changes the LD estimates. If correlation is >0.995 at lead loci, we proceed with the PCA-based cohort only.

### 3.3 Target cohort size

| Filter | Expected remaining (AoU v7, ~245k WGS) |
|---|---|
| WGS available | ~245,000 |
| ancestry_pred == 'afr' | ~55,000–70,000 (**needs verification** — AoU v7 release notes give genetic ancestry proportions by CDR) |
| After kinship pruning (0.0442) | ~50,000–65,000 |
| After sample QC | ~48,000–62,000 |

The "~100k AFR" figure in the brief is aspirational for AoU v8; v7 is closer to ~60k post-QC. This is still ~75× 1000G AFR and is the correct target for M1a. Flag for Carter: **if v8 lands during pipeline development, we re-run on v8 before export**.

### 3.4 EUR sensitivity cohort (optional)

Same logic, `ancestry_pred == 'eur'`, target ~130k–150k post-QC. Purpose: cross-ancestry validation against 1000G EUR Phase 3.

### 3.5 Full multi-ancestry sensitivity

For a small number of anchor regions (say 5 regions where we have strong EUR fine-mapping and strong AFR GWAS signal), also compute LD on the full multi-ancestry AoU cohort to document how much of the AFR-specific LD structure is lost when pooled.

---

## 4. Variant QC filters

Applied genome-wide before any per-region subsetting. Filters are **ancestry-specific** (HWE and MAF computed within the AFR cohort, not across AoU as a whole).

| Filter | Threshold | Rationale |
|---|---|---|
| MAF | ≥ 0.005 in AFR subset | Lower than the conventional 0.01 because SuSiE benefits from denser variant grids; 0.005 keeps LD estimates stable at n≈60k |
| Call rate | ≥ 0.95 | AoU WGS quality is generally higher than this; this is a floor, not a target |
| HWE | p ≥ 1×10⁻⁶, AFR-only | Tight HWE filter removes sequencing artifacts; AFR-only to avoid admixture-driven false positives |
| Chromosome | autosomes (chr1–22) | chrX handled separately — **out of scope for M1a** |
| Variant class | SNVs + small indels (<50 bp) | SuSiE handles SNVs cleanly; indels included because causal variants at some loci are indels |
| Structural variants | excluded (≥50 bp) | LD for SVs is poorly defined and SuSiE assumptions break down |
| Multiallelics | decomposed into biallelics via `hl.split_multi_hts` | Required for PLINK-style LD and for consistent indexing |
| Mixed variants (MNPs) | left-aligned, re-normalized via `hl.split_multi_hts` | Same |
| AoU flagged variants | drop variants with AoU QC flag (`variant_qc.filters` non-empty) | AoU pre-flags low-quality variants; respect this |

Result: per-chromosome filtered MatrixTable, AFR-subset, ready for per-region LD computation.

---

## 5. LD matrix computation — Hail pipeline

Two implementation paths. We recommend **Path A (Hail BlockMatrix)** as primary; Path B (PLINK) is a fallback for regions where Hail is unexpectedly slow.

### 5.1 Path A — Hail BlockMatrix

```python
# pseudocode / working hail — run inside AoU Dataproc Jupyter kernel
import hail as hl
import numpy as np
from google.cloud import storage
import pandas as pd

hl.init(default_reference="GRCh38", log="/home/jupyter/hail.log")

# --------------------------------------------------------------------------
# 1. Load AoU v7 WGS MatrixTable.  The CDR-specific path is in the workspace
#    environment variable WGS_ACAF_THRESHOLD_MT_PATH (or similar - verify).
# --------------------------------------------------------------------------
WGS_MT_PATH = os.environ["WGS_ACAF_THRESHOLD_MT_PATH"]   # NEEDS VERIFICATION
mt = hl.read_matrix_table(WGS_MT_PATH)

# --------------------------------------------------------------------------
# 2. Attach genetic-ancestry annotations from cb_search_person equivalent.
#    AoU provides an ancestry-prediction HT at a workspace-visible path;
#    path differs by CDR version - NEEDS VERIFICATION.
# --------------------------------------------------------------------------
anc = hl.read_table(os.environ["ANCESTRY_PRED_HT_PATH"])   # NEEDS VERIFICATION
mt = mt.annotate_cols(ancestry=anc[mt.s].ancestry_pred)

# --------------------------------------------------------------------------
# 3. Load AoU-provided relatedness/flagged-samples table and drop relateds.
# --------------------------------------------------------------------------
relateds = hl.read_table(os.environ["RELATED_SAMPLES_HT_PATH"])  # NEEDS VERIFICATION
mt = mt.filter_cols(hl.is_missing(relateds[mt.s]))

# --------------------------------------------------------------------------
# 4. Restrict to AFR cohort and apply sample QC.
# --------------------------------------------------------------------------
mt_afr = mt.filter_cols(mt.ancestry == "afr")
mt_afr = hl.sample_qc(mt_afr, name="sqc")
mt_afr = mt_afr.filter_cols(mt_afr.sqc.call_rate >= 0.98)

# --------------------------------------------------------------------------
# 5. Variant QC within AFR, then filter.
# --------------------------------------------------------------------------
mt_afr = hl.variant_qc(mt_afr, name="vqc")
mt_afr = mt_afr.filter_rows(
    (mt_afr.vqc.AF[1] >= 0.005) & (mt_afr.vqc.AF[1] <= 0.995) &
    (mt_afr.vqc.call_rate >= 0.95) &
    (mt_afr.vqc.p_value_hwe >= 1e-6) &
    (hl.len(mt_afr.filters) == 0)                           # AoU-flagged drop
)

# Split multiallelics (small indels allowed; SVs already excluded upstream).
mt_afr = hl.split_multi_hts(mt_afr)

# Persist as checkpoint so per-region loops don't recompute the filter chain.
CKPT = "gs://fc-secure-<workspace-id>/ld/mt_afr_qc.mt"
mt_afr = mt_afr.checkpoint(CKPT, overwrite=True)
print(f"AFR QC cohort: {mt_afr.count_cols()} samples, {mt_afr.count_rows()} variants")

# --------------------------------------------------------------------------
# 6. Per-region LD: iterate over the region manifest TSV.
# --------------------------------------------------------------------------
regions = pd.read_csv("region_manifest.afr.tsv", sep="\t")
OUT_BUCKET = "gs://fc-secure-<workspace-id>/ld/AFR_aou"

def compute_region_ld(region_row, mt_source):
    rid = region_row.region_id
    interval = hl.parse_locus_interval(
        f"chr{region_row.chr}:{region_row.start_grch38}-{region_row.end_grch38}",
        reference_genome="GRCh38",
    )
    mt_r = hl.filter_intervals(mt_source, [interval])
    # require a minimum number of variants in region; skip otherwise
    n_var = mt_r.count_rows()
    if n_var < 10:
        return {"region_id": rid, "status": "skipped_few_variants", "n_var": n_var}

    # Hail computes correlation between rows (variants) using n_alt_alleles dosage.
    # hl.ld_matrix returns a BlockMatrix of Pearson correlations.
    ld_bm = hl.ld_matrix(
        mt_r.GT.n_alt_alleles(),
        mt_r.locus,
        radius=2_500_000,  # larger than our window so no truncation
    )
    # Collect rsids / chr:pos:ref:alt IDs aligned with BM rows.
    variant_ids = mt_r.aggregate_rows(
        hl.agg.collect(
            hl.str(mt_r.locus) + ":" + mt_r.alleles[0] + ":" + mt_r.alleles[1]
        )
    )
    # rsIDs: prefer mt_r.rsid if populated, else synthetic ID above.
    rsids = mt_r.aggregate_rows(hl.agg.collect(hl.coalesce(mt_r.rsid, hl.missing(hl.tstr))))

    # Materialize to dense numpy (OK for regions ~2Mb ~20k variants -> ~3.2GB float64;
    # use float32 to halve that).
    ld_np = ld_bm.to_numpy().astype("float32")

    # Save to workspace bucket as .npz (matrix + ids).  Actual -> .rds is done
    # post-export in R on NCSU side (see section 8).
    out_path = f"{OUT_BUCKET}/{rid}.npz"
    local_tmp = f"/tmp/{rid}.npz"
    np.savez_compressed(local_tmp, ld=ld_np, variant_ids=np.array(variant_ids),
                        rsids=np.array([r if r is not None else "" for r in rsids]))
    # upload to bucket
    storage.Client().bucket(OUT_BUCKET.split("/")[2]).blob(
        "/".join(OUT_BUCKET.split("/")[3:]) + f"/{rid}.npz"
    ).upload_from_filename(local_tmp)
    return {"region_id": rid, "status": "ok", "n_var": n_var, "out": out_path}

# Drive serially per cluster; parallelism comes from running multiple Dataproc jobs,
# not from Python threads inside one cluster.
results = [compute_region_ld(r, mt_afr) for r in regions.itertuples()]
pd.DataFrame(results).to_csv("ld_afr_run_log.tsv", sep="\t", index=False)
```

Notes on the snippet:

- `hl.ld_matrix` returns a BlockMatrix of Pearson correlations between variant rows, using the provided numeric expression (`n_alt_alleles` → dosage 0/1/2). This is the right LD for SuSiE-RSS: SuSiE uses Pearson correlation on genotype dosages, not D'/r².
- `radius=2_500_000` is a safety margin above our 2 Mb window so the matrix isn't truncated at region edges; actual region LD is subset exactly by the upstream `filter_intervals`.
- `to_numpy()` materializes the dense matrix in driver memory. For a 2 Mb region with ~20k variants at float32, that's ~1.6 GB. For denser regions or larger windows this will OOM — add a fallback to writing the BlockMatrix directly to bucket and only densify at export time.
- `rsid` field: AoU v7 CDR generally populates `rsid` from dbSNP but coverage is imperfect. We emit both rsid and chr:pos:ref:alt synthetic ID so downstream can match either.
- **The entire pipeline lives inside the AoU Workbench.** Only the per-region summary-level `.npz` files ever leave, and only via the approved export path (§7).

### 5.2 Path B — PLINK `--r` as fallback

For regions where Hail BlockMatrix is OOM or unexpectedly slow:

```bash
# export cohort to PLINK1 bfile inside AoU bucket first
plink2 \
    --pgen aou_afr_qc.pgen --pvar aou_afr_qc.pvar --psam aou_afr_qc.psam \
    --chr ${CHR} --from-bp ${START} --to-bp ${END} \
    --maf 0.005 --geno 0.05 --hwe 1e-6 \
    --r square \
    --out ${REGION_ID}
```

Trade-off: PLINK export of 60k samples × autosomes is slow (hours) and the PLINK1 bfile format is size-inefficient. Path B is only worth invoking if Hail fails on specific regions.

### 5.3 Parallelism strategy

- Each Dataproc job processes a chunk of ~150 regions (sized so one 8-hour job finishes the chunk).
- Submit 20 Dataproc jobs concurrently (subject to AoU quota limits — **needs verification**).
- Region manifest is partitioned deterministically by `region_id` hash mod 20.

---

## 6. Region list input format

Consumed by both the Hail driver and the Snakemake integration. Flat TSV at `config/ld_regions.tsv` (generated by Track B M3 programmatic region generation; committed to repo for reproducibility).

**Columns** (required):

| column | type | example |
|---|---|---|
| `region_id` | string, must be filesystem-safe | `r00042_chr16_53500000_55500000` |
| `chr` | int 1–22 (no "chr" prefix) | `16` |
| `start_grch38` | int, 1-based inclusive | `53500000` |
| `end_grch38` | int, 1-based inclusive | `55500000` |
| `ancestry` | enum {AFR, EUR, AFR_aou, EUR_aou} | `AFR_aou` |
| `source_trait` | string, trait that drove region definition | `BMI_UKB_AFR` |
| `lead_variant` | chr:pos:ref:alt | `16:53809247:T:A` |

### Minimal example

```
region_id	chr	start_grch38	end_grch38	ancestry	source_trait	lead_variant
r00042_chr16_53500000_55500000	16	53500000	55500000	AFR_aou	BMI_UKB_AFR	16:53809247:T:A
r00043_chr11_27000000_29000000	11	27000000	29000000	AFR_aou	LDL_MVP_AFR	11:27743253:G:A
r00044_chr6_31000000_33000000	6	31000000	33000000	AFR_aou	CRP_AoU_AFR	6:32021526:C:T
```

One row per region × ancestry; a region is emitted twice when both AFR_aou and EUR_aou panels are needed.

---

## 7. Export protocol

### 7.1 The two-stage export path

1. **Within-workspace stage.** All intermediate products (filtered MT, BlockMatrices, dense `.npz` per region) live in the workspace bucket `gs://fc-secure-<workspace-id>/ld/`. No user action needed; these are already inside the controlled environment.

2. **Out-of-workspace stage.** Summary-level `.npz` LD matrices are requested for egress via AoU's export mechanism:
   - Terra UI → workspace → **Notebooks/Files** → select bucket path → **Request export**
   - Or programmatic: `aou_workbench_client` export endpoint — **needs verification this is available for non-notebook artifacts**
   - AoU review queue: variant-level summary statistics computed from ≥20 participants are typically within the exportable scope. LD matrices from n=60k+ AFR participants comfortably clear the 20-person suppression floor on every cell (each LD correlation entry is computed from all n participants, so no cell is computed from <20).
   - **Unresolved:** whether AoU classifies a full variant × variant LD matrix as "aggregate summary statistics" (exportable by default) vs "derived individual-level data" (requires additional review). We proceed assuming the former and flag the risk in §12.

### 7.2 File size and export throughput

Dominant constraint: file size per region.

- Budget: 20k variants × 20k variants × 4 bytes (float32) = **1.6 GB** dense.
- Compressed `.npz` typically reaches 30–40% of dense size for LD (~500–700 MB). Still sizeable.
- Across 3000 regions: ~1.5–2 TB aggregate before compression, ~500 GB–1 TB compressed.

**Mitigations**, in priority order:

1. **MAF pruning.** Tighten to MAF ≥ 0.01 for *export*, while keeping MAF ≥ 0.005 for internal validation. Drops variant count by ~30% in AFR, quartered matrix size.
2. **Lower-triangular-only storage.** Halve the size; standard for symmetric matrices. Reconstruct full matrix on NCSU side.
3. **Sparse storage** with a correlation threshold (e.g., drop entries |r| < 0.01). Does not work for SuSiE directly but works for downstream LD-pruning operations.
4. **Per-chromosome chunking** for export (bulk move rather than per-region). Lets AoU review one export request per chromosome rather than 3000 individual requests.

Recommendation: export as **lower-triangular float32 `.npz` with MAF ≥ 0.01**, one export request per chromosome.

### 7.3 Ingest on NCSU side

Arrive as `.npz` on GPFS. Convert to `.rds` via an R script once (see §8).

---

## 8. Local integration

### 8.1 Target layout

```
data/processed/ld_reference/
├── EUR_1kg/          # existing, 1000G Phase 3 EUR — 503 samples
│   └── {region_id}.rds
├── AFR_1kg/          # existing, 1000G Phase 3 AFR — 661 samples (fallback only)
│   └── {region_id}.rds
├── AFR_aou/          # NEW — this pipeline's primary output
│   └── {region_id}.rds
└── EUR_aou/          # NEW — optional cross-ancestry sensitivity
    └── {region_id}.rds
```

### 8.2 Conversion `.npz` → `.rds`

One-shot R script, run on the NCSU side after each chromosome batch arrives:

```r
# src/scripts/ld_npz_to_rds.R
suppressPackageStartupMessages({
  library(reticulate); library(Matrix)
})
np <- reticulate::import("numpy")

convert_one <- function(npz_path, rds_path) {
  z <- np$load(npz_path, allow_pickle = TRUE)
  # recover full symmetric matrix from lower triangle if exported that way
  tri <- z$f[["ld"]]
  if (!is.matrix(tri)) stop("unexpected ld shape in ", npz_path)
  if (!isSymmetric(tri)) tri <- tri + t(tri) - diag(diag(tri))
  rsids <- as.character(z$f[["rsids"]])
  vids  <- as.character(z$f[["variant_ids"]])
  snp_ids <- ifelse(nzchar(rsids), rsids, vids)
  dimnames(tri) <- list(snp_ids, snp_ids)
  saveRDS(list(ld = tri, snp_ids = snp_ids), rds_path, compress = "xz")
}
```

### 8.3 Snakemake integration

New rule in `src/snakemake/rules/ld_reference.smk` (paralleling the existing 1000G EUR rule):

```python
rule build_ld_rds_aou_afr:
    input:
        npz = "data/interim/aou_ld_exports/AFR_aou/{region_id}.npz",
    output:
        rds = "data/processed/ld_reference/AFR_aou/{region_id}.rds",
    log:
        "logs/ld_reference/aou_afr/{region_id}.log",
    conda:
        "../envs/r_ld.yaml"
    shell:
        """
        Rscript src/scripts/ld_npz_to_rds.R {input.npz} {output.rds} &> {log}
        """
```

### 8.4 Config flag — which AFR panel to use

`config/finemap.yaml` gains:

```yaml
ld_panel:
  EUR: 1kg              # or aou
  AFR: aou              # preferred; fall back to "1kg" → identity-placeholder chain
  aou_fallback_to_1kg: false     # if AoU panel missing a region, do we fall back?
```

The `run_finemap` rule resolves the LD `.rds` path via a helper that consults this config; existing rule at `src/snakemake/rules/finemap.smk:45` consumes the resolved path as input.

---

## 9. Validation protocol

Before any AoU-derived LD is admitted to production Snakemake DAGs, the following four checks must pass on a 10-region development subset.

### 9.1 Check 1 — Known-locus LD pattern

At a well-characterized locus with published AFR LD figures (FTO 16q12 around rs1558902, or SORT1 1p13 around rs12740374), render the AoU AFR LD matrix as a heatmap and compare visual LD block structure to published figures (e.g., Locke et al. 2015 FTO heatmaps, or the AA-specific LD patterns in Kichaev et al.). **Pass threshold**: block boundaries within ±5 kb of published.

### 9.2 Check 2 — AoU EUR vs 1000G EUR

Compute AoU EUR LD at the same 10 regions; compute entry-wise Pearson correlation against 1000G EUR. **Pass threshold**: mean entry-wise r ≥ 0.97 for variants with MAF ≥ 0.05 in both; ≥ 0.90 for MAF 0.01–0.05. Document any regions below threshold.

### 9.3 Check 3 — SuSiE-RSS convergence on a well-behaved AFR trait

Run SuSiE-RSS with the AoU AFR LD at 16q12 BMI (published AFR GWAS sumstats, e.g., Graff et al. PAGE or MVP BMI). **Pass thresholds**:
- SuSiE `converged == TRUE`
- ≥ 1 credible set at PIP coverage 0.95
- median credible-set size ≤ 30 variants (matching EUR-pipeline expectations)
- lead variant PIP ≥ 0.1 (we don't require it to be ranked #1; AFR fine-mapping is harder)

### 9.4 Check 4 — Identity-placeholder A/B

For the same 10 regions, run SuSiE-RSS twice: once with AoU AFR LD, once with the identity-placeholder fallback we used in Stage 2 narrow validation. Document the yield difference (credible sets emitted, median CS size, lead PIP). This is the headline validation number — it justifies M1a's existence.

All four check outputs go to `.planning/phases/phase-XX-aou-ld/validation/` and are a hard gate for promoting the pipeline from dev to production.

---

## 10. Storage naming and gitignore

### 10.1 Naming

As in §8.1. Strict convention:

- Panel directories: `{ANCESTRY}_{SOURCE}` (e.g. `AFR_aou`, `EUR_1kg`).
- Per-region file: `{region_id}.rds`, where `region_id` follows `r{NNNNN}_chr{C}_{START}_{END}` (zero-padded, hyphen-free, filesystem-safe).
- Intermediate `.npz`: `data/interim/aou_ld_exports/{PANEL}/{region_id}.npz`.

### 10.2 .gitignore additions

```
data/interim/aou_ld_exports/
data/processed/ld_reference/AFR_aou/
data/processed/ld_reference/EUR_aou/
```

`AFR_1kg/` and `EUR_1kg/` already gitignored; no change.

### 10.3 Size budget

| Path | Expected size | Retention |
|---|---|---|
| `data/interim/aou_ld_exports/AFR_aou/` | 500 GB–1 TB | delete after successful `.rds` conversion |
| `data/processed/ld_reference/AFR_aou/` | 300–600 GB (xz-compressed RDS) | keep; backed up to Zenodo at publication |
| `data/processed/ld_reference/EUR_aou/` | 500 GB–1 TB (larger cohort, denser LD) | keep if built |
| Total new footprint on GPFS | ~1–2 TB | within `clintonlab` project quota — **confirm with cluster admin** |

---

## 11. Compute cost estimate

Ballpark only. AoU credit pricing and GCP Dataproc rates change — refer to current AoU billing docs at fire time.

**Per-cluster config (recommended starting point)**:
- 1 master: `n1-standard-8`
- 4 workers: `n1-highmem-16` (highmem because LD dense matrices are RAM-bound, not CPU-bound)
- 500 GB SSD per worker
- Preemptible workers disabled for the main pipeline (LD computation is not checkpoint-friendly)

**Per-region timing** (empirical from analogous Hail LD workloads; **needs verification on AoU**):
- Small/sparse region (2 Mb, ~8k variants): 8–12 min
- Typical region (2 Mb, ~20k variants): 15–25 min
- Dense HLA-adjacent region (2 Mb, ~50k variants): 45–90 min

**Aggregate**:
- 3000 regions × 20 min average = 1000 cluster-hours = ~42 cluster-days on a single cluster.
- At 20 concurrent clusters: ~2 days raw compute.
- With job setup, failures, retries, QC checkpointing: **5–7 days wall clock**.

**Dollar range**: AoU credits are the relevant currency; a Dataproc cluster of the above spec runs approximately $5–10/hour (highmem-16 × 4 workers + master + storage) in general GCP list pricing. 1000 cluster-hours ≈ $5k–$10k order of magnitude. **This must be confirmed against current AoU credit rates, which differ from public GCP list pricing, and against Carter's available credit balance before launch.**

**Cost reduction levers** if budget is tight:
1. Reduce cluster to 2 workers (doubles wall time, halves cost).
2. Use preemptible secondary workers for the ~60% of regions that are low-variant-density (3–5× cheaper).
3. Process only the 500 highest-priority regions in the first pass; batch the rest.
4. Restrict MAF to ≥ 0.01 throughout (smaller matrices, faster computation, smaller export).

---

## 12. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | AoU export policy classifies variant × variant LD matrices as "derived individual-level data" and blocks export | **Medium** | **Critical** | Pre-check with AoU support team before computing anything; have a written classification in hand. Fallback: compute LD inside AoU and run SuSiE inside AoU, only exporting the credible-set tables. |
| R2 | Per-region LD file size exceeds AoU export per-file or per-batch limits | Medium | High | MAF ≥ 0.01 for export; lower-triangular storage; per-chromosome bundled requests; sparse format if unavoidable |
| R3 | Compute cost exceeds Carter's available credits | Medium | High | Phase launch: 10-region dev → 500 priority-region batch → remaining regions. Stop between batches to re-estimate |
| R4 | AoU EUR vs 1000G EUR show material discrepancy (Check 2 fails) | Medium | Medium | Expected for MAF 0.01–0.05; would be unexpected for common variants. Document in methods; consider reporting both panels in Track B results for transparency |
| R5 | AoU v7 → v8 release during pipeline development; would need re-run | Low-Medium | High | Check AoU release cadence at project start; if v8 is within 2 months, wait for it |
| R6 | Publication submission blocked because AoU P&P registration lapses | Low | Critical | Register P&P at draft stage (P6); update at every major change; do not submit without confirmation |
| R7 | `ancestry_pred` field name or path changes across CDR releases | Medium | Low-Medium | Pin CDR release version in workspace config; re-verify at pipeline start |
| R8 | Kinship pruning leaves AFR cohort smaller than expected (< 40k) | Low | Medium | Document N in manuscript; n=40k is still >60× 1000G AFR and sufficient for LD |
| R9 | AoU-derived LD exhibits unexpected pattern (e.g., structured residual admixture LD at low MAF) that trips SuSiE | Medium | Medium | Check 3 and Check 4 in §9 catch this; report lambda-GC-equivalent metric for LD matrix quality |
| R10 | Time-to-first-usable-panel exceeds Track B M4 critical path | **High** | High | Sequence: dev pipeline on a 10-region manifest **before** Track B M3 completes region generation. The 10-region panel should exist by M3 landing, so M4 can start the moment region generation finishes |
| R11 | AoU publication disclosure text changes after manuscript draft | Low | Low | Use the templated AoU-provided citation verbatim; check disclosure language ≤ 1 week before submission |
| R12 | Hail BlockMatrix OOM on dense regions (HLA, 8p23 inversion) | Medium | Low | Path B (PLINK) fallback; also consider block-wise LD with larger `block_size` |

**Items I flag as requiring immediate attention before any workspace spend:** R1 (AoU export classification — get this in writing), R3 (cost cap and staged launch plan), R10 (sequencing against Track B M3 timeline).

---

## 13. AoU publication policy integration

Text to insert in Track B manuscript.

### 13.1 Methods — LD reference paragraph

> Ancestry-matched linkage-disequilibrium reference matrices for African-ancestry fine-mapping were computed from whole-genome sequence data in the All of Us Research Program (v7 Controlled Tier, Curated Data Repository release C2025Q1 — update to actual release at submission). Analysis was restricted to participants with genetically-inferred African ancestry (`ancestry_pred == "afr"`) after removal of related individuals at KING kinship coefficient ≥ 0.0442, yielding n = \{FINAL_N\} samples. Per-variant QC required minor allele frequency ≥ 0.005 in the AFR subset, variant call rate ≥ 0.95, Hardy-Weinberg p-value ≥ 10⁻⁶ in AFR, and removal of AoU-flagged variants. Multiallelic sites were decomposed into biallelic variants. For each fine-mapping region (±1 Mb around each lead associated variant), Pearson correlation linkage-disequilibrium matrices were computed from allele dosages using Hail v0.2.x (`hl.ld_matrix`). All individual-level computation was performed within the All of Us Researcher Workbench (Terra-hosted Google Cloud environment); only summary-level LD matrices were exported. Lower-triangular LD matrices were converted to serialized R objects for use in downstream SuSiE-RSS fine-mapping.

### 13.2 Acknowledgments

> The All of Us Research Program is supported by the National Institutes of Health, Office of the Director: Regional Medical Centers: 1 OT2 OD026549; 1 OT2 OD026554; 1 OT2 OD026557; 1 OT2 OD026556; 1 OT2 OD026550; 1 OT2 OD 026552; 1 OT2 OD026553; 1 OT2 OD026548; 1 OT2 OD026551; 1 OT2 OD026555; IAA #: AOD 16037; Federally Qualified Health Centers: HHSN 263201600085U; Data and Research Center: 5 U2C OD023196; Biobank: 1 U24 OD023121; The Participant Center: U24 OD023176; Participant Technology Systems Center: 1 U24 OD023163; Communications and Engagement: 3 OT2 OD023205; 3 OT2 OD023206; and Community Partners: 1 OT2 OD025277; 3 OT2 OD025315; 1 OT2 OD025337; 1 OT2 OD025276. In addition, the All of Us Research Program would not be possible without the partnership of its participants.

> **(Verify current funding acknowledgment text at submission — AoU updates this periodically.)**

### 13.3 Required citation

> The All of Us Research Program (ClinicalTrials.gov Identifier: NCT03658122).

### 13.4 Data availability statement

> Aggregate LD matrices derived from All of Us data will be deposited in Zenodo at publication, after All of Us review and approval. Individual-level All of Us data are not publicly available; qualified researchers may apply for controlled-tier access at researchallofus.org.

---

## 14. Timeline

Week numbering relative to kick-off of M1a, which is gated on prerequisites P1–P4.

| Week | Activity | Exit criterion |
|---|---|---|
| 1 | Workspace setup, DUS approval, RPS finalized, billing profile attached, P&P draft registered. Local dev environment mirrored. | Workspace accessible; a trivial Hail "hello world" runs on Dataproc |
| 2 | Cohort definition pipeline: run AFR QC filters, kinship pruning, sample QC. Produce checkpointed `mt_afr_qc.mt`. | Cohort table with final N, per-chromosome variant counts, QC summary |
| 2–3 | LD pipeline dev on 10-region subset (handpicked: 3 EUR 1000G-comparable, 5 AFR known-signal, 2 HLA-adjacent stress test) | All 10 regions produce a `.npz`; Checks 1–4 (§9) pass |
| 3 | Validation: run Checks 1–4, write up validation memo, checkpoint for human review | Validation memo committed; approved by Carter |
| 4 | Region list integration (wait for Track B M3 if not already done). Scale-up dry-run on 100 regions. | 100-region batch completes; cost per region falls within budgeted range |
| 5–7 | Full scale-up: 3000 regions across 20 concurrent clusters in chunks. | All regions produce `.npz` or are flagged; run log complete |
| 7 | Export request to AoU, per-chromosome. | All `.npz` files landed in NCSU GPFS |
| 8 | `.rds` conversion, Snakemake integration, end-to-end fine-mapping smoke test | `run_finemap` rule produces credible sets using AoU AFR LD |

**Critical path concern**: the 10-region dev pipeline (week 2–3) should complete **before** Track B M3 region generation lands. That way, Track B M3 output goes directly into the already-validated scale-up infrastructure.

---

## 15. Open questions

Decisions I cannot make for Carter — these need explicit answers before week 1 starts.

1. **Does AoU export policy permit variant × variant LD matrices as aggregate summary data?** (R1) — requires a written answer from AoU support. Kill or proceed gate.
2. **Kinship threshold: 0.0442 (third-degree) or 0.088 (second-degree)?** Community defaults vary; AoU has a recommendation — which is it for LD panel construction?
3. **Use AoU's precomputed ancestry-prediction table, or re-run PCA inside the workspace?** Precomputed saves compute but ties us to AoU's choice of reference and thresholds. Recommendation: use precomputed for M1a, document the dependency.
4. **Build AoU EUR in parallel, or defer to M1b?** Adds ~40% to compute cost but gives us the Check 2 validation substrate directly. Recommendation: build AoU EUR on the same 10-region dev subset; defer full-scale AoU EUR to M1b.
5. **Is the region list from Track B M3 frozen at M1a launch, or do we allow it to grow?** If it grows, do we re-compute incrementally or re-run? Recommendation: freeze at M1a week 4; any additions after that become "M1a supplementary batch."
6. **Release-version pinning: lock to AoU v7 C2025Q1, or track latest?** Tracking latest is nicer scientifically, disastrous operationally. Recommendation: pin at kickoff; re-pin at manuscript revision round.
7. **Does H3Africa (~3500 samples across continental Africa) or PAGE (~50k, mixed ancestry) serve as a better backstop if AoU falls through?** H3Africa is continental African (same limitation as 1000G AFR, just bigger); PAGE is admixed but access is slower. Recommendation: AoU primary; if AoU blocks, PAGE is the backstop, not H3Africa.
8. **Who reviews the validation memo in §9?** Sole author constraint means self-review only; document explicitly that OSF-posted validation memo is the external reviewer substitute.

---

**End of amendment.**
