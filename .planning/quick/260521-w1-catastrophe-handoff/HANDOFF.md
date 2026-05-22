# m3-W1 Empty-MT Catastrophe — Next-Session Handoff

**Created:** 2026-05-21 end-of-session
**Status:** Active — read this FIRST when resuming work on coloc_analysis m3
**Branch at handoff:** main (= origin/m3-W2-aou-deltas) HEAD `822d47d`

---

## TL;DR (read this in 60 seconds)

m3-W1 Wave 1 catastrophically failed. All 3 cohort MTs that prior sessions claimed "committed" are 0×0 empty schema-only skeletons in the AoU bucket. ~$2,140 of compute produced no usable data. Root cause is Hail's `mt.checkpoint()` writing `_SUCCESS` markers based on driver-side task accounting without contents validation, compounded by v7→v8 CDR partition explosion and executor-side memory pressure under aggressive `spark.executor.cores=1/mem=5g` profile. Verification methodology never traversed `entries/entries/parts/` — only checked `_SUCCESS` markers.

**Path forward = 4 parallel NCSU-only tracks. No AoU compute needed for 1-2 weeks.**

**AoU env is DELETED.** Do not recreate without (a) NCSU code patches landed AND (b) chr22 smoke fire validated.

---

## What you should KNOW before doing anything

1. **STATE.md `stopped_at` field has the full chain.** Read it before this handoff if you want the long version.
2. **Debug session file at `.planning/debug/m3-W1-empty-mt-catastrophe.md`** (40 KB) is the authoritative root-cause analysis.
3. **Two new memories baked 2026-05-21:**
   - `[[feedback_aou_success_marker_not_evidence_of_data]]` — _SUCCESS alone is NOT evidence
   - `[[feedback_hail_checkpoint_contract_violation]]` — Hail's task-accounting-not-contents-validation
4. **One memory amended:** `[[feedback_aou_spark_ui_stack_trace_verification]]` — cascade signature is necessary but NOT sufficient
5. **Project state memory updated:** `[[project_state]]` now reflects catastrophe + 4 tracks

## What the bucket actually contains (as of 2026-05-21 end-of-session)

```
gs://${WORKSPACE_BUCKET}/
├── forensics/
│   └── hail.log.pre_pd_migration.20260521T201919Z.log  (~27 MiB; W1 forensic from EUR write attempt)
└── ld/
    ├── mt_afr_qc.mt/         ← 0×0 EMPTY (full schema, _SUCCESS markers, 2,045 partitions of ~35-byte Parquet footers)
    └── mt_afr_pca_selfid_qc.mt/  ← 0×0 EMPTY (same pattern)
    (mt_eur_qc.mt/ does not exist)
```

Bucket-wide total: ~71 MiB. Cannot contain populated WGS MTs of any kind.

## The 4 parallel tracks (all NCSU-only, no AoU compute needed)

### Track 1 — AoU credit recovery claim (FILE FIRST — evidence is freshest now)

**Goal:** Submit AoU researcher support ticket requesting compute credit recovery for the $2,140 lost to platform-level Hail contract violation.

**Why it's worth filing:**
- Hail wrote `_SUCCESS` on empty MTs — that's a platform contract violation, not user error
- Hail's `mt.checkpoint()` task-completion accounting is decoupled from contents validation
- Full forensic chain documented in `.planning/debug/m3-W1-empty-mt-catastrophe.md` + `.planning/quick/260511-aou-w2-oom-fix/forensics/`
- AoU has discretion to credit back compute lost to platform issues; this is a strong case

**Suggested claim contents:**
- Hail read-probe transcript (count_cols=0, count_rows=0, TOTAL CELLS=0 on both AFR MTs despite _SUCCESS stack)
- bucket-wide `gsutil du -s` showing ~71 MiB total
- Reference to the 2026-05-04 forensics directory (`.planning/quick/260511-aou-w2-oom-fix/forensics/2026-05-04-stage8-regionpool-oom/00_README.md`)
- The 2026-05-21 Hail read-probe full output (also captured in debug session file)
- Cost ledger: $10 + $10 + $17 + $1,275 + $30 = ~$2,142

**STATUS (2026-05-22):** Initial Zendesk ticket FILED. Awaiting AoU Research Support reply to `carterclinton@ncsu.edu`. Full follow-up email draft saved at [`AOU-SUPPORT-FOLLOWUP-DRAFT.md`](AOU-SUPPORT-FOLLOWUP-DRAFT.md) for when AoU asks for forensic detail.

**IMPORTANT email constraint (per [[feedback_aou_researcher_email_auth_only]]):** Carter's AoU researcher account `cclinton@researchallofus.org` is AUTH-ONLY — Gmail is disabled at the researchallofus.org org admin level. ALL email correspondence MUST go to `carterclinton@ncsu.edu`. Reference the researcher account inline in ticket bodies for account correlation, but NEVER CC it or set it as reply-to.

**Start command:** "draft AoU credit claim" — Claude writes the formal text, Carter submits via AoU support form.

### Track 2 — Pivot Wave 2 to 1000G LD substrate (FREE, unblocks immediately)

**Goal:** Make Wave 2 dev fire executable without ANY AoU compute, using existing 1000G AFR + EUR LD panels.

**Steps:**
1. 1000G EUR Phase 3 LD panel already at `data/processed/ld_reference/EUR/*.rds` (from Track A)
2. Download 1000G AFR Phase 3 panel (~2 GB, free, ~30 min) — Zenodo or 1000G FTP
3. Revise Wave 2 plan (`.planning/phases/m3-aou-afr-ld-panel-build/m3-02-W2-dev-fire-and-validation-PLAN.md`) to use 1000G as the LD source for the 4 validation checks
4. Document "limited LD substrate" deviation in OSF amendment trail (`.planning/amendments/`)
5. Wave 2 dev fire runs entirely on NCSU HPC

**Trade-offs (transparently documented):**
- Lower power for AFR-specific signals (1000G AFR N=661 vs AoU ~91k)
- Smaller LD panel → noisier rare-allele estimates
- Track B's full-power Wave 4 fire becomes grant-funded follow-on

**Start command:** "pivot to 1000G" — Claude drafts the plan revision + 1000G AFR download script + OSF deviation entry.

### Track 3 — NCSU v7→v8 forensic investigation (FREE, identifies the schema mismatch)

**Goal:** Read the v7 success log vs v8 fail log to identify EXACTLY what changed in the v7→v8 CDR bump that broke cohort definition. If the fix is small, future rebuild becomes cheap (~$200-400 instead of $1500-2500).

**Steps:**
1. Read `.planning/quick/260511-aou-w2-oom-fix/forensics/2026-05-04-stage8-regionpool-oom/11_hail_current_run.log` (2.9 MB — v8 failed run)
2. Read `12_hail_prior_run.log` (2.9 MB — v7 successful run)
3. Diff sample counts, column names, ancestry_pred lookup behavior between the two
4. Most likely candidate: `ANCESTRY_FIELD` constant in `aou_ld_panel.py` doesn't match v8's actual column name, causing `filter_cols(mt[ANCESTRY_FIELD] == ancestry)` to filter everything out

**Start command:** "investigate v8 mismatch" — Claude reads the logs and produces a diff analysis.

### Track 4 — NCSU code patches (FREE, prevents recurrence)

**Goal:** Land the code patches the debugger identified, so any future fire (with credit-recovered AoU compute or grant funding) cannot reproduce this catastrophe.

**Mandatory patches (per `.planning/debug/m3-W1-empty-mt-catastrophe.md`):**

1. **Add `_validate_checkpoint_populated(uri)` helper** in `src/python/aou_ld_panel.py`:
   - Validates `_SUCCESS` marker exists
   - Validates `entries/entries/parts/` is non-empty (gsutil du > minimum threshold)
   - Validates Hail-level `mt.count_rows() > 0`
2. **Replace `_has_checkpoint()` calls** in auto-resume state machine (lines 554, 572)
3. **Add post-write contents assertion** after each `mt.checkpoint()` call (lines 641, 667, 687):
   ```python
   mt = mt.checkpoint(ckpt, overwrite=True)
   n_rows = mt.count_rows()
   n_cols = mt.count_cols()
   assert n_rows > 0 and n_cols > 0, (
       f"checkpoint wrote empty MT at {ckpt}: {n_rows} rows × {n_cols} cols. "
       f"See [[feedback_hail_checkpoint_contract_violation]]."
   )
   ```
4. **Add 3 regression tests** in `tests/m3/test_aou_ld_panel_local.py`:
   - `test_validate_checkpoint_populated_rejects_stub_entries`
   - `test_validate_checkpoint_populated_rejects_empty_entries_dir`
   - `test_has_checkpoint_vs_validate_diverge_on_stub_mt`
5. **Insert bucket-state assertion cells** in `.planning/notebooks/AOU-1_template.ipynb` (Cells 3.5 / 4.5 / 5.5):
   ```python
   import subprocess
   r = subprocess.run(["gsutil", "du", "-s", ckpt_uri + "/entries/entries/parts/"], capture_output=True, text=True)
   size_bytes = int(r.stdout.split()[0]) if r.returncode == 0 else 0
   assert size_bytes > 10_000_000_000, f"MT entries < 10 GB: {size_bytes:,} bytes at {ckpt_uri}"
   ```
6. **Update `.planning/WAVE-1-CLOSEOUT-CHECKLIST.md`** STEP 3 to verify entries/ size, not just `_SUCCESS`
7. **Add new decision token** to m3-CONTEXT.md (D-M3-XX) documenting the new verification protocol

**Start command:** "land the code patches" — Claude implements all 7 patches with TDD discipline (RED tests first), commits each atomically.

## DO-NOT-DO list

1. **DO NOT fire any AoU compute** without:
   - `_validate_checkpoint_populated()` landed (Track 4)
   - chr22 smoke fire validated (only do this AFTER Track 4 + ideally AFTER Track 3 reveals v8 mismatch fix)
   - Verified AoU credit availability (don't burn more $$ on speculation)
2. **DO NOT trust `_SUCCESS` markers alone** as evidence of write success. Always check `entries/entries/parts/` size + Hail `count_cols + count_rows` per `[[feedback_aou_success_marker_not_evidence_of_data]]`.
3. **DO NOT use Spark UI cascade signature inference** as the sole verification per amended `[[feedback_aou_spark_ui_stack_trace_verification]]`. Cascade is necessary but NOT sufficient.
4. **DO NOT defer the AoU credit claim.** File ASAP while forensic evidence is fresh and AoU staff can correlate to recent timestamps.
5. **DO NOT recreate the AoU env** until Tracks 3+4 are landed. The env was DELETED end-of-session to stop the $19/hr meter; recreation overhead is ~10 min, worth waiting until the rebuild path is clean.
6. **DO NOT touch Track A artifacts.** Per `[[track_a_submission_in_progress]]` + `[[feedback_stop_asking_track_a]]` Carter's submission lane is locally on his machine; nothing in `targeted_rerun_*` / `results_lsweep_L*.preFix.bak.*` is yours to commit.
7. **DO NOT mark Wave 1 as complete** in any future STATE.md / ROADMAP update — the HONEST_FINDING disposition stands.

## What SURVIVED the catastrophe (don't redo this work)

- **W2 design-delta** (quick task `260520-s2s`): all 7 POST-WAVE-1-ROADMAP design questions resolved; code deltas landed at commits `51f9ce2 RED → 0abff84 GREEN → 595d1f3 docs → a4424be close-out`. These are per-region LD-compute deltas (Wave 2/4), NOT cohort-def deltas (Wave 1). They'll be re-used regardless of which track succeeds.
- **W2 notebook authoring** (commits `e3c29e7 → 6962607 → 001d8b1 → 822d47d`): AOU-2 + AOU-4 notebooks with 12 + 13 cells respectively, 5 pytest scaffolds, 4 .gitkeep dirs. These run against EITHER rebuilt AoU MTs OR 1000G LD compute outputs.
- **Refactored `load_qc_cohort`** with Phase 1/2/3 intermediate checkpoints (commit chain ending at `bd144a6`): still useful, just needs Track 4 patches before any production fire.
- **AOU-LD-PIPELINE.md §11.0**: cluster sizing analysis still valid; 256 vCPU minimum stands.
- **OSF amendment trail** (`.planning/amendments/`): pre-registration intact; Wave 1 deviation will be appended.

## Recommended starting move for the next session

Open Claude Code, type:

```
/gsd-resume-work
```

OR if `/gsd-resume-work` doesn't pick up this handoff cleanly, just paste:

> Read .planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md and tell me which of the 4 tracks to start with. I'm leaning toward [pick: Track 1 credit claim / Track 2 1000G pivot / Track 3 v8 investigation / Track 4 code patches / all in parallel].

Claude has full context via:
- This HANDOFF.md
- `.planning/STATE.md` `stopped_at` field
- `.planning/debug/m3-W1-empty-mt-catastrophe.md` (40 KB forensic analysis)
- The two new memories + amended stack-trace memory
- Updated `[[project_state]]` memory

## Carter's emotional state at handoff

Discouraged. Lost ~$2,100. Cannot afford another $2,000 rebuild. Going home for the day. Tracks 1+2 are the most important psychologically — Track 1 might recover the money, Track 2 unblocks the science without spending more.

Lead with empathy. The work is recoverable. The science isn't dead. We have a clear path forward that doesn't require Carter to come up with another $2k.

## Carter's title (corrected 2026-05-22)

Carter is **Assistant Professor and Director of the ASHES Laboratory at North Carolina State University**. Do NOT refer to him as PhD candidate, postdoc, or graduate student in any email signature, correspondence, or attribution. See [[feedback_user_profile_correction_2026-05-22]] / updated [[user_profile]] memory.
