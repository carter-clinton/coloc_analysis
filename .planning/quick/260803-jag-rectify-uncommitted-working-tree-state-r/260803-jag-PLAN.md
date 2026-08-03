---
phase: quick-260803-jag
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md      # RESTORE from HEAD (no commit)
  - data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md        # RESTORE from HEAD (no commit)
  - .claude/settings.json                                              # PRUNE 4 entries, then COMMIT
  - .planning/quick/260625-r6m-build-resumable-native-plink-ld-loop-dri/260625-r6m-SUMMARY.md  # COMMIT AS-IS
  - tests/m3/sparse_parent_benchmark.tsv                               # REVERT to HEAD (no commit)
autonomous: true
requirements: [QUICK-260803-jag]   # quick-task brief, not a ROADMAP requirement ID
user_setup: []

must_haves:
  truths:
    - "Both AFR disclosure docs exist on disk again, byte-identical to HEAD"
    - "git status --short reports ZERO tracked-file entries (no M, no D) — only untracked noise remains"
    - "The 260625-r6m SUMMARY update is committed and reachable from the new HEAD"
    - ".claude/settings.json on the branch grants NO rm -rf, NO rm -f, and NO unattended background fire launch"
    - "The 8 durable read/inspect grants and the additionalDirectories codex-tmp block survive in the committed settings.json"
    - "src/ and tests/*.py have a ZERO-line diff vs. bf16289"
    - "origin == local after push"
  artifacts:
    - path: "data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md"
      provides: "AFR-stroke max-FDR 0.1154 honest-finding disclosure (witness for M2-POST-M3-09)"
      exact_bytes: 7454
    - path: "data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md"
      provides: "AFR mtCOJO 1000G-AFR LD insufficiency disclosure (why all 4 rows are sensitivity_flag=FAIL by design)"
      exact_bytes: 4629
    - path: ".claude/settings.json"
      provides: "permission allow-list with exactly 33 entries (25 committed + 8 durable new)"
      contains: "additionalDirectories"
    - path: ".planning/quick/260625-r6m-build-resumable-native-plink-ld-loop-dri/260625-r6m-SUMMARY.md"
      provides: "record of the durable gs:// out-dir (Dataproc bucket-first) follow-up that landed as 10aaa6f"
  key_links:
    - from: ".claude/settings.json"
      to: "data/processed/"
      via: "the removed rm -rf grant would have permanently pre-approved recursive deletion over the SAME tree whose accidental deletion Task 1 repairs"
      pattern: "NOT rm -rf"
    - from: "restored disclosure docs"
      to: "git HEAD blobs"
      via: "git checkout HEAD -- <path>"
      pattern: "git diff --quiet -- data/processed"
---

<objective>
Rectify the four uncommitted working-tree items on `m3-W2-aou-deltas` @ `bf16289`, each with a
DIFFERENT disposition, and land the two that are committable.

Purpose: the tree currently hides (a) two silently-deleted honest-finding disclosure docs that back
OSF-pre-registered negative results, and (b) a pending commit that would permanently grant an
`rm -rf` over `data/processed/` — the very class of action that most plausibly caused (a). Leaving
either in place is a provenance and safety liability.

Output: a clean tracked working tree, two commits, one push. $0. No perimeter contact. No `src/` change.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@CLAUDE.md

## Verified starting state (orchestrator-investigated + planner spot-checked)

Branch `m3-W2-aou-deltas`, HEAD `bf16289`, `origin == local`.
Full `tests/m3` verified GREEN today at this exact HEAD: **420 passed / 31 skipped / 0 failed**.

`git status --short` on tracked paths shows EXACTLY four entries:

```
 M .claude/settings.json
 M .planning/quick/260625-r6m-build-resumable-native-plink-ld-loop-dri/260625-r6m-SUMMARY.md
 D data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md
 D data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md
 M tests/m3/sparse_parent_benchmark.tsv
```

Spot-checks the planner re-ran and CONFIRMED:
- `git ls-files -d -- data/processed | wc -l` == **2** → those two are the ONLY tracked files missing
  under `data/processed`. Bounded blast radius.
- `git cat-file -e HEAD:<path>` succeeds for BOTH → fully recoverable from HEAD.
- Blob sizes at HEAD: `AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md` = **7454 B**,
  `AFR_LD_INSUFFICIENT_FOR_MTCOJO.md` = **4629 B**.
- `git merge-base --is-ancestor 10aaa6f HEAD` → **yes**. The code the r6m SUMMARY documents LANDED;
  only the SUMMARY update was stranded.
- Both parent directories (`data/processed/mtag/AFR/`, `data/processed/mtcojo/AFR/`) are gone entirely;
  `git checkout` recreates them.

## PLANNER CORRECTION 1 — the settings.json entry count

The brief says the diff "adds 13 entries". The raw diff has **13 `+` lines inside `allow`**, but one of
them is a comma-only re-add of the pre-existing `Read(//gpfs_common/.../coloc_analysis/**)` entry.
Net-new entries = **12** (8 durable + 4 one-off). Verified numerically:

- `HEAD:.claude/settings.json` → `len(permissions.allow)` == **25**, `additionalDirectories` == **absent**
- on-disk `.claude/settings.json` → `len(permissions.allow)` == **37**, `additionalDirectories` == `['/home/ckclinto/.codex/.tmp']`
- 25 + 12 = 37 ✓ → **after the prune the target count is exactly 33.**

## PLANNER CORRECTION 2 — the benchmark TSV values drift every run

The brief quotes `read_s 1.133→1.100 / densify_window_s 0.236→0.242`. The planner observes
`1.133→1.115 / 0.236→0.231` right now. Same conclusion, stronger: the file is rewritten by the
`tests/m3` suite on **every** run and the timing columns differ each time. `rds_bytes`,
`peak_ram_load_gib`, `peak_ram_densify_gib`, `window_var`, `M` are IDENTICAL. Pure noise → revert.

**⚠ ORDERING HAZARD this creates:** any `tests/m3` invocation AFTER the revert re-dirties the file.
Therefore the revert is scheduled **LAST** (Task 3), and no test may be run after it.

## The disclosure docs are substantive, not scratch

`AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md` records the Turley-2018 max-FDR scalar
**0.11541401327515466** for `stroke.AFR.GIGASTROKE.2022` — the single above-0.05 scalar across the
21-trait × 3-stratum harvest — explicitly framed as an **honest finding** preserved as
`historical_outcome` per `feedback_failed_to_honest_finding`, with the re-evaluation queued as
`M2-POST-M3-09`. `AFR_LD_INSUFFICIENT_FOR_MTCOJO.md` records why all 4 AFR mtCOJO targets carry
`sensitivity_flag=FAIL` **by design** under the 1000G AFR N=504 panel. Both are negative-result
provenance. Deletion is judged ACCIDENTAL collateral of an M2 data-directory purge, **not a
deliberate retraction** → restore.

## Current `.claude/settings.json` on disk — the four entries to REMOVE

They are the LAST four entries of `allow` (file lines 37-40). Line 36
(`"Bash(sed -n '289,310p' docs/manuscript/track_a_pivot.md)"`) currently ends with a comma and must
become the last entry with **NO trailing comma**:

```json
      "Bash(rm -rf data/processed/clumping/*/ data/processed/clumping/.m2_clumping_complete)",
      "Bash(rm -f logs/m2_04_clumping.fire.log)",
      "Bash(PARALLEL=20 nohup bash bin/fire_m2_04_clumping.sh)",
      "Bash(echo \"Fired PID $!\")"
```

**RATIONALE (load-bearing — do not lose this):** these four were transient grants for a single M2
clumping fire that has already happened. Committing them permanently pre-approves an `rm -rf` under
`data/processed/` and an unattended background fire launch, for every future agent session, with no
prompt. That is exactly the class of action that most plausibly produced finding (1) — two disclosure
docs vanishing from `data/processed/`. Persisting a standing `rm -rf` grant over the same tree whose
accidental deletion we are repairing **in the same task** is self-defeating. Removal costs only a
one-time re-prompt if that fire is ever re-run.

## Hard rules in force

- **NEVER `git add .` or `git add -A`** on this GPFS tree. Explicit paths only, always. Baked by the
  2026-04-28 multi-terminal collision. Other terminals may be writing this tree right now.
- **Do NOT run the full `tests/m3` suite** as a gate (~8 min; already GREEN at this HEAD today).
- Frozen contracts stay 0-line diff: `src/python/plink_ld_to_npz.py`, `src/R/ld_npz_to_rds.R`,
  `src/python/condition_ld_matrix.py`.
- Remote is **SSH** since 2026-07-15 → `git push` needs no PAT. This task creates **no tags**, so the
  "push does not push tags" hazard does not apply.
- Do NOT touch the m3-07 arc, the AoU perimeter, or any `gs://` object.

## DECISION: STATE.md is an explicit NON-GOAL

The baked rule `feedback_state_md_keep_current` normally wants a STATE.md refresh in the same atomic
commit. **Deliberately not done here**, for two reasons: (a) this task changes no project state —
nothing about m3-07, the loop, or the perimeter moves; (b) STATE.md's top block at line 28 is the
`★★ RESUME HERE ★★` m3-07 CODE-COMPLETE block, and prepending a working-tree-hygiene block above it
would actively misdirect the next resume. The outcome is recorded in the quick SUMMARY instead.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Restore the two deleted AFR disclosure docs from HEAD</name>
  <files>
    data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md
    data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md
  </files>
  <action>
Restore both tracked files from HEAD. Both parent directories are gone; `git checkout` recreates them.

```bash
git checkout HEAD -- \
  data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md \
  data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md
```

Enumerate BOTH paths explicitly. Do NOT use `git checkout HEAD -- data/processed` or any directory-level
pathspec — a broad pathspec on this shared GPFS tree can clobber another terminal's concurrent work
(threat T-jag-03), and `git ls-files -d` already proved only these two paths are affected.

This restores committed content into the working tree, so it produces **NO diff to commit** for these
two paths. Do not stage them, do not commit them, do not `git add` them. If `git diff --cached` shows
anything for `data/processed` afterwards, something went wrong — stop and report.

Do NOT edit either file's content. They are byte-frozen provenance artifacts.
  </action>
  <verify>
    <automated>
git checkout HEAD -- data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md && \
test -f data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md && \
test -f data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md && \
test "$(stat -c%s data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md)" -eq 7454 && \
test "$(stat -c%s data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md)" -eq 4629 && \
test "$(git ls-files -d -- data/processed | wc -l)" -eq 0 && \
git diff --quiet -- data/processed && \
git diff --cached --quiet -- data/processed && \
grep -q '0.11541401327515466' data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md && \
grep -q 'sensitivity_flag=FAIL' data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md && \
echo "T1 PASS"
    </automated>
  </verify>
  <done>
Both files exist at exactly 7454 B and 4629 B, contain their known anchor strings, `git ls-files -d --
data/processed` is empty, and both `git diff` and `git diff --cached` are clean for `data/processed`
(restore produced nothing to commit). `T1 PASS` printed.
  </done>
</task>

<task type="auto">
  <name>Task 2: Prune the 4 one-off destructive grants from .claude/settings.json</name>
  <files>.claude/settings.json</files>
  <action>
Surgically remove EXACTLY these four entries from `permissions.allow`, leaving every other byte of the
file unchanged:

1. `Bash(rm -rf data/processed/clumping/*/ data/processed/clumping/.m2_clumping_complete)`
2. `Bash(rm -f logs/m2_04_clumping.fire.log)`
3. `Bash(PARALLEL=20 nohup bash bin/fire_m2_04_clumping.sh)`
4. `Bash(echo "Fired PID $!")`

Use the **Edit tool** (a targeted textual edit), NOT a JSON round-trip via `python3 -c "json.dump(...)"`.
A round-trip would rewrite key order, indentation, and escaping across the whole file and destroy the
"every other line byte-identical" property.

They are the last four entries of the array. After removal, the preceding entry
`"Bash(sed -n '289,310p' docs/manuscript/track_a_pivot.md)"` becomes the LAST element and its trailing
comma MUST be dropped, or the file is invalid JSON. Target end-state tail:

```json
      "Bash(sed -n '220,228p' docs/manuscript/track_a_pivot.md)",
      "Bash(sed -n '289,310p' docs/manuscript/track_a_pivot.md)"
    ],
    "additionalDirectories": [
      "/home/ckclinto/.codex/.tmp"
    ]
  }
}
```

KEEP (do not touch): the 25 already-committed entries, the 8 durable new entries
(`WebFetch(domain:www.ncbi.nlm.nih.gov)`; the four `git -C <repo> log --oneline -6/-4/-8` and
`status --short` grants; the three `sed -n` manuscript-excerpt grants), and the whole
`additionalDirectories` block — the codex-tmp entry pairs with the committed memory note about
redirecting `~/.codex/.tmp` off the `/home` inode quota.

Do NOT commit in this task. Task 3 owns all commits.
  </action>
  <verify>
    <automated>
export PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH"; python3 - <<'PY'
import json, subprocess
d = json.load(open('.claude/settings.json'))
allow = d['permissions']['allow']
head = json.loads(subprocess.check_output(['git','show','HEAD:.claude/settings.json']))
h = head['permissions']['allow']
forbidden = [
  "Bash(rm -rf data/processed/clumping/*/ data/processed/clumping/.m2_clumping_complete)",
  "Bash(rm -f logs/m2_04_clumping.fire.log)",
  "Bash(PARALLEL=20 nohup bash bin/fire_m2_04_clumping.sh)",
  'Bash(echo "Fired PID $!")',
]
durable = [
  "WebFetch(domain:www.ncbi.nlm.nih.gov)",
  "Bash(git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis log --oneline -6)",
  "Bash(git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis status --short)",
  "Bash(git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis log --oneline -4)",
  "Bash(sed -n '220,224p' /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/docs/manuscript/track_a_pivot.md)",
  "Bash(git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis log --oneline -8)",
  "Bash(sed -n '220,228p' docs/manuscript/track_a_pivot.md)",
  "Bash(sed -n '289,310p' docs/manuscript/track_a_pivot.md)",
]
assert len(h) == 25, f"HEAD allow drifted: {len(h)}"
assert allow[:25] == h, "committed 25-entry prefix was mutated"
assert len(allow) == 33, f"expected 33 entries, got {len(allow)}"
still = [f for f in forbidden if f in allow]
assert not still, f"one-off grant STILL PRESENT: {still}"
missing = [x for x in durable if x not in allow]
assert not missing, f"durable grant LOST: {missing}"
assert d['permissions'].get('additionalDirectories') == ['/home/ckclinto/.codex/.tmp'], "additionalDirectories block damaged"
print("T2 PASS: valid JSON, 33 entries, 25-entry committed prefix intact, 8 durable kept, 4 one-off removed")
PY
grep -nE 'rm -rf|rm -f logs|nohup|Fired PID' .claude/settings.json && { echo "T2 FAIL: destructive grant text still in file"; exit 1; } || echo "T2 PASS: no destructive grant text"
    </automated>
  </verify>
  <done>
`.claude/settings.json` parses as valid JSON; `allow` has exactly 33 entries; `allow[:25]` is
element-wise identical to `HEAD:.claude/settings.json`; all four one-off grants are absent (both by
list membership and by raw-text grep); all 8 durable grants present; `additionalDirectories` ==
`['/home/ckclinto/.codex/.tmp']`. Nothing committed yet.
  </done>
</task>

<task type="auto">
  <name>Task 3: Revert the benchmark byproduct, then commit + push the two committable items</name>
  <files>
    tests/m3/sparse_parent_benchmark.tsv
    .planning/quick/260625-r6m-build-resumable-native-plink-ld-loop-dri/260625-r6m-SUMMARY.md
    .claude/settings.json
  </files>
  <action>
**Step 3a — revert the benchmark TSV (do this FIRST within this task, and run NO `tests/m3` test after it):**

```bash
git checkout HEAD -- tests/m3/sparse_parent_benchmark.tsv
```

This file is regenerated by the `tests/m3` suite on every run; only the timing columns (`read_s`,
`densify_window_s`) moved and they differ run-to-run. Zero information. This is a REVERT — the file is
NOT modified, NOT committed, and must not be edited by hand.

**Step 3b — commit the stranded r6m SUMMARY, AS-IS. Do not rewrite its content.**

```bash
git add .planning/quick/260625-r6m-build-resumable-native-plink-ld-loop-dri/260625-r6m-SUMMARY.md
git commit -m "docs(260625-r6m): commit stranded SUMMARY update for the durable gs:// out-dir follow-up

The code this documents landed as 10aaa6f (verified ancestor of HEAD); only the
SUMMARY update was never committed. Content committed unchanged (+55/-11)."
```

**Step 3c — commit the pruned settings.json, with the rationale in the message:**

```bash
git add .claude/settings.json
git commit -m "chore(claude): keep durable read/inspect grants, drop 4 one-off destructive ones

Commits 8 durable permission entries (ncbi WebFetch, git log/status inspection,
three manuscript sed excerpts) plus the additionalDirectories codex-tmp block,
which pairs with the committed note redirecting ~/.codex/.tmp off the /home
inode quota.

Deliberately NOT committed (removed before staging):
  Bash(rm -rf data/processed/clumping/*/ ...)
  Bash(rm -f logs/m2_04_clumping.fire.log)
  Bash(PARALLEL=20 nohup bash bin/fire_m2_04_clumping.sh)
  Bash(echo \"Fired PID \$!\")

These were transient grants for a single M2 clumping fire that already ran.
Committing them would permanently pre-approve an rm -rf under data/processed/
and an unattended background fire launch for every future session, with no
prompt. That is exactly the class of action that most plausibly deleted the two
AFR disclosure docs restored in this same task. Cost of removal is one re-prompt
if that fire is ever re-run."
```

**⚠ NEVER `git add .` or `git add -A`.** Stage only the single explicit path shown in each step. Other
terminals may be writing this GPFS tree concurrently.

**Step 3d — push (SSH remote, no PAT, no tags):**

```bash
git push
```

**CONTINGENCY — GPFS loose-object loss.** This tree has lost loose git objects three times in ~3 weeks
(2026-06-28 / 07-03 / 07-15). If either commit fails with `invalid object ... / Error building trees`:

```bash
git ls-files -s | while read -r mode sha stage path; do
  git cat-file -e "$sha" 2>/dev/null || echo "MISSING $sha $path"
done
```

For each MISSING line, re-hash the intact working-tree file: `git hash-object -w "<path>"` and confirm
the printed sha matches. Then retry the commit AND **push immediately** — the local store is unreliable.
Note `git fsck` also reports ~194 pre-existing broken links in OLDER already-pushed history; that is
known and out of scope — verify only that the PUSH SET is intact, do not attempt history surgery.
  </action>
  <verify>
    <automated>
git checkout HEAD -- tests/m3/sparse_parent_benchmark.tsv && \
git diff --quiet -- tests/m3/sparse_parent_benchmark.tsv && \
test -z "$(git status --porcelain --untracked-files=no)" && \
git diff --quiet bf16289 HEAD -- src tests && \
git diff --quiet bf16289 HEAD -- src/python/plink_ld_to_npz.py src/R/ld_npz_to_rds.R src/python/condition_ld_matrix.py && \
test "$(git rev-parse HEAD)" = "$(git rev-parse @{u})" && \
git log --oneline bf16289..HEAD | wc -l | grep -qx '2' && \
git cat-file -e HEAD:data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md && \
git cat-file -e HEAD:data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md && \
git show HEAD:.claude/settings.json | grep -qE 'rm -rf|nohup|Fired PID' && { echo "T3 FAIL: destructive grant reached HEAD"; exit 1; } || echo "T3 PASS"
    </automated>
  </verify>
  <done>
`git status --porcelain --untracked-files=no` is EMPTY (zero tracked M/D entries). `bf16289..HEAD` is
exactly 2 commits. `git diff bf16289 HEAD -- src tests` is empty (zero-line code diff; the three frozen
contracts re-checked individually). `HEAD == @{u}` (pushed, origin == local). Both disclosure docs still
resolve at HEAD. The committed `.claude/settings.json` contains no `rm -rf` / `nohup` / `Fired PID` text.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `settings.json` allow-list → autonomous tool execution | Any string committed here executes in future sessions with NO user prompt. Committing is a privilege grant, permanent until revoked. |
| working tree → committed history (shared GPFS) | Multiple terminals write this tree concurrently; a broad pathspec or `git add .` can capture or destroy another terminal's work. |
| local object store → origin | The GPFS loose-object store has demonstrably lost blobs 3× in ~3 weeks; unpushed commits are at risk. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-jag-01 | Elevation of Privilege | `Bash(rm -rf data/processed/clumping/*/ ...)` in `settings.json` | mitigate | Remove before staging (Task 2). Verify by BOTH JSON list-membership AND raw `grep -E 'rm -rf'` on the committed blob (Task 3 verify). This is the primary purpose of the task. |
| T-jag-02 | Elevation of Privilege / DoS | `Bash(PARALLEL=20 nohup bash bin/fire_m2_04_clumping.sh)` + `Bash(echo "Fired PID $!")` | mitigate | Remove before staging. A committed grant pre-approves an unattended 20-way background compute launch with no prompt. Verified by the same `grep -E 'nohup\|Fired PID'` gate. |
| T-jag-03 | Tampering | `git checkout HEAD -- <pathspec>` / staging on shared GPFS tree | mitigate | Enumerate every path explicitly; never a directory pathspec, never `git add .`/`-A`. `git ls-files -d -- data/processed` == 2 bounds the restore set positively before acting. Final gate is `git status --porcelain -uno` EMPTY, which would also expose any collateral capture. |
| T-jag-04 | Repudiation / information loss | the two AFR disclosure docs | mitigate | Restore from HEAD and prove byte-identity via exact `stat -c%s` (7454 / 4629) + anchor-string greps (`0.11541401327515466`, `sensitivity_flag=FAIL`) + `git diff --quiet -- data/processed`. These back OSF-pre-registered negative results; silent loss would erase the provenance for `M2-POST-M3-09`. |
| T-jag-05 | Tampering | GPFS loose-object loss during commit | accept + recipe | Cannot be prevented at this layer. Task 3 carries the guarded `git cat-file -e` → `git hash-object -w` recovery recipe and mandates an immediate push. Residual risk accepted (3/3 prior occurrences fully recovered). |
| T-jag-06 | Tampering | hand-edit of `settings.json` producing invalid JSON | mitigate | `json.load` gate + trailing-comma call-out + `allow[:25] == HEAD allow` element-wise equality, all BEFORE any commit. A broken permissions file would silently disable the allow-list. |
| T-jag-07 | Tampering | test byproduct re-dirtying after revert | mitigate | Schedule the TSV revert LAST (Task 3, step 3a) and forbid any `tests/m3` run after it. Full-suite run is separately forbidden — already GREEN 420P/31S/0F at `bf16289` today. |
</threat_model>

<verification>
Run after all three tasks:

```bash
# 1. Tracked tree fully clean
git status --porcelain --untracked-files=no        # → EMPTY

# 2. Disclosure docs on disk, exact sizes
stat -c '%s %n' data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md \
                data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md
                                                    # → 7454 / 4629

# 3. Exactly 2 new commits, zero code diff
git log --oneline bf16289..HEAD                     # → 2 lines
git diff --stat bf16289 HEAD -- src tests           # → EMPTY

# 4. No destructive grant in committed history
git show HEAD:.claude/settings.json | grep -E 'rm -rf|nohup|Fired PID'   # → no match

# 5. Pushed
git rev-parse HEAD; git rev-parse @{u}              # → identical
```

Explicitly NOT run: the full `tests/m3` suite (~8 min, already GREEN 0F/420P/31S at `bf16289` today,
and running it would re-dirty `sparse_parent_benchmark.tsv`).
</verification>

<success_criteria>
- `git status --porcelain --untracked-files=no` is EMPTY
- Both AFR disclosure docs present at exactly 7454 B and 4629 B with anchor strings intact
- Exactly 2 commits on `bf16289..HEAD`: the r6m SUMMARY (content unchanged), the pruned settings.json
- `git diff bf16289 HEAD -- src tests` is EMPTY (zero-line code diff; all 3 frozen contracts untouched)
- `git show HEAD:.claude/settings.json` → 33 allow entries, first 25 byte-identical to `bf16289`,
  8 durable added, `additionalDirectories` present, ZERO `rm -rf` / `rm -f` / `nohup` / `Fired PID`
- `HEAD == @{u}` (pushed; SSH remote; no tags created)
- $0 spent; no perimeter contact; no `gs://` object touched; m3-07 arc untouched
</success_criteria>

<output>
After completion, create
`.planning/quick/260803-jag-rectify-uncommitted-working-tree-state-r/260803-jag-SUMMARY.md`.

Record in it: the 4 dispositions and which produced commits (2) vs. working-tree-only changes (2); the
two planner corrections (net-new allow entries = 12 not 13, so the target count is 33; the benchmark
timing values drift every suite run); and the rationale for refusing to commit the 4 destructive grants.
Note that STATE.md was intentionally NOT modified (see the DECISION block in `<context>`).
</output>
