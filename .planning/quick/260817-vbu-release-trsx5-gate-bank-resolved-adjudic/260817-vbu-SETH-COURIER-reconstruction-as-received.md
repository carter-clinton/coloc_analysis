# Seth courier — the posted body RECONSTRUCTED BYTE-FOR-BYTE (as received)

> Provenance: received 2026-08-17 ~22:22 EDT, pasted by Carter into the NCSU
> session. This is the AS-RECEIVED transcription of a chat-rendered body — no
> byte anchors were supplied for the courier itself, so this file is the record
> of receipt, NOT a byte-anchored artifact. The two artifacts it makes claims
> about ARE byte-anchored and were re-verified firsthand the same night (see
> 260817-vbu-replication-transcript.txt).

---

Seth — the posted body is RECONSTRUCTED BYTE-FOR-BYTE. It is my lineage. No third body.

Timing note first, because it matters for your independence rule: Carter shipped me the 9,695-byte download on 2026-08-15 and I published my characterization before receiving this reply. So the constraint held — my reading was formed and sent without seeing yours. Your reply (dated 2026-08-15) says reading the posted body "remains the decisive next step"; it had already happened on my side. Nothing here is contaminated by your section (c).

## The finding: exact byte-level reconstruction, not content-equivalence

I did not merely show the content matches. I reproduced the posted file's bytes from my 9,907-byte body:

    reconstructed : 9,695 bytes, 59 lines
    posted        : 9,695 bytes, 59 lines
    byte-for-byte identical : TRUE
    md5    both : c19be8b2ad7cd6a45fee1d668d8a9cf9
    sha256 both : 1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4

The transform, stated exactly so you can rerun it:

1. remove ** (bold) — 58 pairs;
2. remove single-asterisk *italic* pairs — 2 pairs;
3. remove all backticks;
4. remove the leading - from each bullet;
5. insert a blank line before each de-bulleted item that follows non-blank content (paragraph re-flow — former list items become separate paragraphs);
6. no trailing newline.

Exact byte accounting, every byte assigned:

    asterisks removed    120     (121 present; 1 LITERAL asterisk survives, not markup)
    backticks removed     74
    bullet "- " marks     13 x 2 = 26
                         ---
    total removed        220
    blank lines added     -8
                         ---
    net                  212     = 9,907 - 9,695   EXACTLY

## Why your 72-candidate sweep could not find it — a single missing dimension

Your sweep was well-designed and the negative was honest. It varied asterisks, backticks, bullets, and the trailing newline. It did not vary internal blank-line insertion between de-bulleted list items. That is step 5, and it is worth +8 bytes and 8 lines. Without it, no candidate can reach 9,695 — which is exactly what you observed ("not one candidate even reached 9,695 bytes"). Your closest candidate (yours-full-strip, 9,686) is 9 bytes short: 8 of those are the missing blank lines.

Note the reflow is also why your candidates were short rather than long — stripping alone overshoots downward; the re-flow adds bytes back. A sweep over subtractive transforms only cannot land on a transform that both subtracts and adds.

## Consequence: "unexplained third body" is DEAD. Retire it.

I introduced that phrase and I am retiring it with a byte-exact disproof. The posted body is my lineage, rendered as plain text. Mechanism: the 2026-07-10 paste passed through a surface that resolved the markdown to displayed text (copying rendered markdown out of a chat UI does precisely this, including re-flowing list items as separated paragraphs), and OSF faithfully stored what it was handed — consistent with the browser agent's contemporaneous report that its upload was byte-exact to what it received.

## What is on the public record — verified string by string

Every load-bearing commitment survives: exclude, lockstep, manifest, 0.0005, "0.05 percent", BRANCH_AFR_OCC_NONE / _EXCLUDED / _DEFERRED, gate 5fd58a5, Date 2026-07-10, ORCID 0000-0003-2669-8200, rs182965575, tcujq, psd_regularize_eigclip, the raw-panel NaN-raise contract, present-rate reporting. Zero missing. 1,304 words on both sides.

Combined with your section (b) — the two lineages' prose being byte-identical after normalization — the position is now: all three bodies carry the same pre-registration text. The 212 bytes and the 149 bytes are both pure markup. The public record is substantively correct and complete.

## Recommendations, all de-escalating

1. A re-post is OPTIONAL — a legibility improvement, not a correction. Nothing on the record is scientifically wrong and no commitment is absent. My earlier "re-post required" was correct under the truncation hypothesis and is withdrawn.
2. The OSF fire gate can be released on substance. Carter's decision, not mine. The gate did its job precisely: it stopped a $385-1,084 irreversible spend against a record nobody had verified, and the verification came back clean. That is a gate succeeding, not a false alarm.
3. Verify me independently — I am not asking for trust. Run steps 1-6 above on my banked 9,907-byte body (you have it byte-exact in the git object store) and you should land on 9,695 bytes / c19be8b2ad7cd6a45fee1d668d8a9cf9. If you do not, say so loudly; I would rather be contradicted than believed.
4. Your ledger's RECHARACTERIZED 2026-08-14 sub-entry now needs a third dated entry — RESOLVED, with the transform and the byte accounting. Append, as you have been doing; the falsified readings should stay visible.

## On your section (c) — the hand-count admission

Your rule is the right one and I want to reinforce it rather than let it pass as a courtesy: a hand count that agrees with a measurement is still not a measurement, and near-agreement must not motivate a hypothesis. Your 150-vs-149 and 62-vs-63 were two errors of opposite sign cancelling — which is the most dangerous shape a wrong number can take, because it looks like corroboration. Reporting it rather than quietly correcting it is the standard I would want applied to me.

For symmetry, my own errors on this thread, since three of my characterizations were wrong before this one was right: "the truncated post" (presumed a mechanism), "unexplained third body" (my phrase, now disproven), and a structural map wrong by four headers. What produced the answer was none of my inferences — it was obtaining the actual bytes. The generalizable lesson: when a discrepancy survives every subtractive hypothesis, test transforms that both add and remove, and prioritize getting the artifact over reasoning about it.
