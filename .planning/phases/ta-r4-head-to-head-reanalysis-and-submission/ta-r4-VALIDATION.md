---
phase: ta-r4
slug: ta-r4-head-to-head-reanalysis-and-submission
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-10-21
revised: 2026-10-21
---

# Phase ta-r4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `ta-r4-RESEARCH.md` §Validation Architecture. Per-task map covers all 80 tasks of the 25 plans
> (revised after plan-check iterations 1 and 2).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 (smoke_dev Python 3.11) driving R via `Rscript` (r_coloc env); testthat for pure-R units |
| **Config file** | existing `tests/conftest.py`; new `tests/ta_r4/conftest.py` (W0a; registers the `r4_heavy` marker) |
| **Quick run command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -x -q -m "not r4_heavy"` |
| **Heavy run command (per wave)** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m r4_heavy -rs` |
| **Full suite command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q` |
| **Estimated runtime** | quick < 120 s (measured and recorded at every wave-close); heavy minutes (Snakemake, frozen-script e2e, live gates); full ≈ 15–20 min |

`r4_heavy` = any test that runs `$SMK`, runs the frozen `run_susie_rss.R`, or reads `data/r4/results/`.

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` command (always present; heavy tests run when named explicitly) + the quick run
- **After every plan wave:** quick + heavy + full suite; ids/passed/skipped/failed recorded against the W0a baseline in `ta-r4-LOG.md` (INDEX §C)
- **Before `/gsd-verify-work`:** full suite green, all live gates green with 0 skips, every negative control observed RED once
- **Max feedback latency:** 120 seconds (quick run)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement / Decision | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|------------------------|------------|-----------------|-----------|-------------------|-------------|--------|
| W0a-T1 | W0a | 1 | D-11, REQ-PATH-PARAMETERIZATION, REQ-PUBLIC-DATA-ONLY | T-r4-W0a-01/02 | survivor sha256 == source | unit + negative controls | `$PY -m pytest tests/ta_r4/test_storage_on_rs1.py -q` | ❌ W0a | ⬜ pending |
| W0a-T2 | W0a | 1 | D-14, D-16 (tag), baseline | T-r4-W0a-04 | shared conda cache untouched | byte-compare + count reconcile | `cmp <(git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis show c2dfb08^:envs/qtl_processing.yml) envs/qtl_processing.yml && echo IDENTICAL` | ✅ (cmp) | ⬜ pending |
| W0a-T3 | W0a | 1 | D-06/D-17/D-19 DEC entries | T-r4-W0a-05 | append-only DECISIONS | git diff + suite join | `git log -1 --format=%s && git diff HEAD~1 --stat -- .planning/DECISIONS.md \| tail -1 && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W0b1-T1 | W0b1 | 2 | D-01, D-14, D-15, B4 | T-r4-W0b1-02/03/05 | stage from code; globs from ARMS | unit + negative controls | `$PY -m pytest tests/ta_r4/test_overlay_semantics.py -q` | ❌ W0b1 | ⬜ pending |
| W0b1-T2 | W0b1 | 2 | B1 sign-off protocol, REQ-OSF-PREREG | T-r4-W0b1-01/04 | bare "approved" rejected; locked config needs sign-off | unit + conditional sentinels | `$PY -m pytest tests/ta_r4/test_signoff.py tests/ta_r4/test_signoffs.py -q` | ❌ W0b1 | ⬜ pending |
| W0b1-T3 | W0b1 | 2 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W0b2-T1 | W0b2 | 3 | D-07, D-24, REQ-NEGATIVE-CONTROLS | T-r4-W0b2-05 | outcome-independent manifest | unit + determinism + negative controls | `$PY -m pytest tests/ta_r4/test_null_windows.py tests/ta_r4/test_pair_manifest.py -q` | ❌ W0b2 | ⬜ pending |
| W0b2-T2 | W0b2 | 3 | D-05/D-27, B5 | T-r4-W0b2-01/02/03 | production refuses without sentinel + receipt; no bypass; offline in jobs | unit (fake fetch) + AST/env/signature | `$PY -m pytest tests/ta_r4/test_lock_gate.py -q -m "not r4_heavy"` | ❌ W0b2 | ⬜ pending |
| W0b2-T3 | W0b2 | 3 | D-04/D-15, B3, REQ-SNAKEMAKE-CI | T-r4-W0b2-04/06 | fixture-repo refusal; isolation | dry-run on fixture repo (r4_heavy) | `$PY -m pytest tests/ta_r4/test_lock_gate.py tests/ta_r4/test_track_b_isolation.py -q -rs` | ❌ W0b2 | ⬜ pending |
| W0b2-T4 | W0b2 | 3 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W0c-T1 | W0c | 4 | D-13, B4/W1 | T-r4-W0c-01/02 | any identity shape fails the job | unit + live gate (r4_heavy) | `$PY -m pytest tests/ta_r4/test_no_silent_identity.py -q` | ❌ W0c | ⬜ pending |
| W0c-T2 | W0c | 4 | D-01, D-13, D-28 | T-r4-W0c-03/04 | frozen script armed only by flags | R e2e (r4_heavy) + live gate | `$PY -m pytest tests/ta_r4/test_frozen_script_armed_e2e.py tests/ta_r4/test_arm_variant_sets_identical.py tests/m3/test_source_freeze_pins.py -q` | ❌ W0c | ⬜ pending |
| W0c-T3 | W0c | 4 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W0d-T1 | W0d | 5 | D-01, D-02, D-21, B4 | T-r4-W0d-01/02/03 | explicit priors; labelled fallback | R unit (r4_heavy) + live gates | `$PY -m pytest tests/ta_r4/test_coloc_pair_r4.py tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q -rs` | ❌ W0d | ⬜ pending |
| W0d-T2 | W0d | 5 | REQ-SNAKEMAKE-CI, D-05 | T-r4-W0d-01 | production dry-run refuses; toy run validates | Snakemake --use-conda e2e (r4_heavy) | `$PY -m pytest tests/ta_r4/test_snakemake_toy_e2e.py -q -rs` | ❌ W0d | ⬜ pending |
| W0d-T3 | W0d | 5 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W1-T1 | W1 | 6 | D-18 | T-r4-W1-02 | input sha256 pinned | unit + negative control | `$PY -m pytest tests/ta_r4/test_bmi_allele_restoration.py -q` | ❌ W1 | ⬜ pending |
| W1-T2 | W1 | 6 | D-06 unit 2, D-15 | T-r4-W1-01 | flag-off identical() | R unit + plink known answer | `$PY -m pytest tests/ta_r4/test_plink_ld_to_rds_ref_alt.py tests/m3/test_ld_npz_to_rds.py tests/m3/test_source_freeze_pins.py -q` | ❌ W1 | ⬜ pending |
| W1-T3 | W1 | 6 | D-06 unit 3, D-15 | T-r4-W1-01/03 | flag-off parsed-JSON equality | R unit + existing m3/phase2 guards | `$PY -m pytest tests/ta_r4/test_qtl_orient.py tests/m3/test_qtl_coloc_allele_join.py tests/m3/test_qtl_coloc_ld_resolution.py tests/phase2/test_run_qtl_coloc.py -q` | ❌ W1 | ⬜ pending |
| W1-T4 | W1 | 6 | D-15, §C | T-r4-W1-01 | 0 outcome changes in Track B suites | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W2a-T1 | W2a | 7 | D-10, D-25, REQ-PUBLIC-DATA-ONLY | T-r4-W2a-01 | md5/size/magic before extraction | unit + checksum | `$PY -m pytest tests/ta_r4/test_fetch_verified.py -q && md5sum /rs1/researchers/c/ckclinto/coloc_analysis/ta_r4/downloads/ldsc_1000G_Phase3_plinkfiles/1000G_Phase3_plin...` | ❌ W2a | ⬜ pending |
| W2a-T2 | W2a | 7 | D-03, D-10, D-12a | T-r4-W2a-03 | no Track B write | data counts | `ls data/r4/ld/EUR_1kg_r4/*.rds \| wc -l && ls data/r4/ld/EUR_identity_r4/*.rds \| wc -l && ls data/r4/ld/legacy_repro/EUR/*.rds \| wc -l` | ✅ (ls) | ⬜ pending |
| W2a-T3 | W2a | 7 | D-12a, D-25 | T-r4-W2a-02/04 | manifest md5 == disk; blockwise checks | live gate (r4_heavy) | `$PY -m pytest tests/ta_r4/test_known_answer_panels.py -q -rs` | ❌ W2a | ⬜ pending |
| W2a-T4 | W2a | 7 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W2b-T1 | W2b | 8 | D-20 | T-r4-W2b-04 | plink-only AFR panels | data counts | `wc -l < data/r4/ref/samples/AFR661.samples && wc -l < data/r4/ref/samples/AFR504.samples && ls data/r4/ld/AFR661_1kg_r4/*.rds \| wc -l && ls data/r4/ld/AFR504_1kg_r4/*...` | ✅ (wc/ls) | ⬜ pending |
| W2b-T2 | W2b | 8 | Pitfall 10, W2 orientation | T-r4-W2b-01/02 | triangle/diag convention; D·R·D known answer | unit + live gate (r4_heavy) | `$PY -m pytest tests/ta_r4/test_ukb_tile_loader.py tests/ta_r4/test_ukb_tile_triangle.py -q -rs` | ❌ W2b | ⬜ pending |
| W2b-T3 | W2b | 8 | D-03, D-04, E6, D-24 | T-r4-W2b-03 | isolated UKB dirs; isect frames identical | data counts + suite | `for d in EUR_ukb337k_r4 EUR_ukb337k_isect_r4 EUR_1kg_isect_r4; do ls data/r4/ld/$d/*.rds \| wc -l; done && $PY -m pytest tests/ta_r4 -q` | ✅ (ls) | ⬜ pending |
| W2c-T1 | W2c | 9 | D-10, REQ-PUBLIC-DATA-ONLY | T-r4-W2c-01 | Content-Length + gzip -t + tabix | manifest reconcile (awk) | `awk -F'\t' 'NR>1{n++; if($8!="true"\|\|$9!="true") bad++} END{print n, bad+0}' $P/manifests/qtl_downloads_sha256.tsv` | ✅ (awk) | ⬜ pending |
| W2c-T2 | W2c | 9 | D-07, W6 | T-r4-W2c-02/04 | no status/tier column; scope = pure filter | unit + determinism | `$PY -m pytest tests/ta_r4/test_qtl_manifest.py -q` | ❌ W2c | ⬜ pending |
| W2c-T3 | W2c | 9 | D-25, §C | — | N/A | commit check | `git log -1 --format=%s && git status --porcelain -- $P/ta-r4-W2-REVIEW-PACKET.md config/ta_r4/qtl_manifest.tsv` | ✅ | ⬜ pending |
| W2c-T4 | W2c | 9 | D-12a/D-25, B1 | T-r4-W2c-03 | carter-approved token required | human-action; sign-off verify + test_signoffs | `(src/python) $PY -m ta_r4.signoff verify W2c-T4 && cd ../.. && $PY -m pytest tests/ta_r4/test_signoffs.py -q && ! grep -q UNRESOLVED config/ta_r4/trait_manifest.tsv &&...` | ❌ W0b1 (signoff.py) | ⬜ pending |
| W2d-T1 | W2d | 10 | D-03/D-04, W3 | T-r4-W2d-01/02/03 | applies only the signed-off choice | arms assertion + overlay/isolation tests | `$PY -c "import sys,yaml;sys.path.insert(0,'src/python');from ta_r4.arms import ARMS;d=yaml.safe_load(open('config/ta_r4/review_decisions.yaml'));exp={'native':'EUR_ukb...` | ✅ (W0b1 tests) | ⬜ pending |
| W2d-T2 | W2d | 10 | D-07, W6 | T-r4-W2d-04 | scope fixed pre-lock | unit + row-count reconcile | `$PY -m pytest tests/ta_r4/test_qtl_manifest.py -q && awk 'NR>1' config/ta_r4/qtl_manifest.tsv \| wc -l` | ✅ (W2c test) | ⬜ pending |
| W2d-T3 | W2d | 10 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W3a-T1 | W3a | 11 | D-12b | T-r4-W3a-01 | legacy code sha256-pinned | dry-run counts + e2e (r4_heavy) | `bash bin/r4_fire.sh repro repro_routeC -n --quiet 2>&1 \| tail -5 && $PY -m pytest tests/ta_r4/test_frozen_script_armed_e2e.py tests/ta_r4/test_snakemake_toy_e2e.py -q` | ✅ (W0c/W0d tests) | ⬜ pending |
| W3a-T2 | W3a | 11 | D-12b | T-r4-W3a-03 | infra retries recorded | output counts | `for a in repro_routeC repro_routeL repro_k2d_routeC repro_k2d_routeL; do echo $a $(ls data/r4/results/$a/fine_mapping/susie/*.json 2>/dev/null \| wc -l); done` | ✅ (ls) | ⬜ pending |
| W3a-T3 | W3a | 11 | D-12b, §B.10 | T-r4-W3a-02 | table built from disk; no equality asserted | unit + live test (r4_heavy) | `$PY -m pytest tests/ta_r4/test_known_answer_repro.py -q -rs` | ❌ W3a | ⬜ pending |
| W3b-T1 | W3b | 12 | D-17 | T-r4-W3b-01 | commits extracted with sha256 | output counts | `ls data/r4/results/repro_sh2b3_r2/coloc/*.json \| wc -l && ls data/r4/results/repro_sh2b3_L10/coloc/*.json \| wc -l` | ✅ (ls) | ⬜ pending |
| W3b-T2 | W3b | 12 | D-17, §B.10 | T-r4-W3b-02 | 18-row table from disk | unit + live test (r4_heavy) | `$PY -m pytest tests/ta_r4/test_sh2b3_known_answer.py -q -rs` | ❌ W3b | ⬜ pending |
| W3b-T3 | W3b | 12 | D-12/D-17, B1 | T-r4-W3b-03 | carter-approved token required | human-action; sign-off verify | `(src/python) $PY -m ta_r4.signoff verify W3b-T3 && echo SIGNED_OFF` | ❌ W0b1 (signoff.py) | ⬜ pending |
| W3c-T1 | W3c | 13 | D-23 | T-r4-W3c-01/02/03 | harness == frozen fit; sim gated | unit + R identity (r4_heavy) | `$PY -m pytest tests/ta_r4/test_simulation_harness.py tests/ta_r4/test_coloc_pair_r4.py tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q` | ❌ W3c | ⬜ pending |
| W3c-T2 | W3c | 13 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W3d-T1 | W3d | 14 | D-26, D-02, REQ-PP.H4-THRESHOLD-SWEEP, W5, iteration-2 blocker | T-r4-W3d-01/02/03/05 | confirmatory set + categories from yaml; NC/repro perturbation leaves branch unchanged | unit (hand-computed) + negative controls | `$PY -m pytest tests/ta_r4/test_estimands.py tests/ta_r4/test_contrast_stats.py tests/ta_r4/test_branch_classifier.py tests/ta_r4/test_cs_cross_purity.py -q` | ❌ W3d | ⬜ pending |
| W3d-T2 | W3d | 14 | B2, D-07 | T-r4-W3d-04 | exact coverage, pre-lock | unit + negative control | `$PY -m pytest tests/ta_r4/test_coloc_coverage.py -q` | ❌ W3d | ⬜ pending |
| W3d-T3 | W3d | 14 | D-26, iteration-2 blocker, B4 | T-r4-W3d-05 | aggregation frozen pre-lock; NC rows never classify | unit (fixture, ast) + negative controls | `$PY -m pytest tests/ta_r4/test_run_aggregation.py -q` | ❌ W3d | ⬜ pending |
| W3d-T4 | W3d | 14 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W3e-T1 | W3e | 15 | D-07, D-10 | T-r4-W3e-01 | harmonized counts reconcile | data counts | `find data/r4/qtl/harmonized -name '*.harmonized.tsv.gz' \| wc -l && cut -f1,5,7,8 config/ta_r4/qtl_manifest.tsv \| tail -n +2 \| awk -F'\t' '{print $2"\|"$3"\|"$4}' \|...` | ✅ (find/cut) | ⬜ pending |
| W3e-T2 | W3e | 15 | D-06, D-22, D-02 | T-r4-W3e-01/02/03 | coverage per group; legacy argv exact; gated | unit + fixture-repo dry-run (r4_heavy) | `$PY -m pytest tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_coloc_pair_r4.py tests/phase2/test_run_qtl_coloc.py -q` | ❌ W3e | ⬜ pending |
| W3e-T3 | W3e | 15 | §C | — | N/A | QUICK + HEAVY + suite join | `$PY -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W4a-T1 | W4a | 16 | D-05, D-18/D-19/D-24/D-25, W4 | T-r4-W4a-01/02 | whole-extract framing + internal-content scans | unit + negative controls | `$PY -m pytest tests/ta_r4/test_amendment_text.py -q -rs` | ❌ W4a | ⬜ pending |
| W4a-T2 | W4a | 16 | D-05, brief-blind review | T-r4-W4a-03 | findings == dispositions | text test + row count | `grep -c "^\|" $P/ta-r4-W4-AMENDMENT-REVIEW-as-received.md && $PY -m pytest tests/ta_r4/test_amendment_text.py -q && git status --porcelain -- .planning/amendments/osf-...` | ✅ (W4a test) | ⬜ pending |
| W4a-T3 | W4a | 16 | D-26, B1 | T-r4-W4a-04 | carter-approved + all lock keys | human-action; sign-off verify + DEC count | `(src/python) $PY -m ta_r4.signoff verify W4a-T3 && cd ../.. && grep -c "ta-r4-prereg-locks" .planning/DECISIONS.md` | ❌ W0b1 (signoff.py) | ⬜ pending |
| W4b-T1 | W4b | 17 | D-26, B1 sentinel | T-r4-W4b-02 | locked configs == sign-off | test_signoffs (lock sentinel live) | `$PY -c "import yaml;print([yaml.safe_load(open(f'config/ta_r4/{n}.yaml'))['locked'] for n in ('coloc_priors','decision_rules','simulation')])" && $PY -m pytest tests/t...` | ✅ (W0b1 test) | ⬜ pending |
| W4b-T2 | W4b | 17 | D-05/D-27, W4 | T-r4-W4b-03 | PUBLIC == extract(FINAL); gate closed | text test + gate CLI exit 1 | `$PY -m pytest tests/ta_r4/test_amendment_text.py -q -rs && cd src/python && $PY -m ta_r4.r4_lock_gate check --stage production; test $? -ne 0 && echo GATE_CLOSED` | ✅ (W4a test, W0b2 gate) | ⬜ pending |
| W4b-T3 | W4b | 17 | D-05/D-27, B1, B5 | T-r4-W4b-01/04 | token (lock_sha) + offline lock gate | human-action; sign-off verify + gate CLI exit 0 | `(src/python) $PY -m ta_r4.signoff verify W4b-T3 && $PY -m ta_r4.r4_lock_gate check --stage production && echo GATE_OPEN` | ✅ (W0b1/W0b2) | ⬜ pending |
| W5a-T1 | W5a | 18 | D-05, B3, B5 | T-r4-W5a-01 | gate open; code == lock commit A | gate CLI + gate-probe dry-run | `(src/python) $PY -m ta_r4.r4_lock_gate check --stage production && cd ../.. && bash bin/r4_fire.sh producti...` | ✅ (W0b2) | ⬜ pending |
| W5a-T2 | W5a | 18 | D-01, D-03, D-07, D-24 | T-r4-W5a-02/03 | validator in every job | output counts | `for a in A3_1kg A2_identity A3_ukb A3_ukb_isect A3_1kg_isect; do echo $a $(ls data/r4/results/$a/fine_mapping/susie/*.json \| wc -l); done` | ✅ (ls) | ⬜ pending |
| W5a-T3 | W5a | 18 | D-13, D-01 | T-r4-W5a-02 | 0 skips on live gates | live gates (r4_heavy) | `$PY -m pytest tests/ta_r4/test_no_silent_identity.py tests/ta_r4/test_arm_variant_sets_identical.py -q -rs 2>&1 \| tail -3` | ✅ (W0c tests) | ⬜ pending |
| W5b-T1 | W5b | 19 | D-01, D-07, D-21, B2 | T-r4-W5b-01/04 | exact coverage 4060 | coverage CLI | `(src/python) $PY -m ta_r4.coloc_coverage --ancestry EUR --repo ../..` | ✅ (W3d tool) | ⬜ pending |
| W5b-T2 | W5b | 19 | D-02, REQ-NEGATIVE-CONTROLS | T-r4-W5b-02/03 | 0 skips; counts only | live gates (r4_heavy) + manifest count | `$PY -m pytest tests/ta_r4/test_fallback_labelled.py tests/ta_r4/test_priors_constant.py -q -rs 2>&1 \| tail -3 && awk 'NR>1' $P/manifests/coloc_production_EUR_sha256.t...` | ✅ (W0d tests) | ⬜ pending |
| W5c-T1 | W5c | 20 | D-20, D-13 | T-r4-W5c-02 | validator in every job | output counts + live gates | `for a in AFR661_A3 AFR661_A2 AFR504_A3; do echo $a $(ls data/r4/results/$a/fine_mapping/susie/*.json \| wc -l); done` | ✅ (W0c tests) | ⬜ pending |
| W5c-T2 | W5c | 20 | D-20, D-21 | T-r4-W5c-02 | exact coverage 300 | coverage CLI | `(src/python) $PY -m ta_r4.coloc_coverage --ancestry AFR --repo ../..` | ✅ (W3d tool) | ⬜ pending |
| W5c-T3 | W5c | 20 | D-23 | T-r4-W5c-01 | locked config; no reps override | row-count rule | `ls data/r4/results/sim/*.tsv \| wc -l` | ✅ (ls) | ⬜ pending |
| W5c-T4 | W5c | 20 | §C | — | N/A | fsck + commit check | `git fsck --connectivity-only 2>&1 \| tail -2 && git status --porcelain -- $P/manifests` | ✅ | ⬜ pending |
| W6-T1 | W6 | 21 | D-06, D-07, D-22 | T-r4-W6-01/03 | per-group + global coverage | output counts | `for a in QTL_A3 QTL_A2 QTL_legacy; do echo $a $(find data/r4/results/$a/qtl -name '*.json' \| wc -l); done && awk 'NR>1' config/ta_r4/qtl_manifest.tsv \| wc -l` | ✅ (find) | ⬜ pending |
| W6-T2 | W6 | 21 | D-06, D-02 | T-r4-W6-02 | orientation counters reconcile | reconciliation script + listing | `ls data/r4/results/QTL_A3/qtl_tiers* data/r4/results/QTL_A2/qtl_tiers* data/r4/results/QTL_legacy/qtl_tiers* 2>&1 \| head -12` | ✅ | ⬜ pending |
| W6-T3 | W6 | 21 | §C | — | N/A | fsck + commit check | `git fsck --connectivity-only 2>&1 \| tail -2 && git log -1 --format=%s` | ✅ | ⬜ pending |
| W7-T1 | W7 | 22 | D-26, D-02, B4 | T-r4-W7-01/02/04 | empty lock diff; frozen code only; FINAL labels | frozen tests + table count + FINAL label check | `$PY -m pytest tests/ta_r4/test_run_aggregation.py tests/ta_r4/test_contrast_stats.py -q && ls docs/manuscript/r4/tables/*.tsv \| wc -l && grep -L 'status=FINAL' docs/m...` | ✅ (W3d tests) | ⬜ pending |
| W7-T2 | W7 | 22 | D-23, D-24, REQ-NEGATIVE-CONTROLS | T-r4-W7-03 | figures from committed tables | listing + commit check | `ls docs/manuscript/r4/figures/ && git status --porcelain -- docs/manuscript/r4` | ✅ (ls) | ⬜ pending |
| W7-T3 | W7 | 22 | B1 | T-r4-W7-05 | carter-approved token required | human-action; sign-off verify | `(src/python) $PY -m ta_r4.signoff verify W7-T3 && echo SIGNED_OFF` | ❌ W0b1 (signoff.py) | ⬜ pending |
| W8a-T1 | W8a | 23 | D-08 | T-r4-W8a-01 | FINAL tables only; unresolved placeholder fails | unit + negative control | `$PY -m pytest tests/ta_r4/test_render_manuscript.py -q` | ❌ W8a | ⬜ pending |
| W8a-T2 | W8a | 23 | D-08, D-17/D-18/D-19/D-24/D-25, W11 | T-r4-W8a-02/03 | framing/provenance scans; old-draft check acceptance-only | text checks + negative control | `$PY -m pytest tests/ta_r4/test_manuscript_r4.py tests/ta_r4/test_render_manuscript.py -q` | ❌ W8a | ⬜ pending |
| W8a-T3 | W8a | 23 | §C | — | N/A | porcelain + fsck | `git status --porcelain -- docs/manuscript && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W8b-T1 | W8b | 24 | D-08 | T-r4-W8b-02 | verbatim banking (sha256) | header + sha256 equality | `head -3 $P/ta-r4-W8-MANUSCRIPT-REVIEW-as-received.md` | ✅ (head) | ⬜ pending |
| W8b-T2 | W8b | 24 | D-08 | T-r4-W8b-01/03 | template-only fixes; re-render | W8a checks | `$PY -m pytest tests/ta_r4/test_manuscript_r4.py tests/ta_r4/test_render_manuscript.py -q` | ✅ (W8a tests) | ⬜ pending |
| W8b-T3 | W8b | 24 | B1 | T-r4-W8b-01 | carter-approved token required | human-action; sign-off verify | `(src/python) $PY -m ta_r4.signoff verify W8b-T3 && echo SIGNED_OFF` | ❌ W0b1 (signoff.py) | ⬜ pending |
| W9-T1 | W9 | 25 | D-09, B1 | T-r4-W9-01 | carter-approved + venue | human-action; sign-off verify + DEC count | `(src/python) $PY -m ta_r4.signoff verify W9-T1 && cd ../.. && grep -c "ta-r4-venue" .planning/DECISIONS.md` | ❌ W0b1 (signoff.py) | ⬜ pending |
| W9-T2 | W9 | 25 | D-09, REQ-PUBLIC-DATA-ONLY | T-r4-W9-02/03 | overlay needs W9-T1; numbers unchanged | unit + test_signoffs | `ls docs/manuscript/r4/submission/ && $PY -m pytest tests/ta_r4/test_manuscript_r4.py tests/ta_r4/test_render_manuscript.py tests/ta_r4/test_signoffs.py -q` | ❌ W9 (overlay test) | ⬜ pending |
| W9-T3 | W9 | 25 | §C | — | N/A | porcelain + fsck | `git status --porcelain -- docs/manuscript/r4/submission .planning/amendments/osf-r4-results-record-DRAFT.md && git fsck --connectivity-only 2>&1 \| tail -2` | ✅ | ⬜ pending |
| W9-T4 | W9 | 25 | D-09, B1 | T-r4-W9-01 | carter-approved + 4 facts; ROADMAP sentinel | human-action; sign-off verify + test_signoffs | `(src/python) $PY -m ta_r4.signoff verify W9-T4 && cd ../.. && $PY -m pytest tests/ta_r4/test_signoffs.py -q && grep -c "ta-r4-submitted" .planning/DECISIONS.md` | ❌ W0b1 (signoff.py) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky.* *File Exists: ✅ = the command needs no new file; ❌ Wn = created in wave Wn (RED first).*

Every task has an `<automated>` command, so no 3 consecutive tasks lack automated verification.
Human-action checkpoints are verified by `python -m ta_r4.signoff verify <ID>` (and, for W4b-T3,
by the lock gate CLI), which fails unless Carter's validated reply is recorded.

---

## Wave 0 Requirements

- [ ] `tests/ta_r4/conftest.py` — overlay-merge helper (`snakemake.utils.update_config`), `r4_heavy` marker, fixture panels and sumstats
- [ ] `src/python/ta_r4/signoff.py` + `tests/ta_r4/test_signoff.py` + `tests/ta_r4/test_signoffs.py` (W0b1) before any human-action checkpoint
- [ ] `tests/ta_r4/fixtures/make_fixture_repo.py` (W0b2) for gate dry-runs that stay meaningful after the real lock record exists
- [ ] every `❌ W0*` test above, committed RED first with its negative control observed failing
- [ ] re-measured `tests/m3` baseline recorded in `ta-r4-LOG.md`; tag `ta-r4-pre-baseline` pushed

---

## Manual-Only Verifications

All are `checkpoint:human-action` (auto-mode stops); each leaves a machine-checked sign-off.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Panel/trait facts, UKB-native and QTL-scope decisions | D-12a/D-25, W3, W6 | judgement on measured facts | W2c-T4: reply `carter-approved YYYY-MM-DD` + keys; `signoff verify W2c-T4` |
| Known-answer findings report | D-12/D-17 | mismatches are findings, not failures | W3b-T3; `signoff verify W3b-T3` |
| Pre-registration lock values + draft approval | D-26 | Carter's decision rule | W4a-T3; `signoff verify W4a-T3`; test_signoffs lock sentinel |
| Analysis locked before production (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf) | D-05/D-27 | Carter confirms the lock commit | W4b-T3: Carter replies with `lock_sha`; `signoff verify W4b-T3` + `r4_lock_gate check --stage production` exit 0 |
| Results review | D-26 | headline is the classifier's branch | W7-T3; `signoff verify W7-T3` |
| Manuscript scientific accuracy | D-08 | prose claims vs results | brief-blind review + W8b-T3; `signoff verify W8b-T3` |
| Venue; submission + OSF results record | D-09 | Carter's external actions | W9-T1, W9-T4; `signoff verify` + test_signoffs ROADMAP sentinel |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s (quick run excludes `r4_heavy`; measured each wave)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending (plan-check iteration 2)
