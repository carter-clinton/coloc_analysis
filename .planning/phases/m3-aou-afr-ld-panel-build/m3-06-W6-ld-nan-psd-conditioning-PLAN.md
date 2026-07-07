---
phase: m3-aou-afr-ld-panel-build
plan: 06
type: execute
wave: 1
depends_on: []
tags: [ld, psd, conditioning, nan, aou, afr, osf-prereg, track-a]
files_modified:
  - src/R/regularization/psd_utils.R
  - src/R/regularization/refit_sh2b3_psd_regularized.R
  - tests/testthat-phase1/test_psd_utils_byte_identical.R
  - tests/testthat-phase1/fixtures/psd_golden_r3.rds
  - src/python/condition_ld_matrix.py
  - tests/m3/test_condition_ld_matrix.py
  - src/python/write_conditioned_ld_npz.py
  - tests/m3/test_write_conditioned_ld_npz.py
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-VALIDATION
  - REQ-AOU-LD-EGRESS
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Running test_psd_utils_byte_identical.R proves psd_utils.R::psd_regularize_ridge and ::psd_regularize_eigclip produce output identical() to the pre-refactor r3 inline functions on a fixed battery of inputs (incl. a matrix with a genuinely negative eigenvalue that exercises the eigclip floor) — the r3 / Track-A numerics do NOT change."
    - "refit_sh2b3_psd_regularized.R SOURCEs src/R/regularization/psd_utils.R (path-robust, mirroring the existing snp_id_bridge.R dual-path source) and no longer defines psd_regularize_ridge/_eigclip inline — psd_utils.R is the single canonical definition consumed by both the EUR r3 refit and (in the deferred §5) the AFR native panel."
    - "condition_ld_matrix zeros ONLY the isolated off-diagonal NaN pairs (diagonal untouched at 1.0, symmetric (i,j)+(j,i) both set to 0.0) and records n_zeroed_pairs == the observed count on a region-1-topology fixture (12 NaN cells = 6 symmetric pairs across 11 rows, 0 fully-NaN rows)."
    - "condition_ld_matrix RAISES on a fully-NaN variant row (a zero-variance / monomorphic source): the message directs an upstream MAF/missingness QC drop, NOT a zero-conditioning."
    - "condition_ld_matrix RAISES when n_zeroed_pairs exceeds the pre-registered ceiling 0.0005 x n_var (substrate anomaly -> BRANCH_AFR_COND_DEFERRED, disclose as deviation)."
    - "condition_ld_matrix is a no-op passthrough on a clean (NaN-free) matrix (BRANCH_AFR_COND_CLEAN; n_zeroed_pairs==0; matrix returned unchanged)."
    - "condition_ld_matrix is MEMORY-BOUNDED: NaN detection, fully-NaN-row classification, and pair location are block-wise (transient bounded by block x n_var, no full n_var**2 temporary), reusing the plink_ld_to_npz.py block-wise discipline; the zeroing mutates in place at the located coordinates (no 40 GiB copy). A block-size-invariance test proves the result is independent of the block parameter."
    - "write_conditioned_npz emits a SEPARATE conditioned .npz ({region}.conditioned.npz, NOT the raw {region}.npz) carrying the base key set (ld, variant_ids, rsids, allele_freq, lower_triangular) PLUS provenance keys (n_zeroed, zeroed_pairs, nan_policy, psd_method, psd_lambda, ceiling_frac); its ld has the zeroed off-diagonals == 0.0, diagonal == 1.0, no remaining NaN, and preserves the source lower_triangular flag (triangle-flag contract)."
    - "The RAW-panel contract stays FROZEN: plink_ld_to_npz.read_square_bin still RAISES on any NaN, content_verify_npz is untouched, and ld_npz_to_rds.R is unchanged — the conditioning stage is strictly downstream and additive."
  artifacts:
    - path: "src/R/regularization/psd_utils.R"
      provides: "Canonical psd_regularize_ridge (Wen 2017) + psd_regularize_eigclip (Hutchinson 2020, lambda_floor=1e-6), verbatim-extracted from refit_sh2b3_psd_regularized.R"
      contains: "psd_regularize_eigclip"
    - path: "src/R/regularization/refit_sh2b3_psd_regularized.R"
      provides: "r3 EUR SuSiE-RSS refit, now sourcing psd_utils.R instead of inline PSD defs"
      contains: "psd_utils.R"
    - path: "tests/testthat-phase1/test_psd_utils_byte_identical.R"
      provides: "Byte-identity regression gate for the Track-A-sensitive PSD refactor"
      contains: "identical"
    - path: "tests/testthat-phase1/fixtures/psd_golden_r3.rds"
      provides: "Frozen golden output captured from the PRE-refactor inline r3 functions"
    - path: "src/python/condition_ld_matrix.py"
      provides: "condition_ld_matrix + block-wise NaN topology/pair helpers; the NaN->0 conditioning stage per OSF amendment (a)(b)(c)(d)"
      exports: ["condition_ld_matrix"]
      min_lines: 60
    - path: "tests/m3/test_condition_ld_matrix.py"
      provides: "Failing-first tests: isolated-pair zeros+records; fully-NaN-row RAISES; over-ceiling RAISES; clean no-op; block invariance; region-1 topology"
    - path: "src/python/write_conditioned_ld_npz.py"
      provides: "write_conditioned_npz — bank the conditioned matrix + provenance keys as a separate {region}.conditioned.npz"
      exports: ["write_conditioned_npz"]
    - path: "tests/m3/test_write_conditioned_ld_npz.py"
      provides: "round-trip + provenance-key + raw-untouched + triangle-flag tests"
  key_links:
    - from: "src/R/regularization/refit_sh2b3_psd_regularized.R"
      to: "src/R/regularization/psd_utils.R"
      via: "source() (path-robust, snp_id_bridge.R pattern)"
      pattern: "source.*psd_utils"
    - from: "src/python/condition_ld_matrix.py"
      to: "src/python/plink_ld_to_npz.py"
      via: "import the block-wise helper pattern (read_square_bin/content_verify_npz stay frozen)"
      pattern: "plink_ld_to_npz"
    - from: "src/python/write_conditioned_ld_npz.py"
      to: "src/python/condition_ld_matrix.py"
      via: "condition then savez"
      pattern: "condition_ld_matrix"
    - from: "src/python/write_conditioned_ld_npz.py"
      to: "conditioned .npz"
      via: "np.savez_compressed with provenance keys"
      pattern: "savez.*n_zeroed"
---

<objective>
Build the NC-State conditioning MACHINERY for the All of Us AFR native-plink LD panel:
(1) factor the two r3 PSD functions into a shared `psd_utils.R` behavior-preservingly,
(2) a memory-bounded `condition_ld_matrix` Python util that applies the pre-registered
off-diagonal `NaN->0` policy with topology branch + `n_zeroed` ceiling + provenance, and
(3) a writer that banks the conditioned matrix as a separate provenance-stamped `.npz`.

This wave promotes ROADMAP backlog item **999.1 steps §2-4 ONLY**. The OSF gate (§1) is
CLOSED (amendment posted as OSF file `tcujq` on `az52u`, 2026-07-04; coverage flag
`D-AFR-NANPSD-OSF-COVERAGE: COVERED`). Steps §5 (fit-time wiring against the real AFR
panel) and §6 (in-perimeter region-1 verification) stay **PARKED / LOOP-GATED** — the
276-region AoU LD loop is still running and the panel does not exist yet. Do NOT plan,
fire, or re-fire anything in-perimeter here.

Purpose: the raw panel `.npz` correctly RAISES on the 12 region-1 NaN cells
(`read_square_bin`); this wave supplies the downstream REPAIR — pre-registered, testable
on synthetic + region-1's already-characterized topology, with the r3 PSD numerics
guarded byte-identical (Track-A sensitivity).

Output: `psd_utils.R` (+ refactored `refit_sh2b3`), `condition_ld_matrix.py`,
`write_conditioned_ld_npz.py`, and three TDD test suites — all NCSU-confirmable, zero
perimeter access, zero contact with the running loop.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md
@src/R/regularization/refit_sh2b3_psd_regularized.R
@src/python/plink_ld_to_npz.py

# The amendment is the SPEC OF RECORD. Implement EXACTLY §(a) topology branch,
# §(b) n_zeroed ceiling = 0.0005 x n_var, §(c) PSD reuse (eigclip lambda_floor=1e-6
# primary; ridge lambda in {0.001,0.01,0.1} robustness companion — consumed at FIT
# TIME / §5, deferred), §(d) provenance. No parameter tuning to any fine-mapping result.

<interfaces>
<!-- Contracts the executor needs. Extracted from the codebase — use directly, no exploration. -->

From src/R/regularization/refit_sh2b3_psd_regularized.R (lines 71-87 — the two functions to extract VERBATIM):
```r
psd_regularize_ridge <- function(R, lambda) {
  R_reg <- R + lambda * diag(nrow(R))
  d <- sqrt(diag(R_reg))
  R_reg <- sweep(sweep(R_reg, 1, d, "/"), 2, d, "/")
  R_reg
}
psd_regularize_eigclip <- function(R, lambda_floor = 1e-6) {
  e <- eigen(R, symmetric = TRUE)
  d_clip <- pmax(e$values, lambda_floor)
  R_clip <- e$vectors %*% diag(d_clip) %*% t(e$vectors)
  d <- sqrt(diag(R_clip))
  R_clip <- sweep(sweep(R_clip, 1, d, "/"), 2, d, "/")
  R_clip
}
```

The existing path-robust source pattern already in refit_sh2b3_psd_regularized.R (lines 43-52) — MIRROR it for psd_utils.R:
```r
.bridge_path <- file.path(dirname(sub("^--file=", "",
  grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)[1])),
  "snp_id_bridge.R")
if (!file.exists(.bridge_path)) { .bridge_path <- "src/R/regularization/snp_id_bridge.R" }
stopifnot(file.exists(.bridge_path)); source(.bridge_path)
```

From src/python/plink_ld_to_npz.py — REUSE these block-wise helpers (do NOT modify this file; read_square_bin's raise-on-NaN + content_verify_npz stay FROZEN):
```python
def _has_any_nan_blocked(m, block: int = 1024) -> bool: ...        # any-NaN existence, bounded
def nan_variant_indices(m, block=1024, max_report=32) -> list: ... # rows ranked by NaN count
def _is_symmetric_blocked(m, atol, block=1024) -> bool: ...        # bounded symmetry
# Pattern to copy for the NEW pair-locator / fully-NaN-row classifier in condition_ld_matrix.py:
#   for i in range(0, n, block):  <slice m[i:i+block, :]>  # transient bounded by block*n
```

Raw-panel .npz key set that ld_npz_to_rds.R already ingests (the conditioned artifact MUST carry these + extra provenance keys):
```
ld, variant_ids, rsids, allele_freq, lower_triangular
```
Raw panel path convention (run_native_ld_panel.py:670): `{region_id}.npz`. Conditioned
artifact convention for THIS wave: `{region_id}.conditioned.npz` (separate file).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1 (999.1 §2): Refactor the two r3 PSD functions into a shared psd_utils.R — byte-identical, Track-A-guarded</name>
  <files>src/R/regularization/psd_utils.R, src/R/regularization/refit_sh2b3_psd_regularized.R, tests/testthat-phase1/test_psd_utils_byte_identical.R, tests/testthat-phase1/fixtures/psd_golden_r3.rds</files>
  <behavior>
    - Golden capture: on a FIXED battery of inputs, the CURRENT inline r3 functions
      produce reference outputs frozen to disk BEFORE any edit to refit_sh2b3.
    - Battery MUST include: (i) a small well-conditioned symmetric correlation matrix;
      (ii) a matrix with a GENUINELY NEGATIVE eigenvalue (so eigclip's `pmax(., lambda_floor)`
      clip branch actually fires — not a no-op); (iii) ridge at each pre-registered lambda
      {0.001, 0.01, 0.1}; (iv) eigclip at lambda_floor=1e-6. Fixed RNG seed; matrices
      built deterministically.
    - Test 1 (RED pre-util): sourcing src/R/regularization/psd_utils.R fails (missing) ->
      non-zero exit.
    - Test 2: psd_utils.R::psd_regularize_ridge output `identical()` to the golden for
      every lambda.
    - Test 3: psd_utils.R::psd_regularize_eigclip output `identical()` to the golden
      (incl. the negative-eigenvalue matrix).
    - Test 4 (secondary cross-check): a VERBATIM in-test copy of the original functions
      (`ref_ridge`/`ref_eigclip`) is also `identical()` to psd_utils.R's exports — anchors
      byte-identity to the literal source text as well as the frozen golden.
  </behavior>
  <action>
    Behavior-preserving extraction of the two PSD functions with a byte-identity gate.
    ⚠⚠ TRACK-A SENSITIVITY: refit_sh2b3_psd_regularized.R is EUR r3 code tied to an
    in-flight Track-A submission + the r3 OSF amendment. The refactor MUST NOT change r3
    numerics. Proceed in this exact order:

    (1) CAPTURE GOLDEN FIRST (before touching refit_sh2b3). Write a throwaway capture
    snippet that copies the two function bodies VERBATIM from refit_sh2b3 lines 71-87
    (see <interfaces>), builds the fixed battery (deterministic seed; include a matrix
    with a negative eigenvalue, e.g. a near-singular / indefinite symmetric matrix so the
    eigclip floor engages), computes ridge at {0.001,0.01,0.1} + eigclip at 1e-6, and
    `saveRDS()` a named list of the outputs to tests/testthat-phase1/fixtures/psd_golden_r3.rds
    (full double precision — saveRDS not dput). This golden reflects the TRUE pre-refactor
    r3 numerics. Run with the m3-r-ld env Rscript (base R only; no reticulate/susieR needed).

    (2) RED: write tests/testthat-phase1/test_psd_utils_byte_identical.R in the base-R
    stopifnot() style of test_refit_sh2b3_psd_snp_id_bridge.R (locate project root via
    commandArgs --file, no testthat). It `source()`s src/R/regularization/psd_utils.R,
    loads the golden fixture, and asserts `identical()` for each battery entry, PLUS the
    secondary in-test verbatim-reference cross-check. With psd_utils.R absent it exits
    non-zero (the failing-first condition). Commit RED (paths: the test only — NOT the
    golden yet if you want a clean RED; but committing the golden with the test is fine).

    (3) GREEN: create src/R/regularization/psd_utils.R containing ONLY the two functions
    copied VERBATIM (identical whitespace/body) from refit_sh2b3 lines 71-87, with a header
    comment noting they are the canonical r3 PSD methods (Wen 2017 ridge + Hutchinson 2020
    eigclip) pre-registered under osf-amendment-r3-2026-05-04.md and reused for AFR under
    osf-amendment-afr-native-ld-nan-psd-2026-07-03.md. Re-run the test -> GREEN.

    (4) Rewire refit_sh2b3_psd_regularized.R: DELETE the inline definitions (lines 71-87)
    and add a path-robust `source()` of psd_utils.R that mirrors the existing snp_id_bridge.R
    dual-path block (script-relative via commandArgs --file, fallback to
    "src/R/regularization/psd_utils.R"), with `stopifnot(exists("psd_regularize_ridge",
    mode="function"), exists("psd_regularize_eigclip", mode="function"))`. psd_utils.R is
    now the single source of truth; refit_sh2b3 CONSUMES it (do NOT keep a duplicate copy).

    Do NOT add a third PSD implementation (Seth do-NOT). Do NOT alter the function bodies,
    the lambda semantics, or the row/col normalization. Commit GREEN with explicit paths
    (GPFS — never git add -A), tag m3-06-W6-T1.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript tests/testthat-phase1/test_psd_utils_byte_identical.R</automated>
    Also: `grep -c 'psd_regularize_.*<- function' src/R/regularization/refit_sh2b3_psd_regularized.R` returns 0 (inline defs removed) AND `grep -c 'source.*psd_utils' src/R/regularization/refit_sh2b3_psd_regularized.R` returns >=1 (sources the canonical util).
  </verify>
  <done>test_psd_utils_byte_identical.R exits 0 (every battery entry identical() to the golden + the verbatim cross-check); refit_sh2b3 sources psd_utils.R and contains no inline PSD defs; psd_utils.R is the single canonical definition.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2 (999.1 §3): condition_ld_matrix — memory-bounded NaN->0 conditioning util (topology branch + ceiling + provenance)</name>
  <files>src/python/condition_ld_matrix.py, tests/m3/test_condition_ld_matrix.py</files>
  <behavior>
    - Signature: `condition_ld_matrix(m, *, nan_policy="off_diagonal_zero", ceiling_frac=0.0005, block=1024) -> tuple[np.ndarray, dict]`. Returns (conditioned matrix, provenance record).
    - CLEAN (no NaN): no-op passthrough; record {nan_policy, n_zeroed_pairs:0, zeroed_pairs:[], n_var, ceiling_frac, ceiling_n}; matrix returned unchanged.
    - ISOLATED off-diagonal NaN pairs (region-1 case): each undefined off-diagonal entry set to 0.0 at BOTH (i,j) and (j,i); diagonal untouched (stays 1.0); record n_zeroed_pairs == number of unordered i<j NaN pairs, zeroed_pairs == sorted list of those (i,j). Region-1-topology fixture: 12 NaN cells = 6 symmetric pairs across 11 index-adjacent rows, 0 fully-NaN rows -> n_zeroed_pairs==6, result symmetric + finite, diagonal all 1.0.
    - FULLY-NaN ROW (zero-variance / monomorphic source): a row whose off-diagonal entries are ALL NaN (nan_count_in_row >= n_var-1, robust to plink keeping the diagonal at 1.0) -> RAISE ValueError naming the row index(es) and directing an upstream MAF/missingness QC drop (NOT zero-conditioning).
    - OVER-CEILING: n_zeroed_pairs > ceiling_n where ceiling_n = ceiling_frac * n_var -> RAISE ValueError referencing BRANCH_AFR_COND_DEFERRED (substrate anomaly; re-diagnose + disclose as deviation).
    - MEMORY-BOUNDED: fully-NaN-row classification and pair location are block-wise (transient bounded by block x n_var; NO full n_var**2 temporary); zeroing mutates in place at the located coordinates. Block-size invariance: identical (matrix, record) for block in {small, large}.
    - Order within the function: (1) block-wise detect fully-NaN rows -> RAISE if any; (2) block-wise locate all off-diagonal NaN i<j pairs; (3) if 0 -> clean no-op; (4) if n_zeroed_pairs > ceiling_n -> RAISE (no mutation); (5) else zero the pairs in place + build record.
  </behavior>
  <action>
    Create src/python/condition_ld_matrix.py implementing EXACTLY the OSF amendment
    (a) topology branch, (b) ceiling, (c)+(d) provenance. REUSE the block-wise discipline
    from plink_ld_to_npz.py: `import plink_ld_to_npz as pln` and use `pln._has_any_nan_blocked`
    for the fast clean short-circuit; add NEW block-wise helpers in this module —
    `_fully_nan_rows_blocked(m, block)` (row NaN-count >= n_var-1) and
    `_nan_offdiag_pairs_blocked(m, block)` (yield i<j coords where m[i,j] is NaN and i!=j) —
    each scanning one `block`-row slice at a time (no full-size temporary), mirroring
    `nan_variant_indices` / `_is_symmetric_blocked`. Zero the located pairs by direct
    coordinate assignment `m[i,j]=0.0; m[j,i]=0.0` (O(n_zeroed) writes, in place — no 40 GiB
    copy at region-1 scale). Do NOT touch plink_ld_to_npz.py (read_square_bin raise-on-NaN +
    content_verify_npz stay FROZEN — the fix is this downstream stage, per STATE.md do-NOT).

    Provenance record dict: {nan_policy, n_zeroed_pairs, zeroed_pairs (list of (i,j), i<j),
    n_var, ceiling_frac, ceiling_n}. Do NOT set psd_method/psd_lambda here — PSD runs at
    FIT TIME on the region submatrix (§5, deferred); document that boundary in the module
    docstring. The over-ceiling + fully-NaN RAISE messages must be specific and actionable
    (name indices; cite BRANCH_AFR_COND_DEFERRED / the MAF-missingness drop respectively).

    Write tests/m3/test_condition_ld_matrix.py (smoke_dev py3.11, numpy only; mirror the
    fixture/style of test_nan_guard.py — `_clean_symmetric` helper, PROJECT_ROOT sys.path
    insert of src/python). Failing-first cases (RED before the module exists):
      - isolated-pair -> zeros + record n_zeroed_pairs==count, diagonal untouched, symmetric zeros;
      - region-1 topology fixture (6 pairs / 11 rows / 0 fully-NaN) -> n_zeroed_pairs==6, finite, symmetric;
      - fully-NaN row -> RAISES (message names the row + says drop by MAF/missingness QC);
      - over-ceiling -> RAISES (parametrize ceiling_frac and/or pair count so n_zeroed_pairs > ceiling_n; message cites BRANCH_AFR_COND_DEFERRED);
      - clean (no NaN) -> no-op passthrough, n_zeroed_pairs==0, matrix unchanged;
      - block-size invariance (result independent of block, mirroring test_nan_guard);
      - a test exercising the REAL default ceiling_frac=0.0005 at a tractable n_var (e.g. 4000 -> ceiling_n=2.0: 1 pair passes, 5 pairs raise) so the amendment default is covered without allocating a region-1-scale dense matrix.
    Commit RED then GREEN, explicit paths, tag m3-06-W6-T2.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_condition_ld_matrix.py -x -q</automated>
  </verify>
  <done>All test_condition_ld_matrix.py cases pass: isolated-pair zeros+records; region-1 topology n_zeroed_pairs==6; fully-NaN row RAISES; over-ceiling RAISES (BRANCH_AFR_COND_DEFERRED); clean no-op; block invariant. plink_ld_to_npz.py byte-unchanged (git diff empty).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3 (999.1 §4): write_conditioned_npz — bank the conditioned matrix as a separate provenance-stamped .npz</name>
  <files>src/python/write_conditioned_ld_npz.py, tests/m3/test_write_conditioned_ld_npz.py</files>
  <behavior>
    - `write_conditioned_npz(*, m, variant_ids, rsids, allele_freq, lower_triangular, out_npz, region_id, nan_policy="off_diagonal_zero", ceiling_frac=0.0005) -> str` calls condition_ld_matrix, then savez_compressed the conditioned matrix + base keys + provenance keys.
    - Conditioned .npz keys: base set (ld, variant_ids, rsids, allele_freq, lower_triangular) + provenance (n_zeroed, zeroed_pairs, nan_policy, psd_method, psd_lambda, ceiling_frac). psd_method/psd_lambda are PLACEHOLDER sentinels here (psd_method="PENDING_FIT_TIME", psd_lambda=NaN) — populated at FIT TIME in §5 (documented boundary).
    - The written ld: zeroed off-diagonals == 0.0, diagonal == 1.0, NO remaining NaN, symmetric; lower_triangular flag PRESERVED from the source (square -> False) per the triangle-flag contract.
    - Refuses to overwrite a raw panel .npz: out_npz MUST end in `.conditioned.npz` (or explicitly differ from the raw {region}.npz) -> else RAISE. Raw artifact never mutated.
    - CLEAN input -> conditioned .npz with n_zeroed==0 (uniform provenance artifact, BRANCH_AFR_COND_CLEAN).
    - fully-NaN / over-ceiling input -> the RAISE from condition_ld_matrix PROPAGATES; no artifact written.
  </behavior>
  <action>
    Create src/python/write_conditioned_ld_npz.py. `import condition_ld_matrix` (sibling in
    src/python) and reuse it — do NOT re-implement the conditioning. After conditioning,
    `np.savez_compressed(out_npz, ld=<conditioned>, variant_ids=..., rsids=...,
    allele_freq=..., lower_triangular=np.array([lower_triangular]), n_zeroed=<record
    n_zeroed_pairs>, zeroed_pairs=<np.array of the i<j pairs>, nan_policy=..., ceiling_frac=...,
    psd_method="PENDING_FIT_TIME", psd_lambda=np.float32("nan"))`. Enforce the out-path guard
    (must be `.conditioned.npz`; MUST NOT equal the raw {region_id}.npz path) so the FROZEN
    raw contract cannot be clobbered. Module docstring: state the boundary — this wave banks
    the NaN-conditioning provenance NOW; PSD (eigclip lambda_floor=1e-6 primary; ridge
    {0.001,0.01,0.1} companion) is applied to the fine-mapping SUBMATRIX at fit time (§5,
    deferred/loop-gated), which fills psd_method/psd_lambda in the FIT provenance; and the
    raw-panel .npz + ld_npz_to_rds.R stay UNCHANGED (the conditioned .rds materialization is
    §5). Keep it Python-only (.npz) for a clean NCSU-confirmable verify — no R round-trip,
    no perimeter access.

    Write tests/m3/test_write_conditioned_ld_npz.py (smoke_dev py3.11): RED-first, then GREEN.
      - write -> np.load round-trip: base keys + provenance keys ALL present; ld off-diagonal zeros==0, diag==1, no NaN, symmetric;
      - provenance correctness: n_zeroed == pair count; zeroed_pairs matches; nan_policy label; psd_method=="PENDING_FIT_TIME"; psd_lambda is NaN;
      - lower_triangular flag preserved (square source -> stored False);
      - out-path guard: writing to a non-`.conditioned.npz` path (or the raw {region}.npz) RAISES; a pre-existing raw .npz on disk is byte-unchanged after a conditioned write;
      - clean input -> conditioned .npz with n_zeroed==0;
      - fully-NaN / over-ceiling input -> RAISE propagates, no file written.
    Commit RED then GREEN, explicit paths, tag m3-06-W6-T3.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_write_conditioned_ld_npz.py -x -q</automated>
  </verify>
  <done>All test_write_conditioned_ld_npz.py cases pass: conditioned .npz carries base + provenance keys with correct values; ld conditioned (zeros/diag/no-NaN/symmetric); triangle-flag preserved; out-path guard blocks raw clobber; clean no-op; RAISE propagates. ld_npz_to_rds.R + plink_ld_to_npz.py byte-unchanged.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| raw LD matrix -> conditioning stage | A NaN-carrying dense LD matrix (untrusted topology) crosses into `condition_ld_matrix`; a malformed / substrate-anomalous NaN pattern could silently corrupt downstream fine-mapping if zeroed blindly. |
| conditioning provenance -> egress (deferred §5/§6) | Only aggregate provenance (counts, pair indices, labels) is designed to leave the AoU perimeter; no genotypes / full LD matrix. |
| r3 PSD source -> refactored psd_utils.R | Track-A / r3 numerics provenance boundary: a silent numeric drift would invalidate an in-flight pre-registered submission. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-06-01 | Tampering | condition_ld_matrix (silent over-zeroing of a substrate anomaly) | mitigate | Pre-registered ceiling `n_zeroed_pairs <= 0.0005 x n_var` RAISES (BRANCH_AFR_COND_DEFERRED); a large NaN fraction is never silently conditioned. Fully-NaN-row RAISES rather than zero-conditioning a zero-variance source. |
| T-m3-06-02 | Repudiation / reproducibility | psd_utils.R refactor (Track-A r3 numerics) | mitigate | Byte-identity regression test (`identical()` vs a frozen golden captured from the PRE-refactor inline source + a verbatim in-test cross-check) gates the refactor; verbatim extraction, no body change; single canonical definition. |
| T-m3-06-03 | Information disclosure | conditioning provenance record | mitigate | Record holds only aggregate counts + variant-pair INDICES + policy labels (egress-safe per amendment (d)); no genotypes/full matrix. Actual egress is §5/§6 (deferred, loop-gated) — schema is aggregate-only by construction. |
| T-m3-06-04 | Denial of service (OOM) | dense n_var**2 NaN scan / zeroing | mitigate | Block-wise detection/classification/location (transient bounded by block x n_var) + in-place coordinate zeroing (no full-size copy) — reuses the m3-02e-T4 dense-verify OOM discipline; block-size-invariance test locks it. |
| T-m3-06-05 | Tampering | raw-panel .npz clobber | mitigate | Writer enforces `.conditioned.npz` out-path guard (refuses the raw {region}.npz path); raw contract + read_square_bin + content_verify_npz + ld_npz_to_rds.R stay FROZEN. |
</threat_model>

<verification>
- Task 1: `Rscript tests/testthat-phase1/test_psd_utils_byte_identical.R` exits 0; refit_sh2b3 has 0 inline PSD defs + >=1 source(psd_utils) line.
- Task 2: `pytest tests/m3/test_condition_ld_matrix.py -x` all pass; `git diff --stat src/python/plink_ld_to_npz.py` empty.
- Task 3: `pytest tests/m3/test_write_conditioned_ld_npz.py -x` all pass; `git diff --stat src/scripts/ld_npz_to_rds.R src/python/plink_ld_to_npz.py` empty.
- Full regression: `pytest tests/m3 -q` stays green (baseline 336 passed / 30 skipped + the new Task 2/3 cases; no regressions in the frozen modules).
- NO perimeter access, NO loop contact, NO re-fire. Work is entirely NCSU-local on synthetic + region-1's characterized topology.
</verification>

<success_criteria>
- psd_utils.R is the single canonical home of psd_regularize_ridge/_eigclip; refit_sh2b3 sources it; the byte-identity gate proves r3 numerics unchanged (Track-A safe).
- condition_ld_matrix implements the amendment exactly: fully-NaN-row RAISE (drop upstream), isolated-pair NaN->0 (diagonal untouched), 0.0005 x n_var ceiling RAISE (DEFERRED), clean no-op, memory-bounded + block-invariant.
- write_conditioned_npz banks a SEPARATE {region}.conditioned.npz with base + provenance keys (psd_method/psd_lambda placeholders documented as fit-time/§5), raw contract un-clobbered.
- The raw-panel .npz contract, read_square_bin raise-on-NaN, content_verify_npz, and ld_npz_to_rds.R are all byte-unchanged.
- §5 (fit-time wiring) + §6 (in-perimeter region-1 verification) remain parked in ROADMAP 999.1 — NOT touched here.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-06-W6-ld-nan-psd-conditioning-SUMMARY.md`.
Record: the byte-identity golden hash, the region-1-topology test result (n_zeroed_pairs==6),
the deferred §5/§6 boundary (psd_method/psd_lambda filled at fit time), and the residual
Track-A byte-identity risk note (source() path resolution under LSF cwd; BLAS/LAPACK
determinism unchanged from the inline version).
</output>
