# .planning/

GSD state lives here. Every entry is persistent across sessions and
tracked in git.

| File / dir | Role |
|---|---|
| `PROJECT.md` | Who, what, where, why, constraints. Condensed from `GSD_BRIEFING.md`. |
| `REQUIREMENTS.md` | 12 numbered requirements with acceptance criteria. One per gap from `GSD_BRIEFING.md` §5.2 plus REQ-12 for the legacy-path-parameterization task discovered during recovery. |
| `DECISIONS.md` | Load-bearing decisions with dates, alternatives considered, and rationale. |
| `ROADMAP.md` | Phase index. Tier tags (T1/T2/T3), dependencies, REQ mappings, per-phase slice outlines. |
| `data_access.md` | Track 0a DUA application tracker — the single longest critical path. |
| `checkpoints/` | `T1_review.md` and `T2_review.md` — go/no-go verdicts written at the end of each tier before the next one is planned. |
| `intel/` | Populated by `/gsd-map-codebase` or `/gsd-intel` after the first execution pass. Not yet populated. |

## Starting a new GSD session in this directory

Recommended sequence:

```bash
conda activate gsd-tools
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/

# Normalize and register this project with GSD v1
/gsd-new-project     # reads PROJECT.md, REQUIREMENTS.md, DECISIONS.md, ROADMAP.md

# Plan Phase 0 (T1, infrastructure + Track 0a DUA kickoff)
/gsd-discuss-phase 0 --auto
/gsd-plan-phase 0
/gsd-execute-phase 0
```

Do **not** plan T2 phases (3, 4, 8) before `.planning/checkpoints/T1_review.md`
exists with a go verdict. Do **not** plan T3 phases (6, 7, 10) before
`.planning/checkpoints/T2_review.md` exists with a go verdict. See REQ-11.
