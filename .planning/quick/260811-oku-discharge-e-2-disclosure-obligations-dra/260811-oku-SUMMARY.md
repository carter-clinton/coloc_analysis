---
phase: quick/260811-oku
plan: 01
subsystem: disclosure-drafting
tags: [e2, disclosure, osf, manuscript, track-a, id-vs-ref-ld, m3, docs-only]

requires:
  - phase: m3-aou-afr-ld-panel-build
    provides: "DEC-2026-08-07-e2-orientation-disposition (option A), e2-exposure-track-a-regions.tsv, e2-exposure-real-corpus.tsv, e2-exposure-measure.R"
provides:
  - "obligation (1) DRAFT: the Track A manuscript paragraph in BOTH framings, 175 / 171 words, journal-ready prose"
  - "obligation (2) DRAFT: the OSF record entry in BOTH framings, 969 / 989 words, append-only NEW-supplementary-file semantics on az52u"
  - "obligation (3) DECISION SURFACE: LIMITATION vs CORRECTION compared, with a recommendation and the two conditions that would flip it"
  - "260811-oku-check-drafts.sh: a 29-clause numbers-fidelity + framing-completeness harness with six OBSERVED-red negative controls"
affects: [e-2, e-4, osf-record, track-a-submission, m3-aou-afr-ld-panel-build]

tech-stack:
  added: []
  patterns:
    - "matched-pair drafting: a framing choice selects one manuscript paragraph AND one OSF entry, so an above-authority question becomes a comparison of two concrete texts"
    - "paste-block contract (<!-- PASTE-BEGIN: id --> / <!-- PASTE-END: id -->) makes prose deliverables machine-checkable for numeric fidelity"
    - "negative-control-first acceptance harness for PROSE, not just code"

key-files:
  created:
    - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-check-drafts.sh
    - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-manuscript-limitation-drafts.md
    - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-osf-entry-drafts.md
    - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-framing-decision-surface.md
  modified:
    - .planning/STATE.md

key-decisions:
  - "Recommended framing: CORRECTION (framing B) -- a limitation is something the data cannot do; an allele-ignoring join is something the pipeline did wrongly. The convention is provable in code and substrate-independent; only the magnitude is stub-bound, and both bodies already carry the identity-LD-stub caveat. Recommendation only -- the choice is Carter's and is deliberately left open."
  - "The pooled 5.29% is deliberately ABSENT from both manuscript paste blocks (per-region is the honest unit for a paragraph) and PRESENT in both OSF bodies, where it appears only alongside the per-region table and the dragged-down-by-the-clean-regions sentence."
  - "The 0.20% -> 20.33% internal misread and the 46/182 = 25.3% synthetic fixture are treated as INTERNAL-record corrections, not OSF obligations, because neither was ever externally reported -- stated explicitly in the decision surface so Carter can overrule it."
  - "Grep dialect re-measured under the real script interpreter: /usr/bin/grep = GNU grep 3.6, NOT the ugrep the plan asserted. The \\b0\\.00\\b pattern is kept and independently verified in both directions."

patterns-established:
  - "Clauses are LINE-SCOPED: grep is line-oriented, so a required multi-word phrase must not be hard-wrapped across a newline in a deliverable. Discovered by a self-test control going red."
  - "Where a required-token control cannot be isolated (NC-2 necessarily trips MS-04 as well), add a companion control that fires the clause ALONE (NC-2b) so the clause is proven capable of firing on its own."

requirements-completed: [E2-OBL-1-MANUSCRIPT, E2-OBL-2-OSF, E2-OBL-3-FRAMING-SURFACE]

duration: 41min
completed: 2026-08-11
---

# quick/260811-oku: E-2 disclosure drafts Summary

**Both framings of both E-2 disclosure artifacts now exist as complete, paste-ready texts guarded by a 29-clause harness with six observed-red negative controls — so the one question still above executor authority ("LIMITATION or CORRECTION?") is now a choice between two matched pairs rather than a decision in the abstract. All three obligations remain UNDISCHARGED.**

## Performance

- **Duration:** ~41 min
- **Tasks:** 3 of 3
- **Files created:** 4 (all inside this quick directory)
- **Files modified:** 1 (`.planning/STATE.md`, two inserted body lines)
- **Cost:** `$0`. Zero perimeter contact — no `gcloud`, no `wb`, no `gsutil`, no LSF submission, no AoU access of any kind.

## Task record

| Task | Name | Commit | Files |
|---|---|---|---|
| 1 | Harness (RED first) + both manuscript paragraphs | `17d4f11` | `260811-oku-check-drafts.sh`, `260811-oku-e2-manuscript-limitation-drafts.md` |
| 2 | The OSF record entry, in both framings | `53e337d` | `260811-oku-e2-osf-entry-drafts.md` |
| 3 | The framing decision surface + full harness green | `237342d` | `260811-oku-e2-framing-decision-surface.md` |

`.planning/STATE.md` carries the required dated body line but is **left uncommitted for the orchestrator's docs commit**, per the execution constraints (the plan's Task 3 asked the executor to commit it; the orchestrator instruction overrides).

## ⚠ THE THREE E-2 OBLIGATIONS REMAIN UNDISCHARGED

Drafting is not disclosing. Nothing was posted, no manuscript file was opened for write, no Track A artifact moved, no source or test changed, and no obligation is marked discharged anywhere.

| Obligation | Discharges when | Status |
|---|---|---|
| (1) manuscript limitation paragraph | the selected paragraph is **placed** in the Track A manuscript | **UNDISCHARGED** |
| (2) OSF record entry | the selected body is **posted** as a new supplementary file on `osf.io/az52u` **and** its URL + timestamp land in `.planning/osf_deviations.md` | **UNDISCHARGED** |
| (3) LIMITATION vs CORRECTION | the framing is **chosen by Carter** and recorded in `DECISIONS.md` | **UNDISCHARGED** |

## Verification 1 — the numbers, re-derived from the TSV (not retyped from prose)

Computed during Task 1 by grouping `.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-track-a-regions.tsv` on `track_a_region` and forming `flipped / (exact + flipped)`:

```
track_a_region            exact  flipped        pct
APOL1_22q12                4910     1108     18.41%
CXADR_F2RL1_6p21          28415       18      0.06%
FTO_16q12                  7188     2245     23.80%
MC4R_18q21                14141       10      0.07%
SH2B3_12q24               11826      333      2.74%
POOLED                    66480     3714      5.29%

anchor tiles1+2: exact=10521 flipped=0   pct=0.00%
tile3          : exact=1305  flipped=333 pct=20.33%
```

Corpus context, re-derived from `e2-exposure-real-corpus.tsv` (EUR arm; 618 rows = 206 regions x 3 ancestry arms):

```
EUR-arm regions measured: 206
regions with >=1 flipped: 195 / 206
median pct: 17.82%
mean pct  : 12.49%
max pct   : 38.68% (RAD50_peak__tile1)
pooled    : 4.18% (31152 / 745534)
```

`ls data/processed/region_analysis/ld_reference/variants/ | wc -l` = **207** catalogs (206 regions measured per arm — the drafts state both, and clause MS-05 requires `206` alongside `195` precisely so a block cannot write "195 of 207").

**Every locked number in the plan reproduced exactly.** No number was carried from prose into a draft.

## Verification 2 — `--self-test`: all five required negative controls OBSERVED red

Verbatim output of `./260811-oku-check-drafts.sh --self-test` (exit 0):

```
=== NC-0 (positive control): untouched fixture must PASS ===
PASS MS-01    both paste blocks present exactly once
PASS MS-02    each block is 120-200 words
PASS MS-03    journal-ready prose: no headers, no tables inside a block
PASS MS-04    every per-region number + the SH2B3 anchor-vs-tile3 split
PASS MS-05    corpus context: median, max, 195 of 206
PASS MS-06    identity-LD-stub caveat in every block
PASS MS-07    the denominator is stated in every block
PASS MS-08    the pooled 5.29% is never quoted alone
PASS MS-09    original-research framing (no revision/salvage/cleanup)
PASS MS-10    fixture correction, mechanism, consequences, E-4, 207 catalogs
PASS MS-11    states DRAFT + not discharged on its face
exit=0

=== NC-1 (18.41 corrupted to 1.841) : expect MS-04 to go RED (and ONLY MS-04) ===
FAIL MS-04    every per-region number + the SH2B3 anchor-vs-tile3 split --  ms-correction:missing(18\.41)
exit=1  fail_clauses=1

=== NC-2 (pooled 5.29% quoted, per-region numbers deleted) : expect MS-08 to go RED ===
FAIL MS-04    every per-region number + the SH2B3 anchor-vs-tile3 split --  ms-limitation:missing(0\.06) ms-limitation:missing(0\.07) ms-limitation:missing(2\.74) ms-limitation:missing(\b0\.00\b) ms-limitation:missing(20\.33) ms-limitation:missing(18\.41) ms-limitation:missing(23\.80) ms-limitation:missing(APOL1_22q12) ms-limitation:missing(FTO_16q12)
FAIL MS-08    the pooled 5.29% is never quoted alone --  ms-limitation:pooled-without-18.41 ms-limitation:pooled-without-23.80
exit=1  fail_clauses=2

=== NC-2b (pooled 5.29% kept, 'dragged down' statement removed) : expect MS-08 to go RED (and ONLY MS-08) ===
FAIL MS-08    the pooled 5.29% is never quoted alone --  file:no-dragged-down-statement
exit=1  fail_clauses=1

=== NC-3 (identity-LD-stub caveat deleted) : expect MS-06 to go RED (and ONLY MS-06) ===
FAIL MS-06    identity-LD-stub caveat in every block --  ms-limitation:missing(identity) ms-limitation:missing(use_identity) ms-limitation:missing(byte-identical) ms-limitation:missing(bookkeeping)
exit=1  fail_clauses=1

=== NC-4 (240-word block) : expect MS-02 to go RED (and ONLY MS-02) ===
FAIL MS-02    each block is 120-200 words --  ms-correction:253words
exit=1  fail_clauses=1

=== NC-5 (SH2B3 anchor 0.00% omitted; SH2B3 still 2.74%, tile 3 still 20.33%) : expect MS-04 to go RED (and ONLY MS-04) ===
FAIL MS-04    every per-region number + the SH2B3 anchor-vs-tile3 split --  ms-correction:missing(\b0\.00\b)
exit=1  fail_clauses=1

=== SELF-TEST VERDICT ===
SELF-TEST PASSED: every negative control was OBSERVED red on its named clause.
```

Four of the five required controls fail on **exactly one** clause. NC-2 necessarily trips MS-04 as well (deleting the per-region numbers is what MS-04 exists to catch), so **NC-2b** was added: it keeps every number and removes only the "dragged down" statement, firing **MS-08 alone**. Without it, MS-08 would never have been seen failing in isolation.

`--self-test` runs with **no deliverable present** (it builds its own fixtures under `$TMPDIR` and cleans up), and absence of a deliverable is a loud failure, never a skip:

```
$ ./260811-oku-check-drafts.sh --only ms          # before any draft existed
FAIL MS-00    deliverable file present -- file not found: .../260811-oku-e2-manuscript-limitation-drafts.md
1 clause failure(s).      # exit 1
```

## Verification 3 — the full harness, green over all three deliverables

`./260811-oku-check-drafts.sh` → **29 clauses, 0 failures, exit 0** (MS-01..11, OSF-01..13, SURF-01..05).

Manuscript paste-block word counts (contract: 120-200):

| Block | Words |
|---|---|
| `ms-limitation` | **175** |
| `ms-correction` | **171** |

OSF paste-body word counts (contract: >= 250): `osf-limitation` **969**, `osf-correction` **989**.

**SURF-03 was observed red against the real decision surface** before the prose was fixed: a capitalised "**No re-analysis**" missed the case-sensitive clause. Unplanned, but it is direct evidence that the surface clauses are exercised rather than assumed.

## Verification 4 — scope

- `git status --porcelain` tracked modifications: **`.planning/STATE.md` only** (plus the four new files in this quick directory).
- `git diff --stat 7d575a5 HEAD -- src/ tests/ config/ results/ .planning/amendments/ .planning/DECISIONS.md .planning/HANDOFF.json Snakefile` → **0 lines**. Nothing outside the allowed surface moved.
- `git status --porcelain .planning/amendments/ results/` (tracked) → **empty**. The four md5 locks and `TRACK-A-FROZEN-NUMBERS.md` are byte-untouched.
- `.planning/STATE.md` diff is a single hunk `@@ -54,0 +55,2 @@` — **body only**. The unparseable YAML frontmatter (lines 1-21, the `last_activity` scalar landmine) is byte-unchanged.
- No `git add -A` / `git add .` was used at any point; every stage was an explicit path.

## Deviations and corrections

### 1. [Correction carried from the plan-checker] The plan's grep-dialect diagnosis was wrong; the pattern it chose is right

The plan (lines ~320-329) asserts that `grep` on this node is **ugrep 7.5.0** and that `grep -E '(^|[^0-9])0\.00([^0-9]|$)'` nomatches. That measurement came from the planning agent's **interactive CLI wrapper**, not from the node's script-execution interpreter. Measured here under a real shebang script:

```
which grep: /usr/bin/grep
grep (GNU grep) 3.6
```

Under GNU grep 3.6 **both** the old and the new pattern behave correctly. The plan's chosen `\b0\.00\b` is kept — it is the clearer form and was independently re-verified in both directions (matches `anchor tiles 0.00% and`, `0.00` at line start and at line end; does **not** match `20.33`, `10.005`, `20.00%`; `\b195\b` matches `195 of 206` and not `1955`). The real interpreter is stated in the script header and the ugrep claim is explicitly **not** propagated.

### 2. [Rule 1 - Bug, in my own harness] Every clause is line-scoped; a required phrase wrapped across a newline never matches

The first `--self-test` run went red on the **positive control**: `MS-10 file:missing(not comparable|NOT comparable)`. The fixture preamble had wrapped the phrase as `not / comparable`, and `grep` is line-oriented. This is a property of the whole harness, not of one fixture: every multi-word required phrase (`not comparable`, `not discharged`, `exact + flipped`, `no pre-registered number`, `new supplementary file`, `append-only`, `Track A's frozen numbers`, and SURF-02's Carter sentence) must sit on ONE line in a deliverable. Documented in the script header; all four deliverables comply.

### 3. [Rule 2 - Missing critical control] NC-2b added so MS-08 is proven able to fire alone

Spec'd NC-2 (per-region numbers deleted while the pooled figure stays) necessarily trips MS-04 too. A clause that has only ever been seen failing *alongside* another clause has not been shown capable of failing on its own. NC-2b keeps every number and removes only the "dragged down" sentence: MS-08 fires alone. Six controls total, five required + one isolator.

### 4. [Constraint from the orchestrator] `.planning/STATE.md` written but not committed

The plan's Task 3 instructed the executor to commit STATE.md with the four deliverables. The execution constraints override: the body line is written, the file is left modified-but-unstaged for the orchestrator's docs commit.

### 5. Two fixture defects fixed, zero clause defects

Both self-test failures on the first run (the wrapped phrase above and a 119-word fixture block against the 120-word floor) were defects in the **fixtures**, not in the clauses — the clauses behaved exactly as specified in every case. Per the plan's own instruction ("If a control passes, fix the clause, not the fixture"), the converse also held: no clause was weakened to make anything green.

## Notes for whoever picks this up

- **The recommendation is CORRECTION, and it is only a recommendation.** The decision surface names two conditions that would flip it, one of which (the target journal's policy on a "correction" framing for a manuscript still *in submission*) is the single input to this decision that does not live in this repository.
- **The E-2/E-4 coupling is stated in all four deliverables.** Option B of the disposition (the code change) is inert today because `_ancestry_for_region` returns `"EUR"` unconditionally; both OSF bodies phrase any code-side commitment as bundled with E-4 and a real panel, never as imminent.
- **The Check-2 amendment-update obligation is untouched and stays separate** — stated on the face of the OSF pre-paste block so the two are not folded into one posting.
- **Do not re-derive these numbers from any draft.** The provenance chain is `e2-exposure-measure.R` -> `e2-exposure-{real-corpus,track-a-regions}.tsv`; the drafts are downstream of it, and the harness is what keeps them consistent with it.

## Self-Check: PASSED

- All four deliverables exist on disk (515 / 145 / 154 / 185 lines; the harness carries the exec bit), each above its `min_lines` floor (90 / 60 / 90 / 70) and each containing its contracted marker (`--self-test`, `PASTE-BEGIN: ms-correction`, `PASTE-BEGIN: osf-correction`, `Recommendation`).
- All three task commits exist: `17d4f11`, `53e337d`, `237342d`.
- Both `key_links` hold: the manuscript drafts cite `e2-exposure-track-a-regions.tsv` as provenance, and the OSF drafts name `az52u`.
- Tracked-tree scope re-verified at close: `.planning/STATE.md` modified (uncommitted, for the orchestrator) and `260811-oku-SUMMARY.md` untracked (likewise). Nothing else.
