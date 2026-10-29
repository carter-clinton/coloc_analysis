---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W2d-apply-review-decisions
subsystem: ta-r4 inputs (A3-UKB panel class, QTL scope)
tags: [ta-r4, review-decisions, no-op]
requires: [ta-r4-W2c-qtl-downloads-manifest-and-panel-review]
provides: [W2c-T4 decisions applied before the W4b lock]
affects: [W3a, W4b]
tech-stack:
  added: []
  patterns: []
key-files:
  created: []
  modified:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - "W2d: ukb_native=native and qtl_scope=full (Carter 2026-10-28) -> both branches no-ops"
metrics:
  duration: ~1h20m (incl. 58 min LSF wave-close run)
  completed: 2026-10-28
---

# Phase ta-r4 Plan W2d: Apply review decisions Summary

Carter's W2c-T4 decisions (`ukb_native: native`, `qtl_scope: full`) are the defaults, so W2d changed no code or data;
both no-ops are recorded in the LOG with evidence.

## Evidence

- Preconditions: `coloc_priors.yaml` `locked: false`; `decision_rules.yaml` and `simulation.yaml` do not exist yet; no
  `R4-LOCK.json`. `python -m ta_r4.signoff verify W2c-T4` rc 0 →
  `{"qtl_scope": "full", "trait.hypertension.EUR.sdY": "20.7", "ukb_native": "native"}`. review_decisions.yaml and
  signoffs/W2c-T4.yaml unchanged since `ac4e5452`.
- T1: verify prints `A3_ukb -> EUR_ukb337k_r4`; `git diff --quiet HEAD -- arms.py overlay_A3_ukb.yaml` rc 0;
  overlay/isolation/signoffs tests `62 passed`.
- T2: `qtl_manifest.tsv` 0-diff; 116550 rows = `qtl_compute_estimate.tsv` `full` n_rows 116550; test_qtl_manifest.py
  `14 passed`.
- Wave close (LSF 431166): QUICK 339 passed / 51 deselected (107 s); HEAVY 47 passed / 4 skipped; pins 39 passed; FULL
  1814 passed / 50 skipped / 0 failed = 1864 ids (full_W2d.xml). Vs full_W2c.xml: removed 55 / added 51 (the kkg
  osf→lock-gate swap), changed 0; tests/m3 1299 (1265/34) unchanged. sparse_parent_benchmark.tsv restored.

## Commits

- `99329eca` chore(ta-r4-W2d): T1 ukb_native=native recorded as no-op
- `d222f160` chore(ta-r4-W2d): T2 qtl_scope=full recorded as no-op
- wave-close commit (LOG, STATE, this SUMMARY)

## Deviations from Plan

- The plan's step-0 lock check opens `decision_rules.yaml` and `simulation.yaml`, which do not exist before W3/W4, so it
  raises FileNotFoundError (rc 1) rather than detecting a lock. I treated missing files as unlocked and re-ran the check
  that way (rc 0). The plan file itself is unchanged.

## Self-Check: PASSED
