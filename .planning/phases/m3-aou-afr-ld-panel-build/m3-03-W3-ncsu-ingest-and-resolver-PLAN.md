---
phase: m3-aou-afr-ld-panel-build
plan: 03
type: execute
wave: 3
depends_on: ["00", "02"]
files_modified:
  - src/scripts/ld_npz_to_rds.R
  - src/python/bm_to_npz.py
  - src/snakemake/rules/m3_ingest_aou_ld.smk
  - src/snakemake/rules/m3_convert_npz_rds.smk
  - src/snakemake/rules/finemap.smk
  - Snakefile
  - tests/m3/test_ld_npz_to_rds.py
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-PATH-PARAMETERIZATION
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "src/scripts/ld_npz_to_rds.R lands per AOU-LD-PIPELINE.md §8.2 verbatim with one fix: chr-prefix-handling stripping (some AoU exports have 'chr16' prefix; some have '16'); GRCh38 to GRCh37 variant ID liftover via data/external/liftover/hg38ToHg19.over.chain.gz per DEC-2026-04-24-01."
    - "src/python/bm_to_npz.py is a Hail-not-required helper that reads a Hail BlockMatrix sharded directory (per Path A.3 from RESEARCH Q5) and emits a single lower-triangular .npz file for ingest. Used for the ≥10 Mb regions that took Path A.3 in Wave 2 / Wave 4."
    - "src/snakemake/rules/m3_ingest_aou_ld.smk encodes the flag-driven AoU-export-arrives rule pattern matching m1_download.smk lines 46-62 (output: flag=os.path.join(LD_INTERIM, '.aou_export_complete.{chr}.{ancestry}'))."
    - "src/snakemake/rules/m3_convert_npz_rds.smk has rules build_ld_rds_aou_afr + build_ld_rds_aou_eur paralleling the existing build_ld_rds_1kg_eur convention; output: data/processed/ld_reference/{ANCESTRY}_aou/{region_id}.rds."
    - "src/snakemake/rules/finemap.smk line 56 ld_matrix input is wrapped in a resolver call: ld_matrix=lambda wildcards: str(resolve_ld_path(wildcards.region, wildcards.ancestry, config)) per RESEARCH Q7 §Integration point."
    - "Top-level Snakefile includes the two new M3 rule files."
    - "tests/m3/test_ld_npz_to_rds.py covers .npz to .rds round-trip, symmetry recovery, dimnames preservation, chr-prefix stripping, GRCh38 to GRCh37 variant ID liftover."
    - "snakemake --use-conda --dry-run resolves a representative target like data/processed/ld_reference/AFR_aou/m2_region_00067.rds without errors (REQ-SNAKEMAKE-CI)."
  artifacts:
    - path: "src/scripts/ld_npz_to_rds.R"
      provides: "R converter from .npz to .rds with symmetry recovery + dimnames + GRCh38 to GRCh37 variant ID liftover"
      min_lines: 60
    - path: "src/python/bm_to_npz.py"
      provides: "Path A.3 helper: read Hail BlockMatrix sharded directory + emit a lower-triangular .npz"
      min_lines: 40
    - path: "src/snakemake/rules/m3_ingest_aou_ld.smk"
      provides: "Flag-driven AoU-export-arrives rule + per-chromosome bundle inventory"
    - path: "src/snakemake/rules/m3_convert_npz_rds.smk"
      provides: "build_ld_rds_aou_afr + build_ld_rds_aou_eur rules wiring to ld_npz_to_rds.R"
    - path: "src/snakemake/rules/finemap.smk"
      provides: "Modified to call resolve_ld_path() at line 56-area ld_matrix input"
      contains: "resolve_ld_path"
    - path: "Snakefile"
      provides: "Top-level Snakefile updated to include m3_ingest_aou_ld.smk + m3_convert_npz_rds.smk"
    - path: "tests/m3/test_ld_npz_to_rds.py"
      provides: "Pytest covering .npz to .rds converter behavior"
  key_links:
    - from: "src/snakemake/rules/m3_convert_npz_rds.smk"
      to: "src/scripts/ld_npz_to_rds.R"
      via: "shell: Rscript src/scripts/ld_npz_to_rds.R {input.npz} {output.rds}"
      pattern: "ld_npz_to_rds\\.R"
    - from: "src/snakemake/rules/finemap.smk"
      to: "src/python/ld_panel.py::resolve_ld_path"
      via: "lambda wildcards: str(resolve_ld_path(wildcards.region, wildcards.ancestry, config))"
      pattern: "resolve_ld_path"
    - from: "src/snakemake/rules/m3_ingest_aou_ld.smk"
      to: "data/interim/aou_ld_exports/{ancestry}/{region}.npz"
      via: "input pattern; flag-driven rule fires when egress-arrives flag is touched"
      pattern: "data/interim/aou_ld_exports"
    - from: "src/python/bm_to_npz.py"
      to: "data/interim/aou_ld_exports/{ancestry}/bm/{region}.bm/"
      via: "Hail BlockMatrix sharded directory read"
      pattern: "BlockMatrix|\\.bm"
---

<objective>
Wave 3 lands the production-grade NCSU-side ingest infrastructure: .npz to .rds R converter (with chr-prefix fix + GRCh38 to GRCh37 liftover for variant IDs per DEC-2026-04-24-01), a BlockMatrix-to-NPZ Python helper for Path A.3 large/xlarge regions, two M3 Snakemake rule files, the finemap.smk resolver wiring per RESEARCH Q7, and the converter pytest. This is the wave that promotes the Wave 2 bootstrap converter to a production-grade Snakemake DAG with full test coverage.

Purpose: All NCSU-side path resolution + .npz to .rds conversion goes through this wave's deliverables. Wave 4 production fire (322 cells) consumes them at scale.

Output: 7 source / rules / Snakefile / test files, all passing pytest + snakemake --use-conda --dry-run resolution against the new ld_panel: chains.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md
@.planning/amendments/AOU-LD-PIPELINE.md

<interfaces>
<!-- Wave 0 deliverables Wave 3 wires up. -->

src/python/ld_panel.py::resolve_ld_path (Wave 0):
- resolve_ld_path(region_id: str, ancestry: str, config: dict) -> pathlib.Path
- Walks config['ld_panel'][ancestry] fallback chain; returns first existing .rds path

config/pipeline.yaml ld_panel: block (Wave 0):
- AFR / EUR / TRANS chains, pin override, strict_aou_only mode

src/snakemake/rules/finemap.smk line 56-area current state (PRE-Wave-3):
```
input:
    ld_matrix = lambda w: f"{config['paths']['ld_reference']}/{w.ancestry}/{w.region}.rds"
```

POST-Wave-3:
```
input:
    ld_matrix = lambda wildcards: str(resolve_ld_path(wildcards.region, wildcards.ancestry, config))
```

src/snakemake/rules/m1_download.smk lines 46-62 — flag-driven download rule pattern (M3 mirrors):
```
rule download_ldsc_data:
    output:
        flag=os.path.join(_RAW_ROOT, ".download_complete.{tag}")
    shell:
        "..."
```

src/snakemake/rules/ld_reference.smk top-of-file conda-env workaround pattern:
```
LD_BUILD_ENV = str(Path(workflow.basedir) / "envs" / "ld_build.yml")
```
M3 follows same pattern with M3_R_LD_ENV = str(... / "envs" / "m3-r-ld.yml") and M3_AOU_DEV_ENV = str(... / "envs" / "m3-aou-dev.yml").

AOU-LD-PIPELINE.md §8.2 verbatim R converter source (lines 343-362):
```r
suppressPackageStartupMessages({ library(reticulate); library(Matrix) })
np <- reticulate::import("numpy")
convert_one <- function(npz_path, rds_path) {
  z <- np$load(npz_path, allow_pickle = TRUE)
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
M3 needs to add: (a) chr-prefix-handling fix; (b) GRCh38 to GRCh37 variant ID liftover via data/external/liftover/hg38ToHg19.over.chain.gz per DEC-2026-04-24-01; (c) provenance JSON output (npz path + chain SHA + datetime).

m3_dev_complete.flag (Wave 2 deliverable) is the gate for Wave 4 production rules (NOT Wave 3 ingest rules — Wave 3 rules can run on dev or production .npz).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: ld_npz_to_rds.R converter + bm_to_npz.py Path A.3 helper + pytest</name>
  <files>src/scripts/ld_npz_to_rds.R, src/python/bm_to_npz.py, tests/m3/test_ld_npz_to_rds.py</files>
  <read_first>
    - .planning/amendments/AOU-LD-PIPELINE.md §8.2 (lines 339-362) — verbatim R source for ld_npz_to_rds.R
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q5 — Hail BlockMatrix block_size tuning" (lines 236-263) — Path A.3 BlockMatrix-write convention
    - .planning/DECISIONS.md DEC-2026-04-24-01 (GRCh37 canonical analytic plane; conversion-step liftover)
    - data/external/liftover/hg38ToHg19.over.chain.gz (existing chain file; SHA-256 verified per project state)
    - envs/m3-r-ld.yml (Wave 0; r-base + reticulate + Matrix + jsonlite)
  </read_first>
  <behavior>
    - test_npz_to_rds_round_trip: write a synthetic LD matrix (50×50 symmetric float32) + variant_ids + rsids to .npz; run ld_npz_to_rds.R; read .rds back; assert symmetric, dimnames present, matrix dimensions match.
    - test_chr_prefix_stripping: variant_ids with "chr16:..." prefix get stripped to "16:..." in the .rds dimnames.
    - test_grch38_to_grch37_liftover: variant ID "chr16:53809247:T:A" (GRCh38 FTO rs1558902) lifts over to "16:53803574:T:A" (GRCh37 — correct rs1558902 b37 coordinate per dbSNP); .rds dimnames carry b37 IDs.
    - test_rsid_preference_over_synthetic: when both rsid and synthetic ID populated, dimnames prefer rsid.
    - test_failed_liftover_drops_variant: variants whose IDs fail to liftover are dropped from the .rds (with stderr audit line); matrix dimensions reduced accordingly.
    - test_provenance_json: .rds contents include a `provenance` field with npz_path, chain_sha256, datetime, n_var_input, n_var_output.
    - test_bm_to_npz_helper: src/python/bm_to_npz.py reads a synthetic Hail BlockMatrix sharded directory (built via hl.BlockMatrix.from_numpy) and writes a valid lower-triangular .npz that ld_npz_to_rds.R can ingest.
  </behavior>
  <action>
    1. Write `src/scripts/ld_npz_to_rds.R` (~80 lines). Skeleton:
       ```r
       suppressPackageStartupMessages({
         library(reticulate); library(Matrix); library(jsonlite); library(digest)
       })
       np <- reticulate::import("numpy")

       args <- commandArgs(trailingOnly = TRUE)
       npz_path  <- args[1]
       rds_path  <- args[2]
       chain_path <- args[3]   # data/external/liftover/hg38ToHg19.over.chain.gz

       chain_sha256 <- digest(file = chain_path, algo = "sha256")

       # 1. Load .npz
       z <- np$load(npz_path, allow_pickle = TRUE)
       tri <- z$f[["ld"]]
       if (!is.matrix(tri)) stop("unexpected ld shape in ", npz_path)

       # 2. Symmetry recovery (lower-triangular -> full symmetric)
       if (!isSymmetric(tri)) tri <- tri + t(tri) - diag(diag(tri))

       # 3. Recover SNP IDs (prefer rsid; fall back to chr:pos:ref:alt)
       rsids <- as.character(z$f[["rsids"]])
       vids  <- as.character(z$f[["variant_ids"]])
       snp_ids_grch38 <- ifelse(nzchar(rsids), rsids, vids)
       n_input <- length(snp_ids_grch38)

       # 4. Strip "chr" prefix (some AoU exports have "chr16:..."; some have "16:...")
       snp_ids_grch38 <- sub("^chr", "", snp_ids_grch38)

       # 5. Liftover variant coordinates GRCh38 -> GRCh37 via pyliftover (reticulate)
       #    Variant IDs of form "16:53809247:T:A" stay as rsid if rsid;
       #    if no rsid, parse chr:pos:ref:alt, liftover pos, reform.
       pyliftover <- reticulate::import("pyliftover")
       lo <- pyliftover$LiftOver("hg38", "hg19")
       liftover_one <- function(vid) {
         if (grepl("^rs[0-9]+$", vid)) return(vid)   # rsid is genome-build-agnostic
         parts <- strsplit(vid, ":")[[1]]
         if (length(parts) < 4) return(NA_character_)
         chr <- parts[1]; pos38 <- as.integer(parts[2]); ref <- parts[3]; alt <- parts[4]
         result <- lo$convert_coordinate(paste0("chr", chr), pos38 - 1L)   # pyliftover is 0-based
         if (length(result) == 0) return(NA_character_)
         pos37 <- result[[1]][[2]] + 1L
         paste(chr, pos37, ref, alt, sep = ":")
       }
       snp_ids_grch37 <- vapply(snp_ids_grch38, liftover_one, character(1))
       drop_idx <- is.na(snp_ids_grch37)
       n_dropped <- sum(drop_idx)
       if (n_dropped > 0) {
         message(sprintf("LIFTOVER_DROP %d / %d variants in %s", n_dropped, n_input, npz_path))
         tri <- tri[!drop_idx, !drop_idx]
         snp_ids_grch37 <- snp_ids_grch37[!drop_idx]
       }
       n_output <- length(snp_ids_grch37)

       # 6. Set dimnames (b37 IDs)
       dimnames(tri) <- list(snp_ids_grch37, snp_ids_grch37)

       # 7. Provenance manifest
       provenance <- list(
         npz_path = npz_path,
         chain_path = chain_path,
         chain_sha256 = chain_sha256,
         datetime = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
         n_var_input = n_input,
         n_var_output = n_output,
         n_var_dropped_liftover = n_dropped,
         genome_build = "GRCh37"
       )

       # 8. Save
       saveRDS(list(ld = tri, snp_ids = snp_ids_grch37, provenance = provenance),
               rds_path, compress = "xz")
       message(sprintf("WROTE %s (%d x %d)", rds_path, n_output, n_output))
       ```

    2. Write `src/python/bm_to_npz.py` (~80 lines). Skeleton:
       ```python
       """Path A.3 helper: read a Hail BlockMatrix sharded directory and emit a lower-triangular .npz.

       Used by Wave 3 + Wave 4 for regions where compute_region_ld() chose Path A.3
       (region_class in {large, xlarge}) per RESEARCH Q5. The BlockMatrix lives at
       gs://${WORKSPACE_BUCKET}/ld/{ANCESTRY}_aou/bm/{region_id}.bm/ — Carter
       gsutil cp's the sharded directory to NCSU GPFS at
       data/interim/aou_ld_exports/{ANCESTRY}_aou/bm/{region_id}.bm/ ; this
       script then converts to .npz for ingest by ld_npz_to_rds.R.
       """
       import argparse, sys, numpy as np
       import hail as hl

       def main():
           p = argparse.ArgumentParser()
           p.add_argument("--bm-dir", required=True, help="Path to Hail BlockMatrix sharded directory")
           p.add_argument("--out-npz", required=True, help="Output .npz path")
           p.add_argument("--variant-ids-tsv", required=True, help="Variant IDs sidecar TSV emitted by AOU-2")
           p.add_argument("--rsids-tsv", required=True, help="rsIDs sidecar TSV emitted by AOU-2")
           args = p.parse_args()

           hl.init(default_reference="GRCh38", quiet=True)
           bm = hl.linalg.BlockMatrix.read(args.bm_dir)
           ld_dense = bm.to_numpy().astype("float32")
           variant_ids = np.loadtxt(args.variant_ids_tsv, dtype=str)
           rsids = np.loadtxt(args.rsids_tsv, dtype=str)
           # Lower-triangular (symmetric storage)
           lower = np.tril(ld_dense)
           np.savez_compressed(args.out_npz, ld=lower, variant_ids=variant_ids, rsids=rsids)
           print(f"WROTE {args.out_npz} ({lower.shape[0]} x {lower.shape[1]})")

       if __name__ == "__main__":
           sys.exit(main())
       ```

    3. Write `tests/m3/test_ld_npz_to_rds.py` covering the 7 behaviors. Use `np.savez_compressed` to build synthetic test fixtures (50×50 symmetric matrices); use `subprocess.run([..., "Rscript", "src/scripts/ld_npz_to_rds.R", npz, rds, chain])` to invoke the converter; use `pyreadr` (Python R reader) or `subprocess` calling R one-liner to read .rds back. For test_grch38_to_grch37_liftover, hard-code rs1558902's GRCh38/GRCh37 known coordinates from dbSNP for verification. Use `pytest.importorskip("hail")` for test_bm_to_npz_helper.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_ld_npz_to_rds.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `wc -l src/scripts/ld_npz_to_rds.R` returns ≥ 60.
    - `grep -c "pyliftover\\|LiftOver" src/scripts/ld_npz_to_rds.R` returns ≥ 1 (variant ID liftover present).
    - `grep -c "chain_sha256\\|chain_path" src/scripts/ld_npz_to_rds.R` returns ≥ 1 (chain file SHA recorded in provenance).
    - `grep -c "saveRDS" src/scripts/ld_npz_to_rds.R` returns 1.
    - `grep -c "provenance" src/scripts/ld_npz_to_rds.R` returns ≥ 2.
    - `grep -c "BlockMatrix.read\\|hl\\.linalg\\.BlockMatrix" src/python/bm_to_npz.py` returns ≥ 1.
    - `grep -c "savez_compressed" src/python/bm_to_npz.py` returns 1.
    - `pytest tests/m3/test_ld_npz_to_rds.py -v` reports ≥ 7 passed (or graceful skips for hail-only tests) with exit 0.
  </acceptance_criteria>
  <done>
    Converter R script + BlockMatrix-to-NPZ helper + pytest scaffold land. Provenance + liftover + chr-prefix-stripping all unit-tested. Ready for Snakemake rule wiring at Task 2.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: m3_ingest_aou_ld.smk + m3_convert_npz_rds.smk + finemap.smk resolver wiring + Snakefile inclusion</name>
  <files>src/snakemake/rules/m3_ingest_aou_ld.smk, src/snakemake/rules/m3_convert_npz_rds.smk, src/snakemake/rules/finemap.smk, Snakefile</files>
  <read_first>
    - src/snakemake/rules/m1_download.smk lines 46-62 — flag-driven download rule pattern reference
    - src/snakemake/rules/ld_reference.smk lines 274-334 (build_ld_rds_1kg_eur) AND lines 349-448 (download_ukbb_ld_tiles, build_hgdp_1kg_ld) — pattern reference
    - src/snakemake/rules/finemap.smk lines 45-102 — current run_finemap rule; line 56-area is the ld_matrix input that gets resolver-wrapped
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q7 — config/pipeline.yaml ld_panel: resolver implementation > Integration point" (lines 344-355) — verbatim resolver-wiring snippet
    - Snakefile (top-level; current state — needs M3 includes added)
  </read_first>
  <action>
    1. Write `src/snakemake/rules/m3_ingest_aou_ld.smk` (~80 lines). Top-of-file:
       ```python
       from pathlib import Path
       M3_AOU_DEV_ENV = str(Path(workflow.basedir) / "envs" / "m3-aou-dev.yml")
       LD_INTERIM = config["paths"].get("ld_interim", "data/interim/aou_ld_exports")
       LD_REF_DIR = config["paths"]["ld_reference"]

       rule m3_ingest_aou_export_arrives:
           """Flag-driven rule: fires when Carter has gsutil cp'd a per-chromosome bundle from
           the AoU workspace bucket to data/interim/aou_ld_exports/{ancestry}/.
           Mirrors m1_download.smk lines 46-62 pattern.
           """
           output:
               flag = os.path.join(LD_INTERIM, ".aou_export_complete.{ancestry}.{chr}")
           input:
               npz_dir = directory(os.path.join(LD_INTERIM, "{ancestry}"))
           run:
               # Verify at least one .npz exists for {chr} under {ancestry}
               npz_files = list(Path(input.npz_dir).glob(f"*.npz"))
               # ... (chromosome filter — region_id pattern ties back to manifest chr column)
               import pandas as pd
               manifest = pd.read_csv(config.get("ld_regions_manifest", "config/ld_regions.tsv"), sep="\t")
               regions_for_chr = manifest[(manifest["chr"] == int(wildcards.chr)) & (manifest["ancestry"] == wildcards.ancestry)]["region_id"].tolist()
               present = [p.stem for p in npz_files]
               missing = [r for r in regions_for_chr if r not in present]
               if missing:
                   raise FileNotFoundError(f"chr {wildcards.chr} {wildcards.ancestry} bundle missing regions: {missing}")
               Path(output.flag).touch()
       ```

    2. Write `src/snakemake/rules/m3_convert_npz_rds.smk` (~60 lines):
       ```python
       from pathlib import Path
       M3_R_LD_ENV = str(Path(workflow.basedir) / "envs" / "m3-r-ld.yml")
       LD_INTERIM = config["paths"].get("ld_interim", "data/interim/aou_ld_exports")
       LD_REF_DIR = config["paths"]["ld_reference"]
       LIFTOVER_CHAIN_38_TO_37 = "data/external/liftover/hg38ToHg19.over.chain.gz"

       rule build_ld_rds_aou_afr:
           """Convert AoU AFR LD .npz to .rds with GRCh38 to GRCh37 variant ID liftover."""
           input:
               npz = os.path.join(LD_INTERIM, "AFR_aou", "{region_id}.npz"),
               chain = LIFTOVER_CHAIN_38_TO_37,
           output:
               rds = os.path.join(LD_REF_DIR, "AFR_aou", "{region_id}.rds"),
           log:
               "logs/ld_reference/aou_afr/{region_id}.log",
           conda:
               M3_R_LD_ENV
           shell:
               "Rscript src/scripts/ld_npz_to_rds.R {input.npz} {output.rds} {input.chain} &> {log}"

       rule build_ld_rds_aou_eur:
           """Convert AoU EUR LD .npz to .rds with GRCh38 to GRCh37 variant ID liftover."""
           input:
               npz = os.path.join(LD_INTERIM, "EUR_aou", "{region_id}.npz"),
               chain = LIFTOVER_CHAIN_38_TO_37,
           output:
               rds = os.path.join(LD_REF_DIR, "EUR_aou", "{region_id}.rds"),
           log:
               "logs/ld_reference/aou_eur/{region_id}.log",
           conda:
               M3_R_LD_ENV
           shell:
               "Rscript src/scripts/ld_npz_to_rds.R {input.npz} {output.rds} {input.chain} &> {log}"
       ```

    3. Modify `src/snakemake/rules/finemap.smk` line 56-area. The current state is approximately:
       ```python
       input:
           ld_matrix = lambda w: f"{config['paths']['ld_reference']}/{w.ancestry}/{w.region}.rds"
       ```
       Replace with (per RESEARCH Q7 §Integration point):
       ```python
       # M3 Wave 3: route LD path through ld_panel: resolver (RESEARCH Q7)
       import sys; sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
       from ld_panel import resolve_ld_path

       # ...

       input:
           ld_matrix = lambda wildcards: str(resolve_ld_path(wildcards.region, wildcards.ancestry, config))
       ```
       Add a top-of-file comment block: "# Modified 2026-04-28 (m3-W3-T2): ld_matrix input routed through resolve_ld_path() per RESEARCH Q7. Original hardcoded path retained as comment for audit."

    4. Modify top-level `Snakefile` to add the M3 includes after the existing `include:` lines:
       ```python
       include: "src/snakemake/rules/m3_ingest_aou_ld.smk"
       include: "src/snakemake/rules/m3_convert_npz_rds.smk"
       ```

    5. Run a Snakemake DAG resolution check inline as part of this task's verification: `snakemake --snakefile Snakefile --dry-run data/processed/ld_reference/AFR_aou/m2_region_00067.rds` should resolve without errors (REQ-SNAKEMAKE-CI extension).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH snakemake --snakefile Snakefile --dry-run --use-conda data/processed/ld_reference/AFR_aou/m2_region_00067.rds 2&gt;&amp;1 | tail -30</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "rule build_ld_rds_aou_afr" src/snakemake/rules/m3_convert_npz_rds.smk` returns 1.
    - `grep -c "rule build_ld_rds_aou_eur" src/snakemake/rules/m3_convert_npz_rds.smk` returns 1.
    - `grep -c "rule m3_ingest_aou_export_arrives\\|aou_export_complete" src/snakemake/rules/m3_ingest_aou_ld.smk` returns ≥ 1.
    - `grep -c "resolve_ld_path" src/snakemake/rules/finemap.smk` returns ≥ 1 (resolver wired).
    - `grep -c "from ld_panel import resolve_ld_path\\|from src.python.ld_panel import" src/snakemake/rules/finemap.smk` returns ≥ 1.
    - `grep -c "include:.*m3_ingest_aou_ld.smk" Snakefile` returns 1.
    - `grep -c "include:.*m3_convert_npz_rds.smk" Snakefile` returns 1.
    - `grep -c "M3_R_LD_ENV\\|m3-r-ld.yml" src/snakemake/rules/m3_convert_npz_rds.smk` returns ≥ 1 (conda env routing).
    - `snakemake --snakefile Snakefile --dry-run --use-conda data/processed/ld_reference/AFR_aou/m2_region_00067.rds` exits 0 (DAG resolution check).
    - `grep -c "hg38ToHg19.over.chain.gz" src/snakemake/rules/m3_convert_npz_rds.smk` returns ≥ 1 (DEC-2026-04-24-01 chain wired).
  </acceptance_criteria>
  <done>
    Three M3 Snakemake rule files / modifications land. Snakefile includes them. snakemake --dry-run resolves a representative AFR_aou region. resolver is wired into finemap.smk (M4 unblocked for the M3 ld_panel: chain). REQ-PATH-PARAMETERIZATION + REQ-SNAKEMAKE-CI both closed for the M3 surface.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| .npz on GPFS ↔ .rds on GPFS | Both NCSU-side; conversion is local. SHA-256 of chain file + provenance JSON anchor reproducibility. |
| pipeline.yaml ld_panel: ↔ M4 fine-mapping consumer | Resolver helper is the single point through which all LD path resolution flows; eliminates ad-hoc path construction throughout the codebase. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3-S2-W3 | Reproducibility / provenance | ld_npz_to_rds.R provenance JSON | mitigate | Every .rds includes a `provenance` field with: npz_path, chain_path, chain_sha256, datetime, n_var_input, n_var_output, n_var_dropped_liftover, genome_build. Auditable per-region for the manuscript supplementary materials. |
| T-M3-S1-W3 | Tampering / supply chain | M3_R_LD_ENV conda env | mitigate | Pinned via envs/m3-r-ld.yml (Wave 0); resolved env hash captured in Snakemake conda cache; `--use-conda` flag enforces env consistency. |
| T-M3-AUTH-W3 | Authorization | finemap.smk resolver wiring | mitigate | resolve_ld_path() is the only legal path-resolution entry point; ld_panel: pin override + strict_aou_only mode allow Track A finalization (EUR_1kg pin) AND M3 strict-AoU production runs to coexist without code modification. |
| T-M3-EGR-W3 | Information disclosure | bm_to_npz.py | accept | Operates on already-egressed BlockMatrix sharded directories (post-AoU classification ruling); no AoU access required. |
</threat_model>

<verification>
**Wave 3 phase-level checks:**

1. `pytest tests/m3 -x --tb=short` passes (now 9+ tests including test_ld_npz_to_rds.py).
2. `snakemake --snakefile Snakefile --dry-run --use-conda data/processed/ld_reference/AFR_aou/m2_region_00067.rds` exits 0 (DAG resolution check).
3. `python -c "from src.python.ld_panel import resolve_ld_path; from pathlib import Path; print('OK')"` exits 0 (resolver still importable).
4. `grep -c "resolve_ld_path" src/snakemake/rules/finemap.smk` ≥ 1.
5. `grep -c "include:.*m3_" Snakefile` returns 2.
6. `grep -c "provenance" src/scripts/ld_npz_to_rds.R` ≥ 2.
</verification>

<success_criteria>
- ld_npz_to_rds.R lands with chr-prefix fix + GRCh38 to GRCh37 liftover + provenance JSON.
- bm_to_npz.py Path A.3 helper lands and reads BlockMatrix sharded dirs.
- m3_ingest_aou_ld.smk + m3_convert_npz_rds.smk land with proper conda env routing.
- finemap.smk wired to call resolve_ld_path() at the ld_matrix input.
- Snakefile includes both M3 rule files.
- snakemake --dry-run resolves AFR_aou path through the resolver chain.
- test_ld_npz_to_rds.py covers 7 behaviors and passes.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-03-W3-ncsu-ingest-and-resolver-SUMMARY.md` recording:
- Files created (7) + lines of code added
- Snakemake DAG resolution check outcome
- Pytest pass count
- Any path-resolution surprises (e.g., legacy region_safe vs region_id mappings encountered)
</output>
