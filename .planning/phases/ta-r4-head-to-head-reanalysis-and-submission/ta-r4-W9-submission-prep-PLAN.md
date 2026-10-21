---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 22
slug: W9-submission-prep
type: execute
wave: 22
depends_on: ["W8b"]
files_modified:
  - docs/manuscript/r4/submission/
  - .planning/amendments/osf-r4-results-record-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/submission_package_sha256.tsv
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
    - "The venue is chosen by Carter AFTER results (D-09); the decision checkpoint's first option is WAIT; the choice is recorded verbatim in a DEC entry"
    - "A venue-formatted manuscript is rendered from the same template (venue overlay for section order/limits only; no number changes), with the measured word, abstract and figure counts checked against the venue's fetched author guidelines"
    - "A cover-letter draft, data and code availability statements, and an OSF R4 results-record draft exist; no preprint is prepared (DEC-2026-08-12-no-preprint)"
    - "A submission package (manuscript, figures, tables, supplementary note, cover letter) is assembled with a sha256 manifest; the executor NEVER submits and NEVER posts to OSF"
    - "The phase is marked complete only when Carter confirms the submission (the final checkpoint's first option is WAIT)"
  artifacts:
    - path: "docs/manuscript/r4/submission/"
      provides: "venue-formatted manuscript, cover letter, statements, package zip"
    - path: ".planning/amendments/osf-r4-results-record-DRAFT.md"
      provides: "the results record Carter posts on osf.io/az52u"
  key_links:
    - from: "docs/manuscript/r4/id-vs-ref-LD-r4.template.md"
      to: "docs/manuscript/r4/submission/<venue>/manuscript.md"
      via: "render_manuscript with a venue overlay"
      pattern: "render_manuscript"
---

<objective>
Wave 9 prepares, but does not perform, the journal submission and the OSF results posting. Carter
chooses the venue now that results exist. The package is assembled and checksum-manifested. The
phase closes only on Carter's confirmation that he has submitted.

Purpose: D-09 (venue after results; neutral format until now; no preprint), D-05/REQ-OSF-PREREG (public results record), §B.12.
Output: venue-formatted package, cover letter, OSF results draft, DEC entries.
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
</interfaces>
</context>

<tasks>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 1: Carter chooses the venue</name>
  <decision>Which journal receives the R4 manuscript?</decision>
  <context>D-09: the venue is decided after results. The 2026-08-12 ladder is on record but not binding. The executor presents the branch outcome, the word count and the ladder for reference only, and makes no recommendation unless Carter asks.</context>
  <options>
    <option id="option-wait">
      <name>WAIT — stop and hand back to Carter (FIRST; the default under auto-mode)</name>
      <pros>No venue is chosen without Carter.</pros>
      <cons>The chain pauses.</cons>
    </option>
    <option id="option-venue">
      <name>Carter names the venue</name>
      <pros>Formatting can proceed.</pros>
      <cons>Requires Carter's explicit journal name. Anything else is treated as WAIT.</cons>
    </option>
  </options>
  <resume-signal>"venue: <journal name>". Anything else = WAIT.</resume-signal>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>On "venue: …", append `DEC-<date>-ta-r4-venue` quoting Carter verbatim, log it, commit with explicit paths, and push.</action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -c "ta-r4-venue" .planning/DECISIONS.md</automated></verify>
  <acceptance_criteria>
    - exactly one `ta-r4-venue` DEC entry quoting Carter's journal name
  </acceptance_criteria>
  <done>The venue is chosen by Carter.</done>
  <read_first>
    - .planning/DECISIONS.md (DEC-2026-08-12-* venue entries, for context only)
  </read_first>
</task>

<task type="auto">
  <name>Task 2: Venue formatting, cover letter, statements, OSF results draft, package with sha256</name>
  <files>docs/manuscript/r4/submission/, .planning/amendments/osf-r4-results-record-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/submission_package_sha256.tsv, .planning/osf_deviations.md</files>
  <read_first>
    - the venue's author guidelines (WebFetch the journal's official "submission guidelines" page; record the URL and fetch date)
    - docs/manuscript/r4/id-vs-ref-LD-r4.template.md; src/python/ta_r4/render_manuscript.py
    - .planning/amendments/osf-amendment-r4-FINAL.md (the results record must reference it)
  </read_first>
  <action>
    1. From the fetched guidelines, write `docs/manuscript/r4/submission/<venue_slug>/requirements.tsv`
       (limit name, value, source URL). Render a venue copy with a venue overlay (section order and
       headings only, via a `--venue-overlay` YAML read by the renderer; add that flag if absent,
       with a test that the rendered numbers are identical to the neutral render). Measure word,
       abstract, figure and table counts against `requirements.tsv`. A limit violation is listed
       for Carter, not silently cut.
    2. Draft `cover_letter.md` (framing rule: original, hypothesis-driven research; state the
       pre-registration with OSF links; no "revision" language), `data_availability.md` (every
       source with licence, from `config/ta_r4/data_sources.yaml`), and `code_availability.md`
       (GitHub repo + commit, OSF).
    3. Draft `.planning/amendments/osf-r4-results-record-DRAFT.md`: the pre-registered branch per
       contrast (rendered from the tables), the deviations list, and links to the amendment. Add a
       "DRAFTED — NOT POSTED" entry to `.planning/osf_deviations.md` (append-only).
    4. Zip the package (manuscript, figures, tables, supplementary note, cover letter, statements)
       to `docs/manuscript/r4/submission/<venue_slug>/package_<UTC>.zip`. Write
       `submission_package_sha256.tsv` with every member's sha256 and the zip's own sha256.
    5. Assert no preprint artifact exists (no file or directory named `*preprint*` under
       docs/manuscript/r4/submission).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ls docs/manuscript/r4/submission/*/ && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_manuscript_r4.py tests/ta_r4/test_render_manuscript.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `requirements.tsv` has a source URL per row; the measured counts vs limits table is in the SUMMARY
    - the venue render has the same placeholder values as the neutral render (test passes)
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

<task type="checkpoint:decision" gate="blocking">
  <name>Task 4: Carter posts the OSF results record and submits the manuscript</name>
  <decision>Has Carter posted the OSF R4 results record and submitted the manuscript?</decision>
  <context>Both are Carter's alone (§B.12). The phase is complete only on his confirmation (memory track_a_submission_in_progress).</context>
  <options>
    <option id="option-wait">
      <name>WAIT — not yet submitted; stop here (FIRST; the default under auto-mode)</name>
      <pros>Nothing is marked complete prematurely.</pros>
      <cons>The phase stays open.</cons>
    </option>
    <option id="option-submitted">
      <name>Carter confirms the submission (journal, date, manuscript id) and the OSF results-record URL</name>
      <pros>The phase can close.</pros>
      <cons>Requires all four facts from Carter. Anything less is treated as WAIT.</cons>
    </option>
  </options>
  <resume-signal>"submitted: <journal>, <date>, <manuscript id>; osf: <url>". Anything else = WAIT.</resume-signal>
  <files>.planning/DECISIONS.md, .planning/osf_deviations.md, .planning/ROADMAP.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>On a complete reply:
    - append `DEC-<date>-ta-r4-submitted`, quoting Carter;
    - add the OSF URL to the R4 entry in osf_deviations.md (append-only);
    - mark the phase plans complete in ROADMAP.md;
    - update STATE.md;
    - commit with explicit paths and push.</action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -c "ta-r4-submitted" .planning/DECISIONS.md</automated></verify>
  <acceptance_criteria>
    - exactly one `ta-r4-submitted` DEC entry quoting Carter; ROADMAP/STATE updated; pushed
  </acceptance_criteria>
  <done>Carter has submitted; the phase is closed.</done>
  <read_first>
    - docs/manuscript/r4/submission/
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → journal / OSF | irreversible public actions (Carter only) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W9-01 | Elevation of privilege | auto-submission | mitigate | the executor never submits or posts; both decisions list WAIT first; completion requires Carter's facts |
| T-r4-W9-02 | Tampering | numbers changed during formatting | mitigate | the venue overlay changes section order only; a test asserts identical placeholder values |
| T-r4-W9-03 | Tampering | package contents | mitigate | sha256 manifest of members and the zip |
</threat_model>

<verification>
Venue recorded from Carter. Package manifested. No preprint. The phase closes only on Carter's confirmation.
</verification>

<success_criteria>
Carter holds a verified, pre-registration-faithful submission package, and the record shows
exactly what he chose and submitted.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W9-submission-prep-SUMMARY.md`
</output>
