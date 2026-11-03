# Feature Request — Soft-Delete for Tasks (Brownfield)

This is the **informal request** that lands in your queue. It is not a spec.
Labs 02–03 turn it into an archaeology note, a change-impact analysis, a scoped
specification, and a minimal, regression-safe implementation.

---

## The ask (as a team lead would raise it)

People delete tasks by accident and there's no undo. Let's make delete
recoverable.

- Deleting a task should **hide** it, not destroy it. It vanishes from the board
  and from the normal API responses.
- There should be a **"Deleted tasks"** view where you can see what was deleted
  and **restore** one.
- Keep a way to **permanently** remove a task for real (e.g. it was spam) — but
  that should be a separate, deliberate action.
- A restored task comes back exactly as it was, comments and all.

## What we know it will touch (why this is brownfield, not a new feature)

- The `DELETE /api/tasks/{id}` behaviour that already exists and is already
  tested — its contract changes from "row is gone" to "row is hidden".
- Every place that lists or fetches tasks — they must now exclude the hidden
  ones by default.
- The `task_comments` cascade from Module 04 — comments must survive a soft
  delete and come back on restore.
- The `GET /api/tasks/stats` endpoint from Module 03 — should deleted tasks
  count?
- The React board and its existing tests that assume six seeded tasks.

## Out of scope

- Auto-purge after N days.
- A trash/recycle-bin retention policy.
- Bulk restore / bulk purge.
- Auditing *who* deleted or restored (no auth in this app).

## Open questions for the spec (don't answer here)

- Soft-delete marker: a `deleted_at` timestamp, or a `deleted` boolean?
- Does `GET /api/tasks/{id}` on a soft-deleted task return `404`, or `200` with
  a flag?
- New endpoints, or query params on the existing ones? (`?deleted=true`,
  `POST .../restore`, `DELETE .../permanent`?)
- Do soft-deleted tasks count in `/api/tasks/stats`?
- Can you still `POST` a comment to a soft-deleted task?
- What does the existing seed data / existing test suite expect, and what has to
  change there?
