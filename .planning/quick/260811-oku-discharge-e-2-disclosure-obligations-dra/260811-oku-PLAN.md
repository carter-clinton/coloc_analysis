---
phase: quick/260811-oku
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: disclosure-drafting
tags: [e2, disclosure, osf, manuscript, track-a, id-vs-ref-ld, m3, docs-only]
autonomous: true
requirements: [E2-OBL-1-MANUSCRIPT, E2-OBL-2-OSF, E2-OBL-3-FRAMING-SURFACE]
baseline_rev: 7d575a5
branch: m3-W2-aou-deltas
files_modified:
  - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-check-drafts.sh
  - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-manuscript-limitation-drafts.md
  - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-osf-entry-drafts.md
  - .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-framing-decision-surface.md
  - .planning/STATE.md
user_setup: []

must_haves:
  truths:
    - "Carter can answer the open question '(c) LIMITATION or CORRECTION?' by picking one of two CONCRETE, paste-ready texts rather than deciding in the abstract: each framing exists in BOTH the manuscript-paragraph deliverable and the OSF-entry deliverable, so choosing a framing selects a complete matched pair."
    - "Every paste-ready block in every deliverable carries the five per-region numbers with APOL1_22q12 (18.41%) and FTO_16q12 (23.80%) named in words, and NO file quotes the pooled 5.29% without the per-region figures and the dragged-down-by-the-clean-regions statement present in the same file."
    - "Every paste-ready block carries the identity-LD-stub caveat (use_identity TRUE, R NULL, EUR/AFR/TRANS byte-identical) and states that the numbers are the catalog<->panel-frame transposition rate for VARIANT BOOKKEEPING, not a real-LD exposure."
    - "Every deliverable states that the previously-quoted 46/182 = 25.3% was a SYNTHETIC FIXTURE, not a measurement, and that the shipped ld_allele_join_indices() over 207 real region variant catalogs (206 regions measured per arm) is the measurement basis."
    - "Every deliverable carries the one-sentence honest mechanism (pre-o7o CHR:POS join with REF/ALT ignored -> a transposed pair entered LD with an unflipped z; the o7o fix makes the join allele-aware, flipping z rather than dropping, palindromes dropped) AND the two consequences: reported BETA/SE do not move, but PIPs and credible sets regenerated after the fix are not comparable to earlier ones."
    - "Every deliverable states the E-2/E-4 coupling: option B (the code change) becomes right only bundled with E-4, after a real panel exists, with a real-LD re-measurement, a before/after comparison and an OSF disclosure."
    - "A checker script exists that FAILS on a fixture carrying the wrong numbers and on a fixture quoting the pooled figure alone, has been OBSERVED failing on both, and exits 0 on the three shipped deliverables."
    - "The decision surface states, for each framing: what a reviewer likely concludes, what the framing obligates (CORRECTION -> regenerate/re-report affected AFR results once a real panel exists; LIMITATION -> prominent disclosure, no re-analysis), the E-4 coupling, and a recommendation with reasoning - while stating in terms that the choice is Carter's."
    - "Nothing is claimed discharged. The deliverables are DRAFTS; obligations (1) and (2) discharge only when Carter selects a framing and posts, and the files say so on their face."
    - "The change set is exactly the four new files under the quick directory plus one appended dated line in the BODY of STATE.md. No source, no test, no manuscript file, no Track A artifact, no .planning/amendments/ body, no DECISIONS.md and no HANDOFF.json edit; STATE.md's (unparseable, pre-existing) YAML frontmatter is untouched."
  artifacts:
    - path: ".planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-check-drafts.sh"
      provides: "the numbers-fidelity + framing-completeness acceptance harness for all three deliverables, with --self-test negative controls"
      contains: "--self-test"
      min_lines: 90
    - path: ".planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-manuscript-limitation-drafts.md"
      provides: "obligation (1) - the Track A (id-vs-ref-LD) paragraph in BOTH framings, each <=200 words, journal-ready prose, no markdown headers inside the paste block"
      contains: "PASTE-BEGIN: ms-correction"
      min_lines: 60
    - path: ".planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-osf-entry-drafts.md"
      provides: "obligation (2) - the OSF record entry in BOTH framings, following the 2026-07-10 amendment-update precedent (pre-paste reference / paste body / post-paste checklist)"
      contains: "PASTE-BEGIN: osf-correction"
      min_lines: 90
    - path: ".planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-framing-decision-surface.md"
      provides: "obligation (3) - the LIMITATION-vs-CORRECTION comparison, obligations of each, E-4 coupling, recommendation, and the explicit statement that the choice is Carter's"
      contains: "Recommendation"
      min_lines: 70
  key_links:
    - from: "260811-oku-check-drafts.sh"
      to: "all three deliverable .md files"
      via: "per-file clause groups selected by --only ms|osf|surface, run over the real files"
      pattern: "18\\.41|23\\.80|17\\.82"
    - from: "the four required numbers sets in every draft"
      to: ".planning/DECISIONS.md DEC-2026-08-07-e2-orientation-disposition and .planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-track-a-regions.tsv"
      via: "verbatim transcription, re-derived from the TSV rather than copied from prose"
      pattern: "e2-exposure-track-a-regions.tsv"
    - from: "260811-oku-e2-osf-entry-drafts.md"
      to: "osf.io/az52u"
      via: "append-only NEW supplementary file semantics - never an edit to the body of trsx5 or tcujq"
      pattern: "az52u"
---

<objective>
Discharge the DRAFTING half of the three E-2 disclosure obligations recorded in
`DEC-2026-08-07-e2-orientation-disposition`, so that the one question still open
above executor authority — **"is this a LIMITATION or a CORRECTION?"** — becomes
a choice between two concrete texts instead of a decision in the abstract.

Purpose: E-2 was decided as option A (code NOT changed, exposure DISCLOSED) on
measured evidence. Three obligations survive, none discharged: (1) a manuscript
limitation paragraph naming `APOL1_22q12` (18.41%) and `FTO_16q12` (23.80%)
explicitly; (2) an OSF record entry; (3) the open LIMITATION-vs-CORRECTION
question. Obligations (1) and (2) each have to be written in whichever framing
(3) resolves to — so writing BOTH framings of BOTH artifacts converts (3) from an
abstract judgement call into "read two matched pairs, pick one."

Output: four new files in this quick directory — two draft files (each carrying
both framings), one decision surface, and one acceptance harness that proves the
numbers in the drafts are the measured ones and that no framing quotes the
flattering pooled figure alone.

⛔ This plan is DRAFT-ONLY. It does not post anything, does not edit any
manuscript file, does not touch Track A artifacts, does not change a line of
source or test code, and does not mark any obligation discharged.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md
@.planning/HANDOFF.json
@.planning/DECISIONS.md
@.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
@.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-track-a-regions.tsv
@.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-real-corpus.tsv
@.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-measure.R
@.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md

**Read `DECISIONS.md` from line 1173** (`DEC-2026-08-07-e2-orientation-disposition`,
~80 lines). Read `deferred-items.md` §`E-2` (line 139) including the
`▶ E-2 EVIDENCE UPDATE (2026-08-07)` block at line 231, and §`E-4` (line 342).
`HANDOFF.json`: `headline`, `carter_decisions_outstanding[0]`,
`analysis_change_to_disclose`, and the four E-2/OSF-relevant `do_not` entries.
</context>

<locked_numbers>
<!-- These are the ONLY numbers permitted in the drafts. Re-derive them from the
     TSV; do not retype them from prose. Every one is verified against
     e2-exposure-track-a-regions.tsv and the DECISIONS.md table. -->

**Track A's five coloc regions** — ratio is `flipped / (exact + flipped)`, i.e.
the share of **bindable** (joinable-at-a-shared-coordinate) variants whose
REF/ALT are transposed. It is NOT a share of the whole catalog: `n_catalog` is
larger, because ambiguous / palindromic / mismatched / unusable rows are dropped
before the ratio is formed. State the denominator in every paste block.

| Track A region | exact | flipped | ratio |
|---|---|---|---|
| `CXADR_F2RL1_6p21` (5 tiles) | 28,415 | 18 | **0.06%** |
| `MC4R_18q21` (2 tiles) | 14,141 | 10 | **0.07%** |
| `SH2B3_12q24` (3 tiles) | 11,826 | 333 | **2.74%** |
| — `__tile1` / `__tile2` (the md5-pinned **anchor**) | 10,521 | 0 | **0.00%** |
| — `__tile3` | 1,305 | 333 | **20.33%** |
| `APOL1_22q12` (2 tiles) | 4,910 | 1,108 | **18.41%** |
| `FTO_16q12` (3 cells) | 7,188 | 2,245 | **23.80%** |
| **pooled over the Track A set** | 66,480 | 3,714 | **5.29%** |

**Corpus context (EUR arm, `e2-exposure-real-corpus.tsv`, 618 rows = 206 regions
x 3 ancestries):** regions measured **206**; regions with >=1 transposed row
**195 / 206**; per-region **median 17.82%**; mean 12.49%; **max 38.68%**
(`RAD50_peak__tile1`); min 0.00%; pooled-across-all-rows 4.18% (31,152 /
745,534).

**Measurement basis:** the SHIPPED `ld_allele_join_indices()` from
`src/snakemake/scripts/ld_allele_join.R`, run over the **207 real region variant
catalogs** in `data/processed/region_analysis/ld_reference/variants/` against the
`variants` frames of the sibling ancestry panels (`e2-exposure-measure.R`).
Read-only, $0, no perimeter contact.

**⛔ The pooled 5.29% may appear ONLY alongside the per-region figures, and only
with the explicit statement that it is dragged down by the two clean large
regions (`CXADR_F2RL1_6p21`, `MC4R_18q21`).**

**⛔ Every framing MUST carry the identity-LD-stub caveat.** Every panel measured
is an identity-LD stub: `use_identity = TRUE`, `R` is `NULL`,
`status = "variants_exceed_threshold"`, and the `EUR/`, `AFR/` and `TRANS/`
directories are byte-identical (md5-verified on two regions). The numbers are the
**catalog<->panel-frame transposition rate for VARIANT BOOKKEEPING**, NOT the
real-LD exposure. A real (non-identity) panel is **not verified** to carry the
same `variants` frames.

**⛔ The 46/182 = 25.3% figure quoted in earlier records was a SYNTHETIC
ACCEPTANCE FIXTURE, not a measurement** — the per-pair receipts it was supposed
to come from cannot exist yet (the counter path is AFR-gated, AFR has zero
QTL-coloc jobs per E-4, and the AoU panel is 0/276). Say so plainly.

**What the number means, precisely:** it is the **population in which an
orientation error can occur**, not a count of realized sign errors. It does not
by itself demonstrate that any published `PP.H4` is wrong. It does mean that
**"we checked and it is immaterial" is not a defensible statement** for
`APOL1_22q12` or `FTO_16q12`.

**The mechanism, in one honest sentence:** the pre-`o7o` join matched on
`CHR:POS` with REF/ALT ignored, so a transposed (REF/ALT-swapped) variant pair
entered LD with an unflipped z; the `o7o` fix makes the join allele-aware — it
**flips z rather than dropping**, and drops palindromes (a strand-inverted
palindrome is a silently sign-wrong EXACT match, the only undetectable class).
**Reported BETA and SE do not move**, so no published direction of effect
changes; **PIPs and credible sets regenerated after the fix are NOT comparable
to ones produced before it.**

**What is fixed vs what is deliberately NOT:** `o7o` made the GWAS-sumstats<->panel
join allele-aware. **E-2 — the QTL-beta <-> panel-ALT orientation — is
deliberately left as-is under option A.** Do not let a draft blur these into "the
allele problem is fixed."

**E-2/E-4 coupling:** option **B** (correct the orientation in code) becomes right
only **bundled with E-4**, after a real panel exists, with a real-LD
re-measurement, a before/after comparison and an OSF disclosure. Today B is inert
(`build_qtl_coloc_manifest.py::_ancestry_for_region` returns `"EUR"`
unconditionally, so zero AFR QTL-coloc jobs exist), it moves Track A numbers
mid-submission, and its only validation substrate is the identity-LD stub tree.

**Framing discipline (project-standing):** original-research framing throughout.
This is a hypothesis-driven original study disclosing a measured property of its
own pipeline. Never "revision", never "fix", never "cleanup", never "salvage".
Use "amendment-update" or "correction to the record" if the concept is needed.
</locked_numbers>

<explicitly_out_of_scope>
- ⛔ **No OSF posting.** Bodies of posted OSF amendments are byte-locked. The
  OSF deliverable drafts a **NEW supplementary file** on `osf.io/az52u`
  (append-only, the `tcujq` -> `trsx5` precedent) for **Carter** to post.
  Never an edit or re-post of `trsx5` or `tcujq`.
- ⛔ **No manuscript file edits.** The paragraph is drafted here for Carter to
  place; nothing under a manuscript tree is opened for write.
- ⛔ **No Track A artifact edits.** `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`,
  `results/` and the four md5 locks stay byte-untouched.
- ⛔ **No source or test changes.** `src/`, `tests/`, `config/`, `Snakefile`
  are not opened for write. The checker is an acceptance harness living in this
  quick directory; it is not a pytest test and must not be added to `tests/`.
- ⛔ **No DECISIONS.md, HANDOFF.json or deferred-items.md edits.** The decision
  is already recorded; drafts do not change it. Do NOT mark obligations
  discharged anywhere — they discharge when Carter picks a framing and posts.
- ⛔ **No AoU / perimeter contact of any kind.** `$0`. The
  `aou-ld-pipeline` skill is not relevant to this task.
- ⛔ **Do not fold the outstanding Check-2 amendment-update into this entry** —
  it is a separate surviving OSF obligation and stays separate.
- ⛔ **No `git add -A` / `git add .`** on this GPFS tree; explicit paths only.
</explicitly_out_of_scope>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Build the numbers-fidelity harness (RED first), then the two manuscript paragraphs</name>
  <files>
.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-check-drafts.sh,
.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-manuscript-limitation-drafts.md
  </files>
  <behavior>
The harness is written and PROVEN ABLE TO FAIL before any draft satisfies it.
`[[feedback_green_assertion_needs_a_negative_control]]`: a green clause is
evidence only if it has been seen red.

`260811-oku-check-drafts.sh [--only ms|osf|surface] [--self-test]`, bash + grep,
exit 0 = pass, non-zero = fail, one line per clause (`PASS`/`FAIL` + clause id).

**Paste-block contract** (used by all three deliverables):
`<!-- PASTE-BEGIN: <id> -->` ... `<!-- PASTE-END: <id> -->` on their own lines.
Ids: `ms-limitation`, `ms-correction`, `osf-limitation`, `osf-correction`.
Word count = `wc -w` of the block with the two marker lines removed.

**Clause groups:**

`ms` (over the manuscript drafts file):
- MS-01 both blocks `ms-limitation` and `ms-correction` exist, exactly once each.
- MS-02 each block is 120 <= words <= 200. **FEASIBILITY MEASURED DURING
  PLANNING: a paragraph carrying every block-level required item came to 178
  words, so the 200-word cap has ~22 words of headroom and is satisfiable.** If a
  block runs over, trim prose — never a required number.
- MS-03 no line inside a block starts with `#` and no line contains `|`
  (journal-ready prose, no markdown headers, no tables inside the paragraph).
- MS-04 each block contains all of: `0.06`, `0.07`, `2.74`, `20.33`, `18.41`,
  `23.80`, and the literal region names `APOL1_22q12` and `FTO_16q12`.
- MS-05 each block contains `17.82` and `38.68` and `195` (corpus context).
- MS-06 each block contains the identity-stub caveat: matches
  `identity` AND `use_identity` AND `byte-identical`, and matches
  `bookkeeping`.
- MS-07 each block states the denominator: matches `bindable` or
  `exact + flipped` or `transposed`.
- MS-08 pooled-alone guard: if `5.29` appears anywhere in the FILE, then
  `dragged` must also appear in the FILE **and** every block containing `5.29`
  must also contain `18.41` and `23.80`.
- MS-09 framing guard: the file contains zero case-insensitive occurrences of
  the standalone words `revision`, `revisions`, `salvage`, `cleanup`.
- MS-10 file-level: contains `46/182`, `25.3`, `fixture`; contains `CHR:POS`
  and `palindrom`; contains `BETA` and (`not comparable` or `NOT comparable`);
  contains `E-4`; contains `207`.
- MS-11 the file states on its face that it is a DRAFT and that the obligation
  is not discharged until Carter selects a framing: matches `DRAFT` and
  `not discharged`.

`osf` (over the OSF drafts file): OSF-01..OSF-11 mirror MS-01..MS-11 for blocks
`osf-limitation` / `osf-correction`, with these differences — no word cap
(replaced by a `>= 250` word floor per block), MS-03 relaxed to "no line inside
a block starts with `#`" (tables are allowed in an OSF body), and MS-10's
file-level items are additionally required INSIDE each block. Plus:
- OSF-12 each block contains `az52u` and `pvb5j`, and the FILE contains
  `append-only` and `new supplementary file`.
- OSF-13 each block contains `no pre-registered number` (or
  `No pre-registered number`) and `TRACK-A-FROZEN-NUMBERS` or
  `Track A's frozen numbers`.

`surface` (over the decision surface file):
- SURF-01 file contains both `LIMITATION` and `CORRECTION` as framing headings.
- SURF-02 contains `Recommendation` and a sentence matching `Carter` +
  (`choice` or `call` or `decision`).
- SURF-03 contains `re-analys` or `regenerat` (the CORRECTION obligation) and
  `no re-analysis` or `without re-analysis` (the LIMITATION obligation).
- SURF-04 contains `E-4`, `18.41`, `23.80`, `17.82`, `identity`.
- SURF-05 the MS-08 pooled-alone guard and the MS-09 framing guard, verbatim.

**Negative controls, all four OBSERVED red before the real drafts are written:**
- NC-1 a fixture identical to a real block but with `18.41` changed to `1.841`
  -> MS-04 FAIL.
- NC-2 a fixture quoting only `5.29` with the per-region numbers deleted ->
  MS-08 FAIL.
- NC-3 a fixture with the identity-stub sentence deleted -> MS-06 FAIL.
- NC-4 a 240-word block -> MS-02 FAIL.
`--self-test` builds these four fixtures in a temp dir, asserts each fails on the
clause named above (and ONLY on that clause where practical), and exits non-zero
if any of them PASSES. `--self-test` must be runnable with no deliverable files
present at all.
  </behavior>
  <action>
1. Write `260811-oku-check-drafts.sh` implementing the contract above. Make it
   executable (`chmod +x`). Pure bash + grep + wc; no python, no new deps. Use
   `mktemp -d` under `$TMPDIR` for `--self-test` fixtures and clean up.
2. RUN `./260811-oku-check-drafts.sh --self-test` and PASTE THE OUTPUT into the
   task record. All four negative controls must be OBSERVED red. If a control
   passes, the clause is structurally incapable of its job — fix the clause, not
   the fixture.
3. RUN `./260811-oku-check-drafts.sh --only ms` with no draft file present and
   confirm it exits non-zero with "file not found" — the harness must fail
   loudly on absence, never skip.
4. Re-derive the Track A numbers FROM THE TSV rather than retyping them from
   prose — e.g. group `e2-exposure-track-a-regions.tsv` by `track_a_region`,
   sum `exact` and `flipped`, and compute `flipped/(exact+flipped)`. Confirm
   you reproduce 0.06 / 0.07 / 2.74 / 18.41 / 23.80 and pooled 5.29 before
   writing a single number into the draft. `[[feedback_a_count_is_a_claim_scope_and_reconcile]]`.
5. Write `260811-oku-e2-manuscript-limitation-drafts.md`. Structure:
   - a short non-paste preamble: what this is, which obligation it discharges
     (obligation 1 of `DEC-2026-08-07-e2-orientation-disposition`), that it is a
     **DRAFT** and **not discharged** until Carter selects a framing and places
     the text, the target (the Track A manuscript, nickname **id-vs-ref-LD**),
     and where each framing goes (LIMITATION -> Limitations section;
     CORRECTION -> a Methods-correction note).
   - `## Framing A — LIMITATION` + the `ms-limitation` paste block.
   - `## Framing B — CORRECTION` + the `ms-correction` paste block.
   - a closing "author notes (do NOT paste)" section carrying the mechanism
     sentence, the 46/182-was-a-fixture note, the BETA/SE-vs-PIP consequence,
     and the E-4 coupling in full, plus the exact provenance line
     (`e2-exposure-measure.R`, `e2-exposure-track-a-regions.tsv`,
     `e2-exposure-real-corpus.tsv`, the shipped `ld_allele_join_indices()`).
   The two paragraphs differ in POSTURE, not in facts: the LIMITATION framing
   reports the exposure as a bounded, disclosed property of the analysis; the
   CORRECTION framing states that the pre-`o7o` join was wrong, names what it did
   (see the mechanism sentence), and commits to what follows. Both carry the same
   locked numbers, the same caveat and the same denominator.
6. RUN `./260811-oku-check-drafts.sh --only ms` and get exit 0.
  </action>
  <verify>
    <automated>cd .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra && ./260811-oku-check-drafts.sh --self-test && ./260811-oku-check-drafts.sh --only ms</automated>
  </verify>
  <done>
`--self-test` exits 0 having OBSERVED all four negative controls red (output
pasted into the task record); `--only ms` exits 0 against the real drafts file;
both paste blocks are 120-200 words with no `#` or `|` lines inside; every
locked number in the file was re-derived from the TSV during this task.
  </done>
</task>

<task type="auto">
  <name>Task 2: The OSF record entry, in both framings</name>
  <files>.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-osf-entry-drafts.md</files>
  <action>
Write `260811-oku-e2-osf-entry-drafts.md`, following the FORMAT PRECEDENT of
`.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`
(read it first): a **Pre-Paste Reference** table (do-not-paste), a
`--- PASTE INTO OSF FROM HERE ---` body, `--- PASTE ENDS HERE ---`, then a
**Post-Paste Reference** checklist (do-not-paste). Produce the paste body TWICE —
once per framing — as blocks `osf-limitation` and `osf-correction`.

**Pre-Paste Reference fields** (both framings share it; note where they differ):
target OSF project `osf.io/az52u`, posted as a **NEW supplementary file**
(append-only; the `tcujq` -> `trsx5` precedent — `trsx5` was confirmed a separate
new file, not a new version); original pre-registration `osf.io/pvb5j`
(DOI `10.17605/OSF.IO/PVB5J`); amendment kind (LIMITATION framing = a disclosure
entry; CORRECTION framing = a methods correction-and-disclosure entry); what is
disclosed; what is NOT withdrawn; substrate; the pre-post commit gate (fill with
the HEAD at posting time, baseline `7d575a5`); expected posting date left for
Carter. Add one explicit line: **this entry does NOT discharge the outstanding
Check-2 amendment-update obligation**, which remains separate.

**Each paste body must contain, at minimum:**
- Title line naming the pre-registration and the subject
  (QTL-beta <-> panel-ALT variant orientation in the AFR LD-panel arm), Date,
  Investigator (`Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200`).
- **Purpose / what is being disclosed** — the exposure, in the project's own
  words, framed per the block's posture.
- **The measurement** — the shipped `ld_allele_join_indices()` over the 207 real
  region variant catalogs (206 regions measured per ancestry arm), the
  denominator (`flipped / (exact + flipped)`, the bindable set, NOT the whole
  catalog), the per-region Track A table verbatim from `<locked_numbers>`
  including the SH2B3 anchor-vs-tile-3 split, the pooled 5.29% WITH the
  dragged-down statement, and the corpus context (median 17.82%, max 38.68%,
  195/206).
- **What the number means and does not mean** — the population in which an
  orientation error can occur, not a count of realized sign errors; it does not
  by itself demonstrate any published `PP.H4` is wrong; and "we checked and it is
  immaterial" is not defensible for `APOL1_22q12` or `FTO_16q12`.
- **Correction to the internal record** — the previously-quoted 46/182 = 25.3%
  was a synthetic acceptance fixture, not a measurement of anything real, and
  the receipts that figure was supposed to come from cannot exist yet (AFR-gated
  counter path, zero AFR QTL-coloc jobs per E-4, panel 0/276).
- **The caveat that bounds all of it** — the identity-LD-stub paragraph, in full.
- **Mechanism** — the one honest sentence, plus: reported BETA/SE do not move, so
  no published direction of effect changes; PIPs and credible sets regenerated
  after the allele-aware join are **not comparable** to ones produced before it.
- **What does NOT change** — no pre-registered number moved; Track A's frozen
  numbers (`TRACK-A-FROZEN-NUMBERS.md`) are untouched; the pre-registered
  occlusion/PSD commitments are unaffected; pre-registration discipline,
  AoU controlled-tier handling (aggregate + coordinate egress only, no genotypes,
  no full LD matrices), and public-data-only handling all stand.
- **What happens next** — the E-2/E-4 coupling: the code-side orientation change
  becomes appropriate only bundled with E-4, after a real (non-identity) panel
  exists, with a real-LD re-measurement, a before/after comparison, and a further
  OSF update. Under the CORRECTION framing this section additionally COMMITS to
  regenerating and re-reporting the affected AFR results at that point; under the
  LIMITATION framing it states the disclosure stands and no re-analysis of
  published results is undertaken.

**Where the two framings genuinely differ** (make this legible, do not just
swap adjectives): the title/kind, the Purpose posture, and the "what happens
next" commitment. Facts, numbers and caveats are identical in both.

Do NOT write anything into `.planning/amendments/`, `.planning/osf_deviations.md`
or `.planning/STATE.md` in this task, and do NOT claim a posting occurred.
Finish by running the checker.
  </action>
  <verify>
    <automated>cd .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra && ./260811-oku-check-drafts.sh --only osf && git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis status --porcelain .planning/amendments/ results/ | grep -Ev '^\?\?' | wc -l | grep -qx 0</automated>
  </verify>
  <done>
`--only osf` exits 0; both paste bodies are self-contained and paste-ready
between their markers; `.planning/amendments/` and `results/` are byte-clean in
`git status`; the file states in its pre-paste block that Carter posts it and
that it does not discharge the Check-2 obligation.
  </done>
</task>

<task type="auto">
  <name>Task 3: The framing decision surface, full-harness green, and a one-line STATE.md record</name>
  <files>
.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-framing-decision-surface.md,
.planning/STATE.md
  </files>
  <action>
1. Write `260811-oku-e2-framing-decision-surface.md` — the artifact that lets
   Carter answer obligation (3). Required sections:

   - **The question, stated once.** Two of five Track A coloc regions carry
     ~18-24% transposed variants (`APOL1_22q12` 18.41%, `FTO_16q12` 23.80%);
     a third has one exposed tile (`SH2B3_12q24__tile3` 20.33%) while its
     md5-pinned anchor tiles are 0.00%; two are clean at ~0.06%. Is that a
     LIMITATION or a CORRECTION?
   - **What each framing says, in one sentence each**, with a pointer to the
     matched paste blocks (`ms-limitation` + `osf-limitation` vs `ms-correction`
     + `osf-correction`) so choosing a framing selects a complete pair.
   - **Side-by-side comparison table** with at least these rows: what a reviewer
     likely concludes; what it obligates NOW; what it obligates ONCE A REAL PANEL
     EXISTS; effect on Track A's frozen numbers; effect on the pre-registration;
     risk if the other framing turns out to have been right; cost.
     - CORRECTION obligates **regenerating and re-reporting the affected AFR
       results once a real panel exists** (and invites the question of why the
       affected numbers are being reported at all in the interim).
     - LIMITATION obligates **prominent disclosure** — in the Limitations
       section and on the OSF record — **but no re-analysis** of published
       results.
   - **The three facts that constrain the choice**, each stated plainly:
     (a) the substrate is an identity-LD stub tree, so the measured rate is a
     catalog<->panel-frame transposition rate for variant bookkeeping and NOT a
     real-LD exposure — a CORRECTION framing asserts more than the substrate can
     currently support, while a LIMITATION framing risks under-stating an
     exposure that a real panel may confirm;
     (b) the number is the population in which an orientation error can occur,
     not a count of realized sign errors — no published `PP.H4` has been shown
     wrong, and equally "we checked and it is immaterial" is not defensible for
     the two exposed regions;
     (c) **the E-4 coupling** — the code-side correction (option B) is INERT
     today because `_ancestry_for_region` returns `"EUR"` unconditionally, so a
     CORRECTION framing that promises a code change promises something that
     cannot be exercised until E-4 lands and a real panel exists.
   - **What we are NOT proposing to disclose, and why** — the interim internal
     report that gave `SH2B3_12q24__tile3` as "0.20%" when it is **20.33%** (a
     ratio of 0.2033 misread as a percentage, a 100x error in the reassuring
     direction) was never externally reported, so it is an internal-record
     correction and not itself an OSF obligation. Say this explicitly so Carter
     can overrule it; note that it IS an argument for quoting per-region numbers
     with their provenance rather than a single pooled figure.
   - **Recommendation** — give one, with reasoning, and say plainly that the
     choice is **Carter's**. Reason from the project's standing
     rigor-over-speed posture and from what is actually provable on today's
     substrate. State the condition that would flip the recommendation.
   - **What discharges the obligations** — obligation (1) discharges when the
     selected paragraph is placed in the manuscript; obligation (2) when the
     selected OSF entry is posted as a new supplementary file on `az52u` and its
     URL + timestamp are recorded in `.planning/osf_deviations.md`; obligation
     (3) when the framing is chosen and recorded in `DECISIONS.md`. **None is
     discharged by this plan.**

2. Run the FULL harness over all three deliverables (no `--only`) and get exit 0.

3. Append ONE dated line to the **BODY** of `.planning/STATE.md` (find the
   current dated activity block and append in its style) recording that the E-2
   disclosure drafts exist at this quick directory, in both framings, and that
   obligation (3) — the framing choice — remains Carter's and all three
   obligations remain UNDISCHARGED.
   ⛔ **Do NOT touch STATE.md's YAML frontmatter** — it is a known pre-existing
   landmine (`yaml.safe_load` fails at the `last_activity` scalar, line 17,
   unescaped double quotes); it is not this task's to repair, and touching it
   risks widening a 34 KB historical scalar edit into a freeze-moment change.

4. Commit with explicit paths only (never `git add -A` / `git add .`):
   the four quick-directory files and `.planning/STATE.md`.
   Suggested message: `docs(e2): draft both framings of the E-2 disclosure —
   manuscript paragraph, OSF entry, and the framing decision surface`.
  </action>
  <verify>
    <automated>cd .planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra && ./260811-oku-check-drafts.sh && cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git status --porcelain | grep -Ev '^\?\?' | grep -Ev '\.planning/(quick/260811-oku|STATE\.md)' | wc -l | grep -qx 0</automated>
  </verify>
  <done>
The full harness exits 0 over all three deliverables; the decision surface
carries the comparison table, the three constraining facts, the not-proposing-to-
disclose note, and a recommendation that names the choice as Carter's; the only
tracked files modified are the four quick-directory files and one appended body
line in STATE.md; the commit lists explicit paths.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo -> OSF public record | a paste body crosses from a draft into a permanent, append-only public record; once posted it cannot be edited |
| repo -> Track A manuscript (in submission) | a paragraph crosses into a document under review; a wrong number there is a correction to a correction |
| AoU controlled tier -> public disclosure | any number published must be aggregate/coordinate-level only |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-oku-01 | Tampering (integrity of a reported number) | the locked numbers inside all four paste blocks | mitigate | `260811-oku-check-drafts.sh` clauses MS-04/05/07 + OSF-04/05, each proven able to fail (NC-1); numbers re-derived from `e2-exposure-track-a-regions.tsv`, not retyped from prose |
| T-oku-02 | Information disclosure (misleading-by-omission) | the pooled 5.29% quoted without per-region context | mitigate | MS-08/SURF-05 pooled-alone guard, proven able to fail (NC-2); `HANDOFF.json` `do_not` carries the same prohibition |
| T-oku-03 | Information disclosure (over-claim) | reporting stub-panel counts as real-LD exposure | mitigate | MS-06/OSF-06 identity-stub caveat required in EVERY block, proven able to fail (NC-3) |
| T-oku-04 | Information disclosure (controlled tier) | AoU perimeter data in an OSF paste body | accept | the measured numbers are variant-bookkeeping counts over GRCh37 region catalogs and panel `variants` frames on the NC-State tree (identity stubs, `R` NULL) — no genotypes, no per-participant data, no LD values; `$0`, zero perimeter contact this plan |
| T-oku-05 | Repudiation (append-only record integrity) | editing or re-posting a byte-locked OSF body | mitigate | drafts declare NEW-supplementary-file semantics on `az52u` (OSF-12); no write to `.planning/amendments/` — asserted by the Task 2 `git status` clause |
| T-oku-06 | Spoofing (a draft mistaken for a posted record) | the two draft `.md` files | mitigate | MS-11/OSF-11: every file states DRAFT + "not discharged" on its face; the pre-paste block names Carter as the poster |
| T-oku-07 | Elevation of privilege (executor deciding above its authority) | the LIMITATION-vs-CORRECTION choice | mitigate | both framings shipped complete; SURF-02 requires the surface to name the choice as Carter's; no deliverable selects one |
| T-oku-08 | Denial of service (scope creep into a frozen surface) | `src/`, `tests/`, `results/`, `.planning/amendments/`, `DECISIONS.md` | mitigate | `<explicitly_out_of_scope>` enumerates every prohibited surface; Task 2 and Task 3 verify clauses assert a byte-clean `git status` outside the allowed paths |
</threat_model>

<verification>
1. `./260811-oku-check-drafts.sh --self-test` — four negative controls OBSERVED
   red; output pasted into the SUMMARY, not summarized as "passed".
2. `./260811-oku-check-drafts.sh` — exit 0 over all three deliverables.
3. The Track A numbers in the drafts were RE-DERIVED from
   `e2-exposure-track-a-regions.tsv` during Task 1, and the re-derivation is
   shown in the SUMMARY (per-region and pooled), not asserted.
4. `git status --porcelain` shows tracked modifications ONLY under
   `.planning/quick/260811-oku-*` and `.planning/STATE.md`.
5. `git diff --stat` shows **zero** changes under `src/`, `tests/`, `config/`,
   `results/`, `.planning/amendments/`, `.planning/DECISIONS.md`,
   `.planning/HANDOFF.json`.
6. `git diff .planning/STATE.md` touches BODY lines only — the YAML frontmatter
   block is byte-unchanged.
7. `$0` and zero perimeter contact — no `gcloud`, no `wb`, no `gsutil`, no LSF
   submission anywhere in the task record.
</verification>

<success_criteria>
- Both obligations (1) and (2) have a complete, paste-ready draft in BOTH
  framings — four paste blocks total, matched pairwise so that choosing a framing
  selects one manuscript paragraph and one OSF entry.
- Each manuscript paste block is 120-200 words of journal-ready prose with no
  markdown headers or tables inside it.
- Every paste block carries: the five per-region numbers with `APOL1_22q12`
  (18.41%) and `FTO_16q12` (23.80%) named; the SH2B3 anchor-0.00%-vs-tile3-20.33%
  split; the corpus context (median 17.82%, max 38.68%, 195/206); the denominator
  definition; and the identity-LD-stub caveat.
- No file quotes the pooled 5.29% without the per-region figures and the
  dragged-down statement — enforced by a guard proven able to fail.
- Every deliverable names the 46/182 = 25.3% figure as a synthetic fixture, states
  the mechanism in one honest sentence, states that BETA/SE do not move while
  post-fix PIPs and credible sets are not comparable to earlier ones, and states
  the E-2/E-4 coupling.
- The decision surface compares the two framings on reviewer reading, obligations
  now and later, Track A impact, and pre-registration impact; gives a
  recommendation with reasoning; and says the choice is Carter's.
- Original-research framing throughout; the words `revision`/`salvage`/`cleanup`
  appear nowhere.
- Nothing is posted, no manuscript file is edited, no Track A artifact moves, no
  source or test changes, and no obligation is marked discharged.
</success_criteria>

<output>
After completion, create
`.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-SUMMARY.md`.

The SUMMARY must carry: the `--self-test` output showing all four negative
controls red; the per-region and pooled re-derivation from the TSV; the word
count of each manuscript paste block; and an explicit statement that the three
E-2 obligations remain **UNDISCHARGED** pending Carter's framing choice, the
manuscript placement, and the OSF posting.
</output>
