---
phase: quick/260806-pd3
plan: 01
subsystem: m3-ld-read-path
tags: [ld-panel, finemap, freeze, blast-radius, provenance, receipt, m3]
requirements: [BR-K1]
baseline_rev: 63453db
commits:
  - bf04199  # T1: the one-line deletion + AUTH-K1-TEST + the new module
  - 9538af0  # T2: the re-pin cascade + decoder-ring coherence + registries
new_freeze_pin: bf04199
requires:
  - quick/260805-o7o
  - quick/260805-w7u
  - quick/260806-b77
provides:
  - "variant_catalog_fallback restored to ONE meaning (Path-1 AFR empty-subset revert)"
  - "a five-outcome variant_catalog_fallback_cause decoder that stays true after K-1"
  - "run_susie_rss.R re-frozen at bf04199"
affects:
  - src/legacy/region_analysis/scripts/run_susie_rss.R
  - src/snakemake/rules/finemap.smk
key-files:
  created:
    - tests/m3/test_variant_catalog_fallback_legacy_semantics.py
  modified:
    - src/legacy/region_analysis/scripts/run_susie_rss.R
    - src/snakemake/rules/finemap.smk
    - src/snakemake/scripts/ld_allele_join.R
    - tests/m3/test_ld_read_path.py
    - tests/m3/test_finemap_receipt_early_exit.py
    - tests/m3/test_qtl_coloc_allele_join.py
    - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
metrics:
  tasks: 3
  files: 8
  tests_m3: "822 passed / 31 skipped / 0 failed"
  tests_phase2: "136 passed / 1 skipped / 0 failed"
  cost: "$0 — NC State only, zero perimeter contact, AoU fire NOT triggered"
  completed: 2026-08-06
---

# quick/260806-pd3: Close blast-radius finding K-1 Summary

**One-liner.** Deleted the single line that made the Path-2 (`ld_overlap == 0`)
retry overload the pre-existing `variant_catalog_fallback` key, restoring its one
legacy meaning; re-froze `run_susie_rss.R` at `bf04199` and gave the receipt's
`variant_catalog_fallback_cause` decoder a fifth outcome so it still tells the
truth afterwards.

**Commits.** `bf04199` (T1) → `9538af0` (T2). Base `63453db`, branch
`m3-W2-aou-deltas`.

---

## 1. THE GATE ROW — and only this one

| Gate row (`m3-04c-BLAST-RADIUS.md:133-144`) | Before | After |
|---|---|---|
| **Publishing the panel provenance** (I, J, K) | PARTIAL — I and J closed, **K DEFERRED** | **CLEARED** — K-1 closed here |

**This is the only gate row this plan touches.** A-J, L, M, E-2 and G-2 are not
re-opened. **No number moves** — no PIP, credible set, `ld_overlap`, `ld_status`
or `d3b_ld_z_consistency_s` depends on this flag, and that is asserted
mechanically (see §3), not assumed. Track A is untouched: **0** files under
`results/` or `src/python/` changed. m3-06 stays HELD (`condition_ld_matrix` /
`nan_to_num` token scan over the whole diff = **0**).

**This says nothing about the AFR results.** It is a reporting-flag closure.

---

## 2. WHAT LANDED

**The R edit (`bf04199`).** One line — `variant_catalog_fallback <- TRUE` —
deleted from the Path-2 brace block, plus the comment above it reworded. The
branch still reverts to `subset_base`, still retries exactly once, still sets
`ld_overlap_zero_fallback <- TRUE`, which is still emitted in the success JSON
and still read by the `finemap.smk` receipt. **Nothing became invisible.**

Measured after: `variant_catalog_fallback <- TRUE` occurs **exactly once**,
inside Path 1. `:787` / `:788` / `:916` / `:936` / `:968` unmoved and
byte-identical. `PARSE_OK`.

**The authorized test edit.** `test_ld_read_path.py`'s Path-2 parity assertion
was **INVERTED, not deleted** — `not in branch` with the K-1 rationale. The
`_brace_block(...)` anchor line is **byte-identical** (proved by `cmp`), the
file's `def test_` count is unchanged at 8, and all three diff hunks carry the
`def test_path2_ld_overlap_zero_fallback_is_observable_and_read` context marker.

**The new module** `tests/m3/test_variant_catalog_fallback_legacy_semantics.py`
— 11 node IDs, **0 skips**, pure source-text + `git` (no R, no Snakemake, no
toolchain fixture, so it is structurally incapable of skipping).

**The re-pin cascade (`9538af0`).** Both FREEZE constants moved to `bf04199`;
the decoder gained `path2_ld_overlap_zero_RETRY`; K-1 marked CLOSED and the
`ld_allele_join.R` extraction registered as a new open deferral.

---

## 3. VERIFICATION — every number measured AFTER commit 2

| # | Criterion | Observed |
|---|---|---|
| 1 | `tests/m3` | **822 passed / 31 skipped / 0 failed** (864.52s) |
| 2 | `tests/phase2` | **136 passed / 1 skipped / 0 failed** (skip = `bedtools not available`) |
| 3 | `snakemake --list` rc 0 | `OK` on `pipeline.yaml` + `lsweep_L{15,20,30}_overlay.yaml` |
| 4 | `git diff --exit-code bf04199 -- run_susie_rss.R` | clean |
| 5 | `Rscript -e 'parse(...)'` | `PARSE_OK` (also `LD_ALLELE_JOIN_PARSE_OK`) |
| 6 | `src.count("variant_catalog_fallback <- TRUE") == 1`, inside Path 1 | yes |
| 7 | scope diff == `files_modified` | exactly the 8 files, nothing else |
| 8 | 0-diff on `plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py`, 6 occlusion modules | all 0-diff |
| 9 | m3-06 token scan | 0 |
| 10 | AoU token scan (`gsutil\|gcloud\|bq\|dataproc\|hailctl\|wb`) | 0 |
| 11 | `results/` or `src/python/` touched | 0 |
| 12 | `sparse_parent_benchmark.tsv` | restored, not staged, not committed |

**Baseline for comparison:** `tests/m3` was **807 passed / 31 skipped** at
`63453db` (measured this session before any edit, 863.90s).

### Per-module delta reconciliation (+15, as the plan predicted)

| Module | Before | After | Δ | Why |
|---|---|---|---|---|
| `test_variant_catalog_fallback_legacy_semantics.py` | — | 11 | **+11** | NEW. 7 `def test_`, one of them `parametrize`d over 5 named MUST-NOT-MOVE regions → 6 + 5 = 11 |
| `test_finemap_receipt_early_exit.py` | 17 | 21 | **+4** | `def test_` 12 → 15 (token-distinctness, NC-K5, NC-K6) plus the decoder's 5th parametrised case (4 → 5) |
| `test_ld_read_path.py` | 8 | 8 | 0 | assertion inverted in place |
| `test_qtl_coloc_allele_join.py` | 40 | 40 | 0 | SHA + prose only |
| | **807** | **822** | **+15** | fully accounted for |

### Skip attribution — all 31 pre-existing, ZERO from the new module

| Module | Skips | Reason |
|---|---|---|
| `test_aou_ld_panel_local.py` | 19 | 18 × `could not import 'hail'`, 1 × SKELETON (Gate C structured-missingness fixture) |
| `test_build_ld_region_manifest.py` | 10 | 8 × chain file absent, 1 × M2 union BED absent, 1 × hail not installed |
| `test_ld_npz_to_rds.py` | 1 | hail |
| `test_occlusion_span_filter.py` | 1 | AoU perimeter / real `.bim` absent |
| **`test_variant_catalog_fallback_legacy_semantics.py`** | **0** | pure source-text + git by construction |

---

## 4. NEGATIVE CONTROLS — NC-K1 … NC-K7

**Four are PERMANENT and in-suite** (they run on every suite invocation, need no
revert, and cannot decay into a claim). **Three were OBSERVED RED once** and are
quoted raw below. **None reverts a file on disk and re-imports**, so none can be
defeated by the `.pyc` bytecode cache.

### PERMANENT, in-suite

| ID | Test | What it proves |
|---|---|---|
| **NC-K1** | `test_nc_k1_the_same_walk_finds_the_line_at_the_pre_k1_revision` | The identical brace-walk over `dc4bbd2` finds the line and counts **2** — so "not in the Path-2 block" is not "the extractor is reading the wrong block" |
| **NC-K2** | `test_nc_k2_splicing_the_line_back_in_memory_turns_the_predicate_red` | Splicing the line back into an **in-memory** copy of today's source raises `AssertionError`; then asserts `SUSIE_R.read_text() == src` — the control never wrote the tree |
| **NC-K5** | `test_nc_k5_the_pre_k1_decoder_called_a_real_path2_revert_none` | The `63453db` receipt on the post-K-1 `(false, true)` fixture prints `none`; the live one prints `path2_ld_overlap_zero_RETRY`. Reproduces the incoherence rather than arguing it |
| **NC-K6** | `test_nc_k6_a_naive_substring_match_cannot_separate_the_two_path2_tokens` | A naive `... path2_ld_overlap_zero` substring matches **both** path2 outputs while the delimiter-aware matcher separates them |

### OBSERVED RED — raw output

**NC-K3 — the authorized `test_ld_read_path.py` assertion can fail.** Driven
against the in-memory spliced source through the *same* `_brace_block` walker
the suite imports:

```
NC-K3 RESULT: RED (as required)
AssertionError: Path 2 must NOT set the legacy variant_catalog_fallback key (K-1): it is a pre-existing key whose meaning is the Path-1 AFR empty-subset revert
working tree untouched: True
```

**NC-K4 — the one-assignment-site count assertion can fail.** Driven against
`git show dc4bbd2:...`:

```
NC-K4 RESULT: RED (as required)
AssertionError: 'variant_catalog_fallback <- TRUE' occurs 2 times; K-1 requires exactly 1 (the Path-1 AFR empty-subset revert)

live source count (must be 1): 1
dc4bbd2 count      (must be 2): 2
working tree untouched: True
```

**NC-K7 — the re-pin actually re-pinned.** Before the T2 edit, against the stale
`dc4bbd2`:

```
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['git', 'diff', '--exit-code', 'dc4bbd2', '--', 'src/legacy/region_analysis/scripts/run_susie_rs...
FAILED tests/m3/test_finemap_receipt_early_exit.py::test_run_susie_rss_r_is_still_frozen_at_its_pin
1 failed in 0.11s
```

After the edit, against `bf04199`:

```
.                                                                        [100%]
1 passed in 0.03s
```

and the forward gate directly: `git diff --exit-code bf04199 -- run_susie_rss.R`
→ `R_FILE_0_DIFF_AT_bf04199`.

**One further control fired unplanned and is reported in §6 (deviation D-1):**
the new module's own non-vacuity guard on the symbol-scoped diff went RED and
caught a plan-fact error.

---

## 5. THE SHA CLASSIFICATION TABLE

Swept **every** 7-hex literal in the touched modules, not only `dc4bbd2`.
21 hits / 4 distinct SHAs at commit 1 (the plan measured 19 at `63453db`; the
+2 are this plan's own `PRE_K1_REF`).

| Site | SHA | Bucket | Action |
|---|---|---|---|
| `test_finemap_receipt_early_exit.py::FROZEN_R_REV` | dc4bbd2 → **bf04199** | **FREEZE pin** | **RE-PINNED** |
| `test_finemap_receipt_early_exit.py` module docstring | dc4bbd2 → **bf04199** | live prose naming the pin | **RE-PINNED** (+ provenance note) |
| `test_qtl_coloc_allele_join.py::FREEZE_REF` | dc4bbd2 → **bf04199** | **FREEZE pin** | **RE-PINNED** |
| `test_qtl_coloc_allele_join.py:57` prose | dc4bbd2 → **bf04199** | live prose naming the pin | **RE-PINNED** |
| `ld_allele_join.R:33`, `:58` | dc4bbd2 → **bf04199** | live prose naming the pin | **RE-PINNED** |
| `finemap.smk` J narrative | dc4bbd2 → **bf04199** | live prose naming the pin | **RE-PINNED**, J's claim preserved verbatim in substance |
| `test_qtl_coloc_allele_join.py:1296` | **dc4bbd2** | **HISTORICAL** (AUTH-b77-01's preserved record) | **ANNOTATED, NOT REWRITTEN** — re-pinning would falsify history |
| `test_variant_catalog_fallback_legacy_semantics.py::PRE_K1_REF` | **dc4bbd2** | **DIFFERENTIAL SUBSTRATE** | untouched — must stay forever |
| `test_finemap_receipt_early_exit.py::PRE_K1_SMK_REF` (NEW) | **63453db** | **DIFFERENTIAL SUBSTRATE** | annotated never-re-pin; NC-K5's substrate |
| `test_finemap_receipt_early_exit.py::PRE_CHANGE_REF` (+3 prose) | **6b427bc** | **DIFFERENTIAL SUBSTRATE** | untouched |
| `test_qtl_coloc_allele_join.py::PRE_CHANGE_REF` (+3 prose) | **7b1025d** | **DIFFERENTIAL SUBSTRATE / HISTORICAL** | untouched |
| `finemap.smk:72`, `:119`, `:347` | **3f431ab** | **HISTORICAL** (pre-m3-04c behavioural baseline; each self-annotating in context — "reproduces 3f431ab's expression character-for-character") | untouched |

**Post-state: no FREEZE pin names `dc4bbd2` anywhere.** Every surviving
`dc4bbd2` hit is an annotated HISTORICAL narrative or a DIFFERENTIAL SUBSTRATE.
`5ec33bd` / `0378ec8` confirmed absent from these files, as the plan said.

### AUTH-K1-REPIN containment, quoted

```
 .../m3-aou-afr-ld-panel-build/deferred-items.md    | 151 +++++++++++++++-
 src/snakemake/rules/finemap.smk                    |  85 +++++----
 src/snakemake/scripts/ld_allele_join.R             |  73 ++++++--
 tests/m3/test_finemap_receipt_early_exit.py        | 189 +++++++++++++++++++--
 tests/m3/test_qtl_coloc_allele_join.py             |  15 +-
```

* `test_qtl_coloc_allele_join.py` — every changed line is the SHA string or
  annotation prose. **No assertion changed.**
* `ld_allele_join.R` — `NO NON-COMMENT LINE CHANGED` (mechanically verified).
* `finemap.smk` — **exactly one** non-comment line changed: the `{PYTHON_BIN} -c`
  receipt. Everything else is comment.
* `test_finemap_receipt_early_exit.py` — the only non-comment removals are the
  module docstring prose, `FROZEN_R_REV`, three parametrize tuples (re-narrated),
  the test docstring, and the assertion replaced by its delimiter-aware form.
  All inside the allow-list; `PRE_CHANGE_REF`, NC-J1, NC-J2, the freeze helper
  and the two shell-constraint tests are untouched.

**Re-verified after the receipt edit:**
`--ld-allele-aware {params.ld_allele_aware}` × 1; `{PYTHON_BIN} -c` × 1; **all
15** `d.get('<key>')` literals preserved; `snakemake --list` rc 0.

---

## 6. DEVIATIONS — named, not silently absorbed

### D-1 (material). The symbol-scoped diff test could not have been green in commit 1 as specified — caught by its own non-vacuity guard

T1 STEP 3(f) specifies `git diff PRE_K1_REF HEAD -- <file>`. That compares two
**commits**, but T1's own `<done>` requires the new module to pass **before**
commit 1 exists. Observed RED on the first run:

```
E  AssertionError: git diff dc4bbd2 HEAD -- src/legacy/region_analysis/scripts/run_susie_rss.R is EMPTY;
   K-1's deletion is not in the tree, so this assertion would be measuring nothing
1 failed, 10 passed in 0.59s
```

**Fix:** `git diff PRE_K1_REF -- <file>` (working tree). This is strictly
*tighter* in time — it also catches an uncommitted regression — and makes (f)
consistent with (a), (d), (e), (g), which all read `SUSIE_R.read_text()`. Once
committed the two forms agree, because the freeze gate independently requires
the working tree to be clean. **The assertion was not weakened**; the substrate
was made consistent with its siblings. Documented in the test's docstring.

*This is the plan's own guard doing exactly its job: the non-vacuity assertion
the plan mandated is what surfaced the plan's error.*

### D-2 (material). The artifact census in the plan is wrong in BOTH directions — the K-1 entry's 1,957 is substantially right, and the plan's "44 measured" is an artefact of a non-symlink-following grep

The plan instructed me to report "1,957 is NOT reproducible on this node (44
measured, all `false`)" as a deviation and to write "44/44 measured on this node"
into the R comment. **I did not write that, because it is false.**

`results/legacy/region_analysis` is a **symlink**. `grep -r` does not follow
symlinked directories; `grep -R` does. Measured 2026-08-06:

| Measurement | Value |
|---|---|
| `grep -rl` (plan's method), region JSONs carrying the key | 35 (+1 `.planning/HANDOFF.json`, prose) — the "44" is of this family |
| **`grep -Rl` (correct), region JSONs carrying the key** | **1,944** |
| — of which `variant_catalog_fallback: false` | **1,935** |
| — of which `variant_catalog_fallback: true` | **9** |
| JSONs carrying `ld_overlap_zero_fallback` | **0** |
| Total JSONs under `results/legacy/region_analysis` | 2,596 (so **687** carry the key not at all → `key_absent`) |

So the K-1 entry's **1,957** was essentially correct (1,944 here).

**And the correction strengthens K-1's premise rather than weakening it.** The
9 `true` artifacts are all AFR — `asthma.AFR.RAD50_peak__tile1` and eight
`t2d.AFR.PYHIN1_1q23__tile*` — and **none** carries `ld_overlap_zero_fallback`.
They are genuine **Path-1** reverts. `true` already meant Path-1 on real
artifacts, so the m3-04c overload would have collided with them in exactly the
automated comparison K-1 describes. I wrote the corrected census into the R
comment, the `finemap.smk` decoder table, `deferred-items.md` and the `:488`
comment fix.

**Still true, and stated plainly:** **0** artifacts on this node were produced
from an m3-04c-window tree (0 carry `ld_overlap_zero_fallback`), so **no
before/after JSON diff was performed and none was possible.** The closure is
proven on **source text and receipt fixtures**.

### D-3 (plan-fact, confirmed as the plan predicted). `AUTH-K1-TEST`'s span

The grant text says `:451-453`; the live statement is **four** lines
(`:451` assert, `:452-453` message, `:454` closing `)`). The plan's correction
to `:451-454` was right. I replaced the whole statement; git minimised the hunk
to `-451,3 +469,3` because the closing `)` is identical on both sides — **no
dangling paren**.

### D-4 (plan-fact, confirmed). `test_ld_read_path.py:449` is a comment

`# the Path-2 branch sets BOTH` — a comment, not a docstring, and it became
false. Reworded to
`# the Path-2 branch records itself with ld_overlap_zero_fallback ONLY (K-1)`.

### D-5 (plan-fact, confirmed). `run_qtl_coloc.R` path resolution

The original brief claimed a `--ld-allele-join` CLI arg threads the path.
It does not: `--ld-allele-join` (`run_qtl_coloc.R:62`) is a **boolean**, and the
path is resolved script-relatively at **`run_qtl_coloc.R:153`** —
`LD_ALLELE_JOIN_R <- file.path(.script_dir(), "ld_allele_join.R")`. Verified by
direct read; recorded in both registries.

### D-6 (plan-fact, confirmed). `test_qtl_coloc_allele_join.py:1296` is historical

Annotated, not re-pinned — re-pinning would falsify the record of why
AUTH-b77-01 was needed.

### D-7 (minor, reported for completeness). The success emit's LINE NUMBER moved; its BYTES did not

The plan lists `:1208` as MUST NOT MOVE. The authorized comment reword is longer
than the comment it replaces (6 lines → 19), so the success emit now sits at
`:1221`. **Its content is byte-identical**, asserted by
`test_the_five_must_not_move_sites_are_byte_identical[success_payload]`, as are
`:787`/`:788`/`:916`/`:936`/`:968`, which did not shift at all. I checked
whether anything pins the R file by line number in an executable assertion:
**nothing does** — every line-number reference (`:220`, `:275`, `:466`, `:611`,
`:184`, `:522-529`) is prose, and all sit **above** the edit point, so all remain
correct. I chose the informative comment over a length-matched one because the
plan requires four substantive claims in it, including the corrected census.

### D-8 (minor). Scratch-harness `sys.path` ordering

Running the NC-K3/NC-K4 harness outside pytest initially failed on
`from conftest import R_SUBPROCESS_TIMEOUT_S` — the bare `conftest` module is the
**root** `tests/conftest.py`, which shadows `tests/m3/conftest.py` under pytest.
Fixed by putting `tests/` ahead of `tests/m3/` on `sys.path` in the scratch
script only. **No repo file was involved.**

**No deviation required a Rule 4 (architectural) STOP. No unexpected red
pre-existing test occurred at any point.**

---

## 7. THE `ld_allele_join.R` EXTRACTION: **DEFERRED**

Evaluated on the merits against an **open** freeze window and declined —
recorded in `deferred-items.md` as new open item **K-2** and in
`ld_allele_join.R` section (d).

1. **DECISIVE.** `run_susie_rss.R` has **zero `source()` calls today**
   (`grep -c "source(" → 0`). The extraction would introduce a
   **first-of-its-kind runtime file dependency** on the exact code path the
   ~11-day / $385–1,084 AoU fire exercises — a catastrophic, expensive failure
   mode **that does not exist today**.
2. The duplication is **already** drift-guarded on every suite run by
   `test_qtl_coloc_allele_join.py`'s differential agreement test plus NC-2f /
   NC-2g. **The benefit is style, not safety.**
3. The path mechanism is **wider** than the brief assumed (D-5).
4. The three closed-over helpers are used only inside the closure's own body, so
   removal is technically feasible — this clears an objection but supplies no
   justification.

> **Freeze economy is not sufficient justification to accept fire-path risk.**

Three conditions recorded for any future attempt: a **fail-CLOSED-and-LOUD**
design (a missing/unsourceable shared file must STOP with a named error and must
never degrade to a position-only match — *that degradation IS finding H*); an
`identical()`-on-the-whole-`load_ld_matrix`-result proof at `allele_aware`
**TRUE and FALSE** against the then-current pin; and a re-freeze re-pin.

---

## 8. WHAT IS INERT, AND WHAT WAS NOT PROVEN

* **INERT on today's artifacts.** **0** region JSONs on this node were produced
  from an m3-04c-window tree (0 carry `ld_overlap_zero_fallback`), so nothing on
  disk changes. **No before/after artifact diff was performed.**
* **No R behavioural test exercises Path 2.** It needs the whole script
  (sumstats + regions csv + policy + variant list + a real region). That
  limitation is **pre-existing**, is documented in `test_ld_read_path.py`'s own
  docstring, and **this plan did not close it.**
* `snakemake --dry-run` is not a criterion: `data/processed/ld_reference/` is
  absent, so `resolve_ld_path` raises for every AFR region independently of this
  plan (`D-04b-03`). `--list` is the achievable substitute.
* **0/276 `.npz` banked.** Nothing here asserts anything about a real panel.
* `path2_ld_overlap_zero_NO_NUMERIC_CAUSE` is now **unreachable** from any tree
  at or after `bf04199`. It is retained as a **forensic marker** dating an
  artifact to the m3-04c window; **0** such artifacts exist here.

---

## 9. THE FREEZE

`src/legacy/region_analysis/scripts/run_susie_rss.R` is **re-frozen at
`bf04199`**. **AUTH-K1-UNFREEZE and AUTH-K1-TEST are both SPENT.** The forward
gate is:

```
git diff --exit-code bf04199 -- src/legacy/region_analysis/scripts/run_susie_rss.R
```

---

## 10. ⚠ STALE-FREEZE HANDOFF BLOCK FOR THE ORCHESTRATOR

The K-1 spec (`deferred-items.md:389-391`) requires the gate be replaced
**"everywhere it is asserted"**. **Code-side that is complete in commit
`9538af0`.** These **orchestrator-owned** planning docs still assert `dc4bbd2`
as the live freeze and must be updated to **`bf04199`** (and K-1 marked CLOSED)
**in the docs commit**:

* `.planning/STATE.md:55`
* `.planning/HANDOFF.json:75` and `:111` — both narrate the unfreeze as
  needed / SPENT
* `.planning/HANDOFF.json:117` — the `freeze_state` field
* `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md:25`

**The executor wrote NONE of these, deliberately** (hard rule 10): they are not
in `files_modified`, so touching them would have broken T3 STEP 4's scope-diff
gate. Listed explicitly so the closure is not left half-applied.

**Also not committed by the executor** (orchestrator owns the docs commit):
this SUMMARY and `260806-pd3-PLAN.md`.

---

## 11. COST

**$0.** NC State node only. **Zero perimeter contact** — the forbidden-token
scan (`gsutil|gcloud|bq|dataproc|hailctl|wb`) over the entire `63453db..HEAD`
diff returns **0**. **The AoU fire was NOT triggered** and remains Carter's
terminal gate.

---

## 12. LESSONS

1. **A non-vacuity guard earns its keep by failing.** The `assert diff.strip()`
   line the plan mandated is the only reason D-1 surfaced instead of shipping a
   filter that proved nothing. Green would have been indistinguishable.
2. **`grep -r` and `grep -R` are different measurements when a symlink is in the
   tree.** A 55× census error (35 vs 1,944) rode on one character, and it was
   about to be written into frozen source as a load-bearing factual claim. When
   a number is going into a comment as evidence, measure it twice by two methods
   — cf. `[[feedback_verify_assumption_before_shipping]]`.
3. **A census correction can strengthen the finding it corrects.** The 9 real
   `true` artifacts were genuine Path-1 reverts, which makes the overload's
   collision concrete rather than hypothetical.
4. **A "MUST NOT MOVE" constraint needs to name bytes, not line numbers.** An
   authorized comment reword shifts every line below it. The plan's own
   mechanism — byte-identity of named regions — was the right one; the line
   numbers in its prose were the brittle part (cf.
   `[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]`, same failure family).
5. **A token set in a test must be recovered from the shipped source.** The
   plan's warning that a lowercase-only regex class silently recovers 3 of 5
   tokens — and that the cheapest repair drops exactly the two the property
   exists for — was correct and was designed around.

---

## Self-Check

Files claimed created/modified, verified on disk; commits verified in
`git log`; suite numbers verified from the raw run output quoted above.

**Self-Check: PASSED**
