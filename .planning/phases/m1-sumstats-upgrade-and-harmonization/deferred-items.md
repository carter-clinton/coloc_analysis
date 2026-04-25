# M1 Deferred Items

## DEF-M1-02a-01 — MAGIC HbA1c file truncation (ALL 6 ANCESTRIES, not just EUR)

- Discovered: 2026-04-25 during m1-02a production smoke test (EUR);
  scope confirmed widened in m1-03 Wave 2a re-fire (TRANS, AFR, EAS,
  SAS, HIS all also truncated).
- Symptom: `gzip -t` on every MAGIC raw `.tsv.gz` returns "unexpected end
  of file"; harmonizer raises EOFError mid-read.
  - EUR: 278,311,724 B
  - TRANS: 228,313,231 B
  - AFR (`HbA1c_AA.tsv.gz`): 100,967,097 B
  - EAS: 179,735,042 B
  - SAS: 278,206,188 B
  - HIS (`HbA1c_HISP.tsv.gz`): 278,435,516 B
- Likely root cause: m1-01 Wave 1 fetch from MAGIC HTTPS portal. The
  driver did not stage `.partial` markers and the sha256 manifest captured
  the truncated bytes as authoritative.
- Caused by: m1-01 (Wave 1). NOT a m1-02a bug; not a m1-03 bug. Both
  harmonizer and Wave 2a fire driver correctly fail-loud on the truncated
  archives.
- Resolution: re-fire
  `bash bin/download_sumstats_v2.sh --manifest config/download_manifest_m1_portal.tsv`
  with each MAGIC2021_HbA1c_* row (cookie env not required); driver is
  idempotent. Add a post-fetch `gzip -t` integrity gate to the driver so
  truncations are caught before sha256 freeze. Re-fire Wave 2a MAGIC
  harmonizers on the repaired files; then m1-03 munge expands the matrix
  by 6 traits (TRANS + 5 single-ancestry + EUR).
- Scope: blocks Wave 3 (m1-03) `hba1c.{TRANS,EUR,AFR,EAS,SAS,HIS}` rows
  of the LDSC matrix until re-fetched. m1-03 closes the matrix at
  N=26 traits (without MAGIC); when MAGIC re-fetches, matrix grows
  to N=32.

## DEF-M1-03-01 — Wave 2 not previously fired; m1-03 inline-fired Wave 2a continuous traits

- Discovered: 2026-04-25 at m1-03 plan-load time. m1-02a SUMMARY described
  "Production smoke test on real Yengo file" + "DAG dry-run loads 30 jobs"
  but no actual production fire of the 28 leaf Wave 2a harmonizers occurred.
  Only Wave 2b (6 case-control + Evangelou rename) had been live-fired.
- Caused by: m1-02a was authored as a TDD-only plan (RED + GREEN + DAG
  dry-run); the production fire was pushed to a later plan but never
  scheduled.
- Resolution (in m1-03 — Rule 3 deviation): authored
  `bin/fire_wave2_continuous_for_m1_03.sh` to fire the 23 missing
  continuous-trait harmonizers via xargs -P 6. Skipped Loh×2 (D-01),
  MAGIC×6 (DEF-M1-02a-01 truncation), and AFR eGFR (raw not present;
  Morris). Result: 26 D-16-named harmonized files on disk, ~1768s wall.
- Scope: cleanly resolved within m1-03; no follow-up. Future plans can
  treat the 26 D-16 files as the M1 closeout state and add MAGIC + Loh
  + DIAMANTE + GBMI as those deferrals resolve.

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
