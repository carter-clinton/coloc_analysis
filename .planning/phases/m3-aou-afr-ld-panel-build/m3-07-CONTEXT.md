# m3-07-W7 — Overlapping-deletion span-filter + provenance manifest + present-rate scan — Context

**Gathered:** 2026-07-10 · **Status:** Ready for planning (`/gsd-plan-phase`) · **Mode:** plan-directly (science already settled in the amendment doc-set)

<domain>
## Task Boundary

Build the **upstream, panel-build-stage fix** for the region-1-class NaN in the AoU AFR native-plink LD panel:

1. **Overlapping-deletion span-filter** across ALL 276 regions — detect where a deletion's REF interval physically covers a partner variant's POS (occlusion) and **exclude the occluded record from the LD window BEFORE plink `--r`**.
2. **Load-bearing provenance manifest** — per excluded variant, a durable record (see schema below). Doubles as the genome-wide occlusion catalog for the Angle-1/3 scientific claim.
3. **Genome-wide present-rate-per-ancestry scan** — for occluded variants, report PRESENT-vs-ABSENT rate per ancestry (the metric that sizes the scientific cost).
4. **Lockstep sumstats-side drop** — wire the same exclusion into the m3-04 consume/ingest step so panel and sumstats stay aligned on the `(CHR,POS)` / `chr:pos:ref:alt` join.

**NOT in scope:** re-firing the AoU loop (do NOT re-fire until this lands); NaN→0 / PSD conditioning of any kind (dead — see below); touching `read_square_bin` / `content_verify_npz` NaN-raise (they correctly surfaced this and STAY).
</domain>

<decisions>
## Locked Decisions (from the byte-verified amendment doc-set — do NOT re-litigate)

### Mechanism (RESOLVED, coordinate-proven — `m3_region1_nan_geometry_verdict.md`, `4543dcf4…`, on origin `5fd58a5`)
- Region-1 NaN = **overlapping-deletion occlusion**: a deletion's REF span covers a neighbor SNP's POS → the base is absent on the deletion haplotype → uncallable → `r` is **structurally undefined** (no "true r").
- 6/6 pairs resolved: **5 direct `ref_span_overlap` + 1 second-order** (pair 4: SNP@5922718 inside the upstream DEL@5922716; pairs 3+4 = ONE 3-record tangle 5922716/5922718/5922724). **0 same-position/mergeable, 0 chance-degeneracy.**
- `bcftools norm -m +` fixes NONE (no same-position cases); `norm -f` left-align won't remove a deletion spanning a neighbor. Left-align is fine as generic hygiene but does not resolve this.
- **SYSTEMIC:** region 1 alone has **7 distinct deletions** (60/29/7/31/31/17/29 bp) occluding neighbors → recurs genome-wide → the fix belongs UPSTREAM at panel-build, **not** a per-region patch.

### Policy (RESOLVED, Seth-endorsed — `m3_panel_occlusion_policy_decision.md`, `42d70167…`, `8f36fdf`)
- **Exclude-in-lockstep across panel AND sumstats.** Handling = exclude the occluded record / flag the locus limited-resolution + treat `r` as structurally undefined **WITH provenance — never zero.**
- **NaN→0 is DEAD.** The m3-06 `condition_ld_matrix.py` conditioning code stays FROZEN/HELD, never fed to a fit. 999.1 §5-6 are dead.
- **Panel-only-exclude is UNSAFE** — it orphans a sumstats-present variant on the `(CHR,POS)` join (proven: the occluded SNP `rs182965575` is PRESENT in 7/9 AFR harmonized sumstats — hinge check `c4e0875`). Hence the sumstats-side drop MUST happen in lockstep.
- The **provenance manifest is a HARD requirement**, not optional logging.

### Provenance manifest schema (per excluded variant — load-bearing)
- Variant ID + **BOTH-build positions** (GRCh38 panel + GRCh37 sumstats, per the `ld_npz_to_rds.R` liftover).
- The occluding deletion (ID) + its **REF span** (start–end).
- Locus / region id; traits-present (which harmonized sumstats carry the variant).
- reason = `reference-occlusion → undefined-LD`.
- Aggregate rollup = the genome-wide occlusion catalog (Angle-1/3).

### Join key (verified NC-State)
- Panel↔sumstats join = `SNP_ID` = `chr:pos:ref:alt` (`ld_npz_to_rds.R` + `refit_sh2b3_psd_regularized.R:106,137`), with a `chr:pos↔rsid` bridge (`snp_id_bridge.R`) for convention drift. **Excluding a panel record changes which variants the panel carries → the sumstats-side must drop in lockstep or the join orphans the variant.** Exclude-occluded is the join-SAFEST option (drops variants, no re-key).
</decisions>

<constraints>
## Hard Constraints / Gates

- **⚠ OSF PRE-REGISTRATION GATE (BLOCKS all fix code):** pre-register the **scoped OSF amendment-update** (panel overlapping-variant policy = exclusion + provenance, never zeroing) BEFORE any fix code lands — mirrors the 999.1 OSF-gate discipline (the AFR NaN-PSD amendment `tcujq` precedent). Planning may proceed now (docs); **execution/code is gated on the amendment-update being posted + recorded.** The plan MUST encode this as its first hard gate.
- **No perimeter access / no loop re-fire** from planning or code landing — the fix is NC-State-side panel-build code; the AoU loop stays untouched until the fix lands and a region-1 re-run is validated.
- **Frozen contracts stay frozen:** `read_square_bin` / `content_verify_npz` NaN-raise, the raw `.npz` format, `ld_npz_to_rds.R`. The fix removes the occluded rows UPSTREAM (before `--r`) so no NaN reaches the reader.
- **TDD RED-first**, panel-build module scope (`run_native_ld_panel.py` / `aou_ld_panel.py` + a new manifest/scan module); reuse existing utilities (window `.bim` reads, `_retained_window_bim` snplist-threading pattern from the drop-monomorphic fix) rather than new machinery where possible.
- Rigor over speed ([[feedback_rigor_over_speed]]); original-research framing ([[feedback_original_research_framing]]).
</constraints>

<canonical_refs>
## Canonical References (all on origin `m3-W2-aou-deltas` @ `5fd58a5`)

- `.planning/amendments/m3_region1_nan_geometry_verdict.md` — WHAT/mechanism (byte-verified `4543dcf4…`)
- `.planning/amendments/m3_panel_occlusion_policy_decision.md` — POLICY (byte-verified `42d70167…`, `8f36fdf`)
- `.planning/amendments/m3_region1_occlusion_hinge_check.md` — JOIN-IMPACT / why lockstep (`c4e0875`)
- `.planning/amendments/m3_nan_conditioning_scientific_review.md` — WHY NaN→0 is wrong (Seth, `3516c18`)
- `.planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md` — the prior AFR amendment + OSF-gate precedent
- ROADMAP m3-07 line + the SUPERSEDED-by-m3-07 banner on 999.1
- Panel-build code: `src/python/run_native_ld_panel.py`, `src/python/aou_ld_panel.py`; join: `src/scripts/ld_npz_to_rds.R`, `src/R/.../snp_id_bridge.R`
- Operating manual for any AoU-side step: the `aou-ld-pipeline` skill
</canonical_refs>
