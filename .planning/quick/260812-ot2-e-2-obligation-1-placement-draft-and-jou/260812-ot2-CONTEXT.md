# Quick Task 260812-ot2: E-2 obligation (1) placement draft + journal-selection memo — Context

**Gathered:** 2026-08-12 (Carter's directives, verbatim-derived; `--auto` — no interactive questions)
**Status:** Ready for planning

<domain>
## Task Boundary

Carter's directive (2026-08-12, 17:48 EDT, verbatim): *"For E-2 obligation (1), we
will write a draft and then determine the best/most rigorous/reputable journal to
submit to (we will aim for nature but we can adjust for others). skip this E-2
obligation (2)."*

Three deliverables:

1. **Placement draft** for `ms-correction-v2` into the Track A manuscript
   (`docs/manuscript/id-vs-ref-LD.md`) — a placement SPEC in this quick dir, NOT an
   edit to the manuscript file.
2. **Journal-selection memo** — Nature-first ladder with per-venue pre-placement
   policy check, honest fit assessment.
3. **Ledger record** — append a DECISIONS.md entry recording Carter's two
   2026-08-12 directives (obligation (2) skipped by direction; venue re-target to
   Nature-first).

</domain>

<decisions>
## Implementation Decisions (LOCKED — do not revisit)

### The standing no-agent-edits rule HOLDS
- ⛔ **No agent edits `docs/manuscript/id-vs-ref-LD.md`, posts to OSF, or edits a
  posted amendment body.** Obligation (1) discharges only at Carter's own placement
  (`260812-09a-SELECTED-PAIR-correction-v2.md` §1, §4). The placement draft is a
  paste-ready SPEC (exact anchor lines + full inserted text) that Carter applies.
- The draft must make placement a ≤2-minute action: name the exact insertion point
  (after Methods `### Ethics Statement`, i.e. a new Methods subsection
  `### Correction and Disclosure: Variant-Orientation Exposure` or equivalent,
  before `## Results`), plus the one-sentence pointer to add in `### Limitations`
  (line ~250 region).

### The v2 body text is byte-locked
- The paste block quoted in the placement draft MUST be byte-identical to the
  `<!-- PASTE-BEGIN: ms-correction-v2 -->` … `<!-- PASTE-END -->` block of
  `.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-SELECTED-PAIR-correction-v2.md`
  — verify with a byte comparison in the draft's own verification section, not by
  eye. v1 (`260811-tf3`) and the `260811-oku` drafts are superseded history; never
  quote from them.

### Obligation (2) is SKIPPED by Carter's direction — with the coherence consequence STATED
- No OSF drafting, posting prep, or `osf_deviations.md` work in this task.
- ⚠ CONSEQUENCE THE DRAFT MUST SURFACE (once, plainly, without relitigating): the
  final sentence of `ms-correction-v2` cross-references "the paired entry posted as
  a supplementary file on osf.io/az52u". With (2) skipped, that sentence is FALSE at
  placement time. The placement draft therefore carries TWO clearly-marked options
  for the closing sentence, Carter chooses at placement:
  - **Option P-1 (pair-coherent, recommended):** keep the v2 text byte-intact and
    treat (2) as deferred-to-submission — the OSF entry must exist by the time the
    manuscript is submitted. (Recommended per the rigor-over-speed standing rule and
    because framing B's pair-matching check — §3 item 4 of the v2 file — assumes the
    two halves agree.)
  - **Option P-2 (skip-permanent):** replace ONLY the final sentence with a marked
    variant that references the internal record + pre-registration osf.io/pvb5j
    without claiming a posted supplementary entry. This deviates from the gated v2
    pair; the deviation is Carter-directed and must be recorded as such in the
    DECISIONS entry, and the placed text is then no longer "the v2 pair half" —
    state that explicitly.
- Do NOT register the E-4 public-commitment obligation (that trigger is posting,
  which is skipped).

### Journal memo scope
- Ladder: Nature (flagship) first per Carter; then candidates including Nature
  Genetics, Nature Communications, Nature Metabolism, AJHG, Genome Biology, Genome
  Medicine, Cell Genomics, eLife, PLOS Genetics, HGG Advances (prune/order by fit).
- Manuscript profile for fit assessment: solo-author reproducibility/methods audit
  of 50 curated cardiometabolic pleiotropy loci; identity-LD vs real-LD; largely
  corrective/negative findings with one surviving Tier-A anchor (SH2B3); current
  header targets *Genome Medicine*; `manuscript/README.md` cover-letter table lists
  Nat Genet, AJHG, Nat Metab, Cell Genomics, Genome Medicine.
- Per venue: (a) scope fit + honest acceptance-realism note; (b) format/length
  constraints vs the current 453-line full article; (c) THE PRE-PLACEMENT CHECK —
  how a "Methods correction-and-disclosure note" inside a FRESH submission reads
  editorially (the v2 file's check concerns an in-submission manuscript; a fresh
  submission has no correction machinery — state this distinction); (d) preprint
  policy vs the planned Day-1 bioRxiv preprint; (e) open-access/APC; (f) dual-
  submission rule.
- ⚠ Track A submission status is UNKNOWN to this task (a 2026-05-12 package was
  downloaded by Carter; never confirmed submitted). Do NOT assert either way; the
  memo carries one conditional paragraph: if a Genome Medicine (or any) submission
  is currently pending, no second submission may be made anywhere until it is
  withdrawn or decided — and placement of the correction note in a pending
  submission re-triggers the in-submission reading of the pre-placement check.
- Honest fit ranking is required even where it cuts against the Nature-first aim;
  Carter said "we can adjust for others". Recommend, do not flatter.

### Standing number/framing rules (bind every quoted figure in both deliverables)
- Never quote the pooled 5.29% alone — name APOL1_22q12 18.41% and FTO_16q12
  23.80% in the same breath.
- Never quote a corpus figure without its unit (17.82% = TILE-ROW median; LOCUS
  median = 0.4234%).
- Never cite the E-2 numbers as real-LD exposure (identity-LD stub caveat).
- All public-facing text frames the work as hypothesis-driven original research;
  never "revision", never "salvage of prior work".

### Process constraints
- $0; zero perimeter contact; nothing posted anywhere.
- Git: explicit paths only (never `git add -A` / `.`); no worktrees on GPFS.
- DECISIONS.md is append-only (0 deleted lines).
- Nothing under `src/`, `tests/`, `config/`, `Snakefile`, `results/`,
  `.planning/amendments/`, or `docs/manuscript/` may change in this task.

</decisions>

<specifics>
## Specific Ideas

- Placement default (pre-placement check does not fire on a fresh submission): the
  §1 destination — Methods correction-and-disclosure note + a pointer sentence from
  Limitations. The memo's per-venue check column notes any venue where A's
  placement (Limitations-only) is the safer read.
- The DECISIONS entry should be one entry covering both directives, dated
  2026-08-12, cross-referencing DEC-2026-08-11-e2-framing-correction and the v2
  pair; it records: (2) skipped-by-direction (deferred, not discharged — the
  obligation row in §4 of the v2 file stays UNDISCHARGED), venue re-target
  Nature-first, and the P-1/P-2 closing-sentence fork with P-1 recommended.

</specifics>

<canonical_refs>
## Canonical References

- `.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-SELECTED-PAIR-correction-v2.md` — the v2 pair (§1 ms body is the paste source; §3 pre-paste checklist; §4 status + number rules)
- `docs/manuscript/id-vs-ref-LD.md` — the Track A manuscript (placement target; READ-ONLY this task)
- `manuscript/README.md` — cover-letter venue table
- `.planning/DECISIONS.md` — DEC-2026-08-11-e2-framing-correction, DEC-2026-08-07-e2-orientation-disposition (append target)
- Memory: feedback_original_research_framing, feedback_rigor_over_speed, feedback_multi_terminal_staging

</canonical_refs>
