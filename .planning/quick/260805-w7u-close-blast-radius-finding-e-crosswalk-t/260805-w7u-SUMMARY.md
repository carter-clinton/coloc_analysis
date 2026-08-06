---
phase: quick/260805-w7u
plan: 01
subsystem: m3-ld-read-path
tags: [R, coloc, susieR, ld-panel, alleles, qtl, aou, snakemake, blast-radius]
status: complete
requires: [quick/260805-23d, quick/260805-o7o]
provides:
  - "resolver-routed coloc LD path -- one crosswalk object shared with run_finemap"
  - "non-path manifest sentinel RESOLVED_BY_LD_PANEL_RESOLVER for gated ancestries"
  - "src/snakemake/scripts/ld_allele_join.R -- shared, source()-able allele-aware 4-key join"
  - "catalog-bridged panel<->fit keying for BOTH live sumstats conventions (rsID and chr:pos)"
  - "non-zero structured exit where LD verification is impossible (was four stacked exit-0 layers)"
  - "bounded sparse->dense coercion on the SUBSET only"
  - "per-pair LD provenance + six disposition counters in the JSON and a log receipt"
affects:
  - config/pipeline.yaml
  - src/python/build_qtl_coloc_manifest.py
  - src/python/ld_read_path.py
  - src/snakemake/rules/qtl_coloc.smk
  - src/snakemake/schemas/pipeline.schema.yaml
  - src/snakemake/scripts/ld_allele_join.R
  - src/snakemake/scripts/run_qtl_coloc.R
tech-stack:
  added: []
  patterns:
    - "ONE gate for both halves of a remedy -- two levers would permit 'resolution ON / join OFF'"
    - "differential agreement against a BODY-WALK EXTRACTION of the frozen source, never a hand-copy"
    - "a sentinel that is deliberately NOT path-shaped cannot be silently opened"
    - "a token that is UNCONSTRUCTIBLE beats a token that is quoted"
    - "an absence claim about CODE must be evaluated against comment-stripped code"
    - "NA (JSON null) vs 0 distinguishes 'not measured' from 'measured clean'"
key-files:
  created:
    - src/snakemake/scripts/ld_allele_join.R
    - tests/m3/test_qtl_coloc_ld_resolution.py
    - tests/m3/test_qtl_coloc_allele_join.py
  modified:
    - config/pipeline.yaml
    - src/python/build_qtl_coloc_manifest.py
    - src/python/ld_read_path.py
    - src/snakemake/rules/qtl_coloc.smk
    - src/snakemake/schemas/pipeline.schema.yaml
    - src/snakemake/scripts/run_qtl_coloc.R
    - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
decisions:
  - "ONE gate (ld_coloc_applies) governs BOTH the resolver route and the allele join"
  - "Duplicate the matcher rather than edit the FROZEN run_susie_rss.R -- and pay for it with a differential agreement test extracted from the real frozen source"
  - "Under the gate an unverifiable LD bridge EXITS NON-ZERO; ungated it stays exit-0 byte-identical"
  - "orient is MEASURED and REPORTED but NOT APPLIED -- E-2 stays deferred, its magnitude now measurable"
  - "Gate the matrix-class fix too: an ungated fix would move EUR from failure to a result"
metrics:
  tasks: 3
  commits: 3
  full_suite_m3: "745 passed / 31 skipped / 0 failed (776 collected)"
  baseline_m3: "641 passed / 31 skipped / 0 failed (672 collected)"
  full_suite_phase2: "136 passed / 1 skipped / 0 failed (137 collected)"
  baseline_phase2: "136 passed / 1 skipped / 0 failed (137 collected)"
  cost: "$0 -- NC State only, zero perimeter contact"
  completed: 2026-08-06
---

# Quick 260805-w7u: Close blast-radius finding E Summary

**One resolver-routed coloc LD path, one shared allele-aware matcher held to the FROZEN
implementation by a differential test extracted from the real source, a non-zero exit
where verification is impossible, per-pair panel provenance, and a byte-identical
EUR/Track-A path proven with an inverted control — discharging the
`m3-04c-BLAST-RADIUS.md:141` gate row "Any GWAS×QTL colocalization".**

---

## Commits

| Task | Commit | What |
|---|---|---|
| 1 | `2563451` | resolver-routed `_qtl_coloc_ld_input`; the single gate; the non-path manifest sentinel |
| 2 | `1815bfd` | `ld_allele_join.R`; catalog bridge; loud non-zero exits; bounded coercion; provenance |
| 3 | *(this task)* | full-suite gate; E-2/E-3/E-4 registered in `deferred-items.md` |

---

## 1. Gate binding, reported against `m3-04c-BLAST-RADIUS.md:133-144`

| Gate | Blocked by | Status after this task |
|---|---|---|
| **Any GWAS×QTL colocalization** | **E** | ✅ **DISCHARGED** — for an allow-listed ancestry the LD reaching `coloc::runsusie` is the artifact `resolve_ld_path` selects, via the same crosswalk object `run_finemap` uses |
| Trusting any AFR fine-map result | A, H, I | unchanged — DISCHARGED by `260805-23d` + `260805-o7o`. **H and I NOT re-opened** |
| Re-running ANY EUR fit | BLOCKER-B | unchanged — re-proven here on the coloc path with whole-file byte identity + an inverted control |
| The ~11-day billed fire | A, C, **D** | unchanged — **D remains PARTIAL**; MC4R / FTO / HLA large-region classes **OPEN and untouched** |
| Publishing the panel provenance | I, **J**, **K** | unchanged — **J and K remain OPEN** |
| Any TRANS fit | **G**, **F** | **OPEN, untouched** |
| Growing the curated region set | **L**, **M** | **OPEN, untouched** |

**Explicitly left OPEN and untouched: F, G, J, K, L, M, and BLOCKER-D's MC4R / FTO / HLA
large-region classes.** m3-06 stays **HELD** — NaN→0 was not revived and
`condition_ld_matrix.py` was not touched (`git diff 7b1025d HEAD -- src config tests |
grep -inE 'condition_ld_matrix|nan_to_num'` → empty).

**The coloc-side analogue of finding I is deliberately NOT closed.**
`aggregate_qtl_coloc.py::METADATA_COLS` is a closed list; the new provenance lands in the
per-pair JSON and a per-pair log receipt but NOT in `qtl_coloc_summary.tsv`.
`aggregate_qtl_coloc.py` was out of scope and is **0-diff**.

---

## 2. ⚠ THE BEHAVIOUR CHANGE, NAMED PLAINLY — for the manuscript / OSF record

For **AFR only** (this is allow-list-gated; EUR / TRANS / EAS / HIS are structurally
unreachable), once an `AFR_aou/<m2_id>.rds` exists on disk:

1. **The coloc LD panel switches from 1kG AFR (n=661) to the AoU AFR panel.** PP.H4,
   credible-set membership, and which variants enter at all will move for that pair.
2. **Variants that previously entered on a first-hit position match may now be DROPPED** —
   palindromic (A/T, C/G), allele-mismatched, ambiguous (duplicate panel 4-key), or
   allele-less. Measured on the acceptance fixture: 8 palindromic + 5 mismatch +
   1 ambiguous + 4 unusable dropped out of 200.
3. **Jobs that previously wrote `too_few_snps` at rc 0 now FAIL THE DAG.** A region whose
   panel cannot be bridged stops being a quiet row in the summary and becomes a job you
   have to look at.

**Any AFR coloc figure or table regenerated after this lands is NOT comparable to one
produced before it.** This is intended — the n=661 1000G AFR reference IS the
miscalibration M3 exists to correct — but it is a **disclosable analysis change**, not a
plumbing detail. State it in the manuscript / OSF record; do not let a reader discover it
by diffing versions.

**No effect direction is flipped.** `orient` is measured and reported but deliberately NOT
applied on the coloc path (see §5, E-2).

**Nothing moves today.** No `AFR_aou/*.rds` exists on this node (0/276 `.npz` banked;
`data/processed/ld_reference/` is absent entirely), and — separately — no manifest row is
AFR at all (see Deviation 1). The wiring goes live after the fire.

---

## 3. The two brief corrections, with evidence

### F2 — `build_ld_rownames` is NOT on the AoU path; fixing it would have been a NO-OP

The brief located the defect at the `SNP_ID` branch of `build_ld_rownames`
(`run_qtl_coloc.R:206-219`). **That function never runs for the AoU panel.**
`ld_npz_to_rds.R:440` writes `R` as a `dsCMatrix` **WITH** dimnames (the GRCh37
`chr:pos:ref:alt` ids), and `:232` is
`rownames(ld_full) %||% colnames(ld_full) %||% build_ld_rownames(ld_obj)` — `%||%` (`:24`)
short-circuits on the first non-NULL, so `ld_snp_names` comes from `rownames(ld_full)`.

The **outcome** the brief describes is right (panel-space keys, zero overlap); the **site**
is not. The legacy 1kG `.rds` is the opposite shape — `plink_ld_to_rds.R:88` sets
`dimnames(R) <- NULL` **and** its `R` is a base matrix from `as.matrix(ld_dt)` (`:72`) —
which is why EUR coloc works today, and which is also the measured reason the matrix-class
fix had to be gated (§6).

**The fix landed at the resolution of `ld_snp_names`, not at `build_ld_rownames`.**
Reproduced permanently in-suite by `test_the_bridge_is_not_reachable_without_the_gate`:

```
status = too_few_snps    message = "Only 0 SNPs after LD intersection (need >= 50)"
n_snps_overlap = 0       rc = 0
```

### F3 — the empty overlap is not a silent identity; it is FOUR stacked exit-0 layers

All four traced and, where behavioural, reproduced:

1. `intersect(overlap_snps, ld_snp_names)` = 0 → `write_status_json("too_few_snps", …)` →
   **`quit(status = 0)`**. Reproduced above.
2. **MEASURED, not argued** — even with keys fixed, `ld_full` is a `dsCMatrix`, the subset
   is sparse, and `coloc::runsusie` rejects it. Observed in
   `test_coloc_receives_a_base_matrix_even_from_a_dscmatrix_panel`:
   ```
   panel class: dsCMatrix
   sparse subset is.matrix: FALSE
   check_dataset: CHECK_PASSED          <- coloc::check_dataset(req="LD") does NOT catch it
   runsusie: RUNSUSIE_ERR:LD must be of class matrix
   ```
   `runsusie` is wrapped in `tryCatch` → `NULL` → `write_status_json("qtl_susie_failed")` →
   **exit 0**. Re-observed under NC-2d.
3. `use_identity` builds `diag(length(overlap_snps))` over the *fit* keys, never intersects
   the panel, and runs `coloc.susie` on it with only a `cat()`; the emitted JSON records
   **nothing** about which LD was used.
4. Snakemake sees rc 0 for all of the above.

**Under the gate, layer 1 / 2 / 3 are each replaced by a named non-zero exit; layer 4
follows.** Raw, on the unbridgeable fixture:

```
Error: [run_qtl_coloc] LD_JOIN_FATAL reason=panel_bridge_below_threshold
  region=SH2B3_12q24 ancestry=AFR ld_matrix=.../fx_bad/ld.rds
  realized_overlap=0 threshold=50
  candidate_overlaps=[panel_rownames=0, panel_chrpos=0, panel_chrpos_ref_alt=0,
                      catalog_snp_id=0, catalog_chrpos=0]
  key_space=catalog_snp_id; the bridged panel<->fit overlap is below the floor
Execution halted
rc = 1 | output JSON written = False
```

**No new fatal threshold was invented.** `MIN_COLOC_LD_OVERLAP <- 50L` is the same literal
the two pre-existing gates use, and `test_the_overlap_floor_agrees_with_the_shipped_policy`
pins it against `config/susie_policy.yaml min_ld_overlap`. Only the LOUDNESS changed.

---

## 4. The reuse decision, verbatim from the plan's `<the_reuse_decision>`

> **DECIDED: do NOT edit the frozen file; land the matcher in a NEW shared source
> `src/snakemake/scripts/ld_allele_join.R`, `source()`d by `run_qtl_coloc.R` only, and hold
> it to the shipped implementation with a DIFFERENTIAL AGREEMENT TEST that drives both on
> the same fixtures. Extraction of `run_susie_rss.R` onto the same file is the correct END
> STATE and is recorded as a named follow-up, not attempted here.**
>
> **Why extraction is right and still not done now.** The shipped
> `match_indices_allele_aware` contract (`subset_dt`/`variants_dt`, both with
> `CHR/POS/REF/ALT`) **is** satisfiable on the coloc path once the catalog is the
> `subset_dt` side. So this is genuinely the same join. The obstacle is not aesthetic: the
> matcher lives INSIDE `src/legacy/region_analysis/scripts/run_susie_rss.R`, **RE-FROZEN at
> `dc4bbd2`**, and the unfreeze granted 2026-08-05 is **SPENT**. A pure-move extraction is
> still a frozen-file edit and would need its own `identical()`-on-the-whole-object
> 0-behaviour proof across every `allele_aware` state — that is a reviewed task of its own,
> not a rider on this one.
>
> **Why the duplication is acceptable HERE and would not be otherwise.** A second
> independent allele-key implementation is precisely how finding H came to exist in two
> places. The difference is that agreement is **machine-checked on every suite run**, not
> documented.

### THE NAMED FOLLOW-UP, to be executed later — NOT executed here

> `run_susie_rss.R:220-323` should be replaced by
> `source("src/snakemake/scripts/ld_allele_join.R")` the next time the freeze is opened for
> an independent reason. Requires: a named unfreeze authorization; an
> `identical()`-on-the-whole-`load_ld_matrix`-result proof at `allele_aware` TRUE **and**
> FALSE against `dc4bbd2`; and a RE-FREEZE re-pin at the new SHA, after which
> `git diff --exit-code <new-sha> -- run_susie_rss.R` becomes the forward gate.

`ld_allele_join.R` is deliberately shaped as a drop-in `source()` target so that change is
a delete-and-source, not a rewrite. Its header states (a) that it is a deliberate second
implementation, (b) the frozen-file reason, (c) that agreement is enforced by test and not
by discipline, and (d) this follow-up.

### The agreement mechanism, and how it was proven not to be self-referential

**STEP 0 was executed FIRST and verified working before a single line of
`ld_allele_join.R` was written.** Measured against the sourced loader prefix:

```
exists load_ld_matrix: TRUE
exists match_indices_allele_aware (top level): FALSE
```

and after the body-walk extraction, on the canonical multiallelic fixture (panel
`12:100 A/G`, `12:100 A/C`, `12:200 C/T`; subset `12:100 A/C`, `12:200 T/C`):

```
class: function
nformals: 2
formals: subset_dt,variants_dt
keep: 1 2
ld: 2 3          <- binds the SECOND panel row, not the first hit
orient: 1 -1
exact: 1 flipped: 1
dropped: 0 0 0 0
```

Every value matches the plan's independently re-derived prediction exactly.

The three nested helpers (`.up`, `.usable`, `.allele_counts0`) are extracted into the child
environment first, and **the list is verified rather than asserted**: each is dropped in
turn and the resulting callable must break on at least one fixture
(`test_every_nested_helper_the_matcher_closes_over_is_extracted`, 3 parametrised cases).
The two implementations are sourced into **separate environments** whose parent is
`globalenv()`, so a missing extraction ERRORS instead of silently borrowing the new code
and agreeing with itself.

**11 shared fixtures** span every disposition class — multiallelic, palindromic, mismatch,
ambiguous, unusable, absent-position, both structured rejections, all-unusable panel,
NA-coordinate, and a 120-row production-scale mixture in which **all six counters are
non-zero simultaneously**. `keep`, `ld`, `orient` and all six counters agree.

---

## 5. `<explicitly_deferred>` reproduced IN FULL

Registered in `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` (committed
with the Task 3 code commit) so it is discoverable from the phase, not only from this file.

### E-2 — the QTL-beta ↔ panel-ALT orientation

`qtl_data$LD` is signed on the panel's ALT (plink `--keep-allele-order`, hardcoded at
`aou_ld_panel.py:2905`); `qtl_data$beta` is signed on the QTL's effect allele. A transposed
variant mis-signs the QTL SuSiE fit — finding H's family, on the QTL side.

**Deferred because:** it is **pre-existing on the legacy 1kG/EUR path** and unaddressed
there today; it is **not named by finding E**; correcting it would **move Track-A EUR
numbers** (today's coloc successes are **32/32 EUR**, 1,957 legacy coloc JSONs exist, Track
A is **in submission**); and it needs a **GRCh38↔GRCh37 allele reconciliation** that is its
own task — the QTL side is GRCh38 (`variant_id = chr12_110962202_G_A`) while the panel and
catalog are GRCh37, so no position join is available on the QTL side at all.

**What this task did do — the part that makes it actionable.** The panel↔catalog join emits
`ld_allele_flipped` (and its five siblings) into **every per-pair JSON and a per-pair log
receipt**. `ld_allele_flipped` is the count of rows transposed between catalog and panel at
the same position — i.e. **the population in which an orientation error can occur at all**.
E-2's magnitude is therefore now **MEASURABLE per region** rather than invisible: read
`ld_allele_flipped / (ld_allele_exact + ld_allele_flipped)` off the receipts and decide on
evidence instead of argument. On the acceptance fixture that ratio is `46 / 182 = 25.3%`.

This task also closed the **row-binding half**, which is independent of sign: a multiallelic
site binding to an arbitrary ALT's LD **ROW** is a wrong-row error whether or not the sign
is right.

The registry entry carries the neutral A/B options table and states plainly that B is
correct but is a Track-A-moving change needing its own containment proof — **Carter's call,
not an executor's**.

### The coloc-side analogue of finding I

`aggregate_qtl_coloc.py::METADATA_COLS` is a closed list; the new provenance fields land in
the per-pair JSON and a per-pair log receipt (`finemap.smk:441`'s pattern) but **NOT** in
`qtl_coloc_summary.tsv`. `aggregate_qtl_coloc.py` was out of scope and is **0-diff**.

### Findings G, J, K, L, M and BLOCKER-D's MC4R/FTO/HLA classes

**OPEN, untouched** — proven by `git diff --name-only 7b1025d HEAD -- src config tests`
(§7), not by claim. **H and I: closed and verified 7/7 — NOT re-opened.** m3-06 stays HELD.

### Also newly registered (discovered, not fixed)

* **E-3** — two stale schema comments assert the measured-FALSE claim that without their
  entry every Snakemake invocation dies at `validate()`. Pre-existing; the NEW `coloc`
  entry's comment states the correction and points at the registry entry.
* **E-4** — `_ancestry_for_region` is hardcoded to `"EUR"`, so the manifest sentinel branch
  is inert today. See Deviation 1.

---

## 6. Negative controls — all ELEVEN OBSERVED RED, raw

### NC-1a — revert STEP 4's ON branch to `7b1025d`'s body

Byte length changed `26138 → 25649` (the `.pyc` staleness guard is moot for a `.smk`, but
see the dedicated proof below). **4 tests RED:**

```
E  AssertionError: assert 'data/process...2B3_12q24.rds' == '/gpfs_common...40__sub14.rds'
   - .../ld_reference/AFR_aou/m2_region_00040__sub14.rds
   + data/processed/ld_reference/AFR/SH2B3_12q24.rds
E  AssertionError: assert 'data/process...2B3_12q24.rds' == '/gpfs_common...40__sub14.rds'   (disagrees with finemap.smk's lambda)
E  Failed: DID NOT RAISE <class 'FileNotFoundError'>
E  AssertionError: assert '/gpfs_common...ti0/decoy.rds' == '/gpfs_common...40__sub14.rds'   (the competing manifest path won)
```

**The `.pyc` trap, proven guarded rather than assumed.** `ld_read_path.py` and
`build_qtl_coloc_manifest.py` ARE loaded as modules. `_load_module_from_text` `compile()`s
source read at call time, consulting no cache. Verified by forcing BOTH `.pyc` validation
fields identical across a byte-length-identical perturbation:

```
pyc-defeat setup: size 11745 -> 11745, mtime 1785990145 -> 1785990145
                  (both fields IDENTICAL -> a cached .pyc would be considered VALID)
E  AssertionError: assert False is True   <- the test still SAW the perturbation
```

### NC-1b — EUR on the allow-list, and a stubbed always-True gate

```
  SHIPPED            -> GREEN (EUR is False)
  SYNTHETIC(+EUR)    -> E  AssertionError: the SYNTHETIC(+EUR) config arms the coloc read path for EUR
```

Then `ld_coloc_applies` stubbed to `return True` (byte length 11721 → 11648):

```
E  AssertionError: block absent          assert True is False
E  AssertionError: block not a dict      assert True is False
E  AssertionError: block is a list       assert True is False
E  AssertionError: block empty           assert True is False
E  AssertionError: enabled: false        assert True is False
E  AssertionError: EUR                   assert 'true' == 'false'
E  FileNotFoundError: No LD panel found for SH2B3_12q24 EUR     <- the OFF branch no longer runs
E  KeyError: 'TRANS'  /  KeyError: 'EAS'                        <- ditto
```

### NC-1c — the schema entry, both directions (F7's ACHIEVABLE control)

```
WITH the entry,  coloc: "not-a-boolean":
  WorkflowError in file .../Snakefile, line 18:
  Error validating config file.
  ValidationError: 'not-a-boolean' is not of type 'boolean'
  Failed validating 'type' in schema['properties']['ld_read_path']['properties']['coloc']
  rc=1

WITHOUT the entry, the SAME bad value:
  rc=0, silently accepted   (0 occurrences of ValidationError)
```

As F7 requires, **no control was written that depends on the false claim** that removing
the entry breaks `--list`. Re-measured here: it does not.

### NC-1d — drop the `resolver_ancestries` branch

Byte length 19261 → 19027.

```
E  AssertionError: assert 'data/process...2B3_12q24.rds' == 'RESOLVED_BY_...ANEL_RESOLVER'
   - RESOLVED_BY_LD_PANEL_RESOLVER
   + data/processed/ld_reference/EUR/SH2B3_12q24.rds
```

The converse half ("default changes nothing") is **permanent and in-suite**:
`test_builder_default_is_byte_identical_to_7b1025d` (rows, three ways) and
`test_builder_emitted_tsv_is_byte_identical_to_7b1025d` (whole-file bytes via `main()`,
argv-for-argv, with a non-vacuity guard that the file is more than a header).

### NC-2a — disable the join branch (legacy position-only first-hit match)

```
E  AssertionError: multiallelic: ld            assert [1, 3] == [2, 3]
E  AssertionError: palindromic: keep           assert [1, 2, 3, 4] == []
E  AssertionError: mismatch: keep              assert [1, 2, 3] == [2, 3]
E  AssertionError: ambiguous: keep             assert [1, 2] == [2]
E  AssertionError: unusable: keep              assert [1, 2, 3, 4] == [4]
E  AssertionError: na_coordinate: keep         assert [1, 2, 3] == [1]
E  AssertionError: mixed_production_scale: keep  assert [1,2,3,4,5,6,...] == [1,2,4,6,8,10,...]
E  AssertionError: bound the FIRST panel row at the position, not the match
```

### NC-2b — break the `order(keep_idx)` lockstep (`orient[ord]` → `rev(orient)`)

```
E  AssertionError: multiallelic: orient            assert [-1, 1] == [1, -1]
E  AssertionError: mixed_production_scale: orient  assert [1, 1, -1, 1, 1, 1, ...] == [1, -1, 1, -1, 1, -1, ...]
```

### NC-2c — revert the loud failures to `write_status_json` + `quit(0)`

```
E  AssertionError: exited 0:
     [run_qtl_coloc] LD candidate key-space overlaps: panel_rownames=0, panel_chrpos=0,
                     panel_chrpos_ref_alt=0, catalog_snp_id=0, catalog_chrpos=0
     [run_qtl_coloc] too_few_snps for ENSG00000111252/Whole_Blood/SH2B3_12q24 -- wrote .../unbridgeable.json
   assert 0 != 0
E  ... same for cat_absent.json / cat_missing.json / cat_unreadable.json
E  ... [NC-2c] use_identity under the gate -- soft path
     [run_qtl_coloc] LD .rds has use_identity=TRUE (status=too_many_variants); using identity matrix
```

An output JSON was present on every path where none was allowed.

### NC-2d — the bounded coercion, BOTH halves

**(i) Remove it entirely, so the sparse subset reaches `coloc`** — the MEASURED F3 defect:

```
E  AssertionError: {'all_pairs': [], 'ancestry': 'AFR', ...}
   assert 'qtl_susie_failed' == 'success'
   - success
   + qtl_susie_failed
```

The underlying error is observed directly and permanently in
`test_coloc_receives_a_base_matrix_even_from_a_dscmatrix_panel`:
`runsusie: RUNSUSIE_ERR:LD must be of class matrix`, next to
`check_dataset: CHECK_PASSED`.

*(An intermediate variant of this control tripped one line earlier, on
`storage.mode(ld_matrix_subset) <- "double"` → `no method for coercing this S4 class to a
vector`. The control was re-run faithfully, removing that line too, so the error observed
is the one F3 predicts.)*

**(ii) Replace subset-then-coerce with `as.matrix(ld_full)[idx, idx]`** — the BLOCKER-D
shape:

```
E  assert 'as.matrix(ld_full)' not in '...'
   'as.matrix(ld_full)' is contained here:
     subset <- as.matrix(ld_full)[idx, idx, drop = FALSE]
```

### NC-2e — attach the additive JSON fields UNCONDITIONALLY (R's `list(k = NULL)` trap)

```
E  assert b'{\n  "statu...e": null\n}\n' == b'{\n  "statu..._qtl": 1\n}\n'
   At index 781 diff: b',' != b'\n'                      (EUR, flags absent)
E  assert b'{\n  "statu...e": null\n}\n' == b'{\n  "statu..._qtl": 1\n}\n'
   At index 781 diff: b',' != b'\n'                      (EUR, flags rendered "false")
E  AssertionError: an additive field leaked onto the legacy caller
   assert 'ld_allele_join' not in {...'ld_allele_dropped_ambiguous': None, ...}
```

**The INVERTED half is permanent and in-suite** — see §8.

### NC-2f — perturb `ld_allele_join.R` ONLY (drop the palindromic mask)

The shipped matcher untouched; agreement alone goes RED:

```
E  AssertionError: palindromic: keep              assert [1, 2, 3, 4] == []
E  AssertionError: mixed_production_scale: keep   assert [1,2,3,4,5,6,...] == [1,2,4,6,8,10,...]
                                                  At index 2 diff: 3 != 4
E  assert [1, 2, 3, 4] == []
FREEZE_OK                                          <- run_susie_rss.R untouched throughout
```

### NC-2g — THE EXTRACTOR ITSELF, and it is PERMANENT AND IN-SUITE

Rather than a one-off revert, NC-2g is landed as four always-running tests. Each alters an
**in-memory / temp copy** of `run_susie_rss.R`, requires the differential agreement to
BREAK against the altered source while staying GREEN against the real file, **and asserts
`git diff --exit-code dc4bbd2 -- run_susie_rss.R` is clean MID-CONTROL**:

| Test | Alteration | Result |
|---|---|---|
| `test_nc2g_extractor_tracks_the_shipped_source[palindromic_set_narrowed]` | `c("AT","TA","CG","GC")` → `c("AT")` | disagreement observed |
| `…[orient_forced_to_one]` | `orient_all <- rep(1, …)` | disagreement observed |
| `…[ambiguity_guard_removed]` | `k4_pan[dup4 & FALSE] <- NA` | disagreement observed |
| `test_nc2g_deleting_the_assignment_raises_the_named_stop` | rename the assignment | `MSG: STOP-and-surface: could not extract match_indices_allele_aware` |

Each also asserts its anchor string occurs **exactly once** in the frozen source, so the
control cannot silently alter nothing. A plain "it is callable" check would have passed on
a hand-copy; these cannot.

---

## 7. Verification — measured, one run each, quoted raw

### `tests/m3`

```
745 passed, 31 skipped, 4 warnings in 814.55s (0:13:34)
```

**Baseline: 641 passed / 31 skipped / 0 failed (672 collected).**
Required: `failed == 0`, `passed >= 641`, `skipped <= 31`. **All met.**

Delta reconciliation, **+104**, arithmetic:

| Task | Module | Tests |
|---|---|---|
| 1 | `tests/m3/test_qtl_coloc_ld_resolution.py` (NEW) | +45 |
| 2 | `tests/m3/test_qtl_coloc_allele_join.py` (NEW) | +59 |
| | **total** | **+104** |

`641 + 104 = 745` ✓ (collected `672 + 104 = 776` ✓).

**No new test landed as a SKIP.** `-rs` shows **31** skips, identical to baseline, and
**zero** originate from the two new modules — every one is a pre-existing
`could not import 'hail'` (19), `chain file not present` (8), `M2 union BED not present`
(1), `hail not installed` (1), the `test_aou_ld_panel_local.py:2442` SKELETON, or the
`test_occlusion_span_filter.py:504` AoU-perimeter gate. Both new modules run under the
no-skip rule (`_require_m3_r_toolchain()` ERRORS rather than skipping).

### `tests/phase2`

```
136 passed, 1 skipped in 1.81s
SKIPPED [1] tests/phase2/test_negative_controls.py:138: bedtools not available in test environment
```

**Baseline: 136 passed / 1 skipped / 0 failed (137 collected).** Unchanged in every
number; the one skip is the same `bedtools` skip. `tests/phase2/test_run_qtl_coloc.py`
(24 tests) pins `run_qtl_coloc.R`'s CLI surface and **stayed 24 passed** — the new options
are purely additive with legacy defaults.

**No pre-existing test file was edited.** `AUTH-o7o-01` was NOT inherited and no
authorization was needed: nothing pre-existing went red at any point.

### Workflow gates

```
OK config/pipeline.yaml
OK config/pipeline_lsweep_L15_overlay.yaml
OK config/pipeline_lsweep_L20_overlay.yaml
OK config/pipeline_lsweep_L30_overlay.yaml
```

⚠ **`--dry-run` was NOT used as an acceptance criterion**, deliberately. The AoU panel does
not exist and `data/processed/ld_reference/` is absent, so any dry-run criterion touching
the resolved AFR path is unsatisfiable — a prior plan in this arc shipped exactly that.
`--list` is the achievable substitute and **does not evaluate input functions**, so it
cannot observe the resolver either way. Stated as a limit, not sold as coverage.

### Scope + freeze, by diff

```
$ git diff --name-only 7b1025d HEAD -- src config tests | sort
config/pipeline.yaml
src/python/build_qtl_coloc_manifest.py
src/python/ld_read_path.py
src/snakemake/rules/qtl_coloc.smk
src/snakemake/schemas/pipeline.schema.yaml
src/snakemake/scripts/ld_allele_join.R
src/snakemake/scripts/run_qtl_coloc.R
tests/m3/test_qtl_coloc_allele_join.py
tests/m3/test_qtl_coloc_ld_resolution.py
```

**Exactly the plan's nine `files_modified`. No pre-existing test file. Nothing else.**

```
FREEZE_RUN_SUSIE_OK            git diff --exit-code dc4bbd2 -- run_susie_rss.R
FROZEN_CONTRACTS_OK            plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py
OUT_OF_SCOPE_OK                finemap.smk, aggregate_qtl_coloc.py, ld_panel.py
M3_07_OCCLUSION_MODULES_OK     occlusion_catalog.py, occlusion_lockstep_cli.py,
                               drop_occluded_from_sumstats.py, occlusion_span_filter.py,
                               m3_occlusion_lockstep.smk
finemap.smk diff | grep -c region_id   ->  0
grep -inE 'condition_ld_matrix|nan_to_num'  ->  (empty)     m3-06 stays HELD
grep -inE "gsutil|gcloud|\bbq\b|dataproc|hailctl| wb "  ->  (empty -- PASS)
grep -c "load_curated_to_m2" qtl_coloc.smk  ->  0
grep -c -- '--ld-allele-join {params.ld_allele_join}' qtl_coloc.smk  ->  1
```

`tests/m3/sparse_parent_benchmark.tsv` was rewritten by the suite as expected and
**restored with `git checkout --`; it is NOT committed.**

### The bridge, working — measured on the acceptance fixture

```
[run_qtl_coloc] candidate overlaps: rsid=200, chrpos=0, variant_id=0
[run_qtl_coloc] match_key=rsid, GWAS snps: 200, QTL snps: 200, overlap: 200
[run_qtl_coloc] LD candidate key-space overlaps: panel_rownames=0, panel_chrpos=0,
                panel_chrpos_ref_alt=0, catalog_snp_id=182, catalog_chrpos=0
rc = 0

  status                         = success
  n_snps_overlap                 = 182
  ld_allele_join                 = true
  ld_key_space                   = catalog_snp_id
  ld_panel_overlap               = 182
  ld_allele_exact                = 136
  ld_allele_flipped              = 46
  ld_allele_dropped_palindromic  = 8
  ld_allele_dropped_mismatch     = 5
  ld_allele_dropped_ambiguous    = 1
  ld_allele_dropped_unusable     = 4
```

`panel_rownames = 0` is finding E's key defect, measured: the AoU panel's own key space
reaches **nothing** in the fit. `catalog_snp_id = 182` is the bridge. The `chr:pos`-named
fixture selects `catalog_chrpos = 182` instead — **both live sumstats conventions bridge.**

---

## 8. Track A — EUR invariance, and its inverted control

**WHOLE-FILE byte comparison** of the emitted JSON, HEAD's `run_qtl_coloc.R` vs
`git show 7b1025d:`'s, on the same legacy-shaped EUR fixture:

| Condition | Result |
|---|---|
| flags **absent** (exactly `sample_null_loci.py`'s argv) | **BYTE-IDENTICAL** |
| flags rendered `--ld-allele-join false` | **BYTE-IDENTICAL** |
| **INVERTED CONTROL:** AFR fixture, gate **ON** | **NOT identical** (`success` vs `too_few_snps`) |

Both identity tests carry a **non-vacuity guard**: the pre-change run must reach
`status == "success"`, so byte-identity is proven on a substantive result and not on a
matching error string.

`ld_status` / `ld_overlap_fraction` / `status` / `n_snps_overlap` were **NOT** used as
evidence — m3-04c proved EUR numerics move while those stay byte-identical.

`test_sample_null_loci_argv_still_takes_the_legacy_path` additionally asserts that
`sample_null_loci.py` contains neither new flag AND that the emitted JSON carries no
additive field. It is the live proof that the defaults point the right way.

**EUR / TRANS / EAS / HIS are structurally unreachable**, asserted against the REAL shipped
`config/pipeline.yaml` and against every degraded block shape (absent, non-dict, list,
empty, `enabled: false`, `ancestries: []`, `coloc` absent, `coloc: false`,
`coloc: "true"` as a string, `coloc: 1`). Their **DAG gains no new edge**:
`input.variants` is `[]` off the allow-list.

---

## Deviations from the plan

### 1. PLAN FACT WRONG — there are no AFR manifest rows; the sentinel branch is INERT today

The plan's Task 1 behaviour requires `build_manifest(..., resolver_ancestries={"AFR"})` to
write the sentinel "for AFR rows and the unchanged legacy path for EUR rows".
**`build_qtl_coloc_manifest.py::_ancestry_for_region` returns `"EUR"` UNCONDITIONALLY** —
it ignores the region argument entirely. There are no AFR rows to gate.

**Not improvised around.** Teaching it about AFR would CHANGE THE MANIFEST (new rows, new
`qtl_coloc_id`s, a different DAG) for a pipeline whose coloc outputs are 32/32 EUR and feed
Track A — a scope and analysis decision, not a plumbing fix. Instead:

* the mechanism is exercised on the ancestry the builder actually emits
  (`resolver_ancestries={"EUR"}` as an explicit FIXTURE choice, not a proposal);
* `test_ancestry_for_region_is_hardcoded_eur_today` pins the measured fact;
* `test_shipped_allow_list_changes_no_row_today` pins that the REAL allow-list leaves the
  manifest byte-identical;
* registered as **E-4** in `deferred-items.md`.

Both halves of finding E's remedy are correct and tested; the manifest half goes live the
moment `_ancestry_for_region` learns about AFR, and that fact is now recorded rather than
assumed.

### 2. PLAN SELF-CONTRADICTORY — STEP 6's code violates the plan's own T1.4

STEP 6 spells the allow-list as
`",".join(a for a in config.get("ld_read_path", {}).get("ancestries", []) if ld_coloc_applies(a, config))`
**inline in the rule**, which makes `qtl_coloc.smk` read the `ld_read_path` block directly
— contradicting the same plan's T1.4 requirement that the `.smk` contain "**no** second
`ld_read_path` block read". One of the two had to give.

**Resolved by satisfying BOTH**, rather than by weakening an assertion: the enumeration was
moved into `ld_read_path.py` as `ld_coloc_ancestries(config)`, which is itself filtered
through `ld_coloc_applies`. The `.smk` now names **no sub-key at all**
(`test_qtl_coloc_smk_never_re_derives_the_gate` asserts `"enabled"`, `"coloc"`,
`"ancestries"`, `"allele_aware"` are absent from the comment-stripped source), and the
DECISION is still exactly one predicate. This is a third exported helper the plan did not
list; it is the smallest change that leaves no requirement unmet.

### 3. Two shell-token traps found and fixed in this task's own changes (Rule 1)

* `--resolver-ancestries {params.resolver_ancestries}` — off the allow-list the value is
  the EMPTY STRING; unquoted, the shell collapses it and argparse consumes `--output` as
  its value, so the manifest build would fail **in exactly the default configuration**.
  Quoted, plus `test_the_resolver_ancestries_shell_token_is_quoted` and an end-to-end
  execution of the empty argv.
* `--variant-list {input.variants}` — same class. Fixed more strongly than by quoting: the
  **flag itself** is a `params` value that is `""` off the allow-list, so the token is
  **unconstructible** rather than merely quoted. The plan's literal `{input.variants}` is
  preserved in the shell.

### 4. `grep -c "load_curated_to_m2" qtl_coloc.smk` must be 0 — including in comments

The explanatory comment recording *why* the crosswalk loader is not imported originally
contained the symbol, making the plan's literal verify return 1. Rather than deviate on a
named acceptance criterion, the comment now names the loader **by role** and says so
explicitly. The literal grep is 0 and the documentation survives.

### 5. Three self-caught defects in my own tests, each a vacuous-assertion class

1. **A comment satisfying its own regex** (twice). `# NO load_curated_to_m2 IMPORT HERE`
   broke the absence assertion; `# ... --variant-list {input.variants} would render ...`
   broke the other. Fixed with two comment-strippers — `code_only` (strips docstrings too;
   for Python-code claims) and `strip_py_comments` (preserves strings; for claims about a
   Snakemake `shell:` body). This is one of the five failure modes the m3-04c process note
   names.
2. **A vacuous byte-identity fixture.** The builder fixture initially produced **zero
   rows** (a `gene` column name and a `sources:` YAML key), so three byte-identity tests
   compared `[] == []` and header-only files. `_rows` now asserts non-emptiness, and the
   TSV test asserts more than one line.
3. **A negative control that could not see its own subject.** The "every nested helper is
   closed over" test ran only the multiallelic fixture and therefore reported
   `.allele_counts0` as not-closed-over — that helper is reachable only via the `empty()`
   REJECTION path. It now runs every fixture and requires at least one to break. Same shape
   as the gate-disabled `test_ld_read_path.py` suite the blast radius indicts.

### 6. The matrix-class fix is GATED, not universal

The plan's matrix-class requirement is not explicitly gated. It was gated anyway, on the
fail-safe direction: an ungated fix would move an EUR job from `qtl_susie_failed` (rc 0) to
a **result**, which is a Track-A-moving change. **Measured** that this leaves nothing
undone: the legacy 1kG `.rds` carries `R <- as.matrix(ld_dt)` — a base matrix
(`plink_ld_to_rds.R:72`) — so the sparse defect is genuinely **inert** on the EUR path.
The gated fix covers exactly the path where the defect can occur.

### 7. The pre-LD-intersection `n_snps_overlap < 50` gate (`:183`) was left exit-0

That gate fires **before any LD is loaded** — a small GWAS∩QTL overlap is a
data-availability fact, not an LD-verification impossibility, so it is not one of F3's four
layers. Under the gate it still writes a status JSON, now carrying the provenance block
with `NA` counters, which reads correctly as "not measured".

---

## Freeze re-pin

> **`src/legacy/region_analysis/scripts/run_susie_rss.R` remains RE-FROZEN at `dc4bbd2`.**
> **This task did not unfreeze it and did not need to.** The differential agreement test
> READS the frozen source (body-walk extraction of an assignment expression) and never
> writes it; NC-2g's alterations are performed on in-memory / temp copies and each control
> re-asserts `git diff --exit-code dc4bbd2 -- run_susie_rss.R` mid-run.
> The forward gate is unchanged:
> `git diff --exit-code dc4bbd2 -- src/legacy/region_analysis/scripts/run_susie_rss.R`.
> **The unfreeze granted by Carter on 2026-08-05 is still SPENT.**

Frozen contracts **0-diff** vs `7b1025d`: `plink_ld_to_npz.py`, `ld_npz_to_rds.R`,
`condition_ld_matrix.py`. The m3-07 occlusion modules **0-diff**. `finemap.smk`,
`ld_panel.py`, `aggregate_qtl_coloc.py` **0-diff**. `finemap.smk:349-350`
(`params.region_id`) untouched — 0 `region_id` hits in the diff, pinned by
`test_params_region_id_is_not_declared_here`.

---

## Cost

**`$0`. NC State only. Zero perimeter contact.** No `gsutil` / `gcloud` / `bq` / `wb` /
`dataproc` / `hailctl` command was run in this session and none appears anywhere in the
diff. **The ~11-day billed AoU fire was NOT triggered.**

---

## Lessons

1. **A green assertion needs a negative control — and three of this task's own assertions
   were structurally incapable of failing before one was run.** Two comments satisfying
   their own regex, one zero-row fixture making three byte-identity tests vacuous, and one
   control that exercised the wrong code path. Every one was caught by running the control,
   not by reading the code.
2. **"Verify the helper list" is not the same as "assert the helper list".** The three
   nested closures the extractor must carry were verified by DROPPING each and requiring a
   break — and that immediately exposed that the naive one-fixture version of the check
   could not see `.allele_counts0` at all.
3. **A plan can be internally unsatisfiable without either half being wrong.** STEP 6's
   code and T1.4's requirement were both reasonable and mutually exclusive. Moving the
   knowledge into the module that owns it satisfied both; weakening the assertion would
   have satisfied neither honestly.
4. **An empty string is a shell-injection-adjacent hazard in its own right.** Two flags in
   this change would have failed in the DEFAULT configuration — the one nobody writes a
   fixture for — because an empty value lets the next flag become the value.
5. **Gate the fix to the path where the defect exists.** The sparse-matrix fix is correct
   everywhere, but applying it everywhere would have moved a manuscript in submission from
   "failed" to "a number". Measuring that the legacy path carries a base matrix turned a
   judgement call into a fact.

---

## Planning artifacts

`.planning/STATE.md` and `.planning/HANDOFF.json` are **Carter's** (standing directive
recorded in `260805-23d-SUMMARY.md` deviation 5) and were **NOT written**. `ROADMAP.md`
untouched — quick tasks are separate from planned phases. The only planning file this task
wrote besides this SUMMARY is
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`, which carries the E-2 /
E-3 / E-4 registry entries and is committed with the Task 3 code commit.

---

## Self-Check: PASSED

All 11 files named in `key-files` verified present on disk; both task commits
(`2563451`, `1815bfd`) verified present in `git log`. Nothing claimed that does not exist.
