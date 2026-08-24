# Stage A env STOP — `plink1.9` absent + stale LOCAL scratch panel TSV (2026-08-24 15:40 EDT)

> Provenance: AoU browser agent's verbatim STOP report, pasted by Carter 15:40 EDT, after Carter's
> "go" for STEP 8 (Stage A) at ~15:30 EDT. Resume pass earlier the same afternoon: repo pin `7c310e5`
> satisfied on the VM; STEP 2 (0 .npz), STEP 4 (no bucket TSV), STEP 5 substitute (20,767,864 /
> 73,122) re-checked; STEP 7 PASSED 20/20 in-perimeter (both gated tests ran). Nothing reached the
> bucket; nothing was banked; $0 wasted beyond idle VM time. Disposition: ENVIRONMENT, not code.

## What the producer printed (verbatim, as received)

```
region m2_region_00001: EXCLUDING 231 reference-occluded variant(s) before --r (102421 in-window; overlapping-deletion REF span -> structurally undefined LD; excluded in lockstep with provenance, never zeroed — osf.io/az52u)
ERROR m2_region_00001: [Errno 2] No such file or directory: 'plink1.9'
Traceback (most recent call last):
  File ".../src/python/run_native_ld_panel.py", line 1344, in <module>
    raise SystemExit(main())
  ...
  File ".../src/python/run_native_ld_panel.py", line 641, in _append_panel_row_local
    raise ValueError(
ValueError: panel TSV /home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv has a STALE header and cannot be appended to.
  found:    ['region_id', 'chr', 'n_var', 'wall_min', 'peak_ram_gib', 'output_gib', 'status']
  expected: ['region_id', 'chr', 'n_var', 'wall_min', 'peak_ram_gib', 'output_gib', 'status', 'n_dropped_occluded', 'n_dropped_monomorphic']
```

Two independent failures, both BEFORE any banking; the second is the fail-closed guard doing its job.

## Failure 1 — `plink1.9` not on PATH

- The producer's argv executable is the hardcoded literal `"plink1.9"` (`src/python/aou_ld_panel.py::build_plink_ld_command`, ~:2903; no flag; `run_native_ld_panel._run_plink` is the sole subprocess seam).
- The Cloud Analysis VM image ships only `plink` (`/opt/workbench-tools/binaries/bin/plink`). STEP 3's check was `which plink || which plink1.9`, which passes on either — it passed on the WRONG binary on 2026-08-19 and again on the 2026-08-24 resume.
- The 2026-06-24 pilot and the m3-02e fire brief pin **PLINK v1.90b7.2 64-bit (11 Dec 2023)** (`plink_linux_x86_64_20231211.zip`); the June/July fires ran on the Dataproc master where that build resolved as `plink1.9`. That provisioning never reached the Cloud Analysis VM recipe — a prep landmine.
- **Ruling (Carter, via this session, 15:43 EDT):** install the PINNED build into `~/bin/plink1.9`, `export PATH="$HOME/bin:$PATH"` in the fire shell, verify `plink1.9 --version`; a shim of the workbench `plink` only if it is a PLINK v1.90 build (PLINK 2.x `--r` semantics differ — never shim it). No code change on the fire path.

## Failure 2 — stale LOCAL scratch panel TSV (7 columns, June era)

- `/home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv` was a June-era leftover with the pre-m3-07b 7-column header. The producer seeds its gs:// mirror from this local path when the bucket copy is absent (`append_panel_row`, ~:659-700) and `_append_panel_row_local` fail-closes on a stale header — correct behaviour; it prevented a ragged TSV.
- STEP 4 checked only the BUCKET copy (absent) and so could not see it.
- **Ruling:** ROTATE, never delete — `mv … m3-W2-native-plink-panel.tsv.STALE.<UTC>`; nothing else in scratch touched; the bucket stays TSV-free and at 0 .npz.

## Runbook remediation (this record's commit)

- STEP 3 (all three `260812-ox1` runbooks): `which plink1.9 && plink1.9 --version` with the pinned-version EXPECT and the install recipe.
- STEP 4b / §4: the local scratch mirror header check + ROTATE rule.
- `260817-vbu-verify.sh all` byte-identical before/after (the 6b card is untouched).
- HANDOFF.json `prep_landmines` gains the entry; the fresh-VM recipe in the `aou-ld-pipeline` skill should carry the plink1.9 install line (follow-up).

## Status at the time of this record

Stage A RE-RUNNING on the VM (Carter's go ~15:45 EDT) after both remedies; nothing banked yet; the mechanical gate follows. An agent never fires.
