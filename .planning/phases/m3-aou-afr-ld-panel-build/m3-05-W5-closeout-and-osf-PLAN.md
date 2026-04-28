---
phase: m3-aou-afr-ld-panel-build
plan: 05
type: execute
wave: 5
depends_on: ["00", "02", "04"]
files_modified:
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md
  - .planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv
  - .planning/amendments/sha256_manifest_m3_frozen.tsv
  - .planning/amendments/aou-egress-audit-log.md
  - .planning/m2_post_m3_rerun_queue.tsv
  - .planning/ROADMAP.md
  - .planning/STATE.md
  - tests/toy_3locus/data/ld_ref/FTO_16q12.AFR.rds
  - tests/toy_3locus/data/ld_ref/SH2B3_12q24.AFR.rds
  - tests/toy_3locus/data/ld_ref/TCF7L2_10q25.AFR.rds
  - tests/toy_3locus/Snakefile.test
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "m3-VALIDATION-MEMO.md (Wave 2 deliverable) is finalized with a Wave 4 production-scale validation addendum (incorporating production_check_4_sample.tsv outcome from Wave 4)."
    - "m3-VALIDATION-MEMO.pdf is generated from the finalized markdown (paste-ready for OSF posting; Carter manually uploads to osf.io/az52u as a supplementary file per D-M3-08)."
    - "sha256_manifest_m3_frozen.tsv lands at .planning/amendments/ as a single 322-row monolith complementing the 44 per-bundle sub-manifests under .planning/amendments/sha256/ (Wave 4 deliverable)."
    - "aou-egress-audit-log.md is finalized: HARD GATE row complete (Wave 1) + 44 per-bundle rows complete (Wave 4) + a Wave 5 close-out summary table at the bottom."
    - ".planning/m2_post_m3_rerun_queue.tsv is updated: status note 'M3 complete YYYY-MM-DD; M2-supplementary phase eligible to start' added to all 8 obligations (NO obligations marked closed — closure happens in the M2-supplementary phase per D-M3-05)."
    - ".planning/ROADMAP.md gains a new M2-supplementary phase entry (slug: m2-supp-aou-afr-rerun) as M3 successor; populated with goal + requirements + dependencies + the 8 carry-forward obligations."
    - ".planning/STATE.md is updated: stopped_at, last_activity, milestone progress, percent."
    - "tests/toy_3locus/data/ld_ref/{FTO_16q12,SH2B3_12q24,TCF7L2_10q25}.AFR.rds identity-placeholder fixtures land (REQ-SNAKEMAKE-CI extension; AFR side-by-side with the existing EUR identity placeholders)."
    - "tests/toy_3locus/Snakefile.test is extended to exercise the resolver fallback chain end-to-end (verifies AFR_aou lookup falls through to identity-placeholder when AoU file absent in CI)."
    - "m3-PHASE-CLOSEOUT.md emits with REQ-coverage table, success-criteria table, deliverable hash table, and links to all governance artifacts."
  artifacts:
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md"
      provides: "Final validation memo with Wave 4 production addendum"
      min_lines: 150
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf"
      provides: "Paste-ready PDF for osf.io/az52u supplementary file upload (D-M3-08)"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md"
      provides: "Phase closure verifier: REQ coverage + success criteria + deliverable hashes + downstream-phase eligibility"
      min_lines: 80
    - path: ".planning/amendments/sha256_manifest_m3_frozen.tsv"
      provides: "Single 322-row monolith of all production .rds SHA-256 hashes"
    - path: ".planning/m2_post_m3_rerun_queue.tsv"
      provides: "Status-note update on all 8 M2-supersede obligations"
    - path: ".planning/ROADMAP.md"
      provides: "M2-supplementary phase entry added (slug: m2-supp-aou-afr-rerun) as M3 successor"
    - path: ".planning/STATE.md"
      provides: "Stopped_at + last_activity + milestone progress reflect M3-complete"
    - path: "tests/toy_3locus/data/ld_ref/*.AFR.rds"
      provides: "3 AFR identity-placeholder fixtures (REQ-SNAKEMAKE-CI)"
    - path: "tests/toy_3locus/Snakefile.test"
      provides: "Extended toy 3-locus pipeline test exercising resolver fallback chain"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv"
      provides: "Cohort summary mirrored from AoU workspace AOU-1 output (Wave 1) — captures final N for the validation memo"
  key_links:
    - from: "m3-VALIDATION-MEMO.pdf"
      to: "osf.io/az52u"
      via: "Carter manual OSF supplementary file upload (same form as M1 osf.io/az52u/files/k8w7n)"
      pattern: "osf\\.io/az52u"
    - from: ".planning/m2_post_m3_rerun_queue.tsv"
      to: ".planning/ROADMAP.md"
      via: "M2-supplementary phase entry references all 8 obligations"
      pattern: "m2-supp-aou-afr-rerun"
    - from: "tests/toy_3locus/Snakefile.test"
      to: "src/python/ld_panel.py::resolve_ld_path"
      via: "CI smoke-test exercises resolver chain (AFR_aou → identity-placeholder fallback)"
      pattern: "resolve_ld_path"
    - from: "sha256_manifest_m3_frozen.tsv"
      to: ".planning/amendments/sha256/m3_chr*.tsv"
      via: "Single monolith aggregates the 44 per-bundle sub-manifests"
      pattern: "sha256/m3_chr"
---

<objective>
Wave 5 closes M3 with all governance artifacts: validation memo finalization (incorporating production-scale Check 4 sample addendum), PDF generation for OSF posting (D-M3-08), monolith SHA-256 freeze, audit log finalization, M2-supersede queue status update, ROADMAP M2-supplementary phase entry, STATE.md update, toy 3-locus AFR identity-placeholder fixtures (REQ-SNAKEMAKE-CI), and the phase close-out verifier document.

Purpose: Lock the phase boundary. Make the M3 outputs auditable for OSF posting + manuscript supplementary deposit. Hand off cleanly to M2-supplementary phase + M4 with the M2-POST-M3-* obligations explicitly carried forward (NOT closed — D-M3-05).

Output: 11 governance artifacts + 4 toy-3-locus extensions, all committed and unit-test-verified for the resolver chain.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/m2_post_m3_rerun_queue.tsv
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md
@.planning/amendments/aou-egress-audit-log.md
@.planning/amendments/AOU-LD-PIPELINE.md

<interfaces>
<!-- Wave 0-4 deliverables Wave 5 finalizes. -->

m3-VALIDATION-MEMO.md (Wave 2 deliverable) — 9 sections + Carter signoff at end of Wave 2.
m3_validation_complete.flag (Wave 4) — production-scale Check 4 sample passed.
.planning/amendments/sha256/m3_chr*.tsv (Wave 4) — 44 per-bundle SHA-256 sub-manifests.
.planning/amendments/aou-egress-audit-log.md (Waves 0-4) — HARD GATE row + 44 per-bundle rows.
.planning/m2_post_m3_rerun_queue.tsv (M2 deliverable) — 8 obligations: M2-POST-M3-01 through -08.

D-M3-08 OSF posting form (RESEARCH §): paste-ready PDF; Carter uploads to osf.io/az52u as supplementary file (same convention as M1's osf.io/az52u/files/k8w7n).

D-M3-05 M2-supplementary phase setup: ROADMAP slug `m2-supp-aou-afr-rerun`; consumes M3 outputs (AFR_aou + EUR_aou .rds files); CONTEXT drafted via /gsd-discuss-phase post-M3 close.

REQ-SNAKEMAKE-CI extension (Wave 5): toy_3locus needs *.AFR.rds identity-placeholder fixtures so the resolver chain test fires AFR_aou (missing in CI; falls through) → AFR_hgdp_1kg (missing) → AFR_1kg (missing) → identity-placeholder (the AFR.rds files this wave creates).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Validation memo Wave 4 addendum + PDF generation + monolith SHA-256 freeze + audit log close-out summary</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md, .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf, .planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv, .planning/amendments/sha256_manifest_m3_frozen.tsv, .planning/amendments/aou-egress-audit-log.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md (Wave 2 first draft; 9 sections)
    - .planning/phases/m3-aou-afr-ld-panel-build/validation/production_check_4_sample.tsv (Wave 4 production-scale sample output)
    - .planning/amendments/sha256/m3_chr*.tsv (Wave 4; 44 per-bundle sub-manifests; aggregate into monolith)
    - .planning/amendments/aou-egress-audit-log.md (Waves 0-4 incremental; finalize close-out summary at bottom)
    - .planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv ←— Wave 1 AOU-1 output mirrored from AoU workspace
  </read_first>
  <action>
    1. Add a Section 10 "Production-scale validation addendum" to `.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md`. Pull Wave 4's `production_check_4_sample.tsv` (30-region sample yield contrast) into a Markdown table. Compare to Wave 2's dev-10 yield contrast (Section 5). State whether the production-scale yield contrast direction is consistent with dev (expected: yes); if not, halt + diagnose.

    2. Add Section 11 "Cluster-hours + AoU credits actually consumed" with: cluster-hours used (Wave 4 SUMMARY input), credit balance before/after, per-bundle wall-clock time mean/median/max, Path A.1/A.2/A.3 region count per ancestry.

    3. Add Section 12 "Per-cohort N (final)" — pull from `cohort_summary_m3.tsv` (Wave 1 AOU-1 output). Mirror cohort_summary_m3.tsv from AoU workspace (Carter `gsutil cp` post-Wave-1) into `.planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv` if not already present.

    4. Add Section 13 "References to OSF posting" — paste DOI+URL of osf.io/az52u + the (forthcoming) supplementary file URL for the validation memo PDF.

    5. Generate `m3-VALIDATION-MEMO.pdf` from the markdown via pandoc:
       ```bash
       pandoc .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md \
         -o .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf \
         --pdf-engine=xelatex \
         --toc --toc-depth=2 \
         -V geometry:margin=1in \
         -V documentclass=article
       ```
       (If pandoc/xelatex unavailable, fall back to weasyprint or fpdf via Python; the PDF must include all 13 sections.)

    6. Aggregate the 44 per-bundle SHA-256 sub-manifests into a single monolith `.planning/amendments/sha256_manifest_m3_frozen.tsv`:
       ```bash
       echo -e "ancestry\tchr\tregion_id\trds_sha256\tnpz_sha256\tbundle_id\tbm_sharded_sha256_or_NA" > .planning/amendments/sha256_manifest_m3_frozen.tsv
       # for each row in 44 sub-manifests: add ancestry/chr/region_id/sha + compute .rds sha256 from data/processed/ld_reference/{ancestry}/{region_id}.rds
       cat .planning/amendments/sha256/m3_chr*.tsv | tail -n +2 >> .planning/amendments/sha256_manifest_m3_frozen.tsv
       ```
       Result: a 323-row TSV (1 header + 322 rows; one row per region × ancestry).

    7. Append a "Close-out summary table" to `.planning/amendments/aou-egress-audit-log.md`:
       - Total bundles egressed: 44
       - Total compressed size egressed: __ GB (sum from per-bundle rows)
       - Total .npz size on disk pre-deletion: __ GB (per-region cumulative)
       - Total .rds size on disk: __ GB (Wave 4 conversion output)
       - .npz files deleted post-conversion per AOU-LD-PIPELINE.md §10.3: yes/no (audit trail)
       - Average AoU review SLA: __ business days
       - Hard-gate cross-references: M3 = osf.io/az52u; M1-AFR-SBP = pending M1-supplementary
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; wc -l .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf &amp;&amp; wc -l .planning/amendments/sha256_manifest_m3_frozen.tsv &amp;&amp; grep -c "Close-out summary" .planning/amendments/aou-egress-audit-log.md &amp;&amp; grep -c "Section 10\\|Production-scale validation addendum" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md</automated>
  </verify>
  <acceptance_criteria>
    - `wc -l .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 150 (Wave 4 addendum added).
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf` exits 0.
    - `wc -c .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf` returns ≥ 50000 bytes (non-trivial PDF).
    - `grep -c "Production-scale validation addendum\\|Section 10" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 1.
    - `grep -c "Section 11\\|Cluster-hours" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 1.
    - `grep -c "Section 12\\|Per-cohort N" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 1.
    - `wc -l .planning/amendments/sha256_manifest_m3_frozen.tsv` returns 323 (1 header + 322 region rows).
    - `head -1 .planning/amendments/sha256_manifest_m3_frozen.tsv | grep -c "rds_sha256"` returns 1.
    - `grep -c "Close-out summary" .planning/amendments/aou-egress-audit-log.md` returns ≥ 1.
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv` exits 0.
  </acceptance_criteria>
  <done>
    Validation memo + PDF + monolith SHA-256 + audit log close-out all committed. Carter has a paste-ready PDF for the osf.io/az52u supplementary upload (Task 3 manual gate).
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Toy 3-locus AFR identity-placeholder fixtures + Snakefile.test resolver-chain CI smoke</name>
  <files>tests/toy_3locus/data/ld_ref/FTO_16q12.AFR.rds, tests/toy_3locus/data/ld_ref/SH2B3_12q24.AFR.rds, tests/toy_3locus/data/ld_ref/TCF7L2_10q25.AFR.rds, tests/toy_3locus/Snakefile.test</files>
  <read_first>
    - tests/toy_3locus/data/ld_ref/*.rds (existing EUR identity-placeholder fixtures: FTO_16q12.rds, SH2B3_12q24.rds, TCF7L2_10q25.rds — convention reference)
    - tests/toy_3locus/Snakefile.test (existing toy 3-locus pipeline; extends with new AFR LD targets)
    - .planning/REQUIREMENTS.md REQ-SNAKEMAKE-CI (lines 25-39) — toy 3-locus runs in <15 min on `--cores 2 --use-conda`
    - src/python/ld_panel.py::resolve_ld_path (Wave 0; the resolver under test)
  </read_first>
  <behavior>
    - test_toy_3locus_afr_fixtures_have_correct_shape: each .AFR.rds is a list with `ld` (n×n symmetric), `snp_ids` (length n), `provenance` (list); n matches the existing EUR fixture for the same region.
    - test_toy_3locus_resolver_chain_falls_through: when AFR_aou path is missing AND AFR_hgdp_1kg is missing AND AFR_1kg is missing, resolve_ld_path returns the identity-placeholder path (the .AFR.rds fixtures created here).
    - test_toy_3locus_snakefile_lists_afr_targets: Snakefile.test's `rule all` (or top-level target) includes paths matching `*.AFR.rds`.
  </behavior>
  <action>
    1. Inspect existing tests/toy_3locus/data/ld_ref/*.rds to determine the EUR-side dimensions for FTO_16q12, SH2B3_12q24, TCF7L2_10q25.

    2. For each of FTO_16q12, SH2B3_12q24, TCF7L2_10q25, write a small R script (one-shot) that creates an identity-placeholder LD `.AFR.rds`:
       ```r
       library(Matrix)
       set.seed(42)  # deterministic
       n <- 50  # match EUR-side n (or detect dynamically)
       ld <- diag(n)  # identity placeholder
       snp_ids <- paste0("rs", seq_len(n))
       provenance <- list(
         npz_path = "synthetic-identity-placeholder",
         genome_build = "GRCh37",
         note = "Toy 3-locus AFR identity placeholder — not real LD; exists only for REQ-SNAKEMAKE-CI smoke."
       )
       saveRDS(list(ld = ld, snp_ids = snp_ids, provenance = provenance),
               "tests/toy_3locus/data/ld_ref/FTO_16q12.AFR.rds", compress = "xz")
       # repeat for SH2B3_12q24.AFR.rds, TCF7L2_10q25.AFR.rds
       ```

    3. Extend `tests/toy_3locus/Snakefile.test` to add AFR-side targets to its top-level `rule all` (or equivalent). Add 3 rules paralleling the EUR-side identity-placeholder consumers, each consuming `tests/toy_3locus/data/ld_ref/{region}.AFR.rds` as input.

    4. Add a CI smoke-test rule that exercises the resolver chain:
       ```python
       rule toy_3locus_resolver_smoke:
           """REQ-SNAKEMAKE-CI: verify resolve_ld_path() fallback chain works in CI by
           pointing at AFR_aou paths that don't exist (in CI). Should fall through to
           the identity-placeholder."""
           input:
               ld_files = expand("tests/toy_3locus/data/ld_ref/{region}.AFR.rds",
                                  region=["FTO_16q12", "SH2B3_12q24", "TCF7L2_10q25"]),
           output:
               "tests/toy_3locus/data/resolver_smoke_pass.flag",
           shell:
               """
               python -c "
               from pathlib import Path
               import sys, yaml
               sys.path.insert(0, 'src/python')
               from ld_panel import resolve_ld_path
               cfg = yaml.safe_load(open('config/pipeline.yaml'))
               # Override paths to point at toy_3locus — for CI smoke
               cfg['ld_panel']['AFR'].append({{'source': 'AFR_identity', 'path': 'tests/toy_3locus/data/ld_ref/{{region_safe}}.AFR.rds'}})
               for region in ['FTO_16q12', 'SH2B3_12q24', 'TCF7L2_10q25']:
                 path = resolve_ld_path(region, 'AFR', cfg)
                 print(f'{{region}} -> {{path}}')
                 assert path.exists(), f'resolver fell through but no path exists for {{region}}'
               print('OK')
               " > {output}
               """
       ```

    5. Add a pytest at `tests/m3/test_toy_3locus_afr_extension.py` (already covered by behaviors above; can fold into existing test_ld_panel_resolver.py or add new):
       ```python
       def test_toy_3locus_afr_fixtures_exist():
           for region in ["FTO_16q12", "SH2B3_12q24", "TCF7L2_10q25"]:
               assert Path(f"tests/toy_3locus/data/ld_ref/{region}.AFR.rds").exists()
       ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; ls tests/toy_3locus/data/ld_ref/*.AFR.rds | wc -l &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3 -x --tb=short 2&gt;&amp;1 | tail -10</automated>
  </verify>
  <acceptance_criteria>
    - `ls tests/toy_3locus/data/ld_ref/*.AFR.rds | wc -l` returns 3.
    - `Rscript -e 'x <- readRDS("tests/toy_3locus/data/ld_ref/FTO_16q12.AFR.rds"); stopifnot(isSymmetric(x$ld)); stopifnot(length(x$snp_ids) == nrow(x$ld)); cat("OK\n")'` prints OK.
    - `grep -c "AFR.rds" tests/toy_3locus/Snakefile.test` returns ≥ 3 (3 AFR targets added).
    - `grep -c "toy_3locus_resolver_smoke\\|resolver_smoke_pass" tests/toy_3locus/Snakefile.test` returns ≥ 1.
    - `pytest tests/m3 -x` STILL passes with the new fixtures (regression).
    - `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda --dry-run` exits 0.
  </acceptance_criteria>
  <done>
    3 AFR identity-placeholder fixtures land. Snakefile.test extended with AFR targets + resolver smoke rule. Pytest still green. REQ-SNAKEMAKE-CI extension closed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: m2_post_m3_rerun_queue update + ROADMAP M2-supplementary entry + STATE.md update + m3-PHASE-CLOSEOUT</name>
  <files>.planning/m2_post_m3_rerun_queue.tsv, .planning/ROADMAP.md, .planning/STATE.md, .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md</files>
  <read_first>
    - .planning/m2_post_m3_rerun_queue.tsv (M2 deliverable; 8 obligations across 9 columns + 1 header)
    - .planning/ROADMAP.md M2 entry (lines 138-144) AND M3 entry (lines 146-180; updated by Wave 0) AND M4 entry (lines 178-220) — convention for M2-supplementary phase entry insertion
    - .planning/STATE.md current state — to update stopped_at, last_activity, milestone progress
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decisions D-M3-05 (M2-supplementary) and D-M3-09 (Wave 0 Carter ruling — must reference in close-out)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/*-SUMMARY.md (M2 close-out template reference)
  </read_first>
  <action>
    1. Edit `.planning/m2_post_m3_rerun_queue.tsv`. For each of the 8 rows (M2-POST-M3-01 through -08): append a status note in the `notes` column (or add a 10th column `m3_close_status` if not present) with `M3 complete YYYY-MM-DD; M2-supplementary phase eligible to start`. DO NOT mark any obligation as closed (per D-M3-05; closure happens in m2-supp-aou-afr-rerun phase).

    2. Edit `.planning/ROADMAP.md` to add a new "M2-supplementary: AoU AFR re-fire" phase entry between M3 (lines 146-180) and M4 (line 178+). The entry follows M2/M3 ROADMAP convention:
       ```markdown
       ### M2-supplementary: AoU AFR re-fire (consumes M3 outputs)
       **Slug**: m2-supp-aou-afr-rerun
       **Goal**: Re-fire the 8 M2-POST-M3-* obligations using the M3 AoU AFR LD panel + AFR ld-scores. Consumes data/processed/ld_reference/AFR_aou/*.rds (M3 deliverable) + (to be built in this phase) data/external/ldscore/afr_w_ld_chr/ derived from AoU AFR WGS. Closes M2's AFR provisional 1000G AFR (N=504) supersede chain per D-M2-02 + D-M3-05.
       **Requirements**: REQ-AOU-LD-EGRESS (carry-forward), REQ-PUBLIC-DATA-ONLY, REQ-PATH-PARAMETERIZATION
       **Dependencies**: M3 complete (all 322 .rds files + validation memo + audit log)
       **Carry-forward obligations** (from .planning/m2_post_m3_rerun_queue.tsv):
         - M2-POST-M3-01 — AFR PLINK clumping re-fire (high)
         - M2-POST-M3-02 — AFR LDSC matrix slice re-fire (high)
         - M2-POST-M3-03 — AFR mtCOJO re-fire (medium)
         - M2-POST-M3-04 — TRANS mtCOJO 1000G AFR sensitivity (low)
         - M2-POST-M3-05 — AFR ld-score derivation from AoU AFR WGS (medium)
         - M2-POST-M3-06 — GWAS Catalog v_lock_M5 refresh (deferred to M5)
         - M2-POST-M3-07 — MTAG --fdr LSF re-fire (high)
         - M2-POST-M3-08 — mtCOJO production sensitivity LSF re-fire (high)
       **Success Criteria**:
         1. data/external/ldscore/afr_w_ld_chr/*.l2.ldscore.gz lands with provenance JSON
         2. data/processed/clumping/AFR/*.LD-AoU-AFR.clumped.bed lands (M2-POST-M3-01)
         3. data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-XX-XX.tsv re-fired with AFR ld-scores (M2-POST-M3-02)
         4. data/processed/mtcojo/AFR/*.mtcojo.AoU.cojo lands (M2-POST-M3-03)
         5. M2 supersede artifacts have provenance pointing at M3 inputs
       **Status**: not planned; eligible to start post-M3 close (planning-phase NEXT step)
       ```

    3. Update `.planning/STATE.md`:
       - `stopped_at:` field: replace with `Phase m3 complete YYYY-MM-DD (322 .rds + validation memo + 44-row audit log + monolith SHA-256 frozen); M2-supplementary phase queued; M4 fine-mapping unblocked.`
       - `last_activity:` field: today's date with text `Phase m3 close-out complete (m3-PHASE-CLOSEOUT.md committed)`.
       - `progress.completed_phases`: increment by 1 (was 6; becomes 7).
       - `progress.total_plans`: add 6 (was 30; becomes 36).
       - `progress.completed_plans`: add 6 (was 30; becomes 36).
       - `progress.percent` recompute.

    4. Create `.planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` (mirroring M2's PHASE-CLOSEOUT pattern):

       ```markdown
       # Phase M3 — AoU AFR LD panel build — Phase Close-out

       Date: YYYY-MM-DD
       Slug: m3-aou-afr-ld-panel-build
       Status: COMPLETE

       ## Requirement coverage

       | REQ ID | Status | Closing artifact(s) |
       |--------|--------|---------------------|
       | REQ-AOU-LD-EGRESS | CLOSED | aou-egress-classification-ruling.eml + aou-egress-audit-log.md (44+ rows) + sha256_manifest_m3_frozen.tsv |
       | REQ-AOU-LD-VALIDATION | CLOSED | m3-VALIDATION-MEMO.md (Carter signoff Section 9 + Wave 4 Section 10 production addendum) |
       | REQ-PUBLIC-DATA-ONLY | CLOSED | OSF posting at osf.io/az52u (D-M3-08); aggregate-LD-only artifacts |
       | REQ-SNAKEMAKE-CI | CLOSED | m3_*.smk rules registered in Snakefile; tests/toy_3locus/data/ld_ref/*.AFR.rds extended |
       | REQ-PATH-PARAMETERIZATION | CLOSED | config/pipeline.yaml ld_panel: block; src/python/ld_panel.py::resolve_ld_path; finemap.smk wired |

       ## Decision audit (D-M3-01 through D-M3-09)

       (table: D-M3-XX | summary | implementation evidence)

       ## Deliverables (322 .rds + governance)

       (table: artifact path | role | SHA-256 if frozen)

       ## Cluster-hours + AoU credits consumed

       (table: cluster-hours, AoU credits, $ cost estimate)

       ## Downstream-phase eligibility

       - M2-supplementary (slug m2-supp-aou-afr-rerun): ELIGIBLE — needs /gsd-discuss-phase
       - M4 (m4-scalable-coloc-finemapping): ELIGIBLE for AFR-side fine-mapping using AoU AFR LD; EUR-side already eligible via 1000G EUR

       ## Lessons / patterns established

       (Bullet list of patterns the next phases inherit; e.g., the per-region radius algorithm, the Path A.3 BlockMatrix-write convention, the per-bundle Q12 audit log schema, the resolve_ld_path() helper.)

       ## Sign-off

       Carter Clinton — YYYY-MM-DD
       ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; grep -c "M3 complete" .planning/m2_post_m3_rerun_queue.tsv &amp;&amp; grep -c "m2-supp-aou-afr-rerun" .planning/ROADMAP.md &amp;&amp; grep -c "Phase m3 complete" .planning/STATE.md &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "M3 complete" .planning/m2_post_m3_rerun_queue.tsv` returns 8 (one per row).
    - `grep -c "m2-supp-aou-afr-rerun" .planning/ROADMAP.md` returns >= 1.
    - `grep -c "M2-POST-M3-01" .planning/ROADMAP.md` returns >= 1 (carry-forward obligations listed).
    - `grep -c "Phase m3 complete" .planning/STATE.md` returns >= 1.
    - `python -c "import yaml,sys; raw=open('.planning/STATE.md').read(); fm=raw.split('---')[1]; m=yaml.safe_load(fm); assert m['progress']['completed_phases'] >= 7; assert m['progress']['total_plans'] >= 36; print('OK')"` prints OK.
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` exits 0.
    - `wc -l .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` returns >= 80.
    - `grep -cE "REQ-AOU-LD-EGRESS|REQ-AOU-LD-VALIDATION|REQ-PUBLIC-DATA-ONLY|REQ-SNAKEMAKE-CI|REQ-PATH-PARAMETERIZATION" .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` returns >= 5.
    - `grep -c "D-M3-01\|D-M3-02\|D-M3-03\|D-M3-04\|D-M3-05\|D-M3-06\|D-M3-07\|D-M3-08\|D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` returns >= 9 (all locked decisions referenced).
  </acceptance_criteria>
  <done>
    M2-supersede queue updated with status notes (no closures). ROADMAP gains M2-supplementary phase entry. STATE.md reflects M3 complete with progress increments. m3-PHASE-CLOSEOUT.md emits with REQ + decision + deliverable tables.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 4: OSF posting of m3-VALIDATION-MEMO.pdf to osf.io/az52u (D-M3-08)</name>
  <files>.planning/amendments/aou-egress-audit-log.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf (Task 1 output; paste-ready)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decision D-M3-08 (OSF posting form)
    - .planning/DECISIONS.md DEC-2026-04-25-02 (OSF amendment posting form; M1 set the pattern at osf.io/az52u/files/k8w7n)
  </read_first>
  <action>See &lt;human_gate&gt; block. This task is a Carter human-action checkpoint; no agent action. The agent's role is to verify acceptance_criteria after Carter completes the gate.</action>
  <human_gate>
    <gate>Manual OSF supplementary file upload</gate>
    <description>
      Carter manually uploads m3-VALIDATION-MEMO.pdf to osf.io/az52u as a supplementary file (same form as M1 osf.io/az52u/files/k8w7n per DEC-2026-04-25-02). After upload:

      1. Capture OSF-issued file URL (e.g., osf.io/az52u/files/abcdef).
      2. Append a new row to the close-out summary in .planning/amendments/aou-egress-audit-log.md with the OSF DOI / URL.
      3. Commit with token (m3-W5-T4) in subject.

      D-M3-08 closure is the final M3 governance deliverable.
    </description>
    <unblocks>M3 phase closure (downstream M2-supplementary + M4)</unblocks>
    <how-to-resolve>
      1. Log into osf.io/az52u; navigate to "Files" tab.
      2. Upload .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf as a supplementary file.
      3. Capture OSF file URL.
      4. Append URL to .planning/amendments/aou-egress-audit-log.md close-out summary.
      5. Commit with (m3-W5-T4) token + type "approved" to resume.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; grep -cE "osf\.io/az52u/files/[a-z0-9]+" .planning/amendments/aou-egress-audit-log.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -cE "osf\\.io/az52u/files/[a-z0-9]+" .planning/amendments/aou-egress-audit-log.md` returns >= 1 (OSF supplementary file URL captured).
    - Git log shows a commit with `(m3-W5-T4)` token in subject.
  </acceptance_criteria>
  <done>
    m3-VALIDATION-MEMO.pdf posted to osf.io/az52u as a supplementary file. URL captured in audit log close-out summary. D-M3-08 closed. M3 phase formally complete.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| .planning artifacts on git ↔ OSF public record | The validation memo PDF crosses from private NCSU repo to public OSF amendment record. By construction the PDF carries only aggregate-LD-statistics tables + cohort N + cluster-hours; no individual-level data. |
| .planning artifacts ↔ M2-supplementary + M4 phases | The 322 .rds files + ld_panel: resolver chain are the hand-off interface. ROADMAP M2-supplementary entry + STATE.md update make the hand-off explicit. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3-EGR-W5 | Information disclosure | OSF posting of m3-VALIDATION-MEMO.pdf | mitigate | PDF is verifiably aggregate-LD-only (no individual-level data); cohort N is from AoU summary statistics; the PDF is generated from m3-VALIDATION-MEMO.md which is itself git-tracked NCSU-side. Carter visually inspects pre-upload. The OSF posting is governed by the AoU egress classification ruling (Wave 1) which already approved aggregate-summary-statistic egress. |
| T-M3-S2-W5 | Reproducibility / provenance | sha256_manifest_m3_frozen.tsv | mitigate | 322-row monolith aggregates the 44 per-bundle sub-manifests; both per-region .rds SHA + per-bundle .npz SHA captured. Zenodo-deposit-ready at publication. |
| T-M3-S2-W5-CLOSEOUT | Reproducibility / provenance | m3-PHASE-CLOSEOUT.md | mitigate | REQ-coverage table + decision audit table + deliverable hash table + downstream-phase eligibility — all required for the next /gsd-verify-work to certify M3 closed. |
| T-M3-AUTH-W5 | Authorization | M2-supersede queue status note | mitigate | NO obligations marked closed (per D-M3-05); status note explicitly says "M2-supplementary phase eligible to start" — the M2-supplementary phase is the only legal closure path for M2-POST-M3-* obligations. |
</threat_model>

<verification>
**Wave 5 phase-level checks:**

1. `wc -l .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` >= 150.
2. `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.pdf` exits 0.
3. `wc -l .planning/amendments/sha256_manifest_m3_frozen.tsv` returns 323.
4. `grep -c "M3 complete" .planning/m2_post_m3_rerun_queue.tsv` returns 8.
5. `grep -c "m2-supp-aou-afr-rerun" .planning/ROADMAP.md` >= 1.
6. `grep -c "Phase m3 complete" .planning/STATE.md` >= 1.
7. `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` exits 0.
8. `ls tests/toy_3locus/data/ld_ref/*.AFR.rds | wc -l` returns 3.
9. `grep -cE "osf\\.io/az52u/files/[a-z0-9]+" .planning/amendments/aou-egress-audit-log.md` >= 1.
10. `pytest tests/m3 -x` passes (no regression).
</verification>

<success_criteria>
- m3-VALIDATION-MEMO.md finalized with Wave 4 production-scale addendum (Section 10) + cluster-hours (Section 11) + cohort N (Section 12) + OSF cross-ref (Section 13).
- m3-VALIDATION-MEMO.pdf generated and OSF-posted.
- sha256_manifest_m3_frozen.tsv 322-row monolith committed.
- aou-egress-audit-log.md finalized with close-out summary + OSF URL.
- m2_post_m3_rerun_queue.tsv updated (status notes; NO closures).
- ROADMAP.md gains m2-supp-aou-afr-rerun phase entry.
- STATE.md reflects M3 complete with progress increments.
- m3-PHASE-CLOSEOUT.md emits with REQ + decision + deliverable tables.
- Toy 3-locus pipeline extended with 3 AFR identity-placeholder fixtures + resolver smoke rule.
- All 5 REQ IDs closed in PHASE-CLOSEOUT.md.
- All 9 D-M3-XX decisions referenced in PHASE-CLOSEOUT.md.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-05-W5-closeout-and-osf-SUMMARY.md` recording:
- Files committed (11 governance + 4 toy-3-locus = 15)
- OSF supplementary file URL
- M3 cumulative cluster-hours + AoU credits consumed (across all waves)
- M3 deliverable count (322 .rds + 44 audit-log rows + governance docs)
- Total wave-by-wave duration in calendar days (Wave 0 -> Wave 5)
- Lessons established for downstream phases (M2-supplementary + M4)
</output>
