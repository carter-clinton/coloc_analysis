# STAGE A PASSED — region 1 banked, six-check mechanical gate exit 0 (as received, 2026-08-24)

> Provenance: AoU browser agent's verbatim report, pasted by Carter 2026-08-24 ~21:10 EDT, after
> Carter's go for STEP 8 at ~15:45 EDT and the two env remedies (pinned `plink1.9` installed by
> Carter's own hand at ~16:05 EDT; stale local scratch panel TSV rotated `…STALE-7col-june.20260824T1947Z`).
> AS-RECEIVED transcription. This is the FIRST banked artifact of the m3-W2 AFR native-plink LD
> panel and the first execution under the RECALIBRATED, POSTED two-condition clause (d)
> (OSF file mk7ze, 2026-08-22T02:58:55Z).

---

## Environment at fire time

```
/home/jupyter/bin/plink1.9
PLINK v1.90b7.2 64-bit (11 Dec 2023)
```

The PINNED build, re-verified in the SAME shell that ran the producer. (The VM image's own
binary is `PLINK v1.9.0-b.8 64-bit (22 Oct 2024)` — 1.9-family but NOT the pin; not used.)

## The banked region (producer stdout, verbatim)

```
WROTE /home/jupyter/native_ld_scratch/m2_region_00001.npz (mode=square, 102190 x 102190, lower_triangular=False)
{"region_id": "m2_region_00001", "chr": 1, "n_var": 102190, "wall_min": 92.0508, "peak_ram_gib": 30.6591, "output_gib": 35.94476, "status": "ok", "out": "gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m2_region_00001.npz", "n_dropped_occluded": 231, "n_dropped_monomorphic": 0}
```

Bucket `.npz` count: **1**. Manifest: **232 lines** (header + 231 records). Excludelist: **231 lines**.

## The gate sidecar (verbatim) — the shipped two-condition gate's own measurement

```json
{
  "region_id": "m2_region_00001",
  "n_rows": 102421,
  "n_sites": 96708,
  "occ_rows": 231,
  "occ_sites": 196,
  "site_fraction": 0.002026719609546263,
  "inflation": 1.1785714285714286,
  "site_fraction_ceiling": 0.005056,
  "inflation_ceiling": 3.42,
  "fired": [],
  "verdict": "ok"
}
```

## Arithmetic reconciliation (NCSU-side, independent of the agent's report)

| Identity | Computed | Reported | Verdict |
|---|---|---|---|
| `n_var` = in-window rows − occluded | 102421 − 231 = **102190** | 102190 | ✓ |
| inflation = occ_rows / occ_sites | 231 / 196 = **1.1785714** | 1.1785714285714286 | ✓ |
| site_fraction = occ_sites / n_sites | 196 / 96708 = **0.00202671961** | 0.002026719609546263 | ✓ |
| site_fraction vs posted ceiling | **0.2027% < 0.5056%** | `fired: []` | ✓ under |
| inflation vs posted ceiling | **1.18× < 3.42×** | `fired: []` | ✓ under |
| `output_gib` = npz bytes / 1024³ | 38595391746 / 1024³ = **35.94476** | 35.94476 | ✓ |

The three independent records of ONE drop set agree exactly: panel `n_dropped_occluded` = 231,
manifest records = 231, sidecar `occ_rows` = 231, excludelist lines = 231. And all four reproduce
the pre-registered measurement sweep (231 rows / 196 sites / 1.1786× — PENDING PASTE #3,
2026-08-20), which is the number the re-derived test oracle pins as MEASURED-NOT-DERIVED.

## STEP 8-GATE — `fire_verifier stage-a`, verbatim

```
=== fire_verifier stage-a ===
PASS  HARD_STOP  stage_a_nan_falsification: the SHIPPED content verification re-read the banked .npz (38595391746 B) and returned ok -> the region carries no NaN; occlusion accounted for 100% of the region-1 NaN (shipped reason: ok (n=102190))
PASS  HARD_STOP  expected_records_derivation: expected_records=231 DERIVED from m2_region_00001.occluded.excludelist (231 non-empty line(s)) and cross-checked against the gate sidecar's occ_rows=231
PASS  HARD_STOP  stage_a_manifest_rows: manifest carries 231 real record(s) + header, fields parseable, every record row region_id='m2_region_00001'
PASS  HARD_STOP  occlusion_gate: 231 occluded row(s) at 196 of 96708 site(s) -> site_fraction 0.2027% vs ceiling 0.5056%; inflation 1.18x vs ceiling 3.42x -> under BOTH posted ceilings
PASS  FINDING    region1_status: region 1 status='ok'
PASS  HARD_STOP  status_classification: 1 ok-class + 0 deferred row(s) of 1, ALL recognized (the gates working; do NOT 'fix' a deferral mid-fire — a region above the n_var ceiling of 120000 defers by design)

hard_stops: []
findings:   []
exit_code:  0
report written: /home/jupyter/fire_gate_stageA.json
gate exit: 0
```

Every mechanism landed in this run for the first time on real data: the derived
`expected_records` (231, from the excludelist, cross-checked against the sidecar — the check that
replaced the false `expected_records=5` default), and `occlusion_gate` evaluating BOTH posted
conditions.

## What the NaN falsification actually established

`stage_a_nan_falsification` is **positive evidence, not an absence**: the shipped content
verification re-read all **38,595,391,746 bytes** of the banked dense matrix and found no NaN.
Since the converter raises on ANY NaN before upload, a banked region 1 proves the occlusion
exclusion accounted for **100%** of region 1's NaN. That is the scientific question the whole
occlusion amendment chain turned on, and it is now answered affirmatively on real AFR WGS data.

## Cleanup (the only deletion R6 authorises)

Scratch `.npz` copy removed after the gate. `df -h /home/jupyter`: 984G total / 417G used /
**527G avail** / 45%. The banked object in the bucket is untouched.

## Open item recorded, not acted on

Producer warning, verbatim:

```
WARNING: no --allele-freq sidecar for region 'm2_region_00001'; writing all-NaN AF. Supply the per-region .afreq sidecar to carry allele frequencies into obj$variants$AF.
```

NOT a region-1 quirk and NOT a gate failure — see `AF-1` in
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`. It is a DECISION FOR BEFORE
STAGE C.

## Status

Stage A PASSED and banked; the agent is HOLDING at STEP 9 (Stage B, 4 regions) for Carter's
fresh go. Nothing is computing. An agent never fires.
