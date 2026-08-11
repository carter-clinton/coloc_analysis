---
phase: quick/260811-pmv
verified: 2026-08-11T23:39:26Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
---

# Quick Task: SR4-OPEN evidence dossier Verification Report

**Task Goal:** Assemble a per-file evidence dossier (commit history since
`bf16289` with provenance, freeze-declaration search, current gating status,
reproduced diffstats) + derived disposition per file, culminating in a
Carter's-decision block. Investigation-only — the SR4-OPEN disposition itself
is NOT recorded; that is a deliberate design property, not a gap.

**Verified:** 2026-08-11T23:39:26Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (from PLAN.md `must_haves.truths`)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Carter can open ONE file (DOSSIER.md) and see, per file: diff vs bf16289, every commit, provenance, freeze-declaration status, gating status, recommendation | VERIFIED | DOSSIER.md §4 has one `###` section per F1–F5, each with drift/commits/provenance/declaration/gated/recommendation subsections (lines 141–338 confirmed present) |
| 2 | Every count/diffstat/commit-total names the producing command, verbatim output in EVIDENCE.md | VERIFIED | Spot-reproduced 5/5 file diffstats + 3/3 control diffstats + DECISIONS.md grep (all 5 = 0) exactly match DOSSIER/TSV values (see below) |
| 3 | Today's diffstats re-measured at HEAD, reported alongside sr4-era numbers, explicit "differ?" statement | VERIFIED | evidence.tsv `moved_since_sr4` column = `no` for all 5; DOSSIER §2/§4 states "identical to sr4-era" explicitly |
| 4 | Every commit traced to a named planning artifact naming its SHA, or flagged UNTRACEABLE; any untraceable forces DRIFT-NEEDS-REVIEW | VERIFIED | Reproduced 2/2 spot-checked SHAs (`3bb8783` in `260804-rtc-SUMMARY.md:63`, `64f420a` in `260805-o7o-VERIFICATION.md:17` and `260805-o7o-SUMMARY.md:67`); DOSSIER claims 8/8 traceable, 0 untraceable, all TSV rows `all_traceable=yes` |
| 5 | Per file, states whether freeze declaration exists in DECISIONS.md (citing entry) or only in narrative (citing earliest READABLE commit) | VERIFIED | DECISIONS.md grep independently re-run for all 5 basenames = 0 hits each, matching TSV `decisions_declaration` = "none - grep -c = 0"; narrative trail present in DOSSIER §4 with cited SHAs |
| 6 | Missing git objects reported as a census (counts + SHAs), never silently skipped; first-appearance claims scoped as LOWER BOUND | VERIFIED | Independently re-ran the presence-checked per-revision loop for all 3 narrative files; counts reproduced EXACTLY: HANDOFF.json 59/76, STATE.md 275/304, continue-here.md 42/64 |
| 7 | Explicit "Carter's decision" block with operational implications + costed gate-extension recommendation | VERIFIED | DOSSIER §6 (lines 413–508) present, non-directive, costs per file itemized (RECORDED decision required, `#:` bucket annotation, negative control, named test that goes RED, missing YAML stripper for F5) |
| 8 | Dossier states its own scope honestly: git-history + declaration evidence, NOT a code-correctness review | VERIFIED | DOSSIER §0 (lines 13–38) states this verbatim; §7 LIMITS restates it |
| 9 | Nothing outside the quick directory is written; zero modified tracked files | VERIFIED | `git diff 7d575a5 HEAD -- .planning/DECISIONS.md/.planning/HANDOFF.json` and `git diff 5f2028e HEAD -- .planning/STATE.md` all empty; `git status --porcelain \| grep -v '^??'` empty; all 3 commits (`f78bbc1`,`399c50f`,`2b13dce`) touch only paths under the quick dir (`git show --stat`) |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `260811-pmv-EVIDENCE.md` | Raw verbatim command log, contains "OBJECT-STORE CENSUS", ≥120 lines | VERIFIED | 2,419 lines; `OBJECT-STORE CENSUS` heading present at line 858; per-file census sub-sections for HANDOFF.json/STATE.md/continue-here.md all present with full unreadable-SHA lists |
| `260811-pmv-evidence.tsv` | 14 columns, 5 data rows, contains "recommendation" | VERIFIED | 6 lines total (1 header + 5 data), 14 columns confirmed by header split, all 5 rows have closed-vocabulary `NEVER-FROZEN` in col 14, no blank cells |
| `260811-pmv-DOSSIER.md` | Human-readable dossier, contains "Carter's decision", ≥150 lines | VERIFIED | 672 lines; §6 heading is `## §6 — CARTER'S DECISION`; §0/§1/§2/§3/§3b/§4(×5)/§5/§6/§7/Reproduction log all present in order |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| DOSSIER.md | EVIDENCE.md | every quoted number cites the command whose output lives there | VERIFIED | T3's own reconciliation confirms 21/21 commands quoted in DOSSIER present in EVIDENCE.md (self-reported and spot-checked: 5 diffstat pairs + object-store counts independently reproduced) |
| DOSSIER.md | evidence.tsv | summary table = TSV rendered, T3 asserts row-for-row agreement | VERIFIED | DOSSIER §2 summary table values (diffstats, commit counts, recommendation) match evidence.tsv rows exactly for all 5 files (cross-checked manually) |
| DOSSIER.md | HANDOFF.json `carter_decisions_outstanding` SR4-OPEN | answers the question verbatim as posed | VERIFIED | DOSSIER §1 quotes `HANDOFF.json:118` verbatim (`grep -n 'SR4-OPEN' .planning/HANDOFF.json` reproduced independently, text matches) and `deferred-items.md:989` |
| DOSSIER.md | tests/m3/test_source_freeze_pins.py | gated-today column derived by reading the gate | VERIFIED | Independently re-ran `pytest tests/m3/test_source_freeze_pins.py -q` → 39 passed, matching DOSSIER/SUMMARY claim; TSV `gated_today` column names the exact asserting test |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SR4-OPEN | 260811-pmv-PLAN.md | Build the evidence needed to answer whether the 5 files were FROZEN-AND-DRIFTED or NEVER-FROZEN, without recording the disposition | SATISFIED (as an investigation deliverable — the underlying question is intentionally left open) | DOSSIER.md exists, is evidence-complete, and explicitly does not record a disposition; DECISIONS.md/HANDOFF.json/STATE.md unchanged (confirmed above) |

### Anti-Patterns Found

None. This is a documentation/investigation-only task (no source, test, or config files were modified — confirmed by `git diff --name-only b945c595 HEAD` returning exactly the 3 deliverable paths). Grep for TODO/FIXME/placeholder inside the three deliverables returns only verbatim-quoted historical prose (captured `git show` output, as the protocol requires) or narrative descriptions of defects found and fixed during T3 reconciliation — not stub content in the deliverables themselves.

### Independent Reproduction (spot-checks required by the verification brief)

All reproduced independently, outside any trust in the SUMMARY's claims:

1. **Diffstats (5/5 files + 3/3 controls):**
   - `occlusion_manifest.py`: `46 8` → matches dossier's `+46 / -8`
   - `occlusion_present_rate_scan.py`: `154 21` → matches `+154 / -21`
   - `drop_occluded_from_sumstats.py`: `97 24` → matches `+97 / -24`
   - `ld_npz_to_rds.R`: `313 62` → matches `+313 / -62`
   - `pipeline.schema.yaml`: `119 0` → matches `+119 / -0`
   - Controls (`plink_ld_to_npz.py`, `condition_ld_matrix.py`, `occlusion_span_filter.py`): empty — matches
2. **DECISIONS.md grep** for all 5 basenames: `0` each — matches "0 — measured" claims
3. **Traceability spot-check (2/2 SHAs):** `3bb8783` found at `260804-rtc-SUMMARY.md:63`; `64f420a` found at `260805-o7o-VERIFICATION.md:17` and `260805-o7o-SUMMARY.md:67` — both confirmed named in the artifacts the dossier cites
4. **OBJECT-STORE CENSUS reproduction (3/3 files):** re-ran the presence-checked per-revision loop myself — `HANDOFF.json` 76 total/59 readable/17 unreadable, `STATE.md` 304/275/29, `continue-here.md` 64/42/22 — all EXACT matches to the dossier's claimed counts
5. **Contradicting-evidence findings (2/2):**
   - F1–F4: confirmed `2bda675` (2026-08-03) names all four individually inside the "All 7 pinned files 0-line diff" roster sentence in `HANDOFF.json`, and confirmed via `git merge-base --is-ancestor 2bda675 3bb8783` that this label predates the drift. DOSSIER §5 reports this prominently in its own "⚠ The one fact that cuts the other way" subsection and explicitly states it does NOT change the verdict — not averaged into the headline.
   - F5: confirmed it is absent from the `2bda675` roster (`grep -c` on that line = 0), and confirmed via `git merge-base --is-ancestor 2563451 63453db` that its only individual label (`freeze_state` at `63453db`) postdates all its drift commits. DOSSIER §4/F5 reports this as the "weakest case" and correctly does NOT relabel it `FROZEN-AND-DRIFTED`.
6. **Disposition-not-recorded (3/3 checks):**
   - `git diff 7d575a5 HEAD -- .planning/DECISIONS.md` → empty
   - `git diff 7d575a5 HEAD -- .planning/HANDOFF.json` → empty
   - `git diff 5f2028e HEAD -- .planning/STATE.md` → empty
7. **Scope (commits + working tree):**
   - `git show --stat` on `f78bbc1`/`399c50f`/`2b13dce` → each touches only files under the quick directory
   - `git status --porcelain | grep -v '^??'` → empty (zero modified tracked files)
   - Only new untracked path relative to the ~15 pre-existing ones is the SUMMARY.md — expected, since SUMMARY.md is written by the GSD workflow after task completion, outside the plan's 3-deliverable scope
8. **Executor's substituted containment check (D1 deviation) — re-run and assessed:**
   - `comm -13 <(sort baseline) <(current ??)` → empty except for `260811-pmv-SUMMARY.md` (expected — written after T3, not a plan deliverable)
   - `git diff --name-only b945c595 HEAD` → exactly the 3 deliverable paths, nothing else
   - **Assessment: the substitution is genuinely strictly stronger, not a relaxation.** The plan's literal check (`comm` alone must equal exactly the 3 deliverables) became structurally unsatisfiable once the execution protocol's per-task-commit requirement landed those deliverables as tracked files in `f78bbc1`/`399c50f` — a tracked file can never again appear as `??`. The substituted pair covers both halves the original single check conflated: the untracked side (nothing new left lying around, proven by `comm`) and the tracked side (nothing landed outside the 3 deliverables, proven directly by `git diff --name-only` against a pre-execution baseline commit that itself sits outside the repo's working-tree state). This is a superset of what the original check could prove, not a narrower substitute, and the executor reported the substitution loudly (D1) rather than silently reinterpreting the plan.
9. **pytest gate:** `pytest tests/m3/test_source_freeze_pins.py -q` → 39 passed — matches the dossier's/SUMMARY's claim (also confirms nothing in the freeze gate itself was touched by this read-only investigation).

### Human Verification Required

None. All must-haves are independently verifiable via git/grep/pytest and were reproduced above.

### Gaps Summary

No gaps found. All 9 must-have truths, all 3 artifacts, and all 4 key links verify against the actual repository state — not merely against the SUMMARY's claims. The one substantive judgment call in the executor's work (the T3 containment-check substitution, D1) was independently re-run and assessed as strictly stronger than the plan's literal (and, after per-task commits, unsatisfiable) wording.

The SR4-OPEN question itself remains open — DECISIONS.md, HANDOFF.json and STATE.md are all confirmed byte-unchanged since before this task ran. This is the task's designed outcome, not a gap: the plan's objective was explicitly to build evidence, not to dispose of the question.

---

*Verified: 2026-08-11T23:39:26Z*
*Verifier: Claude (gsd-verifier)*
