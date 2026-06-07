---
id: SEED-001
status: dormant
planted: 2026-06-07
planted_during: v3.1.2 / m3-W2 genome-wide AoU AFR LD cohort build
trigger_when: After the genome-wide AFR+EUR cohort build fully validates AND m3-W2-aou-deltas is merged to main
scope: Small
---

# SEED-001: Link the coloc_analysis GitHub repo to the AoU RW 2.0 "Git repositories" auto-clone feature

## Why This Matters

RW 2.0 environments are **ephemeral — no persistent disk** (per `[[feedback_aou_use_persistent_disk]]`: PD rule retired on Dataproc). So every new cluster/app currently requires a manual `git clone` + `git checkout m3-W2-aou-deltas` + `git pull` + re-applying env guards. The AoU workspace exposes a built-in **"Git repositories"** feature ("Automatically cloned to your apps to help you manage source code") that auto-clones a linked repo into each new app. Linking it removes the manual `git clone` step on every fresh environment and shrinks the fresh-clone error surface (the exact friction that has bitten us across re-fires).

## When to Surface

**Trigger:** After the genome-wide AFR+EUR cohort build fully validates AND `m3-W2-aou-deltas` is merged to `main`.

Surface during the post-AFR / post-genome-wide-build wrap-up, or at `/gsd-new-milestone` when the scope touches AoU environment setup / reproducibility / onboarding. Do NOT act before BOTH conditions hold:

1. **Genome-wide build validated** — Cell 3/4/5 + validation cells 3.5/4.5/5.5 all PASS. Don't poke workspace config mid-production-run.
2. **`m3-W2-aou-deltas` merged to `main`** — the auto-clone pulls the **default branch (`main`)**, which currently lacks the fan-out fix (`ab0853a`) and the baked-in env guards (`fdf257c`, only on `m3-W2-aou-deltas`). Until merged, auto-clone lands `main` and STILL requires a manual checkout+pull — defeating the purpose.

**Real payoff sequence:** validate build → clean PR `m3-W2-aou-deltas` → `main` (via `/gsd-pr-branch`, filtering `.planning/` commits) → THEN link the repo so a fresh app auto-clones working code at `main` directly.

## Scope Estimate

**Small** — the link action itself is ~2 minutes in the AoU UI. The gating **merge-to-main** is the larger (but separate, already-planned) step.

## How to do it (when triggered)

In the AoU workspace **Git repositories** card → **Add repository**:
- **Name:** `coloc_analysis` (EXACT — Cell 1b does `sys.path.insert(0, os.path.expanduser("~/coloc_analysis/src/python"))`, so the clone must land at `~/coloc_analysis`)
- **Repository URL:** `https://github.com/carter-clinton/coloc_analysis.git`
- Public repo → **HTTPS, no SSH key needed** (the dialog's SSH requirement is only for private repos)

## Breadcrumbs

- `[[project_repo_url]]` — origin = https://github.com/carter-clinton/coloc_analysis
- `[[feedback_aou_use_persistent_disk]]` — RW 2.0 has no PD → ephemeral envs → clone needed each time
- `[[feedback_aou_cluster_template_bucket_pollution]]` — the manual fresh-clone guard friction this reduces
- `.planning/notebooks/AOU-1_template.ipynb` Cell 1b — the `~/coloc_analysis/src/python` sys.path dependency that pins the Name field
- Commits `ab0853a` (fan-out fix) + `fdf257c` (baked env guards) — on `m3-W2-aou-deltas`, NOT on `main` (verified 2026-06-07)

## Notes

Planted 2026-06-07 while the genome-wide AFR fan-out was live (mid-run, ~chr10/22). Carter explicitly chose NOT to add it mid-run and asked to remember it for later. Pairs naturally with the eventual `m3-W2-aou-deltas` → `main` merge.
