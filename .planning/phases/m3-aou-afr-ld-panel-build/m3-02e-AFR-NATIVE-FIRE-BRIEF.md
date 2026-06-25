# m3-02e AFR-NATIVE FIRE BRIEF — turnkey in-perimeter native-plink LD loop

**Task:** m3-02e-T4 (`checkpoint:human-action`, `gate=blocking`, `autonomous:false`).
**Who fires:** Carter (in the AoU perimeter). This is the **ONLY billable step** in
m3-02e; the `--auto` gate cannot cross it.
**Going-in verdict:** native-plink PILOT was **GREEN** (`m3-W2-pilot-report.md`,
2026-06-24). This brief turns the one-cell pilot into the full 276-region AFR panel.
**Cost design:** Move 1 of the accepted re-architecture
(`m3-W2-cost-effective-rearchitecture.md`) — AFR LD in-house but **NATIVE** plink1.9
on a single Spot VM, **not** Hail BlockMatrix on a 24-node cluster
(~34k cluster-h, NOT taken).

> Resume signal when done: type **`native-panel-recorded`** (then NCSU
> reconstructs + pushes), or describe issues / a re-measure budget overrun / a
> verification failure.

---

## GATE CONDITIONS (read first — these are gates, not footnotes)

These three PILOT CAVEATS are GATE conditions on committing the budget:

1. **PRODUCTION-VM RE-MEASURE (blocking stop-gate).** The pilot's $4.19 (on-demand)
   / $1.49 (Spot) hourly rates are labelled **n2-highmem-64**, but the pilot
   actually ran on an **n2-standard-16** master. Before the full 276-region loop
   commits budget, re-measure the per-region wall on the **actual production VM
   type** (Step 3). If the re-measured ×276 projection blows the $3–4k budget,
   **STOP and re-cost** before the loop.
2. **Banded pair count is ESTIMATED** (~400M, inferred from the .ld.gz size), not
   an exact `wc -l`. If you choose the banded alternate, capture the real count.
3. **Export is one-time/amortized.** Per-region `export_plink` is ~33 s, but the
   one-time `count_cols` scan is ~20 min — paid ONCE in Step 2, not per region.

### PILOT GOING-IN NUMBERS (the budget baseline)

Cell `m2_region_00040__sub00` AFR, chr12 GRCh38 37,463,740–45,398,515 (~7.93 Mb),
buffer 3 Mb, MAF ≥ 0.005, n_var = 64,060, count_cols = 73,122. plink1.9 v1.90b7.2,
single-node n2-standard-16:

| mode | per-region wall | peak RAM | output | ×276 VM-h | Spot | on-demand |
|------|-----------------|----------|--------|-----------|------|-----------|
| **square** `--r square bin4` | 56.224 min | 17.89 GiB | `.ld.bin` 15.29 GiB (64060² f32, diag 1.0, sym_check 0.0) | **258.6** | **$385** | **$1,084** |
| banded `--r gz` (3000 kb, r2 0) | 25.446 min | 16.68 GiB | `.ld.gz` 16.55 GiB (~400M pairs est.) | 117.05 | $174 | $490 |

Footprint ×276 ≈ ~4.6 TB square / ~4.2 TB banded. **Default = square bin4**
(SuSiE-ready, fixed-size, random-access, verified symmetric). Banded + r² floor is
the disk-tight documented alternate (D-02e-01).

---

## LIVE COORDINATES

- Workspace `aou-rw-476cdac2` · project `wb-perky-corn-6639` · bucket
  `gs://rw-migration-aou-rw-476cdac2`.
- **AFR cohort MT:** `gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt`
  (73,122 samples, COMPLETE_VERIFIED). The path is **`/ld/`, NOT `/ld/mt/`** —
  readers read URIs literally ([[feedback_aou_canonical_mt_path_no_mt_subdir]]).
- **Run branch:** `m3-W2-aou-deltas` (NOT main). **No Workbench push token** →
  token-free handback ([[feedback_push_ncsu_before_aou_clone_fire]]).
- **Manifest:** `config/ld_regions.tsv`, 276 AFR rows; the plink loop iterates each
  AFR row's `window_start_grch38..window_end_grch38` (GRCh38, AoU-native).
- **Code (landed by m3-02e Tasks 1–3, autonomous):**
  `src/python/aou_ld_panel.py::export_cohort_to_plink` + `build_plink_ld_command`
  (--keep-allele-order hardcoded), `src/python/plink_ld_to_npz.py` (square/banded
  → egress-clean .npz), `src/python/ld_egress_bundle.py` (per-chrom bundler, reuse).

---

## STEP 0 — PREFLIGHT (free)

1. **Push NCSU first**, then on the cluster home: `git pull` + `git checkout -f`;
   confirm **origin tip == local HEAD** (the m3-02e code must be present:
   `test -f src/python/plink_ld_to_npz.py`). [[feedback_push_ncsu_before_aou_clone_fire]]
2. Confirm the AFR cohort MT:
   ```
   gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt/    # /ld/ NOT /ld/mt/
   ```
   and (in-perimeter) `read_final_cohort_mt(...).count_cols() == 73,122` (the
   empty-final trust gate runs first; D-M3-10).
3. Confirm `config/ld_regions.tsv` has 276 AFR compute windows:
   ```
   awk -F'\t' 'NR>1 && $7=="AFR"' config/ld_regions.tsv | wc -l   # -> 276
   ```
4. **VM choice:** use a single **Spot VM** (~$1.49/hr) for the plink loop. The
   `hl.export_plink` step (Step 2) needs the Hail/MT toolchain — run it on the
   existing HAIL cluster 20260604 master (or a Hail-enabled VM), then run the
   plink loop on the Spot VM that mounts the exported bfile. Pick the cheapest
   valid path and **re-measure the production-VM wall (Step 3) before the loop.**

---

## STEP 1 — (covered by Step 0; no separate action)

---

## STEP 2 — EXPORT-ONCE (in-perimeter; the .bed NEVER egresses)

Run the export ONCE — the `count_cols` scan is amortized across all 276 regions:

```python
from aou_ld_panel import export_cohort_to_plink
export_cohort_to_plink(
    "gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt",
    "<bfile_prefix>",   # in-perimeter scratch / bucket
)
# -> <bfile_prefix>.bed/.bim/.fam (INDIVIDUAL-LEVEL — stays IN-PERIMETER, never egress)
```

**EGRESS BOUNDARY (REQ-AOU-LD-EGRESS / T-M3-02e-EGR):** the `.bed/.bim/.fam` is
individual-level genotype data and **stays in-perimeter**. It is consumed ONLY by
the in-perimeter plink LD loop. **Only** the per-region aggregate LD `.npz` + AF
ever crosses egress.

---

## STEP 3 — PRODUCTION-VM RE-MEASURE GATE (blocking)

Before the full loop, run ONE representative region on the **actual production VM**
and re-measure wall + peak RAM:

```python
from aou_ld_panel import build_plink_ld_command
cmd = build_plink_ld_command(
    bfile_prefix="<bfile_prefix>", chrom=12,
    from_bp=37463740, to_bp=45398515,
    out_prefix="m2_region_00040__sub00", mode="square",   # --keep-allele-order hardcoded
)
# run cmd via subprocess; record wall_min + peak_ram_gib
```

Project ×276: `wall_min × 276 / 60 = VM-h`; `VM-h × $/hr`. **If the projection
exceeds the $3–4k budget, STOP and re-cost.** (Pilot baseline: square ≈ 56.2
min/region → 258.6 VM-h → $385 Spot / $1,084 on-demand.) Banded is the disk-tight
alternate if square ×276 disk (~4.6 TB) is tight.

---

## STEP 4 — THE LOOP (276 AFR windows, single Spot VM)

Run the resumable native-plink loop driver **once**. It is idempotent across Spot
preemption: re-run this **verbatim** after any preemption and every content-valid
region is skipped via `_existing_region_npz` (the MED-6 byte-floor), so the re-run
banks only what's still missing — never a truncated `.npz`.

```bash
# STEP 4 — resumable native-plink loop (idempotent across Spot preemption)
python src/python/run_native_ld_panel.py \
    --manifest config/ld_regions.tsv \
    --bfile-prefix <bfile_prefix> \
    --out-dir <in_perimeter_out_dir> \
    --mode square \
    --ancestry AFR \
    --panel-tsv <out_dir>/m3-W2-native-plink-panel.tsv
# square (D-02e-01 default) -> lower_triangular=False ; --mode banded -> the
# disk-tight alternate (lower_triangular=True), set automatically per --mode.
```

The driver, per region: skips-if-banked (MED-6 floor); else issues plink ONLY via
`build_plink_ld_command` (so `--keep-allele-order` is always present); converts the
`.ld.bin`/`.ld.gz` to the egress-clean `.npz` via `plink_ld_to_npz`; **content-
verifies every region inline (D-M3-10)** — float32 / square / diag==1.0 / symmetric
(or the one-triangle invariant for banded) — and records `region_id, chr, n_var,
wall_min, peak_ram_gib, output_gib, status` to the panel TSV. A region that fails
verification is marked `verify_failed` and the loop **continues** (one bad region
never aborts the 276 loop).

**`m3-W2-native-plink-panel.tsv`** is the **REAL production-cost measurement** and
**REPLACES** the one-cell pilot TSV as the cost basis.

> The `--keep-allele-order` flag is hardcoded into `build_plink_ld_command` and is
> MANDATORY on every call (else LD signs mismatch the GWAS z → susieR failure;
> T-M3-02e-SIGN). The Move 3 `estimate_s` z-vs-LD guard catches any residual flip
> per region downstream.

---

## STEP 5 — VERIFY (D-M3-10; markers are NOT evidence)

The STEP-4 driver **already content-verifies every region inline** (D-M3-10) —
float32 / square / `diag==1.0` / symmetric (or the one-triangle invariant for
banded) — and records the per-region `status` (`ok` / `verify_failed`) in the panel
TSV. **The driver's inline gate is now the PRIMARY D-M3-10 check.** This STEP-5
standalone numpy check is the **spot re-check** (run it on a sample of regions, plus
any row whose panel `status` is not `ok`), not the primary gate. First skim the
panel TSV: any `status != ok` row must be re-fired (the loop banked nothing for it).

Per region, **contents-validate** — never trust `_SUCCESS` / file existence:

```bash
gsutil du -sh {region_id}.npz        # non-trivial size
python -c "import numpy as np; z=np.load('{region_id}.npz', allow_pickle=True); \
  ld=z['ld']; n=ld.shape[0]; \
  assert ld.dtype==np.float32 and ld.shape==(n,n), 'shape/dtype'; \
  assert abs(float(ld[0,0])-1.0)<1e-3, 'diag!=1'; \
  assert np.allclose(ld, ld.T, atol=1e-4), 'not symmetric'; \
  print('OK', n)"
```

(For banded mode, verify the one triangle + `lower_triangular==True` instead of full
symmetry.) [[feedback_aou_success_marker_not_evidence_of_data]]

---

## STEP 6 — EGRESS (only aggregate LD + AF crosses)

Bundle per-chromosome and split any chrom bundle over the 50 GB working ceiling:

```python
from ld_egress_bundle import plan_egress_bundles
bundles = plan_egress_bundles(cell_sizes)   # reuse m3-02d; splits >50 GB -> chrN_a/chrN_b
```

Egress **ONLY** the aggregate LD `.npz` + AF (**never** the `.bed`). Append each
per-chromosome egress entry to `aou-egress-audit-log.md`. The AFR LD `.npz` is
egress-clean per the prior G0 ruling.

---

## STEP 7 — SHUTDOWN + TOKEN-FREE HANDBACK

1. **STOP** the Spot VM (and the HAIL cluster 20260604 if used for the export) —
   verify the Stopped badge in the Apps panel. `wb cluster stop` is the
   from-NCSU billing-safety lever.
2. Write **`m3-02e-cluster-shutdown.md`** with the verified Stopped badge + $-spent.
3. **Token-free handback** (no Workbench push token): `cat` the panel TSV
   (`m3-W2-native-plink-panel.tsv`) + the shutdown record to the chat; ping NCSU
   **`native-panel-recorded`**. NCSU reconstructs both artifacts verbatim + pushes,
   then verifies `origin tip == local HEAD`.

---

## DO-NOT (hard rules)

- Do **NOT** egress the `.bed/.bim/.fam` (individual-level; in-perimeter only).
- Do **NOT** skip the production-VM re-measure gate (Step 3) before the loop.
- Do **NOT** trust `_SUCCESS` / file existence — contents-validate every `.npz`
  (Step 5, D-M3-10).
- Do **NOT** drop `--keep-allele-order` (it is hardcoded in `build_plink_ld_command`;
  do not bypass the helper).
- Do **NOT** route the AFR panel through the retired Hail A.3 BlockMatrix write
  (`_write_a3_banded_correlation_bm` stays in the tree but is NOT the AFR route).
- Do **NOT** `git add -A` on the GPFS tree — explicit paths only.

---

## GATE VERIFICATION (what NCSU checks at the resume signal)

1. AFR cohort exported ONCE to plink `.bed/.bim/.fam` in-perimeter
   (count_cols == 73,122 logged once; `.bed` never left the perimeter).
2. Production-VM re-measure ran on one region and the ×276 projection is within
   budget BEFORE the full loop (the pilot-caveat gate).
3. 276-region plink loop completed with `--keep-allele-order` on every call; each
   region landed a square float32 `.npz` (diag 1.0, symmetric), data-layer-verified
   (gsutil du + numpy read-back, NOT a marker) per D-M3-10.
4. `m3-W2-native-plink-panel.tsv` carries the REAL per-region walls/RAM/output/n_var.
5. Per-chromosome egress bundles filed under the 50 GB ceiling; ONLY aggregate
   LD + AF egressed; `aou-egress-audit-log.md` updated.
6. VM/cluster verified STOPPED ($0 idle) with `m3-02e-cluster-shutdown.md`.
7. Token-free handback completed; NCSU reconstructed + pushed; origin tip == local HEAD.
