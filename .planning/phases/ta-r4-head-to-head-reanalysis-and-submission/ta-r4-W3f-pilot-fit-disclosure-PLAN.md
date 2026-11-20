---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7i
slug: W3f-pilot-fit-disclosure
type: execute
wave: 15.7i
depends_on: ["ta-r4-W3f-proxy-asthma-refit"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15V3-reply-<date>.txt              # only if the recount differs from v2
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15-wording-as-approved-v3-<date>.txt # only if the recount differs from v2
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/prelock_pilot_fits.tsv
  - tests/ta_r4/test_prelock_pilot_fits.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-pilot-fit-disclosure-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "Gates: gate_reply.py Q-F15 prints \"A: Full disclosure + manifest (Recommended)\" and Q-F15W prints \"Clarify to the 20 fits (Recommended)\", each with its <question> text and sha256, and the v2 wording file has sha256 65c3851d21ee0cc0b044c9ee4c4d413dd3eb1c95423ea4d861c12792198b243b; otherwise nothing is edited"
    - "Before any DRAFT edit, every number and list in v2 is recounted from disk, now including 15.7h2's 20 asthma repro pilot fits (manifests/proxy_asthma_pilot_fits_sha256.tsv): total pilot fits (v2: 146), production-panel fits (20), earlier-catalog fits (18), reproduction-route fits (108), kernel-experiment runs (17), production-panel fits with ≥ 1 set (7 of 20) and their trait/region list, the purity measurement (109 components of the 20 production-panel fits, 15.7f), and the after-the-fact exact-purity recompute of 15.7h2 (the existing repro_routeC / repro_k2d_routeC fits of the other 4 EUR traits at the 10 confirmatory regions: 70 fitted objects at planning; and the 20 new asthma fits)"
    - "If every recounted value equals v2, v2 is inserted (no checkpoint). If any differs (expected: 15.7h2 adds 20 fits, so 146 → 166 and 108 → 128), the plan stops at Task 2, a checkpoint:human-action that stops even under --auto (§D), after printing a v3 paragraph with the recounted values and the added sentence on the 20 asthma fits; nothing is written to the DRAFT until Carter's re-approval exists as W3f-carter-15-7-Q-F15V3-reply-<date>.txt (label \"Approve v3 (Recommended)\") plus W3f-carter-15-7-Q-F15-wording-as-approved-v3-<date>.txt whose sha256 the orchestrator pins in this plan's <question> block on resume"
    - "No colocalization output computed from any pilot fit exists (searched and recorded)"
    - "The DRAFT purpose line reads \"before any production-arm fit exists\", and the end of (h) carries the approved paragraph (v2 or v3) inserted from its file with only its hard line wraps removed; an assertion compares the inserted text with the unwrapped file"
    - "manifests/prelock_pilot_fits.tsv lists every pilot fit JSON/RDS under data/r4/measure_asthma_fix/fits (including fits/proxy_asthma_repro_routeC and fits/proxy_asthma_repro_k2d_routeC) and bmi_determinism/fits, with sha256, set, trait, ancestry, region, status, purity-filtered CS count and sizes, and the measurement each was used for (purity_flip_measurement.tsv, w3f_region_contribution_proxy.tsv); test_prelock_pilot_fits enumerates the disk and fails on any unlisted or missing file"
    - "FULL vs full_15_7h2.xml: 0 removed; added == the 3 <new_tests>; 0 outcome changes; 2,692 = 2,639 P / 53 S / 0 F"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/prelock_pilot_fits.tsv"
      provides: "the checkable list of pre-lock pilot fits"
  key_links:
    - from: "DRAFT (h)"
      to: "the approved wording file (v2, or v3 after re-approval)"
      via: "inserted from the file, unwrapped"
      pattern: "Pre-lock pilot fits"
---

<objective>
Close F15 (CONFIRMED) with Carter's Q-F15 A and Q-F15W. The DRAFT says the analysis is fixed "before any production fit
exists", while corrected-input pilot fits exist and were inspected. 15.7h2 adds 20 more pilot fits, so the approved v2
numbers will not match the disk; this plan then stops for Carter to re-approve a v3 paragraph with the recounted
numbers, rather than inserting text he did not approve.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-F15: file `W3f-carter-15-7-Q-F15-reply-2026-11-20.txt`, sha256 `aaff9960248a711c4d2e5c7b4fd77ad24a84c784fe25c1a673c4646d50895877`.
Question text: The DRAFT says the lock comes 'before any production fit exists', but 146 corrected-input pilot fits exist outside the production directories (plus 17 kernel-experiment runs). They were inspected, never colocalized. 15.7f will also recompute exact purity on 109 of their credible-set components, to measure the F2 subsampling. How should the DRAFT disclose this?
Required label: `A: Full disclosure + manifest (Recommended)`

Q-F15W: file `W3f-carter-15-7-Q-F15W-reply-2026-11-20.txt`, sha256 `5bd31c68a69f2adf34a10aa363017ec02b3804506d4138cc55ba69a763ffef05`.
Question text: The F15 paragraph you approved says the purity 'of their credible-set components was also recomputed exactly'. 'Their' could be read as all 146 pilot fits, but the measurement covers only the 20 production-panel fits (109 components). Fix the wording?
Required label: `Clarify to the 20 fits (Recommended)`

Wording v2: `W3f-carter-15-7-Q-F15-wording-as-approved-v2-2026-11-20.txt`, sha256
`65c3851d21ee0cc0b044c9ee4c4d413dd3eb1c95423ea4d861c12792198b243b` (v1 c60e4346…439a superseded).

Q-F15V3 (only if the recount differs; presented at Task 2):
Question text: 15.7h2 ran 20 further pilot fits (asthma on the corrected inputs, 10 regions × 2 reproduction routes) for the region-contribution proxy, so the approved F15 paragraph's counts are out of date. Approve this v3 paragraph (recounted numbers, plus one sentence on the 20 fits)?
Labels: `Approve v3 (Recommended)` / `Edit v3` (an edit is a new wording file, re-presented)
Pinned on resume: reply file sha256 `<orchestrator pins>`, wording-v3 file sha256 `<orchestrator pins>`.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/amendments/osf-amendment-r4-DRAFT.md

**Gates.** Q-F15 and Q-F15W via gate_reply.py; v2 sha256 check. On resume after Task 2: Q-F15V3 via gate_reply.py
with label `Approve v3 (Recommended)` and the pinned sha256, plus the v3 wording file's pinned sha256. Any failure →
STOP.

**Measured at planning (recompute in Task 1):** measure_asthma_fix/fits before 15.7h2: A3_1kg_newcat 20,
A3_1kg_oldcat 16, determinism_rerun_oldcat 2, repro_routeC_newcat 60, repro_routeC_oldcat 48 = 146; bmi_determinism
17 runs; 7 of the 20 A3_1kg_newcat fits with ≥ 1 purity-filtered set (asthma FTO_16q12; BMI FTO_16q12, MC4R_18q21,
SH2B3_12q24; hypertension SH2B3_12q24; stroke SH2B3_12q24; type 2 diabetes FTO_16q12). 15.7h2 adds 20 reproduction-route
fits under fits/proxy_asthma_*.

**v3 template (Task 1 fills every number from the recount and prints it; it differs from v2 only in recounted values
and one added sentence placed before "No colocalization…"):** v2's text with the counts replaced, plus: "A further 20
reproduction-route fits of asthma on the corrected inputs (10 regions × 2 reproduction routes) were run to measure the
region-contribution proxy for the confirmatory region floor, after the floor was fixed at 7 regions; N of them stopped
before fitting (more than 16,000 variants) and their credible-set counts entered only that proxy
(manifests/w3f_region_contribution_proxy.tsv). For that proxy the purity of the credible sets of these fits and of
M existing reproduction-route fits of the other four EUR traits was recomputed exactly after fitting, without refitting."
(N and M come from the recount.)
</context>

<new_tests>
tests/ta_r4/test_prelock_pilot_fits.py; N_new = 3.
1. `test_manifest_lists_every_pilot_fit_on_disk` (r4_heavy)
2. `test_manifest_sha256_match` (r4_heavy)
3. `test_draft_paragraph_equals_the_approved_file_unwrapped` (reads the committed approved wording file, v2 or v3, and
   the DRAFT; fails if an earlier version's text is present)
Expected FULL: base full_15_7h2.xml (2,689) + 3 = 2,692 = 2,639 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: Gates, DEC, recount, manifest; decide v2 or v3</name>
  <files>.planning/DECISIONS.md, manifests/prelock_pilot_fits.tsv, tests/ta_r4/test_prelock_pilot_fits.py</files>
  <action>
    0. Gates; `git rev-parse HEAD > $Q/start_15_7i.txt`; DEC `DEC-2026-11-20-ta-r4-prelock-pilot-fit-disclosure`
       quoting Q-F15, Q-F15W and wording v2 (`cat` + `cmp`); commit 1.
    1. Recount everything in must_haves into `$Q/pilot_recount.txt` and compare with v2's values; search for
       colocalization outputs whose inputs point into measure_asthma_fix.
    2. Manifest; RED tests 1-2 (absent → fail), then green. Commit 2.
    3. Write one line `recount_matches_v2=true` or `recount_matches_v2=false` to `$Q/pilot_recount.txt`. Equal to v2 →
       skip Task 2. Different → write `$Q/F15_wording_v3_draft.txt` from the template (19-line wrap
       like v2), print it in full with the recount table, and go to Task 2.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_prelock_pilot_fits.py -q -p no:cacheprovider -k "manifest" && test -s data/r4/tmp/w3f/q157/pilot_recount.txt</automated>
  </verify>
  <done>Gates passed; recount and manifest done; v2 kept or a v3 draft printed.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: Carter re-approves the F15 paragraph (only if the recount differs from v2)</name>
  <what-built>Recount of all pre-lock pilot fits including 15.7h2's 20 asthma fits; v3 draft at data/r4/tmp/w3f/q157/F15_wording_v3_draft.txt</what-built>
  <how-to-verify>
    1. Read the recount table and the v3 draft.
    2. Approve with label "Approve v3 (Recommended)", or supply edited wording.
    3. Only Carter's own typed reply may create the Q-F15V3 file: the executor never writes it, and an auto-mode or
       orchestrator-composed "approved" is not a reply. The orchestrator saves Carter's message verbatim as `W3f-carter-15-7-Q-F15V3-reply-<date>.txt` and the approved text byte-for-byte
       as `W3f-carter-15-7-Q-F15-wording-as-approved-v3-<date>.txt`, then pins both sha256 values in <question>.
  </how-to-verify>
  <files>(none written by the executor; Carter's reply and wording files are saved by the orchestrator)</files>
  <action>Skip this task if Task 1 found the recount equal to v2. Otherwise present the recount table and the v3 draft to Carter and wait; write nothing to the DRAFT.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && if grep -qx 'recount_matches_v2=true' data/r4/tmp/w3f/q157/pilot_recount.txt; then echo "recount matches v2: Task 2 skipped"; else ls .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15V3-reply-*.txt .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15-wording-as-approved-v3-*.txt; fi</automated>
  </verify>
  <done>Either the recount matched v2 (task skipped), or both v3 files exist with their sha256 pinned in <question>.</done>
  <resume-signal>Both files exist and their sha256 values are pinned in this plan; an auto "approved" is WAIT (§B.15)</resume-signal>
</task>

<task type="auto">
  <name>Task 3: Insert the approved paragraph; FULL vs full_15_7h2.xml; records (no push)</name>
  <files>the v3 reply and wording files (if any), .planning/DECISIONS.md, tests/ta_r4/test_prelock_pilot_fits.py, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-pilot-fit-disclosure-SUMMARY.md</files>
  <action>
    1. If v3: gate Q-F15V3 and the v3 sha256; append the v3 reply and file to the DEC (`cat` + `cmp`); commit them.
    2. DRAFT, one script: purpose line "before any production fit exists" → "before any production-arm fit exists"
       (asserted unique); append to (h) the approved file's text with in-paragraph newlines replaced by one space;
       assert equality with the unwrapped file; test 3; test_amendment_text.py green (a length or framing failure is
       STOP; the approved text is not reworded). Commit.
    3. Close per the 15.7 protocol, tag 15_7i: `$Q/check_15_7i.py` (removed 0; added == the 3; 0 outcome changes;
       2,692 = 2,639 / 53 / 0). Records (STATE NEXT = 15.7j; NOT PUSHED). fsck; commit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_prelock_pilot_fits.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider && grep -q "before any production-arm fit exists" .planning/amendments/osf-amendment-r4-DRAFT.md && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7i.py</automated>
  </verify>
  <done>The approved paragraph (v2, or v3 after re-approval) is in the DRAFT; manifest enforced; FULL reconciled; no push.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| public text → outcome-blindness claim | the text must match what exists and what Carter approved |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157i-01 | Repudiation | wording Carter did not approve | mitigate | v2 only on an exact recount match; otherwise a blocking human-action checkpoint and a sha256-pinned v3 |
| T-r4-157i-02 | Tampering | counts in public text | mitigate | recount from disk; test 3 ties the DRAFT to the approved file |
</threat_model>

<verification>
- The DRAFT contains the approved paragraph; check_15_7i.py passes.
</verification>

<success_criteria>
- The amendment discloses every pre-lock pilot fit, including the 20 proxy fits, in words Carter approved.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-pilot-fit-disclosure-SUMMARY.md`
</output>
