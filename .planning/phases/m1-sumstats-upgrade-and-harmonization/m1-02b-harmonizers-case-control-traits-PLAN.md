---
plan_id: m1-02b-harmonizers-case-control-traits
phase: m1
plan: 02b
type: execute
wave: 2
depends_on: [m1-00-preflight-and-environment, m1-01-portal-fetches-and-aragam-route]
autonomous: true
requirements: [REQ-TRAIT-INVENTORY, REQ-PATH-PARAMETERIZATION, REQ-SNAKEMAKE-CI]
objective: "Author 3 case-control harmonizers (T2D/DIAMANTE, stroke/GIGASTROKE, CAD/Aragam + Klarin fallback); extend harmonize_gbmi.py with opt-in b38->b37 liftover for 2022 asthma release; verify + D-16-rename Evangelou 2018 SBP-EUR pre-pivot file; freeze secondary harmonized SHA-256 manifest at wave end"
files_modified:
  - src/python/harmonize_diamante.py
  - src/python/harmonize_gigastroke.py
  - src/python/harmonize_aragam.py
  - src/python/harmonize_gbmi.py
  - src/python/verify_evangelou_sbp.py
  - src/snakemake/rules/m1_harmonize.smk
  - tests/m1/test_harmonize_diamante.py
  - tests/m1/test_harmonize_gigastroke.py
  - tests/m1/test_harmonize_aragam.py
  - tests/m1/test_harmonize_gbmi_liftover.py
  - tests/m1/test_verify_evangelou_sbp.py
  - tests/m1/fixtures/diamante_head.tsv
  - tests/m1/fixtures/gigastroke_head.tsv
  - tests/m1/fixtures/aragam_head.tsv
  - tests/m1/fixtures/klarin2018_mvp_afr_head.tsv
  - tests/m1/fixtures/gbmi_b38_head.tsv
  - tests/m1/fixtures/evangelou_b37_head.tsv
  - data/processed/sumstats_harmonized/sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz
  - data/processed/sumstats_harmonized_parquet/sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.parquet
  - data/processed/sumstats_harmonized/sha256_manifest.tsv
  - .planning/amendments/sha256_manifest_harmonized_m1.tsv
must_haves:
  truths:
    - "harmonize_diamante.py harmonizes T2D TRANS + EUR + EAS + SAS and rejects AFR/HIS (TSV rows 8 + 11 dua_pending)"
    - "harmonize_gigastroke.py loads D-02-integer-locked GCST accessions from SUMSTATS-UPGRADE.tsv at module load (defensive assertion raises if placeholders remain)"
    - "harmonize_aragam.py checks aragam_zip_manifest.txt to route branch a (AFR present) vs branch b (Klarin fallback)"
    - "harmonize_gbmi.py accepts --liftover-chain flag; Phase 09 behavior unchanged when flag omitted"
    - "verify_evangelou_sbp.py asserts b37 chromosome-length invariants before renaming pre-pivot file to D-16 naming"
    - "Secondary harmonized SHA-256 manifest present at data/processed/sumstats_harmonized/sha256_manifest.tsv AND mirrored to .planning/amendments/sha256_manifest_harmonized_m1.tsv"
    - "All 47 in-scope SUMSTATS-UPGRADE.tsv data rows (47 = current freeze; minus any DEFERRED drop) are either harmonized on disk OR explicit .deferred placeholder with stated reason — N is dynamic, not fixed at 45"
    - "W8 fix (option A): every harmonize rule (DIAMANTE/GIGASTROKE/Aragam/GBMI-asthma) prepends a universal `if [ {params.raw} = __DEFERRED__ ]` shell guard that branches on the DEFERRED_SENTINEL constant returned by m1_raw_glob.resolve_raw_for when a `.deferred` marker is present. Source-specific ad-hoc `harmonize_deferred_*` rules (DIAMANTE AFR/HIS, CAD-AFR D-03 branch-b) are RETAINED — they encode trait/source-specific fallback logic independent of the sentinel-marker path."
  artifacts:
    - path: "src/python/harmonize_diamante.py"
      provides: "DIAMANTE Mahajan 2022 T2D harmonizer (4 released ancestries)"
      min_lines: 120
    - path: "src/python/harmonize_gigastroke.py"
      provides: "GIGASTROKE Mishra 2022 all-stroke harmonizer (4-5 ancestries per D-02)"
      min_lines: 110
    - path: "src/python/harmonize_aragam.py"
      provides: "Aragam CARDIoGRAM-C4D-MVP CAD harmonizer + Klarin 2018 fallback codepath"
      min_lines: 130
    - path: "src/python/verify_evangelou_sbp.py"
      provides: "Schema + build verify + D-16 rename of pre-pivot Evangelou SBP file"
      min_lines: 70
    - path: "data/processed/sumstats_harmonized/sha256_manifest.tsv"
      provides: "Secondary harmonized SHA-256 manifest per D-13 — pipeline-reproducibility artifact"
  key_links:
    - from: "src/python/harmonize_aragam.py"
      to: "data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt"
      via: "_branch_for_afr() reads manifest at module load"
      pattern: "aragam_zip_manifest"
    - from: "src/python/harmonize_gbmi.py"
      to: "src/python/sumstats_utils.py"
      via: "liftover_to_grch37 call under --liftover-chain flag"
      pattern: "liftover_to_grch37"
    - from: "src/python/harmonize_gigastroke.py"
      to: ".planning/amendments/SUMSTATS-UPGRADE.tsv"
      via: "D-02 integer-locked accession lookup at module load"
      pattern: "SUMSTATS-UPGRADE\\.tsv"
---

<objective>
Close out Wave 2 by authoring the 3 remaining per-source harmonizers (DIAMANTE T2D, GIGASTROKE stroke, Aragam CAD) + extending the existing harmonize_gbmi.py with an opt-in b38->b37 liftover branch for the 2022 GBMI asthma release (RESEARCH pitfall #4) + schema-verifying and D-16-renaming the pre-pivot Evangelou 2018 SBP-EUR T1-spine file (`hypertension.EUR.tsv.bgz` -> `sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz`) + freezing the secondary harmonized SHA-256 manifest per D-13.

Combined with m1-02a (continuous-trait harmonizers), this plan's completion means every cell of the 45-row SUMSTATS-UPGRADE.tsv inventory is addressed: either a harmonized `.tsv.bgz + .tbi + .parquet + .qc.json` quadruple exists OR an explicit `.deferred` placeholder exists with a documented reason (DIAMANTE AFR/HIS per TSV rows 8+11; possibly MVP Giri AFR-BP pending AoU derivation per D-06).

Purpose: Wave 3 (munge + LDSC rg) gates on munged files; munged files gate on harmonized files. This plan delivers the remaining ~18 harmonized cells (T2D×4 + stroke×4-5 + CAD×3-4 + asthma×3 + sbp×1 = ~15-17 cells). The secondary SHA-256 manifest is D-13's pipeline-reproducibility artifact — re-running M1 on identical raw inputs MUST yield identical harmonized outputs, and the `sha256_manifest_harmonized_m1.tsv` committed to `.planning/amendments/` is the reference for that check.
Output: 3 new harmonizer modules + extended harmonize_gbmi + new verify_evangelou_sbp + 5 pytest modules + extended m1_harmonize.smk + renamed Evangelou file + frozen secondary harmonized SHA-256 manifest mirrored to git-tracked location.
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
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-02a-harmonizers-continuous-traits-PLAN.md
@.planning/phases/09-replication-in-independent-cohorts/09-02-PLAN.md
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@src/python/sumstats_utils.py
@src/python/harmonize_gbmi.py
@src/python/harmonize_yengo.py
@src/python/freeze_sha256_manifest.py
@config/pipeline.yaml
@CLAUDE.md

<interfaces>
```python
# Same as m1-02a — canonical schema + helpers
CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
```

Per DIAMANTE Mahajan 2022 (TRANS/EUR/EAS/SAS; AFR + HIS dua_pending per TSV rows 8 + 11):
Typical raw columns: `chromosome, position, rsID, effect_allele, other_allele,
effect_allele_frequency, beta, standard_error, pvalue, N_effective, N_case, N_control`.
N column preference: N_effective, fallback N_case + N_control.

Per GIGASTROKE Mishra 2022 (EBI FTP GWAS-Catalog harmonized format — b37 native):
Columns: `variant_id, chromosome, base_pair_location, effect_allele, other_allele,
effect_allele_frequency, beta, standard_error, p_value, n, n_cases, n_controls`.
Phenotype: all-stroke (not ischemic-only).

Per Aragam 2022 CARDIoGRAM-C4D-MVP (ZIP-unpacked; b37):
Typical RVTESTS meta columns: `MarkerName, CHR, BP, A1, A2, Freq1, Effect,
StdErr, P-value, N`. Confirm column names against actual files enumerated in
`data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt` (Wave 0 output).

D-03 branch routing:
- Branch (a, AFR in ZIP): harmonize_aragam handles TRANS + EUR + EAS + AFR.
- Branch (b, AFR absent): harmonize_aragam handles TRANS + EUR + EAS; Klarin 2018 MVP-AFR-CAD fallback handled by sibling function harmonize_aragam_klarin2018() IF Carter separately fetches Klarin files to data/raw/sumstats_v2/Klarin2018/MVP/CAD/AFR/; else AFR cell gets .deferred placeholder with reason.

Per GBMI Zhou 2022 2022 asthma release (b38 per TSV rows 18-20):
Same column shape as Phase 09 consumed earlier GBMI release (existing harmonize_gbmi.py ANCESTRY_PREFIX_MAP). Build is GRCh38 (M1 release; RESEARCH pitfall #4) → requires liftover via --liftover-chain data/external/liftover/hg38ToHg19.over.chain.gz.

Existing harmonize_gbmi.py behavior (line 116 comment):
"No liftover: GBMI flagship releases are already GRCh37." — true for Phase 09; NOT true for M1 2022 release.

Per Evangelou 2018 SBP-EUR pre-pivot T1-spine file at
`data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz`:
- b37 per TSV row 12 (RESEARCH ASSUMPTION A2 — re-verify in this plan)
- Old naming pre-D-16 (no consortium/year tokens)
- Target D-16 name: `sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz`
- phenotype_lock: "SBP continuous (mmHg), medication-adjusted"
- Trait token D-16: `sbp`

b37 chromosome max BP (for Evangelou verify guard — hg19 primary assembly):
```python
CHR_MAX_B37 = {1:249250621, 2:243199373, 3:198022430, 4:191154276,
               5:180915260, 6:171115067, 7:159138663, 8:146364022,
               9:141213431, 10:135534747, 11:135006516, 12:133851895,
               13:115169878, 14:107349540, 15:102531392, 16:90354753,
               17:81195210, 18:78077248, 19:59128983, 20:63025520,
               21:48129895, 22:51304566}
```
Any BP > CHR_MAX_B37[chr] + tolerance (1000) implies file is b38 → abort rename.
</interfaces>
</context>

<tasks>

<task id="m1-02b-T1" type="auto" tdd="true">
  <name>Task 1: harmonize_diamante.py + harmonize_gigastroke.py + harmonize_aragam.py (with D-03 branch + Klarin fallback)</name>
  <files>
    src/python/harmonize_diamante.py,
    src/python/harmonize_gigastroke.py,
    src/python/harmonize_aragam.py,
    tests/m1/test_harmonize_diamante.py,
    tests/m1/test_harmonize_gigastroke.py,
    tests/m1/test_harmonize_aragam.py,
    tests/m1/fixtures/diamante_head.tsv,
    tests/m1/fixtures/gigastroke_head.tsv,
    tests/m1/fixtures/aragam_head.tsv,
    tests/m1/fixtures/klarin2018_mvp_afr_head.tsv
  </files>
  <read_first>
    - src/python/harmonize_yengo.py (from m1-02a — copy module skeleton + CLI + .qc.json pattern verbatim)
    - src/python/harmonize_glgc.py (from m1-02a — copy header-normalization helper pattern)
    - src/python/harmonize_gbmi.py (B-2 guard + ANCESTRY_PREFIX_MAP pattern — lines 100-130)
    - src/python/sumstats_utils.py (CANONICAL_COLS + filter_palindromic_ambiguous)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv rows 6-11 (T2D) + 14-17 (stroke) + 21-24 (CAD) — copy phenotype_definition + cohort_overlap_notes verbatim into module docstrings
    - data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt (from Wave 0 — determines D-03 branch)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Klarin 2018 fetch status for branch b)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md Pattern 1 + Example 1
  </read_first>
  <behavior>
    - harmonize_diamante.py: CLI `--ancestry {TRANS,EUR,EAS,SAS}`. Rejects AFR + HIS with a clear SystemExit noting TSV rows 8 + 11 dua_pending. N column prefers N_effective, fallback N_case + N_control (stores both in .qc.json). phenotype_lock="doctor-diagnosed T2D case-control". Palindromic filter + dual emit (D-09).
    - harmonize_gigastroke.py: Loads D-02-integer-locked GCST accession -> filename map from SUMSTATS-UPGRADE.tsv at module load. Defensive guard: if any row still contains substring "GCST90104540-series" in `expected_filename`, raise RuntimeError — Wave 0 D-02 lock not committed. CLI `--ancestry {TRANS,EUR,AFR,EAS[,SAS]}`. phenotype_lock="all-stroke case-control".
    - harmonize_aragam.py: `_branch_for_afr()` reads aragam_zip_manifest.txt; returns 'a' if any of {"AFR", "African", "AA_", "_AA."} substrings present, 'b' otherwise. `harmonize_aragam()` — for ancestry=AFR + branch=b, raise NotImplementedError directing caller to Klarin fallback. Separate function `harmonize_aragam_klarin2018()` handles Klarin 2018 MVP format if data/raw/sumstats_v2/Klarin2018/MVP/CAD/AFR/ populated; else Snakemake rule writes .deferred placeholder.
    - Each harmonizer emits dual output + .qc.json sidecar.
    - pytest modules exercise (i) 10 CANONICAL_COLS output schema, (ii) palindromic drop count > 0, (iii) rejection paths (DIAMANTE AFR/HIS raise; GIGASTROKE invalid ancestry raises; Aragam branch-b AFR raises NotImplementedError with fixture manifest that lacks AFR tokens).
  </behavior>
  <action>
    (A) Create src/python/harmonize_diamante.py (modeled on harmonize_yengo.py skeleton from m1-02a):

    ```python
    #!/usr/bin/env python3
    """DIAMANTE Mahajan 2022 T2D trans + per-ancestry harmonizer (D-10).

    Source columns: chromosome, position, rsID, effect_allele, other_allele,
                    effect_allele_frequency, beta, standard_error, pvalue,
                    N_effective, N_case, N_control

    Handles TRANS + EUR + EAS + SAS. AFR + HIS strata are dua_pending per
    SUMSTATS-UPGRADE.tsv rows 8 + 11 (DIAGRAM gate on manuscript acceptance);
    Snakemake emits .deferred placeholder for those — this module refuses.
    """
    # ... full module ...
    DEFERRED_ANCESTRIES = {"AFR", "HIS"}
    DIAMANTE_COLS = {"chromosome": "CHR", "position": "BP", "rsID": "SNP",
                     "effect_allele": "EA", "other_allele": "OA",
                     "effect_allele_frequency": "EAF",
                     "beta": "BETA", "standard_error": "SE", "pvalue": "P",
                     "N_effective": "N"}
    # _main asserts args.ancestry not in DEFERRED_ANCESTRIES; raises SystemExit otherwise.
    ```

    (B) Create src/python/harmonize_gigastroke.py with the D-02 integer-lock loader:

    ```python
    import pandas as pd
    from pathlib import Path
    _TSV = Path(".planning/amendments/SUMSTATS-UPGRADE.tsv")
    if _TSV.exists():
        _tsv_df = pd.read_csv(_TSV, sep="\t")
        _GIGASTROKE = _tsv_df[_tsv_df["source_consortium"] == "GIGASTROKE"].copy()
        for _, _row in _GIGASTROKE.iterrows():
            _fn = str(_row["expected_filename"])
            if "GCST90104540-series" in _fn:
                raise RuntimeError(
                    f"GIGASTROKE ancestry={_row['ancestry']}: filename still has "
                    f"placeholder '{_fn}'. Wave 0 D-02 lock not committed. "
                    f"Fix .planning/amendments/SUMSTATS-UPGRADE.tsv before running.")
        GIGASTROKE_FILENAMES = dict(zip(_GIGASTROKE["ancestry"],
                                        _GIGASTROKE["expected_filename"]))
    else:
        GIGASTROKE_FILENAMES = {}  # tests may pass fixture manifest

    GIGASTROKE_COLS = {"variant_id": "SNP", "chromosome": "CHR",
                       "base_pair_location": "BP",
                       "effect_allele": "EA", "other_allele": "OA",
                       "effect_allele_frequency": "EAF",
                       "beta": "BETA", "standard_error": "SE",
                       "p_value": "P", "n": "N"}
    ```

    (C) Create src/python/harmonize_aragam.py:

    ```python
    from pathlib import Path

    def _branch_for_afr(manifest: Path = Path("data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt")) -> str:
        if not manifest.exists():
            raise FileNotFoundError(
                f"D-03 aragam_zip_manifest.txt missing at {manifest}; Wave 0 unzip not performed")
        text = manifest.read_text()
        afr_tokens = ("AFR", "African", "AA_", "_AA.")
        return "a" if any(tok in text for tok in afr_tokens) else "b"

    ARAGAM_COLS = {"MarkerName": "SNP", "CHR": "CHR", "BP": "BP",
                   "A1": "EA", "A2": "OA", "Freq1": "EAF",
                   "Effect": "BETA", "StdErr": "SE", "P-value": "P", "N": "N"}

    KLARIN_COLS = {"CHROM": "CHR", "POS": "BP", "ID": "SNP",
                   "REF": "OA", "ALT": "EA", "AF": "EAF",
                   "BETA": "BETA", "SE": "SE", "P": "P"}
    # Klarin N column computed from N_case + N_ctrl if both present.

    def harmonize_aragam(input_path, ..., ancestry, ...):
        if ancestry == "AFR":
            branch = _branch_for_afr()
            if branch == "b":
                raise NotImplementedError(
                    "D-03 branch b: Aragam AFR absent from ZIP manifest. "
                    "Use harmonize_aragam_klarin2018 or Snakemake .deferred.")
        # standard col map + palindromic + dual emit

    def harmonize_aragam_klarin2018(input_path, ..., chain_file=None):
        # Klarin 2018 MVP-AFR-CAD; b37 native typically; handles COL_MAP variants
        ...
    ```

    (D) Create 4 synthetic fixture TSVs under tests/m1/fixtures/:
    - diamante_head.tsv: 100 rows with DIAMANTE column names, 4 palindromic.
    - gigastroke_head.tsv: 100 rows with GWAS-Catalog harmonized column names, 4 palindromic.
    - aragam_head.tsv: 100 rows with CARDIoGRAM RVTESTS columns, 4 palindromic.
    - klarin2018_mvp_afr_head.tsv: 100 rows with MVP format columns.

    (E) Author 3 pytest modules:
    - test_harmonize_diamante.py: runs harmonizer on TRANS + EUR + EAS + SAS fixtures (4 tests), then runs with --ancestry AFR and asserts SystemExit raised.
    - test_harmonize_gigastroke.py: runs with TRANS fixture, asserts schema. Separately tests the D-02 placeholder guard by writing a fixture SUMSTATS-UPGRADE.tsv with placeholder in expected_filename and asserting RuntimeError on module import.
    - test_harmonize_aragam.py: writes a fixture aragam_zip_manifest.txt (a) WITH "AFR" token — assert branch a routes to harmonize; (b) without AFR token — assert NotImplementedError for ancestry=AFR.

    (F) Extend src/snakemake/rules/m1_harmonize.smk with rules for DIAMANTE (TRANS/EUR/EAS/SAS), GIGASTROKE (TRANS/EUR/AFR/EAS per D-02), Aragam (TRANS/EUR/EAS + conditional AFR per D-03 branch). B4 fix: every harmonize rule's input raw-file path is resolved via `params: raw=lambda wc: resolve_raw_for(f"<SOURCE_TAG>_<trait>_{wc.ancestry}", wc.ancestry)` (NOT an ad-hoc lambda; NOT a placeholder). Import at top of m1_harmonize.smk: `from m1_raw_glob import resolve_raw_for`. Source tags: `DIAMANTE2022_T2D_<ancestry>`, `GIGASTROKE2022_stroke_<ancestry>`, `Aragam2022_CAD_<ancestry>` (note Aragam ZIP unpacking yields per-ancestry subset filenames). Shell uses `--input {params.raw}`. W8 fix (option A): every shell body MUST start with the universal .deferred guard `if [ "{params.raw}" = "__DEFERRED__" ]; then mkdir -p $(dirname {output[0]}); touch {output[0]}.deferred && echo "DEFERRED: upstream marker present" && exit 0; fi` BEFORE invoking the harmonizer. The source-specific DEFERRED rule pattern below for DIAMANTE AFR + HIS (and conditional CAD-AFR branch-b Klarin) is RETAINED — it encodes source-specific DUA-pending and branch-routing logic, not sentinel handling, and is independent of the universal-guard path:

    ```python
    rule harmonize_deferred_diamante_afr:
        output: os.path.join(HARM_DIR, "t2d.AFR.DIAMANTE.2022.GRCh37.tsv.bgz.deferred"),
        shell: r'''
            mkdir -p $(dirname {output})
            cat > {output} <<EOF
        Status: DEFERRED
        Trait: t2d, Ancestry: AFR, Consortium: DIAMANTE, Year: 2022
        Reason: SUMSTATS-UPGRADE.tsv row 8 status=dua_pending; DIAGRAM gate on manuscript acceptance
        Recheck: quarterly per m1-CONTEXT.md Deferred Ideas
        EOF
        '''
    ```

    Apply the same pattern to `t2d.HIS.DIAMANTE.2022` and conditionally to `cad.AFR.*` (branch b) and `hypertension.AFR.MVP.Giri.2019` (if D-06 fallback pending).

    Run:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest \
      tests/m1/test_harmonize_diamante.py tests/m1/test_harmonize_gigastroke.py \
      tests/m1/test_harmonize_aragam.py -x --tb=short
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
      -s workflow/Snakefile --dry-run --cores 1 2>&1 | grep -E "harmonize_(diamante|gigastroke|aragam)" | head
    ```
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_diamante.py tests/m1/test_harmonize_gigastroke.py tests/m1/test_harmonize_aragam.py -x --tb=short 2>&amp;1 | tail -5 &amp;&amp; test -f src/python/harmonize_diamante.py &amp;&amp; test -f src/python/harmonize_gigastroke.py &amp;&amp; test -f src/python/harmonize_aragam.py &amp;&amp; grep -q "_branch_for_afr" src/python/harmonize_aragam.py &amp;&amp; grep -q "GCST90104540-series" src/python/harmonize_gigastroke.py</automated>
  </verify>
  <done>3 harmonizer modules created; each defines harmonize_&lt;source&gt;() + _main(); 3 pytest modules pass; harmonize_gigastroke.py contains the defensive placeholder guard (grep matches the warning string, not a hardcoded accession); harmonize_aragam.py defines _branch_for_afr() helper; m1_harmonize.smk declares rules for all 3 + DEFERRED placeholders.</done>
</task>

<task id="m1-02b-T2" type="auto" tdd="true">
  <name>Task 2: Extend harmonize_gbmi.py (liftover flag) + verify_evangelou_sbp.py + freeze secondary harmonized SHA-256 manifest</name>
  <files>
    src/python/harmonize_gbmi.py,
    src/python/verify_evangelou_sbp.py,
    tests/m1/test_harmonize_gbmi_liftover.py,
    tests/m1/test_verify_evangelou_sbp.py,
    tests/m1/fixtures/gbmi_b38_head.tsv,
    tests/m1/fixtures/evangelou_b37_head.tsv,
    src/snakemake/rules/m1_harmonize.smk,
    data/processed/sumstats_harmonized/sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz,
    data/processed/sumstats_harmonized/sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz.tbi,
    data/processed/sumstats_harmonized_parquet/sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.parquet,
    data/processed/sumstats_harmonized/qc_log/sbp.EUR.Evangelou-ICBP-UKBB.2018.qc.json,
    data/processed/sumstats_harmonized/sha256_manifest.tsv,
    .planning/amendments/sha256_manifest_harmonized_m1.tsv
  </files>
  <read_first>
    - src/python/harmonize_gbmi.py (entire file — 154 lines; line 116 is the "GRCh37" assertion to extend)
    - src/python/sumstats_utils.py (liftover_to_grch37 signature + validate_canonical_frame)
    - src/python/freeze_sha256_manifest.py (from m1-01 Task 1 — reuse for secondary manifest rule)
    - data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz (pre-pivot Evangelou T1-spine input — N2 fix moved the zcat probe instruction to action (B))
    - .planning/amendments/SUMSTATS-UPGRADE.tsv row 12 (Evangelou metadata — phenotype_definition, cohort_overlap)
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-RESEARCH.md Pitfall #4 (GBMI b38 liftover) + Pitfall #7 (chain-file guard) + Assumption A2 (Evangelou schema)
  </read_first>
  <behavior>
    - harmonize_gbmi.py gains a new CLI `--liftover-chain <path>` flag. When set AND basename of path contains "hg38ToHg19", the module calls sumstats_utils.liftover_to_grch37() after the column rename but BEFORE the palindromic filter. When unset, Phase 09 behavior preserved exactly (no liftover; downstream Phase 09 regression tests keep passing).
    - Chain-file guard (RESEARCH Pitfall #7): if --liftover-chain is set but basename lacks "hg38ToHg19", raise ValueError — prevents silent wrong-direction lift.
    - Line 116 comment extended: "GBMI flagship releases 2020-2021 are GRCh37; M1 2022 release is GRCh38 and requires --liftover-chain data/external/liftover/hg38ToHg19.over.chain.gz per DEC-2026-04-24-01."
    - verify_evangelou_sbp.py: reads pre-pivot hypertension.EUR.tsv.bgz, invokes sumstats_utils.validate_canonical_frame, spot-checks all BP <= CHR_MAX_B37[chr] with tolerance 1000, spot-checks EAF in [0,1] and P in [0,1], then on pass copies to D-16-named target + builds .parquet + writes .qc.json. On fail raises AssertionError listing specific defects.
    - m1_freeze_harmonized_sha256_manifest Snakemake rule runs after all harmonize_* rules (collect via a checkpoint rule or static input list). Invokes freeze_sha256_manifest.py --root data/processed/sumstats_harmonized --out data/processed/sumstats_harmonized/sha256_manifest.tsv --no-mtime --skip-glob "*.deferred,qc_log/*,sha256_manifest.tsv" then mirror-copies to .planning/amendments/sha256_manifest_harmonized_m1.tsv.
  </behavior>
  <action>
    (A) Edit src/python/harmonize_gbmi.py. Add `--liftover-chain` argument in _main():

    ```python
    ap.add_argument("--liftover-chain", type=Path, default=None,
        help="If set, liftover b38->b37 using this chain. For the 2022 GBMI asthma "
             "release. Path basename must contain 'hg38ToHg19' (guard against Pitfall #7).")
    ```

    Just after the `df = df[CANONICAL_COLS]` line (existing line ~114) and BEFORE `df = _su.filter_palindromic_ambiguous(df)`:

    ```python
    if args.liftover_chain is not None:
        chain_path = Path(args.liftover_chain)
        if "hg38ToHg19" not in chain_path.name:
            raise ValueError(
                f"--liftover-chain expects hg38ToHg19 chain; got '{chain_path.name}'. "
                f"Use data/external/liftover/hg38ToHg19.over.chain.gz. "
                f"Guards against Pitfall #7 silent wrong-direction lift.")
        df, qc_lift = _su.liftover_to_grch37(
            df, chain_file=str(chain_path),
            chr_col="CHR", bp_col="BP", max_drop_rate=0.05)
        print(f"[gbmi] liftover b38->b37 qc: {qc_lift}", file=sys.stderr)
    ```

    Update the existing line-116 comment to: "GBMI flagship releases 2020-2021 are GRCh37; M1 2022 release is GRCh38 and requires --liftover-chain per DEC-2026-04-24-01. See Pitfall #4."

    (B) Pre-step (N2 fix): before authoring verify_evangelou_sbp.py, probe the pre-pivot file to confirm column order and sample SBP values are plausible b37 coordinates:
    ```bash
    zcat data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz | head -20
    ```
    Inspect the column header against CANONICAL_COLS and spot-check 1-5 BP values against CHR_MAX_B37 (defined in m1-02b context block). If anything looks off (column order differs, BP > 250M, SNP IDs missing), STOP and resolve before authoring verify — verify_evangelou_sbp.py assumes a b37 10-col TSV.

    Then create src/python/verify_evangelou_sbp.py:

    ```python
    #!/usr/bin/env python3
    """D-10 + D-16 verify + rename of pre-pivot Evangelou 2018 SBP-EUR T1-spine file.

    Asserts hypertension.EUR.tsv.bgz is (a) GRCh37 (all BP <= chrom max), (b) 10-col
    canonical schema, (c) EAF/P in valid ranges. On pass: copies to D-16 name
    sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz + .tbi + builds .parquet + .qc.json.
    On fail: raises AssertionError; target not written.
    """
    from __future__ import annotations
    import argparse, json, shutil, sys
    from pathlib import Path
    import pandas as pd

    HERE = Path(__file__).resolve().parent
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    import sumstats_utils as _su

    CHR_MAX_B37 = {1:249250621, 2:243199373, 3:198022430, 4:191154276,
                   5:180915260, 6:171115067, 7:159138663, 8:146364022,
                   9:141213431, 10:135534747, 11:135006516, 12:133851895,
                   13:115169878, 14:107349540, 15:102531392, 16:90354753,
                   17:81195210, 18:78077248, 19:59128983, 20:63025520,
                   21:48129895, 22:51304566}
    TOL_BP = 1000  # forgive ~1kb rounding

    def verify_and_rename(source: Path, target_tsv_bgz: Path,
                          target_parquet: Path, target_qc: Path) -> dict:
        df = pd.read_csv(source, sep="\t", compression="infer", low_memory=False)
        _su.validate_canonical_frame(df)
        def _chrom_int(c):
            c = str(c).replace("chr", "")
            try: return int(c)
            except ValueError: return None
        df["_chr_i"] = df["CHR"].map(_chrom_int)
        over_rows = []
        for chrom, max_bp in CHR_MAX_B37.items():
            sub = df[df["_chr_i"] == chrom]
            over = sub[sub["BP"] > max_bp + TOL_BP]
            if len(over) > 0:
                over_rows.append((chrom, len(over)))
        if over_rows:
            raise AssertionError(
                f"Evangelou build verify FAILED: BP > b37 max on "
                f"{over_rows}. File may be b38 — aborting rename.")
        assert df["EAF"].between(0, 1).all(), "EAF out of [0,1]"
        assert df["P"].between(0, 1).all(),   "P out of [0,1]"
        df = df.drop(columns=["_chr_i"])
        target_tsv_bgz.parent.mkdir(parents=True, exist_ok=True)
        target_parquet.parent.mkdir(parents=True, exist_ok=True)
        target_qc.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_tsv_bgz)
        tbi_src = source.parent / (source.name + ".tbi")
        tbi_dst = target_tsv_bgz.parent / (target_tsv_bgz.name + ".tbi")
        if tbi_src.exists(): shutil.copy2(tbi_src, tbi_dst)
        df.to_parquet(target_parquet, index=False, compression="snappy")
        qc = {"source": str(source), "n_rows": int(len(df)),
              "build_verified": "GRCh37",
              "phenotype_lock": "SBP continuous (mmHg), medication-adjusted",
              "d16_name": target_tsv_bgz.name,
              "schema_valid": True}
        target_qc.write_text(json.dumps(qc, indent=2))
        return qc

    def _main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--source", type=Path,
            default=Path("data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz"))
        ap.add_argument("--target-tsv-bgz", type=Path, required=True)
        ap.add_argument("--target-parquet",  type=Path, required=True)
        ap.add_argument("--target-qc",       type=Path, required=True)
        args = ap.parse_args()
        qc = verify_and_rename(args.source, args.target_tsv_bgz,
                                args.target_parquet, args.target_qc)
        print(json.dumps(qc, indent=2))

    if __name__ == "__main__":
        _main()
    ```

    (C) Author tests/m1/test_harmonize_gbmi_liftover.py. Fixture gbmi_b38_head.tsv: 100 rows with realistic b38 positions (e.g. chr1:100_000..200_000) using the GBMI column names per ANCESTRY_PREFIX_MAP. Test:
    - Case 1: harmonize with --liftover-chain pointing to staged hg38ToHg19.over.chain.gz — assert output file exists, assert .qc-like stderr line shows non-zero drop count below 5% threshold.
    - Case 2: harmonize WITHOUT --liftover-chain — assert output schema matches (Phase 09 regression; should be unchanged).
    - Case 3: --liftover-chain pointing to a path with "hg19ToHg38" in name — assert ValueError raised.

    (D) Author tests/m1/test_verify_evangelou_sbp.py. Fixture evangelou_b37_head.tsv: 10 rows at valid b37 coordinates; test invokes verify_and_rename into tmp_path; asserts target exists + parquet exists + qc.json contains `build_verified=GRCh37`. Failing-case fixture with chr1:260_000_000 (> 249M b37 max); asserts AssertionError raised + no target file written.

    (E) Extend src/snakemake/rules/m1_harmonize.smk with:

    ```python
    # B4 fix: resolve_raw_for replaces <resolved_raw_glob> placeholder.
    # W8 fix: universal .deferred guard at shell prelude branches on DEFERRED_SENTINEL.
    # Top of m1_harmonize.smk: `from m1_raw_glob import resolve_raw_for`
    rule harmonize_gbmi_asthma:
        """Per-ancestry GBMI asthma; all three call harmonize_gbmi with --liftover-chain."""
        input:
            flag  = os.path.join(RAW_DIR, ".download_complete.GBMI2022_asthma_{ancestry}"),
            chain = CHAIN_B38_TO_B37,
        output:
            tsv_bgz = os.path.join(HARM_DIR, "asthma.{ancestry}.GBMI.2022.GRCh37.tsv.bgz"),
            tbi     = os.path.join(HARM_DIR, "asthma.{ancestry}.GBMI.2022.GRCh37.tsv.bgz.tbi"),
            parquet = os.path.join(PARQ_DIR, "asthma.{ancestry}.GBMI.2022.GRCh37.parquet"),
            qc_json = os.path.join(HARM_DIR, "qc_log/asthma.{ancestry}.GBMI.2022.qc.json"),
        wildcard_constraints: ancestry="(MULTI|EUR|AFR)",
        params:
            raw = lambda wc: resolve_raw_for(f"GBMI2022_asthma_{wc.ancestry}", wc.ancestry),
        conda: "../../envs/m1-harmonize.yml"
        resources: mem_mb=12000, runtime=2880
        shell:
            r"""
            # W8 fix (option A): universal .deferred guard. Closes any PENDING_*
            # sentinel path symmetrically; emits .deferred output marker and exits 0.
            if [ "{params.raw}" = "__DEFERRED__" ]; then
                mkdir -p $(dirname {output.tsv_bgz})
                touch {output.tsv_bgz}.deferred
                echo "DEFERRED: upstream marker present for GBMI2022_asthma_{wildcards.ancestry}"
                exit 0
            fi
            python src/python/harmonize_gbmi.py \
                --input {params.raw} \
                --output-prefix {HARM_DIR}/asthma.{wildcards.ancestry}.GBMI.2022.GRCh37.tmp \
                --trait asthma --ancestry {wildcards.ancestry} \
                --liftover-chain {input.chain} \
                --qc-json {output.qc_json}
            zcat {HARM_DIR}/asthma.{wildcards.ancestry}.GBMI.2022.GRCh37.tmp_*.tsv.gz | bgzip -c > {output.tsv_bgz}
            tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
            # parquet emitted by harmonize_gbmi.py directly at {output.parquet}
            """

    rule verify_evangelou_sbp:
        input: os.path.join(HARM_DIR, "hypertension.EUR.tsv.bgz"),
        output:
            tsv_bgz = os.path.join(HARM_DIR, "sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz"),
            parquet = os.path.join(PARQ_DIR, "sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.parquet"),
            qc_json = os.path.join(HARM_DIR, "qc_log/sbp.EUR.Evangelou-ICBP-UKBB.2018.qc.json"),
        conda: "../../envs/m1-harmonize.yml"
        shell:
            "python src/python/verify_evangelou_sbp.py "
            "--source {input} --target-tsv-bgz {output.tsv_bgz} "
            "--target-parquet {output.parquet} --target-qc {output.qc_json}"

    rule m1_freeze_harmonized_sha256_manifest:
        input: HARM_ALL_FLAG = os.path.join(HARM_DIR, ".all_harmonize_complete"),
        output:
            manifest = os.path.join(HARM_DIR, "sha256_manifest.tsv"),
            mirror   = ".planning/amendments/sha256_manifest_harmonized_m1.tsv",
        conda: "../../envs/m1-download.yml"
        shell:
            r"""
            python src/python/freeze_sha256_manifest.py \
                --root {HARM_DIR} --out {output.manifest} --no-mtime \
                --skip-glob "*.deferred,qc_log/*,sha256_manifest.tsv,.all_harmonize_complete"
            cp {output.manifest} {output.mirror}
            """
    ```

    (F) B4 fix: m1_raw_glob.resolve_raw_for(source_tag, ancestry) is the canonical raw-path resolver, authored as the (A0) sub-task of m1-02a-T2. The harmonize_gbmi_asthma rule above already uses `params.raw = lambda wc: resolve_raw_for(...)`. The harmonize rules for DIAMANTE / GIGASTROKE / Aragam authored in m1-02b-T1 step (F) MUST use the same pattern (NOT a separate ad-hoc helper). Required imports at top of src/snakemake/rules/m1_harmonize.smk: `from m1_raw_glob import resolve_raw_for`. W8 fix (option A — universal .deferred guard): every harmonize rule (m1-02a yengo/glgc/wuttke/magic AND m1-02b diamante/gigastroke/aragam/gbmi_asthma) MUST prepend the universal shell prelude `if [ "{params.raw}" = "__DEFERRED__" ]; then mkdir -p $(dirname {output[0]}); touch {output[0]}.deferred && echo "DEFERRED: upstream marker present" && exit 0; fi` to the shell body. resolve_raw_for returns the module-level `DEFERRED_SENTINEL = "__DEFERRED__"` constant when a `.deferred` marker is present in the resolved target_dir (Loh PENDING_D01_ACCESSION from m1-01 N1 fix, OR future PENDING_* sentinels). This single choke-point change closes Loh-EUR, Loh-AFR, AND any future deferred-by-marker path symmetrically; no per-source ad-hoc `harmonize_deferred_loh_{ancestry}` rules are needed. The existing source-specific ad-hoc rules in m1-02b-T1 step (F) — `harmonize_deferred_diamante_afr`, `harmonize_deferred_diamante_his`, and conditional CAD-AFR D-03 branch-b Klarin fallback — are RETAINED because they encode source-specific fallback logic (DUA gating, branch routing) independent of the sentinel-marker path.

    Run tests + optional live verify:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest \
      tests/m1/test_harmonize_gbmi_liftover.py tests/m1/test_verify_evangelou_sbp.py \
      -x --tb=short
    # If pre-pivot Evangelou exists, smoke the verify:
    if [ -f data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz ]; then
      /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python src/python/verify_evangelou_sbp.py \
        --target-tsv-bgz data/processed/sumstats_harmonized/sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz \
        --target-parquet data/processed/sumstats_harmonized_parquet/sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.parquet \
        --target-qc data/processed/sumstats_harmonized/qc_log/sbp.EUR.Evangelou-ICBP-UKBB.2018.qc.json
    fi
    ```
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_gbmi_liftover.py tests/m1/test_verify_evangelou_sbp.py -x --tb=short 2>&amp;1 | tail -5 &amp;&amp; grep -q "liftover-chain" src/python/harmonize_gbmi.py &amp;&amp; grep -q "hg38ToHg19" src/python/harmonize_gbmi.py &amp;&amp; test -f src/python/verify_evangelou_sbp.py &amp;&amp; grep -q "m1_freeze_harmonized_sha256_manifest" src/snakemake/rules/m1_harmonize.smk &amp;&amp; grep -q "verify_evangelou_sbp" src/snakemake/rules/m1_harmonize.smk &amp;&amp; grep -q "__DEFERRED__" src/snakemake/rules/m1_harmonize.smk</automated>
  </verify>
  <done>harmonize_gbmi.py accepts --liftover-chain with hg38ToHg19 guard (no regression when flag omitted); verify_evangelou_sbp.py passes pytest on synthetic fixtures (both success + failing-chr1 cases); m1_harmonize.smk declares harmonize_gbmi_asthma + verify_evangelou_sbp + m1_freeze_harmonized_sha256_manifest rules; when executed, the frozen secondary SHA-256 manifest is reproducible and mirrored to .planning/amendments/.</done>
</task>

</tasks>

<threat_model>
security_enforcement disabled — data-transformation plan with no user input, no network at harmonize time (files on disk from Wave 1), no secrets. GBMI liftover guard (reject wrong-direction chain) is a data-correctness control, not security.
</threat_model>

<verification>
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest \
  tests/m1/test_harmonize_diamante.py tests/m1/test_harmonize_gigastroke.py \
  tests/m1/test_harmonize_aragam.py tests/m1/test_harmonize_gbmi_liftover.py \
  tests/m1/test_verify_evangelou_sbp.py -x --tb=short \
  && test -f src/python/harmonize_diamante.py \
  && test -f src/python/harmonize_gigastroke.py \
  && test -f src/python/harmonize_aragam.py \
  && test -f src/python/verify_evangelou_sbp.py \
  && grep -q "liftover-chain" src/python/harmonize_gbmi.py \
  && grep -q "hg38ToHg19" src/python/harmonize_gbmi.py \
  && grep -q "verify_evangelou_sbp" src/snakemake/rules/m1_harmonize.smk \
  && grep -q "m1_freeze_harmonized_sha256_manifest" src/snakemake/rules/m1_harmonize.smk \
  && ! grep -r "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/harmonize_diamante.py src/python/harmonize_gigastroke.py src/python/harmonize_aragam.py src/python/verify_evangelou_sbp.py
</verification>

<success_criteria>
- 3 case-control harmonizer modules under src/python/ with _main() + typed harmonize_*() entry points
- harmonize_gbmi.py accepts --liftover-chain with hg38ToHg19 guard; Phase 09 regression unchanged when flag omitted
- verify_evangelou_sbp.py enforces b37 chromosome-length invariants + schema before renaming
- 5 pytest modules under tests/m1/ all pass (including Aragam branch routing + DIAMANTE ancestry rejection + GBMI liftover guard + Evangelou b37 spot-check)
- src/snakemake/rules/m1_harmonize.smk declares rules for DIAMANTE (4 ancestries + 2 DEFERRED), GIGASTROKE (4 ancestries), Aragam (3-4 ancestries per D-03), GBMI asthma (3 ancestries with liftover), verify_evangelou_sbp, + m1_freeze_harmonized_sha256_manifest
- Secondary harmonized SHA-256 manifest at `data/processed/sumstats_harmonized/sha256_manifest.tsv` + mirror at `.planning/amendments/sha256_manifest_harmonized_m1.tsv`
- REQ-PATH-PARAMETERIZATION: `grep -r "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/harmonize_{diamante,gigastroke,aragam}.py src/python/verify_evangelou_sbp.py` returns 0
- All in-scope cells (N = line count of trait_keys.txt; current freeze 47 minus DEFERRED) have a harmonized artifact quadruple (.tsv.bgz + .tbi + .parquet + .qc.json)
</success_criteria>

<output>
After completion, create `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-02b-SUMMARY.md` with:
- 3 new harmonizer module line counts + function signatures
- harmonize_gbmi.py line-116 comment diff + --liftover-chain flag addition
- verify_evangelou_sbp.py build-verification outcome on the pre-pivot file
- Per-rule DAG coverage: TRANS/EUR/AFR/EAS/SAS/HIS × {t2d, stroke, cad, asthma, sbp} matrix with status LANDED / DEFERRED
- Secondary harmonized SHA-256 manifest row count + sha256-of-sha256s (meta hash)
- Evidence that repeated freeze-manifest invocations yield byte-identical TSV
</output>
</content>
</invoke>