---
phase: 260426-aow
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md
  - .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-SUMMARY.md
  - .planning/STATE.md
autonomous: true
requirements:
  - AOU-WORKBENCH-REGISTRATION-TRACK-B-M3
user_setup: []

must_haves:
  truths:
    - "A single new document at .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md contains paste-ready content for All of Us Researcher Workbench portal workspace creation."
    - "Document covers Track B + M3 ONLY; Track A is explicitly omitted with a single paragraph stating Track A uses 1000G Phase 3 EUR real LD on 10 EUR autosomal regions only and requires no AoU controlled-tier access."
    - "Document sections map 1:1 to AoU portal Research Purpose Statement fields: Workspace Title, Research Summary (plain language), Scientific Approach, Methods Inventory, Notebooks/Components Inventory, Data Use & Egress Plan, Anticipated Findings, Disease Focus (9 traits × 2 ancestries with AFR emphasis rationale), Why Interested, Use of Race / Ancestry / Demographics, Expected Publications, OSF cross-link."
    - "Trait inventory table reproduces the 9 Track B traits (BMI, T2D, stroke, SBP, asthma, CAD, lipids, eGFR, HbA1c) sourced from .planning/amendments/SUMSTATS-UPGRADE.tsv with EUR + AFR columns."
    - "Methods inventory enumerates LDSC, MTAG, CPASSOC, PLINK clumping, ABF-coloc, SuSiE-RSS, HyPrColoc, PolyFun baselineLF2, mtCOJO sensitivity, L2G/Open Targets, Borzoi/Enformer per .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §6."
    - "Notebooks/components inventory distinguishes inside-AoU work (Hail Dataproc cohort QC, hl.ld_matrix per-region computation, optional EUR parity panel, R validation memo, LD QC log) from outside-AoU work (npz→rds conversion, Snakemake fine-mapping, coloc, manuscript) per .planning/amendments/AOU-LD-PIPELINE.md §5 + §8."
    - "Data Use and Egress Plan section reproduces the AOU-LD-PIPELINE.md §7 export protocol: per-region LD .npz aggregate matrices exportable post-AoU-review, no individual-level genotypes, no sample-level metadata, ≥20 cell-suppression floor (trivially satisfied because each LD cell is computed across all n≈60–95k participants), per-chromosome bundled export requests."
    - "Anticipated Findings section reports five novel-variant discovery classes with locked yield estimates (Class 1 50–200, Class 2 5–30, Class 3 100–400, Class 4 30–150, Class 5 10–50) per PROJECT-AMENDMENT §7.1–§7.3."
    - "Use of Race/Ancestry/Demographics section uses PCA-based ancestry (not self-ID gate) for cohort definition; describes how demographics WILL be used (LD reference construction, ancestry-stratified GWAS, kinship pruning) and WILL NOT be used (no individual prediction, no group-level biological essentialism); language anchored in AOU-LD-PIPELINE.md §13 RPS template."
    - "Expected Publications section commits to: (1) Track B → Nature Genetics (genome-wide novel-variant + cross-trait pleiotropy, M6 est. 2027-04 / 2027-05); (2) M3 deliverable → Scientific Data data descriptor + Zenodo deposit (AoU-derived AFR LD reference panel, summary-only post AoU review)."
    - "OSF cross-link explicit: root pre-registration osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) + amendment record osf.io/az52u where the Track B / AoU LD egress amendment is filed; PI ORCID 0000-0003-2669-8200."
    - "Document includes a 'paste-time trim note' at the top advising the reader to right-size each section to AoU portal field character limits before submission."
    - "Every factual claim in the document carries an inline `[src: <path> §<section>]` footnote so the user can verify before pasting."
    - "STATE.md gains exactly one new row in the Quick Tasks Completed table cross-linking to this quick-task directory; nothing else in STATE.md changes."
    - "PROJECT.md, ROADMAP.md, .planning/amendments/* and the AoU portal itself are NOT modified by this plan."
    - "Two atomic commits maximum: (1) the AOU-WORKBENCH-REGISTRATION.md deliverable + this PLAN.md, (2) the SUMMARY.md + STATE.md row."
  artifacts:
    - path: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md"
      provides: "Paste-ready Markdown document for AoU Researcher Workbench workspace creation portal — Track B + M3 only"
      contains: "Workspace Title, Research Summary, Scientific Approach, Methods Inventory, Components & Notebooks Inventory, Data Use & Egress Plan, Anticipated Findings, Disease Focus (9 traits × 2 ancestries), Why Interested, Use of Race/Ancestry/Demographics, Expected Publications, OSF cross-link, Track A explicit omission paragraph, P&P registration disclosure note"
      min_lines: 200
    - path: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-SUMMARY.md"
      provides: "Quick-task closure summary"
      contains: "One-liner, atomic commit table, deliverable locations, verification checks"
      min_lines: 40
    - path: ".planning/STATE.md"
      provides: "Quick Tasks Completed table row for 260426-aow"
      contains: "260426-aow"
      min_lines: 1
  key_links:
    - from: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md"
      to: ".planning/amendments/AOU-LD-PIPELINE.md"
      via: "inline `[src: ...]` footnotes citing §1, §3, §5, §7, §9, §13"
      pattern: "AOU-LD-PIPELINE\\.md"
    - from: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md"
      to: ".planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md"
      via: "inline `[src: ...]` footnotes citing §4, §5, §6, §7"
      pattern: "PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe\\.md"
    - from: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md"
      to: ".planning/amendments/SUMSTATS-UPGRADE.tsv"
      via: "trait inventory table footnote"
      pattern: "SUMSTATS-UPGRADE\\.tsv"
    - from: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md"
      to: ".planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md"
      via: "egress wording mirror reference"
      pattern: "OSF-AMENDMENT-TEXT-2026-04-22\\.md"
    - from: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md"
      to: "osf.io/az52u"
      via: "Expected Publications section explicit cross-link"
      pattern: "az52u"
    - from: ".planning/STATE.md"
      to: ".planning/quick/260426-aow-aou-workbench-registration-track-b-m3/"
      via: "Quick Tasks Completed table relative-path link"
      pattern: "260426-aow"
---

<objective>
Produce a paste-ready Markdown document at
`.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md`
that contains all content needed for Carter to create the All of Us
Researcher Workbench workspace for Track B + M3 (AFR LD reference panel
build). The document covers Workspace Title, Research Summary,
Scientific Approach, Methods Inventory, Components & Notebooks
Inventory, Data Use & Egress Plan (per Amendment §5 / OSF-AMENDMENT-TEXT
paragraph (f) verbatim), Anticipated Findings, Disease Focus (9 traits ×
2 ancestries with AFR emphasis), Why Interested, Use of Race / Ancestry
/ Demographics, Expected Publications (Track B → Nature Genetics + M3 →
Scientific Data + Zenodo), OSF cross-link to az52u, and an explicit
single-paragraph omission of Track A (which uses 1000G Phase 3 EUR real
LD only and does not require AoU access). Every claim is footnoted with
an inline `[src: <path> §<section>]` reference so the user can verify
content fidelity before paste. Document includes a top-of-file
paste-time trim note since AoU portal field character limits vary.

Out of scope: editing PROJECT.md / ROADMAP.md / .planning/amendments/*
or the AoU portal itself; running any compute; making any decisions
beyond what is already recorded in PROJECT-AMENDMENT-2026-04-22 and
AOU-LD-PIPELINE.md.

Open questions resolved by reasonable default (auto mode):
1. Track A submission tense → forward-looking ("being submitted in 2026-05 / 2026-06"),
   matching the actual ROADMAP Track-A-finalization milestone state.
2. Scientific Data venue → committed explicitly per the user's command.
   Flagged as a new commitment for Carter to record in DECISIONS.md if desired.
3. Portal field-format granularity → narrative-Markdown with conservative
   sectioning under typical AoU character limits, plus a paste-time trim
   note at the document top.
</objective>

## Tasks

### Task 1 — Build AOU-WORKBENCH-REGISTRATION.md and commit

**Action:** Write the paste-ready document at
`.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md`.

**Source files** (read-only, citations only):
- [`.planning/PROJECT.md`](../../../.planning/PROJECT.md) — Who, What, Why, Goals
- [`.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`](../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md) — §4 Trait Inventory, §5 AFR LD Panel Strategy, §6 Method Stack, §7 Novel-Variant Discovery, §11 Timeline
- [`.planning/amendments/AOU-LD-PIPELINE.md`](../../amendments/AOU-LD-PIPELINE.md) — §1 Purpose, §3 Cohort Definition, §5 Hail BlockMatrix Pipeline, §7 Export Protocol, §9 Validation Protocol, §13 AoU Publication Policy Integration
- [`.planning/amendments/SUMSTATS-UPGRADE.tsv`](../../amendments/SUMSTATS-UPGRADE.tsv) — 9-trait × ancestry × source-cohort × N inventory
- [`.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md`](../../amendments/OSF-AMENDMENT-TEXT-2026-04-22.md) — paragraph (f) egress language to mirror
- [`.planning/amendments/TRACK-A-PIVOT.md`](../../amendments/TRACK-A-PIVOT.md) — Track A working title and venue ladder, for omission paragraph

**Atomic commit:**
- Stage: `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-PLAN.md` and `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md`
- Commit message: `docs(quick-260426-aow): draft AoU Researcher Workbench workspace registration (Track B + M3)`

### Task 2 — Write SUMMARY.md and update STATE.md

**Action:**
- Write `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-SUMMARY.md` with the standard YAML frontmatter + One-liner + Atomic commits table + Verification checks.
- Append a new row to the Quick Tasks Completed table in [`.planning/STATE.md`](../../STATE.md) for `260426-aow`.

**Atomic commit:**
- Stage only: `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-SUMMARY.md` and `.planning/STATE.md`
- Pre-existing dirty paths (`.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`, other `260426-06n-*` quick-task scratch md5 files, untracked `bin/fire_m2_04_mtcojo.sh`, `bin/track-a-repro-bundle.*`, `src/python/*.py`, `src/snakemake/rules/m2_*.smk`) are NOT staged.
- Commit message: `docs(quick-260426-aow): close AoU workspace registration quick task (SUMMARY + STATE row)`

## Verification

- `grep -c '\[src:' .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` ≥ 20 (every factual claim cited).
- `grep -c 'Track A' .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` returns ≥ 1 (omission paragraph present).
- `grep -c 'az52u' .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` returns ≥ 1 (OSF cross-link present).
- `grep -E '^## ' .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` returns ≥ 11 section headers (matches portal-section count + omission + P&P note).
- `git log --oneline -2` shows two new commits with `(quick-260426-aow)` scope tag.
- `grep -c '260426-aow' .planning/STATE.md` returns ≥ 1 (table row added).
