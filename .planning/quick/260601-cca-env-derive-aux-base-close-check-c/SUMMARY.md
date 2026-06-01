# 260601-cca — Env-derive AUX base; close CHECK C as a manual gate

**Date:** 2026-06-01
**Branch:** m3-W2-aou-deltas
**Commits:** `f4c495c` (feat: env-derive AUX base + 12 tests), `e196ac1` (docs: AOU-0 precheck CHECK-C reframe), + this state commit.
**Trigger:** Carter — "Solve / resolve this problem so we can move forward" re: CHECK C/D stuck on AoU.

## Problem

CHECK C (does the hardcoded AUX path resolve on the RW 2.0 R8→R9 CDR?) was a
manual Workbench gate blocking the migration's STAGE phase. Root reason: the
driver pinned the AoU auxiliary tables to a hardcoded `CDR_VERSION = "v8"`
literal at `src/python/aou_ld_panel.py:85`, so every CDR advance needed (a) a
manual gsutil path-verification in a CDR-wired env, and (b) a code edit. It had
already required exactly this dance at v7→v8.

CHECK D was already resolved (q04): Hail `0.2.135` on RW 2.0 → checkpoint-
contract catastrophe mechanism still live → Track 4 patches stay load-bearing.

## Resolution (structural, not operational)

Made the blocker disappear in code rather than waiting on a Carter env-capture:
`_resolve_aux_base(mt_path)` env-derives the AUX base from the WGS ACAF MT path
the cohort is actually built from (split on the stable
`/wgs/short_read/snpindel/` infix; aux/ is a documented sibling of
acaf_threshold/, verified 2026-05-01 Run 2). Resolution order: explicit arg →
`$WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` → hardcoded literal fallback.

**Effect:** v8/v9/bucket-move is a no-op for AUX-path *resolution* — the code
self-resolves on whatever the platform binds. CHECK C downgrades from a gate to
a one-line confirmation now baked into the AOU-0 precheck (Cell 2 prints the
resolved base + `gsutil` confirms both tables list, before any compute spend).

`_collect_provenance` now records the *resolved* paths (reproducibility-truthful
sidecar). Dead `RELATEDNESS_FULL_PATH` removed. Module docstring corrected.

## Method

- **Understand workflow** (3 parallel Explore agents): mapped blast radius (only
  the load_qc_cohort override seam + provenance sidecar consume the constants;
  no hidden readers), confirmed the infix-split assumption against in-repo
  evidence (v8 path + Run 2 gsutil verification), captured test conventions.
- **TDD**: 12 pure-Python regression tests RED→GREEN. Key guards:
  `test_resolve_aux_base_derives_v9_from_mt_path` (the CHECK-C regression),
  `test_validate_sidecar_rejects_cdr_version_drift` (codifies correct
  invalidation). `tests/m3`: 86 passed / 27 skipped / 0 failed.
- **Adversarial review workflow** (3 refutation lenses): correctness, resume/
  provenance, coverage/doc-drift. Findings adjudicated against the actual code
  below (receiving-code-review discipline — verify, don't reflexively implement).

## Adversarial-review dispositions

### Accepted → implemented
- **1.6 empty-prefix guard** — only derive when the prefix carries a URI scheme
  (`://`); else fall back. Prevents a malformed root-rooted `/wgs/.../aux` from a
  pathological infix-at-root path. + regression test.
- **3.1 docstring drift** — module docstring still said "Hardcoded auxiliary
  paths (NOT env vars)"; corrected to describe env-derivation + fallback.
- **3.2 dead code** — removed unused `RELATEDNESS_FULL_PATH` (zero refs).
- **2.2 contract test** — added `test_validate_sidecar_rejects_cdr_version_drift`.

### Rejected → with rationale (NOT bugs)
- **1.1 "add silent fallback to v8 literal if derived v9 path is missing"** —
  REJECTED. Would silently pair v9 genotypes with v8 ancestry calls — the exact
  version-mismatch hazard DEC-2026-05-01-01 warned against. Ancestry is mandatory
  → hard-fail is correct; relatedness is best-effort → soft-fail is intentional.
  Existence *confirmation* belongs in the compute-free AOU-0 precheck (now added),
  not a silent inline fallback.
- **2.1(A)/2.3 "exclude source_mt_path so checkpoints reuse across CDR versions"**
  — REJECTED. A v9 WGS MT is different data; reusing a v8-derived checkpoint
  against it is a data-integrity bug. The R8→R9 invalidation is (a) PRE-EXISTING
  via `source_mt_path` (recorded at line 341 *before* this change), and (b)
  correct. The env-derive change adds aux fields that are *collinear* with
  source_mt_path (aux is derived from it), so it introduces ZERO new invalidation
  scenarios — refuting the review's "introduces false-invalidation" claim.
- **2.4 schema_version bump** — REJECTED. Field schema unchanged (only values are
  now env-derived); bumping would needlessly invalidate sidecars.

## CHECK C / CHECK D status after this task

| Check | Status |
|---|---|
| CHECK D | DONE (q04) — Hail 0.2.135, mechanism live, Track 4 load-bearing |
| CHECK C | **RESOLVED CODE-SIDE** — driver auto-derives; no code edit on R9. Remaining: one compute-free *confirmation* run of AOU-0 precheck Cell 2 in a CDR-wired Standard Analysis env (prints resolved base + gsutil-confirms the two tables list). Not a gate; not blocking design work. |

## Next

AOU-0 precheck (compute-free, after `git clone` + push) → chr22 smoke (Carter
holds trigger). Push `f4c495c`/`e196ac1` + this commit to origin so a fresh AoU
clone carries the fix + the reframed precheck.
