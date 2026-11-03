# Lab 02 — Brownfield: Repository Archaeology & Change-Impact Analysis

**Time:** ~40 min · **Surface:** Copilot Chat (Ask + `#codebase`) + Spec Kit ·
**Prereq:** Lab 01 complete

## Objective

A change to **existing behaviour** has landed — [soft-delete for tasks](feature-request.md).
Before writing a line of code, produce two artifacts: a **repository archaeology**
note (what exists, and how) and a **change-impact analysis** (the blast radius).
Only then turn it into a scoped spec and plan.

## Why it matters for the enterprise

On brownfield code, the risk is not under-specifying the feature — it's an
unintended **regression** in code that already works. Skipping the "understand
first" step is exactly how a well-meaning change breaks a downstream feature
nobody remembered. Archaeology and change-impact analysis make the blast radius
explicit, so "minimal change" has a concrete boundary and regression testing
knows what to protect.

## Background — the brownfield flow

```
Repository Archaeology → Architecture & Dependency Analysis → Change-Impact Analysis → Minimal-Change Implementation → Verify & Protect
     (Step 1)                        (Step 1)                       (Step 2)                  (Lab 03)                 (Lab 03)
```

Every stage before implementation exists to answer one question: **what could
this break, and how will we know it didn't?**

---

## Step 1 — Repository archaeology

Create a working folder for the analysis and the note. (In Step 3,
`/speckit.specify` will create its own numbered feature folder — if the name it
picks differs, move `archaeology.md` and `change-impact.md` into that folder so
everything for this change lives together.)

**macOS / Linux**

```bash
mkdir -p specs/002-task-soft-delete
cp ../module-05/templates/archaeology-template.md specs/002-task-soft-delete/archaeology.md
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path specs\002-task-soft-delete | Out-Null
Copy-Item ..\module-05\templates\archaeology-template.md specs\002-task-soft-delete\archaeology.md
```

Use Copilot as a **guide**, not an author. In Ask mode:

```
#codebase I'm about to change DELETE /api/tasks/{id} from a hard delete to a
soft delete. Before I do:
1. Trace the current delete path end to end — every file and function, from the
   React services layer to the tasks table.
2. List every repository/query method that reads tasks (list, get, filter,
   count) — anything that would need to exclude soft-deleted rows.
3. Show me the existing tests that assert a task is GONE after DELETE.
4. What depends on DELETE cascading to task_comments today?
Paths and function names only; I'll read them myself.
```

Verify each path Copilot names by opening the file. Fill in `archaeology.md`
sections 1–5 from what you actually read. Pay special attention to **section 4**:
the exact tests that pin the current "row is gone" behaviour.

Write the **section 6 summary** — this is what the change-impact analysis builds
on.

## Step 2 — Change-impact analysis (the blast radius)

**macOS / Linux**

```bash
cp ../module-05/templates/change-impact-template.md specs/002-task-soft-delete/change-impact.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-05\templates\change-impact-template.md specs\002-task-soft-delete\change-impact.md
```

Work outward from the change:

- **Ring 1 — directly dependent:** the repository's list/get/count methods, the
  DELETE router + service, the `task_comments` FK behaviour.
- **Ring 2 — indirectly affected:** `GET /api/tasks/stats` (Module 03 — does it
  count deleted tasks?); the frontend board + its "six seeded tasks" tests; the
  seed data; the `port-endpoint` parity expectation for the other backends;
  `usecase.md`'s documented DELETE contract (`204`, "row is gone").
- **Ring 3 — believed unaffected, protected by tests:** task *creation* and
  *update*, comment creation on a live task, status filtering — name the
  existing test that proves each stays green.

Ask Copilot to pressure-test your analysis:

```
Here is my change-impact analysis for soft-delete (attached). What did I miss?
Look especially for read paths that don't filter, tests that assume a row count,
and any feature that joins or counts tasks.
```

Complete the **regression-protection plan** table: for each existing behaviour
that must be preserved, name the test that guards it, and flag gaps where you
need to *add* a regression test before implementing.

## Step 3 — Scoped spec + plan

Now — and only now — write the spec, bounded by the analysis:

```
/speckit.specify

Soft-delete for tasks, per labs/module-05/feature-request.md and the analysis in
specs/002-task-soft-delete/change-impact.md. Honour the constitution. The change
is bounded by the blast radius in change-impact.md — do not expand scope beyond
Ring 1 + the necessary Ring 2 items. Resolve the open questions from the feature
request.
```

```
/speckit.clarify
```

Suggested decisions to record (use your judgement):

| Question | Decision |
|----------|----------|
| Marker | `deleted_at TIMESTAMP NULL` (consistent with `created_at`/`updated_at`) |
| `GET /api/tasks/{id}` on a deleted task | `404` by default; `200` only with `?includeDeleted=true` |
| API surface | `DELETE /api/tasks/{id}` → soft; `POST /api/tasks/{id}/restore`; `DELETE /api/tasks/{id}?permanent=true` → hard |
| Deleted tasks in `/api/tasks/stats` | Excluded (stats reflect the active board) |
| Comment on a deleted task | `404` (task not found by default rules) |
| List deleted | `GET /api/tasks?deleted=true` |

Then:

```
/speckit.plan     → design the change: the schema column, the ONE place the
                    default "exclude deleted" filter belongs (repository), the
                    new endpoints, and — critically — the list of existing tests
                    that must be UPDATED vs the new regression tests to ADD.
/speckit.tasks    → ordered units; the first task is "add regression tests that
                    pin current create/update/comment behaviour", before any
                    behaviour changes.
/speckit.analyze  → resolve all findings.
```

## Step 4 — Commit

```bash
git add specs/002-task-soft-delete
git commit -m "Module 05 Lab 02: soft-delete archaeology, change-impact, spec, plan"
```

## Verify

- [ ] `archaeology.md` sections 1–6 are filled from files you actually opened,
      with `file:line` evidence.
- [ ] `change-impact.md` has all three rings, cross-cutting checks, and a
      regression-protection plan.
- [ ] The Module 03 stats endpoint and the "six seeded tasks" frontend tests
      appear in the blast radius (if you missed them, that's the lesson).
- [ ] `spec.md` scope matches the blast radius — no more, no less.
- [ ] `tasks.md`'s first task adds regression tests *before* any behaviour change.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `#codebase` gives vague paths | Ask one question at a time; verify each answer by opening the file before trusting it. |
| Blast radius feels endless | Ring 3 is meant to be large — that's the code you *don't* touch. Only Ring 1 + necessary Ring 2 are in scope. |
| Spec balloons into "task lifecycle management" | Re-scope to the feature request. Auto-purge, retention, bulk ops are explicitly out. |
| Can't tell which tests will break | Grep the test suite for the current DELETE assertions (`assert ... is None`, `404` after delete, row-count checks). Those are your section-4 list. |

## Recap & carry-forward

You know exactly what this change touches and what must stay still. **Lab 03**
implements it with the minimal-change strategy, proves the pre-existing suite
still passes, and compares the whole brownfield experience to Lab 01's
greenfield one.
