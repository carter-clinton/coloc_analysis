# AoU workspace storage — full inventory, integrity proofs, and the reclaim plan

**Date:** 2026-09-14 → 2026-09-16 · **Workspace:** `aou-rw-476cdac2` · **Project:** `wb-perky-corn-6639`
**Status:** ⛔ **INVENTORY ONLY — NOTHING HAS BEEN DELETED FROM THE BUCKET.** Every reclaim below is
**pending a Carter decision**. Agents never delete cloud resources; Carter runs the deletion himself.
**Predecessor:** the 2026-09-10 cost block in `.planning/STATE.md` / `HANDOFF.json` (four STOPPED
Dataproc clusters deleted, ~$14k leak closed).

All sizes were measured in-perimeter by the AoU browser agent (read-only) from a single saved
object listing of `ld/` (`/tmp/ld_du.txt`, 1,788,824 lines, matching two prior enumerations).
**Every partition below was reconciled on the NCSU side to ZERO residual in bytes AND objects.**

---

## 1. What changed on the compute side since the 2026-09-10 close

| action | result |
|---|---|
| Inventory of `AoU_Jupyter_ComputeEngine_20260608` local disk | 37 G used of 492 G. **No self-report / sidecar / selfid / D-M3-07 / TSV extract.** Only a 77 MB GitHub clone, 7 small IAM-probe files, `load-env.sh` + `load-env`. |
| Probe files preserved | 7 files → `gs://rw-migration-aou-rw-476cdac2/provenance/vm_20260608_probes/`, 2,921 B, **all md5 BOTH-MATCHING** (`iam_probe.sh` 8b33b8df…, `iam_probe2.sh` 792b5ffb…, `iam_probe3.sh` ae08d93f…, `dataproc_iam_probe.json` 485c76de…, `describe_err.txt` d5c16f0f…, `iam_probe_err.txt` and `cluster_20260604_config.yaml` both 0-byte d41d8cd9… — **empty on the VM too**). |
| `load-env.sh` / `load-env` preserved | same prefix, 9,389,635 B. `load-env.sh` md5 **1cba2aee540018b363e5188d98016afe** matches; `load-env` size-matched only. ⚠ `load-env` is **the Workbench platform's own 9.4 MB ELF env-loader binary**, not project data — it carries no project provenance. |
| `20260608` **DELETED** by Carter | Confirmed at **Workbench app-registry level only** (Apps tab lists only `20260626b`, Stopped, $0.06/hr). ⚠ Raw `gcloud compute instances list` **not re-run** — the only in-perimeter shell was on the deleted VM, and the Console is refused out-of-perimeter by VPC-SC. **Run it the next time `20260626b` starts.** |
| AoU platform incident | "App Startup Delays" (Sept 2026): **previously-created apps** may provision slowly or never; new apps are fixed. Support article 53568084254228. `20260608` sat in Provisioning ~75+ min before starting. |

**Only remaining app: `aoujupytercomputeengine20260626b` — STOPPED — its reattachable PD holds the 379 GB bfile.**

---

## 2. The workspace bucket — `gs://rw-migration-aou-rw-476cdac2`

### 2a. `ld/` = **45,519,841,557,487 B / 1,788,824 objects** (~41.4 TiB, 99.3% of the bucket)

**182 MatrixTables = 8 per-chromosome sets × 22 + 6 singletons. No `.mt` exists outside `ld/`.**

⚠ The 8 sets are **NOT superseded reruns.** They are **two checkpoint stages** (`post_split`,
`post_variant_qc`) × **four cohort builds** (AFR, EUR, AFR-sens clean, AFR-sens contaminated).

| partition | bytes | objects |
|---|---:|---:|
| `ld/intermediate/mt_afr_post_split_chr*` (22/22) | 5,316,397,930,388 | 148,618 |
| `ld/intermediate/mt_afr_post_variant_qc_chr*` (22/22) | 1,638,076,426,058 | 148,525 |
| `ld/intermediate/mt_eur_post_split_chr*` (22/22) | 13,259,819,890,464 | 148,700 |
| `ld/intermediate/mt_eur_post_variant_qc_chr*` (22/22) | 3,474,821,008,794 | 148,523 |
| `ld/intermediate/mt_afr_pca_selfid_post_split_chr*` (22/22) | 4,521,348,968,433 | 148,614 |
| `ld/intermediate/mt_afr_pca_selfid_post_variant_qc_chr*` (22/22) | 1,399,955,178,715 | 148,516 |
| `ld/intermediate/mt_afr_post_split.mt` — **orphan partial whole-genome checkpoint** | 441,609,776,928 | 695 |
| `ld/intermediate/` other | 141,763 | 138 |
| `ld/_forensics/contaminated_afr_selfid_noop_20260608/intermediate/` (2 sets 22/22 + other) | 6,954,941,334,673 | 296,698 |
| `ld/_forensics/contaminated_afr_selfid_noop_20260608/mt_afr_pca_selfid_qc.mt` | 1,607,108,093,330 | 147,787 |
| `ld/_forensics/` root logs/json (hail_*.log, jstack_*, *_capture.json) | 40,078,737 | 14 |
| **`ld/mt_afr_qc.mt`** (live final) | 1,607,107,496,236 | 147,810 |
| **`ld/mt_eur_qc.mt`** (live final) | 3,435,886,633,904 | 147,806 |
| **`ld/mt_afr_pca_selfid_qc.mt`** (live final) | 1,383,638,976,285 | 147,798 |
| `ld/afr_native_panel/` (pinned bfile + panel TSV + tools/plink1.9) | 380,584,276,457 | 5 |
| `ld/AFR_aou/` (Stage A/B banked outputs) | 59,735,526,381 | 13 |
| `ld/cost_probe_m3d/` | 36,686,415,849 | 327 |
| `ld/pilot_plink/` | 1,175,232,599 | 3 |
| `ld/_probe_synthetic.mt` | 768,321,302 | 8,226 |
| `ld/EUR_aou/` | 119,207,151 | 6 |
| `ld/aux/` | 20,643,040 | 1 |
| `ld/` zero-byte folder-marker object | 0 | 1 |
| **SUM — reconciled 2026-09-16, residual 0 bytes / 0 objects** | **45,519,841,557,487** | **1,788,824** |

### 2b. Everything outside `ld/` (< 350 MB total)

`coloc_analysis/` 136,422,565 B (1,708 obj) · `provenance/` 108,390,543 B + 2,921 + 9,389,635 added
2026-09-16 · `forensics/` 64,689,041 · `forensics_archive/` 14,383,272 · `m3-W2-forensics/` 11,442,325 ·
`notebooks/` 459,516 · `m3-W1-forensics/` 373,666 · `Untitled.ipynb` 14,369 · `.ipynb_checkpoints/` 72.

### 2c. Orphan Dataproc buckets — **real names differ from the Workbench resource labels**

`gs://dataproc-staging-wb-perky-corn-6639` 90,131,951 B (~86 MiB) ·
`gs://dataproc-temp-wb-perky-corn-6639` 8,747,580,737 B (~8.1 GiB).
⚠ `gs://dataproc-{staging,temp}-aou-rw-476cdac2` **do not exist** (404) — those are Workbench labels.
Together ~$0.17/month: **not a cost lever**, but they serve clusters that no longer exist.

---

## 3. Integrity proofs (all read-only, all PASSED)

### 3a. The three live finals match `cohort_summary_m3.tsv` EXACTLY

Hail-free, from each MT's own metadata. ⚠ In this Hail layout `partitionCounts` is **ABSENT**; the counts
live at **`components.partition_counts.counts`** in the TableSpec-level `metadata.json.gz` files
(MT-level, `rows/`, `cols/`, `entries/`). The RVD-level files (`rows/rows/`, `entries/rows/`) hold
`_partFiles` and no counts.

| final | rows (partitions) | cols | banked | entries vs rows partition list |
|---|---|---|---|---|
| `mt_afr_qc.mt` | 20,767,864 (36,944) | 73,122 | 73,122 × 20,767,864 ✅ | **identical element-wise** |
| `mt_eur_qc.mt` | 11,375,140 (36,943) | 220,098 | 220,098 × 11,375,140 ✅ | **identical element-wise** |
| `mt_afr_pca_selfid_qc.mt` | 20,817,925 (36,941) | 62,557 | 62,557 × 20,817,925 ✅ | **identical element-wise** |

**No final carries a `_VALIDATED` marker — and that is EXPECTED, not a warning.**
`src/python/aou_ld_panel.py` `_final_is_trustworthy`: *"CONTENTS are the sole source of truth … the three
already-banked cohorts carry no `_VALIDATED` and validate True via contents."* `_VALIDATED` postdates them
(`f931446`, 2026-06-11). All three `_SUCCESS` markers sit over 1.38–3.43 TB of real `entries/` bytes, so
the June empty-final catastrophe signature is **absent**.

### 3b. The June no-op contamination — PROVEN numerically

`ld/_forensics/contaminated_afr_selfid_noop_20260608/mt_afr_pca_selfid_qc.mt`:
**cols = 73,122** (a working self-report filter gives ≤ 62,557), **rows = 20,767,864 — identical to
`mt_afr_qc.mt`**, 36,941 partitions, entries-vs-rows lists identical. Bytes differ from `mt_afr_qc.mt` by
only **597,094 B**. **The "self-report" cohort is the full AFR cohort under another name.**
These numbers are the evidence of the bug; the 8.56 TB of bytes are needed only if a credit claim
requires the artifact itself (see §5).

### 3c. The pinned bfile — the bucket copy IS the disclosure anchor

`ld/afr_native_panel/bfile/afr_cohort.bed` 379,657,321,787 B ✅ · `.bim` 883,834,306 B ✅ ·
`.fam` 1,389,318 B · panel TSV 254 B · `tools/plink1.9` 41,730,792 B.
**`.bim` sha256 = `9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99`** — byte-for-byte the
anchor in `.planning/osf_deviations.md`. (The 379 GB `.bed` was deliberately never streamed.)

---

## 4. Classification — reconciles to the byte

| label | what | bytes | objects | ~$/mo* |
|---|---|---:|---:|---:|
| **KEEP** | 3 proven finals, pinned bfile, `AFR_aou`, `pilot_plink`, `EUR_aou`, `aux`, `_forensics` root logs, all non-`ld/` prefixes | 6,868,308,070,790 | 443,457 | ~137 |
| **DECIDE — intermediates** | `ld/intermediate/**` (all 8 checkpoint sets + orphan + other) | 30,052,029,321,543 | 892,329 | ~601 |
| **DECIDE — credit claim** | `ld/_forensics/contaminated_afr_selfid_noop_20260608/**` | 8,562,049,428,003 | 444,485 | ~171 |
| **RECLAIM** | `ld/_probe_synthetic.mt/**` + `ld/cost_probe_m3d/**` | 37,454,737,151 | 8,553 | ~1 |
| total reclaim candidates | | **38,651,533,486,697** | **1,345,367** | **~773** |

\* at ~$0.020/GB-month Standard storage; an estimate, not an invoice line.
**Honest floor after full reclaim: ~$137/mo storage + `20260626b`'s PD ≈ ~$180/mo — not $0.** That residual
is the price of keeping the pinned `C2024Q3R8` finals and the anchored bfile verifiable. A rebuild on the
newly published CDR would **not** reproduce them.

**Why the intermediates are a decision, not an automatic reclaim.** `_final_is_trustworthy` names them the
recovery path for a corrupted final: *"re-finalize via `force_fresh=False` from the still-intact 22
per-chrom intermediates (a finalize-only re-drive, minutes not hours)."* Deleting them turns that into a
full rebuild from a CDR that is no longer the default. **Recommendation: reclaim** — all three finals are
now proven exact partition-by-partition, and the failure they insure against needs a killed *re-write*,
which nothing planned performs. Irreversible; Carter's call.

---

## 5. ⛔ DECISIONS PENDING — all Carter's

1. **Daily spend reading.** Falsifiable test recorded 2026-09-10: ~$93/day → **~$30/day if the 92 cluster
   nodes' disks released**; still ~$90 means they did not. Not yet reported.
2. **Credit claim — yes/no.** Did Carter file, or intend, an AoU credit request for the June no-op? Records
   call `_forensics` "Track-1 credit evidence" (`STATE.md:1778`, `:1900`, `:1915`) **and** separately list
   deleting this exact tree as a planned ~7.8 TiB reclaim (`STATE.md:1802`). "Track-1 credit" is **defined
   nowhere in the repo.** Unanswered.
3. **Intermediates — go/no-go.** Unanswered.

## 6. The deletion procedure — ONLY after §5, run by Carter

**Order is mandatory: (1) this record is committed → (2) dry-run reconciles → (3) delete → (4) verify.**

```bash
B=gs://rw-migration-aou-rw-476cdac2
gcloud storage buckets describe $B --format="value(soft_delete_policy)"
for p in 'ld/intermediate/**' 'ld/_forensics/contaminated_afr_selfid_noop_20260608/**' \
         'ld/_probe_synthetic.mt/**' 'ld/cost_probe_m3d/**'; do
  echo "== $p"; timeout 1800 gsutil ls -l "$B/$p" | tail -1 ; echo "EXIT=${PIPESTATUS[0]}"
done
```

Each `TOTAL:` line must equal the §4 row **exactly** — intermediate `30,052,029,321,543 B / 892,329`,
contaminated `8,562,049,428,003 / 444,485`, `_probe_synthetic.mt` `768,321,302 / 8,226`, `cost_probe_m3d`
`36,686,415,849 / 327`. **Any mismatch means the pattern reaches something unintended — STOP.**

⚠ **Soft delete bills.** Newer GCS buckets retain deleted objects (default 7 days) and those still charge.
If the policy shows retention, the cost falls only after the window. **Keep it** — it is a 7-day undo on an
irreversible 38 TB delete.

## 7. Command traps hit during this inventory (all caught by the agent, most introduced by my cards)

- `gsutil du -s <prefix>` returned **0 bytes with EXIT 0** on `ld/` over 1.79 M objects — a folder-marker
  false-empty. Use an object-wildcard listing and sum it.
- `gsutil ls -d '**/*.mt'` **cannot** match a MatrixTable: `**` matches *objects*, a `.mt` is a *prefix*.
- `gsutil ls -r '<mt>/'` with a trailing slash matched only the folder marker → instantly empty, EXIT 0.
- `awk printf %d` clipped a 45 TB sum to exactly **2,147,483,647** (INT32_MAX). Use `%.0f`.
- `gcloud … | sort | uniq -c; echo $?` reports **`uniq`'s** exit code. Use `${PIPESTATUS[0]}`.
- `gcloud compute disks list` **exits 0 on a permission denial** with empty output.
- Hail `partitionCounts` is **absent** in this layout — see §3a for the real key.
- A bare `du -sh /home/jupyter/*` walked three **gcsfuse bucket mounts** over the network.

## 8. Corrections to my own statements in this period

- I said the D-M3-07 extract might be one-of-one on `20260608`; measured: **it was not on that VM at all.**
- I used **63,312** as the AFR-sens sample count; that is the self-report filter's output *before* sample QC.
  The banked final is **62,557**.
- I reported a **−43,740 B residual**; it was **my double count** of a line the agent had already included.
- I called `load-env` "June-era setup context"; it is **platform tooling**.
- I recommended deleting the MTs and bfile as "regenerable"; **withdrawn** — the newly published CDR means a
  rebuild does not reproduce them, and the disclosure pins the `.bim` hash.
