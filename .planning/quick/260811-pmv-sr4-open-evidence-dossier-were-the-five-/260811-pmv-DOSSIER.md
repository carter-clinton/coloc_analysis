# SR4-OPEN — the evidence dossier

**Were the five files this project called "frozen" FROZEN-AND-DRIFTED, or were
they NEVER ACTUALLY FROZEN?**

Everything below is measured. Every number cites the command that produced it,
and that command's verbatim output lives in
[`260811-pmv-EVIDENCE.md`](260811-pmv-EVIDENCE.md). The machine-readable form of
the summary table is [`260811-pmv-evidence.tsv`](260811-pmv-evidence.tsv).

---

## §0 — SCOPE. Read this before any finding.

> This dossier is **git-history and declaration evidence**. It establishes what
> changed, when, under which task, and whether anything ever declared these
> files frozen. It is **NOT a code review of whether the drift is correct** — no
> reviewer read the `+46 / -8` or the `+313 / -62` for correctness here, and a
> `NEVER-FROZEN` verdict says **nothing** about whether those changes were good.
> **The disposition is Carter's; this document does not record it.**

**Measurement frame.**

- **HEAD** `b945c595`, branch `m3-W2-aou-deltas`, measured **2026-08-11**
  (`git rev-parse HEAD`, `date -u` — EVIDENCE.md STEP 0).
- **`results/` was never searched.** It and `results/legacy/` are symlinks into
  `/rs1` which `grep -r` does not follow on this tree, and they contain none of
  the eight subject paths. Every scoped search is `.planning/ src/ tests/ config/`.
- **Read-only.** No `src/`, `tests/`, `config/`, `DECISIONS.md`, `HANDOFF.json`
  or `STATE.md` file was written. `$0`, no perimeter contact.
- **⚠ `git log -S` is banned as a primary method here.** It reads the blob at
  every revision and *aborts the walk* on a missing object — while leaving the
  rows it already emitted on stdout. Reproduced at HEAD: it printed 2 plausible
  rows **and returned `rc=128`** (EVIDENCE.md STEP 5b). All history walks below
  use a presence-checked per-revision loop instead.

---

## §1 — THE QUESTION, verbatim

From `.planning/HANDOFF.json:118` (`grep -n 'SR4-OPEN' .planning/HANDOFF.json`):

> ▶ SR4-OPEN (a QUESTION, not a blocker) — FIVE files the project has been
> calling "frozen" were never enforced by anything AND have drifted:
> occlusion_manifest.py (+46/-8), occlusion_present_rate_scan.py (+154/-21),
> drop_occluded_from_sumstats.py (+97/-24), ld_npz_to_rds.R (+313/-62),
> pipeline.schema.yaml (+119/-0). Were they frozen-and-drifted (in which case the
> drift needs review) or never actually frozen (in which case the handoff
> language was wrong)? Nothing is blocked on the answer; the 3
> genuinely-0-diff files are now gated for real.

From `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md:989` onward
(`sed -n '989,1035p'`):

> **THE QUESTION FOR CARTER — not answered here.** For each of the five: were
> they **frozen and have since drifted** (in which case something was changed
> that should not have been, and the drift needs review), or were they **never
> actually frozen** (in which case `HANDOFF.json:14` should be corrected and
> they should stop being described as pinned)? These are different problems with
> different remedies, and choosing between them is a call about intent that no
> agent can make from the diff alone.

---

## §2 — SUMMARY TABLE

| file | diff vs `bf16289` TODAY | same as sr4-era? | # commits since `bf16289` | all traceable? | freeze declaration in `DECISIONS.md`? | gated today? | recommendation |
|---|---|---|---|---|---|---|---|
| `src/python/occlusion_manifest.py` | `+46 / -8` | **yes — identical** | 2 | **yes** (2/2) | **NO — measured zero** | no | **NEVER-FROZEN** |
| `src/python/occlusion_present_rate_scan.py` | `+154 / -21` | **yes — identical** | 3 | **yes** (3/3) | **NO — measured zero** | no | **NEVER-FROZEN** |
| `src/python/drop_occluded_from_sumstats.py` | `+97 / -24` | **yes — identical** | 2 | **yes** (2/2) | **NO — measured zero** | no | **NEVER-FROZEN** |
| `src/scripts/ld_npz_to_rds.R` | `+313 / -62` | **yes — identical** | 1 | **yes** (1/1) | **NO — measured zero** | no | **NEVER-FROZEN** |
| `src/snakemake/schemas/pipeline.schema.yaml` | `+119 / -0` | **yes — identical** | 5 | **yes** (5/5) | **NO — measured zero** | no | **NEVER-FROZEN** |

- **Diff column:** `git diff --numstat bf16289 HEAD -- <path>` (EVIDENCE.md STEP 2).
- **Commit-count column:** `git log --format='%h' bf16289..HEAD -- <path> | wc -l`
  (EVIDENCE.md STEP 3). Every one of those five walks returned **`rc=0`** — no
  history was truncated by a missing object.
- **"gated today" = no** for all five, and it is not an omission: it is
  **asserted** by `test_the_handoff_frozen_claim_is_recorded_as_partly_false` in
  `tests/m3/test_source_freeze_pins.py`.
- **"same as sr4-era"** compares today's numstat against the sr4 SUMMARY §2
  table (2026-08-06). **Nothing has moved in the five days since.**

This table is `260811-pmv-evidence.tsv` rendered; §T3 asserts they agree
row-for-row.

---

## §3 — THE CONTROL. This is why "these five moved" is a measurement, not a story.

`git diff --numstat bf16289 HEAD -- <path>` on the three files sr4 gated for
real (EVIDENCE.md STEP 2):

| file | diff vs `bf16289` TODAY |
|---|---|
| `src/python/plink_ld_to_npz.py` | `+0 / -0` (empty output, `rc=0`) |
| `src/python/condition_ld_matrix.py` | `+0 / -0` (empty output, `rc=0`) |
| `src/python/occlusion_span_filter.py` | `+0 / -0` (empty output, `rc=0`) |

Also run as one command over all three: **empty**, `rc=0`.

**The control HOLDS.** The same command, against the same pin, on the same day,
returns **empty for three files and non-empty for five**. That is what makes the
five a measurement rather than a narrative — the instrument demonstrably can
return "no drift", so "drift" is a fact about those files and not about the
method. Had any of C1–C3 come back non-empty,
`test_the_handoff_frozen_claim_is_recorded_as_partly_false` would have changed
meaning and this dossier would say so loudly. It did not.

---

## §3b — ⚠ WHAT `bf16289` ACTUALLY IS

This is not trivia; it is the load-bearing fact of the whole question.

```
$ git log -1 --format='%H%n%ad%n%s' bf16289
bf16289dacaa67c978977d378b132e73ac9adb69
Thu Jul 16 01:44:30 2026 -0400
docs(handoff): 2026-07-16 close-session — m3-07 CODE-COMPLETE; unambiguous resume point

$ git show --stat --oneline --format='' bf16289
 .../m3-aou-afr-ld-panel-build/.continue-here.md    | 22 +++++++++++++++++++---
 1 file changed, 19 insertions(+), 3 deletions(-)
```

**`bf16289` is a session-close handoff commit that changed exactly ONE file — a
planning narrative file — and touched NONE of the eight files it supposedly
froze.** Measured per file with
`git show --name-only --format='' bf16289 | grep -c '<path>'` → **0 for all five
subjects and 0 for all three controls** (EVIDENCE.md STEP 1).

It is not a freeze commit. It is the SHA of the handoff that happened to be HEAD
when someone wrote down a list of files that were, at that moment, unchanged.

---

## §4 — PER-FILE EVIDENCE

### F1 — `src/python/occlusion_manifest.py`

**1. Drift today.** `git diff --numstat bf16289 HEAD -- src/python/occlusion_manifest.py`
→ `46	8	src/python/occlusion_manifest.py`, `rc=0`. Rendered: **`+46 / -8`**.
Identical to the sr4-era figure.

**2. Commit history.** `git log --format='%h|%ad|%an|%s' --date=short bf16289..HEAD -- <path>`, `rc=0`:

| short SHA | date | subject |
|---|---|---|
| `bf963df` | 2026-08-04 | `feat(260804-rtc-T2)`: unparseable counters (HIGH-4) + a total-miss guard that can fire (HIGH-0) |
| `3bb8783` | 2026-08-04 | `fix(260804-rtc-T1)`: ONE shared integral-position coercion + canonical key (D-04b-01) |

Provenance (EVIDENCE.md STEP 4):

- `bf963df` → token `260804-rtc` → `.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo`
  → SHA named **1×** in `260804-rtc-SUMMARY.md:64`. **TRACEABLE.**
- `3bb8783` → same artifact → SHA named **1×** in `260804-rtc-SUMMARY.md:63`. **TRACEABLE.**

**No untraceable commit. 2/2 traceable.**

**3. Freeze declaration.** `grep -c 'occlusion_manifest.py' .planning/DECISIONS.md`
→ **`0`** (`rc=1`). **A measured zero, not an assumption.** The register's only
freeze entry — `DEC-2026-08-06-sr4-freeze-scope` at line 1039 — names only
`run_susie_rss.R` (at `bf04199`) and C1/C2/C3 (at `bf16289`); `grep -c` for this
basename *inside that entry* is also **0**.

Narrative trail: earliest **READABLE** revision carrying a genuine freeze claim
that names this file is **`2bda675`, 2026-08-03**, and it names it only inside a
**COLLECTIVE** roster:

> All 7 pinned files 0-line diff vs bf16289: the 4 m3-07 modules
> (occlusion_span_filter, occlusion_manifest, occlusion_present_rate_scan,
> drop_occluded_from_sumstats) + the 3 frozen contracts (plink_ld_to_npz.py,
> ld_npz_to_rds.R, condition_ld_matrix.py).

⚠ **LOWER BOUND** — 17 revisions of `HANDOFF.json`, 29 of `STATE.md` and 22 of
`.continue-here.md` were unreadable, and the unreadable set skews old.

**4. Gated today.** **No** — asserted OUT by
`test_the_handoff_frozen_claim_is_recorded_as_partly_false`.

**5. Recommendation: `NEVER-FROZEN`.** No register declaration exists, `bf16289`
was enforced by zero tests at both drift commits, and both commits trace to a
reviewed SUMMARY that names their SHAs.

---

### F2 — `src/python/occlusion_present_rate_scan.py`

**1. Drift today.** `git diff --numstat bf16289 HEAD -- <path>` → `154	21`,
`rc=0`. Rendered: **`+154 / -21`**. Identical to the sr4-era figure.

**2. Commit history.** `rc=0`:

| short SHA | date | subject |
|---|---|---|
| `fac9a93` | 2026-08-04 | `feat(260804-rtc-T3)`: region-coverage assertion (BLOCKER-4), LOW-1 visibility, measured k/n |
| `bf963df` | 2026-08-04 | `feat(260804-rtc-T2)`: unparseable counters (HIGH-4) + a total-miss guard that can fire (HIGH-0) |
| `3bb8783` | 2026-08-04 | `fix(260804-rtc-T1)`: ONE shared integral-position coercion + canonical key (D-04b-01) |

All three → token `260804-rtc` → the same artifact dir; SHAs named at
`260804-rtc-SUMMARY.md:65`, `:64`, `:63` respectively (1 hit each).
**No untraceable commit. 3/3 traceable.**

**3. Freeze declaration.** `grep -c` in `DECISIONS.md` → **`0`**. Narrative:
same `2bda675` COLLECTIVE roster, 2026-08-03 (⚠ **LOWER BOUND**).

⚠ The loose scan also flagged `e3075ae` (2026-07-15) for this file, but reading
the line shows it is a **false positive**: *"`test_occlusion_present_rate_scan.py:79-84`
**pins** `scan_present_rate` to return a dict keyed by a (chr, pos) TUPLE"* — a
test pinning a **return type**, not a freeze. Not reported as a freeze date.

**4. Gated today.** **No** — asserted OUT by
`test_the_handoff_frozen_claim_is_recorded_as_partly_false`.

**5. Recommendation: `NEVER-FROZEN`.** Same basis as F1: zero register
declaration, zero enforcement at drift time, 3/3 drift commits traceable.

---

### F3 — `src/python/drop_occluded_from_sumstats.py`

**1. Drift today.** `git diff --numstat bf16289 HEAD -- <path>` → `97	24`,
`rc=0`. Rendered: **`+97 / -24`**. Identical to the sr4-era figure.

**2. Commit history.** `rc=0`:

| short SHA | date | subject |
|---|---|---|
| `bf963df` | 2026-08-04 | `feat(260804-rtc-T2)`: unparseable counters (HIGH-4) + a total-miss guard that can fire (HIGH-0) |
| `3bb8783` | 2026-08-04 | `fix(260804-rtc-T1)`: ONE shared integral-position coercion + canonical key (D-04b-01) |

Both → `260804-rtc` artifact; SHAs named at `260804-rtc-SUMMARY.md:64` and `:63`.
**No untraceable commit. 2/2 traceable.**

**3. Freeze declaration.** `grep -c` in `DECISIONS.md` → **`0`**. Narrative:
same `2bda675` COLLECTIVE roster, 2026-08-03 (⚠ **LOWER BOUND**).

**4. Gated today.** **No** — asserted OUT by
`test_the_handoff_frozen_claim_is_recorded_as_partly_false`.

**5. Recommendation: `NEVER-FROZEN`.** Zero register declaration, zero
enforcement at drift time, 2/2 traceable.

---

### F4 — `src/scripts/ld_npz_to_rds.R`

**1. Drift today.** `git diff --numstat bf16289 HEAD -- <path>` → `313	62`,
`rc=0`. Rendered: **`+313 / -62`** — the largest drift of the five. Identical to
the sr4-era figure.

**2. Commit history.** `rc=0`:

| short SHA | date | subject |
|---|---|---|
| `57b381f` | 2026-08-05 | `feat(260805-23d-T5)`: drop the dense ld field, bound the converter read (BLOCKER-D, PARTIAL) |

Provenance: token `260805-23d` →
`.planning/quick/260805-23d-m3-04c-blast-radius-remediation-eur-tran` → SHA named
**2×** in `260805-23d-SUMMARY.md` (`:147` the per-task table, `:345` an explicit
"all 8 referenced commits resolve" check). **TRACEABLE.**

**No untraceable commit. 1/1 traceable.** ⚠ Note the asymmetry: this is the
**biggest** drift of the five and the **best**-documented — one commit, named
twice, in a SUMMARY that independently re-verified its own commit references.

**3. Freeze declaration.** `grep -c 'ld_npz_to_rds.R' .planning/DECISIONS.md`
→ **`0`**. Narrative: named individually inside the `2bda675` COLLECTIVE roster
(as one of "the 3 frozen contracts"), 2026-08-03 (⚠ **LOWER BOUND**).

⚠ The loose scan flagged `262ff12` (2026-06-19) for this file — a **false
positive**: an m3-02b work description mentioning the file on a line that also
carries a freeze word. Not a freeze claim, not reported as a freeze date.

**4. Gated today.** **No** — asserted OUT by
`test_the_handoff_frozen_claim_is_recorded_as_partly_false`.

**5. Recommendation: `NEVER-FROZEN`.** Zero register declaration, zero
enforcement at drift time, 1/1 traceable.

---

### F5 — `src/snakemake/schemas/pipeline.schema.yaml`

**1. Drift today.** `git diff --numstat bf16289 HEAD -- <path>` → `119	0`,
`rc=0`. Rendered: **`+119 / -0`** — pure addition, nothing deleted. Identical to
the sr4-era figure.

**2. Commit history.** `rc=0` — **five** commits, the most of any subject:

| short SHA | date | subject |
|---|---|---|
| `2563451` | 2026-08-06 | `feat(260805-w7u-T1)`: route the coloc LD path through the resolver; make the manifest fail loudly (FINDING E) |
| `64f420a` | 2026-08-05 | `feat(260805-o7o-T2)`: AFR-gated allele-aware join, z orientation flip, counted JSON (FINDING H, wiring half) |
| `57b381f` | 2026-08-05 | `feat(260805-23d-T5)`: drop the dense ld field, bound the converter read (BLOCKER-D, PARTIAL) |
| `aeed8c0` | 2026-08-05 | `feat(260805-23d-T1)`: ancestry-gate the LD read path (BLOCKER-B, half 1 of 2) |
| `d7dfa67` | 2026-08-03 | `feat(m3-04b-T1)`: genome-wide occlusion catalog assembler + Snakemake rule |

Provenance (all named in a reviewed artifact):

- `2563451` → `260805-w7u` dir → **2 hits** (`260805-w7u-SUMMARY.md:77`, `:837`).
- `64f420a` → `260805-o7o` dir → **2 hits** (`260805-o7o-VERIFICATION.md:17`, `260805-o7o-SUMMARY.md:67`).
- `57b381f` → `260805-23d` dir → **2 hits** (`:147`, `:345`).
- `aeed8c0` → `260805-23d` dir → **3 hits** (`:143`, `:282`, `:345`).
- `d7dfa67` → `.planning/phases/m3-aou-afr-ld-panel-build/` → **6 hits** across
  `m3-04b-W4-SUMMARY.md`, `.continue-here.md`, `m3-04b-BLAST-RADIUS.md`.

**No untraceable commit. 5/5 traceable.**

**3. Freeze declaration.** `grep -c 'pipeline.schema.yaml' .planning/DECISIONS.md`
→ **`0`**.

⚠ **F5 is the weakest case of the five, in two independent ways, and both matter:**

- **It was never in the "7 pinned files" roster at all.** That roster is 4 m3-07
  modules + 3 frozen contracts; `pipeline.schema.yaml` is none of them. The
  SR4-OPEN premise *"files the project has been calling frozen"* is thinnest here.
- **Its only individual freeze label POSTDATES all of its drift.** That label is
  the `HANDOFF.json` `freeze_state` field at `63453db` (2026-08-06): *"Six frozen
  Python modules + src/snakemake/schemas/pipeline.schema.yaml all 0-diff."*
  `git merge-base --is-ancestor 2563451 63453db` → **true**: its last drift
  commit **precedes** that label.

Narrative first-appearance therefore recorded as **`63453db` 2026-08-06 (⚠ LOWER
BOUND)**, with the explicit note that it postdates the drift.

**4. Gated today.** **No** — asserted OUT by
`test_the_handoff_frozen_claim_is_recorded_as_partly_false`.

**5. Recommendation: `NEVER-FROZEN`.** Zero register declaration, zero
enforcement at drift time, 5/5 traceable. ⚠ Had its label been a `DECISIONS.md`
declaration rather than handoff prose, the date-order rule would have returned
`NEVER-FROZEN-UNTIL-DECLARED` instead — the shape is the same: **F5 was called
frozen only after it stopped moving, so there is nothing to review.**

---

## §5 — WHAT THE EVIDENCE SUPPORTS

**The evidence supports `NEVER ACTUALLY FROZEN` for all five.** Four
independent measurements agree, and none contradicts:

**1. `bf16289` is not a freeze commit.** It is a `docs(handoff)` session-close
commit that changed **one** file — `.continue-here.md`, +19/−3 — and touched
**none** of the eight (§3b, measured per path). A pin that never touched what it
pinned was never an act of freezing; it was a bookmark.

**2. The freeze convention did not exist in the register until after all the
drift.** `DEC-2026-08-06-sr4-freeze-scope` (2026-08-06) is the **only** freeze
entry in `DECISIONS.md` other than the unrelated 2026-05-03 aggregator lock
(`grep -n '^## .*freeze\|^## .*froz\|^## .*pin\|^## .*Freeze\|^## .*Pin' .planning/DECISIONS.md` → 3 headings, EVIDENCE.md STEP 5a). That
entry says so about itself, and our own measurements confirm both of its claims:

> Before this, `bf16289` was enforced by **zero** tests anywhere in the repository.

> What existed **nowhere** was the **FREEZE convention** itself — no
> `DECISIONS.md` entry, and `bf16289` enforced by zero tests.

Checked independently, **at the drift commits themselves** rather than inferred:
`git grep -c 'bf16289' <commit> -- tests/ src/ config/ Snakefile` returned
**zero matching files at every one of the 8 drift commits** (EVIDENCE.md STEP
5d). Today it appears in exactly one place — `tests/m3/test_source_freeze_pins.py`
— and in **zero** places under `src/` or `config/`.

**3. Every drift commit is reviewed work.** All 8 distinct commits satisfy both
halves of traceability: the task token resolves to a real artifact directory
**and** the commit's short SHA is named inside that artifact (13 grep hits
total, EVIDENCE.md STEP 4). **There are no untraceable commits, so no file is
forced to `DRIFT-NEEDS-REVIEW`.** Every one of these changes landed under a
planned, executed and summarised GSD task — `260804-rtc`, `260805-23d`,
`260805-o7o`, `260805-w7u`, `m3-04b` — each closing a named blast-radius finding.

**4. The label was COLLECTIVE, and it was a status report, not a prohibition.**
The five were never declared frozen individually. Four of them (F1–F4) appear
only inside one sentence — *"All 7 pinned files 0-line diff vs bf16289: ..."* —
whose grammatical content is an **observation that they were currently
unchanged**, not an instruction that they must not change. F5 was not in that
roster at all.

### ⚠ The one fact that cuts the other way — stated, not buried

**For F1–F4 that collective label existed BEFORE the drift.** `2bda675` is dated
2026-08-03 and `git merge-base --is-ancestor` confirms it **precedes** `3bb8783`,
`bf963df`, `fac9a93` and `57b381f` (EVIDENCE.md, ORDERING section). So it is not
true that nobody had written anything about these files before they moved.
Something had been written, it predated the drift, and the files moved anyway.

Three things bound how much weight that carries, and Carter should weigh them
himself:

- it is a **status report** (*"0-line diff"*), not a **freeze instruction**;
- it lives in a **handoff narrative**, not in the decision register, and this
  project has already baked the rule that an invariant with no named enforcer is
  a belief (`[[feedback_a_claimed_invariant_needs_a_named_enforcer]]`);
- it was enforced by **literally nothing** — measured zero at each drift commit.

(For F5 the ordering runs the other way: `d7dfa67` **predates** `2bda675`, and
F5's own label postdates all its drift.)

### ⚠ Does the evidence contradict the expected "never actually frozen" reading?

**No — but the pre-drift collective label above is genuine contrary evidence and
is reported as such rather than smoothed over.** No file carries an untraceable
drift commit; no history walk was truncated; no register declaration exists for
any of the five. The reading the plan expected is the reading the evidence
supports, and the one fact that pulls against it has been given its own
subsection instead of being averaged into a tidy verdict.

---

## §6 — CARTER'S DECISION

**The disposition is yours. This section states what each answer implies
operationally; it does not choose.**

### If you answer FROZEN-AND-DRIFTED

The review set is exactly these commits — **8 distinct commits across 5 tasks**:

| file | commits to review |
|---|---|
| `src/python/occlusion_manifest.py` | `bf963df`, `3bb8783` |
| `src/python/occlusion_present_rate_scan.py` | `fac9a93`, `bf963df`, `3bb8783` |
| `src/python/drop_occluded_from_sumstats.py` | `bf963df`, `3bb8783` |
| `src/scripts/ld_npz_to_rds.R` | `57b381f` |
| `src/snakemake/schemas/pipeline.schema.yaml` | `2563451`, `64f420a`, `57b381f`, `aeed8c0`, `d7dfa67` |

Deduplicated: `3bb8783`, `bf963df`, `fac9a93`, `aeed8c0`, `57b381f`, `64f420a`,
`2563451`, `d7dfa67`. Reviewing them means reading **8 commits across 5 tasks**
(`260804-rtc`, `260805-23d`, `260805-o7o`, `260805-w7u`, `m3-04b`). **Every one
is already covered by a task SUMMARY that names its SHA** — that is precisely how
this dossier established traceability — so this is a re-read of reviewed work,
not an archaeology dig.

⚠ If you take this branch, note that F5's drift is the least defensible
candidate for review: it was never in the pinned roster, and its label postdates
its drift, so there is no window in which changing it violated anything.

### If you answer NEVER-FROZEN

The remedy is a **language correction**, and most of it has already landed:
`HANDOFF.json:18` already carries the explicit retraction (*"the earlier claim
'All 7 pinned files 0-line diff vs bf16289' is FALSE ... Do not repeat the
retracted claim"*), and `STATE.md:39` carries the same.

The residual work is to stop describing these five as pinned **elsewhere**. The
scoped search (EVIDENCE.md STEP 5c) separates **live current-state assertions**
from **dated historical `>` blocks** — the latter correctly describe what was
believed when written and are **not** correction sites. Classified mechanically
by the `>` prefix, the live sites are:

| site | current text | why it is wrong |
|---|---|---|
| `.planning/STATE.md:15` | `# Frozen contracts byte-unchanged (plink_ld_to_npz.py / ld_npz_to_rds.R / condition_ld_matrix.py all git-diff EMPTY).` | **FALSE for `ld_npz_to_rds.R`** — it is `+313 / -62`. Sits in the live frontmatter comment block (self-labelled 2026-07-15 and deferring to "the LATEST block below", but not inside a `>` block). |
| `.planning/ROADMAP.md:1077` | `panel .npz contract frozen (ld_npz_to_rds.R unchanged).` | **FALSE** — `ld_npz_to_rds.R` is `+313 / -62`. |
| `.planning/HANDOFF.json:124` | `freeze_state` — currently describes the rescoped CODE pin | ✅ already correct; listed only so the sweep is complete. |

**These are the exact sites; a follow-up task is scoped, not searched for.**
Nothing was edited here — this is a read-only investigation.

⚠ Historical `>` blocks that also carry the stale claim (`STATE.md:266`, `:278`,
`:297`, `:301`, `:311`, `:349`, `:362`; `.continue-here.md:57`, `:113`, `:205`,
`:217`, `:233`, `:249`, `:252`) were classified **HISTORICAL** and are
deliberately **not** listed as correction sites. Rewriting history blocks would
destroy the record this dossier depends on.

### Should any of the five now be GATED? — a costed decision surface, not a recommendation

**No recommendation is made here.** The costs, all derived from EVIDENCE.md STEP 6:

| requirement | cost | applies to |
|---|---|---|
| A **RECORDED Carter decision** first | `PY_FROZEN_RELS`'s own `#:` comment: *"Adding a file here requires a RECORDED DECISION that it is frozen, not an inference."* | all five |
| A pin constant carrying a `#:` **bucket annotation** | the repo-wide `test_every_pin_constant_declares_its_bucket` gate enforces this | all five |
| A **negative control observed RED** | `[[feedback_green_assertion_needs_a_negative_control]]` — green is evidence only if you have seen it fail | all five |
| ⚠ **`test_the_handoff_frozen_claim_is_recorded_as_partly_false` goes RED** | see below | **any** file added |
| ⚠ **A YAML code-stripper that does not exist** | `source_freeze.py` supports `LANG_R` and `LANG_PY` only (`grep -c -i 'yaml'` → **0**); sr4 declined to build it | **F5 only** |
| `LANG_R` covers it mechanically | F4 is R — no new stripper needed | **F4 only** |

⚠ **The concrete, checkable cost.** Adding any of the five to `PY_FROZEN_RELS`
makes this assertion fail — it is the *first* assertion in the loop:

```python
for rel in MOVED_SINCE_PY_CODE_REF:
    assert rel not in PY_FROZEN_RELS, (
        f"{rel} has MOVED since {PY_CODE_REF} and must not be gated against "
        "it -- declaring a moving file frozen is a DECISION for Carter, not "
        "an inference (see deferred-items.md)"
    )
```

and the second assertion in the same loop requires each of the five to still
have a **non-empty** numstat vs `bf16289`, so the finding cannot silently rot
either. The live gate is **green today**:
`pytest tests/m3/test_source_freeze_pins.py -q` → **39 passed in 1.26s**.

**A note on what gating would and would not buy.** A pin at `bf16289` is not
available for these five — they have moved, so it would be red at birth. Gating
would mean pinning them at a **new** SHA (today's HEAD), which is a different and
weaker claim than the one the handoff made: not *"these have not changed since
the freeze"* but *"these must not change from here."* That is a legitimate thing
to want and a legitimate thing to decline; it is your call, and it is
independent of the SR4-OPEN answer.

---

## §7 — LIMITS. What this dossier does NOT establish.

- **No correctness review of the drift.** Nobody read the `+46 / -8` or the
  `+313 / -62` to judge whether the changes were right. `NEVER-FROZEN` is a
  statement about **process and intent**, not about code quality.
- **The narrative first-appearance dates are LOWER BOUNDS.** 17 revisions of
  `HANDOFF.json`, 29 of `STATE.md` and 22 of `.continue-here.md` could not be
  read (missing loose git objects — a known recurring GPFS failure). The
  unreadable set skews **old**, which is exactly where an earlier freeze label
  would live. An earlier label may exist and be unrecoverable.
- **No object recovery was attempted.** That is a repo-repair task, not this one.
  All unreadable SHAs are listed in EVIDENCE.md's `OBJECT-STORE CENSUS`.
- **No claim about whether any NUMBER moved.** These are **source-text facts
  only**. Whether the drift changed any Track A or AFR result is a question only
  the AoU perimeter and the ~11-day billed fire can answer, and nothing here
  touches it.
- **`results/` was never searched** (symlinked into `/rs1`; contains none of
  these paths).
- **The freeze-word scan is line-level and loose.** It over-matches by design;
  false positives were read and discarded individually (§4 F2, F4), but a freeze
  claim split across two lines of a narrative file could have been missed.
- **This dossier records no disposition.** SR4-OPEN remains open.

---

## Reproduction log

`[[feedback_a_count_is_a_claim_scope_and_reconcile]]` was baked by a figure that
shipped a count wrong **three times** and was self-inconsistent with numbers in
its own paragraph. This section is the guard against repeating that here: every
number above was re-derived from a freshly re-run command, not re-read.

**Re-run date:** 2026-08-11. **HEAD at re-run:** `399c50f`.

⚠ **HEAD MOVED since the T1 measurement** (`b945c595` → `f78bbc1` (T1) →
`399c50f` (T2)). Both are docs-only commits inside this quick directory. Rather
than reconcile to a stale tree, **every value below was RE-MEASURED at the
current HEAD.** They all reproduce, which is the expected result — none of the
measured quantities is a function of a docs commit — but it was checked, not
assumed.

### Re-run table

| claim | command | T1 value | T3 re-run value | match? |
|---|---|---|---|---|
| F1 drift | `git diff --numstat bf16289 HEAD -- src/python/occlusion_manifest.py` | `+46 / -8` | `+46 / -8` | ✅ |
| F2 drift | `git diff --numstat bf16289 HEAD -- src/python/occlusion_present_rate_scan.py` | `+154 / -21` | `+154 / -21` | ✅ |
| F3 drift | `git diff --numstat bf16289 HEAD -- src/python/drop_occluded_from_sumstats.py` | `+97 / -24` | `+97 / -24` | ✅ |
| F4 drift | `git diff --numstat bf16289 HEAD -- src/scripts/ld_npz_to_rds.R` | `+313 / -62` | `+313 / -62` | ✅ |
| F5 drift | `git diff --numstat bf16289 HEAD -- src/snakemake/schemas/pipeline.schema.yaml` | `+119 / -0` | `+119 / -0` | ✅ |
| C1 control | `git diff --numstat bf16289 HEAD -- src/python/plink_ld_to_npz.py` | empty | empty | ✅ |
| C2 control | `git diff --numstat bf16289 HEAD -- src/python/condition_ld_matrix.py` | empty | empty | ✅ |
| C3 control | `git diff --numstat bf16289 HEAD -- src/python/occlusion_span_filter.py` | empty | empty | ✅ |
| F1 commits | `git log --oneline bf16289..HEAD -- <path>` | 2, `rc=0` | 2, `rc=0` | ✅ |
| F2 commits | `git log --oneline bf16289..HEAD -- <path>` | 3, `rc=0` | 3, `rc=0` | ✅ |
| F3 commits | `git log --oneline bf16289..HEAD -- <path>` | 2, `rc=0` | 2, `rc=0` | ✅ |
| F4 commits | `git log --oneline bf16289..HEAD -- <path>` | 1, `rc=0` | 1, `rc=0` | ✅ |
| F5 commits | `git log --oneline bf16289..HEAD -- <path>` | 5, `rc=0` | 5, `rc=0` | ✅ |
| F1–F5 declaration | `grep -c '<basename>' .planning/DECISIONS.md` | 0 (all five) | 0 (all five) | ✅ |
| live gate | `pytest tests/m3/test_source_freeze_pins.py -q` | 39 passed | 39 passed | ✅ |
| distinct drift commits | union of the TSV `commit_shas` column | 8 | 8 | ✅ |

**Cross-artifact agreement:** all 5 rows of `260811-pmv-evidence.tsv` agree with
the §2 summary table on every shared column (file, `+ADD / -DEL` pair, commit
count, recommendation), and each file's §4 commit table has exactly as many rows
as its TSV `n_commits_since_bf16289` cell. **5/5 AGREE.**

**Command coverage:** 21 distinct command strings are quoted in this dossier;
**0 are absent from `260811-pmv-EVIDENCE.md`.**

**Internal arithmetic:** TSV rows with `all_traceable=no` = **0**; ⚠ UNTRACEABLE
callouts in this dossier = **0**; match. TSV rows with `gated_today=yes` among
F1–F5 = **0**, which is what the live gate supports (it passes *while* asserting
all five are out of `PY_FROZEN_RELS`).

### Discrepancies found: **3. All three were defects, all three were fixed. None was a number.**

**1. A command quoted here did not exist as quoted.** §5 abbreviated the
freeze-heading search to `grep -n '^## .*freeze\|^## .*pin'`. The command
actually run was
`grep -n '^## .*freeze\|^## .*froz\|^## .*pin\|^## .*Freeze\|^## .*Pin' .planning/DECISIONS.md`.
A quoted command that was never run is a number with no provenance, even when
the number is right. **Resolved by correcting the dossier to the exact command**
— not by relaxing the check.

**2. My own coverage probe was wrong, and would have failed a correct
artifact.** The probe *deleted* the `<path>` operand from placeholder commands,
producing strings like `git log --format='%h' bf16289..HEAD | wc -l` that never
existed anywhere. That is a defect in the **check**, not the artifact.
**Resolved by substituting a concrete instance** for `<path>` / `<commit>`
instead of deleting the operand. Reported rather than quietly re-run, because a
check that fails a correct artifact is exactly as dangerous as one that passes a
wrong one.

**3. The ⚠ UNTRACEABLE flag token was being used inside its own negation.** Five
per-file sections and §5 read *"No ⚠ UNTRACEABLE commit"*, so a `grep -c` for the
flag returned **6** while the true callout count was **0** — a reserved flag
token that appears in negations makes every grep-based audit of this file wrong.
**Resolved by reserving the token for real callouts** (the negations now read
"No untraceable commit"), so the count is meaningful to any future reader. The
arithmetic then reconciled at 0 = 0.

**After the fixes: 0 discrepancies.**

### Object-store miss counts, restated

So a reader of this dossier alone still learns why the first-appearance dates are
lower bounds (full SHA lists in EVIDENCE.md's `OBJECT-STORE CENSUS`):

| narrative file | total revisions | readable | **unreadable** |
|---|---|---|---|
| `.planning/HANDOFF.json` | 76 | 59 | **17** |
| `.planning/STATE.md` | 304 | 275 | **29** |
| `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` | 64 | 42 | **22** |

⚠ **The unreadable set skews OLD, which is exactly where an earlier freeze label
would live.** Every first-appearance date in §4 is therefore a **LOWER BOUND**,
and an earlier label may exist and be unrecoverable. No object recovery was
attempted — that is a repo-repair task, not this one.

### Containment, proven by set difference

```
$ git status --porcelain | grep -v '^??'
(empty — zero modified tracked files)

$ BASE=${TMPDIR:-/tmp}/260811-pmv-untracked-baseline.txt   # 20 paths, taken at T1 STEP 0
$ comm -13 <(sort -u "$BASE") <(git status --porcelain | grep '^??' | cut -c4- | sort -u)
(empty)
```

⚠ **Empty is the correct result here, and the plan's literal expectation of
"exactly the three deliverables" is unsatisfiable at this point — say so rather
than paper over it.** T1 and T2 **committed** the deliverables (the execution
protocol requires a commit per task), so they are tracked and can no longer
appear as `??`. The untracked check therefore proves only that **nothing new was
left lying around**. The half it can no longer see is proven directly, and the
pair is **strictly stronger** than the untracked check alone:

```
$ git diff --name-only b945c595 HEAD
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-EVIDENCE.md
.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-evidence.tsv

CONTAINMENT PROVEN: the tracked delta is EXACTLY the 3 deliverables (n=3)
```

Nothing under `src/`, `tests/`, `config/`, `.planning/DECISIONS.md`,
`.planning/HANDOFF.json` or `.planning/STATE.md` was written. **The baseline was
taken before any deliverable existed and lives OUTSIDE the repo** — the measuring
instrument is not a member of the set it measures.

### What this reconciliation did NOT do

It re-derived every **number**. It did **not** re-verify the 13 provenance grep
hits by re-reading each artifact's prose, and it did **not** re-walk the 444
narrative revisions of the object-store census — those remain as measured in
EVIDENCE.md at `b945c595`.

---

**SR4-OPEN remains OPEN. No disposition is recorded in this document, and none
was written to `.planning/DECISIONS.md`. The call is Carter's.**
