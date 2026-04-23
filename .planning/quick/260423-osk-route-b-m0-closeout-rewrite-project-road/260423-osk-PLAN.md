---
phase: quick-260423-osk
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/DECISIONS.md
autonomous: true
requirements:
  - AMEND-2026-04-22-SEC3   # M0–M6 milestone table
  - AMEND-2026-04-22-SEC4   # 9-trait × 2-ancestry inventory
  - AMEND-2026-04-22-SEC7   # 5 novel-variant discovery classes
  - AMEND-2026-04-22-SEC8   # preserved artifacts (pre-pivot spine reuse)
  - AMEND-2026-04-22-SEC9   # OSF amendment timing constraint
  - AMEND-2026-04-22-SEC12  # planning doc rewrite spec
  - AOU-LD-EGRESS           # controlled-tier WGS, summary-only export
  - SKIP-OSF-SUBMISSION     # explicit human-action gate, do NOT submit
must_haves:
  truths:
    - ".planning/PROJECT.md describes the M0–M6 two-track plan as original, hypothesis-driven research (never 'revision' or 'cleanup')"
    - ".planning/PROJECT.md preserves the six CLAUDE.md constraint bullets verbatim"
    - ".planning/PROJECT.md flags the three open human-action items at the end of the file"
    - ".planning/ROADMAP.md archives Phase 00–11 under a 'Pre-pivot spine' section without deleting content"
    - ".planning/ROADMAP.md lists the seven M0–M6 slugs plus a Track A finalization row"
    - ".planning/REQUIREMENTS.md covers all 9 traits, both tracks, the 5 novelty classes, and AoU egress compliance"
    - ".planning/REQUIREMENTS.md preserves load-bearing pre-pivot REQs (Snakemake CI, SuSiE-RSS policy, public-data-only)"
    - ".planning/DECISIONS.md has exactly 5 new entries appended after DEC-2026-04-21 (distal gene scope) with no prior entries modified"
    - "All four files committed as four separate atomic commits on main, no push, no worktree"
  artifacts:
    - path: ".planning/PROJECT.md"
      provides: "Two-track scope, M0–M6 milestone references, verbatim constraints, open human-action items"
      contains: "M0–M6"
    - path: ".planning/ROADMAP.md"
      provides: "Pre-pivot spine archive + current milestone sequence (Track B M0–M6) + Track A finalization row"
      contains: "Pre-pivot spine"
    - path: ".planning/REQUIREMENTS.md"
      provides: "9-trait × 2-ancestry × joint-signal REQ set with 5 novelty classes + AoU egress compliance + preserved SuSiE-RSS REQ"
      contains: "novelty class"
    - path: ".planning/DECISIONS.md"
      provides: "Append-only log with 5 new dated entries for candidate-locus abandonment + 9-trait locks + MTAG/CPASSOC + AoU-AFR LD + two-track strategy"
      contains: "DEC-2026-04-22-01"
  key_links:
    - from: ".planning/PROJECT.md open human-action items"
      to: ".planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §9"
      via: "explicit relative-path reference"
      pattern: "amendments/PROJECT-AMENDMENT-2026-04-22"
    - from: ".planning/ROADMAP.md M-entries"
      to: ".planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §3"
      via: "each M-entry cites Amendment §3 row"
      pattern: "Amendment §3"
    - from: ".planning/REQUIREMENTS.md AoU-LD REQ"
      to: ".planning/amendments/AOU-LD-PIPELINE.md"
      via: "egress-policy compliance citation"
      pattern: "AOU-LD-PIPELINE"
    - from: ".planning/DECISIONS.md new entries"
      to: ".planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §2/§3/§4"
      via: "each DEC entry cites Amendment section"
      pattern: "Amendment §"
---

<objective>
Close out Track B milestone M0 (pivot scaffolding) by rewriting the four
top-level .planning/ documents to the M0–M6 two-track framing defined in
Amendment §3. Four atomic commits (one per file); no push; no worktree.

Purpose: Lock the planning scaffold to the post-pivot structure so every
subsequent GSD session (M1 sumstats planning, M2 OSF gating, M3 AoU-LD
kickoff) reads a coherent source of truth. Without this rewrite, STATE.md
is the only doc reflecting the pivot, and `/gsd-plan-phase M1` would draw
on stale T1/T2/T3 tier language.

Output: Four planning files rewritten as forward-looking original research
(never "revision", "cleanup", or "fix"), each committed separately on main.

Explicit non-goals:
- Do NOT submit the OSF amendment. OSF web UI is manual; M2 execution is
  gated on OSF posting per Amendment §9 but the submission is Carter's
  web-UI action. This plan surfaces it as an open human-action item.
- Do NOT run Route C sumstats downloads or Route A manuscript edits. Those
  are separate steps in snappy-humming-pine.md (Steps 1 and 2 respectively).
- Do NOT touch STATE.md. That's Step 3.2 of snappy-humming-pine.md and
  runs after all four doc rewrites land.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/DECISIONS.md
@.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@.planning/amendments/AOU-LD-PIPELINE.md
@CLAUDE.md

<interfaces>
<!-- Key upstream anchors the executor will consume directly. -->

Amendment §3 (M0–M6 milestone table): seven rows with Content / Duration /
Dependencies / Deliverables. Each ROADMAP M-entry MUST cite its §3 row.

Amendment §4 (trait inventory): 9 traits × up to 2 ancestries. Note the
BMI EUR row has TWO candidate sources (Yengo 2022 in the §9.3 amendment
text, AND the SUMSTATS-UPGRADE.tsv has Loh 2022 n=1,108,983 on row 3 +
Yengo 2018 n=681,275 on row 2). The primary-source decision is outstanding
and MUST be surfaced as an open human-action item in PROJECT.md.

Amendment §7 (5 discovery classes): Class 1 joint-signal, Class 2 AFR-
specific, Class 3 secondary-signal, Class 4 pleiotropy-class, Class 5
functional-mechanism. REQUIREMENTS must name each class with operational
threshold per §7.1.

Amendment §8 (preserved artifacts): Phase 0 reference data, Phase 1 SuSiE
outputs, Phase 2 Stage 2 real-LD coloc, Phase 5 LDSC+HESS+MAGMA+LDSC-SEG,
Phase 9 replication scaffolding. ROADMAP "Pre-pivot spine" section MUST
preserve the Phase 00–11 content verbatim (so per-phase git-history traces
stay interpretable).

Amendment §9 (OSF timing): Amendment posts AFTER M1 sumstats harmonization
completes and BEFORE any M2 MTAG/CPASSOC run. This is a hard pre-reg gate,
NOT something to execute here — surface as open human-action item only.

CLAUDE.md "## Constraints" subsection (lines 56–72 of current PROJECT.md,
which duplicates CLAUDE.md lines 4–24): six bullet points. PROJECT.md
rewrite MUST preserve all six verbatim (they are the project's anchoring
invariants). Do NOT change wording or ordering.

TRACK-A-FROZEN-NUMBERS.md (disk-verified):
- 51/96 non-empty credible sets (4.25× identity-LD baseline of 12/96)
- 0 Tier A, 0 Tier B, 9 Tier C (4 AFR + 5 EUR)
- 224 negative-control rows, all null (pre-registered behavior matched)
- SH2B3 × asthma EUR: identity-LD PP.H4=1.0 → real-LD n_cs_a=0
- 28 trait-pair coloc.susie attempts (0 with valid PP.H3/PP.H4)
- 1,274 QTL-coloc attempts (32 successes, 1,005 too_few_snps)
If any of these numbers appear in REQUIREMENTS.md they must match this
file verbatim. (Expected: REQUIREMENTS shouldn't cite these — they're
Track A numbers and belong in the manuscript + OSF amendment.)

AOU-LD-PIPELINE.md §7 (export protocol): summary-only LD matrix + AF
metadata via AoU Researcher Workbench → Terra UI → workspace → Notebooks/
Files → Request export. Egress is AoU-policy-compliant; REQUIREMENTS
must reference this path.
</interfaces>

<phase_slugs>
<!-- Canonical ROADMAP row slugs (from task_boundary) -->
M0: m0-pivot-scaffolding
M1: m1-sumstats-upgrade-and-harmonization
M2: m2-ldsc-mtag-cpassoc-discovery
M3: m3-aou-afr-ld-panel-build
M4: m4-scalable-coloc-finemapping
M5: m5-variant-to-gene-prioritization-plus-novelty-cross-reference
M6: m6-manuscript-and-replication
</phase_slugs>

<language_constraints>
MANDATORY wording rules for every task:

- Frame as "original research", "forward-looking scope expansion", "hypothesis-
  driven genome-wide discovery". NEVER "revision", "cleanup", "fix", "correct",
  "re-do". The 2026-04-22 pivot is a scope expansion informed by Stage 2
  evidence, not a retraction.
- The candidate-locus work is "pre-specified methods validation subset" (per
  Amendment §8), NOT "failed attempt" or "discarded approach".
- Track A is "short-form methods paper leveraging existing real-LD audit",
  NOT "salvage paper" or "consolation prize".
- Phase 00–11 content in ROADMAP is "pre-pivot spine, completed, artifacts
  reusable", NOT "abandoned" or "obsolete".
- DECISIONS.md entries use "adopted", "locked", "chosen", "selected" — never
  "corrected", "reversed", "fixed".
</language_constraints>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Rewrite .planning/PROJECT.md to M0–M6 two-track framing</name>
  <files>.planning/PROJECT.md</files>
  <action>
Rewrite .planning/PROJECT.md per Amendment §12 row 1 ("Replace scope section
with 9-trait × 2-ancestry genome-wide framing; add Track A / Track B
structural note; preserve constraints block verbatim").

Structure of the new file (top-to-bottom):

1. **Header**: `# PROJECT.md — coloc_analysis` (retain)

2. **North-star pointer** (1 paragraph): Replace the existing Revision_Plan /
   GSD_BRIEFING pointer with:
   - Authoritative pivot charter: `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`
   - Companion docs: `TRACK-A-PIVOT.md`, `SUMSTATS-UPGRADE.tsv/.md`, `AOU-LD-PIPELINE.md`, `TRACK-A-FROZEN-NUMBERS.md`
   - Project-instruction anchor: `CLAUDE.md`

3. **Who** section (retain verbatim): Carter K. Clinton, ASHES Lab, NCSU, solo author.

4. **What** section (REPLACE entirely): Two-track original research program.
   - **Track A** — Real-LD audit of 50 curated cardiometabolic regions under
     current-best-practice SuSiE-RSS + coloc.susie with matched real LD.
     Quantifies how published candidate-locus pleiotropy claims survive a
     fully-pre-registered real-LD re-analysis. Target venue ladder: Genome
     Medicine → AJHG short report → Bioinformatics Applications Note. Artifacts
     are the Phase 1/2/5/9 pre-pivot spine outputs (reusable per Amendment §8).
   - **Track B** — Genome-wide joint-signal discovery across 9 complex traits
     (BMI, T2D, stroke, SBP, asthma, CAD, lipids [LDL primary; HDL/TG/TC
     secondary], eGFR, HbA1c) in EUR and AFR ancestries, executed under
     milestones M0–M6 per Amendment §3. Two co-equal scientific aims: (i)
     cross-trait pleiotropy discovery and (ii) novel-variant discovery across
     five operationally-defined classes (joint-signal, AFR-specific, secondary-
     independent, pleiotropy-class, functional-mechanism). Target venue:
     Nature Genetics.

5. **Where** section (retain the path table verbatim — canonical repo,
   upstream data root, miniconda3, LSF, GPFS constraints).

6. **Why (in one paragraph)** (REPLACE): Original-research motivation framing
   per Amendment §2. Summary: the candidate-locus design is non-informative
   about genome-wide pleiotropy architecture by construction (regions chosen
   because prior literature reported cross-trait signal there); Track A
   quantifies that as a pre-specified methods-validation contribution, while
   Track B pursues genome-wide hypothesis-agnostic discovery using multi-trait
   methods (MTAG Turley 2018 + CPASSOC Zhu 2015), two-stage scalable coloc
   (ABF triage → SuSiE-RSS rescue + PolyFun baselineLF2 priors Weissbrod 2020),
   HyPrColoc ≥3-trait, and All-of-Us controlled-tier WGS (~100k AFR) for real
   matched-ancestry LD. Five novel-variant discovery classes are pre-registered
   with locked comparator catalogs (GWAS Catalog, Pickrell 2016, Watanabe 2019,
   Open Targets L2G, ClinVar) per Amendment §7. FRAMING: forward-looking scope
   expansion informed by Stage 2 real-LD evidence — NOT revision, correction,
   cleanup, or fix.

7. **Constraints** section — PRESERVE VERBATIM. Copy the exact six bullet
   points from current PROJECT.md lines 56–72 (which already match CLAUDE.md
   lines 4–24). Do NOT reword. These are the project's anchoring invariants
   (public-data-only; solo-author; timeline-not-binding; no-web-stack; DUA
   lead-time reality; GPFS no-worktree).

8. **Goals for this GSD-managed program** (REPLACE): Replace the T1/T2/T3
   checkpoint language with M0–M6 goals.
   - Execute M0–M6 Track B to Nature Genetics acceptance bar.
   - Ship Track A short-form at Genome Medicine (primary) independently of M1–M6 progress.
   - Pre-register all Track B claims on OSF via the amendment flow described in
     Amendment §9 (amendment posts at end of M1, before M2 MTAG/CPASSOC runs).
   - Deliver reproducible Snakemake pipeline with pinned conda envs,
     Singularity containers, Zenodo-deposited AoU-derived AFR LD panels, and
     hold-out replication on FinnGen / Pan-UKBB / MVP (REQ-1 + Snakemake CI REQ).

9. **Current status** (REPLACE): Summarize M0 progress. Pre-pivot spine
   (Phases 0/1/2/5/9) complete and artifacts are the Track A data + Track B
   validation subset. Stage 2 real-LD production fire 2026-04-22 produced
   51/96 non-empty credible sets (4.25× identity-LD baseline of 12/96); 0 Tier
   A, consistent with Amendment §2.2 pre-registration. M0 pivot scaffolding in
   flight: 6 amendment artifacts committed under `.planning/amendments/`;
   Track A first-pass draft committed; this PROJECT.md rewrite + the parallel
   ROADMAP/REQUIREMENTS/DECISIONS rewrites + OSF amendment web-UI submission
   are the remaining M0 closeout items.
   Last updated: 2026-04-23.

10. **Open human-action items** (NEW subsection at end of file):
    - (a) **OSF amendment submission** (gates M2 execution per Amendment §9).
      Draft amendment text lives in Amendment §9.3. Submission is manual via
      the OSF web UI at osf.io/pvb5j (root pre-reg) and the existing amendment
      record osf.io/az52u. Confirmation PDF to be saved to
      `.planning/amendments/osf-amendment-m0-2026-04-XX.pdf` (filename to be
      finalized on submission date). M2 MTAG/CPASSOC runs are BLOCKED until
      this lands. Claude tools cannot submit; Carter web-UI action.
    - (b) **BMI EUR primary-source decision**: Loh 2022 (n≈1.1M, GIANT+23andMe,
      GRCh38) vs Yengo 2022 GIANT+UKBB (n≈700k, GRCh37) per SUMSTATS-UPGRADE.tsv
      rows 2–3. Amendment §9.3 draft text names Yengo 2022 in the declared
      trait inventory but the SUMSTATS-UPGRADE.tsv prefers Loh 2022 for N. To
      be locked at M1 kickoff before LDSC munge.
    - (c) **MVP phs001672 DUA submission status**: Giri 2019 MVP SBP-AFR (row
      13 of SUMSTATS-UPGRADE.tsv) is `dua_pending`. Carter-action to verify
      current status with the VA Data Access Request System.

Wording rules:
- NEVER use "revision", "cleanup", "fix", "correct", "re-do", "failed",
  "abandoned", "obsolete", "salvage".
- USE "original research", "scope expansion informed by", "pre-specified
  methods validation", "forward-looking", "adopted", "locked".

Do NOT:
- Do NOT modify the "Constraints" subsection wording. It is locked to CLAUDE.md.
- Do NOT touch CLAUDE.md itself. Its "## Constraints" section belongs to it.
- Do NOT reference T1/T2/T3 tier language anywhere in the new body.
- Do NOT remove the Where path table.
- Do NOT claim to have submitted the OSF amendment.

After writing the file, commit it as a standalone atomic commit:
`git add .planning/PROJECT.md`
`git commit -m "docs(project): rewrite PROJECT.md to M0–M6 two-track framing per Amendment §12"`
  </action>
  <verify>
    <automated>test -f .planning/PROJECT.md && grep -q "M0" .planning/PROJECT.md && grep -q "M6" .planning/PROJECT.md && grep -q "Track A" .planning/PROJECT.md && grep -q "Track B" .planning/PROJECT.md && grep -q "GPFS" .planning/PROJECT.md && grep -q "no-web-stack\|No web/JS" .planning/PROJECT.md && grep -q "public data" .planning/PROJECT.md && ! grep -qiE "revision|cleanup|\\bfix[ ,.]|correct the" .planning/PROJECT.md && grep -q "Open human-action" .planning/PROJECT.md && grep -q "osf.io/pvb5j" .planning/PROJECT.md && git log -1 --pretty=%B -- .planning/PROJECT.md | grep -q "M0–M6\|M0-M6"</automated>
  </verify>
  <done>
.planning/PROJECT.md contains M0–M6 two-track framing; six CLAUDE.md
constraint bullets preserved verbatim; three open human-action items flagged
at end (OSF submission + BMI source decision + MVP DUA); no prohibited
language ("revision", "cleanup", "fix the…") anywhere in the body; file
committed as a single atomic commit on main with message per task_boundary.
  </done>
</task>

<task type="auto">
  <name>Task 2: Rewrite .planning/ROADMAP.md — pre-pivot archive + M0–M6 + Track A finalization</name>
  <files>.planning/ROADMAP.md</files>
  <action>
Rewrite .planning/ROADMAP.md per Amendment §12 row 2, keeping per-phase git-
history traces interpretable by preserving Phase 00–11 content under an
explicit "Pre-pivot spine" heading rather than deleting it.

Structure of the new file (top-to-bottom):

1. **Header**:
```
# Roadmap: coloc_analysis

> **Pivot note** (2026-04-22): This program was reframed from a 50-region
> candidate-locus study into a two-track original research program covering
> genome-wide joint-signal discovery across 9 traits × 2 ancestries (Track B,
> milestones M0–M6) plus a pre-specified short-form methods validation paper
> leveraging the existing real-LD audit (Track A finalization). Pivot charter:
> `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`.
> The pre-pivot Phase 00–11 content is preserved below under "Pre-pivot
> spine"; its artifacts are reusable per Amendment §8 and form the Track A
> data plus the Track B candidate-locus validation subset.
```

2. **## Overview** (REPLACE body): Two-track original research program.
   Track B runs M0 → M1 → M2 → M3 → M4 → M5 → M6 with M2 gated on OSF
   amendment posting, M3 partially parallel with M2, M4 gated on M3 LD
   panels + M2 region list, M5 gated on M4 Tier A, M6 gated on M5. Track A
   is scientifically independent and ships on pre-pivot spine outputs.

3. **## Current milestone sequence (Track B M0–M6)**: Seven entries using
   the canonical slugs. For each M-entry, follow this template sourced
   verbatim from Amendment §3:

```
### M0: Pivot scaffolding
**Slug**: m0-pivot-scaffolding
**Goal**: Adopt pivot charter; rewrite .planning/ scaffold (Amendment §12);
lock 9-trait × 2-ancestry inventory; lock phenotype definitions; write
TRACK-A-PIVOT.md, SUMSTATS-UPGRADE, AOU-LD-PIPELINE.md.
**Requirements**: REQ-AMEND-SEC12, REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI
(carried forward)
**Dependencies**: None (planning only)
**Success Criteria**:
  1. Amendment committed under `.planning/amendments/`
  2. PROJECT / ROADMAP / REQUIREMENTS / DECISIONS rewritten to M0–M6 framing
  3. 9-trait × 2-ancestry inventory locked (Amendment §4)
  4. Track A and Track B companion documents committed
**Deliverable Artifacts**:
  - `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`
  - Updated `.planning/PROJECT.md` / `ROADMAP.md` / `REQUIREMENTS.md` / `DECISIONS.md`
  - `TRACK-A-PIVOT.md`, `TRACK-A-FROZEN-NUMBERS.md`, `SUMSTATS-UPGRADE.{md,tsv}`, `AOU-LD-PIPELINE.md`, `SUMSTATS-MANUAL-FETCH.md`
**Gating condition for M1**: M0 scaffolding commit lands (this plan's 4 commits).
**Status**: in flight — scaffolding complete; doc rewrites are this plan.
```

Repeat the template for M1–M6. Extract Goal / Dependencies / Deliverable
Artifacts from Amendment §3 each row. Each entry must have:
- Slug (from phase_slugs in <context>)
- Goal (from Amendment §3 "Content" column)
- Requirements (cross-cut to REQUIREMENTS.md IDs)
- Dependencies (from Amendment §3 "Critical-Path Dependencies")
- Success Criteria (3–5 measurable; derive from Amendment §3 + §7 for novelty deliverables where M=2, 4, 5)
- Deliverable Artifacts (from Amendment §3 "Deliverable Artifacts" + Amendment §7 novelty TSVs where M=2, 4, 5)
- Gating condition for starting the next milestone (only M>=1)

Key details to encode (do not omit):
- **M1**: est 4–6 weeks; download per SUMSTATS-UPGRADE.tsv; per-ancestry QC;
  LDSC-munge + MTAG-ready formats; ancestry and sample-overlap flags verified.
  Gating for M2: "M1 harmonization verified AND OSF amendment posted per
  Amendment §9" — both conditions must hold.
- **M2**: LDSC pairwise rg → MTAG --overlap with LDSC intercept → CPASSOC
  orthogonal SHom/SHet → PLINK clump (p=5e-8, r²<0.01, 1Mb) → union region
  list (~1,500–3,000 regions). Novelty deliverable Class 1 (joint-signal
  novel).
- **M3**: Inside AoU Researcher Workbench (Terra), build per-region LD
  matrices from controlled-tier WGS per AOU-LD-PIPELINE.md; export summary-
  only (LD matrix + AF metadata) per AoU data-egress policy; parallel EUR
  rebuild from 1000G+UKB for parity.
- **M4**: Two-stage coloc (ABF genome-wide → SuSiE-RSS where PP.H4 > 0.5);
  HyPrColoc ≥3 traits; PolyFun baselineLF2 functional priors per Weissbrod
  2020. Novelty Classes 2 (AFR-specific) + 3 (secondary-signal).
- **M5**: L2G (Open Targets) + eQTL/pQTL coloc refresh + Borzoi variant-
  effect scoring per Linder 2024 + MAGMA re-run. Novelty Classes 4
  (pleiotropy-class) + 5 (functional-mechanism). Catalog versions locked
  at M5 cross-reference date with SHA-256 checksums.
- **M6**: Hold-out replication (FinnGen / Pan-UKBB / MVP release n+1);
  Nature Genetics submission; OSF post-reg deposit.

4. **## Current milestone sequence (Track A short-form)**: Single entry.

```
### Track-A-finalization
**Slug**: track-a-finalization
**Goal**: Finalize Track A short-form methods paper framing the real-LD audit
of 50 curated cardiometabolic regions; submit bioRxiv preprint + venue
(Genome Medicine primary; AJHG short-report / Bioinformatics Applications
fallbacks).
**Requirements**: REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI, REQ-SUSIE-RSS-POLICY,
REQ-OSF-PREREG (carried forward from pre-pivot)
**Dependencies**: Pre-pivot spine (Phases 1, 2, 5, 9) outputs; independent of
Track B milestone sequence
**Sub-tasks**:
  - [x] Numeric reconciliation complete (2026-04-23, commit 05a701a): Stage 2
    values locked in TRACK-A-FROZEN-NUMBERS.md (51/96 CS; 0 Tier A; SH2B3 ×
    asthma EUR identity-LD PP.H4=1.0 → real-LD n_cs_a=0; 224 negative-control
    rows all null)
  - [ ] Introduction rewrite (TRACK-A-PIVOT.md §4.5): 5-paragraph restructure;
    strip ML framing; demote evolutionary-medicine to Discussion
  - [ ] Discussion rewrite (TRACK-A-PIVOT.md §4.17): identity-LD inflation as
    dominant finding; drug-target-inference caution; Track B forward pointer
  - [ ] References additions: Wallace 2021, Zou 2022, Weissbrod 2020, Benner 2017
  - [ ] 3 figures: identity-LD vs real-LD CS yield, SH2B3 locus plot,
    pathway enrichment reconfiguration (build scripts under `src/R/figures/`)
  - [ ] bioRxiv preprint submission (Day 1 of draft-complete)
  - [ ] Genome Medicine Original Research submission (primary target)
**Success Criteria**:
  1. bioRxiv DOI minted and logged in `.planning/amendments/`
  2. Genome Medicine submission confirmation + tracking number
  3. All abstract numbers cite TRACK-A-FROZEN-NUMBERS.md verbatim
**Status**: numeric reconciliation done; remaining edit passes are Route A of
snappy-humming-pine.md
```

5. **## Pre-pivot spine (completed; artifacts reusable per Amendment §8)**:
   New section heading. **PASTE the entire existing ROADMAP.md body** from
   the start of `## Phases` through the end of `## Progress` VERBATIM as a
   sub-section here. Per-phase status markers (`[x]` and `[ ]`) stay as-is
   so that per-phase git-history traces remain interpretable. Add a single
   prefacing paragraph explaining that these phases executed 2026-02-XX →
   2026-04-14 under the original candidate-locus framing, closed as
   pre-specified methods-validation subset per Amendment §8, and that the
   Phase 0 reference data + Phase 1 SuSiE-RSS outputs + Phase 2 Stage 2
   real-LD coloc + Phase 5 partitioned heritability + Phase 9 replication
   scaffolding are reused as-is downstream (Track A primary data; Track B
   candidate-locus validation subset).

6. **## Progress (current milestone sequence)** (NEW small table at end):

```
| Milestone | Plans Complete | Status | Target end-month |
|---|---|---|---|
| M0 pivot scaffolding | 0/1 (this plan) | in flight | 2026-05 |
| M1 sumstats upgrade + harmonization | not planned | planning queued | 2026-06 / 2026-07 |
| M2 LDSC + MTAG + CPASSOC | not planned | gated on M1 + OSF amendment | 2026-08 / 2026-09 |
| M3 AoU AFR LD build | not planned | gated on M2 region list | 2026-09 / 2026-10 |
| M4 scalable coloc + fine-mapping | not planned | gated on M3 + M2 | 2026-12 / 2027-01 |
| M5 variant→gene prioritization + novelty | not planned | gated on M4 Tier A | 2027-02 |
| M6 manuscript + replication + submission | not planned | gated on M5 | 2027-04 / 2027-05 |
| Track-A-finalization | Route A in flight | in flight (independent of M0–M6) | 2026-05 / 2026-06 |
```

Wording rules (same as Task 1): original research / forward-looking / adopted.
Never revision / cleanup / fix / abandoned / obsolete / salvage.

After writing the file, commit it as a standalone atomic commit:
`git add .planning/ROADMAP.md`
`git commit -m "docs(roadmap): rewrite ROADMAP.md — M0–M6 Track B + Track A finalization per Amendment §3"`
  </action>
  <verify>
    <automated>test -f .planning/ROADMAP.md && grep -q "Pre-pivot spine" .planning/ROADMAP.md && grep -q "m0-pivot-scaffolding" .planning/ROADMAP.md && grep -q "m6-manuscript-and-replication" .planning/ROADMAP.md && grep -q "m3-aou-afr-ld-panel-build" .planning/ROADMAP.md && grep -q "Track-A-finalization\|track-a-finalization" .planning/ROADMAP.md && grep -q "Phase 0: Data access" .planning/ROADMAP.md && grep -q "Phase 9: Replication" .planning/ROADMAP.md && grep -q "Amendment §3\|Amendment §8" .planning/ROADMAP.md && ! grep -qiE "abandoned|obsolete|salvage" .planning/ROADMAP.md && git log -1 --pretty=%B -- .planning/ROADMAP.md | grep -q "M0–M6\|M0-M6"</automated>
  </verify>
  <done>
.planning/ROADMAP.md has (a) top header noting the 2026-04-22 pivot, (b)
Track B M0–M6 section with all seven slugs and per-milestone Goal /
Requirements / Dependencies / Success Criteria / Deliverables / Gating, (c)
Track A finalization row with sub-task checklist, (d) Pre-pivot spine section
archiving Phase 00–11 content verbatim (status markers preserved), (e)
current-sequence progress table. Committed as single atomic commit.
  </done>
</task>

<task type="auto">
  <name>Task 3: Rewrite .planning/REQUIREMENTS.md to 9-trait × 2-ancestry × joint-signal scope</name>
  <files>.planning/REQUIREMENTS.md</files>
  <action>
Rewrite .planning/REQUIREMENTS.md per Amendment §12 row 3. Re-derive from 9-
trait × 2-ancestry × joint-signal scope; preserve pre-pivot REQs that are
still load-bearing; add new REQs for MTAG / CPASSOC / HyPrColoc / PolyFun /
AoU-AFR-LD / Borzoi / 5 novelty classes / catalog cross-reference.

Structure of the new file (top-to-bottom):

1. **Header + preamble**:
```
# REQUIREMENTS.md

Testable acceptance criteria for the two-track original research program.
Track B milestone coverage maps via Amendment §3 M0–M6; Track A finalization
inherits the pre-pivot REQs that are still load-bearing. Each requirement
names its source (Amendment section or carried-forward pre-pivot origin),
a rule, and an acceptance test. Phase plans produced by `/gsd-plan-phase`
must reference the REQ IDs they satisfy.

Legend:
- **[B]** = Track B requirement (Amendment §3 milestone)
- **[A]** = Track A requirement (pre-pivot, carried forward)
- **[AB]** = Shared by both tracks
```

2. **Preserved pre-pivot REQs** (carry forward, tag with [A] / [AB] as
   appropriate). For each, retain the REQ ID if still meaningful (otherwise
   renumber to preserve monotonic ordering), and update the cross-references
   to point to milestone slugs instead of phase numbers.
   - **REQ-SNAKEMAKE-CI [AB]** — From pre-pivot REQ-9. Toy 3-locus CI smoke
     test; pinned conda envs; Singularity containers. Track B milestones all
     register their rules in the existing Snakemake skeleton.
   - **REQ-PUBLIC-DATA-ONLY [AB]** — Carter directive (CLAUDE.md): every
     GWAS / QTL / reference dataset must be publicly available or under
     standard academic DUAs. No wet-lab, no industry data, no proprietary.
     Enforces AoU controlled-tier pathway (summary-only export) as the
     AFR-LD provider.
   - **REQ-SUSIE-RSS-POLICY [A]** — From pre-pivot REQ-2. Explicit policy
     for convergence failures / L cap / min_abs_corr. `config/susie_policy.yaml`
     loaded by `src/snakemake/rules/finemap.smk`. Track A data depends on
     this; Track B inherits the policy when M4 SuSiE-RSS runs.
   - **REQ-NEGATIVE-CONTROLS [AB]** — From pre-pivot REQ-7. ≥3 negative-
     control gene/pathway sets (HLA, pigmentation, blood-group) must be null
     in coloc and enrichment outputs. Verified in Stage 2 (224 negative-
     control rows, all null per TRACK-A-FROZEN-NUMBERS.md §Negative-control).
   - **REQ-PATH-PARAMETERIZATION [AB]** — From pre-pivot REQ-12. All path
     references go through `config/pipeline.yaml`. No hardcoded absolute
     paths in `src/R`, `src/python`, `src/snakemake`, or `config/`.
   - **REQ-OSF-PREREG [AB]** — From pre-pivot REQ-11 (tier gating) re-scoped.
     Every Track B claim must be pre-registered on OSF before execution. The
     M2 MTAG/CPASSOC discovery phase is BLOCKED until the OSF amendment (per
     Amendment §9) is publicly posted to osf.io/pvb5j / osf.io/az52u.
   - **REQ-PP.H4-THRESHOLD-SWEEP [A]** — From pre-pivot REQ-3. Track A
     reports tier counts across PP.H4 ∈ {0.5, 0.7, 0.8, 0.9}. Track B M4
     reports region-level PP.H4 FDR correction instead (new REQ below).
   - **REQ-EQUITY-FRAMING [B]** — From pre-pivot REQ-8. Cross-ancestry
     claims framed as quantified trade-offs, not wins; AFR numbers reported
     at power-corrected detection probability. Carried into Track B M6
     manuscript.

3. **New Track B requirements** (drawn from Amendment §§3, 7):

   - **REQ-TRAIT-INVENTORY [B]** (Amendment §4) — Track B analyzes 9 traits
     × up to 2 ancestries per the locked §4 table: BMI, T2D, stroke, SBP,
     asthma, CAD, lipids (LDL primary; HDL/TG/TC secondary), eGFR, HbA1c.
     Ancestry coverage follows §4 column "Ancestry" (EUR primary for all
     nine; AFR for BMI/T2D/SBP/CAD/lipids/eGFR/HbA1c via GIGASTROKE AA and
     other ancestry-stratified subfiles). M1 verifies ancestry and sample-
     overlap flags per trait.
     **Acceptance**: `config/trait_inventory.yaml` enumerates 9 traits ×
     ancestry coverage per Amendment §4; harmonized sumstats exist for every
     (trait, ancestry) cell listed before M2 begins.

   - **REQ-MTAG-OVERLAP [B]** (Amendment §3 M2, §6, §10) — MTAG (Turley 2018)
     applied with `--overlap` using the LDSC pairwise intercept matrix for
     UKB / MVP cohort overlap correction. `max_FDR` filter per Turley 2018
     to control constant-covariance-assumption violation. mtCOJO (Zhu 2018)
     sensitivity check on top-N MTAG-novel loci where overlap is extreme.
     **Acceptance**: LDSC pairwise rg intercept matrix exists for all 9-trait
     ancestry-stratified pairs; MTAG output tables include `max_FDR` column;
     ≥1 mtCOJO sensitivity table exists for MTAG-novel loci.

   - **REQ-CPASSOC-ORTHOGONAL [B]** (Amendment §3 M2, §6) — CPASSOC (Zhu 2015)
     SHom / SHet statistics applied as orthogonal joint-signal test (does
     not assume constant covariance) for cross-method corroboration of MTAG
     novel loci.
     **Acceptance**: CPASSOC per-locus output tables exist; MTAG ∩ CPASSOC
     intersection is reported as the high-confidence Class 1 (joint-signal)
     novelty subset.

   - **REQ-TWO-STAGE-COLOC [B]** (Amendment §3 M4) — Two-stage coloc: fast
     ABF-coloc (Giambartolomei 2014) genome-wide first as triage filter;
     SuSiE-RSS (Wallace 2020; Zou 2022) only on regions with PP.H4 > 0.5.
     Region-level PP.H4 FDR correction on the combined table.
     **Acceptance**: pipeline produces per-region ABF PP.H4 column and
     SuSiE-RSS outputs restricted to PP.H4 > 0.5 regions; FDR-corrected
     region table exists.

   - **REQ-HYPRCOLOC-MULTI [B]** (Amendment §3 M4, §6) — HyPrColoc (Foley
     2021) applied for simultaneous colocalization across ≥3 traits, capped
     at 3–5 traits per block per §10 risk mitigation. Sensitivity check
     against pairwise coloc on all pairs within each HyPrColoc block.
     **Acceptance**: HyPrColoc output with `regional_prob ≥ 0.8` tables;
     pairwise-coloc sensitivity table for each ≥3-trait block.

   - **REQ-POLYFUN-RESCUE [B]** (Amendment §3 M4, §6) — PolyFun baselineLF2
     functional priors (Weissbrod 2020) applied to SuSiE credible sets for
     rescue of underpowered signals, especially in AFR where N is lower.
     **Acceptance**: rescued credible-set table labeled with PolyFun vs
     uniform-prior PIP; rescue count reported per ancestry.

   - **REQ-L2G-GENE-PRIORITIZATION [B]** (Amendment §3 M5, §6) — Open Targets
     Locus2Gene (Mountjoy 2021) secondary gene-prioritization axis
     independent of coloc/eQTL.
     **Acceptance**: per-Tier-A credible-set L2G top-3 gene column in the
     gene-prioritization table.

   - **REQ-BORZOI-VARIANT-EFFECT [B]** (Amendment §3 M5, §6; Linder 2024) —
     Borzoi variant-effect scoring applied to Tier A credible-set variants
     with per-tissue-track scores. Linder 2024 training-distribution
     caveats documented; Class 5 functional-mechanism novelty treated as
     supplementary context, not primary claim, per Amendment §7.3.
     **Acceptance**: Borzoi per-variant tissue-specific score column for
     every Tier A credible-set variant; methods-paragraph caveat present.

   - **REQ-NOVELTY-CLASS-1 [B]** (Amendment §7.1) — Joint-signal novelty
     via MTAG / CPASSOC. Operational definition: (MTAG p < 5e-8 OR CPASSOC
     p < 5e-8) AND max(single-trait p) ≥ 5e-8 AND no single-trait GWS hit
     within ±500 kb in GWAS Catalog v_lock. High-confidence subset =
     MTAG ∩ CPASSOC.
     **Acceptance**: `joint_signal_novel.tsv` exists with one row per
     claimed locus and columns for MTAG p, CPASSOC p, max single-trait p,
     nearest GWAS Catalog v_lock entry, confidence tier.

   - **REQ-NOVELTY-CLASS-2 [B]** (Amendment §7.1) — AFR-specific novelty.
     Operational definition: AFR PP.H4 ≥ 0.8 with |CS| ≤ 25 AND (no
     overlapping EUR coloc signal at the same locus, OR AFR lead variant has
     MAF_AFR ≥ 0.01 with MAF_EUR < 0.005).
     **Acceptance**: `afr_specific_novel.tsv` with AFR PP.H4, AFR CS size,
     EUR-overlap flag, MAF_AFR, MAF_EUR per claimed locus.

   - **REQ-NOVELTY-CLASS-3 [B]** (Amendment §7.1) — Secondary-independent
     credible-set novelty. Operational definition: SuSiE-RSS CS index ≥ 2
     AND CS purity ≥ 0.5 AND PIP_max(CS) ≥ 0.5 AND lead variant of CS
     index ≥ 2 not within ±100 kb of prior GWAS Catalog v_lock entry for
     the same trait.
     **Acceptance**: `secondary_signals.tsv` with region, CS index,
     purity, PIP_max, lead variant, nearest GWAS Catalog v_lock entry.
     Cross-panel LD-sensitivity parity check per Amendment §10 risk row.

   - **REQ-NOVELTY-CLASS-4 [B]** (Amendment §7.1) — Pleiotropy-class
     novelty. Operational definition: cross-trait PP.H4 ≥ 0.8 (pairwise) or
     HyPrColoc regional_prob ≥ 0.8 (≥3 traits) AND not present as cross-
     trait shared in {Pickrell 2016 supplement, Watanabe 2019 GWAS Atlas,
     Open Targets L2G top-3} as locked on M5 cross-reference date.
     **Acceptance**: `pleiotropy_novel.tsv` with trait-pair-locus rows,
     PP.H4 / regional_prob, Pickrell-2016 status, Watanabe-2019 status,
     L2G top-3 status.

   - **REQ-NOVELTY-CLASS-5 [B]** (Amendment §7.1, §7.3) — Functional-
     mechanism novelty (SUPPLEMENTARY, not primary claim). Operational
     definition: max-tissue Borzoi/Enformer score in top decile across the
     credible set AND no ClinVar pathogenic/likely-pathogenic entry AND
     no primary-literature functional characterization (PubMed search via
     mcp__claude_ai_PubMed).
     **Acceptance**: `functional_novel.tsv` reported as supplementary;
     methods paragraph explicitly labels Class 5 as supplementary.

   - **REQ-CATALOG-VERSION-LOCK [B]** (Amendment §7.2, §10) — All
     comparator catalog versions (GWAS Catalog, Pickrell 2016, Watanabe
     2019, Open Targets L2G, ClinVar) locked at the M5 cross-reference
     date with SHA-256 checksums and download URLs reported in the
     manuscript supplement. Delta-analysis between lock-date and
     submission-date catalogs if catalog drift occurs during review.
     **Acceptance**: `catalog_lock_manifest.tsv` exists with catalog name,
     version, download URL, SHA-256, lock-date.

   - **REQ-AOU-LD-EGRESS [B]** (Amendment §3 M3; AOU-LD-PIPELINE.md §§7,
     13) — Track B AFR LD reference is built inside the All-of-Us
     Researcher Workbench (Terra) from controlled-tier WGS (~100k AFR
     post-QC). Only summary-level artifacts (LD matrix + AF metadata)
     exported per AoU data-egress policy. No individual-level data leaves
     the Workbench. Zero cells computed from <20 participants (trivially
     satisfied at n≈60k AFR).
     **Acceptance**: AoU P&P draft registered before any Dataproc compute;
     RPS filed per AOU-LD-PIPELINE.md §2.1; export request categorized as
     aggregate summary statistics with written AoU classification
     (Amendment §10 risk R1). Per-region `.npz` LD files + AF metadata
     land on GPFS under `data/processed/ld_reference/AFR_aou/`;
     conversion to `.rds` per AOU-LD-PIPELINE.md §8.2.

   - **REQ-AOU-LD-VALIDATION [B]** (AOU-LD-PIPELINE.md §9) — Before any
     AoU-derived LD is admitted to production DAGs, the four-check
     validation protocol passes on a 10-region dev subset: (1) known-locus
     LD pattern matches published AFR figures; (2) AoU EUR vs 1000G EUR
     entry-wise r ≥ 0.97 for MAF ≥ 0.05; (3) SuSiE-RSS converges on
     16q12 BMI AFR with CS size ≤ 30 and lead PIP ≥ 0.1; (4) AoU-AFR vs
     identity-placeholder A/B documented for the 10 regions.
     **Acceptance**: `.planning/phases/m3-aou-afr-ld-panel-build/validation/`
     contains check outputs; validation memo committed before scale-up.

   - **REQ-REPLICATION-HOLDOUT [B]** (Amendment §3 M6) — Hold-out
     replication on FinnGen / Pan-UKBB / MVP release n+1 where available
     for Tier A claimed loci and novel-variant classes 1–4.
     **Acceptance**: per-class replication table with point estimate,
     95% CI, sign agreement, and post-hoc power per replication cohort.

4. **ID cross-reference table at bottom**: A small table mapping REQ IDs to
   the Track B milestone(s) they gate and the pre-pivot REQ (if carried
   forward). Example:

```
| REQ ID | Milestone(s) | Track | Prior-pivot origin |
|---|---|---|---|
| REQ-SNAKEMAKE-CI | M0, M1, M2, M3, M4, M5, M6, Track-A-finalization | AB | pre-pivot REQ-9 |
| REQ-MTAG-OVERLAP | M2 | B | new |
| REQ-AOU-LD-EGRESS | M3 | B | new |
| ... | ... | ... | ... |
```

Wording rules (same as Task 1): original research / forward-looking /
adopted / locked. Never revision / cleanup / fix the / correct the.

After writing the file, commit it as a standalone atomic commit:
`git add .planning/REQUIREMENTS.md`
`git commit -m "docs(requirements): rewrite REQUIREMENTS.md — 9-trait × 2-ancestry joint-signal scope + 5 novelty classes"`
  </action>
  <verify>
    <automated>test -f .planning/REQUIREMENTS.md && grep -q "REQ-TRAIT-INVENTORY\|REQ-NOVELTY-CLASS-1\|REQ-NOVELTY-CLASS-5" .planning/REQUIREMENTS.md && grep -q "REQ-AOU-LD-EGRESS" .planning/REQUIREMENTS.md && grep -q "REQ-MTAG-OVERLAP" .planning/REQUIREMENTS.md && grep -q "REQ-CPASSOC-ORTHOGONAL" .planning/REQUIREMENTS.md && grep -q "REQ-HYPRCOLOC-MULTI" .planning/REQUIREMENTS.md && grep -q "REQ-POLYFUN-RESCUE" .planning/REQUIREMENTS.md && grep -q "REQ-BORZOI-VARIANT-EFFECT" .planning/REQUIREMENTS.md && grep -q "REQ-TWO-STAGE-COLOC" .planning/REQUIREMENTS.md && grep -q "REQ-CATALOG-VERSION-LOCK" .planning/REQUIREMENTS.md && grep -q "REQ-SUSIE-RSS-POLICY" .planning/REQUIREMENTS.md && grep -q "REQ-PUBLIC-DATA-ONLY" .planning/REQUIREMENTS.md && grep -q "REQ-SNAKEMAKE-CI" .planning/REQUIREMENTS.md && grep -q "AOU-LD-PIPELINE" .planning/REQUIREMENTS.md && git log -1 --pretty=%B -- .planning/REQUIREMENTS.md | grep -q "joint-signal\|novelty"</automated>
  </verify>
  <done>
.planning/REQUIREMENTS.md covers all 5 novelty classes, both tracks, AoU
egress compliance, and preserves load-bearing pre-pivot REQs (Snakemake CI,
SuSiE-RSS policy, public-data-only, negative controls, path parameterization,
OSF pre-reg, equity framing). ID cross-reference table exists. Committed as
single atomic commit on main.
  </done>
</task>

<task type="auto">
  <name>Task 4: Append 5 new DEC entries to .planning/DECISIONS.md (append-only)</name>
  <files>.planning/DECISIONS.md</files>
  <action>
APPEND-ONLY operation. Do NOT modify any existing entries in .planning/
DECISIONS.md. Add 5 new entries at the end of the file, each in the same
format as the existing log (dated `## YYYY-MM-DD — <title>` with
Decision / Alternatives considered / Why / How to apply subsections),
dated 2026-04-22 or 2026-04-23, each cross-referencing Amendment sections
and, where applicable, TRACK-A-FROZEN-NUMBERS.md and AOU-LD-PIPELINE.md.

The 5 entries (use exactly these DEC IDs and topics — from task_boundary):

---

## 2026-04-22 — DEC-2026-04-22-01: Candidate-locus design abandoned (Amendment §2)

**Decision:** Abandon the 50-region candidate-locus design as the primary
discovery vehicle. Adopt genome-wide, hypothesis-agnostic region generation
(MTAG + CPASSOC + per-trait PLINK clumping union) as the Track B discovery
mode. The candidate-locus outputs survive as Track A's pre-specified methods
validation subset per Amendment §8.

**Alternatives considered:** (a) Keep candidate-locus as primary + expand
region windows; (b) Abandon entirely with no Track A salvage; (c) Pivot to
Track B + publish Track A as short-form methods paper (adopted).

**Why:** The candidate-locus design is circular by construction — regions
were chosen from prior literature that already reported cross-trait
signal, so the test is not discovering pleiotropy but estimating the
replication rate of prior claims under a new method (Amendment §2.1, §2.3).
Stage 2 real-LD production fire 2026-04-22 made the circularity
quantitative: SH2B3 × asthma EUR collapsed from identity-LD PP.H4 = 1.0 to
real-LD n_cs_a = 0 (TRACK-A-FROZEN-NUMBERS.md §Stage 2 trait-pair coloc.susie),
and 0 of 233 Tier assignments reached Tier A (§Tier assignments). Nature
Genetics calibre requires (a) genome-wide hypothesis-agnostic region
generation, (b) joint-signal discovery methods, (c) matched-ancestry real
LD, (d) multi-method triangulation, (e) non-EUR ancestry at non-footnote
power, (f) explicit comparator-catalog novelty claims (Amendment §2.1).
The candidate-locus design fails (a), (b), (e), (f).

**How to apply:** Track B M0–M6 execution follows Amendment §3. Track A
finalization ships the candidate-locus real-LD audit independently per
TRACK-A-PIVOT.md. The 205 analysis windows and 96 Stage 2 coloc cells are
reusable per Amendment §8 as (i) Track A's primary data and (ii) Track B's
candidate-locus validation appendix.

---

## 2026-04-22 — DEC-2026-04-22-02: 9-trait × up-to-2-ancestry inventory locked (Amendment §4)

**Decision:** Lock Track B trait inventory at 9 traits: BMI, T2D, stroke,
SBP, asthma, CAD, lipids (LDL primary; HDL/TG/TC secondary), eGFR, HbA1c.
Ancestry coverage follows Amendment §4 column "Ancestry" (EUR primary for
all nine; AFR via ancestry-stratified subfiles from DIAMANTE-AFR,
GIGASTROKE-AA, Giri 2019 MVP-AFR, GBMI-AFR, GLGC-AFR, CKDGen-AFR /
Morris 2019, MAGIC-AFR, PAGE / Loh 2022 BMI-AFR, Aragam 2022 CAD-AFR
where released). Phenotype definitions locked per §4 "Phenotype lock"
column (e.g., stroke = all-stroke, not ischemic-only; LDL-C continuous
primary; eGFR creatinine-based continuous).

**Alternatives considered:** (a) Keep 5 traits (BMI, T2D, SBP, stroke,
asthma) from pre-pivot; (b) Expand to 12 traits including three additional
cardiometabolic phenotypes (CRP, fasting glucose, fasting insulin); (c)
Lock at 9 per Amendment §4 (adopted).

**Why:** 5 traits underpowers MTAG / HyPrColoc joint-signal discovery
(Turley 2018 reported ~30–80 MTAG-novel loci per 4-trait run; more traits
in the correlated cardiometabolic block yield higher Class 1 novelty —
Amendment §7.3). 12 traits adds fasting-glucose / fasting-insulin overlap
with HbA1c and CAD-CRP correlations that inflate `--overlap` correction
burden without proportional discovery gain. 9 traits covers the shared
cardiometabolic architecture span (anthropometry → glycemic → blood
pressure → lipids → renal → inflammatory-respiratory-diabetes cross-talk
via asthma) while keeping the LDSC intercept matrix tractable (9 × 9 = 81
pairs vs 12 × 12 = 144 pairs).

**Decision pending** (open human-action item in PROJECT.md): BMI EUR
primary source is Loh 2022 (n ≈ 1.1M, GRCh38, GIANT+23andMe) vs Yengo 2022
GIANT+UKBB (n ≈ 700k, GRCh37). SUMSTATS-UPGRADE.tsv rows 2–3 list both;
Amendment §9.3 draft text cites Yengo 2022. To be locked at M1 kickoff
before LDSC munge.

**How to apply:** M1 sumstats harmonization per SUMSTATS-UPGRADE.tsv;
`config/trait_inventory.yaml` enumerates 9 traits × ancestry coverage;
REQUIREMENTS.md REQ-TRAIT-INVENTORY enforces.

---

## 2026-04-22 — DEC-2026-04-22-03: MTAG + CPASSOC joint-signal method stack adopted (Amendment §3 M2)

**Decision:** Adopt MTAG (Turley 2018, *Nature Genetics*) with `--overlap`
correction using LDSC pairwise intercept matrix as the primary joint-signal
discovery method. Adopt CPASSOC (Zhu 2015, *AJHG*) SHom / SHet statistics
as an orthogonal joint-signal test for cross-method corroboration. Retain
mtCOJO (Zhu 2018) as an overlap-correction sensitivity check for trait
pairs with extreme cohort overlap (e.g., UKB-heavy triples).

**Alternatives considered:** (a) S-MultiXcan (Barbeira 2019) —
interpretability constraints with shared eQTL tissues complicate cross-
ancestry application; (b) GFM / Generalized Factor Model — strong
parametric assumptions and less tested at genome-wide scale; (c) mtCOJO
alone as the primary discovery method — mtCOJO is overlap-correction-
focused rather than joint-signal-discovery focused; (d) MTAG alone —
fails to corroborate under `--overlap` mis-calibration (Amendment §10
risks); (e) MTAG + CPASSOC adopted as the joint-signal method stack with
mtCOJO as sensitivity check.

**Why:** MTAG's constant-covariance assumption is violated when trait-
pair cohort overlap inflates correlated noise; `--overlap` with LDSC
intercept matrix is the Turley-2018-recommended correction for UKB / MVP
dominance across the 9-trait block. CPASSOC's SHom / SHet do not assume
constant covariance and provide the orthogonal corroboration filter per
Amendment §7.1 Class 1 high-confidence definition (MTAG ∩ CPASSOC).
mtCOJO rounds out the robustness story on top-N MTAG-novel loci.
S-MultiXcan / GFM are rejected on interpretability and overlap-handling
grounds (Amendment §6 method-stack justification).

**How to apply:** M2 (m2-ldsc-mtag-cpassoc-discovery) executes: LDSC
pairwise rg → MTAG per-trait with `--overlap` → CPASSOC per-locus → PLINK
clump (p=5e-8, r²<0.01, 1Mb) → union region list. REQUIREMENTS.md
REQ-MTAG-OVERLAP + REQ-CPASSOC-ORTHOGONAL enforce.

---

## 2026-04-22 — DEC-2026-04-22-04: All-of-Us controlled-tier WGS as AFR LD source with egress-aware summary-only pipeline (Amendment §3 M3; AOU-LD-PIPELINE.md)

**Decision:** Adopt All-of-Us v7 controlled-tier WGS as the Track B AFR
LD reference panel. Build per-region LD matrices inside the AoU Researcher
Workbench (Terra) from ~60–95k AFR-ancestry participants (post-QC).
Export only summary-level artifacts (LD matrix + AF metadata) per AoU
data-egress policy. 1000G AFR (n = 661) is retained as a validation-only
fallback and as the comparator for AOU-LD-PIPELINE.md §9 Check 4
(AoU-AFR vs identity-placeholder A/B).

**Alternatives considered:** (a) 1000G AFR (n=661) as primary — Amendment
§2.2 and TRACK-A-FROZEN-NUMBERS.md (AFR regions remained on identity-
placeholder under Stage 2 for this reason) document that n=661 produces
LD SEs ~1/sqrt(n) ≈ 0.04 per off-diagonal, incompatible with SuSiE-RSS
fixed-LD assumption; (b) H3Africa (~3,500 continental African samples) —
same continental-vs-admixed mismatch as 1000G AFR, bigger N but wrong
population for MVP / AoU / PAGE targets; (c) PAGE (~50k admixed) — right
population, slower access, smaller than AoU; (d) AoU controlled-tier
(adopted) — ~150× 1000G AFR N, population-matched to a Track B target
cohort (AoU itself) and near-match for MVP-AFR / PAGE-AFR.

**Why:** n≈60k AFR WGS collapses LD SE to ~1/sqrt(60,000) ≈ 0.004, three
orders of magnitude below 1000G AFR and adequate for SuSiE-RSS credible-
set construction. Population match matters more than panel size in
admixed populations — 1000G AFR YRI/LWK/ESN/GWD/MSL/ACB/ASW does not
reflect MVP-AFR / AoU-AFR haplotype structure. AoU summary-only export
is AoU-data-egress-policy-compliant (AOU-LD-PIPELINE.md §7); the export
is aggregate summary statistics where every LD cell is computed from
all n participants (trivially ≥20 per-cell suppression floor). Using
AoU WGS for AFR LD is a methodological novelty axis in its own right
(Amendment §5); to our knowledge no published pleiotropy fine-mapping at
genome-wide scale has used it.

**Risks acknowledged** (AOU-LD-PIPELINE.md §12):
- R1 AoU export classification must be confirmed in writing before any
  Dataproc compute (Amendment §10 risk row).
- R3 compute cost: staged launch (10-region dev → 500-region priority
  batch → remaining) caps exposure.
- R10 critical-path risk: 10-region dev pipeline completes BEFORE M2
  region generation to de-risk M4 start.

**How to apply:** M3 (m3-aou-afr-ld-panel-build) executes per
AOU-LD-PIPELINE.md §§2–14. REQUIREMENTS.md REQ-AOU-LD-EGRESS +
REQ-AOU-LD-VALIDATION enforce. AoU P&P registered at draft stage before
any cluster spend. Local layout per AOU-LD-PIPELINE.md §8.1 under
`data/processed/ld_reference/AFR_aou/` (gitignored); `.rds` conversion
per §8.2.

---

## 2026-04-23 — DEC-2026-04-23-01: Two-track publication strategy adopted

**Decision:** Track A (short-form methods paper on real-LD audit of 50
curated cardiometabolic regions) and Track B (genome-wide 9-trait joint-
signal discovery + 5 novel-variant classes on upgraded sumstats) ship as
scientifically independent, co-primary outputs of the coloc_analysis
program. Track A targets Genome Medicine (primary), AJHG short report
(fallback 1), Bioinformatics Applications Note (fallback 2). Track B
targets Nature Genetics. Track A preprint (bioRxiv) establishes priority
on the real-LD-audit framing independently of the Track B discovery
timeline.

**Alternatives considered:** (a) Single Nature Genetics manuscript
combining the candidate-locus audit and the genome-wide discovery —
rejected because the two aims have incompatible scope claims (Amendment
§2 circularity argument); (b) Track A only (candidate-locus audit as
sole deliverable) — rejected because it would leave the pipeline
investment in M1 sumstats and the AoU-AFR LD methodological novelty
unpublished; (c) Track B only (genome-wide only) — rejected because it
discards the Stage 2 real-LD identity-LD-inflation finding (SH2B3 × asthma
EUR PP.H4 = 1.0 → n_cs_a = 0) which is itself a publishable methods
contribution (TRACK-A-FROZEN-NUMBERS.md §Usage); (d) Two-track (adopted).

**Why:** Track A quantifies how published candidate-locus pleiotropy
claims survive fully-pre-registered real-LD re-analysis — a forward-
looking, pre-specified methods validation contribution targeting
cardiometabolic genetics audiences at Genome Medicine / AJHG. Track B
pursues genome-wide hypothesis-agnostic joint-signal discovery across
9 traits × 2 ancestries with AoU-AFR LD — the Nature Genetics
contribution. Scheduling Track A preprint in 2026-05 / 2026-06 (per
Amendment §11) ahead of Track B M6 (2027-04 / 2027-05) establishes
priority on the real-LD-audit framing and positions Track A as "pre-
specified validation ahead of discovery" rather than a post-hoc carve-out
(Amendment §8).

**How to apply:**
- Track A finalization proceeds per TRACK-A-PIVOT.md and the ROADMAP
  "Track-A-finalization" sub-task checklist.
- Track B proceeds per Amendment §3 M0–M6 with the OSF amendment posted
  at end of M1 and before any M2 MTAG/CPASSOC run.
- Each manuscript has its own cover letter under
  `manuscript/cover_letter/` per REQ-10-equivalent carry-forward.
- Pre-pivot spine artifacts (Phases 0, 1, 2, 5, 9) serve both tracks per
  Amendment §8 preservation commitment.

---

After appending the 5 entries, commit the file as a standalone atomic
commit:
`git add .planning/DECISIONS.md`
`git commit -m "docs(decisions): append 5 DEC entries for candidate-locus abandonment + 9-trait locks + MTAG/CPASSOC + AoU-AFR LD + two-track strategy"`

Sanity check before commit: the only diff against pre-rewrite state is the
5 new entries appended at the end. No prior entry (2026-04-09 through
2026-04-21 distal-gene entries) is touched. Run `git diff --stat
.planning/DECISIONS.md` and verify insertion-only diff pattern.

Wording rules (same as Task 1): adopted / locked / chosen / selected.
Never reverse / correct / fix.
  </action>
  <verify>
    <automated>test -f .planning/DECISIONS.md && grep -c "DEC-2026-04-22-01\|DEC-2026-04-22-02\|DEC-2026-04-22-03\|DEC-2026-04-22-04\|DEC-2026-04-23-01" .planning/DECISIONS.md | awk '$1 == 5 { exit 0 } { exit 1 }' && grep -q "2026-04-22 — DEC-2026-04-22-01" .planning/DECISIONS.md && grep -q "2026-04-23 — DEC-2026-04-23-01" .planning/DECISIONS.md && grep -q "Candidate-locus design abandoned" .planning/DECISIONS.md && grep -q "MTAG + CPASSOC\|MTAG.*CPASSOC" .planning/DECISIONS.md && grep -q "All-of-Us controlled-tier\|AoU controlled-tier" .planning/DECISIONS.md && grep -q "Two-track publication" .planning/DECISIONS.md && grep -q "2026-04-09 — Repo scope" .planning/DECISIONS.md && grep -q "2026-04-21 — Phase 2 Recovery\|2026-04-21 — Pre-registration" .planning/DECISIONS.md && git log -1 --pretty=%B -- .planning/DECISIONS.md | grep -q "append 5 DEC"</automated>
  </verify>
  <done>
.planning/DECISIONS.md has exactly 5 new entries appended with the
specified DEC IDs and dates (DEC-2026-04-22-01 through -04, DEC-2026-04-23-01).
Prior entries from 2026-04-09 through 2026-04-21 (distal gene-scope entry)
remain untouched (verified by presence-check of earliest and latest prior
entries). Git diff is insertion-only at end of file. Committed as a single
atomic commit with the specified message. Four atomic commits total (one
per file) now on main, no push, no worktree.
  </done>
</task>

</tasks>

<verification>
## Overall phase checks (post all 4 commits)

1. Four atomic commits on main:
   ```
   git log --oneline -4 -- .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md .planning/DECISIONS.md
   ```
   Should show exactly four new commits with the four prescribed messages.

2. No push executed:
   ```
   git status   # working tree should be clean (except any untracked files from other steps)
   ```
   `HEAD` is ahead of `origin/main` by 4 commits.

3. No worktree:
   ```
   git worktree list   # should show exactly one worktree (the main repo)
   ```

4. All four files exist and are non-trivial:
   ```
   wc -l .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md .planning/DECISIONS.md
   ```
   Expected: PROJECT.md ~100–150 lines; ROADMAP.md ~350+ lines (pre-pivot archive expands it); REQUIREMENTS.md ~250+ lines; DECISIONS.md ~500+ lines (existing ~370 + ~130 appended).

5. Framing check across all four files:
   ```
   grep -iE "\bfix the\b|\bcorrect the\b|\brevision\b|\bcleanup\b|\babandoned\b|\bobsolete\b|\bsalvage\b" \
     .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md | head -5
   ```
   Expected: 0 matches. (Exception: DECISIONS.md DEC-2026-04-22-01 uses
   "abandoned" in the DEC title as the user-specified verbatim title, which
   is allowed per task_boundary.)

6. OSF submission NOT claimed:
   ```
   grep -iE "OSF amendment (posted|submitted|published)" .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md .planning/DECISIONS.md
   ```
   Expected: 0 matches claiming completion. The word "post" may appear in
   forward-looking context only ("will be posted", "must post before M2").

7. Amendment cross-references present in all four files:
   ```
   grep -c "Amendment" .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md .planning/DECISIONS.md
   ```
   Expected: each file has ≥3 Amendment references.

8. CLAUDE.md constraints subsection preserved verbatim in PROJECT.md:
   ```
   for c in "100% public data" "Solo author" "Timeline is not a binding" "No web/JS stack" "Data access lead times" "GPFS filesystem"; do
     grep -q "$c" .planning/PROJECT.md || echo "MISSING: $c"
   done
   ```
   Expected: no MISSING output.

9. `gsd-tools init resume` runs cleanly:
   ```
   node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" init resume 2>&1 | tail -40
   ```
   Expected: no incomplete-plan warnings about the M0 planning docs (ROADMAP
   still shows unplanned M1–M6; that's correct, they are queued for future
   `/gsd-plan-phase MN` sessions).
</verification>

<success_criteria>
- [ ] .planning/PROJECT.md rewritten to M0–M6 two-track framing; CLAUDE.md constraints preserved verbatim; three open human-action items flagged (OSF submission, BMI primary-source decision, MVP DUA); no prohibited "revision/cleanup/fix" language.
- [ ] .planning/ROADMAP.md archives Phase 00–11 under "Pre-pivot spine" (content verbatim, status markers preserved); adds seven M0–M6 entries using canonical slugs with per-milestone Goal / Requirements / Dependencies / Success Criteria / Deliverables / Gating; adds Track A finalization row.
- [ ] .planning/REQUIREMENTS.md re-derived for 9-trait × 2-ancestry × joint-signal scope; 5 novelty-class REQs present (REQ-NOVELTY-CLASS-1 through -5); AoU egress + validation REQs present; pre-pivot REQs preserved with carry-forward tagging; cross-reference table at bottom.
- [ ] .planning/DECISIONS.md appended with exactly 5 new entries (DEC-2026-04-22-01 through -04, DEC-2026-04-23-01); prior entries unchanged; diff is insertion-only at end.
- [ ] Four atomic commits on main with the prescribed messages; no push; no worktree; working tree clean post-commits.
- [ ] OSF amendment submission is surfaced as an open human-action item but NOT claimed as done.
- [ ] STATE.md not touched (belongs to snappy-humming-pine.md Step 3.2, a separate session).
</success_criteria>

<output>
After completion, no SUMMARY.md required (this is a `/gsd-quick` plan, not a
formal phase). The four commits on main are the deliverable. The Resume plan
at /home/ckclinto/.claude/plans/snappy-humming-pine.md Step 3 expects:
- Step 3.2 STATE.md refresh to follow in a separate session.
- Step 3.3 OSF amendment posting to follow in a separate (manual, Carter)
  session.
</output>
