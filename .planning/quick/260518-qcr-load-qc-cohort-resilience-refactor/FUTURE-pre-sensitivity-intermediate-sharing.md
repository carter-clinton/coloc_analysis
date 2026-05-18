# FUTURE quick-task spec stub: pre-sensitivity intermediate sharing

**Status:** SPEC_STUB — NOT a started task. Pre-spawn placeholder so the future quick task can hit the ground running. To be promoted to a full `/gsd-quick` task with its own PLAN.md + SUMMARY.md when warranted (see Trigger conditions below).

**Parent:** [260518-qcr load_qc_cohort algorithmic resilience refactor](./260518-qcr-DESIGN.md). This stub documents a Carter-identified optimization that emerged during the parent task but was explicitly deferred per §6 out-of-scope.

**Suggested future slug:** `260518-psi` (or current-date-+-random-3-char per convention). Suggested directory name: `{date}-{slug}-pre-sensitivity-intermediate-sharing`.

**Framing:** audit-driven re-analysis (incremental refactor extending 260518-qcr's resilience scope to share work across sensitivity branches; per [[feedback_original_research_framing]]).

---

## Motivation

`load_qc_cohort(ancestry="afr", sensitivity=False)` (Cell 3 / AFR primary) and `load_qc_cohort(ancestry="afr", sensitivity=True)` (Cell 4 / AFR sensitivity) execute **identical** steps 1-3 of the function ([src/python/aou_ld_panel.py:240-280](../../../src/python/aou_ld_panel.py#L240-L280)):

```
Step 1: hl.read_matrix_table(mt_path)
Step 2: ancestry filter (ancestry_pred == 'afr')
Step 3: anti_join_cols against relateds_flagged_samples.tsv
```

Step 4 is where they diverge:

```
Step 4: if sensitivity: mt.filter_cols(mt.self_report.contains("Black or African American"))
        else: no-op (Cell 3's path)
```

The current 260518-qcr refactor's auto-resume keys intermediates by `(ancestry, sensitivity, interval_filter)` — so `mt_afr_post_split.mt` (Cell 3's intermediate 1) and `mt_afr_pca_selfid_post_split.mt` (Cell 4's intermediate 1) are at distinct paths and Cell 4 cannot auto-resume from Cell 3's work.

**Carter's observation (during 260518-qcr execution on 2026-05-18):** the work of steps 1-3 is identical and ~3-5 hours of compute (full source MT read from GCS + ancestry filter + relateds anti-join). Sharing it across the sensitivity branches saves a meaningful chunk of Cell 4's first-fire wall time on every AFR-side re-derive cycle.

---

## Proposed design (high-level; promote to full DESIGN.md when scheduled)

Extend the existing 2-intermediate scheme to **3 intermediates**:

```
Intermediate 0 (NEW): mt_{ancestry}_pre_sensitivity.mt
  Written after step 3 (relateds anti-join), BEFORE step 4 (sensitivity filter).
  Sidecar keyed by: (ancestry, source_mt_path, interval_filter, ancestry_preds_path, relateds_path, cdr_version)
  Specifically EXCLUDES sensitivity from the sidecar key, since this intermediate
  is sensitivity-agnostic by construction.

Intermediate 1 (EXISTING): mt_{ancestry}{_sens}_post_split.mt
  Unchanged from 260518-qcr.

Intermediate 2 (EXISTING): mt_{ancestry}{_sens}_post_sample_qc.mt
  Unchanged from 260518-qcr.
```

State machine extension:

```
ENTRY:
  if intermediate_2 exists AND sidecar matches (incl. sensitivity)
    → state = "RESUME_FROM_POST_SAMPLE_QC"
  elif intermediate_1 exists AND sidecar matches (incl. sensitivity)
    → state = "RESUME_FROM_POST_SPLIT"
  elif intermediate_0 (pre_sensitivity) exists AND sidecar matches (EXCLUDING sensitivity)
    → state = "RESUME_FROM_PRE_SENSITIVITY"  ← NEW
  else
    → state = "FRESH"
```

In `RESUME_FROM_PRE_SENSITIVITY` state, Phase 1 skips steps 1-3 (reads intermediate_0 directly), applies step 4 (sensitivity filter, no-op or real per the call's `sensitivity` flag), then continues to steps 5-6 + intermediate_1 write.

---

## Estimated cost-benefit

Per the 2026-05-18 Cell 3 empirical timing:

- Steps 1-3 (read MT + ancestry filter + relateds anti-join) ≈ **~3-5 hours** of the ~8h pre-Stage-19 work on the 256-vCPU cluster (~$57-95)
- Steps 4-6 (sensitivity filter + naive_coalesce + split_multi_hts + repartition + intermediate-1 write) ≈ **~3-5 hours** of the remaining pre-Stage-19 work

Cell 4 (AFR sensitivity) first-fire on this extended refactor:
- Skips ~3-5 hours via intermediate_0 resume
- Cell 4 wall time: ~7-10h instead of ~10-13h
- Cost savings: ~$57-95 per AFR-side re-derive cycle

**Marginal value calculation:**
- Single re-derive cycle savings: ~$57-95
- Implementation cost (estimated, comparable to 260518-qcr): ~2-3 days of agent work + ~$5 of test fires
- **Break-even at ~5-10 AFR-side re-derives**, OR fewer if any single re-derive happens during a tight budget window where saving $90 matters.

---

## Trigger conditions for promoting this stub to a full quick task

Schedule the full `/gsd-quick` task when ANY of the following becomes true:

1. **Reviewer iteration scenario surfaces** — e.g., paper reviewer asks for QC threshold variations on AFR sensitivity that require re-deriving the cohort 3+ times.
2. **AoU CDR version bump** (v8 → v9) requires re-running both AFR primary and AFR sensitivity on new source data — the intermediate_0 sharing saves ~half the redo cost.
3. **A second M3 consumer needs sensitivity-style cohort variation** (e.g., M4 / M5 future work) — the sharing pattern generalizes.
4. **Carter explicitly requests it** out-of-band.

Until then: keep this stub. The 2-intermediate scheme from 260518-qcr is sufficient for the current Wave-1 production fire + foreseeable single-cycle re-derives.

---

## Scope notes (when the task IS scheduled)

- **Backwards compatibility**: existing intermediate_1 and intermediate_2 layouts unchanged. Adding intermediate_0 is purely additive.
- **Sidecar schema extension**: bump `schema_version` to 2 (intermediate_0's sidecar has a different key composition; sidecar reader must accept both versions).
- **Test coverage extension**: add ~3-5 new live-Hail tests covering `RESUME_FROM_PRE_SENSITIVITY` state + sidecar-mismatch-on-sensitivity-agnostic-fields detection + interaction with `force_fresh`.
- **DESIGN.md inheritance**: derive from 260518-qcr DESIGN; cite as parent; document the schema_version bump rationale.

---

## Related cross-references

- Parent task: [260518-qcr DESIGN](./260518-qcr-DESIGN.md) (commit 3cb659c, APPROVED at v2.1)
- Parent task: [260518-qcr SUMMARY](./260518-qcr-SUMMARY.md) (commit 717303e; §"Future quick-task spec candidates" mentions this stub)
- AOU-LD-PIPELINE.md §11.0 cluster sizing (commit d6f2748) — relevant because the cost-benefit analysis assumes the same correctly-sized 256-vCPU cluster.

---

**End of FUTURE stub. Not a started task. Promote via `/gsd-quick` when Trigger conditions warrant.**
