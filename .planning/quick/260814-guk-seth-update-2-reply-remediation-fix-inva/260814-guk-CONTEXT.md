# Quick Task 260814-guk: Seth UPDATE #2 remediation — Context

**Gathered:** 2026-08-14
**Status:** Ready for planning
**Source document:** `260814-guk-SETH-REPLY.md` (Seth's verbatim reply, banked; read it first)

<domain>
## Task Boundary

Remediate Seth's 2026-08-14 reply to UPDATE #2. One BLOCKING transcription defect in
the trsx5 adjudication card (fire surface), one runbook omission, two record items
(R3 numbers, R4 coverage-gap disclosure obligation), and a reply-to-Seth courier
package. Docs-only, $0, no perimeter contact, no src/tests/config/Snakefile changes.

</domain>

<decisions>
## Implementation Decisions (LOCKED — from Seth's reply + orchestrator verification, do not revisit)

### D1 — The card defect is CONFIRMED, not taken on faith
- The shipped short-body hash string `c19e8b2ad7cd6a45fee1d668d8a9cf9` was counted
  firsthand by the orchestrator on 2026-08-14: **31 hex chars** (`printf | wc -c` = 31).
  An md5 is 32. It can never match ⇒ the STOP-truncated branch could never fire by
  hash comparison. Defect class: a comparison structurally incapable of firing
  (the project's recurring "assertion that cannot fail" class — see
  [[feedback_green_assertion_needs_a_negative_control]]).
- Seth's corrected value `c19be8b2ad7cd6a45fee1d668d8a9cf9` (32 chars, dropped 'b'
  at index 3) is **Seth-reported from the OSF API and UNVERIFIED BY US** — we cannot
  fetch trsx5 (sign-in wall). It must therefore be ADVISORY-ONLY in the card, clearly
  attributed, never an adjudication anchor.

### D2 — Size-first card formulation (Seth's "safest formulation", ADOPTED)
The rewritten card at every executable site must read, in substance:
1. Carter downloads https://osf.io/az52u/files/trsx5 (the file, not the page),
   reports `wc -c` and `md5sum` verbatim.
2. **Adjudicate on byte count FIRST**: any size other than **9,758** or **9,907**
   is a **STOP by itself** (STOP-truncated/anomalous) — no hash comparison required;
   a byte count cannot be mistranscribed into a false pass.
3. Hashes then confirm which known body it is:
   - 9,758 B → expect md5 `28ecdb3160833da80cfa25952f76415b` = repo-canonical paste
     block → **gate PASSES**. (If 9,758 B but md5 differs: STOP — same-size different
     content, report verbatim.)
   - 9,907 B → expect md5 `425d925a88ab474ec2396cbea25e665c` = Seth-complete
     lineage → **STOP-reconcile** lineages before firing.
4. Advisory note only: Seth reports the truncated body's md5 as
   `c19be8b2ad7cd6a45fee1d668d8a9cf9` (32 chars, via OSF API; unverified by us; the
   previously-shipped 31-char string was an invalid transcription and could never
   match — recorded so it is never trusted again).

### D3 — The PASS anchor is now FIRSTHAND-VERIFIED (include this derivation in the card's provenance and the reply to Seth)
Verified 2026-08-14 by the orchestrator, working tree AND `ac4c990` both:
```
F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | wc -c
# → 9758
awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | md5sum
# → 28ecdb3160833da80cfa25952f76415b
```
Identical at `git show ac4c990:$F`. The extraction is exclusive of both marker lines.
The 425d925a / 9,907 anchor is Seth-reported (we do NOT hold his body — see D7).

### D4 — Sites to fix (complete map, grep-verified 2026-08-14)
Executable card sites (full rewrite per D2):
- `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md`
  STEP 6b (lines ~91–103; the 31-char string is at :101).
- `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md`
  §6b (lines ~107–115; wrong prefix `c19e8b2…` at :113).
Live record fields (correct the wrong prefix `c19e8b2` → note the correction; dated
correction clause, do NOT rewrite dated historical narrative):
- `.planning/HANDOFF.json` `gates.trsx5_posted_body` (line ~73) — live gate field;
  correct in place + date the correction (precedent: the m3_04b gate-field
  correction, 2026-08-12).
- `.planning/STATE.md` line ~34 (the "THE trsx5 CONTEST (do not lose this)" block —
  body-side, LIVE instruction block) — correct in place + date.
- `.planning/HANDOFF.json` `status` (:9) and `resume_on_reconnect[0]` (:24): these
  carry the old card inside the dated 2026-08-14 close record. Do NOT rewrite the
  dated bodies. Add ONE dated correction clause at the TOP of the `status` field
  (same pattern as the existing "wave" field's superseding preamble) pointing to the
  corrected card; leave `resume_on_reconnect` untouched (the new STATE.md continuity
  + quick-task row carry the correction forward).
- `.planning/STATE.md` :1702 Session Continuity — handled by the orchestrator's
  continuity refresh in Step 7 (NOT the executor; avoids collision).

### D5 — READY-TO-FIRE.md gets the missing item 6b
`260812-ox1-READY-TO-FIRE.md` claims "Contents: ONLY Carter's remaining items, in
fire order" yet omits the fire-blocking trsx5 gate entirely. Insert a new **item 6b**
between item 6 (billing eyeball) and item 7 (PRE-FIRE 1b signature) carrying the
FULL corrected card per D2 (self-contained, matching the file's register), marked
"(added 2026-08-14, Seth escalation — this gate BLOCKS THE FIRE and obligation-(2)
posting)". Note in it that the ledger stays un-annotated toward either lineage until
the download adjudicates. Rationale for a third copy despite drift risk: the
size-first design makes a mistranscribed hash unable to false-pass, and the runbook
is Carter's primary checklist; a fire-blocking gate absent from "the only list" is
the exact divergence class DEC-2026-08-12 consolidated against.

### D6 — R3 + R4 record items
- R3 concrete numbers → add to BOTH deferral-vocabulary blocks (AGENT-PROMPT's
  "STAGE C HOLD LIFTED" paragraph and READY-TO-FIRE §10's "Deferral vocabulary"
  paragraph): clause-(d) anomaly threshold = 0.0005 × n_var, strict >; at the
  120,000 cap → 60.0; at region-1's n_var 102,421 → 51.2 (defer when the occluded
  count strictly exceeds); region 1's expected ~5 occlusions sit ~10× under.
  Attribute: "ceiling figures per Seth's 2026-08-14 review".
- R4 → THREE placements:
  1. `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`: register a new
     item (suggest id "R4-COVERAGE") — the square-mode deferral set is a genuine
     ancestry-specific COVERAGE GAP (est. ~29/276 = 10.5% of regions at the 120k
     cap, largest deferred span 48.5 Mb — Seth's estimates; ACTUAL numbers emerge at
     fire time), to be DISCLOSED as a methods/limitations item alongside the
     occlusion disclosure ("N regions exceeding n_var X were not converted in square
     mode; affected span M Mb", actual post-fire numbers), WITH the remedy path
     recorded so the gap is bounded-not-permanent: the frozen producer already
     supports banded mode (`--r gz` with an `--ld-window-*` bound), and large
     regions can be split into overlapping sub-windows; NEITHER pre-fire. Framing
     "nothing scientific is lost" is RETIRED — do not repeat it.
  2. READY-TO-FIRE §10's post-fire disclosure note: extend from "disclosed as a
     deviation" to name the methods/limitations placement + remedy-path note.
  3. Stage-B cost-gate relabel: in AGENT-PROMPT STEP 9's GATE sentence and
     READY-TO-FIRE item 11-C's egress/cost language where applicable — the Stage-B
     extrapolation covers ONLY the square-feasible class; read it as
     **cost-per-BANKABLE-region**, never cost-per-region-of-276.

### D7 — Reply-to-Seth courier package
New file `260814-guk-REPLY-TO-SETH.md` in the task dir, for Carter to courier:
- BLOCKING: confirmed (31 chars, counted, not argued) and fixed at every site; the
  new card text quoted in full; his safest formulation adopted (size-first).
- R1: his withdrawal noted; the gate stands on the records-integrity ground alone.
- R3: his ceiling figures now in both runbook vocabulary blocks.
- R4: registered as a disclosure obligation with remedy path (quote the
  deferred-items entry); cost gate relabelled cost-per-bankable-region.
- The anchor re-derivation transcript (D3) so he can see the 28ecdb31/9,758
  derivation is mechanical.
- His two requests: (a) the canonical 9,758-byte block — give Carter the exact
  extraction command (D3's awk) plus an output path so he can produce and courier
  the file whenever needed (pre- or post-download; it is our own already-public
  text); (b) the 149-byte diff — WE DO NOT HOLD his 9,907-byte body (grep-verified:
  only its hash appears in our records), so ask him to courier his lineage body;
  on receipt we produce the byte-level diff. Do not promise a diff we cannot compute.
- Restate: ledger stays neutral until the download adjudicates; an agent never
  fires; nothing else blocking from our side either.

### Claude's Discretion
- Exact wording/formatting at each site, provided D2's substance and each file's
  existing register are preserved.
- Whether HANDOFF.json status-field correction clause precedes or follows the
  "SESSION CLOSE 2026-08-14." opener — match the existing superseding-clause style.

</decisions>

<specifics>
## Hard Constraints (project standing rules — violations are blockers)

- **Docs-only.** ZERO changes under `src/`, `tests/`, `config/`, `Snakefile`,
  `docs/manuscript/`. No suite runs required (docs-only); do NOT run pytest (it
  rewrites `tests/m3/sparse_parent_benchmark.tsv`).
- **STATE.md frontmatter (lines 1–24) is UNTOUCHABLE** (byte-identity gate;
  pre-existing-unparseable YAML). Only body edits below the fence.
- **Dated historical `>` blocks in STATE.md / .continue-here.md are NOT correction
  sites.** Live fields get dated corrections; history stays.
- **git add with EXPLICIT PATHS only** — never `-A`/`.` on this GPFS tree.
- **No worktree isolation** (GPFS; `workflow.use_worktrees=false`).
- **No perimeter contact** — no gsutil/gcloud/bq/wb, not even read-only.
- **An agent must never fire the loop** — nothing in this task touches execution,
  only documents.
- **Do not annotate the trsx5 LEDGER toward either lineage** — the contest itself
  stays open pending Carter's download; this task only fixes the instrument.
- HANDOFF.json is valid JSON today and MUST remain so: after editing it, run
  `python3 -c "import json;json.load(open('.planning/HANDOFF.json'))"` and require
  exit 0. (STATE.md's YAML frontmatter is the pre-existing-unparseable one — and it
  is untouched by this task.)

</specifics>

<canonical_refs>
## Canonical References

- `260814-guk-SETH-REPLY.md` (same dir) — the source document, verbatim.
- `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`
  — carries the canonical paste block between `--- PASTE INTO OSF FROM HERE ---` /
  `--- PASTE ENDS HERE ---` markers (exclusive).
- `.planning/quick/260813-t21-wire-the-two-pre-fire-producer-gates-trs/260813-t21-SUMMARY.md`
  — the producer-gate wiring Seth's R3/R4 respond to.
- DEC-2026-08-12-adversarial-review-remediation (DECISIONS.md) — the precedent for
  live-field correction vs preserved history.
</canonical_refs>
