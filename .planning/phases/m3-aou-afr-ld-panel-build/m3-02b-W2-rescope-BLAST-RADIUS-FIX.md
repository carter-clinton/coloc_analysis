---
phase: m3-02b-W2-rescope
artifact: blast-radius-fix
created: 2026-06-19
trigger: post-CR-01-fix impact sweep (4 parallel read-only investigations)
status: resolved
findings:
  critical_regression: 1   # BR-01
  latent_test_fragility: 1 # BR-02
  exposed_preexisting: 1   # stale liftover test expectation
  deferred: 1              # A.3 AF sidecar gap
---

# Blast-Radius Sweep — CR-01 fix + WR-01/02/03

After fixing CR-01 (LD off-diagonal doubling) + WR-01/02/03, four parallel read-only
investigations mapped the downstream blast radius across the four changed contracts.
Two dimensions were clean; one surfaced a critical fix-induced regression; one a latent
test fragility; and the env-probe enabler exposed a pre-existing stale test.

## Dimension verdicts
- **LD numerical-output change** — CLEAN / forward-looking. dev-10 was killed with **0 LD
  artifacts**; Track A / ta-r3 use **GTEx** LD, not AoU. Nothing committed needs regeneration.
- **WR-01/WR-02 guards + manifest schema** — CLEAN. No existing caller breaks; committed
  manifests are static; no Snakemake rule wires the stitch yet; consumers read the manifest
  generically/defensively. The guards only make the previously-silent unsafe path fail loudly.
- **Same-bug-pattern / flag contract** — **CRITICAL regression (BR-01)**, below.
- **AF 0.0→NaN** — one **latent** test fragility (BR-02); producers/consumers otherwise NaN-safe.

## BR-01 (CRITICAL — regression introduced by the CR-01 fix) — RESOLVED
The CR-01 fix made the `.npz` `lower_triangular` flag AUTHORITATIVE: `ld_npz_to_rds.R` /
`stitch_subregions_to_rds.R` reconstruct the upper triangle ONLY when the flag is True, else
they only symmetrize `(M+t(M))/2`. But `src/python/bm_to_npz.py` — the **Path A.3** (large/
xlarge, >10 Mb) converter that the *entire xlarge-split deliverable* feeds — wrote
`np.tril(...)` lower-triangular **without** the flag. Post-fix, an A.3 `.npz` read with the
flag absent → defaulted False → treated as full → reconstruction skipped → **every off-diagonal
r HALVED** (proven: 0.6→0.30, 0.5→0.25). So the CR-01 fix traded an A.1 *doubling* bug for an
A.3 *halving* bug on the load-bearing path.

**Verified producer scope:** `bm_to_npz.py` is the ONLY remaining lower-tri `ld=`-schema
producer missing the flag. The two UKBB scripts (`ukbb_ld_tile_to_region_rds.py`,
`download_ukbb_ld_tiles.py`) use a different `R=`/`variants=` schema + separate bridge — out
of scope. `_save_npz` A.1 (full, flag absent=full → correct) and A.2 (lower, flag True →
correct) already agree.

**Fix (commit, TDD RED-first):** `bm_to_npz.py` now writes `lower_triangular=np.array([True])`.
Regression tests in `tests/m3/test_ld_npz_to_rds.py`:
- `test_bm_to_npz_static_writes_lower_triangular_flag` — static contract (RED against flag-less).
- `test_bm_style_lower_tri_npz_recovers_true_r` — round-trips a bm_to_npz-style lower-tri `.npz`
  through `ld_npz_to_rds.R`, asserts off-diagonal == 0.60 (NOT 0.30 halved, NOT 1.20 doubled).
Both GREEN after the fix.

## Stale liftover test EXPOSED (not caused) — RESOLVED
Verifying BR-01 required the converter R tests to actually run. They were silently SKIPPING:
the file's env-probe let reticulate bind to an ephemeral uv interpreter lacking pyliftover.
A new `_r_env` helper pins `RETICULATE_PYTHON` to the Rscript's sibling python (the m3-r-ld env
that ships pyliftover), un-skipping the converter families. That exposed
`test_grch38_to_grch37_liftover`, which asserted a **dbSNP-derived** GRCh37 position
(53,803,574) for chr16:53,809,247. The pipeline uses **UCSC hg38ToHg19 chain** liftover, which
maps it to **53,843,159** — confirmed by running `LiftOver(hg38ToHg19).convert("chr16",
53809247)` directly. **The converter is correct; the test expectation was stale** (and never
ran before, so was never caught). Test expectation + comment corrected to the chain truth.
No pipeline bug. (Anti-pattern note: a real skip was masking an unvalidated assertion —
[[feedback_skip_guard_masks_not_fixes]].)

## BR-02 (LOW / latent) — RESOLVED
`test_npz_payload_has_allele_freq` asserted `((af>=0)&(af<=1)).all()`, which silently fails on
`NaN` once the WR-03 change makes null AF NaN. Widened to `... | np.isnan(af)`. (hail-gated;
skips in smoke_dev — fixed regardless.)

## DEFERRED (pre-existing, NOT caused by the CR-01 fix) — flag for m3-02c / m3-04
`bm_to_npz.py` writes NO `allele_freq` key at all → **Path A.3 regions currently get NA AF**.
The phase deliverable is "LD + AF metadata", so A.3 (the large/xlarge regions) needs an AF
sidecar exported from the A.3 branch in `aou_ld_panel.py` (alongside the variant_ids/rsids
sidecars) and read by `bm_to_npz.py`. Larger scope; not a CR-01-fix regression. **Do not ship
the A.3 LD panel claiming AF coverage until this is closed.**

## Commits
- BR-01: `bm_to_npz` flag + `_r_env` un-skip + stale-liftover correction (`tests/m3/test_ld_npz_to_rds.py`, `src/python/bm_to_npz.py`)
- BR-02: NaN-safe AF range assertion (`tests/m3/test_build_ld_region_manifest.py`)

## Verification
- `pytest tests/m3/test_ld_npz_to_rds.py` → 11 passed, 1 skipped (hail only); BR-01 GREEN, liftover GREEN.
- Full `pytest tests/m3` → see session log (0 failed expected).
