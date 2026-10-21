---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 14
slug: W4-osf-r4-amendment-and-gate
type: execute
wave: 14
depends_on: ["W3e"]
files_modified:
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/amendments/osf-amendment-r4-FINAL.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md
  - tests/ta_r4/test_amendment_text.py
  - config/ta_r4/coloc_priors.yaml
  - config/ta_r4/decision_rules.yaml
  - config/ta_r4/simulation.yaml
  - .planning/osf_deviations.md
  - .planning/DECISIONS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SUSIE-RSS-POLICY

must_haves:
  truths:
    - "A paste-ready R4 amendment in the osf-amendment-r3-2026-05-04.md format exists, stating arms A1/A2/A3/A3-UKB (+ isect) and the AFR secondary (661 primary, 504 sensitivity), the matched-variant and fallback rules, E1-E8, the five branches plus the explicit partial_rule, the decision thresholds, the simulation design, the known-answer findings (with the D-17 SH2B3 provenance), the E-2 finding and fix (replacing the unposted osf-correction-v2, D-19), the BMI allele restoration (D-18), the measured EUR n / trait types / sdY (D-25), the HLA/BMI_Xq24 inadmissibility (D-24), and the analysis-code commit shas (W0d, W3c, W3d, W3e)"
    - "A brief-blind adversarial review (Codex CLI) attacked the amendment against the code before Carter saw the final text; its output is banked verbatim and every finding is dispositioned"
    - "Carter's lock values (p12 primary, kappa_cut, n_both_min, partial_rule, UKB-native handling, any remaining trait facts) are recorded verbatim; coloc_priors.yaml, decision_rules.yaml and simulation.yaml then carry locked: true in one commit whose sha the FINAL amendment cites"
    - "The executor NEVER posts to OSF and NEVER creates OSF-R4-POSTED.json; both blocking decisions list WAIT first; production is reachable only after `python -m ta_r4.r4_osf_gate --stage production` exits 0 against Carter's committed sentinel (D-05, D-27)"
    - "Public text contains none of: pivot, revision, salvage, audit-driven (framing rule)"
  artifacts:
    - path: ".planning/amendments/osf-amendment-r4-FINAL.md"
      provides: "the exact file Carter uploads to osf.io/az52u; its sha256 is what the gate verifies"
      contains: "--- PASTE INTO OSF FROM HERE ---"
    - path: "tests/ta_r4/test_amendment_text.py"
      provides: "framing-word scan and required-section presence for the amendment files"
  key_links:
    - from: ".planning/amendments/osf-amendment-r4-FINAL.md (sha256)"
      to: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json (Carter)"
      via: "amendment_sha256 field; verified against the OSF API by r4_osf_gate"
      pattern: "amendment_sha256"
---

<objective>
Wave 4 writes the R4 pre-registration amendment from measured facts and frozen analysis code. It
has the amendment attacked by a brief-blind reviewer, gets Carter's lock decisions, freezes the
configs, and then stops. Carter alone posts the amendment on osf.io/az52u and commits the
sentinel. Production (W5+) is enforced in code to be unreachable until then.

Purpose: D-05, D-27, D-26 (Carter locks κ / n_both), D-17/D-18/D-19/D-24/D-25 disclosures, REQ-OSF-PREREG.
Output: DRAFT and FINAL amendment files, the review record, locked configs, DEC + deviations entries.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-CONTEXT.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/amendments/osf-amendment-r3-2026-05-04.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2-REVIEW-PACKET.md

<interfaces>
Exemplar structure (.planning/amendments/osf-amendment-r3-2026-05-04.md): "Pre-Paste Reference (do NOT paste)" table + numbered pre-paste checklist,
  "--- PASTE INTO OSF FROM HERE ---" … "--- PASTE ENDS HERE ---" body (title, Date, Investigator: Carter K. Clinton, NCSU ASHES Lab,
  ORCID 0000-0003-2669-8200, Purpose, Motivation, New analytical commitments with lettered paragraphs and outcome branches, What is not changing),
  then "Post-Paste Reference (do NOT paste)"
Target: osf.io/az52u (supplementary file on the parent amendment record, the M1/R3 pattern); root pre-registration osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J)
Sentinel schema (r4_osf_gate.py): {osf_url, osf_file_guid, posted_utc, amendment_path, amendment_sha256, head_sha}
Codex CLI for review: memory reference_codex_cli_for_gsd_review (npm-installed; the only working external reviewer on this node)
Analysis-code commit shas: from the LOG entries of W0d, W3c, W3d, W3e
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify the p12 citation; draft the amendment and the deviations entry; framing test</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, tests/ta_r4/test_amendment_text.py, .planning/osf_deviations.md</files>
  <read_first>
    - .planning/amendments/osf-amendment-r3-2026-05-04.md (whole; format exemplar)
    - .planning/osf_deviations.md (the last 3 entries' format)
    - ta-r4-W3-KNOWN-ANSWER-FINDINGS.md, ta-r4-W2-REVIEW-PACKET.md, manifests/*.tsv, config/ta_r4/*.yaml, config/ta_r4/trait_manifest.tsv
    - the W3d SUMMARY (36-row truth table; partial_rule combos)
    - .planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-placement-draft-ms-correction-v2.md (the retired correction text: source material only)
  </read_first>
  <action>
    1. Verify the p12 recommendation: Wallace 2020 (PLoS Genet 16:e1008720, "Eliciting priors and
       relaxing the single causal variant assumption in colocalisation analyses"). Use the
       Consensus search tool or WebFetch of the paper. Quote the exact sentence and record it in the
       LOG. If the paper does not support 5e-6, put that into the draft as a decision for Carter;
       do not silently keep 5e-6.
    2. Write `.planning/amendments/osf-amendment-r4-DRAFT.md` in the exemplar's structure. The
       PASTE body's lettered paragraphs:
       (a) the hypothesis under test, stated neutrally ("whether LD handling changes cross-trait colocalization calls");
       (b) the arms and why A1 ≠ "identity LD";
       (c) the data, with checksums and the measured n (EUR from the .fam; AFR 661/504), the BMI allele restoration with match-rate numbers, and the trait types / sdY;
       (d) the matched-variant rule and the D-02 fallback with dual reporting;
       (e) the estimands E1–E8 with formulas and the region statistic;
       (f) the decision thresholds and the five branches, plus the partial_rule mapping table;
       (g) the simulation design;
       (h) the known-answer results, including the SH2B3 provenance stated as measured;
       (i) the allele-orientation finding and fix with its before/after reporting commitment. This replaces the unposted correction note; phrase it as a methods finding;
       (j) HLA_6p21 / BMI_Xq24 inadmissibility;
       (k) the production policy (current corrected max_iter) disclosed vs the reproduction policy;
       (l) "What is not changing", with the analysis-code commit shas.
       Leave lock values as `‹CARTER-LOCK: …›` placeholders. Every number is copied from a committed
       file named inline in the Pre-Paste Reference. Keep the body ≤ ~2,500 words.
    3. Write `tests/ta_r4/test_amendment_text.py`:
       - Scans the PASTE block of DRAFT and FINAL (FINAL only when it exists) for
         `\b(pivot|revision|salvage|audit-driven)\b` (case-insensitive). The words themselves are
         the property being banned, so this text scan is legitimate.
       - Asserts every lettered paragraph (a)–(l) is present.
       - Asserts FINAL contains no `‹CARTER-LOCK` placeholder.
       - Negative control: the scanner reports a tmp file containing "pivot".
    4. Draft a new dated entry at the END of `.planning/osf_deviations.md`, append-only, headed
       "R4 amendment — DRAFTED, NOT POSTED", listing the deviations (BMI restoration; SH2B3
       provenance; E-2 fix; correction-v2 retired; production policy vs frozen effective max_iter;
       AFR substrate 661).
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the test passes (with FINAL absent, its FINAL-only checks skip with an explicit reason); the negative control was observed
    - the LOG quotes the Wallace 2020 sentence with its source
    - `git diff -- .planning/osf_deviations.md | grep -c '^-[^-]'` prints 0 (append-only)
  </acceptance_criteria>
  <done>A complete draft built from measured, sourced facts.</done>
</task>

<task type="auto">
  <name>Task 2: Brief-blind adversarial review of the draft against the code (Codex CLI); disposition the findings</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - memory reference_codex_cli_for_gsd_review (invocation), feedback_internal_validation_cannot_catch_misspecified_premise
    - .planning/amendments/osf-amendment-r4-DRAFT.md
  </read_first>
  <action>
    Run Codex CLI non-interactively from the repo root. The prompt contains ONLY the draft
    amendment's PASTE block and this instruction: "You are a hostile methods reviewer. For every
    factual or methodological claim in this pre-registration, find the code or data file in this
    repository that implements or supports it, and report any claim that the code contradicts,
    that is unsupported, or that is ambiguous enough to allow post-hoc choice. Cite file:line."
    Do NOT give it the CONTEXT, RESEARCH, LOG or any summary (brief-blind). Bank the raw output
    verbatim, byte-for-byte, in `ta-r4-W4-AMENDMENT-REVIEW-as-received.md` under a 3-line header
    (date, command, sha256 of the prompt). Then append a disposition table: finding → verified
    against the code (file:line) → fixed in the draft / rejected with evidence. Apply the fixes to
    the DRAFT only.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -c "^|" .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the review file holds the verbatim Codex output and a disposition table with one row per finding (count of findings == count of rows; both numbers pasted)
    - the amendment text test still passes
  </acceptance_criteria>
  <done>The draft has survived a brief-blind attack against the code.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 3: Carter locks the pre-registration parameters</name>
  <decision>Lock values for the R4 pre-registration: p12 primary (5e-6 proposed; 1e-5 sensitivity), kappa_cut (0.6 proposed), n_both_min (10 proposed), partial_rule (HETEROGENEOUS proposed for the combos listed in the draft §(f)), UKB-native handling (from W2c), and approval of the draft text.</decision>
  <context>These values define the outcome branches. They must be fixed by Carter before the data exist (D-26). GSD auto-mode selects the first option, so the first option is WAIT.</context>
  <options>
    <option id="option-wait">
      <name>WAIT — stop execution and hand back to Carter (FIRST; the default under auto-mode)</name>
      <pros>Nothing is locked or posted without Carter.</pros>
      <cons>The chain pauses.</cons>
    </option>
    <option id="option-lock">
      <name>Carter provides every lock value explicitly in his reply</name>
      <pros>The pre-registration can be finalized.</pros>
      <cons>Requires Carter's explicit values. If any value is missing, the executor treats the whole reply as WAIT.</cons>
    </option>
  </options>
  <resume-signal>Carter replies "lock:" followed by every value (p12_primary, kappa_cut, n_both_min, partial_rule, ukb_native) and "draft approved" or his edits. Anything else = WAIT.</resume-signal>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>Present the draft, the review dispositions and the proposed values. On a complete "lock:" reply, append `DEC-<date>-ta-r4-prereg-locks` to DECISIONS.md quoting Carter's values verbatim, and log it. Do not infer any value.</action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -c "ta-r4-prereg-locks" .planning/DECISIONS.md</automated></verify>
  <acceptance_criteria>
    - DECISIONS.md has exactly one `ta-r4-prereg-locks` entry quoting all five values verbatim
  </acceptance_criteria>
  <done>Carter's lock values are recorded.</done>
  <read_first>
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md
  </read_first>
</task>

<task type="auto">
  <name>Task 4: Apply the locks, finalize the amendment, commit and push (still NOT posted)</name>
  <files>config/ta_r4/coloc_priors.yaml, config/ta_r4/decision_rules.yaml, config/ta_r4/simulation.yaml, .planning/amendments/osf-amendment-r4-FINAL.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - the `ta-r4-prereg-locks` DEC entry
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    1. Commit A (`chore(ta-r4-W4): lock pre-registration parameters`) contains only the three config
       files. Write Carter's values into them, set `locked: true`, and run the full `tests/ta_r4`
       suite. The estimand DRAFT/FINAL label test must still pass: FINAL also requires the gate,
       so outputs stay DRAFT until posting.
    2. Copy DRAFT → `osf-amendment-r4-FINAL.md`, replace every `‹CARTER-LOCK›` with the locked
       values, and cite commit A's sha in "What is not changing" as the locked-configuration commit,
       alongside the analysis-code shas. Fill the Pre-Paste checklist:
       1. upload THIS file unchanged as a supplementary file on osf.io/az52u;
       2. copy the OSF file GUID;
       3. `sha256sum .planning/amendments/osf-amendment-r4-FINAL.md`;
       4. create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json` with osf_url, osf_file_guid, posted_utc (ISO-8601 Z), amendment_path, amendment_sha256, head_sha (`git rev-parse HEAD` at posting);
       5. `git add` that file explicitly, commit, push;
       6. record the URL and timestamp in `.planning/osf_deviations.md` under the R4 entry.
    3. Run the amendment text test (FINAL now checked), then §C with label `W4`, commit type `docs`
       (commit B). Record `sha256sum osf-amendment-r4-FINAL.md` in the LOG.
    4. Run `$PY -m ta_r4.r4_osf_gate --stage production` (from src/python) and paste its non-zero
       refusal ("sentinel absent"). This proves the gate is closed at hand-off.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_osf_gate --stage production; test $? -ne 0 && echo GATE_CLOSED</automated>
  </verify>
  <acceptance_criteria>
    - the verify prints `GATE_CLOSED`
    - `$PY -c "import yaml;print([yaml.safe_load(open(f'config/ta_r4/{n}.yaml'))['locked'] for n in ('coloc_priors','decision_rules','simulation')])"` prints `[True, True, True]`
    - the amendment text test passes, including the FINAL checks (no placeholder, no banned words); the FINAL sha256 is in the LOG; pushed
  </acceptance_criteria>
  <done>The pre-registration is final and committed; the gate is provably closed.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 5: OSF POSTING GATE — Carter posts the amendment and commits the sentinel</name>
  <decision>Has Carter uploaded `.planning/amendments/osf-amendment-r4-FINAL.md` unchanged to osf.io/az52u AND committed and pushed `OSF-R4-POSTED.json`?</decision>
  <context>D-05/D-27. Production fits, coloc, simulation and QTL production are refused in code until `r4_osf_gate --stage production` exits 0. The executor must never create the sentinel or post anything.</context>
  <options>
    <option id="option-wait">
      <name>WAIT — STOP. The amendment is not yet posted. End execution here (FIRST; the default under auto-mode)</name>
      <pros>No production run can start before the public pre-registration.</pros>
      <cons>The chain pauses until Carter acts.</cons>
    </option>
    <option id="option-posted">
      <name>Carter has posted and committed the sentinel</name>
      <pros>Production may begin.</pros>
      <cons>Valid only if the gate check below exits 0. Otherwise the executor treats it as WAIT.</cons>
    </option>
  </options>
  <resume-signal>Carter says "posted" AND `python -m ta_r4.r4_osf_gate --stage production` exits 0. If the gate fails, report its reason and WAIT.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>Run the gate check. If it exits 0, log the OSF URL, GUID, posted_utc and the gate output, and continue to W5a. If it does not, log the reason and STOP. Never write OSF-R4-POSTED.json.</action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_osf_gate --stage production && echo GATE_OPEN</automated></verify>
  <acceptance_criteria>
    - `GATE_OPEN` printed
    - the sha of the commit that added the sentinel (`git log --format=%h -1 -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json`) is NOT in the list of commits this executor created (listed in the SUMMARY)
  </acceptance_criteria>
  <done>The R4 analysis is publicly pre-registered, and production is unlocked by verified evidence.</done>
  <read_first>
    - .planning/amendments/osf-amendment-r4-FINAL.md (Pre-Paste checklist)
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → public OSF record | an irreversible, public action (Carter only) |
| auto-mode → gate | an auto-selected option must not open production |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W4-01 | Spoofing | sentinel fabricated | mitigate | the OSF API sha256 check in r4_osf_gate; §B.12; the executor is instructed never to write it; first option WAIT |
| T-r4-W4-02 | Repudiation | parameters chosen after results | mitigate | locks committed before posting; the amendment cites the lock commit + code shas; production refuses until posting |
| T-r4-W4-03 | Tampering | a mis-specified premise in the public text | mitigate | brief-blind Codex review against the code; dispositions recorded |
| T-r4-W4-04 | Information disclosure | framing violations in public text | mitigate | banned-word scan with a negative control |
</threat_model>

<verification>
The draft passed the brief-blind review. Carter's locks are verbatim. Configs are locked. The gate
was closed at hand-off and opens only on verified posting.
</verification>

<success_criteria>
The comparison is publicly pre-registered with every decision rule fixed by Carter before any
production result exists, and the code enforces that ordering.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-osf-r4-amendment-and-gate-SUMMARY.md`
</output>
