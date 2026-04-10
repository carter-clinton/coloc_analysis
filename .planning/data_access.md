# data_access.md

Track 0a DUA application tracker. This is the **single longest critical
path** in the project (`GSD_BRIEFING.md` §5.2 gap #1 → `REQUIREMENTS.md`
REQ-1). Applications run in parallel with Phase 0 infrastructure work
from Day 1.

## Status legend

- `not-started` — no action taken yet
- `drafting` — application form being prepared
- `submitted` — sent to the data provider, waiting on decision
- `approved` — access granted, credentials/download steps in progress
- `credentialed` — data is reachable from the pipeline
- `blocked` — external issue (missing document, rejection, indefinite delay)
- `not-needed` — determined not required after scope review

## Applications

| Data source | Why we need it | Phases it gates | Status | Date submitted | Tracking ID | Expected lead time | Contact | Notes |
|---|---|---|---|---|---|---|---|---|
| UK Biobank (main) | EUR GWAS replication / polygenic scoring | 8, 9 | not-started | — | — | 4-8 weeks | ukb-access@ukbiobank.ac.uk | |
| UKB-PPP (Olink pQTL) | Phase 2 3-way QTL coloc — pQTL spine | 2 | not-started | — | — | 6-12 weeks | ukb-ppp-access@ukbiobank.ac.uk | Requires UKB main access first |
| deCODE pQTL (Ferkingstad 2021) | Phase 2 3-way QTL coloc — pQTL replication | 2 | not-started | — | — | varies (emailed request) | decode@decode.is | Summary statistics available via sumstats portal — check if DUA needed at all |
| FinnGen (latest release) | Replication cohort | 9 | not-started | — | — | 2-6 weeks | finngen-access@finngen.fi | Open-access portal for most phenotypes |
| MVP (Million Veteran Program) | AFR replication cohort | 9 | not-started | — | — | 8-16 weeks (VA approval) | mvp-access@va.gov | Longest lead time — **apply first** |
| All of Us Researcher Workbench | Hispanic + AFR replication | 8, 9 | not-started | — | — | 4-6 weeks (Tier 2) | aou-researcher@researchallofus.org | Requires institutional verification |
| BBJ (BioBank Japan) | EAS replication cohort | 3, 4, 9 | not-started | — | — | 4-8 weeks | bbj-access@ims.u-tokyo.ac.jp | |
| Pan-UKBB | Trans-ancestry MR instruments | 3 | not-started | — | — | Public portal, no DUA? | — | Check: may be open-access |

## Actions checklist (Phase 0 Day 1)

- [ ] Confirm institutional eligibility for each provider (NCSU IRB /
      institutional letters of support)
- [ ] Draft a one-page project description usable across multiple
      applications
- [ ] Identify which datasets already have **open-access summary statistics**
      and do not require a full DUA (likely: Pan-UKBB, FinnGen for most
      phenotypes, deCODE pQTL sumstats portal)
- [ ] File **MVP application first** (longest lead time)
- [ ] File **UKB main + UKB-PPP together** (UKB-PPP requires UKB main)
- [ ] Open All of Us account + complete Tier 2 training

## Gates (do not run without these)

| Phase / slice | DUA required |
|---|---|
| Phase 2: UKB-PPP pQTL coloc | UKB-PPP approved |
| Phase 2: deCODE pQTL coloc | deCODE sumstats portal credentials (or confirm open-access) |
| Phase 3 (T2): MVP trans-ancestry MR | MVP approved |
| Phase 3 (T2): BBJ trans-ancestry MR | BBJ approved |
| Phase 8 (T2): All of Us PRS validation | All of Us Tier 2 approved |
| Phase 9: FinnGen replication | FinnGen (most phenotypes open-access; check) |
| Phase 9: MVP replication | MVP approved |
| Phase 9: BBJ replication | BBJ approved |
| Phase 9: AoU replication | All of Us Tier 2 approved |
