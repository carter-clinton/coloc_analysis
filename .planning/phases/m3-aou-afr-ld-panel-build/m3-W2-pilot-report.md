# m3-W2 PILOT report — native-plink AFR LD cost-feasibility (one region)

**Date:** 2026-06-24 · **Verdict: GREEN** · brief = `m3-W2-PILOT-plink-native-BRIEF.md`

## Provenance
Reconstructed on the NCSU node from the AoU agent's **token-free `cat`-handback**
(2026-06-24). The on-disk cluster copies (`m3-W2-pilot-plink-native.tsv`,
`m3-W2-pilot-report.md`, the two `*_time.txt`) could **not** be retrieved verbatim —
the terminal websocket dropped as cluster `20260604` began stopping. All measurements
below are as reported by the agent before shutdown. **Source of truth** = the in-bucket
pilot outputs `gs://rw-migration-aou-rw-476cdac2/ld/pilot_plink/m2_region_00040__sub00_AFR.*`
+ the handback numbers. The two `*_time.txt` files were not cat'd back and are not
reconstructable, but their load-bearing values (Elapsed wall, peak RAM) are captured in
`m3-W2-pilot-plink-native.tsv`.

## The cell (identical to the Hail v2 probe — direct apples-to-apples)
`m2_region_00040__sub00` **AFR** · chr12 **GRCh38 37,463,740–45,398,515** (~7.93 Mb) ·
buffer 3 Mb · MAF ≥ 0.005. STEP-0 confirm: `count_cols = 73,122` ✓ (matches runbook);
contig convention `chr1`-style ✓. `n_var = 64,060` (expected ~64,176 ✓).
Hail baseline for this exact cell: 168 blocks, 57.4 min on 24 n2-standard-16 workers =
**~24 cluster-h**, `.bm` ~18.5 GiB.

## Measurements
Master VM = `n2-standard-16` (16 vCPU / 64 GB); plink1.9 v1.90b7.2 ran single-node.

| metric | export | banded (`--r gz`) | square (`--r square bin4`) |
|---|---|---|---|
| wall (min) | 0.555 (export_plink call; full run 20m15s, dominated by the one-time `count_cols` scan) | 25.446 | 56.224 |
| peak RAM (GiB) | — | 16.68 | 17.89 |
| output | `.bed/.bim/.fam` = 1.090 GiB | `.ld.gz` = 16.55 GiB | `.ld.bin` = 15.29 GiB |

Both runs used `--keep-allele-order` (mandatory — else LD signs mismatch GWAS z-scores;
known susieR failure). Verification:
- **Banded** `.ld.gz`: columns `CHR_A BP_A SNP_A CHR_B BP_B SNP_B R`; signed R ∈ [−1,1];
  in-band span ≤ 3 Mb. Pair count ~400M (**estimated from output size** — exact `wc -l`
  over the 16.5 GiB gzip was interrupted to conserve cost).
- **Square** `.ld.bin`: numpy shape (64060, 64060) = exactly 64060² float32; diag = 1.0;
  off-diag ∈ [−1,1]; symmetric (`sym_check = 0.0`).

## Extrapolation to the full AFR panel (276 regions)
`VM-hours = plink_wall_min × 276 / 60`, then × hourly VM rate.

| mode | VM-hours | × $1.49/hr (Spot) | × $4.19/hr (on-demand) |
|---|---|---|---|
| banded | 25.446 × 276 / 60 = **117.05** | **$174** | **$490** |
| square | 56.224 × 276 / 60 = **258.6** | **$385** | **$1,084** |

Export is one-time/amortized in the export-once design (per-region `export_plink` ~33 s;
the ~20 min `count_cols` scan is paid once for the whole cohort), so it is negligible in
the panel total.

## Verdict — GREEN
**Native plink lands the full AFR LD panel well under the $3–4k budget** in every mode:
banded ~$174–490, square ~$385–1,084. This is **~1–2 orders of magnitude cheaper** than
the Hail BlockMatrix path (~24 cluster-h for THIS cell → ~17k cluster-h for the AFR half
of the 34k-cluster-h projection that returned NOT-GREEN). **Move 2** of the cost
re-architecture (`m3-W2-cost-effective-rearchitecture.md`) is confirmed: compute AFR LD
in-house but **natively on a single Spot VM**, not on a 24-node Hail cluster.

## Recommendation (output mode)
Use **square `bin4`** downstream — SuSiE-ready, fixed-size, random-access, verified
symmetric — unless disk-tight, in which case use **banded** with an r² floor. Footprint
across 276 regions ≈ **~4.6 TB square / ~4.2 TB banded**.

## Caveats (carry into the m3-02e re-plan)
1. **VM-type mismatch.** The $4.19/$1.49 rates are labelled `n2-highmem-64` in the brief,
   but the pilot VM was `n2-standard-16`. The $ figures are therefore a **conservative
   bound**; the production-VM wall-time should be re-measured before the m3-02e budget is
   committed (a 64-vCPU VM with `--threads` raised could finish faster, but bills more
   per hour).
2. **Banded pair count is estimated** (~400M, from output size), not an exact `wc -l`.
3. **Export wall** (0.555 min) is the `export_plink` call only; the one-time `count_cols`
   full-MT scan (~20 min) amortizes across all regions in the export-once design.
