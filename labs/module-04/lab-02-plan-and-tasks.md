# Lab 02 — Plan & Tasks

**Time:** ~25 min · **Surface:** Copilot Chat (Spec Kit commands) ·
**Prereq:** Lab 01 complete (clarified `spec.md` exists)

## Objective

Turn the specification into a reviewed **architecture plan** (`plan.md`) and a
**task list** (`tasks.md`) of small, independently verifiable units — then run
`/speckit.analyze` for cross-artifact consistency and build the first half of
the **traceability matrix** (REQ → TASK).

## Why it matters for the enterprise

The plan is where architectural decisions get made *and written down* —
reviewable before a line of code exists. The task list is where a feature
becomes work that can be checked one piece at a time, instead of a big-bang diff.
And the traceability matrix is what lets an auditor (or the next engineer) answer
"why does this code exist?" with "REQ-04" instead of a shrug.

## Background

| Command | Produces | Derived from |
|---------|----------|--------------|
| `/speckit.plan` | `plan.md` (+ often `data-model.md`, `contracts/`, `research.md`) | `spec.md` + `constitution.md` |
| `/speckit.tasks` | `tasks.md` — ordered, numbered, each independently verifiable | `plan.md` |
| `/speckit.analyze` | A consistency report across spec / plan / tasks | all three |

---

## Step 1 — Generate the plan

In Copilot Chat:

```
/speckit.plan

Target the Python backend first (we port to .NET and Java in Lab 03). Use the
existing stack and patterns — FastAPI, SQLAlchemy async, the repository/service/
router layering already in backend-python/. Frontend: React + the existing
services/ + components/ structure, plain CSS.

Decisions to make explicit in plan.md:
- The task_comments table definition to add to database/schema.sql (columns,
  types, FK to tasks with ON DELETE CASCADE, index on task_id).
- New repository / service / router methods and their signatures.
- DTO / schema shapes for request and response.
- Frontend: which components change (TaskCard), which are new (a thread + form),
  how the count is fetched.
- Test approach per layer.

Do not write implementation code. This is the design.
```

## Step 2 — Review the plan like a senior engineer

Open `plan.md` (and `data-model.md` / `contracts/` if generated). Check against
the **constitution**:

- [ ] All comment DB access is in a **repository** method — nothing in the
      service or router does SQL.
- [ ] The schema change is an edit to **`database/schema.sql`** — no Alembic, no
      `Base.metadata.create_all`, no `ddl-auto` change.
- [ ] `404` / `422` mapping matches the existing error contract; no new codes.
- [ ] The response shapes are specified field-by-field (so the .NET/Java ports
      can match them exactly).
- [ ] The plan says how each layer is tested.

Push back in chat where it's weak, e.g.:

```
plan.md has the service building the response dict with a raw SQL count. Move
all queries into repository methods and have the service compose DTOs only.
Regenerate the affected sections.
```

Switch to the **API Reviewer** chat mode (Module 02, Lab 03) and ask it to
review `plan.md` against `usecase.md` and the constitution for a second pass.

## Step 3 — Generate tasks

```
/speckit.tasks
```

Open `tasks.md`. Good tasks for this feature look like:

```
T001  Add task_comments table to database/schema.sql (+ index, FK CASCADE)
T002  Add CommentRepository methods: list_by_task, add, delete, task_exists
T003  Add CommentService: validation (lengths), 404/422 mapping inputs
T004  Add router: GET/POST/DELETE /api/tasks/{id}/comments
T005  Backend tests: GET (200 ordered, 404), POST (201, 422 x3, 404), DELETE (204, 404), cascade
T006  Frontend service: getComments / postComment / deleteComment in services/
T007  TaskCard: comment count badge (hidden when 0)
T008  CommentThread + CommentForm components
T009  Frontend tests: badge visibility, thread expand, form validation
T010  Update usecase.md API-contract table with the three new routes
```

Check each task is: **independently verifiable** (you can run *something* after
it), **small** (roughly one sitting), and **ordered** (nothing depends on a
later task).

## Step 4 — Analyze for consistency

```
/speckit.analyze
```

It flags mismatches — a requirement with no task, a task with no requirement, an
acceptance criterion nothing covers, a contract in `plan.md` that contradicts
`spec.md`. **Resolve every finding**, in the right artifact:

- Missing task → the plan/tasks were incomplete: regenerate or add the task.
- Missing requirement → either it's scope creep (drop it) or the spec is
  incomplete (add the requirement — that's change control, even now).

## Step 5 — Start the traceability matrix

**macOS / Linux**

```bash
cp ../module-04/templates/traceability-matrix.md specs/001-task-comments/traceability.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-04\templates\traceability-matrix.md specs\001-task-comments\traceability.md
```

Fill the **REQ → Task(s)** columns from `spec.md` and `tasks.md`. Every `REQ-xx`
must have at least one task; every task must map to at least one `REQ-xx`. If one
doesn't, go back to Step 4 — `/speckit.analyze` should have caught it.

## Step 6 — Commit

```bash
git add specs/ && git commit -m "Module 04 Lab 02: plan, tasks, analyze, REQ->TASK trace"
```

## Verify

- [ ] `plan.md` exists, reviewed, and honours the constitution (repository-only
      DB access, schema.sql edit, error contract).
- [ ] `tasks.md` is a numbered, ordered list of independently verifiable units.
- [ ] `/speckit.analyze` reports no unresolved findings.
- [ ] `specs/001-task-comments/traceability.md` has every REQ mapped to task(s)
      and vice versa.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Plan invents a new stack / ORM | Re-run `/speckit.plan` naming the existing files and patterns explicitly; point it at `backend-python/`. |
| Tasks are huge ("implement the backend") | Ask: "Split any task that can't be verified on its own into smaller ones." |
| `/speckit.analyze` finds contradictions | Fix them in the **upstream** artifact (spec > plan > tasks), then regenerate downstream — don't patch `tasks.md` in isolation. |
| Traceability has orphans | An orphan task = unspecified work (add a REQ or delete it). An orphan REQ = missing task (regenerate tasks). |

## Recap & carry-forward

Design and work breakdown are done and consistent. **Lab 03** implements the
tasks with `/speckit.implement`, validates each acceptance criterion, and ports
the feature to a second backend with the Module 02 `port-endpoint` skill.
