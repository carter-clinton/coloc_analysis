---
phase: quick-260821-w68
verified: 2026-08-22T04:10:00Z
status: passed
score: 22/22 must-haves verified
overrides_applied: 0
---

# Quick 260821-w68: Record the OSF posting of the occlusion-gate recalibration amendment — Verification Report

**Task Goal:** Record the OSF posting of the occlusion-gate recalibration amendment (mk7ze,
2026-08-22T02:58:55Z): deviation entry appended with Carter's four captures,
DEC-2026-08-22-occlusion-recalibration-posted banked, HANDOFF.gates.osf_pre_registration
CLEARED, record commit tagged AFR-OCCLUSION-GATE-RECALIBRATION-OSF-POSTED-2026-08-22 and pushed,
STATE/HANDOFF/continue-here refreshed. Docs-only; no code change; no OSF contact; an agent never
posts and never fires.

**Verified:** 2026-08-22T04:10:00Z
**Status:** passed
**Mode:** Initial verification (no prior VERIFICATION.md found)

## Method

Every check below was RE-EXECUTED against the live tree at HEAD `84b583d` (branch
`m3-W2-aou-deltas`, origin == local) — nothing was taken on the SUMMARY's word. SUMMARY claims
are cited only as "claimed" values to compare against "observed" re-execution output.

## Checks

| # | Check | Command | Observed | Status |
|---|-------|---------|----------|--------|
| 1 | Paste-block frozen (size) | `awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' <amendment> \| wc -c` | `22945` | PASS |
| 2 | Paste-block frozen (md5) | same, `\| md5sum` | `13a49f543cabcc27ce9f1e589783c060` | PASS |
| 3 | Placeholder guard, all sections | `bash 260819-u8d-placeholder-guard.sh all <amendment>` | `GUARD all: GREEN`, exit 0 (draft/paste-ready/arith/quote all PASS) | PASS |
| 4 | Zero sentinel braces | `grep -c '{{' <amendment>` | `0` | PASS |
| 5 | SLOT_LEDGER exactly 21 lines | `grep -cE '^  [A-Z0-9_]+ = ' <amendment>` | `21` | PASS |
| 6 | Last deviations entry contains `mk7ze` | `tail -n +422 osf_deviations.md \| grep -c mk7ze` | `4` (≥1) | PASS |
| 7 | Contains `https://osf.io/mk7ze` | grep -c | `1` | PASS |
| 8 | Contains `2026-08-22T02:58:55Z` | grep -c | `2` | PASS |
| 9 | Contains observed `2026-08-22T02:58:53Z` + "NOT borne out" (template-refutation disclosure) | grep -c | `1` / `1` | PASS |
| 10 | OSF-stored md5 `13a49f543cabcc27ce9f1e589783c060` present with method caveat (`REFUSED`, "re-download") | grep -c | md5 `2`; `REFUSED` `1`; "re-download" (case-insens.) `3` | PASS |
| 11 | Contains `07df11e44f2d56536ef4ef0753c8d2f8fdb55ae8` | grep -c | `1` | PASS |
| 12 | Contains `2026-07-10T13:32:21Z` (trsx5 1 revision) | grep -c | `1` | PASS |
| 13 | Posting-date disclosure: `422f1f28…` vs posted `13a49f54…`, diff = Date line only | grep -c `422f1f28d6a3b76c7657fadec05a0237` / `4c4` | `1` / `1` | PASS |
| 14 | Zero `<TO BE FILLED AT POSTING>` markers | `tail -n +422 \| grep -c 'TO BE FILLED AT POSTING'` | `0` | PASS |
| 15 | Append is pure — 0 deletions | `git diff c61d179 a2f4fa9 --numstat -- osf_deviations.md` | `110\t0\t...` (deletions col = 0) | PASS |
| 16 | Prefix byte-identical | `git show c61d179:osf_deviations.md \| md5sum` == `head -420` of current file | both `dd3806312977513a8727463ec3a032df`; `git show c61d179:file` is exactly 420 lines, current file's first 420 lines match | PASS |
| 17 | Tag is a plain (non-annotated) tag | `git cat-file -t AFR-OCCLUSION-GATE-RECALIBRATION-OSF-POSTED-2026-08-22` | `commit` | PASS |
| 18 | Tag points at `a2f4fa9`, diff touches only `osf_deviations.md` | `git rev-parse <tag>`; `git show --name-only --format= <tag>` | `a2f4fa9289da9a0d47cf66f87d8bbfeed47c4364`; `.planning/osf_deviations.md` (sole path) | PASS |
| 19 | Tag on origin | `git ls-remote --tags origin \| grep <tag>` | `a2f4fa9…\trefs/tags/AFR-OCCLUSION-GATE-RECALIBRATION-OSF-POSTED-2026-08-22` (count 1) | PASS |
| 20 | DECISIONS.md contains DEC with two-condition authorisation, ceiling-alone NOT authorised | `grep`/`sed` inspection of `DECISIONS.md:2304-2392` | Heading present at line 2304; "The ceiling alone is NOT authorised" present verbatim; both constants (`0.5056`, `3.42x`) stated; three rejected alternatives present | PASS |
| 21 | `run_native_ld_panel.py:133` unchanged | `sed -n '133p' src/python/run_native_ld_panel.py` | `_OCCLUSION_ANOMALY_FRACTION = 0.0005` | PASS |
| 22a | No code touched | `git diff --stat c61d179 HEAD -- src/ tests/ config/ \| wc -l` | `0` | PASS |
| 22b | July amendment byte-unchanged | `git diff --stat c61d179 HEAD -- .../osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md \| wc -l` | `0` | PASS |
| 23 | HANDOFF.json valid JSON | `python3 -m json.tool` | exit 0 | PASS |
| 24 | `gates.osf_pre_registration` contains `THIS OBLIGATION IS CLEARED` and Check-2 still OPEN | python3 json inspection | both `True` | PASS |
| 25 | `resume_on_reconnect[0]` names mk7ze + remediation batch | python3 json inspection | both `True`; list length `19` | PASS |
| 26 | STATE.md exactly one `★ RESUME HERE — LATEST ★`, is the 2026-08-22 POSTED block | `grep -c`; `grep -n` | count `1`, at line 28, heading text is the `2026-08-22 03:25 UTC … POSTED + RECORDED` block | PASS |
| 27 | `.continue-here.md` exactly one `★★ LATEST ★★` | `grep -c` | `1`, matching the `2026-08-22 03:25 UTC — POSTED + RECORDED` block | PASS |
| 28 | `git status -sb` shows no `ahead` | `git status -sb \| head -1` | `## m3-W2-aou-deltas...origin/m3-W2-aou-deltas` (no ahead/behind token) | PASS |
| 29 | Fresh negative control (independent of SUMMARY's transcript) | one-byte flip inside paste block on a scratch copy, same awk/md5 command | unperturbed → `13a49f543cabcc27ce9f1e589783c060`; perturbed (line 169) → `c6ded5b3cadfa69017eecd167772a630`; `cmp -l` = 1 byte | PASS |

**Score:** 22/22 must-haves verified (29 discrete commands run, all passing; some commands
jointly evidence a single must-have from the task brief).

## Notes on the SUMMARY's own honest-count caveats

The SUMMARY (section "Honest count / measurement notes") flagged three plan-vs-observed
discrepancies (HANDOFF.json byte count mismatch, `0.5056` grep count of 9 vs an unstated
expectation, per-line vs per-occurrence grep semantics for `mk7ze`). None of these are
must-haves with hard-pinned expected values in the PLAN's verify blocks — they are informational
byte/line-count observations, and independent re-execution here confirms every value the SUMMARY
reports (the HANDOFF timestamp, gate content, and `mk7ze` occurrence counts all reproduce
exactly). No gap.

## Anti-Patterns Scan

Reviewed the diffs touched by this task (`osf_deviations.md`, `DECISIONS.md`, the amendment's
two post-paste edits, `HANDOFF.json`, `STATE.md`, `.continue-here.md`). No TODO/FIXME/placeholder
patterns, no empty-return stubs, no hardcoded-empty data — this is a docs-only record-keeping
task and the content inspected above is substantive, specific, and internally consistent (no
generic filler text). The one deliberate content substitution (the refuted "Date created"
sentence) was verified replaced with the observed facts rather than silently deleted, matching
the plan's explicit trap-avoidance requirement.

## Human Verification Required

None. Every must-have in this task is either a file-content grep/hash check or a git-object
check, all of which are fully re-executable without human judgment. The task is explicitly
docs-only with no UI, no runtime behavior, and no external service to probe (OSF contact is
prohibited by the task's own constraints, and the four captures are Carter's own supplied
prose, not independently re-verifiable by an agent by design).

## Gaps Summary

None found. All 22 must-haves from the task brief were re-executed against the live tree and
passed, including a fresh, independently-run negative control that reproduced the SUMMARY's own
transcript exactly (same perturbed line, same resulting hash), confirming the frozen-paste-block
invariant is a real, working check and not decoration. The three commits (`a2f4fa9`, `3b9d824`,
`84b583d`) are exactly as claimed: single-path, in order, with the tag on the first and pushed to
origin. No code was touched. The July amendment is byte-unchanged.

---

_Verified: 2026-08-22T04:10:00Z_
_Verifier: Claude (gsd-verifier)_
