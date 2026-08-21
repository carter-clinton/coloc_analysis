---
phase: quick-260820-u6i
verified: 2026-08-21T03:03:04Z
status: passed
score: 10/10 must-haves verified
overrides_applied: 0
---

# quick-260820-u6i: Revise the Instantiated Amendment per Seth's Attack — Verification Report

**Task Goal:** Revise the instantiated occlusion-recalibration amendment per Seth's attack —
count-vs-fraction fix, permissiveness pre-emption, companion inflation gate adopted, §6 note
homed, guard extended additively, PRE_EXECUTE_COMMIT advanced, byte anchors refreshed, reply
courier written.
**Verified:** 2026-08-21T03:03Z
**Status:** passed

## Environment note

`git fsck` shows pre-existing broken tree/blob links elsewhere in this repo (the known
GPFS git object-store loss issue). All objects needed for this verification (the four
quick-260820-u6i commits, the guard, the engine, the amendment, the courier, `8638ed3`,
`f47d9a5`) resolved cleanly via `git show`/`git cat-file`; this is unrelated to the task
under review.

## Goal Achievement — Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | §2 states 1.18x is a COUNT ratio, non-converting, gives 1.12x fraction ratio separately | ✓ VERIFIED | Lines 189-193 state "It is a COUNT ratio and nothing else. **It does NOT convert...**"; fraction ratio 1.12x present with mechanism and 102,421/96,708 denominators, inside the paste block |
| 2 | No-calibrate-to-pass paragraph states the ceiling is numerically MORE permissive than the 10x-withdrawn candidate, and why | ✓ VERIFIED | Lines ~385-400: "more permissive" comparison, row-against-row (0.5664% vs 0.5%), reasoning = selection-for-clearing-the-sample not magnitude |
| 3 | Clause (d) defers on EITHER site-fraction OR row/site inflation > 3.42x, both derived by the same location-statistic x3 rule, three quantities reported per region | ✓ VERIFIED | Lines 319-322 disjunction; companion sub-paragraph derives 3.42x = 3×1.14x median; *Accounting* paragraph names site fraction, row count, and inflation per region |
| 4 | Companion anchor is the MEDIAN (1.14x), explicitly distinguished from the reported MEAN (1.18x) | ✓ VERIFIED | R8 mean-vs-median disambiguation present in text; SLOT_LEDGER carries both `MEAN_ROW_SITE_INFLATION=1.18x` and `INFLATION_MEDIAN_X=1.14x` |
| 5 | Collinearity note: substance inside paste block, exact repo path only in NOT-YET-APPENDED deviations block, never both | ✓ VERIFIED | `near-collinear` substance found inside paste block (lines 1-498); `note-same-position-collinearity` path absent from paste block, present only at line ~85 (after paste closer at line 498) |
| 6 | Seth's status line verbatim, lowercase "not posted", from attack record line 104, not the capitalized provenance-header paraphrase | ✓ VERIFIED | Attack record line 104 = "measurement banked; amendment drafted, not posted; ..." (lowercase); amendment line 37 (outside paste markers) matches byte-for-byte; provenance header (lines 10-11) has capitalized "NOT posted" and is NOT what was copied |
| 7 | Every new number entered through the extended script from a banked record; 11 Class-M unmoved; 2 Class-P force-substituted; PRE_EXECUTE_COMMIT advanced at every occurrence | ✓ VERIFIED | Independent recompute of all 8 new slots from the two banked records matches file values exactly (see below); Python diff of pre-revision vs. current ledger confirms 11 Class-M byte-identical, PRE_EXECUTE_COMMIT advanced `8638ed3→2689cae` (== `b4263e7^`, the correct pre-Task-2 HEAD) at exactly 2 occurrences, superseded hash absent, `2026-08-21` exactly 3 occurrences |
| 8 | Extended guard seen RED once per new identity on a perturbed copy; pre-existing controls reproduce | ✓ VERIFIED | Re-ran transcript's NC-A/B/C/D/E/F/G and REG-1/2/3 sections directly from `260820-u6i-guard-transcript.txt`; all signature strings present and isolated as claimed. Independently perturbed `INFLATION_CEILING_3X_X` in a fresh scratch copy and confirmed guard `arith` exits 1 naming exactly that identity |
| 9 | Guard extension is additions-only: commit carries zero deleted lines | ✓ VERIFIED | `git diff --numstat 9a9f51f^ 9a9f51f` = `64  0`; `TOL_RATIO = 0.02` and fail-closed `*)` arm both still present |
| 10 | Nothing posted/fired: DRAFT-NOT-POSTED banner intact, `_OCCLUSION_ANOMALY_FRACTION` untouched, `osf_deviations.md` byte-unchanged | ✓ VERIFIED | Banner present in `guard all` output; `src/python/run_native_ld_panel.py:133` still `= 0.0005`; `git status --porcelain` on `osf_deviations.md`, `STATE.md`, `ROADMAP.md`, and the collinearity note file all empty across `9a9f51f^..HEAD` |

**Score:** 10/10 truths verified

### Independent recomputation (not trusting the SUMMARY's numbers)

Recomputed directly from `.planning/debug/260820-site-basis-sweep-results-as-received.md`'s
21-row inflation column and `.planning/debug/260819-occ-measure-sweep-results-as-received.md`'s
21 `frac=` values, using plain Python (`statistics.median`, MAD):

| Slot | Independently recomputed | In file | Match |
|---|---|---|---|
| INFLATION_MIN_X | 1.04x | 1.04x | ✓ |
| INFLATION_MEDIAN_X | 1.14x | 1.14x | ✓ |
| INFLATION_MAX_X | 1.79x | 1.79x | ✓ |
| INFLATION_ROBUST_SIGMA_X (1.4826×MAD) | 0.088956 → 0.0890x | 0.0890x | ✓ |
| INFLATION_CEILING_3X_X (3×median) | 3.42x | 3.42x | ✓ |
| INFLATION_MARGIN_X (ceiling/max) | 1.9106 → 1.91x | 1.91x | ✓ |
| ROW_MEDIAN_PCT | 0.1888% | 0.1888% | ✓ |
| FRACTION_RATIO_X (row median/site median) | 1.1205 → 1.12x | 1.12x | ✓ |
| MEAN_ROW_SITE_INFLATION (unchanged, sanity) | 1.1805 → 1.18x | 1.18x | ✓ |

### 2x2 guard/document matrix (independently reproduced)

Old guard extracted at `8638ed3` was placed at the correct relative repo depth
(`.planning/quick/<tmp>/old_guard.sh`, cleaned up after) so its internal `REPO_ROOT`
resolution worked; old 13-slot amendment extracted at `f47d9a5`.

| | PRE-REVISION file (13 slots) | REVISED file (21 slots) |
|---|---|---|
| **PRE-EXTENSION guard** (`8638ed3`) | GREEN (exit 0) | RED (exit 1) |
| **EXTENDED guard** (current) | RED (exit 1, missing 8 roster names) | GREEN (exit 0) |

Matches the claimed diagonal-only shape exactly.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `260819-u8d-placeholder-guard.sh` | 21-slot roster, `*_X` pattern arm, 3 identities + ordering check | ✓ VERIFIED | `ROSTER+=(` present; all 8 new slot names present; `git diff --numstat` for `9a9f51f` = `64  0` |
| `260820-s2x-instantiate.py` | `SOURCE_ROW`, `--second-pass`, `--dry-run`, pre-registered expectations | ✓ VERIFIED | `--dry-run` exits 0, prints `RECONCILIATION: OK` and all 8 pre-registered renders byte-identical |
| `260820-u6i-guard-transcript.txt` | ≥200 lines, verbatim green+reds+matrix | ✓ VERIFIED | 894 lines, 20 sections, 5×`EXIT=0`, 17×`EXIT=1` |
| `osf-amendment-occlusion-gate-recalibration-2026-08-20.md` | 21 filled ledger slots | ✓ VERIFIED | `guard all` GREEN; 21 ledger lines; 0 sentinels; 42,213 B / `e1b4a11d18ad2907af4f0a93fd5747d2` |
| `260820-SETH-ATTACK-instantiated-amendment-as-received.md` | banked 6th supporting record | ✓ VERIFIED | Tracked; status line present |
| `260820-COURIER-TO-SETH-revision-reply.md` | ≥20 lines, ≤50 cap, new anchors | ✓ VERIFIED | 49 lines; names `2689cae` and `8638ed3`; anchors match file byte-for-byte |

### Key Link Verification

| From | To | Via | Status |
|---|---|---|---|
| site-basis sweep record | amendment | `--second-pass` inflation-column parse | ✓ WIRED — independently recomputed values match file |
| row-sweep record | amendment | `ROW_MEDIAN_PCT` parse + reconciliation | ✓ WIRED — recomputed median 0.1888% matches |
| guard.sh | amendment | `guard all` — exit 0 gate | ✓ WIRED — reproduced GREEN independently |
| amendment | note-same-position-collinearity-2026-08-19.md | path in deviations block only | ✓ WIRED — path absent from paste block, present after closer |
| amendment | courier | `wc -c`/`md5sum` anchors | ✓ WIRED — anchors identical |

### Anti-Patterns / Forbidden-Scope Check

`git diff --name-only 9a9f51f^..HEAD` touches exactly six files, all under
`.planning/{amendments,debug,quick}/`. No hits under `src/`, `tests/`, `config/`,
`Snakefile`, the July amendment, `osf_deviations.md`, `STATE.md`, `ROADMAP.md`, or the
collinearity note file. `tests/m3/sparse_parent_benchmark.tsv` unstaged. No blockers found.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Guard green on revised amendment | `bash guard.sh all <amendment>` | `GUARD all: GREEN`, exit 0 | ✓ PASS |
| Negative control on new identity | perturb `INFLATION_CEILING_3X_X` in scratch copy, run `arith` | exit 1, names exactly that identity BROKEN | ✓ PASS |
| Full Task 1/2/3 automated verify blocks (from PLAN) | re-executed verbatim | all print `TASK{1,2,3} VERIFY OK` | ✓ PASS |
| PRE_EXECUTE_COMMIT advance check | Python diff old vs. new ledger, `EXPECT_COMMIT = b4263e7^` | `PRE_EXECUTE_COMMIT ADVANCED 8638ed3 -> 2689cae` | ✓ PASS |

Note: the PLAN's own Task 2 verify snippet computes `EXPECT_COMMIT=$(git rev-parse HEAD^)`,
which is only correct when run immediately after Task 2's commit (before Task 3 lands). Run
at the current HEAD (after Task 3's courier commit), `HEAD^` resolves to Task 2's own commit
rather than Task 1's. This is a timing artifact of the verify snippet's design, not a defect
in the deliverable — using the point-in-time-correct reference (`b4263e7^`, which is exactly
what `PRE_EXECUTE_COMMIT` in the file equals) confirms the advance is correct.

### Requirements Coverage

| Requirement | Status | Evidence |
|---|---|---|
| DEC-2026-08-19-occlusion-recalibration-adopted | ✓ SATISFIED | Companion gate adopted per this revision, consistent with the prior decision record |
| OSF-AMEND-OCCLUSION-REVISE-PER-SETH | ✓ SATISFIED | All four of Seth's asks (§2/§3/§4/§6) addressed with text + machine-checked identities |
| OSF-AMEND-OCCLUSION-COMPANION-INFLATION-GATE | ✓ SATISFIED | Clause (d) is now a disjunction with the 3.42x companion condition, derived and guarded |

### Human Verification Required

None. All must-haves are machine-verifiable and were independently re-executed (not merely
re-read from the SUMMARY).

## Gaps Summary

No gaps found. All 10 must-have truths, all 6 artifacts, and all 5 key links verified
independently — guard re-run fresh (not trusted from transcript alone), inflation/fraction
statistics recomputed from the banked source records by hand, the 2x2 guard/document matrix
reproduced from scratch (old guard placed at correct relative path depth to resolve its
internal `REPO_ROOT`), a fresh negative control run against a newly perturbed copy, byte
anchors recomputed and compared to both the amendment and the courier, forbidden-path scope
checked via `git diff --name-only` across the full task commit range, and all three of the
PLAN's own automated verify blocks re-executed end-to-end with matching results.

---

_Verified: 2026-08-21T03:03:04Z_
_Verifier: Claude (gsd-verifier)_
