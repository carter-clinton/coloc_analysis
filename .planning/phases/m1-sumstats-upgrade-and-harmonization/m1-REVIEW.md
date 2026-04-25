---
phase: m1-sumstats-upgrade-and-harmonization
reviewed: 2026-04-25T15:36:24Z
depth: standard
files_reviewed: 33
files_reviewed_list:
  - src/python/sumstats_utils.py
  - src/python/m1_raw_glob.py
  - src/python/freeze_sha256_manifest.py
  - src/python/harmonize_yengo.py
  - src/python/harmonize_glgc.py
  - src/python/harmonize_wuttke.py
  - src/python/harmonize_magic.py
  - src/python/harmonize_diamante.py
  - src/python/harmonize_gigastroke.py
  - src/python/harmonize_aragam.py
  - src/python/harmonize_gbmi.py
  - src/python/verify_evangelou_sbp.py
  - src/python/munge_sumstats_ldsc.py
  - src/python/m1_trait_keys.py
  - src/python/reduce_ldsc_rg_matrix.py
  - src/python/build_trait_inventory.py
  - src/python/verify_m1_artifacts.py
  - src/python/render_qc_html_minimal.py
  - src/snakemake/rules/m1_download.smk
  - src/snakemake/rules/m1_harmonize.smk
  - src/snakemake/rules/m1_munge.smk
  - src/snakemake/rules/m1_ldsc_rg.smk
  - src/snakemake/rules/m1_qc.smk
  - src/R/qc/m1_qc_report.qmd
  - src/R/qc/m1_qc_index.qmd
  - bin/download_sumstats_v2.sh
  - bin/fire_m1_03_munge_and_rg.sh
  - bin/fire_m1_03_complete.sh
  - envs/m1-harmonize.yml
  - envs/m1-munge.yml
  - envs/m1-ldsc-rg.yml
  - envs/m1-download.yml
  - envs/m1-qc.yml
  - config/pipeline.yaml
findings:
  critical: 3
  warning: 16
  info: 6
  total: 25
status: issues_found
---

# Phase M1: Code Review Report

**Reviewed:** 2026-04-25T15:36:24Z
**Depth:** standard
**Files Reviewed:** 33 (1 config additionally read for cross-reference; not in scope list)
**Status:** issues_found

## Summary

Reviewed the M1 sumstats-upgrade-and-harmonization phase: 18 Python modules
(harmonizers, munge wrapper, reducers, verifiers), 5 Snakemake rule files,
2 Quarto QC templates, 3 bash drivers, and 5 conda env pins. The codebase
is generally rigorous: B-2 column guards, palindromic-MAF filter, b38→b37
liftover with chain-name guard, Pitfall #7 wrong-direction-lift catch, and
explicit `--no-mtime` SHA-256 manifest determinism are all present.
Path-parameterization is consistently honored in src/snakemake/rules and
src/python.

Three correctness issues warrant immediate attention before re-fire:

1. **m1_qc.smk parallel Quarto race** — every per-trait render writes
   `m1_qc_report.html` into the same QC_DIR before being moved by an
   `if [ -f ... ]` block. Concurrent renders clobber each other.
2. **harmonize_gbmi.py emits no QC sidecar** — m1_harmonize.smk synthesizes
   a stub via `python -c` that omits `n_input` / `n_output` /
   `n_palindromic_dropped` / `n_maf_below_threshold`, so verify_d/e/g all
   SKIP for the asthma cells.
3. **harmonize_gbmi.py applies no MAF filter** — palindromic filter only;
   inconsistent with the D-12 `--maf-min 0.005` floor every other M1
   harmonizer enforces.

Sixteen warnings cover NaN/Inf propagation in effective-N math, a Quarto
race, hardcoded snakemake-cached env paths, indirect-bash-variable cookie
dereference, type-coercion gaps in CHR comparisons, and a few file-handle
patterns. Six info items capture duplication (b2_guard / dual-emit /
coerce in every harmonizer) and minor robustness suggestions.

No SQL injection, no eval, no unsafe deserialization, no hardcoded
secrets, no `dangerouslySetInnerHTML`-style sinks. The shell drivers
quote variables consistently and parse TSV rows via `IFS` + `read -r`
rather than `eval`.

## Critical Issues

### CR-01: Race condition in `m1_qc_per_trait` Quarto render

**File:** `src/snakemake/rules/m1_qc.smk:44-61`
**Issue:** Every per-trait render runs `quarto render src/R/qc/m1_qc_report.qmd --output-dir {QC_DIR}`. Quarto names its output after the source `.qmd` basename, so every job writes to `{QC_DIR}/m1_qc_report.html` then moves it via `if [ -f ... ]; then mv ...` in a separate shell step. With Snakemake `--cores N>1` (or LSF parallel jobs), two harmonized traits rendering simultaneously will race on the same `m1_qc_report.html` filename — last-writer-wins for the source HTML, then both `mv` calls compete and one trait's report ends up containing another trait's content (or empty, if the mv races between produce-and-move).
**Fix:** Render into a per-trait temp dir, then move:
```bash
TMPDIR=$(mktemp -d -p {QC_DIR} qc_render.XXXXXX)
quarto render {input.qmd} \
  --to html \
  --output-dir "$TMPDIR" \
  -P trait:{wildcards.trait} \
  -P ancestry:{wildcards.ancestry} \
  -P consortium:{wildcards.consortium} \
  -P year:{wildcards.year} \
  -P parquet:{input.parquet} \
  -P harmonized_tsv:{params.harmonized_tsv} \
  -P rg_log_dir:{params.rg_log_dir} \
  -P qc_json:{params.qc_json} \
  -P control_loci_csv:{input.loci}
mv "$TMPDIR/m1_qc_report.html" {output.html}
rm -rf "$TMPDIR"
```
The same fix applies to `m1_qc_index` (line 79–90), although that rule is single-output and won't race with itself.

### CR-02: `harmonize_gbmi.py` does not emit a QC sidecar; smk stub omits required fields

**File:** `src/python/harmonize_gbmi.py:156-168` and `src/snakemake/rules/m1_harmonize.smk:864-865`
**Issue:** `harmonize_gbmi_sumstats` returns a `qc` dict but never writes it to disk. The Snakemake rule then synthesizes a sidecar via `python -c "import json; print(json.dumps({{'trait': 'asthma', 'ancestry': '{wildcards.ancestry}', 'consortium': 'GBMI', 'year': 2022, 'phenotype_lock': '...', 'build_target': 'GRCh37', 'liftover_chain': '{input.chain}'}}, indent=2))" > {output.qc_json}`. That stub has none of: `n_input`, `n_output`, `n_palindromic_dropped`, `n_maf_below_threshold`, `liftover_drop_rate`. As a result:
- `verify_m1_artifacts.verify_d` (MAF=0 fraction) SKIPs every asthma cell.
- `verify_m1_artifacts.verify_e` (palindromic drop < 10%) SKIPs every asthma cell.
- `render_qc_html_minimal._per_trait_html` shows "—" for the §7 §1 + §8 rows.
- `m1_qc_report.qmd` §8 falls into `palin_status = "SKIP"` (line 219–224) for every asthma trait.

**Fix:** Add a `--qc-json` argument to `harmonize_gbmi.py` and write the qc dict from inside the function (mirroring the other harmonizers). Then drop the `python -c` stub from `m1_harmonize.smk`. Concrete patch (harmonize_gbmi.py):
```python
def harmonize_gbmi_sumstats(
    input_gz: Path,
    output_prefix: Path,
    trait: str,
    ancestry: str = "eur",
    liftover_chain: "Path | None" = None,
    qc_json_path: "Path | None" = None,
    maf_min: float = 0.005,
) -> dict:
    ...
    qc["n_input"]  = int(n_input_pre_filters)   # capture before filters
    qc["n_output"] = int(len(df))
    qc["n_palindromic_dropped"] = n_palin
    qc["n_maf_below_threshold"] = n_maf
    qc["maf_min"] = maf_min
    if qc_json_path is not None:
        qc_json_path.parent.mkdir(parents=True, exist_ok=True)
        qc_json_path.write_text(json.dumps(qc, indent=2, default=str) + "\n")
    return qc
```
And in `_main()`:
```python
ap.add_argument("--qc-json", type=Path, default=None)
ap.add_argument("--maf-min", type=float, default=0.005)
```
And in m1_harmonize.smk replace the `python -c "..." > {output.qc_json}` line with `--qc-json {output.qc_json}` on the harmonize_gbmi.py invocation.

### CR-03: `harmonize_gbmi.py` skips MAF=0.005 floor; inconsistent with all other M1 harmonizers

**File:** `src/python/harmonize_gbmi.py:128-150`
**Issue:** Every other M1 harmonizer (`harmonize_yengo`, `harmonize_glgc`, `harmonize_wuttke`, `harmonize_magic`, `harmonize_diamante`, `harmonize_gigastroke`, `harmonize_aragam`) applies a MAF >= 0.005 filter from CONTEXT D-12 before the palindromic filter. `harmonize_gbmi.py` applies only `filter_palindromic_ambiguous`. asthma×{MULTI,EUR,AFR} parquet/tsv outputs therefore retain MAF<0.005 variants that downstream LDSC munge will drop anyway, but this also means the verify_d "MAF=0 fraction < 5%" gate is computed against a different denominator than peer cells.
**Fix:**
```python
# After df = _su.filter_palindromic_ambiguous(df):
af = pd.to_numeric(df["EAF"], errors="coerce")
maf = af.where(af < 0.5, 1 - af)
keep_maf = maf >= maf_min
n_maf = int((~keep_maf).sum())
df = df.loc[keep_maf].reset_index(drop=True)
qc["n_maf_below_threshold"] = n_maf
qc["maf_min"] = maf_min
```
Add `--maf-min` CLI argument with default 0.005.

## Warnings

### WR-01: Inf/NaN propagation in DIAMANTE effective-N computation

**File:** `src/python/harmonize_diamante.py:162-167`
**Issue:** `df["N"] = 4.0 / (1.0 / nc + 1.0 / nk)`. When either `nc==0` or `nk==0` (rare DIAMANTE rows), `1.0/0` raises ZeroDivisionError under numpy strict, but with the default pandas-numeric coercion it produces `inf`, then `4.0 / (inf + ...)` is `0.0`. So rows with N_case==0 silently get `N=0` rather than being filtered. Same pattern in `harmonize_aragam.py:288-290` for the Klarin path with `df["N"] = nc.fillna(0) + nk.fillna(0)` (NaN→0 silently produces N=0 rows).
**Fix:** Replace the inline div with the shared helper, and filter zero-N rows:
```python
from sumstats_utils import compute_effective_n
nc = pd.to_numeric(df_raw["N_case"], errors="coerce")
nk = pd.to_numeric(df_raw["N_control"], errors="coerce")
mask = (nc > 0) & (nk > 0)
df = df.loc[mask].copy()
df["N"] = 4.0 / (1.0 / nc[mask] + 1.0 / nk[mask])
qc["n_dropped_zero_n"] = int((~mask).sum())
```

### WR-02: Hardcoded snakemake-cached LDSC env path in `munge_sumstats_ldsc.py`

**File:** `src/python/munge_sumstats_ldsc.py:357-362`
**Issue:** The fallback for an LDSC-capable Python interpreter is hardcoded to `.snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python`. The `481e5f...` hash is a content-addressed snakemake env hash that changes whenever `envs/m1-munge.yml` changes (channel ordering, version pin, transitive deps). This will silently break next time the env file is touched.
**Fix:** Resolve dynamically by globbing `.snakemake/conda/*/bin/python` and probing each for `bitarray`. Or better: require `--ldsc-python` to be supplied explicitly by the Snakemake rule (which knows its conda env path via `${CONDA_PREFIX}/bin/python`). Concrete:
```python
cached = sorted(Path(".snakemake/conda").glob("*/bin/python"))
for cand in cached:
    if subprocess.run([str(cand), "-c", "import bitarray"],
                      capture_output=True).returncode == 0:
        ldsc_python = str(cand)
        break
else:
    raise RuntimeError(
        "LDSC munge requires bitarray; tried "
        f"sys.executable + {len(cached)} cached envs. "
        "Set LDSC_PYTHON or --ldsc-python explicitly."
    )
```

### WR-03: Indirect bash variable expansion of cookie env name (download driver)

**File:** `bin/download_sumstats_v2.sh:86-94`
**Issue:** `cookie_value="${!cookie_env_name:-}"` performs indirect expansion of any string supplied in the manifest's `requires_cookie_env` column. If a manifest row contains, e.g., `requires_cookie_env=PATH`, `${!cookie_env_name}` expands to `$PATH` and is passed as a `-b` cookie header to curl. The TSV is checked-in and authored by Carter, so this is not an injection vector against an external attacker — but it does mean a copy/paste typo in the manifest (e.g. `DIAMANTE_COKIE` matching `DIAMANTE_COOKIE_BACKUP`) silently uses the wrong cookie.
**Fix:** Validate cookie_env_name against an allow-list before expansion:
```bash
case "$cookie_env_name" in
    NONE|"") ;;
    DIAMANTE_COOKIE) cookie_value="${!cookie_env_name:-}" ;;
    *) echo "ERROR: unrecognized cookie_env_name '$cookie_env_name'" >&2; return 1 ;;
esac
```

### WR-04: `m1_munge.smk` `_DEFERRED_GUARD` writes empty `.sumstats.gz` that downstream LDSC may consume

**File:** `src/snakemake/rules/m1_munge.smk:91-100`
**Issue:** The guard does `touch {output.munged}` after `touch {output.munged}.deferred` and exits 0. The 0-byte `.sumstats.gz` will then be picked up by `m1_ldsc_rg_star._others_input` if its trait_key happens to land in `trait_keys.txt`. LDSC reading a 0-byte gzip will error out with an opaque message (likely `EOFError: Compressed file ended before the end-of-stream marker was reached`). The actual mitigation today is that `_read_trait_keys` reads `trait_keys.txt` produced by `m1_build_trait_keys_list` from `SUMSTATS-UPGRADE.tsv`, not from disk — so deferred cells in the TSV are still listed unless dropped. The `bin/fire_m1_03_munge_and_rg.sh` driver (Stage 2) builds trait_keys.txt from disk via `ls "$MUNGED"/*.sumstats.gz` (Stage 2 line 100–103); 0-byte files survive that glob.
**Fix:** Make Stage 2 in `bin/fire_m1_03_munge_and_rg.sh` skip 0-byte files:
```bash
ls -l "$MUNGED"/*.sumstats.gz 2>/dev/null \
  | awk '$5 > 0 {print $NF}' \
  | xargs -n1 basename \
  | sed 's/\.sumstats\.gz$//' \
  | sort -u > "$OVERLAP/trait_keys.txt"
```
And/or have `_DEFERRED_GUARD` emit only `.deferred` and NOT `touch {output.munged}` (declare a separate output marker instead). The latter requires updating Snakemake DAG semantics, so the Stage-2 awk filter is the lower-risk fix.

### WR-05: NaN / boundary EAF handling in MAF filter is silent

**File:** `src/python/harmonize_yengo.py:219-222`, `src/python/harmonize_glgc.py:173-177`, `src/python/harmonize_wuttke.py:160-164`, `src/python/harmonize_diamante.py:180-183`, `src/python/harmonize_gigastroke.py:209-212`, `src/python/harmonize_aragam.py:155-158`
**Issue:** `maf = df["EAF"].where(df["EAF"] < 0.5, 1 - df["EAF"])`. For NaN EAF, the predicate `df["EAF"] < 0.5` is False, so `maf = 1 - df["EAF"]` = NaN. Then `keep_maf = NaN >= 0.005` is False, so NaN-EAF rows are silently dropped along with low-MAF rows in the `n_maf_below_threshold` count. The qc.json conflates these two failure modes.
**Fix:** Track NaN-EAF separately:
```python
af = pd.to_numeric(df["EAF"], errors="coerce")
n_nan_eaf = int(af.isna().sum())
maf = af.where(af < 0.5, 1 - af)
keep_maf = maf >= maf_min
qc["n_eaf_nan_dropped"] = n_nan_eaf
qc["n_maf_below_threshold"] = int((~keep_maf).sum() - n_nan_eaf)
```

### WR-06: `verify_evangelou_sbp.py` flags valid files when EAF/P contain any NaN

**File:** `src/python/verify_evangelou_sbp.py:145-154`
**Issue:** `df["EAF"].between(0, 1).all()` returns False if any row has NaN EAF. NaN is not in `[0,1]`. Most large GWAS sumstats have a small NaN tail (variants without MAF estimate). The verifier will raise AssertionError on those, even though the underlying file is correctly b37 / canonical. The check intends "EAF values that ARE present must be in [0,1]".
**Fix:**
```python
eaf_present = df["EAF"].dropna()
if not eaf_present.between(0, 1).all():
    bad_eaf = df[~df["EAF"].fillna(0.5).between(0, 1)].head(3)
    raise AssertionError(
        f"Evangelou verify FAILED: EAF out of [0, 1] on rows like:\n{bad_eaf}"
    )
# Same for P:
p_present = df["P"].dropna()
if not p_present.between(0, 1).all():
    ...
```

### WR-07: `verify_evangelou_sbp.py` silently ignores X/Y/MT chromosomes in b37 invariant

**File:** `src/python/verify_evangelou_sbp.py:131-143`
**Issue:** `df["_chr_i"] = df["CHR"].map(_chrom_int)` returns None for X/Y/MT/0. The subsequent loop only checks rows where `_chr_i == chrom in 1..22`, so a row with `CHR='X' BP=999999999` is not caught by the b37 chromosome-length invariant. If the source file is actually b38 with a misnamed X, the verifier passes.
**Fix:** Add a `n_dropped_non_autosome` count to the QC dict and either (a) reject the file if the fraction exceeds a threshold, or (b) extend `CHR_MAX_B37` with X/Y entries:
```python
CHR_MAX_B37 = {..., 23: 155270560, 24: 59373566}  # X, Y in b37
# and treat 'X','Y' / 'chrX','chrY' as 23/24 in _chrom_int:
def _chrom_int(c) -> "int | None":
    s = str(c).replace("chr", "").upper()
    if s == "X": return 23
    if s == "Y": return 24
    if s in ("MT", "M"): return None  # mitochondria — exclude
    try: return int(s)
    except ValueError: return None
```

### WR-08: `harmonize_gigastroke.py` raises at module import on placeholder TSV

**File:** `src/python/harmonize_gigastroke.py:80-107`
**Issue:** `_reload_filenames()` is called at module load (line 107: `GIGASTROKE_FILENAMES = _reload_filenames()`), and raises `RuntimeError` if any GIGASTROKE row in the SUMSTATS-UPGRADE.tsv still has the `GCST90104540-series` placeholder. Side-effect: any tooling that imports this module — including pytest collection, IDE static analysis, `pydoc`, `python -c "import harmonize_gigastroke"` — breaks before the user can call the harmonizer. This is a Wave-0 hygiene check that should be deferred until `harmonize_gigastroke()` actually fires.
**Fix:** Lazily evaluate inside the function:
```python
GIGASTROKE_FILENAMES: dict | None = None  # lazy

def _ensure_filenames_loaded():
    global GIGASTROKE_FILENAMES
    if GIGASTROKE_FILENAMES is None:
        GIGASTROKE_FILENAMES = _reload_filenames()

def harmonize_gigastroke(...):
    _ensure_filenames_loaded()
    ...
```

### WR-09: Symbol-table assertion in `m1_trait_keys.py` is stripped under `python -O`

**File:** `src/python/m1_trait_keys.py:99-102`
**Issue:** `assert _MIN_KEYS <= len(keys) <= _MAX_KEYS, "..."` is the only enforcement of the 40<=N<=50 inventory-hygiene bound. With `python -O` (or `PYTHONOPTIMIZE=1`), `assert` is stripped at compile time and the helper silently returns whatever count it finds. Smoke fixtures that intentionally violate the bound depend on catching `AssertionError` — also broken under `-O`.
**Fix:**
```python
if not (_MIN_KEYS <= len(keys) <= _MAX_KEYS):
    raise ValueError(
        f"m1_trait_keys: expected {_MIN_KEYS}<=N<={_MAX_KEYS} keys, got {len(keys)}. "
        f"Inspect SUMSTATS-UPGRADE.tsv for new rows or DEFERRED churn."
    )
```
Tests that previously caught `AssertionError` should be updated to catch `ValueError`.

### WR-10: `bin/fire_m1_03_munge_and_rg.sh` hardcodes absolute conda + bim paths

**File:** `bin/fire_m1_03_munge_and_rg.sh:25-35`
**Issue:** Three absolute HPC-scratch paths are hardcoded:
```
SMOKE_PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
LDSC_PY=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python
export PATH=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin:$PATH
```
`verify_m1_artifacts.verify_req_path_parameterization` excludes `bin/` from its grep target list (line 322–333) — this is intentional per the verifier comment "REQ-PATH-PARAM applies to source code authored in M1 (m1-00..m1-04)". So it doesn't FAIL the closeout. But it DOES break reproducibility for any other operator (or any future re-fire after env rebuild — same hash drift as WR-02).
**Fix:** Read these from environment variables with sensible-default fallbacks:
```bash
SMOKE_PY="${SMOKE_PY:-$(command -v python)}"
LDSC_PY="${LDSC_PY:-$(ls -d .snakemake/conda/*/bin/python 2>/dev/null | head -1)}"
[ -x "$LDSC_PY" ] || { echo "ERROR: LDSC_PY not resolvable"; exit 1; }
```

### WR-11: `m1_qc_report.qmd` chr-column comparison is type-coercion fragile

**File:** `src/R/qc/m1_qc_report.qmd:192`
**Issue:** `df[df[[chr_col]] == as.character(row$chr) & df[[bp_col]] >= win_lo & ...` — if the parquet reads `CHR` as integer (post-harmonization, our coerce step casts CHR to str but parquet round-trip can re-infer types), comparing `int == as.character()` returns FALSE everywhere and `n_variants_in_window` is always 0, falsely triggering WARN on §7 control loci.
**Fix:** Explicit cast on both sides:
```r
chr_match <- as.character(df[[chr_col]]) == as.character(row$chr)
sub <- df[chr_match & df[[bp_col]] >= win_lo & df[[bp_col]] <= win_hi, , drop = FALSE]
```

### WR-12: `m1_harmonize.smk` GBMI rule uses inline `python -c` for parquet conversion

**File:** `src/snakemake/rules/m1_harmonize.smk:858-865`
**Issue:** Two consecutive `python -c "..."` invocations build the parquet sidecar and the qc.json. The strings interpolate `{params.ancestry_lc}`, `{wildcards.ancestry}`, `{input.chain}`, and `{output.tsv_bgz}` directly into the python source. Wildcards are constrained to safe charsets (`MULTI|EUR|AFR`), but `{input.chain}` and `{output.tsv_bgz}` are paths that, while safe in this codebase, are fragile if anything ever lands a `'` or backslash in a path. Also: this duplicates parquet-write logic already present in every other harmonizer.
**Fix:** Move parquet write + qc.json write into `harmonize_gbmi.py` (resolves CR-02 + CR-03 + WR-12 together). Replace lines 851–866 with a single call:
```bash
python src/python/harmonize_gbmi.py \
    --input {params.raw} \
    --output {output.tsv_bgz}.tmp.tsv.gz \
    --parquet {output.parquet} \
    --qc-json {output.qc_json} \
    --trait asthma \
    --ancestry {params.ancestry_lc} \
    --maf-min 0.005 \
    --liftover-chain {input.chain}
zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
rm -f {output.tsv_bgz}.tmp.tsv.gz
```

### WR-13: `harmonize_aragam.py` Klarin schema is unverified placeholder

**File:** `src/python/harmonize_aragam.py:62-77`
**Issue:** Comment block explicitly states "best-effort guess; verify against actual file at fire time — Wave 1 has not located the file yet". `KLARIN_COLS = {"ID":"SNP", "CHROM":"CHR", "POS":"BP", "ALT":"EA", "REF":"OA", "AF":"EAF", ...}`. If this map is wrong, `_b2_guard` raises ValueError (good) — but a partial match (e.g. PLINK2 sumstats output that shares some column names but uses `BETA_LOG_OR` instead of `BETA`) would pass `_b2_guard` and silently produce a frame with the wrong effect statistic.
**Fix:** Add a sentinel field-validation step that looks at the first row's BETA value and confirms it's in a plausible range for log-odds (|β| < 5). And lock `KLARIN_COLS` behind an "unverified" flag that requires the caller to pass `--klarin-schema-confirmed` after eyeballing the actual file:
```python
def harmonize_aragam_klarin2018(..., schema_confirmed: bool = False, ...):
    if not schema_confirmed:
        raise NotImplementedError(
            "Klarin 2018 schema is unverified (best-effort placeholder). "
            "Fire with --klarin-schema-confirmed only after verifying KLARIN_COLS "
            "against the actual file headers."
        )
```

### WR-14: `download_sumstats_v2.sh` lacks `set -e`; `set -uo pipefail` only

**File:** `bin/download_sumstats_v2.sh:41`
**Issue:** Only `set -uo pipefail` is set. This is by design (xargs -P 5 should not propagate one row failure into the whole batch), but `fetch_one` itself can hit unhandled errors above the `if curl ...` block (e.g., the `mkdir -p "$destdir"` on line 75 has no error handling — if the parent path is unwritable, `mkdir` fails silently and `curl` then writes nothing because `$dest` doesn't exist either; the `if [ -f "$dest" ] && [ -s "$dest" ]` skip check passes through fine but the failure is not logged in `$FAIL_LOG`).
**Fix:** Add explicit error handling around `mkdir`:
```bash
if ! mkdir -p "$destdir" 2>/dev/null; then
    echo "${ts} FAIL_MKDIR: $destdir" | tee -a "$FAIL_LOG"
    return 1
fi
```

### WR-15: `harmonize_diamante.py` silently drops X/Y/MT chromosomes during sort

**File:** `src/python/harmonize_diamante.py:191-197`
**Issue:** `df["_chr_sort"] = pd.to_numeric(df["CHR"], errors="coerce"); df = df.dropna(subset=["_chr_sort"]).sort_values(...)` drops any non-numeric CHR (X, Y, MT) silently. Same pattern in `harmonize_gigastroke.py:222-226` and `harmonize_aragam.py:166-170`. The QC sidecar should at minimum log how many rows were dropped.
**Fix:**
```python
df["_chr_sort"] = pd.to_numeric(df["CHR"], errors="coerce")
n_non_autosome = int(df["_chr_sort"].isna().sum())
qc["n_non_autosome_dropped"] = n_non_autosome
df = df.dropna(subset=["_chr_sort"]).sort_values(["_chr_sort", "BP"]) \
       .drop(columns=["_chr_sort"]).reset_index(drop=True)
```
Per CONTEXT D-01 the autosome-only restriction may be intentional (no X-stratified GWAS in M1 scope), but it should be auditable.

### WR-16: `m1_raw_glob.py` reads PORTAL_MANIFEST twice

**File:** `src/python/m1_raw_glob.py:64-90`
**Issue:** The function reads `PORTAL_MANIFEST` once at line 65 to find the target_dir for the deferred check, then re-reads it at line 77 for the actual file resolution. Each invocation re-parses ~50-row TSV from disk. With ~36-46 trait keys in the manifest and Snakemake `params: lambda` being called once per rule per DAG evaluation, this becomes O(N²) reads. Not catastrophic at this scale (TSV is small) but trivially fixable.
**Fix:** Read once and reuse the dataframe:
```python
df = pd.read_csv(PORTAL_MANIFEST, sep="\t") if PORTAL_MANIFEST.exists() else None
if df is not None:
    row = df[df["source_tag"] == source_tag]
    if len(row) == 1:
        cand_dir = Path(row["target_dir"].iloc[0])
        if (cand_dir / ".deferred").exists():
            return DEFERRED_SENTINEL
        ...
```

## Info

### IN-01: Duplicated `_b2_guard` / `_emit_dual_artifacts` / `_coerce_canonical_dtypes` across 7 harmonizers

**File:** `src/python/harmonize_yengo.py:92-130`, `src/python/harmonize_glgc.py:87-115`, `src/python/harmonize_wuttke.py:65-93`, `src/python/harmonize_magic.py:82-109`, `src/python/harmonize_diamante.py:58-89`, `src/python/harmonize_gigastroke.py:110-140`, `src/python/harmonize_aragam.py:109-139`
**Issue:** The same three helpers (B-2 column guard, dual TSV+parquet emit, dtype coercion) are reimplemented in seven harmonizers with subtle variations (one upper-cases EA/OA, one doesn't; one coerces CHR to str inside, one does it after). Drift across these copies is a real risk as M1 grows.
**Fix:** Promote to `sumstats_utils`. Single `_b2_guard(df, col_map, source) -> df` and `emit_dual_artifacts(df, tsv_gz, parquet)` and `coerce_canonical_dtypes(df, allele_upper=True)` — every harmonizer becomes a thin column-map + filter wrapper.

### IN-02: Module-level rsid lookup cache in `sumstats_utils._rsid_lookup_cache` never cleared

**File:** `src/python/sumstats_utils.py:351`
**Issue:** `_rsid_lookup_cache` is populated by `build_rsid_to_chrpos` and never cleared. ~9.5M entries × 22 chromosomes per `bim_prefix` × however many prefixes are loaded over a long-running interpreter (e.g. tests). Each Snakemake rule invocation runs in a fresh subprocess so this is bounded in production. Notable for unit tests that load multiple bim_prefixes.
**Fix (optional):** Provide `clear_rsid_lookup_cache()` for test fixtures and document the cache lifecycle.

### IN-03: `validate_canonical_frame` only spot-checks the first non-null value of EA/OA

**File:** `src/python/sumstats_utils.py:333-342`
**Issue:** The allele-column type check inspects only `df[c].dropna().head(1)`. A column that is `["A", 42, "G", ...]` (object dtype with mixed types) passes if the first non-null is "A". This is permissive by design (object dtype + mixed types is hard to constrain in pandas), but downstream `df["EA"].str.upper()` will fail for the integer entries.
**Fix:** Document the limitation explicitly, or use `df[c].apply(lambda x: isinstance(x, str) or pd.isna(x)).all()` for full coverage on a sample of N>1.

### IN-04: `reduce_ldsc_rg_matrix.validate_self_consistency` diagonal check is effectively a no-op

**File:** `src/python/reduce_ldsc_rg_matrix.py:217-226`
**Issue:** `build_intercept_matrix` sets every diagonal entry to 1.0 by convention (line 141). The subsequent `bad_diag` check at line 218–222 then verifies the diagonal is ~1.0 — but it always is by construction, so this branch never fires. The check would only catch a mutation between assembly and validation.
**Fix:** Either remove the dead check or replace it with a "diagonal contains some NaN" sanity check (which would catch absent trait keys). The latter is more useful:
```python
n_diag_nan = int(np.isnan(np.diag(mat.values)).sum())
if n_diag_nan > 0:
    warnings.append(f"Diagonal contains {n_diag_nan} NaN — missing trait keys?")
```

### IN-05: `freeze_sha256_manifest.py` sort key is filesystem-locale dependent only via Python str compare

**File:** `src/python/freeze_sha256_manifest.py:84`
**Issue:** `files.sort(key=lambda r: r[0])` uses Python's default str comparison (Unicode codepoint), which is locale-INdependent — good for determinism. Worth a comment so future maintainers don't `import locale; locale.strcoll` "to fix it".
**Fix (optional):** Add `# Codepoint-ordered sort guarantees byte-identical TSV across locales/platforms.` above the sort call.

### IN-06: Missing log handler / progress reporting in long-running rg-star fire

**File:** `bin/fire_m1_03_munge_and_rg.sh:148-181`
**Issue:** `xargs -P "$jobs_p" -I {} bash -c '...'` echoes start/end markers but provides no aggregate progress. With 22 parallel jobs and ~45 traits, mid-run visibility is poor. Stage-3 rgstar wall ranges from minutes to hours depending on `pair_wall`. Not a correctness issue.
**Fix (optional):** Pipe through `pv -l` or maintain a simple counter file.

---

_Reviewed: 2026-04-25T15:36:24Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
