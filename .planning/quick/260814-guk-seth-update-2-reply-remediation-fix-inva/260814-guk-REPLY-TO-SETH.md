# Reply to Seth — UPDATE #3, 2026-08-14 (for Carter to courier)

> Provenance: drafted in-repo by `quick-260814-guk` on 2026-08-14, answering Seth's
> 2026-08-14 reply to UPDATE #2 (banked verbatim at `260814-guk-SETH-REPLY.md`).
> $0, zero perimeter contact, nothing fired. Everything below is checkable in-repo
> by `bash 260814-guk-verify.sh all`.

---

## BLOCKING — confirmed by counting, and fixed at every site

You were right, and it was worse than a typo. I counted it rather than eyeballing it:

```
printf 'c19e8b2ad7cd6a45fee1d668d8a9cf9' | wc -c    # -> 31
printf 'c19be8b2ad7cd6a45fee1d668d8a9cf9' | wc -c   # -> 32
```

An md5 is 32 characters, so the string in the card could not have matched any
download. The consequence is the one you named: the **STOP-truncated branch was
structurally incapable of firing** — the branch that exists to protect the public
record could never have executed, one step before a $385–1,084 irreversible spend.
That is a comparison that cannot fail, which is a class this project has now hit
repeatedly and which our own green checks are bad at seeing. You flagged it once and
it came back unchanged; escalating was the correct call.

**Fixed at every site** (grep-verified — the invalid string now appears nowhere
outside the task directory that records it):

| Site | What it is |
|---|---|
| `260812-ox1-AGENT-PROMPT.md` STEP 6b | the text pasted to the AoU browser agent |
| `260812-ox1-BROWSER-PASTE.md` §6b | the paste-ready rendering |
| `260812-ox1-READY-TO-FIRE.md` item 6b | **NEW** — the gate was missing from Carter's primary checklist entirely |
| `.planning/HANDOFF.json` `gates.trsx5_posted_body` | the live gate field |
| `.planning/STATE.md` trsx5-contest block | the live instruction block |

**Your safest formulation was adopted wholesale: size-first, hashes confirm only.**
Here is the new card in full (the READY-TO-FIRE copy — it is the self-contained one):

---

⛔ **This gate BLOCKS THE FIRE and blocks obligation-(2) posting.** trsx5 IS the
pre-registration the fire executes; a truncated posted body is unanswerable after
output is banked.

**1 — download.** In a logged-in OSF browser tab, download
https://osf.io/az52u/files/trsx5 — the **file**, not the page. Then `wc -c` and
`md5sum` it, and report **both, verbatim**, whatever they say.

**2 — ⚠ ADJUDICATE ON THE BYTE COUNT FIRST.** A byte count cannot be mistranscribed
into a false pass; a hash can. **Any size other than 9,758 or 9,907 is a STOP by
itself** — no hash comparison is required, and none may overrule it.

**3 — the hashes then confirm which known body it is:**

| Observed | Expected md5 | Meaning | Action |
|---|---|---|---|
| **9,758 B** | `28ecdb3160833da80cfa25952f76415b` | the repo-canonical paste block | **gate PASSES** — proceed |
| 9,758 B | anything else | same size, different content — its own anomaly | **STOP**; report verbatim |
| **9,907 B** | `425d925a88ab474ec2396cbea25e665c` | the methodologist's complete lineage (Seth-reported; **we do not hold this body**) | **STOP** — reconcile the lineages before firing |
| any other size | — | truncated / anomalous posted body | **STOP** — the fire is **HELD** until a complete body is re-posted and recorded |

**4 — advisory only, ⚠ NEVER an adjudication anchor.** The truncated body's md5 is
reported as `c19be8b2ad7cd6a45fee1d668d8a9cf9` by Seth, read from the OSF API and
unverified by us (the file sits behind a sign-in wall). Do **not** adjudicate on it.
The version of this card shipped 2026-08-13 carried a 31-character transcription of
that value — an md5 is 32 characters, so that comparison could never fire the
STOP-truncated branch.

⚠ **The ledger's trsx5 entry stays UN-ANNOTATED toward either lineage until this
download adjudicates.**

---

Two notes on how it is now held in place, since a fix you cannot see is not much
better than the defect. First, your corrected 32-character value is carried
**advisory-only and attributed to you as unverified-by-us at every site** — we
cannot fetch trsx5, so it is not something we get to treat as an anchor. Second,
the check that would have caught this is now mechanical and generic: a **hex-run
length invariant** over the card blocks (every run of ≥20 hex characters must be
exactly 32), deliberately *not* a list of expected hashes, because an
expected-hash list is blind to this class by construction. It was proven able to
fail before it was trusted — deleting one character from `28ecdb31…` in a scratch
copy makes it report `len=31`, and the identical file without the mutation passes.

## R1 — withdrawal noted and accepted

Accepted, and we are not restating the stronger claim anywhere. The gate stands on
the narrower **records-integrity** ground alone: we should not bank output while the
contents of the public record are unknown. It is not, and is no longer written as,
a "we might be executing an unregistered method" argument.

## R3 — your ceiling figures are now in both runbook vocabulary blocks

Landed in `260812-ox1-AGENT-PROMPT.md` (the STAGE C HOLD LIFTED paragraph) and
`260812-ox1-READY-TO-FIRE.md` §10 (Deferral vocabulary), attributed to your
2026-08-14 review: the clause-(d) anomaly threshold is **`0.0005 × n_var`** with a
**strict `>`** — defer only when the occluded count strictly exceeds it; at the
pinned **120,000** cap that is **60.0** variants, at region 1's `n_var` of
**102,421** it is **51.2**, and region 1's expected ~5 occlusions sit roughly **10×
under** the ceiling. A deferral at region 1 would therefore itself be the finding.

## R4 — registered as a coverage gap, with the remedy path

Registered as **`R4-COVERAGE`** in
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`. The substance, so
you can check it says what you asked for:

- **Status: REGISTERED as a DISCLOSURE OBLIGATION — not blocking the fire.**
- The gap: **29 / 276 = 10.5%** of regions defer at the 120,000 cap; bankable target
  **~247**; largest deferred span **48.5 Mb**. These are recorded explicitly as
  *your estimates*, and the entry requires that the ACTUAL post-fire numbers from the
  panel TSV's `deferred_infeasible_square` rows replace them before anything is
  published.
- The obligation: disclose as a **methods/limitations** item alongside the occlusion
  disclosure, in the form *"N regions exceeding n_var X were not converted in square
  mode; affected span M Mb"*, with the actual numbers — not merely as an internal
  deferral status.
- The framing you objected to is **explicitly RETIRED**, with your reasoning recorded
  as the reason: it is true of this pipeline as currently built and false as a
  statement about the science, and an undisclosed ancestry-specific hole is the
  reviewer question that cannot be answered later. The checker asserts the retired
  wording appears **zero** times across all three runbook files.
- The remedy path is recorded so the gap is **bounded rather than permanent**: the
  frozen producer already supports **banded mode** (`--r gz` with an `--ld-window-*`
  bound), and large regions can be split into **overlapping sub-windows** — with
  **neither happening before this fire**, and the entry says so.

On your second point: the Stage-B cost model is relabelled
**cost-per-bankable-region**, never cost-per-region-of-276, at all three sites that
state it (AGENT-PROMPT STEP 9's gate sentence, READY-TO-FIRE item 11-C's egress/cost
language, and BROWSER-PASTE's cost-refinement gate — that third one was not in the
original scope; leaving one uncorrected copy of the same claim is the divergence
problem we consolidated against, so it was fixed too).

## The 9,758 / 28ecdb31 anchor — re-derived, not asserted

You should not have to take this one on faith either. Verbatim transcript, run
2026-08-14 on the working tree, and again against the posting-day revision:

```
F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md

awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | wc -c
9758

awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" | md5sum
28ecdb3160833da80cfa25952f76415b  -
```

`git show ac4c990:$F` piped through the same extraction gives **byte-identical**
results (9758 / 28ecdb31…). The extraction is **exclusive of both marker lines** —
that is the definition of the block, and it is what makes the number reproducible
rather than a convention.

## Your request (a) — the canonical 9,758-byte block

It is our own already-public text, so it does not wait on the adjudication. Carter
can produce it on demand, before or after the download:

```
F=.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md
awk '/^--- PASTE ENDS HERE ---$/{p=0} p{print} /^--- PASTE INTO OSF FROM HERE ---$/{p=1}' "$F" > "$HOME/trsx5-canonical-9758.txt"
wc -c   "$HOME/trsx5-canonical-9758.txt"    # must print 9758
md5sum  "$HOME/trsx5-canonical-9758.txt"    # must print 28ecdb3160833da80cfa25952f76415b
```

⚠ The output goes **outside the repo** on purpose: a committed second copy of the
canonical body would be a drift surface, and the amendment file is deliberately the
single source. If the two lines above do not print exactly those values, do not send
the file — something moved and that is its own finding.

## Your request (b) — the 149-byte diff. We cannot produce it.

**We do not hold your 9,907-byte body.** Grep-verified across the repo: only its
md5 (`425d925a88ab474ec2396cbea25e665c`) appears anywhere in our records, never the
body. So we **cannot compute** the diff, and we are not going to promise one we
cannot produce.

Courier us the 9,907-byte body — or its exact source — and we will produce the
byte-level diff and send it back, **independent of what the download shows**. We
agree it is worth knowing whether the two lineages differ in substance or only in
formatting, before either is cited again.

## Standing positions, unchanged

- The ledger's trsx5 entry **stays un-annotated** toward either lineage until
  Carter's authenticated download adjudicates. Nothing in this round moved it.
- **An agent never fires the loop.** Unchanged, and nothing in this task touched
  execution — documents only, $0, no perimeter contact.
- Nothing else is blocking from our side either.
