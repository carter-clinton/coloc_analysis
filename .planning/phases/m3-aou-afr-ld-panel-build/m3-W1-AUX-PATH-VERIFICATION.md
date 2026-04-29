# M3 Wave 1 — AUX Path Verification Spec

**Status:** PRE-STAGED 2026-04-28 (quick task 260428-vt2). Awaits Carter
Workbench session to execute and capture run log.

**Why this spec exists:** Of the 7 Wave 1 readiness items in
[m3-00-W0-foundations-SUMMARY.md](./m3-00-W0-foundations-SUMMARY.md)
"Wave 1 Readiness Checklist", 6 are now PASS (D-M3-09 ruled 2026-04-28
quick-260428-stv; P1+P2+P3+P4+P6 portal gates cleared 2026-04-28 under
NCSU faculty controlled-tier access; R1 HARD GATE ruled PASS 2026-04-28
in [aou-egress-audit-log.md](../../amendments/aou-egress-audit-log.md)).
The single remaining pre-condition is **AUX path verification** — a
~30-second `gsutil ls` smoke check that must run from inside an AoU
Researcher Workbench Jupyter notebook + terminal session, because the
controlled-tier AUX bucket is not reachable from outside the Workbench.

Once this verification passes (or a path fix-up commits per Failure
Mode (ii) below), Wave 1 is unblocked and `/gsd-execute-phase
m3-aou-afr-ld-panel-build` can fire the m3-01 plan
(AOU-1 cohort definition notebook → 3 checkpointed MTs).

---

## What we're verifying

The AFR cohort definition notebook in
[src/python/aou_ld_panel.py](../../../src/python/aou_ld_panel.py) (line 61)
consumes ancestry predictions from a constant
`ANCESTRY_PREDS_PATH` whose value is **inferred** from the AoU AUX
bucket pattern documented in `AOU-LD-PIPELINE.md` §3.1:

```python
# src/python/aou_ld_panel.py:58–61
AUX_BASE = f"gs://fc-aou-datasets-controlled/{CDR_VERSION}/wgs/short_read/snpindel/aux"
RELATED_SAMPLES_PATH = f"{AUX_BASE}/relatedness/relatedness_flagged_samples.tsv"
RELATEDNESS_FULL_PATH = f"{AUX_BASE}/relatedness/relatedness.tsv"
ANCESTRY_PREDS_PATH  = f"{AUX_BASE}/ancestry/ancestry_preds.tsv"  # INFERRED (Q9 / O3)
```

With `CDR_VERSION = "v7"` (per D-M3 default), the resolved path is:

```
gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
```

We need to verify two things from inside the Workbench:

1. The directory `gs://.../aux/ancestry/` is readable from Carter's
   workspace (controlled-tier access propagated to bucket ACL).
2. The filename `ancestry_preds.tsv` exists at that path. If the actual
   filename differs (`ancestry_preds_v7.tsv` /
   `ancestry_predictions.tsv` / etc), `ANCESTRY_PREDS_PATH` must be
   updated to match before Wave 1 fires.

---

## Run procedure (paste into AoU Workbench terminal)

**Pre-requisite:** Launch a Jupyter notebook in the AoU Researcher
Workbench, then open a terminal (File → New → Terminal). All commands
below assume the Workbench shell with controlled-tier credentials
already loaded.

### Step 1 — Sanity-check shell environment

```bash
# Confirm we are inside a Workbench shell with workspace context loaded.
echo "$WORKSPACE_BUCKET"
echo "$WORKSPACE_NAMESPACE"
echo "$GOOGLE_PROJECT"
```

* **Expected:** all three echo non-empty values. `WORKSPACE_BUCKET`
  resembles `gs://fc-secure-<workspace-uuid>` and is the workspace
  egress staging bucket (used by the Hail driver in
  `aou_ld_panel.py:217` for output checkpointing — **not** for
  consuming AUX data).
* **If empty:** open the AoU Workbench docs page or run
  `env | grep -i -E "BUCKET|WORKSPACE|PROJECT|AOU"` to find the right
  variable name. The Workbench should set these on every notebook
  start; if missing, the notebook session may not have fully
  initialized — restart the notebook kernel before retrying.

### Step 2 — Load-bearing command (canonical, literal path)

```bash
# Canonical AUX bucket path matching ANCESTRY_PREDS_PATH in
# src/python/aou_ld_panel.py:61. This is the authoritative command.
gsutil ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/
```

* **Expected output:** a directory listing including
  `ancestry_preds.tsv` (and possibly other files such as
  `ancestry_preds.tsv.tbi` index or per-platform variants — capture
  the full listing).
* **This is the command that confirms or refutes the inferred path.**

### Step 3 — Backup commands (env-var experiments; informational)

```bash
# Try AUX_BASE as a Workbench env var. AUX_BASE is hard-coded as a
# Python constant in src/python/aou_ld_panel.py:58, NOT documented
# as an AoU-set env var. This will likely echo empty.
echo "AUX_BASE='$AUX_BASE'"
[ -n "$AUX_BASE" ] && gsutil ls "$AUX_BASE/ancestry/" || \
  echo "(AUX_BASE not set — Step 2 literal-path command is the load-bearing one)"

# WORKSPACE_BUCKET is the workspace egress staging bucket, NOT
# the AoU AUX bucket. This is included only to confirm the bucket
# is reachable from this shell; the LISTING below will NOT contain
# AUX data.
gsutil ls "$WORKSPACE_BUCKET/" 2>&1 | head -5
```

* **Expected:** `AUX_BASE` echoes empty (this is the normal case);
  `gsutil ls $WORKSPACE_BUCKET/` returns workspace contents (likely
  empty or near-empty on first session).
* **Diagnostic value:** if Step 2 fails but `gsutil ls
  $WORKSPACE_BUCKET/` works, the issue is bucket-specific (AUX access);
  if both fail, the issue is gsutil credential / network / Workbench
  session.

### Step 4 — File-name pin

```bash
# Direct existence check on the inferred filename — this is the byte
# that, if missing, triggers Failure Mode (ii) below.
gsutil stat gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
```

* **Expected output:** `gsutil stat` prints object metadata
  (Creation time, Update time, Storage class, Content-Length, etc.) +
  exit code 0.
* **If the file exists:** Verification PASS — record the byte size and
  Content-MD5 hash from `gsutil stat` output in the Run Log below.
* **If the file is missing:** triggers Failure Mode (ii); follow
  remediation.

---

## Failure modes and remediation

### (i) Workbench env vars not set (`WORKSPACE_BUCKET` / `WORKSPACE_NAMESPACE` empty)

* **Diagnosis:** Step 1 echoes empty. Notebook session not fully
  initialized OR Workbench billing profile not yet attached / propagated.
* **Remediation:** (a) restart the notebook kernel
  (Kernel → Restart Kernel); (b) close + relaunch the notebook from
  the Workbench dashboard; (c) confirm billing profile attached in
  Workbench → Billing tab; (d) wait 5–15 min after billing-profile
  attach for Workbench resource provisioning to propagate.
* **If still empty after 15 min:** consult AoU Researcher Workbench
  documentation for the current standard env-var names (variable names
  occasionally change between Workbench releases). Run
  `env | grep -i -E "BUCKET|WORKSPACE|PROJECT|AOU"` for a full
  inventory of Workbench-set variables and pin the actual name in this
  spec under Run Log.

### (ii) `ancestry_preds.tsv` filename differs from `ANCESTRY_PREDS_PATH` constant

* **Diagnosis:** Step 2 succeeds (directory listing returns) but does
  not contain `ancestry_preds.tsv`; OR Step 4 returns
  `CommandException: No URLs matched`.
* **Remediation steps (in order):**
  1. Capture the directory listing from Step 2 verbatim — note the
     actual filename(s) under `aux/ancestry/`.
  2. Locate the `ANCESTRY_PREDS_PATH` constant:

     ```bash
     grep -n "ANCESTRY_PREDS_PATH" src/python/aou_ld_panel.py
     # expected line 61: ANCESTRY_PREDS_PATH = f"{AUX_BASE}/ancestry/ancestry_preds.tsv"  # INFERRED (Q9 / O3)
     ```

  3. Edit `src/python/aou_ld_panel.py:61` — replace
     `ancestry_preds.tsv` with the observed filename. Preserve the
     `f"{AUX_BASE}/ancestry/"` prefix; only the trailing filename
     changes. Drop the `# INFERRED` comment and replace with
     `# VERIFIED 2026-XX-XX via AoU Workbench AUX path check`.
  4. Update the docstring header at line 28 (currently reads
     `ancestry/ancestry_preds.tsv (INFERRED; Wave 1 first-fire verifies)`)
     to drop the `(INFERRED; …)` annotation in favor of the verified
     filename.
  5. Stage + commit with token `(m3-W1-aux-path-fix)` in subject:

     ```bash
     git add src/python/aou_ld_panel.py \
       .planning/phases/m3-aou-afr-ld-panel-build/m3-W1-AUX-PATH-VERIFICATION.md
     git commit -m "fix(m3-W1-aux-path-fix): pin ANCESTRY_PREDS_PATH to verified AoU AUX filename"
     ```

  6. Append the Run Log entry below documenting the observed filename,
     the byte size from `gsutil stat`, and the resulting `ANCESTRY_PREDS_PATH`
     value post-edit. This commit closes the AUX gate.

### (iii) Bucket access denied (`AccessDeniedException`)

* **Diagnosis:** Step 2 returns `AccessDeniedException: 403` or
  `Anonymous caller does not have storage.objects.list access` or
  similar.
* **Remediation:** This is access propagation lag on the AoU
  controlled-tier ACL. Wait 5–15 minutes after billing profile
  attached, then retry. If still denied after 15 min:
  (a) confirm billing profile is attached AND active in the Workbench
  → Billing tab; (b) confirm controlled-tier access is showing as
  granted in the Workbench → Profile tab; (c) confirm the workspace
  itself is created at controlled-tier (not registered-tier) — a
  registered-tier workspace cannot read the controlled-tier AUX
  bucket. If all three above check out and access is still denied,
  this becomes a per-file egress-classification trigger event per the
  ruling block in `aou-egress-audit-log.md` "Re-open conditions"; open
  an AoU support case and document under
  `## Per-Bundle Audit Entries`.

---

## Verification checklist (Carter signs off)

* [ ] **(a)** `gsutil ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/`
  returns a non-empty listing (at least one file, no
  `AccessDeniedException` or empty output).
* [ ] **(b)** `ancestry_preds.tsv` (or the observed equivalent
  filename) appears in the listing from (a).
* [ ] **(c)** `ANCESTRY_PREDS_PATH` in
  [src/python/aou_ld_panel.py](../../../src/python/aou_ld_panel.py)
  matches the observed filename byte-for-byte (no path-fix-up commit
  needed if the inferred filename was correct; otherwise commit
  `(m3-W1-aux-path-fix)` lands per Failure Mode (ii) remediation).

When all three boxes are checked and any necessary path-fix-up commit
has landed, this AUX gate clears and Wave 1 is unblocked.

---

## Run Log

Carter pastes the verbatim output of Steps 1 + 2 + 4 below, then
commits this file with the verification result.

### Run 1 — TEMPLATE (replace with actual run output)

* **Date / time (Workbench session):** YYYY-MM-DD HH:MM (Workbench timezone)
* **Workbench session:** notebook name / kernel / Workbench release
* **Workspace:** workspace title from AoU portal

```
$ echo "$WORKSPACE_BUCKET" "$WORKSPACE_NAMESPACE" "$GOOGLE_PROJECT"
<paste actual values here, redacting any sensitive workspace UUIDs only if needed>

$ gsutil ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/
<paste actual listing here>

$ gsutil stat gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
<paste actual stat output here>
```

* **Verification result:**
  * Checklist (a): PASS / FAIL
  * Checklist (b): PASS / FAIL — observed filename: `<filename>`
  * Checklist (c): PASS / FAIL — `ANCESTRY_PREDS_PATH` value:
    `<resolved path>` (matches observed filename: yes / no)
* **Path-fix-up commit (if any):** `<commit hash>` token
  `(m3-W1-aux-path-fix)`
* **Closing notes:** any anomalies, unexpected files in listing, etc.

---

**Cross-references:**

* [m3-00-W0-foundations-SUMMARY.md](./m3-00-W0-foundations-SUMMARY.md) "Wave 1 Readiness Checklist"
* [m3-01-W1-aou-cohort-and-hard-gates-PLAN.md](./m3-01-W1-aou-cohort-and-hard-gates-PLAN.md) "AUX path live verification" task
* [aou-egress-audit-log.md](../../amendments/aou-egress-audit-log.md) (R1 HARD GATE PASS 2026-04-28)
* [src/python/aou_ld_panel.py](../../../src/python/aou_ld_panel.py) (lines 17–28 docstring + lines 58–61 path constants)
* m3-RESEARCH.md §O3 "Wave 0 ancestry preds path verification" (the open question this spec closes)
* AOU-LD-PIPELINE.md §3.1 (AoU AUX bucket convention source)
