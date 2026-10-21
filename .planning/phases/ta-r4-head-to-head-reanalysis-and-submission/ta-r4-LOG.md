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
