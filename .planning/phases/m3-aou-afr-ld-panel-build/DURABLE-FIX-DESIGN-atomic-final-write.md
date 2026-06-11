# Durable-fix design — atomic final-write contract for `_apply_sample_qc_and_finalize`

**Status:** ⚙️ **PHASE 1 LANDED 2026-06-11** (producer stamp + helpers + contents-only gate + tests). **PHASE 2 PENDING** (consumer wiring + chr22 smoke). Originally drafted 2026-06-10 as design-only; implemented after the cohort was banked.

## ✅ Implementation status (2026-06-11)

**Landed (NCSU-side, TDD, `tests/m3` GREEN — 145 passed / 35 skipped):**
- `VALIDATED_MARKER` + `_has_marker()` + `_write_validated_marker()` + `_final_is_trustworthy()` in `src/python/aou_ld_panel.py` (near `_validate_checkpoint_populated`).
- Producer: `_apply_sample_qc_and_finalize` writes `_VALIDATED` **after** `_assert_checkpoint_nonempty` passes.
- 6 pure `file://` tests (helpers + the catastrophe-signature rejection + a **stale-marker regression**).

**Review correction (adversarial review, 2026-06-11):** the originally-designed Option-2 gate `_has_marker(_VALIDATED) OR _validate_checkpoint_populated` was **REJECTED** — a stale `_VALIDATED` surviving a killed `mt.checkpoint(overwrite=True)` re-fire could vouch for re-emptied contents (the exact re-fire failure this project hit). **The landed gate is CONTENTS-ONLY** (`_final_is_trustworthy = _validate_checkpoint_populated`); the marker is producer-side documentation, never a trust fast-path. The RED-2 snippet below shows the rejected OR form — ignore it; the code is the source of truth.

**PHASE 2 — REMAINING (needs the cluster; Carter):**
1. **Wire the gate into consumers** — the protective value is unrealized until the **AOU-2 / AOU-4 notebook readers** call `_final_is_trustworthy(final_uri)` and **raise on False** before `hl.read_matrix_table`. Until then the producer stamps a marker nobody reads (the read-side hole the catastrophe exposed is reduced-but-not-closed). This is the load-bearing remaining step.
2. **chr22 smoke** — verify the producer actually writes `_VALIDATED` on a real `gs://` finalize (not unit-testable locally — see #3).
3. **`_qc_checkpoint_uri` `file://` footgun (Finding 4, latent):** `_normalize_bucket` strips only `gs://` and `_qc_checkpoint_uri` force-prepends `gs://`, so a `file://` bucket yields `gs://file://…`. Inert in production (always `gs://`) but blocks local finalize integration testing. Fix = make the URI builder scheme-aware. Low priority.

---

_Original design rationale follows (the OR fast-path in "Option 2" + RED-2 was superseded by the contents-only gate above)._

---

## Context — why this fix

The AFR-sens re-fire built all 22 per-chrom intermediates (populated, ~1.29 TB), then the union+finalize died mid-write, leaving a lying `_SUCCESS` over a **0-byte `mt_afr_pca_selfid_qc.mt`**. Diagnosed root cause **H1**: the driver was killed in the window between the two adjacent statements at [`src/python/aou_ld_panel.py:1973–1974`](../../../src/python/aou_ld_panel.py#L1973-L1974):

```python
mt = mt.checkpoint(ckpt, overwrite=True)        # 1973 — Hail writes _SUCCESS here (driver-side finalize)
_assert_checkpoint_nonempty(mt, ckpt, phase="final")  # 1974 — validation; NEVER RAN (driver gone)
```

`mt.checkpoint()` writes `_SUCCESS` on driver-side tasks-reported-complete accounting **before** our post-write assertion runs. A kill in that window → canonical `_SUCCESS` present, contents empty, no traceback. This is the m3-W1 empty-MT catastrophe class, now localized to the **final** write.

## The actual exposure (what's defended vs not)

| Path | Read-gate today | Status |
|---|---|---|
| Intermediates (`post_split`, `post_variant_qc`) | `_validate_checkpoint_populated` + explicit empty-MT fall-through to `auto_fresh` (lines 1631/1649/1659/1675) | ✅ DEFENDED — strict contents gate already in place |
| **Final output (`_qc_checkpoint_uri`)** | **none** — the final is an output, always (re)written; **no consumer-side contents gate** | ❌ EXPOSED |

So the real hole is twofold:
1. **Write side:** the canonical `_SUCCESS` can land before validation (the 1973→1974 window).
2. **Read side:** downstream consumers of the final (`AOU-2_per_region_ld`, `cohort_summary_m3.tsv`, and any human doing `gsutil ls`) **trust `_SUCCESS` directly** — nothing re-validates the final's contents the way the intermediate resume-gates do. A bad final propagates silently.

> Note: the recovery itself is **not** blocked by this — the finalize-only re-drive reads the 22 *intermediates* (strictly gated) and rewrites the final. This fix hardens the final for the *future*, so a canonical `_SUCCESS` always implies validated contents.

## Design options

### Option 1 — write-temp → validate → promote-by-copy ❌ (rejected on GCS)
Write to `{ckpt}__staging`, validate, then promote temp→canonical. On GCS a directory "rename" is **copy + delete, not atomic**, and the final is ~1.5 TiB across thousands of parts → the promote is a second full-size write (doubles cost + is itself interruptible). The handoff's "write-temp→promote" phrasing assumes a cheap rename that GCS does not provide. **Rejected.**

### Option 2 — checkpoint-direct + atomic `_VALIDATED` sentinel + read-gate ✅ (recommended)
Keep the single `mt.checkpoint()` write (the 1.5 TiB cost is unavoidable), but change the **trust contract** so the canonical `_SUCCESS` alone is never the done-signal:

**Producer** (`_apply_sample_qc_and_finalize`, lines 1971–1975):
```python
if bucket is not None:
    ckpt = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
    mt = mt.checkpoint(ckpt, overwrite=True)
    _assert_checkpoint_nonempty(mt, ckpt, phase="final")   # raises on empty
    _write_validated_marker(ckpt)                          # NEW: atomic single-object PUT, ONLY after assert passes
    print(f"[load_qc_cohort] wrote final: {ckpt}")
```
`_write_validated_marker` writes a tiny `{ckpt}/_VALIDATED` object (single atomic GCS PUT). A kill in the old 1973→1974 window leaves `_SUCCESS` but **no `_VALIDATED`** → the final is detectably untrustworthy.

**Consumer / resume-gate** — new helper, mirrors `_validate_checkpoint_populated`:
```python
def _final_is_trustworthy(uri) -> bool:
    # Fast path: _VALIDATED present => producer asserted non-empty. 
    # Back-compat path: _VALIDATED ABSENT (pre-fix clean cohorts) => fall back to
    # contents validation so mt_afr_qc.mt / mt_eur_qc.mt (written before this fix,
    # no _VALIDATED) remain readable.
    return _has_marker(uri, "_VALIDATED") or _validate_checkpoint_populated(uri)
```
Wire it into: (a) a new final-output resume branch in the union/finalize path (skip re-finalize iff trustworthy), and (b) AOU-2 / cohort_summary readers (reject + loud error if a final fails the gate, instead of silently consuming an empty MT).

**Why Option 2 over 1:** O(1) marker vs O(1.5 TiB) copy; same guarantee ("`_SUCCESS` alone is not trust; `_SUCCESS`+`_VALIDATED` is"); fully backward-compatible with the two already-built clean cohorts that have no `_VALIDATED`.

**Residual window (acknowledge honestly):** a kill between `mt.checkpoint()` and `_write_validated_marker` still leaves an un-marked final — but now that state is **detected** (read-gate rejects it) and **recoverable** (re-fire `force_fresh=False` re-finalizes from the still-intact intermediates). The window goes from "silent corruption" to "detected, auto-recoverable." That is the achievable guarantee; true atomicity is impossible without a cheap atomic rename the platform doesn't offer.

## Failing TDD regression (RED-first, reuses existing fixtures)

Conventions from `tests/m3/test_aou_ld_panel_local.py`: `file://` + `tmp_path` + the `_make_stub_mt(mt_dir, with_entries_dir=False)` helper (lines 904–928) that builds the exact `_SUCCESS`+stub-footer catastrophe skeleton.

```python
# RED 1 — the catastrophe signature must be rejected by the new final-trust gate.
def test_final_is_trustworthy_rejects_empty_success_only(tmp_path):
    from aou_ld_panel import _final_is_trustworthy          # NEW symbol -> import fails RED
    mt_dir = tmp_path / "mt_afr_pca_selfid_qc.mt"
    _make_stub_mt(mt_dir, with_entries_dir=True)            # _SUCCESS + empty entries, NO _VALIDATED
    assert _final_is_trustworthy(f"file://{mt_dir}") is False

# RED 2 — a populated final WITHOUT _VALIDATED (the two pre-fix clean cohorts) stays trustworthy.
def test_final_is_trustworthy_backcompat_populated_no_marker(tmp_path):
    from aou_ld_panel import _final_is_trustworthy
    mt_dir = tmp_path / "mt_afr_qc.mt"
    _make_populated_mt(mt_dir)                              # reuse existing populated-MT fixture (see line ~994)
    assert _final_is_trustworthy(f"file://{mt_dir}") is True

# RED 3 — producer writes _VALIDATED only AFTER the non-empty assertion passes.
def test_write_validated_marker_only_after_nonempty(tmp_path):
    from aou_ld_panel import _write_validated_marker, _has_marker
    mt_dir = tmp_path / "final.mt"; _make_populated_mt(mt_dir)
    _write_validated_marker(f"file://{mt_dir}")
    assert _has_marker(f"file://{mt_dir}", "_VALIDATED") is True
```

(Symbols `_final_is_trustworthy`, `_write_validated_marker`, `_has_marker` do not exist yet → all three fail to import = RED, satisfying TDD before any implementation.)

## Scope of the eventual change (for `/gsd-plan-phase --gaps`)
1. `_write_validated_marker(uri)` + `_has_marker(uri, name)` + `_final_is_trustworthy(uri)` helpers (scheme-dispatch `file://` vs `hl.hadoop`, same pattern as `_has_checkpoint`/`_validate_checkpoint_populated`).
2. One new line in `_apply_sample_qc_and_finalize` (1971–1975) after the existing assert.
3. Final-output read-gate in the union/finalize caller + AOU-2 + cohort_summary readers.
4. The 3 RED tests above → GREEN; full `tests/m3` regression must stay green.
5. chr22 smoke re-validation (the durable fix touches the production finalize path).

**Do NOT** start (1)–(5) until the AFR-sens cohort is recovered + banked.
