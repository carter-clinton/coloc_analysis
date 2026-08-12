# Quick Task 260812-ox1 Summary — m3-04c Task 3 fire-prep: PRE-FIRE 1 landed, L-checks re-anchored, PRE-FIRE 3 settled, READY-TO-FIRE runbook

**One-liner:** PRE-FIRE 1 (per-region occlusion-manifest upload, the review's preferred
lower-risk option) landed TDD with 5 new tests; L-01..L-20 re-anchored 20/20 PASS at the
post-change HEAD with the new suite baseline 907/31/0; PRE-FIRE 3 settled decision-grade
(gated test is origin-safe; source-doc base unrecoverable); one Carter-only
READY-TO-FIRE runbook with corrected commands only. **$0, zero perimeter contact,
nothing fired.**

## Commits (3 task commits, all explicit-path staged)

| Task | Commit | What |
|---|---|---|
| 1 (feat) | `5284505` | PRE-FIRE 1: per-region `{region_id}.occlusion_manifest.tsv` written in the existing best-effort occlusion try + uploaded existence-gated inside `if ok:`; 5 new tests (all `-k per_region_occlusion_manifest`) |
| 2 (docs) | `02775af` | `260812-ox1-evidence.log` + `.tsv` — L-01..L-20 re-anchor, CONTEXT-P3a/b/c, RED/GREEN + mutation transcripts, zero-perimeter proof |
| 3 (docs) | `6055bed` | `260812-ox1-READY-TO-FIRE.md` — 11 Carter-only items in fire order, corrected commands only |

task_start_sha (pre-Task-1 HEAD, first line of the evidence log): `b17de1c`.

## OX1-D1 — PRE-FIRE 1 (per-region manifest upload), TDD

- **N = 5 new tests** in `tests/m3/test_run_native_ld_panel.py`, every name carrying
  `per_region_occlusion_manifest`. (a) upload + byte-level Stage-A content assertion
  (STAGE_A_COLUMNS header, 5 occluded ids under `m2_region_00001` — the stricter
  direct assertion, AUTH-o7o-01); (b) occluded-vs-clean region against ONE shared
  mock bucket (absent => skipped, no error); (c) verify_failed uploads NO region
  artifact — panel-TSV status row is the only cp destination, with the docstring
  explaining WHY that cp is expected; (d) lockstep-glob contract read from the .smk
  source with an in-test negative control; (e) shared local manifest byte-unchanged
  vs an independently constructed expectation (non-vacuous: 5 records).
- **RED observed before impl** (evidence log `CONTEXT-RED-0`/`CONTEXT-RED`): (a)/(b)/(c)
  FAIL, (d)/(e) PASS. (d)/(e) failability proven by deliberate one-edit mutations,
  each observed FAILED then reverted (`CONTEXT-MUT-D`/`-E`/`-REVERTED`; __pycache__
  cleared against the same-second .pyc trap).
- **GREEN** (`CONTEXT-GREEN`): 5/5 pass; containment: whole file 63 passed, zero
  regressions. Existing 3-object upload set, shared-manifest append, and
  `_reclaim_region_scratch` keep-set all byte-unchanged; frozen files untouched.
- **Impl:** two edits in `src/python/run_native_ld_panel.py` only — the per-region
  `append_region_manifest` call inside the ONE best-effort try (provenance can never
  abort a region), and the existence-gated upload beside the excludelist with the
  m3-07b egress-discipline comment (coordinate/id-only).

### Deviations from plan

1. **[Rule 3 – blocking] Test (c) recipe corrected.** The plan's
   `corrupt_regions={"m2_region_00001"}` cannot produce `verify_failed`: the FROZEN
   reader in `plink_ld_to_npz` raises on the same defect classes (NaN/diagonal/
   symmetry) BEFORE `content_verify_npz` runs, yielding `status == "error: …"`
   (measured in the first RED run; the pre-existing
   `test_one_bad_region_does_not_abort_loop` accepts either status for this reason).
   Fixed by forcing the state at the driver's OWN verify seam (monkeypatch
   `drv.content_verify_npz` → `(False, …)`), which drives the exact
   `status="verify_failed"` stamp and the `if ok:` upload gate the must-have truth
   pins — no upload assertion weakened. Recorded verbatim in `CONTEXT-RED-0`.
2. **[Rule 3 – blocking] Evidence log force-added.** `.gitignore:95 (*.log)` blocks
   the plan-mandated `260812-ox1-evidence.log` path; force-added the single file
   (`git add -f`, explicit path) per the exact rcw precedent
   (`260811-rcw-evidence.log` is tracked the same way). No `.gitignore` edit.
3. **Zero-perimeter proof recorded as an indented CONTEXT block**, not a `$ `-prefixed
   command line — a `$ grep …gsutil…` line would match its own pattern and poison the
   count. Same discipline as the rcw log (its grep appears only in review prose).

## OX1-D2 — L-check re-anchor (20/20 PASS, evidence_date 2026-08-12)

- Files: `260812-ox1-evidence.log` (verbatim blocks) + `260812-ox1-evidence.tsv`
  (8-column rcw schema). rcw evidence files byte-untouched — both gates EMPTY
  (git-log range from `task_start_sha` AND porcelain).
- **Expected deltas, all observed, no others (zero FINDINGS):**
  - L-01: new HEAD `5284505` (Task 1's feat commit).
  - **L-03: 907 passed / EXACTLY 31 skipped / 0 failed — the NEW BASELINE, 902 + N
    with N = 5** (907/31/0 in 866.18s). Suites ran EXACTLY once (serving Task-1
    verification and L-03/L-04); benchmark jitter file restored after.
  - **L-04: 136 / EXACTLY 1 / 0.**
  - Everything else identical to rcw (L-05 575 jobs; L-06 926/148; L-11/L-12 = 1;
    L-13 8P/0S four behavioural RUN; L-14 22P/0S; L-17 552/276/123/153; L-18
    `__sub14`/contained; L-19 0; L-02/L-20 EMPTY).
- Corrected labels honored: L-09 CONFIG-VALUE READ ONLY; L-11 FILE-WIDE PRESENCE
  (scoped proof = L-13); **L-16 run with `test -d` preamble, NO `2>/dev/null` — its 0
  disambiguated as DIR-ABSENT** (dir_exists=1 + the ls error recorded).

## OX1-D3 — PRE-FIRE 3 verdict

**The gated test `test_region1_real_window_known_answer_gated` computes both sides in
the same 0-based `enumerate` space (`:520` vs the `:186` oracle; note `:182-183`), so
an origin error produces a LOUD uniformly-±1-shifted FAIL and can never false-pass;
the source doc fixes NO base (its adjacency language — "index-adjacent (10327/10328,
46713/46714/46715…)", "chains two pairs" — is base-invariant, so the base is
UNRECOVERABLE from the doc and no certainty was manufactured); the gated test is
therefore THE decision instrument, manual line-number comparison is FORBIDDEN in the
runbook, and Carter's sole in-perimeter action is placing `data/aou/region1_window.bim`
and running the test by name.** Measured re-anchor: `enumerate(rows)` at `:520`
(CONTEXT.md cited `:519`; the measured value is recorded). SKIP message captured
verbatim (CONTEXT-P3a-4).

## OX1-D4 — READY-TO-FIRE runbook

`.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md`
— 11 items in fire order; header states agent-produced / verified at `5284505` /
**AN AGENT MUST NEVER FIRE IT**; PRE-FIRE 1b template pre-filled for branch (i) with
date+signature blank and the branch-(ii) STEP-E re-entry instruction; PRE-FIRE 3
interpretation table; STEP A criteria verbatim incl. the SH2B3 `__sub14` `estimate_s`
follow-up; STEP B with both corrected poll forms, "276 IS NOT A PASS BAR", teardown
UI-only; C–G one-liners. Items 2/4/5/10 byte-matched against the CORRECTED review with
`grep -F` (the `cat`/`head -1` form carries the review's markdown-escaped pipe); the
never-prefix warning appears in PARAPHRASE only — no `gs://$`-prefixed form (braced or
unbraced) anywhere in the document.

## Overall verification (all run post-Task-3)

1. Exactly 3 new commits (feat + 2 docs) — PASS. 2. `src tests config Snakefile`
porcelain EMPTY — PASS. 3. Frozen surface untouched (and freeze-pin tests green inside
L-03) — PASS. 4. rcw dir untouched under BOTH gates — PASS. 5. **New baseline: tests/m3
= 907 passed / 31 skipped / 0 failed (N = 5 named new tests); tests/phase2 = 136 / 1 /
0** — stated. 6. Zero-perimeter grep = 0 — PASS. 7. DECISIONS.md unchanged (no decision
added; branch (i) selection remains Carter's signature) — PASS.

## What remains is Carter's alone

Items 1–11 of the runbook: push/pull gate, the four §4 gate-time checks, the billing
eyeball, signing the 1b template, the gated PRE-FIRE 3 run, STEP A, the fire itself,
and C–G. **AN AGENT MUST NEVER FIRE IT.**

## Self-Check: PASSED

All 5 artifact files exist (evidence.log, evidence.tsv, READY-TO-FIRE.md, SUMMARY.md,
plus the two modified source/test files); all 4 commit SHAs resolve (`b17de1c`
task_start, `5284505`, `02775af`, `6055bed`); 5 `per_region_occlusion_manifest` test
defs present.
