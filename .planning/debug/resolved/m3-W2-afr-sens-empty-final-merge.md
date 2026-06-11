---
status: resolved
resolution: "2026-06-11 — H1 (driver killed mid-finalize-flush) confirmed; recovered via finalize-only re-drive from the 22 intact intermediates + gsutil rsync promote; AFR-sens cohort banked (62,557×20,817,925). Durable atomic-final-write fix DESIGNED (DURABLE-FIX-DESIGN-atomic-final-write.md) but NOT applied — route via /gsd-plan-phase --gaps before GATE 3. Pattern: knowledge-base.md#m3-empty-mt-success-before-validate."
trigger: "m3-W2-afr-sens-empty-final-merge — AFR-sens clean re-fire traversed all 22 chroms but produced an EMPTY final MT (mt_afr_pca_selfid_qc.mt: _SUCCESS + 0-byte entries/rows/cols), W1 catastrophe signature localized to the final union/merge/write"
created: 2026-06-10T00:00:00Z
updated: 2026-06-10T00:00:00Z
mode: find_root_cause_only
symptoms_prefilled: true
---

# Root Cause Analysis: m3-W2 AFR-sens empty final MT (final-merge localized)

Cross-links:
- `.planning/debug/m3-W1-empty-mt-catastrophe.md` — THE prior root-cause analysis of this exact signature class (empty MT + `_SUCCESS`). The defenses described there (`_validate_checkpoint_populated`, `_assert_checkpoint_nonempty`, the catastrophe-pattern auto-fresh branch) all LANDED since and are what this session reasons against.
- `.planning/debug/m3-W2-afr-sensitivity-selfid-noop.md` — the contamination/no-op fix (SENS_FILTER_VERSION=2). The self-report filter that the live run printed `74576 -> 63312` is THIS code path working correctly.
- `.planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md` — the per-chrom fan-out (ab0853a) whose union+finalize tail is the suspect region.

## Confidence

- **HIGH** that the failure is localized to the post-fan-out **final union + `_apply_sample_qc_and_finalize` write**, NOT the per-chrom Phase 1-2 traversal (the symptom itself asserts intermediates exist; the code shows per-chrom recursion stops at `post_variant_qc` with its own `_assert_checkpoint_nonempty` guard, so each per-chrom checkpoint self-validated as it landed).
- **HIGH** that an EMPTY final MT did NOT raise inside Cell 4 because the in-code post-write guard (`_assert_checkpoint_nonempty` at aou_ld_panel.py:1974) was **never reached** — the driver/kernel terminated between Hail's `_SUCCESS` write and that guard's `count_rows()/count_cols()`. Reason: the guard, if reached on a 0x0 MT, RAISES a loud RuntimeError (line 1022-1027) — and the symptom reports NO traceback + a reset (Idle/"No Kernel") kernel with the in-memory `mt_afr_selfid` object GONE. A reached-and-passed guard is impossible (the MT is empty); a reached-and-raised guard would have left a traceback. So it was not reached.
- **MEDIUM** on WHICH of two non-exclusive mechanisms produced the empty final: (H1) the websocket-drop / stray-navigation killed the driver mid-final-write (the kernel-death reading — empty is an artifact, intermediates are real, recovery is cheap), vs (H2) the union/finalize genuinely computed a 0-row or 0-col result that Hail finalized empty and the kernel died at/just after the same point (a real logic defect — far more serious). The two are distinguishable ONLY with in-perimeter data-layer probes (below). The FIRST DIAGNOSTIC PRIORITY probe (du-floor the 22 intermediates) gates this.
- **LOW-MEDIUM** that a third mechanism (H3: `union_rows` schema/key quirk over 22 inputs silently yielding empty, or H4: a het-band / sample-callrate predicate collapsing the sample axis) is the cause — both are argued against below but cannot be fully excluded from code alone.

---

## Root Cause Statement (proximate, pending probe confirmation)

The AFR-sens final cohort MT `gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_pca_selfid_qc.mt` is empty (`_SUCCESS` + 0-byte `entries/`, `rows/`, `cols/`) because the final write step never completed its **in-code post-write validation**. The per-chrom fan-out (Phases 1-2, ×22) and the self-report restriction (`74576 -> 63312`, printed live) demonstrably ran. The failure is downstream of those, at the union → `_apply_sample_qc_and_finalize` → `mt.checkpoint(ckpt, overwrite=True)` → `_assert_checkpoint_nonempty` sequence (aou_ld_panel.py:1550-1570 caller; 1971-1975 finalize).

The single most-likely mechanism (H1): Hail's `mt.checkpoint()` async driver-side `finalize()` wrote the `_SUCCESS` marker on tasks-reported-complete accounting, then the **stray-browser-navigation / websocket drop terminated the driver JVM (or the kernel that owns it) before the writer flushed entries row-group payloads AND before `_assert_checkpoint_nonempty` (line 1974) could run its `count_rows()/count_cols()`**. This is exactly the W1 finalize-contract weakness ([[feedback_hail_checkpoint_contract_violation]]), here NOT prevented because the guard that defends against it lives one statement AFTER the `_SUCCESS`-writing checkpoint and was never reached. The 22 per-chrom intermediates are expected to be POPULATED (each self-validated at write time) → recovery should be a cheap re-drive of ONLY the final merge, not another 15h fan-out. CONFIRM via the probe battery before any action.

---

## Code Evidence (what the source establishes)

### E1 — The per-chrom recursion stops at `post_variant_qc` and self-validates (intermediates should be real)
- `load_qc_cohort` genome-wide branch (1521-1570) loops `AUTOSOMES` (chr1..chr22), recursing with `interval_filter="chrN", _skip_final_write=True` (1530-1542).
- Each per-chrom recursion runs Phase 1 (read/ancestry/relateds/**sensitivity self-report restriction**/coalesce/split → `post_split` checkpoint) and Phase 2 (variant_qc → `post_variant_qc` checkpoint), then **returns at line 1907-1908** (`if _skip_final_write: return mt`). It NEVER runs sample QC or the final write.
- BOTH per-chrom checkpoints are guarded by `_assert_checkpoint_nonempty(mt, ckpt, phase=...)` at lines 1826 (post_split) and 1894 (post_variant_qc). That guard calls `count_rows()+count_cols()` and RAISES on any empty axis (988-1027).
- **Implication:** if any per-chrom intermediate had landed empty, that chrom's recursion would have raised LOUDLY (traceback) and the genome-wide loop would have aborted before reaching chr22 / the union. The run reportedly traversed all 22. So the per-chrom intermediates self-validated as populated AT WRITE TIME. (Caveat per [[feedback_hail_checkpoint_contract_violation]]: a kernel death during one of the per-chrom writes is also possible, but then the loop would not have advanced past that chrom — the all-22-traversed claim argues against it. Probe FIRST anyway.)

### E2 — The self-report restriction (the sensitivity-specific branch) ran correctly and is UPSTREAM of the failure
- Step 4 (1735-1810) sources `self_report` via `_resolve_aux_file`/`import_table`/`annotate_cols`, asserts coverage ≥ `MIN_SELF_REPORT_COVERAGE` (1780), applies `filter_cols(self_report.contains("WhatRaceEthnicity_Black"))` (1791-1792), then asserts a PROPER non-empty subset `0 < N_post < N_pre` (1799-1807) and prints `N_pre -> N_post` (1808-1810).
- The live run printed `sensitivity self-report filter applied: 74576 -> 63312 samples (match=WhatRaceEthnicity_Black, ver=2)`. That print is EMITTED ONLY if the proper-subset assertion PASSED. So Step 4 worked and did NOT zero the cohort.
- **Implication:** the empty final is NOT caused by the self-report filter (the 2026-06-08 no-op fix is working). The sensitivity-specific divergence from the primary path is fully contained in Phase 1 of each per-chrom recursion and is PROVEN to have produced a non-empty (63,312-sample) per-chrom cohort. This answers key-question #4: the join against the self-report keytable does NOT zero rows AFTER per-chrom QC — it happens BEFORE the per-chrom checkpoints, and it printed a healthy subset.
  - NOTE: the `74576 -> 63312` print is PER-CHROM (Step 4 runs inside each recursion). The symptoms cite it as a single line; in the live log it should appear ~22 times (once per autosome), all with N_post = the same 63,312 in-scope-before-sample-QC count (Step 4 is sample-axis only; chrom-independent). Worth confirming in the hail.log scrollback (probe P6).

### E3 — The final-write post-validation guard is one statement AFTER the `_SUCCESS`-writing checkpoint
- `_apply_sample_qc_and_finalize` (1919-1977): sample_qc (1950) → optional call_rate filter (1951-1952) → het ±3SD band (1960-1966) → `ckpt = _qc_checkpoint_uri(...)` (1972) → `mt = mt.checkpoint(ckpt, overwrite=True)` (1973) → `_assert_checkpoint_nonempty(mt, ckpt, phase="final")` (1974) → print "wrote final" (1975).
- `mt.checkpoint()` (1973) is the statement that triggers Hail's writer + driver-side `finalize()` (which writes `_SUCCESS`). `_assert_checkpoint_nonempty` (1974) is a SEPARATE subsequent Hail action (`count_rows()/count_cols()`).
- **Implication:** there is a window between (1973) writing `_SUCCESS` and (1974) validating contents. A driver/kernel death anywhere in that window leaves EXACTLY the observed state: `_SUCCESS` present, entries unflushed/empty, assertion never raised, no traceback, in-memory object gone. This is the H1 mechanism and is the single highest-prior reading.

### E4 — An empty final reaching the guard would have RAISED (so the guard was NOT reached)
- `_assert_checkpoint_nonempty` (988-1027): on `0x0` it raises "the m3-W1 empty-MT catastrophe signature" RuntimeError; on `N x 0` (sample-axis collapse) or `0 x N` (variant-axis collapse) it raises distinct messages.
- The symptom reports `entries/`, `rows/`, AND `cols/` all 0 bytes = a true `0x0` skeleton.
- **Implication:** had (1974) executed against this `0x0` MT, Cell 4 would have shown a loud RuntimeError traceback. The symptom reports NO traceback (kernel reset to Idle, object gone). Therefore (1974) did not execute → the driver died at/before it. This is strong evidence for H1 (kernel/driver death) over H2/H3/H4 (genuine empty-compute that ran to completion), because any genuine-empty path that ran `_apply_sample_qc_and_finalize` to completion WOULD have hit the raising guard.
  - The ONLY way a genuine-empty result evades a traceback is if the kernel died at the same point regardless of cause — i.e. H2/H3/H4 would ALSO have to coincide with a kernel death right at the final write to hide the traceback. That coincidence is possible but lower-prior than H1, where the death IS the cause.

### E5 — `union_rows` is variant-axis and metadata-level; unlikely to silently empty, but not impossible
- `mt = per_chrom_mts[0].union_rows(*per_chrom_mts[1:])` (1550). `union_rows` concatenates rows (variants) across the 22 disjoint-interval MTs; requires identical col-keys (samples) + row schema. All 22 are built from the same source/ancestry/relateds/self-report filter, so cols are identical and row schema identical.
- `union_rows` does not DROP rows; an empty result would require ALL 22 inputs empty (excluded by E1) or a Hail-version quirk. The fan-out debug doc flags a fallback (two-level pairwise union) if a 22-way `union_rows` quirk ever surfaces.
- **Implication:** H3 (union quirk) is LOW prior but is cheaply tested by the probe battery (the union output is only realized at the final checkpoint; if intermediates are populated AND the final is empty, re-driving the union in isolation discriminates union-quirk from kernel-death).

### E6 — Sample-axis collapse at the final (het band / call_rate) would yield `N x 0`, not `0x0` — and would RAISE
- Phase 3 (1947-1966): `sample_qc` → call_rate ≥ 0.98 filter (applied at genome scale since union row-count ≫ 500K, 1559) → het ±3SD band (1962-1966).
- If the call_rate or het filter dropped EVERY sample, the result is `rows>0, cols=0` → `_assert_checkpoint_nonempty` raises the "sample (column) axis collapsed" message (997-1009). That is `N x 0`, NOT the observed `0x0`, AND it would raise.
- **Implication:** H4 (Phase-3 sample-axis collapse) is argued against by BOTH the `0x0` shape (cols/ is 0 bytes but so is rows/) AND the no-traceback observation. LOW prior. (Caveat: a 0-byte `cols/` on disk for an interrupted write is ALSO consistent with H1 — the writer never flushed any axis. So `0x0`-on-disk does not by itself prove the compute produced 0x0; it is consistent with an interrupted flush. The discriminator is whether the union of intermediates, re-driven, produces a populated final.)

### E7 — force_fresh propagation is correct (resume-off-contaminated is not in play)
- The fire used `force_fresh=True` (symptom). The genome-wide branch passes `force_fresh=force_fresh` to each per-chrom recursion (1539), and `overwrite_flag = force_fresh or auto_fresh` (1683) makes intermediate writes overwrite. So this clean re-fire did NOT resume off the contaminated 7.8 TiB v1 intermediates. The empty final is a property of THIS fresh fire, not a stale-resume artifact.

---

## Ranked Hypotheses

### H1 (PRIMARY, HIGH prior) — Kernel/driver death in the `_SUCCESS`→validate window of the final write
The stray-browser-navigation / websocket drop terminated the driver JVM (or orphaned/killed the kernel that owns the Py4J gateway and thus the SparkContext) AFTER `mt.checkpoint()` (1973) wrote `_SUCCESS` but BEFORE the writer flushed entries row-groups AND before `_assert_checkpoint_nonempty` (1974) ran. Result: `_SUCCESS` + 0-byte axes, no traceback, in-memory object gone. Per-chrom intermediates are POPULATED (E1). Recovery = re-drive ONLY the final union+finalize from existing intermediates (cheap).
- FOR: E3 (the guard is one statement after the `_SUCCESS` write), E4 (no traceback ⇒ guard not reached ⇒ death before it), the explicit "stray browser navigation dropped the websocket / kernel reconnected Idle" symptom, the `0x0`-all-axes-0-byte shape consistent with an interrupted flush that never wrote any axis payload, and AFR-primary+EUR succeeding on the same code path (so the path is not categorically broken).
- AGAINST: the symptom's own note that "the Dataproc job runs server-side, browser-independent, so the websocket drop should NOT have killed the driver — but this is unconfirmed." If the driver truly survived, the write should have COMPLETED and the guard should have RAISED on empty or PASSED on populated — neither matches a silent empty. This tension is the crux H1 must resolve: see P3 (`_SUCCESS` mtime vs intermediate mtimes) + P4 (Dataproc job/YARN application final state) — they directly test whether the driver outlived the websocket.

### H2 (SECONDARY, MEDIUM prior) — Genuine empty-compute at the union/finalize, coincident with kernel death
The union or Phase-3 actually produced an empty result (some real defect), Hail finalized it empty, and the kernel died at the same point so no traceback surfaced. This is the "far more serious" reading from key-question #3.
- FOR: cannot be excluded from code alone; `union_rows`/Phase-3 edge cases (H3/H4) feed this.
- AGAINST: requires a coincidence (real-empty AND kernel-death-right-then to hide the traceback); E4 shows a completed-but-empty compute would normally RAISE. Lower prior than H1.
- Discriminator: re-drive the union+finalize from the existing intermediates in a FRESH kernel with the guard active (P7). If it reproduces empty → H2/H3/H4. If it yields ~62-62.5K × ~20.5-20.8M → H1.

### H3 (LOW prior) — `union_rows` 22-way quirk silently yields empty/mis-schema
A Hail-version interaction in the flat 22-way `union_rows` (1550) produces an empty or zero-row union.
- AGAINST: union_rows is additive; documented fallback exists; EUR/AFR-primary used the SAME union path and succeeded.
- Discriminator: P7 (re-drive union); if empty, P7b (two-level pairwise union fallback).

### H4 (LOW prior) — Phase-3 sample-axis collapse (call_rate 0.98 / het ±3SD drops all samples)
- AGAINST: would yield `N x 0` (rows survive) and would RAISE the "sample axis collapsed" message — neither the observed `0x0` nor the no-traceback. AFR-primary passed the identical Phase-3 over a 73,122-sample cohort.
- Discriminator: P7 surfaces the per-axis counts before/after Phase 3.

### H5 (VERY LOW prior, but cheap to exclude) — Per-chrom intermediates are ALSO empty (catastrophe is upstream)
The fan-out `_SUCCESS` markers are lying too; the all-22-traversed impression is wrong.
- AGAINST: E1 (each per-chrom write is guarded by `_assert_checkpoint_nonempty`, which would have raised). 
- Discriminator: P1/P2 (FIRST DIAGNOSTIC PRIORITY) — du-floor + count the intermediates. This is the gate for the entire recovery cost and MUST run first.

---

## RELAYED PROBE BATTERY (Carter runs in the AoU Workbench; ordered)

Constraints honored: gsutil ls/du + `_SUCCESS` mtime + count_rows/count_cols off intermediates only; NO destructive action; the empty final, all 22 intermediates, clean cohorts, and _forensics stay UNTOUCHED. `${B}` below = `gs://rw-migration-aou-rw-476cdac2`. Intermediate path scheme (from `_intermediate_checkpoint_uri`): `${B}/ld/intermediate/mt_afr_pca_selfid_{post_split|post_variant_qc}_chrN.mt`. Final: `${B}/ld/mt_afr_pca_selfid_qc.mt`.

### P1 — FIRST DIAGNOSTIC PRIORITY: du-floor the 22 post_variant_qc intermediates (gates recovery cost)
```
gsutil du -s ${B}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc_chr1.mt/entries/rows/parts/
gsutil du -s ${B}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc_chr11.mt/entries/rows/parts/
gsutil du -s ${B}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc_chr22.mt/entries/rows/parts/
# (optional: loop all 22)
for c in $(seq 1 22); do echo -n "chr$c "; gsutil du -s ${B}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc_chr${c}.mt/entries/rows/parts/ 2>&1 | head -1; done
```
- If each `entries/rows/parts/` is GB-scale (chr1 largest, chr21/22 smallest, all ≫ 1 KB) → **intermediates POPULATED → H5 ELIMINATED; recovery is cheap (re-drive final merge only)**. Proceed to P3.
- If any are 0-byte / stub-only (≤ a few KB) → **H5 LIVE; the fan-out _SUCCESS markers are lying; catastrophe is upstream and worse**. Stop the cheap-recovery assumption; escalate to a full re-fire investigation.

### P2 — Confirm intermediate populated-ness with Hail counts (contents, not du), chr1 + chr22
In the live (Idle) kernel, fresh — `_SUCCESS`/du is necessary but [[feedback_aou_success_marker_not_evidence_of_data]] requires counts:
```
import hail as hl
for c in ("chr1","chr22"):
    mt = hl.read_matrix_table(f"{B}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc_{c}.mt")
    print(c, mt.count_cols(), mt.count_rows())
```
- Expect cols == 63,312 for ALL chroms (Step-4 self-report subset, sample-axis identical across chroms; sample QC NOT yet applied per-chrom), rows = that chrom's post-variant-QC variant count (>0, chrom-scaled).
- If cols == 63,312 and rows > 0 on both → intermediates real, self-report subset correctly carried into every per-chrom MT → **confirms H1/cheap-recovery; ELIMINATES H5 and the self-report-zeroing variant of H2**.
- If cols == 73,122 (== primary) on the intermediates → the per-chrom self-report restriction did NOT apply (contamination recurred) — but the live `74576->63312` print argues against this; flag if seen.
- If cols == 0 or rows == 0 on any → catastrophe upstream (H5).

### P3 — `_SUCCESS` mtime test: did the driver outlive the websocket drop? (H1 vs H2 distinguisher — the free test from [[feedback_w1_catastrophe_hypothesis_distinguisher]])
```
gsutil ls -l ${B}/ld/mt_afr_pca_selfid_qc.mt/_SUCCESS
gsutil ls -l ${B}/ld/intermediate/mt_afr_pca_selfid_post_variant_qc_chr22.mt/_SUCCESS
gsutil ls -lR ${B}/ld/mt_afr_pca_selfid_qc.mt/ | sort -k2   # spread of object mtimes inside the final MT dir
```
- If the final `_SUCCESS` mtime is LATER than chr22's post_vqc `_SUCCESS` (i.e. the union+finalize started and got far enough to write `_SUCCESS`) AND the final MT dir's object mtimes cluster in a narrow window then STOP abruptly (no entries payload objects after the metadata/cols objects) → consistent with **H1: finalize wrote `_SUCCESS`, then the writer was interrupted mid-entries-flush**. 
- If the final `_SUCCESS` mtime roughly coincides with the reported websocket-drop time → the death and the marker are contemporaneous → **H1 strongly favored**.
- If the final `_SUCCESS` mtime is well BEFORE the drop AND the dir is fully skeletal with no entries → suggests the write finalized empty and ran to completion (the compute produced empty) → **shifts weight to H2/H3/H4**; then P7 is decisive.

### P4 — Dataproc job / YARN application final state (did the server-side job survive the browser?)
```
# list recent Dataproc jobs on the cluster (region per cluster), or via YARN RM:
gcloud dataproc jobs list --cluster <CLUSTER> --region <REGION> --limit 10
# or, on the cluster master:
yarn application -list -appStates ALL | tail
yarn application -status <appId>   # for the AFR-sens app
```
- If the YARN application for the AFR-sens fire shows FAILED/KILLED with a finish time at the websocket-drop moment → **the driver did NOT survive → H1 confirmed (server-side job died with the kernel)**, resolving the symptom's "should be browser-independent — unconfirmed" tension toward death.
- If it shows SUCCEEDED/FINISHED cleanly → the server-side job ran to completion and STILL produced empty → **H2/H3/H4** (genuine empty-compute); P7 then identifies which.
- (This directly answers key-question #3.)

### P5 — Final MT shape: count off the empty final (cheap confirmation of `0x0` vs partial)
```
import hail as hl
mt = hl.read_matrix_table(f"{B}/ld/mt_afr_pca_selfid_qc.mt")
print(mt.count_cols(), mt.count_rows())   # may throw if skeleton is unreadable
```
- If it throws/hangs → the skeleton is not Hail-loadable (deeper than empty; consistent with interrupted flush, H1).
- If it returns `0 0` cleanly → a coherent empty MT was finalized (leans H2/H3/H4).
- If it returns `0 N` or `N 0` → an axis-collapse (re-weights toward H4 / a real predicate bug) — but contradicts the 0-byte `rows/`+`cols/` observation, so reconcile carefully.

### P6 — hail.log scrollback: confirm the final-merge phase and locate the cut
On the cluster master / preserved `/tmp/hail.log`:
```
grep -nE "genome-wide [0-9]+/22|wrote intermediate|sensitivity self-report filter applied|wrote final|union" /tmp/hail.log | tail -60
tail -200 /tmp/hail.log
```
- Expect 22× `sensitivity self-report filter applied: 74576 -> 63312` and 22× `wrote intermediate 1/2` pairs (E2/E1), then the union, then NO `wrote final` line.
- If the log ENDS after the union submit / mid-final-checkpoint with no `wrote final` and no traceback → **H1 (interrupted final write) confirmed**; the absence of "wrote final" (printed at 1975, AFTER the guard at 1974) means neither the guard nor the print ran.
- If a traceback IS present (e.g. an assertion or union schema error) that the frontend lost → re-weights to H2/H3/H4 per the traceback class.

### P7 — DECISIVE recovery+discriminator probe: re-drive ONLY the final merge from existing intermediates, in a FRESH kernel
This is BOTH the cleanest H1-vs-H2/H3/H4 discriminator AND the candidate cheap recovery. Run ONLY after P1/P2 confirm intermediates are populated. NON-destructive (writes to a SCRATCH URI, leaves the empty final + intermediates untouched):
```
import hail as hl
from aou_ld_panel import (AUTOSOMES, _intermediate_checkpoint_uri,
                          _apply_sample_qc_and_finalize, MIN_VARIANTS_FOR_SAMPLE_CALLRATE)
B = "rw-migration-aou-rw-476cdac2"
parts = [hl.read_matrix_table(_intermediate_checkpoint_uri(B,"afr","post_variant_qc",True,c)) for c in AUTOSOMES]
mt = parts[0].union_rows(*parts[1:])
print("union:", mt.count_cols(), mt.count_rows())     # expect 63,312 x ~20.5-20.8M
# Phase 3 + final to a SCRATCH path (do NOT overwrite the real final yet):
scratch = f"gs://{B}/ld/_scratch/mt_afr_pca_selfid_qc_REMERGE.mt"
mt = _apply_sample_qc_and_finalize(
    mt, ancestry="afr", sensitivity=True, bucket=None,   # bucket=None => skip write; we write scratch by hand
    sample_callrate_filtered=(mt.count_rows() >= MIN_VARIANTS_FOR_SAMPLE_CALLRATE))
mt = mt.checkpoint(scratch, overwrite=True)
print("final:", mt.count_cols(), mt.count_rows())       # expect ~62,000-62,500 x ~20.5-20.8M
```
- If `union` prints `63,312 x ~20.5-20.8M` and `final` prints `~62-62.5K x ~20.5-20.8M` → **H1 CONFIRMED** (the data was always there; only the original final write was interrupted). The empty `mt_afr_pca_selfid_qc.mt` is a kernel-death artifact. Recovery = promote the scratch (or re-run finalize writing the real URI) — minutes, NOT 15h. ELIMINATES H2/H3/H4/H5.
- If `union` prints `0` rows → **H3 (union quirk) LIVE**; retry with two-level pairwise union (P7b).
- If `union` is populated but `final` collapses an axis (`N x 0` or `0 x N`) → **H4 LIVE** (Phase-3 predicate bug); inspect call_rate/het distributions.
- (`bucket=None` in the helper skips the helper's own final write so we control the scratch URI and never touch the real final.)

### P7b — fallback only if P7 shows a 22-way union quirk
```
import functools
pairs = [parts[i].union_rows(parts[i+1]) for i in range(0,22,2)]   # 11 pairwise
mt = functools.reduce(lambda a,b: a.union_rows(b), pairs)
print(mt.count_cols(), mt.count_rows())
```
- If two-level union is populated while flat 22-way was empty → confirms the Hail-version 22-way `union_rows` quirk flagged in the fan-out debug doc; recovery uses the two-level form.

---

## Recovery Plan (SEPARATE from root cause; no action without Carter)

Recovery is GATED on P1/P2 (intermediates populated) and CONFIRMED by P7.

- **If P1/P2 populated + P7 yields the expected populated final (H1):** recovery is a **final-merge re-drive only** (P7's scratch path, then promote to `${B}/ld/mt_afr_pca_selfid_qc.mt`). Cost = minutes-to-~1h (union is metadata-level; Phase 3 = sample_qc + 2 filters over 63,312 samples; one final checkpoint write). NO 15h re-fan-out. The arbiter is membership + counts, not `_SUCCESS`: final `count_cols ≈ 62-62.5K` (strictly < 63,312 in-scope and < 73,122 primary), `count_rows ≈ 20.5-20.8M`, du-floor GB-scale, `.describe()` shows `self_report`.
- **The CODE FIX for the root cause (H1) is the durable concern, separate from recovering this cohort:** the final-write guard `_assert_checkpoint_nonempty` runs AFTER `mt.checkpoint()` writes `_SUCCESS`, so a death in that window leaves a lying `_SUCCESS`. Cell 4.5's du-floor guard would have CAUGHT this on the next-cell run — but the kernel went Idle before Cell 4 even returned, so Cell 4.5 never fired. Durable hardening (for the orchestrator to plan; NOT executed here): (a) make the final write atomic-or-validated (write to a temp URI, validate populated, then rename/promote — so `_SUCCESS` at the canonical URI implies validated contents); and/or (b) fold the Cell-4.5 du-floor check into `load_qc_cohort` itself as a bucket-state (not in-memory) post-write gate that re-reads `_SUCCESS`+entries from a fresh handle, so an interrupted write cannot leave a canonical `_SUCCESS` that downstream trusts.
- **If P1/P2 show intermediates EMPTY (H5) or P7 reproduces empty (H2/H3/H4):** do NOT promote anything; the catastrophe is upstream / a real logic defect — escalate to a full re-investigation with the new evidence.

---

## ROUND 2 (2026-06-10) — SOURCE-CODE RECOVERY TRACE (post-probe-confirmation)

In-perimeter probes CONFIRMED H1 (driver died in the 1973→1974 window; 22 intermediates
intact, ~1.29 TB, monotonic cadence chr1@04:57→chr22@15:19 GMT; final `_SUCCESS`
@19:52:19 GMT, ~4.5h after chr22, 0-byte entries/rows/cols, no `wrote final` print). This
round answers the recovery-design questions from source, line-grounded.

### Q1 — RECOVERY ENTRY POINT

**Q1(a) — How the 22 intermediates are combined.**
- `src/python/aou_ld_panel.py:1550` — `mt = per_chrom_mts[0].union_rows(*per_chrom_mts[1:])`.
- This is a SINGLE variadic `union_rows(*others)` call (Hail's native multi-way union),
  NOT a Python `functools.reduce`/serial left-fold. `per_chrom_mts` is the list built by
  the fan-out loop at 1527-1543 — each element is the RETURN of a per-chrom recursion
  (`_skip_final_write=True`), i.e. an in-memory MT handle pointing at that chrom's
  `post_variant_qc` checkpoint on disk (the recursion's final action before `return mt` at
  1907-1908 is the `mt.checkpoint(ckpt_post_vqc, ...)` read-through at 1893). So the union
  inputs are disk-backed, identical col-key (sample) sets, identical post-split/variant_qc
  row schema.

**Q1(b) — Does the auto-resume state machine support finalize-only resume?**
PARTIAL — important nuance. There is NO checkpoint of the union or of the final cohort
short of the final URI itself. Resume is PER-CHROM, INSIDE each recursion, NOT at the union:
- The genome-wide branch (1521-1570) is entered whenever `interval_filter is None and not
  skip_checkpoint and not _skip_final_write`. It UNCONDITIONALLY re-runs the fan-out loop
  (1528) → union (1550) → `count_rows` (1558) → `_apply_sample_qc_and_finalize` (1567).
  There is no "is the final already done?" guard at the genome-wide level.
- The RESUME happens one level down, inside each per-chrom `load_qc_cohort(... interval_filter="chrN",
  _skip_final_write=True)` call. With `force_fresh=False`, that recursion hits the resume
  state machine at 1621-1680: `_validate_checkpoint_populated(ckpt_post_vqc)` (1631) →
  (sidecar matches) → `state="RESUME_FROM_POST_VARIANT_QC"` (1642) → at 1848-1850 it does
  `mt = hl.read_matrix_table(ckpt_post_vqc)` and RETURNS at 1907-1908 (`if _skip_final_write:
  return mt`) WITHOUT re-reading RAW or re-running per-chrom QC.
- **Net behavior of a plain `force_fresh=False` re-invocation of Cell 4:** each of the 22
  per-chrom recursions resumes cheaply from its existing `post_variant_qc` checkpoint (a
  metadata read + sidecar-validate, seconds each, NO source re-read, NO per-chrom QC), THEN
  the union + finalize re-drive over the union. This IS effectively a finalize-only resume —
  PROVIDED the 22 sidecars (`*.meta.json`) exist and match current provenance.
  - CAVEAT 1 (sidecar gate): if any per-chrom `post_variant_qc.mt.meta.json` is ABSENT, that
    recursion takes the orphan branch (1633-1638 → `auto_fresh=True`) and RE-RUNS that chrom
    from RAW source (Phase 1+2) — expensive. The clean re-fire wrote each sidecar at 1895-1897
    immediately after the chrom's checkpoint, so they SHOULD all be present; P2/P-new should
    confirm `gsutil ls .../mt_afr_pca_selfid_post_variant_qc_chrN.mt.meta.json` for all 22.
  - CAVEAT 2 (provenance match): the sidecar compare (1640, `_validate_sidecar`) excludes
    timestamp/git-sha/hail-version (717-730), so a same-code re-fire matches. A DIFFERENT git
    SHA does NOT invalidate (git_commit_sha is excluded). Match string / SENS_FILTER_VERSION /
    resolved self_report_path ARE compared — unchanged since the clean fire, so they match.
  - CAVEAT 3 (force_fresh=True would be WRONG for recovery): firing Cell 4 with the original
    `load_qc_cohort(... )` default is `force_fresh=False` — correct. Do NOT pass force_fresh=True:
    that sets `overwrite_flag` (1683) and RE-RUNS all 22 chroms from RAW (another ~15h + cost).
- **THE BLOCKER for using the stock entry point as-is:** `_apply_sample_qc_and_finalize`
  (1567) is called with `bucket=bucket` (resolved at 1564), so it WRITES THE LIVE FINAL URI
  `mt_afr_pca_selfid_qc.mt` at 1972-1973 (`overwrite=True`, hardcoded). The objective forbids
  writing the live path in this round. So the stock genome-wide entry point cannot be used for
  the read-only DRY-RUN — it has no scratch-URI parameter. → Deliver a hand-written cell (Q1d-ii)
  that reuses the SAME helper but redirects the write, OR calls the helper with `bucket=None`
  (which skips the helper's own write, 1971) and checkpoints to scratch by hand.

**Q1(c) — Exact post-union finalize sequence (the stage that must be re-driven).**
From the union at 1550, in order:
1. `1558` — `_n_var_union = mt.count_rows()` (one bounded count over the union).
2. `1559` — `sample_callrate_filtered = _n_var_union >= MIN_VARIANTS_FOR_SAMPLE_CALLRATE`
   (500_000; union ≫ 500K → APPLY).
3. `1564-1566` — resolve `bucket` (errors if WORKSPACE_BUCKET unset).
4. `1567-1569` — `_apply_sample_qc_and_finalize(mt, ancestry, sensitivity=True, bucket, sample_callrate_filtered)`.
   Inside that helper:
   - `1950` — `mt = hl.sample_qc(mt, name="sqc")`.
   - `1951-1952` — IF `sample_callrate_filtered` (True here): `mt = mt.filter_cols(mt.sqc.call_rate >= 0.98)`.
   - `1961` — `het_stats = mt.aggregate_cols(hl.agg.stats(mt.sqc.r_het_hom_var))` (the heavy
     genome-wide `aggregate_cols` collect — see Q2).
   - `1962-1966` — IF `stdev>0`: het ±3SD band `filter_cols`.
   - `1972` — `ckpt = _qc_checkpoint_uri(bucket, "afr", True)` → `…/ld/mt_afr_pca_selfid_qc.mt`.
   - `1973` — `mt = mt.checkpoint(ckpt, overwrite=True)`  ← writes `_SUCCESS`; DRIVER DIED HERE.
   - `1974` — `_assert_checkpoint_nonempty(mt, ckpt, phase="final")`  ← never reached.
   - `1975` — `print("wrote final")`  ← never printed (consistent with probe evidence).

**Q1(d) — DELIVERED RECOVERY APPROACH: hand-written scratch dry-run cell (option ii).**
Rationale for option (ii) over (i): the stock genome-wide entry point has no scratch param and
hardcodes the live URI (1972) + `overwrite=True` (1973); it cannot do a read-only dry-run. The
hand-written cell below reuses `_apply_sample_qc_and_finalize` with `bucket=None` so the helper
SKIPS its own write (guard at 1971 `if bucket is not None`), then checkpoints to a SCRATCH URI
by hand. It reads the 22 intermediates directly (no fan-out, no source re-read), so it is cheap
and touches nothing live. RUN ONLY AFTER P1/P2 confirm the 22 intermediates are populated.

```python
# ── AFR-sens FINALIZE DRY-RUN (read-only; writes SCRATCH only) ──────────────
# Re-drives ONLY the union + Phase-3 finalize from the existing 22 post_variant_qc
# intermediates. Does NOT touch the live mt_afr_pca_selfid_qc.mt. Decisive H1 test
# AND the recovery rehearsal. Fresh kernel; Cell 1a/1a''/1b already run.
import os, hail as hl
from aou_ld_panel import (
    AUTOSOMES, _intermediate_checkpoint_uri, _apply_sample_qc_and_finalize,
    _assert_checkpoint_nonempty, MIN_VARIANTS_FOR_SAMPLE_CALLRATE,
)
BUCKET = os.environ["WORKSPACE_BUCKET"]          # gs://rw-migration-aou-rw-476cdac2

# 1. Read the 22 disjoint per-chrom post_variant_qc intermediates (disk-backed).
parts = [
    hl.read_matrix_table(
        _intermediate_checkpoint_uri(BUCKET, "afr", "post_variant_qc",
                                     True, chrom))      # sensitivity=True
    for chrom in AUTOSOMES
]

# 2. Variant-axis union — the exact 1550 call, variadic (NOT a serial fold).
mt = parts[0].union_rows(*parts[1:])

# 3. Raw-count guard decision exactly as 1558-1559 (union ≫ 500K → APPLY).
n_var_union = mt.count_rows()
sample_callrate_filtered = n_var_union >= MIN_VARIANTS_FOR_SAMPLE_CALLRATE
print(f"union: cols={mt.count_cols()} rows={n_var_union} "
      f"callrate_filter={'APPLY' if sample_callrate_filtered else 'SKIP'}")
# EXPECT cols == 63312, rows ≈ 20.5-20.8M, callrate_filter == APPLY.

# 4. Phase-3 finalize via the SHARED helper with bucket=None => helper SKIPS its
#    own write (1971 guard); we control the scratch checkpoint by hand.
mt = _apply_sample_qc_and_finalize(
    mt, ancestry="afr", sensitivity=True, bucket=None,
    sample_callrate_filtered=sample_callrate_filtered,
)

# 5. Checkpoint to a SCRATCH URI — NEVER the live mt_afr_pca_selfid_qc.mt path.
scratch = f"{BUCKET}/ld/_scratch/mt_afr_pca_selfid_qc_DRYRUN.mt"
mt = mt.checkpoint(scratch, overwrite=True)
_assert_checkpoint_nonempty(mt, scratch, phase="final-dryrun")   # 988-1028 guard
print(f"DRYRUN final: cols={mt.count_cols()} rows={mt.count_rows()}")
print(f"   wrote scratch: {scratch}")
mt.describe()   # confirm self_report col-field present (sens-path provenance)
# EXPECT cols ≈ 62.0-62.5K (< 63312 < 73122), rows ≈ 20.5-20.8M, .describe shows self_report.
```

Interpretation:
- union `63312 × ~20.5-20.8M` AND DRYRUN final `~62-62.5K × ~20.5-20.8M` → **H1 CONFIRMED**;
  data was always intact; only the original live final-write was interrupted. Promote (separate
  green-lit step): re-run finalize writing the LIVE URI, OR `gsutil -m cp -r` scratch → live.
- union `0` rows → H3 (22-way union quirk) LIVE → P7b two-level pairwise union fallback.
- union populated but final collapses an axis → H4 (Phase-3 predicate) → inspect call_rate/het.

### Q2 — FAILURE MECHANISM + DON'T-REPEAT-IT

**Q2(a) — union shape: serial fold or variadic?** VARIADIC, single call (1550,
`union_rows(*per_chrom_mts[1:])`). NOT `functools.reduce`. Hail lowers a variadic
`union_rows` into its own multi-way union IR (not a 21-deep left-nested Python fold), so the
"deep unbalanced lineage from a serial fold" risk does NOT apply here. Lineage depth is the
22 disk-backed `read_matrix_table` leaves under one union node — shallow and balanced.

**Q2(b) — where the OOM/instability risk lives under cores=1/5g.** The union (1550) and
`count_rows` (1558) are metadata/partition-level and cheap. The genome-wide-scale heavy tail
is the TWO `aggregate_cols` collects in `_apply_sample_qc_and_finalize`:
- `1954` (only on the SKIP branch — not taken here) and, taken here, `1961`
  `mt.aggregate_cols(hl.agg.stats(mt.sqc.r_het_hom_var))`. `aggregate_cols` materializes a
  per-sample (63,312-wide) aggregation that walks ALL ~20.8M variants per sample — a driver-
  side collectDArray gather, exactly the GC-heavy tail prior notes flagged for EUR. Plus the
  `1952` `filter_cols(call_rate)` forces `sample_qc` (1950) over the full genome-wide MT.
  This is the single most memory-intensive driver step in the finalize.

**Q2(c) — does recovery need different framing to survive?**
WEIGHING config-OOM vs external-kill:
- AFR-primary (73,122 samples, LARGER than the 63,312 sens cohort) and EUR (220,098 samples,
  MUCH larger) both finalized fine through the IDENTICAL `_apply_sample_qc_and_finalize` path
  under the SAME cores=1/5g/n2-standard-16 config. A deterministic config-OOM at the het
  `aggregate_cols` would have struck the LARGER AFR-primary and EUR cohorts FIRST. It did not.
- The probe evidence is dispositive for external-kill: `_SUCCESS` was WRITTEN
  (@19:52:19 GMT) — i.e. the finalize ran all the way THROUGH sample_qc + call_rate +
  het-aggregate + het-band and reached `mt.checkpoint` (1973), which only writes `_SUCCESS`
  after the driver-side finalize accounting. An OOM during the het `aggregate_cols` would have
  died BEFORE `_SUCCESS`, leaving no final-MT dir at all (the EUR-never-existed W1 signature),
  NOT a `_SUCCESS`-with-0-byte-entries. The observed state (clean `_SUCCESS`, no traceback, no
  `wrote final`, in-memory object gone, kernel Idle) is the websocket/stray-navigation driver
  loss in the 1973→1974 flush window — NOT a compute OOM.
- **VERDICT: external driver-kill (H1), confidence HIGH.** The merge LOGIC is sound (proven by
  AFR-primary + EUR + the 22 self-validated intermediates). No framing change is REQUIRED for
  correctness.

**Q2(d) — recommendation.** Recovery = "re-run the finalize, protect the driver from
disconnect." NO algorithmic framing change needed. The MINIMAL robustness additions (cheap
insurance, not correctness fixes) for the eventual LIVE re-drive:
1. PROTECT THE DRIVER: run the finalize so a browser/websocket drop cannot kill it — submit as
   a detached `gcloud dataproc jobs submit pyspark` (server-side, survives the browser) rather
   than an interactive notebook cell; or keep the tab foregrounded + screen-awake for the
   ~minutes the finalize takes. This is the ONE thing that actually addresses the root cause.
2. OPTIONAL lineage/robustness (only if the dry-run shows a GC-heavy tail): add ONE
   `mt = mt.checkpoint(scratch_union)` immediately AFTER the union (1550) and before the het
   `aggregate_cols`, to cut lineage and make the het stage read from a balanced on-disk union.
   AFR-primary/EUR did not need it, so treat as contingent on observed dry-run behavior, not
   mandatory.
Confidence: HIGH that a protected re-drive of the existing intermediates reproduces a
populated final in minutes; the dry-run cell above is the proof-of-recovery before any live write.

### Q3 — DURABLE FIX (FLAG ONLY — do NOT apply this round)

Root durable concern: the `_SUCCESS`-without-data window between `mt.checkpoint()` (1973,
writes `_SUCCESS`) and `_assert_checkpoint_nonempty` (1974, validates). A driver death in that
window leaves a trusted-but-empty canonical MT. The notebook Cell-4.5 du-floor (second line of
defense) ALSO did not fire because the kernel went Idle before Cell 4 returned. Two candidate
durable fixes, with the file:line where each would land:

- **OPTION A (preferred) — atomic write-then-promote in `_apply_sample_qc_and_finalize`
  (`src/python/aou_ld_panel.py:1971-1975`).** Replace the direct write-to-canonical with:
  write to a TEMP URI (`{ckpt}.tmp` or `…/_staging/…`), run `_assert_checkpoint_nonempty` on
  the TEMP, and ONLY THEN promote (`hl.hadoop_copy`/rename) temp → canonical. Then a canonical
  `_SUCCESS` IMPLIES validated contents — an interrupted write leaves the temp dirty and the
  canonical absent, which the resume state machine already treats as "not done." This closes
  the window for ALL callers (single-interval + genome-wide union) since both funnel through
  this helper. Same pattern should be mirrored on the intermediate writes (1825, 1893) for
  belt-and-suspenders, though those self-validated at write-time here.
- **OPTION B (complementary) — fold the Cell-4.5 bucket-state du-floor INTO
  `_apply_sample_qc_and_finalize` after the write (`1974`+).** After `_assert_checkpoint_nonempty`,
  add a FRESH-HANDLE bucket re-read (`_validate_checkpoint_populated(ckpt)` at 829, which lists
  `entries/rows/parts/` and checks ≥1 file > 1 KB) so the in-code gate checks ON-DISK bytes, not
  just the in-memory count (which can be satisfied from cached partition metadata without a
  bucket read-back). This makes load_qc_cohort itself fail loudly on a stub write even if the
  count is served from cache.

RECOMMENDATION TO ORCHESTRATOR/PLANNING: implement OPTION A (atomic promote) as the primary
durable fix — it structurally eliminates the lying-`_SUCCESS` class, not just detects it — and
add OPTION B's fresh-handle bucket re-read as a cheap secondary gate. Both are NON-trivial code
changes requiring TDD regression tests (stub-write fixture → assert raise) and a chr22 smoke
re-fire to verify the promote path under live Hail; they are OUT OF SCOPE for this
find_root_cause_only round and are flagged here for the planning phase.

### Files inspected (Round 2)
- src/python/aou_ld_panel.py — genome-wide fan-out + union 1521-1570; auto-resume state
  machine 1601-1685; per-chrom Phase 1-2 + sensitivity Step-4 1693-1908; `_skip_final_write`
  return 1907-1908; `_apply_sample_qc_and_finalize` 1919-1977; `_validate_checkpoint_populated`
  829-911; `_assert_checkpoint_nonempty` 952-1028; `_intermediate_checkpoint_uri` 488-526;
  `_qc_checkpoint_uri` 436-456; sidecar compare-exclude 717-730.
- .planning/notebooks/AOU-1_template.ipynb — Cell 3/3.5/4/4.5/5/5.5 (load_qc_cohort invoked
  with default force_fresh=False, no interval_filter, sensitivity=True at Cell 4; Cell 4.5
  du-floor over `_qc_checkpoint_uri(...,'afr',True)/entries/rows/parts/`, 1.0 GB floor).

---

## Answers to the four key code questions

1. **Final-step combine:** genome-wide caller (1550) does `per_chrom_mts[0].union_rows(*per_chrom_mts[1:])` (variant-axis 22-way union of disk-backed post_variant_qc MTs), then `_apply_sample_qc_and_finalize` (1567) runs sample_qc + call_rate + het, then `mt.checkpoint(_qc_checkpoint_uri(...), overwrite=True)` (1973) + `_assert_checkpoint_nonempty` (1974). A 0-row/0-col result could be produced silently ONLY if (a) all inputs empty (excluded by E1), (b) a union quirk (H3), (c) Phase-3 collapses an axis (H4, but that RAISES), or (d) the write is interrupted before flushing entries (H1 — and then the validating guard never runs).
2. **Did the W1 patches land for sensitivity=True?** YES — `_validate_checkpoint_populated` (829), `_assert_checkpoint_nonempty` (952) on EVERY checkpoint incl. final (1974), and the catastrophe-pattern auto-fresh branches (1649-1680) are all present and apply to the sensitivity path (sensitivity is just a flag threaded through; no separate write code). The empty final slipped through NOT because the guard is missing on this path but because the guard is the statement AFTER the `_SUCCESS`-writing checkpoint and the driver died in between (E3/E4). The notebook second-line guard (Cell 4.5) also never fired because the kernel went Idle before Cell 4 returned.
3. **Could the websocket drop kill the driver mid-final-write?** This is the open question P3+P4 resolve. If "Idle" means Cell 4 RETURNED, then `_assert_checkpoint_nonempty` would have run and (on empty) RAISED — contradicting the no-traceback observation; so "Idle" almost certainly means the kernel was RESET (orphaned/killed), not that Cell 4 completed. P4 (YARN app final state) directly tests whether the server-side driver survived; P3 (`_SUCCESS` mtime vs drop time) is the free distinguisher.
4. **Sensitivity-specific branch that could zero rows after per-chrom QC but before final write?** NO. The self-report join (`annotate_cols` + `filter_cols`, Step 4, 1750-1792) happens INSIDE each per-chrom Phase 1, BEFORE the per-chrom checkpoints, and printed a healthy `74576 -> 63312` (E2). There is NO sensitivity-specific code between the union and the final write — `_apply_sample_qc_and_finalize` is sensitivity-agnostic except for the URI suffix (1972). So a key/type mismatch zeroing rows post-QC is not in the code path.

---

## Files Inspected
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/aou_ld_panel.py (genome-wide fan-out 1497-1570; aux/sidecar resolution + auto-resume 1572-1685; Phase 1-2 + Step-4 sensitivity 1693-1908; `_apply_sample_qc_and_finalize` 1919-1977; `_qc_checkpoint_uri` 436-456; `_intermediate_checkpoint_uri` 488-520; `_validate_checkpoint_populated` 829-910; `_assert_checkpoint_nonempty` 952-1027; constants 114-305)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/notebooks/AOU-1_template.ipynb (Cell 3/3.5/4/4.5/5/5.5/7 structure; the du-floor guard cells operate on `entries/rows/parts/` of the final URI)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/debug/m3-W1-empty-mt-catastrophe.md (FULL)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/debug/m3-W2-afr-sensitivity-selfid-noop.md (FULL)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md (FULL)
- git log -- src/python/aou_ld_panel.py (live HEAD includes ab0853a fan-out, 9b86b99 + 06b8a97 self-report fixes)

## Resolution

root_cause: |
  PROXIMATE (HIGH confidence, pending in-perimeter probe confirmation): the AFR-sens
  final MT mt_afr_pca_selfid_qc.mt is empty (_SUCCESS + 0-byte entries/rows/cols)
  because the final union+write step never completed its in-code post-write validation.
  The per-chrom fan-out (Phases 1-2 ×22) and the self-report restriction (74576->63312,
  printed live) demonstrably ran and self-validated. The most-likely mechanism (H1):
  Hail's mt.checkpoint() (aou_ld_panel.py:1973) wrote _SUCCESS via driver-side finalize,
  then the stray-browser-navigation / websocket drop terminated the driver/kernel BEFORE
  the writer flushed entries row-groups AND before _assert_checkpoint_nonempty (line 1974)
  could run its count_rows()/count_cols(). The validating guard exists on this path but is
  the statement AFTER the _SUCCESS-writing checkpoint, so a death in that window leaves a
  lying _SUCCESS with no traceback and the in-memory object gone (E3/E4). Cell 4.5's
  second-line du-floor guard never fired because the kernel went Idle before Cell 4
  returned. The 22 per-chrom intermediates are expected POPULATED (each guarded at write
  time), so recovery should be a cheap re-drive of ONLY the final merge. Competing readings
  H2/H3/H4 (genuine empty-compute at union or Phase 3) are lower prior because a completed
  empty compute would have RAISED at line 1974 (contradicting the no-traceback symptom);
  H5 (intermediates also empty) is very low prior (per-chrom guards). The FIRST DIAGNOSTIC
  PRIORITY probe (du-floor the 22 intermediates) gates recovery cost; P3/P4 (mtime + YARN
  app state) distinguish driver-death from genuine-empty; P7 (re-drive the final merge in a
  fresh kernel to a scratch URI) is the decisive discriminator AND the candidate recovery.

fix: |
  HIGH-LEVEL ONLY (mode = find_root_cause_only; no fix applied). Recovery (gated on
  P1/P2 + confirmed by P7): re-drive ONLY the final union + _apply_sample_qc_and_finalize
  from the existing 22 post_variant_qc intermediates (minutes-to-~1h), NOT another 15h
  fan-out; arbiter = count_cols ~62-62.5K (< 63,312 < 73,122) + count_rows ~20.5-20.8M +
  GB-scale du-floor + .describe() shows self_report; promote to the canonical URI only
  after that passes. Durable code hardening for the H1 class (orchestrator to plan):
  make the final write atomic/validated (write temp URI -> validate populated -> promote)
  so a canonical _SUCCESS implies validated contents, and/or fold the Cell-4.5 bucket-state
  du-floor check into load_qc_cohort so an interrupted final write cannot leave a trusted
  _SUCCESS. NO destructive action; empty final, 22 intermediates, clean cohorts, _forensics
  all untouched until root cause is probe-confirmed.

verification: |
  Not applicable — find_root_cause_only. The relayed probe battery (P1-P7) is the
  verification plan; Carter runs it in-perimeter. P1 gates recovery cost; P7 is decisive.

files_changed: []

---

## ROUND 3 (2026-06-10 evening) — PROBES CONFIRMED H1; DRY-RUN FIRED, RUNNING SERVER-SIDE

**Probe results (Carter, in-perimeter) CONFIRM H1:**
- All 22 `mt_afr_pca_selfid_post_variant_qc_chrN.mt` POPULATED: ~19-117 GB each, ~1.29 TB total, monotonic by chrom size. Per-chrom `_SUCCESS` cadence chr1@04:57 -> chr22@15:19:44 GMT (clean ~20-55 min intervals shrinking with chrom size).
- Final `mt_afr_pca_selfid_qc.mt/_SUCCESS` written **19:52:19 GMT** (~4.5h AFTER chr22) over **0-byte** entries/rows/cols. `_SUCCESS` lands AFTER the full fan-out -> driver reached finalize, then died in the 1973->1974 window. **H1 confirmed; not upstream (intermediates intact), not config-OOM (`_SUCCESS` written = ran through het aggregate).**

**Recovery cell signatures re-verified against source by orchestrator before fire:**
- `_intermediate_checkpoint_uri(bucket, ancestry, phase, sensitivity, interval_filter=None)` :488 — only call-sites :1612 (`post_split`) + :1614 (`post_variant_qc`), both threading `interval_filter`=chrom; the 5th arg IS the chrom-selection mechanism (no separate per-chrom builder). Dry-run uses `interval_filter=chrom` keyword -> reconstructs the verified 22 URIs by construction.
- `_apply_sample_qc_and_finalize(mt, *, ancestry, sensitivity, bucket, sample_callrate_filtered)` :1919 — `bucket=None` hits the write-skip guard :1971 -> compute-but-don't-write. Confirmed.

**DRY-RUN FIRED (read-only; writes ONLY to `_scratch/`):** the Q1(d) cell, fresh kernel (setup 1a/1a''/1b re-run; HARD CONFIRMS `WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2`, `spark.executor.cores=1`, Hail 0.2.135 clean). Scratch target `gs://rw-migration-aou-rw-476cdac2/ld/_scratch/mt_afr_pca_selfid_qc_DRYRUN.mt` (distinct from live, no collision).

**Status at session disconnect (Carter went home, ~evening EST):** RUNNING + advancing server-side on Dataproc app `application_1780788262188_0005`. Discriminator confirmed healthy (NOT a Py4J mutual-wait wedge) via YARN/RM stage deltas: stage 25->26 (868->1054 tasks, 95 active), later stage 47 (3,098->11,469/36,941 tasks ~31%, 94 active) — stage id + completed-tasks both climbing. Still inside the first `count_rows()` over the 36,941-partition union at cores=1; `union:` print (first gate, EXPECT cols=63312) not yet landed. A `[ ]` cell prompt at disconnect = stale canvas-render artifact; the cluster-side task counter is the source of truth.

**Resume:** `.planning/STATE.md` (2026-06-10 EVENING block) + `.planning/HANDOFF.json`. Liveness = Spark stage advancing on `_0005`, NOT the kernel light. Completion = `_scratch/...DRYRUN.mt/entries/rows/parts/` populated + `count_cols`/`count_rows`. PASS -> green-lit promote to live -> Cell 4.5 -> backfill cohort_summary to 3 rows. EMPTY `_scratch` -> failure reproducible/deterministic (bigger finding) -> resume this session.
