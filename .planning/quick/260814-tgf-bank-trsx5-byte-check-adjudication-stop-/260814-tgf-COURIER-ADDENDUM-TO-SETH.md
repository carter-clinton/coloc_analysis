# Addendum to UPDATE #3 — the trsx5 download adjudicated, 2026-08-14

> Provenance: drafted in-repo by `quick-260814-tgf` on 2026-08-14, reporting the outcome of
> the size-first byte check you specified. $0, zero perimeter contact, nothing fired. The
> measurement is Carter's, from a logged-in session on his own machine; the prefix test is
> in-repo and read-only. **No agent contacted OSF.**

---

## (a) You were right. The gate fired, and it stopped the fire.

Carter downloaded https://osf.io/az52u/files/trsx5 — the **file**, not the page — from a
logged-in OSF session on his own machine, 2026-08-14 ~21:07 EDT:

```
wc -c    ->  9695
md5sum   ->  c19be8b2ad7cd6a45fee1d668d8a9cf9
```

**The gate fired on the size alone.** 9,695 is in neither {9,758, 9,907}, so the card's
"any other size → STOP" row fired. No hash comparison was required, none adjudicated, and
none could have overruled it. Your size-first formulation — adopted wholesale in UPDATE #3
— is the thing that produced a clean verdict instead of an argument about a digest.

**Corroboration, not adjudication.** The observed md5 equals your API-read advisory value
exactly. It corroborates; we still did not adjudicate on it, and did not need to.

**Your contest is CONFIRMED to the byte.** 9,907 - 9,695 = **212**. Exactly your claim, and
we are stating it without qualification.

**The prefix test against OUR block is NEGATIVE.** Run in-repo, read-only:

```
# repo-canonical block, re-derived via the awk extraction (exclusive of both markers)
wc -c    ->  9758
md5sum   ->  28ecdb3160833da80cfa25952f76415b

head -c 9695 <that block> | md5sum
         ->  6b75e660e52413e4cbec116f315590b6
```

`6b75e660e52413e4cbec116f315590b6` ≠ `c19be8b2ad7cd6a45fee1d668d8a9cf9`, therefore **the
posted body is NOT a tail-truncation of our 9,758-byte canonical block.**

*Our reading, labelled as a reading:* the posted body most plausibly belongs to **your**
9,907-byte lineage, and our 2026-07-10 hand-paste source was evidently not byte-identical
to the repo-canonical block. That makes the **149-byte** delta between the two "complete"
lineages the central open question rather than a formatting curiosity.

## (b) Two asks

**1 — Does `head -c 9695` of your 9,907-byte body md5 to
`c19be8b2ad7cd6a45fee1d668d8a9cf9`?** Against your own file:

```
head -c 9695 <your-9907-byte-file> | md5sum
```

- **YES** establishes the posted body is a **clean tail-truncation of your lineage** — which
  localizes the failure to the 2026-07-10 hand-paste, and tells us the posted prefix is at
  least uncorrupted as far as it goes.
- **NO** means a third body, and the scope widens rather than closes.

**2 — Send the complete 9,907-byte body, sha256-anchored** — the anchor travelling with the
body, so we can verify byte-faithful arrival through the chat channel before it touches the
repo — **or** a byte-exact diff against our 9,758-byte canonical block.

Repeating honestly what UPDATE #3 said: **we do not hold your 9,907-byte body.** Only its
md5 (`425d925a88ab474ec2396cbea25e665c`) appears anywhere in our records, never the body.
So we **cannot compute** the 149-byte diff ourselves, and we are not going to promise one we
cannot produce. Our canonical block remains reproducible on demand at **9,758 /
`28ecdb3160833da80cfa25952f76415b`** via the awk extraction, unchanged from UPDATE #3.

**Ordering constraint: the 149 bytes get reconciled BEFORE anything is re-posted.**
Re-posting the wrong lineage would put a second wrong body on the public record.

## (c) What is held

- **The fire is HELD.** No AoU compute has run. The browser agent stood down at the Step 3
  GATE, the VM was never started, `$0`, zero perimeter contact.
- **Obligation-(2) posting is HELD** by the same gate.
- **The ledger entry is no longer un-annotated.** `.planning/osf_deviations.md` now carries
  a dated ADJUDICATED sub-entry recording exactly the numbers above — appended, with the
  2026-07-10 and 2026-07-15 text preserved.
- **The remediation path is a recommendation Carter has not yet decided on:** reconcile →
  adjudicate the true complete body → re-post as a **new OSF version** (OSF versioning keeps
  the truncated v1 in history; **disclose, never silently replace**) → record
  URL / timestamp / bytes / md5 → only then does the fire unhold. To be plain: **we are not
  going to silently swap the file.**
