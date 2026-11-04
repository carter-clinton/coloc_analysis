---
phase: quick-261102-log
plan: 01
status: complete
commits: [2266482b, 53106f8f, 52760f08]
---

# quick-261102-log SUMMARY: W3 mismatch causes + JSON credible-set fix

## Task 1 (2026-11-02, `2266482b`)
Errata E1–E7 appended to TRACK-A-FROZEN-NUMBERS.md (additions only); FINDINGS §4/§7/§8 carry measured causes.

## Task 2 (2026-11-03)
Carter's reply saved verbatim: `carter-d28-reply.txt`, sha256 `9db087ad50631a2fd3c10c37c9653ead9aa5ac945348b4e9c0f444b2bdef1199`
("carter-approved 2026-11-03 / d28: unfreeze"). Format check passed.

## Task 3 (unfreeze branch)

**(a) Pin inventory.** Only CODE pin on the live script: `R_CODE_REF` (tests/m3/test_source_freeze_pins.py), imported by
test_finemap_receipt_early_exit.py and test_qtl_coloc_allele_join.py. Differential substrates left alone: K3_PRE_FIX_REF bf04199,
PRE_K1_REF dc4bbd2, PRE_CHANGE_REF 7b1025d / 6b427bc. `r4_lock_gate.LOCKED_PATHS` includes the script but the W4b lock is not
yet taken. Legacy copies match `legacy_code_sha256.tsv` (3dd76df 62fbe9da…, 02c4404 a5d1edf3…).
**Found:** `test_the_k3_edit_touched_only_two_comment_lines` diffed bf04199 against the working tree (red on any authorized
code change). Now diffs bf04199..656529a via new `K3_FIX_REF` (differential substrate).

**Deviation.** JSON line uses `cs <- fit$sets`, not the proposed `susie_get_cs(fit, Xcorr = R_cs, …)`: `fit$sets` is computed
inside susie_rss from the LD the fit used, which is `R_reg` on `converged_regularized` fits, so a recompute with `R` can differ
at the purity boundary. Sweep and `n_cs_default` changed as proposed (`Xcorr = R_cs`).

**(b) RED** (`tests/ta_r4/test_json_cs_equals_fit_sets.py`, r4_heavy; fixture = e2e region on A2_identity panel):
T2 guard passed (10 unfiltered sets > 5 `fit$sets`); T1 failed: "Left contains 5 more items, first extra item: ['1:17000', '1:44000']".
**(c) GREEN:** `3 passed in 10.31s`. Fixed file sha256 `cc3d9115…f2a5`.
**(d) NC:** line reverted to `susie_get_cs(fit)` → `1 failed, 2 passed` (T1); restored, sha256 identical.
**(e) fit.rds:** fixture md5 pre (656529a) == post (T3 green). Real fit (LSF 483126, serial, r_coloc job env, susieR 0.14.2)
repro_routeC t2d.EUR.SH2B3_12q24: md5 `147f8ea441ed4e488dc749b8336f67a4` both; new JSON 5 sets = fit$sets 5 (was 9).
Written to data/r4/tmp/261102-log/ only.
**(f)** Commit F `53106f8f`. Re-pin `52760f08`: R_CODE_REF bf04199 → 53106f8. Pins tier (3 files) `120 passed`. NCs with
bytecode disabled: R_CODE_REF=2266482 → 2 failed; K3_FIX_REF=53106f8 → 1 failed; restored → 39 passed.
⚠ A first restore run showed a stale-.pyc false red (same-length SHA swapped within one second) — rerun with `-B`.
DEC-2026-11-03-run-susie-rss-json-cs-purity-unfreeze added. Pushed 2266482b..52760f08.

**(g) Wave close** (LSF 483132): see below.
LSF 483132, c010n03, HEAD 52760f08. QUICK `360 passed, 57 deselected` (76.8 s). HEAVY `53 passed, 4 skipped` (18m39s; same
4 W5a/W5b skips; +3 = the new test). PINS `39 passed`. FULL `1 failed, 1840 passed, 50 skipped` (34m21s, full_261102.xml).
Vs full_W3b.xml: common 1888, removed 0, added 3 (all test_json_cs_equals_fit_sets), changed 1:
`tests/m3/test_source_freeze.py::test_the_mask_invariants_are_load_bearing` passed → failed, `assert 820 == 818` (:488).
Cause: a hard-coded live-file code-line count (missed by the step-(a) grep: the test names the file via `SUSIE_R`, not by path).
The property it describes still holds — both mask variants count equal on the live file (820/820) and the pre-fix file (818/818).
**STOPPED per step (g): test not edited; awaiting Carter.** sparse_parent_benchmark.tsv clean; legacy copies sha256 unchanged.

## Close (2026-11-03, Carter: option 1)
`test_the_mask_invariants_are_load_bearing` now asserts `n_real > 0` and that both mask variants give the same count on the
live file (no hard-coded 818). NC: appended `q <- "a\nb trailing\nc"` to the live text → `assert 821 == 823` failed; file
restored (sha256 7528b39b… identical); file 41 passed. FULL (LSF 483423, `full_261103.xml`, `-B`): `1841 passed, 50 skipped`
(36m38s). Vs full_261102.xml: common 1891, removed 0, added 0, changed 1 (that test failure → passed). FINDINGS item 10 updated
to "fixed in 53106f8f". Task closed.
