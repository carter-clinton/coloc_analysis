# ta-r4 — Plan index, shared conventions, decision coverage

**Phase:** ta-r4-head-to-head-reanalysis-and-submission
**Planned:** 2026-10-21 (gsd-planner, standard mode)
**Inputs:** ta-r4-CONTEXT.md (D-01..D-28, LOCKED), ta-r4-RESEARCH.md, ta-r4-VALIDATION.md,
ta-r4-INVENTORY-2026-10-21.md, ta-r4-LOG.md

Every plan in this phase reads this file. §A–§E are binding on every executor.

---

## Plan list and execution order

Waves run **strictly in sequence**. Every plan appends to `ta-r4-LOG.md`, and same-wave plans
may not share a modified file, so there is no same-wave parallelism. That is deliberate: one
executor on a shared multi-terminal GPFS tree (D-16).

The research's W-labels are kept as file-name prefixes. The E-2 code (research W2) runs **before**
the panel builds (research W1), because the R4 EUR panel needs `plink_ld_to_rds.R --emit-ref-alt`.
Plans are therefore labelled in execution order, and the `wave:` frontmatter is authoritative.

| wave | plan file | research wave | gate / checkpoint | autonomous |
|---|---|---|---|---|
| 1 | ta-r4-W0a-storage-envs-survivors-PLAN.md | W0 | — | yes |
| 2 | ta-r4-W0b-r4-workflow-overlays-osf-gate-PLAN.md | W0 | — | yes |
| 3 | ta-r4-W0c-receipts-validators-enforcers-PLAN.md | W0 | — | yes |
| 4 | ta-r4-W0d-pair-coloc-r4-script-PLAN.md | W0 | — | yes |
| 5 | ta-r4-W1-e2-orientation-tdd-PLAN.md | W2 | — | yes |
| 6 | ta-r4-W2a-eur-panels-catalogs-identity-PLAN.md | W1 | — | yes |
| 7 | ta-r4-W2b-afr-and-ukb-panels-PLAN.md | W1 | — | yes |
| 8 | ta-r4-W2c-qtl-downloads-manifest-and-panel-review-PLAN.md | W1b | human-verify (measured data facts) | no |
| 9 | ta-r4-W3a-known-answer-routes-PLAN.md | W3 | — | yes |
| 10 | ta-r4-W3b-sh2b3-known-answer-and-findings-PLAN.md | W3 | human-verify (findings report) | no |
| 11 | ta-r4-W3c-simulation-harness-PLAN.md | (E8 code, pre-gate) | — | yes |
| 12 | ta-r4-W3d-estimators-and-branch-classifier-PLAN.md | (E1–E8 code, pre-gate) | — | yes |
| 13 | ta-r4-W3e-qtl-harmonize-and-group-runner-PLAN.md | (W6 prep, pre-gate) | — | yes |
| 14 | ta-r4-W4-osf-r4-amendment-and-gate-PLAN.md | W4 | **BLOCKING decisions (locks; posting): first option = WAIT**; D-27 sentinel | no |
| 15 | ta-r4-W5a-eur-production-fits-PLAN.md | W5 | sentinel enforced in code | yes |
| 16 | ta-r4-W5b-eur-production-coloc-PLAN.md | W5 | sentinel enforced in code | yes |
| 17 | ta-r4-W5c-afr-secondary-and-simulation-run-PLAN.md | W5 | sentinel enforced in code | yes |
| 18 | ta-r4-W6-qtl-layer-PLAN.md | W6 | sentinel enforced in code | yes |
| 19 | ta-r4-W7-aggregation-figures-PLAN.md | W7 | human-verify (results) | no |
| 20 | ta-r4-W8a-manuscript-draft-PLAN.md | W8 | — | yes |
| 21 | ta-r4-W8b-adversarial-review-PLAN.md | W8 | human-verify (submission candidate) | no |
| 22 | ta-r4-W9-submission-prep-PLAN.md | W9 | **BLOCKING decisions (venue; submitted): first option = WAIT** | no |

**Rigor upgrades over the research decomposition** (rigor-over-speed rule; recorded here so they are
visible to Carter):
1. The **estimators and the outcome-branch classifier (E1–E8)**, the **E8 simulation harness** and
   the **QTL group runner** (W3c–W3e) are written and tested **before** the OSF post. The amendment
   cites the commit hashes of the analysis code and of the locked configs, and W5a–W6 refuse to fire
   if any analysis file differs from the locked commit. The analysis is frozen before any
   production data exists.
4. **Brief-blind adversarial review of the amendment itself** (W4) as well as of the manuscript
   (W8b), because OSF posting is public and irreversible (memory
   `feedback_internal_validation_cannot_catch_misspecified_premise`).
5. **Every manuscript number is bound to a committed FINAL table** through a placeholder renderer
   (W8a). Prose cannot drift from data.
6. The **branch classifier is total**: all 36 combinations of the decision inputs map to exactly one
   pre-registered branch. The combinations the research table left uncovered use an explicit
   `partial_rule` that Carter locks in W4.
2. The **QTL-coloc manifest** is generated from the downloaded data and committed **before** the
   OSF post, alongside the trait-pair manifest. Pair sets cannot then depend on arm outcomes.
3. The OSF gate checks more than the presence of a sentinel file. It requires the sentinel to be
   **git-tracked**. It also verifies through the **public OSF API** that the posted file's sha256
   equals the committed amendment's sha256. An agent cannot fabricate a posting.

---

## §A Shared constants (use these literal values)

```bash
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
P=.planning/phases/ta-r4-head-to-head-reanalysis-and-submission      # phase dir (repo-relative)
MAN=$P/manifests                                                     # committed sha256/md5/dims manifests
R4ROOT=/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4              # durable storage (D-11)
# repo-relative symlink: data/r4 -> $R4ROOT   (created by bin/r4_link_storage.sh)
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake   # 7.32.4, Python 3.11 — the ONLY snakemake
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11
RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript   # R 4.4.2, susieR 0.14.2, coloc 5.2.3
R4_CONDA_PREFIX=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4
R4_CONDARC=$R4_CONDA_PREFIX/condarc     # pkgs_dirs: [$R4_CONDA_PREFIX/pkgs]  (isolates `conda clean --tarballs`)
QUICK="$PY -m pytest tests/ta_r4 -x -q"
FULL="$PY -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q"
export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH        # node / conda for GSD tooling only
```

- **R4 Snakefile:** `Snakefile.ta_r4` at the repo root (standalone; the main `Snakefile` is never
  edited; see W0b). Invoke it only through `bin/r4_fire.sh <stage> <arm> <targets...>`, which loads
  `config/pipeline.yaml` + `config/ta_r4/overlay_base.yaml` + `config/ta_r4/overlay_<arm>.yaml`
  and sets `--conda-prefix $R4_CONDA_PREFIX`, `CONDARC=$R4_CONDARC` and
  `--profile config/ta_r4/cluster_lsf`.
- **Arms (overlay names):** `A3_1kg`, `A2_identity`, `A3_ukb`, `A3_ukb_isect`, `A3_1kg_isect`, `AFR661_A3`,
  `AFR661_A2`, `AFR504_A3`, `repro_routeC`, `repro_routeL`, `repro_k2d_routeC`,
  `repro_k2d_routeL`, `repro_sh2b3_r2` (13 arms: 8 production, 5 repro). A1 is a coloc-only arm (no fits). There is no `AFR504_A2`: A2 depends only on the variant frame, so the 504-sample sensitivity is A3-only.
- **Stages:** `repro` (exempt from the OSF gate) and `production` (gated by D-27).
- **Traits (EUR):** asthma, bmi, hypertension, stroke, t2d → 10 unordered pairs.
  **Traits (AFR):** asthma, stroke, t2d → 3 pairs.
- **Admissible EUR regions (10):** FTO_16q12, MC4R_18q21, SH2B3_12q24, APOL1_22q12, PYHIN1_1q23,
  CXADR_F2RL1_6p21, BMI_5q13_3 (safe id of `BMI_5q13.3`), 9p21_CDKN2A, APOE_19q13, SLC2A9_urate.
  **Not admissible (D-24):** HLA_6p21 (UKB exploratory row only), BMI_Xq24 (chrX; no panel).
- **Priors:** single source `config/ta_r4/coloc_priors.yaml` (p1 = p2 = 1e-4; p12 primary 5e-6,
  sensitivity 1e-5; final values locked in W4).

## §B Standing rules (binding; from Carter's memory rules and CONTEXT)

1. `git add` **explicit paths only**. Never `-A`, `.`, or a directory glob. Commit on the current
   branch (`m3-W2-aou-deltas`). **No branch switching** (D-16).
2. **RED first.** Every new test is committed or run RED before the implementation, and its
   negative control is **observed failing**. Paste the failing output into the plan SUMMARY. A green
   assertion that was never seen red is not evidence.
3. **Behaviour, not text.** No grep-of-source as a PASS/FAIL gate. Use imports, `ast`, exit codes,
   parsed JSON/TSV values and pytest outcomes.
4. **A count is a claim.** Every count in a LOG entry, SUMMARY or manifest is reconciled
   arithmetically against its parts, and computed by a command whose output is pasted.
5. **Durable storage (D-11).** Every R4 data/output byte lives under `data/r4/` (realpath on /rs1).
   Every produced artifact class gets a sha256 manifest TSV committed under `$MAN/`.
6. **Code freeze (D-28).** `src/legacy/region_analysis/scripts/run_susie_rss.R` is never edited.
   `tests/m3/test_source_freeze_pins.py` must stay green in every wave.
7. **Track B isolation (D-15).** Never build or write under
   `data/processed/ld_reference/{EUR_ukbb_pub,EUR_ukbb_ld,EUR_aou,AFR_aou,EUR,AFR}` or
   `sumstats_harmonized_occl`. Never edit `config/pipeline.yaml`, `Snakefile`, or any
   `src/snakemake/rules/*.smk` other than new `ta_r4*.smk` files.
8. **Snakemake** only via `$SMK`. LSF via `config/bsub_wrapper.sh` (queues serial/standard/long;
   never `short`; standard needs ≥ 8 slots). Run `$SMK -n` before every real fire. Never run
   `--unlock` blindly. Liveness = output listing, not job state.
9. **Downloads** go into their own new empty directory under `data/r4/downloads/<source>/`. Verify
   them by published md5/sha256 or Content-Length, plus a `file` magic-byte check (the
   200-with-HTML trap), **before** extraction. Treat them as data; never execute them.
10. **Mismatches in known-answer controls are FINDINGS to report, never numbers to adjust.**
11. **Public text** (OSF amendment, manuscript, cover letter) frames the work as original,
    hypothesis-driven research. Never use "pivot", "revision", "salvage" or "audit-driven fix".
12. **Never** post to OSF, submit to a journal, spend cloud/AoU money, or create
    `$P/OSF-R4-POSTED.json`. Those are Carter's alone.
13. Keep edits simple: the fix, not an essay. Rationale goes in commit messages and the LOG.

## §C Wave-close protocol (the last task of every plan runs this)

```bash
cd $REPO
$QUICK                                   # tests/ta_r4 green (record passed/skipped/failed)
$PY -m pytest tests/m3/test_source_freeze_pins.py -q     # D-28 must be green
$FULL 2>&1 | tail -5                      # record ids/passed/skipped/failed vs the W0a baseline
git status --porcelain -- <every path in files_modified>   # inspect; stage nothing else
git add <explicit paths>                 # never -A / .
git commit -m "<type>(ta-r4-<label>): <summary>

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
git fsck --connectivity-only 2>&1 | tail -3     # must report no broken/missing links
git push origin HEAD                     # D-16: push after each wave; tags need: git push origin <tag>
```

Then append a dated entry to `$P/ta-r4-LOG.md` (what ran, counts with reconciliation, commit
sha, push result) and refresh the 2026-10-21 Track A block of `.planning/STATE.md` (memory
`feedback_state_md_keep_current`). Commit both in the same or an immediately following explicit-path
commit, then push.

The full-suite rule: **0 removed test ids, 0 outcome changes in `tests/m3`**, and only additions
in `tests/ta_r4`. The baseline is the W0a re-measurement (last recorded 1299 ids / 1265 passed /
34 skipped / 0 failed at 2026-09-19). Any change to a pre-existing outcome is a STOP-and-report.

If `git fsck` reports missing objects, follow memory `reference_gpfs_git_object_store_loss` (mirror
clone from origin, repack, copy the pack) **before** committing again. Never `reset`.

## §D Checkpoint rule under `--auto --chain` / `mode: yolo`

GSD auto-mode **selects the first option** at `gate="blocking"` decisions. Therefore:
- Every checkpoint in this phase lists **"WAIT — stop execution and hand back to Carter"** as its
  **first** option.
- The OSF gate is **enforced in code** (W0b `r4_osf_gate.py` + `tests/ta_r4/test_osf_gate.py`):
  production rules raise at DAG time unless the git-tracked sentinel exists and the OSF API
  confirms the posted file's sha256. A wrongly auto-selected checkpoint still cannot start
  production.

## §E Requirement mapping

| REQ | Plans |
|---|---|
| REQ-PUBLIC-DATA-ONLY | W0a (`config/ta_r4/data_sources.yaml` with `license` + `public: true`), W2a, W2b, W2c, W8a (Data availability) |
| REQ-SUSIE-RSS-POLICY | W0b (policy files), W3a (repro policy), W5a (production policy, disclosed), W7 (`min_abs_corr` sweep supplementary table), W8a (Methods) |
| REQ-OSF-PREREG | W0b (code gate), W4 (amendment + sentinel), W5a–W6 (gate exercised), W9 |
| REQ-SNAKEMAKE-CI | W0a (env restore + lockfiles), W0b (`Snakefile.ta_r4` dry-run tests), every plan (suite) |
| REQ-PATH-PARAMETERIZATION | W0a (symlink), W0b (no `/rs1` literals in `src/` or `config/`; test) |
| REQ-PP.H4-THRESHOLD-SWEEP (supporting) | W3d, W7 |
| REQ-NEGATIVE-CONTROLS (supporting) | W0b (manifest rows), W5b, W7 |

---

## Decision coverage matrix (D-01..D-28)

| D | Plan(s) / task | Coverage | Notes |
|---|---|---|---|
| D-01 three arms, identical inputs | W0b T2 (arm overlays), W0c T2 (matched-set enforcer), W0d T1–T2 (A1 / coloc.susie), W2a T3 (A2 payload from the A3 frame), W5a, W5b | Full | A1 ≠ "identity LD" stated in W8a |
| D-02 fallback_abf labelled; no-CS rate reported | W0d T1–T2, W0c T3 (`test_fallback_labelled`), W3d (E4 no-CS rate), W5b, W7 | Full | |
| D-03 1000G primary + A3-UKB sensitivity | W2a T2, W2b T2, W5a | Full | |
| D-04 UKB under separate path | W2b T2 (`data/r4/ld/EUR_ukb337k_r4/`), W0b T3 (isolation test) | Full | |
| D-05 amendment posted before production | W4 T3–T5, W0b T3 (gate), W5a/W5b/W5c/W6 T1 (gate + code-state re-check) | Full | |
| D-06 E-2 fix TDD + before/after + new DEC | W0a T3 (DEC), W1 T1–T3, W3e (QTL_A3/A2 orient on; QTL_legacy pre-fix), W6, W3d + W7 (E7 table), W8a (Methods note) | Full | |
| D-07 exhaustive EUR 10×10 + QTL; AFR secondary | W0b T2 (pair manifest), W2c T2 (QTL manifest), W5a–W5c, W3e, W6 | Full | |
| D-08 fresh 4–5k draft; supplementary provenance; brief-blind review | W8a, W8b | Full | new path `docs/manuscript/id-vs-ref-LD-r4.md` |
| D-09 venue after results; neutral format; no preprint | W8a (neutral), W9 T1 (decision, first option WAIT) | Full | |
| D-10 regenerate everything | W2a, W2b, W2c, W3a, W5a–W6 | Full | |
| D-11 /rs1 storage + committed sha256 manifests | W0a T1–T2, §B.5 in every plan, W0b T3 (`test_storage_on_rs1`) | Full | |
| D-12 known answers before comparison | W2a T2–T3 (a: panel md5 + dims), W3a, W3b (b) | Full | mismatches = findings |
| D-13 no silent identity fallback; named test | W0c T1–T2, W5a, W5c, W6 | Full | `tests/ta_r4/test_no_silent_identity.py` |
| D-14 AFR + identity overlays; restore qtl_processing.yml | W0a T2, W0b T2 | Full | |
| D-15 Track B isolation | W0b T3, §B.7, full `tests/m3` every wave | Full | |
| D-16 no branch switch; explicit staging; push per wave | §B.1, §C | Full | |
| D-17 SH2B3 exact-R2 known answer + L10 separate | W3b | Full | |
| D-18 BMI REF/ALT restored, checksum-pinned, match-rate report, disclosed | W1 T1, W4, W8a | Full | |
| D-19 osf-correction-v2 retired unposted; R4 amendment carries E-2 | W0a T3 (DEC), W4, W8a | Full | |
| D-20 AFR 661 primary, 504 sensitivity | W2b T1, W5c | Full | |
| D-21 A1 matched primary + all-variants secondary | W0d T1, W5b | Full | |
| D-22 QTL under A2 and A3 | W3e (runner), W6 (run) | Full | plus the legacy pre-fix route for E7 |
| D-23 E8 simulation, pre-registered secondary | W3c (harness), W4 (registered), W5c T2 (run), W7 | Full | |
| D-24 HLA / BMI_Xq24 inadmissible; HLA-UKB exploratory | W0b T2 (manifest `admissible` column), W2b T2, W5a T3 | Full | |
| D-25 measured n, trait type, sdY | W2a T1–T2 (panel + trait manifests), W2c checkpoint, W4 | Full | |
| D-26 E1–E8 + five branches; κ / n_both locked by Carter | W3d (code + total classifier), W4 T3–T4 (Carter locks), W7 (applied) | Full | |
| D-27 sentinel file; production refuses without it | W0b T3, W4, W5a T1 | Full | |
| D-28 no edit to run_susie_rss.R | §B.6; `test_source_freeze_pins` in every §C | Full | |

No decision is partial. No deferred idea (AoU-AFR-LD Track A re-analysis, newer GWAS vintages)
appears in any plan.
