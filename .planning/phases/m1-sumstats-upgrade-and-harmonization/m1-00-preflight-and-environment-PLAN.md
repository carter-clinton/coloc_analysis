---
plan_id: m1-00-preflight-and-environment
phase: m1
plan: 00
type: execute
wave: 0
depends_on: []
autonomous: false
requirements: [REQ-SNAKEMAKE-CI, REQ-PUBLIC-DATA-ONLY, REQ-PATH-PARAMETERIZATION]
objective: "Pre-flight probes (MAGIC FTP egress, GWAS-Catalog Giri 2019, LDSC 2-trait benchmark) + conda envs + pytest scaffolding + chain-file staging + LDSC reference LD + human-gated D-02/D-03/D-06 resolutions"
files_modified:
  - envs/m1-harmonize.yml
  - envs/m1-munge.yml
  - envs/m1-ldsc-rg.yml
  - envs/m1-qc.yml
  - envs/m1-download.yml
  - tests/m1/conftest.py
  - tests/m1/test_harmonizer_contract.py
  - tests/m1/test_liftover.py
  - tests/m1/test_palindromic_filter.py
  - tests/m1/test_ldsc_star_reducer.py
  - tests/m1/test_inventory_yaml.py
  - tests/m1/wave0_probes.sh
  - tests/m1/fixtures/ldsc_rg_log_sample.log
  - tests/m1/fixtures/synth_10col_b37.tsv
  - tests/m1/fixtures/synth_10col_b38.tsv
  - data/external/liftover/hg38ToHg19.over.chain.gz
  - data/external/ldscore/eur_w_ld_chr/
  - data/external/ldscore/w_hm3.snplist
  - data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt
  - .planning/amendments/SUMSTATS-UPGRADE.tsv
  - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md
  - .planning/DECISIONS.md
  - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
must_haves:
  truths:
    - "Conda envs m1-harmonize, m1-munge, m1-ldsc-rg, m1-qc, m1-download solve dry-run via mamba"
    - "pytest collects tests/m1/ with zero import errors"
    - "hg38ToHg19 chain file is on disk and passes a round-trip coordinate test"
    - "LDSC 2-trait --rg smoke call succeeds and the reducer parses its log"
    - "MAGIC FTP egress probe outcome is recorded (pass OR documented fallback)"
    - "GIGASTROKE GCST accessions are integer-locked in SUMSTATS-UPGRADE.tsv (placeholders removed)"
    - "Aragam ZIP contents enumerated and committed; AFR branch decision recorded (D-03)"
    - "MVP Giri D-06 primary attempt recorded with outcome; fallback branch documented"
    - "DEC-2026-04-24 entry records GRCh37 canonical decision + AoU scope expansion"
  artifacts:
    - path: "envs/m1-harmonize.yml"
      provides: "pandas 2.2.3 + pyarrow 18.1.0 + pyliftover + CrossMap + htslib"
      min_lines: 8
    - path: "envs/m1-ldsc-rg.yml"
      provides: "abdenlab ldsc-python3 fork via git+ pip install"
    - path: "envs/m1-qc.yml"
      provides: "quarto + R tidyverse + ggplot2 + qqman + locuszoomr"
    - path: "tests/m1/conftest.py"
      provides: "synthetic 10-col TSV fixture factory + chain-file fixture + LDSC log fixture"
    - path: "tests/m1/test_ldsc_star_reducer.py"
      provides: "gcov_int parser regression on fixture log"
    - path: "data/external/liftover/hg38ToHg19.over.chain.gz"
      provides: "UCSC chain for Loh 2022 + GBMI asthma b38->b37"
    - path: "data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt"
      provides: "unzip -l enumeration; AFR branch resolution"
    - path: ".planning/amendments/SUMSTATS-UPGRADE.tsv"
      provides: "GIGASTROKE GCST placeholders replaced with integer accessions per D-02"
    - path: ".planning/DECISIONS.md"
      provides: "DEC-2026-04-24 entry for GRCh37 canonical + AoU compute scope expansion"
  key_links:
    - from: "tests/m1/conftest.py"
      to: "src/python/sumstats_utils.py"
      via: "import canonical schema, is_palindromic, filter_palindromic_ambiguous"
      pattern: "import sumstats_utils"
    - from: "tests/m1/test_ldsc_star_reducer.py"
      to: "tests/m1/fixtures/ldsc_rg_log_sample.log"
      via: "fixture load"
      pattern: "parse_rg_log|gcov_int"
    - from: "envs/m1-ldsc-rg.yml"
      to: "github.com/abdenlab/ldsc-python3"
      via: "pip git+"
      pattern: "ldsc-python3"
---

<objective>
Wave 0 foundations for M1. Install all conda envs used by downstream waves. Build the pytest scaffolding (shared fixtures + per-task contract/liftover/palindromic/reducer/inventory tests). Stage missing reference data (UCSC hg38ToHg19 chain + LDSC `eur_w_ld_chr` + `w_hm3.snplist`). Run three pre-flight probes whose outcomes gate Wave 1 & Wave 3 — (a) MAGIC FTP port-21 egress from NCSU HPC compute node (RESEARCH pitfall #2; SUMSTATS-UPGRADE Q5), (b) GWAS-Catalog summary-only availability check for Giri 2019 MVP AFR-BP (CONTEXT D-06 primary attempt; RESEARCH open question #3), (c) LDSC `--rg` 2-trait smoke benchmark on pre-existing munged files to calibrate per-pair wall time before the 44 star-pattern jobs fire (RESEARCH open question #4; wave-3 budget check). Finally, drive three human-gated resolutions: commit Carter's GIGASTROKE GCST integer lock into `SUMSTATS-UPGRADE.tsv` replacing `GCST90104540-series` placeholders (D-02); unzip Aragam 2022 CARDIoGRAM ZIP and commit a manifest (D-03); file DEC-2026-04-24 DECISIONS.md entry capturing the GRCh37 canonical decision (D-08) AND the M1-scoped AoU compute scope expansion (D-07).

Purpose: Every downstream wave depends on these foundations. The 7 new harmonizers (Wave 2a/2b) need `envs/m1-harmonize.yml` + chain file + pytest contract. The 44 LDSC star calls (Wave 3) need `envs/m1-ldsc-rg.yml` + `eur_w_ld_chr/` + `w_hm3.snplist` + the 2-trait benchmark. Per-trait Quarto (Wave 4) needs `envs/m1-qc.yml`. The portal downloads (Wave 1) need the MAGIC egress verdict and the D-02 integer accessions.
Output: 5 conda env YAMLs, pytest fixtures + 5 contract tests, the chain file + LDSC reference LD staged under `data/external/`, the Aragam manifest + GCST-locked TSV, a DEC-2026-04-24 decisions entry, and Wave 0 probe outcomes recorded in `SUMSTATS-MANUAL-FETCH-STATUS.md`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/DECISIONS.md
@.planning/amendments/SUMSTATS-UPGRADE.md
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@.planning/amendments/SUMSTATS-MANUAL-FETCH.md
@.planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md
@.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md
@.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
@.planning/amendments/AOU-LD-PIPELINE.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-CONTEXT.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-VALIDATION.md
@.planning/phases/09-replication-in-independent-cohorts/09-02-PLAN.md
@src/python/sumstats_utils.py
@src/python/harmonize_gbmi.py
@tools/ldsc/ldsc.py
@envs/python_stats.yml
@envs/ldsc_py3.yml
@CLAUDE.md

<interfaces>
<!-- Keys any downstream wave relies on. Extract verbatim so no codebase spelunking is needed. -->

From src/python/sumstats_utils.py:
```python
CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]

def is_palindromic(ea: str, oa: str) -> bool:
    """A/T or G/C allele pair."""

def filter_palindromic_ambiguous(df: pd.DataFrame,
                                 maf_band: tuple[float,float] = (0.48, 0.52)) -> pd.DataFrame:
    """Drop A/T, G/C palindromic SNPs whose EAF falls in the ambiguous strand band."""

def liftover_to_grch37(df: pd.DataFrame,
                       chain_file: str,
                       chr_col: str = "CHR",
                       bp_col: str = "BP",
                       max_drop_rate: float = 0.05) -> tuple[pd.DataFrame, dict]:
    """Lift b38 -> b37. Hard-fails if drop_rate > max_drop_rate. Returns (df_b37, qc)."""

def validate_canonical_frame(df: pd.DataFrame) -> None:
    """Raises if df lacks any of CANONICAL_COLS or types are off."""
```

From tools/ldsc/ldsc.py lines 608-613 (VERIFIED — no --rg-cross exists):
```python
parser.add_argument("--rg", default=None, type=str,
    help="Comma-separated list of prefixes of .chisq filed for genetic correlation estimation.")
```
Behavior: first entry is focal; pairs with each subsequent entry (N-1 pairs per call, star topology).

From SUMSTATS-UPGRADE.tsv column 11 (rows 14-17):
GIGASTROKE download_url = `https://www.ebi.ac.uk/gwas/publications/36180795`
GIGASTROKE expected_filename contains `GCST90104540-series` placeholders that MUST be integer-locked.

From SUMSTATS-UPGRADE.tsv row 13 (MVP Giri hypertension AFR):
- download_url = dbGaP `phs001672` — D-06 explicitly REJECTS dbGaP DUA path
- D-06 primary = GWAS-Catalog probe at `ebi.ac.uk/gwas/publications/30578418`
- D-06 fallback = AoU Researcher Workbench AFR-SBP derivation (reuses AOU-LD-PIPELINE.md §2 P1-P7)

From project memory feedback_lsf_queues.md:
- LSF queues: standard (2880 min), serial (5760 min), long (14400 min)
- bsub_wrapper.sh sets -W to queue max; LSF_UNIT_FOR_LIMITS=GB
- NEVER run snakemake from miniconda3 base (Python 3.13); use /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
</interfaces>
</context>

<tasks>

<task id="m1-00-T1" type="auto" tdd="true">
  <name>Task 1: Stage conda envs, pytest scaffolding, and shared fixtures</name>
  <files>
    envs/m1-download.yml,
    envs/m1-harmonize.yml,
    envs/m1-munge.yml,
    envs/m1-ldsc-rg.yml,
    envs/m1-qc.yml,
    tests/m1/__init__.py,
    tests/m1/conftest.py,
    tests/m1/fixtures/__init__.py,
    tests/m1/fixtures/synth_10col_b37.tsv,
    tests/m1/fixtures/synth_10col_b38.tsv,
    tests/m1/fixtures/ldsc_rg_log_sample.log,
    tests/m1/test_harmonizer_contract.py,
    tests/m1/test_liftover.py,
    tests/m1/test_palindromic_filter.py,
    tests/m1/test_ldsc_star_reducer.py,
    tests/m1/test_inventory_yaml.py
  </files>
  <read_first>
    - envs/python_stats.yml (pinned versions for reuse)
    - envs/ldsc_py3.yml (abdenlab fork pip git+ install — copy the `ldsc-python3 @ git+https://github.com/abdenlab/ldsc-python3.git` line verbatim into envs/m1-ldsc-rg.yml + envs/m1-munge.yml)
    - src/python/sumstats_utils.py (copy CANONICAL_COLS + function signatures into fixtures)
    - src/python/harmonize_gbmi.py lines 100-130 (B-2 guard pattern; test_harmonizer_contract.py asserts this)
    - tests/phase9/conftest.py (existing pytest fixture pattern — mirror its layout)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md §Validation Architecture (Wave 0 Requirements list verbatim)
  </read_first>
  <behavior>
    - envs/m1-harmonize.yml declares: name: m1-harmonize; channels [conda-forge, bioconda]; deps: python=3.11, pandas=2.2.3, pyarrow=18.1.0, htslib=1.21, pyliftover, CrossMap, requests, pyyaml, pytest
    - envs/m1-munge.yml: inherits ldsc_py3 via git+pip install ldsc-python3; plus pandas, pyyaml, pytest
    - envs/m1-ldsc-rg.yml: same as m1-munge plus numpy<2 for LDSC Py3 fork compat
    - envs/m1-qc.yml: quarto>=1.5; r-base=4.4; r-tidyverse; r-ggplot2; r-qqman; r-locuszoomr; python=3.11, pandas, jupyter (for engine=jupyter fallback)
    - envs/m1-download.yml: curl, xargs, pyyaml, requests; lightweight
    - conftest.py provides synth_b37_frame(n=1000) and synth_b38_frame(n=1000) fixtures; emits TSVs into tmp_path; includes palindromic AT/GC rows + non-palindromic
    - test_harmonizer_contract.py imports sumstats_utils.validate_canonical_frame and asserts 10 CANONICAL_COLS present; tests B-2 guard (raises ValueError when renaming missing cols)
    - test_liftover.py round-trips a b37 fixture: hg19->hg38 then hg38->hg19 via pyliftover should recover >=95% of positions (uses BOTH chain files in tests/m1/fixtures/ if staged, else skip with reason)
    - test_palindromic_filter.py inputs 10 synthetic rows (4 A/T palindromic in MAF [0.48,0.52]; 4 non-palindromic; 2 G/C outside band) and asserts filter_palindromic_ambiguous drops exactly 4
    - test_ldsc_star_reducer.py parses tests/m1/fixtures/ldsc_rg_log_sample.log (a 3-pair LDSC rg log fixture written in this task) and asserts gcov_int extraction returns 3 float rows with p1/p2/gcov_int columns
    - test_inventory_yaml.py declares pydantic/jsonschema validator for the trait_inventory.yaml schema per Example 4 in m1-RESEARCH.md; tests pass on a 2-trait fixture YAML
  </behavior>
  <action>
    Create all 5 env YAMLs under envs/ with the dependencies above. For envs/m1-ldsc-rg.yml and envs/m1-munge.yml, copy the pip section from envs/ldsc_py3.yml verbatim (adds `ldsc-python3 @ git+https://github.com/abdenlab/ldsc-python3.git`). Verify each solves with:

    ```bash
    for f in envs/m1-*.yml; do
      mamba env create -n smoke-$(basename $f .yml)-dry -f $f --dry-run 2>&1 | tail -3 || echo "SOLVE FAIL: $f"
    done
    ```

    Create tests/m1/ directory tree including tests/m1/__init__.py, tests/m1/fixtures/__init__.py, and tests/m1/fixtures/. Write synth_10col_b37.tsv with 100 rows (5 palindromic + 95 non-palindromic; EAF distribution across [0.005, 0.5]). Write synth_10col_b38.tsv matching the first 20 rows of synth_10col_b37.tsv with positions shifted by +1Mb (simulates hg38 coordinates).

    Write tests/m1/fixtures/ldsc_rg_log_sample.log containing a 3-pair "Summary of Genetic Correlation Results" table with columns `p1 p2 rg se z p h2_obs h2_obs_se h2_int h2_int_se gcov_int gcov_int_se` with realistic values (e.g., gcov_int in {0.12, 0.04, 0.98}). Use the exact format the LDSC fork emits (lines 608-613 of tools/ldsc/ldsc.py).

    Write the 5 pytest modules. test_harmonizer_contract.py calls `sumstats_utils.validate_canonical_frame(df)` on the b37 fixture and asserts no exception; asserts missing column raises ValueError. test_palindromic_filter.py counts dropped rows against the band [0.48, 0.52]. test_ldsc_star_reducer.py imports a stub `reduce_ldsc_rg_matrix.parse_rg_log` that the Wave 3 plan will implement — for now it's allowed to skip with pytest.skip("Wave 3 module not yet created") BUT the test exists and pytest collects it.

    Verify collection:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/ --collect-only 2>&1 | tail -20
    ```
    Must return "5 tests collected" (or more) with zero import errors. Per DEC-2026-04-24 and feedback_no_conda.md, DO NOT emit `conda activate` in docs — tests always run via full path or via `snakemake --use-conda`.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/ --collect-only 2>&1 | grep -E "collected|error" &amp;&amp; for f in envs/m1-*.yml; do test -f "$f" || exit 1; done &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_palindromic_filter.py tests/m1/test_harmonizer_contract.py -x 2>&amp;1 | tail -3</automated>
  </verify>
  <done>All 5 envs/m1-*.yml exist and are syntactically valid; pytest collects tests/m1/ with zero import errors; test_palindromic_filter.py + test_harmonizer_contract.py pass; test_ldsc_star_reducer.py and test_liftover.py exist and either pass or skip with explicit reason.</done>
</task>

<task id="m1-00-T2" type="auto">
  <name>Task 2: Stage UCSC chain + LDSC reference LD + run 3 pre-flight probes</name>
  <files>
    data/external/liftover/hg38ToHg19.over.chain.gz,
    data/external/ldscore/eur_w_ld_chr/,
    data/external/ldscore/w_hm3.snplist,
    tests/m1/wave0_probes.sh,
    tests/m1/wave0_probes.log,
    .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md
  </files>
  <read_first>
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md §Common Pitfalls (Pitfall 2 MAGIC FTP egress) + §Environment Availability (hg38ToHg19 URL, LDSC LD URLs) + §Open Questions #1 #3 #4
    - /home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/feedback_url_rot_workarounds.md (Zenodo/NCBI/Bitbucket alternates if Broad URLs broken)
    - /home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/feedback_parallel_downloads.md (xargs -P 5 pattern)
    - bin/download_sumstats_v2.sh (idempotent fetch_one helper pattern)
    - data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz (Evangelou pre-pivot — re-verify build before reuse per D-10; load 10 rows)
    - results/pathway/ldsc_partitioned/munged/ (pre-pivot munged files; pick any two for LDSC smoke benchmark)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (append new rows; do not rewrite)
  </read_first>
  <action>
    (A) Stage hg38ToHg19 chain file:
    ```bash
    mkdir -p data/external/liftover
    curl --connect-timeout 30 --max-time 1800 -fsSL \
      "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz" \
      -o data/external/liftover/hg38ToHg19.over.chain.gz
    # Verify: file is non-empty and gzip-parseable
    gzip -t data/external/liftover/hg38ToHg19.over.chain.gz
    sha256sum data/external/liftover/hg38ToHg19.over.chain.gz
    ```
    Fallback if UCSC URL rots: `https://ftp.ensembl.org/pub/assembly_mapping/homo_sapiens/GRCh38_to_GRCh37.chain.gz` (Ensembl mirror per feedback_url_rot_workarounds).

    (B) Stage LDSC reference LD + HM3 SNP list:
    ```bash
    mkdir -p data/external/ldscore
    # eur_w_ld_chr/ (EUR-EUR pairs)
    curl --connect-timeout 30 --max-time 3600 -fsSL \
      "https://data.broadinstitute.org/alkesgroup/LDSCORE/eur_w_ld_chr.tar.bz2" \
      -o data/external/ldscore/eur_w_ld_chr.tar.bz2
    tar -xjf data/external/ldscore/eur_w_ld_chr.tar.bz2 -C data/external/ldscore/
    # w_hm3.snplist (HM3 SNP restriction for munge)
    curl --connect-timeout 30 --max-time 600 -fsSL \
      "https://data.broadinstitute.org/alkesgroup/LDSCORE/w_hm3.snplist.bz2" \
      -o data/external/ldscore/w_hm3.snplist.bz2
    bzip2 -d data/external/ldscore/w_hm3.snplist.bz2
    ```
    If Broad URLs return 403/404, fall back to Zenodo mirror per feedback_url_rot_workarounds.md; record fallback source in wave0_probes.log.

    (C) Author tests/m1/wave0_probes.sh and run it. Probe 1 (MAGIC FTP egress):
    ```bash
    # Must run on a compute node, not login node. Use bsub -I on standard queue:
    bsub -I -q standard -W 10 -n 1 \
      curl --connect-timeout 30 --head "ftp://web-ftp.ex.ac.uk/docs/downloads/" 2>&1 | tee /tmp/magic_ftp_probe.log
    # Record: pass (0-exit + 200-like header) OR fail (timeout / rc!=0)
    ```
    If fail, the Wave 1 plan (m1-01) MUST fall back to EBI mirror OR login-node proxy per SUMSTATS-UPGRADE §5 Tier 1. Record outcome in SUMSTATS-MANUAL-FETCH-STATUS.md under a new "Wave 0 pre-flight" section.

    Probe 2 (GWAS-Catalog Giri 2019 summary availability — D-06 primary):
    ```bash
    curl -sS "https://www.ebi.ac.uk/gwas/publications/30578418" > /tmp/giri_page.html
    grep -i -A 3 "summary statistics\|sumstats\|GCST" /tmp/giri_page.html | head -30
    ```
    Record outcome: (a) sumstats visible with GCST accession → Wave 1 downloads directly; (b) no summary download → Wave 1 triggers D-06 FALLBACK (AoU Workbench AFR-SBP derivation; out-of-band Carter action reusing AOU-LD-PIPELINE.md §2 P1–P7). Add primary-attempt result line to SUMSTATS-MANUAL-FETCH-STATUS.md.

    Probe 3 (LDSC 2-trait rg smoke benchmark):
    ```bash
    # Pick two pre-pivot munged files that already exist.
    ls results/pathway/ldsc_partitioned/munged/ 2>/dev/null | head -5
    # Example invocation (substitute real file names):
    time /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python tools/ldsc/ldsc.py \
      --rg results/pathway/ldsc_partitioned/munged/bmi_EUR.sumstats.gz,results/pathway/ldsc_partitioned/munged/t2d_EUR.sumstats.gz \
      --ref-ld-chr data/external/ldscore/eur_w_ld_chr/ \
      --w-ld-chr   data/external/ldscore/eur_w_ld_chr/ \
      --out /tmp/ldsc_smoke
    # Record wall time in seconds in wave0_probes.log.
    # W6 contract: emit one line of the form `PAIR_WALL_SECONDS <integer>` so m1-03-T2's
    # awk-based dynamic --jobs computation can read it. Example shell:
    #   PAIR_WALL=$(grep -oE 'real\s+[0-9]+m[0-9.]+s' /tmp/ldsc_smoke_time.txt | tail -1)
    #   echo "PAIR_WALL_SECONDS $PAIR_WALL" >> tests/m1/wave0_probes.log
    ```
    Record per-pair wall time. If > 30 min/pair, Wave 3 plan (m1-03) MUST de-parallelize the 44 star-calls into chunks to stay under 240 h long-queue ceiling (RESEARCH assumption A5). If < 15 min/pair, proceed as designed.

    Append all three probe outcomes to .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md under "## Wave 0 pre-flight probes (2026-04-24)" section. Commit with message `chore(m1): stage Wave 0 reference data + probe outcomes`.
  </action>
  <verify>
    <automated>test -f data/external/liftover/hg38ToHg19.over.chain.gz &amp;&amp; gzip -t data/external/liftover/hg38ToHg19.over.chain.gz &amp;&amp; test -d data/external/ldscore/eur_w_ld_chr &amp;&amp; test -f data/external/ldscore/w_hm3.snplist &amp;&amp; test -f tests/m1/wave0_probes.sh &amp;&amp; test -f tests/m1/wave0_probes.log &amp;&amp; grep -q "Wave 0 pre-flight" .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md</automated>
  </verify>
  <done>Chain file (>500KB, gzip-valid) on disk; eur_w_ld_chr/ directory unpacked with chr1..chr22 .M / .l2.ldscore / .l2.M_5_50 files; w_hm3.snplist ~1.2M lines; wave0_probes.sh runs cleanly; all three probes recorded in .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md with explicit pass/fail and a fallback plan for any failure.</done>
</task>

<task id="m1-00-T3" type="checkpoint:human-action" gate="blocking">
  <name>Task 3: Human-gated D-02 (GIGASTROKE GCST lock) + D-03 (Aragam ZIP enumerate) + D-06 disposition + DEC-2026-04-24 decisions entry</name>
  <files>
    .planning/amendments/SUMSTATS-UPGRADE.tsv,
    data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt,
    .planning/DECISIONS.md,
    .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
  </files>
  <read_first>
    - .planning/amendments/SUMSTATS-UPGRADE.tsv rows 14, 15, 16, 17 (stroke TRANS/EUR/AFR/EAS rows; placeholders `GCST90104540-series_*`)
    - .planning/amendments/SUMSTATS-UPGRADE.md §Q2 (GIGASTROKE accession resolution)
    - .planning/amendments/SUMSTATS-UPGRADE.md §Q3 (Aragam AFR branch)
    - data/raw/sumstats_v2/Aragam2022/ (check whether Aragam_2022_CARDIoGRAM_CAD_GWAS.zip is present)
    - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md (scan for any "GRCh38" wording that needs pre-paste correction per D-08)
    - .planning/DECISIONS.md last decision block (copy date/format convention for DEC-2026-04-24)
  </read_first>
  <what-built>Wave 0 foundations — envs staged, tests scaffolded, chain + LDSC LD staged, three probes recorded.</what-built>
  <how-to-verify>
    Carter performs the three human-gated actions in sequence. All three are ~30 min total elapsed + ~15 min Carter active time.

    **(1) GIGASTROKE GCST lock (D-02; ~15 min Carter active):**
    Browser: `https://www.ebi.ac.uk/gwas/publications/36180795`. For each of the 5 stroke rows (trans, EUR, AFR, EAS, SAS), record the integer GCST accession for "all-stroke". Open each accession's "Summary Statistics" tab — note the FTP URL pattern `https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST{range}/GCST{acc}/` so Wave 1 (m1-01) can construct download URLs.

    Edit `.planning/amendments/SUMSTATS-UPGRADE.tsv`:
    - Row 14 (stroke TRANS): replace `GCST90104539_buildGRCh37.tsv.gz` with the integer-locked file name.
    - Row 15 (stroke EUR): replace `GCST90104540-series_EUR_AS.tsv.gz` with `GCST{int}_...tsv.gz`.
    - Row 16 (stroke AFR): replace `GCST90104541-series_AA_AS.tsv.gz`.
    - Row 17 (stroke EAS): replace `GCST90104542-series_EAS_AS.tsv.gz`.
    Add a row if a SAS subset exists; skip if not.
    Commit: `docs(amendments): GIGASTROKE GCST integer lock per D-02`.

    **(2) Aragam 2022 ZIP enumeration (D-03; ~5 min automated):**
    ```bash
    mkdir -p data/raw/sumstats_v2/Aragam2022/
    unzip -l data/raw/sumstats_v2/Aragam2022/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip \
      | tee data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt
    ```
    Inspect manifest. If AFR file (e.g. `Aragam2022_AFR_subset.tsv` or any file with `AFR`/`AA` token) is present → D-03 branch (a): row 23 harmonizes via harmonize_aragam. If absent → D-03 branch (b): mark row 23 for Klarin 2018 fallback in SUMSTATS-UPGRADE.tsv column `notes` (value: "D-03 branch b: Aragam ZIP lacks AFR; use Klarin 2018 MVP-AFR-CAD fallback per SUMSTATS-UPGRADE §Q3"). Commit: `chore(m1): aragam zip manifest + D-03 branch disposition`.

    **(3) MVP Giri D-06 primary result disposition (~10 min Carter active):**
    Review wave0_probes.log Probe 2 outcome from Task 2. Record verdict in SUMSTATS-MANUAL-FETCH-STATUS.md:
    - If Giri sumstats are available on GWAS-Catalog → add row to SUMSTATS-UPGRADE.tsv with resolved download_url + expected_filename; Wave 1 harmonizes as Giri.
    - If not available → set SUMSTATS-UPGRADE.tsv row 13 column `notes` = "D-06 fallback: AoU Workbench AFR-SBP derivation per CONTEXT D-07; Wave 1 marks DEFERRED, not BLOCKED". Carter separately kicks off the AoU derivation using AOU-LD-PIPELINE.md §2 P1-P7 scaffolding (out of band from M1 planner execution).

    **(4) DEC-2026-04-24 DECISIONS.md entry (mandatory regardless of #3 outcome):**
    Append new decision block to .planning/DECISIONS.md (use exact format of existing 2026-04-22 blocks):

    ```markdown
    ## 2026-04-24 — DEC-2026-04-24-01: GRCh37 canonical target for M1 harmonized sumstats (override of Amendment §3 M1 "GRCh38" wording)

    **Decision:** Keep GRCh37 as the canonical analytic plane across all M1 harmonized sumstats per CONTEXT D-08. Amendment §3 M1 text reading "Harmonize to GRCh38" is overridden. Two b38-native sources (Loh 2022 BMI rows 3-4, GBMI asthma rows 18-20 of SUMSTATS-UPGRADE.tsv) undergo b38→b37 liftover at harmonize step using pyliftover + `data/external/liftover/hg38ToHg19.over.chain.gz` + 5% drop-rate hard-fail ceiling. All other 42 source files are b37 native.

    **Alternatives considered:** (a) GRCh38 per Amendment §3 literal — would require lifting 42 sources instead of 2 + forcing LDSC reference LD re-keying + breaking Evangelou 2018 T1-spine reuse; (b) GRCh37 per D-08 (adopted).

    **Why:** 42 of 47 source files are b37 native. 1000G Phase 3 reference panels at `data/external/ldscore/eur_w_ld_chr/` are b37. Evangelou 2018 SBP-EUR at `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz` (T1 spine reuse) is b37. Flipping canonical to b38 would force 42 liftovers and a reference-LD rebuild for 0 analytic gain.

    **How to apply:** Harmonizer modules for Loh 2022 (`harmonize_yengo.py` loh-variant path) and GBMI asthma (extended `harmonize_gbmi.py` with opt-in liftover flag) call `sumstats_utils.liftover_to_grch37(df, chain_file="data/external/liftover/hg38ToHg19.over.chain.gz", max_drop_rate=0.05)`. Filename convention appends `.GRCh37` token unconditionally.
    ```

    ```markdown
    ## 2026-04-24 — DEC-2026-04-24-02: AoU Researcher Workbench compute scope expansion into M1 (override of DEC-2026-04-22-04 M3-only scope)

    **Decision:** Adopt AoU Researcher Workbench AFR-SBP derivation as M1 D-06 fallback if GWAS-Catalog Giri 2019 summary-only attempt fails. This adds an AoU compute path to M1 that DEC-2026-04-22-04 had previously scoped to M3 only. Egress-audit scaffolding from AOU-LD-PIPELINE.md §2 P1–P7 is reusable for AFR-SBP derivation with minimal adaptation. Dual egress-audit entry required (one for M1 AFR-SBP if fired, one for M3 AFR-LD).

    **Alternatives considered:** (a) Keep M1 AoU-free by dropping AFR-BP — rejected per D-06 ("drop AFR-BP from M1 is off-table"; Amendment §4 locked inventory holds); (b) dbGaP phs001672 DUA submission — rejected per D-06 (critical-path killer, REQ-PUBLIC-DATA-ONLY path avoids DUA where possible); (c) Expand scope per D-07 (adopted).

    **Why:** Amendment §4 lock on 45-row trait × ancestry inventory is binding. D-06 primary (GWAS-Catalog public summary-only) is preferred path; if it fails, D-06 fallback (AoU) is the only REQ-PUBLIC-DATA-ONLY-compatible option. dbGaP is explicitly off-table. Scope expansion to M1 is a pragmatic acceptance of the cost (single AFR-SBP derivation, ~1-2 weeks AoU compute, reuses the P1-P7 scaffolding M3 was going to require anyway).

    **How to apply:** If Wave 0 probe #2 (Giri GWAS-Catalog check) returned negative AND Carter has not yet kicked off AoU AFR-SBP derivation, the Wave 1 download rule for row 13 emits status=DEFERRED with a `.placeholder` file pointing to the AoU derivation SOP. M1 closeout does not block on AFR-SBP; Wave 3 LDSC matrix has at most 44 keys instead of 45 until AoU artifact lands.
    ```

    Separately pre-paste-check .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md for the wording "Harmonize to GRCh38" or "harmonize to build 38"; if found, edit the wording inline to "Harmonize to GRCh37 per DEC-2026-04-24-01 (two b38-native sources lifted via pyliftover)". Commit: `docs(amendments): DEC-2026-04-24 GRCh37 canonical + M1 AoU scope expansion; pre-paste OSF text consistency`.
  </how-to-verify>
  <resume-signal>Type "approved" after the three edits + one commit land, or describe which step blocked.</resume-signal>
</task>

</tasks>

<threat_model>
security_enforcement disabled for this phase (data-pipeline sumstats harmonization; no user auth; no web surface; no secrets). No STRIDE register required. Public-data-only policy covered under REQ-PUBLIC-DATA-ONLY acceptance (every data source in trait_inventory.yaml declares `license` + `public: true`).
</threat_model>

<verification>
# Wave 0 global gate
test -f envs/m1-harmonize.yml \
  && test -f envs/m1-munge.yml \
  && test -f envs/m1-ldsc-rg.yml \
  && test -f envs/m1-qc.yml \
  && test -f envs/m1-download.yml \
  && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/ -q --tb=short \
  && test -s data/external/liftover/hg38ToHg19.over.chain.gz \
  && test -d data/external/ldscore/eur_w_ld_chr \
  && test -f data/external/ldscore/w_hm3.snplist \
  && test -f data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt \
  && ! grep -q "GCST90104540-series" .planning/amendments/SUMSTATS-UPGRADE.tsv \
  && grep -q "DEC-2026-04-24-01" .planning/DECISIONS.md \
  && grep -q "DEC-2026-04-24-02" .planning/DECISIONS.md
</verification>

<success_criteria>
- Five `envs/m1-*.yml` files solve via `mamba env create --dry-run`
- `pytest tests/m1/ --collect-only` reports zero import errors and at least 5 tests collected
- `pytest tests/m1/test_palindromic_filter.py tests/m1/test_harmonizer_contract.py -x` exits 0
- `data/external/liftover/hg38ToHg19.over.chain.gz` is >500 KB and `gzip -t` passes
- `data/external/ldscore/eur_w_ld_chr/` contains per-chromosome `.l2.ldscore.gz` + `.l2.M_5_50` files for chr1..chr22
- `data/external/ldscore/w_hm3.snplist` has ~1.2M lines (3-column TSV)
- MAGIC FTP probe recorded in `wave0_probes.log` (pass OR documented fallback)
- Giri 2019 GWAS-Catalog probe recorded in `SUMSTATS-MANUAL-FETCH-STATUS.md`
- LDSC 2-trait smoke run wall-time recorded in `wave0_probes.log`
- `SUMSTATS-UPGRADE.tsv` no longer contains the string `GCST90104540-series` (integer accessions in place)
- `aragam_zip_manifest.txt` committed; D-03 branch disposition (a or b) recorded
- Two new decision blocks (`DEC-2026-04-24-01`, `DEC-2026-04-24-02`) present in `.planning/DECISIONS.md`
- `OSF-AMENDMENT-TEXT-2026-04-22.md` pre-paste consistent with GRCh37 (no lingering GRCh38 assertion)
</success_criteria>

<output>
After completion, create `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-00-SUMMARY.md` with:
- Conda env solve results (5 lines)
- pytest collection count + pass count
- Chain-file + LDSC reference LD + HM3 SNP list sizes
- Three Wave 0 probe outcomes (verbatim from SUMSTATS-MANUAL-FETCH-STATUS.md)
- D-02 GIGASTROKE resolved accessions (5 integer GCSTs + file names)
- D-03 Aragam ZIP contents (unzip -l output summary)
- D-06 disposition (primary success OR fallback documented)
- DEC-2026-04-24-01 + -02 commit hashes
</output>
</content>
</invoke>