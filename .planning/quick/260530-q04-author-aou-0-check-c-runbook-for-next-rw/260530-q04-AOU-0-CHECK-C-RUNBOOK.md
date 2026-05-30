# AOU-0 + CHECK-C Runbook — close the CDR/AUX question on the next CDR-wired env

**For:** Carter (you hold every launch/compute trigger on the AoU Researcher Workbench).
**Platform:** RW 2.0 · workspace `aou-rw-476cdac2` · project `wb-perky-corn-6639` · CDR `C2024Q3R9`.
**Type:** Operational instructions. Nothing here runs on NCSU — this is what *you* execute in the Workbench. **DOCS ONLY — apply no source patch from this runbook.**

---

## 0. Why this runbook exists

This session resolved **CHECK D** (Hail version captured) and **reframed CHECK C** from a presumed FAIL into INCONCLUSIVE / env-not-wired. The two prior probes failed to bind the CDR because they were **featherweight / terminal-only Compute-Engine envs** that never ran the CDR-binding startup. A `403` from a non-bound env tells us **nothing** about whether the legacy AUX path is correct for R9 — it only tells us the env's pet service account lacks the dataset authorization scope a real CDR-wired env would have. So CHECK C is **deferred to a real CDR-wired Standard Analysis env**, where one capture block settles it decisively.

---

## 1. Session outcomes baked in

| Check | Outcome | Detail |
|---|---|---|
| **CHECK D** | **PASS** | Hail **0.2.135** (full `0.2.135-034ef3e08116`) captured from RW 2.0 terminal Python. This is the **SAME 0.2.x family as Legacy** → the checkpoint-contract-violation mechanism behind the m3-W1 empty-MT catastrophe is **STILL LIVE** on RW 2.0. **Consequence:** Track 4 defensive patches (`count_rows`/`count_cols` asserts + entries-dir `gsutil` size checks) **remain load-bearing**; chr22 smoke stays gated on them. |
| **CHECK C** | **INCONCLUSIVE (not FAIL)** | Both `gsutil ls` on the legacy v8 AUX paths returned `AccessDeniedException: 403` (storage.objects.list denied for pet SA `pet-...@wb-perky-corn-6639.iam.gserviceaccount.com`). Listing the bucket **ROOT** `gs://fc-aou-datasets-controlled/` gave the **SAME 403** (NOT 404 → not a wrong path; an **authorization-scope** failure). `env \| grep` for CDR/AUX/dataset vars returned **NOTHING**. Terminal startup printed `Failed to get CDR configuration: CDR version not found: cdrv8 - R9 (env: prod, access tier: controlled)`. **DIAGNOSIS: env-not-wired, not workspace-misbound.** |
| **Resources-tab read** (FREE, $0, read-only) | workspace correctly version-bound | Workspace is bound to `C2024Q3R9` = "cdrv8 - R9 (version-bound)", a **Referenced BigQuery dataset**, Source "All of Us Controlled Tier", Project ID `wb-silky-artichoke-2408`, Dataset ID `C2024Q3R9`. That CDR BigQuery project is **SEPARATE** from the compute project `wb-perky-corn-6639` (normal AoU split — irrelevant here; our cohort is pure-Hail, zero BigQuery). **R8-pin hypothesis RULED OUT.** The soft "a different version is available" banner's only actions are **View Release Notes** + **Close**; adopting a different version requires a deliberate Data-collections-catalog action (nothing one-click / accidentally trippable). The Resources tab exposes the **BigQuery side ONLY** — it does **NOT** surface the `fc-aou-datasets-controlled` WGS/AUX Cloud Storage path where `ancestry_preds.tsv` + `relatedness_flagged_samples.tsv` live, so it does **NOT** hand us `AUX_BASE` directly. |

---

## 2. Decision (locked): KEEP the version-bound R9 pin

**Keep the version-bound `C2024Q3R9` (cdrv8–R9) pin.** A pinned CDR is the reproducibility-correct posture — the data-layer equivalent of the Snakemake pin (R9 won't shift mid-analysis). **Do NOT adopt the catalog default.** Reopen this decision ONLY if the pinned R9 snapshot fails to expose WGS/AUX paths at AOU-0 (no evidence of that today). Aligns with `feedback_rigor_over_speed`.

---

## 3. Env launch preconditions (MUST read before spending)

- **Use a Standard Analysis (Jupyter) env**, **NOT** a featherweight / terminal-only Compute-Engine env. The **Standard Analysis** env runs the CDR-binding startup; the featherweight one does **not** — that is the whole reason the prior two probes 403'd.
- **FIRST check on startup:** confirm NO `Failed to get CDR configuration` / `cdrv8 - R9 not found` error appears in the startup log. **If it DOES → STOP**, do not spend further compute, report back before proceeding (relaunch a Standard Analysis env or escalate).
- **RW 2.0 has NO persistent disks** → the repo clone is **ephemeral**. Each fresh env:
  ```bash
  git clone https://github.com/carter-clinton/coloc_analysis.git
  cd coloc_analysis
  git checkout m3-W2-aou-deltas
  ```
  Expect cosmetic nbstripout `—` (em-dash) churn on notebooks — `git checkout -f`, **NEVER commit it** (`feedback_multi_terminal_staging`).

---

## 4. THE DECISIVE CAPTURE BLOCK

Run in the **CDR-wired Standard Analysis env terminal**:

```bash
echo "WORKSPACE_CDR = $WORKSPACE_CDR"
echo "WGS_ACAF MT   = $WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"
env | grep -iE 'CDR|WGS|AUX|fc-aou|DATASET' | sort
```

Then `gsutil ls -l` the two AUX siblings under **whatever bucket prefix the WGS path reveals** (substitute the real prefix the capture printed for `<WGS_PREFIX>`):

```bash
# substitute <WGS_PREFIX> with the bucket+CDR prefix the capture printed above
gsutil ls -l "<WGS_PREFIX>/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv"
gsutil ls -l "<WGS_PREFIX>/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv"
```

The whole question turns on what `$WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` prints and whether those two `gsutil ls -l` calls now **succeed** (a real CDR-wired env carries the dataset authorization scope the featherweight env lacked).

---

## 5. Decision tree (no-change vs env-derive patch)

- **IF** the WGS prefix is `gs://fc-aou-datasets-controlled/v8/...` **AND** the two `gsutil ls -l` now **SUCCEED**
  → **CHECK C PASSES with NO code edit.** The hardcoded `AUX_BASE` at `src/python/aou_ld_panel.py:85` is correct for R9. Mark CHECK C done.

- **IF** the WGS prefix is **NOT** `gs://fc-aou-datasets-controlled/v8/...` (e.g. a different bucket, a `/v9/` segment, or an R9-specific path)
  → **that printed prefix IS the answer.** The code gets a **one-line env-derive patch**: derive `AUX_BASE` from `$WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` (the AUX TSVs are **siblings** of the WGS ACAF MT) rather than the hardcoded literal — cleaner than introducing a new literal. The existing `ancestry_table_path` / `relateds_table_path` override seam (`aou_ld_panel.py:646-648, 674-675`) already supports threading an override. **DO NOT apply the patch here** — capture the prefix, route to a **follow-up `/gsd-quick` that edits source**.

- **IF** startup showed the CDR-not-found error
  → env was **not wired**; do **not** trust any result. Relaunch a **Standard Analysis** env or report back.

> **DO NOT apply any source patch from this runbook.** This runbook only captures the data that decides which path; the edit (if any) is a **separate code-touching quick task**.

---

## 6. Forward sequence (Carter holds every trigger)

1. **Close the CDR/AUX question** via the capture block above → either "no change" (mark CHECK C done) or route the captured prefix to an **env-derive patch** quick task.
2. **Run the AOU-0 precheck notebook** (compute-free; `git clone` the repo into the env FIRST per §3) → produces `post-precheck-routing-decision.txt`.
3. **chr22 smoke** — 256-vCPU Dataproc, ~$30–75, cost-signed-off; **you hold the trigger**.
   - **Pass** → Wave 2 AOU-2 / AOU-4 paste-ins per `AOU-2-AOU-4-TRACK-4-PATTERN.md`.
   - **Fail** → 1000G AFR safety net per `feedback_no_1000g_ld_pivot` (fallback only; do not propose proactively).

---

## 7. New RW 2.0 coordinates (quick reference)

| Field | Value |
|---|---|
| Workspace ID | `aou-rw-476cdac2` (title `coloc_analysis`) |
| Google project | `wb-perky-corn-6639` |
| `WORKSPACE_BUCKET` | `gs://rw-migration-aou-rw-476cdac2` (content at bucket ROOT) |
| CDR | `C2024Q3R9` (cdrv8–R9) |
| Billing pod | `user-pod-cclinton-2d12` |
| Region | `us-central1` |
| CLI set workspace | `wb workspace set --id=aou-rw-476cdac2` |

---

*All shell/code blocks above are fenced per `feedback_code_paste_fences`. Authored 2026-05-30 (q04). DOCS ONLY — no source edits.*
