# Consolidated adversarial-review findings — substrate for quick-260812-09a

**Provenance:** 2026-08-11/12 five-way adversarial review of commit range `7d575a5..42c060e`, ordered by Carter ("100% certain we have all our bases covered ... comprehensive adversarial review using codex and /assess-blast-radius"). Reviewers: Codex CLI v0.141.0 (external, read-only sandbox; raw output preserved in the session scratchpad) + four blind parallel read-only investigators (D1 record-surface consistency, D2 fire-surface fidelity, D3 disclosure content, D4 guard integrity + repo health). Every finding below was evidence-cited by at least one reviewer; the blockers were independently confirmed by two.

**What the review CLEARED (do not re-litigate; reasons are the load-bearing part):**
- All eleven outgoing figures re-derive to the digit from the two e2-exposure TSVs (three independent re-derivations).
- Pooled 5.29% never appears alone in the shipped texts; identity-LD-stub caveat present in both outgoing bodies; synthetic-fixture (46/182=25.3%) and 100×-misread disclosures correctly labeled and never externally reported.
- No posted OSF body contradicted or touched; no frozen number moves; "revision" appears nowhere; TRACK-A-FROZEN-NUMBERS values appear nowhere.
- The pmv SR4 dossier's evidence chain held under attack (drift counts, traceability, bf16289 characterization all reproduced).
- DECISIONS.md provably append-only (252/0); HANDOFF.json parses; tf3 containment held (exactly entries [0]/[2]).
- §5 of the rcw review is faithful to m3-04c PLAN Task 3 (PRE-FIRE 1/1b/2/3, STEP A–G, allow_degraded, region-1 gate all present, correctly ordered).
- Zero perimeter contact proven (log grep = 0); no source/test/config drift in the whole range; all 144 new git objects readable; origin == 42c060e; standing freeze gate test_source_freeze_pins.py untouched, 39 passed; STATE.md frontmatter byte-identical (pre-existing unparseability NOT aggravated); none of the 68 historical GPFS blob losses touches the range.
- tf3's DEC-01 append-only gate, HJ-02 walker, SP-02 byte-identity (both-empty case guarded) — all defeat-resistant; tf3's task-local disclosure consistent across its own SUMMARY/VERIFICATION/STATE row.

**What STANDS unchanged:** DEC-2026-08-11-e2-framing-correction (framing B chosen) and DEC-2026-08-11-sr4-disposition (never-frozen). The review found no reason to revisit either decision. The remediation fixes texts and surfaces, never the decisions.

---

## PART A — the outgoing disclosure pair (v2 required; DO NOT place/post v1)

**A-BLOCKER-1 (D3): the mechanism sentence misstates which join was defective.** v1 says the catalog↔panel join "matched on coordinates alone and ignored the alleles" (SELECTED-PAIR :72-74, :110, :133). FALSE for that join: `src/snakemake/scripts/ld_allele_join.R:218-241` is a 4-key allele-aware matcher (k4_exact + k4_swap, palindromes dropped, duplicated 4-keys removed) whose own `flipped` counter PRODUCED the disclosed percentages. The actual E-2 defect is downstream: `src/snakemake/scripts/run_qtl_coloc.R:478-479` — orientation is MEASURED AND REPORTED, AND DELIBERATELY NOT APPLIED to the QTL beta (per option A / DEC-2026-08-07). The allele-blind CHR:POS description belongs to the PRE-o7o sumstats↔panel join (fixed by o7o for AFR; still allele-blind on EUR today because the o7o gate is AFR-only — do not describe it in past tense repo-wide). Root cause on the record: the orchestrator's oku task brief specified the o7o mechanism sentence for the E-2 disclosure; harness/checker/verifier then enforced fidelity to a mis-specified requirement. v2 must state: (i) the exposure numbers come FROM the shipped allele-aware join's transposition counter; (ii) the disclosed property is that the computed orientation is not applied to the QTL beta in the current pipeline (a recorded decision, DEC-2026-08-07); (iii) which join is which, so a reviewer with the code finds exact agreement.

**A-BLOCKER-2 (D3): the remedy/commitment describes already-shipped o7o work and mis-scopes the re-report.** v1 commits to "the join is made allele-aware" (it already is) and to regenerating "the affected African-ancestry results" (zero AFR coloc jobs exist; E-4: _ancestry_for_region returns EUR unconditionally). The record says applying the orientation moves EUR/Track A numbers (run_qtl_coloc.R:479-481; deferred-items.md:228: "PP.H4 moves for any pair with transposed variants, including EUR"; actual E-2 remedy per deferred-items.md:228 = apply the measured orientation to the QTL beta + a GRCh38↔GRCh37 reconciliation on the QTL side + an ancestry gate if Track A must not move). v2 commitment must: name the real remedy; scope the re-report to ALL affected ancestries' results that exist at remediation time (explicitly including the EUR results that exist today), bundled with E-4 once a real non-identity panel exists; keep it condition-bounded, no schedule.

**A-BLOCKER-3 (D3): ms-correction dropped its bounding.** v1 ms paragraph lost "a population in which an orientation error can occur, not a count of realised errors" (present in ms-limitation) and nowhere states the code is unchanged, while reading "We report a correction" in past tense — a Methods reader infers a fix was made and results regenerated. v2 ms paragraph must carry: the population-not-realised-errors bounding; an explicit statement that the analysis code is unchanged by this disclosure (the correction is to the record and the forward analysis plan — the framing-B-is-not-option-B axis from DEC-2026-08-11); and the no-PP.H4-shown-wrong sentence or equivalent.

**A-HIGH-1 (D3): unit equivocation.** "195 of 206 measured regions ... per-region median 17.82%" is per-TILE (206 tile-rows per arm across 51 loci). Per-LOCUS: 49/51 affected, median 0.4234%, max 38.6824% (re-derived). The adjacent table uses locus units. v2 must state BOTH units with explicit labels (tiles vs loci) and stop calling the tile median "per-region". Note the same conflation exists in internal records (DECISIONS/HANDOFF "per-region median 17.82%") — internal fix is PART C's sweep-record note; external texts must be right regardless.

**A-MEDIUM (D3/Codex):**
- ms paragraph lacks the measurement basis (shipped `ld_allele_join_indices()` over the 207 real region variant catalogs) and any provenance pointer to the paired OSF entry — add both (Codex #6).
- "published direction of effect" → "reported direction of effect" (manuscript in submission; Codex #7).
- The trsx5 interaction: v1 asserts the posted occlusion commitment is "unaffected"; the posted trsx5 body premises a position-based join (osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md:47,:57). v2 must REASON the interaction: an allele-aware join with palindrome-dropping introduces a new one-sided drop class relative to that premise; state it honestly (either bounded-compatible with why, or as a noted premise update).
- Add an original-research framing sentence per posted precedent (the 2026-07-03 body's "not a fix, cleanup, correction, or salvage of prior work" — adapted, since this IS a correction entry: e.g. hypothesis-driven original research disclosing a measured property of its own pipeline; not a salvage of prior work).
- "FTO_16q12 (3 cells)" → "(3 tiles)".

**A-HARNESS (D4) — the v2 texts must be gated by a NEW harness (v2, in this quick dir) that fixes the defeated clause classes; the v1 oku/tf3 harnesses stay untouched as historical artifacts:**
- D4-01: number↔region fidelity, not token presence — assert each figure within N chars of ITS region label (label-swap must go red). Control: an APOL1↔CXADR label-swap fixture OBSERVED red.
- D4-02: the pooled-alone guard must be scoped to the PASTE BLOCK (not file) and must have its own isolating control (pooled kept + "dragged down" sentence removed INSIDE the block → red; the word "dragged" in an out-of-block comment must NOT satisfy it).
- D4-03: any (UN)DISCHARGED assertion uses word boundaries: require `\bUNDISCHARGED\b` present AND reject `(^|[^N])\bDISCHARGED\b` as standalone where UNDISCHARGED is meant — control: flip fixture OBSERVED red.
- D4-07: never use `[^\n]` inside a POSIX ERE bracket expression (GNU grep 3.6 reads it as "not backslash, not n") — use `.` with line-oriented grep instead.
- Every clause group gets expect_red coverage (the v1 oku self-test hard-coded the ms group; 25/29 clauses were never observed red).
- Carry the correct grep-provenance note (runtime = /usr/bin/grep GNU 3.6 via shebang; the interactive ugrep is a CLI wrapper artifact).

## PART B — the rcw PRE-FIRE gate review (correct IN PLACE + a dated "## Corrections (2026-08-12)" changelog section; the corrected command must sit at point-of-use, not in an addendum the reader may miss)

**B-BLOCKER-1 (Codex #1 + D2, independently):** §4 row 1 / liveness arbiter (:281, :287-296, :418-421): `gsutil ls gs://${WORKSPACE_BUCKET}/ld/AFR_aou/*.npz | wc -l` double-prefixes (WORKSPACE_BUCKET already carries gs:// per SKILL.md:43) → gsutil errors to stderr, stdout empty, `wc -l` prints 0 = FALSE PASS on the pre-fire "expected: 0" row, and reads a healthy fire as dead during STEP B polling. Same defect class the project fixed in quick-260611-tbw (gap C3). Fix BOTH forms at point-of-use: primary literal `gsutil ls gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/*.npz | wc -l`; alternate env form `gsutil ls "${WORKSPACE_BUCKET}/ld/AFR_aou/"*.npz | wc -l` with an explicit "the variable already contains gs:// — never prefix it" warning. Producer path verified correct (run_native_ld_panel.py:925-926 writes {bucket}/ld/AFR_aou/{region_id}.npz).

**B-HIGH-1 (D2):** restore the PLAN's caveat (m3-04c PLAN :1494-1497): do NOT hardcode 276 as a pass bar — a partial bank is a real, reportable outcome (producer: status="verify_failed" regions never upload, :920-926; loop continues on error, :942). Add to the liveness-arbiter paragraph and STEP B.

**B-MEDIUM (Codex #2/#8 + D2):**
- Refresh the fire-time open-items table (:476-477): E-2 obligation (3) is DISCHARGED (DEC-2026-08-11-e2-framing-correction; obligations (1)+(2) open, Carter's external actions); SR4-OPEN is DECIDED (DEC-2026-08-11-sr4-disposition). Date the refresh.
- §4 panel-TSV row: replace `<panel-uri>` with the actual URI (trace the panel TSV name from the repo record — Codex read it as gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv; the executor must verify the name from run_native_ld_panel.py / the m3 records, not trust Codex).
- §4 real-.bim row: currently "Byte-check..." with no executable command — either supply the command + path, or state honestly "exact command determined in-perimeter; the 0-vs-1-based index-origin question is OPEN (see m3-07/16 record)".
- §2 rows for egress ruling / CDR pin / cohort rebuild: add "last-known (dated record; not re-verifiable from NC-State)" labels; either add a §4 gate-time recheck row for the cohort MTs (du + count per the skill's invariant 1) or state why fire-time re-verification is not required.
- Add the PLAN branch-(ii)/(iii) self-contradiction to §2.1 (PLAN :1391-1393 says degraded only under (iii) — agrees with code: assemble_occlusion_catalog.py:230/:415/:460 — while :1505-1509 and :1527 say (ii)); state the code-correct reading so a post-fire auditor isn't hit cold.

**B-LOW (D2):**
- Fix the three wrong §2.1(8) line corrections: occlusion_manifest.py write = append_region_manifest :195-196 (fresh-file :181), not :203-208; run_native_ld_panel.py:507 is a docstring (note it as such or cite the code line); run_susie_rss.R thresholds :715-718 (the cited :713-716 excludes two of three).
- "four test_negative_control_pre_change_* tests" → three (:935, :1018, :1296).
- Annotate L-11 (file-wide grep; the SCOPED proof is L-13's test_run_finemap_shell_passes_the_declared_ld_matrix) and L-09 (config value only; fail-fast enforcement lives at m3_convert_npz_rds.smk:132/163/180 + ld_npz_to_rds.R:272 and is not measured by the L-set) so their labels claim exactly what the commands prove. Annotate L-16's 2>/dev/null missing-dir blindness.

## PART C — claim-level stale sweep of the record surfaces (fix by CLAIM, not by file; the v1 sweep registered sites by file and missed six+)

**C-HIGH (D1):**
- HANDOFF.json:47 gates.m3_04b — a LIVE status field still carrying verbatim the retracted "all 7 pinned files 0-line diff" sentence that DECISIONS.md:1474 forbids repeating. STRIKE the clause; replace with a retraction pointer (this is a correction to a live field, not history-rewriting).
- HANDOFF.json:24 resume_on_reconnect[0] — still "ZERO Carter decisions outstanding ... THREE E-2 OBLIGATIONS ... open LIMITATION-vs-CORRECTION question" and self-labels as superseding everything. Prepend a new dated #0 (2026-08-12, supersedes) with the current state; demote the old one in place.
- HANDOFF.json:131 resume_entry_point — routes readers to the two stale 2026-08-07 blocks and omits both new DECs; add DEC-2026-08-11-e2-framing-correction + DEC-2026-08-11-sr4-disposition + the corrected rcw review + this task's dir.
- STATE.md:55 — the line THIS RANGE ADDED into the ★★ RESUME HERE ★★ block ("ALL THREE E-2 obligations remain UNDISCHARGED") then falsified 17 commits later. Annotate in place (dated supersession note).
- STATE.md:47-49 — the RESUME-HERE block's "ZERO decisions outstanding / three undischarged / SR4-OPEN question" bullets: dated supersession annotations.

**C-MEDIUM (D1 + Codex #4/#5):**
- HANDOFF.json gates panel_reachability (:49) / blocker1_ld_read_path (:53) / aou_loop_refire (:50) / m3_04c 548P (:48): prefix each with a dated "⚠ STALE — superseded by [rcw review §2 / suite_baselines]" marker; do not delete bodies.
- DECISIONS.md — append DEC-2026-08-12 remediation entry (append-only) recording: the five-way review, the findings, the corrections applied, AND (Codex #4) the scoped restatement of the SR4 grep counts ("0 hits measured at 0e7e309, before the disposition entry itself named the basenames — at HEAD the same grep counts ≥1 by self-reference"). This entry also carries the CANONICAL residual/stale-site table (D1 found three different lists across DECISIONS/HANDOFF/STATE; one list, here, wins), including the sites this sweep fixes and any it deliberately leaves (with reasons).
- STATE.md:15 (# comment block): correct the false "ld_npz_to_rds.R byte-unchanged" claim. STATE.md:17 last_activity "2026-08-04 (LATEST)": note in the sweep record (frontmatter zone — the YAML is pre-existing-broken; a body-side note suffices, do not attempt frontmatter surgery).
- STATE.md:1633 Session Continuity: refresh to current (it still says SR4-OPEN new + NEXT = Carter decides E-2).
- ROADMAP.md:1077: correct the "leave ld_npz_to_rds.R unchanged / frozen" claim (it is +313/-62 and never-frozen per DEC-2026-08-11-sr4-disposition).
- .continue-here.md top block (:7 status field, :11 "SUPERSEDES every block below", :39-40): prepend a new dated 2026-08-12 LATEST block per the close-session prepend-demote convention (current state: decisions recorded, obligations 1+2 open, fire gate Carter's, corrected rcw review is the fire surface); demote the 2026-08-07 marker.
- .claude/skills/aou-ld-pipeline/SKILL.md: add a dated banner to the Wave-2 gate table + the "322 = 161 × 2" region-set line marking GATE 2/3 and the 322 figure as describing the RETIRED Hail A.3 producer; current path = native plink (run_native_ld_panel.py, 276 AFR regions per config/ld_regions.tsv 552 rows = 276 × 2), gate surface = m3-04c Task 3 + the rcw review. GATE 0/1/1.5 rows remain live. Do not delete the historical rows.
- The oku "enforced by" overclaim (D4-10): STATE.md body + oku ledger row read as standing enforcement with 29 control-backed clauses (true figure: 4 observed-red of 29, ms-group only). Correct the two STATE.md surfaces to "gated at selection time by (task-local, not CI)"; record the oku-harness caveat in the DEC entry rather than editing the closed oku SUMMARY/VERIFICATION.
- HANDOFF.json:3 timestamp: update to the sweep time with the sweep as the named reason (or leave for close-session — executor's call, disclosed either way).

**C-LOW (D1):** STATE.md:233 and :1625/:1626 dated ledger rows (historical/acceptable) — list in the canonical site table as no-action-needed with reasons; HANDOFF entry [0]'s double-✅ skim risk — cosmetic, list as no-action.

## Constraints inherited by all parts
- DECISIONS.md strictly append-only. No posted OSF amendment body edited. No manuscript file touched. No src/tests/config changes. No perimeter contact. HANDOFF.json must parse after every edit (json.load gate) with a containment walker for exactly the intended paths. Negative controls on fixture copies only, each OBSERVED red. The two 2026-08-11 decisions are NOT reopened. STATE.md frontmatter untouched (body edits only).
