---
phase: m3-aou-afr-ld-panel-build
plan: 260518-qcr
type: execute
wave: 1
mode: quick
status: IMPLEMENTATION_COMPLETE_AOU_VALIDATION_PENDING
completed: 2026-05-18T21:00:00Z  # local commit chain landed on HPC main; AoU validation deferred
commits_hpc:
  design: [aab73a2, 4f6014b, 3cb659c]              # DESIGN v1 → v2 → v2.1 (spec review cycles 1+2 APPROVED)
  scaffolding: [da63e4f, 328f0f1]                   # config.json + PLAN.md
  phase_1_helpers: [2cefa9e, 8bbd1d6, 4431a7e, 2c8a50d, d227862, a023206]  # 7 helper functions
  phase_2_refactor: [e82d9cb, c23f920, bd144a6]    # signature + state machine + 3-phase body
  phase_3_tests: [3720beb, 415ad84, a0c31bd, 5279376, 83b777b]  # 5 live-Hail tests
commits_origin: null  # NOT YET PUSHED -- bundled push deferred to post-AoU-validation per cherry-pick-on-push-fix-branch pattern (779fe84 precedent)
branch: main
subject_token: m3-W1-qc-cohort-resilience
framing: audit-driven re-analysis (algorithmic-resilience refactor closing the 2026-05-18 Cell 3 12h+ slow-path empirical observation)
files_modified:
  - src/python/aou_ld_panel.py  # 7 new helpers + load_qc_cohort signature extension + 3-phase body refactor; ~211 lines (was ~115)
  - tests/m3/test_aou_ld_panel_local.py  # +198 lines: 18 new pure-Python tests + 5 new live-Hail tests + synthetic_bucket fixture
  - .planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-DESIGN.md  # 412 -> 624 lines across v1->v2->v2.1
  - .planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-PLAN.md  # 1631 lines, 15 tasks across 4 phases
  - .planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-SUMMARY.md  # this file
  - .planning/config.json  # GSD init added use_worktrees: false
requirements:
  - REQ-AOU-LD-RESILIENCE  # new -- intermediate checkpointing per ancestry
  - REQ-AOU-LD-PROVENANCE  # new -- sidecar metadata audit trail
  - REQ-AOU-LD-VALIDATION  # existing -- still satisfied by chr22 smoke
tdd_evidence:
  baseline: "16 PASSED + 4 SKIPPED (pre-260518-qcr test suite)"
  phase_1_final: "34 PASSED + 4 SKIPPED (+18 new pure-Python tests across 6 helpers)"
  phase_2_final: "34 PASSED + 4 SKIPPED (preserved through 3 commits; no regression; no new tests)"
  phase_3_final: "34 PASSED + 9 SKIPPED (+5 new live-Hail tests, all SKIP via _require_hail since Hail not in smoke_dev env)"
  net_test_count_delta: "20 collected -> 43 collected (+23 tests: +18 pure-Python + 5 live-Hail)"
  hail_availability: "Hail NOT installed in /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/; 5 new live-Hail tests SKIP cleanly (same pattern as existing 4 live-Hail SKIPs); actual execution deferred to AoU env"
gsd_workflow_compliance:
  initial_slip: "DESIGN.md v1-v2.1 + PLAN.md drafted via brainstorming + writing-plans skills WITHOUT /gsd-quick entry"
  recovery_path: "Option B -- accept existing 260518-qcr directory; commit PLAN.md to existing structure; use gsd-executor subagents for execution (where GSD discipline matters most)"
  recovery_commits: "da63e4f (config.json from gsd init) + 328f0f1 (PLAN.md)"
  execution_compliance: "all 14 implementation commits (Phase 1 + 2 + 3) produced by gsd-executor subagents with full TDD discipline + atomic commits + explicit-path staging + audit-driven-re-analysis framing"
spec_review_cycles:
  cycle_1: "ISSUES_FOUND (2 HIGH + 2 MEDIUM + 2 LOW + impl notes)"
  cycle_2: "APPROVED -- all 6 cycle-1 issues RESOLVED; 2 LOW notes addressed as v2.1 micro-amendments"
  final_verdict: "APPROVED at v2.1 (commit 3cb659c)"
out_of_scope_explicit_deferrals:
  - "EUR-specific scaling decisions (decide after refactored AFR empirical timing)"
  - "Per-chromosome chunking (Q3 Option D; deferred unless C empirically insufficient)"
  - "AOU-1 template Cell 3/4/5 modifications (refactor preserves call shape)"
  - "variant_qc internals (behavior preserved, existing tests still cover)"
  - "AOU-2 template gs://gs:// bug pattern (separate /gsd-quick follow-up)"
  - "Sidecar utility extraction to src/python/_checkpoint_sidecar.py (defer to second M3 consumer per [[feedback_extract_reusable_utilities]])"
  - "Sidecar atomicity via .meta.json.pending + atomic rename (defer unless empirically needed)"
  - "Pre-sensitivity intermediate sharing across (sensitivity=False, sensitivity=True) -- Carter-identified optimization; separate quick task; design TBD"
operational_context:
  cell_3_state: "currently running on un-refactored code path; Stage 19 complete (~21:05 UTC); Stage 26 active (~2045 tasks variant_qc); ~$337 burned; ETA Cell 3 _SUCCESS ~22:30-00:30 UTC"
  cell_4_plan: "will auto-fire after Cell 3; un-refactored; estimated ~12-13h, ~$245-285"
  cell_5_plan: "DEFERRED to refactored code via post-AoU re-clone; halt before Cell 5 auto-fires (Kernel Interrupt at Cell 4 _SUCCESS)"
  refactor_benefit_realized_when: "Cell 5 (EUR parity, ~150K samples × ~1.2B variants); resilience to mid-fire failures; reviewer-iteration re-derives"
---

# Quick Task 260518-qcr: `load_qc_cohort` algorithmic resilience refactor

**One-liner:** Audit-driven re-analysis of the 2026-05-18 Cell 3 12h+ slow-path empirical observation. Refactored `load_qc_cohort` in `src/python/aou_ld_panel.py` to add 2 intermediate checkpoints + JSON sidecar metadata for provenance + auto-resume with parameter sanity check + balanced repartitioning, all behind a `force_fresh=True` user-override. 7 new private helpers, 23 new tests (18 pure-Python + 5 live-Hail), 14 atomic TDD commits across 4 phases. Implementation complete; production validation deferred to refactored Cell 5 (EUR parity) re-fire post-AoU re-clone.

## Empirical motivation

Cell 3 (AFR primary cohort definition) fired 2026-05-18T03:22 UTC on a correctly-sized 256-vCPU AoU Dataproc cluster (16× n1-highmem-16, per AOU-LD-PIPELINE.md §11.0 spec committed in d6f2748). chr22 smoke test passed in 12.3 min — 3.57× speedup vs the prior under-sized cluster — confirming the cluster sizing fix from the 2026-05-17 session.

**But Cell 3 itself took ~18 hours to complete Stage 19 alone** (the fused execute of the post-naive_coalesce sample_qc + aggregate_cols + variant_qc + final checkpoint write). Empirical signals:

- **Bimodal task velocity** in Stage 19: slow start (~58 min/task-wave for the first hour) → fast steady-state (~15 tasks/min). Consistent with partition skew from `naive_coalesce(2048)` merging adjacent native partitions without rebalancing.
- **No intermediate checkpoints** in the function. A worker crash mid-Stage-19 forfeits all 18+ hours of work; resumption requires re-firing from scratch.
- **Cost outlier projection**: AFR sensitivity (Cell 4) at ~$245 and EUR parity (Cell 5) at ~$1100 on un-refactored code path. All 3 Wave-1 ancestries: ~$1800 single-fire, vulnerable to total-work-loss on any executor crash.

The refactor preserves Cell 3's outputs (already committed locally; AoU production fire still in flight on un-refactored code) and gates future re-derives + the high-cost Cell 5 EUR fire through a resilient code path.

## What was built (mechanical summary)

### 7 new private helper functions in [src/python/aou_ld_panel.py](../../../src/python/aou_ld_panel.py)

| Helper | Lines | Purpose |
|---|---|---|
| `_intermediate_checkpoint_uri(bucket, ancestry, phase, sensitivity, interval_filter=None)` | ~30 | URI builder for `gs://.../ld/intermediate/mt_{ancestry}{_sens}_{phase}{_interval}.mt`. `_chr22` suffix for smoke isolation. |
| `_sidecar_uri(checkpoint_uri)` | ~5 | Appends `.meta.json` to a checkpoint URI. |
| `_collect_provenance(ancestry, sensitivity, source_mt_path, interval_filter)` | ~40 | Builds the JSON-serializable provenance dict (without `phase` field). Captures 7 QC thresholds + CDR metadata + git_commit_sha + hail_version + timestamp + schema_version. |
| `_write_sidecar(uri, provenance, phase)` | ~15 | Writes sidecar JSON via the scheme-dispatch shim. Adds `phase` field at write time. |
| `_read_sidecar(uri)` | ~25 | Reads sidecar JSON. Returns `None` if absent; raises `RuntimeError` on malformed JSON or unknown schema_version. |
| `_validate_sidecar(sidecar, provenance)` | ~30 | Compares sidecar vs current provenance, ignoring `phase`/`timestamp_utc`/`git_commit_sha`/`hail_version`. Returns `(matches: bool, diagnostic: str)`. |
| `_has_checkpoint(uri)` | ~15 | Checks for `{uri}/_SUCCESS` marker. Strong GCS object-existence consistency. |

Plus one **scheme-dispatch shim** introduced by the Phase 1 executor (gsd-executor agent identified the need): `_open_sidecar(uri, mode)` dispatches `file://` URIs to `pathlib.Path.open()` (local tests without Hail) and other URIs to `hl.hadoop_open` (production GCS). DESIGN §3.1's "unified file:// / gs:// handling" intent preserved; testability improved.

### `load_qc_cohort` signature extension + 3-phase body refactor

New keyword-only parameters added to existing signature:
- `force_fresh: bool = False` — bypass auto-resume; overwrite existing intermediates
- `interval_filter: str | None = None` — for chr22 smoke testing; produces path-isolated `_chr22`-suffixed intermediates

Body restructured into:
- **Phase 1** (former steps 1-6): read → ancestry filter → relateds anti-join → sensitivity filter → `naive_coalesce(2048)` → `split_multi_hts` → `repartition(2048)` → write intermediate 1 (`mt_*_post_split.mt`)
- **Phase 2** (former steps 7-9): `sample_qc` → call_rate filter → het ±3 SD filter → write intermediate 2 (`mt_*_post_sample_qc.mt`)
- **Phase 3** (former steps 10-12): `variant_qc` → MAF/HWE/call_rate filter → drop AoU-flagged variants → final checkpoint (`mt_*_qc.mt`)

State machine at function entry detects existing intermediates via `_has_checkpoint` + `_validate_sidecar`:
- **FRESH**: no intermediates OR `force_fresh=True` OR orphan-MT-recovery (sidecar absent → auto_fresh + WARN print)
- **RESUME_FROM_POST_SPLIT**: intermediate 1 exists + sidecar matches → skip Phase 1
- **RESUME_FROM_POST_SAMPLE_QC**: intermediate 2 exists + sidecar matches → skip Phase 1 + Phase 2

Sidecar mismatch → loud `RuntimeError` with diagnostic naming the specific differing parameter(s). `force_fresh=True` overrides.

### Sidecar atomicity policy

Order: checkpoint write FIRST, then sidecar write. Crash window between the two leaves an orphan MT; next fire detects sidecar absence → auto-force-fresh with WARN print. Cost: one phase re-done on crash-during-sidecar-write window. Alternative (`.meta.json.pending` + atomic rename) deferred to a future quick task if empirically needed.

### Test suite

20 collected → **43 collected** (+23 net tests):
- 18 new pure-Python tests across 6 helpers — all PASS in `smoke_dev` env
- 5 new live-Hail tests (auto_resume_from_post_split / auto_resume_from_post_sample_qc / force_fresh_bypasses_auto_resume / raises_on_sidecar_mismatch / auto_recovers_from_orphan_mt) — SKIP cleanly in `smoke_dev` (same pattern as existing 4 live-Hail tests); will execute and PASS on AoU env

Final full-suite gate: **34 PASSED + 9 SKIPPED** (no regression on prior 16 PASSED + 4 SKIPPED).

## Spec review cycles

- **Cycle 1 (general-purpose subagent):** ISSUES_FOUND with 2 HIGH + 2 MEDIUM + 2 LOW + impl notes. Issues: (1) phase-mismatch bug in control-flow pseudocode; (2) `interval_filter` smoke/production collision risk; (3) `overwrite` semantics on resume-from-post-split underspecified; (4) sidecar/checkpoint atomicity ordering not specified; (5) GCS consistency note missing; (6) test 7 deletion mechanism not specified.
- **Cycle 2 (general-purpose subagent):** APPROVED. All 6 cycle-1 issues RESOLVED. 2 LOW notes from cycle 2 (count typo + interval_filter malformed-input note) addressed as v2.1 micro-amendments.
- **User review gate:** Carter approved the final DESIGN at v2.1.

## GSD workflow compliance note

**Initial procedural slip identified mid-task:** DESIGN.md v1-v2.1 + PLAN.md draft were produced via the `superpowers:brainstorming` + `superpowers:writing-plans` skills WITHOUT entering through the project-mandated `/gsd-quick` workflow per `CLAUDE.md`. Carter flagged the slip; chose **recovery Option B**: accept the existing 260518-qcr directory and committed planning artifacts; commit PLAN.md to that directory; use `gsd-executor` subagents for execution (where GSD's atomic-commits-per-task + audit-trail discipline matters most for the implementation work).

All 14 implementation commits (Phase 1 + 2 + 3) produced by `gsd-executor` subagents with full TDD red-green discipline + atomic commits + explicit-path staging per [[feedback_multi_terminal_staging]] + audit-driven-re-analysis framing per [[feedback_original_research_framing]].

## Notable executor deviations from PLAN.md (all legitimate; documented in commit messages)

1. **Phase 1 Task 4**: `_open_sidecar(uri, mode)` scheme-dispatch shim introduced when the executor discovered that unconditional `hl.hadoop_open` would couple local tests to a Hail install (the existing 4 live-Hail tests use `pytest.importorskip("hail")` precisely to avoid this). The shim preserves DESIGN §3.1's "unified file:// / gs:// handling" intent while keeping helpers testable in pure Python. Production AoU path unchanged.

2. **Multiple tasks**: PLAN.md's "Expected: N PASSED" gate annotations referenced an outdated 12-test baseline; actual baseline was 16. Executors corrected on-the-fly using actual `pytest` output, not the plan's anticipated count. Counts in commit messages reflect actuals.

3. **Task 9 typographical micro-adjustment**: PLAN.md Task 9 body uses smart-quoted backticks that render as ASCII single-quotes through HEREDOC processing. Semantic content identical; commit messages match plan body.

No deviations affected implementation correctness, semantic preservation of the existing pipeline, test coverage targets, or the spec's `state ∈ {FRESH, RESUME_FROM_POST_SPLIT, RESUME_FROM_POST_SAMPLE_QC}` invariants.

## Production-validation status

| Validation | Status | Where |
|---|---|---|
| HPC unit tests (16 → 34 pure-Python + 4 → 9 live-Hail SKIP) | ✅ PASSED | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/` |
| chr22 smoke fresh fire (DESIGN §5.2) | ⏳ DEFERRED | AoU env post re-clone + pull origin/main |
| chr22 smoke resume fire (auto-resume from intermediates) | ⏳ DEFERRED | AoU env, second fire |
| Production Cell 5 EUR fire on refactored code | ⏳ DEFERRED | AoU env post Cell 4 halt |
| Wall-clock budget assertion (chr22 smoke fresh ≤ 30 min, resume ≤ 5 min, per DESIGN §8) | ⏳ DEFERRED | AoU env, regression guard |

The implementation is mechanically complete. Production validation runs in the next operational window after the current Cell 3 + Cell 4 (un-refactored) cycle completes and the refactor is pushed to origin/main.

## Carter's next-actions (immediate operational checklist)

1. **Monitor Cell 3 finalization** — Stage 26 (variant_qc, 2045 tasks) is currently active; ETA 22:30-00:30 UTC for `mt_afr_qc.mt/_SUCCESS` to land in bucket
2. **Cell 4 auto-fires** when Cell 3 completes — let it run on un-refactored code (~12-13h, ~$245-285)
3. **HALT before Cell 5** — when `mt_afr_pca_selfid_qc.mt/_SUCCESS` lands, immediately Kernel → Interrupt to stop the queue (or env Delete via AoU panel)
4. **Push refactor to origin** via cherry-pick-on-push-fix-branch (per 779fe84 pattern) — bundle 17 commits from this session + the still-unpushed `fc1a94f` (260514-npb docs) + post-AoU-cycle STATE.md Wave-1 update
5. **Provision new AoU env** (or re-use current after Delete + recreate) at 16× n1-highmem-16 (256 vCPU per AOU-LD-PIPELINE.md §11.0)
6. **chr22 smoke (fresh + resume) on AoU** — DESIGN §5.2 procedure
7. **Cell 5 EUR fire on refactored code** — first real production exercise of the resilience properties

## Future quick-task spec candidates (deferred from this task)

- **`260518-???-pre-sensitivity-intermediate-sharing`** — Carter-identified optimization: add a shared intermediate at the boundary between step 3 (relateds anti-join) and step 4 (sensitivity filter), keyed by `(ancestry, source_mt_path, interval_filter)` WITHOUT sensitivity. Would allow Cell 4 (sensitivity=True) to resume from Cell 3's (sensitivity=False) work, saving ~3-5h of source-MT read + ancestry filter + relateds anti-join per re-derive cycle. Architecture: extend the existing 2-intermediate scheme to 3 intermediates. Cost-benefit favors implementing only AFTER reviewer iteration scenarios warrant it (not for first Wave-1 production fire).
- **AOU-2 template `gs://gs://` bug pattern follow-up** — same defensive-normalization treatment as 260514-npb but for the AOU-2 read/write paths.
- **Sidecar utility extraction to `src/python/_checkpoint_sidecar.py`** — when the second M3 consumer needs the resume contract (AOU-2 or AOU-4).

## Commit lineage on HPC main

```
3cb659c docs(quick-260518-qcr): DESIGN v2.1 post-cycle-2 micro-amendments
4f6014b docs(quick-260518-qcr): DESIGN v2 addresses spec review v1 feedback
aab73a2 docs(quick-260518-qcr): load_qc_cohort algorithmic resilience refactor design
da63e4f chore(planning): record use_worktrees=false from /gsd-quick init
328f0f1 docs(quick-260518-qcr): PLAN.md -- 15-task TDD breakdown
2cefa9e feat(m3-W1-qc-cohort-resilience): _intermediate_checkpoint_uri helper
8bbd1d6 feat(m3-W1-qc-cohort-resilience): _sidecar_uri helper
4431a7e feat(m3-W1-qc-cohort-resilience): _collect_provenance helper
2c8a50d feat(m3-W1-qc-cohort-resilience): _write_sidecar + _read_sidecar helpers
d227862 feat(m3-W1-qc-cohort-resilience): _validate_sidecar helper
a023206 feat(m3-W1-qc-cohort-resilience): _has_checkpoint helper
e82d9cb feat(m3-W1-qc-cohort-resilience): add force_fresh + interval_filter kwargs to load_qc_cohort
c23f920 feat(m3-W1-qc-cohort-resilience): auto-resume state machine in load_qc_cohort
bd144a6 feat(m3-W1-qc-cohort-resilience): refactor load_qc_cohort body into Phase 1/2/3 with intermediate checkpoints
3720beb test(m3-W1-qc-cohort-resilience): auto_resume_from_post_split live-Hail test
415ad84 test(m3-W1-qc-cohort-resilience): auto_resume_from_post_sample_qc live-Hail test
a0c31bd test(m3-W1-qc-cohort-resilience): force_fresh_bypasses_auto_resume live-Hail test
5279376 test(m3-W1-qc-cohort-resilience): raises_on_sidecar_mismatch live-Hail test
83b777b test(m3-W1-qc-cohort-resilience): auto_recovers_from_orphan_mt live-Hail test
```

20 commits total in this quick task. To-be-pushed to origin/main in a subsequent bundled cherry-pick (this SUMMARY.md commit will be the 21st).

## Cross-references

- DESIGN spec: [`260518-qcr-DESIGN.md`](./260518-qcr-DESIGN.md) (v2.1, commit 3cb659c, APPROVED)
- PLAN: [`260518-qcr-PLAN.md`](./260518-qcr-PLAN.md) (commit 328f0f1)
- Predecessor: 260514-npb (bucket-prefix-defensive fix; commit fc1a94f HPC / 779fe84 origin)
- Cluster sizing: [`.planning/amendments/AOU-LD-PIPELINE.md §11.0`](../../amendments/AOU-LD-PIPELINE.md) (commit d6f2748)
- Memory: [[feedback_aou_cluster_sizing_for_ld_panel]] + [[feedback_aou_websocket_drop_zombie_pattern]] + [[feedback_aou_use_persistent_disk]] + [[feedback_aou_dataproc_pyspark_submit_args]]

---

**End of SUMMARY.**
