---
phase: quick/260805-o7o
plan: 01
subsystem: m3-ld-read-path
tags: [R, susieR, ld-panel, alleles, sumstats, aou, fine-mapping, blast-radius, snakemake]
status: complete
requires: [quick/260805-23d]
provides:
  - "allele-aware chr:pos:REF:ALT sumstats<->panel join, AFR-gated, orientation-resolving"
  - "z sign flip for transposed variants; palindromic/mismatch/ambiguous/unusable drops, all counted"
  - "two new structured rejections routing through the existing hard stop()"
  - "panel-visible finemap_summary.tsv (14 appended columns)"
affects:
  - src/legacy/region_analysis/scripts/run_susie_rss.R
  - src/legacy/region_analysis/scripts/summarize_finemap_results.py
  - src/python/ld_read_path.py
  - src/snakemake/rules/finemap.smk
  - src/snakemake/schemas/pipeline.schema.yaml
  - config/pipeline.yaml
tech-stack:
  added: []
  patterns:
    - "two match() calls on 4-keys; multiallelics disambiguated BY CONSTRUCTION, no tie-break"
    - "a fallback that is never CONSTRUCTED cannot be silently taken (inherited from 260805-23d)"
    - "NA (JSON null) vs 0 distinguishes 'not measured' from 'measured clean'"
    - "load source text via compile(), never __pycache__, for column-order guards"
key-files:
  created:
    - tests/m3/test_ld_allele_aware_join.py
    - tests/m3/test_ld_allele_aware_wiring.py
    - tests/m3/test_finemap_summary_panel_visible.py
  modified:
    - src/legacy/region_analysis/scripts/run_susie_rss.R
    - src/legacy/region_analysis/scripts/summarize_finemap_results.py
    - src/python/ld_read_path.py
    - src/snakemake/rules/finemap.smk
    - src/snakemake/schemas/pipeline.schema.yaml
    - config/pipeline.yaml
    - tests/m3/test_ld_read_path_ancestry_gate.py   # AUTH-o7o-01 ONLY
decisions:
  - "Resolve orientation (flip z), do NOT merely exclude swapped variants"
  - "DROP palindromes unconditionally; not configurable"
  - "Reported BETA/SE are NOT flipped -- no published effect direction moves"
  - "allele_aware defaults FALSE; fail-safe is caller-relative CHANGE NOTHING"
metrics:
  tasks: 3
  commits: 3
  full_suite: "641 passed / 31 skipped / 0 failed (672 collected)"
  baseline: "584 passed / 31 skipped / 0 failed (615 collected)"
  cost: "$0 -- NC State only, zero perimeter contact"
  completed: 2026-08-05
---

# Quick 260805-o7o: Close blast-radius findings H and I Summary

**Allele-aware, orientation-resolving, fully-counted sumstats↔panel join gated to the AFR
allow-list, plus a panel-visible `finemap_summary.tsv` — discharging the
`m3-04c-BLAST-RADIUS.md:140` gate row "Trusting any AFR fine-map result."**

---

## Commits

| Task | Commit | What |
|---|---|---|
| 1 | `10c14f2` | allele-aware matcher inside `load_ld_matrix`, gated OFF by default (loader half) |
| 2 | `64f420a` | allow-list gate, argv thread, z flip, allele-keyed catalog join, counted JSON (wiring half) |
| 3 | `dc4bbd2` | panel-visible `finemap_summary.tsv`, full-suite gate, freeze re-pin |

---

## Gate binding, reported against `m3-04c-BLAST-RADIUS.md:133-144`

| Gate | Blocked by | Status after this task |
|---|---|---|
| **Trusting any AFR fine-map result** | BLOCKER-A, **H**, **I** | ✅ **DISCHARGED** — A closed by `260805-23d`; H and I closed here |
| Publishing the panel provenance | **I**, J, K | 🟠 **PARTIAL** — I closed; **J and K remain OPEN** |
| Re-running ANY EUR fit | BLOCKER-B | unchanged (closed by `260805-23d`); re-proven here with `identical()` |
| The ~11-day billed fire | A, C, D | unchanged — **D remains PARTIAL** |
| Any GWAS×QTL colocalization | E | **OPEN, untouched** |
| Any TRANS fit | G, F | **OPEN, untouched** |
| Growing the curated region set | L, M | **OPEN, untouched** |

**Explicitly left OPEN and untouched: E, G, J, K, L, M, and BLOCKER-D's MC4R / FTO / HLA
large-region classes.** m3-06 stays HELD — NaN→0 was not revived and
`condition_ld_matrix.py` was not touched (repo grep empty).

---

## ⚠ THE BEHAVIOUR CHANGE, NAMED PLAINLY — for the manuscript / OSF record

For **AFR** (and only AFR — this is allow-list-gated), variants that previously entered the
fit via a **first-hit position match** now:

1. **may have their z NEGATED**, when the sumstats and panel ALT alleles are transposed; and
2. **may be DROPPED**, when they are palindromic (A/T, C/G), allele-mismatched, ambiguous
   (duplicate 4-key), or allele-less.

**Any AFR figure or table regenerated after this lands is NOT comparable to one produced
before it.** This is intended — it is the correction the phase exists to make — but it is a
disclosable analysis change, not a plumbing detail. State it in the manuscript/OSF record; do
not let a reader discover it by diffing versions.

**Reported `BETA` and `SE` are NOT flipped.** They stay in sumstats effect-allele orientation
in `credible_sets` and every downstream table. The flip is strictly an internal alignment of
`z` to the panel's coding allele. **No published direction of effect moves.** Verified in the
end-to-end fixture: the emitted `credible_sets` carry `BETA = 0.12` / `-0.072` — the raw
sumstats values — with the flag both on and off.

**EUR and TRANS are structurally unreachable.** `ld_allele_aware` renders `"false"` for them
off the same allow-list, and the new formal defaults `FALSE`.

---

## The H remedy, and the palindromic-drop consequence

Two `match()` calls on 4-keys (`chr:pos:REF:ALT` and the REF/ALT transpose), loop-free, with
multiallelics disambiguated **by construction** rather than by a tie-break someone has to
trust. Duplicated panel 4-keys are removed from the match *table* before matching — the
`260805-23d` "a fallback that is never constructed cannot be silently taken" discipline.

| Case | Disposition | Counter |
|---|---|---|
| position hit, (REF,ALT) exact | KEEP, `orient = +1` | `ld_allele_exact` |
| position hit, (REF,ALT) transposed | KEEP, **`orient = -1` → z NEGATED** | `ld_allele_flipped` |
| palindromic (A/T, T/A, C/G, G/C) | **DROP** | `ld_allele_dropped_palindromic` |
| position present, no compatible pair | **DROP** | `ld_allele_dropped_mismatch` |
| >1 panel row shares the 4-key | **DROP** | `ld_allele_dropped_ambiguous` |
| REF/ALT missing / `""` / `"N"` / NA | **DROP** | `ld_allele_dropped_unusable` |
| position absent from panel | ordinary non-overlap | *not counted* |

**Why palindromes are dropped, specific to THIS panel rather than boilerplate:**
`ld_npz_to_rds.R:348-361` (`liftover_one`) lifts GRCh38→GRCh37 carrying `ref`/`alt` through
**verbatim — it does not complement them**. A strand-inverted chain block therefore yields a
panel REF/ALT reverse-complemented relative to GRCh37. For a **non**-palindromic variant that
surfaces as a detectable allele **mismatch**; for a **palindromic** one it surfaces as an
**exact match that is silently sign-wrong** — the one class whose error is invisible from the
allele codes alone. Dropping them removes the sole undetectable failure mode. Expected cost is
the palindromic fraction of overlap (single-digit percent) against `min_ld_coverage = 0.5` at
realized AFR overlap ~10³. **Deliberately not configurable** — a knob here is another silent
lever. **No new fatal threshold was invented**: drops reduce realized overlap and the
*existing* gate (50 / 0.5 / 10) decides fatality, unchanged.

**Two new structured rejections** — `alleles_unavailable_panel`,
`alleles_unavailable_sumstats` — cover the two cases where verification is *impossible*. They
route through the pre-existing `assert_declared_ld_authoritative()`, which stops on
`declared_rejected` regardless of reason and **needed no edit**. Both are proven **inert**
under `authoritative = FALSE`.

---

## AUTH-o7o-01 — the one authorized pre-existing test edit

**Task 2 was STOPPED and surfaced** under hard rule 5 before this authorization existed.
`tests/m3/test_ld_read_path_ancestry_gate.py::test_rendered_argv_delta_vs_3f431ab_is_exactly_four_tokens`
went red:

```
E  AssertionError: the argv delta versus 3f431ab must be exactly
   ['--ld-file', '{input.ld_matrix}', '--ld-authoritative', '{params.ld_authoritative}'],
   got [..., '--ld-allele-aware', '{params.ld_allele_aware}']
E  Left contains 2 more items, first extra item: '--ld-allele-aware'
```

Three plan requirements were structurally unsatisfiable together: STEP 4 *mandated* the shell
token; `<verify>` *required* the module to pass; hard rule 3 *forbade* editing it. Carter
authorized the resolution directly as **AUTH-o7o-01**, in two required parts:

1. **APPEND** the two tokens to `EXPECTED_ADDED_TOKENS` (order preserved; the
   `--ld-file` < `--ld-authoritative` assertion still holds).
2. **STRENGTHEN** — new `test_params_ld_allele_aware_values` asserting the flag renders
   `"false"` for **EUR, TRANS, EAS, HIS** and `"true"` for **AFR**, against *both* a synthetic
   config *and* the REAL shipped `config/pipeline.yaml`, plus every degraded shape (block
   absent / malformed / `enabled: false` / `ancestries: []` / sub-key absent / explicitly
   false), plus lever independence from `--ld-authoritative`.

`EXPECTED_ADDED_TOKENS` is a **proxy**; T1.4's docstring states the real contract ("inert BY
CONSTRUCTION"). Being a closed literal it trips on any extra token whether inert or not. Part
(2) converts the widened proxy back into a **direct** assertion — the list got longer, the
containment got **stricter**. The rationale is recorded in the test file itself.

Measured at HEAD against the shipped config:

```
  AFR    allele_aware=true    authoritative=true
  EUR    allele_aware=false   authoritative=false
  TRANS  allele_aware=false   authoritative=false
  EAS    allele_aware=false   authoritative=false
  HIS    allele_aware=false   authoritative=false
```

**This authorization covered exactly one file and did not reopen hard rule 3 for any other.**
No other pre-existing test was edited.

---

## Track A — EUR invariance

`identical()` on the **ENTIRE** `load_ld_matrix` result object, HEAD source vs
`git show 0378ec8:` source, same EUR fixture, flag rendered `false`:

```
EUR_IDENTICAL=TRUE          (no declared --ld-file)
EUR_DECL_IDENTICAL=TRUE     (with a declared --ld-file present)
```

**INVERTED NEGATIVE CONTROL:** the same comparison on an AFR fixture with
`allele_aware = TRUE` returns **`AFR_IDENTICAL=FALSE`** (`flipped=300`) — proving the
comparison can detect a difference at all.

`ld_status` and `ld_overlap_fraction` were **not** used as evidence. m3-04c proved EUR
numerics move (r[1,2] 0.1→0.9, credible sets 3→10, nonzero PIPs 200→78) while both stay
byte-identical.

---

## Negative controls — every one OBSERVED RED

### Permanent and in-suite (6)

| Test | Asserts the defect |
|---|---|
| `test_negative_control_allele_aware_false_is_byte_identical_to_pre_change` | `identical()` HEAD vs `0378ec8` on the whole object; inverted control with the flag ON must be FALSE |
| `test_negative_control_pre_change_loader_binds_the_first_alt` | `0378ec8` binds `SNP_ID='x1' ALT='G'` — the first hit — instead of the matching `A:C` row |
| `test_schema_entry_is_what_rejects_a_non_boolean_allele_aware` | with the schema entry → `ValidationError`; without it → silently accepted |
| `test_finemap_smk_declares_renders_and_reads_the_flag` | identical predicate against `0378ec8` must fail |
| `test_r_script_declares_parses_and_threads_the_flag` | identical predicate against `0378ec8` must fail |
| `test_negative_control_pre_change_rows_are_byte_identical` | `0378ec8`'s `FIELDNAMES` renders the AoU row and the 1kG row identically — finding I, reproduced |

### Observed by deliberate revert (recorded per hard rule 6b)

**Task 1 — disable the branch (`if (isTRUE(allele_aware))` → `if (FALSE)`):**
```
E AssertionError: identical() returned TRUE even with allele_aware = TRUE ... assert 'TRUE' == 'FALSE'
E AssertionError: the allele-aware matcher bound the A/C sumstats row to a panel row with ALT='G' (SNP_ID='x1') ... assert 'G' == 'C'
E AssertionError: expected the A/T row to be dropped as palindromic, got <NULL> ... assert '<NULL>' == '1'
E AssertionError: <NULL> ... assert '<NULL>' == '60'      (counters absent)
E AssertionError: FALSE ... assert 'FALSE' == 'TRUE'      (no rejection)
E AssertionError: 80 ... assert '80' == '60'              (unusable rows not dropped)
E AssertionError: 75 ... assert '75' == '60'              (mismatched rows bound)
```

**Task 1 — additive fields attached unconditionally (the R NULL-element trap):**
```
E AssertionError: allele_aware = FALSE is NOT byte-identical to the pre-change loader ... assert 'FALSE' == 'TRUE'
```

**Task 1 — orient/keep_idx lockstep broken (`orient[ord]` → `rev(orient)`):**
```
E AssertionError: orient[0] = 1 for subset row 1; the orientation vector is OUT OF STEP with subset_idx ... assert '1' == '-1'
```

**AUTH-o7o-01 part (2) — required by the authorization, both observed:**
```
# shipped ld_read_path.ancestries drifted to [AFR, EUR]
E AssertionError: the SHIPPED config/pipeline.yaml arms the allele-aware join for EUR
  assert 'true' == 'false'

# ld_allele_aware() stubbed to `return "false"`
E AssertionError: assert 'false' == 'true'
```

**Schema entry — with / without:**
```
WITH    allele_aware: "not-a-boolean"  ->  WorkflowError ... ValidationError:
                                           'not-a-boolean' is not of type 'boolean'   rc=1
WITHOUT the same bad value             ->  rc=0, silently accepted
```

**Task 3 — revert `FIELDNAMES` to the pre-change 17:**
```
E ValueError: 'ld_matrix' is not in list
E AssertionError: [] ... Right contains 14 more items, first extra item: 'ld_matrix'
```

**Task 3 — de-sync the `json_error` dict (drop one appended key):**
```
E AssertionError: ['ld_allele_catalog_join'] ... Extra items in the right set: 'ld_allele_catalog_join'
```

**Task 3 — reorder an existing column (`ld_dir` before `sumstats`):**
```
E AssertionError: the first 17 columns are no longer byte-identical to 0378ec8's, in order
E At index 14 diff: 'ld_dir' != 'sumstats'
```

---

## Defects found by the tests themselves (not by review)

**1. R's `list(k = NULL)` creates a NULL element.** Unlike `x$k <- NULL` (which deletes),
`list(allele_orient = NULL)` *adds* a named NULL. The first implementation therefore made the
`allele_aware = FALSE` result structurally different from `0378ec8`'s and `identical()`
returned FALSE. Fixed by attaching the additive fields only when non-NULL. **Caught by my own
permanent negative control, before any commit.**

**2. `use_snp_id` gated on the wrong condition.** It was `!use_allele_key`, so when the flag
was ON but catalog alleles were unusable, the SNP_ID branch ran anyway — finding H reapplied
to the catalog, one line later. Observed:
`AssertionError: snp_id ... assert 'snp_id' == 'skipped_alleles_unusable'`. Now gated on
`!isTRUE(ld_allele_aware)`: under the flag **neither** legacy branch can run.

**3. `estimate_s_rss` is invariant to a GLOBAL sign flip.** `s(z, R) == s(-z, R)` exactly, so
an all-transposed fixture cannot discriminate consumption from non-consumption at all —
measured **6.4741e-09 with the flag ON and OFF**. The fixture was rebuilt backwards from the
truth (LD-consistent `z_pan`, odd panel rows transposed, `BETA = z_pan · orient · SE`). Had
this not been caught, the plan's headline consumption proof would have been vacuous.

**4. A stale `.pyc` produced a FALSE RED — and could produce a FALSE GREEN.** The first
full-suite run reported `1 failed` on my own column-order guard while the source on disk was
correct. Root cause: `SourceFileLoader` validates cached bytecode against the source's
`(mtime_seconds, size)`. The reorder negative control is a **byte-length-identical** two-line
swap, and the restore landed in the same wall-clock second, so both fields still matched:

```
pyc records: source mtime=1785972228 size=8872
actual     : source mtime=1785972228 size=8872   -> considered VALID
```

Python executed the reordered bytecode against the corrected source. **A column-order guard
that can be silenced by a filesystem timestamp is not a guard** — in the mirror case (real
reorder, stale good `.pyc`) it would pass. `_load_module` now `compile()`s source text read at
call time, consulting no cache, and the test additionally cross-checks executed
`FIELDNAMES` against the source text. Re-verified that the hardened loader still catches a
real byte-length-identical reorder.

---

## Finding I — the 5-consumer blast-radius check (run BEFORE the edit)

All five read the summary **by column NAME**. Raw evidence:

| Script | Read | Verdict |
|---|---|---|
| `filter_finemap_summary.py:280-284` | `csv.DictReader`, `base_fields = reader.fieldnames`, `out_fields = base_fields + extras` (`:401`) | **name-based**; appended columns propagate to augmented/tier outputs automatically. `DictWriter` defaults `extrasaction='raise'`; rows carry only header keys + `extra_fields`, so no row can carry an undeclared key |
| `build_a_list_pip_summary.py:47` | `pd.read_csv(sep="\t")` | **name-based** |
| `replication_compare.py:288-302` | `pd.read_csv` | **name-based**. Its `parts[0..2]` at `:62` parses the **anchors string** (`trait_a:trait_b:ancestry`), not the summary — confirmed |
| `cross_ancestry_compare.py:156` | `pd.read_csv` | **name-based**. Its `row[0]` / `chr_idx` block at `:124-135` is over **tabix'd sumstats**, header-driven — confirmed |
| `build_region_trait_qc.py:114` | `pd.read_csv` | **name-based**. Its `row[idx_*]` block at `:69-101` is over **tabix'd sumstats**, header-driven — confirmed |

**None is positional or column-count sensitive over the summary.** Additionally pinned by a
live `filter_finemap_summary.py` round trip in `test_filter_finemap_summary_survives_the_widened_header`.

**14 columns APPENDED, zero reordered.** `ld_dir` deliberately stays where it is (it is the
constant that *constitutes* finding I, but removing it would reorder the header); a comment at
`FIELDNAMES` states plainly that `ld_dir` is a constant and `ld_matrix` is the
actually-resolved panel. First 17 entries pinned byte-for-byte against `0378ec8`;
`summary`/`json_error` dict parity pinned.

---

## Deviations from the plan

### 1. Plan fact WRONG — the schema negative control is unachievable as specified
The plan (Task 2 STEP 3, `<behavior>`, threat `T-o7o-08`) states that without the schema entry
`snakemake --list` dies at `validate()`. **Measured: it does not — rc 0.**
`additionalProperties: false` is set only at the **top level** of
`src/snakemake/schemas/pipeline.schema.yaml:431`; the `ld_read_path` object declares none of
its own, so JSON-Schema's permissive default covers its **sub-keys**. The `260805-23d`
precedent differed — `ld_read_path` was a new *top-level* key. Verified `validate()` **is**
reached and **does** reject a genuinely undeclared top-level key:
```
ValidationError: Additional properties are not allowed
('__o7o_probe_undeclared_top_level_key__' was unexpected)   rc=1
```
The entry is kept (it **types** the key) and an **achievable** control was substituted and
landed permanently. **This is the third assertion in this arc found structurally incapable of
failing** — see Lessons.

### 2. Plan self-contradictory — the A/T multiallelic fixture
Task 1's `<behavior>` asserts both "sumstats `REF=A ALT=T` binds to the panel's `A:T` row" and
"sumstats `REF=A ALT=T` vs panel `A:T` is DROPPED". **A/T is palindromic**, so the two are
mutually unsatisfiable. The palindromic rule was honoured exactly (it is the load-bearing
scientific decision, carried by `T-o7o-03`) and the multiallelic fixture uses a
**non-palindromic** alternate (`A/C`). The plan's literal `A/T` case is separately asserted as
a **drop** in `test_plan_literal_multiallelic_at_row_is_dropped_palindromic`, so both
sentences are covered and neither is quietly discarded.

### 3. AUTH-o7o-01 — one pre-existing test edited under named authorization
See above. Surfaced as a STOP first; executed only after explicit authorization.

### 4. `dropped_unusable` is the sumstats-side class
Following the plan's explicit formulas, a row whose **panel** counterpart has the unusable
alleles is counted under `dropped_mismatch` rather than `dropped_unusable`. Still dropped,
still counted — only the label differs. Recorded in a source comment.

### 5. The third `nrow(R) != length(keep_idx)` return path is unreachable under the flag
The plan asks for a length assertion on three returns. Under `allele_aware` that branch is
only reachable with a variants-less (bare matrix) panel, which is now a **structured
rejection** — so it cannot return a `subset_idx` without an orient at all. Asserted as such in
`test_allele_orient_is_aligned_to_subset_idx_on_every_return` (F3).

---

## Freeze re-pin

> **`src/legacy/region_analysis/scripts/run_susie_rss.R` is RE-FROZEN** as of **`dc4bbd2`**
> (the Task 3 commit).
> The forward gate is
> `git diff --exit-code dc4bbd2 -- src/legacy/region_analysis/scripts/run_susie_rss.R`.
> **The unfreeze granted by Carter on 2026-08-05 is SPENT.**

The only source files touched since `0378ec8` are this plan's `files_modified` plus
`tests/m3/test_ld_read_path_ancestry_gate.py` (AUTH-o7o-01):

```
config/pipeline.yaml
src/legacy/region_analysis/scripts/run_susie_rss.R
src/legacy/region_analysis/scripts/summarize_finemap_results.py
src/python/ld_read_path.py
src/snakemake/rules/finemap.smk
src/snakemake/schemas/pipeline.schema.yaml
tests/m3/test_ld_allele_aware_join.py            (NEW)
tests/m3/test_ld_allele_aware_wiring.py          (NEW)
tests/m3/test_finemap_summary_panel_visible.py   (NEW)
tests/m3/test_ld_read_path_ancestry_gate.py      (AUTH-o7o-01)
```

Frozen contracts **0-diff** vs `0378ec8`: `plink_ld_to_npz.py`, `ld_npz_to_rds.R`,
`condition_ld_matrix.py`. The four m3-07 modules **0-diff**. m3-06 grep empty.

---

## Verification — measured, one run, quoted raw

```
641 passed, 31 skipped, 4 warnings in 746.66s (0:12:26)
```

**Baseline to beat: 584 passed / 31 skipped / 0 failed (615 collected).**
Required: `failed == 0`, `passed >= 584`, `skipped <= 31`. **All met.**

Delta reconciliation — **+57**, per task, against a stated budget of "roughly +30" (a budget,
not a target; the plan's expectation was **not** tuned to the outcome):

| Task | Module | Tests |
|---|---|---|
| 1 | `test_ld_allele_aware_join.py` (NEW) | +20 |
| 2 | `test_ld_allele_aware_wiring.py` (NEW) | +29 |
| 2 | `test_ld_read_path_ancestry_gate.py::test_params_ld_allele_aware_values` (AUTH-o7o-01) | +1 |
| 3 | `test_finemap_summary_panel_visible.py` (NEW) | +7 |
| | **total** | **+57** |

`584 + 57 = 641` ✓.

**No new test landed as a skip.** `-rs` shows 31 skips, identical to baseline; zero originate
from the three new modules (all are pre-existing `hail not installed` / AoU-perimeter gates).

Other gates, all green:

- `snakemake --snakefile Snakefile --list` → rc 0 on `config/pipeline.yaml` **and** on
  `pipeline_lsweep_L15/L20/L30_overlay.yaml`.
- `grep -c -- '--ld-allele-aware {params.ld_allele_aware}' finemap.smk` == **1**.
- `params.region_id` **byte-unchanged** — 0 hits for `region_id=lambda` in the `finemap.smk`
  diff vs `0378ec8`, and pinned by `test_region_id_param_is_byte_unchanged`.
- `tests/m3/sparse_parent_benchmark.tsv` restored, **not committed**.
- **$0. NC State only. No `gsutil` / `gcloud` / `bq` / `wb` / cluster command anywhere in the
  session. The ~11-day AoU fire was NOT triggered.**

### The full-script consumption proof (a number the fit was computed from)

Mixed-orientation fixture, 150 of 300 panel rows transposed, **identical panel and identical
overlap on both sides**:

| | `--ld-allele-aware false` | `--ld-allele-aware true` |
|---|---|---|
| `d3b_ld_z_consistency_s` | **1** (maximum mismatch) | **6.4741e-09** |
| `ld_source_mismatch_flag` | **True** | **False** |
| credible sets | 2 | 1 |
| `pip_nonzero` | 3 | 300 |
| `ld_allele_flipped` / `ld_allele_exact` | `null` / `null` | 150 / 150 |
| `lambda_gc`, `max_abs_z` | 0, 6 | 0, 6 (sign-invariant, as required) |
| reported `BETA` | 0.12 / −0.072 | 0.12 / −0.072 (unflipped) |

---

## Lessons

1. **A green assertion needs a negative control — and this arc has now found FIVE assertions
   incapable of failing.** The prior four, plus the schema control in this plan's own text.
   Two of this task's four self-caught defects were found *only* because the control was run.
2. **`list(k = NULL)` ≠ absent, in R.** Any "additive fields" change to a returned list must
   attach conditionally or it silently changes the object's structure.
3. **A symmetry in the metric can make a proof vacuous.** `estimate_s_rss` is invariant to a
   global sign flip; the obvious all-transposed fixture proved nothing. Check whether the
   discriminator can *see* the change before trusting it.
4. **Bytecode caching can silence a source-level guard.** `(mtime_seconds, size)` validation is
   defeated by a byte-length-identical edit restored within the same second. Any test whose
   subject is the *text* of a module should read the text.
5. **A closed literal list is a proxy, not a contract.** `EXPECTED_ADDED_TOKENS` trips on any
   new token whether or not it violates the property the docstring names. When widening a
   proxy, pay for it by asserting the real property directly.

---

## Planning artifacts

`.planning/STATE.md` and `.planning/HANDOFF.json` are **Carter's** for this session (standing
directive recorded in `260805-23d-SUMMARY.md` deviation 5) and were **not written**. This
SUMMARY is the sole planning artifact. `ROADMAP.md` untouched — quick tasks are separate from
planned phases.
