# m3-W2 PILOT — native-tool (plink) AFR LD on ONE region (cost-feasibility probe)

**Date:** 2026-06-23 · **autonomous: false (COSTS MONEY, ~$5–25).** · **Goal:** measure the real cost of
computing one AFR region's banded LD with **plink1.9 on a single node** vs the Hail BlockMatrix path
(which cost ~24 cluster-h for this exact cell), to decide the m3 re-architecture
(`m3-W2-cost-effective-rearchitecture.md`). This is a direct apples-to-apples: **same cell** the Hail v2
probe measured. Operating manual = the `aou-ld-pipeline` skill. Token-free handback (no push token in the
Workbench — `cat` the artifacts, NCSU reconstructs + pushes; see [[feedback_push_ncsu_before_aou_clone_fire]]).

## The cell (identical to the v2 Hail probe)
`m2_region_00040__sub00` **AFR** · chr12 **GRCh38 window 37,463,740–45,398,515** (~7.93 Mb) · buffer 3 Mb ·
expected n_var ≈ 64,176 after MAF ≥ 0.005. Hail baseline for this cell: 168 blocks, **57.4 min on 24
n2-standard-16 workers = ~24 cluster-h**, .bm ~18.5 GiB.

## Cluster (cheap — this is single-node plink + a light one-region export)
- **START HAIL `20260604`** (the known-good framework=HAIL cluster; per `aou-ld-pipeline` skill / memory
  [[reference_aou_hail_cluster_create_time_config]]). **To minimize cost, RESIZE workers down to 2** (the
  export of one region is light; plink runs SINGLE-NODE on the master n2-standard-16, 16 vCPU / 64 GB) →
  ~$3–5/hr instead of ~$20/hr. (If resizing is friction, just run it as-is and stop promptly.)
- The baked AOU env guards still apply (bucket pin, `git checkout -f`, etc.) — follow the skill's
  fresh-clone checklist. We are READING the already-built `gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt`
  (canonical bucket, not requester-pays WGS), so the requester-pays lever is not needed for this pilot.

## STEP 0 — sync + confirm
1. `cd ~/coloc_analysis && git pull && git checkout -f && git rev-parse HEAD`.
2. Confirm the cohort MT: read `gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt`, `mt.count_cols()` → **73,122**.
   (`_SUCCESS` is not evidence — count it; skill invariant 1.)

## STEP 1 — export ONE region to plink (Hail, on the cluster) — measure export wall + size
```python
import hail as hl, time
mt = hl.read_matrix_table("gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt")
# Match the MT's contig convention (confirm 'chr12' vs '12' from mt.locus first):
iv = hl.parse_locus_interval("chr12:37463740-45398515", reference_genome="GRCh38")
mt = hl.filter_intervals(mt, [iv])
# MAF >= 0.005 (the AFR rare-signal export convention; skill LD-compute specifics)
mt = hl.variant_qc(mt)
mt = mt.filter_rows(hl.min(mt.variant_qc.AF) >= 0.005)
n_var = mt.count_rows(); print("n_var =", n_var)   # expect ~64,176
t0 = time.time()
hl.export_plink(mt, "gs://rw-migration-aou-rw-476cdac2/ld/pilot_plink/m2_region_00040__sub00_AFR",
                ind_id = mt.s)   # writes .bed/.bim/.fam
print("export_wall_min =", (time.time()-t0)/60.0)
```
Record `n_var`, `export_wall_min`, and `gsutil du -s …/pilot_plink/…` (the .bed size).

## STEP 2 — native LD with plink1.9 on the master (single node) — measure wall + RAM + output size
```bash
# localize plink1.9 + the exported bed
mkdir -p ~/pilot && cd ~/pilot
wget -q https://s3.amazonaws.com/plink1-assets/plink_linux_x86_64_20231211.zip && unzip -o plink_linux_x86_64_20231211.zip   # or any plink1.9 build
gsutil -m cp "gs://rw-migration-aou-rw-476cdac2/ld/pilot_plink/m2_region_00040__sub00_AFR.*" .
B=m2_region_00040__sub00_AFR
# (a) BANDED windowed LD (matches the production banded .npz design): all in-band pairs within 3 Mb, no r2 floor
/usr/bin/time -v ./plink --bfile $B --r gz --keep-allele-order \
    --ld-window-kb 3000 --ld-window 9999999 --ld-window-r2 0 \
    --threads 16 --out ${B}_band 2> band_time.txt
# (b) DENSE square (the SuSiE-ready full matrix) — for timing/size comparison (may be ~16 GB; skip if disk-tight)
/usr/bin/time -v ./plink --bfile $B --r square bin4 --keep-allele-order \
    --threads 16 --out ${B}_square 2> square_time.txt
ls -la ${B}_band.ld.gz ${B}_square.ld.bin 2>/dev/null
grep -E "Elapsed|Maximum resident" band_time.txt square_time.txt
```
**`--keep-allele-order` is MANDATORY** (else LD signs mismatch the GWAS z-scores — a known susieR failure).
Record from `/usr/bin/time -v`: **Elapsed (wall)** and **Maximum resident set size (peak RAM)** for each;
and the **output file sizes**. (plink's binding constraint is usually output size, not RAM — capture both.)

## STEP 3 — verify the matrix is real (not just that plink exited 0)
- Banded: `zcat ${B}_band.ld.gz | head` — columns are CHR_A BP_A SNP_A CHR_B BP_B SNP_B R; confirm R ∈ [-1,1],
  signed, and the in-band span ≤ 3 Mb. Count pairs: `zcat ${B}_band.ld.gz | wc -l`.
- Square: load `${B}_square.ld.bin` (n_var² float32) in numpy, assert shape = (n_var, n_var), diagonal ≈ 1,
  off-diagonal ∈ [-1,1], symmetric. Spot-check a couple of high-LD neighboring SNPs.

## STEP 4 — record + extrapolate + shutdown
Write `m3-W2-pilot-plink-native.tsv` (one row):
`region_id  ancestry  n_var  export_wall_min  bed_size_gib  plink_band_wall_min  plink_band_peak_ram_gib  band_output_gib  plink_square_wall_min  square_output_gib  notes`
**Extrapolation (put in a short `m3-W2-pilot-report.md`):**
- AFR full sweep = `plink_band_wall_min × 276 regions / 60` = VM-hours →
  × **$4.19/hr (n2-highmem-64 on-demand)** and × **$1.49/hr (Spot)** = $ for the whole AFR LD panel.
- Compare to the Hail projection (~24 cluster-h THIS cell; ~17k cluster-h ≈ AFR-half of the 34k).
- **Verdict: does native plink land the full AFR panel under ~$3–4k?** (and which output mode — banded vs
  square — is practical given the size).
Then **STOP `20260604`** (resize back / pause), verify `$0`, write `m3-W2-cluster-shutdown.md` (pilot).

## Handback (token-free)
`cat` these to the terminal for NCSU to reconstruct + push: `m3-W2-pilot-plink-native.tsv`,
`m3-W2-pilot-report.md`, `m3-W2-cluster-shutdown.md`, plus the two `*_time.txt`. Then STOP the cluster. Ping
**"pilot-recorded"**. (Don't push from the Workbench — no token; NCSU pushes.)

## Cost controls / do-NOT
- This is ~$5–25. Stop the cluster as soon as STEP 4 is recorded. Kill only on a genuine wedge.
- Do NOT export individual-level data off-perimeter — only the **aggregate LD matrix** egresses later (this
  pilot keeps everything in-bucket; nothing leaves the perimeter except the small TSV/report via `cat`).
- Do NOT start 20260620/20260617 (no Hail). Do NOT delete the cohort MT.
- If `export_plink` is slow/odd, `export_bgen` + LDstore2 is the alternative tool (note it, don't switch mid-pilot).
