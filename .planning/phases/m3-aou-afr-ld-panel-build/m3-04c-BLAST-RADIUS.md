# m3-04c BLAST RADIUS — post-execution downstream assessment

**Swept:** `3f431ab..b06cef8`+Task2 (`1798598`), i.e. m3-04c Tasks 1a / 1b / 1c / 2.
**Method:** 4 independent read-only investigators (output-divergence, caller-surface, DAG/wildcard, subregion-correctness), blind to each other, plus orchestrator re-verification of every load-bearing claim.
**Cost:** `$0`, NC State, no perimeter contact. Investigators left **zero** source drift (`git diff --stat HEAD -- src tests config` empty at report time).
**Suite at sweep time:** `tests/m3` **548 passed / 31 skipped / 0 failed**, independently re-run by the orchestrator. **Every defect below is invisible to it.**

---

## ★ HEADLINE — DO NOT FIRE. The fix works only with the quality gate disabled, and it silently un-pins Track-A EUR.

Two findings dominate. Both were **proven end-to-end by the orchestrator**, not argued from the diff.

### ⛔ BLOCKER-A — `--ld-file` is a *preference*, not a mandate, at production thresholds

`run_susie_rss.R` puts the declared file first in `candidates`, but the loop **only `return`s a candidate that passes the quality gate** (`:216`, `overlap >= MIN_LD_OVERLAP && coverage >= MIN_LD_COVERAGE`). On failure it does not stop — it falls through to the `--ld-dir` reconstruction, finds the legacy 1kG panel, and returns **that** with a success status.

Reproduced at the real production thresholds (`config/susie_policy.yaml`: `min_ld_overlap: 50`, `min_ld_coverage: 0.5`):

```
DECLARED (DAG):   .../AFR_aou/m2_region_00067.rds
OPENED  (loader): .../AFR/FTO_16q12.rds            <- 1kG
STATUS:           ld_loaded;overlap_ok;200;1.000   <- reports SUCCESS
MISMATCH:         TRUE
```

This is **BLOCKER-1's exact defect class** — the DAG declares one panel, the fit reads another, nothing warns — relocated ~60 lines down.

⚠ **Why nothing caught it, including the orchestrator's own acceptance proof.** Every test in
`tests/m3/test_ld_read_path.py` pins `MIN_LD_OVERLAP <- 1L; MIN_LD_COVERAGE <- 0.0; MIN_LD_MIN_USE <- 1L`
(`:186-188`) — the gate is **disabled in all 8 of them**. The orchestrator's `resolved == opened`
proof set `MIN_LD_OVERLAP <- 1L` for the same reason (to let a 5-variant fixture qualify), so it
was valid only under permissive thresholds and was reported without that caveat. **The suite is
structurally incapable of observing production behaviour.**

Three further ways the "single source of truth" claim fails, all proven:
- **Last-partial-wins.** `best_partial <- list(...)` (`:237`) overwrites unconditionally, so a declared AoU panel at 40/100 overlap **loses** to a dir candidate at 20/100 — the fit silently takes the *worse* panel.
- **`use_identity` bypass.** `:182-184` `return()`s *before* the gate is evaluated, and `:529` sets `ld_source <- ld_result$source`, so the JSON receipt shows `ld_matrix == ld_file_declared` **while SuSiE ran on `diag(n)`**. The receipt reads GREEN on a forged match.
- **Corrupt file = silence.** `:171-175` wraps `readRDS` in `tryCatch` → `NULL` → bare `next`. No message, no warning, no JSON field, no non-zero exit. A truncated `.rds` from an interrupted conversion burns full compute and emits a plausible result.

### ⛔ BLOCKER-B — Track-A EUR numerics MOVE. The "EUR cannot move" claim is REFUTED.

BLOCKER-1 was **silently pinning every EUR fit** to `{ld_dir}/EUR/{region}.rds` (the 1kG tail),
because the script always rebuilt its own path regardless of what `resolve_ld_path` chose.
**Task 1b removes that pin for every ancestry, not just AFR.**

Proven with two deliberately different EUR panels:

```
BEFORE (no --ld-file): opened .../EUR/FTO_16q12.rds           r[1,2] = 0.1
AFTER  (--ld-file):    opened .../EUR_ukbb_pub/FTO_16q12.rds  r[1,2] = 0.9
EUR LD MATRIX CHANGED: TRUE
ld_status BEFORE == ld_status AFTER: TRUE   <- byte-identical
```

An independent investigator ran the full script and measured the downstream effect on one EUR
fixture: **credible sets 3 → 10, nonzero PIPs 200 → 78**, while `ld_status` and
`ld_overlap_fraction` — *the two fields Track A would check to argue nothing changed* — stayed
**byte-identical**.

**EUR is safe TODAY only because `data/processed/ld_reference/` does not exist at all.** That is
enforced by nothing. `EUR_ukbb_pub` is the configured EUR chain head (`config/pipeline.yaml:213`)
and building it is a `$0` NC-State prerequisite already on the roadmap (Check 2c). The day it
lands, published Track-A numbers move with **no error and no flag**.
⚠ Track A is in submission. This is the highest-consequence item in the sweep.

---

## Other confirmed defects (orchestrator-verified)

| # | Sev | Finding | Evidence |
|---|---|---|---|
| C | **BLOCKER** | **Nothing builds the `.rds`.** `resolve_ld_path` returns the first *existing* path (`ld_panel.py:87`), so a not-yet-built chain head is skipped, never pulled in as a to-be-built input. `m3_convert_npz_rds.smk` has one rule and **no aggregate target**; `ALL_TARGETS` names no `AFR_aou/*.rds`. After a successful 11-day fire, `snakemake all` resolves AFR to the 1kG tail **silently**. The rule *is* reachable by explicitly naming the path (verified: clean 3-job DAG) — so the fix is wiring, not logic. m3-04c fixed which path is *requested* (1a) and *opened* (1b); **who builds it** was never fixed. |
| D | **BLOCKER** | **The `.npz→.rds` consumer is unbounded-dense.** `ld_npz_to_rds.R:103` materialises a full dense n×n float64 matrix (plus 2 more copies at `:134,:138`), under a declared `mem_mb=8000` (`m3_convert_npz_rds.smk:119`). Real `n_var` for the crosswalk targets: SH2B3 `__sub14` = 75,497 → **45.6 GB**; FTO/HLA = 363k–372k → **~1.1 TB**. This is the *same OOM class* the project already fixed **twice** on the producer side and never on the consumer. SH2B3's subregion is by far the smallest target; the other ten are categorically impossible as written. |
| E | **HIGH** | **The colocalization would mix LD panels.** `qtl_coloc.smk` has **zero** references to the crosswalk or resolver (`grep -c` = 0); `_qtl_coloc_ld_input` (`:203-218`) builds the legacy `{ld_reference}/{ancestry}/{region}.rds`. That LD reaches `coloc::runsusie` (`run_qtl_coloc.R:204,290`) while the GWAS fit it colocalizes was produced on the AoU panel. Only one of the repo's LD consumers was crosswalked. |
| F | **HIGH** | **The crosswalk has no ancestry gate.** `finemap.smk:282` applies `CURATED_TO_M2.get(...)` for **every** ancestry, but the crosswalk was built AFR-only (`build_curated_m2_crosswalk.py:145`). `config/pipeline.yaml:214` (EUR pos. 2) and `:222` (**TRANS chain HEAD**) both template on `{region_id}`. Contrast the occlusion lockstep, which *is* ancestry-scoped (`pipeline.yaml:257`) for exactly this hazard. |
| G | **HIGH** | **Retiring `build_ld_rds_aou_eur` orphaned the TRANS chain head, and strict mode cannot catch it.** `config/pipeline.yaml:222` still makes `EUR_aou/{region_id}.rds` TRANS's *first* candidate; its producer was removed in this change set. The `strict_aou_only` guard tests `entry["source"].endswith("_aou")` and the source is `TRANS_aou_eur` → **`False`** (verified). TRANS walks to `EUR_1kg` forever, silently, even with strict mode ON. The removal note verified the *rule name* had no references, not the *artifact path*. |
| H | **HIGH** | **The sumstats↔panel join is allele-blind.** Panel `SNP_ID` is GRCh37 `chr:pos:ref:alt` (`ld_npz_to_rds.R:75-80`); harmonized AFR sumstats carry `chr:pos`. The `SNP_ID` branch therefore matches **zero** rows and everything degrades to the CHR/POS branch's `match()` — first hit, REF/ALT ignored. On a WGS panel that means multiallelics bind to an arbitrary ALT's LD row with no orientation check. Only defence is the non-blocking `d3b_ld_z_consistency_s` flag. PRE-EXISTING but **activated** by this change (the join never ran against a WGS panel before). |
| I | MEDIUM | **`finemap_summary.tsv` cannot distinguish an AoU row from a 1kG row.** The only LD field in `FIELDNAMES` is `ld_dir` = the constant `data/processed/ld_reference`. The panel lives only in `ld_matrix`, which is not a fieldname. Every manuscript table built from that summary is panel-blind. |
| J | MEDIUM | **The receipt false-alarms.** `finemap.smk:362` reads `ld_matrix`/`ld_file_declared`, but the `no_variants` (`:401-418`) and `too_many_variants` (`:432-450`) early-exit writers emit neither key — printing `None None`, indistinguishable from a real regression. HLA_6p21 and PYHIN1_1q23 are named `too_many_variants` regions. |
| K | MEDIUM | **`variant_catalog_fallback` is a MUTATED pre-existing key, not additive.** All 1,957 legacy JSONs carry `false`; the Path-2 parity change flips it `TRUE` with no numeric cause. Anyone diffing before/after will chase it. (`ld_overlap_zero_fallback` *is* genuinely additive and fine.) |
| L | MEDIUM | **The crosswalk artifact is hand-run, DAG-absent, and compared against nothing.** No rule produces `config/curated_to_m2_region_map.tsv`; no test reads the committed file (all tests rebuild into a tmpdir). The WARN fires only on a **fully empty** dict, so a 13th curated region added without a rebuild is silently legacy-routed. **Verified in sync today** (fresh rebuild is byte-identical) — the risk is forward drift. |
| M | MEDIUM | **`load_curated_to_m2` filters `unmapped` only** (`:485-490`), so a future `status=partial` row (30% coverage) would be handed to `resolve_ld_path` exactly like a contained one, contradicting the builder's own promise at `:47-49`. Inert today. |

---

## ✅ Verified safe — and one important correction to the pre-sweep framing

- **THE SH2B3 CORE STRADDLE IS A NON-RISK.** The pre-sweep framing (including the orchestrator's)
  treated the `__sub14`/`__sub15` core straddle as the headline scientific risk. **It is empirically
  false on the axis that matters.** The panel is computed over the **WINDOW**, not the core
  (`run_native_ld_panel.py:727-728`), and `start_grch38 == window_start_grch38` for **all 552
  manifest rows, 0 exceptions** (verified). `__sub14`'s window lifted to GRCh37 is
  103,944,368–114,923,170, which **strictly contains** SH2B3 — the crosswalk's own
  `overlap_frac` is **1.000000**. The 12.8% "gap" is core bookkeeping; **no variant is missing.**
- **The core-overlap ranking key is scientifically INERT.** Both `__sub14` and `__sub15` windows
  fully contain the locus, and the banding radius (3 Mb) dwarfs the 600 kb locus, so **pairwise r
  for every SH2B3 pair is identical under either choice.** Worse, its stated justification cites
  `stitch_subregions_to_rds.R` "de-dup on core ownership" — and that script is **wired into no
  Snakemake rule** (one hit repo-wide, a comment). A reviewer following that disclosure looks in
  the wrong place. *(The selection is still right; the disclosure explaining it is misleading.)*
- **There is no stitch to bypass.** One `.npz` → one `.rds`, per subregion. No split parent appears
  as a whole `region_id`, so a subregion is the **only buildable panel** — the crosswalk pointing at
  one is correct, not a shortcut.
- **The gate passes for SH2B3 with margin** on real inputs: ~4.1k panel variants vs 1,011–3,354
  sumstats variants in the window; MAF-floor coverage ceiling 0.81–1.00 vs the 0.5 threshold;
  overlap ~10³ vs the 50 threshold.
- **Correction to the assumed failure mode:** sub-threshold does **not** fall to identity. `:232-251`
  returns `best_partial` whenever overlap ≥ `MIN_LD_MIN_USE` (10), and `:488` then **shrinks the
  region to the matched variants** and fits *that*, under `ld_loaded;partial_overlap;N;f` — a status
  that reads as success. **Silent truncation is less visible than identity**, and the committed
  disclosure describes only identity.
- **The widened wildcard is clean.** No `__sub` mis-parser anywhere on the live path (every site is
  exact-string or suffix-based, never `_`-split); constraint properly anchored; `--list` succeeds;
  a real dry-run resolves `m2_region_00040__sub14 → chr 12` correctly; no ambiguity fires;
  `__sub14__sub02` correctly rejected. Parent/child collision is **structurally impossible** —
  0 of the 8 split parents appear as standalone ids.
- **Resume/idempotency is sound** for the 123 newly-admitted ids: panel-TSV dedup and `.npz`
  existence checks are exact-string.
- **`plan_ld_egress.py` is `__sub`-safe** — derives `chr` from the joined column, never by parsing
  the id. Verified on the real 276-row manifest.
- **`BMI_Xq24` falls through byte-identically** — `status=unmapped` → loader skips → the expression
  evaluates to the pre-change form character-for-character.
- **`pyliftover` is lazy and correctly scoped** — module import succeeds without it; `_open_lifter`
  raises a loud named `ImportError`; DAG construction does not depend on it.
- **`character(0)` prepend is a genuine no-op** for legacy callers; both-absent returns the
  byte-identical `ld_dir_missing` status.
- **The `.rds` contract is honored identically on both paths** (triangle, symmetry, `diag=1`,
  alignment) — *except* the `use_identity` early return, which is the one real gate bypass.

---

## Gate binding — what blocks what

| Gate | Blocked by | Autonomous? |
|---|---|---|
| **Nothing (already merged)** | every item in "Verified safe" | — |
| **Re-running ANY EUR fit / rebuilding `EUR_ukbb_pub`** | **BLOCKER-B** (Track-A numerics move silently) | Yes — `$0`. **Highest consequence; Track A is in submission.** |
| **The ~11-day billed fire** | **BLOCKER-A** (declared panel not authoritative), **BLOCKER-C** (nothing builds the `.rds`), **BLOCKER-D** (consumer OOM at 45.6 GB–1.1 TB vs `mem_mb=8000`) | Mostly yes, `$0` — but D may need a big-memory node decision |
| **Trusting any AFR fine-map result** | BLOCKER-A, H (allele-blind join), I (summary is panel-blind) | Yes, `$0` |
| **Any GWAS×QTL colocalization** | E (mixed LD panels inside one `coloc.susie`) | Yes, `$0` |
| **Any TRANS fit** | G (orphaned chain head, strict mode blind), F (no ancestry gate) | Yes, `$0` |
| **Publishing the panel provenance** | I, J, K | Yes, `$0` |
| **Growing the curated region set** | L (no drift detection), M (`partial` promoted) | Yes, `$0` |

**Nothing here blocks what has already merged.** The change is directionally right — it genuinely
closed the declare-vs-read split, and I proved the AoU panel is now readable when the gate passes.
No revert is warranted. What it did **not** do is make the declared panel *authoritative*, and it
un-pinned EUR as a side effect nobody attributed to it.

---

## Recommended sequence

1. **Decide the EUR/TRANS containment FIRST** (BLOCKER-B) — it is `$0` and it protects a manuscript
   in submission. Either ancestry-gate `--ld-file` + `CURATED_TO_M2` (mirroring
   `occlusion_lockstep.ancestries`), or set `ld_panel.pin.EUR` / `pin.TRANS` to `EUR_1kg` for the
   duration and record it as a disclosed deviation.
2. **Make the declared file authoritative** (BLOCKER-A): fail loudly when `--ld-file` is supplied but
   rejected / unreadable / `use_identity`, instead of `next`. Fix `best_partial` to keep the *best*
   overlap, not the last (`:237`). Consider dropping `--ld-dir` from the rule entirely.
3. **Re-run the acceptance tests at PRODUCTION thresholds** — the current 8 are all gate-disabled and
   cannot see any of this.
4. **Wire the build** (BLOCKER-C): an aggregate convert target, or 276 explicit paths in the runbook.
5. **Size the consumer** (BLOCKER-D): bound `ld_npz_to_rds.R` block-wise (the producer-side fix
   already exists as precedent) or declare a real `mem_mb` and a big-memory queue.
6. Then E (crosswalk `_qtl_coloc_ld_input`), H, I/J/K, L/M.
7. **Fire only after 1-5.** Otherwise the ~$385–1,084 buys a panel the DAG never builds, a loader
   that may silently prefer 1kG, and a converter that OOMs on ten of twelve targets.

---

## Process note — the recurring failure mode of this session

**Five separate assertions in this change set were structurally incapable of failing**, and each was
found by a *different* reviewer: HIGH-0's total-miss guard (membership always true); the
`resolve_ld_path` regex (matched from a docstring); two self-caught test defects (a `pytest.skip`
masking a status regression, and a comment satisfying its own regex); and now the entire
`test_ld_read_path.py` suite (gate disabled). **The orchestrator's own BLOCKER-1 proof had the same
flaw** and was reported without the caveat.

The generalizable rule: **a green assertion is evidence only if you have seen it fail.** Every one of
these would have been caught by a negative control. The plan mandated exactly one such control
(`test_kwarg_assertion_is_not_vacuous`) and it worked — it is the only assertion in the set nobody
had to re-litigate. Related: `[[feedback_skip_guard_masks_not_fixes]]`,
`[[feedback_declared_input_is_not_the_read_path]]`,
`[[feedback_coverage_assertion_can_be_false_invariant]]`.
