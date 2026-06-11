<!-- GSD:project-start source:PROJECT.md -->
## Project

**PROJECT.md — coloc_analysis**

### Constraints

- **100% public data.** No wet-lab, no functional validation, no proprietary
  or industry datasets. Standard academic DUAs for UK Biobank, UKB-PPP,
  deCODE, FinnGen, MVP, All of Us, BBJ, Pan-UKBB, etc.
- **Solo author.** Rigor must come from multi-method triangulation,
  pre-registration on OSF, Snakemake-pinned pipeline, hold-out replication —
  not from internal QC.
- **Timeline is not a binding constraint.** Rigor and impact matter more than
  speed. Do not compress phases to save time.
- **No web/JS stack.** Relevant stack is R (`coloc`, `susieR`, `TwoSampleMR`,
  `MRPRESSO`, `hyprcoloc`), Python (LDSC, PRS-CSx, selscan, Enformer / Borzoi
  inference), bash, Snakemake, conda. Skip any skill pack aimed at React /
  Next / Vite / TypeScript.
- **Data access lead times are the real critical path.** UKB-PPP, deCODE,
  FinnGen, MVP, All of Us, BBJ, Pan-UKBB require DUAs that take weeks to
  months. These must run in parallel with Phase 0 from Day 1 (REQ-1).
- **GPFS filesystem.** Do **not** use worktree isolation. GSD mode is
  `solo` with `git.isolation: branch`.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

- **`aou-ld-pipeline`** (`.claude/skills/aou-ld-pipeline/SKILL.md`) — operating manual for the All of Us genome-wide cohort build (AOU-1) and per-region LD panel (AOU-2). Auto-surfaces on AoU pipeline / cohort / LD work. Holds the fresh-clone re-run checklist (incl. the manual notebook edits NOT in the templates), the verification invariants (`_SUCCESS` ≠ data; liveness = GCS listing not the kernel light; `force_fresh=False` on resume), the **RW2.0-is-a-mirror / VPC-SC perimeter** facts (regenerate in-perimeter rather than cross-perimeter transfer), the "do not run from `main`" branch trap, the Wave 2 gate sequence, and the catastrophe→recovery recipes. **Read it before any AoU fire.**
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
