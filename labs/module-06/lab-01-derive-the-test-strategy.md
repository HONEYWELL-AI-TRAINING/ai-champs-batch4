# Lab 01 — Derive the Test Strategy from the Spec

**Time:** ~35 min · **Surface:** Copilot Chat (Ask) + terminal ·
**Prereq:** Module 06 [set-up](README.md#set-up--do-this-once-before-lab-01) done

## Objective

Turn the **soft-delete** specification's acceptance criteria into a test
strategy: map every criterion to the test type that can actually prove it,
design test data across four categories, and find the gaps in the current suite
— unmapped criteria and orphan tests.

## Why it matters for the enterprise

A test strategy is not a shopping list you pick from — it is a **translation**.
"Valid restore returns 200" is a unit test; "restore preserves the comment
cascade" needs a real database; "the whole delete-restore flow works on the
board" is end-to-end. Deriving the strategy from the spec is what guarantees no
acceptance criterion ships unproven and no test exists without a reason.

## Background — the pyramid, derived

```
        ╱ E2E ╲            few, slow, expensive — full user flows
      ╱ contract ╲         the HTTP contract callers depend on
    ╱ integration  ╲       real DB: queries, constraints, cascades (Testcontainers)
  ╱      unit        ╲     many, fast, cheap — isolated logic
 ─────────────────────
  Specification & acceptance criteria  ← every layer exists because some AC needs that kind of proof
```

Test-data categories (a feature is only as tested as its worst-case input):
**happy path · boundary & edge · negative & invalid · failure & timeout**.

---

## Step 1 — Create the strategy doc

**macOS / Linux**

```bash
cp ../module-06/templates/test-strategy-template.md specs/002-task-soft-delete/test-strategy.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-06\templates\test-strategy-template.md specs\002-task-soft-delete\test-strategy.md
```

## Step 2 — Extract every acceptance criterion

Open `specs/002-task-soft-delete/spec.md` and `acceptance-checklist.md`. In
Copilot Chat (Ask mode), attach both and ask:

```
List every acceptance criterion for the soft-delete feature as a numbered table:
AC id | the criterion, verbatim | is it about isolated logic, a real DB
behaviour (constraint/cascade/tx), the HTTP contract, or a full user flow?
Do not invent criteria — only what's in the spec.
```

Paste the table into `test-strategy.md` section 2 and **verify each row against
the spec yourself** — Copilot is drafting, you are deciding.

## Step 3 — Assign a test type to each criterion, with a reason

Fill the "Test type" and "Why this type proves it" columns. Use this guide:

| The criterion is about… | Test type | Example for soft-delete |
|-------------------------|-----------|-------------------------|
| Input validation, status mapping, a pure function | **unit** | `DELETE` on unknown id → 404 |
| A real SQL query, a `WHERE deleted_at IS NULL`, a FK cascade, a transaction | **integration** (Testcontainers) | restore keeps `task_comments`; `?permanent=true` cascades |
| The HTTP contract in `usecase.md` — path, method, status, body shape | **API / contract** | `DELETE` still returns `204`; `GET ?deleted=true` shape |
| A full flow across UI + API + DB | **end-to-end** | delete on the board → gone → restore → back with comments |

Anything you can prove with a fast unit test, prove there — don't push it up the
pyramid.

## Step 4 — Design the test data

Fill section 4. For soft-delete, that looks like:

| Category | Concretely |
|----------|-----------|
| Happy path | a live task, delete it, it's hidden; restore it, it's back |
| Boundary & edge | delete a task with **0** comments; with **many** comments; restore a task that was never deleted; double-delete |
| Negative & invalid | delete a non-existent id; restore a non-existent id; `?permanent=` with a bad value |
| Failure & timeout | the FK cascade under a DB constraint; a delete inside a transaction that rolls back; `deleted_at` filter missing from one read path (the Module 05 Ring-2 risk) |

## Step 5 — Find the gaps in the current suite

Ask Copilot:

```
#codebase Here is my soft-delete test strategy (attached). Compare it to the
tests that actually exist for tasks today. Report:
1. Acceptance criteria with NO test that proves them.
2. Existing task tests that don't map to any acceptance criterion.
3. Any behaviour currently tested only with a mock/fixture that my strategy says
   needs a real database.
Paths and test names only.
```

Fill section 5. The goal state, written at the top of `test-strategy.md`:
**no unmapped acceptance criteria, no orphan tests.**

## Step 6 — Commit

```bash
git add specs/002-task-soft-delete/test-strategy.md
git commit -m "Module 06 Lab 01: soft-delete test strategy + traceability"
```

## Verify

- [ ] `test-strategy.md` section 2 has a row for **every** acceptance criterion,
      each with a test type and a one-line reason.
- [ ] Section 4 has concrete test data in all four categories.
- [ ] Section 5 names the unmapped criteria and orphan tests in the current
      suite (if there are none, you've said so explicitly).
- [ ] Nothing is assigned to E2E that a unit or integration test could prove.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Everything looks like an "integration" test | Split the criterion. "404 on unknown id" is unit (no DB needed for the not-found path if the repo is faked); "cascade on permanent delete" is integration. |
| No gaps found, suite feels thin | Re-read the spec's negative and failure criteria — those are the ones usually missing. |
| Copilot invents acceptance criteria | Attach the spec explicitly and say "verbatim only"; cross-check every row. |

## Recap & carry-forward

You have a strategy that says exactly what to test and where. **Lab 02** builds
the integration and contract layers for real — against an ephemeral Postgres via
Testcontainers, not a mock.
