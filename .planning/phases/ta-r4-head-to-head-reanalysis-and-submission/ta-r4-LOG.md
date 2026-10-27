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
