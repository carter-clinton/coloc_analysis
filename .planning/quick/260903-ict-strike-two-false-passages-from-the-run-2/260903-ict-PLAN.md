---
task: 260903-ict
title: Correct two false passages in the RUN 2 courier record (fix at source, re-splice) and append the tail DISCLOSURE
mode: quick
type: execute
branch: m3-W2-aou-deltas
worktree: none            # GPFS constraint — worktrees disabled project-wide
docs_only: true           # src/ and tests/ MUST be untouched at commit time
autonomous: true
push: false               # commit only
revision: 2               # r1 remedy for F-2 REVERSED by coordinator; spec re-anchored

files_modified:
  - .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
  - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md   # splice SOURCE — fixed at source per ee3af4b
  - .planning/osf_deviations.md
  - .planning/STATE.md
  - .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/260903-ict-PLAN.md
  - .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/260903-ict-SUMMARY.md
  - .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/deferred-items.md

files_frozen:
  - src/**            # DOCS-ONLY gate
  - tests/**          # DOCS-ONLY gate
  - .planning/amendments/**   # posted OSF bodies — never edited in-repo

must_haves:
  truths:
    - "`LIVE CONTRADICTION` appears ZERO times in the whole courier record, appendix included."
    - "The false claim is corrected AT SOURCE in the splice spec, not masked by a note."
    - "The courier appendix is a byte-faithful splice of the CORRECTED source, re-verified and re-anchored."
    - "The stale wording note describing a state that no longer exists is deleted."
    - "The courier states the collapse test does not discriminate, without restating the struck inference."
    - "osf_deviations.md carries a new 2026-09-03 entry marked DRAFTED — NOT POSTED."
    - "The 530 pre-existing lines of osf_deviations.md are byte-identical."
    - "Every pin that this task moves is refreshed to a true post-task value."
    - "src/ and tests/ are untouched."
  artifacts:
    - path: ".planning/debug/260902-COURIER-...-definitional-disagreement.md"
      provides: "corrected courier record + re-spliced appendix"
    - path: ".planning/quick/260902-vsp-.../CONTENT-SPEC.md"
      provides: "corrected splice source"
    - path: ".planning/osf_deviations.md"
      provides: "the tail disclosure, appended"
    - path: ".planning/quick/260903-ict-.../deferred-items.md"
      provides: "the report-only findings, recorded not fixed"
  key_links:
    - from: "courier appendix (BEGIN..END markers)"
      to: ".planning/quick/260902-vsp-.../CONTENT-SPEC.md from '## ARTIFACTS' to EOF"
      via: "byte-equal splice, re-verified after the source fix"
    - from: "courier line 23"
      to: "splice source md5 / bytes / lines"
      via: "pin refreshed to post-fix values"
    - from: ".planning/STATE.md:45"
      to: "courier md5 / line count"
      via: "pin refreshed to post-task values"
---

<objective>
DOCS-ONLY. One commit, no push.

**PART A** — three corrections to the committed courier record
`.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md`:
**A1** the false `0.0005` action item (fixed in BODY *and* AT SOURCE, then re-spliced);
**A2** the heterogeneity correction (an ADDITION — see F-1);
**A3** deletion of a now-stale wording note.
**PART B** — append the tail DISCLOSURE to `.planning/osf_deviations.md` as a PURE APPEND.
**PART C** — one `### Quick Tasks Completed` row in `.planning/STATE.md`, plus every pin this
task moves.

Purpose: the record contains a passage that is FALSE (an alleged `0.0005` contradiction that
does not exist), lacks the correction to an argument since shown not to discriminate, and
carries a note advertising a superseded policy. The disclosure is the methods-side companion;
it is DRAFTED ONLY.
</objective>

<authority>
`CONTENT-SPEC.md` in this task directory is THE authoritative content
(**225 lines, 14917 B, md5 `20d3b287c3f5bbea5104d79f67b710a8`**).

⚠ This SUPERSEDES the r1 anchor `dbd3d8a0129716a224d207c80c546f15` / 193 / 12504. If the
executor finds the old anchor, it is reading a stale spec: STOP.

Copy from it. **Do not recompute or re-derive any number.** If any number appears to disagree
with the tree: STOP, record it, report it. Never reconcile silently.
</authority>

<hard_constraints>
1. **DOCS-ONLY.** `git status --porcelain -- src tests` EMPTY at commit time. The
   `condition_ld_matrix.py` docstring defect is DEFERRED, not fixed here.
2. **DISCLOSURE, NOT AMENDMENT. NOTHING IS POSTED.** The entry is marked
   `DRAFTED — NOT POSTED; placement and posting are Carter's.` No agent contacts OSF.
   Never edit the posted July amendment or the posted `mk7ze` body in-repo.
3. **`.planning/osf_deviations.md` is a PURE APPEND** — the pre-existing 530 lines byte
   identical afterwards, proven by `cmp`, not by eyeball.
4. **Explicit git paths only. NEVER `git add -A` / `git add .`** (shared GPFS tree).
5. **No push.** Commit only.
6. Leave `.planning/debug/m3-producer-unbounded-dense-read.md` untracked.
7. Do NOT backfill the four missing STATE rows (`260828-uej`, `260831-kw8`, `260901-l55`,
   `260901-rvu`). Append ONE row, for `260903-ict`.
8. **The appendix is SPLICED BY SCRIPT, never retyped.** Fix at source, re-splice, re-anchor.
</hard_constraints>

<planning_findings>
Measured at plan time and re-confirmed after the coordinator's revision. Stated here so the
executor does not rediscover them mid-edit.

### ✅ F-1 — PART A2 HAS NO TARGET. IT IS AN ADDITION, NOT A STRIKE. (accepted; spec updated)

The collapse-to-parents argument is **not in the courier record**. Measured across all 491
lines:

| pattern | hits in courier |
|---|---|
| `collaps` | 0 |
| `parent` | 0 |
| `2.62` | 0 |
| `leave-one-out` | 0 |
| `2.48` | 0 |
| `0.0063` | 0 (the record writes the same p as `6.3e-3`) |

It lives only in `.planning/STATE.md:54` and `.continue-here.md:23`; it was made in
correspondence and never written into the courier. PART A2 is therefore a **pure addition**.
The check "the record must STILL contain 1.99x, leave-one-out 1.99–2.48, p 0.0063" is only
satisfiable this way: `1.99x` is already present; the leave-one-out range, `0.0063`, and the
`0.98` refutation are **new**. Re-prove the six zero-counts in the executor's own shell
(Task 1D) before relying on this.

### ⛔ F-2 — REVERSED FROM r1. FIX AT SOURCE AND RE-SPLICE. DO NOT ADD A SUPERSESSION NOTE.

`LIVE CONTRADICTION` appears **twice**: courier line **296** (BODY heading) and line **450**
(inside the VERBATIM APPENDIX, lines 338–491).

r1 proposed leaving the appendix copy standing behind a supersession note, citing the
record's own note at lines 290–294 as precedent. **That precedent is stale, and the r1
remedy is rejected.** Verified at plan time:

- The note claims the appendix "still says 'the three **pre-registered** values'."
- Measured now: `pre-registered value` = **0** occurrences in the record and **0** in the
  appendix. The appendix reads *"the three COMPLETION-CHECK values (see that section — they
  are NOT a pre-registration)."*
- Commit `ee3af4b` already overturned leave-it-and-note-it: it fixed the phrase **at source**
  in the `260902-vsp` CONTENT-SPEC, re-spliced, and re-anchored. The note explaining why that
  had *not* been done was never deleted, so the record kept advertising a superseded policy —
  and it misled this task's r1 planner.

**Byte-equality is a MEANS — proof that no number was retyped — not an end. It survives
re-anchoring. Preserving a false claim to protect an md5 is a guard scoped to a proxy, which
is exactly what `ee3af4b` rejected.**

So: **G-A1 stands as originally written and is satisfiable** — `LIVE CONTRADICTION` = 0
occurrences in the **WHOLE** record, appendix included. The r1 construction rule is KEPT (the
correction's own prose must not use the phrase); it removes the scoping trap by design rather
than by a grep that has to reason about which occurrence is legitimate. The splice-equality
guard is KEPT but re-pinned to the **NEW** anchors.

Splice mechanics verified at plan time:
- Source `## ACTION ITEM` section: `260902-vsp-.../CONTENT-SPEC.md` lines **117–124**
  (`## SCOPE CAVEATS` follows at 126).
- `## ARTIFACTS` is at source line **7**, so the section is **inside** the spliced region and
  the fix propagates into the appendix automatically.
- Pre-fix: appendix region == source `## ARTIFACTS`→EOF, both 10427 B, sha256 `3a8371b0…`.

### ⚠ F-5 — A SPEC EDITING ARTIFACT IN PART A2. RESOLVE AS STATED; DO NOT IMPROVISE.

The updated spec's PART A2 contains a leftover fragment from its pre-revision wording:

> "Where the record discusses heterogeneity, ADD *"merging correlated units should REMOVE
> manufactured dispersion; it increased to 2.62x; therefore the heterogeneity is between
> parents"* — STRIKE THE ARGUMENT, KEEP THE CONCLUSION. Replace with:"

Read literally, that says **add the false argument**. That cannot be the intent: it
contradicts the same section's heading ("**THIS IS AN ADDITION, NOT A STRIKE** … a PURE
ADDITION of *the corrected statistical position*"), it would reintroduce `2.62`, and it would
write a known-false claim into a record this task exists to correct.

**Resolution — add ONLY the indented "Replace with:" block** (the four paragraphs beginning
"That test DOES NOT DISCRIMINATE"). Do **not** add the quoted argument, and do not add the
"STRIKE THE ARGUMENT" instruction text. Record this resolution in the SUMMARY. It is a
recorded reading of an ambiguous authority, not a silent reconciliation.

### ✅ F-3 — BOTH PINS NOW IN SCOPE (PART A1 moves them anyway)

- **(a) courier line 23** pins its splice source at `20fb7fa058b0e0c03ff669706f534349` /
  10672 B / 157 lines. Already drifted (source is now `5bfbfadffd7a7383e6e9c7047e0c983a` /
  10729 B / 158 lines, from `ee3af4b`), and Task 2's source fix moves it **again**. Refresh
  to the true post-task values.
- **(b) `.planning/STATE.md:45`** pins the courier at "491 lines, md5
  `e2c0b5443bf82a12940d492fefb1f282`". Both change. Refresh.

A pin whose subject has moved is a false invariant. Every pin this task moves, it refreshes.

### ℹ F-4 — DEFERRED, with the wider scope recorded (report-only)

The withdrawn-policy labelling defect spans **two** files, not one:
- `condition_ld_matrix.py:4` and `:153` — cite `tcujq` as pre-registering the NaN→0 policy.
- `write_conditioned_ld_npz.py:4`, `:17`, `:85` — call the same ceiling "pre-registered".

`.planning/osf_deviations.md:133` and `:166` record that the 2026-07-10 update (`trsx5`)
**withdraws exactly that policy**. Record both files in `deferred-items.md`. Do **not** fix —
touches `src/`.

### ✅ Premise check — every tree fact the correction asserts was verified at plan time

| assertion (CONTENT-SPEC PART A1) | measured |
|---|---|
| `_OCCLUSION_ANOMALY_FRACTION` removed, 0 hits in `src/`+`tests/` | 0 hits ✅ |
| `OCCLUSION_SITE_FRACTION_CEILING = 0.005056` in `src/python/occlusion_gate_constants.py` | line 61 ✅ |
| `OCCLUSION_INFLATION_CEILING = 3.42` in same file | line 66 ✅ |
| `condition_ld_matrix.py` contains `occlu` zero times | 0 ✅ |
| `condition_ld_matrix.py` cites the `tcujq` amendment at :3-4 and :153 | lines 4, 153 ✅ |
| `pairwise_completeness_scan.py:45` calls the bound "withdrawn" | line 45 ✅ |
| `osf_deviations.md:133`/`:166` record `trsx5` withdrawing NaN→0 | ✅ |

The correction rests on checked premises, not on a grep of a literal — which is precisely the
root cause it names.
</planning_findings>

<tasks>

<task type="auto" id="1">
  <name>Task 1: STOP GATE — pin all four anchors, snapshot originals, arm the negative controls</name>
  <files>(reads only; writes only under the scratchpad)</files>
  <action>
Set `SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/260903-ict`
and `mkdir -p "$SCRATCH"`.

**A. Pin FOUR anchors. ANY mismatch = STOP, edit nothing, report.**

| file | md5 | lines | bytes |
|---|---|---|---|
| `260903-ict-.../CONTENT-SPEC.md` (**this task's spec**) | `20d3b287c3f5bbea5104d79f67b710a8` | 225 | 14917 |
| courier record | `e2c0b5443bf82a12940d492fefb1f282` | 491 | 30995 |
| `260902-vsp-.../CONTENT-SPEC.md` (**splice SOURCE**) | `5bfbfadffd7a7383e6e9c7047e0c983a` | 158 | 10729 |
| `.planning/osf_deviations.md` | `c37ccbd34e5af67663413d1dd264e0ae` | 530 | 40052 |

⚠ If this task's spec hashes to `dbd3d8a0129716a224d207c80c546f15` / 193 lines, that is the
SUPERSEDED r1 spec — STOP.

**B. Snapshot the originals** into `$SCRATCH/` as `courier.orig.md`, `vsp_spec.orig.md`,
`osf_deviations.orig.md`, `STATE.orig.md`. These are the `cmp` baselines. Scratch only —
never committed.

**C. Record the PRE-fix splice equality** (so the re-splice is provably a re-splice and not a
retype): appendix region (between the BEGIN marker line and the `END` marker) == source
`## ARTIFACTS`→EOF, both **10427 B**, sha256 `3a8371b08a78f7b2…`. Confirm True before editing.

**D. Prove F-1 in this executor's own shell.** Case-insensitively count on the courier:
`collaps`, `parent`, `2\.62`, `leave.one.out`, `2\.48`, `0\.0063`. All must be **0**. Paste
the table into the SUMMARY. Any non-zero → STOP; F-1's premise has changed and A2 may be a
real strike.

**E. Prove F-2's staleness in-shell:** `pre-registered value` must be **0** in the whole
record and **0** in the appendix. If non-zero, the note at 290–294 is NOT stale — STOP and
report, because PART A3 would then be deleting a live note.

**F. Arm negative controls** — copy `courier.orig.md` → `courier.negctl.md` and
`osf_deviations.orig.md` → `osf.negctl.md` for Task 8 to mutate.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
md5sum .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/CONTENT-SPEC.md \
       .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
       .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md \
       .planning/osf_deviations.md
# expect: 20d3b287c3f5bbea5104d79f67b710a8 / e2c0b5443bf82a12940d492fefb1f282 /
#         5bfbfadffd7a7383e6e9c7047e0c983a / c37ccbd34e5af67663413d1dd264e0ae
    </automated>
  </verify>
  <done>All four md5s match; snapshots exist; pre-fix splice equality confirmed; F-1 six zero-counts and F-2 staleness re-proven in-shell; negative controls staged.</done>
</task>

<task type="auto" id="2">
  <name>Task 2: PART A1 (source) — correct the false action item AT SOURCE in the splice spec</name>
  <files>.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md</files>
  <action>
This is the `ee3af4b` pattern, step 1 of 3. Replace the source's
`## ACTION ITEM (flag it; do NOT fix it in this docs-only task)` section — **lines 117–124**,
stopping before the blank line preceding `## SCOPE CAVEATS` at 126 — so it states the
CORRECTION rather than the false claim.

New content, in substance (this file's style is plain/indented, not the courier's bolded
markdown — match the surrounding sections):

  - Heading: `## CORRECTION — the 0.0005 "contradiction" was FALSE; the two constants are unrelated`
  - The two `0.0005` values are **different, unrelated constants**.
  - `_OCCLUSION_ANOMALY_FRACTION = 0.0005` (commit `d9fbc63`) was the OCCLUSION gate:
    genuinely withdrawn, and **REMOVED — 0 hits in `src/` and `tests/`**. Replaced by the
    POSTED two-condition gate (`mk7ze`): `OCCLUSION_SITE_FRACTION_CEILING = 0.005056` and
    `OCCLUSION_INFLATION_CEILING = 3.42`, both in `src/python/occlusion_gate_constants.py`.
  - `condition_ld_matrix.py`'s `ceiling_frac = 0.0005` is the **LD-matrix NaN-zeroing**
    ceiling (`n_zeroed_pairs <= ceiling_frac * n_var`). That file contains `occlu`
    **zero** times.
  - Therefore `pairwise_completeness_scan.py:45` calling the occlusion bound "withdrawn" is
    **CORRECT**. There is no contradiction.
  - ROOT CAUSE: the original action item grepped the literal `0.0005` and treated textual
    co-occurrence as semantic identity.
  - A SEPARATE, REAL defect remains, DEFERRED (touches `src/`, not fixed here):
    `condition_ld_matrix.py:3-4` and `:153` cite `tcujq` as PRE-REGISTERING the NaN→0 policy
    that `trsx5` withdrew (`.planning/osf_deviations.md:133`, `:166`). Accurate label:
    "parameter of a withdrawn policy, retained in a frozen module, not called in production."

⚠ **CONSTRUCTION RULE — load-bearing for G-A1, which is now WHOLE-FILE.** This text lands in
the appendix by splice, so it MUST NOT contain the two-word string `LIVE CONTRADICTION` in
any case. Write "the alleged contradiction", "the superseded claim", "was FALSE". If a guard
later needs an exception for this prose, the prose broke the rule: **fix the prose, not the
guard.**

Do not touch anything else in this file. In particular the `## ARTIFACTS` heading at line 7
must stay byte-identical — it is the splice anchor.

**Then record the source's POST-fix anchors** (md5, bytes, lines) for Task 3's pin refresh
and for the SUMMARY.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
P=.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
grep -ci "live contradiction" "$P"      # expect 0
grep -c "^## ARTIFACTS" "$P"            # expect 1 (splice anchor intact)
grep -c "0.005056" "$P"                 # expect >=1
grep -c "occlu" "$P"                    # expect >=1 (the correction names it)
md5sum "$P"; wc -l -c "$P"              # record POST-fix anchors
    </automated>
  </verify>
  <done>The source's action item now states the correction; `live contradiction` = 0 in the source; the `## ARTIFACTS` anchor is intact; post-fix anchors recorded.</done>
</task>

<task type="auto" id="3">
  <name>Task 3: PART A1 (body) + PART A3 — correct the body section, delete the stale note, refresh the splice-source pin</name>
  <files>.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md</files>
  <action>
Three body edits. All are strictly **before** the `BEGIN VERBATIM APPENDIX` marker; the
appendix is handled by Task 4's splice, never by hand.

**Edit 1 — PART A3: DELETE the stale wording note, courier lines 290–294**, together with the
blank line that separates it from the preceding paragraph (leave exactly one blank line
between "…No consoling clause is appended." and the next heading). The note begins
"⚠ One wording note, so the appendix is not read as a contradiction…" and ends "…an INVARIANT
CHECK, not a pre-registration."

It describes a state that no longer exists (F-2: `pre-registered value` = 0 everywhere), and
leaving it invites a future reader — as it already misled this task's r1 planner — to treat
"leave it and add a note" as the governing precedent when the actual precedent is **fix at
source and re-splice**. Delete it outright. Do **not** replace it with another note.

**Edit 2 — PART A1 body: replace lines 296–313**, the section
`## ACTION ITEM — THE 0.0005 BOUND IS A LIVE CONTRADICTION (NOT FIXED HERE)` through its last
line, stopping before the blank line preceding `## THE ASK`. Content from CONTENT-SPEC.md
PART A1 (the same substance as Task 2, in the courier's bolded-markdown style): the two
constants are different and unrelated; `_OCCLUSION_ANOMALY_FRACTION` withdrawn and REMOVED
(0 hits), replaced by the posted `0.005056` + `3.42` gate; `ceiling_frac` is the LD-matrix
NaN-zeroing ceiling and `condition_ld_matrix.py` contains `occlu` zero times; therefore
`pairwise_completeness_scan.py:45` is CORRECT; ROOT CAUSE as stated; and the DEFERRED `tcujq`
docstring defect.

Suggested heading:
`## CORRECTION — THE 0.0005 ACTION ITEM WAS FALSE; THE TWO CONSTANTS ARE UNRELATED`

Keep the existing DOCS-ONLY sentence ("`git status --porcelain -- src tests` is empty at
commit time") — still true, still load-bearing.

⚠ Same **CONSTRUCTION RULE**: this prose MUST NOT contain `LIVE CONTRADICTION` in any case.

**Edit 3 — F-3a: refresh the splice-source pin at line 23.** It currently reads
"(md5 `20fb7fa058b0e0c03ff669706f534349`, **10672** B, 157 lines)". Write Task 2's **post-fix**
source anchors. Do not write the pre-fix `5bfbfadf…` values — those were true only between
`ee3af4b` and Task 2.

⛔ Do **NOT** hand-edit anything at or after the `BEGIN VERBATIM APPENDIX` marker.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
B=$(awk '/^<!-- BEGIN VERBATIM APPENDIX/{exit} {print}' "$F")
printf '%s\n' "$B" | grep -ci "live contradiction"          # expect 0
printf '%s\n' "$B" | grep -ci "One wording note"            # expect 0  (A3: note deleted)
printf '%s\n' "$B" | grep -c "0.005056"                     # expect >=1
printf '%s\n' "$B" | grep -c "tcujq"                        # expect >=1 (deferred note)
printf '%s\n' "$B" | grep -c "20fb7fa058b0e0c03ff669706f534349"  # expect 0  (stale pin gone)
sed -n '23p' "$F"                                            # pin shows Task 2's post-fix values
    </automated>
  </verify>
  <done>The stale note is gone; the body correction is in place with 0 hits for the banned phrase; line 23 pins the post-fix source anchors; nothing at or after the BEGIN marker was hand-edited.</done>
</task>

<task type="auto" id="4">
  <name>Task 4: PART A1 (splice) — re-splice the appendix from the corrected source, BY SCRIPT</name>
  <files>.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md</files>
  <action>
Step 3 of the `ee3af4b` pattern. **Spliced by script, never retyped** — that is what makes
byte-equality evidence that no number was re-keyed.

⚠ **Locate the markers by PATTERN, not by line number.** Task 3 changed the body's length, so
338/491 are stale. Use the marker strings.

```python
import pathlib
F = pathlib.Path(".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md")
P = pathlib.Path(".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md")
BEGIN = "<!-- BEGIN VERBATIM APPENDIX (byte-equal to CONTENT-SPEC.md from '## ARTIFACTS' to EOF) -->\n"
END   = "<!-- END VERBATIM APPENDIX -->"
c = F.read_text(encoding="utf-8")
s = P.read_text(encoding="utf-8")
spec = s[s.index("## ARTIFACTS"):]          # '## ARTIFACTS' .. EOF, ends with a newline
i = c.index(BEGIN) + len(BEGIN)
j = c.index(END, i)
F.write_text(c[:i] + spec + c[j:], encoding="utf-8")
```

Then **re-verify and re-anchor**:
1. Re-extract the appendix region and assert it is **byte-equal** to `spec`. Record the new
   byte length and sha256 — these SUPERSEDE 10427 B / `3a8371b0…`.
2. Assert `LIVE CONTRADICTION` is now **0** in the WHOLE courier file (this is the moment
   G-A1 becomes satisfiable).
3. Record the courier's post-splice md5 and line count for Task 7's STATE pin.

Sanity check that the splice was a true replacement, not a duplication or truncation: exactly
one `BEGIN VERBATIM APPENDIX` and one `END VERBATIM APPENDIX` remain, and `## ARTIFACTS`
appears exactly once inside the appendix region.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
grep -ci "live contradiction" "$F"                 # G-A1 WHOLE-FILE: expect 0
grep -c "BEGIN VERBATIM APPENDIX" "$F"             # expect 1
grep -c "END VERBATIM APPENDIX" "$F"               # expect 1
python3 - <<'PY'
import pathlib
F=pathlib.Path(".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md")
P=pathlib.Path(".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md")
BEGIN="<!-- BEGIN VERBATIM APPENDIX (byte-equal to CONTENT-SPEC.md from '## ARTIFACTS' to EOF) -->\n"
END="<!-- END VERBATIM APPENDIX -->"
c=F.read_text(encoding="utf-8"); s=P.read_text(encoding="utf-8")
i=c.index(BEGIN)+len(BEGIN); j=c.index(END,i)
print("SPLICE BYTE-EQUAL:", c[i:j]==s[s.index("## ARTIFACTS"):], len(c[i:j]),"B")
PY
    </automated>
  </verify>
  <done>Appendix re-spliced by script and byte-equal to the corrected source; `LIVE CONTRADICTION` = 0 in the whole file; exactly one BEGIN/END pair; new splice anchors recorded.</done>
</task>

<task type="auto" id="5">
  <name>Task 5: PART A2 — add the heterogeneity correction (addition, no deletion; see F-1 and F-5)</name>
  <files>.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md</files>
  <action>
Per **F-1** nothing is deleted. Add a new body subsection immediately after
`## FINDING 2 — THE REGIONS DO NOT SHARE A COMMON POST RATE` (before `## FINDING 3`).
Suggested heading: `### WHAT DOES AND DOES NOT ESTABLISH THE HETEROGENEITY`

Per **F-5**, add **only** the spec's indented "Replace with:" block — the four paragraphs
below. Do **NOT** add the spec's quoted struck argument or its "STRIKE THE ARGUMENT"
instruction text; that fragment is a spec editing artifact.

  - **A test we ran does NOT discriminate, and is withdrawn.** For a chi-square homogeneity
    statistic the contribution of a deviation scales with the denominator, so merging two
    same-rate sub-windows holds chi-square roughly constant while removing a degree of
    freedom — the ratio rises **by construction**. Simulated under the rival hypothesis being
    TRUE: collapse raises dispersion in **65%** of runs, median **+3.6%**. Same direction
    under both hypotheses, so it distinguished nothing.
  - **THE VALID REFUTATION (Seth's, not ours):** non-independence cannot **CREATE**
    dispersion, only amplify dispersion already present at parent level. Simulated: parent
    rates ALL EQUAL + duplication → dispersion **0.98**. An observed ~2x therefore REQUIRES
    real parent-level heterogeneity.
  - **STILL VALID AND RETAINED:** leave-one-out over 21 fits — overdispersion **1.99–2.48**,
    worst-case p **0.0063** — independently rules out a single influential point.
  - **READER-FACING TRANSLATION:** overdispersion ~2.0 corresponds to parent-rate
    **CV ≈ 0.20**, i.e. roughly **20%** relative variation in tail rate between parent
    regions. (Our simulation; CV 0.25 gives **2.54**. Seth proposed 0.25–0.30 — corrected
    **downward**.)
  - One sentence recording that the withdrawn argument was ours and was never written into
    this record, so a reader who met it in correspondence knows its disposition.

⚠ **CONSTRUCTION RULE — load-bearing for G-A2.** State that the collapse test does not
discriminate; do **NOT restate the struck inference**. No sentence may assert that collapsing
to parents *removed* manufactured dispersion, or that a rise to `2.62x` demonstrates
parent-level heterogeneity. **The numeral `2.62` must not appear anywhere in the file.**
`2.62` is the struck argument's fingerprint — it occurs nowhere legitimate in the repo — so
its absence is a clean discriminator that a `collaps` substring grep cannot give, because the
corrected prose necessarily says "collapse".

The headline elsewhere stays **1.99x**: this removes an argument, not the conclusion. Do not
touch the FINDING 2 table or the `+0.886` power clause.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
grep -c "2\.62" "$F"                                    # G-A2 fingerprint: expect 0
B=$(awk '/^<!-- BEGIN VERBATIM APPENDIX/{exit} {print}' "$F")
for pat in "does not discriminate" "65%" "3.6%" "0.98" "2.48" "0.0063" "1.99" "0.886"; do
  printf '%s => ' "$pat"; printf '%s\n' "$B" | grep -ci -- "$pat"
done                                                     # each expect >=1
    </automated>
  </verify>
  <done>The subsection is present with all seven numbers; `2.62` appears zero times file-wide; the FINDING 2 headline and the +0.886 power clause are unchanged; the F-5 resolution is recorded.</done>
</task>

<task type="auto" id="6">
  <name>Task 6: PART B — append the tail DISCLOSURE to osf_deviations.md (PURE APPEND)</name>
  <files>.planning/osf_deviations.md</files>
  <action>
**Append only.** Do not touch lines 1–530. The file ends with a newline, so append cleanly:
one blank line, then the entry.

Heading, verbatim from CONTENT-SPEC:
`## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure (measured characterisation; NO amendment, NO predicate change, NO carrier floor)`

Match the 2026-08-22 entry's conventions at `:422` — `## YYYY-MM-DD — TITLE`, bolded-lead
bullets, sub-headings for grouped material.

⛔ **NOT-POSTED discipline.** The 2026-08-22 entry opens `**Posted:** OSF file mk7ze …`. This
entry **MUST NOT** carry a `**Posted:**` lead, and must carry, near the top and unmissable:

`**Status:** DRAFTED — NOT POSTED; placement and posting are Carter's.`

Naming `mk7ze` / `trsx5` / `tcujq` is fine and required — those are existing posted records
being cited. Prohibited: any line asserting *this* entry was posted, or inventing a GUID.

Reproduce all nine blocks from CONTENT-SPEC PART B, copying every number exactly:

1. **DISPOSITION, adjudicated** — DISCLOSE + ANNOTATE, no amendment; the two disclosure
   targets; why (ii) is additive provenance under clause (c); why a carrier floor later WOULD
   be an amendment.
2. **WHAT WAS MEASURED** — 21 regions, 3,094 defined tail rows at
   `max(carriers_lost_frac) >= 0.9`; ROWS 2560 PRE / 534 POST of 3094 = **17.26%**; PAIRS
   2047 PRE / 474 POST of 2521 = **18.80%**; regions with tail rows **21**, with zero POST
   rows **0**; overdispersion **1.99x** (chi2 37.78, dof 19, p 6.3e-3) after dropping the
   chr15 double-count; rho **-0.199 / -0.201 / +0.004** against **+0.886**; ~20% relative
   variation; definitional axis **24.27%** vs **0.52%** = **46.5x**, independent at rho
   **+0.173**.
3. ⭐ **THE SURVIVOR GEOMETRY — headline, and a POSITIVE result for the rule.**
   `m2_region_00149`, `chr7:89454077:GCGTA:G` (REF len 5, span 89454077..89454081) ×
   `chr7:89454076:C:T`, offset **-1**, upstream, `already_occluded` False, pair_key
   `9776035|9776036`. Predicate `d.pos < v.pos`: `89454077 < 89454076` = FALSE — invisible by
   construction, and the only surviving direction; offset histogram
   `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`. ⛔ NO PREDICATE CHANGE; the ~0.12% cheapness is an
   argument AGAINST (calibrate-to-pass at n=1). Record the REGISTERED PREDICTION verbatim:
   *"Residual undefined-r is expected EXCLUSIVELY at negative offsets. A positive-offset
   survivor would falsify predicate completeness in the downstream direction."*
4. ⭐ **SCOPE OF mk7ze LINE 275 — a RECORDED COMMITMENT.** Quote line 275 and clause (a) at
   line 467 as given. Its argumentative work is carried by "but not conversely"; the survivor
   is outside the sentence's domain, not a counterexample within it. Include the ⚠ paragraph
   on why this is written down rather than left as an interpretation (mk7ze §(a)'s remedy was
   explicit scoping in the record, converting a narrow reading from a defence into a
   commitment).
5. ⭐ **RECORDING THE SILENCE.** The 598-line posted body sweep: ZERO hits for "defined row",
   "finite r", "degraded", "precision", "SE(". A silence, not a false statement — nothing in
   the posted record is falsified. Include the quoted "in substance" paragraph (one undefined
   pair with no covering deletion; 474 degraded pairs across 21 regions; neither class claimed
   against, both reported so the silence is not read as coverage).
6. **NO CARRIER FLOOR — the definition PINNED before one exists.** 📌 Any floor MUST be defined
   on min-on-the-pairwise-complete-INTERSECTION, NEVER rarer-by-overall-MAF; they disagree on
   ~24% of exactly the rows a floor exists to catch. Mechanism: occlusion strips ~99.4–99.9%
   of the deletion's carriers on the intersection, inverting the rank — which is why the
   definitional disagreement is a signature of the first finding, not a third phenomenon.
7. **THE NEGATIVE RESULT, registered.** Three correlates, none found, in a design returning
   +0.886. Stronger than an unexamined null because both artifact explanations were eliminated
   (0.98 under equal parent rates; leave-one-out 1.99–2.48, worst p 0.0063). ⛔ Do NOT
   pre-register a dispersion FIGURE.
8. **EPISTEMIC STATUS — do not soften.** MEASURED, NOT PRE-REGISTERED; the governing
   document's deliberate refusal to state an expected value; the genuine pre-registration is
   `260826-…prereg-prediction.md` §(e), confirmed 5/5 + histogram, zero adjustments,
   2026-09-01; **3094/0/0 are a COMPLETION CHECK, NOT a pre-registration**; the VM-reboot
   blackout, unrecoverable stdout/`$?`, md5s anchor FORWARD not backward.
9. **PROVENANCE.** `pcs_tail_verdicts.tsv` md5 `960f283734aea3b2c56c9249cf4fe94b`, 1031086 B;
   `pcs_tail_summary.json` md5 `bd74c0d502d15ac4e2fb5e1bdafc72b1`, 38548 B; both written
   2026-09-02T21:07:03Z, launched 18:26:17Z, 2h40m46s wall; `bim_sha256 9cc378b7…feeeb99`
   (20,767,864 lines); `pairs_tsv_sha256 eb2de2fd…123583` (353,090 lines);
   `regions_tsv_sha256 e3c25ea0…ce4d6a` — VERIFIED equal to `sha256sum config/ld_regions.tsv`
   at HEAD. State explicitly that `region_ids_selected = 276` is the ancestry-resolved
   MANIFEST size, **not** the 21 regions carrying rows.

⚠ Do not "improve" any number, do not round, do not convert `6.3e-3` to `0.0063` or back —
copy the notation the spec uses in each place.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
S=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/19c6a323-a3ca-4c18-bffc-bfcb052f7fe3/scratchpad/260903-ict
head -530 .planning/osf_deviations.md > "$S/osf.head530"
cmp "$S/osf.head530" "$S/osf_deviations.orig.md" && echo "G-B1 PURE-APPEND OK"
tail -n +531 .planning/osf_deviations.md > "$S/osf.new"
grep -c "DRAFTED — NOT POSTED" "$S/osf.new"     # expect >=1
grep -c '^\*\*Posted:\*\*' "$S/osf.new"         # expect 0
git status --porcelain -- .planning/amendments/  # expect EMPTY
    </automated>
  </verify>
  <done>`cmp` reports the first 530 lines identical; the new region carries DRAFTED — NOT POSTED and no `**Posted:**` lead; `.planning/amendments/` clean.</done>
</task>

<task type="auto" id="7">
  <name>Task 7: PART C — STATE.md row, pin refresh, queued-fix status, and deferred-items.md</name>
  <files>.planning/STATE.md, .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/deferred-items.md</files>
  <action>
**A. One quick-task row.** Insert immediately after line 2353 (the `260902-vsp` row), before
the blank line preceding `## Session Continuity`. This is a **mid-file insert** — STATE.md is
3121 lines and continues well past the table.

Match the existing shape exactly: **7 pipes / 6 cells**, ending with the directory link. The
header declares `| # | Description | Date | Commit | Status | Directory |`; copy
`260902-vsp`'s literal shape rather than the header's nominal one.

```
| 260903-ict | **<description>** | 2026-09-03 | <commit-sha> | Inline (docs-only; fixed at source + re-spliced; pure-append + all negative controls observed RED) | [260903-ict-strike-two-false-passages-from-the-run-2](./quick/260903-ict-strike-two-false-passages-from-the-run-2/) |
```

The description must state: the false `0.0005` action item was corrected **at source and
re-spliced** (`ee3af4b` pattern), so `LIVE CONTRADICTION` is now 0 in the whole record,
appendix included; the stale wording note was **deleted** (it advertised a superseded
leave-it-and-note-it policy and had already misled a planner); the heterogeneity correction
was an **ADDITION** because the argument was never in the record (F-1); the tail disclosure
was appended as DRAFTED — NOT POSTED; nothing posted, no VM, `src/`+`tests/` untouched.

The commit SHA is known only after Task 8. Write a placeholder and `git commit --amend` once —
**one commit total**; do not create a second commit for the SHA.

**B. Refresh the pin at `.planning/STATE.md:45`** ("— 491 lines, md5
`e2c0b5443bf82a12940d492fefb1f282`") to the post-task courier values from Task 4.

**C. Update the "Three repo fixes QUEUED, NOT DONE" block** (~lines 70–73): items 1 and 2 are
DONE by this task; item 3 (`condition_ld_matrix.py` docstring) remains QUEUED and touches
`src/`. Note that item 3's scope is **wider than stated** — see F-4.

**D. Optionally correct STATE.md:54** if it still frames the collapse argument as needing to
be struck *from the record*: it was never in the record. Keep it factual; do not delete the
finding.

⛔ Do NOT backfill `260828-uej`, `260831-kw8`, `260901-l55`, `260901-rvu`.

**E. Write `deferred-items.md`**, recording each finding as *not fixed here* with what would
discharge it:

  1. **The withdrawn-policy docstring defect — TWO files (F-4).**
     `condition_ld_matrix.py:4`, `:153` cite `tcujq` as pre-registering the NaN→0 policy;
     `write_conditioned_ld_npz.py:4`, `:17`, `:85` call the same ceiling "pre-registered".
     `osf_deviations.md:133`, `:166` record that `trsx5` withdrew exactly that policy.
     Accurate label: "parameter of a withdrawn policy, retained in a frozen module, not called
     in production." Touches `src/`. Discharge: fix both files in one task **plus a named
     enforcer test** — a claimed invariant with no named enforcer is belief only.
  2. **The four missing STATE quick-task rows** — `260828-uej`, `260831-kw8`, `260901-l55`,
     `260901-rvu`. Carried forward from `260902-vsp`'s deferred-items; out of scope by
     instruction.
  3. **Note that F-3a is now CLOSED, not deferred** — the courier's splice-source pin was
     refreshed by Task 3, because Task 2 moved it anyway. Record it so the next reader does
     not re-open it.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
F=.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
# G-E1: the stale courier md5 survives ONLY inside this task's own directory
grep -rn "e2c0b5443bf82a12940d492fefb1f282" .planning --include=*.md \
  | grep -v "^\.planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/" | wc -l   # expect 0
md5sum "$F"; wc -l "$F"; sed -n '45,46p' .planning/STATE.md   # pin agrees with the file it pins
grep -c "^| 260903-ict |" .planning/STATE.md                  # expect 1
grep -c "^| 260828-uej |\|^| 260831-kw8 |\|^| 260901-l55 |\|^| 260901-rvu |" .planning/STATE.md  # expect 0
test -s .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/deferred-items.md && echo "deferred-items OK"
    </automated>
  </verify>
  <done>One `260903-ict` row; STATE:45 pins post-task values; the old md5 appears nowhere outside this task dir; fixes 1-2 marked done with 3 left queued and widened; deferred-items.md written.</done>
</task>

<task type="auto" id="8">
  <name>Task 8: Full verification battery with negative controls SEEN RED, then one commit</name>
  <files>(verification only, then git commit)</files>
  <action>
**Every guard runs GREEN on the real tree, and its negative control runs on a scratch copy and
MUST be observed RED. A green assertion you have never seen fail is not evidence.** Paste both
outcomes into the SUMMARY. Never mutate a tracked file for a negative control — mutate
`$SCRATCH/*.negctl.md` only.

| id | guard (GREEN on real tree) | negative control (MUST go RED) |
|----|---------------------------|-------------------------------|
| G-A1 | **WHOLE courier file** has **0** hits for `live contradiction`, case-insensitive — appendix included | reinsert the old heading into `courier.negctl.md` → count ≥1 |
| G-A1b | splice **source** spec has **0** hits for `live contradiction` | reinsert it into a scratch copy of the source → count ≥1 |
| G-A2 | whole courier has **0** hits for `2\.62` | insert `overdispersion rose to 2.62x` into `courier.negctl.md` → count ≥1 |
| G-A3 | body contains `1.99`, `2.48`, `0.0063`, `0.98`, `65%`, `3.6%`, `0.886` | delete `2.48` and `0.0063` from `courier.negctl.md` → presence check fails |
| G-A4 | appendix region is **byte-equal** to the corrected source `## ARTIFACTS`→EOF (NEW anchors from Task 4, superseding 10427 B / `3a8371b0…`); exactly one BEGIN and one END marker | change one character inside `courier.negctl.md`'s appendix → equality fails |
| G-A5 | the stale note is gone: **0** hits for `One wording note` | reinsert the note into `courier.negctl.md` → count ≥1 |
| G-B1 | `cmp` of `head -530` against `osf_deviations.orig.md` → identical | flip one byte on line 100 of `osf.negctl.md` → `cmp` differs |
| G-B2 | new region (`tail -n +531`) contains `DRAFTED — NOT POSTED` and **0** lines matching `^\*\*Posted:\*\*` | add a `**Posted:** OSF file xxxxx` line to the scratch new-region → count ≥1 |
| G-C1 | `git status --porcelain -- src tests` is **EMPTY** | `touch src/python/__negctl_probe.py` → non-empty; then `rm` and re-confirm empty |
| G-C2 | `git status --porcelain -- .planning/amendments/` is **EMPTY** | (covered by G-C1's demonstration of the idiom) |
| G-E1 | old courier md5 appears **0** times outside this task's directory | show the out-of-task count is 0 while the in-task count is ≥0, proving the scope is real |
| G-E2 | courier line 23's source pin equals the **live** `md5sum`/`wc` of the splice source | point the scratch pin at a wrong md5 → mismatch |

⚠ **Scoping notes, so they are not rediscovered the hard way.**
  - **G-A1 is WHOLE-FILE, not body-scoped.** The r1 plan scoped it to the body because it
    proposed leaving the appendix copy standing; that remedy was reversed. Fixing at source
    and re-splicing makes the whole-file guard satisfiable, which is the point: the guard was
    right and the r1 remedy was wrong.
  - **G-A1 needs no "exclude the correction's own prose" clause**, because Tasks 2/3/5
    forbid the banned strings from the correction entirely. That is stronger than a scoped
    grep — the trap is removed by construction. **If the executor finds itself needing an
    exception for the correction's prose, the prose violated its construction rule: fix the
    prose, not the guard.**
  - **G-E1 IS scoped** — the SUMMARY legitimately quotes the pre-edit md5 as a "was" value —
    so it excludes this task's directory and nothing else.
  - **G-A2 uses `2.62`, not `collaps`**, because the corrected prose must say "collapse" to
    state that the test does not discriminate. `2.62` is the struck claim's fingerprint.

**Also confirm by READING (a grep matches text, not meaning):** the new heterogeneity
subsection nowhere asserts that collapsing removed dispersion or that a rise demonstrates
parent-level heterogeneity; and the re-spliced appendix's correction reads correctly in
context. State in the SUMMARY that this was checked by reading — do not claim a grep proved it.

**Write the SUMMARY** at
`.planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/260903-ict-SUMMARY.md`:
the Task-1 four-anchor table; the F-1 zero-hit table measured in-shell; the F-2 reversal (r1's
supersession-note remedy rejected; `ee3af4b` fix-at-source pattern applied) with pre- and
post-splice byte-equality evidence; the F-5 spec-artifact resolution; PART A2 executed as an
addition; the deleted stale note; every pin moved and its new value; the guard table with both
green and RED outcomes; the deferred items; and the statement that nothing was posted, no VM
was started, `$0` spend.

**Commit — ONE commit, explicit paths, NO push, NO `git add -A`.**

```
git add .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
        .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md \
        .planning/osf_deviations.md \
        .planning/STATE.md \
        .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/260903-ict-PLAN.md \
        .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/CONTENT-SPEC.md \
        .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/260903-ict-SUMMARY.md \
        .planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/deferred-items.md
```

Afterwards `git status --porcelain` must still show
`?? .planning/debug/m3-producer-unbounded-dense-read.md` untracked, and `git log --oneline -1`
must show exactly one new commit. **Do not push.**

⚠ **If `git commit` fails with `invalid object` / `Error building trees`** — the known GPFS
loose-object loss (3 hits in ~3 weeks). Recipe from `.planning/HANDOFF.json`
(`gpfs_object_store_recovery_recipe`): for each `git ls-files -s` entry test
`git cat-file -e <sha>`; for misses re-hash the intact working-tree file via
`git hash-object -w <path>`; then commit. The recipe notes the local store is unreliable and
normally says push — **this task is NO PUSH, so flag to Carter instead of pushing.** Never
work around it with `git add -A`.
  </action>
  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
git status --porcelain -- src tests             # MUST be empty
git status --porcelain -- .planning/amendments/  # MUST be empty
git log --oneline -1
git status --porcelain | grep -c "^ M\|^M "     # expect 0
    </automated>
  </verify>
  <done>All twelve guards GREEN and every negative control observed RED; SUMMARY written; exactly one commit on `m3-W2-aou-deltas`; `src`/`tests`/`amendments` clean; producer-debug file still untracked; nothing pushed.</done>
</task>

</tasks>

<commit_message>
Use exactly this, via `git commit -F <file>` (the body contains characters a shell `-m` chain
will mangle):

```
docs(quick-260903-ict): correct the false 0.0005 action item AT SOURCE and re-splice, delete a stale wording note, add the heterogeneity correction, and bank the tail DISCLOSURE as DRAFTED — NOT POSTED

PART A1 — the "0.0005 bound is a LIVE CONTRADICTION" action item was FALSE and is replaced
by a CORRECTION, fixed AT SOURCE and re-spliced per the ee3af4b pattern rather than masked
behind a note. The two constants are different and unrelated: _OCCLUSION_ANOMALY_FRACTION =
0.0005 (d9fbc63) was the OCCLUSION gate — genuinely withdrawn and REMOVED, 0 hits in src/
and tests/, replaced by the posted mk7ze gate (OCCLUSION_SITE_FRACTION_CEILING = 0.005056,
OCCLUSION_INFLATION_CEILING = 3.42). condition_ld_matrix.py's ceiling_frac = 0.0005 is the
LD-matrix NaN-zeroing ceiling; that file contains "occlu" zero times. pairwise_completeness_scan.py:45
calling the occlusion bound "withdrawn" is CORRECT. ROOT CAUSE: the original item grepped
the literal 0.0005 and treated textual co-occurrence as semantic identity.

The phrase was fixed in 260902-vsp's CONTENT-SPEC.md (the splice source) and the courier's
VERBATIM APPENDIX was RE-SPLICED BY SCRIPT from the corrected spec, then re-verified
byte-equal and re-anchored. Byte-equality is a MEANS — proof no number was retyped — not an
end; it survives re-anchoring, and preserving a false claim to protect an md5 would be a
guard scoped to a proxy. RESULT: LIVE CONTRADICTION now appears ZERO times in the whole
record, appendix included.

PART A2 was executed as an ADDITION, not a deletion, and this is a recorded deviation from
the spec's wording. The collapse-to-parents argument was never written into the courier —
measured: 0 hits for collaps / parent / 2.62 / leave-one-out / 2.48 / 0.0063. It lived only
in STATE.md and in correspondence. The new subsection states that the collapse test DOES NOT
DISCRIMINATE (it raises dispersion in 65% of runs, median +3.6%, under the rival hypothesis
too), records the valid refutation (equal parent rates + duplication gives 0.98, so
non-independence cannot CREATE dispersion), retains leave-one-out (1.99-2.48, worst p
0.0063), and translates overdispersion ~2.0 to parent-rate CV ~ 0.20. The conclusion
survives; only the argument is withdrawn.

PART A3 — deleted the now-stale wording note that claimed the appendix "still says 'the
three pre-registered values'" and was "reproduced unedited because the appendix is byte-equal
by construction and must not be touched." ee3af4b had already fixed that phrase at source and
re-spliced; measured now, "pre-registered value" occurs 0 times in the record and 0 in the
appendix. The note described a state that no longer existed and advertised a superseded
leave-it-and-note-it policy — it had already misled a planner into proposing exactly that for
this task.

PART B — the tail DISCLOSURE appended to .planning/osf_deviations.md. DISCLOSURE, NOT
AMENDMENT: marked "DRAFTED — NOT POSTED; placement and posting are Carter's", carrying no
**Posted:** lead and no invented GUID. Nine blocks: disposition (disclose + annotate, two
targets); the measurement (2560/534 of 3094 rows = 17.26% POST, 2047/474 of 2521 pairs =
18.80%, 21 regions with tail rows, 0 with zero POST); the survivor geometry promoted to a
headline and stated as a POSITIVE result for the predicate, with NO predicate change and a
registered prediction instead; the explicit scope of mk7ze line 275 recorded as a COMMITMENT;
the posted record's SILENCE recorded so it is not read as coverage; NO carrier floor, with the
definition PINNED to min-on-the-pairwise-complete-intersection before one exists; the negative
result registered without a pre-registered dispersion figure; the epistemic status left
unsoftened (MEASURED, NOT PRE-REGISTERED; 3094/0/0 is a completion check); and full
provenance. PURE APPEND, proven by cmp: the pre-existing 530 lines are byte-identical.

PART C — one STATE.md quick-task row, and every pin this task moved refreshed to a true
post-task value: the courier's splice-source pin at its line 23, and STATE.md:45's courier
md5 and line count. The four missing rows (260828-uej, 260831-kw8, 260901-l55, 260901-rvu)
were NOT backfilled, by instruction.

DOCS-ONLY: git status --porcelain -- src tests EMPTY. The withdrawn-policy docstring defect
is DEFERRED with its full scope recorded — it spans TWO files, condition_ld_matrix.py:4,153
and write_conditioned_ld_npz.py:4,17,85 — and needs a named enforcer test, not just an edit.
Nothing posted, no OSF contact, no VM, $0. Not pushed.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```
</commit_message>

<integrity_risks>
Not a STRIDE surface — no code, no trust boundary, no untrusted input. The threat surface is
**record integrity**, so the register is scoped to that.

| ID | Risk | Disposition | Mitigation |
|----|------|-------------|------------|
| R-01 | Preserving a false claim in the appendix to protect an md5 (the r1 error) | mitigate | Fix at source + re-splice + re-anchor; G-A1 is WHOLE-FILE; byte-equality re-proven against NEW anchors (G-A4) |
| R-02 | Hand-editing the appendix, destroying the "no number was retyped" evidence | mitigate | Task 4 splices BY SCRIPT from the source, locating markers by pattern; Tasks 3/5 forbid edits at/after the BEGIN marker |
| R-03 | A stale note left standing, advertising a superseded policy to future readers | mitigate | PART A3 deletes it; G-A5 proves it gone; the failure it already caused is recorded in the commit message |
| R-04 | A mid-file edit to `osf_deviations.md` corrupting the pre-registration chain | mitigate | G-B1 `cmp` against a Task-1 snapshot, not an eyeball or a line count |
| R-05 | The disclosure being read later as something that was posted | mitigate | G-B2 requires `DRAFTED — NOT POSTED` and forbids a `**Posted:**` lead; posted bodies never edited (G-C2) |
| R-06 | A banned-phrase guard firing on the correction's own prose, then being loosened until it proves nothing | mitigate | Construction rules keep banned strings out of the correction entirely; `2.62` used as the struck claim's fingerprint; plan states: fix the prose, not the guard |
| R-07 | A guard that is green but has never been seen red | mitigate | Twelve guards, each with a paired negative control that MUST be observed RED and pasted into the SUMMARY |
| R-08 | Silently reconciling an authority against the tree when they disagree | mitigate | F-1, F-3 and F-5 surfaced at plan time, executed as recorded readings, and re-proven in the executor's own shell at Task 1D/1E |
| R-09 | A pin left describing a subject that moved (false invariant) | mitigate | G-E1 and G-E2; every pin this task moves, it refreshes — courier line 23 and STATE.md:45 |
| R-10 | Scope creep into `src/` via the "obvious" one-line docstring fix | mitigate | G-C1 with a demonstrated red; the defect is recorded in `deferred-items.md` across BOTH files with a named-enforcer requirement |
| R-11 | Staging collisions on the shared GPFS tree; or `git add -A` used to dodge object-store loss | mitigate | Explicit paths only; recovery recipe inlined in Task 8 with an explicit NO-PUSH deviation |
</integrity_risks>

<success_criteria>
- [ ] Task 1 matched all four anchors (this task's spec at `20d3b287…` / 225 / 14917); any mismatch stopped the task
- [ ] `LIVE CONTRADICTION` = 0 in the WHOLE courier record, appendix included, and 0 in the splice source
- [ ] The correction was made AT SOURCE and the appendix RE-SPLICED BY SCRIPT, byte-equal to the corrected source, re-anchored
- [ ] The stale wording note is deleted (0 hits for `One wording note`); no replacement note added
- [ ] Courier: 0 hits for `2.62` file-wide; the new subsection carries 65% / +3.6% / 0.98 / 1.99–2.48 / 0.0063 / CV≈0.20
- [ ] Courier retains 1.99x and the +0.886 power clause — an argument was removed, not the conclusion
- [ ] `osf_deviations.md` PURE APPEND proven by `cmp`; entry marked DRAFTED — NOT POSTED, no `**Posted:**` lead
- [ ] All nine content blocks present with numbers copied, not recomputed
- [ ] Courier line 23 and STATE.md:45 both pin true post-task values; old courier md5 absent outside this task dir
- [ ] Exactly one `260903-ict` STATE row; no backfill of the four deferred ids
- [ ] `deferred-items.md` records the two-file docstring defect with a named-enforcer requirement
- [ ] Every guard GREEN and every negative control observed RED, both pasted into the SUMMARY
- [ ] `git status --porcelain -- src tests` EMPTY; `.planning/amendments/` EMPTY
- [ ] One commit, explicit paths, no push; `m3-producer-unbounded-dense-read.md` still untracked
</success_criteria>

<output>
`.planning/quick/260903-ict-strike-two-false-passages-from-the-run-2/260903-ict-SUMMARY.md`
</output>
