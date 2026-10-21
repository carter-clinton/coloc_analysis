# ta-r4 plan-check record

Banked by the orchestrator from gsd-plan-checker hand-backs (model output, summarized; the
structured issue ids are verbatim).

## Iteration 1 (2026-10-21) — ISSUES FOUND: 7 blockers, 16 warnings, 6 info
Blockers: B1 human-verify auto-approved under --chain (verified at execute-phase.md:636);
B2 coloc_coverage.py added after the analysis lock; B3 test_osf_gate permanently RED after
posting; B4 live gates/aggregation glob reproduction outputs; B5 OSF API call per LSF job;
B6 W0b oversized; B7 RESEARCH open questions not marked RESOLVED.
Warnings: W1 D-13 glob omits A3_1kg_isect; W2 UKB isect panel re-orientation missing;
W3 HM3 option unimplemented; W4 whole amendment file public; W5 classifier precedence/partial
rule; W6 QTL manifest size unmeasured; W7 W3a/W3b files_modified incomplete; W8 path scan
omits ta_r4 rules; W9 no toy e2e --use-conda run; W10 only 2 negative-control sets;
W11 fixed-SHA pin on old draft; W12 VALIDATION map incomplete; W13 no pre-R4 baseline tag;
W14 W4 5 tasks; W15 382 not ~384 repro fits; W16 quick-run latency.
Resolution: B7 + CONTEXT path by orchestrator (584482d); rest by planner revision 1 (8be8c29).

## Iteration 2 (2026-10-21) — ISSUES FOUND: 1 blocker, 5 warnings, 4 info
Iteration-1 B1, B3–B7 RESOLVED; B2 partly (run_aggregation.py post-lock).
Count cascade (31 regions, 346/320, 29 EUR panels, 730 fits, 4060 coloc) consistent.
BLOCKER: confirmatory row set, CI/McNemar subset, kappa threshold, cluster set and
stat→category derivation unspecified pre-lock (29 "admissible" clusters incl. 19 NC vs 10 EUR).
Warnings: W-1 fabricated sign-off possible; W-2 ukb_native re-decision dead end + W2d no
post-lock guard; W-3 repro manifest keyed by region only + no legacy panel for HLA/BMI_Xq24;
W-4 data/r4 NOT gitignored (measured); W-5 R1_STRUCTURAL re-examination has no deliverable.
Info: W0b2 dense; test_qtl_manifest heavy; HLA ukb too_many_variants; W5a job-count rule filter.
Orchestrator decision for the blocker (rigor rule; Carter can change at W4a lock): confirmatory
set = primary curated EUR rows only (10 admissible curated EUR regions × 10 pairs = 100 rows,
row_class primary, p12_primary, A1 matched), bootstrap clusters = those 10 regions; negative-
control rows are a pre-specified specificity analysis, never inputs to the branch classifier.
