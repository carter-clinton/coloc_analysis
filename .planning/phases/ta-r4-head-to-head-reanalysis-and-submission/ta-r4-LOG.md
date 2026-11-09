# ta-r4 running log

Chronological record of every action in this phase. Append-only.

## 2026-10-21

- **Revival.** Carter: "There was a Track 1 publication that I started but didn't
  follow through with. I want to revive it and get it out for review." Then:
  "definitely run the re-analysis. Rigor over speed... use the gsd workflow, log
  everything, update Git." Track 1 = Track A = `docs/manuscript/id-vs-ref-LD.md`.
  The 2026-05-12 Genome Medicine package was never submitted.
- **Pre-phase review findings** (the reasons this phase exists):
  1. Headline claim ("identity-LD systematically inflates") is not a measurement:
     Results/Table 3 report 0 survived / 0 lost / 28 both-null; mean ΔPP.H4
     non-computable; identity-LD trait-pair comparator never run; SH2B3 survives.
  2. E-2 option A's rationale ("would move numbers in a manuscript under
     submission") is stale; transposed share 18.41% APOL1, 23.80% FTO.
  3. Table 3 lists SH2B3 canonical pairs "not executed"; Results reports PP.H4 = 1.0.
  4. Draft is ~16k words; 31 lines carry `.planning/` paths, commit hashes or DEC ids.
  5. m3-04c BLOCKER-B: EUR numbers move silently if `EUR_ukbb_pub` is built.
  6. OSF `osf-correction-v2` never posted (P-1 requires it by submission day).
- **Git repair (objects only; no tracked file changed).** `git fsck` showed 837
  broken links; `git log -- docs/manuscript/id-vs-ref-LD.md` failed with
  `unable to read tree`. Root cause found: `.git/objects/pack/pack-f4a99a73….idx`
  had NO `.pack` (a whole pack file lost on GPFS, not just loose objects).
  Repair: `git clone --mirror` of origin (== local HEAD `5c11293`) into the session
  scratchpad, `git repack -a -d`, copied `pack-3efade46….{pack,idx}` into
  `.git/objects/pack/`; orphan `.idx` moved to scratch backup (not deleted).
  Result: `fsck --connectivity-only` 0 broken/missing; every index blob present;
  manuscript history readable again.
- **Branch note.** CLAUDE.md asks for branch isolation, but this is a shared
  multi-terminal GPFS tree; switching branches would yank the working tree out
  from under any concurrent Track B session. Phase work is committed on the
  current branch (`m3-W2-aou-deltas`) with explicit-path staging only.
- Phase registered in ROADMAP.md (Track-A-R4 section) and STATE.md.
- **Fact found (scout):** all 28 empty R1 trait-pair rows are `status=no_signal`
  with `n_cs = 0` on at least one side (ta-r3 W2 SUMMARY) — coloc.susie never ran.
  Also: `coloc.abf` uses no LD matrix, so "identity LD" exists only inside SuSiE;
  the draft conflates them.
- **Inventory (background agent, read-only, banked verbatim as
  `ta-r4-INVENTORY-2026-10-21.md`):** every Track A fit (96 real + 95 identity),
  the 1000G EUR/AFR LD panels, variant lists, GTEx v8 QTL inputs and the QTL-coloc
  outputs are GONE — never git-tracked, purged from `/share` (30-day purge,
  inferred). Survivors: 8 harmonized sumstats (sha256 match), 1000G VCFs on /rs1,
  code/config, pinned `r_coloc` env, tracked aggregates. Hazards recorded:
  `02c4404` max_iter change, silent `diag(n)` fallback, AFR now routed to AoU
  paths, identity overlay depends on real panel, `envs/qtl_processing.yml`
  deleted but referenced, `coloc_summary.tsv` md5 ≠ the one the manuscript cites.
- **Discuss-phase decisions (Carter, two AskUserQuestion rounds):** three arms;
  coloc.abf fallback labelled separately; 1000G primary + UKB sensitivity in a
  separate path; OSF pre-registration posted before the production comparison;
  E-2 FIX then before/after (reverses DEC-2026-08-07 option A for Track A);
  exhaustive scope with AFR secondary; fresh draft; venue after results.
- **Orchestrator-locked (rigor rule):** regenerate everything; outputs on /rs1
  with committed sha256 manifests; known-answer reproduction (k2d identity n_CS,
  SH2B3 PP.H4=1.0 at max_iter=100) before production; named test against silent
  identity fallback; AFR/identity overlays; restore qtl_processing.yml; no Track B
  side effects.
- `ta-r4-CONTEXT.md` + `ta-r4-DISCUSSION-LOG.md` written.
- **Research complete** (`ta-r4-RESEARCH.md`, 688 lines, gsd-phase-researcher). Two of its
  corrections spot-checked by the orchestrator and CONFIRMED: (a) the SH2B3 PP.H4=1.0 came
  from L=15 lsweep fits swapped into the Stage-2 namespace (ta-sh2b3 W2 SUMMARY :153-156);
  (b) `config/regions_curated.csv` has **12** regions — the draft says "50 curated regions"
  (manuscript factual error to fix in the rewrite). Other key findings: E-2 reaches EUR
  fine-mapping (panel `.rds` has no REF/ALT; plink run without `--keep-allele-order`;
  BMI file lacks alleles); the naive QTL-side fix would orient the wrong object; p12 defaults
  differ between coloc.abf and coloc.susie; the legacy manifest admits only converged fits;
  negative controls cannot separate arms → simulation arm.
- **Carter decisions D-17..D-20** (SH2B3 exact-mix known answer; BMI allele restoration;
  fold osf-correction-v2 into the R4 amendment; AFR n=661). **Orchestrator-locked D-21..D-28.**
- **15:09 — Carter directive:** "continue with this analysis using --auto --chain choosing
  rigor over speed, but feel free to ask me any necessary questions." Interpretation applied:
  plan → check → execute without per-step confirmation; at every discretionary choice take the
  more rigorous option; STILL hard-stop for Carter at (a) the W4 OSF gate (D-27 sentinel — auto
  mode must never select past it), (b) any OSF posting or journal submission, (c) human-verify
  checkpoints whose outcome is a scientific judgement (panel manifest, known-answer findings,
  manuscript), (d) anything that spends AoU/cloud money (none planned).
- `ta-r4-VALIDATION.md` committed (`daedde5`).
- **Planning complete** (gsd-planner): 22 plans in 22 sequential waves + `ta-r4-PLAN-INDEX.md`
  (shared constants, standing rules, D-01..D-28 coverage). Planner-introduced rigor choices:
  analysis code frozen at a lock commit BEFORE the OSF post (W3c/W3d/W3e precede W4; W5–W6
  refuse to fire if analysis files differ from the lock); OSF sentinel must match the committed
  amendment sha256 AND the hash the public OSF API reports for the file on az52u; exhaustive
  36-case branch classifier; two brief-blind Codex reviews (amendment, manuscript); static
  246-row pair manifest (220 admissible) + static QTL manifest; manuscript numbers rendered only
  from FINAL tables; separate `Snakefile.ta_r4`; extra `A3_1kg_isect` arm (13 arms total).
  Corrections: legacy EUR panel count 10 (not 11); AFR 661 = 504 + ASW 61 + ACB 96 (measured).
  Committing plans before the plan-checker run.
- **Plan check iteration 1: ISSUES FOUND** (gsd-plan-checker): 7 blockers, 16 warnings, 6 info.
  Orchestrator VERIFIED B1 against `~/.claude/get-shit-done/workflows/execute-phase.md:636`:
  under auto/chain, `checkpoint:human-verify` is auto-approved with user_response "approved" and
  `checkpoint:decision` auto-selects the first option; ONLY `checkpoint:human-action` stops.
  So the LOG's promised scientific stops (item c, 15:09 entry) would NOT have held — corrected:
  every Carter-judgement checkpoint becomes `checkpoint:human-action` with a resume token the auto
  path cannot produce (`carter-approved YYYY-MM-DD`). Orchestrator fixed B7 (RESEARCH Open
  Questions marked RESOLVED → D-ids) and its own CONTEXT error (frozen file is
  `src/legacy/region_analysis/scripts/run_susie_rss.R`, not `src/snakemake/scripts/...`).
  Remaining blockers B1–B6 + all warnings sent to the planner (revision mode).
- **Plan revision iteration 1 complete** (gsd-planner): 25 plans / 25 sequential waves / 79 tasks,
  all with automated verify; VALIDATION `nyquist_compliant: true`. B1: every Carter checkpoint is
  `checkpoint:human-action`, resumable only by `carter-approved YYYY-MM-DD` + required keys, parsed
  by `src/python/ta_r4/signoff.py`, recorded verbatim in `signoffs/<ID>.yaml`, enforced by
  `test_signoffs.py`. B5: OSF API verified once per fire on the submit host → receipt bound to HEAD;
  in-job checks offline. New design element (planner, rigor rule — Carter can veto at the W4a
  lock): a THIRD negative-control set of 10 GWAS-null windows (P ≥ 1e-5 in all 8 Track A sumstats,
  seed 20261021), raising regions to 31 and the pair manifest to 346 rows / 320 admissible.
  New plan W2d applies Carter's W2c review choices (UKB HM3 restriction, QTL scope) before the lock.
- **Plan check iteration 2: 1 blocker, 5 warnings** (details + iteration-1 list banked in
  `ta-r4-PLAN-CHECK-LOG.md`). Orchestrator fixed the confirmatory row set (see that file) and
  sent all issues to the planner for revision 2 (final allowed iteration).
- **Plan revision 2 complete** (25 plans / 80 tasks): confirmatory set fixed in
  `config/ta_r4/decision_rules.yaml` (`confirmatory:` block) + `estimands.contrast_stats` +
  `run_aggregation.py` all pre-lock in W3d, rendered verbatim into the amendment; sign-off
  integrity text on all 8 human-action tasks; manifests keyed (ancestry, region_safe);
  `/data/r4` gitignored in W0a; R1_STRUCTURAL cause into the W3b findings + amendment (h).
- **Plan check iteration 3 (final): 0 blockers.** Two warnings + three info items applied by the
  orchestrator (see `ta-r4-PLAN-CHECK-LOG.md`). Planning closed; proceeding to
  `/gsd-execute-phase` under --auto --chain with human-action stops.

## 2026-10-21 — W0a executed (storage, survivors, env, baseline, DEC entries)

- **Tag:** `ta-r4-pre-baseline` (annotated, object `09e7795f`) → commit `3a2c1add`; pushed
  explicitly; `git ls-remote` shows `refs/tags/ta-r4-pre-baseline^{}` = `3a2c1add`. Created
  before any W0a commit so it marks the pre-R4 HEAD.
- **Storage:** `bin/r4_link_storage.sh` → `data/r4` -> `/rs1/researchers/c/ckclinto/coloc_analysis/ta_r4`
  (2770 on root + 8 subdirs; group `oit-rs-researcher-ckclinto`, inherited from the parent).
  Second run: same realpath, exit 0. Refusal branch measured on a scratch fake repo: a real
  `data/r4` dir → exit 2, dir untouched. `/data/r4` appended to `.gitignore` (+1/-0).
- **Survivors:** N_SRC = 92 = 24 lsweep-backup files (6 dirs × 4) + 46 stage2_narrow_validation
  + 21 `coloc_susie_R2*` + 1 zip. Copied by `rsync -a --relative` to
  `data/r4/known_answer_survivors/`; sha256(copy) == sha256(source) for 92/92; sizes equal;
  manifest `manifests/survivors_sha256.tsv` 92 rows, 0 non-hex sha256. 19 of the 92 are `.rds`.
- **Env:** `envs/qtl_processing.yml` restored, `cmp` vs `c2dfb08^` IDENTICAL.
- **Conda cache isolation — plan premise FALSE (measured):** `CONDARC=$R4_CONDARC conda config
  --show pkgs_dirs` lists THREE dirs (shared `/rs1/.../conda_pkgs` included), because conda
  always reads `~/.condarc` and `~/.bashrc` exports `CONDA_PKGS_DIRS=/rs1/.../conda_pkgs`.
  Only `CONDA_PKGS_DIRS=$R4_CONDA_PREFIX/pkgs HOME=$R4_CONDA_PREFIX/home CONDARC=$R4_CONDARC`
  listed exactly one. That recipe also drops `~/.condarc`'s `channel_priority: strict` and
  `solver: libmamba`. Also measured: Snakemake 7.32.4 `--conda-cleanup-pkgs` defaults to None
  (cleans only when the flag is passed); the 2026-10-11 incident was Snakemake 9.x. Hand-off to
  W0b2 (`bin/r4_fire.sh`). `~/.condarc` NOT edited.
- **Baseline** (`tests/m3 tests/phase1 tests/phase2 -q -rA`, 16m10s): 1474 ids / 1428 passed /
  46 skipped / 0 failed (tests/m3 alone 1299 / 1265 / 34 / 0 = the 2026-09-19 record). Skipped
  ids = collected − PASSED ids; per-file skip counts equal the `-rA` SKIPPED [N] sums for all
  11 files. No pre-existing failure. Log: `data/r4/logs/tests_baseline_W0a.log`.
- **RED → GREEN:** `test_storage_on_rs1.py` 6 failed / 1 passed before the link, config and
  manifest existed; 7 passed after. Every negative control was also seen biting: each checker
  blinded → its test RED; a `/share/clintonlab` literal dropped into `config/ta_r4/` → RED.
- **DEC entries** appended (0 removed lines): `DEC-2026-10-21-ta-r4-e2-fix-supersedes-option-a`,
  `DEC-2026-10-21-osf-correction-v2-retired-unposted`, `DEC-2026-10-21-sh2b3-known-answer-premise`.
- **Wave close:** QUICK 7 passed (32 s cold first run, 0.4 s warm); HEAVY 0 selected (exit 5,
  no r4_heavy tests yet); `test_source_freeze_pins.py` 39 passed; FULL 1481 ids / 1435 passed /
  46 skipped / 0 failed (14m49s) = baseline 1474 + 7 new ta_r4; join vs baseline: 0 removed,
  7 added, 0 outcome changes. fsck before/after: 0 missing/broken.
- **Commits:** `c8130c5a` (T1), `c26d77ad` (T2), `6f968b1b` (T3 DEC), pushed.
- ⚠ **Hand-off to W0b1:** `tests/ta_r4/__init__.py` makes pytest import the test dir as the
  package `ta_r4` (`tests/` has no `__init__.py`), which shadows `src/python/ta_r4`. Measured
  on a scratch mock: `from ta_r4.paths import X` → `ModuleNotFoundError: No module named
  'ta_r4.paths'`. Without the `__init__.py`, `tests/ta_r4/conftest.py` becomes the bare
  `conftest` and breaks the tests/m3 `from conftest import R_SUBPROCESS_TIMEOUT_S` imports
  (also measured). W0b1 must pick a resolution before its first `from ta_r4...` test.
- **Orchestrator decisions after W0a (technical, not scientific):**
  (1) `ta_r4` import clash (tests/ta_r4 package shadows src/python/ta_r4): keep all plan paths;
  `tests/ta_r4/__init__.py` inserts `src/python` on sys.path then
  `__path__ = pkgutil.extend_path(__path__, __name__)`; W0b1 proves it with a test that
  `from ta_r4.paths import ...` imports and that `tests/m3` `from conftest import ...` still works.
  (2) conda isolation for W0b2's fire script = `CONDA_PKGS_DIRS=$R4_CONDA_PREFIX/pkgs
  HOME=$R4_CONDA_PREFIX/home CONDARC=$R4_CONDARC` (measured to list exactly one pkgs_dir), with
  `channel_priority: strict` and `solver: libmamba` written into the R4 condarc.
  Noted: /rs1 R4 dirs are group `oit-rs-researcher-ckclinto` (inherited), not `clintonlab`.

## 2026-10-21 — W0b1 executed (arms, paths, overlays, sign-off helper + sentinels)

- **Arms:** `src/python/ta_r4/arms.py` ARMS = 13 arms (8 production + 5 repro); stage is
  code-owned (`test_stage_is_code_not_config`). `paths.result_dirs("fits")` = 8 dirs (incl.
  A3_1kg_isect), `result_dirs("coloc")` = 10 (8 + A1_EUR + A1_AFR); no repro dir.
- **Overlays:** base + 13 arm overlays in `config/ta_r4/`; chain replaced wholesale + pinned;
  `config/pipeline.yaml`, Snakefile, all rules and the frozen script unchanged (`git diff --quiet` 0).
  Repro policy differs from `config/susie_policy.yaml` in one line (`max_iter_retry` 200 -> 100).
- **Import clash (orchestrator decision) fixed:** `tests/ta_r4/__init__.py` puts src/python first +
  `pkgutil.extend_path`; `test_import_isolation.py` RED without extend_path
  (`No module named 'ta_r4.arms'`), GREEN with it, incl. a tests/m3 `from conftest import` module
  in a subprocess, both orders.
- **Sign-off:** `ta_r4.signoff` rejects `approved` / `Approved.` / no date / bad date / future /
  pre-min / missing / empty / enum / unknown / duplicate keys (all `WAIT:`). Negative control: the
  plan's literal relaxed regex `^(carter-)?approved` turned 8 valid-reply tests RED but left the
  bare-approved rejections green (second layer: no date, missing key). A relaxation that also
  defaults the date turned 2 rejection tests RED. `test_signoffs.py`: every sentinel blinded →
  its fixture tests RED (4/4/1/1/1/1).
- **Hand-off to W2a/W2c:** sentinel reads Carter cells as `F` + `F_source == "Carter <date>"`;
  W2a's trait manifest needs a `type_source` column if `type` can be UNRESOLVED; review_decisions
  carries `trait_facts: {trait.<t>.<anc>.<field>: value}`. W4a: confirmatory_sha256 =
  `ta_r4.signoff.canonical_sha256(decision_rules["confirmatory"])`.
- **Wave close:** QUICK 91 passed, 8.3 s wall (7+2+25+35+22); HEAVY 0 selected; freeze pins 39
  passed; FULL 1565 ids / 1519 passed / 46 skipped / 0 failed (15m07s). Join vs
  tests_baseline_W0a.tsv: common 1474, removed 0, added 91 (all tests/ta_r4, passed), outcome
  changes 0; 1474 + 91 = 1565, 1428 + 91 = 1519.
- **Commits:** `714df7a5` (T1), `c6e9297f` (T2), docs commit follows; fsck clean before/after each.
- **Orchestrator spot-check of W0b1** (`47c9e9b`): origin HEAD matches; quick suite re-run by the
  orchestrator. Hand-offs carried forward: W2a must add a `type_source` column to the trait
  manifest if any trait `type` can be UNRESOLVED (W2c-T4 sign-off check reads `F_source`);
  `review_decisions.yaml` trait facts as `trait_facts: {trait.<t>.<anc>.<field>: value}`; W4a-T3
  prints `ta_r4.signoff.canonical_sha256(decision_rules["confirmatory"])` for Carter to sign.
- **18:39 — SESSION CLOSE requested (Carter relocating).** Terminal is not in tmux/screen, so the
  W0b2 executor would have died at an unknown point; the orchestrator stopped it via TaskStop
  after Task 2's commit (`ab77e97`) while Task 3 was mid conda-frontend solve. Verified: no
  conda/snakemake/pytest/bsub processes, `bjobs` empty, `data/r4/gate` absent. Task 3 WIP left
  uncommitted and inventoried (sha256 prefixes) in HANDOFF.json `ta_r4.in_progress`.
  Measured by W0b2 before the stop: compute node c017n03 has no route to api.osf.io (curl exit 28);
  login01 returns 200.

## 2026-10-22 — W0b2 resumed and closed (Task 3 finished, Task 4 wave-close)

- **Resume.** T1 `9bb65c01` and T2 `ab77e97c` were already committed. Their tests were re-run: T1 28 passed;
  T2 is inside the Task 3 run. The Task 3 WIP sha256 prefixes matched the hand-off. It was read line by line against
  the spec and conformed, except for the 3 fixes below. The stopped executor's T1/T2 RED evidence had never been
  written down; it was re-derived after the fact (modules moved aside → ImportError at collection; (o)-skip →
  `test_o_receipt_head_sha` DID NOT RAISE + `test_env_vars_do_not_change_pass`, 2 failed / 46 passed).
- **Task 3 RED → GREEN.** With the implementation moved to scratch: 9 failed / 55 passed / 3 errors. Restored on the
  unmodified WIP: 67 passed. Six more negative controls (gate call removed; CLI blinded; base config;
  crosswalk injection; forbidden path in a probe shell; ld_matrix_region_id name) all RED, each restored byte-identically.
- **Fixes to the WIP.** (1) The R4 condarc now has `channel_priority: flexible`. `envs/plink.yml` (bioconda first)
  is UNSATISFIABLE under strict with today's repodata (this is what stopped the previous solve; reproduced in
  scratch: strict rc=1, flexible rc=0). (2) The profile has `conda-frontend: conda` (Snakemake 7.32.4 defaults to mamba
  from condabin; isolation was measured for conda). (3) `bin/r4_fire.sh` runs `mkdir -p data/r4/logs/lsf`
  (bsub_wrapper only creates logs/lsf).
- **Env solve from scratch.** The stale `55c377a7…_.yaml`, `pkgs/`, `home/` and `condarc` were removed from the confirmed
  R4 prefix. `--conda-create-envs-only` rc=0 (10m08s). `--cores 1 --profile ''` was accepted (localrules), 4/4 steps.
  The three probe tools resolve inside the R4 env dirs. Lockfiles: plink 110 lines / qtl_processing 186 /
  python_stats 252 / r_coloc_named 224, each with `dependencies:`. Shared `/rs1/.../conda_pkgs`: archives 0 → 0,
  entries 2188 → 2188 (identical listing sha256), du 23348M → 23348M. R4 pkgs: 809 entries / 403 archives.
  `R4_PLINK=/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin/plink`
  (PLINK v1.90b6.21).
- **Network probe (informational).** The LSF row was verified against `data/r4/logs/net_probe.404985.{out,err}` (c017n03,
  000, curl exit 28, 20004 ms timeout). The submit host was re-measured today: login03 → 200. The gate design does not depend on it.
- ⚠ **OSF anonymous-read finding (NOT fixed; for Carter / W4b).** `fetch_osf_file('k8w7n')` → HTTP 401.
  `curl` `/v2/files/k8w7n/`, `/v2/nodes/az52u/` and the redirect target `/v2/files/69ed77ef…/` → 401 "Authentication
  credentials were not provided". `/v2/registrations/pvb5j/` → 200, `public: True`. So the k8w7n known-answer
  dict could not be recorded. verify_online is anonymous by design, so it would fail closed (i) on any non-public
  node. W4b must confirm an anonymous API read returns 200 for the posted R4 file before the sentinel is written.
- **Measured.** Snakemake 7.32.4 prints the DAG-time OsfGateError on stdout (stderr empty). Tests assert on both streams.
- **Wave close.** QUICK 180 passed / 6 deselected, 24.9 s wall. HEAVY 6 passed (204 s). Freeze pins 39 passed.
  FULL 1660 ids / 1614 passed / 46 skipped / 0 failed (19m09s). Join vs tests_baseline_W0a.tsv (junit XML): common
  1474, removed 0, added 186 (all tests/ta_r4, passed), changed 0; tests/m3 1299/1299, 0 changed;
  1474 + 186 = 1660, 1428 + 186 = 1614. The main Snakefile / pipeline.yaml / frozen script / finemap.smk are unchanged.
  PLAN-INDEX §A now records the 10 NC_NULL tiles, the full conda-isolation recipe + flexible priority, and R4_PLINK.
  ARMS = 13 = §A (no change). Commits: `2d4da61e` (T3) + the wave-close commits; fsck clean before/after.

## 2026-10-22 — W0c executed (D-13 receipts, validator, r4_run_finemap, frozen-script e2e)

- **Task 1 RED → GREEN.** `test_no_silent_identity.py` written first: `55 failed in 2.20s`, all
  `ModuleNotFoundError: No module named 'ta_r4.validate_r4_fits'` / `No module named ta_r4.write_ld_receipt`.
  GREEN: `54 passed, 1 skipped` (skip = live gate, "no production fits yet (W5a enables)"). 24 injected silent shapes
  are each rejected by name (NULL-R identity/None, identity_fallback, ld_dir_missing as status and as ld_status,
  LD_DECLARED_ABSENT, matrix != declared, non-authoritative, non-allele-aware, md5 != manifest, LD fields missing,
  AFR receipt on an EUR fit, no row, no receipt, panel absent, receipt declared != fit, status not loaded, arm/mode
  mismatch, fallback_identity in ld_status; A2: points at the real panel, sha256 != manifest, NULL-R, declared not
  the arm's panel, identity_fallback).
  Negative controls: validator made to ignore `convergence_status` → `FAILED [a2_identity_fallback]`,
  `FAILED [identity_fallback]`, `2 failed, 52 passed`; receipt md5 check disabled → `FAILED test_receipt_writer_exits_3[md5_mismatch]`.
  Both restored (`cmp` identical). CLI on an identity fixture from src/python: 5 VIOLATION lines, `echo $?` → `1`.
- **Task 2 RED → GREEN.** e2e + variant-set tests written before `commands.py`/the rule: `3 failed, 1 passed, 1 skipped,
  6 errors` (ImportError `ta_r4.commands`; r4_run_finemap absent from `--list`; production dry-run raised no OsfGateError).
  GREEN with freeze pins: `49 passed, 1 skipped`; with the controls added later: e2e 9 + variant 4 (1 skip) + silent 56 (1 skip).
- **Fixture facts (60 SNPs, seed 20261021).** A3: `status ok`, `ld_matrix data/r4/ld/EUR_1kg_r4/FIX_1.rds` (== declared),
  `ld_status ld_loaded;overlap_ok;59;0.983`, `ld_allele_flipped 1`, `ld_allele_dropped_palindromic 1`, `ld_overlap 59`.
  A2: `ld_matrix data/r4/ld/EUR_identity_r4/FIX_1.rds`, same ld_status. Retained variants A3 59, A2 59, identical sets
  (60 − 1 palindrome = 59).
- **Missing-panel negative control (recorded verbatim):** the frozen script exited **rc 0** with
  `ld_matrix 'identity'`, `ld_status 'ld_dir_missing'`, `ld_file_declared 'data/r4/ld/EUR_1kg_r4/FIX_1.rds'`;
  validator violations `['LD_MATRIX_IDENTITY', 'LD_DIR_MISSING', 'LD_STATUS_NOT_LOADED', 'IDENTITY_SUBSTRING',
  'LD_MATRIX_NE_DECLARED']`; validator CLI rc 1. (In the rule, `test -s` and the receipt writer stop this case earlier.)
- **Rule-level runs (fixture repo from make_fixture_repo):** repro_routeC r4_run_finemap ran for real (receipt → frozen
  script → validator legacy_any `ld_source_class=real violations=0` → receipt one-liner `ld_fields_present`);
  the printed shell contains the three `shlex.join(commands.*)` strings. A3_1kg dry-run → OsfGateError `sentinel absent`.
  Manifest md5 swapped → job fails with `LD_RECEIPT_REFUSED ... != manifest md5`, frozen script never started, no JSON.
- **Task 2 sabotage controls (all RED, all restored `cmp` identical):** `--ld-file` dropped from fit_command →
  A3 fit rc 0 on `identity`/`ld_dir_missing`, 2 tests RED; receipt md5 check off → `test_rule_fails_on_panel_swap` RED;
  payload drops one variant → A2 58 vs A3 59, fixture set test RED; gate call removed from the input function →
  `test_rule_production_arm_refused_without_gate` RED. Live gates carry in-test controls (empty arm dir / identity fit;
  one arm of a pair alone / 58 vs 59 ids).
- **Measured:** the frozen loader also accepts a `Matrix::Diagonal` payload (rc 0, `ld_loaded;overlap_ok;59;0.983`);
  the builder keeps base `diag(n)`. The finemap.smk receipt one-liner is copied verbatim and produces identical output
  on the A3 JSON (test). `conda:` uses `workflow.basedir/envs/r_coloc.yml` (byte-identical to rules/envs/r_coloc.yml;
  plain `envs/r_coloc.yml` resolves rule-relative, which the fixture repo lacks — first rule run failed on it).
- **D-28:** `git diff --quiet HEAD -- run_susie_rss.R` → 0; `test_source_freeze_pins.py` 39 passed.
- **Wave close.** QUICK 235 passed / 20 deselected, 18.8 s wall. HEAVY 18 passed / 2 skipped (231 s). FULL
  1729 ids / 1681 passed / 48 skipped / 0 failed (19m28s). Join vs W0b2 junit (`full_W0b2.xml` → `full_W0c.xml`):
  common 1660, removed 0, changed 0, added 69 (silent 56, e2e 9, variant 4; 67 passed + 2 live-gate skips);
  1660 + 69 = 1729, 1614 + 67 = 1681, 46 + 2 = 48; tests/m3 1299/1299, 0 changed. sparse_parent_benchmark.tsv restored.
  Commits `dbc2c19d` (T1), `fef3589f` (T2), wave-close commit follows; fsck clean before.

## 2026-10-22 — W0d executed (run_coloc_pair_r4.R, r4_coloc_pair / r4_coloc_A1, toy --use-conda e2e)

- **Task 1 RED → GREEN.** test_coloc_pair_r4 / test_fallback_labelled / test_priors_constant written first, fixture
  fits built by the frozen script via `commands.fit_command`: `16 failed, 14 passed, 2 skipped`; every failure
  `Fatal error: cannot open file 'src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R'`. The 14 passes are the gate-checker
  unit tests (controlled below); the 2 skips are the live gates. GREEN: `30 passed, 2 skipped` (102.7 s).
- **Fixture numbers (verbatim test prints).** coloc_susie (FIXP_SAME) `pp_h4_max 0.999999999998337 direct
  0.999999999998337 max|diff| 0.0`. A1_matched (FIXP_MIX, n_snps 57) p12_primary `0.999441327677598`, direct coloc.abf
  with explicit priors identical (|diff| 0.0), package-default coloc.abf `0.999720585788306` (!=). Fallback (FIXP_NULL,
  n_cs_b 0): p12_primary fallback `0.0267819546730813` == A1_matched `0.0267819546730813`; p12_sensitivity
  `0.0521667809824499` == `0.0521667809824499`. A1 allvars n_snps 60 (59 allele-matched + 1 position-only) vs matched 57.
- **Sabotage REDs (each restored, `cmp` identical):** `P12 <- 1e-5` hard-coded → test_priors_constant `2 failed`
  (`test_every_mode_records_yaml_priors`, `test_explicit_prior_moves_the_answer`); fallback labelled `coloc_susie` →
  test_fallback_labelled `2 failed` (`assert ('coloc_susie' == 'fallback_abf'`); gate globbing every `results/*/coloc`
  → both repro-tree tests RED; n_cs check removed / p12 not compared / cross-arm check no-op → the matching checker
  test RED; UNMAPPED refusal disabled → override test RED.
- **Measured (name alignment).** The frozen script renames chr:pos sumstats SNP_IDs to LD-panel rsids
  ("Overriding 59 sumstats SNP_IDs with LD-panel rsids"). On that shape run_coloc_susie.R prints
  `fit_b=1/57 (intersect=0)`: it drops every non-CS column and colocalizes nothing. run_coloc_pair_r4.R stops with
  UNMAPPED_FIT_NAMES instead. On the rsid-vs-chr:pos shape both give `intersect=57`, same hits/nsnps/PPs.
  ⚠ DECISION NEEDED before W4 (analysis frozen at the OSF lock): W2a's 1000G panels carry .bim IDs (likely rsids),
  so production hypertension/stroke/t2d fits will have the override shape and refuse.
- **Measured (reader).** The named r_coloc env has no R.utils, so run_coloc_susie.R's `fread(<.bgz>)` fails and it
  silently skips its rewrite there. run_coloc_pair_r4.R uses the frozen script's reader (`fread(cmd = "gunzip -c ...")`).
- **Task 2.** Toy e2e RED (rule held aside): `4 failed, 1 passed` — `MissingRuleException: No rule to produce
  data/r4/results/A1_EUR/coloc/FIX_1__EUR__asthma_vs_bmi.matched.p12_primary.json`; the pass is the receipt negative
  control (fit rule only). That run was the first r_coloc solve into the R4 prefix: env `0f3436279d4146c376747a0ea5bfd4bf_`
  (R 4.4.2, coloc 5.2.3, susieR 0.14.2, R.utils 2.12.3). GREEN `5 passed`: A3_1kg 24 targets rc 0 in 50.3 s,
  A2_identity 12 targets rc 0 in 26.0 s. Negative control: FIX_2 A3 manifest row deleted → `Error in rule
  r4_run_finemap`, `LD_RECEIPT_REFUSED: no manifest row (EUR, FIX_2)`. Coloc gate refusal test (A1 allvars target, no
  sentinel) → OsfGateError; with the gate call removed → `MissingInputException in rule r4_coloc_A1` (RED), restored.
- **Shared conda cache** `/rs1/.../conda_pkgs`: before 2188 entries / listing sha256 `f094b37d…9085` / 23348 MB /
  0 archives; after all --use-conda runs identical, 0 entries newer than the start. R4 pkgs 809 → 1095 (546 archives).
- **Production dry-run (real repo).** Dirty tree: `REFUSED: uncommitted changes ... ?? src/snakemake/rules/ta_r4_coloc.smk`
  (rc 2). After commit: `OsfGateError: (a) sentinel absent` from verify-online (rc 1), Snakemake never started. Direct
  `$SMK -n`: `InputFunctionException in rule r4_coloc_pair ... OsfGateError: (a) sentinel absent` (and r4_coloc_A1).
  `bin/r4_fire.sh repro repro_routeC --list` lists r4_coloc_pair; r4_coloc_A1 is listed only under A3_1kg.
- **Wave close.** QUICK 254 passed / 39 deselected, 36.7 s wall. HEAVY 35 passed / 4 skipped (live gates), 7m14s.
  Freeze pins 39 passed. FULL 1767 ids / 1717 passed / 50 skipped / 0 failed (22m43s). Join vs `full_W0c.xml`:
  common 1729, removed 0, changed 0, added 38 (coloc_pair 11, fallback 11, priors 10, toy 6; 36 passed + 2 live-gate
  skips); 1729 + 38 = 1767, 1681 + 36 = 1717, 48 + 2 = 50; tests/m3 1299/1299, 0 changed. sparse_parent_benchmark.tsv
  restored. Frozen files (run_susie_rss.R, run_coloc_susie.R, Snakefile, pipeline.yaml, finemap.smk, envs/r_coloc.yml,
  Snakefile.ta_r4) 0-diff. Commits `99e05961` (T1), `c536547c` (T2), wave-close commit follows; fsck clean before.

## 2026-10-22 — W1 executed (E-2 orientation: BMI alleles, panel REF/ALT, QTL-beta orientation)

- **Unit 1 (D-18) RED → GREEN.** test_bmi_allele_restoration RED `5 failed, 5 errors` (`No module named
  ta_r4.restore_bmi_alleles`); GREEN `10 passed`. Controls (each restored, `cmp` identical): flipped class removed →
  class-count test RED (`{'exact': 2, ..._mismatch': 4}`) while `test_report_reconciles` stayed GREEN (the class test is
  the discriminating one); tolerance forced to 0 → 5 RED; sha256 check disabled → the 2 refusal tests RED.
- **Unit 1 real run** (`restore` 44 s): frozen bmi.EUR.tsv.bgz has **2,336,269** rows and the Yengo source
  **2,327,244** (the plan's interfaces block had the two counts swapped). Report: n_frozen 2336269 = exact 2327244 +
  flipped 0 + value_mismatch 0 + unjoined 9025 (awk: RECONCILED; equals `zcat | tail -n +2 | wc -l`). n_kept 2327244.
  n_sign_uninformative 23896 (all frozen BETA "0.0"; kept as exact). n_ambiguous_source 0 (9 frozen duplicate keys,
  byte-identical rows in both files). Raw cross-check (seed 20261021, 10000 kept rows): Tested_Allele == ALT
  10000/10000 (rate 1.000000). **FINDING:** the 9,025 unjoined rows are absent from the Yengo M1 file and are ALL A/T
  (3,844) or C/G (5,181) in the raw file, which has all 2,336,269 rows — they are dropped from R4, not restored.
  Output sha256 2f87e771…b1b4 (.bgz) / 36d01d38…572a (.tbi); index -s1 -b2 -e2 -S1 (frozen .tbi parameters).
  sumstats_r4_sha256.tsv 11 rows (9 inputs m1-verified + 2 outputs); `sha256sum -c` 11 OK.
- **Unit 2 RED → GREEN.** test_plink_ld_to_rds_ref_alt RED `8 failed, 3 passed` (`long flag "emit-ref-alt" is
  invalid`; the passes are the flag-absent identity and the plink property). GREEN `11 passed`, 0 skipped. Measured:
  `--keep-allele-order` R[1,2] 0.5000000000 == cor(A1 dosages) 0.5000000000; SNP 2 A1/A2 swapped with recoded dosage
  → -0.5000000000 == cor(d1, 2-d2); without `--keep-allele-order` → -0.5 (A1 major is re-coded). Sabotage
  `ALT = A2` → 2 RED (label assertions; a global label swap leaves every pairwise LD sign unchanged); per-SNP
  inconsistent ALT → known-answer correlation assertion RED; unconditional attr → 4 identity tests RED. My first swap
  test was wrong (kept the .bed, so A1 dosage was unchanged); fixed to recode the dosage as the plan says.
- **Unit 3 RED → GREEN.** test_qtl_orient RED `10 failed, 2 passed` (passes = flag-absent identity); GREEN 12 passed.
  `join$orient` sabotage → only `test_transposed_qtl_is_negated` RED (PP.H4 0.7488 vs 0.7178); `qtl_orient: FALSE`
  emitted off-flag → the 4 identity tests RED. Task verify (4 files) 141 passed.
- **Wave close.** QUICK 287 passed / 39 deselected, 112.2 s wall (budget 120 s; slowest = test_qtl_orient e2e ~11 s
  each). HEAVY 35 passed / 4 skipped (live gates), 6m59s. Freeze pins 39 passed. FULL 1800 ids / 1750 passed /
  50 skipped / 0 failed (24m01s, junit data/r4/logs/full_W1.xml). Join vs full_W0d.xml: common 1767, removed 0,
  changed 0, added 33 (bmi 10, plink 11, qtl_orient 12; all passed); 1767 + 33 = 1800, 1717 + 33 = 1750, 50 + 0 = 50;
  tests/m3 1299/1299, phase1 38/38, phase2 137/137, 0 changed (D-15). sparse_parent_benchmark.tsv restored. Shared
  conda cache after HEAVY: 2188 entries / f094b37d…9085 / 23348 MB / 0 archives (= W0d). Frozen files 0-diff.
  Commits `fb0a5b5c` (T1), `4896e011` (T2), `e7224a91` (T3), wave-close commit follows; fsck clean before.

## 2026-10-26 — W2a executed (EUR 1000G legacy + R4 panels, A2/k2d payloads, catalogs, trait manifest)

- **Task 1** (`f19d6398`, previous executor, 2026-10-23): Zenodo 10515792 tgz md5 `a7773ab485827b533cb300c76356d76b`, size
  288277344 (re-measured today); 66 members, single top dir; 22 `.fam` sha256 distinct = 1; **EUR n_samples = 489** (D-25;
  not 503). RED re-derived today (module aside → `1 error`), HTML-magic sabotage → `test_html_body_with_200_fails_magic` RED.
- **Resume.** Earlier fire: 130/136 then a killed resume fire; stale lock (5 W2a outputs, no live process/job) → unlocked via
  r4_fire.sh. All earlier W2a outputs DELETED and rebuilt; rebuild byte-identical (135/135 md5). Fire 1 hung at 124/136 on 7
  LSF jobs that exited before their script ran ("Cannot open your job file", c018n02/c014n04/c002n01; no .jobfailed marker)
  → stopped, re-fired, 12/12; final dry-run "Nothing to be done".
- **Counts.** EUR_1kg_r4 29, EUR_identity_r4 29, legacy_repro/EUR 10, k2d 24 (EUR 12 + AFR 12 = 24 distinct pairs in the k2d
  summary), catalogs 43 (legacy 12 + r4 31); 29+29+10+24+43 = 135 files. data/processed/ld_reference absent → 0 Track B writes.
- **SNP_ID format (pre-W4 decision input; nothing chosen).** Panels: R4 86,035/86,035 rsid, legacy 68,214/68,214 rsid, 0 chr:pos.
  Sumstats in the 10 admissible regions: hypertension/stroke/t2d EUR and stroke/t2d AFR 100% chr:pos; bmi 100% rsid; asthma
  EUR/AFR rsid or empty (32,491 / 23,471 empty). So hypertension/stroke/t2d fits will take the override shape.
- **Orientation.** A1 identical legacy vs R4 for all 68,214 variants (LDSC .bim A1 = minor): R4 == legacy matrices including sign.
- **Manifests** legacy 10 / R4 29 / identity 29 / k2d 24; max asym 0, max |diag-1| 0, finite; identity_exact 29/29; chmod a-w
  92 .rds. **Live gate** 8 passed, 0 skips; 181 checks = md5 92 + n_var 10 + |R| 10 + identity 29 + has_ref_alt 39 + sh2b3 1,
  all PASS, **0 FINDING rows**. **SH2B3 legacy n_var 895**; spectrum 210 neg / 81 < -1e-6 / rank 451 / cond 1.466e+07 = W1.5 audit.
  Fake-root controls: legacy→R4 swap → has_ref_alt FAIL; identity wrong region → identity FAIL; legacy wrong region →
  n_var + |R| FAIL; n_var 894 → FINDING (not FAIL). Unit sabotage (symmetry, duplicate, identity, md5) each RED.
- **Trait manifest** 8 rows. ⚠ **UNRESOLVED for W2c:** hypertension.EUR sdY. The file is Evangelou 2018 SBP (continuous, mmHg;
  sha256 = the sbp inventory entry), type quant; sdY.est median 10.72 (record only). BMI quant sdY 1 (inverse-rank-normal;
  sdY.est 1.012). asthma/stroke/t2d cc. stroke.EUR = METASTROKE N 75000 constant; stroke.AFR / stroke.EUR sha256 ≠ GIGASTROKE
  inventory entries; t2d.AFR N = Neff.
- **Wave close.** QUICK 304 passed in 125.7 s (> 120 s) → 5 test_qtl_orient e2e marked r4_heavy → 299 passed / 46 deselected,
  73.1 s. HEAVY 42 passed / 4 skipped (10m39s). Pins 39 passed. FULL 1819 ids / 1769 passed / 50 skipped / 0 failed
  (27m49s, `full_W2a.xml`). Join vs full_W1.xml: common 1800, removed 0, changed 0, added 19 (fetch 11, panels 8; passed);
  1800+19 = 1819, 1750+19 = 1769; tests/m3 1299/1299, phase1 38, phase2 137, 0 changed. sparse_parent_benchmark.tsv restored.
  Shared conda cache 2188 / f094b37d…9085 / 0 archives before and after (23348 MB before; 0 entries newer). Frozen files 0-diff.
  Commits `8a5c75e2` (T2), `b266e1d8` (T3), wave-close commit follows; fsck clean before/after each.

## 2026-10-27 — W2b executed (AFR 661/504 panels, legacy AFR repro, UKB 337k loader + native/isect panels)

- **Resume.** The stopped session's WIP was verified by content, not presence. Restored 2 purged forensics logs (not committed).
- **Task 1** (`37a391e4`): AFR504 = AFR.samples (sha256 97ff9e57…); AFR661 = 504 + ASW 61 + ACB 96 (157, 0 overlap); .fam IIDs ==
  sample lists. 20 R4 panels: n_var == .bim, REF/ALT == .bim A2/A1, asym 0, |diag-1| 0. 10 AFR661 identity payloads identical()
  frames. Legacy AFR 12 (= frozen 36 AFR fits / 3 traits; TRACK-A-FROZEN-NUMBERS.md:64 + IDENTITY-LD-K2D-FIT-SUMMARY.tsv), **12/12
  use_identity placeholders**. FINDING afr_panel_size.tsv: BMI_5q13_3 21323/21154 and PYHIN1 20818/20686 > 16000.
- **Task 2** (`f6d637aa`): RED re-derived (module absent → collection error; 8 sabotages each RED; the two diagonal guards mask
  each other, both off → 3 RED). Live tile chr12_111000001_114000001: diag == 1 exactly, symmetric; sign agreement 21409/21410 =
  0.999953 (745 shared, 717 flipped). No-D.R.D control still passed at 0.992760 overall → mixed-orientation assertion added:
  154/154 = 1.0, control 0/154 RED. Halving control → 3 RED.
- **Task 3** (`fa91305f`, fixes `0e621884`, `1d900305`): 121 candidate tiles HEADed; 7 chr6 26-35 Mb .npz are 404 → HLA native has
  a 28-33 Mb hole. 41 files fetched; tile manifest 76 rows (39 gz + 37 npz), size/ETag == HEAD, sha256 == disk. Native 30, isect
  29, 1000G isect 29; isect frames identical() 29/29; isect sign agreement min 0.990293 (APOL1), mixed min 0.999347. Native > 16000:
  HLA 34361, PYHIN1 26050, BMI_5q13_3 24121, SLC2A9 16752. Isect 71,769 of 86,035 EUR_1kg_r4 variants (palindromes dropped).
  Fires: LSF exit-255 losses stalled #1, #2 and #4 (#4 at 52/60: 7 jobs lost) → stopped, unlocked (UKB-only lock), re-fired. UKB
  rebuilt from scratch twice (declared code input changed); all builds byte-identical (122/122, 147/147). UKB jobs ran in the
  r_coloc job env (0f343627…, yaml == envs/r_coloc.yml, R 4.4.2).
- **Wave close.** QUICK 330 passed / 50 deselected, 74.6 s (one load-affected run 144.5 s). HEAVY 46 passed / 4 skipped (14m26s).
  Pins 39 passed. FULL 1854 ids / 1804 passed / 50 skipped / 0 failed (29m54s, full_W2b.xml). Vs full_W2a.xml: common 1819,
  removed 0, changed 0, added 35 (loader 30, triangle 4, fetch 1); tests/m3 1299 (1265/34) unchanged, phase1 38, phase2 137.
  Shared conda cache 2188 / f094b37d… / 0 archives before and after. Frozen files 0-diff. fsck clean before/after each commit.

## 2026-10-28 — W2c Tasks 1–3 executed (GTEx QTL downloads, static QTL manifest, W2 review packet); STOPPED at Task 4

- **Task 1** (`e3afa4dd`). Downloader PID 1793323 `FINISHED todo=98 failed=0`; `RESOLVED_COUNT 98 = 49 tissues x 2 sources`;
  `HEAD_OK 98 total_bytes 192123270766`. Verify awk → `98 0`. sum(size) + sum(tbi) = `191965693189 + 157577577 = 192123270766`
  = HEAD_OK total. `du -sh data/r4/downloads/eqtl_catalogue` → `180G`; 98 QTD dirs + empty `_tbi_stage`; `find data/raw -newer
  fetch_eqtl_catalogue.py` → nothing. Published checksums: the QTD000116, QTD000121, QTS000015 and sumstats/ listings have no md5
  file (checked 2026-10-28) → all 98 rows `no published checksum`.
- **Task 2 RED.** First recorded in `33d5f640` (`6 failed, 8 errors`, ImportError) and its controls in `14318720`. Re-derived
  today (pyc deleted, PYTHONDONTWRITEBYTECODE=1, cmp-restored): module moved aside → `6 failed, 8 errors in 1.06s`; check_schema
  no-op → `FAILED test_schema_rejects_status_or_tier_column`; `"tier"` appended to COLUMNS → `FAILED
  test_schema_rejects_status_or_tier_column`, `FAILED test_written_manifest_deterministic`. Committed-manifest controls:
  `tier` column appended to the TSV → `Left contains one more item: 'tier'` (RED); stroke rows dropped → `assert 93240 ==
  (23310 * 5)` (RED); restored sha256 0f10d922…4ad8.
- **Task 2 build** (LSF 429971–429975, 429980 after `Cannot open your job file` on 429975). `review_decisions.yaml` absent →
  `full`. `scope=full frozen_tissues=49 (src/python/build_tissue_n_lookup.py:25 GTEX_V8_TISSUE_N_FALLBACK) files=98 regions=10
  traits=5 features=23310 rows=116550`, 205 s. full_a == full_b == committed sha256 `0f10d9223833…4ad8`; tissues_frozen
  identical to full; eqtl_only == tf+eo `fce5f86b…5c85` (105745 rows, 21149 features). **Reconciliation:** `awk 'NR>1' | wc -l`
  = **116550** = 5 × **23310** unique (region, source, tissue, feature); dropping qtl_row_id+trait also gives 23310. Per source:
  eqtl 105745 + sqtl 10805 = 116550. Per region (rows/features): 9p21 4055/811, APOE 30930/6186, APOL1 10070/2014, BMI_5q13_3
  12195/2439, CXADR_F2RL1 5855/1171, FTO 4905/981, MC4R 5465/1093, PYHIN1 27125/5425, SH2B3 9740/1948, SLC2A9 6210/1242; sum of
  features 23310. Per trait 23310 × 5. Groups (region, source, qtd) 899 = eqtl 490 + sqtl 409.
- **Frozen QTL layer re-derived.** Legacy `build_manifest` with gtex_eqtl+gtex_sqtl and the 49-tissue fallback → **1274** rows
  (= TRACK-A-FROZEN-NUMBERS.md 1274): 10 regions (HLA_6p21 in, BMI_5q13.3 out), EUR, 4 traits (first per region), 13 curated
  genes. R4 coverage: 412 / 1274 (eqtl 379, sqtl 33). Missing 862 = HLA 98 + SLC2A9 ENSG00000109107 98 + CXADR 98 + F2RL1 98
  + MC4R 98 + 372 (sqtl 359, eqtl 13 where the gene lacks rows in that tissue). **FINDING** for Task 4 (packet §7).
- **t_row.** No legacy QTL logs survive (`find results data/r4/known_answer_survivors -path '*qtl*' -name '*.log'` → 0). Fixture
  timing LSF 429976 (tests/phase2 has no runnable fixture; used the test_qtl_orient 200-variant fixture): `N 15 median_s 2.397
  min 2.290 max 7.224 median_json_bytes 1355`. Labelled "fixture lower bound, UNMEASURED on real data". Estimate (rows × 3 ×
  t_row): full 116550 rows / 899 groups / 232.8 core-h / 0.474 GB; tissues_frozen same; eqtl_only and tf+eo 105745 / 490 /
  211.2 / 0.430.
- **Deviation.** My first verify ran the r4_heavy determinism test on login01 for ~2.5 min (2 builds); killed. The file was
  intact (sha256 0f10d922…). All later heavy runs went on LSF.
- **Open-item evidence (packet §4).** stroke.AFR: local GCST90104553 md5 `c63fdaba…fee4` = published; meta.yaml trait "Small
  vessel stroke" (EFO_1001504), sample_size 20453. GCST90104549 = "Stroke" (EFO_0000712), 23991, md5 `15d6213c…` = published,
  sha256 `220d2610…` = inventory sha256_raw. stroke.AFR.tsv.bgz (sha256 bf08ef28…) vs GCST90104553: `raw_rows 5259724 r4_rows
  5259724 joined_ALT=effect_allele 5259724 joined_flipped 0 unjoined 0`; BETA/SE/P/EAF equal 5259724; N {20271} (LSF 429983).
  Inventory harmonized all-stroke file sha256 `3c58b250…` = inventory sha256_harmonized (LSF 429984). hypertension sdY: Evangelou
  2018 Supp. Table 1a SBP SD 20.7 mmHg (UKB+BiLEVE N 458,575), fetched to `data/r4/downloads/evangelou2018_supp/` (sha256
  a24bdb44…; row added to downloads_sha256.tsv; md5 computed, none published); sdY.est median 10.72 (trait_facts.tsv).
- **Wave close (LSF 429989, c018n02).** VERIFY test_qtl_manifest.py `14 passed` (7m54s, incl. r4_heavy). QUICK `343 passed, 51
  deselected`, 96.0 s. HEAVY `47 passed, 4 skipped` (21m22s; the 4 = W5a/W5b-enabled skips). Pins `39 passed`. FULL `1818
  passed, 50 skipped` (39m58s, full_W2c.xml). Vs full_W2b.xml: common 1854, removed 0, changed 0, added 14 (test_qtl_manifest,
  all passed); 1854 + 14 = 1868 ids, 1804 + 14 = 1818, 50 + 0 = 50; tests/m3 1299 (1265/34) unchanged. sparse_parent_benchmark.tsv
  restored. Shared conda cache 2188 / f094b37d… / 0 archives before and after, 0 entries newer. Frozen files 0-diff since
  1a887069. Commits `e3afa4dd` (T1), `f288ab82` (T2), packet + wave-close commit follows.
- **STOP at Task 4.** No sign-off recorded. Carter's 2026-10-27 "carter approved 10-27-2026 / proceed with your recommendations"
  predates the packet and does not match `carter-approved YYYY-MM-DD`; it is not a sign-off.
- **Pushed.** Wave-close commit `57da00e6`; `git push origin HEAD` → `14318720..57da00e6  HEAD -> m3-W2-aou-deltas`; fsck clean before/after.

## 2026-10-28 — W2c Task 4: Carter sign-off recorded

Two earlier replies were WAIT and recorded nothing: `carter-approved 10-28-2026` (signoff rc=1, wrong date format) and a reply with the `<...>` placeholders unfilled (not run). Carter's reply, verbatim:

```
carter-approved 2026-10-28
ukb_native: native
qtl_scope: full
trait.hypertension.EUR.sdY: 20.7
```

- `ta_r4.signoff record W2c-T4 --min-date 2026-10-28 --extra-required trait.hypertension.EUR.sdY` → rc 0, `signoffs/W2c-T4.yaml`, raw_sha256 `26e3c3020026af8616c5751f9fcacf11988aefeb4f932d693e973b7b8bfa2f3c`.
- `config/ta_r4/review_decisions.yaml` written from the recorded `fields` only; `trait_manifest.tsv` hypertension.EUR sdY = 20.7, sdY_source = `Carter 2026-10-28`; 0 UNRESOLVED cells remain.
- sdY 20.7 = Evangelou 2018 Supp. Table 1a UKB+BiLEVE SBP SD (packet §4); coloc `sdY.est` median 10.72 is the recorded caveat.
- stroke.AFR (§4b, GCST90104553 small vessel stroke): Carter raised no change; the packet had no reply key for it.

## 2026-10-28 — quick-261028-kkg: production gate = git lock (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf)

- **Commits.** `26b358e2` feat: `ta_r4.r4_lock_gate` + W4b-T3 schema `lock_sha: <40-hex>` (+ `check_lock_record` in
  test_signoffs, `write_fixture_lock`). `b119c34e` refactor: Snakefile/rules/`bin/r4_fire.sh` use the lock gate;
  `r4_osf_gate.py` and `test_osf_gate.py` deleted.
- **RED.** Before the module existed: `ImportError: cannot import name 'r4_lock_gate' from 'ta_r4'` (collection error);
  test_signoff `2 failed, 36 passed` (`posted: yes` still accepted; valid `lock_sha` reply rejected).
- **Negative control (unit).** Checks (g)/(h) blinded to `pass`: `-k drift` → `3 failed, 1 passed` (the 1 is the
  outside-LOCKED_PATHS edit, which must pass). Restored, `cmp` identical, `__pycache__` cleared → `4 passed`.
- **Negative control (end to end).** Fixture repo, after `write_fixture_lock`: production `r4_gate_probe` dry-run rc 0;
  an uncommitted edit to `src/python/ta_r4/arms.py` → refused, `LockGateError ... drifted`. In the toy e2e, the
  uncommitted manifest-row deletion is now refused by the lock gate first; re-locked, it reaches `LD_RECEIPT_REFUSED`.
- **Reconciliation by id (tests/ta_r4, quick + heavy, LSF 430489 before / 430615 after).** Before 390 passed + 4 skipped.
  Removed 55 = 52 test_osf_gate + 3 replaced (`test_other_enum_violations[W4b-T3 ... posted: no]`,
  `test_real_repo[check_osf_sentinel]`, `test_tracked_osf_sentinel_requires_w4b`). Added 51 = 45 test_lock_gate +
  4 test_signoff + 2 test_signoffs. 390 − 55 + 51 = 386 passed; 4 skipped (same 4 W5a/W5b reasons); 0 changed.
- **FULL** `1814 passed, 50 skipped` (0 failed; 37m27s) = 1864 ids. Vs full_W2c.xml (1868/1818/50): the same −55/+51,
  0 changed. Pins `39 passed`. sparse_parent_benchmark.tsv restored. run_susie_rss.R 0-diff.
- **Real repo.** `bash bin/r4_fire.sh production A3_1kg -n r4_gate_probe` → `LockGateError: (a) lock record absent:
  .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json`, rc 1.
  `bash bin/r4_fire.sh repro repro_routeC -n r4_gate_probe_repro` → dry-run lists the probe, rc 0.
- Records: DEC appended; osf_deviations R4 entry; PLAN-INDEX, CONTEXT (D-05/D-27 superseded lines), VALIDATION and the
  pending W3d/W3e/W4a/W4b/W5a/W5b/W5c/W6/W7 plans now gate on the lock; OSF posting is optional.

## 2026-10-28 — W2d executed (apply W2c-T4 decisions)

- Preconditions: `coloc_priors.yaml` locked: false; `decision_rules.yaml` / `simulation.yaml` not yet created; no R4-LOCK.json.
  `signoff verify W2c-T4` rc 0 → `{"qtl_scope": "full", "trait.hypertension.EUR.sdY": "20.7", "ukb_native": "native"}`.
- W2d: ukb_native=native (Carter 2026-10-28), no-op. ARMS['A3_ukb'].panel_dir = EUR_ukb337k_r4; arms.py and
  overlay_A3_ukb.yaml 0-diff vs HEAD; overlay/isolation/signoffs tests `62 passed`.
- W2d: qtl_scope=full (Carter 2026-10-28), no-op. qtl_manifest.tsv 0-diff vs HEAD; 116550 rows = qtl_compute_estimate
  `full` n_rows 116550; test_qtl_manifest.py `14 passed` (5m10s).
- Wave close (LSF 431166, c018n03, HEAD d222f160). QUICK `339 passed, 51 deselected` (107 s). HEAVY `47 passed, 4 skipped`
  (19m25s; same 4 W5a/W5b skips). Pins `39 passed`. FULL `1814 passed, 50 skipped` (36m26s, full_W2d.xml) = 1864 ids. Vs
  full_W2c.xml: common 1813, removed 55 / added 51 (the kkg osf→lock-gate swap), changed 0; tests/m3 1299 (1265/34) unchanged.
  sparse_parent_benchmark.tsv restored. Commits `99329eca` (T1), `d222f160` (T2), wave-close commit follows.

## 2026-10-29 — W3a executed (known-answer routes)

- **Route L code.** `bin/r4_extract_legacy_code.sh 3dd76df`: run_susie_rss.R sources no repo file (library() only), so
  1 file + the convenience copy; sha256 62fbe9da… (legacy_code_sha256.tsv, 2 rows). Blob 75f2d34 = git object, and the
  same blob at 0948a76, 1635d37 and 08beb4c: the alternates are byte-identical and were not run.
  `config/susie_policy.yaml` is 0-diff vs 3dd76df. Commit `49a8f47b`.
- **Fires** (`data/r4/results/<arm>/fine_mapping/susie`, /rs1). routeC 96, routeL 96, k2d_routeC 95, k2d_routeL 95 = 382;
  dry-run "Nothing to be done" for each. fits_repro_sha256.tsv 764 rows = 2 × 382. k2d omits bmi.EUR.APOE_19q13
  (absent from the k2d manifest input; TRACK-A-FROZEN-NUMBERS.md:26). Receipts: real-LD 86 legacy_panel + 10 missing
  (EUR HLA_6p21 + BMI_Xq24 × 5 traits) = 96; k2d 95 legacy_panel. 15 jobs died at LSF start with exit 255
  (C 7, L 4, k2dC 1, k2dL 3); a watchdog killed the waiting Snakemake, unlocked and re-fired. No R errors. Commit `741f44b5`.
- **Route C vs Route L** (known_answer_W3a.tsv, 191 rows = 96 + 95). Equal 96 + differ 0 = 96 (real-LD); equal 95 +
  differ 0 = 95 (k2d). max |ΔPIP| = 0 on 131 fits with a PIP vector (66 + 65); 60 early exits (30 + 30) have none.
  No code drift is detected under the reproduction semantics.
- **vs k2d record** (both routes identical). status 95 + 0 = 95; n_CS 95 + 0 = 95; cs_sizes 47 + 48 = 95.
  FINDING: the 48 cs_sizes differences are all the non-empty fits. The record's cs_sizes column equals
  `len("CS<i>")` for i = 1..n_CS on 95/95 rows (e.g. 10 sets → `3;…;3;4`): the summariser iterated CS keys. Aggregates
  65 ok / 24 too_many_variants / 6 no_variants and non-empty 48/95 equal the record.
- **vs frozen real-LD** (both routes identical). non-empty 51/96 = 51. Status 44 ok + 22 non_converged + 24
  too_many_variants + 6 no_variants = 96, vs frozen 48 + 18 + 24 + 6 = 96. FINDING: 4 more fits are non_converged
  (no per-fit frozen table survives, so which 4 is unknown). Per-fit spots: bmi.EUR.APOE_19q13 non_converged n_CS 6 =
  frozen (1/1). The 10 surviving 04-21 narrow-validation real-LD fits (FTO + SH2B3, EUR) match on status, n_CS and
  cs_sizes (10/10). They come from a pre-fire run, not the frozen fire.
- **Record tension (FINDING).** TRACK-A-FROZEN-NUMBERS.md:72 calls asthma "sole ok SH2B3 EUR fit". Both routes give
  t2d.EUR.SH2B3_12q24 ok (n_CS 9) as well, as does the 04-21 survivor, and :222 says asthma_vs_t2d was the only SH2B3
  EUR manifest row (the manifest admits only ok fits). Asthma ld_overlap_fraction 0.0385 is reproduced.
- Panel-absent EUR HLA_6p21 / BMI_Xq24 (10 fits): 9 exit early (4 too_many_variants HLA, 4 no_variants + t2d
  too_many_variants Xq24). bmi.EUR.HLA_6p21 is ok n_CS 10 with no panel. The frozen HLA fire used UKBB-LD tiles, so a
  per-fit difference there would come from the absent panel, not from code drift.
- Both routes ran in the same R env (r_coloc). Route C ≡ Route L therefore measures code drift only; environment drift
  since 04-22 is not tested. No policy or code was changed in response to any mismatch (§B.10).
- **Wave close** (LSF 432078, c017n03, HEAD 741f44b5). QUICK `346 passed, 52 deselected` (100 s). HEAVY `48 passed,
  4 skipped` (20m28s; same 4 W5a/W5b skips; the live known-answer test RAN). Pins `39 passed`. FULL 1872 ids / 1822
  passed / 50 skipped / 0 failed (38m31s, full_W3a.xml). Vs full_W2d.xml: common 1864, removed 0, added 8 (all
  test_known_answer_repro), changed 0; tests/m3 1299 unchanged. sparse_parent_benchmark.tsv restored.
  run_susie_rss.R 0-diff. A first close job (431883) stopped at QUICK: a `/rs1/researchers` literal in
  known_answer_compare.py (test_storage_on_rs1). Fixed with `R4_RSCRIPT` / PATH. Commit `26a6bb5f`.

## 2026-10-29 — W3b executed (SH2B3 R2-exact known answer, L10/iter-100, findings report); STOPPED at Task 3

Entry written 2026-11-02 from commit `0ef8b029`, `data/r4/logs/fire_w3b_sh2b3.log`, `data/r4/logs/lsf/`, `data/r4/logs/sh2b3_{r2,L10}/`
and the committed manifests. The W3b work itself ran 2026-10-29 02:20–02:43 EDT. `$W1` = `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md`,
`$W2` = `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md`.
- **(a) L15 fit code = `02c4404`.** `$W1:219` "21:51:00 — Rule 1 auto-fix applied to `src/legacy/region_analysis/scripts/run_susie_rss.R:38`;
  commit `02c4404`". The fits R2 used are the 2nd/3rd re-fire attempts after it (`$W1:223` "22:26:04 → 23:01:39 — third re-fire attempt …
  covered remaining 7 fits (1 L=15 stroke …)"). run_susie_rss.R blob ad2b3e3 at 02c4404, 299b52d and c0f02b6 (`git rev-parse`), i.e. unchanged
  through the R2 coloc; `git log 02c4404..c0f02b6 -- run_susie_rss.R config/susie_policy_L15.yaml` is empty.
- **(b) Policy = `config/susie_policy_L15.yaml` at 9c87157, max_iter_primary 500 / max_iter_retry 1000.** `$W1:216` "config/susie_policy_L{15,20,30}.yaml
  patched (max_iter_primary 100→500, max_iter_retry 200→1000); commit `9c87157`". `git show 02c4404:config/susie_policy_L15.yaml` lines 24–25
  `max_iter_primary: 500` / `max_iter_retry: 1000`; blob 09da798 at 9c87157, 02c4404 and HEAD.
- **(c) R2 coloc = `src/snakemake/scripts/run_coloc_susie.R` at `c0f02b6` (blob 4ed2599), la_multitrait_r Rscript.** `$W2:178` "- **Commit:** c0f02b6"
  (R.utils made optional, `$W2:172-177`); commit time 2026-04-29 23:43:43, and `$W2:63` "LSF dispatch TS=20260429_234353 (re-fire after R.utils
  Rule 1 auto-fix …)". Dispatcher `bin/fire_canonical_susie_pairs_W2_strategy3.sh` (`$W2:29`, `$W2:159`); its line 11
  `RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript`. la_multitrait_r `conda-meta/history` last entry 2026-04-24 17:31:08,
  so the env is unchanged since before R2. The R2 fits were swapped into the Stage-2 namespace (`$W2:155`).
- **Extraction** (`bin/r4_extract_legacy_code.sh`, now path-aware): legacy_code_sha256.tsv 2 + 5 = 7 rows (02c4404 script ×2 + policy; c0f02b6 ×2).
  arms.repro_sh2b3_r2 points at the extracted 02c4404 script and policy. commands.fit_command and ta_r4_finemap.smk unchanged. Commit `0ef8b029`.
- **Fire** (`data/r4/tmp/w3b_fire_chain.sh`, R4_R2_RSCRIPT = la_multitrait_r; serial queue). DAG 22 = 3 r4_run_finemap + 9 r4_sh2b3_r2_coloc +
  9 r4_sh2b3_L10_coloc + 1 r4_sh2b3_all (local). LSF submissions 21 + 1 re-fire = 22 (440330–440672); 440334 (L10 stroke_vs_t2d) died at LSF start ("Cannot open your job file",
  the W3a exit-255 pattern). At 20/22 the watchdog killed Snakemake, unlocked (`.snakemake/log/2026-10-29T023746…` "Unlocking working directory")
  and re-fired: 2 steps, 440672 completed. Dry-run "Nothing to be done" (re-checked 2026-11-02). L15 fits written 02:28:33 / 02:31:13 / 02:32:28.
- **Outputs**: 9 + 9 coloc JSONs; fits_repro_sh2b3_sha256.tsv 3 JSON + 3 fit.rds + 18 coloc = 24 rows (`sha256sum -c` OK 2026-11-02).
  L15 `.fit.rds` md5 903782e2 / 3dc6fe83 / 4c539b5a = the R2 post-swap md5s in `wave2_dispatch_tracker.json:28-30`.
- **R2_exact vs frozen R2** (known_answer_sh2b3.tsv, 18 rows = 9 R2_exact + 9 L10_iter100): match 9 + differ 0 = 9; `cmp` byte-identical 9/9.
  Fingerprint bmi_vs_hypertension n_cs 13 × 5, nsnps 168, hit1/hit2 rs3184504: 5/5. L15 n_CS 13/5/3, ld_overlap 170/589/622, all non_converged
  niter 1000 L_used 15, policy_hash 456efb68….
- **L10/iter-100** (separate measurement): bmi–htn 1.0 and htn–stroke 1.0 hold; htn–t2d 3.0943e-08 (R2 1.0).
- **New findings** (FINDINGS §4/§5/§8): JSON credible_sets vs `.fit.rds` `$sets$cs` eq 37 + differ 29 + no_sets 30 = 96, non-empty 51 vs 25;
  R1 28 pairs ≥ 1 side zero 14 (JSON) / 22 (rds), 6 FTO EUR pairs non-empty both sides; TRACK-A-FROZEN-NUMBERS.md:357/:361 cite a later commit
  and later fits; the R2 coloc skipped the chr:pos rewrite (18/18 logs, R.utils absent). No number adjusted (§B.10).
- Negative controls (2026-11-02, module restored by sha256): TOL 1e-6→1e-30 → `test_tolerance_1e6[5e-07-true]` FAILED; dropping the
  fingerprint_check from match → `test_bmi_htn_fingerprint_is_absolute_not_relative` FAILED. The original RED run is not on record.
- FINDINGS edits 2026-11-02: source paths added to §6 (effective max_iter 100, `$W1:218`, Route C niter) and to each §7 line. No number changed.
- **Wave close** (LSF 481675, c017n04, HEAD 0ef8b029, 2026-11-02). QUICK `360 passed, 54 deselected` (87.7 s). HEAVY `50 passed, 4 skipped`
  (21m44s; same 4 W5a/W5b skips; both W3b live tests ran). Pins `39 passed`. FULL 1888 ids / 1838 passed / 50 skipped / 0 failed (40m02s,
  full_W3b.xml). Vs full_W3a.xml: common 1872, removed 0, added 16 (all test_sh2b3_known_answer), changed 0; 1872 − 0 + 16 = 1888;
  tests/m3 1299 (1265/34) unchanged. sparse_parent_benchmark.tsv restored; run_susie_rss.R 0-diff. An earlier close (440842, 2026-10-29)
  gave the same ids/outcomes (full_W3b.440842.xml). Commit `57ed36a8`.
- **Task 3 (W3b-T3, Carter human-action) NOT started.** No sign-off recorded.

## 2026-11-02 — W3b-T3 signed off (Carter)

Reply, verbatim:

```
carter-approved 2026-11-02
instructions: proceed. 1. ive read it, 2. lets fix these mismatches, what are the causes? 3. confirm unless there is a reason to use a different one. 4. findings dont change the pre-reg
```

`signoffs/W3b-T3.yaml` raw_sha256 e8800b8e…; `signoff verify W3b-T3` exit 0. D-17 SH2B3 provenance statement confirmed.
Pre-registration (W4a) unchanged by the findings. Follow-up: cause analysis of the W3 mismatches (no number adjusted, §B.10).

## 2026-11-02 — quick-261102-log Task 1: W3 errata + FINDINGS causes

- TRACK-A-FROZEN-NUMBERS.md: `## ERRATA (2026-11-02)` appended, E1–E7 (additions only; `git diff` 14 added / 0 deleted lines).
- FINDINGS §4 (4 fits named: asthma/bmi/hypertension/t2d.EUR.FTO_16q12, identity-placeholder FTO LD in the 04-22 fire;
  env-drift caveat no longer needed), §7 items 3/4/9 updated, items 10 (JSON `credible_sets` unfiltered; fix pending Carter's
  D-28 decision, Task 2) and 11 (latent chr:pos alignment defect, open) added, §8 measured cause (R1 read V4 fits).
- Counts re-measured from `$MAN/fit_cs_json_vs_rds.tsv`: eq 37 (22 non_converged + 15 ok) + differ 29 (ok) + no sets 30 = 96;
  non-empty JSON 51, rds 25, JSON-only 26; 51 − 26 = 25. Status: 44 + 4 = 48 ok, 22 − 4 = 18 non_converged (debug file).
- cs_sizes writer check (E1): `grep -rn IDENTITY-LD-K2D-FIT-SUMMARY bin src` = readers only (fig2/fig3, ta_r4, repro bundle);
  no writer in code. The TSV was written in ec86832e (quick-260425-ieh), whose PLAN :161 says "len(cs) for each cs in
  JSON.credible_sets". Current `summarize_finemap_results.py` `summarize_file` on
  `repro_k2d_routeC/.../stroke.EUR.SH2B3_12q24.json` gives `CS1:1;…;CS8:1;CS9:19;CS10:38` = `len(v)` per set; the record
  row is `3;3;3;3;3;3;3;3;3;4` = `len(key)`. Verdict: not present in current code; no Task 3 sub-step needed.
- No code, fit or frozen number changed (§B.10). `run_susie_rss.R` untouched.

## 2026-11-03 — W3c simulation harness (code + config + tests; no production run)

- Precondition: `signoff verify W3b-T3` exit 0. Carter's instructions: none concern the simulation design; item 4 ("findings dont
  change the pre-reg") applied — design values as in the plan.
- **Harness commit `0efac930`** (cite in the W4a amendment): simulate_coloc_r4.R, simulation.yaml (locked: false), ta_r4_sim.smk,
  run_coloc_pair_r4.R main-guard refactor (coloc_pair_core), tests/ta_r4/test_simulation_harness.py (21 tests: 11 quick, 10 r4_heavy).
- Harness SuSiE = run_susie_rss.R's `%||%`, `regularize_ld`, `run_susie_with_ladder`, parsed from the frozen file at load time (not copied).
  run_susie_rss.R 0-diff vs 53106f8.
- RED: 4 failed + 17 errors (harness file absent, simulation.yaml absent, no rule). GREEN 21 passed.
- SuSiE identity vs the frozen script via commands.fit_command (fixture, 60 variants): max|dPIP| 0.0 A2_identity (5 CS = 5) and A3_1kg (1 = 1).
  Coloc identity vs the run_coloc_pair_r4.R CLI on the harness's fits (A1_matched, A2 susie, A3 susie): max|dPP| 0.0.
- W0d CLI before/after the refactor (4 fixture regions x 2 p12 keys x 3 modes = 24; 20 JSON + 4 UNMAPPED_FIT_NAMES refusals):
  parsed-dict diff empty; snapshot files byte-identical.
- Negative controls (8, `-B -p no:cacheprovider`, each restored sha256-identical): frozen call + estimate_residual_variance=TRUE,
  L-5, harness p12_sensitivity, no PSD clip, seed +1, H3 bin ignored, rule without gate, rule passing --reps-override → each RED.
- Config key `n_per_trait` (not `n`): R yaml parsed `n:` as FALSE → harness n = numeric(0) → every susie_rss errored. Harness now refuses
  non-positive/missing numeric config keys.
- Gate: `bash bin/r4_fire.sh production A3_1kg -n data/r4/results/sim/SH2B3_12q24.H4.gen_1kg.tsv` rc 1,
  `LockGateError: (a) lock record absent`. Fixture-repo dry runs: no lock → refused; with fixture lock → 100 r4_sim jobs, no --reps-override.
- Smoke (pre-gate; not an estimate): SH2B3_12q24 gen_1kg H4 and H3_r2_0.6, `--reps-override 2`, data/r4/tmp/sim_smoke/ (window 745,
  6 rows each; H3_r2_0.6 qualifying pairs 4782; seed rep 1 H4 = 20278622 = 20261021 + 17601).
- **Scheduler: Slurm from 2026-11-03 (Carter); LSF no longer used.**
- **Wave close** (Slurm 1672481, c207n03, HEAD 0efac930, 1h05m). QUICK `371 passed, 67 deselected` (97 s). HEAVY `63 passed, 4 skipped`
  (21m44s; same 4 W5a/W5b skips). Pins `39 passed`. FULL 1912 ids / 1862 passed / 50 skipped / 0 failed (41m56s, data/r4/tmp/w3c/full_W3c.xml).
  Vs full_261103.xml by id: common 1891, removed 0, added 21 (all test_simulation_harness, all passed), changed 0; 1891 − 0 + 21 = 1912;
  skips 50 = 50 same ids; tests/m3 1299 (1265/34) unchanged. sparse_parent_benchmark.tsv clean.

## 2026-11-03 — W3d estimators, branch classifier, coverage, aggregation (code + config + tests; no production data)

- **Analysis-code commits (cite in the W4a amendment, with W0d/W3c/W3e):** `db2bf8c9` (estimands.py, branch_classifier.py,
  cs_cross_purity.R, decision_rules.yaml draft locked: false), `83b3240d` (coloc_coverage.py), `bd551895` (run_aggregation.py),
  `aef3be84` (Rscript from PATH, not an /rs1 literal).
- Real manifest: confirmatory rows 100 over 10 region_safe clusters. Coverage expected EUR 290 × 2 × 7 = 4060 and AFR 30 × 2 × 5 = 300;
  real-repo CLI `missing=4060` / `missing=300`, rc 1 (no outputs yet).
- Truth table: 36 combos; via rule1 18 / rule2 6 / rule3 4 / partial_rule 8. Branches excluding partial_rule: NON_INFORMATIVE 18,
  NO_SYSTEMATIC_DIFFERENCE 3, HETEROGENEOUS 3, INFLATION_SUPPORTED 2, DEFLATION 2.
  - The 8 partial rows are (pos, ns), (pos, sig_A3_gt_X), (neg, ns) and (neg, sig_X_gt_A3), each × kappa_ok. They are governed by 4
    keys, all drafted HETEROGENEOUS.
  - These keys, plus kappa_cut, n_both_min and the confirmatory block, are Carter's decisions in W4a-T3.
- REDs: T1 49 failed + 33 errors; T2 6 failed; T3 6 failed + 4 errors.
- Negative controls (each RED, restored sha256-identical):
  - T1 (4): partial key deleted, precedence swapped, row bootstrap, NC rows in the filter.
  - T2 (2): `check()` drops missing; CLI with one file removed exits 1.
  - T3 (4): gate removed, coloc globbed from every results dir, `import math`, NC leak into the confirmatory filter.
- Cluster bootstrap vectorized (bit-identical to the per-draw loop on the same picks) to hold QUICK under 120 s.
- **Wave close run 1** (Slurm 1674027, HEAD bd551895): FULL 1 failed, `test_storage_on_rs1::test_no_rs1_or_share_literals_in_r4_config_and_src`
  (an /rs1 Rscript literal in run_aggregation.py). The code was fixed in aef3be84; the test is unchanged.
- **Wave close run 2** (Slurm 1674938, c207n09, HEAD aef3be84, 59m36s):
  - QUICK `470 passed, 67 deselected` (118 s).
  - HEAVY `63 passed, 4 skipped` (same 4 W5a/W5b skips).
  - Pins `39 passed`.
  - FULL 2011 ids / 1961 passed / 50 skipped / 0 failed (`data/r4/tmp/w3d/full_W3d.xml`).
- **By id vs full_W3c.xml:**
  - Removed 0, added 99 (all passed: contrast_stats 33, branch_classifier 24, estimands 22, run_aggregation 10, coloc_coverage 6,
    cs_cross_purity 4), changed 0; 1912 − 0 + 99 = 2011.
  - Skips: the same 50 ids. tests/m3: 1299 (1265/34), unchanged.
  - fsck: dangling only. sparse_parent_benchmark.tsv clean.

## 2026-11-04 — W3e QTL harmonization (pre-gate) + group runner (code + config + tests; no QTL coloc on real data)

- **Analysis-code commits (cite in the W4a amendment, with W0d/W3c/W3d):** `4d27ac00` (harmonize_qtl_r4.py, r4_qtl_harmonize,
  qtl_harmonized_sha256.tsv), `0ca16af9` (run_qtl_group_r4.py, run_coloc_pair_r4.R --mode qtl_abf, r4_qtl_group /
  r4_qtl_aggregate / r4_qtl_tiers / r4_qtl_all). **`0ca16af9` is the last analysis-code commit of W3.**
- **Harmonization fire** (D-05, pre-gate): `bin/r4_fire.sh repro repro_routeC` inside Slurm 1675878 with a local profile and a
  refusing `bsub` shim (no LSF; `Provided cores: 8`). Result: 899 groups, `900 of 900 steps (100%) done`, 13.5 min, then
  `Nothing to be done`.
  - Files: 23,310 = distinct (source, qtd, molecular_trait_id, region) manifest features 23,310 (eqtl 21,149 + sqtl 2,161).
  - 0 empty; 0 rehash mismatches; 91,853,028 harmonized rows.
  - `$MAN/qtl_harmonized_sha256.tsv` has 23,310 rows.
- **Deviation: sQTL per junction.** The shipped `harmonize_sqtl()` filters on gene_id, so gene-level files mix the junctions of
  376 genes (882 junctions). The plan's gene_id count, 22,804, is lower by 882 − 376 = 506. The wrapper cuts the window per
  molecular_trait_id and runs the shipped function. eQTL output equals the shipped CLI; sQTL junction files partition the shipped
  gene-level rows. **Finding for W4a:** the frozen layer's sQTL rows for multi-junction genes were mixed.
- **Runner:** QTL_A3 (A3_1kg, EUR_1kg_r4, join + orient), QTL_A2 (A2_identity, EUR_identity_r4, same flags) and QTL_legacy
  (repro_routeL, legacy_repro, `--ld-allele-join false`, no `--variant-list`, no `--qtl-orient`).
  - No-CS rows get fallback_abf via `run_coloc_pair_r4.R --mode qtl_abf`, on the bridged set run_qtl_coloc.R uses (equality
    tested by tracing `coloc::check_dataset`).
  - Fixture group: 1 coloc_susie and 3 fallback_abf (qtl_n_cs==0 / gwas_n_cs==0 / both) in both arms.
  - Coverage exits 1 naming any missing or extra row.
- **Dry runs (HEAD 0ca16af9):**
  - `production A3_1kg -n <QTL_A3 group>`: rc 1, `LockGateError: (a) lock record absent`.
  - `repro repro_routeL -n <QTL_legacy group>`: 1 r4_qtl_group job.
  - `repro repro_routeL -n r4_qtl_all`: 1002 jobs (899 groups + 100 routeL trait-pair coloc + aggregate + tiers + all).
- **REDs:** T1 ImportError (collection); T2 `15 failed, 15 passed` (R mode and rules absent).
- **Negative controls** (each RED, restored sha256-identical):
  - T1 (2): no junction cut, reader not restored.
  - T2 (8): fallback mislabelled, legacy `--qtl-orient`, coverage drops missing, bridge keeps orientation drops, bridge keys on
    chrpos, abf on p12_sensitivity, QTL gate removed, every R failure becomes a row.
- **W0d** CLI snapshot before/after the run_coloc_pair_r4.R refactor: 24 outputs, byte-identical.
- **Wave close** (Slurm 1677128, c024n04, HEAD 0ca16af9, 56m45s):
  - QUICK `491 passed, 83 deselected` (108 s). Vs W3d: +21 quick (harmonize 7, runner 14), +16 heavy (runner 9, qtl_abf 7).
  - HEAVY `79 passed, 4 skipped` (63 + 16; the same 4 W5a/W5b skips).
  - Pins `39 passed`.
  - FULL 2048 ids / 1998 passed / 50 skipped / 0 failed (`data/r4/tmp/w3e/full_W3e.xml`).
- **By id vs full_W3d.xml:**
  - Removed 0, added 37 (all passed: test_qtl_group_runner 23, test_coloc_pair_r4 7, test_qtl_harmonize_r4 7), changed 0;
    2011 − 0 + 37 = 2048.
  - No passed→skipped. tests/m3 1299 (1265/34), unchanged.
  - fsck: dangling only, before and after each commit. sparse_parent_benchmark.tsv clean.
- **For W4a (Carter):** sQTL unit = junction (frozen-layer finding); tiers count coloc_susie rows only (fallback_abf reported, not
  tiered); QTL_legacy tier input = routeL trait-pair coloc via run_coloc_pair_r4.R; below-floor rows kept as method none;
  run_qtl_coloc.R uses the coloc.susie package priors (= yaml now; a p12 change needs a priors flag before the lock).
- **For W6:** bin/r4_fire.sh still carries the LSF profile. Fire under Slurm with a second `--profile` (local) and a bsub shim,
  or add a Slurm profile. 899 group jobs per QTL arm; per-row cost on real windows is unmeasured.

## 2026-11-04 — W4a Task 1 (extractor + text tests, R4 amendment DRAFT, deviations entry)

- **p12 citation (verified).** Wallace 2020, "Eliciting priors and relaxing the single causal variant assumption in
  colocalisation analyses", PLoS Genet 16:e1008720. Source: JATS XML from
  `https://journals.plos.org/plosgenetics/article/file?id=10.1371/journal.pgen.1008720&type=manuscript` (sha256
  b6af1f883af8eaf2eefd85247a3683e8b54daa8fdc2d68e06b822ab49b8c4347; scratch only). Exact sentences:
  - Results: "The results suggest that the coloc default of p12= = 10−5 may be overly liberal, with data simulated under H3
    having posterior support for H4, particularly for smaller samples, and that p12 = 5 × 10−6 may be a more generally robust choice."
  - Discussion: "Perhaps the most widely applicable are the results of simulations, that suggest values of the order
    p12 ≈ 5×10−6 lead to robust inference over a range of scenarios, but the adoption of sensitivity analysis will help
    evalutate robustness of inference to changes in prior parameter values."
  - ⚠ Closing summary (conflicts): "The simulations here (Fig (4)) suggest that p12 = 5×10−5 provides a reasonable balance
    between power and false positive calls, but it is unlikely that any single point distribution on p12 captures all prior knowledge."
  Two sentences support 5e-6; the summary prints 5e-5 (probable typo, not verified). 5e-6 kept as the PROPOSED value; the
  conflict is stated in the DRAFT §(f) and goes to Carter at W4a-T3.
- **Plan vs code (measured before writing).** The W0d "Decision needed" (fit-name alignment) is still open in code:
  `run_coloc_pair_r4.R --mode susie` on repro_routeC SH2B3_12q24 hypertension × stroke →
  `Error: UNMAPPED_FIT_NAMES: fit_a: 589 of 589 fit variant names (e.g. rs7961935) are neither a sumstats SNP_ID nor
  CHR:POS in SH2B3_12q24 (LD-panel rsid override?)`, rc 1. Fit names (repro_routeC SH2B3 EUR): hypertension 589/589 rsid,
  stroke 622/622, t2d 863/863, asthma 147/147, bmi 170/170. hypertension/stroke/t2d sumstats are chr:pos (W2a). So
  production coloc refuses most EUR pairs as coded. Carried to W4a-T3 as an open decision; the DRAFT §(d) has a
  ‹CARTER-LOCK› placeholder for the rule. Nothing changed in code.
- **Plan vs record.** (h)'s R1 line follows FINDINGS §(8) (measured: non-empty PP.H4 0/28; 22/28 zero purity-filtered
  sets on ≥1 side; 3 FTO pairs reached coloc.susie), not the plan's shorter "no_signal, n_cs 0" wording. (m) names the
  phase-dir panel manifests as `manifests/panels_*.tsv` (the internal-content scan bans `.planning/`); the text test maps
  that LOCKED_PATHS entry the same way. The A3-UKB panel is Weissbrod 2020 UKB 337k (data_sources.yaml), not Pan-UKBB.
- **RED** (`data/r4/tmp/w4a/red_t1.txt`): `ImportError: cannot import name 'extract_paste_block'` (collection error).
  **GREEN:** `19 passed, 2 skipped` (FINAL/PUBLIC absent, reason printed).
- **Negative controls** (`data/r4/tmp/w4a/nc_t1_out.txt`; files restored sha256-identical):
  NC1 "pivot" in DRAFT extract → `test_draft_extract_framing` failed; NC2 ".planning/x" → `test_draft_extract_internal_content`
  failed; NC3 decision_rules.yaml clusters → `row_id of ...` → 2 failed (confirmatory NC + rendered-block test). In-file NCs
  (tmp extracts with "Pivot", ".planning/x", checklist/CARTER-LOCK, end-before-start) pass as tests.
- **DRAFT** extract 2,514 words (≤ ~2,700). Confirmatory sentences pasted from `render_confirmatory(rules)` unchanged.
- **osf_deviations.md** "R4 amendment — DRAFTED, NOT POSTED" appended; `git diff | grep -c '^-[^-]'` = 0.

## 2026-11-04 — W4a Task 2 (brief-blind Codex review of the extract; dispositions; DRAFT fixes)

- Review input: `extract_paste_block --in DRAFT@a4090fa6 --out data/r4/tmp/w4a_review_input.md` (sha256 95a5f928…). Prompt =
  the plan's instruction + that extract only (sha256 34620f5c…). No CONTEXT/RESEARCH/LOG/summary was given.
- Attempt 1 (codex-cli 0.141.0, config model gpt-5.5): rc 1, empty output, "model is not supported when using Codex with a
  ChatGPT account". Probed gpt-5/5.1/5.2/5.3/5.4 codex names: all rejected. `~/.codex/models_cache.json` lists gpt-6.x.
  codex-cli 0.166.0 installed into a scratch prefix (shared gsd-tools env untouched). Attempt 2: `-m gpt-6.1-sol`, rc 0,
  40,055 B (sha256 697bfd1f…). Banked verbatim (embedded-bytes check True) in `ta-r4-W4-AMENDMENT-REVIEW-as-received.md`.
- Findings 31 (18 numbered + 13 table qualifications) = 31 disposition rows. Verified myself: cap order run_susie_rss.R:946
  before :1042; R4 catalog PYHIN1_1q23 98,393 rows; asthma×PYHIN1 catalog-joined 38,313 (> 16,000) → `too_many_variants` →
  run_coloc_pair_r4.R FIT_EARLY_EXIT; LOCKED_PATHS lacks config/susie_policy.yaml (read by arms.py:6) and config/pipeline.yaml
  (bin/r4_fire.sh:71); kriging rule :1297; ladder 3 steps; susieR 0.14.2 estimate_residual_variance default FALSE (measured);
  UKB n_samples NA; BMI_5q13_3 isect zero-filled 8,635,830; aggregate_qtl_coloc reads `summary` only; sim identity refit :61-64.
- DRAFT: 26 text replacements so the text describes the code (one script, each match asserted unique); new ‹CARTER-LOCK›
  early-exit rule in (d); Pre-Paste OPEN row. `test_amendment_text.py` 19 passed / 2 skipped after. Extract 2,799 words
  (over the ~2,700 guide by ~100; accuracy additions, not trimmed).
- No analysis code changed. Carter decisions before the lock: N1, N2, N3, N4, N5, N6, N7, N8, N12, N14, T1 (+ optional N9, N10).
- **§C wave close (W4a-draft; Slurm 1680976, c205n03, HEAD a4090fa6 + uncommitted DRAFT/review edits, 1h35m):**
  QUICK 510 passed / 2 skipped / 83 deselected in 150.5 s (> 120 s); HEAVY 79 passed / 4 skipped (same 4 W5a/W5b skips);
  PINS 39 passed; FULL 2069 ids = 2017 passed + 52 skipped + 0 failed (`data/r4/tmp/w4a/full_W4a.xml`).
  By id vs full_W3e.xml: common 2048, removed 0, added 21 (all test_amendment_text: 19 passed + 2 skipped), changed 0;
  2048 − 0 + 21 = 2069. tests/m3 1299 (1265 / 34) unchanged. sparse_parent_benchmark.tsv clean.
- **QUICK budget:** `--durations` on the login node: `test_import_isolation.py::test_m3_conftest_import_still_works` 68.67 s
  (next slowest 5.72 s). Marked `r4_heavy` (marker only; still runs in HEAVY and FULL; passes, 24 s). QUICK re-timed:
  509 passed, 2 skipped, 84 deselected in 91.9 s.

## 2026-11-04/05 — W3f 15.1 (N1 cap after LD restriction; N2 fit-name alignment; N8 method none)

- DECs: DEC-2026-11-04-ta-r4-w3f-fix-all, DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor,
  DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze.
- Commits: e38a519c, 4a1b9d4a (decisions); 6c6e9546 + 1f771281 (N1, two code commits) with re-pins 3e895261, e5792b8b;
  7a3415df (N2 + N8); 215ddde3 (differential-substrate argv fix).
- RED/GREEN/NC under `data/r4/tmp/w3f/`: t2_red 5F/1P → t2_green 6P; t2_nc1, t2_nc2 1F each; t3_red 30F + 2E;
  t3_nc1 3F, t3_nc2 1F, t3_nc3 1F.
- SH2B3_12q24 hypertension × stroke: 589 = 0 direct + 589 panel_exact + 0 swapped + 0 strand; 622 = 0 + 622 + 0 + 0; n_snps 583, rc 0.
- Close (Slurm 1716306): plan verify 104P/1S; QUICK 531P/2S in 185.9 s (over the 120 s budget); HEAVY 1F/95P/4S →
  test_fit_rds_unchanged_by_the_fix (pre-fix 656529a rejects the N1 flag) → 215ddde3 → 3P (Slurm 1717387); PINS 39P.

## 2026-11-09 — W3f 15.2 (N3 locked paths; N4 in-job input sha256; N5 in-job gate; T1 label)

- Commits: 82490835 (N3), 6312db61 (N4), d61fb081 (N5 + r4_fire.sh + T1). Pushed to origin/m3-W2-aou-deltas.
- **N3 dependency measurement** (grep of quoted repo paths across Snakefile.ta_r4, ta_r4_*.smk, ta_r4/*.py, bin/r4_fire.sh;
  `source(`/`file.path(` in the R scripts; repo-local imports of the ta_r4 modules and shared helpers). Live non-data reads not
  previously locked: config/susie_policy.yaml (arms.py:6), config/pipeline.yaml (Snakefile.ta_r4:14, r4_fire.sh --configfile),
  src/snakemake/scripts/qtl_orient.R (run_qtl_coloc.R:184-188, run_coloc_pair_r4.R:346), config/qtl_sources.yaml
  (harmonize_qtl_r4.py:29), src/python/build_tissue_n_lookup.py (harmonize_qtl_r4.py:22), config/pph4_thresholds.yaml
  (ta_r4_qtl.smk:141); plus, found by the measurement: manifests/{sumstats_r4,catalogs,qtl_harmonized}_sha256.tsv (read by
  the N4 in-job check) and manifests/known_answer_{W3a,sh2b3}.tsv (run_aggregation.py:27-28). 6 + 5 = 11 entries appended.
  Not added (builder inputs whose outputs are locked or hash-checked): config/negative_controls.yaml (build_pair_manifest →
  pair_manifest.tsv, locked), config/regions_curated_grch38.csv + review_decisions (build_qtl_manifest → qtl_manifest.tsv,
  locked), config/eqtl_catalogue_qtd_map.yaml + manifests/qtl_downloads_sha256.tsv (pre-gate downloads/harmonize → harmonized
  files, sha-checked in-job), collect_region_variants.py / build_ld_rds.py / ukb337k_tiles (catalogs sha-checked in-job;
  panels md5-checked by write_ld_receipt). Enforcer: test_lock_gate.py::test_every_measured_dependency_is_covered_by_locked_paths
  (41-entry R4_DEPENDENCIES).
- **N4 input listing** (production arms, admissible pair_manifest rows + QTL manifest rows): sumstats 8 listed / 8,
  catalogs 29 / 29, harmonized QTL 23,310 / 23,310 (116,550 qtl_manifest rows). Repro arms: sumstats 8/8 but catalogs 10/29 —
  unlisted = 19 data/r4/ld/variants_legacy/NC_*.tsv → verification applied to production arms only (repro renders `true`);
  QTL_legacy inputs are all listed, so run_qtl_group_r4 verifies every QTL arm. Cost: stroke.EUR 137 MB verifies in 0.8 s.
- RED/GREEN/NC under data/r4/tmp/w3f2/: t1_red 13F → t1_green 77P/2S; t1_nc (susie_policy removed) 3F.
  t2_red collection error, t2_red2 11F/10P → 21P; t2_nc1 (skip unlisted) 2F; t2_nc2 (no verify in run_group) 4F.
  t3_red 16F/3P; fire RED with old DIRTY list (susie_policy dirty → rc 0, SMK called); globbing-on RED (deleted ta_r4_b.smk
  missed) → set -f → 5P; t3_green 19P (gate rc 0 before drift, 1 after); t3_nc1 (gate only in finemap) 6F/1P; t3_nc2 2F.
- Task 2 verify Slurm 1782976: 64 passed. Close Slurm 1783263 (c203n05, tree = d61fb081 less the aggregation fixture fix):
  plan verify T3 104P; HEAVY 115P / 4S (the W5a/W5b skips) in 29m15s; PINS 39P; QUICK 566P / 1F / 2S —
  test_run_aggregation::test_final_label_with_fixture_lock_and_signoff: its fixture left the now-locked known-answer tables
  untracked → gate (h) → status DRAFT. Fixture now commits them (assertions unchanged). QUICK rerun Slurm 1783856: 567P / 2S
  in 137.7 s (566 + 1 = 567; over the 120 s budget, carried to 15.6). FULL not run (plan §C list: QUICK, HEAVY, PINS).

## 2026-11-09 — W3f 15.3 (N7 region sign-flip test + n_regions_min 7; N6 completeness + coverage-gated FINAL)

- Commits: 92caa306 (N7), 0ac1a15e (N6), a36d4ad1 (DRAFT (e) render). Pushed 0ad0b742..a36d4ad1.
- confirmatory_sha256: old f6e6e90f83fd14975d3afa04789c3dcf1a9211b8e3ddd38bf23c72f8cbe0e9e3 (from
  `git show 0ad0b742:config/ta_r4/decision_rules.yaml`) -> interim 9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5.
  Command (cwd src/python): `$PY -c "import yaml; from ta_r4.signoff import canonical_sha256;
  print(canonical_sha256(yaml.safe_load(open('../../config/ta_r4/decision_rules.yaml'))['confirmatory']))"`. Final value: 15.5.
- Counterexample A (10 rows of one region of 100) on 0ad0b742: ('INFLATION_SUPPORTED', 'rule3_agree'), n_both 10, CI
  [0.2, 0.2], McNemar p 0.001953125. After N7 alone it is NON_INFORMATIVE, but a cherry-picked set (one row per region over 10
  regions) is still INFLATION_SUPPORTED (signflip p 0.001953125). After N6 both raise ConfirmatoryIncomplete. Counterexample B
  (10-row manifest): ('NON_INFORMATIVE', 'rule1_n_both'), n_regions 1.
- RED/GREEN/NC under data/r4/tmp/w3f3/: t1_red 31F/80P -> t1_green 111P; t1_nc1 (row McNemar) 9F, t1_nc2 (no region term) 5F,
  t1_nc3 (> for >=) 17F. t2_red 27F/34P -> t2_green 91P; t2_nc1 (ids from rows) 2F, t2_nc2 (no coverage) 3F. t3_red 5F/16P/2S
  -> t3_green 62P/2S; t3_nc (renderer hard-codes 7) 1F (path0-6 only).
- Truth table: 18 NON_INFORMATIVE / 3 NO_SYSTEMATIC_DIFFERENCE / 11 HETEROGENEOUS (3 + 8) / 2 INFLATION_SUPPORTED / 2 DEFLATION = 36.
- Close Slurm 1784345: plan verify 111P / 61P / 62P+2S; QUICK 612P/2S in 189.2 s (567 + 45 new = 612; over 120 s, for 15.6);
  HEAVY 115P/4S in 32m00s; PINS 39P. FULL not run.
