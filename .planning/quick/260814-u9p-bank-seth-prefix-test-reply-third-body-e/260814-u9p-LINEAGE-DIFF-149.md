# The 149-byte lineage delta — RECONCILED EXACTLY. The prose is byte-identical.

> **Provenance:** Seth's complete 9,907-byte body arrived 2026-08-15 ~01:27 EDT as 8
> base64 chunks with per-chunk md5s; Carter ran the verification recipe on the NCSU node
> ~11:21 EDT and **every check passed** (§1). The analysis below is **mechanical** — every
> number is a measured `wc -c` / `md5sum` / `diff` / `tr -cd | wc -c`, run read-only on the
> NCSU node. `$0`, no network, no perimeter contact, nothing fired.
>
> ⚠ **This file supersedes an earlier draft of itself** written a few hours earlier in a
> session where Bash was unavailable. That draft reached its headline conclusion by
> *reading* the two texts and **hand-counting** bytes. Two of its claims were wrong and are
> corrected in §3 rather than quietly overwritten.

---

## 1. Arrival verification — PASS at every step

| check | expected | observed |
|---|---|---|
| chunk md5 × 8 | Seth's table | **all 8 match** |
| `body.b64` chars | 13212 | **13212** |
| decoded size ⟵ **adjudicates first** | 9907 | **9907** |
| md5 | `425d925a88ab474ec2396cbea25e665c` | **match** |
| sha256 | `40831cdebcc71de21cd536fa67f0e29873877864c78f455acfe4776708f46045` | **match** |

The chunked-with-per-chunk-md5 format did real work: it made an agent's hand-transcription
of 13,212 base64 characters out of a chat window **verifiable**. That transcription step is
the same class of operation that produced this entire investigation, and here it was caught
by construction rather than trusted.

## 2. ★ FINDING (mechanically confirmed) — the prose is BYTE-IDENTICAL

Normalize both bodies by removing every asterisk, every backtick, and every leading `- `,
then `diff`:

```
diff <(norm ours) <(norm seth)
1d0
<                                   # ours carries one leading blank line
52,53c51
< Expected timeline: …closeout.     # text IDENTICAL on both sides
<                                   # ours has a trailing newline; seth: "\ No newline at end of file"
```

**The only surviving differences are boundary whitespace.** Not one word, number,
threshold, branch name, date, or gate SHA differs between the two lineages. All 11 headers
of Seth's corrected structural map are present in both, in the same order, and the four
inline-value fields he flagged as the likeliest divergence points are identical:

| field | value (both bodies) |
|---|---|
| `Date:` | 2026-07-10 |
| `Investigator:` | Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200. |
| `Purpose of amendment-update:` | identical prose |
| `Expected timeline:` | identical prose, gate `5fd58a5` |

### The 149 bytes decompose exactly — every byte accounted for

| class | Seth 9,907 | ours 9,758 | differential |
|---|---:|---:|---:|
| asterisks (`**bold**`, `*italic*`) | 121 | 45 | **+76** |
| backticks (code spans) | 74 | 0 | **+74** |
| leading `- ` bullets | 13 | 12 | **+2** |
| | | formatting subtotal | **+152** |
| boundary whitespace (leading blank line + trailing newline, **ours only**) | — | 3 B | **−3** |
| | | **net** | **= 149** ✓

`9,907 − 9,758 = 149`, and `152 − 3 = 149`. The reconciliation is complete, not
approximate.

**Reading it in plain terms:** our canonical is the same text with inline code-span and
emphasis markup stripped (section-header bold retained), one bullet dropped under *"What is
withdrawn"* — the single asymmetry, since every other list kept its dashes, which reads as
a partly manual strip — and three bytes of extraction-boundary whitespace that our `awk`
range includes and Seth's does not.

## 3. ⚠ Corrections to this file's own earlier draft — kept on the record

1. **"The two lineages differ ONLY in inline markdown formatting" was not quite true.**
   It missed the **3 bytes of boundary whitespace** entirely — invisible when reading, since
   a leading blank line and a trailing newline are exactly what the eye skips. The corrected
   statement is stronger and more precise: *the prose is byte-identical; the delta is
   formatting **plus** extraction-boundary whitespace.*
2. **The hand-counted byte table was wrong in one class.** Header bold was hand-counted at
   44 B and measures **exactly 44 B**; but bullets were hand-counted as 9 (18 B) and there
   are **12** in our copy and **13** in Seth's. The old table's 150-vs-149 "within 1 byte"
   agreement was therefore **partly luck** — two errors of opposite sign landing close to
   the right total. A hand count that agrees with a measurement is still not a measurement.
3. The old §5 hypothesis is **refuted** — see §4.

## 4. ⛔ HYPOTHESIS REFUTED — the posted body is NOT a formatting-strip of either lineage

The earlier draft proposed that the posted 9,695-byte body might be a further-stripped,
fully-plain-text rendering, on the strength of a 62-vs-63-byte hand-count agreement. **That
hypothesis is dead.**

Direct tests:

| candidate | size | md5 |
|---|---:|---|
| ours, strip header bold | 9714 | `e540a70dfd62822008e04ca20c15c5b3` |
| ours, strip header bold + bullets | 9690 | `db15a88437d9b0ba47a0d8200643f6d3` |
| Seth, full strip | 9686 | `b6ef87a11df90ebac73dd71d9588d55e` |
| **target (posted body)** | **9695** | **`c19be8b2ad7cd6a45fee1d668d8a9cf9`** |

Then a **72-candidate sweep** — both source bodies × {asterisks: keep / `**`-only / all} ×
{backticks: keep / strip} × {bullets: keep / strip} × {trailing newline: as-is / add /
remove}:

> **Zero md5 matches. Zero size-only matches.** Not one candidate even reached 9,695 bytes.

So markdown-formatting stripping — the transformation class Seth's own sweep had not
tested, and the one our canonical demonstrably belongs to relative to his — **does not
explain the posted body either.** The near-miss arithmetic that motivated it (62 vs 63) was
numerology: it rested on the same miscounted bullets corrected in §3.

**The posted body remains an unexplained third body.** Two independent sweeps from two
directions have now failed to derive it: Seth's (truncation, line loss, whitespace
normalization, block deletion, placeholder substitution) and ours (formatting stripping).

## 5. What this changes — and what it does not

**Changes, and it is genuinely good news:** the 149-byte question is **closed**, and the
answer is benign. The two bodies either side of it are **the same pre-registration text**.
There is no lost commitment, no differing threshold, no differing gate SHA, no differing
date. Whichever lineage is adjudicated the true text, **the science is the same** — which
removes the worst branch of the remediation, where the two "complete" bodies might have
made materially different public commitments.

**Does NOT change:**

- **The STOP verdict stands.** The posted body measured 9,695 B, not in {9,758, 9,907},
  and adjudicated on size alone.
- **The fire stays HELD; obligation-(2) posting stays HELD.**
- **The posted body is still unread**, and now has *two* refuted derivation hypotheses
  against it. It is the only artifact that says what was publicly claimed, and reading it
  is still the decisive next step.

## 6. Still open

1. **Read the posted 9,695-byte body.** Carter ships it both directions; both sides
   characterize independently, no shared intermediate. ⚠ The independence constraint now
   binds harder, not less: two hypotheses have already died, and a shared prior would make
   the third one no safer.
2. **Which lineage is the true pre-registration text** — now a *presentation* question,
   not a substance one. Carter's call.
3. **The re-post** — new OSF version, never a silent swap.
4. The fire and obligation-(2) remain **HELD** until 1–3 close.
