---
phase: quick-260825-ngh
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, undefined-ld, deletion-boundary, prevalence-sweep, bed-reader, tdd, instrument-only, m3-07, stage-b]

files_modified:
  - src/python/pairwise_completeness_scan.py
  - tests/m3/test_pairwise_completeness_scan.py
  - .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
  - .planning/HANDOFF.json
  - .planning/STATE.md
  - .planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-PLAN.md
  - .planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-SUMMARY.md

autonomous: true

requirements:
  - PCS-BED-READER-FAIL-CLOSED
  - PCS-CANDIDATE-ENUMERATION-BOTH-SIDES
  - PCS-PAIRWISE-PROPERTY-DIRECT
  - PCS-GRADIENT-PARTIAL-CONFOUNDING
  - PCS-CLI-EGRESS-CLEAN-SUMMARY
  - PCS-PENDING-PASTE-00057-CROSSCHECK
  - PCS-FROZEN-SURFACES-UNCHANGED
  - PCS-SUITE-REBASELINE

user_setup: []

must_haves:
  truths:
    - "The new module exists and NEVER re-declares the frozen `.bim` column indices: `grep -c '_COL_BP *=' src/python/pairwise_completeness_scan.py` == 0 AND the same is true for `_COL_CHR`/`_COL_ID`/`_COL_ALT`/`_COL_REF`, while `grep -c 'occlusion_span_filter' src/python/pairwise_completeness_scan.py` >= 1 — the constants, `parse_bim_row`, `load_bim_rows` and the `_Variant.span_end` / `is_deletion` semantics are IMPORTED from the frozen module, never forked. A test asserts a DISCRIMINATING identity on the frozen import surface — `pcs.parse_bim_row is osf.parse_bim_row` and `pcs.load_bim_rows is osf.load_bim_rows` (FUNCTIONS are never interned across modules, so this genuinely fails if the executor forks them). Do NOT use `pcs._COL_REF is osf._COL_REF`: CPython interns small ints (-5..256), so two INDEPENDENTLY declared `_COL_REF = 5` also satisfy `is` (verified empirically 2026-08-25) — a FALSE INVARIANT that passes on a fork. The authoritative enforcer for the constants stays the textual `grep -c '_COL_BP *='` == 0 guard."
    - "Nothing on the fire path or the public record moved: `git diff --stat 7b59721 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/` is EMPTY, and the amendment's marker-exclusive paste block is still 22945 B / md5 `13a49f543cabcc27ce9f1e589783c060` at every commit. This task adds an INSTRUMENT; it changes no criterion, no producer, no verifier."
    - "The module implements THE PROPERTY, stated directly, never a proxy: for a pair (X, Y) `undefined` is computed as `X is constant within called(X) ∩ called(Y)` OR `Y is constant within it` (empty intersection included as the degenerate true case). `carriers(X) ⊆ missing(Y)` appears in the code ONLY as a derived diagnostic label (`confounding_pattern`), never as the primary test — enforced by a test that constructs a pair which IS undefined but is NOT a carriers-subset-of-missing case (the non-deletion member collapses) and asserts the detector still reports `undefined=True`."
    - "The `.bed` decoder is FAIL-CLOSED on every structural error, and each raise was SEEN RED before it existed: bad magic bytes RAISE, individual-major mode (`0x00`) RAISES, and a file whose size != `3 + n_variants * bytes_per_variant` RAISES (truncated AND over-long both tested). Three distinct tests, three pasted reds. A silent byte-order or mode mistake here would corrupt every downstream number, so none of the three may be a warning."
    - "Padding bits cannot manufacture a phantom sample: with `n_samples % 4 != 0`, two fixtures identical except for the value of the trailing padding bits in each variant's last byte decode to BYTE-IDENTICAL dosage arrays of length exactly `n_samples` — a must-be-identity comparison (`np.array_equal`), not a tolerance. Seen red by an implementation that reshapes without truncating to `n_samples`."
    - "Seek-by-index is real: a multi-variant fixture whose variants are mutually distinguishable (variant 0 all hom-A1, variant 1 all het, variant 2 all hom-A2) is read correctly at every index, and the test was seen RED against a perturbed offset formula (`3 + i*(bpv+1)`) — a reader that always returns block 0 must FAIL."
    - "The confirmed real case reproduces synthetically and is LABELLED as mirroring a measurement, not as derived truth: a 1/10-scale mirror of the measured `m2_region_00057` joint-callability table yields `undefined=True`, `invariant_member == \"deletion\"`, `partner_invariant == False`, and hand-computed `n_both_called` / `del_carriers_lost` / `del_carriers_lost_frac == 1.0` / marginal MAF ≈ 0.600%. The test name and docstring both carry `MIRRORS_A_MEASURED_CASE`, and the docstring cites `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md` §MECHANISM CONFIRMED as the provenance rather than re-deriving it."
    - "The NaN check's BLIND SPOT is instrumented and visible: the identical fixture with a handful of carriers retained returns `undefined == False` (plink would compute a finite `r`) while the gradient fields report `del_carriers_lost == 82 of 87`, `del_carriers_lost_frac ≈ 0.9425`, and the region summary counts that pair in its `carriers_lost_frac >= 0.9 AND defined` tail bin. Without this row the pipeline has no instrument that can see a biased-subsample correlation at all."
    - "Both members are tested, in both directions: a case where the NON-deletion member is the invariant one reports `invariant_member == \"partner\"`, and the empty-intersection case reports `undefined=True` with `n_both_called == 0` and `invariant_member == \"both\"`."
    - "Offsets are swept on BOTH sides under ONE stated signed convention: `span_offset` is the SIGNED DISTANCE from the deletion's REF interval `[pos, span_end]` — negative upstream of `pos`, `0` anywhere inside the interval (both ends inclusive), positive past `span_end` — documented in the module docstring and pinned by a test. An upstream partner is enumerated with a NEGATIVE offset; an interior partner is flagged `already_occluded=True` under the POSTED rule `d.pos < v.pos <= d.span_end`; a CO-LOCATED partner (`v.pos == d.pos`) has `offset == 0` but `already_occluded == False` (the posted rule's strict left bound), so `offset == 0` and `already_occluded` are provably NOT the same predicate."
    - "The window is a MEASUREMENT PARAMETER with an exact boundary: with `--window-bp K`, a partner at exactly `+K` past `span_end` and one at exactly `-K` before `pos` are BOTH included, and partners at `+(K+1)` / `-(K+1)` are BOTH excluded. Default K is 25 and is stated in the docstring as a measurement window, never a threshold."
    - "The module refuses a loose window `.bim` BY CONSTRUCTION, and the reason is pinned by a negative control: the scanner takes a `--bfile-prefix` and streams the prefix's OWN `.bim` to derive GLOBAL 0-based variant indices, because a pre-extracted window `.bim` carries window-relative indices that would silently read the WRONG `.bed` blocks. A test demonstrates that exact corruption (reading global index 0 for what is actually row 5 returns a different, wrong genotype vector) and a second test proves `BedReader` RAISES when its `.bim`/`.fam` line counts disagree with the `.bed` file size."
    - "The output is EGRESS-CLEAN and pinned: `TSV_COLUMNS` is a module constant compared for EXACT tuple equality against a hand-written tuple in the test; no column name contains `sample`/`iid`/`fid`; every emitted field is a scalar whose rendered length is <= 64 chars; and the `--summary` JSON's key set is pinned by exact equality. A negative control adds a per-sample field to a copy of the row dict and shows the egress test FAILS."
    - "The summary answers the three OPEN questions the halt record names, per region: `n_undefined_distinct_pairs`, `n_undefined_not_already_occluded` (the newly-discovered class — 'already covered' is separated from 'new'), the OFFSET HISTOGRAM of the undefined set (which is what supplies the empirical boundary width instead of a guess), and the `carriers_lost_frac` distribution over DEFINED pairs (which is what would surface a partial-confounding tail). It reports counts and fractions only — never a rate inferred from one region."
    - "The PENDING PASTE exists at `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` in the `260819-PENDING-PASTE-3` house style and carries a harness cross-check that DISCARDS ALL RESULTS on failure: `m2_region_00057` must reproduce `chr15:20394741:AT:A` x `chr15:20394743:T:C` with `undefined=True`, `offset == 1`, `n_both_called == 71048`, `del_carriers_lost == 871` — `grep -c 71048` >= 1 and `grep -c 871` >= 1 and `grep -c 20394741` >= 1 in that file. It runs the 00057 cross-check as STEP 1, ALONE, before the 21-region sweep, and states that a failure means STOP and paste, never adjust."
    - "The paste cannot be run against stale code: its STEP 0 is `git fetch && git checkout m3-W2-aou-deltas && git pull --ff-only && git log -1 --oneline` with the SHA pasted back plus `ls -l src/python/pairwise_completeness_scan.py`, and the file states that NCSU must be pushed FIRST (the banked `feedback_push_ncsu_before_aou_clone_fire` failure mode). It also states: the VM must be STARTED by Carter and STOPPED after; `export PATH=\"$HOME/bin:$PATH\"` is per-shell (and that THIS sweep needs no plink at all, so that export is not on its critical path); aggregate counts only cross back, the full per-pair TSV stays in-perimeter under `/home/jupyter/occ_measure/`; and an agent never fires anything billable without Carter's go."
    - "NOTHING WAS FIRED and nothing was measured in-perimeter by this task: zero VM / Dataproc / OSF / `gsutil` / `gcloud` contact, the paste is WRITTEN and NOT RUN, and no prevalence number, boundary width, or criterion change appears anywhere in the deliverables. The three OPEN questions stay OPEN, by design."
    - "The suite is re-baselined honestly: `tests/m3` reports 0 FAILED at EVERY commit, the skip count STAYS at 33 (every new test is pure-synthetic and gate-free — a new test landing as a SKIP is not evidence), and the SUMMARY reconciles the move from the 1021 passed / 33 skipped / 0 failed baseline (measured 2026-08-22 at 14e62eb, re-measured at 7b59721 as 1054 collected) COMPONENT-EXACT: every added test named, arithmetic shown, `1021 + N == new_passed` and `1054 + N == new_collected`. The corrected counts land in `.planning/HANDOFF.json` `suite_baselines[\"tests/m3\"]` (CORRECTED, not appended to)."
    - "The branch is published: after the final task `git status -sb` shows no `ahead`, and every commit staged EXPLICIT paths (never `git add .` / `-A` on the shared GPFS tree)."
  artifacts:
    - path: "src/python/pairwise_completeness_scan.py"
      provides: "The instrument: a fail-closed seek-by-index plink1 .bed reader, both-sides candidate enumeration off the frozen .bim semantics, the direct pairwise-invariance test, the carriers-lost gradient, an egress-clean TSV writer and a per-region summary rollup + CLI"
      contains: "TSV_COLUMNS"
      min_lines: 400
    - path: "tests/m3/test_pairwise_completeness_scan.py"
      provides: "The RED-first suite: decoder codes/padding/seek/3 raises, the MIRRORS_A_MEASURED_CASE 00057 reproduction, the partial-confounding DEFINED blind-spot case, both-members, empty intersection, both-side offsets, the +/-K boundary, the window-relative-index corruption negative control, and the egress pins"
      contains: "MIRRORS_A_MEASURED_CASE"
      min_lines: 500
    - path: ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md"
      provides: "The in-perimeter block for the AoU browser agent — STEP 0 pull-and-report, STEP 1 the 00057 harness cross-check alone (71048 / 871 / offset +1 or DISCARD ALL), STEP 2 the 21-region sweep, aggregate-counts-only egress, VM start/stop and never-fires rules"
      contains: "71048"
      min_lines: 80
    - path: ".planning/HANDOFF.json"
      provides: "The corrected tests/m3 suite baseline + a resume entry naming the instrument as BUILT-AND-UNRUN and the three questions as still OPEN"
      contains: "pairwise_completeness_scan"
  key_links:
    - from: "src/python/occlusion_span_filter.py (_COL_* / parse_bim_row / load_bim_rows / _Variant.span_end / is_deletion)"
      to: "src/python/pairwise_completeness_scan.py"
      via: "import binding — the SAME objects, never a second declaration of the .bim column indices; a test asserts object identity"
      pattern: "from occlusion_span_filter import"
    - from: "the plink1 .bed byte layout (magic 6c 1b, mode 01, bytes_per_variant = (n_samples+3)//4, variant i at 3 + i*bpv, 2-bit codes packed LOW-to-HIGH)"
      to: "BedReader.read_variant"
      via: "seek(3 + index*bpv) + read(bpv) — ONLY the candidate variants' blocks are ever read, never the ~354 GB file"
      pattern: "3 \\+ index \\* self.bytes_per_variant"
    - from: "the measured m2_region_00057 joint-callability table (.planning/debug/260824-STAGE-B-HALT-...md §MECHANISM CONFIRMED)"
      to: "tests/m3/test_pairwise_completeness_scan.py MIRRORS_A_MEASURED_CASE fixture"
      via: "1/10-scale mirror of the seven joint cells; the measurement is CITED, never re-derived, and the label keeps measured apart from derived"
      pattern: "MIRRORS_A_MEASURED_CASE"
    - from: "src/python/pairwise_completeness_scan.py (the module the sweep runs)"
      to: ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md"
      via: "STEP 0 pulls the pushed branch and reports the SHA; STEP 1 cross-checks 00057 against 71048 / 871 / offset +1 or discards everything"
      pattern: "71048"
---

<objective>
Build the INSTRUMENT that can measure what the Stage B halt left OPEN — and build nothing
else.

The halt's mechanism is CONFIRMED: `chr15:20394741:AT:A` (a 1 bp deletion) and
`chr15:20394743:T:C` (a SNP one base past its REF span) are perfectly confounded — 0 of 871
deletion carriers are called at the SNP — so within the 71,048 samples called at both, the
deletion is invariant, plink writes `0/0` -> NaN, and its marginal MAF is a healthy 0.601%.
The pre-registered occlusion criterion tests REF-span OVERLAP and correctly declined to
exclude the pair.

Three things are UNKNOWN and CANNOT be inferred from n=1 — the prevalence, the true boundary
width (and whether it is one-sided), and whether a partial-confounding tail exists. Inferring
any of them from this one pair is EXACTLY the error that produced the withdrawn `0.0005`
constant. This task builds the measuring device. It does NOT answer the questions.

Purpose: give the project a genotype-only detector of the ACTUAL property — "within
`called(X) ∩ called(Y)`, X or Y is constant" — that reads only candidate variants' `.bed`
blocks (no `--r`, no 42 GB matrices, no LD recompute), records the SIGNED OFFSET on BOTH
sides so the data reveals the boundary width, and records the CARRIERS-LOST GRADIENT so the
partial-confounding tail (a finite `r` on a carrier-depleted subsample, which no NaN check
anywhere catches) becomes visible for the first time.

Output: one new module + its RED-first test suite + one in-perimeter PENDING PASTE +
a reconciled suite baseline + a pushed branch.

EXPLICITLY OUT OF SCOPE, and any of these appearing is a plan violation:
  * ANY change to `occlusion_span_filter.py`, `run_native_ld_panel.py`, `fire_verifier.py`
  * ANY criterion, threshold, span-widening or NaN-policy change
  * ANY prevalence / boundary-width / tail number stated as a result
  * RUNNING the paste, or any VM / Dataproc / OSF / `gsutil` / `gcloud` contact

NO FIRE. $0. An agent never fires.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md
@.planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md
@src/python/occlusion_span_filter.py
@tests/m3/test_occlusion_span_filter.py
@tests/m3/conftest.py

<measured_facts>
<!-- Read-only measurements taken at HEAD 7b59721 during planning. Do not re-derive; DO re-verify. -->

PYTHON (never miniconda base):
  PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
  -> Python 3.11.15 (conda-forge), numpy 2.4.4.  MEASURED.

BASE SHA for every `git diff --stat` guard in this plan: 7b59721
BRANCH: m3-W2-aou-deltas (tracking origin/m3-W2-aou-deltas, currently NOT ahead)

SUITE BASELINE (tests/m3): 1021 passed / 33 skipped / 0 failed; 1054 collected.
  Re-measured at 7b59721 during planning: `--collect-only` = 1054 collected in 14.23 s.
  Full run ~13-14 min. Use `-q -rs`. `pytest tests` AS ONE INVOCATION DOES NOT COLLECT
  (tests/m2/conftest.py shadows tests/m3/conftest.py) — run sub-suites separately.
  Skips must STAY at 33.

FROZEN-SURFACE GUARD (run at the START and END of every task):
  git diff --stat 7b59721 HEAD -- \
    src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py \
    src/python/fire_verifier.py .planning/amendments/ | wc -l    # MUST be 0

AMENDMENT PASTE-BLOCK GUARD — ⚠ USE THIS EXACT FORM:
  A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
  awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb.txt
  wc -c < /tmp/pb.txt        # MUST be 22945   (SIZE FIRST — 260817-vbu house order)
  md5sum /tmp/pb.txt         # MUST be 13a49f543cabcc27ce9f1e589783c060
  ⚠ TRAP MEASURED DURING PLANNING: the older one-liner
  `awk ... "$A" | tee >(wc -c) | md5sum` is RACY — process substitution interleaves into
  md5sum's stdin and it printed 2f2e9548e1b2952ac802a847ea5dff40 on an UNCHANGED file.
  Markers verified at lines 167 and 501. Do NOT chase that phantom; use the file form.

FROZEN SYMBOLS TO IMPORT (occlusion_span_filter.py — byte-unchanged at 7b59721):
  _COL_CHR = 0 · _COL_ID = 1 · _COL_BP = 3 · _COL_ALT = 4 (A1=ALT) · _COL_REF = 5 (A2=REF)
  parse_bim_row(row, *, index=0) -> _Variant(index, vid, pos, ref_len)
      _Variant.span_end  == pos + ref_len - 1
      _Variant.is_deletion == ref_len > 1
      RAISES ValueError on <6 fields / non-integer bp / empty REF — loud, never silent.
  load_bim_rows(bim_path) -> list[list[str]]   (splits, keeps parts[:6], skips blanks)
  detect_occluded_variants(rows) -> (sorted_unique_ids, edges)
  THE POSTED OCCLUSION RULE (do not restate it as anything else):
      V occluded iff exists D with len(REF_D) > 1 and  d.pos < v.pos <= d.span_end
  ⚠ The `.bim` id convention is chr:pos:REF:ALT == chr:bp:A2:A1.

THE MEASURED 00057 CASE (halt record §MECHANISM CONFIRMED, lines 150-189 — CITE, never re-derive):
  pair: chr15:20394741:AT:A  (ref_len 2 -> span_end 20394742)  x  chr15:20394743:T:C
  offset = +1 past span_end.  Cohort .fam total 73,122 (the joint table sums to it exactly).
  joint (A,B) dosage cells incl NA:
      ('0','0') 70232 · ('0','NA') 570 · ('0','1') 816 · ('1','NA') 871
      ('NA','NA') 598 · ('NA','1') 14 · ('NA','0') 21
  n_both_called            = 70232 + 816 = 71048
  A carriers CALLED at B   = 0 of 871           <- perfect confounding; ('1','0')/('1','1') ABSENT
  A within intersection    = constant 0         -> undefined
  B within intersection    = 70232 ref / 816 het -> B is VARIABLE; only A collapses
  A marginal AF            = 871 / (2 * 72489) = 0.601%
  A called = 71618 + 871 = 72489 (hom-ref 71618, het 871, NA 633; NO hom carriers)

REGION-1 NEGATIVE CONTROL (Stage A, banked): 102,421 in-window rows, 7,951 multi-base-REF
  rows, 231 occluded, 38,595,391,746 bytes re-read, ZERO NaN. Deletion-boundary adjacency is
  NECESSARY-AT-MOST, NOT SUFFICIENT. ⚠ It establishes only that region 1 held no PERFECTLY
  confounded pair — NOT that it is free of deletion-linked missingness bias.

PLINK1 .bed BYTE LAYOUT (the contract the reader must enforce):
  bytes 0-1 magic 0x6c 0x1b · byte 2 mode: 0x01 = SNP-major (variant-major), 0x00 = individual-major
  bytes_per_variant = (n_samples + 3) // 4 ; variant i block starts at 3 + i*bytes_per_variant
  within a byte: FOUR samples, sample with the LOWEST index in the LOW-order 2 bits (bits 0-1)
  2-bit codes: 00 = hom-A1 · 01 = MISSING · 10 = het · 11 = hom-A2
  dosage of A1: 00 -> 2 · 10 -> 1 · 11 -> 0 · 01 -> missing
  trailing bits of the last byte of each variant block are PADDING when n_samples % 4 != 0
  expected file size = 3 + n_variants * bytes_per_variant

SIZING (why this is minutes, not days):
  73,122 samples -> bytes_per_variant = 18,281. A ~6,000-candidate region reads ~110 MB.
  Region 1: ~7,951 deletions x ~7.6 variants/kb over a ~220 bp window -> ~13k candidate rows
  over ~21k distinct variants -> ~385 MB of seeks. The ~354 GB .bed is NEVER read whole.

IN-PERIMETER PATHS (for the PENDING PASTE only — this task does not touch them):
  bfile prefix        /home/jupyter/afr_cohort           (.bed/.bim/.fam)
  pre-committed sample /home/jupyter/occ_measure/occ_measure_sample.tsv  (21 regions, header + rows,
                       region_id in column 1 — the SAME sample as the row-basis and site-basis sweeps)
  repo on VM          ~/coloc_analysis   (branch m3-W2-aou-deltas)
  region manifest     config/ld_regions.tsv — 1-based cols: 1 region_id · 2 chr ·
                       15 window_start_grch38 · 16 window_end_grch38  (0-based 0/1/14/15)
  R6 occ_measure/ allowance applies. Aggregate counts only cross back.
</measured_facts>

<interfaces>
<!-- The contracts the executor builds TO. No codebase exploration required. -->

FROM src/python/occlusion_span_filter.py (FROZEN — import, never fork):

```python
_COL_CHR = 0
_COL_ID  = 1
_COL_BP  = 3
_COL_ALT = 4  # A1
_COL_REF = 5  # A2 — its LENGTH is the reference footprint

class _Variant(NamedTuple):
    index: int; vid: str; pos: int; ref_len: int
    @property
    def span_end(self) -> int: ...       # pos + ref_len - 1
    @property
    def is_deletion(self) -> bool: ...   # ref_len > 1

def parse_bim_row(row: Sequence, *, index: int = 0) -> _Variant: ...
def load_bim_rows(bim_path: "str | Path") -> list[list[str]]: ...
```

NEW PUBLIC SURFACE of src/python/pairwise_completeness_scan.py (build exactly this):

```python
MISSING_DOSAGE: int = -1
BED_MAGIC: bytes = b"\x6c\x1b"
BED_MODE_SNP_MAJOR: int = 0x01
BED_MODE_INDIVIDUAL_MAJOR: int = 0x00
DEFAULT_WINDOW_BP: int = 25            # a MEASUREMENT window, never a threshold
TSV_COLUMNS: tuple[str, ...]           # pinned by exact tuple equality in the test
SUMMARY_KEYS: tuple[str, ...]          # pinned by exact set equality in the test

class Genotypes(NamedTuple):
    dosage: "np.ndarray"               # int8, len == n_samples, MISSING_DOSAGE where no-call
    @property
    def called(self) -> "np.ndarray": ...   # bool, dosage >= 0

class BedReader:
    """Seek-by-index plink1 .bed reader. Reads ONLY the blocks asked for."""
    def __init__(self, bfile_prefix, *, cache_variants: int = 2048) -> None: ...
    n_samples: int; n_variants: int; bytes_per_variant: int
    def read_variant(self, index: int) -> Genotypes: ...   # GLOBAL 0-based .bim row index
    def close(self) -> None: ...

class CandidatePair(NamedTuple):
    region_id: str
    del_index: int; del_vid: str; del_chr: str; del_pos: int
    del_ref_len: int; del_span_end: int
    partner_index: int; partner_vid: str; partner_pos: int
    offset: int; side: str                 # "upstream" | "interior" | "downstream"
    already_occluded: bool                 # POSTED rule: d.pos < v.pos <= d.span_end
    pair_key: str                          # "|".join(sorted((del_vid, partner_vid)))

class PairResult(NamedTuple):
    # the CandidatePair fields, plus:
    n_called_del: int; n_called_partner: int; n_both_called: int
    del_invariant: bool; partner_invariant: bool; undefined: bool
    invariant_member: str                  # "deletion" | "partner" | "both" | "none"
    del_carriers_marginal: int; del_carriers_retained: int
    del_carriers_lost: int; del_carriers_lost_frac: float; del_maf_marginal: float
    partner_carriers_marginal: int; partner_carriers_retained: int
    partner_carriers_lost: int; partner_carriers_lost_frac: float; partner_maf_marginal: float
    confounding_pattern: str               # DERIVED LABEL ONLY, never the test

def span_offset(deletion: "_Variant", variant: "_Variant") -> int: ...
def enumerate_candidates(region_id, indexed_rows, *, window_bp=DEFAULT_WINDOW_BP) -> list[CandidatePair]: ...
def evaluate_pair(reader: BedReader, pair: CandidatePair) -> PairResult: ...
def iter_bim_windows(bim_path, windows) -> dict[str, list[tuple[int, list[str]]]]: ...
    # ONE streaming pass over the FULL .bim; values are (GLOBAL 0-based index, 6-field row)
def scan_region(reader, region_id, indexed_rows, *, window_bp) -> list[PairResult]: ...
def write_tsv(results, path) -> None: ...
def summarize(region_id, results) -> dict: ...
def main(argv: "list[str] | None" = None) -> int: ...
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: The fail-closed seek-by-index plink1 .bed reader (RED -> GREEN)</name>
  <files>src/python/pairwise_completeness_scan.py, tests/m3/test_pairwise_completeness_scan.py</files>
  <behavior>
    RED FIRST, every assertion written before the code that satisfies it. Paste each red
    verbatim in the SUMMARY. A green assertion that was never seen fail is not evidence
    (`feedback_green_assertion_needs_a_negative_control`).

    FIXTURE BUILDER (write it first; it is the thing every later test stands on):
      `_write_bfile(tmp_path, *, codes_per_variant, n_samples, mode=0x01, magic=b"\x6c\x1b",
                    pad_bits=0b00, bim_rows=None, truncate_bytes=0, extra_bytes=0)`
      packs 2-bit codes LOW-to-HIGH within each byte, writes `.bed` (magic + mode + blocks),
      a matching `.bim` (6 fields, chr:pos:REF:ALT ids) and a `.fam` of `n_samples` lines.
      `pad_bits` fills the unused trailing bit-pairs of each block's last byte.

    DECODER TESTS (each its own test function):
      - all four codes decode correctly: 00 -> dosage 2, 10 -> 1, 11 -> 0, 01 -> MISSING_DOSAGE,
        and `called` is False exactly at the 01 positions. A single 4-sample variant carrying
        one of each code, asserted element-wise.
      - LOW-to-HIGH packing is the pinned direction: a byte whose bit-pairs are 00,01,10,11
        (low to high) decodes to samples [2, MISSING, 1, 0] IN THAT ORDER. Seen red against a
        high-to-low implementation.
      - n_samples % 4 == 0: exact length, no truncation surprise.
      - PADDING (n_samples = 5 or 7, i.e. % 4 != 0): TWO fixtures identical except
        `pad_bits=0b00` vs `pad_bits=0b11`, asserted `np.array_equal(a.dosage, b.dosage)` AND
        `len(dosage) == n_samples`. A pad_bits=0b11 phantom would decode as dosage 0
        (hom-A2) and lengthen the array — that is exactly the red to observe first.
      - SEEK: a 3-variant fixture, variant 0 all-`00`, variant 1 all-`10`, variant 2 all-`11`
        -> `read_variant(i)` returns all-2 / all-1 / all-0 respectively. Seen red against a
        perturbed offset (`3 + i*(bpv+1)`) AND against a stuck reader that always returns
        block 0. Both perturbations pasted.
      - RAISE 1 — bad magic (`b"\x00\x00"`) -> ValueError naming the observed bytes.
      - RAISE 2 — individual-major mode byte `0x00` -> ValueError naming the mode.
      - RAISE 3a — truncated file (`truncate_bytes=1`) -> ValueError naming expected vs actual size.
      - RAISE 3b — over-long file (`extra_bytes=1`) -> ValueError. Size is `==`, never `>=`.
      - RAISE 4 — `.bim` line count disagrees with the `.bed` size (e.g. a `.bim` with one
        extra row) -> ValueError. This is the guard that makes a mismatched bfile loud.
      - out-of-range index (`n_variants`, and `-1`) -> IndexError/ValueError, not a silent read.
      - THE WINDOW-RELATIVE-INDEX CORRUPTION negative control (a documentation test):
        build a 6-variant fixture whose blocks are mutually distinguishable, show that
        `read_variant(0)` returns block 0 and NOT block 5, and assert the two differ — i.e.
        handing a window-relative index to a global reader silently returns the WRONG
        genotypes. Docstring states this is WHY the module refuses a loose window `.bim`.
      - the reader does not slurp: after constructing `BedReader` on a fixture, assert no
        attribute holds an array of length `n_variants * n_samples` (a cheap structural
        assertion that the ~354 GB file is never materialized).

    MEMORY BOUND (state it, do not exceed it): the decode cache holds int8 dosage ONLY
    (`called` is derived on access), so the bound is `cache_variants * n_samples` bytes —
    2048 * 73,122 ~= 150 MB at production scale. Add a test that the cache evicts (LRU) and
    that `cache_variants=1` still returns correct results for an alternating read pattern
    (`feedback_dense_matrix_verify_memory_bounded`: never let a verify materialize unboundedly).
  </behavior>
  <action>
Guard first: run the FROZEN-SURFACE guard and the AMENDMENT PASTE-BLOCK guard from
`<measured_facts>` (file form, size then md5). Abort if either moves.

1. Create `tests/m3/test_pairwise_completeness_scan.py` with the `tests/m3` header conventions
   copied from `tests/m3/test_occlusion_span_filter.py`:
     `PROJECT_ROOT = Path(__file__).resolve().parents[2]`
     `sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))`
   Import the module under test INSIDE each test body (the house pattern that keeps the file
   COLLECTABLE while the module does not exist, so the red is a test failure, not a collection
   error). Write `_write_bfile` plus every decoder test above. Run it — every test MUST fail on
   `ModuleNotFoundError`. Paste the red.

2. Create `src/python/pairwise_completeness_scan.py`. Module docstring must state, in this order:
     * WHAT PROPERTY THIS DETECTS, verbatim and first: "for a pair (X, Y), plink's `r` is
       undefined iff, within `called(X) ∩ called(Y)`, X is constant or Y is constant (the empty
       intersection included)". Then, explicitly: "`carriers(X) ⊆ missing(Y)` is ONE SUFFICIENT
       SPECIAL CASE of that condition and is NEVER the test — it appears only as the derived
       `confounding_pattern` label."
     * WHY IT EXISTS: the CONFIRMED m2_region_00057 mechanism, cited to
       `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`
       (0 of 871 carriers called at the partner; intersection 71,048; marginal MAF 0.601%),
       and the SECOND-ORDER consequence in one sentence: partial confounding yields a FINITE
       `r` on a carrier-depleted subsample that NO NaN check anywhere catches.
     * WHAT IT IS NOT: it changes no criterion, no threshold, no policy; it states no
       prevalence; the prevalence, the boundary width and the tail are OPEN and are settled
       ONLY by running it in-perimeter over the pre-committed sample. n=1 supplies none of them.
     * THE .bed BYTE CONTRACT, verbatim from `<measured_facts>`, plus: "a byte-order or mode
       mistake here silently corrupts every downstream number, so every structural check RAISES."
     * THE GLOBAL-INDEX RULE: the scanner takes a `bfile_prefix` and streams that prefix's OWN
       `.bim`, because a pre-extracted window `.bim` carries WINDOW-RELATIVE indices that would
       silently read the wrong `.bed` blocks. Name the negative control test that pins it.
   Then import from the frozen module — `from occlusion_span_filter import (_COL_CHR, _COL_ID,
   _COL_BP, _COL_ALT, _COL_REF, parse_bim_row, load_bim_rows)` — with a one-line comment: "its
   OWN .bim column indices (never a 2nd copy)". DECLARE NO COLUMN INDEX IN THIS FILE.

3. Implement `MISSING_DOSAGE`, `BED_MAGIC`, `BED_MODE_*`, `Genotypes` and `BedReader` ONLY.
   Decode with a vectorised shift-and-mask (`(block[:, None] >> [0,2,4,6]) & 3`), ravel, then
   TRUNCATE to `n_samples` — the truncation IS the padding fix. Map codes through a 4-entry
   int8 lookup `[2, MISSING_DOSAGE, 1, 0]`. `n_samples` from the `.fam` line count, `n_variants`
   from the `.bim` line count; validate magic, then mode, then size, then index bounds — in
   that order, each with its own message. Bounded LRU decode cache (`collections.OrderedDict`).

4. Re-run the test file — GREEN. Then run the perturbation negative controls (high-to-low packing; `3 + i*(bpv+1)`; reshape-without-truncate; AND a reader hardcoded to always seek block 0 -- the 4th perturbation `<behavior>` requires for the SEEK test, so all four reds are executed and pasted) one at a time in a `tmp_path` scratch
   COPY of the module — NEVER in-tree — and paste each observed red. ⚠ Between perturbation and
   revert, use a fresh interpreter or `importlib.invalidate_caches()`: a byte-length-identical
   edit reverted within the same second runs STALE bytecode
   (`feedback_negative_control_defeated_by_bytecode_cache`).

5. Run the full `tests/m3` for this task's file only plus a fast sanity sweep of the neighbours:
   `$PY -m pytest tests/m3/test_pairwise_completeness_scan.py tests/m3/test_occlusion_span_filter.py -q`.
   Re-run both guards. Commit EXPLICIT paths only:
   `git add src/python/pairwise_completeness_scan.py tests/m3/test_pairwise_completeness_scan.py`
   Message: `feat(quick-260825-ngh): T1 — fail-closed seek-by-index plink1 .bed reader for the pairwise-completeness scanner`
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pairwise_completeness_scan.py tests/m3/test_occlusion_span_filter.py -q 2>&1 | tail -3 | grep -q "failed" && echo T1-FAIL && exit 1; test "$(grep -c '_COL_BP *=\|_COL_CHR *=\|_COL_ID *=\|_COL_ALT *=\|_COL_REF *=' src/python/pairwise_completeness_scan.py)" = 0 && grep -q 'occlusion_span_filter' src/python/pairwise_completeness_scan.py && test "$(git diff --stat 7b59721 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/ | wc -l)" = 0 && A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md && awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb_t1.txt && test "$(wc -c < /tmp/pb_t1.txt)" = 22945 && md5sum /tmp/pb_t1.txt | grep -q 13a49f543cabcc27ce9f1e589783c060 && echo T1-VERIFY-OK</automated>
  </verify>
  <done>`BedReader` decodes all four 2-bit codes LOW-to-HIGH, seeks correctly by GLOBAL index,
truncates padding so `n_samples % 4 != 0` cannot yield a phantom sample, and RAISES on bad
magic / individual-major / wrong file size (both directions) / `.bim`-count mismatch / bad
index. Every one of those was OBSERVED RED first and the reds are pasted in the SUMMARY. The
module declares ZERO `.bim` column indices of its own and imports them from the frozen module.
Frozen surfaces and the amendment paste block are byte-unchanged. One explicit-path commit.
`tests/m3` has 0 failed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Candidate enumeration (both sides, one signed convention) + the direct pairwise test + the carriers-lost gradient (RED -> GREEN)</name>
  <files>src/python/pairwise_completeness_scan.py, tests/m3/test_pairwise_completeness_scan.py</files>
  <behavior>
    RED FIRST for every assertion. This task contains the science; it must not contain a proxy.

    THE SIGNED OFFSET CONVENTION — pick it, state it once, pin it:
      `span_offset(D, V)` is the SIGNED DISTANCE from D's REF interval `[D.pos, D.span_end]`:
          V.pos <  D.pos       -> V.pos - D.pos        (NEGATIVE, "upstream")
          D.pos <= V.pos <= D.span_end -> 0            ("interior")
          V.pos >  D.span_end  -> V.pos - D.span_end   (POSITIVE, "downstream")
      Pinned by a table-driven test. The measured 00057 partner sits at offset +1.
      `already_occluded` is the POSTED rule and is COMPUTED SEPARATELY:
      `D.pos < V.pos <= D.span_end`. A CO-LOCATED partner (`V.pos == D.pos`) has offset 0 but
      `already_occluded == False` — a test asserts that offset==0 and already_occluded are NOT
      the same predicate, so "already covered" can never be silently conflated with "interior".

    ENUMERATION TESTS:
      - both sides: an upstream partner at `D.pos - 3` is EMITTED with offset -3 and
        side "upstream"; a downstream partner at `span_end + 3` with offset +3 / "downstream".
        (The posted rule is one-sided; alignment ambiguity at an indel is not directional.)
      - BOUNDARY of the measurement window K: partners at exactly `span_end + K` and exactly
        `D.pos - K` are INCLUDED; `span_end + K + 1` and `D.pos - K - 1` are EXCLUDED. `K=5`
        in the fixture; DEFAULT_WINDOW_BP is 25 and is asserted to be 25.
      - only `is_deletion` rows anchor candidates (an SNV or an INSERTION anchors nothing) —
        reuse the `_del_row` / `_snp_row` / `_ins_row` builders' shape from
        `tests/m3/test_occlusion_span_filter.py`.
      - self-pairs are never emitted (`del_index != partner_index`).
      - a deletion-deletion neighbour emits TWO ordered rows (one per anchor, with the two
        anchors' own offsets) but ONE distinct `pair_key`; a test asserts
        `len(rows) == 2 and len({r.pair_key for r in rows}) == 1`. Summary counts BOTH
        `n_candidate_rows` and `n_distinct_pairs` so neither can be quoted as the other.
      - unsorted input RAISES (binary-search windowing depends on position order) — fail-closed.
      - a partner on a different chromosome RAISES (a window is single-chromosome by contract).
      - `iter_bim_windows` does ONE streaming pass over the full `.bim` for N windows and
        returns GLOBAL 0-based indices; a test with 3 windows over a 20-row `.bim` asserts the
        exact global indices, and asserts the file was opened exactly once (monkeypatched
        `open` counter or `Path.read_text` guard).

    THE PAIRWISE TEST — the PROPERTY, directly:
      `both = called_del & called_partner`; `n_both_called = both.sum()`;
      `del_invariant  = n_both_called == 0 or np.unique(dosage_del[both]).size == 1`;
      `partner_invariant` symmetrically; `undefined = del_invariant or partner_invariant`.
      `invariant_member` in {"deletion", "partner", "both", "none"}.
      NO set-containment test anywhere on the primary path.

    THE GRADIENT (this is what surfaces the tail):
      minor allele determined EMPIRICALLY over each member's own CALLED set (A1 if
      `sum(dosage)/2/n_called <= 0.5` else A2); `carriers` = samples with >= 1 copy of that
      minor allele; then per member: `carriers_marginal` (over `called`), `carriers_retained`
      (over `both`), `carriers_lost = marginal - retained`, `carriers_lost_frac` (0.0 when
      marginal == 0), and `maf_marginal`.
      `confounding_pattern` is a DERIVED LABEL ONLY: "perfect_deletion_confounding" /
      "perfect_partner_confounding" / "partial" / "none" / "empty_intersection".

    THE CASES (each its own test):
      - `test_mirrors_a_measured_case_00057_perfect_confounding_MIRRORS_A_MEASURED_CASE`:
        a 1/10-scale mirror of the MEASURED joint table, n_samples = 7,313 (deliberately
        `% 4 == 1`, so this realistic fixture ALSO exercises padding):
            ('0','0') 7024 · ('0','NA') 57 · ('0','1') 82 · ('1','NA') 87
            ('NA','NA') 60 · ('NA','1') 1 · ('NA','0') 2      [sums to 7313 — assert it]
        expected, HAND-COMPUTED IN THE TEST BODY with the arithmetic shown as comments:
            n_both_called = 7024 + 82 = 7106
            del_invariant True, partner_invariant False, undefined True,
            invariant_member "deletion"
            n_called_del = 7024+57+82+87 = 7250; del_carriers_marginal = 87;
            del_carriers_retained = 0; del_carriers_lost = 87; lost_frac == 1.0;
            del_maf_marginal = 87/(2*7250) = 0.006 -> assert round(...,4) == 0.0060
            (the MEASURED marginal was 0.601% — assert the mirror lands within 0.01 pp and
            SAY that the agreement is a fixture property, not a rederivation)
            n_called_partner = 7024+82+1+2 = 7109; partner_carriers_marginal = 83;
            retained = 82; lost = 1; lost_frac = 1/83
            confounding_pattern == "perfect_deletion_confounding"
        The test NAME and DOCSTRING both carry `MIRRORS_A_MEASURED_CASE`; the docstring cites
        the halt record §MECHANISM CONFIRMED as provenance and states "this MIRRORS a
        measurement at 1/10 scale; it DERIVES nothing and establishes no prevalence."
      - `test_partial_confounding_is_DEFINED_and_the_gradient_sees_it`: the identical fixture
        with 5 of the 87 `('1','NA')` moved to `('1','0')`. Expect `undefined == False`
        (plink would return a FINITE r), `del_carriers_retained == 5`,
        `del_carriers_lost == 82`, `round(del_carriers_lost_frac, 4) == 0.9425`,
        `confounding_pattern == "partial"`. Docstring: "THIS IS THE BLIND SPOT — no NaN check
        anywhere in the pipeline fires on this row; the gradient is the only instrument that
        can see it."
      - `test_partner_is_the_invariant_member`: mirror-image construction ->
        `invariant_member == "partner"`, `del_invariant False`, `undefined True`.
      - `test_undefined_without_carriers_subset_of_missing`: an undefined pair that the
        `carriers(X) ⊆ missing(Y)` shortcut would MISS (e.g. the partner is invariant inside
        the intersection through a different missingness pattern) -> still `undefined True`.
        This is the test that proves the primary path is the property, not the shortcut.
      - `test_empty_intersection_is_undefined`: disjoint call sets -> `n_both_called == 0`,
        `undefined True`, `invariant_member == "both"`,
        `confounding_pattern == "empty_intersection"`.
      - `test_fully_defined_pair_has_zero_gradient`: a healthy pair -> `undefined False`,
        both `carriers_lost == 0`, both `lost_frac == 0.0`, pattern "none".
      - `test_lost_frac_one_implies_undefined`: property assertion over the constructed cases —
        `carriers_lost_frac == 1.0` for a member IMPLIES that member is invariant. Guards
        against a gradient that disagrees with the primary test.
  </behavior>
  <action>
Guards first (frozen surfaces + paste block, file form).

1. Extend `tests/m3/test_pairwise_completeness_scan.py` with the enumeration, offset, pairwise
   and gradient tests above, plus a `_joint_table_bfile(tmp_path, cells, ...)` builder that
   turns a 7-cell joint (deletion, partner) dosage/NA table into a 2-variant `.bed`/`.bim`/`.fam`
   at the right positions (deletion at 20394741 with REF "AT", partner at 20394743) so the
   fixture geometry MATCHES the measured pair's offset of +1. Run — RED. Paste it.

2. Implement `span_offset`, `enumerate_candidates` (sorted-position binary-search windowing —
   NOT an O(n^2) double loop; the region-1 scale is ~7,951 deletions x ~102k rows),
   `iter_bim_windows` (one streaming pass, `enumerate()` supplies the GLOBAL index),
   `evaluate_pair`, `PairResult`, `CandidatePair` and `scan_region`. Every variant read goes
   through `BedReader.read_variant`; nothing re-opens the `.bed`.

3. GREEN. Then the negative controls, each in a `tmp_path` scratch COPY of the module, each red
   pasted (fresh interpreter between them — bytecode-cache rule):
     (a) replace the primary test with `carriers(del) ⊆ missing(partner)` ->
         `test_undefined_without_carriers_subset_of_missing` must FAIL;
     (b) make the window one-sided (`offset >= 0` only) ->
         the upstream enumeration test must FAIL;
     (c) use `<` instead of `<=` at the window boundary -> the `+K` inclusion test must FAIL;
     (d) drop the empty-intersection branch -> that test must FAIL.

4. Re-run `$PY -m pytest tests/m3/test_pairwise_completeness_scan.py -q`. Re-run both guards.
   Commit EXPLICIT paths only (same two files).
   Message: `feat(quick-260825-ngh): T2 — both-sides candidate enumeration + the direct pairwise-invariance test + the carriers-lost gradient`
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3 | grep -q "failed" && echo T2-FAIL && exit 1; grep -q "MIRRORS_A_MEASURED_CASE" tests/m3/test_pairwise_completeness_scan.py && grep -q "partial_confounding_is_DEFINED" tests/m3/test_pairwise_completeness_scan.py && test "$(grep -c '_COL_BP *=\|_COL_CHR *=\|_COL_ID *=\|_COL_ALT *=\|_COL_REF *=' src/python/pairwise_completeness_scan.py)" = 0 && test "$(git diff --stat 7b59721 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/ | wc -l)" = 0 && echo T2-VERIFY-OK</automated>
  </verify>
  <done>`span_offset` implements ONE stated signed convention pinned by a table test; candidates
are enumerated on BOTH sides with an exact `+/-K` boundary and an `already_occluded` flag that is
provably a different predicate from `offset == 0`; the pairwise test is the PROPERTY (invariance
within the intersection), proved by a test the `carriers ⊆ missing` shortcut would fail; the
measured 00057 case reproduces at 1/10 scale under a `MIRRORS_A_MEASURED_CASE` label with
hand-computed oracles; the partial-confounding case returns `undefined == False` with a populated
gradient (82 of 87 lost, 0.9425). Four perturbation reds pasted. `tests/m3` 0 failed. One
explicit-path commit.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: CLI + egress-clean TSV/summary rollup + the in-perimeter PENDING PASTE (RED -> GREEN; the paste is WRITTEN, never run)</name>
  <files>src/python/pairwise_completeness_scan.py, tests/m3/test_pairwise_completeness_scan.py, .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md</files>
  <behavior>
    RED FIRST for the CLI/TSV/summary tests.

    TSV + SUMMARY TESTS:
      - `TSV_COLUMNS` is compared for EXACT TUPLE EQUALITY against a hand-written tuple in the
        test (a must-be-identity transform, not a subset check) — adding or reordering a column
        must break it.
      - EGRESS: no `TSV_COLUMNS` entry and no `SUMMARY_KEYS` entry contains `sample`, `iid`,
        `fid`, `id_list` or `dosage`; every field written for a real `PairResult` renders to a
        string of length <= 64; the header row written to disk equals `TSV_COLUMNS` exactly.
        NEGATIVE CONTROL: build a row dict with an added `sample_ids` field carrying an
        `n_samples`-long value, run the same egress assertion helper the green test uses, and
        OBSERVE IT FAIL. Paste that red.
      - the summary is a dict whose key set equals `SUMMARY_KEYS` exactly, containing at least:
        `region_id, window_bp, n_deletions, n_candidate_rows, n_distinct_pairs,
         n_undefined_rows, n_undefined_distinct_pairs, n_undefined_already_occluded,
         n_undefined_not_already_occluded, undefined_offset_histogram,
         defined_carriers_lost_frac_bins, max_carriers_lost_frac_defined,
         n_defined_lost_frac_ge_0p9`.
        `undefined_offset_histogram` is `{offset: count}` over the UNDEFINED set only — that is
        the thing that supplies the empirical boundary width instead of a guess.
        `defined_carriers_lost_frac_bins` covers `0`, `(0,0.25]`, `(0.25,0.5]`, `(0.5,0.9]`,
        `(0.9,0.99]`, `(0.99,1)` over DEFINED rows only — the partial-confounding tail.
      - a summary test over a small hand-built result list asserts EVERY number, including that
        an already-occluded interior undefined pair lands in `n_undefined_already_occluded` and
        NOT in `n_undefined_not_already_occluded` (the "already covered" vs "newly discovered"
        separation the sweep exists to make).
      - the summary contains NO rate, NO extrapolation, NO prevalence estimate — asserted by a
        key-set equality plus a test that no key name contains `rate`, `prevalence`, `estimate`
        or `ceiling`.

    CLI TESTS (`main(argv)` returning an int, exercised in `tmp_path` end-to-end on a synthetic
    bfile — no perimeter, no network):
      - single region: `--bfile-prefix P --region-id R --chr 15 --from-bp A --to-bp B
        --window-bp 5 --out T.tsv --summary S.json` writes both files, exit 0, and the TSV
        reproduces the T2 oracles for the mirrored 00057 pair.
      - multi region: `--regions-tsv config-shaped-file --region-ids r1,r2` does ONE `.bim`
        pass and writes one TSV with both regions plus one summary JSON keyed by region_id.
      - `--cache-variants 1` produces byte-identical TSV output to the default (a memory knob
        must not be a correctness knob) — `filecmp.cmp(..., shallow=False)`.
      - a missing `.bed`/`.bim`/`.fam` exits NON-ZERO with a message naming the missing path;
        it never writes a partial TSV.
      - `--help` exits 0 and mentions that `--window-bp` is a MEASUREMENT window.

    THE PENDING PASTE (a DOCUMENT — write it; DO NOT RUN IT):
      `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`, in the
      `260819-PENDING-PASTE-3-site-basis-sweep.md` house style: a short purpose header outside
      the markers, then `--- PASTE FROM HERE ---` / `--- PASTE ENDS HERE ---` around a
      self-contained block. Required content:
        STEP 0 — freshness: `cd ~/coloc_analysis && git fetch && git checkout m3-W2-aou-deltas
        && git pull --ff-only && git log -1 --oneline` plus
        `ls -l src/python/pairwise_completeness_scan.py`; paste the SHA back. State that NCSU
        must be pushed FIRST or the clone silently runs stale code.
        STEP 1 — THE HARNESS CROSS-CHECK, ALONE, BEFORE ANYTHING ELSE: run the scanner on
        `m2_region_00057` only and assert the known pair reproduces —
        `chr15:20394741:AT:A` x `chr15:20394743:T:C`, `undefined == True`, `offset == 1`,
        `n_both_called == 71048`, `del_carriers_lost == 871`. On ANY mismatch: STOP, paste
        verbatim, DISCARD ALL RESULTS, change nothing. (This mirrors the region-1 `231`
        cross-check that guarded the site-basis sweep.) Run it separately even if 00057 is
        already inside the 21-region sample.
        STEP 2 — the sweep over the pre-committed 21-region sample from
        `/home/jupyter/occ_measure/occ_measure_sample.tsv` against `/home/jupyter/afr_cohort`,
        window `--window-bp 25`, writing the full per-pair TSV to `/home/jupyter/occ_measure/`
        (IN-PERIMETER, stays there) and printing ONLY the per-region summary lines + the
        pooled offset histogram + the pooled lost-frac bins.
        EGRESS RULE, stated: aggregate counts, fractions, variant coordinates/ids only —
        NEVER per-sample data. Paste back the summary stdout verbatim plus
        `wc -l` on the TSV.
        OPERATIONAL NOTES: the VM must be STARTED by Carter and STOPPED after; every result is
        aggregate; `export PATH="$HOME/bin:$PATH"` is PER-SHELL (and note honestly that THIS
        sweep calls no plink at all, so that export is not on its critical path — it is listed
        because the shell is shared with the fire runbooks); an agent NEVER fires anything
        billable without Carter's explicit go; on ANY exception STOP and paste verbatim.
        WHAT THIS DOES NOT DECIDE, stated in the file: it produces MEASUREMENTS ONLY — no
        criterion change, no span widening, no NaN policy. Adjudication is a separate,
        pre-registration question and happens after the numbers exist.
      A test asserts the file exists and contains `71048`, `871`, `20394741`, `20394743`,
      `--- PASTE FROM HERE ---`, `--- PASTE ENDS HERE ---` and `occ_measure_sample.tsv`.
  </behavior>
  <action>
Guards first.

1. Extend the test file with the TSV/summary/CLI tests + the egress negative control. RED. Paste.

2. Implement `TSV_COLUMNS`, `SUMMARY_KEYS`, `write_tsv`, `summarize` and `main` in the module.
   `main` uses `argparse` in the `run_native_ld_panel.main` house shape (`--bfile-prefix`
   `dest="bfile_prefix"`, `type=Path` where a path is meant, an explicit `--window-bp` default
   of `DEFAULT_WINDOW_BP` whose help text says "MEASUREMENT window (bp) on BOTH sides of the
   deletion REF span — not a threshold"). Returns 0 on success, non-zero on a missing input.

3. GREEN. Write `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` per the
   spec above. ⚠ WRITE IT ONLY. No VM, no `gcloud`, no `gsutil`, no OSF, no billing. Verify the
   embedded commands are syntactically valid by `python -m py_compile` on the extracted block
   (a syntax check, NOT an execution) if the block is a heredoc'd script; if the block is a CLI
   invocation, `--help`-check the flags it uses against the shipped `main`.

4. Re-run the full test file. Re-run both guards. Commit EXPLICIT paths only:
   `git add src/python/pairwise_completeness_scan.py tests/m3/test_pairwise_completeness_scan.py .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`
   Message: `feat(quick-260825-ngh): T3 — egress-clean TSV/summary rollup + CLI + the 21-region PENDING PASTE (written, NOT run)`
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3 | grep -q "failed" && echo T3-FAIL && exit 1; P=.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md; test -f "$P" && grep -q 71048 "$P" && grep -q 871 "$P" && grep -q 20394741 "$P" && grep -q 'PASTE FROM HERE' "$P" && grep -q 'occ_measure_sample.tsv' "$P" && $PY src/python/pairwise_completeness_scan.py --help >/dev/null && test "$(git diff --stat 7b59721 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/ | wc -l)" = 0 && echo T3-VERIFY-OK</automated>
  </verify>
  <done>The CLI runs end-to-end on a synthetic bfile in `tmp_path` and reproduces the T2 oracles;
`--cache-variants 1` yields a byte-identical TSV (the memory knob is not a correctness knob);
`TSV_COLUMNS` and `SUMMARY_KEYS` are pinned by exact equality and pass an egress assertion whose
negative control was SEEN RED; the summary separates already-occluded from newly-discovered
undefined pairs, carries the undefined-set offset histogram and the defined-set lost-frac bins,
and contains no rate/prevalence/estimate key. The PENDING PASTE exists with the STEP 1 00057
cross-check (71048 / 871 / offset +1 or DISCARD ALL) and was NOT RUN — zero perimeter contact.
`tests/m3` 0 failed. One explicit-path commit.</done>
</task>

<task type="auto">
  <name>Task 4: Full-suite re-baseline reconciled component-exact + docs/handoff + push</name>
  <files>.planning/HANDOFF.json, .planning/STATE.md, .planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-SUMMARY.md</files>
  <action>
Guards first (frozen surfaces + paste block, file form).

1. Run the FULL suite exactly as the baseline was measured (~13-14 min):
   `$PY -m pytest tests/m3 -q -rs 2>&1 | tail -40`
   Record collected / passed / skipped / failed. `tests/phase2` as collateral:
   `$PY -m pytest tests/phase2 -q 2>&1 | tail -5`.

2. RECONCILE COMPONENT-EXACT against the baseline `1021 passed / 33 skipped / 0 failed`
   (1054 collected, measured 2026-08-22 at 14e62eb; `--collect-only` re-measured 1054 at
   7b59721 during planning). Requirements:
     * FAILED must be 0. If it is not, STOP and report — do not proceed to docs.
     * SKIPPED must still be 33. Every test added by this task is pure-synthetic and
       gate-free, so a new SKIP would mean a test is silently not running — that is a
       BLOCKER, not a rounding difference (`feedback_skip_guard_masks_not_fixes`).
     * Show the arithmetic: `1021 + N == new_passed` and `1054 + N == new_collected`, with N
       enumerated BY TEST NAME (list every added test function; state parametrize expansions
       explicitly — a 4-way parametrize is 4 items, not 1). If the arithmetic does not close,
       find the discrepancy test-by-test; do NOT report an aggregate that happens to agree
       (`feedback_aggregate_agreement_hides_component_errors`).

3. Update `.planning/HANDOFF.json`:
     * `suite_baselines["tests/m3"]` — CORRECT it to the new measured counts with the
       component-exact reconciliation inline (do not append a second sentence to the old one).
     * `resume_on_reconnect[0]` — a new entry stating: the pairwise-completeness scanner is
       BUILT AND TESTED AT NCSU AND HAS NEVER BEEN RUN ON DATA; the PENDING PASTE is written
       and UNRUN; the next action is CARTER starting the VM and giving the go, then STEP 1's
       00057 cross-check; and that the prevalence, the boundary width and the partial-
       confounding tail remain OPEN and may not be inferred from n=1.
     Keep the file valid JSON — verify with `$PY -c "import json;json.load(open('.planning/HANDOFF.json'))"`.

4. Prepend a dated section to `.planning/STATE.md` (house style, `★ RESUME HERE — LATEST ★`)
   with the same three points, plus one line naming the frozen surfaces proved unchanged.
   ⚠ State NO prevalence, NO boundary width, NO criterion recommendation anywhere.

5. Write `.planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-SUMMARY.md`
   from the GSD summary template, carrying: every pasted RED (T1 x >=8, T2 x 4, T3 x 1), the
   component-exact reconciliation, the guard outputs at every commit, the 1/10-scale mirror's
   arithmetic, and an explicit "WHAT THIS DOES NOT ESTABLISH" section naming the three open
   questions.

6. Final guards, then commit EXPLICIT paths only and PUSH:
   `git add .planning/HANDOFF.json .planning/STATE.md .planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-PLAN.md .planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-SUMMARY.md`
   Message: `docs(quick-260825-ngh): T4 — tests/m3 re-baselined component-exact; scanner BUILT AND UNRUN; prevalence/boundary/tail stay OPEN`
   `git push` (origin is SSH; no PAT needed). Then `git status -sb` MUST show no `ahead`.
   ⚠ Never `git add .` / `-A` on the shared GPFS tree.
   ⚠ If a commit fails with "invalid object / Error building trees", that is the known GPFS
   loose-object loss — recover per `reference_gpfs_git_object_store_loss`, do not force.
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3 -q -rs 2>&1 | tail -3 | tee /tmp/t4_suite.txt | grep -q "failed" && echo T4-SUITE-RED && exit 1; grep -q "33 skipped" /tmp/t4_suite.txt && $PY -c "import json;json.load(open('.planning/HANDOFF.json'))" && grep -q "pairwise_completeness_scan" .planning/HANDOFF.json && test "$(git diff --stat 7b59721 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/ | wc -l)" = 0 && A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md && awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb_t4.txt && test "$(wc -c < /tmp/pb_t4.txt)" = 22945 && md5sum /tmp/pb_t4.txt | grep -q 13a49f543cabcc27ce9f1e589783c060 && ! git status -sb | head -1 | grep -q ahead && echo T4-VERIFY-OK</automated>
  </verify>
  <done>`tests/m3` reports 0 failed and exactly 33 skipped; the passed/collected move from
1021/1054 is reconciled COMPONENT-EXACT with every added test named and the arithmetic shown;
`.planning/HANDOFF.json` carries the CORRECTED baseline and a resume entry saying the instrument
is built and UNRUN; `.planning/STATE.md` carries the same and states no prevalence, no boundary
width and no criterion recommendation; the SUMMARY carries every red, every guard output and a
"WHAT THIS DOES NOT ESTABLISH" section; frozen surfaces and the amendment paste block are
byte-unchanged at 22945 B / 13a49f54; the branch is pushed and `git status -sb` shows no
`ahead`.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| on-disk `.bed`/`.bim`/`.fam` -> `BedReader` | a binary file whose header/size is the only structural evidence; a wrong mode or a mismatched `.bim` silently corrupts every number |
| window `.bim` row index -> global `.bed` variant index | the index space crossing that, if conflated, reads the WRONG variant with no error |
| in-perimeter genotypes -> pasted stdout | the AoU egress boundary; per-sample data must never cross |
| a pasted result -> a project claim | an unverified harness could bank a wrong number as a measurement |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-ngh-01 | Tampering | `BedReader.__init__` | mitigate | validate magic, then mode, then `size == 3 + n_variants*bpv` (both directions), then `.bim`/`.fam` line-count agreement — each RAISES with its own message; four tests, each seen red |
| T-ngh-02 | Information disclosure | TSV / summary emission | mitigate | `TSV_COLUMNS` and `SUMMARY_KEYS` pinned by exact equality; no `sample`/`iid`/`fid`/`dosage` token; every field renders <= 64 chars; egress assertion has a SEEN-RED negative control |
| T-ngh-03 | Tampering | window-relative vs global variant index | mitigate | the module takes a `bfile_prefix` and derives global indices from that prefix's OWN `.bim` in one streaming pass; a loose window `.bim` is refused by construction; a negative control test demonstrates the corruption it prevents |
| T-ngh-04 | Repudiation | the in-perimeter sweep's results | mitigate | STEP 1 harness cross-check on `m2_region_00057` (71048 / 871 / offset +1) runs ALONE and DISCARDS ALL RESULTS on mismatch; STEP 0 pastes back the running commit SHA so results are attributable to code |
| T-ngh-05 | Elevation of privilege | the scanner reaching the fire path | mitigate | the module is import-isolated: `run_native_ld_panel.py` / `fire_verifier.py` / `occlusion_span_filter.py` are proved byte-unchanged by a `git diff --stat` guard at EVERY commit; the scanner is never imported by any of them |
| T-ngh-06 | Denial of service | unbounded decode memory on a 354 GB `.bed` | mitigate | seek-by-index reads ONLY candidate blocks; bounded LRU cache stores int8 dosage only (`cache_variants * n_samples` bytes, ~150 MB at default); `--cache-variants 1` proved byte-identical in output |
| T-ngh-07 | Spoofing | a stale clone on the VM running old code | mitigate | PENDING PASTE STEP 0 does `git pull --ff-only` + `git log -1 --oneline` pasted back + `ls -l` on the module; NCSU push is T4 and is a precondition |
| T-ngh-08 | Tampering | inference of a prevalence from n=1 | accept-with-control | no rate/prevalence/estimate key may exist in the summary (asserted); the plan, module docstring, STATE and SUMMARY all state the three questions stay OPEN. The residual risk is a human quoting a single region — controlled by wording, not code |
</threat_model>

<verification>
Run after the final task, from the repo root:

```bash
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
BASE=7b59721

# 1. the instrument exists and never forked the frozen column indices
grep -c '_COL_BP *=\|_COL_CHR *=\|_COL_ID *=\|_COL_ALT *=\|_COL_REF *=' \
  src/python/pairwise_completeness_scan.py          # MUST be 0
grep -c 'occlusion_span_filter' src/python/pairwise_completeness_scan.py   # MUST be >= 1

# 2. nothing on the fire path or the public record moved
git diff --stat $BASE HEAD -- \
  src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py \
  src/python/fire_verifier.py .planning/amendments/ | wc -l                # MUST be 0

# 3. the amendment paste block (FILE FORM — the tee form is racy)
A=.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}/--- PASTE ENDS HERE ---/{f=0}f' "$A" > /tmp/pb.txt
wc -c < /tmp/pb.txt                                  # MUST be 22945
md5sum /tmp/pb.txt                                   # MUST be 13a49f543cabcc27ce9f1e589783c060

# 4. the suite
$PY -m pytest tests/m3 -q -rs 2>&1 | tail -3         # 0 failed, exactly 33 skipped
$PY -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3

# 5. the blind-spot instrument and the measured mirror are both present
grep -c 'MIRRORS_A_MEASURED_CASE' tests/m3/test_pairwise_completeness_scan.py   # >= 2
grep -c 'partial_confounding_is_DEFINED' tests/m3/test_pairwise_completeness_scan.py

# 6. the PENDING PASTE carries the harness cross-check
P=.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
grep -c 71048 "$P"; grep -c 871 "$P"; grep -c 20394741 "$P"   # each >= 1

# 7. nothing fired, branch published
git log --oneline $BASE..HEAD                        # 4 commits, all explicit-path
git status -sb | head -1                             # no 'ahead'
```

Manual reads (no command can check these):
- The module docstring states THE PROPERTY first and marks `carriers ⊆ missing` as a derived
  label only.
- The PENDING PASTE nowhere instructs an agent to fire, edit a criterion, or adjust a number.
- STATE.md / HANDOFF.json state NO prevalence, NO boundary width, NO criterion recommendation.
</verification>

<success_criteria>
- `src/python/pairwise_completeness_scan.py` exists (>= 400 lines), imports the frozen `.bim`
  column constants and `parse_bim_row` / `load_bim_rows` from `occlusion_span_filter`, and
  declares ZERO column indices of its own.
- `tests/m3/test_pairwise_completeness_scan.py` exists (>= 500 lines) and passes; `tests/m3`
  is 0 failed at every one of the 4 commits and 33 skipped at the end.
- Every raise, every boundary, every property assertion was OBSERVED RED before it was green,
  and each red is pasted in the SUMMARY (>= 13 reds total).
- The measured 00057 case reproduces synthetically under a `MIRRORS_A_MEASURED_CASE` label with
  hand-computed oracles, and the partial-confounding case returns `undefined == False` with a
  populated gradient — the first instrument in the project that can see a defined-but-biased `r`.
- `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` exists, carries the
  STEP 0 freshness check and the STEP 1 `m2_region_00057` cross-check (71048 / 871 / offset +1,
  DISCARD ALL on mismatch), and was NOT RUN.
- Frozen surfaces byte-unchanged; amendment paste block 22945 B / `13a49f54...`; zero VM /
  Dataproc / OSF / `gsutil` / `gcloud` contact; $0.
- The suite move is reconciled COMPONENT-EXACT with every added test named; `.planning/HANDOFF.json`
  `suite_baselines["tests/m3"]` is CORRECTED and the file is valid JSON.
- The prevalence, the boundary width and the partial-confounding tail are stated as OPEN in the
  module docstring, the PENDING PASTE, STATE.md, HANDOFF.json and the SUMMARY. No number for any
  of them appears anywhere.
- `git status -sb` shows no `ahead`.
</success_criteria>

<output>
After completion, create
`.planning/quick/260825-ngh-build-tdd-the-pairwise-completeness-scan/260825-ngh-SUMMARY.md`
</output>
