# Phase M1: Sumstats Upgrade and Harmonization — Research

**Researched:** 2026-04-24
**Domain:** Cross-ancestry GWAS summary-statistics harmonization + LDSC bivariate-intercept estimation + Quarto QC + OSF-ready SHA-256 provenance
**Confidence:** HIGH (stack + reusables) / MEDIUM (LDSC 45-trait orchestration — no native --rg-cross in vendored toolkit) / LOW (portal availability of specific files; resolved at fetch-time)

## Summary

M1 lands the 9-trait × up-to-2-ancestry (45-row) public GWAS inventory per `SUMSTATS-UPGRADE.tsv`, harmonizes each source to **GRCh37 canonical** per DEC-2026-04-24 (override of Amendment §3 M1 "GRCh38" wording), and emits two parallel artifact classes per trait × ancestry: a full-coverage `.tsv.bgz + .tbi + .parquet` triple for coloc/fine-mapping/CPASSOC, and an HM3-munged `.sumstats.gz` for LDSC/MTAG. It then builds the 45×45 LDSC bivariate-intercept matrix that MTAG `--overlap` consumes in M2, freezes two SHA-256 manifests (raw for OSF paste, harmonized for pipeline reproducibility), and publishes per-trait Quarto QC HTML reports. Every upstream decision is locked in CONTEXT.md D-01..D-17 — this research is prescriptive for execution, not exploratory.

The phase stack reuses heavily proven Phase 09 pattern: 10-column canonical schema (CHR/BP/SNP/EA/OA/BETA/SE/P/EAF/N), `sumstats_utils.py` helpers (is_palindromic, filter_palindromic_ambiguous with MAF∈[0.48,0.52] exclusion, liftover_to_grch37 with 5% drop ceiling), `pyliftover`-backed coordinate conversion using pre-existing chain `data/external/liftover/hg19ToHg38.over.chain.gz` (reverse chain `hg38ToHg19.over.chain.gz` must be staged — not on disk yet), `harmonize_gbmi.py` reused as-is for asthma, `munge_sumstats_ldsc.py` reused as-is. Seven new per-source harmonizer modules follow the Phase 09 template verbatim.

**The single LOAD-BEARING finding the planner must internalize:** the vendored `tools/ldsc/ldsc.py` (`abdenlab/ldsc-python3` fork pinned in `envs/ldsc_py3.yml`) **does not expose `--rg-cross`**. Its `--rg` flag consumes a comma-separated prefix list where the first entry is "focal" and pairs with each subsequent entry (N-1 pairs per call — star topology, not cross). Populating the full 45×45 matrix (990 unique pairs) therefore requires orchestration: Snakemake emits 44 star-topology `ldsc --rg` invocations (focal_i against traits i+1..45), parses each `.log`, and reduces the union into a 45×45 symmetric wide TSV. CONTEXT.md D-11 reads "single `ldsc.py --rg-cross` invocation"; that phrasing is aspirational and must be revised in the plan. This is the single most important plan-correctness note in M1.

**Primary recommendation:** Plan 5 waves — (Wave 0) tests + env + config + chain-file staging + pre-flight egress checks; (Wave 1) portal fetch + Aragam ZIP unpack + manual-fetch queue driver integration; (Wave 2) 7 new per-source harmonizers + reuse of `harmonize_gbmi.py`; (Wave 3) munge + 45-orchestrated LDSC `--rg` batch + matrix reduction; (Wave 4) Quarto QC per-trait + cross-trait index + SHA-256 manifests + `config/trait_inventory.yaml` freeze. Tasks are harmonize-as-ready (D-14) — 27 files already landed on disk can start Wave 2 immediately; portal + MVP-Giri tiered attempt (D-06/D-07) fire in parallel.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**A. Source locks**

- **D-01 BMI EUR primary source:** Yengo 2018 GIANT+UKB (N=681k EUR, GCST006900, GRCh37, scripted-ready) is primary. Loh 2022 Nat Commun (DOI 10.1038/s41467-022-35553-2, ~1.1M EUR + ~100k AFR multi-ancestry, GRCh38) carried in parallel pending (a) GCST accession resolution and (b) AFR-subset provenance documentation. Both rows stay in SUMSTATS-UPGRADE.tsv; harmonizer emits both; MTAG intercept matrix includes both until one is retired.

- **D-02 GIGASTROKE per-ancestry GCST resolution:** Carter performs ~15-min manual EBI browse of `ebi.ac.uk/gwas/publications/36180795` to pin each (ancestry, subtype) tuple to an integer GCST accession. Resolved values replace `GCST90104540-series` placeholders in TSV via `docs(amendments): GIGASTROKE GCST lock` commit. Snakemake download rule consumes resolved accessions. Unblocks 5 stroke rows (TRANS, EUR, AFR, EAS, SAS).

- **D-03 Aragam 2022 AFR-CAD release policy:** Unzip `Aragam_2022_CARDIoGRAM_CAD_GWAS.zip` at `data/raw/sumstats_v2/Aragam2022/` and enumerate contents. (a) AFR subset present → harmonize as row 23; (b) AFR subset absent → fall back to Klarin 2018 MVP-AFR-CAD (DOI 10.1038/s41591-018-0090-y, N≈8.5k AFR) with one-line Track B methods-disclosure. CAD-AFR slot stays in Amendment §4 locked inventory either way.

- **D-04 GLGC HDL/TG/TC ancestry fanout:** Keep TSV as-is — LDL at 5 ancestries (TRANS+EUR+AFR+EAS+SAS+HIS = 6 rows); HDL/TG/TC at TRANS+EUR+AFR only (9 rows). No expansion. Scripted downloads already landed this set (24 GLGC files).

- **D-05 PAGE BMI-AFR access:** Treat as public sumstat-only per Wojcik 2019 data-availability statement (GCST publication 31217584). Verify at download-time. If portal barrier surfaces, flip `dua_required = yes` and submit dbGaP phs000920 DUA in parallel; M1 proceeds without blocking on this row's DUA in the expected-case path.

**B. MVP Giri AFR-BP critical path**

- **D-06 Tiered strategy:** Primary = public GWAS-Catalog summary-only check at `ebi.ac.uk/gwas/publications/30578418`. Fallback (if primary fails) = AoU Researcher Workbench AFR-SBP derivation on Carter's controlled-tier access (~60-95k AFR WGS post-QC), exporting summary-level effects only per AoU egress policy. **dbGaP phs001672 DUA submission is NOT on primary or fallback path.** "Drop AFR-BP from M1" is explicitly off-table — Amendment §4 locked inventory holds.

- **D-07 Scope expansion — AoU compute in M1:** Confirming the D-06 fallback adds an AoU Researcher Workbench compute path to M1 that DEC-2026-04-22-04 had previously scoped to M3 only. File a new `DEC-2026-04-24` entry capturing this scope expansion before planner lays out tasks. Egress-audit scaffolding from `AOU-LD-PIPELINE.md` §2 P1–P7 is reusable for AFR-SBP derivation with minimal adaptation.

**C. Genome build target**

- **D-08 GRCh37 canonical; liftover two b38 sources:** Keep GRCh37 as canonical analytic plane. Two b38-native sources (Loh 2022 BMI + GBMI asthma) undergo b38→b37 liftover at harmonize step using CrossMap plus HRC rsid remap per SUMSTATS-UPGRADE §6. Everything else stays b37 native. File a new `DEC-2026-04-24` entry overriding Amendment §3 M1 text that reads "Harmonize to GRCh38". Also update `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` if that text asserts b38 (pre-paste check).

**D. Pipeline architecture and deliverable specs**

- **D-09 Canonical harmonized deliverable format:** Dual-emit per trait × ancestry. Primary: `.tsv.bgz` + `.tbi` at `data/processed/sumstats_harmonized/<trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz`. Mirror: `.parquet` at `data/processed/sumstats_harmonized_parquet/<trait>.<ancestry>.<consortium>.<year>.GRCh37.parquet`.

- **D-10 Harmonizer strategy — seven new modules + reuse:** Per-source Python modules following Phase 09 pattern. Seven new:
  - `src/python/harmonize_yengo.py` (GIANT BMI Yengo 2018 + Loh 2022 variant)
  - `src/python/harmonize_diamante.py` (T2D TRANS + EUR + EAS + SAS; AFR/HIS pending)
  - `src/python/harmonize_gigastroke.py` (GWAS-Catalog harmonized format; 5 ancestries)
  - `src/python/harmonize_aragam.py` (CARDIoGRAM zip; TRANS + EUR + EAS; AFR conditional on D-03)
  - `src/python/harmonize_glgc.py` (RVTESTS meta tabix-pre-indexed; handles logTG)
  - `src/python/harmonize_wuttke.py` (CKDGen eGFR TRANS + EUR; Morris 2019 AFR variant)
  - `src/python/harmonize_magic.py` (HbA1c 6 ancestries; rsid-only SNPID → chr:pos crosswalk)
  Existing `harmonize_gbmi.py` reused without change (GBMI asthma slot). Evangelou 2018 SBP-EUR already harmonized (T1 spine); re-verify build + canonical-schema conformance, do not re-run.

- **D-11 LDSC bivariate-intercept matrix scope:** Full 45×45 wide TSV at `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv`. Rows indexed by 45 munged files with `<trait>.<ancestry>.<consortium>.<year>` keys. M2 MTAG wrapper slices matching sub-matrix per run — not M1's job to pre-slice. CONTEXT language says "single `ldsc.py --rg-cross` invocation"; **this is aspirational — vendored tool has no `--rg-cross`. See Pitfall 1 below for the orchestrated-star workaround.**

- **D-12 Per-trait QC report format:** Quarto (`.qmd` → HTML) per trait, rendered under Snakemake with `quarto render`. Mixes R (tidyverse + ggplot2 for MAF histogram, LDSC intercept plot, Manhattan, QQ, locuszoom of 7 control loci) with Python (pandas for variant counts, PASS/FAIL table, checksum display). One HTML per trait at `data/processed/sumstats_harmonized/qc_log/<trait>.qc.html` plus cross-trait `index.html`. QC checklist items 1–9 from SUMSTATS-UPGRADE §7 all surface.

- **D-13 SHA-256 manifest semantics:** Two manifests. **Primary** (OSF-paste): `data/raw/sumstats_v2/sha256_manifest.tsv` covering every raw download under `data/raw/sumstats_v2/**/*`. **Secondary** (pipeline-repro): `data/processed/sumstats_harmonized/sha256_manifest.tsv` covering harmonized outputs, drifts with harmonizer code versions.

- **D-14 Parallelization policy:** Harmonize-as-ready. Snakemake per-source-file → per-harmonized-file → per-munged-file. As Carter resolves portal fetches, DAG re-triggers. 45×45 LDSC matrix rule gates on all 45 munged files.

- **D-15 HapMap3 vs full-coverage duality:** Emit both artifact classes per trait × ancestry — full-coverage (`.tsv.bgz` + `.parquet`) feeds coloc/fine-mapping/CPASSOC; HM3-munged (`.sumstats.gz`) feeds LDSC/MTAG. Both are M1 deliverables; neither optional.

**F. M1 → M2 handoff contract**

- **D-16 Per-trait munged file naming:** Lowercase-trait-token-first dotted convention: `<trait>.<ancestry>.<consortium>.<year>.sumstats.gz`. Trait tokens: `bmi, t2d, sbp, stroke, asthma, cad, ldl, hdl, tg, tc, egfr, hba1c`. These tokens are primary keys of `config/trait_inventory.yaml`. Dotted separator avoids underscore-within-token ambiguity (e.g. consortium = `CARDIoGRAM-C4D-MVP`).

- **D-17 MTAG per-run trait grouping:** Deferred to M2 discuss-phase.

### Claude's Discretion

- Exact schema of `config/trait_inventory.yaml` — derived from D-16 trait tokens and 45-row TSV; must include at minimum `{trait, ancestry, consortium, year, source_url, build, harmonized_path, munged_path, parquet_path, n_total, n_cases, n_controls, sha256_raw, sha256_harmonized, ldsc_intercept, ldsc_h2, qc_report_path, qc_status}`.
- Snakemake rule layout across files (suggested: `workflow/rules/m1_download.smk`, `m1_harmonize.smk`, `m1_munge.smk`, `m1_ldsc_rg.smk`, `m1_qc.smk`).
- Conda environment partitioning.
- LSF queue selection per rule (follow `feedback_lsf_queues` memory).
- CPASSOC variant-set alignment algorithm (arguably M2's job but M1 harmonizer should emit variant-universe helper).
- Parquet region-slice helper signature for coloc readers.
- Retry / re-download policy if portal-fetched files fail checksum validation on later re-run.

### Deferred Ideas (OUT OF SCOPE)

- MTAG per-run trait grouping topology (D-17; to M2 discuss).
- DIAMANTE AFR + HIS strata (DIAGRAM gate on manuscript acceptance; quarterly recheck; carry placeholders).
- Aragam author email for AFR file (last-resort contingent under D-03).
- dbGaP phs001672 DUA submission (de-prioritized per D-06).
- Q5 MAGIC FTP port-21 egress test from NCSU HPC (planner pre-flight check).

### NON-goals for M1 (per phase description; do NOT research or plan)

- Running MTAG `--overlap`.
- Running CPASSOC SHom/SHet.
- PLINK clumping.
- Union-region-list construction.
- Novelty extraction.

All M2+.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-TRAIT-INVENTORY | Track B analyzes 9 traits × up to 2 ancestries per Amendment §4; `config/trait_inventory.yaml` enumerates; harmonized sumstats exist per (trait, ancestry) before M2. | D-16 naming convention + discretion-area YAML schema + D-14 harmonize-as-ready enables incremental satisfaction; 27/45 source files already landed. |
| REQ-SNAKEMAKE-CI | End-to-end toy 3-locus CI; envs pinned in `envs/*.yml`; every new rule registers into skeleton. | Proposed per-rule-family env partitioning (`envs/m1-*.yml`); 27 landed files + Phase 09 harmonizer reuse mean toy-3-locus smoke is feasible on Wave 0 itself; existing toy at `tests/toy_3locus/`. |
| REQ-PUBLIC-DATA-ONLY | Every data source has `license` + `public: true` fields in `config/data_sources.yaml`. DUAs count as public for academic researchers. | D-06 explicitly avoids dbGaP DUA for MVP-Giri; D-05 flips PAGE only if portal barrier appears; D-07 AoU controlled-tier summary-only export complies (established by REQ-AOU-LD-EGRESS precedent); `SUMSTATS-UPGRADE.tsv` has `dua_required` column that feeds directly into the `license` emit. |
| REQ-PATH-PARAMETERIZATION | All paths via `config/pipeline.yaml`; `grep -r "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config` returns 0 matches. | Every path in D-09, D-11, D-12, D-13, D-16 routes through config; Phase 09 pattern for `config["paths"]["raw_sumstats"]`/`config["paths"]["harmonized_sumstats"]` is already in `src/snakemake/rules/sumstats.smk` and extends cleanly for v2. |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| python | 3.11 (conda `smoke_dev` at `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11`) | Harmonizer scripts; Snakemake orchestration | [VERIFIED: project memory `project_python_311_pin.md`] Snakemake 7.32.4 requires Python 3.11. |
| snakemake | 7.32.4 pinned in `envs/python_stats.yml` | DAG-based pipeline orchestration | [VERIFIED: `envs/python_stats.yml` line 14] Pre-pivot spine standard. |
| pandas | 2.2.3 | Sumstats DataFrame operations | [VERIFIED: `envs/python_stats.yml`] Phase 09 harmonizers use pandas throughout. |
| pyarrow | 18.1.0 | Parquet read/write for `.parquet` mirror artifact per D-09 | [VERIFIED: `envs/python_stats.yml` line 18] Enables `df.to_parquet()` + `pyarrow.dataset` region slicing. |
| htslib | 1.21 (provides `bgzip`, `tabix`) | Block-gzip compression + tabix index for `.tsv.bgz` primary artifact | [VERIFIED: `envs/python_stats.yml` line 23] Standard GWAS sumstats serialization. |
| pyliftover | installed in `smoke_dev` env — `import pyliftover; print('pyliftover ok')` verified | Pure-Python GRCh38→GRCh37 coordinate lift in `src/python/liftover.py:liftover_coordinates` | [VERIFIED: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3 -c "import pyliftover; print('ok')"` returns "pyliftover ok"] Used by `sumstats_utils.liftover_to_grch37` with 5% drop ceiling. |
| CrossMap | v0.7+ in `hlp_crossmap` conda env at `/rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/CrossMap` | UCSC chain-based liftover CLI (alternative to UCSC liftOver binary for batch mode) | [VERIFIED: `ls /rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/CrossMap` returns CrossMap] CrossMap is the Python-native liftOver; Carter has a dedicated env. |
| LDSC (abdenlab/ldsc-python3 fork) | Python 3.11-compatible fork pinned in `envs/ldsc_py3.yml` via `ldsc-python3 @ git+https://github.com/abdenlab/ldsc-python3.git` | HapMap3 sumstats munging + pairwise bivariate-intercept regression for MTAG --overlap matrix | [VERIFIED: `envs/ldsc_py3.yml` line 21; `tools/ldsc/README.md` documents abdenlab fork + Poetry install] Statistical logic unchanged vs Bulik-Sullivan 2015; only Python-version port. |
| quarto | system-level binary (CLI: `quarto render`) | Mixed-engine (R + Python) QC report rendering per D-12 | [CITED: quarto.org — supersedes Rmd for multi-engine docs] Per D-12 decision. |
| R + tidyverse + ggplot2 + qqman + locuszoomr | R 4.x in `envs/m1-qc.yml` (new) | Manhattan, QQ, MAF hist, locuszoom-7-control-loci plots inside Quarto | [CITED: standard GWAS QC R stack] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| curl + xargs -P 5 | system | Parallel portal downloads per Carter `feedback_parallel_downloads` memory | Any HTTP/FTP fetch — already the proven pattern in `bin/download_sumstats_v2.sh` |
| requests | 2.32.3 from `python_stats.yml` | Python-side URL fetch with retries (inside Snakemake `run:` blocks) | `src/snakemake/rules/sumstats.smk` uses `requests.get(meta["url"], stream=True)` already |
| PyYAML | 6.0.2 | `config/trait_inventory.yaml` write + Snakemake config load | All config |
| sha256sum (coreutils) | system | Primary + secondary SHA-256 manifests per D-13 | Two scheduled manifest-freeze rules |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pyliftover + `sumstats_utils.liftover_to_grch37` | CrossMap CLI batch | CrossMap is faster on big files (BED-batch) but adds subprocess overhead and chain-file path coupling; pyliftover is already proven in 4 Phase 09 harmonizers; recommend pyliftover for Loh 2022 BMI + GBMI asthma (2 files only). **CrossMap is the documented recommendation in SUMSTATS-UPGRADE §6** — keep CrossMap available as fallback in `envs/m1-harmonize.yml` but default to pyliftover via the existing helper. |
| Quarto | Rmd | Quarto is the forward path; D-12 locked. |
| abdenlab ldsc-python3 fork | Original Bulik-Sullivan LDSC (Python 2.7) | `envs/ldsc_py3.yml` already pins the fork; consortium LDSC is Py2.7 and incompatible with the rest of the Python-3.11 stack. Fork is statistically unchanged [CITED: `envs/ldsc_py3.yml` line 4 comment "without altering statistical logic"]. |

**Installation:** All envs already exist or are trivial extensions. No new package installations required — verified `pyliftover`, `CrossMap`, `snakemake`, `pyarrow` all present on disk.

**Version verification (2026-04-24 against conda envs on disk, `npm view` not applicable — Python ecosystem):**

- `pandas==2.2.3` — verified in `envs/python_stats.yml` [VERIFIED]
- `pyarrow==18.1.0` — verified in `envs/python_stats.yml` [VERIFIED]
- `snakemake==7.32.4` — verified in `envs/python_stats.yml`; Carter's `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` also 7.32.4 [VERIFIED]
- `htslib==1.21` — verified [VERIFIED]
- `pyliftover` — installed in `smoke_dev` env (version unpinned; `python -c "import pyliftover"` succeeds) [VERIFIED]
- LDSC fork — `git+https://github.com/abdenlab/ldsc-python3.git` at whatever HEAD the lockfile captures [VERIFIED via `envs/ldsc_py3.yml` pip section]

## Architecture Patterns

### Recommended Project Structure

```
coloc_analysis/
├── bin/
│   └── download_sumstats_v2.sh              # existing; extend for portal sources per D-14
├── config/
│   ├── pipeline.yaml                         # path parameterization (REQ-PATH-PARAMETERIZATION)
│   ├── trait_inventory.yaml                  # NEW — M1 deliverable per D-16 + REQ-TRAIT-INVENTORY
│   ├── datasets.yaml                         # existing; extend with v2 rows
│   └── cluster_lsf.yaml                      # existing; LSF queue + mem + wall-time per rule
├── envs/
│   ├── m1-download.yml                       # NEW — curl, xargs, requests; lightweight
│   ├── m1-harmonize.yml                      # NEW — pandas, pyarrow, pyliftover, CrossMap
│   ├── m1-munge.yml                          # NEW or alias of ldsc_py3 — LDSC munge_sumstats.py
│   ├── m1-ldsc-rg.yml                        # alias of envs/ldsc_py3.yml — LDSC rg regression
│   ├── m1-qc.yml                             # NEW — quarto + R tidyverse + ggplot2 + qqman + locuszoomr
│   ├── ldsc_py3.yml                          # existing; reuse
│   └── python_stats.yml                      # existing; reuse (Snakemake orchestrator)
├── src/
│   ├── python/
│   │   ├── sumstats_utils.py                 # existing; 10-col schema, palindromic, liftover_to_grch37
│   │   ├── liftover.py                       # existing; pyliftover wrapper
│   │   ├── harmonize_gbmi.py                 # existing — REUSED AS-IS for asthma
│   │   ├── harmonize_finngen.py              # existing — pattern template only
│   │   ├── harmonize_bbj.py                  # existing — pattern template only
│   │   ├── harmonize_mvp.py                  # existing — pattern template only
│   │   ├── harmonize_yengo.py                # NEW — BMI (Yengo 2018 + Loh 2022 two-variant)
│   │   ├── harmonize_diamante.py             # NEW — T2D 4 ancestries (AFR/HIS deferred)
│   │   ├── harmonize_gigastroke.py           # NEW — stroke 5 ancestries
│   │   ├── harmonize_aragam.py               # NEW — CAD 3+1 ancestries (AFR conditional)
│   │   ├── harmonize_glgc.py                 # NEW — lipids 4 traits x {4/3} ancestries
│   │   ├── harmonize_wuttke.py               # NEW — eGFR TRANS+EUR + Morris2019 AFR
│   │   ├── harmonize_magic.py                # NEW — HbA1c 6 ancestries + rsid→chr:pos
│   │   ├── munge_sumstats_ldsc.py            # existing — REUSED AS-IS
│   │   ├── build_trait_inventory.py          # NEW — emit config/trait_inventory.yaml from TSV + SHA manifest
│   │   ├── reduce_ldsc_rg_matrix.py          # NEW — parse 44 star-topology .log files → 45×45 wide TSV
│   │   └── freeze_sha256_manifest.py         # NEW — walk raw/harmonized dirs, emit sorted .tsv
│   ├── snakemake/
│   │   ├── rules/
│   │   │   ├── m1_download.smk               # NEW — scripted + portal-gated dispatch
│   │   │   ├── m1_harmonize.smk              # NEW — per-source harmonizer calls + liftover
│   │   │   ├── m1_munge.smk                  # NEW — canonical TSV → HM3-munged .sumstats.gz
│   │   │   ├── m1_ldsc_rg.smk                # NEW — 44 star-topology rg calls + reducer
│   │   │   ├── m1_qc.smk                     # NEW — Quarto render per-trait + index
│   │   │   └── sumstats.smk                  # existing; unchanged (pre-pivot pattern)
│   │   └── Snakefile                         # include m1_*.smk
│   └── R/
│       └── qc/
│           └── m1_qc_report.qmd              # NEW — per-trait Quarto template
├── data/
│   ├── raw/sumstats_v2/
│   │   ├── GLGC2021/                         # 24 files landed
│   │   ├── CKDGen2019/                       # 2 files landed
│   │   ├── Aragam2022/                       # 1 ZIP; must unzip per D-03
│   │   ├── GIANT2018/                        # PORTAL — 1 expected
│   │   ├── Loh2022/                          # PORTAL — 2 expected
│   │   ├── PAGE2019/                         # PORTAL — 1 expected
│   │   ├── DIAMANTE2022/                     # PORTAL — 4 expected (AFR/HIS deferred)
│   │   ├── GIGASTROKE2022/                   # PORTAL — 5 expected
│   │   ├── GBMI2022/                         # PORTAL — 3 expected
│   │   ├── MAGIC2021/                        # PORTAL — 6 expected
│   │   ├── MVP2019/BP/AFR/                   # TIERED — D-06 primary/fallback
│   │   └── sha256_manifest.tsv               # NEW — FROZEN for OSF paste per D-13
│   ├── processed/
│   │   ├── sumstats_harmonized/
│   │   │   ├── <trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz   # D-09 primary
│   │   │   ├── <trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz.tbi
│   │   │   ├── qc_log/
│   │   │   │   ├── <trait>.qc.html                                      # D-12 per-trait
│   │   │   │   └── index.html                                           # D-12 cross-trait
│   │   │   └── sha256_manifest.tsv                                      # D-13 secondary
│   │   ├── sumstats_harmonized_parquet/
│   │   │   └── <trait>.<ancestry>.<consortium>.<year>.GRCh37.parquet   # D-09 mirror
│   │   └── ldsc_overlap/
│   │       ├── munged/
│   │       │   └── <trait>.<ancestry>.<consortium>.<year>.sumstats.gz  # D-16 HM3-munged
│   │       ├── rg_logs/
│   │       │   └── focal_<i>_vs_<j..45>.log                             # 44 star-calls
│   │       └── bivariate_intercept_matrix_2026-04.tsv                   # D-11 45×45 wide TSV
│   └── external/
│       └── liftover/
│           ├── hg19ToHg38.over.chain.gz      # on disk
│           └── hg38ToHg19.over.chain.gz      # MUST STAGE IN WAVE 0 (not yet present)
├── tests/
│   ├── toy_3locus/                           # existing; extend for M1 smoke
│   └── m1/
│       ├── test_harmonize_yengo.py           # NEW
│       ├── test_harmonize_diamante.py        # NEW
│       ├── test_harmonize_gigastroke.py      # NEW
│       ├── test_harmonize_aragam.py          # NEW
│       ├── test_harmonize_glgc.py            # NEW
│       ├── test_harmonize_wuttke.py          # NEW
│       ├── test_harmonize_magic.py           # NEW
│       ├── test_reduce_ldsc_rg_matrix.py     # NEW — matrix-assembly from 44 logs
│       └── test_build_trait_inventory.py     # NEW — schema validation
└── tools/ldsc/                                # existing vendored abdenlab fork
```

### Pattern 1: Harmonize-then-unify per-source module

**What:** Each source (Yengo, DIAMANTE, GIGASTROKE, Aragam, GLGC, Wuttke, MAGIC, GBMI) has a Python module that reads the raw format, applies source-specific column mapping, optional liftover, and palindromic filter; emits canonical 10-column TSV.

**When to use:** Every sumstats source in M1. Reuses `sumstats_utils.py` helpers so individual modules stay ~100 lines each.

**Example:** See `src/python/harmonize_gbmi.py` (121 lines — REUSED AS-IS for M1 asthma). The column map + `filter_palindromic_ambiguous` + canonical schema pattern is the template.

```python
# Source: src/python/harmonize_gbmi.py (existing; lines 87-122)
CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
col_map = {
    "CHR": "CHR", "POS": "BP", "rsid": "SNP", "REF": "OA", "ALT": "EA",
    f"{prefix}_beta": "BETA", f"{prefix}_sebeta": "SE", f"{prefix}_pval": "P",
    f"{prefix}_AF": "EAF", f"{prefix}_sample_N": "N",
}
# B-2 guard: fail loudly if the expected per-ancestry prefix is absent.
missing = [src for src in col_map if src not in df.columns]
if missing:
    raise ValueError(f"... expected columns {sorted(col_map.keys())} but file is "
                     f"missing {missing}. Found columns: {sorted(df.columns.tolist())}.")
df = df[list(col_map.keys())].rename(columns=col_map)
df = df[CANONICAL_COLS]
df = _su.filter_palindromic_ambiguous(df)  # RESEARCH pitfall #2 — MAF ∈ [0.48, 0.52] exclusion
```

### Pattern 2: Liftover via sumstats_utils.liftover_to_grch37 (pyliftover-backed with 5% drop ceiling)

**What:** Two b38-native sources (Loh 2022 BMI rows 3 + 4 of TSV, GBMI asthma rows 18 + 19 + 20) get lifted to GRCh37 via the shared helper. Drop-rate ceiling **hard-fails at >5%** to prevent the Phase 09 silent-drop class of bugs (RESEARCH pitfall #1).

**When to use:** Inside `harmonize_yengo.py` on the Loh 2022 path and inside `harmonize_gbmi.py` **only if** the caller opts in (the existing GBMI harmonizer does NOT liftover — comment line 116 says "GBMI flagship releases are already GRCh37"; but the M1 release is GRCh38 per TSV row 18 build column, so a lift step must be added — see Pitfall 5).

**Example:**

```python
# Source: src/python/sumstats_utils.py lines 164-252 (existing)
from sumstats_utils import liftover_to_grch37

# Inside harmonize_yengo.py on the Loh 2022 variant:
df_b37, qc = liftover_to_grch37(
    df_b38,
    chain_file="data/external/liftover/hg38ToHg19.over.chain.gz",
    chr_col="CHR",
    bp_col="BP",
    max_drop_rate=0.05,   # hard fail on >5% drop
)
# qc contains: n_input, n_lifted, n_dropped, n_dropped_unknown_chrom,
# n_dropped_liftover_failed, drop_rate
```

### Pattern 3: Path-parameterized Snakemake rule with wildcard-tokenized naming (D-16)

**What:** Every M1 rule uses `{trait}.{ancestry}.{consortium}.{year}` wildcards with lowercase trait tokens matching YAML keys. Driven by `config["paths"][...]` for REQ-PATH-PARAMETERIZATION.

**When to use:** Every `m1_*.smk` rule.

**Example (skeleton — planner to flesh):**

```python
# workflow/rules/m1_harmonize.smk (NEW; modeled on existing src/snakemake/rules/sumstats.smk)
import os
RAW = os.path.join(config["paths"]["raw_sumstats_v2"],
                   "{consortium}{year}/{trait}/{ancestry}/{filename}")
HARM = os.path.join(config["paths"]["harmonized_sumstats"],
                    "{trait}.{ancestry}.{consortium}.{year}.GRCh37.tsv.bgz")
PARQ = os.path.join(config["paths"]["harmonized_parquet"],
                    "{trait}.{ancestry}.{consortium}.{year}.GRCh37.parquet")

rule harmonize_yengo_bmi_eur:
    input:
        raw = RAW.replace("{consortium}", "GIANT").replace("{year}", "2018").replace(
              "{trait}", "bmi").replace("{ancestry}", "EUR")
    output:
        tsv_bgz = HARM.replace("{consortium}", "GIANT").replace("{year}", "2018").replace(
                  "{trait}", "bmi").replace("{ancestry}", "EUR"),
        parquet = PARQ.replace("{consortium}", "GIANT").replace("{year}", "2018").replace(
                  "{trait}", "bmi").replace("{ancestry}", "EUR"),
    conda: "../envs/m1-harmonize.yml"
    resources: mem_mb=8000
    threads: 2
    shell:
        "python src/python/harmonize_yengo.py "
        "--input {input.raw} --output {output.tsv_bgz} --parquet {output.parquet} "
        "--trait bmi --ancestry EUR --year 2018"
```

### Pattern 4: LDSC rg orchestration (star-topology, 44 calls, matrix reducer)

**What:** The vendored `ldsc.py --rg` takes a comma-separated trait list where the **first** trait is pairwise-compared against each of the **remaining** traits (N-1 pairs per call — star pattern from the focal). To populate the full C(45,2)=990-pair upper triangle, Snakemake fires 44 `ldsc.py --rg` invocations: focal = trait 1 vs traits 2..45 → 44 pairs; focal = trait 2 vs traits 3..45 → 43 pairs; ...; focal = trait 44 vs trait 45 → 1 pair. Total 44+43+...+1 = 990 pairs. Each call emits one `.log` with a pairwise table. A Python reducer parses all 44 logs, extracts the intercept column, builds the 45×45 symmetric wide TSV.

**When to use:** The single most important M1 rule (`m1_ldsc_rg.smk`). Total compute ≈ 990 × per-pair-time. LDSC pairwise rg on HM3 snp set (~1.2M variants, w_hm3.snplist) is ~5-20 min per pair on a single core → ~3-11 hours per focal-star call (some star calls are ~44 pairs, some just 1 pair) → total serial run is ~100-300 hours; parallelizable by focal-trait (44 jobs fire simultaneously on LSF long queue).

**Example (Python-level LDSC invocation pattern):**

```bash
# Source: vendored tools/ldsc/ldsc.py lines 608-613 (verified from source)
# --rg help: "Comma-separated list of prefixes of .chisq filed for genetic correlation estimation."

# Star-call for focal_idx=0 (e.g. bmi.EUR.GIANT.2018):
python tools/ldsc/ldsc.py \
    --rg data/processed/ldsc_overlap/munged/bmi.EUR.GIANT.2018.sumstats.gz,\
data/processed/ldsc_overlap/munged/bmi.AFR.GIANT.2022.sumstats.gz,\
data/processed/ldsc_overlap/munged/bmi.AFR.PAGE.2019.sumstats.gz,\
...[all 44 remaining munged files comma-separated]...\
data/processed/ldsc_overlap/munged/hba1c.HIS.MAGIC.2021.sumstats.gz \
    --ref-ld-chr data/external/ldscore/eur_w_ld_chr/ \
    --w-ld-chr   data/external/ldscore/eur_w_ld_chr/ \
    --out data/processed/ldsc_overlap/rg_logs/focal_00_bmi.EUR.GIANT.2018
```

LD panel selection per pair (D-11):
- EUR-EUR pairs: 1KG Phase 3 b37 EUR baseline-LD (standard LDSC release at `https://data.broadinstitute.org/alkesgroup/LDSCORE/eur_w_ld_chr.tar.bz2` per vendored README line 297).
- AFR-AFR pairs: 1KG Phase 3 b37 AFR (downloadable from Pan-UKBB LDSC or HGDP+1kG release; Phase 01-03-PLAN laid the pattern for AFR LD panel download).
- Cross-ancestry pairs (EUR-AFR, EUR-EAS, etc.): use the shared-ancestry LDSC release (Galinsky et al "shared ancestry" scores) or **PopCorn** as fallback per CONTEXT.md D-11. LDSC itself doesn't do rigorous cross-ancestry rg out of the box; for this research phase the 45×45 matrix just needs the **bivariate intercept** (not rg), and the intercept is interpretable regardless of LD-panel mismatch as long as both files went through the same HM3 filter. CONTEXT.md D-11 is correct that the cross-ancestry fallback is PopCorn; the planner should note this in VALIDATION.md.

**Reducer sketch (`src/python/reduce_ldsc_rg_matrix.py` — NEW):**

```python
# NEW file; parses 44 star-call logs → 45×45 symmetric intercept matrix
import re, pandas as pd
from pathlib import Path

TRAIT_KEY_RE = re.compile(r"(?P<trait>\w+)\.(?P<ancestry>[A-Z]+)\."
                          r"(?P<consortium>[\w-]+)\.(?P<year>\d{4})\.sumstats\.gz")

def parse_rg_log(log_path: Path) -> pd.DataFrame:
    """Extract the pairwise rg table from an LDSC .log.

    The LDSC .log prints a 'Summary of Genetic Correlation Results' table with
    columns: p1, p2, rg, se, z, p, h2_obs, h2_obs_se, h2_int, h2_int_se,
    gcov_int, gcov_int_se. We want gcov_int (bivariate intercept).
    """
    text = log_path.read_text()
    # Table starts after 'Summary of Genetic Correlation Results' header
    # Match per-row: 'file1.sumstats.gz file2.sumstats.gz rg se z p h2a h2a_se h2b h2b_se gcov_int gcov_int_se'
    rows = []
    in_table = False
    for line in text.splitlines():
        if "Summary of Genetic Correlation Results" in line:
            in_table = True; continue
        if in_table and line.strip() and not line.startswith(("p1", "Analysis", "Total")):
            parts = line.split()
            if len(parts) >= 12:
                rows.append({
                    "p1": parts[0], "p2": parts[1],
                    "rg": float(parts[2]), "rg_se": float(parts[3]),
                    "gcov_int": float(parts[10]),  # bivariate intercept
                    "gcov_int_se": float(parts[11]),
                })
    return pd.DataFrame(rows)

def build_intercept_matrix(log_dir: Path, trait_keys: list[str]) -> pd.DataFrame:
    """Aggregate 44 star-call logs into a 45×45 symmetric intercept matrix."""
    mat = pd.DataFrame(1.0, index=trait_keys, columns=trait_keys)  # diag defaults to 1.0
    for log_path in sorted(log_dir.glob("focal_*.log")):
        df = parse_rg_log(log_path)
        for _, row in df.iterrows():
            k1 = Path(row["p1"]).name.replace(".sumstats.gz", "")
            k2 = Path(row["p2"]).name.replace(".sumstats.gz", "")
            mat.at[k1, k2] = row["gcov_int"]
            mat.at[k2, k1] = row["gcov_int"]  # symmetric
    return mat
```

### Anti-Patterns to Avoid

- **Re-implementing `filter_palindromic_ambiguous` or `liftover_to_grch37` inside new harmonizer modules.** `sumstats_utils.py` has both; reuse via `import sumstats_utils as _su`. Deviating from the shared helper recreates the exact class of bugs Phase 09 caught (silent liftover drops, palindromic strand flips).
- **Baking absolute paths into harmonizer modules.** All paths go through Snakemake wildcards + `config["paths"][...]`. REQ-PATH-PARAMETERIZATION test greps `src/` for hardcoded `/share/`, `/rs1/`, `/gpfs_common/` — must return 0.
- **Serial LDSC rg via 990 independent `--rg t1,t2` calls.** This is ~2× slower (each call does its own `--merge-alleles` expansion and LD-score load) and harder to audit. Use the 44 star-calls pattern.
- **Reading Parquet via pandas `read_parquet` for region slicing** — pandas pulls the full file into memory. Use `pyarrow.dataset` or `pyarrow.parquet.ParquetFile.read_row_group` for chromosome-range slicing in the coloc/CPASSOC consumer; this is the discretion-item "parquet region-slice helper signature" — recommend `pyarrow.dataset.dataset(path).to_table(filter=(pc.field("CHR")==chrom) & (pc.field("BP")>=start) & (pc.field("BP")<=end))`.
- **Committing `data/` files to git.** Verified `.gitignore` already excludes `data/`. For OSF amendment, the hash manifest (`data/raw/sumstats_v2/sha256_manifest.tsv`) must be copy-committed to a non-gitignored location (recommend `.planning/amendments/sha256_manifest_m1_frozen.tsv`) so it survives in-repo alongside the OSF paste.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GRCh38→GRCh37 coordinate liftover | Custom chr:pos chain parser | `sumstats_utils.liftover_to_grch37` (pyliftover-backed) | Handles edge cases (chrMT, chr0, unmapped intervals); hard-enforces 5% drop ceiling per RESEARCH pitfall #1. |
| Palindromic / strand-ambiguous SNP handling | Custom allele-pair exclusion | `sumstats_utils.filter_palindromic_ambiguous` with MAF∈[0.48,0.52] | Phase 09 already trained the exclusion band; deviating regenerates the strand-flip bug class. |
| LDSC munging from canonical 10-col TSV | Custom column-renaming wrapper | `src/python/munge_sumstats_ldsc.py` (existing — reused as-is per D-10) | Handles binary-trait N_eff, chr:pos→rsID lookup against 1000G bim, REF/ALT absence fallback (dummy A/G avoids LDSC strand-drop). |
| HapMap3 SNP filtering for LDSC | Custom HM3 intersection | LDSC `munge_sumstats.py --merge-alleles w_hm3.snplist` | Standard. Vendored `tools/ldsc/munge_sumstats.py:498` accepts `--merge-alleles` argument. |
| Bivariate-intercept regression for MTAG `--overlap` | Custom IV-regression | LDSC `ldsc.py --rg` star-pattern | 44 orchestrated calls cover all 990 pairs; bivariate intercept is the `gcov_int` column in the rg log. |
| Parallel portal downloads | Custom queue | `curl ... \| xargs -P 5 -n 1` per Carter `feedback_parallel_downloads` memory; extend `bin/download_sumstats_v2.sh` manifest | Proven pattern; 27 files landed without incident. |
| Quarto HTML assembly | Custom HTML templating | `quarto render <trait>.qmd --output-dir qc_log/` | D-12 locked; mixed R+Python engine. |
| LSF wall-time/memory/queue selection | Hardcoded `-W`/`-q` in rules | `config/bsub_wrapper.sh` (existing) sets queue max wall per `feedback_lsf_queues` memory | Already ships; uses `LSF_UNIT_FOR_LIMITS=GB` and sets wall = queue max (serial=5760, long=14400, standard=2880 min). |
| Variant-count / MAF / λ_GC / intercept sanity checks | Custom QC script | Existing Phase 1 Quarto dashboard pattern (`01-05-PLAN.md`); extend `src/R/qc/` with a `m1_qc_report.qmd` template consuming pandas-emitted JSON from harmonizer stats + LDSC `.log` h2 intercept | The 9-item QC checklist from SUMSTATS-UPGRADE §7 maps directly to report sections. |
| SHA-256 manifest | Custom hashing loop | `find data/raw/sumstats_v2 -type f \| sort \| xargs -n 100 sha256sum > manifest.tsv` followed by pandas sort | Canonical. Captures file path + hash in reproducible sort order. |

**Key insight:** M1 is ~70% code reuse. Seven new harmonizer modules + 1 reducer + 1 inventory builder + 1 manifest freezer = ~1,200 LoC net, almost all copy-adapt from Phase 09 and Phase 1 patterns. The hard parts (liftover edge cases, palindromic MAF band, LDSC P3 port, path parameterization, LSF wall-time auto-detection) are already solved.

## Runtime State Inventory

> This phase is not a rename/refactor, but surfaces a runtime-state audit because M1 adds new data classes and config contracts that downstream M2+ consumers depend on.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | 27 files already landed under `data/raw/sumstats_v2/{GLGC2021,CKDGen2019,Aragam2022}/` (40.4 GB total); 11 pre-pivot harmonized sumstats at `data/processed/sumstats_harmonized/{asthma,bmi,hypertension,stroke,...}.{EUR,AFR}.tsv.bgz`; 8 pre-pivot munged files at `results/pathway/ldsc_partitioned/munged/*.sumstats.gz` (use as sanity-check baselines for the new M1 munge pipeline — they used a different naming convention with underscore separator and no consortium/year token). | (a) M1 uses new `<trait>.<ancestry>.<consortium>.<year>` dotted naming; do NOT overwrite pre-pivot files. (b) Evangelou 2018 SBP-EUR at `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz` — verify build + canonical-schema conformance per D-10 note; copy/rename to `data/processed/sumstats_harmonized/sbp.EUR.Evangelou.2018.GRCh37.tsv.bgz` for consistency. |
| Live service config | None. M1 is pure local/HPC — no external service registrations. | None. |
| OS-registered state | None. M1 adds no daemons, tasks, systemd units. Snakemake jobs are ephemeral LSF bsub submissions. | None. |
| Secrets / env vars | No new secrets. Existing `LSF_UNIT_FOR_LIMITS=GB` env var set by `bsub_wrapper.sh` per `feedback_lsf_queues`. If D-06/D-07 AoU fallback fires, AoU workspace token lives inside the AoU Researcher Workbench — NOT exported to GPFS. | None — verified AoU egress scaffolding keeps auth inside AoU per `AOU-LD-PIPELINE.md §7`. |
| Build artifacts / installed packages | pyliftover, CrossMap, pyarrow, snakemake, pandas, htslib, LDSC-py3 fork all already installed in conda envs on `/rs1/` (verified by `ls` and `python -c "import pyliftover"` on 2026-04-24). | None — envs are ready. `envs/m1-*.yml` stubs can be materialized via `conda env create -f` on first Snakemake `--use-conda` run. |

**Nothing found in 3 of 5 categories** — verified by direct `find`/`ls`/`grep` inspection. The one consequential finding is the pre-pivot harmonized artifacts under `data/processed/sumstats_harmonized/`: they use the **old** naming convention `<trait>.<ancestry>.tsv.bgz`, which clashes with M1's new `<trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz`. The planner must decide whether to symlink old→new names for backward compat (Phase 09 downstream rules expect the old pattern) or let them coexist. Recommend coexist — M1 emits new, pre-pivot stays until downstream (Track A finalization) references are explicitly re-pointed.

## Common Pitfalls

### Pitfall 1: **LDSC `--rg-cross` does not exist in the vendored toolkit**

**What goes wrong:** CONTEXT.md D-11 says "Computation: single `ldsc.py --rg-cross` invocation over the trait list (990 pairs)." This is **not a real flag** in the vendored `abdenlab/ldsc-python3` fork (verified: `grep -n "rg-cross" tools/ldsc/ldsc.py` → 0 matches; `--rg` at line 609 takes a comma-separated list that runs star-topology, not cross).

**Why it happens:** CONTEXT author conflated the conceptual "cross-product of rg" with a specific CLI flag that was added in an unofficial fork or never existed.

**How to avoid:** Plan the 45×45 matrix as **44 star-topology `ldsc.py --rg` calls** plus a reducer. See Pattern 4 above. This is the canonical approach in the LDSC rg literature (Bulik-Sullivan 2015 Atlas paper used exactly this pattern before `--rg-cross` was a concept).

**Warning signs:** Any plan-text that says "single LDSC invocation for all 990 pairs" — that path does not exist in the installed toolkit and will fail at Wave 3. The Wave 0 smoke test should include a 2-trait `ldsc.py --rg` call against the pre-pivot munged files at `results/pathway/ldsc_partitioned/munged/bmi_EUR.sumstats.gz,t2d_EUR.sumstats.gz` to verify the CLI shape before 44-way parallel execution.

### Pitfall 2: **MAGIC FTP port-21 egress from NCSU HPC not verified**

**What goes wrong:** MAGIC 2021 HbA1c FTP URLs use `ftp://web-ftp.ex.ac.uk/docs/downloads/`. Many HPC clusters block outbound port 21 (passive or active FTP). If NCSU HPC blocks it, the scheduled Snakemake fetch fails silently (or with a 5-minute timeout per `curl --connect-timeout 30 --max-time 7200` pattern in `download_sumstats_v2.sh`).

**Why it happens:** Institutional firewalls drop FTP because of NAT traversal issues and security posture updates since 2020.

**How to avoid:** **Wave 0 pre-flight check**: `curl --connect-timeout 30 --head "ftp://web-ftp.ex.ac.uk/docs/downloads/"` on a compute node (not login node — they often differ). If it returns 0-exit + headers, FTP is open. If timeout / rc!=0, fall back to either (a) EBI mirror if one exists, (b) login-node proxy with `--proxy` and a small nohup'd transfer, or (c) re-host to a staging bucket (GitHub Releases for ~50 MB files / S3 for larger) from a laptop with open FTP and pull via HTTPS on HPC. SUMSTATS-UPGRADE §5 Tier 1 calls this out explicitly as Q5.

**Warning signs:** `Connection timed out` on FTP HEAD; `curl: (7) Failed to connect`.

### Pitfall 3: **GIGASTROKE per-ancestry GCST accessions are JS-rendered and not scriptable**

**What goes wrong:** The EBI GWAS Catalog publication page `www.ebi.ac.uk/gwas/publications/36180795` lists stroke accessions through JavaScript-rendered DOM — `curl`/`requests` returns a placeholder HTML with no accessions. This breaks any "just scrape the catalog for accessions" approach.

**Why it happens:** EBI moved to client-rendered SPA in mid-2024.

**How to avoid:** D-02 resolves this with a one-time ~15-minute manual browse by Carter, committing resolved accessions to `SUMSTATS-UPGRADE.tsv` **before** Snakemake download rule fires. The planner's Wave 0 should include a "gate on Carter's manual GCST commit" note; after Carter commits `docs(amendments): GIGASTROKE GCST lock`, the download rule reads the resolved per-ancestry accessions from the TSV and uses them in URL construction (EBI catalog FTP URLs follow the pattern `https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST{range}/GCST{acc}/`).

**Warning signs:** Manifest entries with `GCST90104540-series` placeholder strings. Snakemake fails with "no such file" on the catalog FTP.

### Pitfall 4: **GBMI harmonizer assumes GRCh37, but 2022 release is GRCh38**

**What goes wrong:** `src/python/harmonize_gbmi.py` line 116: `# No liftover: GBMI flagship releases are already GRCh37.` This was true for the Phase 09 GBMI release consumed by the replication subset. The SUMSTATS-UPGRADE.tsv row 18 lists build=38 for the GBMI asthma 2022 release, so the existing harmonizer will emit GRCh38 coordinates labeled as GRCh37 — silent bad data.

**Why it happens:** GBMI changed default build between versions.

**How to avoid:** In the M1 wave that reuses `harmonize_gbmi.py`, **add a liftover branch**: pass `--liftover hg38ToHg19.over.chain.gz` as a new CLI flag, invoke `sumstats_utils.liftover_to_grch37` after the column rename, before the palindromic filter. Existing `harmonize_gbmi.py` can be extended with ~10 lines. Alternatively, treat GBMI asthma as a new `harmonize_gbmi_v2.py` to avoid breaking Phase 09 consumers.

**Warning signs:** Variant count drops by >5% at liftover (hard error per `sumstats_utils.liftover_to_grch37` max_drop_rate=0.05); OR asthma harmonized file has variants with positions that don't match 1KG b37 bim.

### Pitfall 5: **MAGIC rsid-only SNPID requires a forward rsid→chr:pos crosswalk**

**What goes wrong:** MAGIC 2021 Chen files use rsid-only SNP_ID column — no CHR/POS. `sumstats_utils.py` + existing harmonizers don't ship a forward `rsid → (chr, pos)` helper; `munge_sumstats_ldsc.py` has the **reverse** direction (chr:pos → rsid via 1000G bim at lines 54-85). Without forward crosswalk, harmonize_magic cannot emit CHR/BP columns.

**Why it happens:** Phase 09 cohorts (FinnGen, GBMI, MVP, BBJ) all shipped chr:pos natively; MAGIC is the first cohort needing forward lookup.

**How to avoid:** Build the forward map by inverting the existing bim-parser: `{rsid: (chr, pos)}` from `data/external/1000G.EUR.QC.{1..22}.bim` files. Load once, apply as `df["CHR"], df["BP"] = zip(*df["SNP_ID"].map(forward_map))`. Drop rsids not in the lookup with a QC stat (expect ~2-5% drop per MAGIC→1KG HRC mismatch, acceptable per SUMSTATS-UPGRADE §7 item 8). Add this helper to `sumstats_utils.py` as `build_rsid_to_chrpos(bim_prefix) -> dict` alongside the reverse `_build_chrpos_to_rsid` that's already there.

**Warning signs:** MAGIC harmonizer emits CHR=NaN, BP=NaN for > 5% of variants.

### Pitfall 6: **Aragam ZIP contents unknown until Wave 1 unpack**

**What goes wrong:** D-03 branch: `Aragam_2022_CARDIoGRAM_CAD_GWAS.zip` (142 MB, landed) must be unzipped to enumerate ancestry subfiles. Whether an AFR subset is inside determines the fate of TSV row 23 (AFR-CAD slot). Premature harmonizer writing assumes file structure before it's known.

**Why it happens:** Aragam 2022 supplementary packaging is not documented in the KP4CD page.

**How to avoid:** Wave 1 first task: `unzip -l data/raw/sumstats_v2/Aragam2022/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip | tee data/raw/sumstats_v2/Aragam2022/manifest.txt`. Commit the manifest. If `Aragam2022_AFR_subset.tsv` (or equivalent) is present, row 23 harmonizes as Aragam. If absent, Klarin 2018 MVP-AFR-CAD triggers via the `SUMSTATS-UPGRADE.md` §D-03 fallback branch — new download URL + new harmonizer variant or a one-off Python module `harmonize_klarin.py` (~80 LoC, symmetric to `harmonize_aragam.py`).

**Warning signs:** Row 23 TSV `status = to_download` but no AFR file under `data/raw/sumstats_v2/Aragam2022/` subdirs.

### Pitfall 7: **b37→b37 sources silently go through liftover if the planner is not careful**

**What goes wrong:** Applying `sumstats_utils.liftover_to_grch37` to a file that is ALREADY b37 is a no-op **when the chain file is hg38→hg19**, but if someone accidentally uses the hg19→hg38 chain (reverse of what D-08 requires), the positions shift to b38 while being LABELED b37.

**Why it happens:** Two chain files could end up in `data/external/liftover/`: `hg19ToHg38.over.chain.gz` (already on disk — verified) and `hg38ToHg19.over.chain.gz` (must be staged in Wave 0, not yet on disk). Mix-up is easy.

**How to avoid:** Harmonizer CLI flag `--liftover-chain {path}` must be explicit, not optional, for the two b38-source harmonizers. Add a guard at the top of `liftover_to_grch37`: inspect the chain-file basename; raise `ValueError` if basename doesn't contain `hg38ToHg19` when `--target-build GRCh37`.

**Warning signs:** Harmonized positions don't match a known b37 landmark (e.g., rs429358 at 19:44908684 per SUMSTATS-UPGRADE §7 item 3) — file-level sanity check catches this.

### Pitfall 8: **Within-GLGC same-sample-different-trait pairs produce bivariate intercept ≈ 1.0 (not a bug)**

**What goes wrong:** LDL-EUR vs HDL-EUR vs TG-EUR vs TC-EUR within GLGC are 100% same-sample different traits (SUMSTATS-UPGRADE §4). Expected bivariate intercept ≈ 1.0 for these 6 within-lipid-EUR pairs. Naive validation "flag intercept > 0.9 as suspicious" would false-alarm on these 6 pairs.

**Why it happens:** Bivariate intercept structurally equals the in-sample genetic covariance when the two "traits" are from the same subjects.

**How to avoid:** QC checklist Pitfall-validation in `m1_qc_report.qmd` must ship an expected-intercept-lookup table (planner artifact; ~20 pairs with known expected intercepts) derived from SUMSTATS-UPGRADE §4:
- UKB-UKB EUR pairs (36 pairs): expected intercept > 0.5.
- Within-GLGC EUR lipids (6 pairs): expected intercept ≈ 1.0.
- BBJ-BBJ EAS pairs (~15 pairs): expected intercept > 0.5.
- MVP-MVP AFR pairs (6 pairs): expected intercept > 0.5.
- Everything else: expected intercept ≈ 0.0 ± 0.05.
Flag only DEVIATIONS from these structural expectations.

**Warning signs:** Flat-threshold alarms on known-overlap pairs.

## Code Examples

### Example 1: `harmonize_yengo.py` skeleton (NEW; Yengo 2018 BMI EUR + Loh 2022 BMI variant with liftover)

```python
#!/usr/bin/env python3
"""Yengo 2018 GIANT+UKB BMI EUR → canonical 10-column TSV (D-10).
Also handles Loh 2022 Nat Commun (BMI EUR + AFR, GRCh38) with liftover.

Source columns (Yengo 2018 GIANT file):
  SNP, CHR, POS, Tested_Allele, Other_Allele, Freq_Tested_Allele, BETA, SE, P, N
Source columns (Loh 2022 EUR/AFR GWAS-Catalog harmonized format):
  variant_id, chromosome, base_pair_location, effect_allele, other_allele,
  effect_allele_frequency, beta, standard_error, p_value, n
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
import sumstats_utils as _su

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]

YENGO_COLS = {"CHR": "CHR", "POS": "BP", "SNP": "SNP",
              "Tested_Allele": "EA", "Other_Allele": "OA",
              "Freq_Tested_Allele": "EAF", "BETA": "BETA", "SE": "SE",
              "P": "P", "N": "N"}

LOH_COLS = {"chromosome": "CHR", "base_pair_location": "BP", "variant_id": "SNP",
            "effect_allele": "EA", "other_allele": "OA",
            "effect_allele_frequency": "EAF", "beta": "BETA",
            "standard_error": "SE", "p_value": "P", "n": "N"}

def harmonize_yengo(input_path: Path, output_path: Path,
                    parquet_path: Path, variant: str,
                    chain_file: Path | None = None) -> dict:
    """variant ∈ {'yengo2018', 'loh2022_eur', 'loh2022_afr'}."""
    df = pd.read_csv(input_path, sep="\t", compression="infer", low_memory=False)
    col_map = YENGO_COLS if variant == "yengo2018" else LOH_COLS
    missing = [c for c in col_map if c not in df.columns]
    if missing:
        raise ValueError(f"harmonize_yengo({variant}): expected {sorted(col_map.keys())}, "
                         f"missing {missing}. Found {sorted(df.columns.tolist())}.")
    df = df[list(col_map.keys())].rename(columns=col_map)[CANONICAL_COLS]

    # Loh 2022 is GRCh38 → liftover to GRCh37 per D-08
    if variant.startswith("loh2022"):
        if chain_file is None:
            raise ValueError("Loh 2022 requires --chain data/external/liftover/hg38ToHg19.over.chain.gz")
        df, qc = _su.liftover_to_grch37(df, chain_file=str(chain_file),
                                         chr_col="CHR", bp_col="BP", max_drop_rate=0.05)
        print(f"[yengo] liftover QC: {qc}", file=sys.stderr)

    df = _su.filter_palindromic_ambiguous(df)  # Pitfall #2

    # Emit both artifact classes per D-09.
    # bgzip + tabix index handled downstream in Snakemake shell: rule.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False, compression="gzip")
    df.to_parquet(parquet_path, index=False, compression="snappy")
    return {"trait": "bmi", "variant": variant, "n_rows": int(len(df)),
            "tsv": str(output_path), "parquet": str(parquet_path)}

def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True, help="tsv.gz output (Snakemake will bgzip+tabix)")
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--variant", choices=["yengo2018", "loh2022_eur", "loh2022_afr"], required=True)
    ap.add_argument("--chain", type=Path, default=None)
    args = ap.parse_args()
    harmonize_yengo(args.input, args.output, args.parquet, args.variant, args.chain)

if __name__ == "__main__":
    _main()
```

### Example 2: Quarto QC template `m1_qc_report.qmd` skeleton (NEW; D-12)

```markdown
---
title: "Phase M1 QC — `{r} params$trait` × `{r} params$ancestry`"
format:
  html:
    embed-resources: true
    toc: true
    code-fold: true
params:
  trait: "bmi"
  ancestry: "EUR"
  consortium: "GIANT"
  year: 2018
  harmonized_tsv: "data/processed/sumstats_harmonized/bmi.EUR.GIANT.2018.GRCh37.tsv.bgz"
  ldsc_log: "data/processed/ldsc_overlap/rg_logs/focal_00_bmi.EUR.GIANT.2018.log"
  sha256: ""
engine: knitr
jupyter: python3
---

## 1. File integrity (SUMSTATS-UPGRADE §7 item 1, 4, 9)

```{python}
import pandas as pd, hashlib
df = pd.read_csv(params["harmonized_tsv"], sep="\t", compression="gzip")
print(f"Variant count: {len(df):,}")
print(f"SHA-256: {params['sha256']}")
print(f"Columns: {list(df.columns)}")
assert set(df.columns) >= {"CHR","BP","SNP","EA","OA","BETA","SE","P","EAF","N"}
assert df["EAF"].between(0, 1).all(), "EAF out of [0,1]"
assert df["P"].between(0, 1).all(), "P out of [0,1]"
```

## 2. Variant count sanity (§7 item 1)

PASS if ≥ 5M for genome-wide EUR, ≥ 10M for trans-ancestry, ≥ 3M minimum.

## 3. MAF histogram (§7 item 2)

```{r}
library(ggplot2); library(tidyverse)
df <- readr::read_tsv(params$harmonized_tsv, col_types="ciccdddddi")
df %>% mutate(MAF = pmin(EAF, 1-EAF)) %>%
  ggplot(aes(x=MAF)) + geom_histogram(bins=100) +
  labs(title=paste("MAF histogram —", params$trait, params$ancestry))
```

## 4. Manhattan + QQ (positive-control locus presence, §7 item 7)

```{r}
qqman::manhattan(df %>% select(SNP, CHR, BP, P),
                 main=paste("Manhattan —", params$trait, params$ancestry))
qqman::qq(df$P, main="QQ")
# Compute λ_GC (§7 item 6)
chisq_med <- median(qchisq(df$P, df=1, lower.tail=FALSE), na.rm=TRUE)
lambda_gc <- chisq_med / qchisq(0.5, df=1)
cat("λ_GC =", round(lambda_gc, 3), "\n")
```

## 5. LDSC single-trait intercept (§7 item 5)

```{r}
log_text <- readLines(params$ldsc_log)
# Parse 'Intercept: X (Y)' line
intercept_line <- grep("Intercept:", log_text, value=TRUE)[1]
cat("LDSC intercept:", intercept_line, "\n")
```

## 6. Seven positive-control locus check (§7 item 7)

Check presence + p < 1e-8 at each of: FTO (16:53.8Mb) for BMI; TCF7L2 (10:114.7Mb) for T2D; APOE (19:45.4Mb) for LDL; UMOD (16:20.3Mb) for eGFR; 9p21.3 (9:22.1Mb) for CAD; ADRB1 (10:115.8Mb) for SBP.

## 7. Strand-ambiguous rate (§7 item 8)

Dropped palindromic SNPs are logged in the harmonizer output; expect < 10% drop.

## 8. Per-variant N sanity (§7 item 9)

`max(N) - reported_total_N` / `reported_total_N` should be within ±1%.

## 9. PASS/FAIL summary

| Check | Status |
|---|---|
| Variant count | {PASS/FAIL} |
| MAF distribution | {PASS/FAIL} |
| GRCh37 build | {PASS/FAIL} |
| Effect allele labeled | {PASS/FAIL} |
| LDSC intercept 1.0-1.15 | {PASS/FAIL} |
| λ_GC ≤ 1.2 | {PASS/FAIL} |
| Positive controls present | {PASS/FAIL} |
| Strand-ambiguous < 10% | {PASS/FAIL} |
| N integrity | {PASS/FAIL} |
```

### Example 3: Snakemake rule for LDSC star-topology rg (NEW; Pattern 4)

```python
# workflow/rules/m1_ldsc_rg.smk (NEW)
# 44 star-topology LDSC rg calls → reducer → 45×45 bivariate-intercept matrix.

import yaml
with open("config/trait_inventory.yaml") as fh:
    INV = yaml.safe_load(fh)
TRAIT_KEYS = list(INV["traits"].keys())  # 45 dotted keys, sorted
assert len(TRAIT_KEYS) == 45, f"Expected 45 trait keys, got {len(TRAIT_KEYS)}"

MUNGED_DIR = config["paths"]["ldsc_munged"]
RG_LOG_DIR = config["paths"]["ldsc_rg_logs"]
REF_LD_CHR = config["paths"]["eur_w_ld_chr"]

rule ldsc_rg_star:
    """Focal file i vs all files i+1..45 in a single LDSC --rg call.
    N-1 pairs per call; 44 calls cover 990 unique upper-triangle pairs.
    """
    input:
        focal   = lambda wc: f"{MUNGED_DIR}/{TRAIT_KEYS[int(wc.focal_idx)]}.sumstats.gz",
        others  = lambda wc: [f"{MUNGED_DIR}/{k}.sumstats.gz"
                              for k in TRAIT_KEYS[int(wc.focal_idx)+1:]],
    output:
        log = f"{RG_LOG_DIR}/focal_{{focal_idx}}.log",
    conda: "../envs/m1-ldsc-rg.yml"
    resources:
        mem_mb=8000,
        runtime=14400,  # 240h on long queue
    params:
        rg_args = lambda wc, input: ",".join([input.focal] + list(input.others)),
        out_prefix = lambda wc: f"{RG_LOG_DIR}/focal_{wc.focal_idx}",
    shell:
        "python tools/ldsc/ldsc.py --rg {params.rg_args} "
        "--ref-ld-chr {REF_LD_CHR} --w-ld-chr {REF_LD_CHR} "
        "--out {params.out_prefix}"

rule ldsc_rg_reduce:
    input:
        logs = expand(f"{RG_LOG_DIR}/focal_{{i}}.log", i=range(44)),
    output:
        matrix = f"{config['paths']['ldsc_overlap']}/bivariate_intercept_matrix_2026-04.tsv",
    conda: "../envs/m1-harmonize.yml"
    shell:
        "python src/python/reduce_ldsc_rg_matrix.py "
        "--log-dir {RG_LOG_DIR} --trait-inventory config/trait_inventory.yaml "
        "--output {output.matrix}"
```

### Example 4: `config/trait_inventory.yaml` schema (NEW; REQ-TRAIT-INVENTORY)

```yaml
# config/trait_inventory.yaml
# Emitted by src/python/build_trait_inventory.py from SUMSTATS-UPGRADE.tsv + SHA manifests.
# Version-controlled. M2+ wrappers read this as the schema contract.
version: "2026-04-M1"
build_target: "GRCh37"
traits:
  # Key format: <trait>.<ancestry>.<consortium>.<year>  (D-16)
  bmi.EUR.GIANT.2018:
    trait: bmi
    ancestry: EUR
    consortium: GIANT
    year: 2018
    source_url: https://portals.broadinstitute.org/collaboration/giant/...
    doi: 10.1093/hmg/ddy271
    build: 37
    phenotype_lock: "continuous BMI inverse-rank-normal"
    harmonized_path: data/processed/sumstats_harmonized/bmi.EUR.GIANT.2018.GRCh37.tsv.bgz
    parquet_path:    data/processed/sumstats_harmonized_parquet/bmi.EUR.GIANT.2018.GRCh37.parquet
    munged_path:     data/processed/ldsc_overlap/munged/bmi.EUR.GIANT.2018.sumstats.gz
    n_total: 681275
    n_cases: null
    n_controls: null
    sha256_raw: "<computed>"
    sha256_harmonized: "<computed>"
    ldsc_intercept: <computed>
    ldsc_h2: <computed>
    qc_report_path: data/processed/sumstats_harmonized/qc_log/bmi.EUR.GIANT.2018.qc.html
    qc_status: "PASS"
    cohort_overlap_cohorts: [UKB, deCODE, HUNT, ARIC, FHS]
    mtag_overlap_correction_required: true
    dua_required: false
    license: public_academic
  # ... 44 more rows
```

### Example 5: Extended `bin/download_sumstats_v2.sh` manifest addendum (Wave 1 portal dispatch)

```bash
# Additional manifest entries for portal-gated sources (appended to existing driver).
# Uses the SAME fetch_one idempotent helper + xargs -P 5 pattern.

# Yengo 2018 BMI EUR - GIANT portal direct-link after manual verification
echo -e "https://portals.broadinstitute.org/collaboration/giant/images/2/2f/Meta-analysis_Locke_et_al%2BUKBiobank_2018_UPDATED.txt.gz\tdata/raw/sumstats_v2/GIANT2018/BMI/EUR\tMeta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz" >> "$MANIFEST"

# MAGIC 2021 HbA1c - only fires after Wave 0 FTP egress check passes
for anc_file in TA EUR AA EAS SAS HISP; do
  anc_local=$(echo "$anc_file" | sed 's/AA/AFR/;s/HISP/HIS/;s/TA/TRANS/')
  echo -e "ftp://web-ftp.ex.ac.uk/docs/downloads/MAGIC1000G_HbA1c_${anc_file}.tsv.gz\tdata/raw/sumstats_v2/MAGIC2021/HbA1c/${anc_local}\tMAGIC1000G_HbA1c_${anc_file}.tsv.gz" >> "$MANIFEST"
done

# DIAMANTE 2022 - requires cookie persistence (ToS click-through); driver picks up $DIAMANTE_COOKIE env var
for anc in TA EUR EAS SAS; do
  anc_local=$(echo "$anc" | sed 's/TA/TRANS/')
  echo -e "https://diagram-consortium.org/downloads/DIAMANTE-${anc}.sumstat.txt.gz\tdata/raw/sumstats_v2/DIAMANTE2022/T2D/${anc_local}\tDIAMANTE-${anc}.sumstat.txt.gz" >> "$MANIFEST"
done
# Note: driver augment — pass `-b "$DIAMANTE_COOKIE"` to curl for DIAMANTE rows only.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Candidate-locus 5-trait design with identity-placeholder LD | Genome-wide 9-trait × 2-ancestry with real matched-ancestry LD (AoU AFR WGS ~100k + 1KG+UKB EUR) | 2026-04-22 Amendment | M1's scope; drives MTAG `--overlap` mandate. |
| MTAG default (no `--overlap`, assumes independent samples) | MTAG with LDSC-intercept `--overlap` matrix for UKB/MVP overlap | Turley 2018 standard | M1 builds the matrix that M2 consumes. |
| CKDGen 2019 Wuttke = latest eGFR | Still latest as of 2026-04-22 — Stanzick 2021 is PRS-specific, Liu 2023 is sex-stratified | 2019-present | Accept D-10. |
| GRCh38 as target for new GWAS | GRCh37 still canonical for M1 per DEC-2026-04-24 — existing 1KG b37 LD panels + Evangelou spine force the choice | 2026-04-24 discuss-phase | Two liftover steps (Loh 2022, GBMI asthma). |
| LDSC `--rg-cross` (mythical) | `--rg` star-pattern × 44 orchestrated | N/A — never existed in abdenlab fork | Pitfall 1; Pattern 4. |
| Original Bulik-Sullivan LDSC (Py2.7) | abdenlab/ldsc-python3 fork (Py3.11) | 2023+ | Enables unified Python stack; statistical logic unchanged per `envs/ldsc_py3.yml` comment. |
| GIANT BMI = Locke 2015 N≈340k | Yengo 2018 N=681k (primary); Loh 2022 N≈1.1M multi-ancestry (parallel-carry) | 2018/2022 | Higher-power EUR; adds AFR. |
| DIAMANTE Mahajan 2018 | DIAMANTE Mahajan 2022 N=1.34M trans-ancestry | 2022 | 2× N; adds SAS, HIS strata. |
| MEGASTROKE IS (ischemic-only) | GIGASTROKE all-stroke 2022 | 2022 + phenotype lock change | Phenotype definition change; Amendment §4 lock. |
| Willer 2013 / Klarin 2018 lipids | GLGC Graham 2021 multi-ancestry | 2021 | 5 ancestries per lipid trait. |
| Köttgen 2010 eGFR | CKDGen 2019 Wuttke + Morris 2019 AFR | 2019 | ~2× N. |
| Wheeler 2017 HbA1c | MAGIC Chen 2021 multi-ancestry | 2021 | 6 ancestries. |

**Deprecated/outdated:**
- MEGASTROKE ischemic-only: retired in favor of GIGASTROKE all-stroke per Amendment §4 phenotype lock.
- Original Bulik-Sullivan LDSC (Python 2.7): retired; use abdenlab/ldsc-python3 fork.
- `--rg-cross` as assumed CLI flag: does not exist; use 44 star-calls.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The abdenlab/ldsc-python3 fork's `--rg` flag behavior (star-topology, first file focal) exactly matches the original Bulik-Sullivan LDSC behavior documented in the 2015 Atlas paper. | Pitfall 1; Pattern 4 | LOW — verified by reading `tools/ldsc/ldsc.py` lines 608-613 ("Comma-separated list of prefixes of .chisq filed for genetic correlation estimation") and the `ldsc/sumstats.py` `estimate_rg` implementation which pairs p1 with each subsequent p_i. If the fork silently added cross-mode, would over-compute (redundant) but not under-compute. |
| A2 | Evangelou 2018 SBP-EUR at `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz` is GRCh37 and conforms to the 10-column canonical schema. | §D-10; Runtime State Inventory | MEDIUM — not re-verified in this research pass; planner's Wave 0 must run a schema-conformance check (`pandas.read_csv` → column-set assertion) before reusing. TSV row 12 confirms b37. |
| A3 | The MAGIC FTP host `web-ftp.ex.ac.uk` is still reachable from NCSU HPC compute nodes in April 2026. | Pitfall 2 | MEDIUM — SUMSTATS-UPGRADE.md Q5 explicitly flags this as an open pre-flight check. Planner Wave 0 must run egress probe. |
| A4 | The hg38ToHg19 UCSC chain file is stable and available from `https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz`. | Runtime State; Pitfall 4, 7 | LOW — UCSC has served this file since 2013; Phase 0 used the reverse (hg19→hg38). Cross-check: Ensembl also mirrors chain files. |
| A5 | LDSC 45-trait bivariate-intercept matrix will complete inside long-queue wall time (14400 min = 240 h) on LSF. | Pattern 4 | MEDIUM — 44 parallel focal-star calls on long queue can each take 3-11 h depending on #pairs in the star. Bottleneck is the longest star (focal=0, 44 pairs, ~11 h). Comfortably under 240 h. If single-call limit is hit, fall back to serialized chunked `--rg`. |
| A6 | CrossMap (in `hlp_crossmap` conda env) is functionally equivalent to pyliftover for the 2 b38→b37 lift cases. | Standard Stack alternatives | LOW — both wrap the same UCSC chain file and algorithm; pyliftover's edge-case handling (chrMT, chr0, strand) is what `sumstats_utils.liftover_to_grch37` already tolerates. |
| A7 | The 7 new harmonizer modules (~100-150 LoC each) can reuse `harmonize_gbmi.py`'s B-2-guard pattern to fail loudly on missing columns. | D-10; Pattern 1 | LOW — the pattern is mechanical. Risk is that one source (e.g., DIAMANTE) has a format quirk not covered by col_map rename. Mitigation: per-harmonizer unit test on ~100-row synthetic input landed in Wave 0. |
| A8 | `config/trait_inventory.yaml` schema (author's discretion) is what M2 MTAG + CPASSOC wrappers will expect. | D-16; discretion-area YAML schema | MEDIUM — M2 isn't planned yet (D-17 deferred). Mitigation: make the YAML self-documenting with a `version: "2026-04-M1"` field; M2 discuss can rev the schema without breaking M1's own frozen emission. |
| A9 | The 27 already-landed raw files under `data/raw/sumstats_v2/{GLGC2021,CKDGen2019,Aragam2022}/` have not been mutated since the 2026-04-23 fetch. | Pattern 3; Wave 2 kickoff | LOW — `data/` is gitignored and `.planning/amendments/SUMSTATS-SCRIPTED-FETCH-COMPLETE.md` records 40.4 GB total on 2026-04-23. Freeze SHA-256 in Wave 1 before Wave 2 harmonizers fire. |

**If this table is empty:** N/A — 9 assumptions logged. Planner should surface A3 and A5 to Carter before Wave 0 fires (A3 is the egress probe; A5 is the wall-time budget on LSF long queue).

## Open Questions (RESOLVED)

1. **Does MAGIC FTP egress work from NCSU HPC compute nodes?**
   - What we know: SUMSTATS-UPGRADE.md Q5 flags this as Wave 0 pre-flight.
   - What's unclear: Real-time probe hasn't been run in this research pass.
   - Recommendation: Wave 0 first task is `curl --connect-timeout 30 --head ftp://web-ftp.ex.ac.uk/docs/downloads/`. If fail, fallback to login-node proxy or EBI mirror per SUMSTATS-UPGRADE §5.
   - **RESOLVED**: deferred to m1-00-T2 Wave 0 probe; HTTPS EBI mirror fallback pre-authored per SUMSTATS-UPGRADE §5 Tier 1.

2. **Does Aragam ZIP contain an AFR subset file?**
   - What we know: D-03 branches on this.
   - What's unclear: Hasn't been unzipped.
   - Recommendation: Wave 1 first task is `unzip -l Aragam_2022_CARDIoGRAM_CAD_GWAS.zip | tee Aragam2022/manifest.txt`; planner folds the conditional branch into Wave 2's harmonizer routing.
   - **RESOLVED**: Wave 1 m1-01-T1 unzip -l step; Klarin 2018 fallback pre-authored if AFR absent (D-03).

3. **Which rsid-to-position lookup file should MAGIC use — 1000G Phase 3 EUR.bim, the union of all ancestries, or HRC?**
   - What we know: `munge_sumstats_ldsc.py` uses 1000G EUR.bim by default (line 72).
   - What's unclear: Whether MAGIC rsids have better coverage in the 1KG TRANS union than EUR-only.
   - Recommendation: Use 1KG Phase 3 EUR.bim as default; fall back to HRC rsid-to-position map if >5% MAGIC rsids are missing from 1KG EUR (expect ~2-5% mismatch). QC report surfaces the drop rate per MAGIC-ancestry-file.
   - **RESOLVED**: default 1KG Phase 3 EUR.bim; fallback HRC sitefile if >5% rsid mismatch rate observed at Wave 0 sanity probe.

4. **LDSC wall-time per focal-star call — what's the real ceiling?**
   - What we know: Single-pair rg is ~5-20 min on one core; 44-pair star is roughly 44×per-pair minus shared startup.
   - What's unclear: Whether the abdenlab fork has the same inner-loop efficiency as Python 2 LDSC.
   - Recommendation: Wave 0 smoke test runs a 2-trait rg and times it. If > 30 min per pair, de-parallelize the star into 44-size chunks; if < 15 min per pair, proceed.
   - **RESOLVED**: deferred to m1-00-T2 Probe 3 benchmark; m1-03-T2 --jobs value computed dynamically from wave0_probes.log.

5. **Should the 45×45 intercept matrix include p-values and rg alongside gcov_int?**
   - What we know: MTAG `--overlap` only needs `gcov_int`; CPASSOC may want rg for effect-size alignment.
   - What's unclear: M2 decision deferred (D-17).
   - Recommendation: Emit a "fat" format with columns `[trait_a, trait_b, rg, rg_se, gcov_int, gcov_int_se, h2_a, h2_b]` in `rg_matrix_long.tsv`, and also emit the 45×45 wide `gcov_int` matrix at `bivariate_intercept_matrix_2026-04.tsv` (D-11 specified). M2 picks what it needs from the long form.
   - **RESOLVED**: emit BOTH — wide gcov_int-only 45×45 TSV (primary for MTAG slice) AND fat long-form (trait_i, trait_j, rg, gcov_int, gcov_int_se) for sensitivity.


## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | All harmonizers + Snakemake | ✓ | 3.11 at `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11` | — |
| Snakemake 7.32.4 | DAG orchestration | ✓ | 7.32.4 | — |
| pandas 2.2.3 | All harmonizers | ✓ | verified | — |
| pyarrow 18.1.0 | .parquet mirror (D-09) | ✓ | verified | — |
| pyliftover | b38→b37 via sumstats_utils.liftover_to_grch37 | ✓ | installed in smoke_dev env; `python -c "import pyliftover"` succeeds | CrossMap CLI at `/rs1/.../hlp_crossmap/bin/CrossMap` |
| CrossMap | Alternative liftover (SUMSTATS-UPGRADE §6 default) | ✓ | present in `hlp_crossmap` env | pyliftover |
| htslib (bgzip + tabix) | .tsv.bgz primary artifact (D-09) | ✓ | 1.21 | — |
| LDSC (abdenlab fork) | 45-trait bivariate-intercept matrix | ✓ via `envs/ldsc_py3.yml` git install | pinned to HEAD at install | — |
| UCSC liftOver binary | CrossMap alternative | Unknown — not probed in Wave 0 | — | pyliftover is primary |
| hg38ToHg19 chain file | Liftover of Loh 2022 BMI + GBMI asthma | ✗ | — | Fetch from `https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz` in Wave 0 |
| hg19ToHg38 chain file | Not needed by M1 but exists for bidirectional smoke tests | ✓ | present at `data/external/liftover/hg19ToHg38.over.chain.gz` | — |
| LDSC reference LD files (eur_w_ld_chr, afr LD, shared-ancestry LD) | LDSC rg regression | Unknown — depends on Phase 05 staging | — | Download from `https://data.broadinstitute.org/alkesgroup/LDSCORE/eur_w_ld_chr.tar.bz2` in Wave 0 |
| w_hm3.snplist (HapMap3 SNP list) | LDSC `--merge-alleles` | Unknown — depends on Phase 05 staging | — | Download from `https://data.broadinstitute.org/alkesgroup/LDSCORE/w_hm3.snplist.bz2` in Wave 0 |
| 1000G Phase 3 EUR bim files | MAGIC rsid→chr:pos crosswalk + munge chr:pos→rsid | Unknown — Phase 01 staged them for EUR | — | Phase 01-02-PLAN produced them; path in `config/pipeline.yaml`. |
| 1000G Phase 3 AFR bim files | AFR-ancestry rsid bim (for AFR MAGIC file only) | Unknown | — | Phase 01-03-PLAN staged AFR LD files. |
| quarto CLI | Per-trait QC render (D-12) | Unknown — needs Wave 0 probe | — | Fallback: knitr-only Rmd rendering; loses Python engine (not ideal). |
| R + tidyverse + ggplot2 + qqman + locuszoomr | QC report plots | Partial — project has r_coloc env but needs qqman + locuszoomr added in new m1-qc.yml | — | — |
| curl / xargs | Portal downloads | ✓ | system | — |
| LSF bsub / bjobs / bqueues | HPC job submission | ✓ | verified in prior phases | — |

**Missing dependencies with no fallback:**
- hg38ToHg19 chain file — must be staged in Wave 0 before any Loh 2022 or GBMI asthma harmonizer runs. 1 curl command.

**Missing dependencies with fallback:**
- LDSC reference LD files: download if not staged (standard operation, documented in `tools/ldsc/README.md` line 297).
- LDSC w_hm3.snplist: same.
- quarto CLI: if absent, fall back to Rmd (format `html_document`, `knit()`) in R-only mode; Python cell work moves to a pre-render Python script that emits JSON the Rmd reads.

## Validation Architecture

> Nyquist validation is enabled per `config/workflow.nyquist_validation = true` (verified in `.planning/config.json`). This section drives VALIDATION.md + Dimension-8 acceptance criteria.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (project-wide; same as Phase 09 tests) |
| Config file | `pyproject.toml` or `pytest.ini` at project root (verify in Wave 0) |
| Quick run command | `pytest tests/m1/ -x --tb=short` (~5 min on 9 harmonizer unit tests + reducer + inventory builder) |
| Full suite command | `pytest tests/m1/ tests/phase9/test_sumstats_utils.py -v` (includes Phase 09 palindromic + liftover regression tests) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-TRAIT-INVENTORY | `config/trait_inventory.yaml` enumerates 45 trait × ancestry rows with all required fields | unit | `pytest tests/m1/test_build_trait_inventory.py -x` | ❌ Wave 0 |
| REQ-TRAIT-INVENTORY | Harmonized sumstats file exists for every (trait, ancestry) cell before M2 begins | integration | `python -c "import yaml; from pathlib import Path; [Path(r['harmonized_path']).is_file() for r in yaml.safe_load(open('config/trait_inventory.yaml'))['traits'].values()]"` | ❌ Wave 0 |
| REQ-SNAKEMAKE-CI | toy 3-locus smoke completes on `tests/toy_3locus/` with M1 rules loaded | integration | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` | ❌ Wave 0 (exists in pre-pivot; M1 rules to be added) |
| REQ-SNAKEMAKE-CI | All `envs/m1-*.yml` install cleanly via mamba | smoke | `for f in envs/m1-*.yml; do mamba env create -n smoke-test -f $f --dry-run; done` | ❌ Wave 0 |
| REQ-PUBLIC-DATA-ONLY | Every data source in config has `license` + `public: true` | unit | `pytest tests/m1/test_data_sources_license.py` | ❌ Wave 0 |
| REQ-PATH-PARAMETERIZATION | No hardcoded `/share/clintonlab`, `/rs1/researchers`, `/gpfs_common` in src/ or config/ | unit | `grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config` should return 0 | ✓ existing |
| — (harmonizer schema) | Each new harmonizer emits canonical 10-column schema | unit | `pytest tests/m1/test_harmonize_yengo.py tests/m1/test_harmonize_diamante.py tests/m1/test_harmonize_gigastroke.py tests/m1/test_harmonize_aragam.py tests/m1/test_harmonize_glgc.py tests/m1/test_harmonize_wuttke.py tests/m1/test_harmonize_magic.py -x` | ❌ Wave 0 (7 files) |
| — (liftover) | Loh 2022 + GBMI asthma liftover drop-rate < 5% on real input | integration | `pytest tests/m1/test_liftover_loh_gbmi.py` | ❌ Wave 2 |
| — (LDSC reducer) | `reduce_ldsc_rg_matrix.py` aggregates 44 synthetic star-logs into a 45×45 symmetric matrix with diag=1.0 | unit | `pytest tests/m1/test_reduce_ldsc_rg_matrix.py -x` | ❌ Wave 0 |
| — (QC report) | Quarto renders a per-trait `.qmd` to HTML without error on a 10k-row synthetic harmonized TSV | integration | `quarto render src/R/qc/m1_qc_report.qmd -P trait:bmi -P ancestry:EUR --output-dir /tmp/smoke` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/m1/ -x --tb=short` (under 30 s on all unit tests).
- **Per wave merge:** `pytest tests/m1/ tests/phase9/test_sumstats_utils.py -v && snakemake --dry-run` (confirms DAG integrity).
- **Phase gate:** Full `pytest tests/m1/ tests/phase9/` green AND 45 harmonized files on disk AND matrix computed AND per-trait Quarto HTMLs rendered AND both SHA-256 manifests frozen AND `config/trait_inventory.yaml` validates.

### Wave 0 Gaps

- [ ] `pytest.ini` or `pyproject.toml` pytest config — verify presence; add `testpaths = ["tests"]` if absent.
- [ ] `tests/m1/conftest.py` — shared fixtures: synthetic 10-col TSV factory, chain-file stub, LDSC-log sample strings.
- [ ] `tests/m1/test_build_trait_inventory.py` — 45-row YAML enumeration + schema validation.
- [ ] `tests/m1/test_harmonize_yengo.py` + 6 more — one per new harmonizer.
- [ ] `tests/m1/test_reduce_ldsc_rg_matrix.py` — symmetric matrix, diag=1.0, 45×45 shape.
- [ ] `tests/m1/test_liftover_loh_gbmi.py` — integration; 100-variant synthetic b38 input, drop rate < 5%.
- [ ] `envs/m1-download.yml`, `envs/m1-harmonize.yml`, `envs/m1-munge.yml` (alias of ldsc_py3), `envs/m1-ldsc-rg.yml` (alias), `envs/m1-qc.yml` — 5 yml files.
- [ ] `src/snakemake/rules/m1_download.smk`, `m1_harmonize.smk`, `m1_munge.smk`, `m1_ldsc_rg.smk`, `m1_qc.smk` — 5 rule files.
- [ ] `src/R/qc/m1_qc_report.qmd` — Quarto template.
- [ ] hg38ToHg19 chain file download + SHA-record.
- [ ] LDSC `w_hm3.snplist` + `eur_w_ld_chr/` download if not staged.
- [ ] MAGIC FTP egress probe (curl --head) — documented result.
- [ ] Carter manual GCST resolution for GIGASTROKE (D-02) — committed to TSV before Wave 1 fires.

### Dimension-8 Acceptance Criteria (Nyquist composite, per phase description item 15 a–i)

| Dim | Name | Acceptance | Evidence |
|-----|------|-----------|----------|
| a | File-integrity checksums | `data/raw/sumstats_v2/sha256_manifest.tsv` has ≥45 rows (some sources may contribute multiple files); every line has a valid 64-hex SHA-256; `data/processed/sumstats_harmonized/sha256_manifest.tsv` symmetric on harmonized files | Two manifest files present and validated by `build_trait_inventory.py` |
| b | Variant-count sanity (§7 item 1) | Per harmonized file, variant count within ±10% of published N for that trait × ancestry; all ≥3M | Per-trait QC report §2 PASS |
| c | Per-file Lambda GC ∈ [0.9, 1.15] (§7 item 6) | λ_GC computed from harmonized P-values; reported in QC HTML; flagged on values outside band | Per-trait QC report §4 PASS; cross-trait index aggregates |
| d | MAF band coverage [0.005, 0.5] (§7 item 2) | MAF histogram right-skew for array-only; U-shape for HRC/1KG-imputed; <5% variants with MAF=0 | Per-trait QC report §3 PASS |
| e | Palindromic exclusion rate < 10% (§7 item 8) | Per-harmonizer QC emits `n_palindromic_dropped / n_input`; report in QC HTML | Per-trait QC report §7 PASS |
| f | LDSC intercept plot shows expected UKB-pair cluster (§4 highest-overlap pairs) | 45×45 matrix heatmap; 36 UKB-UKB EUR pairs show intercept > 0.5; within-GLGC lipids 6 pairs ≈ 1.0; non-overlap pairs ≈ 0 ± 0.05 | `qc_log/index.html` intercept-matrix heatmap |
| g | Quarto HTML renders without error | All 9 per-trait HTMLs + 1 index exist at `data/processed/sumstats_harmonized/qc_log/`; no render-error logs | Wave 4 gate |
| h | Parquet/bgz/sumstats.gz all present per trait × ancestry | For every 45-row entry in `config/trait_inventory.yaml`, the three path fields resolve to existing, non-empty files | `python src/python/verify_m1_artifacts.py` |
| i | `config/trait_inventory.yaml` validates against schema | 45 rows; all required fields populated; types enforced | `pytest tests/m1/test_build_trait_inventory.py::test_schema_valid` |

**Planner note:** Dimension-8 criteria are a superset of SUMSTATS-UPGRADE §7 items 1-9. Items (a)-(e) map to §7 (1, 2, 5, 8, 9); (f) is the MTAG overlap prerequisite (§4); (g)-(i) are pipeline-completeness. VALIDATION.md should enumerate these 9 dimensions verbatim with per-dimension evidence paths.

## Project Constraints (from CLAUDE.md)

- **100% public data.** M1 must not admit any non-public source. D-06 explicitly avoids dbGaP DUA. D-05 flips PAGE to DUA only if portal barrier appears. AoU controlled-tier export is summary-only per `REQ-AOU-LD-EGRESS`.
- **Solo author; rigor over speed.** No corners cut on the 9-item QC checklist. Every harmonizer ships with a pytest unit test in Wave 0.
- **No web/JS stack.** No React/Next/Vite/TS. Quarto is rendered CLI, not served. Any interactive visualization lives inside the static HTML via Plotly-JS bundled by Quarto (acceptable — Quarto is not a web framework).
- **Data access lead times.** D-06 tiered path avoids the dbGaP 4-8-week block. Portal downloads require Carter's manual action but fit within M1's 4-6-week scope. AoU fallback compute time (D-07) if triggered: ~1-2 weeks.
- **GPFS filesystem; no worktree isolation.** GSD mode is `solo` with `git.isolation: branch`. Verified in `.planning/config.json` (mode: "yolo"; git.branching_strategy: "none"). All M1 work happens on `main` or a feature branch, no per-phase worktrees.
- **Python 3.11 pin (project memory `project_python_311_pin.md`).** All M1 Snakemake invocations use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` OR `snakemake --use-conda` with `envs/python_stats.yml`. Never invoke snakemake from miniconda3 base (Python 3.13).
- **LSF queues (`feedback_lsf_queues.md`).** bsub_wrapper.sh sets wall = queue max (serial=5760, long=14400, standard=2880 min). LSF_UNIT_FOR_LIMITS=GB. M1 rule queue assignments (suggested):
  - `m1_download` rules: standard (2880 min) for portal fetches; long (14400 min) for giant ZIPs.
  - `m1_harmonize` per-file rules: standard.
  - `m1_munge` per-file rules: serial (5760 min).
  - `m1_ldsc_rg_star` (44 jobs): long (14400 min).
  - `m1_qc` per-trait render: standard.
- **Parallel downloads (`feedback_parallel_downloads.md`).** xargs -P 5 for portal downloads. Already the pattern in `bin/download_sumstats_v2.sh`.
- **URL rot workarounds (`feedback_url_rot_workarounds.md`).** If MAGIC / DIAMANTE portals are broken at fetch time, fall back to Zenodo / EBI mirror / login-node proxy per that memory.
- **Don't tell user to `conda activate` (`feedback_no_conda.md`).** Use Snakemake `--use-conda` or full path invocations; never emit "run `conda activate smoke_dev`" instructions.

## Sources

### Primary (HIGH confidence)

- **`.planning/amendments/SUMSTATS-UPGRADE.md` + `.tsv`** — 48-line TSV source-of-truth; 9-item QC checklist §7; MTAG overlap strategy §4; download tier ordering §5; harmonization alignment §6. In-repo; committed.
- **`.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-CONTEXT.md`** — 17 user-locked decisions D-01..D-17.
- **`.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`** §3 M1, §4 trait inventory, §5 AFR LD strategy, §9 OSF amendment timing.
- **`src/python/sumstats_utils.py`** — canonical helpers (is_palindromic, filter_palindromic_ambiguous, liftover_to_grch37).
- **`src/python/harmonize_gbmi.py`** — reference implementation, REUSED AS-IS.
- **`src/python/liftover.py`** — pyliftover wrapper at function `liftover_coordinates`.
- **`src/python/munge_sumstats_ldsc.py`** — REUSED AS-IS; trait→effective-N logic.
- **`tools/ldsc/ldsc.py`** — vendored abdenlab fork; verified `--rg` semantics at lines 608-613.
- **`tools/ldsc/README.md`** — LDSC install + usage patterns.
- **`envs/python_stats.yml`, `envs/ldsc_py3.yml`** — pinned env versions.
- **`bin/download_sumstats_v2.sh`** — proven xargs -P 5 idempotent driver.
- **`config/bsub_wrapper.sh`** — LSF queue-max wall-time logic.
- **`.planning/config.json`** — workflow.nyquist_validation: true; mode: yolo; git.branching_strategy: none.
- **`CLAUDE.md`** — project constraints.
- **`.planning/DECISIONS.md`** — DEC-2026-04-22-02 (9-trait lock); DEC-2026-04-22-03 (MTAG+CPASSOC); DEC-2026-04-22-04 (AoU controlled-tier WGS).

### Secondary (MEDIUM confidence)

- **`.planning/phases/09-replication-in-independent-cohorts/09-02-PLAN.md`** — Wave 2 harmonizer architecture; verified reusable for M1.
- **`.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md`** — paste-ready body; M1 SHA-256 manifest feeds placeholder 1.
- **`.planning/amendments/AOU-LD-PIPELINE.md`** §2 P1-P7 — egress-audit scaffolding reusable for D-06/D-07.
- **Memory items** — `project_python_311_pin.md`, `feedback_lsf_queues.md`, `feedback_parallel_downloads.md`, `feedback_url_rot_workarounds.md`, `feedback_no_conda.md`.

### Tertiary (LOW confidence — flagged)

- GIGASTROKE per-ancestry GCST accessions (JS-rendered; D-02 manual resolution pending).
- MAGIC FTP egress from NCSU HPC (Wave 0 pre-flight pending).
- Aragam AFR subset presence in ZIP (Wave 1 unzip pending).
- Exact LDSC rg per-pair wall-time on abdenlab fork (Wave 0 smoke benchmark pending).

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — all tools verified on disk or in pinned env YAMLs; known-working Phase 09 pattern.
- Architecture: HIGH for patterns 1-3 (all have working exemplars); MEDIUM for pattern 4 (LDSC star orchestration — no Python-3 fork benchmark in project yet).
- Pitfalls: HIGH for 1, 4, 5, 8 (verified by reading source/docs); MEDIUM for 2, 3, 6, 7 (require Wave 0 probe).
- Don't-hand-roll: HIGH (every row cites an existing file).
- Environment availability: MEDIUM — two unknowns (quarto CLI, LDSC reference LD staging) must resolve in Wave 0.
- Validation architecture: HIGH — 9-dim mapping is direct from SUMSTATS-UPGRADE §7 + phase description §15.

**Research date:** 2026-04-24
**Valid until:** 2026-05-24 (30 days — stable; no fast-moving releases in the core stack; two open pre-flight checks reduce to 0 open after Wave 0).

---

## RESEARCH COMPLETE (as this file)
