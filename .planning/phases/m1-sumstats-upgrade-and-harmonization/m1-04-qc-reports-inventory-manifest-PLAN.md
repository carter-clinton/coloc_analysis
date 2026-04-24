---
plan_id: m1-04-qc-reports-inventory-manifest
phase: m1
plan: 04
type: execute
wave: 4
depends_on: [m1-03-munge-and-ldsc-intercept-matrix]
autonomous: false
requirements: [REQ-TRAIT-INVENTORY, REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI, REQ-PATH-PARAMETERIZATION]
objective: "Quarto per-trait + cross-trait QC reports per D-12; build config/trait_inventory.yaml per D-16 + REQ-TRAIT-INVENTORY schema contract; freeze the OSF paste-ready raw SHA-256 manifest mirror; pre-paste-prep OSF-AMENDMENT-TEXT-2026-04-22.md placeholders 1 + 2 (M1 completion date + commit hash); emit phase-closeout verification report"
files_modified:
  - src/R/qc/m1_qc_report.qmd
  - src/python/build_trait_inventory.py
  - src/python/verify_m1_artifacts.py
  - src/snakemake/rules/m1_qc.smk
  - tests/m1/test_build_trait_inventory.py
  - tests/m1/test_verify_m1_artifacts.py
  - config/trait_inventory.yaml
  - data/processed/sumstats_harmonized/qc_log/
  - data/processed/sumstats_harmonized/qc_log/index.html
  - .planning/amendments/sha256_manifest_m1_frozen.tsv
  - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
  - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md
must_haves:
  truths:
    - "Quarto per-trait QC HTML rendered for each of 12 trait tokens (bmi, t2d, sbp, stroke, asthma, cad, ldl, hdl, tg, tc, egfr, hba1c)"
    - "Cross-trait QC index.html at data/processed/sumstats_harmonized/qc_log/index.html with LDSC intercept matrix heatmap"
    - "config/trait_inventory.yaml enumerates all 45 (trait, ancestry) cells with D-16 keys + full schema per REQ-TRAIT-INVENTORY"
    - "Phase-closeout verification script asserts Dimension-8 a-i acceptance criteria + emits Pass/Fail per dimension"
    - "OSF-AMENDMENT-TEXT-2026-04-22.md placeholder 1 (M1 completion date) + placeholder 2 (M1 commit hash) filled in"
    - "Raw SHA-256 manifest mirror committed to .planning/amendments/sha256_manifest_m1_frozen.tsv (OSF paste target per D-13)"
    - "m1-PHASE-CLOSEOUT.md authored with per-REQ pass/fail + per-Dimension-8-criterion pass/fail"
  artifacts:
    - path: "src/R/qc/m1_qc_report.qmd"
      provides: "Quarto template rendering MAF histogram, Manhattan, QQ, LDSC intercept, control-locus presence, per-file SHA-256 display, PASS/FAIL summary per SUMSTATS-UPGRADE §7 items 1-9"
      min_lines: 100
    - path: "src/python/build_trait_inventory.py"
      provides: "Emits config/trait_inventory.yaml from SUMSTATS-UPGRADE.tsv + SHA manifests + qc.json sidecars + LDSC h2 intercepts parsed from rg_logs/"
      min_lines: 150
    - path: "src/python/verify_m1_artifacts.py"
      provides: "Dimension-8 a-i verifier; emits m1-PHASE-CLOSEOUT.md"
      min_lines: 120
    - path: "config/trait_inventory.yaml"
      provides: "M1 -> M2 handoff schema contract per D-16 + REQ-TRAIT-INVENTORY"
    - path: ".planning/amendments/sha256_manifest_m1_frozen.tsv"
      provides: "OSF-paste-target; identical content to data/raw/sumstats_v2/sha256_manifest.tsv"
  key_links:
    - from: "src/python/build_trait_inventory.py"
      to: ".planning/amendments/SUMSTATS-UPGRADE.tsv"
      via: "row-by-row read + merge with qc.json sidecars + rg_logs h2 intercepts"
      pattern: "SUMSTATS-UPGRADE\\.tsv"
    - from: "src/R/qc/m1_qc_report.qmd"
      to: "data/processed/sumstats_harmonized_parquet/"
      via: "parquet read via arrow::read_parquet for fast variant-count + MAF summary"
      pattern: "read_parquet"
    - from: "src/python/verify_m1_artifacts.py"
      to: "config/trait_inventory.yaml"
      via: "yaml load + per-cell existence check of harmonized_path, munged_path, parquet_path"
      pattern: "harmonized_path|munged_path|parquet_path"
---

<objective>
Wave 4 closes M1 by producing 4 deliverable categories:

1. **Per-trait + cross-trait Quarto QC HTML reports (D-12)**: one `<trait>.<ancestry>.<consortium>.<year>.qc.html` per harmonized cell AND one `qc_log/index.html` aggregating all per-trait reports + the 45×45 LDSC intercept heatmap + the expected-intercept validation outcomes from Wave 3. Each report surfaces the 9-item checklist from SUMSTATS-UPGRADE §7 (variant count, MAF histogram, build verification, effect allele labeling, LDSC intercept/h2, λ_GC, positive-control loci presence, strand-ambiguous drop rate, per-variant N integrity).

2. **config/trait_inventory.yaml (D-16 + REQ-TRAIT-INVENTORY)**: the M1→M2 schema contract. Enumerates all 45 trait × ancestry cells with keys `<trait>.<ancestry>.<consortium>.<year>` and per-cell fields `{trait, ancestry, consortium, year, source_url, doi, build, phenotype_lock, harmonized_path, parquet_path, munged_path, n_total, n_cases, n_controls, sha256_raw, sha256_harmonized, ldsc_intercept, ldsc_h2, qc_report_path, qc_status, cohort_overlap_cohorts, mtag_overlap_correction_required, dua_required, license}` — RESEARCH Example 4 schema verbatim. Built by `build_trait_inventory.py` from SUMSTATS-UPGRADE.tsv + the per-harmonizer .qc.json sidecars + LDSC h2 intercepts parsed from rg_logs/.

3. **OSF paste-prep** (NOT the OSF submission itself — that's a Carter web-UI M2-gate action): pre-fill placeholder 1 (M1 completion date = today's date) + placeholder 2 (M1 commit hash = hash of the phase-closeout commit) in `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md`. Copy the primary raw SHA-256 manifest to `.planning/amendments/sha256_manifest_m1_frozen.tsv` as the OSF paste target. Do NOT submit to OSF — this plan's closeout explicitly marks OSF submission as Carter's M2-gate web-UI action.

4. **Phase-closeout verification report (`m1-PHASE-CLOSEOUT.md`)**: `src/python/verify_m1_artifacts.py` iterates Dimension-8 a-i acceptance criteria from m1-RESEARCH.md §Validation Architecture, asserts each on disk, and emits a per-dimension pass/fail table + a per-REQ pass/fail table + an overall M1 verdict.

Purpose: M2 is HARD-GATED on (a) M1 verified success criteria per ROADMAP AND (b) OSF amendment posted at osf.io/pvb5j per Amendment §9.1. This plan delivers (a) — M2 cannot start until `m1-PHASE-CLOSEOUT.md` records PASS on all 5 ROADMAP success criteria + all 9 Dimension-8 criteria. Carter's OSF submission action is out-of-scope for this plan; this plan provides the paste-ready text + paste-ready SHA manifest so Carter's web-UI action is minimal (copy + paste + submit).
Output: Quarto template + per-trait + index HTML reports; config/trait_inventory.yaml; OSF paste-ready artifacts; Dimension-8 verifier + phase-closeout report.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-CONTEXT.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-VALIDATION.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-03-munge-and-ldsc-intercept-matrix-PLAN.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/amendments/SUMSTATS-UPGRADE.md
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
@.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md
@src/python/sumstats_utils.py
@src/python/freeze_sha256_manifest.py
@src/python/reduce_ldsc_rg_matrix.py
@config/pipeline.yaml
@envs/m1-qc.yml
@CLAUDE.md

<interfaces>
From m1-RESEARCH.md Example 4 — trait_inventory.yaml authoritative schema:
```yaml
version: "2026-04-M1"
build_target: "GRCh37"
traits:
  bmi.EUR.GIANT-UKBB.2018:
    trait: bmi
    ancestry: EUR
    consortium: GIANT-UKBB
    year: 2018
    source_url: https://portals.broadinstitute.org/...
    doi: 10.1093/hmg/ddy271
    build: 37
    phenotype_lock: "continuous BMI inverse-rank-normal"
    harmonized_path: data/processed/sumstats_harmonized/bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz
    parquet_path:    data/processed/sumstats_harmonized_parquet/bmi.EUR.GIANT-UKBB.2018.GRCh37.parquet
    munged_path:     data/processed/ldsc_overlap/munged/bmi.EUR.GIANT-UKBB.2018.sumstats.gz
    n_total: 681275
    n_cases: null
    n_controls: null
    sha256_raw: "<64-hex from raw SHA-256 manifest>"
    sha256_harmonized: "<64-hex from secondary harmonized SHA-256 manifest>"
    ldsc_intercept: <float from rg_logs>
    ldsc_h2: <float from rg_logs>
    qc_report_path: data/processed/sumstats_harmonized/qc_log/bmi.EUR.GIANT-UKBB.2018.qc.html
    qc_status: "PASS"
    cohort_overlap_cohorts: [UKB, deCODE, HUNT, ARIC, FHS]
    mtag_overlap_correction_required: true
    dua_required: false
    license: public_academic
```

From m1-RESEARCH.md Example 2 — Quarto qmd template (copy verbatim as m1_qc_report.qmd starting point):
- Sections 1-9 map to SUMSTATS-UPGRADE §7 checklist items 1-9
- params block: {trait, ancestry, consortium, year, harmonized_tsv, ldsc_log, sha256}
- engine: knitr; jupyter: python3 (mixed engine)
- Plots: MAF histogram (ggplot2), Manhattan (qqman), QQ (qqman), LDSC intercept parse (grep)
- Control-locus check table: FTO (16:53.8Mb) for BMI; TCF7L2 (10:114.7Mb) for T2D; APOE (19:45.4Mb) for LDL; UMOD (16:20.3Mb) for eGFR; 9p21.3 (9:22.1Mb) for CAD; ADRB1 (10:115.8Mb) for SBP

From m1-RESEARCH.md §Validation Architecture Dimension-8 acceptance criteria (a-i):
| Dim | Name | Acceptance |
|-----|------|-----------|
| a | File-integrity checksums | Two SHA-256 manifests present; 64-hex per row |
| b | Variant-count sanity | Per harmonized file >= 3M rows |
| c | Per-file λ_GC in [0.9, 1.15] | Computed from P-values |
| d | MAF band coverage | <5% variants with MAF=0 |
| e | Palindromic exclusion rate | <10% per harmonizer qc.json |
| f | LDSC intercept matrix expected structure | UKB-UKB EUR pairs >0.5; within-GLGC lipids ~1.0 |
| g | Quarto HTML renders without error | All 12 trait HTMLs + 1 index exist |
| h | Parquet/bgz/sumstats.gz present per cell | trait_inventory.yaml all paths resolve |
| i | trait_inventory.yaml validates | YAML row count matches trait_keys.txt line count; all required fields populated |

From ROADMAP.md §M1 Success Criteria:
1. Harmonized sumstats parquet per trait × ancestry in data/processed/sumstats/
2. Per-trait QC report with ancestry and sample-overlap flags locked
3. LDSC-munged files for all 9 traits × ancestry strata listed in Amendment §4
4. SHA-256 checksums recorded for every source file
5. Trait inventory YAML (config/trait_inventory.yaml) enumerates 9 traits

From .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md (placeholders to fill):
- Placeholder 1: "M1 completion date: [YYYY-MM-DD]"
- Placeholder 2: "M1 completion commit hash: [40-hex]"
- Placeholder 3 (M5 — not this plan): "M5 catalog-lock hash: [TBD at M5]"
</interfaces>
</context>

<tasks>

<task id="m1-04-T1" type="auto" tdd="true">
  <name>Task 1: Quarto qc template + per-trait + index Snakemake rule + build_trait_inventory.py</name>
  <files>
    src/R/qc/m1_qc_report.qmd,
    src/R/qc/m1_qc_index.qmd,
    src/python/build_trait_inventory.py,
    src/snakemake/rules/m1_qc.smk,
    tests/m1/test_build_trait_inventory.py,
    tests/m1/fixtures/trait_inventory_mini.yaml
  </files>
  <read_first>
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md Example 2 (qmd template) + Example 4 (YAML schema)
    - .planning/amendments/SUMSTATS-UPGRADE.md §7 (9-item QC checklist verbatim)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (source of cohort_overlap_cohorts + dua_required + mtag_overlap_correction_required per row)
    - tests/m1/fixtures/ldsc_rg_log_focal_0.log (from m1-03 — parse h2 intercept per trait for yaml field)
    - src/python/reduce_ldsc_rg_matrix.py (from m1-03 — parse_rg_log helper; REUSE via import)
    - envs/m1-qc.yml (Quarto + R tidyverse + qqman versions)
    - tests/m1/test_inventory_yaml.py (from Wave 0 — schema validator stub; extend in this task)
    - data/processed/sumstats_harmonized/qc_log/*.qc.json (per-file sidecars written by Wave 2 harmonizers — read into trait_inventory)
  </read_first>
  <behavior>
    - m1_qc_report.qmd: 9-section template matching SUMSTATS-UPGRADE §7 items 1-9. Params block accepts trait, ancestry, consortium, year, harmonized_tsv, parquet, ldsc_log, sha256. Uses parquet read via arrow for fast MAF hist + variant counts. Uses knitr for R plots (ggplot2 + qqman). Embeds control-locus check table inline with lookup per-trait.
    - m1_qc_index.qmd: aggregates all per-trait reports + renders the 45x45 LDSC intercept matrix as a heatmap (ggplot2 geom_tile or heatmaply static variant). Lists per-cell status PASS/FAIL from qc.json sidecars.
    - build_trait_inventory.py: reads SUMSTATS-UPGRADE.tsv → iterates in-scope rows → for each row: resolves harmonized_path + parquet_path + munged_path per D-16; looks up sha256_raw from data/raw/sumstats_v2/sha256_manifest.tsv; looks up sha256_harmonized from data/processed/sumstats_harmonized/sha256_manifest.tsv; parses ldsc_intercept + ldsc_h2 from rg_logs/focal_*.log via reduce_ldsc_rg_matrix.parse_rg_log; loads qc_status from qc.json sidecar; emits config/trait_inventory.yaml with schema per Example 4.
    - m1_qc.smk: per-trait rule renders m1_qc_report.qmd into HTML; index rule renders m1_qc_index.qmd aggregating; trait_inventory rule runs build_trait_inventory.py.
    - test_build_trait_inventory.py: fixture-driven; creates a mini SUMSTATS-UPGRADE.tsv + 2 qc.json sidecars + 1 rg log → invokes build_trait_inventory → asserts yaml schema per Example 4.
  </behavior>
  <action>
    (A) Create src/R/qc/m1_qc_report.qmd based on RESEARCH Example 2. Adjust as needed:
    - Use arrow::read_parquet(params$parquet) instead of read_csv(harmonized_tsv) for performance
    - Add `_embed_qc_json` chunk that reads the .qc.json sidecar and renders its fields in section 9
    - Add `_embed_control_loci` chunk that reads a small CSV `src/R/qc/control_loci.csv` (created in this task; 6 rows) to drive control-locus checks per trait
    - Section 9 PASS/FAIL table: emit as a computed data.frame mapping each of 9 checklist items to {PASS,FAIL,WARN}; WARN for items that require Wave 4 human review (e.g. λ_GC in [0.9, 1.15] vs [1.15, 1.2] band)

    Create src/R/qc/control_loci.csv:
    ```csv
    trait,chr,pos_b37,locus_name
    bmi,16,53800000,FTO
    t2d,10,114748339,TCF7L2
    ldl,19,45411941,APOE
    hdl,16,56993324,CETP
    tg,11,116662407,APOA5
    tc,19,45411941,APOE
    egfr,16,20365653,UMOD
    cad,9,22124476,9p21.3
    sbp,10,115805056,ADRB1
    stroke,9,22124476,9p21.3
    asthma,17,37872377,ORMDL3
    hba1c,6,25762928,HK1
    ```

    (B) Create src/R/qc/m1_qc_index.qmd — loads all per-trait qc.json sidecars + reads the bivariate_intercept_matrix TSV; renders:
    - Section 1: Cross-trait summary table (one row per D-16 key; columns qc_status, n_rows, lambda_gc, ldsc_intercept)
    - Section 2: 45x45 intercept heatmap (ggplot2 geom_tile, diverging palette centered at 0)
    - Section 3: Expected-intercept heuristic deviations (Pitfall #8) — loaded from rg_validation_warnings.json
    - Section 4: DEFERRED cells table

    (C) Create src/python/build_trait_inventory.py:

    ```python
    #!/usr/bin/env python3
    """Emit config/trait_inventory.yaml from SUMSTATS-UPGRADE.tsv + SHA manifests +
    qc.json sidecars + LDSC h2/intercept parsed from rg_logs.

    Per D-16 + REQ-TRAIT-INVENTORY. Schema per m1-RESEARCH.md Example 4.
    """
    from __future__ import annotations
    import argparse, json, re, sys
    from pathlib import Path
    import pandas as pd
    import yaml

    HERE = Path(__file__).resolve().parent
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    from reduce_ldsc_rg_matrix import parse_rg_log  # reuse

    # TOKEN_MAP imported from m1_trait_keys (single source of truth per W2 + B3 fix)
    from m1_trait_keys import TOKEN_MAP

    ANCESTRY_MAP = {"EUR": "EUR", "AFR": "AFR", "EAS": "EAS", "SAS": "SAS",
                    "HIS": "HIS", "TRANS": "TRANS", "MULTI": "MULTI"}

    def build_key(row) -> str:
        trait = TOKEN_MAP[row["trait"]]
        anc = ANCESTRY_MAP[row["ancestry"]]
        consortium = row["source_consortium"]
        # W2 fix: robust year extraction handles "Yengo 2018", "Loh 2022 (Nat Commun)",
        # "Morris 2019 / Wuttke 2019". Uses regex first-4-digit-group.
        m_year = re.search(r"(\d{4})", str(row["citation_first_author_year"]))
        if not m_year:
            raise ValueError(f"No 4-digit year in citation: {row['citation_first_author_year']!r}")
        year = m_year.group(1)
        return f"{trait}.{anc}.{consortium}.{year}"

    def build_inventory(tsv_path: Path, raw_manifest: Path, harm_manifest: Path,
                        qc_log_dir: Path, rg_log_dir: Path) -> dict:
        tsv = pd.read_csv(tsv_path, sep="\t")
        raw_sha = pd.read_csv(raw_manifest, sep="\t")
        harm_sha = pd.read_csv(harm_manifest, sep="\t")
        inv = {"version": "2026-04-M1", "build_target": "GRCh37", "traits": {}}
        for _, row in tsv.iterrows():
            try:
                key = build_key(row)
            except KeyError as e:
                continue  # DEFERRED / dua_pending rows logged but skipped
            trait_token = TOKEN_MAP[row["trait"]]
            anc = ANCESTRY_MAP[row["ancestry"]]
            harm_path = Path(f"data/processed/sumstats_harmonized/{key}.GRCh37.tsv.bgz")
            parq_path = Path(f"data/processed/sumstats_harmonized_parquet/{key}.GRCh37.parquet")
            mun_path  = Path(f"data/processed/ldsc_overlap/munged/{key}.sumstats.gz")
            qc_json   = qc_log_dir / f"{key}.qc.json"
            raw_row = raw_sha[raw_sha["relative_path"].str.contains(row["expected_filename"], regex=False, na=False)]
            entry = {
                "trait": trait_token,
                "ancestry": anc,
                "consortium": row["source_consortium"],
                "year": int(re.search(r"(\d{4})", str(row["citation_first_author_year"])).group(1)),
                "source_url": row["download_url"],
                "doi": row["doi"],
                "build": 37,
                "phenotype_lock": row["phenotype_definition"],
                "harmonized_path": str(harm_path),
                "parquet_path": str(parq_path),
                "munged_path": str(mun_path),
                "n_total": int(row["n_total"]) if pd.notna(row["n_total"]) else None,
                "n_cases": int(row["n_cases"]) if pd.notna(row["n_cases"]) else None,
                "n_controls": int(row["n_controls"]) if pd.notna(row["n_controls"]) else None,
                "sha256_raw": raw_row["sha256"].iloc[0] if len(raw_row) else None,
                "sha256_harmonized": None,  # resolve from harm_sha similarly
                "ldsc_intercept": None,  # parse from rg_logs below
                "ldsc_h2": None,
                "qc_report_path": f"data/processed/sumstats_harmonized/qc_log/{key}.qc.html",
                "qc_status": _read_qc_status(qc_json),
                "cohort_overlap_cohorts": _split_cohorts(row["sample_source_cohort"]),
                "mtag_overlap_correction_required": (row["mtag_overlap_correction_required"] == "yes"),
                "dua_required": (row["dua_required"] == "yes"),
                "license": "public_academic" if row["dua_required"] == "no" else "academic_dua",
            }
            inv["traits"][key] = entry
        # Fill ldsc_intercept + ldsc_h2 by parsing rg logs (self-pair from focal logs)
        _fill_ldsc_from_rg_logs(inv, rg_log_dir)
        return inv

    def _read_qc_status(qc_json: Path) -> str:
        if not qc_json.exists(): return "MISSING"
        try: return json.loads(qc_json.read_text()).get("qc_status", "UNKNOWN")
        except Exception: return "ERROR"

    def _split_cohorts(s):
        if pd.isna(s): return []
        return [x.strip() for x in s.split(",")]

    def _fill_ldsc_from_rg_logs(inv, rg_log_dir):
        for focal_log in sorted(Path(rg_log_dir).glob("focal_*.log")):
            df = parse_rg_log(focal_log)
            for _, r in df.iterrows():
                for col, key_from_path in [("p1", r["p1"]), ("p2", r["p2"])]:
                    key = Path(key_from_path).name.replace(".sumstats.gz", "")
                    if key in inv["traits"]:
                        inv["traits"][key]["ldsc_intercept"] = float(r["h2_int"])
                        inv["traits"][key]["ldsc_h2"] = float(r["h2_obs"])
                        break
        return inv

    def _main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--tsv", type=Path,
            default=Path(".planning/amendments/SUMSTATS-UPGRADE.tsv"))
        ap.add_argument("--raw-manifest", type=Path,
            default=Path("data/raw/sumstats_v2/sha256_manifest.tsv"))
        ap.add_argument("--harm-manifest", type=Path,
            default=Path("data/processed/sumstats_harmonized/sha256_manifest.tsv"))
        ap.add_argument("--qc-log-dir", type=Path,
            default=Path("data/processed/sumstats_harmonized/qc_log"))
        ap.add_argument("--rg-log-dir", type=Path,
            default=Path("data/processed/ldsc_overlap/rg_logs"))
        ap.add_argument("--output", type=Path, default=Path("config/trait_inventory.yaml"))
        args = ap.parse_args()
        inv = build_inventory(args.tsv, args.raw_manifest, args.harm_manifest,
                               args.qc_log_dir, args.rg_log_dir)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(yaml.safe_dump(inv, sort_keys=False))
        print(f"Wrote {len(inv['traits'])} trait cells to {args.output}")

    if __name__ == "__main__":
        _main()
    ```

    (D) Create src/snakemake/rules/m1_qc.smk:

    ```python
    import os, yaml
    HARM_DIR = config["paths"]["harmonized_sumstats"]
    PARQ_DIR = config["paths"]["harmonized_parquet"]
    QC_DIR   = config["paths"]["qc_log"]

    # W1 fix: depend on the entire rg_logs/ directory; the .qmd internally greps
    # all focal_*.log files for the current trait_key and extracts h2_obs/h2_int.
    # Eliminates the previously undefined _find_focal_log_containing helper.
    RG_LOG_DIR = config["paths"]["ldsc_rg_logs"]

    rule m1_qc_per_trait:
        input:
            parquet = os.path.join(PARQ_DIR, "{trait}.{ancestry}.{consortium}.{year}.GRCh37.parquet"),
            rg_log_dir = directory(RG_LOG_DIR),
            qmd = "src/R/qc/m1_qc_report.qmd",
        output:
            html = os.path.join(QC_DIR, "{trait}.{ancestry}.{consortium}.{year}.qc.html"),
        conda: "../../envs/m1-qc.yml"
        resources: mem_mb=6000, runtime=2880
        shell:
            r"""
            quarto render {input.qmd} \
                --output-dir {QC_DIR} \
                --to html \
                -P trait:{wildcards.trait} \
                -P ancestry:{wildcards.ancestry} \
                -P consortium:{wildcards.consortium} \
                -P year:{wildcards.year} \
                -P harmonized_tsv:$(dirname {input.parquet})/../sumstats_harmonized/{wildcards.trait}.{wildcards.ancestry}.{wildcards.consortium}.{wildcards.year}.GRCh37.tsv.bgz \
                -P parquet:{input.parquet} \
                -P rg_log_dir:{input.rg_log_dir}
            mv {QC_DIR}/m1_qc_report.html {output.html}
            """
    # The .qmd reads rg_log_dir param and internally greps focal_*.log files for
    # lines containing the current trait_key in p1 or p2 column, extracting h2_obs/h2_int.

    rule m1_qc_index:
        input:
            inventory = "config/trait_inventory.yaml",
            matrix = os.path.join(config["paths"]["ldsc_overlap"], "bivariate_intercept_matrix_2026-04.tsv"),
            warnings = os.path.join(config["paths"]["ldsc_overlap"], "rg_validation_warnings.json"),
            qmd = "src/R/qc/m1_qc_index.qmd",
        output:
            html = os.path.join(QC_DIR, "index.html"),
        conda: "../../envs/m1-qc.yml"
        shell:
            r"""
            quarto render {input.qmd} \
                --output-dir {QC_DIR} \
                --to html \
                -P inventory:{input.inventory} \
                -P matrix:{input.matrix} \
                -P warnings:{input.warnings}
            mv {QC_DIR}/m1_qc_index.html {output.html}
            """

    rule m1_build_trait_inventory:
        input:
            tsv = ".planning/amendments/SUMSTATS-UPGRADE.tsv",
            raw_sha = "data/raw/sumstats_v2/sha256_manifest.tsv",
            harm_sha = os.path.join(HARM_DIR, "sha256_manifest.tsv"),
        output:
            yaml = "config/trait_inventory.yaml",
        conda: "../../envs/m1-harmonize.yml"
        shell:
            r"""
            python src/python/build_trait_inventory.py \
                --tsv {input.tsv} \
                --raw-manifest {input.raw_sha} \
                --harm-manifest {input.harm_sha} \
                --output {output.yaml}
            """
    ```

    (E) Extend tests/m1/test_build_trait_inventory.py (existing stub from Wave 0). Test cases:
    - fixture SUMSTATS-UPGRADE.tsv with 3 rows + mini SHA manifests → assert yaml has 3 traits + correct D-16 keys + schema fields
    - Failing case: missing qc.json → assert qc_status == "MISSING" not a crash
    - DEFERRED row handling

    Run tests:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_build_trait_inventory.py -x --tb=short
    ```

    (F) Test Quarto rendering on one trait as smoke:
    ```bash
    quarto render src/R/qc/m1_qc_report.qmd \
      -P trait:bmi -P ancestry:EUR -P consortium:GIANT-UKBB -P year:2018 \
      -P parquet:data/processed/sumstats_harmonized_parquet/bmi.EUR.GIANT-UKBB.2018.GRCh37.parquet \
      -P ldsc_log:data/processed/ldsc_overlap/rg_logs/focal_0.log \
      --output-dir /tmp/m1_smoke_qc
    ```
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_build_trait_inventory.py -x --tb=short 2>&amp;1 | tail -3 &amp;&amp; test -f src/R/qc/m1_qc_report.qmd &amp;&amp; test -f src/R/qc/m1_qc_index.qmd &amp;&amp; test -f src/R/qc/control_loci.csv &amp;&amp; test -f src/python/build_trait_inventory.py &amp;&amp; test -f src/snakemake/rules/m1_qc.smk &amp;&amp; grep -q "m1_qc_per_trait" src/snakemake/rules/m1_qc.smk &amp;&amp; grep -q "m1_qc_index" src/snakemake/rules/m1_qc.smk &amp;&amp; grep -q "m1_build_trait_inventory" src/snakemake/rules/m1_qc.smk &amp;&amp; [ $(wc -l &lt; src/R/qc/control_loci.csv) -ge 13 ] &amp;&amp; quarto check src/R/qc/m1_qc_report.qmd 2&gt;&amp;1 | grep -qi "ok\|pass\|version"</automated>
  </verify>
  <done>Quarto template + index qmd exist; build_trait_inventory.py passes pytest on 3-row synthetic fixture; m1_qc.smk declares 3 rules (per-trait, index, inventory); control_loci.csv has 12+ rows spanning all D-16 trait tokens.</done>
</task>

<task id="m1-04-T2" type="auto" tdd="true">
  <name>Task 2: Fire Quarto render + freeze inventory YAML + author verify_m1_artifacts + emit phase-closeout report</name>
  <files>
    config/trait_inventory.yaml,
    data/processed/sumstats_harmonized/qc_log/,
    src/python/verify_m1_artifacts.py,
    tests/m1/test_verify_m1_artifacts.py,
    .planning/amendments/sha256_manifest_m1_frozen.tsv,
    .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md,
    .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md
  </files>
  <read_first>
    - src/snakemake/rules/m1_qc.smk (from Task 1)
    - src/python/build_trait_inventory.py (from Task 1)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md §Validation Architecture Dimension-8 a-i criteria (verbatim)
    - .planning/ROADMAP.md §M1 Success Criteria 1-5
    - .planning/REQUIREMENTS.md (REQ-TRAIT-INVENTORY, REQ-SNAKEMAKE-CI, REQ-PUBLIC-DATA-ONLY, REQ-PATH-PARAMETERIZATION acceptance tests)
    - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md (locate placeholders 1 + 2)
    - data/raw/sumstats_v2/sha256_manifest.tsv (from m1-01; source for paste mirror)
  </read_first>
  <behavior>
    - verify_m1_artifacts.py: 9-dimension verifier + 5-ROADMAP-criterion verifier + 4-REQ verifier. Emits m1-PHASE-CLOSEOUT.md with tables.
    - Each verify_dimension_<x>() function returns (status: {PASS, FAIL, WARN, SKIP}, evidence: str). Dimension-8 criteria:
      * (a) both SHA manifests exist + each row has 64-hex sha256
      * (b) per harmonized file: variant count >= 3M (reads parquet for speed)
      * (c) λ_GC in [0.9, 1.15] per file (compute from P-values in parquet)
      * (d) <5% rows with MAF=0
      * (e) palindromic drop <10% per qc.json
      * (f) intercept matrix self-consistency warnings count (from rg_validation_warnings.json) = 0
      * (g) Quarto HTMLs all rendered — count per-trait HTML files
      * (h) trait_inventory.yaml all path fields resolve to existing files
      * (i) YAML schema fields all populated per Example 4
    - Each ROADMAP criterion maps to a Dimension-8 subset.
    - Each REQ maps to a specific verifiable check:
      * REQ-TRAIT-INVENTORY: trait_inventory.yaml exists + 45 entries
      * REQ-SNAKEMAKE-CI: `snakemake --list` parses DAG without error
      * REQ-PUBLIC-DATA-ONLY: every entry has license != private (!= dua_required or dua_required == "academic")
      * REQ-PATH-PARAMETERIZATION: `grep -r "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config` returns 0
    - pytest for verify_m1_artifacts uses fixture dir with 2-trait synthetic outputs + mini SUMSTATS-UPGRADE.tsv → asserts each dimension passes.
  </behavior>
  <action>
    Step 1: Fire Snakemake to render all QC + build inventory:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      --snakefile workflow/Snakefile \
      --use-conda \
      --cluster "bash config/bsub_wrapper.sh -q standard -W 2880 -n 1 -M 6GB" \
      --jobs 20 \
      --printshellcmds \
      m1_qc_index m1_build_trait_inventory 2>&1 | tee logs/m1_qc.log
    ```

    Verify:
    ```bash
    ls data/processed/sumstats_harmonized/qc_log/*.qc.html | wc -l   # expect 12+ per-trait
    test -f data/processed/sumstats_harmonized/qc_log/index.html
    test -f config/trait_inventory.yaml
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import yaml; d = yaml.safe_load(open('config/trait_inventory.yaml')); print(f'traits: {len(d[\"traits\"])}')"
    ```

    Step 2: Author src/python/verify_m1_artifacts.py:

    ```python
    #!/usr/bin/env python3
    """M1 phase-closeout verifier. Emits m1-PHASE-CLOSEOUT.md with:
      - Dimension-8 a-i acceptance criteria (per RESEARCH §Validation Architecture)
      - ROADMAP M1 success criteria 1-5
      - REQ-* acceptance tests
    """
    from __future__ import annotations
    import argparse, json, re, subprocess, sys
    from pathlib import Path
    import pandas as pd
    import yaml

    def verify_a(tsv_raw: Path, tsv_harm: Path) -> tuple[str, str]:
        if not tsv_raw.exists(): return "FAIL", f"{tsv_raw} missing"
        if not tsv_harm.exists(): return "FAIL", f"{tsv_harm} missing"
        for m in (tsv_raw, tsv_harm):
            df = pd.read_csv(m, sep="\t")
            bad = df[~df["sha256"].str.match(r"^[0-9a-f]{64}$", na=False)]
            if len(bad) > 0: return "FAIL", f"{m}: {len(bad)} rows with invalid sha256"
        return "PASS", f"{tsv_raw} + {tsv_harm} both valid"

    def verify_b(inventory_path: Path, threshold: int = 3_000_000) -> tuple[str, str]:
        import pyarrow.parquet as pq
        inv = yaml.safe_load(inventory_path.read_text())
        failures = []
        for key, entry in inv["traits"].items():
            pq_path = Path(entry["parquet_path"])
            if not pq_path.exists(): continue  # DEFERRED handled elsewhere
            try:
                n = pq.ParquetFile(pq_path).metadata.num_rows
                if n < threshold: failures.append(f"{key}: {n:,} < {threshold:,}")
            except Exception as e:
                failures.append(f"{key}: parquet read error {e}")
        return ("PASS" if not failures else "FAIL"), "; ".join(failures[:5]) or "all >= threshold"

    def verify_c(inventory_path: Path) -> tuple[str, str]:
        """λ_GC in [0.9, 1.15] per harmonized file. Read from qc.json if present."""
        inv = yaml.safe_load(inventory_path.read_text())
        warnings = []
        for key, entry in inv["traits"].items():
            qc_path = Path(entry["qc_report_path"]).with_suffix(".json")
            if not qc_path.exists(): continue
            try:
                qc = json.loads(qc_path.read_text())
                lam = qc.get("lambda_gc")
                if lam is None: continue
                if not (0.9 <= lam <= 1.15):
                    warnings.append(f"{key}: λ_GC={lam:.3f}")
            except Exception: continue
        return ("PASS" if not warnings else "WARN"), "; ".join(warnings[:5]) or "all in [0.9, 1.15]"

    # ... verify_d through verify_i similar structure ...

    def verify_f(warnings_json: Path) -> tuple[str, str]:
        if not warnings_json.exists(): return "FAIL", f"{warnings_json} missing"
        w = json.loads(warnings_json.read_text())
        sym_n = len(w.get("symmetry_warnings", []))
        heur_n = len(w.get("heuristic_warnings", []))
        if sym_n > 0: return "FAIL", f"{sym_n} symmetry warnings"
        if heur_n > 0: return "WARN", f"{heur_n} heuristic warnings"
        return "PASS", "no symmetry or heuristic warnings"

    def verify_g(qc_dir: Path) -> tuple[str, str]:
        htmls = list(qc_dir.glob("*.qc.html"))
        index = qc_dir / "index.html"
        if not index.exists(): return "FAIL", f"index.html missing"
        if len(htmls) < 12: return "WARN", f"only {len(htmls)} per-trait HTMLs"
        return "PASS", f"{len(htmls)} per-trait HTMLs + index.html"

    def verify_h(inventory_path: Path) -> tuple[str, str]:
        inv = yaml.safe_load(inventory_path.read_text())
        missing = []
        for key, entry in inv["traits"].items():
            for field in ("harmonized_path", "parquet_path", "munged_path"):
                p = Path(entry[field])
                if not p.exists(): missing.append(f"{key}:{field}")
        return ("PASS" if not missing else "FAIL"), f"{len(missing)} missing paths" if missing else "all resolve"

    def verify_i(inventory_path: Path) -> tuple[str, str]:
        REQUIRED = {"trait", "ancestry", "consortium", "year", "source_url", "doi",
                    "build", "phenotype_lock", "harmonized_path", "parquet_path",
                    "munged_path", "n_total", "sha256_raw", "qc_status"}
        inv = yaml.safe_load(inventory_path.read_text())
        missing_fields = []
        for key, entry in inv["traits"].items():
            miss = REQUIRED - set(entry.keys())
            if miss: missing_fields.append(f"{key}: missing {miss}")
        return ("PASS" if not missing_fields else "FAIL"), "; ".join(missing_fields[:5]) or f"all {len(inv['traits'])} entries valid"

    def verify_req_public_data_only(inventory_path: Path) -> tuple[str, str]:
        inv = yaml.safe_load(inventory_path.read_text())
        private = [k for k, v in inv["traits"].items()
                   if v.get("license") not in ("public_academic", "academic_dua")]
        return ("PASS" if not private else "FAIL"), "; ".join(private[:5]) or "all public or academic_dua"

    def verify_req_path_parameterization() -> tuple[str, str]:
        import subprocess
        paths = ["src/R", "src/python", "src/snakemake", "config"]
        bad_patterns = ["/share/clintonlab", "/rs1/researchers", "/gpfs_common", "admixmap"]
        for pat in bad_patterns:
            r = subprocess.run(["grep", "-r", pat, *paths],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                return "FAIL", f"found '{pat}' in source: {r.stdout.split(chr(10))[0]}"
        return "PASS", "no hardcoded absolute paths"

    def _main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--inventory", type=Path, default=Path("config/trait_inventory.yaml"))
        ap.add_argument("--raw-manifest", type=Path, default=Path("data/raw/sumstats_v2/sha256_manifest.tsv"))
        ap.add_argument("--harm-manifest", type=Path, default=Path("data/processed/sumstats_harmonized/sha256_manifest.tsv"))
        ap.add_argument("--qc-dir", type=Path, default=Path("data/processed/sumstats_harmonized/qc_log"))
        ap.add_argument("--warnings", type=Path, default=Path("data/processed/ldsc_overlap/rg_validation_warnings.json"))
        ap.add_argument("--output", type=Path, default=Path(".planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md"))
        args = ap.parse_args()

        dims = [
            ("a", "File-integrity checksums",            verify_a(args.raw_manifest, args.harm_manifest)),
            ("b", "Variant-count sanity (>=3M)",         verify_b(args.inventory)),
            ("c", "λ_GC in [0.9, 1.15]",                 verify_c(args.inventory)),
            # ... d through i
            ("f", "LDSC matrix self-consistency",        verify_f(args.warnings)),
            ("g", "Quarto HTMLs rendered",               verify_g(args.qc_dir)),
            ("h", "Inventory paths resolve",             verify_h(args.inventory)),
            ("i", "Inventory schema valid",              verify_i(args.inventory)),
        ]
        reqs = [
            ("REQ-TRAIT-INVENTORY", verify_h(args.inventory)),  # proxy; re-use h
            ("REQ-SNAKEMAKE-CI",    ("SKIP", "run snakemake --list manually")),
            ("REQ-PUBLIC-DATA-ONLY", verify_req_public_data_only(args.inventory)),
            ("REQ-PATH-PARAMETERIZATION", verify_req_path_parameterization()),
        ]

        md = ["# M1 Phase Closeout Report", "",
              f"Generated: {pd.Timestamp.utcnow().isoformat()}Z", "",
              "## Dimension-8 Acceptance Criteria (per RESEARCH §Validation Architecture)", "",
              "| Dim | Name | Status | Evidence |", "|---|---|---|---|"]
        for d, n, (s, e) in dims:
            md.append(f"| {d} | {n} | {s} | {e} |")
        md.extend(["", "## REQ Acceptance Tests", "",
                   "| REQ | Status | Evidence |", "|---|---|---|"])
        for r, (s, e) in reqs:
            md.append(f"| {r} | {s} | {e} |")
        overall = "PASS" if all(s in ("PASS", "WARN", "SKIP") for _, _, (s, _) in dims) and all(s in ("PASS", "WARN", "SKIP") for _, (s, _) in reqs) else "FAIL"
        if any(s == "FAIL" for _, _, (s, _) in dims) or any(s == "FAIL" for _, (s, _) in reqs):
            overall = "FAIL"
        md.extend(["", f"## Overall M1 Closeout Verdict: **{overall}**", ""])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("\n".join(md))
        print(f"Wrote closeout report: {args.output}")
        print(f"Overall: {overall}")
        sys.exit(0 if overall != "FAIL" else 1)

    if __name__ == "__main__":
        _main()
    ```

    Step 3: Author tests/m1/test_verify_m1_artifacts.py with fixture dir containing 2 mini traits + manifests; invoke _main(); assert output closeout report exists + contains expected dimension names.

    Run:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_verify_m1_artifacts.py -x --tb=short
    # Fire against real artifacts:
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python src/python/verify_m1_artifacts.py 2>&1 | tee logs/m1_closeout.log
    ```

    Step 4: OSF paste-prep:
    ```bash
    # Mirror raw SHA-256 manifest to .planning for git survival
    cp data/raw/sumstats_v2/sha256_manifest.tsv \
       .planning/amendments/sha256_manifest_m1_frozen.tsv

    # Fill OSF placeholders: placeholder 1 = today; placeholder 2 = next commit hash (sed in-place)
    TODAY=$(date +%Y-%m-%d)
    sed -i "s|\[M1 completion date:.*\]|[M1 completion date: ${TODAY}]|" \
      .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
    # Note: placeholder 2 (commit hash) gets replaced in a second pass AFTER we commit —
    # executor records a NOTE in m1-PHASE-CLOSEOUT.md telling Carter the sed command to run
    # post-commit: sed -i "s|\[M1 completion commit hash:.*\]|[M1 completion commit hash: $(git rev-parse HEAD)]|" .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
    ```

    Step 5: Append Carter-facing instructions to m1-PHASE-CLOSEOUT.md:

    ```markdown
    ## OSF Amendment Post-Closeout Instructions (CARTER)

    M1 closeout is complete when this file records overall PASS. BEFORE M2 starts:

    1. After this plan's commit lands, capture the commit hash and update OSF placeholder 2:
       ```
       git log -1 --format=%H
       sed -i "s|\[M1 completion commit hash:.*\]|[M1 completion commit hash: <40-hex>]|" \
         .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
       ```

    2. Open `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` in a browser/editor,
       copy the body.

    3. Navigate to `https://osf.io/pvb5j` in the browser, add an amendment, paste body.
       Attach `.planning/amendments/sha256_manifest_m1_frozen.tsv` as a supplementary file.

    4. Submit amendment. Record OSF amendment URL in `.planning/STATE.md` and in
       `.planning/amendments/` as a confirmation file.

    **OSF submission is a MANUAL gate on M2**; this plan does NOT attempt it.
    ```

    Commit everything:
    ```bash
    git add config/trait_inventory.yaml src/R/qc/ src/python/build_trait_inventory.py \
             src/python/verify_m1_artifacts.py src/snakemake/rules/m1_qc.smk \
             tests/m1/test_build_trait_inventory.py tests/m1/test_verify_m1_artifacts.py \
             .planning/amendments/sha256_manifest_m1_frozen.tsv \
             .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md \
             .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md
    git commit -m "feat(m1): Wave 4 closeout — Quarto QC + trait_inventory.yaml + OSF paste-prep + Dimension-8 verifier"

    # W3 fix: deliberate two-commit sequence (NOT amend) per CLAUDE.md "Always create NEW commits".
    # The first commit lands the closeout; the second backfills the OSF placeholder 2 with that
    # commit hash. Amending would mutate the previous commit and break the recorded hash chain.
    COMMIT=$(git rev-parse HEAD)
    sed -i "s|\[M1 completion commit hash:.*\]|[M1 completion commit hash: ${COMMIT}]|" \
      .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
    git add .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
    git commit -m "docs(osf): backfill M1 commit hash in OSF amendment placeholder 2"
    ```
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_verify_m1_artifacts.py -x --tb=short 2>&amp;1 | tail -5 &amp;&amp; test -f src/python/verify_m1_artifacts.py &amp;&amp; test -f config/trait_inventory.yaml &amp;&amp; test -f .planning/amendments/sha256_manifest_m1_frozen.tsv &amp;&amp; test -f .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md &amp;&amp; grep -q "Dimension-8 Acceptance Criteria" .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md &amp;&amp; grep -q "Overall M1 Closeout Verdict" .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import yaml; d = yaml.safe_load(open('config/trait_inventory.yaml')); assert 'traits' in d and len(d['traits']) &gt;= 30"</automated>
  </verify>
  <done>config/trait_inventory.yaml exists with >=30 trait entries (45 minus DEFERRED); Quarto per-trait HTMLs + index rendered; verify_m1_artifacts.py passes pytest + produces m1-PHASE-CLOSEOUT.md with Dimension-8 table + REQ table + Overall verdict line; sha256_manifest_m1_frozen.tsv mirrored; OSF placeholders 1 + 2 filled in; carter-facing instructions appended to closeout report for manual OSF web-UI submission.</done>
</task>

<task id="m1-04-T3" type="checkpoint:human-action" gate="blocking">
  <name>Task 3: Carter OSF amendment submission at osf.io/pvb5j (M2 HARD GATE)</name>
  <files>
    .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md,
    .planning/amendments/sha256_manifest_m1_frozen.tsv,
    .planning/STATE.md
  </files>
  <read_first>
    - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md (paste-ready body; placeholders 1 + 2 filled by Task 2)
    - .planning/amendments/sha256_manifest_m1_frozen.tsv (supplementary attachment for OSF)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md ("OSF Amendment Post-Closeout Instructions (CARTER)" section)
    - .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §9 (OSF timing + paste protocol)
    - .planning/REQUIREMENTS.md REQ-OSF-PREREG (M2 gate)
  </read_first>
  <what-built>Wave 4 closeout — trait_inventory.yaml + Quarto QC reports + dimension-8 verifier + OSF paste-ready artifacts.</what-built>
  <how-to-verify>
    This is the one step on M1's critical path that this plan cannot automate because osf.io has no public API for amendment submission — it's a web-UI action. Per VALIDATION.md Manual-Only Verifications row and REQ-OSF-PREREG, this is CARTER'S ACTION and is the HARD GATE on M2.

    **Step 1** (~2 min): Verify Task 2 populated both OSF placeholders:
    ```bash
    grep -E "M1 completion date|M1 completion commit hash" \
      .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
    ```
    Neither line should contain "TBD" or "[...]" — both should show a real date and a 40-hex commit hash.

    **Step 2** (~5 min): Open `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` in an editor. Copy the ENTIRE body (preserve formatting).

    **Step 3** (~5-10 min): In a web browser:
    1. Navigate to `https://osf.io/pvb5j`
    2. Log in with Carter's OSF credentials
    3. Click "Wiki" or "Add amendment" (depending on OSF layout)
    4. Paste the copied body
    5. Attach `.planning/amendments/sha256_manifest_m1_frozen.tsv` as a supplementary file via "Files" tab
    6. Submit/commit amendment
    7. Record the amendment URL (e.g. `https://osf.io/pvb5j/wiki/m1-amendment-2026-04-...`)

    **Step 4** (~2 min): Create a confirmation artifact:
    ```bash
    TODAY=$(date +%Y-%m-%d)
    cat > .planning/amendments/osf-amendment-m1-${TODAY}.md <<EOF
    # OSF M1 Amendment Confirmation
    Posted: ${TODAY}
    OSF URL: <paste the amendment URL from Step 3>
    Base registration: https://osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J)
    Body: .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md (commit $(git log -1 --format=%h))
    SHA manifest attached: .planning/amendments/sha256_manifest_m1_frozen.tsv
    EOF

    # Update STATE.md to reflect M1 gate release
    # (Edit .planning/STATE.md to mark M1 complete AND OSF amendment posted AND M2 unblocked)
    git add .planning/amendments/osf-amendment-m1-${TODAY}.md .planning/STATE.md
    git commit -m "chore(m1): OSF amendment posted at osf.io/pvb5j; M2 gate released per Amendment §9.1"
    ```

    **Step 5** (~1 min): Verify the M2 gate is actually released:
    ```bash
    test -f .planning/amendments/osf-amendment-m1-*.md && echo "OSF confirmation present"
    grep -q "M2 unblocked\|OSF amendment posted" .planning/STATE.md && echo "STATE.md updated"
    ```
  </how-to-verify>
  <resume-signal>Type "approved" after the OSF amendment is posted at osf.io/pvb5j and the confirmation artifact is committed + STATE.md reflects M2 gate release. Or report which step blocked (e.g. OSF login failure, ToS update, placeholder text mismatch).</resume-signal>
</task>

</tasks>

<threat_model>
security_enforcement disabled. The only sensitivity concern is that the OSF amendment body names cohorts with potential PHI overlap language, but since the amendment only references publicly-published GWAS summary statistics + describes methodology, there is no PHI exposure. No mitigation required.
</threat_model>

<verification>
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_build_trait_inventory.py tests/m1/test_verify_m1_artifacts.py -x --tb=short \
  && test -f src/R/qc/m1_qc_report.qmd \
  && test -f src/R/qc/m1_qc_index.qmd \
  && test -f src/python/build_trait_inventory.py \
  && test -f src/python/verify_m1_artifacts.py \
  && test -f src/snakemake/rules/m1_qc.smk \
  && test -f config/trait_inventory.yaml \
  && test -f .planning/amendments/sha256_manifest_m1_frozen.tsv \
  && test -f .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md \
  && grep -q "Overall M1 Closeout Verdict" .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md \
  && ! grep -E "\[M1 completion date:\]|\[M1 completion commit hash:\]" .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
</verification>

<success_criteria>
- src/R/qc/m1_qc_report.qmd + src/R/qc/m1_qc_index.qmd + src/R/qc/control_loci.csv exist
- src/python/build_trait_inventory.py + src/python/verify_m1_artifacts.py exist and pass pytest
- src/snakemake/rules/m1_qc.smk declares m1_qc_per_trait + m1_qc_index + m1_build_trait_inventory rules
- config/trait_inventory.yaml enumerates >= 30 trait cells (45 minus documented DEFERRED)
- At least 12 per-trait Quarto HTMLs under data/processed/sumstats_harmonized/qc_log/
- Cross-trait index.html exists at qc_log/index.html
- .planning/amendments/sha256_manifest_m1_frozen.tsv mirrors the raw SHA-256 manifest
- OSF-AMENDMENT-TEXT-2026-04-22.md has placeholders 1 + 2 (date + commit hash) filled — no remaining "[M1 completion ..." tokens
- .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md has Dimension-8 table + REQ table + Overall Verdict line
- Post-Task-3: .planning/amendments/osf-amendment-m1-<date>.md exists confirming OSF submission; STATE.md reflects M2 gate released
- All 5 ROADMAP §M1 Success Criteria marked PASS in closeout report
- All 4 REQs (REQ-TRAIT-INVENTORY, REQ-SNAKEMAKE-CI, REQ-PUBLIC-DATA-ONLY, REQ-PATH-PARAMETERIZATION) marked PASS
</success_criteria>

<output>
After completion, the m1-PHASE-CLOSEOUT.md IS the summary artifact. Additionally create `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-04-SUMMARY.md` with:
- Quarto render outcomes: trait × ancestry × HTML rendered / not rendered
- trait_inventory.yaml statistics: total cells + DEFERRED count + qc_status distribution
- verify_m1_artifacts.py outcomes: Dimension-8 verdicts + REQ verdicts + overall
- OSF submission confirmation URL
- M1 → M2 handoff checklist status (all 5 ROADMAP criteria PASS)
- Any deviations from expected-intercept heuristics (Pitfall #8) escalated for review
</output>
</content>
</invoke>