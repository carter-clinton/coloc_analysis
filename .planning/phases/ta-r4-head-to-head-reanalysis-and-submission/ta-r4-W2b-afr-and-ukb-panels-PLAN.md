---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 8
slug: W2b-afr-and-ukb-panels
type: execute
wave: 8
depends_on: ["ta-r4-W2a-eur-panels-catalogs-identity"]
files_modified:
  - src/snakemake/rules/ta_r4_panels_afr_ukb.smk
  - src/python/ta_r4/ukb337k_tiles.py
  - tests/ta_r4/test_ukb_tile_loader.py
  - tests/ta_r4/test_ukb_tile_triangle.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/afr_samples_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb337k_tiles_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_AFR661_1kg_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_AFR504_1kg_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_AFR661_identity_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_legacy_repro_AFR.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_isect_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_isect_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "AFR661 = the 504 continental AFR samples + ASW (61) + ACB (96) from integrated_call_samples.panel = 661; AFR504 = the existing AFR.samples; both sample lists are sha256-manifested (D-20)"
    - "AFR R4 panels are built from the /rs1 1000G Phase 3 VCFs with plink 1.9 --keep-allele-order (biallelic SNPs, MAF >= 0.01 in the panel's own samples, catalog positions) + --emit-ref-alt, under data/r4/ld/AFR661_1kg_r4 and AFR504_1kg_r4; the 6000-variant identity-placeholder builder is NOT used for R4 (Pitfall 12)"
    - "Legacy AFR reproduction panels reproduce the original build_ld_rds semantics (including its identity placeholders above 6000 variants) under data/r4/ld/legacy_repro/AFR/, so Route C/L can reproduce the frozen AFR fit statuses"
    - "UKB 337k LD tiles are fetched anonymously with recorded size/ETag/sha256 into data/r4/downloads/ukb337k/, never under data/processed/ld_reference/ (D-04)"
    - "The UKB loader turns the stored triangle into a full symmetric R with diag == 1 exactly; on a real tile, r signs agree with the 1000G EUR panel for >= 90% of variant pairs with |r_1kg| > 0.5 after allele alignment (ALT := allele1, REF := allele2) (Pitfall 10)"
    - "Three EUR UKB-derived panel classes exist: native (UKB ∩ region catalog), isect (UKB ∩ EUR_1kg_r4 variants), and the matched EUR_1kg_isect_r4 (1000G restricted to the same intersection); regions wider than 3 Mb are assembled from overlapping tiles with n_pairs_zero_filled recorded (D-03, D-04, E6)"
    - "The UKB isect panel is explicitly re-oriented to the 1000G REF/ALT: s_i = +1 if UKB allele1 == ALT_1kg (allele2 == REF_1kg), -1 if transposed; R_ukb_isect = D·R·D with D = diag(s); its variants frame carries the 1000G REF/ALT, so the frozen script's allele-aware join treats z/beta identically under both isect panels; a known-answer test proves D·R·D on a transposed fixture (checker W2)"
  artifacts:
    - path: "src/python/ta_r4/ukb337k_tiles.py"
      provides: "tile fetch (via fetch_verified), triangle-safe loader, overlapping-tile region assembly, .rds writer with REF/ALT"
    - path: "tests/ta_r4/test_ukb_tile_triangle.py"
      provides: "the named Pitfall 10 live known-answer gate"
    - path: "src/snakemake/rules/ta_r4_panels_afr_ukb.smk"
      provides: "AFR plink panels, legacy AFR repro panels, UKB region panels, isect panels"
  key_links:
    - from: "src/python/ta_r4/ukb337k_tiles.py"
      to: "data/r4/ld/EUR_ukb337k_r4/{region_safe}.rds"
      via: "assemble_region_R + write via Rscript saveRDS (variants with REF/ALT)"
      pattern: "EUR_ukb337k_r4"
---

<objective>
Wave 2b builds the AFR secondary-arm panels (661 primary, 504 sensitivity) and the legacy AFR
reproduction panels. It also builds the UKB 337k sensitivity panels under an isolated path, with a
loader that is proven correct on a real tile against the triangle/diagonal convention that bit this
repo before.

Purpose: D-03, D-04, D-07 (AFR secondary), D-10, D-20, E6 (intersection-matched comparison), Pitfalls 10 and 12.
Output: AFR and UKB panel families + manifests + the UKB loader with tests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2a-eur-panels-catalogs-identity-SUMMARY.md

<interfaces>
1000G VCFs (read-only): /rs1/researchers/c/ckclinto/coloc_analysis/region_analysis/data_raw/1kg/vcf/chr{N}.vcf.gz (+ .tbi), GRCh37
  link into the repo as data/r4/inputs/1kg_vcf (symlink; ln -sfn), never copy
Sample files: /rs1/.../region_analysis/data_raw/1kg/{AFR.samples (504), EUR.samples (503), integrated_call_samples.panel}
  panel populations measured 2026-10-21: ACB 96, ASW 61, ESN 99, GWD 113, LWK 99, MSL 85, YRI 108 (sum of the five continental = 504)
Legacy AFR builder: ld_reference.smk:168-200 rule build_ld_rds (src/python? script path in the rule), LD_MAX_VARIANTS env default 6000 -> use_identity placeholder
UKB tiles: s3://broad-alkesgroup-ukbb-ld/UKBB_LD/chr{c}_{s}_{e}.{npz,gz}; HTTPS form https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/<name>
  tiles are 3 Mb windows starting every 1 Mb (s = k*1e6+1, e = s+3e6); e.g. chr12_111000001_114000001.npz = 640,814,458 bytes
  any two positions <= 2 Mb apart share at least one tile; pairs farther apart may share none
Existing (do NOT edit): src/snakemake/scripts/download_ukbb_ld_tiles.py (its loader halves off-diagonals: (dense + dense.T)/2 at :174-182)
PolyFun convention (cited, MEDIUM): stored as one triangle; ld + ld.T gives the full matrix with diag 1; z is consistent when the effect allele == allele1
From W1: plink_ld_to_rds.R --emit-ref-alt true; from W2a: panel_manifest.py, fetch_verified.py, variants_r4 catalogs
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: AFR sample lists and AFR panels (R4 661/504, matched identity, legacy reproduction)</name>
  <files>src/snakemake/rules/ta_r4_panels_afr_ukb.smk, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/afr_samples_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_AFR661_1kg_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_AFR504_1kg_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_AFR661_identity_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_legacy_repro_AFR.tsv</files>
  <read_first>
    - src/snakemake/rules/ld_reference.smk lines 100-200 (download_1kg_*, build_1kg_sample_lists, build_ld_rds and its script)
    - the script build_ld_rds calls (path from the rule), esp. its LD_MAX_VARIANTS placeholder branch (:16, :444-455 per research)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pitfall 12"
    - PLINK 1.9 docs for --vcf, --keep (FID IID), --biallelic-only strict, --snps-only just-acgt, --maf, --set-missing-var-ids, --extract range
  </read_first>
  <action>
    1. `ln -sfn /rs1/researchers/c/ckclinto/coloc_analysis/region_analysis/data_raw/1kg/vcf data/r4/inputs/1kg_vcf`
       (mkdir -p data/r4/inputs first). Write `data/r4/ref/samples/AFR504.samples` (a copy of
       AFR.samples) and `AFR661.samples` (AFR504 ∪ panel rows with pop ∈ {ASW, ACB}). Use the
       two-column FID IID form plink expects (FID = IID); record the original single-column files
       too. Assert counts 504 and 661 and an empty intersection between the added 157 and the 504.
       Write `$MAN/afr_samples_sha256.tsv`.
    2. In `ta_r4_panels_afr_ukb.smk`, rule `r4_panel_afr_1kg`, wildcards `panel ∈ {AFR661_1kg_r4, AFR504_1kg_r4}`
       and the 10 AFR-admissible curated regions. Steps:
       - Build `range.txt` from `data/r4/ld/variants_r4/{region}.tsv` (CHR, POS, POS, CHR:POS).
       - Run plink:
         ```
         plink --vcf data/r4/inputs/1kg_vcf/chr{c}.vcf.gz --keep {samples} --chr {c} --from-bp {s} --to-bp {e}
               --snps-only just-acgt --biallelic-only strict --maf 0.01 --set-missing-var-ids @:#:$1:$2
               --extract range range.txt --keep-allele-order --r square --make-just-bim --write-snplist --out W
         ```
       - Run `plink_ld_to_rds.R --ld W.ld --variants W.bim --region-id ID --ancestry AFR --ld-source onekg_phase3_{panel} --emit-ref-alt true --output data/r4/ld/{panel}/{region_safe}.rds`.
       - Use mem_mb 16000 for wide regions; record the plink log's "variants and N people pass filters" line.
       Rule `r4_identity_payload_afr`: AFR661 matched identity payloads.
       Rule `r4_panel_afr_legacy`: the original `build_ld_rds` command semantics (VCF route,
       `LD_MAX_VARIANTS` unset, so the 6000 default applies and placeholders appear exactly as
       before) into `data/r4/ld/legacy_repro/AFR/`, for the AFR regions the frozen record fitted.
    3. Build (dry-run first). Run `panel_manifest.py --ancestry AFR` per class (the legacy AFR manifest is `panels_legacy_repro_AFR.tsv`, per `paths.panel_manifest_path`) with n_samples 661 / 504 measured
       from the .fam the plink run reports. Record per-region n_var. Any region with n_var > 16000
       is written to `data/r4/findings/afr_panel_size.tsv` as a FINDING: those fits will report
       `too_many_variants`, and the outcome is reported, not hidden. Run `chmod a-w` on the panels.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && wc -l < data/r4/ref/samples/AFR661.samples && wc -l < data/r4/ref/samples/AFR504.samples && ls data/r4/ld/AFR661_1kg_r4/*.rds | wc -l && ls data/r4/ld/AFR504_1kg_r4/*.rds | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - the sample-file line counts print 661 and 504; each AFR R4 panel dir holds 10 .rds files; `panels_AFR661_identity_r4.tsv` has 10 rows
    - every AFR R4 manifest row has has_ref_alt true and n_samples equal to its panel size
    - the legacy AFR panel count equals the number of distinct AFR regions in the frozen record (source and number pasted), and the count of `use_identity` placeholders among them is recorded
  </acceptance_criteria>
  <done>The AFR secondary-arm panels and the legacy AFR reproduction panels exist, manifested.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: UKB tile loader (TDD) and the real-tile triangle/diagonal known-answer gate</name>
  <files>src/python/ta_r4/ukb337k_tiles.py, tests/ta_r4/test_ukb_tile_loader.py, tests/ta_r4/test_ukb_tile_triangle.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb337k_tiles_sha256.tsv</files>
  <read_first>
    - src/snakemake/scripts/download_ukbb_ld_tiles.py (esp. :150-200; the halving bug to NOT reproduce) and src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py
    - https://raw.githubusercontent.com/omerwe/polyfun/master/finemapper.py (WebFetch: the load_ld_npz convention, allele1/allele2 semantics)
    - memory feedback_npz_triangle_flag_contract
    - src/python/ta_r4/fetch_verified.py
  </read_first>
  <behavior>
    Unit (synthetic):
    - load_tile(npz, gz) on a lower-triangular sparse M with diag 0.5 returns R = M + M.T with diag exactly 1
    - On a one-triangle M with diag 1, it returns M + M.T − I
    - On an already-symmetric M, it returns M unchanged
    - Any other diagonal (not all 0.5 and not all 1) → raises TileConventionError
    - The returned variants frame has REF = allele2, ALT = allele1, CHR, POS, SNP_ID
    - assemble_region(tiles, region) over overlapping synthetic tiles: each pair's r comes from a tile containing both (unique where tiles overlap; equality across tiles is checked, any disagreement > 1e-6 raises); pairs in no common tile get 0, counted in n_pairs_zero_filled
    - orient_to_reference(R, variants, ref_variants) (known answer): a 3-variant fixture whose genotypes give R_ref; the same genotypes with variant 2's alleles swapped (dosage recoded 2 − x) give R_swap, where R_swap[1,2] = −R_ref[1,2] and R_swap[2,3] = −R_ref[2,3]; orient_to_reference(R_swap, swapped_variants, ref_variants) returns R equal to R_ref within 1e-12, variants REF/ALT equal to ref_variants', and n_flipped == 1. Variants whose unordered allele set differs from the reference are dropped and counted (n_var_dropped_allele_mismatch); palindromic A/T, C/G variants are dropped and counted (orientation cannot be inferred from alleles). Negative control: skipping the D·R·D step leaves R[1,2] with the wrong sign and the test fails
    Live (marked r4_heavy; skips only while no tile has been fetched; then must run):
    - On chr12_111000001_114000001: diag == 1 exactly, symmetry within 1e-8
    - Over pairs (i, j) of variants present in both this tile and EUR_1kg_r4/SH2B3_12q24 with |r_1kg| > 0.5, after orienting both to the same ALT, sign(r_ukb) == sign(r_1kg) for >= 90% of pairs (the measured rate is pasted)
  </behavior>
  <action>
    1. Tests RED. Implement `ukb337k_tiles.py` (including `orient_to_reference`; its negative control is observed RED and restored):
       - `tile_names_for(chr, start, end) -> list[str]` (tiles whose window intersects the region)
       - `fetch_tile(name, dest)`: HEAD first, recording `Content-Length` + `ETag`, then
         `fetch_verified(size=Content-Length)`, then append to `$MAN/ukb337k_tiles_sha256.tsv`
       - `load_tile(npz_path, gz_path) -> (R: np.ndarray float64, variants: DataFrame)`
       - `assemble_region(tile_list, chr, start, end, keep_positions=None) -> (R, variants, stats)`
       - `write_rds(R, variants, out, ld_source)`: dense float64 to a tmp `.npy` + variants TSV, then
         a short inline R snippet through `$RSCRIPT` writes `list(R=, variants=, ld_source=)`
       Use numpy/scipy from the smoke_dev Python (record versions). If scipy is missing there, run
       inside `envs/python_stats.yml` through the R4 conda prefix and say which.
    2. Fetch `chr12_111000001_114000001.{npz,gz}` into `data/r4/downloads/ukb337k/`. Run the live
       known-answer gate. A sign-agreement rate < 0.90 means the convention is wrong: STOP, report
       it, and do not build UKB panels. Negative control: apply the old `(M + M.T)/2` transform in a
       test-local copy and observe the diag == 1 assertion fail.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_ukb_tile_loader.py tests/ta_r4/test_ukb_tile_triangle.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - both test files pass with 0 skips in test_ukb_tile_triangle.py; the SUMMARY pastes the measured sign-agreement rate and the number of pairs it was computed on
    - the SUMMARY shows the initial RED and the halving-transform negative control failing
    - `$MAN/ukb337k_tiles_sha256.tsv` rows carry size_bytes equal to the HEAD Content-Length
  </acceptance_criteria>
  <done>The UKB LD convention is proven on a real tile; the repo's earlier halving bug cannot recur in R4.</done>
</task>

<task type="auto">
  <name>Task 3: UKB region panels (native, isect) + matched 1000G isect panels + HLA exploratory, manifests, wave-close (W2b)</name>
  <files>src/snakemake/rules/ta_r4_panels_afr_ukb.smk, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_isect_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_isect_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - src/python/ta_r4/ukb337k_tiles.py (Task 2)
    - config/ta_r4/regions_r4.csv; data/r4/ld/variants_r4/
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    1. Add rules to `ta_r4_panels_afr_ukb.smk`:
       - `r4_panel_ukb_native`: output `data/r4/ld/EUR_ukb337k_r4/{region_safe}.rds`. The UKB
         variants are restricted to positions in `variants_r4/{region}.tsv`, matched on CHR:POS
         with an unordered {allele1, allele2} == {REF, ALT} check.
       - `r4_panel_ukb_isect`: output `data/r4/ld/EUR_ukb337k_isect_r4/{region_safe}.rds`. It keeps
         only variants also present in `EUR_1kg_r4/{region}.rds`, with the same unordered-allele
         check, then calls `orient_to_reference(R_ukb, ukb_variants, eur_1kg_r4_variants)` so the
         panel's REF/ALT and R signs follow the 1000G panel (checker W2). `n_flipped` and
         `n_var_dropped_allele_mismatch` go into the manifest.
       - `r4_panel_1kg_isect`: output `data/r4/ld/EUR_1kg_isect_r4/{region_safe}.rds`. It subsets
         EUR_1kg_r4 to the same intersection, in the same variant order as the UKB isect panel.
       All three cover the 10 admissible + 19 NC regions = 29, plus HLA_6p21 for native only
       (exploratory fits, D-24; no coloc row because no admissible 1000G comparator exists).
    2. Build them. Fetch only the tiles the regions need, with 5 parallel downloads (memory
       feedback_parallel_downloads). Write the three manifests with `panel_manifest.py`. Their
       extra columns are `n_tiles`, `n_pairs_zero_filled`, and `n_var_dropped_allele_mismatch`.
       The manifests also carry `n_flipped` (isect). Run `chmod a-w`.
    3. Record each region's native n_var in `data/r4/findings/ukb_native_panel_size.tsv`, flagging
       n_var > 16000. Whether to keep native as-is (with `too_many_variants` outcomes) or to
       pre-register an HM3 restriction is Carter's decision at the W2c checkpoint; W2d applies it
       before the lock. Do not choose for him.
    4. Assert, in the SUMMARY, that the variants frame of `EUR_ukb337k_isect_r4/r` equals that of
       `EUR_1kg_isect_r4/r`: the same CHR, POS, REF and ALT, in the same order, for all 29 regions.
       Also paste, per region, n_flipped and the sign agreement of the oriented isect R with the
       1000G isect R over pairs with |r_1kg| > 0.5.
    5. Run §C with label `W2b`, commit type `feat`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && for d in EUR_ukb337k_r4 EUR_ukb337k_isect_r4 EUR_1kg_isect_r4; do ls data/r4/ld/$d/*.rds | wc -l; done && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q</automated>
  </verify>
  <acceptance_criteria>
    - the counts print 30, 29, 29 (native includes HLA_6p21)
    - the isect variant-frame equality holds for 29/29 regions (script output pasted)
    - `find data/processed/ld_reference -newer data/r4/ld/EUR_1kg_r4 -print 2>/dev/null | wc -l` prints 0
    - tests/ta_r4 green; tests/m3 unchanged against the baseline; committed with explicit paths; pushed
  </acceptance_criteria>
  <done>The A3-UKB sensitivity substrate exists in an isolated path, with native and intersection-matched variants.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AWS S3 public bucket → /rs1 | untrusted downloads |
| UKB panel → EUR chain | must never become resolvable by the Track A/B EUR chain (BLOCKER-B) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W2b-01 | Tampering | UKB tiles | mitigate | HEAD Content-Length + ETag recorded; fetch_verified size check; sha256 manifest |
| T-r4-W2b-02 | Tampering | triangle/diagonal convention | mitigate | real-tile known-answer gate (diag == 1, symmetry, ≥ 90% sign agreement); STOP below the threshold |
| T-r4-W2b-03 | Elevation of privilege | EUR chain resolution of UKB data | mitigate | the isolated `data/r4/ld/EUR_ukb337k_*` dirs are never in the base `ld_panel` chain; the W0b2 isolation test |
| T-r4-W2b-04 | Tampering | AFR placeholder builder used for R4 | mitigate | the R4 AFR rule uses plink only; has_ref_alt + a real-matrix check in the manifest |
</threat_model>

<verification>
AFR 661/504 counts measured. The UKB convention is proven on a real tile. The isect frames are
identical across panels. No write under the Track B tree.
</verification>

<success_criteria>
The secondary AFR arm and the reference-mismatch sensitivity arm have verified, isolated,
manifested panels.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2b-afr-and-ukb-panels-SUMMARY.md`
</output>
