# Gate controls for `260815-i2v` — the verify block was SEEN TO FAIL before it was trusted

> Run by the planner on the NCSU node, 2026-08-15, read-only, `$0`. Nothing fired, nothing
> committed by this file's production. Stub controls were written to the session scratchpad
> (outside the repo) and are not part of the deliverable.

Project rule: *a green assertion needs a negative control — green is evidence ONLY if you have
seen it fail.* The Task 1 `<automated>` gate was therefore driven through one positive and three
negative controls **before** the plan was finalized.

| control | defect injected | expected | observed |
|---|---|---|---|
| `pos` | none (fully compliant stub) | all GREEN, `RC=0` | **V1 V1b V2 V3 V4 V5 V6 all PASS, RC=0** |
| `neg_trunc` | full sha256 replaced by `40831cdebcc71de21cd536fa…` | RED | **RED on four independent detectors** — V1 (`len=24` unexpected run), V1b (shipped `_hexlen`), V2 (full anchor absent), V3 (ellipsis-truncated digest) |
| `neg_arith` | closing line's `` `152 - 3 = 149` `` reworded | RED | **V5 RED** — `missing: \`152 - 3 = 149\`` |
| `neg_hex` | rogue 20-char hex run appended | RED | **V1 + V1b RED** — `len=20 deadbeefcafebabe0123` |

Two properties this establishes, neither of which was assumed:

1. **Truncating the sha256 cannot pass this gate.** It is caught four separate ways, one of them
   the *shipped* `_hexlen` sub-mode of `260814-guk-verify.sh` — the same code path the fire card
   is checked with, not a local re-implementation that could stay green while the shipped function
   rotted.
2. **The arithmetic literals are load-bearing, not decorative.** Reworded prose that still reads
   correctly to a human fails the gate, which is the point: the last document in this chain that
   was checked by reading rather than measuring is the one that produced the refuted hypothesis.

Baseline captured in the same session, **before** any file in this quick was written:

```
bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh fire
  -> RESULT: ALL CHECKS PASSED (section: fire)   [F1..F10, 10/10]   exit 0
```

Any `fire` result other than 10/10 after Task 1 is therefore attributable to Task 1 and is a
**STOP**, not something to improvise around.
