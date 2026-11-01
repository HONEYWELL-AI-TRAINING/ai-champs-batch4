# Lab 03 — Implement & Validate

**Time:** ~35 min · **Surface:** Copilot Chat + terminal ·
**Prereq:** Lab 02 complete; database + Python backend + frontend running

## Objective

Implement `tasks.md` with `/speckit.implement`, verifying after **each** task,
then validate the feature against every acceptance criterion and port it to a
second backend using the Module 02 `port-endpoint` skill. Output: a working,
tested comments feature and a filled acceptance checklist.

## Why it matters for the enterprise

Spec-driven implementation is not "let the agent run" — it is executing a
reviewed plan task by task, each one validated before the next. That is what
makes the result traceable: when `T004` is done, you can point at the code, the
test, and the requirement. And because the spec fixed the response shapes,
porting to the other backends is a mechanical, checkable step rather than a
re-interpretation.

## Step 1 — Implement, task by task

Start on the Spec Kit feature branch. In Copilot Chat:

```
/speckit.implement
```

Spec Kit works through `tasks.md`. **Do not accept it all in one go.** After each
task (or small group), stop and verify:

| After | Verify |
|-------|--------|
| T001 (schema) | Re-load schema into a clean DB; it applies without error |
| T002–T004 (backend) | `pytest -q` for the affected tests; the endpoint responds |
| T005 (backend tests) | Full `pytest` green |
| T006–T008 (frontend) | `npm run dev` — badge appears, thread expands, form posts |
| T009 (frontend tests) | `npm test -- --run` green |

Reload the schema (Docker example):

**macOS / Linux**

```bash
docker exec -i taskboard-db psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS tb_check;"
docker exec -i taskboard-db psql -U postgres -d postgres -c "CREATE DATABASE tb_check;"
docker exec -i taskboard-db psql -U postgres -d tb_check < database/schema.sql
```

**Windows (PowerShell)**

```powershell
docker exec -i taskboard-db psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS tb_check;"
docker exec -i taskboard-db psql -U postgres -d postgres -c "CREATE DATABASE tb_check;"
Get-Content database/schema.sql | docker exec -i taskboard-db psql -U postgres -d tb_check
```

Run backend + frontend tests:

**macOS / Linux**

```bash
cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd ..
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q ; cd ..\frontend ; npm test -- --run ; cd ..
```

> **Use your Module 02/03 tools:** feed `/speckit.implement` a scoped context
> with `/context-brief` when a task needs it; switch to the **Test Author** chat
> mode for `T005` / `T009`; commit after each green task so you can bisect.

## Step 2 — Commit per task

```bash
git add -A && git commit -m "T004: comments router (GET/POST/DELETE /api/tasks/{id}/comments)"
```

Record the commit hash against the task in
`specs/001-task-comments/traceability.md` (the **Commit / PR** column).

## Step 3 — Validate against acceptance criteria

**macOS / Linux**

```bash
cp ../module-04/templates/acceptance-criteria-checklist.md specs/001-task-comments/acceptance-checklist.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-04\templates\acceptance-criteria-checklist.md specs\001-task-comments\acceptance-checklist.md
```

For every row: fill in the `AC-xx` from your `spec.md`, name the test that
proves it, and tick the box only when that test passes. Exercise the error cases
by hand too:

```
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/api/tasks/1/comments -H "Content-Type: application/json" -d "{\"author\":\"Ana\"}"
# expect 422  (missing body)

curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/tasks/9999/comments
# expect 404  (missing task)
```

Any criterion you can't tick is a bug **or** a spec gap — decide which, and fix
it in the right place.

## Step 4 — Port to a second backend with the skill

Start both backends (Python `:8000`, .NET `:5088`). In Copilot Chat / CLI:

```
Follow .github/skills/port-endpoint/SKILL.md to port the task-comments feature
from the Python backend to the .NET backend. The response shapes are fixed by
specs/001-task-comments/spec.md and its contracts/ — match them exactly.
```

Then verify parity with the bundled script:

**macOS / Linux**

```bash
.github/skills/port-endpoint/scripts/compare-responses.sh "/api/tasks/1/comments"
```

**Windows (PowerShell)**

```powershell
.\.github\skills\port-endpoint\scripts\compare-responses.ps1 -Path "/api/tasks/1/comments"
```

Expect `IDENTICAL`. Run `dotnet test`. (Java is the same procedure — do it if
you're running that backend.)

## Step 5 — Update the contract and open the PR

- Confirm `T010` updated the API-contract table in `usecase.md`.
- Run the **API Reviewer** chat mode over the full diff one last time.
- Push and open a PR. Let **Copilot code review** (Module 02, Lab 07) run.

```bash
git push -u origin 001-task-comments
gh pr create --fill
```

## Verify

- [ ] All tasks in `tasks.md` are done and committed, one commit per task.
- [ ] `pytest`, `dotnet test` (ported backend), and `npm test -- --run` are green.
- [ ] `acceptance-checklist.md` is fully ticked, each row bound to a passing test.
- [ ] `compare-responses` shows `IDENTICAL` for the comments routes across
      backends.
- [ ] `usecase.md` lists the three new endpoints.
- [ ] `traceability.md` has commit hashes in the implementation column.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `/speckit.implement` runs away / does many tasks at once | Interrupt, ask it to do "only T00X, then stop for review". |
| Schema won't load — FK error | The `task_comments` FK references `tasks(id)`; ensure the `tasks` table is defined first in `schema.sql`. |
| Frontend badge always shows | Spec said "hidden when 0" — that's AC row 14; it's a real bug, fix the component. |
| `compare-responses` diff on timestamps | Key casing (`created_at` vs `createdAt`) is allowed and the script normalises it; a *value* or *field* diff is a real port bug. |
| Ported backend test count looks low | Mirror every Python test case in xUnit — the skill's SKILL.md says to. |

## Recap & carry-forward

The feature is built, validated, and consistent across backends — every line
traceable to a requirement. **Lab 04** changes a requirement and practises
change control: spec first, then plan, tasks, code — and compares that to doing
the same change prompt-only.
