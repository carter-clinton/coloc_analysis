---
phase: quick-260427-azv
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/manuscript/track_a_pivot.md
  - src/R/figures/fig_s2_paired_fit_structural_inflation.R
  - docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.pdf
  - docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.png
  - .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  - .planning/DECISIONS.md
  - .planning/STATE.md
autonomous: true
requirements:
  - AUDIT-V2-HQ1   # SH2B3 narrative sweep across 5 manuscript surfaces
  - AUDIT-V2-HQ2   # Paired-fit structural inflation supplementary figure
  - AUDIT-V2-HQ3   # Conclusion-1 method-namespace reframe
  - AUDIT-V2-QI1   # Citation fix (Wang²⁹ → Zou²⁰)
  - AUDIT-V2-QI2   # Move Methods L82 narrative to new Discussion subsection
  - AUDIT-V2-QI3   # Stale Decision-Pending item 4 deletion
  - AUDIT-V2-NewIssue4  # QTL-coloc caveat in Abstract / FTO callouts
  - AUDIT-V2-NewIssue5  # Fig S7 framing promotion
  - AUDIT-V2-NewIssue6  # Methods L-saturation prose disclosure (11/95)
  - AUDIT-V2-Eval2a-integration  # niter-twist into §3.4
tags: track-a, audit, manuscript, figure, prose, identity-ld, real-ld, susie-rss, coloc-susie, audit-v2, biorxiv

source_of_truth: .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md
plan_file: /home/ckclinto/.claude/plans/track-a-audit-v2-revision-sweep-overnig-cozy-meerkat.md

must_haves:
  truths:
    - "All 13 audit-v2 actionable items (HQ1, HQ2, HQ3, QI1, QI2, QI3, NewIssue1–6, Eval 2(a) integration) land as V2-CLOSED with disk-verifiable evidence."
    - "Where the audit-v2 doc and on-disk per-fit JSONs diverge, disk truth wins. Specifically: (a) identity-LD niter at SH2B3 EUR is 9/3/12 (BMI/HTN/stroke), NOT 100; only real-LD hits niter=100. (b) identity-LD L_saturated=TRUE at SH2B3 EUR is hypertension, NOT BMI."
    - "Figure S2 R script writes 4-panel composite (PIP-top Δ histogram, lead-rank distribution, max-Jaccard histogram, PIP-top scatter) computed entirely from on-disk per-fit JSONs (no LSF, no re-SuSiE fire). Hard-fail asserts paired_n == 48."
    - "Figure S2 PDF + PNG land at docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.{pdf,png} (cairo_pdf, 180mm × 140mm, 600 dpi). Locked scalars emitted to TRACK-A-FROZEN-NUMBERS.md as a new LIVE block."
    - "Conclusion claim 1 (manuscript L252-254) is fully replaced by the audit-v2 drop-in paragraph that names the actual method contrast (SuSiE-RSS + coloc.susie) and cites Figure S2 by name."
    - "QI2 Methods L82 audit-process narrative is excised; new Discussion subsection §Audit-driven Comparator Tightening lands between §Identity-LD Inflation and §Reframing of Cardiometabolic Pleiotropy Claims."
    - "Stale-narrative tokens swept: 'manufactures PP.H4', 'four of five non_converged', 'lost (pair absent', 'credible-set composition collapse' all return 0 grep hits in the manuscript post-sweep. The 'credible-set collapse' phrase remaining in 3 places is in the new 'missing run rather than a documented credible-set collapse' framing only."
    - "Citation integrity at L148: 'Wang et al. 2020²⁹' is purged; only 'Zou et al. 2022²⁰' remains for the SuSiE convergence-theory cite."
    - "Stage 2 source-of-truth TSVs (finemap_summary.tsv, coloc_summary.tsv, tier_assignments.tsv) remain byte-identical (md5 unchanged) pre vs post each commit."
    - "results_identity_ld/ remains gitignored and read-only (DEC-2026-04-25-01); the Figure S2 script reads JSONs from the tree but writes nothing back."
    - "Three new DEC-2026-04-27-XX entries land in .planning/DECISIONS.md documenting HQ3 (namespace reframe), HQ2 (supplementary figure), and QI2 (narrative location)."
    - "12 atomic commits land on main, with commit-message hooks unmodified (no --no-verify, no --amend)."
    - "STATE.md Quick Tasks Completed table receives one new row for quick-260427-azv with full closure summary."
    - "No LSF, no data egress (no scp / rsync / gh release / OSF API); bin/track-a-repro-bundle.sh remains untouched and out of scope."
    - "Original-research framing only: zero forbidden tokens (revision, cleanup, fix-up, mistake, correction, simplified, placeholder, TBD, for now, v1) in any new prose or commit-message body. The audit-v2 sweep is original scientific-integrity work, not post-publication revision."

  ordered_commits:
    1: "docs(quick-260427-azv): land HQ1 — SH2B3 narrative sweep across Abstract, Discussion opener, Fig 3 caption, Table 3"
    2: "docs(quick-260427-azv): land HQ3 — Conclusion claim 1 method-namespace reframe (audit-v2 drop-in)"
    3: "docs(quick-260427-azv): land QI1 + QI3 + HQ1-followup — cite fix, Decision-Pending item-4 deletion, L140 residual stale leak"
    4: "docs(quick-260427-azv): land QI2 — move audit-process narrative from Methods L82 to new Discussion §Audit-driven Comparator Tightening"
    5: "docs(quick-260427-azv): land NewIssue4 + NewIssue5 — QTL-coloc caveat in Abstract/L140 + Fig S7 framing promotion"
    6: "docs(quick-260427-azv): land NewIssue6 + Eval 2(a) integration — Methods L-saturation disclosure + §3.4 niter-twist clause + Fig 3 caption L_sat attribution fix"
    7: "feat(quick-260427-azv): add fig_s2_paired_fit_structural_inflation.R — paired-fit PIP + Jaccard + lead-rank from on-disk JSONs (HQ2)"
    8: "docs(quick-260427-azv): render fig_s2_paired_fit_structural_inflation.{pdf,png} + fix PROJECT_ROOT detection under Rscript"
    9: "docs(quick-260427-azv): land Figure S2 caption + reference in track_a_pivot.md"
    10: "docs(quick-260427-azv): flip TRACK-A-AUDIT-RESPONSE rows to V2-CLOSED — HQ1/HQ2/HQ3/QI1/QI2/QI3 + 6 new issues + Eval 2(a) twist"
    11: "docs(quick-260427-azv): append paired-fit structural inflation LIVE block to TRACK-A-FROZEN-NUMBERS.md (HQ2 scalars)"
    12: "docs(quick-260427-azv): record DEC-2026-04-27-01 (HQ3 namespace) + 02 (HQ2 supp figure) + 03 (QI2 narrative location)"

constraints:
  - "no LSF (gsd-executor must never invoke bsub)"
  - "no data egress (no scp / rsync / gh release / OSF-CLI / HTTP POSTs)"
  - "no OSF portal action (no auth, no upload, no POST)"
  - "no new SuSiE fits (Figure S2 reads existing JSONs; no fitting)"
  - "Stage 2 TSVs byte-identical (md5-attested per 260426-06n precedent)"
  - "results_identity_ld/ untouched (per DEC-2026-04-25-01; gitignored)"
  - "disk truth wins over audit-v2 doc where they diverge"
  - "atomic commits — no --amend, no --no-verify"
  - "single branch (main); no feature branch (per .planning/config.json git.branching_strategy = none)"

scope:
  in_scope:
    - "All 13 audit-v2 actionable prose items + Figure S2 build + 3 tracker updates."
    - "L140 residual stale-narrative leak (HQ1-followup; bundled with QI1+QI3 commit per opportunistic cleanup)."
    - "Fig 3 caption L_saturated attribution fix (HQ1-followup; bundled with NewIssue6 commit)."
  out_of_scope_explicitly_deferred:
    - "HQ#2(i) — SH2B3 EUR L = 20 re-fit (DEFERRED-COMPUTE; needs LSF)"
    - "HQ#2(ii) — drop / flag non-converged fits in yield numerator (DEFERRED-DESIGN; Carter's call)"
    - "HQ#2(iii) — execute canonical BMI–HTN + HTN–stroke coloc.susie pairs (DEFERRED-COMPUTE; needs LSF)"
    - "Eval 3.3 — 28/28 empty coloc.susie interpretation (IN-PROGRESS; gated on HQ#2(i)+(iii))"
    - "Filling 10 [EXTRACT: …] placeholders in Tables 1/2/3/4 + Results subsections (separate quick task; needs aggregator scripts)"
    - "L-sweep re-fit at L ∈ {15, 20, 30} mentioned in NewIssue6 disclosure (DEFERRED-COMPUTE)"
    - "bioRxiv submission itself (manual; user action)"
    - "OSF amendment posting (manual web UI per DEC-2026-04-25-02)"
    - "bin/track-a-repro-bundle.sh execution (manual, post-morning, separate task)"

verification_recipe:
  - "grep -n 'credible-set collapse|manufactures PP.H4|four of five|lost (pair absent' docs/manuscript/track_a_pivot.md → only 3 hits, all in 'missing run rather than a documented credible-set collapse' framing"
  - "grep -n 'Wang et al. 2020²⁹' docs/manuscript/track_a_pivot.md → 0 hits"
  - "sed -n '252,260p' docs/manuscript/track_a_pivot.md | grep -E 'SuSiE-RSS \\\\+ \\`coloc.susie\\`' → PASS; grep -E 'coloc.abf.*inflat' → 0 hits"
  - "grep -n 'We tightened the comparator|earlier Stage 1d narrow-validation' docs/manuscript/track_a_pivot.md → hits only in Discussion §Audit-driven Comparator Tightening + Headline Result + Figure 2 caption (NOT in Methods L82)"
  - "ls docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.{pdf,png} && ls src/R/figures/fig_s2_paired_fit_structural_inflation.R → all three exist"
  - "/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript src/R/figures/fig_s2_paired_fit_structural_inflation.R → 'paired non-empty: 48' with no FAIL/ERROR"
  - "md5sum results/fine_mapping/finemap_summary.tsv results/multitrait/coloc_summary.tsv results/qtl_coloc/tier_assignments.tsv → matches md5_pre captured at task start"
  - "grep -n 'DEC-2026-04-27-0[123]' .planning/DECISIONS.md → 3 entries"
  - "grep -n 'Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md → 1 hit"
  - "grep -n 'V2-CLOSED|V2 sweep' .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md → ≥ 13 V2-CLOSED rows in the new V2 sweep section"
  - "git log --oneline main~12..main → 12 atomic commits"
---
