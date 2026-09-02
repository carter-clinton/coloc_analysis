# Deferred items — quick-260901-rvu

Out-of-scope discoveries. **Not fixed by this task** (SCOPE BOUNDARY: only issues
directly caused by this task's changes are auto-fixed).

## 1. `.planning/STATE.md` frontmatter does not parse as strict YAML — PRE-EXISTING

**Measured, both sides:**

```
HEAD FAILS: while parsing a block mapping
NOW  FAILS: while parsing a block mapping
```

`yaml.safe_load` on the frontmatter block fails at the same position **at
`HEAD` (`a7f1291`) and after this task's edit** — line 17, inside the
`last_activity` scalar, at the 2026-09-01 sweep entry's embedded double quotes
(`"at least one of three"`) inside a double-quoted YAML scalar.

**Not introduced here, and not worsened:** the segment prepended by this task
contains **0** `"` characters (measured), so it adds no new embedded quote.

**Why it is NOT fixed here:** the repair is a re-quote of a ~20 KB historical
narrative scalar. That is a large edit to the project's own record, outside this
task's scope, and it would rewrite bytes of entries other tasks may cite. It also
touches the surface `gsd-tools state *` reads, so it deserves its own task with
its own before/after parse assertion and a negative control.

**Suggested fix when scheduled:** convert `last_activity` (and `status` /
`stopped_at`, which carry the same hazard) to YAML block scalars (`|`), which
require no escaping, and add a test asserting the frontmatter round-trips through
`yaml.safe_load`.
