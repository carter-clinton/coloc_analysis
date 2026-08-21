# POSTING CARD — OSF amendment (occlusion gate recalibration), 2026-08-21

> **For Carter, driving a browser and a Mac terminal. No agent is in the loop for any step on
> this card.** An agent never posts and never fires. Everything below is yours to execute; the
> session's job was to make the bytes correct and to hand you the numbers that prove they are.
>
> Prepared by quick task `260821-jcs` at repo commit `4487a18` on branch `m3-W2-aou-deltas`.
> Seth's final pass (no blocking objection) is banked at
> `.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md` — the seventh
> supporting record.

---

## (i) ANCHORS — the numbers that must still be true when you post

| Quantity | Value |
| --- | --- |
| Repo file (whole) | **42,715 B** / `45453596402874bf6c52ae490241eb86` / **594 lines** |
| Repo file, at commit | `4487a18` (branch `m3-W2-aou-deltas`) |
| **What actually gets posted — the paste block** | **22,945 B** / `422f1f28d6a3b76c7657fadec05a0237` |
| `PRE_EXECUTE_COMMIT` | `d45db429b3fa6c1f08989c418de911a1fe15fbf2` |
| `POSTING_DATE` | `2026-08-21` |

**The paste-block line is the one that matters.** `22,945 B / 422f1f28d6a3b76c7657fadec05a0237`
is the byte-identity **Seth verified himself**, reading the repo copy on your Mac directly. The
re-confirmation performed today advanced the gate commit hash and corrected three prose
statements — **all of them OUTSIDE the paste markers**. The posted body **did not move**. That is
the whole point of the exercise.

> ⛔ **If the Mac-side extraction in step (ii) does not print exactly `22945` and exactly
> `422f1f28d6a3b76c7657fadec05a0237`, STOP. Do not upload.** Paste the two numbers you actually
> got back into the NCSU session and let it diagnose. A mismatch means the file in your hands is
> not the file Seth reviewed, and posting it would put an unreviewed body into a permanent public
> record.

Note the whole-file anchor **did** change today (it was `42,213 B / e1b4a11d…` when Seth read it)
— that is expected and correct: the prose outside the markers changed, the posted body did not.
Seth reviewed the *body*, and the body's anchor is unchanged.

---

## (ii) MAC-SIDE — copy the file down and extract the body

macOS ships the BSD `md5` tool, which prints the digest **after** the filename. Do not reach for
the GNU/Linux spelling; it does not exist on macOS.

```
scp ckclinto@login.hpc.ncsu.edu:/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
    /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/

cd /Users/cc/Documents/NCSU/1.ASHES_Lab_Research/Analyses/coloc_analysis/

awk '/^--- PASTE INTO OSF FROM HERE ---$/{f=1;next} /^--- PASTE ENDS HERE ---$/{f=0} f' \
    osf-amendment-occlusion-gate-recalibration-2026-08-20.md \
    > osf-amendment-occlusion-gate-recalibration-2026-08-21.md

wc -c osf-amendment-occlusion-gate-recalibration-2026-08-21.md    # must read 22945
md5   osf-amendment-occlusion-gate-recalibration-2026-08-21.md    # must read 422f1f28d6a3b76c7657fadec05a0237
```

The `awk` excludes both marker lines by construction, so what lands in the new file is exactly
the body and nothing else.

### ⚠ The two filenames are DIFFERENT, and that is correct

This is the easy mistake, so it is spelled out:

| File | Basename | Which date it records |
| --- | --- | --- |
| Repo source you `scp` down | `osf-amendment-occlusion-gate-recalibration-2026-08-20.md` | the **INSTANTIATION** date |
| File you UPLOAD to OSF | `osf-amendment-occlusion-gate-recalibration-2026-08-21.md` | the **POSTING** date |

The uploaded name matches the template in the prepared (not-yet-appended) deviation entry. A
mismatch between the two basenames is **expected, not an error** — they are different quantities.

---

## (iii) THE OSF PROCEDURE

1. Go to **`osf.io/az52u`** → **Files**.
2. **UPLOAD** `osf-amendment-occlusion-gate-recalibration-2026-08-21.md` as a **NEW file**.

> ⛔ **NEVER use "upload new version" on `trsx5`.** This posts as a new dated record in the chain,
> append-only. After you are done, `trsx5` must **still show exactly 1 revision (2026-07-10
> 13:32)**. A new dated record, never a silent swap.
>
> ⛔ **NEVER paste the text into a wiki or any text box. Upload the FILE.** The 2026-07-10
> hand-paste is precisely how `trsx5`'s posted body came out as a re-rendered lineage —
> see `.planning/osf_deviations.md` lines 190-300. A file upload cannot re-render markup; a
> paste box can and did.

---

## (iv) POST-UPLOAD — capture these four things

The prepared deviation entry needs exactly these. Capture them before you close the tab.

1. **The new file's GUID and its URL.**
2. **The authoritative UTC timestamp**, taken from OSF **Recent Activity**.
   > ⚠ **NOT** the file page's "Date created." That field shows the PARENT record's creation
   > date (2026-04-10, `osf.io/pvb5j`) and will silently give you a date four months wrong.
3. **Re-download the posted file and hash it.** The digest must read
   `422f1f28d6a3b76c7657fadec05a0237`. This closes the loop: what OSF actually stores == what
   Seth actually verified.
4. **Confirm `trsx5` still shows exactly 1 revision.**

---

## (v) WHAT TO PASTE BACK to the NCSU session

Paste all four captures above verbatim, plus the filename as OSF displays it.

With those in hand, the record quick task will:

- append the prepared entry to `.planning/osf_deviations.md` (it is written and waiting in the
  amendment's Post-Paste Reference section — it has never been appended);
- bank the decision `DEC-2026-08-21-occlusion-recalibration-posted`;
- set `HANDOFF.gates.osf_pre_registration`;
- tag the record commit.

None of that runs until your four captures arrive. The gate does not move on an agent's say-so.

---

## (vi) IF IT SLIPS — do NOT hand-edit the date

If posting does not happen on 2026-08-21:

> ⛔ **Do not edit the date by hand, anywhere, for any reason.**

Ask the NCSU session to re-run the engine's Class-P pass with the new `--posting-date`. All three
occurrences (the pre-paste table row, its `SLOT_LEDGER` line, and the paste block's `**Date:**`
line) move together by construction, because Class-P force-substitutes at every occurrence. Then
`guard all` is re-run and fresh anchors are re-issued to you.

Either route changes the paste block — the `**Date:**` line sits INSIDE the markers — so a
date change necessarily retires the `422f1f28d6a3b76c7657fadec05a0237` anchor; do not expect it
to survive a slip. The engine route moves all three occurrences together, re-runs `guard all`,
and re-issues fresh anchors whose only delta from the body Seth verified is that one date
token (re-anchored, disclosed, and checkable). A hand edit can leave the three occurrences
disagreeing and hands you a body whose anchor nobody has re-issued.

The date token appears **only** in those three machine-substituted slots. Today's re-confirmation
deliberately kept it out of the surrounding prose, so a future date change cannot silently rewrite
a sentence about what happened on 21 August 2026 into a false one.

---

## Status

```
measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires.
```
