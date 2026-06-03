# Gate B nano re-fire #2 — live FAIL diagnostics (sample-axis collapse)

**Date:** 2026-06-03
**Author:** Carter K. Clinton (live AoU forensics)
**Reconstructed:** on NCSU from the operator session report. The original was authored
in the AoU instance clone and was NOT pushed before cluster teardown, so the standalone
file did not survive; this faithful reconstruction preserves the narrative. Raw command
transcripts (full `gsutil ls -l` listings) from the original may be lost — augment here
if recovered from local download / terminal scrollback.
**Canonical debug session:** `.planning/debug/m3-gateb-nano-sample-axis-collapse.md`
**Confirms:** root-cause mechanism for the canonical session (sample-axis collapse, NOT
checkpoint I/O corruption, NOT the colon/URI bug).

## Run environment (all confirmed working before the failure)

- Cluster: **JupyterLab Spark cluster for AoU (Dataproc)**, "Software to install" =
  **Hail (Spark 3.5.3, hail 0.2.135)** — the framework selector that the old
  `Spark_20260602` preset had set to None (why Hail was missing last attempt).
- Sizing: **n2-standard-16 master + 4× n2-standard-16 workers**, non-preemptible.
  App id `e92b9cdf-4dc7-4db4-9dc4-66c26efdce3e`.
- Hail verified first: `pip show hail` → 0.2.135; `import hail` OK.
- Repo: public HTTPS clone, `git checkout -f m3-W2-aou-deltas` → HEAD **603482d**
  (incl. c97bf4e / a96f2cf).
- `/home/jupyter → /home/dataproc` symlink recreated (per-instance; did not persist).
- `INTERVAL = "chr22:16000000-18000000"` (2 Mb nano window).
- **YARN-not-local confirmed:** Cell 1b printed `spark.master : yarn`,
  `spark.executor.cores : 1`, Hail 0.2.135. Cell 1c: suffix `_chr22_16000000_18000000`,
  du soft-floor scaled to 2,000,000 bytes.

## What worked (regression-clean this run)

- **Colon-sanitization fix (a96f2cf) HELD** — first intermediate wrote cleanly:
  `…/ld/intermediate/mt_afr_post_split_chr22_16000000_18000000.mt` (sanitized, no colon).
  The prior `java.net.URISyntaxException` did NOT recur.
- Hail ran on **YARN (not local)** under the cores=1 / mem=5g catastrophe config.

## The failure

```
RuntimeError: checkpoint at gs://rw-migration-aou-rw-476cdac2/ld/intermediate/
mt_afr_post_sample_qc_chr22_16000000_18000000.mt (phase=post_sample_qc)
returned empty MT: 118903 rows x 0 cols.
```

## Byte-level forensic chain (the decisive evidence)

- **post_split** MT: `cols/rows/parts/part-0` = **245,342 bytes** (fully populated sample
  table) — i.e. the ancestry filter + relatedness anti-join (Phase 1) did NOT drop
  samples.
- **post_sample_qc** MT: the same partition = **35 bytes** — a parquet file with schema
  but **zero data rows**.
- **Hail's own write-time log:** *"wrote matrix table with 118903 rows and 0 columns."*
  → the MT genuinely had **0 columns in memory before `mt.checkpoint()` was ever called**.

## Interpretation

- **Rules OUT** the m3-W1 "_SUCCESS written over missing bytes" finalize-corruption
  theory: the bytes are honestly present; the columns are honestly gone.
- **Variant (row) axis survived intact** at 118,903 rows; **only the sample axis
  vanished** → a predicate inside the **sample-QC** step dropped every sample.
- `_assert_checkpoint_nonempty` fired exactly as designed (caught it before any
  downstream cohort defined on top of an empty MT).

## Disposition (corrected from the initial operator read)

Initial operator read was "cheap-tier FAIL → pivot to 1000G AFR." **Corrected after
triangulated diagnosis:** this is a **scale-DEPENDENT nano-tier artifact** — the
unguarded `sqc.call_rate >= 0.98` sample filter measured over ~119K un-variant-QC'd
variants on a 2 Mb window. It would PASS at whole-chr22 / genome scale. It is a missing
degeneracy guard in the harness, **NOT** evidence the AoU build is broken, and **NOT** a
1000G pivot trigger (`[[feedback_no_1000g_ld_pivot]]`, `[[feedback_rigor_over_speed]]`).
Fix landed (guard + truthful provenance + assertion-message fix + regression test); see
canonical session doc. Revalidate via a Gate B nano re-fire, then Gate C.
