# ta-r3 phase CONTEXT: audit-V2-driven PSD-regularized SH2B3 re-fit + R1 trait-pair coloc.susie cache-invalidated re-fire

**Phase scope:** HPC-side compute work that produces substrate the Cowork-side v5 *Genome Medicine* manuscript revision (audit items A1, A2, A3, A6-stats, A7, A8, A9 — explicitly OUT of phase scope) draws on. After W5 closeout, a `/gsd-quick 260504-XXX-ta-r3-cowork-handoff` ships artifacts back to Cowork for v5 bundle ship.

**Honest-framing lock (per `.planning/feedback_original_research_framing.md`):** Frame as "audit-driven re-analysis," NOT "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot". The manuscript md5 (`MANUSCRIPT-MD5-AT-ENTRY` below) MUST stay stable through this phase; manuscript edits OUT of scope.

**OSF amendment:** [.planning/amendments/osf-amendment-r3-2026-05-04.md](../../amendments/osf-amendment-r3-2026-05-04.md) — locks lambda sweep + W1 outcome branches + W2 outcome branches + W3 conditional gate.

**Manuscript md5 lock semantics:**

- `MANUSCRIPT-MD5-AT-ENTRY: 2a57c1a061f0c66988a55d1d6600efdf`
  - Captured 2026-05-05 at phase entry from `docs/manuscript/id-vs-ref-LD.md` after the inline `wc -c`/`md5sum` invocation. Replaces the stale literal `63fd81385590ffc8d23d45a0f0598959` referenced in the W1-PLAN.md `must_haves.truths` block (drift between plan-mode and execute-mode; planner-side md5 was cached against an older snapshot of the manuscript).
  - Lock-at-entry semantic: every task's acceptance criteria asserts md5 unchanged from this value. If a task observes drift, it surfaces as a Rule 1 deviation in the SUMMARY.md.

---

## Decisions

### D-TA-R3-OSF-COVERAGE: OVERRIDDEN at 2026-05-05T13:49:10Z

**Status:** OVERRIDDEN — operator override 2026-05-05; the OSF amendment posting hard gate has been intentionally bypassed for this phase.

**D-TA-R3-OSF-OVERRIDE-RATIONALE:** operator override 2026-05-05 — amendment text committed locally at `.planning/amendments/osf-amendment-r3-2026-05-04.md`; OSF posting deferred; W5 closeout will flag for Cowork-side disclosure decision.

**Pre-execute hard gate disposition:** The original plan required this token to read `COVERED at <timestamp>` before any LSF dispatch fired. The override accepts the deviation (recorded in `.planning/osf_deviations.md`) and permits Task 2 dispatch without OSF-side posting. The amendment text is locally committed and reviewable; W5 closeout Brief will explicitly flag this deviation to Cowork-side for v5 disclosure decision (whether to post the amendment retroactively or fold the disclosure into the v5 cover letter).

**Permitted under OVERRIDDEN disposition:**
- W1 Task 1 (mkdir + CONTEXT.md scaffold + LD pathology inspection) — read-only / local-only; no LSF.
- W1 Task 2 (LSF dispatch of 15 PSD-regularized SuSiE-RSS fits) — fires under override; no further gate beyond explicit-path commit hygiene.
- W1 Task 3 (harvest + branch classification) — deferred to `/gsd-resume-work` (fire-and-forget pattern; harvest is a separate execute pass after `bjobs` clears).

**Verification at override time:**
- `git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l` returns 3 (commits remain ancestors)
- Amendment text on disk: `.planning/amendments/osf-amendment-r3-2026-05-04.md` (committed locally)
- Override entry appended to `.planning/osf_deviations.md` under "Deviations (OSF amendment required)"
- DECISIONS.md row landed: `DEC-2026-05-05-XX: OSF amendment posting deferred for TA-R3 audit-v2-driven phase; operator override; W5 closeout follow-up`

---

### D-TA-R3-W1-BRANCH_PSD_*: PENDING (Wave 1 outcome)

**Status:** PENDING — Wave 1 Task 3 classifies into exactly one of:
- `BRANCH_PSD_FIRM` — lambda exists where all 3 SuSiE-RSS fits converge AND PP.H4 >= 0.8 across all 3 canonical pairs
- `BRANCH_PSD_PARTIAL` — lambda exists with convergence but PP.H4 in [0.5, 0.8) for at least one canonical pair
- `BRANCH_PSD_COLLAPSE` — PP.H4 < 0.5 at all converged lambda values
- `BRANCH_PSD_NON_CONVERGE` — even with regularization across all lambda values, per-trait fits remain non-converged

Wave 3 gate consumes this: FIRM/PARTIAL -> W3 fires; COLLAPSE -> W3 skipped (anchor itself fails; parity moot); NON_CONVERGE -> W3 deferred to Track B.

**Operator-instructed deferral:** Per the 2026-05-05 fire-and-forget operator directive, the harvest of LSF outputs (coloc.susie at canonical pairs + branch classification) is OUT OF SCOPE for this execute pass. After `bjobs` clears, `/gsd-resume-work` will run the harvest tasks and write the resolved `D-TA-R3-W1-BRANCH_PSD_*` value here.

---

### D-TA-R3-W2-BRANCH_R1_*: PENDING (Wave 2 outcome)

**Status:** PENDING — Wave 2 Task 3 classifies into exactly one of:
- `BRANCH_R1_BUG` — post-refire produces non-empty PP rows in previously-empty 28
- `BRANCH_R1_STRUCTURAL` — post-refire holds at 28/28 empty (or near-empty)

---

### D-TA-R3-W3-GATE: PENDING (computed from W1 outcome at W3 entry)

**Status:** PENDING — gate fires only if W1 returns FIRM or PARTIAL; SKIPPED if COLLAPSE; DEFERRED_TO_TRACK_B if NON_CONVERGE. Resolved on `/gsd-resume-work` after W1 harvest classifies the branch.

---

### D-TA-R3-W4-GATE: PENDING (default DEFERRED_TO_FOOTNOTE; only fires if Cowork-side decides cheap A9 footnote insufficient)

**Status:** PENDING — default disposition is `DEFERRED_TO_FOOTNOTE`.

---

## Reused Existing Substrate

- [src/legacy/region_analysis/scripts/run_susie_rss.R](../../../src/legacy/region_analysis/scripts/run_susie_rss.R) — z-score derivation at line 466 (`subset[, z := BETA / SE]`); fitter pattern reused by W1's new PSD-regularized script
- [config/bsub_wrapper.sh](../../../config/bsub_wrapper.sh) — sets -W per queue (serial=5760 min via `*` default case); W1+W2+W3 use it via the same pattern as ta-sh2b3-W1-PLAN.md
- [.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv](../ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv) — W5 appends successor rows (NOT overwrite)
- Commits in HEAD: `069b34f` (variant-ID matcher in run_qtl_coloc.R), `7d54183` (LD-panel-rsid override in run_susie_rss.R), `02c4404` (max_iterations -> max_iter)
