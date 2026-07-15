---
phase: m3-aou-afr-ld-panel-build
plan: 07a
type: execute
wave: 1
depends_on: []
tags: [ld, occlusion, osf-prereg, red-first, tdd, aou, afr]
files_modified:
  # Task 1 is a PRE-CLOSED provenance record (gate cleared at ac4c990) — the doc below
  # already exists and is POSTED; the executor does NOT create or modify it.
  - .planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md  # READ-ONLY (pre-existing)
  - tests/m3/test_occlusion_span_filter.py
  - tests/m3/test_occlusion_manifest.py
  - tests/m3/test_occlusion_present_rate_scan.py
  - tests/m3/test_occlusion_lockstep_drop.py
  - tests/m3/test_run_native_ld_panel.py
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI
  - REQ-AOU-LD-VALIDATION

must_haves:
  truths:
    - "The OSF gate is honored — SATISFIED 2026-07-10 (pre-closed; see Task 1): `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` exists describing the panel overlapping-variant policy = exclusion + provenance in lockstep (withdrawing the `tcujq` NaN→0 conditioning rather than zeroing), it is POSTED to osf.io/az52u (2026-07-10T13:32:22Z), and it is RECORDED in-repo at commit `ac4c990` + git tag `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10` — before ANY code plan (07b/07c) begins (mirrors the `tcujq` / 999.1 OSF-gate precedent). This plan BLOCKS 07b and 07c via the depends_on chain."
    - "Wave 0 RED scaffolds exist and FAIL RED for the RIGHT reason: the 4 new test files (test_occlusion_span_filter/manifest/present_rate_scan/lockstep_drop) + the extended test_run_native_ld_panel.py COLLECT cleanly (impl modules imported INSIDE test bodies, not at module top) and FAIL as test/assert failures (ModuleNotFoundError raised at call-time), NOT as pytest collection errors."
    - "The synthetic region-1 `.bim` fixture helper `_REGION1_BIM_ROWS` reproduces the geometry verdict's coordinates (7 deletions of 60/29/7/31/31/17/29 bp occluding neighbours) so the downstream 07b filter must return EXACTLY {1980475, 5733487, 5922718, 7492693, 8375822} (5 occluded; the 5922716/5922718/5922724 tangle collapses to 5922718)."
    - "The pair-4 second-order tangle is pinned (SETTLED, Seth 5/5 vs geometry verdict `4543dcf4…`): SNP 5922718 is attributed to the UPSTREAM DEL 5922716 (not the downstream DEL 5922724), and dropping 5922718 collapses the 5922716/5922718/5922724 3-record tangle. The SETTLED region-1 REAL-window known-answer oracle `{10328, 44784, 46714, 59097, 66730}` + the 7-deletion REF-span inventory (60/29/7/31/31/17/29 bp) is documented as the answer the detector must reproduce at the GATED real-`.bim` validation (Seth's full prototype is a read-only reference for the executor, not committed)."
  artifacts:
    - path: ".planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md"
      provides: "The scoped OSF amendment-update (the HARD GATE artifact, PRE-EXISTING + POSTED + RECORDED at ac4c990): withdraws the tcujq NaN→0 conditioning and pre-registers occlusion exclude-in-lockstep + mandatory provenance manifest. Carter-authored, byte-identical to the file posted to osf.io/az52u — the executor MUST NOT edit it (an in-repo edit would diverge the project copy from the posted bytes)."
      contains: "exclusion"
    - path: "tests/m3/test_occlusion_span_filter.py"
      provides: "RED-first occlusion-rule tests + the region-1 `.bim` fixture helper (5 occluded), boundary/SNV/insertion cases; function-local import so it collects clean"
      contains: "detect_occluded_variants"
    - path: "tests/m3/test_occlusion_manifest.py"
      provides: "RED-first manifest schema + ref_span + reason + resume-safe dedup + aggregate rollup + liftover (skip if chain absent)"
    - path: "tests/m3/test_occlusion_present_rate_scan.py"
      provides: "RED-first present-rate k/n on synthetic sumstats fixtures"
    - path: "tests/m3/test_occlusion_lockstep_drop.py"
      provides: "RED-first: drop = exactly manifest (CHR,POS); idempotent; non-occluded rows untouched"
    - path: "tests/m3/test_run_native_ld_panel.py"
      provides: "Extended _MockPlink honors --exclude + RED tests for occlusion integration (no NaN) + n_dropped_occluded/n_dropped_monomorphic split"
      contains: "exclude"
---

<objective>
Plan **07a of the m3-07 split** (OSF gate + Wave 0 RED scaffold). Two tasks:
(1) the OSF pre-registration HARD GATE — pre-register the scoped panel overlapping-variant
policy amendment-update (exclusion + provenance, never zeroing) BEFORE any fix code lands;
(2) author ALL the RED-first pytest scaffolds + the synthetic region-1 `.bim` fixture helper.

This plan is the ROOT of the m3-07 dependency chain: **07b depends_on 07a; 07c depends_on 07b.**
The OSF gate (Task 1) blocks EVERYTHING downstream through that chain.

The SCIENCE is settled and LOCKED in the byte-verified amendment doc-set (mechanism =
overlapping-deletion occlusion, `m3_region1_nan_geometry_verdict.md` `4543dcf4…`; policy =
exclude-in-lockstep + provenance, `m3_panel_occlusion_policy_decision.md` `42d70167…`; join
impact = `m3_region1_occlusion_hinge_check.md`). Do NOT re-litigate.

Purpose: pre-register the deviation (never zero, always exclude+provenance) and stand up the
failing tests that define the behavior 07b/07c must deliver. `NaN→0` is DEAD; m3-06
`condition_ld_matrix.py` stays FROZEN/HELD and is NOT touched.

Output: the OSF amendment-update doc + 4 new test files + the extended driver test (all RED).

⚠ **EXECUTION ORDER (hard):** Task 1 is the OSF pre-registration HARD GATE. It BLOCKS Task 2
of this plan AND all of 07b/07c. No test/impl code lands until the amendment-update is POSTED
to OSF and its file id/SHA-256/git tag are RECORDED.

**STATUS 2026-07-10 — GATE CLEARED:** the amendment-update was POSTED 2026-07-10T13:32:22Z and
recorded in-repo (tag `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`, commit `ac4c990`).
Task 1 STAYS in the plan as the provenance record (do not delete); 07b/07c are now unblocked.

**RECONCILED 2026-07-15 — READ THIS BEFORE EXECUTING.** Task 1 was authored pre-post and guessed both the amendment
filename and tag. Carter authored and posted the real doc himself under DIFFERENT names; the placeholder
`osf-amendment-panel-occlusion-exclusion-2026-07-10.md` / `PANEL-OCCLUSION-OSF-AMENDMENT-POSTED-2026-07-10` NEVER
EXISTED. Task 1 is now **PRE-CLOSED**: its only remaining job is a read-only confirmation of the real artifacts.
**The executable scope of this plan is Task 2 ONLY.** The as-posted doc does not contain the literal phrase
"never zeroing" nor the anchors `4543dcf4…`/`42d70167…` (it names its supporting docs by filename); the anchors are
verified against the SOURCE docs, where they hold byte-exactly. Do not "correct" the amendment doc to match the plan —
the plan was corrected to match the posted reality.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/amendments/m3_region1_nan_geometry_verdict.md
@.planning/amendments/m3_panel_occlusion_policy_decision.md
@.planning/amendments/m3_region1_occlusion_hinge_check.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-07-RESEARCH.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-07-VALIDATION.md

# The amendment doc-set is the SPEC OF RECORD for the SCIENCE (do NOT re-derive). m3-07-RESEARCH.md §5
# has the region-1 .bim fixture table + task-shaped RED tests. m3-06-W6-...-PLAN.md is the convention template.

<interfaces>
<!-- Contracts the RED tests encode. Extracted from the working tree @ m3-W2-aou-deltas. -->

The `.bim` REF-span crux is RESOLVED (RESEARCH §2). From src/python/plink_ld_to_npz.py:105-119 (load_bim — FROZEN):
```
.bim columns: [chr, snp_id, cm, bp, A1, A2]. Under hl.export_plink: A1 = ALT (col 5, parts[4]);
A2 = REF (col 6, parts[5]). canonical vid = {chr}:{bp}:{A2}:{A1} = chr:pos:REF:ALT.
For a row: POS=int(parts[3]); REF=parts[5]; ALT=parts[4]; len(REF)=len(parts[5]).
Deletion: len(REF)>1; reference footprint = [POS, POS + len(REF) − 1].
```

THE DETERMINISTIC OCCLUSION RULE the tests pin (RESOLVED — conservative, RESEARCH §2/§7):
```
V is OCCLUDED iff ∃ window variant D with len(REF_D)>1 and POS_D < POS_V ≤ POS_D+len(REF_D)−1
(computed over the ORIGINAL window). Insertions/SNVs never occlude. Exclude the downstream occluded V.
```

The region-1 `.bim` fixture (RESEARCH §5 — deletions get a multi-char A2/REF of the exact span length):
```
bp=1980423 del1 A1=G A2=<60ch> ; bp=1980475 snpA A1=A A2=A  (occluded)
bp=5733474 del2 A1=G A2=<29ch> ; bp=5733487 snpB A1=A A2=A  (occluded)
bp=5922716 del3 A1=G A2=<7ch>  ; bp=5922718 snpC A1=A A2=A  (occluded by del3)
bp=5922724 del4 A1=G A2=<31ch>
bp=7492679 del5 A1=G A2=<31ch> ; bp=7492693 del6 A1=G A2=<17ch> (occluded by del5)
bp=8375794 del7 A1=G A2=<29ch> ; bp=8375822 snpD A1=A A2=A  (occluded)
```
Variant ids = f"1:{bp}:{A2}:{A1}" (production chr:pos:ref:alt). Expected occluded set = the 5 downstream members;
edges mark 5922718↔5922724 as disjoint/second-order.
PAIR-4 SECOND-ORDER (SETTLED, Seth 5/5 vs geometry verdict `4543dcf4…`): SNP 5922718 is occluded by the UPSTREAM
DEL 5922716 (its len(REF) span covers 5922718), NOT by the downstream DEL 5922724 — the detector MUST attribute the
occlusion to 5922716 and drop 5922718, collapsing the 3-record 5922716/5922718/5922724 tangle with the single drop.
SETTLED region-1 REAL-window oracle (for the GATED real-`.bim` validation, NOT the synthetic-fixture unit):
occluded set `{10328, 44784, 46714, 59097, 66730}`; 7-deletion REF-span inventory 60/29/7/31/31/17/29 bp; 0 same-position
(`bcftools norm -m` fixes none). Seth's full detector prototype exists as a READ-ONLY reference for the executor once the
plan lands — NOT for commit (it needs the real `.bim` loader + the GSD RED-first TDD flow; build the detector test-first).

Liftover anchors (reuse ld_npz_to_rds.R:167-183, chain data/external/liftover/hg38ToHg19.over.chain.gz, pos−1 in/+1 out):
5922716→5982776, 5922718→5982778, 5922724→5982784.

AFR harmonized sumstats header (public GRCh37): `CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD`.
Panel↔sumstats join (snp_id_bridge.R:107-121): (CHR,POS)-only; drop-only, no re-key.

Test conventions (tests/m3/test_run_native_ld_panel.py:48-163 + conftest.py): `_write_bim(path, rows)` where a row is
(chr, snp_id, cm, bp, A1, A2), A1=ALT/A2=REF (indel -> multi-char A2); `_MockPlink` models --mac/--write-snplist and
records every argv; PROJECT_ROOT via Path(__file__).resolve().parents[2]; src/python on sys.path; env =
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest (py3.11, numpy/pandas, no hail).
</interfaces>
</context>

<tasks>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 1 (HARD GATE — BLOCKS Task 2 + all of 07b/07c): OSF pre-registration of the scoped panel overlapping-variant policy amendment-update</name>
  <read_first>
    .planning/amendments/m3_panel_occlusion_policy_decision.md (the settled policy — the doc restates it),
    .planning/amendments/m3_region1_nan_geometry_verdict.md (the mechanism it pre-registers),
    .planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md (the tcujq / 999.1 OSF-gate PRECEDENT — mirror its shape + posting discipline).
  </read_first>
  <files>.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md (READ-ONLY — pre-existing, posted)</files>
  <action>
    ⛔ **PRE-CLOSED — NO ACTION REQUIRED. DO NOT EXECUTE THIS TASK.** The gate it guards is already CLEARED.

    RECONCILED 2026-07-15: this task was authored BEFORE the gate cleared, and it anticipated that Claude would draft a
    doc named `osf-amendment-panel-occlusion-exclusion-2026-07-10.md` for Carter to post under tag
    `PANEL-OCCLUSION-OSF-AMENDMENT-POSTED-2026-07-10`. That is NOT what happened. Carter AUTHORED the amendment-update
    himself as `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`, POSTED it to osf.io/az52u at
    2026-07-10T13:32:22Z, and it was recorded in-repo at commit `ac4c990` with tag
    `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`. The placeholder filename/tag never existed. This task is
    retained ONLY as the provenance record of the gate; its <verify> below now checks the REAL artifact.

    THE EXECUTOR MUST NOT: re-draft the doc; re-post to OSF; create the placeholder filename; create the placeholder
    tag; or EDIT `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`. That file is byte-identical to what was
    uploaded to OSF — editing the project-side copy would silently diverge the repo from the posted artifact, which is
    exactly the provenance failure this gate exists to prevent. Run the <verify> to CONFIRM the gate, then go to Task 2.
  </action>
  <what-built>
    ✅ ALREADY BUILT (Carter-authored, posted 2026-07-10T13:32:22Z, recorded `ac4c990`) —
    `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`, the scoped OSF amendment-update.
    Recorded here for provenance; NOT a work item. It states, in original-research framing (never "fix/cleanup/revision"):
      (1) the panel overlapping-variant policy = **exclusion + provenance, never zeroing** — a variant whose
          LD is structurally undefined because an overlapping deletion's REF span makes it uncallable in the AoU
          AFR reference is EXCLUDED in lockstep from BOTH the LD panel and the harmonized sumstats, with an
          auditable provenance manifest (per-variant: ID + both-build positions + occluding deletion + REF span
          + locus + traits-present + reason=reference-occlusion→undefined-LD);
      (2) the deterministic upstream span-filter across all 276 regions (the conservative rule, cited from the
          geometry verdict — 5 direct ref_span_overlap + 1 second-order, 0 same-position);
      (3) NaN→0 is retired as directionally wrong (cite the concrete harm: rs182965575 present 7/9 AFR sumstats);
      (4) the genome-wide present-rate scan quantifies the scientific cost (Angle-1/3 catalog).
    AS POSTED, the doc cross-links osf.io/az52u (7×) and names its supporting docs
    (`m3_region1_nan_geometry_verdict.md`, `m3_panel_occlusion_policy_decision.md`) by FILENAME rather than by
    body-SHA anchor. The anchors themselves (`4543dcf4…` / `42d70167…`) live in — and are verified against — those
    source docs, which is where the <verify> now checks them. The as-posted doc frames the policy as withdrawing the
    tcujq NaN→0 conditioning in favour of exclude-in-lockstep; it does not use the literal phrase "never zeroing".
  </what-built>
  <human-action>
    ✅ DONE 2026-07-10 — no outstanding human action. Carter (carterclinton@ncsu.edu; researcher account
    cclinton@researchallofus.org is AUTH-ONLY — never email it) POSTED the amendment-update to the OSF project
    **osf.io/az52u** (same project as the tcujq AFR NaN-PSD amendment) at 2026-07-10T13:32:22Z, and provenance is
    RECORDED at commit `ac4c990` + tag `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10` (project-side copy +
    tcujq superseded-by pointer + `.planning/osf_deviations.md` dated entry + STATE.md block).

    ONE non-blocking follow-up (does NOT gate 07a/07b/07c): the OSF direct file GUID/URL was never captured — only
    the activity timestamp from Carter's screenshot. When Carter opens the OSF file page, fill
    `osf.io/az52u/files/<GUID>` into the amendment doc header + `.planning/osf_deviations.md`. Deferred by design:
    the gate's requirement is that the policy be publicly on the record before the code lands, which the posting
    timestamp establishes; the GUID is a convenience pointer.
  </human-action>
  <acceptance_criteria>
    ALL SATISFIED as of `ac4c990` (2026-07-10). The <verify> below re-confirms them; it does not create anything.
    - `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` exists and encodes the policy:
      "exclusion" + "provenance" + "lockstep", and names "tcujq" as the withdrawal target (never zeroing — expressed
      as the withdrawal of the tcujq NaN→0 conditioning, not as that literal phrase).
    - The amendment is POSTED to osf.io/az52u (2026-07-10T13:32:22Z, from the OSF Recent Activity record).
    - Provenance is RECORDED in-repo: commit `ac4c990` + git tag `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`.
    - The settled-science body anchors still hold BYTE-EXACTLY in their source docs (this is the check that actually
      protects the science: `tail -c 5012` of the geometry verdict == `4543dcf4…`; `tail -c 5247` of the policy
      decision == `42d70167…` — each doc's transfer header is excluded from its hash by construction).
    - ⛔ Task 2 (and all of 07b/07c) MUST NOT begin until this gate is cleared — it IS cleared (mirrors the
      `AFR-NANPSD-OSF-AMENDMENT-POSTED-2026-07-04` precedent).
  </acceptance_criteria>
  <verify>
    <automated>bash -c 'set -e; D=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md; test -f "$D"; grep -qi "exclusion" "$D"; grep -qi "provenance" "$D"; grep -qi "lockstep" "$D"; grep -q "tcujq" "$D"; grep -q "az52u" "$D"; git rev-parse -q --verify refs/tags/AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10 >/dev/null; git cat-file -e ac4c990^{commit}; [ "$(tail -c 5012 .planning/amendments/m3_region1_nan_geometry_verdict.md | sha256sum | cut -d" " -f1)" = "4543dcf4a61c3cf79061c8c55b71b316c38c4a938541cf0040c94212c8cdc06a" ]; [ "$(tail -c 5247 .planning/amendments/m3_panel_occlusion_policy_decision.md | sha256sum | cut -d" " -f1)" = "42d701677ac8bc85d3b03f390413c4406ba65f3b11ab085350e560738ab209ef" ]; echo GATE_CONFIRMED_OK'</automated>
    Note: this is a CONFIRMATION of an already-cleared gate — it is read-only and must PASS on an unmodified tree. It
    checks the REAL posted artifact (not the never-existent placeholder), the recorded tag + commit, and re-verifies
    both settled-science body anchors where they actually live (the source docs) rather than grepping them out of the
    amendment doc, which never cited them. If it FAILS, STOP and escalate to Carter — do NOT "fix" it by editing the
    amendment doc (that would diverge the repo copy from the bytes posted to OSF).
  </verify>
  <done>✅ COMPLETE 2026-07-10T13:32:22Z (reconciled to the real artifact 2026-07-15) — `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` exists (exclusion + provenance + lockstep; withdraws tcujq NaN→0), is POSTED to osf.io/az52u, and is RECORDED at commit `ac4c990` / tag `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`. Both settled-science body anchors re-verified byte-exact (`4543dcf4…` / `42d70167…`). Gate CLEARED; Task 1 retained as the provenance record only — NOT a work item. 07b/07c unblocked. Non-blocking follow-up: fill the OSF file GUID/URL when available.</done>
  <resume-signal>None — this gate is already cleared. Run the <verify> to confirm, then proceed directly to Task 2. If the <verify> fails, STOP and escalate to Carter rather than modifying the posted amendment doc.</resume-signal>
</task>

<task type="auto">
  <name>Task 2 (Wave 0 — RED-first): occlusion test scaffolds + the region-1 `.bim` fixture helper</name>
  <read_first>
    tests/m3/test_run_native_ld_panel.py:40-163 (fixture helpers _write_bim/_default_bim_rows/_MockPlink/_setup_cohort + the argv-assertion test at 366-388),
    tests/m3/test_condition_ld_matrix.py + tests/m3/test_nan_guard.py + tests/m3/conftest.py (RED-first + PROJECT_ROOT/sys.path + skip-if-no-chain conventions),
    m3-07-RESEARCH.md §5 (the region-1 .bim fixture table + task-shaped RED tests),
    m3-07-VALIDATION.md (Wave 0 Requirements checklist).
  </read_first>
  <files>tests/m3/test_occlusion_span_filter.py, tests/m3/test_occlusion_manifest.py, tests/m3/test_occlusion_present_rate_scan.py, tests/m3/test_occlusion_lockstep_drop.py, tests/m3/test_run_native_ld_panel.py</files>
  <action>
    Author ALL the RED-first test scaffolds (they FAIL now because the impl modules do not exist — that IS the
    Wave 0 RED state). ⚠ CRITICAL for a clean RED: in the 4 NEW test files, `import occlusion_span_filter` /
    `occlusion_manifest` / `occlusion_present_rate_scan` / `drop_occluded_from_sumstats` INSIDE each test function
    body (NOT at module top), so pytest COLLECTS the files cleanly and each test FAILS as a test/assert failure
    (ModuleNotFoundError raised at call-time) — NOT as a "collection error". Mirror the tests/m3 conventions
    (PROJECT_ROOT via Path(__file__).resolve().parents[2]; insert src/python on sys.path; env smoke_dev py3.11
    numpy/pandas). Reuse the `_write_bim(path, rows)` helper shape (row = (chr, snp_id, cm, bp, A1, A2), A1=ALT/A2=REF;
    an indel sets A2 to a multi-char REF string).

    (1) tests/m3/test_occlusion_span_filter.py — a module-level `_REGION1_BIM_ROWS` fixture helper reproducing the
        verdict's coordinates (chr1; deletions get a multi-char A2/REF of the exact span length) per <interfaces>.
        (Use variant ids = f"1:{bp}:{A2}:{A1}".) Assert `detect_occluded_variants(rows)` returns EXACTLY the 5
        occluded ids {snpA,snpB,snpC,del6,snpD}; plus unit cases: no-deletion window -> []; single deletion covering
        a downstream SNP -> that SNP; a SNP UPSTREAM of a deletion -> NOT occluded (disjoint); off-by-one boundary
        (POS_V==POS_D+len(REF_D)−1 occluded; ==+len(REF_D) not); an SNV (len REF=1) never occludes; an INSERTION
        (len ALT>len REF) never occludes a downstream base; `edges` records occluder→occluded and marks the
        5922718↔5922724 pair as disjoint/second-order.
    (2) tests/m3/test_occlusion_manifest.py — Stage-A record has all coordinate columns + correct ref_span_start/end
        (from the OCCLUDING deletion) + occluding_deletion_id + occluding_deletion_ref_len + reason; resume-safe
        dedup by (region_id, variant_id); aggregate rollup concatenates per-region records. A liftover test
        (skip if `data/external/liftover/hg38ToHg19.over.chain.gz` absent, per the conftest chain-skip pattern)
        asserts pos_grch37 for 5922716/5922718/5922724 == 5982776/5982778/5982784.
    (3) tests/m3/test_occlusion_present_rate_scan.py — on tiny synthetic TSV fixtures with the harmonized header
        (CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD), a variant present in k of n files ->
        present-rate k/n; a variant absent -> 0; CHR/POS auto-detected.
    (4) tests/m3/test_occlusion_lockstep_drop.py — `drop_occluded_from_sumstats` removes exactly the manifest's
        GRCh37 (CHR,POS) rows, logs each drop, leaves non-occluded rows byte-identical, is idempotent (2nd apply =
        no-op), and does NOT re-key.
    (5) EXTEND tests/m3/test_run_native_ld_panel.py — extend `_MockPlink` to honor an `--exclude <file>` argv (drop
        those col-2 ids from the window BEFORE sizing the `.ld.bin`/snplist, composing with the existing
        `--write-snplist`/`mono_snps` modeling). Add tests: (a) the driver writes `{out_prefix}.occluded.excludelist`
        containing exactly the occluded ids for a cohort seeded with the region-1 topology; (b) `--exclude` reaches
        the plink argv (`-k exclude`); (c) `--keep-allele-order` still present on every call; (d) the resulting
        `.npz` has NO NaN and passes content_verify_npz (`-k occlusion`); (e) `n_dropped_occluded` is recorded and
        `n_dropped_monomorphic` is correctly SEPARATED (an in-window mono variant + an occluded variant both present
        -> each counted in its own column). (This file imports the driver — which exists — so it collects fine and
        its new tests fail on ASSERTIONS, not import.)

    SETTLED ORACLE (fold into the fixture assertions — Seth 5/5 vs geometry verdict `4543dcf4…`): (i) the fixture MUST
    reproduce the pair-4 second-order tangle and assert the detector attributes SNP 5922718 to the UPSTREAM DEL 5922716
    (NOT the downstream DEL 5922724), so the single 5922718 drop collapses the 5922716/5922718/5922724 tangle; (ii) DOCUMENT
    (as a comment / xfail-marked gated stub) the SETTLED region-1 REAL-window known-answer occluded set
    `{10328, 44784, 46714, 59097, 66730}` + the 7-deletion REF-span inventory 60/29/7/31/31/17/29 bp — the oracle the
    detector must reproduce at the GATED real-`.bim` validation (out-of-scope for the synthetic unit; it gives the gated
    276-region Nyquist check a concrete expected answer). Note in the test module docstring that Seth's full detector
    prototype exists as a READ-ONLY executor reference (NOT committed; build the detector test-first against the real loader).

    Commit RED (explicit paths — GPFS, NEVER `git add -A`/`.`), tag m3-07a-W7-T-WAVE0. The suite must FAIL only on
    test/assert failures (module/attribute not found raised at call-time; not-yet-wired driver behavior) — NOT on
    pytest collection errors.
  </action>
  <acceptance_criteria>
    - The 4 new test files + the extended test_run_native_ld_panel.py exist and are COLLECTED by pytest with ZERO collection errors.
    - Running the 4 new suites exits NON-ZERO (RED) with NO "error ... collect" line — i.e. they fail as test/assert failures, not collection errors.
    - The region-1 `.bim` fixture helper `_REGION1_BIM_ROWS` is present in test_occlusion_span_filter.py AND encodes the
      pair-4 tangle (5922716/5922718/5922724) so the detector-attribution assertion (5922718 ← upstream 5922716) is testable.
    - The SETTLED region-1 REAL-window oracle `{10328,44784,46714,59097,66730}` + the 7-deletion inventory (60/29/7/31/31/17/29 bp)
      is documented (comment / gated-xfail stub) as the gated real-`.bim` known-answer; the read-only prototype availability is noted.
  </acceptance_criteria>
  <verify>
    <automated>bash -c 'out=$(/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_span_filter.py tests/m3/test_occlusion_manifest.py tests/m3/test_occlusion_present_rate_scan.py tests/m3/test_occlusion_lockstep_drop.py -q 2>&1); rc=$?; echo "$out" | grep -qiE "error.*collect" && { echo COLLECTION_ERROR; exit 1; }; [ $rc -ne 0 ] && echo RED_AS_EXPECTED || { echo UNEXPECTED_GREEN; exit 1; }'</automated>
  </verify>
  <done>All 4 new test files + the extended driver tests collect cleanly (zero collection errors) and fail RED as test/assert failures; region-1 `.bim` fixture helper present. Committed RED with explicit paths.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| policy decision → OSF pre-registration | The exclusion-not-zeroing deviation must be pre-registered before code lands, or the panel change is an undisclosed deviation (reviewer/pre-registration integrity boundary). |
| RED test scaffold → downstream impl (07b/07c) | The tests DEFINE the behavior 07b/07c must satisfy; a mis-encoded expectation (wrong occluded set / wrong liftover anchor) would let a wrong impl pass — pinned against the byte-verified verdict coordinates. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-07a-01 | Repudiation / reproducibility | undisclosed panel-policy deviation | mitigated (CLEARED 2026-07-10) | OSF HARD GATE pre-registered exclusion + provenance in lockstep (withdrawing NaN→0) BEFORE any code: posted 13:32:22Z, recorded `ac4c990`, tagged `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`; blocks 07b/07c via depends_on. |
| T-m3-07a-03 | Tampering / repudiation | the in-repo amendment copy silently diverges from the bytes posted to OSF | mitigate | The posted doc is READ-ONLY to the executor — Task 1 forbids editing it, and the gate <verify> confirms rather than repairs. A failing verify escalates to Carter; it never "fixes" the doc. |
| T-m3-07a-02 | Tampering | RED tests encode the wrong excluded set | mitigate | The fixture reproduces the byte-verified verdict coordinates (4543dcf4…); the expected occluded set {1980475,5733487,5922718,7492693,8375822} and liftover anchors (5982776/5982778/5982784) are pinned to the amendment doc-set, not invented. |
</threat_model>

<verification>
- Task 1 (OSF gate — PRE-CLOSED, read-only confirmation): `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` exists (exclusion + provenance + lockstep + withdraws tcujq), is POSTED to osf.io/az52u, is recorded at `ac4c990` + tag `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`, and both settled-science body anchors re-verify byte-exact in their source docs. Confirm only — create/modify nothing.
- Task 2 (Wave 0): the 4 new test files + extended driver tests collect cleanly (zero collection errors) and fail RED as test/assert failures.
- NO perimeter access, NO loop contact, NO re-fire. Entirely NC-State (docs + failing tests).
</verification>

<success_criteria>
- The OSF pre-registration HARD GATE is honored: exclusion + provenance (never zeroing) is posted + recorded before any fix code lands (REQ-OSF-PREREG); 07b/07c are blocked until then via depends_on.
- All Wave 0 RED scaffolds exist, collect cleanly, and fail RED for the right reason (test/assert failure, not collection error) — REQ-SNAKEMAKE-CI.
- The region-1 `.bim` fixture pins the exact behavior (5 occluded ids; liftover anchors) that 07b/07c must deliver — REQ-AOU-LD-VALIDATION precondition.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-07a-W7-osf-gate-and-red-scaffold-SUMMARY.md`.
Record: the OSF gate confirmation (real filename + posted timestamp + `ac4c990` + tag + both re-verified body anchors;
note Task 1 was PRE-CLOSED and reconciled 2026-07-15, and that the OSF file GUID remains an open non-blocking
follow-up); the RED-collection-clean confirmation (zero collection errors) with the actual pytest output; the
region-1 fixture coordinates; and the depends_on chain (07b/07c gated on this).
</output>
