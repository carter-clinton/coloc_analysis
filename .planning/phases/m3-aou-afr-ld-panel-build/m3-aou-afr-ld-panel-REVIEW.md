---
phase: m3-aou-afr-ld-panel-build
reviewed: 2026-04-30T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - src/python/aou_ld_panel.py
  - src/python/build_ld_region_manifest.py
  - src/python/ld_panel.py
  - src/python/select_ld_regions_dev.py
  - src/python/bm_to_npz.py
  - src/scripts/ld_npz_to_rds.R
  - src/snakemake/rules/m3_ingest_aou_ld.smk
  - src/snakemake/rules/m3_convert_npz_rds.smk
  - src/snakemake/rules/finemap.smk
  - Snakefile
findings:
  critical: 4
  warning: 9
  info: 7
  total: 20
status: issues_found
---

# Phase m3-aou-afr-ld-panel-build: Code Review Report

**Reviewed:** 2026-04-30
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the M3 AoU AFR LD panel build pipeline in mid-flight (Wave 0/1 done, Wave 2 partial, Waves 3-5 pending). The code is generally well-documented, with thoughtful provenance tracking, defensive guards, and clear separation of concerns between Hail-side compute (`aou_ld_panel.py`, `bm_to_npz.py`) and NCSU-side conversion (`ld_npz_to_rds.R`).

However, the review surfaced four Critical issues that will break Carter's imminent dev-fire and bootstrap conversion if not fixed before the AoU mirror, plus nine Warnings that warrant attention before Wave 4 production.

The most consequential finding is **CR-001**: the `finemap.smk` resolver call passes `wildcards.region` (a `region_safe` slug like `FTO_16q12`) into `resolve_ld_path()`, but the AoU panel chain head (`AFR_aou/{region_id}.rds`) expects an `m2_region_NNNNN` ID. Both `{region_id}` and `{region_safe}` placeholders are filled with the same value (the region_safe slug), so the resolver will look for `data/processed/ld_reference/AFR_aou/FTO_16q12.rds` and never find the actual `m2_region_00067.rds` files that `build_ld_rds_aou_afr` produces. This silently degrades the resolver to the 1kg fallback for every region — invisible to dry-run, only catchable at runtime when AoU panels are expected to be active.

**CR-002** is a per-region row-order alignment hazard in `aou_ld_panel.compute_region_ld()`: `variant_ids` and `rsids_raw` are built from two separate `aggregate_rows()` calls, which Hail does not guarantee will return identically-ordered rows, and the row order is not pinned to match the BlockMatrix `ld_bm` row order either.

**CR-003** is a Path A.3 sidecar emission gap: the AoU driver only writes variant_ids/rsids sidecar TSVs in the `_save_npz` paths (A.1/A.2). Path A.3 writes the BlockMatrix to bucket but **never emits** the variant_ids.tsv / rsids.tsv that `bm_to_npz.py` requires as input.

**CR-004** is a liftover-failure handling bug in `ld_npz_to_rds.R`: when a chr:pos:ref:alt liftover fails, the variant is dropped from the matrix — but if the original ID was an rsid (build-agnostic), it passes through, and the matrix shape may diverge from what the snp_ids vector promises if the npz emitted `nzchar(rsids)` rsids that actually correspond to dropped chr:pos rows. The vapply preserves length, so this is currently safe — but the logic only preserves correctness because rsids from AoU are always coupled to the variant_id (both are dropped together when the variant is absent). Still, the pyliftover walks every variant including rsids, which then return their own rsid back — fine, but the dimnames assignment downstream becomes a strict-mode trap if any rsid happens to start with non-`rs[0-9]+` characters.

## Critical Issues

### CR-001: resolver receives region_safe slug but AoU chain expects region_id

**File:** `src/snakemake/rules/finemap.smk:95-101`, `src/python/ld_panel.py:63`, `config/pipeline.yaml:209,213`

**Issue:** `run_finemap.input.ld_matrix` calls `resolve_ld_path(wildcards.region, wildcards.ancestry, config)`. In this pipeline, `wildcards.region` is the **region_safe** slug (e.g., `FTO_16q12`, `APOE_19q13`) — see `Snakefile:84` (`{region_safe}.json`) and `finemap.smk:123` (`region_id=lambda w: REGION_SAFE_TO_ID[w.region]` confirms `wildcards.region` *is* the safe slug, with `REGION_SAFE_TO_ID` translating to the original ID).

`resolve_ld_path()` at `ld_panel.py:63` does `entry["path"].format(region_id=region_id, region_safe=region_id)` — both placeholders get filled with the same value, the safe slug. The AoU chain head in `pipeline.yaml:209/213` is `data/processed/ld_reference/AFR_aou/{region_id}.rds`. With `region_id=FTO_16q12`, this resolves to `data/processed/ld_reference/AFR_aou/FTO_16q12.rds`, but the `build_ld_rds_aou_afr` rule (`m3_convert_npz_rds.smk:99`) emits `data/processed/ld_reference/AFR_aou/m2_region_NNNNN.rds`. The resolver will never find the AoU panel and silently falls through to the 1kg/HGDP fallback for every Track A region.

**Impact:** Critical — once Wave 4 lands AoU panels, every fine-mapping run for the 11 Track A overlap regions will continue using 1kg LD instead of the new AoU panel, with no error message. This violates the entire premise of the AFR_aou supersede chain (D-M3-05) and breaks the rigor-over-speed framing the manuscript depends on. Worst case: silent wrong-LD use in published results.

**Fix:** Use the `REGION_SAFE_TO_ID` mapping (already present in Snakefile.py) when calling the resolver, and fix the resolver to substitute the two placeholders independently:

```python
# In finemap.smk
ld_matrix=lambda wildcards: str(
    resolve_ld_path(
        region_id=REGION_SAFE_TO_ID[wildcards.region],   # m2_region_00067
        region_safe=wildcards.region,                    # FTO_16q12
        ancestry=wildcards.ancestry,
        config=config,
    )
),

# In ld_panel.py
def resolve_ld_path(region_id: str, region_safe: str, ancestry: str, config: dict) -> Path:
    ...
    for entry in chain:
        path_str = entry["path"].format(region_id=region_id, region_safe=region_safe)
        ...
```

Add a regression pytest that asserts `AFR_aou` resolves to an `m2_region_*.rds` path while `EUR_1kg` resolves to a `FTO_16q12.rds` path for the same region.

---

### CR-002: rsids/variant_ids row-order may diverge from BlockMatrix row order

**File:** `src/python/aou_ld_panel.py:269-284`

**Issue:** Inside `compute_region_ld`:

```python
ld_bm = hl.ld_matrix(mt_r.GT.n_alt_alleles(), mt_r.locus, radius=radius_bp)
variant_ids = mt_r.aggregate_rows(hl.agg.collect(...))   # call #1
rsids_raw = mt_r.aggregate_rows(hl.agg.collect(...))     # call #2
```

Three independent traversals of `mt_r` are made: one to compute `ld_bm`, two to collect IDs. Hail does not guarantee that `aggregate_rows` returns rows in the same physical order as `hl.ld_matrix`'s row indexing — and even between the two `aggregate_rows` calls, while typically deterministic, the contract is "no row order guarantee" unless the table is keyed and the ordering is explicit. Rows of `ld_bm` are ordered by **locus** (the second arg to `hl.ld_matrix`), but `aggregate_rows` ordering is determined by the MT key (locus, alleles), which generally aligns with locus order — but the alignment is implicit, not enforced.

If row orderings diverge, the .npz emits LD matrix rows that do not correspond to the variant_ids/rsids vectors the R converter assigns as dimnames. The downstream fine-mapping consumer would receive a corrupt LD matrix where every entry's variant label is wrong.

**Impact:** Critical — silent data corruption. The dev-fire's 4-check validation gate in Wave 2 would not necessarily catch this (LD matrix sanity checks usually look at the matrix shape and density, not at every label).

**Fix:** Materialize variant_ids + rsids in the same row-ordered traversal that produces ld_bm, by collecting them on the same rows() call against `mt_r.rows()` rather than `aggregate_rows`:

```python
rows_ht = mt_r.rows().select('rsid' if 'rsid' in mt_r.row else 'locus', 'alleles', 'locus')
rows_df = rows_ht.to_pandas()  # or .collect() for hail Struct list
variant_ids = [f"{r.locus}:{r.alleles[0]}:{r.alleles[1]}" for r in rows_df.itertuples()]
rsids = [getattr(r, 'rsid', '') or '' for r in rows_df.itertuples()]
```

Or collect both fields in a single `aggregate_rows`:

```python
aligned = mt_r.aggregate_rows(hl.agg.collect(hl.struct(
    vid=hl.str(mt_r.locus) + ":" + mt_r.alleles[0] + ":" + mt_r.alleles[1],
    rsid=hl.coalesce(mt_r.rsid, hl.str("")) if "rsid" in mt_r.row else hl.str(""),
)))
variant_ids = [a.vid for a in aligned]
rsids = [a.rsid for a in aligned]
```

Add a pytest assertion that for the synthetic MT, the .npz's `ld[i,i] == 1.0` (self-correlation diagonal) — this catches gross misalignment.

---

### CR-003: Path A.3 BlockMatrix write does not emit variant_ids/rsids sidecar TSVs

**File:** `src/python/aou_ld_panel.py:299-310`

**Issue:** Path A.3 (large/xlarge regions; HLA + 8p23 in dev-10, 36 regions in production) only writes the BlockMatrix:

```python
ld_bm.write(bm_uri, overwrite=True)
out_uri = bm_uri
```

But `bm_to_npz.py:45-67` requires `variant_ids_tsv` and `rsids_tsv` as inputs:

```bash
python src/python/bm_to_npz.py \
    --bm-dir       .../m2_region_00120.bm \
    --variant-ids  .../m2_region_00120.variant_ids.tsv \
    --rsids        .../m2_region_00120.rsids.tsv \
    --out-npz      .../m2_region_00120.npz
```

The driver collects `variant_ids` and `rsids` (lines 275-284) for ALL paths, but only writes them to .npz inside `_save_npz`. For Path A.3, those vectors are computed and then dropped on the floor. Carter's bootstrap conversion of the dev-10 .npz files plus the Wave 3 production conversion will fail at the `bm_to_npz.py` step with `FileNotFoundError: sidecar TSV missing`.

**Impact:** Critical — blocks Carter's dev-fire conversion of the HLA + 8p23 stress regions. Dev-10 has exactly 2 Path-A.3 regions, both of which will fail conversion until this is fixed.

**Fix:** Emit the sidecar TSVs alongside the BlockMatrix write in Path A.3:

```python
else:
    path_a = "A.3"
    if out_bucket is None:
        local_path = (out_local_dir or Path("/tmp")) / "bm" / f"{rid}.bm"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        ld_bm.write(str(local_path), overwrite=True)
        # Sidecar TSVs (matches bm_to_npz.py expected input)
        sidecar_dir = local_path.parent
        np.savetxt(sidecar_dir / f"{rid}.variant_ids.tsv", np.array(variant_ids), fmt="%s")
        np.savetxt(sidecar_dir / f"{rid}.rsids.tsv", np.array(rsids), fmt="%s")
        out_uri = str(local_path)
    else:
        bm_uri = f"{out_bucket}/bm/{rid}.bm"
        ld_bm.write(bm_uri, overwrite=True)
        # Sidecar TSVs to bucket
        for sidecar_name, payload in [("variant_ids.tsv", variant_ids), ("rsids.tsv", rsids)]:
            local_tmp = Path("/tmp") / f"{rid}.{sidecar_name}"
            np.savetxt(local_tmp, np.array(payload), fmt="%s")
            # use _upload_to_gcs helper or duplicate the upload block from _save_npz
            ...
        out_uri = bm_uri
```

Refactor the GCS upload code in `_save_npz` into a helper so it can be reused for sidecar uploads. Add a Wave 2 dev-fire validation check that the bm/ directory has exactly N×3 entries (`.bm/`, `.variant_ids.tsv`, `.rsids.tsv`) per Path A.3 region.

---

### CR-004: ingest rule's manifest filter compares int vs string fragilely; X chr unreachable

**File:** `src/snakemake/rules/m3_ingest_aou_ld.smk:148-155, 119-122, 188-195`

**Issue:** Two related problems:

(a) `chr_int = int(wildcards.chr) if wildcards.chr.isdigit() else wildcards.chr`, then filtered as `manifest["chr"] == chr_int`. The build_ld_region_manifest emits `chr_int_str` (a string post-`replace("chr","")`) in the TSV. When pandas reads the TSV, it auto-infers types. If all rows are autosomes with numeric strings, pandas infers int and the comparison works. But **the X-chromosome wildcard branch** (`chr=r"[0-9]+|X"`) feeds string `"X"` into the filter, while pandas will still type column as int (X rows are excluded from the M2 union per D-M2-09). The filter would silently return zero rows, raising `ValueError: manifest has no rows for ... chr X`. Carter would interpret this as "X bundle not provided" rather than "X is not in scope."

(b) The aggregate target `m3_ingest_aou_export_arrives_all` (lines 188-195) only iterates `chr=[str(i) for i in range(1, 23)]` — autosomes only. But the per-rule wildcard constraint admits `X`. So if Carter hand-runs the rule with `chr=X`, it will fail at the manifest filter with a confusing message rather than at wildcard expansion. The two definitions disagree on scope.

**Impact:** Critical for Carter's dispatch UX — confusing error messages at the dev-fire flag-stamping step. Will block the dev-10 ingest workflow if Carter runs the ingest target manually with chr=X, and will fail silently (no flag stamped, no error) for any chromosome-ancestry combination missing from the manifest.

**Fix:**

1. Drop `X` from the wildcard constraint to match the M2 scope:
   ```python
   wildcard_constraints:
       ancestry=r"AFR|EUR",
       chr=r"[0-9]+",
   ```

2. Coerce the comparison to string on both sides for safety:
   ```python
   manifest["chr"] = manifest["chr"].astype(str)
   sub = manifest[
       (manifest["chr"] == str(wildcards.chr))
       & (manifest["ancestry"] == wildcards.ancestry)
   ]
   ```

3. Improve the empty-set error message to disambiguate scope-out-of-bounds from manifest-not-yet-built:
   ```python
   if not expected_regions:
       raise ValueError(
           f"manifest has no rows for {wildcards.ancestry} chr {wildcards.chr}; "
           f"manifest covers chrs {sorted(manifest['chr'].unique().tolist())}; "
           f"verify the chromosome is within the M2 union scope (autosomes only per D-M2-09)"
       )
   ```

## Warnings

### WR-001: rsids fall-back branch returns a per-row aggregator at parse time only when `rsid` is present

**File:** `src/python/aou_ld_panel.py:280-283`

**Issue:** `rsids_raw = mt_r.aggregate_rows(hl.agg.collect(hl.coalesce(mt_r.rsid, hl.missing(hl.tstr))) if "rsid" in mt_r.row else hl.agg.collect(hl.missing(hl.tstr)))`. This Python conditional is evaluated at driver time; it works correctly. But the `else` branch passes `hl.agg.collect(hl.missing(hl.tstr))` which collects N missing strings — fine, but it's not obvious to a reader that this is per-row vs. one-shot.

**Impact:** Maintainability hazard. AoU production MTs always have `rsid`; the synthetic MT for tests may or may not. If a future contributor refactors and the `else` branch reduces to a length-1 list, alignment with `variant_ids` breaks silently.

**Fix:** Be explicit:
```python
if "rsid" in mt_r.row:
    rsids_raw = mt_r.aggregate_rows(hl.agg.collect(hl.coalesce(mt_r.rsid, hl.str(""))))
else:
    # Match length to variant_ids by collecting an empty string per row
    rsids_raw = ["" for _ in variant_ids]
```

---

### WR-002: `_load_sidecar` returns 0-d array for single-variant TSV

**File:** `src/python/bm_to_npz.py:48`

**Issue:** `np.loadtxt(str(path), dtype=str, delimiter="\t")` returns a 0-d scalar array when the file has exactly one row, and a 1-d array for ≥2 rows. The downstream check `variant_ids.shape[0] != n_rows` raises `IndexError` on 0-d array (no `shape[0]`). Path A.3 should never have a 1-variant region (MIN_VARIANTS_PER_REGION=10), but `bm_to_npz.py` is also conceivably reusable for non-region debugging.

**Impact:** Defensive — current dev-10 won't hit this. Future single-region debugging will produce a confusing `IndexError`.

**Fix:** Use `ndmin=1` to force 1-D:
```python
return np.loadtxt(str(path), dtype=str, delimiter="\t", ndmin=1)
```

---

### WR-003: float32 cast on >10 Mb dense matrix loses precision in symmetry recovery

**File:** `src/python/bm_to_npz.py:96`, `src/scripts/ld_npz_to_rds.R:76`

**Issue:** `bm.to_numpy().astype("float32", copy=False)` then `np.tril(...)`. The R converter then does `tri + t(tri) - diag(diag(tri))` on the float32 matrix. For a 50 Mb region with ~500k variants (HLA, 8p23), the cumulative float32 rounding on the symmetry recovery is ~1e-7 per cell — generally fine for finemapping, but the diagonal subtraction can introduce visible 1e-6 ulp drift on the off-diagonal that depends on float ordering.

The Hail-side `compute_region_ld` already casts to float32 in `_save_npz`. Path A.3 round-trips through bm_to_npz which double-casts.

**Impact:** Subtle. SuSiE-RSS is generally tolerant of 1e-6 noise on LD entries, but the ld_npz_to_rds.R does not check Hermitian property after the recovery — if cumulative float32 drift makes `tri + t(tri)` non-symmetric, the downstream `dimnames(tri)` and any Cholesky solver in coloc/SuSiE may emit warnings.

**Fix:** Either preserve float64 through the conversion (~doubles RAM cost, but acceptable on NCSU GPFS head with 256+ GB), or explicitly enforce symmetry post-recovery:

```r
# In ld_npz_to_rds.R after symmetry recovery
if (!isSymmetric(tri)) tri <- tri + t(tri) - diag(diag(tri))
# Force exact symmetry to suppress float32 drift
tri <- (tri + t(tri)) / 2
```

Document the precision decision (float32 vs float64) in AOU-LD-PIPELINE.md.

---

### WR-004: `_load_region_to_chr_index` reads manifest at DAG construction time but silently no-ops if missing

**File:** `src/snakemake/rules/m3_ingest_aou_ld.smk:212-239`

**Issue:** `_load_region_to_chr_index()` swallows all exceptions with `except Exception: return`, and returns `None` from `_region_chr` if the manifest is missing or malformed. The flag input function then formats with `_region_chr(...) or "UNKNOWN"`, producing a non-existent flag path `aou_export_complete.AFR.UNKNOWN`. Snakemake will report "MissingInputException" at apply time but not at dry-run time.

**Impact:** Confusing failure mode. If Carter forgets to run Wave 0 manifest build before invoking the ingest rule, the error message is "missing input file: .aou_export_complete.AFR.UNKNOWN" rather than "manifest not built; run M3 Wave 0 first".

**Fix:** Raise a workflow-time error from `_region_chr` if the manifest is missing:

```python
def _region_chr(region_id: str) -> str | None:
    _load_region_to_chr_index()
    if not _REGION_TO_CHR:
        raise WorkflowError(
            f"M3 region manifest is empty or missing at {LD_REGIONS_MANIFEST}; "
            f"run `python src/python/build_ld_region_manifest.py ...` (Wave 0) first."
        )
    chrom = _REGION_TO_CHR.get(region_id)
    if chrom is None:
        raise WorkflowError(f"region_id {region_id} not in manifest")
    return chrom
```

---

### WR-005: `m3_aou_npz_arrives` rule has output without producing it

**File:** `src/snakemake/rules/m3_ingest_aou_ld.smk:262-299`

**Issue:** The rule declares `output: npz=...` but its shell block only `touch`es the file if it already exists, and `exit 1` otherwise. This is a Snakemake anti-pattern: a rule that "produces" its output by checking it. If the .npz is missing, Snakemake will retry the rule (since the output didn't materialize), producing the same error in a loop until the retry budget is exhausted.

A dry-run will resolve the DAG cleanly, but `--rerun-triggers mtime` could mark this rule's output as out-of-date and re-fire it, producing confusing "manual gsutil cp" errors during what looks like a routine pipeline run.

**Impact:** UX hazard during Wave 4 production. Carter could see the rule fire every time the M2 manifest is updated even though the .npz files are present.

**Fix:** Either (a) make this a checkpoint that consumes `output: touch(...)` of a flag rather than the .npz itself, or (b) change to `localrule:` and only touch when the file is present:

```python
localrule: m3_aou_npz_arrives
rule m3_aou_npz_arrives:
    input:
        flag=...,
        npz=os.path.join(LD_INTERIM, "{ancestry}_aou", "{region_id}.npz"),
    output:
        sentinel=os.path.join(LD_INTERIM, "{ancestry}_aou", ".{region_id}.npz.sentinel"),
    shell:
        r"""touch {output.sentinel}"""
```

Then have `build_ld_rds_aou_afr/eur` depend on the sentinel, not the .npz directly. This makes the contract "the npz is here, certified by the sentinel" rather than "the rule produces the npz".

---

### WR-006: liftover `_find_mappable` has off-by-one accounting on `walked`

**File:** `src/python/build_ld_region_manifest.py:140-151`

**Issue:** The walked counter increments by `step_size_bp` regardless of direction; `probe += direction * step_size_bp`. The check `if probe < 0: break` only handles negative-position underflow but not chromosome-end overflow. For chr1 with 248 Mb length, walking outward (direction=-1 from start_probe near 0) will hit `probe < 0` correctly, but walking inward on a 248-Mb region toward the centromere may step past valid positions without finding hits because the walking step (1 kb) is small relative to centromeric gaps (~3 Mb).

**Impact:** The `max_step_bp=1_000_000` cap mitigates this — after 1 Mb of walking, the function gives up. So the worst case is a "failed liftover" status rather than corruption. But the M2 union has wide regions whose endpoints often land in centromeres > 1 Mb, and these will be flagged as "FAILED" rather than recovered.

**Fix:** Increase `max_step_bp` to 5 Mb for chrosomome boundaries and add chromosome-length awareness; or document that any region with > 1 Mb of unmappable territory at an endpoint is a hard liftover fail.

---

### WR-007: ANCESTRY_VALUES rejects EUR_AOU/AFR_AOU but accepts MID/SAS

**File:** `src/python/aou_ld_panel.py:58, 158`

**Issue:** `ANCESTRY_VALUES = {"afr", "amr", "eas", "eur", "sas", "mid", "oth"}`. The CLI restricts `--ancestry` to `["afr", "eur"]` (line 364). But `load_qc_cohort` accepts any of the seven labels and would happily run a `mid` or `oth` cohort with no error, even though M2 manifest only emits AFR/EUR rows (line 36-37 of `build_ld_region_manifest.py`).

**Impact:** A future contributor (or a manual Workbench session) could invoke `load_qc_cohort(..., ancestry="amr")` against a manifest that has no AMR rows — the regions list would be empty, and the QC chain would still run on the entire AMR cohort and waste cluster-hours producing a checkpoint nobody can use.

**Fix:** Tighten the validation:
```python
SUPPORTED_ANCESTRIES = {"afr", "eur"}  # M3 manifest scope per D-M3-02
if ancestry not in SUPPORTED_ANCESTRIES:
    raise ValueError(
        f"ancestry={ancestry!r} not supported in M3; manifest emits {SUPPORTED_ANCESTRIES}. "
        f"AoU pred values {ANCESTRY_VALUES} are documented but routing only AFR/EUR."
    )
```

---

### WR-008: ld_panel resolver does not handle `pin: AFR: AFR_aou` skipping the AoU panel availability check

**File:** `src/python/ld_panel.py:56-71`

**Issue:** When `pin` is set, `chain = [c for c in chain if c["source"] == pin]` reduces the chain to a single entry. Then the `for entry in chain` loop tries that one path. If it doesn't exist, the outer `raise FileNotFoundError("No LD panel found ...")` fires — but the `strict_aou_only` branch inside the loop is also active. With pin=AFR_aou and the panel missing:

- `path.exists()` → False
- `panel_cfg.get("strict_aou_only", False)` → False (default)
- loop ends
- Raises `FileNotFoundError("No LD panel found for ...")`

This works, but the error message is generic. If `strict_aou_only=True` and `pin=AFR_aou`, the strict branch fires correctly. If `strict_aou_only=True` and `pin=AFR_1kg` (operator wants to force 1kg), the strict-mode check triggers on the `_aou` suffix — but with pin=AFR_1kg, the chain has no `_aou` entries, so the strict check never fires. Inconsistent semantics.

**Impact:** Confusing error semantics at manuscript-freeze time when operators flip strict mode + pin combinations.

**Fix:** Document the precedence (pin > strict_aou_only > fallback) at the function docstring; add a pytest matrix that exercises all four (pin × strict) combinations against existing/missing panels and asserts the expected error class.

---

### WR-009: Snakefile m3 includes are unconditional but config block is gated

**File:** `Snakefile:118-122`

**Issue:** `m3_ingest_aou_ld.smk` and `m3_convert_npz_rds.smk` are included unconditionally, but `pipeline.yaml` `ld_panel:` section is only useful when `enable_ld_pipeline: true` (line 198) AND when the AoU mirror has been completed. If a downstream user clones the repo and runs `snakemake -n` without ever building the manifest, the m3 ingest rule's `_load_region_to_chr_index` will silently return empty (per WR-004), and the rule will not be triggered unless explicitly named.

But if the user runs `snakemake all` and `LD_TARGETS` is empty (because `ENABLE_LD: false`), the m3 rules are still parsed and active in the DAG. A user accidentally invoking `snakemake .aou_export_complete.AFR.16` would get the WR-004 cascade.

**Impact:** Cleaner separation between Track A (legacy 1kg LD) and M3 (AoU LD) at workflow include time would reduce DAG-pollution surface.

**Fix:** Gate the m3 includes on a config flag analogous to `enable_ld_pipeline`:
```python
ENABLE_M3_AOU_LD = config.get("enable_m3_aou_ld", False)
if ENABLE_M3_AOU_LD:
    include: "src/snakemake/rules/m3_ingest_aou_ld.smk"
    include: "src/snakemake/rules/m3_convert_npz_rds.smk"
```

This keeps Track A workflows fully decoupled until M3 is ready to dispatch.

## Info

### IR-001: `"config" in dir()` guard at module-level is fragile

**File:** `src/snakemake/rules/m3_ingest_aou_ld.smk:79-81`

**Issue:** The expression `(config.get(...) if "config" in dir() else "config/ld_regions.tsv")` uses `dir()` (no args) at module-level scope. Snakemake injects `config` as a global before parsing the include, so `dir()` *should* contain `config` — but this depends on Snakemake's include semantics and is unusual. The standard pattern is `try: config.get(...) except NameError: ...`.

**Fix:** Match the pattern already used at lines 62-67 / 69-72:
```python
try:
    LD_REGIONS_MANIFEST_REL = config.get("ld_regions_manifest", "config/ld_regions.tsv")  # type: ignore[name-defined]
except NameError:
    LD_REGIONS_MANIFEST_REL = "config/ld_regions.tsv"
LD_REGIONS_MANIFEST = str(_M3_PROJECT_ROOT / Path(LD_REGIONS_MANIFEST_REL))
```

---

### IR-002: relateds_table KING ≥ 0.0442 actually loads `relatedness_flagged_samples.tsv`, not `relatedness.tsv`

**File:** `src/python/aou_ld_panel.py:66-67, 182`

**Issue:** Two paths defined: `RELATED_SAMPLES_PATH` (the flagged-samples list) and `RELATEDNESS_FULL_PATH` (the full pairwise table). Only the former is used. The full pairwise table would be needed if Carter ever wanted to apply a stricter (e.g., 2nd-degree, KING ≥ 0.0884) cutoff — currently `RELATEDNESS_FULL_PATH` is dead code.

**Fix:** Either use it (apply local degree-of-relatedness threshold) or remove it. The conservative choice for rigor-over-speed is to use it for a sensitivity analysis at the manuscript stage.

---

### IR-003: `aggregate_rows` materialization order is the same call site as the BlockMatrix

**File:** `src/python/aou_ld_panel.py:269-285`

**Issue:** Related to CR-002 — even if the order *happens* to align in current Hail (0.2.x), this is implicit and fragile. Add an assertion:

```python
assert len(variant_ids) == n_var, f"variant_ids count {len(variant_ids)} != n_var {n_var}"
assert len(rsids) == n_var
```

---

### IR-004: `derive_source_trait_and_lead` lead_variant always "NA"

**File:** `src/python/build_ld_region_manifest.py:95-124`

**Issue:** Function signature returns `(source_trait, lead_variant)` but `lead_variant` is unconditionally `"NA"` in every code path. The function could be simplified to return only `source_trait`, with `lead_variant` set at the manifest-row construction layer.

**Fix:** Drop the second return value or document that lead_variant is intentionally a Wave 1 fill-in:
```python
def derive_source_trait(prov: dict, ancestry: str) -> str:
    """Return source_trait for a region × ancestry cell.

    lead_variant is intentionally NA at manifest-build time; resolved at
    AoU-side cohort definition (Wave 1, D-M2-09).
    """
```

---

### IR-005: `select_dev_rows` HLA stress pick can collide with AFR_KNOWN_REGIONS

**File:** `src/python/select_ld_regions_dev.py:110-117`

**Issue:** The 5 AFR-known regions (FTO, SORT1, SH2B3, APOE, LDLR) and the 2 stress targets (HLA chr6, 8p23 chr8) are on different chromosomes (16, 1, 12, 19, 11 vs. 6, 8) — so collision is impossible by current selection. The `drop_duplicates` is dead code in current scope, but a defensive guard. Comment says "an AFR-known + HLA-stress could collide — unlikely here, but guard." The guard is fine to keep, but the dev-10 size assertion (10 rows) is worth adding:

```python
expected = len(AFR_KNOWN_REGIONS) + len(EUR_OVERLAP_REGIONS) + len(HLA_STRESS_TARGETS)
assert len(dev_df) == expected, f"dev subset size mismatch: got {len(dev_df)}, expected {expected}"
```

This catches accidental misconfiguration of the constant tuples.

---

### IR-006: `compute_radius_bp` does not document interaction with `radius` arg semantics in hl.ld_matrix

**File:** `src/python/aou_ld_panel.py:269-273`, `src/python/build_ld_region_manifest.py:231-235`

**Issue:** `hl.ld_matrix(..., radius=radius_bp)` computes pairwise LD only between variants within `radius_bp` of each other. The manifest's `radius_bp = span + 500_000` ensures the entire region is covered (every variant is within radius of every other). For a 50-Mb region (HLA), `radius_bp = 50.5 Mb`, which means hl.ld_matrix computes the FULL pairwise LD across HLA — exactly Path A.3's worst case. The radius is not actually doing any pruning; it's a no-op cap. This matches RESEARCH Q2 intent but is worth a docstring comment.

**Fix:** Add a comment in `compute_radius_bp`:
```python
def compute_radius_bp(start_b38: int, end_b38: int) -> int:
    """Per-region radius (RESEARCH Q2). Capped at 50 Mb.

    Note: this is the `radius` kwarg to hl.ld_matrix. Setting it to
    `span + 500kb` ensures every variant pair within the region is computed
    (no inadvertent pruning). For 50Mb regions, the cap kicks in but this
    still covers the full region's interior.
    """
```

---

### IR-007: ld_npz_to_rds.R rsid pass-through preserves 'chr'-stripped synthetic IDs that match `^rs[0-9]+$` by accident

**File:** `src/scripts/ld_npz_to_rds.R:101-114`

**Issue:** After `sub("^chr", "", ...)`, any variant_id that is already an rsid (rs12345) bypasses the strip. The liftover function checks `grepl("^rs[0-9]+$", vid)` — fine. But if the AoU MT emits an `rsid` field that mixes rsids and dbSNP merge-ids (rsids that have been retired and merged, e.g., `rs12345 -> rs67890`), the pass-through doesn't catch the merge. Not in current scope, but worth flagging for Wave 4 production validation.

**Fix:** Add an audit count of pass-through rsids vs. liftover-converted positions in the provenance manifest:

```r
n_rsid_passthrough <- sum(grepl("^rs[0-9]+$", snp_ids_grch37))
provenance$n_rsid_passthrough <- n_rsid_passthrough
```

This makes the rsid/synthetic-id ratio audit-able from the .rds.

---

_Reviewed: 2026-04-30_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
