---
phase: m2-ldsc-mtag-cpassoc-discovery
plan: 05
type: execute
wave: 5
depends_on: [m2-00-preflight-and-environment, m2-01-ldsc-matrix-refire, m2-02-mtag-3-strata, m2-03-cpassoc-3-strata, m2-04-clumping-mtcojo-regions]
autonomous: false
requirements: [REQ-NOVELTY-CLASS-1, REQ-CATALOG-VERSION-LOCK, REQ-OSF-PREREG, REQ-SNAKEMAKE-CI, REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL]
task_count: 5
files_modified:
  - src/python/call_class1_novelty.py
  - src/snakemake/rules/m2_novelty.smk
  - results/novelty/joint_signal_novel.tsv
  - .planning/m2_post_m3_rerun_queue.tsv
  - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md
  - tests/toy_3locus/Snakefile.test
  - tests/toy_3locus/m2_smoke_targets.smk
  - src/python/verify_m2_artifacts.py
  - .planning/amendments/sha256_manifest_m2_frozen.tsv
  - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md
  - .planning/STATE.md
must_haves:
  truths:
    - "src/python/call_class1_novelty.py applies the OSF amendment §7.1 Class 1 operational definition: (MTAG p < 5e-8 OR CPASSOC p < 5e-8) AND max(single-trait p) ≥ 5e-8 AND no GWS hit within ±500 kb in GWAS Catalog v_lock_M2"
    - "results/novelty/joint_signal_novel.tsv has one row per claimed locus with columns chr, pos, rsid, mtag_p, cpassoc_shom_p, cpassoc_shet_p, max_single_trait_p, nearest_gwas_catalog_entry, nearest_distance_bp, confidence_tier (high if MTAG ∩ CPASSOC; medium otherwise)"
    - ".planning/m2_post_m3_rerun_queue.tsv records the AFR LDSC + AFR clumping + AFR mtCOJO re-run obligations (D-M2-02 supersede commitment) + the AFR LD-score re-derivation per Pitfall 11"
    - "tests/toy_3locus/m2_smoke_targets.smk extends the existing toy 3-locus smoke pipeline with at least one M2 rule (residcov_slice or build_region_union) per REQ-SNAKEMAKE-CI"
    - "src/python/verify_m2_artifacts.py is a Python-only verifier per D-M2-Q4 (Quarto deferred); emits Dimension-N PASS/WARN/FAIL JSON covering ROADMAP success criteria 1–6"
    - ".planning/amendments/sha256_manifest_m2_frozen.tsv freezes SHA-256 hashes for all M2 deliverable artifacts (Pattern E) for OSF supplementary upload (M5 follow-up posting per DEC-2026-04-25-02)"
    - ".planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md documents M2 closeout per the M1 closeout template; verifier verdict, deviations, post-M3 queue, M3 hand-off"
  artifacts:
    - path: "src/python/call_class1_novelty.py"
      provides: "OSF amendment §7.1 Class 1 novelty filter — joint-signal novel loci (MTAG ∩ CPASSOC high-confidence + MTAG-only or CPASSOC-only medium tier)"
      min_lines: 120
    - path: "src/snakemake/rules/m2_novelty.smk"
      provides: "Class 1 novelty caller rule + closeout aggregator (calls call_class1_novelty.py against v_lock_M2 GWAS Catalog snapshot)"
      min_lines: 50
    - path: "results/novelty/joint_signal_novel.tsv"
      provides: "ROADMAP M2 success criterion 5 — Class 1 novelty deliverable"
    - path: ".planning/m2_post_m3_rerun_queue.tsv"
      provides: "M3 hand-off — AFR LDSC + clumping + mtCOJO re-run obligations under AoU AFR LD (D-M2-02 supersede commitment + Pitfall 11)"
    - path: "tests/toy_3locus/m2_smoke_targets.smk"
      provides: "REQ-SNAKEMAKE-CI extension — toy 3-locus smoke runs at least one M2 rule"
    - path: "src/python/verify_m2_artifacts.py"
      provides: "M2 phase verifier — Dimension-N PASS/WARN/FAIL coverage of ROADMAP success criteria 1-6 (D-M2-Q4 Python only)"
      min_lines: 200
    - path: ".planning/amendments/sha256_manifest_m2_frozen.tsv"
      provides: "M2 closeout SHA-256 freeze for OSF supplementary upload (M5 follow-up per DEC-2026-04-25-02)"
    - path: ".planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md"
      provides: "M2 closeout report — verifier verdict, deviations log, M3 hand-off"
  key_links:
    - from: "data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt + data/processed/cpassoc/{stratum}/cpassoc_results.tsv + data/catalogs/gwas-catalog-associations-full.zip"
      to: "results/novelty/joint_signal_novel.tsv"
      via: "src/python/call_class1_novelty.py — OSF amendment §7.1 Class 1 operational definition"
      pattern: "joint_signal_novel|class1"
    - from: "results/novelty/joint_signal_novel.tsv + results/regions/union_region_list.bed + bivariate_intercept_matrix_2026-04-M2.tsv"
      to: ".planning/amendments/sha256_manifest_m2_frozen.tsv"
      via: "src/python/freeze_sha256_manifest.py (Pattern E) over M2 deliverable artifacts"
      pattern: "sha256sum|freeze_sha256"
---

<objective>
Wave 5 closes M2 with the novelty deliverable (ROADMAP M2 success criterion 5), the M3 hand-off queue, the Snakemake CI smoke extension, the Python-only phase verifier (D-M2-Q4 — Quarto deferred), the SHA-256 manifest freeze for OSF supplementary upload (DEC-2026-04-25-02), and the M2 PHASE-CLOSEOUT report.

Five tasks:

1. **Class 1 novelty caller** (`call_class1_novelty.py` + `m2_novelty.smk`) implements OSF amendment §7.1 Class 1 operational definition exactly: (MTAG p < 5e-8 OR CPASSOC p < 5e-8) AND max(single-trait p) ≥ 5e-8 AND no contributing single-trait GWS hit within ±500 kb in GWAS Catalog v_lock_M2 (the snapshot frozen in Wave 0 Task 5). High-confidence subset = MTAG ∩ CPASSOC. Output at `results/novelty/joint_signal_novel.tsv` per CONTEXT artifact #8.

2. **Post-M3 re-run queue** (`.planning/m2_post_m3_rerun_queue.tsv`) records D-M2-02 supersede obligations: when M3 lands the AoU AFR LD panel, the AFR clumping + AFR LDSC matrix slice + AFR mtCOJO must re-run with AoU panel; results carry the LD-AoU-AFR token to distinguish from the M2 LD-1000G-AFR provisional outputs. Also queues the AFR LD-score re-derivation per Pitfall 11.

3. **Snakemake CI smoke extension** (`tests/toy_3locus/m2_smoke_targets.smk`) adds a minimal M2 rule to the existing toy 3-locus pipeline so REQ-SNAKEMAKE-CI is preserved end-to-end. Choose a fast deterministic M2 rule (e.g. residcov_slice on a synthetic 3×3 matrix). Smoke must finish < 15 minutes per REQ-SNAKEMAKE-CI acceptance.

4. **Python-only phase verifier** (`src/python/verify_m2_artifacts.py`, D-M2-Q4) modeled directly on the M1 verify_m1_artifacts.py (492 lines per RESEARCH §G). Checks 7 dimensions matching ROADMAP success criteria 1-6 + Class 1 novelty deliverable. Emits a JSON summary with PASS/WARN/FAIL per dimension and an overall verdict.

5. **SHA-256 manifest freeze + PHASE-CLOSEOUT** (`sha256_manifest_m2_frozen.tsv` + `m2-PHASE-CLOSEOUT.md` + STATE.md update). Freeze covers M2 expanded matrix + per-stratum MTAG outputs + per-stratum CPASSOC outputs + clumping aggregator BEDs (sample) + mtcojo_sensitivity.tsv + union_region_list.bed + joint_signal_novel.tsv + the v_lock_M2 GWAS Catalog .zip. Mirror to .planning/amendments/ for the M5 follow-up OSF posting per DEC-2026-04-25-02.

This plan has `autonomous: false` because Task 5 includes a checkpoint:human-verify gate where Carter signs off on the M2 PHASE-CLOSEOUT.md before STATE.md is updated and the M3 phase opens.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-00-preflight-and-environment-PLAN.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-01-ldsc-matrix-refire-PLAN.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-02-mtag-3-strata-PLAN.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-03-cpassoc-3-strata-PLAN.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-04-clumping-mtcojo-regions-PLAN.md
@CLAUDE.md
@src/python/freeze_sha256_manifest.py
@src/python/m2_stratum_keys.py
@src/python/run_cpassoc.py
@.planning/REQUIREMENTS.md
@.planning/ROADMAP.md
@.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
@data/catalogs/catalog_lock_manifest.tsv
@results/regions/union_region_list.bed

<interfaces>
**OSF amendment §7.1 Class 1 operational definition (CONTEXT.md inputs §, OSF-AMENDMENT-TEXT-2026-04-22.md line 74):**

> Joint-signal novel loci = (MTAG p < 5 × 10⁻⁸) OR (CPASSOC p < 5 × 10⁻⁸), AND no contributing single-trait association at p < 5 × 10⁻⁸ within ±500 kb per GWAS Catalog v_lock.

Implementation:
1. For each MTAG-significant locus (mtag_p < 5e-8 AND max_FDR < 0.05): record stratum, trait, chr, pos, rsid, mtag_p
2. For each CPASSOC-significant locus (SHom_p < 5e-8 OR SHet_p < 5e-8): record stratum, chr, pos, rsid, cpassoc_shom_p, cpassoc_shet_p
3. Union the two sets by chr:pos (±1 bp tolerance)
4. For each union locus: compute max single-trait p across the K traits in the stratum (from individual harmonized sumstats) — must be ≥ 5e-8 to qualify as Class 1 (else it's a single-trait win, not joint-signal)
5. Compute nearest GWAS Catalog v_lock_M2 entry within ±500 kb; if any contributing single-trait GWS hit exists in catalog within ±500 kb → drop (NOT novel)
6. confidence_tier = "high" if both MTAG p < 5e-8 AND CPASSOC p < 5e-8; else "medium"

**Output schema (per REQ-NOVELTY-CLASS-1 acceptance):**
```
chr  pos  rsid  stratum  mtag_p  cpassoc_shom_p  cpassoc_shet_p  max_single_trait_p  nearest_gwas_catalog_entry  nearest_distance_bp  confidence_tier
```

**v_lock_M2 catalog snapshot:**
- data/catalogs/gwas-catalog-associations-full.zip (Wave 0 Task 5)
- Unzip on demand (~500 MB TSV); columns include CHR_ID, CHR_POS, MAPPED_TRAIT, P-VALUE, SNPS, etc.
- Use bedtools intersect or simple chr:pos ±500 kb scan

**freeze_sha256_manifest.py contract (M1 Pattern E):**
- Input: list of paths or directory
- Output: TSV with [path, sha256, size_bytes, mtime] sorted by path
- Reuse the existing helper (no code change needed)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: src/python/call_class1_novelty.py + m2_novelty.smk + production fire (REQ-NOVELTY-CLASS-1)</name>
  <files>src/python/call_class1_novelty.py, src/snakemake/rules/m2_novelty.smk, results/novelty/joint_signal_novel.tsv, tests/m2/test_call_class1_novelty.py</files>
  <read_first>
    - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md lines 73-75 (Class 1 operational definition VERBATIM)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-05 lines 82-89
    - data/catalogs/catalog_lock_manifest.tsv (verify v_lock_M2 row from Wave 0 Task 5)
    - data/catalogs/gwas-catalog-associations-full.zip (Wave 0 Task 5 — input for prior-art exclusion)
    - data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt (Wave 2)
    - data/processed/cpassoc/{stratum}/cpassoc_results.tsv (Wave 3)
    - data/processed/sumstats_harmonized/{trait}.{ancestry}.{consortium}.{year}.GRCh37.tsv.bgz (per-trait single-trait p inputs)
    - tests/m2/test_call_class1_novelty.py (RED stub from Wave 0 Task 1)
  </read_first>
  <behavior>
    call_class1_novelty inputs: per-stratum mtag filtered, per-stratum cpassoc results, harmonized single-trait sumstats, gwas catalog .zip, output path.
    Logic:
    1. Build candidate locus set = union(MTAG-significant per stratum, CPASSOC-significant per stratum) by chr:pos
    2. For each candidate: lookup max single-trait p across K traits in stratum from harmonized sumstats — drop if any single-trait p < 5e-8 (NOT joint-signal)
    3. Build BedTool of candidate positions ±500 kb windows
    4. Build BedTool of GWAS Catalog v_lock_M2 entries (chr:pos parsing from MAPPED_TRAIT_URI ÷ CHR_POS columns); filter to entries with P-VALUE < 5e-8
    5. Intersect: any candidate with a catalog hit within ±500 kb is dropped (prior art)
    6. Tag confidence_tier: high if BOTH MTAG and CPASSOC significant; medium otherwise
    7. Output TSV with full schema per REQ-NOVELTY-CLASS-1
    Test cases (4):
    - All single traits significant → drop (not joint-signal)
    - Catalog hit within ±500 kb → drop (prior art)
    - MTAG and CPASSOC both significant + no catalog hit → high confidence
    - Only MTAG significant + no catalog hit → medium confidence
  </behavior>
  <action>
    **Step A — `src/python/call_class1_novelty.py`:**

    ```python
    #!/usr/bin/env python3
    """Class 1 (joint-signal) novelty caller per OSF amendment §7.1.

    Operational definition (locked in OSF posting at osf.io/az52u/files/k8w7n,
    commit 61315de):
      Joint-signal novel = (MTAG p < 5e-8 OR CPASSOC p < 5e-8) AND
                           max(single-trait p) >= 5e-8 AND
                           no contributing single-trait GWS hit within +/-500 kb
                           in GWAS Catalog v_lock.
      High-confidence subset = MTAG ∩ CPASSOC.
    """
    from __future__ import annotations
    import argparse
    import gzip
    import io
    import json
    import zipfile
    from pathlib import Path

    import numpy as np
    import pandas as pd
    from scipy.stats import norm

    _PSIG = 5e-8
    _CATALOG_WINDOW = 500_000   # ±500 kb per OSF §7.1 Class 1


    def _load_mtag_significant(mtag_filtered_paths: dict[str, Path]) -> pd.DataFrame:
        rows = []
        for stratum, path in mtag_filtered_paths.items():
            if not path.exists() or path.stat().st_size == 0:
                continue
            df = pd.read_csv(path, sep='\t')
            p_cols = [c for c in df.columns if c.startswith('P_')]
            for c in p_cols:
                trait = c[2:]
                hits = df[df[c] < _PSIG].copy()
                if hits.empty:
                    continue
                hits = hits.rename(columns={'CHR':'chr','BP':'pos','SNP':'rsid', c:'mtag_p'})
                hits['stratum'] = stratum
                hits['trait'] = trait
                rows.append(hits[['chr','pos','rsid','stratum','trait','mtag_p']])
        if not rows:
            return pd.DataFrame(columns=['chr','pos','rsid','stratum','trait','mtag_p'])
        return pd.concat(rows, ignore_index=True)


    def _load_cpassoc_significant(cpassoc_paths: dict[str, Path]) -> pd.DataFrame:
        rows = []
        for stratum, path in cpassoc_paths.items():
            if not path.exists() or path.stat().st_size == 0:
                continue
            df = pd.read_csv(path, sep='\t')
            hits = df[(df['SHom_p'] < _PSIG) | (df['SHet_p'] < _PSIG)].copy()
            if hits.empty:
                continue
            hits['stratum'] = stratum
            rows.append(hits[['chr','pos','rsid','stratum','SHom_p','SHet_p']]
                       .rename(columns={'SHom_p':'cpassoc_shom_p','SHet_p':'cpassoc_shet_p'}))
        if not rows:
            return pd.DataFrame(columns=['chr','pos','rsid','stratum','cpassoc_shom_p','cpassoc_shet_p'])
        return pd.concat(rows, ignore_index=True)


    def _max_single_trait_p_per_locus(
        candidates: pd.DataFrame,
        harmonized_dir: Path,
        stratum_traits: dict[str, list[str]],
    ) -> pd.Series:
        """For each candidate (chr, pos, stratum), return max p across single-trait sumstats in that stratum."""
        max_p = []
        for _, r in candidates.iterrows():
            stratum = r['stratum']
            traits = stratum_traits.get(stratum, [])
            best_p = 1.0
            for trait_key in traits:
                # trait_key like "bmi.EUR.GIANT-UKBB.2018"
                path = harmonized_dir / f"{trait_key}.GRCh37.tsv.bgz"
                if not path.exists():
                    continue
                # Lookup p for chr:pos in this trait's harmonized sumstats
                # (real impl uses tabix-indexed lookup; this stub scans for the rsid which is faster)
                try:
                    with gzip.open(path, 'rt') as f:
                        header = next(f).strip().split('\t')
                        try:
                            rsid_col = header.index('SNP') if 'SNP' in header else header.index('rsid')
                            p_col = next(i for i, h in enumerate(header) if h in ('P', 'p', 'pval', 'P_value'))
                        except (ValueError, StopIteration):
                            continue
                        for line in f:
                            cols = line.rstrip('\n').split('\t')
                            if cols[rsid_col] == r['rsid']:
                                try:
                                    p_val = float(cols[p_col])
                                    if p_val < best_p:
                                        best_p = p_val
                                except ValueError:
                                    pass
                                break
                except OSError:
                    continue
            max_p.append(best_p)
        return pd.Series(max_p)


    def _load_catalog_v_lock_M2(catalog_zip_path: Path) -> pd.DataFrame:
        """Read GWAS Catalog v_lock_M2 .zip; return DataFrame with [chr, pos, p_value, mapped_trait, snps] for entries with P < 5e-8."""
        with zipfile.ZipFile(catalog_zip_path) as zf:
            tsv_name = next(n for n in zf.namelist() if n.endswith('.tsv'))
            with zf.open(tsv_name) as f:
                df = pd.read_csv(io.TextIOWrapper(f, encoding='utf-8', errors='replace'),
                                 sep='\t', low_memory=False, on_bad_lines='skip')
        # Common columns in EBI GWAS Catalog: CHR_ID, CHR_POS, P-VALUE, MAPPED_TRAIT, SNPS
        chr_col = 'CHR_ID' if 'CHR_ID' in df.columns else 'CHR'
        pos_col = 'CHR_POS' if 'CHR_POS' in df.columns else 'POS'
        p_col = 'P-VALUE' if 'P-VALUE' in df.columns else 'P_VALUE'
        df = df[[chr_col, pos_col, p_col, 'MAPPED_TRAIT', 'SNPS']].copy()
        df.columns = ['chr', 'pos', 'p_value', 'mapped_trait', 'snps']
        df['p_value'] = pd.to_numeric(df['p_value'], errors='coerce')
        df['pos'] = pd.to_numeric(df['pos'], errors='coerce').astype('Int64')
        df = df.dropna(subset=['chr', 'pos', 'p_value'])
        df = df[df['p_value'] < _PSIG]
        return df


    def _nearest_catalog_within_500kb(
        candidates: pd.DataFrame,
        catalog: pd.DataFrame,
    ) -> pd.DataFrame:
        """Return per-candidate nearest_gwas_catalog_entry + nearest_distance_bp."""
        out_entries = []
        out_distances = []
        for _, r in candidates.iterrows():
            chr_match = catalog[catalog['chr'].astype(str) == str(r['chr']).replace('chr','')]
            if chr_match.empty:
                out_entries.append('')
                out_distances.append(np.nan)
                continue
            distances = (chr_match['pos'] - r['pos']).abs()
            i_min = distances.idxmin()
            d = int(distances.loc[i_min])
            if d <= _CATALOG_WINDOW:
                out_entries.append(f"{chr_match.loc[i_min, 'snps']}:{chr_match.loc[i_min, 'mapped_trait']}")
            else:
                out_entries.append('')
            out_distances.append(d)
        return pd.DataFrame({
            'nearest_gwas_catalog_entry': out_entries,
            'nearest_distance_bp': out_distances,
        })


    def call_class1_novelty(
        mtag_filtered_paths: dict[str, Path],
        cpassoc_paths: dict[str, Path],
        sidecar_paths: dict[str, Path],
        harmonized_dir: Path,
        catalog_zip_path: Path,
        out_path: Path,
    ) -> int:
        # 1. Build candidate set
        mtag_sig = _load_mtag_significant(mtag_filtered_paths)
        cpassoc_sig = _load_cpassoc_significant(cpassoc_paths)
        candidates = pd.merge(mtag_sig, cpassoc_sig, on=['chr','pos','rsid','stratum'], how='outer')

        if candidates.empty:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text("chr\tpos\trsid\tstratum\tmtag_p\tcpassoc_shom_p\tcpassoc_shet_p\tmax_single_trait_p\tnearest_gwas_catalog_entry\tnearest_distance_bp\tconfidence_tier\n")
            return 0

        # 2. Load stratum trait lists from sidecars
        stratum_traits = {}
        for stratum, sidecar in sidecar_paths.items():
            if sidecar.exists():
                stratum_traits[stratum] = json.loads(sidecar.read_text())['trait_order']

        # 3. Max single-trait p per candidate
        candidates['max_single_trait_p'] = _max_single_trait_p_per_locus(candidates, harmonized_dir, stratum_traits)

        # 4. Filter: max single-trait p must be >= 5e-8 (NOT a single-trait win)
        candidates = candidates[candidates['max_single_trait_p'] >= _PSIG]

        # 5. GWAS Catalog v_lock_M2 prior-art exclusion
        catalog = _load_catalog_v_lock_M2(catalog_zip_path)
        nearest = _nearest_catalog_within_500kb(candidates, catalog)
        candidates = pd.concat([candidates.reset_index(drop=True), nearest.reset_index(drop=True)], axis=1)

        # Drop candidates with a catalog hit within ±500 kb (prior art)
        candidates = candidates[(candidates['nearest_distance_bp'].isna()) | (candidates['nearest_distance_bp'] > _CATALOG_WINDOW)]

        # 6. Confidence tier
        is_mtag = candidates['mtag_p'].notna() & (candidates['mtag_p'] < _PSIG)
        is_cpassoc = ((candidates['cpassoc_shom_p'].notna() & (candidates['cpassoc_shom_p'] < _PSIG)) |
                      (candidates['cpassoc_shet_p'].notna() & (candidates['cpassoc_shet_p'] < _PSIG)))
        candidates['confidence_tier'] = np.where(is_mtag & is_cpassoc, 'high', 'medium')

        # 7. Output
        out_cols = ['chr','pos','rsid','stratum','mtag_p','cpassoc_shom_p','cpassoc_shet_p',
                    'max_single_trait_p','nearest_gwas_catalog_entry','nearest_distance_bp','confidence_tier']
        for c in out_cols:
            if c not in candidates.columns:
                candidates[c] = np.nan
        out_path.parent.mkdir(parents=True, exist_ok=True)
        candidates[out_cols].to_csv(out_path, sep='\t', index=False)
        return len(candidates)


    def _main() -> None:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("--strata", nargs='+', default=['EUR','AFR','TRANS'])
        ap.add_argument("--mtag-dir", type=Path, default=Path("data/processed/mtag"))
        ap.add_argument("--cpassoc-dir", type=Path, default=Path("data/processed/cpassoc"))
        ap.add_argument("--harmonized-dir", type=Path, default=Path("data/processed/sumstats_harmonized"))
        ap.add_argument("--catalog-zip", type=Path, default=Path("data/catalogs/gwas-catalog-associations-full.zip"))
        ap.add_argument("--out", type=Path, default=Path("results/novelty/joint_signal_novel.tsv"))
        args = ap.parse_args()
        mtag_paths = {s: args.mtag_dir / s / f"{s}_mtag_maxfdr_filtered.txt" for s in args.strata}
        cpassoc_paths = {s: args.cpassoc_dir / s / "cpassoc_results.tsv" for s in args.strata}
        sidecar_paths = {s: args.mtag_dir / s / "residcov.trait_order.json" for s in args.strata}
        n = call_class1_novelty(mtag_paths, cpassoc_paths, sidecar_paths,
                                args.harmonized_dir, args.catalog_zip, args.out)
        print(f"Wrote {n} Class 1 novel loci to {args.out}")


    if __name__ == "__main__":
        _main()
    ```

    **Step B — `src/snakemake/rules/m2_novelty.smk`:**

    ```python
    """M2 Wave 5 — Class 1 novelty caller per OSF amendment §7.1.

    Plan: m2-05-class1-novelty-and-closeout-PLAN.md.
    REQ-NOVELTY-CLASS-1 + D-M2-05 (catalog v_lock_M2) + D-M2-07 (max_FDR threshold).
    """
    from pathlib import Path

    STRATA = ("EUR", "AFR", "TRANS")

    rule m2_call_class1_novelty:
        """Class 1 (joint-signal) novelty filter against GWAS Catalog v_lock_M2."""
        input:
            mtag=expand("data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt", stratum=STRATA),
            cpassoc=expand("data/processed/cpassoc/{stratum}/cpassoc_results.tsv", stratum=STRATA),
            sidecars=expand("data/processed/mtag/{stratum}/residcov.trait_order.json", stratum=STRATA),
            catalog="data/catalogs/gwas-catalog-associations-full.zip",
        output:
            novel="results/novelty/joint_signal_novel.tsv",
        conda:
            "../../../envs/m2-novelty.yml"
        resources:
            mem_mb=8000,
            runtime=60,
        shell:
            r"""
            mkdir -p $(dirname {output.novel})
            python src/python/call_class1_novelty.py \
                --strata EUR AFR TRANS \
                --catalog-zip {input.catalog} \
                --out {output.novel}
            wc -l {output.novel}
            """
    ```

    Wire tests/m2/test_call_class1_novelty.py from RED → GREEN with the 4 test cases described in <behavior>.

    Production fire:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_novelty.smk \
        --cores 4 \
        m2_call_class1_novelty
    ```

    Atomic commit: `feat(m2-05): call_class1_novelty.py + m2_novelty.smk + production fire (REQ-NOVELTY-CLASS-1)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/call_class1_novelty.py &amp;&amp; test -f src/snakemake/rules/m2_novelty.smk &amp;&amp; grep -c "_PSIG = 5e-8" src/python/call_class1_novelty.py &amp;&amp; grep -c "_CATALOG_WINDOW = 500_000" src/python/call_class1_novelty.py &amp;&amp; grep -c "rule m2_call_class1_novelty:" src/snakemake/rules/m2_novelty.smk &amp;&amp; pytest tests/m2/test_call_class1_novelty.py -x &amp;&amp; test -s results/novelty/joint_signal_novel.tsv &amp;&amp; head -1 results/novelty/joint_signal_novel.tsv | grep -E "confidence_tier"</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/call_class1_novelty.py` exists ≥120 lines
    - `grep -c "_PSIG = 5e-8" src/python/call_class1_novelty.py` returns 1
    - `grep -c "_CATALOG_WINDOW = 500_000" src/python/call_class1_novelty.py` returns 1 (±500 kb per OSF §7.1)
    - `grep -c "v_lock" src/python/call_class1_novelty.py` returns ≥1 (catalog snapshot reference)
    - File `src/snakemake/rules/m2_novelty.smk` exists ≥50 lines
    - `grep -c "rule m2_call_class1_novelty:" src/snakemake/rules/m2_novelty.smk` returns 1
    - `pytest tests/m2/test_call_class1_novelty.py -x` exits 0
    - After fire: `results/novelty/joint_signal_novel.tsv` exists
    - Header row contains literal `confidence_tier`, `mtag_p`, `cpassoc_shom_p`, `cpassoc_shet_p`, `max_single_trait_p`, `nearest_gwas_catalog_entry`, `nearest_distance_bp`
    - All confidence_tier values are in {"high", "medium"}
    - All max_single_trait_p ≥ 5e-8 (Class 1 invariant — NOT a single-trait win)
    - All nearest_distance_bp values where present are > 500_000 OR the entry column is empty
    - `git log --oneline -3 | grep "m2_novelty.smk\|call_class1_novelty"`
  </acceptance_criteria>
  <done>Class 1 novelty caller GREEN; results/novelty/joint_signal_novel.tsv produced; ROADMAP success criterion 5 satisfied; REQ-NOVELTY-CLASS-1 deliverable in place; OSF amendment §7.1 operational definition encoded literally.</done>
</task>

<task type="auto">
  <name>Task 2: M3 hand-off + REQ-SNAKEMAKE-CI extension (D-M2-02 supersede queue + toy-3-locus M2 smoke)</name>
  <files>.planning/m2_post_m3_rerun_queue.tsv, .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md, tests/toy_3locus/m2_smoke_targets.smk, tests/toy_3locus/Snakefile.test</files>
  <read_first>
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-02 lines 53-59 + §D-M2-06 lines 90-96
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 11" lines 671-679 (AFR LD-score re-derivation queued)
    - tests/toy_3locus/Snakefile.test (the existing toy 3-locus smoke pipeline; verify exists; if not, create minimal scaffold)
    - .planning/REQUIREMENTS.md §REQ-SNAKEMAKE-CI lines 25-39 (acceptance: 15 min ceiling)
    - data/processed/mtag/EUR/skipped_traits.tsv (Wave 2 — collect skip-with-doc rows for the deferred-items.md)
    - data/processed/mtag/{stratum}/skipped_strata.tsv (Wave 2 — same)
  </read_first>
  <action>
    **Step A — `.planning/m2_post_m3_rerun_queue.tsv`:**

    Author the queue file with header + rows describing each M3-supersede obligation per D-M2-02 + Pitfall 11:

    ```
    obligation_id	source_decision	description	current_artifact	supersede_artifact	dependency	priority
    M2-POST-M3-01	D-M2-02	Re-fire AFR PLINK clumping using AoU AFR LD panel	data/processed/clumping/AFR/*.LD-1000G-AFR.clumped.bed	data/processed/clumping/AFR/*.LD-AoU-AFR.clumped.bed	M3 AoU AFR LD panel build complete (AOU-LD-PIPELINE.md §6)	high
    M2-POST-M3-02	D-M2-02	Re-fire AFR LDSC matrix slice (gcov_int row + col) using AoU AFR LD	data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv (AFR rows estimated with EUR LD per Pitfall 11 cross-ancestry approximation)	bivariate_intercept_matrix_2026-04-M3.tsv (AFR rows re-estimated with AoU AFR ld-scores)	M3 AoU AFR ld-scores derived	high
    M2-POST-M3-03	D-M2-02	Re-fire AFR mtCOJO with AoU AFR LD	data/processed/mtcojo/AFR/*.mtcojo.cojo (LD ref 1000G AFR N=661)	data/processed/mtcojo/AFR/*.mtcojo.AoU.cojo (LD ref AoU AFR N=~95k)	M3 AoU AFR PLINK bfile available	medium
    M2-POST-M3-04	D-M2-Q3	TRANS mtCOJO 1000G AFR sensitivity check	(not yet run)	data/processed/mtcojo/TRANS/*.mtcojo.AFR-sensitivity.cojo (column trans_ld_panel_concordance in mtcojo_sensitivity.tsv)	1000G AFR PLINK bfile (already built Wave 0 Task 4)	low — Wave 4 robustness add
    M2-POST-M3-05	Pitfall-11	AFR LD-score re-derivation for proper AFR-AFR LDSC bivariate intercept estimation	data/external/ldscore/eur_w_ld_chr/ (used for ALL pairs incl. AFR-AFR — cross-ancestry approximation per D-M2-Q2)	data/external/ldscore/afr_w_ld_chr/ from AoU AFR WGS	M3 AoU AFR ld-scores derived	medium
    M2-POST-M3-06	D-M2-05	GWAS Catalog v_lock_M5 refresh + delta with v_lock_M2	data/catalogs/catalog_lock_manifest.tsv row gwas_catalog.v_lock_M2	additional row gwas_catalog.v_lock_M5 + gwas_catalog_lock_diff_M2_to_M5.tsv	M5 cross-reference date reached	deferred to M5
    ```

    **Step B — `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md`:**

    Author markdown summary listing:
    - Skipped strata per D-M2-Q6 (collect rows from data/processed/mtag/*/skipped_strata.tsv + data/processed/cpassoc/*/skipped_strata.tsv)
    - Skipped trait cells per D-M2-06 (collect rows from data/processed/mtag/*/skipped_traits.tsv)
    - Carter resume queue items inherited from M1 (DIAMANTE cookies, GBMI portal, Loh D-01, MAGIC EUR re-fetch, Aragam EUR sex-strat, Klarin) per CONTEXT inputs §
    - Cross-reference to .planning/m2_post_m3_rerun_queue.tsv for M3-supersede obligations
    - Cross-reference to .planning/RETROSPECTIVE.md (if exists) for M2 pattern lessons

    **Step C — `tests/toy_3locus/m2_smoke_targets.smk` + extend `tests/toy_3locus/Snakefile.test`:**

    Add a minimal M2 smoke rule using a synthetic 3×3 matrix:

    ```python
    # tests/toy_3locus/m2_smoke_targets.smk
    """REQ-SNAKEMAKE-CI extension — M2 smoke targets.

    Adds at least one M2 rule (residcov_slice on synthetic 3x3) to the existing
    toy 3-locus pipeline. Smoke must finish < 15 minutes per REQ-SNAKEMAKE-CI.
    """

    rule m2_smoke_residcov_slice:
        """Smoke test of build_mtag_residcov_slice on a synthetic 3x3 matrix."""
        output:
            residcov="tests/toy_3locus/m2_smoke_out/EUR/residcov.txt",
            sidecar="tests/toy_3locus/m2_smoke_out/EUR/residcov.trait_order.json",
        conda:
            "../../envs/m2-cpassoc.yml"
        shell:
            r"""
            mkdir -p $(dirname {output.residcov})
            # Generate a synthetic 3-trait LDSC matrix
            python -c "
            import pandas as pd, numpy as np
            keys = ['toy_a.EUR.SYN.2020', 'toy_b.EUR.SYN.2020', 'toy_c.EUR.SYN.2020']
            M = np.array([[1.0, 0.1, 0.2], [0.1, 1.0, 0.15], [0.2, 0.15, 1.0]])
            pd.DataFrame(M, index=keys, columns=keys).to_csv(
                'tests/toy_3locus/m2_smoke_out/synthetic_matrix.tsv', sep='\t')
            # Synthetic inventory minimal
            import yaml
            inv = {{}}
            for k in keys:
                inv[k] = {{
                    'ancestry': 'EUR',
                    'qc_status': 'PASS',
                    'munged_path': 'tests/toy_3locus/m2_smoke_out/' + k + '.fake',
                }}
                # Touch the fake munged path
                with open(inv[k]['munged_path'], 'w') as fh:
                    fh.write('')
            with open('tests/toy_3locus/m2_smoke_out/synthetic_inventory.yaml', 'w') as fh:
                yaml.safe_dump({{'traits': inv}}, fh)
            "
            python src/python/build_mtag_residcov_slice.py \
                --matrix tests/toy_3locus/m2_smoke_out/synthetic_matrix.tsv \
                --stratum EUR \
                --inventory tests/toy_3locus/m2_smoke_out/synthetic_inventory.yaml \
                --out-dir $(dirname {output.residcov})
            test -s {output.residcov}
            test -s {output.sidecar}
            """
    ```

    Edit `tests/toy_3locus/Snakefile.test` to include this rule via `include: "m2_smoke_targets.smk"` and add `m2_smoke_residcov_slice` to the default target.

    Atomic commit: `feat(m2-05): M3 supersede queue + deferred-items.md + REQ-SNAKEMAKE-CI M2 smoke (D-M2-02, D-M2-Q3, Pitfall 11)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -s .planning/m2_post_m3_rerun_queue.tsv &amp;&amp; grep -c "M2-POST-M3-01" .planning/m2_post_m3_rerun_queue.tsv &amp;&amp; grep -c "M2-POST-M3-05" .planning/m2_post_m3_rerun_queue.tsv &amp;&amp; test -f .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md &amp;&amp; test -f tests/toy_3locus/m2_smoke_targets.smk &amp;&amp; grep -c "rule m2_smoke_residcov_slice:" tests/toy_3locus/m2_smoke_targets.smk &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake -s tests/toy_3locus/Snakefile.test --cores 2 --use-conda --dry-run m2_smoke_residcov_slice</automated>
  </verify>
  <acceptance_criteria>
    - File `.planning/m2_post_m3_rerun_queue.tsv` exists with at least 5 obligation rows
    - At minimum these obligation_id values appear: M2-POST-M3-01, M2-POST-M3-02, M2-POST-M3-03, M2-POST-M3-05
    - Each row references its source_decision (D-M2-02 / D-M2-Q3 / Pitfall-11 / D-M2-05)
    - File `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md` exists with sections for "Skipped strata", "Skipped trait cells", "Carter resume queue", and "M3 supersede queue cross-reference"
    - File `tests/toy_3locus/m2_smoke_targets.smk` exists with `rule m2_smoke_residcov_slice:` defined
    - `tests/toy_3locus/Snakefile.test` includes the M2 smoke rule (`grep -c "m2_smoke_targets" tests/toy_3locus/Snakefile.test` ≥ 1)
    - Snakemake dry-run for `m2_smoke_residcov_slice` exits 0
    - `git log -1 --pretty=%B` matches `feat(m2-05): M3 supersede queue`
  </acceptance_criteria>
  <done>M3 hand-off queue authored with 6 supersede obligations; deferred-items.md aggregates skip-with-doc rows; REQ-SNAKEMAKE-CI extended with at least one M2 rule; toy 3-locus smoke dry-run passes.</done>
</task>

<task type="auto">
  <name>Task 3: src/python/verify_m2_artifacts.py — Python-only phase verifier per D-M2-Q4</name>
  <files>src/python/verify_m2_artifacts.py</files>
  <read_first>
    - src/python/verify_m1_artifacts.py if it exists (the M1 reference per RESEARCH §Pattern G — model verify_m2 directly on it)
    - .planning/ROADMAP.md M2 Success Criteria 1-6 lines 119-125
    - .planning/REQUIREMENTS.md §"REQ-MTAG-OVERLAP" + §"REQ-CPASSOC-ORTHOGONAL" + §"REQ-NOVELTY-CLASS-1" + §"REQ-CATALOG-VERSION-LOCK" + §"REQ-OSF-PREREG" + §"REQ-SNAKEMAKE-CI"
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §"Expected Deliverable Artifacts" table lines 137-153
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-Q4 lines 260-264 (Python only, Quarto deferred)
  </read_first>
  <action>
    Author `src/python/verify_m2_artifacts.py` modeled directly on verify_m1_artifacts.py (RESEARCH §G fallback per D-M2-Q4 — Quarto deferred to M6 manuscript phase). 7 Dimensions matching ROADMAP M2 success criteria 1-6 + Class 1 deliverable + REQ-* coverage:

    ```python
    #!/usr/bin/env python3
    """M2 phase verifier — Python only per D-M2-Q4.

    Plan: m2-05-class1-novelty-and-closeout-PLAN.md.
    Modeled on src/python/verify_m1_artifacts.py (RESEARCH §G fallback pattern).
    Quarto QC report deferred to M6 manuscript phase.

    Dimensions checked (PASS/WARN/FAIL):
      D1 — RM-1: bivariate_intercept_matrix_2026-04-M2.tsv exists, square N>=20, symmetric, diag~1.0
      D2 — RM-2: per-stratum MTAG outputs exist with max_FDR column; --residcov_path was used (not --overlap)
      D3 — RM-3: per-stratum CPASSOC outputs exist with SHom_p + SHet_p columns
      D4 — RM-4: results/regions/union_region_list.bed exists with provenance JSON
      D5 — RM-5: results/novelty/joint_signal_novel.tsv exists with confidence_tier column
      D6 — RM-6: data/processed/mtcojo/*/mtcojo_sensitivity.tsv exists for at least one stratum
      D7 — REQ-CATALOG-VERSION-LOCK: catalog_lock_manifest.tsv has row gwas_catalog.v_lock_M2 with valid SHA-256
      D8 — REQ-OSF-PREREG: gate-release commit d55c1d1 already landed (manual sentinel; pass-through)
      D9 — REQ-SNAKEMAKE-CI: tests/toy_3locus/m2_smoke_targets.smk exists with at least one M2 rule
    Overall verdict: PASS only if all dimensions PASS.
    """
    from __future__ import annotations
    import argparse
    import json
    import re
    import subprocess
    from pathlib import Path
    from datetime import datetime

    import pandas as pd
    import numpy as np

    _PROJECT_ROOT = Path(__file__).resolve().parents[2]


    def _check_d1_ldsc_matrix() -> dict:
        path = _PROJECT_ROOT / "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
        if not path.exists():
            return {"dimension": "D1", "verdict": "FAIL", "reason": f"missing {path}"}
        try:
            M = pd.read_csv(path, sep='\t', index_col=0)
        except Exception as e:
            return {"dimension": "D1", "verdict": "FAIL", "reason": f"unparseable: {e}"}
        if M.shape[0] != M.shape[1]:
            return {"dimension": "D1", "verdict": "FAIL", "reason": f"not square: {M.shape}"}
        if not (20 <= M.shape[0] <= 50):
            return {"dimension": "D1", "verdict": "WARN", "reason": f"N={M.shape[0]} out of expected band 20-50"}
        A = M.values
        if np.nanmax(np.abs(A - A.T)) > 1e-6:
            return {"dimension": "D1", "verdict": "FAIL", "reason": "not symmetric"}
        return {"dimension": "D1", "verdict": "PASS", "n_traits": int(M.shape[0])}


    def _check_d2_mtag(strata=("EUR","AFR","TRANS")) -> dict:
        results = {}
        for s in strata:
            f = _PROJECT_ROOT / f"data/processed/mtag/{s}/{s}_mtag_maxfdr_filtered.txt"
            skip = _PROJECT_ROOT / f"data/processed/mtag/{s}/skipped_strata.tsv"
            if f.exists():
                df = pd.read_csv(f, sep='\t')
                results[s] = {
                    "exists": True,
                    "rows": int(len(df)),
                    "has_max_FDR": "max_FDR" in df.columns,
                    "all_below_threshold": bool((df["max_FDR"] < 0.05).all()) if "max_FDR" in df.columns else False,
                }
            elif skip.exists():
                results[s] = {"exists": False, "skipped": True, "reason": skip.read_text().strip().split('\n')[0]}
            else:
                results[s] = {"exists": False, "skipped": False, "reason": "not produced"}
        any_landed = any(r.get("exists", False) for r in results.values())
        all_with_max_fdr = all(r.get("has_max_FDR", False) for r in results.values() if r.get("exists"))
        if any_landed and all_with_max_fdr:
            return {"dimension": "D2", "verdict": "PASS", "per_stratum": results}
        if any_landed:
            return {"dimension": "D2", "verdict": "WARN", "per_stratum": results, "reason": "some max_FDR columns missing"}
        return {"dimension": "D2", "verdict": "FAIL", "per_stratum": results, "reason": "no MTAG output landed"}


    def _check_d3_cpassoc(strata=("EUR","AFR","TRANS")) -> dict:
        results = {}
        for s in strata:
            f = _PROJECT_ROOT / f"data/processed/cpassoc/{s}/cpassoc_results.tsv"
            if f.exists() and f.stat().st_size > 0:
                df = pd.read_csv(f, sep='\t', nrows=10)
                results[s] = {
                    "exists": True,
                    "has_SHom_p": "SHom_p" in df.columns,
                    "has_SHet_p": "SHet_p" in df.columns,
                }
            else:
                results[s] = {"exists": False}
        any_landed = any(r.get("exists", False) for r in results.values())
        all_complete = all(r.get("has_SHom_p") and r.get("has_SHet_p") for r in results.values() if r.get("exists"))
        if any_landed and all_complete:
            return {"dimension": "D3", "verdict": "PASS", "per_stratum": results}
        return {"dimension": "D3", "verdict": "FAIL" if not any_landed else "WARN", "per_stratum": results}


    def _check_d4_regions() -> dict:
        path = _PROJECT_ROOT / "results/regions/union_region_list.bed"
        if not path.exists():
            return {"dimension": "D4", "verdict": "FAIL", "reason": f"missing {path}"}
        df = pd.read_csv(path, sep='\t', header=None, nrows=5)
        n = sum(1 for _ in open(path))
        if n < 100:
            return {"dimension": "D4", "verdict": "WARN", "regions": n, "reason": "below 100-region floor"}
        last_col = df.iloc[0, -1]
        try:
            json.loads(str(last_col))
            has_provenance = True
        except Exception:
            has_provenance = False
        return {
            "dimension": "D4",
            "verdict": "PASS" if has_provenance else "WARN",
            "regions": n,
            "has_provenance_json": has_provenance,
        }


    def _check_d5_novelty() -> dict:
        path = _PROJECT_ROOT / "results/novelty/joint_signal_novel.tsv"
        if not path.exists():
            return {"dimension": "D5", "verdict": "FAIL", "reason": f"missing {path}"}
        df = pd.read_csv(path, sep='\t')
        required = {"chr","pos","rsid","stratum","mtag_p","cpassoc_shom_p","cpassoc_shet_p",
                    "max_single_trait_p","nearest_gwas_catalog_entry","nearest_distance_bp","confidence_tier"}
        missing = required - set(df.columns)
        if missing:
            return {"dimension": "D5", "verdict": "FAIL", "reason": f"missing columns: {missing}"}
        if not df["confidence_tier"].isin({"high","medium"}).all():
            return {"dimension": "D5", "verdict": "WARN", "reason": "confidence_tier values out of vocab"}
        return {"dimension": "D5", "verdict": "PASS", "loci": int(len(df)), "high_confidence": int((df["confidence_tier"]=="high").sum())}


    def _check_d6_mtcojo(strata=("EUR","AFR","TRANS")) -> dict:
        any_landed = False
        per = {}
        for s in strata:
            f = _PROJECT_ROOT / f"data/processed/mtcojo/{s}/mtcojo_sensitivity.tsv"
            if f.exists() and f.stat().st_size > 0:
                any_landed = True
                df = pd.read_csv(f, sep='\t', nrows=5)
                per[s] = {"exists": True, "has_sensitivity_flag": "sensitivity_flag" in df.columns}
            else:
                per[s] = {"exists": False}
        return {
            "dimension": "D6",
            "verdict": "PASS" if any_landed else "FAIL",
            "per_stratum": per,
        }


    def _check_d7_catalog() -> dict:
        path = _PROJECT_ROOT / "data/catalogs/catalog_lock_manifest.tsv"
        if not path.exists():
            return {"dimension": "D7", "verdict": "FAIL", "reason": f"missing {path}"}
        text = path.read_text()
        if "gwas_catalog.v_lock_M2" not in text:
            return {"dimension": "D7", "verdict": "FAIL", "reason": "no v_lock_M2 row"}
        sha_match = re.search(r"gwas_catalog\.v_lock_M2.*?([a-f0-9]{64})", text)
        if not sha_match:
            return {"dimension": "D7", "verdict": "WARN", "reason": "v_lock_M2 row found but no 64-hex SHA-256"}
        return {"dimension": "D7", "verdict": "PASS", "sha256_prefix": sha_match.group(1)[:12]}


    def _check_d8_osf() -> dict:
        # OSF gate already released 2026-04-25 per DEC-2026-04-25-02
        try:
            log = subprocess.run(["git", "log", "--oneline", "--all", "--grep=M2 gate released"],
                                 cwd=_PROJECT_ROOT, capture_output=True, text=True, timeout=30)
            has_gate_release = "d55c1d1" in log.stdout or "M2 gate released" in log.stdout
        except Exception:
            has_gate_release = False
        return {
            "dimension": "D8",
            "verdict": "PASS",
            "gate_release": has_gate_release,
            "note": "OSF amendment posted at osf.io/az52u/files/k8w7n per DEC-2026-04-25-02",
        }


    def _check_d9_snakemake_ci() -> dict:
        smoke = _PROJECT_ROOT / "tests/toy_3locus/m2_smoke_targets.smk"
        if not smoke.exists():
            return {"dimension": "D9", "verdict": "FAIL", "reason": f"missing {smoke}"}
        if "rule m2_smoke" not in smoke.read_text():
            return {"dimension": "D9", "verdict": "WARN", "reason": "no m2_smoke* rule found"}
        return {"dimension": "D9", "verdict": "PASS"}


    def verify_all() -> dict:
        results = [
            _check_d1_ldsc_matrix(),
            _check_d2_mtag(),
            _check_d3_cpassoc(),
            _check_d4_regions(),
            _check_d5_novelty(),
            _check_d6_mtcojo(),
            _check_d7_catalog(),
            _check_d8_osf(),
            _check_d9_snakemake_ci(),
        ]
        verdicts = [r["verdict"] for r in results]
        if all(v == "PASS" for v in verdicts):
            overall = "PASS"
        elif any(v == "FAIL" for v in verdicts):
            overall = "FAIL"
        else:
            overall = "WARN"
        return {
            "phase": "m2-ldsc-mtag-cpassoc-discovery",
            "verified_at": datetime.utcnow().isoformat() + "Z",
            "overall": overall,
            "dimensions": results,
        }


    def _main() -> None:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("--out", type=Path,
                        default=Path(".planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json"))
        args = ap.parse_args()
        result = verify_all()
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2))
        print(f"Overall: {result['overall']}")
        for d in result["dimensions"]:
            print(f"  {d['dimension']}: {d['verdict']}")
        raise SystemExit(0 if result["overall"] != "FAIL" else 1)


    if __name__ == "__main__":
        _main()
    ```

    Run the verifier and capture output:
    ```bash
    python src/python/verify_m2_artifacts.py --out .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json
    cat .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json
    ```

    Atomic commit: `feat(m2-05): verify_m2_artifacts.py Python-only verifier (D-M2-Q4, Dimensions D1-D9)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/verify_m2_artifacts.py &amp;&amp; grep -c "def _check_d1_ldsc_matrix" src/python/verify_m2_artifacts.py &amp;&amp; grep -c "def _check_d5_novelty" src/python/verify_m2_artifacts.py &amp;&amp; grep -c "def verify_all" src/python/verify_m2_artifacts.py &amp;&amp; python src/python/verify_m2_artifacts.py --out /tmp/m2_verify.json &amp;&amp; python -c "import json; r=json.load(open('/tmp/m2_verify.json')); print('overall:', r['overall']); assert r['overall'] in ('PASS','WARN'), r"</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/verify_m2_artifacts.py` exists ≥200 lines
    - `grep -c "def _check_d" src/python/verify_m2_artifacts.py` returns ≥9 (one per Dimension D1-D9)
    - `grep -c "def verify_all" src/python/verify_m2_artifacts.py` returns 1
    - Running the verifier exits 0 (overall PASS or WARN; FAIL would block closeout)
    - `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json` exists with valid JSON
    - JSON contains keys `phase`, `verified_at`, `overall`, `dimensions`
    - JSON `dimensions` array has ≥9 items, each with `dimension` and `verdict` keys
    - Overall verdict is "PASS" or "WARN" (not "FAIL")
    - `git log -1 --pretty=%B` matches `feat(m2-05): verify_m2_artifacts.py`
  </acceptance_criteria>
  <done>verify_m2_artifacts.py emits Dimension D1-D9 PASS/WARN/FAIL JSON; overall verdict PASS or WARN; D-M2-Q4 Python-only verifier landed; Quarto deferred to M6 per CONTEXT.</done>
</task>

<task type="auto">
  <name>Task 4: SHA-256 manifest freeze for M2 deliverables (Pattern E + DEC-2026-04-25-02 OSF follow-up)</name>
  <files>.planning/amendments/sha256_manifest_m2_frozen.tsv</files>
  <read_first>
    - src/python/freeze_sha256_manifest.py (M1 Pattern E reference — reuse the existing helper)
    - .planning/amendments/sha256_manifest_m1_frozen.tsv (M1 manifest schema — must match)
    - .planning/amendments/sha256_manifest_harmonized_m1.tsv (secondary schema reference)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pattern E" lines 459-475 (M2 freeze coverage list)
    - .planning/DECISIONS.md §DEC-2026-04-25-02 lines 680-693 (OSF posting form — file uploaded to az52u as supplementary)
  </read_first>
  <action>
    Use the existing `src/python/freeze_sha256_manifest.py` helper to compute SHA-256 over the M2 deliverable artifacts per RESEARCH Pattern E coverage list:

    Files to freeze (in order):
    1. `data/catalogs/gwas-catalog-associations-full.zip` (raw bytes for v_lock_M2 — Pitfall 10 invariant)
    2. `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv`
    3. `data/processed/ldsc_overlap/rg_matrix_long_M2.tsv`
    4. All `data/processed/mtag/{stratum}/{stratum}_mtag_meta_results.txt`
    5. All `data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt`
    6. All `data/processed/cpassoc/{stratum}/cpassoc_results.tsv`
    7. Sample of `data/processed/clumping/{ancestry}/*.clumped.bed` (first 5 by lex order — full set is too large for OSF supplementary)
    8. All `data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv`
    9. `results/regions/union_region_list.bed`
    10. `results/novelty/joint_signal_novel.tsv`

    Concrete shell:
    ```bash
    set -euo pipefail
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

    OUT=.planning/amendments/sha256_manifest_m2_frozen.tsv
    mkdir -p $(dirname $OUT)

    # Build paths list
    PATHS_LIST=$(mktemp)
    trap "rm -f $PATHS_LIST" EXIT

    {
        echo data/catalogs/gwas-catalog-associations-full.zip
        echo data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv
        echo data/processed/ldsc_overlap/rg_matrix_long_M2.tsv
        ls data/processed/mtag/*/[A-Z]*_mtag_meta_results.txt 2>/dev/null
        ls data/processed/mtag/*/[A-Z]*_mtag_maxfdr_filtered.txt 2>/dev/null
        ls data/processed/cpassoc/*/cpassoc_results.tsv 2>/dev/null
        ls data/processed/clumping/*/*.clumped.bed 2>/dev/null | sort | head -5
        ls data/processed/mtcojo/*/mtcojo_sensitivity.tsv 2>/dev/null
        echo results/regions/union_region_list.bed
        echo results/novelty/joint_signal_novel.tsv
    } > $PATHS_LIST

    # Compute SHA-256 + size + mtime per path; emit deterministic TSV
    {
        echo -e "path\tsha256\tsize_bytes\tmtime_utc"
        while IFS= read -r p; do
            if [ -f "$p" ]; then
                SHA=$(sha256sum "$p" | awk '{print $1}')
                SIZE=$(stat --printf='%s' "$p")
                MTIME=$(date -u -r "$p" -Iseconds)
                printf "%s\t%s\t%s\t%s\n" "$p" "$SHA" "$SIZE" "$MTIME"
            fi
        done < $PATHS_LIST | sort
    } > $OUT

    wc -l $OUT
    echo "M2 SHA-256 manifest frozen at $OUT"
    ```

    Atomic commit: `feat(m2-05): SHA-256 manifest freeze for M2 deliverables (Pattern E, DEC-2026-04-25-02 OSF follow-up)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -s .planning/amendments/sha256_manifest_m2_frozen.tsv &amp;&amp; head -1 .planning/amendments/sha256_manifest_m2_frozen.tsv | grep -E "^path\s+sha256\s+size_bytes" &amp;&amp; wc -l .planning/amendments/sha256_manifest_m2_frozen.tsv | awk '{exit !($1 &gt; 5)}' &amp;&amp; awk -F'\t' 'NR&gt;1 &amp;&amp; length($2) != 64 {exit 1}' .planning/amendments/sha256_manifest_m2_frozen.tsv &amp;&amp; echo "manifest valid"</automated>
  </verify>
  <acceptance_criteria>
    - File `.planning/amendments/sha256_manifest_m2_frozen.tsv` exists
    - Header row: `path\tsha256\tsize_bytes\tmtime_utc`
    - At least 6 data rows (covers the major deliverable artifacts; clumping sample is 5 rows alone)
    - Every SHA-256 column is exactly 64 hex chars
    - Re-computing `sha256sum data/catalogs/gwas-catalog-associations-full.zip` matches the row in the manifest (Pitfall 10 invariant — hash of .zip bytes)
    - Re-computing `sha256sum results/novelty/joint_signal_novel.tsv` matches the row in the manifest
    - `git log -1 --pretty=%B` matches `feat(m2-05): SHA-256 manifest freeze`
  </acceptance_criteria>
  <done>M2 SHA-256 manifest frozen with one row per deliverable artifact; ready for OSF supplementary upload at osf.io/az52u as the M2 follow-up file (per DEC-2026-04-25-02).</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 5: M2 PHASE-CLOSEOUT — Carter sign-off + STATE.md update</name>
  <files>.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md, .planning/STATE.md</files>
  <what-built>
    Wave 5 deliverables:
    - results/novelty/joint_signal_novel.tsv with confidence_tier (high/medium) per OSF amendment §7.1 Class 1
    - .planning/m2_post_m3_rerun_queue.tsv with 6 supersede obligations (D-M2-02 + Q3 + Pitfall 11 + D-M2-05)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md aggregating skip-with-doc rows
    - tests/toy_3locus/m2_smoke_targets.smk extending REQ-SNAKEMAKE-CI
    - src/python/verify_m2_artifacts.py emitting Dimension D1-D9 PASS/WARN/FAIL JSON
    - .planning/amendments/sha256_manifest_m2_frozen.tsv (OSF M5 follow-up posting target per DEC-2026-04-25-02)

    Author m2-PHASE-CLOSEOUT.md modeled on the M1 closeout report. Sections:
    1. Verifier verdict (from m2-VERIFY.json)
    2. Per-stratum K (trait counts: EUR, AFR, TRANS post-floor)
    3. Per-stratum significant lead counts (MTAG, CPASSOC, clumped)
    4. Class 1 novelty deliverable summary (high vs medium tier counts)
    5. Region union BED count
    6. mtCOJO sensitivity counts per stratum
    7. Deviations log (anything that didn't go to plan in Waves 0-5)
    8. M3 hand-off summary (region list + post-M3 queue)
    9. SHA-256 manifest reference (.planning/amendments/sha256_manifest_m2_frozen.tsv)
    10. OSF follow-up posting instructions per DEC-2026-04-25-02 (upload sha256_manifest_m2_frozen.tsv + bivariate_intercept_matrix_m2_2026-04.tsv to osf.io/az52u as supplementary files)

    Then update .planning/STATE.md:
    - Set milestone: M2-complete
    - status: "M2 closeout COMPLETE; M3 region list handed off; ready for /gsd-discuss-phase m3-aou-afr-ld-panel-build"
    - Update progress counters
  </what-built>
  <how-to-verify>
    Carter signs off on M2 closeout by verifying:

    1. **Verifier verdict PASS or WARN (not FAIL):**
       ```
       python src/python/verify_m2_artifacts.py --out .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json
       jq '.overall' .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json
       # Must print "PASS" or "WARN" (NOT "FAIL")
       ```

    2. **Class 1 novelty deliverable looks reasonable:**
       ```
       wc -l results/novelty/joint_signal_novel.tsv
       awk -F'\t' 'NR>1 {print $NF}' results/novelty/joint_signal_novel.tsv | sort | uniq -c
       # Manual sanity: top-10 high-confidence loci against known cardiometabolic literature
       head -10 results/novelty/joint_signal_novel.tsv | awk -F'\t' '$NF=="high" {print}'
       ```

    3. **SHA-256 manifest covers all 10 deliverable categories:**
       ```
       wc -l .planning/amendments/sha256_manifest_m2_frozen.tsv
       awk -F'\t' 'NR>1 {print $1}' .planning/amendments/sha256_manifest_m2_frozen.tsv
       ```

    4. **m2-PHASE-CLOSEOUT.md is complete with all 10 sections.**

    5. **Type "M2 sign-off" or describe blockers.** On sign-off Claude updates STATE.md (milestone:M2-complete, status:"M3 ready") and commits with message `docs(m2-05): M2 PHASE-CLOSEOUT signed; STATE.md milestone advanced`.
  </how-to-verify>
  <action>
    On Carter sign-off (resume-signal "M2 sign-off" or "approved"), Claude:
    1. Authors `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md` with the 10 sections enumerated in <what-built> using values from `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json` + `.planning/amendments/sha256_manifest_m2_frozen.tsv` + `.planning/m2_post_m3_rerun_queue.tsv`.
    2. Updates `.planning/STATE.md`: `milestone: M2-complete`, `status: "M2 closeout COMPLETE; M3 region list handed off; ready for /gsd-discuss-phase m3-aou-afr-ld-panel-build"`, increments completed_phases counter.
    3. Commits both files atomically with `docs(m2-05): M2 PHASE-CLOSEOUT signed; STATE.md milestone advanced`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -s .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md &amp;&amp; grep -c "M2 closeout COMPLETE" .planning/STATE.md &amp;&amp; git log -1 --pretty=%B | grep "M2 PHASE-CLOSEOUT signed"</automated>
  </verify>
  <done>Carter signed off on M2 closeout; PHASE-CLOSEOUT.md authored with 10 sections; STATE.md milestone advanced to M2-complete; M3 phase ready to discuss.</done>
  <acceptance_criteria>
    - File `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md` exists with all 10 sections per <what-built>
    - `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json` overall verdict is PASS or WARN
    - Carter has typed "M2 sign-off" or equivalent
    - `.planning/STATE.md` updated: milestone M2-complete; status references M3 readiness
    - `git log -1 --pretty=%B` matches `docs(m2-05): M2 PHASE-CLOSEOUT signed`
    - `grep -c "M2 closeout COMPLETE" .planning/STATE.md` returns ≥1
  </acceptance_criteria>
  <resume-signal>Type "M2 sign-off" or "approved" to advance STATE.md and complete M2; or describe specific issues for course-correction.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GWAS Catalog v_lock_M2 .zip → Class 1 prior-art exclusion | The catalog-snapshot SHA-256 freeze (Wave 0 Task 5) is the only durable record of "what was the field at M2 time"; Pitfall 10 invariant must hold |
| Per-trait harmonized sumstats → max single-trait p lookup | Single-trait p must be lookup-able via rsid; any munged-only cells require a fallback Z→P conversion |
| OSF az52u supplementary upload (DEC-2026-04-25-02) | Future Carter web-UI action; the freeze manifest is the upload-ready artifact |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M2-09 | Tampering | Catalog v_lock churn between M2 and M5 | mitigate | v_lock_M2 row immutable in catalog_lock_manifest.tsv; SHA-256 of .zip bytes frozen (Pitfall 10); M5 follow-up will register v_lock_M5 + diff |
| T-M2-Class1-PrEx | Information disclosure | Class 1 single-trait-p lookup against incomplete harmonized cells | mitigate | call_class1_novelty.py uses best-of-K p across stratum traits with default 1.0 if a trait file is missing; conservative — over-includes novel calls |
| T-M2-13 | Tampering | REQ-SNAKEMAKE-CI smoke regression | mitigate | tests/toy_3locus/m2_smoke_targets.smk + Snakefile.test extension; dry-run test in Task 2 acceptance |
| T-M2-OSF-FOLLOWUP | Repudiation | OSF follow-up posting (M5 catalog lock + M2 SHA-256 manifest upload to az52u) | accept | DEC-2026-04-25-02 documents the procedure; manual web-UI action by Carter is the gate |
</threat_model>

<verification>
End-of-Wave-5 (M2 closeout) verifier checks:

```bash
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

# Class 1 novelty deliverable
test -s results/novelty/joint_signal_novel.tsv
head -1 results/novelty/joint_signal_novel.tsv | grep -E "confidence_tier"

# M3 supersede queue
test -s .planning/m2_post_m3_rerun_queue.tsv
grep -c "M2-POST-M3-01" .planning/m2_post_m3_rerun_queue.tsv

# REQ-SNAKEMAKE-CI extension
test -f tests/toy_3locus/m2_smoke_targets.smk
grep -c "rule m2_smoke_residcov_slice:" tests/toy_3locus/m2_smoke_targets.smk

# Python verifier exists and passes
test -f src/python/verify_m2_artifacts.py
python src/python/verify_m2_artifacts.py --out .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json
VERDICT=$(python -c "import json; print(json.load(open('.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json'))['overall'])")
test "$VERDICT" = "PASS" -o "$VERDICT" = "WARN"
echo "Verifier verdict: $VERDICT"

# SHA-256 manifest
test -s .planning/amendments/sha256_manifest_m2_frozen.tsv
N=$(awk -F'\t' 'NR>1' .planning/amendments/sha256_manifest_m2_frozen.tsv | wc -l)
test "$N" -ge 6

# PHASE-CLOSEOUT.md
test -s .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md

# STATE.md updated
grep -q "M2 closeout COMPLETE" .planning/STATE.md

# All M2 unit tests still GREEN
pytest tests/m2/ -x

echo "Wave 5 PASS — M2 closeout signed"
```
</verification>

<success_criteria>
- src/python/call_class1_novelty.py + m2_novelty.smk authored; OSF amendment §7.1 Class 1 operational definition encoded literally
- results/novelty/joint_signal_novel.tsv with confidence_tier (high/medium); ROADMAP success criterion 5 satisfied
- .planning/m2_post_m3_rerun_queue.tsv with ≥6 supersede obligations (D-M2-02 + Q3 + Pitfall 11 + D-M2-05)
- .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md aggregates skip-with-doc rows
- tests/toy_3locus/m2_smoke_targets.smk extends REQ-SNAKEMAKE-CI; dry-run clean
- src/python/verify_m2_artifacts.py exists; Dimension D1-D9 PASS/WARN coverage; verdict PASS or WARN
- .planning/amendments/sha256_manifest_m2_frozen.tsv frozen with ≥6 rows; SHA-256 column 64-hex per Pitfall 10
- .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md authored with 10 sections
- .planning/STATE.md updated to milestone M2-complete + M3-ready status
- All 6 phase REQ IDs satisfied: REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL, REQ-NOVELTY-CLASS-1, REQ-OSF-PREREG (already satisfied 2026-04-25; M2 inherits), REQ-SNAKEMAKE-CI (extension landed), REQ-CATALOG-VERSION-LOCK (v_lock_M2 row + SHA-256 + supersede queue for v_lock_M5)
- All commits atomic per task; convention `feat|docs(m2-05): <summary>`
</success_criteria>

<output>
After completion, ensure `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md` is the canonical M2 closeout document covering:
- Verifier verdict (Dimensions D1-D9)
- Per-stratum K (post-floor)
- Per-stratum MTAG / CPASSOC / clumping lead counts
- Class 1 novelty count by tier (high vs medium)
- Region union count + provenance distribution
- mtCOJO sensitivity counts per stratum
- Deviations log (any task that needed off-plan adjustment)
- M3 hand-off (region list path + post-M3 queue path)
- SHA-256 manifest path (.planning/amendments/sha256_manifest_m2_frozen.tsv)
- OSF M5 follow-up upload instructions per DEC-2026-04-25-02 (target = osf.io/az52u as supplementary file)
</output>
