# 1000G AFR PLINK bfile build log — m2-00 Task 4 production fire

**Date:** 2026-04-26
**Plan:** m2-00-preflight-and-environment (Task 4 BLOCKING)
**Pitfall:** RESEARCH Pitfall 3 — `data/reference/ldsc/1000G_AFR_Phase3_plink/` did not exist on disk; only `.frq` files at `1000G_Phase3_frq_AFR/` were present.

## Build configuration

- **PLINK binary:** `/rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/plink`
- **PLINK version:** v1.9.0-b.8 64-bit (22 Oct 2024)
- **VCF source:** `data/raw/1kg/vcf/chr{1..22}.vcf.gz`
- **Sample keep file:** `data/raw/1kg/AFR.samples` (504 IDs; FID==IID)
- **QC filters:** `--maf 0.005 --geno 0.05 --hwe 1e-6`
- **Memory per chr:** 3500 MB
- **Parallelism:** xargs -P 5 (per project memory `feedback_parallel_downloads.md`)

## Wall time

- chr22 sentinel: ~30 s (smallest autosome, 265 k SNPs)
- chr1..21 parallel batches of 5: 505 s (~8.5 min)
- **Total wall: ~9 min** (vs plan budget of ~3 hr LSF wall)

## Outputs

- 22 chr × 3 file types (`.bed`, `.bim`, `.fam`) = 66 files
- Sentinel: `data/reference/ldsc/1000G_AFR_Phase3_plink/.build_complete`
- Total disk: 2.9 GB

## SNP counts (post-QC)

| Chromosome | SNPs (post-QC) | Samples |
|------------|----------------|---------|
| 1          | 1,508,501      | 504     |
| 2          | 1,631,201      | 504     |
| 22         | 265,294        | 504     |

(All 22 .bim files exist with ≥100k SNPs; chr22 is the smallest at 265k.)

## Verification

```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m2/test_1000g_afr_plink_build.py -x
tests/m2/test_1000g_afr_plink_build.py ..                                [100%]
============================== 2 passed in 0.09s ===============================
```

## Deviations from plan

- **Faster build via direct PLINK invocation:** Plan recipe used `snakemake --use-conda m2_build_1000g_afr_plink_all` which would build the m2-clumping conda env first (~10 min solver overhead). Used the existing PLINK 1.9 binary at `/rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/plink` directly (Rule 3 — auto-fix blocking dependency without altering the rule semantics). The Snakemake rule itself is unchanged at `src/snakemake/rules/m2_reference.smk`; production runs of the rule via `--use-conda` will still work as Wave 4 PLINK clumping consumers come online and need the m2-clumping env anyway.
- **Parallel xargs over LSF:** Plan suggested LSF dispatch via bsub_wrapper.sh queue=standard. Local xargs -P 5 finished the build faster than the per-job LSF queue overhead would allow. No LSF job ID to record.

## D-M2-02 commitments

This 1000G AFR PLINK build is **provisional** per D-M2-02. The M3 AoU AFR WGS LD panel build (~100k samples) will supersede it; outputs at that time gain an `LD-AoU-AFR` filename token to distinguish from these `LD-1000G-AFR` outputs. The post-M3 re-run trigger will be appended to `.planning/m2_post_m3_rerun_queue.tsv` at M2 closeout.
