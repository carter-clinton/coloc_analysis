# REQUIREMENTS.md

Each requirement below maps to a specific gap in
[`GSD_BRIEFING.md`](../GSD_BRIEFING.md) §5.2 or a core methodological change
from [`Revision_Plan.md`](../Revision_Plan.md). They are the concrete,
testable acceptance criteria the revision must meet before the manuscript
can go out. Phase plans produced by `/gsd-plan-phase` must reference the
REQ IDs they satisfy.

---

## REQ-1 — Data access runs in parallel from Day 1

**Source:** `GSD_BRIEFING.md` §5.2 gap #1.

**Rule:** DUAs for UK Biobank (main + UKB-PPP), deCODE pQTL, FinnGen, MVP,
All of Us, BBJ, and Pan-UKBB must be submitted on the **first working day**
of Phase 0, not deferred to a later phase. The phase plan treats DUAs as
**long-running parallel work**, not as a gate.

**Acceptance:** every DUA application has a row in `.planning/data_access.md`
with `date_submitted`, `expected_lead_time`, `tracking_id`, `status`, and
`contact`. At least 6 of 7 applications are `submitted` before any Phase 1
rule is run.

---

## REQ-2 — SuSiE complex-region handling is explicit

**Source:** `GSD_BRIEFING.md` §5.2 gap #2, `Revision_Plan.md` Phase 1.

**Rule:** SuSiE default `L=10` gives up to 100 credible-set pair comparisons
per region. Phase 1 must ship an explicit policy for: (a) convergence
failures, (b) regions that hit the `L` cap, (c) `min_abs_corr` sensitivity,
(d) how to downweight or collapse coincident credible sets.

**Acceptance:** `config/susie_policy.yaml` exists, is loaded by
`src/snakemake/rules/finemap.smk`, and is referenced in the methods
section of the manuscript. A sensitivity sweep on `min_abs_corr` (at least
3 values) is reported for complex regions as a supplementary table.

---

## REQ-3 — PP.H4 threshold sweep (not hardcoded ≥ 0.8)

**Source:** `GSD_BRIEFING.md` §5.2 gap #3, `Revision_Plan.md` Phase 2.

**Rule:** Tier A / B / C assignment must **not** hardcode PP.H4 ≥ 0.8. Phase
2 must report tier counts as a function of PP.H4 threshold across at least
4 values: `{0.5, 0.7, 0.8, 0.9}`.

**Acceptance:** `config/pph4_thresholds.yaml` exists; `src/snakemake/rules/`
generates a tier-by-threshold matrix per ancestry; the supplementary tables
include a sensitivity figure showing tier counts at each threshold.

---

## REQ-4 — MR weak-instrument mitigation for AFR / EAS

**Source:** `GSD_BRIEFING.md` §5.2 gap #4, `Revision_Plan.md` Phase 3.

**Rule:** AFR and EAS instrument sets are small and inflate MR bias. Phase
3 must implement at least two of: MR-RAPS, IVW-with-correction, trans-
ancestry MR per Lyon et al. 2023, and must make an explicit **ancestry
-specific vs. trans-ancestry instrument** choice per trait pair — not
default to either.

**Acceptance:** `src/snakemake/rules/mr.smk` runs MR-RAPS on AFR and EAS.
A weak-instrument diagnostic table (F-statistic, I-squared, Q-statistic)
is produced per ancestry per trait pair and included in supplementary tables.

---

## REQ-5 — Polygenic selection has a pre-specified fallback framing

**Source:** `GSD_BRIEFING.md` §5.2 gap #5, `Revision_Plan.md` Phase 6.

**Rule:** Phase 6 (polygenic selection) is the highest scientific-risk phase.
A null polygenic selection result must **not** invalidate the single-locus
selection signatures (iHS, PBS, SDS). The phase plan must pre-specify the
fallback framing **before running anything**.

**Acceptance:** the Phase 6 `PLAN.md` contains a "fallback framing" section
that reframes the evolutionary-medicine story in terms of locus-level signals
if the polygenic test is null. This section exists before the first
`/gsd-execute-phase 6` run. T3 is a gated decision anyway — this REQ only
activates if T3 lights up.

---

## REQ-6 — PRS evaluation includes calibration and clinical utility

**Source:** `GSD_BRIEFING.md` §5.2 gap #6, `Revision_Plan.md` Phase 8.

**Rule:** PRS evaluation must cover three dimensions, not just discrimination:

1. **Discrimination:** R², AUC, incremental C-statistic.
2. **Calibration:** Hosmer-Lemeshow test, calibration slope, calibration
   intercept, observed-vs-expected plot.
3. **Clinical utility:** NRI (net reclassification improvement),
   decision-curve analysis (DCA), net benefit vs. status quo.

**Acceptance:** `src/snakemake/rules/pgs.smk` produces all three metric
families in a single report per ancestry. Supplementary tables include
calibration plots and DCA curves. The discussion quantifies the equity-vs-
accuracy trade-off (REQ-8) using these metrics.

---

## REQ-7 — Negative-control genes and pathways

**Source:** `GSD_BRIEFING.md` §5.2 gap #7.

**Rule:** At least three negative-control gene / pathway sets must be tested
in Phase 2 (coloc) and Phase 5 (pathway enrichment) and must **not** show
spurious colocalization or enrichment. Standard choices: HLA (immune),
pigmentation genes (e.g. `OCA2`, `SLC24A5`, `MC1R`), eye-color genes.

**Acceptance:** `config/negative_controls.yaml` exists with at least three
gene sets and their matching pathway sets. Phase 2 output includes a
negative-control row in the colocalization tier table. Phase 5 output
includes a negative-control row in every enrichment table. All three sets
are null (PP.H4 < threshold, enrichment q > 0.05) in the final report.

---

## REQ-8 — Equity framed as quantified trade-off, not a win

**Source:** `GSD_BRIEFING.md` §5.2 gap #8, `Revision_Plan.md` §2 / §3.9.

**Rule:** The manuscript must not claim "equitable polygenic risk prediction"
as a win. Pathway-restricted PRS may *trade* accuracy for equity, and the
abstract, introduction, and discussion must reconcile this consistently.
The finding is framed as a **quantified equity-vs-accuracy trade-off** with
explicit numbers from REQ-6.

**Acceptance:** `docs/methods/equity_framing.md` exists and is referenced
from all three sections (abstract, intro, discussion) of the manuscript
draft. The discussion cites explicit numbers for AFR / EAS / Hispanic vs.
EUR on both accuracy metrics (R², AUC) and calibration metrics.

---

## REQ-9 — Snakemake pipeline has a CI smoke test

**Source:** `GSD_BRIEFING.md` §5.2 gap #9, `Revision_Plan.md` §7.

**Rule:** The Snakemake pipeline must run end-to-end on a toy 3-locus subset
**nightly** (or on every merge to `main`). Environments must be pinned via
`envs/*.yml` files, not ad-hoc conda installs. Containers (Docker +
Singularity) must be built and published.

**Acceptance:** `tests/toy_3locus/` exists with toy sumstats and a minimal
config override. `snakemake --snakefile tests/toy_3locus/Snakefile.test
--cores 2 --use-conda` completes in under 15 minutes. A GitHub Actions
workflow (or a cron-scheduled LSF job if no GitHub mirror yet) runs it on
schedule and records pass/fail in `.planning/ci_status.md`.

---

## REQ-10 — Nature Metabolism is in the target journal list

**Source:** `GSD_BRIEFING.md` §5.2 gap #10.

**Rule:** The manuscript's target journal list must include Nature
Metabolism between AJHG and Nature Genetics. Cover letters and response-
to-reviewers templates must be versioned per target journal.

**Acceptance:** `.planning/DECISIONS.md` lists the target journals as
`Nat Genet → AJHG → Nat Metab → Cell Genomics → Genome Medicine` (already
decided). `manuscript/cover_letter/` has one file per target journal.

---

## REQ-11 — Scope is tiered and gated

**Source:** `GSD_BRIEFING.md` §5.2 gap #11 + §5.3.

**Rule:** Phases are assigned to tiers T1 / T2 / T3. T1 is must-ship. T2
is conditional on Checkpoint #1 after T1 completes. T3 is conditional on
Checkpoint #2 after T2 completes. No phase is allowed to be treated as
"maybe we'll also do this" — each phase is either in the current tier or
explicitly deferred to a later checkpoint.

**Acceptance:** `.planning/ROADMAP.md` explicitly tags every phase with
T1 / T2 / T3. Checkpoints #1 and #2 produce written go/no-go decisions at
`.planning/checkpoints/T1_review.md` and `.planning/checkpoints/T2_review.md`
before the next tier is planned or executed.

---

## REQ-12 — Legacy path references are parameterized

**Source:** Discovered during Plan A recovery (2026-04-09). See
`src/legacy/README.md` "Known issues".

**Rule:** The recovered legacy code has 174 hardcoded absolute path
references: 100 to `/share/.../admix_map/`, 35 to the nonexistent
`/share/.../admixmap/` (source of the broken symlinks in the old shadow
dirs), 23 to `/gpfs_common/...`, and 16 to `/rs1/...`. These must all be
replaced with references to a single `config/pipeline.yaml` entry
(`data_root`, `legacy_root`, `result_root`) before any legacy script or
Snakemake rule is re-run.

**Acceptance:** `grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config`
returns 0 matches. Snakemake runs end-to-end on the toy-3-locus dataset
(REQ-9) with only `config/pipeline.yaml` values resolved.
