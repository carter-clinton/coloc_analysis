# quick 260701-qcy: Drop monomorphic (MAC=0-in-AFR) variants from the native-plink LD panel — Research

**Researched:** 2026-07-01
**Domain:** plink1.9 `--r square` LD export + variant filtering + .ld.bin↔.bim alignment (Python driver)
**Confidence:** HIGH (plink semantics verified against cog-genomics.org/plink/1.9 order-of-operations + code read)

## User Constraints (from HANDOFF.json 2026-07-01 correction block)

### Locked Decisions
- **Root cause is CONFIRMED — do NOT re-investigate.** ~11 monomorphic (MAC=0-in-AFR) variants in region 1's window make plink emit NaN LD entries; `NaN != NaN` breaks `read_square_bin`'s `_is_symmetric_blocked` check. Proven by running `read_square_bin` directly on the intact 42 GB region-1 `.ld.bin` (deterministic RAISE) + a pinpoint diagnostic (12 NaN entries across 11 clustered rows, diagonals still 1.0). SYSTEMIC across the 276 windows.
- **DECISION = DROP MAC=0 variants from the LD computation.** Leading mechanism = add `--mac 1` (+ `--write-snplist`) at the plink step and thread the retained variant list through the converter so `.ld.bin` rows, the window `.bim`, `n_var`, and the `.npz` variant list all align to the SAME retained set.
- **VM stays n1-standard-32 (NO respec).** Both OOM fixes + chr-prefix fix already proven-good.
- The retry-on-zero guard (`27af416`) is harmless but does NOT fix this and is untouched by this work.
- **Rigor over speed (CLAUDE.md):** in any gray area, prefer the more robust / reviewer-defensible option.

### Claude's Discretion
- Exact threading approach (snplist-driven window `.bim` rebuild vs. re-derive retained set another way).
- Whether to also add `--nonfounders` (see Pitfall 3 — recommendation: NOT needed, but cheap insurance).
- Per-region `--mac1+snplist` **vs.** one-time bfile pre-filter — this research **recommends per-region** (see Recommendation).

### Deferred / OUT OF SCOPE
- The pre-existing "`.afreq` sidecar is never produced in production" issue (`build_plink_ld_command` emits no `--freq`, so `af_arg` is always `None` → all-NaN AF). Real, but a SEPARATE concern; do not fix it here unless the plan explicitly scopes it. (Noted in Q5/Q7 below.)
- m3-04 replan.

## Summary

The fix is small and well-supported by plink1.9's documented order of operations. plink1.9 applies filters in this order: **chr/pos window (`--chr/--from-bp/--to-bp`) → minor-allele filters (`--maf/--mac`) → `--write-snplist` → LD report (`--r`)** [CITED: cog-genomics.org/plink/1.9/order]. Therefore adding `--mac 1` drops MAC=0 (monomorphic) variants *before* `--r square` runs, so the emitted `.ld.bin` is exactly `(n_retained)²` with no monomorphic rows → **no NaN LD, symmetry check passes.** `--write-snplist` writes exactly the retained variant IDs (those that "pass the filters and inclusion thresholds"), one per line, in filtered `.bim` order — the SAME order as the `.ld.bin` rows [CITED: cog-genomics.org/plink/1.9/data + /order]. That snplist is the linchpin that lets the converter rebuild a retained window `.bim` whose row order == the `.ld.bin` row order.

The current alignment path in `run_native_ld_panel.process_region` derives the window variant set by *re-filtering the cohort `.bim` on `[from_bp,to_bp]`* (`_window_bim_n_var`) — that count is the RAW window count and will now DISAGREE with the `.ld.bin` (which excludes monomorphic vars). The minimal correct change is to **stop deriving the window from the raw `.bim` and instead intersect the raw window with the plink-emitted `.snplist`** so `window_n_var == bin_n_var == len(retained)` and the `.npz` `variant_ids` are the retained set. `read_square_bin` / `load_bim` / the symmetry+diagonal checks in `plink_ld_to_npz.py` are CORRECT and must NOT change.

**Primary recommendation:** Per-region `--mac 1 --write-snplist` at the plink step; thread the emitted `{out_prefix}.snplist` into `process_region` to build the retained window `.bim` (subset the raw window `.bim` to snplist IDs, preserving snplist order) → feed that to `plink_ld_to_npz` with `n_var = len(retained)`. Do NOT do the one-time bfile pre-filter (disk-tight + a re-stage; see Recommendation). TDD: extend `_MockPlink` to honor `--write-snplist` (drop k synthetic "monomorphic" rows, emit `.snplist`, size `.ld.bin` to retained).

## Research Questions — Answers

### Q1. Does `--mac 1` drop ONLY MAC=0 before `--r square`, giving an exactly `n_retained²` `.ld.bin`?
**YES. [CITED: cog-genomics.org/plink/1.9/filter + /order]**
- `--mac` / `--max-mac` "impose lower and upper minor allele count bounds." `--mac 1` = keep variants with **minor allele count ≥ 1**, i.e. exclude MAC=0 (monomorphic) ONLY. It is a *count* threshold, not a frequency threshold — it will NOT touch low-MAF-but-polymorphic variants (any variant seen in ≥1 minor-allele copy across the cohort survives). This is exactly the right knife: drop the ~11 monomorphic-in-AFR variants, keep everything else.
- Order of operations [CITED: /order]: position/`--from`/`--to` filtering happens EARLY; MAF/MAC in "Main variant filters"; LD report (`--r`) "much later." So `--mac 1` executes over the already-windowed variant set and *before* `--r square` → the `.ld.bin` is emitted over exactly the retained set → shape `(n_retained, n_retained)`, `n_var_from_ld_bin = sqrt(bytes/4) = n_retained`.

### Q2. Does `--write-snplist` emit retained IDs in the SAME order as the `.ld.bin` rows?
**YES. [CITED: cog-genomics.org/plink/1.9/data + /order]**
- `--write-snplist` "writes IDs of all variants which pass the filters and inclusion thresholds you've specified" → post-MAC retained set only.
- Order-of-operations places `--write-snplist` AFTER main variant filters and BEFORE the LD report, both consuming the identical filtered variant list in input (`.bim`) order. plink is deterministic in `.bim` order throughout. So `.snplist` line *k* ↔ `.ld.bin` row/col *k*. This is the alignment guarantee the converter needs.
- Format: plain text, ONE variant ID per line, in filtered `.bim` order (well-established `.snplist` format; the exact format page did not render but the `--write-snplist` semantics + deterministic `.bim` ordering are confirmed). [ASSUMED: one-ID-per-line — universally true of `--write-snplist`, but the plan's test should hard-assert it and a fire pre-flight can `head` the real file.]

### Q3. Interaction with `--keep-allele-order` (already used) and `--chr/--from-bp/--to-bp`?
**Composes cleanly. [CITED: /order]**
- `--keep-allele-order` controls A1/A2 assignment (REF/ALT), independent of which variants are *retained*; `--mac` is a keep/drop filter. No conflict. `--keep-allele-order` stays MANDATORY (hardcoded in `build_plink_ld_command`; a test asserts it).
- `--chr/--from-bp/--to-bp` run BEFORE `--mac`, so `--mac` operates only on in-window variants — no cross-window leakage.
- **Gotcha (Pitfall 3):** `--maf/--mac` "Only founders are normally considered" [CITED: /filter]. See Pitfall 3 — with an `hl.export_plink` `.fam` (parents = 0 → all founders) this is a no-op, but document `--nonfounders` as the safe fallback.

### Q4. Minimal change to thread the retained snplist (so `n_var=retained`, the cross-check uses retained, `.npz` == retained)?
Touch `run_native_ld_panel.process_region` (square path) + `build_plink_ld_command`. Do NOT touch `plink_ld_to_npz.py`'s readers/checks.

Current square path (lines ~507–528):
```python
ld_path = Path(f"{out_prefix}.ld.bin")
bin_n_var = _n_var_from_ld_bin(ld_path)                       # = n_retained (after --mac 1)
window_n_var, window_bim = _window_bim_n_var_retry_on_zero(   # RAW window count -> now WRONG (> n_retained)
    bim_path, chrom, from_bp, to_bp, expect_nonzero=(bin_n_var > 0),
)
if bin_n_var != window_n_var:                                 # would RAISE (raw > retained)
    raise ValueError(...)
```
**Minimal fix:** after plink runs, build the retained window `.bim` by **intersecting the raw window `.bim` with the emitted `.snplist`, in snplist order**, and use THAT count as `window_n_var`:
- New helper (reusable, per [[feedback_extract_reusable_utilities]]), e.g. `_retained_window_bim(bim_path, chrom, from_bp, to_bp, snplist_path) -> (n_retained, retained_window_bim_path)`:
  1. read `.snplist` → ordered list of retained SNP IDs (col-2 IDs);
  2. read the raw in-window rows from the cohort `.bim` (reuse the `_chrom_match_key` + `[from_bp,to_bp]` predicate already in `_window_bim_n_var`);
  3. keep only rows whose SNP id ∈ snplist, EMITTED IN SNPLIST ORDER (snplist order == `.ld.bin` order — do not re-sort by bp);
  4. write the retained window `.bim`; return `(len, path)`.
  (In practice raw-window `.bim` order and snplist order are identical `.bim` order, but ordering by the snplist is the defensive/authoritative choice.)
- `window_n_var = n_retained`; the existing `if bin_n_var != window_n_var: raise` line is now a REAL guard that passes (`retained == retained`) and still traps a genuine drift. Keep it byte-identical if possible.
- `n_var = window_n_var = n_retained` flows unchanged into `plink_ld_to_npz(..., bim_path=retained_window_bim, n_var=n_retained)`. `load_bim` reads the retained `.bim` → `variant_ids`/`rsids` are the retained set → `.npz` variant list == retained set. `read_square_bin(ld_path, n_retained)` reshapes exactly; **no monomorphic rows → no NaN → `_is_symmetric_blocked` passes.**
- **Transient-guard interaction:** `_window_bim_n_var_retry_on_zero` guards a *raw*-window zero. With the retained-window rebuild, the transient guard can wrap the raw `.bim` read inside the new helper OR the helper can call the existing retry wrapper for the raw read step, then intersect. Keep the retry semantics; just move the "count that must equal `bin_n_var`" to the retained count. (The plan should decide whether to nest the retry inside `_retained_window_bim` — recommended — so the transient-heal still applies.)
- Add `--mac 1 --write-snplist` in `build_plink_ld_command` for the SQUARE branch (banded path is not in the fire; scope decision — safest to add to both since monomorphic → NaN affects banded `R` too, but the fire only runs square; recommend add to square, note banded).

### Q5. The `.afreq` sidecar after `--mac 1` — re-align needed?
- **In production TODAY: N/A.** `build_plink_ld_command` emits NO `--freq`, so no per-region `.afreq` is produced; `process_region` finds no `{out_prefix}.afreq`, `af_arg = None`, and `plink_ld_to_npz` writes an all-NaN AF (with a WARNING). So there is nothing to re-align. (The `cohort.afreq` in the test fixture is a decoy at the bfile path, not the `{out_prefix}.afreq` the driver looks for.)
- **IF the plan later adds `--freq`** (out of scope here): plink applies `--mac` before `--freq` output too, so a `--freq`-emitted `{out_prefix}.afreq` would ALREADY contain only retained variants, in the same filtered `.bim` order → row-aligned to the retained `.ld.bin`/`.bim` for free. `_load_af_sidecar` asserts `len(af) == n_var`; with retained-everywhere that assertion holds. So `--freq` composes cleanly with `--mac 1` if/when added — but it is NOT required for this fix. [ASSUMED: `--freq` respects `--mac` — consistent with order-of-operations placing frequency reports after filters; confirm before adding `--freq`.]

### Q6. ALTERNATIVE — one-time bfile pre-filter vs. per-region `--mac1+snplist`?
**RECOMMENDATION: per-region `--mac 1 --write-snplist` (the leading mechanism). Do NOT pre-filter the bfile.**

| Axis | Per-region `--mac1 + snplist` (RECOMMENDED) | One-time `plink --mac 1 --make-bed` pre-filter |
|------|---------------------------------------------|-----------------------------------------------|
| Code change | Small, TDD-covered (`build_plink_ld_command` + one helper + threading) | "Zero pipeline code change" claim is FALSE — `bin_n_var` still uses raw-window `.bim`... but the pre-filtered `.bim` IS the retained set, so `_window_bim_n_var` over the filtered bfile == `.ld.bin`. Genuinely near-zero code. |
| Correctness / "monomorphic dropped" semantics | **Per-region MAC** = monomorphic *within each window's variant set* = the exact NaN trigger. Also the reviewer-defensible unit ("no monomorphic variant enters any region's LD"). | Global MAC over the whole cohort = a variant polymorphic somewhere but monomorphic *in a given window* is impossible (MAC is cohort-wide, window-independent), so global == per-region for MAC. Equivalent correctness. |
| **Disk (the real constraint)** | **No new large artifact.** Only tiny per-region `.snplist` (~KB) added to scratch, reclaimed with the rest. | **Tight/blocking.** Loop VM 1TB PD is ~588 GB used (base ~192 + bfile ~354 + region-1 `.ld.bin` ~42). A 2nd ~354 GB `.bed` overflows unless the original bfile is deleted first — but that original is the durable source; deleting adds a re-stage risk, and a mid-filter failure could strand the VM with neither bfile. Violates rigor-over-speed. |
| Provisioning / re-stage risk | None. | Deleting/re-staging the 354 GB bfile is exactly the SPARSE-copy / stat-not-ls hazard already burned ([[reference_aou_analysis_vm_large_bfile_staging]]). Extra failure surface for no correctness gain. |
| Fire disruption | Re-fire the SAME `loop_command` after a `git pull`; VM untouched. | Requires an extra in-perimeter plink `--make-bed` step + disk juggling before the loop can start. |
| Reviewer defensibility | Per-region filter is explicit + logged per region (`n_var` now = polymorphic count); snplist is an auditable artifact. | Filter is a one-off upstream step, less visible in the per-region panel. |

Both are correct (cohort-wide MAC makes the two equivalent), but per-region wins decisively on the disk constraint, provisioning risk, and per-region auditability, at a modest, TDD-able code cost. Per CLAUDE.md rigor-over-speed, choose the option with the smaller blast radius on the live 11-day fire → **per-region.**

### Q7. Panel accounting — where must docstrings/semantics say `n_var` now excludes monomorphic?
- `run_native_ld_panel.process_region` / `_retained_window_bim` docstring: state that `n_var` is the **polymorphic (MAC≥1) in-window variant count** — monomorphic-in-AFR variants are dropped by `--mac 1` before LD, so the LD panel's per-region `n_var` legitimately excludes them.
- `build_plink_ld_command` docstring: note `--mac 1` drops MAC=0 monomorphic variants (prevents plink NaN LD → symmetry-check failure) and `--write-snplist` emits the retained set for downstream alignment.
- The panel TSV `n_var` column semantics (in the module header contract) → "retained polymorphic variant count," not raw window size. Region 1 will now report `n_var ≈ 102,410` (≈102,421 − ~11), not 102,421 — the fire proof-point in HANDOFF should expect the slightly-lower count.
- `plink_ld_to_npz.py` header already says "variant order comes from the cohort `.bim`" — still true (retained `.bim`); no change needed, but the plan may add one line noting the `.bim` fed to it is the retained window subset.

## Don't Hand-Roll

| Problem | Don't build | Use instead |
|---------|-------------|-------------|
| Detecting/removing monomorphic variants from the genotype matrix in Python | A custom MAC counter over `.bed` | plink `--mac 1` (runs before `--r`, over the windowed set) |
| Determining the retained variant set + its order | Re-deriving "which variants plink kept" from AF thresholds | plink `--write-snplist` (authoritative, filtered, `.bim`-ordered) |
| Symmetry / diagonal / NaN checks | New checks | Existing `read_square_bin` + `_is_symmetric_blocked` (already correct; NaN is CAUGHT by them — that's the whole diagnosis) |

## Common Pitfalls

### Pitfall 1: Cross-check still uses the RAW window count → false ValueError on every region
After `--mac 1`, `bin_n_var` (retained) < raw `_window_bim_n_var`. If you add `--mac 1` but leave the cross-check reading the raw window `.bim`, EVERY region now raises `n_var mismatch` and banks 0/276 (a NEW systemic failure). The retained-window rebuild (Q4) is MANDATORY, not optional polish.

### Pitfall 2: Feeding the RAW window `.bim` (or the wrong order) to `plink_ld_to_npz`
`load_bim` maps `.bim` row *k* → `variant_ids[k]` → `.npz` col *k*, and `read_square_bin` reshapes to `n_var²`. If `bim_path` still points at the raw window `.bim` (has the dropped rows) OR is re-sorted by bp instead of snplist order, `n_var` mismatches or the variant labels misalign against the `.ld.bin` columns → silent wrong-variant LD. Build the retained `.bim` in **snplist order** and pass THAT path.

### Pitfall 3: `--mac` only counts FOUNDERS by default
[CITED: cog-genomics.org/plink/1.9/filter] "Only founders are normally considered by these filters." `hl.export_plink` writes a `.fam` with paternal/maternal IDs = 0 (unknown → every sample is a founder), so `--mac 1` counts all ~73,122 AFR samples and the MAC is the true cohort MAC — no adjustment needed. BUT if any `.fam` row ever had nonzero parent IDs, founders-only counting could mis-drop. **Cheap insurance:** add `--nonfounders` alongside `--mac 1` so ALL samples are counted regardless of `.fam` parent columns. Recommend including `--nonfounders` (rigor-over-speed; zero downside for an all-founder cohort). Confirm at fire pre-flight: `awk '$3!=0||$4!=0' afr_cohort.fam | head` should be empty.

### Pitfall 4: Assuming `.snplist` needs a header / has extra columns
`.snplist` is bare IDs, one per line, no header. Parse as `line.strip()` non-empty. (Test should assert format; a fire pre-flight `head afr_cohort.<region>.snplist` confirms.)

### Pitfall 5: Banded path left inconsistent
The fire runs `--mode square` only. Monomorphic → NaN also affects banded `R`, but banded scatters named pairs (so a NaN would land as a NaN entry, different symptom). Scope: add `--mac 1 --write-snplist` to the SQUARE branch; note the banded branch as a follow-up if ever fired. Don't silently change banded behavior without a test.

## Code Examples

Plink argv after the fix (square branch of `build_plink_ld_command`):
```python
cmd = [
    "plink1.9",
    "--bfile", str(bfile_prefix),
    "--keep-allele-order",           # MANDATORY (unchanged)
    "--chr", str(chrom),
    "--from-bp", str(from_bp),
    "--to-bp", str(to_bp),
    "--mac", "1",                    # NEW: drop MAC=0 monomorphic BEFORE --r (no NaN LD)
    "--nonfounders",                 # NEW (insurance): count all samples, not founders-only
    "--write-snplist",               # NEW: retained IDs, .bim order == .ld.bin order
    "--r", "square", "bin4",
    "--out", str(out_prefix),
]
# emits: {out_prefix}.ld.bin  (n_retained^2 float32)  AND  {out_prefix}.snplist
```

TDD — extend `_MockPlink.__call__` (tests/m3/test_run_native_ld_panel.py) to model the drop:
```python
# when "--write-snplist" in cmd:
#   pick k "monomorphic" rows in the window to DROP (e.g. every m-th, or a fixed set)
#   retained = [in-window bim rows not dropped], in bim order
#   write "{out_prefix}.snplist" = "\n".join(r[1] for r in retained) + "\n"   # col-2 SNP ids
#   size the synthetic .ld.bin to len(retained)^2  (NOT the raw window count)
# assert argv contains --mac 1 (mirror the existing --keep-allele-order test)
# assert the produced .npz has variant_ids == retained ids, shape (len(retained),)^2
# add a NaN-injection regression: a mock that, WITHOUT --mac, writes a NaN row ->
#   read_square_bin RAISES (locks the diagnosis); WITH the fix -> passes.
```

## Environment Availability

| Dependency | Required by | Available (NCSU dev) | Notes |
|------------|-------------|----------------------|-------|
| plink1.9 | LD + `--mac`/`--write-snplist` | Not on NCSU node (verified `which plink plink1.9` → none) | plink runs IN-PERIMETER on the loop VM at `gs://…/ld/afr_native_panel/tools/plink1.9`. NCSU only needs the Python driver + tests (subprocess seam monkeypatched — no real plink needed for TDD). |
| pytest / numpy / pandas | tests | Yes (repo test env) | `tests/m3` runs green (309/30 baseline). |

**No blocker for TDD** — the fix + tests land on NCSU with the monkeypatched `_run_plink` seam; the real plink flags are exercised only at the in-perimeter re-fire (region-1-only validation per HANDOFF `do_not`).

## Validation Architecture

### Test framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Test files | `tests/m3/test_run_native_ld_panel.py` (driver + `_MockPlink`), `tests/m3/test_plink_ld_to_npz.py` (reader) |
| Quick run | `pytest tests/m3/test_run_native_ld_panel.py -x` |
| Full suite | `pytest tests/m3` (baseline 309 passed / 30 skipped) |

### Requirements → test map
| Behavior | Test type | Command |
|----------|-----------|---------|
| `build_plink_ld_command` includes `--mac 1` + `--write-snplist` (square) | unit | `pytest tests/m3/test_run_native_ld_panel.py -k mac -x` (NEW) |
| Retained-window `.bim` == snplist set, in snplist order | unit | NEW test via extended `_MockPlink` |
| `n_var`/`.npz` variant list == retained set; `bin_n_var==window_n_var` passes | unit | NEW |
| A monomorphic/NaN `.ld.bin` (no `--mac`) makes `read_square_bin` RAISE (locks diagnosis) | unit (regression) | NEW in `test_plink_ld_to_npz.py` |
| `--keep-allele-order` still on every issued command | unit | existing `test_keep_allele_order_on_every_issued_command` (must still pass) |

### Wave 0 gaps
- Extend `_MockPlink` to honor `--write-snplist` (drop k rows, emit `.snplist`, size `.ld.bin` to retained). This is the enabling fixture change — do it FIRST (failing-first).
- No new framework install needed.

## Sources

### Primary (HIGH)
- cog-genomics.org/plink/1.9/order — order of operations: chr/pos filter → MAF/MAC → write-snplist → LD report.
- cog-genomics.org/plink/1.9/filter — `--mac`/`--max-mac` = minor-allele-COUNT bounds; "only founders normally considered."
- cog-genomics.org/plink/1.9/data — `--write-snplist` writes IDs of variants that "pass the filters and inclusion thresholds."
- Code read: `src/python/run_native_ld_panel.py` (process_region square path, `_window_bim_n_var`, retry guard), `src/python/plink_ld_to_npz.py` (`read_square_bin`, `load_bim`, `_is_symmetric_blocked`), `src/python/aou_ld_panel.py:2854` (`build_plink_ld_command`), `tests/m3/test_run_native_ld_panel.py` (`_MockPlink`).
- `.planning/HANDOFF.json` 2026-07-01 correction block (locked root cause + decision).

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | `.snplist` is bare one-ID-per-line, no header, filtered `.bim` order | Q2 / Pitfall 4 | LOW — universal `--write-snplist` format; test asserts + fire pre-flight `head` confirms. If wrong, parse adjusts trivially. |
| A2 | `hl.export_plink` `.fam` has parents=0 → all founders → `--mac` counts all samples | Q3 / Pitfall 3 | LOW — `--nonfounders` insurance nullifies it; pre-flight `awk` on `.fam` confirms. |
| A3 | `--freq` (if ever added) respects `--mac`, emitting retained-only `.afreq` | Q5 | LOW/none — `.afreq` is not produced in production today; only matters if a future task adds `--freq`. |

## Metadata
**Confidence:** plink flag semantics HIGH (order-of-operations + filter pages verified); threading approach HIGH (code-read). Founders caveat MEDIUM→mitigated by `--nonfounders`.
**Research date:** 2026-07-01. **Valid until:** ~30 days (plink1.9 is frozen; project code is the moving part).
