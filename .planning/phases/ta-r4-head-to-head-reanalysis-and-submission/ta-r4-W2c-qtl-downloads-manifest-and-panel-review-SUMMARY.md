---
plan: ta-r4-W2c-qtl-downloads-manifest-and-panel-review
status: complete
completed: 2026-10-28
commits: [c89a22b8, 33d5f640, 14318720, e3afa4dd, f288ab82, 57da00e6, 5c0bb92b]
---

# ta-r4 W2c SUMMARY

Tasks 1-3 were executed by a gsd-executor; Task 4 (sign-off) was recorded by the orchestrator
from Carter's verbatim reply. Full evidence is in `ta-r4-LOG.md` (2026-10-27 and 2026-10-28 entries).

## Task 1: GTEx v8 QTL downloads
- 98 files (49 tissues x eqtl/sqtl) + 98 .tbi; `FINISHED todo=98 failed=0`; verify awk `98 0`.
- Byte identity: sum(size_bytes) 191,965,693,189 + sum(tbi_size_bytes) 157,577,577 = 192,123,270,766 = HEAD_OK total.
- No published md5 on EBI: every row reads "no published checksum".
- `manifests/qtl_downloads_sha256.tsv` committed in e3afa4dd.

## Task 2: static QTL-coloc manifest
- RED: 33d5f640 (`6 failed, 8 errors`, ImportError), re-observed 2026-10-28 with the module removed.
- `tier` negative controls all went RED, then were restored (schema check disabled, `tier` in COLUMNS, `tier` column in TSV, stroke rows dropped → `assert 93240 == (23310 * 5)`).
- Scope `full`. Rows 116,550 = 5 x 23,310 unique (region, source, tissue, feature); eqtl 105,745 + sqtl 10,805.
- Deterministic: two LSF builds and the committed file share sha256 `0f10d922…4ad8`. `test_qtl_manifest.py` 14 passed incl. r4_heavy (LSF 429989).
- `qtl_compute_estimate.tsv`: full / tissues_frozen 232.8 core-h; eqtl_only / tissues_frozen+eqtl_only 211.2 core-h. t_row is a fixture lower bound, UNMEASURED on real data.
- Scope vs frozen layer (FINDING, raised in packet §7): 412 of the frozen layer's 1,274 rows have an R4 counterpart. The 862 without one are HLA_6p21 98 (inadmissible, D-24), SLC2A9 98 (legacy gene ID ENSG00000109107 absent from the R4 window), CXADR / F2RL1 / MC4R 98 each (legacy IDs have no rows in their own windows) and 372 source/tissue gaps (sQTL 359, eQTL 13). `tissues_frozen` == `full` (the frozen set is all 49 tissues).

## Task 3: review packet + wave close
- `ta-r4-W2-REVIEW-PACKET.md`, 9 sections, committed 57da00e6, pushed.
- Full suite: 1868 ids / 1818 passed / 0 failed / 50 skipped; vs W2b, 0 removed, 0 changed, 14 added (test_qtl_manifest).

## Task 4: Carter sign-off
Resume payload, verbatim:

```
carter-approved 2026-10-28
ukb_native: native
qtl_scope: full
trait.hypertension.EUR.sdY: 20.7
```

- raw_sha256 `26e3c3020026af8616c5751f9fcacf11988aefeb4f932d693e973b7b8bfa2f3c` (`signoffs/W2c-T4.yaml`).
- Two earlier replies were WAIT and recorded nothing: wrong date format (signoff rc=1), and placeholders left unfilled.
- `config/ta_r4/review_decisions.yaml` was written from the recorded fields; trait_manifest hypertension.EUR sdY 20.7, source `Carter 2026-10-28`, 0 UNRESOLVED.
- `signoff verify W2c-T4` rc 0; test_signoff + test_signoffs + test_qtl_manifest (not r4_heavy) 70 passed.
- Negative control: setting `qtl_scope: eqtl_only` in review_decisions → `1 failed` ("review_decisions qtl_scope='eqtl_only' != W2c-T4 'full'"); restored → 22 passed.
- stroke.AFR stays GCST90104553 (small vessel stroke). The packet had no reply key for it, and Carter raised no change.

## Deviations
- The executor's first heavy verify ran on login01 for about 2.5 minutes. It was killed with no output change; every later heavy run used LSF.
- `config/bsub_wrapper.sh` appends `-W` after the arguments, so with a string command the limit is never applied. The executor worked around it with jobscript files. Not fixed here.
