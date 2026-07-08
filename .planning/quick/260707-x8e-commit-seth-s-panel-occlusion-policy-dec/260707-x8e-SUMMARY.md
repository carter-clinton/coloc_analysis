# Quick 260707-x8e — SUMMARY

**Status:** Done (docs-only, byte-verified). **Commit:** `_this-commit_`. **Branch:** `m3-W2-aou-deltas`.

## What landed

`.planning/amendments/m3_panel_occlusion_policy_decision.md` — Seth's authoritative policy-decision
record, committed **byte-verified**: a self-locating `>` header + the verbatim body, whose last
5247 bytes hash to **SHA-256 `42d701677ac8bc85d3b03f390413c4406ba65f3b11ab085350e560738ab209ef`
== Seth's anchor** (assembled file 5897 B total = 650 B header + 5247 B body).

## Byte-fidelity method

Transcribed the paste to scratch → `sha256sum` matched Seth's anchor only with **no trailing
newline** (5247 B, not 5248) → assembled `header + verified-body` → re-verified
`tail -c 5247 | sha256sum == anchor` before committing. Did NOT fabricate; the anchor arbitrated.
(The prose-only doc survived the chat paste intact — unlike the still-blocked verdict, whose table
was mangled in transit.)

## The decision (now the in-repo authority)

**Exclude-in-lockstep across panel AND sumstats + a mandatory, load-bearing provenance manifest.**
NaN→0 dead (fabricates r=0 vs common neighbors); panel-only-exclude unsafe (orphans sumstats-present
`rs182965575`); Flag converges on the same fit but adds machinery. Scope = upstream span-filter for
all 276 regions + lockstep sumstats-side drop at m3-04; OSF amendment-update = exclusion+provenance,
never zeroing. **This doc CLOSES the verdict's open "exclude-vs-flag" policy-call section.**

## Guardrails honored

m3-06 stays HELD; `condition_ld_matrix.py` FROZEN; raw-panel NaN-raise intact; OSF amendment /
coverage flag / tag untouched; no loop contact; no source code changed. Explicit-path staging only.

## Still open (not this task)

- **Verdict `m3_region1_nan_geometry_verdict.md` STILL BLOCKED** — chat paste mangled its table;
  needs base64 or a filesystem file-drop to commit byte-faithful (anchor `4543dcf4…` / 5012 B).
- Seth's new requirements to carry into the genome-wide build: manifest is a hard requirement
  (per-variant schema); report the genome-wide **present-rate** per ancestry; span-filter for all 276.
- Carter/loop: AoU loop-state (in-perimeter) unresolved; do not re-fire until the fix lands.

Plan: `260707-x8e-PLAN.md`.
