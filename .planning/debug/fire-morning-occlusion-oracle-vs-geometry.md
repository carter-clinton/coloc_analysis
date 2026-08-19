---
status: diagnosed
trigger: "fire-morning-occlusion-oracle-vs-geometry — gated real-window known-answer test failed on first-ever contact with real data: 231 geometry-occluded variants vs settled 5-member oracle; 7,951 multi-base REF rows vs asserted exactly-7 inventory"
created: 2026-08-19T00:00:00Z
updated: 2026-08-19T00:00:00Z
mode: symptoms_prefilled, goal=find_root_cause_only
constraints: "$0, NCSU-only, read-only vs the repo. Nothing edited, nothing fixed, nothing committed. VM STOPPED and never contacted. No OSF contact. Suites NOT run (nothing changed)."
---

## Current Focus

hypothesis: CONFIRMED — the oracle is a false extrapolation. Two independent scope
errors, both of the form "the set I looked at" written as "the set that exists":
(1) observable-NaN ⊂ geometric occlusion (5 NaN-implicated partners promoted to
"the full occluded set"); (2) the 7 deletions implicated in the 6 NaN pairs
promoted to "the window's deletion inventory". The detector is byte-faithful to
its pinned rule; the ASSERTION is the defect.
test: provenance trace to source docs; line-by-line read of the shipped detector
against the pinned predicate; adversarial search for a detector-defect story
consistent with 231-with-consecutive-runs; forward-model arithmetic.
expecting: all four detector-defect candidates refuted by evidence already in
hand, and the geometry verdict's own text shown to be pair-scoped.
next_action: DIAGNOSIS COMPLETE — deliverables 1-6 below. No fix applied by design
(goal: find_root_cause_only). Carter decides from the options memo (§5).

## Symptoms

expected: test_region1_real_window_known_answer_gated passes — detector over the real region-1 window .bim returns exactly {10328, 44784, 46714, 59097, 66730} (0-based row indices) and the window contains exactly 7 multi-base REF rows with spans 60/29/7/31/31/17/29 bp.
actual: detector returned 231 occluded (oracle 5 subset-of observed, nothing missing, no shift); window has 7,951 multi-base REF rows, max span 170 bp; assertion at tests/m3/test_occlusion_span_filter.py:521 failed with ~226 extra members, many in consecutive runs (65340-65343, 71567-71573, 101915-101920).
errors: AssertionError set diff (full -vv capture is on the VM at /home/jupyter/step7_vv.txt — NOT locally available; the probe summary numbers were relayed verbatim in-session and are authoritative).
reproduction: In-perimeter only (real .bim required): pytest tests/m3/test_occlusion_span_filter.py::test_region1_real_window_known_answer_gated with data/aou/region1_window.bim present (102,421 rows, awk chr1 10000-13506933 window of /home/jupyter/afr_cohort.bim). NOT reproducible on NCSU (no real .bim; test skips).
started: First-ever real-data run of this gated test (2026-08-19 fire morning). Oracle settled ~2026-07 from June NaN forensics; synthetic-fixture tests have always passed and still do.

## Eliminated

- hypothesis: Detector uses non-strict left bound (POS_D <= POS_V), over-dropping
  co-located multiallelic partners — which WOULD manufacture consecutive-index runs.
  evidence: src/python/occlusion_span_filter.py:250 reads `d.pos < v.pos <= d.span_end`
  — strict `<` on the left, verbatim the pinned predicate. The discriminating test
  (tests/m3/test_occlusion_span_filter.py:462-485,
  test_distinct_variant_at_the_deletion_position_is_not_occluded) is purpose-built to
  separate `<` from `<=` — it constructs a DISTINCT variant at the deletion's exact POS
  plus a genuinely-inside positive control at POS+5, and asserts the co-located one is
  NOT occluded while the downstream one IS. That test is green and unchanged. This is
  the only hypothesis that would have explained the runs as a defect; it is dead.
  timestamp: 2026-08-19

- hypothesis: Right-bound off-by-one (`POS + len(REF)` rather than `POS + len(REF) − 1`),
  adding one spurious covered base per deletion.
  evidence: occlusion_span_filter.py:118 `return self.pos + self.ref_len - 1`. Pinned by
  test_off_by_one_boundary_last_covered_base_occluded (:358-374), which asserts POS+9 IN
  and POS+10 OUT for a len(REF)=10 deletion at POS=1000. Green. Quantitatively this
  defect would have added ~60 (7,951 × 102,421/13,496,934), not ~226 — wrong magnitude
  even if it existed.
  timestamp: 2026-08-19

- hypothesis: A1/A2 column swap — len(A1)=len(ALT) read as the footprint, making every
  INSERTION an occluder and inflating the count.
  evidence: SELF-REFUTING against the observed result. Region 1's occluders are
  left-anchored deletions: multi-char REF (A2), single-char ALT (A1). Under a swap their
  ref_len would be 1, they would not qualify as deletions, and NONE of the 5 oracle
  variants could have been detected. All 5 WERE detected at their exact indices
  (`oracle_subset_of_observed: True`, `oracle_missing_from_observed: []`). The oracle-5
  subset result is itself the negative control against a column swap. Also:
  occlusion_span_filter.py:87-88 declares _COL_ALT=4 / _COL_REF=5 consistent with the
  FROZEN plink_ld_to_npz.load_bim convention.
  timestamp: 2026-08-19

- hypothesis: Wrong window — data/aou/region1_window.bim is wider than the window the
  production gate reads, so 231 overstates what clause (d) would see at fire time.
  evidence: The probe window (`awk '($1=="1"||$1=="chr1") && $4>=10000 && $4<=13506933'`
  over /home/jupyter/afr_cohort.bim, ox1 AGENT-PROMPT.md:166) is coordinate-identical to
  the production window. config/ld_regions.tsv:2 gives m2_region_00001 AFR
  window_start_grch38=10000, window_end_grch38=13506933; the producer derives its count
  via `_window_bim_n_var(bim_path, chrom, from_bp, to_bp)`
  (run_native_ld_panel.py:815-817) over the SAME /home/jupyter/afr_cohort.bim reached by
  `--bfile-prefix /home/jupyter/afr_cohort`. Same file, same interval, same filter.
  `pre_window_n_var` at fire time = 102,421 exactly, and the gate at :853 would compute
  231 > 0.0005 × 102,421 = 51.2105.
  timestamp: 2026-08-19

- hypothesis: Duplicate rows / degenerate ids inflate the count.
  evidence: occlusion_span_filter.py:263 returns `sorted(set(occluded_ids))`, and
  occluded_ids is appended once per VARIANT (:254), not once per edge. Duplicate vids
  would UNDER-count, never over-count. Pinned by
  test_doubly_occluded_variant_appears_exactly_once (:434-459). Green.
  timestamp: 2026-08-19

- hypothesis: The consecutive-index runs are themselves anomalous and indicate a defect.
  evidence: A .bim is position-sorted, so consecutive row indices are consecutive
  positions. A run of k consecutive occluded rows = k variants inside one (or a set of
  overlapping) deletion footprint(s). With max_span=170 bp and mean spacing 131.8 bp,
  a 7-long run requires locally-dense records — exactly the multiallelic-split /
  complex-indel-locus structure the m3 scientific review itself named as the leading
  mechanism (:46-49: "a multiallelic site split into adjacent bi-allelic records, or
  overlapping indel / MNP representations, where a caller emits several records"). The
  runs are a PREDICTION of the settled mechanism, not a contradiction of it. Note the
  split partners sharing a POS are NOT occluded (strict left); it is their downstream
  neighbours inside the same footprint that are.
  timestamp: 2026-08-19

## Evidence

- timestamp: 2026-08-19 (phase 0)
  checked: .planning/debug/knowledge-base.md — 8 entries, keyword scan for occlusion/oracle/span/geometry/multi-base REF/known-answer
  found: NO keyword match. Nearest neighbours are representation/contract-class bugs (npz triangle flag, declared-input-not-read-path) but none touch the occlusion detector or its oracle.
  implication: Novel pattern for this repo. No prior-session shortcut; investigate from first principles.

- timestamp: 2026-08-19
  checked: src/python/occlusion_span_filter.py in full (264 lines) against the pinned
  predicate in STATE.md:460 ("POS < variant_POS ≤ POS + len(REF) − 1", Seth 5/5) and
  against the posted amendment clause (a) (:55).
  found: The rule is implemented at :248-251 as
  `[d for d in deletions if d.index != v.index and d.pos < v.pos <= d.span_end]`
  with `span_end = pos + ref_len - 1` (:118), `is_deletion = ref_len > 1` (:123), and
  `ref_len = len(row[5])` = len(A2) = len(REF) (:157-162, :88). Evaluated over the
  ORIGINAL window (:233-234, no iteration). Occluded appended once per variant (:254),
  deduped and sorted (:263). Deterministic single attribution (:182-196).
  implication: BYTE-FAITHFUL to the pinned rule. There is no gap between the specified
  predicate and the shipped predicate. Any story in which 231 is "wrong" must attack the
  RULE, not the code — and the rule is the one pre-registered at clause (a).

- timestamp: 2026-08-19
  checked: .planning/amendments/m3_nan_conditioning_scientific_review.md (116 lines, the
  document the oracle's index-space note cites at test:172-175).
  found: Its entire input is "the 12 NaN cells (6 symmetric pairs)" (:18). Its features
  list (:41-43) is "pairs are index-adjacent (10327/10328, 46713/46714/46715, …); within
  8–52 bp (five bp clusters; spans 52/13/8/14/28 bp, median 14 bp); one variant (46714)
  chains two pairs". NOTE: the spans quoted there — 52/13/8/14/28 — are the bp GAPS
  BETWEEN NaN partners, a different quantity from the test's REF-span inventory
  60/29/7/31/31/17/29. The review never scans the window; it reasons from reported
  aggregates and says so explicitly at :110-112 ("This analysis reasons from the reported
  aggregate statistics … not from re-derived genotype data").
  implication: The oracle's index space (row indices, not bp) IS correctly sourced here.
  But the review is a 6-pair document end to end. Nothing in it licenses a window-wide
  total of any kind.

- timestamp: 2026-08-19
  checked: .planning/amendments/m3_region1_nan_geometry_verdict.md (79 lines, body anchor
  4543dcf4…) — the document the test docstring calls the settled mechanism source.
  found: THE PROVENANCE SMOKING GUN. Its scope is stated at :13 ("The verdict (6/6 now
  mechanistically resolved)") and :9-11 ("I recomputed every REF span and coverage test
  from the raw bp/len(REF) values — result is byte-for-byte the browser agent's geometry
  (5 ref_span_overlap, 1 disjoint)"). The 6-row table at :15-22 names exactly 7 distinct
  deletions: 1980423(60), 5733474(29), 5922716(7), 5922724(31), 7492679(31), 7492693(17),
  8375794(29). Then :73-74, under a heading titled "## Generalization flag", writes:
  "Region 1 alone has **7 distinct deletions** (60/29/7/31/31/17/29 bp)". That sentence
  enumerates the NaN-implicated subset in WINDOW-WIDE language. The same slip governs the
  same-position claim at :41-42: "**bcftools norm -m + is the wrong tool for all six** —
  there are **zero same-position cases**" — correctly scoped to the six pairs in the
  verdict, but reduced to an unscoped "0 same-position" downstream.
  implication: The verdict itself is CORRECT and its per-pair geometry is confirmed by
  the real run. What is false is the sentence's SCOPE, and only that. Note the same
  paragraph (:75-78) predicts "Across 276 regions of AFR WGS this pattern will recur" and
  :65 asks "whether an overlapping-deletion span filter belongs upstream at panel-build
  for ALL 276 regions (region 1 is unlikely to be unique)" — the verdict was already
  telling us the phenomenon is general. We read the generality and dropped the magnitude.

- timestamp: 2026-08-19
  checked: probe-2 numbers against a uniform-density forward model (arithmetic run
  locally, $0).
  found: window = 13,506,933 − 10,000 + 1 = 13,496,934 bp (13.497 Mb — CONFIRMED against
  .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv:2, which
  carries 13496933 / "13.497" / class "medium"). Density = 7.5885e-3 var/bp = 1 per
  131.8 bp. multi-base-REF fraction = 7,951/102,421 = 7.763%. occluded fraction =
  231/102,421 = 0.2255%. Ceiling = 51.2105; observed/ceiling = 4.51×. INVERTING the
  observation: 231 occluded implies ~30,441 downstream-covered bases, i.e. ~3.83 bp of
  downstream coverage per deletion, i.e. mean len(REF) ≈ 4.83 (mean deleted length
  ≈ 3.83 bp).
  implication: A mean deleted length of ~3.8 bp is the textbook shape of a short-indel
  WGS deletion spectrum (median 1-2 bp, mean pulled up by a tail — here to 170 bp). The
  observed 231 is the number a correct geometric detector MUST produce on a substrate
  with these two measured aggregates. It is not an excess; it is the arithmetic.
  ⚠ CORRECTION TO THE BRIEF: the task framing said "7,951 deletions in 3.5 Mb". The
  window is 13.5 Mb, not 3.5 Mb. This matters — at 3.5 Mb the implied density would be
  ~4× higher and the deletion burden would look genuinely anomalous. At the true 13.5 Mb
  it is ordinary.

- timestamp: 2026-08-19
  checked: FORWARD MODEL (NCSU, $0). Built a synthetic region-1-SHAPED window from the
  two measured aggregates ONLY — 102,421 uniformly-random positions over 13,496,934 bp,
  7,951 of them multi-base-REF with a generic short-indel length draw
  (len(REF) = 2 + int(Exp(mean 3)), capped at 170) — and ran the SHIPPED detector on it.
  found: 222 occluded (vs the measured 231). Agreement within 4%.
  implication: The measured 231 is PREDICTED from n_rows + n_deletions + a generic indel
  length spectrum, with no knowledge of the real positions. Strong corroboration that the
  detector is doing pure geometry and that 231 is the correct answer for this substrate.
  HONESTY CAVEAT: the length distribution's mean was informed by the inversion above, so
  this is corroborative rather than fully independent. The load-bearing point is the
  ORDER OF MAGNITUDE: any plausible short-indel spectrum lands in the low hundreds; none
  lands at 5.

- timestamp: 2026-08-19
  checked: external sanity check on the 7.76% multi-base-REF fraction (web, gnomAD v3
  WGS aggregate).
  found: gnomAD v3 (71,702 WGS samples) reports ~602M SNVs and ~105M indels — indels
  ≈ 14.8% of all variants. Deletions are roughly half of indels in short-read callsets,
  so deletions ≈ 7-8% of all variant records.
  implication: 7,951/102,421 = 7.76% multi-base-REF rows is EXACTLY the expected WGS
  deletion fraction. It is not a representation pathology. Conversely, the oracle's
  implied inventory — 7 deletions in 102,421 records = 0.0068% — is biologically
  impossible for any WGS callset; it is off by a factor of ~1,140. This is the single
  cleanest falsification of the oracle available, and it needed no perimeter access.

- timestamp: 2026-08-19
  checked: PERFORMANCE of the shipped detector at real dimensions (NCSU, $0, synthetic
  window of region-1 shape). Relevant because the brief hypothesised a "minutes, ~$0"
  multi-region measurement pass.
  found: 168.0 s for one region-1-shaped window, single-threaded CPython. The rule is
  O(n_variants × n_deletions) — 102,421 × 7,951 ≈ 8.1e8 comparisons per region.
  implication: ⚠ THE BRIEF'S COST PREMISE IS WRONG. All 276 regions with the shipped
  detector unchanged ≈ 10-13 h of VM wall time (not minutes). A ~20-region stratified
  sample ≈ 1 h. Still cheap in absolute terms (an analysis VM is order $0.20-0.40/h → ~$0.50
  for the sample, ~$5 for all 276) and trivial beside the $385-1,084 fire — but it is
  hours, not minutes, and it must be planned as such. SECOND-ORDER FINDING: this same
  ~168 s/region is already on the Stage-C critical path 276 times (≈10 h of the 11-day
  budget). Not a blocker; worth knowing before the fire.

## Resolution

root_cause: |
  The oracle asserted at tests/m3/test_occlusion_span_filter.py:186-188 and enforced at
  :521-523 is a FALSE EXTRAPOLATION, not a known answer. It was produced by promoting
  the SCOPE of the June 2026 NaN forensics from "the 6 observed NaN pairs" to "the
  region-1 window", in two independent steps:

    (1) OCCLUDED SET. The 5 oracle row indices are the 5 variants whose occlusion was
        OBSERVABLE as a NaN LD cell. Observable-NaN is a strict subset of geometric
        occlusion: a NaN requires the pairwise-complete genotype subset to be degenerate
        (near-perfectly correlated missingness at MAF high enough to matter), whereas
        geometric occlusion requires only that POS_V fall inside an upstream deletion's
        REF footprint. Every NaN-producing pair is geometrically occluded; the converse
        is false — most geometrically occluded variants are too rare, or their partner
        too distant/too common, to force r to 0/0 anywhere the panel looks. The forensics
        enumerated the observable tip; the detector enumerates the geometry. 5 ⊂ 231, and
        the probe confirms exactly that containment with no shift and nothing missing.

    (2) DELETION INVENTORY. The "7 deletions, spans 60/29/7/31/31/17/29" are the 7
        distinct deletions appearing in the geometry verdict's 6-pair table. The verdict
        wrote them up under a "Generalization flag" heading as "Region 1 alone has 7
        distinct deletions" — window-wide phrasing for a pair-scoped enumeration — and
        that sentence was copied forward verbatim into the plans, the tests and the
        posted OSF amendment. The real window has 7,951 multi-base-REF rows, which is the
        ordinary WGS deletion fraction (7.76%; gnomAD-consistent).

  The DETECTOR IS CORRECT. src/python/occlusion_span_filter.py:248-251 implements the
  pre-registered clause-(a) predicate byte-faithfully; all 22 synthetic fixture tests
  including the three purpose-built discriminators (strict-left, right-boundary,
  duplicate-drop) are green and unchanged; four candidate detector-defect stories are
  refuted above, one of them (the A1/A2 swap) by the oracle-subset result itself.

  STEP 7's actual scientific purpose — confirming the oracle's index ORIGIN (0- vs
  1-based) against the real .bim, the one reconciliation item flagged at test:180-183 —
  PASSED. The 5 oracle indices resolve to real occluded variants at exactly those
  0-based positions. What failed is the equality operator wrapped around them.

  CONSEQUENCE AT THE GATE: run_native_ld_panel.py:853 evaluates
  231 > 0.0005 × 102,421 = 51.2105 → TRUE → region 1 returns status
  "deferred_occlusion_anomaly: 231 occluded of 102421 (ceiling 51)" BEFORE the
  excludelist, manifests or plink run (:853-861), and under Stage A's --fail-fast the
  loop then raises RegionGateError (:1161-1162). Region 1 cannot bank as pre-registered.
  This is the pre-registered machinery WORKING, on a ceiling whose calibration premise is
  now measured false.

  ⚠ HIGHEST-BLAST-RADIUS CONSEQUENCE, not in the original deliverable list:
  the false claim is in the POSTED OSF record. See §1-A below.

fix: NOT APPLIED — mode is goal=find_root_cause_only. Nothing edited, nothing committed.
verification: n/a (no fix applied). The diagnosis is verified by five independent lines
  of evidence: code-vs-spec read, provenance scope trace, inverted arithmetic, forward
  model at real dimensions, and an external WGS deletion-fraction check.
files_changed: []

---

# DELIVERABLES

---

## 1. PROVENANCE TRACE — every consumer of the false premise

**The chain, with the exact language at each hop.**

**HOP 0 — the true, correctly-scoped source.**
`.planning/amendments/m3_region1_nan_geometry_verdict.md` (body SHA-256 `4543dcf4…`).
Scope declared at `:13` — "## The verdict (6/6 now mechanistically resolved)" — and at
`:9-11`, "I recomputed every REF span and coverage test from the raw `bp`/`len(REF)`
values — result is byte-for-byte the browser agent's geometry (5 `ref_span_overlap`, 1
`disjoint`)". The 6-row table (`:15-22`) is the whole evidentiary base. Everything in it
is CONFIRMED by the real run.

**HOP 1 — the scope slip. `m3_region1_nan_geometry_verdict.md:73-74`:**

> ## Generalization flag (worth raising now)
> Region 1 alone has **7 distinct deletions** (60/29/7/31/31/17/29 bp): a 7-bp, four
> ~30-bp (29/31/31/29 at pairs 2, 4, 5, 6), a 17-bp co-terminating with the pair-5 31-bp
> deletion, and a 60-bp — each occluding or overlapping a neighbor.

The parenthetical "(at pairs 2, 4, 5, 6)" proves the enumeration is pair-indexed. The
sentence's subject — "Region 1 alone has" — is window-indexed. That one mismatch is the
origin of everything below.

The companion slip, `:41-42`:

> **`bcftools norm -m +` is the wrong tool for all six** — there are **zero same-position
> cases**, so allele-merging touches nothing.

Correctly scoped in the verdict ("for all six"). The scope is dropped downstream.

**HOP 2 — the ratification.** `.planning/STATE.md:460` records the 2026-07-10 design input:

> a coordinate-predicate reference validated **5/5** against the region-1 geometry
> verdict — occluded set `{10328,44784,46714,59097,66730}`, the 7-deletion inventory
> (60/29/7/31/31/17/29 bp), **0** same-position (bcftools norm fixes none) …

"Validated 5/5 **against the geometry verdict**" is exactly right and exactly the problem:
the predicate was checked against a 6-row hand table, never against the 102,421-row
window. A 5/5 on 5 rows was recorded as a window-wide known answer. The "0 same-position"
has lost its "for all six" here.

### CONSUMER SWEEP (file:line, what it asserts, live/latent)

**(1-A) THE POSTED OSF RECORD — HIGHEST BLAST RADIUS. Not in the original brief.**

| file:line | text | status |
|---|---|---|
| `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md:45` | "…Zero pairs are same-position multiallelic records — so allele-merge normalization (bcftools norm -m +) resolves none of them. **Region 1 alone contains 7 distinct overlapping deletions (60/29/7/31/31/17/29 bp).**" | **PUBLIC · MEASURED FALSE** |

This is inside the `--- PASTE INTO OSF FROM HERE ---` block, i.e. it is in the body posted
to `osf.io/az52u` file `trsx5` at 2026-07-10T13:32:22Z. It is a factual claim about the
substrate, in a pre-registration, and the real window carries **7,951** multi-base-REF
rows. Under the narrower reading ("overlapping deletions" = deletions that actually
occlude a neighbour) it is still false: 231 occluded variants imply on the order of
150-230 distinct occluding deletions, not 7.

Note the precision asymmetry *within the same bullet*: "**Zero pairs** are same-position"
is correctly pair-scoped and remains TRUE; "**Region 1 alone contains** 7 distinct
overlapping deletions" is window-scoped and is FALSE. One sentence survives, the next does
not.

Byte-identical copies of the posted body, for the record:
- `.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt:11` (the re-measured posted body — 9,695 B / `c19be8b2…`, re-verified at fire time this morning per STEP 6b)
- `.planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-seth-lineage-9907.txt:11`

**Correcting this is a disclosure obligation independent of anything else on this page.**
It is not a candidate for a silent swap, and it is not contingent on which of options
A/B/C Carter picks.

**(1-B) TESTS**

| file:line | what it encodes | status |
|---|---|---|
| `tests/m3/test_occlusion_span_filter.py:147-149` | `_REGION1_EXPECTED_OCCLUDED_POS = {1980475, 5733487, 5922718, 7492693, 8375822}` | **TRUE** — synthetic fixture only; correctly scoped |
| `:152` | `_REGION1_DELETION_REF_SPANS = [60,29,7,31,31,17,29]` | **TRUE** — describes the 11-row synthetic fixture |
| `:154-183` | the "SETTLED REAL-WINDOW ORACLE" comment block | **FALSE PREMISE, correct index space.** `:163` "SETTLED (Seth 5/5 vs the geometry verdict 4543dcf4…)"; `:168-175` correctly reconciles the index SPACE (row indices, not bp) and cites the scientific review's adjacency language; `:180-183` flags index ORIGIN as the one open item. Origin is now CONFIRMED 0-based. The block never questions the scope. |
| `:186` | `_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES = {10328, 44784, 46714, 59097, 66730}` | **TRUE AS A SUBSET, FALSE AS AN EQUALITY** |
| `:187` | `_REGION1_REAL_DELETION_REF_SPANS = [60,29,7,31,31,17,29]` | **FALSE as a window inventory** (7,951 rows; max span 170) |
| `:188` | `_REGION1_REAL_SAME_POSITION_COUNT = 0` | **LATENT FALSE.** Never asserted — interpolated only into the skip message at `:510`. Its scope ("among the 6 NaN pairs") was lost at HOP 2. |
| `:201` | `assert spans == _REGION1_REAL_DELETION_REF_SPANS  # synthetic mirrors the real window` | assertion holds (two identical literals); the **comment is now known false** |
| `:492-511` | gated test docstring + skip message, restating the oracle | FALSE premise, propagated |
| **`:521`** | `assert got_row_indices == _REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES` | **THE FAILING ASSERTION #1** — equality where only containment is derived |
| **`:523`** | `assert spans == sorted(_REGION1_REAL_DELETION_REF_SPANS)` | **THE FAILING ASSERTION #2** — window inventory equality |
| `tests/m3/test_run_native_ld_panel.py:1599-1601` | "Region-1 synthetic fixture -> EXACTLY 5 occluded" | **TRUE** — explicitly says *synthetic fixture* |
| `tests/m3/test_run_native_ld_panel.py:2142-2143` | "The region-1 TEST fixture is topology-dense (5 occluded / 11 = 45%; **the REAL region 1 is 5/102,421 = 4.9e-5**)" | **FALSE** — real is 231/102,421 = 2.26e-3, 46× higher |
| `tests/m3/test_run_native_ld_panel.py:1656, :1680, :1748, :1917, :1966, :2188, :2207` | "exactly the 5 occluded ids", `11 raw − 5 occluded`, `"5 occluded of 11" in status` | **TRUE** — all synthetic-fixture-scoped |
| `tests/m3/test_fire_verifier.py:101` | "The Stage-A panel: region 1 computed ok, **5 occluded of 102,421**" | **FALSE** — the fixture encodes the false real-world expectation |
| `tests/m3/test_fire_verifier.py:513,520,529,534,541` | `check_manifest_rows(..., expected_records=5, ...)` | **FALSE premise** inherited from the same source |
| `tests/m3/test_occlusion_catalog_assembly.py:150` | `assert len(df) == 10  # 5 occluded x 2 regions` | **TRUE** — synthetic |

**(1-C) SHIPPED SOURCE**

| file:line | what it encodes | status |
|---|---|---|
| `src/python/run_native_ld_panel.py:133` | `_OCCLUSION_ANOMALY_FRACTION = 0.0005` | the pre-registered constant. Deliberately **not** CLI-tunable (`:129-130`: "a knob would invite silent deviation from the public commitment"). **Correctly implemented; its calibration premise is what is false.** |
| `src/python/run_native_ld_panel.py:848-850` | comment: "Real region-1 headroom: **5/102,421 = 4.9e-5** vs ceiling 51 = int(0.0005 * 102,421) — **10x headroom; the gate must not fire there.**" | **FALSE** — in shipped source. Real headroom is 0.22× (i.e. 4.51× OVER). The comment states as fact the exact thing that just failed. |
| `src/python/run_native_ld_panel.py:853-861` | the clause-(d) gate; defers BEFORE excludelist/manifest/plink | **CORRECT** — will fire, as designed |
| `src/python/run_native_ld_panel.py:1161-1162` | `if fail_fast and status != "ok": raise RegionGateError` | **CORRECT** — Stage A will HALT, not merely record |
| `src/python/fire_verifier.py:485` | `def check_manifest_rows(..., expected_records: int = 5, ...)` | **FALSE default** |
| `src/python/fire_verifier.py:490-491` | "Region 1 is the ONLY region with a known answer (**5 occluded**), so it is the one chance to validate the manifest writer against ground truth." | **FALSE** — and note the irony: the module's own docstring (`:38-41`) forbids hand-transcribed shipped constants precisely to avoid "a silent divergence with no enforcer". `expected_records=5` is exactly such a hand-transcribed constant; it is the one number in the module NOT imported from a shipped source. |
| `src/python/fire_verifier.py:595-596` | "region 1 is the known-answer region (**5 occluded, ~51 ceiling, 10x headroom**)" | **FALSE** |
| `src/python/fire_verifier.py:114-122, :547-575` | `_default_occlusion_fraction()` reads `rnlp._OCCLUSION_ANOMALY_FRACTION` at evaluation time; `check_occlusion_ceiling` reproduces the strict `>` | **CORRECT** — will FAIL closed (HARD_STOP) with `n_occluded=231 > ceiling=51.2` |
| `src/python/fire_verifier.py:578-601` | `check_region1_status` — anything but `"ok"` is the finding, severity `FINDING` (`:98`) | **CORRECT** — will FAIL |

**(1-D) RUNBOOK — `.planning/quick/260812-ox1-…/`**

| file:line | text | status |
|---|---|---|
| `260812-ox1-AGENT-PROMPT.md:183` | "n_var slightly under 102421, **n_dropped_occluded near 5**" | FALSE |
| `260812-ox1-AGENT-PROMPT.md:196-198` | "EXPECT: **6 lines (header + exactly 5 records)**, region_id m2_region_00001 on every record row. This is the one region with a known ground truth" | FALSE — and moot: the gate defers **before** the manifest is written (`run_native_ld_panel.py:853-861`), so the manifest will not exist at all |
| `260812-ox1-AGENT-PROMPT.md:311-315` | "at region 1's n_var of 102,421 it is 51.2. **Region 1's expected ~5 occlusions therefore sit about 10x under the ceiling, so a deferral there would itself be the finding.**" | FALSE premise — but note the conditional is now SATISFIED: a deferral there IS the finding, exactly as written. The runbook's own language authorises treating this as a finding rather than a retry. |
| `260812-ox1-AGENT-PROMPT.md:304-306` | "no deferral count is a pre-committed expectation (the count emerges at fire time)" | **TRUE and load-bearing** — deferral counts were never pre-committed |
| `260812-ox1-READY-TO-FIRE.md:257`, `260812-ox1-BROWSER-PASTE.md:236,245`, `260812-ox1-PLAN.md:468` | same "≈ 5" / "ground truth = 5 records" expectations | FALSE |
| `260812-ox1-VERIFICATION.md:27` | `assert len(records) == 5` (local-mode manifest byte-compare) | TRUE — synthetic/local fixture |

**(1-E) PLANNING RECORD (documentation only, no execution effect)**

`.planning/STATE.md:443`, `:460`, `:461`; `.planning/ROADMAP.md`;
`.planning/phases/m3-aou-afr-ld-panel-build/`: `m3-07-CONTEXT.md:25`,
`m3-07-RESEARCH.md:81,215,494`, `m3-07-VALIDATION.md:81`,
`m3-07a-…-PLAN.md:28,29,134,288,302`, `m3-07a-…-SUMMARY.md:175,188,285`,
`m3-07a-UAT.md:64,78`, `m3-07b-…-PLAN.md:23,135,136,250`, `m3-07b-…-SUMMARY.md:218-219`,
`.continue-here.md:281`; `.planning/quick/260812-ox1-…-SUMMARY.md:86-87`,
`…-CONTEXT.md:90-91,100`, `…-PLAN.md:183,361`;
`.planning/quick/260811-pmv-…-EVIDENCE.md`.

**One entry deserves separate note.** `m3-07-RESEARCH.md:494` (assumption register, row A1):

> The real in-perimeter cohort `.bim` stores full multi-char indel REF in A2 (not
> `.`/normalized) — inferred from `load_bim`'s contract + the verdict's `len(REF)`
> re-derivation; not directly inspectable NC-State this phase. … **CONTRADICTED by the
> verdict's 60/29/7-bp spans, so risk is LOW; confirm at the gated re-run.**

That assumption is now **CONFIRMED TRUE** by the real run (7,951 multi-char A2 rows,
max 170 bp). The research register did its job. It is the only artifact in the chain that
correctly labelled the real-window claims as unverified.

**Summary of the sweep.** One posted public claim (1-A), two live failing assertions plus
five stale constants/comments in tests (1-B), four false statements in shipped source
including one hand-transcribed constant the module's own policy forbids (1-C), five
runbook EXPECTs (1-D), ~25 planning-doc restatements (1-E). Every one traces to a single
sentence: `m3_region1_nan_geometry_verdict.md:73-74`.

---

## 2. PRE-REGISTRATION — exact text and what is actually pre-committed

### 2.1 Clause (d), verbatim
`.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md:61`:

> (d) Anomaly gate (per region). If the count of occlusion-excluded variants in a region
> exceeds 0.05 percent of the region's variant count (n_excluded ≤ 0.0005 × n_var; the
> same fractional gate as the withdrawn ceiling, re-purposed to exclusions), the region is
> treated as a substrate anomaly: it is NOT auto-excluded, it is deferred for
> re-diagnosis, and it is disclosed as a deviation. A large excluded fraction indicates an
> LD-construction or variant-representation problem beyond isolated occlusion.

### 2.2 The three outcome branches, verbatim (`:73-75`)

> - BRANCH_AFR_OCC_NONE — the region contains no occlusion-undefined pair; the panel and
>   fine-mapping result stand unmodified.
> - BRANCH_AFR_OCC_EXCLUDED — the region contains ≥ 1 occluded variant under the anomaly
>   gate; the occluded variant(s) are excluded in lockstep (panel + sumstats) with manifest
>   entries, and fine-mapping proceeds on the reduced variant set; the manifest of excluded
>   variants is reported with the result.
> - BRANCH_AFR_OCC_DEFERRED — the region's occlusion-exclusion count exceeds the anomaly
>   gate; the region is deferred, not auto-excluded, and disclosed as a deviation with its
>   occlusion count.

And immediately after, `:77` — **the constraint that most disciplines the decision**:

> All three outcomes are reportable; excluding variants silently (without a manifest),
> fabricating a correlation value, or choosing the occlusion criterion to obtain a
> particular fine-mapping result are the only paths not on this list.

### 2.3 The deviation-logging commitment, verbatim (`:81`)

> - Pre-registration discipline: the occlusion criterion, the lockstep-exclusion rule, the
>   manifest requirement, the anomaly gate, and the three outcome branches are fixed before
>   any occlusion-handling code fires; deviations are logged in .planning/osf_deviations.md
>   and disclosed in the manuscript.

### 2.4 What is ACTUALLY pre-committed — a four-way decomposition

**(i) The 0.0005 constant — pre-committed, but the record itself discloses that it was
never calibrated for this quantity.** Clause (d) says so in its own parenthetical: *"the
same fractional gate as the withdrawn ceiling, re-purposed to exclusions."* The withdrawn
ceiling governed how many off-diagonal LD **cells** could be zeroed under NaN→0. The new
gate counts excluded **variants**. Different numerator (matrix cells vs variant records),
different denominator semantics, different failure mode. The number was carried across
because it was to hand, and the amendment says as much on the public record.

This is the strongest available ground for recalibration and it is *already disclosed*:
Carter is not correcting a hidden assumption, he is completing a substitution the
pre-registration explicitly labelled as inherited. That framing is honest and it is
supportable by quoting clause (d) against itself.

**(ii) The defer-not-exclude protocol — pre-committed, load-bearing, and it WORKED.**
"NOT auto-excluded … deferred for re-diagnosis … disclosed as a deviation." This is the
protective machinery, and it is the part that must not be touched. It fired on first
contact with real data and stopped the fire before anything was banked. Any amendment must
retain it verbatim.

**(iii) The interpretation sentence — pre-committed as a HYPOTHESIS, and it is now
TESTABLE.** *"A large excluded fraction indicates an LD-construction or
variant-representation problem beyond isolated occlusion."* This is a scientific claim, not
a procedure. Region 1 now provides one datum against it: the excluded fraction is 0.226%,
and the deletion burden generating it (7.76% multi-base-REF rows) is the ordinary WGS
figure (§4). So for region 1 the sentence's antecedent fires while its consequent appears
false — the fraction is "large" only relative to a mis-inherited constant, not relative to
the substrate.

But **one region cannot settle this**, and the sentence is precisely why. Its purpose is to
DISCRIMINATE anomalous regions from typical ones. Deciding whether 0.226% is "large"
requires knowing what typical is. That is the entire argument for Option C in §5.

**(iv) The occlusion CRITERION — pre-committed at clause (a), and NOT in question.**
`:55`: *"a variant record is flagged as an occluder when its reference-allele interval
[POS, POS + len(REF) − 1] covers the position of a neighboring variant."* The detector
implements this. Clause (a) is untouched by anything here, and `:77` fences it: changing
the criterion to obtain a particular result is prohibited. **Note carefully that the gate
(clause d) and the criterion (clause a) are different objects.** Recalibrating (d) is not
prohibited by (:77); changing (a) would be. Keeping that distinction crisp in any
amendment text is what keeps the action defensible.

### 2.5 The sanctioned deviation path

Two commitments, and they sit in **different places** — which matters:

- **`:81` is inside the PASTE block** → publicly pre-registered: deviations are logged in
  `.planning/osf_deviations.md` and disclosed in the manuscript.
- **`:98` is in the "Post-Paste Reference (do NOT paste this block)"** → an in-repo
  procedural commitment only, not part of the public record: *"If any commitment changes
  between posting and closeout: pause at the next wave boundary, log the deviation, and if
  an outcome-branch rule changes, post a subsequent amendment-update citing this record
  URL."*

So the publicly-visible obligation is `:81`; `:98` is the house rule that operationalises
it. Both point the same way. Also relevant: `:85` already commits that *"Realized outcome
branches, the per-region exclusion manifest, and the genome-wide present-rate are added as
a follow-up OSF update at the panel-rebuild closeout"* — i.e. **a follow-up OSF update is
already pre-registered as part of the plan.** Recalibration disclosure has a pre-committed
vehicle; it does not require inventing a new one.

**Net:** the sanctioned path is a subsequent OSF amendment-update that (1) corrects the
`:45` factual error, (2) recalibrates the (d) constant with the measurement that motivates
it stated in full, (3) retains the defer-not-exclude protocol and clause (a) unchanged, and
(4) is logged in `osf_deviations.md`. Silent modification of `_OCCLUSION_ANOMALY_FRACTION`
is excluded — by `:81`, by `:98`, and by the shipped source's own comment at
`run_native_ld_panel.py:129-130`.

---

## 3. RE-DERIVED ORACLE — what the gated test should defensibly assert

**Recommendation: option (c), both layers — but in TWO SEPARATE TESTS, and with the
derived layer strengthened well beyond what it asserts today.**

### Layer 1 (DERIVED) — strengthen and keep. This is the real known-answer test.

Everything the geometry verdict actually established is **per-locus and
window-size-independent**. Assert exactly that, and nothing about totals:

1. **Index → position mapping, not just index membership.** Today `:520-521` only checks
   *which indices* come back. Assert instead that the row at each oracle index carries the
   verdict's bp:
   `10328→1980475, 44784→5733487, 46714→5922718, 59097→7492693, 66730→8375822`.
   This is strictly stronger: it validates index origin AND that the file under test is
   the right window AND that the substrate has not shifted — three properties for free,
   all fully derived from `m3_region1_nan_geometry_verdict.md:15-22`. *(The bp↔index
   pairing itself needs one in-perimeter confirmation before it is pinned — see the
   caveat below.)*
2. **Containment, not equality:** oracle-5 ⊆ observed. Correct, derived, and it is what
   the probe already confirmed.
3. **Attribution edges.** Assert the verdict's five `ref_span_overlap` edges are present:
   `1980423→1980475`, `5733474→5733487`, `5922716→5922718`, `7492679→7492693`,
   `8375794→8375822`. Particularly assert `5922716→5922718` and **not** `5922724→5922718`
   — the pair-4 second-order attribution, the subtlest thing the verdict settled and the
   thing a wrong detector is most likely to get backwards.
4. **The 7 named deletions exist with their verdict spans** — as **(pos, len(REF)) pairs**,
   not as an inventory:
   `(1980423,60) (5733474,29) (5922716,7) (5922724,31) (7492679,31) (7492693,17) (8375794,29)`.
   This subsumes the span-inventory content, is immune to the scope error, and is a much
   sharper check than a sorted multiset ever was.

**Specifically for `:522-523`:** replace the inventory equality with #4. If a multiset form
is wanted as well, the defensible version is containment —
`Counter([60,29,7,31,31,17,29]) <= Counter(window_spans)` — but #4 dominates it, because
it anchors each span to its position.

**Caveat that must be honoured before #1 and #3 are pinned:** the *index→bp* pairing and
the *edge* set have not yet been directly observed on the real window. Probe 2 confirmed
index containment only. Both are cheap to confirm read-only (print the 5 rows and their
attributed occluders) and **must be measured before being asserted** — otherwise this
re-derivation repeats the original sin at smaller scale. Until then they are hypotheses
with very high prior, not oracle.

### Layer 2 (MEASURED) — a separate, loudly-labelled regression pin.

A second test, in its own function, whose name and docstring both carry
**MEASURED-NOT-DERIVED**, pinning today's substrate totals:
`n_rows=102421`, `n_deletion_rows=7951`, `n_occluded=231`, `max_span=170`.

- **Value:** catches substrate drift (a CDR refresh, a re-QC, a different cohort build)
  loudly instead of silently, and it is the only thing that would catch a future
  regression in the detector's *aggregate* behaviour.
- **Risk, stated plainly:** it pins today's cohort. A CDR v8→v9 refresh will break it, and
  a future reader may "fix" it by editing the number — the same failure mode that produced
  this session. Mitigations: the label in the name; a docstring that names the measurement
  provenance (probe 2, 2026-08-19, `afr_cohort.bim`, window 10000-13506933) and states
  that the correct response to a break is **re-measure and record**, never edit-to-green;
  and physical separation from Layer 1 so a substrate change cannot take the derived
  science down with it.
- **Do not merge the layers.** The whole defect being repaired is a measured observation
  wearing derived-science clothes.

### Also requiring attention (not assertions, but false state)

- `:188 _REGION1_REAL_SAME_POSITION_COUNT = 0` — re-scope to "same-position among the 6 NaN
  pairs = 0" (true, per verdict `:41-42`) or delete. As a window-wide constant it is false
  and currently unenforced, i.e. a trap for the next reader.
- `:201` comment "synthetic mirrors the real window" — now known false.
- `:154-183` oracle comment block — needs the scope correction recorded in place, and
  `:180-183`'s open index-origin item can be closed as CONFIRMED 0-based.
- `run_native_ld_panel.py:848-850` and `fire_verifier.py:490,595` — false comments in
  shipped source. Per the standing lesson *"a claimed invariant needs a named enforcer"*,
  these are belief statements with no enforcer; the enforcer that would have caught them
  is exactly the gated test that just fired.

---

## 4. SCIENCE ANALYSIS (for the memo)

### 4.1 Is 231/102,421 = 0.226% geometrically plausible? — YES, it is close to *required*.

Three independent lines, all consistent:

**(a) Density arithmetic.** Window 13,496,934 bp (13.497 Mb — **not 3.5 Mb as the brief
stated**; confirmed at `m3-region-class-projection.tsv:2` and `config/ld_regions.tsv:2`),
102,421 variants → 1 variant per 131.8 bp. Inverting the observation: 231 occluded implies
~30,441 downstream-covered bases, i.e. **~3.83 bp of downstream coverage per deletion**,
i.e. mean len(REF) ≈ 4.83. A mean deleted length of ~3.8 bp is the ordinary short-indel
spectrum (median 1-2 bp, mean lifted by a tail — here reaching 170 bp).

**(b) Forward model at real dimensions (run, NCSU, $0).** A synthetic window built from the
two measured aggregates alone — 102,421 uniform positions over 13,496,934 bp, 7,951
multi-base-REF rows, generic short-indel lengths — run through the **shipped** detector
yields **222 occluded** against the measured **231**. Within 4%.

**(c) External WGS check.** gnomAD v3 (71,702 WGS samples) reports ~602M SNVs and ~105M
indels — indels ≈ 14.8% of variants; deletions ≈ half of indels ≈ 7-8% of records. The
observed **7.76%** multi-base-REF fraction sits squarely there.

**Contrapositive, and this is the cleanest single fact in the whole dossier:** the oracle's
implied inventory of 7 deletions in 102,421 records is **0.0068%** — three orders of
magnitude below every WGS callset ever published, and ~1,140× below the measured value. No
real WGS window can have 7 deletions. The oracle was falsifiable from the armchair, with no
perimeter access, at any point in the last five weeks.

**On the review request's open question — reconciling "0 same-position" with the consecutive
runs: RESOLVED.** The claim's scope was "for all six [NaN pairs]"
(`m3_region1_nan_geometry_verdict.md:41-42`), not the window. The window-wide same-position
count has never been measured. The consecutive-index runs are fully consistent with
multiallelic-split and complex-indel loci — the very structure
`m3_nan_conditioning_scientific_review.md:46-49` named as the leading mechanism — and note
that split partners *sharing* a POS are **not** occluded (strict left bound); it is their
downstream neighbours inside the same footprint that are. There is no contradiction to
reconcile, only a scope that was dropped in transit.

**One genuine caveat about 7,951 as an EVENT count.** Hail `split_multi` emits one row per
ALT allele, so a multiallelic deletion site produces several multi-base-REF rows carrying
the same REF. 7,951 is therefore a **row** count and may overstate distinct deletion
**events**. This does not touch 231: `occluded_ids` is deduplicated per variant
(`occlusion_span_filter.py:254,263`), so multiallelic inflation of the occluder pool cannot
inflate the occluded count. The alarming number is the soft one; the number that matters is
robust.

### 4.2 What does excluding 0.23% of variants do to the panel scientifically?

**Nothing material — and the reasoning holds up under pressure, with one caveat worth
stating rather than waving past.**

1. **These variants have no recoverable LD to lose.** Per the verdict (`:47-51`): "The
   missingness is real biology (the base is absent on the deletion haplotype), so there is
   no 'true r' to recover." An occluded variant's LD is structurally undefined. Excluding
   it removes nothing that could have been validly used. This is the argument the posted
   amendment already makes at `:57`: *"An occluded variant's LD is genuinely undefined, so
   it cannot be validly fine-mapped at that locus regardless; lockstep exclusion is the
   honest realization of that fact."*
2. **Scale.** Ordinary panel QC (MAF, missingness, HWE) removes single-digit *percentages*.
   0.23% is an order of magnitude below routine attrition. Marginal effect on SuSiE
   credible-set width or coloc PP4 is negligible at that scale.
3. **Lockstep protects the join.** Clause (b) drops from panel and sumstats together, so
   the position-based join never carries a one-sided variant — the asymmetry that made
   both NaN→0 and panel-only exclusion unsafe.

**The caveat, stated rather than dismissed.** Occluded variants are *not* uniformly
distributed — they concentrate at complex indel loci, which are exactly the loci where
representation is hardest and where a causal variant could plausibly sit. The relevant
number is therefore not the global 0.23% but **the per-credible-set drop rate**. Clause (e)
(genome-wide present-rate reporting) is precisely the pre-registered instrument for this and
should be read at closeout with this in mind: if a credible set loses several members to
occlusion, that locus needs flagging regardless of the global fraction. The right posture is
"globally negligible, locally auditable via the clause-(c) manifest" — not "negligible,
move on".

### 4.3 What would the ceiling need to be, and on what defensible basis?

To pass region 1 at all: > 0.2255%, i.e. > 4.51× the current constant. But **"what makes
region 1 pass" is the wrong question and must not be the stated basis** — that is the
reasoning `:77` fences off. Defensible bases, ranked:

| Basis | Form | Defensibility |
|---|---|---|
| **Empirical percentile across regions** | defer when a region's occluded fraction exceeds e.g. the 99th percentile of the measured genome-wide distribution, or a fixed constant set ≥ some multiple of the observed maximum | **STRONGEST.** Restores clause (d)'s actual purpose — discriminating anomalous regions from typical ones — and the threshold is set by the substrate, not by the region that failed. Requires §4.4. |
| **Fraction of the region's deletion count** | e.g. `n_occluded ≤ k × n_deletions` | **STRONG, and arguably the most principled form.** Occlusion is mechanistically driven by deletion burden × variant density, so normalising by deletion count makes the gate detect *disproportionate* occlusion rather than merely *abundant* deletions. Region 1: 231/7,951 = 2.9%. Still needs a k, hence still needs §4.4 — but it is the shape that best matches the physics. |
| **Analytic expectation** | defer when observed exceeds N× the density-model prediction `ρ × Σ(len(REF)−1)` | Elegant and self-calibrating per region, but adds a model to a pre-registration; more surface to defend. |
| **Any constant chosen so region 1 passes** | — | **NOT DEFENSIBLE.** Post-hoc tuning against the region that motivated the change. |

**Flag, prominently: only ONE region has been measured.** 231 may be typical or may be
region 1 telling us chr1p is indel-dense. Every recalibration basis above needs a
distribution.

### 4.4 The multi-region measurement pass — what it would actually take

Occlusion counts are computable **without any LD**: `.bim` coordinates only, no plink, no
matrices, no genotypes, no banking. Egress is counts — same class as the June diagnostics
the amendment itself cites at `:43` as its evidentiary base.

**Mechanics (no new algorithm required):** loop the 276 AFR rows of `config/ld_regions.tsv`;
for each, call the shipped `run_native_ld_panel._window_bim_n_var(bim_path, chrom, from_bp,
to_bp)` then `occlusion_span_filter.detect_occluded_variants(rows)`. Record per region:
`region_id, n_var, n_deletion_rows, n_occluded, max_span, n_same_position`. Using shipped
functions means **no new detection code to validate** — the driver is a loop.

**⚠ COST — the brief's "minutes, ~$0" premise is wrong; I measured it.** The rule is
O(n_variants × n_deletions) — ~8.1e8 comparisons for region 1. Timed on an NCSU node with
the **shipped** detector on a region-1-shaped window: **168 s for one region.**

| Scope | Wall time | Approx VM cost | Yield |
|---|---|---|---|
| ~20-region stratified sample (spanning the `n_var` range in `config/ld_regions.tsv`) | **~1 h** | ~$0.50 | central estimate + rough spread; almost certainly enough to establish that ~0.2-0.3% is baseline |
| all 276 regions, shipped detector unchanged | **~10-13 h** | ~$5 | full distribution, exact percentiles, the complete `:45` factual correction |
| all 276 with an interval-sweep rewrite | minutes | ~$0 | same — **but** new code on the critical path, requiring validation against the shipped detector's 231. Not worth it at these prices. |

**Second-order finding from the same measurement:** ~168 s/region is *already* on the
Stage-C fire path 276 times ≈ 10 h of the 11-day budget. Not a blocker, but it means the
measurement pass is essentially "the occlusion-detect portion of the fire, run standalone"
— and if it is run, its per-region results can be diffed against Stage C's later as a free
consistency check.

**Also collect `n_same_position` per region.** It costs nothing extra, it closes the open
`_REGION1_REAL_SAME_POSITION_COUNT` question, and it directly tests clause (d)'s
interpretation sentence: widespread same-position records *would* be the
variant-representation problem the sentence contemplates, and their absence *would* confirm
the occlusion is ordinary geometry.

---

## 5. OPTIONS MEMO FOR CARTER

**Situation in one line.** The detector is right, the oracle was wrong, region 1 defers
against a ceiling whose calibration premise is measured false, nothing is banked, and one
sentence of the *posted* pre-registration is factually incorrect.

**A precondition that binds under every option.**
`osf-amendment-…-2026-07-10.md:45` — *"Region 1 alone contains 7 distinct overlapping
deletions (60/29/7/31/31/17/29 bp)"* — is on the public OSF record and is measured false.
Correcting it is required by `:81` regardless of which option is chosen. It is not a
bargaining chip and it is not deferrable to closeout convenience.

---

### Option A — cheap Stage-A probe fire; let region 1 land the deferral, then amend

**What actually happens, mechanically.** `run_native_ld_panel.py:853` computes
`231 > 51.2105` → status `"deferred_occlusion_anomaly: 231 occluded of 102421 (ceiling
51)"`; the region returns at `:861` **before** excludelist, manifest, or plink; a panel-TSV
row is appended at `:860`; then `--fail-fast` raises `RegionGateError` at `:1161-1162` and
Stage A **halts**. The subsequent runbook manifest check (`AGENT-PROMPT.md:196`) finds
nothing, because no manifest was written. `fire_verifier` then returns three reds:
`occlusion_anomaly_ceiling` FAIL/HARD_STOP, `stage_a_manifest_rows` FAIL-CLOSED/HARD_STOP
(absent file), `region1_status` FAIL/FINDING.

- **Cost / time:** minutes of VM time; plink never runs, so the "hour-plus" is skipped. ~$1-2.
- **OSF visibility:** none at the time of firing; the deferral becomes disclosable material.
- **Rigor posture:** superficially attractive — "the pre-registered gate fired on real data"
  is a good thing to be able to show.
- **The decisive objection: information yield is ZERO.** Probe 2 *already ran the shipped
  `load_bim_rows` + `detect_occluded_variants` over the same window from the same
  `afr_cohort.bim`*, and the gate at `:853` is arithmetic over that same 231 and that same
  102,421. Option A spends VM time and banks a panel row to re-derive a number already in
  hand, read-only, at $0.
- **Second objection, and it is a rigor objection.** Banking a deferral against a ceiling
  you have *already established is mis-calibrated* records a known-mis-calibrated gate
  firing. That is a worse artifact than no artifact — it puts a number on the record whose
  interpretation you already intend to retract.
- **Risks:** changes the current clean state ("nothing banked"); creates a panel-TSV row
  that must itself be explained at closeout; consumes a fire window for no new information.

### Option B — amend clause (d) first, then fire

- **Cost / time:** $0 compute. Carter's drafting time + Seth review + OSF post; ~days.
- **OSF visibility:** full and immediate — a new amendment-update citing `trsx5`, which is
  exactly the vehicle `:98` and `:85` already anticipate.
- **Rigor posture:** honest in *process*, weak in *basis*.
- **The objection: you would be setting a discriminating threshold from n = 1** — and from
  the single region whose failure prompted the change. Clause (d) exists to separate
  anomalous regions from typical ones (`:61`: *"A large excluded fraction indicates an
  LD-construction or variant-representation problem beyond isolated occlusion"*). Without a
  distribution you cannot say what "large" is, so any new constant is either arbitrary or
  reverse-engineered from region 1. `:77` prohibits *"choosing the occlusion criterion to
  obtain a particular fine-mapping result"* — recalibrating the *gate* (d) is not the same
  object as the *criterion* (a), so this is not literally prohibited, but a hostile reviewer
  will not grant that distinction unprompted, and you would be handing them the opening.
- **Risks:** meaningful chance of amending twice (if the 276-region distribution later shows
  regions at 1-2%, the n=1 constant is wrong again); the disclosure would have to say "we
  set the new threshold from the one region we had", which is a weak sentence to have to
  write in a pre-registration.

### Option C (RECOMMENDED) — measurement pass → amend from data → fire

1. Restart the VM; run the **shipped** detector over per-region `.bim` windows. Start with a
   ~20-region stratified sample (~1 h, ~$0.50); extend to all 276 (~10-13 h, ~$5) if the
   sample shows spread. No LD, no plink, no banking, no `.npz`, no GCS writes. Record
   `n_var, n_deletion_rows, n_occluded, max_span, n_same_position` per region.
2. Draft the amendment-update from the measured distribution: correct `:45`; recalibrate the
   (d) constant on an empirical-percentile or per-deletion-fraction basis (§4.3); retain the
   defer-not-exclude protocol and clause (a) **verbatim**; log in `osf_deviations.md`.
3. **Seth adversarially reviews the text brief-blind, BEFORE any OSF-visible action.**
4. Post. Then repair the test oracle per §3 (derived layer + separately-labelled measured
   layer). Then fire.

- **Cost / time:** ~$0.50-5 compute; ~1 day of measurement + drafting, plus Seth's turnaround.
- **OSF visibility:** full, and — this is the point — the disclosure gets to *lead with a
  measurement* rather than with a retraction.
- **Rigor posture: strongest available, by a clear margin.**
- **Why it dominates B.** It is the only option that makes the recalibrated gate
  *scientifically meaningful* rather than merely permissive. With the distribution in hand
  the amendment can say: *"the inherited 0.0005 was carried over from a NaN-cell ceiling, as
  clause (d) itself discloses; measurement across N regions shows the substrate's baseline
  occlusion fraction is X% (median), Y% (max); the gate is re-set to Z on that basis and
  continues to defer genuinely anomalous regions."* That is a threshold set by the substrate.
  B's is a threshold set by the accident that region 1 is region 1.
- **Why it dominates A.** A buys an artifact and no information. C buys the information that
  makes the artifact meaningful — and if Carter still wants the deferral-on-the-record, C can
  produce it afterwards against the *correct* ceiling, where it will actually mean something.
- **It also directly tests clause (d)'s own pre-registered hypothesis** (§2.4-iii). If every
  region sits near 0.2%, that IS the finding: 0.2% is baseline, not anomaly. If a handful
  spike, those are the real anomalies clause (d) was written to catch — and the recalibrated
  gate must still catch them. Either result is publishable and honest.
- **Precedent:** the amendment's own evidentiary base (`:43-47`) is *"in-perimeter aggregate
  diagnostics run after that amendment posted"*. Running a coordinate-only diagnostic before
  amending is the pattern this record already established and defended.
- **Risks:** perimeter contact and a VM restart (small, and the VM must restart for the fire
  anyway); ~1 day of calendar; the measurement could surface something new — which is a
  benefit disguised as a risk, and far better surfaced now than 11 days into a $385-1,084 run.

---

### Recommendation

**Option C.** The reasoning laid bare, in four steps:

1. **A is dominated on information.** Everything A would learn, probe 2 already measured
   read-only at $0. Firing to re-learn 231 is spending money for an artifact, and the
   artifact is a known-mis-calibrated gate firing.
2. **B is dominated on basis.** Clause (d) is a *discriminating* threshold. n = 1 cannot
   calibrate a discriminator, and the one datum you have is the region that failed. Any
   constant chosen there is either arbitrary or reverse-engineered, and both are bad
   sentences to write into a pre-registration.
3. **C is the only option that makes the fix mean something.** It converts "we picked a
   bigger number because the old one fired" into "we measured the substrate and set the
   threshold from it" — and it costs about $5 and a day.
4. **It matches the project's own standing rule** (*"in any gray-area trade-off, take the
   more rigorous, reviewer-defensible option; timeline is not a binding constraint"*), and it
   is the option that survives the specific attack a reviewer will actually mount: *"you
   changed your pre-registered threshold after it failed — on what basis?"* Under C the
   answer is a distribution. Under B it is region 1.

**Standing condition on all of C's OSF-visible steps:** Seth reviews the amendment text
adversarially and **brief-blind** before anything is posted. The precedent is explicit — the
2026-08-12 lesson (*"internal validation cannot catch a mis-specified premise"*) is the exact
failure mode that produced this session's bug: a harness, a checker and a verifier all
enforced a premise that no one had measured. The gated test is what finally caught it, on
first contact with reality, five weeks late. Do not let the amendment text ship on internal
review alone.

**One sequencing note.** The `:45` factual correction is required under every option and does
not depend on the measurement — but it should be *posted together with* the recalibration
rather than separately, so the record carries one coherent update instead of two partial
ones. The measurement pass supplies the correct number for `:45` as a free by-product.

---

## 6. IN-SESSION PROBE EVIDENCE — banked verbatim

### Probe 2 (structural; mirrors the test's own loading — `osf.load_bim_rows` + `detect_occluded_variants` over `data/aou/region1_window.bim`), in-perimeter, read-only:

```
n_rows: 102421
n_occluded: 231
oracle_subset_of_observed: True
oracle_missing_from_observed: []
n_deletion_REF_rows: 7951
max_span: 170
clause_d_ceiling_this_window: 51.2105
```

### Probe 1 (`-vv` full set diff) — summary as relayed:

Full capture banked on the VM at `/home/jupyter/step7_vv.txt` (NOT retrievable NCSU; VM
STOPPED). Structural features reported by the in-perimeter agent:

- the extra members often come in **consecutive-index runs** — `65340-65343`,
  `71567-71573`, `101915-101920`;
- the **oracle members appear unmarked in the diff** (subset confirmed).

### Failure shape, as relayed:

Assertion at `tests/m3/test_occlusion_span_filter.py:521` failed with ~226 extra members;
`:523` (span inventory) would fail with 7,944 extra deletions. **No shift, no displacement,
nothing missing.**

### Provenance / discipline note carried with the probes:

Both probes were run in-perimeter by the Workbench-side agent under R3 stop discipline; the
VM is now STOPPED. Nothing fired, Stage A was never reached, nothing was banked, the
deferral machinery was never exercised, and no test, frozen file, or pre-registered constant
has been edited. No OSF contact by any agent.

### Locally-derived measurements added by THIS session (NCSU, $0, no perimeter contact):

```
window span            = 13,496,934 bp (13.497 Mb)   [10000..13506933 inclusive]
variant density        = 7.5885e-03 var/bp = 1 per 131.8 bp
multi-base REF frac    = 7,951 / 102,421 = 7.7631%
occluded frac          =   231 / 102,421 = 0.2255%
clause-(d) ceiling     = 0.0005 x 102,421 = 51.2105   (observed = 4.51x ceiling)
implied covered bases  = 30,441 (0.2255% of window)
implied downstream coverage per deletion = 3.83 bp  =>  mean len(REF) ~ 4.83

FORWARD MODEL, shipped detector on a region-1-SHAPED synthetic window
(102,421 uniform positions over 13,496,934 bp; 7,951 multi-base REF;
 len(REF) = 2 + int(Exp(mean 3)) capped at 170):
    rows=102421  deletions=7951  occluded=222  elapsed=168.0s
  -> predicts 222 vs the measured 231 (within 4%)
  -> shipped-detector throughput: 168 s per region-1-shaped window
  -> 276 regions, code unchanged: ~10-13 h
  -> 20-region stratified sample:  ~1 h
```

External check: gnomAD v3 (71,702 WGS samples) ~602M SNVs / ~105M indels → indels ≈ 14.8%
of variants; deletions ≈ 7-8% of records. Observed 7.76% is ordinary. The oracle's implied
0.0068% is impossible.
