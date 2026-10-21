# Phase ta-r4: Head-to-head re-analysis and submission — Context

**Gathered:** 2026-10-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Track A (`docs/manuscript/id-vs-ref-LD.md`) was never submitted. This phase:

1. regenerates the Track A analysis from a pinned, verified pipeline;
2. runs a pre-registered, matched, three-arm head-to-head that measures what LD
   handling does to cross-trait colocalization at the admissible curated regions;
3. fixes the E-2 allele-orientation defect and reports frozen-vs-fixed numbers;
4. writes a fresh, reviewer-ready manuscript from the results; and
5. prepares (but does not perform) the OSF posting and journal submission.

The result decides the headline. "Identity-LD inflates colocalization" is a
hypothesis under test here, not a conclusion to be supported.

Out of scope: Track B (M0–M6, AoU panel), genome-wide discovery, new traits,
new GWAS vintages (the audit stays at the vintages of the claims it audits).

</domain>

<decisions>
## Implementation Decisions

### Analysis arms (Carter, 2026-10-21)
- **D-01:** Three arms on identical sumstats, regions, priors and SuSiE policy:
  **A1** `coloc.abf` (single causal variant, uses no LD matrix — the method most
  published claims used); **A2** SuSiE-RSS + `coloc.susie` with R = I (identity);
  **A3** SuSiE-RSS + `coloc.susie` with real 1000G Phase 3 EUR LD.
  A1 vs A3 = "literature method vs best practice"; A2 vs A3 = the pure LD-matrix
  effect. The manuscript must stop conflating `coloc.abf` with "identity LD".

### Zero-credible-set rule (Carter)
- **D-02:** When either trait has 0 credible sets under an arm, the pre-specified
  fallback is `coloc.abf` on the same region, reported as a **separately labelled
  outcome** (`fallback_abf`). The per-arm no-CS rate is itself a reported result.
  Fallback and `coloc.susie` values are never pooled silently.

### LD panels (Carter)
- **D-03:** Primary real-LD panel = 1000G Phase 3 EUR (n≈503). Sensitivity arm
  **A3-UKB** = public Pan-UKBB / UKB LD matrices (most GWAS here are UKB-derived),
  testing reference mismatch directly.
- **D-04:** The UKB sensitivity panel is built under a **separate path** that the
  EUR `ld_panel` chain cannot resolve to (m3-04c BLOCKER-B: `EUR_ukbb_pub` is the
  EUR chain head and would silently replace the primary panel).

### Pre-registration (Carter)
- **D-05:** The R4 analysis plan (arms, estimands, decision rules, outcome
  branches, known-answer controls) is drafted as an OSF amendment and **posted by
  Carter on osf.io/az52u before any production fit runs**. Infrastructure,
  data re-acquisition and known-answer reproduction may run before posting;
  the A1/A2/A3 production comparison may not.

### E-2 allele orientation (Carter — reverses option A of DEC-2026-08-07)
- **D-06:** Fix, then report before/after. Make the EUR sumstats-to-panel join
  allele-aware and apply the computed orientation to QTL betas in QTL-coloc,
  TDD (failing test first). All R4 arms run on fixed code. Report frozen
  (pre-fix) vs fixed numbers side by side. Option A's premise ("Track A is in
  submission") is recorded as false. Needs a new DEC entry superseding
  DEC-2026-08-07 option A for Track A.

### Scope (Carter)
- **D-07:** Exhaustive: every admissible EUR region × all 10 trait pairs of the
  5 traits, plus the QTL-coloc layer. AFR is a clearly secondary arm on 1000G AFR
  (Track A's original substrate, not the AoU panel).

### Manuscript (Carter)
- **D-08:** Fresh ~4–5k-word draft written from R4 results; the existing draft is
  source material only. Process provenance (commits, DEC ids, `.planning` paths)
  moves to a Supplementary reproducibility note. Brief-blind adversarial review
  before Carter sees a submission candidate.
- **D-09:** Venue decided **after** results. The 2026-08-12 Nature-first ladder
  stays on record but is not acted on. Draft in a neutral format meanwhile.
  No preprint (DEC-2026-08-12-no-preprint stands).

### Locked by the orchestrator under the standing rigor-over-speed rule
(found by the 2026-10-21 inventory; Carter may override)
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

### Post-research decisions (2026-10-21, after `ta-r4-RESEARCH.md`)
Carter (AskUserQuestion):
- **D-17 (corrects D-12(b)):** the SH2B3 known answer is the EXACT R2 configuration —
  L=15 @ max_iter 500/1000 fits for BMI/HTN/stroke + Stage-2 L=10 fits for asthma/T2D
  (`ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md:153-156`, verified). The standard
  L=10/iter-100 SH2B3 run is reported as a separate measurement. The manuscript states the
  true provenance of the 1.0.
- **D-18:** BMI REF/ALT restored from the same Yengo 2018 release already on disk, by a
  checksum-pinned script with a match-rate report; disclosed in the OSF amendment and Methods.
- **D-19:** `osf-correction-v2` is retired UNPOSTED; the R4 pre-registration amendment carries
  the E-2 finding and fix as one public record. The manuscript's Methods correction note is
  rewritten to match. (Supersedes the P-1 posting obligation of DEC-2026-08-12; needs a DEC entry.)
- **D-20:** AFR secondary arm pre-registers 1000G AFR n=661 (incl. ASW/ACB); 504 continental
  as sensitivity.

Orchestrator-locked (rigor rule; Carter may override):
- **D-21:** A1 primary on the matched (A3-bound) variant set; "all region sumstats variants"
  (literature practice) as a secondary A1 row.
- **D-22:** QTL layer runs under A2 and A3 (identity effect on GWAS×QTL coloc is measured).
- **D-23:** Simulation calibration arm (E8, known truth) is a pre-registered secondary — the
  research shows null loci fall back to identical LD-free results in every arm, so negative
  controls cannot separate arms.
- **D-24:** HLA_6p21 and BMI_Xq24: not admissible (no panel), reported as such; HLA on UKB
  tiles optional exploratory row only.
- **D-25:** Measured-not-assumed facts (EUR panel n from the `.fam`, hypertension trait type
  and sdY per trait for coloc.abf) are measured in execution, recorded in the panel/trait
  manifests, and fixed in the amendment before posting.
- **D-26:** Estimands E1–E8 and the five outcome branches in RESEARCH §Estimands are the draft
  pre-registration; κ and n_both cut-offs are locked in the amendment (Carter).
- **D-27:** OSF gate is a sentinel file Carter commits after posting (GSD `mode: yolo`
  auto-picks the first option at blocking gates — memory
  `feedback_gsd_automode_bypasses_blocking_fire_gates`); production rules refuse to run without it.
- **D-28:** No edit to code-frozen `run_susie_rss.R` (pinned by `test_source_freeze_pins`);
  R4 behaviour comes from overlays + receipts/validators per RESEARCH §Architecture.

### Claude's Discretion
- Wave structure, Snakemake overlay design, how Pan-UKBB LD is fetched/sliced,
  estimand formulas (e.g. paired ΔPP.H4 per pair, agreement at 0.8/0.5,
  calibration on negative-control loci), figure design.
- Compute placement (LSF queues per `feedback_lsf_queues`).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Manuscript and frozen record
- `docs/manuscript/id-vs-ref-LD.md` — current draft (source material only, D-08)
- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — frozen numbers; comparison target
- `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` — known-answer target (D-12)
- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` — md5 history
- `results/track_a_aggregations/` — tracked aggregates; `results/multitrait/coloc_susie_R2*/` — tracked R2 JSONs
- `targeted_rerun_outputs/hpc_inventory.tsv` — 2026-05-07 record of what existed

### Decisions
- `.planning/DECISIONS.md` — DEC-2026-08-07-e2-orientation-disposition (superseded for Track A by D-06), DEC-2026-08-11-e2-framing-correction, DEC-2026-08-12-* (venue, P-1, placement, no-preprint), DEC-2026-04-25-01
- `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md` — 28/28 empty = n_cs 0 on ≥1 side
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-BLAST-RADIUS.md` — BLOCKER-B (EUR un-pinning), E (mixed LD panels in QTL-coloc)
- `.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-SELECTED-PAIR-correction-v2.md` — E-2 correction pair (to be revised after D-06)
- `.planning/osf_prereg_draft.md`, `.planning/osf_deviations.md` — OSF record conventions

### Pipeline
- `Snakefile`, `src/snakemake/rules/{finemap,coloc,multitrait,qtl_coloc,ld_reference}.smk`
- `src/snakemake/scripts/{run_susie_rss.R,run_coloc_susie.R,run_qtl_coloc.R,ld_allele_join.R,make_identity_ld_refs.R}`
- `config/pipeline.yaml`, `config/susie_policy.yaml`, `config/pipeline_identity_overlay.yaml`, `config/qtl_sources.yaml`, `config/regions_curated.csv`
- `envs/r_coloc.yml` (R 4.4.2, susieR 0.14.2, coloc 5.2.3)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ld_allele_join_indices()` (`ld_allele_join.R`): the 4-key allele-aware join with
  palindrome drop — already used for AFR; the E-2 fix extends it to EUR.
- `make_identity_ld_refs.R` + `pipeline_identity_overlay.yaml`: identity arm (needs D-14 fix).
- `bin/fire_canonical_susie_pairs.sh`, `bin/fire_phase2_stage2_refit.sh`: prior fire patterns.
- `psd_utils.R` (canonical PSD conditioning), `source_freeze` code pins.

### Established Patterns
- Outcome branches pre-registered before fires; RED-first tests; negative controls
  observed failing; sha256/md5 manifests; append-only DEC entries.
- Snakemake via `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Python 3.11).

### Integration Points / hazards
- `run_susie_rss.R:1114` silent `diag(n)` fallback (D-13).
- EUR declared-input chain vs read path differ (`ld_panel.EUR` chain vs `{ld_reference_dir}/EUR`).
- `02c4404` changed effective max_iter for retries (D-12).
- `envs/qtl_processing.yml` deleted by `c2dfb08` but referenced by 5 rules (D-14).

</code_context>

<specifics>
## Specific Ideas

- Carter: "definitely run the re-analysis. Rigor over speed." "log everything,
  update Git and anything else that needs to be done."
- Running log for every action: `ta-r4-LOG.md` in this phase directory.
- Framing rules: original research; never "pivot", "revision", "salvage",
  "audit-driven fix" in public artifacts (`feedback_original_research_framing`,
  `project_track_a_handle`).

</specifics>

<deferred>
## Deferred Ideas

- AoU-AFR-LD re-analysis of Track A regions — belongs to Track B once its panel exists.
- Newer GWAS vintages (DIAMANTE 2022, GBMI, Yengo 2022) — Track B companion study.

</deferred>

---

*Phase: ta-r4-head-to-head-reanalysis-and-submission*
*Context gathered: 2026-10-21*
