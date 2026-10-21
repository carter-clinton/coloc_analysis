---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 6
slug: W2a-eur-panels-catalogs-identity
type: execute
wave: 6
depends_on: ["W1"]
files_modified:
  - src/snakemake/rules/ta_r4_panels.smk
  - src/python/ta_r4/panel_manifest.py
  - src/python/ta_r4/fetch_verified.py
  - config/ta_r4/trait_manifest.tsv
  - tests/ta_r4/test_known_answer_panels.py
  - tests/ta_r4/test_fetch_verified.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/downloads_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ref_1000G_EUR_plink_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_legacy_repro.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_identity_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_k2d_identity.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "The LDSC 1000G Phase 3 plinkfiles tgz on /rs1 has md5 a7773ab485827b533cb300c76356d76b and size 288277344, verified BEFORE extraction; the EUR sample n is measured from the .fam and recorded (D-25)"
    - "Legacy-identical EUR panels (plink WITHOUT --keep-allele-order, plink_ld_to_rds.R without --emit-ref-alt) exist for the 10 EUR autosomal non-HLA curated regions (12 minus HLA_6p21 minus chrX BMI_Xq24) under data/r4/ld/legacy_repro/EUR/; R4 EUR panels (--keep-allele-order + --emit-ref-alt) exist for the 10 admissible + 9 negative-control regions under data/r4/ld/EUR_1kg_r4/ (D-12a)"
    - "For every region built both ways, n_var(R4) == n_var(legacy) and |R4| == |legacy| elementwise within 1e-12 (orientation changes signs, not magnitudes); the SH2B3 panel has n_var 895 or the mismatch is recorded as a finding"
    - "A2 payloads EUR_identity_r4/{region}.rds have R = I and variants identical() to EUR_1kg_r4; k2d R=NULL payloads exist only under data/r4/ld/k2d_identity/ for reproduction (D-01, D-14, Pattern 3)"
    - "Every panel class has a committed manifest (md5, sha256, size_bytes, n_var, n_samples, build, source, has_ref_alt) and panels are chmod a-w after the manifest is written"
    - "config/ta_r4/trait_manifest.tsv records, per trait x ancestry, the measured type (cc|quant), sdY with its source, and N_median; unresolved items are marked UNRESOLVED for the W2c checkpoint (D-25)"
    - "No file is written under data/processed/ld_reference/ (D-15)"
  artifacts:
    - path: "src/snakemake/rules/ta_r4_panels.smk"
      provides: "r4_catalog, r4_panel_eur_legacy, r4_panel_eur_1kg, r4_identity_payload, r4_k2d_payload rules"
    - path: "src/python/ta_r4/panel_manifest.py"
      provides: "memory-bounded panel inspection + manifest writer"
    - path: "config/ta_r4/trait_manifest.tsv"
      provides: "measured trait types / sdY / N (D-25)"
    - path: "tests/ta_r4/test_known_answer_panels.py"
      provides: "D-12a live gate"
  key_links:
    - from: "src/snakemake/rules/ta_r4_panels.smk::r4_panel_eur_1kg"
      to: "src/snakemake/scripts/plink_ld_to_rds.R --emit-ref-alt true"
      via: "plink --keep-allele-order --r square then Rscript"
      pattern: "keep-allele-order"
    - from: "manifests/panels_EUR_1kg_r4.tsv"
      to: "src/python/ta_r4/write_ld_receipt.py"
      via: "receipt md5 gate at fit time"
      pattern: "panels_"
---

<objective>
Wave 2a regenerates the EUR LD substrate on /rs1. It builds two versions: a legacy-identical panel
for reproducing the frozen numbers, and the R4 panel signed under `--keep-allele-order`, which
carries REF/ALT for the allele-aware join. It also builds the variant catalogs, the matched A2
identity payloads, the k2d reproduction payloads and the measured trait manifest. Every artifact
is checksum-manifested and pinned by a live known-answer test.

Purpose: D-03 (1000G primary), D-10, D-11, D-12a, D-25, D-01/D-14 (matched identity).
Output: panels + payloads + catalogs under data/r4/ld/, manifests, the trait manifest, tests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W1-e2-orientation-tdd-SUMMARY.md

<interfaces>
Legacy panel rule to mirror: src/snakemake/rules/ld_reference.smk:274-333 build_ld_rds_1kg_eur
  plink --bfile {prefix}.{chr} --chr C --from-bp S --to-bp E --r square --write-snplist --make-just-bim --out W --threads 2
  Rscript plink_ld_to_rds.R --ld W.ld --variants W.bim --region-id ID --ancestry EUR --ld-source onekg_phase3_eur_hm3 --output OUT
  bfile prefix inside the tgz: 1000G_EUR_Phase3_plink/1000G.EUR.QC.{chr}
Catalog rule to mirror: ld_reference.smk:203-270 collect_region_variants (inputs: the Track A sumstats ONLY —
  asthma/bmi/hypertension/stroke/t2d .EUR + asthma/stroke/t2d .AFR — never the newer M1 files sitting alongside)
k2d payload builder: src/snakemake/scripts/make_identity_ld_refs.R (R = NULL / use_identity payloads)
Matched A2 builder (W0c): src/snakemake/scripts/ta_r4/make_matched_identity_payload.R --in --out
Region-file naming the legacy loader expects: run_susie_rss.R safe_region_id() (line 69) — read it to name legacy_repro files
Zenodo: record 10515792, file 1000G_Phase3_plinkfiles.tgz, md5 a7773ab485827b533cb300c76356d76b, 288,277,344 bytes, CC-BY-4.0
  (URL rot workarounds: memory feedback_url_rot_workarounds)
Memory rule: dense n_var^2 verification must be memory-bounded (blockwise), never np.allclose(m, m.T) on the full matrix
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Verified download helper (TDD), fetch the LDSC 1000G plinkfiles, measure the EUR sample n</name>
  <files>src/python/ta_r4/fetch_verified.py, tests/ta_r4/test_fetch_verified.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/downloads_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ref_1000G_EUR_plink_sha256.tsv</files>
  <read_first>
    - config/ta_r4/data_sources.yaml
    - memory feedback_url_rot_workarounds (Zenodo mirrors), feedback_parallel_downloads
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Standard Stack / Data sources", §"Security Domain"
  </read_first>
  <behavior>
    - fetch_verified(url, dest_dir, md5=None, sha256=None, size=None, magic=("gzip",)) downloads to dest_dir/<name>.part, renames only after every provided check passes, and returns {path, md5, sha256, size, magic}
    - Size mismatch → raises and deletes .part; md5 mismatch → raises; an HTML body (e.g. b"<!DOCTYPE html") with a 200 → raises on the magic check
    - dest_dir must be a new or empty dir under data/r4/downloads/ (refuses a non-empty dir that holds other files)
    - No shell=True; the URL must start with https://
  </behavior>
  <action>
    1. Write the tests RED. Use a local `http.server` fixture serving a gzip file and an HTML file.
       Implement `fetch_verified.py` with `urllib.request` (streaming, 1 MiB chunks) and `hashlib`.
       The magic check reads the first 4 bytes: `\x1f\x8b` is gzip; tar is checked via `tarfile.is_tarfile` after the gzip check.
       Make it GREEN.
    2. Fetch `https://zenodo.org/records/10515792/files/1000G_Phase3_plinkfiles.tgz?download=1`
       into `data/r4/downloads/ldsc_1000G_Phase3_plinkfiles/` with md5 `a7773ab485827b533cb300c76356d76b`
       and size `288277344`. If the URL fails, use the mirror list in memory
       `feedback_url_rot_workarounds`; the md5 must still match. Append a row to
       `$MAN/downloads_sha256.tsv` (`source, url, file, size_bytes, md5, sha256, fetched_utc`).
    3. List the archive before extracting:
       `tar -tzf ... | awk -F/ '{print $1}' | sort -u` must show a single top dir and no absolute
       or `..` members. Extract into `data/r4/ref/` (a new dir). Write
       `$MAN/ref_1000G_EUR_plink_sha256.tsv` for every extracted file.
       Measure `wc -l data/r4/ref/1000G_EUR_Phase3_plink/1000G.EUR.QC.1.fam` and confirm all 22 .fam
       files have the same sha256 (identical sample sets). Record n_samples in the LOG. This is the
       measured EUR n (D-25; research A4 says 489 vs 503 is unverified).
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_fetch_verified.py -q && md5sum /rs1/researchers/c/ckclinto/coloc_analysis/ta_r4/downloads/ldsc_1000G_Phase3_plinkfiles/1000G_Phase3_plinkfiles.tgz</automated>
  </verify>
  <acceptance_criteria>
    - test_fetch_verified passes; the SUMMARY shows its RED run and the HTML-magic negative case failing as designed
    - `md5sum` of the tgz prints `a7773ab485827b533cb300c76356d76b`; `stat -c %s` prints `288277344`
    - the 22 .fam sha256 values are identical (`cut -f3 ... | sort -u | wc -l` over the .fam rows prints 1); the measured n_samples is in the LOG
  </acceptance_criteria>
  <done>The 1000G EUR reference is on /rs1, checksum-verified, with the sample n measured rather than assumed.</done>
</task>

<task type="auto">
  <name>Task 2: Panel rules — catalogs, legacy-identical and R4 EUR panels, A2 and k2d payloads — then build them</name>
  <files>src/snakemake/rules/ta_r4_panels.smk, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv</files>
  <read_first>
    - src/snakemake/rules/ld_reference.smk lines 200-335 (collect_region_variants; build_ld_rds_1kg_eur)
    - src/snakemake/scripts/make_identity_ld_refs.R (which ancestries/regions it writes; the payload shape)
    - src/legacy/region_analysis/scripts/run_susie_rss.R lines 60-170 (safe_region_id; how the legacy loader names {ld_dir}/{ancestry}/<file>.rds)
    - .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (which trait x ancestry x region rows exist: 95)
    - src/python/ta_r4/paths.py, src/python/ta_r4/arms.py, Snakefile.ta_r4
  </read_first>
  <action>
    In `src/snakemake/rules/ta_r4_panels.smk`, write the rules below. The guarded include in
    `Snakefile.ta_r4` from W0b picks the file up. None of these rules takes the gate input, because
    they are infrastructure (D-05).
    - `r4_catalog_legacy`: the catalog command from `collect_region_variants`, pointed at the 8
      original sumstats, output `data/r4/ld/variants_legacy/{region_safe}.tsv`. Run it for the 12
      curated regions.
    - `r4_catalog_r4`: the same command, but with `paths.sumstats_path` (restored BMI), output
      `data/r4/ld/variants_r4/{region_safe}.tsv`. Run it for the 12 curated regions plus the 9 NC
      regions.
    - `r4_panel_eur_legacy`: the plink + `plink_ld_to_rds.R` commands verbatim from
      `build_ld_rds_1kg_eur` (no `--keep-allele-order`, no `--emit-ref-alt`, `--ld-source
      onekg_phase3_eur_hm3`), bfile prefix `data/r4/ref/1000G_EUR_Phase3_plink/1000G.EUR.QC`.
      Output `data/r4/ld/legacy_repro/EUR/<legacy file name per safe_region_id>.rds`. Covers the
      10 autosomal non-HLA curated regions (the rule's own eligibility set, `_ONEKG_EUR_REGION_PATTERN`).
    - `r4_panel_eur_1kg`: the same, plus `--keep-allele-order` on plink and `--emit-ref-alt true`
      on the Rscript, `--ld-source onekg_phase3_eur_hm3_keep_allele_order`. Output
      `data/r4/ld/EUR_1kg_r4/{region_safe}.rds`. Covers the 10 admissible + 9 NC regions. The
      plink work dir is `data/r4/ld/work/{panel}/{region_safe}`. Keep the .bim, .snplist and .log;
      delete the .ld text after the .rds is written and its manifest row recorded.
    - `r4_identity_payload`: `make_matched_identity_payload.R --in EUR_1kg_r4/{r}.rds --out EUR_identity_r4/{r}.rds`.
    - `r4_k2d_payload`: `make_identity_ld_refs.R` semantics into `data/r4/ld/k2d_identity/{ancestry}/...`,
      for exactly the ancestry × region set it produced for k2d. Read the script; if it writes AFR
      too, include AFR.
    - All rules: `conda: envs/plink.yml` for plink steps and `envs/r_coloc.yml` for pure-R steps,
      `resources: mem_mb=16000` for regions with > 8,000 variants (PYHIN1), queue serial.
    - Target lists `R4_PANEL_TARGETS_EUR` and `R4_CATALOG_TARGETS`.
    Build with `bash bin/r4_fire.sh repro repro_routeC <targets> -n` first, then for real. Watch
    progress by listing `data/r4/ld/*/`. When it is done, write `$MAN/catalogs_sha256.tsv`.
    Reconcile the counts: 12 legacy catalogs + 21 r4 catalogs = 33 rows; 10 legacy panels;
    19 R4 panels; 19 A2 payloads; and k2d payloads equal to the number of distinct
    (ancestry, region) pairs in the k2d summary. Paste every count.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ls data/r4/ld/EUR_1kg_r4/*.rds | wc -l && ls data/r4/ld/EUR_identity_r4/*.rds | wc -l && ls data/r4/ld/legacy_repro/EUR/*.rds | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - the three `ls | wc -l` outputs are 19, 19 and 10
    - `find data/processed/ld_reference -newer data/r4/ld/variants_legacy -print 2>/dev/null | wc -l` prints 0 (no Track B tree write during this wave)
    - `$MAN/catalogs_sha256.tsv` has 33 data rows (`awk 'NR>1' | wc -l`)
    - the dry-run printout (first 40 lines) is in the SUMMARY and contains no forbidden substring from INDEX §B.7
  </acceptance_criteria>
  <done>EUR panels (legacy + R4), matched identity payloads, k2d payloads and catalogs exist on /rs1.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Panel manifests + known-answer live gate + trait manifest (D-12a, D-25)</name>
  <files>src/python/ta_r4/panel_manifest.py, tests/ta_r4/test_known_answer_panels.py, config/ta_r4/trait_manifest.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_legacy_repro.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_identity_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_k2d_identity.tsv</files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1.5-ld-audit.md around line 81 (SH2B3 895 dims)
    - config/trait_inventory.yaml and config/trait_sample_sizes.yaml (trait sources / DOIs / types)
    - memory feedback_dense_matrix_verify_memory_bounded, feedback_npz_triangle_flag_contract
    - src/python/ta_r4/write_ld_receipt.py (manifest columns it reads)
  </read_first>
  <behavior>
    - panel_manifest.py inspects each .rds through `$RSCRIPT` with a blockwise checker (2,000-row blocks): n_var, symmetric within 1e-8, diag == 1 within 1e-8 (identity payloads: R == I exactly; k2d payloads: R NULL recorded as such), finite, has_ref_alt, plus md5/sha256/size. It writes the manifest TSV
    - Live gate test_known_answer_panels (skips only while data/r4/ld/EUR_1kg_r4 is absent):
      (a) every manifest row's md5 equals the file on disk;
      (b) n_var(EUR_1kg_r4/r) == n_var(legacy_repro/r) for the 10 shared curated regions;
      (c) |R_r4| == |R_legacy| elementwise within 1e-12, blockwise;
      (d) EUR_identity_r4 variants identical() to EUR_1kg_r4;
      (e) has_ref_alt true for every EUR_1kg_r4 row and false for legacy;
      (f) the SH2B3 legacy n_var is compared with 895. A mismatch is a FINDING written to `data/r4/findings/panel_known_answers.tsv` and the LOG, and does not fail the gate (§B.10); the test asserts that the findings file was written with one row per check
    - Negative control: corrupt one byte of a COPY of one panel in tmp, point the md5 check at it, and observe the failure
  </behavior>
  <action>
    1. Tests RED, then implement `panel_manifest.py` (CLI `--panel-dir --source --build GRCh37 --n-samples N --out`).
       Run it for the four panel dirs, then `chmod a-w` every panel file. n_samples is the measured
       .fam count for the 1kg panels and NA for payloads.
    2. Trait manifest `config/ta_r4/trait_manifest.tsv`, columns
       `trait, ancestry, type, sdY, sdY_source, N_median, source_study, evidence`. One row per
       Track A trait × ancestry (8 rows). Fill `type` from the trait's source study per
       `config/trait_inventory.yaml`; asthma/stroke/t2d are expected cc. For `hypertension.EUR`,
       find which phenotype the file is (binary hypertension vs continuous BP) by tracing its
       provenance in the repo (the download script / trait_inventory / harmonize notes) and its
       value distribution (median |BETA|, presence of an OR-like scale). If the evidence does not
       settle it, write `UNRESOLVED` with the evidence. It goes to Carter at W2c and is fixed in W4.
       For BMI (quant), set `sdY = 1` with source "Yengo 2018 per-SD units" only if confirmed in
       the paper or repo docs. Also compute, for the record, `coloc:::sdY.est(varbeta, MAF, N)`
       medians over the 10 admissible regions, using the restored EAF, and put them in `evidence`.
       `N_median` is measured from the sumstats N column inside the admissible regions.
    3. Live gate GREEN. Paste `data/r4/findings/panel_known_answers.tsv`.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_known_answer_panels.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - the test passes with 0 skips (the panels exist); the SUMMARY shows the RED run and the corrupted-copy negative control
    - `awk 'NR>1' $MAN/panels_EUR_1kg_r4.tsv | wc -l` prints 19; `panels_legacy_repro.tsv` 10; `panels_EUR_identity_r4.tsv` 19
    - `config/ta_r4/trait_manifest.tsv` has 8 data rows; any `UNRESOLVED` entries are listed in the LOG for W2c
    - `stat -c %A data/r4/ld/EUR_1kg_r4/SH2B3_12q24.rds` shows no `w` bits
  </acceptance_criteria>
  <done>Panels are manifested, read-only and known-answer-checked; trait facts are measured or flagged.</done>
</task>

<task type="auto">
  <name>Task 4: Wave-close (W2a)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W2a`, commit type `feat`. The LOG records the measured EUR n, every panel count, the SH2B3 n_var, and every finding row.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - tests/ta_r4 green; tests/m3 unchanged against the baseline; committed with explicit paths; pushed
  </acceptance_criteria>
  <done>W2a committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Zenodo / mirrors → /rs1 | an untrusted download crosses here |
| panel files → fits | a modified panel silently changes every downstream number |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W2a-01 | Tampering | 1000G tgz | mitigate | md5 + size + magic before extraction; tar member listing refuses absolute or `..` paths |
| T-r4-W2a-02 | Tampering | panels after build | mitigate | sha256/md5 manifests committed; chmod a-w; receipt md5 gate at fit time |
| T-r4-W2a-03 | Tampering | wrong panel version (legacy vs R4) | mitigate | separate dirs; the live gate compares n_var and \|R\| and asserts has_ref_alt per class |
| T-r4-W2a-04 | Denial of service | dense-matrix OOM in checks | mitigate | blockwise verification |
</threat_model>

<verification>
Panel counts reconciled (19/19/10 + k2d); the known-answer findings file is written; the sample n is
measured; nothing is written under the Track B tree.
</verification>

<success_criteria>
The EUR LD substrate for both reproduction and R4 exists durably, verified against known answers,
with every measured fact recorded rather than assumed.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2a-eur-panels-catalogs-identity-SUMMARY.md`
</output>
