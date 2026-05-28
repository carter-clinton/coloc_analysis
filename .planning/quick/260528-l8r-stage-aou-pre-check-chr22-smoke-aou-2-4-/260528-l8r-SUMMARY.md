---
quick_id: 260528-l8r
description: Stage pre-migration moves (Abby reply + forensic mirror + migration playbook) + post-migration AoU notebook staging (precheck + chr22-smoke + AOU-2/4 pattern doc)
mode: quick
date: 2026-05-28
status: complete
disposition: SUCCESS
commits:
  - d16a32f  # T1/7 — ABBY-MIGRATION-CLARIFICATION-DRAFT.md
  - 0e5cba2  # T2/7 — run_forensic_mirror.sh + NCSU receiver README
  - 83e8606  # T3/7 — MIGRATION-PLAYBOOK.md
  - 298defc  # T4/7 — AOU-0-precheck_template.ipynb
  - e521cd0  # T5/7 — AOU-1-chr22-smoke_template.ipynb
  - 4e04226  # T6/7 — AOU-2-AOU-4-TRACK-4-PATTERN.md
related_artifacts:
  - .planning/quick/260528-jvd-land-m3-w1-track-4-defensive-code-patche/260528-jvd-SUMMARY.md (Track 4 patches; landed earlier this session)
  - .planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md (catastrophe handoff + 4-track plan; forensic-mirror receiver lives under this dir)
  - .planning/debug/m3-W1-empty-mt-catastrophe.md (root cause analysis source)
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md (D-M3-10 protocol)
---

# SUMMARY — Quick Task 260528-l8r

## Outcome

6 atomic commits + 1 closeout commit = 7 commit-day total on `main` / `origin/m3-W2-aou-deltas`. Scope expanded mid-task on discovery of the AoU Researcher Workbench 2.0 migration hard deadline (2026-06-30) — original 4 post-migration staging tasks supplemented with 3 pre-migration tasks (Zendesk reply + forensic mirror script + migration playbook). All AOU-1 / AOU-2 / AOU-4 currently-committed notebooks preserved byte-identical per Carter's directive — every paste-in or chr22 variant lives in a fresh sibling file.

**Test sweep:** 38 PASSED + 11 SKIPPED + 0 FAILED on `tests/m3/test_aou_ld_panel_local.py` at every commit boundary (no regression at any patch).

**Pre-existing dirty paths untouched** per `[[feedback_multi_terminal_staging]]`: `.claude/settings.json`, `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v4_addendum_supervisor_orphan.json`, the 260429-utt / 260501-wdn / 260502-lsk quick-task scaffolds, `results/track_a_aggregations/phase5_overview.tsv`, the 6 lsweep backup dirs, the targeted_rerun_* dirs. Explicit-path staging only.

## Per-task summary

| # | Commit  | Title                                                                    | Files                                                              | LOC delta |
|---|---------|--------------------------------------------------------------------------|--------------------------------------------------------------------|-----------|
| 1 | d16a32f | Abby Doyle Zendesk reply draft                                           | 260528-l8r/ABBY-MIGRATION-CLARIFICATION-DRAFT.md                   | +72       |
| 2 | 0e5cba2 | Forensic mirror script + NCSU receiver dir                               | 260528-l8r/run_forensic_mirror.sh + 260521/forensic-mirror/README.md | +343      |
| 3 | 83e8606 | RW 2.0 migration playbook                                                | 260528-l8r/MIGRATION-PLAYBOOK.md                                   | +212      |
| 4 | 298defc | AOU-0 pre-check notebook                                                 | .planning/notebooks/AOU-0-precheck_template.ipynb                  | +262      |
| 5 | e521cd0 | AOU-1-chr22-smoke notebook                                               | .planning/notebooks/AOU-1-chr22-smoke_template.ipynb               | +426      |
| 6 | 4e04226 | AOU-2/AOU-4 Track-4-pattern paste-in doc                                 | .planning/notebooks/AOU-2-AOU-4-TRACK-4-PATTERN.md                 | +211      |

## Verification gates (must_haves vs reality)

1. **ABBY-MIGRATION-CLARIFICATION-DRAFT.md exists with paste-ready Zendesk reply** — yes; sets internal hard deadline 2026-06-08 for Abby's engineering team response; uses corrected title per [[user_profile]]; reply-to honors [[feedback_aou_researcher_email_auth_only]]. PASS.
2. **run_forensic_mirror.sh exists and is executable** — yes (chmod +x); `bash -n` syntax-clean; gsutil-only (paused-cluster compatible); produces /tmp/forensic_mirror/forensic_mirror_*.tar.gz with per-MT du + ls + _SUCCESS mtime (hypothesis distinguisher) + bucket inventory + hail.log preserve copy + git rev-parse HEAD verification. PASS.
3. **NCSU receiver dir exists with README explaining receiver layout** — yes at `.planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/README.md`; explains end-to-end Path A (workspace bucket → NCSU) and Path B (Workbench Files UI → laptop → NCSU); 7-mode failure recovery matrix. PASS.
4. **MIGRATION-PLAYBOOK.md exists with pre-migration gates + Step 1-4 + post-migration validation** — yes; G0 (wait for Abby with 2026-06-08 internal deadline) + G1 (forensic mirror) + G2 (Track 4 patches verified on origin + AoU clone) + G3 (pre-migration inventory); Steps 1-4 contextualized to coloc_analysis workspace; 7-mode failure recovery matrix; recommended window 2026-06-02 → 2026-06-15. PASS.
5. **AOU-0-precheck_template.ipynb exists with 6 cells covering env + clone + mtime + entries + routing** — yes (Cell 0 markdown intro, Cell 1 clone state + Track 4 patch presence + RW platform identification, Cell 2 env-var assertions + CDR version inference, Cell 3 catastrophe MT inventory + entries discriminator, Cell 4 _SUCCESS mtime hypothesis test, Cell 5 routing matrix); nbformat.validate clean; platform-agnostic (Legacy or RW 2.0). PASS.
6. **AOU-1-chr22-smoke_template.ipynb exists as fork of AOU-1_template.ipynb** — yes; 12 cells preserving AOU-1 structure with three smoke-specific changes (interval_filter="chr22" in Cells 3/4/5 = 4 grep hits; _MIN_BYTES = 50_000_000 in Cells 3.5/4.5/5.5 = 3 grep hits; cohort_summary_m3_chr22.tsv output = 4 grep hits); cluster sizing preserved (256 vCPU still needed for v8 partition explosion); nbformat.validate clean. PASS.
7. **AOU-2-AOU-4-TRACK-4-PATTERN.md exists with paste-ready snippets** — yes; §2 AOU-2 Cell 4 cohort-MT validation (count_cols/count_rows + _validate_checkpoint_populated); §3 AOU-2 Cell 6 per-region .npz output validation (gsutil du for gs:// path; np.load + finite check for local path); §4 AOU-4 input .npz validation (shape + finite + symmetry); §5 D-M3-07 sensitivity-pair shape match; §6 application rules (apply at Wave 2 fire time only; comment with source token; audit grep); 16 grep hits on the marker tokens. PASS.
8. **AOU-1_template.ipynb + AOU-2_per_region_ld.ipynb + AOU-4_validation.ipynb byte-identical to origin/m3-W2-aou-deltas tip e38e8f2** — yes (git diff origin/m3-W2-aou-deltas..HEAD -- .planning/notebooks/AOU-1_template.ipynb .planning/notebooks/AOU-2_per_region_ld.ipynb .planning/notebooks/AOU-4_validation.ipynb returns 0 lines). PASS.
9. **pytest tests/m3/test_aou_ld_panel_local.py still passes 38/49** — yes (38 PASSED + 11 SKIPPED + 0 FAILED at final verify; no regression at any commit boundary in the chain). PASS.

## Test sweep evidence (final)

```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_aou_ld_panel_local.py --no-header -q
.....................................sssssssss.ss                        [100%]
38 passed, 11 skipped in 0.66s
```

## Branch / commit chain

Branch: `main` (per project memory `git.isolation: branch`; gsd-quick init returned `branch_name: null`); will fast-forward to `origin/m3-W2-aou-deltas` (same target as 260528-jvd push).

```
$ git log --oneline e38e8f2..HEAD
[T7/7 closeout commit]
4e04226 docs(quick-260528-l8r): AOU-2/AOU-4 Track-4-pattern paste-in doc (T6/7)
e521cd0 feat(quick-260528-l8r): AOU-1-chr22-smoke notebook ... (T5/7)
298defc feat(quick-260528-l8r): AOU-0 pre-check notebook ... (T4/7)
83e8606 docs(quick-260528-l8r): RW 2.0 migration playbook ... (T3/7)
0e5cba2 feat(quick-260528-l8r): forensic mirror script + NCSU receiver dir (T2/7)
d16a32f docs(quick-260528-l8r): Abby Doyle Zendesk reply draft ... (T1/7)
```

## What this DOES NOT change

- AoU env state — env stays DELETED per Carter end-of-Session-2; no recreation triggered by this staging
- Track A submission lane — untouched per `[[track_a_submission_in_progress]]` + `[[feedback_stop_asking_track_a]]`
- AOU-1_template.ipynb / AOU-2_per_region_ld.ipynb / AOU-4_validation.ipynb — preserved byte-identical for tech support review
- Track 4 source-code patches at `src/python/aou_ld_panel.py` — landed in 260528-jvd; no further changes
- LSF queue jobs, M2 manifest, M4/M5 downstream pipelines — none touched
- Pre-catastrophe W2 design-delta commits — preserved verbatim

## What this UNBLOCKS

- **Carter can send the Abby Zendesk reply today** (just paste from ABBY-MIGRATION-CLARIFICATION-DRAFT.md into ticket #57144). Sets the 2026-06-08 internal deadline clock.
- **Carter can run the forensic mirror script as soon as he recreates the AoU env** (paused-cluster compatible; ~$1 total; produces hypothesis-distinguisher answer in ~5 min). The kill-as-culprit vs Hail-finalize question gets resolved without waiting for Abby.
- **Carter has a step-by-step migration playbook ready** (MIGRATION-PLAYBOOK.md) so when he's ready to migrate, every gate + step + failure-mode is documented in advance.
- **AOU-0 / AOU-1-chr22-smoke / AOU-2/4 pattern paste-ins are paste-ready** for the moment Abby's reply lands + migration completes. No notebook-authoring blocker on the path to Wave 1 chr22 smoke validation or Wave 2 fire.
- **Any future operator (Carter himself in 3 months, or a second author down the line) inherits the full Track 4 protocol** via the D-M3-10 lock + the AOU-2/AOU-4 paste-in doc.

## Recommended next-session entry

1. **Read this SUMMARY + the 260528-jvd SUMMARY** to refresh context on the day's deliverables.
2. **Check Zendesk #57144 for Abby's reply.** If present, route per the matrix in ABBY-MIGRATION-CLARIFICATION-DRAFT.md "What to watch for in Abby's reply" section.
3. **If green-lit by Abby**, follow MIGRATION-PLAYBOOK.md: G0 → G1 (run forensic mirror) → G2 → G3 → Step 1 → Step 2 → Step 3 → Step 4. End state: workspace migrated to RW 2.0, forensic mirror committed, pre-migration inventory committed, post-migration validation committed.
4. **After migration**: paste AOU-0-precheck notebook into RW 2.0 Jupyter; run; record routing decision; if greenlight, fire AOU-1-chr22-smoke.
5. **If silence past 2026-06-08**: forensic mirror + migrate anyway; pivot Wave 2 to 1000G AFR substrate; document Wave 2 deviation in OSF amendment trail.

## Open items deferred to future tasks

- **Actual execution** of run_forensic_mirror.sh inside the AoU env — Carter user-action when env is recreated.
- **AOU-2 / AOU-4 paste-ins applied to live notebooks** — defer until Wave 2 is fire-ready (after migration + Abby reply + chr22 smoke pass OR 1000G pivot decision).
- **post-precheck-routing-decision.txt** — written by Carter after running AOU-0; commit to 260528-l8r/ dir.
- **post-smoke-validation.md** — written by Carter after AOU-1-chr22-smoke fires; commit to 260528-l8r/ dir.
- **cohort_summary_m3_chr22.tsv** mirror to NCSU — Carter user-action post-smoke.
- **CDR v8 → v9 migration patch in aou_ld_panel.py** — separate quick task when Carter learns at Step 4 validation whether RW 2.0 uses v8 or v9 paths.

## Total cost

- Compute: $0 — all staging NCSU-side; no AoU compute.
- Wall-time: single Carter-Claude session, ~90 min including planning + 6 atomic commits + closeout.
- Net lines: +1,526 across 6 new files (no modifications to committed notebooks).
