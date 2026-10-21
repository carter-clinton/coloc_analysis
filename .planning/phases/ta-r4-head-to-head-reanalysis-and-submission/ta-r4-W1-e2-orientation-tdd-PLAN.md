---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 6
slug: W1-e2-orientation-tdd
type: tdd
wave: 6
depends_on: ["ta-r4-W0d-pair-coloc-r4-script"]
files_modified:
  - src/python/ta_r4/restore_bmi_alleles.py
  - src/snakemake/scripts/plink_ld_to_rds.R
  - src/snakemake/scripts/run_qtl_coloc.R
  - tests/ta_r4/test_bmi_allele_restoration.py
  - tests/ta_r4/test_plink_ld_to_rds_ref_alt.py
  - tests/ta_r4/test_qtl_orient.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/bmi_allele_restoration_report.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz carries REF/ALT/EAF restored from the same Yengo 2018 release; BETA/SE/P/N/POS/SNP_ID strings are byte-identical to the frozen bmi.EUR.tsv.bgz for every kept row; the report reconciles n_frozen = exact + flipped + value_mismatch + unjoined (D-18)"
    - "Both inputs are sha256-verified against .planning/amendments/sha256_manifest_harmonized_m1.tsv before use, and the output sha256 is committed"
    - "plink_ld_to_rds.R --emit-ref-alt adds REF := A2, ALT := A1 from the same run's .bim; without the flag its output object is identical() to the pre-change script's output (D-06 unit 2; D-15)"
    - "A plink 1.9 --keep-allele-order --r square known-answer shows the LD sign equals the Pearson correlation of A1 dosages, so ALT := A1 is the correct label for the sign convention"
    - "run_qtl_coloc.R --qtl-orient true negates QTL beta for transposed alleles, drops palindromic/mismatch/unparseable rows and writes qtl_orient_* counters; --qtl-orient false (the default) produces output identical to the pre-change script (D-06 unit 3; D-15)"
    - "All pre-existing tests/m3 and tests/phase2 outcomes are unchanged (AFR/Track B paths byte-identical at default flags)"
  artifacts:
    - path: "src/python/ta_r4/restore_bmi_alleles.py"
      provides: "checksum-pinned BMI allele restoration with match-rate report"
    - path: "tests/ta_r4/test_plink_ld_to_rds_ref_alt.py"
      provides: "unit 2 tests incl. plink sign known-answer and the flag-off identical() proof"
    - path: "tests/ta_r4/test_qtl_orient.py"
      provides: "unit 3 tests: exact/transposed/palindromic/mismatch + flag-off identity"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/bmi_allele_restoration_report.tsv"
      provides: "D-18 match-rate report (disclosed in W4a and W8a)"
  key_links:
    - from: "src/python/ta_r4/paths.py::sumstats_path('bmi','EUR', r4 arm)"
      to: "data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz"
      via: "R4 fit rule input"
      pattern: "r4_alleles"
    - from: "run_qtl_coloc.R --qtl-orient"
      to: "QTL beta"
      via: "orient_qtl multiplier computed from the QTL's own variant_id REF/ALT vs the panel REF/ALT"
      pattern: "qtl-orient"
---

<objective>
Wave 1 fixes the E-2 allele-orientation defect for the R4 EUR pipeline in three TDD units, each
default-off or additive so Track B cannot move:
(1) restore BMI REF/ALT from the same release;
(2) let the EUR panel carry REF/ALT signed under `--keep-allele-order`;
(3) orient QTL betas to the panel with the QTL's own alleles.
Every unit is RED first, with an observed negative control, and the flag-off identity is proven
against the pre-change script.

Purpose: D-06 (fix + before/after), D-18 (BMI restoration with a match-rate report), D-15.
Output: three code units, three test modules, the restored BMI file on /rs1, and committed
sha256 + match-rate manifests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W0b2-pair-manifest-osf-gate-workflow-SUMMARY.md

<interfaces>
Frozen BMI file (no alleles): data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz
  header: CHR POS BETA SE P N SNP_ID TRAIT ANCESTRY BUILD   (2,327,244 rows per research)
Source with alleles: data/processed/sumstats_harmonized/bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz
  (2,336,269 rows; EA/OA/EAF per research; sha256 0147fbcd… in .planning/amendments/sha256_manifest_harmonized_m1.tsv)
Independent cross-check: /rs1/.../region_analysis/data_raw/sumstats/bmi.EUR.raw.gz (Tested_Allele / Other_Allele)
Target header (as hypertension.EUR): CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD
plink_ld_to_rds.R options: --ld --variants --region-id --ancestry (default AFR) --ld-source --output;
  the .bim branch builds variants = data.frame(SNP_ID, CHR, POS, A1 = bim[[5]], A2 = bim[[6]])
run_qtl_coloc.R: options at lines 30-75; allele-join block ~440-480 computes join$orient (catalog->panel) and
  deliberately does NOT apply it. QTL variant_id format chr{c}_{pos}_{ref}_{alt} (GRCh38; config/qtl_sources.yaml:28);
  beta is signed on that ALT.
Existing guards to keep green: tests/m3/test_qtl_coloc_allele_join.py, tests/m3/test_qtl_coloc_ld_resolution.py,
  tests/phase2/test_run_qtl_coloc.py, tests/m3/test_ld_npz_to_rds.py
R4 PLINK binary: R4_PLINK recorded in the W0b2 SUMMARY (plink 1.90b6.21 from envs/plink.yml)
</interfaces>
</context>

<feature>
  <name>E-2 orientation fix: BMI alleles, panel REF/ALT, QTL-beta orientation</name>
  <files>src/python/ta_r4/restore_bmi_alleles.py, src/snakemake/scripts/plink_ld_to_rds.R, src/snakemake/scripts/run_qtl_coloc.R, tests/ta_r4/test_bmi_allele_restoration.py, tests/ta_r4/test_plink_ld_to_rds_ref_alt.py, tests/ta_r4/test_qtl_orient.py</files>
  <behavior>
    Unit 1 (BMI), fixture: 8 frozen rows × source rows.
    - Classes: exact (source BETA == frozen BETA numerically at the frozen string's precision, same SE and P) → REF=OA, ALT=EA, EAF=source EAF; flipped (source BETA == −frozen BETA, same SE/P) → REF=EA, ALT=OA, EAF=1−source EAF; value_mismatch → dropped; unjoined (no CHR+POS+SNP_ID match) → dropped
    - Kept rows keep the frozen BETA/SE/P/N strings byte-for-byte
    - The report reconciles n_frozen = n_exact + n_flipped + n_value_mismatch + n_unjoined
    - Wrong input sha256 → exit 2 before reading data
    Unit 2 (panel):
    - Without --emit-ref-alt, identical(readRDS(new), readRDS(old)) on fixtures; old = `git show HEAD:src/snakemake/scripts/plink_ld_to_rds.R` saved to tmp
    - With --emit-ref-alt (.bim input): variants$REF == A2 and variants$ALT == A1; with a .pvar input it stops with "--emit-ref-alt requires .bim"
    - Known answer: a 6-sample × 3-SNP bfile written by the test, run through `$R4_PLINK --bfile x --keep-allele-order --r square`, gives R[1,2] equal to cor(A1 dosage 1, A1 dosage 2) within 1e-6, and the sign flips when the test swaps A1/A2 of SNP 2 in the .bim and recodes its dosage
    Unit 3 (QTL), fixture: 4-variant panel with REF/ALT plus QTL rows.
    - With --qtl-orient true: exact → beta unchanged; transposed (QTL ref/alt == panel ALT/REF) → beta negated; palindromic (A/T, C/G) → dropped; mismatch (allele sets differ) → dropped; unparseable variant_id → dropped. Counters qtl_orient_{exact,flipped,dropped_palindromic,dropped_mismatch,dropped_unparseable} in the output JSON sum to the n of bridged rows
    - With the flag omitted or false: the output JSON parsed object equals the one from the pre-change script on the same fixture
    - An unrecognised value (e.g. "yes") → stop() (house convention: no silent default)
  </behavior>
  <implementation>Per the tasks below. RED → GREEN → (REFACTOR) per unit, each commit-sized.</implementation>
</feature>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Unit 1 — BMI allele restoration (TDD), then run it on the real files</name>
  <files>src/python/ta_r4/restore_bmi_alleles.py, tests/ta_r4/test_bmi_allele_restoration.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/bmi_allele_restoration_report.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_sha256.tsv</files>
  <read_first>
    - .planning/amendments/sha256_manifest_harmonized_m1.tsv (rows for bmi.EUR.tsv.bgz and bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz)
    - `zcat data/processed/sumstats_harmonized/bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz | head -3` and `zcat .../bmi.EUR.tsv.bgz | head -3` (record both headers in the SUMMARY)
    - `tabix -l` / the .tbi of the frozen file, to reproduce its index parameters
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pitfall 2"
  </read_first>
  <behavior>See Unit 1 in the feature block.</behavior>
  <action>
    1. Write the tests RED.
    2. Implement `restore_bmi_alleles.py` with CLI `--frozen --source --manifest --out --report`:
       - Stream both files with `gzip` + `csv`; never pandas float round-trips for the kept strings.
       - Join key: (CHR, POS, SNP_ID).
       - Numeric comparison at the frozen string's decimal precision: |frozen − (±source)| ≤ 0.5·10^(−d), where d = digits after the decimal point in the frozen string; the same rule for SE and P, where P may be in scientific notation (compare relative difference ≤ 0.5·10^(−sig) on the mantissa).
       - Write uncompressed, then `bgzip` + `tabix -s1 -b2 -e2 -S1` from the R4 plink env, unless the frozen .tbi parameters say otherwise.
    3. Run it on the real files into `data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz`.
       - Write `$MAN/bmi_allele_restoration_report.tsv`: one row per class, the totals, and the raw-file cross-check, i.e. the fraction of 10,000 seeded random kept rows (seed 20261021) whose raw `Tested_Allele` equals the assigned ALT. Record it; do not gate on it. A rate < 0.99 is a FINDING to put in the LOG and in front of Carter at the W2c checkpoint.
       - Write `$MAN/sumstats_r4_sha256.tsv` rows for the output .bgz and .tbi.
       - Also add the 9 inputs, each re-verified against the m1 manifest: the 7 untouched Track A files (asthma.EUR, asthma.AFR, hypertension.EUR, stroke.EUR, stroke.AFR, t2d.EUR, t2d.AFR), the frozen bmi.EUR.tsv.bgz, and the Yengo source bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz. That makes 9 + 2 outputs = 11 rows.
    4. Negative control: temporarily drop the flipped-sign class, so those rows count as
       value_mismatch. Observe the reconciliation test stay green while the class-count test goes
       RED. That shows the class test is the discriminating one. Restore.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_bmi_allele_restoration.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the tests pass; the SUMMARY shows the RED run and the negative-control RED
    - `$MAN/bmi_allele_restoration_report.tsv` row values satisfy n_frozen == exact + flipped + value_mismatch + unjoined (`awk` arithmetic pasted), and n_frozen equals `zcat frozen | tail -n +2 | wc -l`
    - `zcat data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz | head -1` equals `CHR	POS	REF	ALT	BETA	SE	P	EAF	N	SNP_ID	TRAIT	ANCESTRY	BUILD`
    - `sha256sum -c` against `$MAN/sumstats_r4_sha256.tsv` (paths adjusted) reports all 11 rows OK (9 inputs + 2 outputs)
  </acceptance_criteria>
  <done>The BMI alleles are restored with a reconciled, disclosed match rate; all R4 sumstats inputs are checksum-pinned.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Unit 2 — plink_ld_to_rds.R --emit-ref-alt (default off) with plink sign known-answer</name>
  <files>src/snakemake/scripts/plink_ld_to_rds.R, tests/ta_r4/test_plink_ld_to_rds_ref_alt.py</files>
  <read_first>
    - src/snakemake/scripts/plink_ld_to_rds.R (whole file)
    - tests/m3/test_ld_npz_to_rds.py (existing expectations touching plink_ld_to_rds.R)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pitfall 3"
    - https://www.cog-genomics.org/plink/1.9/data (--keep-allele-order semantics; WebFetch if needed)
  </read_first>
  <behavior>See Unit 2 in the feature block.</behavior>
  <action>
    Tests RED first. Then add
    `make_option("--emit-ref-alt", dest="emit_ref_alt", type="character", default="false")`.
    Accept only "true" or "false"; anything else → stop(). When "true" and the variants file is
    .bim, append `REF = variants$A2; ALT = variants$A1` after the A1/A2 assignment and set
    `attr(out, "ref_alt_source") <- "bim_A2_A1_keep_allele_order"`. Do not modify any other
    branch. The flag-off path must not touch the object, so `identical()` holds; the test proves
    it against `git show HEAD:` of the pre-change file. Run `tests/m3/test_ld_npz_to_rds.py` and
    `tests/m3/test_source_freeze_pins.py`, both green. For the negative control, temporarily set
    `ALT = variants$A2`, observe the known-answer sign test RED, and restore.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_plink_ld_to_rds_ref_alt.py tests/m3/test_ld_npz_to_rds.py tests/m3/test_source_freeze_pins.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the tests pass, and the known-answer test RAN (not skipped): `-rs` shows 0 skips in the ta_r4 file. A missing R4_PLINK is a failure, not a skip
    - the SUMMARY shows the RED run and the sabotage RED, plus the measured R[1,2] and cor() values
  </acceptance_criteria>
  <done>The EUR panel can carry REF/ALT consistent with its LD sign; existing callers are unchanged.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Unit 3 — run_qtl_coloc.R --qtl-orient (default false)</name>
  <files>src/snakemake/scripts/run_qtl_coloc.R, tests/ta_r4/test_qtl_orient.py</files>
  <read_first>
    - src/snakemake/scripts/run_qtl_coloc.R (whole file; esp. option parsing, the bridge/join at ~380-480, beta/z construction)
    - src/snakemake/scripts/ld_allele_join.R (ld_allele_join_indices; the .up() normalizer)
    - src/python/harmonize_eqtl.py (harmonized QTL output columns; is variant_id retained?)
    - tests/m3/test_qtl_coloc_allele_join.py, tests/m3/test_qtl_coloc_ld_resolution.py, tests/phase2/test_run_qtl_coloc.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pitfall 4"
  </read_first>
  <behavior>See Unit 3 in the feature block.</behavior>
  <action>
    Tests RED first. Add
    `make_option("--qtl-orient", dest="qtl_orient", type="character", default="false")`.
    Accept only "true" or "false". When "true", after the QTL rows are bound to panel rows by the
    existing bridge:
    - Parse QTL ref/alt from `variant_id` with the regex `^chr[0-9XY]+_[0-9]+_([ACGT]+)_([ACGT]+)$`
      after `.up()`.
    - Compare against the bound panel row's `REF`/`ALT`. If the panel lacks REF/ALT, stop with
      "qtl-orient requires panel REF/ALT".
    - Set `orient_qtl` = +1 for exact, −1 for transposed, NA for palindromic, mismatch and
      unparseable. Drop the NA rows, multiply beta by orient_qtl, and recompute z from the oriented
      beta/se exactly as the script already computes z.
    - Write the five counters plus `qtl_orient: true` to the output JSON.
    When "false", write nothing new. The JSON must stay identical, so do not add a
    `qtl_orient: false` key. Prove identity against `git show HEAD:` of the pre-change script.
    Update the "DELIBERATELY NOT APPLIED" comment block to say the orientation is now applied only
    under `--qtl-orient true`, with D-06 and the new DEC id. If any existing test asserts that
    comment's text, STOP and report. Do not edit pre-existing tests.
    Negative control: temporarily orient with `join$orient` (the catalog→panel vector, the wrong
    object per Pitfall 4). Observe the transposed-QTL test RED. Restore.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_orient.py tests/m3/test_qtl_coloc_allele_join.py tests/m3/test_qtl_coloc_ld_resolution.py tests/phase2/test_run_qtl_coloc.py -q</automated>
  </verify>
  <acceptance_criteria>
    - all four test files pass; the SUMMARY shows the RED run and the `join$orient` sabotage RED
    - the flag-off identity test compares parsed JSON objects from the pre-change and post-change scripts on the same fixture and asserts equality
  </acceptance_criteria>
  <done>QTL betas can be oriented to the panel with their own alleles; default behaviour is unchanged.</done>
</task>

<task type="auto">
  <name>Task 4: Full-suite regression and wave-close (W1)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/tests_baseline_W0a.tsv
  </read_first>
  <action>
    Run §C with label `W1`, commit type `fix`. The commit message cites D-06, D-18 and
    DEC-2026-10-21-ta-r4-e2-fix-supersedes-option-a. The full-suite join against the baseline must
    show 0 outcome changes in tests/m3, tests/phase1 and tests/phase2. That is the D-15 proof that
    the two shared scripts did not move Track B. The LOG entry records the BMI match-rate numbers.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - the full-suite join shows 0 removed ids and 0 outcome changes in pre-existing suites; tests/ta_r4 additions only
    - committed with explicit paths and pushed
  </acceptance_criteria>
  <done>E-2 is fixed for R4 in code, with Track B unchanged.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| shared scripts (plink_ld_to_rds.R, run_qtl_coloc.R) → Track B | an R4 edit could move AFR/AoU outputs |
| restored BMI data → every BMI fit | a wrong allele assignment flips z relative to the panel |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W1-01 | Tampering | plink_ld_to_rds.R / run_qtl_coloc.R | mitigate | default-off flags; identical() / parsed-JSON equality vs the HEAD version; full pre-existing suites unchanged |
| T-r4-W1-02 | Tampering | BMI allele assignment | mitigate | sha256-verified inputs; value-identity classes; raw-file cross-check; reconciled report |
| T-r4-W1-03 | Tampering | wrong orientation vector for QTL | mitigate | the QTL's own alleles; join$orient sabotage RED observed |
</threat_model>

<verification>
Three units, each with an observed RED and an observed negative control. The flag-off identity is
proven. Pre-existing suites are unchanged.
</verification>

<success_criteria>
The E-2 mechanism is closed on both the fine-mapping side (allele-aware join + panel REF/ALT) and
the QTL side (oriented betas) for R4, with no Track B movement.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W1-e2-orientation-tdd-SUMMARY.md`
</output>
