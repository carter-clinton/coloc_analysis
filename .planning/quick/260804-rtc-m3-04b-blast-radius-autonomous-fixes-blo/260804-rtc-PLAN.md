---
phase: 260804-rtc-m3-04b-blast-radius-autonomous-fixes
plan: 01
type: execute
wave: 1
depends_on: []
autonomous: true
requirements: [D-04b-01, HIGH-4, HIGH-0, BLOCKER-4, LOW-1]
files_modified:
  - src/python/occlusion_coord_key.py          # NEW
  - src/python/occlusion_present_rate_scan.py
  - src/python/drop_occluded_from_sumstats.py
  - src/python/occlusion_manifest.py
  - src/python/assemble_occlusion_catalog.py
  - src/snakemake/rules/m3_occlusion_lockstep.smk
  - tests/m3/test_occlusion_coord_key.py        # NEW
  - tests/m3/test_occlusion_present_rate_scan.py
  - tests/m3/test_occlusion_lockstep_drop.py
  - tests/m3/test_occlusion_manifest.py
  - tests/m3/test_occlusion_catalog_assembly.py
  - .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.py   # NEW
  - .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.json # NEW
  - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md

must_haves:
  truths:
    - "A float-formatted INTEGRAL position ('5982778.0') resolves to the SAME canonical key as '5982778' in all three key implementations; a genuinely non-integral position ('5982778.5') RAISES and is never truncated."
    - "drop_occluded_from_sumstats reports n_unparseable / n_truncated, so 'ran and correctly found nothing' is distinguishable from 'ran, parsed nothing, dropped nothing' in the returned dict AND in counts.json."
    - "A sumstats file that carries body rows but yields ZERO coercible coordinates makes the present-rate scan and the drop filter FAIL LOUDLY, naming the file, instead of publishing a silent zero."
    - "assemble_occlusion_catalog REFUSES to stamp provenance_source=stage_a_manifest on a Stage-A rollup that does not cover every region carrying an excludelist."
    - "The expected-region helper returns 276 AFR region_ids from config/ld_regions.tsv — NOT 552 (the file is 276 unique region_id x 2 ancestries)."
    - "The real 9-file present-rate scan reports rs182965575 (GRCh37 1:5982778) present in 7 of 9 AFR sumstats, matching the project record (was 6 of 9)."
    - "The stroke double-count is VISIBLE (9 files / 8 distinct traits reported + a loud note); the published k/n denominator is NOT silently redefined."
    - "tests/m3 exits with >= 444 passed and 0 failed, with every new RED turned GREEN."
  artifacts:
    - path: "src/python/occlusion_coord_key.py"
      provides: "The single shared (chr,pos) canonical-key + integral-position coercion contract"
      exports: ["coerce_integral_position", "canonical_coord_key"]
      min_lines: 60
    - path: "tests/m3/test_occlusion_coord_key.py"
      provides: "RED-first regression for D-04b-01 + the three-way byte-compat proof"
      min_lines: 60
    - path: ".planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.json"
      provides: "The measured, auditable k/n for rs182965575 over the real 9 AFR files"
      contains: "n_traits_present"
    - path: "src/python/assemble_occlusion_catalog.py"
      provides: "Region-coverage assertion closing BLOCKER-4"
      contains: "allow_partial_manifest"
  key_links:
    - from: "src/python/occlusion_present_rate_scan.py"
      to: "src/python/occlusion_coord_key.py"
      via: "from occlusion_coord_key import canonical_coord_key"
      pattern: "occlusion_coord_key"
    - from: "src/python/drop_occluded_from_sumstats.py"
      to: "src/python/occlusion_coord_key.py"
      via: "from occlusion_coord_key import canonical_coord_key"
      pattern: "occlusion_coord_key"
    - from: "src/python/occlusion_manifest.py"
      to: "src/python/occlusion_coord_key.py"
      via: "_present_rate_key delegates after its pandas NA check"
      pattern: "canonical_coord_key"
    - from: "src/python/assemble_occlusion_catalog.py"
      to: "src/python/occlusion_manifest.py"
      via: "scan_present_rate(stats=scan_stats) -> enrich_occlusion_manifest(scan_stats=scan_stats)"
      pattern: "scan_stats"
    - from: "src/snakemake/rules/m3_occlusion_lockstep.smk"
      to: "src/python/assemble_occlusion_catalog.py"
      via: "--regions-tsv config/ld_regions.tsv on the assemble rule shell"
      pattern: "--regions-tsv"
---

<objective>
Land the four autonomous, `$0`, NC-State-only correctness fixes cleared by the m3-04b
blast radius: **D-04b-01** (float POS crashes the canonical key), **HIGH-4** (nothing
counts unparseable coordinates), **HIGH-0** (the total-miss guard is structurally
incapable of firing), and **BLOCKER-4** (a PARTIAL Stage-A rollup is stamped as complete
provenance). **LOW-1** (the `stroke` double-count) is folded in as *visibility only*.

Purpose: these gate (a) the ~11-day / $385–1,084 billed AoU fire's trustworthiness as a
drop key, and (b) the pre-registered per-variant present-rate k/n that osf.io/az52u
commits to publishing. They are cheap now and expensive after the fire.

Output: one shared coordinate-key utility, unparseable counters wired into the audit
artifacts, a guard that can actually fire, a region-coverage assertion, and a measured,
auditable k/n for rs182965575 over the real 9 AFR files.

**Cost/perimeter: `$0`. NC State only. Public GRCh37 data, read-only. No AoU resource,
no `gs://` object, no perimeter contact.**
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-SUMMARY.md
@src/python/occlusion_coord_key.py
@src/python/occlusion_present_rate_scan.py
@src/python/drop_occluded_from_sumstats.py
@src/python/occlusion_manifest.py
@src/python/assemble_occlusion_catalog.py
@src/python/occlusion_lockstep_cli.py

<hard_constraints>
**THE m3-04b 0-DIFF PIN ON THESE FOUR MODULES IS RELEASED.** It was scoped to m3-04b's
own must_haves; `m3-04b-W4-SUMMARY.md:312-314` explicitly assigns the D-04b-01 fix to
"a later plan" = THIS plan. You MAY edit `occlusion_present_rate_scan.py`,
`drop_occluded_from_sumstats.py`, `occlusion_manifest.py`,
`assemble_occlusion_catalog.py`.

**STILL FROZEN — do NOT touch:** `src/python/plink_ld_to_npz.py`,
`src/scripts/ld_npz_to_rds.R`, `src/python/condition_ld_matrix.py`. Do NOT revive
`NaN->0`. Do NOT import or feed `condition_ld_matrix` to anything — m3-06 stays HELD.

**Do NOT touch `src/snakemake/rules/finemap.smk`.** It is m3-04c's territory and is
mid-replan. In particular do NOT change `run_finemap.params.region_id` (now at
`finemap.smk:206`, NOT the `:158` older docs cite).

**Git staging: explicit paths ONLY.** Never `git add -A` / `git add .` on this GPFS
tree (a multi-terminal collision baked this rule). No worktree isolation.

**TDD is mandatory, failing-test-FIRST.** Write the RED, RUN it, SEE it fail for the
right reason, then GREEN. **NEVER edit an existing test to force green.** If an existing
test genuinely contradicts a required change, **STOP and surface it as a decision** —
do not improvise. (`[[feedback_check_plan_against_red_before_executing]]`; this project
has been bitten hard by exactly that escape.)

**Never silently move a pre-registered number.** The project record is
`rs182965575 present in 7 of 9 AFR sumstats`. If any change moves that, STOP and
surface it — do not ship it.

**pytest:** `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest`.
Do NOT tell anyone to `conda activate`. Full `tests/m3` takes ~420 s → run targeted
subsets during development and ONE full run at the end.
**Baseline: 444 passed / 31 skipped / 0 failed. Exit must be >= 444 passed, 0 failed.**
</hard_constraints>

<interfaces>
<!-- The contracts the executor needs. Use these directly — no codebase exploration. -->

**The THREE duplicated key implementations that must stay byte-compatible in output:**

```python
# src/python/occlusion_present_rate_scan.py:72-86   (stdlib only — MUST stay pandas-free)
def _canonical_key(chrom, pos) -> tuple:
    contig = str(chrom).strip()
    if contig.lower().startswith("chr"): contig = contig[3:]
    if contig.isdigit(): contig = int(contig)
    return (contig, int(pos))                       # <-- ValueError on '5982778.0'

# src/python/drop_occluded_from_sumstats.py:90-104  (identical body)

# src/python/occlusion_manifest.py:296-317          (pandas-aware; NA -> None)
def _present_rate_key(chrom, pos_grch37):
    if pos_grch37 is None or pd.isna(pos_grch37): return None
    ...same three lines...
    return (contig, int(pos_grch37))
```

**The scan return is a NO-ADAPTER contract — do NOT add a 5th per-variant key:**
```python
scan_present_rate(variants_grch37, sumstats_paths) -> {
    (chr, pos): {"n_traits_present": int, "n_traits_scanned": int,
                 "present_rate": float, "traits_present": list[str]}
}
# those four names == occlusion_manifest.STAGE_B_TRAIT_COLUMNS + the rate, fed
# DIRECTLY to enrich_occlusion_manifest(present_rate=...) with NO adapter.
```

**The drop return (safe to EXTEND — verified: no test asserts exact dict equality;
`occlusion_lockstep_cli._emit_counts` json.dumps the whole dict, so new keys flow into
`counts.json` for free):**
```python
drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> {"n_in","n_dropped","n_out"}
```

**The established counter naming to MIRROR (do not invent a new one):**
`assemble_occlusion_catalog.py` already has `n_unparseable`
(`:161, :170, :192, :341, :382, :439`) for its degraded path.

**The BLOCKER-4 site verbatim (`assemble_occlusion_catalog.py:352-362`):**
```python
if not rollup.empty:
    source = PROVENANCE_STAGE_A_MANIFEST
    if excludelist_paths:
        print("... the {N} excludelist(s) are IGNORED "
              "(the manifests carry strictly more provenance).", file=sys.stderr)
    _write_stage_a(rollup.to_dict("records"), stage_a, source)
```

**The HIGH-0 site (`occlusion_manifest.py:373-394`)** — READ the comment at `:375-383`
FIRST. It documents a **deliberate, correct** decision to scope the guard to LIFTABLE
rows only. **Your fix must PRESERVE that reasoning verbatim.**

**Assemble rule shell block (`m3_occlusion_lockstep.smk:228-242`)** — where `--regions-tsv`
is appended:
```
        python {input.script} \
            --chain {input.chain} \
            --out {output.catalog} \
            {params.sumstats_args} \
            {params.manifest_args} \
            {params.excludelist_args} \
            {params.degraded_flag} \
            > {log} 2>&1
```
Existing convention for the regions manifest path
(`m3_ingest_aou_ld.smk:79-80`): `config.get("ld_regions_manifest", "config/ld_regions.tsv")`.

**Test import path:** `tests/m3/conftest.py:26-29` puts `src/python` on `sys.path`,
so tests do a bare `import occlusion_coord_key`.

**⚠⚠ THE 276/552 TRAP — ALREADY VERIFIED, DO NOT GET THIS WRONG.**
`config/ld_regions.tsv` = header + **552 data rows** = **276 unique `region_id` x 2
ancestries (AFR, EUR)**. Verified directly:
`awk -F'\t' 'NR>1{print $1}' config/ld_regions.tsv | sort -u | wc -l` -> **276**;
AFR-only unique region_id -> **276**; EUR-only unique region_id -> **276**.
The authoritative count is `nunique(region_id)`, **NEVER** `len(df)` / `wc -l`
(which give 552/553 and would fail 100% of the time).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Extract ONE shared integral-position coercion + canonical key (D-04b-01)</name>
  <files>
    src/python/occlusion_coord_key.py (NEW),
    src/python/occlusion_present_rate_scan.py,
    src/python/drop_occluded_from_sumstats.py,
    src/python/occlusion_manifest.py,
    tests/m3/test_occlusion_coord_key.py (NEW),
    tests/m3/test_occlusion_lockstep_drop.py,
    tests/m3/test_occlusion_present_rate_scan.py
  </files>

  <behavior>
  RED first — write and RUN these, confirm they FAIL for the right reason, then GREEN.

  New `tests/m3/test_occlusion_coord_key.py`:
  - `coerce_integral_position('5982778.0') == 5982778` (the D-04b-01 headline).
  - `coerce_integral_position('5982778') == 5982778`.
  - `coerce_integral_position(5982778.0) == 5982778` (numpy/py float from pandas).
  - `coerce_integral_position('5982778.00') == 5982778` and `'5982778.' == 5982778`.
  - `coerce_integral_position('5982778.5')` **RAISES ValueError** — NEVER truncates to
    5982778. Assert the message names the value (this is the whole point of the fix
    shape prescribed by `m3-04b-W4-SUMMARY.md:312-314`).
  - `coerce_integral_position('1_000')` RAISES (today `int('1_000')` -> 1000 — a latent
    quirk the blast radius flagged; close it now, it has no live exposure).
  - `coerce_integral_position('1e6')` RAISES (measured: ZERO sci-notation anywhere in the
    10-file corpus; accepting it would be a silent widening. Rejecting makes a
    sci-notation file blare via the T2 counter instead of scoring silently absent).
  - `coerce_integral_position('')`, `'NA'`, `'.'`, `None`, `'  '` all RAISE.
  - `canonical_coord_key('chr1','5982778.0') == canonical_coord_key('1', 5982778) == (1, 5982778)`.
  - `canonical_coord_key('X', 100) == ('X', 100)` (contig stays a str — LOW-5 is
    explicitly OUT of scope; pin today's behavior so it cannot drift silently).
  - **THREE-WAY BYTE-COMPAT PROOF** (this is the "prove the join still holds" requirement):
    parametrize a matrix of `(chrom, pos)` inputs — `('1','5982778')`, `(1, 5982778)`,
    `('chr1', 5982778)`, `('1', numpy.int64(5982778))`, `('1', 5982778.0)`, `('X', 100)` —
    and assert `occlusion_present_rate_scan._canonical_key`,
    `drop_occluded_from_sumstats._canonical_key` and
    `occlusion_manifest._present_rate_key` return **the identical tuple** for every one.
  - `occlusion_manifest._present_rate_key(1, None)` and `(1, pd.NA)` still return `None`
    (its documented unlifted-row branch survives the refactor).
  - `import occlusion_coord_key` succeeds with **no pandas / no pyliftover** in the
    module's imports (assert via `inspect.getsource` or an explicit source scan) —
    `occlusion_present_rate_scan`'s docstring guarantees it stays importable without them.

  In `tests/m3/test_occlusion_lockstep_drop.py` — the SILENT UNDER-DROP regression:
  - Build a sumstats fixture whose POS column is FLOAT-formatted (`'5982778.0'`, exactly
    the `bmi.AFR.PAGE.2019.GRCh37` shape: 100% of 17,195,956 rows) plus a manifest keyed
    on integer `5982778`. Today: `n_dropped == 0` wearing a clean
    `n_in - n_dropped == n_out`. Required: `n_dropped == 1` and the drop is LOGGED.

  In `tests/m3/test_occlusion_present_rate_scan.py` — the k/n undercount regression:
  - Two files for the same variant, one int-POS and one float-POS. Today: k=1.
    Required: k=2, `n_traits_scanned=2`, `present_rate == 1.0`.
  </behavior>

  <action>
  1. **Write the REDs above and RUN them.** Confirm each fails for the stated reason
     (`ValueError: invalid literal for int() with base 10: '5982778.0'` / `n_dropped == 0`
     / `k == 1`). A RED that passes on first run is a broken RED — fix the RED, not the code.

  2. **Create `src/python/occlusion_coord_key.py`** — STDLIB ONLY (no pandas, no
     pyliftover, no numpy import; it must accept numpy scalars duck-typed, not by import).
     Module docstring must state: this is the ONE canonical (CHR,POS) key contract, that
     three call sites previously duplicated it verbatim, that D-04b-01
     (`bmi.AFR.PAGE.2019.GRCh37`, 100% float POS over 17,195,956 rows) is the bug it
     closes, and that it is deliberately dependency-free so
     `occlusion_present_rate_scan` stays importable without the span filter or pyliftover.

     ```
     def coerce_integral_position(value) -> int
     ```
     Contract, exactly:
     - `int` (incl. any integral duck type where `int(value) == value` and it is not a
       float): return as `int`.
     - `float` (incl. `numpy.float64`): accept **only** if `value.is_integer()` /
       `float(value).is_integer()`; otherwise `raise ValueError`. **NEVER truncate.**
     - `str`: `.strip()`, then accept ONLY `^[+-]?[0-9]+$` -> `int`, or
       `^[+-]?[0-9]+\.[0-9]*$` where the fractional digits are all `0` -> `int` of the
       integer part. Everything else raises: underscores, scientific notation,
       non-ASCII/full-width digits, `''`, `'NA'`, `'.'`, `None`.
       **Use an explicit `re.fullmatch`, not `int()`/`float()` with a try/except** — that
       is what closes the `'1_000'` and full-width-digit quirks the blast radius flagged.
     - Every raise message must quote the offending value AND say what is accepted, so
       the T2 counter's exemplar line is self-explanatory.

     ```
     def canonical_coord_key(chrom, pos) -> tuple
     ```
     - Contig normalization **byte-identical to today**: `str(chrom).strip()`; strip a
       case-insensitive leading `chr`; `if contig.isdigit(): contig = int(contig)`.
       **Do NOT tighten `.isdigit()`** — that would move the manifest-side key and break
       the join. LOW-5 (chrX `'X'` vs `23`) is explicitly OUT of scope; add a comment
       saying so and naming it, so a future reader does not "fix" it here by accident.
     - `return (contig, coerce_integral_position(pos))`.

  3. **Rewire all three call sites to delegate** — do NOT fix it twice in place
     (`[[feedback_extract_reusable_utilities]]`: recurrent bug class -> ONE reusable
     utility + failing-test-first regression):
     - `occlusion_present_rate_scan.py`: `from occlusion_coord_key import canonical_coord_key`;
       keep the private name `_canonical_key` as a **one-line delegation** so any existing
       reference still resolves; replace its body's duplicated logic with the call and
       shrink its docstring to point at the shared module.
     - `drop_occluded_from_sumstats.py`: identical treatment.
     - `occlusion_manifest.py:_present_rate_key`: **keep** its pandas `None`/`pd.isna`
       early-return (that branch needs pandas and must stay here), then
       `return canonical_coord_key(chrom, pos_grch37)`. Preserve its existing docstring
       paragraphs about why the helper exists and why the `"chr1"` branch is not pinned
       by a contrived test.
     - Update the three module docstrings that currently say the rule is "mirrored rather
       than imported" (`occlusion_present_rate_scan.py:31-35` and the `_canonical_key`
       docstrings) — the rule is now IMPORTED from one place. Leaving a docstring
       asserting a mirror that no longer exists is exactly the
       `[[feedback_fallback_chain_hides_unreachable_artifact]]` failure mode.

  4. **Run the targeted suites and confirm GREEN.** If `test_occlusion_manifest.py` goes
     red because a pre-existing test depended on the silent non-integral truncation:
     **STOP. Surface it as a decision. Do NOT edit that test.**
  </action>

  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_coord_key.py tests/m3/test_occlusion_lockstep_drop.py tests/m3/test_occlusion_present_rate_scan.py tests/m3/test_occlusion_manifest.py -q 2>&1 | tail -20</automated>
    <automated>grep -c "int(pos)\|int(pos_grch37)" src/python/occlusion_present_rate_scan.py src/python/drop_occluded_from_sumstats.py src/python/occlusion_manifest.py</automated>
    <automated>grep -n "^import \|^from " src/python/occlusion_coord_key.py</automated>
  </verify>

  <done>
  `occlusion_coord_key.py` exists, imports nothing outside the stdlib, and is the ONLY
  place the `(chr,pos)` key is computed (the three `int(pos)` / `int(pos_grch37)` call
  sites are gone). `'5982778.0'` -> `5982778`; `'5982778.5'` RAISES. All three key
  implementations return byte-identical tuples across the parametrized matrix. The
  float-POS under-drop regression and the k/n undercount regression are GREEN. All four
  targeted test files pass with 0 failures.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Unparseable counters (HIGH-4) + a total-miss guard that can actually fire (HIGH-0)</name>
  <files>
    src/python/drop_occluded_from_sumstats.py,
    src/python/occlusion_present_rate_scan.py,
    src/python/occlusion_manifest.py,
    src/python/assemble_occlusion_catalog.py,
    src/python/occlusion_lockstep_cli.py,
    tests/m3/test_occlusion_lockstep_drop.py,
    tests/m3/test_occlusion_present_rate_scan.py,
    tests/m3/test_occlusion_manifest.py,
    tests/m3/test_occlusion_catalog_assembly.py,
    tests/m3/test_occlusion_lockstep_wiring.py
  </files>

  <behavior>
  RED first, then GREEN.

  HIGH-4 — `drop_occluded_from_sumstats`:
  - A file where SOME rows have unparseable coordinates returns `n_unparseable == <that
    count>` and `n_truncated == <short-row count>` alongside `n_in/n_dropped/n_out`, and
    the invariant `n_in - n_dropped == n_out` STILL holds (the counters are additive
    diagnostics, not a change to the audit invariant).
  - A file where **every** body row is unparseable (`n_in > 0 and n_unparseable == n_in`)
    **RAISES ValueError**. Message must name the file, the count, and the first offending
    raw coordinate. Fail-closed: a clean `n_dropped == 0` over a wholly unparsed file is
    the exact silent under-drop the lockstep exists to prevent.
  - `counts.json` written via `occlusion_lockstep_cli` carries the new keys
    (`_emit_counts` json.dumps the whole dict — assert the file content, not the
    function).
  - A clean file still returns `n_unparseable == 0`, `n_truncated == 0` — no false alarm.

  HIGH-4 — `occlusion_present_rate_scan`:
  - `scan_present_rate(..., stats=d)` leaves the per-variant return **byte-identical**
    (still exactly the four keys) and populates `d` with `n_files_scanned`,
    `n_distinct_traits_scanned`, `duplicate_traits`, `n_rows_seen`, `n_rows_parsed`,
    `n_unparseable`, `n_truncated`, `n_files_empty`, and `per_file` (one record per file).
  - Calling `scan_present_rate` WITHOUT `stats` still works and returns the same thing
    (kwarg-only, default `None`).

  HIGH-0 — the guard that can fire:
  - `scan_present_rate` **RAISES ValueError** when any file has
    `n_rows_seen > 0 and n_rows_parsed == 0`. This is the unambiguous predicate: a file
    that carries body rows but not ONE coercible coordinate is BROKEN, not empty. Message
    names the file and the first offending value.
  - A header-only / 0-byte file does NOT raise (`n_rows_seen == 0`); it increments
    `n_files_empty`. A legitimately empty scan stays legal.
  - A file whose FIRST line is blank but which has further non-blank content RAISES
    (today `:159` silently `continue`s and scores the whole file "nothing present",
    mis-counting BOTH k and n).
  - `enrich_occlusion_manifest(..., present_rate=pr, scan_stats=st)` RAISES when
    `st["n_rows_seen"] > 0 and st["n_rows_parsed"] == 0`, even though every requested key
    IS present in `pr` — i.e. the new guard fires exactly where the old membership test
    could not. **Reproduce the blast radius' verified scenario**: a manifest lifted to
    `(1, 5982778)` scanned against a float-POS file alone, which today publishes
    `n_traits_present=0, traits_present='[]'` and does NOT raise.
  - `enrich_occlusion_manifest` called WITHOUT `scan_stats` behaves exactly as today
    (all three existing pinned raise-boundary tests stay green, untouched).
  - A manifest whose occluded variants ALL sit in a liftover/assembly gap (zero liftable
    rows) still does NOT raise — pin this explicitly. That is the deliberate,
    documented decision at `occlusion_manifest.py:375-383` and it must survive.
  - `assemble_occlusion_catalog` surfaces the scan stats in its returned dict as
    `n_files_scanned`, `n_distinct_traits_scanned`, `n_scan_rows_seen`,
    `n_scan_rows_parsed`, `n_scan_unparseable` — **`n_scan_unparseable`, NOT
    `n_unparseable`**, which is already taken by the degraded excludelist path
    (`:341, :382, :439`) and must not be collided with.
  </behavior>

  <action>
  1. **Write the REDs and RUN them.** The HIGH-0 RED is the load-bearing one: it must
     demonstrate that the CURRENT `any(k in present_rate for k in keys_present)` test
     passes while the scan parsed nothing. If your RED does not reproduce that, you have
     not reproduced HIGH-0.

  2. **`drop_occluded_from_sumstats`** — add `n_unparseable` and `n_truncated` counters at
     the two swallow sites the blast radius names (`:215-216` unparseable coord, `:212`
     short row). Mirror the ESTABLISHED naming/reporting convention in
     `assemble_occlusion_catalog._degraded_records` (loud STDERR warning + a counter) —
     do not invent a new one. Emit one STDERR summary line at the end when
     `n_unparseable > 0 or n_truncated > 0`, naming the file, the counts, and the first
     offending raw value. Then raise when `n_in > 0 and n_unparseable == n_in`. Extend the
     module docstring's CONTRACT block to document the five returned keys and to state
     plainly that `n_in - n_dropped == n_out` holding is NOT evidence the file parsed.
     Preserve the early-return `{"n_in":0,...}` on an empty header — extend it with the
     two new keys so the dict shape is uniform across every return path.

  3. **`occlusion_present_rate_scan`** — add the kwarg-only `stats: dict | None = None`
     out-param, populate it in place, and add the two raises above. **Do NOT add a fifth
     key to the per-variant record** — that would break the no-adapter contract with
     `enrich_occlusion_manifest`. Track `n_rows_seen` / `n_rows_parsed` per file inside the
     existing single pass (no second pass — these are genome-wide files). Also record each
     file's resolved trait label in `per_file` (this is what T3's LOW-1 visibility reads).

  4. **`occlusion_manifest.enrich_occlusion_manifest`** — add the kwarg-only
     `scan_stats: dict | None = None`.
     - **KEEP the existing `keys_present` membership guard AND its comment at `:375-383`
       verbatim.** That comment documents a correct decision (scope the guard to LIFTABLE
       rows; an unliftable row is a documented signal, not a bug). Do not weaken it and do
       not make an assembly-gap region hard-abort.
     - ADD the substance guard immediately BEFORE it, with a comment explaining the HIGH-0
       finding in one sentence: **key PRESENCE is necessary but NOT sufficient — the scan
       returns a record for EVERY requested key, so membership is always True and can only
       detect key-SHAPE drift. Substance (did the scan parse anything?) is the missing
       half, and it is not derivable from `present_rate` alone — which is why
       `scan_stats` is threaded in.**
     - Add a FOURTH bullet to the docstring's "THE EXACT RAISE BOUNDARY" block covering
       the new `scan_stats` case. Leave the three existing bullets untouched.

  5. **`assemble_occlusion_catalog`** — create `scan_stats: dict = {}`, pass it to
     `scan_present_rate(keys, sumstats_paths, stats=scan_stats)`, thread it into
     `om.enrich_occlusion_manifest(..., scan_stats=scan_stats or None)`, and surface the
     five fields in the returned dict. Extend the function docstring's `Returns` line.

  6. **`occlusion_lockstep_cli`** — no code change should be needed (`_emit_counts`
     json.dumps the whole dict). VERIFY that by asserting `counts.json` content in the
     test, and extend `_emit_counts`'s docstring to say the counts now also carry the
     parse-health fields so a reader knows the invariant alone is not a health check.

  7. Run the targeted suites. Note `tests/m3/test_occlusion_lockstep_wiring.py` asserts
     `counts["n_in"]`/`["n_dropped"]`/`["n_out"]` **key-by-key, never exact-dict
     equality** (verified) — added keys are safe. If any pre-existing test contradicts a
     required change: **STOP and surface it. Do not edit the test.**
  </action>

  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_lockstep_drop.py tests/m3/test_occlusion_present_rate_scan.py tests/m3/test_occlusion_manifest.py tests/m3/test_occlusion_catalog_assembly.py tests/m3/test_occlusion_lockstep_wiring.py -q 2>&1 | tail -20</automated>
    <automated>grep -n "n_unparseable\|n_truncated\|n_rows_parsed\|scan_stats\|n_scan_unparseable" src/python/drop_occluded_from_sumstats.py src/python/occlusion_present_rate_scan.py src/python/occlusion_manifest.py src/python/assemble_occlusion_catalog.py</automated>
    <automated>grep -n "Guarding on \`keys\` instead of" src/python/occlusion_manifest.py</automated>
  </verify>

  <done>
  `drop_occluded_from_sumstats` returns `n_unparseable` + `n_truncated` on every path,
  they reach `counts.json`, and a 100%-unparseable file raises instead of reporting a
  clean `n_dropped == 0`. `scan_present_rate` fills a `stats` out-param without touching
  its four-key per-variant contract and raises on a body-rows-but-nothing-parsed file.
  `enrich_occlusion_manifest` raises on the blast radius' verified HIGH-0 scenario while
  the liftable-scoping comment at `:375-383` survives verbatim and the assembly-gap
  no-raise case is pinned by a test. `assemble_occlusion_catalog` surfaces the five scan
  fields under non-colliding names. All five targeted test files pass, 0 failures.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Region-coverage assertion (BLOCKER-4), LOW-1 visibility, and the measured k/n</name>
  <files>
    src/python/assemble_occlusion_catalog.py,
    src/python/occlusion_present_rate_scan.py,
    src/snakemake/rules/m3_occlusion_lockstep.smk,
    tests/m3/test_occlusion_catalog_assembly.py,
    .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.py,
    .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.json,
    .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
  </files>

  <behavior>
  RED first, then GREEN.

  BLOCKER-4 — reproduce the blast radius' verified end-to-end failure, then close it:
  - 1 Stage-A manifest (region A) + 1 excludelist-only region (region B), both variants
    genuinely present in the sumstats. **Today**: `{'n_regions': 1, 'source':
    'stage_a_manifest'}`, catalog has 1 row, region B ABSENT, and a downstream drop
    reports `n_dropped=1` when truth is 2. **Required**: `assemble_occlusion_catalog`
    RAISES `ValueError`, naming region B as covered by an excludelist but absent from the
    Stage-A rollup, and naming both remedies. Nothing is written to `out_path`.
  - `allow_partial_manifest=True` (and `--allow-partial-manifest`) accepts the same input
    explicitly, and the returned dict then reports
    `n_regions_excludelist_only == 1` so the incompleteness is IN the artifact's
    provenance, never inferred from its absence.
  - When the manifest set DOES cover every excludelist region, no raise, `source ==
    'stage_a_manifest'`, and the STDERR note now claims only what is true (see action 3).
  - The existing degraded path (`allow_degraded`) and the empty path are UNCHANGED — pin
    them so this fix cannot regress `test_degraded_reconstruction_refuses_without_flag`
    or `test_empty_catalog_still_carries_stage_b_columns`.

  The 276/552 trap:
  - `load_expected_region_ids('config/ld_regions.tsv', ancestry='AFR')` returns a set of
    length **276**. Assert `== 276` **and** `!= 552` **and** `!= 553` explicitly, with a
    comment naming the trap, so a future `len(df)` / `wc -l` regression fails loudly.
  - `expected_region_ids` supplied + an OBSERVED region id not in it -> RAISE (naming
    drift / crosswalk bug).
  - `expected_region_ids` supplied + observed is a strict SUBSET -> **no raise**, and
    `n_regions_expected` / `n_regions_missing` are REPORTED. Pin this: a region with zero
    occluded variants legitimately writes no manifest (`assemble_occlusion_catalog.py:346-347`),
    so `n_regions == 276` is NOT a valid invariant and must never be asserted.

  LOW-1 visibility (report, do NOT silently redefine):
  - With two files carrying the same trait label, `stats["n_files_scanned"] == 2`,
    `stats["n_distinct_traits_scanned"] == 1`, `stats["duplicate_traits"] == ["stroke"]`,
    and a loud STDERR note fires. The per-variant `n_traits_scanned` (the FILE-based
    denominator the pre-registration publishes) is **UNCHANGED**.
  </behavior>

  <action>
  1. **Write the REDs and RUN them**, including the exact 1-manifest + 1-excludelist
     reproduction from the blast radius. Confirm today's behavior matches the verified
     `{'n_regions': 1, ..., 'source': 'stage_a_manifest'}` before fixing.

  2. **Add `load_expected_region_ids(regions_tsv, ancestry="AFR") -> set[str]`** to
     `assemble_occlusion_catalog.py`. Its docstring MUST carry the trap in plain words:
     *"`config/ld_regions.tsv` is header + 552 DATA ROWS = 276 unique `region_id` x 2
     ancestries (AFR, EUR). The authoritative count is `nunique(region_id)` filtered to
     `ancestry` — NEVER `len(df)` or `wc -l`, which give 552/553 and would make any
     coverage assertion fail 100% of the time."*
     Implement as `set(df.loc[df["ancestry"] == ancestry, "region_id"].astype(str))`.

  3. **Close BLOCKER-4** at `assemble_occlusion_catalog.py:352-362`. Add kwarg-only
     `expected_region_ids: Iterable[str] | None = None` and
     `allow_partial_manifest: bool = False`. In the `if not rollup.empty:` branch:
     ```
     manifest_regions = set(rollup["region_id"].astype(str))
     excl_regions     = {_region_id_from_excludelist(p) for p in excludelist_paths}
     orphaned         = sorted(excl_regions - manifest_regions)
     if orphaned and not allow_partial_manifest:  raise ValueError(...)
     ```
     The raise message must state, explicitly, WHY the shipped note was wrong: *"the
     manifests carry strictly more provenance" is true PER REGION and FALSE AS A SET CLAIM
     when the manifest set is a SUBSET of the regions with excludelists.* Name the
     orphaned region ids, state the consequence (their occluded variants are never dropped
     from the sumstats = ORPHANED VARIANTS, the exact failure osf.io/az52u exists to
     forbid), and name both remedies (supply the missing Stage-A manifests, or pass
     `--allow-partial-manifest` to accept a knowingly-incomplete catalog explicitly).
     **Rewrite the existing STDERR NOTE** so it claims only what is true — e.g. *"every
     excludelist region is already covered by a Stage-A manifest, so the {N} excludelist(s)
     are IGNORED"*. Do NOT implement a manifest∪excludelist union: it would produce a
     MIXED `provenance_source` (a property §1 of the blast radius verified as currently
     invariant) and would let degraded rows ride out WITHOUT the `allow_degraded` gate the
     pre-registration depends on. Record that reasoning in a code comment.
     Then add the coverage reporting: `unknown = observed - expected` -> RAISE when
     `expected_region_ids` is supplied; `n_regions_expected` / `n_regions_missing` /
     `n_regions_excludelist_only` -> REPORTED in the returned dict, with a comment saying
     why `missing` is reported and never asserted (zero-occlusion regions write no
     manifest).

  4. **CLI + rule wiring** so the check is LIVE in production, not merely available:
     - `main()`: add `--regions-tsv` (default None), `--regions-ancestry` (default `AFR`),
       `--allow-partial-manifest`. When `--regions-tsv` is given, call
       `load_expected_region_ids` and pass the result through.
     - `m3_occlusion_lockstep.smk`: add
       `OCCLUSION_REGIONS_TSV = config.get("ld_regions_manifest", "config/ld_regions.tsv")`
       (mirroring `m3_ingest_aou_ld.smk:79-80`), declare it as an `input:` of
       `rule m3_assemble_occlusion_catalog`, and append `--regions-tsv {input.regions_tsv}`
       to the shell block at `:228-242`. **Touch NOTHING in `finemap.smk`.**

  5. **LOW-1 — visibility only.** In `occlusion_present_rate_scan`, populate
     `stats["n_distinct_traits_scanned"]` and `stats["duplicate_traits"]` from the
     `per_file` labels added in T2, and emit ONE loud STDERR note when
     `duplicate_traits` is non-empty: the scan resolves 9 files but only 8 distinct traits
     (`stroke.AFR` + `stroke.AFR.GIGASTROKE.2022.GRCh37`), so `n_traits_scanned` is a
     **FILE** rate, not a trait rate.
     **DO NOT change the denominator.** The project record and the pre-registration
     publish "present in 7 of 9 AFR **sumstats**" — a file rate. Redefining it to distinct
     traits would move a pre-registered number, which is Carter's call, not an executor's.
     Log that fork to `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` as
     `LOW-1 DEFERRED — denominator redefinition (files vs distinct traits) needs Carter`.

  6. **Measure the real k/n** — this is the pre-registered number, so measure it, do not
     assert it blind. Write
     `.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.py`
     (use the Write tool, not a heredoc) that:
     - imports `scan_present_rate` from `src/python`,
     - scans the target `[(1, 5982778)]` (rs182965575, GRCh37) over the **9** files
       matching `data/processed/sumstats_harmonized/*.AFR*.tsv.bgz` **excluding**
       `asthma.AFR.grch38_backup.tsv.bgz` (a build-38 backup — scanning it would put
       GRCh38 coordinates into a GRCh37 k/n; this is the exact scope
       `m3_occlusion_lockstep.smk:156-159` defines),
     - passes a `stats` dict,
     - writes `{"variant": "rs182965575", "chr": 1, "pos_grch37": 5982778,
       "n_traits_present": k, "n_traits_scanned": n, "traits_present": [...],
       "stats": {...}, "files": [...]}` to `measure_present_rate_kn.json` beside it.
     Run it DETACHED with a generous cap — 9 files, ~130M rows, streamed gzip in Python:
     **expect 1–4 hours.** `timeout 21600 <pytest-env python> <script> > <log> 2>&1 &`,
     then poll the log. **DO NOT KILL IT.** `$0`, NC State, public data, read-only.
     - **Expected: `n_traits_present == 7`, `n_traits_scanned == 9`** (was 6 of 9 —
       `m3-04b-W4-SUMMARY.md:300-307`), and `traits_present` includes `bmi`.
     - **If the measured k/n is anything other than 7/9: STOP and surface it as a
       decision.** A pre-registered number moved; that is not an executor's call.
     Commit both the script and the JSON — they are the auditable provenance for the
     published k/n.

  7. **One full-suite run at the end** (~420 s). Then stage with EXPLICIT PATHS ONLY.
  </action>

  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_catalog_assembly.py -q 2>&1 | tail -20</automated>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import sys; sys.path.insert(0,'src/python'); from assemble_occlusion_catalog import load_expected_region_ids as f; s=f('config/ld_regions.tsv'); print(len(s)); assert len(s)==276, f'THE 276/552 TRAP: got {len(s)}'"</automated>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import json; d=json.load(open('.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.json')); print(d['n_traits_present'],'/',d['n_traits_scanned']); assert (d['n_traits_present'],d['n_traits_scanned'])==(7,9), 'PRE-REGISTERED NUMBER MOVED — STOP'"</automated>
    <automated>grep -n "regions_tsv\|allow_partial_manifest" src/snakemake/rules/m3_occlusion_lockstep.smk src/python/assemble_occlusion_catalog.py</automated>
    <automated>git diff --stat -- src/snakemake/rules/finemap.smk src/python/plink_ld_to_npz.py src/python/condition_ld_matrix.py src/scripts/ld_npz_to_rds.R</automated>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q 2>&1 | tail -5</automated>
  </verify>

  <done>
  A 1-manifest + 1-excludelist-only input RAISES instead of silently stamping
  `stage_a_manifest` on a partial rollup; `--allow-partial-manifest` accepts it explicitly
  and reports `n_regions_excludelist_only`. `load_expected_region_ids` returns 276 (not
  552/553) and its trap is pinned by a test. `--regions-tsv` is wired into
  `m3_assemble_occlusion_catalog` so the coverage check is live. The stroke double-count is
  reported (9 files / 8 traits) with the published FILE denominator untouched, and the
  denominator fork is logged to `deferred-items.md`.
  `measure_present_rate_kn.json` records **7 of 9** for rs182965575. `git diff --stat` on
  the four frozen/off-limits files is EMPTY. Full `tests/m3` reports **>= 444 passed,
  0 failed**.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

The security-relevant boundary in this plan is **scientific data integrity**, not network
attack surface. This is an offline research pipeline on public data.

| Boundary | Description |
|----------|-------------|
| external public sumstats file -> parser | Third-party-formatted `POS` text crosses into a coercion that decides whether a variant is dropped. Untrusted *format*, trusted *provenance*. |
| perimeter-egressed artifacts -> catalog assembler | Excludelists/manifests arrive as a possibly-INCOMPLETE set; the assembler decides a provenance claim from them. |
| catalog -> published pre-registered k/n | A wrong number here is published to osf.io/az52u and is the highest-consequence output of the whole path. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-rtc-01 | Tampering (silent data corruption) | `_canonical_key` `int(pos)` | mitigate | T1: strict `re.fullmatch` coercion accepting integral floats, RAISING on non-integral — never a silent truncation that would drop the WRONG row |
| T-rtc-02 | Repudiation (unauditable failure) | `drop_occluded_from_sumstats` counts | mitigate | T2: `n_unparseable`/`n_truncated` in `counts.json` + a hard raise at 100% unparsed, so "parsed nothing" cannot masquerade as "found nothing" |
| T-rtc-03 | Spoofing (a false provenance claim) | `PROVENANCE_STAGE_A_MANIFEST` stamp | mitigate | T3: refuse the stamp when the rollup does not cover every excludelist region; `--allow-partial-manifest` makes the incompleteness explicit and reported |
| T-rtc-04 | Denial of correctness (a guard that cannot fire) | `enrich_occlusion_manifest` total-miss guard | mitigate | T2: guard on scan SUBSTANCE via a threaded `scan_stats`, preserving the liftable-scoping decision at `:375-383` |
| T-rtc-05 | Information disclosure | catalog columns | accept | Pre-existing egress test `test_catalog_columns_are_egress_clean` re-runs the Stage-A token scan over the catalog header; every column added here is a coordinate/aggregate count, nothing per-person |
| T-rtc-06 | Elevation (an executor edits a pinned test to force green) | `tests/m3` | mitigate | Explicit STOP-and-surface rule in `<hard_constraints>` + a `git diff --stat` verify on the four frozen files |
</threat_model>

<verification>
1. `git diff --stat -- src/snakemake/rules/finemap.smk src/python/plink_ld_to_npz.py
   src/python/condition_ld_matrix.py src/scripts/ld_npz_to_rds.R` -> **EMPTY**.
2. Full `tests/m3` -> **>= 444 passed, 0 failed** (baseline 444/31/0).
3. `measure_present_rate_kn.json` -> `7 / 9` for rs182965575.
4. `load_expected_region_ids('config/ld_regions.tsv')` -> `276`.
5. No `NaN->0` anywhere; nothing imports `condition_ld_matrix`.
6. Staging used explicit paths only — no `git add -A` / `git add .`.
</verification>

<success_criteria>
- All four blast-radius defects (D-04b-01, HIGH-4, HIGH-0, BLOCKER-4) closed with a
  failing-test-FIRST regression for each, and no existing test edited to force green.
- LOW-1 is VISIBLE (9 files / 8 traits reported) with the pre-registered FILE-based
  denominator untouched; the denominator fork is logged to `deferred-items.md`.
- The `(chr,pos)` key exists in exactly ONE place; all three former implementations
  delegate to it and are proven byte-compatible by a parametrized test.
- The measured k/n for rs182965575 is 7 of 9 and is committed as an auditable artifact.
- `tests/m3` >= 444 passed / 0 failed; frozen contracts at 0-line diff; `$0`, NC State
  only, no perimeter contact.
</success_criteria>

<output>
After completion, create
`.planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/260804-rtc-SUMMARY.md`
recording: the four defects closed, the measured k/n (with the before/after), the LOW-1
deferral, any STOP-and-surface decision raised, the final `tests/m3` line, and the
frozen-file 0-diff confirmation.
</output>
