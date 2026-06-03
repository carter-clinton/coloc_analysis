# AOU-2 / AOU-4 — Track 4 contents-validation paste-in patterns

> **Status:** paste-ready cell snippets. NOT applied to `AOU-2_per_region_ld.ipynb` or `AOU-4_validation.ipynb` at task creation 2026-05-28. Apply at Wave 2 fire time per the directive below.
>
> **Why now:** the m3-W1 Track 4 patches (quick task 260528-jvd) lock D-M3-10 into `m3-CONTEXT.md` — every MT write touchpoint across Waves 1+2+4+5 must be contents-validated, not `_SUCCESS`-only. AOU-2 (Wave 2 per-region LD compute) reads the same cohort MTs that the W1 catastrophe produced, then writes per-region `.npz` files. AOU-4 (validation harness) consumes those `.npz` files. Either step is silently corruptible without inheritance of the Track 4 pattern.
>
> **Why not now:** Carter's directive 2026-05-28 — preserve every committed notebook for AoU tech support / Abby Doyle review (Zendesk #57144). The smoke notebook is a fresh fork; the AOU-2 / AOU-4 paste-ins go live only when Wave 2 fires.

## §1 Why this doc exists

The Track 4 defensive code in `src/python/aou_ld_panel.py` protects:

- `load_qc_cohort()` writes (AOU-1) — via `_assert_checkpoint_nonempty(mt, uri, *, phase)` after every `mt.checkpoint()` and `_validate_checkpoint_populated()` in the auto-resume gate.

Track 4 does NOT protect:

- AOU-2 Cell 4 — reads the AOU-1-emitted cohort MTs from the workspace bucket. If those MTs are empty-but-_SUCCESS-marked (the W1 catastrophe signature), AOU-2 proceeds into the per-region LD loop on empty cohorts and emits empty `.npz` files.
- AOU-2 Cell 6 — the per-region LD compute loop. `compute_region_ld()` returns a status dict; a misclassified status could silently produce stub `.npz` outputs (e.g., zero-byte BlockMatrix writes under Path A.3 OOM).
- AOU-4 Cells 1, 3, 5, 7, 9, 11 — read the `.npz` files. If those are empty or stub-only, the R-side susieR / coloc / LDheatmap calls would either crash unhelpfully or produce silently-wrong outputs.

D-M3-10 mandates we close these gaps. This doc is the paste-in playbook for doing that, ready to apply when Wave 2 is greenlit.

## §2 AOU-2 Cell 4 paste-in — cohort-MT contents validation

**Where to paste:** AOU-2 Cell 4 currently reads:

```python
mt_afr = hl.read_matrix_table(f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_afr_qc.mt")
mt_eur = hl.read_matrix_table(f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_eur_qc.mt")
```

**Paste-in (insert AFTER the two `hl.read_matrix_table` calls):**

```python
# Track 4 D-M3-10 paste-in (260528-l8r): cohort-MT contents validation
# Guards against AOU-1 emitting empty-but-_SUCCESS-marked MTs (the m3-W1
# catastrophe signature). Either MT being empty here means every downstream
# per-region LD computation would silently produce empty .npz outputs.
#
# References: .planning/debug/m3-W1-empty-mt-catastrophe.md
#             .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md D-M3-10
#             [[feedback_aou_success_marker_not_evidence_of_data]]
#             [[feedback_hail_checkpoint_contract_violation]]
from aou_ld_panel import _validate_checkpoint_populated

for cohort_name, mt, uri in [
    ("mt_afr", mt_afr, f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_afr_qc.mt"),
    ("mt_eur", mt_eur, f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_eur_qc.mt"),
]:
    n_cols = mt.count_cols()
    n_rows = mt.count_rows()
    assert n_cols > 0 and n_rows > 0, (
        f"{cohort_name} read returned empty MT: {n_cols} samples x {n_rows} variants. "
        f"Bucket URI: {uri}. The m3-W1 catastrophe signature reproduced — AOU-1 emitted "
        f"an empty-with-_SUCCESS MT. HALT before per-region LD loop fires."
    )
    assert _validate_checkpoint_populated(uri), (
        f"{cohort_name} at {uri} fails _validate_checkpoint_populated despite non-zero "
        f"in-memory count — possibly cached JVM-side IR masking an empty bucket commit. "
        f"HALT and inspect entries/rows/parts/ directly via gsutil."
    )
    print(f"  {cohort_name} validated: {n_cols:,} samples x {n_rows:,} variants at {uri}")
```

**Why both checks (count_* + _validate_checkpoint_populated):** Cell 4 reads the MT from the bucket. The Hail-internal `count_cols()` and `count_rows()` calls could (in theory) be satisfied from JVM-cached IR from prior cells without forcing a fresh bucket read — this is the same pattern that masked the W1 catastrophe in the original notebook. The `_validate_checkpoint_populated()` helper forces a direct gsutil-style bucket-contents check that bypasses any caching, providing belt-and-suspenders coverage.

## §3 AOU-2 Cell 6 paste-in — per-region `.npz` output validation

**Where to paste:** AOU-2 Cell 6 currently runs a per-region loop calling `compute_region_ld(region, mt, ...)` and recording the result. The exact lines vary slightly by region path-branch (A.1 / A.2 / A.3) but the loop structure is:

```python
for _, region in regions.iterrows():
    mt_for_anc = mt_afr if region["ancestry"] == "afr" else mt_eur
    res = compute_region_ld(region, mt_for_anc, out_bucket=OUT_BUCKET_AFR if ... else OUT_BUCKET_EUR, out_local_dir=None)
    results.append(res)
```

**Paste-in (insert AFTER `results.append(res)`):**

```python
    # Track 4 D-M3-10 paste-in (260528-l8r): per-region .npz output validation
    # Guards against compute_region_ld emitting status="ok" with a zero-byte .npz
    # output (e.g., Path A.3 BlockMatrix write that finalized _SUCCESS but produced
    # empty Parquet stubs — same failure class as the cohort-MT catastrophe but at
    # per-region granularity).
    if res["status"] == "ok":
        import numpy as np
        out_uri = res["out"]
        if out_uri.startswith("gs://"):
            # Production path: gsutil du -s on the .npz
            r = subprocess.run(
                ['gsutil', 'du', '-s', out_uri],
                capture_output=True, text=True,
            )
            assert r.returncode == 0, (
                f"per-region .npz at {out_uri} ({region['region_id']}) gsutil failed: "
                f"{r.stderr}. The m3-W1 catastrophe pattern at region scope?"
            )
            size_bytes = int(r.stdout.split()[0])
            # Lower-triangular .npz for ~1-2 Mb region with ~1000-10000 variants
            # is typically 10s of MB. Below 100 KB is stub territory.
            assert size_bytes > 100_000, (
                f"per-region .npz at {out_uri} ({region['region_id']}) is "
                f"{size_bytes} bytes — below 100 KB stub floor. HALT."
            )
        else:
            # Local-test path: load the .npz and assert non-empty + finite
            z = np.load(out_uri)
            ld = z["ld"]
            assert ld.shape[0] > 0 and ld.shape[1] > 0, (
                f"per-region .npz at {out_uri} ({region['region_id']}) is "
                f"zero-shape: {ld.shape}. HALT."
            )
            assert np.all(np.isfinite(ld)), (
                f"per-region .npz at {out_uri} ({region['region_id']}) contains "
                f"non-finite values. HALT."
            )
    elif res["status"] == "skipped_idempotent":
        # Idempotency skip per W1-G1 (260520-s2s design delta); validate the
        # existing file via the same checks, not assume it's fine.
        # (Same body as the "ok" branch above; refactor into a helper if this
        # paste-in lands as committed code.)
        pass
    elif res["status"] == "skipped_few_variants":
        # Documented per-region skip per AOU-LD-PIPELINE.md §5.1 MIN_VARIANTS_PER_REGION
        # threshold. No .npz emitted. No validation needed.
        pass
    else:
        # Unknown status — halt and inspect.
        raise RuntimeError(
            f"compute_region_ld returned unknown status {res['status']} for "
            f"region {region['region_id']}; refusing to silently continue."
        )
```

**Performance note:** `subprocess.run(['gsutil', 'du', ...])` per region adds ~1-2 seconds per call. For 322 production regions = ~10 min total overhead. Trivial against 558.5 cluster-hours-per-ancestry baseline. For dev-10 = ~20 seconds total. Acceptable.

## §4 AOU-4 Check 1/2/3/4 + sensitivity paste-in — `.npz` input validation

**Where to paste:** AOU-4 Cell 1 (imports + reticulate) is followed by Check cells that each open `.npz` files. The exact lines vary by check but the pattern is `np.load(LD_NPZ_PATH)` followed by `ld = z["ld"]` followed by R-side compute. AT EACH such load point:

**Paste-in (insert IMMEDIATELY AFTER each `np.load(...)` + `z["ld"]` extraction):**

```python
    # Track 4 D-M3-10 paste-in (260528-l8r): per-region .npz input validation
    # Guards against AOU-2 having silently emitted a stub .npz that would otherwise
    # propagate through R-side susieR / coloc / LDheatmap as wrong-result-without-error.
    assert ld.shape[0] > 0 and ld.shape[1] > 0, (
        f"input .npz at {LD_NPZ_PATH} is zero-shape: {ld.shape}. "
        f"Track 4 D-M3-10 violation upstream — AOU-2 emitted a stub. HALT."
    )
    assert ld.shape[0] == ld.shape[1], (
        f"input .npz at {LD_NPZ_PATH} is non-square: {ld.shape}. Should be a "
        f"symmetric LD matrix. HALT."
    )
    assert np.all(np.isfinite(ld)), (
        f"input .npz at {LD_NPZ_PATH} contains non-finite values. HALT."
    )
    # Optional: assert the matrix is approximately symmetric (numerical noise OK)
    assert np.allclose(ld, ld.T, atol=1e-6), (
        f"input .npz at {LD_NPZ_PATH} is not symmetric within 1e-6 atol. HALT."
    )
```

**Apply at:**
- Cell 3 (Check 1 — known-locus heatmaps for FTO + SORT1): wherever `ld = z["ld"]` for each input region.
- Cell 5 (Check 2 — AoU EUR vs 1000G EUR Pearson r): both AoU and 1000G `.npz` loads.
- Cell 7 (Check 3 — SuSiE-RSS on FTO 16q12 BMI AFR): the LD `.npz` load before the R-side `susieR::susie_rss` call.
- Cell 9 (Check 4 — A/B yield contrast + MAF drop): each region's `.npz` load (AoU AFR + identity-LD comparator).
- Cell 11 (D-M3-07 sensitivity-cohort correlation): both PCA-only and PCA+selfid `.npz` loads per region.

## §5 D-M3-07 sensitivity check paste-in

Same pattern as §4 applied to AOU-4 Cell 11. The sensitivity correlation requires both PCA-only and PCA+selfid `.npz` files to be populated and equal-shape, so add:

```python
# Track 4 D-M3-10 paste-in (260528-l8r): sensitivity-pair shape match
assert ld_pca.shape == ld_selfid.shape, (
    f"PCA vs sensitivity LD shape mismatch for {region_id}: "
    f"{ld_pca.shape} vs {ld_selfid.shape}. HALT."
)
```

immediately after both load+validate blocks.

## §6 Application rules

1. **Apply at Wave 2 fire time, NOT before.** Until then, AOU-2 / AOU-4 stay byte-identical to their committed state (`origin/m3-W2-aou-deltas` HEAD) for AoU tech support / Abby Doyle review of the catastrophe execution context. The committed state is what fired (or was about to fire); modifying it before Wave 2 gives Abby's team a different artifact to review than the one that's actually in flight on her side.
2. **Comment every paste-in cell with the source token** `# Track 4 D-M3-10 paste-in (260528-l8r)` so future git blame can trace the lineage back to this doc + the originating Track 4 quick task.
3. **Run a paste-in audit AFTER applying.** Verify in a single grep that every `hl.read_matrix_table`, every `compute_region_ld` result, and every `np.load(...)["ld"]` extraction is followed by a Track 4 validation block:
   ```bash
   grep -c "Track 4 D-M3-10 paste-in" .planning/notebooks/AOU-2_per_region_ld.ipynb
   grep -c "Track 4 D-M3-10 paste-in" .planning/notebooks/AOU-4_validation.ipynb
   ```
   Expect AOU-2 ≥ 2 (Cell 4 cohort validation + Cell 6 per-region validation) and AOU-4 ≥ 6 (Cells 3 / 5 / 7 / 9 / 11 + sensitivity-pair check).
4. **Commit each paste-in as a separate atomic commit** per the standard quick-task TDD pattern. Don't bundle "Cell 4 cohort validation" with "Cell 6 per-region validation" — they're independently revertable defensive layers.
5. **Test on the synthetic_mt fixture FIRST** if Hail is available (smoke_dev has no Hail per `[[project_python_311_pin]]`; the test runs only on AoU or any env with Hail installed). The synthetic_mt fixture's MTs are populated, so the paste-ins should be silent.

## §7 Cross-references

- `.planning/notebooks/AOU-1_template.ipynb` — Track 4 cells 3.5 / 4.5 / 5.5 (the pattern this doc inherits)
- `.planning/notebooks/AOU-2_per_region_ld.ipynb` — target for §2 + §3 paste-ins
- `.planning/notebooks/AOU-4_validation.ipynb` — target for §4 + §5 paste-ins
- `.planning/notebooks/AOU-0-precheck_template.ipynb` — sister pre-check notebook (run before any Wave 1 or Wave 2 fire)
- `.planning/notebooks/AOU-1-chr22-smoke_template.ipynb` — Wave 1 chr22 smoke (validates the Track 4 pattern under live Hail before Wave 2 inherits it)
- `.planning/quick/260528-jvd-land-m3-w1-track-4-defensive-code-patche/260528-jvd-SUMMARY.md` — originating Track 4 quick task
- `.planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/MIGRATION-PLAYBOOK.md` — RW 2.0 migration sequence; this doc applies AFTER Step 4 validation passes
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` D-M3-10 — protocol locked here
- `.planning/debug/m3-W1-empty-mt-catastrophe.md` — root cause analysis
- `[[feedback_aou_success_marker_not_evidence_of_data]]`
- `[[feedback_hail_checkpoint_contract_violation]]`
