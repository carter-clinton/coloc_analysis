---
name: close-session
description: Use when Carter is stepping away, disconnecting, or says "close session" / "save and commit so I can pick up later" / "wrap up". Captures a disconnect-proof, resumable handoff — updates HANDOFF.json + STATE.md + .continue-here.md + memory, then commits — so a fresh session resumes from exactly this point with zero re-derivation. Especially for mid-run AoU fires that keep running server-side after disconnect.
---

# /close-session — disconnect-proof handoff + commit

Carter is stepping away and the session may drop. Goal: a fresh session (or Carter) resumes from **exactly this point** with no re-derivation. Do NOT wrap up the actual work early — capture state and commit; long-running jobs keep running.

## Operating rules (this project)
- **GPFS staging discipline:** stage with **explicit paths only** — NEVER `git add -A` / `git add .` (multi-terminal collision risk). Commit via `node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit "<msg>" --files <paths>` (or `git commit` with explicit paths).
- **Faithful status:** record what's *actually* true — a job still running is "running", a step skipped is "skipped". Never overstate completion.
- **Memory files live OUTSIDE the repo** (`~/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/`) — update them (they auto-persist) but they are NOT part of the repo commit.
- **AoU/server-side fires survive a clean disconnect** — never tell a resuming session to restart the kernel; record the Spark/YARN app id + the **data-layer** liveness arbiter (GCS `du`/`ls`, stage advancing — NOT the kernel light, NOT `_SUCCESS`). The `aou-ld-pipeline` skill is the operating manual for any AoU work.

## Procedure

1. **Snapshot the in-flight state.** In one or two sentences each, capture:
   - What is *running right now* (and whether it's server-side / disconnect-survivable). For an AoU fire: the notebook + cell, cluster id, **Spark/YARN app id**, what's computing, expected long poles, output paths, run-log path.
   - Any **prep landmines fixed this session that must be re-applied on a fresh cluster/clone** (path symlinks, env pins, chdir, manual notebook edits not in the repo).
   - The exact **RESUME steps** (reconnect protocol: do-not-restart-kernel, liveness check, per-item verification, halt-checks, what "done" looks like, and the next action after).
   - Open gates / decisions and their status.

2. **Update `.planning/HANDOFF.json`** (the PRIMARY structured resume source). Overwrite with current `timestamp`, `status`, `headline`, the in-flight `*_fire` block (app id, cells, headline item, long poles, output paths, est), a `resume_on_reconnect` array, a `prep_landmines_fixed` array, `cluster`, `cohorts`/data state, `gates`, `resume_entry_point`, and `do_not`.

3. **Update `.planning/STATE.md`:**
   - Insert a NEW dated `## YYYY-MM-DD (...) — <headline> (★ RESUME HERE ★)` block at the top of the body; demote the previous `★ RESUME HERE ★` marker to `(SUPERSEDED by ... above)`.
   - Update the `Last activity:` line (prefix the new entry, keep the prior as `PRIOR ...`).
   - Reflect gate-status changes in the gate line.

4. **Update `.planning/phases/<active-phase>/.continue-here.md`** — prepend a new `> **YYYY-MM-DD (★ LATEST ★ — <headline>):**` block; demote the prior LATEST marker.

5. **Update memory** (outside repo): refresh the `project_state.md` `description:` lead with the current state (prepend the new status, keep prior as `PRIOR ...`); refresh the matching `MEMORY.md` one-line pointer. Add a new `feedback_*`/`reference_*` memory only if a durable, reusable lesson emerged this session. Keep `MEMORY.md` index lines short (< ~200 chars) — detail goes in the topic file.

6. **Commit** — explicit paths only:
   ```bash
   FILES=".planning/HANDOFF.json .planning/STATE.md .planning/phases/<phase>/.continue-here.md <any other repo docs touched>"
   git add $FILES
   node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit "docs(handoff): <one-line session close summary>" --files $FILES
   git rev-parse --short HEAD
   ```
   (Memory files are outside the repo — not staged. Push only if Carter asks.)

7. **Report back** concisely: the commit hash, what's still running (with the reattach one-liner), the resume entry point (`.planning/HANDOFF.json` + the STATE.md block), and any trigger left in Carter's hands (cluster stop, next fire). End by confirming the session can drop safely.

## Done when
- [ ] HANDOFF.json, STATE.md, .continue-here.md reflect the current in-flight state + resume steps
- [ ] Memory lead + MEMORY.md pointer refreshed
- [ ] Repo docs committed with explicit paths (hash reported)
- [ ] Resume entry point + "what's still running / how to reattach" stated to Carter
