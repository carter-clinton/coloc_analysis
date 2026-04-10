---
phase: 00-data-access-infrastructure
reviewed: 2026-04-10T16:15:00Z
depth: standard
files_reviewed: 26
files_reviewed_list:
  - config/pipeline.yaml
  - config/datasets.yaml
  - config/cluster_lsf.yaml
  - envs/r_coloc.yml
  - envs/python_stats.yml
  - envs/plink.yml
  - src/R/utils/load_config.R
  - data/manifest.yaml
  - src/snakemake/schemas/pipeline.schema.yaml
  - src/snakemake/schemas/datasets.schema.yaml
  - Snakefile
  - src/snakemake/rules/sumstats.smk
  - src/snakemake/rules/regions.smk
  - src/snakemake/rules/ld_reference.smk
  - src/snakemake/rules/finemap.smk
  - src/snakemake/rules/qc.smk
  - src/snakemake/rules/multitrait.smk
  - src/snakemake/rules/mr.smk
  - src/snakemake/rules/pgs.smk
  - src/python/liftover.py
  - config/regions_curated.csv
  - tests/toy_3locus/Snakefile.test
  - tests/toy_3locus/config_test.yaml
  - tests/toy_3locus/data/regions_toy.csv
  - tests/toy_3locus/expected/expected_results.yaml
  - scripts/subset_toy_loci.py
  - scripts/run_ci_smoke.sh
findings:
  critical: 3
  warning: 5
  info: 4
  total: 12
status: issues_found
---

# Phase 0: Code Review Report

**Reviewed:** 2026-04-10T16:15:00Z
**Depth:** standard
**Files Reviewed:** 26
**Status:** issues_found

## Summary

Reviewed the complete Phase 0 infrastructure: Snakemake pipeline config, conda environments, rule files, schemas, Python scripts, R utility, and CI smoke test harness. The codebase is well-structured with zero hardcoded absolute paths (REQ-12 satisfied), proper schema validation, and clean separation of concerns across rule modules.

Three critical issues were found: (1) missing `FINEMAP_MANIFEST` and `HARMONIZED_ALL` definitions in the test Snakefile causing `NameError` at parse time, (2) HIS ancestry in the global `ancestries` list has no 1000 Genomes population mapping, causing LD pipeline failures, and (3) two Snakemake rules invoke scripts without passing any I/O arguments, disconnecting declared Snakemake contracts from actual execution. Five warnings address shell injection in subprocess calls, a chrX region with no LD panel coverage, a potential conda environment build failure for `r-hyprcoloc`, and dead code in MD5 validation. No hardcoded secrets, credentials, or absolute paths were found.

## Critical Issues

### CR-01: Test Snakefile missing FINEMAP_MANIFEST and HARMONIZED_ALL before include

**File:** `tests/toy_3locus/Snakefile.test:82`
**Issue:** The test Snakefile includes `finemap.smk` at line 82, but `FINEMAP_MANIFEST` is never defined, and `HARMONIZED_ALL` is defined at line 104 (after the include). `finemap.smk` references both variables in rule definitions (lines 31 and 34), which are evaluated at parse time. This causes a `NameError` when `FINEMAP_METHODS` is non-empty (which it is, since `config_test.yaml` sets `finemap.methods: [susie]`).

**Fix:** Define `FINEMAP_MANIFEST` and `HARMONIZED_ALL` before the finemap include block, mirroring the production Snakefile's structure:
```python
# Move HARMONIZED_ALL above the includes (before line 70)
HARMONIZED_ALL = [
    os.path.join(HARMONIZED_DIR, f"{trait}.{ancestry}.tsv.bgz")
    for trait, ancestry in TRAIT_ANCESTRY_PAIRS
]

# Add FINEMAP_MANIFEST definition before the finemap include (before line 81)
if FINEMAP_METHODS:
    FINEMAP_MANIFEST = os.path.join(FINEMAP_DIR, "finemap_manifest.tsv")
    UNIQUE_TRAIT_ANC = sorted(set(TRAIT_ANCESTRY_PAIRS))
else:
    FINEMAP_MANIFEST = None
```

### CR-02: HIS ancestry has no 1000 Genomes population mapping -- LD pipeline will fail

**File:** `config/pipeline.yaml:17`
**Issue:** `HIS` is listed in the global `ancestries` array (line 17) and in `trait_ancestries.hypertension` (line 39), but has no entry in `onekg.populations` (lines 46-49). When `enable_ld_pipeline: true`, the Snakefile (lines 117-125) generates LD targets for all `ANCESTRIES` including HIS. The `build_1kg_sample_lists` rule will have no HIS population codes to extract, and `build_ld_rds` will fail with a missing sample list file for HIS.

**Fix:** Either add a HIS/AMR proxy population mapping to `onekg.populations`, or exclude HIS from LD target generation:

Option A -- Add population mapping:
```yaml
onekg:
  populations:
    AFR: ["YRI", "LWK", "GWD", "MSL", "ESN"]
    EUR: ["CEU", "TSI", "GBR", "FIN", "IBS"]
    EAS: ["CHB", "JPT", "CHS", "CDX", "KHV"]
    HIS: ["MXL", "PUR", "CLM", "PEL"]  # AMR super-population as HIS proxy
```

Option B -- Filter LD targets to only ancestries with population mappings (in Snakefile):
```python
LD_ANCESTRIES = [a for a in ANCESTRIES if a in config["onekg"]["populations"]]
if ENABLE_LD:
    LD_TARGETS = [
        os.path.join(config["paths"]["ld_reference"], ancestry, f"{region_safe}.rds")
        for ancestry in LD_ANCESTRIES
        for _, region_safe in REGION_INFOS
    ]
```

### CR-03: Two Snakemake rules invoke scripts without passing I/O arguments

**File:** `src/snakemake/rules/multitrait.smk:274-277`
**Issue:** Rules `build_coloc_clean_sets` (line 263) and `build_coloc_h4_reports` (line 280) declare Snakemake `input` and `output` but the `shell` commands call the Python scripts with no arguments at all. The scripts are invoked bare (`{PYTHON_BIN} src/legacy/.../build_coloc_clean_sets.py`) without `--input`, `--output`, or any flags. This means either the scripts have hardcoded paths (violating REQ-12 and making them fail when paths change), or they will fail at runtime because they expect arguments.

**Fix:** Pass the declared inputs and outputs to the scripts:
```python
rule build_coloc_clean_sets:
    # ... (input/output as-is) ...
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_coloc_clean_sets.py \
            --input {input.summary} \
            --output-clean {output.clean} \
            --output-h4 {output.clean_h4}
        """

rule build_coloc_h4_reports:
    # ... (input/output as-is) ...
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_coloc_h4_reports.py \
            --input {input.summary} \
            --output-main {output.main} \
            --output-candidate {output.candidate} \
            --output-counts {output.counts}
        """
```
Verify the actual CLI interface of the legacy scripts before applying this fix.

## Warnings

### WR-01: Shell injection via string formatting in subprocess call

**File:** `scripts/subset_toy_loci.py:45`
**Issue:** The `subset_sumstats` function constructs a shell command by formatting `input_bgz` directly into a string passed to `bash -c`:
```python
header_cmd = ["bash", "-c", "zcat '{}' | head -1".format(input_bgz)]
```
If `input_bgz` contains a single quote followed by shell metacharacters, this enables command injection. While the path is constructed from trusted config values, this pattern is unsafe by design and violates defense-in-depth.

**Fix:** Avoid `bash -c` and use `subprocess.Popen` with a pipe, or use Python's `gzip` module:
```python
import gzip

with gzip.open(input_bgz, 'rt') as f:
    header = f.readline()
```

### WR-02: chrX region in regions_curated.csv has no LD panel coverage

**File:** `config/regions_curated.csv:9`
**Issue:** The region `BMI_Xq24` uses chromosome `X`, but `pipeline.yaml` `onekg.chromosomes` only includes "1" through "22". No VCF will be downloaded for chrX, so any LD-dependent analysis (fine-mapping, coloc requiring LD matrix) for this region will fail at runtime with a missing input file error.

**Fix:** Either add "X" to the `onekg.chromosomes` list and update the VCF template to handle chrX naming:
```yaml
onekg:
  chromosomes:
    # ... existing "1" through "22" ...
    - "X"
```
Or add a note in the regions CSV indicating this region requires special handling and exclude it from LD-dependent rules.

### WR-03: r-hyprcoloc conda package may not exist in specified channels

**File:** `envs/r_coloc.yml:17`
**Issue:** The dependency `r-hyprcoloc=1.0` is listed under conda channels `conda-forge`, `bioconda`, and `defaults`. However, `hyprcoloc` is an R package typically distributed only via GitHub (`jrs95/hyprcoloc`), not through conda channels. If this package is not in the channels, `conda env create -f envs/r_coloc.yml` will fail, blocking all rules that use this environment (coloc, fine-mapping, hyprcoloc analysis).

**Fix:** If `r-hyprcoloc` is not available via conda, install it via `pip` or R's `remotes`:
```yaml
dependencies:
  # ... other deps ...
  - r-remotes
  - pip
  - pip:
    - hyprcoloc  # or use a post-deploy script
```
Or add a post-create hook:
```yaml
# In the env YAML or a separate setup script:
# Rscript -e 'remotes::install_github("jrs95/hyprcoloc")'
```

### WR-04: Snakemake validate_sumstats rule uses fragile inline Python with Snakemake interpolation

**File:** `src/snakemake/rules/sumstats.smk:183-196`
**Issue:** The `validate_sumstats` rule embeds a Python script as a string inside the `shell:` directive, with Snakemake wildcards interpolated directly into the Python source. The path `'{input.harmonized}'` is inserted into a `gzip.open()` call as a Python string literal. If the interpolated path ever contains a single quote (unlikely but possible with certain filename patterns), the Python code would break or execute unintended code.

**Fix:** Extract the inline Python into a standalone script file (e.g., `src/python/validate_sumstats.py`) and pass paths as CLI arguments:
```python
shell:
    r"""
    mkdir -p $(dirname {output.report})
    {PYTHON_BIN} src/python/validate_sumstats.py \
        --input {input.harmonized} \
        --output {output.report} \
        --trait {wildcards.trait} \
        --ancestry {wildcards.ancestry}
    """
```

### WR-05: DATASETS_CONFIG loaded without schema validation in main Snakefile

**File:** `Snakefile:22-23`
**Issue:** The main Snakefile validates `config` (pipeline.yaml) against its schema but loads `datasets.yaml` with raw `yaml.safe_load()` without any schema validation:
```python
with open("config/datasets.yaml") as _dsfh:
    DATASETS_CONFIG = yaml.safe_load(_dsfh)
```
A `datasets.schema.yaml` exists in `src/snakemake/schemas/` but is never used. Malformed datasets config (missing `column_map`, wrong types) would only surface as cryptic runtime errors deep in the harmonization pipeline.

**Fix:** Add schema validation for the datasets config:
```python
from snakemake.utils import validate
with open("config/datasets.yaml") as _dsfh:
    DATASETS_CONFIG = yaml.safe_load(_dsfh)
validate(DATASETS_CONFIG, "src/snakemake/schemas/datasets.schema.yaml")
```

## Info

### IN-01: Dead code in MD5 hash computation loop

**File:** `src/snakemake/rules/sumstats.smk:96-97`
**Issue:** The `iter(lambda: handle.read(8192), b"")` pattern uses a sentinel value of `b""` to stop iteration when `read()` returns an empty bytes object at EOF. The `if not chunk: break` guard on lines 96-97 can never execute because the `iter()` sentinel already prevents empty chunks from being yielded.

**Fix:** Remove the dead guard:
```python
hasher = hashlib.md5()
with open(tmp_path, "rb") as handle:
    for chunk in iter(lambda: handle.read(8192), b""):
        hasher.update(chunk)
```

### IN-02: PYTHON_BIN redefined in every rule file

**File:** `src/snakemake/rules/sumstats.smk:21`, `regions.smk:10`, `ld_reference.smk:19`, `finemap.smk:14`, `qc.smk:10`, `multitrait.smk:14`, `mr.smk:11`, `pgs.smk:11`
**Issue:** `PYTHON_BIN = sys.executable` is defined identically in all 8 rule files. This duplication adds maintenance burden -- if the convention changes (e.g., to use a conda-resolved path), all 8 files must be updated.

**Fix:** Define `PYTHON_BIN` once in the main Snakefile (before the `include` statements) and remove the per-file definitions. Included `.smk` files inherit the parent Snakefile's global namespace.

### IN-03: Empty MD5 checksums in datasets.yaml

**File:** `config/datasets.yaml:35-36` (and many other entries)
**Issue:** Many dataset entries have `md5: ""` (empty string). The download rule at `sumstats.smk:91` correctly skips validation when MD5 is empty, but this means downloaded files are accepted without integrity verification. This is acceptable during development but should be populated before production use.

**Fix:** After downloading each dataset for the first time, compute and record the MD5:
```bash
md5sum cache/downloads/dataset_name/file.gz
```
Update the corresponding `md5:` field in `datasets.yaml`.

### IN-04: Toy test loci regions use different naming convention than production regions

**File:** `tests/toy_3locus/data/regions_toy.csv` vs `config/regions_curated.csv`
**Issue:** Toy regions use subband notation (`FTO_16q12.2`, `TCF7L2_10q25.2`, `SH2B3_12q24.12`) while the production curated regions use shorter IDs (`FTO_16q12`, `SH2B3_12q24`). This is intentional (separate files) but means the safe-ID sanitization (`.` to `_`) produces different IDs between test and production, so test results cannot be directly compared to production region IDs.

**Fix:** No code change needed. Document this naming divergence in the expected_results.yaml or the test README so future maintainers understand the mapping.

---

_Reviewed: 2026-04-10T16:15:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
