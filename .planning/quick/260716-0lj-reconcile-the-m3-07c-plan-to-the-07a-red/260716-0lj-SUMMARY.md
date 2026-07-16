---
quick_id: 260716-0lj
phase: 260716-0lj
plan: 01
subsystem: planning-docs
type: execute
mode: quick
tags: [docs, m3, occlusion, present-rate, lockstep, plan-reconciliation, red-is-the-contract]
requires: ["tests/m3/test_occlusion_present_rate_scan.py", "tests/m3/test_occlusion_lockstep_drop.py", "src/python/occlusion_manifest.py"]
provides: ["m3-07c PLAN reconciled to the 07a RED contract (T3 + T4) + the 63bdb59 seam"]
affects: [".planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-PLAN.md"]
tech-stack:
  added: []
  patterns: ["tests-are-the-contract (fix the PLAN, never the RED)", "reconciliation note as a placement-sensitive cut marker"]
key-files:
  created:
    - .planning/quick/260716-0lj-reconcile-the-m3-07c-plan-to-the-07a-red/260716-0lj-SUMMARY.md
  modified:
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-PLAN.md
decisions:
  - "T4 reconciled in this pass, NOT deferred — no T4 OPEN flag."
  - "The reconciliation note quotes the old drifted names deliberately; the ban is scoped to the SPEC BODY via the single-occurrence cut marker."
metrics:
  duration: ~25 min
  completed: 2026-07-16
  tasks: 1
  files: 1
base_commit: 13a2e6c
commit: 8d4087a
---

# Quick 260716-0lj: Reconcile the m3-07c Plan to the 07a RED Summary

DOCS-ONLY reconciliation of the m3-07c PLAN to its governing 07a REDs — **10 drift sites across both
tasks fixed (T3=6, T4=4, both wider than predicted)**, the 63bdb59 `present_rate=` seam recorded, and the
handoff's "07c's plan has no drift" claim retired as STALE AND WRONG for BOTH tasks. **Code and tests
byte-untouched; m3-07c NOT started.**

**Commit:** `8d4087a` — 1 file changed, 183 insertions(+), 20 deletions(-)

## What Was Done

The handoff claimed 07c's plan had been checked for the drift that hit 07b's plan and "has none."
**That claim was wrong for BOTH tasks.** An executor handed the unreconciled plan would have faced an
unsatisfiable spec whose likeliest escape is **editing the REDs** — the exact failure mode
[[feedback_check_plan_against_red_before_executing]] exists to prevent. Precedent `f3b79fe` did this
same pre-execution reconciliation for 07b.

**Rule applied throughout (settled by 07b, not re-litigated): TESTS ARE THE CONTRACT — fix the PLAN,
never the RED.**

### T3 drift table — ALL FIXED (6 sites: `:20, :27, :96, :117, :129, :142`)

Contract: `tests/m3/test_occlusion_present_rate_scan.py`. The plan was **self-contradictory** — `:96`
already used the RED's real column names while `:117` spec'd a return shape appearing nowhere in the RED.

| concern         | plan said (WRONG)           | RED requires (now spec'd)  | status |
|-----------------|-----------------------------|----------------------------|--------|
| function name   | `present_rate_for_variants` | `scan_present_rate` (:79)  | FIXED  |
| numerator key   | `present_count`             | `n_traits_present` (:82)   | FIXED  |
| denominator key | `scanned_count`             | `n_traits_scanned` (:83)   | FIXED  |
| trait-list key  | `files_present`             | `traits_present` (:132)    | FIXED  |

Additionally made explicit (was absent, and load-bearing): the return is **keyed by the
`(chr:int, pos:int)` GRCh37 TUPLE** — `target = (1, 5_982_778)`; `res[target]` (:72, :81).

**6 sites, not the 4 predicted.**

### T4 drift table — ALL FIXED (4 sites: `:21, :156, :158, :160`)

Contract: `tests/m3/test_occlusion_lockstep_drop.py`. **The NAME matched — nothing else did.**

| concern   | plan said (WRONG)                         | RED requires (now spec'd)                        | status |
|-----------|-------------------------------------------|--------------------------------------------------|--------|
| params    | `(sumstats_df, manifest, build='GRCh37')` | `(sumstats_path, manifest_path, out_path)` (:10) | FIXED  |
| shape     | DataFrame-in / tuple-out                  | **FILE-IN / FILE-OUT** — writes `out_path` (:104)| FIXED  |
| return    | `(filtered_df, drop_log)`                 | dict `n_in`/`n_dropped`/`n_out` (:243-247)       | FIXED  |
| logging   | `drop_log` records each drop              | **STDERR** — `capsys.readouterr().err` (:223)    | FIXED  |
| `build=`  | `build='GRCh37'` kwarg                    | **no such kwarg exists** (0 occurrences)         | FIXED  |

**4 sites, not the 2 predicted.** Two corrections went **beyond the rename** — the RED is *stronger* than
the old prose, so paraphrasing would have lost real contract:

* **Idempotence** was "a second application is a no-op (`drop_log` empty)". The RED re-runs the filter
  **on its own OUTPUT** (`drop_occluded_from_sumstats(out1, mf, out2)`, :197), requiring `n_dropped == 0`
  (:200) AND `out2.read_bytes() == out1.read_bytes()` (:201). **The output must be re-readable AS INPUT.**
* **The manifest is a FILE** (TSV: `region_id, variant_id, chr, pos_grch37`; only `(chr, pos_grch37)`
  load-bearing) — which is what makes the whole signature file-in/file-out.

Also encoded as RED facts: chr-aware key (:112-124), `n_dropped == 0` is a valid no-op not an error
(:127-139), byte-identical survivors + no SNP_ID re-key (:160-179), and the producer→consumer seam test
(:272-319) that runs the REAL 07b producer end-to-end.

**T4 is RECONCILED, not deferred — no `T4 OPEN` flag.**

### The 63bdb59 seam paragraph added

Added to `<interfaces>`: `enrich_occlusion_manifest(manifest_path, chain_path, *, out_path=None,
present_rate=None)` consumes EXACTLY `{(chr, pos_grch37): {...}}`, joins **POST-lift** on
`(chr, pos_grch37)` (**not** `variant_id`), and **raises ValueError** if liftable keys exist but none
match. `STAGE_B_TRAIT_COLUMNS` == the RED's key names. The 4 seam tests 63bdb59 added are cited.
=> **`scan_present_rate`'s return is DIRECTLY FEEDABLE to `present_rate=` — no adapter**, and the raise
boundary need not be rediscovered during integration.

Direction of travel recorded explicitly: the plan's `:95-96` **already** correctly assumed
`(chr, pos_grch37)`; 63bdb59 aligned the shipped consumer to it. **The plan's premise is now TRUE in
code, not aspirational.**

## Verification

**Gate result: ALL PASS.** The plan's verify block was run verbatim — 14/14 foreground gates green.

| Gate | Result |
|------|--------|
| `plan_vs_red_reconciliation` marker occurs EXACTLY ONCE (the cut marker) | PASS |
| T3 drifted names == 0 in SPEC BODY (`present_rate_for_variants`/`present_count`/`scanned_count`/`files_present`) | PASS |
| T4 drifted names == 0 in SPEC BODY (`sumstats_df`/`filtered_df`/`drop_log`/`build=`) | PASS |
| `scan_present_rate` >= 6 | PASS (**10**) |
| T3 keys + `(chr,pos)` tuple key `5_982_778` stated | PASS |
| T4 signature `sumstats_path, manifest_path, out_path` | PASS |
| T4 counts dict `n_in`/`n_dropped`/`n_out` | PASS |
| `file-in` called out explicitly; `stderr` recorded | PASS |
| `enrich_occlusion_manifest` + `63bdb59` recorded | PASS |
| `STALE AND WRONG` recorded; `T4 OPEN` == 0 | PASS |
| **CODE GATE (hard):** `git diff --stat 13a2e6c..HEAD -- src/ tests/` EMPTY | **PASS (post-commit)** |

**The gate caught one real incomplete-fix during execution:** my own spec-body prose wrote the literal
token `` `build=` `` while asserting the kwarg does not exist. The ban is on the *token*, so the gate
flagged it — rephrased to `` `build` `` (the note below the marker quotes `build=` freely, which is its
purpose). This is precisely the "flags surviving `build=` sites" behavior the planner's dry-run predicted.

### RED stays RED — 15, stated BY FILE and BY MODULE

| File | Failures | Reason |
|------|----------|--------|
| `tests/m3/test_occlusion_present_rate_scan.py` | **6 failed** | `ModuleNotFoundError: No module named 'occlusion_present_rate_scan'` (T3) — 6/6 |
| `tests/m3/test_occlusion_lockstep_drop.py` | **9 failed** | `ModuleNotFoundError: No module named 'drop_occluded_from_sumstats'` (T4) — 9/9 |
| **Total** | **15** | RED-for-the-right-reason |

Both 07c modules confirmed **non-existent** on disk — `src/python/occlusion_present_rate_scan.py` and
`src/python/drop_occluded_from_sumstats.py` do not exist. **m3-07c is NOT started.**

### Full regression — UNCHANGED

```
15 failed, 405 passed, 31 skipped in 386.38s (0:06:26)
```

Byte-for-byte the baseline at HEAD `13a2e6c` (**15 / 405 / 31**). Docs-only cannot move this, and it did not.

### Bidirectional cross-check (beyond the plan's gate)

Programmatically verified that **every** identifier the reconciled spec body names actually exists in the
RED (15/15 OK: `scan_present_rate`, `n_traits_present`, `n_traits_scanned`, `traits_present`,
`present_rate`, `5_982_778`, `drop_occluded_from_sumstats`, `sumstats_path`, `manifest_path`, `out_path`,
`n_in`, `n_dropped`, `n_out`, `pos_grch37`, `capsys`) — and that all 8 drifted names are 0-occurrence in
**both** the RED and the spec body. Frontmatter YAML re-parsed clean (`exports: [scan_present_rate]`).

## Deviations from Plan

None — plan executed exactly as written. The `build=` self-catch (above) was the plan's own gate working
as designed, not a deviation.

## Standing Note for the Next Reader

**The handoff's "07c's plan was CHECKED for drift — it has none" claim was STALE AND WRONG for BOTH
tasks.** Do not trust it again; the in-plan `plan_vs_red_reconciliation` note supersedes it.

**HOW T4 SLIPPED THROUGH: the check was NAME-ONLY.** `drop_occluded_from_sumstats` — the function name —
matched the RED exactly, so a name-grep passed it clean, while its signature, return, logging mechanism,
and a phantom `build=` kwarg all contradicted the RED. **A name-only check cannot see shape drift.**
Generalizable rule: **grep the NAME, then read the ASSERTIONS.**

## Scope Discipline

- Science/scope **unchanged**: T3 = present-rate scan over the 9 public GRCh37 AFR harmonized sumstats
  (CHR/POS auto-detected BY NAME); T4 = reusable lockstep (CHR,POS) drop-only filter; m3-04 consume-wiring
  stays a **DISCLOSED deferral** (`finemap.smk` m3-04-W4 STALE/SUPERSEDED-PENDING-REPLAN). Tasks not
  renumbered; `threat_model` untouched.
- REQ-PUBLIC-DATA-ONLY honored — no perimeter access, no spend, no loop contact. m3-06 stays HELD.
- Commit used **explicit paths** (never `git add -A`/`.` on this shared GPFS tree,
  [[feedback_multi_terminal_staging]]). Exactly 1 file staged. The 3 pre-existing dirty files
  (`.claude/settings.json`, `260625-r6m-SUMMARY.md`, `tests/m3/sparse_parent_benchmark.tsv`) confirmed
  **not staged** and left dirty.
- No push (orchestrator's job). No GPFS object-store loss encountered.

## Next Step

**m3-07c awaits Carter's explicit GO.** The plan is now executable-as-written for both tasks: every name
it specs exists in the RED, and every name/shape the RED requires is what the plan specs.

## Self-Check: PASSED

- `.planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-PLAN.md` — FOUND (modified, committed)
- `.planning/quick/260716-0lj-reconcile-the-m3-07c-plan-to-the-07a-red/260716-0lj-SUMMARY.md` — FOUND
- Commit `8d4087a` — FOUND on `m3-W2-aou-deltas`
- `git diff --stat 13a2e6c..HEAD -- src/ tests/` — EMPTY (verified post-commit)
</content>
