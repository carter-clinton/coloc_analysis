# Quick Task 260812-ox1: m3-04c Task 3 fire-prep — Context

**Gathered:** 2026-08-12 (Carter's directive: *"For m3-04c Task 3, do all you can
for the checklist and get me to the point where im ready to fire."* `--auto
--chain`)
**Status:** Ready for planning

<domain>
## Task Boundary

Advance the m3-04c Task 3 PRE-FIRE checklist as far as an agent can, per the
corrected fire surface
(`.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md`,
read its `## Corrections (2026-08-12)` first). Four deliverables:

1. **PRE-FIRE 1 lands** — per-region occlusion-manifest upload (the review's
   PREFERRED lower-risk option), as reviewed code + tests.
2. **L-check re-anchor** — the L-01..L-20 local checks re-measured at the
   post-change HEAD, producing a fresh evidence log + TSV in this quick dir
   (the rcw evidence files are a dated record; do NOT modify them).
3. **PRE-FIRE 3 settled code-side** — the 0-vs-1-based index-origin question
   documented to a decision-grade answer with the safe in-perimeter instrument
   named.
4. **READY-TO-FIRE runbook** — one document with ONLY Carter's remaining
   actions, in order, each with its exact command (corrected forms only) and
   expected result, plus a PRE-FIRE 1b decision template.

⛔ **HARD BOUNDS:** The fire itself is NEVER touched — no perimeter contact of
any kind (no gsutil/gcloud/bq/wb, not even read-only), nothing started on any
VM/cluster, $0 spent. No OSF, no manuscript edits.
</domain>

<decisions>
## Implementation Decisions (LOCKED)

### Deliverable 1 — PRE-FIRE 1 (per-region manifest upload)
- File: `src/python/run_native_ld_panel.py` (NOT freeze-gated — `PY_FROZEN_RELS`
  in `tests/m3/test_source_freeze_pins.py:83-87` names only plink_ld_to_npz /
  condition_ld_matrix / occlusion_span_filter).
- Design, per the review §5 PRE-FIRE 1 "LOWER-RISK OPTION, PREFERRED":
  - In the occlusion block (`:795-831` region), in ADDITION to the existing
    best-effort shared-manifest append (unchanged), write a per-region Stage-A
    manifest `{out_prefix}.occlusion_manifest.tsv` (same records via
    `ocm.build_region_records` + `ocm.append_region_manifest` on a fresh
    per-region path — fresh path ⇒ header row written). Keep it inside the same
    best-effort guard: provenance must never abort a region.
  - In the `if ok:` upload block (`:922-937`), upload the per-region manifest
    alongside the excludelist, gated on file existence:
    `_gs_join(gs_out_dir, f"{region_id}.occlusion_manifest.tsv")`. Content is
    coordinate/id-only (same egress class as the excludelist — mirror the m3-07b
    comment discipline at `:932-934`).
  - NO object is ever overwritten (per-region names are unique); the aggregation
    glob `*occlusion_manifest*.tsv` in
    `src/snakemake/rules/m3_occlusion_lockstep.smk:175-176` already matches the
    per-region name — assert this in a test, do not just claim it.
- TDD, RED first: extend `tests/m3/test_run_native_ld_panel.py` using the
  existing `_MockGsutil` harness (`:657+`) — (a) a region WITH occluded variants
  in gs:// mode uploads the per-region manifest; (b) a region with NO occlusions
  uploads no manifest (absent ⇒ skipped, no error); (c) verify_failed region
  uploads NOTHING (unchanged property); (d) the per-region filename matches the
  lockstep glob (fnmatch against the literal patterns read from the .smk or
  restated as a contract test); (e) the shared local manifest behavior is
  byte-unchanged for local (non-gs) mode. Negative control: each new assertion
  must be OBSERVED RED before the implementation lands (project standing rule —
  a green assertion needs a negative control).
- Suite discipline: full `tests/m3` + `tests/phase2` re-run at the end; skips
  must STAY at exactly 31 and 1; passed counts may only grow. `git checkout --
  tests/m3/sparse_parent_benchmark.tsv` after runs.
- ⚠ Check for and update any test that pins the upload set as exactly-three
  before adding the fourth upload (grep for cp-destination assertions in
  `test_run_native_ld_panel.py`); widening such a pin must be paid for with a
  stricter direct assertion (AUTH-o7o-01 precedent).

### Deliverable 2 — L-check re-anchor
- Re-run the L-01..L-20 command set from `260811-rcw-evidence.tsv` at the FINAL
  post-change HEAD of this task; write `260812-ox1-evidence.log` +
  `260812-ox1-evidence.tsv` in this quick dir with the same schema.
- Respect the corrected labels: L-09 is a config-value read only; L-11 is
  file-wide presence (the scoped proof is L-13); L-16 must be run WITHOUT
  `2>/dev/null` blindness (test -d first, record which case the 0 means).
- L-03/L-04 = the full-suite runs from Deliverable 1's verification (do not run
  the suites twice; one post-change run serves both).
- Expected deltas vs rcw: L-01 (new HEAD), L-03 pass count may EXCEED 902 by
  exactly the number of new tests added here (record the new baseline; skips
  still 31), L-11/L-12 unchanged at 1, all other expectations unchanged. Any
  OTHER delta is a FINDING to report, not to paper over.

### Deliverable 3 — PRE-FIRE 3 index-origin settle
- Facts already measured (verify, then write up):
  `_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES = {10328, 44784, 46714, 59097,
  66730}` at `tests/m3/test_occlusion_span_filter.py:186`, documented 0-based
  (`:184-185` note); the gated test
  `test_region1_real_window_known_answer_gated` (`:492`) computes BOTH sides in
  the same 0-based space (`enumerate(rows)` at `:519`) — so the gated test is
  ORIGIN-SAFE: an origin error makes it FAIL loudly; it cannot false-pass. The
  §4-row-4 off-by-one risk belongs to a MANUAL line-number comparison, which the
  runbook must therefore forbid.
- Trace the constant's provenance
  (`.planning/amendments/m3_nan_conditioning_scientific_review.md` — the
  "10327/10328, 46713/46714/46715" index-adjacency language) far enough to state
  which base the source doc used, or state explicitly that the base is
  unrecoverable from the doc and the gated test's loud-fail property is the
  decision instrument.
- Deliverable: a short section in the runbook: Carter's in-perimeter action is
  to place the real region-1 window `.bim` at `data/aou/region1_window.bim` and
  run the gated test by name; interpretation table (pass / fail-with-uniform-±1
  / other-fail) with the action each implies.

### Deliverable 4 — READY-TO-FIRE runbook
- One file: `260812-ox1-READY-TO-FIRE.md` in this quick dir. Contents, in fire
  order, ONLY Carter's remaining items:
  1. Push/pull gate: origin == local at fire time; Workbench clone on
     `m3-W2-aou-deltas` + `git checkout -f` (skill checklist).
  2. §4 row 1: bucket `.npz` count — corrected literal-bucket command, expected
     0, and the never-prefix warning.
  3. §4 row 2: VM state via UI panel + disk-type label rule.
  4. §4 row 3: stale panel-TSV check/rotate — exact `gsutil stat`/`cat`/`rm`
     commands, 9-column/index-7 expectation.
  5. §4 row 5: cohort-MT data-layer re-verify (`du -s` on entries/rows/parts +
     count_cols/count_rows; no `/mt/` subdir; `_SUCCESS` is not evidence).
  6. GATE 1 cost/credit eyeball in the billing panel.
  7. PRE-FIRE 1b: the decision template — with PRE-FIRE 1 landed, branch (i) is
     the default; the template records the branch choice, the date, and the
     branch-(ii) re-entry instruction at STEP E ("re-read this at STEP E; (ii)
     is diagnosable only post-fire"). Pre-fill branch (i) language, leave the
     signature/date to Carter.
  8. PRE-FIRE 3: the gated-test instruction (per Deliverable 3).
  9. STEP A region-1 gate: pass criteria verbatim from the review (including
     the SH2B3 `__sub14` estimate_s follow-up check).
  10. STEP B: the fire command shape (nohup + timeout 312h, server-side), the
      corrected poll command (both forms + warning), the 2-3 day check-in
      cadence, "276 is NOT a pass bar", teardown-is-UI-only.
  11. STEP C/D/E/F/G pointers (each one line + where its full text lives).
- Every command in the runbook must be copied from the CORRECTED review text,
  never from the PLAN or the blast radius (their line numbers and commands have
  drifted — review §2.1(8)).
- The runbook states at the top: produced by an agent, verified at <HEAD>,
  agent-verifiable rows green as of <date>; the fire decision and every
  perimeter command are Carter's; AN AGENT MUST NEVER FIRE IT.

### Process constraints
- Git: explicit paths only; no worktrees (GPFS); commit per deliverable
  (code+tests atomic, docs separate).
- DECISIONS.md: this task ADDS no decision (PRE-FIRE 1 landing implements the
  review's recommendation; branch (i) selection remains Carter's signature in
  the runbook template). If the executor believes a decision is being made,
  STOP and report instead.
- Do not modify: the rcw quick dir (dated record), `.planning/amendments/`,
  `results/`, the three PY_FROZEN_RELS files, `run_susie_rss.R` (CODE-frozen),
  `docs/manuscript/`.
- The 260812-09a and 260811-* quick dirs are read-only history.
</decisions>

<specifics>
## Specific Ideas

- The review's §5 PRE-FIRE 1 paragraph documents WHY per-region beats
  shared-object upload (P3 lesson ff8cc47, overwrite race under future
  fan-out). Cite it in the code comment sparingly (one line, not a essay).
- `aggregate_manifests` skips absent/empty inputs
  (`assemble_occlusion_catalog.py:508` comment) — a zero-occlusion region
  legitimately has NO manifest anywhere; nothing may assert coverage == 276
  (false-invariant rule, `gates.blocker4_partial_rollup`).
</specifics>

<canonical_refs>
## Canonical References

- `.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-PRE-FIRE-GATE-REVIEW.md` (+ its `## Corrections (2026-08-12)`) — THE fire surface
- `.planning/quick/260811-rcw-assemble-the-m3-04c-task-3-pre-fire-gate/260811-rcw-evidence.tsv` — the L-check schema to re-anchor
- `src/python/run_native_ld_panel.py` — occlusion block `:795-831`, upload block `:900-950`
- `src/python/occlusion_manifest.py` — `append_occlusion_rows` `:200-214`, `append_region_manifest` write paths `:181`, `:195-196`
- `src/snakemake/rules/m3_occlusion_lockstep.smk:172-176` — the manifest glob
- `tests/m3/test_run_native_ld_panel.py` — `_MockGsutil` harness `:657+`, upload tests `:754+`
- `tests/m3/test_occlusion_span_filter.py:170-200, :492-525` — index-origin facts
- `.claude/skills/aou-ld-pipeline/SKILL.md` — invariants + fresh-clone checklist (runbook step 1 source)
- HANDOFF `suite_baselines` — 902/31/0 + 136/1/0, skips stay 31/1
</canonical_refs>
