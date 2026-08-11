---
phase: quick/260811-pmv
plan: 01
subsystem: m3-source-freeze
tags: [freeze, provenance, evidence, sr4-open, m3, git-history]
baseline_rev: b945c595
commits:
  - f78bbc1  # T1 -- EVIDENCE.md (verbatim log) + evidence.tsv
  - 399c50f  # T2 -- DOSSIER.md
  - 2b13dce  # T3 -- reconciliation + reproduction log + 3 defect fixes
requires: [bf16289, bf04199]
provides:
  - "260811-pmv-DOSSIER.md -- the one file Carter opens to answer SR4-OPEN per file"
  - "260811-pmv-EVIDENCE.md -- every command, unedited output and rc; the dossier's source of truth"
  - "260811-pmv-evidence.tsv -- 14 columns x 5 rows, machine-readable"
affects:
  - "SR4-OPEN remains OPEN -- this task builds the evidence, it does not dispose"
tech-stack:
  added: []
  patterns:
    - "presence-checked per-revision history walk (git log -S is BANNED: rc=128 with rows still on stdout)"
    - "two-half traceability -- a task token is a CLAIM, the SHA named in the artifact is the RECORD"
    - "loose match + read the hits, so a null result is strong and false positives are discarded by name"
    - "containment proven by set difference against a repo-EXTERNAL baseline"
key-files:
  created:
    - .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-EVIDENCE.md
    - .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-evidence.tsv
    - .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md
  modified: []
decisions:
  - "NONE RECORDED -- the SR4-OPEN disposition is Carter's and was deliberately NOT written to DECISIONS.md"
metrics:
  duration: "~1h"
  completed: 2026-08-11
  tests_m3_freeze_gate: "39 passed (read, never changed)"
  cost: "$0, NC State only, zero perimeter contact, zero LSF"
---

# quick/260811-pmv: SR4-OPEN evidence dossier Summary

Put every fact bearing on **SR4-OPEN** — *were the five "frozen" files
**FROZEN-AND-DRIFTED** or **NEVER ACTUALLY FROZEN**?* — into one file, measured
today, each number naming the command that produced it. **The disposition is
Carter's and is deliberately NOT recorded.**

---

## 1. THE ANSWER THE EVIDENCE SUPPORTS

**`NEVER-FROZEN`, all five.** Per-file recommendations (closed vocabulary):

| file | diff vs `bf16289` today | commits | all traceable? | `DECISIONS.md` declaration | recommendation |
|---|---|---|---|---|---|
| `src/python/occlusion_manifest.py` | `+46 / -8` | 2 | yes (2/2) | **0 — measured** | **NEVER-FROZEN** |
| `src/python/occlusion_present_rate_scan.py` | `+154 / -21` | 3 | yes (3/3) | **0 — measured** | **NEVER-FROZEN** |
| `src/python/drop_occluded_from_sumstats.py` | `+97 / -24` | 2 | yes (2/2) | **0 — measured** | **NEVER-FROZEN** |
| `src/scripts/ld_npz_to_rds.R` | `+313 / -62` | 1 | yes (1/1) | **0 — measured** | **NEVER-FROZEN** |
| `src/snakemake/schemas/pipeline.schema.yaml` | `+119 / -0` | 5 | yes (5/5) | **0 — measured** | **NEVER-FROZEN** |

All five diffstats are **identical to the sr4-era (2026-08-06) numbers** —
nothing moved in the five days since. The control (`plink_ld_to_npz.py`,
`condition_ld_matrix.py`, `occlusion_span_filter.py`) is **`+0 / -0`**, so
"these five moved" is a measurement, not a story.

**Four independent measurements support the verdict:**

1. **`bf16289` is not a freeze commit.** It is a `docs(handoff)` session-close
   commit that changed **one** file (`.continue-here.md`, +19/−3) and touched
   **none** of the eight it supposedly froze (measured per path).
2. **The freeze convention did not exist in the register until after all the
   drift.** `DEC-2026-08-06-sr4-freeze-scope` is the only freeze entry, it names
   only the three controls and `run_susie_rss.R`, and `grep -c` for each of the
   five inside it is **0**.
3. **`bf16289` was enforced by zero tests AT EVERY DRIFT COMMIT** — checked at
   the 8 commits themselves (`git grep -c 'bf16289' <commit> -- tests/ src/
   config/ Snakefile` → 0 matching files, all 8), not inferred from the register.
4. **Every drift commit is reviewed work** (see §2).

## 2. ⚠ UNTRACEABLE COMMITS FOUND: **ZERO**

All **8** distinct drift commits satisfy **both** halves of traceability — the
task token resolves to a real artifact directory **and** the commit's short SHA
is named inside that artifact (13 grep hits total):

`3bb8783`, `bf963df`, `fac9a93` → `260804-rtc` · `aeed8c0`, `57b381f` →
`260805-23d` · `64f420a` → `260805-o7o` · `2563451` → `260805-w7u` ·
`d7dfa67` → `m3-04b` (phase dir).

**No file is forced to `DRIFT-NEEDS-REVIEW`.** All five `git log` walks returned
`rc=0` — no history was truncated by a missing object.

## 3. ⚠ THE EVIDENCE THAT CUTS THE OTHER WAY — reported, not buried

**For F1–F4 a narrative label DID exist before the drift.** The collective
roster at `2bda675` (2026-08-03) — *"All 7 pinned files 0-line diff vs bf16289:
the 4 m3-07 modules (...) + the 3 frozen contracts (...)"* — names F1, F2, F3
and F4 individually and **precedes every one of their drift commits**
(`git merge-base --is-ancestor`, measured). Three things bound its weight, and
Carter should weigh them: it is a **status report**, not a prohibition; it lives
in handoff prose, not the register; it was enforced by nothing.

**F5 is the weakest case, in two independent ways.** `pipeline.schema.yaml` was
**never in the "7 pinned files" roster at all**, and its only individual label
(the `freeze_state` field at `63453db`) **postdates all of its drift**
(`2563451` is an ancestor of `63453db`). Had that label been a register
declaration, the date-order rule would have returned
`NEVER-FROZEN-UNTIL-DECLARED`: **declared frozen only after it stopped moving, so
there is nothing to review.**

**Nothing else contradicted the expected reading.** No untraceable commit, no
truncated walk, no register declaration for any of the five.

## 4. OBJECT-STORE CENSUS — first-appearance dates are LOWER BOUNDS

| narrative file | revisions | readable | **unreadable** |
|---|---|---|---|
| `.planning/HANDOFF.json` | 76 | 59 | **17** |
| `.planning/STATE.md` | 304 | 275 | **29** |
| `.../m3-aou-afr-ld-panel-build/.continue-here.md` | 64 | 42 | **22** |

All 68 unreadable SHAs are listed in EVIDENCE.md's `OBJECT-STORE CENSUS`. The
unreadable set skews **old** — exactly where an earlier freeze label would live —
so **every first-appearance claim is a LOWER BOUND**. No object recovery was
attempted (that is a repo-repair task).

**The `git log -S` trap was reproduced at HEAD:** it printed 2 plausible rows
**and returned `rc=128`**. Had it been used with `2>/dev/null` it would have
returned a short, credible, **truncated** answer with the old end silently cut
off. All walks used a presence-checked per-revision loop instead.

## 5. THE RESIDUAL LIVE CORRECTION SITES (scoped, not searched for)

If Carter answers `NEVER-FROZEN`, the remedy is language. The retraction already
landed at `HANDOFF.json:18` and `STATE.md:39`. Classified mechanically by the
`>` prefix (dated `>` blocks are HISTORY and are **not** correction sites), the
live sites are exactly two:

- **`.planning/STATE.md:15`** — *"Frozen contracts byte-unchanged (plink_ld_to_npz.py
  / ld_npz_to_rds.R / condition_ld_matrix.py all git-diff EMPTY)"* — **FALSE for
  `ld_npz_to_rds.R`** (`+313 / -62`).
- **`.planning/ROADMAP.md:1077`** — *"panel `.npz` contract frozen
  (`ld_npz_to_rds.R` unchanged)"* — **FALSE**.

**Neither was edited.** This was a read-only investigation.

## 6. THE COST OF GATING ANY OF THE FIVE (a decision surface, no recommendation)

A recorded Carter decision first (`PY_FROZEN_RELS`'s own comment demands it), a
`#:` bucket annotation, a negative control observed RED, and:

- ⚠ **`test_the_handoff_frozen_claim_is_recorded_as_partly_false` goes RED for
  any file added** — its first assertion is `rel not in PY_FROZEN_RELS` and its
  second requires a non-empty numstat. Quoted in the dossier.
- ⚠ **F5 additionally needs a YAML code-stripper that does not exist** —
  `source_freeze.py` supports `LANG_R` and `LANG_PY` only (`grep -c -i 'yaml'`
  → **0**); sr4 declined to build it. **F4 is R, so `LANG_R` covers it.**
- A pin at `bf16289` is unavailable for all five (they have moved); gating would
  mean pinning at a **new** SHA — a weaker and different claim than the handoff's.

## 7. DEVIATIONS

### D1 (SIGNIFICANT) — ⚠ the plan's containment check is UNSATISFIABLE once per-task commits land

T3 STEP 6 requires `comm -13 <baseline> <current '??'>` to print **exactly the
three deliverables**. But the execution protocol requires a **commit per task**,
and T1/T2 committed the deliverables — so they are **tracked** and can never
appear as `??` again. The clause returns empty and fails as written. Both
mandates cannot hold at the end of T3.

**Resolved by strengthening, never by relaxing** — reported loudly rather than
papered over:

- untracked delta vs the baseline → **EMPTY** (nothing new left lying around);
- `git diff --name-only b945c595 HEAD` → **EXACTLY the 3 deliverables**.

The pair is strictly stronger than the original: it proves nothing escaped
either as a stray file **or** as a commit — the half the `??` check structurally
cannot see. The baseline was taken before any deliverable existed and lives
**outside** the repo, so the measuring instrument is not a member of the set it
measures.

### D2 — three defects found by T3, all fixed, none a number

1. **A command was quoted in an abbreviated form that was never run** (§5's
   freeze-heading grep). Corrected to the exact command. A quoted command that
   was never run is a number with no provenance even when the number is right.
2. **My own coverage probe was wrong and would have FAILED a correct artifact** —
   it deleted the `<path>` operand, producing probe strings that never existed.
   Fixed to substitute a concrete instance. Reported rather than quietly re-run:
   a check that fails a correct artifact is as dangerous as one that passes a
   wrong one.
3. **The `⚠ UNTRACEABLE` flag token was used inside its own negation** ("No ⚠
   UNTRACEABLE commit"), so a `grep -c` audit returned **6** where the true
   callout count was **0**. The token is now reserved for real callouts.

### D3 — an instrumentation defect in T1, recorded rather than overwritten

The first `DEC-2026-08-06-sr4-freeze-scope` extraction anchored on
`^## DEC-...` while the real heading is `## 2026-08-06 — DEC-...`. It matched
nothing and printed an **empty fenced block with `rc=0`** — a silent empty
result wearing a success code, which is precisely the failure class this task
exists to catch. **Both the defect and the corrected extraction are in
EVIDENCE.md**; the bad block was not deleted.

### D4 — the freeze-word scan is loose ON PURPOSE, and its hits were READ

Matching any line carrying both a basename and `frozen|freeze|pinned|pin`
over-matches — the conservative direction for a *"was it EVER declared frozen?"*
question, since it makes a hit **easier** and a null **stronger**. But loose
matching means hits must be read: `e3075ae`'s F2 hit is a **test** pinning a
return type, and `262ff12`'s F4 hit (2026-06-19) is a work description. Reporting
those raw dates as freeze-label dates would have been a **false finding**. Both
are named and discarded in the dossier.

## 8. WHAT THIS DOES **NOT** COVER — limits, not coverage

- **No correctness review of the drift.** Nobody read the `+46 / -8` or the
  `+313 / -62` for correctness. `NEVER-FROZEN` says **nothing** about whether
  those changes were good.
- **First-appearance dates are LOWER BOUNDS** (68 unreadable revisions).
- **No claim about whether any NUMBER moved** — source-text facts only.
- **`results/` was never searched** (symlinked into `/rs1`; contains none of
  these paths). Every search was scoped to `.planning/ src/ tests/ config/`.
- **T3 re-derived every number**, but did not re-read the 13 provenance hits'
  prose or re-walk the 444 narrative revisions.

## 9. ⚠ THE DISPOSITION REMAINS CARTER'S AND WAS **NOT** RECORDED

**SR4-OPEN is still OPEN.** No entry was written to `.planning/DECISIONS.md`; no
`HANDOFF.json` field was changed; no file was described as frozen or un-frozen
anywhere. The dossier presents both branches with their concrete operational
consequences and presents gating as **costed options, never as a recommendation
to act**. Recording the answer is a future task.

Per hard rule, this executor wrote **none** of `.planning/STATE.md`,
`.planning/HANDOFF.json`, `.planning/DECISIONS.md`, `.continue-here.md` or
`ROADMAP.md`.

## 10. COST

**$0. NC State node only. Zero perimeter contact, zero LSF.** No `gsutil` /
`gcloud` / `bq` / `dataproc` / `hailctl` / `wb` was invoked — verified: **0**
command lines in EVIDENCE.md carry any of those tokens (the 10 textual matches
in the diff are all quoted historical prose captured by `git show`, plus this
task's own scope statement listing the forbidden tokens).

---

## Verification

| # | Clause | Result |
|---|---|---|
| 1 | `pytest tests/m3/test_source_freeze_pins.py -q` | **39 passed** (read, never changed) |
| 2 | `git status --porcelain \| grep -v '^??'` | **empty** |
| 3 | control `git diff --numstat bf16289 HEAD -- C1 C2 C3` | **empty** |
| 4 | three deliverables exist in the quick dir | ✅ |
| 5 | `git diff --name-only b945c595 HEAD -- src/ tests/ config/ DECISIONS HANDOFF STATE ROADMAP` | **empty** |
| 6 | tracked delta == exactly the 3 deliverables | ✅ (n=3) |
| 7 | TSV: 14 cols, 5 data rows, 0 blank cells, closed vocabulary | ✅ |
| 8 | 21/21 commands quoted in the dossier present in EVIDENCE.md | ✅ |
| 9 | dossier ↔ TSV row-for-row agreement | ✅ 5/5 |
| 10 | discrepancies after fixes | **0** |

## Self-Check: PASSED

- `260811-pmv-EVIDENCE.md` (2,419 lines), `260811-pmv-evidence.tsv` (6 lines),
  `260811-pmv-DOSSIER.md` (672 lines) — all present.
- Commits `f78bbc1`, `399c50f`, `2b13dce` — all present in `git log --oneline`.
- Zero modified tracked files; tracked delta is exactly the three deliverables.
