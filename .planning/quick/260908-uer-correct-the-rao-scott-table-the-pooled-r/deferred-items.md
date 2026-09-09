# Deferred — `260908-uer`

Out of scope for this DOCS-ONLY estimator correction. Recorded, not acted on.

---

## RESOLVED (not deferred) — `260908-u5k` D1 is CLOSED, and the COURIER was the right side

`260908-u5k` deferred item **D1** flagged that `.planning/osf_deviations.md` §(10b) gave
**1.969** for the drop-`sub13` uncorrected phi while the 2026-09-02 courier body gives
**1.99**, and correctly declined to adjudicate it (adjudicating would have meant
re-deriving a number, which that DOCS-ONLY task must not do).

**RESOLUTION: the COURIER was right; §(10b) carried the artifact.** Under the correct
subset estimator the value is **1.988** (≈ 1.99). §(10b)'s **1.969** was produced by the
fixed all-21 pooled rate.

⭐ **This is a reconciliation, not a new number, and the tree already said so.** §(7) of the
same file has reported the matching figures since before §(10b) existed, and they were
measured here rather than copied:

| §(7) statement (pre-existing, `.planning/osf_deviations.md`) | corrected §(10b) | superseded §(10b) |
| --- | --- | --- |
| leave-one-**WINDOW**-out worst case **1.99 at p 0.0063** (`:834`, "its minimum **is the headline itself**" = drop-`sub13`) | **1.988 / 0.0063** | 1.969 / 0.0071 |
| leave-one-**PARENT**-out worst case **p 0.073** (`:838`; removing parent `00060` removes both chr15 windows) | **1.518 / 0.0732** | 1.535 / 0.0678 |

The superseded fixed-rate column matched **neither**. The corrected column matches **both**,
and `p 0.0063` is an exact string match already present in the file at line 834.

**Where recorded:** in the authoritative document itself —
`.planning/osf_deviations.md` §(10b), the paragraph beginning
*"A DISCREPANCY STANDING IN THE RECORD IS CLOSED BY THIS CORRECTION"*.

⚠ **`260908-u5k`'s own `deferred-items.md` was deliberately NOT edited.** It is a dated task
record and D1 was **true when written**. Re-splicing it would rewrite a correct historical
observation; even an appended annotation would be a write to a dated record, which this
task's constraints forbid. The closure is discoverable from §(10b), which names `260908-u5k`
and `D1` explicitly.

---

## D1 (uer) — the 2026-09-02 courier's `260908-u5k` annotation carries three superseded figures

**File:** `.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md:147`

The SCOPE-LIMITED annotation added by `260908-u5k` reads *"the corrections give
1.931 / 1.652 / 1.564 / **1.249**"*. Under the corrected estimator these are
**1.931 / 1.675 / 1.579 / 1.241** — three of the four moved.

⭐ **Nothing false and load-bearing is left standing.** The annotation exists to support one
claim: *"and the last falls BELOW 1.3."* The corrected last value is **1.241**, which is
still below 1.3. The claim is **unaffected**. Its companion list of uncorrected figures
*"(2.36 / 1.97 / 1.99 / 1.52)"* supports only *"all > 1.3"*, also unaffected — though under
the correction the drop-`sub13` and drop-`sub12` values are now **both** ≈ 1.99, so the
`1.97` element is itself an artifact of the same fixed-rate error.

**Why deferred, not fixed here:**

1. It is a **dated communication record** — this task's constraints keep those untouched.
2. Editing it would **break a live hash pin**: `.planning/STATE.md` records the courier as
   **621 lines, md5 `f52b76ce73b5f83d03a6e09e2822563f`** (both re-measured this session and
   still holding). A DOCS-ONLY numeric correction should not expand its blast radius into a
   file that another live document hashes.
3. The correct treatment is **annotate-forward**, which is a separate decision about a
   document that was **sent to a third party** — not a side effect of fixing our own table.

---

## D2 (uer) — dated task records now quote the superseded table, by design

These are **correct as historical records** and must not be rewritten. Listed so a future
reader does not mistake them for live figures:

| Record | What it carries |
| --- | --- |
| `.planning/quick/260908-tnd-.../CONTENT-SPEC.md:46-62` | the superseded table as specified |
| `.planning/quick/260908-tnd-.../SUMMARY.md:107` | a verification count `0.0366 x6, 0.0556 x6` — **measured true at the time**. Re-measured after this edit: each is now **x1** (the correction note alone), and the corrected `0.0326`/`0.0517` stand at **x7** each — the six sites the old figures held, **plus** the correction note that names what they replaced |
| `.planning/quick/260908-u5k-.../CONTENT-SPEC.md`, `SUMMARY.md` | `1.931 / 1.652 / 1.564 / 1.249` |
| `.planning/quick/260908-u5k-.../deferred-items.md` | D1 as originally raised |

No action. The authoritative figures live in `.planning/osf_deviations.md` §(10b), which now
carries its own correction note naming what it replaced.

---

## D3 (uer) — `tcujq` remains DEFERRED

Unchanged by this task, and explicitly out of scope. Note that `HANDOFF.json` still records
the open `tcujq` question (`osf_deviations.md:133`/`:166` cite the trsx5 update as
**WITHDRAWING** the NaN→0 policy that `tcujq` is cited as pre-registering). Both line pins
were **re-measured this session and still resolve correctly** — they sit inside the frozen
1-531 prefix and were not moved by this edit.
