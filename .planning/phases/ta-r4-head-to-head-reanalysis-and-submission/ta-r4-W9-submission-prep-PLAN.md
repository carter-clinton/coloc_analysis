---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 25
slug: W9-submission-prep
type: execute
wave: 25
depends_on: ["ta-r4-W8b-adversarial-review"]
files_modified:
  - src/python/ta_r4/render_manuscript.py
  - tests/ta_r4/test_render_manuscript.py
  - docs/manuscript/r4/submission/venue_overlay.yaml
  - docs/manuscript/r4/submission/requirements.tsv
  - docs/manuscript/r4/submission/manuscript_venue.md
  - docs/manuscript/r4/submission/cover_letter.md
  - docs/manuscript/r4/submission/data_availability.md
  - docs/manuscript/r4/submission/code_availability.md
  - docs/manuscript/r4/submission/package.zip
  - .planning/amendments/osf-r4-results-record-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/submission_package_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W9-T1.yaml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W9-T4.yaml
  - .planning/DECISIONS.md
  - .planning/osf_deviations.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/ROADMAP.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "This plan starts only if `python -m ta_r4.signoff verify W8b-T3` exits 0"
    - "The venue is chosen by Carter AFTER results (D-09) through a checkpoint:human-action; the reply must parse as `carter-approved YYYY-MM-DD` + `venue:`; it is recorded in signoffs/W9-T1.yaml and quoted verbatim in a DEC entry (B1)"
    - "Code-level sentinels (kept for W9 per checker B1): render_manuscript --venue-overlay refuses unless signoffs/W9-T1.yaml verifies; test_signoffs fails if venue_overlay.yaml exists without a valid W9-T1, or if the ROADMAP W9 line is checked without a valid W9-T4"
    - "A venue-formatted manuscript is rendered from the same template (venue overlay for section order/limits only; no number changes), with the measured word, abstract and figure counts checked against the venue's fetched author guidelines"
    - "A cover-letter draft, data and code availability statements, and an OSF R4 results-record draft exist; no preprint is prepared (DEC-2026-08-12-no-preprint)"
    - "A submission package is assembled with a sha256 manifest; the executor NEVER submits and NEVER posts to OSF"
    - "The phase is marked complete only through a second checkpoint:human-action whose reply parses as `carter-approved YYYY-MM-DD` + journal, submitted_date, manuscript_id, osf_url"
  artifacts:
    - path: "docs/manuscript/r4/submission/manuscript_venue.md"
      provides: "venue-formatted manuscript rendered from the template"
    - path: "docs/manuscript/r4/submission/package.zip"
      provides: "the submission package (members + zip sha256 in the manifest)"
    - path: ".planning/amendments/osf-r4-results-record-DRAFT.md"
      provides: "the results record Carter posts on osf.io/az52u"
  key_links:
    - from: "docs/manuscript/r4/id-vs-ref-LD-r4.template.md"
      to: "docs/manuscript/r4/submission/manuscript_venue.md"
      via: "render_manuscript --venue-overlay docs/manuscript/r4/submission/venue_overlay.yaml (requires signoffs/W9-T1.yaml)"
      pattern: "venue-overlay"
---

<objective>
Wave 9 prepares, but does not perform, the journal submission and the OSF results posting. Carter
chooses the venue now that results exist. The package is assembled and checksum-manifested. The
phase closes only on Carter's recorded confirmation that he has submitted.

Purpose: D-09 (venue after results; neutral format until now; no preprint), D-05/REQ-OSF-PREREG (public results record), §B.12, checker B1.
Output: venue-formatted package, cover letter, OSF results draft, sign-offs and DEC entries.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@docs/manuscript/id-vs-ref-LD-r4.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W7-RESULTS.md

<interfaces>
The 2026-08-12 venue ladder (DEC-2026-08-12-*) is on record but NOT acted on (D-09); show it to Carter as context only
Renderer: python -m ta_r4.render_manuscript (W8a); memory track_a_submission_in_progress / feedback_stop_asking_track_a (do not mark complete until Carter confirms)
Sign-offs: python -m ta_r4.signoff verify W8b-T3 / record W9-T1 / record W9-T4 (SCHEMAS in src/python/ta_r4/signoff.py)
</interfaces>
</context>

<tasks>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 1: Carter chooses the venue (human-action; auto-mode cannot pass it)</name>
  <what-built>The approved submission candidate (W8b), the branch outcome, the measured word count, and the 2026-08-12 ladder for reference only. The executor makes no recommendation unless Carter asks.</what-built>
  <how-to-verify>
    0. (Executor, before presenting) `cd src/python && $PY -m ta_r4.signoff verify W8b-T3` must exit 0; otherwise STOP.
    1. Choose the journal.
  </how-to-verify>
  <resume-signal>Carter replies with the first line exactly `carter-approved YYYY-MM-DD`, then `venue: <journal name>`. Any other reply, including a bare "approved", means WAIT: re-present and record nothing.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W9-T1.yaml, .planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>
    Sign-off integrity (§B.15): the executor never authors, types or completes any
    `carter-approved` text and never writes signoffs/*.yaml except via `python -m ta_r4.signoff record`.
    The raw file is written only from the resume payload the orchestrator passes, which must be
    Carter's message pasted verbatim (never a summary, paraphrase or auto response). The SUMMARY
    quotes the resume payload next to the recorded raw_sha256.

    Save the reply byte-for-byte to `data/r4/tmp/signoff_W9-T1.txt` and run
    `cd src/python && $PY -m ta_r4.signoff record W9-T1 --raw-file ../../data/r4/tmp/signoff_W9-T1.txt --min-date <date of the W8b sign-off>`.
    Non-zero exit → WAIT. Never construct a reply or log an auto-generated response as Carter's
    sign-off. On success, append `DEC-<date>-ta-r4-venue` quoting the reply verbatim and citing the
    sign-off file; log it; commit the three files with explicit paths; push.
  </action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.signoff verify W9-T1 && cd ../.. && grep -c "ta-r4-venue" .planning/DECISIONS.md</automated></verify>
  <acceptance_criteria>
    - `signoff verify W9-T1` exits 0; exactly one `ta-r4-venue` DEC entry quoting Carter's reply
    - the SUMMARY quotes the resume payload verbatim next to the recorded raw_sha256
  </acceptance_criteria>
  <done>The venue is chosen by Carter and recorded in a machine-checkable sign-off.</done>
  <read_first>
    - .planning/DECISIONS.md (DEC-2026-08-12-* venue entries, for context only)
  </read_first>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Venue overlay (sign-off-gated), formatting, cover letter, statements, OSF results draft, package with sha256</name>
  <files>src/python/ta_r4/render_manuscript.py, tests/ta_r4/test_render_manuscript.py, docs/manuscript/r4/submission/venue_overlay.yaml, docs/manuscript/r4/submission/requirements.tsv, docs/manuscript/r4/submission/manuscript_venue.md, docs/manuscript/r4/submission/cover_letter.md, docs/manuscript/r4/submission/data_availability.md, docs/manuscript/r4/submission/code_availability.md, docs/manuscript/r4/submission/package.zip, .planning/amendments/osf-r4-results-record-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/submission_package_sha256.tsv, .planning/osf_deviations.md</files>
  <read_first>
    - the venue's author guidelines (WebFetch the journal's official "submission guidelines" page; record the URL and fetch date)
    - docs/manuscript/r4/id-vs-ref-LD-r4.template.md; src/python/ta_r4/render_manuscript.py
    - .planning/amendments/osf-amendment-r4-FINAL.md (the results record must reference it)
  </read_first>
  <behavior>
    - `--venue-overlay` (YAML: section order and headings only) re-orders/renames sections; the set of resolved placeholder values is identical to the neutral render (test)
    - `--venue-overlay` refuses (exit 1, message naming W9-T1) unless `verify_signoff("W9-T1")` succeeds; negative control with a tmp signoff dir lacking W9-T1
    - an overlay key outside {section_order, headings, venue_slug} is rejected (numbers cannot be changed through it)
  </behavior>
  <action>
    1. Tests RED; add `--venue-overlay` to `render_manuscript.py`; GREEN; negative controls observed.
    2. From the fetched guidelines, write `docs/manuscript/r4/submission/requirements.tsv`
       (limit name, value, source URL) and `venue_overlay.yaml` (venue name from W9-T1). Render
       `manuscript_venue.md`. Measure word, abstract, figure and table counts against
       `requirements.tsv`. A limit violation is listed for Carter, not silently cut.
    3. Draft `cover_letter.md` (framing rule: original, hypothesis-driven research; state the
       analysis lock commit, never "pre-registered on OSF" for R4 (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf); no "revision" language), `data_availability.md` (every
       source with licence, from `config/ta_r4/data_sources.yaml`), and `code_availability.md`
       (GitHub repo + commit, OSF).
    4. Draft `.planning/amendments/osf-r4-results-record-DRAFT.md`: the pre-registered branch per
       contrast (rendered from the tables), the deviations list, and links to the amendment. Add a
       "DRAFTED — NOT POSTED" entry to `.planning/osf_deviations.md` (append-only).
    5. Zip the package (manuscript_venue.md, the 10 figure files, the 17 tables, the supplementary
       note, cover letter, statements) to `docs/manuscript/r4/submission/package.zip`. Write
       `submission_package_sha256.tsv` with every member's sha256, the zip's own sha256 and the build UTC.
    6. Assert no preprint artifact exists (`find docs/manuscript/r4/submission -iname '*preprint*' | wc -l` prints 0).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ls docs/manuscript/r4/submission/ && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_manuscript_r4.py tests/ta_r4/test_render_manuscript.py tests/ta_r4/test_signoffs.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `requirements.tsv` has a source URL per row; the measured counts vs limits table is in the SUMMARY
    - the venue render has the same placeholder values as the neutral render (test passes); the unsigned-overlay negative control fails as designed; test_signoffs passes with the venue sentinel live
    - `unzip -l` of the package lists exactly the manifest's members; the zip sha256 is in the manifest
    - `find docs/manuscript/r4/submission -iname '*preprint*' | wc -l` prints 0
  </acceptance_criteria>
  <done>The package is ready for Carter to submit.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W9 pre-submission)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W9`, commit type `docs`. STATE.md says "package ready — awaiting Carter's submission". Do NOT mark the phase complete.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git status --porcelain -- docs/manuscript/r4/submission .planning/amendments/osf-r4-results-record-DRAFT.md && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - committed (empty porcelain); pushed
  </acceptance_criteria>
  <done>The package is committed and pushed.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 4: Carter posts the OSF results record and submits the manuscript (human-action; auto-mode cannot pass it)</name>
  <what-built>The committed submission package and the OSF results-record draft.</what-built>
  <how-to-verify>
    1. Submit the package to the journal and post the results record on osf.io/az52u (both Carter's alone, §B.12).
    2. Reply as below.
  </how-to-verify>
  <resume-signal>Carter replies with the first line exactly `carter-approved YYYY-MM-DD`, then `journal: <name>`, `submitted_date: <YYYY-MM-DD>`, `manuscript_id: <id>`, `osf_url: <url>`. Any other reply, including a bare "approved", means WAIT: the phase stays open.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W9-T4.yaml, .planning/DECISIONS.md, .planning/osf_deviations.md, .planning/ROADMAP.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>
    Sign-off integrity (§B.15): the executor never authors, types or completes any
    `carter-approved` text and never writes signoffs/*.yaml except via `python -m ta_r4.signoff record`.
    The raw file is written only from the resume payload the orchestrator passes, which must be
    Carter's message pasted verbatim (never a summary, paraphrase or auto response). The SUMMARY
    quotes the resume payload next to the recorded raw_sha256.

    Save the reply byte-for-byte to `data/r4/tmp/signoff_W9-T4.txt` and run
    `cd src/python && $PY -m ta_r4.signoff record W9-T4 --raw-file ../../data/r4/tmp/signoff_W9-T4.txt --min-date <date of the W9 commit>`.
    Non-zero exit → WAIT. On success:
    - append `DEC-<date>-ta-r4-submitted`, quoting the reply verbatim and citing the sign-off;
    - add the OSF URL to the R4 entry in osf_deviations.md (append-only);
    - mark the phase plans complete in ROADMAP.md (test_signoffs now requires the valid W9-T4);
    - update STATE.md; run `test_signoffs.py`;
    - commit with explicit paths and push.
  </action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.signoff verify W9-T4 && cd ../.. && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_signoffs.py -q && grep -c "ta-r4-submitted" .planning/DECISIONS.md</automated></verify>
  <acceptance_criteria>
    - `signoff verify W9-T4` exits 0; test_signoffs passes with the ROADMAP sentinel live; exactly one `ta-r4-submitted` DEC entry quoting Carter; ROADMAP/STATE updated; pushed
    - the SUMMARY quotes the resume payload verbatim next to the recorded raw_sha256
  </acceptance_criteria>
  <done>Carter has submitted; the phase is closed on a recorded, machine-checked confirmation.</done>
  <read_first>
    - docs/manuscript/r4/submission/package.zip (members via the manifest)
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → journal / OSF | irreversible public actions (Carter only) |
| auto-mode → venue / completion | an auto-selected option must not choose a venue or close the phase |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W9-01 | Elevation of privilege | auto-submission / auto-venue | mitigate | the executor never submits or posts; both checkpoints are `checkpoint:human-action` with `carter-approved` tokens; the venue overlay and ROADMAP completion require valid sign-offs in code |
| T-r4-W9-02 | Tampering | numbers changed during formatting | mitigate | the venue overlay accepts only section order/headings; a test asserts identical placeholder values |
| T-r4-W9-03 | Tampering | package contents | mitigate | sha256 manifest of members and the zip |
</threat_model>

<verification>
Venue recorded from Carter's validated sign-off. Package manifested. No preprint. The phase closes only on Carter's validated confirmation.
</verification>

<success_criteria>
Carter holds a verified, pre-registration-faithful submission package, and the record shows
exactly what he chose and submitted.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W9-submission-prep-SUMMARY.md`
</output>
