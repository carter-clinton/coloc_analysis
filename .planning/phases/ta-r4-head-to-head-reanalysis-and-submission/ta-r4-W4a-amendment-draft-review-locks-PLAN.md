---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 16
slug: W4a-amendment-draft-review-locks
type: execute
wave: 16
depends_on: ["ta-r4-W3e-qtl-harmonize-and-group-runner"]
files_modified:
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - src/python/ta_r4/extract_paste_block.py
  - tests/ta_r4/test_amendment_text.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md
  - .planning/osf_deviations.md
  - .planning/DECISIONS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W4a-T3.yaml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SUSIE-RSS-POLICY
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "A paste-ready R4 amendment DRAFT in the osf-amendment-r3-2026-05-04.md format exists, stating arms A1/A2/A3/A3-UKB (+ isect) and the AFR secondary (661 primary, 504 sensitivity), the matched-variant and fallback rules, E1-E8, the classifier precedence and the five branches with the 8 partial_rule combinations, the decision thresholds, the simulation design, the three negative-control sets including the GWAS-null window rule, the known-answer findings (with the D-17 SH2B3 provenance), the E-2 finding and fix (replacing the unposted osf-correction-v2, D-19), the BMI allele restoration (D-18), the measured EUR n / trait types / sdY (D-25), Carter's W2c decisions (ukb_native, qtl_scope), the HLA/BMI_Xq24 inadmissibility (D-24; HLA UKB fits are exploratory and produce no coloc row), and the analysis-code commit shas (W0d, W3c, W3d, W3e)"
    - "extract_paste_block.py deterministically extracts the text strictly between `--- PASTE INTO OSF FROM HERE ---` and `--- PASTE ENDS HERE ---`; that extract is the only public text, and the framing scan and the internal-content scan cover the WHOLE extract (checker W4)"
    - "A brief-blind adversarial review (Codex CLI) attacked the extract against the code before Carter saw it; its output is banked verbatim and every finding is dispositioned"
    - "Carter's lock values are recorded only through a checkpoint:human-action whose reply parses as `carter-approved YYYY-MM-DD` + every required key (signoffs/W4a-T3.yaml); a bare 'approved' is WAIT (B1)"
    - "The executor NEVER posts to OSF and NEVER creates OSF-R4-POSTED.json"
  artifacts:
    - path: ".planning/amendments/osf-amendment-r4-DRAFT.md"
      provides: "draft amendment with ‹CARTER-LOCK› placeholders"
      contains: "--- PASTE INTO OSF FROM HERE ---"
    - path: "src/python/ta_r4/extract_paste_block.py"
      provides: "extract(path) -> str; CLI writes the PUBLIC file"
    - path: "tests/ta_r4/test_amendment_text.py"
      provides: "framing + internal-content scans over the whole public extract; required paragraphs; PUBLIC == extract(FINAL)"
  key_links:
    - from: ".planning/amendments/osf-amendment-r4-DRAFT.md"
      to: "src/python/ta_r4/extract_paste_block.py"
      via: "the reviewed text is the extract, the same function that produces the PUBLIC file in W4b"
      pattern: "PASTE INTO OSF FROM HERE"
---

<objective>
Wave 4a writes the R4 pre-registration amendment from measured facts and frozen analysis code,
builds the extractor that produces the public text, has that text attacked by a brief-blind
reviewer, and obtains Carter's lock values through a checkpoint that auto-mode cannot pass.

Purpose: D-05, D-26 (Carter locks κ / n_both / partial_rule), D-17/D-18/D-19/D-24/D-25 disclosures,
REQ-OSF-PREREG, REQ-NEGATIVE-CONTROLS (third set disclosed). Split from the original W4 (checker W14).
Output: DRAFT amendment, extractor + text tests, review record, deviations entry, sign-off + DEC entry.
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
Codex CLI for review: memory reference_codex_cli_for_gsd_review (npm-installed; the only working external reviewer on this node)
Analysis-code commit shas: from the LOG entries of W0d, W3c, W3d, W3e
Carter's W2c decisions: config/ta_r4/review_decisions.yaml (+ signoffs/W2c-T4.yaml); W3b instructions: signoffs/W3b-T3.yaml
Classifier truth table and the 8 partial_rule rows: W3d SUMMARY
Sign-off tool: python -m ta_r4.signoff record|verify W4a-T3 (SCHEMAS in src/python/ta_r4/signoff.py)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Verify the p12 citation; extractor + text tests; draft the amendment and the deviations entry</name>
  <files>src/python/ta_r4/extract_paste_block.py, tests/ta_r4/test_amendment_text.py, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/osf_deviations.md</files>
  <read_first>
    - .planning/amendments/osf-amendment-r3-2026-05-04.md (whole; format exemplar)
    - .planning/osf_deviations.md (the last 3 entries' format)
    - ta-r4-W3-KNOWN-ANSWER-FINDINGS.md, ta-r4-W2-REVIEW-PACKET.md, manifests/*.tsv, config/ta_r4/*.yaml, config/ta_r4/trait_manifest.tsv, config/ta_r4/review_decisions.yaml
    - the W3d SUMMARY (36-row truth table; the 8 partial_rule rows) and manifests/null_windows_selection.tsv
    - .planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-placement-draft-ms-correction-v2.md (the retired correction text: source material only)
  </read_first>
  <behavior>
    - extract(path) returns the text strictly between the two marker lines (markers excluded); it raises if either marker is missing, duplicated or out of order; output is byte-deterministic
    - Framing scan over the WHOLE extract (DRAFT now; FINAL and PUBLIC when they exist): no match for `\b(pivot|revision|salvage|audit-driven)\b` (case-insensitive). The banned words are the property itself, so a text scan is the right instrument
    - Internal-content scan over the whole extract: no `.planning/`, `/rs1/`, `/gpfs`, `/share/`, `data/r4`, `signoffs/`, `DEC-20`, `Pre-Paste`, `do NOT paste`, `CARTER-LOCK` (FINAL/PUBLIC only), and no Markdown checklist item (`- [ ]` / `- [x]`)
    - Paragraphs (a)–(m) are present in the extract
    - When PUBLIC exists: PUBLIC is byte-identical to extract(FINAL)
    - Negative controls: a tmp extract containing "pivot" fails the framing scan; one containing ".planning/x" fails the internal-content scan; a file with the end marker before the start marker raises
  </behavior>
  <action>
    1. Verify the p12 recommendation: Wallace 2020 (PLoS Genet 16:e1008720, "Eliciting priors and
       relaxing the single causal variant assumption in colocalisation analyses"). Use the
       Consensus search tool or WebFetch of the paper. Quote the exact sentence and record it in the
       LOG. If the paper does not support 5e-6, put that into the draft as a decision for Carter;
       do not silently keep 5e-6.
    2. Tests RED; implement `extract_paste_block.py` (CLI `--in FINAL --out PUBLIC`); GREEN; observe the negative controls.
    3. Write `.planning/amendments/osf-amendment-r4-DRAFT.md` in the exemplar's structure. The
       PASTE body's lettered paragraphs:
       (a) the hypothesis under test, stated neutrally ("whether LD handling changes cross-trait colocalization calls");
       (b) the arms and why A1 ≠ "identity LD";
       (c) the data, with checksums and the measured n (EUR from the .fam; AFR 661/504), the BMI allele restoration with match-rate numbers, the trait types / sdY, and the A3-UKB panel class Carter chose (`ukb_native`);
       (d) the matched-variant rule and the D-02 fallback with dual reporting;
       (e) the estimands E1–E8 with formulas and the region statistic;
       (f) the decision thresholds, the classifier precedence (n_both → CI includes 0 → CI and McNemar agree → partial_rule) and the five branches, plus a table of the 8 partial_rule combinations with `‹CARTER-LOCK›` values;
       (g) the simulation design;
       (h) the known-answer results, including the SH2B3 provenance stated as measured;
       (i) the allele-orientation finding and fix with its before/after reporting commitment. This replaces the unposted correction note; phrase it as a methods finding;
       (j) HLA_6p21 / BMI_Xq24 inadmissibility; HLA_6p21 UKB fits are exploratory, reported descriptively, and produce no coloc row because no admissible 1000G comparator exists for the head-to-head (D-24);
       (k) the production policy (current corrected max_iter) disclosed vs the reproduction policy;
       (l) negative controls: the cosmetic and blood_group loci, the third set of 10 GWAS-null windows with its exact selection rule (250-kb tiles, exclusions, P ≥ 1e-5 in all 8 files, ≥ 200 variants, seed 20261021) and the ABO caveat; the QTL scope (`qtl_scope`) and its row count;
       (m) "What is not changing", with the analysis-code commit shas.
       Leave lock values as `‹CARTER-LOCK: …›` placeholders. Every number is copied from a committed
       file named inline in the Pre-Paste Reference (outside the extract). Keep the body ≤ ~2,700 words.
    4. Append a new dated entry at the END of `.planning/osf_deviations.md` headed
       "R4 amendment — DRAFTED, NOT POSTED", listing the deviations (BMI restoration; SH2B3
       provenance; E-2 fix; correction-v2 retired; production policy vs frozen effective max_iter;
       AFR substrate 661; third negative-control set added; UKB-native and QTL-scope decisions).
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - the test passes (FINAL/PUBLIC-only checks skip with an explicit reason while those files are absent); the three negative controls were observed
    - the LOG quotes the Wallace 2020 sentence with its source
    - `git diff -- .planning/osf_deviations.md | grep -c '^-[^-]'` prints 0 (append-only)
  </acceptance_criteria>
  <done>A complete draft built from measured, sourced facts, with a tested public extract.</done>
</task>

<task type="auto">
  <name>Task 2: Brief-blind adversarial review of the public extract against the code (Codex CLI); disposition; commit before the checkpoint</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - memory reference_codex_cli_for_gsd_review (invocation), feedback_internal_validation_cannot_catch_misspecified_premise
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    1. Produce the review input with `python -m ta_r4.extract_paste_block --in .planning/amendments/osf-amendment-r4-DRAFT.md --out data/r4/tmp/w4a_review_input.md`.
       Run Codex CLI non-interactively from the repo root. The prompt contains ONLY that extract and
       this instruction: "You are a hostile methods reviewer. For every factual or methodological
       claim in this pre-registration, find the code or data file in this repository that
       implements or supports it, and report any claim that the code contradicts, that is
       unsupported, or that is ambiguous enough to allow post-hoc choice. Cite file:line."
       Do NOT give it the CONTEXT, RESEARCH, LOG or any summary (brief-blind).
    2. Bank the raw output verbatim, byte-for-byte, in `ta-r4-W4-AMENDMENT-REVIEW-as-received.md`
       under a 3-line header (date, command, sha256 of the prompt). Then append a disposition
       table: finding → verified against the code (file:line) → fixed in the draft / rejected with
       evidence. Apply the fixes to the DRAFT only, then re-run `test_amendment_text.py`.
    3. Run §C with label `W4a-draft`, commit type `docs`, so Carter reviews committed files.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -c "^|" .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q && git status --porcelain -- .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <acceptance_criteria>
    - the review file holds the verbatim Codex output and a disposition table with one row per finding (count of findings == count of rows; both numbers pasted)
    - the amendment text test still passes; the DRAFT is committed (empty porcelain) and pushed
  </acceptance_criteria>
  <done>The public text has survived a brief-blind attack against the code and is committed for Carter.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: Carter locks the pre-registration parameters and approves the draft (human-action; auto-mode cannot pass it)</name>
  <what-built>The committed DRAFT amendment, its brief-blind review with dispositions, and the proposed lock values: p12_primary 5e-6 (sensitivity 1e-5), kappa_cut 0.6, n_both_min 10, partial_rule HETEROGENEOUS for each of the 4 keys (the 8 combinations in §(f)), and ukb_native as recorded at W2c.</what-built>
  <how-to-verify>
    1. Read the PASTE block of `.planning/amendments/osf-amendment-r4-DRAFT.md` and the disposition table in `ta-r4-W4-AMENDMENT-REVIEW-as-received.md`.
    2. Decide every lock value. These define the outcome branches and must be fixed before the data exist (D-26).
  </how-to-verify>
  <resume-signal>Carter replies with the first line exactly `carter-approved YYYY-MM-DD`, then these lines: `p12_primary: <value>`, `kappa_cut: <value>`, `n_both_min: <value>`, `partial_rule.ci_pos_mcnemar_ns: <branch>`, `partial_rule.ci_pos_mcnemar_opposite: <branch>`, `partial_rule.ci_neg_mcnemar_ns: <branch>`, `partial_rule.ci_neg_mcnemar_opposite: <branch>`, `ukb_native: <native|hm3>`, `draft: approved`. Any other reply, including a bare "approved", means WAIT. A reply asking for text edits is also WAIT: apply the edits to the DRAFT only, re-run the text test, commit, and re-present this checkpoint.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W4a-T3.yaml, .planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>
    Present the draft, the dispositions and the proposed values. Save the reply byte-for-byte to
    `data/r4/tmp/signoff_W4a-T3.txt` and run
    `cd src/python && $PY -m ta_r4.signoff record W4a-T3 --raw-file ../../data/r4/tmp/signoff_W4a-T3.txt --min-date <date of the W4a-draft commit>`.
    Non-zero exit → WAIT (print the message, re-present, write nothing). Never infer, default or
    complete any value, and never log an auto-generated response as Carter's sign-off.
    If the recorded `ukb_native` differs from `config/ta_r4/review_decisions.yaml`, STOP and hand
    back: W2d must be re-run for the new choice before the lock (record this in the LOG).
    On success, append `## <date> — DEC-<date>-ta-r4-prereg-locks: R4 pre-registration lock values (Carter)`
    to DECISIONS.md quoting the reply verbatim and citing `signoffs/W4a-T3.yaml`; log it; commit the
    three files with explicit paths; push.
  </action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.signoff verify W4a-T3 && cd ../.. && grep -c "ta-r4-prereg-locks" .planning/DECISIONS.md</automated></verify>
  <acceptance_criteria>
    - `signoff verify W4a-T3` exits 0; DECISIONS.md has exactly one `ta-r4-prereg-locks` entry quoting Carter's reply verbatim
    - the recorded ukb_native equals review_decisions.yaml
  </acceptance_criteria>
  <done>Carter's lock values are recorded and machine-checkable; W4b applies them.</done>
  <read_first>
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md
    - src/python/ta_r4/signoff.py (SCHEMAS["W4a-T3"])
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → public OSF text | anything inside the extract becomes public and irreversible |
| auto-mode → lock values | an auto-selected option must not fix the decision rule |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W4a-01 | Information disclosure | internal paths/checklists in public text | mitigate | the public text is the deterministic extract; internal-content scan over the whole extract with a negative control |
| T-r4-W4a-02 | Information disclosure | framing violations in public text | mitigate | banned-word scan over the whole extract with a negative control |
| T-r4-W4a-03 | Tampering | a mis-specified premise in the public text | mitigate | brief-blind Codex review of the extract against the code; dispositions recorded |
| T-r4-W4a-04 | Spoofing | lock values without Carter | mitigate | `checkpoint:human-action`; `carter-approved YYYY-MM-DD` + all required keys parsed by ta_r4.signoff; test_signoffs ties locked configs to this sign-off |
</threat_model>

<verification>
The draft's public extract passed the text tests and a brief-blind review. Carter's lock values are
recorded verbatim through a validated sign-off.
</verification>

<success_criteria>
Every pre-registration decision is written from measured facts and frozen code and fixed by Carter
before any production result exists.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-SUMMARY.md`
</output>
