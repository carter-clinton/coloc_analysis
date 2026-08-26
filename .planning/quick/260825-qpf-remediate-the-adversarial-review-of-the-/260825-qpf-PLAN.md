---
phase: quick-260825-qpf
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, adversarial-review-remediation, plink-semantics-falsifier, undefined-ld, deletion-boundary, prevalence-sweep, r6-governance, tdd, instrument-only, m3-07, stage-b]

files_modified:
  - src/python/pairwise_completeness_scan.py
  - tests/m3/test_pairwise_completeness_scan.py
  - .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
  - .planning/HANDOFF.json
  - .planning/STATE.md
  - .planning/quick/260825-qpf-remediate-the-adversarial-review-of-the-/260825-qpf-PLAN.md
  - .planning/quick/260825-qpf-remediate-the-adversarial-review-of-the-/260825-qpf-SUMMARY.md

autonomous: true

requirements:
  - PCS-FIX-SEEK-INDEX-NORMALISED
  - PCS-FIX-PAIR-KEY-INDEX-BASED
  - PCS-FIX-MINOR-ALLELE-TIE-MAX-LOSS
  - PCS-REPORT-EDGE-CLIPPED-CANDIDATES
  - PCS-REPORT-GLOBALLY-INVARIANT-VARIANTS
  - PCS-DOC-NONFOUNDERS-COUPLING
  - PCS-SUMMARIZE-EXPLICIT-DENOMINATORS
  - PCS-PASTE-PLINK-PAIRWISE-COMPLETE-FALSIFIER
  - PCS-R6-OCC-MEASURE-ALLOWANCE-RECORDED
  - PCS-FROZEN-SURFACES-UNCHANGED
  - PCS-SUITE-REBASELINE

user_setup: []

must_haves:
  truths:
    - "F6 IS FIXED AND ENFORCED BY NAME: `BedReader.read_variant` computes its seek from the NORMALISED index, not the raw argument — `grep -c '3 + idx \\* self.bytes_per_variant' src/python/pairwise_completeness_scan.py` == 1 AND `grep -c '3 + index \\* self.bytes_per_variant' …` == 0. A test passes `\"1\"` (str) and `1.0` (integral float) and asserts the returned dosage array is `np.array_equal` to `read_variant(1)`; that test was SEEN RED against the shipped code (raw `index` makes `3 + \"1\"*18281` a TypeError). A companion test asserts a NON-integral index (`1.5`) RAISES rather than silently truncating to variant 1 — a silent truncation would be a wrong-genotype read with no error anywhere, the exact class the module's global-index rule exists to prevent."
    - "F4 IS FIXED IN THE UNDERCOUNT DIRECTION: `pair_key` is derived from the GLOBALLY-UNIQUE, order-normalised `.bim` ROW INDICES (`_pair_key(a, b) -> f\"{min}|{max}\"`), never from variant IDs — `grep -c \"sorted((deletion.vid, partner.vid))\" src/python/pairwise_completeness_scan.py` == 0. A fixture in which TWO DISTINCT partner rows both carry the id `.` next to one deletion (one pair undefined, one defined) reports `n_distinct_pairs == 2` and `n_undefined_distinct_pairs == 1`; it was SEEN RED against the vid key, which collapsed both to 1 and 1. The deletion-deletion neighbour still yields TWO ordered rows and ONE distinct pair key (the pre-existing test stays green), and a test asserts `sorted(int(x) for x in row.pair_key.split(\"|\")) == sorted([row.del_index, row.partner_index])` — a must-be-identity link between the key and the rows it names."
    - "F5 IS FIXED AT THE EXACT TIE AND THE TIE IS VISIBLE IN THE OUTPUT: at `af_a1 == 0.5` the carriers-lost gradient is computed for BOTH alleles and the member reports the LARGER `lost_frac` (ties broken by the larger `lost` count, then A1 — stated in the docstring), and two new boolean columns `del_minor_allele_tie` / `partner_minor_allele_tie` are emitted so the tie is never invisible. The pinning test is the tail-hiding case: 8 samples with A1 dosages `[2,2,2,2,0,0,0,0]` (af_a1 exactly 0.5) where 3 of the 4 A2-carriers are no-called at the partner — the OLD A1-on-tie rule reports `lost_frac == 0.0` (reassuring) and the new rule reports `0.75` with `minor_allele_tie == True`. Seen RED. For every `af_a1 != 0.5` case the numbers are UNCHANGED, proven by the pre-existing 00057-mirror / partial-confounding / zero-gradient / lost-frac-1.0 tests staying green with their original hand-computed values."
    - "F2 IS REPORTED, NOT CHANGED: the region's universe is still exactly the region's own matrix — no emitted row may reference a variant outside `[from_bp, to_bp]` (a test asserts `from_bp <= r.del_pos <= to_bp` AND `from_bp <= r.partner_pos <= to_bp` over every emitted row) — but the suppression is now COUNTED. `n_candidates_edge_clipped` is a `SUMMARY_KEYS` member and a fixture with an in-region edge deletion whose ±`window_bp` neighbourhood reaches a partner 1 bp beyond `to_bp` reports `n_candidates_edge_clipped == 1` with `n_candidate_rows` unchanged; a fixture with no edge-adjacent candidate reports 0. Seen RED (the key did not exist). The module docstring states that the universe is the region's matrix and not the genome, that a partner outside the region cannot produce a NaN in that region's matrix so the clipping is CORRECT, and that anchor-side clipping (a deletion outside the region) is out of scope because such a deletion is not a row of that matrix."
    - "THE `--mac 1` / RETAINED-SET PARITY GAP IS SEPARABLE INSTEAD OF SILENT: two new boolean columns `del_globally_invariant` / `partner_globally_invariant` (invariant within the member's OWN called set, the empty called set included) and two new summary keys `n_globally_invariant_variants` (distinct variant indices) and `n_undefined_rows_with_globally_invariant_member`. A fixture with an all-hom-ref partner reports both booleans/counters correctly AND `undefined == True`; a normal fixture reports 0/False. Seen RED. The docstring states the set relation in the correct direction — `{MAC 0} ⊆ {invariant within its own called set}` — and states that the production matrix is built on the RETAINED set (post-`--exclude`, post-`--mac 1`) while the scanner enumerates the full window `.bim`, so a globally invariant variant would OVER-report undefined pairs; these counters make that subtractable rather than a finding. It also states that the `--exclude` side is already visible via `already_occluded`."
    - "F1 IS A NAMED CROSS-MODULE ENFORCER, NOT PROSE: the module docstring states the coupling verbatim — this scanner's ALL-SAMPLES policy is valid ONLY because the production LD command passes `--nonfounders` (plink1.9 LD considers founders only by default); if that flag is ever dropped, the scanner must switch to founders-only or its verdicts become non-comparable. A test named `test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag` READS `src/python/aou_ld_panel.py` (read-only; the file is NOT modified), extracts `build_plink_ld_command`, asserts `\"--nonfounders\"` is present in its square branch, and asserts the scanner docstring names the coupling. It is a SYMBOL pin, never a fixed-SHA whole-file pin (`feedback_fixed_sha_whole_file_pin_is_a_timebomb`), and it was seen red against a scratch copy with the flag removed."
    - "F7 IS EXPLICIT-OR-RAISE, NOT A SILENT LIE: `summarize()` takes `n_deletions` and `n_candidates_edge_clipped` as REQUIRED keyword-only arguments with NO default, so `summarize(\"R\", [])` raises `TypeError` naming the missing argument instead of deriving `n_deletions=0` from an empty result list for a region that genuinely contains an isolated deletion. A test asserts the raise; the six existing call sites in the suite are updated to pass their own denominators explicitly (which also makes each of those tests state the denominator it is asserting against)."
    - "F3 — THE HIGHEST-VALUE ITEM — EXISTS AS A RUNNABLE, READ-ONLY, THREE-RUN DISCRIMINATOR IN THE PENDING PASTE, BEFORE THE 00057 CROSS-CHECK: a new STEP 1 that (a) SELECTS Z EMPIRICALLY — it scans variants near X with the module's own `BedReader`, prints a small retention table, names the chosen Z with its MEASURED carrier retention, and STOPS if no candidate clears the stated retention floor because the discriminator would have no power; (b) runs plink1.9 THREE times with the production LD modifiers `--keep-allele-order --mac 1 --nonfounders --write-snplist --r square bin4` on `{X,Y,Z}`, `{X,Z}` and `{X,Y}`; (c) READS `--write-snplist` FIRST to fix the row order before reshaping any `.ld.bin` (the matrix is in `.bim`/position order, so Z may be row 0); and (d) discriminates against a printed 3-hypothesis table. ⛔ Any pattern other than pairwise-complete means STOP, DISCARD THE SWEEP, REPORT — the instrument's premise is falsified and the approach needs rethinking before ANY number is generated. That consequence is written into the paste in those terms. The 2-variant `{X,Z}` run is what separates real listwise-over-the-window (NaN at 3 variants, FINITE at 2) from a merely mis-selected Z (NaN at both), so a false alarm cannot silently kill a valid sweep and a real falsification cannot be explained away."
    - "THE PASTE'S OWN 'no plink' CLAIM IS RETRACTED AND THE PLINK LANDMINE IS HANDLED: the two occurrences of 'This sweep calls no plink at all' are GONE (a negative-needle test asserts the string is absent), the `export PATH=\"$HOME/bin:$PATH\"` note is promoted from 'not on this sweep's critical path' to REQUIRED-FIRST-ACTION, STEP 0 gates on `plink1.9 --version` printing `v1.90b7.2` (never a PLINK 2.x shimmed as `plink1.9`), and the paste records that a browser agent's safety layer will correctly refuse the download-and-execute install so CARTER pastes that one command into the same tab (`reference_aou_vm_plink19_pinned_build`). STEP 0 also prints the `.fam` FOUNDER COUNT — `awk '$3==\"0\" && $4==\"0\" ' … | wc -l` against the total line count — so the paste RECORDS whether the founders/nonfounders distinction is even live in this cohort instead of assuming it."
    - "THE PASTE STILL CONTAINS THE 00057 CROSS-CHECK, AFTER THE FALSIFIER: a test asserts `text.index(\"<falsifier marker>\") < text.index(\"<00057 cross-check marker>\") < text.index(\"<sweep marker>\")`, and every pre-existing needle (`71048`, `871`, `20394741`, `20394743`, `occ_measure_sample.tsv`, `m2_region_00057`, `DISCARD ALL`, both PASTE markers) is still present. The steps are renumbered consistently (STEP 0 freshness+environment, STEP 1 falsifier, STEP 2 the 00057 cross-check, STEP 3 the 21-region sweep) with no orphaned 'do not skip STEP 1' reference to the wrong step."
    - "THE R6 CITATION GAP IS CLOSED BY AMENDING R6, NOT BY DELETING THE CITATION: `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md` R6 now names `/home/jupyter/occ_measure/`, dated, with a one-line provenance stating that this RECORDS an allowance already exercised with Carter's explicit go rather than granting a new one. A newline-tolerant enforcer test (`re.search(r\"R6's\\s+occ_measure/\", text)`) confirms all THREE runbooks still carry the citation, and a scoped block test (`^R6\\.` … `^R7\\.`) confirms R6 itself now contains `occ_measure` — `grep -c occ_measure` on that file was 0 before the change (measured) and the citation-vs-rule gap is what made three runbooks cite a rule that did not exist."
    - "THE R6 EDIT IS PROVEN NOT TO HAVE DISTURBED THE vbu-PINNED §6b CARD: `bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all` exits 0 and its stdout is BYTE-IDENTICAL before and after — 2070 bytes, md5 `83d60d91c6861c1f13ac728c059442ba` (both MEASURED at 19a5224 during planning), captured with the SAFE two-step file form and compared with `cmp`. This is sound because the verifier's card checks operate on the block delimited by `^STEP 6b` … `^STEP 7` (verified at `260817-vbu-verify.sh:183`) and report line numbers RELATIVE to that block, while R6 sits at line 32 — far above it — so an insertion there cannot shift a single reported number."
    - "NOTHING ON THE FIRE PATH OR THE PUBLIC RECORD MOVED, AT EVERY COMMIT: `git diff --stat e63b9af HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/` is EMPTY, and the posted amendment's marker-exclusive paste block is still 22945 B / md5 `13a49f543cabcc27ce9f1e589783c060` — computed with the SAFE TWO-STEP FILE FORM (awk into a file, then `wc -c` and `md5sum` on that file), NEVER `awk … | tee >(wc -c) | md5sum`, which deterministically prints the phantom `2f2e9548e1b2952ac802a847ea5dff40` on an unchanged file. `src/python/aou_ld_panel.py` is READ by the F1 enforcer and is likewise unchanged."
    - "NOTHING WAS FIRED: zero VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact; the PENDING PASTE is EXTENDED and still NOT RUN; the plink falsifier is WRITTEN and UNRUN; the scanner module still calls no plink itself. No prevalence, no boundary width and no partial-confounding tail number is asserted anywhere in any deliverable — all three stay OPEN, by design."
    - "THE SUITE IS RE-BASELINED HONESTLY AND COMPONENT-EXACT: `tests/m3` reports 0 FAILED at EVERY commit; the skip count STAYS at 33 (a new test landing as a SKIP is not evidence); and the SUMMARY reconciles from the measured baseline 1083 passed / 33 skipped / 0 failed / 1116 collected (re-measured at 19a5224 during planning: `--collect-only` = 1116 in 3.80 s) by naming every added test and showing `1083 + N == new_passed` AND `1116 + N == new_collected`. The corrected counts land in `.planning/HANDOFF.json` `suite_baselines[\"tests/m3\"]` — CORRECTED, never appended."
    - "THE BRANCH IS PUBLISHED AND THE SHARED TREE WAS NOT TRAMPLED: after the final task `git status -sb` shows no `ahead`; every commit staged EXPLICIT paths (never `git add .` / `-A` on the GPFS tree); and the pre-existing dirty entry `tests/m3/sparse_parent_benchmark.tsv` (modified before this plan started) and the untracked `.planning/debug/m3-producer-unbounded-dense-read.md` are LEFT EXACTLY AS FOUND."
  artifacts:
    - path: "src/python/pairwise_completeness_scan.py"
      provides: "The remediated instrument: normalised-index seek, index-based pair keys, the max-loss minor-allele tie rule with visible tie columns, the edge-clip counter, the globally-invariant counters, explicit-or-raise summary denominators, and the documented --nonfounders coupling"
      contains: "minor_allele_tie"
      min_lines: 1100
    - path: "tests/m3/test_pairwise_completeness_scan.py"
      provides: "The remediation tests, each seen RED first: str/float/non-integral index, the duplicate-ID pair-key collapse, the exact af_a1 == 0.5 tail-hiding tie, the edge-clip counter and the no-row-outside-bounds guard, the globally-invariant counters, the summarize explicit-or-raise, the cross-module --nonfounders enforcer, the falsifier-before-crosscheck ordering, the 'no plink at all' negative needle, and the newline-tolerant R6 citation enforcer"
      contains: "test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag"
      min_lines: 2000
    - path: ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md"
      provides: "STEP 0 freshness + pinned plink1.9 v1.90b7.2 gate + .fam founder count; STEP 1 the three-run plink pairwise-complete FALSIFIER with empirical Z selection, the snplist-first row-order rule and the discard-on-mismatch consequence; STEP 2 the 00057 cross-check; STEP 3 the 21-region sweep; aggregate-counts-only egress"
      contains: "pairwise-complete"
      min_lines: 200
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
      provides: "R6 amended to RECORD the /home/jupyter/occ_measure/ allowance that three runbooks already cite and that the earlier sweeps already exercised"
      contains: "occ_measure"
    - path: ".planning/HANDOFF.json"
      provides: "The corrected tests/m3 baseline and a resume entry naming the review as REMEDIATED, the falsifier as WRITTEN-AND-UNRUN, and the premise as UNCONFIRMED until it runs"
      contains: "pairwise_completeness_scan"
  key_links:
    - from: "BedReader.read_variant bounds check (`idx = int(index)`)"
      to: "the .bed seek offset"
      via: "the SAME normalised value feeds both — the bounds-checked quantity IS the addressed quantity"
      pattern: "3 \\+ idx \\* self\\.bytes_per_variant"
    - from: "the two globally-unique .bim row indices of a candidate pair"
      to: "pair_key (and therefore n_distinct_pairs / the undefined occlusion split)"
      via: "_pair_key(a, b) order-normalised on INDICES, with the vids kept only for display"
      pattern: "def _pair_key"
    - from: "src/python/aou_ld_panel.py::build_plink_ld_command (`--nonfounders` in the square branch)"
      to: "the scanner's all-samples policy"
      via: "a read-only cross-module SYMBOL enforcer test that fails if the flag is ever dropped — never a fixed-SHA whole-file pin"
      pattern: "--nonfounders"
    - from: "plink1.9's actual --r missingness semantics on the real cohort"
      to: "every number the 21-region sweep would produce"
      via: "the three-run STEP 1 falsifier — the 2-variant {X,Z} run separates listwise-over-the-window from a mis-selected Z; anything but pairwise-complete DISCARDS the sweep"
      pattern: "pairwise-complete"
    - from: "R6's file whitelist in 260812-ox1-AGENT-PROMPT.md"
      to: "the three PENDING-PASTE runbooks that cite 'R6's occ_measure/ allowance'"
      via: "a newline-tolerant citation enforcer plus a scoped ^R6.…^R7. block test — the rule and its citations now agree"
      pattern: "occ_measure"
---

<objective>
An external adversarial review (Codex) plus a three-dimension blast-radius sweep examined the
pairwise-completeness scanner built yesterday. **Nothing here blocks the committed code.
Everything here blocks TRUSTING THE NUMBERS the sweep will produce** — and those numbers are
headed for a public OSF pre-registration, where a wrong instrument yields a confidently wrong
prevalence.

Two kinds of work, and the second matters more than the first:

1. **Three real correctness defects** (a raw-vs-normalised seek index; a pair key that collapses
   distinct pairs when two rows share a variant ID — in the UNDERCOUNT direction; an exact
   allele-frequency tie that tracks the wrong allele and so reads the carrier-loss tail as
   reassuring), plus reporting for two silent couplings (region-edge clipping, `--mac 1`
   retained-set parity) and two documentation/API items (the `--nonfounders` coupling, the
   `summarize` denominator default).

2. **The experiment that tests the instrument's load-bearing assumption against real plink.**
   The whole scanner assumes plink1.9 `--r` correlates over PAIRWISE-COMPLETE observations. The
   evidence for that today is CIRCUMSTANTIAL — both marginals variable, diagonal 1.0, exactly one
   symmetric NaN pair. If plink instead mean-imputes, or drops samples missing at ANY variant in
   the window, the scanner measures the wrong thing and EVERY number is void. This plan writes a
   cheap, read-only, three-run discriminator into the runbook, placed BEFORE the 00057
   cross-check, with an explicit ⛔ DISCARD-AND-REPORT consequence.

The review's own severities are not adopted uncritically. Two were re-dispositioned after
independent verification of every cited line: its HIGH #2 (edge clipping) is CORRECT behaviour
whose defect is SILENCE, so it is COUNTED and DOCUMENTED, not changed; its HIGH #1 (founders) is a
COUPLING to a flag production already passes, so it is DOCUMENTED and given a named enforcer, not
changed. Downgrading a finding is only legitimate when it is written down with its reason, which
is what the docstring paragraphs and the enforcer test are for.

Purpose: make the instrument's numbers TRUSTWORTHY before any of them exist — and make the one
assumption that could void all of them FALSIFIABLE by a $0-to-write, minutes-to-run experiment.

Output: a remediated module + tests (every one seen RED first), an extended PENDING PASTE with the
falsifier, an amended R6 that records the allowance three runbooks already cite, a reconciled
suite baseline, and a pushed branch.

EXPLICITLY OUT OF SCOPE — any of these appearing is a plan violation:
  * ANY change to `occlusion_span_filter.py`, `run_native_ld_panel.py`, `fire_verifier.py`,
    `aou_ld_panel.py` (it is READ by the F1 enforcer, never written) or `.planning/amendments/`
  * ANY criterion, threshold, span-widening or NaN-policy change
  * ANY prevalence / boundary-width / partial-confounding-tail number stated as a result
  * RUNNING the paste or the falsifier; any VM / Dataproc / OSF / `gsutil` / `gcloud` contact
  * Changing the edge-CLIPPING behaviour (F2 is reported, not changed) or the scanner's
    all-samples policy (F1 is documented, not changed)

NO FIRE. $0. An agent never fires.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/quick/260825-qpf-remediate-the-adversarial-review-of-the-/CODEX-REVIEW-as-received.md
@src/python/pairwise_completeness_scan.py
@tests/m3/test_pairwise_completeness_scan.py
@.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
@.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md
@.planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-PLAN.md

<measured_facts>
<!-- Read-only measurements taken at HEAD 19a5224 during planning. Do not re-derive; DO re-verify. -->

PYTHON (never miniconda base):
  PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python

BASE SHA for every `git diff --stat` guard in this plan: e63b9af
HEAD at planning time: 19a5224   BRANCH: m3-W2-aou-deltas (tracking origin, NOT ahead)

PRE-EXISTING DIRT — LEAVE IT EXACTLY AS FOUND, never stage it:
  ` M tests/m3/sparse_parent_benchmark.tsv`  and several untracked paths incl.
  `.planning/debug/m3-producer-unbounded-dense-read.md`. Explicit-path staging only
  (`feedback_multi_terminal_staging`).

SUITE BASELINE (tests/m3): 1083 passed / 33 skipped / 0 failed; 1116 collected.
  Re-measured at 19a5224: `--collect-only -q` = 1116 collected in 3.80 s. Full run ~13-14 min.
  Use `-q -rs`. `pytest tests` AS ONE INVOCATION DOES NOT COLLECT (tests/m2/conftest.py shadows
  tests/m3/conftest.py) — run sub-suites separately. Skips must STAY at 33.

FROZEN-SURFACE GUARD (run at the START and END of every task):
  git diff --stat e63b9af HEAD -- \
    src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py \
    src/python/fire_verifier.py .planning/amendments/ | wc -l    # MUST be 0
  MEASURED 0 at 19a5224 during planning.

AMENDMENT PASTE-BLOCK GUARD — ⚠ USE THIS EXACT TWO-STEP FILE FORM:
  A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb.txt
  wc -c < /tmp/pb.txt      # MUST be 22945   (SIZE FIRST — 260817-vbu house order)
  md5sum /tmp/pb.txt       # MUST be 13a49f543cabcc27ce9f1e589783c060
  Both RE-MEASURED at 19a5224 during planning. ⚠ NEVER `awk … | tee >(wc -c) | md5sum` — process
  substitution interleaves into md5sum's stdin and deterministically prints the phantom
  2f2e9548e1b2952ac802a847ea5dff40 on an UNCHANGED file.

vbu ENFORCER BASELINE (for the R6 edit) — MEASURED at 19a5224:
  bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all
    exit 0 · stdout 2070 bytes · md5 83d60d91c6861c1f13ac728c059442ba
    last line: `RESULT: ALL CHECKS PASSED (section: all)`
  The output is path-free and deterministic (verified by inspection).
  WHY THE R6 EDIT IS SAFE: the verifier's card checks run over the block delimited by
  `^STEP 6b` … `^STEP 7` (`260817-vbu-verify.sh:183`, `AP` = the AGENT-PROMPT) and report line
  numbers RELATIVE TO THAT BLOCK (`V1 … 9,695 on block line 11`). R6 begins at AGENT-PROMPT
  line 32; STEP 6b begins near line 128. An insertion at 32 cannot shift a reported number.
  Capture BEFORE and AFTER to files and `cmp` them — never eyeball.

THE R6 CITATION GAP — MEASURED:
  `grep -c occ_measure .planning/quick/260812-ox1-…/260812-ox1-AGENT-PROMPT.md` == 0.
  R6 is a CLOSED whitelist at lines 32-45 enumerating /tmp/region1_only.tsv, /tmp/stageB.tsv,
  data/aou/region1_window.bim, /home/jupyter/native_ld_scratch/, /home/jupyter/native_ld_fire.log
  and the R8 gate artifacts. It never mentions occ_measure/.
  THREE runbooks cite it, ONE occurrence each (newline-tolerant count `tr '\n' ' ' | grep -o
  "R6's *occ_measure/" | wc -l` == 1 for each):
    .planning/debug/260819-PENDING-PASTE-2-samepos-and-chain.md   (WRAPS: `R6's` line 18 /
        `occ_measure/ allowance extends to these files.` line 19)
    .planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md    (line 13, same line)
    .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md (WRAPS: lines 25/26)
  A naive `grep "R6's occ_measure/"` finds only ONE of the three. Use the newline-tolerant form.

THE PRODUCTION plink LD COMMAND (src/python/aou_ld_panel.py:2895-2935 — READ ONLY, never edited):
  ["plink1.9", "--bfile", P, "--keep-allele-order", "--chr", C, "--from-bp", F, "--to-bp", T]
  + optional ["--exclude", EXCL]
  + square branch: ["--mac", "1", "--nonfounders", "--write-snplist", "--r", "square", "bin4"]
  + optional ["--threads", N] + ["--out", O]
  The in-code comment states `--nonfounders` "counts all samples (founders-only default is a
  no-op for an all-founder export, insurance)" — which is EXACTLY the coupling F1 must pin.

THE PINNED plink1.9 BUILD ON THE AoU VM (reference_aou_vm_plink19_pinned_build):
  The VM image ships only `plink`; the producer's argv names the literal `plink1.9`.
  Required build: PLINK v1.90b7.2 64-bit (11 Dec 2023), plink_linux_x86_64_20231211.zip,
  installed to ~/bin/plink1.9. `export PATH="$HOME/bin:$PATH"` is PER-SHELL and does not survive
  a new tab or a VM restart. NEVER shim a PLINK 2.x binary as plink1.9 (`--r square bin4`
  semantics differ). A browser agent's safety layer will correctly REFUSE the download-and-execute
  install — Carter pastes that one command into the same tab.

THE MEASURED 00057 CASE (halt record §MECHANISM CONFIRMED — CITE, never re-derive):
  X = chr15:20394741:AT:A  (ref_len 2 -> span_end 20394742), 871 carriers, marginal MAF 0.601%
  Y = chr15:20394743:T:C   (offset +1 past span_end)
  0 of 871 X-carriers are called at Y; n_both_called = 71048; X invariant there -> NaN.
  Cohort .fam total 73,122. Region 1 is the NaN-free negative control.

CURRENT SCHEMA (what the remediation extends):
  TSV_COLUMNS == PairResult._fields, 32 columns today (pinned by EXACT tuple equality at
  tests/m3/test_pairwise_completeness_scan.py:1323 — adding a column breaks it DELIBERATELY).
  SUMMARY_KEYS, 13 keys today (pinned at :1370).
  `_fake_result` (:1465) supplies defaults for every PairResult field and MUST gain the new ones.
  `summarize(...)` is called WITHOUT `n_deletions` at test lines 1385, 1394, 1422, 1539, 1570,
  1603 — all six become explicit under F7.
  `_minor_allele_carriers` / `_gradient` are PRIVATE and are called from NO test — they may be
  refactored freely. Nothing outside `tests/m3/test_pairwise_completeness_scan.py` imports the
  module (`grep -r pairwise_completeness_scan` over .py/.smk/Snakefile — MEASURED: 0 hits).
</measured_facts>

<interfaces>
<!-- The contracts the executor builds TO. No codebase exploration required. -->

AFTER THIS PLAN, the module's changed/new surface is EXACTLY:

```python
# --- F6 ---------------------------------------------------------------- #
def _as_variant_index(value) -> int:
    """Normalise a variant index. Accepts int / np.integer / a digit str / an
    INTEGRAL float. RAISES on a non-integral float (silent truncation would be a
    wrong-genotype read with no error) and on anything int() rejects."""

class BedReader:
    def read_variant(self, index) -> Genotypes:
        idx = _as_variant_index(index)
        ...
        offset = 3 + idx * self.bytes_per_variant     # <- idx, never `index`

# --- F4 ---------------------------------------------------------------- #
def _pair_key(index_a: int, index_b: int) -> str:
    """Order-normalised key over the two GLOBALLY-UNIQUE .bim row indices.
    Two rows that share a variant id (a bare `.` or a duplicated rsID) are
    DISTINCT pairs and must never collapse; the vids stay on the row for display."""
    lo, hi = sorted((int(index_a), int(index_b)))
    return f"{lo}|{hi}"

# --- F5 + the --mac 1 parity counter ------------------------------------ #
def _carrier_gradient(dosage, called, both) -> tuple:
    """(marginal, retained, lost, lost_frac, maf, minor_allele_tie, globally_invariant).

    REPLACES _minor_allele_carriers + _gradient (both private, both uncalled by
    any test). Behaviour for af_a1 != 0.5 is IDENTICAL to today.
      af_a1 = dosage[called].sum() / (2 * n_called)
      A1-carrier mask = (dosage >= 1) & called        # >= 1 copy of A1
      A2-carrier mask = (dosage >= 0) & (dosage <= 1) & called
      af_a1 <  0.5 -> A1 mask ; af_a1 >  0.5 -> A2 mask ; tie False
      af_a1 == 0.5 -> tie True; compute the gradient for BOTH masks and return the
                      one with the LARGER lost_frac (break by larger `lost`, then A1)
      n_called == 0 -> all-zero gradient, maf 0.0, tie False, globally_invariant True
      maf = min(af_a1, 1 - af_a1)
      globally_invariant = np.unique(dosage[called]).size <= 1   # incl. the empty called set
    """

# --- F2 ----------------------------------------------------------------- #
def iter_bim_windows(bim_path, windows, *, pad_bp: int = 0) -> dict:
    """pad_bp=0 is TODAY'S BEHAVIOUR EXACTLY. With pad_bp>0 the returned rows also
    include the [start-pad, end+pad] flanks, in ONE streaming pass, so the clipped
    candidates can be COUNTED. The 2-tuple (global_index, row) shape is UNCHANGED."""

def enumerate_candidates(region_id, indexed_rows, *, window_bp=DEFAULT_WINDOW_BP,
                         region_bounds: "tuple[int, int] | None" = None) -> list[CandidatePair]:
    """region_bounds=None -> today's behaviour. When given, a deletion anchors ONLY
    if start <= pos <= end, and a partner is EMITTED ONLY if start <= pos <= end.
    The emitted set is therefore IDENTICAL to the unpadded run."""

def count_edge_clipped_candidates(region_id, indexed_rows, *, window_bp,
                                  region_bounds: "tuple[int, int]") -> int:
    """Ordered candidate ROWS an IN-BOUNDS deletion's +/-window_bp reach would have
    produced but the region boundary suppressed (partner outside [start, end]).
    Anchor-side clipping is NOT counted — a deletion outside the region is not a row
    of that region's matrix, so no pair containing it exists there at all."""

def scan_region(reader, region_id, indexed_rows, *, window_bp=DEFAULT_WINDOW_BP,
                region_bounds=None) -> list[PairResult]:  # pass-through

# --- F7 ------------------------------------------------------------------ #
def summarize(region_id, results, *, window_bp=DEFAULT_WINDOW_BP,
              n_deletions: int,                 # REQUIRED keyword-only, NO default
              n_candidates_edge_clipped: int    # REQUIRED keyword-only, NO default
              ) -> dict:
```

TSV_COLUMNS gains FOUR columns, each immediately after its sibling (order matters —
the exact-tuple test must be updated to match):
  `del_invariant`, **`del_globally_invariant`**, `partner_invariant`,
  **`partner_globally_invariant`**, … `del_maf_marginal`, **`del_minor_allele_tie`**,
  … `partner_maf_marginal`, **`partner_minor_allele_tie`**, `confounding_pattern`

SUMMARY_KEYS gains THREE keys, appended in this order after `n_defined_lost_frac_ge_0p9`:
  `n_candidates_edge_clipped`, `n_globally_invariant_variants`,
  `n_undefined_rows_with_globally_invariant_member`

`main()` changes: `iter_bim_windows(..., pad_bp=args.window_bp)`; per window build
`region_bounds=(start_bp, end_bp)`; count `n_deletions` over IN-BOUNDS rows ONLY; call
`count_edge_clipped_candidates(...)`; pass both denominators to `summarize`.
</interfaces>
</context>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU VPC-SC perimeter → this repo / chat | Individual-level genotypes live in-perimeter; ONLY aggregate counts, fractions and variant coordinates may cross. The PENDING PASTE is the crossing protocol. |
| this repo → the public OSF record | Numbers produced by this instrument are destined for a pre-registration; a wrong instrument becomes a confidently wrong public claim, and posting is irreversible. |
| governance rule (R6) → the runbooks that cite it | A citation to a rule that does not say what is cited is an unenforceable permission; agents act on the citation. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-qpf-01 | Information disclosure | STEP 1 falsifier on the VM | mitigate | The falsifier uses ONLY `--r square bin4` (a 3x3 / 2x2 aggregate) and the module's own `BedReader`. It deliberately does NOT use `--recode A`, which would materialise an individual-level 73,122-row dosage file in-perimeter and would require widening R6's narrow deletion exception. Only the matrices, the snplist and counts are read; only counts cross back. |
| T-qpf-02 | Tampering (of the record) | the vbu-pinned §6b card in 260812-ox1-AGENT-PROMPT.md | mitigate | The R6 edit is at line 32, above the `^STEP 6b`…`^STEP 7` block the enforcer reads. Capture the enforcer's stdout to a file BEFORE and AFTER and `cmp` for byte identity (2070 B / 83d60d91c6861c1f13ac728c059442ba); a non-identical output is a STOP, not a re-baseline. |
| T-qpf-03 | Tampering (of the record) | the POSTED OSF amendment paste block | mitigate | Two-step file-form size+md5 guard (22945 B / 13a49f5…) at every task; the piped `tee >(wc -c)` form is banned by name because it prints a phantom hash on an unchanged file. |
| T-qpf-04 | Repudiation / false assurance | the scanner's pairwise-complete premise | mitigate | The premise is UNCONFIRMED and is now falsifiable: STEP 1's three-run discriminator with an explicit ⛔ DISCARD-AND-REPORT rule, placed BEFORE the cross-check and BEFORE the sweep, plus the 2-variant `{X,Z}` control that separates real listwise from a mis-selected Z. |
| T-qpf-05 | Elevation of privilege | R6's file whitelist | mitigate | R6 is amended to RECORD an allowance already exercised with Carter's go, dated and reasoned, scoped to `/home/jupyter/occ_measure/`. It grants no deletion right and no new directory. The falsifier is designed so no new deletion exception is needed (see T-qpf-01). |
| T-qpf-06 | Denial of service (of the sweep) | a mis-selected Z causing a false falsification | mitigate | Z is selected EMPIRICALLY with a printed retention table and a stated retention floor; if nothing clears the floor the paste STOPS rather than proceeding with a powerless discriminator; and the 2-variant `{X,Z}` run distinguishes a bad Z from real listwise. |
| T-qpf-07 | Spoofing (of the binary) | `plink1.9` on the VM | mitigate | STEP 0 gates on `plink1.9 --version` printing `v1.90b7.2`; a `which plink \|\| which plink1.9` style check is banned by name (it passed on the wrong binary twice). |
| T-qpf-08 | Information disclosure | the per-pair TSV | accept | Unchanged from the shipped design: the full TSV stays in-perimeter under `/home/jupyter/occ_measure/`; every emitted field is a scalar count/fraction/coordinate, pinned by the egress-clean tests and their negative control. |
</threat_model>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: The three correctness fixes — F6 normalised seek index, F4 index-based pair key, F5 the exact-tie max-loss rule (RED -> GREEN)</name>
  <files>src/python/pairwise_completeness_scan.py, tests/m3/test_pairwise_completeness_scan.py</files>
  <behavior>
    RED FIRST for every assertion, each red pasted verbatim in the SUMMARY. A green assertion that
    was never seen fail is not evidence (`feedback_green_assertion_needs_a_negative_control`).

    F6 — THE SEEK INDEX (`:281` validates `idx`, `:292` seeks with raw `index`).
      - `test_read_variant_accepts_a_coercible_index`: build a 3-variant fixture whose blocks are
        mutually distinguishable; assert `np.array_equal(r.read_variant("1").dosage,
        r.read_variant(1).dosage)` and the same for `1.0`. RED against the shipped code
        (`3 + "1" * 18281` is a str, `3 + <str>` is a TypeError; `3 + 1.0*bpv` is a float and
        `seek(float)` is a TypeError).
      - `test_read_variant_rejects_a_non_integral_index`: `read_variant(1.5)` RAISES. This is the
        one that matters — `int(1.5) == 1` would silently read the WRONG variant, which is the
        exact failure class the module's global-index rule exists to prevent. Name that reason in
        the test docstring.
      - `test_seek_offset_uses_the_normalised_index` — the NAMED ENFORCER
        (`feedback_a_claimed_invariant_needs_a_named_enforcer`): read the module source and assert
        `"3 + idx * self.bytes_per_variant" in src` AND
        `"3 + index * self.bytes_per_variant" not in src`. Textual, comment-insensitive on the
        SYMBOL, never a fixed-SHA whole-file pin.

    F4 — THE PAIR KEY (`:459` keys on sorted VIDS).
      - `test_duplicate_variant_ids_do_not_collapse_distinct_pairs`: one deletion plus TWO distinct
        partner rows BOTH carrying the id `.` (a real `.bim` occurrence), at different positions,
        one pair undefined and one defined. Assert `n_distinct_pairs == 2` and
        `n_undefined_distinct_pairs == 1`. RED against the vid key (which yields 1 and 1 — the
        UNDERCOUNT direction, which is the dangerous one).
      - `test_pair_key_names_the_rows_it_keys`: a must-be-identity link —
        `sorted(int(x) for x in row.pair_key.split("|")) == sorted([row.del_index,
        row.partner_index])` over every emitted row of a multi-pair fixture.
      - The pre-existing `test_deletion_deletion_neighbour_emits_two_rows_one_pair_key` MUST stay
        green: two ordered rows, ONE distinct key (sorted indices are identical from either
        anchor). Re-run it explicitly and say so.

    F5 — THE EXACT af_a1 == 0.5 TIE (`:562` `if af_a1 <= 0.5` tracks A1).
      - `test_exact_allele_frequency_tie_reports_the_larger_carrier_loss`: THE TAIL-HIDING CASE.
        8 samples; deletion A1 dosages `[2,2,2,2,0,0,0,0]` -> `af_a1 = 8/(2*8) = 0.5` EXACTLY (an
        exactly-representable float — assert `af` is exactly 0.5 in the fixture comment, do not
        rely on luck). Partner is no-called at 3 of the 4 A2-carriers and called everywhere else,
        and is variable within the intersection so the PAIR STAYS DEFINED. Then:
          A1-carriers = 4, lost 0 -> lost_frac 0.0   (the OLD rule: reassuring)
          A2-carriers = 4, lost 3 -> lost_frac 0.75  (the NEW rule: the tail)
        Assert `del_carriers_lost == 3`, `del_carriers_lost_frac == 0.75`,
        `del_minor_allele_tie is True`, `undefined is False`, and that `summarize` bins this row
        into `(0.5,0.9]` rather than `0`. RED against the shipped rule (which reports 0.0 and has
        no tie column at all).
      - `test_no_tie_flag_when_the_minor_allele_is_unambiguous`: an ordinary fixture reports
        `del_minor_allele_tie is False` / `partner_minor_allele_tie is False`.
      - REGRESSION, must-be-identity: the four pre-existing genotype tests
        (`…MIRRORS_A_MEASURED_CASE`, `…partial_confounding_is_DEFINED…`,
        `…fully_defined_pair_has_zero_gradient`, `…lost_frac_one_implies_undefined`) keep their
        ORIGINAL hand-computed numbers unchanged. If any of them moves, the refactor changed
        non-tie behaviour and the task is wrong.

    SCHEMA: `del_minor_allele_tie` goes immediately after `del_maf_marginal`;
    `partner_minor_allele_tie` immediately after `partner_maf_marginal`. Update
    `test_tsv_columns_exact_tuple_equality` (it breaks DELIBERATELY) and `_fake_result`'s defaults
    (both new fields default `False`). `TSV_COLUMNS == PairResult._fields` must still hold.
  </behavior>
  <action>
Guard FIRST: run the FROZEN-SURFACE guard and the AMENDMENT PASTE-BLOCK guard (two-step file
form, SIZE then md5) from `<measured_facts>`. Abort if either moves.

1. Write the F6/F4/F5 tests listed in `<behavior>` into
   `tests/m3/test_pairwise_completeness_scan.py`, following the file's existing conventions
   (module imported INSIDE each test body; `_write_bfile` / `_joint_table_bfile` /
   `_single_pair_result` / `_fake_result` reused, not re-invented). Run ONLY the new tests and
   PASTE EVERY RED. Do not touch the module yet.

2. Implement in `src/python/pairwise_completeness_scan.py`, per `<interfaces>`:
   * `_as_variant_index(value)` + `offset = 3 + idx * self.bytes_per_variant`.
   * `_pair_key(index_a, index_b)`; `enumerate_candidates` calls
     `pair_key=_pair_key(deletion.index, partner.index)`. Add a one-line comment naming WHY
     (two rows sharing a `.` id are distinct pairs; keying on vids UNDERCOUNTS).
   * `_carrier_gradient(dosage, called, both)` REPLACING `_minor_allele_carriers` and `_gradient`
     (delete both — they are private and no test calls them; MEASURED). Its docstring states the
     tie rule and its tie-break order in full. `evaluate_pair` calls it once per member and fills
     the two new tie columns. (`globally_invariant` is returned now but is CONSUMED in Task 2 —
     wire the field through `PairResult` in Task 2, not here, so each task's schema change is
     one reviewable step. If that is awkward, wiring all four columns in Task 1 is acceptable
     PROVIDED Task 1's exact-tuple test lists all four and Task 2 adds only summary keys.)
   * Docstring: add one short paragraph under a new heading `THE MINOR-ALLELE TIE RULE` stating
     the exact-tie max-loss rule and WHY (at a tie, tracking A1 by fiat can report a depleted-A2
     member as unaffected — precisely the partial-confounding tail this instrument exists to find).

3. Re-run the new tests — GREEN. Then run the perturbation negative controls ONE AT A TIME in a
   `tmp_path` scratch COPY of the module, never in-tree: (a) revert the seek to `index`;
   (b) revert `pair_key` to the vid form; (c) revert the tie to `af_a1 <= 0.5`. Paste each
   observed red. ⚠ Between perturbation and revert use a FRESH INTERPRETER or
   `importlib.invalidate_caches()` — a byte-length-identical edit reverted within the same second
   runs STALE bytecode (`feedback_negative_control_defeated_by_bytecode_cache`).

4. Run the whole file plus its neighbour:
   `$PY -m pytest tests/m3/test_pairwise_completeness_scan.py tests/m3/test_occlusion_span_filter.py -q`.
   Re-run both guards. Commit EXPLICIT paths only:
   `git add src/python/pairwise_completeness_scan.py tests/m3/test_pairwise_completeness_scan.py`
   Message: `fix(quick-260825-qpf): T1 — normalised seek index (F6), index-based pair keys (F4), max-loss minor-allele tie rule + visible tie columns (F5)`
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pairwise_completeness_scan.py tests/m3/test_occlusion_span_filter.py -q 2>&1 | tail -3 | grep -qE '[0-9]+ failed' && { echo T1-SUITE-FAIL; exit 1; }; grep -q '3 + idx \* self.bytes_per_variant' src/python/pairwise_completeness_scan.py && ! grep -q '3 + index \* self.bytes_per_variant' src/python/pairwise_completeness_scan.py && grep -q 'def _pair_key' src/python/pairwise_completeness_scan.py && ! grep -q 'sorted((deletion.vid, partner.vid))' src/python/pairwise_completeness_scan.py && grep -q 'minor_allele_tie' src/python/pairwise_completeness_scan.py && test "$(git diff --stat e63b9af HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/ | wc -l)" = 0 && A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md && awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb_qpf_t1.txt && test "$(wc -c < /tmp/pb_qpf_t1.txt)" = 22945 && md5sum /tmp/pb_qpf_t1.txt | grep -q 13a49f543cabcc27ce9f1e589783c060 && echo T1-VERIFY-OK</automated>
  </verify>
  <done>The seek uses the bounds-checked index (a str/integral-float index now reads correctly; a
non-integral one RAISES); `pair_key` is index-based and a duplicate-`.`-id fixture reports 2
distinct pairs where the shipped code reported 1; the exact `af_a1 == 0.5` tie reports the LARGER
carrier loss with a visible `minor_allele_tie` column, seen red on the tail-hiding fixture; every
non-tie number in the four pre-existing genotype tests is UNCHANGED; three in-scratch perturbation
reds are pasted; frozen surfaces and the amendment paste block are byte-unchanged; one
explicit-path commit; the file's tests are 0 failed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Make the two silent couplings visible — F2 edge-clip counter, the --mac 1 globally-invariant counters, F1 the --nonfounders enforcer, F7 explicit denominators (RED -> GREEN)</name>
  <files>src/python/pairwise_completeness_scan.py, tests/m3/test_pairwise_completeness_scan.py</files>
  <behavior>
    RED FIRST for every assertion. NOTHING in this task changes what the scanner DECIDES — it
    changes what the scanner REPORTS. Two of the review's findings are deliberately re-dispositioned
    here, and the docstring must say so in its own words.

    F2 — EDGE CLIPPING IS COUNTED, NOT CHANGED.
      Behaviour-preservation guard FIRST:
      - `test_no_emitted_row_references_a_variant_outside_the_region`: over every row of a
        multi-pair CLI fixture, `from_bp <= del_pos <= to_bp` AND `from_bp <= partner_pos <= to_bp`.
        This is the assertion that proves the `pad_bp` read did not leak an out-of-region pair into
        the output. Seen red by temporarily emitting padded partners in a scratch copy.
      Then the counter:
      - `test_edge_clipped_candidates_are_counted_not_silently_absent`: a region `[start, end]` with
        a deletion near `end` whose `±window_bp` reach includes a partner at `end + 1`. Assert
        `n_candidates_edge_clipped == 1`, that NO row names that partner, and that
        `n_candidate_rows` equals the hand-counted in-region value. RED (the key does not exist ->
        `KeyError` / `SUMMARY_KEYS` mismatch).
      - `test_no_edge_clipping_reports_zero`: an interior-only fixture reports 0.
      - The pre-existing `test_iter_bim_windows_one_pass_global_indices` (default `pad_bp=0`) and
        `test_cli_multi_region_one_bim_pass` (the `.bim` is opened EXACTLY ONCE) must both stay
        green — padding must not cost a second pass. Re-run them explicitly and say so.

    THE `--mac 1` / RETAINED-SET PARITY COUNTER.
      - `test_globally_invariant_variant_is_reported_separately`: a partner that is all-hom-ref
        across its whole called set. Assert `partner_globally_invariant is True`,
        `undefined is True`, `n_globally_invariant_variants == 1`, and
        `n_undefined_rows_with_globally_invariant_member == 1`. RED.
      - `test_ordinary_variants_are_not_globally_invariant`: 0 / False on a normal fixture.
      - Rationale to encode in the docstring, in the CORRECT set direction:
        `{MAC 0} ⊆ {invariant within its own called set}` (a MAC-0 variant is necessarily invariant
        among its called samples; the converse is false — an all-het variant is invariant here but
        has MAC == n_called). The production matrix is built on the RETAINED set (post-`--exclude`,
        post-`--mac 1`) while the scanner enumerates the full window `.bim`, so a globally invariant
        variant makes EVERY pair containing it read as undefined — an OVER-report, not a finding.
        Both observed regions reported `n_dropped_monomorphic = 0`, but that is a measurement of two
        regions and not a guarantee, so the class is COUNTED and SUBTRACTABLE instead of folded in.
        The `--exclude` side is already visible via `already_occluded`.

    F1 — THE `--nonfounders` COUPLING, WITH A NAMED CROSS-MODULE ENFORCER.
      - `test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag`: READ
        `src/python/aou_ld_panel.py` (READ-ONLY — the file is NEVER written by this plan), slice
        out `build_plink_ld_command`, assert `"--nonfounders"` occurs in its square branch, and
        assert the scanner's `__doc__` contains the coupling sentence. A SYMBOL pin, never a
        fixed-SHA whole-file pin (`feedback_fixed_sha_whole_file_pin_is_a_timebomb`). Seen red
        against a `tmp_path` scratch copy of `aou_ld_panel.py` with the flag deleted.
      - Docstring heading `SAMPLE POLICY — A COUPLING, NOT AN ASSUMPTION`: this scanner counts ALL
        `.fam` rows and evaluates every sample; plink1.9 LD considers FOUNDERS ONLY by default; the
        production square command passes `--nonfounders`, so all-samples is the MATCHING policy;
        **if `--nonfounders` is ever dropped from that command, this scanner must switch to
        founders-only or its verdicts become non-comparable**; the enforcer test is named inline.

    F7 — EXPLICIT-OR-RAISE DENOMINATORS.
      - `summarize` takes `n_deletions` and `n_candidates_edge_clipped` as REQUIRED keyword-only
        args with NO default. `test_summarize_requires_its_denominators`: `summarize("R", [])`
        raises `TypeError` naming the missing argument. Seen red (today it returns
        `n_deletions=0`, which is a LIE for a region holding an isolated deletion with no
        candidate partners). Update the six existing call sites (test lines 1385, 1394, 1422,
        1539, 1570, 1603) to pass their own denominators explicitly. Docstring states the reason.

    SCHEMA: `del_globally_invariant` immediately after `del_invariant`;
    `partner_globally_invariant` immediately after `partner_invariant` (unless Task 1 already
    wired them — then only the summary keys move here). Append to `SUMMARY_KEYS`, in this order:
    `n_candidates_edge_clipped`, `n_globally_invariant_variants`,
    `n_undefined_rows_with_globally_invariant_member`. Update
    `test_tsv_columns_exact_tuple_equality`, `test_summary_keys_exact_equality`, `_fake_result`.
    The egress pins must still pass: no new name contains `sample`/`iid`/`fid`, no new key names a
    rate or prevalence, every new field is a bool or an int (rendered width « 64).
  </behavior>
  <action>
Guard FIRST (frozen surfaces + amendment paste block, two-step file form).

1. Write every test in `<behavior>` FIRST. Run them and PASTE EVERY RED, including the two
   scratch-copy negative controls (the padded-partner leak; the `aou_ld_panel.py` copy with
   `--nonfounders` removed). Both scratch copies live in `tmp_path`, NEVER in-tree.

2. Implement per `<interfaces>`:
   * `iter_bim_windows(..., pad_bp=0)` — one streaming pass, unchanged 2-tuple shape.
   * `enumerate_candidates(..., region_bounds=None)` — in-bounds anchors, in-bounds partners.
   * `count_edge_clipped_candidates(...)` — the ordered-row count, partner-side only.
   * `scan_region(..., region_bounds=None)` pass-through.
   * `PairResult` / `TSV_COLUMNS` gain the two `*_globally_invariant` booleans (if not already
     wired in Task 1); `evaluate_pair` fills them from `_carrier_gradient`.
   * `summarize(...)` gains the three keys and the two REQUIRED keyword-only denominators.
   * `main()` — `pad_bp=args.window_bp`; per-window `region_bounds`; `n_deletions` counted over
     IN-BOUNDS rows ONLY (with padding it would otherwise silently inflate); the edge-clip count
     computed and passed through. The stdout scalar table picks up the three new keys
     automatically via `SUMMARY_KEYS` — confirm they appear and are not histograms/bins.
   * Docstring: add `REGION EDGES — CLIPPED BY DESIGN, COUNTED SO IT IS NEVER SILENT`,
     `RETAINED-SET PARITY (--exclude / --mac 1)` and `SAMPLE POLICY — A COUPLING, NOT AN
     ASSUMPTION`, each in the terms given in `<behavior>`. Under the first, state plainly that a
     variant outside the region is not in that region's LD matrix and cannot produce a NaN there,
     so the clipping is CORRECT and only the SILENCE was the defect — and that anchor-side
     clipping is out of scope for the same reason.

3. GREEN. Re-run the pre-existing one-pass tests explicitly and report them.

4. Full file + neighbour run; re-run both guards; commit EXPLICIT paths:
   `git add src/python/pairwise_completeness_scan.py tests/m3/test_pairwise_completeness_scan.py`
   Message: `feat(quick-260825-qpf): T2 — count the region-edge clipping (F2) and the globally-invariant/--mac-1 parity class, pin the --nonfounders coupling (F1), require the summary denominators (F7)`
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pairwise_completeness_scan.py tests/m3/test_occlusion_span_filter.py -q 2>&1 | tail -3 | grep -qE '[0-9]+ failed' && { echo T2-SUITE-FAIL; exit 1; }; $PY -c "import sys; sys.path.insert(0,'src/python'); import pairwise_completeness_scan as p; ks=p.SUMMARY_KEYS; assert 'n_candidates_edge_clipped' in ks and 'n_globally_invariant_variants' in ks and 'n_undefined_rows_with_globally_invariant_member' in ks, ks; assert p.TSV_COLUMNS == p.PairResult._fields; assert 'del_globally_invariant' in p.TSV_COLUMNS and 'partner_globally_invariant' in p.TSV_COLUMNS; assert 'nonfounders' in p.__doc__; import inspect; s=inspect.signature(p.summarize); assert s.parameters['n_deletions'].default is inspect.Parameter.empty; assert s.parameters['n_candidates_edge_clipped'].default is inspect.Parameter.empty; print('T2-SURFACE-OK')" && test "$(git diff --stat e63b9af HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/ | wc -l)" = 0 && A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md && awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb_qpf_t2.txt && test "$(wc -c < /tmp/pb_qpf_t2.txt)" = 22945 && md5sum /tmp/pb_qpf_t2.txt | grep -q 13a49f543cabcc27ce9f1e589783c060 && echo T2-VERIFY-OK</automated>
  </verify>
  <done>`n_candidates_edge_clipped`, `n_globally_invariant_variants` and
`n_undefined_rows_with_globally_invariant_member` are `SUMMARY_KEYS` members exercised by tests seen
red; no emitted row references a variant outside the region bounds and the `.bim` is still read in
ONE pass; `del_globally_invariant`/`partner_globally_invariant` are emitted columns;
`summarize` RAISES when a denominator is omitted and all six existing call sites are explicit; the
module docstring carries the edge-clip, retained-set-parity and `--nonfounders` paragraphs; the
cross-module enforcer test passes and was seen red against a scratch copy with the flag removed;
`aou_ld_panel.py` is UNCHANGED; one explicit-path commit; 0 failed.</done>
</task>

<task type="auto">
  <name>Task 3: F3 — the plink pairwise-complete FALSIFIER in the PENDING PASTE (+ the pinned-plink gate and the .fam founder count), and the R6 amendment with its vbu byte-identity check</name>
  <files>.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md, .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md, tests/m3/test_pairwise_completeness_scan.py</files>
  <action>
⚠ CAPTURE THE vbu BASELINE BEFORE TOUCHING THE ox1 FILE:
```
V=.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh
bash "$V" all > /tmp/vbu_qpf_before.txt 2>&1; echo "exit=$?"
wc -c < /tmp/vbu_qpf_before.txt      # expect 2070
md5sum /tmp/vbu_qpf_before.txt       # expect 83d60d91c6861c1f13ac728c059442ba
```
Then the frozen-surface + amendment guards. Abort if any moves.

1. TESTS FIRST (RED), appended to `tests/m3/test_pairwise_completeness_scan.py`:
   * extend `test_pending_paste_exists_and_carries_the_harness_crosscheck`'s needle list with the
     falsifier tokens: `pairwise-complete`, `mean-imputation`, `listwise`, `--write-snplist`,
     `--mac 1`, `--nonfounders`, `--keep-allele-order`, `plink1.9 --version`, `v1.90b7.2`,
     `DISCARD THE SWEEP`, `founder`.
   * `test_pending_paste_runs_the_falsifier_before_the_crosscheck_and_the_sweep`: assert
     `text.index(<falsifier step heading>) < text.index(<00057 cross-check heading>) <
     text.index(<sweep heading>)`, and that all pre-existing needles (`71048`, `871`, `20394741`,
     `20394743`, `occ_measure_sample.tsv`, `m2_region_00057`, `DISCARD ALL`, both PASTE markers)
     survive.
   * `test_pending_paste_no_longer_claims_it_calls_no_plink` — the NEGATIVE needle:
     `"calls no plink at all" not in text` (it currently appears TWICE — MEASURED).
   * `test_r6_records_the_occ_measure_allowance_and_all_three_runbooks_cite_it`: for each of the
     three runbooks, `re.search(r"R6's\s+occ_measure/", text)` is truthy (NEWLINE-TOLERANT — a
     naive one-line grep finds only ONE of the three, MEASURED); and on
     `260812-ox1-AGENT-PROMPT.md`, slice the block from `^R6\.` to `^R7\.` and assert
     `"occ_measure" in block`. Scope the assertion to the R6 BLOCK, not the whole file
     (`feedback_scope_a_guard_to_the_property_not_a_proxy`). PASTE THE RED — `grep -c occ_measure`
     on that file is 0 today.

2. REWRITE `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`, keeping the
   `260819-PENDING-PASTE-3` house style and the `--- PASTE FROM HERE ---` / `--- PASTE ENDS HERE ---`
   markers. New step order, renumbered consistently (no orphaned "do not skip STEP 1" pointing at
   the wrong step):

   **STEP 0 — FRESHNESS + ENVIRONMENT.** Keep the existing `git fetch / checkout / pull --ff-only /
   log -1 --oneline / ls -l` block and the NCSU-must-be-pushed warning; the STEP 0 SHA check must
   now expect a `quick-260825-qpf` commit. ADD:
     * `export PATH="$HOME/bin:$PATH"` promoted to REQUIRED FIRST ACTION in every new shell
       (per-shell, does not survive a tab or a restart), then `which plink1.9` and
       `plink1.9 --version` — MUST print `PLINK v1.90b7.2 64-bit (11 Dec 2023)`. Any other version,
       or a PLINK 2.x binary shimmed as `plink1.9`, is a STOP. State that a
       `which plink || which plink1.9` style check is WRONG (it passed on the wrong binary twice).
       State that the download-and-execute install will be refused by a browser agent's safety
       layer, correctly, and that CARTER pastes that one command into the same tab; include the
       pinned one-liner from `<measured_facts>` for him to paste.
     * the `.fam` FOUNDER COUNT (this is F1's field record, not a decision):
       ```
       wc -l < /home/jupyter/afr_cohort.fam
       awk '$3=="0" && $4=="0"' /home/jupyter/afr_cohort.fam | wc -l
       ```
       with one line of prose: plink1.9 LD considers founders only BY DEFAULT and the production
       command passes `--nonfounders`; these two numbers RECORD whether the distinction is even
       live in this cohort. If they are equal, the distinction is a no-op here. Do NOT state an
       expected value; report whatever they say.
     * `df -h /home/jupyter` (kept from the current OPERATIONAL NOTES).

   **STEP 1 — THE plink PAIRWISE-COMPLETE FALSIFIER (new; the highest-value step in this file).**
   Open with the stakes, in the paste itself: the scanner assumes plink1.9 `--r` correlates over
   PAIRWISE-COMPLETE observations (samples non-missing at BOTH variants). The evidence today is
   circumstantial. If plink mean-imputes, or drops samples missing at ANY variant in the window,
   the scanner measures the wrong thing and every number the sweep would produce is VOID. This
   step is read-only, costs three tiny plink runs, and decides it.

   * **1a — SELECT Z EMPIRICALLY (do not assume one).** A short python block that imports
     `BedReader` / `iter_bim_windows` from `src/python/pairwise_completeness_scan.py`, takes
     X = `chr15:20394741:AT:A` and Y = `chr15:20394743:T:C`, walks the variants within ±200 bp of
     X, and for each candidate C prints `vid`, `pos`, `n_called`, and
     `retention = |carriers(X) ∩ called(C)| / |carriers(X)|`. Print the whole small table, then
     choose Z = the candidate with the HIGHEST retention, excluding X and Y. **STATE THE FLOOR:**
     if the best retention is below 0.80, STOP and report — the discriminator has no power without
     a Z at which X's carriers are largely called, and running it anyway would manufacture a false
     falsification. Print the chosen Z's vid and its MEASURED retention; every later step quotes
     that number.
     One line of honesty in the paste: 1a uses the instrument's own decoder, so a decoder bug
     could mis-select Z — that failure mode is FAIL-SAFE (it produces a false STOP, never false
     confidence) and step 1c's 2-variant control distinguishes it from a real falsification.

   * **1b — THREE plink RUNS, production LD modifiers.** Write the three ids to
     `/home/jupyter/occ_measure/falsifier_xyz.txt` and use `--extract` rather than `--snps`
     (the ids contain colons and `--snps` parses `-` as a range separator; production itself
     selects variants from a FILE via `--exclude`, and variant SELECTION is not correlation
     SEMANTICS). For each of `{X,Y,Z}`, `{X,Z}`, `{X,Y}`:
     ```
     plink1.9 --bfile /home/jupyter/afr_cohort --extract <ids> \
       --keep-allele-order --mac 1 --nonfounders --write-snplist \
       --r square bin4 --out /home/jupyter/occ_measure/falsifier_<tag>
     ```
     **State the modifier decisions and WHY, in the paste:**
       - `--keep-allele-order`, `--nonfounders`, `--r square bin4` — the production semantics;
         these are the point of the experiment.
       - `--mac 1` — INCLUDED. It is a variant-DROP filter, not a correlation-semantics change,
         and all three variants are polymorphic cohort-wide, so it must be a no-op here. It is
         included precisely so the command is production-shaped; the `.snplist` line count is what
         PROVES it was a no-op (3 lines / 2 lines). If a run's `.snplist` is short, STOP: a
         dropped variant means the matrix is not the shape assumed and the read would be
         mis-indexed.
       - `--exclude` (the occlusion manifest) — OMITTED, and why: it removes variants, which
         changes which pairs EXIST, not how `r` is computed over a pair that does exist. The
         falsifier tests the computation.
       - `--chr/--from-bp/--to-bp` replaced by `--extract` — same reasoning.
     ⚠ **READ THE `.snplist` FIRST, ALWAYS.** The `.ld.bin` rows are in `.bim`/position order, so
     if Z sits before X on the chromosome, Z is ROW 0. Assert the snplist length and derive the
     row index of each id FROM IT before reshaping anything. Assert the `.ld.bin` byte size is
     exactly `k*k*4` (36 for k=3, 16 for k=2) before `np.fromfile(..., dtype='<f4')`.
     ⚠ Do NOT import `read_square_bin` from `src/python/run_native_ld_panel.py` — it RAISES on NaN
     by design and NaN is the SIGNAL here. Use a plain `np.fromfile` in the paste.

   * **1c — DISCRIMINATE.** Print the matrices with the ids labelled, then this table verbatim:

     | hypothesis | 3-var (X,Y) | 3-var (X,Z) | 3-var (Y,Z) | 2-var (X,Z) | 2-var (X,Y) |
     |---|---|---|---|---|---|
     | **pairwise-complete** (assumed) | NaN | finite | finite | finite | NaN |
     | **mean-imputation** | finite | finite | finite | finite | finite |
     | **listwise over the window** | NaN | **NaN** | finite | **finite** | NaN |
     | **Z mis-selected** (X invariant in X∩Z) | NaN | **NaN** | finite | **NaN** | NaN |

     The bolded 2-var `{X,Z}` cell is the DISCRIMINATOR: real listwise makes `(X,Z)` NaN at three
     variants and FINITE at two (the window shrank); a bad Z makes it NaN at both. Say that in the
     paste so a false alarm cannot kill a valid sweep and a real falsification cannot be explained
     away. Also assert the diagonal is 1.0 in every run and note that any OTHER pattern is
     unclassified and is itself a STOP.

   * **1d — THE CONSEQUENCE, explicit.** ⛔ If the observed pattern is anything other than
     pairwise-complete: **STOP. Paste everything verbatim. DISCARD THE SWEEP. Do NOT run STEP 2 or
     STEP 3.** The instrument's premise is falsified and the whole approach needs rethinking before
     any number is generated. Do not adjust the code, the window or the expectations to make it
     pass. EGRESS from STEP 1: the two/three matrices (9 + 4 + 4 floats), the snplist line counts,
     the chosen Z and its retention — counts and coordinates only.

   **STEP 2 — THE 00057 HARNESS CROSS-CHECK.** The EXISTING step, moved down and renumbered,
   otherwise UNCHANGED (same command, same `71048` / `871` / offset `+1` / `already_occluded False`
   / `invariant_member deletion` assertions, same "DISCARD ALL RESULTS" rule). Add one lead-in
   line: it runs only after STEP 1 prints the pairwise-complete verdict.

   **STEP 3 — THE 21-REGION SWEEP.** The existing step, renumbered, gated on STEP 2 passing.

   **EGRESS RULE / OPERATIONAL NOTES / WHAT THIS DOES NOT DECIDE** — keep, with these edits:
     * DELETE both occurrences of "This sweep calls no plink at all" (header line and the PATH
       bullet). Replace with: this sweep's STEP 1 calls plink1.9 three times on 2-3 variants;
       STEPS 2-3 call no plink. The PATH export is therefore ON the critical path.
     * Keep the R6 citation (it becomes TRUE this task) and extend it to name the falsifier's
       working files under `/home/jupyter/occ_measure/`.
     * Keep the "no prevalence / no boundary width / no tail" language and the
       adjudication-is-separate paragraph verbatim.
     * Update the front-matter Status line: WRITTEN AND NOT RUN, now including the falsifier.

3. AMEND R6 in `.planning/quick/260812-ox1-…/260812-ox1-AGENT-PROMPT.md` (line ~32-45), inside the
   R6 paragraph, BEFORE the `ONE NARROW DELETION EXCEPTION` sentence. Keep R6's closed-whitelist
   character. Add, in R6's own voice and indentation:
     * `/home/jupyter/occ_measure/` and the measurement-sweep outputs written inside it
       (the row-basis, site-basis and pairwise-completeness sweep TSV/JSON files and the small
       plink working files of the pairwise-complete falsifier).
     * A dated provenance clause: `(added 2026-08-25, quick-260825-qpf: this RECORDS an allowance
       already exercised with Carter's explicit go from 2026-08-19 onward — three runbooks cite
       "R6's occ_measure/ allowance" and R6 did not say it. It grants no new directory and no new
       deletion right.)`
   Do NOT touch the `ONE NARROW DELETION EXCEPTION`, R7, R8, or anything at or below `STEP 6b`.
   The falsifier is deliberately designed to create no individual-level file, so no deletion right
   is needed (see `<threat_model>` T-qpf-01/T-qpf-05).

4. THE vbu BYTE-IDENTITY CHECK (the whole reason the R6 edit is safe):
```
bash "$V" all > /tmp/vbu_qpf_after.txt 2>&1; echo "exit=$?"
cmp /tmp/vbu_qpf_before.txt /tmp/vbu_qpf_after.txt && echo VBU-BYTE-IDENTICAL
wc -c < /tmp/vbu_qpf_after.txt; md5sum /tmp/vbu_qpf_after.txt
```
   Exit 0, `cmp` silent, 2070 B, md5 `83d60d91c6861c1f13ac728c059442ba`. A difference is a STOP and
   a revert — NEVER a re-baseline.

5. GREEN on the new tests. Re-run guards. Commit EXPLICIT paths:
   `git add .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md tests/m3/test_pairwise_completeness_scan.py`
   Message: `feat(quick-260825-qpf): T3 — the plink pairwise-complete FALSIFIER as STEP 1 of the sweep runbook (discard-on-mismatch), the pinned-plink1.9 gate + .fam founder count, and R6 amended to record the occ_measure/ allowance three runbooks already cite`
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; V=.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh; $PY -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3 | grep -qE '[0-9]+ failed' && { echo T3-SUITE-FAIL; exit 1; }; P=.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md; O=.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md; ! grep -q 'calls no plink at all' "$P" && grep -q 'v1.90b7.2' "$P" && grep -q 'write-snplist' "$P" && grep -q 'mean-imputation' "$P" && grep -q 'listwise' "$P" && grep -q '71048' "$P" && grep -q 'DISCARD ALL' "$P" && $PY -c "import re; b=re.search(r'^R6\.(.*?)^R7\.', open('$O').read(), re.S|re.M).group(1); assert 'occ_measure' in b, 'R6 block still does not name occ_measure'; assert all(re.search(r\"R6's\s+occ_measure/\", open(f).read()) for f in ['.planning/debug/260819-PENDING-PASTE-2-samepos-and-chain.md','.planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md','$P']), 'a runbook citation is missing'; print('R6-OK')" && bash "$V" all > /tmp/vbu_qpf_verify.txt 2>&1 && test "$(wc -c < /tmp/vbu_qpf_verify.txt)" = 2070 && md5sum /tmp/vbu_qpf_verify.txt | grep -q 83d60d91c6861c1f13ac728c059442ba && test "$(git diff --stat e63b9af HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/ | wc -l)" = 0 && A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md && awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb_qpf_t3.txt && test "$(wc -c < /tmp/pb_qpf_t3.txt)" = 22945 && md5sum /tmp/pb_qpf_t3.txt | grep -q 13a49f543cabcc27ce9f1e589783c060 && echo T3-VERIFY-OK</automated>
  </verify>
  <done>The PENDING PASTE carries STEP 1 = the three-run plink pairwise-complete falsifier with
empirical Z selection (printed retention table + a stated floor), the snplist-first row-order rule,
the four-hypothesis discrimination table whose 2-variant `{X,Z}` cell separates listwise from a bad
Z, and an explicit ⛔ DISCARD-THE-SWEEP consequence — ordered BEFORE the 00057 cross-check (STEP 2)
and the sweep (STEP 3), both of which survive unchanged. The "calls no plink at all" claim is gone,
`plink1.9 --version` gates on v1.90b7.2, and the `.fam` founder count is recorded. R6 names
`/home/jupyter/occ_measure/` with a dated provenance clause; all three runbooks' citations verify
newline-tolerantly; the vbu enforcer output is byte-identical (2070 B / 83d60d91…) and exit 0. The
paste is EXTENDED and STILL NOT RUN. One explicit-path commit; 0 failed.</done>
</task>

<task type="auto">
  <name>Task 4: Suite re-baseline (component-exact), HANDOFF/STATE, self-check, push</name>
  <files>.planning/HANDOFF.json, .planning/STATE.md, .planning/quick/260825-qpf-remediate-the-adversarial-review-of-the-/260825-qpf-SUMMARY.md</files>
  <action>
1. FULL SUITE, one invocation, ~13-14 min:
   `$PY -m pytest tests/m3 -q -rs 2>&1 | tail -25`
   (NEVER `pytest tests` as one invocation — `tests/m2/conftest.py` shadows `tests/m3/conftest.py`
   and it does not collect.)
   RECONCILE COMPONENT-EXACT against the measured baseline 1083 passed / 33 skipped / 0 failed /
   1116 collected: name EVERY test added across T1-T3, show `1083 + N == new_passed` and
   `1116 + N == new_collected`, and confirm skips are STILL 33. A new test landing as a SKIP is not
   evidence — investigate rather than absorb it. If the arithmetic does not close, do not round it:
   find the discrepancy (`feedback_a_count_is_a_claim_scope_and_reconcile`,
   `feedback_aggregate_agreement_hides_component_errors`).

2. `.planning/HANDOFF.json`: CORRECT `suite_baselines["tests/m3"]` in place (never append a second
   entry) and add a resume entry stating: the Codex adversarial review is REMEDIATED (F6/F4/F5
   fixed; F2/F1 re-dispositioned to reported-and-documented with named enforcers; F7 explicit-or-
   raise; the `--mac 1` parity class counted); **the instrument's pairwise-complete premise is
   UNCONFIRMED until STEP 1 of the paste runs**; the falsifier is WRITTEN AND UNRUN; prevalence,
   boundary width and the partial-confounding tail remain OPEN. `.planning/STATE.md`: prepend ONE dated Session Continuity section (house style, `* RESUME HERE - LATEST *`) in this same commit -- NOT a row in the orchestrator-owned `Quick Tasks Completed` table, which the /gsd-quick orchestrator populates in its own Step 7 after this plan's commits AND verification are complete (`feedback_state_md_keep_current`).

3. WRITE `260825-qpf-SUMMARY.md` from the house template. It MUST contain: every RED pasted
   verbatim (T1's three + the schema reds, T2's edge-clip/globally-invariant/summarize/enforcer
   reds, T3's R6 red), the three T1 + two T2 in-scratch perturbation negative controls, the
   component-exact suite arithmetic, the vbu before/after byte identity, and the two re-disposition
   rationales (why F2 is counted rather than changed; why F1 is pinned rather than changed) stated
   as decisions with reasons. State plainly: **no prevalence, no boundary width, no tail number
   appears anywhere**, and NOTHING WAS FIRED.

4. SELF-CHECK before pushing — run all of these and paste the output:
   * frozen-surface guard (incl. `src/python/aou_ld_panel.py`) -> 0
   * amendment paste-block guard, two-step file form -> 22945 / 13a49f543cabcc27ce9f1e589783c060
   * `bash $V all` -> exit 0, 2070 B, 83d60d91c6861c1f13ac728c059442ba
   * `grep -rIn "prevalence is\|boundary width is\|tail is [0-9]" .planning/quick/260825-qpf-*/ .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` -> no asserted value
   * `git status -s` shows ONLY this plan's files staged/committed; `tests/m3/sparse_parent_benchmark.tsv`
     is still ` M` and untouched, and `.planning/debug/m3-producer-unbounded-dense-read.md` is still untracked.

5. Commit EXPLICIT paths, then `git push`. Confirm `git status -sb` shows no `ahead`.
   Message: `docs(quick-260825-qpf): T4 — tests/m3 re-baselined component-exact; adversarial review REMEDIATED; the pairwise-complete premise is UNCONFIRMED until the falsifier runs; prevalence/boundary/tail stay OPEN`
   ⚠ `git push` does NOT push tags; none are created here.
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; V=.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh; $PY -m pytest tests/m3 -q 2>&1 | tail -3 | grep -qE '[0-9]+ failed' && { echo T4-SUITE-FAIL; exit 1; }; $PY -m pytest tests/m3 -q 2>&1 | tail -3 | grep -q '33 skipped' && test "$(git diff --stat e63b9af HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/ | wc -l)" = 0 && A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md && awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb_qpf_t4.txt && test "$(wc -c < /tmp/pb_qpf_t4.txt)" = 22945 && md5sum /tmp/pb_qpf_t4.txt | grep -q 13a49f543cabcc27ce9f1e589783c060 && bash "$V" all > /tmp/vbu_qpf_t4.txt 2>&1 && md5sum /tmp/vbu_qpf_t4.txt | grep -q 83d60d91c6861c1f13ac728c059442ba && grep -q 'pairwise_completeness_scan' .planning/HANDOFF.json && ! git status -sb | grep -q 'ahead' && echo T4-VERIFY-OK</automated>
  </verify>
  <done>`tests/m3` is 0 failed with skips still 33, reconciled component-exact from 1083/33/0 (1116
collected) with every added test named and the arithmetic shown; `HANDOFF.json`
`suite_baselines["tests/m3"]` is CORRECTED in place and names the premise as UNCONFIRMED;
`STATE.md` has its dated Session Continuity section (NOT a Quick Tasks Completed table row — that is the orchestrator's); the SUMMARY carries every red, every perturbation negative control, the
suite arithmetic, the vbu byte identity and both re-disposition rationales; the self-check output
is pasted; frozen surfaces, the amendment paste block and the vbu enforcer are all unchanged; no
prevalence/boundary/tail number appears anywhere; the branch is pushed and `git status -sb` shows
no `ahead`.</done>
</task>

</tasks>

<verification>
Run at the END of the plan (all must hold simultaneously):

```bash
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
V=.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh
P=.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
O=.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md

# 1. the three fixes, by name
grep -c '3 + idx \* self.bytes_per_variant' src/python/pairwise_completeness_scan.py     # 1
grep -c '3 + index \* self.bytes_per_variant' src/python/pairwise_completeness_scan.py   # 0
grep -c 'def _pair_key' src/python/pairwise_completeness_scan.py                          # 1
grep -c 'sorted((deletion.vid, partner.vid))' src/python/pairwise_completeness_scan.py    # 0
grep -c 'minor_allele_tie' src/python/pairwise_completeness_scan.py                       # >= 3

# 2. the reporting surface
$PY -c "import sys;sys.path.insert(0,'src/python');import pairwise_completeness_scan as p;\
print(p.TSV_COLUMNS==p.PairResult._fields, len(p.TSV_COLUMNS), len(p.SUMMARY_KEYS));\
print([k for k in ('n_candidates_edge_clipped','n_globally_invariant_variants',\
'n_undefined_rows_with_globally_invariant_member') if k in p.SUMMARY_KEYS]);\
print('nonfounders' in p.__doc__)"

# 3. the falsifier is in the paste, before the cross-check, and the no-plink claim is retracted
! grep -q 'calls no plink at all' "$P" && grep -c 'v1.90b7.2\|write-snplist\|mean-imputation\|listwise' "$P"

# 4. R6 and its three citations
$PY - <<'EOF'
import re
O = ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
b = re.search(r'^R6\.(.*?)^R7\.', open(O).read(), re.S | re.M).group(1)
assert "occ_measure" in b
for f in (".planning/debug/260819-PENDING-PASTE-2-samepos-and-chain.md",
          ".planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md",
          ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md"):
    assert re.search(r"R6's\s+occ_measure/", open(f).read()), f
print("R6 + all three citations OK")
EOF

# 5. the pinned enforcer is byte-identical
bash "$V" all > /tmp/vbu_final.txt 2>&1; echo "exit=$?"; wc -c < /tmp/vbu_final.txt; md5sum /tmp/vbu_final.txt
#   -> exit 0 · 2070 · 83d60d91c6861c1f13ac728c059442ba

# 6. frozen surfaces + the posted amendment (SAFE TWO-STEP FILE FORM ONLY)
git diff --stat e63b9af HEAD -- src/python/occlusion_span_filter.py \
  src/python/run_native_ld_panel.py src/python/fire_verifier.py \
  src/python/aou_ld_panel.py .planning/amendments/ | wc -l                                # 0
awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb_final.txt
wc -c < /tmp/pb_final.txt      # 22945
md5sum /tmp/pb_final.txt       # 13a49f543cabcc27ce9f1e589783c060

# 7. the suite and the branch
$PY -m pytest tests/m3 -q -rs 2>&1 | tail -5     # 0 failed, 33 skipped, 1083+N passed
git status -sb | head -1                          # no 'ahead'
```
</verification>

<success_criteria>
- [ ] F6: seek uses the normalised index; str/integral-float indices read correctly; a non-integral
      index RAISES; the textual enforcer test passes and was seen red
- [ ] F4: `pair_key` is index-based; a duplicate-`.`-id fixture reports 2 distinct pairs (seen red
      at 1); the del-del one-key test is still green
- [ ] F5: the exact `af_a1 == 0.5` tie reports the LARGER carrier loss with visible
      `del_/partner_minor_allele_tie` columns; the tail-hiding fixture was seen red at `0.0`; every
      non-tie number in the four pre-existing genotype tests is unchanged
- [ ] F2: `n_candidates_edge_clipped` is in `SUMMARY_KEYS` and exercised; NO emitted row references
      a variant outside the region bounds; the `.bim` is still read in ONE pass; the docstring
      states the region-matrix universe and why the clipping is correct
- [ ] `--mac 1` parity: `del_/partner_globally_invariant` columns +
      `n_globally_invariant_variants` + `n_undefined_rows_with_globally_invariant_member`; the set
      relation is stated in the correct direction
- [ ] F1: the docstring states the `--nonfounders` coupling and the drop-the-flag consequence; the
      read-only cross-module SYMBOL enforcer test passes and was seen red on a scratch copy;
      `aou_ld_panel.py` is UNCHANGED
- [ ] F7: `summarize` requires both denominators; `summarize("R", [])` raises; all six existing
      call sites are explicit
- [ ] F3: the paste's STEP 1 is the three-run falsifier with empirical Z selection + a retention
      floor, `--extract` + production LD modifiers with each modifier decision reasoned, the
      snplist-first row-order rule, the four-hypothesis table with the 2-variant `{X,Z}`
      discriminator, and the ⛔ DISCARD-THE-SWEEP consequence — ordered before STEP 2 (00057) and
      STEP 3 (sweep), both of which survive
- [ ] The paste no longer claims it calls no plink; `plink1.9 --version` gates on v1.90b7.2; the
      PATH export is required-first-action; the `.fam` founder count is recorded
- [ ] R6 names `/home/jupyter/occ_measure/` with a dated provenance clause; all three runbook
      citations verify newline-tolerantly; the vbu enforcer output is byte-identical (2070 B /
      83d60d91c6861c1f13ac728c059442ba, exit 0)
- [ ] Frozen surfaces empty-diff vs `e63b9af`; the amendment paste block is 22945 B /
      13a49f543cabcc27ce9f1e589783c060 by the SAFE TWO-STEP FILE FORM at every commit
- [ ] Every new/changed test was SEEN RED before GREEN and the red is pasted; five in-scratch
      perturbation negative controls are pasted
- [ ] `tests/m3` 0 failed at EVERY commit; skips still 33; reconciled component-exact from
      1083/33/0 (1116 collected)
- [ ] NOTHING FIRED: no VM/Dataproc/OSF/gsutil/gcloud/network contact; the paste is EXTENDED and
      NOT RUN; no prevalence, boundary-width or tail number is asserted anywhere — all three OPEN
- [ ] Explicit-path staging only; the pre-existing dirty/untracked paths are untouched;
      `git status -sb` shows no `ahead`
</success_criteria>

<output>
After completion, create
`.planning/quick/260825-qpf-remediate-the-adversarial-review-of-the-/260825-qpf-SUMMARY.md`.
</output>
