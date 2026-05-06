---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 4
slug: W4-tier-assignments-hla-reconcile
status: DONE
branch: DEFERRED_TO_FOOTNOTE
subsystem: track-a-audit-driven-re-analysis
tags: [audit-v2-driven, w4-skipped, deferred-to-footnote, hla-reconciliation, tier-assignments, cowork-handoff, a9-footnote, honest-framing-lock]
requires:
  - results/qtl_coloc/tier_assignments.tsv (read-only inspection target; 233 data rows; md5 17ff46dbbfe78dd537d6b9bff7f3ae67)
  - config/regions_curated.csv (HLA_6p21 line 12; empty canonical_pairs)
  - .planning/amendments/osf-amendment-r3-2026-05-04.md (W4 gate spec; option (i) footnote default; option (ii) reclass)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W4-GATE token at entry: PENDING with default DEFERRED_TO_FOOTNOTE)
  - .planning/feedback_failed_to_honest_finding.md (HONEST_FINDING re-disposition memory; informs footnote-vs-reclass decision)
provides:
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv (35-line investigation: row count + HLA encoding enumeration + region-id distribution + reconciliation interpretation + Cowork-side A9 footnote prose recommendation)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W4-GATE: PENDING -> SKIPPED + D-TA-R3-W4-DEFERRED_TO_FOOTNOTE block with full investigation summary + Cowork-side A9 footnote prose recommendation)
  - logs/ta_r3_W4_hla_reconcile/hla_reconcile.log (34-line investigation log; gitignored per project convention)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md (this file; closeout)
affects:
  - downstream W5 (closeout brief + Cowork handoff) — must reference D-TA-R3-W4-DEFERRED_TO_FOOTNOTE outcome AND surface the A9 footnote prose recommendation in the v5 manuscript narrative branch
  - Cowork-side A9 manuscript footnote (OUT of phase scope; informational handoff text recorded in CONTEXT.md verbatim for v5 revision)
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv — NO successor row appended (file unchanged; DEFERRED path preserves the W7 baseline as-is)
tech-stack:
  added: []
  patterns:
    - HONEST_FINDING re-disposition pattern (per .planning/feedback_failed_to_honest_finding.md memory) — when a row-count discrepancy investigation reveals the on-disk encoding is correct AND the narrative-vs-disk mismatch is fully attributable to legitimate substrate growth, the rigor-preserving outcome is footnote-disclosure, NOT silent on-disk rewrite to match a stale narrative baseline
    - Investigation-first deferral — TSV investigation is mandatory regardless of branch (footnote-suffices vs reclass-needed); the TSV is the canonical source of truth for the Cowork-side A9 footnote text
    - awk + grep based row-count + neg_ctrl_set enumeration (no LSF; ~5 min wall)
    - Multi-encoding HLA grep (HLA_6p21, HLA-DRB1, HLA_DRB1, MHC, chr6:25-35Mb range) to falsify the "HLA encoded as region_id substring" hypothesis before defaulting to the canonical neg_ctrl_set encoding
    - Pre-W3 baseline arithmetic check (224 - 24 = 200) vs post-W3 substrate state (233 - 24 = 209) to attribute the 9-row drift to legitimate W3 R2 fire vs aggregator corruption
    - Honest-framing-lock invariant verification at entry + exit (manuscript md5 unchanged; tier_assignments.tsv md5 unchanged)
key-files:
  created:
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv (35 lines; investigation deliverable)
    - logs/ta_r3_W4_hla_reconcile/hla_reconcile.log (34 lines; gitignored per logs/* rule)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md (this file; closeout)
  modified:
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W4-GATE: PENDING -> SKIPPED + D-TA-R3-W4-DEFERRED_TO_FOOTNOTE block appended with investigation summary + Cowork-side A9 footnote prose recommendation)
    - .planning/STATE.md (stopped_at + last_updated + last_activity refresh per feedback_state_md_keep_current.md memory)
    - .planning/ROADMAP.md (W4 plan progress updated to completed via gsd-tools)
  untouched_critical:
    - results/qtl_coloc/tier_assignments.tsv (md5 17ff46dbbfe78dd537d6b9bff7f3ae67 at entry = exit; DEFERRED path preserves on-disk state)
    - docs/manuscript/id-vs-ref-LD.md (md5 2a57c1a061f0c66988a55d1d6600efdf at entry = exit; honest-framing-lock invariant)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (W7 baseline preserved; no W4 successor row needed)
    - results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv (NOT created; only created on RECLASS_FIRED branch which did not fire)
key-decisions:
  - MANUSCRIPT-MD5-AT-ENTRY (W4) = 2a57c1a061f0c66988a55d1d6600efdf (matches CONTEXT.md MANUSCRIPT-MD5-AT-ENTRY lock; supersedes stale plan-mode literal 63fd81385590ffc8d23d45a0f0598959 in PLAN.md L28 must_haves.truths block per CLAUDE.md critical_constraints rule 1)
  - MANUSCRIPT-MD5-AT-EXIT (W4) = 2a57c1a061f0c66988a55d1d6600efdf (UNCHANGED through full Wave 4; honest-framing-lock invariant preserved)
  - tier_assignments.tsv md5 at W4 entry = exit = 17ff46dbbfe78dd537d6b9bff7f3ae67 (DEFERRED path; on-disk file UNTOUCHED)
  - W4 gate at entry = PENDING (default disposition per OSF amendment paragraph (g) option (i) = SKIPPED -> DEFERRED_TO_FOOTNOTE)
  - W4 gate at exit = SKIPPED (W4 investigation confirms footnote path is sufficient; no escalation to RECLASS_FIRED required)
  - HLA encoding canonical mechanism = neg_ctrl_set == "hla_immune" column flag (24 rows; matches v5 narrative "minus 24 HLA" referent EXACTLY); NOT region_id substring (HLA_6p21 / HLA-DRB1 / MHC all return 0 grep matches; falsifies the "HLA-encoded-as-region_id-substring" hypothesis)
  - HLA_6p21 IS curated in config/regions_curated.csv (line 12) but with EMPTY canonical_pairs list — upstream pipeline correctly fires no positional coloc rows for HLA_6p21; HLA exclusion is implemented at the canonical_pairs config level, NOT as a downstream row-removal step
  - Row-count decomposition verified arithmetically consistent: 224 negative_control + 9 Tier C = 233 total data rows ✓
  - 9-row drift between v5 narrative baseline of 224 and post-W3 disk state of 233 is FULLY ATTRIBUTABLE to legitimate W3 R2 canonical-pair parity fire per OSF amendment paragraph (f); the v5 narrative arithmetic ("224 - 24 = 200") was internally consistent against the pre-W3 baseline; the post-W3 audit-driven substrate referent should be updated to "233 - 24 = 209 non-HLA"
  - Reconciliation interpretation = footnote_suffices (no schema corruption; no downstream aggregator dependency that breaks under footnote-only narrative; no factual inconsistency that the footnote cannot resolve)
  - Cowork-side A9 footnote prose recorded verbatim in CONTEXT.md as the canonical handoff text for v5 manuscript revision (informational; OUT of phase scope per OSF amendment "What is not changing")
  - HONEST_FINDING re-disposition principle applied (per .planning/feedback_failed_to_honest_finding.md memory) — the rigor-preserving outcome is transparent footnote-disclosure of the narrative-vs-disk arithmetic, NOT silent on-disk rewrite to match a stale narrative baseline; rewriting the file would violate the audit-driven re-analysis framing and could mislead reviewers who compare the v5 manuscript supplementary table to the on-disk substrate
  - W5 closeout brief implication — DEFERRED_TO_FOOTNOTE outcome recorded; no md5 successor row needed for tier_assignments.tsv in md5_baseline.tsv (file unchanged in this wave); A9 footnote prose available verbatim in CONTEXT.md for Cowork-side v5 ship
requirements-completed:
  - REQ-PUBLIC-DATA-ONLY (verified — investigation operates on existing public-data-derived tier_assignments.tsv; no new data ingest)
duration: ~10 min wall (gate read + investigation + TSV + log + CONTEXT.md update + atomic commit + SUMMARY + STATE/ROADMAP refresh)
completed: 2026-05-06
---

# Phase ta-r3 Plan W4: Tier-assignments HLA reconcile Summary

**One-liner:** W4 SKIPPED via D-TA-R3-W4-DEFERRED_TO_FOOTNOTE — investigation confirms tier_assignments.tsv on-disk encoding is correct (HLA exclusion via `neg_ctrl_set == "hla_immune"` flag, 24 rows) and the v5 narrative's 200-vs-224 row-count discrepancy is fully attributable to legitimate W3 R2 fire substrate growth (224 → 233 rows); Cowork-side A9 manuscript footnote handles the reconciliation without on-disk modification, preserving the audit-driven re-analysis framing and honest-framing-lock manuscript md5 invariant.

## Disposition

**D-TA-R3-W4-DEFERRED_TO_FOOTNOTE** (per OSF amendment paragraph (g) option (i)).

## Acceptance criteria (D1-D7 + invariants)

| ID | Criterion | Status |
|---|---|---|
| D1 | W4 gate read at task entry; default SKIPPED applied | PASS — gate token at entry was `D-TA-R3-W4-GATE: PENDING`; defaulted to SKIPPED per OSF amendment paragraph (g) option (i); resolved gate updated to `SKIPPED` in CONTEXT.md |
| D2 | Investigation TSV written with HLA encoding ambiguity enumeration | PASS — 35 lines (≥8 required); 9 HLA-encoding refs (≥3 required); enumerates HLA_6p21/HLA-DRB1/MHC/6p21 grep counts + neg_ctrl_set canonical encoding + row-count decomposition |
| D3 | DEFERRED branch: D-TA-R3-W4-DEFERRED_TO_FOOTNOTE recorded; on-disk file UNTOUCHED | PASS — token recorded in CONTEXT.md; tier_assignments.tsv md5 at entry = exit = `17ff46dbbfe78dd537d6b9bff7f3ae67` |
| D4 | RECLASS branch: tier_assignments split + HLA-fallback created | N/A — RECLASS branch did not fire (footnote path sufficient) |
| D5 | RECLASS branch: row-count conservation invariant | N/A — DEFERRED branch; conservation trivially holds (no rows split) |
| D6 | RECLASS branch: downstream aggregators re-run | N/A — DEFERRED branch; aggregators not re-run |
| D7 | RECLASS branch: md5 successor rows appended to ta-sh2b3-W7 baseline | N/A — DEFERRED branch; W7 baseline row preserved as-is (no successor row needed) |
| INV-1 | Manuscript md5 honest-framing-lock invariant preserved | PASS — entry md5 `2a57c1a061f0c66988a55d1d6600efdf` = exit md5 `2a57c1a061f0c66988a55d1d6600efdf`; supersedes stale plan-mode literal `63fd81385590ffc8d23d45a0f0598959` in PLAN.md L28 per CLAUDE.md critical_constraints rule 1 |
| INV-2 | tier_assignments.tsv on-disk file UNTOUCHED | PASS — entry md5 `17ff46dbbfe78dd537d6b9bff7f3ae67` = exit md5 `17ff46dbbfe78dd537d6b9bff7f3ae67` |
| INV-3 | Multi-terminal git staging (explicit paths only) | PASS — atomic commit `4ab6a51` staged 2 explicit paths only (investigation TSV + CONTEXT.md); no `git add .` / `git add -A` |
| INV-4 | Atomic commit landed | PASS — commit `4ab6a51` landed on main; 2 files changed; 88 insertions; conventional-commits-with-scope format with HEREDOC body |
| INV-5 | Conventional Commits format with `(ta-r3, W4)` scope and Co-Authored-By trailer | PASS — `docs(ta-r3, W4): SKIPPED — D-TA-R3-W4-DEFERRED_TO_FOOTNOTE...` with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer |
| INV-6 | Original-research framing preserved | PASS — commit message + CONTEXT.md update + SUMMARY frame as "audit-driven re-analysis" / "audit-driven substrate growth"; no "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot" language |

## Investigation findings (summary)

**Row-count decomposition (verified arithmetically consistent):**

| metric | value |
|---|---|
| Total disk rows (data) | 233 |
| `tier == "negative_control"` rows | 224 |
| `tier == "Tier C"` rows | 9 |
| Sanity check | 224 + 9 = 233 ✓ |
| `neg_ctrl_set == "hla_immune"` rows | 24 (matches v5 narrative "minus 24 HLA" referent) |
| `neg_ctrl_set == "cosmetic"` rows | 120 (5 cosmetic neg_ctrls × 24 each) |
| `neg_ctrl_set == "blood_group"` rows | 80 (4 blood-group neg_ctrls × 20 each) |
| Empty `neg_ctrl_set` rows | 9 (Tier C rows) |

**HLA encoding (canonical mechanism vs falsified hypotheses):**

| pattern | grep count | interpretation |
|---|---|---|
| `HLA_6p21` (region_id substring) | 0 | FALSIFIED — HLA is NOT encoded via region_id substring |
| `HLA-DRB1` / `HLA_DRB1` | 0 | FALSIFIED — no HLA gene-symbol substring encoding |
| `MHC` | 0 | FALSIFIED — no MHC substring encoding |
| `chr6:(28-33)` (HLA range) in region_id | 0 | FALSIFIED — no positional chr6 HLA-range encoding (CXADR_F2RL1_6p21 at chr6:10.3-11.8Mb is coincidental cytogenetic-band naming, NOT HLA-range) |
| `neg_ctrl_set == "hla_immune"` (column flag) | 24 | **CONFIRMED — canonical HLA encoding** (matches v5 narrative referent EXACTLY) |

**HLA_6p21 region status (from `config/regions_curated.csv`):**

> `HLA_6p21,EUR,6,25000000,35000000,NA,HLA,asthma,G3_complex,""`

The HLA_6p21 region IS curated, but with an EMPTY `canonical_pairs` list. So the upstream pipeline correctly fires no positional coloc rows for HLA_6p21. HLA exclusion is implemented at the `canonical_pairs` config level — NOT as a downstream row-removal step. This explains why `grep HLA_6p21` on the tier table returns 0: there genuinely should be 0 rows, by design.

**Drift attribution (v5 narrative `224` → post-W3 disk `233`):**

| baseline | total | minus 24 hla_immune | non-HLA |
|---|---|---|---|
| v5 narrative (pre-W3) | 224 | -24 | **200** ← v5 manuscript referent |
| Post-W3 disk (current) | 233 | -24 | **209** ← post-audit-driven re-analysis substrate |
| Drift | +9 | 0 | +9 |

The 9-row drift is fully attributable to the legitimate W3 R2 canonical-pair parity fire per OSF amendment paragraph (f) (which appended new R2-region rows for FTO/MC4R/APOL1/CXADR canonical pairs). The "minus 24 HLA" mechanic is correct and stable across baselines; only the total row count drifted.

## Cowork-side A9 footnote prose recommendation (handoff text)

The following prose is recorded verbatim in CONTEXT.md (D-TA-R3-W4-DEFERRED_TO_FOOTNOTE block) for direct insertion into the Cowork-side v5 manuscript revision A9 footnote:

> The supplementary tier_assignments.tsv table encodes HLA exclusion via the `neg_ctrl_set == "hla_immune"` flag (24 rows; canonical mechanism). The HLA_6p21 region is curated in `config/regions_curated.csv` with an empty `canonical_pairs` list, so the upstream pipeline correctly fires no positional coloc rows for HLA_6p21 itself. The manuscript narrative's "224 disk rows minus 24 HLA = 200 non-HLA" arithmetic was anchored to the pre-W3 aggregator baseline; the post-W3 audit-driven re-analysis substrate has 233 disk rows (224 negative-control + 9 Tier C), and the 200 non-HLA referent is updated to 209 non-HLA in the audit-driven re-analysis. The data-integrity invariant (HLA-class exclusion via the per-region `canonical_pairs` policy at `config/regions_curated.csv`) holds at file level; no on-disk reclassification is performed in this audit-driven re-analysis pass.

## Why DEFERRED_TO_FOOTNOTE is the rigor-preserving outcome

Per `.planning/feedback_failed_to_honest_finding.md` (HONEST_FINDING re-disposition principle):

1. **The on-disk encoding is correct.** HLA exclusion via `neg_ctrl_set == "hla_immune"` is the canonical mechanism, agreed-upon at the upstream `config/regions_curated.csv` level (HLA_6p21 has empty `canonical_pairs`). Rewriting the file to match a stale narrative baseline would corrupt a correctly-encoded substrate.
2. **The narrative-vs-disk arithmetic discrepancy is fully attributable to legitimate substrate growth** (W3 R2 fire under OSF amendment paragraph (f)). It is not a corruption, drift, or bug.
3. **Transparent footnote disclosure preserves reviewer-defensibility.** A reviewer comparing the v5 manuscript supplementary table to the on-disk substrate sees a footnote that maps "200 non-HLA" → "209 non-HLA" with the W3 fire attribution; rewriting the disk to match "200" would silently hide the W3 substrate growth and is therefore less rigorous.
4. **No downstream aggregator is broken under the footnote narrative.** The downstream consumers (`src/R/aggregators/aggregate_table3_admissible_pairs.R`, `src/snakemake/scripts/compute_jaccard.R`, `src/snakemake/scripts/compute_tier_a_retention.R`, three figure scripts) consume the on-disk file as-is; no rewrite is required for them to function correctly.

## Files touched

**Created:**
- `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv` (35 lines; investigation deliverable)
- `logs/ta_r3_W4_hla_reconcile/hla_reconcile.log` (34 lines; gitignored per `logs/*` rule)
- `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md` (this file)

**Modified:**
- `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` (D-TA-R3-W4-GATE: PENDING → SKIPPED + D-TA-R3-W4-DEFERRED_TO_FOOTNOTE block with full investigation summary + A9 footnote prose recommendation)
- `.planning/STATE.md` (stopped_at + last_updated + last_activity refresh)
- `.planning/ROADMAP.md` (W4 plan progress updated to completed)

**Untouched (by design, DEFERRED branch):**
- `results/qtl_coloc/tier_assignments.tsv` (md5 17ff46dbbfe78dd537d6b9bff7f3ae67 at entry = exit)
- `docs/manuscript/id-vs-ref-LD.md` (md5 2a57c1a061f0c66988a55d1d6600efdf at entry = exit)
- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` (W7 baseline preserved; no W4 successor row needed because file unchanged)
- `results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv` (NOT created; only on RECLASS_FIRED branch)

## Atomic commits

| commit | scope | message |
|---|---|---|
| `4ab6a51` | docs(ta-r3, W4) | SKIPPED — D-TA-R3-W4-DEFERRED_TO_FOOTNOTE; row-count reconciliation via Cowork-side A9 footnote |

(W4 closes with a single atomic commit because the DEFERRED branch is fully complete via investigation TSV + CONTEXT.md update; no further commits needed for tier_assignments.tsv or md5_baseline.tsv since both are UNTOUCHED. STATE/ROADMAP/SUMMARY refresh is committed in a separate metadata closeout commit per execute-plan.md `<final_commit>` step.)

## Deviations from plan

None — DEFERRED_TO_FOOTNOTE is the OSF-amendment-paragraph-(g)-option-(i) default path; W4 executed exactly as anticipated under the default disposition.

The PLAN.md line 28 stale plan-mode literal `63fd81385590ffc8d23d45a0f0598959` for the manuscript md5 was explicitly superseded by the LIVE value `2a57c1a061f0c66988a55d1d6600efdf` at execution time per CLAUDE.md critical_constraints rule 1 — this is documented in CONTEXT.md MANUSCRIPT-MD5-AT-ENTRY block and is NOT a deviation but rather a planner-vs-executor md5 reconciliation that was anticipated by the constraints rule.

## Self-Check: PASSED

**File existence:**
- FOUND: `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv`
- FOUND: `logs/ta_r3_W4_hla_reconcile/hla_reconcile.log`
- FOUND: `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md` (this file)

**Commit existence:**
- FOUND: commit `4ab6a51` on main (verified via `git log --oneline -1`)

**md5 invariants:**
- FOUND: manuscript md5 `2a57c1a061f0c66988a55d1d6600efdf` (matches honest-framing-lock invariant)
- FOUND: tier_assignments.tsv md5 `17ff46dbbfe78dd537d6b9bff7f3ae67` (UNCHANGED through full Wave 4)
