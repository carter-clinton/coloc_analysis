---
phase: quick/260811-pmv
plan: 01
type: execute
wave: 1
depends_on: [quick/260806-sr4]
subsystem: m3-source-freeze
tags: [freeze, provenance, evidence, sr4-open, m3, git-history]
autonomous: true
requirements: [SR4-OPEN]
baseline_rev: 5f2028e
files_modified:
  - .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-EVIDENCE.md
  - .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-evidence.tsv
  - .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md
user_setup: []

must_haves:
  truths:
    - "Carter can open ONE file (260811-pmv-DOSSIER.md) and, for each of the five files, see: the diff vs bf16289 measured TODAY, every commit that produced that drift, which planned/reviewed task each commit belongs to, whether any freeze declaration for that file exists in DECISIONS.md, whether it is gated today, and a per-file recommendation."
    - "Every count, diffstat and commit total quoted in the dossier names the exact command that produced it, and that command's verbatim output exists in 260811-pmv-EVIDENCE.md -- nothing is copied from HANDOFF.json or the sr4 SUMMARY."
    - "Today's diffstats are re-measured at HEAD and reported ALONGSIDE the sr4-era (2026-08-06) numbers, with an explicit statement of whether they differ."
    - "Every commit that touched one of the five since bf16289 is either traced to a named planning artifact that NAMES that commit's SHA, or flagged loudly as UNTRACEABLE -- and an untraceable commit forces that file's recommendation to DRIFT-NEEDS-REVIEW regardless of any other evidence."
    - "The dossier states, per file, whether a freeze declaration exists in DECISIONS.md (citing the entry) or only in handoff/STATE narrative (citing the earliest READABLE commit where the frozen/pinned label attached)."
    - "Missing git objects are REPORTED as a census (how many revisions of each narrative file were unreadable, and their SHAs), never silently skipped, and every narrative first-appearance claim is explicitly scoped as a LOWER BOUND because of them."
    - "The dossier carries an explicit 'Carter's decision' block stating what each answer implies operationally, plus a gate-extension recommendation with its concrete cost per file."
    - "The dossier states its own scope honestly: git-history + declaration evidence, NOT a code review of whether the drift is correct."
    - "Nothing outside the quick directory is written: git status shows zero modified tracked files at the end."
  artifacts:
    - path: ".planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-EVIDENCE.md"
      provides: "The raw evidence log -- every command run, verbatim, with its exit code and unedited output. The dossier's single source of truth."
      contains: "OBJECT-STORE CENSUS"
      min_lines: 120
    - path: ".planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-evidence.tsv"
      provides: "Machine-readable one-row-per-file summary; 14 columns, 5 data rows."
      contains: "recommendation"
    - path: ".planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md"
      provides: "The human-readable dossier: summary table, per-file evidence sections, the honest overall conclusion, and Carter's decision block."
      contains: "Carter's decision"
      min_lines: 150
  key_links:
    - from: "260811-pmv-DOSSIER.md"
      to: "260811-pmv-EVIDENCE.md"
      via: "every quoted number cites the command whose verbatim output lives in EVIDENCE.md"
      pattern: "EVIDENCE\\.md"
    - from: "260811-pmv-DOSSIER.md"
      to: "260811-pmv-evidence.tsv"
      via: "the summary table is the TSV rendered; T3 asserts they agree row-for-row"
      pattern: "evidence\\.tsv"
    - from: "260811-pmv-DOSSIER.md"
      to: ".planning/HANDOFF.json carter_decisions_outstanding SR4-OPEN"
      via: "the dossier answers the SR4-OPEN question verbatim as posed"
      pattern: "SR4-OPEN"
    - from: "260811-pmv-DOSSIER.md"
      to: "tests/m3/test_source_freeze_pins.py"
      via: "gated-today column derived by reading PY_FROZEN_RELS / MOVED_SINCE_PY_CODE_REF and running the gate"
      pattern: "test_source_freeze_pins"
---

<objective>
Assemble the evidence Carter needs to answer **SR4-OPEN**: five files this
project's handoffs called "frozen" were (a) enforced by nothing and (b) have
drifted vs `bf16289`. Were they **FROZEN-AND-DRIFTED** (the drift needs review)
or **NEVER ACTUALLY FROZEN** (the handoff language was wrong)?

Purpose: the question is a call about **intent**, and no agent can make it from
a diff alone. What an agent *can* do is put every fact in one place so the call
takes five minutes instead of an archaeology session. This task builds the
evidence; **the disposition is Carter's and is deliberately NOT recorded here.**

Output: a raw evidence log, a machine-readable TSV, and a dossier.

⚠ **THIS IS A READ-ONLY INVESTIGATION.** The only writes are three markdown/TSV
files inside this quick directory. **NO** source change, **NO** test change,
**NO** new pin implemented, **NO** `DECISIONS.md` edit, **NO** `HANDOFF.json`
edit. Recording Carter's eventual answer is a FUTURE task.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/quick/260806-sr4-replace-whole-file-freeze-pins-with-comm/260806-sr4-SUMMARY.md
@.planning/HANDOFF.json
@tests/m3/test_source_freeze_pins.py
@tests/m3/source_freeze.py

`.planning/DECISIONS.md` — read `DEC-2026-08-06-sr4-freeze-scope` (line ~1039
onward). Do **not** read the whole 1,250-line file; grep it.

<subjects>
THE FIVE (the subjects of SR4-OPEN):
  F1  src/python/occlusion_manifest.py
  F2  src/python/occlusion_present_rate_scan.py
  F3  src/python/drop_occluded_from_sumstats.py
  F4  src/scripts/ld_npz_to_rds.R
  F5  src/snakemake/schemas/pipeline.schema.yaml

THE THREE (the CONTROL — genuinely 0-diff and gated for real since sr4):
  C1  src/python/plink_ld_to_npz.py
  C2  src/python/condition_ld_matrix.py
  C3  src/python/occlusion_span_filter.py

THE PIN: bf16289 — the SHA the handoff claimed pinned all eight.
</subjects>

<what_the_repo_already_asserts>
`tests/m3/test_source_freeze_pins.py` already encodes part of the answer and is
a live gate. Read it rather than re-deriving:

- `PY_FROZEN_RELS` = the three gated files. Its `#:` comment states: *"Adding a
  file here requires a RECORDED DECISION that it is frozen, not an inference."*
- `MOVED_SINCE_PY_CODE_REF` = the five, with the sr4-era diffstats in the `#:`
  block above it.
- `test_the_handoff_frozen_claim_is_recorded_as_partly_false` asserts each of the
  five is **NOT** in `PY_FROZEN_RELS` **and** that each still has a **non-empty**
  numstat vs `bf16289`. ⚠ **That second half means adding any of the five to the
  gate makes this test go RED** — a concrete, checkable cost for the
  gate-extension recommendation in T2. Verify it by reading the test; do not
  take it from this plan.
- `source_freeze.py` supports `LANG_PY` (via `ast`) and `LANG_R` (via a
  length-preserving mask). **There is no YAML support** — the sr4 SUMMARY §7
  says it was deliberately not built. Confirm this by reading the module.
</what_the_repo_already_asserts>

<gpfs_object_loss_WARNING>
⚠⚠ **THE SINGLE BIGGEST TRAP IN THIS TASK, VERIFIED AT PLANNING TIME.**

This tree has lost loose git objects (a known recurring GPFS failure —
`[[reference_gpfs_git_object_store_loss]]`). Measured on 2026-08-11 at `5f2028e`:

```
$ git log -S "bf16289" --oneline --no-decorate -- .planning/HANDOFF.json
fatal: unable to read 8c3b13dbfd13070afe1223c5e34b096b38f4c92d
...but it STILL PRINTED 2 rows to stdout, and rc was 128.
```

**`git log -S` (the pickaxe) reads the BLOB at every revision. On a missing blob
it ABORTS the walk — but the rows it already emitted are still on stdout.** So
`git log -S ... 2>/dev/null` returns a short, plausible, **TRUNCATED** list and
looks like a complete answer. `git log` walks newest→oldest, so what gets cut is
exactly the OLD end — which is exactly where a "when did the frozen label first
attach?" answer lives.

**Therefore:** `git log -S` is **BANNED** as the primary method in this task.
Use the presence-checked per-revision loop in T1 STEP 5. If you run `-S` at all,
you MUST capture and report its rc.

**A count is a claim** (`[[feedback_a_count_is_a_claim_scope_and_reconcile]]`).
Report `readable=N unreadable=M` for every narrative file walked, list the
unreadable SHAs, and scope every first-appearance claim as a **LOWER BOUND**.
Do **NOT** attempt object recovery — that is a repo-repair task, not this one.
</gpfs_object_loss_WARNING>

<grep_discipline>
- `grep -r` does **NOT** follow symlinks on this tree. `results/` and
  `results/legacy/` are symlinks into `/rs1`. **This investigation never touches
  `results/`** — scope every search to `.planning/ src/ tests/ config/` and say so.
- Never `git add -A` / `git add .` on this GPFS tree — explicit paths only.
- Every count in a deliverable names the command that produced it.
</grep_discipline>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Collect the evidence verbatim — raw log + machine-readable TSV</name>
  <files>
    .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-EVIDENCE.md
    .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-evidence.tsv
  </files>
  <action>
Run the protocol below and write **every command and its unedited output** into
`260811-pmv-EVIDENCE.md`, in order, each in a fenced block preceded by the exact
command line and followed by `rc=<exit code>`. **Paste output verbatim — do not
summarise inside EVIDENCE.md.** Interpretation happens in T2, not here.

Then write `260811-pmv-evidence.tsv` (tab-separated, one header row + exactly 5
data rows, one per F1–F5) with EXACTLY these 14 columns:

```
file	diff_add_today	diff_del_today	diff_sr4era	moved_since_sr4	n_commits_since_bf16289	commit_shas	all_traceable	untraceable_shas	decisions_declaration	first_readable_frozen_narrative	unreadable_revisions	gated_today	recommendation
```

`recommendation` uses a CLOSED vocabulary — exactly one of:
`NEVER-FROZEN` | `NEVER-FROZEN-UNTIL-DECLARED` | `FROZEN-AND-DRIFTED` |
`DRIFT-NEEDS-REVIEW`. (`NEVER-FROZEN-UNTIL-DECLARED` exists so STEP 7's
date-order branch has a label it is allowed to emit; a mandated label the verify
rejects is an unsatisfiable spec — `[[feedback_check_plan_against_red_before_executing]]`.)
Use `-` for a genuinely empty cell; never leave a cell blank.

---

**STEP 0 — the frame.** Record, in this order:
`date -u`; `git rev-parse HEAD`; `git status --porcelain`;
`git cat-file -t bf16289` (must print `commit`).

⚠ **The untracked baseline must be PERSISTED, not just pasted.** The tree
already carries ~15 untracked paths that are **NOT yours**, so "only my files are
new" is unprovable without a before-picture. Write it to a **fixed, repo-EXTERNAL
path**, and paste the same list verbatim into EVIDENCE.md:

```bash
BASE=${TMPDIR:-/tmp}/260811-pmv-untracked-baseline.txt
git status --porcelain | grep '^??' | cut -c4- | sort -u > "$BASE"
wc -l "$BASE"          # record this count in EVIDENCE.md
```

⚠ **It lives OUTSIDE the repo deliberately: the measuring instrument must not
be a member of the set it measures.** A baseline file inside the working tree
would itself show up as a new untracked path and make T3's containment assertion
either wrong or self-excusing. Record the absolute `$BASE` path and its line
count in EVIDENCE.md so a reader can tell the baseline was taken at all.

**STEP 1 — what `bf16289` actually IS.** This is evidence, not trivia:
```
git log -1 --format='%H%n%ad%n%s' bf16289
git show --stat --oneline --format='' bf16289 | head -40
```
Then, for each of F1–F5, state whether `bf16289` itself touched that file
(derive it: `git show --name-only --format='' bf16289 | grep -c '<path>'`).
A "freeze SHA" that touches none of the files it supposedly froze is a fact the
dossier must carry.

**STEP 2 — diffstat TODAY, for all EIGHT.** For each of F1–F5 **and** C1–C3:
```
git diff --numstat bf16289 HEAD -- <path>
```
Record the raw line (or the empty output) and rc for each.

⚠ **C1–C3 are a live control, not padding.** They MUST be empty. If any is
non-empty, `test_the_handoff_frozen_claim_is_recorded_as_partly_false` has
changed meaning and that is a **loud finding** for the dossier — record it, do
not smooth it over.

Then populate `diff_sr4era` from the sr4 SUMMARY §2 table and set
`moved_since_sr4` to `yes`/`no` per file by **comparing the two numbers**, not by
assuming. If any file moved since 2026-08-06, say so prominently.

**STEP 3 — the full commit history since the pin.** For each of F1–F5:
```
git log --format='%h|%ad|%an|%s' --date=short bf16289..HEAD -- <path>
```
Capture rc. **If rc != 0 the walk was truncated by a missing object** — record
the fatal line verbatim, mark that file's history INCOMPLETE, and say so in
every downstream claim about it.

**STEP 4 — provenance, per commit.** For every distinct commit SHA found in
STEP 3, establish provenance to a **planned or reviewed** task. A commit is
**TRACEABLE** only if BOTH hold:

  (a) its subject carries a GSD task token (e.g. `260804-rtc-T2`, `260805-23d-T5`,
      `m3-04b-T1`) that resolves to a real artifact directory —
      `ls -d .planning/quick/*<token>*` or a file under
      `.planning/phases/m3-aou-afr-ld-panel-build/`; AND
  (b) **the commit's short SHA is NAMED inside that artifact** —
      `grep -rn "<short-sha>" <artifact-dir-or-file>` returns ≥1 hit.

⚠ (b) is the load-bearing half. A token in a commit subject is a *claim by the
commit author*; the SHA appearing in a SUMMARY/PLAN is *the reviewed record
naming it*. A commit satisfying (a) but not (b) is **NOT** traceable — record it
as `token-only, SHA absent from <artifact>` and treat it as untraceable.

Record per commit: token, artifact path, grep hit count, verdict. Set
`all_traceable` to `yes`/`no` and list any failures in `untraceable_shas`.

**STEP 5 — was a freeze EVER declared? (the decisive evidence)**

5a. **DECISIONS.md — the authoritative register.** For each of F1–F5:
```
grep -c "<basename>" .planning/DECISIONS.md
grep -n  "<basename>" .planning/DECISIONS.md
```
plus `grep -n "bf16289" .planning/DECISIONS.md`. Record the counts verbatim.
**The ABSENCE of an entry is itself the key evidence** — so it must be a
measured zero with its command shown, never an assertion. Also read the
`DEC-2026-08-06-sr4-freeze-scope` entry's "What is pinned" section and record
whether it names any of the five (it is the only freeze entry in the register;
confirm that by grepping for other candidate entries, e.g.
`grep -n "^## .*freeze\|^## .*froz\|^## .*pin" .planning/DECISIONS.md`).

5b. **The narrative record — where the label DID attach.** Walk
`.planning/HANDOFF.json`, `.planning/STATE.md` and (if present)
`.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` with a
**presence-checked per-revision loop**, NOT `git log -S`:

```bash
for c in $(git log --format=%H -- <narrative_path>); do
  b=$(git rev-parse "$c:<narrative_path>" 2>/dev/null)
  if [ -n "$b" ] && git cat-file -e "$b" 2>/dev/null; then
     # READABLE: git show "$c:<narrative_path>" and grep for the basename
     # and for freeze words (frozen|freeze|pinned|pin)
  else
     # UNREADABLE: record "$c" in the miss list
  fi
done
```

For each narrative file record: total revisions, `readable=N`, `unreadable=M`,
and the **full list of unreadable commit SHAs**, under a heading containing the
literal string `OBJECT-STORE CENSUS`. (Measured 2026-08-11 for calibration:
HANDOFF.json 59/76 readable, STATE.md 275/304 readable — **re-measure, do not
copy these**; and the unreadable ones skew OLD, which is precisely why the
first-appearance answer is a lower bound.)

Then, per file F1–F5, record the **earliest READABLE** commit (SHA + date +
subject) in which that basename appears within a freeze/pin claim, and populate
`first_readable_frozen_narrative` as `<sha> <date> (LOWER BOUND)` or `-` if the
label never attached individually. Also note whether the label attached to the
file **individually** or only via a **collective** phrase such as "All 7 pinned
files 0-line diff vs bf16289" — that distinction matters to the answer.

5c. **Anywhere else?** Scoped repo search (never `results/`):
```
grep -rn --include='*.md' --include='*.py' --include='*.R' --include='*.yaml' \
  --include='*.yml' --include='*.smk' --include='*.json' \
  "<basename>" .planning/ src/ tests/ config/ | grep -iE "frozen|freeze|pinned"
```
Record hit counts per file and the distinct source files of the hits (the raw
hit text is large — record counts + file list + up to 5 representative lines per
subject; state that truncation explicitly with the count it was truncated from).

**STEP 6 — gated TODAY?** Read `tests/m3/test_source_freeze_pins.py` and record
verbatim: `PY_CODE_REF`, `PY_FROZEN_RELS`, `MOVED_SINCE_PY_CODE_REF`, and the
body of `test_the_handoff_frozen_claim_is_recorded_as_partly_false`. Then run
the live gate and record its output:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_source_freeze_pins.py -q
```
(≈10 s wall; 39 passed at planning time.) Also record, from
`tests/m3/source_freeze.py`, which languages the utility supports — this bounds
what gating F4 (R) and F5 (YAML) would cost. Set `gated_today` to
`yes` / `no (asserted OUT by <test name>)` per file.

**STEP 7 — derive the recommendation.** Apply this rule mechanically per file
and record the derivation in EVIDENCE.md so T2 transcribes rather than invents:

- ANY commit in STEP 4 untraceable, **OR** the STEP 3 history INCOMPLETE
  (rc != 0) → **`DRIFT-NEEDS-REVIEW`**, naming the offending SHA(s) or the miss.
- ELSE no DECISIONS.md declaration for that file (5a = 0) **AND** `bf16289`
  enforced by zero tests at the time of the drift (STEP 6 + the sr4 finding)
  **AND** all drift traceable → **`NEVER-FROZEN`**.
- ELSE a declaration for that file exists → ⚠ **CHECK THE DATE ORDER BEFORE
  LABELLING IT.** A declaration is **not retroactive**. Compare the declaration's
  date (the `DECISIONS.md` entry heading, corroborated by the commit that landed
  it) against **every** commit date from STEP 3:
    * commits dated **BEFORE** the declaration are **NOT freeze violations** —
      **exclude them from the review set** and note the exclusion with both
      dates, so the exclusion is auditable rather than invisible;
    * if some drift **postdates** the declaration → **`FROZEN-AND-DRIFTED`**, and
      the review set is **only** the post-declaration commits;
    * if **100%** of that file's drift **predates** its only declaration → the
      honest label is **`NEVER-FROZEN-UNTIL-DECLARED`**, **NOT**
      `FROZEN-AND-DRIFTED`, and the dossier **must say so explicitly**: the file
      was declared frozen only after it stopped moving, so **there is nothing to
      review**.
  Labelling pre-declaration drift a violation would manufacture a review set out
  of work that was legitimate when it landed — a false finding, which costs more
  than a missing one here.

**Let the evidence decide.** If a declaration turns up that nobody expected, the
verdict changes — that is the point of running the protocol. ⚠ On the evidence
measured at planning time this branch will **not** fire (STEP 5a returns 0 for
all five). It is written to be **self-correcting anyway**: a rule that is only
right because its hard branch never executes is not a rule.
  </action>
  <verify>
    <automated>D=.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-; test -s $D/260811-pmv-EVIDENCE.md && test -s $D/260811-pmv-evidence.tsv && [ "$(awk 'END{print NR}' $D/260811-pmv-evidence.tsv)" = "6" ] && [ "$(head -1 $D/260811-pmv-evidence.tsv | awk -F'\t' '{print NF}')" = "14" ] && [ "$(awk -F'\t' 'NR>1{print NF}' $D/260811-pmv-evidence.tsv | sort -u)" = "14" ] && grep -q "OBJECT-STORE CENSUS" $D/260811-pmv-EVIDENCE.md && for p in src/python/occlusion_manifest.py src/python/occlusion_present_rate_scan.py src/python/drop_occluded_from_sumstats.py src/scripts/ld_npz_to_rds.R src/snakemake/schemas/pipeline.schema.yaml src/python/plink_ld_to_npz.py; do grep -q "$p" $D/260811-pmv-EVIDENCE.md || exit 1; done && awk -F'\t' 'NR>1 && $14 !~ /^(NEVER-FROZEN|NEVER-FROZEN-UNTIL-DECLARED|FROZEN-AND-DRIFTED|DRIFT-NEEDS-REVIEW)$/{exit 1}' $D/260811-pmv-evidence.tsv && echo T1_OK</automated>
  </verify>
  <done>
EVIDENCE.md contains a verbatim command+output+rc block for every step of the
protocol, including an `OBJECT-STORE CENSUS` section with readable/unreadable
counts and the full unreadable-SHA list for each narrative file walked.
evidence.tsv has a 14-column header, exactly 5 data rows, no blank cells, and a
`recommendation` drawn from the closed vocabulary. All eight paths (five
subjects + three controls) appear in EVIDENCE.md. `git status --porcelain |
grep -v '^??'` is empty.
  </done>
</task>

<task type="auto">
  <name>Task 2: Write the dossier — summary table, per-file evidence, conclusion, Carter's decision block</name>
  <files>
    .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md
  </files>
  <action>
Write `260811-pmv-DOSSIER.md` **entirely from `260811-pmv-EVIDENCE.md`**. If a
number is not in EVIDENCE.md, it does not go in the dossier — go measure it and
add it to EVIDENCE.md first. **Do not copy any figure from `HANDOFF.json` or the
sr4 SUMMARY except where explicitly quoting them as the CLAIM UNDER TEST**, and
label such quotes as claims, not measurements.

Required structure, in this order:

**§0 — SCOPE (first, before any finding).** State plainly:
> This dossier is **git-history and declaration evidence**. It establishes what
> changed, when, under which task, and whether anything ever declared these files
> frozen. It is **NOT a code review of whether the drift is correct** — no
> reviewer read the +46/-8 or the +313/-62 for correctness here, and a
> `NEVER-FROZEN` verdict says nothing about whether those changes were good.
> The disposition is Carter's; this document does not record it.

Also state the measurement frame: HEAD SHA, date, and that `results/` was never
searched (symlinked; irrelevant to these paths).

**§1 — THE QUESTION, verbatim.** Quote SR4-OPEN as posed in
`HANDOFF.json:carter_decisions_outstanding` and in the phase `deferred-items.md`,
so the answer is visibly answering the question actually asked.

**§2 — SUMMARY TABLE.** The TSV rendered as markdown, columns:

| file | diff vs bf16289 TODAY | same as sr4-era? | # commits since bf16289 | all traceable? | freeze declaration in DECISIONS.md? | gated today? | recommendation |

⚠ **The diff column uses EXACTLY this literal rendering: `+ADD / -DEL`** (e.g.
`+46 / -8`), taken from `git diff --numstat`'s two fields. This is not cosmetic:
T3's containment check verifies the *pair*, because a bare `46` would match a
line number, a date or an unrelated count anywhere in the file — a proxy guard,
which is the failure class `[[feedback_scope_a_guard_to_the_property_not_a_proxy]]`
names. Render `0-diff` as the literal `+0 / -0`.

Immediately below the table, one line naming the command behind the diff column
and one naming the command behind the commit-count column.

**§3 — THE CONTROL.** A short subsection reporting C1–C3's measured 0-diff (or
the loud finding if not). Explain why it matters: it is what makes "these five
moved" a *measurement* rather than a story — the same command on the same pin
returns empty for three files and non-empty for five.

**§4 — PER-FILE EVIDENCE.** One `###` section per file F1–F5, each containing:
  1. **Drift today** — the numstat line + its command.
  2. **Commit history** — a table (short SHA | date | subject), then per commit
     the provenance verdict: task token → artifact path → whether the artifact
     NAMES the SHA (grep hit count). Any commit failing either half gets a **⚠
     UNTRACEABLE** callout in bold with its SHA.
  3. **Freeze declaration** — DECISIONS.md hit count (with command) and, if zero,
     say so as a measured zero. Then the narrative trail: earliest READABLE
     commit where the label attached, whether individually or only via the
     collective "All 7 pinned files" phrase, and the ⚠ LOWER BOUND caveat with
     that narrative file's unreadable-revision count.
  4. **Gated today** — yes/no, and if no, the test that asserts it OUT.
  5. **Recommendation** — one of the four closed-vocabulary tokens + **one
     line** of reasoning. If the token is `NEVER-FROZEN-UNTIL-DECLARED`, state
     the declaration date and the latest drift date that precedes it.

**§5 — WHAT THE EVIDENCE SUPPORTS.** The honest overall answer, derived from §4
and nothing else. Address explicitly:
  - whether `bf16289` is a freeze commit or a session-close handoff commit that
    touched none of the five (from T1 STEP 1);
  - whether the freeze convention existed in the register at all before
    `DEC-2026-08-06-sr4-freeze-scope` (that entry states the convention "existed
    nowhere" and that `bf16289` was "enforced by zero tests" — quote it and check
    it against your own measurements);
  - whether the label attached to these files **individually** or only
    **collectively**.
  ⚠ If ANY file carries an untraceable drift commit, that file gets a **loud**
  flagged subsection here — do not let a tidy majority verdict bury it.
  ⚠ If the evidence contradicts the expected "never actually frozen" reading,
  **say so**. The plan does not get to pre-decide the finding.

**§6 — CARTER'S DECISION.** Explicit, operational, and non-directive:
  - **If FROZEN-AND-DRIFTED** → the review set is exactly these commits: [list,
    per file, from §4]. Name what reviewing them would mean (reading N commits
    across M tasks) and note that each is already covered by a task SUMMARY.
  - **If NEVER-FROZEN** → the remedy is a language correction: `HANDOFF.json:14`
    already carries the retraction; the residual work is to stop describing these
    five as pinned anywhere else. **List the exact sites** found in T1 STEP 5c
    (path:line) so the follow-up task is scoped, not searched for. Do not edit
    them.
  - **Should any of the five now be gated?** A recommendation only, with the
    per-file COST derived from T1 STEP 6:
      * a RECORDED Carter decision is required first — `PY_FROZEN_RELS`'s own
        comment says adding a file "requires a RECORDED DECISION that it is
        frozen, not an inference";
      * a pin constant carrying a `#:` bucket annotation (the repo-wide bucket
        gate enforces this);
      * a negative control **observed RED**
        (`[[feedback_green_assertion_needs_a_negative_control]]`);
      * ⚠ `test_the_handoff_frozen_claim_is_recorded_as_partly_false` would go
        RED for any file added — quote the assertion;
      * ⚠ **F5 (`pipeline.schema.yaml`) additionally needs a YAML code-stripper
        that does not exist** (`source_freeze.py` supports R and Python only;
        sr4 declined to build it). F4 is R, so `LANG_R` covers it mechanically.
    Present this as a decision surface with costs. **Do not recommend gating
    anything as if the decision were made.**

**§7 — LIMITS.** What this dossier does NOT establish, as limits rather than
coverage: no correctness review of the drift; the narrative first-appearance
dates are lower bounds (N revisions unreadable); no attempt at object recovery;
no claim about whether any *number* moved — these are source-text facts only.

Style: this project's readers check claims. Every table cell that is a number
must be traceable to a command in EVIDENCE.md. Use ⚠ for anything that would
change the answer if wrong.
  </action>
  <verify>
    <automated>D=.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-; test -s $D/260811-pmv-DOSSIER.md && [ "$(wc -l < $D/260811-pmv-DOSSIER.md)" -ge 150 ] && grep -q "SCOPE" $D/260811-pmv-DOSSIER.md && grep -qi "Carter's decision" $D/260811-pmv-DOSSIER.md && grep -q "SR4-OPEN" $D/260811-pmv-DOSSIER.md && grep -q "EVIDENCE.md" $D/260811-pmv-DOSSIER.md && grep -q "bf16289" $D/260811-pmv-DOSSIER.md && grep -q "LOWER BOUND" $D/260811-pmv-DOSSIER.md && grep -q "test_source_freeze_pins" $D/260811-pmv-DOSSIER.md && for p in occlusion_manifest.py occlusion_present_rate_scan.py drop_occluded_from_sumstats.py ld_npz_to_rds.R pipeline.schema.yaml plink_ld_to_npz.py; do grep -q "$p" $D/260811-pmv-DOSSIER.md || exit 1; done && [ "$(grep -coE 'NEVER-FROZEN-UNTIL-DECLARED|NEVER-FROZEN|FROZEN-AND-DRIFTED|DRIFT-NEEDS-REVIEW' $D/260811-pmv-DOSSIER.md)" -ge 5 ] && echo T2_OK</automated>
  </verify>
  <done>
DOSSIER.md exists with §0 scope statement first, the verbatim SR4-OPEN question,
an 8-column summary table, the C1–C3 control subsection, five per-file evidence
sections each ending in a closed-vocabulary recommendation, a conclusion derived
only from §4, an operational Carter's-decision block listing the exact
correction sites and the per-file gating cost (including the missing YAML
stripper), and a limits section. Every number in it appears in EVIDENCE.md.
  </done>
</task>

<task type="auto">
  <name>Task 3: Reconcile — re-run every quoted number and prove the deliverables agree</name>
  <files>
    .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md
    .planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-evidence.tsv
  </files>
  <action>
`[[feedback_a_count_is_a_claim_scope_and_reconcile]]` was baked by a figure that
shipped a count wrong **three times** and was self-inconsistent with numbers in
its own paragraph. This task is the guard against repeating that here.

**STEP 1 — Re-run, from a clean shell, in the repo root:**
  - the five `git diff --numstat bf16289 HEAD -- <path>` commands;
  - the three control `git diff --numstat bf16289 HEAD -- <path>` commands;
  - the five `git log --oneline bf16289..HEAD -- <path>` commands (recording rc);
  - `grep -c "<basename>" .planning/DECISIONS.md` for all five.
Confirm each value **matches** what the dossier and the TSV state.

**STEP 2 — Cross-artifact agreement.** Assert row-for-row that the dossier's
summary table and `evidence.tsv` carry the SAME values for all five files across
all shared columns. A mismatch is a **finding**, not a typo: fix BOTH artifacts
and record what was wrong and where in a reproduction log.

**STEP 3 — Command coverage.** For every distinct command string quoted in the
dossier, confirm that command appears in EVIDENCE.md. A command quoted in the
dossier but absent from the evidence log means a number was produced somewhere
unrecorded — treat it as a defect and fix it by recording the command and its
output in EVIDENCE.md.

**STEP 4 — Internal arithmetic.** Check the dossier is self-consistent: the
`# commits` column equals the number of rows in that file's §4 commit table; the
count of files marked `all traceable = no` equals the number of ⚠ UNTRACEABLE
callouts; the count of `gated today = yes` among F1–F5 equals what the live gate
supports. Reconcile any disagreement **arithmetically before shipping**.

**STEP 5 — Append `## Reproduction log` to the end of DOSSIER.md**, containing:
  - the re-run date, HEAD SHA, and confirmation that HEAD is unchanged since T1
    (if it moved, say so and re-measure rather than reconciling to a stale tree);
  - a table: claim | command | T1 value | T3 re-run value | match?
  - **every discrepancy found and how it was resolved** — if there were none,
    say "0 discrepancies" explicitly rather than omitting the line;
  - the object-store miss counts restated, so a reader of the dossier alone
    still learns the first-appearance dates are lower bounds.

**STEP 6 — Containment, PROVEN BY SET DIFFERENCE.** Confirm
`git status --porcelain | grep -v '^??'` is empty (zero modified tracked files),
then prove the untracked side rather than asserting it:

```bash
BASE=${TMPDIR:-/tmp}/260811-pmv-untracked-baseline.txt
comm -13 <(sort -u "$BASE") \
         <(git status --porcelain | grep '^??' | cut -c4- | sort -u)
```

This must print **EXACTLY** the three deliverable paths and nothing else. Record
the command and its output in the reproduction log.

⚠ If `$BASE` does not exist, containment is **UNPROVEN** — **FAIL LOUDLY and
say so**; do NOT fall back to eyeballing `git status`, and do NOT reconstruct the
baseline from the current tree (that assumes the answer). A skipped check
reported as a pass is the exact failure class
`[[feedback_skip_guard_masks_not_fixes]]` names.

If any extra path appears, **report it loudly in the reproduction log** — do not
revert silently.

⚠ Do **not** "fix" a disagreement by editing the number to match. Re-derive it,
then correct whichever artifact is wrong, and record both values.
  </action>
  <verify>
    <automated>D=.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-; grep -q "## Reproduction log" $D/260811-pmv-DOSSIER.md && grep -qiE "discrepanc" $D/260811-pmv-DOSSIER.md && [ -z "$(git status --porcelain | grep -v '^??')" ] && BASE=${TMPDIR:-/tmp}/260811-pmv-untracked-baseline.txt; { test -s "$BASE" || { echo "BASELINE MISSING at $BASE -- containment UNPROVEN, NOT passed"; exit 1; }; } && [ "$(comm -13 <(sort -u "$BASE") <(git status --porcelain | grep '^??' | cut -c4- | sort -u))" = "$(printf '%s\n' $D/260811-pmv-DOSSIER.md $D/260811-pmv-EVIDENCE.md $D/260811-pmv-evidence.tsv | sort -u)" ] && for p in src/python/occlusion_manifest.py src/python/occlusion_present_rate_scan.py src/python/drop_occluded_from_sumstats.py src/scripts/ld_npz_to_rds.R src/snakemake/schemas/pipeline.schema.yaml; do pair=$(git diff --numstat bf16289 HEAD -- $p | awk '{printf "+%s / -%s", $1, $2}'); grep -qF "$pair" $D/260811-pmv-DOSSIER.md || { echo "MISSING $p -> $pair"; exit 1; }; done && [ -z "$(git diff --numstat bf16289 HEAD -- src/python/plink_ld_to_npz.py src/python/condition_ld_matrix.py src/python/occlusion_span_filter.py)" ] && echo T3_OK</automated>
  </verify>
  <done>
Every diffstat, commit count and grep count in the dossier reproduced by a
freshly re-run command; dossier and TSV agree row-for-row; every command quoted
in the dossier exists in EVIDENCE.md; a `## Reproduction log` section records
the re-run table, an explicit discrepancy count (0 or the list), the
object-store miss counts, and the containment `comm` command with its output.
`git status --porcelain | grep -v '^??'` is empty, and the set difference of
untracked paths against the T1 STEP 0 baseline is EXACTLY the three
deliverables — proven by `comm`, not asserted.
  </done>
</task>

</tasks>

<threat_model>
## Trust boundaries

| Boundary | Description |
|----------|-------------|
| lossy git object store → dossier claims | The GPFS store is missing loose objects; history walks return **partial** results with a plausible shape. Untrusted as a completeness oracle. |
| handoff/STATE narrative → dossier claims | Prose written by past sessions, already proven wrong once (the retracted "all 7 pinned files 0-diff"). Untrusted as a measurement. |
| this task's writes → the repo | Read-only investigation; only three files in one quick directory may be written. |

## STRIDE threat register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-pmv-01 | Information disclosure (a truncated read presented as complete) | `git log -S` over `.planning/HANDOFF.json` / `STATE.md` | mitigate | `-S` BANNED as primary method (verified rc=128 with rows still on stdout). T1 STEP 5b uses a presence-checked per-revision loop; `OBJECT-STORE CENSUS` reports readable/unreadable counts + SHAs; all first-appearance claims scoped as LOWER BOUND. |
| T-pmv-02 | Repudiation (a number with no provenance) | every count in DOSSIER.md | mitigate | Each count names its command; the verbatim output lives in EVIDENCE.md; T3 STEP 3 asserts command coverage and T3 STEP 1 re-runs each value. |
| T-pmv-03 | Spoofing (an unreviewed commit passing as reviewed) | provenance trace, T1 STEP 4 | mitigate | Traceability requires the short SHA to be NAMED in a planning artifact, not merely a task token in the commit subject; token-only ⇒ untraceable ⇒ forces `DRIFT-NEEDS-REVIEW`. |
| T-pmv-04 | Tampering (a write outside scope) | working tree | mitigate | T1 STEP 0 records the pre-existing untracked baseline; T3 STEP 6 + the T3 verify assert zero modified tracked files and that new untracked paths are only the three deliverables. |
| T-pmv-05 | Elevation of privilege (evidence read as a decision) | DOSSIER.md | mitigate | §0 scope statement + §6 Carter's-decision block state the disposition is Carter's; no `DECISIONS.md` / `HANDOFF.json` edit is in scope; gating is presented as costed options, never as a recommendation to act. |
| T-pmv-06 | Tampering (stale-tree reconciliation) | T3 re-run vs T1 measurement | mitigate | T3 STEP 5 records HEAD at re-run time and requires re-measurement rather than reconciliation if HEAD moved. |
| T-pmv-07 | Denial of service | n/a | accept | Local, read-only, `$0`, no network, no LSF, no AoU perimeter contact, no fire path touched. |
| T-pmv-08 | Information disclosure (data exposure) | n/a | accept | No PII, no genotypes, no perimeter data. Deliverables contain only git metadata and file paths already committed to this repo. |
</threat_model>

<verification>
1. `pytest tests/m3/test_source_freeze_pins.py -q` → **39 passed** (the state
   this dossier describes; it is read, never changed).
2. `git status --porcelain | grep -v '^??'` → **empty**. No tracked file
   modified anywhere in the repo.
3. `git diff --numstat bf16289 HEAD -- <C1> <C2> <C3>` → **empty** (the control
   still holds).
4. The three deliverables exist under
   `.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/` and
   **nothing** was written outside it.
5. No file under `src/`, `tests/`, `config/`, or `.planning/DECISIONS.md`,
   `.planning/HANDOFF.json`, `.planning/STATE.md` was modified.
6. `$0` — no LSF job, no `gsutil`/`gcloud`/`bq`/`dataproc`/`hailctl`/`wb`
   invocation, no perimeter contact.
</verification>

<success_criteria>
- Carter can answer SR4-OPEN from `260811-pmv-DOSSIER.md` alone, per file.
- Every count in the dossier is reproduced by a stated command whose verbatim
  output is in `260811-pmv-EVIDENCE.md`; the reproduction log records 0
  discrepancies or lists each one and its resolution.
- Today's diffstats are re-measured at HEAD and compared against the sr4-era
  numbers, with the comparison stated explicitly.
- Every drift commit is either traced to a planning artifact that NAMES its SHA,
  or flagged ⚠ UNTRACEABLE — and any untraceable commit forces that file to
  `DRIFT-NEEDS-REVIEW`.
- Missing git objects are reported as a census with SHAs; every narrative
  first-appearance claim is scoped as a lower bound.
- The dossier states its own scope limits and does not record a disposition.
- Zero modified tracked files; three new files, all inside the quick directory.
</success_criteria>

<output>
After completion, create
`.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-SUMMARY.md`.

The SUMMARY must state the per-file recommendations, the overall answer the
evidence supports, any ⚠ UNTRACEABLE commit found, the object-store miss counts,
and — explicitly — that **the disposition remains Carter's and was NOT recorded**.
Do NOT write `.planning/STATE.md`, `.planning/HANDOFF.json`,
`.planning/DECISIONS.md` or `.continue-here.md`; the orchestrator owns those.
</output>
