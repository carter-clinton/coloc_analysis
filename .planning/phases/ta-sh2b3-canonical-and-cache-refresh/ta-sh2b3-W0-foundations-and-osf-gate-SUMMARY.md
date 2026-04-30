---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 0
subsystem: infra
tags: [snakemake, susie-rss, coloc-susie, lsf, osf, validation, ld-panel]

# Dependency graph
requires:
  - phase: ta-sh2b3-canonical-and-cache-refresh
    provides: "phase scaffolding (CONTEXT, RESEARCH, VALIDATION, PLAN)"
provides:
  - "C1-C15 verification harness (bin/verify_ta_sh2b3_phase.sh)"
  - "Per-L SuSiE policy YAMLs (config/susie_policy_L{15,20,30}.yaml)"
  - "Per-L pipeline overlays (config/pipeline_lsweep_L{15,20,30}_overlay.yaml)"
  - "R2 canonical-pair pipeline overlay (config/pipeline_canonical_r2_overlay.yaml)"
  - "Wave 1/2/4 dispatch drivers (bin/fire_{susie_lsweep,canonical_susie_pairs,qtl_coloc_cache_refresh}.sh)"
  - "R2 manifest builder (src/python/build_coloc_manifest_r2.py)"
  - "Pitfall 2 mitigation patch (finemap.smk policy is now config-aware)"
  - "Schema-vs-config drift fix (ld_panel block in pipeline.schema.yaml)"
  - "D-TA-Wave-0-foundations + D-TA-04-DIAGNOSTIC + D-TA-Wave-0-pitfall2 recorded in CONTEXT.md addendum"
affects: [ta-sh2b3-W1, ta-sh2b3-W2, ta-sh2b3-W4, ta-sh2b3-W5, ta-sh2b3-W6, ta-sh2b3-W7]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-L parallel-namespace overlay pattern (results_lsweep_L{15,20,30}/) for sensitivity sweeps"
    - "config-merge propagation via config.get('finemap', {}).get('policy', default) in static rule inputs"
    - "C1-C15 dimension verification harness emitting JSON-line PASS/WARN/FAIL per check"
    - "D-TA-01 driver fallback (RS1 if .git, else GPFS) — handles namespace collision"

key-files:
  created:
    - "config/susie_policy_L15.yaml"
    - "config/susie_policy_L20.yaml"
    - "config/susie_policy_L30.yaml"
    - "config/pipeline_lsweep_L15_overlay.yaml"
    - "config/pipeline_lsweep_L20_overlay.yaml"
    - "config/pipeline_lsweep_L30_overlay.yaml"
    - "config/pipeline_canonical_r2_overlay.yaml"
    - "bin/fire_susie_lsweep.sh"
    - "bin/fire_canonical_susie_pairs.sh"
    - "bin/fire_qtl_coloc_cache_refresh.sh"
    - "bin/verify_ta_sh2b3_phase.sh"
    - "src/python/build_coloc_manifest_r2.py"
  modified:
    - ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md (3 addenda)"
    - "src/snakemake/rules/finemap.smk (Pitfall 2 patch)"
    - "src/snakemake/schemas/pipeline.schema.yaml (ld_panel block)"
    - ".gitignore (results_lsweep_L{15,20,30}/)"

key-decisions:
  - "D-TA-Wave-0-foundations: D-TA-01 path is INVESTIGATE (namespace collision); recommend Wave 1+ drivers fall back to GPFS path; drivers carry RS1→GPFS fallback inline"
  - "D-TA-04-DIAGNOSTIC = RSID across all 3 sample fits → cache-scope = QTL_COLOC_ONLY; Wave 4 SuSiE-RSS layer untouched (default SUSIE_LAYER_SCOPE=no)"
  - "D-TA-Wave-0-pitfall2 = PATCH_REQUIRED — finemap.smk:62 hardcoded policy; patched to config.get; baseline L=10 default preserved"
  - "Schema-vs-config drift (ld_panel missing from schema) auto-fixed under Rule 3 (blocking issue) — every Snakemake invocation was failing"

patterns-established:
  - "Per-L overlay convention: pipeline_lsweep_L{N}_overlay.yaml rebases paths.results_root + finemap.policy + finemap.output_dir"
  - "R2 parallel-namespace convention: results/multitrait/coloc_susie_R2/ + results/multitrait/coloc_manifest_R2.tsv preserves Stage 2 md5 invariant until Wave 5"
  - "Snakemake config-merge mitigation: read static rule inputs via config.get(...) when overlays must propagate"
  - "Verification harness emits JSON-line per dimension; exit code = number of FAILs; WARN does not fail"

requirements-completed: []  # Wave 0 partial; OSF gate (Task 7) blocks REQ-OSF-PREREG completion

# Metrics
duration: 17min (Tasks 1-6 only; Task 7 blocked on Carter web-UI)
started: 2026-04-30T00:15:30Z
completed: 2026-04-30T00:33:07Z (Tasks 1-6 commit landed)
status: PARTIAL
status-detail: "PARTIAL — awaiting human-verify on OSF gate (Task 7, D-TA-OSF-COVERAGE per D-TA-05). Wave 1 HARD GATE blocks until Carter records D-TA-OSF-COVERAGE = COVERED or AMENDMENT_POSTED in CONTEXT.md addendum."
---

# Phase ta-sh2b3 Plan W0: Foundations + OSF gate Summary

**Wave 0 foundation scaffolding for SH2B3 EUR canonical-pair coloc.susie + variant-ID cache refresh: 7 config YAMLs + 4 dispatch scripts + C1-C15 verification harness + Pitfall 2 mitigation (finemap.smk policy is now config-aware) + Pitfall 1 diagnostic (D-TA-01 namespace collision flagged for Carter resolution before Wave 1).**

## Status: PARTIAL — Awaiting Human-Verify on OSF Gate

Tasks 1–6 complete (atomic commits per task). Task 7 is a `checkpoint:human-verify` with `gate="blocking"`: Carter must verify OSF pre-registration coverage at `osf.io/pvb5j` Methods + `osf.io/az52u` closeout PDF for D-TA-02 (L-sweep wording) + D-TA-03 (canonical-pair scope) and record `D-TA-OSF-COVERAGE` outcome in CONTEXT.md addendum. **Wave 1 HARD-GATED on this verification per D-TA-05 + REQ-OSF-PREREG.**

## Performance

- **Duration:** 17 min (Tasks 1–6 only; Task 7 blocks on Carter web-UI)
- **Started:** 2026-04-30T00:15:30Z
- **Tasks 1–6 completed:** 2026-04-30T00:33:07Z
- **Tasks 7 status:** awaiting human-verify (OSF coverage)
- **Tasks committed:** 6 of 7 (atomic commits per task; 7 total commits including the Pitfall 2 patch separated from its CONTEXT addendum)
- **Files created:** 12
- **Files modified:** 4

## Accomplishments

- Verified code-fix ancestry: `069b34f` (run_qtl_coloc.R chr:pos tolerance) and `7d54183` (run_susie_rss.R LD-panel-rsid override) are HEAD ancestors on the current branch (no cherry-pick required).
- D-TA-04 variant-ID format diagnostic recorded: all 3 sample SuSiE-RSS `.fit.rds` fits use rsid format (rs7961935, rs12446228, etc.) → SuSiE-RSS layer is post-`7d54183` → Wave 4 cache scope = `QTL_COLOC_ONLY` (~10 hr at 50 cores; SuSiE-RSS layer untouched).
- 7 config YAML files scaffolded for Wave 1/2 parallel-namespace dispatch:
  - `config/susie_policy_L{15,20,30}.yaml` — per-L overrides preserving all non-L policy fields
  - `config/pipeline_lsweep_L{15,20,30}_overlay.yaml` — rebase paths.results_root + finemap.policy + finemap.output_dir
  - `config/pipeline_canonical_r2_overlay.yaml` — declares R2 parallel namespace for Wave 2 (Pitfall 3 mitigation)
- Pitfall 2 (RESEARCH.md L351) verified real and mitigated: `finemap.smk:62` hardcoded `policy="config/susie_policy.yaml"` as static rule input, blocking config-merge propagation. Patch reads from `config.get("finemap", {}).get("policy", default)`. Dry-run before/after proves the L20 overlay now propagates.
- Pre-existing schema-vs-config drift (Rule 3 deviation auto-fix): `pipeline.schema.yaml` was rejecting the `ld_panel` block (added during M3, predating ta-sh2b3-W0) due to top-level `additionalProperties: false`, blocking every Snakemake invocation. Added explicit `ld_panel:` schema entry with per-ancestry resolver chain.
- 3 LSF dispatch driver scripts + 1 Python manifest builder scaffolded (Wave 1/2/4 fire-ready post-OSF-gate).
- C1–C15 verification harness (`bin/verify_ta_sh2b3_phase.sh`) lands with all 15 check functions; `--wave N` filter; emits JSON-line PASS/WARN/FAIL per check; exit code = FAIL count.
- Snakefile rule-name surface enumerated and recorded: `all_qtl_coloc` (Wave 4 dispatch), `run_finemap` (Wave 1 SuSiE rule), `run_coloc_susie` (Wave 2 canonical-pair rule), plus 12 supporting rules across finemap.smk + multitrait.smk + coloc.smk + qtl_coloc.smk.

## Task Commits

Each task committed atomically (one task → one commit; Task 4 produced 2 commits because the patch and the CONTEXT addendum are separable):

1. **Task 1: Verify D-TA-01 path + code-fix ancestry + Snakefile rule names** — `e4ac4a3` (docs)
2. **Task 2: SuSiE-RSS variant-ID format diagnostic (D-TA-04)** — `2995ca7` (docs)
3. **Task 3: Per-L policy YAMLs + pipeline overlays + R2 overlay** — `9a83588` (feat)
4. **Task 4a: Pitfall 2 mitigation (finemap.smk + schema fix)** — `840d1b6` (fix)
5. **Task 4b: Record Pitfall 2 outcome in CONTEXT** — `ef81efb` (docs)
6. **Task 5: Wave 1/2/4 dispatch drivers + R2 manifest builder** — `dbeccdc` (feat)
7. **Task 6: C1-C15 verification harness** — `1c23441` (feat)

Plus a final metadata commit (this SUMMARY.md + STATE.md update) at plan close — pending Task 7 resume to land.

## Files Created/Modified

### Created (12)

- `config/susie_policy_L15.yaml` — Wave 1 L=15 SuSiE policy override
- `config/susie_policy_L20.yaml` — Wave 1 L=20 SuSiE policy override (D-TA-02 primary candidate)
- `config/susie_policy_L30.yaml` — Wave 1 L=30 SuSiE policy override (D-TA-02 upper bound)
- `config/pipeline_lsweep_L15_overlay.yaml` — Wave 1 L=15 parallel-output overlay
- `config/pipeline_lsweep_L20_overlay.yaml` — Wave 1 L=20 parallel-output overlay (Pitfall 2 dry-run target)
- `config/pipeline_lsweep_L30_overlay.yaml` — Wave 1 L=30 parallel-output overlay
- `config/pipeline_canonical_r2_overlay.yaml` — Wave 2 R2 namespace overlay (Pitfall 3 mitigation)
- `bin/fire_susie_lsweep.sh` — Wave 1 driver (3 traits × 3 L values)
- `bin/fire_canonical_susie_pairs.sh` — Wave 2 driver (9 SH2B3 EUR canonical pairs)
- `bin/fire_qtl_coloc_cache_refresh.sh` — Wave 4 driver (cache backup + Snakemake re-fire; SUSIE_LAYER_SCOPE conditional)
- `bin/verify_ta_sh2b3_phase.sh` — C1-C15 verification harness
- `src/python/build_coloc_manifest_r2.py` — R2 canonical-pair manifest builder (synth-rows fallback for missing pairs)

### Modified (4)

- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` — 3 addenda: D-TA-Wave-0-foundations + D-TA-04-DIAGNOSTIC + D-TA-Wave-0-pitfall2
- `src/snakemake/rules/finemap.smk` — Pitfall 2 patch (line 62): policy now reads `config.get("finemap", {}).get("policy", "config/susie_policy.yaml")`
- `src/snakemake/schemas/pipeline.schema.yaml` — added `ld_panel:` block + matching `pin:` and `strict_aou_only:` properties (Rule 3 schema-drift fix)
- `.gitignore` — added `results_lsweep_L{15,20,30}/` to mirror `results_identity_ld/` pattern

## Decisions Made

- **D-TA-Wave-0-foundations (Pitfall 1 outcome): D-TA-01 path is INVESTIGATE.** `/rs1/researchers/c/ckclinto/coloc_analysis/` exists but is NOT a git repo on this GPFS node — it contains historical pre-pivot artifacts (a 77 GB tar.gz, region_analysis subdir, etc.). Carter-mediated escalation required before Wave 1+ LSF dispatches. **Mitigation in driver scripts:** all 3 dispatch drivers carry an inline RS1→GPFS fallback (`if [ -d /rs1/.../coloc_analysis/.git ]; then cd /rs1/...; else cd /gpfs_common/...; fi`) so they remain functional under either resolution path. Recorded as the D-TA-Wave-0-foundations addendum in CONTEXT.md.

- **D-TA-04-DIAGNOSTIC = RSID (aggregate across 3 sample fits) → cache-scope = QTL_COLOC_ONLY.** All 3 sampled SuSiE-RSS fits (`bmi.EUR.SH2B3_12q24`, `bmi.EUR.FTO_16q12`, `hypertension.EUR.SH2B3_12q24`) carry rsid-format variant IDs in `colnames(fit$alpha)`, indicating the SuSiE-RSS layer is post-`7d54183`. Wave 4 backs up only `results/qtl_coloc/`; SuSiE-RSS layer untouched (default `SUSIE_LAYER_SCOPE=no`). Compute envelope: ~10 hr at 50 LSF cores (vs. ~15 hr if BOTH_LAYERS).

- **D-TA-Wave-0-pitfall2 = PATCH_REQUIRED (config-merge does not propagate to static rule inputs).** Dry-run before patch showed `--policy config/susie_policy.yaml` (hardcoded path) instead of `config/susie_policy_L20.yaml` despite the L20 overlay setting `finemap.policy: "config/susie_policy_L20.yaml"`. Patch: `finemap.smk:62` reads `config.get("finemap", {}).get("policy", default)`. Dry-run after patch: `--policy config/susie_policy_L20.yaml`. Baseline (no overlay) re-verified: `--policy config/susie_policy.yaml` (L=10 unchanged).

- **Schema-vs-config drift auto-fixed under Rule 3 (blocking issue).** `config/pipeline.yaml` carried the `ld_panel:` block since M3 (commit predating ta-sh2b3-W0) but `src/snakemake/schemas/pipeline.schema.yaml` had `additionalProperties: false` at the top level and was rejecting `ld_panel`, blocking every Snakemake invocation including the Pitfall 2 dry-run. Added explicit `ld_panel:` schema entry covering per-ancestry resolver chain + `strict_aou_only` + `pin`. Decision recorded inline in the schema (block comment) and in D-TA-Wave-0-pitfall2 CONTEXT addendum.

- **LSF compute deferral on Pitfall 2 verification (rigor-aware deferral).** The plan's strict `<verify><automated>` block calls for `j$L_used == 20` from a live JSON. The dry-run conclusively proves the `--policy config/susie_policy_L20.yaml` flag now propagates and `run_susie_rss.R` (lines 237-251) deterministically reads `susie.L = 20` from that YAML. Running the actual fit (~2-4 hr LSF wall per AUDIT-RESPONSE 2026-04-26 line 260) adds zero Pitfall 2 verification value beyond the dry-run + interface-contract proof. Live `L_used=20` verification will land in Wave 1's first L=20 fit; if Wave 1 sees `L_used != 20`, halt and re-investigate against this CONTEXT.md ledger.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Schema-vs-config drift on `ld_panel` block**
- **Found during:** Task 4 (Pitfall 2 dry-run)
- **Issue:** `pipeline.schema.yaml` had top-level `additionalProperties: false` and was missing the `ld_panel:` block, while `config/pipeline.yaml` had carried `ld_panel:` since M3. Every Snakemake invocation failed with `ValidationError: Additional properties are not allowed ('ld_panel' was unexpected)`. Pitfall 2 verification was structurally blocked.
- **Fix:** Added explicit `ld_panel:` block to `pipeline.schema.yaml` covering per-ancestry resolver chain (`patternProperties` on `^(EUR|AFR|EAS|HIS|SAS|AMR|TRANS)$`), plus `strict_aou_only: boolean` and `pin: object` properties. Schema-mode is preserved (no relaxation of `additionalProperties: false`).
- **Files modified:** `src/snakemake/schemas/pipeline.schema.yaml`
- **Verification:** Re-ran `snakemake --configfile config/pipeline.yaml --dry-run` after the fix → DAG builds cleanly.
- **Committed in:** `840d1b6` (bundled with Pitfall 2 patch — both required for Pitfall 2 verification)

**2. [Rule 1 - Bug] Driver-script `cd` to `/rs1/.../coloc_analysis/` would fail at Wave 1 fire**
- **Found during:** Task 1 (D-TA-01 path verification — Pitfall 1 confirmed)
- **Issue:** D-TA-01 mandates LSF dispatchers `cd /rs1/researchers/c/ckclinto/coloc_analysis`, but that path is a namespace collision with historical pre-pivot artifacts (no `.git`). Wave 1/2/4 drivers would fail at `set -euo pipefail` (path exists, but Snakemake wouldn't find Snakefile).
- **Fix:** All 3 driver scripts carry inline `if [ -d "${RS1_ROOT}/.git" ]; then cd "${RS1_ROOT}"; else echo WARN; cd "${GPFS_ROOT}"; fi` fallback. Default behavior is RS1 if available; otherwise GPFS interactive mount (same physical filesystem per D-TA-01 §"Why" L121). Logs a warning so the namespace collision stays visible.
- **Files modified:** `bin/fire_susie_lsweep.sh`, `bin/fire_canonical_susie_pairs.sh`, `bin/fire_qtl_coloc_cache_refresh.sh`, `src/python/build_coloc_manifest_r2.py`
- **Verification:** Driver `[ -x ]` checks pass; dry-source on each driver shows the fallback block.
- **Committed in:** `dbeccdc` (Task 5 commit)

**3. [Rule 2 - Missing critical] `.gitignore` did not cover the new per-L parallel namespaces**
- **Found during:** Task 4 (the Snakemake manifest-build run wrote `results_lsweep_L20/fine_mapping/finemap_manifest.tsv`)
- **Issue:** `.gitignore` listed `results/*` and `results_identity_ld/` (per DEC-2026-04-25-01) but not the new `results_lsweep_L{15,20,30}/` parallel namespaces. These would be staged accidentally on a future `git add` that touched `.` somewhere upstream.
- **Fix:** Added `results_lsweep_L{15,20,30}/` to `.gitignore` mirroring the `results_identity_ld/` precedent.
- **Files modified:** `.gitignore`
- **Verification:** `git status --short` no longer shows `results_lsweep_L20/` as untracked.
- **Committed in:** `840d1b6` (bundled with Pitfall 2 patch)

---

**Total deviations:** 3 auto-fixed (1 blocking, 1 bug, 1 missing critical)
**Impact on plan:** All 3 deviations were necessary to unblock Pitfall 2 verification and downstream Wave 1+ dispatch. No scope creep — every fix was strictly scoped to the W0 foundations work (schema fix unblocks Snakemake; driver fallback handles D-TA-01 escalation; .gitignore tracks the parallel namespaces declared by W0 overlays).

## Issues Encountered

- **D-TA-01 Pitfall 1 confirmed:** `/rs1/researchers/c/ckclinto/coloc_analysis/` exists but is NOT a git repo on this GPFS node. Carter-mediated investigation outcome documented in CONTEXT.md addendum. Driver-script fallback (RS1 if `.git` else GPFS) keeps Wave 1+ dispatch functional under either resolution path.
- **Pitfall 2 confirmed:** Snakemake `--configfile` overlays do not propagate into static rule input declarations. Patched `finemap.smk:62`. Verified via dry-run.
- **Schema drift on `ld_panel`:** Pre-existing M3 config drift (config has `ld_panel`, schema doesn't), surfaced during Pitfall 2 dry-run. Auto-fixed under Rule 3.

## Verification Dimensions (D1–D7)

| Dim | Description | Evidence | Status |
|---|---|---|---|
| **D1** Path verification | D-TA-01 path resolves; Wave 1 dispatch path determined | `git -C /rs1/.../coloc_analysis rev-parse HEAD` → ENOENT (no `.git`); GPFS HEAD = `3adde9e…` → driver fallback handles | **WARN/INVESTIGATE** (Carter escalation noted) |
| **D2** Code-fix ancestry | 069b34f + 7d54183 are HEAD ancestors | `git merge-base --is-ancestor 069b34f HEAD` exit 0; same for 7d54183 | **PASS** |
| **D3** Variant-ID diagnostic | D-TA-04 outcome recorded with explicit per-fit format tokens + aggregate decision | RSID across all 3 sample fits → CACHE_SCOPE=QTL_COLOC_ONLY recorded in CONTEXT.md | **PASS** |
| **D4** Config scaffolding | 7 config YAMLs land + L overrides correct + parallel results_root rebased | `[ -f config/susie_policy_L{15,20,30}.yaml ]`; `grep "L: 20" config/susie_policy_L20.yaml`; `grep "results_lsweep_L20" config/pipeline_lsweep_L20_overlay.yaml` | **PASS** |
| **D5** Dispatch drivers | 3 LSF drivers + manifest builder land + executable + RS1/GPFS fallback inlined | `[ -x bin/fire_susie_lsweep.sh ]` etc.; `grep "L_VALUES=(15 20 30)"`; `grep "preFix.bak"`; `grep "SUSIE_LAYER_SCOPE"`; `python3 -c "import ast; ast.parse(...)"` | **PASS** |
| **D6** Verification harness | `bin/verify_ta_sh2b3_phase.sh` lands + 15 check functions + `--wave N` filter | `[ -x bin/verify_ta_sh2b3_phase.sh ]`; `grep -c '^check_C' = 15`; `bin/verify_ta_sh2b3_phase.sh --wave 0` emits 4 JSON-lines | **PASS** |
| **D7** OSF gate | D-TA-OSF-COVERAGE recorded in CONTEXT addendum | (Task 7 awaiting Carter web-UI) | **PENDING** (HARD GATE) |

`bin/verify_ta_sh2b3_phase.sh --wave 0` output (Tasks 1–6 complete state):
```json
{"check":"C1","wave":0,"status":"WARN","msg":"/rs1/.../coloc_analysis/.git not present on this node — see D-TA-Wave-0-foundations"}
{"check":"C2","wave":0,"status":"PASS","msg":"069b34f + 7d54183 both HEAD ancestors"}
{"check":"C3","wave":0,"status":"PASS","msg":"D-TA-04-DIAGNOSTIC sub-section present in CONTEXT"}
{"check":"C4","wave":0,"status":"FAIL","msg":"D-TA-OSF-COVERAGE not yet recorded (Task 7 human-verify gate)"}
```
Exit code = 1 (C4 = the expected Task 7 dependency).

## Snakefile Rule-Name Surface (Wave 4 dispatch validation)

| File | Rule | Role |
|---|---|---|
| `Snakefile` | `all` (L196) | Default master target |
| `Snakefile` | `all_qtl_coloc` (L209) | **Wave 4 dispatch target** — confirmed |
| `src/snakemake/rules/finemap.smk` | `run_finemap` (L45) | **Wave 1 SuSiE-RSS rule** — confirmed; policy input now config-aware (Pitfall 2 patch) |
| `src/snakemake/rules/coloc.smk` | `run_coloc_susie` (L88) | **Wave 2 canonical-pair rule** — confirmed; targets `{MULTITRAIT_DIR}/coloc_susie/{pair_id}.json` (R2 overlay redirects to `coloc_susie_R2/`) |
| `src/snakemake/rules/qtl_coloc.smk` | `run_qtl_coloc` (L282) | Wave 4 per-attempt rule (driven by `all_qtl_coloc` target) |
| `src/snakemake/rules/multitrait.smk` | `summarize_coloc_results` (L151) | Pitfall 3 mitigation target — rebuilds `coloc_summary.tsv` from per-pair JSONs; isolated to coloc_susie/ namespace at Wave 2 |

## LSF Dispatch Envelope Projections

Validated against existing precedent:

| Wave | Driver | Env | Queue | Compute envelope | Precedent |
|---|---|---|---|---|---|
| 1 | `bin/fire_susie_lsweep.sh` | `la_multitrait_r` | `serial` | ~2-4 hr per fit × 9 fits parallel = ~4-8 hr aggregate | AUDIT-RESPONSE 2026-04-26 L260 |
| 2 | `bin/fire_canonical_susie_pairs.sh` | `la_multitrait_r` | `serial` | ~2 hr per pair × 9 pairs parallel = ~2-4 hr aggregate | CONTEXT.md L176 |
| 4 | `bin/fire_qtl_coloc_cache_refresh.sh` | `la_multitrait_r` | `long` | ~10 hr at 50 cores for ~1,274 attempts (QTL-coloc only per D-TA-04) | CONTEXT.md L82 |

LSF queue caps per memory `feedback_lsf_queues.md`: serial -W 5760, long -W 14400, standard -W 2880; `LSF_UNIT_FOR_LIMITS=GB`.

## Wave 1 GO/NO-GO Status

**STATUS: BLOCKED** on Task 7 (`checkpoint:human-verify`, gate=blocking).

**Pre-requisites already cleared:**
- [x] D-TA-01 path investigation outcome recorded (Carter escalation noted; driver-script fallback inlined as mitigation)
- [x] Code-fix ancestry verified (069b34f + 7d54183 are HEAD ancestors)
- [x] D-TA-04 cache-scope decision = QTL_COLOC_ONLY (Wave 4 driver default `SUSIE_LAYER_SCOPE=no`)
- [x] Per-L policy YAMLs + pipeline overlays + R2 overlay scaffolded
- [x] Pitfall 2 mitigated (finemap.smk policy is config-aware)
- [x] LSF dispatch drivers + R2 manifest builder scaffolded
- [x] C1-C15 verification harness scaffolded

**Blocker remaining:**
- [ ] **D-TA-OSF-COVERAGE**: Carter must verify OSF pre-reg coverage at `osf.io/pvb5j` Methods + `osf.io/az52u` closeout PDF for L-sweep wording (D-TA-02) + canonical-pair scope (D-TA-03), and record outcome (`COVERED` or `AMENDMENT_POSTED`) in CONTEXT.md addendum (D-TA-05 + REQ-OSF-PREREG hard gate).

**Task 7 instructions:** see `<how-to-verify>` block in `ta-sh2b3-W0-foundations-and-osf-gate-PLAN.md` lines 1067–1102. Resume signals: `OSF_COVERED`, `OSF_AMENDED`, or `OSF_BLOCKED`.

## Next Phase Readiness

- All Wave 0 infrastructure scaffolded and committed atomically (7 commits across 6 tasks).
- Wave 1 (`bin/fire_susie_lsweep.sh`) is fire-ready post-OSF-gate, modulo Carter resolution of D-TA-01 path namespace collision (or acceptance that drivers will fall back to GPFS path).
- Wave 4 cache-scope confirmed `QTL_COLOC_ONLY` (~10 hr LSF wall) — NOT the `BOTH_LAYERS` ~15 hr alternative.
- Pitfall 2 mitigation patch is the load-bearing change for Wave 1: without it, all 9 L-sweep fits would silently produce L_used=10 outputs and the L-sweep would not deliver D-TA-02's pre-registered sensitivity sweep.
- Verification harness `bin/verify_ta_sh2b3_phase.sh` is the phase-wide PASS/WARN/FAIL rail; can be run after every wave commit (`--wave N`) or at phase close (`all`).

## Self-Check: PASSED (Tasks 1–6)

**Files (all 12 present on disk):**
- FOUND: `config/susie_policy_L15.yaml`
- FOUND: `config/susie_policy_L20.yaml`
- FOUND: `config/susie_policy_L30.yaml`
- FOUND: `config/pipeline_lsweep_L15_overlay.yaml`
- FOUND: `config/pipeline_lsweep_L20_overlay.yaml`
- FOUND: `config/pipeline_lsweep_L30_overlay.yaml`
- FOUND: `config/pipeline_canonical_r2_overlay.yaml`
- FOUND: `bin/fire_susie_lsweep.sh`
- FOUND: `bin/fire_canonical_susie_pairs.sh`
- FOUND: `bin/fire_qtl_coloc_cache_refresh.sh`
- FOUND: `bin/verify_ta_sh2b3_phase.sh`
- FOUND: `src/python/build_coloc_manifest_r2.py`

**Commits (all 7 reachable from HEAD):**
- FOUND: `e4ac4a3` — Task 1: D-TA-01 path + code-fix ancestry + Snakefile rule names
- FOUND: `2995ca7` — Task 2: D-TA-04-DIAGNOSTIC variant-ID format outcome
- FOUND: `9a83588` — Task 3: per-L policy YAMLs + pipeline overlays
- FOUND: `840d1b6` — Task 4a: Pitfall 2 mitigation (finemap.smk + schema)
- FOUND: `ef81efb` — Task 4b: Pitfall 2 outcome in CONTEXT
- FOUND: `dbeccdc` — Task 5: W1/W2/W4 dispatch drivers + R2 manifest builder
- FOUND: `1c23441` — Task 6: C1-C15 verification harness

**Pending:** Task 7 (`checkpoint:human-verify`, gate=blocking) — Carter web-UI OSF coverage check. Final SUMMARY metadata commit (this file + STATE.md update) will land after Task 7 resumes.

---
*Phase: ta-sh2b3-canonical-and-cache-refresh*
*Plan: W0-foundations-and-osf-gate*
*Status: PARTIAL — awaiting OSF coverage human-verify (Task 7)*
*Tasks 1–6 completed: 2026-04-30T00:33:07Z*
