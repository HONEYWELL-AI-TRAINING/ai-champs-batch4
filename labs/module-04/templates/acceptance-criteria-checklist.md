# Acceptance-Criteria Checklist — Task Comments

Copy to `specs/001-task-comments/acceptance-checklist.md` and tick each item in
Lab 03. Every row must trace to an acceptance criterion (`AC-xx`) in `spec.md`
and to at least one automated test. Fill the AC and test columns from your own
spec — the criteria below are a starting scaffold; your `/speckit.specify` +
`/speckit.clarify` output is authoritative.

| # | Criterion (must be mechanically checkable) | spec AC | Test(s) | Backend ✅ | Frontend ✅ |
|---|-------------------------------------------|---------|---------|:---------:|:----------:|
| 1 | `GET /api/tasks/{id}/comments` returns `200` with an array, oldest first | | | | |
| 2 | `GET` for a non-existent task returns `404` | | | | |
| 3 | `POST /api/tasks/{id}/comments` with valid `{author, body}` returns `201` and the created comment | | | | |
| 4 | `POST` with missing `author` **or** missing `body` returns `422` | | | | |
| 5 | `POST` with `body` longer than the spec's limit returns `422` | | | | |
| 6 | `POST` with `author` longer than the spec's limit returns `422` | | | | |
| 7 | `POST` to a non-existent task returns `404` | | | | |
| 8 | `DELETE /api/tasks/{id}/comments/{commentId}` returns `204`; the comment is gone | | | | |
| 9 | `DELETE` of a non-existent comment returns `404` | | | | |
| 10 | Deleting a task removes its comments (FK cascade or explicit) | | | | |
| 11 | All comment DB access is in the repository layer | | (code review) | | — |
| 12 | `database/schema.sql` contains the new table; no migration tooling added | | (code review) | | — |
| 13 | The three backends return byte-identical JSON for the same request | | `port-endpoint` skill compare | | — |
| 14 | Board card shows a comment count only when count > 0 | | | — | |
| 15 | Clicking the count expands the thread; comments show author + time | | | — | |
| 16 | The add-comment form rejects an empty author or empty body client-side | | | — | |

## Sign-off

- [ ] Every row above is ✅ in the relevant column(s).
- [ ] `pytest` / `dotnet test` / `./mvnw test` and `npm test -- --run` all green.
- [ ] Each `AC-xx` in `spec.md` appears at least once in the "spec AC" column.
- [ ] No implemented behaviour is missing from `spec.md` (nothing unspecified
      shipped).
