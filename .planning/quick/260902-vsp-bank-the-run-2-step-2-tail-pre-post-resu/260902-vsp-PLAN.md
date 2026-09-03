---
phase: quick-260902-vsp
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: m3-afr-ld-panel
tags: [bank-a-result, courier-to-seth, docs-only, pre-vs-post-filter, partial-confounding-tail, heterogeneity, definitional-disagreement, informative-carriers-no-floor, prereg-confirmed, nothing-fired, vm-stopped]

files_modified:
  - .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md
  - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
  - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md
  - .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-PLAN.md
  - .planning/STATE.md

autonomous: true

requirements:
  - VSP-ONE-RECORD-BANKS-RUN2-STEP2-AND-IS-THE-COURIER
  - VSP-THREE-FINDINGS-STATED-AS-THREE-NOT-ONE
  - VSP-HEADLINE-HETEROGENEITY-IS-THE-REDUCED-1P99
  - VSP-EVERY-SCOPE-CAVEAT-IN-ITS-OWN-SECTION-NOT-A-FOOTNOTE
  - VSP-HONEST-LIMITATIONS-NOT-SOFTENED
  - VSP-NUMBERS-SPLICED-VERBATIM-NEVER-RETYPED
  - VSP-PREREG-ATTRIBUTION-PRECISE-NOT-CONFLATED
  - VSP-0P0005-CONTRADICTION-FLAGGED-NOT-FIXED
  - VSP-CHR7-SITING-DECLARED-BLOCKED-NOT-SKIPPED
  - VSP-NO-CARRIER-FLOOR-PROPOSED
  - VSP-DOCS-ONLY-SRC-AND-TESTS-UNTOUCHED
  - VSP-STATE-MD-QUICK-TASKS-ROW-LANDED
  - VSP-NOTHING-FIRED-NO-VM-NO-OSF

user_setup: []

must_haves:
  truths:
    - "A READER WHO WAS NOT IN THIS SESSION CAN LEARN THE RUN 2 STEP 2 RESULT FROM ONE FILE. `.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md` states what was run, on which artifacts, what came out, what it means, what it does NOT establish, and what is being asked of Seth — without requiring any other document to be open."
    - "THE THREE FINDINGS READ AS THREE FINDINGS. The PRE/POST split, the between-region heterogeneity of the POST rate, and the rarer-vs-min definitional disagreement each get their OWN top-level section with its own numbers and its own claim, and the record states in its own words that they are INDEPENDENT axes — `spearman(POST frac, disagree frac) = +0.173` over 21 regions — so no reader can take them for one result described three ways."
    - "THE HEADLINE HETEROGENEITY FIGURE IS THE REDUCED ONE. In the human-written prose, `1.99` (chi2 37.78, dof 19, p 6.3e-3, `m2_region_00060__sub13` dropped) appears BEFORE `2.36`, and `2.36` appears only with its explanation — inflated by the chr15 overlap, whose two regions rank 2nd and 3rd on POST fraction and are largely one locus."
    - "NO NUMBER WAS RETYPED. The record carries a VERBATIM APPENDIX spliced BY SCRIPT from `CONTENT-SPEC.md` (`## ARTIFACTS` to EOF), and the appendix bytes are proven byte-equal to that slice by a check that reads both files at verification time. The prose above it may restate a number, but the authority is the appendix and the record says so."
    - "THE PRE-REGISTRATION ATTRIBUTION IS PRECISE. The record states that RUN 1's pre-registration (`.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md` §(e)) was confirmed 5/5 plus the offset histogram with ZERO adjustments, AND that RUN 2 STEP 2's three values — `n_tail_rows_in` 3094, `n_tail_rows_out_of_scope` 0, `n_defined_rows_out_of_scope` 0 — PASSED with ZERO adjustments. It does NOT claim the 260826 table contains those three; it does not conflate the two pre-registrations. See FLAG-1 below."
    - "EVERY SCOPE CAVEAT IS STATED PLAINLY IN ITS OWN NUMBERED SECTION. All six — the 2521 per-region sum vs a panel-wide dedup, the INDEX-keyed `pair_key` with its 564/2461 deletion-deletion neighbours and the 1897 + 2*564 + 69 = 3094 closure, the chr15 overlap and its 69/69 agreement, the absence of per-region emission for the disagreement count, the RUN-LEVEL-only provenance, and the monotonicity condition — appear as prose in the record's own caveats section, not only inside the appendix and not as footnotes."
    - "THE HONEST LIMITATIONS ARE NOT SOFTENED. The record says, in its own section: the run finished during a VM blackout; the full stdout and the exit status `$?` are UNRECOVERABLE and were NEVER SEEN by anyone; the completion verdict rests entirely on the three pre-registered values plus the artifacts; there is NO pre-reboot hash, so the recorded md5s anchor FORWARD, not backward, and cannot prove byte-identity to what was written at 21:07:03Z. What they DO establish is that a damaged file would not have parsed and summed to exactly 3094/0/0."
    - "THE 0.0005 CONTRADICTION IS AN ACTION ITEM, NOT A FIX. The record carries all four citations verbatim — `src/python/pairwise_completeness_scan.py:45` (\"the withdrawn 0.0005 bound\"), `src/python/condition_ld_matrix.py:120` (`ceiling_frac: float = 0.0005`, live default), `src/python/write_conditioned_ld_npz.py:64` (same live default), `src/python/write_conditioned_ld_npz.py:17` (\"the pre-registered 0.0005\") — states that one module calls it withdrawn while another calls it pre-registered while the value is live in both, and routes the fix to a SEPARATE task. `git status --porcelain -- src tests` is EMPTY after this plan."
    - "`chr7:89454077` IS DECLARED BLOCKED, NOT SKIPPED. The record states plainly that the surviving pair's deletion cannot be sited as at-signal versus cold-sequence because no genome-wide fine-mapping exists (only Track A candidate-locus `results/multitrait/coloc_susie_R2*`; NO MTAG outputs), and that it is BLOCKED ON THIS VERY PANEL."
    - "NO CARRIER FLOOR IS PROPOSED ANYWHERE. The record reports the informative-carrier distribution — both percentile rows and both low-tail cumulative rows — and states explicitly that no floor is proposed, applied or named, and that no row has zero informative carriers while the matrix-reaching set has no singletons."
    - "STATE.md CARRIES THE ROW. `.planning/STATE.md`'s `### Quick Tasks Completed` table gains exactly ONE new row for `260902-vsp`, appended after the `260826-qq9` row, in the table's 6-column shape, and no other line of STATE.md is edited by this plan."
    - "NOTHING WAS FIRED. Zero AoU VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact; $0. The VM stays STOPPED and no step in this plan suggests starting it. No file under `.planning/amendments/` is touched. No `git add -A` and no `git add .`; every staged path is named."
  artifacts:
    - path: ".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md"
      provides: "The banked RUN 2 STEP 2 result AND the courier to Seth, in one file, with a byte-anchored verbatim appendix"
      contains: "VERBATIM APPENDIX"
      min_lines: 180
    - path: ".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md"
      provides: "The single source of truth for every number, committed so the record's appendix has an in-repo origin"
      contains: "PRE-REGISTERED VALUES"
    - path: ".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md"
      provides: "The two things this plan deliberately does NOT do, so neither becomes a silent omission"
      contains: "DEFERRED"
    - path: ".planning/STATE.md"
      provides: "The Quick Tasks Completed row for 260902-vsp"
      contains: "260902-vsp"
  key_links:
    - from: ".planning/debug/260902-COURIER-TO-SETH-RUN2-...md"
      to: ".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md"
      via: "verbatim script splice of `## ARTIFACTS`..EOF plus a stated md5/size anchor"
      pattern: "d10acca5ca2b6c15548bb50d5c11bc43"
    - from: ".planning/debug/260902-COURIER-TO-SETH-RUN2-...md"
      to: ".planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md"
      via: "named reference to the RUN 1 pre-registration, confirmed 5/5 + histogram, zero adjustments"
      pattern: "260826-PCS-ancestry-blind-manifest-read"
    - from: ".planning/STATE.md"
      to: ".planning/debug/260902-COURIER-TO-SETH-RUN2-...md"
      via: "Quick Tasks Completed row"
      pattern: "260902-vsp"
---

<objective>
Bank the **RUN 2 STEP 2** result — the panel-wide PRE- vs POST-filter classification of
the DEFINED-row tail — as ONE new docs-only record in `.planning/debug/`, written so it
serves simultaneously as the permanent bank record and as the courier to Seth. Then add
one row to `.planning/STATE.md`'s `### Quick Tasks Completed` table.

Purpose: Seth CONCEDED Q4 and then refused the rest of the consultation until one thing
was settled — are the 3,094 defined rows with `carriers_lost_frac >= 0.9` PRE-filter (the
posted rule already discards them, a characterisation) or POST-filter (they survive into
the banked LD matrix, "a prevalent, systematic, silent corruption")? RUN 2 STEP 2 answered
it. **Both, in every region.** That answer, its two independent companions, its six scope
caveats and its unflattering limitations need to exist in the repo before they exist in a
reply.

Output: one `.planning/debug/` record, one `deferred-items.md`, one STATE.md row, one
commit with explicit paths.

**DOCS-ONLY. NOTHING IS FIRED. THE VM STAYS STOPPED.**
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
@.planning/debug/260820-COURIER-TO-SETH-revision-reply.md
@.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md
@.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md
@.planning/STATE.md
</context>

<non_negotiable_constraints>

These are constraints, not preferences. Each one has a verification step attached below.

1. **DOCS-ONLY.** Nothing under `src/` or `tests/` changes. `git status --porcelain -- src tests`
   was EMPTY at plan time and must be EMPTY at commit time. The 0.0005 contradiction is
   FLAGGED here and FIXED in a separate task.
2. **DO NOT RECOMPUTE, RE-DERIVE OR "SANITY CHECK" ANY NUMBER.** Every number in
   `CONTENT-SPEC.md` is measured and verified. Copy it. If a number appears to disagree with
   something else in the repo, **STOP and report it** — never reconcile silently. A count is
   a claim.
3. **NOTHING IS FIRED.** No AoU VM, no Dataproc, no `gcloud`, no `gsutil`, no network. Do not
   suggest starting the VM. Carter is stopping it; an agent never fires it.
4. **NO OSF CONTACT OF ANY KIND.** Never edit the posted July amendment in-repo. Nothing under
   `.planning/amendments/` is touched.
5. **EXPLICIT GIT PATHS ONLY.** Never `git add -A`, never `git add .`. This is a shared GPFS
   tree and a bare add has already caused a multi-terminal collision.
6. **DO NOT EDIT THE PREDECESSOR RECORDS.** `.planning/debug/260901-PENDING-PASTE-...md` has
   FIRED; `.planning/debug/260826-PCS-...md` holds a pre-registration; both are read-only for
   this plan. So is `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`.
7. **NO CARRIER FLOOR.** The record reports a distribution and proposes no floor, applies none
   and names none. Seth withheld the value deliberately.
8. **THE UNTRACKED `.planning/debug/m3-producer-unbounded-dense-read.md` IS NOT OURS.** It was
   untracked before this plan and stays untracked. Do not stage it.

</non_negotiable_constraints>

<flags_reported_not_reconciled>

Per constraint 2, these are reported to Carter rather than silently smoothed. Neither is a
numeric disagreement; both are **attribution** questions, and both change what the record is
allowed to say.

## FLAG-1 — the task brief attributes the three pre-registered values to `260826`; the tree does not

The brief says `260826-PCS-...md` is "the PRE-REGISTRATION this run answers" and that the
record "must state that all three pre-registered values passed with ZERO adjustments."
Measured against the tree, those are **two different pre-registrations**:

* `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md`
  §(e) *"PRE-REGISTERED PREDICTION — RECORDED BEFORE THE RE-RUN"* (file line 551) contains a
  table of **seven** rows: `n_undefined_rows` 15, `n_undefined_distinct_pairs` 13,
  `n_undefined_already_occluded` 10, `n_undefined_not_already_occluded` 3, the offset
  histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`, `POOLED candidate rows` 353089,
  `wc -l pcs_pairs.tsv` 353090. **None of `n_tail_rows_in`, `n_tail_rows_out_of_scope` or
  `n_defined_rows_out_of_scope` appears in it.** That table is what **RUN 1** answered, and
  `.planning/STATE.md` records it CONFIRMED **5/5 plus the histogram, ZERO adjustments**, on
  2026-09-01.
* The three values in `CONTENT-SPEC.md` belong to **RUN 2 STEP 2**. Their pre-run anchor is
  `.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md`:
  **3,094** is stated at `:19` and again at `:48` (`3,094 / 353,074 = 0.876%`) before the run,
  and the zero out-of-scope expectation for the FULL run is the stated contrast at `:124`
  ("With `--region-ids` given, the run is NARROWED on purpose and `n_defined_rows_out_of_scope`
  / `n_tail_rows_out_of_scope` will be large. That is the smoke's basis"). At runtime the
  `--pcs-summary` reconciliation RAISES before writing anything if `n_tail_rows_in` disagrees
  with the code-frozen scanner's own `n_defined_lost_frac_ge_0p9`.
* ⚠ **The same file also says, under `### NO EXPECTED VALUE IS STATED`:** *"Not for
  `n_tail_rows_in`, not for either side of the split, not for any percentile."* Read in
  context that disclaimer is about the **split** and the **percentiles** — the quantities
  never computed before — while 3,094 was a carried-forward, runtime-enforced quantity. **That
  reading is an inference, and it is not this plan's to bake.**

**What the record is therefore REQUIRED to do (Task 1, §PRE-REGISTERED VALUES):**
state both, separately and by name — RUN 1's `260826` §(e) prediction confirmed **5/5 + the
histogram, ZERO adjustments**; RUN 2 STEP 2's **three** values `3094 / 0 / 0` **PASS, ZERO
adjustments**, anchored to the `260901` PENDING PASTE and the runtime `--pcs-summary` gate.
**It MUST NOT write a sentence claiming `260826` pre-registered `3094 / 0 / 0`.** It MUST
carry a one-paragraph note naming the `NO EXPECTED VALUE IS STATED` line and saying which
quantities it covers and which it does not.

**Not fixed here:** the `260901` PENDING PASTE is a FIRED runbook (constraint 6). If Carter
wants its disclaimer sentence narrowed in wording, that is a separate task. Recorded in
`deferred-items.md`.

## FLAG-2 — four prior quick tasks are missing from the STATE.md Quick Tasks Completed table

The table ends at `.planning/STATE.md:2300` with the `260826-qq9` row. `260828-uej`,
`260831-kw8`, `260901-l55` and `260901-rvu` all completed and all have `.planning/quick/`
directories, and none has a row. (Each IS represented in the `last_activity` frontmatter and
in a narrative section.)

**This plan appends ONE row, for `260902-vsp`, and DOES NOT backfill the other four.**
Backfilling would mean authoring four descriptions from other summaries inside a docs-only
bank task — exactly the kind of unverified claim this record must not contain. Recorded in
`deferred-items.md` as a follow-up.

</flags_reported_not_reconciled>

<tasks>

<task type="auto">
  <name>Task 1: Write the RUN 2 STEP 2 bank record + courier, with a script-spliced verbatim appendix</name>

  <files>.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md</files>

  <action>
**The filename is EXACT. Do not shorten, re-slug or re-date it.** It follows the
`.planning/debug/` convention of its neighbours (`260819-COURIER-TO-SETH-distribution-and-discriminators.md`,
`260820-COURIER-TO-SETH-revision-reply.md`, `260826-PCS-...-and-the-prereg-prediction.md`):
`YYMMDD-` prefix, then a descriptive slug naming the finding.

**STEP 1 — anchor the source before writing a word.**

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
md5sum .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
wc -lc .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md
```

EXPECT `d10acca5ca2b6c15548bb50d5c11bc43`, **124** lines, **8248** B. **If any differs: STOP.**
A different spec answers a different question and no number below is comparable. Put the
measured md5 and byte size into the record's provenance line — the record must name the bytes
it was built from.

**STEP 2 — write the human-readable body.** These sections are REQUIRED, in this order, each
a top-level `##` heading. Register: the `260820-COURIER-TO-SETH-revision-reply.md` voice —
declarative, numbers with their basis attached, no hedging, no throat-clearing.

1. **Title + status line.** Title names the result, not the activity. Status line, one line,
   the established shape: measurement banked; nothing fired; VM STOPPED; $0; docs-only; an
   agent never posts and never fires.
2. **`## WHAT THIS BANKS, AND WHERE EVERY NUMBER COMES FROM`** — one paragraph. Names
   `CONTENT-SPEC.md` with its md5/size from STEP 1, states that the appendix is spliced BY
   SCRIPT and is the authority, and that the prose restates rather than re-derives.
3. **`## THE RUN`** — the artifacts and the run-level provenance. `pcs_tail_verdicts.tsv`
   (md5 `960f283734aea3b2c56c9249cf4fe94b`, 1031086 B) and `pcs_tail_summary.json` (md5
   `bd74c0d502d15ac4e2fb5e1bdafc72b1`, 38548 B), both written 2026-09-02T21:07:03Z, launched
   18:26:17Z, 2 h 40 m 46 s wall. **They live on the AoU VM, not in this repo — say so.**
   `bim_sha256` / `pairs_tsv_sha256` / `regions_tsv_sha256` in full, with the note that the
   regions hash was **VERIFIED IN THIS SESSION** to equal `sha256sum config/ld_regions.tsv` at
   HEAD. Ancestry AFR. ⚠ **`region_ids_selected = 276` is the ancestry-resolved MANIFEST size,
   NOT the number of regions carrying rows. 21 regions carry rows. State this explicitly in
   its own sentence.** `region_ids_out_of_scope = []`.
4. **`## PRE-REGISTERED VALUES — THREE, AND THEY ALL PASSED WITH ZERO ADJUSTMENTS`** — write
   this section exactly as FLAG-1 above requires. RUN 1's `260826` §(e) prediction: confirmed
   **5/5 + the offset histogram, ZERO adjustments**, named as a SEPARATE and EARLIER
   pre-registration. RUN 2 STEP 2's three: `n_tail_rows_in` measured 3094 / expected 3094 /
   PASS; `n_tail_rows_out_of_scope` 0 / 0 / PASS; `n_defined_rows_out_of_scope` 0 / 0 / PASS —
   anchored to `260901-PENDING-PASTE-...md:19`, `:48`, `:124` and to the runtime
   `--pcs-summary` reconciliation that raises before writing. Then the required one-paragraph
   note on that file's `### NO EXPECTED VALUE IS STATED` line: quote it, say it covers the
   split and the percentiles, say the reading that it does not cover the carried-forward 3,094
   is an INFERENCE stated here and not silently baked into either file. **Do not write that
   260826 pre-registered 3094/0/0.**
5. **`## FINDING 1 — THE TAIL IS PRE-FILTER DOMINANT, WITH A POST-FILTER RESIDUAL IN EVERY REGION`**
   — rows 2560 PRE / 534 POST of 3094, POST = 17.26%; pairs 2047 PRE / 474 POST of 2521,
   POST = 18.80%; **21 regions carry tail rows and ZERO regions have zero POST rows.** Pooled
   defined-row accounting: `n_rows_in_tsv` 353089, `n_defined_rows_in` 353074,
   `n_undefined_rows_in` 15, `n_defined_rows_member_occluded_panelwide` 7475,
   `n_defined_rows_reaching_matrix` 345599, `n_pairs_with_ambiguous_member_id` 0. Say what the
   answer MEANS for Seth's fork: it is not the clean PRE-filter that would have made this a
   characterisation, and not a uniform POST-filter either — the residual is present in every
   single region.
6. **`## FINDING 2 — THE REGIONS DO NOT SHARE A COMMON POST RATE`** — ⚠ **LEAD WITH THE
   REDUCED FIGURE.** Pair-level dropping `m2_region_00060__sub13` (78.5% inside sub12's
   window): chi2 **37.78**, dof **19**, p **6.3e-3**, overdispersion **1.99x** — this is the
   headline. THEN the all-21 pair-level figure (chi2 47.24, dof 20, p 5.4e-4, overdispersion
   **2.36x**) shown alongside and explained as inflated by the chr15 overlap, whose two regions
   rank 2nd and 3rd on POST fraction and are largely one locus. Then row-level all-21 (chi2
   51.25, dof 20, p 1.5e-4, overdispersion 2.56), the row-level POST fraction range
   8.33%–36.36%, CV 0.365. Then **UNEXPLAINED**: spearman(POST frac, window rows) = **-0.199**,
   spearman(POST frac, occluded ids) = **-0.201**, spearman(POST frac, occlusion density) =
   **+0.004** — in a design with the power to find spearman(tail rows, window rows) =
   **+0.886**. State that last clause as the power argument it is: the design CAN find a strong
   structural correlation, and did, just not for this.
7. **`## FINDING 3 — DEFINITIONAL DISAGREEMENT, A SEPARATE AND INDEPENDENT AXIS`** — where
   `informative_carriers_rarer != informative_carriers_min`: **751 / 3094 = 24.27%** in the
   tail versus **1826 / 349980 = 0.52%** below it, a **46.5x** enrichment. NOT a tie artifact:
   `rarer_by_maf_tie` is False for **ALL 3094** tail rows. **Independence is carried by
   `spearman(POST frac, disagree frac) = +0.173` over 21 regions.** ⚠ **Do NOT support
   independence with the PRE-vs-POST 2x2** — you may REPORT it (606/2560 = 23.67% vs 145/534 =
   27.15%, chi2 2.914, p 0.088, Fisher p 0.096, POST trending HIGHER) but you MUST label it
   **UNDERPOWERED, NOT NULL**, and the independence claim must lean on the rho. Then: also
   heterogeneous but less so (chi2 37.80, dof 20, p 0.0094, overdispersion 1.89, CV 0.196),
   tail disagreement spread 13.7%–32.1%. Close with the definitions: "rarer" is decided by
   `*_maf_marginal` (each member's MAF over its OWN called set), never by carrier counts,
   **because `n_called_del != n_called_partner` IS the phenomenon under study**;
   `informative_carriers_min = min(del_retained, partner_retained)`; they are emitted side by
   side because `SE(r) ~ 1/sqrt(m)` binds on the MINIMUM while the rarer-variant definition is
   the scientifically motivated one.
8. **`## THE THREE FINDINGS ARE INDEPENDENT`** — short, explicit, its own section. They are not
   one result described three ways; the axis linking 1 and 3 is measured at rho = **+0.173**.
9. **`## ALSO BANKED`** — Seth's class (i) is **EMPTY**. The ONE surviving pair: region
   `m2_region_00149`, deletion `chr7:89454077:GCGTA:G`, partner `chr7:89454076:C:T`, offset
   **-1**, side upstream, `already_occluded` False, `pair_key` `9776035|9776036`; offset
   histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`, **NO positive offset anywhere**. Then, in
   its own paragraph: **`chr7:89454077` CANNOT be sited as at-signal versus cold-sequence.** No
   genome-wide fine-mapping exists — only Track A candidate-locus
   `results/multitrait/coloc_susie_R2*`, and NO MTAG outputs. **It is BLOCKED ON THIS VERY
   PANEL, not skipped. Say it plainly.** Then the informative-carrier distribution: percentiles
   p0/p1/p5/p10/p25/p50/p75/p90/p99/p100 for `defined_rows` = 1 / 413 / 792 / 907 / 1419 /
   3239 / 7959 / 15948 / 39551 / 54843 and for `reaching_matrix` = 2 / 728 / 813 / 934 / 1461 /
   3314 / 8074 / 16098 / 39630 / 54843; low-tail cumulative `defined_rows` n_le_1=4,
   n_le_100=1938, n_gt_100=351136 (sum 353074) and `reaching_matrix` n_le_1=0, n_le_100=313,
   n_gt_100=345286 (sum 345599); **NO row has zero informative carriers and the matrix-reaching
   set has NO singletons**; **NO CARRIER FLOOR IS PROPOSED — the tool emits the distribution
   only.**
10. **`## SCOPE CAVEATS`** — all six, each as its own `###` subsection with its own heading, in
    prose, stated plainly. Not footnotes, not softened, not collapsed into the appendix:
    (1) `n_tail_distinct_pairs_in = 2521` is the SUM of per-region distinct pairs, NOT a
    panel-wide dedup; verified identical to the per-region column sum.
    (2) `pair_key` is INDEX-keyed DELIBERATELY (`src/python/pairwise_completeness_scan.py:508`,
    `_pair_key` over `.bim` ROW INDICES) — a vid key would UNDERCOUNT because two `.bim` rows
    can share an id. **564 of 2461** panel-wide pairs (**22.9%**) are DELETION-DELETION
    NEIGHBOURS contributing two anchored rows each — a STRUCTURAL property of the tail, NOT a
    defect. Closure: **1897 + 2*564 = 3025, + 69 cross-region = 3094** tail rows. ⚠
    `already_occluded` is ANCHOR-RELATIVE, so the two anchored rows of one such pair SHOULD
    differ — that is not a conflict.
    (3) The chr15 overlap: `m2_region_00060__sub12` x `__sub13` share **6,000,001 bp** (78.5%
    of sub13, 56.4% of sub12). It is the ONLY overlap among the 21 — all **210** pairs
    enumerated against `config/ld_regions.tsv`. **69** ordered rows are adjudicated TWICE under
    two DIFFERENT excludelists built over two DIFFERENT row sets; **69/69 agree** on the exact
    `(del_occ, partner_occ)` tuple, zero disagreements. "Final for its region" holds where
    testable.
    (4) `n_defined_rows_rarer_and_min_definitions_disagree` has **NO per-region emission**. The
    per-region spread is available for the TAIL only. The **1826** below-tail disagreements
    have **NO regional attribution in this artifact**.
    (5) Provenance is **RUN-LEVEL only**. Per-region monotonicity conditions attach via
    `n_rows_in_window` against ONE shared `bim_sha256`.
    (6) **MONOTONICITY.** Occlusion is monotone in the row set, so an OCCLUDED verdict on a
    subset is SOUND while a NOT-OCCLUDED verdict on a subset is CONDITIONAL. Each region's
    window is COMPLETE at `pad_bp=0` against fixed manifest bounds with ONE excludelist per
    region, so these verdicts are FINAL for their region and do NOT shrink as regions are
    added.
11. **`## HONEST LIMITATIONS`** — verbatim in substance, not softened, no consoling clause
    appended. The VM blackout (machine rebooted; `uptime` showed 14 min against a 21:07:03Z
    write); the full stdout and the exit status `$?` are **UNRECOVERABLE and were NEVER SEEN
    by anyone**; the completion verdict rests entirely on the three pre-registered values plus
    the artifacts; there is **NO pre-reboot hash**, so the recorded md5s **anchor FORWARD, not
    backward** — they cannot prove byte-identity to what was written at 21:07:03Z. What they DO
    establish: a damaged file would not have parsed and summed to exactly 3094/0/0.
12. **`## ACTION ITEM — THE 0.0005 BOUND IS A LIVE CONTRADICTION (NOT FIXED HERE)`** — all four
    citations, each `path:line` with the quoted text, verified present in the tree at plan
    time: `src/python/pairwise_completeness_scan.py:45` "the withdrawn ``0.0005`` bound";
    `src/python/condition_ld_matrix.py:120` `ceiling_frac: float = 0.0005` (live default);
    `src/python/write_conditioned_ld_npz.py:64` `ceiling_frac: float = 0.0005` (live default);
    `src/python/write_conditioned_ld_npz.py:17` "the pre-registered 0.0005". One module says
    withdrawn, another says pre-registered, and the value is live in both. **State that this
    task is DOCS-ONLY and deliberately does not fix it; a code fix belongs to a SEPARATE task.**
13. **`## THE ASK`** — what Seth is being asked for, scoped the way the `260820` courier scopes
    its ask: not a re-read of everything. Name the specific things: whether the
    every-region POST residual changes his PRE/POST fork disposition; whether the unexplained
    heterogeneity (1.99x, no structural covariate, in a design with power to find +0.886)
    changes what must be pre-registered; and whether the rarer-vs-min disagreement's 46.5x
    tail enrichment is a third disclosure or a property of the first. State that no floor is
    proposed and none is being requested.
14. **`## VERBATIM APPENDIX — CONTENT-SPEC.md \`## ARTIFACTS\` .. EOF (spliced by script)`** —
    see STEP 3.

**STEP 3 — splice the appendix BY SCRIPT. Do not retype it.**

Locate the start by matching the line `## ARTIFACTS (on the AoU VM, not in this repo)` and
take everything from there to EOF. **Do not hardcode line numbers** — a hardcoded `7` drifts.
Emit the slice inside a fenced block whose opening fence line is exactly:

```
<!-- BEGIN VERBATIM APPENDIX (byte-equal to CONTENT-SPEC.md from '## ARTIFACTS' to EOF) -->
```

and whose closing marker line is exactly:

```
<!-- END VERBATIM APPENDIX -->
```

Between the two markers: the slice bytes, unmodified, with **no** re-wrapping, **no** added
indentation and **no** surrounding code fence (the slice already contains markdown headings;
wrapping it in a fence would change bytes on the way back out). Nothing else may appear
between those two marker lines.

**STEP 4 — the prose ordering rule.** In the region of the file **strictly before** the BEGIN
marker, the first occurrence of `1.99` must precede the first occurrence of `2.36`. (The
appendix itself lists 2.36 first, per the spec's own order — that is why the check is scoped
to the prose region. Do not "fix" the appendix.)
  </action>

  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && python3 - <<'EOF'
import hashlib, pathlib, sys

SPEC = pathlib.Path(".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md")
REC  = pathlib.Path(".planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md")

BEGIN = "<!-- BEGIN VERBATIM APPENDIX (byte-equal to CONTENT-SPEC.md from '## ARTIFACTS' to EOF) -->"
END   = "<!-- END VERBATIM APPENDIX -->"

fail = []

spec_b = SPEC.read_bytes()
if hashlib.md5(spec_b).hexdigest() != "d10acca5ca2b6c15548bb50d5c11bc43":
    sys.exit("SPEC MOVED — STOP. md5=%s" % hashlib.md5(spec_b).hexdigest())
if len(spec_b) != 8248:
    sys.exit("SPEC MOVED — STOP. bytes=%d" % len(spec_b))

spec_txt = spec_b.decode()
anchor = "## ARTIFACTS (on the AoU VM, not in this repo)"
if anchor not in spec_txt:
    sys.exit("SPEC ANCHOR MISSING — STOP")
slice_txt = spec_txt[spec_txt.index(anchor):]

if not REC.exists():
    sys.exit("RECORD NOT WRITTEN YET: %s" % REC)
rec = REC.read_text()

# 1. appendix present exactly once, byte-equal to the spec slice
if rec.count(BEGIN) != 1 or rec.count(END) != 1:
    fail.append("appendix markers must appear exactly once each (got %d/%d)"
                % (rec.count(BEGIN), rec.count(END)))
else:
    i = rec.index(BEGIN) + len(BEGIN)
    j = rec.index(END)
    if j < i:
        fail.append("END marker precedes BEGIN marker")
    else:
        got = rec[i:j].strip("\n")
        want = slice_txt.strip("\n")
        if got != want:
            fail.append("APPENDIX IS NOT BYTE-EQUAL to CONTENT-SPEC '## ARTIFACTS'..EOF "
                        "(got %d chars, want %d)" % (len(got), len(want)))

    # 2. headline ordering, scoped to the PROSE region only
    prose = rec[:rec.index(BEGIN)]
    a, b = prose.find("1.99"), prose.find("2.36")
    if a < 0:
        fail.append("prose never states the reduced overdispersion 1.99")
    elif b >= 0 and b < a:
        fail.append("prose leads with 2.36 before 1.99 — headline must be the REDUCED figure")

# 3. required section headings
for h in ["## WHAT THIS BANKS", "## THE RUN", "## PRE-REGISTERED VALUES",
          "## FINDING 1", "## FINDING 2", "## FINDING 3",
          "## THE THREE FINDINGS ARE INDEPENDENT", "## ALSO BANKED",
          "## SCOPE CAVEATS", "## HONEST LIMITATIONS", "## ACTION ITEM", "## THE ASK",
          "## VERBATIM APPENDIX"]:
    if h not in rec:
        fail.append("missing required section: %s" % h)

# 4. six caveats as their own subsections
n_sub = rec.count("\n### ")
if n_sub < 6:
    fail.append("scope caveats must be their own '###' subsections (found %d '###' headings)" % n_sub)

# 5. load-bearing strings that must survive into the PROSE, not only the appendix
prose = rec[:rec.index(BEGIN)] if BEGIN in rec else rec
for tok in ["d10acca5ca2b6c15548bb50d5c11bc43", "8248",
            "960f283734aea3b2c56c9249cf4fe94b", "bd74c0d502d15ac4e2fb5e1bdafc72b1",
            "2026-09-02T21:07:03Z",
            "9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99",
            "eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583",
            "e3c25ea083490017ffe7461fbcc1df5d3788e23f9c4130602c8bc9d040ce4d6a",
            "3094", "17.26", "18.80", "37.78", "6.3e-3", "1.99", "2.36",
            "+0.886", "+0.173", "24.27", "0.52", "46.5",
            "23.67", "27.15", "0.088", "0.096",
            "9776035|9776036", "chr7:89454077:GCGTA:G", "chr7:89454076:C:T",
            "54843", "351136", "345286",
            "pairwise_completeness_scan.py:45", "condition_ld_matrix.py:120",
            "write_conditioned_ld_npz.py:64", "write_conditioned_ld_npz.py:17",
            "pairwise_completeness_scan.py:508",
            "260826-PCS-ancestry-blind-manifest-read",
            "260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter",
            "1897 + 2*564 = 3025", "69/69", "6,000,001",
            "NO CARRIER FLOOR IS PROPOSED", "UNRECOVERABLE", "NEVER SEEN",
            "anchor FORWARD", "BLOCKED ON THIS", "MTAG",
            "UNDERPOWERED", "276", "21 regions"]:
    if tok not in prose:
        fail.append("prose is missing load-bearing string: %r" % tok)

if fail:
    print("RED (%d):" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("GREEN — record structure, appendix byte-equality, headline ordering and all "
      "load-bearing strings verified")
EOF
    </automated>
    <negative_control>
**This gate was already PROVEN ABLE TO FAIL at plan time**, on scratchpad fixtures: a
`3094` -> `3095` flip inside the appendix went RED with `APPENDIX IS NOT BYTE-EQUAL ...
(got 7962 chars, want 7962)` — note the IDENTICAL character count, so a length check alone
would have missed it — and an inverted prose order went RED with the headline rule. Reproduce
both yourself against the REAL record; do not inherit this observation.

Green is evidence only if it has been seen fail. Copy the record to the SESSION SCRATCHPAD
(never `/tmp`, never inside the repo tree), perturb ONE byte inside the appendix region
(e.g. `3094` -> `3095`), point the checker's `REC` at the copy, and confirm it exits 1
naming "APPENDIX IS NOT BYTE-EQUAL". Then, on a second scratch copy, move the first `2.36`
in the prose above the first `1.99` and confirm it exits 1 naming the headline rule. Delete
both scratch copies. Report both RED observations in the SUMMARY.
    </negative_control>
  </verify>

  <done>
`.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md`
exists; the checker exits 0; the appendix is proven byte-equal to `CONTENT-SPEC.md` from
`## ARTIFACTS` to EOF; the prose leads with 1.99 and explains 2.36; both negative controls
were observed RED. `git status --porcelain -- src tests` is EMPTY.
  </done>
</task>

<task type="auto">
  <name>Task 2: Append the Quick Tasks Completed row to STATE.md (and record the two deferrals)</name>

  <files>.planning/STATE.md, .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md</files>

  <action>
**2a — the STATE.md row.** `.planning/STATE.md` has a `### Quick Tasks Completed` table at
line 2151 whose header is:

```
| # | Description | Date | Commit | Status | Directory |
```

Its LAST row is `260826-qq9` at line 2300, followed by a blank line at 2301 and
`## Session Continuity` at 2302. **Append exactly ONE new row immediately after the
`260826-qq9` row.** Six columns, matching the shape of the recent rows (e.g. `260825-ngh`,
`260824-fast-env-stop`):

* `#` = `260902-vsp`
* `Description` = a dense bolded lead sentence naming the RESULT, then the three findings in
  order with their headline numbers (rows 2560 PRE / 534 POST of 3094, POST 17.26%, **zero
  regions with zero POST rows**; heterogeneity **1.99x** reduced / 2.36x all-21 with the chr15
  explanation, unexplained by any structural covariate in a design that finds +0.886; the
  definitional disagreement 751/3094 = 24.27% vs 1826/349980 = 0.52%, **46.5x**, independent
  at rho +0.173), the three pre-registered values `3094 / 0 / 0` **PASS, ZERO adjustments**
  (distinct from RUN 1's 5/5 + histogram), the ONE surviving pair and that `chr7:89454077` is
  **BLOCKED ON THIS PANEL**, the 0.0005 contradiction FLAGGED not fixed, the honest limitation
  (stdout and `$?` unrecoverable, never seen; md5s anchor FORWARD), and the close: docs-only,
  NOTHING FIRED, VM STOPPED, $0.
* `Date` = `2026-09-02`
* `Commit` = `(this commit)` — the precedent is the `260824-fast-env-stop` row; do NOT invent
  or back-fill a hash the row cannot know.
* `Status` = `Inline (docs-only; appendix byte-equality + both negative controls observed RED)`
* `Directory` = `[260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu](./quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/)`

⚠ Markdown table cells: escape any literal `|` inside the Description (the existing
`260824-fast-env-stop` row escapes it as `\|`). The pair_key `9776035|9776036` must therefore
be written `9776035\|9776036` if it appears in the cell — or simply omitted from the row,
since the record carries it.

⚠ **Edit ONLY that one insertion point.** Do not touch the `last_activity` frontmatter, the
narrative sections, `HANDOFF.json`, or any other line. Those are out of scope for this brief.

**2b — `deferred-items.md`.** New file in the task directory, matching the shape of
`.planning/quick/260901-rvu-.../deferred-items.md`. Two entries, each with what, why deferred,
and what would discharge it:

1. **DEFERRED — the 0.0005 contradiction (code fix).** Four citations as in the record. Why:
   this task is docs-only by explicit constraint. Discharge: a separate quick that decides
   whether the bound is withdrawn or pre-registered, makes both docstrings agree with the live
   default, and lands an enforcer test so the agreement has a named guard.
2. **DEFERRED — four missing STATE.md Quick Tasks rows** (`260828-uej`, `260831-kw8`,
   `260901-l55`, `260901-rvu`). Why: backfilling four descriptions from other summaries inside
   a bank task would introduce unverified claims into a file that must not carry them.
   Discharge: a separate quick that writes each row from that task's own SUMMARY.
3. **NOT DEFERRED, REPORTED** — FLAG-1's attribution note. Record that the `260901` PENDING
   PASTE's `### NO EXPECTED VALUE IS STATED` line was NOT edited (it is a fired runbook), that
   the record handles it by attribution rather than by amendment, and that narrowing its
   wording is Carter's call.
  </action>

  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && python3 - <<'EOF'
import pathlib, sys
lines = pathlib.Path(".planning/STATE.md").read_text().splitlines()
fail = []

hdr = [i for i, l in enumerate(lines) if l.startswith("### Quick Tasks Completed")]
if len(hdr) != 1:
    sys.exit("expected exactly one '### Quick Tasks Completed' heading, got %d" % len(hdr))

rows = [(i, l) for i, l in enumerate(lines) if l.startswith("| 260")]
ours = [(i, l) for i, l in rows if l.startswith("| 260902-vsp ")]
if len(ours) != 1:
    fail.append("expected exactly ONE 260902-vsp row, got %d" % len(ours))
else:
    i, row = ours[0]
    prev = [j for j, l in rows if j < i]
    if not prev or not lines[max(prev)].startswith("| 260826-qq9 "):
        fail.append("260902-vsp row must sit immediately after the 260826-qq9 row")
    # six columns => seven pipe-delimited fields with leading/trailing empties
    cells = [c for c in row.split("|")]
    if len(cells) != 8:
        fail.append("row must have exactly 6 cells (found %d fields); "
                    "escape any literal '|' inside the Description as '\\|'" % (len(cells) - 2))
    for tok in ["2026-09-02", "(this commit)",
                "./quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/",
                "3094", "17.26", "1.99", "46.5", "ZERO adjustments",
                "BLOCKED", "0.0005", "NOTHING FIRED"]:
        if tok not in row:
            fail.append("STATE.md row missing %r" % tok)

d = pathlib.Path(".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md")
if not d.exists():
    fail.append("deferred-items.md missing")
else:
    t = d.read_text()
    for tok in ["0.0005", "260828-uej", "260831-kw8", "260901-l55", "260901-rvu",
                "NO EXPECTED VALUE IS STATED"]:
        if tok not in t:
            fail.append("deferred-items.md missing %r" % tok)

if fail:
    print("RED (%d):" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("GREEN — STATE.md row placement/shape/content and deferred-items.md verified")
EOF
    </automated>
    <negative_control>
Before running the checker against the real tree, run it once against a scratchpad copy of
STATE.md with the new row DELETED and confirm it exits 1 naming "expected exactly ONE
260902-vsp row, got 0"; and once with the row moved above `260826-qq9` and confirm it exits 1
naming the placement rule. Delete the scratch copies. Report both RED observations.
    </negative_control>
  </verify>

  <done>
`.planning/STATE.md` gains exactly one 6-cell `260902-vsp` row immediately after the
`260826-qq9` row and nothing else in the file changed (prove with
`git diff --stat -- .planning/STATE.md`: additions only, and
`git diff -U0 -- .planning/STATE.md | grep -c '^-[^-]'` = 0). `deferred-items.md` exists with
all three entries. Both negative controls observed RED.
  </done>
</task>

<task type="auto">
  <name>Task 3: Scope gate, then ONE commit with explicit paths</name>

  <files>.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md, .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md, .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md, .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-PLAN.md, .planning/STATE.md</files>

  <action>
**STEP 1 — the docs-only gate, BEFORE staging.** All three must hold:

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
git status --porcelain -- src tests            # MUST print NOTHING
git status --porcelain -- .planning/amendments # MUST print NOTHING
git diff --stat -- .planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md \
                   .planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md \
                   .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md   # MUST print NOTHING
```

Any output from any of these: **STOP**. Do not "clean it up" — report it.

**STEP 2 — stage EXPLICIT PATHS ONLY.** ⛔ Never `git add -A`, never `git add .`. Shared GPFS
tree. Five paths, named:

```bash
git add \
  .planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md \
  .planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-PLAN.md \
  .planning/STATE.md
```

**STEP 3 — prove the staged set is exactly those five.** `git diff --cached --name-only | sort`
must equal the sorted five paths — no more (in particular NOT the pre-existing untracked
`.planning/debug/m3-producer-unbounded-dense-read.md`, which is not ours and stays untracked)
and no fewer.

**STEP 4 — commit.** Use this message. The `Co-Authored-By` trailer is mandatory and must be
the final line.

```
docs(quick-260902-vsp): bank RUN 2 STEP 2 — the defined-row tail is PRE-filter DOMINANT with a POST-filter RESIDUAL IN EVERY REGION, the regions do NOT share a common POST rate, and rarer-vs-min disagreement is a SEPARATE axis

Seth conceded Q4 and then refused the rest of the consultation until one thing was
settled: are the 3,094 defined rows with carriers_lost_frac >= 0.9 PRE-filter (the
posted rule already discards them) or POST-filter (they survive into the banked LD
matrix)? RUN 2 STEP 2 answered it. BOTH — and the POST residual is present in every
single region.

FINDING 1 — rows 2560 PRE / 534 POST of 3094 (POST 17.26%); pairs 2047 PRE / 474 POST
of 2521 (POST 18.80%); 21 regions carry tail rows and ZERO regions have zero POST rows.
Pooled: n_rows_in_tsv 353089, n_defined_rows_in 353074, n_undefined_rows_in 15,
member_occluded_panelwide 7475, reaching_matrix 345599, ambiguous_member_id 0.

FINDING 2 — the regions do NOT share a common POST rate. HEADLINE is the REDUCED
figure: dropping m2_region_00060__sub13 (78.5% inside sub12's window) gives chi2 37.78,
dof 19, p 6.3e-3, overdispersion 1.99x. The all-21 2.36x is shown alongside and is
INFLATED by the chr15 overlap (its two regions rank 2nd and 3rd on POST fraction and are
largely one locus). UNEXPLAINED: spearman(POST frac, window rows) -0.199, (occluded ids)
-0.201, (occlusion density) +0.004 — in a design with the power to find
spearman(tail rows, window rows) = +0.886.

FINDING 3 — a SEPARATE and INDEPENDENT axis. informative_carriers_rarer !=
informative_carriers_min in 751/3094 = 24.27% of tail rows vs 1826/349980 = 0.52% below
it, a 46.5x enrichment; rarer_by_maf_tie is False for ALL 3094 rows, so not a tie
artifact. Independence carried by spearman(POST frac, disagree frac) = +0.173; the
PRE-vs-POST 2x2 (23.67% vs 27.15%, chi2 2.914, p 0.088) is reported as UNDERPOWERED,
NOT NULL, and is deliberately NOT used as support.

PRE-REGISTERED VALUES — three, all PASS, ZERO adjustments: n_tail_rows_in 3094,
n_tail_rows_out_of_scope 0, n_defined_rows_out_of_scope 0. Attributed precisely: this is
a DIFFERENT and LATER pre-registration than RUN 1's 260826 §(e) table (15/13/10/3 +
histogram + 353089/353090), which was itself confirmed 5/5 + the histogram with zero
adjustments on 2026-09-01. The record names the 260901 PENDING PASTE's "NO EXPECTED
VALUE IS STATED" line rather than quietly working around it.

ALSO BANKED — Seth's class (i) is EMPTY. The ONE surviving pair: m2_region_00149,
chr7:89454077:GCGTA:G x chr7:89454076:C:T, offset -1, upstream, already_occluded False.
No positive offset anywhere. chr7:89454077 CANNOT be sited as at-signal vs cold-sequence
— no genome-wide fine-mapping exists (Track A candidate-locus only; NO MTAG outputs) —
so it is BLOCKED ON THIS VERY PANEL, not skipped. Informative-carrier distribution
emitted; NO row has zero informative carriers; the matrix-reaching set has NO singletons;
NO CARRIER FLOOR IS PROPOSED, applied or named.

Every number is spliced BY SCRIPT from CONTENT-SPEC.md (8248 B /
d10acca5ca2b6c15548bb50d5c11bc43) into a VERBATIM APPENDIX proven byte-equal at
verification time — nothing was retyped. All six scope caveats are stated in prose, in
their own subsections, including that 2521 is a per-region SUM not a panel-wide dedup,
that pair_key is INDEX-keyed deliberately (564/2461 = 22.9% deletion-deletion neighbours;
closure 1897 + 2*564 = 3025, + 69 cross-region = 3094), and the chr15 double-adjudication
agreeing 69/69.

HONEST LIMITATION, NOT SOFTENED: the run finished during a VM blackout. The full stdout
and the exit status $? are UNRECOVERABLE and were NEVER SEEN by anyone. There is no
pre-reboot hash, so the recorded md5s anchor FORWARD, not backward.

ACTION ITEM, FLAGGED NOT FIXED: the 0.0005 bound is a LIVE CONTRADICTION —
pairwise_completeness_scan.py:45 calls it withdrawn, write_conditioned_ld_npz.py:17
calls it pre-registered, and it is the live default at condition_ld_matrix.py:120 and
write_conditioned_ld_npz.py:64. DOCS-ONLY here; the code fix is a separate task.

DOCS-ONLY: src/ and tests/ untouched. No OSF contact; .planning/amendments/ untouched.
NOTHING FIRED — zero VM / Dataproc / gcloud / gsutil / network contact. VM STOPPED. $0.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

**STEP 5 — do NOT push.** Pushing is not in this brief.
  </action>

  <verify>
    <automated>
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
test -z "$(git status --porcelain -- src tests)" && \
test -z "$(git status --porcelain -- .planning/amendments)" && \
test -z "$(git diff HEAD~1 --name-only -- src tests .planning/amendments)" && \
diff <(git diff HEAD~1 --name-only | sort) <(printf '%s\n' \
  '.planning/STATE.md' \
  '.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md' \
  '.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-PLAN.md' \
  '.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md' \
  '.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/deferred-items.md' | sort) && \
git log -1 --format=%B | tail -1 | grep -qx 'Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>' && \
echo "GREEN — docs-only scope held, commit touched exactly the five intended paths, trailer is the final line"
    </automated>
  </verify>

  <done>
One commit on `m3-W2-aou-deltas` touching exactly five `.planning/` paths; `src/`, `tests/` and
`.planning/amendments/` untouched in both the working tree and the commit; the
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer is the final line of the
message; nothing pushed; nothing fired.
  </done>
</task>

</tasks>

<verification>

Run in order. None of these requires re-running the AoU pipeline, the scanner, the
reclassifier, or anything on a VM. Everything is a check on files already in the tree.

1. **Source anchor unmoved** — `CONTENT-SPEC.md` md5 `d10acca5ca2b6c15548bb50d5c11bc43`,
   8248 B, 124 lines. If moved: STOP.
2. **Appendix byte-equality** — Task 1's checker proves the record's appendix is byte-equal to
   `CONTENT-SPEC.md` from `## ARTIFACTS` to EOF. This is the guarantee that no number was
   retyped wrong.
3. **Headline ordering** — in the prose region strictly before the BEGIN marker, `1.99`
   precedes `2.36`.
4. **Structure** — all 13 required `##` sections present; the six scope caveats are `###`
   subsections.
5. **Load-bearing strings in the PROSE, not only the appendix** — the ~50-token list in Task 1.
6. **STATE.md** — exactly one `260902-vsp` row, 6 cells, immediately after `260826-qq9`;
   `git diff -U0 -- .planning/STATE.md | grep -c '^-[^-]'` = 0 (pure insertion).
7. **Docs-only** — `git status --porcelain -- src tests` EMPTY; `git diff HEAD~1 --name-only
   -- src tests .planning/amendments` EMPTY.
8. **Predecessor records untouched** — zero diff on the `260901`, `260826` and `260825`
   `.planning/debug/` files.
9. **Commit scope** — `git diff HEAD~1 --name-only` equals exactly the five intended paths;
   the untracked `.planning/debug/m3-producer-unbounded-dense-read.md` is still untracked.
10. **Trailer** — `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` is the final line.
11. **Four negative controls observed RED and reported** — two in Task 1 (perturbed appendix
    byte; prose ordering inverted), two in Task 2 (row deleted; row misplaced). A green
    assertion is evidence only if it has been seen fail.
12. **Nothing fired** — no VM, no Dataproc, no `gcloud`, no `gsutil`, no network, no OSF; $0.

</verification>

<success_criteria>

- [ ] `.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md`
      exists and reads as a self-contained record for someone who was not in this session
- [ ] The three findings are three sections with an explicit independence statement (rho +0.173)
- [ ] Heterogeneity headline is 1.99x; 2.36x appears only with its chr15 explanation
- [ ] All six scope caveats are prose subsections, not footnotes
- [ ] Honest limitations present and unsoftened (stdout and `$?` unrecoverable, NEVER SEEN,
      md5s anchor FORWARD not backward)
- [ ] The 0.0005 contradiction is an ACTION ITEM with all four `path:line` citations, and is
      NOT fixed
- [ ] `chr7:89454077` is stated BLOCKED ON THIS PANEL, not skipped
- [ ] No carrier floor is proposed, applied or named
- [ ] Pre-registration attribution is precise per FLAG-1; the two pre-registrations are not
      conflated
- [ ] `.planning/STATE.md` gains exactly one `260902-vsp` row; nothing else in the file changed
- [ ] `deferred-items.md` records the 0.0005 code fix, the four missing STATE.md rows, and the
      FLAG-1 attribution note
- [ ] ONE commit, five explicit paths, `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`
      as the final line
- [ ] `src/` and `tests/` untouched; `.planning/amendments/` untouched; predecessor records
      zero-diff
- [ ] Four negative controls observed RED and reported in the SUMMARY
- [ ] NOTHING FIRED; VM STOPPED; $0; nothing pushed

</success_criteria>

<output>
After completion, create
`.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/260902-vsp-SUMMARY.md`
recording: the record's path/size/md5, the appendix byte-equality result, the four RED
negative controls with what each one said, the STATE.md row placement, the two deferrals, and
FLAG-1 as an item for Carter. State plainly that nothing was fired and that Seth has NOT been
contacted — the courier exists in the repo; sending it is Carter's call.
</output>
