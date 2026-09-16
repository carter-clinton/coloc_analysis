#!/usr/bin/env python3
"""quick-260916-kht -- citation re-verifier for the banked Stage C NaN error-posture OPTIONS draft.

PURPOSE
  `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` goes BRIEF-BLIND to an
  external methodological adjudicator, and then Carter decides. Its citations are its
  load-bearing content: a wrong line number, a misquote or a stray recommendation sentence would
  mislead the adjudicator or leak our reasoning. Every citation is therefore re-verified
  MECHANICALLY here -- against the POSTED OSF texts (mk7ze = repo lines 168-500 of the 2026-08-20
  amendment; trsx5 = the byte-exact 9,695 B reconstruction) and against the shipped fire-path
  code -- never by eye.

BASIS = c93e97b, AND WHY
  Default mode reads every cited file with `git show c93e97b:<path>`. The citations were written
  against that immutable drafting basis, so default-mode verdicts are reproducible forever.
  `--live` asks a DIFFERENT question: are the citations still current in the working tree?
  A `--live` RED after a later edit to a cited file is the CORRECT outcome -- it means
  "re-verify (and if needed re-cite) the draft before it is sent". NEVER re-pin BASIS to make
  it green.

LIMITS -- read these before trusting a GREEN
  * (g) is a LEXICAL screen for recommendation language. It cannot prove neutrality; the
    brief-blind structure of the review is the real safeguard.
  * STATE.md (ST) is a living log and the draft cites a dated observation in it, so ST is ALWAYS
    read at BASIS, in every mode (including --live).
  * trsx5 TRAP: `wc -l` on the trsx5 file prints 58, but the file has 59 lines (it has no
    trailing newline) and the draft cites trsx5:59. Lines are counted with str.splitlines(),
    never with wc -l.
  * f:forward needs the scratchpad source (--source); f:reverse does not -- it is the permanent
    must-be-identity proof (undoing the permitted edits must give 16,817 B / md5 5e11157f...).
  * c-ast:S9 parts (iii) and (iv) are anchored on the AST-LOCATED `gate_sidecar = ...`
    assignment inside process_region (part (ii) pins that assignment to line 923), so an early
    return inserted directly before the sidecar write goes RED in part (iii) instead of slipping
    past a literal line number.
  * A GREEN is evidence only because `--selftest` has observed every check family RED on a
    deliberately corrupted input (33 mutations).

Stdlib only; Python 3.9 compatible; the only subprocess is `git` (cwd=ROOT, never shell=True);
nothing is imported from src/; no network.
"""
import argparse
import ast
import copy
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
assert (ROOT / ".git").exists(), "ROOT %s has no .git" % ROOT

BASIS = "c93e97b"
SOURCE_SIZE = 16817
SOURCE_MD5 = "5e11157f3b56addada24134bd7e2225f"
MK_START, MK_END, MK_SIZE, MK_MD5 = 168, 500, 22945, "13a49f543cabcc27ce9f1e589783c060"
TR_SIZE, TR_MD5 = 9695, "c19be8b2ad7cd6a45fee1d668d8a9cf9"
OFFSET = 167
SINCE = "2026-08-24 00:00:00 -0400"
SINCE_CONTROL = "2026-08-01 00:00:00 -0400"
MK_CONTROL = (167, 500)
MK_CONTROL_PREFIX = "8154025b"
TR_CONTROL_LEN = 9694
H2_MARKER = "PRIOR: 2026-09-01 — ✅ SWEEP COMPLETE"
H3_LINE = 532
S2_NAME = "process_region"

BANKED_REL = ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md"

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
    "TFV": "tests/m3/test_fire_verifier.py",
}
# short form written inside backticks when a bare `:n` ref is expanded (--bare-ref-plan)
SHORT = {
    "AP": "AGENT-PROMPT.md", "RF": "READY-TO-FIRE.md", "RN": "run_native_ld_panel.py",
    "FV": "fire_verifier.py", "PL": "plink_ld_to_npz.py", "OD": "osf_deviations.md",
    "HA": "260824-STAGE-B-HALT-…md", "DI": "deferred-items.md", "ST": "STATE.md",
}

# --------------------------------------------------------------------------------------------
# CLAIMS: positional, parsed reading order. (id, file key, kind Q|T, payload, NOT-tokens, edit)
# Payload strings are raw; they are normalized at check time.
# --------------------------------------------------------------------------------------------
CLAIMS = [
 ("c01","AP","T",["run_native_ld_panel.py","--mode square","--ancestry afr"],["--fail-fast"],None),  # `260812-ox1-AGENT-PROMPT.md:398`
 ("c02","AP","T",["without --fail-fast"],[],None),                      # `:372-373`
 ("c03","AP","T",["without --fail-fast"],[],None),                      # `:417`
 ("c04","RF","T",["the loop continues","partial bank"],[],None),        # `260812-ox1-READY-TO-FIRE.md:360-366`
 ("c05","RN","Q",["Stage C runs without --fail-fast"],[],None),         # `run_native_ld_panel.py:1325-1328`
 ("c06","PL","T",["raise ValueError","square LD carries NaN"],[],None), # `plink_ld_to_npz.py:218-228`
 ("c07","RN","T",["plink_ld_to_npz("],[],None),                         # `run_native_ld_panel.py:1090-1093`
 ("c08","RN","T",["except Exception","error: {e}"],[],None),            # `:1144-1146`
 ("c09","RN","T",["append_panel_row("],[],None),                        # `:1148`
 ("c10","RN","T",["if ok:","_gsutil_upload(out_npz"],[],None),          # `:1101-1107`
 ("c11","RN","T",["if fail_fast and",'!= "ok"',"RegionGateError"],[],None),  # `:1278-1279`
 ("c12","FV","T",["def _stage_c","classify_statuses"],[],None),         # `fire_verifier.py:1097-1099`
 ("c13","FV","T",["_FAILURE_STATUSES",'"error:"'],[],None),             # `:302-303`
 ("c14","FV","T",["_FAILURE_PREFIXES","STATUS_FAILURE"],[],None),       # `:324-326`
 ("c15","FV","Q",["Stage C runs without --fail-fast so the loop continues by design; report these to Carter … Do NOT re-fire blindly"],[],None),  # `:381-389`
 ("c16","FV","T",['"exit_code": 0 if not failed else 1'],[],None),      # `:976-981`
 ("c17","AP","T",["R8.","exit 1 means STOP and report"],[],None),       # `AGENT-PROMPT.md:55-61`
 ("c18","AP","T",["STOP under R8"],[],None),                            # `:422-423`
 ("c19","FV","T",["A RED IS A STOP"],[],None),                          # `fire_verifier.py:999-1001`
 ("c20","RN","T",["if fail_fast and",'!= "ok"'],[],None),               # `run_native_ld_panel.py:1278`
 ("c21","RN","T",['"skipped_idempotent"',"return result"],[],None),     # `:806-815`
 ("c22","HA","T",["m2_region_00001","m2_region_00017","m2_region_00040__sub14","all `ok`"],[],None),  # `260824-STAGE-B-HALT-…md:20-21`
 ("c23","RN","T",["Deferrals (deferred_infeasible_square","also halt"],[],None),  # `:1325-1328`  (EXPANDED in banked, E3)
 ("c24","HA","T",["m2_region_00057","read_square_bin","raised","square LD carries NaN"],[],None),  # `260824-STAGE-B-HALT-…md:11-16`
 ("c25","OD","T",["m2_region_00149","offset -1","single survivor"],[],None),  # `.planning/osf_deviations.md:657-663`
 ("c26","TR","Q",["The raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract."],[],None),  # trsx5:39
 ("c27","MK","T",["the raw-panel NaN-raise contract","continues to RAISE on any NaN"],[],None),  # mk7ze P321-322 / R488-489
 ("c28","TR","Q",["If the count of occlusion-excluded variants in a region exceeds … the region is … NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation."],[],None),  # trsx5:29
 ("c29","MK","Q",["Deferral remains NOT auto-exclusion. A region over the ceiling …"],[],None),  # mk7ze P261 / R428
 ("c30","MK","Q",["A region over the anomaly gate is deferred for re-diagnosis …"],[],None),  # mk7ze P311 / R478  (source: RED; banked P311-312 / R478-479, E6)
 ("c31","TR","Q",["the region's occlusion-exclusion count exceeds the anomaly gate"],[],None),  # trsx5:47
 ("c32","MK","Q",["NO fourth branch and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`"],[],None),  # mk7ze P316-318 / R483-485
 ("c33","MK","T",["DEFERRED when EITHER condition holds","n_occluded_sites","n_occluded_rows / n_occluded_sites"],[],None),  # mk7ze P155-158 / R322-325
 ("c34","TR","Q",["the region contains no occlusion-undefined pair; the panel and fine-mapping result stand unmodified."],[],None),  # trsx5:43
 ("c35","TR","Q",["… fine-mapping proceeds on the reduced variant set"],[],None),  # trsx5:45
 ("c36","TR","Q",["All three outcomes are reportable; excluding variants silently (without a manifest), fabricating a correlation value, or choosing the occlusion criterion to obtain a particular fine-mapping result are the only paths not on this list."],[],None),  # trsx5:49
 ("c37","TR","T",["deviations are logged in .planning/osf_deviations.md","disclosed in the manuscript"],[],None),  # trsx5:53
 ("c38","MK","T",["deviation logging",".planning/osf_deviations.md","disclosure in the manuscript"],[],None),  # mk7ze P323-324 / R490-491
 ("c39","TR","T",["Realized outcome branches","per-region exclusion manifest","present-rate","follow-up OSF update","closeout"],[],None),  # trsx5:59
 ("c40","MK","Q",["Every region computes its own occlusion count AND its own occluded-site inflation during the production run, so both complete distributions fold in at closeout"],[],None),  # mk7ze P247-250 / R414-417
 ("c41","TR","T",["correlation fabrication (NaN→0)","prohibited"],[],None),  # trsx5:25
 ("c42","MK","T",["correlation","fabrication (NaN→0) both remain prohibited"],[],None),  # mk7ze P307-308 / R474-475
 ("c43","TR","Q",["choosing the occlusion criterion to obtain a particular fine-mapping result"],[],None),  # trsx5:49
 ("c44","MK","Q",["choosing the occlusion criterion to obtain a particular fine-mapping result"],[],None),  # mk7ze P302-305 / R469-472
 ("c45","PL","T",["NaN check FIRST","zero-variance variant"],[],None),  # `plink_ld_to_npz.py:213-228`
 ("c46","HA","T",["FALSIFIED","nan_count == 1","diag == 1.0"],[],None),  # `260824-STAGE-B-HALT-…md:45-58`
 ("c47","RN","T",['result["n_dropped_occluded"] = n_dropped_occluded'],[],None),  # `:1068-1069`  (EXPANDED in banked, E4)
 ("c48","RN","T",["pln.plink_ld_to_npz("],[],None),                     # `:1090`
 ("c49","RN","T",['result["status"] = f"error: {e}"',"append_panel_row("],[],None),  # `run_native_ld_panel.py:1144-1148`
 ("c50","RN","T",["if ok:","_gsutil_upload(out_npz"],[],None),          # `:1101-1107`
 ("c51","RN","T",['if result["status"] == "ok":',"_reclaim_region_scratch("],[],None),  # `:1149-1154`
 ("c52","RN","Q",["~30+ GiB/region … overflows any finite scratch disk"],[],None),  # `:723-725`
 ("n01","RN","T",['"skipped_idempotent"',"return result"],[],"E8"),        # `run_native_ld_panel.py:806-815` (F1)
 ("n07","RN","T",["deferred_infeasible_square","return result"],[],"E8"),     # `:866-872` (F1, bare; resolves via n01)
 ("c53","RN","T",["occlusion_gate.json",'"occ_sites"','"n_sites"','"inflation"','"verdict"'],[],None),  # `:923-939`
 ("c54","RN","T",["_gsutil_upload(","gate_sidecar"],[],None),           # `:961-965`
 ("c55","RN","T",["gate_json","_gsutil_upload("],[],None),              # `:1129-1139`
 ("c56","RN","T",["SKIP guard","existing",'"skipped_idempotent"'],[],None),  # `:799-815`
 ("c57","FV","T",["def classify_statuses","THE GATES WORKING","FINDING","HARD_STOP","UNRECOGNIZED"],[],None),  # `fire_verifier.py:330-399`
 ("c58","FV","T",["test_shipped_status_vocabulary_is_covered_by_the_allow_list"],[],None),  # `:309-312`
 ("c59","RN","T",["deferred_infeasible_square","return result"],[],None),  # `run_native_ld_panel.py:866-872`
 ("c60","DI","Q",["a DISCLOSURE OBLIGATION — not blocking the fire"],[],None),  # `deferred-items.md:1148-1191`
 ("c61","FV","T",["def check_coverage_disclosure_resolved","R4-COVERAGE","deferred-items.md"],[],None),  # `fire_verifier.py:875-939`
 ("c62","RF","Q",["a real, reportable outcome"],[],None),              # `READY-TO-FIRE.md:360-366`
 ("c63","AP","Q",["a real, reportable outcome"],[],None),              # `AGENT-PROMPT.md:424-428`
 ("c64","TR","Q",["the panel and fine-mapping result stand unmodified"],[],None),  # trsx5:43 (Option A)  corrected by E7 (Task-1 value "the fine-mapping result stand unmodified" lives in E7 evidence.before)
 ("c65","TR","Q",["fine-mapping proceeds on the reduced variant set"],[],None),  # trsx5:45
 ("c66","RN","T",["return result"],[],None),                            # `:967`  (EXPANDED in banked, E5)
 ("c67","RN","T",["pln.plink_ld_to_npz("],[],None),                     # `:1090`
 ("c68","TR","Q",["the three outcome branches … before any occlusion-handling code fires"],[],None),  # trsx5:53
 ("n02","AP","T",["~11 days"],[],"E10"),                                      # `AGENT-PROMPT.md:393` (K2)
 ("c69","FV","T",['"counts": counts','"n_failed"'],[],None),            # `fire_verifier.py:363-370`
 ("c70","OD","Q",["no covering record for EITHER member"],[],None),    # `osf_deviations.md:703-704`
 ("c71","MK","T",["Clause (a), the occlusion criterion","flagged as an occluder"],[],None),  # mk7ze P300-302 / R467-469
 ("c72","MK","Q",["NO new token"],[],None),                             # mk7ze P316 / R483
 ("c73","FV","Q",["the gates working"],[],None),                        # `fire_verifier.py:335-336`
 ("c74","HA","T",["MECHANISM CONFIRMED","0 of 871","perfectly confounded"],[],None),  # `260824-STAGE-B-HALT-…md:150-179`
 ("c75","HA","Q",["`--fail-fast` is correct for Stage A/B and **must not be carried into Stage C** at an unknown per-region failure rate"],[],None),  # `260824-STAGE-B-HALT-…md:104-107`
 ("n03","OD","T",["single survivor","21-region scan"],[],"E9"),               # `osf_deviations.md:660-663` (K1)
 ("n04","MK","T",["A systematic-by-span sample of 21 of the 276 AFR regions"],[],"E9"),   # mk7ze P88-89 / R255-256 (K1)
 ("n05","MK","T",["A systematic-by-span sample of 21 of the 276 AFR regions"],[],"E11"),  # mk7ze P88-89 / R255-256 (K3)
 ("c76","OD","Q",["to be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"],[],None),  # `osf_deviations.md:685-689`
 ("c77","OD","Q",["Production tests the rate on BOTH sides"],[],None),  # `:682`
 ("c78","OD","Q",["NO PREDICATE CHANGE … calibrate-to-pass at n=1"],[],None),  # `osf_deviations.md:670-671`
 ("c79","MK","Q",["both complete distributions fold in at closeout"],[],None),  # mk7ze P247-250 (§4 X1)
 ("n06","RF","T",["120000","--max-n-var"],[],"E12"),                           # `READY-TO-FIRE.md:369-370` (K4)
 ("c80","MK","Q",["NO new token"],[],None),                             # mk7ze P316 (§5 Q2)
 ("c81","MK","T",["both complete distributions fold in at closeout"],[],None),  # mk7ze P247-250 (§5 Q4, no quote)
]

# ==== PERMITTED_EDITS (Task 2) ===============================================================
# The ONLY differences allowed between the scratchpad source (16,817 B / md5 5e11157f...) and the
# banked draft. Applied in list order (E1..E17); every `old` must occur exactly once in the source
# and every `new` exactly once in the banked file. Class 1 = status line; class 2 = Files-cited key
# and bare-ref expansions printed by --bare-ref-plan; class 3 = proven citation corrections (live
# before-RED / after-GREEN evidence); class 4 = orchestrator-specified factual, citation-
# completeness and neutrality corrections (revision 1), each new citation with its own CLAIMS row.
_KEY_BLOCK = "".join(line + "\n" for line in (
    "",
    "**Files cited** (short form used below → full repo-relative path):",
    "- `260812-ox1-AGENT-PROMPT.md`, `AGENT-PROMPT.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md`",
    "- `260812-ox1-READY-TO-FIRE.md`, `READY-TO-FIRE.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md`",
    "- `260824-STAGE-B-HALT-…md` → `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`",
    "- `run_native_ld_panel.py` → `src/python/run_native_ld_panel.py`",
    "- `fire_verifier.py` → `src/python/fire_verifier.py`",
    "- `plink_ld_to_npz.py` → `src/python/plink_ld_to_npz.py`",
    "- `osf_deviations.md` → `.planning/osf_deviations.md`",
    "- `deferred-items.md` → `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`",
    "- `STATE.md` → `.planning/STATE.md`",
    "- `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` → `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`",
))
_ORIGIN4 = "orchestrator-specified, quick-260916-kht revision 1"

PERMITTED_EDITS = [
    {"id": "E1", "cls": 1,
     "old": "**Status:** DRAFT, not banked in the repo, no code written, **no decision made.** Built for review by",
     "new": "**Status:** DRAFT, banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by",
     "why": "class 1 (task constraint 1): status line records banked / NOT sent to Seth / NOT decided; line 4 untouched"},
    {"id": "E2", "cls": 2,
     "old": "- Code at HEAD `c93e97b`.\n",
     "new": "- Code at HEAD `c93e97b`.\n" + _KEY_BLOCK,
     "why": "class 2 (task constraint 2): Files-cited key mapping every short form to its full repo-relative path (+12 lines)"},
    {"id": "E3", "cls": 2, "bare_ref": True,
     "old": "It also halts on every deferral (`:1325-1328`)",
     "new": "It also halts on every deferral (`run_native_ld_panel.py:1325-1328`)",
     "why": "class 2 bare-ref expansion printed by --bare-ref-plan (PLAN 1, pos 23, c23): nearest-preceding explicit resolved to the Stage B HALT record, table file run_native_ld_panel.py"},
    {"id": "E4", "cls": 2, "bare_ref": True,
     "old": "(set at `:1068-1069`",
     "new": "(set at `run_native_ld_panel.py:1068-1069`",
     "why": "class 2 bare-ref expansion printed by --bare-ref-plan (PLAN 2, pos 47, c47): nearest-preceding explicit resolved to the Stage B HALT record, table file run_native_ld_panel.py"},
    {"id": "E5", "cls": 2, "bare_ref": True,
     "old": "returns at `:967`",
     "new": "returns at `run_native_ld_panel.py:967`",
     "why": "class 2 bare-ref expansion printed by --bare-ref-plan (PLAN 3, pos 68, c66): nearest-preceding explicit resolved to AGENT-PROMPT.md, table file run_native_ld_panel.py"},
    {"id": "E6", "cls": 3,
     "old": "mk7ze P311 / R478",
     "new": "mk7ze P311-312 / R478-479",
     "why": "class 3 (c30): the quoted 're-diagnosis' is on R479 / P312, not inside R478 / P311",
     "evidence": {"claim": "c30", "file": "MK", "kind": "Q",
                  "before": {"range": [478, 478], "prange": [311, 311],
                             "payload": ["A region over the anomaly gate is deferred for re-diagnosis …"]},
                  "after": {"range": [478, 479], "prange": [311, 312],
                            "payload": ["A region over the anomaly gate is deferred for re-diagnosis …"]}}},
    {"id": "E7", "cls": 3,
     "old": 'NONE needs "the fine-mapping result stand unmodified"',
     "new": 'NONE needs "the panel and fine-mapping result stand unmodified"',
     "why": "class 3 (c64): trsx5:43 reads 'the panel and fine-mapping result stand unmodified'; the quoted fragment is not a substring",
     "evidence": {"claim": "c64", "file": "TR", "kind": "Q",
                  "before": {"range": [43, 43], "payload": ["the fine-mapping result stand unmodified"]},
                  "after": {"range": [43, 43], "payload": ["the panel and fine-mapping result stand unmodified"]}}},
    {"id": "E8", "cls": 4, "label": "F1", "origin": _ORIGIN4,
     "old": "is written locally for every square region before plink.",
     "new": "is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at `run_native_ld_panel.py:806-815`, an infeasible one at `:866-872`).",
     "why": "F1 factual: c-ast:S9 + rows n01/n07 (RN:806-815 returns skipped_idempotent before the try: at :825; RN:866-872 returns deferred_infeasible_square before the sidecar write at :923-939)"},
    {"id": "E9", "cls": 4, "label": "K1", "origin": _ORIGIN4,
     "old": "rate:* 1 of 21 sampled regions carries a surviving pair. The sample was systematic-by-span, not\n  random,",
     "new": "rate:* 1 of 21 sampled regions carries a surviving pair (`osf_deviations.md:660-663`). The sample was systematic-by-span, not\n  random (mk7ze P88-89 / R255-256),",
     "why": "K1 citation completeness: rows n03 (OD:660-663) and n04 (mk7ze P88-89 / R255-256)"},
    {"id": "E10", "cls": 4, "label": "K2", "origin": _ORIGIN4,
     "old": "for the rest of the ~11 days.",
     "new": "for the rest of the ~11 days (`AGENT-PROMPT.md:393`).",
     "why": "K2 citation completeness: row n02 (AP:393 STEP 10 ~11 days)"},
    {"id": "E11", "cls": 4, "label": "K3", "origin": _ORIGIN4,
     "old": "scan across all 276 AFR regions before",
     "new": "scan across all 276 AFR regions (mk7ze P88-89 / R255-256) before",
     "why": "K3 citation completeness: row n05 (mk7ze P88-89 / R255-256, 276 AFR regions)"},
    {"id": "E12", "cls": 4, "label": "K4", "origin": _ORIGIN4,
     "old": "120,000-variant ceiling)",
     "new": "120,000-variant ceiling; `READY-TO-FIRE.md:369-370`)",
     "why": "K4 citation completeness: row n06 (RF:369-370 --max-n-var default 120000)"},
    {"id": "E13", "cls": 4, "label": "N1", "origin": _ORIGIN4,
     "old": "*READING 2 (the counter-reading, to be tested):*",
     "new": "*READING 2:*",
     "why": "N1 neutrality: orchestrator-specified"},
    {"id": "E14", "cls": 4, "label": "N2", "origin": _ORIGIN4,
     "old": "literal `--fail-fast` is not workable (P4). The realistic form is the operator stopping\n  the fire at the first `error:` row.",
     "new": "literal `--fail-fast` would also halt on already-banked and deferred regions (P4), so\n  this option means the operator stopping the fire at the first `error:` row.",
     "why": "N2 neutrality: orchestrator-specified"},
    {"id": "E15", "cls": 4, "label": "N3", "origin": _ORIGIN4,
     "old": "turns a surprise into a pre-declared, measured set. Needs VM time (Carter).",
     "new": "the regions expected to raise are measured before Stage C instead of observed during it. Needs VM time (Carter).",
     "why": "N3 neutrality: orchestrator-specified"},
    {"id": "E16", "cls": 4, "label": "N4", "origin": _ORIGIN4,
     "old": "A full-panel\n  scan *is* that test. Running D before the disclosure is posted would use up the prediction, unless\n  the prediction is explicitly retired first.",
     "new": "A full-panel\n  scan would measure that same both-sides rate before production does; whether that uses up the\n  prediction is question 5.",
     "why": "N4 neutrality: orchestrator-specified"},
    {"id": "E17", "cls": 4, "label": "N5", "origin": _ORIGIN4,
     "old": 'A contract raise gets counted as "the gates working"\n  (`fire_verifier.py:335-336`), which is not the rationale that PASS was built on.',
     "new": 'A contract raise would be classified under the deferral PASS, whose stated reason is "the gates working"\n  (`fire_verifier.py:335-336`).',
     "why": "N5 neutrality: orchestrator-specified (rewrites text around the existing c73 token; adds no citation)"},
]
# ==== end PERMITTED_EDITS ====================================================================


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
    ST is always read at BASIS. `overrides` maps a repo-relative path to a file (selftest)."""

    def __init__(self, live=False, overrides=None):
        self.live = live
        self.overrides = dict(overrides or {})
        self._cache = {}

    def raw(self, rel, at_basis=False):
        if rel in self.overrides:
            return Path(self.overrides[rel]).read_bytes()
        from_tree = bool(self.live and not at_basis and rel != PATHS["ST"])
        key = (rel, from_tree)
        if key not in self._cache:
            if from_tree:
                self._cache[key] = (ROOT / rel).read_bytes()
            else:
                r = git("show", "%s:%s" % (BASIS, rel))
                if r.returncode != 0:
                    raise VerifyError("git show %s:%s rc=%d %s" % (
                        BASIS, rel, r.returncode, r.stderr.decode("utf-8", "replace").strip()))
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
    """Content check of a payload inside a cited 1-based inclusive range (never clamped).
    MK claims are checked BOTH at the repo range and at the posted-extract P range."""
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
# parser / key / resolution / paragraph units
# --------------------------------------------------------------------------------------------
CITE = re.compile(
    r'`(?P<file>[^`\s:]*(?:\.|…)(?:md|py|txt)):(?P<a>\d+)(?:-(?P<b>\d+))?`'
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
            c.update(kind="mk7ze", p=p, r=r, rng=r if r is not None else (p[0] + OFFSET, p[1] + OFFSET))
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
    return line.lstrip(" ").startswith("|")


def unit_for_offset(draft, off):
    lines = draft.split("\n")
    li = draft.count("\n", 0, off)
    if _is_table(lines[li]):
        return lines[li]
    i = li
    while (not _UNIT_START.match(lines[i]) and i > 0
           and lines[i - 1].strip() != "" and not _is_table(lines[i - 1])):
        i -= 1
    j = li
    while (j + 1 < len(lines) and lines[j + 1].strip() != "" and not _is_table(lines[j + 1])
           and not _UNIT_START.match(lines[j + 1])):
        j += 1
    return "\n".join(lines[i:j + 1])


# --------------------------------------------------------------------------------------------
# (a) mk7ze anchor, (b) trsx5 anchor
# --------------------------------------------------------------------------------------------
def check_anchor_mk(mk_bytes, draft, start=MK_START, end=MK_END, ctrl=MK_CONTROL):
    out = []
    ext = byte_lines(mk_bytes, start, end)
    if ext is None:
        out.append(("RED", "a:size", "lines %d-%d outside the file" % (start, end)))
        out.append(("RED", "a:md5", "not computed: size failed"))
    else:
        ok = len(ext) == MK_SIZE
        out.append(("PASS" if ok else "RED", "a:size", "lines %d-%d = %d B (want %d)" % (start, end, len(ext), MK_SIZE)))
        if ok:
            h = md5(ext)
            out.append(("PASS" if h == MK_MD5 else "RED", "a:md5", "md5 %s (want %s)" % (h, MK_MD5)))
        else:
            out.append(("RED", "a:md5", "not computed: size failed"))
    ctl = byte_lines(mk_bytes, ctrl[0], ctrl[1])
    if ctl is None:
        out.append(("RED", "a:control", "control lines %d-%d outside the file" % ctrl))
        out.append(("RED", "a:control-prefix", "control not computed"))
    else:
        ch = md5(ctl)
        if ch == MK_MD5:
            out.append(("RED", "a:control", "control matched: anchor cannot fail (lines %d-%d md5 %s)" % (ctrl[0], ctrl[1], ch)))
        else:
            out.append(("PASS", "a:control", "lines %d-%d md5 %s != anchor" % (ctrl[0], ctrl[1], ch)))
        out.append(("PASS" if ch.startswith(MK_CONTROL_PREFIX) else "RED", "a:control-prefix",
                    "control md5 %s starts with %s: %s" % (ch, MK_CONTROL_PREFIX, ch.startswith(MK_CONTROL_PREFIX))))
    nd = norm(draft)
    miss = [n for n in ("22,945 B", MK_MD5, MK_CONTROL_PREFIX) if norm(n) not in nd]
    out.append(("PASS" if not miss else "RED", "a:draft", "draft states size/md5/control prefix" + ("" if not miss else "; missing %r" % miss)))
    return out


def check_anchor_tr(tr_bytes, draft, ctrl_len=TR_CONTROL_LEN):
    out = []
    ok = len(tr_bytes) == TR_SIZE
    out.append(("PASS" if ok else "RED", "b:size", "%d B (want %d)" % (len(tr_bytes), TR_SIZE)))
    if ok:
        h = md5(tr_bytes)
        out.append(("PASS" if h == TR_MD5 else "RED", "b:md5", "md5 %s (want %s)" % (h, TR_MD5)))
    else:
        out.append(("RED", "b:md5", "not computed: size failed"))
    ch = md5(tr_bytes[:ctrl_len])
    if ch == TR_MD5:
        out.append(("RED", "b:control", "control matched: anchor cannot fail (first %d B md5 %s)" % (ctrl_len, ch)))
    else:
        out.append(("PASS", "b:control", "first %d B md5 %s != anchor" % (ctrl_len, ch)))
    nd = norm(draft)
    miss = [n for n in ("9,695 B", TR_MD5) if norm(n) not in nd]
    out.append(("PASS" if not miss else "RED", "b:draft", "draft states size/md5" + ("" if not miss else "; missing %r" % miss)))
    return out


# --------------------------------------------------------------------------------------------
# (c) citations
# --------------------------------------------------------------------------------------------
def check_citations(draft, claims, reader):
    out = []
    cites = parse_citations(draft)
    key = parse_key(draft)
    km = keymap_of(key)
    # c-key
    if key is None:
        out.append(("RED", "c-key", "no **Files cited** key block in the draft"))
    else:
        probs = []
        if key["bad"]:
            probs.append("unparseable key lines %r" % key["bad"])
        if not key["entries"]:
            probs.append("key block has no entries")
        outside = draft[:key["span"][0]] + draft[key["span"][1]:]
        for full in sorted({f for _, f in key["entries"]}):
            if not (ROOT / full).is_file():
                probs.append("not a file: %s" % full)
            if git("cat-file", "-e", "%s:%s" % (BASIS, full)).returncode != 0:
                probs.append("not tracked at %s: %s" % (BASIS, full))
        for s, full in key["entries"]:
            pat = ".*" + re.escape(s).replace(re.escape("…"), ".*")
            if not re.fullmatch(pat, Path(full).name):
                probs.append("short %r does not match basename of %s" % (s, full))
            if s not in outside:
                probs.append("short %r not used outside the key block" % s)
        for s, fs in sorted(km.items()):
            if len(fs) > 1:
                probs.append("short %r maps to %d paths %r" % (s, len(fs), sorted(fs)))
        out.append(("PASS" if not probs else "RED", "c-key",
                    ("%d shorts -> %d paths" % (len(key["entries"]), len({f for _, f in key["entries"]})))
                    + ("" if not probs else "; " + "; ".join(probs))))
    resolve(cites, km)
    np_, nt = len(cites), len(claims)
    msg = "parsed=%d table=%d" % (np_, nt)
    if np_ != nt:
        msg += "; parsed tokens: %r" % [c["text"] for c in cites]
    out.append(("PASS" if np_ == nt else "RED", "c-count", msg))
    nd = norm(draft)
    for i, row in enumerate(claims):
        cid, fkey, kind, payload, nots = row[:5]
        c = cites[i] if i < np_ else None
        if c is None:
            out.append(("RED", "c-res:" + cid, "no parsed citation at position %d" % (i + 1)))
            out.append(("RED", "c:" + cid, "no parsed citation at position %d" % (i + 1)))
            if kind == "Q":
                out.append(("RED", "c-quote:" + cid, "no parsed citation at position %d" % (i + 1)))
                out.append(("RED", "c-bind:" + cid, "no parsed citation at position %d" % (i + 1)))
            if fkey == "MK":
                out.append(("RED", "c-pr:" + cid, "no parsed citation at position %d" % (i + 1)))
            continue
        want = PATHS[fkey]
        out.append(("PASS" if c["resolved"] == want else "RED", "c-res:" + cid,
                    "pos %d %s -> %s (want %s)" % (i + 1, c["text"], c["resolved"], want)))
        prng = None
        rng = c["rng"]
        if fkey == "MK":
            prng = c["p"] if c["kind"] == "mk7ze" else (rng[0] - OFFSET, rng[1] - OFFSET)
        try:
            ok, detail = content_check(reader, fkey, rng, kind, payload, nots, prng)
        except Exception as e:  # a read/parse failure is a RED, never a crash-to-green
            ok, detail = False, "exception %s: %s" % (type(e).__name__, e)
        rtxt = "%s:%d-%d" % (fkey, rng[0], rng[1]) + (" P%d-%d" % prng if prng else "")
        out.append(("PASS" if ok else "RED", "c:" + cid, "pos %d %s %s%s" % (i + 1, c["text"], rtxt, "" if ok else " -- " + detail)))
        if kind == "Q":
            qm = [q for q in payload if not seg_in(q, nd)]
            out.append(("PASS" if not qm else "RED", "c-quote:" + cid,
                        "quote in draft" if not qm else "quote NOT in draft: %r" % qm))
            unit = unit_for_offset(draft, c["start"])
            bm = [q for q in payload if not seg_in(q, norm(unit))]
            first = draft.count("\n", 0, c["start"]) + 1
            out.append(("PASS" if not bm else "RED", "c-bind:" + cid,
                        ("quote bound to the paragraph of %s (draft line %d)" % (c["text"], first)) if not bm
                        else "quote %r NOT in the paragraph unit of %s (draft line %d): %r" % (bm, c["text"], first, unit)))
        if fkey == "MK":
            if c["kind"] != "mk7ze":
                out.append(("RED", "c-pr:" + cid, "parsed token %s is not an mk7ze citation" % c["text"]))
            elif c["r"] is None:
                out.append(("PASS", "c-pr:" + cid, "R derived = P+167 (%s)" % c["text"]))
            else:
                p, r = c["p"], c["r"]
                ok = r[0] == p[0] + OFFSET and r[1] == p[1] + OFFSET
                out.append(("PASS" if ok else "RED", "c-pr:" + cid,
                            "%s: P%d-%d +167 = R%d-%d vs stated R%d-%d" % (c["text"], p[0], p[1], p[0] + OFFSET, p[1] + OFFSET, r[0], r[1])))
    return out, np_


# --------------------------------------------------------------------------------------------
# c-ast
# --------------------------------------------------------------------------------------------
def _seg(src, node):
    return ast.get_source_segment(src, node)


def _innermost_func(tree, line):
    best = None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno <= line <= n.end_lineno:
            if best is None or (n.end_lineno - n.lineno) < (best.end_lineno - best.lineno):
                best = n
    return best


def _in_if_body(src, tree, test, a, b):
    for n in ast.walk(tree):
        if isinstance(n, ast.If) and n.body and _seg(src, n.test) == test:
            if n.body[0].lineno <= a and b <= n.body[-1].end_lineno:
                return n.lineno
    return None


def max_n_var_literal(tree):
    for n in tree.body:
        tgt, val = None, None
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            tgt, val = n.targets[0].id, n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            tgt, val = n.target.id, n.value
        if tgt == "_DEFAULT_MAX_N_VAR" and isinstance(val, ast.Constant) and isinstance(val.value, int):
            return val.value
    return None


def s9_check(src, tree):
    """F1 evidence: both early returns of process_region precede the gate-sidecar write."""
    fails = []
    ifs = [n for n in ast.walk(tree) if isinstance(n, ast.If)]
    # (i)
    i806 = [n for n in ifs if n.lineno == 806]
    if len(i806) != 1 or _seg(src, i806[0].test) != "existing is not None":
        fails.append("(i) no `if existing is not None:` at 806")
    elif not (isinstance(i806[0].body[-1], ast.Return) and i806[0].body[-1].end_lineno == 815):
        fails.append("(i) body of 806 does not end in a Return at 815")
    tries = [n for n in ast.walk(tree) if isinstance(n, ast.Try) and n.lineno <= 866 and n.end_lineno >= 923]
    if not tries:
        fails.append("(i) no ast.Try spans 866 and 923")
    else:
        t = max(tries, key=lambda n: n.lineno)
        if not (815 < t.lineno and t.lineno == 825):
            fails.append("(i) enclosing Try at %d (want 825, after 815)" % t.lineno)
    # (ii)
    i866 = [n for n in ifs if n.lineno == 866]
    if len(i866) != 1 or _seg(src, i866[0].test) != "pre_window_n_var > max_n_var":
        fails.append("(ii) no `if pre_window_n_var > max_n_var:` at 866")
    elif not (isinstance(i866[0].body[-1], ast.Return) and i866[0].body[-1].end_lineno == 872):
        fails.append("(ii) body of 866 does not end in a Return at 872")
    pr = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "process_region"]
    sc_nodes = []
    if len(pr) == 1:
        for n in ast.walk(pr[0]):
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "gate_sidecar" for t in n.targets):
                sc_nodes.append(n)
    else:
        fails.append("(ii) %d FunctionDefs named process_region" % len(pr))
    sc = min(n.lineno for n in sc_nodes) if sc_nodes else None
    if sc != 923:
        fails.append("(ii) sidecar assignment `gate_sidecar = ...` at %s (want 923)" % sc)
    w925 = [n for n in ast.walk(tree) if isinstance(n, ast.With) and n.lineno == 925]
    if not (len(w925) == 1 and _seg(src, w925[0].items[0].context_expr) == 'open(gate_sidecar, "w")'):
        fails.append('(ii) no `with open(gate_sidecar, "w")` at 925')
    for ln in (806, 815, 866, 872, 923, 925):
        f = _innermost_func(tree, ln)
        if f is None or f.name != "process_region":
            fails.append("(ii) innermost def of %d is %s" % (ln, None if f is None else f.name))
    # (iii) EXHAUSTIVE early-return set before the (AST-located) sidecar assignment
    if sc is None:
        fails.append("(iii) sidecar assignment not located")
    else:
        rets = [n for n in ast.walk(tree) if isinstance(n, ast.Return) and n.lineno < sc]
        own = set()
        for n in rets:
            f = _innermost_func(tree, n.lineno)
            if f is not None and f.name == "process_region":
                own.add(n.lineno)
        if own != {815, 872}:
            fails.append("(iii) process_region returns before the sidecar (line %d) = %s (want [815, 872])" % (sc, sorted(own)))
        r891 = [n for n in rets if n.lineno == 891]
        f891 = _innermost_func(tree, 891) if r891 else None
        if not r891 or f891 is None or f891.name != "_site" or 891 in own:
            fails.append("(iii) nested `_site` return at 891 not explicitly excluded (found=%s, innermost=%s)" % (
                bool(r891), None if f891 is None else f891.name))
    # (iv) enclosing compound statements of the sidecar assignment
    if sc is not None:
        kinds = (ast.If, ast.Try, ast.With, ast.For, ast.While, ast.AsyncWith, ast.AsyncFor)
        enc = sorted((type(n).__name__, n.lineno) for n in ast.walk(tree)
                     if isinstance(n, kinds) and n.lineno <= sc <= n.end_lineno)
        if enc != [("If", 850), ("Try", 825)]:
            fails.append("(iv) nodes enclosing the sidecar (line %d) = %s (want Try@825, If@850)" % (sc, enc))
        else:
            i850 = [n for n in ifs if n.lineno == 850]
            if not i850 or _seg(src, i850[0].test) != 'mode == "square"':
                fails.append('(iv) If@850 test is not `mode == "square"`')
    return fails


def check_ast(reader, s2_name=S2_NAME):
    out = []

    def parsed(key):
        src = reader.text(PATHS[key])
        return src, ast.parse(src)

    def run(sid, fn):
        try:
            ok, msg = fn()
        except Exception as e:
            ok, msg = False, "exception %s: %s" % (type(e).__name__, e)
        out.append(("PASS" if ok else "RED", "c-ast:" + sid, msg))

    def s1():
        src, t = parsed("PL")
        f = _innermost_func(t, 218)
        n = None if f is None else f.name
        return n == "read_square_bin", "PL:218 innermost def = %s (want read_square_bin)" % n

    def s2():
        src, t = parsed("RN")
        f = _innermost_func(t, 1144)
        n = None if f is None else f.name
        return n == s2_name, "RN:1144 innermost def = %s (want %s)" % (n, s2_name)

    def s_if(test, a, b):
        def fn():
            src, t = parsed("RN")
            at = _in_if_body(src, t, test, a, b)
            return at is not None, "RN:%d-%d in body of `if %s:` = %s" % (a, b, test, "at %d" % at if at else "NOT FOUND")
        return fn

    def s7():
        src, t = parsed("RN")
        v = max_n_var_literal(t)
        return v == 120000, "RN module _DEFAULT_MAX_N_VAR literal = %r (want 120000)" % v

    def s8():
        src, t = parsed("TFV")
        name = "test_shipped_status_vocabulary_is_covered_by_the_allow_list"
        ok = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name for n in ast.walk(t))
        return ok, "TFV defines %s: %s" % (name, ok)

    def s9():
        src, t = parsed("RN")
        fails = s9_check(src, t)
        if fails:
            return False, "FAILED parts: " + " | ".join(fails)
        return True, ("(i) if@806 returns at 815 before Try@825; (ii) if@866 returns at 872 before sidecar@923 <= with@925, "
                      "all in process_region; (iii) process_region returns before the sidecar == {815, 872}, _site@891 excluded; "
                      "(iv) enclosing = Try@825, If@850 `mode == \"square\"`")

    run("S1", s1)
    run("S2", s2)
    run("S3", s_if("fired", 967, 967))
    run("S4", s_if("fired", 962, 965))
    run("S5", s_if("ok", 1106, 1106))
    run("S6", s_if("ok", 1136, 1139))
    run("S7", s7)
    run("S8", s8)
    run("S9", s9)
    return out


# --------------------------------------------------------------------------------------------
# c-hand
# --------------------------------------------------------------------------------------------
def binom_cdf(k, n, p):
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(k + 1))


def clopper_pearson(x, n, conf):
    alpha = (100.0 - conf) / 200.0
    if x == 0:
        lo = 0.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            m = (a + b) / 2
            if 1.0 - binom_cdf(x - 1, n, m) < alpha:
                a = m
            else:
                b = m
        lo = (a + b) / 2
    if x == n:
        hi = 1.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            m = (a + b) / 2
            if binom_cdf(x, n, m) > alpha:
                a = m
            else:
                b = m
        hi = (a + b) / 2
    return lo, hi


H1_REGEX = {
    "sample": r'(\d+) of (\d+) sampled regions',
    "scale": r'scaled to (\d+) that is ≈(\d+) regions, with an exact (\d+)% binomial range of ([\d.]+)–(\d+)',
    "runtime": r'the (\d+)-region run took (\d+) min \(.*?\), which scales linearly to ~([\d.]+) h',
    "panel": r'scan across all (\d+) afr regions',
    "bytes": r'\(nvar² × (\d+) b; ≈([\d.]+) gb at the ([\d,]+)-variant ceiling',
}


def check_hand(draft, reader, h2_marker=H2_MARKER, h3_line=H3_LINE):
    out = []
    nd = norm(draft)

    def h1():
        probs, g = [], {}
        for name, rx in H1_REGEX.items():
            ms = re.findall(rx, nd)
            if len(ms) != 1:
                probs.append("regex %s matched %d times (want 1): %s" % (name, len(ms), rx))
            else:
                g[name] = ms[0]
        if probs:
            return False, "; ".join(probs)
        x, n = int(g["sample"][0]), int(g["sample"][1])
        N, mid, conf = int(g["scale"][0]), int(g["scale"][1]), int(g["scale"][2])
        lo_s, hi_s = float(g["scale"][3]), int(g["scale"][4])
        n_run, minutes, hours_s = int(g["runtime"][0]), int(g["runtime"][1]), float(g["runtime"][2])
        n_panel = int(g["panel"])
        bpc, gb_s, cap = int(g["bytes"][0]), float(g["bytes"][1]), int(g["bytes"][2].replace(",", ""))
        lo, hi = clopper_pearson(x, n, conf)
        lit = max_n_var_literal(ast.parse(reader.text(PATHS["RN"])))
        calc = [
            ("mid", round(x / n * N), mid),
            ("lo", round(lo * N, 1), lo_s),
            ("hi", round(hi * N), hi_s),
            ("hours", round(minutes * n_panel / n_run / 60, 1), hours_s),
            ("gb", round(cap ** 2 * bpc / 1e9, 1), gb_s),
            ("cap==S7", lit, cap),
        ]
        bad = [c for c in calc if c[1] != c[2]]
        msg = ("extracted x=%d n=%d N=%d conf=%d n_run=%d min=%d N_panel=%d bytes/cell=%d cap=%d; CP95=(%.6f, %.5f); "
               % (x, n, N, conf, n_run, minutes, n_panel, bpc, cap, lo, hi)
               + ", ".join("%s recomputed %r stated %r" % c for c in calc))
        return not bad, msg + ("" if not bad else " -- MISMATCH %r" % bad)

    def h2():
        lines = reader.text(PATHS["ST"], at_basis=True).split("\n")
        idx = [i for i, l in enumerate(lines) if l.rstrip("\r") == "---"][:2]
        if len(idx) < 2:
            return False, "ST frontmatter delimiters not found"
        fm = "\n".join(lines[idx[0] + 1:idx[1]])
        k = fm.count(h2_marker)
        if k != 1:
            return False, "marker %r occurs %d times in ST@%s frontmatter (want 1)" % (h2_marker, k, BASIS)
        s = fm.index(h2_marker)
        e = fm.find(" PRIOR: ", s + len(h2_marker))
        block = fm[s:] if e < 0 else fm[s:e]
        ok = "Runtime 48m" in block
        return ok, "ST@%s frontmatter marker %r once; its block (%d chars) contains 'Runtime 48m': %s" % (BASIS, h2_marker, len(block), ok)

    def h3():
        lines = reader.lines(PATHS["OD"])
        if not (1 <= h3_line <= len(lines)) or not re.match(r"^## ", lines[h3_line - 1]):
            return False, "OD line %d is not a `## ` heading" % h3_line
        end = len(lines)
        for k in range(h3_line + 1, len(lines) + 1):
            if re.match(r"^## ", lines[k - 1]):
                end = k - 1
                break
        probs = []
        if not (h3_line <= 657 and 704 <= end):
            probs.append("657-704 not inside entry %d-%d" % (h3_line, end))
        st = [k for k in range(h3_line, end + 1) if re.match(r"^- \*\*Status:\*\*", lines[k - 1])]
        if not st:
            probs.append("no Status line in entry")
        elif "DRAFTED — NOT POSTED" not in lines[st[0] - 1]:
            probs.append("first Status line %d lacks DRAFTED — NOT POSTED" % st[0])
        return (not probs), ("OD entry %d-%d (EOF %d) contains 657-704; first Status line %s: %r" % (
            h3_line, end, len(lines), st[0] if st else None, lines[st[0] - 1] if st else None)
            + ("" if not probs else " -- " + "; ".join(probs)))

    def h4():
        h = md5(reader.raw(PATHS["U7"]))
        return h != TR_MD5, "U7 md5 %s != trsx5 posted md5 %s: %s" % (h, TR_MD5, h != TR_MD5)

    def h5():
        stated = "code at head c93e97b" in nd
        rc = git("merge-base", "--is-ancestor", BASIS, "HEAD").returncode
        return stated and rc == 0, "draft states Code at HEAD c93e97b: %s; merge-base --is-ancestor %s HEAD rc=%d" % (stated, BASIS, rc)

    for hid, fn in (("H1", h1), ("H2", h2), ("H3", h3), ("H4", h4), ("H5", h5)):
        try:
            ok, msg = fn()
        except Exception as e:
            ok, msg = False, "exception %s: %s" % (type(e).__name__, e)
        out.append(("PASS" if ok else "RED", "c-hand:" + hid, msg))
    return out


# --------------------------------------------------------------------------------------------
# (d) sweep of the posted bodies
# --------------------------------------------------------------------------------------------
D_REGEX = (r'and searched\. (.+?): 0 hits in either\. control: defer has (\d+) hits in mk7ze and (\d+) in trsx5; '
           r'raise has (\d+) and (\d+),')


def check_sweep(draft, reader):
    out = []
    nd = norm(draft)
    m = re.search(D_REGEX, nd)
    if not m:
        return [("RED", "d:parse", "sweep sentence regex did not match the normalized draft")]
    terms = m.group(1).split(", ")
    bad = [t for t in terms if not re.fullmatch(r"^[a-z]+$", t)]
    ok = bool(terms) and not bad
    out.append(("PASS" if ok else "RED", "d:parse", "terms=%r; stated defer=%s/%s raise=%s/%s%s" % (
        terms, m.group(2), m.group(3), m.group(4), m.group(5), "" if not bad else "; bad terms %r" % bad)))
    mk_raw = byte_lines(reader.raw(PATHS["MK"]), MK_START, MK_END).decode("utf-8")
    tr_raw = reader.text(PATHS["TR"])
    mkn, trn = norm(mk_raw), norm(tr_raw)
    seen = set()
    for t in terms:
        if t in seen:
            continue
        seen.add(t)
        a, b = mkn.count(t), trn.count(t)
        out.append(("PASS" if a == 0 and b == 0 else "RED", "d:zero:" + t, "%r mk7ze=%d trsx5=%d (want 0/0)" % (t, a, b)))
    for did, term, want_mk, want_tr in (("d:defer", "defer", int(m.group(2)), int(m.group(3))),
                                        ("d:raise", "raise", int(m.group(4)), int(m.group(5)))):
        a, b = mkn.count(term), trn.count(term)
        out.append(("PASS" if (a, b) == (want_mk, want_tr) else "RED", did,
                    "%r recomputed mk7ze=%d trsx5=%d; draft states %d/%d" % (term, a, b, want_mk, want_tr)))
    raw_mk, raw_tr = mk_raw.lower().count("deferred_infeasible_square"), tr_raw.lower().count("deferred_infeasible_square")
    st_mk, st_tr = mkn.count("deferredinfeasiblesquare"), trn.count("deferredinfeasiblesquare")
    stated = "the existing deferredinfeasiblesquare route is also absent from both" in nd
    ok = raw_mk == raw_tr == st_mk == st_tr == 0 and stated
    out.append(("PASS" if ok else "RED", "d:dis", "deferred_infeasible_square raw-lower mk7ze=%d trsx5=%d; underscore-stripped mk7ze=%d trsx5=%d; draft states absent: %s" % (
        raw_mk, raw_tr, st_mk, st_tr, stated)))
    return out


# --------------------------------------------------------------------------------------------
# (e) git freeze facts on the fire-path files
# --------------------------------------------------------------------------------------------
def check_git(ref, since=SINCE, since_control=SINCE_CONTROL, live=False):
    out = []
    paths = [PATHS["RN"], PATHS["FV"], PATHS["PL"]]
    lg = git("log", "--since=" + since, "--format=%H", ref, "--", *paths)
    ct = git("log", "--since=" + since_control, "--format=%H", ref, "--", *paths)
    ctl = ct.stdout.decode().split()
    ctl_ok = ct.returncode == 0 and len(ctl) > 0
    out.append(("PASS" if ctl_ok else "RED", "e:control",
                "git log --since=%r --format=%%H %s -- RN FV PL: rc=%d count=%d oldest=%s all=%s" % (
                    since_control, ref, ct.returncode, len(ctl), ctl[-1][:7] if ctl else None, " ".join(h[:7] for h in ctl))))
    lgl = lg.stdout.decode().split()
    ok = lg.returncode == 0 and len(lgl) == 0 and ctl_ok
    out.append(("PASS" if ok else "RED", "e:log",
                "git log --since=%r --format=%%H %s -- RN FV PL: rc=%d count=%d%s" % (
                    since, ref, lg.returncode, len(lgl), "" if ctl_ok else " (control empty: an empty log proves nothing)")))
    if ctl:
        rc = git("diff", "--quiet", ctl[-1] + "~1", BASIS, "--", PATHS["RN"]).returncode
        out.append(("PASS" if rc == 1 else "RED", "e:diff-control",
                    "git diff --quiet %s~1 %s -- src/python/run_native_ld_panel.py rc=%d (want 1)" % (ctl[-1][:7], BASIS, rc)))
    else:
        out.append(("RED", "e:diff-control", "no control commit to diff against"))
    if live:
        rc = git("diff", "--quiet", BASIS, "--", *paths).returncode
        out.append(("PASS" if rc == 0 else "RED", "e:diff", "git diff --quiet %s -- RN FV PL rc=%d (want 0)" % (BASIS, rc)))
    return out


# --------------------------------------------------------------------------------------------
# (g) neutrality screen -- LEXICAL, cannot prove neutrality
# --------------------------------------------------------------------------------------------
G_PATTERNS = [r"recommend", r"\bprefer", r"\bsuggest", r"\bpropos(e|es|ed|al)\b", r"\badvis(e|es|ed|able)\b",
              r"\bbest (option|choice|path|course)\b", r"\b(we|i) (favou?r|endorse|lean|urge|advocate)\b",
              r"\bin (our|my) (view|opinion|judgement|judgment)\b", r"\b(right|correct) (choice|option|call)\b",
              r"\bshould (choose|adopt|pick|go with|select)\b", r"\bopt for\b"]


def check_neutral(draft):
    out = []
    nd = norm(draft)
    st = [l for l in draft.split("\n") if l.startswith("**Status:**")]
    if not st:
        out.append(("RED", "g:status", "no **Status:** line"))
    else:
        s = norm(st[0])
        need = ["banked in the repo", "not sent to seth", "not decided", "no code written"]
        miss = [n for n in need if n not in s]
        bad = "not banked" in s
        out.append(("PASS" if not miss and not bad else "RED", "g:status",
                    "status line %r%s%s" % (st[0], "" if not miss else "; missing %r" % miss, "; contains 'not banked'" if bad else "")))
    ex = "with no recommendation"
    k = nd.count(ex)
    out.append(("PASS" if k == 1 else "RED", "g:exempt", "%r occurs %d times (want exactly 1)" % (ex, k)))
    screened = nd.replace(ex, "", 1)
    hits = []
    for p in G_PATTERNS:
        for m in re.finditer(p, screened):
            hits.append("%s -> ...%s..." % (p, screened[max(0, m.start() - 40):m.end() + 40]))
    out.append(("PASS" if not hits else "RED", "g:recommend", "0 hits over %d patterns" % len(G_PATTERNS) if not hits else "%d hits: %s" % (len(hits), " || ".join(hits))))
    opts = re.findall(r'(?m)^### Option ([A-E]): ', draft)
    out.append(("PASS" if opts == ["A", "B", "C", "D", "E"] else "RED", "g:options", "options %r" % opts))
    h = "## 5. Questions for the adjudicator"
    if h not in draft:
        out.append(("RED", "g:questions", "heading %r missing" % h))
    else:
        qs = re.findall(r'(?m)^(\d)\. ', draft[draft.index(h) + len(h):])
        out.append(("PASS" if qs == ["1", "2", "3", "4", "5"] else "RED", "g:questions", "questions %r" % qs))
    return out


# --------------------------------------------------------------------------------------------
# report-only sweeps (INFO; never a gate, never counted)
# --------------------------------------------------------------------------------------------
EVAL_WORDS = ["not workable", "unworkable", "realistic", "surprise", "only honest", "clearly", "obviously", "should",
              "better", "worse", "prefer", "simply", "merely", "of course", "naturally"]
DERIVED = {"1", "21", "276", "13", "95", "0.3", "66", "48", "10.5", "4", "57.6", "120,000", "17", "3", "2", "0"}


def report_sweeps(draft):
    out = []
    lines = draft.split("\n")
    skip = set()
    for i, l in enumerate(lines):
        if l.startswith("**Anchors checked"):
            j = i
            while j < len(lines) and lines[j].strip() != "":
                skip.add(j)
                j += 1
        if l.startswith("**Files cited**"):
            skip.add(i)
            j = i + 1
            while j < len(lines) and lines[j].startswith("- "):
                skip.add(j)
                j += 1
    for i, l in enumerate(lines):
        words = [w for w in EVAL_WORDS if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", l, re.I)]
        if words:
            out.append(("INFO", "report:eval:%d" % (i + 1), "%r :: %s" % (words, l)))
    for i, l in enumerate(lines):
        if i in skip or CITE.search(l):
            continue
        s = re.sub(r"`[^`]*`", "", l)
        s = re.sub(r"^(\s*(?:#+\s*)?)\d+\.(?=\s)", r"\1", s)
        s = re.sub(r"\b[PTCXRQ]\d+\b", "", s)
        s = re.sub(r"\d{4}-\d{2}-\d{2}", "", s)
        nums = [n for n in re.findall(r"(?<![\w.])[+−-]?\d+(?:,\d{3})*(?:\.\d+)?", s) if n not in DERIVED]
        if nums:
            out.append(("INFO", "report:numeric:%d" % (i + 1), "%r :: %s" % (nums, l)))
    return out


# ==== (f) permitted-edit identity checks (Task 2) =============================================
_BARE_TOK = re.compile(r"`:\d+(?:-\d+)?`")
_EXPL_TOK = re.compile(r"`[^`\s:]*(?:\.|…)(?:md|py|txt):\d+(?:-\d+)?`")


def apply_edits(text, edits, reverse=False):
    """Exact replacements, each required to occur exactly once at its point of application."""
    probs = []
    for e in (list(reversed(edits)) if reverse else list(edits)):
        a, b = (e["new"], e["old"]) if reverse else (e["old"], e["new"])
        k = text.count(a)
        if k != 1:
            probs.append("%s: %s occurs %d times at its point of application (want 1)" % (e["id"], "new" if reverse else "old", k))
            if k == 0:
                continue
        text = text.replace(a, b, 1)
    return text, probs


def bare_ref_plan(source_text, edits, claims):
    """Apply every NON-bare-ref edit, then greedily (reading order) expand the first bare `:n`
    whose nearest-preceding-explicit resolution differs from the CLAIMS file; repeat."""
    text, probs = apply_edits(source_text, [e for e in edits if not e.get("bare_ref")])
    if probs:
        raise VerifyError("non-bare-ref edits did not apply: %r" % probs)
    plan = []
    for _ in range(len(claims) + 1):
        cites = resolve(parse_citations(text), keymap_of(parse_key(text)))
        if len(cites) != len(claims):
            raise VerifyError("parsed %d != table %d; positional plan undefined" % (len(cites), len(claims)))
        hit = None
        for i, c in enumerate(cites):
            if c["kind"] == "bare" and c["resolved"] != PATHS[claims[i][1]]:
                hit = (i, c)
                break
        if hit is None:
            return plan
        i, c = hit
        fkey = claims[i][1]
        new_tok = "`" + SHORT[fkey] + c["text"][1:]
        plan.append({"pos": i + 1, "claim": claims[i][0], "old": c["text"], "new": new_tok,
                     "resolved": c["resolved"], "want": PATHS[fkey]})
        text = text[:c["start"]] + new_tok + text[c["end"]:]
    raise VerifyError("bare-ref plan did not converge")


def evidence_check(reader, ev, side):
    s = ev[side]
    prng = tuple(s["prange"]) if s.get("prange") else None
    return content_check(reader, ev["file"], tuple(s["range"]), ev["kind"], s["payload"], [], prng)


def check_edits(banked_text, source_bytes, edits, claims, reader):
    out = []
    # f:classes
    probs = []
    ids = [e.get("id") for e in edits]
    if ids != ["E%d" % i for i in range(1, 18)]:
        probs.append("ids %r != E1..E17 in application order" % ids)
    for e in edits:
        if e.get("cls") not in (1, 2, 3, 4):
            probs.append("%s cls %r" % (e.get("id"), e.get("cls")))
        if not e.get("why"):
            probs.append("%s has no why" % e.get("id"))
        if e.get("cls") == 3 and not e.get("evidence"):
            probs.append("%s class 3 without evidence" % e.get("id"))
        if e.get("cls") == 4 and not (e.get("label") and e.get("origin")):
            probs.append("%s class 4 without label/origin" % e.get("id"))
    c1 = [e.get("id") for e in edits if e.get("cls") == 1]
    if c1 != ["E1"]:
        probs.append("class-1 edits %r (want ['E1'])" % c1)
    nl = [(e["id"], e["new"].count("\n") - e["old"].count("\n")) for e in edits if e["new"].count("\n") != e["old"].count("\n")]
    if nl != [("E2", 12)]:
        probs.append("newline-count changes %r (want [('E2', 12)])" % nl)
    out.append(("PASS" if not probs else "RED", "f:classes",
                "%d edits, classes %r; only E2 changes line count (+12)" % (len(edits), [(e.get("id"), e.get("cls"), e.get("label")) for e in edits])
                + ("" if not probs else " -- " + "; ".join(probs))))
    # f:reverse (ALWAYS; must-be-identity)
    rev, rprobs = apply_edits(banked_text, edits, reverse=True)
    rb = rev.encode("utf-8")
    rsize_ok = len(rb) == SOURCE_SIZE
    rmd5 = md5(rb) if rsize_ok else None
    rev_ok = not rprobs and rsize_ok and rmd5 == SOURCE_MD5
    out.append(("PASS" if rev_ok else "RED", "f:reverse",
                "reverse-applied E17..E1 to the draft: %d B (want %d); md5 %s (want %s)%s" % (
                    len(rb), SOURCE_SIZE, rmd5 if rsize_ok else "not computed: size failed", SOURCE_MD5,
                    "" if not rprobs else " -- " + "; ".join(rprobs))))
    # f:forward (needs --source)
    src_text = None
    if source_bytes is None:
        out.append(("SKIP", "f:forward", "no --source"))
    else:
        fp = []
        if len(source_bytes) != SOURCE_SIZE:
            fp.append("source size %d != %d (md5 not computed)" % (len(source_bytes), SOURCE_SIZE))
        elif md5(source_bytes) != SOURCE_MD5:
            fp.append("source md5 %s != %s" % (md5(source_bytes), SOURCE_MD5))
        else:
            src_text = source_bytes.decode("utf-8")
            fwd, fprobs = apply_edits(src_text, edits)
            fp += fprobs
            if fwd.encode("utf-8") != banked_text.encode("utf-8"):
                fp.append("forward-applied source (%d B) != draft (%d B)" % (len(fwd.encode("utf-8")), len(banked_text.encode("utf-8"))))
        out.append(("PASS" if not fp else "RED", "f:forward",
                    ("source %d B md5 %s; E1..E17 applied == draft bytes (%d B)" % (SOURCE_SIZE, SOURCE_MD5, len(banked_text.encode("utf-8"))))
                    if not fp else "; ".join(fp)))
    base = src_text if src_text is not None else (rev if rev_ok else None)
    base_name = "source" if src_text is not None else "reverse-reconstructed source"
    # f:unique:<Eid>
    for e in edits:
        kn = banked_text.count(e["new"])
        ko = base.count(e["old"]) if base is not None else None
        ok = kn == 1 and ko == 1
        out.append(("PASS" if ok else "RED", "f:unique:" + e["id"],
                    "new x%d in draft; old x%s in %s (want 1/1)" % (kn, ko, base_name if base is not None else "source (UNAVAILABLE: no --source and f:reverse failed)")))
    # f:evidence:<Eid> (class 3): before RED, after GREEN, recomputed live
    for e in edits:
        if e.get("cls") != 3:
            continue
        ev = e["evidence"]
        try:
            b_ok, b_msg = evidence_check(reader, ev, "before")
            a_ok, a_msg = evidence_check(reader, ev, "after")
        except Exception as x:
            out.append(("RED", "f:evidence:" + e["id"], "exception %s: %s" % (type(x).__name__, x)))
            continue
        ok = (not b_ok) and a_ok
        out.append(("PASS" if ok else "RED", "f:evidence:" + e["id"],
                    "%s %s before %r -> %s (%s); after %r -> %s%s" % (
                        ev["claim"], ev["file"], {k: v for k, v in ev["before"].items() if k != "payload"},
                        "RED" if not b_ok else "GREEN", b_msg or "-", {k: v for k, v in ev["after"].items() if k != "payload"},
                        "GREEN" if a_ok else "RED", "" if a_ok else " (" + a_msg + ")")
                    + ("" if ok else " -- want before RED and after GREEN")))
    # f:bareplan
    if base is None:
        out.append(("RED", "f:bareplan", "no source available (no --source and f:reverse failed)"))
    else:
        try:
            plan = bare_ref_plan(base, edits, claims)
            got = [(p["old"], p["new"]) for p in plan]
            want = []
            for e in edits:
                if e.get("bare_ref"):
                    bo, bn = _BARE_TOK.findall(e["old"]), _EXPL_TOK.findall(e["new"])
                    want.append((bo[0] if len(bo) == 1 else bo, bn[0] if len(bn) == 1 else bn))
            ok = got == want and len(want) > 0
            out.append(("PASS" if ok else "RED", "f:bareplan",
                        "greedy plan from %s %r == class-2 bare-ref edits %r: %s" % (base_name, got, want, ok)))
        except Exception as x:
            out.append(("RED", "f:bareplan", "exception %s: %s" % (type(x).__name__, x)))
    return out
# ==== end (f) =================================================================================


# --------------------------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------------------------
class Ctx(object):
    def __init__(self, draft, claims, reader, live=False, baseline=False, source_bytes=None):
        self.draft = draft
        self.claims = claims
        self.reader = reader
        self.live = live
        self.baseline = baseline
        self.source_bytes = source_bytes
        self.mk_bytes = None
        self.tr_bytes = None
        self.a_start, self.a_end, self.a_ctrl = MK_START, MK_END, MK_CONTROL
        self.b_ctrl_len = TR_CONTROL_LEN
        self.s2_name = S2_NAME
        self.h2_marker, self.h3_line = H2_MARKER, H3_LINE
        self.since, self.since_control = SINCE, SINCE_CONTROL
        self.edits = PERMITTED_EDITS
        self.report = not baseline


def baseline_claims(claims, edits):
    """--baseline table: drop rows tagged with a class-4 edit; class-3-corrected rows get their
    `before` payload from that edit's evidence."""
    before = {}
    for e in edits:
        if e.get("cls") == 3:
            before[e["evidence"]["claim"]] = e["evidence"]["before"]["payload"]
    tagged4 = {e["id"] for e in edits if e.get("cls") == 4}
    out = []
    for row in claims:
        if row[5] is not None and row[5] in tagged4:
            continue
        if row[0] in before:
            row = (row[0], row[1], row[2], list(before[row[0]]), row[4], row[5])
        out.append(row)
    return out


def _guard(fam_id, fn):
    try:
        return fn()
    except Exception as e:
        return [("RED", fam_id, "exception %s: %s" % (type(e).__name__, e))]


def run_all(ctx):
    res = []
    rd = ctx.reader
    res += _guard("a:size", lambda: check_anchor_mk(ctx.mk_bytes if ctx.mk_bytes is not None else rd.raw(PATHS["MK"]),
                                                    ctx.draft, ctx.a_start, ctx.a_end, ctx.a_ctrl))
    res += _guard("b:size", lambda: check_anchor_tr(ctx.tr_bytes if ctx.tr_bytes is not None else rd.raw(PATHS["TR"]),
                                                    ctx.draft, ctx.b_ctrl_len))
    parsed = [0]

    def cits():
        out, n = check_citations(ctx.draft, ctx.claims, rd)
        parsed[0] = n
        return out
    res += _guard("c-count", cits)
    res += _guard("c-ast:S1", lambda: check_ast(rd, ctx.s2_name))
    res += _guard("c-hand:H1", lambda: check_hand(ctx.draft, rd, ctx.h2_marker, ctx.h3_line))
    res += _guard("d:parse", lambda: check_sweep(ctx.draft, rd))
    res += _guard("e:log", lambda: check_git("HEAD" if ctx.live else BASIS, ctx.since, ctx.since_control, ctx.live))
    if ctx.baseline:
        res.append(("SKIP", "f:", "baseline"))
    else:
        res += _guard("f:reverse", lambda: check_edits(ctx.draft, ctx.source_bytes, ctx.edits, ctx.claims, rd))
    res += _guard("g:status", lambda: check_neutral(ctx.draft))
    if ctx.report:
        res += _guard("report:error", lambda: report_sweeps(ctx.draft))
    return res, parsed[0]


def summarize(results, parsed, table, baseline=False, have_source=False):
    fixed = []
    for st, i, m in results:
        allowed = (baseline and i == "f:") or (i == "f:forward" and not have_source)
        if st == "SKIP" and not allowed:
            fixed.append(("RED", i, "SKIP not allowed for this id: " + m))
        else:
            fixed.append((st, i, m))
    ids = [r[1] for r in fixed if r[0] != "INFO"]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        fixed.append(("RED", "dup-ids", "duplicate result ids %r" % dups))
    checks = [r for r in fixed if r[0] in ("PASS", "RED")]
    reds = [r for r in checks if r[0] == "RED"]
    verified = sum(1 for r in fixed if r[0] == "PASS" and r[1].startswith("c:"))
    n_res = sum(1 for r in fixed if r[1].startswith("c-res:"))
    green = not reds and parsed == table == verified == n_res
    if green:
        line = "RESULT GREEN checks=%d parsed=%d table=%d verified=%d" % (len(checks), parsed, table, verified)
    else:
        line = "RESULT RED %d/%d parsed=%d table=%d verified=%d" % (len(reds), len(checks), parsed, table, verified)
        if not reds:
            line += " (count reconciliation failed: c-res=%d)" % n_res
    return fixed, green, line


def fmt(r):
    st, i, m = r
    tag = {"PASS": "PASS", "RED": "RED ", "SKIP": "SKIP", "INFO": "INFO"}[st]
    return "%s %s %s" % (tag, i, m)


# ==== bare-ref plan (Task 2) ==================================================================
def cmd_bare_ref_plan(args):
    if not args.source:
        print("RED bare-ref-plan --source is required")
        return 1
    sb = Path(args.source).read_bytes()
    if len(sb) != SOURCE_SIZE:
        print("RED bare-ref-plan source size %d != %d" % (len(sb), SOURCE_SIZE))
        return 1
    if md5(sb) != SOURCE_MD5:
        print("RED bare-ref-plan source md5 %s != %s" % (md5(sb), SOURCE_MD5))
        return 1
    applied = [e["id"] for e in PERMITTED_EDITS if not e.get("bare_ref")]
    print("BARE-REF-PLAN source %d B md5 %s; non-bare-ref edits applied in memory: %s" % (len(sb), SOURCE_MD5, " ".join(applied)))
    plan = bare_ref_plan(sb.decode("utf-8"), PERMITTED_EDITS, CLAIMS)
    for k, p in enumerate(plan, 1):
        print("PLAN %d pos=%d claim=%s %s -> %s (nearest-preceding explicit resolved to %s; table file %s)" % (
            k, p["pos"], p["claim"], p["old"], p["new"], p["resolved"], p["want"]))
    print("BARE-REF-PLAN %d expansion(s)" % len(plan))
    return 0
# ==== end bare-ref plan =======================================================================


# ==== selftest (Task 3) =======================================================================
class SelftestError(Exception):
    pass


def _once(s, old, new, what):
    k = s.count(old)
    if k != 1:
        raise SelftestError("%s: mutation `old` occurs %d times (want exactly 1): %r" % (what, k, old))
    out = s.replace(old, new, 1)
    if out == s:
        raise SelftestError("%s: mutation changed nothing" % what)
    return out


def selftest(args):
    """Every check family must be OBSERVED RED on a deliberately corrupted input (33 mutations),
    after a positive control on the real inputs is GREEN. Works only in a temp dir under $TMPDIR."""
    tmpdir_env = os.environ.get("TMPDIR", "")
    if not tmpdir_env:
        print("SELFTEST RED tmpdir: TMPDIR is not set (refusing to fall back to /tmp)")
        return 1
    tmp = tempfile.mkdtemp(prefix="kht-selftest-")
    try:
        tp = Path(tmp).resolve()
        if inside_root(tp):
            print("SELFTEST RED tmpdir: %s is inside the repo %s" % (tp, ROOT.resolve()))
            return 1
        if tp.parent != Path(tmpdir_env).resolve():
            print("SELFTEST RED tmpdir: %s is not directly under $TMPDIR %s" % (tp, Path(tmpdir_env).resolve()))
            return 1
        print("SELFTEST tmpdir %s (outside repo %s)" % (tp, ROOT.resolve()))
        reader = Reader(live=False)
        banked = (ROOT / BANKED_REL).read_bytes().decode("utf-8")

        def run(ctx):
            res, parsed = run_all(ctx)
            return summarize(res, parsed, len(ctx.claims), ctx.baseline, ctx.source_bytes is not None)

        # POSITIVE CONTROL (BASIS mode, no --source)
        fixed, green, line = run(Ctx(banked, list(CLAIMS), reader))
        pc_reds = [r for r in fixed if r[0] == "RED"]
        if pc_reds or not green:
            print("SELFTEST RED positive-control")
            for r in pc_reds:
                print(fmt(r))
            print(line)
            return 1
        print("SELFTEST positive-control GREEN: %s" % line)

        def put(name, data):
            p = tp / name
            p.write_bytes(data)
            return p

        def draft_ctx(name, text):
            if text == banked:
                raise SelftestError("%s: mutated draft equals the banked draft" % name)
            return Ctx(put(name + ".md", text.encode("utf-8")).read_bytes().decode("utf-8"), list(CLAIMS), reader)

        def dmut(name, old, new):
            return lambda: draft_ctx(name, _once(banked, old, new, name))

        def dappend(name, suffix):
            return lambda: draft_ctx(name, banked + suffix)

        def ddel_line(name, prefix):
            def b():
                ls = banked.split("\n")
                hit = [i for i, l in enumerate(ls) if l.startswith(prefix)]
                if len(hit) != 1:
                    raise SelftestError("%s: %d lines start with %r (want 1)" % (name, len(hit), prefix))
                return draft_ctx(name, "\n".join(ls[:hit[0]] + ls[hit[0] + 1:]))
            return b

        def pmut(name, attr, value):
            def b():
                c = Ctx(banked, list(CLAIMS), reader)
                if getattr(c, attr) == value:
                    raise SelftestError("%s: parameter %s already == %r" % (name, attr, value))
                setattr(c, attr, value)
                return c
            return b

        def st_a1():
            mk = reader.raw(PATHS["MK"])
            m = b"\n" + mk
            c = Ctx(banked, list(CLAIMS), reader)
            c.mk_bytes = put("ST-a1.mk7ze.md", m).read_bytes()
            if c.mk_bytes == mk:
                raise SelftestError("ST-a1: unchanged")
            return c

        def st_b1():
            tr = reader.raw(PATHS["TR"])
            c = Ctx(banked, list(CLAIMS), reader)
            c.tr_bytes = put("ST-b1.trsx5.txt", tr + b"x").read_bytes()
            if c.tr_bytes == tr or len(c.tr_bytes) != len(tr) + 1:
                raise SelftestError("ST-b1: not exactly +1 byte")
            return c

        def st_b2():
            tr = reader.raw(PATHS["TR"])
            ba = bytearray(tr)
            ba[100] ^= 0x01
            c = Ctx(banked, list(CLAIMS), reader)
            c.tr_bytes = put("ST-b2.trsx5.txt", bytes(ba)).read_bytes()
            if c.tr_bytes == tr or len(c.tr_bytes) != len(tr):
                raise SelftestError("ST-b2: not a same-size change")
            return c

        def st_c3():
            claims = copy.deepcopy(CLAIMS)
            i = [k for k, r in enumerate(claims) if r[0] == "c26"]
            if len(i) != 1:
                raise SelftestError("ST-c3: c26 rows %d" % len(i))
            row = claims[i[0]]
            new_payload = [_once(row[3][0], "continues to RAISE", "continued to RAISE", "ST-c3")] + list(row[3][1:])
            claims[i[0]] = (row[0], row[1], row[2], new_payload, row[4], row[5])
            if claims == CLAIMS:
                raise SelftestError("ST-c3: unchanged")
            return Ctx(banked, claims, reader)

        def st_f2():
            c = Ctx(banked, list(CLAIMS), reader)
            edits = copy.deepcopy(PERMITTED_EDITS)
            e6 = [e for e in edits if e["id"] == "E6"]
            if len(e6) != 1 or e6[0]["evidence"]["after"] == e6[0]["evidence"]["before"]:
                raise SelftestError("ST-f2: E6 missing or after already == before")
            e6[0]["evidence"]["after"] = copy.deepcopy(e6[0]["evidence"]["before"])
            c.edits = edits
            return c

        def st_f3():
            e8 = [e for e in PERMITTED_EDITS if e["id"] == "E8"]
            if len(e8) != 1:
                raise SelftestError("ST-f3: E8 missing")
            return draft_ctx("ST-f3", banked + e8[0]["new"] + "\n")

        def st_s9():
            src = reader.raw(PATHS["RN"]).decode("utf-8")
            ls = src.split("\n")
            if not ls[922].startswith("            gate_sidecar = Path("):
                raise SelftestError("ST-s9: line 923 is not the sidecar assignment: %r" % ls[922])
            mutated = "\n".join(ls[:922] + ["        if False:", "            return result"] + ls[922:])
            if mutated == src:
                raise SelftestError("ST-s9: unchanged")
            ast.parse(mutated)  # the RED must come from S9's logic, not from a parse failure
            p = put("ST-s9.run_native_ld_panel.py", mutated.encode("utf-8"))
            return Ctx(banked, list(CLAIMS), Reader(live=False, overrides={PATHS["RN"]: str(p)}))

        e1 = [e for e in PERMITTED_EDITS if e["id"] == "E1"][0]
        MUTATIONS = [
            ("ST-a1", "a:", st_a1, None),
            ("ST-a2", "a:", pmut("ST-a2", "a_start", 169), None),
            ("ST-a3", "a:control", pmut("ST-a3", "a_ctrl", (168, 500)), None),
            ("ST-b1", "b:size", st_b1, None),
            ("ST-b2", "b:md5", st_b2, None),
            ("ST-b3", "b:control", pmut("ST-b3", "b_ctrl_len", 9695), None),
            ("ST-c1", "c:c03", dmut("ST-c1", "`:417`", "`:422`"), None),
            ("ST-c2", "c-quote:c26", dmut("ST-c2", "RAISE on any NaN rather", "RAISE on every NaN rather"), None),
            ("ST-c3", "c:c26", st_c3, None),
            ("ST-c4", "c-count", dmut("ST-c4", "(`fire_verifier.py:363-370`)", ""), None),
            ("ST-c5", "c-res:c60", dmut("ST-c5", "`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`",
                                        "`.planning/quick/260908-n48-bank-the-seth-adjudication-closure-no-op/deferred-items.md`"), None),
            ("ST-c6", "c-pr:c29", dmut("ST-c6", "mk7ze P261 / R428", "mk7ze P262 / R428"), None),
            ("ST-c7", "c-ast:S2", pmut("ST-c7", "s2_name", "main"), None),
            ("ST-d1", "d:defer", dmut("ST-d1", "17 hits in mk7ze", "18 hits in mk7ze"), None),
            ("ST-c8", "c-bind:c73", dmut("ST-c8", 'whose stated reason is "the gates working"', 'whose stated reason is "the gate outcome"'), None),
            ("ST-n1", "c:n02", dmut("ST-n1", "`AGENT-PROMPT.md:393`", "`AGENT-PROMPT.md:398`"), None),
            ("ST-n2", "c-pr:n04", dmut("ST-n2", "random (mk7ze P88-89 / R255-256)", "random (mk7ze P88-89 / R256-257)"), None),
            ("ST-d2", "d:zero:defer", dmut("ST-d2", "`feasib`: **0 hits", "`defer`: **0 hits"), None),
            ("ST-h1", "c-hand:H1", dmut("ST-h1", "≈13 regions", "≈14 regions"), None),
            ("ST-h2", "c-hand:H2", pmut("ST-h2", "h2_marker", "PRIOR: 2026-09-01 — NO SUCH BLOCK"), None),
            ("ST-h3", "c-hand:H3", pmut("ST-h3", "h3_line", 533), None),
            ("ST-e1", "e:control", pmut("ST-e1", "since_control", "2026-08-24 00:00:00 -0400"), None),
            ("ST-e2", "e:log", pmut("ST-e2", "since", "2026-08-01 00:00:00 -0400"), None),
            ("ST-f1", "f:reverse", dmut("ST-f1", "run the card as committed", "run the card exactly as committed"), None),
            ("ST-f2", "f:evidence", st_f2, None),
            ("ST-f3", "f:unique:E8", st_f3, None),
            ("ST-s9", "c-ast:S9", st_s9, "(iii)"),
            ("ST-g1", "g:recommend", dappend("ST-g1", "\nWe recommend Option B.\n"), None),
            ("ST-g2", "g:recommend", dappend("ST-g2", "\nmy **recom**mendation is Option A\n"), None),
            ("ST-g3", "g:options", ddel_line("ST-g3", "### Option E: "), None),
            ("ST-g4", "g:questions", ddel_line("ST-g4", "5. Does a full-panel scan"), None),
            ("ST-g5", "g:status", dmut("ST-g5", e1["new"], e1["old"]), None),
            ("ST-g6", "g:exempt", dappend("ST-g6", " with no recommendation"), None),
        ]
        if len(MUTATIONS) != 33 or len({m[0] for m in MUTATIONS}) != 33:
            print("SELFTEST RED mutation-count %d (want 33 distinct)" % len(MUTATIONS))
            return 1
        observed, failed = 0, []
        for st_id, prefix, build, must in MUTATIONS:
            try:
                ctx = build()
            except SelftestError as e:
                print("SELFTEST NOT-OBSERVED %s (mutation invalid: %s)" % (st_id, e))
                failed.append(st_id)
                continue
            fx, g, ln = run(ctx)
            hits = [r for r in fx if r[0] == "RED" and r[1].startswith(prefix) and (must is None or must in r[2])]
            if hits and not g:
                observed += 1
                print("SELFTEST OBSERVED %s -> %s" % (st_id, fmt(hits[0])))
            else:
                failed.append(st_id)
                print("SELFTEST NOT-OBSERVED %s (no RED id starting with %r%s; %s)" % (
                    st_id, prefix, "" if must is None else " naming %r" % must, ln))
        if failed:
            print("SELFTEST RED positive-control=GREEN observed=%d/%d not-observed=%s" % (observed, len(MUTATIONS), " ".join(failed)))
            return 1
        print("SELFTEST GREEN positive-control=GREEN observed=%d/%d" % (observed, len(MUTATIONS)))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
# ==== end selftest ============================================================================


def main(argv=None):
    ap = argparse.ArgumentParser(description="quick-260916-kht citation re-verifier")
    ap.add_argument("--draft", default=str(ROOT / BANKED_REL))
    ap.add_argument("--source")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--bare-ref-plan", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    if args.json and inside_root(args.json):
        print("RED json:path refusing to write inside the repo: %s" % Path(args.json).resolve())
        return 1
    if args.selftest:
        return selftest(args)
    if args.bare_ref_plan:
        return cmd_bare_ref_plan(args)
    draft = Path(args.draft).read_bytes().decode("utf-8")
    source_bytes = Path(args.source).read_bytes() if args.source else None
    claims = baseline_claims(CLAIMS, PERMITTED_EDITS) if args.baseline else list(CLAIMS)
    ctx = Ctx(draft, claims, Reader(live=args.live), live=args.live, baseline=args.baseline, source_bytes=source_bytes)
    results, parsed = run_all(ctx)
    fixed, green, line = summarize(results, parsed, len(claims), args.baseline, source_bytes is not None)
    for r in fixed:
        print(fmt(r))
    print(line)
    if args.json:
        Path(args.json).write_text(json.dumps([{"status": s, "id": i, "msg": m} for s, i, m in fixed],
                                              indent=1, ensure_ascii=False), encoding="utf-8")
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
