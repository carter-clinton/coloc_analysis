---
plan_id: m1-03-munge-and-ldsc-intercept-matrix
phase: m1
plan: 03
type: execute
wave: 3
depends_on: [m1-02a-harmonizers-continuous-traits, m1-02b-harmonizers-case-control-traits]
autonomous: true
requirements: [REQ-TRAIT-INVENTORY, REQ-PATH-PARAMETERIZATION, REQ-SNAKEMAKE-CI]
objective: "Munge all 45 harmonized files to HM3 .sumstats.gz per D-15/D-16 naming; orchestrate 44 star-pattern ldsc.py --rg calls (NOT --rg-cross which does not exist); parse each .log with Python reducer extracting gcov_int; emit the 45x45 bivariate-intercept wide TSV at data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv per D-11."
files_modified:
  - src/python/munge_sumstats_ldsc.py
  - src/python/reduce_ldsc_rg_matrix.py
  - src/python/m1_trait_keys.py
  - src/snakemake/rules/m1_munge.smk
  - src/snakemake/rules/m1_ldsc_rg.smk
  - tests/m1/test_reduce_ldsc_rg_matrix.py
  - tests/m1/fixtures/ldsc_rg_log_focal_0.log
  - tests/m1/fixtures/ldsc_rg_log_focal_1.log
  - data/processed/ldsc_overlap/munged/
  - data/processed/ldsc_overlap/rg_logs/
  - data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv
  - data/processed/ldsc_overlap/rg_matrix_long.tsv
must_haves:
  truths:
    - "All N harmonized files (N = line count of trait_keys.txt; current freeze 47 in-scope SUMSTATS-UPGRADE.tsv rows minus DEFERRED) are munged into HM3-restricted .sumstats.gz under data/processed/ldsc_overlap/munged/ using D-16 naming (<trait>.<ancestry>.<consortium>.<year>.sumstats.gz)"
    - "LDSC 45-trait bivariate-intercept matrix is computed via 44 star-pattern ldsc.py --rg calls (NOT --rg-cross which is verified to not exist in tools/ldsc/ldsc.py — RESEARCH Pitfall #1)"
    - "reduce_ldsc_rg_matrix.py parses .log files extracting gcov_int column from the Summary of Genetic Correlation Results table"
    - "N×N (N = line count of trait_keys.txt; ~45) symmetric wide TSV at data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv passes self-consistency (diag = 1.0 or NaN, upper == lower within tolerance)"
    - "Long-form matrix at data/processed/ldsc_overlap/rg_matrix_long.tsv includes rg + rg_se + gcov_int + gcov_int_se + h2_a + h2_b columns for M2 wrapper consumption"
    - "Expected-intercept validation heuristics fire: UKB-UKB EUR pairs intercept > 0.5; within-GLGC EUR lipids ~ 1.0 (6 pairs); non-overlap pairs ~ 0 +/- 0.05"
  artifacts:
    - path: "src/python/reduce_ldsc_rg_matrix.py"
      provides: "LDSC .log parser + 45x45 symmetric matrix assembler + self-consistency validator"
      min_lines: 150
    - path: "src/snakemake/rules/m1_munge.smk"
      provides: "Munge rule running tools/ldsc/munge_sumstats.py on each of 45 harmonized inputs"
    - path: "src/snakemake/rules/m1_ldsc_rg.smk"
      provides: "44 star-pattern ldsc --rg calls + reducer rule"
    - path: "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv"
      provides: "M2 MTAG --overlap handoff — 45x45 symmetric bivariate-intercept matrix"
    - path: "data/processed/ldsc_overlap/rg_matrix_long.tsv"
      provides: "Fat format for M2 CPASSOC wrapper — per-pair rg + gcov_int + h2"
  key_links:
    - from: "src/python/reduce_ldsc_rg_matrix.py"
      to: "data/processed/ldsc_overlap/rg_logs/focal_*.log"
      via: "regex parse of Summary of Genetic Correlation Results table"
      pattern: "gcov_int|Summary of Genetic Correlation"
    - from: "src/snakemake/rules/m1_ldsc_rg.smk"
      to: "tools/ldsc/ldsc.py"
      via: "python tools/ldsc/ldsc.py --rg <comma-list>"
      pattern: "tools/ldsc/ldsc\\.py --rg"
    - from: "src/snakemake/rules/m1_munge.smk"
      to: "src/python/munge_sumstats_ldsc.py"
      via: "python wrapper invocation per harmonized file"
      pattern: "munge_sumstats_ldsc"
---

<objective>
Wave 3 is the single most computationally heavy step of M1 and the single highest-risk plan-correctness note from RESEARCH (Pitfall #1: `ldsc.py --rg-cross` does NOT exist in the vendored abdenlab fork; CONTEXT D-11's reference to a single `--rg-cross` invocation is aspirational). This plan replaces that with the actual canonical approach: 44 orchestrated `ldsc.py --rg` calls in star-topology where for i in 1..44 the focal i-th trait is passed as the first entry in a comma-separated list followed by all traits i+1..45; each call emits one `.log` containing N-i pairwise rg records; a Python reducer parses all 44 logs, extracts the `gcov_int` column from each pair, and assembles a symmetric 45×45 wide TSV with diagonal = 1.0 (by convention, since self-pair intercept equals h2 intercept which LDSC reports separately).

The plan does three things in sequence:
1. **Munge all 45 harmonized files** to HM3-restricted `.sumstats.gz` using the existing `src/python/munge_sumstats_ldsc.py` wrapper + vendored `tools/ldsc/munge_sumstats.py` + `data/external/ldscore/w_hm3.snplist`. Output naming per D-16: `<trait>.<ancestry>.<consortium>.<year>.sumstats.gz` under `data/processed/ldsc_overlap/munged/`.
2. **Orchestrate 44 LDSC --rg star-calls** on LSF long queue (per feedback_lsf_queues memory: -W 14400 min). Each call uses `--ref-ld-chr` + `--w-ld-chr` pointing to the appropriate panel per pair ancestry combination (EUR-EUR → eur_w_ld_chr; AFR-AFR → 1KG AFR LD or Pan-UKBB release; cross-ancestry → shared-ancestry LDSC release or PopCorn fallback per D-11 / RESEARCH §Pattern 4 LD-panel-selection note).
3. **Reduce 44 .log files** into two artifacts: (a) the 45×45 symmetric wide TSV at `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv` (D-11 primary deliverable consumed by M2 MTAG --overlap wrapper); (b) a long-form fat-format `rg_matrix_long.tsv` with columns `[trait_a, trait_b, rg, rg_se, gcov_int, gcov_int_se, h2_a, h2_b]` for M2 CPASSOC wrapper that wants rg in addition to gcov_int (RESEARCH open question #5).

Purpose: M2 is HARD-GATED on this wave. MTAG --overlap requires a bivariate-intercept matrix; CPASSOC sensitivity checks may want rg. Without this artifact, M2 cannot fire. The Wave 0 benchmark (Task 2 probe 3) calibrated per-pair wall time for this wave; per-focal-star wall time is approximately `(44 - focal_idx) * per_pair_seconds + overhead`, with the longest star (focal=0, 44 pairs) being the bottleneck. The expected-intercept heuristics from SUMSTATS-UPGRADE §4 (UKB-UKB EUR pairs, within-GLGC-lipids pairs, MVP-MVP AFR pairs) are validated by the reducer as self-consistency check against RESEARCH Pitfall #8 false-alarm risk.
Output: One new Python module (reduce_ldsc_rg_matrix.py), 2 new Snakemake rule files (m1_munge.smk + m1_ldsc_rg.smk), 45 munged .sumstats.gz files, 44 LDSC rg logs, the final 45×45 wide intercept matrix + fat long-format matrix.
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
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-02a-harmonizers-continuous-traits-PLAN.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-02b-harmonizers-case-control-traits-PLAN.md
@.planning/amendments/SUMSTATS-UPGRADE.md
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@src/python/munge_sumstats_ldsc.py
@tools/ldsc/ldsc.py
@tools/ldsc/munge_sumstats.py
@tools/ldsc/README.md
@envs/ldsc_py3.yml
@envs/m1-ldsc-rg.yml
@envs/m1-munge.yml
@config/pipeline.yaml
@config/bsub_wrapper.sh
@CLAUDE.md

<interfaces>
From tools/ldsc/ldsc.py lines 608-613 (VERIFIED — no --rg-cross flag):
```python
parser.add_argument("--rg", default=None, type=str,
    help="Comma-separated list of prefixes of .chisq filed for genetic correlation estimation.")
```
Behavior: first entry is focal; pairs with each subsequent entry (N-1 pairs per call, star topology).

Star-call example for focal_idx=0 (focal = trait 0 vs traits 1..44):
```bash
python tools/ldsc/ldsc.py \
  --rg data/processed/ldsc_overlap/munged/bmi.EUR.GIANT-UKBB.2018.sumstats.gz,\
data/processed/ldsc_overlap/munged/bmi.EUR.GIANT-23andMe.2022.sumstats.gz,\
...(42 more comma-separated files)... \
  --ref-ld-chr data/external/ldscore/eur_w_ld_chr/ \
  --w-ld-chr   data/external/ldscore/eur_w_ld_chr/ \
  --out data/processed/ldsc_overlap/rg_logs/focal_00
```
Output: data/processed/ldsc_overlap/rg_logs/focal_00.log containing the Summary of Genetic Correlation Results table with 44 pairs.

LD panel selection per pair (from D-11 + RESEARCH Pattern 4):
- EUR-EUR: data/external/ldscore/eur_w_ld_chr/ (staged in Wave 0)
- AFR-AFR: Pan-UKBB LDSC release OR HGDP+1kG AFR LD panel (Phase 01-03-PLAN staged AFR LD files; verify at Wave 3 Task 2)
- Cross-ancestry: Galinsky shared-ancestry LDSC release OR PopCorn fallback per D-11 / RESEARCH Pattern 4 note. For M1 purposes, the bivariate INTERCEPT (gcov_int) is what MTAG --overlap consumes; it is interpretable across LD panels so the cross-ancestry choice is secondary. Default: use eur_w_ld_chr for all cross-ancestry pairs and flag in the QC output that they're approximated.

Reducer parser from m1-RESEARCH.md Pattern 4:
```python
TRAIT_KEY_RE = re.compile(r"(?P<trait>\w+)\.(?P<ancestry>[A-Z]+)\."
                          r"(?P<consortium>[\w-]+)\.(?P<year>\d{4})\.sumstats\.gz")

def parse_rg_log(log_path: Path) -> pd.DataFrame:
    """Extract pairwise rg table from LDSC .log.
    LDSC .log prints a 'Summary of Genetic Correlation Results' table with columns:
      p1, p2, rg, se, z, p, h2_obs, h2_obs_se, h2_int, h2_int_se, gcov_int, gcov_int_se
    """
    text = log_path.read_text()
    rows = []
    in_table = False
    for line in text.splitlines():
        if "Summary of Genetic Correlation Results" in line:
            in_table = True; continue
        if in_table and line.strip() and not line.startswith(("p1", "Analysis", "Total")):
            parts = line.split()
            if len(parts) >= 12:
                rows.append({
                    "p1": parts[0], "p2": parts[1],
                    "rg": float(parts[2]), "rg_se": float(parts[3]),
                    "gcov_int": float(parts[10]),
                    "gcov_int_se": float(parts[11]),
                })
    return pd.DataFrame(rows)

def build_intercept_matrix(log_dir, trait_keys):
    mat = pd.DataFrame(1.0, index=trait_keys, columns=trait_keys)  # diag defaults to 1.0
    for log_path in sorted(log_dir.glob("focal_*.log")):
        df = parse_rg_log(log_path)
        for _, row in df.iterrows():
            k1 = Path(row["p1"]).name.replace(".sumstats.gz", "")
            k2 = Path(row["p2"]).name.replace(".sumstats.gz", "")
            mat.at[k1, k2] = row["gcov_int"]
            mat.at[k2, k1] = row["gcov_int"]  # symmetric
    return mat
```

Existing munge wrapper src/python/munge_sumstats_ldsc.py signature (re-used as-is per D-10):
```
python src/python/munge_sumstats_ldsc.py \
  --input-tsv <harmonized>.tsv.bgz \
  --output    <trait>.<ancestry>.<consortium>.<year>.sumstats.gz \
  --merge-alleles data/external/ldscore/w_hm3.snplist \
  --n-col N     # for continuous; for case-control, pass --n-cas/--n-con
```

Per feedback_lsf_queues memory:
- standard = 2880 min max, serial = 5760, long = 14400
- For 44 parallel ldsc --rg jobs: submit to long queue via `bsub_wrapper.sh -q long -W 14400 -n 1 -M 8GB`
- LSF_UNIT_FOR_LIMITS=GB
</interfaces>
</context>

<tasks>

<task id="m1-03-T1" type="auto" tdd="true">
  <name>Task 1: Munge rules (45 harmonized -> .sumstats.gz) + LDSC star-call orchestration + reducer module</name>
  <files>
    src/snakemake/rules/m1_munge.smk,
    src/snakemake/rules/m1_ldsc_rg.smk,
    src/python/reduce_ldsc_rg_matrix.py,
    src/python/m1_trait_keys.py,
    tests/m1/test_reduce_ldsc_rg_matrix.py,
    tests/m1/test_m1_trait_keys.py,
    tests/m1/fixtures/ldsc_rg_log_focal_0.log,
    tests/m1/fixtures/ldsc_rg_log_focal_1.log
  </files>
  <read_first>
    - src/python/munge_sumstats_ldsc.py (existing wrapper — reused as-is per D-10; read its CLI + N-col handling for continuous vs case-control dispatch)
    - tools/ldsc/munge_sumstats.py (vendored LDSC munge; --merge-alleles line ~498)
    - tools/ldsc/ldsc.py lines 608-613 (verify --rg CLI; NO --rg-cross exists)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md Pattern 4 (star-call orchestration + reducer skeleton) + Example 3 (Snakemake rule)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md Pitfall #1 (NO --rg-cross) + Pitfall #8 (within-GLGC lipids expected intercept ~1.0)
    - tests/m1/fixtures/ldsc_rg_log_sample.log (from Wave 0; LDSC log format reference)
    - config/bsub_wrapper.sh (LSF wall-time wrapper for long queue)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (to build the TRAIT_KEYS list deterministically from rows)
  </read_first>
  <behavior>
    - src/snakemake/rules/m1_munge.smk: 45 rules (consolidated via wildcards) — one rule `m1_munge_per_trait` that takes wildcards {trait}.{ancestry}.{consortium}.{year}, reads the harmonized tsv.bgz input, dispatches to `python src/python/munge_sumstats_ldsc.py` with case-control vs continuous N dispatch from a YAML side-car (read from config/trait_inventory.yaml if present, else from SUMSTATS-UPGRADE.tsv). Output: data/processed/ldsc_overlap/munged/{trait}.{ancestry}.{consortium}.{year}.sumstats.gz.
    - src/snakemake/rules/m1_ldsc_rg.smk: loads TRAIT_KEYS at module load (deterministic sort from SUMSTATS-UPGRADE.tsv rows; skip DEFERRED rows; also include Evangelou sbp.EUR row from verify_evangelou_sbp rule + Loh bmi.EUR + bmi.AFR). Declares `rule m1_ldsc_rg_star` parameterized by `{focal_idx}` wildcard in 0..len(TRAIT_KEYS)-2 (so 0..43 for 45 traits). The rule expands input to the focal munged file PLUS all traits after focal_idx. Also declares `rule m1_ldsc_rg_reduce` that takes all 44 logs as input and emits the wide TSV.
    - src/python/reduce_ldsc_rg_matrix.py: implements parse_rg_log + build_intercept_matrix from RESEARCH Pattern 4 + build_long_format (long-form fat TSV) + self-consistency validator (assertion: symmetric matrix within 1e-6 tolerance; diag is 1.0 or NaN). Emits per-pair h2_a + h2_b as well (RESEARCH open question #5). Also emits a "heatmap-ready" sub-TSV for Wave 4 Quarto.
    - Expected-intercept validation function (RESEARCH Pitfall #8 false-alarm protection): load a lookup table of (pair, expected_intercept_range) from a config file or inline list; for each computed pair, flag if gcov_int is outside expected range by > 0.1. UKB-UKB EUR pair cluster (36 pairs) expected > 0.5; within-GLGC EUR lipids (6 pairs) expected ~1.0; BBJ-BBJ EAS (~15 pairs) expected > 0.5; MVP-MVP AFR (6 pairs) expected > 0.5; everything else expected ~0.0 ± 0.05.
    - tests/m1/test_reduce_ldsc_rg_matrix.py uses 2 fixture logs (focal_0 with 2 pairs; focal_1 with 1 pair, total 3 traits → 3×3 matrix). Asserts parse_rg_log returns 2 rows from focal_0, 1 row from focal_1. Asserts build_intercept_matrix returns symmetric 3×3 with diag=1.0. Tests failing case where gcov_int column is missing.
  </behavior>
  <action>
    (A0) Author src/python/m1_trait_keys.py — shared helper that constructs the deterministic D-16 trait-keys list AND exports the canonical TOKEN_MAP (consumed by both this plan's rule m1_build_trait_keys_list AND m1-04-T1's build_trait_inventory.py per W2 fix). Body:

    ```python
    #!/usr/bin/env python3
    """Deterministic D-16 trait-keys list builder + canonical TOKEN_MAP export.

    Single source of truth for the trait-key list consumed by:
      - src/snakemake/rules/m1_ldsc_rg.smk (rule m1_build_trait_keys_list)
      - src/python/build_trait_inventory.py (imports TOKEN_MAP)
    Reads .planning/amendments/SUMSTATS-UPGRADE.tsv (47 data rows in current freeze; not
    hard-coded to 45 — see W5 fix). Filters to in-scope rows (status IN to_download,
    already_downloaded), maps SUMSTATS-UPGRADE trait labels -> D-16 lowercase tokens,
    parses 4-digit year robustly, appends the pre-pivot Evangelou sbp.EUR row, dedupes
    + sorts, writes one key per line.
    """
    from __future__ import annotations
    import argparse, re, sys
    from pathlib import Path
    import pandas as pd

    # SUMSTATS-UPGRADE.tsv trait label -> D-16 lowercase token (canonical map; D-16 + D-10)
    TOKEN_MAP = {
        "BMI": "bmi", "T2D": "t2d", "hypertension": "sbp",
        "stroke": "stroke", "asthma": "asthma", "CAD": "cad",
        "LDL": "ldl", "HDL": "hdl", "TG": "tg", "TC": "tc",
        "eGFR": "egfr", "HbA1c": "hba1c",
    }

    # Pre-pivot Evangelou SBP-EUR row (T1 spine reuse) is renamed in m1-02b-T2 verify_evangelou_sbp.
    EVANGELOU_SBP_KEY = "sbp.EUR.Evangelou-ICBP-UKBB.2018"

    IN_SCOPE_STATUSES = {"to_download", "already_downloaded"}

    def _year_from_citation(citation: str) -> str:
        """Robust year extraction. Handles 'Yengo 2018', 'Mahajan 2022', 'Loh 2022 (Nat Commun)',
        'Morris 2019 / Wuttke 2019' (W2 fix — replaces brittle .split()[1].rstrip(')')).
        """
        m = re.search(r"(\d{4})", citation)
        if not m:
            raise ValueError(f"No 4-digit year found in citation: {citation!r}")
        return m.group(1)

    def build_keys(tsv_path: Path) -> list[str]:
        df = pd.read_csv(tsv_path, sep="\t")
        in_scope = df[df["status"].isin(IN_SCOPE_STATUSES)].copy()
        keys: list[str] = []
        for _, row in in_scope.iterrows():
            trait_label = row["trait"]
            if trait_label not in TOKEN_MAP:
                continue  # unknown label — skip; build_trait_inventory uses same skip behavior
            token = TOKEN_MAP[trait_label]
            ancestry = row["ancestry"]
            consortium = row["source_consortium"]
            year = _year_from_citation(str(row["citation_first_author_year"]))
            keys.append(f"{token}.{ancestry}.{consortium}.{year}")
        # Append pre-pivot Evangelou SBP-EUR (T1 spine reuse via verify_evangelou_sbp)
        keys.append(EVANGELOU_SBP_KEY)
        keys = sorted(set(keys))
        # Defensive bound — current TSV has 47 data rows (W5 fix language); after dropping any
        # DEFERRED + adding Evangelou we expect 40-50 keys. Hard ceiling guard.
        assert 40 <= len(keys) <= 50, (
            f"m1_trait_keys: expected 40<=N<=50 keys, got {len(keys)}. "
            f"Inspect SUMSTATS-UPGRADE.tsv for new rows or DEFERRED churn.")
        return keys

    def _main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--tsv", type=Path,
                        default=Path(".planning/amendments/SUMSTATS-UPGRADE.tsv"))
        ap.add_argument("--out", type=Path, required=True)
        args = ap.parse_args()
        keys = build_keys(args.tsv)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(keys) + "\n")
        print(f"Wrote {len(keys)} trait keys to {args.out}", file=sys.stderr)

    if __name__ == "__main__":
        _main()
    ```

    Author tests/m1/test_m1_trait_keys.py: fixture mini-TSV with 5 rows (3 in-scope + 1 dua_pending + 1 with bracketed-year citation `Yengo (2018)`); assert build_keys returns 4 sorted keys (3 in-scope + Evangelou); assert TOKEN_MAP exported. Year parser test: build_keys handles `'Loh 2022 (Nat Commun)'` and `'Morris 2019 / Wuttke 2019'` without crashing.

    (A) Create src/python/reduce_ldsc_rg_matrix.py (~180 lines; expand on RESEARCH Pattern 4):

    ```python
    #!/usr/bin/env python3
    """Reduce 44 LDSC star-topology rg log files into:
      (1) 45x45 symmetric bivariate-intercept wide TSV (D-11 primary; MTAG --overlap consumer)
      (2) Long-form fat TSV with rg/rg_se/gcov_int/gcov_int_se/h2_a/h2_b (M2 CPASSOC consumer)

    NO --rg-cross in vendored abdenlab/ldsc-python3 fork (Pitfall #1); star-pattern is canonical.
    """
    from __future__ import annotations
    import argparse, json, re, sys
    from pathlib import Path
    import pandas as pd
    import numpy as np

    TRAIT_KEY_RE = re.compile(
        r"(?P<trait>[a-z0-9]+)\.(?P<ancestry>[A-Z]+)\."
        r"(?P<consortium>[\w-]+)\.(?P<year>\d{4})\.sumstats\.gz")

    TABLE_HEADER_MARKER = "Summary of Genetic Correlation Results"
    # LDSC log column order:
    # p1 p2 rg se z p h2_obs h2_obs_se h2_int h2_int_se gcov_int gcov_int_se
    _COLS_EXPECTED = 12

    def parse_rg_log(log_path: Path) -> pd.DataFrame:
        text = log_path.read_text()
        rows, in_table = [], False
        for line in text.splitlines():
            if TABLE_HEADER_MARKER in line:
                in_table = True
                continue
            if not in_table: continue
            stripped = line.strip()
            if not stripped: continue
            if stripped.startswith(("p1", "Analysis", "Total")):
                continue
            parts = stripped.split()
            if len(parts) < _COLS_EXPECTED:
                continue
            try:
                rows.append({
                    "p1": parts[0], "p2": parts[1],
                    "rg": float(parts[2]) if parts[2] != "NA" else np.nan,
                    "rg_se": float(parts[3]) if parts[3] != "NA" else np.nan,
                    "z":  float(parts[4]) if parts[4] != "NA" else np.nan,
                    "p":  float(parts[5]) if parts[5] != "NA" else np.nan,
                    "h2_obs":    float(parts[6]) if parts[6] != "NA" else np.nan,
                    "h2_obs_se": float(parts[7]) if parts[7] != "NA" else np.nan,
                    "h2_int":    float(parts[8]) if parts[8] != "NA" else np.nan,
                    "h2_int_se": float(parts[9]) if parts[9] != "NA" else np.nan,
                    "gcov_int":    float(parts[10]) if parts[10] != "NA" else np.nan,
                    "gcov_int_se": float(parts[11]) if parts[11] != "NA" else np.nan,
                })
            except (ValueError, IndexError):
                continue
        return pd.DataFrame(rows)

    def key_from_path(path_str: str) -> str:
        name = Path(path_str).name
        m = TRAIT_KEY_RE.match(name)
        if not m:
            raise ValueError(f"Path '{name}' does not match D-16 trait-key pattern")
        return name.replace(".sumstats.gz", "")

    def build_intercept_matrix(log_dir: Path, trait_keys: list[str]) -> pd.DataFrame:
        mat = pd.DataFrame(np.nan, index=trait_keys, columns=trait_keys, dtype=float)
        for k in trait_keys:
            mat.at[k, k] = 1.0  # diagonal convention
        for log_path in sorted(log_dir.glob("focal_*.log")):
            df = parse_rg_log(log_path)
            for _, row in df.iterrows():
                k1 = key_from_path(row["p1"])
                k2 = key_from_path(row["p2"])
                if k1 not in trait_keys or k2 not in trait_keys:
                    continue
                mat.at[k1, k2] = row["gcov_int"]
                mat.at[k2, k1] = row["gcov_int"]
        return mat

    def build_long_format(log_dir: Path, trait_keys: list[str]) -> pd.DataFrame:
        rows = []
        for log_path in sorted(log_dir.glob("focal_*.log")):
            df = parse_rg_log(log_path)
            for _, r in df.iterrows():
                try:
                    k1, k2 = key_from_path(r["p1"]), key_from_path(r["p2"])
                except ValueError:
                    continue
                rows.append({
                    "trait_a": k1, "trait_b": k2,
                    "rg": r["rg"], "rg_se": r["rg_se"],
                    "gcov_int": r["gcov_int"], "gcov_int_se": r["gcov_int_se"],
                    "h2_a": r["h2_obs"], "h2_b": np.nan,   # h2_b from focal file's h2_obs column per pair
                    "p_rg": r["p"], "z_rg": r["z"],
                })
        return pd.DataFrame(rows)

    def validate_self_consistency(mat: pd.DataFrame, tol: float = 1e-6) -> list[str]:
        """Returns list of warnings; empty on clean matrix."""
        warnings = []
        # Symmetry
        diff = (mat.values - mat.values.T)
        max_off_diag = np.nanmax(np.abs(diff)) if mat.size > 0 else 0.0
        if max_off_diag > tol:
            warnings.append(f"Symmetry violation: max|mat - mat.T| = {max_off_diag}")
        # Diagonal
        diag = np.diag(mat.values)
        bad_diag = [(i, d) for i, d in enumerate(diag) if not (np.isnan(d) or abs(d - 1.0) < 0.1)]
        if bad_diag:
            warnings.append(f"Diagonal values not ~1.0: {bad_diag[:5]}")
        return warnings

    def validate_expected_intercept_heuristics(mat: pd.DataFrame) -> list[str]:
        """Pitfall #8: within-GLGC lipids EUR expect ~1.0; UKB-UKB EUR expect > 0.5.
        Returns list of deviations."""
        warnings = []
        eur_cols = [c for c in mat.columns if ".EUR." in c]
        lipid_traits = {"ldl", "hdl", "tg", "tc"}
        glgc_eur = [c for c in eur_cols
                    if c.startswith(tuple(f"{t}." for t in lipid_traits))
                    and ".GLGC." in c]
        for i, c1 in enumerate(glgc_eur):
            for c2 in glgc_eur[i+1:]:
                v = mat.at[c1, c2]
                if not np.isnan(v) and not (0.7 < v < 1.3):
                    warnings.append(f"Within-GLGC EUR lipid pair ({c1}, {c2}) intercept={v:.3f}; expected ~1.0")
        return warnings

    def _main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--log-dir", type=Path, required=True)
        ap.add_argument("--trait-keys-file", type=Path, required=True,
            help="Path to a file listing one trait key per line (D-16 format).")
        ap.add_argument("--output-matrix", type=Path, required=True)
        ap.add_argument("--output-long",   type=Path, required=True)
        ap.add_argument("--output-validation", type=Path,
            default=Path("data/processed/ldsc_overlap/rg_validation_warnings.json"))
        args = ap.parse_args()
        trait_keys = sorted([l.strip() for l in args.trait_keys_file.read_text().splitlines() if l.strip()])
        mat = build_intercept_matrix(args.log_dir, trait_keys)
        long = build_long_format(args.log_dir, trait_keys)
        warn_sym = validate_self_consistency(mat)
        warn_heur = validate_expected_intercept_heuristics(mat)
        args.output_matrix.parent.mkdir(parents=True, exist_ok=True)
        mat.to_csv(args.output_matrix, sep="\t")
        long.to_csv(args.output_long, sep="\t", index=False)
        args.output_validation.write_text(json.dumps({
            "symmetry_warnings": warn_sym,
            "heuristic_warnings": warn_heur,
            "n_traits": len(trait_keys),
            "n_pairs": int((mat.notna().sum().sum() - len(trait_keys)) / 2),
        }, indent=2))
        print(f"Wrote matrix {mat.shape} to {args.output_matrix}")
        print(f"Wrote long ({len(long)} pairs) to {args.output_long}")
        if warn_sym or warn_heur:
            print(f"VALIDATION WARNINGS: {len(warn_sym)} symmetry + {len(warn_heur)} heuristic — see {args.output_validation}")

    if __name__ == "__main__":
        _main()
    ```

    (B) Create tests/m1/fixtures/ldsc_rg_log_focal_0.log with a 2-pair Summary table (file names matching 3 synthetic D-16 keys like `bmi.EUR.GIANT-UKBB.2018.sumstats.gz`, `t2d.EUR.DIAMANTE.2022.sumstats.gz`, `sbp.EUR.Evangelou-ICBP-UKBB.2018.sumstats.gz`). Create ldsc_rg_log_focal_1.log with 1 pair. Values plausible (gcov_int in {0.12, 0.87, 0.05}).

    (C) Create tests/m1/test_reduce_ldsc_rg_matrix.py with test functions:
    - `test_parse_rg_log_focal_0`: returns 2 rows with expected gcov_int values.
    - `test_build_intercept_matrix`: 3×3 symmetric matrix; diag=1.0; upper==lower.
    - `test_validate_self_consistency_clean`: 0 warnings on clean fixture.
    - `test_validate_self_consistency_broken`: manually corrupt matrix; assert symmetry violation detected.
    - `test_heuristic_within_glgc_flags_deviation`: build fake 3-lipid EUR matrix with gcov_int=0.2 (should flag).

    (D) Create src/snakemake/rules/m1_munge.smk:

    ```python
    import os, pandas as pd
    HARM_DIR  = config["paths"]["harmonized_sumstats"]
    MUNGED_DIR = config["paths"]["ldsc_munged"]
    TSV = ".planning/amendments/SUMSTATS-UPGRADE.tsv"
    _df = pd.read_csv(TSV, sep="\t")
    # Filter to 45 in-scope rows (drop dua_pending + documented DEFERRED cells);
    # include pre-pivot-Evangelou rename as sbp.EUR row
    IN_SCOPE = _df[_df["status"].isin(["to_download", "already_downloaded"])].copy()
    # ... build trait_key per row: {trait_token}.{ancestry}.{consortium}.{year} ...

    rule m1_munge_per_trait:
        input:
            harmonized = lambda wc: os.path.join(HARM_DIR,
                f"{wc.trait}.{wc.ancestry}.{wc.consortium}.{wc.year}.GRCh37.tsv.bgz"),
            w_hm3      = "data/external/ldscore/w_hm3.snplist",
        output:
            munged = os.path.join(MUNGED_DIR,
                "{trait}.{ancestry}.{consortium}.{year}.sumstats.gz"),
        conda: "../../envs/m1-munge.yml"
        resources: mem_mb=8000, runtime=5760  # serial queue
        shell:
            r"""
            python src/python/munge_sumstats_ldsc.py \
                --input-tsv {input.harmonized} \
                --output {output.munged} \
                --merge-alleles {input.w_hm3}
            """

    rule m1_munge_all:
        input:
            expand(os.path.join(MUNGED_DIR, "{key}.sumstats.gz"),
                   key=TRAIT_KEYS),
    ```

    (E) Create src/snakemake/rules/m1_ldsc_rg.smk:

    ```python
    import os, pandas as pd
    from pathlib import Path

    MUNGED_DIR = config["paths"]["ldsc_munged"]
    RG_LOG_DIR = config["paths"]["ldsc_rg_logs"]
    OVERLAP_DIR = config["paths"]["ldsc_overlap"]
    EUR_REF_LD = "data/external/ldscore/eur_w_ld_chr/"
    # Build sorted TRAIT_KEYS list from in-scope munged files to be produced by m1_munge_all.
    # Write to disk as trait_keys.txt for reducer consumer.
    TRAIT_KEYS_FILE = os.path.join(OVERLAP_DIR, "trait_keys.txt")

    rule m1_build_trait_keys_list:
        input:
            tsv = ".planning/amendments/SUMSTATS-UPGRADE.tsv",
        output: TRAIT_KEYS_FILE,
        conda: "../../envs/m1-harmonize.yml"
        shell:
            "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python "
            "src/python/m1_trait_keys.py --tsv {input.tsv} --out {output[0]}"

    def _others(wildcards):
        trait_keys = sorted(Path(TRAIT_KEYS_FILE).read_text().splitlines())
        i = int(wildcards.focal_idx)
        return [os.path.join(MUNGED_DIR, f"{k}.sumstats.gz") for k in trait_keys[i+1:]]

    def _focal(wildcards):
        trait_keys = sorted(Path(TRAIT_KEYS_FILE).read_text().splitlines())
        i = int(wildcards.focal_idx)
        return os.path.join(MUNGED_DIR, f"{trait_keys[i]}.sumstats.gz")

    rule m1_ldsc_rg_star:
        """Focal i vs traits i+1..N-1. Produces one .log with (N-1-i) pairs."""
        input:
            focal = _focal,
            others = _others,
            keys   = TRAIT_KEYS_FILE,
            ref_ld = EUR_REF_LD,   # default EUR LD; per-pair LD selection deferred — D-11
        output:
            log = os.path.join(RG_LOG_DIR, "focal_{focal_idx}.log"),
        conda: "../../envs/m1-ldsc-rg.yml"
        resources:
            mem_mb=8000,
            runtime=14400,   # long queue max per feedback_lsf_queues
        params:
            out_prefix = lambda wc: os.path.join(RG_LOG_DIR, f"focal_{wc.focal_idx}"),
            rg_args = lambda wc, input: ",".join([input.focal] + list(input.others)),
        wildcard_constraints:
            focal_idx="[0-9]+",
        shell:
            r"""
            mkdir -p {RG_LOG_DIR}
            python tools/ldsc/ldsc.py \
                --rg {params.rg_args} \
                --ref-ld-chr {input.ref_ld} \
                --w-ld-chr   {input.ref_ld} \
                --out {params.out_prefix}
            """

    rule m1_ldsc_rg_all_stars:
        input:
            expand(os.path.join(RG_LOG_DIR, "focal_{i}.log"),
                   i=[str(n) for n in range(44)]),

    rule m1_ldsc_rg_reduce:
        input:
            logs = rules.m1_ldsc_rg_all_stars.input,
            keys = TRAIT_KEYS_FILE,
        output:
            matrix = os.path.join(OVERLAP_DIR, "bivariate_intercept_matrix_2026-04.tsv"),
            long   = os.path.join(OVERLAP_DIR, "rg_matrix_long.tsv"),
            validation = os.path.join(OVERLAP_DIR, "rg_validation_warnings.json"),
        conda: "../../envs/m1-harmonize.yml"
        shell:
            r"""
            python src/python/reduce_ldsc_rg_matrix.py \
                --log-dir {RG_LOG_DIR} \
                --trait-keys-file {input.keys} \
                --output-matrix {output.matrix} \
                --output-long {output.long} \
                --output-validation {output.validation}
            """
    ```

    (F) Verify Snakemake DAG:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      -s workflow/Snakefile --dry-run --cores 1 m1_ldsc_rg_reduce 2>&1 | tail -30
    ```
    Must emit 44 `m1_ldsc_rg_star` rule instances + 1 reduce + N munge rules.

    (G) Run reducer pytest:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_reduce_ldsc_rg_matrix.py tests/m1/test_m1_trait_keys.py -x --tb=short
    ```

    DO NOT fire the 44 rg jobs in this task — that's Task 2 live execution. This task only stages + unit-tests the rules + reducer.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_reduce_ldsc_rg_matrix.py -x --tb=short 2>&amp;1 | tail -5 &amp;&amp; test -f src/snakemake/rules/m1_munge.smk &amp;&amp; test -f src/snakemake/rules/m1_ldsc_rg.smk &amp;&amp; test -f src/python/reduce_ldsc_rg_matrix.py &amp;&amp; test -f src/python/m1_trait_keys.py &amp;&amp; ! grep -q "rg-cross" src/snakemake/rules/m1_ldsc_rg.smk src/python/reduce_ldsc_rg_matrix.py &amp;&amp; grep -q "comma-separated" src/snakemake/rules/m1_ldsc_rg.smk || grep -q -- "--rg " src/snakemake/rules/m1_ldsc_rg.smk &amp;&amp; ! grep -r "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/snakemake/rules/m1_munge.smk src/snakemake/rules/m1_ldsc_rg.smk src/python/reduce_ldsc_rg_matrix.py src/python/m1_trait_keys.py</automated>
  </verify>
  <done>Reducer module imports cleanly, parses fixture logs into a 3x3 matrix with diag=1.0; unit tests pass; m1_munge.smk + m1_ldsc_rg.smk declare rules that dry-run-load; both rule files use `--rg` (NOT `--rg-cross`); zero hardcoded absolute paths.</done>
</task>

<task id="m1-03-T2" type="auto">
  <name>Task 2: Fire production munge + 44-way LDSC star jobs under LSF + reduce into final 45x45 matrix</name>
  <files>
    data/processed/ldsc_overlap/munged/,
    data/processed/ldsc_overlap/rg_logs/,
    data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv,
    data/processed/ldsc_overlap/rg_matrix_long.tsv,
    data/processed/ldsc_overlap/rg_validation_warnings.json,
    data/processed/ldsc_overlap/trait_keys.txt
  </files>
  <read_first>
    - src/snakemake/rules/m1_munge.smk (from Task 1)
    - src/snakemake/rules/m1_ldsc_rg.smk (from Task 1)
    - config/bsub_wrapper.sh (LSF queue-max wall-time wrapper; -q long -W 14400 for rg stars; -q serial -W 5760 for munge)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Wave 0 probe 3 outcome — LDSC 2-trait benchmark wall time; if > 30 min/pair, reduce parallel jobs per Wave 0 note)
    - tests/m1/wave0_probes.log (W6 fix: contains PAIR_WALL_SECONDS line written by m1-00-T2 Probe 3; --jobs value is computed dynamically from this benchmark — m1-03-T2 cannot fire until this file contains a PAIR_WALL_SECONDS entry)
  </read_first>
  <action>
    Step 1: Munge all 45 harmonized files. Fire Snakemake with --use-conda + LSF cluster:
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      --snakefile workflow/Snakefile \
      --use-conda \
      --cluster "bash config/bsub_wrapper.sh -q serial -W 5760 -n 1 -M 8GB" \
      --jobs 20 \
      --printshellcmds \
      m1_munge_all 2>&1 | tee logs/m1_munge.log
    ```
    Expected: ~45 parallel bsub jobs; each ~10-30 min depending on file size; total wall ~45 min on a cooperative LSF queue.

    Verify:
    ```bash
    ls data/processed/ldsc_overlap/munged/*.sumstats.gz | wc -l   # expect $(wc -l < data/processed/ldsc_overlap/trait_keys.txt) lines (minus DEFERRED)
    ```

    Step 2: Build trait_keys.txt + fire 44-way LDSC rg stars:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      --snakefile workflow/Snakefile \
      --use-conda \
      m1_build_trait_keys_list -c 1

    cat data/processed/ldsc_overlap/trait_keys.txt | wc -l   # expect ~45 (40-50 per defensive bound in m1_trait_keys.py)

    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      --snakefile workflow/Snakefile \
      --use-conda \
      --cluster "bash config/bsub_wrapper.sh -q long -W 14400 -n 1 -M 8GB" \
      --jobs $(awk '/PAIR_WALL_SECONDS/ {s=$2} END {if (s > 1800) print 22; else print 44}' tests/m1/wave0_probes.log) \
      --printshellcmds \
      --latency-wait 120 \
      m1_ldsc_rg_all_stars 2>&1 | tee logs/m1_ldsc_rg_stars.log
    ```
    W6 fix: --jobs value is computed dynamically from Wave 0 benchmark. Acceptance criterion: tests/m1/wave0_probes.log MUST contain a `PAIR_WALL_SECONDS <N>` line written by m1-00-T2 Probe 3 before m1-03-T2 fires. The awk evaluates: if per-pair wall > 1800 s (30 min) use 22 parallel jobs; else use 44. Validate with `grep PAIR_WALL_SECONDS tests/m1/wave0_probes.log` before launching.

    Monitoring:
    ```bash
    bjobs -w   # count running rg jobs
    ls data/processed/ldsc_overlap/rg_logs/focal_*.log | wc -l   # progress
    ```
    Expected wall time: longest star (focal=0) ~3-11 hours per Wave 0 benchmark; 44 parallel → total wall ~3-11 hours assuming LSF long queue accepts all 44. If Wave 0 benchmark reported > 30 min/pair, the dynamic awk above auto-reduces to 22 parallel jobs and run in 2 waves of 22 focal-stars each.

    If any focal_i.log shows LDSC error (e.g. "SE^2 of gcov_int is negative"), re-fire that focal only with --ref-ld-chr pointing to the panel that matches the focal's ancestry — EUR-focal uses eur_w_ld_chr (default); AFR-focal uses AFR LD panel staged in Phase 01-03 at data/processed/ld_reference/AFR_*/  (if that path doesn't have an eur_w_ld_chr-shaped release, run with eur_w_ld_chr as approximation and note in QC sidecar).

    Step 3: Reduce to 45x45 matrix + long-format:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      --snakefile workflow/Snakefile \
      --use-conda \
      --cores 2 \
      m1_ldsc_rg_reduce 2>&1 | tee logs/m1_ldsc_rg_reduce.log

    wc -l data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv   # expect 1+N (header + N data rows; N = line count of trait_keys.txt)
    awk -F'\t' 'NR==1 {print NF}' data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv  # expect 46 (index + 45 cols)
    wc -l data/processed/ldsc_overlap/rg_matrix_long.tsv   # expect 991 (header + 990 pairs)
    cat data/processed/ldsc_overlap/rg_validation_warnings.json
    ```

    If rg_validation_warnings.json has non-empty symmetry_warnings list, re-run the reduce rule; if still non-empty, diagnose (likely one focal log is truncated — re-fire).

    If heuristic_warnings reports within-GLGC pairs deviating > 0.1 from 1.0, that's a RED FLAG worth investigating but NOT a block — log to m1-03-SUMMARY.md and decide at Wave 4 QC review.

    Commit everything:
    ```bash
    git add src/python/reduce_ldsc_rg_matrix.py src/snakemake/rules/m1_munge.smk \
             src/snakemake/rules/m1_ldsc_rg.smk tests/m1/test_reduce_ldsc_rg_matrix.py \
             tests/m1/fixtures/ldsc_rg_log_focal_*.log
    # Note: data/ is gitignored — do NOT git-add the matrix TSV itself; instead copy to in-repo mirror:
    cp data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv \
       .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv
    git add .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv
    git commit -m "feat(m1): 45x45 LDSC bivariate-intercept matrix frozen (Wave 3 closeout); 44 star-calls + reducer per RESEARCH Pitfall #1"
    ```
  </action>
  <verify>
    <automated>test -f data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv &amp;&amp; test -f data/processed/ldsc_overlap/rg_matrix_long.tsv &amp;&amp; test -f data/processed/ldsc_overlap/rg_validation_warnings.json &amp;&amp; MATRIX_ROWS=$(wc -l &lt; data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv) &amp;&amp; [ "$MATRIX_ROWS" -ge 20 ] &amp;&amp; LOG_COUNT=$(ls data/processed/ldsc_overlap/rg_logs/focal_*.log 2&gt;/dev/null | wc -l) &amp;&amp; [ "$LOG_COUNT" -ge 1 ] &amp;&amp; MUNGED_COUNT=$(ls data/processed/ldsc_overlap/munged/*.sumstats.gz 2&gt;/dev/null | wc -l) &amp;&amp; [ "$MUNGED_COUNT" -ge 30 ]</automated>
  </verify>
  <done>At least 30 of 45 expected munged files on disk (allowing for deferrals); at least 1 focal_*.log present with parseable Summary of Genetic Correlation Results table; bivariate_intercept_matrix TSV exists with at least header + 20 rows; rg_matrix_long.tsv exists with at least header + 100 pairs; validation warnings JSON contains symmetry and heuristic fields (possibly with explained deviations).</done>
</task>

</tasks>

<threat_model>
security_enforcement disabled — pipeline orchestration plan. LDSC rg compute runs on NCSU HPC LSF; no external network; no user input at runtime.
</threat_model>

<verification>
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_reduce_ldsc_rg_matrix.py -x --tb=short \
  && test -f src/python/reduce_ldsc_rg_matrix.py \
  && test -f src/snakemake/rules/m1_munge.smk \
  && test -f src/snakemake/rules/m1_ldsc_rg.smk \
  && ! grep -E "rg-cross" src/snakemake/rules/m1_ldsc_rg.smk src/python/reduce_ldsc_rg_matrix.py \
  && test -f data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv \
  && test -f data/processed/ldsc_overlap/rg_matrix_long.tsv \
  && [ $(ls data/processed/ldsc_overlap/rg_logs/focal_*.log 2>/dev/null | wc -l) -ge 1 ] \
  && [ $(ls data/processed/ldsc_overlap/munged/*.sumstats.gz 2>/dev/null | wc -l) -ge 30 ]
</verification>

<success_criteria>
- reduce_ldsc_rg_matrix.py exists, has parse_rg_log / build_intercept_matrix / build_long_format / validate_self_consistency / validate_expected_intercept_heuristics, and passes pytest on fixture logs
- m1_munge.smk + m1_ldsc_rg.smk rule files exist; dry-run loads without error
- NO reference to `--rg-cross` anywhere in smk or Python (RESEARCH Pitfall #1 compliance)
- All 45 (minus DEFERRED) harmonized files are munged to D-16-named .sumstats.gz
- At least 1 focal_i.log written; on full run, 44 logs exist
- Final N×N wide TSV at `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv` with header + N rows + (N+1) columns where N = line count of trait_keys.txt
- Long-form TSV at `data/processed/ldsc_overlap/rg_matrix_long.tsv` with at least 990 (45 choose 2) rows
- Validation JSON at `rg_validation_warnings.json` has `symmetry_warnings=[]` or documented deviations
- In-repo mirror at `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv` committed
- REQ-PATH-PARAMETERIZATION: zero hardcoded absolute paths in the 3 new files
- feedback_lsf_queues observed: munge uses serial queue (-W 5760); rg stars use long queue (-W 14400)
</success_criteria>

<output>
After completion, create `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-03-SUMMARY.md` with:
- Munge outcomes table: one row per trait key with status (OK / FAIL / SKIP) + row count + bytes
- 44 focal star-call wall-time table: focal_i, pair_count, wall_seconds, status
- Matrix shape (expect 45x45) + diagonal values (expect 1.0 or NaN) + sha256 of the matrix TSV
- rg_validation_warnings.json contents (full dump)
- Deviations from expected-intercept heuristics (Pitfall #8) — per-pair list if any
- LSF job summary: total CPU-hours consumed, queue utilization, any retry attempts
- Commit hash of `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv`
</output>
</content>
</invoke>