#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""260916-vqq-verify.py — the re-verifier for Stage C NaN error-posture options draft **v2**.

WHAT THIS PROVES (and what it deliberately does not)
====================================================
v2 goes brief-blind to an external methodological adjudicator. Three things must hold, and each is
MEASURED here rather than asserted:

  1. Every citation in v2 resolves, AT A STATED BASIS COMMIT, to text that really says what v2 says
     it says  (families ``a: b: c-key c-count c-res: c: c-quote: c-bind: c-pr: c-ast: c-hand: d: e:
     c-halt:``).
  2. v2's delta from v1 is fully declared and REVERSIBLE to v1's exact bytes  (family ``f:``), and v1
     plus the checker that verified it are byte-unchanged  (family ``imm:``).
  3. Nothing in v2 leaks a recommendation — lexically (``g:``) OR structurally (``bal:``).
     The v1 imbalance was structural, not lexical: kht's inherited word screen scores 0 hits on all
     five v1 option bodies while v1's option word counts spanned 6.0x and only two of its five
     options carried a labelled READING.

NOT SCREENED, ON PURPOSE (recorded so a reader does not mistake the omission for an oversight):
  * §4 MEMBERSHIP — which options leave a region unbanked is a factual property of the options, not a
    presentational choice. Balancing it would be falsification.
  * PER-OPTION CITATION DENSITY — how much cited ground exists at BASIS differs per option as a matter
    of fact. ``report:cites`` PRINTS the per-option citation counts as INFO so the asymmetry is
    visible, but it is never a gate.

BASIS
=====
BASIS is ``74f962d21b07a8b765dfba6c3825448e05eb17e7`` (short ``74f962d``), captured at execution time
in Task 1 of quick-260916-vqq, on branch ``m3-W2-aou-deltas``. Every constant below was RE-DERIVED at
that commit in ``260916-vqq-BASIS-AND-REDERIVATION.md``. Nothing was copied forward from
``260916-kht-verify.py`` because it was green there:

  * ``BASIS``            c93e97b  -> 74f962d21b07a8b765dfba6c3825448e05eb17e7
  * ``SINCE``            2026-08-24 (now FALSE: 1 commit) -> 2026-09-17 (0 commits)
  * ``H3_LINE``          532 -> 567     (.planning/osf_deviations.md gained 35 lines under vqp)
  * every RN citation    +143           (measured per claim, not applied as an offset)
  * every OD citation    +35            (measured per claim, not applied as an offset)
  * the AST anchors      re-anchored on AST-LOCATED symbols/statements, never on line numbers
    (kht's ``c-ast:S2`` is GREEN FOR THE WRONG REASON at BASIS: it asserts the innermost ``def``
    containing RN:1144 is ``process_region``; at BASIS :1144 is an unrelated comment that happens to
    sit inside the same several-hundred-line function, so the +143 shift does not turn it red.)

MODES
=====
  (default)          check v2 at BASIS
  --live             read the working tree instead of BASIS (ST is ALWAYS read at BASIS)
  --source <path>    additionally apply the edit ledger FORWARD to v1 and require byte identity
  --baseline         run the citation families against v1 AT BASIS and reconcile the RED id set,
                     BY SET EQUALITY, against Task 1's hand re-derivation
  --bare-ref-plan    print the expansion plan for bare ``:n`` refs
  --selftest         positive control, then OBSERVE every family RED on a corrupted input
  --json <path>      write results as JSON; REFUSED for any path inside the repo

CONSTRAINTS: stdlib only; py3.9-compatible; the only subprocess is ``git`` with ``cwd=ROOT`` and never
``shell=True``; nothing imported from ``src/``; no network; no writes inside the repo.
"""

from __future__ import print_function

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
assert (ROOT / ".git").exists(), "ROOT %s has no .git" % ROOT

# ============================================================================================
# CONSTANTS — every one re-derived at BASIS in 260916-vqq-BASIS-AND-REDERIVATION.md
# ============================================================================================
BASIS = "74f962d21b07a8b765dfba6c3825448e05eb17e7"
BASIS_SHORT = "74f962d"
OLD_BASIS = "c93e97b"                       # v1's basis; allowed in v2 ONLY in the supersession note
BRANCH = "m3-W2-aou-deltas"
VQP_PREFIX = "docs(quick-260916-vqp)"

BANKED_REL = ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md"

# --- imm: the two IMMUTABLE records (size THEN md5 — a size failure must never silently hash) ---
SOURCE_REL = ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md"
SOURCE_SIZE, SOURCE_LINES, SOURCE_MD5 = 18309, 223, "763f412bb1a8dbdb38f2cc332ed5a21d"
KHT_REL = ".planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py"
KHT_SIZE, KHT_LINES, KHT_MD5 = 88899, 1711, "50a4de7a954db77a6f162b9dcb573504"

# --- a:/b: posted-body anchors, re-measured at BASIS ---
MK_START, MK_END, MK_SIZE, MK_MD5 = 168, 500, 22945, "13a49f543cabcc27ce9f1e589783c060"
MK_CONTROL, MK_CONTROL_MD5 = (167, 500), "8154025b50ef344cd43078f910add359"
OFFSET = 167                                 # mk7ze: P + OFFSET == R
TR_SIZE, TR_MD5 = 9695, "c19be8b2ad7cd6a45fee1d668d8a9cf9"
TR_LINES = 59                                # splitlines(); `wc -l` prints 58 (no trailing newline)
TR_CONTROL_LEN, TR_CONTROL_MD5 = 9694, "0775eef2aa3f4965c42375ed955aced0"

# --- e: the git-freeze property, RE-DERIVED (kht's SINCE = 2026-08-24 is now FALSE) ---
FROZEN_FILES = ["src/python/run_native_ld_panel.py",
                "src/python/fire_verifier.py",
                "src/python/plink_ld_to_npz.py"]
SINCE = "2026-09-17 00:00:00 -0400"          # 0 commits at BASIS
SINCE_CONTROL = "2026-08-01 00:00:00 -0400"  # 7 commits at BASIS (an empty control proves nothing)
NEWEST_TOUCH = "9a3eb9786e20208249d04f5510f5d3799af8ec4c"   # 2026-09-16 19:17:15 -0400 (RAM-1)

# --- c-hand: inputs ---
H2_KEY = "sweep_2026_09_01_COMPLETE"      # HANDOFF.json at BASIS; its "runtime" is cited at HANDOFF.json:142
H3_HEADING = "## 2026-09-03 —"               # found by HEADING SEARCH, not by a literal line number
H3_LINE = 567                                # re-derived at BASIS (was 532 before vqp)
H3_STATUS = "- **Status:** DRAFTED — NOT POSTED"

# --- c-halt: the two passages quick-260916-ocb FALSIFIED, located by UNIQUE content anchors ---
# A-4: every anchor is matched under norm() and asserted UNIQUE (hit count == 1) BEFORE use.
# Bare `RAM-1` is REJECTED: 5 hits (112, 146, 256, 293, 294) and :112 is NOT falsified.
HALT_ANNOTATION = "SUPERSEDED 2026-09-16"    # ASCII, matching vqp's own enforcer exactly (A-6 iv)
HALT_ANCHORS = {
    "H1-meas": "(inherited; a 2,854-variant region cannot use 26.6 GiB)",
    "H1-end": "Clean fix: `subprocess.Popen` + `os.wait4(pid, 0)`, whose `rusage` is that child's own.",
    "H2": "4. Separately and independently: **RAM-1** fix (TDD) and the **00071** anchor.",
}
HALT_REJECTED = {"RAM-1": 5, "Clean fix:": 2}   # measured hit counts; both REJECTED as ambiguous

# ============================================================================================
# PATHS / SHORT
# ============================================================================================
PATHS = {
    "AP": ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md",
    "RF": ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md",
    "RN": "src/python/run_native_ld_panel.py",
    "FV": "src/python/fire_verifier.py",
    "PL": "src/python/plink_ld_to_npz.py",
    "OD": ".planning/osf_deviations.md",
    "HA": ".planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md",
    "DI": ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md",
    "MK": ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md",
    "TR": ".planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt",
    "ST": ".planning/STATE.md",
    "U7": ".planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md",
    # --- new in v2 ---
    "AR": ".planning/debug/260831-seth-brief-blind-review-already-occluded-is-anchor-relative.md",
    "KW": ".planning/quick/260831-kw8-close-seth-s-brief-blind-review-already-/260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md",
    "VS": ".planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md",
    "HJ": ".planning/HANDOFF.json",
}
SHORT = {
    "AP": "AGENT-PROMPT.md", "RF": "READY-TO-FIRE.md", "RN": "run_native_ld_panel.py",
    "FV": "fire_verifier.py", "PL": "plink_ld_to_npz.py", "OD": "osf_deviations.md",
    "HA": "260824-STAGE-B-HALT-…md", "DI": "deferred-items.md", "ST": "STATE.md",
    "AR": "260831-…-anchor-relative.md", "KW": "260901-kw8-PANELWIDE-RECLASSIFICATION.md",
    "VS": "260902-vsp-CONTENT-SPEC.md", "HJ": "HANDOFF.json",
}
AT_BASIS_KEYS = ("ST", "HJ")    # per-session ledgers: ALWAYS read at BASIS, even under --live

# ============================================================================================
# CLAIMS_V1 — v1's 88 positional rows. Used by --baseline, and inherited by v2's table.
# (id, file key, kind "Q"|"T", payload[], NOT-tokens[], edit-id|None)
# The PAYLOADS are the claims themselves (quotes from the cited records), each re-verified at BASIS in
# Task 1. The RANGES are NOT here: they are parsed positionally out of whichever draft is being graded,
# which is exactly what makes --baseline able to go RED on v1 while default mode is GREEN on v2.
# ============================================================================================
CLAIMS_V1 = [
 ("c01", "AP", "T", ["run_native_ld_panel.py", "--mode square", "--ancestry afr"], ["--fail-fast"], None),
 ("c02", "AP", "T", ["without --fail-fast"], [], None),
 ("c03", "AP", "T", ["without --fail-fast"], [], None),
 ("c04", "RF", "T", ["the loop continues", "partial bank"], [], None),
 ("c05", "RN", "Q", ["Stage C runs without --fail-fast"], [], None),
 ("c06", "PL", "T", ["raise ValueError", "square LD carries NaN"], [], None),
 ("c07", "RN", "T", ["plink_ld_to_npz("], [], None),
 ("c08", "RN", "T", ["except Exception", "error: {e}"], [], None),
 ("c09", "RN", "T", ["append_panel_row("], [], None),
 ("c10", "RN", "T", ["if ok:", "_gsutil_upload(out_npz"], [], None),
 ("c11", "RN", "T", ["if fail_fast and", '!= "ok"', "RegionGateError"], [], None),
 ("c12", "FV", "T", ["def _stage_c", "classify_statuses"], [], None),
 ("c13", "FV", "T", ["_FAILURE_STATUSES", '"error:"'], [], None),
 ("c14", "FV", "T", ["_FAILURE_PREFIXES", "STATUS_FAILURE"], [], None),
 ("c15", "FV", "Q", ["Stage C runs without --fail-fast so the loop continues by design; report these to Carter … Do NOT re-fire blindly"], [], None),
 ("c16", "FV", "T", ['"exit_code": 0 if not failed else 1'], [], None),
 ("c17", "AP", "T", ["R8.", "exit 1 means STOP and report"], [], None),
 ("c18", "AP", "T", ["STOP under R8"], [], None),
 ("c19", "FV", "T", ["A RED IS A STOP"], [], None),
 ("c20", "RN", "T", ["if fail_fast and", '!= "ok"'], [], None),
 ("c21", "RN", "T", ['"skipped_idempotent"', "return result"], [], None),
 ("c22", "HA", "T", ["m2_region_00001", "m2_region_00017", "m2_region_00040__sub14", "all `ok`"], [], None),
 ("c23", "RN", "T", ["Deferrals (deferred_infeasible_square", "also halt"], [], None),
 ("c24", "HA", "T", ["m2_region_00057", "read_square_bin", "raised", "square LD carries NaN"], [], None),
 ("c25", "OD", "T", ["m2_region_00149", "offset -1", "single survivor"], [], None),
 ("c26", "TR", "Q", ["The raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract."], [], None),
 ("c27", "MK", "T", ["the raw-panel NaN-raise contract", "continues to RAISE on any NaN"], [], None),
 ("c28", "TR", "Q", ["If the count of occlusion-excluded variants in a region exceeds … the region is … NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation."], [], None),
 ("c29", "MK", "Q", ["Deferral remains NOT auto-exclusion. A region over the ceiling …"], [], None),
 ("c30", "MK", "Q", ["A region over the anomaly gate is deferred for re-diagnosis …"], [], None),
 ("c31", "TR", "Q", ["the region's occlusion-exclusion count exceeds the anomaly gate"], [], None),
 ("c32", "MK", "Q", ["NO fourth branch and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`"], [], None),
 ("c33", "MK", "T", ["DEFERRED when EITHER condition holds", "n_occluded_sites", "n_occluded_rows / n_occluded_sites"], [], None),
 ("c34", "TR", "Q", ["the region contains no occlusion-undefined pair; the panel and fine-mapping result stand unmodified."], [], None),
 ("c35", "TR", "Q", ["… fine-mapping proceeds on the reduced variant set"], [], None),
 ("c36", "TR", "Q", ["All three outcomes are reportable; excluding variants silently (without a manifest), fabricating a correlation value, or choosing the occlusion criterion to obtain a particular fine-mapping result are the only paths not on this list."], [], None),
 ("c37", "TR", "T", ["deviations are logged in .planning/osf_deviations.md", "disclosed in the manuscript"], [], None),
 ("c38", "MK", "T", ["deviation logging", ".planning/osf_deviations.md", "disclosure in the manuscript"], [], None),
 ("c39", "TR", "T", ["Realized outcome branches", "per-region exclusion manifest", "present-rate", "follow-up OSF update", "closeout"], [], None),
 ("c40", "MK", "Q", ["Every region computes its own occlusion count AND its own occluded-site inflation during the production run, so both complete distributions fold in at closeout"], [], None),
 ("c41", "TR", "T", ["correlation fabrication (NaN→0)", "prohibited"], [], None),
 ("c42", "MK", "T", ["correlation", "fabrication (NaN→0) both remain prohibited"], [], None),
 ("c43", "TR", "Q", ["choosing the occlusion criterion to obtain a particular fine-mapping result"], [], None),
 ("c44", "MK", "Q", ["choosing the occlusion criterion to obtain a particular fine-mapping result"], [], None),
 ("c45", "PL", "T", ["NaN check FIRST", "zero-variance variant"], [], None),
 ("c46", "HA", "T", ["FALSIFIED", "nan_count == 1", "diag == 1.0"], [], None),
 ("c47", "RN", "T", ['result["n_dropped_occluded"] = n_dropped_occluded'], [], None),
 ("c48", "RN", "T", ["pln.plink_ld_to_npz("], [], None),
 ("c49", "RN", "T", ['result["status"] = f"error: {e}"', "append_panel_row("], [], None),
 ("c50", "RN", "T", ["if ok:", "_gsutil_upload(out_npz"], [], None),
 ("c51", "RN", "T", ['if result["status"] == "ok":', "_reclaim_region_scratch("], [], None),
 ("c52", "RN", "Q", ["~30+ GiB/region … overflows any finite scratch disk"], [], None),
 ("n01", "RN", "T", ['"skipped_idempotent"', "return result"], [], "E8"),
 ("n07", "RN", "T", ["deferred_infeasible_square", "return result"], [], "E8"),
 ("c53", "RN", "T", ["occlusion_gate.json", '"occ_sites"', '"n_sites"', '"inflation"', '"verdict"'], [], None),
 ("c54", "RN", "T", ["_gsutil_upload(", "gate_sidecar"], [], None),
 ("c55", "RN", "T", ["gate_json", "_gsutil_upload("], [], None),
 ("c56", "RN", "T", ["SKIP guard", "existing", '"skipped_idempotent"'], [], None),
 ("c57", "FV", "T", ["def classify_statuses", "THE GATES WORKING", "FINDING", "HARD_STOP", "UNRECOGNIZED"], [], None),
 ("c58", "FV", "T", ["test_shipped_status_vocabulary_is_covered_by_the_allow_list"], [], None),
 ("c59", "RN", "T", ["deferred_infeasible_square", "return result"], [], None),
 ("c60", "DI", "Q", ["a DISCLOSURE OBLIGATION — not blocking the fire"], [], None),
 ("c61", "FV", "T", ["def check_coverage_disclosure_resolved", "R4-COVERAGE", "deferred-items.md"], [], None),
 ("c62", "RF", "Q", ["a real, reportable outcome"], [], None),
 ("c63", "AP", "Q", ["a real, reportable outcome"], [], None),
 ("c64", "TR", "Q", ["the panel and fine-mapping result stand unmodified"], [], None),
 ("c65", "TR", "Q", ["fine-mapping proceeds on the reduced variant set"], [], None),
 ("c66", "RN", "T", ["return result"], [], None),
 ("c67", "RN", "T", ["pln.plink_ld_to_npz("], [], None),
 ("c68", "TR", "Q", ["the three outcome branches … before any occlusion-handling code fires"], [], None),
 ("n02", "AP", "T", ["~11 days"], [], "E10"),
 ("c69", "FV", "T", ['"counts": counts', '"n_failed"'], [], None),
 ("c70", "OD", "Q", ["no covering record for EITHER member"], [], None),
 ("c71", "MK", "T", ["Clause (a), the occlusion criterion", "flagged as an occluder"], [], None),
 ("c72", "MK", "Q", ["NO new token"], [], None),
 ("c73", "FV", "Q", ["the gates working"], [], None),
 ("c74", "HA", "T", ["MECHANISM CONFIRMED", "0 of 871", "perfectly confounded"], [], None),
 ("c75", "HA", "Q", ["`--fail-fast` is correct for Stage A/B and **must not be carried into Stage C** at an unknown per-region failure rate"], [], None),
 ("n03", "OD", "T", ["single survivor", "21-region scan"], [], "E9"),
 ("n04", "MK", "T", ["A systematic-by-span sample of 21 of the 276 AFR regions"], [], "E9"),
 ("n05", "MK", "T", ["A systematic-by-span sample of 21 of the 276 AFR regions"], [], "E11"),
 ("c76", "OD", "Q", ["to be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"], [], None),
 ("c77", "OD", "Q", ["Production tests the rate on BOTH sides"], [], None),
 ("c78", "OD", "Q", ["NO PREDICATE CHANGE … calibrate-to-pass at n=1"], [], None),
 ("c79", "MK", "Q", ["both complete distributions fold in at closeout"], [], None),
 ("n06", "RF", "T", ["120000", "--max-n-var"], [], "E12"),
 ("c80", "MK", "Q", ["NO new token"], [], None),
 ("c81", "MK", "T", ["both complete distributions fold in at closeout"], [], None),
]

# Task 1's hand re-derivation: the ids whose v1 range no longer carries their payload at BASIS.
# --baseline must reproduce EXACTLY this set, reconciled by SET EQUALITY (ids, not counts).
TASK1_MOVED_OR_FALSE = set("""
c05 c07 c08 c09 c10 c11 c20 c21 c23 c25 c47 c48 c49 c50 c51 c52 c53 c54 c55 c56
c59 c66 c67 c70 c76 c77 c78 n01 n03 n07
""".split())

# ============================================================================================
# DECLARED SCREENS — fixed in the PLAN before a word of v2 existed (<declared_screens> S-1..S-5).
# Do NOT extend, trim or re-tokenize any of this to make v2 green.
# ============================================================================================
OPTION_LETTERS = ["A", "B", "C", "D", "E", "F"]
SUBFIELDS = ["Behaviour:", "Code needed:", "Already pre-registered?", "Consequences:"]
BAND_WORDS = 3.0            # S-2: across the six option units (heading + body)
BAND_READWEIGHT = 2.0       # S-2: WITHIN each option, across that option's READINGs
PRECEDENT_SET = {"A", "C", "F"}     # S-5: the options the R4-COVERAGE precedent fits
PRECEDENT_TOKEN = "R4-COVERAGE"

EVAL_CUES = [
    # inherited from 260916-kht-verify.py EVAL_WORDS (base; measured NON-discriminating on its own:
    # 0 hits in all five of v1's option bodies)
    "not workable", "unworkable", "realistic", "surprise", "only honest", "clearly", "obviously",
    "should", "better", "worse", "prefer", "simply", "merely", "of course", "naturally",
    # added in revision round 1 — the cue classes the blast-radius review actually found
    "listed for completeness", "for completeness", "already argues", "already established",
    "a formality", "in practice", "the obvious", "in any case",
    # added: editorial verbs (the reviewer's own vocabulary for v1's defects)
    "argues against", "stretches", "overstates",
]

G_PATTERNS = [
    # inherited verbatim from 260916-kht-verify.py:1096-1099 (11 patterns)
    r"recommend", r"\bprefer", r"\bsuggest", r"\bpropos(e|es|ed|al)\b", r"\badvis(e|es|ed|able)\b",
    r"\bbest (option|choice|path|course)\b", r"\b(we|i) (favou?r|endorse|lean|urge|advocate)\b",
    r"\bin (our|my) (view|opinion|judgement|judgment)\b", r"\b(right|correct) (choice|option|call)\b",
    r"\bshould (choose|adopt|pick|go with|select)\b", r"\bopt for\b",
    # added in revision round 1
    r"\bthe (default|obvious|natural) (option|choice|course)\b", r"\bleast bad\b",
    r"\bthe way to go\b", r"\bwe would\b", r"\bour (view|position|preference)\b",
]
G_EXEMPT = "with no recommendation"          # must occur EXACTLY once

# ============================================================================================
# v2's OWN claims (appended in Task 2b) and the edit ledger (Task 2b).
# ============================================================================================
# ============================================================================================
# v2's OWN claims: the rows v2 adds to v1's 88, and the two v1 rows v2 drops.
#   c72 (`mk7ze P316 / R483`, "NO new token")  -> superseded in Option B by the FULL sentence
#        (n32, `mk7ze P316-318 / R483-485`), which is what R3(i)'s counter-READING rests on.
#   n05 (`mk7ze P88-89 / R255-256` on Option D's SCAN sentence) -> DROPPED: R6(iii). That sentence
#        describes the pre-committed 21-of-276 occlusion SAMPLE, which is Option C's sentence, where
#        the same citation already lives as n04. A citation on the wrong sentence is a wrong citation.
# CLAIMS is POSITIONAL: it is spliced into v1's order at named anchors, never appended, because the
# engine pairs the Nth parsed citation token with the Nth row.
# ============================================================================================
CLAIMS_DROP = {"c72", "n05"}

CLAIMS_INSERTS = [
 ("before", "c01", ("n00", "OD", "T", ["AFR native-panel DEFINED-ROW TAIL disclosure"], [], None)),
 ("after", "c44", ("n30", "TR", "Q", ["The fully-NaN-row → drop rule (prior item (a) first branch): a variant row that is entirely NaN (a zero-variance / monomorphic-within-analysis-set source) is dropped by MAF / missingness QC. This converges with the new exclude policy and is retained."], [], "E6")),
 ("after", "n30", ("n31", "MK", "T", ["The fully-NaN-row → drop rule"], [], "E6")),
 ("after", "c71", ("n32", "MK", "Q", ["NO fourth branch and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`"], [], "E8")),
 ("after", "n04", ("n33", "OD", "Q", ["Production tests the rate on BOTH sides"], [], "E9")),
 ("after", "n33", ("n34", "AR", "Q", ["`already_occluded == False` means \"not inside THIS anchor's span\"… does not count pairs that survive filtering"], [], "E10")),
 ("after", "c77", ("n35", "HJ", "T", ['"runtime": "48m'], [], "E25")),
 ("after", "n35", ("n36", "KW", "T", ["1h53m", "exit 0"], [], "E10")),
 ("after", "n36", ("n37", "KW", "T", ["m2_region_00001", "m2_region_00008", "m2_region_00062", "m2_region_00081", "m2_region_00120__sub03", "m2_region_00149"], ["m2_region_00057"], "E25")),
 ("after", "n37", ("n38", "VS", "T", ["2 h 40 m 46 s wall"], [], "E10")),
 ("after", "c78", ("n39", "TR", "Q", ["choosing the occlusion criterion to obtain a particular fine-mapping result"], [], "E11")),
 ("after", "n39", ("n40", "MK", "Q", ["the anomaly GATE is a different object from the CRITERION, and recalibrating the gate against a measured population is not that prohibited act"], [], "E11")),
 ("after", "n40", ("n41", "FV", "T", ["_DEFERRAL_PREFIXES", "deferred_infeasible_square"], [], "E11")),
 ("after", "n41", ("n42", "RN", "T", ["deferred_infeasible_square", "return result"], [], "E11")),
 ("after", "n42", ("n43", "DI", "Q", ["a DISCLOSURE OBLIGATION — not blocking the fire"], [], "E11")),
 ("after", "n43", ("n44", "FV", "T", ["def check_coverage_disclosure_resolved", "R4-COVERAGE"], [], "E11")),
 ("after", "n44", ("n45", "TR", "T", ["All three outcomes are reportable"], [], "E11")),
 ("after", "n45", ("n46", "TR", "T", ["the three outcome branches", "before any occlusion-handling code fires"], [], "E11")),
 ("after", "n46", ("n47", "RN", "Q", ["~30+ GiB/region … overflows any finite scratch disk"], [], "E11")),
 ("after", "n47", ("n48", "RF", "T", ["120000", "--max-n-var"], [], "E11")),
 ("after", "c79", ("n49", "RN", "T", ["if ok:"], [], "E13")),
 ("after", "n49", ("n54", "RN", "T", ["_gsutil_upload(", "afreq"], [], "E13")),
 ("after", "n54", ("n50", "RN", "T", ["_gsutil_upload(", "occluded.excludelist"], [], "E13")),
 ("after", "n50", ("n51", "RN", "T", ["_gsutil_upload(", "occlusion_manifest.tsv"], [], "E13")),
 ("after", "n51", ("n52", "RN", "T", ["_gsutil_upload(", "occlusion_gate.json"], [], "E13")),
 ("after", "c81", ("n53", "TR", "T", ["choosing the occlusion criterion to obtain a particular fine-mapping result"], [], "E14")),
]


def build_claims():
    rows = [r for r in CLAIMS_V1 if r[0] not in CLAIMS_DROP]
    for pos, anchor, row in CLAIMS_INSERTS:
        i = [r[0] for r in rows].index(anchor)
        rows.insert(i if pos == "before" else i + 1, row)
    return rows


CLAIMS_NEW = []          # kept for the module contract; v2's table is built by build_claims()


PERMITTED_EDITS = [
 {
  "id": 'E1', "cls": 1,
  "why": 'R1(i)(iv): v2 status block; SUPERSEDES v1 for couriering with a brief-blind-safe reason (no defect count, no option letter); method note recording what is and is not screened (A-7 iii).',
  "old": '# Stage C: what happens to a region that RAISES on a leftover pairwise NaN (options draft)\n\n**Status:** DRAFT, banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by\nan adjudicator who has not seen our reasoning: options are laid out neutrally, with no recommendation.\nEvery claim cites file:line. Labels: **TEXT** = what a posted record says; **CODE** = what shipped code\ndoes; **READING** = an interpretation offered for adjudication, not a finding.',
  "new": "# Stage C: what happens to a region that RAISES on a leftover pairwise NaN (options draft v2)\n\n**Status:** DRAFT v2, banked in the repo (quick-260916-vqq), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by\nan adjudicator who has not seen our reasoning: options are laid out neutrally, with no recommendation.\nEvery claim cites file:line. Labels: **TEXT** = what a posted record says; **CODE** = what shipped code\ndoes; **READING** = an interpretation offered for adjudication, not a finding.\n\n**SUPERSEDES** `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` for couriering: that draft's code citations were written at `c93e97b`, the code basis has since moved, so every citation here was re-derived at the commit stated below, and the options section was restructured for symmetry.\n\n**Method note.** This draft is screened mechanically by\n`.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py`: a phrase\nscreen for advocacy language, and a balance family that measures the option structure — identical\nlabelled sub-fields, READING symmetry within and across options, a word band, an evaluative-cue screen\nover the whole document, precedent placement, and question coverage. Two things are deliberately\n**not** balanced, because both are factually determined and evening them out would be falsification:\nwhich options appear in §4, and how much cited ground each option has. The checker prints per-option\ncitation counts as information only.",
 },
 {
  "id": 'E2', "cls": 2,
  "why": 'R1(i)(ii): the basis statement replaces "Code at HEAD c93e97b" with the full 40-char commit, the branch, and a reader-actionable reproduction instruction plus the checker\'s path.',
  "old": '- Code at HEAD `c93e97b`.',
  "new": '- **Code basis for every citation below:** commit\n  `74f962d21b07a8b765dfba6c3825448e05eb17e7` (short `74f962d`) on branch `m3-W2-aou-deltas`. To read\n  any cited file exactly as it is cited here, run `git show 74f962d:<path>`; every `file:line` below\n  is a 1-based line number in that output. The mechanical re-verification of this draft is\n  `.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py`, run\n  with no arguments from the repository root.',
 },
 {
  "id": 'E3', "cls": 2,
  "why": "R1/R6/R8b: three new Files-cited key entries for the records Option D cites, plus the two scope notes a brief-blind reader needs — that every osf_deviations citation sits inside a DRAFTED - NOT POSTED entry, and that the halt record's RAM-measurement passages are FALSIFIED and nothing here depends on them.",
  "old": '- `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` → `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`',
  "new": '- `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` → `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`\n- `260831-…-anchor-relative.md` → `.planning/debug/260831-seth-brief-blind-review-already-occluded-is-anchor-relative.md`\n- `260901-kw8-PANELWIDE-RECLASSIFICATION.md` → `.planning/quick/260831-kw8-close-seth-s-brief-blind-review-already-/260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md`\n- `260902-vsp-CONTENT-SPEC.md` → `.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md`\n\n⚠ **Scope of the `osf_deviations.md` citations.** Every one of them sits inside a single ledger entry\nheaded "AFR native-panel DEFINED-ROW TAIL disclosure", which is marked **DRAFTED — NOT POSTED**. The\nentry begins at `osf_deviations.md:567` and runs to the end of the file. Nothing cited from it is\nposted text; it is our own working ledger.\n\n⚠ **Scope of the `260824-STAGE-B-HALT-…md` citations.** That record now carries a\n`## ⚠ SUPERSEDED 2026-09-16` section recording that its RAM-measurement passages — the `ru_maxrss`\ninheritance reading and the `subprocess.Popen` + `os.wait4` "clean fix" it prescribed — are\nFALSIFIED. **No citation in this draft depends on those passages**, and the re-verifier gates that\ndisjointness mechanically rather than by inspection.',
 },
 {
  "id": 'E4', "cls": 4,
  "why": 'R8(i): retitle §0 away from "Premise corrections" (which frames the section as a rebuttal of the reader\'s premise) to a neutral measured-premise heading.',
  "label": 'R8(i) §0 heading', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '## 0. Premise corrections: the question is narrower than "the fire will halt"',
  "new": '## 0. Measured premises: what the committed card and the shipped code fix today',
 },
 {
  "id": 'E5', "cls": 4,
  "why": 'R8(ii): v1 pre-dismissed the halt/continue question ("the open question is not halt versus continue"). Both questions are open; C addresses one, A/B/F the other.',
  "label": 'R8(ii) both questions open', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '**So the open question is not halt versus continue.** It is: **what pre-registered disposition does a\nregion get when the raw-panel NaN-raise contract fires, the region banks nothing, and the loop moves\non?** And does settling that need a posted amendment-update before Stage C?',
  "new": '**Two questions are open here, and this draft treats both as open.** The first: **does the\noperator stop the fire when a region raises, or let the loop continue?** Option C addresses that one.\nThe second: **what pre-registered disposition does a region get when the raw-panel NaN-raise contract\nfires, the region banks nothing, and the loop moves on?** Options A, B and F address that one. For\neither: does settling it need a posted amendment-update before Stage C?',
 },
 {
  "id": 'E6', "cls": 4,
  "why": 'R7(i): the only posted rule that disposes of NaN-bearing variants had no §1 row. APPENDED as T9 — T1-T8 are NOT renumbered, because their ids are referenced by name throughout §3, §4 and §5 and renumbering would silently invalidate every reference. The checker carries f:t18 as the named enforcer of that invariant.',
  "label": 'R7(i) T9 appended', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '| T8 | Prohibited or fenced: NaN→0 (trsx5:25; mk7ze P307-308 / R474-475); "choosing the occlusion criterion to obtain a particular fine-mapping result" (trsx5:49; mk7ze P302-305 / R469-472). | as cited |',
  "new": '| T8 | Prohibited or fenced: NaN→0 (trsx5:25; mk7ze P307-308 / R474-475); "choosing the occlusion criterion to obtain a particular fine-mapping result" (trsx5:49; mk7ze P302-305 / R469-472). | as cited |\n| T9 | The one posted rule that disposes of NaN-bearing variants, and it is RETAINED: "The fully-NaN-row → drop rule (prior item (a) first branch): a variant row that is entirely NaN (a zero-variance / monomorphic-within-analysis-set source) is dropped by MAF / missingness QC. This converges with the new exclude policy and is retained." Restated as unchanged at "**The fully-NaN-row → drop rule** and **the raw-panel NaN-raise contract**". | trsx5:37; mk7ze P321 / R488 |',
 },
 {
  "id": 'E7a', "cls": 4,
  "why": 'R4(i): the four labelled sub-fields. The pre-registration answer opens with the scope sentence instead of two unlabelled bullets.',
  "label": 'R4 Option A sub-fields', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '### Option A: run the card as committed (no code change)\n\n- **Behaviour:** no `--fail-fast`. A raising region records `error:`, banks nothing, and the loop\n  continues (P2). At the next check-in the gate exits 1 and the agent reports to Carter (P3). At\n  closeout the region is reported as unbanked and logged as a deviation.\n- **Code needed:** none.\n- **Already pre-registered?**\n  - The *raise* is (T1). The *non-halting loop* is runbook, not OSF.',
  "new": '### Option A: run the card as committed (no code change)\n\n- **Behaviour:** no `--fail-fast`. A raising region records `error:`, banks nothing, and the loop\n  continues (P2). At the next check-in the gate exits 1 and the agent reports to Carter (P3). At\n  closeout the region is reported as unbanked and logged as a deviation.\n- **Code needed:** none. This is the committed card run unchanged, and no file in the fire path moves.\n- **Already pre-registered?** The *raise* is (T1); the *non-halting loop* is runbook, not OSF; the\n  *disposition* is what is at issue.',
 },
 {
  "id": 'E7b', "cls": 3,
  "why": "c66 c67 +143: Option A's gate-returns-before-plink citations re-based, in their final wording.",
  "evidence": {'key': 'RN', 'kind': 'T', 'payload': ['return result'], 'before': [967, 967], 'after': [1110, 1110]},
  "old": '  - The *disposition* is not. No branch fits: NONE needs "the panel and fine-mapping result stand unmodified"\n    (trsx5:43), but nothing was banked; EXCLUDED needs "fine-mapping proceeds on the reduced variant set"\n    (trsx5:45); DEFERRED\'s trigger is the anomaly gate (T3), and 00057\'s gate did **not** fire (a region\n    whose gate fires returns at `run_native_ld_panel.py:967` before plink runs, so it cannot reach the raise at `:1090`).',
  "new": '  - No posted branch fits on its face: NONE needs "the panel and fine-mapping result stand unmodified"\n    (trsx5:43) and nothing was banked; EXCLUDED needs "fine-mapping proceeds on the reduced variant set"\n    (trsx5:45); DEFERRED\'s trigger is the anomaly gate (T3), and 00057\'s gate did **not** fire — a\n    region whose gate fires returns at `run_native_ld_panel.py:1110` before plink runs, so it cannot\n    reach the raise at `:1233`.',
 },
 {
  "id": 'E7c', "cls": 4,
  "why": 'R4(ii): both readings carry an explicit READING label of comparable weight. R4(vii): the supporting material is distributed between them rather than piled under one.',
  "label": 'R4(ii)(vii) Option A readings', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '  - *READING 1:* logging it under T6 changes no criterion, no gate and no variant\'s treatment. A\n    deviation entry plus disclosure is what the posted discipline already requires, so no amendment\n    is needed before code (and no code is involved).\n  - *READING 2:* T5 presents the three branches as the complete\n    list, and trsx5:53 fixes "the three outcome branches … before any occlusion-handling code fires".\n    A region in none of them is a fourth outcome, which may need a posted amendment-update **before**\n    Stage C.\n- **Consequences:**\n  - Each raising region is a coverage gap shaped like R4-COVERAGE (C7), but with **no** registered\n    disclosure obligation or enforcer yet.\n  - After the first raise, every later `stage-c` check-in exits 1 for the rest of the ~11 days (`AGENT-PROMPT.md:393`). Each is\n    an R8 STOP. A *new* failure then shows up on a gate that is already red. The verifier does print\n    per-status counts (`fire_verifier.py:363-370`), so a new failure is visible only by diffing check-ins.\n  - C3, C4 and C5 apply (see §4).\n',
  "new": '  - *READING 1:* logging it under T6 changes no criterion, no gate and no variant\'s treatment. A\n    deviation entry plus manuscript disclosure is what the posted discipline already requires of any\n    deviation, so on this reading nothing is owed before Stage C — and no code is involved either way.\n  - *READING 2:* T5 presents the three branches as the complete list, and trsx5:53 fixes "the three\n    outcome branches … before any occlusion-handling code fires". A region in none of the three is a\n    fourth realized outcome, and on this reading a posted amendment-update is owed **before** Stage C\n    rather than at closeout.\n- **Consequences:** each raising region is a coverage gap shaped like the R4-COVERAGE precedent (C7),\n  but with no registered disclosure obligation and no enforcer yet. After the first raise, every later\n  `stage-c` check-in exits 1 for the rest of the ~11 days (`AGENT-PROMPT.md:393`), and each exit 1 is\n  an R8 STOP, so a *new* failure arrives on a gate that is already red. The verifier does print\n  per-status counts (`fire_verifier.py:363-370`), so a new failure is visible by diffing check-ins.\n  C3, C4 and C5 apply (see §4).\n',
 },
 {
  "id": 'E8a', "cls": 4,
  "why": "R4(i)(ii): the four sub-fields, and v1's single flat *READING:* becomes a labelled READING 1 so it has a peer.",
  "label": 'R4 Option B sub-fields + READING 1', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '### Option B: send raising regions to `BRANCH_AFR_OCC_DEFERRED` (defer, don\'t exclude)\n\n- **Behaviour:** the producer catches this particular raise, records a deferral status, and the\n  verifier PASSes it.\n- **Code needed:** yes. The producer\'s error path, plus either a new status prefix (which turns the C6\n  enforcer red until the vocabulary is extended) or reuse of `deferred_occlusion_anomaly:`.\n- **Already pre-registered?** *READING:* no. DEFERRED is tied to the anomaly-gate trigger (T3), and\n  defer-not-exclude is stated for "a region over the anomaly gate" (T2). Adding a NaN-raise trigger\n  changes what DEFERRED means, which would need an amendment-update **before** code.\n  - Reusing `deferred_occlusion_anomaly:` would record an anomaly the gate did not find.',
  "new": '### Option B: send raising regions to `BRANCH_AFR_OCC_DEFERRED` (defer, don\'t exclude)\n\n- **Behaviour:** the producer catches this particular raise, records a deferral status, and the\n  verifier PASSes it instead of reporting a FINDING.\n- **Code needed:** yes. The producer\'s error path, plus either a new status prefix (which turns the C6\n  enforcer red until the vocabulary is extended) or reuse of `deferred_occlusion_anomaly:`.\n- **Already pre-registered?**\n  - *READING 1:* no. DEFERRED is tied to the anomaly-gate trigger (T3), and defer-not-exclude is\n    stated for "a region over the anomaly gate" (T2). Adding a NaN-raise trigger changes what DEFERRED\n    denotes, which would need an amendment-update **before** code.\n  - Reusing `deferred_occlusion_anomaly:` would record an anomaly the gate did not find.',
 },
 {
  "id": 'E8b', "cls": 3,
  "why": "c70 +35: Option B's no-covering-record citation re-based, in its final wording.",
  "evidence": {'key': 'OD', 'kind': 'Q', 'payload': ['no covering record for EITHER member'], 'before': [703, 704], 'after': [738, 739]},
  "old": '  - The surviving class has "no covering record for EITHER member" (`osf_deviations.md:703-704`, a\n    DRAFTED — NOT POSTED entry), so it is not an occlusion under clause (a) (mk7ze P300-302 / R467-469).',
  "new": '  - The surviving class has "no covering record for EITHER member" (`osf_deviations.md:738-739`, a\n    DRAFTED — NOT POSTED entry), so it is not an occlusion under clause (a) (mk7ze P300-302 / R467-469).',
 },
 {
  "id": 'E8c', "cls": 4,
  "why": "R3(i): a counter-READING of comparable weight, built from cited posted text — mk7ze's own 'NO fourth branch and NO new token' read as a commitment AGAINST token proliferation — with its scope limit stated. R3(ii): the overreach 'the mechanism for this class is already established for 00057' is removed; the mechanism is measured for ONE member and predicted for the second, and whether re-diagnosis is discharged is left OPEN.",
  "label": 'R3(i)(ii) Option B counter-READING', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '  - A new token runs into the explicit "NO new token" sentence (mk7ze P316 / R483). That sentence is\n    scoped to the companion condition, so how far it reaches is itself a question for review.\n- **Consequences:** check-ins stay green. A contract raise would be classified under the deferral PASS, whose stated reason is "the gates working"\n  (`fire_verifier.py:335-336`). "Deferred for\n  re-diagnosis" presumes a diagnosis still to do, but the mechanism for this class is already\n  established for 00057 (`260824-STAGE-B-HALT-…md:150-179`).\n',
  "new": '  - *READING 2:* the same posted text can be read the other way. mk7ze commits to "NO fourth branch\n    and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity\n    companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`" (mk7ze P316-318 / R483-485). A reader\n    could take that as a commitment against token proliferation — directing any disposition that is\n    neither NONE nor EXCLUDED to the SAME token rather than to a new one. Scope limit: that sentence\n    is written about the companion condition, so how far it reaches is itself part of the question.\n- **Consequences:** check-ins stay green. A contract raise would then be classified under the deferral\n  PASS, whose stated reason is "the gates working" (`fire_verifier.py:335-336`). "Deferred for\n  re-diagnosis" presumes a diagnosis still to do: the mechanism is measured for one member,\n  `m2_region_00057` (`260824-STAGE-B-HALT-…md:150-179`), and predicted rather than observed for the\n  second, `m2_region_00149` (P5). Whether "re-diagnosis" is discharged for this class at n=1 is open.\n',
 },
 {
  "id": 'E9a', "cls": 4,
  "why": "R8(iii): 'the Stage B halt record already argues against this' is replaced by the record's sentence as TEXT with no editorial verb — 'already argues' and 'argues against' are both on the declared evaluative-cue list. R4(i)(ii): the four sub-fields and two READINGs.",
  "label": 'R8(iii) + R4 Option C', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '### Option C: halt on each raise and re-diagnose before continuing\n\n- **Behaviour:** literal `--fail-fast` would also halt on already-banked and deferred regions (P4), so\n  this option means the operator stopping the fire at the first `error:` row.\n- **Code needed:** none (runbook change only).\n- **Already pre-registered?** No posted text requires or forbids halting, so no amendment either way.\n- **Consequences:** the Stage B halt record already argues against this at an unknown rate:\n  "`--fail-fast` is correct for Stage A/B and **must not be carried into Stage C** at an unknown\n  per-region failure rate" (`260824-STAGE-B-HALT-…md:104-107`). *For planning only, not a calibrated',
  "new": '### Option C: stop the fire at the first raise and re-diagnose before continuing\n\n- **Behaviour:** literal `--fail-fast` would also halt on already-banked and deferred regions (P4), so\n  this option means the operator stopping the fire at the first `error:` row and resuming by hand.\n- **Code needed:** none. This is a runbook change: the committed command is unchanged and the operator\n  acts on the check-in the gate already produces.\n- **Already pre-registered?**\n  - *READING 1:* no posted text requires halting and none forbids it, so on this reading the choice is\n    operational, sits outside the amendment surface, and carries nothing to post in either direction.\n  - *READING 2:* stopping changes which regions are measured and in what order, and T7 commits the\n    realized branches and the genome-wide present-rate to a closeout update. On this reading an\n    operator-truncated run is a closeout-disclosure question even though the halt itself is not a\n    posted act.\n- **Consequences:** the Stage B halt record states: "`--fail-fast` is correct for Stage A/B and **must\n  not be carried into Stage C** at an unknown per-region failure rate"\n  (`260824-STAGE-B-HALT-…md:104-107`). *For planning only, not a calibrated',
 },
 {
  "id": 'E9b', "cls": 3,
  "why": "n03 +35: Option C's 1-of-21 citation re-based, in its final wording.",
  "evidence": {'key': 'OD', 'kind': 'T', 'payload': ['single survivor', '21-region scan'], 'before': [660, 663], 'after': [695, 698]},
  "old": '  rate:* 1 of 21 sampled regions carries a surviving pair (`osf_deviations.md:660-663`). The sample was systematic-by-span, not',
  "new": '  rate:* 1 of 21 sampled regions carries a surviving pair (`osf_deviations.md:695-698`).',
 },
 {
  "id": 'E9c', "cls": 4,
  "why": "R8(iv): the C rate now carries the ledger's OWN one-sided-sweep caveat beside the systematic-by-span and predicted-not-observed ones. R4(iv): the R4-COVERAGE precedent is named here because C also leaves the region unbanked (declared fitting set {A, C, F}).",
  "label": 'R8(iv) + R4(iv) Option C caveats', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '  random (mk7ze P88-89 / R255-256), and the one case is predicted, not observed (P5). Scaled to 276 that is ≈13 regions, with an\n  exact 95% binomial range of 0.3–66.\n',
  "new": '  Three caveats travel with that number: the sample was systematic-by-span rather than random\n  (mk7ze P88-89 / R255-256); the one case is predicted, not observed (P5); and the ledger\'s own caveat\n  is that this sweep could observe only one side, while "Production tests the rate on BOTH sides"\n  (`:717`). Scaled to 276 that is ≈13 regions, with an exact 95% binomial range of 0.3–66. A region\n  skipped by an operator stop is still unbanked, so the R4-COVERAGE-shaped obligation (C7) reaches it\n  as it does under A.\n',
 },
 {
  "id": 'E10a', "cls": 4,
  "why": "R6(i): the scan alone is ANCHOR-RELATIVE and the expected-raise list needs the separate pcs_panelwide_reclassify pass — both stated with citations. R6(iii): mk7ze P88-89 / R255-256 is REMOVED from the scan sentence; it describes the pre-committed 21-of-276 SAMPLE and already sits on C's sample sentence. R6(iv)+R4(i)(ii): four sub-fields, two labelled READINGs.",
  "label": 'R6(i)(iii) + R4 Option D', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '### Option D: measure before deciding (combines with A or B)\n\n- **Behaviour:** Carter runs the existing pairwise-completeness scan across all 276 AFR regions (mk7ze P88-89 / R255-256) before\n  Stage C, so any posture is chosen against a measured list of regions expected to raise. This is a\n  read-only measurement. *Unmeasured scaling:* the 21-region run took 48 min (STATE.md frontmatter,\n  2026-09-01), which scales linearly to ~10.5 h.\n- **Code needed:** none expected. Whether the scan runs unchanged over all 276 has **not** been checked.\n- **Already pre-registered?** A read-only measurement changes no analysis choice, so no amendment.\n  **But there is a sequencing constraint.** The disclosure\'s prospective production prediction is "to',
  "new": '### Option D: measure the expected raise list before deciding (combines with A, B or F)\n\n- **Behaviour:** Carter runs the pairwise-completeness scan across the AFR regions before Stage C, so\n  any posture is chosen against a measured list rather than against one observed case. The scan alone\n  is **anchor-relative**: "`already_occluded == False` means "not inside THIS anchor\'s span"… does not\n  count pairs that survive filtering" (`260831-…-anchor-relative.md:50-53`), so the list of regions\n  expected to RAISE needs the separate `pcs_panelwide_reclassify` pass on top of it. Both passes are\n  read-only.\n- **Code needed:** none expected for the scan; whether it runs unchanged over all 276 regions has\n  **not** been checked, and the reclassify pass has so far been run only on subsets of them.\n- **Already pre-registered?**\n  - *READING 1:* a read-only measurement changes no analysis choice, no criterion and no variant\'s\n    treatment, so on this reading it sits outside the amendment surface entirely and nothing is owed\n    before it runs.\n  - *READING 2:* there is a sequencing constraint. The disclosure\'s prospective production prediction\n    is "to',
 },
 {
  "id": 'E10b', "cls": 3,
  "why": "c76 c77 +35: Option D's sequencing-constraint citations re-based, in their final wording.",
  "bare_ref": '`:717`',
  "evidence": {'key': 'OD', 'kind': 'Q', 'payload': ['to be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing'], 'before': [685, 689], 'after': [720, 724]},
  "old": '  be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"\n  (`osf_deviations.md:685-689`), and "Production tests the rate on BOTH sides" (`:682`). A full-panel',
  "new": '    be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"\n    (`osf_deviations.md:720-724`), and "Production tests the rate on BOTH sides" (`:717`).',
 },
 {
  "id": 'E10c', "cls": 4,
  "why": 'R6(ii): the MEASURED runtimes with instrument, run and region count. ⚠ The review brief\'s "1h53m for 21 regions" is FALSE and conflates two runs: 1h53m is the 6-region RUN 1 of 2026-09-01; the 21-region reclassify pass is RUN 2 of 2026-09-02 at 2h40m46s. Both scalings are recomputed by the checker from their stated inputs.',
  "label": 'R6(ii) Option D measured runtimes', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '  scan would measure that same both-sides rate before production does; whether that uses up the\n  prediction is question 5.\n- **Consequences:** the regions expected to raise are measured before Stage C instead of observed during it. Needs VM time (Carter).\n',
  "new": '    A full-panel measurement tests that same both-sides rate before production does, and on this\n    reading that is the prediction being spent rather than a neutral measurement.\n- **Consequences:** the regions expected to raise are measured before Stage C instead of observed\n  during it, at the cost of VM time (Carter). Measured runtimes, named by instrument, run and region\n  count: the 21-region pairwise-completeness scan took 48 min (`STATE.md:18`), which scales linearly\n  to ~10.5 h over 276 regions; the `pcs_panelwide_reclassify` pass covered 6 regions in 1 h 53 m on\n  2026-09-01 (`260901-kw8-PANELWIDE-RECLASSIFICATION.md:13`, region count at `STATE.md:485`) and the\n  21 regions that carry rows in 2 h 40 m 46 s on 2026-09-02 (`260902-vsp-CONTENT-SPEC.md:10`), which\n  scales linearly to ~35.2 h over 276 regions. Both scalings are linear extrapolations of a measured\n  run, not measurements.\n',
 },
 {
  "id": 'E11a', "cls": 4,
  "why": "R5(i): the heading cue '(listed for completeness)' is dropped — it is on the declared evaluative-cue list and it sat in the HEADING, where a body-only screen cannot see it. R4(i): Option E gains the four sub-fields it had none of.",
  "label": 'R5(i) + R4 Option E', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '### Option E: change what reaches the matrix (listed for completeness)\n\nOptions here would be widening the predicate to cover −1/+1, a pairwise-completeness exclusion rule, or',
  "new": '### Option E: change what reaches the matrix\n\n- **Behaviour:** widen the occlusion predicate to cover −1/+1 offsets, add a pairwise-completeness\n  exclusion rule, or coerce NaN→0. NaN→0 is prohibited outright (T8), so the live members of this\n  family are the predicate widening and the new exclusion rule.\n- **Code needed:** yes, in the panel-build path — and, for the predicate widening, a rebuild of every\n  region already banked under the current predicate.\n- **Already pre-registered?**',
 },
 {
  "id": 'E11b', "cls": 3,
  "why": "c78 +35: Option E's NO PREDICATE CHANGE citation re-based, in its final wording, with the DRAFTED - NOT POSTED label R5(iii) requires at the point of citation.",
  "evidence": {'key': 'OD', 'kind': 'Q', 'payload': ['NO PREDICATE CHANGE … calibrate-to-pass at n=1'], 'before': [670, 671], 'after': [705, 706]},
  "old": 'NaN→0. NaN→0 is prohibited (T8). The criterion is unchanged and fenced (T8). "NO PREDICATE CHANGE …\ncalibrate-to-pass at n=1" is already recorded (`osf_deviations.md:670-671`). Any new exclusion rule',
  "new": '  - *READING 1:* no. "NO PREDICATE CHANGE … calibrate-to-pass at n=1" is already recorded\n    (`osf_deviations.md:705-706`, a DRAFTED — NOT POSTED entry), and a new exclusion rule is a new\n    criterion, so an amendment-update would be owed **before** code on either live member. That record\n    is our own working ledger rather than posted text, so it binds our practice, not the\n    pre-registration.',
 },
 {
  "id": 'E11c', "cls": 4,
  "why": "R5(ii): 'The criterion is unchanged and fenced (T8)' is replaced by what the posted text actually says — trsx5:49 fences a MOTIVE, and mk7ze P302-305 separates recalibrating the GATE from that act — so the question is OPEN. R7(ii): the new Option F on the deferred_infeasible_square analogue, same four sub-fields, its own READINGs and consequences. R7(iv): the LOW subsection, each item cited or explicitly marked UNCITED, under its own ### heading so the option spans terminate naturally and LOW is excluded from the balance counts (A-6 i).",
  "label": 'R5(ii) + R7(ii) Option F + R7(iv) LOW', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": 'would be an amendment-update **before** code.\n\n---\n',
  "new": '  - *READING 2:* what the posted text fences is narrower than "any change". trsx5:49 fences\n    "choosing the occlusion criterion to obtain a particular fine-mapping result", and mk7ze separates\n    recalibration from that act: "the anomaly GATE is a different object from the CRITERION, and\n    recalibrating the gate against a measured population is not that prohibited act"\n    (mk7ze P302-305 / R469-472). On this reading a change made for a stated methodological reason is\n    not the fenced act.\n- **Consequences:** this is the only family that changes which variants reach the matrix, so it moves\n  the panel itself rather than the disposition of a region that banks nothing. Regions banked under\n  the current predicate would then be inconsistent with regions built after it unless they are\n  rebuilt, which is compute that has not been scoped here.\n\n### Option F: record an operational `deferred_*` status not mapped to a posted branch\n\n- **Behaviour:** the producer records a distinct operational status — say `deferred_pairwise_nan:` —\n  which the verifier treats as a deferral PASS, while the draft asserts nothing about whether the\n  region falls under `BRANCH_AFR_OCC_DEFERRED` or under any posted branch. The disposition question is\n  answered at closeout, in the open, rather than at fire time.\n- **Code needed:** yes. A new prefix in the producer\'s error path and one entry in the verifier\'s\n  deferral allow-list (`fire_verifier.py:300-303`), which the C6 enforcer holds honest.\n- **Already pre-registered?**\n  - *READING 1:* the shipped code already carries this exact shape. `deferred_infeasible_square`\n    (`run_native_ld_panel.py:1009-1015`) is an operational `deferred_*` status that is in the verifier\n    vocabulary and in none of the three posted branches, registered in-repo as "a DISCLOSURE\n    OBLIGATION — not blocking the fire" (`deferred-items.md:1148-1191`) with a named enforcer\n    (`fire_verifier.py:875-939`). On this reading the precedent is the surface that governs.\n  - *READING 2:* that precedent is in-repo, not posted. trsx5:49 presents the branch list as closed\n    and trsx5:53 fixes the three outcome branches before any occlusion-handling code fires, so a new\n    operational token is still a fourth realized outcome in the record. On this reading an\n    amendment-update is owed **before** code, exactly as under B.\n- **Consequences:** check-ins stay green without asserting anything about the posted branch list. The\n  region still banks nothing, so the R4-COVERAGE-shaped obligation (C7) reaches it as under A and C —\n  and unlike A, this option would register that obligation and its enforcer when the status is added.\n\n### LOW: three further options with less cited ground at this basis\n\nBrevity here reflects how much cited ground exists at this basis, not a ranking.\n\n- **LOW-1 — a per-region pairwise-completeness pre-check at fire time.** Run the completeness check\n  for a region before its plink pass, so a region expected to raise is dispositioned before the\n  compute and the scratch are spent: the docstring puts intermediates at "~30+ GiB/region … overflows\n  any finite scratch disk" (`run_native_ld_panel.py:866-868`) against a `--max-n-var` ceiling of\n  120,000 (`READY-TO-FIRE.md:369-370`). **Cited.**\n- **LOW-2 — re-run on a different sample set, or with sample-level QC.** A different analysis set\n  changes which rows are monomorphic-within-set, and so which pairs are structurally undefined.\n  **UNCITED:** no posted or in-repo record at this basis states what that would do to this class.\n- **LOW-3 — the downstream effect on AFR fine-mapping and coloc denominators.** A region that banks\n  nothing is absent from the panel and therefore from every downstream denominator. **UNCITED:** the\n  posted text defines the panel-stands and reduced-set cases but says nothing about an unbanked\n  region, which is the §1 sweep finding restated.\n\n---\n',
 },
 {
  "id": 'E12', "cls": 4,
  "why": 'R2: uploading evidence fixes X1 only. X2 (scratch reclaimed only on ok), X3 (a region with no .npz is recomputed on every re-fire) and X4 apply to B regardless — and the new Option F also leaves the region unbanked, so F belongs in the scope.',
  "label": 'R2 §4 heading', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": "## 4. Issues that apply to any option that leaves a raising region unbanked (A, C, and B unless B's code also uploads evidence)",
  "new": "## 4. Issues that apply when a raising region banks nothing (A, C and F; and B, where adding uploads to B's code would close X1 but not X2–X4)",
 },
 {
  "id": 'E13', "cls": 4,
  "why": 'R7(iii): the excludelist and the occlusion manifest upload under the SAME `if ok:` block as the gate sidecar. MEASURED at BASIS by AST containment (never by line number): that block encloses FIVE upload calls, so the allele-frequency sidecar is lost too — four artifacts besides the .npz, where the review listed two. Reported as a finding.',
  "label": 'R7(iii) X1 completeness', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '- **X1: evidence egress versus the mk7ze closeout commitment.** mk7ze P247-250 commits that "both\n  complete distributions fold in at closeout". A raising region\'s sidecar (site counts, inflation) is\n  written locally but never uploaded (C4). Its `n_dropped_occluded` row count does reach the panel TSV\n  (C2); its site count and inflation do not. As shipped, the closeout distributions would be missing\n  every raising region unless scratch is harvested by hand. Closing that gap in code touches the fire\n  path and needs a decision.',
  "new": '- **X1: evidence egress versus the mk7ze closeout commitment.** mk7ze P247-250 commits that "both\n  complete distributions fold in at closeout". A raising region\'s gate sidecar (site counts,\n  inflation) is written locally but never uploaded (C4) — and the same `if ok:` block\n  (`run_native_ld_panel.py:1245`) gates four further per-region artifacts: the allele-frequency\n  sidecar (`:1251-1252`), the **excludelist** (`:1257-1261`), the **occlusion manifest**\n  (`:1266-1271`) and the gate sidecar (`:1277-1282`). A raising region therefore loses four egress\n  artifacts besides the `.npz` itself, not one. Its `n_dropped_occluded` row count does reach the\n  panel TSV (C2); its allele frequencies, site count, inflation, excludelist and manifest do not. As shipped, the closeout\n  distributions would be missing every raising region unless scratch is harvested by hand. Closing\n  that gap in code touches the fire path and needs a decision.',
 },
 {
  "id": 'E14', "cls": 4,
  "why": 'R4(vi): every question carries an explicit option tag and the union of tags is exactly {A..F}, so no option is silently left un-interrogated (measured: v1 interrogates A, B, the precedent, X1 and D and never C or E). R4(iv): the precedent question sits in neither the first nor the last slot. R4(viii)+A-7(i): one neutral sentence on the labels AND on the question order. The word "Should" is removed: it is on the declared evaluative-cue list.',
  "label": 'R4(vi)(viii) + A-7(i) §5', "origin": 'orchestrator-specified, blast-radius 260916 finding B2',
  "old": '## 5. Questions for the adjudicator\n\n1. Does a region that banks nothing *because the raw-panel NaN-raise contract fired* fall under any of\n   the three posted branches (T4, T3)? If not, does T5 require a posted amendment-update before Stage C,\n   or is a deviation entry plus disclosure (T6) enough?\n2. Would routing such a region to `BRANCH_AFR_OCC_DEFERRED` change what DEFERRED means (T3), and does\n   "NO new token" (mk7ze P316) reach beyond the companion condition?\n3. Should the R4-COVERAGE precedent (C7: a disclosure obligation with a named enforcer, not blocking\n   the fire) govern this class?\n4. Does honouring mk7ze P247-250 require that a raising region\'s gate evidence reach the bucket (X1)?\n   If so, must that land before Stage C?\n5. Does a full-panel scan (D) before the disclosure is posted use up the prospective production\n   prediction?',
  "new": '## 5. Questions for the adjudicator\n\nThe A–F labels are inherited and alphabetical: they carry no ranking, and the order in §3 is not an\nordering by merit. The question order below follows the option order and likewise carries no ranking.\n\n1. Does a region that banks nothing *because the raw-panel NaN-raise contract fired* fall under any of\n   the three posted branches (T4, T3)? If not, does T5 require a posted amendment-update before Stage\n   C, or is a deviation entry plus disclosure (T6) enough? (Options A, B, F)\n2. Would routing such a region to `BRANCH_AFR_OCC_DEFERRED` change what DEFERRED means (T3), and does\n   "NO new token" (mk7ze P316) reach beyond the companion condition? (Options B, F)\n3. Is an operator stop at the first raise a matter the posted text speaks to at all, and does an\n   operator-truncated run raise a closeout-disclosure question under T7? (Options C, D)\n4. Does the R4-COVERAGE precedent (C7: a disclosure obligation with a named enforcer, not blocking the\n   fire) govern this class? (Options A, C, F)\n5. Does honouring mk7ze P247-250 require that a raising region\'s gate evidence — sidecar, excludelist\n   and occlusion manifest — reach the bucket (X1)? If so, must that land before Stage C? (Options A,\n   B, C, F)\n6. Does a full-panel measurement before the disclosure is posted use up the prospective production\n   prediction, and would changing the occlusion criterion for a stated methodological reason be the\n   act trsx5:49 fences? (Options D, E)',
 },
 {
  "id": 'E15', "cls": 3,
  "why": 'c05 +143: the --fail-fast help text moved with the RAM-1 launcher insertion.',
  "evidence": {'key': 'RN', 'kind': 'Q', 'payload': ['Stage C runs without --fail-fast'], 'before': [1325, 1328], 'after': [1468, 1471]},
  "old": '--fail-fast" (`run_native_ld_panel.py:1325-1328`).',
  "new": '--fail-fast" (`run_native_ld_panel.py:1468-1471`).',
 },
 {
  "id": 'E16', "cls": 3,
  "why": "c07 c08 c09 c10 c11 +143: P2's whole CODE trace re-based.",
  "bare_ref": '`:1287-1289`',
  "evidence": {'key': 'RN', 'kind': 'T', 'payload': ['except Exception', 'error: {e}'], 'before': [1144, 1146], 'after': [1287, 1289]},
  "old": '**P2: Without the flag, a raising region does not stop the loop (CODE).** The NaN raise is\n`plink_ld_to_npz.read_square_bin` (`plink_ld_to_npz.py:218-228`), called at\n`run_native_ld_panel.py:1090-1093`. `process_region` catches it (`:1144-1146`) and records\n`status = "error: square LD carries NaN …"`. The panel row is appended (`:1148`), no `.npz` is uploaded\n(uploads happen only under `if ok:`, `:1101-1107`), and the region returns. The loop raises only\n`if fail_fast and status != "ok"` (`:1278-1279`).',
  "new": '**P2: Without the flag, a raising region does not stop the loop (CODE).** The NaN raise is\n`plink_ld_to_npz.read_square_bin` (`plink_ld_to_npz.py:218-228`), called at\n`run_native_ld_panel.py:1233-1236`. `process_region` catches it (`:1287-1289`) and records\n`status = "error: square LD carries NaN …"`. The panel row is appended (`:1291`), no `.npz` is uploaded\n(uploads happen only under `if ok:`, `:1244-1250`), and the region returns. The loop raises only\n`if fail_fast and status != "ok"` (`:1421-1422`).',
 },
 {
  "id": 'E17', "cls": 3,
  "why": "c20 c21 c23 +143: P4's fail-fast, skip and deferral citations re-based.",
  "evidence": {'key': 'RN', 'kind': 'T', 'payload': ['"skipped_idempotent"', 'return result'], 'before': [806, 815], 'after': [949, 958]},
  "old": '**P4: Adding `--fail-fast` to Stage C would halt on regions already banked.** The flag raises on any\n`status != "ok"` (`run_native_ld_panel.py:1278`). An already-banked region returns\n`skipped_idempotent` (`:806-815`), and `00001`, `00017` and `00040__sub14` are banked\n(`260824-STAGE-B-HALT-…md:20-21`). It also halts on every deferral (`run_native_ld_panel.py:1325-1328`).',
  "new": '**P4: Adding `--fail-fast` to Stage C would halt on regions already banked.** The flag raises on any\n`status != "ok"` (`run_native_ld_panel.py:1421`). An already-banked region returns\n`skipped_idempotent` (`:949-958`), and `00001`, `00017` and `00040__sub14` are banked\n(`260824-STAGE-B-HALT-…md:20-21`). It also halts on every deferral (`run_native_ld_panel.py:1468-1471`).',
 },
 {
  "id": 'E18', "cls": 3,
  "why": 'c25 +35: osf_deviations.md gained 35 lines above this entry under vqp.',
  "evidence": {'key': 'OD', 'kind': 'T', 'payload': ['m2_region_00149', 'offset -1', 'single survivor'], 'before': [657, 663], 'after': [692, 698]},
  "old": '(`.planning/osf_deviations.md:657-663`, a DRAFTED — NOT POSTED ledger',
  "new": '(`.planning/osf_deviations.md:692-698`, a DRAFTED — NOT POSTED ledger',
 },
 {
  "id": 'E19', "cls": 3,
  "why": 'c47 c48 c49 c50 +143: §2 row C2 re-based.',
  "evidence": {'key': 'RN', 'kind': 'T', 'payload': ['result["n_dropped_occluded"] = n_dropped_occluded'], 'before': [1068, 1069], 'after': [1211, 1212]},
  "old": '| C2 | The raise becomes `status="error: …"`. The row keeps `n_dropped_occluded` (set at `run_native_ld_panel.py:1068-1069`, before conversion at `:1090`). No `.npz` upload. | `run_native_ld_panel.py:1144-1148`, `:1101-1107` |',
  "new": '| C2 | The raise becomes `status="error: …"`. The row keeps `n_dropped_occluded` (set at `run_native_ld_panel.py:1211-1212`, before conversion at `:1233`). No `.npz` upload. | `run_native_ld_panel.py:1287-1291`, `:1244-1250` |',
 },
 {
  "id": 'E20', "cls": 3,
  "why": 'c51 c52 +143: §2 row C3 re-based.',
  "evidence": {'key': 'RN', 'kind': 'Q', 'payload': ['~30+ GiB/region … overflows any finite scratch disk'], 'before': [723, 725], 'after': [866, 868]},
  "old": '| C3 | Local scratch is reclaimed **only** when `status == "ok"`. The docstring puts intermediates at "~30+ GiB/region … overflows any finite scratch disk". | `:1149-1154`, `:723-725` |',
  "new": '| C3 | Local scratch is reclaimed **only** when `status == "ok"`. The docstring puts intermediates at "~30+ GiB/region … overflows any finite scratch disk". | `:1292-1297`, `:866-868` |',
 },
 {
  "id": 'E21', "cls": 3,
  "why": 'n01 n07 c53 c54 c55 +143: §2 row C4 re-based.',
  "evidence": {'key': 'RN', 'kind': 'T', 'payload': ['occlusion_gate.json', '"occ_sites"'], 'before': [923, 939], 'after': [1066, 1082]},
  "old": '| C4 | The gate sidecar (`occ_sites`, `n_sites`, inflation, verdict) is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at `run_native_ld_panel.py:806-815`, an infeasible one at `:866-872`). It is uploaded **only** on deferral or on `ok`. | written `:923-939`; uploaded `:961-965` (deferral), `:1129-1139` (inside `if ok:`) |',
  "new": '| C4 | The gate sidecar (`occ_sites`, `n_sites`, inflation, verdict) is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at `run_native_ld_panel.py:949-958`, an infeasible one at `:1009-1015`). It is uploaded **only** on deferral or on `ok`. | written `:1066-1082`; uploaded `:1104-1108` (deferral), `:1272-1282` (inside `if ok:`) |',
 },
 {
  "id": 'E22', "cls": 3,
  "why": 'c56 +143: §2 row C5 re-based.',
  "evidence": {'key': 'RN', 'kind': 'T', 'payload': ['SKIP guard', 'existing'], 'before': [799, 815], 'after': [942, 958]},
  "old": '| C5 | Resume skips a region only if its `.npz` exists, so an `error:` region is recomputed on every re-fire. | `:799-815` |',
  "new": '| C5 | Resume skips a region only if its `.npz` exists, so an `error:` region is recomputed on every re-fire. | `:942-958` |',
 },
 {
  "id": 'E23', "cls": 3,
  "why": "c59 +143: §2 row C7's producer-site citation re-based.",
  "evidence": {'key': 'RN', 'kind': 'T', 'payload': ['deferred_infeasible_square', 'return result'], 'before': [866, 872], 'after': [1009, 1015]},
  "old": '| C7 | Precedent for a region that banks nothing outside the three posted branches: `deferred_infeasible_square` (`run_native_ld_panel.py:866-872`). Registered in-repo as "a DISCLOSURE OBLIGATION — not blocking the fire", with measured numbers owed at publication, a remedy path recorded, and a named enforcer. | `deferred-items.md:1148-1191`; enforcer `fire_verifier.py:875-939` |',
  "new": '| C7 | Precedent for a region that banks nothing outside the three posted branches: `deferred_infeasible_square` (`run_native_ld_panel.py:1009-1015`). Registered in-repo as "a DISCLOSURE OBLIGATION — not blocking the fire", with measured numbers owed at publication, a remedy path recorded, and a named enforcer. | `deferred-items.md:1148-1191`; enforcer `fire_verifier.py:875-939` |',
 },
 {'id': 'E24', 'cls': 4, 'label': 'f68 E-S: key maps HANDOFF.json, not STATE.md', 'origin': 'orchestrator brief-blind finding 2026-09-17 (quick-260917-f68)', 'why': 'E-S: v2 no longer cites STATE.md, so the Files-cited key maps HANDOFF.json in its place.', 'old': '- `STATE.md` → `.planning/STATE.md`', 'new': '- `HANDOFF.json` → `.planning/HANDOFF.json`'},
 {'id': 'E25', 'cls': 4, 'amends': 'E10c', 'bare_ref': '`:47-61`', 'label': 'f68 E-S: Option D re-cited', 'origin': 'orchestrator brief-blind finding 2026-09-17 (quick-260917-f68)', 'why': "E-S: the 48-min runtime is re-cited to HANDOFF.json:142 and the 6-region count to kw8's verdict rows :47-61, so no STATE.md line is cited; declared as amending E10c, which stays byte-unchanged.", 'old': '  count: the 21-region pairwise-completeness scan took 48 min (`STATE.md:18`), which scales linearly\n  to ~10.5 h over 276 regions; the `pcs_panelwide_reclassify` pass covered 6 regions in 1 h 53 m on\n  2026-09-01 (`260901-kw8-PANELWIDE-RECLASSIFICATION.md:13`, region count at `STATE.md:485`) and the\n  21 regions that carry rows in 2 h 40 m 46 s on 2026-09-02 (`260902-vsp-CONTENT-SPEC.md:10`), which\n  scales linearly to ~35.2 h over 276 regions. Both scalings are linear extrapolations of a measured\n  run, not measurements.\n', 'new': '  count: the 21-region pairwise-completeness scan took 48 min (`HANDOFF.json:142`), which scales\n  linearly to ~10.5 h over 276 regions; the `pcs_panelwide_reclassify` pass covered\n  6 regions in 1 h 53 m on 2026-09-01 (`260901-kw8-PANELWIDE-RECLASSIFICATION.md:13`; its verdict\n  rows at `:47-61` name the 6 regions) and the 21 regions that carry rows in 2 h 40 m 46 s on\n  2026-09-02 (`260902-vsp-CONTENT-SPEC.md:10`), which scales linearly to ~35.2 h over 276 regions.\n  Both scalings are linear extrapolations of a measured run, not measurements.\n'},
 {'id': 'E26', 'cls': 4, 'amends': 'E7c', 'label': 'f68 D1: Option A points to X4', 'origin': 'Carter decision 2026-09-17 (quick-260917-f68)', 'why': 'D1 "State it once": Option A points to X4. It says "the disclosure obligation" (X4\'s heading noun) because "that obligation" would have no antecedent in Option A; amends E7c.', 'old': 'precedent (C7),\n  but with no registered disclosure obligation and no enforcer yet.', 'new': 'precedent (C7);\n  whether the disclosure obligation has an enforcer is X4.'},
 {'id': 'E27', 'cls': 4, 'amends': 'E11c', 'label': 'f68 D1: Option F drops the unlike-A clause', 'origin': 'Carter decision 2026-09-17 (quick-260917-f68)', 'why': 'D1 "State it once": Option F carries the same X4 pointer as Option A, byte-identical; amends E11c.', 'old': 'as under A and C —\n  and unlike A, this option would register that obligation and its enforcer when the status is added.', 'new': 'as under A and C;\n  whether the disclosure obligation has an enforcer is X4.'},
 {'id': 'E28', 'cls': 4, 'label': 'f68 D1: X4 states the enforcer fact once', 'origin': 'Carter decision 2026-09-17 (quick-260917-f68)', 'why': 'D1 "State it once": X4 is the single statement of the enforcer fact and names both options that add a status (orchestrator wording B5).', 'old': '**X4: the disclosure obligation has no enforcer.** R4-COVERAGE has one (C7). This class does not.', 'new': '**X4: the disclosure obligation has no enforcer.** R4-COVERAGE has one (C7); this class has none\n  under A, B, C or F as written. Under F, and under B with a new status prefix, one could be\n  registered at the point the status is added.'},
 {'id': 'E29', 'cls': 4, 'amends': 'E14', 'label': 'f68 D2: question counts are not a weighting', 'origin': 'Carter decision 2026-09-17 (quick-260917-f68)', 'why': 'D2 "Split Q6": one §5 sentence, on its own line because the line before it is already 101 columns; amends E14.', 'old': 'The question order below follows the option order and likewise carries no ranking.', 'new': 'The question order below follows the option order and likewise carries no ranking.\nThe number of questions that name an option is not a weighting of that option.'},
 {'id': 'E30', 'cls': 4, 'amends': 'E14', 'label': 'f68 D2: Q6 split, E gets its own question', 'origin': 'Carter decision 2026-09-17 (quick-260917-f68)', 'why': 'D2 "Split Q6": Q6 (Option D) and Q7 (Option E), each clause verbatim; amends E14.', 'old': '6. Does a full-panel measurement before the disclosure is posted use up the prospective production\n   prediction, and would changing the occlusion criterion for a stated methodological reason be the\n   act trsx5:49 fences? (Options D, E)', 'new': '6. Does a full-panel measurement before the disclosure is posted use up the prospective production\n   prediction? (Option D)\n7. Would changing the occlusion criterion for a stated methodological reason be the act trsx5:49\n   fences? (Option E)'},
 {'id': 'E31', 'cls': 4, 'amends': 'E8a', 'label': 'f68 O2: Option B names the C6 check as F does', 'origin': 'orchestrator symmetry edit O2 2026-09-17 (quick-260917-f68)', 'why': 'O2 symmetry: Option B describes the new-prefix mechanism in the same terms as Option F ("which the C6 enforcer checks"), with no new citation; amends E8a.', 'old': 'plus either a new status prefix (which turns the C6\n  enforcer red until the vocabulary is extended) or reuse of `deferred_occlusion_anomaly:`.', 'new': "plus either a new status prefix and its entry in\n  the verifier's deferral allow-list, which the C6 enforcer checks, or reuse of\n  `deferred_occlusion_anomaly:`."},
 {'id': 'E32', 'cls': 4, 'amends': 'E11c', 'label': 'f68 O2: Option F says checks', 'origin': 'orchestrator symmetry edit O2 2026-09-17 (quick-260917-f68)', 'why': 'O2 symmetry: Option F ends with the same phrase as Option B ("which the C6 enforcer checks"); amends E11c.', 'old': 'which the C6 enforcer holds honest.', 'new': 'which the C6 enforcer checks.'},
]


class VerifyError(Exception):
    pass


_GIT_MEMO = {}


def git(*args):
    """Run git with cwd=ROOT (never shell=True). Memoized per process on the exact argv."""
    key = tuple(args)
    if key not in _GIT_MEMO:
        _GIT_MEMO[key] = subprocess.run(["git"] + list(args), cwd=str(ROOT), capture_output=True)
    return _GIT_MEMO[key]


def md5(b):
    return hashlib.md5(b).hexdigest()


def inside_root(p):
    p = Path(p).resolve()
    r = ROOT.resolve()
    return r == p or r in p.parents


class Reader(object):
    """Cited-file reader: `git show BASIS:<path>` (default) or the working tree (--live).

    Every key in AT_BASIS_KEYS (ST, HJ) is ALWAYS read at BASIS (a ledger whose head moves every
    session is not a citable surface in --live mode); `lk:hj-basis` is the named enforcer.  `overrides` maps a repo-relative path to a file on disk; it is the ONLY way
    --selftest corrupts an input, so no working-tree file is ever mutated.
    """

    def __init__(self, live=False, overrides=None, basis=None, at_basis_keys=None):
        self.live = live
        self.at_basis_rels = frozenset(
            PATHS[k] for k in (AT_BASIS_KEYS if at_basis_keys is None else at_basis_keys))
        self.overrides = dict(overrides or {})
        self.basis = basis or BASIS
        self._cache = {}

    def raw(self, rel, at_basis=False):
        if rel in self.overrides:
            return Path(self.overrides[rel]).read_bytes()
        from_tree = bool(self.live and not at_basis and rel not in self.at_basis_rels)
        key = (rel, from_tree)
        if key not in self._cache:
            if from_tree:
                self._cache[key] = (ROOT / rel).read_bytes()
            else:
                r = git("show", "%s:%s" % (self.basis, rel))
                if r.returncode != 0:
                    raise VerifyError("git show %s:%s rc=%d %s" % (
                        self.basis, rel, r.returncode, r.stderr.decode("utf-8", "replace").strip()))
                self._cache[key] = r.stdout
        return self._cache[key]

    def text(self, rel, at_basis=False):
        return self.raw(rel, at_basis).decode("utf-8")

    def lines(self, rel, at_basis=False):
        return self.text(rel, at_basis).splitlines()


# --------------------------------------------------------------------------------------------
# normalization + matching
# --------------------------------------------------------------------------------------------
_QMAP = (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'))


def norm(s):
    for a, b in _QMAP:
        s = s.replace(a, b)
    s = re.sub(r"[*_`]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.lower().strip()


def haystacks(raw, is_py):
    hs = [norm(raw)]
    if is_py:
        hs.append(norm(re.sub(r'"\s*f?"', "", raw)))
    return hs


def seg_in(needle, hay):
    """Quote match: `…`-separated normalized non-empty segments occur IN ORDER in hay."""
    segs = [x for x in (norm(p) for p in needle.split("…")) if x]
    if not segs:
        return False
    pos = 0
    for sg in segs:
        i = hay.find(sg, pos)
        if i < 0:
            return False
        pos = i + len(sg)
    return True


def byte_lines(b, start, end):
    ls = b.splitlines(keepends=True)
    if start < 1 or end > len(ls) or start > end:
        return None
    return b"".join(ls[start - 1:end])


def range_text(lines, rng):
    a, b = rng
    if a < 1 or b > len(lines) or a > b:
        return None
    return "\n".join(lines[a - 1:b])


def mk_posted_lines(mk_bytes):
    ext = byte_lines(mk_bytes, MK_START, MK_END)
    if ext is None:
        raise VerifyError("mk7ze extract lines %d-%d not available" % (MK_START, MK_END))
    return ext.decode("utf-8").splitlines()


def match_payload(raw, is_py, kind, payload, nots):
    hs = haystacks(raw, is_py)
    miss = []
    for needle in payload:
        if kind == "Q":
            ok = any(seg_in(needle, h) for h in hs)
        else:
            ok = any(norm(needle) in h for h in hs)
        if not ok:
            miss.append(needle)
    present = [n for n in nots if any(norm(n) in h for h in hs)]
    return miss, present


def content_check(reader, fkey, rng, kind, payload, nots, prng=None):
    """Payload inside a 1-based inclusive cited range. NEVER clamped: an out-of-range citation is a
    RED, not a silently-truncated PASS. MK rows are checked at BOTH the repo range and the posted
    P range, because a repo-only check would pass on text a reader of the POSTED body cannot see."""
    rel = PATHS[fkey]
    probs = []
    lines = reader.lines(rel)
    raw = range_text(lines, rng)
    if raw is None:
        probs.append("range %d-%d outside [1,%d] of %s" % (rng[0], rng[1], len(lines), fkey))
    else:
        miss, present = match_payload(raw, rel.endswith(".py"), kind, payload, nots)
        if miss:
            probs.append("%s:%d-%d missing %r" % (fkey, rng[0], rng[1], miss))
        if present:
            probs.append("%s:%d-%d NOT-token present %r" % (fkey, rng[0], rng[1], present))
    if fkey == "MK":
        if prng is None:
            prng = (rng[0] - OFFSET, rng[1] - OFFSET)
        posted = mk_posted_lines(reader.raw(rel))
        raw2 = range_text(posted, prng)
        if raw2 is None:
            probs.append("posted P%d-%d outside [1,%d]" % (prng[0], prng[1], len(posted)))
        else:
            miss2, present2 = match_payload(raw2, False, kind, payload, nots)
            if miss2:
                probs.append("posted P%d-%d missing %r" % (prng[0], prng[1], miss2))
            if present2:
                probs.append("posted P%d-%d NOT-token present %r" % (prng[0], prng[1], present2))
    return (not probs), "; ".join(probs)


# --------------------------------------------------------------------------------------------
# citation parser / Files-cited key / bare-ref resolution / paragraph units
# --------------------------------------------------------------------------------------------
CITE = re.compile(
    r'`(?P<file>[^`\s:]*(?:\.|…)(?:md|py|txt|json)):(?P<a>\d+)(?:-(?P<b>\d+))?`'
    r'|`:(?P<ba>\d+)(?:-(?P<bb>\d+))?`'
    r'|\btrsx5:(?P<ta>\d+)(?:-(?P<tb>\d+))?'
    r'|\bmk7ze P(?P<pa>\d+)(?:-(?P<pb>\d+))?(?:\s*/\s*R(?P<ra>\d+)(?:-(?P<rb>\d+))?)?')

KEY_RE = re.compile(r'\*\*Files cited\*\*[^\n]*\n((?:- [^\n]*\n)+)')


def _rng(a, b):
    a = int(a)
    return (a, int(b) if b is not None else a)


def parse_citations(draft):
    out = []
    for m in CITE.finditer(draft):
        g = m.groupdict()
        c = {"start": m.start(), "end": m.end(), "text": m.group(0)}
        if g["file"] is not None:
            c.update(kind="explicit", file=g["file"], rng=_rng(g["a"], g["b"]))
        elif g["ba"] is not None:
            c.update(kind="bare", rng=_rng(g["ba"], g["bb"]))
        elif g["ta"] is not None:
            c.update(kind="trsx5", rng=_rng(g["ta"], g["tb"]))
        else:
            p = _rng(g["pa"], g["pb"])
            r = _rng(g["ra"], g["rb"]) if g["ra"] is not None else None
            c.update(kind="mk7ze", p=p, r=r,
                     rng=r if r is not None else (p[0] + OFFSET, p[1] + OFFSET))
        out.append(c)
    return out


def parse_key(draft):
    m = KEY_RE.search(draft)
    if not m:
        return None
    entries, bad = [], []
    for ln in m.group(1).split("\n"):
        if not ln:
            continue
        body = ln[2:]
        if body.count(" → ") != 1:
            bad.append(ln)
            continue
        left, right = body.split(" → ")
        shorts = re.findall(r"`([^`]+)`", left)
        fm = re.fullmatch(r"`([^`]+)`", right.strip())
        if not shorts or not fm:
            bad.append(ln)
            continue
        for s in shorts:
            entries.append((s, fm.group(1)))
    return {"entries": entries, "bad": bad, "span": (m.start(), m.end())}


def keymap_of(key):
    km = {}
    if key:
        for s, f in key["entries"]:
            km.setdefault(s, set()).add(f)
    return km


def resolve(cites, km):
    """A bare `:n` ref inherits the nearest PRECEDING explicit resolution. That inheritance is the
    reason c-res: exists: a bare ref that drifts under the wrong parent resolves silently."""
    ctx = None
    for c in cites:
        k = c["kind"]
        if k == "explicit":
            f = c["file"]
            if (ROOT / f).is_file():
                res = f
            else:
                fs = km.get(f, set())
                res = sorted(fs)[0] if len(fs) == 1 else None
            c["resolved"] = res
            ctx = res
        elif k == "bare":
            c["resolved"] = ctx
        elif k == "trsx5":
            c["resolved"] = PATHS["TR"]
        else:
            c["resolved"] = PATHS["MK"]
    return cites


_UNIT_START = re.compile(r"^\s*(- |\d+\. |#)")


def _is_table(line):
    return line.lstrip().startswith("|")


def unit_for_offset(draft, off):
    """The paragraph / list-item / table-row unit a quote must be BOUND to, so that `c-bind:` cannot
    be satisfied by the same words appearing three paragraphs away."""
    lines = draft.split("\n")
    starts, pos = [], 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln) + 1
    idx = 0
    for i, s in enumerate(starts):
        if s <= off:
            idx = i
        else:
            break
    if _is_table(lines[idx]):
        return lines[idx]
    a = idx
    while a > 0:
        cur = lines[a]
        if cur.strip() == "" or _is_table(cur):
            a += 1
            break
        if _UNIT_START.match(cur):
            break
        a -= 1
    b = idx
    while b + 1 < len(lines):
        nxt = lines[b + 1]
        if nxt.strip() == "" or _UNIT_START.match(nxt) or _is_table(nxt):
            break
        b += 1
    return "\n".join(lines[a:b + 1])


# ============================================================================================
# a: / b:  — the POSTED-BODY anchors (size THEN md5, each with a control that must NOT match)
# ============================================================================================
def check_anchor_mk(mk_bytes, draft, ctrl=None):
    out = []
    ext = byte_lines(mk_bytes, MK_START, MK_END)
    if ext is None:
        out.append(("a:extract", False, "mk7ze lines %d-%d unavailable" % (MK_START, MK_END)))
        return out
    out.append(("a:size", len(ext) == MK_SIZE, "%d B (want %d)" % (len(ext), MK_SIZE)))
    if len(ext) == MK_SIZE:                       # size THEN md5: never hash past a size failure
        h = md5(ext)
        out.append(("a:md5", h == MK_MD5, "%s (want %s)" % (h, MK_MD5)))
    else:
        out.append(("a:md5", False, "SKIPPED after size failure — a size failure must not silently hash"))
    ctrl = ctrl or MK_CONTROL
    ctl = byte_lines(mk_bytes, ctrl[0], ctrl[1])
    if ctl is None:
        out.append(("a:control", False, "control range unavailable"))
    else:
        hc = md5(ctl)
        out.append(("a:control", hc != MK_MD5 and hc == MK_CONTROL_MD5,
                    "control lines %d-%d md5 %s (want %s, and != the anchor)"
                    % (ctrl[0], ctrl[1], hc, MK_CONTROL_MD5)))
    nd = norm(draft)
    out.append(("a:stated", ("22,945" in draft or str(MK_SIZE) in draft) and norm(MK_MD5) in nd,
                "draft states BOTH the size and the md5 of the extract"))
    out.append(("a:ctlstated", MK_CONTROL_MD5[:8] in draft,
                "draft states the control hash prefix %s (so a reader can re-run the control)"
                % MK_CONTROL_MD5[:8]))
    return out


def check_anchor_tr(tr_bytes, draft, ctrl_len=None):
    out = []
    out.append(("b:size", len(tr_bytes) == TR_SIZE, "%d B (want %d)" % (len(tr_bytes), TR_SIZE)))
    if len(tr_bytes) == TR_SIZE:
        h = md5(tr_bytes)
        out.append(("b:md5", h == TR_MD5, "%s (want %s)" % (h, TR_MD5)))
    else:
        out.append(("b:md5", False, "SKIPPED after size failure"))
    nl = len(tr_bytes.decode("utf-8").splitlines())
    out.append(("b:lines", nl == TR_LINES,
                "%d lines by splitlines() (want %d; `wc -l` prints %d — the file has no trailing newline)"
                % (nl, TR_LINES, nl - 1)))
    cl = TR_CONTROL_LEN if ctrl_len is None else ctrl_len
    ctl = tr_bytes[:cl]
    hc = md5(ctl)
    out.append(("b:control", hc != TR_MD5 and hc == TR_CONTROL_MD5,
                "first %d B md5 %s (want %s, and != the anchor)" % (cl, hc, TR_CONTROL_MD5)))
    nd = norm(draft)
    out.append(("b:stated", ("9,695" in draft or str(TR_SIZE) in draft) and norm(TR_MD5) in nd,
                "draft states BOTH the size and the md5 of the posted body"))
    return out


# ============================================================================================
# c-key / c-count / c-res: / c: / c-quote: / c-bind: / c-pr:  — the citation engine
# ============================================================================================
def check_citations(draft, claims, reader, prefix=""):
    """Positional check of every citation token in `draft` against `claims`.

    Positional (not id-keyed) on purpose: it is the only form that catches a citation ADDED to the
    prose without a matching CLAIMS row, and a CLAIMS row left behind when its citation is deleted.
    """
    res = []
    key = parse_key(draft)
    if key is None:
        res.append((prefix + "c-key", False, "no **Files cited** block found"))
        km = {}
    else:
        probs = list(key["bad"])
        km = keymap_of(key)
        for s, fs in sorted(km.items()):
            if len(fs) != 1:
                probs.append("short form %r maps to %d paths" % (s, len(fs)))
        tracked = set(PATHS.values())
        for s, fs in sorted(km.items()):
            for f in fs:
                if not (ROOT / f).is_file():
                    probs.append("key target %r is not a file" % f)
                elif f not in tracked:
                    probs.append("key target %r is not in PATHS" % f)
        body = draft[:key["span"][0]] + draft[key["span"][1]:]
        for s in sorted(km):
            if s not in body:
                probs.append("short form %r never used outside the key" % s)
        res.append((prefix + "c-key", not probs,
                    "%d short forms -> %d paths; %s"
                    % (len(km), len(set(f for fs in km.values() for f in fs)),
                       "; ".join(probs) if probs else "every short form maps to one tracked path and is used")))

    cites = resolve(parse_citations(draft), km)
    res.append((prefix + "c-count", len(cites) == len(claims),
                "parsed %d citation tokens, CLAIMS has %d rows" % (len(cites), len(claims))))
    n = min(len(cites), len(claims))
    for i in range(n):
        c = cites[i]
        cid, fkey, kind, payload, nots, _edit = claims[i]
        want = PATHS[fkey]
        res.append((prefix + "c-res:" + cid, c.get("resolved") == want,
                    "%s -> %s (want %s)" % (c["text"], c.get("resolved"), want)))
        if c.get("resolved") != want:
            res.append((prefix + "c:" + cid, False, "resolution mismatch; content not checked"))
            continue
        prng = c.get("p") if fkey == "MK" else None
        try:
            ok, msg = content_check(reader, fkey, c["rng"], kind, payload, nots, prng)
        except VerifyError as e:
            ok, msg = False, str(e)
        res.append((prefix + "c:" + cid, ok,
                    msg if msg else "%s:%d-%d carries %d payload token(s)"
                    % (fkey, c["rng"][0], c["rng"][1], len(payload))))
        if kind == "Q":
            q = payload[0]
            nd = norm(draft)
            present = seg_in(q, nd)
            res.append((prefix + "c-quote:" + cid, present,
                        "quoted string present in the draft" if present else "quote NOT in the draft"))
            unit = unit_for_offset(draft, c["start"])
            bound = seg_in(q, norm(unit))
            res.append((prefix + "c-bind:" + cid, bound,
                        "quote is in the SAME unit as its citation" if bound
                        else "quote is NOT in the citation's own paragraph/row unit"))
        if c["kind"] == "mk7ze" and c.get("r") is not None:
            p, r = c["p"], c["r"]
            okpr = (p[0] + OFFSET == r[0]) and (p[1] + OFFSET == r[1])
            res.append((prefix + "c-pr:" + cid, okpr,
                        "P%s + %d == R%s" % (p, OFFSET, r)))
    return res, cites


# ============================================================================================
# c-ast: — STRUCTURAL facts about the shipped code.
# Every anchor is AST-LOCATED (a FunctionDef by name, a Raise by its message constant, an assignment
# target, If-body containment by node range). NEVER a bare line number: kht's S2 asserts "the innermost
# def containing RN:1144 is process_region" and is GREEN FOR THE WRONG REASON at BASIS, because :1144
# is now an unrelated comment that still happens to sit inside that same several-hundred-line function.
# ============================================================================================
def _funcs(tree):
    return {n.name: n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _contains(outer, node):
    return outer.lineno <= node.lineno and (node.end_lineno or node.lineno) <= (outer.end_lineno or outer.lineno)


def _calls(node, name):
    """Calls whose callee renders as `name` or `<anything>.name`."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id == name:
                out.append(n)
            elif isinstance(f, ast.Attribute) and f.attr == name:
                out.append(n)
    return out


def _joined_prefix(node):
    """The leading constant text of a str / f-string value, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and node.values:
        v = node.values[0]
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            return v.value
    if isinstance(node, ast.BinOp):
        return _joined_prefix(node.left)
    return None


def _status_assigns(node):
    """Assignments of the form result["status"] = <str-ish>, with their constant prefix."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            t = n.targets[0]
            if (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                    and t.value.id == "result"):
                sl = t.slice
                k = sl.value if isinstance(sl, ast.Constant) else None
                if k == "status":
                    out.append((n, _joined_prefix(n.value)))
    return out


def check_ast(reader):
    out = []

    def run(fid, fn):
        try:
            ok, msg = fn()
        except Exception as e:                    # a broken anchor is RED, never a silent skip
            ok, msg = False, "EXC %s: %s" % (type(e).__name__, e)
        out.append(("c-ast:" + fid, ok, msg))

    rn_src = reader.text(PATHS["RN"])
    fv_src = reader.text(PATHS["FV"])
    pl_src = reader.text(PATHS["PL"])
    rn, fv, pl = ast.parse(rn_src), ast.parse(fv_src), ast.parse(pl_src)
    rnf, fvf, plf = _funcs(rn), _funcs(fv), _funcs(pl)

    def a1():
        f = rnf.get("process_region")
        return (f is not None and isinstance(f, ast.FunctionDef),
                "process_region is a def at RN:%s-%s" % (f.lineno, f.end_lineno) if f else "absent")

    def a2():
        f = rnf["process_region"]
        hits = []
        for n in ast.walk(f):
            if isinstance(n, ast.Try):
                body_calls = _calls(n, "plink_ld_to_npz")
                if not body_calls:
                    continue
                for h in n.handlers:
                    for asg, pre in _status_assigns(h):
                        if pre and pre.startswith("error: "):
                            hits.append((n.lineno, body_calls[0].lineno, asg.lineno, pre))
        return (len(hits) >= 1,
                "try/except in process_region: try@RN:%s wraps plink_ld_to_npz@RN:%s; its handler sets "
                "result[\"status\"] = %r @RN:%s" % (hits[0][0], hits[0][1], hits[0][3], hits[0][2])
                if hits else "no try wrapping plink_ld_to_npz whose handler sets an `error: ` status")

    def a3():
        f = plf.get("read_square_bin")
        if f is None:
            return False, "read_square_bin absent"
        for n in ast.walk(f):
            if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call):
                fn_ = n.exc.func
                nm = fn_.id if isinstance(fn_, ast.Name) else getattr(fn_, "attr", None)
                if nm == "ValueError" and n.exc.args:
                    pre = _joined_prefix(n.exc.args[0]) or ""
                    if "square LD carries NaN" in pre:
                        return True, ("read_square_bin raises ValueError(%r…) at PL:%s"
                                      % (pre[:34], n.lineno))
        return False, "no ValueError('square LD carries NaN…') raise inside read_square_bin"

    def a4():
        want = {"_OK_STATUSES": ("ok", "skipped_idempotent"),
                "_DEFERRAL_PREFIXES": ("deferred_infeasible_square", "deferred_occlusion_anomaly"),
                "_FAILURE_PREFIXES": ("error:",)}
        got, probs = {}, []
        for n in fv.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                nm = n.targets[0].id
                if nm in want and isinstance(n.value, ast.Tuple):
                    vals = tuple(e.value for e in n.value.elts if isinstance(e, ast.Constant))
                    got[nm] = (vals, n.lineno)
        for nm, w in sorted(want.items()):
            if nm not in got:
                probs.append("%s absent" % nm)
            elif got[nm][0] != w:
                probs.append("%s == %r (want %r)" % (nm, got[nm][0], w))
        return (not probs, "; ".join(probs) if probs else
                "FV module-level: " + ", ".join("%s@:%d" % (k, v[1]) for k, v in sorted(got.items())))

    def a5():
        f = rnf["process_region"]
        for asg, pre in _status_assigns(f):
            if pre and pre.startswith("deferred_infeasible_square"):
                return True, ("process_region emits result[\"status\"] = %r… at RN:%s"
                              % (pre[:32], asg.lineno))
        return False, "no deferred_infeasible_square status assignment in process_region"

    def a6():
        """THE X1 FACT, by AST CONTAINMENT (not by line number): the .npz, the excludelist, the
        occlusion manifest and the gate sidecar are ALL uploaded inside one `if ok:` body."""
        f = rnf["process_region"]
        ifok = [n for n in ast.walk(f)
                if isinstance(n, ast.If) and isinstance(n.test, ast.Name) and n.test.id == "ok"]
        if len(ifok) != 1:
            return False, "expected exactly one `if ok:` in process_region, found %d" % len(ifok)
        blk = ifok[0]
        ups = _calls(f, "_gsutil_upload")
        # MEASURED at BASIS: the `if ok:` body gates FIVE uploads, not the four the review listed —
        # the per-region allele-frequency sidecar is in there too. Reported as a finding.
        want = {"npz": "out_npz", "afreq": ".afreq", "excludelist": ".occluded.excludelist",
                "manifest": ".occlusion_manifest.tsv", "sidecar": "gate_json"}
        inside_calls, outside_calls = [], []
        for c in ups:
            seg = ast.get_source_segment(rn_src, c) or ""
            (inside_calls if any(_contains(s, c) for s in blk.body)
             else outside_calls).append((c.lineno, seg))
        got = {}
        for k, tok in want.items():
            hit = [ln for ln, seg in inside_calls if tok in seg]
            if hit:
                got[k] = hit[0]
        missing = sorted(k for k in want if k not in got)
        # the DEFERRAL sidecar upload (gate_sidecar) is a DIFFERENT call and must live OUTSIDE
        defer = [ln for ln, seg in outside_calls if "gate_sidecar" in seg]
        ok = (not missing) and len(inside_calls) == 5 and len(defer) == 1
        return (ok, "if ok: @RN:%d body encloses %d upload call(s): %s%s; the deferral sidecar upload "
                "is OUTSIDE it at RN:%s"
                % (blk.lineno, len(inside_calls),
                   ", ".join("%s@RN:%d" % (k, got[k]) for k in sorted(got)),
                   ("; MISSING %s" % missing) if missing else "", defer or "ABSENT"))

    def a7():
        f = rnf.get("run_native_ld_panel") or rnf["process_region"]
        calls = []
        for fn_ in (rnf.get("run_native_ld_panel"), rnf.get("process_region"), rn):
            if fn_ is None:
                continue
            calls += _calls(fn_, "_reclaim_region_scratch")
        calls = {c.lineno: c for c in calls}.values()
        bad = []
        for c in calls:
            guarded = False
            for n in ast.walk(rn):
                if isinstance(n, ast.If) and any(_contains(s, c) for s in n.body):
                    seg = ast.get_source_segment(rn_src, n.test) or ""
                    if '"status"' in seg and '"ok"' in seg:
                        guarded = True
            if not guarded:
                bad.append("RN:%d" % c.lineno)
        return (bool(calls) and not bad,
                "%d _reclaim_region_scratch call site(s) at %s, each guarded by a status == \"ok\" test%s"
                % (len(calls), sorted(c.lineno for c in calls),
                   ("; UNGUARDED: %s" % bad) if bad else ""))

    def a8():
        f = fvf.get("check_coverage_disclosure_resolved")
        if f is None:
            return False, "check_coverage_disclosure_resolved absent"
        seg = ast.get_source_segment(fv_src, f) or ""
        return ("R4-COVERAGE" in seg,
                "check_coverage_disclosure_resolved at FV:%s-%s names R4-COVERAGE"
                % (f.lineno, f.end_lineno))

    def a9():
        f = rnf.get("run_native_ld_panel")
        if f is None:
            return False, "run_native_ld_panel absent"
        for n in ast.walk(f):
            if isinstance(n, ast.If) and isinstance(n.test, ast.BoolOp) and isinstance(n.test.op, ast.And):
                seg = ast.get_source_segment(rn_src, n.test) or ""
                if "fail_fast" in seg and '!= "ok"' in seg:
                    raises = [r for r in ast.walk(n) if isinstance(r, ast.Raise)]
                    txt = " ".join((ast.get_source_segment(rn_src, r) or "") for r in raises)
                    if "RegionGateError" in txt:
                        return True, ("fail-fast raise guarded by `%s` at RN:%d, raising RegionGateError"
                                      % (seg.replace("\n", " ")[:60], n.lineno))
        return False, "no `if fail_fast and … != \"ok\"` guard raising RegionGateError"

    for fid, fn in (("A1", a1), ("A2", a2), ("A3", a3), ("A4", a4), ("A5", a5),
                    ("A6", a6), ("A7", a7), ("A8", a8), ("A9", a9)):
        run(fid, fn)
    return out


# ============================================================================================
# c-hand: — every hand-computed number RECOMPUTED from its stated inputs
# ============================================================================================
def binom_cdf(k, n, p):
    from math import comb
    return sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(k + 1))


def clopper_pearson(x, n, conf=0.95):
    a = (1.0 - conf) / 2.0
    lo, hi = 0.0, 1.0
    if x > 0:
        l, h = 0.0, 1.0
        for _ in range(200):
            m = (l + h) / 2.0
            if 1.0 - binom_cdf(x - 1, n, m) > a:
                h = m
            else:
                l = m
        lo = (l + h) / 2.0
    if x < n:
        l, h = 0.0, 1.0
        for _ in range(200):
            m = (l + h) / 2.0
            if binom_cdf(x, n, m) < a:
                h = m
            else:
                l = m
        hi = (l + h) / 2.0
    return lo, hi


H_REGEX = {
    "rate": r"1 of (\d+) sampled regions",
    "scale": r"Scaled to (\d+) that is ≈(\d+) regions",
    "ci": r"exact 95% binomial range of ([\d.]+)–(\d+)",
    "scan": r"took (\d+) min",
    "lin": r"scales linearly to ~([\d.]+) h over (\d+) regions",
    "run1": r"(\d+) regions in 1 h 53 m",
    "run2": r"(\d+) regions that carry rows in 2 h 40 m 46 s",
    "scratch": r"≈([\d.]+) GB at the ([\d,]+)-variant ceiling",
    "entry": r"entry begins at `osf_deviations\.md:(\d+)`",
}


def check_hand(draft, reader):
    out = []
    # The draft is hard-wrapped at ~100 columns, so a stated number and its units routinely straddle a
    # newline. Every H pattern therefore runs against a whitespace-FLATTENED copy; the raw draft is
    # still what every other family reads.
    flat = re.sub(r"\s+", " ", draft)

    def need(key):
        m = re.search(H_REGEX[key], flat)
        return m

    # H1 — the C rate, recomputed from its own stated inputs
    m1, m2, m3 = need("rate"), need("scale"), need("ci")
    if not (m1 and m2 and m3):
        out.append(("c-hand:H1", False, "the C-rate sentence did not parse (%s/%s/%s)"
                    % (bool(m1), bool(m2), bool(m3))))
    else:
        n = int(m1.group(1)); tot = int(m2.group(1)); stated = int(m2.group(2))
        lo_s, hi_s = float(m3.group(1)), int(m3.group(2))
        pt = tot * 1.0 / n
        lo, hi = clopper_pearson(1, n)
        ok = (round(pt) == stated and abs(lo * tot - lo_s) < 0.05 and abs(hi * tot - hi_s) <= 0.5)
        out.append(("c-hand:H1", ok,
                    "1/%d scaled to %d = %.4f -> stated %d; Clopper-Pearson 95%% = %.6f..%.6f -> "
                    "%.2f..%.2f, stated %.1f–%d" % (n, tot, pt, stated, lo, hi,
                                                         lo * tot, hi * tot, lo_s, hi_s)))

    # H2 — the 48-minute scan and its linear scaling
    ms, ml = need("scan"), re.findall(H_REGEX["lin"], flat)
    if not (ms and ml):
        out.append(("c-hand:H2", False, "the scan-runtime sentence did not parse"))
    else:
        mins = int(ms.group(1))
        st_h, st_n = float(ml[0][0]), int(ml[0][1])
        calc = mins * st_n / 21.0 / 60.0
        hj = json.loads(reader.text(PATHS["HJ"], at_basis=True))
        rt = hj[H2_KEY]["runtime"].split()[0]
        marker = rt == "%dm" % mins
        out.append(("c-hand:H2", abs(calc - st_h) < 0.06 and marker,
                    "%d min x %d/21 = %.2f h, stated ~%.1f h; HANDOFF.json at BASIS %s.runtime starts %r: %s"
                    % (mins, st_n, calc, st_h, H2_KEY, rt, marker)))

    # H6 — Option D's MEASURED reclassify runtimes (the brief's "1h53m for 21 regions" is FALSE)
    r1, r2 = need("run1"), need("run2")
    if not (r1 and r2 and len(ml) >= 2):
        out.append(("c-hand:H6", False, "the reclassify-runtime sentences did not parse"))
    else:
        n1, n2 = int(r1.group(1)), int(r2.group(1))
        st_h, st_n = float(ml[1][0]), int(ml[1][1])
        calc = 9646.0 * st_n / n2 / 3600.0
        kw = reader.text(PATHS["KW"])
        vs = reader.text(PATHS["VS"])
        src_ok = ("1h53m" in kw) and ("2 h 40 m 46 s wall" in vs) and ("21 regions carry rows" in vs)
        mv = re.search(r"its verdict rows at `:(\d+)-(\d+)` name the (\d+) regions", flat)
        cnt_ok = False
        if mv:
            ka, kb_, kst = int(mv.group(1)), int(mv.group(2)), int(mv.group(3))
            kwl = reader.text(PATHS["KW"], at_basis=True).splitlines()[ka - 1:kb_]
            rows_ok = bool(kwl) and all(re.match(r"^\d+\s+m2_region_", l) for l in kwl)
            ids = set(re.findall(r"m2_region_\d{5}(?:__sub\d+)?", "\n".join(kwl)))
            cnt_ok = rows_ok and len(ids) == kst == n1
        src_ok = src_ok and cnt_ok
        out.append(("c-hand:H6", n1 == 6 and n2 == 21 and abs(calc - st_h) < 0.06 and src_ok,
                    "RUN1 %d regions / 1h53m; RUN2 %d regions / 2h40m46s = 9646 s; 9646 x %d/%d = "
                    "%.2f h, stated ~%.1f h; source records carry the strings: %s"
                    % (n1, n2, st_n, n2, calc, st_h, src_ok)))

    # H7 — X2's scratch size
    msz = need("scratch")
    if not msz:
        out.append(("c-hand:H7", False, "the scratch-size sentence did not parse"))
    else:
        gb = float(msz.group(1)); ceil = int(msz.group(2).replace(",", ""))
        calc = ceil * ceil * 4 / 1e9
        out.append(("c-hand:H7", abs(calc - gb) < 0.05,
                    "%d^2 x 4 B = %.1f GB, stated %.1f GB" % (ceil, calc, gb)))

    # H3 — the DRAFTED — NOT POSTED entry, found by HEADING SEARCH, and OD citation containment
    od = reader.lines(PATHS["OD"])
    heads = [i + 1 for i, l in enumerate(od) if l.startswith(H3_HEADING)]
    me = need("entry")
    stated_line = int(me.group(1)) if me else None
    ends = [h for h in
            [i + 1 for i, l in enumerate(od) if l.startswith("## ")] if heads and h > heads[0]]
    entry_end = (ends[0] - 1) if ends else len(od)
    status_ok = any(l.startswith(H3_STATUS) for l in od[heads[0] - 1:entry_end]) if heads else False
    cites = resolve(parse_citations(draft), keymap_of(parse_key(draft)))
    od_c = [c for c in cites if c.get("resolved") == PATHS["OD"]]
    outside = [c["text"] for c in od_c
               if heads and not (heads[0] <= c["rng"][0] and c["rng"][1] <= entry_end)]
    out.append(("c-hand:H3", len(heads) == 1 and heads[0] == H3_LINE
                and stated_line == H3_LINE and status_ok and not outside,
                "heading search %r -> %s (constant %d); draft states %s; %r inside the entry: %s; "
                "entry spans :%s-:%s; %d OD citation(s), outside the entry: %s"
                % (H3_HEADING, heads, H3_LINE, stated_line, H3_STATUS, status_ok,
                   heads[0] if heads else "?", entry_end, len(od_c), outside or "none")))

    # H4 — the repo draft is NOT the posted body (md5 inequality, recomputed)
    u7 = md5(reader.raw(PATHS["U7"]))
    tr = md5(reader.raw(PATHS["TR"]))
    out.append(("c-hand:H4", u7 != tr and tr == TR_MD5,
                "U7 md5 %s != trsx5 md5 %s" % (u7, tr)))

    # H5 — the basis statement
    out.append(("c-hand:H5", BASIS in draft,
                "draft states the full 40-char BASIS %s" % BASIS))
    return out


# ============================================================================================
# d: — the "what the posted text does NOT say" sweep, RECOMPUTED
# ============================================================================================
D_TERMS = ["halt", "abort", "skip", "partial", "incomplete", "feasib"]
D_RE = (r"`defer` has (\d+) hits in mk7ze and (\d+) in\s+trsx5; `raise` has (\d+) and (\d+)")


def check_sweep(draft, reader):
    out = []
    mkp = "\n".join(mk_posted_lines(reader.raw(PATHS["MK"])))
    trp = reader.text(PATHS["TR"])
    nm, nt = norm(mkp), norm(trp)
    bad = ["%s(mk=%d,tr=%d)" % (t, nm.count(t), nt.count(t))
           for t in D_TERMS if nm.count(t) or nt.count(t)]
    stated = [t for t in D_TERMS if ("`%s`" % t) in draft]
    out.append(("d:zero", not bad and len(stated) == len(D_TERMS),
                "%d terms 0 hits in BOTH posted bodies; draft names %d/%d%s"
                % (len(D_TERMS) - len(bad), len(stated), len(D_TERMS),
                   ("; NON-ZERO: " + ", ".join(bad)) if bad else "")))
    m = re.search(D_RE, draft)
    if not m:
        out.append(("d:control", False, "the control sentence did not parse"))
    else:
        want = (nm.count("defer"), nt.count("defer"), nm.count("raise"), nt.count("raise"))
        got = tuple(int(x) for x in m.groups())
        out.append(("d:control", want == got and all(v > 0 for v in want),
                    "measured defer mk=%d tr=%d, raise mk=%d tr=%d; draft states %s "
                    "(a zero control would prove nothing)" % (want + (got,))))
    raw = nm.count("deferred_infeasible_square") + nt.count("deferred_infeasible_square")
    strip = nm.count("deferredinfeasiblesquare") + nt.count("deferredinfeasiblesquare")
    out.append(("d:dis", raw == 0 and strip == 0,
                "deferred_infeasible_square absent from both posted bodies: raw %d hits, "
                "underscore-stripped %d hits (norm() deletes `_`, so a raw-only search would be "
                "green over nothing)" % (raw, strip)))
    return out


# ============================================================================================
# e: — the fire-path freeze, with a NON-EMPTY control window
# ============================================================================================
def check_git(ref, since=None, since_control=None):
    out = []
    SINCE_, SINCE_CONTROL_ = since or SINCE, since_control or SINCE_CONTROL
    r = git("log", "--since=" + SINCE_, "--format=%H", ref, "--", *FROZEN_FILES)
    n = len([x for x in r.stdout.decode().split() if x])
    out.append(("e:frozen", n == 0,
                "%d commit(s) touching the 3 fire-path files since %s at %s" % (n, SINCE_, ref[:7])))
    rc = git("log", "--since=" + SINCE_CONTROL_, "--format=%H", ref, "--", *FROZEN_FILES)
    nc = len([x for x in rc.stdout.decode().split() if x])
    out.append(("e:control", nc >= 1,
                "%d commit(s) since the control window %s (an EMPTY control proves nothing)"
                % (nc, SINCE_CONTROL_)))
    rn = git("log", "-1", "--format=%H", ref, "--", *FROZEN_FILES)
    newest = rn.stdout.decode().strip()
    out.append(("e:newest", newest == NEWEST_TOUCH,
                "newest commit touching them: %s (want %s)" % (newest[:12], NEWEST_TOUCH[:12])))
    return out


# ============================================================================================
# c-halt: — no claim range may land in a passage quick-260916-ocb FALSIFIED
# ============================================================================================
def halt_ranges(reader):
    """Locate the falsified passages BY CONTENT at BASIS. Every anchor is asserted UNIQUE first."""
    lines = reader.lines(PATHS["HA"])
    nl = [norm(l) for l in lines]
    ann = [i + 1 for i, l in enumerate(lines) if HALT_ANNOTATION in l]
    pos, probs = {}, []
    for k, a in sorted(HALT_ANCHORS.items()):
        na = norm(a)
        hits = [i + 1 for i, l in enumerate(nl) if na in l]
        if len(hits) != 1:
            probs.append("anchor %s hit %d times %s (must be UNIQUE)" % (k, len(hits), hits[:5]))
        else:
            pos[k] = hits[0]
    for k, want in sorted(HALT_REJECTED.items()):
        got = len([1 for l in nl if norm(k) in l])
        if got < 2:
            probs.append("REJECTED anchor %r now hits %d times (it was rejected as ambiguous at %d)"
                         % (k, got, want))
    if probs or len(pos) != len(HALT_ANCHORS):
        return None, ann, probs
    f1 = (pos["H1-meas"] - 1, pos["H1-end"] + 1)
    f2 = (pos["H2"], pos["H2"])
    return [f1, f2], ann, probs


def check_halt(draft, reader):
    out = []
    rngs, ann, probs = halt_ranges(reader)
    out.append(("c-halt:annot", len(ann) == 1 and not probs,
                "%r present at %s; anchor uniqueness: %s"
                % (HALT_ANNOTATION, ann, "; ".join(probs) if probs else "all UNIQUE")))
    if rngs is None:
        out.append(("c-halt:disjoint", False, "forbidden ranges not derivable: %s" % "; ".join(probs)))
        return out
    cites = resolve(parse_citations(draft), keymap_of(parse_key(draft)))
    ha = [c for c in cites if c.get("resolved") == PATHS["HA"]]
    bad = []
    for c in ha:
        a, b = c["rng"]
        for (x, y) in rngs:
            if a <= y and x <= b:
                bad.append("%s overlaps :%d-%d" % (c["text"], x, y))
    out.append(("c-halt:disjoint", not bad,
                "forbidden (FALSIFIED) ranges at BASIS: %s; %d citation(s) into the halt record: %s%s"
                % (rngs, len(ha), [c["rng"] for c in ha],
                   ("; OVERLAP: " + "; ".join(bad)) if bad else "; all DISJOINT")))
    return out


# ============================================================================================
# imm: — v1 and the kht checker are byte-unchanged, in the TREE and at BASIS
# ============================================================================================
def check_imm(overrides=None):
    """`overrides` maps a repo-relative path to a file on disk. That is the ONLY negative control that
    proves anything here: showing a one-byte-altered copy hashes differently proves md5 is injective,
    not that THIS CHECK can fail."""
    overrides = dict(overrides or {})
    out = []
    for tag, rel, size, nlines, want in (("v1", SOURCE_REL, SOURCE_SIZE, SOURCE_LINES, SOURCE_MD5),
                                         ("kht", KHT_REL, KHT_SIZE, KHT_LINES, KHT_MD5)):
        p = Path(overrides.get(rel, str(ROOT / rel)))
        b = p.read_bytes()
        szok = len(b) == size
        out.append(("imm:%s:size" % tag, szok, "%d B (want %d)" % (len(b), size)))
        if not szok:
            out.append(("imm:%s:md5" % tag, False, "SKIPPED after size failure"))
        else:
            h = md5(b)
            out.append(("imm:%s:md5" % tag, h == want, "%s (want %s)" % (h, want)))
        nl = len(b.decode("utf-8", "replace").splitlines())
        out.append(("imm:%s:lines" % tag, nl == nlines, "%d lines (want %d)" % (nl, nlines)))
        if rel in overrides:
            out.append(("imm:%s:basis" % tag, False,
                        "OVERRIDDEN path %s — not the tracked file" % p))
        else:
            r = git("diff", "--quiet", BASIS, "--", rel)
            out.append(("imm:%s:basis" % tag, r.returncode == 0,
                        "git diff --quiet %s -- %s rc=%d" % (BASIS_SHORT, rel, r.returncode)))
    return out


# ============================================================================================
# sup: — the supersession block, and its BRIEF-BLIND SAFETY
# ============================================================================================
_DIGIT_WORDS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")


def sup_sentence(draft):
    for ln in draft.split("\n"):
        if "SUPERSEDES" in ln:
            return ln
    return None


def check_sup(draft):
    out = []
    s = sup_sentence(draft)
    out.append(("sup:names", bool(s) and SOURCE_REL in (s or ""),
                "supersession line names v1's repo-relative path"
                if s else "no line containing SUPERSEDES"))
    r = git("diff", "--name-only", BASIS, "HEAD")
    changed = [x for x in r.stdout.decode().splitlines() if x]
    out.append(("sup:untouched", SOURCE_REL not in changed,
                "v1 is not in `git diff --name-only %s HEAD` (%d path(s))" % (BASIS_SHORT, len(changed))))
    if not s:
        out.append(("sup:noleak", False, "no supersession sentence to screen"))
        return out
    probs = []
    ns = norm(s)
    # strip the repo-relative path first: "…-DRAFT.md" carries no defect count, and its own digits
    # (260916) are a filename, not a quantity.
    scan = ns.replace(norm(SOURCE_REL), " ")
    for w in _DIGIT_WORDS:
        if re.search(r"\b%s\b\s+(defect|issue|problem|finding|error|flaw)" % w, scan):
            probs.append("digit-word defect count %r" % w)
    if re.search(r"\b\d+\s+(defect|issue|problem|finding|error|flaw)", scan):
        probs.append("numeral defect count")
    for L in OPTION_LETTERS:
        if re.search(r"\boption %s\b" % L.lower(), scan):
            probs.append("names Option %s" % L)
    out.append(("sup:noleak", not probs,
                "supersession reason carries no defect count and no option letter"
                if not probs else "; ".join(probs)))
    return out


# ============================================================================================
# basis: — v2 is pinned to ONE commit, and c93e97b is quarantined
# ============================================================================================
def check_basis(draft):
    out = []
    out.append(("basis:stated", BASIS in draft, "v2 states the full 40-char SHA %s" % BASIS))
    r = git("merge-base", "--is-ancestor", BASIS, "HEAD")
    out.append(("basis:ancestor", r.returncode == 0,
                "merge-base --is-ancestor %s HEAD rc=%d" % (BASIS_SHORT, r.returncode)))
    lg = git("log", "--format=%H %s", BASIS)
    vqp = [l.split(" ", 1)[0] for l in lg.stdout.decode().splitlines()
           if l.split(" ", 1)[1:] and l.split(" ", 1)[1].startswith(VQP_PREFIX)]
    ok = bool(vqp) and git("merge-base", "--is-ancestor", vqp[0], BASIS).returncode == 0
    out.append(("basis:vqp", ok,
                "%d %s commit(s) reachable from BASIS; newest %s is an ancestor of BASIS: %s"
                % (len(vqp), VQP_PREFIX, vqp[0][:8] if vqp else "-", ok)))
    occ = [m.start() for m in re.finditer(re.escape(OLD_BASIS), draft)]
    s = sup_sentence(draft) or ""
    inside = all(draft[o:o + len(OLD_BASIS)] in s and OLD_BASIS in s for o in occ)
    # stricter: the occurrence's line must BE the supersession line
    lines, pos, linefor = draft.split("\n"), 0, []
    for ln in lines:
        linefor.append((pos, pos + len(ln)))
        pos += len(ln) + 1
    ok2 = True
    for o in occ:
        ln = next(l for (a, b), l in zip(linefor, lines) if a <= o <= b)
        if "SUPERSEDES" not in ln and "quick-260916-kht" not in ln:
            ok2 = False
    out.append(("basis:quarantine", len(occ) <= 1 and ok2,
                "%r occurs %d time(s) in v2, only on the supersession line" % (OLD_BASIS, len(occ))))
    out.append(("basis:branch", BRANCH in draft, "v2 names the branch %s" % BRANCH))
    return out


# ============================================================================================
# S-1: the COUNTING CONTRACT, declared in the PLAN before a word of v2 existed.
#   option span = the `### Option X: …` heading line through the line before the next `###` heading
#                 or before `## 4.`, whichever comes first
#   bal:words and bal:eval both score HEADING + BODY (v1's surviving cue lived in a HEADING)
#   tokenization = Python str.split() on the raw span, no markdown stripping
#   the LOW subsection, the Files-cited key, the anchors block and the §1/§2 tables are EXCLUDED
# Every bal: check PRINTS its spans and its per-unit numbers: a number without its span is not evidence.
# ============================================================================================
OPT_HEAD = re.compile(r"^### Option ([A-F]):")
READ_RE = re.compile(r"\*READING")
SUBFIELD_RE = {f: re.compile(re.escape("**" + f + "**")) for f in SUBFIELDS}


def option_units(draft):
    lines = draft.split("\n")
    stops = [i + 1 for i, l in enumerate(lines) if l.startswith("### ") or l.startswith("## 4.")]
    units = {}
    for i, l in enumerate(lines):
        m = OPT_HEAD.match(l)
        if not m:
            continue
        ln = i + 1
        nxt = [s for s in stops if s > ln]
        end = (nxt[0] - 1) if nxt else len(lines)
        units[m.group(1)] = {"letter": m.group(1), "start": ln, "end": end,
                             "heading": l, "lines": lines[ln - 1:end]}
    return units


def section_lines(draft, prefix):
    lines = draft.split("\n")
    start = None
    for i, l in enumerate(lines):
        if l.startswith(prefix):
            start = i
            break
    if start is None:
        return None, None, []
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return start + 1, end, lines[start:end]


def readings_of(u):
    lines = u["lines"]
    idx_read = [i for i, l in enumerate(lines) if READ_RE.search(l)]
    idx_field = [i for i, l in enumerate(lines) if any(r.search(l) for r in SUBFIELD_RE.values())]
    terms = sorted(set(idx_read + idx_field))
    out = []
    for i in idx_read:
        after = [t for t in terms if t > i]
        end = after[0] if after else len(lines)
        lab = re.search(r"\*READING[^*]*\*", lines[i])
        out.append({"label": lab.group(0) if lab else lines[i].strip()[:26],
                    "a": u["start"] + i, "b": u["start"] + end - 1,
                    "words": len(" ".join(lines[i:end]).split())})
    return out


def eval_hits(text):
    """Declared EVAL_CUES over `text`. Single words on word boundaries, multi-word cues as
    normalized substrings. Returns [(cue, [line numbers])]."""
    lines = text.split("\n")
    hits = []
    for c in EVAL_CUES:
        n = norm(c)
        where = []
        for i, l in enumerate(lines, 1):
            nl = norm(l)
            if " " in n:
                if n in nl:
                    where.append(i)
            elif re.search(r"\b%s\b" % re.escape(n), nl):
                where.append(i)
        if where:
            hits.append((c, where))
    return hits


def check_balance(draft):
    """Seven checks. No option may be pre-favoured by EMPHASIS, at the option level AND within it."""
    out = []
    U = option_units(draft)
    letters = sorted(U)

    # ---- bal:fields -------------------------------------------------------------------------
    fields = {}
    for L in letters:
        txt = "\n".join(U[L]["lines"])
        fields[L] = [f for f in SUBFIELDS if SUBFIELD_RE[f].search(txt)]
    sets = set(tuple(v) for v in fields.values())
    out.append(("bal:fields", letters == OPTION_LETTERS and len(sets) == 1
                and list(sets)[0] == tuple(SUBFIELDS),
                "options %s; per-option labelled sub-fields: %s"
                % (letters, "; ".join("%s=%s" % (L, fields[L]) for L in letters))))

    # ---- bal:reading (+ A-3: the vacuity guard) ----------------------------------------------
    R = {L: readings_of(U[L]) for L in letters}
    counts = {L: len(R[L]) for L in letters}
    vals = list(counts.values()) or [0]
    spread_ok = (max(vals) - min(vals)) <= 1 and min(vals) >= 1
    multi = sorted([L for L in letters if counts[L] >= 2])
    # A-3: S-2's claim that bal:reading makes a single-READING option RED is FALSE — if EVERY option
    # carries exactly one, min == max == 1, the spread is 0 and bal:readweight has nothing to compare.
    vac_ok = bool(multi) and counts.get("B", 0) >= 2
    out.append(("bal:reading", spread_ok and vac_ok,
                "per-option READING labels %s (spread %d, min %d); options with >= 2 READINGs "
                "(the set bal:readweight actually compares): %s; Option B has %d"
                % (counts, max(vals) - min(vals), min(vals), multi, counts.get("B", 0))))

    # ---- bal:readweight ----------------------------------------------------------------------
    probs, shown = [], []
    for L in letters:
        if len(R[L]) < 2:
            shown.append("%s: %s" % (L, [(r["label"], ":%d-%d" % (r["a"], r["b"]), r["words"])
                                         for r in R[L]]))
            continue
        w = [r["words"] for r in R[L]]
        ratio = max(w) * 1.0 / max(1, min(w))
        shown.append("%s: %s max/min=%d/%d=%.2f"
                     % (L, [(r["label"], ":%d-%d" % (r["a"], r["b"]), r["words"]) for r in R[L]],
                        max(w), min(w), ratio))
        if ratio > BAND_READWEIGHT:
            probs.append("%s %.2f > %.1f" % (L, ratio, BAND_READWEIGHT))
    out.append(("bal:readweight", not probs,
                "within-option READING weights (sub-bullets attributed to their READING) | "
                + " | ".join(shown) + ("  BREACH: " + ", ".join(probs) if probs else "")))

    # ---- bal:words ---------------------------------------------------------------------------
    wc, badspan = {}, []
    for L in letters:
        span = U[L]["lines"]
        wc[L] = len(" ".join(span).split())
        if any(re.search(r"\bLOW\b", l) for l in span):
            badspan.append("%s span contains the token LOW" % L)
        if any(l.lstrip().startswith("|") for l in span):
            badspan.append("%s span contains a table row" % L)
    v = list(wc.values()) or [0]
    ratio = max(v) * 1.0 / max(1, min(v))
    out.append(("bal:words", ratio <= BAND_WORDS and not badspan,
                "heading+body words (str.split(), raw span) %s | spans %s | max/min = %d/%d = %.2f "
                "(band <= %.1f)%s"
                % (wc, {L: ":%d-%d" % (U[L]["start"], U[L]["end"]) for L in letters},
                   max(v), min(v), ratio, BAND_WORDS,
                   ("; " + "; ".join(badspan)) if badspan else "")))

    # ---- bal:eval  (A-1: the WHOLE draft, not only the option units) --------------------------
    whole = eval_hits(draft)
    per = {L: [c for c, _ in eval_hits("\n".join(U[L]["lines"]))] for L in letters}
    out.append(("bal:eval", not whole,
                "declared EVAL_CUES over the WHOLE draft (§0/§4/§5/LOW included): %s | per-option: %s"
                % ("0 hits" if not whole else whole,
                   {L: per[L] for L in letters if per[L]} or "0 hits in every option unit")))

    # ---- bal:precedent -----------------------------------------------------------------------
    s4a, s4b, s4 = section_lines(draft, "## 4.")
    in4 = any(PRECEDENT_TOKEN in l for l in s4)
    fit = set(L for L in letters if any(PRECEDENT_TOKEN in l for l in U[L]["lines"]))
    qs = questions_of(draft)
    qidx = [i for i, q in enumerate(qs, 1) if PRECEDENT_TOKEN in q["text"]]
    place_ok = len(qidx) == 1 and qidx[0] != 1 and qidx[0] != len(qs)
    out.append(("bal:precedent", in4 and fit == PRECEDENT_SET and place_ok,
                "%s named in §4: %s; fitting set %s (declared %s); its §5 question is Q%s of %d "
                "(neither first nor last: %s)"
                % (PRECEDENT_TOKEN, in4, sorted(fit), sorted(PRECEDENT_SET),
                   qidx[0] if qidx else "-", len(qs), place_ok)))

    # ---- bal:questions -----------------------------------------------------------------------
    # Only the AUTHOR-TIME tag is read — never a regex over the question prose. §5's precedent
    # question contains the token `C7` (the CODE claim id); a naive option-letter matcher would
    # FALSE-MATCH Option C there and report C as interrogated when that question is about the
    # precedent. R4(vi)'s explicit tags are what make this gate real.
    union, qmap = set(), []
    for i, q in enumerate(qs, 1):
        union |= set(q["tags"])
        qmap.append("Q%d->%s" % (i, "".join(sorted(q["tags"])) or "UNTAGGED"))
    out.append(("bal:questions", union == set(OPTION_LETTERS) and all(q["tags"] for q in qs),
                "question -> option map: %s | union %s (want %s)"
                % (", ".join(qmap), sorted(union), OPTION_LETTERS)))
    return out


QTAG = re.compile(r"\(Options?\s+([A-F][^)]*)\)")


def questions_of(draft):
    a, b, s5 = section_lines(draft, "## 5.")
    out, cur = [], None
    for l in s5:
        m = re.match(r"^(\d+)\.\s", l)
        if m:
            if cur:
                out.append(cur)
            cur = {"n": int(m.group(1)), "text": l}
        elif cur is not None:
            cur["text"] += "\n" + l
    if cur:
        out.append(cur)
    for q in out:
        tags = set()
        for m in QTAG.finditer(q["text"]):
            tags |= set(re.findall(r"\b([A-F])\b", m.group(1)))
        q["tags"] = tags
    return out


# ============================================================================================
# g: — the LEXICAL neutrality screen (bal: is the STRUCTURAL one)
# ============================================================================================
def check_neutral(draft):
    out = []
    head = draft.split("\n\n")[1] if len(draft.split("\n\n")) > 1 else draft[:1200]
    want = ["DRAFT", "NOT sent to Seth", "NOT decided", "no decision made"]
    miss = [w for w in want if w not in draft[:2600]]
    out.append(("g:status", not miss, "status block carries %s%s"
                % (want, ("; MISSING %s" % miss) if miss else "")))
    n = draft.count(G_EXEMPT)
    out.append(("g:exempt", n == 1, "%r occurs %d time(s) (want exactly 1)" % (G_EXEMPT, n)))
    nd = norm(draft)
    ex = norm(G_EXEMPT)
    i = nd.find(ex)
    scan = (nd[:i] + " " + nd[i + len(ex):]) if i >= 0 else nd
    hits = []
    for p in G_PATTERNS:
        for m in re.finditer(p, scan):
            hits.append((p, m.group(0)))
    out.append(("g:recommend", not hits,
                "%d declared recommendation pattern(s) over the normalized draft with the single "
                "exemption removed%s" % (len(hits), ("" if not hits else ": %s" % hits[:6]))))
    U = option_units(draft)
    out.append(("g:options", sorted(U) == OPTION_LETTERS,
                "option set %s (want %s)" % (sorted(U), OPTION_LETTERS)))
    qs = questions_of(draft)
    nums = [q["n"] for q in qs]
    out.append(("g:questions", nums == list(range(1, len(nums) + 1)) and len(nums) >= 5,
                "§5 numbering %s (contiguous from 1)" % nums))
    return out


# ============================================================================================
# report: — INFO ONLY. Never a gate.
# A-7(iv): per-option citation density is deliberately NOT screened (it is factually determined);
# printing it lets a reader see the asymmetry without it becoming a target.
# ============================================================================================
def report_sweeps(draft):
    out = []
    U = option_units(draft)
    per = {L: len(parse_citations("\n".join(U[L]["lines"]))) for L in sorted(U)}
    out.append(("report:cites", None,
                "per-option citation counts (NOT a gate — see the module docstring): %s" % per))
    R = {L: len(readings_of(U[L])) for L in sorted(U)}
    out.append(("report:readings", None, "per-option READING label counts: %s" % R))
    a, b, low = section_lines(draft, "### LOW")
    out.append(("report:low", None,
                "LOW subsection at lines %s-%s, %d words (EXCLUDED from every bal: count)"
                % (a, b, len(" ".join(low).split()))))
    return out


# ============================================================================================
# f: — THE EDIT LEDGER.  v2 is v1 plus an ordered, declared list of replacements, and nothing else.
#   f:forward   E1..En applied to v1 reproduces v2's bytes
#   f:reverse   En..E1 applied to v2 reproduces v1's bytes (size THEN md5)  <- must-be-identity
#   f:unique    every `old` occurs EXACTLY once at its point of application, every `new` once in v2;
#               an edit that a LATER edit declares it `amends` is checked AS AMENDED (quick-260917-f68)
#   f:amends    every declared `amends` names an edit in the ledger (no dangling declaration)
#   f:evidence  every class-3 (citation correction) edit carries live before-RED / after-GREEN proof
#   f:t18       NAMED ENFORCER for the "T1-T8 are not renumbered" invariant (W10 / R7 i).
#               f: covers the file as a whole, but a claimed invariant needs its own named enforcer.
# ============================================================================================
_BARE_TOK = re.compile(r"`:\d+(?:-\d+)?`")
_EXPL_TOK = re.compile(r"`[^`\s:]*(?:\.|…)(?:md|py|txt|json):\d+(?:-\d+)?`")
_TROW = re.compile(r"^\| (T[1-8]) \|")


def apply_edits(text, edits, reverse=False):
    seq = list(reversed(edits)) if reverse else list(edits)
    for e in seq:
        a, b = (e["new"], e["old"]) if reverse else (e["old"], e["new"])
        n = text.count(a)
        if n != 1:
            raise VerifyError("edit %s: %r occurs %d time(s) (want exactly 1) in the %s direction"
                              % (e["id"], a[:60], n, "reverse" if reverse else "forward"))
        text = text.replace(a, b, 1)
    return text


def evidence_check(reader, ev, side):
    rng = ev[side]
    ok, msg = content_check(reader, ev["key"], tuple(rng), ev.get("kind", "T"),
                            ev["payload"], ev.get("nots", []),
                            tuple(ev["p" + side]) if ("p" + side) in ev else None)
    return ok, msg


def check_edits(banked_text, source_bytes, edits, claims, reader, have_source=False):
    out = []
    classes = sorted(set(e["cls"] for e in edits))
    bad = [e["id"] for e in edits
           if e["cls"] not in (1, 2, 3, 4) or not e.get("old") or not e.get("new")
           or not e.get("why")]
    out.append(("f:classes", not bad and bool(edits),
                "%d edits in classes %s%s" % (len(edits), classes,
                                              ("; MALFORMED %s" % bad) if bad else "")))
    src = source_bytes.decode("utf-8")
    try:
        fwd = apply_edits(src, edits)
        okf = fwd == banked_text
        msgf = ("forward E1..E%d on v1 reproduces v2 byte-for-byte" % len(edits)) if okf else \
               ("forward result differs from v2 (%d B vs %d B)" % (len(fwd.encode()), len(banked_text.encode())))
    except VerifyError as e:
        okf, msgf = False, str(e)
    out.append(("f:forward", okf, msgf))
    try:
        rev = apply_edits(banked_text, edits, reverse=True).encode("utf-8")
        szok = len(rev) == SOURCE_SIZE
        h = md5(rev) if szok else None
        okr = szok and h == SOURCE_MD5
        msgr = ("reverse En..E1 on v2 -> %d B (want %d)%s"
                % (len(rev), SOURCE_SIZE, ("" if not szok else ", md5 %s (want %s)" % (h, SOURCE_MD5))))
    except VerifyError as e:
        okr, msgr = False, str(e)
    out.append(("f:reverse", okr, msgr))
    for e in edits:
        amenders = [x for x in edits if x.get("amends") == e["id"]]
        if not amenders:
            n_new = banked_text.count(e["new"])
            out.append(("f:unique:" + e["id"], n_new == 1,
                        "cls%d `new` occurs %d time(s) in v2 (want 1)" % (e["cls"], n_new)))
            continue
        cur, probs = e["new"], []
        for x in amenders:
            k = cur.count(x["old"])
            if k != 1:
                probs.append("FALSE DECLARATION: %s `old` occurs %d time(s) in %s's `new`"
                             % (x["id"], k, e["id"]))
            else:
                cur = cur.replace(x["old"], x["new"], 1)
        n_new = banked_text.count(cur)
        out.append(("f:unique:" + e["id"], (not probs) and n_new == 1,
                    "cls%d `new` AS AMENDED by declared %s occurs %d time(s) in v2 (want 1)%s"
                    % (e["cls"], [x["id"] for x in amenders], n_new,
                       ("; " + "; ".join(probs)) if probs else "")))
    ids_ = set(e["id"] for e in edits)
    dang = [(e["id"], e["amends"]) for e in edits if e.get("amends") and e["amends"] not in ids_]
    out.append(("f:amends", not dang,
                "every `amends` names an edit in the ledger; dangling: %s" % (dang or "none")))
    for e in edits:
        if e["cls"] != 3:
            continue
        ev = e.get("evidence")
        if not ev:
            out.append(("f:evidence:" + e["id"], False, "class-3 edit with no evidence block"))
            continue
        b_ok, b_msg = evidence_check(reader, ev, "before")
        a_ok, a_msg = evidence_check(reader, ev, "after")
        out.append(("f:evidence:" + e["id"], (not b_ok) and a_ok,
                    "before %s:%s -> %s (want RED: %s) | after %s:%s -> %s"
                    % (ev["key"], ev["before"], "PASS" if b_ok else "RED", b_msg[:70] or "-",
                       ev["key"], ev["after"], "PASS" if a_ok else "RED")))
    bare = _BARE_TOK.findall(banked_text)
    planned = [e for e in edits if e.get("bare_ref")]
    out.append(("f:bareplan", all(e["bare_ref"] in banked_text for e in planned),
                "%d bare `:n` tokens in v2; %d declared bare-ref expansions, all present"
                % (len(bare), len(planned))))
    v1rows = [l for l in src.split("\n") if _TROW.match(l)]
    v2rows = [l for l in banked_text.split("\n") if _TROW.match(l)]
    out.append(("f:t18", len(v1rows) == 8 and v1rows == v2rows,
                "T1-T8 table rows: %d in v1, %d in v2, byte-identical: %s (T9 is APPENDED; "
                "renumbering would silently invalidate every §3/§4/§5 reference to T1-T8)"
                % (len(v1rows), len(v2rows), v1rows == v2rows)))
    return out


def bare_ref_plan(banked_text):
    cites = resolve(parse_citations(banked_text), keymap_of(parse_key(banked_text)))
    rows = []
    for c in cites:
        if c["kind"] != "bare":
            continue
        rel = c.get("resolved")
        key = next((k for k, v in PATHS.items() if v == rel), None)
        rows.append((c["text"], rel, "`%s:%d-%d`" % (SHORT.get(key, key or "?"),
                                                     c["rng"][0], c["rng"][1])))
    return rows


# ============================================================================================
# runner / summarize
# ============================================================================================
class Ctx(object):
    def __init__(self, draft_path=None, live=False, overrides=None, source=None,
                 claims=None, edits=None, basis=None):
        self.draft_path = draft_path or str(ROOT / BANKED_REL)
        self.live = live
        self.overrides = dict(overrides or {})
        self.source = source
        self.claims = claims if claims is not None else build_claims()
        self.edits = edits if edits is not None else PERMITTED_EDITS
        self.reader = Reader(live=live, overrides=self.overrides, basis=basis)
        self.ref = "HEAD" if live else BASIS
        self.draft = Path(self.draft_path).read_text()


def _guard(fam, fn):
    try:
        r = fn()
        return r if isinstance(r, list) else [r]
    except Exception as e:
        return [(fam, False, "EXC %s: %s" % (type(e).__name__, e))]


# ============================================================================================
# lk: — the brief-blind LEAK screen (quick-260917-f68).
#   Markers are stored ONLY as sha256 digests of their normalized word n-grams (lower-case
#   [A-Za-z0-9]+ runs joined by one space), so this file discloses no content. Every lk: message
#   prints COUNTS only: never a phrase, never a line number, never a context window.
# ============================================================================================
MARKER_DIGESTS = (
    (3, "b5160ce5da19ee3df632263c152bc2ae5e093d282ad00e35bdd44821af1bccc6"),
    (2, "45032ce437619f482fc629292f6623def42765984dfcd1468e8119e7731dc884"),
    (3, "d2fb4a03852c37a5f2a9a5392f9443060b8bbc575bb130e04010020d792c0028"),
    (5, "3cd9cd553d93c8dbf5065ee82aef9d8b931a09d96a60a54d6020bec5312395ae"),
)
CHECKER_DIR_REL = ".planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-"
_MK_TOKEN = re.compile(r"[A-Za-z0-9]+")


def checker_dir():
    return ROOT / CHECKER_DIR_REL


def _marker_scan(text, digests=None):
    """(start, end, j) for every word n-gram whose sha256 equals declared digest j."""
    dg = MARKER_DIGESTS if digests is None else digests
    toks = [(m.start(), m.end(), m.group(0).lower()) for m in _MK_TOKEN.finditer(text)]
    out = []
    for n in sorted(set(k for k, _dg in dg)):
        want = {}
        for j, (k, h) in enumerate(dg):
            if k == n:
                want.setdefault(h, []).append(j)
        for i in range(len(toks) - n + 1):
            w = toks[i:i + n]
            h = hashlib.sha256(" ".join(t[2] for t in w).encode("utf-8")).hexdigest()
            for j in want.get(h, ()):
                out.append((w[0][0], w[-1][1], j))
    return sorted(out)


def marker_windows(text, digests=None):
    """Char spans (start, end) of every word n-gram whose sha256 is a declared marker digest."""
    return [(a, b) for a, b, _j in _marker_scan(text, digests)]


def marker_counts(text, digests=None):
    """Hit count per declared digest, in declared order."""
    dg = MARKER_DIGESTS if digests is None else digests
    per = [0] * len(dg)
    for _a, _b, j in _marker_scan(text, dg):
        per[j] += 1
    return per


def marker_hits(text, digests=None):
    return len(_marker_scan(text, digests))


def check_sibling(folder=None):
    """v2 sends its reviewers to this checker, so every file beside it is reviewer-visible."""
    folder = Path(folder) if folder is not None else checker_dir()
    files = sorted(p for p in folder.iterdir() if p.is_file())
    per = [marker_hits(p.read_text(encoding="utf-8", errors="replace")) for p in files]
    return [("lk:sibling", bool(files) and not any(per),
             "%d file(s) in the checker's own folder (working tree) screened; %d carry a marker hit; "
             "%d hit(s) in total" % (len(files), sum(1 for h in per if h), sum(per)))]


def check_leak(draft, claims, reader):
    """No STATE.md citation, key entry or mention (case-insensitive, markdown stripped); no declared
    marker in any cited record or in the draft."""
    out = []
    cites = parse_citations(draft)
    n_cite = sum(1 for c in cites
                 if c.get("file") is not None and norm(os.path.basename(c["file"])) == "state.md")
    out.append(("lk:state-cite", n_cite == 0,
                "%d citation token(s) into STATE.md (case-insensitive, markdown stripped)" % n_cite))
    key = parse_key(draft)
    n_key = sum(1 for s, f in (key["entries"] if key else [])
                if norm(s).endswith("state.md") or norm(f) == norm(PATHS["ST"]))
    out.append(("lk:state-key", bool(key) and n_key == 0,
                "%d Files-cited key entr(ies) naming STATE.md (case-insensitive)" % n_key))
    n_txt = norm(draft).count("state.md")
    out.append(("lk:state-text", n_txt == 0,
                "'state.md' occurs %d time(s) in the normalized draft (case-insensitive, markdown "
                "stripped)" % n_txt))
    fkeys = sorted(set(r[1] for r in claims))
    per = [marker_hits(reader.text(PATHS[k], at_basis=True)) for k in fkeys]
    out.append(("lk:private", not any(per),
                "%d cited record(s) screened at BASIS; %d carry a marker hit; %d hit(s) in total"
                % (len(fkeys), sum(1 for h in per if h), sum(per))))
    n_draft = marker_hits(draft)
    out.append(("lk:private-draft", n_draft == 0, "%d marker hit(s) in the draft" % n_draft))
    return out


def check_private_control(reader, digests=None):
    """The screen must be able to FIND each declared marker: every digest hits the control record at
    least once (a total >= 1 would let a dead digest pass unseen). Counts only; the record is not named."""
    per = marker_counts(reader.text(PATHS["ST"], at_basis=True), digests)
    each = bool(per) and all(c >= 1 for c in per)
    return [("lk:private-control", each,
             "control record at BASIS: %d marker hit(s) (each digest ≥1: %s)" % (sum(per), "yes" if each else "no"))]


def check_hj_basis(at_basis_keys=None):
    """W2: under --live a per-session ledger must still be read at BASIS, never from the tree."""
    rd = Reader(live=True, at_basis_keys=at_basis_keys)
    rd.raw(PATHS["HJ"])
    at_b, from_t = (PATHS["HJ"], False) in rd._cache, (PATHS["HJ"], True) in rd._cache
    return [("lk:hj-basis", at_b and not from_t,
             "Reader(live=True) cached HANDOFF.json with from_tree=False: %s; with from_tree=True: %s"
             % (at_b, from_t))]


def run_all(ctx, families=None):
    res = []
    want = (lambda f: True) if families is None else (lambda f: f in families)
    if want("imm"):
        res += _guard("imm:", lambda: check_imm(ctx.overrides))
    if want("basis"):
        res += _guard("basis:", lambda: check_basis(ctx.draft))
    if want("sup"):
        res += _guard("sup:", lambda: check_sup(ctx.draft))
    if want("a"):
        res += _guard("a:", lambda: check_anchor_mk(ctx.reader.raw(PATHS["MK"]), ctx.draft))
    if want("b"):
        res += _guard("b:", lambda: check_anchor_tr(ctx.reader.raw(PATHS["TR"]), ctx.draft))
    parsed = table = verified = cres = 0
    if want("c"):
        cr, cites = [], []
        try:
            cr, cites = check_citations(ctx.draft, ctx.claims, ctx.reader)
        except Exception as e:
            cr = [("c:ENGINE", False, "EXC %s: %s" % (type(e).__name__, e))]
        res += cr
        parsed, table = len(cites), len(ctx.claims)
        verified = sum(1 for (i, ok, _m) in cr if i.startswith("c:") and ok)
        cres = sum(1 for (i, _ok, _m) in cr if i.startswith("c-res:"))
    if want("c-ast"):
        res += _guard("c-ast:", lambda: check_ast(ctx.reader))
    if want("c-hand"):
        res += _guard("c-hand:", lambda: check_hand(ctx.draft, ctx.reader))
    if want("d"):
        res += _guard("d:", lambda: check_sweep(ctx.draft, ctx.reader))
    if want("e"):
        res += _guard("e:", lambda: check_git(ctx.ref))
    if want("c-halt"):
        res += _guard("c-halt:", lambda: check_halt(ctx.draft, ctx.reader))
    if want("f"):
        srcb = (Path(ctx.source).read_bytes() if ctx.source
                else ctx.reader.raw(SOURCE_REL, at_basis=True))
        res += _guard("f:", lambda: check_edits(ctx.draft, srcb, ctx.edits, ctx.claims,
                                                ctx.reader, bool(ctx.source)))
    if want("g"):
        res += _guard("g:", lambda: check_neutral(ctx.draft))
    if want("bal"):
        res += _guard("bal:", lambda: check_balance(ctx.draft))
    if want("lk"):
        res += _guard("lk:", lambda: (check_sibling() + check_leak(ctx.draft, ctx.claims, ctx.reader)
                                      + check_private_control(ctx.reader) + check_hj_basis()))
    if want("report"):
        res += _guard("report:", lambda: report_sweeps(ctx.draft))
    return res, parsed, table, verified, cres


def fmt(r):
    i, ok, m = r
    tag = "INFO" if ok is None else ("PASS" if ok else "RED ")
    return "%s %-22s :: %s" % (tag, i, m)


def summarize(res, parsed, table, verified, cres, baseline=False):
    ids = [r[0] for r in res]
    dup = sorted(set(i for i in ids if ids.count(i) > 1))
    reds = [r[0] for r in res if r[1] is False]
    counted = sum(1 for r in res if r[1] is not None)
    green = (not reds) and (not dup)
    if not baseline:
        green = green and (parsed == table == verified == cres) and parsed > 0
    return green, reds, dup, counted


# ============================================================================================
# --baseline: run the citation engine against v1 AT BASIS and reconcile BY SET EQUALITY
# A count can hide two opposite-sign component errors; a set cannot.
# ============================================================================================
def baseline_reds(draft, reader):
    res, cites = check_citations(draft, CLAIMS_V1, reader)
    reds = sorted(set(i.split(":", 1)[1] for (i, ok, _m) in res
                      if i.startswith("c:") and ok is False))
    return res, cites, reds


def reconcile(got, expected):
    g, e = set(got), set(expected)
    only_g, only_e = sorted(g - e), sorted(e - g)
    ok = not only_g and not only_e
    line = ("baseline-set-equal=%s measured=%d expected=%d symmetric_difference=%s"
            % ("YES" if ok else "NO", len(g), len(e),
               "EMPTY" if ok else ("only-measured=%s only-expected=%s" % (only_g, only_e))))
    return ok, line


# ============================================================================================
# --selftest: a GREEN is evidence ONLY because the engine has been SEEN to fail.
# Every mutation is proven to have changed something; a mutation whose anchor is not unique, or that
# changes nothing, is a selftest ERROR — never a pass.
# ============================================================================================
def _tmpdir():
    td = os.environ.get("TMPDIR")
    if not td:
        raise VerifyError("TMPDIR is unset — refusing to run --selftest (mutations must live "
                          "OUTSIDE the repo, and a fixed name under a shared $TMPDIR collides)")
    d = tempfile.mkdtemp(dir=td, prefix="vqq-selftest-")
    if inside_root(d):
        raise VerifyError("tempdir %s is INSIDE the repo" % d)
    return d


def mut(text, old, new):
    n = text.count(old)
    if n != 1:
        raise VerifyError("mutation anchor %r occurs %d time(s) (want exactly 1)" % (old[:60], n))
    out = text.replace(old, new, 1)
    if out == text:
        raise VerifyError("mutation %r -> %r changed nothing" % (old[:40], new[:40]))
    return out


def _w(d, name, data):
    p = os.path.join(d, name)
    with open(p, "wb") as fh:
        fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return p


def selftest(args):
    log = []
    print("SELFTEST tempdir policy: mkdtemp under $TMPDIR, asserted OUTSIDE the repo; no working-tree "
          "file is ever mutated (every corruption is delivered through Reader.overrides).")
    d = _tmpdir()
    try:
        # ---- (1) POSITIVE CONTROL on the real inputs --------------------------------------
        ctx0 = Ctx()
        res0, p0, t0, v0, c0 = run_all(ctx0)
        g0, reds0, dup0, n0 = summarize(res0, p0, t0, v0, c0)
        print("SELFTEST positive-control RESULT %s checks=%d parsed=%d table=%d verified=%d%s"
              % ("GREEN" if g0 else "RED", n0, p0, t0, v0,
                 "" if g0 else "  reds=%s dup=%s" % (reds0[:8], dup0)))
        if not g0:
            print("SELFTEST ABORTED: the positive control is RED. A mutation observed against a "
                  "already-red baseline proves nothing.")
            return 1
        D = ctx0.draft
        v1b = ctx0.reader.raw(SOURCE_REL, at_basis=True)
        mkb = ctx0.reader.raw(PATHS["MK"])
        trb = ctx0.reader.raw(PATHS["TR"])
        rn_src = ctx0.reader.text(PATHS["RN"])

        def C(text=None, overrides=None, claims=None, edits=None, name="m.md"):
            path = _w(d, name, text) if text is not None else ctx0.draft_path
            return Ctx(draft_path=path, overrides=overrides, claims=claims, edits=edits)

        def fam(ctx, families):
            r, _p, _t, _v, _c = run_all(ctx, families=families)
            return r

        M = []          # (label, expected RED id or prefix, callable -> results)

        # ---- a: / b: posted anchors ---------------------------------------------------------
        M.append(("a:size — one byte INSERTED inside the mk7ze extract (lines 168-500)", "a:size",
                  lambda: check_anchor_mk(_mk_mut(mkb, "size"), D)))
        M.append(("a:md5 — one byte FLIPPED inside the extract, size preserved", "a:md5",
                  lambda: check_anchor_mk(_mk_mut(mkb, "md5"), D)))
        M.append(("a:control — control range set EQUAL to the anchor range (a control that DOES match)",
                  "a:control", lambda: check_anchor_mk(mkb, D, ctrl=(MK_START, MK_END))))
        M.append(("b:size — trsx5 body truncated by 1 byte", "b:size",
                  lambda: check_anchor_tr(trb[:-1], D)))
        M.append(("b:md5 — one byte flipped inside trsx5, size preserved", "b:md5",
                  lambda: check_anchor_tr(_flip(trb, 4000), D)))
        M.append(("b:control — control length set to the FULL body (a control that DOES match)",
                  "b:control", lambda: check_anchor_tr(trb, D, ctrl_len=TR_SIZE)))
        M.append(("b:lines — a trailing newline appended (splitlines() count moves)", "b:lines",
                  lambda: check_anchor_tr(trb + b"\nx", D)))

        # ---- imm: OVERRIDDEN-PATH form (the only control that proves the CHECK can fail) -----
        alt_v1 = _w(d, "v1.md", _flip(v1b, 500))
        alt_kht = _w(d, "kht.py", _flip((ROOT / KHT_REL).read_bytes(), 5000))
        M.append(("imm:v1 — check run against an OVERRIDDEN path holding an altered copy",
                  "imm:v1:md5", lambda: check_imm({SOURCE_REL: alt_v1})))
        M.append(("imm:kht — check run against an OVERRIDDEN path holding an altered copy",
                  "imm:kht:md5", lambda: check_imm({KHT_REL: alt_kht})))

        # ---- c-*: the citation engine --------------------------------------------------------
        M.append(("c-key — a short form mapped to a non-file", "c-key",
                  lambda: fam(C(mut(D, "`run_native_ld_panel.py` → `src/python/run_native_ld_panel.py`",
                                    "`run_native_ld_panel.py` → `src/python/NOPE.py`")), {"c"})))
        M.append(("c-count — one citation token deleted", "c-count",
                  lambda: fam(C(mut(D, "(`plink_ld_to_npz.py:218-228`)", "(the converter)")), {"c"})))
        M.append(("c-res: — a citation re-pointed at another tracked file", "c-res:",
                  lambda: fam(C(mut(D, "`plink_ld_to_npz.py:218-228`",
                                    "`fire_verifier.py:218-228`")), {"c"})))
        M.append(("c: — a cited range moved off its payload", "c:",
                  lambda: fam(C(mut(D, "`plink_ld_to_npz.py:218-228`",
                                    "`plink_ld_to_npz.py:18-28`")), {"c"})))

        # ---- c-ast: a mutation a bare LINE-NUMBER anchor would have MISSED -------------------
        def ast_mut():
            old = "                gate_json = Path(f\"{out_prefix}.occlusion_gate.json\")"
            if old not in rn_src:
                raise VerifyError("c-ast mutation anchor absent")
            # De-indent the gate-sidecar upload OUT of the `if ok:` body while leaving it inside
            # process_region at almost the same line number. kht's line-number anchors (S5/S6) would
            # still "fall inside process_region" and stay green; AST containment does not.
            blk_old = ("                gate_json = Path(f\"{out_prefix}.occlusion_gate.json\")\n"
                       "                if gate_json.is_file():\n"
                       "                    _gsutil_upload(\n"
                       "                        gate_json,\n"
                       "                        _gs_join(gs_out_dir, f\"{region_id}.occlusion_gate.json\"),\n"
                       "                    )\n")
            blk_new = ("                pass\n"
                       "            gate_json = Path(f\"{out_prefix}.occlusion_gate.json\")\n"
                       "            if gate_json.is_file():\n"
                       "                _gsutil_upload(\n"
                       "                    gate_json,\n"
                       "                    _gs_join(gs_out_dir, f\"{region_id}.occlusion_gate.json\"),\n"
                       "                )\n")
            src2 = mut(rn_src, blk_old, blk_new)
            p = _w(d, "rn.py", src2)
            return check_ast(Reader(overrides={PATHS["RN"]: p}))
        M.append(("c-ast:A6 — the gate-sidecar upload moved OUT of the `if ok:` body "
                  "(a line-number anchor would have missed it)", "c-ast:A6", ast_mut))
        M.append(("c-ast:A4 — a status-vocabulary constant altered", "c-ast:A4",
                  lambda: check_ast(Reader(overrides={PATHS["FV"]: _w(
                      d, "fv.py", mut(ctx0.reader.text(PATHS["FV"]),
                                      '_FAILURE_PREFIXES = ("error:",)',
                                      '_FAILURE_PREFIXES = ("err:",)'))}))))

        # ---- c-hand: / d: / e: ----------------------------------------------------------------
        M.append(("c-hand:H1 — a stated scaled count altered by one", "c-hand:H1",
                  lambda: fam(C(mut(D, "that is ≈13 regions", "that is ≈14 regions")), {"c-hand"})))
        M.append(("c-hand:H6 — a stated region count altered by one", "c-hand:H6",
                  lambda: fam(C(mut(D, "6 regions in 1 h 53 m", "7 regions in 1 h 53 m")), {"c-hand"})))
        M.append(("d:control — a stated sweep count altered by one", "d:control",
                  lambda: fam(C(mut(D, "`defer` has 17 hits", "`defer` has 18 hits")), {"d"})))
        M.append(("d:zero — a 0-hit term replaced by one that DOES occur", "d:zero",
                  lambda: _sweep_with_term(ctx0, D, "defer")))
        M.append(("e:frozen — the SINCE window widened until the log is non-empty", "e:frozen",
                  lambda: check_git(BASIS, since=SINCE_CONTROL)))
        M.append(("e:control — the control window narrowed until it is EMPTY "
                  "(an empty control proves nothing)", "e:control",
                  lambda: check_git(BASIS, since_control=SINCE)))

        # ---- c-halt: in-range positive AND just-outside negative -----------------------------
        rngs, _ann, _p = halt_ranges(ctx0.reader)
        f1 = rngs[0]
        M.append(("c-halt: — a citation injected INTO a falsified range (:%d-%d)" % f1,
                  "c-halt:disjoint",
                  lambda: fam(C(mut(D, "(`260824-STAGE-B-HALT-…md:20-21`)",
                                    "(`260824-STAGE-B-HALT-…md:%d-%d`)" % f1)), {"c-halt"})))
        M.append(("c-halt: NEGATIVE CONTROL — a citation JUST OUTSIDE the falsified range "
                  "(:%d-%d) must stay GREEN" % (f1[0] - 2, f1[0] - 1), "__MUST_STAY_GREEN__",
                  lambda: fam(C(mut(D, "(`260824-STAGE-B-HALT-…md:20-21`)",
                                    "(`260824-STAGE-B-HALT-…md:%d-%d`)" % (f1[0] - 2, f1[0] - 1))),
                              {"c-halt"})))

        # ---- g: ------------------------------------------------------------------------------
        M.append(("g:recommend (plain) — \"We recommend Option B.\" injected", "g:recommend",
                  lambda: fam(C(mut(D, "## 5. Questions for the adjudicator",
                                    "We recommend Option B.\n\n## 5. Questions for the adjudicator")), {"g"})))
        M.append(("g:recommend (markdown-obfuscated) — `my **recom**mendation is Option A`",
                  "g:recommend",
                  lambda: fam(C(mut(D, "## 5. Questions for the adjudicator",
                                    "my **recom**mendation is Option A\n\n## 5. Questions for the adjudicator")),
                              {"g"})))
        M.append(("g:exempt — the single exemption phrase duplicated", "g:exempt",
                  lambda: fam(C(mut(D, "## 5. Questions for the adjudicator",
                                    "Laid out with no recommendation.\n\n## 5. Questions for the adjudicator")),
                              {"g"})))
        M.append(("g:status — the status block's \"no decision made\" removed", "g:status",
                  lambda: fam(C(mut(D, "**no decision made.**", "**nothing here.**")), {"g"})))
        M.append(("g:options — one option heading removed from the option set", "g:options",
                  lambda: fam(C(mut(D, "### Option F:", "#### Option F:")), {"g"})))
        M.append(("g:questions — §5 numbering made non-contiguous", "g:questions",
                  lambda: fam(C(mut(D, "\n2. ", "\n7. ")), {"g"})))

        # ---- sup: / basis: --------------------------------------------------------------------
        M.append(("sup:names — the SUPERSEDES sentence removed", "sup:names",
                  lambda: fam(C(mut(D, "SUPERSEDES", "replaces")), {"sup"})))
        M.append(("sup:noleak — a defect COUNT injected into the supersession sentence",
                  "sup:noleak",
                  lambda: fam(C(mut(D, "for couriering:", "for couriering: seven defects were found;")),
                              {"sup"})))
        M.append(("sup:noleak — an OPTION LETTER injected into the supersession sentence",
                  "sup:noleak",
                  lambda: fam(C(mut(D, "for couriering:", "for couriering: Option B was rewritten;")),
                              {"sup"})))
        M.append(("basis:stated — the stated BASIS SHA altered by one character", "basis:",
                  lambda: fam(C(mut(D, BASIS, BASIS[:-1] + ("0" if BASIS[-1] != "0" else "1"))),
                              {"basis"})))
        M.append(("basis:quarantine — a `c93e97b` occurrence injected OUTSIDE the supersession line",
                  "basis:quarantine",
                  lambda: fam(C(mut(D, "## 5. Questions for the adjudicator",
                                    "Read the code at c93e97b.\n\n## 5. Questions for the adjudicator")),
                              {"basis"})))
        # ---- lk: (quick-260917-f68). Markers are located BY HASH, never by a stored phrase, and every
        #      lk: mutation is matched on its EXACT result id (no prefix matching). ----------------------
        st_basis = ctx0.reader.text(PATHS["ST"], at_basis=True)
        st_win = marker_windows(st_basis)

        def _exact(res, cid, must=None):
            return [r for r in res if r[0] == cid and (must is None or must in r[2])]

        def _frag():
            if not st_win:
                raise VerifyError("the control record at BASIS carries no marker window to copy")
            a, b = st_win[0]
            return st_basis[a:b]

        def _sibling_reinserted():
            tmp = Path(d) / "lk-sibling"
            tmp.mkdir()
            files = sorted(p for p in checker_dir().iterdir() if p.is_file())
            for p in files:
                shutil.copyfile(str(p), str(tmp / p.name))
            victim = tmp / files[0].name
            victim.write_text(victim.read_text(encoding="utf-8", errors="replace")
                              + "\n" + _frag() + "\n", encoding="utf-8")
            return _exact(check_sibling(tmp), "lk:sibling")
        M.append(("lk:sibling — a marker window, found by hash in the control record at BASIS, re-inserted into a "
                  "temp copy of the checker's folder", "lk:sibling", _sibling_reinserted))
        M.append(("lk:state-cite — a STATE.md citation token (upper case)", "lk:state-cite",
                  lambda: _exact(fam(C(mut(D, "(`HANDOFF.json:142`)", "(`STATE.md:18`)")), {"lk"}),
                                 "lk:state-cite")))
        M.append(("lk:state-cite — a state.md citation token (lower case)", "lk:state-cite",
                  lambda: _exact(fam(C(mut(D, "(`HANDOFF.json:142`)", "(`state.md:18`)")), {"lk"}),
                                 "lk:state-cite")))
        M.append(("lk:state-key — a lower-case state.md Files-cited entry", "lk:state-key",
                  lambda: _exact(fam(C(mut(D, "- `HANDOFF.json` → `.planning/HANDOFF.json`\n",
                                           "- `HANDOFF.json` → `.planning/HANDOFF.json`\n"
                                           "- `state.md` → `.planning/state.md`\n")), {"lk"}),
                                 "lk:state-key")))
        M.append(("lk:state-text — STATE.md named in prose", "lk:state-text",
                  lambda: _exact(fam(C(mut(D, "## 1. What the posted text commits to",
                                           "See STATE.md.\n\n## 1. What the posted text commits to")),
                                     {"lk"}), "lk:state-text")))
        M.append(("lk:state-text — a markdown-obfuscated **State**.md:18 in prose", "lk:state-text",
                  lambda: _exact(fam(C(mut(D, "## 1. What the posted text commits to",
                                           "See **State**.md:18.\n\n## 1. What the posted text commits to")),
                                     {"lk"}), "lk:state-text")))
        M.append(("lk:private — a marker window (found by hash) copied into a cited record's override",
                  "lk:private",
                  lambda: _exact(fam(C(D, overrides={PATHS["KW"]: _w(
                      d, "lk-kw.md", ctx0.reader.text(PATHS["KW"], at_basis=True) + "\n" + _frag() + "\n")}),
                      {"lk"}), "lk:private")))
        M.append(("lk:private-draft — a marker window (found by hash) copied into the draft",
                  "lk:private-draft",
                  lambda: _exact(fam(C(mut(D, "## 1. What the posted text commits to",
                                           _frag() + "\n\n## 1. What the posted text commits to")),
                                     {"lk"}), "lk:private-draft")))

        def _st_windows_deleted():
            t = st_basis
            for _i in range(200):
                win = marker_windows(t)
                if not win:
                    break
                a, b = win[0]
                t = t[:a] + t[b:]
            if marker_windows(t):
                raise VerifyError("marker windows could not all be deleted from the control-record copy")
            return _exact(fam(C(D, overrides={PATHS["ST"]: _w(d, "lk-ctl.md", t)}), {"lk"}),
                          "lk:private-control")
        M.append(("lk:private-control — every marker window (found by hash) deleted from the control "
                  "record's override", "lk:private-control", _st_windows_deleted))

        def _one_digest_corrupted():
            dg = list(MARKER_DIGESTS)
            k, h = dg[-1]
            dg[-1] = (k, h[:-1] + ("0" if h[-1] != "0" else "1"))
            if sum(marker_counts(st_basis, tuple(dg))) < 1:
                raise VerifyError("corrupting one digest also zeroed the total: not a per-digest control")
            return _exact(check_private_control(ctx0.reader, digests=tuple(dg)), "lk:private-control")
        M.append(("lk:private-control — ONE declared digest corrupted (the total stays >= 1, so only the "
                  "per-digest rule can see it)", "lk:private-control", _one_digest_corrupted))
        M.append(("lk:hj-basis — HANDOFF.json dropped from the always-at-BASIS set, so --live reads it "
                  "from the working tree", "lk:hj-basis",
                  lambda: _exact(check_hj_basis(at_basis_keys=("ST",)), "lk:hj-basis")))
        M.append(("c-hand:H2 — HANDOFF.json's runtime altered in an override", "c-hand:H2",
                  lambda: _exact(fam(C(D, overrides={PATHS["HJ"]: _w(d, "lk-hj.json", mut(
                      ctx0.reader.text(PATHS["HJ"], at_basis=True), '"runtime": "48m', '"runtime": "58m'))}),
                      {"c-hand"}), "c-hand:H2")))
        M.append(("c-hand:H6 — a kw8 verdict row re-labelled so the distinct-region count drops to 5",
                  "c-hand:H6",
                  lambda: _exact(fam(C(D, overrides={PATHS["KW"]: _w(d, "lk-kw2.md", mut(
                      ctx0.reader.text(PATHS["KW"], at_basis=True), "14  m2_region_00149",
                      "14  m2_region_00062"))}), {"c-hand"}), "c-hand:H6")))
        M += _mut_bal(C, fam, D, ctx0, v1b)
        M += _mut_f(C, fam, D, ctx0, d)
        M += _mut_baseline(ctx0)
        return _finish(d, M, log)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _mk_mut(mkb, mode):
    """Mutate mk7ze INSIDE lines 168-500, so the mutation actually reaches the extract a: hashes."""
    ls = mkb.splitlines(keepends=True)
    pre, ext, post = b"".join(ls[:167]), b"".join(ls[167:500]), b"".join(ls[500:])
    if mode == "size":
        return pre + ext[:100] + b"X" + ext[100:] + post
    j = next(k for k in range(200, len(ext)) if 65 <= ext[k] <= 90 or 97 <= ext[k] <= 122)
    return pre + ext[:j] + bytes([ext[j] + 1]) + ext[j + 1:] + post


def _flip(b, i):
    ba = bytearray(b)
    ba[i] = (ba[i] + 1) % 128 or 65
    return bytes(ba)


def _sweep_with_term(ctx0, D, term):
    d2 = D.replace("`feasib`", "`%s`" % term, 1)
    global D_TERMS
    old = D_TERMS
    try:
        D_TERMS = [t if t != "feasib" else term for t in old]
        return check_sweep(d2, ctx0.reader)
    finally:
        D_TERMS = old


def _in_option(text, letter, old, new):
    """Mutate INSIDE one option unit, so a label that legitimately appears in all six options can
    still be a UNIQUE mutation anchor."""
    u = option_units(text)[letter]
    lines = text.split("\n")
    seg = "\n".join(lines[u["start"] - 1:u["end"]])
    n = seg.count(old)
    if n != 1:
        raise VerifyError("anchor %r occurs %d time(s) inside Option %s" % (old[:40], n, letter))
    seg2 = seg.replace(old, new, 1)
    if seg2 == seg:
        raise VerifyError("option mutation changed nothing")
    return "\n".join(lines[:u["start"] - 1] + seg2.split("\n") + lines[u["end"]:])


def _precedent_to(text, target):
    qs = questions_of(text)
    cur = next(i for i, q in enumerate(qs, 1) if PRECEDENT_TOKEN in q["text"])
    if cur == target:
        raise VerifyError("precedent question is already at slot %d" % target)
    t = mut(text, qs[cur - 1]["text"],
            qs[cur - 1]["text"].replace(PRECEDENT_TOKEN, "the registered precedent"))
    t = mut(t, qs[target - 1]["text"], qs[target - 1]["text"].rstrip() + " (%s)" % PRECEDENT_TOKEN)
    return t


FILLER = (" This sentence exists only to move a word count and carries no argument, no citation and "
          "no claim about any option or any posted record whatsoever, which is the point of it.") * 6


def _mut_bal(C, fam, D, ctx0, v1b):
    M = []
    M.append(("bal:fields — one option's labelled sub-field removed", "bal:fields",
              lambda: fam(C(_in_option(D, "E", "**Consequences:**", "**Outcome:**")), {"bal"})))
    M.append(("bal:reading — BOTH READING labels removed from one option (count 0, spread 2)",
              "bal:reading",
              lambda: fam(C(_in_option(_in_option(D, "C", "*READING 2:*", "*Point 2:*"),
                                       "C", "*READING 1:*", "*Point 1:*")), {"bal"})))
    M.append(("bal:reading (A-3 vacuity guard) — Option B's two READINGs collapsed into one",
              "bal:reading",
              lambda: fam(C(_in_option(D, "B", "*READING 2:*", "and further,")), {"bal"})))
    M.append(("bal:readweight — one READING inflated until the within-option 2.0 band breaks",
              "bal:readweight",
              lambda: fam(C(_in_option(D, "B", "*READING 1:*", "*READING 1:*" + FILLER)), {"bal"})))
    M.append(("bal:readweight — READING 1's supporting line RE-ATTRIBUTED to READING 2 "
              "(the v1 defect wearing a label)", "bal:readweight",
              lambda: fam(C(_shift_bullets(D, "D")), {"bal"})))
    M.append(("bal:words — one option unit padded until the 3.0 band breaks", "bal:words",
              lambda: fam(C(_in_option(D, "A", "**Consequences:**",
                                       "**Consequences:**" + FILLER * 3)), {"bal"})))
    M.append(("bal:eval — a declared cue injected into §0 (A-1: OUTSIDE any option unit)",
              "bal:eval",
              lambda: fam(C(mut(D, "## 1. What the posted text commits to",
                                "This is obviously the case.\n\n## 1. What the posted text commits to")),
                          {"bal"})))
    # --- the REAL-TEXT discrimination control (S-3). A synthetic injection alone is NOT sufficient:
    #     kht's inherited EVAL_WORDS list scores 0 hits on all five of v1's option bodies and would
    #     have passed a synthetic-only control while catching nothing real.
    def real_text_control():
        v1 = v1b.decode("utf-8")
        U = option_units(v1)
        out = []
        for L, expect in (("C", "already argues / argues against"),
                          ("E", "listed for completeness (in the HEADING)")):
            h = eval_hits("\n".join(U[L]["lines"]))
            out.append(("bal:eval", not h,
                        "v1 Option %s unit (:%d-%d) — expected %s; measured %s"
                        % (L, U[L]["start"], U[L]["end"], expect,
                           [(c, w) for c, w in h] or "NO HITS (the screen is NOT discriminating)")))
        return out
    M.append(("bal:eval REAL-TEXT control — v1's own Option C and Option E units at BASIS",
              "bal:eval", real_text_control))
    M.append(("bal:precedent — the precedent question moved to the LAST slot (recency)",
              "bal:precedent",
              lambda: fam(C(_precedent_to(D, len(questions_of(D)))), {"bal"})))
    M.append(("bal:precedent — the precedent question moved to the FIRST slot (primacy)",
              "bal:precedent", lambda: fam(C(_precedent_to(D, 1)), {"bal"})))
    M.append(("bal:precedent — the precedent named in a FOURTH option unit (set != {A,C,F})",
              "bal:precedent",
              lambda: fam(C(_in_option(D, "D", "**Consequences:**",
                                       "**Consequences:** (%s)" % PRECEDENT_TOKEN)), {"bal"})))
    M.append(("bal:questions — one option's tag removed from every question", "bal:questions",
              lambda: fam(C(_drop_tag(D, "E")), {"bal"})))
    return M


def _shift_bullets(text, letter):
    """Move the line immediately BEFORE the READING 2 label to just AFTER it, so words that were
    attributed to READING 1 are attributed to READING 2 instead. Nothing is added or deleted — only
    re-attributed. This is the v1 defect in miniature: the labels stay balanced, the weight does not."""
    u = option_units(text)[letter]
    lines = list(text.split("\n"))
    a, b = u["start"] - 1, u["end"]
    idx = None
    for i in range(a, b):
        if "*READING 2:*" in lines[i]:
            idx = i
            break
    if idx is None or idx - 1 <= a:
        raise VerifyError("no READING 2 with a preceding line in Option %s" % letter)
    moved = lines.pop(idx - 1)
    lines.insert(idx, moved)
    out = "\n".join(lines)
    if out == text:
        raise VerifyError("bullet shift changed nothing")
    return out


def _drop_tag(text, letter):
    out = text
    n = 0
    for q in questions_of(text):
        for m in QTAG.finditer(q["text"]):
            inner = m.group(1)
            if re.search(r"\b%s\b" % letter, inner):
                new = re.sub(r",?\s*\b%s\b" % letter, "", inner).strip().strip(",")
                out = out.replace(m.group(0), "(Options %s)" % new, 1)
                n += 1
    if not n:
        raise VerifyError("option %s is not tagged on any question" % letter)
    return out


def _mut_f(C, fam, D, ctx0, d):
    M = []
    M.append(("f:forward — a stray character appended to v2 outside the ledger", "f:forward",
              lambda: fam(C(D + "x"), {"f"})))
    M.append(("f:reverse — a character changed inside v2 outside the ledger", "f:reverse",
              lambda: fam(C(mut(D, "## 5. Questions for the adjudicator",
                                "## 5. Questions for the adjudicators")), {"f"})))
    if PERMITTED_EDITS:
        e0 = PERMITTED_EDITS[0]
        M.append(("f:unique:%s — the edit's `new` string duplicated in v2" % e0["id"],
                  "f:unique:%s" % e0["id"],
                  lambda: fam(C(D + "\n" + e0["new"] + "\n"), {"f"})))
        c3 = [e for e in PERMITTED_EDITS if e["cls"] == 3 and e.get("evidence")]
        if c3:
            def same_evidence():
                import copy
                ed = copy.deepcopy(PERMITTED_EDITS)
                tgt = next(e for e in ed if e["id"] == c3[0]["id"])
                tgt["evidence"]["before"] = list(tgt["evidence"]["after"])
                return fam(C(D, edits=ed), {"f"})
            M.append(("f:evidence:%s — a class-3 edit whose `after` equals its `before`"
                      % c3[0]["id"], "f:evidence:%s" % c3[0]["id"], same_evidence))
        br = [e for e in PERMITTED_EDITS if e.get("bare_ref")]
        if br:
            M.append(("f:bareplan — a declared bare-ref expansion removed from v2", "f:bareplan",
                      lambda: fam(C(D.replace(br[0]["bare_ref"], "REMOVED")), {"f"})))
    # ---- the declared-amends gate (quick-260917-f68): EXACT ids, edits located by `amends` ----------
    import copy as _copy
    am = [e for e in PERMITTED_EDITS if e.get("amends")]
    if am:
        def _ex(res, cid, must=None):
            return [r for r in res if r[0] == cid and (must is None or must in r[2])]

        def _gate_undeclared():
            ed = _copy.deepcopy(PERMITTED_EDITS)
            next(e for e in ed if e["id"] == am[0]["id"]).pop("amends")
            return _ex(fam(C(D, edits=ed), {"f"}), "f:unique:%s" % am[0]["amends"])
        M.append(("f:unique:%s — the `amends` declaration removed from %s (an UNDECLARED overwrite)"
                  % (am[0]["amends"], am[0]["id"]), "f:unique:%s" % am[0]["amends"], _gate_undeclared))
        xb = next(e for e in am if e["amends"] != "E7c")

        def _gate_false():
            ed = _copy.deepcopy(PERMITTED_EDITS)
            x = next(e for e in ed if e["id"] == xb["id"])
            if x["old"] in next(e for e in ed if e["id"] == "E7c")["new"]:
                raise VerifyError("the false declaration is not false: %s `old` is inside E7c's `new`" % x["id"])
            x["amends"] = "E7c"
            return _ex(fam(C(D, edits=ed), {"f"}), "f:unique:E7c", "FALSE DECLARATION")
        M.append(("f:unique:E7c — %s re-declared as amending E7c, whose `new` lacks its `old` (must print "
                  "FALSE DECLARATION)" % xb["id"], "f:unique:E7c", _gate_false))

        def _gate_dangling():
            ed = _copy.deepcopy(PERMITTED_EDITS)
            next(e for e in ed if not e.get("amends"))["amends"] = "E_NOT_IN_LEDGER"
            return _ex(fam(C(D, edits=ed), {"f"}), "f:amends")
        M.append(("f:amends — an `amends` naming an id that is not in the ledger", "f:amends",
                  _gate_dangling))
        M.append(("f:unique:E14 — v2 altered inside E14's amended text, outside every amender's `new`",
                  "f:unique:E14",
                  lambda: _ex(fam(C(mut(D, "The A–F labels are inherited", "The A–F labels are inheritted")),
                                  {"f"}), "f:unique:E14")))
    M.append(("f:t18 — a T1-T8 row altered (the NAMED enforcer for \"no renumbering\")", "f:t18",
              lambda: fam(C(_bump_trow(D)), {"f"})))
    return M


def _bump_trow(text):
    for l in text.split("\n"):
        if _TROW.match(l):
            return mut(text, l, l.replace("| T", "| t", 1))
    raise VerifyError("no T-row found")


def _mut_baseline(ctx0):
    def drop_one():
        got, _c, _r = None, None, None
        res, cites, reds = baseline_reds(ctx0.reader.text(SOURCE_REL, at_basis=True), ctx0.reader)
        shrunk = set(TASK1_MOVED_OR_FALSE)
        shrunk.discard(sorted(shrunk)[0])
        ok, line = reconcile(reds, shrunk)
        return [("baseline:setequal", ok, line)]
    return [("--baseline set equality — one id removed from the expected MOVED/FALSE set",
             "baseline:setequal", drop_one)]


def _finish(d, M, log):
    observed, total, notobs = 0, 0, []
    for label, expect, fn in M:
        total += 1
        try:
            res = fn()
        except Exception as e:
            print("SELFTEST ERROR   %-60s :: mutation failed: %s: %s"
                  % (label[:60], type(e).__name__, e))
            notobs.append(label)
            continue
        if expect == "__MUST_STAY_GREEN__":
            reds = [r for r in res if r[1] is False]
            if not reds:
                observed += 1
                print("SELFTEST OBSERVED negative-control-stays-GREEN -> %s" % label)
            else:
                notobs.append(label)
                print("SELFTEST NOT-OBSERVED %s -> the just-outside control went RED: %s"
                      % (label, [r[0] for r in reds]))
            continue
        hit = [r for r in res if r[1] is False and (r[0] == expect or r[0].startswith(expect))]
        if hit:
            observed += 1
            print("SELFTEST OBSERVED %s -> %s" % (hit[0][0], fmt(hit[0])[:190]))
        else:
            notobs.append(label)
            print("SELFTEST NOT-OBSERVED %s (expected %s); reds were %s"
                  % (label, expect, [r[0] for r in res if r[1] is False][:8]))
    print("SELFTEST families: %s" % sorted(set(e.split(":")[0] for _l, e, _f in M)))
    print("SELFTEST GREEN positive-control=GREEN observed=%d/%d" % (observed, total))
    if notobs:
        print("SELFTEST NOT-OBSERVED-LIST %s" % notobs)
    return 0 if observed == total else 1


# ============================================================================================
# CLI
# ============================================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--draft", default=None, help="draft to grade (default: v2 at %s)" % BANKED_REL)
    ap.add_argument("--live", action="store_true", help="read the working tree (ST stays at BASIS)")
    ap.add_argument("--source", default=None, help="v1 path; adds the forward identity check")
    ap.add_argument("--baseline", action="store_true",
                    help="run the citation families against v1 at BASIS and reconcile by SET EQUALITY")
    ap.add_argument("--bare-ref-plan", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", default=None, help="write results as JSON (REFUSED inside the repo)")
    args = ap.parse_args(argv)

    if args.json and inside_root(args.json):
        sys.stderr.write("REFUSED: --json %s is inside the repo (%s). This checker never writes "
                         "into the tree it grades.\n" % (args.json, ROOT))
        return 1

    if args.selftest:
        return selftest(args)

    if args.baseline:
        draft = args.draft or str(ROOT / SOURCE_REL)
        rd = Reader(live=args.live)
        text = Path(draft).read_text()
        res, cites, reds = baseline_reds(text, rd)
        for r in res:
            print(fmt(r))
        ok, line = reconcile(reds, TASK1_MOVED_OR_FALSE)
        print("BASELINE measured-RED-claim-ids: %s" % " ".join(reds))
        print("BASELINE expected (Task 1 hand re-derivation): %s"
              % " ".join(sorted(TASK1_MOVED_OR_FALSE)))
        print("BASELINE %s" % line)
        nred = len([r for r in res if r[1] is False])
        ncount = len([r for r in res if r[1] is not None])
        verified = sum(1 for (i, o, _m) in res if i.startswith("c:") and o)
        green = ok and nred == 0
        print("RESULT %s %d/%d checks RED over v1 at BASIS %s; parsed=%d table=%d verified=%d; "
              "baseline-set-equal=%s"
              % ("GREEN" if green else "RED", nred, ncount, BASIS_SHORT, len(cites),
                 len(CLAIMS_V1), verified, "YES" if ok else "NO"))
        # --baseline is EXPECTED RED (that is its job): it must independently find, on its own, the
        # exact set Task 1 found by hand. rc 0 iff the reconciliation succeeded.
        return 0 if ok else 1

    ctx = Ctx(draft_path=args.draft, live=args.live, source=args.source)

    if args.bare_ref_plan:
        rows = bare_ref_plan(ctx.draft)
        for tok, rel, exp in rows:
            print("BARE %-14s -> %-70s expand to %s" % (tok, rel, exp))
        print("BARE total=%d" % len(rows))
        return 0

    res, parsed, table, verified, cres = run_all(ctx)
    for r in res:
        print(fmt(r))
    green, reds, dup, counted = summarize(res, parsed, table, verified, cres)

    # <escape_hatch>: a declared band STOP is an acceptable close-out; a silently-widened band is not.
    for bid, band in (("bal:words", BAND_WORDS), ("bal:readweight", BAND_READWEIGHT)):
        for (i, ok, m) in res:
            if i == bid and ok is False:
                print("VQQ-BAND-STOP band=%s declared=%.1f measured-line=%s" % (bid, band, m))

    if args.json:
        payload = {"basis": BASIS, "draft": ctx.draft_path, "live": bool(args.live),
                   "green": green, "parsed": parsed, "table": table, "verified": verified,
                   "c_res": cres, "reds": reds, "duplicates": dup,
                   "results": [{"id": i, "status": ("INFO" if o is None else
                                                    ("PASS" if o else "RED")), "message": m}
                               for (i, o, m) in res]}
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
        print("JSON written to %s (outside the repo)" % args.json)

    print("RESULT %s checks=%d parsed=%d table=%d verified=%d c-res=%d%s%s"
          % ("GREEN" if green else "RED", counted, parsed, table, verified, cres,
             ("" if not reds else "  reds=%s" % reds[:12]),
             ("" if not dup else "  DUPLICATE-IDS=%s" % dup)))
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
