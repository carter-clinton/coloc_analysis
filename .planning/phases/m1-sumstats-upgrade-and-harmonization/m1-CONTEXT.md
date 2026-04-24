# Phase M1: Sumstats upgrade and harmonization — Context

**Gathered:** 2026-04-24
**Status:** Ready for planning
**Slug:** m1-sumstats-upgrade-and-harmonization
**Discuss round:** R4 (parsed-plotting-lynx routing plan, 2026-04-24)

<domain>
## Phase Boundary

Land the 9-trait × up-to-2-ancestry public GWAS sumstats inventory enumerated in
`.planning/amendments/SUMSTATS-UPGRADE.tsv` (45 rows; 27 scripted-downloads
already landed, 7 portal-gated + 1 DUA-gated pending); harmonize each source
to the locked genome build with per-ancestry QC; emit two parallel artifact
classes per trait × ancestry (full-coverage harmonized for coloc / fine-mapping
/ CPASSOC input + HM3-munged `.sumstats.gz` for LDSC / MTAG input); build
the 45×45 LDSC bivariate-intercept matrix required by MTAG `--overlap`; freeze
the SHA-256 manifest for the OSF amendment paste-ready text.

In scope: all sumstats acquisition, harmonization, QC, LDSC munging, bivariate-
intercept matrix estimation, trait-inventory YAML freeze, SHA-256 manifest
freeze, Snakemake rule + conda env authoring, Quarto QC reports.

Out of scope (belongs to M2+): running MTAG `--overlap`; running CPASSOC
SHom/SHet; PLINK clumping; union-region-list construction; joint-signal
novelty extraction; any downstream discovery artifact.

Gating: M1 verified success criteria AND OSF amendment posted at osf.io/pvb5j
(Carter web-UI action, Amendment §9.1) are both required before M2 fires.

</domain>

<decisions>
## Implementation Decisions

### A. Source locks

- **D-01 BMI EUR primary source (SUMSTATS-UPGRADE Q1):** Yengo 2018 GIANT+UKB
  (N=681k EUR, GCST006900, GRCh37, scripted-ready) is the primary. Loh 2022
  Nat Commun (DOI 10.1038/s41467-022-35553-2, ~1.1M EUR + ~100k AFR multi-
  ancestry, GRCh38, pending GCST accession confirmation) is carried in parallel.
  Promote Loh 2022 to primary once (a) GWAS Catalog accession resolves and
  (b) AFR-subset provenance is documented. Both rows stay in
  `SUMSTATS-UPGRADE.tsv`; harmonizer emits both; MTAG intercept matrix includes
  both until one is retired.

- **D-02 GIGASTROKE per-ancestry GCST resolution (SUMSTATS-UPGRADE Q2):**
  Carter performs a ~15-minute manual browse of
  `ebi.ac.uk/gwas/publications/36180795` to pin each (ancestry, subtype)
  tuple to an integer GCST accession. Resolved values commit to
  `SUMSTATS-UPGRADE.tsv` (replacing `GCST90104540-series` placeholders) with
  a `docs(amendments): GIGASTROKE GCST lock` commit. Snakemake download rule
  consumes the resolved accessions. Unblocks 5 stroke rows (TRANS, EUR, AFR,
  EAS, SAS) cleanly.

- **D-03 Aragam 2022 AFR-CAD release policy (SUMSTATS-UPGRADE Q3):** Unzip
  `Aragam_2022_CARDIoGRAM_CAD_GWAS.zip` at
  `data/raw/sumstats_v2/Aragam2022/` and enumerate contents. Two branches:
  (a) AFR subset file present → harmonize as row 23 of TSV, no further action;
  (b) AFR subset file absent → fall back to Klarin 2018 MVP-AFR-CAD
  (`10.1038/s41591-018-0090-y`, N≈8.5k AFR) with a one-line methods-
  disclosure in the Track B paper's cohort table. CAD-AFR slot stays in
  Amendment §4 locked inventory either way.

- **D-04 GLGC HDL/TG/TC ancestry fanout (SUMSTATS-UPGRADE Q4):** Keep the
  TSV as-is. LDL at 5 ancestries (TRANS, EUR, AFR, EAS, SAS, HIS = 6 rows).
  HDL / TG / TC at TRANS + EUR + AFR only (9 rows). No expansion. Sufficient
  for cross-ancestry sensitivity on lipids without ballooning MTAG intercept
  matrix or storage. Scripted downloads already landed this set.

- **D-05 PAGE BMI-AFR access (SUMSTATS-UPGRADE Q6):** Treat as public sumstat-
  only per Wojcik 2019 data-availability statement (GCST publication 31217584).
  Verify at download-time by attempting direct GWAS Catalog sumstat fetch.
  If any portal barrier surfaces, flip `dua_required` flag to `yes` and
  submit dbGaP phs000920 DUA in parallel. M1 proceeds without blocking
  on this row's DUA in the expected-case path.

### B. MVP Giri AFR-BP critical path

- **D-06 MVP Giri AFR-BP tiered strategy:** Primary attempt is a public
  GWAS Catalog summary-only check at
  `ebi.ac.uk/gwas/publications/30578418` to see whether Giri 2019 released
  sumstats independent of dbGaP phs001672 individual-level DUA. Fallback
  (if primary fails) is AoU Researcher Workbench AFR-SBP derivation on
  Carter's controlled-tier access (~60-95k AFR WGS post-QC), exporting
  summary-level effects only per AoU egress policy. dbGaP phs001672 DUA
  submission is NOT on the primary or fallback path. `drop AFR-BP from
  M1` is explicitly off-table — Amendment §4 locked inventory holds.

- **D-07 Scope expansion — AoU compute in M1:** Confirming the D-06
  fallback adds an AoU Researcher Workbench compute path to M1 that
  DEC-2026-04-22-04 had previously scoped to M3 (LD panel build) only.
  File a new `DEC-2026-04-24` entry capturing this scope expansion before
  planner lays out M1 tasks. Egress-audit scaffolding from
  `AOU-LD-PIPELINE.md` §2 P1–P7 is reusable for the AFR-SBP derivation
  with minimal adaptation.

### C. Genome build target

- **D-08 GRCh37 canonical; liftover two b38 sources; amend Amendment §3 M1
  text (SUMSTATS-UPGRADE Q7):** Keep GRCh37 as the canonical analytic plane
  across all of M1 output. Two b38-native sources (Loh 2022 BMI +
  GBMI asthma) undergo b38→b37 liftover at harmonize step using CrossMap
  plus HRC rsid remap per SUMSTATS-UPGRADE §6. Everything else stays b37
  native. File a new `DEC-2026-04-24` entry overriding Amendment §3 M1
  text that reads "Harmonize to GRCh38". Also update
  `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` if that text
  asserts b38 (pre-paste check — may already say 'harmonize to common
  build' or similar).

### D. Pipeline architecture and deliverable specs

- **D-09 Canonical harmonized deliverable format:** Dual-emit per trait ×
  ancestry. Primary: `.tsv.bgz` + `.tbi` at
  `data/processed/sumstats_harmonized/<trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz`
  (tabix-indexed region-query path for coloc / fine-mapping / CPASSOC).
  Mirror: `.parquet` at
  `data/processed/sumstats_harmonized_parquet/<trait>.<ancestry>.<consortium>.<year>.GRCh37.parquet`
  (columnar fast-read for LDSC / MTAG bulk scans, satisfies
  Amendment Success Criterion 1 literal wording).

- **D-10 Harmonizer implementation strategy:** Per-source Python modules
  following the Phase 09 pattern. Reuse `src/python/sumstats_utils.py`
  + the canonical 10-column schema (CHR, POS, SNP, REF, ALT, BETA, SE, P,
  EAF, N). Seven new modules to author:
  - `src/python/harmonize_yengo.py` (GIANT BMI Yengo 2018 + Loh 2022 variant)
  - `src/python/harmonize_diamante.py` (T2D TRANS + EUR + EAS + SAS; AFR / HIS pending)
  - `src/python/harmonize_gigastroke.py` (GWAS-Catalog harmonized format; 5 ancestries)
  - `src/python/harmonize_aragam.py` (CARDIoGRAM zip; TRANS + EUR + EAS; AFR conditional on D-03)
  - `src/python/harmonize_glgc.py` (RVTESTS meta tabix-pre-indexed; handles logTG)
  - `src/python/harmonize_wuttke.py` (CKDGen eGFR TRANS + EUR; Morris 2019 AFR variant)
  - `src/python/harmonize_magic.py` (HbA1c 6 ancestries; rsid-only SNPID → chr:pos crosswalk)
  Existing `harmonize_gbmi.py` is reused without change (GBMI asthma slot).
  Evangelou 2018 SBP-EUR already harmonized (T1 spine); re-verify build
  + canonical-schema conformance, do not re-run harmonize.

- **D-11 LDSC bivariate-intercept matrix scope:** Full 45×45 wide TSV at
  `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv`.
  Rows indexed by the 45 munged sumstats files with
  `<trait>.<ancestry>.<consortium>.<year>` keys. M2 MTAG wrapper slices
  the matching sub-matrix per run — not M1's job to pre-slice.
  Computation: single `ldsc.py --rg-cross` invocation over the trait list
  (990 pairs). LD panel selection per pair: EUR-EUR = 1KG Phase 3 b37 EUR
  baseline-LD; AFR-AFR = 1KG Phase 3 b37 AFR; cross-ancestry pairs use
  the LDSC shared-AFR+EUR release (Galinsky-Gazal et al) or PopCorn fallback.

- **D-12 Per-trait QC report format:** Quarto (`.qmd` → HTML) per trait,
  rendered under Snakemake with `quarto render` invocation. Mixes R
  (tidyverse + ggplot2 for MAF histogram, LDSC intercept plot, Manhattan,
  QQ, locuszoom of 7 control loci) with Python (pandas for variant counts,
  PASS / FAIL summary table, file-integrity checksum display). One HTML
  per trait at
  `data/processed/sumstats_harmonized/qc_log/<trait>.qc.html` plus a
  cross-trait index at `data/processed/sumstats_harmonized/qc_log/index.html`.
  QC checklist items 1–9 from SUMSTATS-UPGRADE §7 all surface in each
  report.

- **D-13 SHA-256 manifest semantics:** Two manifests. Primary:
  `data/raw/sumstats_v2/sha256_manifest.tsv` covering every raw download
  under `data/raw/sumstats_v2/**/*` (pre-harmonization source files). This
  is the frozen provenance artifact that pastes into
  `OSF-AMENDMENT-TEXT-2026-04-22.md` hash slot at M1 closeout.
  Secondary: `data/processed/sumstats_harmonized/sha256_manifest.tsv`
  covering harmonized outputs, committed to git for pipeline reproducibility
  tracking (drifts with harmonizer code versions).

- **D-14 Parallelization policy:** Harmonize-as-ready. Snakemake rule
  pattern: per-source-file → per-harmonized-file → per-munged-file. As
  Carter resolves portal fetches (Yengo, PAGE, DIAMANTE, GIGASTROKE, GBMI,
  MAGIC, Aragam-zip-unpacked), the DAG re-triggers. The 45×45 LDSC matrix
  rule gates on all 45 munged files. Gets analytic value from the 27
  already-landed GLGC+CKDGen+Aragam files immediately rather than waiting
  on MVP-Giri AoU derivation weeks from now.

- **D-15 HapMap3 vs full-coverage duality:** Emit both artifact classes
  per trait × ancestry — full-coverage harmonized (`.tsv.bgz` + `.parquet`)
  feeds coloc / fine-mapping / CPASSOC; HM3-munged (`.sumstats.gz`) feeds
  LDSC / MTAG. Both are M1 deliverables; neither is optional.

### F. M1 → M2 handoff contract

- **D-16 Per-trait munged file naming:** Lowercase-trait-token-first
  dotted convention: `<trait>.<ancestry>.<consortium>.<year>.sumstats.gz`.
  Trait tokens: `bmi, t2d, sbp, stroke, asthma, cad, ldl, hdl, tg, tc,
  egfr, hba1c`. These same tokens are the primary keys of
  `config/trait_inventory.yaml` so downstream M2 MTAG wrapper + CPASSOC
  wrapper can read the YAML and construct paths deterministically. Dotted
  separator avoids underscore-within-token ambiguity (e.g.
  consortium = `CARDIoGRAM-C4D-MVP`).

- **D-17 MTAG per-run trait grouping:** Deferred to M2 discuss-phase.
  M1 emits per-trait munged files + the full 45×45 intercept matrix; M2
  picks topology (cluster-based vs all-9-per-ancestry vs pairwise) with
  Turley 2018 ≤6-trait guidance in hand at that time. M1 stays tight.

### Claude's Discretion

- Exact schema of `config/trait_inventory.yaml` — derived from D-16 trait
  tokens and the 45-row TSV; fields must include at minimum
  `{trait, ancestry, consortium, year, source_url, build, harmonized_path,
  munged_path, parquet_path, n_total, n_cases, n_controls, sha256_raw,
  sha256_harmonized, ldsc_intercept, ldsc_h2, qc_report_path, qc_status}`.
- Snakemake rule layout across files (suggest: `workflow/rules/m1_download.smk`,
  `m1_harmonize.smk`, `m1_munge.smk`, `m1_ldsc_rg.smk`, `m1_qc.smk`).
- Conda environment partitioning (likely: `envs/m1-harmonize.yml` for
  Python harmonizers, `envs/m1-ldsc.yml` for LDSC + munge, `envs/m1-qc.yml`
  for Quarto + R plotting stack).
- LSF queue selection per rule (follow `feedback_lsf_queues` memory:
  standard / serial / long with `bsub_wrapper.sh` queue max wall-times).
- CPASSOC variant-set alignment algorithm (intersect-all-traits vs
  reference-MAF-threshold union) — this is arguably M2's job but the M1
  harmonizer should emit the variant-universe helper needed by either.
- Parquet region-slice helper signature for coloc readers (likely a thin
  `pyarrow.dataset` wrapper exposing a tabix-shaped `query(chrom, start, end)`
  API).
- Retry / re-download policy if portal-fetched files fail checksum
  validation on later re-run.

### Folded Todos

None — no todos matched M1 scope at this time.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Pivot + milestone spec
- `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3 M1 — milestone content + duration + gating; §4 — locked trait inventory (18-row Track B plane); §5 — AFR LD panel strategy (AoU scope); §9 — OSF amendment timing + paste protocol
- `.planning/ROADMAP.md` §M1 — slug, goal, requirements, success criteria (5 items), deliverable artifacts (5 classes), gating condition for M2

### Requirements + decisions
- `.planning/REQUIREMENTS.md` — REQ-TRAIT-INVENTORY, REQ-SNAKEMAKE-CI, REQ-PUBLIC-DATA-ONLY, REQ-PATH-PARAMETERIZATION (M1 requirement bindings)
- `.planning/DECISIONS.md` — DEC-2026-04-22-01 (candidate-locus abandonment; context for pivot); DEC-2026-04-22-02 (9-trait × up-to-2-ancestry inventory lock); DEC-2026-04-22-03 (MTAG+CPASSOC stack → intercept-matrix dependency); DEC-2026-04-22-04 (AoU egress-aware LD → reuse scaffolding for D-06/D-07); DEC-2026-04-23-01 (two-track publication strategy)

### Sumstats inventory + download state
- `.planning/amendments/SUMSTATS-UPGRADE.md` — full rationale; §2 summary table; §3 per-trait rationale (all 9 traits); §4 MTAG overlap strategy; §5 download tier ordering; §6 harmonization pipeline alignment; §7 9-item QC checklist; §8 storage plan; §9 DUA critical path; §10 all 7 open questions (this CONTEXT resolves Q1, Q2, Q3, Q4, Q6, Q7; Q5 MAGIC FTP test defers to planner pre-flight)
- `.planning/amendments/SUMSTATS-UPGRADE.tsv` — 48-line TSV (47 data rows + header); source of truth for per-row metadata. GIGASTROKE GCST placeholders updated per D-02 before planner fires
- `.planning/amendments/SUMSTATS-SCRIPTED-FETCH-COMPLETE.md` — 27 files landed (GLGC 24 + CKDGen 2 + Aragam 1 zip), 40.4 GB, driver `bin/download_sumstats_v2.sh`
- `.planning/amendments/SUMSTATS-MANUAL-FETCH.md` — 7 portal-source fetch protocols
- `.planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md` — live tracker of portal + DUA queue

### OSF amendment
- `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` — paste-ready body with 3 placeholders (M1 completion date, M1 commit hash, M5 lock hash). M1 SHA-256 manifest per D-13 feeds this doc's raw-source hash slot

### AoU scaffolding (for D-06 fallback + D-07 scope expansion)
- `.planning/amendments/AOU-LD-PIPELINE.md` — egress-audit framework, P1–P7 prerequisites, 4-check validation protocol (reusable for AFR-SBP derivation)

### Phase 09 handoff pattern (reusable for M1 harmonizer architecture per D-10)
- `.planning/phases/09-replication-in-independent-cohorts/09-CONTEXT.md` — cohort portfolio pattern, deferred-items discipline
- `.planning/phases/09-replication-in-independent-cohorts/09-02-PLAN.md` — 10-column canonical schema + GRCh38→GRCh37 liftover + palindromic-SNP exclusion + harmonizer wave structure
- `src/python/sumstats_utils.py` — shared harmonization helpers
- `src/python/harmonize_gbmi.py`, `harmonize_finngen.py`, `harmonize_bbj.py`, `harmonize_mvp.py` — per-source harmonizer reference implementations
- `src/python/munge_sumstats_ldsc.py` — existing munge wrapper that reads 10-column canonical TSV → LDSC input
- `tools/ldsc/munge_sumstats.py` — vendored LDSC munge script
- `bin/download_sumstats_v2.sh` — idempotent scripted-fetch driver (27 files complete; extend for portal sources per D-14)

### Project-level constraints
- `CLAUDE.md` — 100% public data; solo author; timeline not binding; rigor > speed; no worktree isolation (GPFS `solo` mode with `git.isolation: branch`)
- `/home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/feedback_lsf_queues.md` — LSF queue selection + wall-time rules
- `/home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/project_python_311_pin.md` — Snakemake 7.32.4 requires Python 3.11; use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` or --use-conda

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`src/python/sumstats_utils.py`** — canonical 10-column schema definitions, column-name normalization helpers, palindromic-SNP filter, MAF-band sanity checks. All 7 new harmonizers (D-10) consume this module directly.
- **`src/python/harmonize_{gbmi,finngen,bbj,mvp}.py`** — per-source harmonizer reference implementations. `harmonize_gbmi.py` is reused as-is for the GBMI asthma slot in M1. The other three are pattern templates for the 7 new harmonizers.
- **`src/python/munge_sumstats.py`** (note: actual filename is `munge_sumstats_ldsc.py`) — wraps `tools/ldsc/munge_sumstats.py` to read canonical 10-column harmonized TSV and emit `.sumstats.gz` with LDSC HM3 SNP restriction + N-column handling. Reused without modification for M1.
- **`tools/ldsc/munge_sumstats.py`** + vendored LDSC toolkit at `tools/ldsc/` — used for munging and for the `ldsc.py --rg-cross` invocation of D-11.
- **`bin/download_sumstats_v2.sh`** — idempotent `xargs -n 1` downloader that already landed 27 scripted files. Extend manifest for portal-gated sources per D-14.
- **`.gitignore`** rules already exclude `data/` — SUMSTATS-UPGRADE §8 mandates an explicit exclusion for `data/raw/sumstats_v2/mvp_giri_bp_afr_2019/` if D-06 DUA branch ever triggers (guard against accidental dbGaP-covered data commits).

### Established Patterns

- **Harmonize-then-unify**: per-source Python harmonizer → canonical 10-column TSV → Snakemake manifest dispatch. Reused verbatim in M1.
- **10-column canonical schema**: `CHR, POS, SNP, REF, ALT, BETA, SE, P, EAF, N` — every harmonized file conforms.
- **Path-parameterized Snakemake rules** (REQ-PATH-PARAMETERIZATION): wildcard patterns like `{trait}.{ancestry}.{consortium}.{year}` drive every downstream rule. D-16 filename convention feeds directly into this.
- **Conda-env-per-rule-family**: each wave of rules gets its own `envs/<name>.yml`. Proposed M1 partition: `m1-download`, `m1-harmonize`, `m1-munge`, `m1-ldsc-rg`, `m1-qc`.
- **QC waypoint discipline** (Phase 09 §09-VALIDATION.md pattern): every deliverable has a checksum + dimension check + format check before downstream consumption.

### Integration Points

- **Writes to**: `data/raw/sumstats_v2/<Consortium><Year>/<trait>/<ancestry>/` (raw download target per existing `SUMSTATS-MANUAL-FETCH.md` convention); `data/processed/sumstats_harmonized/<trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz` (+ `.tbi`); `data/processed/sumstats_harmonized_parquet/<trait>.<ancestry>.<consortium>.<year>.GRCh37.parquet`; `data/processed/sumstats_harmonized_munged/<trait>.<ancestry>.<consortium>.<year>.sumstats.gz`; `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv`; `data/processed/sumstats_harmonized/qc_log/<trait>.qc.html` (+ `index.html`); `data/raw/sumstats_v2/sha256_manifest.tsv`; `config/trait_inventory.yaml`.
- **Reads from**: `.planning/amendments/SUMSTATS-UPGRADE.tsv` (source-of-truth); existing `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz` (Evangelou T1 spine reuse — verify build before reuse).
- **Downstream hook**: `config/trait_inventory.yaml` is the schema contract with M2. M2 MTAG wrapper reads the YAML, resolves munged-path per trait, slices intercept matrix accordingly. CPASSOC wrapper reads YAML, resolves harmonized-path per trait, aligns variant sets.
- **OSF hook**: `data/raw/sumstats_v2/sha256_manifest.tsv` + M1 completion commit hash paste into `OSF-AMENDMENT-TEXT-2026-04-22.md` placeholders 1 + 2 before Carter performs the osf.io/pvb5j amendment submission (M2 hard gate per Amendment §9.1).

</code_context>

<specifics>
## Specific Ideas

- MTAG `--overlap` is the downstream reason the 45×45 intercept matrix is mandatory, not a nice-to-have. "Without it, MTAG's default assumption of independent samples systematically over-weights correlated traits … inflating discovery counts and producing false-positive MTAG-specific loci" (SUMSTATS-UPGRADE §4). Plan must treat the intercept matrix as a first-class deliverable, not a by-product of LDSC munging.
- Highest-overlap EUR pair cluster is the UKB-containing rows (36 pairs with expected bivariate intercept > 0.5). Within-GLGC lipids are same-sample different-traits (expected intercept ~1.0 for 6 within-lipid pairs). Planner should pre-allocate these as sanity-check validation in the QC step.
- Phenotype-definition locks (SUMSTATS-UPGRADE §1 closer: "must not be silently relaxed downstream") → trait-inventory YAML must carry `phenotype_lock` free-text field per row so downstream papers can disclose the exact lock used.
- The 5 post-MTAG validation checklist items (SUMSTATS-UPGRADE §4) are M2's problem, not M1's — but M1 QC report per D-12 must ship the LDSC intercept + mean chi² + genomic control lambda per single-trait so M2's validation has the baseline.
- Amendment §3 M1 says "GRCh38" and `OSF-AMENDMENT-TEXT-2026-04-22.md` may propagate that wording — pre-paste DEC + amendment text consistency check is a planner task.
- MVP Giri D-06 primary attempt is a publication-page-check, not a DUA submission. If it succeeds, AFR-BP lands cleanly. If it fails, AoU derivation fires under D-07 scope expansion — protocol reuses AOU-LD-PIPELINE.md §2 P1–P7 egress scaffolding.

</specifics>

<deferred>
## Deferred Ideas

- **MTAG per-run trait grouping** (D-17): topology decision (cluster-based, all-9-per-ancestry, pairwise, or hybrid) defers to M2 discuss-phase. M1 emits the building blocks; M2 picks assembly. Turley 2018 ≤6-trait guidance plus the 45×45 matrix both feed into that decision.
- **DIAMANTE AFR + HIS strata**: not released as of 2026-04-22 (DIAGRAM gate on manuscript acceptance). Carry placeholders in TSV; quarterly recheck; plug in when released. Does not block M1 closeout.
- **Aragam author email for AFR file**: fallback of last resort — only fires if D-03 ZIP inspection shows AFR absent AND Klarin 2018 MVP-AFR-CAD is judged too small. Pre-registered as a deferred contingent branch.
- **dbGaP phs001672 DUA submission**: explicitly de-prioritized per D-06. If both primary (GWAS Catalog check) + fallback (AoU derivation) fail, dbGaP becomes a re-open option but that is a scope re-discuss, not a default path.
- **Q5 MAGIC FTP port-21 egress test from NCSU HPC**: a planner pre-flight check, not a gray area. If blocked, fallback is EBI mirror or login-node proxy per SUMSTATS-UPGRADE §5 Tier 1.

### Reviewed Todos (not folded)

None — no pending todos surfaced as relevant to M1 scope.

</deferred>

---

*Phase: m1-sumstats-upgrade-and-harmonization*
*Context gathered: 2026-04-24 (R4 routing, parsed-plotting-lynx plan)*
