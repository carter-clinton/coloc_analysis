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
