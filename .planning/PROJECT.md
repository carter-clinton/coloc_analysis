# PROJECT.md — coloc_analysis

> **Authoritative pivot charter:**
> [`.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`](amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md)
> (this is the post-pivot source of truth).
> **Companion documents:**
> [`ID-VS-REF-LD-STRATEGY.md`](amendments/ID-VS-REF-LD-STRATEGY.md),
> [`SUMSTATS-UPGRADE.tsv`](amendments/SUMSTATS-UPGRADE.tsv) /
> [`SUMSTATS-UPGRADE.md`](amendments/SUMSTATS-UPGRADE.md),
> [`AOU-LD-PIPELINE.md`](amendments/AOU-LD-PIPELINE.md),
> [`TRACK-A-FROZEN-NUMBERS.md`](amendments/TRACK-A-FROZEN-NUMBERS.md).
> **Project-instruction anchor:** [`CLAUDE.md`](../CLAUDE.md).
> Read the Amendment and this file together before touching anything else.

## Who

**Author / sole owner:** Carter K. Clinton, ASHES Lab, North Carolina State
University. **Solo author.** No internal co-author review. Rigor comes from
multi-method triangulation, pre-registration (OSF), and hold-out replication.

## What

Two-track original research program (adopted 2026-04-22 per Amendment §3):

- **Track A — Real-LD audit of 50 curated cardiometabolic regions.**
  Forward-looking short-form methods paper that quantifies how published
  candidate-locus pleiotropy claims survive fully-pre-registered real-LD
  re-analysis under current-best-practice SuSiE-RSS + coloc.susie with
  matched-ancestry real LD. Target venue ladder: Genome Medicine (primary)
  → AJHG short report (fallback 1) → Bioinformatics Applications Note
  (fallback 2). Track A is scientifically independent of Track B and ships
  on the pre-pivot spine outputs, which are reusable per Amendment §8 as
  pre-specified methods validation data.

- **Track B — Genome-wide joint-signal discovery across 9 complex traits.**
  Hypothesis-driven original research across BMI, T2D, stroke, SBP,
  asthma, CAD, lipids (LDL primary; HDL/TG/TC secondary), eGFR, and HbA1c
  in EUR and AFR ancestries, executed under milestones M0–M6 per
  Amendment §3. Two co-equal pre-registered scientific aims:
  (i) cross-trait pleiotropy discovery and
  (ii) novel-variant discovery across five operationally-defined classes
  (joint-signal, AFR-specific, secondary-independent, pleiotropy-class,
  functional-mechanism) per Amendment §7. Target venue: Nature Genetics.

## Where

| Path | Role |
|---|---|
| `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` | **Canonical repo** (this directory). Git root. GSD state lives under `.planning/`. |
| `https://github.com/carter-clinton/coloc_analysis` | **GitHub remote** (`origin`). Canonical public mirror; bundle for AoU Workbench `git clone` lives here. |
| `/rs1/researchers/c/ckclinto/coloc_analysis/` | Upstream data root. Symlinked from `data/` and `results/legacy/`. 77 GB historical backup tarball lives here. |
| `/rs1/researchers/c/ckclinto/miniconda3/` | Miniconda3 install. `gsd-tools` conda env has the GSD plugin. |
| NCSU HPC (LSF scheduler) | Compute. `bsub` for job submission. |
| All of Us Researcher Workbench (Terra / Google Cloud) | Track B M3 AFR LD panel build site. Controlled-tier WGS; summary-only export per AoU data-egress policy. |
| GPFS `/gpfs_common/` | Shared filesystem. **Worktree isolation is known-bad here — use `mode: solo` with `git.isolation: branch` in GSD.** |

## Why (in one paragraph)

The coloc_analysis program is hypothesis-driven original research at two
scales. At the candidate-locus scale, Track A quantifies — as a pre-specified
methods-validation contribution per Amendment §8 — how many published
cross-trait pleiotropy claims at 50 curated cardiometabolic regions survive
fully-pre-registered real-LD re-analysis. Stage 2 real-LD evidence on
2026-04-22, refined under the matched-coverage k2d full-coverage 2026-04-25
re-fire (51/96 non-empty credible sets vs 48/95 under k2d identity-LD =
1.06× count-level yield contrast; 0 Tier A; SH2B3 × asthma EUR identity-LD
PP.H4 = 1.0 collapses to real-LD n_cs_a = 0; SUPERSEDED 2026-04-25
narrow-validation 12/96 / 4.25× baseline preserved in
`TRACK-A-FROZEN-NUMBERS.md`) shows that identity-LD inflation operates
primarily at the structural credible-set composition level even at canonical
literature loci, with modest count-level differential under the matched-
coverage comparator. This is itself a publishable finding; Track A reports
it. At the genome-wide scale, Track B
pursues hypothesis-agnostic joint-signal discovery across 9 complex traits in
EUR and AFR ancestries using a multi-method stack: MTAG (Turley 2018) with
`--overlap` LDSC-intercept correction for UKB/MVP cohort overlap, CPASSOC
(Zhu 2015) as an orthogonal SHom/SHet joint-signal test for cross-method
corroboration, two-stage scalable coloc (ABF triage followed by SuSiE-RSS
rescue with PolyFun baselineLF2 priors per Weissbrod 2020), HyPrColoc
(Foley 2021) for ≥3-trait shared-architecture inference, and All of Us
controlled-tier WGS (~60–95k AFR post-QC) as the ancestry-matched LD
reference panel — a ~150× sample-size upgrade over 1000G AFR (n = 661). Five
novel-variant discovery classes are pre-registered per Amendment §7 with
locked comparator catalogs (GWAS Catalog, Pickrell 2016, Watanabe 2019,
Open Targets L2G, ClinVar) and SHA-256 version checksums. The 2026-04-22
pivot is a forward-looking scope expansion informed by the Stage 2 real-LD
evidence — Track A inherits the candidate-locus artifacts as its primary
data, Track B operates at genome-wide scale with ancestry-matched real LD.

## Constraints

- **100% public data.** No wet-lab, no functional validation, no proprietary
  or industry datasets. Standard academic DUAs for UK Biobank, UKB-PPP,
  deCODE, FinnGen, MVP, All of Us, BBJ, Pan-UKBB, etc.
- **Solo author.** Rigor must come from multi-method triangulation,
  pre-registration on OSF, Snakemake-pinned pipeline, hold-out replication —
  not from internal QC.
- **Timeline is not a binding constraint.** Rigor and impact matter more than
  speed. Do not compress phases to save time.
- **No web/JS stack.** Relevant stack is R (`coloc`, `susieR`, `TwoSampleMR`,
  `MRPRESSO`, `hyprcoloc`), Python (LDSC, PRS-CSx, selscan, Enformer / Borzoi
  inference), bash, Snakemake, conda. Skip any skill pack aimed at React /
  Next / Vite / TypeScript.
- **Data access lead times are the real critical path.** UKB-PPP, deCODE,
  FinnGen, MVP, All of Us, BBJ, Pan-UKBB require DUAs that take weeks to
  months. These must run in parallel with Phase 0 from Day 1 (REQ-1).
- **GPFS filesystem.** Do **not** use worktree isolation. GSD mode is
  `solo` with `git.isolation: branch`.

## Goals for this GSD-managed program

1. Execute Track B milestones **M0 → M1 → M2 → M3 → M4 → M5 → M6** to
   Nature Genetics acceptance bar per Amendment §3. Each milestone lands
   via `/gsd-plan-phase` + `/gsd-execute-phase` with atomic commits and a
   SUMMARY.md audit trail.
2. Ship **Track A short-form methods paper** at Genome Medicine (primary),
   independently of Track B progress. Track A preprint (bioRxiv) establishes
   priority on the real-LD-audit framing in 2026-05 / 2026-06 ahead of
   Track B M6 submission in 2027-04 / 2027-05 per Amendment §11.
3. Pre-register all Track B scientific claims on OSF via the amendment flow
   described in Amendment §9: the amendment posts at the end of M1 (after
   harmonized sumstats checksums are frozen) and before any M2 MTAG /
   CPASSOC run. OSF submission is the pre-registration gate for M2
   execution.
4. Deliver a reproducible GitHub release with a pinned Snakemake pipeline,
   conda envs, Singularity containers, Zenodo DOI deposit of the AoU-derived
   AFR LD panels (summary-only per AoU data-egress policy), and hold-out
   replication tables on FinnGen / Pan-UKBB / MVP release n+1 (per REQ-1
   parallel-DUA convention and the Snakemake-CI requirement).
5. Maintain every component of the pre-pivot spine (Phases 0, 1, 2, 5, 9)
   as reusable artifacts per Amendment §8: Phase 0 reference data, Phase 1
   SuSiE-RSS fine-mapping outputs, Phase 2 Stage 2 real-LD coloc, Phase 5
   LDSC partitioned heritability + HESS + MAGMA + LDSC-SEG, Phase 9
   replication scaffolding. These are Track A's primary data and Track B's
   candidate-locus validation subset.

## Current status

**M0 pivot scaffolding — in flight.** Six amendment artifacts committed
under `.planning/amendments/` (Amendment, Track A pivot, frozen numbers,
SUMSTATS upgrade TSV + MD, AoU LD pipeline, sumstats manual-fetch manifest).
Track A first-pass manuscript draft committed 2026-04-23 (Stage 2 values
locked in TRACK-A-FROZEN-NUMBERS.md). PROJECT.md + REQUIREMENTS.md
reconciled to Amendment §12 spec on 2026-04-28 under quick task
`260428-pj4` (zero substantive drift from the 2026-04-23 post-pivot
rewrite — current files already satisfy §12); ROADMAP.md / DECISIONS.md
M0 closeout rewrites are the remaining documentation items, owned by
Terminal A in parallel.

**Pre-pivot spine (Phases 0 / 1 / 2 / 5 / 9) — complete.** Artifacts are
reusable per Amendment §8: Phase 1 SuSiE-RSS across 205 windows; Phase 2
Stage 2 real-LD coloc delivered **51/96 non-empty credible sets (53.1%) vs
48/95 (50.5%) under the matched-coverage k2d full-coverage identity-LD
comparator (2026-04-25 re-fire) = 1.06× yield contrast** (SUPERSEDED
2026-04-25 narrow-validation 12/96 / 4.25× baseline preserved in
`TRACK-A-FROZEN-NUMBERS.md`), with 0 Tier A and 9 Tier C across the 10 EUR
autosomal curated regions on real LD plus AFR / HLA / BMI_Xq24 regions on
the legacy identity-LD fallback pending M3; Phase 5
LDSC partitioned heritability + HESS (290 local-h² outputs) + MAGMA 8/8
traits + LDSC-SEG tissue-specific enrichment; Phase 9 replication
scaffolding across FinnGen R12 + GBMI + MVP + BBJ with FIQT
winner's-curse correction and metafor IVW meta. These artifacts flow into
both Track A (primary data) and Track B (candidate-locus validation
subset) per Amendment §8.

**M1 sumstats upgrade + harmonization — COMPLETE 2026-04-25.** All 6 plans
landed (m1-00 through m1-04); verifier independently PASSED 5/5 ROADMAP
success criteria (harmonized parquet, per-trait QC, LDSC-munged files,
SHA-256 manifests, trait inventory YAML). Delivered: 26 D-16 harmonized
`.tsv.bgz`+`.tbi`+`.parquet` triples; 47-cell `config/trait_inventory.yaml`;
12-trait LDSC bivariate intercept matrix (12×12, symmetric, 64/66 pairs
filled, diag=1.0) at `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv`;
two SHA-256 manifests (45-row primary raw + 73-row harmonized) at
`.planning/amendments/`; OSF amendment paste-ready in
`OSF-AMENDMENT-TEXT-2026-04-22.md`. Plan was designed to tolerate Wave-1
deferrals (`m1_raw_glob.py` `.deferred`-marker guard) — 12-trait matrix
is the M2 MTAG `--overlap` consumer artifact; expansion to ~26 traits
is queued via Carter resume queue + DEF-M1-03-02. Two new decisions
recorded: DEC-2026-04-24-01 (GRCh37 canonical override of Amendment §3
GRCh38 wording) and DEC-2026-04-24-02 (AoU AFR-SBP M2 fallback for
Giri 2019 D-06).

**Track B M2–M6 — gated on Carter OSF web-UI submission** (Amendment §9.1
hard gate). M2 LDSC + MTAG + CPASSOC discovery cannot commit until OSF
amendment posts at osf.io/pvb5j. Carter resume queue (DIAMANTE cookies,
GBMI portal, Loh D-01, Klarin D-03, MAGIC EUR re-fetch) is independent
of M2 kickoff.

Last updated: 2026-04-28.

## Open human-action items

These three items are outside Claude tool scope and require Carter action.
They are flagged here as the forward-looking gate list for M0 closeout and
for M1/M2 kickoff.

- **(a) OSF amendment submission** — **BLOCKS M2 execution** per Amendment
  §9. The draft amendment text is in Amendment §9.3. Submission is a manual
  action through the OSF web UI at
  [osf.io/pvb5j](https://osf.io/pvb5j) (root pre-registration, DOI
  [10.17605/OSF.IO/PVB5J](https://doi.org/10.17605/OSF.IO/PVB5J)) and the
  existing amendment record at [osf.io/az52u](https://osf.io/az52u)
  (distal-gene expansion, already filed). Confirmation PDF is to be saved
  under `.planning/amendments/` with filename pattern
  `osf-amendment-m0-2026-04-XX.pdf` (date finalized on submission).
  M2 MTAG / CPASSOC discovery runs are blocked until this lands. Claude
  cannot submit the amendment; Carter web-UI action required.

- **(b) BMI EUR primary-source decision** — The trait inventory lists two
  candidate sources: Loh 2022 *Nature Communications* (n ≈ 1.1M,
  GIANT + 23andMe, GRCh38; `SUMSTATS-UPGRADE.tsv` row 3) and Yengo 2022
  GIANT + UKBB (n ≈ 700k, GRCh37; `SUMSTATS-UPGRADE.tsv` row 2). The
  Amendment §9.3 draft text cites Yengo 2022 in the declared trait
  inventory; SUMSTATS-UPGRADE.tsv flags Loh 2022 as the larger-N candidate.
  To be locked at M1 kickoff before LDSC munge.

- **(c) MVP phs001672 DUA submission status** — Giri 2019 MVP SBP-AFR
  (`SUMSTATS-UPGRADE.tsv` row 13, status `dua_pending`) requires
  confirmation of current submission status with the VA Data Access
  Request System. Gates the SBP-AFR ancestry stratum for M1 harmonization.
