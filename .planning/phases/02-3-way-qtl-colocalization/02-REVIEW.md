---
phase: 02-3-way-qtl-colocalization
reviewed: 2026-04-12T21:30:00Z
depth: standard
files_reviewed: 38
files_reviewed_list:
  - config/negative_controls.yaml
  - config/pph4_thresholds.yaml
  - config/qtl_sources.yaml
  - config/regions_curated_grch38.csv
  - config/susie_policy.yaml
  - envs/qtl_processing.yml
  - Snakefile
  - src/python/assign_tiers.py
  - src/python/build_gene_tissue_matrix.py
  - src/python/build_protein_ensembl_map.py
  - src/python/build_tissue_n_lookup.py
  - src/python/download_onek1k.py
  - src/python/download_ukbppp.py
  - src/python/estimate_sdy.py
  - src/python/harmonize_eqtl.py
  - src/python/harmonize_onek1k.py
  - src/python/harmonize_pqtl.py
  - src/python/harmonize_sqtl.py
  - src/python/liftover_regions.py
  - src/python/parse_l2g.py
  - src/python/sample_null_loci.py
  - src/python/variant_id_map.py
  - src/snakemake/rules/negative_controls.smk
  - src/snakemake/rules/qtl_coloc.smk
  - src/snakemake/rules/qtl_download.smk
  - src/snakemake/scripts/run_qtl_coloc.R
  - tests/phase2/conftest.py
  - tests/phase2/generate_qtl_fixtures.py
  - tests/phase2/test_config_validation.py
  - tests/phase2/test_harmonize_eqtl.py
  - tests/phase2/test_harmonize_pqtl.py
  - tests/phase2/test_harmonize_sqtl.py
  - tests/phase2/test_liftover.py
  - tests/phase2/test_negative_controls.py
  - tests/phase2/test_onek1k_harmonize.py
  - tests/phase2/test_pph4_sweep.py
  - tests/phase2/test_run_qtl_coloc.py
  - tests/phase2/test_tier_assignment.py
findings:
  critical: 2
  warning: 5
  info: 4
  total: 11
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-04-12T21:30:00Z
**Depth:** standard
**Files Reviewed:** 38
**Status:** issues_found

## Summary

Reviewed all 38 source files comprising the Phase 2 QTL colocalization pipeline: 4 YAML configs, 1 CSV, 1 conda env, 1 top-level Snakefile, 14 Python processing scripts, 3 Snakemake rule files, 1 R script, and 13 test files. The codebase is well-structured with clean separation between download, harmonization, coloc dispatch, and tier assignment stages. Column mappings are config-driven, and threat mitigations (T-02-xx) are consistently referenced.

Two critical issues were found: a shell injection vector in `sample_null_loci.py` and a Snakemake rule that will write the wrong output file. Five warnings cover a TLS bypass in downloads, missing `logging.basicConfig()` calls, broad exception handling hiding real errors, and a `pysam.TabixFile` resource leak. Four informational items note unused imports, redundant variable re-definitions, and a dead code path.

## Critical Issues

### CR-01: Shell injection via unsanitized file paths in subprocess call

**File:** `src/python/sample_null_loci.py:132-134`
**Issue:** The `cat_cmd` string is built by interpolating `exclusion_parts` (which contain file paths) directly into a shell command string, then executed with `shell=True`. If any path in `exclusion_parts` (derived from `args.blacklist`) contains shell metacharacters, this enables command injection. While the blacklist path is typically from a Snakemake rule parameter, the script can also be run as a standalone CLI where `--blacklist` comes from user input.
**Fix:**
```python
# Replace shell=True with a safe subprocess pipeline:
import shlex

# Instead of:
#   cat_cmd = f"cat {' '.join(exclusion_parts)} | sort -k1,1 -k2,2n | bedtools merge"
#   subprocess.run(cat_cmd, shell=True, ...)

# Use:
cat_proc = subprocess.Popen(
    ["cat"] + exclusion_parts,
    stdout=subprocess.PIPE,
)
sort_proc = subprocess.Popen(
    ["sort", "-k1,1", "-k2,2n"],
    stdin=cat_proc.stdout,
    stdout=subprocess.PIPE,
)
cat_proc.stdout.close()
merge_proc = subprocess.Popen(
    ["bedtools", "merge"],
    stdin=sort_proc.stdout,
    stdout=subprocess.PIPE,
    text=True,
)
sort_proc.stdout.close()
stdout, _ = merge_proc.communicate()
with open(exclusion_bed, "w") as f:
    f.write(stdout)
```

### CR-02: pph4_threshold_sweep rule writes tier assignments instead of sweep table

**File:** `src/snakemake/rules/negative_controls.smk:106-128`
**Issue:** The `pph4_threshold_sweep` rule invokes `assign_tiers.py --sweep --output {output.sweep_table}` but does NOT pass `--sweep-output`. In `assign_tiers.py main()`, `--output` is the destination for the full tier assignment table (line 259: `tier_df.to_csv(args.output, ...)`). The sweep output is written to `args.sweep_output or args.output.replace(".tsv", "_sweep.tsv")` (line 265). This means Snakemake expects the sweep at `pph4_threshold_sweep.tsv` but the actual sweep goes to `pph4_threshold_sweep_sweep.tsv`, and the declared output path contains the tier assignments instead. Downstream consumers of this output will get the wrong data.
**Fix:**
```python
# In negative_controls.smk, replace the shell command:
    shell:
        r"""
        python {params.script} \
          --input {input.qtl_results} \
          --pph4-config {input.pph4_config} \
          --sweep \
          --sweep-output {output.sweep_table} \
          --output /dev/null
        """
# Or better: refactor assign_tiers.py to support a --sweep-only mode
# that skips full tier assignment when --gwas-coloc is not provided.
```

## Warnings

### WR-01: TLS certificate verification disabled for onek1k.org downloads

**File:** `src/python/download_onek1k.py:186`
**Issue:** `wget --no-check-certificate` disables TLS certificate verification for onek1k.org S3 downloads. This makes the download vulnerable to MITM attacks that could inject tampered QTL data, which would silently corrupt colocalization results. While this is a fallback path, it downloads data that feeds directly into the scientific pipeline.
**Fix:**
```python
# Remove --no-check-certificate. If the S3 endpoint has cert issues,
# download the CA bundle or use requests with verify=True:
subprocess.run(
    ["wget", "-q", "-O", out_path, url],
    check=True,
    timeout=3600,
)
# If the cert is genuinely invalid, document the risk and add a
# hash verification step after download (T-02-01 pattern).
```

### WR-02: pysam TabixFile resource leak

**File:** `src/python/harmonize_eqtl.py:190-212`
**Issue:** `pysam.TabixFile(input_path)` is opened but `tbx.close()` is only called on the success path (line 212). If an exception occurs during the `tbx.fetch()` loop (lines 201-208), the file handle leaks. This can exhaust file descriptors when processing many regions in parallel on an HPC node.
**Fix:**
```python
def _read_with_tabix(input_path: str, region: dict) -> pd.DataFrame:
    import pysam

    region_chr = str(region["chr"])
    region_start = int(region["start"])
    region_end = int(region["end"])

    with pysam.TabixFile(input_path) as tbx:
        header = tbx.header
        if header:
            col_names = header[-1].lstrip("#").split("\t")
        else:
            with gzip.open(input_path, "rt") as f:
                col_names = f.readline().strip().split("\t")

        rows = []
        for chr_fmt in [region_chr, f"chr{region_chr}", region_chr.replace("chr", "")]:
            try:
                for row in tbx.fetch(chr_fmt, region_start, region_end):
                    rows.append(row.split("\t"))
                if rows:
                    break
            except ValueError:
                continue

    if not rows:
        return pd.DataFrame(columns=col_names)
    return pd.DataFrame(rows, columns=col_names)
```

### WR-03: Broad except clauses mask real errors in download_ukbppp.py

**File:** `src/python/download_ukbppp.py:117-119`
**Issue:** `except Exception as e:` catches all exceptions from the Synapse download path and falls back to S3. This hides real errors like `MemoryError`, `KeyboardInterrupt` (via `BaseException` but close pattern), disk full (`OSError`), or authentication misconfiguration. A user with an expired token would silently fail to S3 without ever knowing their token was bad.
**Fix:**
```python
# Narrow the exception to expected failure modes:
except (synapseclient.exceptions.SynapseHTTPError,
        synapseclient.exceptions.SynapseError,
        FileNotFoundError,
        ConnectionError,
        TimeoutError) as e:
    logger.warning("Synapse download failed: %s. Trying S3 fallback.", e)
    return _download_from_s3(protein, chromosome, output_dir)
```

### WR-04: Missing logging.basicConfig in several scripts

**File:** `src/python/harmonize_eqtl.py`, `src/python/harmonize_sqtl.py`, `src/python/harmonize_onek1k.py`, `src/python/download_onek1k.py`
**Issue:** These scripts create a `logger` via `logging.getLogger(__name__)` but never call `logging.basicConfig()` in their `main()` functions (unlike `assign_tiers.py` and `sample_null_loci.py` which do). When run as standalone scripts (not through Snakemake), all log messages including warnings about empty results, failed tabix queries, and liftover problems are silently dropped. This makes debugging pipeline failures significantly harder.
**Fix:**
```python
# Add at the top of each main() function:
def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # ... rest of main
```

### WR-05: harmonize_onek1k.py row-by-row liftover will be extremely slow for large files

**File:** `src/python/harmonize_onek1k.py:200-209`
**Issue:** The onek1k.org fallback path iterates `df.iterrows()` to liftover each variant position individually via `pyliftover`. For a typical OneK1K cell type file with hundreds of thousands of variants, this will take hours per file due to Python loop overhead. While the eQTL Catalogue path avoids this, if the eQTL Catalogue download fails for any cell type, the fallback path is effectively unusable at scale. The liftover should also warn that coordinates remain in GRCh37 if pyliftover is not available (line 212-215), because using GRCh37 positions with a GRCh38 region filter will silently drop most/all variants.
**Fix:**
```python
# Vectorize the liftover using a list comprehension and batch approach,
# or better, pre-lift the onek1k.org data with CrossMap (already in
# the conda env) before reading into pandas:
#
# Option 1: Use CrossMap via subprocess:
# subprocess.run(["CrossMap.py", "bed", chain_file, input_bed, output_bed])
#
# Option 2: At minimum, change the warning to an error when pyliftover
# is unavailable, since the data will be silently wrong:
except ImportError:
    raise ImportError(
        "pyliftover is required for onek1k_org format (GRCh37->GRCh38 liftover). "
        "Install with: pip install pyliftover"
    )
```

## Info

### IN-01: Unused import of `re` in build_protein_ensembl_map.py

**File:** `src/python/build_protein_ensembl_map.py:14`
**Issue:** `import re` is present but `re` is never used directly -- the regex operations use `str.match()` on pandas Series (line 76, 144), which does not require `re` to be imported.
**Fix:** Remove `import re` from line 14.

### IN-02: Redundant NEG_CTRL_DIR re-definition in qtl_coloc.smk

**File:** `src/snakemake/rules/qtl_coloc.smk:236`
**Issue:** `NEG_CTRL_DIR` is re-defined in `qtl_coloc.smk` line 236 with a comment acknowledging the duplication: "Redefined here for self-contained reference; Snakemake tolerates re-assignment." While technically harmless, this creates a maintenance risk -- if the definition in `negative_controls.smk` changes, the copy here could diverge silently.
**Fix:** Remove the re-definition and rely on the include-order guarantee documented in the Snakefile (negative_controls.smk is included before qtl_coloc.smk).

### IN-03: Broad except in build_protein_ensembl_map.py HGNC API fallback

**File:** `src/python/build_protein_ensembl_map.py:134`
**Issue:** `except Exception as e:` in the HGNC API lookup catches all exceptions, including programming errors. This is a rate-limited network call so transient errors are expected, but catching `Exception` rather than specific network errors (`urllib.error.URLError`, `json.JSONDecodeError`, `TimeoutError`) makes it harder to detect bugs in the API parsing logic.
**Fix:** Narrow to `except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:`.

### IN-04: Dead code path in negative_controls.yaml cosmetic/blood_group sets

**File:** `config/negative_controls.yaml:14-28`
**Issue:** The `cosmetic` and `blood_group` sets define `regions_grch37` (GRCh37 coordinates) but no `regions_grch38`. When `build_neg_ctrl_manifest()` in `sample_null_loci.py` processes these sets (line 273-279), it uses GRCh37 coordinates as-is with a comment "liftover handled elsewhere." However, no downstream liftover is actually applied to these coordinates before they reach `run_qtl_coloc.R`, which expects GRCh38. The `hla_immune` set correctly provides `region_grch38`. The cosmetic and blood_group sets will produce incorrect region coordinates in the negative control manifest.
**Fix:** Add `regions_grch38` entries to the cosmetic and blood_group sets in `config/negative_controls.yaml`, matching the pattern used by `hla_immune`. Alternatively, add liftover logic in `build_neg_ctrl_manifest()` for sets that only provide GRCh37 coordinates.

---

_Reviewed: 2026-04-12T21:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
