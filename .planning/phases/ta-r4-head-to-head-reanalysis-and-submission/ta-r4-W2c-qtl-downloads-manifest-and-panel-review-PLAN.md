---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 8
slug: W2c-qtl-downloads-manifest-and-panel-review
type: execute
wave: 8
depends_on: ["W2b"]
files_modified:
  - src/python/ta_r4/fetch_eqtl_catalogue.py
  - src/python/ta_r4/build_qtl_manifest.py
  - config/ta_r4/qtl_manifest.tsv
  - tests/ta_r4/test_qtl_manifest.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_downloads_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2-REVIEW-PACKET.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: false
requirements:
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "GTEx v8 eQTL (.all.tsv.gz) and sQTL (.cc.tsv.gz) files for exactly the tissue set in config/qtl_sources.yaml + config/eqtl_catalogue_qtd_map.yaml are on /rs1 under data/r4/downloads/eqtl_catalogue/, each with Content-Length match, gzip -t pass, its .tbi, and a sha256 row (D-10)"
    - "config/ta_r4/qtl_manifest.tsv is a static, outcome-independent enumeration (admissible EUR region x EUR trait x tissue x source x gene with >= 1 QTL row in the region's GRCh38 window); no GWAS-fit status or tier column; deterministic builder; committed BEFORE the OSF post (rigor upgrade 2)"
    - "Carter has reviewed the W2 review packet (panel manifests, measured EUR n, trait manifest incl. UNRESOLVED items, BMI match rate, AFR and UKB-native panel-size findings) before any known-answer fit; the checkpoint's first option is WAIT"
  artifacts:
    - path: "config/ta_r4/qtl_manifest.tsv"
      provides: "pre-registered QTL-coloc row set"
      contains: "qtl_row_id"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2-REVIEW-PACKET.md"
      provides: "one-page review packet for Carter (measured facts + open decisions)"
  key_links:
    - from: "config/ta_r4/qtl_manifest.tsv"
      to: "W3e QTL group runner and W6 QTL fires"
      via: "row enumeration"
      pattern: "qtl_row_id"
---

<objective>
Wave 2c re-acquires the GTEx v8 QTL inputs onto durable storage. It freezes the QTL-coloc row set as
a static manifest so QTL rows cannot depend on arm outcomes. Then it stops for Carter to review the
measured data facts that the OSF amendment will fix (D-25).

Purpose: D-07 (QTL layer), D-10, D-12a/D-25 (human review of measured facts).
Output: QTL downloads + sha256 manifest, the static QTL manifest + builder + test, a review packet.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2b-afr-and-ukb-panels-SUMMARY.md

<interfaces>
eQTL Catalogue (verified in research): https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/QTS000015/{QTD}/{QTD}.all.tsv.gz (eQTL ge),
  {QTD}.cc.tsv.gz (sQTL leafcutter; the .all URL 404s); eQTL ≈ 3.8 GB/tissue, sQTL ≈ 1.0 GB/tissue; GRCh38
Tissue/QTD mapping: config/eqtl_catalogue_qtd_map.yaml; source definitions: config/qtl_sources.yaml (study_id, qtd_kind, upstream_suffix)
URL resolver to mirror (do not import the .smk): qtl_download.smk::_resolve_eqtlcat_url
Legacy manifest enumeration to mirror MINUS the tier gate: qtl_coloc.smk:382-433 build_qtl_coloc_manifest and the script it runs
GRCh38 region windows: config/regions_curated_grch38.csv
Parallel downloads: xargs -P 5 (memory feedback_parallel_downloads); /rs1 has ~28 TB free
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Download the GTEx v8 eQTL/sQTL files with integrity checks</name>
  <files>src/python/ta_r4/fetch_eqtl_catalogue.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_downloads_sha256.tsv</files>
  <read_first>
    - config/qtl_sources.yaml, config/eqtl_catalogue_qtd_map.yaml
    - src/snakemake/rules/qtl_download.smk lines 1-160 (URL resolution, T-02-04/T-02-06 mitigations)
    - src/python/ta_r4/fetch_verified.py
  </read_first>
  <action>
    1. `fetch_eqtl_catalogue.py` (CLI `--sources gtex_eqtl gtex_sqtl --dest data/r4/downloads/eqtl_catalogue --jobs 5`)
       - Resolve every (tissue, source) URL exactly as `_resolve_eqtlcat_url` does: same YAML keys,
         same suffix rule. Print the resolved list and its count. The count is the number of tissues
         in the map × 2 sources; reconcile it in the SUMMARY.
       - HEAD every URL first. A non-200, or a Content-Length < 1 MB, aborts before any download.
       - Download each file plus its `.tbi` via `fetch_verified(size=Content-Length, magic=gzip)`
         into `data/r4/downloads/eqtl_catalogue/{QTD}/`, 5 at a time.
       - After download, run `gzip -t` on each file (bgzf-compatible), then
         `tabix -l <file> | head -1` with the R4 plink env's tabix to prove the index matches.
       - Check whether the eQTL Catalogue publishes checksums for these files (look for an md5 listing
         in the QTS000015 or QTD directory). If it does, verify against them and record the source;
         if not, record "no published checksum".
       - Append rows to `$MAN/qtl_downloads_sha256.tsv`
         (`qtd, tissue, source, url, size_bytes, sha256, published_md5, gzip_ok, tabix_ok, fetched_utc`).
    2. Run it with `nohup ... > data/r4/logs/qtl_fetch.log 2>&1 &`. Track progress by listing the
       files under data/r4/downloads/eqtl_catalogue, not by process state. When it is done,
       reconcile: rows == resolved URL count, all `gzip_ok` and `tabix_ok` true.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && awk -F'\t' 'NR>1{n++; if($8!="true"||$9!="true") bad++} END{print n, bad+0}' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_downloads_sha256.tsv</automated>
  </verify>
  <acceptance_criteria>
    - the awk prints `<N> 0`, where N equals the resolved URL count printed by the script (both pasted)
    - `du -sh data/r4/downloads/eqtl_catalogue` is recorded; nothing was written under `data/raw/`
  </acceptance_criteria>
  <done>GTEx v8 QTL inputs are on /rs1, integrity-checked and manifested.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Static QTL-coloc manifest (outcome-independent) with a deterministic builder</name>
  <files>src/python/ta_r4/build_qtl_manifest.py, config/ta_r4/qtl_manifest.tsv, tests/ta_r4/test_qtl_manifest.py</files>
  <read_first>
    - src/snakemake/rules/qtl_coloc.smk lines 360-435 and the manifest script it invokes
    - config/regions_curated_grch38.csv; config/ta_r4/pair_manifest.tsv (admissible EUR regions)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (the frozen QTL-layer scope: which ancestries, sources, tissues; record what it says)
  </read_first>
  <behavior>
    - One row per (region_safe [10 admissible EUR], trait [5 EUR], source [eqtl, sqtl], tissue, gene_or_phenotype_id) where the raw file has ≥ 1 row inside the region's GRCh38 window; columns `qtl_row_id, region_safe, ancestry, trait, source, tissue, qtd, gene_id, molecular_trait_id, chr38, start38, end38, n_qtl_variants_in_window`
    - Removing the trait column and taking unique rows gives the per-region feature set, and the row count == that set's size × 5 traits (reconciliation identity)
    - No column refers to GWAS fit status or tier. The schema test rejects a `status` / `tier` column (negative control)
    - Deterministic: two builds give the same sha256
    - The scope differences from the frozen QTL layer (ancestries / sources / tissues) are written to the SUMMARY; an R4 row set narrower than the frozen scope is a FINDING to raise at Task 4
  </behavior>
  <action>
    Tests RED, then implement `build_qtl_manifest.py`. It slices each raw file with `tabix` over
    each region's GRCh38 window and enumerates distinct `molecular_trait_id` / gene ids, mirroring
    the legacy builder's id semantics but without its tier gate. Run it and commit
    `config/ta_r4/qtl_manifest.tsv`. Record the row count and the per-source and per-region counts
    in the LOG.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_manifest.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the test passes; the SUMMARY shows the RED run and the `tier`-column negative control
    - `awk 'NR>1' config/ta_r4/qtl_manifest.tsv | wc -l` equals 5 × the unique (region, source, tissue, feature) count (both numbers pasted)
  </acceptance_criteria>
  <done>The QTL row set is fixed before any QTL result exists.</done>
</task>

<task type="auto">
  <name>Task 3: Write the W2 review packet; wave-close (W2c)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2-REVIEW-PACKET.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - all $MAN/panels_*.tsv; config/ta_r4/trait_manifest.tsv; $MAN/bmi_allele_restoration_report.tsv
    - data/r4/findings/*.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    Write `ta-r4-W2-REVIEW-PACKET.md`. Keep it short: tables plus one line per open decision, every
    number copied from a manifest by a command whose output is pasted. Sections:
    (1) Measured EUR n (.fam) vs the draft's claims;
    (2) per-panel-class counts and n_var ranges; SH2B3 n_var vs 895;
    (3) BMI restoration classes and the raw cross-check rate;
    (4) trait manifest, with every UNRESOLVED item stated as a question (hypertension type; sdY sources);
    (5) AFR panel-size findings;
    (6) UKB-native panel sizes and the open decision: keep native as-is, or pre-register an HM3 restriction;
    (7) QTL scope vs the frozen layer.
    Then run §C with label `W2c`, commit type `feat`. Commit BEFORE the checkpoint so Carter
    reviews committed files.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git log -1 --format=%s && git status --porcelain -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2-REVIEW-PACKET.md config/ta_r4/qtl_manifest.tsv</automated>
  </verify>
  <acceptance_criteria>
    - the packet exists with the 7 sections; the git status line is empty (committed); pushed
  </acceptance_criteria>
  <done>The review packet is committed and pushed.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 4: Carter reviews the measured data facts (panel manifests, trait manifest, BMI restoration, UKB native sizes)</name>
  <what-built>Every R4 panel (EUR legacy + R4, A2, k2d, AFR 661/504, UKB native/isect, 1000G isect), the trait manifest, the BMI allele restoration and the QTL downloads and manifest, all on /rs1 with committed manifests. The review packet summarizes the measured facts and the open questions.</what-built>
  <how-to-verify>
    1. Open `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2-REVIEW-PACKET.md`.
    2. Check that the EUR n, the panel dims and the SH2B3 895 comparison are plausible.
    3. Answer each UNRESOLVED trait-manifest item (hypertension trait type; sdY values).
    4. Decide the UKB-native question (keep native with `too_many_variants` outcomes, or pre-register an HM3 restriction in W4).
    5. Confirm or adjust the QTL scope.
  </how-to-verify>
  <options>
    - option-wait (FIRST, the default under auto-mode): WAIT. Stop execution and hand back to Carter. No further plan runs.
    - option-approved: Carter has reviewed and typed his answers. The executor records them verbatim in the LOG and in `config/ta_r4/trait_manifest.tsv` (UNRESOLVED → value, with source "Carter 2026-MM-DD"), commits, and the chain continues to W3a.
  </options>
  <resume-signal>Carter types "approved" plus his answers to every open item, or describes the issues. Anything else = WAIT.</resume-signal>
  <files>config/ta_r4/trait_manifest.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>Present the packet. On approval, record Carter's answers verbatim and commit with explicit paths. Do not infer answers.</action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ! grep -q UNRESOLVED config/ta_r4/trait_manifest.tsv && echo RESOLVED</automated></verify>
  <acceptance_criteria>
    - the LOG contains Carter's verbatim answers, dated; `config/ta_r4/trait_manifest.tsv` has no `UNRESOLVED` cell
  </acceptance_criteria>
  <done>Carter has signed off the measured data facts.</done>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2-REVIEW-PACKET.md
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| EBI FTP → /rs1 | ~235 GB of untrusted downloads |
| GSD auto-mode → scientific judgement | facts that go into a public pre-registration must be seen by Carter |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W2c-01 | Tampering | QTL downloads | mitigate | HEAD Content-Length match, gzip -t, tabix -l, sha256 manifest, published checksums where available |
| T-r4-W2c-02 | Tampering | arm-dependent QTL row attrition | mitigate | static manifest with no status/tier column; deterministic builder; schema negative control |
| T-r4-W2c-03 | Elevation of privilege | auto-approval of a scientific checkpoint | mitigate | first option WAIT; the acceptance check requires zero UNRESOLVED cells, which only Carter's answers can supply |
</threat_model>

<verification>
Downloads reconciled to the resolved URL count. The QTL manifest is reconciled and deterministic.
Carter's answers are recorded verbatim.
</verification>

<success_criteria>
Every data input for R4 is on durable storage with checksums, the QTL row set is fixed, and Carter
has confirmed the measured facts that the pre-registration will state.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2c-qtl-downloads-manifest-and-panel-review-SUMMARY.md`
</output>
