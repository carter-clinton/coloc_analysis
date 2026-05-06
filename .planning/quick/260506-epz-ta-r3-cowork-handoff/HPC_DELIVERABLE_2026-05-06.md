# HPC Deliverable — Track A R3 Audit-Driven Re-analysis (HPC-side closeout)

**Phase:** `ta-r3-audit-v2-driven-psd-and-r1-refire`
**Closeout:** 2026-05-06
**OSF amendment:** [.planning/amendments/osf-amendment-r3-2026-05-04.md](../../amendments/osf-amendment-r3-2026-05-04.md) (parent record [osf.io/az52u](https://osf.io/az52u); amendment text committed locally; OSF web-UI posting OVERRIDDEN per operator decision 2026-05-05 — see "Disclosure" section below)
**Cowork-side scope (NOT in this deliverable):** A1 / A2 / A3 / A6-stats / A7 / A8 / A9 manuscript edits + v5 *Genome Medicine* submission bundle ship + OSF outcome-branch follow-up update + (per Disclosure decision below) retroactive OSF amendment posting OR v5-cover-letter pre-registration limitation disclosure. Execute after this handoff lands in a separate Cowork-side session.

---

## Honest-Framing-Lock Reminder

Per [.planning/feedback_original_research_framing.md](../../feedback_original_research_framing.md): every artifact this phase + Cowork-side touched frames the work as **"audit-driven re-analysis"**, NOT "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot". The Track A id-vs-ref-LD manuscript narrative survives unchanged through all 5 waves. Manuscript md5 = `2a57c1a061f0c66988a55d1d6600efdf` at phase entry AND exit (byte-identical).

---

## Phase Headline Finding

The audit-V2 §HQ#2(i)/(ii)/(iii)/(g) reviewer concerns are all addressed empirically. SH2B3 12q24 EUR Tier-A anchor SURVIVES under PSD-regularized LD (W1 FIRM), the SH2B3-only outcome is REPRODUCIBLE under symmetric pipeline application (W3 0/6 elsewhere — Layer-2 attrition extends to canonical non-SH2B3 pairs), and the empty-PP layer is STRUCTURAL not cache-staleness (W2 28/28 still empty after re-fire under HEAD with all 3 variant-ID-format-fix commits as ancestors). The Track A id-vs-ref-LD manuscript narrative survives unchanged.

---

## Wave Outcome Branches (pre-registered in OSF amendment paragraphs (c) + (e) + (f) + (g))

| wave | outcome | implication |
|------|---------|-------------|
| W1 | `BRANCH_PSD_FIRM` | SH2B3 anchor empirically supported under regularized LD. Manuscript reports primary lambda=0.01, PSD diagnostic table (negative_eig_pct=23.4637 within 0.0037pp of v2-audit baseline 23.46%), and converged-status disclosure (5/5 per-trait fits converged at primary lambda; 3/3 canonical pair PP.H4 = 1.000000). The OSF amendment paragraph (c) decision-matrix cells `BRANCH_PSD_PARTIAL` / `BRANCH_PSD_COLLAPSE` / `BRANCH_PSD_NON_CONVERGE` did not fire. |
| W2 | `BRANCH_R1_STRUCTURAL` | Layer-2-attrition framing empirically supported across the 28 non-SH2B3 R1 trait-pairs at non-Tier-A regions. R1_non_empty_PP.H4_rows = 0 of 28 post-refire (Δ=0 vs pre-W2 baseline of 0/28). Variant-ID-format-fix commits 069b34f + 7d54183 + 02c4404 confirmed as HEAD ancestors at re-fire time AND at post-fire commit time. The OSF amendment paragraph (e) decision-matrix cell `BRANCH_R1_BUG` did not fire. The reviewer-defensible re-application of fix commits to the full 28-pair set produces zero new PP rows; the structural framing in the manuscript Discussion §"Layer-2 colocalization-feasibility yield" + Discussion §"Identity-LD Inflation" + Limitations bullet 5 survives. |
| W3 | `OUTCOME` = 0 of 6 W3 canonical pairs surviving PP.H4 ≥ 0.8 | Layer-2 attrition consistent with W2 BRANCH_R1_STRUCTURAL extends to canonical pairs at non-SH2B3 regions × EUR ancestry under matched-LD. SH2B3 12q24 EUR remains the only surviving Tier-A signal across the 5 admissible regions × canonical-pair set. Manuscript narrative for Cowork side: "Of 9 canonical pairs across 5 admissible regions (3 SH2B3 + 6 W3), 3 survive at PP.H4 ≥ 0.8 under matched-LD — all 3 at SH2B3 12q24 EUR anchor." Per-region detail: FTO_16q12=0/3 (1 status=error), MC4R_18q21=0/1, APOL1_22q12=0/1, CXADR_F2RL1_6p21=0/1. |
| W4 | `DEFERRED_TO_FOOTNOTE` | tier_assignments.tsv on-disk file UNTOUCHED (md5 17ff46db... at entry = exit). HLA exclusion canonical mechanism = `neg_ctrl_set == "hla_immune"` column flag (24 rows; matches v5 narrative referent EXACTLY); HLA_6p21 region itself has empty `canonical_pairs` in regions_curated.csv. Cowork-side A9 footnote prose recorded verbatim in [ta-r3-CONTEXT.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md) for v5 manuscript revision. The OSF amendment paragraph (g) decision-matrix cell `RECLASS_FIRED` did not fire. |

---

## Disclosure — OSF Amendment Posting Status (D9 WARN dimension)

**State:** `D-TA-R3-OSF-COVERAGE = OVERRIDDEN at 2026-05-05T13:49:10Z` (operator decision; OSF web-UI posting deferred). The amendment text was authored and committed locally at [.planning/amendments/osf-amendment-r3-2026-05-04.md](../../amendments/osf-amendment-r3-2026-05-04.md) BEFORE any W1 LSF dispatch fired — so the analytical pre-registration discipline holds (lambda values + outcome-branch decision matrices + convergence criteria were locked on disk pre-discovery). What did NOT happen: the public OSF posting via the web-UI workflow on osf.io/az52u.

**Recorded:** [.planning/osf_deviations.md](../../osf_deviations.md) L37-60 entry under "Deviations (OSF amendment required)" + DECISIONS.md row `DEC-2026-05-05-osf-r3-defer`.

**Cowork-side disclosure decision required (one of two paths):**

| option | action | best-fit if |
|--------|--------|-------------|
| (a) **Retroactive OSF posting** | Post the amendment text + the realized W1/W2/W3/W4 outcome-branch follow-up update (per OSF amendment "Note on outcome-branch verification follow-up") to osf.io/az52u BEFORE submitting the v5 *Genome Medicine* bundle. The OSF timestamp will postdate W1 LSF dispatch (2026-05-05T13:49:10Z), but the amendment text on disk predates dispatch. Disclose this timing in a v5 cover-letter footnote: "The amendment was authored 2026-05-04, applied to disk before any W1 compute fired, and retroactively posted to OSF on YYYY-MM-DD" — rigor-defensible per [.planning/feedback_rigor_over_speed.md](../../feedback_rigor_over_speed.md). | The reviewer / editor places weight on the OSF web-UI timestamp specifically. |
| (b) **v5 cover-letter pre-registration-timing limitation** | Skip retroactive OSF posting; disclose the OSF posting override in the v5 cover letter as a pre-registration-timing limitation. The amendment text on disk + the deviation entry in osf_deviations.md + DECISIONS.md row are the authoritative substrate; the v5 cover letter notes that the amendment was authored pre-execute and committed locally, but the public OSF posting was deferred per operator decision. | Cowork-side editorial judgment is that the in-tree audit trail (amendment text + osf_deviations entry + DECISIONS.md row + this VERIFICATION.md D9 dimension) is sufficient transparency without retroactive OSF web-UI workflow effort. |

Either path is rigor-defensible; option (a) is the stricter route. This is a Cowork-side editorial decision, NOT an HPC-side compute decision; the HPC-side job is to surface the override and provide the substrate for either path.

---

## Phase Commit Hash Range

**First commit (W1 scaffold):** `bccd0d6` — feat(ta-r3, W1): scaffold ta-r3-CONTEXT.md + Wen 2017 ridge / Hutchinson 2020 eigclip fitter + verify LD pathology baseline (audit-driven re-analysis)

**Last commit (W5 closeout):** `eebdc2f` (Task 1 of W5; full W5 commit range will close after Tasks 2 + 3 land).

**Per-wave atomic commits:**

### Wave 1 (SH2B3 PSD-regularized re-fit)

| commit | scope |
|--------|-------|
| `bccd0d6` | scaffold CONTEXT.md + Wen 2017 ridge / Hutchinson 2020 eigclip fitter + LD pathology baseline |
| `728d760` | failing-test-first regression for variant-ID bridge |
| `ad19818` | chr:pos↔rsid bridge utility + wire into PSD-regularized fitter |
| `12274a2` | bug-fix addendum + 12-job redispatch (jobs 119067-119078) |
| `ce4e074` | drain confirmation — all 12 redispatched fits landed |
| `6a221fa` | archive ta_r3_w1_snp_id_overlap_zero debug session |
| `3886d14` | record D-TA-R3-W1-BRANCH_PSD_FIRM + W3 gate FIRES (primary lambda=0.01; canonical-pair PP.H4 table) |
| `3aeac5d` | finalize SUMMARY (D-TA-R3-W1-BRANCH_PSD_FIRM) + STATE.md refresh |

### Wave 2 (R1 trait-pair cache-invalidated re-fire)

| commit | scope |
|--------|-------|
| `03716d9` | identify 28 R1 R-pair targets + pre-W2 baseline + R1 cache mv-backup |
| `d9707df` | cache-invalidate + Snakemake re-fire 28 R1 trait-pair coloc.susie targets (HEAD = 069b34f + 7d54183 + 02c4404) |
| `03335a4` | record D-TA-R3-W2-BRANCH_R1_STRUCTURAL (R1 non-empty=0/28; SH2B3 R2 non-empty=5/9) |
| `a06dcdf` | finalize SUMMARY (D-TA-R3-W2-BRANCH_R1_STRUCTURAL) + STATE.md refresh |

### Wave 3 (R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR EUR)

| commit | scope |
|--------|-------|
| `71abb77` | parameterize fire_canonical_susie_pairs.sh additively (--region + --ancestry; default SH2B3 EUR backwards-compatible) + ancestry-keyed regions_curated.csv |
| `d79fa1a` | R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR EUR + merge_r2_into_summary.R aggregator (0/6 surviving — Layer-2 attrition consistent with W2 BRANCH_R1_STRUCTURAL) |
| `4e9ed81` | finalize SUMMARY (D-TA-R3-W3-OUTCOME = 0/6 surviving) + STATE.md / ROADMAP.md refresh |

### Wave 4 (tier_assignments HLA reconcile — DEFERRED)

| commit | scope |
|--------|-------|
| `4ab6a51` | SKIPPED — D-TA-R3-W4-DEFERRED_TO_FOOTNOTE; row-count reconciliation via Cowork-side A9 footnote |
| `2cb6b82` | complete W4-tier-assignments-hla-reconcile plan — SUMMARY + STATE + ROADMAP closeout |

### Wave 5 (closeout + Cowork handoff — this wave)

| commit | scope |
|--------|-------|
| `eebdc2f` | append 8 successor md5 rows for W1-W3 file shifts (NEVER overwrite W7 baseline; audit-driven re-analysis) |
| `<this commit>` | write VERIFICATION.md (D1-D13 PASS/WARN/FAIL) + Cowork-side handoff brief at .planning/quick/260506-epz-ta-r3-cowork-handoff/ + osf_deviations.md W5 closeout entry |
| `<task 3 commit>` | close phase ROADMAP.md status + STATE.md refresh + D-TA-R3-W5-PHASE-CLOSURE in CONTEXT.md |

**Recorded full commit range:** `bccd0d6..<W5 task 3 commit>` — exact hash captured in the W5 SUMMARY post-Task 3.

---

## LSF Job IDs (for cross-reference with bjobs/bhist post-closeout)

### W1 dispatch (15 PSD-regularized SuSiE-RSS fits)

**Original dispatch (15 jobs; 9 of 15 failed at variant-ID-bridge gate):**

```
asthma:       115619 (l=0.001), 115621 (l=0.01), 115622 (l=0.1)   — 3/3 landed
bmi:          115624 (l=0.001), 115626 (l=0.01), 115627 (l=0.1)   — 3/3 landed
hypertension: 115629 (l=0.001), 115631 (l=0.01), 115632 (l=0.1)   — 0/3 — variant-ID overlap gate FAILED
stroke:       115634 (l=0.001), 115636 (l=0.01), 115637 (l=0.1)   — 0/3 — variant-ID overlap gate FAILED
t2d:          115639 (l=0.001), 115641 (l=0.01), 115643 (l=0.1)   — 0/3 — variant-ID overlap gate FAILED
```

**Redispatch after variant-ID-bridge fix (12 jobs; bmi×3 skipped — binary-identical):**

```
asthma:       119067 (l=0.001), 119068 (l=0.01), 119069 (l=0.1)
hypertension: 119070 (l=0.001), 119071 (l=0.01), 119072 (l=0.1)
stroke:       119073 (l=0.001), 119074 (l=0.01), 119075 (l=0.1)
t2d:          119076 (l=0.001), 119077 (l=0.01), 119078 (l=0.1)
```

**Drain confirmation:** all 12 redispatched fits landed by 2026-05-06; 15/15 .fit.rds verified on disk under bridged code path. Forensic dispatch log: [logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log](../../../logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log).

### W2 dispatch (Snakemake DAG-confined; 28 R1 trait-pair coloc.susie targets)

**Snakemake invocation:** `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --profile config/cluster_lsf --use-conda --conda-prefix .snakemake/conda --jobs 50 --keep-going --rerun-incomplete --latency-wait 120 --forcerun run_coloc_susie --until run_coloc_susie`

**Wall envelope:** ~9 min (2026-05-06T14:13:00Z → 2026-05-06T14:22:17Z). Most jobs returned quickly under coloc.susie status="no_signal" (n_cs_a=0 OR n_cs_b=0 short-circuits the call).

**Forensic dispatch log:** [logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log](../../../logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log).

### W3 dispatch (synchronous per-pair Rscript; Snakemake LSF profile bypassed per overlay yaml NOTE option (a))

**6 pairs dispatched synchronously:** FTO_16q12 EUR × {bmi-htn, bmi-t2d, htn-t2d}; MC4R_18q21 EUR × bmi-t2d; APOL1_22q12 EUR × hypertension-stroke; CXADR_F2RL1_6p21 EUR × bmi-hypertension.

**Wall envelope:** ~3 min total (synchronous per-pair Rscript dispatch is far faster than the projected ~3 hr LSF envelope because no LSF queueing overhead and coloc.susie returns quickly when CS vacancy short-circuits the call).

**Forensic dispatch log:** [logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log](../../../logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log).

### W4 (no LSF — local investigation only)

W4 is a local investigation pass; no LSF jobs fired (DEFERRED branch). Investigation log: [logs/ta_r3_W4_hla_reconcile/hla_reconcile.log](../../../logs/ta_r3_W4_hla_reconcile/hla_reconcile.log).

---

## md5 Invariants (post-W5 baseline)

**Manuscript md5 (honest-framing-lock):** `2a57c1a061f0c66988a55d1d6600efdf` — UNCHANGED through all 5 waves. (NOT the stale plan-mode literal `63fd81385590ffc8d23d45a0f0598959` that appears in PLAN.md frontmatter — that literal was cached by the planner against an older snapshot of the manuscript and is explicitly superseded per CLAUDE.md critical_constraints rule 1.)

**md5_baseline.tsv successor rows appended (W7 baseline preserved verbatim per Pitfall 5; never overwritten):**

```bash
awk -F'\t' '$3 ~ /\(ta-r3\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
```

Returns 8 successor rows (one per file whose md5 shifted in W1/W2/W3 + new files created in W1/W3):

| file | md5 | wave / rationale |
|------|-----|------------------|
| `results/multitrait/coloc_summary.tsv` | `073f8c0577c366647ea7952b7c39a152` | W2-W3 chain: 558fca45 (W7) → 85ab5aa2 (post-W2) → 073f8c05 (post-W3 R2-canonical-pair-parity merge) |
| `src/R/regularization/refit_sh2b3_psd_regularized.R` | `4a480e4d95c39657d6d2a2b0198cffe1` | W1 NEW: Wen 2017 ridge + Hutchinson 2020 eigclip fitter |
| `src/R/regularization/snp_id_bridge.R` | `86592b36dd1bef1f97a2bde5ba34a44c` | W1 NEW: chr:pos↔rsid variant-ID bridge utility (factored from run_susie_rss.R commit 7d54183 pattern) |
| `src/R/aggregators/merge_r2_into_summary.R` | `29480b7bf063ef2d241792595b676ba7` | W3 NEW: UPSERT-by-pair_id merge across 5 R2 directories |
| `bin/fire_canonical_susie_pairs.sh` | `dfe39a5efce06946ce68014beba7afa3` | W3 additive `--region` + `--ancestry` parameterization (default SH2B3 EUR backwards-compatible) |
| `config/regions_curated.csv` | `313ec434c7b68db4e9fa36b425ba5b15` | W3 added 4 EUR region rows (FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21) + ancestry + canonical_pairs columns |
| `results/multitrait/coloc_manifest_R2.tsv` | `262205a088f0d18a8e3cda9e7dce57ef` | W3 extended 9 → 15 rows (9 SH2B3 R2 baseline preserved + 6 W3 canonical pair_ids appended) |
| `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` | `19c8fa0481624cb254e1f18f0263fc51` | W1-W4 phase context: D-TA-R3-OSF-COVERAGE OVERRIDDEN + W1 BRANCH_PSD_FIRM + W2 BRANCH_R1_STRUCTURAL + W3 OUTCOME 0/6 + W4 DEFERRED_TO_FOOTNOTE decision tokens |

`tier_assignments.tsv` md5 `17ff46dbbfe78dd537d6b9bff7f3ae67` — UNCHANGED (W4 DEFERRED path; no successor row needed).

**Pre-append:** 30 lines. **Post-append:** 38 lines. **Duplicate lines:** 0. **W7 baseline rows preserved:** verbatim per Pitfall 5.

---

## Artifact Paths (for Cowork-side v5 manuscript revision)

### W1 PSD-regularized re-fit substrate

- **15 PSD-regularized SuSiE-RSS fits:** [results/fine_mapping_psd_regularized/{asthma,bmi,hypertension,stroke,t2d}.EUR.SH2B3_12q24.lambda{0.001,0.01,0.1}.fit.rds](../../../results/fine_mapping_psd_regularized/) (5 traits × 3 lambdas)
- **9-row pair × lambda × PP table:** [results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv](../../../results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv) (3 canonical pairs × 3 lambdas)
- **LD pathology baseline:** [results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv](../../../results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv) (negative_eig_pct=23.4637 within 0.0037pp of v2-audit baseline 23.46%; load-bearing PSD-pathology metric)
- **PSD-regularized fitter:** [src/R/regularization/refit_sh2b3_psd_regularized.R](../../../src/R/regularization/refit_sh2b3_psd_regularized.R) + [src/R/regularization/snp_id_bridge.R](../../../src/R/regularization/snp_id_bridge.R) (chr:pos↔rsid bridge utility)
- **W1 SUMMARY:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W1-sh2b3-psd-regularized-refit-SUMMARY.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W1-sh2b3-psd-regularized-refit-SUMMARY.md)

### W2 R1 cache-invalidated re-fire substrate

- **28 R1 trait-pair coloc.susie JSONs (post 069b34f + 7d54183 + 02c4404 cache invalidation):** results/multitrait/coloc_susie/*.json (gitignored — regenerable from manifest + HEAD code)
- **R1 cache pre-W2 mv-backup (rollback path):** results/multitrait/coloc_susie.preFix.bak.20260506_141119Z/ (gitignored — Pitfall 5 timestamped backup)
- **Pre-W2 baseline + post-W2 outcome TSVs:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-{pre_refire_baseline,post_refire_outcome,post_refire_md5,r1-targets,backup-path}.tsv](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/) (5 forensic artifacts)
- **W2 SUMMARY:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md)

### W3 R2 canonical-pair parity substrate

- **W3 R2-parity outputs (per-region):** results/multitrait/coloc_susie_R2_FTO/{FTO_16q12__EUR__bmi_vs_hypertension,FTO_16q12__EUR__bmi_vs_t2d,FTO_16q12__EUR__hypertension_vs_t2d}.json + results/multitrait/coloc_susie_R2_MC4R/MC4R_18q21__EUR__bmi_vs_t2d.json + results/multitrait/coloc_susie_R2_APOL1/APOL1_22q12__EUR__hypertension_vs_stroke.json + results/multitrait/coloc_susie_R2_CXADR/CXADR_F2RL1_6p21__EUR__bmi_vs_hypertension.json
- **W3 R2-parity outputs (canonical R2 namespace; 15 rows = 9 SH2B3 + 6 W3):** results/multitrait/coloc_susie_R2/*.json
- **R2 merge aggregator:** [src/R/aggregators/merge_r2_into_summary.R](../../../src/R/aggregators/merge_r2_into_summary.R)
- **Parameterized canonical-pair driver:** [bin/fire_canonical_susie_pairs.sh](../../../bin/fire_canonical_susie_pairs.sh) (additive --region + --ancestry; default SH2B3 EUR backwards-compatible)
- **Region manifest (extended 9 → 15 rows):** [results/multitrait/coloc_manifest_R2.tsv](../../../results/multitrait/coloc_manifest_R2.tsv)
- **Region config (4 new EUR rows):** [config/regions_curated.csv](../../../config/regions_curated.csv)
- **W3 SUMMARY:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W3-r2-canonical-pair-parity-SUMMARY.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W3-r2-canonical-pair-parity-SUMMARY.md)

### W4 HLA reconcile substrate (DEFERRED)

- **Investigation TSV:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv) (35 lines; HLA encoding enumeration + row-count decomposition + Cowork-side A9 footnote prose recommendation)
- **A9 footnote prose:** recorded verbatim in [ta-r3-CONTEXT.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md) under D-TA-R3-W4-DEFERRED_TO_FOOTNOTE block (canonical handoff text for v5 manuscript revision)
- **tier_assignments.tsv:** UNTOUCHED (md5 17ff46db... at entry = exit)
- **W4 SUMMARY:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md)

### Phase-wide artifacts

- **Rebuilt cross-pair summary (R1 + R2 + W3; 40 rows; md5 073f8c05...):** [results/multitrait/coloc_summary.tsv](../../../results/multitrait/coloc_summary.tsv)
- **Phase context (all decision tokens):** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md) — D-TA-R3-OSF-COVERAGE + D-TA-R3-W1-BRANCH_PSD_FIRM + D-TA-R3-W2-BRANCH_R1_STRUCTURAL + D-TA-R3-W3-GATE FIRES + D-TA-R3-W3-OUTCOME (0/6) + D-TA-R3-W4-DEFERRED_TO_FOOTNOTE
- **Phase verification:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md](../../phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md) — D1-D13 PASS/WARN/FAIL JSON evidence
- **md5 invariants whitelist (W7 baseline + 8 ta-r3 successor rows):** [.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv](../../phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv)
- **OSF amendment text (committed locally; posting OVERRIDDEN):** [.planning/amendments/osf-amendment-r3-2026-05-04.md](../../amendments/osf-amendment-r3-2026-05-04.md)
- **OSF deviations log:** [.planning/osf_deviations.md](../../osf_deviations.md) (TA-R3 override entry under "Deviations (OSF amendment required)")

### Submission bundle (NOT in this deliverable; Cowork-side scope)

The v5 *Genome Medicine* submission bundle will be rebuilt via [bin/build_id_vs_ref_ld_submission_bundle.sh](../../../bin/build_id_vs_ref_ld_submission_bundle.sh) against post-W5 disk numbers, with a fresh SHA-256 manifest. This step executes in a Cowork-side session AFTER this handoff lands and after the Cowork-side A1-A9 manuscript edits ship.

---

## Cowork-side TODO list (informational; OUT of HPC scope)

The following items are explicitly OUT of this phase's scope per the OSF amendment "What is not changing" paragraph and per [.planning/feedback_original_research_framing.md](../../feedback_original_research_framing.md). Cowork-side execution after this handoff lands:

1. **A1 / A2 / A3:** Manuscript text edits (re-title disclosures, captions, references) — frame as "audit-driven re-analysis" verbiage NOT "fix" / "revision" / "cleanup".
2. **A6 statistical formalization:** McNemar, bootstrap, BH-FDR per audit-V2 statistical recommendations.
3. **A7:** Redact internal-state-machine references in the manuscript.
4. **A8:** Promote Fig S2 to main-text Fig 4.
5. **A9 footnote:** Negative-control narrative — uses W4 DEFERRED_TO_FOOTNOTE prose recorded verbatim in CONTEXT.md as the canonical handoff text. Wording (verbatim from W4 SUMMARY): "The supplementary tier_assignments.tsv table encodes HLA exclusion via the `neg_ctrl_set == \"hla_immune\"` flag (24 rows; canonical mechanism). The HLA_6p21 region is curated in `config/regions_curated.csv` with an empty `canonical_pairs` list, so the upstream pipeline correctly fires no positional coloc rows for HLA_6p21 itself. The manuscript narrative's '224 disk rows minus 24 HLA = 200 non-HLA' arithmetic was anchored to the pre-W3 aggregator baseline; the post-W3 audit-driven re-analysis substrate has 233 disk rows (224 negative-control + 9 Tier C), and the 200 non-HLA referent is updated to 209 non-HLA in the audit-driven re-analysis. The data-integrity invariant (HLA-class exclusion via the per-region `canonical_pairs` policy at `config/regions_curated.csv`) holds at file level; no on-disk reclassification is performed in this audit-driven re-analysis pass."
6. **v5 submission bundle ship:** Build via [bin/build_id_vs_ref_ld_submission_bundle.sh](../../../bin/build_id_vs_ref_ld_submission_bundle.sh) against post-W5 disk numbers; SHA-256 manifest update; OSF deviation log entry; submit to *Genome Medicine* portal.
7. **OSF outcome-branch follow-up update:** Append realized W1/W2/W3/W4 outcomes to osf.io/az52u parent record per OSF amendment "Note on outcome-branch verification follow-up" paragraph. Include lambda value (0.01), LSF job ID range (115619-115643 + 119067-119078), post-W5 md5 invariants (the 8 ta-r3 successor rows above), and v5 submission bundle SHA-256.
8. **OSF amendment posting decision (D9 WARN follow-up; see Disclosure section above):** Decide between option (a) retroactive OSF posting + cover-letter timing footnote, OR option (b) v5 cover-letter pre-registration-timing limitation. Either path is rigor-defensible; option (a) is stricter.

---

## Honest-Framing-Lock Reminder (final)

Per [.planning/feedback_original_research_framing.md](../../feedback_original_research_framing.md): every artifact this phase + the Cowork-side v5 revision touches frames the work as **"audit-driven re-analysis"**, NOT "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot". The Track A id-vs-ref-LD manuscript narrative survives unchanged; the audit-V2 reviewer concerns are addressed empirically through the 4 wave outcomes (W1 BRANCH_PSD_FIRM + W2 BRANCH_R1_STRUCTURAL + W3 0/6 + W4 DEFERRED_TO_FOOTNOTE). Manuscript md5 = `2a57c1a061f0c66988a55d1d6600efdf` at phase entry AND exit (byte-identical).
