# quick-260812-thz — Blast-radius remediation — SUMMARY

**Charter.** Carter, 2026-08-12 21:13 EDT: *"Implement all fixes"* — the fix list
from the five-dimension blast-radius sweep of `76dd7cd..23059f4` (5 read-only
investigators: producer fire-path, manifest consumers, test integrity, record
surfaces, E-2 public texts; verdict: 0 BLOCKER / 0 HIGH / 6 MEDIUM / ~10 LOW).

**Executed fixes.**

1. **CODE (the MEDIUM fire tax):** `src/python/run_native_ld_panel.py` — ONE
   `build_region_records` pass now feeds BOTH the shared and the per-region
   manifest (the shared write goes through `append_region_manifest` directly,
   which is exactly `append_occlusion_rows`' own tail call, so resume-safe dedup
   semantics are unchanged). Removes the third O(n_var × n_deletions) span-filter
   pass the ox1 change had added (~25–100 s per occluded region, ~2–8 h across
   the serial 276-region fire). `src/python/occlusion_manifest.py` —
   `append_occlusion_rows` docstring updated (comment-only): it is no longer the
   driver's call site; kept as the stable public hook. Grep confirmed no test or
   other caller references `append_occlusion_rows`.
   Tests: behavior is pinned by the existing 5 ox1 tests + the module suite —
   `test_run_native_ld_panel.py` 63/63, `test_occlusion_manifest.py` 18/18,
   full `tests/m3` re-run at the end (see below).
2. **HANDOFF.json `wave`** (MEDIUM): evening supersession layer prepended —
   NEXT no longer commands "post osf-correction-v2" (obligation (2) skipped =
   deferred); fire surface = the READY-TO-FIRE runbook. Close body preserved
   verbatim after `||`. Also fixed the destroyed "13:10Z stamp below" referent
   (LOW) in `timestamp_reason_2026_08_12_evening`.
3. **aou-ld-pipeline SKILL.md** (MEDIUM): both gate-surface banners now route
   through the runbook, state PRE-FIRE 1 LANDED (`5284505`), branch (i) live
   default, and "enter through the runbook, never the review directly".
4. **Placement SPEC** (MEDIUM): new **Step 0 — choose the closing sentence
   first** in §3 (the P-1/P-2 fork is now forced by the paste procedure itself);
   plus a §2 note pre-judging the v2 pair's §3-item-3 `git log … -- src/`
   checklist command (now non-empty because of `5284505`+this task — fire-prep
   plumbing, not an E-2 code change).
5. **Runbook item 11-D** (LOW): wrong-tense clause fixed — post-fire the bucket
   holds one manifest per occluded region that PASSED verify; zero-occlusion and
   verify-failed regions have none, by design.
6. **`.continue-here.md` frontmatter** (LOW): `status`/`last_updated` refreshed
   to the evening state.
7. **STATE.md** (LOWs): the pre-change "902/31/0 in 14:49" claim now cites
   banked evidence — verbatim run output at
   `.planning/quick/260812-ox1-…/260812-ox1-prechange-baseline-76dd7cd.txt`
   (was scratchpad-only = belief-only on the record); "Last session:" line
   refreshed (was 2026-08-06).
8. **deferred-items.md** (LOW): dated annotation under the E-2 obligation status
   table — v2 pair names supersede the v1 names in the rows; obligation (2)
   skipped-by-direction = deferred, discharge condition unchanged. Rows
   preserved, not rewritten.
9. **rcw PRE-FIRE review** (LOW + the routing MEDIUM's other half): dated
   in-place status refreshes per its own Corrections-layer precedent — §2 gate
   row + §5 PRE-FIRE 1 banner + §6 row (LANDED, branch (i) default), §4 row 4 +
   §5 PRE-FIRE 3 (index origin settled; manual comparison forbidden) — and two
   new Corrections entries (#12, #13) labeled as STATUS refreshes.

**Deliberately NOT changed, with reasons.**
- The manifest upload's fail-loud semantics (a transient cp failure flips the
  region to `error`): consistent with its `.afreq`/excludelist siblings;
  changing failure semantics on the fire path adds risk for marginal benefit.
- The `is_file()` existence-not-integrity upload gate (LOW corner): the catalog
  re-derives attribution and GATE-1 checks coverage; an integrity pre-check is
  scope creep on the fire path.
- Salvage-path GATE-1 notes (LOWs): salvage-only, pre-existing, and the salvage
  becomes unnecessary now that per-region upload exists.
- The two test-design observations ((a)+(d) literal linkage; (e) shared-code
  oracle): both were judged acceptable by the investigator; no regression class
  unpinned.
- HANDOFF's dated morning-session fields (`verified_this_session_firsthand`,
  `nc_state_cost`): session-history records, corrected on the prescribed
  reading path; layering history was judged noisier than leaving it dated.

**Verification.**
- Paste block re-verified byte-identical post-edit (first-marker-range awk
  extraction, `cmp` clean, 3,429 bytes — the naive two-marker sed picks up §7's
  recorded commands; the block itself is untouched).
- Runbook `grep -c 'gs://$'` = 0 still holds after the 11-D edit.
- HANDOFF parses as JSON after the `wave` layer.
- STATE.md frontmatter (lines 1–24) untouched this task.
- Full `tests/m3` + `tests/phase2` at the post-fix tree: see the suite line in
  the STATE quick-task row (recorded at commit time; skips must be exactly 31/1).

**Commits.** (1) `perf(quick-260812-thz)` — the two src files; (2)
`docs(quick-260812-thz)` — the nine record surfaces + banked baseline + this
SUMMARY; STATE row in the docs commit.
