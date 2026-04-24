---
plan_id: m1-02a-harmonizers-continuous-traits
phase: m1
plan: 02a
type: execute
wave: 2
depends_on: [m1-00-preflight-and-environment, m1-01-portal-fetches-and-aragam-route]
autonomous: true
requirements: [REQ-TRAIT-INVENTORY, REQ-PATH-PARAMETERIZATION, REQ-SNAKEMAKE-CI]
objective: "Author 4 continuous-trait harmonizers (BMI via Yengo+Loh, lipids via GLGC, eGFR via Wuttke+Morris, HbA1c via MAGIC) emitting canonical 10-column schema + Loh 2022 b38->b37 liftover + palindromic filter + MAF>=0.005 + INFO>=0.8 where present; dual-emit .tsv.bgz + .parquet per D-09."
files_modified:
  - src/python/harmonize_yengo.py
  - src/python/harmonize_glgc.py
  - src/python/harmonize_wuttke.py
  - src/python/harmonize_magic.py
  - src/python/sumstats_utils.py
  - src/python/m1_raw_glob.py
  - src/snakemake/rules/m1_harmonize.smk
  - tests/m1/test_harmonize_yengo.py
  - tests/m1/test_harmonize_glgc.py
  - tests/m1/test_harmonize_wuttke.py
  - tests/m1/test_harmonize_magic.py
  - tests/m1/fixtures/yengo_head.tsv
  - tests/m1/fixtures/loh_head.tsv
  - tests/m1/fixtures/glgc_head.tsv
  - tests/m1/fixtures/wuttke_head.tsv
  - tests/m1/fixtures/morris_afr_head.tsv
  - tests/m1/fixtures/magic_head.tsv
must_haves:
  truths:
    - "harmonize_yengo.py harmonizes Yengo 2018 GIANT+UKBB BMI EUR AND Loh 2022 EUR + AFR (with b38->b37 liftover) to canonical 10-column schema"
    - "harmonize_glgc.py harmonizes all 15 GLGC rows (LDL × 6 ancestries + HDL/TG/TC × 3 ancestries each per D-04) including logTG inverse-normal handling"
    - "harmonize_wuttke.py harmonizes Wuttke 2019 eGFR TRANS + EUR AND Morris 2019 eGFR AFR companion"
    - "harmonize_magic.py harmonizes MAGIC 2021 HbA1c 6 ancestries with rsid -> (chr, pos) forward crosswalk via 1000G bim"
    - "sumstats_utils.py gains build_rsid_to_chrpos(bim_prefix) helper used by harmonize_magic.py"
    - "Each harmonizer emits BOTH .tsv.bgz + tabix index AND .parquet per D-09"
    - "Palindromic filter uses MAF band [0.48, 0.52] via filter_palindromic_ambiguous (never reimplemented)"
    - "Loh 2022 liftover drop-rate is < 5% (hard-fail ceiling via sumstats_utils.liftover_to_grch37)"
    - "W8 fix (option A): m1_raw_glob.resolve_raw_for returns DEFERRED_SENTINEL ('__DEFERRED__') when a `.deferred` marker is present in the resolved target_dir; every harmonize rule's shell prelude branches on this sentinel and emits its own `.deferred` output marker. Closes Loh-EUR/AFR (PENDING_D01_ACCESSION from m1-01 N1 fix) AND any future PENDING_* path symmetrically via a single choke-point change."
  artifacts:
    - path: "src/python/harmonize_yengo.py"
      provides: "Yengo 2018 + Loh 2022 (EUR/AFR) harmonizer with opt-in liftover branch"
      min_lines: 120
    - path: "src/python/harmonize_glgc.py"
      provides: "GLGC Graham 2021 lipids (LDL, HDL, TG, TC × {TRANS, EUR, AFR, EAS, SAS, HIS}) harmonizer with logTG handling"
      min_lines: 120
    - path: "src/python/harmonize_wuttke.py"
      provides: "CKDGen Wuttke 2019 + Morris 2019 AFR companion eGFR harmonizer"
      min_lines: 100
    - path: "src/python/harmonize_magic.py"
      provides: "MAGIC 2021 HbA1c harmonizer with forward rsid->(chr,pos) crosswalk"
      min_lines: 130
    - path: "src/python/sumstats_utils.py"
      provides: "Extended with build_rsid_to_chrpos(bim_prefix)->dict helper"
  key_links:
    - from: "src/python/harmonize_yengo.py"
      to: "src/python/sumstats_utils.py"
      via: "import filter_palindromic_ambiguous, liftover_to_grch37, CANONICAL_COLS"
      pattern: "import sumstats_utils"
    - from: "src/python/harmonize_magic.py"
      to: "src/python/sumstats_utils.py"
      via: "build_rsid_to_chrpos(bim_prefix) call"
      pattern: "build_rsid_to_chrpos"
    - from: "src/snakemake/rules/m1_harmonize.smk"
      to: "src/python/harmonize_{yengo,glgc,wuttke,magic}.py"
      via: "python module invocation per wildcard-expanded rule"
      pattern: "python src/python/harmonize_(yengo|glgc|wuttke|magic)"
---

<objective>
Author 4 of 7 new per-source harmonizers per D-10 — the CONTINUOUS-TRAIT half of the harmonizer suite. Each module reads the raw source-specific file format (already on disk from Wave 1), applies source-specific column-rename map + optional liftover + palindromic filter + MAF/INFO QC, and emits dual artifacts per D-09: `.tsv.bgz` + `.tbi` primary under `data/processed/sumstats_harmonized/` AND `.parquet` mirror under `data/processed/sumstats_harmonized_parquet/`. Filename convention is D-16 dotted lowercase-trait-first: `<trait>.<ancestry>.<consortium>.<year>.GRCh37.tsv.bgz` / `.parquet`.

The 4 continuous-trait harmonizers together cover 24 of the 45 expected (trait, ancestry) cells:
- **harmonize_yengo.py** — 3 cells: bmi.EUR.GIANT-UKBB.2018 (Yengo), bmi.EUR.GIANT-23andMe.2022 (Loh b38→b37), bmi.AFR.GIANT-23andMe.2022 (Loh b38→b37). PAGE BMI AFR 2019 (row 5) is a separate, non-GIANT source and routes through harmonize_yengo's `variant=page2019` codepath since it's also a continuous BMI file.
- **harmonize_glgc.py** — 15 cells (LDL × 6 ancestries + HDL/TG/TC × 3 ancestries) per D-04 frozen fanout. Handles RVTESTS meta tabix-pre-indexed format + logTG inverse-normal handling per TSV row 34 phenotype_definition.
- **harmonize_wuttke.py** — 3 cells: egfr.TRANS.CKDGen.2019 (Wuttke), egfr.EUR.CKDGen.2019 (Wuttke), egfr.AFR.CKDGen.2019 (Morris 2019 companion per TSV row 42).
- **harmonize_magic.py** — 6 cells: hba1c × {TRANS, EUR, AFR, EAS, SAS, HIS}.MAGIC.2021. Handles rsid-only SNP_ID column (RESEARCH pitfall #5) via new `sumstats_utils.build_rsid_to_chrpos(bim_prefix)` forward crosswalk against `data/external/1000G.EUR.QC.{1..22}.bim`.

Purpose: Wave 3 (munge + LDSC rg matrix) consumes exactly the canonical TSV + N column that these harmonizers emit. Wave 4 (Quarto QC) consumes the dual-emit `.parquet` for fast-read variant counts + MAF histograms. M2 (CPASSOC / MTAG) consumes the same dual-emit artifacts. The palindromic filter + Loh liftover hard-fails protect against the exact class of silent-bad-data bugs Phase 09 already trained `sumstats_utils.py` against — reusing the shared helper (not reimplementing) is a hard rule per D-10 + anti-pattern list in m1-RESEARCH.md.
Output: 4 harmonizer modules (~100-150 LoC each per RESEARCH Example 1 template), one Snakemake rules file wiring them to wildcards + config paths, 4 pytest modules asserting the 10-col schema on synthetic fixtures, one extension to sumstats_utils.py for the rsid forward lookup. Harmonized artifacts land under `data/processed/sumstats_harmonized/` + `_parquet/` for all 27 (4+15+3+6-1=27; the Yengo module shares between Yengo/Loh/PAGE codepaths).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-CONTEXT.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-VALIDATION.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-00-preflight-and-environment-PLAN.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-01-portal-fetches-and-aragam-route-PLAN.md
@.planning/phases/09-replication-in-independent-cohorts/09-02-PLAN.md
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@.planning/amendments/SUMSTATS-UPGRADE.md
@src/python/sumstats_utils.py
@src/python/harmonize_gbmi.py
@src/python/harmonize_finngen.py
@src/python/harmonize_bbj.py
@src/python/harmonize_mvp.py
@src/python/munge_sumstats_ldsc.py
@config/pipeline.yaml

<interfaces>
<!-- Canonical schema + helper signatures extracted from src/python/sumstats_utils.py and harmonize_gbmi.py. -->

```python
# src/python/sumstats_utils.py — required imports
CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]

def filter_palindromic_ambiguous(df: pd.DataFrame,
                                 maf_band: tuple[float,float] = (0.48, 0.52)) -> pd.DataFrame: ...

def liftover_to_grch37(df: pd.DataFrame,
                       chain_file: str,
                       chr_col: str = "CHR",
                       bp_col: str = "BP",
                       max_drop_rate: float = 0.05) -> tuple[pd.DataFrame, dict]: ...

def validate_canonical_frame(df: pd.DataFrame) -> None: ...
```

```python
# NEW helper to add to sumstats_utils.py (used only by harmonize_magic.py)
def build_rsid_to_chrpos(bim_prefix: str,
                         chromosomes: list[int] = list(range(1, 23))) -> dict[str, tuple[int,int]]:
    """Build forward rsid -> (chr, bp) lookup from 1000G PLINK bim files.

    Reads files of form {bim_prefix}.{chr}.bim (cols: chr, rsid, cm, bp, a1, a2).
    Returns dict mapping rsid -> (chr:int, bp:int). Memory: ~150MB for 1000G.
    """
```

```python
# D-09 dual-emit pattern — use a shared helper at the end of each harmonizer's main():
def emit_dual_artifacts(df: pd.DataFrame, tsv_bgz_path: Path, parquet_path: Path) -> None:
    """Write df to both .tsv.bgz + .tbi (via pysam) AND .parquet (via pyarrow snappy)."""
    # .tsv.bgz + .tbi via bgzip + tabix (handled in Snakemake shell wrapper; this function
    # writes an intermediate .tsv.gz and the rule bgzips it + tabix-indexes).
    tsv_bgz_path.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(tsv_bgz_path).replace(".tsv.bgz", ".tsv.gz"), sep="\t",
              index=False, compression="gzip")
    df.to_parquet(parquet_path, index=False, compression="snappy")
```

Per Yengo 2018 file (raw) columns (D-10 authoritative):
`SNP, CHR, POS, Tested_Allele, Other_Allele, Freq_Tested_Allele, BETA, SE, P, N`
Rename → CHR, BP, SNP, EA, OA, EAF, BETA, SE, P, N → CANONICAL_COLS reorder.

Per Loh 2022 file (GWAS-Catalog harmonized format) columns:
`variant_id, chromosome, base_pair_location, effect_allele, other_allele,
 effect_allele_frequency, beta, standard_error, p_value, n`
Rename similarly; chromosome/bp are GRCh38 → liftover required per DEC-2026-04-24-01.

Per GLGC file (Graham 2021 RVTESTS meta) columns typically:
`CHROM, POS_b37, rsID, REF, ALT, ALT_FREQ, BETA, SE, PVALUE, N` (header varies;
the logTG file uses log-transformed beta — no transform applied by harmonizer).
`_INV` suffix in filename indicates inverse-normal-transformed (D-10 note).

Per Wuttke 2019 file columns:
`Chr, Pos_b37_hg19, RSID, Allele1, Allele2, Freq1, Effect, StdErr, P-value, n_total_sum` (header
pattern in files at https://ckdgen.imbi.uni-freiburg.de/files/Wuttke2019/).

Per Morris 2019 AFR companion file columns: similar to Wuttke but confirm against the downloaded file in Wave 1; may use `Chromosome, Position, SNP_ID, Effect_Allele, Other_Allele, EAF, BETA, SE, P, N` pattern.

Per MAGIC 2021 Chen file columns:
`SNP_ID, A1, A2, eaf_meta, BETA, SE, P, N_INFO, HetPval`
**Critical — no CHR/BP columns in raw file.** RESEARCH pitfall #5.
Per-ancestry suffix in filename (TA, EUR, AA, EAS, SAS, HISP) maps to local tokens
(TRANS, EUR, AFR, EAS, SAS, HIS).

Phase 09 reference (harmonize_gbmi.py lines 100-130 — the B-2 guard pattern for missing cols):
```python
col_map = {...}  # source -> canonical
missing = [src for src in col_map if src not in df.columns]
if missing:
    raise ValueError(
        f"<source> harmonizer: expected columns {sorted(col_map.keys())} "
        f"but file is missing {missing}. Found columns: {sorted(df.columns.tolist())}.")
df = df[list(col_map.keys())].rename(columns=col_map)
df = df[CANONICAL_COLS]
df = _su.filter_palindromic_ambiguous(df)
```

Each harmonizer CLI (D-16 filename wildcards applied by Snakemake):
```bash
python src/python/harmonize_yengo.py \
  --input  data/raw/sumstats_v2/GIANT2018/BMI/EUR/Meta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz \
  --output data/processed/sumstats_harmonized/bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz \
  --parquet data/processed/sumstats_harmonized_parquet/bmi.EUR.GIANT-UKBB.2018.GRCh37.parquet \
  --variant yengo2018 \
  --trait bmi --ancestry EUR --year 2018 --consortium GIANT-UKBB
```
</interfaces>
</context>

<tasks>

<task id="m1-02a-T1" type="auto" tdd="true">
  <name>Task 1: harmonize_yengo.py (BMI Yengo + Loh + PAGE) + harmonize_glgc.py (lipids) + sumstats_utils extension</name>
  <files>
    src/python/harmonize_yengo.py,
    src/python/harmonize_glgc.py,
    src/python/sumstats_utils.py,
    tests/m1/test_harmonize_yengo.py,
    tests/m1/test_harmonize_glgc.py,
    tests/m1/fixtures/yengo_head.tsv,
    tests/m1/fixtures/loh_head.tsv,
    tests/m1/fixtures/page_bmi_afr_head.tsv,
    tests/m1/fixtures/glgc_ldl_head.tsv,
    tests/m1/fixtures/glgc_tg_logtg_head.tsv
  </files>
  <read_first>
    - src/python/harmonize_gbmi.py (entire file — 154 lines — the B-2 guard + col_map pattern is what these 2 modules copy)
    - src/python/sumstats_utils.py (CANONICAL_COLS, filter_palindromic_ambiguous, liftover_to_grch37 signatures; append build_rsid_to_chrpos helper at end)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md Example 1 (harmonize_yengo.py skeleton — copy verbatim as starting point)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md §Common Pitfalls #1 #5 (Loh liftover, rsid crosswalk)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv rows 2-5 (BMI sources) + rows 25-39 (GLGC 15 rows)
    - data/raw/sumstats_v2/GLGC2021/ (ls the 24 already-landed files to confirm filename pattern for harmonize_glgc)
    - tests/phase9/test_harmonize_bbj.py if exists (pytest pattern reference)
    - config/pipeline.yaml (add `paths.harmonized_sumstats`, `paths.harmonized_parquet` keys if absent)
  </read_first>
  <behavior>
    - harmonize_yengo.py: 3 variant codepaths — yengo2018 (no liftover), loh2022_eur (b38->b37 liftover), loh2022_afr (b38->b37 liftover), page2019_afr (no liftover, b37 native). CLI flag --variant {yengo2018,loh2022_eur,loh2022_afr,page2019_afr}. --chain flag required for loh2022_*. Returns {trait, variant, n_rows, tsv, parquet} dict.
    - harmonize_glgc.py: single module handling 15 rows. CLI flag --subtype {LDL,HDL,TG,TC} --ancestry {TRANS,EUR,AFR,EAS,SAS,HIS}. For TG, detect `logTG` in filename and mark phenotype_lock="log(TG) inverse-normal transformed" in output metadata. Column map handles RVTESTS + GLGC meta variants.
    - sumstats_utils.build_rsid_to_chrpos(bim_prefix, chromosomes) reads {bim_prefix}.{chr}.bim per chromosome (6-column PLINK bim), returns dict rsid -> (chr:int, bp:int). Caches in module-level dict keyed by bim_prefix to avoid re-reading per-call.
    - Each harmonizer writes a `.qc.json` sidecar alongside its output (palindromic drop count, liftover drop count, input_rows, output_rows, MAF<0.005 count, INFO<0.8 count if INFO available). Wave 4 Quarto QC reads these sidecars.
    - Tests create fixture TSVs under tests/m1/fixtures/ with 100 synthetic rows matching each source's expected column names; invoke harmonizer; assert (a) 10 CANONICAL_COLS in output, (b) no nulls in CHR/BP/BETA/SE, (c) palindromic drop count > 0, (d) for Loh fixture, liftover drop rate < 5%.
  </behavior>
  <action>
    (A) Extend src/python/sumstats_utils.py by appending build_rsid_to_chrpos at the end of the file:

    ```python
    _rsid_lookup_cache: dict[str, dict[str, tuple[int,int]]] = {}

    def build_rsid_to_chrpos(bim_prefix: str,
                              chromosomes: list[int] | None = None) -> dict[str, tuple[int,int]]:
        """Forward rsid -> (chr, bp) lookup from PLINK .bim files.

        Args:
            bim_prefix: path prefix such that {prefix}.{chr}.bim exists for each
                        chromosome. Example: "data/external/1000G.EUR.QC" with
                        files "data/external/1000G.EUR.QC.1.bim".
            chromosomes: list of chromosome ints; defaults to 1..22.

        Returns:
            dict of rsid (str) -> (chromosome:int, bp:int). Cached by bim_prefix.

        Raises FileNotFoundError if any chromosome bim is missing.
        """
        if bim_prefix in _rsid_lookup_cache:
            return _rsid_lookup_cache[bim_prefix]
        if chromosomes is None:
            chromosomes = list(range(1, 23))
        lookup: dict[str, tuple[int,int]] = {}
        import pandas as pd
        from pathlib import Path
        for chrom in chromosomes:
            bim = Path(f"{bim_prefix}.{chrom}.bim")
            if not bim.exists():
                raise FileNotFoundError(f"build_rsid_to_chrpos: {bim} missing")
            df = pd.read_csv(bim, sep=r"\s+", header=None,
                             names=["chr","rsid","cm","bp","a1","a2"],
                             dtype={"chr": int, "bp": int})
            lookup.update({r.rsid: (int(r.chr), int(r.bp)) for r in df.itertuples()})
        _rsid_lookup_cache[bim_prefix] = lookup
        return lookup
    ```

    (B) Create src/python/harmonize_yengo.py. Start from the RESEARCH Example 1 skeleton, extend with `page2019_afr` variant codepath (different col_map: `rsid, chr, bp, effect_allele, other_allele, eaf, beta, se, pvalue, n` per PAGE-published format; b37 native). Add `.qc.json` sidecar emission at end.

    (C) Create src/python/harmonize_glgc.py (~130 lines). Column-rename table for GLGC RVTESTS format:
    ```python
    GLGC_COLS = {"CHROM": "CHR", "POS_b37": "BP", "rsID": "SNP",
                 "REF": "OA", "ALT": "EA",
                 "ALT_FREQ": "EAF", "BETA": "BETA", "SE": "SE",
                 "PVALUE": "P", "N": "N"}
    ```
    Header variants detected via `_normalize_header(df)` that handles common synonyms (CHR/CHROM, POS/POS_b37/BP, RSID/rsID/SNP, etc.). `--subtype TG` fixes `phenotype_lock` to "log(TG) inverse-normal transformed" but does NOT transform values again (file is pre-transformed per TSV row 34).

    (D) Create the 5 fixture TSVs under tests/m1/fixtures/. Each has 100 synthetic rows with realistic column names per source. loh_head.tsv uses b38 positions (e.g. start at chr1:1000000 increment by 10kb) — test asserts liftover shifts them down by the known b38→b37 delta (varies by chromosome but typically tens of Mb on some chroms).

    (E) Author tests/m1/test_harmonize_yengo.py with 4 test functions (one per variant), test_harmonize_glgc.py with 2 test functions (one for a non-log lipid, one for logTG). Each invokes the harmonizer's main() via subprocess and asserts on the output TSV + parquet + .qc.json.

    Run:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest \
      tests/m1/test_harmonize_yengo.py tests/m1/test_harmonize_glgc.py -x --tb=short
    ```
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_yengo.py tests/m1/test_harmonize_glgc.py -x --tb=short 2>&amp;1 | tail -5 &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import sys; sys.path.insert(0, 'src/python'); from sumstats_utils import build_rsid_to_chrpos, CANONICAL_COLS, filter_palindromic_ambiguous, liftover_to_grch37; print('OK')" &amp;&amp; grep -c "^def " src/python/harmonize_yengo.py | awk '$1 >= 2' &amp;&amp; grep -c "^def " src/python/harmonize_glgc.py | awk '$1 >= 2'</automated>
  </verify>
  <done>harmonize_yengo.py defines harmonize_yengo() and _main(); 4 variant codepaths implemented; harmonize_glgc.py defines harmonize_glgc() and _main(); sumstats_utils.build_rsid_to_chrpos importable; pytest tests/m1/test_harmonize_yengo.py tests/m1/test_harmonize_glgc.py passes.</done>
</task>

<task id="m1-02a-T2" type="auto" tdd="true">
  <name>Task 2: harmonize_wuttke.py (eGFR) + harmonize_magic.py (HbA1c) + wire Snakemake rules + bgzip/tabix outputs</name>
  <files>
    src/python/harmonize_wuttke.py,
    src/python/harmonize_magic.py,
    src/python/m1_raw_glob.py,
    src/snakemake/rules/m1_harmonize.smk,
    tests/m1/test_harmonize_wuttke.py,
    tests/m1/test_harmonize_magic.py,
    tests/m1/test_m1_raw_glob.py,
    tests/m1/fixtures/wuttke_head.tsv,
    tests/m1/fixtures/morris_afr_head.tsv,
    tests/m1/fixtures/magic_head.tsv,
    config/pipeline.yaml
  </files>
  <read_first>
    - src/python/harmonize_yengo.py (just authored — copy module structure verbatim)
    - src/python/harmonize_glgc.py (just authored — copy column-rename guard pattern)
    - src/python/sumstats_utils.py (build_rsid_to_chrpos signature from Task 1)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv rows 40-48 (eGFR 3 rows + HbA1c 6 rows)
    - data/external/ (ls for 1000G.EUR.QC.*.bim files; if absent, add fallback to Wave 0 staging)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md Example 3 (Snakemake rule skeleton for harmonize)
    - src/snakemake/rules/sumstats.smk (existing path-parameterized example — wildcard pattern)
    - config/pipeline.yaml (add paths.harmonized_sumstats, paths.harmonized_parquet, paths.raw_sumstats_v2 keys if absent)
  </read_first>
  <behavior>
    - harmonize_wuttke.py: 3 variant codepaths — wuttke2019_trans, wuttke2019_eur, morris2019_afr (Morris 2019 AFR companion paper; header differs from Wuttke — verify against downloaded file columns). All b37-native, no liftover. EAF column is Freq1 (Wuttke) or EAF (Morris).
    - harmonize_magic.py: 6 ancestry codepaths. CRITICAL — raw file has no CHR/BP; harmonizer MUST call sumstats_utils.build_rsid_to_chrpos(bim_prefix) to forward-map rsid→(chr,bp). Unmapped rsids dropped with count in .qc.json. Expected 2-5% drop per MAGIC→1KG mismatch (RESEARCH pitfall #5). bim_prefix defaults to config value resolved via pyyaml read of config/pipeline.yaml at import time.
    - src/snakemake/rules/m1_harmonize.smk: 4 wildcard-expanded rules total (one per harmonizer module). Each rule:
      - input: flag file from Wave 1 rule `.download_complete.<source_tag>` + actual raw file (globbed from target_dir)
      - output: `.tsv.bgz` + `.tbi` + `.parquet` + `.qc.json` using D-16 dotted naming
      - shell: runs python harmonize_<module>.py → writes .tsv.gz → `bgzip -f` → `tabix -s1 -b2 -e2 -S1` (CHR=col1, BP=col2, skip header)
      - conda: `../envs/m1-harmonize.yml`
      - resources: mem_mb=8000, runtime=2880 (standard queue per feedback_lsf_queues)
    - The 4 harmonizer rules all depend only on Wave 1 download flags, so they fire in parallel once their respective raw files land. This implements D-14 harmonize-as-ready parallelization.
    - Tests fire each harmonizer on synthetic fixtures; assert dual-emit artifacts + .qc.json fields (input_rows, output_rows, n_palindromic_dropped, n_unmapped_rsid for MAGIC, liftover_drop_rate for Loh path).
  </behavior>
  <action>
    (A0) Author src/python/m1_raw_glob.py — shared helper that resolves the single expected raw-file path for any (source_tag, ancestry) pair, used by all harmonize Snakemake rules in m1-02a-T2 (GBMI asthma) AND m1-02b-T1 (DIAMANTE/GIGASTROKE/Aragam) per B4 fix. Replaces the `<resolved_raw_glob>` placeholder. W8 fix (option A — universal .deferred guard): resolve_raw_for returns the module-level constant `DEFERRED_SENTINEL = "__DEFERRED__"` when a `.deferred` marker is present in the resolved target_dir, BEFORE the `assert len(matches) == 1`. Every harmonize rule's shell prelude branches on this sentinel and emits its own `.deferred` output marker without invoking the harmonizer body. This single choke point closes Loh-EUR, Loh-AFR (PENDING_D01_ACCESSION sentinels from m1-01 N1 fix), AND any future PENDING_* deferral path symmetrically. Source-specific ad-hoc `harmonize_deferred_*` rules (e.g. DIAMANTE AFR/HIS, CAD-AFR D-03 branch-b) are RETAINED because they encode trait/source-specific fallback logic independent of the sentinel path.

    ```python
    #!/usr/bin/env python3
    """Resolve the single expected raw-file path for a given source_tag + ancestry.

    Single source of truth consumed by every harmonize_* Snakemake rule's params: lambda
    so executors do not invent ad-hoc globs. Reads:
      - config/download_manifest_m1_portal.tsv (source_tag -> {target_dir, filename})
      - .planning/amendments/SUMSTATS-UPGRADE.tsv (fallback for already_downloaded rows
        not on the portal manifest, e.g. GLGC + CKDGen)
      - directory convention data/raw/sumstats_v2/<Consortium><Year>/<trait>/<ancestry>/
    Returns the single matching path string or raises if zero or multiple matches.
    """
    from __future__ import annotations
    from pathlib import Path
    import pandas as pd

    PORTAL_MANIFEST = Path("config/download_manifest_m1_portal.tsv")
    UPGRADE_TSV     = Path(".planning/amendments/SUMSTATS-UPGRADE.tsv")
    RAW_ROOT        = Path("data/raw/sumstats_v2")

    # W8 fix (option A): module-level sentinel returned when an upstream `.deferred`
    # marker is present in the resolved target_dir. Every harmonize rule's shell prelude
    # MUST guard on `[ "{params.raw}" = "__DEFERRED__" ]` and emit a `.deferred` output
    # marker without invoking the harmonizer body. This single choke point closes Loh-EUR,
    # Loh-AFR, AND any future PENDING_* sentinel symmetrically, replacing per-source
    # ad-hoc `harmonize_deferred_*` rules with a universal guard.
    DEFERRED_SENTINEL = "__DEFERRED__"

    def resolve_raw_for(source_tag: str, ancestry: str) -> str:
        """Return the single expected raw-file path for (source_tag, ancestry).

        Resolution order:
          0) `.deferred` marker present in target_dir -> DEFERRED_SENTINEL (W8 fix)
          1) Portal manifest exact source_tag match (e.g. 'GBMI2022_asthma_EUR')
          2) Portal manifest source_tag derivable from {Consortium}{Year}_{trait}_{ancestry}
          3) SUMSTATS-UPGRADE.tsv expected_filename + directory convention
        Returns DEFERRED_SENTINEL if any candidate target_dir holds a .deferred marker.
        Raises FileNotFoundError if zero matches; AssertionError if multiple.
        """
        # W8 fix (option A): early-return DEFERRED_SENTINEL when upstream wrote a
        # .deferred marker. Universal across PENDING_D01_ACCESSION (Loh) + future
        # PENDING_* + manual DEFERRED rows. Every harmonize rule's shell prelude
        # checks for this sentinel and emits its own .deferred output marker.
        candidate_dirs: list[Path] = []
        if PORTAL_MANIFEST.exists():
            _df_check = pd.read_csv(PORTAL_MANIFEST, sep="\t")
            _row_check = _df_check[_df_check["source_tag"] == source_tag]
            if len(_row_check) == 1:
                candidate_dirs.append(Path(_row_check["target_dir"].iloc[0]))
        for cand_dir in candidate_dirs:
            if (cand_dir / ".deferred").exists():
                return DEFERRED_SENTINEL

        matches: list[Path] = []
        if PORTAL_MANIFEST.exists():
            df = pd.read_csv(PORTAL_MANIFEST, sep="\t")
            row = df[df["source_tag"] == source_tag]
            if len(row) == 1:
                target = Path(row["target_dir"].iloc[0]) / row["filename"].iloc[0]
                if target.exists():
                    matches.append(target)
                else:
                    # Glob within target_dir for the canonical filename pattern
                    matches.extend(Path(row["target_dir"].iloc[0]).glob(row["filename"].iloc[0]))
        if not matches and UPGRADE_TSV.exists():
            tsv = pd.read_csv(UPGRADE_TSV, sep="\t")
            sub = tsv[tsv["ancestry"] == ancestry]
            for _, r in sub.iterrows():
                consortium = r["source_consortium"].split("-")[0]  # GIGASTROKE2022 etc
                trait = str(r["trait"]).lower()
                cand_dir = RAW_ROOT / f"{consortium}{r['citation_first_author_year'].split()[-1].rstrip(')')}" / trait / ancestry
                # W8 fix: also inspect this fallback dir for a .deferred marker
                if (cand_dir / ".deferred").exists():
                    return DEFERRED_SENTINEL
                if cand_dir.exists():
                    matches.extend(p for p in cand_dir.glob(r["expected_filename"]) if p.is_file())
        assert len(matches) == 1, (
            f"resolve_raw_for: expected exactly 1 raw file for "
            f"{source_tag}/{ancestry}, found {len(matches)}: {matches}"
        )
        return str(matches[0])

    if __name__ == "__main__":
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("--source-tag", required=True)
        ap.add_argument("--ancestry", required=True)
        args = ap.parse_args()
        print(resolve_raw_for(args.source_tag, args.ancestry))
    ```

    Author tests/m1/test_m1_raw_glob.py: fixture mini portal manifest + a fake raw tree under tmp_path; assert resolve_raw_for returns single path; assert AssertionError when zero or two files match; assert exact-one match drives the rule body. W8 fix — add a 4th test case: write a `.deferred` marker into the resolved target_dir alongside zero raw files; assert resolve_raw_for returns the DEFERRED_SENTINEL constant ("__DEFERRED__") instead of raising AssertionError. Import the sentinel via `from m1_raw_glob import DEFERRED_SENTINEL`. This locks in the option-A universal-guard contract.

    All Snakemake harmonize rules in m1_harmonize.smk that previously used `<resolved_raw_glob>` MUST now declare:
    ```python
    from m1_raw_glob import resolve_raw_for  # at top of m1_harmonize.smk

    rule harmonize_<source>:
        params:
            raw = lambda wc: resolve_raw_for(f"<SOURCE_TAG>_<trait>_{wc.ancestry}", wc.ancestry),
        shell:
            r"""
            # W8 fix (option A): universal .deferred guard. If resolve_raw_for returned
            # DEFERRED_SENTINEL, emit a .deferred output marker and skip the harmonizer body.
            # This closes Loh-EUR, Loh-AFR, AND any future PENDING_* sentinel symmetrically.
            if [ "{params.raw}" = "__DEFERRED__" ]; then
                mkdir -p $(dirname {output[0]})
                touch {output[0]}.deferred
                echo "DEFERRED: upstream marker present for <SOURCE_TAG>/{wildcards.ancestry}"
                exit 0
            fi
            python src/python/harmonize_<source>.py --input {params.raw} ...
            """
    ```
    Apply this universal-guard pattern to ALL harmonize rules: m1-02a (yengo, glgc, wuttke, magic) AND m1-02b (diamante, gigastroke, aragam, gbmi_asthma). Source-specific ad-hoc `harmonize_deferred_*` rules in m1-02b-T1 step (F) (DIAMANTE AFR/HIS trait-pending; CAD-AFR D-03 branch-b Klarin fallback) are RETAINED — they encode source-specific fallback logic independent of the universal-guard sentinel path.

    (A) Create src/python/harmonize_wuttke.py. Column map for Wuttke 2019 TRANS/EUR format:
    ```python
    WUTTKE_COLS = {"Chr": "CHR", "Pos_b37_hg19": "BP", "RSID": "SNP",
                   "Allele1": "EA", "Allele2": "OA",
                   "Freq1": "EAF", "Effect": "BETA", "StdErr": "SE",
                   "P-value": "P", "n_total_sum": "N"}
    ```
    For Morris 2019 AFR, use a separate MORRIS_AFR_COLS map (verify column names against the downloaded file; if download lands a header-different pattern, add a `_normalize_morris_header()` function that handles the top 3 most likely patterns and raises ValueError with the found columns listed if none match). Add `.qc.json` sidecar.

    (B) Create src/python/harmonize_magic.py. Column map:
    ```python
    MAGIC_COLS = {"A1": "EA", "A2": "OA", "eaf_meta": "EAF",
                  "BETA": "BETA", "SE": "SE", "P": "P", "N_INFO": "N"}
    # CHR + BP + SNP filled via build_rsid_to_chrpos lookup — not in raw file
    ```
    Flow: `df = pd.read_csv(raw)` → rename A1/A2/eaf_meta/BETA/SE/P/N_INFO + keep SNP_ID as SNP → `lookup = build_rsid_to_chrpos(bim_prefix)` → `df["_lookup"] = df["SNP"].map(lookup)` → drop unmapped with QC stat → `df["CHR"], df["BP"] = zip(*df["_lookup"])` → reorder CANONICAL_COLS → palindromic filter → emit dual.

    Add `--bim-prefix` CLI flag defaulting to `data/external/1000G.EUR.QC` (EUR ancestry crosswalk per RESEARCH open question #3 recommendation); override to `data/external/1000G.AFR.QC` for AFR MAGIC files.

    (C) Create src/snakemake/rules/m1_harmonize.smk. Key rule skeleton:

    ```python
    # src/snakemake/rules/m1_harmonize.smk
    import os

    RAW_DIR  = config["paths"]["raw_sumstats_v2"]
    HARM_DIR = config["paths"]["harmonized_sumstats"]
    PARQ_DIR = config["paths"]["harmonized_parquet"]
    CHAIN_B38_TO_B37 = "data/external/liftover/hg38ToHg19.over.chain.gz"

    rule harmonize_yengo:
        input:
            flag = os.path.join(RAW_DIR, ".download_complete.GIANT2018_BMI_EUR"),
        output:
            tsv_bgz = os.path.join(HARM_DIR, "bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz"),
            tbi     = os.path.join(HARM_DIR, "bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz.tbi"),
            parquet = os.path.join(PARQ_DIR, "bmi.EUR.GIANT-UKBB.2018.GRCh37.parquet"),
            qc_json = os.path.join(HARM_DIR, "qc_log/bmi.EUR.GIANT-UKBB.2018.qc.json"),
        params:
            # W8 fix: resolve_raw_for returns DEFERRED_SENTINEL ('__DEFERRED__') if a
            # `.deferred` marker is present in target_dir; shell prelude branches on it.
            raw = lambda wc: resolve_raw_for("GIANT2018_BMI_EUR", "EUR"),
        conda: "../../envs/m1-harmonize.yml"
        resources: mem_mb=8000, runtime=2880
        shell:
            r"""
            # W8 fix (option A): universal .deferred guard at shell prelude.
            if [ "{params.raw}" = "__DEFERRED__" ]; then
                mkdir -p $(dirname {output.tsv_bgz})
                touch {output.tsv_bgz}.deferred
                echo "DEFERRED: upstream marker present for GIANT2018_BMI_EUR"
                exit 0
            fi
            python src/python/harmonize_yengo.py \
                --input {params.raw} \
                --output {output.tsv_bgz}.tmp.tsv.gz \
                --parquet {output.parquet} \
                --qc-json {output.qc_json} \
                --variant yengo2018 \
                --trait bmi --ancestry EUR --consortium GIANT-UKBB --year 2018
            zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
            tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
            rm -f {output.tsv_bgz}.tmp.tsv.gz
            """

    # ... 3 additional near-identical rules for loh_eur, loh_afr, page_afr ...
    # ... 15 rules for harmonize_glgc (parameterized by wildcards {subtype}.{ancestry}) ...
    # ... 3 rules for harmonize_wuttke (wuttke_trans, wuttke_eur, morris_afr) ...
    # ... 6 rules for harmonize_magic (by ancestry) ...
    # W8 fix: ALL of the above rules MUST follow the harmonize_yengo skeleton:
    #   (a) declare `params: raw = lambda wc: resolve_raw_for("<SOURCE_TAG>_<trait>_<ancestry>", "<ancestry>")`
    #   (b) prepend the universal .deferred guard to the shell body:
    #       `if [ "{params.raw}" = "__DEFERRED__" ]; then mkdir -p $(dirname {output[0]}); touch {output[0]}.deferred && echo 'DEFERRED: upstream marker present' && exit 0; fi`
    # This closes Loh-EUR, Loh-AFR (PENDING_D01_ACCESSION sentinels), and ANY future
    # PENDING_* deferral path with a single choke-point change. No source-specific
    # `harmonize_deferred_loh_{ancestry}` ad-hoc rules are needed (option A supersedes
    # option B). Existing source-specific ad-hoc deferred rules in m1-02b (DIAMANTE
    # AFR/HIS trait-pending, CAD-AFR D-03 branch-b Klarin fallback) are independent
    # and RETAINED — they encode trait/source-specific logic, not sentinel handling.
    ```

    Consolidate repetition via a single wildcard rule driven by a side-car manifest or YAML that lists {source_tag, variant, raw_path, output_prefix}; final rule count may be ~6 grouping rules rather than 27 individual rules. Use the harmonize-as-ready policy (D-14) by making the per-tag flag file be the only input dependency beyond the raw file itself.

    (D) Extend config/pipeline.yaml with the three new path keys:
    ```yaml
    paths:
      raw_sumstats_v2: data/raw/sumstats_v2
      harmonized_sumstats: data/processed/sumstats_harmonized
      harmonized_parquet: data/processed/sumstats_harmonized_parquet
      ldsc_munged: data/processed/ldsc_overlap/munged
      ldsc_rg_logs: data/processed/ldsc_overlap/rg_logs
      ldsc_overlap: data/processed/ldsc_overlap
      qc_log: data/processed/sumstats_harmonized/qc_log
    ```

    (E) Author tests/m1/test_harmonize_wuttke.py + test_harmonize_magic.py. MAGIC test creates a mini bim fixture at tests/m1/fixtures/mini_1kg.{1,2}.bim with ~50 rsids, invokes harmonizer via --bim-prefix tests/m1/fixtures/mini_1kg, asserts the unmapped count is as expected from the fixture mismatch.

    Run: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_wuttke.py tests/m1/test_harmonize_magic.py -x` and also `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake -s workflow/Snakefile --dry-run --cores 1 harmonize_yengo harmonize_glgc harmonize_wuttke harmonize_magic` (names per rules authored).
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_wuttke.py tests/m1/test_harmonize_magic.py tests/m1/test_m1_raw_glob.py -x --tb=short 2>&amp;1 | tail -5 &amp;&amp; test -f src/snakemake/rules/m1_harmonize.smk &amp;&amp; grep -cE "^rule harmonize_(yengo|glgc|wuttke|magic)" src/snakemake/rules/m1_harmonize.smk | awk '$1 &gt;= 4' &amp;&amp; grep -q "harmonized_sumstats:" config/pipeline.yaml &amp;&amp; grep -q "harmonized_parquet:" config/pipeline.yaml &amp;&amp; grep -q "DEFERRED_SENTINEL" src/python/m1_raw_glob.py &amp;&amp; grep -q "__DEFERRED__" src/snakemake/rules/m1_harmonize.smk &amp;&amp; ! grep -rE "/rs1/researchers|/gpfs_common|/share/clintonlab" src/python/harmonize_yengo.py src/python/harmonize_glgc.py src/python/harmonize_wuttke.py src/python/harmonize_magic.py src/snakemake/rules/m1_harmonize.smk</automated>
  </verify>
  <done>harmonize_wuttke.py + harmonize_magic.py importable and passing their pytests; m1_harmonize.smk declares rules for all 4 continuous-trait harmonizers (consolidated or per-source); config/pipeline.yaml has the 7 paths keys; zero hardcoded absolute paths in any of the 4 .py files or the smk file.</done>
</task>

</tasks>

<threat_model>
security_enforcement disabled — pure data-transformation plan. No user input; no network calls (raw files already on disk); no secrets. Palindromic filter + liftover hard-fail are data-correctness controls, not security controls.
</threat_model>

<verification>
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest \
  tests/m1/test_harmonize_yengo.py tests/m1/test_harmonize_glgc.py \
  tests/m1/test_harmonize_wuttke.py tests/m1/test_harmonize_magic.py -x --tb=short \
  && test -f src/python/harmonize_yengo.py \
  && test -f src/python/harmonize_glgc.py \
  && test -f src/python/harmonize_wuttke.py \
  && test -f src/python/harmonize_magic.py \
  && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import sys; sys.path.insert(0, 'src/python'); from sumstats_utils import build_rsid_to_chrpos" \
  && test -f src/snakemake/rules/m1_harmonize.smk \
  && ! grep -r "admixmap\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/harmonize_yengo.py src/python/harmonize_glgc.py src/python/harmonize_wuttke.py src/python/harmonize_magic.py src/snakemake/rules/m1_harmonize.smk config/pipeline.yaml
</verification>

<success_criteria>
- 4 harmonizer modules exist under src/python/ with _main() + typed harmonize_<source>() entry points
- sumstats_utils.build_rsid_to_chrpos is importable and caches per bim_prefix
- 4 pytest modules under tests/m1/ each exit 0 on synthetic fixtures
- src/snakemake/rules/m1_harmonize.smk declares rules that dry-run-load without error
- config/pipeline.yaml has all 7 new paths keys
- REQ-PATH-PARAMETERIZATION: `grep -r "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/harmonize_{yengo,glgc,wuttke,magic}.py src/snakemake/rules/m1_harmonize.smk` returns 0
- Each harmonizer emits dual-emit artifacts + `.qc.json` sidecar per D-09 + D-12 QC hook
- Loh 2022 liftover drop-rate < 5% (hard fail otherwise) per DEC-2026-04-24-01 + RESEARCH pitfall #1
- MAGIC rsid forward crosswalk reports < 5% unmapped rsids (expected per RESEARCH open question #3)
</success_criteria>

<output>
After completion, create `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-02a-SUMMARY.md` with:
- 4 harmonizer module line counts + function signatures
- Per-fixture test outcomes (pytest pass counts)
- Snakemake dry-run DAG sketch for the 4 rule families
- config/pipeline.yaml delta (new paths keys)
- sumstats_utils.build_rsid_to_chrpos cache hit-rate on the MAGIC test fixture
- Summary of any pre-existing pre-pivot harmonized files coexisting under old naming (for Track A back-compat)
</output>
</content>
</invoke>