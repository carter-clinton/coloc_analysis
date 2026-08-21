# Deferred items — quick 260821-jcs

## DI-1 — `260821-jam` is a DUPLICATE of this task, from a parallel terminal, with STALE anchors

**Found during:** Task 3, on `git log` after the close-out commits.

**What:** `.planning/quick/260821-jam-bank-seth-final-pass-as-7th-record-pre-p/260821-jam-PLAN.md`
carries the same objective as `260821-jcs` (bank Seth's final pass as the 7th record; execute the
RE-CONFIRMED-AT-POSTING advance by the engine; write a posting card). Its two commits — `41349e2`,
`4307278` — touch ONLY its own PLAN.md. It has executed no artifact work; every artifact in this
arc was produced by `260821-jcs`.

**The stale pin:** jam's plan REQUIREs the amendment's PRE-task whole-file anchors at lines 124,
279 and 321 — `42,213 B / 591 lines / e1b4a11d18ad2907af4f0a93fd5747d2`. Commit `4487a18`
(this task) legitimately superseded those to **42,715 B / 594 lines /
`45453596402874bf6c52ae490241eb86`**. If jam executes those assertions unchanged it will go RED on
a stale pin, not on a real defect.

**The paste-block anchor jam pins 15 times — `422f1f28d6a3b76c7657fadec05a0237` — is UNCHANGED and
still correct.** That is the invariant that matters, and it survived.

**NOT FIXED, deliberately.** Editing another live terminal's plan file is precisely the
multi-terminal collision the project memory (`feedback_multi_terminal_staging`) was baked to
prevent, and jam's own terminal is already reconciling (its `41349e2` message reads "the 7th record
landed from a parallel terminal"). This needs a human routing decision, not an agent edit.

**Recommended:** close `260821-jam` as superseded by `260821-jcs`. Do NOT let it execute its
engine step — a second Class-P pass would advance `PRE_EXECUTE_COMMIT` again to a newer HEAD,
churning the gate hash for no reason and invalidating the anchors already handed to Carter on the
posting card.

**RESOLVED 2026-08-21 14:45 EDT (jam side):** closed as SUPERSEDED — see `.planning/quick/260821-jam-bank-seth-final-pass-as-7th-record-pre-p/260821-jam-SUMMARY.md`. Cause corrected there: not a parallel terminal but a duplicated orchestration of ONE `/gsd-quick` invocation inside the same session (background skill-runner = `jcs`, foreground = `jam`). No engine re-run; `d45db42` stands; no jam executor was ever spawned.
