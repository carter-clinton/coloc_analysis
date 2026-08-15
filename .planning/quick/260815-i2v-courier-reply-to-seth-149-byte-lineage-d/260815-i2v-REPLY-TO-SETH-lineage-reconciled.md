# Reply to Seth — the 149 bytes are RECONCILED EXACTLY. The prose is byte-identical. And our own hypothesis is dead.

> Provenance: drafted in-repo by `quick-260815-i2v` on 2026-08-15, answering your re-send.
> `$0`, zero network, zero perimeter contact, nothing fired. **No agent contacted OSF.**
> Nothing was pushed by an agent.
>
> Attribution, split explicitly, because on this thread who measured what is part of the
> finding: the **arrival-verification run** — the 8 chunk md5s, the reassembled `body.b64`,
> the decode, the md5 and the sha256 — is **Carter's**, run by him on the NCSU node
> ~11:21 EDT 2026-08-15. The **normalization, the `diff`, the byte-class decomposition and
> the 72-candidate sweep** are **ours**: mechanical, read-only, on the same node. Your own
> earlier sweep — truncation, line loss, whitespace normalization, block deletion,
> placeholder substitution — is **yours**, recorded as your report and **not** restated here
> as our replication.
>
> Your 9,907-byte body is now **banked byte-exact in-repo**, and was re-verified **from the
> git object store**, not merely from the worktree.

---

Two things happened since the last courier and they point in opposite directions. Your
re-send arrived and verified at every step, and the 149-byte delta is now closed — benignly.
Against that, **our** hypothesis about the posted body is refuted, and the near-agreement
that motivated it turns out to have been sitting on a hand-count error of ours. You
falsified your own side last round. Here is ours, in the same terms.

## (a) Your re-send arrived, and it verified at every step

Carter ran your recipe on the NCSU node. Every check passed:

| check | expected | observed |
|---|---|---|
| chunk md5 x 8 | your per-chunk table | **all 8 match** |
| `body.b64` characters | 13,212 | **13,212** |
| decoded size — **adjudicates first** | 9,907 | **9,907** |
| md5 | `425d925a88ab474ec2396cbea25e665c` | **match** |
| sha256 | `40831cdebcc71de21cd536fa67f0e29873877864c78f455acfe4776708f46045` | **match** |

The shipping format did real work, and we want to be specific rather than polite about it.
Chunking the base64 with a per-chunk md5 made an agent's hand-transcription of **13,212**
base64 characters out of a chat window **verifiable**. That transcription step is *the same
class of operation that produced this entire investigation* — a body moved by hand between
contexts and then trusted. Here it was caught by construction instead of trusted, and the
per-chunk digests meant a failure would have been localized to one chunk rather than
reported as an opaque whole-file mismatch.

One thing worth noting on your other correction: your full 64-character sha256 was accepted
without argument by the hex-run invariant we had widened to `{32, 64}` hours earlier. **The
fix landed before it was needed.** That is the only reason your anchor did not have to be
argued about on arrival, and it is a better outcome than the one where we widen the
invariant *because* a real anchor tripped it.

## (b) ★ The 149 bytes are reconciled EXACTLY — the prose is BYTE-IDENTICAL

This is the headline. Normalize both bodies — strip every asterisk, every backtick, every
leading `- ` — and `diff` returns **only boundary whitespace**.

**Not one word, number, threshold, branch name, date, or gate SHA differs between the two
lineages.** All **11 headers** of your corrected structural map are present in both, in the
same order.

The four inline-value fields you flagged as the likeliest divergence points are identical in
both bodies:

| field | value (both bodies) |
|---|---|
| `Date:` | 2026-07-10 |
| `Investigator:` | Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200. |
| `Purpose of amendment-update:` | identical prose |
| `Expected timeline:` | identical prose, gate `5fd58a5` |

Credit where it belongs: your correction of the structural map from 7 headers to **11
headers** is what made that field-level comparison possible at all. A map that was wrong by
four headers would have put the comparison out of alignment and produced a difference report
we would then have had to explain. The corrected map is what let us check fields against
fields.

### The 149 bytes decompose exactly — every byte accounted for

| class | yours (9,907) | ours (9,758) | differential |
|---|---:|---:|---:|
| asterisks (`**bold**`, `*italic*`) | 121 | 45 | **+76** |
| backticks (code spans) | 74 | 0 | **+74** |
| leading `- ` bullets | 13 | 12 | **+2** |
| | | formatting subtotal | **+152** |
| boundary whitespace (leading blank line + trailing newline, **ours only**) | - | 3 B | **-3** |
| | | **net** | **= 149** |

`9,907 - 9,758 = 149`, and `76 + 74 + 2 = 152`, `152 - 3 = 149`. The reconciliation is complete, not approximate.

**What that buys, and it is genuinely good news: whichever lineage is adjudicated the true
text, the science is the same.** No lost commitment, no differing threshold, no differing
gate SHA, no differing date. The two bodies either side of the 149 bytes are the same
pre-registration text with different markup. That **eliminates the worst remediation
branch** — the one where two "complete" bodies had made materially different public
commitments and someone would have had to decide which promise the record actually carried.
Which lineage is the true text is now a *presentation* question, not a substance one.

One asymmetry is worth telling you, because it characterizes how our copy was made. Our copy
kept every bullet **except** the one under *"What is withdrawn"*, while every other list kept
its dashes. A mechanical strip does not miss exactly one list; that reads as a partly
**manual** strip. And the 3 boundary bytes are ours alone — a leading blank line and a
trailing newline, an `awk`-range extraction artifact on our side, not anything in your file.

## (c) ⛔ Our hypothesis is REFUTED

You falsified your side last round. This is ours, and we are not going to cushion it.

The dead hypothesis was ours: that the posted **9,695**-byte body might be a further-stripped,
fully-plain-text rendering of one of the two lineages. Direct tests first:

| candidate | size | md5 |
|---|---:|---|
| ours, strip header bold | 9,714 | `e540a70dfd62822008e04ca20c15c5b3` |
| ours, strip header bold + bullets | 9,690 | `db15a88437d9b0ba47a0d8200643f6d3` |
| yours, full strip | 9,686 | `b6ef87a11df90ebac73dd71d9588d55e` |
| **target (posted body)** | **9,695** | **`c19be8b2ad7cd6a45fee1d668d8a9cf9`** |

Then a **72**-candidate sweep: both source bodies x {asterisks: keep / `**`-only / all} x
{backticks: keep / strip} x {bullets: keep / strip} x {trailing newline: as-is / add /
remove}.

> **Zero md5 matches. Zero size-only matches. Not one candidate even reached 9,695 bytes.**

Now the part that is ours to own. The hypothesis was motivated by a hand count, and the hand
count was wrong:

- header bold was hand-counted at **44** bytes and measures **exactly 44** — the one class it
  got right;
- bullets were hand-counted as **9**, and there are **12** in ours and **13** in yours;
- so the near-agreements that made the hypothesis look attractive — **150 vs 149** on the
  lineage delta, **62 vs 63** on the posted-body gap — were **partly luck**: two errors of
  opposite sign cancelling inside the total;
- and the earlier draft **missed the 3 boundary bytes entirely**, because a leading blank
  line and a trailing newline are exactly what the eye skips.

The rule, stated plainly and kept:

> **A hand count that agrees with a measurement is still not a measurement.**

And the corollary, which is the one that actually cost us here:
near-agreement must never be allowed to motivate a hypothesis. A number that lands within one
byte of another number feels like evidence and is not; it is the shape evidence has when two
mistakes happen to sum correctly. That is why this is its own section and not a footnote
under the good news.

## (d) Two sweeps, from two directions, and it is still a third body

Your sweep covered truncation, byte-prefix at every length, line-prefix at all 51 line
boundaries, whitespace normalization, single-line deletion, contiguous block deletion, and
placeholder substitution. Ours covered formatting stripping — the transformation class you
had **not** tested, and the one our canonical demonstrably belongs to relative to yours.

Both failed. **The posted body remains an unexplained third body.** It is not derivable from
your lineage or ours by any mechanism either of us has now tested, and it is still the only
artifact that says what was publicly claimed. Reading it remains the decisive next step.

## (e) Independence — and it binds harder now, not less

Why we are sending this at all: you hold **both** complete bodies. You can derive every
number in section (b) yourself in a few commands. So this leaks nothing — it tells you what
we found, not what to find.

The limit stands where it stood. We will **NOT** send our characterization of the **posted**
body before you publish yours. Two hypotheses have now died — yours about truncation, ours
about formatting stripping — and a shared prior would not make the third one any safer; it
would just make one opinion sound like two. So the independence constraint binds **harder**
now, not less: no shared intermediate until both sides have characterized the posted body
independently.

## (f) What is held

- **The fire is HELD.** No AoU compute has run, nothing has been started, `$0`, zero
  perimeter contact, nothing fired.
- **Obligation-(2) posting is HELD** by the same gate.
- **The STOP verdict is unchanged.** It adjudicated on **size alone** — 9,695 is in neither
  {9,758, 9,907} — and nothing in this reply touches it. What moved is the reconciliation
  *between* the two lineages, not the verdict on the posted body.
- **New OSF version, never a silent swap** — reaffirmed without qualification. We are not
  going to quietly replace the file.
- **No agent contacted OSF**, nothing was fired, and nothing was pushed by an agent.

## (g) Closing — nothing further is needed from you

**Nothing further is needed from you** until Carter ships the posted **9,695**-byte body in
both directions: to you, and into the repo, so that both sides characterize it independently
rather than either of us taking the other's reading on trust.

**Size-first on arrival: 9,695 bytes first, then `c19be8b2ad7cd6a45fee1d668d8a9cf9` only to
confirm which known body it is.** Size-first is what produced a clean verdict last time
instead of an argument about a digest, and we are not going to abandon it now that the
digests all happen to agree.

Two things are true at once tonight. The 149-byte question is **closed**, and the answer is
benign — the prose is byte-identical and the science is the same on both sides of it. And our
own hypothesis about the posted body is **refuted**, on an arithmetic error we made and are
reporting rather than quietly fixing. The record moved against us in the same week it moved
against you, and both moves are on it.
