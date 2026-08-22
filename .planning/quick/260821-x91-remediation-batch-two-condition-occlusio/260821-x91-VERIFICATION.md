---
phase: quick-260821-x91
verified: 2026-08-22T07:15:00Z
status: passed
score: 17/17 must-haves verified
overrides_applied: 0
---

# Quick Task 260821-x91: Remediation batch — two-condition occlusion gate — Verification Report

**Task goal:** Bring the code into line with the POSTED occlusion-gate recalibration amendment
(OSF `mk7ze`): one pinned constants module + enforcer test; producer two-condition gate
(strict `>`, per-region `occlusion_gate.json` sidecar); test-oracle re-derivation (Layer-1
containment, Layer-2 `MEASURED_NOT_DERIVED`); `fire_verifier` two-condition API with a
defaultless `check_manifest_rows` and derived `expected_records`; runbooks updated
(231/232/two-condition) with the vbu enforcer byte-identical; suite re-baselined and
reconciled component-exact; docs + push. Frozen: the amendment (paste block 22,945 B /
`13a49f543cabcc27ce9f1e589783c060`) and `src/python/occlusion_span_filter.py`.

**Verified:** 2026-08-22, re-execution mode (no prior VERIFICATION.md existed).
**Status:** passed
**HEAD:** `b265708` (5 commits ahead of pre-task base `ef59ca1`); `git status -sb` shows no `ahead`.

This is a re-execution verification: every claim below was independently re-derived from the
working tree, not read off the SUMMARY. Where the SUMMARY's numbers are quoted, they were
first reproduced by a fresh command run in this session.

## Goal Achievement

### Observable Truths (17, from PLAN frontmatter `must_haves.truths`)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | The two posted numbers exist in exactly ONE place, pinned by rendered-string identity | ✓ VERIFIED | `src/python/occlusion_gate_constants.py` defines `OCCLUSION_SITE_FRACTION_CEILING = 0.005056` / `OCCLUSION_INFLATION_CEILING = 3.42`; `test_ceilings_render_identically_to_the_posted_slot_ledger` parses the amendment's SLOT_LEDGER and passes (re-ran: 8 passed at commit 4fa2778, and green in the full suite). |
| 2 | The enforcer is evidence, not decoration — seen to FAIL under perturbation | ✓ VERIFIED | Independently reproduced BOTH negative controls in scratch (not in-tree): a scratch constants module perturbed to 0.005057 fails `test_ceilings_render_identically_to_the_posted_slot_ledger` with `assert '0.5057%' == '0.5056%'`; a scratch amendment copy with a one-byte flip (`occlusion`→`occlusiom`) inside the paste block produces md5 `99880ef6858992e9247bf859d8c41486` (≠ anchor) at the same 22,945 B, and `test_amendment_paste_block_is_the_posted_bytes` fails on it. Both match the SUMMARY's claimed transcripts exactly. |
| 3 | The false premise is GONE from code and prose | ✓ VERIFIED | `grep -rn '_OCCLUSION_ANOMALY_FRACTION' src/ tests/` = 0; comment-stripped `run_native_ld_panel.py` contains no `0.0005`; comment-stripped `fire_verifier.py` contains none of `0.0005`/`0.005056`/`0.5056`/`3.42`; `grep -c '5 occluded' src/python/fire_verifier.py` = 0; `grep -c 'known answer (5' src/python/fire_verifier.py` = 0. Read the actual replacement prose at `check_manifest_rows` (:508-517) and `check_region1_status` (:713-724) — both now state the MEASURED 231/196/96,708 semantics, rendered from the accessors, never hand-typed. |
| 4 | No commit in the batch leaves `tests/m3` red (the T2 merge design) | ✓ VERIFIED | Re-ran each commit in an isolated `git archive` extraction (no working-tree mutation): T1 (`4fa2778`) constants file `8 passed`; T2 (`e5e7ac7`) the three merged files `170 passed, 1 skipped`; T3 (`dd8f0b8`) fire_verifier+span_filter `109 passed, 3 skipped`; T4 is docs-only; T5/HEAD full `tests/m3` `1021 passed, 33 skipped, 0 failed`. All match the SUMMARY's claimed per-commit counts exactly, independently re-derived. |
| 5 | The shipped gate is the POSTED two-condition gate, both routes, strict `>`, one status prefix | ✓ VERIFIED | Read `run_native_ld_panel.py:879-967`: `fired` list built from `site_fraction > site_ceiling` and `inflation > inflation_ceiling` (strict), single `deferred_occlusion_anomaly:` prefix for both routes. Confirmed by the 5 gate tests in `test_run_native_ld_panel.py` (site-fraction-only fire, inflation-only fire with site fraction under, both-under proceeds, both boundary-strict-greater tests) — all present and passing in the full run. |
| 6 | Accounting stays ROW-keyed; `_PANEL_COLUMNS` byte-unchanged | ✓ VERIFIED | In-process probe: `rnlp._PANEL_COLUMNS == ['region_id','chr','n_var','wall_min','peak_ram_gib','output_gib','status','n_dropped_occluded','n_dropped_monomorphic']` (9 cols, `n_dropped_occluded` a row count, `n_dropped_monomorphic` last). |
| 7 | Every square-path region banks the `occlusion_gate.json` sidecar with the 11 keys, independently recomputed | ✓ VERIFIED | Read the sidecar-write block (`run_native_ld_panel.py:923-939`): all 11 keys present (`region_id, n_rows, n_sites, occ_rows, occ_sites, site_fraction, inflation, site_fraction_ceiling, inflation_ceiling, fired, verdict`); `test_occlusion_gate_sidecar_numbers_are_independently_recomputed` does a second, independent set-arithmetic computation over the fixture `.bim`; `_reclaim_region_scratch`'s `_keep_names` includes `f"{region_id}.occlusion_gate.json"` (line 748-749). |
| 8 | The deferral route ships its own evidence — a deliberate CONTRACT CHANGE | ✓ VERIFIED | `test_occlusion_gate_deferred_region_ships_only_its_sidecar` and `test_occlusion_gate_site_fraction_fires` assert an EXACT one-object allow-list (`r1 == [f"{gs_out}/m2_region_00001.occlusion_gate.json"]`) plus explicit negatives for `.npz`/`.afreq`/`.occluded.excludelist`/`.occlusion_manifest.tsv`; both pass in the full run. `verify_failed` path is untouched (separately pinned test). |
| 9 | The region-1 oracle no longer claims more than measured (containment, not equality) | ✓ VERIFIED | Read `tests/m3/test_occlusion_span_filter.py:536-593`: both gated assertions use containment (`missing = SETTLED - got_row_indices; assert not missing` and the explicit per-key Counter form, chosen over `Counter.__le__` for Python-3.9 safety, with the equivalence stated in a comment); `_REGION1_NAN_PAIRS_SAME_POSITION_COUNT` re-scoped and never asserted window-wide; `test_containment_assertions_discriminate_a_wrong_answer` proves containment is not vacuous. |
| 10 | Measured substrate totals pinned loudly in a separate `MEASURED_NOT_DERIVED` test | ✓ VERIFIED | `test_region1_real_window_substrate_totals_MEASURED_NOT_DERIVED` (name AND docstring carry the label) pins `n_rows=102421, n_deletion_rows=7951, n_occluded_rows=231, max_span=170, n_sites=96708, occ_sites=196` with the stated provenance and the "RE-MEASURE AND RECORD, never edit-to-green" rule; skips outside the perimeter (confirmed: this is exactly one of the 33 skips observed). |
| 11 | `fire_verifier` reproduces the shipped comparison (evaluation-time accessors, fail-closed) | ✓ VERIFIED | In-process probe confirms `check_occlusion_gate` fails closed on any `None` in `occ_rows`/`occ_sites`/`n_sites` and distinguishes measured-zero (`occ_rows=0` → PASS) from missing (`occ_rows=None` → FAIL); `_default_site_fraction_ceiling()`/`_default_inflation_ceiling()` read `rnlp._OCCLUSION_SITE_FRACTION_CEILING`/`rnlp._OCCLUSION_INFLATION_CEILING` at call time (`test_producer_ceilings_come_from_the_one_pinned_constants_module` passes); `check_manifest_rows` has no default for `expected_records` (confirmed via `inspect.signature`). |
| 12 | Stage A derives `expected_records` from the excludelist and cross-checks the sidecar | ✓ VERIFIED | Read `derive_expected_records` (fire_verifier.py:595-635) and `_stage_a` (1012-1071): line-count derivation, cross-check against sidecar `occ_rows`, mismatch → FAIL with `"CROSS-CHECK FAILED"` detail; `--gate-json` and `--excludelist` are `required=True`; `--expected-records` defaults to `None` and is logged as an override (`test_cli_stage_a_expected_records_override_is_logged_as_an_override` passes). |
| 13 | Runbooks tell the truth region 1 will produce | ✓ VERIFIED | `grep -rn 'near 5\|exactly 5\|10x under\|10× under\|51\.2\|0\.0005' <3 files>` = 0; forbidden phrases `nothing scientific is lost`/`nothing is lost` = 0 across the whole `260812-ox1` directory; `231`, `occlusion_gate.json`, `0.5056`, `3.42`, `232`, `0.2027`, `1.18x` all present in the expected files. |
| 14 | The frozen §6b adjudication card was not disturbed | ✓ VERIFIED | Re-ran `260817-vbu-verify.sh all` fresh in this session (exit 0, `RESULT: ALL CHECKS PASSED`), captured with the exact plan-specified format (`> file 2>&1; echo "exit=$?" >> file`) → 26 lines, md5 `9063cdea0e92bbe22ea148649cc14b17` — matches the SUMMARY's recorded pre-task md5 byte for byte, independently reproduced (not copied from the SUMMARY). |
| 15 | The suite is re-baselined honestly, reconciled component-exact | ✓ VERIFIED | Fresh `pytest tests/m3 -q -rs` run: `1021 passed, 33 skipped, 0 failed in 801.34s`. Independently reconstructed the added/removed test-name reconciliation via `git archive ef59ca1` + `--collect-only` diff (not read from the SUMMARY): exactly the same 8 removed node-ids and the same 38 added node-ids the SUMMARY lists, arithmetic `167 - 8 + 38 = 197` on the 3-file subset closes exactly. `HANDOFF.json` `suite_baselines["tests/m3"]` carries the corrected 1021/33/0 numbers and states the prior stale value (914/31) explicitly. |
| 16 | Nothing public moved and nothing fired | ✓ VERIFIED | `awk` extraction of the amendment paste block = 22,945 B / md5 `13a49f543cabcc27ce9f1e589783c060`; `git diff --stat ef59ca1 HEAD -- src/python/occlusion_span_filter.py .planning/amendments/` is empty. No OSF/AoU/VM/Dataproc/gsutil command was executed by this verification, and none is referenced as executed in the SUMMARY beyond the documented mock-based tests. |
| 17 | The branch is published, explicit-path commits only | ✓ VERIFIED | `git status -sb` → `## m3-W2-aou-deltas...origin/m3-W2-aou-deltas` (no `ahead`); `git diff --stat ef59ca1 HEAD --name-only` lists exactly the 15 files in the PLAN's `files_modified:` list, no more, no less; each of the 5 commits (`git show --stat`) touches only files consistent with its task scope. |

**Score:** 17/17 truths verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/python/occlusion_gate_constants.py` | THE one pinned place, ≥30 lines, contains `OCCLUSION_SITE_FRACTION_CEILING` | ✓ VERIFIED | 66 lines; exactly two module constants + provenance docstring; zero imports; enforcer test passes. |
| `tests/m3/test_occlusion_gate_constants.py` | Enforcer, ≥60 lines, contains the paste-block md5 | ✓ VERIFIED | 268 lines; identity test + public-record pin + 2 negative-control tests + 2 banned-literal scans; all pass; both controls independently re-confirmed RED under perturbation. |
| `src/python/run_native_ld_panel.py` | Two-condition gate + sidecar; `_OCCLUSION_ANOMALY_FRACTION` gone | ✓ VERIFIED | Imports the two constants (lines 101-104), binds module globals (160-161), computes `fired` via strict `>` on both conditions (905-909), writes the sidecar unconditionally before any branch (923-939), uploads it on both the deferred path (961-965) and the `ok` path (1134-1139), keeps it in `_reclaim_region_scratch` (748-749). |
| `src/python/fire_verifier.py` | `check_occlusion_gate` + evaluation-time accessors + defaultless `check_manifest_rows` + Stage A deriving `expected_records` | ✓ VERIFIED | All present and behaviorally probed directly (fail-closed, measured-zero-vs-missing, no default). |
| `tests/m3/test_occlusion_span_filter.py` | Layer 1 (DERIVED, containment) / Layer 2 (MEASURED_NOT_DERIVED) | ✓ VERIFIED | Both layers present, physically separated, correct skip behavior confirmed in the live run. |
| `.planning/quick/260812-ox1-.../260812-ox1-AGENT-PROMPT.md` | 231 / 232 / sidecar EXPECT / two-condition clause (d) | ✓ VERIFIED | `231` (8 hits), `occlusion_gate.json` (5 hits) present; forbidden phrases absent. |
| `.planning/HANDOFF.json` | `resume_on_reconnect[0]` = Stage A from STEP 7 + corrected `suite_baselines` | ✓ VERIFIED | Valid JSON; `resume_on_reconnect[0]` ends with the exact "NEXT = STAGE A ... CARTER starts the VM and CARTER fires; AN AGENT NEVER FIRES" sequence; `suite_baselines["tests/m3"]` reads 1021/33/0 reconciled, states the prior stale 914/31 explicitly. |

All artifacts pass Levels 1-3 (exist, substantive, wired). Level-4 data-flow trace is not
separately applicable here — this is a backend gate/pipeline change with no rendering layer;
the equivalent check (does the sidecar's data actually originate from a real computation
rather than a static/empty stub) was performed via the independent-recomputation test and the
in-process probes above, and both confirm real computed values (not hardcoded/empty).

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| Amendment SLOT_LEDGER | `occlusion_gate_constants.py` | Rendered-string identity test | ✓ WIRED | `test_ceilings_render_identically_to_the_posted_slot_ledger` parses live and passes. |
| `occlusion_gate_constants.py` | `run_native_ld_panel.py` module globals | Module-level import, evaluation-time read | ✓ WIRED | Confirmed via source read + `test_producer_ceilings_come_from_the_one_pinned_constants_module`. |
| `run_native_ld_panel.py` globals | `fire_verifier.check_occlusion_gate` | `_default_*_ceiling()` accessors reading `rnlp.*` at call time | ✓ WIRED | Confirmed by source read and direct in-process probe. |
| `{out_prefix}.occlusion_gate.json` | `fire_verifier._stage_a` | `--gate-json` + `--excludelist` cross-check | ✓ WIRED | Confirmed by source read of `_stage_a`/`derive_expected_records`, and by `test_RED_cli_stage_a_excludelist_sidecar_mismatch_fails_closed` passing in the full run. |
| Posted clause (d) | `260812-ox1-*.md` runbooks | Rewritten clause-(d) paragraph | ✓ WIRED | Grep confirms `0.5056`/`3.42`/`0.2027`/`1.18x` present in all three files; vbu byte-identity confirms the edits stayed outside the frozen card. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full `tests/m3` suite is green | `pytest tests/m3 -q -rs` | `1021 passed, 33 skipped, 0 failed in 801.34s` | ✓ PASS |
| T1 commit alone is green | `git archive 4fa2778` + pytest on constants file | `8 passed` | ✓ PASS |
| T2 merge commit alone is green | `git archive e5e7ac7` + pytest on 3 merged files | `170 passed, 1 skipped` | ✓ PASS |
| T3 commit alone is green | `git archive dd8f0b8` + pytest on fire_verifier+span_filter | `109 passed, 3 skipped` | ✓ PASS |
| Negative control 1 (perturbed constant) | scratch copy, `0.005056`→`0.005057` | `1 failed` (identity test) | ✓ PASS (discriminates) |
| Negative control 2 (one-byte flip) | scratch copy amendment, `occlusion`→`occlusiom` | `1 failed` (md5 pin test) | ✓ PASS (discriminates) |
| `check_occlusion_gate` fail-closed | in-process probe, `None` in each of 3 inputs | 3/3 FAIL as expected | ✓ PASS |
| `check_occlusion_gate` measured-zero ≠ missing | in-process probe | `occ_rows=0` → PASS; `occ_rows=None` → FAIL | ✓ PASS |
| §6b card byte-identical | `260817-vbu-verify.sh all` (exact capture format) | 26 lines, md5 `9063cdea0e92bbe22ea148649cc14b17` | ✓ PASS (matches SUMMARY) |
| Collect-only reconciliation | `git archive ef59ca1` + `--collect-only` diff vs HEAD | 8 removed / 38 added, names match SUMMARY exactly | ✓ PASS |

### Requirements Coverage

| Requirement | Source | Status | Evidence |
|---|---|---|---|
| `DEC-2026-08-22-occlusion-recalibration-posted` | PLAN frontmatter | ✓ SATISFIED | Confirmed banked in `.planning/DECISIONS.md:2304`; the code change this task makes is exactly the two-condition gate the decision authorizes. |
| `OCC-GATE-CONSTANTS-PINNED` | PLAN frontmatter | ✓ SATISFIED | Truth #1. |
| `OCC-GATE-TWO-CONDITION-PRODUCER` | PLAN frontmatter | ✓ SATISFIED | Truths #5, #6. |
| `OCC-GATE-SIDECAR-EVIDENCE` | PLAN frontmatter | ✓ SATISFIED | Truths #7, #8. |
| `OCC-ORACLE-RE-DERIVATION` | PLAN frontmatter | ✓ SATISFIED | Truths #9, #10. |
| `OCC-FIRE-VERIFIER-TWO-CONDITION` | PLAN frontmatter | ✓ SATISFIED | Truths #11, #12. |
| `OCC-RUNBOOK-231-TRUTH` | PLAN frontmatter | ✓ SATISFIED | Truth #13. |
| `OCC-SUITE-REBASELINE` | PLAN frontmatter | ✓ SATISFIED | Truth #15. |

Note: these are quick-task-local requirement labels tracked against `.planning/DECISIONS.md`,
not entries in the milestone `.planning/REQUIREMENTS.md` (which is a phase-roadmap artifact
last touched 2026-04-28, unrelated to this quick task). No orphaned requirements found for
this task directory.

### Anti-Patterns Found

None. Scanned all three new/modified `src/python` files for TODO/FIXME/placeholder/"coming
soon"/"not yet implemented" markers: zero hits. No stub returns, no hardcoded empty
collections masquerading as computed values — the sidecar's six numeric fields are computed
from `raw_rows`/`occluded_ids` at runtime in every code path, and a dedicated test
independently re-derives them from the fixture `.bim` to guard against a right-shape/
wrong-content defect.

### Human Verification Required

None. This task is fully code/test/doc-level (constants module, producer gate, verifier CLI,
oracle tests, runbook prose, JSON/markdown docs) with no UI, no visual rendering, and no
external-service integration exercised. Every claim was mechanically checkable, and every
mechanical check in this report was independently re-executed rather than trusted from the
SUMMARY.

### Gaps Summary

None. All 17 must-have truths verified, all required artifacts present and substantive, all
key links wired, the full `tests/m3` suite re-run fresh (1021 passed / 33 skipped / 0 failed,
matching the reconciled baseline), both negative controls independently reproduced RED, the
frozen §6b card independently reproduced byte-identical, all 5 commits spot-checked green in
isolation, and the branch confirmed pushed with the exact file set the plan authorized.

---

_Verified: 2026-08-22T07:15:00Z_
_Verifier: Claude (gsd-verifier)_
