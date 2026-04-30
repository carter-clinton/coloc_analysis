# m2_post_m3_rerun_queue.tsv status legend

Documented status values for the `status` column of
`.planning/m2_post_m3_rerun_queue.tsv`:

| status                | meaning                                                           |
|-----------------------|-------------------------------------------------------------------|
| not_started           | Obligation queued; no work yet                                    |
| in_flight             | LSF jobs submitted; outcomes pending                              |
| partially_completed   | Some sub-tasks completed; remainder re-routed to peer obligation  |
| completed             | All sub-tasks DONE; artifact superseded                           |

`partially_completed` was introduced 2026-04-29 by quick task `260429-tq9`
for row M2-POST-M3-08, where 9 of 13 LSF jobs completed cleanly and the
4 AFR EXITs were re-routed to sibling obligation M2-POST-M3-03 (AFR mtCOJO
with AoU AFR LD panel) — already queued and `not_started` since 2026-04-27.
The handoff is informational; M2-POST-M3-03 already covers the AFR re-fire
scope independently.

When a row is marked `partially_completed`, the `current_artifact` column
is appended with a `; HARVEST <date>:` separator documenting the partial
disposition and naming the receiving sibling obligation (if any). The
original artifact path remains parseable as the substring before the
separator.
