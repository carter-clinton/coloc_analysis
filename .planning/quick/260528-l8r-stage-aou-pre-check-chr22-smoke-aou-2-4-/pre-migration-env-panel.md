# Pre-migration env-panel snapshot (gate G3, manual half)

Captured 2026-05-28/29 from the AoU Legacy Workbench Cloud-analysis-environment
panel for the `coloc_analysis` workspace, while the env was up to run the
forensic mirror + G3 CLI inventory. This is the CLI-uncapturable half of gate
G3 (the `gsutil` inventory is in `pre-migration-inventory.txt`).

## Environment configuration (Legacy platform, pre-RW-2.0-migration)

| Field | Value |
|---|---|
| Compute | 4 CPUs / 15 GB RAM; GPUs off |
| Compute type | **Standard VM** — no Dataproc cluster (featherweight gsutil-only config, as intended for the mirror + inventory) |
| Zone | us-central1-a |
| Auto-pause | 30 min |
| Storage | **Reattachable persistent disk**, type **Standard (HDD)**, 120 GB |
| Cost | $0.20/hr running; <$0.01/hr paused; $4.80/mo disk |

**Note on "cluster preset":** the playbook G3 step asks to record master/worker
type + count, but those fields only exist for the **Dataproc** compute type.
This env is a Standard VM with no cluster, so there are no master/worker counts
to record — "Standard VM, no cluster" is the accurate state. The 256-vCPU /
≥16× n1-highmem-16 Dataproc sizing applies only to the future chr22-smoke /
Wave-2 jobs, NOT to this env.

**Disk rule compliance:** Reattachable PD (not the delete-with-env disk),
Standard/HDD media, default 120 GB — consistent with
[[feedback_aou_use_persistent_disk]] and the HDD-is-fine-for-gsutil reasoning.

**Guardrail confirmation:** the env panel was closed via the X without touching
NEXT or DELETE ENVIRONMENT; nothing was modified; env remained running (green
dot). No cleanup/deletion pass was run at any point — `AOU-1.ipynb` and the
`ld/mt_*_qc.mt/` dirs are untouched; catastrophe evidence in `forensics/` is all
present (both `_SUCCESS` markers + jstack/pyspy/yarn captures + `hail.log.*` +
the `forensic_mirror_20260528T231308Z.tar.gz` bundle).
