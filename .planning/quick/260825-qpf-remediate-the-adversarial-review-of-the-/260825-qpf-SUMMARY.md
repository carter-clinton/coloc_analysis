---
phase: quick-260825-qpf
plan: 01
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, adversarial-review-remediation, plink-semantics-falsifier, undefined-ld, deletion-boundary, prevalence-sweep, r6-governance, tdd, instrument-only, m3-07, stage-b]

requires:
  - src/python/pairwise_completeness_scan.py (quick-260825-ngh)
  - tests/m3/test_pairwise_completeness_scan.py (quick-260825-ngh)
  - .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md
provides:
  - a remediated pairwise-completeness scanner whose three real defects are fixed and whose two silent couplings are counted
  - a RUNNABLE, READ-ONLY, THREE-RUN plink falsifier for the instrument's load-bearing premise, placed BEFORE any number is generated
  - R6 amended to RECORD the /home/jupyter/occ_measure/ allowance that three runbooks already cite
affects:
  - .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md

tech-stack:
  added: []
  patterns:
    - "cross-module SYMBOL enforcer via ast, not grep — the in-code COMMENT carried the same string, so a textual pin stayed GREEN with the flag deleted from the argv"
    - "explicit-or-raise denominators: a derived default is a WRONG number, not a missing one"
    - "count the suppression instead of changing the behaviour, when the behaviour is correct and the SILENCE is the defect"
    - "falsify the premise BEFORE producing the numbers, with a written discard-on-mismatch consequence"

key-files:
  created:
    - .planning/quick/260825-qpf-remediate-the-adversarial-review-of-the-/260825-qpf-SUMMARY.md
  modified:
    - src/python/pairwise_completeness_scan.py
    - tests/m3/test_pairwise_completeness_scan.py
    - .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
    - .planning/HANDOFF.json
    - .planning/STATE.md
    - .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md

decisions:
  - "F2 (region-edge clipping) is COUNTED and DOCUMENTED, not changed — the clipping is CORRECT and the defect was the SILENCE"
  - "F1 (founders) is DOCUMENTED and given a named ast enforcer, not changed — it is a COUPLING to a flag production already passes"
  - "the --nonfounders enforcer is an ast pin on the argv, never a textual grep, because the in-code comment also contains the string"
  - "the exact af_a1 == 0.5 tie reports the LARGER carrier loss and emits a visible tie column, rather than picking A1 by fiat"
  - "the plink falsifier goes BEFORE the 00057 cross-check and BEFORE the sweep, with an explicit DISCARD-THE-SWEEP consequence"
  - "R6 is AMENDED to record an already-exercised allowance rather than the citations being deleted"

metrics:
  duration: "~2 h 40 m (2026-08-25 19:44 -> 22:2x EDT)"
  completed: 2026-08-25
---

# quick-260825-qpf: Remediate the adversarial review of the pairwise-completeness scanner — Summary

An external adversarial review (Codex) found three real correctness defects, two silent
couplings and two API/doc items in the pairwise-completeness scanner, and named the one
experiment that could void every number the instrument will ever produce. All of it is
remediated. **Nothing here blocked the committed code; everything here blocked TRUSTING
THE NUMBERS** — and those numbers are headed for a public OSF pre-registration, where a
wrong instrument yields a *confidently* wrong prevalence.

**The single most important outcome is a negative one:** the scanner's load-bearing
premise — that plink1.9 `--r` correlates over PAIRWISE-COMPLETE observations — is still
**UNCONFIRMED**. It is now **FALSIFIABLE** by a $0-to-write, minutes-to-run, read-only
three-run experiment that is written into the runbook **before** any number is generated,
with an explicit ⛔ DISCARD-THE-SWEEP consequence. **It has not been run.**

**NOTHING WAS FIRED.** Zero VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact.
`$0`. The VM stays STOPPED. No plink was invoked anywhere. **No prevalence, no boundary
width and no partial-confounding tail number appears in any deliverable** — all three
stay OPEN, by design.

---

## Commits

| Task | Commit | What |
|------|--------|------|
| T1 | `2aed0db` | F6 normalised seek index, F4 index-based pair keys, F5 the max-loss minor-allele tie rule + visible tie columns |
| T2 | `a6dd4bc` | F2 edge-clip counter, the `--mac 1` globally-invariant parity counters, F1 the `--nonfounders` `ast` enforcer, F7 explicit-or-raise denominators |
| T3 | `1d2bd53` | the three-run plink pairwise-complete FALSIFIER as STEP 1 of the runbook, the pinned-plink gate + `.fam` founder count, R6 amended |
| T4 | *(this docs commit)* | suite re-baseline, HANDOFF/STATE/.continue-here, this SUMMARY |

Every commit staged **EXPLICIT PATHS ONLY** (`feedback_multi_terminal_staging`).

---

## Findings, dispositions, and what actually changed

| # | Review severity | Our disposition | What changed |
|---|-----------------|-----------------|--------------|
| F6 | LOW | **FIXED** | the `.bed` seek now uses the bounds-checked `idx`; a non-integral index RAISES |
| F4 | MEDIUM | **FIXED** | `pair_key` is the two globally-unique `.bim` ROW INDICES |
| F5 | MEDIUM | **FIXED** | the exact `af_a1 == 0.5` tie reports the LARGER carrier loss, with a visible tie column |
| F2 | HIGH | **RE-DISPOSITIONED → REPORTED, not changed** | `n_candidates_edge_clipped` + a behaviour-preservation guard + a docstring section |
| F1 | HIGH | **RE-DISPOSITIONED → DOCUMENTED + ENFORCED, not changed** | a docstring coupling paragraph + a read-only cross-module `ast` enforcer |
| F3 | HIGH | **ANSWERED WITH AN EXPERIMENT** | a three-run falsifier written into the runbook, unrun |
| F7 | LOW | **FIXED** | `summarize()` requires both denominators; no default |
| `--mac 1` parity | (from the blast-radius sweep) | **COUNTED** | two boolean columns + two summary counters |
| R6 citation gap | (from the blast-radius sweep) | **RULE AMENDED** | R6 now names `/home/jupyter/occ_measure/`, dated |

### Why F2 was downgraded (a decision, with its reason)

The review's HIGH #2 said region-edge clipping "can miss candidates". It is right that
candidates are suppressed and wrong that the suppression is a defect. **A region's
universe is exactly that region's own LD matrix.** A variant outside `[from_bp, to_bp]`
is not a row of that matrix and therefore *cannot produce a NaN in it*, so declining to
emit a pair that reaches past the boundary is CORRECT. The defect was that the
suppression was **SILENT** — a region-edge deletion simply looked like a deletion with
fewer neighbours.

So it is COUNTED (`n_candidates_edge_clipped`), documented in the module docstring under
`REGION EDGES — CLIPPED BY DESIGN, COUNTED SO IT IS NEVER SILENT`, and *guarded*:
`test_no_emitted_row_references_a_variant_outside_the_region` proves the padded `.bim`
read leaks no out-of-region pair into the output, and the pre-existing one-pass tests
prove the `.bim` is still opened exactly once. **Anchor-side** clipping (a deletion
outside the region) is deliberately not counted, for the same reason: such a deletion is
not a row of that matrix either, so no pair containing it exists there at all.

### Why F1 was downgraded (a decision, with its reason)

The review's HIGH #1 said the scanner's all-samples policy could create false negatives
against plink's founders-only default. Correct as a *mechanism*, but the production
square command **already passes `--nonfounders`** — so all-samples is the MATCHING policy
today, and changing the scanner would *introduce* the mismatch. What was missing is that
nothing enforced the coupling.

It is now documented (`SAMPLE POLICY — A COUPLING, NOT AN ASSUMPTION`, including the
drop-the-flag consequence in as many words) and enforced by
`test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag`, which READS
`src/python/aou_ld_panel.py` (never writes it) and parses
`build_plink_ld_command` with `ast`.

**Why `ast` and not a grep — this is the load-bearing detail.** The in-code comment
beside that argv line *also* contains the string `--nonfounders`, three times in the
file altogether. A textual pin would stay GREEN with the flag deleted from the command.
Measured on a scratch copy with the flag removed from the argv: `grep -c -- "--nonfounders"`
still returned **3**, while the `ast` pin went RED with
`assert '--nonfounders' in {'--mac', '--r', '--write-snplist', '1', 'bin4', 'square'}`.
The pin is on the argv the function BUILDS. It is a SYMBOL pin, never a fixed-SHA
whole-file pin (`feedback_fixed_sha_whole_file_pin_is_a_timebomb`).

---

## The RED, verbatim

Every new/changed assertion was seen fail before it was made to pass
(`feedback_green_assertion_needs_a_negative_control`). Reds are excerpted verbatim from
`pytest` output; the full captures live in the session scratchpad.

### T1 — the three correctness fixes (7 tests, 7 RED)

```
--- test_read_variant_accepts_a_coercible_index
>           got_str = np.array(reader_str.read_variant("1").dosage)
>       offset = 3 + index * self.bytes_per_variant
E       TypeError: unsupported operand type(s) for +: 'int' and 'str'

--- test_read_variant_rejects_a_non_integral_index
>               reader.read_variant(1.5)
>       self._fh.seek(offset)
E       TypeError: 'float' object cannot be interpreted as an integer

--- test_seek_offset_uses_the_normalised_index
>       assert src.count("3 + idx * self.bytes_per_variant") == 1, (
E       AssertionError: the .bed seek offset must be computed from the NORMALISED index `idx`
E       assert 0 == 1

--- test_duplicate_variant_ids_do_not_collapse_distinct_pairs
>       assert summary["n_distinct_pairs"] == 2
E       assert 1 == 2

--- test_pair_key_names_the_rows_it_keys
>   assert sorted(int(x) for x in r.pair_key.split("|")) == sorted(
        [r.del_index, r.partner_index]
    )
E   ValueError: invalid literal for int() with base 10: '.'

--- test_exact_allele_frequency_tie_reports_the_larger_carrier_loss
>       assert pr.del_carriers_retained == 1
E       AssertionError: assert 4 == 1

--- test_no_tie_flag_when_the_minor_allele_is_unambiguous
>       assert pr.del_minor_allele_tie is False
E       AttributeError: 'PairResult' object has no attribute 'del_minor_allele_tie'
```

Note on the F6 non-integral red: the shipped code *did* raise — a `TypeError` from deep
inside `file.seek()`, as an **accident of the very defect F6 fixes**. Once the seek is
corrected, a bare `int(1.5) == 1` reads variant 1 and returns a well-formed dosage array
for the **wrong variant** with no error anywhere. Pinning the exception TYPE and MESSAGE
(`pytest.raises(ValueError, match="non-integral")`) is what makes the rejection survive
the fix — see negative control **(d)** below, which shows the test catching exactly that.

Note on the F5 red: `assert 4 == 1` is the tail-hiding case in one line. The shipped
A1-by-fiat rule reported `del_carriers_retained 4 / lost 0 / lost_frac 0.0` for a member
whose *other* allele had lost **3 of its 4** carriers to the partner's missingness — and
`summarize` binned that row as `"0"`, the most reassuring bin there is.

### T2 — the two silent couplings (7 tests, 6 RED + 1 green-by-design)

```
--- test_edge_clipped_candidates_are_counted_not_silently_absent
>       assert summary["n_candidates_edge_clipped"] == 1
E       KeyError: 'n_candidates_edge_clipped'

--- test_no_edge_clipping_reports_zero
>       assert summary["n_candidates_edge_clipped"] == 0
E       KeyError: 'n_candidates_edge_clipped'

--- test_globally_invariant_variant_is_reported_separately
>       assert pr.partner_globally_invariant is True
E       AttributeError: 'PairResult' object has no attribute 'partner_globally_invariant'

--- test_ordinary_variants_are_not_globally_invariant
>       assert pr.del_globally_invariant is False
E       AttributeError: 'PairResult' object has no attribute 'del_globally_invariant'

--- test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag
>       assert "--nonfounders" in doc
E       AssertionError: assert '--nonfounders' in 'Pairwise-completeness scanner — a genotype-only detector of UNDEFINED LD....'

--- test_summarize_requires_its_denominators
>       with pytest.raises(TypeError, match="n_deletions"):
E       Failed: DID NOT RAISE <class 'TypeError'>
```

`test_no_emitted_row_references_a_variant_outside_the_region` was **GREEN at write time
and that is by design** — it is a behaviour-PRESERVATION guard, and today's unpadded read
cannot leak. Its red is negative control **(e)** below, run against a scratch copy that
emitted the padded partners. Reported honestly rather than counted as a RED.

### T3 — the falsifier runbook and the R6 amendment (4 tests, 4 RED)

```
--- test_pending_paste_carries_the_falsifier_tokens
E           AssertionError: PENDING PASTE is missing the falsifier token 'mean-imputation'

--- test_pending_paste_runs_the_falsifier_before_the_crosscheck_and_the_sweep
E           AssertionError: missing step heading '=== STEP 1 — THE plink PAIRWISE-COMPLETE FALSIFIER'

--- test_pending_paste_no_longer_claims_it_calls_no_plink
>       assert "calls no plink at all" not in text
E       AssertionError: assert 'calls no plink at all' not in '# PENDING P...two apart.\n'
E         'calls no plink at all' is contained here:
E           his sweep calls no plink at all.**

--- test_r6_records_the_occ_measure_allowance_and_all_three_runbooks_cite_it
>       assert "occ_measure" in block, (
E       AssertionError: R6 still does not name /home/jupyter/occ_measure/, yet three runbooks cite 'R6's occ_measure/ allowance'
```

**One in-flight test correction, disclosed.** The STEP 1 consequence sentence wraps across
a line in the rendered runbook, so an initial single-line assertion
(`"Do NOT run STEP 2. Do NOT run STEP 3." in text`) failed against a runbook that *did*
carry the property. Rather than reflow the prose to satisfy a brittle proxy
(`feedback_scope_a_guard_to_the_property_not_a_proxy`), the assertion was made
newline-tolerant. It was then **re-proved RED against the pre-`qpf` paste**, so the
correction did not weaken it:

```
$ git show HEAD:.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
Do not skip STEP 1.        -> True
STEP2+STEP3 consequence    -> False        # <- the regex is still RED on the old file
```

---

## Perturbation negative controls (in SCRATCH copies only, never in-tree)

Six controls, each run in a **throwaway mirror tree** under the session scratchpad
(`src/python/` + `tests/m3/` copies), in a **fresh interpreter** with `__pycache__`
removed and `python -B`, so a byte-length-identical edit reverted within the same second
cannot run stale bytecode (`feedback_negative_control_defeated_by_bytecode_cache`). The
in-tree files were never touched by any of them.

**Mirror sanity first** — the UNPERTURBED mirror is GREEN (`7 passed, 62 deselected`), so
every red below is attributable to the perturbation and not to the mirror.

| # | Perturbation (scratch copy) | Result |
|---|------------------------------|--------|
| a | seek reverted to `3 + index * bytes_per_variant` | 2 failed — `test_read_variant_accepts_a_coercible_index`, `test_seek_offset_uses_the_normalised_index` |
| b | `pair_key` reverted to `"\|".join(sorted((deletion.vid, partner.vid)))` | 2 failed — `test_duplicate_variant_ids_do_not_collapse_distinct_pairs`, `test_pair_key_names_the_rows_it_keys` |
| c | tie reverted to `if af_a1 <= 0.5` (A1 by fiat) | 1 failed — `test_exact_allele_frequency_tie_reports_the_larger_carrier_loss` (`assert 4 == 1`) |
| d | `_as_variant_index` truncates silently instead of raising | 1 failed — `test_read_variant_rejects_a_non_integral_index` (`Failed: DID NOT RAISE <class 'ValueError'>`) |
| e | `enumerate_candidates` emits the PADDED partners | 1 failed — `test_no_emitted_row_references_a_variant_outside_the_region` (`assert 1011 <= 1010`) |
| f | `--nonfounders` deleted from the square argv of a scratch `aou_ld_panel.py` | 1 failed — `test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag` |

**Control (f) is the one that changed a design decision.** After deleting the flag from
the argv, `grep -c -- "--nonfounders"` on the scratch file still returned **3** (docstring
×2 + the in-code comment). A textual enforcer would have been GREEN on a file where the
production command no longer passes the flag. That is why the enforcer parses the argv
with `ast`.

Control (e)'s run also confirmed the three new summary keys reach the stdout scalar table
(and are not histograms/bins):

```
region_id  window_bp  n_deletions  n_candidate_rows  ...  n_candidates_edge_clipped  n_globally_invariant_variants  n_undefined_rows_with_globally_invariant_member
edge       25         1            2                 ...  1                          0                              0
```

---

## The falsifier (F3) — what was written, and what it does NOT establish

STEP 1 of `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`, placed
**before** the 00057 cross-check (now STEP 2) and **before** the 21-region sweep (now
STEP 3):

* **1a selects Z EMPIRICALLY.** It walks the variants within ±200 bp of X with the
  module's own `BedReader`, prints a full retention table
  (`vid / pos / n_called / retention = |carriers(X) ∩ called(C)| / |carriers(X)|`),
  names the chosen Z with its MEASURED retention, and **STOPS if the best retention is
  below 0.80** — a discriminator with no power would manufacture a false falsification.
  The paste states, in its own text, that 1a uses the instrument's own decoder and that
  this failure mode is **FAIL-SAFE** (a false STOP, never false confidence).
* **1b runs plink1.9 three times** on `{X,Y,Z}`, `{X,Z}` and `{X,Y}` with the production
  LD modifiers `--keep-allele-order --mac 1 --nonfounders --write-snplist --r square bin4`,
  selecting variants with `--extract` (the ids contain colons, and `--snps` parses `-` as
  a range separator). Every modifier decision is reasoned **in the paste**: `--mac 1` is
  included so the command is production-shaped and the `.snplist` line count (3/2/2) is
  what PROVES it was a no-op; `--exclude` is omitted because it changes which pairs EXIST,
  not how `r` is computed over a pair that does.
* **The `.snplist` is read FIRST, always** — the `.ld.bin` rows are in `.bim`/position
  order, so if Z sits before X, **Z is row 0**. The byte size is asserted to be exactly
  `k*k*4` before any `np.fromfile`, and `read_square_bin` is banned by name because it
  RAISES on the NaN that is the *signal* here.
* **1c discriminates** against a printed four-hypothesis table. The **2-variant `{X,Z}`**
  cell is the discriminator: real listwise-over-the-window makes `(X,Z)` NaN at three
  variants and **finite** at two; a merely mis-selected Z makes it **NaN at both**. A
  non-1.0 diagonal anywhere, or any unclassified pattern, is itself a STOP.
* **1d states the consequence.** ⛔ Any verdict but `PAIRWISE-COMPLETE`: **STOP, paste
  verbatim, DISCARD THE SWEEP, do NOT run STEP 2 or STEP 3.** Do not adjust the code, the
  window, the Z, or the expectations to make it pass.

**It is WRITTEN AND UNRUN.** As a one-off editorial check (not a committed test) all four
of the paste's embedded Python heredoc blocks were `ast.parse`d and are syntactically
valid, so a syntax error cannot waste a fire.

STEP 0 additionally gates on `plink1.9 --version` printing **`PLINK v1.90b7.2 64-bit
(11 Dec 2023)`**, bans the `which plink || which plink1.9` form **by name** (it passed on
the wrong binary twice), promotes `export PATH="$HOME/bin:$PATH"` to REQUIRED FIRST
ACTION, records that a browser agent will correctly REFUSE the download-and-execute
install so **Carter** pastes that one command, and records the `.fam` **founder count**
as a field record of whether the founders/nonfounders distinction is even live in this
cohort (no expected value stated).

Both occurrences of *"This sweep calls no plink at all"* are **retracted**, pinned by a
negative-needle test.

---

## R6, and the proof it disturbed nothing

`grep -c occ_measure` on `260812-ox1-AGENT-PROMPT.md` was **0** (measured) while **three**
runbooks cited *"R6's `occ_measure/` allowance"*. A cited rule that does not say what is
cited is an unenforceable permission, and agents act on the citation. R6 now names
`/home/jupyter/occ_measure/` and the measurement-sweep outputs written inside it,
including the falsifier's small plink working files, with a dated provenance clause
stating that this **RECORDS an allowance already exercised with Carter's explicit go from
2026-08-19 onward** and grants no new directory and no new deletion right. The falsifier
is deliberately designed to create **no individual-level file** (no `--recode A`), so no
new deletion right is needed.

The citation enforcer is **newline-tolerant** (`re.search(r"R6's\s+occ_measure/", text)`):
two of the three runbooks wrap the citation across a line break, so a naive one-line grep
finds only ONE of the three (measured). The R6 assertion itself is scoped to the
`^R6\.` … `^R7\.` **block**, not the whole file.

### vbu §6b enforcer — BEFORE and AFTER, byte-identical

```
BEFORE   bash 260817-vbu-verify.sh all   exit=0   2070 bytes   83d60d91c6861c1f13ac728c059442ba
AFTER    bash 260817-vbu-verify.sh all   exit=0   2070 bytes   83d60d91c6861c1f13ac728c059442ba
cmp /tmp-scratch/vbu_before.txt /tmp-scratch/vbu_after.txt  ->  VBU-BYTE-IDENTICAL
last line: RESULT: ALL CHECKS PASSED (section: all)
```

Sound because the verifier's card checks operate on the block delimited by `^STEP 6b` …
`^STEP 7` and report line numbers RELATIVE to that block, while R6 sits at line 32 — far
above it — so an insertion there cannot shift a single reported number. Captured to files
and compared with `cmp`, never eyeballed.

---

## Frozen surfaces and the public record — BEFORE and AFTER

Re-verified at the START and END of **every** task.

| Anchor | BEFORE (T1 start) | AFTER (T4 self-check) |
|--------|-------------------|------------------------|
| `git diff --stat e63b9af HEAD -- occlusion_span_filter.py run_native_ld_panel.py fire_verifier.py aou_ld_panel.py .planning/amendments/` \| `wc -l` | `0` | `0` |
| posted amendment paste block, size | `22945` | `22945` |
| posted amendment paste block, md5 | `13a49f543cabcc27ce9f1e589783c060` | `13a49f543cabcc27ce9f1e589783c060` |
| `260817-vbu-verify.sh all` | exit 0, 2070 B, `83d60d91c6861c1f13ac728c059442ba` | exit 0, 2070 B, `83d60d91c6861c1f13ac728c059442ba` |

The md5 was computed with the **SAFE TWO-STEP FILE FORM** (`awk` into a scratch file, then
`wc -c` and `md5sum` on that file). The `awk … | tee >(wc -c) | md5sum` one-liner is
banned by name: process substitution interleaves into `md5sum`'s stdin and deterministically
prints the phantom `2f2e9548e1b2952ac802a847ea5dff40` on an unchanged file.

`src/python/aou_ld_panel.py` is READ by the F1 enforcer and is byte-unchanged
(`git status --porcelain` empty for that path at every task).

---

## Suite re-baseline — COMPONENT-EXACT

```
BASELINE (72814e6, quick-260825-ngh):  1083 passed / 33 skipped / 0 failed   (1116 collected)
MEASURED (1d2bd53, quick-260825-qpf):  1101 passed / 33 skipped / 0 failed   (1134 collected, 813.85 s)
```

**+18 items added, 0 removed, 0 renamed**, all in the SAME one file
`tests/m3/test_pairwise_completeness_scan.py`.

```
1083 + 18 = 1101 passed            ✓
1116 + 18 = 1134 collected         ✓
1101 + 33 = 1134                   ✓
```

Every added test, by name:

| Task | Tests added |
|------|-------------|
| T1 (7) | `test_read_variant_accepts_a_coercible_index`, `test_read_variant_rejects_a_non_integral_index`, `test_seek_offset_uses_the_normalised_index`, `test_duplicate_variant_ids_do_not_collapse_distinct_pairs`, `test_pair_key_names_the_rows_it_keys`, `test_exact_allele_frequency_tie_reports_the_larger_carrier_loss`, `test_no_tie_flag_when_the_minor_allele_is_unambiguous` |
| T2 (7) | `test_no_emitted_row_references_a_variant_outside_the_region`, `test_edge_clipped_candidates_are_counted_not_silently_absent`, `test_no_edge_clipping_reports_zero`, `test_globally_invariant_variant_is_reported_separately`, `test_ordinary_variants_are_not_globally_invariant`, `test_all_samples_policy_is_pinned_to_the_production_nonfounders_flag`, `test_summarize_requires_its_denominators` |
| T3 (4) | `test_pending_paste_carries_the_falsifier_tokens`, `test_pending_paste_runs_the_falsifier_before_the_crosscheck_and_the_sweep`, `test_pending_paste_no_longer_claims_it_calls_no_plink`, `test_r6_records_the_occ_measure_allowance_and_all_three_runbooks_cite_it` |

`7 + 7 + 4 = 18`. No `parametrize` among them — every one is a single item.

**Checked a third, independent way** rather than trusting the arithmetic
(`feedback_aggregate_agreement_hides_component_errors`):

```
pytest tests/m3 --collect-only -q                                                   -> 1134
pytest tests/m3 --collect-only -q --ignore=tests/m3/test_pairwise_completeness_scan.py -> 1054   (UNCHANGED since before ngh)
pytest tests/m3/test_pairwise_completeness_scan.py --collect-only -q                 ->   80   (= 62 + 18)
                                                                            1054 + 80 = 1134   ✓
```

So the pre-existing set is **provably untouched** and the `+18` cannot be masking an
offsetting add/remove.

**Skips STAYED at 33** (`grep -c "^SKIPPED"` on the `-rs` output = 33). Every added test
is pure-synthetic (`tmp_path` fixtures, or a read-only parse of an in-repo file), needs no
perimeter, no Hail, no chain file and no measured artifact, so it cannot land as a skip. A
new SKIP would be a BLOCKER, not a rounding difference
(`feedback_skip_guard_masks_not_fixes`).

`tests/m3` reported **0 failed at every commit** (T1 and T2 verified with the two-file
run; T3 with the pairwise file; T4 with the full suite).

---

## Deviations from plan

**One, and it is a test correction, not a scope change:** the T3 step-consequence
assertion was written as a single-line needle and had to be made newline-tolerant when
the sentence wrapped in the rendered runbook. Documented above with proof that the
corrected regex is still RED against the pre-`qpf` file, so nothing was weakened.

**One plan expectation not met, reported rather than forced:** T2's
`test_no_emitted_row_references_a_variant_outside_the_region` was **green when written**.
The plan anticipated this (it specifies the scratch-copy red for that test), and the red
was obtained as negative control (e). Counted honestly as 6 RED of 7 in T2, not 7.

Otherwise the plan executed as written. No architectural change was needed; no Rule 4
checkpoint was reached.

---

## Housekeeping note — `tests/m3/sparse_parent_benchmark.tsv`

Reported because it moved without my action, which on a shared GPFS tree is worth saying
out loud.

* At session start (`git status` snapshot) it was ` M` — pre-existing timing noise.
* At **19:46:59 EDT** it became **clean** on its own. I never ran
  `tests/m3/test_sparse_parent_benchmark.py` (the only writer of that file, verified by
  grep) at that time, and I never staged it. Most likely another terminal on the shared
  tree restored it.
* My T4 full-suite run then re-dirtied it with fresh timing noise, and I restored it with
  `git checkout -- tests/m3/sparse_parent_benchmark.tsv`, as directed.
* **It appears in none of this plan's commits.** The untracked
  `.planning/debug/m3-producer-unbounded-dense-read.md` is untouched and still untracked.

## Follow-up worth doing later (NOT done here, deliberately)

The four Python heredoc blocks embedded in the PENDING PASTE were `ast.parse`d once, by
hand, this session — all four are syntactically valid. That check is **not** a committed
test, because adding a 19th test mid-reconciliation would have required a second 14-minute
suite run and re-derivation of every count. A future quick task should make it one: a
syntax error inside a runbook is a wasted fire.

---

## WHAT THIS DOES NOT ESTABLISH

Read this section before quoting anything above.

1. **It does NOT establish that plink1.9 `--r` is pairwise-complete.** That is the
   instrument's load-bearing premise and it remains **UNCONFIRMED**. The evidence is still
   circumstantial (both marginals variable, diagonal 1.0, one symmetric NaN pair). The
   falsifier that would settle it is **WRITTEN AND UNRUN**. If it comes back anything other
   than `PAIRWISE-COMPLETE`, the sweep is discarded and the approach is rethought.
2. **It does NOT establish any prevalence** of undefined pairs — not for the panel, not
   for a region, not for the 21-region sample. No such number appears anywhere in any
   deliverable.
3. **It does NOT establish the boundary width**, nor whether it is one-sided. The
   ±25 bp window is a MEASUREMENT parameter, never a threshold; nothing is excluded or
   decided on the basis of it.
4. **It does NOT establish that a partial-confounding tail exists**, nor how large it
   would be. The gradient can now *see* one; it has seen nothing, because it has touched
   no data.
5. **It does NOT validate the instrument against real genotypes.** Everything here was
   exercised on synthetic `tmp_path` fixtures and read-only parses of in-repo files. The
   scanner has still never touched data.
6. **It does NOT change any criterion, threshold, span rule or NaN policy**, and it does
   not widen the pre-registered occlusion span by one base or any other amount. The posted
   OSF record is byte-unchanged.
7. **It does NOT settle whether the region-1 negative control is bias-free.** Region 1
   passing NaN-free establishes only that it held no *perfectly* confounded pair.
8. **It does NOT adjudicate anything.** Whether the criterion is extended, whether an
   explicit pairwise-completeness policy is added, and what Stage C's error-handling
   posture becomes are SEPARATE pre-registration questions, for after the numbers exist,
   brief-blind, with Seth.
9. **NOTHING WAS FIRED.** Zero VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact;
   `$0`; the VM stayed STOPPED; no plink binary was invoked; the PENDING PASTE is EXTENDED
   and NOT RUN.

---

## Self-Check: PASSED

Run at T4, immediately before the push, in the checked-out tree on `m3-W2-aou-deltas`.

```
=== 1. FROZEN-SURFACE GUARD (incl. aou_ld_panel.py) ===
0
=== 2. AMENDMENT PASTE BLOCK (two-step FILE form) ===
22945
13a49f543cabcc27ce9f1e589783c060  .../pb_final.txt
=== 3. vbu ENFORCER ===
exit=0
2070
83d60d91c6861c1f13ac728c059442ba  .../vbu_final.txt
RESULT: ALL CHECKS PASSED (section: all)
=== 4. no asserted prevalence / boundary / tail value ===
(no output = none)
=== 5. the three fixes by name ===
grep -c '3 + idx * self.bytes_per_variant'      -> 1
grep -c '3 + index * self.bytes_per_variant'    -> 0
grep -c 'def _pair_key'                         -> 1
grep -c 'sorted((deletion.vid, partner.vid))'   -> 0
grep -c 'minor_allele_tie'                      -> 6
=== 6. R6 + the three citations ===
R6 + all three citations OK
=== 7. HANDOFF names the module ===
2
=== 8. git status ===
 M .planning/HANDOFF.json
 M .planning/STATE.md
 M .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
?? .planning/debug/m3-producer-unbounded-dense-read.md      (pre-existing, untouched)
## m3-W2-aou-deltas...origin/m3-W2-aou-deltas [ahead 3]
```

`tests/m3/sparse_parent_benchmark.tsv` is **clean** and appears in no commit (see the
housekeeping note above). Every artifact this SUMMARY claims exists was confirmed on
disk, and all three task commits (`2aed0db`, `a6dd4bc`, `1d2bd53`) were confirmed present
in `git log`.
