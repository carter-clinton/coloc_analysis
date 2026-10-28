# ta-r4 — Plan index, shared conventions, decision coverage

**Phase:** ta-r4-head-to-head-reanalysis-and-submission
**Planned:** 2026-10-21 (gsd-planner, standard mode); **revised** 2026-10-21 (plan-check iteration 1: B1–B6, W1–W16; iteration 2: confirmatory-set blocker, W-1..W-5)
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
`depends_on` uses plan ids (file name minus `-PLAN.md`).

| wave | plan file | research wave | Carter checkpoint (all `checkpoint:human-action`) | autonomous |
|---|---|---|---|---|
| 1 | ta-r4-W0a-storage-envs-survivors-PLAN.md | W0 | — | yes |
| 2 | ta-r4-W0b1-arms-paths-overlays-signoff-PLAN.md | W0 | — | yes |
| 3 | ta-r4-W0b2-pair-manifest-osf-gate-workflow-PLAN.md | W0 | — | yes |
| 4 | ta-r4-W0c-receipts-validators-enforcers-PLAN.md | W0 | — | yes |
| 5 | ta-r4-W0d-pair-coloc-r4-script-PLAN.md | W0 | — | yes |
| 6 | ta-r4-W1-e2-orientation-tdd-PLAN.md | W2 | — | yes |
| 7 | ta-r4-W2a-eur-panels-catalogs-identity-PLAN.md | W1 | — | yes |
| 8 | ta-r4-W2b-afr-and-ukb-panels-PLAN.md | W1 | — | yes |
| 9 | ta-r4-W2c-qtl-downloads-manifest-and-panel-review-PLAN.md | W1b | W2c-T4 data facts + ukb_native + qtl_scope | no |
| 10 | ta-r4-W2d-apply-review-decisions-PLAN.md | W1b | — (applies W2c-T4) | yes |
| 11 | ta-r4-W3a-known-answer-routes-PLAN.md | W3 | — | yes |
| 12 | ta-r4-W3b-sh2b3-known-answer-and-findings-PLAN.md | W3 | W3b-T3 known-answer findings | no |
| 13 | ta-r4-W3c-simulation-harness-PLAN.md | (E8 code, pre-lock) | — | yes |
| 14 | ta-r4-W3d-estimators-and-branch-classifier-PLAN.md | (E1–E8, confirmatory contrast_stats, coverage + aggregation code, pre-lock) | — | yes |
| 15 | ta-r4-W3e-qtl-harmonize-and-group-runner-PLAN.md | (W6 prep, pre-lock) | — | yes |
| 16 | ta-r4-W4a-amendment-draft-review-locks-PLAN.md | W4 | W4a-T3 lock values + draft approval | no |
| 17 | ta-r4-W4b-amendment-final-and-posting-gate-PLAN.md | W4 | W4b-T3 lock confirmation (+ lock gate) | no |
| 18 | ta-r4-W5a-eur-production-fits-PLAN.md | W5 | — (code gate) | yes |
| 19 | ta-r4-W5b-eur-production-coloc-PLAN.md | W5 | — (code gate) | yes |
| 20 | ta-r4-W5c-afr-secondary-and-simulation-run-PLAN.md | W5 | — (code gate) | yes |
| 21 | ta-r4-W6-qtl-layer-PLAN.md | W6 | — (code gate) | yes |
| 22 | ta-r4-W7-aggregation-figures-PLAN.md | W7 | W7-T3 results | no |
| 23 | ta-r4-W8a-manuscript-draft-PLAN.md | W8 | — | yes |
| 24 | ta-r4-W8b-adversarial-review-PLAN.md | W8 | W8b-T3 submission candidate | no |
| 25 | ta-r4-W9-submission-prep-PLAN.md | W9 | W9-T1 venue; W9-T4 submitted (+ code sentinels) | no |

**Rigor upgrades over the research decomposition** (rigor-over-speed rule; recorded here so they are
visible to Carter):
1. The **estimators, the confirmatory row set and stats→category rules (`decision_rules.yaml`
   `confirmatory:` + `estimands.contrast_stats`), the outcome-branch classifier, the coloc coverage
   tool and the aggregation entry point `run_aggregation.py` (E1–E8)**, the **E8
   simulation harness** and the **QTL group runner** (W3c–W3e) are written and tested **before** the
   lock (W4b). The amendment cites the commit hashes of the analysis code and of the locked configs
   (W4b commit A), and W5a–W6 refuse to fire if any analysis file differs from the lock commit
   (enforced by `ta_r4.r4_lock_gate`: `LOCKED_PATHS`, lock record `$P/R4-LOCK.json`). The
   analysis is frozen before any production data exists.
2. The **QTL-coloc manifest** is generated from the downloaded data and committed **before** the
   lock (W4b), alongside the trait-pair manifest; its scope is Carter's pre-registered choice among
   outcome-independent filters, with a measured cost per option. Row sets cannot depend on arm outcomes.
3. The production gate is the **git lock** (`ta_r4.r4_lock_gate`, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf). Production
   passes only if `$P/R4-LOCK.json` is git-tracked and committed, its `lock_sha` (W4b commit A) is an
   ancestor of HEAD, the three configs are `locked: true` at `lock_sha`, no `LOCKED_PATHS` file differs
   from `lock_sha` (committed, working copy or untracked), and Carter's W4b-T3 sign-off records the same
   `lock_sha`. Offline: no network, no environment-variable bypass. OSF posting is optional.
4. **Brief-blind adversarial review of the amendment's public text** (W4a) as well as of the
   manuscript (W8b), because OSF posting is public and irreversible (memory
   `feedback_internal_validation_cannot_catch_misspecified_premise`).
5. **Every manuscript number is bound to a committed FINAL table** through a placeholder renderer
   (W8a). Prose cannot drift from data.
6. The **branch classifier is total and ordered**: all 36 combinations of the decision inputs map to
   exactly one pre-registered branch by a stated precedence. The 8 combinations the research table
   leaves uncovered use four explicit `partial_rule` keys that Carter locks in W4a.
7. **Every Carter judgement is a `checkpoint:human-action`** whose reply must parse as
   `carter-approved YYYY-MM-DD` + required keys (`ta_r4.signoff`); the configuration states that
   depend on those judgements are enforced by `tests/ta_r4/test_signoffs.py`.
8. A **third admissible negative-control set** (10 GWAS-null windows, deterministic seeded rule)
   satisfies REQ-NEGATIVE-CONTROLS, because the config's third set (HLA) is inadmissible (D-24).

---

## §A Shared constants (use these literal values)

```bash
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
P=.planning/phases/ta-r4-head-to-head-reanalysis-and-submission      # phase dir (repo-relative)
MAN=$P/manifests                                                     # committed sha256/md5/dims manifests
SIGNOFFS=$P/signoffs                                                 # Carter sign-offs (ta_r4.signoff)
R4ROOT=/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4              # durable storage (D-11)
# repo-relative symlink: data/r4 -> $R4ROOT   (created by bin/r4_link_storage.sh)
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake   # 7.32.4, Python 3.11 — the ONLY snakemake
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11
RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript   # R 4.4.2, susieR 0.14.2, coloc 5.2.3
R4_CONDA_PREFIX=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4
R4_CONDARC=$R4_CONDA_PREFIX/condarc     # pkgs_dirs: [$R4_CONDA_PREFIX/pkgs]  (isolates `conda clean --tarballs`)
# bin/r4_fire.sh also exports CONDA_PKGS_DIRS=$R4_CONDA_PREFIX/pkgs HOME=$R4_CONDA_PREFIX/home (CONDARC alone does not isolate; W0a);
# channel_priority flexible (envs/plink.yml is unsatisfiable under strict; W0b2); conda-frontend conda
R4_PLINK=$R4_CONDA_PREFIX/55c377a7e8fce799d92381bcc5138d7f_/bin/plink   # PLINK v1.90b6.21 (W0b2 env solve)
QUICK="$PY -m pytest tests/ta_r4 -x -q -m 'not r4_heavy'"          # per task; must stay < 120 s
HEAVY="$PY -m pytest tests/ta_r4 -q -m r4_heavy -rs"               # per wave: live gates, Snakemake runs, frozen-script e2e
FULL="$PY -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q"
export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH        # node / conda for GSD tooling only
```

- **`r4_heavy` marker** (registered in `tests/ta_r4/conftest.py`, W0a): any test that runs `$SMK`,
  runs the frozen `run_susie_rss.R`, or reads `data/r4/results/`. Task-level `<verify>` commands
  that name a test file run it regardless of the marker.
- **R4 Snakefile:** `Snakefile.ta_r4` at the repo root (standalone; the main `Snakefile` is never
  edited; see W0b2). Invoke it only through `bin/r4_fire.sh <stage> <arm> <targets...>`, which loads
  `config/pipeline.yaml` + `config/ta_r4/overlay_base.yaml` + `config/ta_r4/overlay_<arm>.yaml`,
  sets `--conda-prefix $R4_CONDA_PREFIX`, `CONDARC=$R4_CONDARC` and
  `--profile config/ta_r4/cluster_lsf`, and for production runs `r4_lock_gate check` first.
- **Arms (overlay names):** `A3_1kg`, `A2_identity`, `A3_ukb`, `A3_ukb_isect`, `A3_1kg_isect`, `AFR661_A3`,
  `AFR661_A2`, `AFR504_A3`, `repro_routeC`, `repro_routeL`, `repro_k2d_routeC`,
  `repro_k2d_routeL`, `repro_sh2b3_r2` (13 arms: 8 production, 5 repro). A1 is a coloc-only arm (no fits). There is no `AFR504_A2`: A2 depends only on the variant frame, so the 504-sample sensitivity is A3-only. `A3_ukb` points at `EUR_ukb337k_r4` or, if Carter chooses HM3 at W2c, `EUR_ukb337k_hm3_r4` (W2d).
- **Result globs:** only through `ta_r4.paths.result_dirs("fits" | "coloc")` (production arms from ARMS; coloc adds `A1_EUR`, `A1_AFR`). Never a hand-written arm list.
- **Stages:** `repro` (exempt from the gate) and `production` (gated by the lock gate, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf).
- **Traits (EUR):** asthma, bmi, hypertension, stroke, t2d → 10 unordered pairs.
  **Traits (AFR):** asthma, stroke, t2d → 3 pairs.
- **Admissible EUR regions (10):** FTO_16q12, MC4R_18q21, SH2B3_12q24, APOL1_22q12, PYHIN1_1q23,
  CXADR_F2RL1_6p21, BMI_5q13_3 (safe id of `BMI_5q13.3`), 9p21_CDKN2A, APOE_19q13, SLC2A9_urate.
  **Not admissible (D-24):** HLA_6p21 (UKB exploratory fits only; no coloc row), BMI_Xq24 (chrX; no panel).
- **Negative-control regions (19, EUR):** cosmetic 5 (NC_OCA2_HERC2, NC_SLC24A5, NC_MC1R, NC_TYR, NC_IRF4),
  blood_group 4 (NC_ABO, NC_RH, NC_FUT1_FUT2, NC_KEL), gwas_null 10 (NC_NULL_01..NC_NULL_10, selected in W0b2;
  GRCh37 250-kb tiles 1:99500001, 1:218750001, 2:190000001, 3:30750001, 3:178250001, 6:81500001,
  11:21500001, 13:38500001, 13:71000001, 14:49000001 (start; end = start + 249999)).
  `regions_r4.csv` = 12 + 19 = 31 rows; `pair_manifest.tsv` = 346 rows, 320 admissible (290 EUR, 30 AFR).
- **Confirmatory analysis (pre-lock, W3d; orchestrator default under the rigor rule, Carter may change it at W4a-T3):**
  rows = primary curated EUR admissible rows (10 regions × 10 pairs = 100), p12_primary, A1 varset
  matched, reference A3_1kg; bootstrap clusters = those 10 regions (never the 29 incl. NC);
  CI / McNemar / kappa / n_both on the both-have-CS subset at PP.H4 ≥ 0.8. Negative-control rows are a
  pre-specified specificity analysis and never feed the classifier; AFR, p12_sensitivity, A1-allvars,
  UKB/isect and repro rows are descriptive.
- **Panel manifests and receipts** are keyed by (ancestry, region_safe); the file comes from
  `ta_r4.paths.panel_manifest_path(arm, ancestry)`. Repro (legacy_any) fits with no legacy panel run
  as the frozen fire did (no panel input; receipt `present: false`, `ld_source_class: missing`).
- **`data/r4`** is gitignored by W0a (it was not, measured 2026-10-21).
- **Priors:** single source `config/ta_r4/coloc_priors.yaml` (p1 = p2 = 1e-4; p12 primary 5e-6,
  sensitivity 1e-5; final values locked in W4b from Carter's W4a sign-off).

## §B Standing rules (binding; from Carter's memory rules and CONTEXT)

1. `git add` **explicit paths only**. Never `-A`, `.`, or a directory glob. Commit on the current
   branch (`m3-W2-aou-deltas`). **No branch switching** (D-16).
2. **RED first.** Every new test is committed or run RED before the implementation, and its
   negative control is **observed failing**. Paste the failing output into the plan SUMMARY. A green
   assertion that was never seen red is not evidence.
3. **Behaviour, not text.** No grep-of-source as a PASS/FAIL gate. Use imports, `ast`, exit codes,
   parsed JSON/TSV values and pytest outcomes. (Exception: banned words and internal paths in public
   text are literal properties of that text.)
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
11. **Public text** (OSF amendment PUBLIC extract, manuscript, cover letter) frames the work as
    original, hypothesis-driven research. Never use "pivot", "revision", "salvage" or "audit-driven fix".
    R4 is described as "analysis locked in commit <sha> before production", never "pre-registered on OSF".
12. **Never** post to OSF on Carter's behalf, submit to a journal, or spend cloud/AoU money. Never
    create `$P/R4-LOCK.json` except in W4b Task 2 with `lock_sha` = commit A; never write
    `signoffs/W4b-T3.yaml` except via `signoff record` from Carter's verbatim reply. Fixture lock
    records are allowed only under pytest `tmp_path` fixture repos.
13. Keep edits simple: the fix, not an essay. Rationale goes in commit messages and the LOG.
14. **No commits while a production fire is in flight.** In-job gate checks re-diff the locked paths
    against the lock commit; commit only after the fire ends and its dry-run says "Nothing to be done".
15. **Carter sign-off protocol.** At every `checkpoint:human-action`, save Carter's reply
    byte-for-byte and run `python -m ta_r4.signoff record <ID> ...`. A non-zero exit (including a
    bare "approved", the auto-mode string) means WAIT: re-present the checkpoint and write nothing.
    The executor never authors, types or completes any `carter-approved` text and never writes
    `signoffs/*.yaml` except via `signoff record`. The raw file is written only from the resume
    payload the orchestrator passes, which must be Carter's message pasted verbatim (never a
    summary, paraphrase or auto response). The SUMMARY quotes the resume payload next to the
    recorded raw_sha256. The next plan's first step runs `signoff verify <ID>`.
16. **Decisions are made once.** `ukb_native` is decided only at W2c-T4 (not at W4a). W2d refuses
    to run once any config carries `locked: true`.

## §C Wave-close protocol (the last task of every plan runs this)

```bash
cd $REPO
time $QUICK                              # tests/ta_r4 quick: record passed/skipped/failed AND wall time (< 120 s; else mark the slowest tests r4_heavy and record it)
$HEAVY                                   # heavy live gates / Snakemake / frozen-script e2e for this wave
$PY -m pytest tests/m3/test_source_freeze_pins.py -q     # D-28 must be green
$FULL 2>&1 | tail -5                      # record ids/passed/skipped/failed vs the W0a baseline
git status --porcelain -- <every path in files_modified>   # inspect; stage nothing else
git fsck --connectivity-only 2>&1 | tail -3     # BEFORE commit: must report no broken/missing links
git add <explicit paths>                 # never -A / .
git commit -m "<type>(ta-r4-<label>): <summary>

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
git fsck --connectivity-only 2>&1 | tail -3     # AFTER commit: still clean
git push origin HEAD                     # D-16: push after each wave; tags need: git push origin <tag>
```

Then append a dated entry to `$P/ta-r4-LOG.md` (what ran, counts with reconciliation, commit
sha, push result, QUICK wall time) and refresh the 2026-10-21 Track A block of `.planning/STATE.md`
(memory `feedback_state_md_keep_current`). Commit both in the same or an immediately following
explicit-path commit, then push.

The full-suite rule: **0 removed test ids, 0 outcome changes in `tests/m3`**, and only additions
in `tests/ta_r4`. The baseline is the W0a re-measurement (last recorded 1299 ids / 1265 passed /
34 skipped / 0 failed at 2026-09-19). Any change to a pre-existing outcome is a STOP-and-report.

If `git fsck` reports missing objects (before or after the commit), follow memory
`reference_gpfs_git_object_store_loss` (mirror clone from origin, repack, copy the pack) **before**
committing again. Never `reset`.

## §D Checkpoint rule under `--auto --chain` / `mode: yolo`

Verified against `~/.claude/get-shit-done/workflows/execute-phase.md` (auto-mode checkpoint
handling): `checkpoint:human-verify` is auto-approved with the response "approved";
`checkpoint:decision` auto-selects its first option; **only `checkpoint:human-action` stops** and
is presented to Carter. Therefore:

- **Every** checkpoint whose outcome is Carter's judgement or action is `checkpoint:human-action`:
  W2c-T4, W3b-T3, W4a-T3, W4b-T3, W7-T3, W8b-T3, W9-T1, W9-T4. This phase has no
  `human-verify` or `decision` checkpoints.
- The resume token is `carter-approved YYYY-MM-DD` on the first line, followed by the checkpoint's
  required `key: value` lines (`ta_r4.signoff.SCHEMAS`). The auto path cannot produce it; a bare
  "approved" is WAIT (§B.15).
- **Code-level sentinels** back the checkpoints that change state:
  - Lock gate (`r4_lock_gate`, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf): production rules raise at DAG time and in every job
    unless the lock record, lock commit, locked configs, locked paths and W4b-T3 `lock_sha` all agree.
    A wrongly passed checkpoint still cannot start production.
  - `tests/ta_r4/test_signoffs.py` (W0b1): `review_decisions.yaml` ⇒ valid W2c-T4; any locked
    config ⇒ valid W4a-T3 with equal values; tracked lock record ⇒ valid W4b-T3 with equal `lock_sha`; venue overlay ⇒ valid
    W9-T1; checked W9 ROADMAP line ⇒ valid W9-T4.
  - `render_manuscript --venue-overlay` refuses without a valid W9-T1; estimand outputs are FINAL
    only with locked configs + valid W4a-T3 + the offline gate passing.
  - The next plan after W3b, W7 and W8b starts with `signoff verify <ID>`.
  - W2d refuses to run after the lock; W7 refuses to aggregate unless the lock diff (incl.
    `run_aggregation.py`) is empty.

## §E Requirement mapping

| REQ | Plans |
|---|---|
| REQ-PUBLIC-DATA-ONLY | W0a (`config/ta_r4/data_sources.yaml` with `license` + `public: true`), W2a, W2b, W2c, W2d (HM3 list entry), W8a (Data availability), W9 |
| REQ-SUSIE-RSS-POLICY | W0b1 (policy files), W3a (repro policy), W5a (production policy, disclosed), W7 (`min_abs_corr` sweep table), W8a (Methods) |
| REQ-OSF-PREREG | W0b1 (sign-off sentinels), W0b2 (original gate), quick-261028-kkg (lock gate), W4a (amendment + locks), W4b (lock commit A + lock record + W4b-T3), W5a–W6 (gate exercised), W9 |
| REQ-SNAKEMAKE-CI | W0a (env restore), W0b2 (`Snakefile.ta_r4` dry-run tests, lockfiles), W0d (toy 3-locus `--use-conda` end-to-end), every plan (suite) |
| REQ-PATH-PARAMETERIZATION | W0a (symlink + literal scan over config/ta_r4, src/python/ta_r4, src/snakemake/scripts/ta_r4, src/snakemake/rules/ta_r4_*.smk, Snakefile.ta_r4), W0b1 (paths module) |
| REQ-PP.H4-THRESHOLD-SWEEP (supporting) | W3d, W7 |
| REQ-NEGATIVE-CONTROLS (supporting) | W0b2 (three admissible sets: cosmetic, blood_group, gwas_null), W4a (disclosed), W5b, W7 |

---

## Decision coverage matrix (D-01..D-28)

| D | Plan(s) / task | Coverage | Notes |
|---|---|---|---|
| D-01 three arms, identical inputs | W0b1 T1 (arm overlays), W0c T2 (matched-set enforcer), W0d T1–T2 (A1 / coloc.susie), W2a T2 (A2 payload from the A3 frame), W2b T3 (isect re-orientation), W5a, W5b | Full | A1 ≠ "identity LD" stated in W8a |
| D-02 fallback_abf labelled; no-CS rate reported | W0d T1–T2 (`test_fallback_labelled`), W3d (E4 no-CS rate), W5b, W7 | Full | |
| D-03 1000G primary + A3-UKB sensitivity | W2a T2, W2b T2–T3, W2d T1, W5a | Full | |
| D-04 UKB under separate path | W2b T3 (`data/r4/ld/EUR_ukb337k_*`), W2d (hm3 dir), W0b2 T3 (isolation test) | Full | |
| D-05 analysis locked before production (lock gate, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf) | W4a, W4b T3, W0b2 T2–T3 (gate), W5a/W5b/W5c/W6 T1 (gate + code-state re-check) | Full | |
| D-06 E-2 fix TDD + before/after + new DEC | W0a T3 (DEC), W1 T1–T3, W3e (QTL_A3/A2 orient on; QTL_legacy pre-fix), W6, W3d + W7 (E7 table), W8a (Methods note) | Full | |
| D-07 exhaustive EUR 10×10 + QTL; AFR secondary | W0b2 T1 (pair manifest), W2c T2 + W2d T2 (QTL manifest + scope), W5a–W5c, W3e, W6 | Full | |
| D-08 fresh 4–5k draft; supplementary provenance; brief-blind review | W8a, W8b | Full | new path `docs/manuscript/id-vs-ref-LD-r4.md` |
| D-09 venue after results; neutral format; no preprint | W8a (neutral), W9 T1 (human-action venue) | Full | |
| D-10 regenerate everything | W2a, W2b, W2c, W3a, W5a–W6 | Full | |
| D-11 /rs1 storage + committed sha256 manifests | W0a T1–T2, §B.5 in every plan, W0a T1 (`test_storage_on_rs1`) | Full | |
| D-12 known answers before comparison | W2a T2–T3 (a: panel md5 + dims), W3a, W3b (b) | Full | mismatches = findings; W3b §(8) records the measured cause of the 28 empty R1 rows (ROADMAP R1_STRUCTURAL item) |
| D-13 no silent identity fallback; named test | W0c T1–T2 (globs from ARMS incl. A3_1kg_isect), W5a, W5c, W6 | Full | `tests/ta_r4/test_no_silent_identity.py` |
| D-14 AFR + identity overlays; restore qtl_processing.yml | W0a T2, W0b1 T1 | Full | |
| D-15 Track B isolation | W0b2 T3, §B.7, full `tests/m3` every wave | Full | |
| D-16 no branch switch; explicit staging; push per wave | §B.1, §C; W0a T2 tag `ta-r4-pre-baseline` pushed explicitly | Full | |
| D-17 SH2B3 exact-R2 known answer + L10 separate | W3b | Full | |
| D-18 BMI REF/ALT restored, checksum-pinned, match-rate report, disclosed | W1 T1, W4a, W8a | Full | |
| D-19 osf-correction-v2 retired unposted; R4 amendment carries E-2 | W0a T3 (DEC), W4a, W8a | Full | |
| D-20 AFR 661 primary, 504 sensitivity | W2b T1, W5c | Full | |
| D-21 A1 matched primary + all-variants secondary | W0d T1, W5b | Full | |
| D-22 QTL under A2 and A3 | W3e (runner), W6 (run) | Full | plus the legacy pre-fix route for E7 |
| D-23 E8 simulation, pre-registered secondary | W3c (harness), W4a (registered), W5c T3 (run), W7 | Full | |
| D-24 HLA / BMI_Xq24 inadmissible; HLA-UKB exploratory | W0b2 T1 (manifest `admissible` column), W2b T3, W5a, W7 (`hla_exploratory.tsv`) | Full | HLA UKB fits are exploratory and produce **no coloc row**: no admissible 1000G comparator exists, so no head-to-head is defined |
| D-25 measured n, trait type, sdY | W2a T1–T3 (panel + trait manifests), W2c T4 (Carter answers), W4a | Full | |
| D-26 E1–E8 + five branches; κ / n_both locked by Carter | W3d T1 (estimators, `confirmatory:` block + contrast_stats, total ordered classifier, 8 partial_rule combos), W3d T3 (run_aggregation, pre-lock), W4a (e)/(f) rendered from the yaml + T3 (Carter locks), W4b T1 (configs), W7 T1 (frozen code run) | Full | confirmatory set = 100 primary curated EUR rows, 10 clusters (orchestrator default; Carter may change at W4a-T3) |
| D-27 lock record; production refuses without it (lock gate, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf) | W0b2 T2–T3, W4b, W5a T1 | Full | |
| D-28 no edit to run_susie_rss.R | §B.6; `test_source_freeze_pins` in every §C | Full | |

No decision is partial. No deferred idea (AoU-AFR-LD Track A re-analysis, newer GWAS vintages)
appears in any plan.
