# Phase ta-r4: Head-to-head re-analysis and submission - Research

**Researched:** 2026-10-21
**Domain:** Summary-statistic colocalization methodology (coloc.abf vs SuSiE-RSS + coloc.susie), LD reference panels, allele orientation, Snakemake/LSF regeneration on purge-prone storage
**Confidence:** HIGH on code paths and data availability (measured this session); MEDIUM on design recommendations; LOW items are flagged in the Assumptions Log

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Analysis arms (Carter, 2026-10-21)
- **D-01:** Three arms on identical sumstats, regions, priors and SuSiE policy:
  **A1** `coloc.abf` (single causal variant, uses no LD matrix — the method most
  published claims used); **A2** SuSiE-RSS + `coloc.susie` with R = I (identity);
  **A3** SuSiE-RSS + `coloc.susie` with real 1000G Phase 3 EUR LD.
  A1 vs A3 = "literature method vs best practice"; A2 vs A3 = the pure LD-matrix
  effect. The manuscript must stop conflating `coloc.abf` with "identity LD".

#### Zero-credible-set rule (Carter)
- **D-02:** When either trait has 0 credible sets under an arm, the pre-specified
  fallback is `coloc.abf` on the same region, reported as a **separately labelled
  outcome** (`fallback_abf`). The per-arm no-CS rate is itself a reported result.
  Fallback and `coloc.susie` values are never pooled silently.

#### LD panels (Carter)
- **D-03:** Primary real-LD panel = 1000G Phase 3 EUR (n≈503). Sensitivity arm
  **A3-UKB** = public Pan-UKBB / UKB LD matrices (most GWAS here are UKB-derived),
  testing reference mismatch directly.
- **D-04:** The UKB sensitivity panel is built under a **separate path** that the
  EUR `ld_panel` chain cannot resolve to (m3-04c BLOCKER-B: `EUR_ukbb_pub` is the
  EUR chain head and would silently replace the primary panel).

#### Pre-registration (Carter)
- **D-05:** The R4 analysis plan (arms, estimands, decision rules, outcome
  branches, known-answer controls) is drafted as an OSF amendment and **posted by
  Carter on osf.io/az52u before any production fit runs**. Infrastructure,
  data re-acquisition and known-answer reproduction may run before posting;
  the A1/A2/A3 production comparison may not.

#### E-2 allele orientation (Carter — reverses option A of DEC-2026-08-07)
- **D-06:** Fix, then report before/after. Make the EUR sumstats-to-panel join
  allele-aware and apply the computed orientation to QTL betas in QTL-coloc,
  TDD (failing test first). All R4 arms run on fixed code. Report frozen
  (pre-fix) vs fixed numbers side by side. Option A's premise ("Track A is in
  submission") is recorded as false. Needs a new DEC entry superseding
  DEC-2026-08-07 option A for Track A.

#### Scope (Carter)
- **D-07:** Exhaustive: every admissible EUR region × all 10 trait pairs of the
  5 traits, plus the QTL-coloc layer. AFR is a clearly secondary arm on 1000G AFR
  (Track A's original substrate, not the AoU panel).

#### Manuscript (Carter)
- **D-08:** Fresh ~4–5k-word draft written from R4 results; the existing draft is
  source material only. Process provenance (commits, DEC ids, `.planning` paths)
  moves to a Supplementary reproducibility note. Brief-blind adversarial review
  before Carter sees a submission candidate.
- **D-09:** Venue decided **after** results. The 2026-08-12 Nature-first ladder
  stays on record but is not acted on. Draft in a neutral format meanwhile.
  No preprint (DEC-2026-08-12-no-preprint stands).

#### Locked by the orchestrator under the standing rigor-over-speed rule (Carter may override)
- **D-10:** **Regenerate everything.** All 96 real-LD + 95 identity-LD fits, the
  1000G EUR/AFR panels, variant lists, identity payloads, coloc outputs, GTEx v8
  QTL inputs and QTL-coloc tiers were purged from `/share` (30-day purge; never
  git-tracked). Only the 8 harmonized sumstats (sha256-verified against
  `.planning/amendments/sha256_manifest_harmonized_m1.tsv`), 1000G VCFs on /rs1,
  committed code/config and the pinned `r_coloc` env survive.
- **D-11:** **Durable storage.** All R4 data and outputs live on
  `/rs1/researchers/c/ckclinto/...`, never under the purged `/share` tree; the
  repo holds symlinks/manifests. Every produced artifact gets a sha256 manifest
  committed to git. (Inferred: the lost git pack file of 2026-10-21 was likely
  the same purge.)
- **D-12:** **Known-answer controls before the comparison.** Before A1–A3
  production: (a) rebuild the 1000G EUR panel and record per-region md5 + dims;
  (b) reproduce the identity-LD k2d fit summary
  (`.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`, per-fit n_CS) and the
  SH2B3 EUR canonical PP.H4 = 1.0 under a reproduction policy with the frozen
  effective `max_iter = 100`; mismatches are findings to report, never numbers
  to adjust. Production then uses the current corrected policy (commit
  `02c4404`: retry honours max_iter 200), disclosed.
- **D-13:** **No silent identity fallback.** Every fit JSON must carry
  `ld_source`/panel path + md5; a run asserts arm A3 never read `diag(n)`
  (`run_susie_rss.R:1114` falls back and exits 0). Enforced by a named test.
- **D-14:** **Config overlays.** AFR runs need an overlay clearing
  `ld_read_path`, `allele_aware`(AFR-AoU path), `coloc` and `occlusion_lockstep`
  AoU routing so AFR reads 1000G AFR; the identity overlay must not depend on the
  real panel existing. Restore `envs/qtl_processing.yml` from `c2dfb08^`.
- **D-15:** **Track B isolation.** No R4 step builds or touches `EUR_ukbb_pub`,
  `EUR_aou` or AoU paths; no R4 commit changes Track B behaviour (AFR-gated code
  paths keep their tests green).
- **D-16:** **Branch.** Shared multi-terminal GPFS tree → no branch switching;
  commit on the current branch with explicit-path staging; push after each wave.

### Claude's Discretion
- Wave structure, Snakemake overlay design, how Pan-UKBB LD is fetched/sliced,
  estimand formulas (e.g. paired ΔPP.H4 per pair, agreement at 0.8/0.5,
  calibration on negative-control loci), figure design.
- Compute placement (LSF queues per `feedback_lsf_queues`).

### Deferred Ideas (OUT OF SCOPE)
- AoU-AFR-LD re-analysis of Track A regions — belongs to Track B once its panel exists.
- Newer GWAS vintages (DIAMANTE 2022, GBMI, Yengo 2022) — Track B companion study.
</user_constraints>

<phase_requirements>
## Phase Requirements

No explicit REQ IDs were passed. These existing REQUIREMENTS.md entries are load-bearing for ta-r4:

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-SUSIE-RSS-POLICY [A] | `config/susie_policy.yaml` loaded by finemap; min_abs_corr sweep reported | The policy file and its loading are unchanged since 04-21 (`finemap.smk:372`). The post-hoc `min_abs_corr` sweep is already emitted per fit (`run_susie_rss.R`, `MIN_ABS_CORR_SWEEP`). A reproduction overlay with `max_iter_primary=100, max_iter_retry=100` is needed (see Pattern 4). |
| REQ-NEGATIVE-CONTROLS [AB] | ≥3 negative-control sets, all null | `config/negative_controls.yaml` (pigmentation, blood group, HLA). See Pitfall 15: under D-02, null loci fall back to LD-free abf, so they **cannot tell the arms apart**. A simulation null is recommended. |
| REQ-PP.H4-THRESHOLD-SWEEP [A] | Tier counts at PP.H4 ∈ {0.5,0.7,0.8,0.9} | `config/pph4_thresholds.yaml` exists (sweep [0.5,0.7,0.8,0.9]). Estimand E2 reports agreement at all four values. |
| REQ-OSF-PREREG [AB] | Guard refuses execution until the amendment is posted | Precedent: R3 fired **without** its amendment (`osf_deviations.md:39`), and GSD `mode: yolo` auto-selects the first option at blocking gates. This needs a **code-level sentinel guard** (Pattern 7). |
| REQ-PUBLIC-DATA-ONLY [AB] | Public or standard-DUA data only | 1000G (Zenodo CC-BY-4.0), Weissbrod UKB LD (AWS Open Data, CC BY-4.0), Pan-UKBB (public S3) and eQTL Catalogue are all anonymous downloads, verified this session. |
| REQ-PATH-PARAMETERIZATION [AB] | No `/rs1/researchers` literals in `src/` or `config/` | R4 overlays must use repo-relative symlink paths (`data/r4/...` → /rs1), not absolute /rs1 literals (Pattern 1). |
| REQ-SNAKEMAKE-CI [AB] | Pinned envs | Restore `envs/qtl_processing.yml` (unpinned `>=` specs) and export a lockfile after the solve (Pattern 8). |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- 100% public data; standard academic DUAs only. No wet-lab, no proprietary data.
- Solo author: rigor comes from triangulation, OSF pre-registration, a Snakemake-pinned pipeline and hold-out replication.
- Timeline is not binding. Rigor over speed (also memory `feedback_rigor_over_speed`).
- Stack: R (coloc, susieR, …), Python, bash, Snakemake, conda. No web/JS stack.
- GPFS: **no worktree isolation**. CLAUDE.md asks for `git.isolation: branch`, but D-16 overrides for this phase: commit on the current branch with explicit-path staging only (memory `feedback_multi_terminal_staging`: never `git add .`/`-A`).
- Every repo edit goes through a GSD workflow (`/gsd-execute-phase` for this phase).
- Snakemake must be `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (7.32.4, Python 3.11; memory `project_python_311_pin`). Never run it from miniconda3 base.
- LSF: use the `standard`/`long`/`serial` queues via `config/bsub_wrapper.sh` (it sets `-W` to the queue max). Never use `short`.
- Public text must frame this as original research. Never use "pivot", "revision", "salvage" or "audit-driven fix". Note: the current draft's line 1 reads "Track A — First-pass pivot draft".
- `aou-ld-pipeline` skill = Track B. Not in scope; do not load.

## Summary

The three-arm design (D-01) can be built almost entirely from code already in the repo. That code is now mainly a Track B (AoU) fire path: `run_susie_rss.R` is **code-frozen** by `tests/m3/test_source_freeze_pins.py` (`R_CODE_REF = "bf04199"`, whole-file floor plus 5 symbol pins). Any edit to it needs an authorized unfreeze and a re-pin. The recommended design therefore **edits none of the frozen fit code**:

- A new, config-gated rules file (`ta_r4.smk`) calls the frozen `run_susie_rss.R` through R4-only config overlays.
- Those overlays put EUR on the `ld_read_path` allow-list, which arms the existing authoritative-declared-panel stop and the existing allele-aware 4-key join for EUR.
- `ld_panel.EUR` is replaced wholesale with a pinned R4 panel path.
- A2 uses an **explicit `R = I` payload built from the A3 panel's own variants frame**, so the A2 and A3 variant sets are identical by construction.

Snakemake 7.32.4 `update_config` merges dicts recursively and **replaces lists wholesale** (verified this session). That is what makes "replace the EUR chain" safe and lets it touch nothing in `config/pipeline.yaml`.

Several premises in CONTEXT.md and the frozen record were found false or incomplete. The planner must handle each:

1. **The SH2B3 PP.H4 = 1.0 known answer was not produced at max_iter 100.** The R2 re-fire swapped in **L=15, max_iter 500/1000, post-02c4404** fits for BMI/HTN/stroke, plus Stage-2 L=10 fits for asthma/T2D (`ta-sh2b3-W2-…-SUMMARY.md:102,155`).
2. **`bmi.EUR.tsv.bgz` has no REF/ALT/EAF columns.** Under the E-2 fix its allele-aware join would hard-stop. Alleles can be restored from the same Yengo-2018 release already on disk.
3. **The EUR panel `.rds` carries `A1/A2`, not `REF/ALT`** (`plink_ld_to_rds.R:108-117`). The allele-aware matcher requires `REF/ALT` and would reject the panel. The Stage-2 plink call also lacked `--keep-allele-order`, so LD is signed on the panel-minor allele while BETA is signed on the effect allele. This is the E-2 mechanism on the **fine-map side for EUR**, not only in QTL-coloc.
4. **Applying the existing `join$orient` to QTL betas would be wrong.** That vector orients the GWAS-derived catalog to the panel. QTL betas are signed on the GTEx GRCh38 ALT, which is a different allele from the GWAS effect allele about half the time. QTL betas must be oriented to the panel using the QTL's own alleles.
5. **`coloc.abf` and `coloc.susie` have different default `p12`** (1e-5 vs 5e-6; verified from coloc 5.2.3 formals). Priors must be set explicitly and identically.
6. **The legacy coloc manifest admits only `status==ok` fits (tier3 gate).** That is why SH2B3 EUR had one R1 pair. Arm-dependent attrition would unmatch the design, so R4 needs a fixed, pre-registered all-pairs manifest.
7. **AFR never had a real LD panel in Track A.** The VCF builder writes identity placeholders above 6,000 catalog positions. The AFR sample list on /rs1 has **504** samples (5 continental populations), not the 661 the draft states.

**Primary recommendation:** Build R4 as an isolated `ta_r4.smk` with explicit overlays, receipts and named validators. Fix E-2 in three TDD units: BMI allele restoration, panel `REF/ALT`, and QTL-beta orientation behind a default-off flag. Reproduce the known answers under **two** legacy routes before the OSF gate. Gate production on a Carter-committed OSF sentinel file, not on a GSD checkpoint alone.

## Standard Stack

### Core
| Library / tool | Version | Purpose | Why standard |
|---|---|---|---|
| R | 4.4.2 | runtime | pinned `envs/r_coloc.yml`; env `/rs1/.../conda_envs/r_coloc` [VERIFIED: Rscript this session] |
| susieR | 0.14.2 | SuSiE-RSS fine-mapping, `estimate_s_rss`, `kriging_rss` | Zou 2022 reference implementation [VERIFIED] |
| coloc | 5.2.3 | `coloc.abf`, `coloc.susie` (via `coloc.bf_bf`), `runsusie` | Wallace 2020/2021 reference implementation [VERIFIED] |
| data.table / Matrix / jsonlite / yaml / digest / optparse | 1.16.4 / 1.7.5 / 2.0.0 / 2.3.10 / 0.6.39 / 1.7.5 | I/O, receipts | already in env [VERIFIED] |
| Snakemake | 7.32.4 (Python 3.11, smoke_dev) | DAG | project pin [VERIFIED] |
| PLINK 1.9 | 1.90b6.21 (`envs/plink.yml`) | `--r square` LD from bfile/VCF | Stage-2 panel builder; **not on PATH** — runs via `--use-conda` [VERIFIED: `command -v plink` empty] |
| pytest | 9.0.3 (smoke_dev) | test runner | existing suites [VERIFIED] |

### Data sources (all anonymous, verified live 2026-10-21)
| Source | Exact location | Size | License | Build |
|---|---|---|---|---|
| LDSC 1000G Phase 3 plinkfiles (EUR QC, HM3) | Zenodo record 10515792, `1000G_Phase3_plinkfiles.tgz` | 288,277,344 B, **md5 a7773ab485827b533cb300c76356d76b** | CC-BY-4.0 | GRCh37 [VERIFIED: Zenodo API] |
| 1000G Phase 3 VCFs (AFR panel) | `/rs1/.../region_analysis/data_raw/1kg/vcf` (48 files) + `EUR.samples` (503) + `AFR.samples` (504) | 17 GB | public | GRCh37 [VERIFIED: ls/wc] |
| Weissbrod/PolyFun UKB 337k LD (A3-UKB primary) | `s3://broad-alkesgroup-ukbb-ld/UKBB_LD/chr{c}_{s}_{e}.{npz,gz}`; e.g. `chr12_111000001_114000001.npz` | 640,814,458 B for that tile | CC BY-4.0 (AWS Open Data) | hg19 [VERIFIED: anonymous S3 list; registry page] |
| Pan-UKBB EUR LD (alternate only) | `s3://pan-ukb-us-east-1/ld_release/UKBB.EUR.ldadj.bm` (Hail BlockMatrix, upper-triangular) + `UKBB.EUR.ldadj.variant.ht` (+ `.b38.ht`) | large | public | GRCh37 [VERIFIED: S3 list; CITED pan.ukbb docs] — **needs Hail** |
| GTEx v8 via eQTL Catalogue (QTS000015) | `https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/QTS000015/{QTD}/{QTD}.all.tsv.gz` (eQTL), `.cc.tsv.gz` (sQTL) | eQTL ≈3.8 GB/tissue; sQTL ≈1.0 GB/tissue | open | GRCh38 [VERIFIED: HEAD 200, Content-Length; note the sQTL `.all` URL 404s, `.cc` exists] |
| 8 Track A harmonized sumstats | `data/processed/sumstats_harmonized` → `/rs1/.../sumstats_harmonized_fixed` | — | public | GRCh37 [VERIFIED: inventory sha256] |
| Yengo 2018 BMI with alleles (E-2 restoration) | `sumstats_harmonized/bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz` (EA/OA/EAF; sha256 0147fbcd… in manifest) and raw `data_raw/sumstats/bmi.EUR.raw.gz` (Tested_Allele/Other_Allele) | — | public | GRCh37 [VERIFIED: headers] |

### Alternatives Considered
| Instead of | Could use | Tradeoff |
|---|---|---|
| Weissbrod 337k `.npz` for A3-UKB | Pan-UKBB 420k BlockMatrix | Pan-UKBB is the "official" Pan-UKBB release, but reading it needs Hail plus a JVM on HPC; the `.npz` route has a repo downloader already. **Use Weissbrod**; cite Pan-UKBB as documented alternate (repo already does: `m3_public_eur_ld.smk:71-73`). |
| LDSC 1000G bfiles (Zenodo) for the EUR panel | Rebuild from /rs1 VCFs (503 EUR) | Only the LDSC bfiles reproduce the frozen Stage-2 panel (HM3-filtered; `ld_reference.smk:247-260`). The VCF route gives a different variant set and the 6,000-cap placeholder hazard. **Use Zenodo bfiles** for EUR (primary and reproduction). Use VCF + plink only for AFR. |
| Full-file QTL downloads | Remote tabix per region | Repo design explicitly forbids remote tabix (T-02-06 rate limiting, `qtl_download.smk:11-14`). Keep full downloads (~235 GB to /rs1; 28 TB free). |

**Installation:** no new packages. `envs/qtl_processing.yml` is restored verbatim from `c2dfb08^` (the specs are unpinned `>=`; export a lockfile after the solve).

## Architecture Patterns

### Recommended structure (new files only; nothing in Track B files changes behaviour)
```
config/
├── ta_r4/overlay_base.yaml          # paths.results_root, finemap.output_dir, conda-free knobs, ta_r4.enabled
├── ta_r4/overlay_A3_1kg.yaml        # ld_read_path EUR on, allele_aware true, coloc true; ld_panel.EUR = [R4 1kg]; pin
├── ta_r4/overlay_A2_identity.yaml   # same but ld_panel.EUR = [R4 identity payload dir]; pin
├── ta_r4/overlay_A3_ukb.yaml        # ld_panel.EUR = [R4 ukb337k dir]; pin; own results_root
├── ta_r4/overlay_AFR.yaml           # occlusion_lockstep.enabled false; ld_panel.AFR = [R4 1kg AFR]; pin; ld_read_path AFR allele_aware true
├── ta_r4/overlay_repro_legacy.yaml  # ld_read_path.ancestries [] ; policy -> susie_policy_repro_iter100.yaml ; legacy panel dir
├── ta_r4/susie_policy_repro_iter100.yaml   # max_iter_primary 100, max_iter_retry 100
├── ta_r4/coloc_priors.yaml          # p1, p2, p12 (single source for A1, A2, A3, A3-UKB, QTL)
└── ta_r4/pair_manifest.tsv          # pre-registered, all pairs, no tier gate (committed BEFORE the OSF post)
src/snakemake/rules/ta_r4.smk        # included only when config ta_r4.enabled; rules: r4_panel_*, r4_run_finemap (receipt), r4_coloc_susie, r4_coloc_abf, r4_qtl_coloc
src/snakemake/scripts/ta_r4/
├── restore_bmi_alleles.py           # E-2 unit 1
├── make_matched_identity_payload.R  # A2 payload = A3 panel variants + R = I
├── run_coloc_abf_r4.R               # A1 + D-02 fallback
├── validate_r4_fits.py              # D-13 enforcer (receipts, ld_matrix == declared, no identity strings)
└── r4_osf_gate.py                   # sentinel check
tests/ta_r4/                         # RED-first tests, named enforcers
data/r4 -> /rs1/researchers/c/ckclinto/coloc_analysis/ta_r4   # symlink (D-11); created by bin/r4_link_storage.sh
.planning/phases/ta-r4-…/manifests/  # committed sha256/md5 + dims manifests
```

### Pattern 1: Durable storage through a repo-relative symlink (D-11, REQ-PATH-PARAMETERIZATION)
**What:** Every R4 config path is repo-relative under `data/r4/…`. `data/r4` is a symlink to `/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4/`. An idempotent `bin/r4_link_storage.sh` recreates the link, and a test asserts `os.path.realpath("data/r4").startswith("/rs1/")`.
**Why:** The repo itself sits on the purged `/share` tree. Directory mtimes cluster at about 00:34–00:41 on purge dates, and the inventory found dangling links whose targets were purged. Absolute `/rs1` literals in `config/` would violate REQ-PATH-PARAMETERIZATION's grep acceptance.
**Also:**
- Put the Snakemake conda prefix on /rs1 (e.g. `--conda-prefix /rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4`).
- Isolate `pkgs_dirs` through `CONDARC` (memory `reference_snakemake_conda_clean_tarballs_shared_cache`: Snakemake runs `conda clean --tarballs` on every writable pkgs dir).
- Put LSF logs under `data/r4/logs/`.

### Pattern 2: Arm selection by overlay, not by code (A2 / A3 / A3-UKB / AFR)
**What:** Use the existing gates as they ship.
- `ld_read_path.ancestries` contains the ancestry. This yields `--ld-authoritative true` (declared panel is the **sole** candidate; unreadable, `use_identity`, no-matrix or sub-`MIN_LD_MIN_USE` → `stop()`, `run_susie_rss.R:642-657`) and `--ld-allele-aware true` (4-key join with z negation, `run_susie_rss.R:220-323,1080-1092`).
- `ld_panel.<ANC>` is **replaced** with a single R4 entry and `pin.<ANC>` is set to it. `resolve_ld_path` raises `ValueError` or `FileNotFoundError` if the pin is wrong or the file is missing (`ld_panel.py:113-129`).
**Example (overlay_A3_1kg.yaml):**
```yaml
# Source: semantics verified against snakemake.utils.update_config (7.32.4): dicts merge, lists replace
ld_read_path: {enabled: true, ancestries: [EUR], allele_aware: true, coloc: true}
ld_panel:
  EUR:
    - {source: "EUR_1kg_r4", path: "data/r4/ld/EUR_1kg_r4/{region_safe}.rds"}
  pin: {EUR: "EUR_1kg_r4"}
paths:   {results_root: "data/r4/results/A3_1kg", ld_reference: "data/r4/ld"}
finemap: {output_dir: "data/r4/results/A3_1kg/fine_mapping", ld_reference_dir: "data/r4/ld_dir_unused_A3"}
```
**Caveats:**
- With EUR on the allow-list, `ld_matrix_region_id` applies the curated→M2 crosswalk to EUR (`ld_read_path.py`). The R4 chain templates on `{region_safe}`, so the resolved path does not move. Pin this with a test.
- Point `finemap.ld_reference_dir` at a **non-existent** directory. The `--ld-dir` back-compat fallback (`run_susie_rss.R:149-166`) then has nothing to fall to, and a missing declared file degrades only to `ld_dir_missing` (caught by the receipt; see Pattern 6).

### Pattern 3: A2 identity payload derived from the A3 panel (matched variant sets, D-01, D-14)
**What:** `make_matched_identity_payload.R` reads `EUR_1kg_r4/{region}.rds` and writes `list(R = Matrix::Diagonal(n) or diag(n), variants = <same frame>, ld_source = "identity_matched_r4")` to `data/r4/ld/EUR_identity_r4/{region}.rds`.
- It carries an **explicit** `R`. The declared-mode loader rejects `use_identity=TRUE` payloads (`run_susie_rss.R:426-439`), which is the loud behaviour we want. The k2d-style payload (`make_identity_ld_refs.R`, `R=NULL`) must **not** be used for A2.
- The identical variants frame makes `subset_idx` and `allele_orient` identical between A2 and A3. Enforce this with a named test.
- The identity overlay no longer depends on any other panel existing. This resolves hazard 4: the old overlay left the hard-coded EUR chain demanding the real panel.
- Under `R = I`, flipping a z sign changes nothing (PIP invariant), so orientation is moot in A2. It is still computed, which keeps the code path identical.

### Pattern 4: Known-answer reproduction by two independent routes (D-12)
- **Route L (legacy source):** `git show 3dd76df:src/legacy/region_analysis/scripts/run_susie_rss.R` into the R4 scratch area. `3dd76df` is the last commit before the 2026-04-22 fire; no fit-code commits sit between it and the k2d fire `08beb4c` [VERIFIED: git log]. Run under legacy semantics (no `--ld-file`) on a **legacy-identical panel** (LDSC bfile, plink **without** `--keep-allele-order`, `plink_ld_to_rds.R` unchanged) and legacy catalogs.
- **Route C (current code, reproduction policy):** current `run_susie_rss.R` + `overlay_repro_legacy.yaml` (`ld_read_path.ancestries: []`, policy `max_iter_primary: 100, max_iter_retry: 100`).
- **Discriminating check:** Route C ≡ Route L per fit (n_CS, cs_sizes, PIP vector `identical()` within 1e-10). Any difference is code drift since 04-22 and is a finding.
- **Known answers available on disk:**

| Target | Value | Source |
|---|---|---|
| k2d identity per-fit `status`, `n_CS`, `cs_sizes` | 95 rows (65 ok / 24 too_many_variants / 6 no_variants) | `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` (k2d used the legacy `R=NULL` payload on the unrestricted catalog subset) |
| Stage-2 real-LD aggregates | 51/96 non-empty; 48 ok / 24 too_many_variants / 18 non_converged / 6 no_variants; H3 33/60, 27/60, 19/60, 41/60 | `TRACK-A-FROZEN-NUMBERS.md` |
| SH2B3 EUR panel dims | 895 variants | `ta-sh2b3-W1.5-ld-audit.md:81` |
| SH2B3 EUR per-trait `ld_overlap` / fraction | bmi **170 / 0.9884**, htn **589 / 0.980**, stroke **622 / 0.9811** | surviving `results_lsweep_L15.preNiter500.bak.*/…json` [VERIFIED this session] |
| L-sweep n_CS at niter 100 | L15 13/5/3; L20 14/4/4; L30 14/4/4 | `ta-sh2b3-W1-convergence-report-niter100.tsv` |
| L-sweep n_CS at niter 1000 | L15 13/5/3; L20 15/4/4; L30 15/4/4 | `ta-sh2b3-W1-convergence-report.tsv` |
| **SH2B3 R2 PP.H4** | bmi–htn 1.0 (hit rs3184504, nsnps 168, n_cs 13 × 5); htn–stroke 1.0; htn–t2d 1.0; bmi–t2d 4.3e-27; stroke–t2d 0 | `results/multitrait/coloc_susie_R2/*.json`, `ta-sh2b3-W2-pp-h4-report.tsv` (tracked) |

- ⚠ **Premise correction (Pitfall 1):** the R2 PP.H4 = 1.0 was computed on **L=15, policy 500/1000, post-02c4404** fits for BMI/HTN/stroke, plus the Stage-2 L=10 fits for asthma/T2D. It was **not** computed at max_iter 100. Reproduce exactly that mixture. Report separately what the same pairs give at L=10 / iter-100 and under production policy.

### Pattern 5: Pre-registered all-pairs manifest (D-07; matched design)
Do **not** use `create_coloc_manifest.py`. It admits only tier-table rows (`status in {ok, success}`, `filter_finemap_summary.py:374`), which makes the pair set depend on the arm. Commit a static `config/ta_r4/pair_manifest.tsv`:
- EUR: 10 admissible regions × 10 pairs = 100 rows.
- AFR: up to 11 autosomal regions × 3 pairs (asthma, stroke, t2d).
- Negative-control loci rows.

Each row is run in every arm. A pair whose fit is `non_converged` still runs; convergence becomes a reported covariate.

### Pattern 6: D-13 receipts without editing the frozen script
The `r4_run_finemap` rule shell does the following:
1. `test -s {input.ld_matrix}`.
2. `md5sum` the declared panel and compare it with the committed panel manifest; on mismatch, `exit 3`.
3. Run the frozen `run_susie_rss.R` exactly as `finemap.smk:441-455` does.
4. Write `{fit}.ld_receipt.json` with `{declared, md5, size, arm, overlay_sha, git_sha, policy_sha1}`.
5. Run `validate_r4_fits.py` on that single JSON and exit non-zero if any condition fails.

`validate_r4_fits.py` (A3, A3-UKB, AFR-A3) requires all of the following:
- `ld_matrix == ld_file_declared`
- `ld_authoritative` true
- `ld_status` matches `^ld_loaded;(overlap_ok|partial_overlap);`
- no `identity` substring in `ld_matrix`, `ld_status` or `convergence_status`
- `ld_allele_aware` true

For A2 it requires `ld_matrix` == the identity payload path.

This closes all three silent shapes: the `:1114` NULL-R branch, the `:1144` ladder-exhaustion `identity_fallback`, and the `LD_DECLARED_ABSENT` degradation (`:157-165`).

### Pattern 7: OSF gate as a sentinel file (D-05, REQ-OSF-PREREG)
- Carter commits `.planning/phases/ta-r4-…/OSF-R4-POSTED.json` containing `{url, posted_utc, amendment_sha256, head_sha}`.
- Every production rule (`r4_*` with `arm in {A1, A2, A3, A3-UKB, AFR}` and `stage == production`) has an input-function guard that raises unless the sentinel exists and its `posted_utc` is earlier than now.
- Known-answer rules carry `stage == repro` and are exempt.
- The test suite contains a negative control: with the sentinel absent, `snakemake -n <production target>` must fail.
- Rationale: GSD `mode: yolo` auto-selects the first option at `gate="blocking"` (memory `feedback_gsd_automode_bypasses_blocking_fire_gates`), and R3 fired without its posted amendment.

### Pattern 8: Environment restoration
- `git show c2dfb08^:envs/qtl_processing.yml > envs/qtl_processing.yml`. `src/snakemake/rules/envs/` is the same directory listing as `envs/`; confirm whether it is a symlink before writing. Five rules reference it (`qtl_coloc.smk:419,543,562` and others).
- After the first solve, `conda env export --no-builds > .planning/phases/ta-r4-…/manifests/env_lock_qtl_processing.yml`. Do the same for `plink.yml` and `python_stats.yml`; `r_coloc` is pinned already.

### Anti-Patterns to Avoid
- **Building anything under `data/processed/ld_reference/{EUR_ukbb_pub,EUR_ukbb_ld,EUR_aou,EUR}`.** All four are EUR-chain members (`pipeline.yaml:213-217`). BLOCKER-B is not only `EUR_ukbb_pub`: `download_ukbb_ld_tiles` writes `EUR_ukbb_ld/`, which is chain entry 3.
- **Running R4 through `finemap.smk::run_finemap` with an edited base `pipeline.yaml`.** Changes Track B behaviour (D-15).
- **Reusing `make_identity_ld_refs.R` payloads for A2.** Unmatched variant set; rejected in declared mode.
- **Letting `coloc.abf` and `coloc.susie` use their defaults** (p12 1e-5 vs 5e-6).
- **Pooling `fallback_abf` rows with `coloc.susie` rows** (D-02).

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Allele-aware sumstats↔panel join | a new matcher | the shipped `match_indices_allele_aware` (inside frozen `run_susie_rss.R`), armed by `ld_read_path` | Already handles multiallelics, palindromes, ambiguity and unusable alleles, with counters to JSON. A drift-guarded twin `ld_allele_join_indices()` exists for coloc (`tests/m3/test_qtl_coloc_allele_join.py`). |
| LD-mismatch diagnostics | custom z-vs-R checks | `susieR::estimate_s_rss` (already serialized as `d3b_ld_z_consistency_s`), `susieR::kriging_rss` (D3), allele-flip LR | Zou 2022's diagnostics; already emitted per fit. |
| Multi-signal colocalization | conditional coloc | `coloc::coloc.susie` on annotated fits (`coloc:::annotate_susie` already applied before `saveRDS`) | Wallace 2021. |
| Panel path resolution | path string building | `ld_panel.resolve_ld_path` with `pin` | Raises on a missing pinned file at DAG time. |
| Code-freeze checks | byte diffs | `tests/m3/source_freeze.py::assert_code_frozen` | Comment-insensitive code pin; reuse it to pin R4 copies. |
| UKB tile download | new S3 client | `download_ukbb_ld_tiles.py` (boto3 UNSIGNED) **with a fixed loader** (Pitfall 10) and a new output dir | Already handles multi-tile and block-diagonal concatenation. |

**Key insight:** this domain's failure mode is silent numeric drift, not crashes. Every reused component above was built in response to a measured silent-drift incident. Prefer arming existing loud paths over new code.

## Runtime State Inventory

(This is a regeneration/migration-shaped phase.)

| Category | Items found | Action required |
|---|---|---|
| Stored data | All Track A fits, panels, catalogs, coloc and QTL outputs are **absent** (inventory). Surviving: 8 sumstats; `results/multitrait/coloc_susie_R2*/` JSONs (tracked); `results_lsweep_*.bak.*` JSONs (untracked, purge-exposed); `.planning/debug/stage2_narrow_validation/*` (10 real + 7 identity `fit.rds`); `targeted_rerun_package_20260507_222752.zip`. | **Copy the untracked known-answer survivors to /rs1 and sha256 them in W0** before the next purge. The lsweep JSONs and narrow-validation fits sit on `/share` now. |
| Live service config | OSF az52u records (posting is Carter's); `osf-correction-v2` **drafted, not posted**, and its text says the code is not changed. Under D-06 it becomes stale. | Decision for Carter: supersede it with an R4 amendment section, or post a revised v3. |
| OS-registered state | None. No cron/LSF recurring jobs for Track A [VERIFIED: nothing referenced in STATE; LSF jobs are one-shot]. | None |
| Secrets / env vars | None needed. All sources are anonymous. `SUSIE_MAX_VARIANTS` env is set in the rule shell (16000). The AFR builder reads `LD_MAX_VARIANTS` env (default 6000). | Set `LD_MAX_VARIANTS` explicitly in the AFR rule, or use the plink route. |
| Build artifacts | `.snakemake/conda/*` purged to shells; `.snakemake/metadata` gone. `envs/qtl_processing.yml` deleted. Stale untracked dirs at repo root (`results_lsweep_*`, `targeted_rerun_*`). | New conda prefix on /rs1. Restore the env. Leave stale dirs untouched (other terminals). |

## Common Pitfalls

### Pitfall 1: The D-12(b) SH2B3 known answer is mis-specified
**What goes wrong:** Running SH2B3 at L=10 with max_iter 100 and calling the outcome a reproduction "failure" or "success".
**Why it happens:** CONTEXT.md says "PP.H4 = 1.0 under … max_iter = 100". The R2 fire actually swapped in L=15, 500/1000 post-fix fits for BMI/HTN/stroke (`ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md:45,102,155`; `TRACK-A-FROZEN-NUMBERS.md` Wave-3 block).
**How to avoid:** Reproduce the exact R2 configuration. Record the premise correction in the LOG and in a DEC. Carter acknowledges at W3.
**Warning signs:** n_cs_a = 13 and n_cs_b = 5 are the R2 fingerprint. At L=10 you cannot get 13.

### Pitfall 2: `bmi.EUR` has no alleles
**What goes wrong:** Under `allele_aware` the BMI EUR fits stop with `alleles_unavailable_sumstats`. Without the fix, BMI's z sign versus panel orientation is unknowable.
**Fix:** `restore_bmi_alleles.py` joins on CHR + POS + SNP_ID to `bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz` (same Yengo 2018 release; 2,327,244 vs 2,336,269 rows). Write REF = OA and ALT = EA to a new file with its own sha256.
**Discriminating test:** BETA, SE and P must be **byte-identical** between the frozen file and the source for every joined row. If BETA signs agree, EA is proven to be the frozen BETA's effect allele. Report unmatched rows as a count; they are dropped from R4, not imputed.
**Deviation:** disclose in the OSF amendment as "allele columns restored from the same release".

### Pitfall 3: EUR panel `.rds` lacks REF/ALT, and Stage-2 LD was signed on the panel-minor allele
**What goes wrong:** Allele-aware EUR rejects the panel (`alleles_unavailable_panel` → stop). The frozen legacy path joined by SNP_ID or CHR:POS with no orientation. Panel A1 (minor allele in the panel, because PLINK 1.9 sets the major allele to A2 unless `--keep-allele-order` [CITED: cog-genomics.org/plink/1.9/data]) differs from the GWAS effect allele for roughly half of SNPs.
**Fix:** In the R4 panel rule, run plink with `--keep-allele-order` and give `plink_ld_to_rds.R` an opt-in flag (e.g. `--emit-ref-alt`) that adds `REF := A2, ALT := A1` from the **same run's** `.bim`. The flag defaults off, so the existing callers' output stays `identical()`.
**Measure:** Report per-region `ld_allele_flipped / (exact + flipped)` for every EUR fit. This is the fine-map-side E-2 exposure, and the "frozen vs fixed" table must show it.

### Pitfall 4: Orienting QTL betas with the catalog↔panel vector
**What goes wrong:** `join$orient` in `run_qtl_coloc.R:471-479` orients the **GWAS catalog** to the panel. GTEx betas are signed on the GRCh38 `variant_id` ALT (non-reference allele). The harmonized GWAS ALT is the effect/risk allele (`harmonize_sumstats.py:255-262` per code comments). The two differ about half the time.
**Fix:** Parse QTL REF/ALT from `variant_id` (`chr{c}_{pos}_{ref}_{alt}`, `qtl_sources.yaml:28`). Bind each QTL row to its panel row through the existing bridge. Compute `orient_qtl` (+1 exact, −1 transposed, drop palindromic, drop mismatch, all counted), multiply `beta` by it, and record counters to the status JSON.
**Placement:** Gate it behind a new `--qtl-orient true|false` flag that defaults to `false`, so AFR/Track B stays byte-identical (D-15). The R4 overlay turns it on.
**TDD fixture:** one exact, one transposed, one palindromic and one mismatched QTL row against a 4-variant panel. Assert betas and counters. With the flag off, assert the output is `identical()` to the pre-change output.

### Pitfall 5: Different default priors across arms
coloc 5.2.3: `coloc.abf` uses p1 = p2 = 1e-4, **p12 = 1e-5**. `coloc.bf_bf`, which `coloc.susie` uses, has **p12 = 5e-6**, `overlap.min = 0.5` and `trim_by_posterior = TRUE` [VERIFIED: formals]. Pass explicit priors from `config/ta_r4/coloc_priors.yaml` to every call. Recommend p12 = 5e-6 as primary (Wallace 2020 recommendation [ASSUMED from training; verify the citation]) with a 1e-5 sensitivity. The current `run_coloc_susie.R` passes no priors and needs either a new R4 script or a flag. Also record `overlap.min` and `trim_by_posterior` in every output.

### Pitfall 6: Tier-gated manifests unmatch the arms
Covered in Pattern 5. Warning sign: a pair present in one arm's summary and absent from another's.

### Pitfall 7: The identity arm silently uses a different variant set
The k2d payload path (`R = NULL`) fits on sumstats ∩ catalog, which is up to 16,000 variants and **not panel-restricted** (`run_susie_rss.R:1112-1117`). That is why 24 identity fits were `too_many_variants` on dense traits. Use Pattern 3. Keep the k2d semantics only for the reproduction control.

### Pitfall 8: `fallback_abf` rows are identical across A1, A2 and A3 by construction
`coloc.abf` uses no LD. On the same matched variant set with the same priors, the fallback value equals A1 exactly. Report every estimand twice:
- (i) on the **both-arms-have-CS** subset, which is the real LD-matrix effect;
- (ii) on all rows with fallback labelled.

The no-CS rate per arm is a primary reported quantity (D-02).

### Pitfall 9: Identity-LD credible-set purity is trivially 1
`susie_get_cs(fit, Xcorr = R, min_abs_corr = 0.5)` with R = I treats every CS as pure. That is one mechanism of identity "CS inflation": the k2d L = 10 saturation fingerprint `3;3;…;4` appears in 11/95 fits. Report **cross-evaluated purity**: A2 credible sets scored against the real 1000G R. A3 and A3-UKB are scored against each other's R as well.

### Pitfall 10: UKB `.npz` triangle and diagonal convention
`download_ukbb_ld_tiles.py:174-182` densifies the matrix and, if it is not symmetric, applies `(dense + dense.T)/2`. That **halves** every off-diagonal of a one-triangle matrix and makes the diagonal 0.5. PolyFun's own loader uses `ld + ld.T` and asserts diag == 1 [CITED: github.com/omerwe/polyfun finemapper.py]. Memory `feedback_npz_triangle_flag_contract` records a prior doubling bug in this repo.
**Required known-answer test:** on the first real tile, assert diag == 1 after the chosen transform and compare r for a few SNP pairs with the 1000G panel (same sign and magnitude ordering).
**Orientation:** PolyFun treats z as consistent when the sumstats effect allele equals the LD file's `allele1`, so map `ALT := allele1, REF := allele2` [CITED: same source; MEDIUM].

### Pitfall 11: The resolver raises at DAG time when the pinned panel does not exist yet
`resolve_ld_path` checks existence while the DAG is built, so one invocation cannot build panels and fit. Use two stages: panel targets first, then the manifest snapshot, then fits. This is already the house pattern (`scripts/fire_identity_ld_rerun.sh`).

### Pitfall 12: AFR is a new real-LD arm, not a regeneration
- No AFR real LD ever existed in Track A ("36 AFR fits excluded — no AFR LD panel loaded").
- `build_ld_rds.py` writes `use_identity` placeholders when catalog positions exceed `LD_MAX_VARIANTS` = 6000 (`:16, :444-455`). The catalog pools all 8 traits, so most regions exceed it.
- Use plink on the VCF with `--keep AFR.samples --snps-only --max-alleles 2 --maf 0.01 --keep-allele-order --r square --extract <catalog positions>`, then `plink_ld_to_rds.R --emit-ref-alt`.
- The AFR sample list is **504** (YRI, LWK, GWD, MSL, ESN; `pipeline.yaml:83`), not 661 as the draft states. 661 includes ASW and ACB. The AFR GWAS (MVP/GIGASTROKE/DIAMANTE AFR) are largely African American, so pre-register the choice (Open Question 7).
- `overlay_AFR.yaml` must set `occlusion_lockstep.enabled: false` (AFR sumstats otherwise reroute to the absent `sumstats_harmonized_occl`) and replace and pin `ld_panel.AFR`.

### Pitfall 13: `run_susie_rss.R` is code-frozen for Track B
Any code edit turns `tests/m3/test_source_freeze_pins.py::test_run_susie_rss_whole_file_code_is_frozen` RED. The recommended design needs **no** edit. If one becomes unavoidable, it needs Carter's authorization, a DEC, an `identical()` proof at default flags, and a re-pin of `R_CODE_REF` only (per `source_freeze.py` protocol).

### Pitfall 14: Purge, auto-mode and git hazards
- `/share` purge eats outputs, envs, logs and symlink targets.
- `yolo` auto-selects the first option at blocking gates, so put "STOP / wait for Carter" first.
- GPFS loses git objects (memory `reference_gpfs_git_object_store_loss`). Run `git fsck --connectivity-only` before each wave commit, and push after each wave (D-16).
- Concurrent Track B Snakemake in the same workdir is safe only when outputs are disjoint; R4 outputs under `data/r4/` guarantee that.
- Never `snakemake --unlock` blindly.

### Pitfall 15: Negative-control loci cannot discriminate the arms
At null loci SuSiE finds no CS, so every arm falls back to the same abf value (Pitfall 8). A null that tests "identity inflates H4" needs **known truth**. Recommend a pre-registered simulation:
- Sample z ~ N(√n·R·b, R) from the regional 1000G R (and from UKB R, to emulate reference mismatch).
- Scenarios: H3 truth (distinct causal variants at r² ∈ {0.3, 0.6, 0.9}), H4 truth, and H0.
- Run A1/A2/A3 and report false-H4 and true-H4 rates per arm.

This is cheap and is the most direct evidence on the headline hypothesis. Also: **ABO is a reported stroke locus** [ASSUMED], so it is a questionable negative control for stroke pairs. Prefer the pigmentation loci.

### Pitfall 16: Other measured inconsistencies the fresh manuscript must not inherit
- The draft says "50 curated regions"; `config/regions_curated.csv` has **12** (10 admissible EUR).
- The draft says "EUR n = 503". The LDSC bfile `.fam` count is unverified (489 vs 503; Open Question 6).
- `coloc_summary.tsv` md5 drifted three times. It is not a comparison target.
- Hypertension EUR is Evangelou 2018 BP. Trait type and sdY for `coloc.abf` must be pre-registered (Open Question 8).

## Code Examples

### Arming EUR allele-aware + authoritative without touching `pipeline.yaml` (unit test, RED-first)
```python
# tests/ta_r4/test_overlay_semantics.py
import yaml, sys; sys.path.insert(0, "src/python")
from snakemake.utils import update_config            # 7.32.4: dicts merge, lists replace (verified)
from ld_read_path import ld_allele_aware, ld_file_authoritative
from ld_panel import resolve_ld_path

def _cfg(*files):
    c = yaml.safe_load(open("config/pipeline.yaml"))
    for f in files: update_config(c, yaml.safe_load(open(f)))
    return c

def test_A3_overlay_arms_eur_and_pins_r4_panel(tmp_path):
    c = _cfg("config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_A3_1kg.yaml")
    assert ld_allele_aware("EUR", c) == "true" and ld_file_authoritative("EUR", c) == "true"
    assert [e["source"] for e in c["ld_panel"]["EUR"]] == ["EUR_1kg_r4"]      # chain replaced, not merged
    assert "EUR_ukbb_pub" not in yaml.safe_dump(c["ld_panel"]["EUR"])

def test_base_config_untouched():                     # D-15 negative control
    c = _cfg()
    assert ld_allele_aware("EUR", c) == "false" and c["ld_read_path"]["ancestries"] == ["AFR"]
```

### A1 / fallback with explicit priors (`run_coloc_abf_r4.R` core)
```r
# Source: coloc 5.2.3 formals verified this session; beta/varbeta route needs no MAF for cc, sdY for quant
pri <- yaml::read_yaml("config/ta_r4/coloc_priors.yaml")       # p1, p2, p12 single source
d1 <- list(beta = a$BETA, varbeta = a$SE^2, snp = a$snp, type = type_a, N = a$N)
if (type_a == "quant") d1$sdY <- sdY_a                          # pre-registered per trait
d2 <- list(beta = b$BETA, varbeta = b$SE^2, snp = b$snp, type = type_b, N = b$N)
if (type_b == "quant") d2$sdY <- sdY_b
res <- coloc::coloc.abf(d1, d2, p1 = pri$p1, p2 = pri$p2, p12 = pri$p12)
out$method <- if (is_fallback) "fallback_abf" else "A1_abf"     # D-02 label; never "coloc.susie"
out$priors <- pri
```

### coloc.susie with the same priors
```r
res <- coloc::coloc.susie(fit_a, fit_b, p1 = pri$p1, p2 = pri$p2, p12 = pri$p12)  # passed through to coloc.bf_bf
# region-pair statistic (pre-register): max PP.H4 over CS pairs + count of CS pairs with PP.H4 >= 0.8
```

## Estimands and decision rules (to pre-register in the R4 amendment)

The unit is a (region, ancestry, trait-pair) row from the static manifest.

- **E1 (primary):** paired ΔPP.H4(X) = PP.H4(X) − PP.H4(A3) for X ∈ {A1, A2}.
  - Primary summary: median and mean with **region-cluster bootstrap** 95% CI (10 EUR regions as clusters; 10,000 resamples).
  - Paired sign test on the both-have-CS subset.
  - Two confirmatory contrasts only (A1 vs A3, A2 vs A3), Bonferroni α = 0.025 each. Everything else is descriptive.
- **E2:** agreement and discordance at PP.H4 ≥ 0.8 (primary) and 0.5 (secondary), plus the REQ sweep {0.5, 0.7, 0.8, 0.9}.
  - Report 2×2 tables and Cohen's κ.
  - McNemar asymmetry (X calls H4 and A3 does not, vs the reverse) is the direct test of "inflation".
- **E3:** hypothesis-class reclassification (argmax over H0–H4) between arms, especially H3↔H4.
- **E4 (fine-map level):** n_CS, CS size and cross-evaluated purity (Pitfall 9) per fit per arm; the no-CS rate per arm (D-02).
- **E5 (diagnostics):** `estimate_s_rss` λ̂ and kriging outlier counts per A3 and A3-UKB fit. Zou 2022 gives **no numeric cutoff** [CITED: PMC9337707]; report λ̂ as continuous and plot |ΔPP.H4| against it. The repo's s > 0.5 flag is a convention, not a literature threshold.
- **E6:** A3-UKB vs A3 under the same E1–E5. Report on the per-panel native variant sets and on the intersection-matched set, with drop counts.
- **E7:** the E-2 frozen-vs-fixed table:
  - Reproduction legacy numbers vs R4-A3-fixed for fit yields, the SH2B3 pairs and QTL tiers.
  - Per-region flipped share on the fine-map side and the QTL side.
- **E8:** simulation calibration (Pitfall 15): false-H4 under H3 truth by r² bin, per arm.

**Outcome branches** (pre-register; all publishable):

| Branch | Condition |
|---|---|
| `INFLATION_SUPPORTED` | McNemar asymmetry X > A3 at α = 0.025 **and** the cluster-bootstrap CI of median ΔPP.H4 excludes 0 (positive) |
| `NO_SYSTEMATIC_DIFFERENCE` | CI includes 0 and κ ≥ 0.6 |
| `DEFLATION` | Mirror of `INFLATION_SUPPORTED` |
| `HETEROGENEOUS` | CI includes 0 but κ < 0.6 |
| `NON_INFORMATIVE` | Fewer than 10 rows have CS in both arms (n_both < 10) |

The κ and n_both cut-offs are discretion items; lock them in the amendment.

## State of the Art

| Old approach | Current approach | When changed | Impact |
|---|---|---|---|
| `coloc.abf` single causal variant | `coloc.susie` on SuSiE fits, with abf as hybrid fallback when no CS | Wallace 2021 (PLoS Genet 17:e1009440) | D-02 matches the paper's recommendation: "using coloc-SuSiE where possible, but falling back on coloc-single when SuSiE cannot identify any credible sets" [CITED: PMC8504726] |
| Ad hoc LD regularization | SuSiE-RSS with `R̂_λ = (1−λ)R̂ + λI`, λ̂ via `estimate_s_rss`; fix residual variance for out-of-sample LD; "reference panel should not be too small" | Zou 2022 (PLoS Genet 18:e1010299) | **A2 (R = I) is the λ = 1 endpoint of Zou's regularization path.** A λ-path sensitivity (λ ∈ {0, λ̂, 0.1, 0.5, 1}) turns the A2/A3 contrast into a dose-response (exploratory) [CITED: PMC9337707] |
| susieR `max_iterations` arg | `max_iter` (the former was silently swallowed) | repo `02c4404` (2026-04-29) | Frozen fits were capped at 100 even on retry. |

**Deprecated/outdated:**
- `create_coloc_manifest.py` tier gating (for R4).
- `make_identity_ld_refs.R` `R = NULL` payloads (reproduction only).
- eQTL Catalogue sQTL `.all.tsv.gz` URLs: 404. Use `.cc.tsv.gz` [VERIFIED].

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The Stage-2 fire ran at code state `3dd76df` (last commit before the 04-22 fire) | Pattern 4 | Route L reproduces the wrong code. Mitigate: also try `0948a76`, `1635d37`; record which matches. |
| A2 | Wallace 2020 recommends p12 = 5e-6 | Pitfall 5 | Prior choice cited wrongly. Verify before the amendment. |
| A3 | PolyFun/Weissbrod `.npz` is single-triangle with diag 0.5, and z is aligned to `allele1` | Pitfall 10 | A3-UKB LD wrong by a factor of 2 or sign-flipped. Mitigated by the required known-answer test. |
| A4 | The LDSC EUR `.fam` holds 489 (not 503) samples | Open Question 6 | Wrong n in Methods. Verify by `wc -l` after download. |
| A5 | ABO is an established stroke locus | Pitfall 15 | Minor; affects the negative-control choice only. |
| A6 | BMI (Yengo 2018) betas are per-SD (sdY = 1) | Code Examples | A1 BMI ABFs mis-scaled. Verify from the paper. |
| A7 | eQTL Catalogue data are openly licensed (CC-BY) | Standard Stack | Licence statement in Data Availability. |
| A8 | A κ ≥ 0.6 / n_both ≥ 10 branch thresholds are reasonable | Estimands | Discretion item; Carter locks them in the amendment. |
| A9 | `src/snakemake/rules/envs` is a symlink to `envs/` (identical listings observed) | Pattern 8 | The restored file may not be visible to rules. Check with `ls -la`. |

## Open Questions (RESOLVED)

1. **RESOLVED: D-17 (ta-r4-CONTEXT.md).** **D-12(b) premise correction.** Accept "reproduce the R2 SH2B3 configuration (L15 @ 500/1000 for BMI/HTN/stroke + Stage-2 L10 for asthma/T2D)" as the known answer, plus an L10/iter-100 run reported as a separate measurement?
2. **RESOLVED: D-18 (ta-r4-CONTEXT.md).** **BMI allele restoration** from the same-release M1 file (Pitfall 2): approve as a disclosed data step?
3. **RESOLVED: D-19 (ta-r4-CONTEXT.md).** **`osf-correction-v2`** (drafted, unposted; it states the code is unchanged): supersede it with the R4 amendment's E-2 section, or post a revised v3? (DEC-2026-08-12 P-1 requires posting by submission day.)
4. **RESOLVED: D-21 (ta-r4-CONTEXT.md).** **A1 variant set:** matched (the A3-bound set) as primary with "all region sumstats variants" (literature practice) as secondary? (Recommended.)
5. **RESOLVED: D-22 (ta-r4-CONTEXT.md).** **QTL layer arms:** A3 only, or A2 + A3, so the identity effect on GWAS×QTL coloc is measured too? (Recommended: both. Under A2 the QTL side also uses R = I.)
6. **RESOLVED: D-25 (ta-r4-CONTEXT.md).** **EUR panel n:** verify the `.fam` row count after download. The manuscript states the measured value.
7. **RESOLVED: D-20 (ta-r4-CONTEXT.md).** **AFR reference:** 504 continental (current sample list) or 661 including ASW/ACB (better ancestry match for African American GWAS)? Pre-register one; optionally run the other as sensitivity.
8. **RESOLVED: D-25 (ta-r4-CONTEXT.md).** **Trait types for `coloc.abf`:** hypertension EUR (Evangelou 2018: binary HTN or continuous BP?), and sdY values for quantitative traits.
9. **RESOLVED: D-23 (ta-r4-CONTEXT.md).** **Simulation calibration arm (E8):** include as pre-registered secondary? (Recommended under rigor-over-speed.)
10. **RESOLVED: D-24 (ta-r4-CONTEXT.md).** **HLA_6p21 and BMI_Xq24:** confirm "not admissible; reported as such" (no panel). Optionally HLA on the UKB tiles as an exploratory row.

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Snakemake (smoke_dev) | all | ✓ | 7.32.4 | — |
| r_coloc env (R, susieR, coloc) | fits, coloc | ✓ | 4.4.2 / 0.14.2 / 5.2.3 | — |
| PLINK 1.9 | panel builds | ✗ on PATH | — | `--use-conda` `envs/plink.yml` (1.90b6.21; fresh solve) |
| bcftools / tabix | QTL harmonize | ✗ on PATH | — | conda envs (`plink.yml`, `qtl_processing.yml`) |
| aws CLI / gsutil | UKB tiles | ✗ | — | boto3 UNSIGNED in `envs/ld_build.yml` (existing downloader), or plain HTTPS (`curl` works; verified) |
| Hail | Pan-UKBB alternate only | ✗ (not checked in a usable env) | — | Not needed if the Weissbrod `.npz` is used |
| `envs/qtl_processing.yml` | 5 QTL rules | ✗ (deleted `c2dfb08`) | — | restore from `c2dfb08^` |
| /rs1 space | all outputs | ✓ | 28 TB free of 31 TB | — |
| Network to Zenodo / EBI / S3 | downloads | ✓ | verified HEAD/list | Mirrors in memory `feedback_url_rot_workarounds` |
| Codex CLI | brief-blind adversarial review (D-08) | ✓ per memory `reference_codex_cli_for_gsd_review` | — | — |

**Missing with no fallback:** none.
**Missing with fallback:** plink, bcftools, tabix (conda), `qtl_processing.yml` (restore).

## Storage and compute (estimates)

| Item | Size / count | Wall time (rough) | Queue |
|---|---|---|---|
| LDSC plinkfiles | 0.29 GB tgz | minutes | login/serial |
| UKB 337k tiles for 10 regions | ~10–20 tiles × 0.2–1 GB ≈ 10–15 GB [ASSUMED from the one measured tile] | < 1 h | serial |
| GTEx v8 eQTL (49 tissues) + sQTL (49) | ≈ 186 GB + ≈ 49 GB | a few hours with `xargs -P 5` (memory `feedback_parallel_downloads`) | serial |
| EUR panels: legacy-repro + R4 (10 regions each); AFR R4 (≤11); identity payloads | small (≤ 15k² doubles = 1.8 GB per region worst case, PYHIN1) | minutes each | standard, `mem_mb` 16000 for n > 8k |
| Fine-map jobs | Reproduction: 96 (Route C) + 96 (Route L) + 95 (k2d identity) + 9 (SH2B3 R2 config). Production: EUR 50 × {A2, A3, A3-UKB} = 150 (+50 A3 intersection-matched); AFR ≤ 33 × {A2, A3} = 66 | seconds to ~30 min each | standard |
| Trait-pair coloc | EUR 100 rows × {A1, A2, A3, A3-UKB} = 400; AFR ≤ 33 × 3; repro ≈ 37 | seconds | serial |
| QTL coloc | ≈ 1,274 attempts per GWAS-arm (× 2 if A2 + A3) | seconds to minutes each | standard |
| Simulation (E8) | e.g. 10 regions × 3 r² bins × 3 truths × 200 reps × 3 arms | hours total | serial array |

## Recommended wave decomposition

| Wave | Content | Autonomy |
|---|---|---|
| **W0** infra and guards | Rescue untracked known-answer survivors to /rs1 with sha256. `data/r4` symlink + test. Conda prefix + CONDARC isolation. Restore `qtl_processing.yml`. `ta_r4.smk` skeleton + overlays + static pair manifest. `validate_r4_fits.py` + receipts. OSF sentinel guard. **RED-first named enforcers.** Re-measure the `tests/m3` baseline (last recorded 1299/1265/34/0). New DEC superseding DEC-2026-08-07 option A for Track A. LOG entries. | autonomous (no fires) |
| **W1** data and panels | Zenodo tgz (md5 a7773ab4…) → /rs1. Regenerate variant catalogs. Legacy-identical EUR panel + R4 EUR panel. AFR plink panel. UKB 337k tiles to an isolated dir with the triangle/diag known-answer test. Identity payloads. Panel manifest TSV (md5, sha256, n_var, n_samples, build, source). QTL downloads in parallel (W1b). | autonomous compute; checkpoint:human-verify on the panel manifest |
| **W2** E-2 TDD | Unit 1: BMI allele restoration. Unit 2: `plink_ld_to_rds.R --emit-ref-alt` (+ `--keep-allele-order` in the R4 rule). Unit 3: `run_qtl_coloc.R --qtl-orient` (default false). RED first, negative controls observed red. Full `tests/m3` green with unchanged counts plus the new tests. | autonomous |
| **W3** known-answer reproduction (D-12) | Route L and Route C; k2d 95 rows; Stage-2 aggregates; SH2B3 overlaps 170/589/622 and 895 dims; L-sweep n_CS; R2 PP.H4 config. Findings report (mismatches = findings). | autonomous compute → **checkpoint:human-verify (Carter)** |
| **W4** OSF R4 amendment | Paste-ready file in the `osf-amendment-r3-2026-05-04.md` format: pre-paste table, checklist, body with arms, estimands, branches, known-answer results, deviations (BMI alleles, D-12 premise, E-2 fix), and the "what is not changing" commit hash. Commit the pair manifest and priors before posting. | draft autonomous → **checkpoint:human-action GATE: Carter posts and commits the sentinel** (first option = "WAIT") |
| **W5** production | A1/A2/A3/A3-UKB EUR; AFR secondary; E8 simulation. Validators on every JSON. | autonomous after the sentinel; sentinel test blocks otherwise |
| **W6** QTL layer | Harmonize, then QTL-coloc on A3 (+ A2) with `--qtl-orient true`; tiers. | autonomous |
| **W7** aggregation and figures | E1–E8 tables; frozen-vs-fixed; manifests with sha256; figures. | autonomous → checkpoint:human-verify |
| **W8** fresh manuscript | ~4–5k words, neutral format. Supplementary reproducibility note holds the provenance. Brief-blind adversarial review (Codex). | autonomous → **checkpoint:human-verify (Carter)** |
| **W9** submission prep | Venue decision (Carter). OSF postings (R4 results / correction). Package. | **checkpoint:human-action (Carter)** |

Push after each wave (D-16). Run `git fsck --connectivity-only` before each push.

## Manuscript (W8) guidance

- **Structure (neutral, ~4,500 words):** Abstract ≤ 250 · Introduction ~700 · Methods ~1,500 · Results ~1,500 · Discussion ~900 · 5 figures + 3 tables main, rest supplementary. Journal-specific limits are [ASSUMED]; confirm at W9.
- **Display items:**
  - Fig 1: design (arms, matched variant set, fallback rule).
  - Fig 2: paired PP.H4 scatter A2 vs A3 and A1 vs A3, plus ΔPP.H4 distributions.
  - Fig 3: fine-map structure per arm (n_CS, size, cross-evaluated purity, no-CS rate).
  - Fig 4: diagnostics (λ̂, kriging) vs |ΔPP.H4|; A3 vs A3-UKB.
  - Fig 5: simulation calibration.
  - Table 1: data.
  - Table 2: agreement/reclassification at 0.8/0.5.
  - Table 3: E-2 frozen vs fixed.
- **Reusable from the draft:** background on coloc assumptions and literature, GWAS source descriptions and DOIs (verify vintages), negative-control rationale, reference list (Wallace 2020/2021, Zou 2022, Benner 2017, Weissbrod 2020).
- **Not reusable:** every number, the "systematically inflates" framing, all `.planning`/commit/DEC references (31 lines per the LOG), "50 regions", n = 661/503 claims (re-measure), and "pivot" wording.

## Validation Architecture

### Test Framework
| Property | Value |
|---|---|
| Framework | pytest 9.0.3 (smoke_dev Python 3.11) driving R via `Rscript` from the r_coloc env; testthat for pure-R units |
| Config file | none (existing `tests/conftest.py`); new `tests/ta_r4/conftest.py` |
| Quick run command | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -x -q` |
| Full suite command | `… -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q` (`tests/m3` alone ≈ 15 min per STATE 2026-09-19) |

### Phase Requirements → Test Map
| Req / Decision | Behaviour | Type | Automated command | File exists? |
|---|---|---|---|---|
| D-13 | A3/A3-UKB/AFR JSONs never carry identity; `ld_matrix == declared`; receipt md5 == manifest | unit + live gate | `pytest tests/ta_r4/test_no_silent_identity.py` (NC: injected `identity_fallback` JSON → RED) | ❌ W0 |
| D-01 matched | A2 and A3 have identical `subset_idx`/SNP sets per (region, trait) | live gate | `pytest tests/ta_r4/test_arm_variant_sets_identical.py` | ❌ W0 |
| D-02 | no `coloc.susie` row with n_cs 0; fallback rows labelled `fallback_abf` | unit | `pytest tests/ta_r4/test_fallback_labelled.py` | ❌ W0 |
| Priors | p1/p2/p12 identical across every arm's outputs and equal to `coloc_priors.yaml` | live gate | `pytest tests/ta_r4/test_priors_constant.py` | ❌ W0 |
| D-04 / D-15 | R4 dry-run DAG contains no `EUR_ukbb_pub`, `EUR_ukbb_ld`, `EUR_aou`, `AFR_aou`, `sumstats_harmonized_occl` paths; base config unchanged | dry-run | `pytest tests/ta_r4/test_track_b_isolation.py` | ❌ W0 |
| D-05 | production targets fail `snakemake -n` without the sentinel; succeed with a fixture sentinel | dry-run | `pytest tests/ta_r4/test_osf_gate.py` | ❌ W0 |
| D-11 | all R4 output realpaths under /rs1; manifests committed | unit | `pytest tests/ta_r4/test_storage_on_rs1.py` | ❌ W0 |
| D-06 u1 | restored BMI: BETA/SE/P/POS/SNP_ID byte-equal; REF/ALT populated; unmatched count reported | unit | `pytest tests/ta_r4/test_bmi_allele_restoration.py` | ❌ W2 |
| D-06 u2 | `plink_ld_to_rds.R --emit-ref-alt` yields REF = A2, ALT = A1; without the flag `identical()` to the pre-change output | unit (R) | `pytest tests/ta_r4/test_plink_ld_to_rds_ref_alt.py` | ❌ W2 |
| D-06 u3 | QTL beta negated for transposed, dropped for palindromic/mismatch, counters in JSON; flag off → byte-identical | unit (R) | `pytest tests/ta_r4/test_qtl_orient.py` | ❌ W2 |
| D-12a | panel n_var, md5 and dims match the manifest; SH2B3 = 895; overlaps 170/589/622 | live gate | `pytest tests/ta_r4/test_known_answer_panels.py` | ❌ W1/W3 |
| D-12b | Route C ≡ Route L; k2d per-fit n_CS table diff reported (not asserted equal; a mismatch writes a findings row) | live gate | `pytest tests/ta_r4/test_known_answer_repro.py` | ❌ W3 |
| UKB loader | diag == 1 and sign sanity vs 1000G on a real tile | live gate | `pytest tests/ta_r4/test_ukb_tile_triangle.py` | ❌ W1 |
| Track B | `tests/m3` counts unchanged except added tests; `test_source_freeze_pins` green | suite | full `tests/m3` | ✅ |

### Sampling Rate
- **Per task commit:** quick run (`tests/ta_r4`) plus the specific `tests/m3` files the task touches (e.g. `test_qtl_coloc_allele_join.py`, `test_ld_allele_aware_wiring.py`, `test_source_freeze_pins.py`).
- **Per wave merge:** full suite, with ids/passed/skipped/failed counts recorded against the W0 baseline.
- **Phase gate:** full suite green, all live gates green, and every negative control observed RED once (memory `feedback_green_assertion_needs_a_negative_control`).

### Wave 0 Gaps
- [ ] `tests/ta_r4/conftest.py`: overlay-merge helper (`snakemake.utils.update_config`), fixture panels and sumstats.
- [ ] All `❌ W0` files above, each committed RED first with its negative control.
- [ ] Re-measured `tests/m3` baseline recorded in the LOG.

## Security Domain

`security_enforcement` is null in config; treated as enabled. The scope is narrow (public data, no services):

| ASVS category | Applies | Standard control |
|---|---|---|
| V2/V3/V4 Auth/Session/Access | no | — (no service). /rs1 R4 dirs at group-private perms (2770), not world-readable |
| V5 Input validation | yes | Downloads verified by md5/sha256 (Zenodo md5; S3 size/ETag recorded; eQTL Content-Length). `file` magic-byte check (memory: 200-with-HTML trap). Strict typed parsing already in loaders. |
| V6 Cryptography | no | sha256 for integrity only (`sha256sum`) |
| V14 Config/supply chain | yes | Pinned envs and exported lockfiles. Downloads stored in their own empty directories and read as data (never executed). |

| Threat pattern | STRIDE | Mitigation |
|---|---|---|
| Silent substitution of an LD panel | Tampering | pinned chain + receipts with md5 + read-only panel files after the manifest |
| Corrupted or partial download | Tampering | checksum gate before extraction |
| Result fabrication by fallback | Repudiation | D-13 validators, labelled fallbacks, committed manifests |

## Sources

### Primary (HIGH)
- Repository code (file:line cited inline): `run_susie_rss.R`, `finemap.smk`, `ld_reference.smk`, `plink_ld_to_rds.R`, `run_qtl_coloc.R`, `ld_allele_join.R`, `ld_read_path.py`, `ld_panel.py`, `config/pipeline.yaml`, `create_coloc_manifest.py`, `tests/m3/test_source_freeze_pins.py`.
- coloc 5.2.3 / susieR 0.14.2 formals, inspected in the r_coloc env.
- Snakemake 7.32.4 `update_config` source and a behaviour test.
- Zenodo API, record 10515792 (file sizes, md5, licence).
- Anonymous S3 listings: `broad-alkesgroup-ukbb-ld`, `pan-ukb-us-east-1`; EBI HEAD checks.
- [Wallace 2021, PMC8504726](https://pmc.ncbi.nlm.nih.gov/articles/PMC8504726/): hybrid fallback recommendation.
- [Zou et al. 2022, PMC9337707](https://pmc.ncbi.nlm.nih.gov/articles/PMC9337707): regularization, λ diagnostic, allele flips, panel size.
- [PLINK 1.9 data docs](https://www.cog-genomics.org/plink/1.9/data): `--keep-allele-order`.

### Secondary (MEDIUM)
- [PolyFun finemapper.py](https://raw.githubusercontent.com/omerwe/polyfun/master/finemapper.py): npz triangle and allele convention.
- [Pan-UKBB Hail-format docs](https://pan.ukbb.broadinstitute.org/docs/hail-format/).
- [AWS Open Data: UKBB LD](https://registry.opendata.aws/ukbb-ld/).
- [coloc SuSiE vignette](https://chr1swallace.github.io/coloc/articles/a06_SuSiE.html).
- [Wallace 2021 PubMed](https://pubmed.ncbi.nlm.nih.gov/34587156/); [Zou 2022 DOI](https://www.doi.org/10.1371/journal.pgen.1010299).

### Tertiary (LOW)
- [Zenodo 10515792 search result](https://zenodo.org/record/10515792) and [PRED-LD table](https://biomedcentral-bmcbioinformatics.publicaciones.saludcastillayleon.es/articles/10.1186/s12859-025-06119-y/tables/2): inconclusive on 489 vs 503.

## Metadata

**Confidence breakdown:**
- Standard stack and data availability: HIGH. Versions, URLs, sizes and checksums were measured this session.
- Architecture (overlay-only arming, receipts, matched identity): MEDIUM-HIGH. Built on verified gate semantics; needs W0 tests to confirm end to end.
- Pitfalls: HIGH for the code-derived ones (1–9, 11–14); MEDIUM for UKB npz conventions (10); LOW for ABO and sample-n details.

**Research date:** 2026-10-21
**Valid until:** 2026-11-20. Code facts stay valid until the next commit touching the cited files. URL facts are subject to rot (see memory `feedback_url_rot_workarounds`).
