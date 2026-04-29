---
phase: ta-sh2b3-canonical-and-cache-refresh
slug: ta-sh2b3-canonical-and-cache-refresh
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase ta-sh2b3-canonical-and-cache-refresh — Validation Strategy

> Per-phase validation contract for Track A R2 (id-vs-ref-LD). Derived from RESEARCH.md `## Validation Architecture` (C1–C15).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash + Rscript + jq + grep — no `pytest` / `Rtest` harness for this phase scope |
| **Config file** | none (in-line per-task verification) |
| **Quick run command** | per-task — see Per-Task Verification Map below |
| **Full suite command** | `bin/verify_ta_sh2b3_phase.sh` (Wave 0 task scaffolds; runs all C1–C15 dimension checks) |
| **Estimated runtime** | <5 min for Wave 0–7 verification sweep (excluding LSF compute waves themselves) |
| **CI smoke (existing)** | `scripts/run_ci_smoke.sh` (REQ-SNAKEMAKE-CI; out-of-phase; Wave 7 SUMMARY notes if it ran clean) |

---

## Sampling Rate

- **After every task commit:** Run the targeted C-row check from the table below (the C-row matching the task).
- **After every wave merge:** Run all C-rows for that wave + the cumulative Stage-2 md5 invariant check (C12).
- **Before `/gsd-verify-work`:** Full C1–C15 sweep + manuscript-anchor preservation re-verify (C13) + bundle integrity check (C14) must be green.
- **Max feedback latency:** ~30 s for unit checks; LSF compute waves (1, 2, 4) report status via `bjobs` polling (~10 hr wall on `serial` for Wave 4).

---

## Per-Task Verification Map

| Claim | Wave | Requirement | Test Type | Automated Command | Expected Output | Status |
|-------|------|-------------|-----------|-------------------|-----------------|--------|
| **C1** D-TA-01 path resolves on login02 | 0 | REQ-PATH-PARAMETERIZATION | smoke | `[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ] && cd /rs1/researchers/c/ckclinto/coloc_analysis && git rev-parse HEAD` | matches GPFS HEAD | ⬜ pending |
| **C2** Code fixes are HEAD ancestors | 0 | REQ-SNAKEMAKE-CI | unit | `git merge-base --is-ancestor 069b34f HEAD && git merge-base --is-ancestor 7d54183 HEAD` | exit 0 | ⬜ pending (verified during research 2026-04-29; re-verify at execute time) |
| **C3** Variant-ID format diagnostic recorded | 0 | REQ-PATH-PARAMETERIZATION | unit | `Rscript -e` snippet on `.fit.rds` `colnames(fit$alpha)` for 3 sample fits → record in CONTEXT addendum as `D-TA-04-DIAGNOSTIC-XX` | one of `RSID` / `CHRPOS` / `MIXED` per fit; aggregate decision recorded | ⬜ pending |
| **C4** OSF pre-reg coverage verified | 0 | REQ-OSF-PREREG | smoke + manual | Carter web-UI grep at osf.io/pvb5j Methods + osf.io/az52u closeout PDF for: "L-sweep", "{15, 20, 30}", "L = 20", "canonical pair", "BMI-HTN", "HTN-stroke" | covered → Wave 1 cleared; uncovered → amendment posted before Wave 1 | ⬜ pending |
| **C5** SuSiE-RSS converges at chosen L for SH2B3 EUR BMI/HTN/stroke | 1 | REQ-SUSIE-RSS-POLICY | unit | `Rscript` convergence verification on per-fit JSON: `n_CS < L_used` AND `L_saturated == FALSE` AND `convergence_status` matches `^converged_` | per-fit JSON shows `n_CS < L_used` with `L_saturated: false` and `convergence_status: "converged_*"` | ⬜ pending |
| **C6** BMI–HTN reference-LD coloc.susie produced | 2 | REQ-PP.H4-THRESHOLD-SWEEP | unit | `jq '.summary."PP.H4.abf"' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json` | numeric in [0, 1]; finite | ⬜ pending |
| **C7** All 9 SH2B3 EUR new pairs produced | 2 | REQ-PP.H4-THRESHOLD-SWEEP | unit | `ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json \| wc -l` | exactly 9 | ⬜ pending |
| **C8** D-TA-WAVE3-OUTCOME branch recorded | 3 | REQ-PP.H4-THRESHOLD-SWEEP | manual | `grep "D-TA-WAVE3-OUTCOME-" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` | matches one of `BRANCH_A_COLLAPSE`, `BRANCH_B_PARTIAL`, `BRANCH_C_SURVIVE` | ⬜ pending |
| **C9** Cache refresh produces materially different numerics | 4 | REQ-SNAKEMAKE-CI | unit | `grep -h '"status"' results/qtl_coloc/*.json \| grep -c '"too_few_snps"'` | ≤ 200 (PASS); FAIL ≈ 1000 → Wave 4.5 SuSiE-RSS layer fallback fires | ⬜ pending |
| **C10** Wave-5 aggregator outputs refreshed | 5 | REQ-SNAKEMAKE-CI | unit | `stat -c '%Y' results/track_a_aggregations/*.tsv` newer than median `stat -c '%Y' results/qtl_coloc/*.json` | TSV mtime > JSON mtime; values consistent with `aggregate_qtl_coloc.py` logic | ⬜ pending |
| **C11** TRACK-A-FROZEN-NUMBERS LIVE block updated | 5 | REQ-OSF-PREREG | unit | `grep -A 20 "Stage 2 fine-mapping yield" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | block reflects D-TA-Wave1-headline outcome (51/96 OR recomputed numerator) | ⬜ pending |
| **C12** Stage 2 md5 invariant preserved on non-target files | 7 | REQ-SNAKEMAKE-CI | unit | `md5sum` diff per-file pre vs post phase against curated whitelist of intentionally rewritten files | per-file md5 diff matches whitelist exactly | ⬜ pending |
| **C13** Honest-framing-lock anchors preserved byte-identical at L148/L295/L220/L90 | 6 | REQ-OSF-PREREG | unit | `grep -nF "<honest-framing-lock anchor phrase>" docs/manuscript/id-vs-ref-LD.md` for each of the 4 anchor phrases | each of 4 anchor phrases returns ≥ 1 hit; line numbers may shift but content exact match required | ⬜ pending |
| **C14** Bundle is reproducible and clean | 7 | REQ-PUBLIC-DATA-ONLY | unit + smoke | `unzip -t <bundle.zip>` AND `sha256sum <bundle.zip>` | exit 0 + sha256 hash captured in `bundle_manifest.tsv` | ⬜ pending |
| **C15** OSF deviation log entry added | 7 | REQ-OSF-PREREG | unit | `grep -E "Cache invalidation\|2026-04-(28\|29)" .planning/amendments/osf_deviations.md` | ≥ 1 entry block | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

The following Wave 0 tasks scaffold the verification infrastructure used by C1–C15:

- [ ] `bin/verify_ta_sh2b3_phase.sh` — runs all C1–C15 checks; emits PASS/WARN/FAIL JSON per dimension D1–D7
- [ ] `config/susie_policy_L15.yaml`, `config/susie_policy_L20.yaml`, `config/susie_policy_L30.yaml` — three policy YAML overlays for Wave 1 (per-L override; pattern from existing `config/susie_policy.yaml`)
- [ ] `config/pipeline_lsweep_L15_overlay.yaml`, `_L20_overlay.yaml`, `_L30_overlay.yaml` — three pipeline overlays that point `finemap.policy` at the per-L susie YAML AND rebase `paths.results_root` to `results_lsweep_L{15,20,30}/` (verify Snakemake config-merge propagation per RESEARCH.md Pitfall 2 in a Wave-0 single-locus dry-run)
- [ ] `config/pipeline_canonical_r2_overlay.yaml` — Wave 2 overlay that rebases `MULTITRAIT_DIR` to `results/multitrait/coloc_susie_R2/`
- [ ] `bin/fire_susie_lsweep.sh` — Wave 1 driver (mirror `scripts/fire_identity_ld_rerun.sh` pattern; LSF dispatch on `serial` queue with `la_multitrait_r` env)
- [ ] `bin/fire_canonical_susie_pairs.sh` — Wave 2 driver (mirror `bin/fire_phase2_stage2_refit.sh` pattern; 9 bsub jobs at primary-result-L from Wave 1)
- [ ] `bin/fire_qtl_coloc_cache_refresh.sh` — Wave 4 driver (cache backup `mv` + Snakemake re-fire `--use-conda -j 50`)
- [ ] `src/python/build_coloc_manifest_r2.py` — manifest builder for the 9-row R2 SH2B3 EUR canonical-pair manifest (filtered slice of `create_coloc_manifest.py` output)
- [ ] `.planning/amendments/osf_deviations.md` — Wave 7 task creates (file does not yet exist)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| OSF pre-reg coverage check (C4 / D-TA-05) | REQ-OSF-PREREG | OSF portal access requires Carter's web-UI session; greppable phrases live in PDFs not in the repo tree | Carter opens osf.io/pvb5j Methods + osf.io/az52u closeout PDF; greps for the 6 phrases listed in C4; records outcome as `D-TA-OSF-COVERAGE-XX` in CONTEXT.md addendum |
| OSF amendment posting (if C4 returns uncovered) | REQ-OSF-PREREG | Amendment authoring + posting requires Carter's web-UI workflow on the OSF portal | Carter posts amendment as addendum to existing osf.io/az52u closeout PDF (~30 min); Wave 1 hard-blocked until amendment confirmed live |
| D-TA-WAVE3-OUTCOME branch selection (C8) | REQ-PP.H4-THRESHOLD-SWEEP | Wave-3 `checkpoint:human-verify` gate is mandatory; Carter selects branch (a/b/c) for BMI–HTN canonical pair from observed disk numbers | After Wave 2 completes, executor presents BMI–HTN PP.H4 + HTN–stroke PP.H4 + 7 other new pairs' PP.H4 from Wave 2 outputs; Carter selects branch; decision recorded as `D-TA-WAVE3-OUTCOME-XX` in CONTEXT.md addendum |
| Wave 7 OSF deviation-log post (C15 follow-up) | REQ-OSF-PREREG | Posting the deviation entry on the OSF portal closeout PDF (vs only the in-tree `.planning/amendments/osf_deviations.md`) requires Carter's web-UI session | Carter optionally appends the cache-invalidation deviation entry to osf.io/az52u closeout PDF; in-tree entry is the canonical source |

---

## Validation Sign-Off

- [ ] All C1–C15 claims map to a wave-specific task with verifiable acceptance criteria
- [ ] Sampling continuity: every wave has at least one C-row check (C1–C4 → Wave 0, C5 → Wave 1, C6–C7 → Wave 2, C8 → Wave 3, C9 → Wave 4, C10–C11 → Wave 5, C13 → Wave 6, C12 + C14 + C15 → Wave 7)
- [ ] Wave 0 covers all MISSING references (verify scripts, policy YAMLs, drivers, manifest builder, deviation-log file)
- [ ] No watch-mode flags; all checks exit-code-driven for `verify_ta_sh2b3_phase.sh`
- [ ] Feedback latency < 30 s for unit checks (LSF compute waves are independent — `bjobs` polling)
- [ ] `nyquist_compliant: true` set in frontmatter once Wave 0 scaffold lands

**Approval:** pending (Wave 0 will set `wave_0_complete: true` and flip `nyquist_compliant: true` after `bin/verify_ta_sh2b3_phase.sh` lands and runs clean against Wave 0 outputs)
