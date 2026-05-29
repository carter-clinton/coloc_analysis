# Migration playbook — AoU Legacy Workbench → Researcher Workbench 2.0

> Contextualized to the `coloc_analysis` workspace. Pre-migration gates protect Track 1 credit-recovery evidence and Abby Doyle's ability to assess the claim. Post-migration validation confirms our infrastructure (workspace bucket + notebooks + clone + env config + billing) survived intact.
>
> **Hard deadline:** 2026-06-30. **Recommended window:** 2026-06-02 through 2026-06-15 (leaves 2-4 weeks of buffer for any platform-side surprises and for AoU engineering to reply before migration is irreversible).

## Pre-migration gates (must complete in order BEFORE Step 1)

### Gate G0 — Wait for Abby's directional reply

Before initiating any migration step, confirm Abby Doyle's response on Zendesk #57144 to the migration-clarification email (paste-ready draft at [`ABBY-MIGRATION-CLARIFICATION-DRAFT.md`](./ABBY-MIGRATION-CLARIFICATION-DRAFT.md)).

| Abby's reply | Action |
|---|---|
| "Migrate at your discretion; forensics preserved" | Proceed to G1 |
| "Engineering team wants to reproduce against Legacy first" | Hold migration until they're done; track via Zendesk; mirror forensics anyway (G1) as insurance |
| "Engineering has finished; here's the diagnosis" | Apply their finding; mirror forensics (G1); migrate (Step 1+) |
| No reply by 2026-06-08 (10 business days from Carter's 2026-05-28 follow-up) | Proceed to G1 + G2 anyway; document silence in OSF audit trail; presume credit recovery unlikely; plan 1000G AFR pivot for Wave 2 |

### Gate G1 — Mirror catastrophe forensics to NCSU

Run [`run_forensic_mirror.sh`](./run_forensic_mirror.sh) inside the AoU env (paused-cluster compatible; ~5 min runtime; ~$1 cost) and commit the resulting bundle to [`.planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/`](../260521-w1-catastrophe-handoff/forensic-mirror/) per its [README.md](../260521-w1-catastrophe-handoff/forensic-mirror/README.md).

This produces:
- Per-MT du + ls + _SUCCESS mtime (resolves Carter's kill-as-culprit hypothesis vs debug doc Hail-finalize hypothesis per `[[feedback_w1_catastrophe_hypothesis_distinguisher]]`)
- Bucket-wide inventory + `metadata.json.gz` parse
- 27 MiB hail.log preserve copy

**Why critical:** Workspace buckets almost certainly persist across migration, but the NCSU-side mirror is insurance + the mtime data is needed regardless.

### Gate G2 — Confirm Track 4 patches in upstream + AoU clone

```bash
# From NCSU side (anywhere):
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
git fetch origin
git log --oneline origin/m3-W2-aou-deltas..HEAD  # should be empty (NCSU side caught up)
grep -c "_validate_checkpoint_populated" src/python/aou_ld_panel.py  # should print 6+
grep -c "_assert_checkpoint_nonempty" src/python/aou_ld_panel.py  # should print 4

# From AoU env (during G1 fire):
cd /home/jupyter/coloc_analysis
git pull origin m3-W2-aou-deltas  # idempotent; brings AoU clone to upstream HEAD
git log --oneline -10  # confirm Track 4 commits 59e914b..bfe5f0e are present
```

If grep counts don't match, halt and investigate before migrating.

### Gate G3 — Inventory workspace assets pre-migration

While the AoU env is up for G1, also record:

```bash
# Inside AoU env terminal
echo "=== Workspace bucket top-level layout ==="
gsutil ls "gs://${WORKSPACE_BUCKET}/"

echo "=== Total bucket size ==="
gsutil du -sh "gs://${WORKSPACE_BUCKET}/"

echo "=== Notebooks in workspace ==="
gsutil ls "gs://${WORKSPACE_BUCKET}/notebooks/"

echo "=== Active env cluster preset (from Workbench UI) ==="
# Manual: screenshot the env panel showing master+worker type, count,
# PD config (Reattachable per [[feedback_aou_use_persistent_disk]] —
# NOTE: not available on Dataproc compute type per the amended memory)
```

Save the output to NCSU at `.planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/pre-migration-inventory.txt`. This is your reference point for the post-migration validation (Step 4).

---

## Step 1 — Confirm Eligibility and Access Requirements

Per AoU support article §1, all four must be true:
- Annual data-access requirements current (eRA Commons linkage + DUA/RPS; already in place per [[user_profile]] + `.planning/amendments/AOU-WORKBENCH-REGISTRATION.md`)
- Controlled-tier access (already approved; required for v8 WGS access)
- **RW 2.0 logged-in + Verily ToS accepted** — one-time (Carter done 2026-05-29 ✅)
- Legacy workspace linked to a valid billing account **AND** an active **billing pod** available in RW 2.0 with a billing account attached (Carter attached a billing account to the pod 2026-05-29 ✅)

**Action:** This is just a one-time RW 2.0 login + Verily ToS accept (done). Do NOT look for a "Migrate" CTA on the RW 2.0 side — it doesn't exist; the trigger is on the legacy side (corrected Step 3). RW 2.0 is only where the migrated `rw-migration-aou-rw-XXXXXXXX` workspace appears afterward.

---

## Step 2 — Prepare and Clean Up Your Workspaces

Specific to `coloc_analysis` workspace:

- [ ] G0 / G1 / G2 / G3 complete (gates above)
- [ ] Confirm no environment is currently running (cost meter shows $0/hr) — Carter end-of-Session-2 already deleted the env, so this should be clean
- [ ] Delete any orphan persistent disks via Workbench UI (cost: PDs are ~$4.80/mo per [[feedback_aou_use_persistent_disk]]; not free)
- [ ] Delete any deleted-but-not-purged notebooks from `gs://${WORKSPACE_BUCKET}/notebooks/`. Specifically check for:
  - `AOU-1.ipynb` (the live notebook used during the catastrophe firings 2026-05-12 / 2026-05-14 / 2026-05-17 / 2026-05-18→20). **DO NOT DELETE** — this IS the catastrophe execution context and may be part of Abby's forensic review.
  - Any test/sandbox notebooks ending in `-Copy.ipynb` or `-test.ipynb` (delete OK)
- [ ] Confirm `gs://${WORKSPACE_BUCKET}/forensics/hail.log.pre_pd_migration.20260521T201919Z.log` is still present
- [ ] Confirm `gs://${WORKSPACE_BUCKET}/ld/mt_*_qc.mt/` directories are still present (catastrophe evidence)
- [ ] If AoU support article requests any specific "stop running jobs" / "downloaded large datasets" action, follow as written

---

## Step 3 — Migrate Your Workspace

> **CORRECTED PROCEDURE (verified live 2026-05-29).** Migration is initiated from the **legacy** Workbench (`workbench.researchallofus.org`), NOT from RW 2.0/Verily. There is no card-level "Migrate" CTA and no "Import legacy workspace" action on the RW 2.0 side — that side is only the destination. The workspace's ⋮ card menu only shows Duplicate/Edit/Share/Delete (that's why the original playbook's assumption was wrong).

**Documented path** (AoU support article §3 "How to Migrate a Workspace"):

1. On the **legacy** landing page → **"Go to workspaces."**
2. **Open `coloc_analysis` itself** (click into the workspace — NOT the ⋮ card menu).
3. Go to the workspace's **"Data" tab** → review the eligibility checks + guidance.
4. On the next page, **select the billing pod** for RW 2.0 to use (Carter attached a billing account to the pod 2026-05-29 ✅ — this is a billing action, Carter's to confirm).
5. Click **"Start migration."**

**The "data on your persistent disk" dialog** ("Persistent disk data will not be migrated…"): for `coloc_analysis`, **click CONTINUE WITH MIGRATION** — nothing of value is on the PD. Everything we created is already in the workspace bucket (forensic mirror + inventory in `forensics/`; MTs in `ld/`) AND on NCSU git; the PD only held the re-clonable git checkout. Continuing does not delete the PD anyway (it stays in legacy until separately deleted). Do NOT spend time copying re-clonable files to the bucket.

**What migration does** (non-destructive): copies the workspace **bucket** into a NEW RW 2.0 workspace folder named `rw-migration-aou-rw-XXXXXXXX`, preserves metadata + access policies. The **legacy workspace is NOT locked or deleted.** NOT migrated: persistent-disk files (unsupported in RW 2.0) + any cohorts/concept-sets/datasets built with the point-and-click Cohort/Dataset Builder. **Ours ride along in the bucket** — all our cohort logic is in notebooks/scripts, not the point-and-click builder — so nothing is lost.

**Carter user-action only** for Steps 1–5 above; no automation.

While migration is in flight:
- [ ] Take screenshot of "before" state (Legacy Workbench → coloc_analysis workspace card with workspace ID + DUA + cost-to-date)
- [ ] Watch for any errors during the migration job (some platform migrations queue server-side and email when complete)
- [ ] Note any URL/workspace-ID changes (the workspace might get a new URL under RW 2.0 but the underlying `${WORKSPACE_BUCKET}` should be unchanged)
- [ ] **DO NOT close the browser tab until the migration reports complete** (some platform migrations require persistent UI session)

Expected duration: per AoU support article. If multi-hour, defer Step 4 to next session.

---

## Step 4 — Validate and Continue Work in Researcher Workbench 2.0

Compare RW 2.0 state against the pre-migration inventory captured in G3.

```bash
# Recreate env in RW 2.0 (paused — $0.14/hr)
# Open terminal in env

# 1. Workspace bucket: same?
echo "=== Workspace bucket layout ==="
gsutil ls "gs://${WORKSPACE_BUCKET}/"
# Expected: same layout as pre-migration inventory. If WORKSPACE_BUCKET changed,
# that means we have a new bucket on RW 2.0 — investigate where Legacy bucket
# data went.

echo "=== Bucket size ==="
gsutil du -sh "gs://${WORKSPACE_BUCKET}/"
# Expected: same as pre-migration (~71 MiB)

# 2. Catastrophe forensics: still there?
gsutil ls "gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt/_SUCCESS"
gsutil ls "gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt/_SUCCESS"
gsutil ls "gs://${WORKSPACE_BUCKET}/forensics/hail.log.pre_pd_migration.20260521T201919Z.log"
# Expected: all 3 present.

# 3. Notebooks: preserved?
gsutil ls "gs://${WORKSPACE_BUCKET}/notebooks/"
# Expected: same notebooks as pre-migration. Check AOU-1.ipynb still present.

# 4. Git clone: clean?
cd /home/jupyter/coloc_analysis
git status
git log --oneline -10
# Expected: clean tree, same HEAD as pre-migration.
# If clone was wiped, git clone fresh:
#   cd /home/jupyter
#   git clone https://github.com/carter-clinton/coloc_analysis.git
#   cd coloc_analysis
#   git checkout m3-W2-aou-deltas

# 5. Env vars: AoU still sets WORKSPACE_BUCKET / GOOGLE_PROJECT /
#    WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH?
env | grep -E "WORKSPACE_BUCKET|GOOGLE_PROJECT|WGS_ACAF"
# Expected: all 3 set. If WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH still points
# at v8 path, we stay on v8; if it points at v9, we need to update
# CDR_VERSION = "v8" in src/python/aou_ld_panel.py (separate quick task).

# 6. Hail / Dataproc image version: same as Legacy?
python3 -c "import hail as hl; print('Hail version:', hl.__version__)"
# Compare against pre-migration. If different, the catastrophe mechanism
# might also be different — note for chr22 smoke planning.
```

Once Step 4 validation passes, **delete the env again** (cost meter back to $0/hr) and write a brief status note to `.planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/post-migration-validation.txt` capturing:
- Migration completion timestamp
- Any deltas from pre-migration inventory (workspace bucket changed? Hail version changed? env vars changed?)
- Hail version on RW 2.0 vs Legacy (this is important for chr22 smoke planning)
- Carter's go/no-go signal for chr22 smoke

Commit + push.

---

## After migration (NOT in this playbook — pointers only)

Once Step 4 validation passes:

1. **chr22 smoke fire** per [`.planning/notebooks/AOU-1-chr22-smoke_template.ipynb`](../../notebooks/AOU-1-chr22-smoke_template.ipynb) (this task) — paste into AoU env's Jupyter, fire, validate Track 4 assertions under live Hail.
2. **AOU-0 pre-check** per [`.planning/notebooks/AOU-0-precheck_template.ipynb`](../../notebooks/AOU-0-precheck_template.ipynb) — always-run-before-any-fire.
3. **Wave 1 cohort rebuild** if Abby's diagnostic + chr22 smoke both clear. Apply Track 4 patches inherit to AOU-2 / AOU-4 per [`.planning/notebooks/AOU-2-AOU-4-TRACK-4-PATTERN.md`](../../notebooks/AOU-2-AOU-4-TRACK-4-PATTERN.md).
4. **OR Wave 2 pivot to 1000G AFR** if Abby's silence persists past 2026-06-08 internal deadline — substrate already on disk at `data/processed/ld_reference/AFR/*.rds` (11 candidate-locus regions); no AoU compute needed.

---

## What to do if migration fails

| Failure mode | Action |
|---|---|
| Migration job errors out mid-flight | Re-try once; if second attempt fails, open NEW Zendesk ticket (NOT #57144) for migration support. Do NOT proceed past 6/30 deadline in error state. |
| Workspace bucket changed URI on RW 2.0 | Update `WORKSPACE_BUCKET` references in code/notebooks. Mirror old bucket → new bucket via gsutil cp -r (or AoU support engagement). |
| Notebooks lost in migration | Restore from `.planning/notebooks/AOU-1_template.ipynb` + `AOU-2_per_region_ld.ipynb` + `AOU-4_validation.ipynb` (all preserved on NCSU). gsutil cp them up to `gs://${WORKSPACE_BUCKET}/notebooks/`. |
| Hail version on RW 2.0 differs from Legacy in a breaking way | Update `envs/m3-aou-dev.yml` Hail pin if necessary; re-fire local pytest sweep on smoke_dev; bake a new memory if the version change is structurally important. |
| Catastrophe forensics lost on workspace bucket | Recover from NCSU mirror (G1) at `.planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/`. Notify Abby. |
| Billing setup broken on RW 2.0 | Re-link billing per AoU support; this WILL block any env recreation. |
| Anything else | Halt; log to STATE.md `stopped_at`; open Zendesk ticket; do NOT attempt re-fire under uncertain platform state. |

---

## Cross-references

- [`ABBY-MIGRATION-CLARIFICATION-DRAFT.md`](./ABBY-MIGRATION-CLARIFICATION-DRAFT.md) — Zendesk reply draft (G0)
- [`run_forensic_mirror.sh`](./run_forensic_mirror.sh) — forensic mirror script (G1)
- [`../260521-w1-catastrophe-handoff/forensic-mirror/README.md`](../260521-w1-catastrophe-handoff/forensic-mirror/README.md) — NCSU receiver (G1)
- AoU RW 2.0 migration support article: https://support.researchallofus.org/hc/en-us/articles/48266066855188
- Zendesk ticket #57144
