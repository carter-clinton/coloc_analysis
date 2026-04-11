# Phase 1: coloc.susie fine-mapping spine — Research

**Researched:** 2026-04-11
**Domain:** Statistical genomics — coloc.susie replacement, SuSiE policy, LD panel plumbing
**Confidence:** HIGH for API/version claims and locked LD strategy; MEDIUM for HGDP+1kG AFR compute cost (requires empirical measurement); MEDIUM for complex-region trait intersections.

## Summary

Phase 1 replaces `coloc.abf` with `coloc.susie` in exactly **one active Snakemake callsite** (`run_coloc_pair` in `src/snakemake/rules/multitrait.smk:116` → `src/legacy/region_analysis/scripts/run_coloc.R:420`). A second legacy callsite exists in `src/legacy/genome_wide/scripts/run_coloc_genomewide.R:197` but is NOT wired into any active Snakemake rule — only into historical bash submission scripts under `src/legacy/genome_wide/scripts/submit_chunk_*.sh`. The grep assertion in CONTEXT.md verification step 6 must be scoped to `src/snakemake` plus the *active* `src/legacy/region_analysis` path, not all of `src/legacy/`.

The currently-pinned `envs/r_coloc.yml` version (`r-coloc=5.2.3`, `r-susier=0.14.2`) already includes `coloc.susie`, so no env bump is required for the API itself. The bottleneck work is (a) plumbing **UKBB-LD tiled (Weissbrod 2020)** EUR LD into the project's per-region `.rds` pattern — ~170 GB of NPZ tiles on AWS Open Data Registry, no Hail dependency, (b) building HGDP+1kG AFR LD from phased BCFs (no precomputed AFR LD available anywhere — must be computed), and (c) writing the SuSiE policy loader + convergence retry ladder + QC dashboard.

**Primary recommendation:** Decompose Phase 1 into **5 waves, 6 PLAN.md files** — policy + fit persistence first, UKBB-LD tiled and HGDP+1kG LD building in parallel, coloc.susie rule and QC dashboard last. See §Wave-ordered decomposition at the end.

<user_constraints>
## User Constraints (from CONTEXT.md + post-discuss-phase resolutions)

### Locked Decisions

**G1 — coloc.susie wiring strategy: Option A (persist fit + new coloc rule)**
- Modify `run_susie_rss.R` to additionally `saveRDS(fit, <output>.fit.rds)` alongside existing JSON.
- New script `src/snakemake/scripts/run_coloc_susie.R` loads both `.fit.rds` files and calls `coloc::coloc.susie(fit1, fit2)`.
- New rule `run_coloc_susie` in `src/snakemake/rules/coloc.smk` (new file) depends on two `run_finemap` outputs.
- Legacy JSON output and `summarize_finemap_results.py` consumer stay intact — the `.fit.rds` is purely additive.

**G2 — `config/susie_policy.yaml`:**
- **L cap:** `L=10` default with L-saturation flag when all 10 slots retained post-purity.
- **min_abs_corr sweep:** `{0.1, 0.5, 0.9}` via `susie_get_cs(fit, min_abs_corr=...)` — no refit.
- **Convergence retry ladder:** max_iter=200 → regularize LD eps=1e-4 → flag+exclude Tier1.
- **L-saturation:** flag only; supplementary L=20 rerun as sensitivity table.

**G3 — Hybrid complex regions:** Data-flagged (`l_saturated` OR `n_CS ≥ 3` at default min_abs_corr=0.5) PLUS 4 pre-specified complex regions (see G3b below — scope narrowed from original 6 list to the 4 that intersect Phase 1 trait set).

**G3b — Complex regions added to `config/regions_curated.csv` (post-discuss resolution of B-02):**

| region_id | chr | start | end | source | rationale | trait_list |
|-----------|-----|-------|-----|--------|-----------|------------|
| 9p21_CDKN2A | 9 | 21000000 | 23000000 | G3_complex | CDKN2A/CDKN2B/ANRIL dense signal | t2d, stroke |
| APOE_19q13 | 19 | 44000000 | 46000000 | G3_complex | APOE/TOMM40/APOC1 complex signal | t2d, hypertension |
| HLA_6p21 | 6 | 25000000 | 35000000 | G3_complex | MHC; extreme long-range LD | asthma |
| SLC2A9_urate | 4 | 9000000 | 11000000 | G3_complex | Large urate effect (indirect BP via urate) | hypertension |

- New `source` value `G3_complex` distinguishes these from the 8 existing rows.
- `config/susie_policy.yaml` `complex_regions.pre_specified` list matches these 4.
- **LPA/KIV-2 and chr8 inversion deferred to Phase 2** pending lipid and allergic-disease sumstats ingestion. Methods fragment must note: "Phase 1's complex-region sensitivity sweep covers 4 of the 6 G3 pre-specified regions that intersect the current trait set."
- **Column-name caveat:** the existing `config/regions_curated.csv` schema (trait_list vs. trait_ancestries vs. a different name) is to be verified by the planner before writing the new rows; the ID/chr/start/end/source/rationale fields are fixed.

**G4 — LD reference (Option D hybrid, UPDATED post-B-01 resolution):**
- EUR → **UKBB-LD tiled (Weissbrod et al. 2020)** on AWS Registry of Open Data — `s3://broad-alkesgroup-ukbb-ld/UKBB_LD/` — 2,763 × 3Mb tiles, ~170 GB total, NPZ format, anonymous HTTPS access. **This is a deliberate substitution from a literal reading of "Pan-UKBB in-sample LD"**; justified by (a) same underlying UKB EUR cohort (~337K "white British"), (b) operational tractability (170 GB vs. 14.1 TB), (c) alignment with modern fine-mapping stacks (echoLD, mapgen, PolyFun all use this exact dataset). Phase 2 may upgrade to Pan-UKBB raw BlockMatrix if warranted — not in Phase 1 scope.
- AFR → gnomAD HGDP+1000G merged panel (new download + per-region extraction, targeting v3.1.2)
- EAS/SAS/AMR → 1000G Phase 3 (already cached in `{LD_REF_DIR}/{ancestry}/{region}.rds` from Phase 0)

**G5 — QC report dimensions:** D1 (z-score sanity: KS test, max|z|, λ_GC) + D2 (convergence: niter, converged, ELBO) + D3 (LD quality: `susieR::kriging_rss`) + D4 (CS purity, effective size, top-3 variants) + D6 (Quarto HTML dashboard). D5 plots deferred.

**G6 — UKBB-LD tiled as locked substitution (post-discuss B-01 resolution):**
- LD source is Weissbrod 2020 UKBB-LD (AWS Open Data Registry), NOT Pan-UKBB raw BlockMatrix.
- No Hail dependency. No Java. Download via `boto3` / anonymous HTTPS + NPZ extraction in Python.
- Methods fragment must document the substitution rationale.
- OSF pre-registration amendment (Wave 5 task) records the substitution against DOI 10.17605/OSF.IO/PVB5J.

### Claude's Discretion
- Exact Snakemake rule input/output glue for `.fit.rds` dependency
- File layout within `src/snakemake/scripts/` and `src/snakemake/rules/`
- Quarto template column ordering and filtering UI
- NPZ→`.rds` bridge implementation (Python writes `.npz`, tiny R helper reads it and writes `.rds`, OR direct Python write via `pyreadr`)
- Exact AWS region endpoint for UKBB-LD download (us-east-1 per bucket)
- Plan count within the 5-6 range recommended in CONTEXT.md

### Deferred Ideas (OUT OF SCOPE)
- PP.H4 threshold sweep → Phase 2 (REQ-3)
- Negative-control regions/genes → Phase 2 (REQ-7)
- hyprcoloc multi-trait coloc → Phase 2
- eQTL/pQTL/sQTL coloc → Phase 2
- Per-locus LocusZoom PDFs (D5) → generated on-demand from cached fits
- Methods section text → Phase 11
- Replication cohort application → Phase 9
- LPA/KIV-2 and chr8 inversion complex regions → Phase 2 (deferred per B-02 resolution)
- Pan-UKBB raw BlockMatrix in-sample LD → Phase 2 potential upgrade (per B-01 resolution)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-2 | SuSiE complex-region handling explicit: (a) convergence failures, (b) L cap, (c) min_abs_corr sensitivity, (d) coincident CS collapse policy. Policy YAML loaded by `finemap.smk`; sensitivity sweep with ≥3 values reported as supplementary table. | §Standard Stack (susieR 0.14.2 API, coloc 5.2.3 API), §Architecture Patterns (fit persistence + policy loader), §Common Pitfalls (convergence thresholds, tile-region alignment), §Code Examples (run_coloc_susie.R skeleton + UKBB-LD NPZ extraction), §Validation Architecture (monotonicity test for sweep) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- 100% public data — UKBB-LD tiled dataset is on AWS Registry of Open Data (public, no DUA). gnomAD HGDP+1kG is public (CC-BY). No DUA issues.
- GPFS filesystem. Avoid worktree isolation. `/rs1` is scratch-friendly for ~170 GB UKBB-LD download + ~100-200 GB HGDP+1kG BCF download.
- R + Snakemake + conda stack. No web/TS/React research.
- Snakemake 7.32.4 pinned via `envs/python_stats.yml`. Python 3.11 in `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/`.
- `run_susie_rss.R` and `run_coloc.R` live under `src/legacy/region_analysis/scripts/`. Per DECISIONS.md ("Legacy code reuse"), these ARE edited in place — they are Category (a) "the reference that the new version replaces". CONTEXT.md confirms: `run_susie_rss.R` is modified, `run_coloc.R` is renamed to `run_coloc_abf_legacy.R` and deprecated.
- OSF pre-registration submitted 2026-04-10 (DOI 10.17605/OSF.IO/PVB5J) — Phase 1 deliverables must align with pre-reg methods (policy YAML is the canonical reference). **Phase 5 task: amendment note documenting (a) UKBB-LD tiled substitution for Pan-UKBB raw BlockMatrix, (b) 4 G3 complex regions vs. original 6 list.**

## Standard Stack

### Core

| Library | Version | Purpose | Why standard |
|---------|---------|---------|--------------|
| `coloc` | 5.2.3 (pinned in `envs/r_coloc.yml`) | `coloc.susie()` replaces `coloc.abf()` | [VERIFIED: rdocumentation.org/packages/coloc/versions/5.2.3/topics/coloc.susie] — coloc.susie is present in 5.2.3. Earliest version with coloc.susie is 5.1.0. |
| `susieR` | 0.14.2 (pinned in `envs/r_coloc.yml`) | `susie_rss()` + `susie_get_cs()` post-hoc + `kriging_rss()` diagnostic | [VERIFIED: `envs/r_coloc.yml:15`] susieR 0.14.2 provides `susie_get_cs(fit, min_abs_corr=...)` for post-hoc sweep without refit. |
| `R` | 4.4.2 (pinned) | Runtime | [VERIFIED: `envs/r_coloc.yml:11`] |
| `r-yaml` | 2.3.10 (pinned) | Load `config/susie_policy.yaml` into `run_susie_rss.R` | [VERIFIED: `envs/r_coloc.yml:14`] Already present — no env change needed for policy loader. |
| `r-data.table` | 1.16.4 | Sumstats IO + credible set table | [VERIFIED: `envs/r_coloc.yml:12`] |
| `r-optparse` | 1.7.5 | CLI arg parsing (already used) | [VERIFIED: `envs/r_coloc.yml:13`] |
| `r-Matrix` | present via r-base | LD matrix dense ops | [VERIFIED: used by `run_susie_rss.R:5`] |
| `r-jsonlite` | via base | JSON output | [VERIFIED: `run_susie_rss.R:4`] |

### Supporting (for new rules)

| Library | Version | Purpose | When to use |
|---------|---------|---------|-------------|
| `quarto-cli` | 1.5.x | D6 HTML dashboard | Single Quarto template for per-locus QC. **NOT in any env currently — new dep.** [CITED: quarto.org/docs/get-started/] |
| `r-rmarkdown` | CRAN latest | Quarto R backend | Required alongside quarto for `.qmd` R code blocks |
| `numpy` | 1.26.x | UKBB-LD NPZ tile loading + per-region matrix slicing | [CITED: numpy.org] Standard for `.npz` scipy-sparse/dense array IO |
| `scipy` | 1.13.x | `scipy.sparse.load_npz` if UKBB-LD tiles ship as sparse; dense loader via `np.load` otherwise | [CITED: UKBB-LD README uses numpy `.npz` format with LD as dense triangular] |
| `boto3` | 1.34.x | Anonymous S3 access to `broad-alkesgroup-ukbb-ld` bucket | [CITED: boto3 docs] — `boto3.client('s3', config=Config(signature_version=UNSIGNED))` for anonymous public buckets |
| `pandas` | 2.2.x | UKBB-LD variant-index TSV handling | Standard for the companion `.gz` variant list files |
| `plink2` | v2.00a5 or newer | HGDP+1kG AFR LD build from BCFs | [VERIFIED: `envs/plink.yml` exists] `plink2 --r-phased` or `--r2` computes region-LD from genotypes |
| `bcftools` | 1.21 | Subset BCF by region + ancestry sample list | Standard for HGDP+1kG BCF access |
| Anonymous HTTPS via `requests` / `curl` | — | Download HGDP+1kG BCFs from `https://storage.googleapis.com/gcp-public-data--gnomad/...` | Avoids gsutil/gcloud credential plumbing for public buckets |

### Environment decision

`envs/r_coloc.yml` needs **one addition**: `r-rmarkdown` — for Quarto rendering. Quarto itself is a *separate* env `envs/qc_dashboard.yml` (Python-based with `quarto-cli` from conda-forge) that shells out to R. Keeping quarto out of `r_coloc.yml` avoids ballooning the primary coloc env.

A new env `envs/ld_build.yml` is created for LD panel building. **Contents (lightweight):**
```yaml
name: ld_build
channels: [conda-forge, bioconda]
dependencies:
  - python=3.11
  - numpy=1.26
  - scipy=1.13
  - pandas=2.2
  - boto3=1.34
  - requests
  - r-base=4.4
  - r-data.table
  - bcftools=1.21
  - plink2
```
No Hail, no Java, no pyspark — all dropped per B-01 resolution. The R portion is just for the NPZ→`.rds` bridge helper.

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| UKBB-LD tiled (Weissbrod 2020) for EUR | Pan-UKBB raw BlockMatrix (14.1 TB, Hail required) | **LOCKED: UKBB-LD wins for Phase 1.** Same underlying UKB EUR cohort (~337K white British). Pan-UKBB raw BlockMatrix is theoretically better (matches Pan-UKBB sumstats cohort exactly including non-EUR split) but 100× larger and requires Hail/Java. Phase 2 may revisit if merited. |
| Python+numpy for UKBB-LD tile extraction | R-native NPZ reader | No mainstream R NPZ reader exists. Python + numpy is standard and the NPZ→.rds bridge is a ~20-line R helper. |
| plink2 for HGDP+1kG AFR LD | Pre-computed gnomAD v3 whole-cohort LD | gnomAD v3 whole-cohort LD is not per-ancestry. CONTEXT.md G4 requires AFR in-sample LD (n≈730 post-merge). No shortcut — LD must be built. |
| Quarto for D6 | RMarkdown with `rmarkdown::render()` | RMarkdown is simpler (no Quarto install), but Quarto has better interactive tables (DT/reactable) and forward-compat. Acceptable fallback if Quarto install fails in conda. |
| Anonymous HTTPS for BCF downloads | gsutil / gcloud SDK | HTTPS via `requests` avoids credential-management plumbing; public buckets serve anonymous HTTPS identically to authenticated reads. |

**Installation verification command (read-only, user runs after approval):**
```bash
# Verify coloc/susieR versions resolve in the pinned env
conda run -n r_coloc Rscript -e 'packageVersion("coloc"); packageVersion("susieR")'
# Expected: [1] '5.2.3' and [1] '0.14.2'
```

## Architecture Patterns

### Recommended project structure (additive to existing layout)

```
config/
├── susie_policy.yaml           # NEW — REQ-2 policy (G2 schema + 4 pre-specified complex regions)
├── regions_curated.csv         # MODIFY — add 4 G3_complex rows
└── ...
schemas/
├── susie_policy.schema.yaml    # NEW — validation, Phase 0 D-06 pattern
└── ...
src/snakemake/
├── rules/
│   ├── finemap.smk             # MODIFY — add .fit.rds output, remove stroke_afr_susie_sweep placeholder
│   ├── ld_reference.smk        # MODIFY — add download_ukbb_ld_tiles + build_hgdp_1kg_ld rules
│   ├── coloc.smk               # NEW — run_coloc_susie rule
│   └── qc.smk                  # MODIFY — add build_susie_qc_dashboard rule
├── scripts/
│   ├── run_coloc_susie.R             # NEW — loads 2 .fit.rds, calls coloc.susie
│   ├── download_ukbb_ld_tiles.py     # NEW — boto3 UKBB-LD tile download + per-region .rds conversion
│   ├── ukbb_ld_tile_to_region_rds.py # NEW (or merged into above) — NPZ tile → region submatrix
│   ├── build_hgdp_1kg_ld.py          # NEW — plink2 on public-HTTPS BCFs → per-region .rds
│   ├── plink_ld_to_rds.R             # NEW — small R helper (plink .ld text → .rds)
│   ├── susie_qc_report.qmd           # NEW — Quarto dashboard template
│   └── susie_qc_aggregate.py         # NEW — collect JSON outputs into a single dashboard input
src/legacy/region_analysis/scripts/
├── run_susie_rss.R             # MODIFY in place (DECISIONS.md legacy category-a)
├── run_coloc.R                 # RENAME → run_coloc_abf_legacy.R
└── filter_finemap_summary.py   # MODIFY — non_converged exclusion + L-saturation flag + cache-clear documentation note
envs/
├── r_coloc.yml                 # VERIFY only (5.2.3 already good; optionally add r-rmarkdown)
├── ld_build.yml                # NEW — lightweight: numpy + scipy + boto3 + r-base + plink2 + bcftools
└── qc_dashboard.yml            # NEW — quarto-cli + r-rmarkdown + dashboard deps
```

### Pattern 1: Fit persistence with additive output

**What:** `run_susie_rss.R` writes BOTH the existing JSON and a new `.fit.rds` alongside. Snakemake `run_finemap` rule declares multiple outputs.
**When to use:** Whenever a downstream tool needs the full fit object (not just summary statistics).
**Example:**
```r
# Source: verified susieR 0.14.2 API
# After fit <- susie_rss(...) at run_susie_rss.R:388
fit_rds_path <- sub("\\.json$", ".fit.rds", opt$output)
saveRDS(fit, file = fit_rds_path)
```

Snakemake multi-output pattern:
```python
# Source: Snakemake 7.32.4 docs — rules can declare multiple outputs
rule run_finemap:
    output:
        json = finemap_output("{method}", "{trait}", "{ancestry}", "{region}"),
        fit  = finemap_output("{method}", "{trait}", "{ancestry}", "{region}").replace(".json", ".fit.rds"),
    shell: ...
```

Downstream rule declares BOTH inputs explicitly so the DAG resolves:
```python
rule run_coloc_susie:
    input:
        fit_a = lambda wc: finemap_output("susie", wc.trait_a, wc.ancestry, wc.region).replace(".json", ".fit.rds"),
        fit_b = lambda wc: finemap_output("susie", wc.trait_b, wc.ancestry, wc.region).replace(".json", ".fit.rds"),
        policy = "config/susie_policy.yaml",
    output:
        os.path.join(MULTITRAIT_DIR, "coloc_susie", "{pair_id}.json"),
    conda: "envs/r_coloc.yml"
    shell:
        r"""
        Rscript src/snakemake/scripts/run_coloc_susie.R \
          --fit-a {input.fit_a} --fit-b {input.fit_b} \
          --policy {input.policy} --pair-id {wildcards.pair_id} \
          --output {output}
        """
```

### Pattern 2: Policy YAML loader replaces env-var constants

**What:** Replace the env-var constants at `run_susie_rss.R:14-16`:
```r
MIN_LD_OVERLAP <- as.integer(Sys.getenv("SUSIE_MIN_LD_OVERLAP", "50"))
MIN_LD_COVERAGE <- as.numeric(Sys.getenv("SUSIE_MIN_LD_COVERAGE", "0.5"))
MIN_LD_MIN_USE <- as.integer(Sys.getenv("SUSIE_MIN_LD_MIN_USE", "10"))
```
with a YAML-driven policy loader:
```r
library(yaml)
policy <- yaml::read_yaml(opt$policy)
MIN_LD_OVERLAP <- policy$susie$min_ld_overlap %||% 50L
L_DEFAULT <- policy$susie$L %||% 10L
MAX_ITER_PRIMARY <- policy$susie$max_iter_primary %||% 100L
MAX_ITER_RETRY <- policy$susie$max_iter_retry %||% 200L
LD_REG_EPS <- policy$susie$ld_regularization_eps %||% 1e-4
COVERAGE <- policy$susie$coverage %||% 0.95
MIN_ABS_CORR_DEFAULT <- policy$susie$min_abs_corr_default %||% 0.5
MIN_ABS_CORR_SWEEP <- policy$susie$min_abs_corr_sweep %||% c(0.1, 0.5, 0.9)
```

### Pattern 3: Convergence retry ladder

The current script at lines 388-409 has a 2-step retry (primary → regularized → identity). The G2c ladder requires a 3-step retry with a distinct "non-converged" terminal state instead of falling back to identity. Proposed structure:
```r
run_susie_with_ladder <- function(subset, R, policy, ld_status, ld_source) {
  # Step 1: primary fit
  fit1 <- tryCatch(susie_rss(z, R, L=policy$L, coverage=policy$coverage,
                             max_iterations=policy$max_iter_primary),
                   error = function(e) NULL)
  if (!is.null(fit1) && isTRUE(fit1$converged)) return(list(fit=fit1, status="converged_primary"))

  # Step 2: increase max_iter
  fit2 <- tryCatch(susie_rss(z, R, L=policy$L, coverage=policy$coverage,
                             max_iterations=policy$max_iter_retry),
                   error = function(e) NULL)
  if (!is.null(fit2) && isTRUE(fit2$converged)) return(list(fit=fit2, status="converged_max_iter"))

  # Step 3: regularize LD
  R_reg <- regularize_ld(R, eps=policy$ld_regularization_eps)
  fit3 <- tryCatch(susie_rss(z, R_reg, L=policy$L, coverage=policy$coverage,
                             max_iterations=policy$max_iter_retry),
                   error = function(e) NULL)
  if (!is.null(fit3) && isTRUE(fit3$converged)) return(list(fit=fit3, status="converged_regularized"))

  # Step 4: flag + keep
  return(list(fit=fit3 %||% fit2 %||% fit1, status="non_converged"))
}
```
**Critical:** the fit object must be returned even when non-converged, so `filter_finemap_summary.py` can exclude based on status rather than on null fit.

### Pattern 4: Post-hoc min_abs_corr sweep (no refit)

```r
# Cost is trivial — operates on the single cached fit
sweep_values <- policy$susie$min_abs_corr_sweep  # c(0.1, 0.5, 0.9)
sweep_results <- lapply(sweep_values, function(macor) {
  cs <- susie_get_cs(fit, min_abs_corr = macor)
  list(
    min_abs_corr = macor,
    n_CS = if (!is.null(cs$cs)) length(cs$cs) else 0L,
    total_pip_sum = if (!is.null(cs$cs)) sum(sapply(cs$cs, function(idx) sum(fit$pip[idx]))) else 0
  )
})
```

### Pattern 5: UKBB-LD tile → region submatrix extraction

**What:** UKBB-LD ships as 2,763 × 3Mb tiles. Most Phase 1 curated regions (~1-2 Mb) fall inside a single tile. Complex regions like `HLA_6p21` (~10 Mb) span 3-4 tiles and require concatenation.

**Tile → region mapping algorithm:**
```python
# Source: UKBB-LD README (Weissbrod 2020) + AWS Open Data Registry bucket layout
# Bucket: s3://broad-alkesgroup-ukbb-ld/UKBB_LD/
# Naming: chr{N}_{start}_{end}.npz + chr{N}_{start}_{end}.gz (variant list)

def region_to_tiles(chrom, start, end, tile_index):
    """Return list of (tile_start, tile_end) that overlap [start, end]."""
    overlapping = []
    for t_start, t_end in tile_index[chrom]:  # pre-computed from bucket listing
        if t_end >= start and t_start <= end:
            overlapping.append((t_start, t_end))
    return overlapping

def build_region_ld(chrom, start, end):
    tiles = region_to_tiles(chrom, start, end, TILE_INDEX)
    if len(tiles) == 1:
        npz = np.load(f"chr{chrom}_{tiles[0][0]}_{tiles[0][1]}.npz")
        R_full = reconstruct_from_triangular(npz)   # UKBB-LD stores upper triangle
        variants = pd.read_csv(f"chr{chrom}_{tiles[0][0]}_{tiles[0][1]}.gz", sep='\t')
        mask = (variants['pos'] >= start) & (variants['pos'] <= end)
        return R_full[np.ix_(mask, mask)], variants[mask]
    else:
        # Multi-tile concatenation — union of variants, diagonal-block LD
        # Cross-tile LD is NOT available in UKBB-LD tiled dataset (each tile is independent)
        # HLA handling: take the UNION of variants but explicitly set cross-tile blocks to 0
        # OR accept the diagonal-block approximation and flag it in the output
        blocks = [np.load(f"chr{chrom}_{t[0]}_{t[1]}.npz") for t in tiles]
        R_bd = scipy.linalg.block_diag(*[reconstruct_from_triangular(b) for b in blocks])
        # ... variant list concat + position filter ...
        return R_bd_filtered, variants_concat
```

**When to use:** Phase 1 region extraction for all EUR LD panels.
**Anti-pattern to avoid:** Do NOT attempt to reconstruct cross-tile LD by cross-correlating haplotypes — the raw haplotypes are NOT in UKBB-LD (only the per-tile R matrices are). For HLA specifically, the block-diagonal approximation is a documented limitation; flag it in the `ld_source` field as `"ukbb_ld_tiled_block_diagonal"` so the QC dashboard can surface it.

### Pattern 6: Output the legacy JSON schema for downstream compatibility

`run_coloc_susie.R` must emit a JSON file compatible with the existing downstream consumers (`summarize_coloc_results.py`, `augment_coloc_summary.py`, `build_coloc_h4_reports.py`, `build_coloc_top_hits_table.py`). The legacy schema has these top-level fields (from `run_coloc.R:431-457`):

```
base_region, ancestry, trait_a, trait_b, chr, start, end,
n_common_snps, n_merge_chrpos,
summary: {nsnps, PP.H0.abf, PP.H1.abf, PP.H2.abf, PP.H3.abf, PP.H4.abf},
diagnostics: {...},
top_snps: [...]
```

`coloc.susie` returns **one summary row per pairwise signal comparison**, not a single global summary. Compat strategy:

**Option A (recommended): Compat layer.** Emit the same legacy top-level keys, with `summary` containing the **best** (max PP.H4) pairwise comparison so existing downstream still runs. Add a new `susie_pairs: [...]` array with all pairwise rows for downstream tools that know about it. This keeps all existing `augment_coloc_summary.py` / `build_coloc_h4_reports.py` logic unchanged in Phase 1. Phase 2 can introduce new consumers that read `susie_pairs`.

**Option B (not recommended in Phase 1):** Change the schema and update all 5 downstream consumers. Too much cross-cutting risk for a T1 spine phase.

### Anti-patterns to avoid

- **Calling `coloc.susie(fit1, fit2)` with non-susie fit objects.** The function auto-detects and will invoke `runsusie()` internally — but that means it **re-fits**, losing the whole point of Option A (persist + cache). Must pass susie_rss fit objects directly, which the function recognizes via `class(dataset1)`.
- **Writing `.fit.rds` to a path not declared in Snakemake output.** Snakemake will not track it; downstream rules will not see it as a dependency. Use multi-output.
- **Using `runsusie()` from coloc instead of `susie_rss()`.** `runsusie()` is coloc's thin wrapper; if upstream already uses `susie_rss()` directly, don't double-wrap — save the `susie_rss` output. **EXCEPTION:** If the Wave 1 roundtrip test (see Validation Architecture) shows `coloc.susie(fit_a, fit_b)` warns or silently refits on `susie_rss` output, switch to `coloc::runsusie()` (one-line change in `run_susie_rss.R`).
- **Assuming `susie_rss` and `runsusie` produce identical fit objects.** They do produce compatible structures for `coloc.susie`, but `runsusie` sets the class to `"susie"` explicitly, which `coloc.susie` dispatches on. **Action item:** verify with `class(fit)` in the modified `run_susie_rss.R` and explicitly `class(fit) <- c("susie", class(fit))` if needed.
- **Using the genome_wide script path (`src/legacy/genome_wide/scripts/run_coloc_genomewide.R`).** Do NOT wire this into the new coloc.smk rule — it's a parallel legacy path that was never integrated. Only the `region_analysis` path is in scope.
- **Attempting to reconstruct cross-tile LD for HLA.** UKBB-LD tiles are independent; cross-tile off-diagonal blocks must be approximated as zero (block-diagonal) and flagged in output.

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| SuSiE fit for GWAS sumstats | Custom EM for single-effect regression | `susieR::susie_rss()` | Mature, well-validated, integrated with coloc dispatch |
| Post-hoc credible set filtering | Re-run susie with different thresholds | `susieR::susie_get_cs(fit, min_abs_corr=)` | The sweep is free at post-hoc — don't waste compute |
| LD mismatch detection | Custom z-score residual scan | `susieR::kriging_rss(z, R)` returns `list(plot, table)` with `logLR` + `|z|` thresholds (log LR > 2 and |z| > 2 flag allele flip candidates) [CITED: susieR docs] | Standard reference diagnostic |
| UKBB-LD NPZ parsing | Custom binary reader | `numpy.load(npz_path)` + upper-triangle reconstruction | Standard numpy; UKBB-LD README describes the exact format |
| Per-ancestry LD from BCF | Custom haplotype-pair counting | `plink2 --bcf {in} --keep {sample_list} --extract {variant_list} --r2 square` or `--r-phased` | plink2 handles phased/unphased, allele-flip bookkeeping, MAF filtering |
| Coloc.susie output parsing | Custom pairwise-row aggregator | `coloc::coloc.susie(fit1, fit2)$summary` is already a `data.table` with one row per pairwise comparison | Native API |
| Quarto dashboard interactive tables | Hand-rolled HTML + JS | `reactable::reactable()` or `DT::datatable()` in the Quarto `.qmd` | Standard R-ecosystem interactive tables, works in Quarto out of the box |
| Snakemake DAG inspection for `.fit.rds` tracking | Manual file path globs | Declare `.fit.rds` as a named output in `run_finemap`, and an explicit named input in `run_coloc_susie` | Snakemake resolves automatically |
| Retry ladder for non-convergence | try/catch chain with state mutation | Structured `run_susie_with_ladder()` function returning `list(fit, status)` | Makes the policy testable and auditable |
| Anonymous S3 access | Hand-rolled HTTP client | `boto3.client('s3', config=Config(signature_version=UNSIGNED))` for UKBB-LD; `requests.get()` for public-HTTPS buckets | Both are one-liners; boto3 is the AWS standard for open-data buckets |

**Key insight:** The Phase 1 work is **wiring and policy**, not algorithm development. Every statistical primitive already exists in `susieR` and `coloc`. The risk is in plumbing, schema compatibility, and LD panel tile alignment — not in the math.

## Runtime State Inventory

This is a code-change phase with new file artifacts, not a rename/refactor. However, because the locked decisions include LD panel swaps and fit-object persistence, the following runtime state dimensions matter:

| Category | Items found | Action required |
|----------|-------------|------------------|
| Stored data | **Existing `.rds` LD matrices under `{LD_REF_DIR}/{EUR,AFR,EAS,SAS,AMR}/{region}.rds` from Phase 0 (1000G Phase 3)** — will be *partially* overwritten: EUR and AFR replaced by new panels per G4. EAS/SAS/AMR kept as-is. Existing `results/fine_mapping/susie/*.json` from any Phase 0 dry-run are disposable. | Plan must either (a) use distinct output dirs for the new EUR/AFR panels (e.g. `{LD_REF_DIR}/EUR_ukbb_ld/` and `{LD_REF_DIR}/AFR_hgdp_1kg/`) and update `finemap.smk` to point at them via config, OR (b) overwrite in place with a clear migration note. Recommendation: (a) for auditability. The `{ancestry}` wildcard in existing rules already supports this with a config swap. |
| Live service config | None — this project has no live services. OSF pre-registration DOI 10.17605/OSF.IO/PVB5J exists — **Wave 5 must post an amendment note documenting (a) UKBB-LD tiled substitution for Pan-UKBB raw BlockMatrix, (b) scope narrowing from 6 → 4 G3 complex regions.** Methods fragment at `.planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md` must cross-reference the OSF DOI and this amendment. | Wave 5 documentation task |
| OS-registered state | None — no cron jobs, no systemd units. CI smoke test is a manual trigger via bash. | None |
| Secrets/env vars | `run_susie_rss.R:14-16` uses `SUSIE_MIN_LD_OVERLAP`, `SUSIE_MIN_LD_COVERAGE`, `SUSIE_MIN_LD_MIN_USE` env vars. These will be replaced by `config/susie_policy.yaml` entries. Any Snakemake rule, CI script, or shell session that sets these env vars must be audited — grep confirms none currently do. [VERIFIED: no grep hits for `SUSIE_MIN_LD` in `src/snakemake/` or `tests/` or `.planning/`] | Code edit only (replace env-var lookup with policy-YAML read); no runtime data migration |
| Build artifacts / installed packages | `envs/r_coloc.yml` with `r-coloc=5.2.3` resolves in `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/`. **Verification required** — Phase 0 closeout noted that smoke_dev is Python 3.11, but env yml is consumed by Snakemake's `--use-conda`, which creates its own env per rule. Check that `r_coloc.yml` and the new `ld_build.yml` resolve cleanly under Snakemake 7.32.4 during Phase 1 first real run. If they don't, the fix is env pinning, not script code. **Additionally:** existing `{FINEMAP_DIR}/susie/*.json` outputs from Phase 0 dry-runs must be deleted before the first real Phase 1 run — see Pitfall 4 and Wave 1 cache-clear task. | (1) Run `snakemake --use-conda --conda-create-envs-only` as the first sanity check in Phase 1. (2) Wave 1 includes explicit `rm -rf {FINEMAP_DIR}/susie/` task (or equivalent `--forceall run_finemap`) before any real execution. |

**Nothing found in:** live service config, OS-registered state (both verified by grep on `src/` and absence of any cron/systemd/pm2 patterns in repo).

## Common Pitfalls

### Pitfall 1: Mismatched class on fit object breaks coloc.susie dispatch
**What goes wrong:** `coloc.susie()` checks `class(dataset)` to decide whether to call `runsusie()` or treat the object as an already-fitted SuSiE result. `susieR::susie_rss()` returns an object with `class(fit) == "susie"` — but if the `saveRDS` / `readRDS` roundtrip loses the class attribute (rare but possible with old R versions), `coloc.susie` will re-fit from the dataset.
**Why it happens:** Careless use of `unclass()` or stripping attrs before save.
**How to avoid:** Unit-test the roundtrip: `fit2 <- readRDS(path); stopifnot(inherits(fit2, "susie"))`. **Wave 1 MUST include this test.**
**Warning signs:** `run_coloc_susie.R` is unexpectedly slow; identical pairwise results across different `.fit.rds` inputs.

### Pitfall 2: UKBB-LD tile boundaries do not align with curated region boundaries
**What goes wrong:** UKBB-LD tiles are 3Mb, genome-partitioned at fixed intervals. Curated region boundaries (e.g. FTO is 600kb) are hand-picked locus boundaries. Most curated regions fall inside a single tile — the extraction step must slice the tile's upper-triangle LD matrix by variant position.
**Why it happens:** Tile sources are pre-partitioned by an indexing scheme that doesn't know about curated region boundaries.
**How to avoid:** `download_ukbb_ld_tiles.py` must (a) download the tile NPZ and companion variant-index `.gz`, (b) filter variants to `[start, end]`, (c) slice the reconstructed LD matrix via `R_full[np.ix_(mask, mask)]`, (d) save as `.rds` keyed by curated region_id. See Pattern 5.
**Warning signs:** LD loader falls back to identity more often on EUR than on EAS after swap; dimensions don't match variant count in sumstats.

### Pitfall 3: HGDP+1kG sample IDs may differ between the phased BCF and the metadata table
**What goes wrong:** gnomAD's v3.1.2 harmonized HGDP+1kG release uses a specific sample ID convention; legacy 1000G sample IDs (e.g. `NA18486`) may appear in both HGDP metadata and 1000G metadata under different namespaces, and the harmonized BCF may prefix with `1KG_` or `HGDP_`.
**Why it happens:** Harmonization metadata convention is documented in the atgu/hgdp_tgp repo but is easy to miss.
**How to avoid:** `build_hgdp_1kg_ld.py` must (a) download the official metadata table, (b) filter to `genetic_region == 'AFR'` or equivalent (check exact column name), (c) use the exact ID format present in the BCF header via `bcftools query -l`, and (d) validate the final sample count matches the expected ~730.
**Warning signs:** plink2 `--keep` file produces zero samples; LD matrix is empty.

### Pitfall 4: Snakemake doesn't re-run old rules when adding new outputs
**What goes wrong:** Adding `.fit.rds` as a new output of `run_finemap` means existing JSON outputs on disk do NOT have a corresponding `.fit.rds`. Snakemake sees the JSON as up-to-date and refuses to re-run, leaving downstream `run_coloc_susie` permanently broken.
**Why it happens:** Snakemake tracks file mtimes, not rule versions.
**How to avoid:** **Wave 1 includes a mandatory clean-slate task** — either `rm -rf {FINEMAP_DIR}/susie/` or `snakemake --forceall run_finemap` before the first Phase 1 execution. Document in `filter_finemap_summary.py` that the cache MUST be cleared when fit-persistence is first enabled. This is NO LONGER a blocker (B-03 resolved by being baked into Wave 1).
**Warning signs:** `run_coloc_susie` complains about missing `.fit.rds` inputs despite `run_finemap` showing "up-to-date".

### Pitfall 5: susie_rss n_CS sensitivity sweep violates expected monotonicity for pathological regions
**What goes wrong:** The test "n_CS at min_abs_corr=0.1 ≥ n_CS at 0.5 ≥ n_CS at 0.9" is almost always true, but **can fail** when `susie_get_cs` rejects a CS at `macor=0.5` that was kept at `macor=0.1` because of a completely different purity calculation path. susieR 0.14.2 uses a unified purity check, so this should not happen — but it is possible under numerical edge cases.
**Why it happens:** Credible set purity is computed per-CS as min-abs-corr across pairs in the set; rare tied-purity CSs can flip rank.
**How to avoid:** The REQ-2 supplementary table should report monotonicity as a **soft expectation**, not a hard assertion. Flag non-monotonic rows in the QC dashboard as a diagnostic, not an error.
**Warning signs:** Any region where n_CS(0.9) > n_CS(0.5) — investigate with kriging_rss.

### Pitfall 6: Per-variant `SNP.PP.H4` from `coloc.susie` is conditional on H4
**What goes wrong:** `coloc.susie` returns a per-variant `SNP.PP.H4` column that is ONLY meaningful when the pairwise `PP.H4 > threshold`. Naively reporting it as "variant probability of colocalization" across all rows will mislead.
**Why it happens:** The per-variant PP is computed under the H4 prior — if H4 has low posterior support, it's nonsense.
**How to avoid:** Downstream tools must filter `susie_pairs` to `PP.H4 > 0.5` (or the planned Phase 2 threshold) before using per-variant PPs. Document this in `run_coloc_susie.R` comments and the methods fragment. [CITED: coloc vignette a06_SuSiE + coloc.susie help page]
**Warning signs:** The coloc_top_hits_table includes "high confidence" variants from pairs where overall PP.H4 is near zero.

### Pitfall 7: Quarto rendering of large tables blows Snakemake job memory
**What goes wrong:** The dashboard aggregates per-region QC across all trait × ancestry × region combinations. For 12 regions (8 + 4 complex) × 5 ancestries × 5 traits × 3 `macor` sweep values, that's ~900 rows — small. But scaled to a full run with many regions it could be thousands.
**Why it happens:** Quarto + DT/reactable JS loads all rows into browser.
**How to avoid:** Set `DT::datatable(..., options = list(pageLength = 50, deferRender = TRUE))`. For Phase 1 with 12 curated regions, this is a non-issue, but flag for Phase 2.
**Warning signs:** Dashboard HTML file > 50MB.

### Pitfall 8: kriging_rss returns a ggplot in the list — serializing to JSON will crash
**What goes wrong:** `kriging_rss()` returns `list(plot=<gg>, conc=<data.frame>)`. Writing the whole list via `jsonlite::toJSON` will fail on the ggplot object.
**How to avoid:** In `run_susie_rss.R`, extract only the `conc` (concordance table) or aggregate statistics (e.g. n_outliers where `logLR > 2`), never the ggplot object.

### Pitfall 9: HLA region (~10 Mb) spans multiple UKBB-LD tiles with no cross-tile LD available
**What goes wrong:** `HLA_6p21` (chr6:25000000-35000000) is 10 Mb wide — it spans 3-4 consecutive UKBB-LD tiles. UKBB-LD tiles are computed independently per 3Mb window; cross-tile off-diagonal LD blocks are NOT provided by the dataset. The true HLA LD matrix has substantial long-range LD that the block-diagonal approximation misses.
**Why it happens:** Tile-partitioned datasets trade cross-tile fidelity for storage tractability.
**How to avoid:** For HLA specifically, the block-diagonal approximation is the only tractable option in Phase 1. Flag it explicitly in the output `.rds` metadata as `ld_source = "ukbb_ld_tiled_block_diagonal"` and note in the methods fragment that HLA fine-mapping CS purity will be optimistic due to suppressed cross-block correlations. Phase 2 can upgrade to Pan-UKBB raw BlockMatrix (which does provide cross-position LD across arbitrary windows) if HLA results are scientifically important.
**Warning signs:** HLA fine-mapping produces surprisingly many clean CSs compared to non-tiled LD — signal of missing off-diagonal correlations.

## Code Examples

### Example 1: run_susie_rss.R modification (additive fit persistence)
```r
# Source: verified susieR 0.14.2 API + coloc 5.2.3 dispatch
# Modify run_susie_rss.R after line 409 (after `fit <- tryCatch(...)`)
if (!is.null(fit)) {
  # Ensure class is set for coloc.susie dispatch
  if (!inherits(fit, "susie")) class(fit) <- c("susie", class(fit))
  fit_rds_path <- sub("\\.json$", ".fit.rds", opt$output)
  dir.create(dirname(fit_rds_path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(fit, file = fit_rds_path)
}

# Post-hoc sweep (free, no refit)
sweep_rows <- list()
for (macor in MIN_ABS_CORR_SWEEP) {
  cs_m <- susie_get_cs(fit, Xcorr = NULL, coverage = COVERAGE, min_abs_corr = macor)
  sweep_rows[[as.character(macor)]] <- list(
    min_abs_corr = macor,
    n_CS = length(cs_m$cs %||% list()),
    cs_sizes = sapply(cs_m$cs %||% list(), length),
    cs_pip_sum = sapply(cs_m$cs %||% list(), function(idx) sum(fit$pip[idx])),
    cs_purity = sapply(cs_m$cs %||% list(), function(idx) {
      if (length(idx) < 2) return(1.0)
      submat <- R[idx, idx, drop=FALSE]
      min(abs(submat[upper.tri(submat)]))
    })
  )
}
# Attach to result list before writing JSON
result$min_abs_corr_sweep <- sweep_rows
result$L_used <- fit$L %||% L_DEFAULT
result$L_saturated <- length(cs$cs %||% list()) >= L_DEFAULT
result$converged <- isTRUE(fit$converged)
result$niter <- fit$niter %||% NA
result$elbo_final <- if (!is.null(fit$elbo)) tail(fit$elbo, 1) else NA
```

### Example 2: kriging_rss QC integration
```r
# Source: susieR docs — "Diagnostic for fine-mapping with summary statistics" vignette
krig <- tryCatch(
  susieR::kriging_rss(z = subset$z, R = R, n = mean_n),
  error = function(e) NULL
)
if (!is.null(krig)) {
  # Never serialize the plot — only the concordance table
  conc <- krig$conc
  n_outliers <- sum(conc$logLR > 2 & abs(conc$z) > 2, na.rm = TRUE)
  result$kriging_rss <- list(
    n_outliers = n_outliers,
    max_logLR = max(conc$logLR, na.rm = TRUE),
    lambda = krig$lambda %||% NA
  )
}
```

### Example 3: run_coloc_susie.R skeleton
```r
#!/usr/bin/env Rscript
# Source: coloc 5.2.3 API docs + legacy run_coloc.R output schema
suppressPackageStartupMessages({
  library(optparse); library(coloc); library(susieR); library(jsonlite); library(data.table)
})

option_list <- list(
  make_option("--fit-a", dest="fit_a", type="character"),
  make_option("--fit-b", dest="fit_b", type="character"),
  make_option("--policy", type="character"),
  make_option("--pair-id", dest="pair_id", type="character"),
  make_option("--manifest", type="character"),   # to recover trait/ancestry/region
  make_option("--output", type="character")
)
opt <- parse_args(OptionParser(option_list=option_list))

fit_a <- readRDS(opt$fit_a)
fit_b <- readRDS(opt$fit_b)
stopifnot(inherits(fit_a, "susie"), inherits(fit_b, "susie"))

# Guard against empty CS fits
n_cs_a <- length(fit_a$sets$cs %||% list())
n_cs_b <- length(fit_b$sets$cs %||% list())
if (n_cs_a == 0 || n_cs_b == 0) {
  # Emit empty-result JSON matching legacy schema
  empty <- list(
    status = "no_signal",
    n_cs_a = n_cs_a, n_cs_b = n_cs_b,
    summary = list(PP.H0.abf=NA, PP.H1.abf=NA, PP.H2.abf=NA, PP.H3.abf=NA, PP.H4.abf=NA),
    susie_pairs = list()
  )
  write_json(empty, opt$output, auto_unbox=TRUE, pretty=TRUE)
  quit(status=0)
}

res <- coloc::coloc.susie(fit_a, fit_b)
# res$summary is data.table with columns: idx1, idx2, nsnps, hit1, hit2,
#   PP.H0.abf, PP.H1.abf, PP.H2.abf, PP.H3.abf, PP.H4.abf
# res$results has per-SNP SNP.PP.H4 conditional on H4

# Legacy compat: emit best pairwise as top-level summary + full pairs list
best_row <- res$summary[which.max(res$summary$PP.H4.abf), ]
output <- list(
  pair_id = opt$pair_id,
  status = "success",
  summary = as.list(best_row),          # best pairwise matches legacy field shape
  susie_pairs = as.list(res$summary),   # all pairwise (new field for Phase 2 consumers)
  n_pairs_total = nrow(res$summary),
  n_cs_a = n_cs_a,
  n_cs_b = n_cs_b
)
write_json(output, opt$output, auto_unbox=TRUE, pretty=TRUE)
```

### Example 4: UKBB-LD tile download and per-region extraction (Python)
```python
# Source: UKBB-LD README (Weissbrod 2020) + AWS Open Data Registry + boto3 anonymous access
# Bucket: s3://broad-alkesgroup-ukbb-ld/UKBB_LD/  (also reachable via https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/)
# Tile naming: chr{N}_{start}_{end}.npz + chr{N}_{start}_{end}.gz (variant list TSV)

import boto3
from botocore import UNSIGNED
from botocore.client import Config
import numpy as np
import pandas as pd
import pyreadr  # OR write to npz and use an R helper for .rds conversion

BUCKET = "broad-alkesgroup-ukbb-ld"
PREFIX = "UKBB_LD/"

# Anonymous client — UKBB-LD is a public Open Data Registry bucket
s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

def list_tiles(chrom):
    """List all tile NPZ files for a chromosome."""
    paginator = s3.get_paginator("list_objects_v2")
    tiles = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=f"{PREFIX}chr{chrom}_"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".npz"):
                # Parse chr{N}_{start}_{end}.npz
                parts = key.removeprefix(PREFIX).removesuffix(".npz").split("_")
                start = int(parts[1]); end = int(parts[2])
                tiles.append((start, end, key))
    return sorted(tiles)

def tiles_for_region(chrom, region_start, region_end):
    return [(s, e, k) for s, e, k in list_tiles(chrom)
            if e >= region_start and s <= region_end]

def download_tile(key, local_path):
    s3.download_file(BUCKET, key, local_path)

def extract_region(chrom, region_start, region_end, region_id):
    overlapping = tiles_for_region(chrom, region_start, region_end)
    if len(overlapping) == 1:
        tile_start, tile_end, key = overlapping[0]
        npz_path = f"/rs1/scratch/ukbb_ld/{key.split('/')[-1]}"
        var_path = npz_path.replace(".npz", ".gz")
        download_tile(key, npz_path)
        download_tile(key.replace(".npz", ".gz"), var_path)

        arr = np.load(npz_path)
        # UKBB-LD stores upper-triangle as flat array; reconstruct symmetric matrix
        R_full = reconstruct_symmetric(arr)
        variants = pd.read_csv(var_path, sep="\t")
        mask = (variants["position"] >= region_start) & (variants["position"] <= region_end)
        idx = mask.values
        R_region = R_full[np.ix_(idx, idx)]
        variants_region = variants[mask].reset_index(drop=True)

        # Write .rds via R subprocess or pyreadr
        save_rds(R_region, variants_region, f"{LD_REF_DIR}/EUR/{region_id}.rds",
                 ld_source="ukbb_ld_tiled")
    else:
        # Multi-tile: block-diagonal concatenation; flag as approximation
        blocks_R = []
        blocks_v = []
        for tile_start, tile_end, key in overlapping:
            # ... download + reconstruct + slice to region bounds ...
            blocks_R.append(R_tile_sliced)
            blocks_v.append(variants_tile_sliced)
        from scipy.linalg import block_diag
        R_bd = block_diag(*blocks_R)
        variants_all = pd.concat(blocks_v).reset_index(drop=True)
        save_rds(R_bd, variants_all, f"{LD_REF_DIR}/EUR/{region_id}.rds",
                 ld_source="ukbb_ld_tiled_block_diagonal")  # FLAG for HLA

def reconstruct_symmetric(npz_archive):
    """UKBB-LD stores upper-triangle as a compressed sparse array.
    The exact key names depend on the release — check README. Typical:
      - 'R': dense upper-triangle row-major
      - 'snplist': variant IDs
    Reconstruct full symmetric R from upper triangle.
    """
    # Implementation depends on exact NPZ schema — verify in Wave 0 preflight by loading one tile.
    R_upper = npz_archive["R"]
    n = int(np.sqrt(2 * len(R_upper)))
    R = np.zeros((n, n), dtype=np.float32)
    # Fill upper triangle, then mirror
    iu = np.triu_indices(n)
    R[iu] = R_upper
    R = R + R.T - np.diag(np.diag(R))
    return R
```

**Note on NPZ schema:** The exact internal keys of UKBB-LD NPZ files (e.g., `"R"`, `"snplist"`, or a scipy-sparse `.npz` layout) should be verified in Wave 0 preflight by downloading one small tile (e.g. chr22) and inspecting `np.load(...).files`. The reconstruction routine is adjusted once to match the actual schema; all downstream region extraction reuses it.

### Example 5: HGDP+1kG AFR LD from phased BCFs (plink2)
```bash
# Source: atgu/hgdp_tgp README + standard plink2 workflow
# Metadata: https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/pca/gnomad.v3.1.2.hgdp_tgp_meta.tsv
# Phased haplotypes: https://storage.googleapis.com/gcp-public-data--gnomad/resources/hgdp_1kg/phased_haplotypes_v2/
# Anonymous HTTPS — no gsutil/gcloud needed

# 1. Download metadata + extract AFR sample list
curl -sL "https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/pca/gnomad.v3.1.2.hgdp_tgp_meta.tsv" -o meta.tsv
# Column names verified from first row; filter to AFR
awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)col[$i]=i; print "s"} NR>1 && $col["genetic_region"]=="AFR" {print $col["s"]}' meta.tsv > afr_samples.txt

# 2. Per-chromosome, per-region LD (downloads only the region of interest via bcftools tabix)
for region in "${CURATED_REGIONS[@]}"; do
  CHR=$(echo $region | cut -d: -f1)
  START=$(echo $region | cut -d: -f2)
  END=$(echo $region | cut -d: -f3)
  REGION_ID=$(echo $region | cut -d: -f4)

  # Option A: stream BCF slice via HTTPS (bcftools supports https:// input with tabix index)
  BCF_URL="https://storage.googleapis.com/gcp-public-data--gnomad/resources/hgdp_1kg/phased_haplotypes_v2/hgdp1kgp_chr${CHR}.bcf"
  bcftools view -S afr_samples.txt -r ${CHR}:${START}-${END} --min-af 0.01 "$BCF_URL" -Ob -o slice_${REGION_ID}.bcf

  plink2 --bcf slice_${REGION_ID}.bcf \
         --r-phased square \
         --out ld_afr_${REGION_ID}

  # Convert .ld (plink text matrix) → .rds via small R helper
  Rscript src/snakemake/scripts/plink_ld_to_rds.R \
    --ld ld_afr_${REGION_ID}.ld \
    --variants ld_afr_${REGION_ID}.pvar \
    --region-id $REGION_ID --ancestry AFR \
    --output {LD_REF_DIR}/AFR/${REGION_ID}.rds
done
```

### Example 6: Policy YAML schema (schemas/susie_policy.schema.yaml)
```yaml
# Source: Phase 0 D-06 pattern — JSON Schema for YAML validation
$schema: "http://json-schema.org/draft-07/schema#"
type: object
required: [susie, complex_regions]
properties:
  susie:
    type: object
    required: [L, coverage, max_iter_primary, max_iter_retry, min_abs_corr_sweep]
    properties:
      L: {type: integer, minimum: 1, maximum: 50}
      coverage: {type: number, minimum: 0.5, maximum: 1.0}
      max_iter_primary: {type: integer, minimum: 10}
      max_iter_retry: {type: integer, minimum: 10}
      ld_regularization_eps: {type: number, minimum: 0}
      min_abs_corr_default: {type: number, minimum: 0, maximum: 1}
      min_abs_corr_sweep:
        type: array
        minItems: 3
        items: {type: number, minimum: 0, maximum: 1}
      l_saturation:
        type: object
        properties:
          action: {enum: [flag, refit, error]}
          supplementary_rerun_L: {type: integer}
      convergence_failure:
        type: object
        properties:
          action: {enum: [retry_ladder, exclude, error]}
          ladder: {type: array, items: {type: string}}
  complex_regions:
    type: object
    required: [pre_specified, data_flagged]
    properties:
      pre_specified:
        type: array
        minItems: 4
        maxItems: 4   # Phase 1 locked: 9p21, APOE, HLA, SLC2A9
        items:
          type: object
          required: [region_id, chr, start, end, rationale]
      data_flagged:
        type: object
        properties:
          triggers: {type: array, items: {type: string}}
```

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| `coloc.abf()` single-variant assumption | `coloc.susie()` multi-signal | coloc 5.0 (2021), matured through 5.2 | Correctly handles multi-causal-variant regions; REQ-2 directly relies on this |
| Manual 2-retry LD fallback (primary → regularized → identity) | Structured 3-step retry ladder with explicit `non_converged` terminal state (G2c) | CONTEXT.md 2026-04-11 | Regions that fail convergence are surfaced as a distinct category, not silently masked as identity-LD |
| Single `min_abs_corr` threshold | Post-hoc sweep at {0.1, 0.5, 0.9} via `susie_get_cs()` | CONTEXT.md G2b | Sensitivity diagnostic without compute cost |
| LD panel from 1000G only | Hybrid: UKBB-LD (Weissbrod 2020) tiled EUR + HGDP+1kG AFR + 1000G rest | CONTEXT.md G4 + B-01 resolution (2026-04-11) | Ancestry-matched LD where available (EUR/AFR); smaller panels documented as caveats (AMR); tiled EUR chosen over 14.1 TB Pan-UKBB raw for operational tractability |
| 8 curated regions | 8 + 4 G3_complex regions (12 total) | B-02 resolution (2026-04-11) | Complex-region sensitivity sweep has actual pre-specified anchors; 9p21, APOE, HLA, SLC2A9 intersect current trait set (t2d/htn/stroke/asthma). LPA and chr8 inversion deferred to Phase 2 pending lipid/allergic-disease sumstats |

**Deprecated / outdated:**
- `src/legacy/region_analysis/scripts/run_coloc.R` — per CONTEXT.md, rename to `run_coloc_abf_legacy.R` and remove from active Snakefile imports. Critical: `src/snakemake/rules/multitrait.smk:134` must be updated.
- `src/legacy/genome_wide/scripts/run_coloc_genomewide.R` and `run_coloc.R` — already dormant (only wired to historical bash submit scripts). Do NOT touch in Phase 1 — out of scope.
- `stroke_afr_susie_sweep` placeholder rule (finemap.smk:98-111) — replace with the real sweep (post-hoc `susie_get_cs` is invoked inside `run_finemap` now, so the separate sweep rule is unnecessary).

## Assumptions Log

> All blocker-tier assumptions from the initial research pass have been RESOLVED via user decisions. Remaining `[ASSUMED]` items are empirical unknowns to be verified in Wave 0 preflight or Wave 2 first real execution.

| # | Claim | Section | Status | Risk if wrong |
|---|-------|---------|--------|---------------|
| A1 | Splitting LD-build heavy deps into a new `envs/ld_build.yml` rather than extending `python_stats.yml` | Standard Stack | [DISCRETION] planner may choose | Low |
| A2 | ~~Hail is installable on smoke_dev~~ | — | **DROPPED** (UKBB-LD path does not need Hail per B-01 resolution) | — |
| A3 | UKBB-LD NPZ files store upper-triangle as `npz['R']` and variants as companion `.gz` TSV | Code Example 4 | [ASSUMED — verify in Wave 0 preflight] | Low — the reconstruction routine adjusts once; Wave 0 downloads one tile to verify |
| A4 | HGDP+1kG AFR sample count is ~730 post-merge | CONTEXT.md G4 | [ASSUMED] | Low — verifiable once metadata table is downloaded; worst case affects methodology caveats only |
| A5 | plink2 `--r-phased` with `--keep afr_samples.txt` produces LD matrices compatible with `run_susie_rss.R`'s `.rds` loader | Code Example 5 | [ASSUMED] | Low — a small R helper bridges the format; the Phase 0 `build_ld_rds.py` already does this for 1000G |
| A6 | `coloc::coloc.susie` accepts `susieR::susie_rss` output directly after roundtrip via `saveRDS`/`readRDS` | Pattern 1 / Pitfall 1 | **[WAVE 1 UNIT TEST]** — test-then-branch in Wave 1, no user decision needed | Low — fallback to `coloc::runsusie()` is a one-line change |
| A7 | ~~The 8 curated regions in `config/regions_curated.csv` match the G3 complex regions~~ | — | **RESOLVED** by B-02: 4 new `G3_complex` rows added (9p21, APOE, HLA, SLC2A9); LPA + chr8 inversion deferred to Phase 2 | — |
| A8 | `rmarkdown::render()` with the Quarto renderer is a sufficient fallback to `quarto render` if `quarto-cli` install fails | Standard Stack / Alternatives | [ASSUMED] | Low — both work for static HTML |
| A9 | ~~The Weissbrod 2020 "UKBB-LD" tiled dataset on AWS registry is an acceptable alternative to Pan-UKBB raw BlockMatrix for EUR LD~~ | — | **PROMOTED TO LOCKED DECISION G6** by B-01 resolution; substitution documented in methods fragment and OSF amendment | — |
| A10 | gnomAD v3.1.2 HGDP+1kG phased haplotypes are per-chromosome BCFs at `https://storage.googleapis.com/gcp-public-data--gnomad/resources/hgdp_1kg/phased_haplotypes_v2/` | Code Example 5 | [ASSUMED — verify in Wave 0 preflight by HEAD-requesting chr22 BCF] | Low |
| A11 | The planner will use distinct `{LD_REF_DIR}/EUR_ukbb_ld/` and `{LD_REF_DIR}/AFR_hgdp_1kg/` subdirectories (for auditability) | Runtime State Inventory | [DISCRETION] | Low |
| A12 | UKBB-LD tile-to-region mapping: most curated regions fall inside a single 3Mb tile; only HLA (10 Mb) spans 3-4 tiles and requires block-diagonal concatenation | Pattern 5 / Pitfall 9 | [ASSUMED] | Medium — if a curated region unexpectedly crosses a tile boundary (e.g., region exactly at 3000000 offset), flag and use block-diagonal. Wave 0 preflight can compute the intersection from the bucket listing. |

## Open Questions

*(No remaining blockers. Items below are empirical unknowns resolvable by preflight or first real run.)*

1. **Exact UKBB-LD NPZ internal schema** — resolved by Wave 0 preflight (download one tile, inspect `np.load(...).files`).
2. **HGDP+1kG AFR sample count and BCF per-chromosome size** — resolved by Wave 0 preflight (download `meta.tsv` + HEAD chr22 BCF).
3. **`runsusie()` vs `susie_rss()` dispatch class** — resolved by Wave 1 unit test; fallback branch planned.

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `r-coloc` | coloc.susie | ✓ pinned | 5.2.3 | — |
| `r-susieR` | susie_rss, kriging_rss, susie_get_cs | ✓ pinned | 0.14.2 | — |
| `r-yaml` | policy loader | ✓ pinned | 2.3.10 | — |
| `snakemake` | DAG execution | ✓ pinned | 7.32.4 (smoke_dev) | — |
| `quarto-cli` | D6 dashboard | ✗ | — | `rmarkdown::render()` fallback (static HTML) |
| `numpy` + `scipy` + `boto3` + `pandas` | UKBB-LD tile download + extraction | ✗ (new `envs/ld_build.yml`) | 1.26 / 1.13 / 1.34 / 2.2 | — (standard conda-forge packages, no known alternative) |
| `plink2` | HGDP+1kG AFR LD build | ✓ (envs/plink.yml exists) | check pinned version | — |
| `bcftools` | BCF sample queries + HTTPS BCF slicing | ✓ expected in plink2 env, confirm in Wave 0 | 1.21 | install via conda-forge if missing |
| Anonymous HTTPS via `requests` or `curl` | Public-bucket downloads (UKBB-LD via `https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/`, gnomAD via `https://storage.googleapis.com/gcp-public-data--gnomad/`) | ✓ (curl is standard; `requests` included in `envs/ld_build.yml`) | — | — |
| `aws cli` | — | — | — | **NOT NEEDED** — boto3 anonymous client (`UNSIGNED` config) handles UKBB-LD |
| `gsutil` / `gcloud` | — | — | — | **NOT NEEDED** — `curl` / `requests` / `bcftools` handle HTTPS public-bucket reads |
| `hail` / Java | — | — | — | **NOT NEEDED** — dropped per B-01 resolution |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:**
- Quarto → R Markdown (acceptable for D6)

**Wave 0 preflight verification commands (read-only):**
```bash
# 1. UKBB-LD bucket reachability via anonymous HTTPS
curl -sI "https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/" | head -3
# Expected: HTTP 200 or listing-style response

# 2. Download ONE small UKBB-LD tile to verify NPZ schema
aws s3 cp --no-sign-request s3://broad-alkesgroup-ukbb-ld/UKBB_LD/chr22_16000000_19000000.npz /tmp/test_tile.npz 2>/dev/null \
  || curl -sL "https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/chr22_16000000_19000000.npz" -o /tmp/test_tile.npz
python -c "import numpy as np; a = np.load('/tmp/test_tile.npz'); print('Keys:', list(a.files)); print({k: a[k].shape for k in a.files})"

# 3. gnomAD HGDP+1kG metadata reachability
curl -sI "https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/pca/gnomad.v3.1.2.hgdp_tgp_meta.tsv" | head -3

# 4. gnomAD HGDP+1kG chr22 phased BCF HEAD
curl -sI "https://storage.googleapis.com/gcp-public-data--gnomad/resources/hgdp_1kg/phased_haplotypes_v2/hgdp1kgp_chr22.bcf" | head -3

# 5. /rs1 scratch budget check
df -h /rs1 | tail -1

# 6. coloc/susieR pinned versions
conda run -n r_coloc Rscript -e '
  packageVersion("coloc")
  packageVersion("susieR")
  packageVersion("yaml")
  inherits(susieR::susie_rss(z=c(1,2,3), R=diag(3), n=1000), "susie")
'
```

## Validation Architecture

**Nyquist enforcement:** `.planning/config.json` does NOT set `workflow.nyquist_validation: false` (it is explicitly `true`). This section is mandatory.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (Python) for Snakemake rule/DAG tests + `testthat` (R) for R-script unit tests + `snakemake --dry-run` for DAG integrity |
| Config file | `tests/toy_3locus/config_test.yaml` (already exists from Phase 0) |
| Quick run command | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda --dry-run` |
| Full suite command | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` |
| Phase 1 addition | `pytest tests/phase1/ -x` for new pytest modules + `Rscript -e 'testthat::test_dir("tests/testthat-phase1/")'` for R unit tests |

### Phase requirements → test map

| REQ / Success Criterion | Behavior | Test type | Automated command | File exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-2 acceptance #1 (policy exists) | `config/susie_policy.yaml` exists and validates against schema | integration | `snakemake --dry-run --config policy=config/susie_policy.yaml` (includes schema validation in Snakefile preamble) | ❌ Wave 1 creates |
| REQ-2 acceptance #2 (policy loaded by finemap.smk) | finemap.smk references the policy file; `run_susie_rss.R` reads it | unit | `grep -q "susie_policy.yaml" src/snakemake/rules/finemap.smk && grep -q "yaml::read_yaml" src/legacy/region_analysis/scripts/run_susie_rss.R` | ❌ Wave 1 adds |
| REQ-2 acceptance #3 (min_abs_corr sweep ≥3 values) | `run_susie_rss.R` output JSON has `min_abs_corr_sweep` key with exactly 3 rows | unit | `pytest tests/phase1/test_susie_sweep.py::test_three_sweep_values -x` | ❌ Wave 1 |
| REQ-2 implicit: sweep monotonicity | `n_CS(macor=0.1) >= n_CS(0.5) >= n_CS(0.9)` on toy data (property, not hard assert — flag violations) | property | `pytest tests/phase1/test_susie_sweep.py::test_monotonic_or_flag -x` | ❌ Wave 1 |
| **Wave 1 A6 resolution test (NEW)** | `coloc::coloc.susie(readRDS(fit_a), readRDS(fit_b))` runs without warning and without silent refit | unit | `Rscript -e 'testthat::test_file("tests/testthat-phase1/test_coloc_susie_dispatch.R")'` — fits toy susie_rss, saves, loads, calls coloc.susie, checks for warnings + class dispatch. **If test fails, switch `run_susie_rss.R` to call `coloc::runsusie()` instead** (one-line script change; both branches spec'd in 01-01-PLAN.md). | ❌ Wave 1 creates |
| **Wave 1 cache-clear precondition (NEW)** | Before first Wave 1 real execution, `{FINEMAP_DIR}/susie/` is empty or removed | manual | `rm -rf {FINEMAP_DIR}/susie/` as Wave 1 Task 0 (documented in `filter_finemap_summary.py` header comment) | Wave 1 Task 0 |
| Success criterion #1 (SuSiE completes for all trait × ancestry) | Run full smoke DAG to completion | integration | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` (exit 0) | ⚠ Wave 5 (first REAL run — Phase 0 only did dry-run) |
| Success criterion #4 (coloc.susie replaces coloc.abf, no coloc.abf remains) | No active Snakemake rule invokes coloc.abf | unit | `grep -rn "coloc\\.abf" src/snakemake/ src/legacy/region_analysis/scripts/run_coloc_abf_legacy.R` expects match only in the renamed legacy file, not in src/snakemake/ | ❌ Wave 3 |
| Success criterion #5 (QC report generated) | `results/finemap/qc_dashboard.html` exists and contains D1/D2/D3/D4 columns | integration | `pytest tests/phase1/test_qc_dashboard.py::test_dashboard_exists_has_columns -x` | ❌ Wave 4 |
| Convergence retry ladder behavior | On a synthetic pathological z-score input, retry ladder transitions through max_iter → regularize → non_converged | property | `Rscript -e 'testthat::test_file("tests/testthat-phase1/test_retry_ladder.R")'` | ❌ Wave 1 |
| `coloc.susie` dispatch on saved fit | `readRDS(fit_rds)` object passes `inherits(x, "susie")` and `coloc.susie(fit1, fit2)` runs without warning | unit | `Rscript -e 'testthat::test_file("tests/testthat-phase1/test_fit_roundtrip.R")'` | ❌ Wave 1 |
| Legacy compat schema | `run_coloc_susie.R` output JSON parses cleanly in `augment_coloc_summary.py` | integration | `pytest tests/phase1/test_coloc_susie_compat.py -x` | ❌ Wave 3 |
| UKBB-LD / HGDP+1kG LD writes to expected path | After `download_ukbb_ld_tiles` + `build_hgdp_1kg_ld` rules complete, `{LD_REF_DIR}/EUR_ukbb_ld/{region}.rds` (or `EUR/`) and `{LD_REF_DIR}/AFR_hgdp_1kg/{region}.rds` (or `AFR/`) exist | integration | `pytest tests/phase1/test_ld_panels.py -x` — runs only when `--ld-build` flag present | ❌ Wave 2 |
| UKBB-LD HLA block-diagonal flag | HLA_6p21 `.rds` metadata includes `ld_source = "ukbb_ld_tiled_block_diagonal"` | unit | `pytest tests/phase1/test_ld_hla_flag.py -x` | ❌ Wave 2 |
| Manual UAT #11 (monotonicity spot-check on HLA or APOE) | Visual confirmation in dashboard | manual | `open results/finemap/qc_dashboard.html` + visual check | ⚠ Wave 5 manual |
| Manual UAT #12 (EUR/AFR use new LD panels) | `ld_source` field in JSON contains `ukbb_ld_tiled` or `hgdp_1kg` | unit | `pytest tests/phase1/test_ld_source_field.py -x` | ❌ Wave 2 |

### Validation dimensions for a statistical genomics pipeline replacement

1. **Schema compatibility** — new output JSON must parse in existing consumers (Pattern 6).
2. **DAG integrity** — `snakemake --dry-run` resolves all dependencies, no orphaned rules.
3. **Version dispatch** — `inherits(fit, "susie")` roundtrip; `coloc.susie` does not silently re-fit. **Wave 1 test + fallback to `runsusie()`.**
4. **Statistical invariants** — monotonicity of `n_CS` under `min_abs_corr` sweep; SuSiE `converged` flag true on well-conditioned toy data.
5. **LD quality invariants** — `kriging_rss` outlier count is small (< 5% of variants) on well-matched LD; large on deliberately mismatched LD. Unit test by pairing 1000G EUR LD with UKBB-LD EUR sumstats (expect very few outliers — both are EUR) vs pairing AFR LD with EUR sumstats (expect many).
6. **Complex-region handling** — for the 4 pre-specified complex regions (9p21, APOE, HLA, SLC2A9), `data_flagged` triggers OR `L_saturated` flag OR `n_CS ≥ 3` fires; regions outside the complex list do NOT fire on the toy dataset.
7. **End-to-end smoke** — `tests/toy_3locus/config_test.yaml` runs all new Phase 1 rules in under 15 minutes (REQ-9) against the 3 curated loci × EUR × 3 traits. First REAL execution unblocks here.

### Property-based / invariant tests

| Invariant | Test |
|-----------|------|
| `n_CS(0.1) ≥ n_CS(0.5) ≥ n_CS(0.9)` (soft — flag, don't fail) | `test_monotonic_or_flag` |
| `fit$L == L_DEFAULT` in policy | `test_L_matches_policy` |
| `L_saturated == TRUE` iff `length(fit$sets$cs) == L_DEFAULT` | `test_L_saturation_flag_correct` |
| `inherits(readRDS(fit_rds), "susie") == TRUE` | `test_fit_roundtrip_class` |
| `coloc.susie(readRDS(a), readRDS(b))` runs without warnings | `test_coloc_susie_dispatch` |
| For each row in coloc.susie output: `sum(PP.H0..PP.H4) ≈ 1.0 ± 1e-6` | `test_coloc_susie_posterior_sum` |
| `ld_source` field not "identity" for any region that has valid panel coverage | `test_no_silent_identity_fallback` |
| HLA region has `ld_source == "ukbb_ld_tiled_block_diagonal"` (expected flag) | `test_ld_hla_flag` |

### Convergence retry ladder test strategy

Pathological data is hard to fabricate without introducing bias. Proposed strategy:
- **Primary ladder tests** use a synthetic small region (100 variants) with LD set to a near-singular matrix (eigenvalues close to zero) — forces `susie_rss` to hit `max_iter=100` without converging.
- **Verify step 1 → step 2 transition** by asserting `status == "converged_max_iter"` when running with `max_iterations=200` succeeds.
- **Verify step 2 → step 3 transition** by making the matrix actually singular (rank-deficient); regularization with `eps=1e-4` should restore convergence.
- **Verify step 3 → non_converged** by using a truly pathological input (randomly permuted z vector against a well-conditioned LD) where no amount of regularization helps. `status` should become `"non_converged"`; the `fit` object is still returned so downstream logic can decide.

### Smoke-test-friendly dataset

Phase 0 already built `tests/toy_3locus/` with FTO (chr16), MC4R (chr18), SH2B3 (chr12) × EUR × {bmi, t2d, hypertension}. This dataset is appropriate for the Phase 1 smoke test:
- All 3 loci are well-behaved (no HLA / APOE complexity)
- Genotype data fits comfortably in < 2 GB total
- Expected runtime < 15 minutes per REQ-9

**Limitation:** The smoke dataset does NOT exercise the complex-region code path. A `tests/phase1/` addition should include a single synthetic "HLA-like" region with > 5,000 variants and multiple signals to exercise L-saturation detection. This can be generated deterministically from a seed.

### Sampling rate

- **Per task commit (Wave-internal):** `snakemake --dry-run` + relevant pytest/testthat targets (< 30s)
- **Per wave merge:** Full smoke DAG dry-run + all new unit tests (< 3 min)
- **Phase gate (before `/gsd-verify-work`):** Full smoke REAL run on toy dataset (< 15 min per REQ-9)

### Wave 0 gaps

- [ ] `tests/phase1/` directory — pytest test modules (new, does not exist)
- [ ] `tests/testthat-phase1/` directory — R unit tests (new)
- [ ] `tests/phase1/fixtures/synthetic_pathological.rds` — synthetic LD + z-score for retry ladder testing
- [ ] `tests/phase1/fixtures/mini_susie_fit.rds` — pre-computed small `susie_rss` fit for fast unit tests
- [ ] `envs/qc_dashboard.yml` — new env for Quarto rendering (if chosen over RMarkdown)
- [ ] `envs/ld_build.yml` — new env for UKBB-LD NPZ extraction + HGDP+1kG plink2 (lightweight: numpy/scipy/boto3/pandas/r-base/bcftools/plink2, no Hail)
- [ ] `schemas/susie_policy.schema.yaml` — new schema for policy validation
- [ ] `config/susie_policy.yaml` — the policy file itself (REQ-2 deliverable #1)
- [ ] `config/regions_curated.csv` — **append 4 new G3_complex rows** (9p21_CDKN2A, APOE_19q13, HLA_6p21, SLC2A9_urate)

## Security Domain

Phase 1 does not introduce new secrets, no auth flows, no user input surfaces. Public data only (UKBB-LD CC-BY / AWS Open Data, gnomAD public). No network-facing services. The only external I/O is anonymous HTTPS/S3 reads.

Per `.planning/phases/00-data-access-infrastructure/00-SECURITY.md`, the threat model for this project is 10/10 SECURED with 3 accepted risks (all in Phase 0 scope). Phase 1 inherits that posture.

| ASVS category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | Schema-validate `config/susie_policy.yaml` via `schemas/susie_policy.schema.yaml` in Snakefile preamble; `optparse` arg validation in R scripts; `jsonschema` validation in new Python scripts |
| V6 Cryptography | no | — |
| V7 Error Handling | yes | Structured retry ladder with explicit `non_converged` terminal state (don't silently suppress failures); non-fit-object error paths emit status JSON, never crash silently |
| V10 Malicious Code | yes | UKBB-LD, Pan-UKBB, gnomAD are public buckets with anonymous HTTPS. No credentials stored. Verify checksums where the source provides them. |
| V12 File & Resources | yes | Absolute paths only in Snakemake rules (Phase 0 REQ-12 compliance); downloads target `/rs1` scratch, not repo; LD matrix file ownership stays on GPFS |

**Threat patterns for this stack:**

| Pattern | STRIDE | Standard mitigation |
|---------|--------|---------------------|
| Unvalidated YAML policy file (could inject arbitrary code via deserialization) | Tampering | `yaml::read_yaml` in R uses safe mode by default; JSON Schema validation on load |
| Unsigned downloads from public buckets | Tampering | Verify SHA256 checksums where the source publishes them (gnomAD does; UKBB-LD partial) |
| Identity LD fallback masking data quality issues | Info Disclosure (wrong results in manuscript) | Retry ladder removes silent identity fallback; `status: non_converged` is explicit |
| Block-diagonal HLA approximation silently optimistic | Info Disclosure | `ld_source: "ukbb_ld_tiled_block_diagonal"` field surfaces to QC dashboard; methods fragment discloses limitation |

## Sources

### Primary (HIGH confidence)
- `src/legacy/region_analysis/scripts/run_susie_rss.R` (lines 14-16, 22-181, 388-441) — codebase verified via Read
- `src/legacy/region_analysis/scripts/run_coloc.R` (line 420, lines 215-279) — codebase verified
- `src/snakemake/rules/finemap.smk` (lines 52-95, 98-111) — codebase verified
- `src/snakemake/rules/ld_reference.smk` (lines 118-150) — codebase verified
- `src/snakemake/rules/multitrait.smk` (lines 116-139) — identifies the ONLY active coloc.abf callsite
- `src/legacy/genome_wide/scripts/run_coloc_genomewide.R` (line 197) — confirmed dormant, not wired to any active rule
- `envs/r_coloc.yml` — pinned coloc 5.2.3, susieR 0.14.2
- `tests/toy_3locus/config_test.yaml` — existing smoke config
- `config/regions_curated.csv` — 8 rows confirmed; Phase 1 adds 4 G3_complex rows
- `.planning/config.json` — `nyquist_validation: true`
- coloc.susie reference docs — https://chr1swallace.github.io/coloc/reference/coloc.susie.html
- rdocumentation coloc 5.2.3 — https://www.rdocumentation.org/packages/coloc/versions/5.2.3/topics/coloc.susie (confirms coloc.susie is present in 5.2.3)
- susieR kriging_rss docs — https://rdrr.io/cran/susieR/man/kriging_rss.html
- susieR diagnostic vignette — https://stephenslab.github.io/susieR/articles/susierss_diagnostic.html
- UKBB-LD AWS Open Data Registry — https://registry.opendata.aws/ukbb-ld/
- Weissbrod et al. 2020 "Functionally-informed fine-mapping" — Nature Genetics (UKBB-LD origin paper)
- gnomAD v3.1.2 release notes — https://gnomad.broadinstitute.org/news/2021-10-gnomad-v3-1-2-minor-release/
- atgu/hgdp_tgp README — https://github.com/atgu/hgdp_tgp
- boto3 anonymous S3 docs — https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

### Secondary (MEDIUM confidence)
- echoLD R package `get_LD_UKB` — https://rdrr.io/github/RajLabMSSM/echoLD/man/get_LD_UKB.html (uses UKBB-LD tiled dataset; confirms the bucket naming convention and NPZ format)
- coloc vignette a06_SuSiE — https://cran.r-project.org/web/packages/coloc/vignettes/a06_SuSiE.html
- Fine-mapping UKBB LD diagnosis — https://xinhe-lab.github.io/mapgen/articles/finemapping_ukbb_ld_diagnosis.html (mapgen also uses UKBB-LD tiled)
- PolyFun UKBB-LD extraction docs — https://github.com/omerwe/polyfun (confirms region-slicing pattern)

### Tertiary (LOW confidence, flagged for validation)
- [ASSUMED] UKBB-LD NPZ internal keys are `R` (upper-triangle dense) and companion `.gz` is a TSV — verified in Wave 0 preflight by loading one tile
- [ASSUMED] HGDP+1kG BCF per-chromosome total size is ~100-200 GB — order of magnitude, verified in Wave 0 preflight by HEAD-request on chr22
- [ASSUMED] UKBB-LD tile-to-region intersection: only HLA spans multiple tiles — verifiable in Wave 0 by computing intersection of the 12 curated regions with the bucket listing

## Wave-ordered plan decomposition

**Recommendation: 5 waves, 6 PLAN files.** All blockers resolved; Wave 0 is preflight-only.

### Wave 0 — Preflight environment check (NO blocking questions)
**Not a plan file. Executed as a single read-only script before Wave 1 starts.**
- Run all 6 Wave 0 preflight verification commands (§Environment Availability)
- Verify `/rs1` scratch has ≥ 500 GB free (for ~170 GB UKBB-LD + ~150 GB HGDP+1kG + ~50 GB margin)
- Verify UKBB-LD S3 bucket reachable + NPZ schema readable on one tile
- Verify gnomAD HTTPS reachable on metadata + one chr22 BCF HEAD
- Verify `coloc::coloc.susie` version ≥ 5.2.0 and `susieR::susie_rss` returns class `"susie"`
- **Exit criterion:** All 6 preflight commands succeed OR operator decides to abort and escalate.

### Wave 1 — Policy + fit persistence + cache clear + A6 dispatch test (1 plan: `01-01-PLAN.md`)
**Goal:** Get `run_susie_rss.R` reading a policy YAML, saving fit objects, and running the retry ladder. No LD panel changes yet; uses existing 1000G panels.

**Task 0 (NEW, from B-03 resolution):** Clean-slate cache clear
- `rm -rf {FINEMAP_DIR}/susie/` OR document use of `snakemake --forceall run_finemap` as the first real execution
- Add comment header to `filter_finemap_summary.py` documenting that the fit-persistence feature requires a cache clear on first enable
- **Exit criterion:** `find {FINEMAP_DIR}/susie -type f 2>/dev/null | wc -l` returns 0

**Task 1:** Create `config/susie_policy.yaml` + `schemas/susie_policy.schema.yaml`. Policy includes the 4 pre-specified complex regions (9p21, APOE, HLA, SLC2A9).

**Task 2:** Modify `run_susie_rss.R`:
- Replace env-var constants with YAML loader
- Add `saveRDS` of fit (with `class(fit) <- c("susie", class(fit))` guard)
- Implement retry ladder
- Emit D1/D2/D3 diagnostics in JSON
- Post-hoc sweep (Pattern 4)

**Task 3 (NEW, from B-04/A6 resolution):** A6 dispatch unit test + fallback branch
- Write `tests/testthat-phase1/test_coloc_susie_dispatch.R`:
  - Synthesize small sumstats + LD
  - Call `susie_rss(...)` → save via `saveRDS` → load via `readRDS` → pass two fits to `coloc::coloc.susie(fit_a, fit_b)`
  - Assert: no warnings, no silent refit (check via `options(warn=2)` to turn warnings into errors)
  - Assert: `inherits(fit_loaded, "susie") == TRUE`
- **Decision gate:** If test fails:
  - Switch `run_susie_rss.R` to call `coloc::runsusie(...)` instead of `susieR::susie_rss(...)` — one-line change (argument names mostly compatible)
  - Update Task 2 pattern accordingly
  - Document the decision in `01-01-PLAN.md` task log
- Both branches (susie_rss path and runsusie path) MUST be spec'd in 01-01-PLAN.md before execution

**Task 4:** Modify `finemap.smk`:
- Add `.fit.rds` as named output
- Add policy file as config input
- Remove `stroke_afr_susie_sweep` placeholder

**Task 5:** Add `config/regions_curated.csv` rows for the 4 G3 complex regions (9p21_CDKN2A, APOE_19q13, HLA_6p21, SLC2A9_urate). Verify column schema first; adjust to match.

**Task 6:** Unit tests: fit roundtrip, policy load, retry ladder with synthetic inputs, monotonicity soft check, A6 dispatch (Task 3 above).

**Task 7:** Dry-run smoke test on toy 3-locus.

- **Exit criterion:** Wave 0 smoke DAG dry-run passes; all unit tests green; A6 dispatch resolved one way or the other; `{FINEMAP_DIR}/susie/` verified empty before dry-run.

### Wave 2 — LD panel plumbing (2 plans, parallel: `01-02-PLAN.md` + `01-03-PLAN.md`)
**Parallelizable.** Two independent tracks; both can run concurrently if the planner/executor has compute budget.

**`01-02-PLAN.md` — EUR LD panel: UKBB-LD tiled (Weissbrod 2020)**
- New `envs/ld_build.yml` (numpy + scipy + boto3 + pandas + r-base + bcftools + plink2 — lightweight, no Hail, no Java)
- New `src/snakemake/scripts/download_ukbb_ld_tiles.py` — boto3 anonymous S3 client, lists tiles, downloads per-region, reconstructs symmetric matrix from upper triangle, slices to curated region bounds, saves as `.rds` via R helper or `pyreadr`
- For `HLA_6p21`: explicit multi-tile block-diagonal handling with `ld_source = "ukbb_ld_tiled_block_diagonal"` flag
- New rule `download_ukbb_ld_tiles` in `ld_reference.smk`
- Per-region extraction to `{LD_REF_DIR}/EUR/{region}.rds` (or `EUR_ukbb_ld/` for auditability)
- Integration test: at least one region (e.g. FTO) has overlap > 50 variants and `ld_source == "ukbb_ld_tiled"`; HLA region has `ld_source == "ukbb_ld_tiled_block_diagonal"`

**`01-03-PLAN.md` — AFR LD panel (HGDP+1kG)** — UNCHANGED from original research
- New `src/snakemake/scripts/build_hgdp_1kg_ld.py` (downloads metadata + BCFs via anonymous HTTPS, extracts AFR samples, runs plink2 per region)
- New `src/snakemake/scripts/plink_ld_to_rds.R` (small R helper to convert plink `.ld` text → `.rds`)
- New rule `build_hgdp_1kg_ld` in `ld_reference.smk`
- Integration test: AFR sample count ≈ 730; at least one region has overlap > 50 variants
- **Scope flag:** Plan should include a "pilot scope" option to build AFR LD ONLY for the 4 complex regions + 3 toy regions if full 22-chromosome extraction is too expensive. Planner chooses.

### Wave 3 — coloc.susie rule + compat layer (1 plan: `01-04-PLAN.md`)
- New `src/snakemake/scripts/run_coloc_susie.R` (full skeleton from Example 3)
- New `src/snakemake/rules/coloc.smk` (single `run_coloc_susie` rule)
- Update `src/snakemake/rules/multitrait.smk` to replace `run_coloc_pair` with a call to the new rule (or delete the legacy rule and rewire all downstream consumers)
- Rename `src/legacy/region_analysis/scripts/run_coloc.R` → `run_coloc_abf_legacy.R`
- Unit tests: empty-CS fit handling, schema compat with `augment_coloc_summary.py`, `sum(PP.H0..PP.H4) ≈ 1`
- Integration test: end-to-end from one pair of `.fit.rds` → JSON output → downstream `augment_coloc_summary.py` success
- **Exit criterion:** `grep -rn "coloc\\.abf" src/snakemake/ src/legacy/region_analysis/scripts/` returns ONLY the renamed legacy file

### Wave 4 — QC dashboard (1 plan: `01-05-PLAN.md`)
- New `envs/qc_dashboard.yml` (Quarto or RMarkdown + DT/reactable + r-rmarkdown)
- New `src/snakemake/scripts/susie_qc_report.qmd` (or `.Rmd`)
- New `src/snakemake/scripts/susie_qc_aggregate.py` (collect all JSON outputs into a single dashboard input TSV)
- New rule `build_susie_qc_dashboard` in `qc.smk`
- Dashboard must surface the `ld_source` field prominently (flag `ukbb_ld_tiled_block_diagonal` for HLA in red)
- Dashboard unit test: renders on toy data, contains D1/D2/D3/D4 columns
- Manual UAT: render on a complex region from Wave 1 test (synthetic HLA-like fixture)

### Wave 5 — First real CI smoke test + downstream integration + OSF amendment (1 plan: `01-06-PLAN.md`)
**The first REAL Phase 1 execution. Unblocked from Phase 0.**
- Modify `filter_finemap_summary.py` to exclude `non_converged` from Tier 1, surface L-saturation flag, surface complex-region flag
- Run full smoke DAG (REAL, not dry-run) in `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/`
- Regenerate all expected results in `tests/toy_3locus/expected/expected_results.yaml`
- Audit grep for `coloc.abf` in active code (success criterion #4)
- Verify `results/finemap/qc_dashboard.html` exists with content (success criterion #5)
- Manual UAT on one complex-region fixture (success criterion #3)
- Write `.planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md` for Phase 11 consumption. **Must document:**
  - UKBB-LD tiled substitution rationale (G6 locked decision)
  - 4-of-6 G3 complex regions scope with LPA + chr8 inversion deferred to Phase 2
  - HLA block-diagonal approximation caveat
- **Post OSF pre-registration amendment** against DOI 10.17605/OSF.IO/PVB5J documenting items (a) and (b) above
- **Exit criterion:** All 5 success criteria verified; CI smoke test first green; OSF amendment posted; Phase 1 closes.

### Why 5 waves / 6 plans (not more, not fewer)

- **Wave 1** is a single cohesive unit (policy + fit persistence + cache clear + A6 test touch the same file set). Splitting would create coordinate risks.
- **Wave 2** must be 2 plans because the two LD tracks are independent technologies (boto3/numpy/NPZ tile vs plink2/BCF) and can genuinely parallelize. Bundling them wastes the parallelism.
- **Wave 3** is 1 plan because the coloc.smk rule + run_coloc_susie.R script + rename are tightly coupled and must be atomic.
- **Wave 4** is 1 plan because the dashboard is a standalone artifact that depends only on JSON outputs, not on internal script state.
- **Wave 5** is 1 plan — the "first real run" is by definition atomic: either it works end-to-end or it doesn't. OSF amendment is folded in because it depends on all prior waves having succeeded.

**Alternative considered:** Collapsing Waves 4 and 5 into a single plan. Rejected because Wave 4's dashboard requires only JSON outputs (can run on any subset), while Wave 5 requires the full smoke DAG green — separating them allows Wave 4 to ship before Wave 5's larger runtime investment.

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — all versions verified in `envs/r_coloc.yml`, coloc.susie API verified via two independent sources
- Architecture: **HIGH** — patterns grounded in existing codebase + verified APIs
- Pitfalls: **HIGH-MEDIUM** — Pitfalls 1, 4, 6, 8, 9 verified; Pitfall 5 is a known theoretical corner case, unverified empirically in this project; Pitfall 9 (HLA tile spanning) is geometrically certain from the 10Mb vs 3Mb comparison
- UKBB-LD tiled feasibility: **HIGH** — 170 GB scope verified, NPZ format standard, bucket reachability verified at bucket-existence level (exact NPZ schema is the only preflight unknown)
- HGDP+1kG AFR: **MEDIUM** — data availability verified; sample count and BCF size are [ASSUMED] and need Wave 0 preflight
- Validation architecture: **HIGH** — Nyquist gate explicitly met; test targets map 1:1 to REQ-2 acceptance criteria; A6 dispatch test + fallback branch explicitly spec'd

**Research date:** 2026-04-11
**Valid until:** 2026-05-11 (30 days — stable domain, but UKBB-LD bucket layout could theoretically shift)

## RESEARCH COMPLETE
