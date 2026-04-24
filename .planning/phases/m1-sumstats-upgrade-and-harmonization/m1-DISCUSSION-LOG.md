# Phase M1: Sumstats upgrade and harmonization — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `m1-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-24
**Phase:** M1 — Sumstats upgrade and harmonization
**Slug:** m1-sumstats-upgrade-and-harmonization
**Discuss round:** R4 (parsed-plotting-lynx routing plan)
**Areas discussed:** Source locks (A), MVP Giri AFR-BP path (B), Genome build (C), Architecture + specs (D), M1→M2 handoff (F)

---

## A. Source locks

### A1. BMI EUR primary source

| Option | Description | Selected |
|--------|-------------|----------|
| Yengo 2018 primary; Loh 2022 parallel-carry | Yengo 2018 scripted-ready, GRCh37, N=681k EUR, fully released. Carry Loh 2022 pending GCST + AFR-subset confirmation. | ✓ |
| Loh 2022 primary; Yengo 2018 fallback only | Larger N (1.1M EUR + 100k AFR multi-ancestry), GRCh38, pending GWAS Catalog accession. | |
| Yengo 2018 only; drop Loh 2022 | Narrowest scope; only if Loh 2022 accession fails to resolve. | |

**User's choice:** Yengo 2018 primary; Loh 2022 parallel-carry (Recommended)
**Notes:** None — accepted recommendation.

---

### A2. GIGASTROKE per-ancestry GCST resolution

| Option | Description | Selected |
|--------|-------------|----------|
| Carter manual EBI browse now, Claude scripts rest | ~15 min human task at ebi.ac.uk/gwas/publications/36180795. Pin each (ancestry, subtype) to integer GCST; commit to TSV. | ✓ |
| Claude attempts headless-browser fetch first | Try Playwright/Selenium or EBI GWAS Catalog JSON API. Higher implementation cost; may still need Carter verification. | |
| Defer accession lock to download-time | Lock accessions inside the download rule at runtime. Makes TSV non-authoritative. | |

**User's choice:** Carter manual EBI browse now, Claude scripts rest (Recommended)
**Notes:** None — accepted recommendation.

---

### A3. Aragam 2022 AFR-CAD release policy

| Option | Description | Selected |
|--------|-------------|----------|
| Inspect ZIP first; Klarin 2018 fallback if absent | Unzip existing Aragam ZIP, enumerate. If AFR absent, use Klarin 2018 MVP-AFR-CAD (N≈8.5k) with methods disclosure. | ✓ |
| Drop CAD-AFR from Amendment §4 inventory | Accept 8 traits × 2 ancestries + CAD EUR-only. Requires re-opening DEC-2026-04-22-02. | |
| Email Aragam authors for AFR file | Direct request; 2-8 week uncertainty. Only if ZIP inspection shows AFR truly unreleased AND Klarin is too small. | |

**User's choice:** Inspect ZIP first; Klarin 2018 MVP-AFR-CAD fallback if absent (Recommended)
**Notes:** Author-email path kept as deferred contingent branch in CONTEXT.

---

### A4. GLGC HDL/TG/TC ancestry fanout

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as-is: LDL at 5, HDL/TG/TC at 3 | Scripted downloads already landed this set (24 files, 17 GB). | ✓ |
| Expand HDL/TG/TC to all 5 ancestries | Adds 9 rows, ~15-20 GB. Trivial extension of download manifest. | |
| Reduce to LDL-only trans+EUR+AFR | Narrowest scope; requires amending DEC-2026-04-22-02. | |

**User's choice:** Keep as-is: LDL at 5, HDL/TG/TC at 3 (Recommended)
**Notes:** None — accepted recommendation.

---

### A5. PAGE BMI-AFR access

| Option | Description | Selected |
|--------|-------------|----------|
| Treat sumstat-only as public; verify at download | Per Wojcik 2019 data-availability. Flip to DUA if portal barrier appears. | ✓ |
| Pre-submit phs000920 DUA now as safety | Parallel submission; 4-8 week lead time. Rigor-maximalist. | |
| Drop PAGE row; use only Loh 2022 AFR for BMI | Reduces BMI-AFR sources to 1. | |

**User's choice:** Treat sumstat-only as public; verify at download (Recommended)
**Notes:** None — accepted recommendation.

---

## B. MVP Giri AFR-BP critical path

### B1. MVP Giri AFR-BP strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Submit dbGaP phs001672 DUA now; park AFR-BP pending | 4-8 week lead time. Rigor-maximalist; preserves full N. | |
| Check for public GWAS-Catalog summary-only release first | Verify at ebi.ac.uk/gwas/publications/30578418 for public sumstat release. | |
| AoU workbench AFR-SBP derivation as primary | Compute de-novo AFR SBP on AoU controlled-tier (~60-95k AFR). | |
| Defer AFR-BP from M1; reopen Amendment §4 | Ship M1 with 8 traits × 2 ancestries + hypertension-EUR only. | |
| **User-custom: Tiered — GWAS-Catalog first, AoU workbench fallback** | **Primary = public GWAS-Catalog check; if not available → AoU workbench AFR-SBP derivation.** | **✓** |

**User's choice:** Tiered — "Check for public GWAS-Catalog summary first. If not available, then we'll go with AoU workbench" (free-text from "Other" branch)
**Notes:** Synthesizes options 2 + 3 into a contingent pipeline. dbGaP DUA submission NOT on primary or fallback path. Drop-from-M1 off-table. Triggers scope confirmation question in group D.

---

## C. Genome build target

### C1. GRCh37 vs GRCh38 canonical

| Option | Description | Selected |
|--------|-------------|----------|
| Keep b37 canonical; liftover 2 b38 sources; amend §3 M1 via DEC | Matches existing spine + 1KG b37 LD. Liftover Loh 2022 + GBMI asthma. File new DEC overriding "GRCh38" wording. | ✓ |
| Migrate everything to b38 | Honor Amendment literally. Requires rebuilding 1KG LD panels, re-liftover Evangelou, audit downstream code. | |
| Dual-build canonical deliverable | Emit both b37 and b38 per trait × ancestry. Doubles storage (~80 GB). | |

**User's choice:** Keep b37 canonical; liftover 2 b38 sources; amend Amendment §3 M1 via DEC (Recommended)
**Notes:** OSF paste-ready text may also need a one-line clarification — planner pre-paste check.

---

## D. Pipeline architecture and deliverable specs

### D1. Canonical harmonized deliverable format

| Option | Description | Selected |
|--------|-------------|----------|
| Dual-emit: .tsv.bgz+tabix primary + .parquet mirror | Tabix for region queries (coloc); parquet for bulk scans (LDSC/MTAG). | ✓ |
| Parquet only; refactor coloc to read parquet regions | Requires pyarrow/duckdb region-slice helper. Late-spine refactor risk. | |
| Keep .tsv.bgz only; amend Success Criterion 1 | Path of least change. Loses columnar speedup. | |

**User's choice:** Dual-emit: .tsv.bgz+tabix primary + .parquet mirror (Recommended)
**Notes:** None — accepted recommendation.

---

### D2. Harmonizer architecture

| Option | Description | Selected |
|--------|-------------|----------|
| Per-source modules; add 7 new following Phase 09 pattern | harmonize_yengo, harmonize_diamante, harmonize_gigastroke, harmonize_aragam, harmonize_glgc, harmonize_wuttke, harmonize_magic. Reuses 10-column schema. | ✓ |
| Consolidate into one harmonize_sumstat.py driven by YAML schema | One module + 12+ YAML configs. DRYer; higher initial design cost. | |
| Hybrid: generic for standards + per-source for outliers | Standard cluster via parameterized module; MAGIC/GLGC/GIGASTROKE per-source. | |

**User's choice:** Per-source modules; add 7 new harmonizers following Phase 09 pattern (Recommended)
**Notes:** None — accepted recommendation.

---

### D3. LDSC bivariate-intercept matrix scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full 45 × 45 matrix over all TSV rows | 990 pairs, single ldsc.py --rg-cross call. Maximum M2 optionality. | ✓ |
| Locked 18-row Track B plane only | 153 pairs. Minimal. Cannot support MTAG against TRANS/EAS/SAS/HIS without re-run. | |
| Tiered: 18×18 first-class + 45×45 as sensitivity artifact | Two matrices emitted. Slight provenance complexity. | |

**User's choice:** Full 45 × 45 matrix over all TSV rows (Recommended)
**Notes:** None — accepted recommendation.

---

### D4. QC report format

| Option | Description | Selected |
|--------|-------------|----------|
| Quarto (.qmd → HTML); reuse R + Python in one doc | Forward-path over Rmd; mixes tidyverse + pandas. | ✓ |
| Rmd → HTML via knitr | Traditional. Works but Quarto supersedes. | |
| Plain HTML dashboard from Python | Language-single; loses R stat-plot ergonomics. | |

**User's choice:** Quarto (.qmd → HTML); reuse R + Python in one doc (Recommended)
**Notes:** None — accepted recommendation.

---

### D5. SHA-256 manifest semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Raw downloads + harmonized outputs; OSF uses raw hashes | Two manifests; OSF pastes raw-source hashes (provenance-locked). | ✓ |
| Raw downloads only; OSF pastes same set | Narrowest; loses harmonized reproducibility. | |
| Harmonized outputs only | Process-centric; hashes drift with code version. Not OSF-safe. | |

**User's choice:** Raw downloads + harmonized outputs; OSF uses raw-source hashes (Recommended)
**Notes:** None — accepted recommendation.

---

### D6. Parallelization policy

| Option | Description | Selected |
|--------|-------------|----------|
| Harmonize-as-ready; re-fire incrementally | Snakemake per-source-file rule. Value from 27 already-landed files now. | ✓ |
| Serial: gate on full inventory landed | Single wave once all 45 rows terminal. Blocks on slowest source. | |
| Two-wave: scripted-complete now, portal+DUA later | Explicit Wave 1 / Wave 2 boundaries. Intermediate LDSC matrix as partial artifact. | |

**User's choice:** Harmonize-as-ready; re-fire incrementally when new sources land (Recommended)
**Notes:** None — accepted recommendation.

---

### D7. AoU compute scope expansion implication

| Option | Description | Selected |
|--------|-------------|----------|
| Confirm — add AoU derivation to M1; file DEC amending §3 M1 | Pre-register AoU AFR-SBP derivation protocol in CONTEXT. Reuses AOU-LD-PIPELINE.md P1-P7. Contingent branch (fires only if D-06 primary fails). | ✓ |
| Defer AoU derivation details to planner | CONTEXT flags the tiered decision; planner builds branch without pre-reg. Risk: mid-M1 rescope. | |
| If GWAS-Catalog fails, drop AFR-BP rather than add AoU compute | Reverses AoU-fallback commitment. | |

**User's choice:** Confirm — add AoU derivation to M1; file DEC amending §3 M1 scope (Recommended)
**Notes:** None — accepted recommendation.

---

## F. M1→M2 MTAG/CPASSOC handoff contract

### F1. LDSC bivariate-intercept matrix format

| Option | Description | Selected |
|--------|-------------|----------|
| Emit 45×45 wide TSV + M2 slices per-run | Single source of truth at data/processed/ldsc_overlap/. | ✓ |
| Emit per-MTAG-run sub-matrices (pre-sliced) | Requires knowing M2 MTAG groupings at M1 time. | |
| Both: full 45×45 + per-run sub-matrices | Belt-and-suspenders; ~5 MB extra. | |

**User's choice:** Emit 45×45 wide TSV + M2 slices per-run (Recommended)
**Notes:** None — accepted recommendation.

---

### F2. MTAG per-run trait grouping

| Option | Description | Selected |
|--------|-------------|----------|
| Claude's discretion; finalize during M2 discuss | M1 emits per-trait munged + 45×45; M2 picks topology. | ✓ |
| Lock now: cluster-based per ancestry | ~6 clusters × 2 ancestries = 12 MTAG runs. Fits Turley ≤6-trait guidance. | |
| Lock now: all-9 per ancestry | Two MTAG runs. Pushes constant-covariance assumption; mitigated by max_FDR. | |

**User's choice:** Claude's discretion; finalize during M2 discuss (Recommended)
**Notes:** None — accepted recommendation.

---

### F3. Per-trait munged file naming

| Option | Description | Selected |
|--------|-------------|----------|
| `<trait>.<ancestry>.<consortium>.<year>.sumstats.gz` | Lowercase trait tokens match YAML keys. Dotted separator. | ✓ |
| `<trait>_<ancestry>_<consortium>_<year>.sumstats.gz` | T1 spine underscore convention. Consortium-underscore ambiguity. | |
| GCST-accession-based naming | Publication-provenance-first. Hurts readability. | |

**User's choice:** `<trait>.<ancestry>.<consortium>.<year>.sumstats.gz` — trait tokens match YAML keys (Recommended)
**Notes:** None — accepted recommendation.

---

### F4. HapMap3 vs full-coverage duality

| Option | Description | Selected |
|--------|-------------|----------|
| Emit full-coverage (.tsv.bgz/.parquet) + HM3-munged (.sumstats.gz) in parallel | Two artifact classes, both per trait × ancestry. | ✓ |
| HM3-munged only; amend CPASSOC input policy | Single artifact; loses rare-variant coverage. | |
| Full-coverage only; skip LDSC munge; derive HM3 slice in M2 | Risks Success Criterion 3. | |

**User's choice:** Emit full-coverage harmonized + HM3-munged in parallel (Recommended)
**Notes:** None — accepted recommendation.

---

## Claude's Discretion (deferred to planning)

- Exact schema of `config/trait_inventory.yaml` field set
- Snakemake rule layout (file partitioning)
- Conda environment partitioning
- LSF queue selection per rule
- CPASSOC variant-set alignment algorithm
- Parquet region-slice helper signature
- Retry / re-download policy for portal-fetch failures
- MTAG per-run trait grouping (deferred to M2 discuss per F2)

## Deferred Ideas

- MTAG per-run trait topology lock (to M2 discuss)
- DIAMANTE AFR + HIS strata (DIAGRAM gate on manuscript acceptance; quarterly recheck)
- Aragam author email for AFR file (last-resort contingent under D-03)
- dbGaP phs001672 DUA submission (de-prioritized per D-06; re-open only if primary + fallback both fail)
- Q5 MAGIC FTP port-21 egress test (planner pre-flight, not a gray area)
