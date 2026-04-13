---
phase: 02-3-way-qtl-colocalization
fixed_at: 2026-04-13T01:59:47Z
review_path: .planning/phases/02-3-way-qtl-colocalization/02-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 02: Code Review Fix Report

**Fixed at:** 2026-04-13T01:59:47Z
**Source review:** .planning/phases/02-3-way-qtl-colocalization/02-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 7
- Fixed: 7
- Skipped: 0

## Fixed Issues

### CR-01: Shell injection via unsanitized file paths in subprocess call

**Files modified:** `src/python/sample_null_loci.py`
**Commit:** 9d8d0ba
**Applied fix:** Replaced `shell=True` subprocess call with a safe three-stage pipeline using `subprocess.Popen` (cat, sort, bedtools merge). File paths are passed as list arguments, eliminating command injection via shell metacharacters. Added return code checking on `merge_proc`.

### CR-02: pph4_threshold_sweep rule writes tier assignments instead of sweep table

**Files modified:** `src/snakemake/rules/negative_controls.smk`
**Commit:** de24f16
**Applied fix:** Added explicit `--sweep-output {output.sweep_table}` argument and routed `--output` to `/dev/null`. Previously, `--output` received the Snakemake-declared sweep path but `assign_tiers.py` wrote the full tier assignment table there instead (sweep went to a derived `_sweep.tsv` path). Now the sweep table lands at the declared output path.

### WR-01: TLS certificate verification disabled for onek1k.org downloads

**Files modified:** `src/python/download_onek1k.py`
**Commit:** 9a802dd
**Applied fix:** Removed `--no-check-certificate` from the wget command in `download_onek1k_org()`. Added comment referencing T-02-01 mitigation. If the S3 endpoint has certificate issues, wget will now fail with a clear error rather than silently accepting potentially tampered data.

### WR-02: pysam TabixFile resource leak

**Files modified:** `src/python/harmonize_eqtl.py`
**Commit:** ee6bd00
**Applied fix:** Wrapped `pysam.TabixFile(input_path)` in a `with` context manager. Previously, `tbx.close()` was only called on the success path (after the fetch loop). If an exception occurred during `tbx.fetch()`, the file handle leaked. The context manager ensures cleanup on both success and exception paths.

### WR-03: Broad except clauses mask real errors in download_ukbppp.py

**Files modified:** `src/python/download_ukbppp.py`
**Commit:** ccf1189
**Applied fix:** Narrowed `except Exception` to `except (synapseclient.core.exceptions.SynapseError, FileNotFoundError, ConnectionError, TimeoutError, OSError)`. This catches all expected Synapse API failures and network errors while letting programming errors (`TypeError`, `AttributeError`), memory errors, and auth misconfiguration bubble up instead of silently falling back to S3.

### WR-04: Missing logging.basicConfig in several scripts

**Files modified:** `src/python/harmonize_eqtl.py`, `src/python/harmonize_sqtl.py`, `src/python/harmonize_onek1k.py`, `src/python/download_onek1k.py`
**Commit:** 5260342
**Applied fix:** Added `logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")` at the top of each script's `main()` function. This ensures log messages (warnings about empty results, failed tabix queries, liftover problems) are visible when scripts are run standalone outside Snakemake.

### WR-05: harmonize_onek1k.py row-by-row liftover will be extremely slow for large files (fixed: requires human verification)

**Files modified:** `src/python/harmonize_onek1k.py`
**Commit:** f6c4aba
**Applied fix:** Two changes: (1) Changed `except ImportError` from a warning-and-continue to a hard `raise ImportError` with an actionable message. This is critical because without liftover, onek1k_org GRCh37 positions would be used against GRCh38 region filters, silently dropping most/all variants. (2) Replaced `df.iterrows()` loop with `df.apply()` and a helper function for the liftover step, which is more idiomatic. Note: for truly large files, a subprocess-based CrossMap approach would be faster; this fix addresses the correctness issue (silent wrong coordinates) as the priority.

## Skipped Issues

None -- all findings were fixed.

---

_Fixed: 2026-04-13T01:59:47Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
