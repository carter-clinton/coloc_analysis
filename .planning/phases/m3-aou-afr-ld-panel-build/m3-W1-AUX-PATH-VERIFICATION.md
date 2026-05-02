# M3 Wave 1 — AUX Path Verification Spec

**Status:** VERIFIED 2026-05-01 against **CDR v8** (Carter Workbench session — Run 2 below).
All three checklist boxes PASS at v8; v8 AUX layout parallels v7 with `ancestry_preds.tsv`,
`relatedness_flagged_samples.tsv`, and `relatedness.tsv` at the analogous v8 paths. Initial
2026-04-30 v7 verification (Run 1 below) is preserved for forensic completeness but
**superseded by v8 adoption** per [DEC-2026-05-01-01](../../DECISIONS.md#2026-05-01--dec-2026-05-01-01-m3-cdr-v7v8-adoption-o2-trigger-fired).
The O2 re-pin trigger documented in `aou_ld_panel.py:70` (now removed) fired because the
Workbench bound `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` to v8 by default once attached to a
v8-bound workspace, creating a v8 WGS / v7 ancestry mismatch hazard. AUX gate cleared at v8;
Wave 1 unblocked.

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

### Run 1 — Carter Workbench session 2026-04-30

* **Date / time (Workbench session):** 2026-04-30 (Workbench shell;
  Jupyter container hostname `1ca6f2e2aaed`)
* **Workbench session:** Carter's first AoU Researcher Workbench
  Jupyter terminal session post-billing-profile activation (billing
  linked ~2026-04-28 per `project_aou_billing_pending.md`; processed
  by 2026-04-30)
* **Workspace:** controlled-tier workspace under NCSU faculty AoU access
  (workspace bucket UUID + namespace below)

```
$ echo "$WORKSPACE_BUCKET"
gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a

$ echo "$WORKSPACE_NAMESPACE"
aou-rw-476cdac2

$ echo "$GOOGLE_PROJECT"
terra-vpc-sc-fe7a5641

$ gsutil ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/
BadRequestException: 400 Bucket is a requester pays bucket but no user project provided.

$ gsutil -u "$GOOGLE_PROJECT" ls gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/
gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/merged_sites_only_intersection.vcf.bgz
gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/merged_sites_only_intersection.vcf.bgz.tbi
gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/preds_oth.html
gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/loadings.ht/

$ gsutil -u "$GOOGLE_PROJECT" stat gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv:
    Creation time:          Thu, 06 Apr 2023 16:14:27 GMT
    Update time:            Thu, 06 Apr 2023 16:14:27 GMT
    Storage class:          STANDARD
    Content-Length:         101406670
    Content-Type:           text/tab-separated-values
    Hash (crc32c):          qH1M/Q==
    Hash (md5):             s3egJnawX2pGSgbrxw++7g==
    ETag:                   CNyTrJ/Tlf4CEAE=
    Generation:             1680797667625436
    Metageneration:         1

$ echo "AUX_BASE='$AUX_BASE'"; gsutil ls "$WORKSPACE_BUCKET/" 2>&1 | head -5
AUX_BASE=''
gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/notebooks/
```

* **Verification result:**
  * Checklist (a): **PASS** — `aux/ancestry/` listing returns 5 entries
    (1 file `ancestry_preds.tsv` + sites-only VCF pair + diagnostic HTML +
    `loadings.ht/` Hail Table directory). No `AccessDeniedException`;
    bucket reachable from controlled-tier workspace.
  * Checklist (b): **PASS** — observed filename `ancestry_preds.tsv`
    appears in the listing; size 101,406,670 bytes (~101 MB);
    Content-MD5 `s3egJnawX2pGSgbrxw++7g==`; updated 2023-04-06
    (CDR v7 release vintage).
  * Checklist (c): **PASS** — `ANCESTRY_PREDS_PATH` in
    `src/python/aou_ld_panel.py:61` resolves to
    `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv`
    which matches the observed filename byte-for-byte. No
    path-fix-up commit needed.
* **Path-fix-up commit (if any):** N/A — inferred filename was
  correct; no edit to `src/python/aou_ld_panel.py:61` required.
  This commit (`docs(m3-W1-aux-path-verified)`) only updates the
  Run Log + Status line + drops the `# INFERRED (Q9 / O3)` annotation
  in `aou_ld_panel.py:61` to `# VERIFIED 2026-04-30 via AoU Workbench`
  per spec Failure Mode (ii) step 3 wording (housekeeping; not a
  semantic change).
* **Closing notes:**
  1. **Requester-pays operational note** — the AoU controlled-tier
     AUX bucket (`gs://fc-aou-datasets-controlled/`) is configured
     as **requester-pays**. Shell-level `gsutil` operations require
     `-u "$GOOGLE_PROJECT"` (or `-u <billing-project>`); the first
     unflagged `gsutil ls` returned `BadRequestException: 400 Bucket
     is a requester pays bucket but no user project provided.` This
     does NOT affect the Hail-side path consumption in
     `aou_ld_panel.py:152` (`hl.import_table(anc_path, ...)`) because
     Hail's GCS connector takes the billing project from the Spark
     conf set in `init_hail()` / Dataproc cluster config. AoU's
     standard Dataproc Hail setup has this wired automatically. Worth
     flagging in Wave 1 AOU-1 notebook documentation so any
     interactive `gsutil` commands Carter runs on the side
     consistently use the `-u "$GOOGLE_PROJECT"` flag.
  2. **`AUX_BASE` env var is empty (expected)** — Step 3's diagnostic
     `echo "AUX_BASE='$AUX_BASE'"` returned `AUX_BASE=''`, confirming
     this is NOT an AoU-set env var. The Step 2 literal-path command
     was the load-bearing one (as the spec anticipated). The
     Python-side `AUX_BASE` constant in `aou_ld_panel.py:58` is the
     authoritative source of the path prefix; no Workbench env var
     bridging is needed.
  3. **Workspace bucket reachable** — `gsutil ls $WORKSPACE_BUCKET/`
     returned `gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/notebooks/`,
     confirming the workspace egress staging bucket is provisioned
     and writable. This is the bucket
     `aou_ld_panel.py:217` will checkpoint MTs into during Wave 1
     (`mt_afr_qc.mt`, `mt_afr_pca_selfid.mt`, `mt_eur_qc.mt`).
  4. **Unexpected directory entries** — the listing also includes
     `merged_sites_only_intersection.vcf.bgz` (+ `.tbi`),
     `preds_oth.html` (the diagnostic page for the AoU "oth" /
     undetermined-ancestry assignments), and `loadings.ht/` (Hail
     Table with PCA loadings). These are NOT consumed by
     `aou_ld_panel.py` (which reads only `ancestry_preds.tsv`) so
     their presence is informational. If Wave 1 sensitivity analyses
     ever need PCA loadings (RESEARCH O5 deferred), `loadings.ht/`
     is the path.
  5. **CDR-version pin still v7** — `CDR_VERSION = "v7"` in
     `aou_ld_panel.py:57` matches the verified bucket layout. O2
     re-pin trigger ("if v8 lands during Wave 1-3") not yet active;
     re-verify at submission time per spec.

---

### Run 2 — Carter Workbench session 2026-05-01 (CDR v8 adoption)

* **Date / time (Workbench session):** 2026-05-01 (Workbench shell;
  same Jupyter container hostname `1ca6f2e2aaed` as Run 1)
* **Workbench session:** Same workspace as Run 1; CDR v8 binding
  surfaced via `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` defaulting to a
  v8 path on this fresh post-clone import sanity check.
* **Trigger:** Mid-flight O2 trigger ("if v8 lands during Wave 1-3")
  fired when AOU-1 Cell 1 import sanity check revealed the workspace
  WGS path is v8 (`gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt`)
  while `ANCESTRY_PREDS_PATH` was still pinned to v7. Mixed v8 WGS +
  v7 ancestry preds risked silent cohort under-counting if AoU
  re-derived ancestry inference for v8.

```
$ gsutil -u "$GOOGLE_PROJECT" ls gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/eigenvalues.txt
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/merged_sites_only_intersection.vcf.bgz
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/merged_sites_only_intersection.vcf.bgz.tbi
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/preds_oth.html
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/rf_classifier.pkl
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/training_pca.tsv
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/loadings.ht/

$ gsutil -u "$GOOGLE_PROJECT" stat gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
[Created/updated 2025-01-20; 171,388,042 bytes (~163 MiB);
 MD5 xfx08/nBfrkxJ+J2j8aL0A==; CRC32C B3HktA==]

$ gsutil -u "$GOOGLE_PROJECT" ls gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/relatedness/
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/relatedness/relatedness.tsv
gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv

$ gsutil -u "$GOOGLE_PROJECT" stat gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv
[v7 still resolves; original 2023-04-06 timestamp; both versions coexist]
```

* **Verification result:**
  * Checklist (a): **PASS at v8** — `aux/ancestry/` listing returns 8 entries
    (v7's 5 + new v8 additions: `eigenvalues.txt`, `rf_classifier.pkl`,
    `training_pca.tsv` for the v8 ancestry inference pipeline). No
    `AccessDeniedException`; bucket reachable from controlled-tier workspace.
  * Checklist (b): **PASS at v8** — observed filename `ancestry_preds.tsv`
    appears in the v8 listing; size 171,388,042 bytes (~163 MiB; **~+69 %**
    over v7's 101 MiB consistent with v8's larger participant roster);
    Content-MD5 `xfx08/nBfrkxJ+J2j8aL0A==`; updated 2025-01-20 (CDR v8
    release vintage). `relatedness_flagged_samples.tsv` and
    `relatedness.tsv` also confirmed at parallel v8 paths.
  * Checklist (c): **PASS at v8 after CDR_VERSION bump** —
    `ANCESTRY_PREDS_PATH` in `src/python/aou_ld_panel.py:75` now resolves
    to `gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv`
    after the `CDR_VERSION = "v7" → "v8"` edit. Matches the observed v8
    filename byte-for-byte.
* **Path-fix-up commit (yes):** `feat(m3-aou-afr-ld-panel): bump CDR_VERSION
  v7→v8 (O2 trigger; v8 AUX paths verified)`. Edits CDR_VERSION pin,
  refreshes inline VERIFIED comments, retires the O2 re-pin trigger comment
  (now resolved), and updates the docstring path example. RELATED_SAMPLES_PATH
  + RELATEDNESS_FULL_PATH automatically re-derive via `f"{AUX_BASE}/..."`
  string interpolation; no per-constant edits needed beyond CDR_VERSION.
* **Closing notes:**
  1. **v8 has 3 new sibling files** vs v7 — `eigenvalues.txt`,
     `rf_classifier.pkl`, `training_pca.tsv`. These are the AoU v8
     ancestry inference pipeline artifacts (eigenvalues for the v8 PCA,
     scikit-learn pickled RF classifier, and the training PCA TSV used
     to fit the classifier). NOT consumed by `aou_ld_panel.py` (which
     reads only `ancestry_preds.tsv`). Worth flagging as candidate
     data for a future RESEARCH O5 sensitivity analysis where the
     ancestry inference reproducibility could be evaluated against
     the AoU classifier directly. Documented here for discoverability.
  2. **Sample roster delta** — v8 ancestry_preds.tsv ~163 MiB vs v7
     ~97 MiB ≈ +69 %, suggesting v8 has roughly +60-80 k participants
     over v7 (rough estimate from per-row byte size; exact count
     surfaces during AOU-1 Cell 2 `count_cols()`). This affects every
     planning-time sample-N estimate in m3-RESEARCH.md and m3-CONTEXT.md
     (D-M3-DEFAULT v7 pin); per DEC-2026-05-01-01, those numbers
     re-baseline at AOU-1 fire time and are not retroactively rewritten
     in the planning artifacts (per `feedback_original_research_framing.md`).
  3. **v7 still resolves** — `gsutil stat` on the v7 path returned its
     original 2023-04-06 metadata. v7 → v8 is **not a forced migration**;
     both versions coexist in the controlled-tier bucket. The v8 adoption
     is driven by Workbench default behavior + larger participant set,
     not by v7 deprecation.
  4. **Requester-pays model unchanged at v8** — same `-u "$GOOGLE_PROJECT"`
     flag pattern as v7. Hail's GCS connector handles this transparently.
  5. **CDR-version pin now v8** — `CDR_VERSION = "v8"` in
     `aou_ld_panel.py:74` matches the verified bucket layout. O2 trigger
     RESOLVED — comment retired in this commit. Next reverify trigger:
     CDR v9 if it lands during Wave 4-5; lock at submission.

---

**Cross-references:**

* [m3-00-W0-foundations-SUMMARY.md](./m3-00-W0-foundations-SUMMARY.md) "Wave 1 Readiness Checklist"
* [m3-01-W1-aou-cohort-and-hard-gates-PLAN.md](./m3-01-W1-aou-cohort-and-hard-gates-PLAN.md) "AUX path live verification" task
* [aou-egress-audit-log.md](../../amendments/aou-egress-audit-log.md) (R1 HARD GATE PASS 2026-04-28)
* [src/python/aou_ld_panel.py](../../../src/python/aou_ld_panel.py) (lines 17–28 docstring + lines 58–61 path constants)
* m3-RESEARCH.md §O3 "Wave 0 ancestry preds path verification" (the open question this spec closes)
* AOU-LD-PIPELINE.md §3.1 (AoU AUX bucket convention source)
