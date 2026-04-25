# M1 Deferred Items

## DEF-M1-02a-01 — MAGIC HbA1c EUR file truncation

- Discovered: 2026-04-25 during m1-02a production smoke test.
- Symptom: `zcat MAGIC1000G_HbA1c_EUR.tsv.gz | tail` shows
  "unexpected end of file" + truncated last record (mid-line at
  chr 1:59348460).
- File size: 278,311,724 B (Wave 1 m1-01 fetch). Likely truncated during
  HTTPS portal fetch (no `.partial` marker; sha256 manifest captured the
  truncated file as authoritative).
- Caused by: m1-01 (Wave 1) — predates m1-02a. NOT a m1-02a bug.
  Harmonizer correctly raises EOFError when reading the truncated file;
  this is the desired fail-loud behavior.
- Resolution: re-fire
  `bash bin/download_sumstats_v2.sh --manifest config/download_manifest_m1_portal.tsv`
  with `MAGIC2021_HbA1c_EUR` row only (cookie env not required); driver
  is idempotent. Then re-run sha256 freeze. Re-test all 6 MAGIC ancestry
  fetches against a tail-record sanity check.
- Scope: blocks Wave 3 (m1-03) `hba1c.EUR` row of the LDSC matrix until
  fixed, but does NOT block m1-02a closeout — harmonizer correctness is
  verified by pytest fixtures + the *other* MAGIC ancestry files
  (TRANS, AFR, EAS, SAS, HIS) which each need their own integrity check
  at fire time.

## DEF-M1-02b-01 — Aragam EUR file is sex-stratified, not pooled-EUR

- Discovered: 2026-04-25 during m1-02b production fire on
  `data/raw/sumstats_v2/Aragam2022/CAD/CAD_GWAS_SEX_STRATIFIED.txt.gz`.
- Symptom: file does NOT match the canonical Aragam RVTESTS schema
  (`MarkerName CHR BP Allele1 Allele2 Freq1 FreqSE MinFreq MaxFreq
  Effect StdErr P-value Direction HetISq HetChiSq HetDf HetPVal Cases
  Effective_Cases N`). Instead it ships per-sex statistics with column
  groups `rs_number reference_allele other_allele eaf beta se beta_95L
  beta_95U z p_value log10_p_value q_statistic q_p_value i2 n_studies
  n_samples effects male_eaf male_beta male_se ... female_eaf
  female_beta female_se ...`.
- Caused by: m1-01 (Wave 1) inferred this file was the EUR-pooled subset
  per the SUMSTATS-UPGRADE.tsv row 22 expected_filename
  `Aragam2022_EUR_subset.tsv` — but this is actually the sex-stratified
  EUR analysis (separate male / female columns). The pooled EUR subset
  may not be released as a separate file in the ZIP — only TRANS
  (primary_discovery_meta) and EAS (BBJ_meta) are present as pooled
  per-ancestry files.
- Resolution options:
  - (a) **DEFERRED for M1 closeout** — accept that EUR coverage comes
    from the TRANS file (pooled) for now. CAD-EUR LDSC rg uses the
    TRANS file marginalization (acceptable since EUR is ~85% of TRANS).
  - (b) Author a sex-aware harmonizer variant `harmonize_aragam_sex_strat`
    that emits two outputs (`cad.EUR-male` + `cad.EUR-female`) and a
    pooled `cad.EUR` derived via inverse-variance meta of the two.
    M2 plan recommends.
- Snakemake disposition: harmonize_aragam_cad rule for ancestry=EUR
  emits a `.deferred` placeholder via the universal guard pattern
  (the rule's params.raw resolves but the harmonizer would fail loud
  on schema mismatch). At fire time the rule must be either updated
  to point at a future pooled-EUR file or replaced with the (b)
  sex-aware variant.
- Scope: blocks Wave 3 (m1-03) `cad.EUR` row of the LDSC matrix until
  resolved (recommend option (b) as M2 deferred work). M1-02b closeout
  proceeds with TRANS + EAS Aragam outputs landed; EUR is a known
  carry-forward gap in the 47-row inventory.
