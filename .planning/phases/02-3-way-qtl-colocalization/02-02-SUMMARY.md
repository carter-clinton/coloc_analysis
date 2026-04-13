---
phase: 02-3-way-qtl-colocalization
plan: 02
subsystem: qtl-coloc-backbone
tags: [eqtl, gtex, coloc, susie, snakemake, harmonize, backbone]

# Dependency graph
requires:
  - phase: 01-coloc-susie-fine-mapping-spine
    provides: ".fit.rds GWAS fits, LD matrices, finemap_output(), coloc.smk pattern"
  - plan: 02-01
    provides: "GRCh38 regions, qtl_sources.yaml, pph4_thresholds.yaml, mock QTL fixtures"
provides:
  - "harmonize_eqtl.py: eQTL Catalogue -> common intermediate TSV"
  - "build_tissue_n_lookup.py: GTEx v8 49-tissue N fallback dict"
  - "run_qtl_coloc.R: unified GWAS-vs-QTL coloc.susie runner (source-agnostic)"
  - "qtl_coloc.smk: manifest-driven QTL coloc dispatch rules"
  - "qtl_download.smk: eQTL Catalogue download + harmonize rules"
  - "Snakefile includes for qtl_download.smk and qtl_coloc.smk"
affects:
  - "Plans 02-03 (sQTL/pQTL) and 02-04 (sc-eQTL) extend this backbone"
  - "Plan 02-05 (tiering/aggregation) consumes qtl_coloc_summary.tsv"

# Tech stack
tech-stack:
  added: [optparse, data.table, jsonlite]
  patterns: [manifest-driven-dispatch, tdd, coloc-susie-runner, harmonize-pipeline]

# Key files
key-files:
  created:
    - src/python/harmonize_eqtl.py
    - src/python/build_tissue_n_lookup.py
    - src/snakemake/scripts/run_qtl_coloc.R
    - src/snakemake/rules/qtl_coloc.smk
    - src/snakemake/rules/qtl_download.smk
    - tests/phase2/test_harmonize_eqtl.py
    - tests/phase2/test_run_qtl_coloc.py
  modified:
    - Snakefile

# Decisions
decisions:
  - "run_qtl_coloc.R fits SuSiE on QTL side (runsusie with suffix=2) then calls coloc.susie; GWAS fit is pre-fitted from Phase 1"
  - "harmonize_eqtl.py uses pandas fallback when pysam not available; tabix path is optimal but not required"
  - "Manifest builder will cross-join ALL QTL sources from config (not just eQTL); sQTL/pQTL/sc-eQTL rows appear once their harmonized files exist"

# Metrics
metrics:
  duration: "7min"
  completed: "2026-04-13"
  tasks: 2
  files: 8
---

# Phase 02 Plan 02: GTEx v8 eQTL Coloc Backbone Summary

**One-liner:** eQTL harmonization pipeline + source-agnostic run_qtl_coloc.R coloc.susie runner with manifest-driven Snakemake dispatch

## What Was Built

### Task 1: eQTL Harmonization Pipeline

**harmonize_eqtl.py** reads eQTL Catalogue allpairs TSV files and outputs a standardized common intermediate format. Key behaviors:
- Filters by GRCh38 region window and Ensembl gene ID (ignoring version suffixes)
- Computes N = an/2 from the eQTL Catalogue `an` column
- Sets sdY = 1.0 for GTEx (inverse-normal transformed)
- MAF filter: drops variants with maf < 0.005 or > 0.995
- Tabix-optimized path via pysam with pandas fallback
- Column mapping driven by config/qtl_sources.yaml

**build_tissue_n_lookup.py** produces a JSON mapping of GTEx v8 tissue -> sample size (N). Contains hardcoded fallback dict with all 49 GTEx v8 tissues (range 73-706 samples). Accepts optional eQTL Catalogue metadata TSV for dynamic lookup.

**qtl_download.smk** provides three Snakemake rules:
- `download_eqtl_catalogue`: downloads allpairs TSV + tabix index with non-empty file validation (T-02-04)
- `build_tissue_n_lookup`: generates the tissue N JSON
- `harmonize_eqtl_region`: harmonizes a single (tissue, gene, region) triple

### Task 2: Unified coloc.susie Runner + Dispatch

**run_qtl_coloc.R** is the most critical new file in Phase 2. It is source-agnostic: any QTL source that produces the harmonized TSV intermediate can feed into it. Processing:
1. Loads pre-fitted GWAS .fit.rds from Phase 1
2. Reads harmonized QTL TSV, matches SNPs across GWAS/QTL/LD
3. Builds coloc dataset, validates via check_dataset(req="LD") (T-02-07)
4. Fits SuSiE on QTL side via runsusie(suffix=2)
5. Calls coloc.susie(gwas_fit, qtl_fit)
6. Writes JSON with best pairwise row, all pairs, metadata
7. Edge cases: too_few_snps (<50 overlap), qtl_susie_failed (retry with max_iter=200), no_qtl_cs, no_gwas_cs

**qtl_coloc.smk** provides manifest-driven dispatch modeled on Phase 1 coloc.smk:
- `build_qtl_coloc_manifest`: cross-joins regions x QTL sources x tissues x genes (all sources, not just eQTL)
- `run_qtl_coloc`: invokes run_qtl_coloc.R with manifest-resolved inputs
- `aggregate_qtl_coloc`: collects per-pair JSONs into summary TSV
- T-02-05: wildcard_constraints on qtl_coloc_id prevents path traversal

**Snakefile** updated with two includes (qtl_download.smk before qtl_coloc.smk) after the existing coloc.smk include.

## Test Coverage

| Test File | Tests | Description |
|-----------|-------|-------------|
| test_harmonize_eqtl.py | 9 | Output columns, sdY=1, N=an/2, region filter, MAF filter, gene filter, tissue column |
| test_run_qtl_coloc.py | 24 | R script interface (13), Snakemake rules (8), Snakefile includes (3) |
| **Total new** | **33** | |
| **Phase 2 total** | **58** | Including Plan 01 tests (all pass) |

## Deviations from Plan

None -- plan executed exactly as written.

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 | fab37fa | feat(02-02): eQTL harmonization pipeline + tissue-N lookup + download rules |
| 2 | 3b2517f | feat(02-02): run_qtl_coloc.R + qtl_coloc.smk + Snakefile wiring |

## Threat Mitigations Implemented

| Threat | Mitigation | File |
|--------|-----------|------|
| T-02-04 | File size > 0 validation after download | qtl_download.smk |
| T-02-05 | qtl_coloc_id wildcard regex `[A-Za-z0-9_.\-]+` | qtl_coloc.smk |
| T-02-06 | Full local download, no remote tabix | qtl_download.smk |
| T-02-07 | check_dataset(req="LD") + n_snps_overlap >= 50 guard | run_qtl_coloc.R |

## Self-Check: PASSED

All 7 created files verified on disk. Both commits (fab37fa, 3b2517f) found in git log.
