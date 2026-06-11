---
status: resolved
resolution: "2026-06-11 — fix live-confirmed (74,576→63,312 strict subset, SENS_FILTER_VERSION=2 matching WhatRaceEthnicity_Black); clean AFR-sens cohort banked (62,557×20,817,925, self_report present, contamination tell absent). Pattern: knowledge-base.md#m3-afr-sensitivity-selfid-noop."
trigger: "m3-W2-afr-sensitivity-selfid-noop — AFR sensitivity cohort is a null/no-op duplicate of AFR primary"
created: 2026-06-08T15:39:28Z
updated: 2026-06-08T15:55:00Z
---

## Current Focus

hypothesis: CONFIRMED — sensitivity=True was a silent no-op (Fault A: self_report never sourced; Fault B: silent skip behind `and "self_report" in mt.col`).
test: TDD complete. RED committed (005d651), GREEN fix committed (9b86b99), extractor committed (next). Local pytest GREEN.
expecting: cluster re-fire of AFR-sens only yields 0 < N_sens < N_primary (strict subset) instead of membership-identical.
next_action: HUMAN-VERIFY — user runs the BigQuery extraction + purge + fresh AFR-sens re-fire per the runbook below, then confirms N_sens < 73,122.

## Symptoms

expected: With sensitivity=True (D-M3-07), AFR cohort = genetic-ancestry AFR ∩ self-reports "Black or African American" — a STRICT non-empty SUBSET of the primary (genetic-ancestry-only) AFR cohort. N_sens < N_primary by a few %.
actual: AFR-sens == AFR-primary, membership-identical: both 73,122 samples × 20,767,864 variants (identical N and M to the last unit). The two on-disk MTs differ by only 306 KB on a 1.6 TB store (~0.014 samples-equivalent) → identical membership, different physical write layout, NOT two distinct cohorts.
errors: No exception. Silent no-op. That is the danger.
reproduction: Run load_qc_cohort(..., sensitivity=True) against the production AoU WGS MT. The self-report restriction never applies.
started: Surfaced 2026-06-08 at the Cell 4.5 N/M gate after the AFR-sens (Cell 4) genome-wide build completed.

## Evidence

- timestamp: 2026-06-08T15:39:28Z
  checked: `grep -rn self_report src/ + all .ipynb`
  found: `self_report` appears at EXACTLY two lines in the whole repo — src/python/aou_ld_panel.py:1659 (filter guard) and :1660 (the filter). NOWHERE is it import_table'd or annotate_cols'd. Zero occurrences in any notebook.
  implication: FAULT A confirmed — the column the sensitivity filter references is never sourced onto the MT. The feature was half-built.

- timestamp: 2026-06-08T15:39:28Z
  checked: Contrast with how `ancestry_pred` and `relateds` ARE sourced.
  found: ancestry: _resolve_aux_file(aux_base,"ancestry","ancestry_preds.tsv", on_ambiguous="raise") at :1531-1532 → import_table(key=research_id) + annotate_cols if ANCESTRY_FIELD absent (:1641-1647). relateds: _resolve_aux_file(...,"relatedness",...,on_ambiguous="fallback") :1533-1535 → import_table(key=sample_id) + anti_join_cols (:1650-1653). Both mandatory/best-effort patterns are explicit + tested.
  implication: There is an EXISTING, well-tested data-sourcing machinery (_resolve_aux_file + import_table + annotate_cols) the self_report feature should have used and did not. Self-reported race is NOT an AoU-shipped genomic aux file (ancestry_preds.tsv / relatedness_flagged_samples.tsv) — it lives in the CDR `person` table, reachable only via BigQuery → must be extracted to a sidecar TSV first.

- timestamp: 2026-06-08T15:39:28Z
  checked: Line 1659 guard semantics.
  found: `if sensitivity and "self_report" in mt.col:` — when self_report is absent (always, per Fault A), the entire filter block is SKIPPED with no log, no warning, no raise.
  implication: FAULT B confirmed — silent skip masks Fault A. Violates the codebase's own MANDATORY discipline (ancestry: on_ambiguous="raise", "refuse to guess", hard-fail loudly — see :1527, :180-191). sensitivity=True therefore yields the IDENTICAL predicate as sensitivity=False (afr-ancestry + relateds anti-join).

- timestamp: 2026-06-08T15:39:28Z
  checked: Why the bug LOOKED like two distinct cohorts (the 306 KB / 1.6 TB byte delta).
  found: Path isolation (_intermediate_checkpoint_uri appends _pca_selfid infix when sensitivity=True; tested at test_intermediate_checkpoint_uri_post_variant_qc_afr_sensitivity etc.) guarantees DISTINCT write URIs. But path isolation guards WHERE you write, never WHAT the cohort contains. Two byte-near-identical MTs at distinct URIs = same membership, different parquet layout.
  implication: The byte-magnitude proof (306 KB delta ≈ 0.014 samples-equivalent on a per-sample ~22 GB store) is positive evidence of identical membership. Contamination guard for the re-fire must verify MEMBERSHIP (N strictly < primary), not just the path or the _SUCCESS marker.

## Eliminated

- hypothesis: "Path isolation failed / sens wrote over primary's URI."
  evidence: _intermediate_checkpoint_uri + _qc_checkpoint_uri _pca_selfid infix is well-tested (tests 187-217, 565-568). The two MTs are at DISTINCT URIs. The defect is membership, not pathing.
  timestamp: 2026-06-08T15:39:28Z

## Resolution

root_cause: |
  TWO compounding faults in src/python/aou_ld_panel.py.
  FAULT A (root cause — missing data sourcing): `self_report` is NEVER sourced onto the MT (referenced only at :1659-1660, never import_table'd / annotate_cols'd). AoU self-reported race is not a genomic aux file; it lives in the CDR `person` table (BigQuery-only). The sensitivity feature was half-built: a filter referencing a column the data flow never provides.
  FAULT B (masking — silent skip): :1659 `if sensitivity and "self_report" in mt.col:` converts the missing column into a silent skip instead of a loud failure, violating the codebase's own ancestry-is-MANDATORY discipline.
  NET: sensitivity=True == sensitivity=False predicate. Path isolation made it LOOK like two MTs.
fix: |
  Scoped STRICTLY to the sensitivity=True branch (sensitivity=False byte-stable -> EUR / AFR-primary unaffected).
  1. New module constants (aou_ld_panel.py): SELF_REPORT_FIELD/SUBDIR/SUFFIX/PATH, SELF_REPORT_AFR_MATCH="Black or African American", SENS_FILTER_VERSION="1", MIN_SELF_REPORT_COVERAGE=0.95.
  2. New param self_report_table_path (mirrors ancestry_table_path); threaded through the genome-wide fan-out recursion.
  3. Sourcing: when sensitivity=True, resolve the sidecar via _resolve_aux_file(SELF_REPORT_SUBDIR, SELF_REPORT_SUFFIX, on_ambiguous="raise") (override wins via `or`).
  4. Step 4 rewrite: DELETE the `and "self_report" in mt.col` silent escape. If self_report not on cols -> import_table(key=research_id)+annotate_cols; import HARD-FAILS loudly on unresolvable sidecar. Then filter_cols(self_report.contains(MATCH)).
  5. Defense in depth: assert coverage >= MIN_SELF_REPORT_COVERAGE; assert proper non-empty subset 0 < N_post < N_pre (catches empty sidecar AND the no-shrink == primary defect).
  6. Provenance: _collect_provenance records self_report_path + sens_filter_version (sensitivity-only; None on primary) so a semantics change auto-invalidates intermediates.
  7. New artifact src/python/extract_aou_self_report.py — BigQuery person-table -> research_id+self_report TSV, staged to WORKSPACE_BUCKET, consumed via self_report_table_path.
  Commits: 005d651 (RED tests) -> 9b86b99 (GREEN fix) -> extractor commit.
verification: |
  LOCAL TDD GREEN on GPFS dev host (smoke_dev python, pytest 9.0.3):
  - tests/m3/test_aou_ld_panel_local.py: 102 passed, 19 skipped (skips = live-Hail incl. T1/T2 — no Hail on GPFS host).
  - tests/m3/ full suite: 139 passed, 35 skipped.
  - New sensitivity guards: test_sensitivity_silent_skip_escape_is_deleted PASS, test_sensitivity_sources_self_report_via_resolve_aux_file PASS, test_selfreport_filter_version_token_in_provenance PASS, test_selfreport_filter_version_token_independent_of_sensitivity_false PASS (scoping).
  - T1 (strict-subset) / T2 (hard-fail) are live-Hail dynamic tests -> run on the cluster re-fire (skip locally, by design — same as every pre-existing live-Hail test here).
  CLUSTER (user's human-verify): BigQuery extract + purge contaminated intermediates + fresh AFR-sens re-fire; confirm 0 < N_sens < 73,122.
files_changed:
  - src/python/aou_ld_panel.py (constants + self_report_table_path param + sourcing + Step-4 rewrite + provenance)
  - src/python/extract_aou_self_report.py (NEW; AoU CDR self-report sidecar extractor)
  - tests/m3/test_aou_ld_panel_local.py (RED-first: 2 pure-Python static guards, 2 provenance tests, 2 live-Hail T1/T2)

## Cluster Runbook (USER ACTION — do NOT run from GPFS; AoU Workbench only)

PRECONDITIONS:
  - Fresh-clone the repo on the AoU Workbench at the fix HEAD (>= 9b86b99 + extractor commit).
  - Re-apply the 3 manual Cell-1a env guards (WORKSPACE_BUCKET pin gs://rw-migration-aou-rw-476cdac2, wgs-literal, requester-pays) — NOT in repo ([[feedback_aou_cluster_template_bucket_pollution]]).
  - AFR-primary (mt_afr_qc.mt) and EUR are UNCONTAMINATED — DO NOT touch them.

(a) BigQuery extract + stage the self_report sidecar:
    python src/python/extract_aou_self_report.py \
        --out gs://${WORKSPACE_BUCKET}/ld/aux/self_report/self_report.tsv
    # Inspects person-table self-reported race; emits research_id<TAB>self_report.
    # Prints the count of persons whose self_report contains "Black or African American".
    # (If that count is 0, STOP and inspect the person schema — the driver will
    #  RAISE on the empty-subset guard rather than ship a degenerate cohort.)
    # NOTE: the controlled-tier aux/ is READ-ONLY, so we stage in WORKSPACE_BUCKET
    # and pass it explicitly via self_report_table_path (override wins over the
    # discover-by-suffix resolver).

(b) PURGE the contaminated AFR-sens intermediates + final (MUST purge or the
    auto-resume state machine resumes off contaminated checkpoints and re-ships
    the bug):
    gsutil -m rm -r gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt
    gsutil -m rm -r gs://${WORKSPACE_BUCKET}/ld/intermediate/mt_afr_pca_selfid_post_split_chr*
    gsutil -m rm -r gs://${WORKSPACE_BUCKET}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc_chr*
    # also remove any non-chrom-suffixed sens intermediates if present:
    gsutil -m rm -r gs://${WORKSPACE_BUCKET}/ld/intermediate/mt_afr_pca_selfid_post_split.mt   2>/dev/null || true
    gsutil -m rm -r gs://${WORKSPACE_BUCKET}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc.mt 2>/dev/null || true
    # and the .meta.json sidecars alongside them.

(c) FRESH re-fire AFR-sens ONLY (AOU-1 Cell 4), patched to pass the sidecar:
    SELF_REPORT_TSV = f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/aux/self_report/self_report.tsv"
    mt_afr_selfid = load_qc_cohort(
        mt_path=os.environ["WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"],
        ancestry="afr",
        sensitivity=True,
        self_report_table_path=SELF_REPORT_TSV,   # NEW: MANDATORY sidecar
        force_fresh=True,                          # post-purge fresh build
    )
    n_afr_selfid = mt_afr_selfid.count_cols()
    # EXPECT: 0 < n_afr_selfid < 73,122 (strict non-empty subset of AFR-primary).
    # The build PRINTS "sensitivity self-report filter applied: N_pre -> N_post".
    # If N_post == N_pre or N_post == 0, the driver RAISES (defense-in-depth) — a
    # malformed sidecar / bad match string fails loudly instead of shipping a
    # degenerate cohort.

(d) Re-run Cell 4.5 (post-write contents validation), then continue Cell 5 (EUR)
    -> 5.5 -> 6 (disjoint) -> 7 (cohort_summary_m3.tsv) -> mirror to GPFS.

CONTAMINATION ARBITER (per byte-magnitude proof): verify MEMBERSHIP, not just
the _SUCCESS marker or the path. mt_afr_pca_selfid_qc.mt count_cols MUST be
strictly < mt_afr_qc.mt count_cols (a few % fewer). A byte-identical or
N-identical sens MT == still contaminated.

---

## 2026-06-08 FOLLOW-UP — VPC-SC perimeter + self-report match contract (commit 06b8a97)

Two issues surfaced during the live PRODUCE attempt:

1. **VPC-SC perimeter (infra, not code).** BigQuery CDR job-insert from the
   migrated Verily workbench (wb-perky-corn-6639 / terra-vpc-sc-fe7a5641) is
   blocked by an org VPC Service Controls perimeter wrapping the classic AoU CDR
   (fc-aou-cdr-prod-ct.C2024Q3R9). Error class = "VPC Service Controls", NOT an
   IAM Access-Denied — data + grant are fine; the request originates outside the
   fence. RESOLUTION = run the extract from an in-perimeter sanctioned AoU env
   (classic Jupyter), stage the TSV to the Verily bucket the PET-SA cluster
   reads. DO NOT circumvent the perimeter.

2. **Match-string contract bug (FIXED 06b8a97).** Live `GROUP BY
   race_source_value` on C2024Q3R9: the Black answer is coded
   `WhatRaceEthnicity_Black` (99,788). The display string "Black or African
   American" is produced only by a fragile concept-name JOIN (AoU names that
   concept "Black, African American, or African") -> the old
   `.contains("Black or African American")` silently matched ZERO -> the
   proper-subset assert would hard-fail the re-fire. FIX = match the stable
   survey CODE in lockstep: driver SELF_REPORT_AFR_MATCH="WhatRaceEthnicity_Black",
   extractor emits race_source_value verbatim (concept JOIN dropped), T1 + static
   tests updated, SENS_FILTER_VERSION 1->2. tests/m3 102 passed/19 skipped.

## 2026-06-08 STATUS — TSV produced + validated; relay VPC-SC-blocked; ticket prepared

Extractor re-run on the classic (in-perimeter) AoU side; TSV produced and
ALL 4 CHECKS GREEN: header `research_id<TAB>self_report`; 633,548 rows; 99,788
`WhatRaceEthnicity_Black`; research_id == MT `s` key (both str bare integer
person_ids — `mt_afr_qc.mt.s.take(5)` = ['1000000','1000042',...] vs TSV
['1447308',...]). Producer↔consumer lockstep confirmed end-to-end.

**TSV is staged in the CLASSIC bucket** (`gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/aux/self_report/self_report.tsv`, 20,643,040 bytes) and must reach the **Verily bucket** (`gs://rw-migration-aou-rw-476cdac2/ld/aux/self_report/self_report.tsv`) for the cluster to read it. **EVERY self-serve transfer path is confirmed dead (VPC-SC):**
- PET-to-PET copy -> IAM 403 (mutually walled)
- user CLI as `cclinton@researchallofus.org` (reads BOTH buckets) -> cross-bucket `gsutil cp` VPC-SC-blocked by org policy
- project switch to `wb-perky-corn-6639` -> same VPC-SC denial (perimeter, not quota project)
- Cloud Console same identity -> same API -> same block
This is the RW1.0->RW2.0 migration two-perimeter split working as designed. NOT bypassed.

**NEXT (Carter, fresh session): SEND THE AOU TICKET.** Full ready-to-send text +
VPC-SC denial IDs + both acceptable resolutions + post-resolution re-fire steps:
`.planning/debug/aou-cross-bucket-transfer-ticket.md`. When AoU lands the TSV in
the Verily bucket (or grants the Verily PET read on the classic object) -> mv
contaminated `mt_afr_pca_selfid_*` to forensics -> FRESH re-fire AFR-sens
(`self_report_table_path=<resolved>, force_fresh=True`). Arbiter: count_cols <
73,122 + `.describe()` shows self_report.

**CRITICAL PATH proceeds in parallel, NO ticket needed:** EUR (Cell 5/9) was
FIRED and is building on the cluster (sensitivity=False, no CDR). Resume = check
EUR via GCS `intermediate/mt_eur_post_variant_qc_chrN` listing; on landing ->
Cell 5.5 (validate) -> 6 (disjoint AFR∩EUR) -> 7 (cohort_summary; interim
2-cohort, backfill the sens row when the ticket clears).
