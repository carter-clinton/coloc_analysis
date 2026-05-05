# OSF Amendment — Paste-Ready Text (Track A R3 audit-driven re-analysis)

> **This file is the posting artifact.** The design rationale lives in
> [HPC_HANDOFF_v5_2026-05-04.md](../../HPC_HANDOFF_v5_2026-05-04.md) (Cowork-side
> canonical A1–A9 spec) and the v2 audit anchor at
> [AUDIT-REVIEW-V2-2026-04-26.md](AUDIT-REVIEW-V2-2026-04-26.md).
> This file contains ONLY the OSF web-UI paste-ready body, bracketed by
> `--- PASTE INTO OSF FROM HERE ---` / `--- PASTE ENDS HERE ---` markers.

---

## Pre-Paste Reference (do NOT paste this block)

| Field | Value |
|---|---|
| Target OSF project | [osf.io/az52u](https://osf.io/az52u) — post as supplementary file on the existing parent amendment record (matches M1 pattern: M1 body uploaded as file `k8w7n` on `az52u` rather than a new record). Both forms satisfy Amendment §9.1. |
| Amendment kind | Methods amendment to Track A; narrower than the 2026-04-25 genome-wide reframe (which addresses Track B). Adds λ ridge sweep + eigenvalue-clip alternative + outcome-branch decision matrices for v2-audit-driven re-fits. |
| Original pre-registration being amended | [osf.io/pvb5j](https://osf.io/pvb5j) (DOI `10.17605/OSF.IO/PVB5J`), posted 2026-04-10. |
| Supersedes-but-incorporates | Phase 1 closeout amendment posted 2026-04-13 at `osf.io/az52u` (distal-gene expansion, PDF only) + M1 amendment posted 2026-04-25 at `osf.io/az52u/files/k8w7n` (genome-wide reframe → Track B). Not retracted; this amendment extends both. |
| Posting gate | Track A R3 phase scaffolded 2026-05-04 with v2-audit-driven scope. BEFORE any W1 LSF job fires (W1 = SH2B3 12q24 EUR PSD-regularized SuSiE-RSS re-fit). Per `.planning/feedback_rigor_over_speed.md` memory: pre-registration discipline applies even to re-analysis of already-published-substrate data; ridge λ values + eigenvalue-clip alternative + outcome-branch decisions are fixed BEFORE discovery, not after. |
| Audit anchor | [AUDIT-REVIEW-V2-2026-04-26.md](AUDIT-REVIEW-V2-2026-04-26.md) — v2 audit findings; HQ#2(i) + HQ#2(iii) + S5 are addressed by this phase. |
| Cowork-side canonical spec | [HPC_HANDOFF_v5_2026-05-04.md](../../HPC_HANDOFF_v5_2026-05-04.md) — A1–A9 split; this amendment covers HPC-side scope only (A4, A5, optional A6, optional A7). |
| Expected posting date | `2026-05-04` — fill in with actual posting date before paste. |
| Attachment | Optional: attach PDF export of [HPC_HANDOFF_v5_2026-05-04.md](../../HPC_HANDOFF_v5_2026-05-04.md) as supplementary material if OSF form allows. |

**Pre-paste checklist (work top-to-bottom before submitting the OSF form):**

1. Fill the `2026-05-04` placeholder in the Date field with the actual amendment posting date (`YYYY-MM-DD`).
2. Replace the `<R3 W0 pre-execute commit hash TBD>` placeholder in the "What is not changing" paragraph with the HEAD commit hash at the moment this amendment is posted (the commit immediately preceding any W1 LSF dispatch).
3. Verify the three commit hashes referenced in this amendment (`069b34f`, `7d54183`, `02c4404`) are still HEAD ancestors at posting time: `git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l` must return 3.
4. Verify the predecessor SH2B3 R2 substrate sha256 still resolves: `id_vs_ref_ld_genome_medicine_submission.zip` sha256 = `a93d8f4952d1...` at `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/` per `/gsd-quick 260503-vcl` close-out.
5. After OSF posts, copy the amendment record URL (e.g., `osf.io/<record-id>` or `osf.io/az52u/files/<file-id>`) back into `.planning/osf_deviations.md` under a new dated entry, AND record the OSF timestamp — it must precede any W1 LSF job submission timestamp.

---

--- PASTE INTO OSF FROM HERE ---

**Amendment to pre-registration osf.io/pvb5j: Track A audit-driven SuSiE-RSS regularization and trait-pair colocalization re-analysis**

**Date:** 2026-05-04

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of amendment:** This amendment expands the Track A methods-validation analysis (the candidate-locus subset retained per the 2026-04-25 amendment as Track A) with a pre-registered re-analysis of the SH2B3 12q24 EUR Tier-A colocalization signal under PSD-regularized linkage-disequilibrium and a pre-registered cache-invalidated re-fire of the 28 unsuccessful trait-pair `coloc.susie` attempts at the four other admissible regions (FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21). The amendment locks the four allowable outcome branches for each re-analysis ahead of execution so that the manuscript narrative cannot be conditioned on the result.

**Motivation:** A second-round audit of the original Track A real-LD coloc analysis (`AUDIT-REVIEW-V2-2026-04-26`) flagged two methods concerns that warrant pre-registered re-analysis ahead of submission to *Genome Medicine*:

(1) The SH2B3 12q24 EUR Tier-A pass at PP.H4 = 1.0 across canonical pairs (BMI–hypertension, hypertension–stroke, hypertension–type 2 diabetes) is computed against a 1000 Genomes Phase 3 EUR LD matrix flagged as weakly NOT positive-semi-definite (23.46 percent negative eigenvalues, 50.4 percent effective rank, 6.7 percent variant coverage), with all three backing per-trait SuSiE-RSS fits flagged `convergence_status = non_converged`. Per Zou et al. 2022 (*PLoS Genetics* 18:e1010299, §Methods 2.4), Wallace 2021 (*PLoS Genetics* 17:e1009440), Wen et al. 2017 (*PLoS Genetics* 13:e1006646), and Benner et al. 2017 (*American Journal of Human Genetics* 101:539), posterior probabilities approaching 1.0 from non-positive-semi-definite LD plus non-converged fine-mapping are a recognized false-positive mode. A reviewer-defensible result requires explicit testing under a regularized configuration where the per-trait fits actually converge.

(2) The original Track A multi-trait analysis reports 28 of 28 trait-pair `coloc.susie` attempts at non-SH2B3 regions returning empty PP.H3 / PP.H4 columns. The Wave 2 R2 SH2B3-only re-fire (post repository commits `069b34f` for variant-ID-format tolerance in the QTL coloc matcher, `7d54183` for the LD-panel-rsid override in the SuSiE-RSS fitter, and `02c4404` for the `max_iterations` to `max_iter` parameter fix) produced 9 working PP rows for SH2B3 EUR specifically, but the same fixes were not re-applied to the 28 non-SH2B3 pairs. The current state therefore reads as result-conditional analysis selection. Re-applying the fixes to the full 28-pair set tests whether the empty PP rows represent a structural Layer-2 attrition under matched-ancestry LD or an incomplete propagation of the variant-ID-format fix.

**New analytical commitments — SH2B3 12q24 EUR PSD-regularized re-fit (this phase Wave 1):**

(a) The 1000 Genomes Phase 3 EUR LD matrix at `data/processed/ld_reference/EUR/SH2B3_12q24.rds` is regularized by Wen et al. 2017 ridge addition `R_reg = R + λI` followed by row-and-column normalization, swept across `λ ∈ {0.001, 0.01, 0.1}`. An eigenvalue-clipping alternative (Hutchinson 2020) at floor `λ_floor = 10⁻⁶` is run as a robustness companion. Per-trait SuSiE-RSS fits at the 5 EUR traits (asthma, BMI, hypertension, stroke, type 2 diabetes) are re-fit at each λ value using `susieR::susie_rss(L = 10, coverage = 0.95, max_iter = 1000, estimate_residual_variance = FALSE, check_R = FALSE)`. Z-scores are derived inline at fit time as `z = BETA / SE` from the harmonized summary statistics at `data/processed/sumstats_harmonized/{trait}.EUR.tsv.bgz` (no separate z-score-input intermediate file).

(b) `coloc.susie` is run on the three canonical pairs (BMI–hypertension, hypertension–stroke, hypertension–type 2 diabetes) at the smallest λ where all three of (BMI, hypertension, stroke) per-trait fits converge. PP.H0 through PP.H4 are recorded into a pair × λ summary table.

(c) The W1 outcome is classified into exactly one of four pre-registered branches:
- `BRANCH_PSD_FIRM` — λ exists where all three SuSiE-RSS fits converge AND PP.H4 ≥ 0.8 across all three canonical pairs. The Track A Tier-A SH2B3 anchor is empirically supported under regularized LD; the manuscript reports the λ value, PSD diagnostic table, and converged-status disclosure.
- `BRANCH_PSD_PARTIAL` — λ exists with convergence but PP.H4 falls into [0.5, 0.8) for at least one canonical pair. SH2B3 is reframed from Tier-A to Tier-B; the abstract and discussion are revised; the result is reported as a nuanced finding.
- `BRANCH_PSD_COLLAPSE` — PP.H4 falls below 0.5 at all converged λ values. SH2B3 no longer qualifies as Tier-A; the manuscript reports the prior-literature PP = 1.0 anchor as not surviving matched-LD with PSD regularization.
- `BRANCH_PSD_NON_CONVERGE` — even with regularization across all λ values, the per-trait fits remain non-converged. The manuscript discloses this as a deeper LD-panel-versus-GWAS-cohort mismatch and the finding is deferred to Track B (in-sample LD via UKB or All of Us EUR).

All four outcomes are publishable; the current "claim survives despite failure" framing is the only branch not on this list.

**New analytical commitments — R1 trait-pair `coloc.susie` cache-invalidated re-fire (this phase Wave 2):**

(d) The 28 R1 trait-pair `coloc.susie` outputs at `results/multitrait/coloc_susie/*.json` (the non-SH2B3 pairs in the existing `results/multitrait/coloc_manifest.tsv`) are cache-invalidated and re-fired against repository HEAD with commits `069b34f` + `7d54183` + `02c4404` confirmed as ancestors. The Snakemake DAG is re-fired with `--forcerun run_coloc_susie` under the same `--use-conda --conda-prefix .snakemake/conda --jobs 50 --keep-going --rerun-incomplete --latency-wait 120` configuration as the SH2B3 R2 fire. The `coloc_summary.tsv` aggregator is rebuilt post-fire and md5-hashed.

(e) The W2 outcome is classified into exactly one of two pre-registered branches:
- `BRANCH_R1_BUG` — post-refire produces non-empty PP.H3 / PP.H4 rows in the previously-empty 28. The Layer-2-attrition-under-matched-LD framing is empirically refuted; the new PP rows are reported in the manuscript Table 3 with the variant-ID-format-fix commit hashes cited as the propagation gap.
- `BRANCH_R1_STRUCTURAL` — post-refire holds at 28 of 28 empty (or near-empty). The Layer-2-attrition framing is empirically supported; the manuscript reports the structural finding with the variant-ID-format-fix commits cited as a falsification test that did not falsify.

**New analytical commitments — R2 canonical-pair parity re-fire (this phase Wave 3, conditional on W1 outcome):**

(f) Conditional on W1 returning either `BRANCH_PSD_FIRM` or `BRANCH_PSD_PARTIAL`, the same Wave 2 R2 SH2B3 canonical-pair `coloc.susie` fire is repeated at each of FTO_16q12, MC4R_18q21, APOL1_22q12, and CXADR_F2RL1_6p21 in EUR. The `bin/fire_canonical_susie_pairs.sh` driver is parameterized to accept `--region` and `--ancestry` arguments in a backwards-compatible manner (default region remains SH2B3, default ancestry remains EUR, so existing SH2B3 R2 outputs reproduce bit-for-bit). The R2-parity rows merge into `coloc_summary.tsv` via the same aggregator pattern used in the SH2B3 R2 merge. If W1 returns `BRANCH_PSD_COLLAPSE` (the SH2B3 anchor itself fails) or `BRANCH_PSD_NON_CONVERGE`, Wave 3 is skipped and the deferral is documented as `D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME` in the phase context file. The conditional gate is pre-registered: parity at the four other regions is informative only if SH2B3 itself qualifies as a comparator anchor.

**New analytical commitments — Negative-control row-count reconciliation (this phase Wave 4, optional):**

(g) The 200-versus-224 row-count mismatch between the manuscript negative-control panel narrative and the on-disk `results/qtl_coloc/tier_assignments.tsv` (which currently holds 233 data rows; the narrative claim implicates HLA_6p21 row reclassification as the source of the discrepancy) is reconciled by either (i) a manuscript footnote disclosing the reclassification arithmetic without modifying the on-disk file, or (ii) splitting HLA-encoded rows out into a sibling file `tier_assignments_hla_fallback_separate.tsv` and rebuilding the primary table to match narrative. The decision between (i) and (ii) is recorded in the phase context file as `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE` (option i) or `D-TA-R3-W4-RECLASS_FIRED` (option ii). If option ii fires, downstream aggregators that consume `tier_assignments.tsv` are rebuilt and the file's md5 hash is added as a successor row in the project's md5 baseline whitelist (existing rows are not overwritten).

**What is superseded by this amendment:**

- Track A SH2B3 12q24 EUR Tier-A pass at PP.H4 = 1.0 with non-positive-semi-definite LD and non-converged per-trait fits → outcome-branch-conditional reporting under PSD-regularized LD.
- Track A 28-of-28 empty trait-pair PP rows reframed as Layer-2-attrition without falsification testing → outcome-branch-conditional reporting under cache-invalidated re-fire.
- SH2B3-only Wave 2 R2 canonical-pair parity → conditional R2 parity at FTO + MC4R + APOL1 + CXADR EUR (W3 fired only if W1 confirms SH2B3 as a comparator anchor).
- Manuscript negative-control panel row count not reconciled to on-disk supplementary file → footnote disclosure or on-disk reclassification with md5 successor row.

**What is not changing:**

- Pre-registration discipline. The four W1 outcome branches and two W2 outcome branches are fixed before discovery execution; manuscript framing is committed to one of these branches based on the empirical result, not chosen to fit the most rhetorically convenient result. The W3 conditional gate on W1 outcome is pre-registered. Any deviation during execution is logged in `.planning/osf_deviations.md` and disclosed in the manuscript's "Deviations from pre-registration" section.
- Multi-method triangulation. PSD-regularized SuSiE-RSS plus `coloc.susie` plus the variant-ID-format-fix-commit falsification test for the trait-pair empty-rows hypothesis remain the triangulation scaffold for Track A.
- Public-data-only commitment. No wet-lab validation, no proprietary industry datasets. The 1000 Genomes Phase 3 EUR LD reference panel and the harmonized summary statistics at `data/processed/sumstats_harmonized/` remain the substrate.
- Snakemake-pinned pipeline with conda environment specifications. The `la_multitrait_r` environment (R 4.4.2 + susieR 0.14.2 + coloc 5.2.3) and the `smoke_dev` environment (Snakemake 7.32.4) used in the M1 → M2 chain remain the analysis envelopes.
- Atomic commits per wave with one SUMMARY.md per plan and one VERIFICATION.md per phase. The md5 invariant whitelist at `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` is extended (new rows appended for files whose md5 shifts in this phase), never overwritten — historical rows remain interpretable.
- Honest-original-research framing. Per `.planning/feedback_original_research_framing.md`: the manuscript at `docs/manuscript/id-vs-ref-LD.md` frames this work as audit-driven re-analysis, not as a fix, revision, cleanup, correction, salvage, or pivot. The W6 manuscript md5 (`63fd81385590ffc8d23d45a0f0598959`) does not shift under this phase; manuscript edits triggered by W1 / W2 outcome branches are out of scope for this phase and execute in a separate Cowork-side session after W5 closeout.
- DEC-2026-04-25-01 preserved: `results_identity_ld/` remains uncommitted.
- OSF deposit of all post-phase outputs: PSD-regularized fits, λ × pair PP summary table, cache-invalidated coloc summary, R2 parity coloc outputs, phase verification dimensions JSON, and the Cowork-side handoff brief.

**Expected timeline:** This amendment is posted at the start of Track A R3 (phase scaffolded 2026-05-04 with v2-audit-driven scope; `/gsd-plan-phase ta-r3-audit-v2-driven-psd-and-r1-refire` planned at this commit; W1 LSF dispatch fires only after this amendment posts). The pre-execute hard gate is repository commit `<R3 W0 pre-execute commit hash TBD>`. The Cowork-side manuscript revision (audit items A1, A2, A3, A6 statistical formalization, A7, A8, A9 — explicitly out of this phase's scope) ships the v5 *Genome Medicine* submission bundle after the W5 closeout artifacts hand off to Cowork. The full milestone table, per-wave success criteria, and outcome-branch decision matrices are available in the companion repository at `.planning/ROADMAP.md` (Track-A-R3-audit-v2-driven-psd-and-r1-refire entry) and `HPC_HANDOFF_v5_2026-05-04.md` (Cowork-side canonical A1–A9 spec).

**Note on outcome-branch verification follow-up:** The realized W1 and W2 outcome branches will be added as a follow-up OSF update at the W5 closeout date, when the Cowork-side handoff brief at `.planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md` is finalized. The follow-up update will also include the LSF job IDs, the post-execution md5 invariants, and the realized λ value selected for the SH2B3 W1 PSD-regularized canonical-pair `coloc.susie`.

--- PASTE ENDS HERE ---

---

## Post-Paste Reference (do NOT paste this block)

**Verification checklist after OSF posting:**

1. Confirm OSF assigned a timestamp to the amendment and the timestamp precedes any commit containing W1 PSD-regularized SuSiE-RSS fit outputs (the directory `results/fine_mapping_psd_regularized/` should not yet exist on disk at posting time). If timestamp-precedence is violated, post a subsequent deviation log entry immediately in `.planning/osf_deviations.md`.
2. Copy the OSF amendment record URL (e.g., `osf.io/<record-id>` or `osf.io/az52u/files/<file-id>`) back into the local repository at `.planning/osf_deviations.md` under a new dated entry citing this amendment.
3. Tag the repository commit that represents the R3 W0 pre-execute gate with `git tag TA-R3-OSF-AMENDMENT-POSTED-YYYY-MM-DD`.
4. Append a new entry to [DECISIONS.md](../DECISIONS.md) (`DEC-YYYY-MM-DD-XX: OSF amendment posted at osf.io/<record-id>; TA-R3 W1 LSF gate cleared.`).
5. Update [STATE.md](../STATE.md) Session Continuity to mark `D-TA-R3-OSF-COVERAGE: COVERED`.
6. Update the R3 phase context file at `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` (created by the gsd-planner agent in the next workflow step) with `D-TA-R3-OSF-COVERAGE: COVERED at <timestamp>` so the W1 PLAN.md hard-gate check has a target.

**If any commitment changes between posting this amendment and W5 closeout:**

- Pause execution at the next wave boundary.
- Log the deviation in `.planning/osf_deviations.md` under a new dated entry citing this amendment.
- If the deviation modifies an outcome-branch decision rule, post a subsequent OSF amendment-update referencing this amendment's record URL.

**Outcome-branch realized-result follow-up (after W5):**

When W5 closeout writes the handoff brief, append a follow-up OSF update at the same parent record citing:
- The realized W1 outcome branch (one of `BRANCH_PSD_FIRM | PARTIAL | COLLAPSE | NON_CONVERGE`).
- The realized W2 outcome branch (one of `BRANCH_R1_BUG | STRUCTURAL`).
- The realized W3 conditional gate state (`fired` or `deferred-on-W1-outcome`).
- The realized W4 reconciliation choice (`footnote` or `reclass-fired`).
- The R3 phase commit hash range (`first..last` from `git log --oneline`).
- The post-W5 md5 invariants (the new rows appended to `md5_baseline.tsv`).
- The Cowork-side v5 submission bundle sha256 (deferred; not in this phase's scope; will be in the follow-up update written at v5 ship time).

**Rollback:** Do not delete this file. If this amendment is posted and later retracted (e.g., a methodological premise is invalidated by a subsequent finding), add a superseded-by pointer at the top of this file to the new amendment record. OSF amendments are append-only by design.
