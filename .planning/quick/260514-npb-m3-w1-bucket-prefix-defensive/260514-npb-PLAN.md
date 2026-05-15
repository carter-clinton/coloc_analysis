---
phase: m3-aou-afr-ld-panel-build
plan: 260514-npb
type: execute
wave: 1
mode: quick
depends_on:
  - 260512-jd9  # _qc_checkpoint_uri helper extraction (the call site this fix corrects)
  - 260512-ldj  # AOU-1 template Cell 1a/1b PYSPARK_SUBMIT_ARGS init pattern (Cell 1b is where the bug surfaced)
files_modified:
  - src/python/aou_ld_panel.py
  - tests/m3/test_aou_ld_panel_local.py
  - .planning/notebooks/AOU-1_template.ipynb
  - .planning/STATE.md
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION

must_haves:
  truths:
    - "Pre-existing helper-caller contract violation surfaced 2026-05-14 during AOU-1 Wave 1 Cell 1b PATCH VERIFICATION on AoU Workbench: _qc_checkpoint_uri at aou_ld_panel.py:147 expected bare bucket name (per existing tests using 'test-bucket') but AOU-1 template Cell 1b + Cell 7 callers passed os.environ['WORKSPACE_BUCKET'] which on AoU is prefixed (gs://fc-secure-...), producing malformed gs://gs://fc-secure-.../ld/mt_*.mt double-protocol-prefix URIs."
    - "load_qc_cohort at aou_ld_panel.py:275 calls _qc_checkpoint_uri for the actual checkpoint write path -- Cell 3 fire under the prior bare-only contract would have attempted to write to a malformed URI and either failed at the GCS-write boundary or silently landed in a wrong prefix."
    - "Reusable defensive utility `_normalize_bucket(bucket: str) -> str` lives top-level in src/python/aou_ld_panel.py just before _qc_checkpoint_uri (line 147), per [[feedback_extract_reusable_utilities]]. Strips optional gs:// prefix + leading/trailing slashes. Pure function; no validation."
    - "_qc_checkpoint_uri (line 178 post-fix) calls _normalize_bucket(bucket) before URI construction. Existing 4 bare-input tests still pass (back-compat). New prefixed-input regression test passes (defensive behavior)."
    - "CLI main() at aou_ld_panel.py:553 also uses _normalize_bucket(ws) for the Wave-2 BlockMatrix-write path's out_bucket construction (closes the same bug pattern in the second call site)."
    - "AOU-1 template Cell 7 cohort_summary checkpoint_path column refactored from inline f-strings (3 sites: f\"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_*.mt\") to _qc_checkpoint_uri() helper calls. DRY: helper is now canonical URI builder."
    - "6 new failing-test-first regression tests in tests/m3/test_aou_ld_panel_local.py (after the existing 260512-jd9 tests, before the live-hail section): test_normalize_bucket_strips_prefix, test_normalize_bucket_keeps_bare, test_normalize_bucket_strips_trailing_slash, test_normalize_bucket_idempotent, test_normalize_bucket_handles_malformed_extra_slash, test_qc_checkpoint_uri_accepts_prefixed_bucket."
    - "TDD ordering enforced: RED step observed all 6 new tests fail (5 ImportError on _normalize_bucket + 1 assertion failure proving the bug empirically: prefixed-input call returns 'gs://gs://test-bucket/ld/mt_afr_qc.mt'). GREEN step: 16 tests pass + 4 SKIPPED (live-hail without hail). All 4 existing 260512-jd9 regressions preserved."
    - "Commit lands on `main` (GPFS branch isolation per CLAUDE.md; no worktree) with subject token `(m3-W1-bucket-prefix-defensive)`; honest-original-research framing applies -- framed as 'audit-driven re-analysis: pre-existing producer/consumer drift at helper-notebook integration boundary surfaced empirically by Wave 1 fire' per [[feedback_original_research_framing]]; zero forbidden tokens (no cleanup/revision/salvage/fix-it tokens in framing-sensitive sections)."
    - "STATE.md refreshed in the same atomic commit per [[feedback_state_md_keep_current]] -- multi-terminal quick plans must not defer STATE.md."
    - "Pushed to origin/main as fast-forward (cherry-picked onto origin/main base since HPC and origin had divergent commit lineages with identical content). Carter's `git pull origin main` inside the AoU clone after a hard-reset (option A from reconciliation -- forensic-preserved 2c6dbee in bucket /forensics/ before reset) lands the fix; AoU-side replay (Kernel Restart + re-fire Cell 1a + Cell 1b) verified GREEN: Cell 1b PATCH VERIFICATION block emits single-gs:// URIs (no gs://gs:// double-prefix)."
  artifacts:
    - path: ".planning/quick/260514-npb-m3-w1-bucket-prefix-defensive/260514-npb-PLAN.md"
      provides: "This PLAN.md -- TDD-ordered remediation plan for the helper-caller bucket-prefix contract violation, scoped to Wave 1 + production code surface."
      min_lines: 80
    - path: ".planning/quick/260514-npb-m3-w1-bucket-prefix-defensive/260514-npb-SUMMARY.md"
      provides: "Outcome record with commit refs, TDD evidence logs, AoU-side replay verification, and explicit deferred follow-ups list."
    - path: "src/python/aou_ld_panel.py"
      provides: "Patched driver: new _normalize_bucket helper at line 147 (just before _qc_checkpoint_uri); _qc_checkpoint_uri calls _normalize_bucket internally; CLI main() out_bucket construction also uses _normalize_bucket."
      contains: "_normalize_bucket"
    - path: "tests/m3/test_aou_ld_panel_local.py"
      provides: "6 new regression tests added between the existing 260512-jd9 tests and the live-hail section."
      contains: "test_normalize_bucket"
    - path: ".planning/notebooks/AOU-1_template.ipynb"
      provides: "Cell 7 cohort_summary refactored from inline f-strings to _qc_checkpoint_uri helper calls (3 sites)."
      contains: "_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET']"
    - path: ".planning/STATE.md"
      provides: "Frontmatter status + stopped_at refreshed; Session Continuity entry appended documenting the bug-find, fix, and AoU-side replay."
  key_links:
    - from: "src/python/aou_ld_panel.py::_qc_checkpoint_uri (line 178 callsite)"
      to: "src/python/aou_ld_panel.py::_normalize_bucket (helper at line 147)"
      via: "f\"gs://{_normalize_bucket(bucket)}/ld/mt_{ancestry}{suffix}.mt\""
      pattern: "_normalize_bucket\\(bucket\\)"
    - from: "src/python/aou_ld_panel.py::main() out_bucket construction (line 553)"
      to: "src/python/aou_ld_panel.py::_normalize_bucket"
      via: "ws = _normalize_bucket(_require_env(\"WORKSPACE_BUCKET\")); out_bucket = f\"gs://{ws}/ld/{anc_upper}_aou\""
      pattern: "_normalize_bucket\\(_require_env"
    - from: ".planning/notebooks/AOU-1_template.ipynb (Cell 7 cohort_summary)"
      to: "src/python/aou_ld_panel.py::_qc_checkpoint_uri"
      via: "_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr'|'eur', False|True)"
      pattern: "_qc_checkpoint_uri\\(os\\.environ"
    - from: "tests/m3/test_aou_ld_panel_local.py (6 new tests)"
      to: "src/python/aou_ld_panel.py::{_normalize_bucket, _qc_checkpoint_uri}"
      via: "from aou_ld_panel import _normalize_bucket, _qc_checkpoint_uri"
      pattern: "from aou_ld_panel import _normalize_bucket"
    - from: "Commit (m3-W1-bucket-prefix-defensive)"
      to: "origin/main + AoU workspace via hard-reset + git pull (forensic 2c6dbee preserved in bucket /forensics/ first)"
      via: "git push origin push-fix:main (fast-forward 7ddafb6..779fe84)"
      pattern: "m3-W1-bucket-prefix-defensive"
---

<objective>
Defensive normalization of bucket-reference inputs in src/python/aou_ld_panel.py URI builders, closing the producer/consumer drift between the helper's bare-only test contract and the AoU notebook callers' prefixed-env-var convention. Without this fix, Cell 3 of the AOU-1 cohort definition notebook (load_qc_cohort primary AFR) would have attempted to write its materialized MT checkpoint to a malformed `gs://gs://fc-secure-...` double-protocol URI -- failing at the GCS-write boundary at best, silently landing wrong at worst. Wave 1 unblock-critical.
</objective>

<context>
Surfaced 2026-05-14 during the Wave 1 fire on AoU Workbench. Carter's Cell 1b PATCH VERIFICATION block (which the 260512-ldj template sync added precisely to catch this class of issue at the helper-caller boundary before any compute fire) emitted malformed URIs of the form `gs://gs://fc-secure-f72fd8d8-.../ld/mt_*.mt`. Initial on-screen reading parsed as 3-slash (`gs://gs:///fc-...`); empirical follow-up via repr() in Cell 5 of scratch_bootstrap_260514.ipynb disambiguated the Jupyter rendering artifact and confirmed the actual emission is exactly 2-protocol-prefix (`gs://gs://fc-...`, 4 slashes total, 2 occurrences of `gs:`).

**Root cause:** Mixed-contract codebase. `_qc_checkpoint_uri(bucket, ...)` (extracted by 260512-jd9) was tested only with bare bucket name (`"test-bucket"`), establishing an implicit bare-only contract. `_upload_to_gcs(out_bucket, ...)` at line 425 has the *opposite* contract (asserts `out_bucket.startswith("gs://")`, then strips). The AoU `$WORKSPACE_BUCKET` env var is prefixed (`gs://fc-secure-...`). When AOU-1 Cell 1b + Cell 7 + Cell 5 cohort def all pass `os.environ['WORKSPACE_BUCKET']` to the bare-only helper, the f-string substitution produces `gs://gs://fc-secure-.../ld/mt_*.mt`.

**Blast radius (mapped via grep + cross-file trace):**
1. `aou_ld_panel.py:160` -- the buggy helper (production write path via load_qc_cohort line 275)
2. `aou_ld_panel.py:513` -- CLI main() BlockMatrix-write `out_bucket` construction (Wave-2 production path; same bug pattern)
3. `.planning/notebooks/AOU-1_template.ipynb:184-186` -- Cell 7 cohort_summary inline f-strings (3 sites; would produce malformed `checkpoint_path` column in cohort_summary_m3.tsv)
4. `.planning/notebooks/AOU-2_per_region_ld.ipynb:51-52, 64-65, 134-136` -- Wave-2 surface (DEFERRED to follow-up /gsd-quick; MTs not yet built)
5. AOU-1 template doc comments at lines 114/132/150 -- misleading bash-style `gs://${WORKSPACE_BUCKET}/...` documentation (DEFERRED; documentation only, not executable)

**Why 260512-jd9 tests didn't catch this:** The 4 existing tests all pass bare `"test-bucket"`, exactly per the documented contract. No test asserts the notebook→helper integration with the AoU-runtime-prefixed env var. Classic test-gap at the integration boundary.
</context>

<approach>
Two-call-site defensive fix per [[feedback_extract_reusable_utilities]] + 6-test TDD coverage:

**Step 1 — Extract _normalize_bucket utility (RED tests added first):**
- New top-level function `_normalize_bucket(bucket: str) -> str` at aou_ld_panel.py:147 (just before _qc_checkpoint_uri).
- Body: `return bucket.removeprefix("gs://").strip("/")`. Strips optional `gs://` prefix and leading/trailing slashes. Pure function; no validation (callers handle empty-input cases).
- Tolerates either bare bucket name OR already-prefixed URI input.

**Step 2 — Wire into _qc_checkpoint_uri (line 178 post-extraction):**
- Helper body changes from `return f"gs://{bucket}/ld/..."` to `return f"gs://{_normalize_bucket(bucket)}/ld/..."`.
- Existing 4 bare-input tests (260512-jd9) still pass (back-compat).
- New prefixed-input regression test passes.

**Step 3 — Wire into CLI main() out_bucket construction (line 553):**
- Closes the same bug pattern in the Wave-2 BlockMatrix-write production path.
- `ws = _require_env("WORKSPACE_BUCKET")` -> `ws = _normalize_bucket(_require_env("WORKSPACE_BUCKET"))`.

**Step 4 — Refactor AOU-1 template Cell 7 cohort_summary (DRY):**
- 3 inline f-strings replaced with `_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr'|'eur', False|True)` calls.
- Helper is now the canonical URI builder; future changes propagate automatically.
- Edit performed via Python helper script (round-trip JSON validated) per the 260512-ldj pattern, NOT hand-edit of brittle JSON escape sequences.

**Step 5 — STATE.md refresh per [[feedback_state_md_keep_current]]:**
- Frontmatter `status` + `stopped_at` updated.
- Session Continuity entry appended documenting bug-find + fix + AoU-side replay sequence.

**Atomic commit + push:**
- Subject token `(m3-W1-bucket-prefix-defensive)`.
- Body uses "audit-driven re-analysis" framing per [[feedback_original_research_framing]]; zero forbidden tokens.
- Explicit `git add <path>` per [[feedback_multi_terminal_staging]] (4 specific files; pre-existing dirty paths NOT staged).
- Push to origin/main. HPC and origin have divergent commit lineages with identical content (separate session-management finding, documented in STATE.md; non-blocking) -- handled via cherry-pick onto temporary push-fix branch off origin/main, then `git push origin push-fix:main` as a clean fast-forward.
</approach>

<plan>
**Task 1 (RED):** Add 6 failing-test-first regression tests to tests/m3/test_aou_ld_panel_local.py:
  - test_normalize_bucket_strips_prefix
  - test_normalize_bucket_keeps_bare
  - test_normalize_bucket_strips_trailing_slash
  - test_normalize_bucket_idempotent
  - test_normalize_bucket_handles_malformed_extra_slash
  - test_qc_checkpoint_uri_accepts_prefixed_bucket
Verify: pytest run shows all 6 FAIL (5 ImportError on _normalize_bucket + 1 AssertionError empirically reproducing the gs://gs:// bug). Save log to /tmp/m3-W1-bucket-prefix-RED.log.

**Task 2 (GREEN):** Apply the 4 file changes:
  - aou_ld_panel.py: add _normalize_bucket at line 147; wire into _qc_checkpoint_uri (line 178) + CLI main() out_bucket (line 553).
  - AOU-1_template.ipynb: Cell 7 cohort_summary -> _qc_checkpoint_uri helper calls (3 sites; via Python edit script with pre/post asserts + JSON round-trip).
  - STATE.md: frontmatter refresh + Session Continuity entry.
  - test_aou_ld_panel_local.py: (already done in Task 1; verify GREEN).
Verify: pytest run shows 16 PASS + 4 SKIPPED (live-hail without hail). Save log to /tmp/m3-W1-bucket-prefix-GREEN.log.

**Task 3:** Atomic commit + push to origin/main:
  - git add (4 explicit paths only).
  - git commit with subject token `(m3-W1-bucket-prefix-defensive)`, body with TDD trace + framing.
  - Cherry-pick onto push-fix branch (= origin/main + 1) since HPC and origin lineages have diverged with identical content.
  - git push origin push-fix:main (fast-forward).
  - Cleanup: back to main, delete push-fix branch, pop stash of pre-existing dirty paths.

**Task 4:** AoU-side replay (user-driven):
  - On AoU clone: forensic-preserve 2c6dbee commit metadata to bucket /forensics/ (since AoU clone's cached origin/main was stale at 2c6dbee from a prior pull; remote was rewritten before my push).
  - git fetch origin + git reset --hard origin/main (aligns clone to new remote tip 779fe84).
  - cp new canonical .planning/notebooks/AOU-1_template.ipynb -> workspace-root /home/jupyter/workspaces/colocanalysis/AOU-1_cohort_definition.ipynb.
  - gsutil cp workspace-root -> bucket notebooks/AOU-1 (Welder Layer 2 sync).
  - 3-layer md5 verification (disk + bucket + canonical template all match).
  - In JupyterLab: File -> Close and Halt on AOU-1 tab; reopen via file panel; Kernel -> Restart Kernel.
  - Re-fire Cell 1a (PYSPARK_SUBMIT_ARGS injection; expect single-line confirmation).
  - Re-fire Cell 1b (~30-60s Spark attach; expect cores=1 OK assert + PATCH VERIFICATION block emitting single-gs:// URIs, NOT gs://gs://).
  - On GREEN: fire Cell 3 (primary AFR cohort, ~45-90 min envelope on 16-worker Dataproc).
</plan>

<deferred>
Out of scope for this quick task; tracked for follow-up /gsd-quick after Wave 1 Cell 3-7 lands:

1. **AOU-2 template (Wave-2 surface):** Same bug pattern at lines 51-52 (read paths: `hl.read_matrix_table(f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_*.mt")`), lines 64-65 (`OUT_BUCKET_AFR/EUR` write-path construction), lines 134-136 (gsutil shell commands with `gs://${WORKSPACE_BUCKET}/...` bash-style interpolation). Not yet fired -- MTs don't exist yet -- so can't be empirically validated end-to-end. Will be the natural follow-up gate before Wave 2 fires.

2. **AOU-1 template doc-comment cleanup:** Lines 114, 132, 150 still use misleading `gs://${WORKSPACE_BUCKET}/ld/mt_*.mt` bash-style documentation form. Documentation only, not executable; cleanup for accuracy + reviewer audit trail (so future readers don't reintroduce the bug pattern by copy-pasting the documentation as code). Trivial change; defer to AOU-2 follow-up commit.

3. **AOU-2/AOU-4 dirty execution-output state on AoU clone:** Flagged 2026-05-13 (carried over from prior session). Likely benign output-only diffs from 260512-864 cross-reads; should `git checkout --` to discard before any Wave-2 fire to avoid drift.

4. **HPC vs origin/main divergent commit lineage:** Separate session-management finding documented in STATE.md. Both have identical project content (4 fix-target files byte-identical between HPC HEAD and origin/main pre-fix). Reconciliation options (reset HPC to origin / leave divergent / force-push HPC over origin) are non-urgent; flagged for separate /gsd-quick investigation into why origin keeps getting rewritten between sessions.

5. **Explicit BM-out_bucket regression test:** Suggested by Carter during the grep blast-radius diagnostic. Currently the line-513 fix is covered transitively by _normalize_bucket behavior tests; an explicit integration-level test for the BM-write path's out_bucket construction would be belt-and-suspenders. Fold into AOU-2 follow-up.
</deferred>

<honest_framing_note>
Per [[feedback_original_research_framing]]: this work is framed as **audit-driven re-analysis** of a pre-existing producer/consumer drift at the helper-notebook integration boundary, surfaced empirically by Wave 1 fire's PATCH VERIFICATION block (which was added by 260512-ldj precisely to catch this class of issue before compute spend). Not "cleanup," "revision," "salvage," or "fix-it." The bug existed in the codebase since 260512-jd9 extracted the helper with bare-only test coverage; today's Wave 1 fire was the first time a caller passed the AoU-runtime-prefixed env var through the helper. The verification design caught it before any cluster-hours were burned. That is original-research methodological rigor working as designed.
</honest_framing_note>
