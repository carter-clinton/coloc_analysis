---
phase: 260619-qjy
plan: 01
type: tdd
wave: 1
depends_on: []
files_modified:
  - tests/m3/test_ld_npz_to_rds.py
  - src/python/bm_to_npz.py
autonomous: true
requirements:
  - AF-SIDECAR-01   # bm_to_npz.py carries allele_freq from A.3 sidecar into the .npz contract
user_setup: []

must_haves:
  truths:
    - "bm_to_npz with --allele-freq writes a row-aligned allele_freq array into the .npz"
    - "A genuinely-missing AF entry (blank sidecar line) round-trips to NaN, never a fake 0.0 (WR-03)"
    - "Omitting --allele-freq writes an all-NaN allele_freq key of length n_rows AND prints a loud stdout WARNING"
    - "A row-misaligned AF sidecar (length != n_rows) raises a loud ValueError naming region/lengths"
    - "AF flows from an A.3-style .npz (lower_triangular + allele_freq) into obj$variants$AF via ld_npz_to_rds.R"
  artifacts:
    - path: "src/python/bm_to_npz.py"
      provides: "Optional --allele-freq CLI arg + allele_freq_tsv param; NaN-aware float loader; allele_freq key always emitted into savez_compressed"
      contains: "allele_freq"
    - path: "tests/m3/test_ld_npz_to_rds.py"
      provides: "RED-first converter-level + A.3 end-to-end AF round-trip tests"
      contains: "allele_freq"
  key_links:
    - from: "src/python/bm_to_npz.py"
      to: "np.savez_compressed"
      via: "allele_freq= kwarg (always present; NaN-filled when sidecar omitted)"
      pattern: "savez_compressed[\\s\\S]*allele_freq="
    - from: "src/python/bm_to_npz.py allele_freq array"
      to: "ld_npz_to_rds.R obj$variants$AF"
      via: ".npz allele_freq key read as z$f[[\"allele_freq\"]]"
      pattern: "allele_freq"
---

<objective>
Close the A.3 AF sidecar gap: `src/python/bm_to_npz.py` is the middle converter
between the AoU-side `{rid}.allele_freq.tsv` sidecar (already produced by
`aou_ld_panel.py`) and the R reader (`ld_npz_to_rds.R`, which already reads
`z$f[["allele_freq"]]` into `obj$variants$AF`). The converter currently writes
`ld/variant_ids/rsids/lower_triangular` but NOT `allele_freq`, so allele
frequency dies in the middle and every Path A.3 (large/xlarge) region ships with
NA AF.

This is a production-precondition for the m3-04 A.3 fire ("do not ship A.3 as
LD+AF until closed"). Per project rigor-over-speed mandate, this is TDD /
RED-first.

Purpose: make AF flow end-to-end for A.3 regions, with the missing-vs-zero
distinction (WR-03 NaN, never fake 0.0) preserved, and a forgotten sidecar made
LOUD (warning + all-NaN key), never silent.

Output: `bm_to_npz.py` gains an optional `--allele-freq` arg + always-emitted
`allele_freq` .npz key; new RED-first tests proving the contract.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md

# THE file to modify (currently writes ld/variant_ids/rsids/lower_triangular, no allele_freq):
@src/python/bm_to_npz.py

# The test file to EXTEND (RED-first):
@tests/m3/test_ld_npz_to_rds.py

<interfaces>
<!-- Contracts the executor needs. Extracted from the codebase. Do NOT explore. -->

DO NOT MODIFY these two files — they are already correct (committed m3-02b):

From src/python/aou_ld_panel.py (the AoU-side AF producer — READ ONLY for contract):
```python
def _af_or_nan(af: "float | None") -> float:
    # WR-03: a NULL AF maps to float('nan'), NOT a fake 0.0. For a MAF>=0.005
    # prefiltered cohort a true 0.0 is impossible, so 0.0 would mask a fault.
    if af is None:
        return float("nan")
    return float(af)
```
The A.3 branch writes a row-aligned `{rid}.allele_freq.tsv` sidecar (one float
per line, in BlockMatrix row order, NaN for missing) alongside variant_ids/rsids.

From src/scripts/ld_npz_to_rds.R (the R reader — READ ONLY for contract):
```r
# Reads the allele_freq array if present (row-aligned to variant_ids); else NA.
allele_freq_in <- tryCatch(as.numeric(z$f[["allele_freq"]]), error = function(e) NULL)
if (is.null(allele_freq_in) || length(allele_freq_in) != n_input) {
  allele_freq_in <- rep(NA_real_, n_input)
}
# ... after liftover drop:
allele_freq_in <- allele_freq_in[keep]   # aligned to kept rows
# ... carried into the saved RDS:
variants <- parse_variants_frame(snp_ids_grch37, af = allele_freq_in)  # obj$variants$AF
```
So the .npz MUST carry an `allele_freq` key (numeric, row-aligned to
variant_ids) for AF to land in `obj$variants$AF`.

From src/python/bm_to_npz.py (THE file to modify):
```python
def _load_sidecar(path: Path) -> np.ndarray:
    # loads a 1-col TSV as dtype=str, ndmin=1. NOT suitable for AF (need float+NaN).
    ...
def bm_to_npz(bm_dir, variant_ids_tsv, rsids_tsv, out_npz, block_size_hint=None) -> None:
    ...
    variant_ids = _load_sidecar(variant_ids_tsv)
    rsids = _load_sidecar(rsids_tsv)
    if variant_ids.shape[0] != n_rows:   # loud-guard pattern to mirror for AF
        raise ValueError(f"variant_ids length {variant_ids.shape[0]} != BlockMatrix rows {n_rows}")
    if rsids.shape[0] != n_rows:
        raise ValueError(f"rsids length {rsids.shape[0]} != BlockMatrix rows {n_rows}")
    lower = np.tril(ld_dense)
    np.savez_compressed(str(out_npz), ld=lower, variant_ids=variant_ids,
                        rsids=rsids, lower_triangular=np.array([True]))
```

bm_to_npz.py has NO production code caller — it is a manual CLI run by Carter on
NCSU GPFS after `gsutil cp -r` of the egressed .bm + sidecars. So there is NO
downstream caller to re-wire; just add the new CLI arg + function param.
</interfaces>
</context>

<feature>
  <name>bm_to_npz.py carries allele_freq from the A.3 sidecar into the .npz contract</name>
  <files>tests/m3/test_ld_npz_to_rds.py, src/python/bm_to_npz.py</files>
  <behavior>
    Converter-level (no R required; uses a hand-built .npz contract — does NOT
    require Hail for the new tests, can construct inputs directly OR Hail-gate
    like test_bm_to_npz_helper):

      - With --allele-freq sidecar: the emitted .npz has an `allele_freq` key,
        numeric, length == n_rows, row-aligned. A blank/empty sidecar line
        round-trips to np.nan (WR-03: genuinely-missing AF is NaN, never 0.0).
        e.g. AF = [0.12, "", 0.34] -> npz allele_freq = [0.12, nan, 0.34].
      - Without --allele-freq: the emitted .npz STILL has an `allele_freq` key,
        all-NaN, length == n_rows; AND a loud stdout WARNING line is printed
        (substring "WARNING" + "no --allele-freq"). Absence is VISIBLE, not silent.
      - Row-misaligned AF sidecar (length != n_rows) raises a loud ValueError
        naming the lengths (mirror the variant_ids/rsids length asserts), region/
        out-name included.
      - Existing keys unchanged: ld (lower-tri only), variant_ids, rsids,
        lower_triangular=[True] still present (no regression of the BR-01 fix).

    A.3 end-to-end round-trip (R-env-gated skip via rscript_or_skip; mirror the
    existing R-execution tests):

      - A hand-constructed A.3-shaped .npz (np.tril ld + variant_ids + rsids +
        lower_triangular=[True] + allele_freq=[0.12, 0.34]) fed to
        ld_npz_to_rds.R yields obj$variants$AF == [0.12, 0.34] (row-aligned,
        survives liftover). This proves the bm_to_npz OUTPUT CONTRACT carries AF
        into obj$variants$AF. Use coords that lift cleanly (FTO ~53.8 Mb) so
        neither variant is dropped. Reading obj$variants$AF requires extending
        the _read_rds R reader to also dump variants$AF (auto_unbox + na="null").
  </behavior>
  <implementation>
    Implementation comes AFTER the RED tests in Task 1. In Task 2:

    1. Add a NaN-aware float sidecar loader to bm_to_npz.py (do NOT reuse
       _load_sidecar — it is dtype=str). Read lines, strip; empty/blank ->
       np.nan, else float(); return np.asarray(dtype=float). Mirror _af_or_nan's
       missing->nan semantics. Honor ndmin=1 single-row safety (1-D even for one
       value). np.loadtxt(dtype=float) errors on blanks, so parse line-wise.

    2. Add `--allele-freq` (dest allele_freq_tsv, optional, type=Path, default
       None) to the argparser; add `allele_freq_tsv: Path | None = None` param to
       bm_to_npz() and pass it through from main().

    3. In bm_to_npz(): if allele_freq_tsv is not None -> load via the float loader;
       assert len == n_rows with a loud ValueError naming lengths + out_npz; else
       allele_freq = np.full(n_rows, np.nan) AND print a loud WARNING naming out_npz
       (e.g. "WARNING: no --allele-freq sidecar provided; writing all-NaN AF — "
       "A.3 region {out_npz} will have NA AF").

    4. Add `allele_freq=allele_freq` to the existing np.savez_compressed call
       (key ALWAYS present). Leave ld/variant_ids/rsids/lower_triangular unchanged.

    5. Update the module docstring Usage block (show the new --allele-freq line +
       the {rid}.allele_freq.tsv sidecar) and the bm_to_npz() docstring Args.
  </implementation>
</feature>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1 (RED): add failing AF-contract tests to test_ld_npz_to_rds.py</name>
  <files>tests/m3/test_ld_npz_to_rds.py</files>
  <behavior>
    These tests MUST FAIL against the current bm_to_npz.py (no allele_freq key,
    no --allele-freq arg):
    - test_bm_to_npz_writes_allele_freq_when_provided: build a small synthetic
      Hail BlockMatrix (mirror test_bm_to_npz_helper, pytest.importorskip("hail"))
      OR — to avoid Hail dependence — assert at the CLI/contract layer. Provide an
      AF sidecar with a blank middle line; invoke bm_to_npz.py via subprocess with
      --allele-freq; load the .npz; assert "allele_freq" in z.files, length ==
      n_rows, row-aligned values, and the blank entry is np.nan (np.isnan).
    - test_bm_to_npz_omitted_allele_freq_is_all_nan_and_warns: invoke without
      --allele-freq; assert "allele_freq" in z.files, all np.isnan, length n_rows,
      and the loud WARNING substring appears in captured stdout.
    - test_bm_to_npz_misaligned_allele_freq_raises: AF sidecar length != n_rows ->
      non-zero return code + ValueError text naming the lengths in stderr.
    - test_a3_style_npz_carries_af_into_variants (rscript_or_skip): hand-build an
      A.3-shaped .npz (np.tril ld + 2 liftable vids + rsids + lower_triangular=
      [True] + allele_freq=[0.12,0.34]); run ld_npz_to_rds.R; assert
      obj$variants$AF == [0.12, 0.34]. Extend the inline _read_rds R reader (or add
      a small local reader) to dump variants$AF with na="null".
    Use the existing rscript_or_skip / chain_38_to_37 fixtures + _run_converter.
    Do NOT introduce silent passes; R-family test skips with the existing
    diagnostic when m3-r-ld env is absent.
  </behavior>
  <action>
    Extend tests/m3/test_ld_npz_to_rds.py with the four tests above (and any small
    helper to write an AF sidecar TSV / build an AF-bearing .npz). For the
    converter-level tests, prefer the subprocess-CLI pattern of
    test_bm_to_npz_helper so PATH-resolution mirrors production; if Hail is
    required to build the .bm, pytest.importorskip("hail") + graceful skip on init
    failure exactly like the existing helper test. The misaligned + omitted tests
    should use the smallest viable BlockMatrix. The A.3 end-to-end test hand-builds
    the .npz directly (no Hail) and is R-env-gated. Run the suite to confirm RED.
    GPFS rule: stage with explicit paths only — never `git add -A`/`.`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && python -m pytest tests/m3/test_ld_npz_to_rds.py -k "allele_freq or a3_style" -x 2>&1 | tail -30</automated>
  </verify>
  <done>
    New tests collected and FAIL (RED) against current bm_to_npz.py with messages
    pointing at the missing allele_freq key / --allele-freq arg (NOT errors/skips
    masking the failure; R-env-gated test may skip if m3-r-ld absent, but the
    converter-level AF tests must RUN and FAIL).
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2 (GREEN): implement --allele-freq + always-emit allele_freq key in bm_to_npz.py</name>
  <files>src/python/bm_to_npz.py</files>
  <behavior>
    After this task the Task 1 tests pass:
    - --allele-freq sidecar loads as float with blank->NaN (WR-03), row-aligned.
    - Misaligned sidecar -> loud ValueError naming lengths + out path.
    - Omitted sidecar -> all-NaN allele_freq key (length n_rows) + loud stdout WARNING.
    - allele_freq key ALWAYS present in savez_compressed; ld/variant_ids/rsids/
      lower_triangular keys unchanged (BR-01 fix intact).
  </behavior>
  <action>
    Implement per the <implementation> block above:
    1. Add a NaN-aware float loader (line-wise parse; blank->np.nan; ndmin=1).
    2. Add --allele-freq (dest allele_freq_tsv, optional) to argparse; add
       allele_freq_tsv: Path | None = None param to bm_to_npz(); thread from main().
    3. Load when provided + loud-guard length == n_rows ValueError (mirror the
       variant_ids/rsids asserts at lines ~108-115, include out_npz in the message);
       else np.full(n_rows, np.nan) + loud stdout WARNING naming out_npz.
    4. Add allele_freq=allele_freq to the existing np.savez_compressed call. Do NOT
       touch the ld/variant_ids/rsids/lower_triangular keys.
    5. Update the module docstring Usage block + bm_to_npz() Args docstring to
       document --allele-freq and the {rid}.allele_freq.tsv sidecar (row-aligned,
       NaN for missing).
    Do NOT modify aou_ld_panel.py or ld_npz_to_rds.R. GPFS: explicit-path staging only.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && python -m pytest tests/m3/test_ld_npz_to_rds.py -k "allele_freq or a3_style" 2>&1 | tail -20</automated>
  </verify>
  <done>
    The Task 1 AF tests pass (GREEN); the A.3 end-to-end test passes when m3-r-ld is
    present (else skips with diagnostic). bm_to_npz.py emits allele_freq in every
    .npz; blank entries are NaN; omission warns loudly; misalignment raises.
  </done>
</task>

<task type="auto">
  <name>Task 3 (REGRESSION): full tests/m3 suite — no regressions vs 194/0/30 baseline</name>
  <files>tests/m3/test_ld_npz_to_rds.py, src/python/bm_to_npz.py</files>
  <action>
    Run the entire m3 test suite. Baseline before this plan was 194 passed / 0
    failed / 30 skipped. After the change the new AF tests add to passed (or to
    skipped only for the R-env-gated A.3 test when m3-r-ld is absent); existing 194
    must remain green; the BR-01 tests (test_bm_to_npz_static_writes_lower_triangular_flag,
    test_bm_style_lower_tri_npz_recovers_true_r, test_bm_to_npz_helper) must still
    pass — confirming the allele_freq addition did not disturb ld/lower_triangular.
    If any prior test regresses, fix bm_to_npz.py (NOT the test) before declaring done.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && python -m pytest tests/m3 2>&1 | tail -15</automated>
  </verify>
  <done>
    0 failed. Prior 194 still pass; BR-01 tests still pass; new AF converter tests
    pass; the A.3 end-to-end test passes or skips-with-diagnostic (never silent-pass).
    Skipped count >= 30 (R-env gating may add the A.3 test to skips when m3-r-ld absent).
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| egressed sidecar TSV -> bm_to_npz.py | Carter-supplied `{rid}.allele_freq.tsv` (post-AoU egress) read off NCSU GPFS; trusted academic provenance but content-validated for shape |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-qjy-01 | Tampering | row-misaligned AF sidecar silently shifting AF onto wrong variants | mitigate | loud ValueError when allele_freq length != n_rows (row-alignment invariant), naming lengths + out path |
| T-qjy-02 | Information disclosure | manual A.3 converter on already-egressed BlockMatrix | accept | inherits the existing T-M3-EGR-W3 ACCEPT in bm_to_npz.py docstring; no AoU access, no individual-level data, AF is a population summary statistic |
| T-qjy-03 | Repudiation | a forgotten --allele-freq silently shipping NA AF (the exact gap this closes) | mitigate | omission writes all-NaN key AND prints loud stdout WARNING; absence is auditable, not silent; WR-03 keeps missing(NaN) distinct from a real 0.0 |
</threat_model>

<verification>
- `pytest tests/m3/test_ld_npz_to_rds.py -k "allele_freq or a3_style"` RED before Task 2, GREEN after.
- `pytest tests/m3` shows 0 failed, prior 194 intact, BR-01 tests intact.
- `grep -n "allele_freq" src/python/bm_to_npz.py` shows: float loader, length-guard, savez_compressed key, docstring mention.
- aou_ld_panel.py and ld_npz_to_rds.R unchanged (`git diff --stat` lists only test + bm_to_npz.py).
</verification>

<success_criteria>
- bm_to_npz.py: optional --allele-freq arg + allele_freq_tsv param; NaN-aware float
  loader (blank->NaN, WR-03); loud length-guard ValueError; loud all-NaN WARNING on omission;
  allele_freq key ALWAYS emitted into the .npz; ld/variant_ids/rsids/lower_triangular unchanged.
- AF demonstrably flows from an A.3-style .npz into obj$variants$AF via ld_npz_to_rds.R
  (R-env-gated test, no silent pass).
- tests/m3: 0 failed; new RED-first AF tests pass; no regression to the 194 baseline.
- aou_ld_panel.py + ld_npz_to_rds.R untouched.
</success_criteria>

<output>
After completion, create `.planning/quick/260619-qjy-close-a-3-af-sidecar-gap-allele-freq-for/260619-qjy-SUMMARY.md`
</output>
