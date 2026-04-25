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
